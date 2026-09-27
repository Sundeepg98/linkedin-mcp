"""THE DOWNLOAD TRANSPORT ON THE ATTACHED BROWSER -- Chrome's own download
behaviour, set over a browser-level DevTools session, with no context created.

Census row ``P C8`` (save the profile as a PDF) was filed blocked on transport,
and ``tests/test_profile_pdf_download_is_blocked_on_transport.py`` pinned the
reason: in ATTACH mode this package adopts the operator's own browser context
and never makes one, and Playwright's download option is an argument to the
call that MAKES one -- so the package had no call site to pass it at.

The ruling that answers it is ``D4-NO-OWN-BROWSER-CONTEXT`` (2026-09-24): the
package does not create its own context; P C8's download transport goes
through the DevTools download behaviour on the attached browser. This module is
that transport, and nothing more.

## HOW IT WORKS

1. A DevTools session on the BROWSER TARGET, from
   ``Browser.new_browser_cdp_session()`` -- which the installed Playwright
   driver's source implements as one ``Target.attachToBrowserTarget``. It
   attaches to the browser that is already there. It makes no context and
   opens no tab.
2. ``Browser.setDownloadBehavior`` with ``allowAndName``, a directory of this
   run's own under ``_state/downloads/`` (gitignored with the rest of
   ``_state/``), and download events switched on for this session.
3. The caller's ``trigger`` runs -- the act that starts the download. This
   module does not know or care what it is.
4. ``Browser.downloadWillBegin`` names the download's GUID;
   ``Browser.downloadProgress`` says when it is ``completed``. With
   ``allowAndName`` Chrome writes the file under that GUID, so the name on
   disk is one the BROWSER chose, never one the page chose.
5. The file is renamed to ``<label><suffix>`` -- a name THIS server chose --
   and, when the caller says what kind of file it expects, its first bytes
   are checked against that kind.
6. ``finally``: the behaviour is set back to ``default``, and the session is
   detached. Whatever happened above.

## WHAT PLAYWRIGHT ALREADY DOES AT ATTACH TIME, AND WHY THIS DOES NOT LEAN ON IT

DERIVED FROM THE INSTALLED DRIVER SOURCE (Playwright 1.63.0, the version in
this repository's virtualenv on 2026-09-24), NOT OBSERVED LIVE:
``connect_over_cdp`` builds the adopted default context's options without a
download setting, ``validateBrowserContextOptions`` then defaults that setting
to ``"accept"``, and ``CRBrowserContext.initialize`` sends
``Browser.setDownloadBehavior`` with ``allowAndName``, NO context id (so the
default context -- his own tabs) and Playwright's temporary artifacts
directory, which ``_connectOverCDPImpl`` removes when the connection closes.
The same holds at 1.40.0, the floor of this repository's ``playwright>=1.40``:
read in that release's driver source on 2026-09-24.

So "there is nowhere to write it" was true of THIS PACKAGE and not of the
library underneath it: until 2026-09-24, while this server was attached, a
download in any of his tabs was written into a temporary directory deleted
when the server disconnected. **:func:`reset_download_behaviour` closes that
at the attach itself:** ``cdp_bridge.attach`` calls it right after it
connects, and it sends ``default`` for that same context (no id), so from
the attach onward his downloads follow his own Chrome settings. The lane D
record's follow-up (``_audit/2026-09-24-lane-d-d6-pdf.md``) says why that,
and not the library's own ``no_defaults`` option, is the fix.

The capture does not rely on the library's default either, for three
reasons: it is a library default a version can change; it puts the file in
a directory this server does not name; and it is never undone. Here the
behaviour is set explicitly, the directory is ours, and the ``finally`` sets
it back.

## WHAT "RESTORED" MEANS, EXACTLY

``default`` is Chrome's OWN behaviour -- the state his browser was in before
anything attached to it. It is deliberately NOT Playwright's attach-time
setting above, which diverts his downloads into a directory that is later
deleted, and it is what the attach itself now sends. So after a capture, as
after the attach, downloads in his browser follow his own Chrome settings for
the rest of the attach session.

**THE RESTORATION IS SENT AND ACKNOWLEDGED, NOT MEASURED.** The protocol has
no call that reads the current download behaviour back, so nothing here can
observe it. ``behaviour_restored`` says the ``default`` call returned without
raising, and it says no more than that.

## THE WINDOW, AND WHOSE FILES MIGHT LAND IN IT

The behaviour belongs to the BROWSER CONTEXT, not to one tab, and his own tabs
share the context this server adopted. So between the set and the restore --
bounded by the two timeouts below -- a download HE starts would land in this
run's directory too. The first download to begin is the one this capture
takes; any other is COUNTED in ``other_downloads`` and LEFT WHERE IT LANDED.
Nothing here ever deletes a file.

## OFF BY DEFAULT, AND ATTACH ONLY

Nothing is CAPTURED unless ``LINKEDIN_ENABLE_CDP_DOWNLOADS`` is set, read at
call time. With the flag off the capture returns ``downloads_disabled`` before
it makes a directory or a session. In LAUNCH mode it returns
``not_attached``: D4 scopes this transport to the attached browser.

The RESET is not behind the switch. It takes no download -- it gives his
back -- and ``cdp_bridge.attach`` runs it on every attach.

## WHAT CROSSES INTO THE RESULT

The browser's own GUID is checked against a GUID's shape before it is used as
a file name. The page's suggested file name and the download's url are never
returned and never decide anything, except that ``from_linkedin`` is ONE
BOOLEAN: whether the url's host is LinkedIn's. A failure carries the
exception's TYPE and never its text, because text can quote the page
(``ERROR-MESSAGE-RULED-AT-THE-RAISE``). The saved path goes through
``config.display``, because an absolute path on this machine carries a
username.

## THE ONLY PROTOCOL METHOD IT MAY SEND

:data:`CDP_METHODS` is a closed table, and :func:`_send` -- the one place in
the package that calls a DevTools session's ``send`` -- refuses anything not
on it. Two functions open a session -- the capture and the reset -- and both
send through it. ``readonly.scan_source_for_mutations`` has no pattern for a
DevTools ``send`` at all, so this table and ``tests/test_cdp_download.py``,
which pins the package's send and session sites by AST, are what stand in
for one.

## WHAT THIS IS NOT

It is not a press and not a navigation, and it reads nothing off a page. The
act that starts P C8's download is LinkedIn's own "Save to PDF" item behind
the profile's "More" menu, and no press in this package reaches it yet, so
nothing calls the capture, and
``tests/test_profile_pdf_download_is_blocked_on_transport.py``
fails the moment anything does. ``cdp_bridge`` imports this module for the
reset alone.
"""

