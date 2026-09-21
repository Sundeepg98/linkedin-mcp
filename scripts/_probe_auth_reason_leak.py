"""RED PROOF: the session cookie reaches ``$.reason`` and the log, via auth.py.

THE CLAIM THIS PROBE ESTABLISHES, IN TWO HALVES THAT ARE MEASURED SEPARATELY
BECAUSE THEY ARE DIFFERENT FACTS.

    PREMISE  A failing ``page.request.get`` renders the WHOLE REQUEST into its
             own exception text, and that rendering enumerates every request
             header -- including ``cookie:``. This is a fact about Playwright.
             It can only be established by CALLING Playwright, so stage 1 does.

    DEFECT   ``auth.check_auth``'s request-failure handler interpolates
             ``str(exc)`` verbatim into a field it RETURNS and into a line it
             LOGS. This is a fact about this repository. It needs no browser,
             so stage 2 drives the REAL ``check_auth`` with the REAL specimen
             stage 1 captured.

Separating them matters. A probe that only fabricated an exception carrying a
cookie would prove the interpolation and assume the premise; a probe that only
called Playwright would prove the premise and assume the reach. Neither alone
is the finding.

## NOTHING HERE TOUCHES THE ACCOUNT

Stage 1 launches an EPHEMERAL headless chromium with ``chromium.launch()`` --
never ``launch_persistent_context``, never the configured Chrome profile,
never a CDP attach to a running browser. It is closed in a ``finally``. There
is no ``page.goto`` anywhere in this file: the only network verbs are
``page.request.get`` aimed at loopback addresses this process owns. Nothing
resolves a public name and nothing reaches linkedin.com.

## THE NEEDLE IS THE REPOSITORY'S OWN PLANT

``tests.leakwalk.PLANTED_LI_AT`` -- credential-LENGTH, credential-CHARSET, and
visibly a plant. It is used rather than a fresh token for two reasons: the
shipped hunt ``leakwalk.assert_no_leak`` already knows how to find every
rendering of it, and a four-letter marker was MEASURED unable to catch a
redaction bug that only fires on long high-entropy values.

**NO REAL CREDENTIAL IS READ, WRITTEN OR PRINTED BY THIS FILE.** The cookie
stage 1 installs is the plant, in a context that has never seen LinkedIn.

## EXIT CODES -- the probe inverts, which is what makes it a proof

    --expect leak    exit 0 while the defect reproduces, 1 once it is closed
    --expect clean   exit 0 once the defect is closed, 1 while it reproduces

So the SAME file is the red proof before the repair and the acceptance check
after it, and neither reading can be had by editing an expectation.

USAGE

    python scripts/_probe_auth_reason_leak.py --expect leak
    python scripts/_probe_auth_reason_leak.py --capture <path.json>
    python scripts/_probe_auth_reason_leak.py --replay <path.json> --expect clean
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import pathlib
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Optional

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.leakwalk import (  # noqa: E402
    PLANTED_JSESSIONID,
    PLANTED_LI_AT,
    find_leaks,
)

#: How long the hanging handler sleeps, and the ceiling the timeout branch is
#: given. The gap has to be wide enough that a slow box does not turn a
#: deliberate timeout into a flake.
HANG_SECONDS = 30.0
TIMEOUT_MS = 900


# ---------------------------------------------------------------------------
# A loopback server this process owns, so the timeout branch has something to
# hang against that is not somebody else's machine.
# ---------------------------------------------------------------------------


class _Hang(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler's spelling
        time.sleep(HANG_SECONDS)

    def log_message(self, *_args: Any) -> None:
        return


def _dead_port() -> int:
    """A port with nothing listening: bind it, read it, give it straight back."""
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = int(sock.getsockname()[1])
    sock.close()
    return port


# ---------------------------------------------------------------------------
# STAGE 1 -- what Playwright quotes. Needs the browser; runs once.
# ---------------------------------------------------------------------------


async def capture_specimens() -> list[dict[str, Any]]:
    """Raise two REAL ``APIRequestContext`` failures and record their text.

    The context is given the planted cookie for the loopback ORIGIN, which is
    the only way the header can appear on a loopback request at all -- a
    cookie scoped to another host is simply not sent, and a specimen built
    that way would record a silence that means nothing.
    """
    from playwright.async_api import async_playwright

    server = ThreadingHTTPServer(("127.0.0.1", 0), _Hang)
    hang_port = int(server.server_address[1])
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    dead_port = _dead_port()
    out: list[dict[str, Any]] = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            context = await browser.new_context()
            # The plant, scoped to loopback. Never a real value, never a real
            # origin, and this context has loaded no page at all.
            await context.add_cookies(
                [
                    {
                        "name": "li_at",
                        "value": PLANTED_LI_AT,
                        "url": f"http://127.0.0.1:{dead_port}",
                    },
                    {
                        "name": "li_at",
                        "value": PLANTED_LI_AT,
                        "url": f"http://127.0.0.1:{hang_port}",
                    },
                ]
            )
            page = await context.new_page()

            branches = [
                (
                    "connect_refused",
                    f"http://127.0.0.1:{dead_port}/identity",
                    None,
                ),
                (
                    "timeout",
                    f"http://127.0.0.1:{hang_port}/identity",
                    TIMEOUT_MS,
                ),
            ]
            for name, url, timeout_ms in branches:
                kwargs: dict[str, Any] = {}
                if timeout_ms is not None:
                    kwargs["timeout"] = timeout_ms
                try:
                    await page.request.get(url, **kwargs)
                except Exception as exc:  # noqa: BLE001 - the specimen
                    out.append(
                        {
                            "branch": name,
                            "exc_type": type(exc).__name__,
                            "exc_module": type(exc).__module__,
                            "text": str(exc),
                        }
                    )
                else:
                    out.append(
                        {
                            "branch": name,
                            "exc_type": None,
                            "exc_module": None,
                            "text": "",
                            "note": "DID NOT RAISE -- this row proves nothing",
                        }
                    )
            # ---------------------------------------------------------------
            # THE SECOND COOKIE-TOUCHING CALL IN THE SAME MODULE.
            #
            # ``auth._cookie_records`` wraps ``page.context.cookies(...)`` and
            # re-raises with ``f"...{type(exc).__name__}: {exc}"`` -- the same
            # VALUE-render shape as the defect, one function above the
            # docstring that claims the jar is "never logged, never persisted,
            # never returned". The census can see the shape; only driving it
            # can say whether THIS library call quotes what it was reading.
            # Assuming either way would be the error the whole wave is about.
            try:
                await context.close()
                await page.context.cookies("https://www.linkedin.com")
            except Exception as exc:  # noqa: BLE001 - the specimen
                out.append(
                    {
                        "branch": "cookie_jar_read_on_closed_context",
                        "exc_type": type(exc).__name__,
                        "exc_module": type(exc).__module__,
                        "text": str(exc),
                        "sink": "_cookie_records re-raise",
                    }
                )
            else:
                out.append(
                    {
                        "branch": "cookie_jar_read_on_closed_context",
                        "exc_type": None,
                        "exc_module": None,
                        "text": "",
                        "note": "DID NOT RAISE -- this row proves nothing",
                    }
                )
        finally:
            await browser.close()

    server.shutdown()
    server.server_close()
    return out


# ---------------------------------------------------------------------------
# STAGE 2 -- where the text goes. Needs no browser.
# ---------------------------------------------------------------------------


class _Collect(logging.Handler):
    """Every record this package emits, kept as its RENDERED message.

    Rendered rather than raw, because this package logs lazily
    (``logger.info("%s: %s", a, b)``) and the credential lives in ``args``,
    not in the format string. A collector that stored ``record.msg`` would
    record a clean-looking format string for a leaking line -- the exact shape
    of blindness this probe exists to refuse.
    """

    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.messages.append(record.getMessage())
        except Exception:  # noqa: BLE001 - a collector may never break a run
            self.messages.append(repr(record.args))


def _rebuild(spec: dict[str, Any]) -> Exception:
    """A stand-in whose ``str()`` is byte-for-byte the captured specimen.

    The class is generic on purpose. What ``check_auth`` does with an
    exception depends on its TEXT, not on its type, and building the real
    Playwright class here would make the probe depend on a private import
    path for nothing.
    """

    name = spec.get("exc_type") or "Error"
    cls = type(str(name), (Exception,), {})
    return cls(spec["text"])


async def drive(specimens: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Hand each specimen to the REAL check_auth, require_auth and session_info."""
    from tests.conftest import FakePage

    from linkedin_server import auth as auth_mod
    from linkedin_server.errors import AuthUnknownError, NotAuthenticatedError

    rows: list[dict[str, Any]] = []

    for spec in specimens:
        if not spec.get("text"):
            rows.append({**spec, "skipped": "no specimen text"})
            continue
        if spec.get("sink"):
            # Not a ``page.request.get`` specimen -- it belongs to a different
            # call site and is reported in stage 1 rather than driven through
            # check_auth, which would put it on a path it cannot reach.
            rows.append({**spec, "skipped": "different call site; see stage 1"})
            continue

        premise_leaks = find_leaks(spec["text"], PLANTED_LI_AT)

        # --- exit 1: the returned dict, via linkedin_auth_status -------------
        #
        # ATTACHED TO THE NAMED LOGGER, AND IT TOOK TWO WRONG ANSWERS TO GET
        # HERE. Both wrong answers reported the log channel CLEAN while four
        # fully-leaking log lines went to stderr in the same run.
        #
        #   1. ``logging.getLogger("linkedin_server")`` -- the package name,
        #      which is the obvious guess and is a SIBLING of the real logger,
        #      not an ancestor. Zero records.
        #   2. ``logging.getLogger()`` -- the root, which is where pytest's
        #      caplog attaches and so looks like the safe universal choice. It
        #      is not: config.py sets ``logger.propagate = False`` on purpose,
        #      because this server speaks MCP over stdio and a record reaching
        #      stdout corrupts the transport. Nothing propagates. Zero records.
        #
        # An absence check over an empty channel PASSES, so a log-leak
        # detector wired to either of those cannot fail -- it certifies
        # silence as cleanliness. ``tests/conftest.py`` carries the same scar
        # and the same fix, where it cost 14 call sites their log half.
        handler = _Collect()
        root = logging.getLogger("linkedin")
        root.addHandler(handler)
        previous = root.level
        root.setLevel(logging.DEBUG)
        try:
            page = FakePage(
                cookies={"li_at": PLANTED_LI_AT, "JSESSIONID": PLANTED_JSESSIONID},
                responses=[_rebuild(spec)],
            )
            result = await auth_mod.check_auth(page, warm=False)
        finally:
            root.removeHandler(handler)
            root.setLevel(previous)

        reason = str(result.get("reason", ""))
        model_leaks = find_leaks(result, PLANTED_LI_AT)
        log_leaks = find_leaks(handler.messages, PLANTED_LI_AT)

        # --- exit 3: the exception message, via require_auth -----------------
        page = FakePage(
            cookies={"li_at": PLANTED_LI_AT, "JSESSIONID": PLANTED_JSESSIONID},
            responses=[_rebuild(spec)],
        )
        raised_text = ""
        raised_type = ""
        try:
            await auth_mod.require_auth(page)
        except (AuthUnknownError, NotAuthenticatedError) as exc:
            raised_type = type(exc).__name__
            raised_text = str(exc)
        exc_leaks = find_leaks(raised_text, PLANTED_LI_AT)

        rows.append(
            {
                "branch": spec["branch"],
                "exc_type": spec["exc_type"],
                "premise_playwright_quotes_the_cookie": bool(premise_leaks),
                "authenticated": result.get("authenticated"),
                "session_cookie_present": result.get("session_cookie_present"),
                "reason": reason,
                "leak_model": bool(model_leaks),
                "leak_log": bool(log_leaks),
                "leak_exception": bool(exc_leaks),
                "raised": raised_type,
                "log_lines": len(handler.messages),
            }
        )
    return rows


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _mask(text: str, limit: int = 2000) -> str:
    """Render a specimen with the plant REPLACED, so stdout never carries it.

    The plant is synthetic, so printing it would harm nothing -- but a probe
    that prints credentials on its happy path teaches the next reader that a
    probe printing credentials is normal, and the next one will not be
    synthetic. The substitution also makes the LOCATION of the value visible,
    which the raw text does not.

    IT ALSO FOLDS TO ASCII, AND THAT IS A FINDING RATHER THAN A CONVENIENCE.
    Playwright writes its call log with U+2192 RIGHTWARDS ARROW. On a cp1252
    console this probe DIED trying to print it -- which is the cheapest
    possible demonstration that the text landing in ``$.reason`` is not ASCII
    and was never composed by anything in this repository.
    """
    shown = text.replace(PLANTED_LI_AT, "<PLANTED-CREDENTIAL-WAS-HERE>")
    shown = shown.replace(PLANTED_JSESSIONID, "<PLANTED-CSRF-WAS-HERE>")
    shown = shown.encode("ascii", "backslashreplace").decode("ascii")
    if len(shown) > limit:
        shown = shown[:limit] + "\n    ... truncated ..."
    return shown


