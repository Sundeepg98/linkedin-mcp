"""THE LIVE FIRES of wave `readers-four-rows` -- one call per reader, attach only.

`_audit/2026-09-23-readers-four-rows.md` is the record; this file only fires.

## WHAT EACH FIRE IS

* ``analytics`` -- the SHIPPED tool ``linkedin_who_viewed_me(open_filter_menus=
  True)``, ONE call, ONE page load. It opens each filter pill on his
  profile-views analytics through ``press.disclose`` (scope ``main``, reading
  ``profile_views_filter_menu``) and closes it. Rows ``P O3`` and ``N 134``.
* ``feed`` -- ``press.disclose`` on ``/feed/``, ONE press, on the first feed
  item's own menu control, under the reading ``feed_item_share_menu``, priced
  by ``off_state`` (the /feed/ surface's declared sensitive counter). Row
  ``M C72``. Not a tool: see the record for why this row's fire is a
  measurement and not a bank.

## WHAT IT MAY NOT DO

It presses nothing itself -- every press is ``press.disclose``'s, and the gate
decides. No keyboard, no fill, no scroll. It never opens ``/messaging/`` or
``/notifications/``. It works in the browser's OWN tab in attach mode and
closes that tab, never the context.

## STOP AT THE FIRST ANOMALY

An error envelope from the tool, an auth wall, a challenge phrase on the page,
or a press the gate did not permit: the run stops there with NO further page
load, and what it had is written to the gitignored ``_state/`` so the anomaly
can be read from disk at zero loads.

## WHAT LEAVES THIS PROCESS

To the console: integers, booleans, and this package's own literals -- refusal
reasons, witness counter names, reading terms from ``press.OPEN_READINGS``.
The analytics tool's raw result carries viewer NAMES; it goes to
``_state/readers4/`` and nowhere else, and nothing prints from its rows.

Run, one fire per invocation::

    set LINKEDIN_CDP_ATTACH=1
    venv\\Scripts\\python.exe scripts/_probe_readers_four_fires.py analytics
    venv\\Scripts\\python.exe scripts/_probe_readers_four_fires.py feed
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

from linkedin_server import config, dom, press, readonly, server  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

import _probe_disclosure_targets as structure  # noqa: E402

ANALYTICS_URL = config.BASE_URL + "/analytics/profile-views/"
FEED_URL = config.BASE_URL + "/feed/"
FIRES = ("analytics", "feed")

#: THE FEED PRESS, fixed from the structural load recorded in section 2.2 of
#: the record -- the shape and scope under which the first feed item's own
#: menu control is candidate 0. Filled in only from that measurement.
FEED_SHAPE = "[aria-expanded]"
FEED_SCOPE = "feed_item"
FEED_READING = "feed_item_share_menu"

STATE = _ROOT / "_state" / "readers4"


def say(line: str = "") -> None:
    print(line, flush=True)


def _write(name: str, payload: dict) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / name).write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    say("  RAW written under _state/ (gitignored): " + name)


def _anomaly(out) -> "str | None":
    """An error envelope is an anomaly; a refusal is an answer. PURE."""
    if not isinstance(out, dict):
        return "not_a_dict"
    kind = out.get("error")
    return str(kind)[:40] if kind else None


async def _health(page) -> dict:
    """Challenge phrases on the page already open, as this probe's own words."""
    hits = await structure._challenge_phrases_hit(page)
    matched = [
        phrase for phrase, hit in zip(structure.CHALLENGE_PHRASES, hits) if hit
    ]
    return {"challenge_terms": matched}


def _numberish(value) -> "str | None":
    text = str(value or "").strip()
    return text if text and all(ch.isdigit() or ch in ",.%" for ch in text) else None


