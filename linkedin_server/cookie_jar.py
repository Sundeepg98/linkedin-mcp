"""Read cookie EXPIRY out of a Chrome profile without launching Chrome.

Everything this server knows about the operator's LinkedIn session lives in a
persistent Chrome profile. Asking Playwright how long that session has left
means LAUNCHING that profile: it takes the cross-process profile lock, costs
seconds, and cannot run at all while a browser already holds the profile. But
the only fact wanted is a date, and that date is already sitting in the
profile's SQLite cookie jar. This module reads it straight off disk, so "when
does my login expire" stops being a question that needs a browser.

Two rules make that safe. Both are the point of this module, not details:

* NO COOKIE VALUE IS EVER FETCHED. The query names its columns explicitly,
  and the ones it names are metadata only: name, host, expiry, persistence.
  Neither the plaintext value column nor the DPAPI-sealed blob beside it is
  ever selected, and no wildcard select exists here. A value that is never
  read cannot reach a return value, a log line, or a traceback -- and a leak
  here would hand over a working LinkedIn login, not merely an expiry date.
* THE LIVE FILE IS NEVER OPENED. sqlite writes to a database it opens even
  when a caller only reads: it replays a hot journal, it can checkpoint a
  WAL, it takes locks. The file in question is the operator's real signed-in
  profile, which took a full day to establish and which Chrome may have open
  right now. So the jar is COPIED to a temp dir first, together with any
  journal / WAL / SHM sibling (a copy taken without its journal can hand back
  rows the journal would have rolled back, i.e. stale ones), the COPY is
  opened, and the copy is deleted in a ``finally``. ``sqlite3.connect`` is
  never handed the original path, not even in read-only mode.

The records returned are shaped like Playwright's ``BrowserContext.cookies()``
entries -- ``{"name": ..., "expires": <posix seconds as float, or -1.0>}`` --
because they are fed straight into ``auth._cookie_expiry``, which already
speaks exactly that convention (``-1`` meaning "dies with the browser").
Nothing else is included, deliberately: a record that carries no value cannot
leak one, and the caller needs nothing else.

Chrome stores ``expires_utc`` in the WebKit epoch: MICROSECONDS since
1601-01-01 UTC, not the Unix epoch. Read as Unix microseconds it lands in the
year 2396; read as Unix seconds it lands past the year 400,000,000; read
without the offset at all it lands in 1601. Every wrong reading still looks
like a date, which is why the offset below is applied exactly, in integer
arithmetic, rather than approximated in floating point.
"""

from __future__ import annotations

import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Iterable

# config IS IMPORTED LATE, inside scrub() below, rather than at module level:
# this module is imported by config's own consumers, so a module-level import
# would risk a cycle. The indirection is deliberate rather than untidy.

#: Seconds between 1601-01-01 UTC (the WebKit epoch Chrome counts from) and
#: 1970-01-01 UTC (the POSIX epoch everything else counts from): 134774 days
#: of exactly 86400 seconds. Both epochs are proleptic and neither counts
#: leap seconds, so this is a constant, not an approximation.
WEBKIT_EPOCH_OFFSET_S = 11644473600

#: Where Chrome keeps the jar inside a user-data dir. Chrome moved it under
#: ``Network/`` in M96; the ``NetworkDataMigrated`` marker beside it is how a
#: profile records that move.
JAR_RELPATH = ("Default", "Network", "Cookies")

#: Sibling files sqlite may need in order to read the jar consistently.
#: ``-journal`` is a rollback journal; ``-wal`` and ``-shm`` appear when the
#: database is in WAL mode. Any that exist are copied alongside the jar.
JAR_SIBLING_SUFFIXES = ("-journal", "-wal", "-shm")

#: The registrable domain whose cookies this reader will report.
LINKEDIN_DOMAIN = "linkedin.com"

#: Metadata columns only, named one by one. This query is the enforcement
#: point for "a cookie value is never fetched" -- see the module docstring.
_JAR_QUERY = (
    "SELECT name, host_key, expires_utc, has_expires, is_persistent "
    "FROM cookies"
)


class CookieJarUnavailableError(Exception):
    """The cookie jar could not be read, and no answer is being invented.

    Raised INSTEAD of returning an empty list. An empty list because the
    profile directory is missing is indistinguishable from an empty list
    because the operator genuinely has no LinkedIn cookies, and the second
    one means "sign in again" while the first one means "you passed the wrong
    path" -- exactly the confusion this server refuses everywhere else.

    Deliberately NOT a subclass of anything in ``errors.py``. This module is
    a plain on-disk reader with no LinkedIn semantics; translating a missing
    jar into whatever a tool surface should say is the caller's job.

    The message always names the path that was tried and distinguishes the
    three ways this fails: no profile directory, no jar file, or sqlite
    refusing the copy.
    """


