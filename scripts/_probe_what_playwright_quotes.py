"""What does PLAYWRIGHT put in its own error strings?

``ERROR-MESSAGE-RULED-AT-THE-RAISE`` says the discriminator for publishing an
error message is not who authored the exception but whether A VALUE THE PAGE
CHOSE entered that exception's arguments. ``_audit/2026-09-21-what-the-browser-
said.md`` section 7 parked ONE case as unmeasured: the case where the BROWSER
ITSELF quotes page content in its own message. It was parked as needing a live
session.

**IT DOES NOT.** Playwright does not know what site it is looking at. Every
message this probe collects is raised against a PLANTED LOCAL PAGE built by
``set_content`` or served by an in-process ``route`` handler. No network, no
signed-in profile, no persistent user-data dir: an ephemeral chromium context
this process launches and closes.

## WHAT IS BEING DISCRIMINATED

Every sentinel in the planted page is tagged with its PROVENANCE, because that
is the axis the ruling turns on and no other axis answers the question:

* ``PAGE_CHOSEN`` -- a value the page decided: element text, an attribute
  value, an id, a class name, the document title, an option label, an input
  value, an href. A hit here is the forbidden class landing inside a library
  exception.
* ``OURS`` -- a value THIS PROCESS composed and handed to Playwright: a
  selector string, a requested address, a literal inside a script we wrote. A
  hit here is publishable under the ruling AS LONG AS the composing expression
  held no page value. Where the composition is an f-string over something read
  from the page, an OURS echo becomes a PAGE_CHOSEN echo, which is why these
  are counted separately rather than ignored.

The verdict axis is therefore ``PAGE_CHOSEN hits, or none``, and a case whose
only hits are OURS is reported as ``OURS_ONLY``, not as an echo and not as
silence.

## HOW TO READ A FAILURE

Each case DECLARES what it expects before it runs. A case that raises when it
was declared not to, or echoes a class it was declared not to, is a FAIL and
this script exits non-zero. ``--flip <case-id>`` inverts one declaration so the
engine can be SEEN convicting; ``--replay <json>`` re-runs the verdict engine
over a recorded run with no browser at all, which is what the companion
``_check_the_playwright_quote_probe_can_fail.py`` drives.

## WHAT THIS PROBE MAY NOT DO

It may not navigate to linkedin.com, attach to the operator's Chrome, or touch
the persistent profile at ``config.CHROME_PROFILE``. It launches its own
throwaway chromium and closes it. The one address family it navigates to is
``http://planted.invalid/``, a reserved TLD that cannot resolve, and every
request to it is answered by an in-process route handler, so nothing leaves
this machine.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Optional

# --------------------------------------------------------------------------
# THE SENTINELS. Obviously synthetic, and tagged by provenance.
# --------------------------------------------------------------------------

PAGE_CHOSEN = {
    "text": "ZQTEXTZQ",
    "attr": "ZQATTRZQ",
    "eid": "ZQIDZQ",
    "cls": "ZQCLASSZQ",
    "hidden": "ZQHIDDENZQ",
    "overlay": "ZQOVERLAYZQ",
    "title": "ZQTITLEZQ",
    "optlabel": "ZQOPTZQ",
    "inputvalue": "ZQVALUEZQ",
    "hrefattr": "ZQHREFZQ",
    "jsontext": "ZQJSONZQ",
    "landing": "ZQLANDZQ",
    # A cookie VALUE is chosen by the remote site in its Set-Cookie, so it is
    # page-chosen in exactly the sense the ruling means -- and it is also the
    # session.
    "cookie": "ZQCOOKIEZQ",
}

OURS = {
    "sel": "ZQSELZQ",
    "req": "ZQREQZQ",
    "hdr": "ZQHDRZQ",
}

ALL_SENTINELS = dict(PAGE_CHOSEN)
ALL_SENTINELS.update(OURS)

PLANTED = """<!doctype html>
<html><head><title>ZQTITLEZQ-doc</title>
<style>
 #cover { position: fixed; left:0; top:0; width:100%; height:100%; }
 .gone { display: none; }