async def fire_analytics() -> int:
    say("=" * 70)
    say("FIRE analytics -- linkedin_who_viewed_me(open_filter_menus=True)")
    say("=" * 70)
    try:
        out = await server.linkedin_who_viewed_me(limit=10, open_filter_menus=True)
    except Exception as exc:  # noqa: BLE001 - type only
        out = {"error": type(exc).__name__}
    _write("fire-analytics-raw.json", {"result": out})
    kind = _anomaly(out)
    if kind:
        say("  ANOMALY: error envelope, kind " + kind + ". STOPPED.")
        return 1

    own = getattr(BROWSER, "_own_page", None)
    health = await _health(own) if own is not None else {"challenge_terms": ["no_page"]}
    say("  challenge terms on the page: " + str(health["challenge_terms"]))
    if health["challenge_terms"]:
        say("  ANOMALY: a challenge phrase is on the page. STOPPED.")
        return 1

    insights = out.get("insights") or {}
    headline = insights.get("headline") or {}
    delta = insights.get("delta") or {}
    observed = insights.get("observed") or {}
    say("  pages_loaded " + str(out.get("pages_loaded"))
        + "   rows " + str(out.get("count")))
    say("  insights: headline value " + str(_numberish(headline.get("value")))
        + "   delta value " + str(_numberish(delta.get("value")))
        + "   trend present " + str(bool(insights.get("trend")))
        + "   filters COUNT " + str(len(insights.get("filters") or []))
        + "   main_present " + str(observed.get("main_present")))
    if out.get("insights_error"):
        say("  insights_error " + str(out.get("insights_error")))
    if out.get("filter_menus_error"):
        say("  filter_menus_error " + str(out.get("filter_menus_error")))
        return 1
    menus = out.get("filter_menus") or {}
    # EVERY STRING IN THIS BLOCK IS A PACKAGE LITERAL -- see
    # server._filter_menu_summary -- so it is printed whole.
    say("  filter_menus: " + json.dumps(menus, sort_keys=True))
    return 0 if not menus.get("stopped") else 1


async def fire_feed() -> int:
    say("=" * 70)
    say("FIRE feed -- press.disclose(" + FEED_SHAPE + ", scope=" + FEED_SCOPE
        + ", reading=" + FEED_READING + ")")
    say("=" * 70)
    pre = press.evaluate(url=FEED_URL, shape=FEED_SHAPE, reading=FEED_READING,
                         scope=FEED_SCOPE)
    say("  pre-press verdict: " + json.dumps(pre, sort_keys=True))
    if pre.get("refused"):
        say("  REFUSED BEFORE ANY LOAD. Nothing loaded.")
        return 1

    async with BROWSER.session() as page:
        landed = await BROWSER.goto(page, FEED_URL)
        walled = any(marker in landed for marker in config.AUTHWALL_MARKERS)
        say("  walled " + str(walled))
        if walled:
            say("  ANOMALY: auth wall. STOPPED.")
            return 1
        health = await _health(page)
        say("  challenge terms on the page: " + str(health["challenge_terms"]))
        if health["challenge_terms"]:
            say("  ANOMALY: a challenge phrase is on the page. STOPPED.")
            return 1
        try:
            await page.wait_for_load_state("networkidle", timeout=15_000)
        except Exception as exc:  # noqa: BLE001
            say("  settle wait: " + type(exc).__name__)

        async def read_counters():
            surface = await dom.read_reaction_surface(page)
            value = surface.get("off_state") if isinstance(surface, dict) else None
            return {"off_state": int(value) if isinstance(value, int) else None}

        first = await read_counters()
        say("  off_state before handing to the gate: " + str(first.get("off_state")))
        if first.get("off_state") is None:
            say("  the sensitive counter does not read. NOTHING PRESSED.")
            return 1
        verdict = await press.disclose(
            page, shape=FEED_SHAPE, index=0, read_counters=read_counters,
            reading=FEED_READING, scope=FEED_SCOPE,
        )
    _write("fire-feed-verdict.json", {"verdict": verdict})
    # A GATE VERDICT IS BUILT FROM PACKAGE LITERALS, counts and the reading's
    # terms -- printed whole.
    say("  VERDICT: " + json.dumps(verdict, sort_keys=True, default=str))
    return 0 if verdict.get("permitted") else 1


async def main() -> int:
    which = sys.argv[1:] or []
    if len(which) != 1 or which[0] not in FIRES:
        say("REFUSING: name exactly one fire, from " + str(FIRES) + ".")
        return 2
    if not config.CDP_ATTACH:
        say("REFUSING: LINKEDIN_CDP_ATTACH is not set. This attaches to the")
        say("browser already running on the persistent profile, never launches one.")
        return 2
    for address in (ANALYTICS_URL, FEED_URL):
        if not readonly.is_read_url(address):
            say("REFUSING: an address is not on the read allowlist.")
            return 2
    try:
        if which[0] == "analytics":
            return await fire_analytics()
        return await fire_feed()
    except Exception as exc:  # noqa: BLE001 - type only, never the message
        say("THE RUN RAISED " + type(exc).__name__)
        return 1
    finally:
        try:
            own = getattr(BROWSER, "_own_page", None)
            if own is not None and not own.is_closed():
                page = own
                await page.close()
        except Exception as exc:  # noqa: BLE001 - shutdown noise only
            say("    closing our tab raised " + type(exc).__name__)
        try:
            await BROWSER.stop()
        except Exception as exc:  # noqa: BLE001 - shutdown noise only
            say("    cleanup raised " + type(exc).__name__)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