def scrub(text: str) -> str:
    """Relativise this server's own paths inside an error message.

    A thin wrapper so ``cookie_jar`` need not import ``config`` at module
    level. The work is ``config.scrub``, whose docstring already names the
    case that made this necessary: several messages here are built as
    ``f"...{path}...{exc}"`` and an OSError STRINGIFIES WITH THE FILENAME it
    failed on, so a path reaches a caller through the exception text even when
    every interpolation of its own is relativised.

    WHY THIS WAS UNCAUGHT FOR SO LONG. Every message below is on an ERROR
    path, and the one that finally leaked -- "could not be given a copy" --
    only runs when something else holds the jar's SQLite lock. That needs a
    live Chrome. So the guard was correct and simply never exercised until a
    browser was running during a test run, which is the same shape as the
    other defects found on this module today: right mechanism, wrong blast
    radius, and a check that only fires in a state the suite rarely reaches.
    """
    from linkedin_server.config import scrub as _scrub

    # A BLANKET REGEX WAS TRIED HERE AND REMOVED, because it fixed the leak by
    # destroying the diagnosis. Replacing every drive-letter run with <path>
    # also ate the JAR PATH THIS MESSAGE EXISTS TO NAME -- the class docstring
    # promises "the message always names the path that was tried", and two
    # tests assert it. In production the jar sits under the repo, so
    # config.scrub relativises it to _state/chrome-profile\... which is both
    # clean and useful; under pytest the profile is a tmp_path that scrub
    # cannot know, so the blanket rule erased it there and only there.
    #
    # The actual leak was never the jar. It was the TEMP DIRECTORY the copy
    # goes into, which stringifies as C:\Users\<name>\AppData\Local\Temp\...
    # and hands over a home directory, hence an account name. That path is an
    # implementation detail no caller can use, so it is no longer interpolated
    # into any message at all -- which fixes the leak at the source instead of
    # scrubbing it downstream.
    return str(_scrub(text))


def _is_linkedin_host(host_key: Any) -> bool:
    """Return True when a Chrome ``host_key`` belongs to LinkedIn.

    Chrome writes a leading dot for domain cookies (``.www.linkedin.com``)
    and no dot for host-only ones (``www.linkedin.com``). Matching is done on
    label boundaries rather than as a raw string suffix: a bare
    ``endswith("linkedin.com")`` would also accept ``notlinkedin.com``, which
    is a different site and can set a cookie with the same name.
    """
    if not isinstance(host_key, str):
        return False
    host = host_key.strip().lower().lstrip(".")
    return host == LINKEDIN_DOMAIN or host.endswith("." + LINKEDIN_DOMAIN)


def _expires_from_row(
    expires_utc: Any, has_expires: Any, is_persistent: Any
) -> float:
    """Convert one row's expiry columns into Playwright's ``expires`` field.

    Returns POSIX seconds as a float, or ``-1.0`` for a session cookie. A row
    is a session cookie when Chrome says so in EITHER flag (``has_expires``
    or ``is_persistent`` clear) or when it carries no usable timestamp -- the
    live profile stores ``JSESSIONID`` as ``expires_utc = 0, has_expires = 0,
    is_persistent = 0``, and older schemas may leave the column NULL.

    The conversion splits into whole seconds and microseconds before touching
    a float, so the result is exact rather than rounded through a 17-digit
    division.
    """
    if not has_expires or not is_persistent:
        return -1.0
    try:
        raw = int(expires_utc)
    except (TypeError, ValueError):
        return -1.0
    if raw <= 0:
        return -1.0
    seconds, micros = divmod(raw, 1000000)
    posix = float(seconds - WEBKIT_EPOCH_OFFSET_S) + micros / 1000000.0
    if posix <= 0.0:
        return -1.0
    return posix


def _copy_jar(jar: Path, dest_dir: Path) -> Path:
    """Copy the jar and any journal / WAL / SHM sibling into ``dest_dir``.

    ``shutil.copy2`` reads the source and writes the destination; it never
    modifies the original, which is the entire reason this function exists.
    Siblings keep their exact names, because sqlite looks for a journal only
    at ``<db>-journal``. Missing siblings are skipped -- a profile Chrome
    closed cleanly has no journal at all.
    """
    dest = dest_dir / jar.name
    shutil.copy2(jar, dest)
    for suffix in JAR_SIBLING_SUFFIXES:
        sibling = jar.with_name(jar.name + suffix)
        if sibling.is_file():
            shutil.copy2(sibling, dest_dir / sibling.name)
    return dest