</style></head>
<body>
 <div class="card ZQCLASSZQ" id="ZQIDZQ-1" data-probe="ZQATTRZQ-1">ZQTEXTZQ-alpha</div>
 <div class="card ZQCLASSZQ" id="ZQIDZQ-2" data-probe="ZQATTRZQ-2">ZQTEXTZQ-beta</div>
 <div class="card ZQCLASSZQ" id="ZQIDZQ-3" data-probe="ZQATTRZQ-3">ZQTEXTZQ-gamma</div>
 <div class="gone" id="hiddenone" data-probe="ZQHIDDENZQ">ZQHIDDENZQ-text</div>
 <a id="link" href="/ZQHREFZQ/path">a link</a>
 <input id="inp" value="ZQVALUEZQ">
 <select id="sel"><option value="ZQOPTZQ">ZQOPTZQ-label</option></select>
 <span id="single">just one</span>
 <script id="jsonblob" type="application/json">{"broken" ZQJSONZQ }</script>
 <div id="cover" data-probe="ZQOVERLAYZQ">ZQOVERLAYZQ-text</div>
</body></html>
"""

T = 900  # per-action timeout, ms. Short so the probe finishes.

ECHO = "ECHO"
SILENT = "SILENT"
OURS_ONLY = "OURS_ONLY"


# --------------------------------------------------------------------------
# THE CASES. Each declares, BEFORE it runs, what it expects.
# --------------------------------------------------------------------------
# family    - grouping for the report
# expect    - ECHO (a PAGE_CHOSEN value reaches str(exc)),
#             OURS_ONLY (only values we composed reach it),
#             SILENT (nothing we planted reaches it)
# must_raise- whether the call is expected to raise at all. A case that does
#             not raise cannot leak through an exception, and the distinction
#             matters: page.text_content(sel) is silent because it does NOT
#             RAISE, not because it declines to quote.


def build_cases(page, ctx) -> list[dict[str, Any]]:
    cards = page.locator(".card")

    def C(cid, family, api, expect, must_raise, fn, note=""):
        return {
            "id": cid,
            "family": family,
            "api": api,
            "expect": expect,
            "must_raise": must_raise,
            "fn": fn,
            "note": note,
        }

    return [
        # ---- STRICT MODE VIOLATION: a Locator method on a 3-element match ---
        C("strict.text_content", "strict", "Locator.text_content", ECHO, True,
          lambda: cards.text_content(timeout=T)),
        C("strict.inner_text", "strict", "Locator.inner_text", ECHO, True,
          lambda: cards.inner_text(timeout=T)),
        C("strict.inner_html", "strict", "Locator.inner_html", ECHO, True,
          lambda: cards.inner_html(timeout=T)),
        C("strict.get_attribute", "strict", "Locator.get_attribute", ECHO, True,
          lambda: cards.get_attribute("data-probe", timeout=T)),
        C("strict.is_visible", "strict", "Locator.is_visible", ECHO, True,
          lambda: cards.is_visible(timeout=T)),
        C("strict.wait_for", "strict", "Locator.wait_for", ECHO, True,
          lambda: cards.wait_for(timeout=T)),
        C("strict.element_handle", "strict", "Locator.element_handle", ECHO, True,
          lambda: cards.element_handle(timeout=T)),
        C("strict.evaluate", "strict", "Locator.evaluate", ECHO, True,
          lambda: cards.evaluate("e => e.textContent", timeout=T)),
        C("strict.bounding_box", "strict", "Locator.bounding_box", ECHO, True,
          lambda: cards.bounding_box(timeout=T)),
        C("strict.click", "strict", "Locator.click", ECHO, True,
          lambda: cards.click(timeout=T)),
        C("strict.fill", "strict", "Locator.fill", ECHO, True,
          lambda: cards.fill("x", timeout=T)),
        C("strict.get_by_text", "strict", "get_by_text(..).text_content", ECHO, True,
          lambda: page.get_by_text("ZQTEXTZQ").text_content(timeout=T),
          "the `aka get_by_text(\"<text>\")` suggestion quotes element text"),
        C("strict.filter_has_text", "strict", "Locator.filter(has_text).text_content",
          ECHO, True,
          lambda: page.locator(".card").filter(has_text="ZQTEXTZQ").text_content(timeout=T)),
        C("strict.page_text_content_strict", "strict",
          "Page.text_content(sel, strict=True)", ECHO, True,
          lambda: page.text_content(".card", strict=True, timeout=T)),
        C("strict.wait_for_selector_strict", "strict",
          "Page.wait_for_selector(sel, strict=True)", ECHO, True,
          lambda: page.wait_for_selector(".card", strict=True, timeout=T)),

        # ---- THE NEAR-MISS: the SAME verbs on Page, which are NOT strict ----
        C("nonstrict.page_text_content", "nonstrict",
          "Page.text_content(sel)", SILENT, False,
          lambda: page.text_content(".card", timeout=T),
          "takes the FIRST of 3 and does not raise"),
        C("nonstrict.page_inner_text", "nonstrict",
          "Page.inner_text(sel)", SILENT, False,
          lambda: page.inner_text(".card", timeout=T)),
        C("nonstrict.page_get_attribute", "nonstrict",
          "Page.get_attribute(sel, name)", SILENT, False,
          lambda: page.get_attribute(".card", "data-probe", timeout=T)),
        C("nonstrict.wait_for_selector", "nonstrict",
          "Page.wait_for_selector(sel)", SILENT, False,
          lambda: page.wait_for_selector(".card", timeout=T)),

        # ---- THE MITIGATION: a qualified locator cannot violate strict -----
        C("qualified.first", "qualified", "Locator.first.text_content", SILENT, False,
          lambda: cards.first.text_content(timeout=T)),
        C("qualified.last", "qualified", "Locator.last.text_content", SILENT, False,
          lambda: cards.last.text_content(timeout=T)),
        C("qualified.nth0", "qualified", "Locator.nth(0).text_content", SILENT, False,
          lambda: cards.nth(0).text_content(timeout=T)),

        # ---- SET-WIDE reads cannot violate strict --------------------------
        C("setwide.count", "setwide", "Locator.count", SILENT, False,
          lambda: cards.count()),
        C("setwide.all_text_contents", "setwide", "Locator.all_text_contents",
          SILENT, False, lambda: cards.all_text_contents()),
        C("setwide.all_inner_texts", "setwide", "Locator.all_inner_texts",
          SILENT, False, lambda: cards.all_inner_texts()),
        C("setwide.evaluate_all", "setwide", "Locator.evaluate_all", SILENT, False,
          lambda: cards.evaluate_all("els => els.length")),

        # ---- TIMEOUTS: what a call log carries -----------------------------
        C("timeout.absent_literal", "timeout",
          "Locator.text_content, literal selector, no match", SILENT, True,
          lambda: page.locator("#no-such-node").text_content(timeout=T),
          "the call log quotes the selector; this one holds no sentinel"),
        C("timeout.selector_echo_id", "timeout",
          "Locator.text_content, selector carrying a token", OURS_ONLY, True,
          lambda: page.locator("#ZQSELZQ-missing").text_content(timeout=T),
          "THE SELECTOR IS ECHOED VERBATIM"),
        C("timeout.selector_echo_hastext", "timeout",
          "Locator :has-text(..) no match", OURS_ONLY, True,
          lambda: page.locator(".card:has-text('ZQSELZQ')").text_content(timeout=T),
          "a :has-text() needle is echoed verbatim"),
        C("timeout.hidden_wait_visible", "timeout",
          "Locator.wait_for(state=visible) on display:none", ECHO, True,
          lambda: page.locator("#hiddenone").wait_for(state="visible", timeout=T),
          "`locator resolved to hidden <outerHTML>` -- no strict violation needed"),
        C("timeout.page_wait_for_selector_visible", "timeout",
          "Page.wait_for_selector(state=visible), NOT strict", ECHO, True,
          lambda: page.wait_for_selector("#hiddenone", state="visible", timeout=T),
          "the non-strict page-level wait echoes the element too"),
        C("timeout.click_intercepted", "timeout",
          "Locator.click intercepted by an overlay", ECHO, True,
          lambda: page.locator("#link").click(timeout=T),
          "the INTERCEPTING element's outerHTML is quoted"),
        C("timeout.page_click_multi", "timeout",
          "Page.click on a 3-element selector", ECHO, True,
          lambda: page.click(".card", timeout=T),
          "`resolved to 3 elements. Proceeding with the first one: <outerHTML>`"),
        C("timeout.nth_out_of_range", "timeout",
          "Locator.nth(9).text_content", SILENT, True,
          lambda: page.locator(".card").nth(9).text_content(timeout=T)),
        C("timeout.wait_for_function", "timeout", "Page.wait_for_function",
          SILENT, True,
          lambda: page.wait_for_function("() => document.title === 'nope'", timeout=T)),
        C("timeout.wait_for_url", "timeout", "Page.wait_for_url", SILENT, True,
          lambda: page.wait_for_url("**/never-here", timeout=T)),
        C("timeout.wait_for_load_state", "timeout", "Page.wait_for_load_state",
          SILENT, False,
          lambda: page.wait_for_load_state("networkidle", timeout=T)),
        C("timeout.set_content", "timeout",
          "Page.set_content (the already-observed case)", SILENT, True,
          lambda: page.set_content(PLANTED, timeout=1, wait_until="load"),
          "the one data point section 7 already had, re-driven"),

        # ---- EVALUATE: JS raising inside the page --------------------------
        C("evaluate.js_throws_page_text", "evaluate",
          "Page.evaluate, our JS throws with page text", ECHO, True,
          lambda: page.evaluate(
              "() => { throw new Error(document.title + ' ' + "
              "document.querySelector('.card').textContent); }"),
          "a script that names what it saw carries it out"),
        C("evaluate.js_typeerror", "evaluate",
          "Page.evaluate, TypeError on a missing node", SILENT, True,
          lambda: page.evaluate("() => document.querySelector('#nope').textContent")),
        C("evaluate.js_syntax", "evaluate", "Page.evaluate, syntax error",
          SILENT, True, lambda: page.evaluate("() => { this is not js }")),
        C("evaluate.json_parse_structural", "evaluate",
          "Page.evaluate, JSON.parse over malformed page JSON", SILENT, True,
          lambda: page.evaluate(
              "() => JSON.parse(document.querySelector('#jsonblob').textContent)"),
          "the STRUCTURAL branch reports a POSITION and quotes nothing"),
        C("evaluate.json_parse_bare_token", "evaluate",
          "Page.evaluate, JSON.parse over page text that is not JSON at all",
          ECHO, True,
          lambda: page.evaluate(
              "() => JSON.parse(document.querySelector('#ZQIDZQ-1').textContent)"),
          "THE NEAR MISS INSIDE ONE FUNCTION: this branch quotes the input"),
        C("evaluate.arg_roundtrip", "evaluate",
          "Page.evaluate, page value passed back as an arg", ECHO, True,
          lambda: page.evaluate(
              "(v) => { throw new Error('rejected ' + v); }",
              "ZQTEXTZQ-alpha")),

        # ---- NAVIGATION: requested address, or the one the site chose? -----
        # Served by a loopback http.server this process starts and stops. An
        # earlier version pointed these at a reserved-TLD host behind
        # ``context.route``; the redirect hop was NOT routed and came back
        # ERR_NAME_NOT_RESOLVED, so the redirect under test never happened and
        # the row recorded a landing that was never visited. A real redirect
        # chain on 127.0.0.1 is the only way to ask this question honestly.
        C("nav.connection_refused", "nav",
          "Page.goto, nothing listening", OURS_ONLY, True,
          lambda: page.goto(ctx["dead"] + "/ZQREQZQ/gone", timeout=T),
          "does the message quote the address we ASKED FOR"),
        C("nav.redirect_then_reset", "nav",
          "Page.goto, 302 to a SITE-CHOSEN address that then dies", OURS_ONLY,
          True,
          lambda: page.goto(ctx["base"] + "/ZQREQZQ/redirect-me", timeout=T),
          "THE ONE THAT MATTERS: requested address, or the LANDING? "
          "I declared ECHO and the measurement convicted me"),
        C("nav.redirect_then_timeout", "nav",
          "Page.goto, 302 to a SITE-CHOSEN address that hangs", OURS_ONLY, True,
          lambda: page.goto(ctx["base"] + "/ZQREQZQ/redirect-slow", timeout=T),
          "same question, timeout branch rather than net-error branch"),
        C("nav.bad_url", "nav", "Page.goto, malformed url", OURS_ONLY, True,
          lambda: page.goto("not-a-url-ZQREQZQ", timeout=T)),

        # ---- page.request: the one non-navigation fetch this server makes --
        C("request.unreachable", "request",
          "page.request.get, nothing listening", OURS_ONLY, True,
          lambda: page.request.get(ctx["dead"] + "/ZQREQZQ/api", timeout=T)),
        C("request.json_over_page_body", "request",
          "APIResponse.json over a body the SITE chose", SILENT, True,
          lambda: _response_json(page, ctx["base"] + "/notjson"),
          "the body is page-chosen; does the decoder quote it"),
        C("request.headers_in_call_log", "request",
          "page.request.get failing while the context holds a cookie",
          ECHO, True,
          lambda: _request_with_session(page, ctx["dead"] + "/ZQREQZQ/api"),
          "THE CALL LOG ENUMERATES EVERY REQUEST HEADER"),
        C("request.timeout_headers", "request",
          "page.request.get timing out while the context holds a cookie",
          ECHO, True,
          lambda: _request_with_session(
              page, ctx["base"] + "/ZQLANDZQ-landing/slow"),
          "the timeout branch, which is the reachable one in practice"),

        # ---- expect(): zero call sites here, measured anyway ---------------
        C("expect.to_have_text", "expect", "expect(..).to_have_text", ECHO, True,
          lambda: _expect_to_have_text(page),
          "`Actual value: <page text>`"),
        C("expect.to_have_attribute", "expect", "expect(..).to_have_attribute",
          ECHO, True, lambda: _expect_to_have_attribute(page)),
        C("expect.to_have_count", "expect", "expect(..).to_have_count", SILENT, True,
          lambda: _expect_to_have_count(page)),
    ]


async def _request_with_session(page, url):
    """A failing fetch made by a context that holds a cookie and a header.

    Both values are synthetic. The question is whether Playwright's own call
    log prints them back, which would put a SESSION value -- not merely a
    display string -- inside an exception this package publishes.
    """
    await page.context.add_cookies([{
        "name": "zq_session",
        "value": PAGE_CHOSEN["cookie"] + "-value",
        "domain": "127.0.0.1",
        "path": "/",
    }])
    return await page.request.get(
        url, headers={"x-zq-probe": OURS["hdr"] + "-header"}, timeout=T)


async def _response_json(page, url):
    response = await page.request.get(url, timeout=T)
    return await response.json()


async def _expect_to_have_text(page):
    from playwright.async_api import expect
    await expect(page.locator("#ZQIDZQ-1")).to_have_text("nothing like it", timeout=T)


async def _expect_to_have_attribute(page):
    from playwright.async_api import expect
    await expect(page.locator("#ZQIDZQ-1")).to_have_attribute(
        "data-probe", "nothing like it", timeout=T)


async def _expect_to_have_count(page):
    from playwright.async_api import expect
    await expect(page.locator(".card")).to_have_count(99, timeout=T)


# --------------------------------------------------------------------------
# THE STDLIB CONTRAST. Not Playwright, but the same law, and this repository
# has been bitten by exactly this family behaving inconsistently.
# --------------------------------------------------------------------------

def stdlib_rows() -> list[dict[str, Any]]:
    needle = PAGE_CHOSEN["text"] + "-alpha"
    trials = [
        ("stdlib.int", "int(<page text>)", lambda: int(needle)),
        ("stdlib.float", "float(<page text>)", lambda: float(needle)),
        ("stdlib.list_index", "[].index(<page text>)", lambda: [].index(needle)),
        ("stdlib.list_remove", "[].remove(<page text>)", lambda: [].remove(needle)),
        ("stdlib.set_remove", "set().remove(<page text>)", lambda: set().remove(needle)),
        ("stdlib.set_discard", "set().discard(<page text>)",
         lambda: set().discard(needle)),
        ("stdlib.dict_getitem", "{}[<page text>]", lambda: {}[needle]),
        ("stdlib.json_loads", "json.loads(<page text>)", lambda: json.loads(needle)),
        ("stdlib.datetime", "datetime.strptime(<page text>)",
         lambda: __import__("datetime").datetime.strptime(needle, "%Y-%m-%d")),
    ]
    rows = []
    for cid, api, fn in trials:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 - cataloguing them is the job
            rows.append(_record(cid, "stdlib", api, exc, True, note=""))
        else:
            rows.append(_record(cid, "stdlib", api, None, True, note=""))
    return rows


# --------------------------------------------------------------------------
# RECORDING AND THE VERDICT ENGINE
# --------------------------------------------------------------------------

def _ascii(text: str) -> str:
    return text.encode("ascii", "backslashreplace").decode("ascii")


def _hits(message: str) -> dict[str, list[str]]:
    return {
        "page_chosen": sorted(k for k, v in PAGE_CHOSEN.items() if v in message),
        "ours": sorted(k for k, v in OURS.items() if v in message),
    }


def _record(cid, family, api, exc, must_raise, note="") -> dict[str, Any]:
    if exc is None:
        return {
            "id": cid, "family": family, "api": api, "note": note,
            "raised": False, "exc_type": None, "message": None,
            "hits": {"page_chosen": [], "ours": []}, "observed": SILENT,
        }
    message = str(exc)
    hits = _hits(message)
    if hits["page_chosen"]:
        observed = ECHO
    elif hits["ours"]:
        observed = OURS_ONLY
    else:
        observed = SILENT
    return {
        "id": cid, "family": family, "api": api, "note": note,
        "raised": True,
        "exc_type": type(exc).__module__ + "." + type(exc).__name__,
        "message": _ascii(message),
        "hits": hits,
        "observed": observed,
    }


# A navigation row asserting "the LANDING is not quoted" is vacuous unless the
# landing was actually reached. These two must show it in the server's log.
LANDING_REQUIRED = ("nav.redirect_then_reset", "nav.redirect_then_timeout")


def verdict(rows: list[dict[str, Any]], declarations: dict[str, dict]) -> list[dict]:
    """Compare every measured row against what its case DECLARED."""
    out = []
    for row in rows:
        decl = declarations.get(row["id"])
        if decl is None:
            out.append(dict(row, verdict="NO_DECLARATION", why="no declared expectation"))
            continue
        problems = []
        if decl["must_raise"] and not row["raised"]:
            problems.append("declared to raise, did not raise")
        if not decl["must_raise"] and row["raised"]:
            problems.append("declared not to raise, raised " + str(row["exc_type"]))
        if row["observed"] != decl["expect"]:
            problems.append(
                "declared " + decl["expect"] + ", observed " + row["observed"])
        if row["id"] in LANDING_REQUIRED:
            seen = row.get("server_saw") or []
            if not any(PAGE_CHOSEN["landing"] in path for path in seen):
                problems.append(
                    "VACUOUS: the redirect target was never requested, so this "
                    "row proves nothing about a landing; server saw "
                    + (", ".join(seen) or "nothing"))
        out.append(dict(
            row,
            expect=decl["expect"],
            must_raise=decl["must_raise"],
            verdict="PASS" if not problems else "FAIL",
            why="; ".join(problems),
        ))
    return out


# --------------------------------------------------------------------------
# DRIVING
# --------------------------------------------------------------------------

class _PlantedHandler(BaseHTTPRequestHandler):
    """A loopback server whose only job is to choose an address WE did not.

    ``/ZQREQZQ/redirect-me``  -> 302 to ``/ZQLANDZQ-landing/page``, which then
                                 drops the connection.
    ``/ZQREQZQ/redirect-slow``-> 302 to ``/ZQLANDZQ-landing/slow``, which then
                                 hangs past the navigation timeout.

    The redirect target is the SITE'S choice in exactly the sense the ruling
    means. Nothing here leaves 127.0.0.1.
    """

    # Every path the browser actually asked for. This is the POSITIVE CONTROL
    # for the navigation rows: "the landing is not quoted" is worth nothing
    # unless the landing was VISITED, and an earlier version of this probe
    # recorded exactly that empty claim when its redirect silently failed DNS.
    REQUESTS: list[str] = []

    def do_GET(self):  # noqa: N802 - BaseHTTPRequestHandler's spelling
        path = self.path
        _PlantedHandler.REQUESTS.append(path)
        if "redirect-me" in path:
            self.send_response(302)
            self.send_header("Location", "/ZQLANDZQ-landing/page")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if "redirect-slow" in path:
            self.send_response(302)
            self.send_header("Location", "/ZQLANDZQ-landing/slow")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if "ZQLANDZQ" in path and "slow" in path:
            time.sleep((T / 1000.0) * 4)
            return
        if "notjson" in path:
            body = ("ZQTEXTZQ-alpha is not json at all").encode("ascii")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if "ZQLANDZQ" in path:
            # Drop the connection with no response at all.
            self.close_connection = True
            try:
                self.wfile.close()
            except OSError:
                pass
            return
        body = PLANTED.encode("ascii")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):  # silence the default stderr logging
        return

    def handle_one_request(self):
        # The ZQLANDZQ branch drops the connection ON PURPOSE, and the stdlib
        # server prints a socketserver traceback when it cannot flush. That
        # traceback is this probe working, not this probe breaking, so it is
        # swallowed here rather than left to look like a failure in the
        # output somebody reads.
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError,
                ValueError, OSError):
            self.close_connection = True

    def handle_error(self, *_args):
        return


def _start_planted_server():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _PlantedHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    return srv, "http://127.0.0.1:%d" % srv.server_address[1]


def _dead_address() -> str:
    """A loopback port with nothing listening, found by binding and closing."""
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return "http://127.0.0.1:%d" % port


async def _replant(page) -> None:
    """Put the planted page back, whatever the previous case left behind.

    A routed-abort navigation can still be in flight when the next case
    starts, and ``set_content`` then dies with "Execution context was
    destroyed". ``about:blank`` is not a network request, so it is not routed;
    it settles the frame before the content goes back in.
    """
    for attempt in range(4):
        try:
            await page.goto("about:blank", wait_until="commit", timeout=5000)
            await page.set_content(PLANTED, timeout=5000)
            return
        except Exception:  # noqa: BLE001 - retry, then let it surface
            if attempt == 3:
                raise
            await asyncio.sleep(0.2)


async def drive() -> list[dict[str, Any]]:
    from playwright.async_api import async_playwright

    rows: list[dict[str, Any]] = []
    srv, base = _start_planted_server()
    addrs = {"base": base, "dead": _dead_address()}
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        try:
            for case in build_cases(page, addrs):
                # RE-PLANT BEFORE EVERY CASE. An earlier version of this probe
                # let a failed goto blow the page away and then recorded three
                # cases as "silent" that had simply run against a blank
                # document. A proven-silent claim built on an empty page is
                # not a measurement, it is a fixture bug wearing one.
                await _replant(page)
                _PlantedHandler.REQUESTS.clear()
                try:
                    await case["fn"]()
                except Exception as exc:  # noqa: BLE001
                    row = _record(case["id"], case["family"], case["api"],
                                  exc, case["must_raise"], case["note"])
                else:
                    row = _record(case["id"], case["family"], case["api"],
                                  None, case["must_raise"], case["note"])
                row["server_saw"] = list(_PlantedHandler.REQUESTS)
                rows.append(row)
        finally:
            # Only what this process opened: its own context, its own browser,
            # its own loopback server. Nothing else is touched.
            await ctx.close()
            await browser.close()
            srv.shutdown()
            srv.server_close()
    rows.extend(stdlib_rows())
    return rows


def declarations() -> dict[str, dict]:
    """The declared expectations, with no browser involved."""
    class _NullLocator:
        def __getattr__(self, _name):
            return self

        def __call__(self, *_a, **_k):
            return self

    decls = {}
    for case in build_cases(_NullLocator(), None):
        decls[case["id"]] = {"expect": case["expect"],
                             "must_raise": case["must_raise"]}
    # The stdlib contrast rows are declared here rather than in build_cases
    # because they need no page.
    for cid, expect in [
        ("stdlib.int", ECHO),
        ("stdlib.float", ECHO),
        ("stdlib.list_index", ECHO),
        ("stdlib.list_remove", SILENT),
        ("stdlib.set_remove", ECHO),
        ("stdlib.set_discard", SILENT),
        ("stdlib.dict_getitem", ECHO),
        ("stdlib.json_loads", SILENT),
        ("stdlib.datetime", ECHO),
    ]:
        decls[cid] = {"expect": expect,
                      "must_raise": cid != "stdlib.set_discard"}
    return decls


def report(judged: list[dict], verbose: bool) -> int:
    fails = [r for r in judged if r["verdict"] != "PASS"]
    width = max(len(r["id"]) for r in judged)
    print("%-*s  %-9s %-9s %-6s %s" % (
        width, "case", "declared", "observed", "verdict", "page-chosen hits"))
    print("-" * (width + 46))
    for r in judged:
        print("%-*s  %-9s %-9s %-6s %s" % (
            width, r["id"], r.get("expect", "?"), r["observed"], r["verdict"],
            ",".join(r["hits"]["page_chosen"]) or "-"))
        if r["verdict"] != "PASS":
            print("%-*s  ^^ %s" % (width, "", r["why"]))
    print()
    echoes = [r for r in judged if r["observed"] == ECHO]
    ours = [r for r in judged if r["observed"] == OURS_ONLY]
    silent = [r for r in judged if r["observed"] == SILENT]
    print("cases                    %d" % len(judged))
    print("  ECHO (page-chosen)     %d" % len(echoes))
    print("  OURS_ONLY              %d" % len(ours))
    print("  SILENT                 %d" % len(silent))
    print("  FAILED declarations    %d" % len(fails))
    if verbose:
        print()
        for r in judged:
            print("=" * 72)
            print(r["id"], "->", r["exc_type"] or "(did not raise)")
            if r["message"]:
                print(r["message"])
    return 1 if fails else 0


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", dest="json_out",
                    help="write the measured rows to this path")
    ap.add_argument("--replay", dest="replay",
                    help="re-judge a recorded run; launches no browser")
    ap.add_argument("--flip", dest="flip", action="append", default=[],
                    help="invert one case's declared expectation, to see the "
                         "engine convict")
    ap.add_argument("--verbose", action="store_true",
                    help="print every message in full")
    args = ap.parse_args(argv)

    if args.replay:
        rows = json.loads(Path(args.replay).read_text(encoding="ascii"))
    else:
        rows = asyncio.run(drive())

    decls = declarations()
    for cid in args.flip:
        if cid not in decls:
            print("no such case: " + cid, file=sys.stderr)
            return 2
        cur = decls[cid]["expect"]
        decls[cid] = dict(decls[cid],
                          expect=SILENT if cur in (ECHO, OURS_ONLY) else ECHO)
        print("FLIPPED %s: declared %s -> %s" % (cid, cur, decls[cid]["expect"]))

    if args.json_out and not args.replay:
        Path(args.json_out).write_text(
            json.dumps(rows, indent=1) + "\n", encoding="ascii")

    return report(verdict(rows, decls), args.verbose)


if __name__ == "__main__":
    sys.exit(main())