from __future__ import annotations

import asyncio
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any, Awaitable, Callable, Optional
from urllib.parse import urlsplit

from linkedin_server.config import STATE_DIR, display, logger

#: The switch. Read at call time, so a test can set it without a reload.
DOWNLOADS_FLAG = "LINKEDIN_ENABLE_CDP_DOWNLOADS"

#: Where captured files go: under the gitignored ``_state/``, one directory per
#: capture, so a file already there can never be mistaken for this run's.
DOWNLOAD_ROOT = STATE_DIR / "downloads"

#: THE CLOSED TABLE of DevTools methods this module may send. One entry.
SET_DOWNLOAD_BEHAVIOR = "Browser.setDownloadBehavior"
CDP_METHODS: frozenset[str] = frozenset({SET_DOWNLOAD_BEHAVIOR})

#: The two events the capture listens to, on its own session only.
EVENT_BEGIN = "Browser.downloadWillBegin"
EVENT_PROGRESS = "Browser.downloadProgress"

#: How long to wait for a download to BEGIN after the trigger returns, and then
#: to COMPLETE. They bound the window in which his own downloads could land in
#: this run's directory, which is the reason they are not larger.
BEGIN_TIMEOUT_S = 20.0
COMPLETE_TIMEOUT_S = 60.0

#: The label names the saved file. It is this server's word, never a page's,
#: and its shape admits no separator and no dot.
_LABEL = re.compile(r"[a-z][a-z0-9-]{0,31}")
#: An optional extension, lower case, one dot.
_SUFFIX = re.compile(r"(?:\.[a-z0-9]{1,8})?")
#: A GUID's shape. The browser chooses it; it is still checked before it
#: becomes a path component, because a check costs nothing and a path does.
_GUID = re.compile(r"[0-9A-Fa-f][0-9A-Fa-f-]{7,63}")