def read_jar(profile_dir: Path, names: Iterable[str]) -> list[dict[str, Any]]:
    """Read expiry metadata for ``names`` out of a Chrome profile's cookie jar.

    Args:
        profile_dir: a Chrome user-data dir, e.g. ``_state/chrome-profile``.
            The jar is expected at ``Default/Network/Cookies`` beneath it.
        names: the cookie names to report, e.g. ``["li_at", "JSESSIONID"]``.

    Returns:
        One record per matching row, in the order the names were requested:
        ``{"name": str, "expires": float}``. ``expires`` is POSIX seconds, or
        ``-1.0`` for a session cookie. A requested name that is not in the jar
        is simply ABSENT from the list -- no placeholder record is emitted,
        because "not there" is a fact the caller already knows how to read.
        Only rows whose host key belongs to LinkedIn are considered.

    Raises:
        CookieJarUnavailableError: the profile directory is missing, the jar
            file is missing, or sqlite could not open or query the copy.
            Never an empty list in place of one of those.

    The live jar is never opened; see the module docstring.
    """
    wanted: list[str] = []
    for name in names:
        if name not in wanted:
            wanted.append(name)

    profile_dir = Path(profile_dir)
    if not profile_dir.is_dir():
        # SCRUBBED, from 2026-09-01, and it was the ONLY message in this
        # function that was not. Every other branch below wraps its text in
        # ``scrub`` and this one interpolated ``profile_dir`` raw.
        #
        # WHY IT SURVIVED SO LONG, and the answer is the finding rather than
        # the bug: THIS BRANCH ONLY FIRES WHEN NO PROFILE DIRECTORY EXISTS,
        # which is never true on a machine that has ever signed in -- which is
        # every machine either developer had ever run the suite on. The shared
        # working tree is green here BECAUSE it carries untracked runtime
        # state a fresh clone does not.
        #
        # It was found by running the suite in a DETACHED WORKTREE at the
        # commit: a pristine checkout has no ``_state/chrome-profile``, so
        # this guard fires before ``_copy_jar`` is ever reached, and the
        # forced-failure test below landed on it instead. For an MCP server
        # that string goes to the CLIENT -- into transcripts and logs --
        # carrying a home-directory path.
        #
        # AND IT IS THE SAME DEFECT THE TEST BELOW WAS WRITTEN ABOUT, one
        # layer down. That docstring argues that "a check whose firing depends
        # on whether an unrelated process is running is not a check". This one
        # depended on whether a DIRECTORY EXISTS -- quieter, same shape.
        raise CookieJarUnavailableError(
            scrub(
                f"chrome profile directory does not exist: {profile_dir} -- "
                "there is no cookie jar to read. Check the profile path, or "
                "sign in once so the profile gets created."
            )
        )

    jar = profile_dir.joinpath(*JAR_RELPATH)
    if not jar.is_file():
        raise CookieJarUnavailableError(
            scrub(
                f"cookie jar file does not exist: {jar} -- the profile "
                f"directory {profile_dir} is there but holds no cookie "
                "database yet, which is what a profile that has never "
                "been signed in to looks like."
            )
        )

    tmp_dir = Path(tempfile.mkdtemp(prefix="linkedin-cookie-jar-"))
    try:
        try:
            copy = _copy_jar(jar, tmp_dir)
        except OSError as e:
            raise CookieJarUnavailableError(
                scrub(
                    f"sqlite could not be given a copy of the cookie jar "
                    f"{jar}: copying it to a temporary directory failed ({e}). The live "
                    "jar is never opened directly, so this is where the "
                    "read stops."
                )
            ) from e

        try:
            # The COPY, never ``jar``. Opened writable on purpose: sqlite may
            # need to replay the copied journal, and the copy is disposable.
            con = sqlite3.connect(str(copy))
        except sqlite3.Error as e:
            raise CookieJarUnavailableError(
                scrub(
                    f"sqlite could not open the copy of the cookie jar "
                    f"{jar}: {e}"
                )
            ) from e
        try:
            rows = con.execute(_JAR_QUERY).fetchall()
        except sqlite3.Error as e:
            raise CookieJarUnavailableError(
                scrub(
                    f"sqlite could not query the copy of the cookie jar "
                    f"{jar}: {e}. The file exists but does "
                    "not look like a Chrome cookie database."
                )
            ) from e
        finally:
            con.close()
    finally:
        # Windows will not delete a file sqlite still has open, hence the
        # close above; ignore_errors keeps a cleanup problem from masking an
        # otherwise successful read.
        shutil.rmtree(tmp_dir, ignore_errors=True)

    found: dict[str, list[float]] = {}
    for name, host_key, expires_utc, has_expires, is_persistent in rows:
        if name not in wanted:
            continue
        if not _is_linkedin_host(host_key):
            continue
        found.setdefault(name, []).append(
            _expires_from_row(expires_utc, has_expires, is_persistent)
        )

    out: list[dict[str, Any]] = []
    for name in wanted:
        for expires in found.get(name, ()):
            out.append({"name": name, "expires": expires})
    return out
