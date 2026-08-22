"""Tests for the browserless Chrome cookie-jar reader.

Every jar in this module is SYNTHETIC: each test builds a Chrome-shaped
sqlite database in ``tmp_path`` with the real column names, so nothing here
touches the operator's live profile. That profile holds a signed-in LinkedIn
session that took a full day to establish; a test suite is not allowed to be
the thing that corrupts it.

The house rule for this file is that a guard is only believed once it has
been SHOWN FAILING. So the checks come in pairs: the assertion that the
reader behaves, plus a CONTROL that drives the same instrument at input it
must reject. A check that cannot fail certifies nothing -- an epoch test that
passes on a naive reading, a "no value leaked" assertion that would pass on a
record carrying a session token, a source scan that would pass on a wildcard
select. Each of those is written out below and shown to fail.
"""

from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional

import pytest

from linkedin_server import cookie_jar
from linkedin_server.cookie_jar import CookieJarUnavailableError, read_jar

# ---------------------------------------------------------------------------
# The numbers, hand-computed once so the assertions do not re-derive them
# ---------------------------------------------------------------------------

#: The real ``expires_utc`` Chrome wrote for ``li_at`` in the operator's
#: profile, in the WebKit epoch (microseconds since 1601-01-01 UTC).
LI_AT_WEBKIT_US = 13463341957810868

#: Hand-computed from the value above:
#:   13463341957810868 us  = 13463341957 s + 810868 us since 1601-01-01
#:   13463341957 - 11644473600 (the 1601->1970 offset, 134774 * 86400)
#:                         = 1818868357 s since 1970-01-01
#: i.e. 2027-08-21 17:12:37 UTC, which is when his session actually lapses.
LI_AT_POSIX_S = 1818868357.810868
LI_AT_UTC_DATE = "2027-08-21"

#: What the SAME integer means if the WebKit epoch is ignored and the value is
#: read as plain Unix microseconds. This is the wrong answer the conversion
#: has to be shown to avoid: it is still a valid-looking date, in 2396.
NAIVE_UNIX_US_READING_S = LI_AT_WEBKIT_US / 1000000.0

#: Planted in the ``value`` column of every synthetic row. If this string ever
#: turns up in a returned record, a session token has leaked.
PLANTED_SECRET = "AQEDATEST_SESSION_TOKEN_MUST_NOT_LEAK"

LINKEDIN_HOST = ".www.linkedin.com"


# ---------------------------------------------------------------------------
# Building a Chrome-shaped jar
# ---------------------------------------------------------------------------

#: Chrome 140's ``cookies`` table, column for column, copied from the schema
#: read out of the operator's own profile (sqlite ``meta.version`` 24). The
#: reader is only allowed to depend on names that really exist.
CHROME_COOKIES_DDL = """
CREATE TABLE cookies(
    creation_utc INTEGER NOT NULL,
    host_key TEXT NOT NULL,
    top_frame_site_key TEXT NOT NULL,
    name TEXT NOT NULL,
    value TEXT NOT NULL,
    encrypted_value BLOB NOT NULL,
    path TEXT NOT NULL,
    expires_utc INTEGER NOT NULL,
    is_secure INTEGER NOT NULL,
    is_httponly INTEGER NOT NULL,
    last_access_utc INTEGER NOT NULL,
    has_expires INTEGER NOT NULL,
    is_persistent INTEGER NOT NULL,
    priority INTEGER NOT NULL,
    samesite INTEGER NOT NULL,
    source_scheme INTEGER NOT NULL,
    source_port INTEGER NOT NULL,
    last_update_utc INTEGER NOT NULL,
    source_type INTEGER NOT NULL,
    has_cross_site_ancestor INTEGER NOT NULL
)
"""

_COLUMNS = (
    "creation_utc", "host_key", "top_frame_site_key", "name", "value",
    "encrypted_value", "path", "expires_utc", "is_secure", "is_httponly",
    "last_access_utc", "has_expires", "is_persistent", "priority", "samesite",
    "source_scheme", "source_port", "last_update_utc", "source_type",
    "has_cross_site_ancestor",
)


def cookie_row(
    name: str,
    *,
    host_key: str = LINKEDIN_HOST,
    expires_utc: int = 0,
    has_expires: int = 0,
    is_persistent: int = 0,
) -> tuple:
    """One fully-populated row; every column in the real table is NOT NULL."""
    return (
        13400000000000000,      # creation_utc
        host_key,
        "",                     # top_frame_site_key
        name,
        PLANTED_SECRET,         # value -- the thing that must never come back
        b"v10_sealed_blob",     # the sealed blob beside it
        "/",                    # path
        expires_utc,
        1,                      # is_secure
        1,                      # is_httponly
        13400000000000000,      # last_access_utc
        has_expires,
        is_persistent,
        1,                      # priority
        0,                      # samesite
        2,                      # source_scheme
        443,                    # source_port
        13400000000000000,      # last_update_utc
        0,                      # source_type
        0,                      # has_cross_site_ancestor
    )