#: The hosts ``from_linkedin`` answers for. Answered as one boolean.
_LINKEDIN_HOSTS = ("linkedin.com", "licdn.com")

#: EVERY value ``why`` can take. Closed, so a caller can branch on it.
WHY: tuple[str, ...] = (
    "saved",
    "downloads_disabled",
    "bad_label",
    "bad_suffix",
    "not_attached",
    "run_dir_failed",
    "session_failed",
    "behaviour_not_set",
    "trigger_raised",
    "no_download_began",
    "download_incomplete",
    "download_canceled",
    "bad_guid",
    "file_missing",
    "rename_failed",
    "magic_mismatch",
)


class CdpMethodRefused(RuntimeError):
    """A DevTools method that is not on :data:`CDP_METHODS`.

    Raised, never returned: it can only be a defect in this package, and a
    defect that returned a verdict would read as a download that did not
    happen.
    """


def downloads_enabled() -> bool:
    """Is the switch on? Off unless ``LINKEDIN_ENABLE_CDP_DOWNLOADS`` says so."""
    return os.environ.get(DOWNLOADS_FLAG, "").strip().lower() in {
        "1", "true", "yes", "on",
    }


def attached_browser(page: Any, *, attached: bool) -> Any:
    """The Playwright ``Browser`` behind ``page`` in ATTACH mode, else ``None``.

    ``attached`` is the caller's reading of ``browser.BROWSER.attached``. It is
    passed in rather than read here so that nothing in this module decides the
    session model. In LAUNCH mode this returns ``None`` and
    :func:`capture_download` refuses with ``not_attached``.

    Synchronous on purpose: it reads two attributes and awaits nothing.
    """
    if not attached:
        return None
    context = getattr(page, "context", None)
    return getattr(context, "browser", None)


async def _send(session: Any, method: str, params: dict[str, Any]) -> Any:
    """THE ONE DevTools ``send`` IN THE PACKAGE, and it takes only the table."""
    if method not in CDP_METHODS:
        raise CdpMethodRefused(
            f"{method!r} is not on cdp_download.CDP_METHODS; this module sends "
            f"{sorted(CDP_METHODS)} and nothing else"
        )
    return await session.send(method, params)


def _behaviour(run_dir: Path) -> dict[str, Any]:
    """What is sent to take the download: Chrome names the file by its GUID."""
    return {
        "behavior": "allowAndName",
        "downloadPath": str(run_dir),
        "eventsEnabled": True,
    }


#: What is sent in the ``finally``: Chrome's own behaviour.
_RESTORE: dict[str, Any] = {"behavior": "default"}


async def _set_behaviour(session: Any, run_dir: Path) -> None:
    """Point this browser's downloads at ``run_dir``, named by GUID.

    Its own function so the control in ``tests/test_cdp_download.py`` can
    remove exactly this step and show the capture failing without it.
    """
    await _send(session, SET_DOWNLOAD_BEHAVIOR, _behaviour(run_dir))


def _is_linkedin(url: Any) -> Optional[bool]:
    """ONE BOOLEAN about the download's host. The url itself goes nowhere."""
    if not isinstance(url, str):
        return None
    try:
        host = (urlsplit(url).hostname or "").lower()
    except ValueError:
        return None
    return any(host == d or host.endswith("." + d) for d in _LINKEDIN_HOSTS)


class _Watch:
    """The events one capture has seen. Handlers are synchronous and cheap."""

    def __init__(self) -> None:
        self.began = asyncio.Event()
        self.finished = asyncio.Event()
        self.guid: Optional[str] = None
        self.begins = 0
        self.others = 0
        self.from_linkedin: Optional[bool] = None
        self.final_state: Optional[str] = None

    def on_begin(self, params: Any) -> None:
        params = params if isinstance(params, dict) else {}
        self.begins += 1
        guid = params.get("guid")
        if self.guid is None and isinstance(guid, str):
            self.guid = guid
            self.from_linkedin = _is_linkedin(params.get("url"))
            self.began.set()
        else:
            self.others += 1

    def on_progress(self, params: Any) -> None:
        params = params if isinstance(params, dict) else {}
        if self.guid is None or params.get("guid") != self.guid:
            return
        state = params.get("state")
        if state in ("completed", "canceled"):
            self.final_state = state
            self.finished.set()