def report(rows: list[dict[str, Any]], specimens: list[dict[str, Any]]) -> bool:
    """Print the finding. Returns True if ANY channel leaks."""
    print("=" * 74)
    print("STAGE 1 -- WHAT PLAYWRIGHT QUOTES (real browser, loopback only)")
    print("=" * 74)
    for spec in specimens:
        print(f"\n  branch      : {spec['branch']}")
        print(f"  exception   : {spec.get('exc_module')}.{spec.get('exc_type')}")
        carries = bool(find_leaks(spec.get("text", ""), PLANTED_LI_AT))
        print(f"  quotes the planted cookie: {carries}")
        print("  text, with the plant located and replaced:")
        for line in _mask(spec.get("text", "")).splitlines():
            print(f"    | {line}")

    print()
    print("=" * 74)
    print("STAGE 2 -- WHERE IT GOES (real check_auth / require_auth, no browser)")
    print("=" * 74)
    leaking = False
    for row in rows:
        if "skipped" in row:
            print(f"\n  {row['branch']}: SKIPPED ({row['skipped']})")
            continue
        any_leak = row["leak_model"] or row["leak_log"] or row["leak_exception"]
        leaking = leaking or any_leak
        print(f"\n  branch                   : {row['branch']}")
        print(f"  authenticated            : {row['authenticated']}")
        print(f"  session_cookie_present   : {row['session_cookie_present']}")
        print(f"  CHANNEL model  ($.reason): leak={row['leak_model']}")
        print(f"  CHANNEL log    (logger)  : leak={row['leak_log']}"
              f"  ({row['log_lines']} record(s))")
        print(f"  CHANNEL except ({row['raised'] or 'none'}): "
              f"leak={row['leak_exception']}")
        print("  $.reason, with the plant located and replaced:")
        for line in _mask(row["reason"]).splitlines():
            print(f"    | {line}")
    return leaking