def persistent_row(name: str, webkit_us: int, **kw: Any) -> tuple:
    """A row Chrome would call persistent: both flags set, real timestamp."""
    return cookie_row(
        name, expires_utc=webkit_us, has_expires=1, is_persistent=1, **kw
    )


def make_profile(
    tmp_path: Path,
    rows: list[tuple],
    *,
    journal: Optional[bytes] = None,
) -> Path:
    """Write a Chrome-shaped profile under ``tmp_path`` and return its root.

    Lays the jar at the real relative path (``Default/Network/Cookies``) so
    the reader's own path arithmetic is under test too, not stubbed out.
    """
    profile = tmp_path / "chrome-profile"
    network = profile / "Default" / "Network"
    network.mkdir(parents=True, exist_ok=True)
    jar = network / "Cookies"

    con = sqlite3.connect(str(jar))
    try:
        con.execute(CHROME_COOKIES_DDL)
        placeholders = ",".join("?" * len(_COLUMNS))
        con.executemany(
            "INSERT INTO cookies (" + ",".join(_COLUMNS) + ") "
            "VALUES (" + placeholders + ")",
            rows,
        )
        con.commit()
    finally:
        con.close()

    if journal is not None:
        (network / "Cookies-journal").write_bytes(journal)
    return profile


# ---------------------------------------------------------------------------
# The two instruments that get driven in both directions
# ---------------------------------------------------------------------------

#: Keys that would mean a value came back under some other name.
VALUE_LIKE_KEYS = {"value", "encrypted_value", "encryptedvalue", "token",
                   "cookie", "secret"}


def find_value_leaks(records: list[dict[str, Any]]) -> list[str]:
    """Return one complaint per way a record carries a cookie value.

    Used on the reader's real output (must be empty) AND, in the control
    below, on a hand-made record that does carry a value (must not be empty).
    One instrument, both directions -- so the empty result means something.
    """
    leaks: list[str] = []
    for i, rec in enumerate(records):
        for key, val in rec.items():
            if str(key).lower() in VALUE_LIKE_KEYS:
                leaks.append(f"record {i} carries a value-like key {key!r}")
            elif isinstance(val, str) and PLANTED_SECRET in val:
                leaks.append(f"record {i} key {key!r} contains the secret")
        extra = set(rec) - {"name", "expires"}
        if extra:
            leaks.append(f"record {i} has unexpected keys {sorted(extra)}")
    return leaks


def scan_for_value_reads(text: str) -> list[str]:
    """Return one complaint per way a source text could fetch a cookie value.

    Driven at the module's own source (must be empty) AND, in the control
    below, at sample SQL that does both of the banned things.
    """
    offences: list[str] = []
    upper = text.upper()
    if "ENCRYPTED_" + "VALUE" in upper:
        offences.append("names the sealed value column")
    if "SELECT" + " *" in upper:
        offences.append("uses a wildcard select")
    return offences


def cookie_jar_source() -> str:
    path = Path(cookie_jar.__file__)
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. The epoch conversion, and the wrong answer it has to avoid
# ---------------------------------------------------------------------------


def test_persistent_li_at_expires_is_converted_from_the_webkit_epoch(tmp_path):
    profile = make_profile(
        tmp_path, [persistent_row("li_at", LI_AT_WEBKIT_US)]
    )

    records = read_jar(profile, ["li_at"])

    assert [r["name"] for r in records] == ["li_at"]
    assert records[0]["expires"] == pytest.approx(LI_AT_POSIX_S, abs=1e-6)


def test_expiry_lands_on_the_operators_known_renewal_date(tmp_path):
    """The date is the human-checkable half of the same assertion."""
    profile = make_profile(
        tmp_path, [persistent_row("li_at", LI_AT_WEBKIT_US)]
    )

    expires = read_jar(profile, ["li_at"])[0]["expires"]

    assert time.strftime("%Y-%m-%d", time.gmtime(expires)) == LI_AT_UTC_DATE