def _blank(label: Any) -> dict[str, Any]:
    """The result, before anything has happened. Every key, every time."""
    return {
        "saved": False,
        "why": None,
        "label": label if isinstance(label, str) and _LABEL.fullmatch(label) else None,
        "file": None,
        "bytes": None,
        "magic_ok": None,
        "downloads_began": 0,
        "other_downloads": 0,
        "from_linkedin": None,
        "final_state": None,
        "behaviour_restored": None,
        "restore_error": None,
        "error": None,
        "context_created": False,
        "transport": f"cdp:{SET_DOWNLOAD_BEHAVIOR}",
    }


def _refused(result: dict[str, Any], why: str, error: Optional[str] = None) -> dict[str, Any]:
    result["why"] = why
    if error is not None:
        result["error"] = error
    return result


def _run_directory(root: Path, label: str) -> Path:
    """A directory no earlier capture can have written into."""
    stamp = time.strftime("%Y%m%d-%H%M%S")
    return Path(root) / f"{label}-{stamp}-{uuid.uuid4().hex[:8]}"


async def capture_download(
    browser: Any,
    trigger: Callable[[], Awaitable[Any]],
    *,
    label: str,
    suffix: str = "",
    expect_magic: Optional[bytes] = None,
    root: Optional[Path] = None,
    begin_timeout_s: float = BEGIN_TIMEOUT_S,
    complete_timeout_s: float = COMPLETE_TIMEOUT_S,
) -> dict[str, Any]:
    """Run ``trigger`` with this browser's downloads pointed at a directory of ours.

    ``browser`` is the ATTACHED Playwright ``Browser`` -- use
    :func:`attached_browser` -- or ``None``. ``trigger`` is an argument-less
    coroutine function that performs the act which starts the download.
    ``label`` and ``suffix`` name the saved file. ``expect_magic``, when given,
    is the byte string the file must begin with (``b"%PDF-"`` for a PDF).

    Returns the dict :func:`_blank` describes. ``saved`` is True only when a
    download began, completed, landed under its GUID, was renamed to
    ``<label><suffix>`` and -- if ``expect_magic`` was given -- begins with it.
    ``why`` is one of :data:`WHY`. Never raises, except
    :class:`CdpMethodRefused`, which is a defect in this module.
    """
    result = _blank(label)
    if not downloads_enabled():
        return _refused(result, "downloads_disabled")
    if not isinstance(label, str) or not _LABEL.fullmatch(label):
        return _refused(result, "bad_label")
    if not isinstance(suffix, str) or not _SUFFIX.fullmatch(suffix):
        return _refused(result, "bad_suffix")
    if browser is None or not hasattr(browser, "new_browser_cdp_session"):
        return _refused(result, "not_attached")

    run_dir = _run_directory(root if root is not None else DOWNLOAD_ROOT, label)
    try:
        run_dir.mkdir(parents=True, exist_ok=False)
    except OSError as exc:
        return _refused(result, "run_dir_failed", type(exc).__name__)

    try:
        session = await browser.new_browser_cdp_session()
    except Exception as exc:  # noqa: BLE001 -- reported by type, never by text
        return _refused(result, "session_failed", type(exc).__name__)

    watch = _Watch()
    attempted = False
    try:
        try:
            session.on(EVENT_BEGIN, watch.on_begin)
            session.on(EVENT_PROGRESS, watch.on_progress)
        except Exception as exc:  # noqa: BLE001
            return _refused(result, "session_failed", type(exc).__name__)
        attempted = True
        try:
            await _set_behaviour(session, run_dir)
        except CdpMethodRefused:
            raise
        except Exception as exc:  # noqa: BLE001
            return _refused(result, "behaviour_not_set", type(exc).__name__)

        try:
            await trigger()
        except Exception as exc:  # noqa: BLE001 -- the TYPE only: text can quote a page
            return _refused(result, "trigger_raised", type(exc).__name__)

        try:
            await asyncio.wait_for(watch.began.wait(), timeout=begin_timeout_s)
        except asyncio.TimeoutError:
            return _refused(result, "no_download_began")
        try:
            await asyncio.wait_for(watch.finished.wait(), timeout=complete_timeout_s)
        except asyncio.TimeoutError:
            return _refused(result, "download_incomplete")
        if watch.final_state == "canceled":
            return _refused(result, "download_canceled")

        guid = watch.guid or ""
        if not _GUID.fullmatch(guid):
            return _refused(result, "bad_guid")
        landed = run_dir / guid
        if not landed.is_file():
            return _refused(result, "file_missing")
        try:
            result["bytes"] = landed.stat().st_size
            if expect_magic is not None:
                with landed.open("rb") as handle:
                    result["magic_ok"] = (
                        handle.read(len(expect_magic)) == expect_magic
                    )
        except OSError as exc:
            return _refused(result, "file_missing", type(exc).__name__)
        target = run_dir / f"{label}{suffix}"
        try:
            landed.replace(target)
        except OSError as exc:
            return _refused(result, "rename_failed", type(exc).__name__)
        result["file"] = display(target)
        if expect_magic is not None and not result["magic_ok"]:
            return _refused(result, "magic_mismatch")
        result["saved"] = True
        result["why"] = "saved"
        return result
    finally:
        result["downloads_began"] = watch.begins
        result["other_downloads"] = watch.others
        result["from_linkedin"] = watch.from_linkedin
        result["final_state"] = watch.final_state
        if attempted:
            try:
                await _send(session, SET_DOWNLOAD_BEHAVIOR, dict(_RESTORE))
                result["behaviour_restored"] = True
            except Exception as exc:  # noqa: BLE001
                result["behaviour_restored"] = False
                result["restore_error"] = type(exc).__name__
                logger.warning(
                    "cdp download: restoring the download behaviour raised %s",
                    type(exc).__name__,
                )
        for event, handler in ((EVENT_BEGIN, watch.on_begin),
                               (EVENT_PROGRESS, watch.on_progress)):
            try:
                session.remove_listener(event, handler)
            except Exception as exc:  # noqa: BLE001 -- detaching below ends them anyway
                logger.debug("cdp download: removing a listener raised %s",
                             type(exc).__name__)
        try:
            await session.detach()
        except Exception as exc:  # noqa: BLE001
            logger.debug("cdp download: detach raised %s", type(exc).__name__)