async def _main_async(args: argparse.Namespace) -> int:
    if args.replay:
        specimens = json.loads(pathlib.Path(args.replay).read_text(encoding="utf-8"))
        # A replayed file carries a PLACEHOLDER where the value was, so the
        # committed artifact holds no credential shape at all. Put the plant
        # back before driving, or the probe measures a needle that is not there.
        for spec in specimens:
            spec["text"] = str(spec.get("text", "")).replace(
                "<PLANTED-CREDENTIAL-HERE>", PLANTED_LI_AT
            )
    else:
        specimens = await capture_specimens()

    if args.capture:
        stored = []
        for spec in specimens:
            stored.append(
                {
                    **spec,
                    "text": str(spec.get("text", "")).replace(
                        PLANTED_LI_AT, "<PLANTED-CREDENTIAL-HERE>"
                    ),
                }
            )
        pathlib.Path(args.capture).write_text(
            json.dumps(stored, indent=2) + "\n", encoding="utf-8"
        )
        print(f"captured {len(stored)} specimen(s) -> {args.capture}")

    rows = await drive(specimens)
    leaking = report(rows, specimens)

    print()
    print("=" * 74)
    driven = [r for r in rows if "skipped" not in r]
    premise = [r for r in driven if r["premise_playwright_quotes_the_cookie"]]
    print(f"branches driven                         : {len(driven)}")
    print(f"branches where Playwright quoted the plant: {len(premise)}")
    print(f"channels leaking                        : "
          f"model={sum(r['leak_model'] for r in driven)} "
          f"log={sum(r['leak_log'] for r in driven)} "
          f"exception={sum(r['leak_exception'] for r in driven)}")

    if not driven:
        print("VERDICT: NOTHING WAS DRIVEN. This run proves nothing either way.")
        return 2

    if args.expect == "leak":
        print("EXPECTED: leak. " + ("REPRODUCED." if leaking else "NOT REPRODUCED."))
        return 0 if leaking else 1
    print("EXPECTED: clean. " + ("NOT CLEAN." if leaking else "CLEAN."))
    return 1 if leaking else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--expect",
        choices=("leak", "clean"),
        default="leak",
        help="what this run asserts; the exit code follows it",
    )
    parser.add_argument(
        "--capture", help="write the captured specimens to this json path"
    )
    parser.add_argument(
        "--replay", help="drive stage 2 from a captured json, with no browser"
    )
    args = parser.parse_args()
    return asyncio.run(_main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