def test_control_the_naive_unix_microsecond_reading_is_a_different_answer(
    tmp_path,
):
    """CONTROL: shows the epoch offset is load-bearing, not decoration.

    If ``read_jar`` divided by a million and stopped, it would return
    13463341957.81, a perfectly plausible float that renders as a date in
    2396. Both assertions below would fail on that reader, which is what
    makes the two tests above meaningful rather than tautological.
    """
    assert NAIVE_UNIX_US_READING_S != pytest.approx(LI_AT_POSIX_S, abs=1.0)
    assert time.strftime(
        "%Y-%m-%d", time.gmtime(NAIVE_UNIX_US_READING_S)
    ) != LI_AT_UTC_DATE

    profile = make_profile(
        tmp_path, [persistent_row("li_at", LI_AT_WEBKIT_US)]
    )
    expires = read_jar(profile, ["li_at"])[0]["expires"]

    assert expires != pytest.approx(NAIVE_UNIX_US_READING_S, abs=1.0)
    # ...and the third wrong reading: no offset applied at all lands in 1601.
    assert time.gmtime(expires).tm_year == 2027


# ---------------------------------------------------------------------------
# 2. Session cookies
# ---------------------------------------------------------------------------


def test_session_cookie_reports_minus_one(tmp_path):
    """``JSESSIONID`` is stored has_expires=0, is_persistent=0, expires_utc=0."""
    profile = make_profile(tmp_path, [cookie_row("JSESSIONID")])

    records = read_jar(profile, ["JSESSIONID"])

    assert records == [{"name": "JSESSIONID", "expires": -1.0}]


def test_control_a_persistent_cookie_in_the_same_jar_is_not_minus_one(tmp_path):
    """CONTROL: -1.0 is a measurement, not this reader's only output."""
    profile = make_profile(
        tmp_path,
        [cookie_row("JSESSIONID"), persistent_row("li_at", LI_AT_WEBKIT_US)],
    )

    by_name = {r["name"]: r["expires"] for r in read_jar(
        profile, ["JSESSIONID", "li_at"]
    )}

    assert by_name["JSESSIONID"] == -1.0
    assert by_name["li_at"] != -1.0
    assert by_name["li_at"] > 0


def test_a_persistent_flag_with_no_timestamp_is_still_a_session_cookie(tmp_path):
    """Flags set but ``expires_utc`` empty: no date exists, so do not invent one."""
    profile = make_profile(
        tmp_path,
        [cookie_row("li_at", expires_utc=0, has_expires=1, is_persistent=1)],
    )

    assert read_jar(profile, ["li_at"]) == [{"name": "li_at", "expires": -1.0}]


# ---------------------------------------------------------------------------
# 3. Absent names are absent, not placeholdered
# ---------------------------------------------------------------------------


def test_a_requested_name_that_is_absent_is_omitted(tmp_path):
    profile = make_profile(
        tmp_path, [persistent_row("li_at", LI_AT_WEBKIT_US)]
    )

    records = read_jar(profile, ["li_at", "bcookie"])

    assert [r["name"] for r in records] == ["li_at"]
    assert all(r["name"] != "bcookie" for r in records)


def test_control_the_same_request_returns_the_name_once_it_exists(tmp_path):
    """CONTROL: the omission above is absence, not a filter that drops all."""
    profile = make_profile(
        tmp_path,
        [
            persistent_row("li_at", LI_AT_WEBKIT_US),
            persistent_row("bcookie", LI_AT_WEBKIT_US),
        ],
    )

    records = read_jar(profile, ["li_at", "bcookie"])

    assert [r["name"] for r in records] == ["li_at", "bcookie"]


# ---------------------------------------------------------------------------
# 4. Host keys
# ---------------------------------------------------------------------------


def test_a_non_linkedin_host_with_the_same_name_is_not_returned(tmp_path):
    profile = make_profile(
        tmp_path,
        [persistent_row(
            "li_at", LI_AT_WEBKIT_US, host_key=".accounts.example.com"
        )],
    )

    assert read_jar(profile, ["li_at"]) == []


def test_control_the_same_row_on_a_linkedin_host_is_returned(tmp_path):
    """CONTROL: the rejection above is about the host, not about the row."""
    profile = make_profile(
        tmp_path,
        [persistent_row("li_at", LI_AT_WEBKIT_US, host_key=LINKEDIN_HOST)],
    )

    records = read_jar(profile, ["li_at"])

    assert [r["name"] for r in records] == ["li_at"]
    assert records[0]["expires"] == pytest.approx(LI_AT_POSIX_S, abs=1e-6)


def test_a_lookalike_domain_is_not_treated_as_linkedin(tmp_path):
    """A raw ``endswith`` would accept this; label-boundary matching does not."""
    profile = make_profile(
        tmp_path,
        [persistent_row("li_at", LI_AT_WEBKIT_US, host_key="notlinkedin.com")],
    )

    assert read_jar(profile, ["li_at"]) == []


