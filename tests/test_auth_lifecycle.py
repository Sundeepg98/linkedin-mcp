"""The auth lifecycle: what session_info reports, and what a logout takes.

Two tools, pulling in opposite directions, and both of them are places this
family of servers has already been wrong.

``linkedin_session_info`` reports the shared auth-lifecycle shape. The field
names moved (``session_cookie`` -> ``credential``, ``csrf_cookie`` ->
``supporting``, ``cookie_source`` -> ``credential_source``) and three blocks
arrived (``server``, ``renewal``, ``credential.expiry_source``), but the one
thing that must NOT have moved is the honesty rule underneath:

    ``authenticated`` comes from a live identity call or it is null.
    Never from a cookie being in the jar.

That rule is the reason ``scripts/presence_is_auth_control.py`` exists. It is
a pytest plugin that rebuilds this server with ``authenticated`` derived from
li_at's PRESENCE -- the exact bug -- and the tests in the first section below
are the ones that have to go red under it. Their measured red counts are in
that file's docstring. A test that has never been shown failing is a claim.

``linkedin_logout`` is the one destructive thing in this package, and the
asset it destroys took the operator a full DAY to establish. So the tests
that matter most here are not the ones proving it works. They are the ones
proving it does NOTHING when it was not confirmed, and nothing when another
process is on the profile:

* the erasing step is a named seam (``auth._erase``) so a test can replace it
  with a recorder and prove the unconfirmed path never REACHES it. "Nothing
  changed on disk" is the weaker claim; "the step was never entered" is the
  one worth having.
* every claim of inertness is checked a second way, by hashing every byte
  under the profile before and after -- and that instrument has its own
  control below, driven at a real erase it must detect.

Every profile in this file is a temp dir built by ``make_profile``. Nothing
here goes anywhere near ``_state/chrome-profile``, and nothing here launches
a browser.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

import pytest

from linkedin_server import auth as auth_module
from linkedin_server import profile_lock as profile_lock_module
from linkedin_server import server as server_module
from linkedin_server.errors import BrowserUnavailableError
from tests.conftest import FakePage, FakeResponse, me_response
from tests.leakwalk import PLANTED_JSESSIONID, assert_no_leak, find_leaks
from tests.test_cookie_jar import PLANTED_SECRET, cookie_row, make_profile
from tests.test_session_info_offline import (
    PREFLIGHT_MESSAGE,
    _FailingSession,
    healthy_profile,
    webkit_us_in_days,
)

# ---------------------------------------------------------------------------
# Instruments
# ---------------------------------------------------------------------------


def snapshot(root: Path) -> dict[str, str]:
    """Every file under ``root`` by relative path, with a hash of its bytes.

    Two snapshots comparing equal is the strongest available reading of "not
    one byte changed": a changed byte moves the digest, a removed file leaves
    the mapping, and a new file joins it. It has a control below.
    """
    out: dict[str, str] = {}
    for path in sorted(Path(root).rglob("*")):
        if path.is_file():
            data = path.read_bytes()
            out[str(path.relative_to(root))] = (
                f"{len(data)}:{hashlib.sha256(data).hexdigest()}"
            )
    return out


def erase_recorder(monkeypatch) -> list:
    """Replace ``auth._erase`` with something that RECORDS and then raises.

    Both halves are deliberate. The raise is the trap the brief asks for; the
    record is what makes the trap readable, because ``logout`` catches every
    exception the erase step throws on purpose -- so a bare raise would be
    swallowed into a ``failed`` entry and a test asserting only "no
    exception" would pass either way. The list is external and cannot be
    swallowed. ``test_the_erase_recorder_fills_on_a_confirmed_call`` is its
    control.
    """
    touched: list = []

    def trap(path):
        touched.append(str(path))
        raise AssertionError(
            "auth._erase was reached. Nothing may erase anything on this path."
        )

    monkeypatch.setattr(auth_module, "_erase", trap)
    return touched


def unlocked(tmp_path, monkeypatch) -> None:
    """Point the profile lock at a path nothing holds.

    Without this a confirmed-logout test would consult the REAL lock file
    beside the operator's real profile, and its answer would depend on
    whether a browser happened to be open. Tests do not read live state.
    """
    monkeypatch.setattr(
        profile_lock_module, "_LOCK_FILE", tmp_path / "nothing-holds-this.lock"
    )


def jar_of(profile) -> Path:
    return Path(profile) / "Default" / "Network" / "Cookies"


@pytest.fixture(autouse=True)
def never_the_real_profile(monkeypatch):
    """A tripwire under every test in this file.

    Every test here builds its own temp profile and every one of them is meant
    to. This wraps the erase seam so that a test which forgot to redirect
    ``CHROME_PROFILE`` fails LOUDLY rather than erasing the operator's real
    cookie jar -- a loss that costs a full day and that no revert can undo.

    It WRAPS rather than replaces, so the erase still really happens where it
    is supposed to and no test is quietly neutered by its own safety net.
    """
    from linkedin_server.config import CHROME_PROFILE as REAL_PROFILE

    real_erase = auth_module._erase

    def guarded(path):
        resolved = Path(path).resolve()
        if resolved == REAL_PROFILE or REAL_PROFILE in resolved.parents:
            raise AssertionError(
                f"a test tried to erase {resolved}, which is inside the real "
                "Chrome profile. Tests in this file use temp dirs only."
            )
        return real_erase(path)

    monkeypatch.setattr(auth_module, "_erase", guarded)


# ---------------------------------------------------------------------------
# 1. The honesty contract, carried through the reshape
#
#    These are the tests presence_is_auth_control must turn red.
# ---------------------------------------------------------------------------


def test_the_offline_path_still_answers_null_and_not_false(tmp_path):
    """The jar could not look healthier, and the verdict is still null.

    Null, specifically -- not False. False means a server said no, and no
    server was asked here. Collapsing "I could not tell" into "you are signed
    out" is how this server would come to tell the operator to spend another
    day signing in while his session was fine.
    """
    info = auth_module.session_info_offline(
        healthy_profile(tmp_path), mode="launch", why_no_live_check="no browser"
    )

    assert info["authenticated"] is None
    assert info["authenticated"] is not False
    assert info["live_check"]["completed"] is False
    assert info["credential"]["present"] is True


async def test_the_browser_failed_path_still_answers_null(tmp_path, monkeypatch):
    """The other route to a null: the tool tried, and the browser was dead."""
    monkeypatch.setattr(server_module, "CHROME_PROFILE", healthy_profile(tmp_path))
    monkeypatch.setattr(
        server_module.BROWSER,
        "session",
        lambda: _FailingSession(BrowserUnavailableError(PREFLIGHT_MESSAGE)),
    )

    info = await server_module.linkedin_session_info()

    assert info["authenticated"] is None
    assert info["live_check"]["attempted"] is True
    assert info["live_check"]["completed"] is False
    # The credential is right there and unexpired. It still buys no verdict.
    assert info["credential"]["present"] is True
    assert info["credential"]["expired"] is False


async def test_the_live_path_does_still_say_true(patched_navigation):
    """The control that gives both nulls above their meaning.

    "Offline returns null" is worth nothing if the live path returns null
    too; that would be a server that had quietly stopped measuring rather
    than one that refuses to guess.
    """
    page = FakePage(
        cookies={"li_at": "live", "JSESSIONID": '"ajax:99"'},
        expiries={"li_at": time.time() + 300 * 86400},
        responses=[me_response()],
    )
    info = await auth_module.session_info(page)

    assert info["authenticated"] is True
    assert info["live_check"]["completed"] is True
    assert "why_not" not in info["live_check"]


async def test_a_refusal_is_a_false_and_a_shrug_is_a_null(patched_navigation):
    """Three outcomes, and the two that are not True do not share a field."""
    refused = await auth_module.session_info(
        FakePage(
            cookies={"li_at": "stale", "JSESSIONID": '"ajax:1"'},
            expiries={"li_at": time.time() + 300 * 86400},
            responses=[FakeResponse(401, "")],
        )
    )
    assert refused["authenticated"] is False
    assert refused["live_check"]["completed"] is True

    shrugged = await auth_module.session_info(
        FakePage(
            cookies={"li_at": "live", "JSESSIONID": '"ajax:1"'},
            expiries={"li_at": time.time() + 300 * 86400},
            responses=[FakeResponse(999, "")],
        )
    )
    assert shrugged["authenticated"] is None
    assert shrugged["live_check"]["completed"] is False
    assert "999" in shrugged["live_check"]["why_not"]


def test_why_not_is_present_exactly_when_the_check_did_not_complete(tmp_path):
    offline = auth_module.session_info_offline(
        healthy_profile(tmp_path), mode="launch", why_no_live_check="no browser"
    )
    assert offline["live_check"]["completed"] is False
    assert offline["live_check"]["why_not"]


# ---------------------------------------------------------------------------
# 2. The shape itself
# ---------------------------------------------------------------------------


def test_both_paths_name_the_server_they_are_speaking_for(tmp_path):
    """Four servers return this shape. A reader holding two of them should not
    have to parse a tool name to tell which is which."""
    offline = auth_module.session_info_offline(
        healthy_profile(tmp_path), mode="launch", why_no_live_check="no browser"
    )
    assert offline["server"] == "linkedin"


async def test_the_credential_is_li_at_and_says_so_in_every_field(
    patched_navigation,
):
    page = FakePage(
        cookies={"li_at": "live", "JSESSIONID": '"ajax:99"'},
        expiries={"li_at": time.time() + 300 * 86400},
        responses=[me_response()],
    )
    credential = (await auth_module.session_info(page))["credential"]

    assert credential["kind"] == "cookie"
    assert credential["name"] == "li_at"
    assert credential["present"] is True
    assert credential["format"] == "cookie"
    assert credential["expiry_is_authoritative"] is True
    assert credential["expires_at"].endswith("Z")
    assert 299 <= credential["expires_in_days"] <= 301
    assert credential["expired"] is False


async def test_supporting_carries_jsessionid_under_its_real_role(
    patched_navigation,
):
    """JSESSIONID is not a second credential and must not read as one.

    It signs nothing in. It decides whether the identity call can be PUT --
    LinkedIn will not answer without the csrf header copied out of it -- and
    it dies with the browser, so filing it as a credential would invite a
    reader to treat "it is gone" as "you are signed out".
    """
    page = FakePage(
        cookies={"li_at": "live", "JSESSIONID": '"ajax:99"'},
        expiries={"li_at": time.time() + 300 * 86400},
        responses=[me_response()],
    )
    supporting = (await auth_module.session_info(page))["supporting"]

    assert [entry["name"] for entry in supporting] == ["JSESSIONID"]
    assert supporting[0]["role"] == "csrf"
    assert supporting[0]["present"] is True
    assert supporting[0]["expires_at"] is None
    assert supporting[0]["expired"] is None


def test_supporting_reports_a_missing_csrf_cookie_as_missing(tmp_path):
    """A cold profile has li_at and no JSESSIONID. That is normal, not broken."""
    profile = make_profile(
        tmp_path,
        [cookie_row("li_at", expires_utc=webkit_us_in_days(300),
                    has_expires=1, is_persistent=1)],
    )
    info = auth_module.session_info_offline(
        profile, mode="launch", why_no_live_check="no browser"
    )

    assert info["supporting"][0]["name"] == "JSESSIONID"
    assert info["supporting"][0]["present"] is False
    assert info["credential"]["present"] is True


async def test_expiry_source_names_the_route_that_produced_the_date(
    tmp_path, patched_navigation
):
    """Both routes read the same jar. Which one answered is not cosmetic: a
    date off disk arrives beside a null verdict, a date from a live context
    beside a real one, and a reader cannot tell them apart from the date."""
    page = FakePage(
        cookies={"li_at": "live", "JSESSIONID": '"ajax:99"'},
        expiries={"li_at": time.time() + 300 * 86400},
        responses=[me_response()],
    )
    live = (await auth_module.session_info(page))["credential"]["expiry_source"]
    disk = auth_module.session_info_offline(
        healthy_profile(tmp_path), mode="launch", why_no_live_check="no browser"
    )["credential"]["expiry_source"]

    assert "live browser" in live
    assert "Playwright" in live
    assert "on-disk" in disk
    assert "no browser launched" in disk
    assert live != disk


def test_expiry_source_says_why_when_there_is_no_date(tmp_path):
    """Three ways to have no date, and they are three different facts."""
    absent = auth_module.session_info_offline(
        make_profile(tmp_path / "a", [cookie_row("JSESSIONID")]),
        mode="launch",
        why_no_live_check="no browser",
    )["credential"]
    assert absent["present"] is False
    assert absent["format"] == "absent"
    assert "no li_at in the jar" in absent["expiry_source"]

    unreadable = auth_module.session_info_offline(
        tmp_path / "no-such-profile", mode="launch", why_no_live_check="no browser"
    )["credential"]
    assert unreadable["present"] is False
    assert "no date could be read" in unreadable["expiry_source"]

    # ...and the two do NOT read the same. "You are signed out" and "I could
    # not look" send an operator to different places.
    assert absent["expiry_source"] != unreadable["expiry_source"]


def test_renewal_says_there_is_no_silent_renew_and_says_why(tmp_path):
    """The gap has to be stated, not left to be noticed.

    Two of the four servers in this family DO ship a silent renew. A caller
    holding this shape and finding no ``renewal.tool`` would otherwise be
    left deciding whether the tool is missing or merely absent.
    """
    renewal = auth_module.session_info_offline(
        healthy_profile(tmp_path), mode="launch", why_no_live_check="no browser"
    )["renewal"]

    assert renewal["silent_renew_available"] is False
    assert renewal["tool"] is None
    assert renewal["why"].strip()
    assert len(renewal["why"]) > 80, renewal["why"]
    # The real reason, not a shrug: one layer, and the recovery path by name.
    assert "one credential layer" in renewal["why"]
    assert "linkedin_login_browser" in renewal["why"]
    assert "linkedin_reauth" in renewal["why"]


async def test_the_live_path_carries_renewal_too(patched_navigation):
    """A block that only appears on the fallback is a block nobody reads."""
    page = FakePage(
        cookies={"li_at": "live", "JSESSIONID": '"ajax:99"'},
        expiries={"li_at": time.time() + 300 * 86400},
        responses=[me_response()],
    )
    info = await auth_module.session_info(page)

    assert info["renewal"]["silent_renew_available"] is False
    assert info["renewal"]["tool"] is None
    assert "linkedin_login_browser" in info["renewal"]["why"]


# ---------------------------------------------------------------------------
# 2b. session_lapses_* -- when the OPERATOR must sign in, not when the cookie
#     dies. On this platform they coincide, and that is a finding.
# ---------------------------------------------------------------------------


def test_the_session_lapse_keys_are_on_the_offline_path(tmp_path):
    renewal = auth_module.session_info_offline(
        healthy_profile(tmp_path), mode="launch", why_no_live_check="no browser"
    )["renewal"]

    assert set(renewal) >= {
        "session_lapses_at",
        "session_lapses_in_days",
        "session_lapses_source",
    }
    assert renewal["session_lapses_at"].endswith("Z")
    assert 299 <= renewal["session_lapses_in_days"] <= 301


async def test_the_session_lapse_keys_are_on_the_live_path_too(patched_navigation):
    """A block that only appears on the fallback is a block nobody reads."""
    page = FakePage(
        cookies={"li_at": "live", "JSESSIONID": '"ajax:99"'},
        expiries={"li_at": time.time() + 300 * 86400},
        responses=[me_response()],
    )
    renewal = (await auth_module.session_info(page))["renewal"]

    assert renewal["session_lapses_at"].endswith("Z")
    assert 299 <= renewal["session_lapses_in_days"] <= 301
    assert renewal["session_lapses_source"]


@pytest.mark.parametrize("days", [364.2, 12.5, -3.0])
def test_the_lapse_date_equals_the_credentials_own_on_this_platform(
    tmp_path, days
):
    """Equal because there is nothing that could carry the session past it.

    This is the whole reason the field exists separately. On a server that can
    re-mint its credential the two dates come apart -- naukri measured
    ``nauk_at`` at +0.02 days while the session behind it held +188 -- so a
    client comparing ``credential.expires_at`` across the family compares the
    wrong number. Here they coincide, and the parametrisation pins that it is
    a real derivation rather than one lucky fixture.
    """
    info = auth_module.session_info_offline(
        healthy_profile(tmp_path, days=days),
        mode="launch",
        why_no_live_check="no browser",
    )

    assert info["renewal"]["session_lapses_at"] == info["credential"]["expires_at"]
    assert (
        info["renewal"]["session_lapses_in_days"]
        == info["credential"]["expires_in_days"]
    )


async def test_the_lapse_date_equals_the_credentials_own_on_the_live_path(
    patched_navigation,
):
    page = FakePage(
        cookies={"li_at": "live", "JSESSIONID": '"ajax:99"'},
        expiries={"li_at": time.time() + 300 * 86400},
        responses=[me_response()],
    )
    info = await auth_module.session_info(page)

    assert info["renewal"]["session_lapses_at"] == info["credential"]["expires_at"]
    assert (
        info["renewal"]["session_lapses_in_days"]
        == info["credential"]["expires_in_days"]
    )


def test_the_lapse_source_names_li_at_and_why_it_governs_alone(tmp_path):
    """The source has to carry the REASON, or the equality above reads as a
    field somebody forgot to populate."""
    source = auth_module.session_info_offline(
        healthy_profile(tmp_path), mode="launch", why_no_live_check="no browser"
    )["renewal"]["session_lapses_source"]

    assert "li_at" in source
    assert "ALONE" in source
    assert "no silent renew" in source
    assert "credential.expires_at" in source


def test_an_unreadable_jar_yields_nulls_and_never_a_zero(tmp_path):
    """A zero here would read as "the session ends now", which is the exact
    opposite of "I could not find out". Never a zero, never a False."""
    renewal = auth_module.session_info_offline(
        tmp_path / "no-such-profile", mode="launch", why_no_live_check="no browser"
    )["renewal"]

    assert renewal["session_lapses_at"] is None
    assert renewal["session_lapses_in_days"] is None
    assert renewal["session_lapses_in_days"] is not False
    assert renewal["session_lapses_in_days"] != 0
    # ...and the source says WHY there is no date, carrying the jar's reason.
    assert "li_at" in renewal["session_lapses_source"]
    assert "No date is available" in renewal["session_lapses_source"]
    assert "does not exist" in renewal["session_lapses_source"]


def test_a_profile_never_signed_in_to_yields_nulls_with_its_own_reason(tmp_path):
    """The other way to have no date, and it is a different fact."""
    renewal = auth_module.session_info_offline(
        make_profile(tmp_path, [cookie_row("JSESSIONID")]),
        mode="launch",
        why_no_live_check="no browser",
    )["renewal"]

    assert renewal["session_lapses_at"] is None
    assert renewal["session_lapses_in_days"] is None
    assert "no li_at in the jar" in renewal["session_lapses_source"]


def test_the_renewal_mechanism_is_declared_as_absent_not_as_free(tmp_path):
    """``uses_browser`` is None, and ``is None`` is the only check worth making.

    ``assert not renewal["uses_browser"]`` would pass on ``False`` too, and
    ``False`` is precisely the wrong answer: it asserts that a renewal exists
    and happens not to need a browser. There is no renewal here at all.
    Absence of a mechanism is not a mechanism that costs nothing -- and the
    two servers in this family that DO ship a reauth both drive a browser,
    which is the cost this field exists to stop "silent renew" from hiding.
    """
    renewal = auth_module.session_info_offline(
        healthy_profile(tmp_path), mode="launch", why_no_live_check="no browser"
    )["renewal"]

    assert renewal["uses_browser"] is None
    assert renewal["uses_browser"] is not False
    assert renewal["mechanism"].strip()


async def test_the_mechanism_declaration_is_on_the_live_path_too(
    patched_navigation,
):
    page = FakePage(
        cookies={"li_at": "live", "JSESSIONID": '"ajax:99"'},
        expiries={"li_at": time.time() + 300 * 86400},
        responses=[me_response()],
    )
    renewal = (await auth_module.session_info(page))["renewal"]

    assert renewal["uses_browser"] is None
    assert renewal["uses_browser"] is not False
    assert renewal["mechanism"].strip()


def test_the_mechanism_answers_in_its_own_words(tmp_path):
    """A caller comparing mechanism across four servers must get a straight
    answer from each, without following a cross-reference into renewal.why."""
    mechanism = auth_module.session_info_offline(
        healthy_profile(tmp_path), mode="launch", why_no_live_check="no browser"
    )["renewal"]["mechanism"]

    assert "linkedin_login_browser" in mechanism
    assert "HUMAN action" in mechanism
    assert "full day" in mechanism
    assert "never sees, types, stores or transmits" in mechanism
    # Self-contained: it says WHY the bool is null without making the reader
    # go and read another field to find out.
    assert "null rather than false" in mechanism


def test_the_two_new_keys_survive_an_unreadable_jar(tmp_path):
    """They describe the RENEWAL PATH, not the credential, so a jar that
    cannot be read must not turn them into nulls-by-accident. There is still
    no renewal here, and that is still knowable."""
    renewal = auth_module.session_info_offline(
        tmp_path / "no-such-profile", mode="launch", why_no_live_check="no browser"
    )["renewal"]

    assert renewal["uses_browser"] is None
    assert "linkedin_login_browser" in renewal["mechanism"]


def test_silent_renew_stays_false_whatever_the_lapse_date_says(tmp_path):
    """The new keys must not have turned the renewal block into a promise.

    An expiry date is not a renewal path. A reader who sees a date next to
    ``silent_renew_available`` has to still be told, on the same object, that
    nothing will renew this for him.
    """
    for days in (364.2, -3.0):
        renewal = auth_module.session_info_offline(
            healthy_profile(tmp_path / f"d{days}", days=days),
            mode="launch",
            why_no_live_check="no browser",
        )["renewal"]
        assert renewal["silent_renew_available"] is False
        assert renewal["tool"] is None


def test_durability_keeps_its_fields_and_its_measured_note(tmp_path):
    durability = auth_module.session_info_offline(
        healthy_profile(tmp_path), mode="launch", why_no_live_check="no browser"
    )["durability"]

    assert durability["survives_server_restart"] is True
    assert durability["survives_machine_reboot"] is True
    assert durability["stored_in"]
    assert durability["why"]
    assert "365-day" in durability["measured_here"]


# ---------------------------------------------------------------------------
# 3. No credential value, anywhere, on any path
# ---------------------------------------------------------------------------


def test_the_offline_result_carries_no_cookie_value(tmp_path, caplog):
    with caplog.at_level("DEBUG"):
        result = auth_module.session_info_offline(
            healthy_profile(tmp_path), mode="launch", why_no_live_check="no browser"
        )
    assert_no_leak(result, PLANTED_SECRET, caplog=caplog)


async def test_the_live_result_carries_no_cookie_value(patched_navigation, caplog):
    page = FakePage(
        cookies={"li_at": PLANTED_SECRET, "JSESSIONID": PLANTED_JSESSIONID},
        expiries={"li_at": time.time() + 300 * 86400},
        responses=[me_response()],
    )
    with caplog.at_level("DEBUG"):
        result = await auth_module.session_info(page)

    assert_no_leak(result, PLANTED_SECRET, caplog=caplog)
    assert_no_leak(result, PLANTED_JSESSIONID, caplog=caplog)


def test_a_logout_result_carries_no_cookie_value(tmp_path, monkeypatch, caplog):
    """The jar is erased with the planted token inside it. Nothing may carry
    it out -- not the result, not a log line, not an error string."""
    unlocked(tmp_path, monkeypatch)
    profile = healthy_profile(tmp_path)

    with caplog.at_level("DEBUG"):
        result = auth_module.logout(profile, confirm=True)

    assert result["cleared"] is True
    assert_no_leak(result, PLANTED_SECRET, caplog=caplog)


def test_that_leak_check_can_actually_fail():
    """The control for the three assertions above, at input they must reject.

    The version this replaced planted the credential VERBATIM, which is the
    one case the old substring hunt already handled -- so it certified the
    only thing that was never broken. These two are the cases that were
    measured GREEN on a leaking build: the whole credential base64'd, and the
    whole credential split across two sibling fields.
    """
    import base64

    encoded = base64.b64encode(PLANTED_SECRET.encode()).decode()
    half = len(PLANTED_SECRET) // 2

    for payload in (
        {"credential": {"value": PLANTED_SECRET}},
        {"credential": {"fingerprint": encoded}},
        {"credential": {"head": PLANTED_SECRET[:half],
                        "tail": PLANTED_SECRET[half:]}},
    ):
        assert find_leaks(payload, PLANTED_SECRET), payload


# ---------------------------------------------------------------------------
# 4. linkedin_logout: the unconfirmed call performs NOTHING
# ---------------------------------------------------------------------------


def test_the_snapshot_instrument_can_see_a_change(tmp_path):
    """The control for every "not one byte changed" assertion below.

    Without it, a snapshot function that returned ``{}`` would make all of
    them pass forever.
    """
    profile = healthy_profile(tmp_path)
    before = snapshot(profile)
    assert before, "the snapshot saw no files at all"

    jar_of(profile).unlink()

    assert snapshot(profile) != before


def test_the_tripwire_would_stop_an_erase_of_the_real_profile():
    """The control for the autouse fixture above.

    A safety net nobody has driven at the thing it catches is a safety net
    nobody can trust. This drives it at the real jar path -- and reaches
    nothing, because the guard raises strictly before the real erase runs.
    """
    from linkedin_server.config import CHROME_PROFILE

    with pytest.raises(AssertionError) as excinfo:
        auth_module._erase(CHROME_PROFILE / "Default" / "Network" / "Cookies")

    assert "real Chrome profile" in str(excinfo.value)


def test_an_unconfirmed_logout_changes_not_one_byte(tmp_path, monkeypatch):
    """The assertion this whole tool is built around."""
    profile = healthy_profile(tmp_path)
    unlocked(tmp_path, monkeypatch)
    touched = erase_recorder(monkeypatch)
    before = snapshot(profile)

    result = auth_module.logout(profile, confirm=False)

    assert touched == [], touched
    assert "failed" not in result
    assert snapshot(profile) == before
    assert jar_of(profile).is_file()
    assert result["cleared"] is False


def test_the_erase_recorder_fills_on_a_confirmed_call(tmp_path, monkeypatch):
    """The control, and the one that gives the assertion above its teeth.

    ``touched == []`` is only a finding if the SAME recorder fills up when
    the call IS confirmed. Without this, a logout that had lost its erase
    step entirely would leave the test above green.
    """
    profile = healthy_profile(tmp_path)
    unlocked(tmp_path, monkeypatch)
    touched = erase_recorder(monkeypatch)

    result = auth_module.logout(profile, confirm=True)

    assert touched, "the confirmed path never reached the erase step"
    # The trap raised, so the tool reports a failure rather than a success --
    # which is itself the second half of "a destructive tool never claims
    # more than it did".
    assert result["cleared"] is False
    assert result["failed"]


def test_an_unconfirmed_logout_previews_exactly_what_would_go(tmp_path):
    profile = healthy_profile(tmp_path)

    preview = auth_module.logout(profile, confirm=False)["preview"]
    would_erase = preview["would_erase"]

    assert len(would_erase) == 4, would_erase
    assert would_erase[0].endswith("Cookies")
    assert [name.rsplit("Cookies", 1)[-1] for name in would_erase[1:]] == [
        "-journal",
        "-wal",
        "-shm",
    ]


def test_the_preview_says_what_the_sign_in_cost_and_how_to_get_back(tmp_path):
    """A confirmation prompt that does not price the thing it is about is a
    prompt somebody clicks through."""
    preview = auth_module.logout(healthy_profile(tmp_path), confirm=False)["preview"]

    assert "full day" in preview["cost_to_re_establish"]
    assert "full day" in preview["would_lose"]
    assert "linkedin_login_browser" in preview["recovery_is_by_hand"]
    assert "himself" in preview["recovery_is_by_hand"]
    assert "confirm=True" in preview["to_proceed"]


def test_the_preview_says_it_does_not_sign_you_out_on_linkedin(tmp_path):
    """The likeliest wrong belief about a tool called logout."""
    result = auth_module.logout(healthy_profile(tmp_path), confirm=False)
    side = result["preview"]["linkedin_side"].lower()

    assert "nothing here reaches linkedin" in side
    assert "no request" in side
    assert "account is untouched" in side


def test_an_unconfirmed_logout_does_not_even_read_the_profile(
    tmp_path, monkeypatch
):
    """It previews a profile that is not there, and says the same thing.

    A preview that stat-ed the jar would answer differently for a missing
    profile. Answering identically is the proof that no filesystem call was
    made at all -- the strongest available reading of "performs nothing".
    """
    real = healthy_profile(tmp_path)
    missing = tmp_path / "no-such-profile-anywhere"

    from_real = auth_module.logout(real, confirm=False)
    from_missing = auth_module.logout(missing, confirm=False)

    assert from_real["cleared"] is False
    assert from_missing["cleared"] is False
    assert from_real["reason"] == from_missing["reason"]
    assert from_real["scope"] == from_missing["scope"]
    assert len(from_missing["preview"]["would_erase"]) == 4


def test_an_unconfirmed_logout_does_not_claim_a_verdict(tmp_path):
    """cleared false is not "you are signed out". Nothing was measured."""
    result = auth_module.logout(healthy_profile(tmp_path), confirm=False)

    assert result["cleared"] is False
    assert result["authenticated"] is None
    assert result["authenticated"] is not False
    assert result["recover_by"] == "linkedin_login_browser"


# ---------------------------------------------------------------------------
# 5. linkedin_logout: the confirmed erase
# ---------------------------------------------------------------------------


def test_a_confirmed_logout_erases_the_jar_and_says_so(tmp_path, monkeypatch):
    unlocked(tmp_path, monkeypatch)
    profile = healthy_profile(tmp_path)
    assert jar_of(profile).is_file()

    result = auth_module.logout(profile, confirm=True)

    assert result["cleared"] is True
    assert not jar_of(profile).is_file()
    # The directory itself stays. A logout is not a profile teardown.
    assert Path(profile).is_dir()
    assert result["erased"], result


def test_a_confirmed_logout_states_the_scope_the_loss_and_the_way_back(
    tmp_path, monkeypatch
):
    unlocked(tmp_path, monkeypatch)
    result = auth_module.logout(healthy_profile(tmp_path), confirm=True)

    assert "Default/Network/Cookies" in result["scope"]
    assert "-journal" in result["scope"] and "-wal" in result["scope"]
    assert "profile directory itself stays" in result["scope"]
    assert "full day" in result["what_is_lost"]
    assert result["recover_by"] == "linkedin_login_browser"


def test_the_false_a_confirmed_logout_returns_is_a_provable_one(
    tmp_path, monkeypatch
):
    """The single place in this server where a false is not a measurement.

    It is allowed here precisely because it needs no measurement: li_at is
    gone, every tool authenticates with li_at and nothing else, so there is
    no authenticated request left to make. The reason has to SAY that, or it
    is indistinguishable from the guess this server refuses to make.
    """
    unlocked(tmp_path, monkeypatch)
    result = auth_module.logout(healthy_profile(tmp_path), confirm=True)

    assert result["authenticated"] is False
    assert "li_at is gone" in result["reason"]
    assert "no authenticated request can be made" in result["reason"]


def test_a_confirmed_logout_takes_the_journal_siblings_too(tmp_path, monkeypatch):
    """A jar erased without its journal is a jar sqlite may rebuild."""
    unlocked(tmp_path, monkeypatch)
    profile = healthy_profile(tmp_path)
    journal = jar_of(profile).with_name("Cookies-journal")
    journal.write_bytes(b"rollback journal")

    result = auth_module.logout(profile, confirm=True)

    assert result["cleared"] is True
    assert not journal.exists()
    assert len(result["erased"]) == 2, result["erased"]


def test_a_logout_on_a_profile_that_was_never_signed_in_is_not_a_failure(
    tmp_path, monkeypatch
):
    unlocked(tmp_path, monkeypatch)

    result = auth_module.logout(tmp_path / "never-signed-in", confirm=True)

    assert result["cleared"] is False
    assert result["erased"] == []
    assert "nothing to take" in result["reason"]
    # Not a verdict on a session either. There was no session to have one on.
    assert result["authenticated"] is None


# ---------------------------------------------------------------------------
# 6. linkedin_logout: the refusals that must not erase
# ---------------------------------------------------------------------------


def test_a_locked_profile_is_never_erased(tmp_path, monkeypatch):
    """Erasing a jar out from under a live Chromium corrupts the profile --
    which costs the same day this tool is asking the operator about.

    The lock file here carries THIS process's pid, so ``live_holder`` runs
    its real aliveness probe against a process that genuinely exists rather
    than against a stub.
    """
    profile = healthy_profile(tmp_path)
    lock = tmp_path / "chrome-profile.lock"
    lock.write_text(f"{os.getpid()}\n", encoding="utf-8")
    monkeypatch.setattr(profile_lock_module, "_LOCK_FILE", lock)
    touched = erase_recorder(monkeypatch)
    before = snapshot(profile)

    result = auth_module.logout(profile, confirm=True)

    assert result["cleared"] is False
    assert touched == [], touched
    assert snapshot(profile) == before
    assert result["holder_pid"] == os.getpid()
    assert str(os.getpid()) in result["reason"]
    assert result["authenticated"] is None


def test_a_stale_lock_from_a_dead_process_does_not_block_forever(
    tmp_path, monkeypatch
):
    """The control for the refusal above.

    A guard that blocked on any lock file would block permanently after one
    crash, and the fix an operator would reach for is deleting a lock file by
    hand next to a profile he is trying not to break.
    """
    profile = healthy_profile(tmp_path)
    lock = tmp_path / "chrome-profile.lock"
    # Not a multiple of four and far past any live pid: it cannot be running.
    lock.write_text("999999999\n", encoding="utf-8")
    monkeypatch.setattr(profile_lock_module, "_LOCK_FILE", lock)

    result = auth_module.logout(profile, confirm=True)

    assert result["cleared"] is True
    assert "holder_pid" not in result


def test_a_logout_never_raises_when_the_os_refuses_a_file(
    tmp_path, monkeypatch
):
    """Never raises. A destructive tool that throws leaves a caller guessing
    how far it got, which is the worst possible state to be in."""
    unlocked(tmp_path, monkeypatch)
    profile = healthy_profile(tmp_path)

    def refuses(path):
        raise PermissionError(13, "used by another process", str(path))

    monkeypatch.setattr(auth_module, "_erase", refuses)

    result = auth_module.logout(profile, confirm=True)

    assert result["cleared"] is False
    assert result["failed"]
    assert "PermissionError" in result["failed"][0]
    assert result["authenticated"] is None
    assert jar_of(profile).is_file()


def test_a_logout_never_raises_on_a_path_that_is_not_a_profile(
    tmp_path, monkeypatch
):
    unlocked(tmp_path, monkeypatch)

    for target in (tmp_path / "missing", tmp_path):
        result = auth_module.logout(target, confirm=True)
        assert result["cleared"] is False
        assert result["recover_by"] == "linkedin_login_browser"


# ---------------------------------------------------------------------------
# 7. linkedin_logout reaches LinkedIn not at all
# ---------------------------------------------------------------------------


def _session_recorder(monkeypatch) -> list:
    """Records every attempt to start a browser, and hands back a dead one."""
    calls: list = []

    def session():
        calls.append("session")
        return _FailingSession(BrowserUnavailableError(PREFLIGHT_MESSAGE))

    monkeypatch.setattr(server_module.BROWSER, "session", session)
    return calls


@pytest.mark.parametrize("confirm", [False, True])
async def test_the_logout_tool_never_starts_a_browser(
    tmp_path, monkeypatch, confirm
):
    """No browser means no page, which means no request. This server stays
    read-only towards the platform even while erasing local state."""
    unlocked(tmp_path, monkeypatch)
    monkeypatch.setattr(server_module, "CHROME_PROFILE", healthy_profile(tmp_path))
    calls = _session_recorder(monkeypatch)

    result = await server_module.linkedin_logout(confirm=confirm)

    assert calls == [], "linkedin_logout reached for a browser"
    assert result["cleared"] is confirm


async def test_the_session_recorder_does_fill_on_a_tool_that_uses_a_browser(
    tmp_path, monkeypatch
):
    """The control. ``calls == []`` above is only a finding if this fills."""
    monkeypatch.setattr(server_module, "CHROME_PROFILE", healthy_profile(tmp_path))
    calls = _session_recorder(monkeypatch)

    await server_module.linkedin_session_info()

    assert calls == ["session"]


async def test_the_logout_tool_defaults_to_doing_nothing(tmp_path, monkeypatch):
    """The default reaches the operator through the TOOL, not only through the
    function under it. A default that only held one layer down is not one."""
    unlocked(tmp_path, monkeypatch)
    profile = healthy_profile(tmp_path)
    monkeypatch.setattr(server_module, "CHROME_PROFILE", profile)
    touched = erase_recorder(monkeypatch)
    before = snapshot(profile)

    result = await server_module.linkedin_logout()

    assert touched == [], touched
    assert snapshot(profile) == before
    assert result["cleared"] is False
    assert "preview" in result


async def test_the_logout_tool_erases_when_it_is_confirmed(tmp_path, monkeypatch):
    """The control for the default above."""
    unlocked(tmp_path, monkeypatch)
    profile = healthy_profile(tmp_path)
    monkeypatch.setattr(server_module, "CHROME_PROFILE", profile)

    result = await server_module.linkedin_logout(confirm=True)

    assert result["cleared"] is True
    assert not jar_of(profile).is_file()