#: How long each step of the attach-time reset may take before it is
#: abandoned. It is one session and one command on a local socket; the bound
#: exists so a wedged browser cannot hang the attach, not because the reset
#: is slow.
RESET_TIMEOUT_S = 10.0


async def reset_download_behaviour(
    browser: Any, *, timeout_s: float = RESET_TIMEOUT_S
) -> dict[str, Any]:
    """Hand the attached browser's downloads back to Chrome's own behaviour.

    ``cdp_bridge.attach`` calls this right after it connects, because the
    library's own handshake has just pointed his default context's downloads
    at a temporary directory it deletes on disconnect (the module docstring's
    section on what Playwright does at attach time). One browser-level
    session, one command -- the same ``default`` the capture restores with --
    sent with NO context id, which is the context the library's own setting
    named. The session is detached afterwards whatever happened.

    Returns ``{"restored": bool, "error": <exception TYPE or None>}``.
    ``restored`` means the command was SENT AND ACKNOWLEDGED: the protocol
    has no call that reads the behaviour back. A browser with no DevTools
    session method returns ``error: "no_cdp_session"``. Never raises,
    except :class:`CdpMethodRefused`, which is a defect in this module; each
    step is bounded by ``timeout_s``.

    NOT behind ``LINKEDIN_ENABLE_CDP_DOWNLOADS``: this takes no download, it
    gives his back.
    """
    if browser is None or not hasattr(browser, "new_browser_cdp_session"):
        return {"restored": False, "error": "no_cdp_session"}
    session = None
    try:
        session = await asyncio.wait_for(
            browser.new_browser_cdp_session(), timeout=timeout_s
        )
        await asyncio.wait_for(
            _send(session, SET_DOWNLOAD_BEHAVIOR, dict(_RESTORE)), timeout=timeout_s
        )
        outcome: dict[str, Any] = {"restored": True, "error": None}
    except CdpMethodRefused:
        raise
    except Exception as exc:  # noqa: BLE001 -- the TYPE only, never the text
        outcome = {"restored": False, "error": type(exc).__name__}
    finally:
        if session is not None:
            try:
                await asyncio.wait_for(session.detach(), timeout=timeout_s)
            except Exception as exc:  # noqa: BLE001
                logger.debug(
                    "cdp download: detaching the reset session raised %s",
                    type(exc).__name__,
                )
    return outcome