def test_both_linkedin_rows_for_one_name_are_returned(tmp_path):
    """Playwright reports one record per jar row; so does this."""
    profile = make_profile(
        tmp_path,
        [
            persistent_row("li_at", LI_AT_WEBKIT_US, host_key=".linkedin.com"),
            persistent_row("li_at", LI_AT_WEBKIT_US, host_key=LINKEDIN_HOST),
        ],
    )

    records = read_jar(profile, ["li_at"])

    assert [r["name"] for r in records] == ["li_at", "li_at"]


# ---------------------------------------------------------------------------
# 5. No value ever comes back
# ---------------------------------------------------------------------------


def test_no_returned_record_carries_a_cookie_value(tmp_path):
    profile = make_profile(
        tmp_path,
        [persistent_row("li_at", LI_AT_WEBKIT_US), cookie_row("JSESSIONID")],
    )

    records = read_jar(profile, ["li_at", "JSESSIONID"])

    assert records, "nothing was read, so the check below would be vacuous"
    assert find_value_leaks(records) == []
    assert PLANTED_SECRET not in repr(records)


def test_control_the_leak_check_rejects_a_record_that_does_carry_a_value():
    """CONTROL: the empty result above is a finding, not an inert check."""
    planted = [{"name": "li_at", "expires": 1.0, "value": PLANTED_SECRET}]

    leaks = find_value_leaks(planted)

    assert leaks, "the leak check passed a record holding a session token"
    assert any("value" in complaint for complaint in leaks)
    # And it catches the value hiding under an innocent key name too.
    assert find_value_leaks(
        [{"name": "li_at", "expires": 1.0, "note": PLANTED_SECRET}]
    )


def test_the_source_never_reads_a_cookie_value():
    offences = scan_for_value_reads(cookie_jar_source())

    assert offences == []


def test_control_the_source_scan_rejects_sql_that_does(tmp_path):
    """CONTROL: the clean scan above would have caught either banned form."""
    assert scan_for_value_reads("SELECT * FROM cookies")
    assert scan_for_value_reads("SELECT encrypted_value FROM cookies")
    assert scan_for_value_reads(
        "cur.execute('select ENCRYPTED_VALUE from cookies')"
    )


def test_the_query_constant_names_only_metadata_columns():
    query = cookie_jar._JAR_QUERY.lower()

    assert "value" not in query
    assert query.startswith("select name, host_key")
    # CONTROL: the same check fails on a query that does select the value.
    assert "value" in "select name, value from cookies"


# ---------------------------------------------------------------------------
# 6. Failures are raised, never returned as an empty list
# ---------------------------------------------------------------------------


def test_a_missing_profile_directory_raises(tmp_path):
    missing = tmp_path / "no-such-profile"

    with pytest.raises(CookieJarUnavailableError) as excinfo:
        read_jar(missing, ["li_at"])

    message = str(excinfo.value)
    assert "profile directory does not exist" in message
    assert str(missing) in message


def test_a_missing_jar_file_raises(tmp_path):
    profile = tmp_path / "chrome-profile"
    (profile / "Default" / "Network").mkdir(parents=True)

    with pytest.raises(CookieJarUnavailableError) as excinfo:
        read_jar(profile, ["li_at"])

    message = str(excinfo.value)
    assert "cookie jar file does not exist" in message
    assert str(profile / "Default" / "Network" / "Cookies") in message


def test_the_two_missing_cases_do_not_report_the_same_thing(tmp_path):
    """CONTROL: two distinct causes must not collapse into one message."""
    missing_profile = tmp_path / "no-such-profile"
    empty_profile = tmp_path / "chrome-profile"
    (empty_profile / "Default" / "Network").mkdir(parents=True)

    with pytest.raises(CookieJarUnavailableError) as no_dir:
        read_jar(missing_profile, ["li_at"])
    with pytest.raises(CookieJarUnavailableError) as no_file:
        read_jar(empty_profile, ["li_at"])

    assert str(no_dir.value) != str(no_file.value)
    assert "profile directory does not exist" not in str(no_file.value)
    assert "cookie jar file does not exist" not in str(no_dir.value)


def test_a_corrupt_jar_raises_the_defined_error_not_a_raw_sqlite_error(tmp_path):
    profile = tmp_path / "chrome-profile"
    network = profile / "Default" / "Network"
    network.mkdir(parents=True)
    (network / "Cookies").write_bytes(b"this is not a sqlite database at all")

    with pytest.raises(CookieJarUnavailableError) as excinfo:
        read_jar(profile, ["li_at"])

    assert not isinstance(excinfo.value, sqlite3.Error)
    assert isinstance(excinfo.value.__cause__, sqlite3.Error)
    assert str(network / "Cookies") in str(excinfo.value)


def test_control_that_corrupt_file_really_does_break_raw_sqlite(tmp_path):
    """CONTROL: the test above is not passing on a file sqlite finds fine."""
    corrupt = tmp_path / "Cookies"
    corrupt.write_bytes(b"this is not a sqlite database at all")

    con = sqlite3.connect(str(corrupt))
    try:
        with pytest.raises(sqlite3.DatabaseError):
            con.execute("SELECT name FROM cookies").fetchall()
    finally:
        con.close()


# ---------------------------------------------------------------------------
# 7. The live file is never the file that gets opened
# ---------------------------------------------------------------------------


class ConnectSpy:
    """Records every path handed to sqlite, and what sat beside it.

    ``clear()`` exists because these tests BUILD a jar with sqlite before
    reading one with sqlite, and only the second call is under test. Without
    it every assertion would be inspecting the fixture's own bookkeeping.
    """

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def clear(self) -> None:
        self.calls.clear()

    @property
    def only(self) -> dict[str, Any]:
        assert len(self.calls) == 1, (
            f"expected exactly one sqlite open, saw {len(self.calls)}: "
            f"{[c['path'] for c in self.calls]}"
        )
        return self.calls[0]


@pytest.fixture()
def connect_spy(monkeypatch):
    real_connect = sqlite3.connect
    spy_state = ConnectSpy()

    def spy(path, *args, **kwargs):
        spy_state.calls.append({
            "path": str(path),
            "siblings": sorted(os.listdir(os.path.dirname(str(path)))),
        })
        return real_connect(path, *args, **kwargs)

    monkeypatch.setattr(cookie_jar.sqlite3, "connect", spy)
    return spy_state


def test_sqlite_is_never_handed_the_live_jar_path(tmp_path, connect_spy):
    profile = make_profile(
        tmp_path, [persistent_row("li_at", LI_AT_WEBKIT_US)]
    )
    jar = profile / "Default" / "Network" / "Cookies"
    connect_spy.clear()

    read_jar(profile, ["li_at"])

    assert connect_spy.calls, "the spy never fired, so this proves nothing"
    opened = Path(connect_spy.only["path"])
    assert opened != jar
    assert opened.parent != jar.parent
    assert profile not in opened.parents


def test_the_temporary_copy_is_deleted_afterwards(tmp_path, connect_spy):
    profile = make_profile(
        tmp_path, [persistent_row("li_at", LI_AT_WEBKIT_US)]
    )
    connect_spy.clear()

    records = read_jar(profile, ["li_at"])

    assert records, "the read must have succeeded for cleanup to be the point"
    opened = Path(connect_spy.only["path"])
    assert not opened.exists()
    assert not opened.parent.exists()


def test_the_journal_sibling_is_copied_next_to_the_jar(tmp_path, connect_spy):
    """A copy without its journal can hand back rows the journal would undo."""
    profile = make_profile(
        tmp_path,
        [persistent_row("li_at", LI_AT_WEBKIT_US)],
        journal=b"",
    )
    assert (profile / "Default" / "Network" / "Cookies-journal").exists()
    connect_spy.clear()

    read_jar(profile, ["li_at"])

    assert connect_spy.only["siblings"] == ["Cookies", "Cookies-journal"]


def test_control_with_no_journal_only_the_jar_is_copied(tmp_path, connect_spy):
    """CONTROL: the assertion above tracks the source, not a fixed answer."""
    profile = make_profile(
        tmp_path, [persistent_row("li_at", LI_AT_WEBKIT_US)]
    )
    assert not (profile / "Default" / "Network" / "Cookies-journal").exists()
    connect_spy.clear()

    read_jar(profile, ["li_at"])

    assert connect_spy.only["siblings"] == ["Cookies"]


def test_the_live_jar_file_is_unchanged_by_a_read(tmp_path):
    """Byte-for-byte, plus mtime: reading must be a pure read."""
    import hashlib

    profile = make_profile(
        tmp_path, [persistent_row("li_at", LI_AT_WEBKIT_US)]
    )
    jar = profile / "Default" / "Network" / "Cookies"
    before = (
        hashlib.sha256(jar.read_bytes()).hexdigest(),
        jar.stat().st_size,
        jar.stat().st_mtime_ns,
    )

    read_jar(profile, ["li_at", "JSESSIONID"])

    after = (
        hashlib.sha256(jar.read_bytes()).hexdigest(),
        jar.stat().st_size,
        jar.stat().st_mtime_ns,
    )
    assert before == after
