"""FIRE the live lane's session-1 queue, one closed key at a time. Shapes out, raw to _state.

A closed, ordered table of KEYS, each a SHIPPED tool called exactly as a
caller would call it:

    per_post       P G6          linkedin_creator_analytics()             1 load
    badge          pre-flight    linkedin_new_messages()                  1 load
                                 (+ the notifications badge off the same
                                 /feed/ page, and a capture of it)
    m43            M M43         linkedin_open_messaging()                1 load
    m33            M M33         linkedin_open_messaging(message_filter=
                                 "starred")                               1 load
    notifications  N 20, N 45    linkedin_notifications()                 1 load
    activity       ids for C72,  linkedin_my_activity_items()             1-2 loads
                   C38, C85

## THE MESSAGING RULE, ENFORCED HERE RATHER THAN REMEMBERED

``/messaging/`` never stays on a list: it redirects into ONE conversation
LinkedIn chooses (``linkedin_open_messaging``'s own docstring). So the lane
cannot choose an already-read thread for the landing. What it CAN do is read
``linkedin_new_messages`` first -- the messaging badge off ``/feed/``, which
counts NEW-SINCE-LAST-VISIT -- and open messaging only when that badge reads
EXACTLY 0. :func:`_selected` refuses ``m43`` / ``m33`` unless ``badge`` runs
earlier in the SAME invocation, and :func:`main` skips them unless the badge
it just read is the integer 0. ``None`` (badge not drawn) is not 0.

## THE LEDGER

``_state/live1/ledger.json`` (gitignored) is the session's page-load record
across processes. :func:`_install_counter` wraps ``BROWSER.goto`` -- the only
place in the package that calls ``page.goto`` -- so EVERY navigation a tool
makes is counted, its own retries included. The wrapper refuses a load that
would be the 41st (``LIVE-BUDGET-40-LOADS``) BEFORE navigating, and waits out
the rest of 20 seconds since the ledger's last load, so the spacing holds
across separate runs too. Inside one process ``BROWSER.goto`` spaces loads by
``LINKEDIN_MIN_INTERVAL_S``, and :func:`_environment_refusal` refuses to run
unless that is at least 20.

## WHAT LEAVES THIS PROCESS

Integers, booleans, ``None``, dict keys that are SHAPED LIKE FIELD NAMES
(:func:`is_field_name` -- a key that is an item urn is counted and withheld;
the first live run printed eight of them, see the session document), and the
handful of string fields in :data:`LITERAL_FIELDS` whose values are this
package's own closed words (a refusal key, an active filter). Every other
string is reported by LENGTH. No url, no page text, no name, no item
key and no exception message is ever printed -- exception TYPE names only.
Raw envelopes go to ``_state/live1/<key>.json`` and page captures to
``_state/live1/<key>.html``: gitignored, never printed, never committed.

## THE ANOMALY RULE

An error envelope or an exception from any key stops every further page
load, as the sibling harnesses do. A login page, a checkpoint or a challenge
phrase on the page stops the SESSION. A refusal is an answer, not an anomaly.

Run it as::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 LINKEDIN_MIN_INTERVAL_S=20 \\
        ./venv/Scripts/python.exe scripts/_probe_live_lane_session_1.py \\
        --only badge,m43 [--no-capture]
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any, Optional

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

from linkedin_server import config, notify_cost, readonly, server  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

import _probe_disclosure_targets as structure  # noqa: E402

STATE = _ROOT / "_state" / "live1"
LEDGER = STATE / "ledger.json"

#: LIVE-BUDGET-40-LOADS, and the ruling's spacing.
CEILING = 40
MIN_GAP_S = 20.0

#: The keys, in the order they may run. Closed.
KEYS: tuple[str, ...] = ("per_post", "badge", "m43", "m33", "notifications", "activity")

#: The keys that open /messaging/. Each needs ``badge`` earlier in the run.
MESSAGING_KEYS = frozenset({"m43", "m33"})

#: The pill this lane presses for M M33, and why it is this one: a starred
#: conversation is one he has read. See the session document, 0.3 point 2.
M33_FILTER = "starred"

#: The most loads one key may spend, for the pre-check before it starts.
MAX_LOADS: dict[str, int] = {
    "per_post": 1, "badge": 1, "m43": 1, "m33": 1, "notifications": 1, "activity": 2,
}

#: String fields whose values are this package's own closed words.
LITERAL_FIELDS = frozenset({
    "refused", "active_filter", "item_root_source", "state", "refused_on",
})

#: Closed phrases for the two notification kinds the census rows ask about.
#: LinkedIn's own wording; matched after lower-casing and collapsing spaces.
INVITATION_PHRASES: tuple[str, ...] = (
    "invited you to connect", "wants to connect", "sent you an invitation",
    "invitation to connect",
)
FOLLOW_PHRASES: tuple[str, ...] = (
    "followed you", "started following you", "is following you", "new follower",
)
#: An invitation notification links into the invitation manager.
INVITATION_LINK_MARKER = "/mynetwork/invitation-manager"


class _Anomaly(Exception):
    """Stops every further page load. Carries no page-derived text."""

    def __init__(self, kind: str, where: str) -> None:
        super().__init__(kind + " at " + where)
        self.kind = kind
        self.where = where


class _LedgerRefusal(Exception):
    """A navigation that would break the session budget. Raised BEFORE it."""


def say(line: str = "") -> None:
    print(line, flush=True)


# ---------------------------------------------------------------------------
# Selection and environment -- decided before the browser is touched.
# ---------------------------------------------------------------------------


def _selected(argv: list[str]) -> list[str]:
    """The keys to run, in the order given. PURE. Refuses via SystemExit."""
    if "--only" not in argv:
        raise SystemExit("REFUSING: name the keys with --only k1,k2 -- this "
                         "session fires nothing by default.")
    at = argv.index("--only")
    if at + 1 >= len(argv):
        raise SystemExit("REFUSING: --only needs a comma list of keys.")
    wanted = [k for k in argv[at + 1].split(",") if k]
    unknown = [k for k in wanted if k not in KEYS]
    if unknown or not wanted:
        raise SystemExit("REFUSING: unknown key(s); the closed set is " + str(list(KEYS)))
    if len(set(wanted)) != len(wanted):
        raise SystemExit("REFUSING: a key is named twice.")
    for position, key in enumerate(wanted):
        if key in MESSAGING_KEYS and "badge" not in wanted[:position]:
            raise SystemExit("REFUSING: " + key + " opens /messaging/ and needs "
                             "'badge' earlier in the same run.")
    return wanted


def _environment_refusal() -> Optional[str]:
    """``None`` when attach mode and the spacing are set; else the reason."""
    if not config.CDP_ATTACH:
        return "LINKEDIN_CDP_ATTACH is not set; this attaches, it never launches."
    if float(config.MIN_NAVIGATION_INTERVAL_S) < MIN_GAP_S:
        return "LINKEDIN_MIN_INTERVAL_S is below " + str(int(MIN_GAP_S)) + "."
    return None


# ---------------------------------------------------------------------------
# The ledger, and the counter wrapped around BROWSER.goto.
# ---------------------------------------------------------------------------


def _ledger_read() -> dict[str, Any]:
    if not LEDGER.exists():
        return {"session": "live-lane-session-1", "ceiling": CEILING,
                "min_gap_s": MIN_GAP_S, "loads": []}
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def _ledger_append(key: str, surface: str) -> int:
    ledger = _ledger_read()
    now = time.time()
    ledger["loads"].append({
        "n": len(ledger["loads"]) + 1, "key": key, "surface": surface,
        "at": now, "at_local": time.strftime("%H:%M:%S", time.localtime(now)),
    })
    STATE.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    return len(ledger["loads"])


def budget_verdict(loads: list[dict[str, Any]], planned: int) -> Optional[str]:
    """``None`` when ``planned`` more loads fit under the ceiling. PURE."""
    if len(loads) + planned > CEILING:
        return ("the session has spent " + str(len(loads)) + " of " + str(CEILING)
                + " loads; this key may need " + str(planned))
    return None


def gap_remaining(loads: list[dict[str, Any]], now: float) -> float:
    """Seconds still owed before the next load may start. PURE."""
    if not loads:
        return 0.0
    return max(0.0, MIN_GAP_S - (now - float(loads[-1]["at"])))


def _surface_of(url: str) -> str:
    """The first path segment of a REQUESTED address -- a word, never an id."""
    path = url.split("://", 1)[-1].split("/", 1)
    head = path[1].split("/", 1)[0] if len(path) > 1 else ""
    return head.split("?", 1)[0][:24] or "root"


_CURRENT = {"key": "none"}


def _install_counter() -> None:
    """Wrap ``BROWSER.goto`` so every navigation passes the ledger first."""
    original = BROWSER.goto

    async def counted_goto(page: Any, url: str, **kwargs: Any) -> str:
        if not readonly.is_read_url(url):
            # REFUSED BY THE BOUNDARY: ``original`` raises inside
            # ``assert_read_url`` before ``page.goto``, so no page loads and
            # none is counted.
            return await original(page, url, **kwargs)
        loads = _ledger_read()["loads"]
        if len(loads) >= CEILING:
            raise _LedgerRefusal("load " + str(len(loads) + 1) + " would pass the ceiling")
        owed = gap_remaining(loads, time.time())
        if owed > 0:
            await asyncio.sleep(owed)
        try:
            return await original(page, url, **kwargs)
        finally:
            number = _ledger_append(_CURRENT["key"], _surface_of(url))
            say("    [ledger] load " + str(number) + " of " + str(CEILING)
                + " (" + _surface_of(url) + ")")

    BROWSER.goto = counted_goto  # type: ignore[method-assign]


# ---------------------------------------------------------------------------
# Printing: shapes only.
# ---------------------------------------------------------------------------


_FIELD_NAME_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")


def is_field_name(key: Any) -> bool:
    """Is this dict key a FIELD NAME, safe to print? PURE.

    **A DICT KEY IS NOT ALWAYS A FIELD NAME, and this harness's first live run
    said so by printing one.** ``linkedin_my_activity_items`` returns
    ``anchors_per_item`` KEYED BY ITEM URN -- real identifiers for his posts --
    and the first version of :func:`shape_of` printed every key on the
    assumption that keys are names this package wrote. So a key prints only if
    it is shaped like one: ASCII letters, digits and underscores, starting with
    a letter or underscore, at most 40 characters, and no run of six digits.
    Anything else is counted and withheld.
    """
    text = str(key)
    if not text or len(text) > 40 or text[0].isdigit():
        return False
    if any(ch not in _FIELD_NAME_CHARS for ch in text):
        return False
    run = 0
    for ch in text:
        run = run + 1 if ch.isdigit() else 0
        if run >= 6:
            return False
    return True


def _key_list(keys: Any) -> str:
    names = sorted(str(k) for k in keys if is_field_name(k))
    withheld = sum(1 for k in keys if not is_field_name(k))
    return str(names[:14]) + ("" if not withheld else " + " + str(withheld) + " withheld")


def shape_of(value: Any, key: str = "", depth: int = 0) -> str:
    """One value, rendered without its content. PURE."""
    if value is None or isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return format(value, ".4g")
    if isinstance(value, str):
        if key in LITERAL_FIELDS and len(value) <= 40 and value.isascii():
            return "'" + value + "'"
        return "str(len=" + str(len(value)) + ")"
    if isinstance(value, (list, tuple)):
        inner = ""
        dicts = [v for v in value if isinstance(v, dict)]
        if dicts:
            inner = ", item keys " + _key_list({k for d in dicts for k in d})
        return "list(len=" + str(len(value)) + inner + ")"
    if isinstance(value, dict):
        if depth >= 2:
            return "dict(keys=" + _key_list(value) + ")"
        named = sorted((str(k), v) for k, v in value.items() if is_field_name(k))
        withheld = sum(1 for k in value if not is_field_name(k))
        parts = [k + ": " + shape_of(v, k, depth + 1) for k, v in named]
        if withheld:
            parts.append(str(withheld) + " key(s) withheld: not field names")
        return "{" + "; ".join(parts) + "}"
    return type(value).__name__


def _print_envelope(out: dict[str, Any]) -> None:
    for field in sorted(str(k) for k in out if is_field_name(k)):
        say("    " + field + ": " + shape_of(out[field], field))
    withheld = sum(1 for k in out if not is_field_name(k))
    if withheld:
        say("    " + str(withheld) + " top-level key(s) withheld: not field names")


# ---------------------------------------------------------------------------
# Readings taken on the page a tool left open.
# ---------------------------------------------------------------------------


def _normalised(text: str) -> str:
    return " ".join(str(text or "").lower().split())


def notification_kinds(rows: list[dict[str, Any]]) -> dict[str, int]:
    """Rows of each census kind, by the closed phrases above. PURE, counts only."""
    invitation = follow = 0
    for row in rows:
        body = _normalised(row.get("text", ""))
        link = str(row.get("link") or "")
        if any(p in body for p in INVITATION_PHRASES) or INVITATION_LINK_MARKER in link:
            invitation += 1
        if any(p in body for p in FOLLOW_PHRASES):
            follow += 1
    return {"invitation_kind_rows": invitation, "follow_kind_rows": follow}


def urn_types(keys: list[Any]) -> dict[str, int]:
    """How many item keys are of each urn TYPE -- the type word only. PURE."""
    counts: dict[str, int] = {}
    for key in keys:
        text = str(key.get("key") if isinstance(key, dict) else key)
        parts = text.split(":")
        kind = parts[2] if len(parts) >= 4 and parts[0] == "urn" and parts[2].isascii() else "not_an_urn"
        counts[kind[:20]] = counts.get(kind[:20], 0) + 1
    return counts


async def _own_page() -> Any:
    own = getattr(BROWSER, "_own_page", None)
    if own is None or own.is_closed():
        return None
    return own


async def _health(where: str) -> None:
    """Auth wall and challenge phrases on the page a tool left open."""
    page = await _own_page()
    if page is None:
        raise _Anomaly("no_page_to_check", where)
    walled = any(marker in (page.url or "") for marker in config.AUTHWALL_MARKERS)
    hits = await structure._challenge_phrases_hit(page)
    matched = [p for p, hit in zip(structure.CHALLENGE_PHRASES, hits) if hit]
    say("    health: walled " + str(walled) + ", challenge terms " + str(len(matched)))
    if walled or matched:
        raise _Anomaly("auth_wall_or_challenge", where)


async def _capture(key: str) -> None:
    page = await _own_page()
    if page is None:
        say("    capture: no page open, nothing written")
        return
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / (key + ".html")).write_text(await page.content(), encoding="utf-8")
    say("    capture written under _state/ (gitignored)")


def _write_raw(key: str, payload: Any) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / (key + ".json")).write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8")


async def _notifications_badge_here() -> Optional[dict[str, Any]]:
    """The notifications nav badge off the page already open. ``None`` if none."""
    page = await _own_page()
    if page is None:
        return None
    return await notify_cost.read_notifications_badge(page)


# ---------------------------------------------------------------------------
# The keys.
# ---------------------------------------------------------------------------


async def _call(key: str) -> dict[str, Any]:
    """Call the shipped tool for ``key``. Returns its envelope untouched."""
    if key == "per_post":
        return await server.linkedin_creator_analytics()
    if key == "badge":
        return await server.linkedin_new_messages()
    if key == "m43":
        return await server.linkedin_open_messaging()
    if key == "m33":
        return await server.linkedin_open_messaging(message_filter=M33_FILTER)
    if key == "notifications":
        return await server.linkedin_notifications()
    if key == "activity":
        return await server.linkedin_my_activity_items()
    raise ValueError("no tool for key " + key)


async def fire(key: str, capture: bool, carried: dict[str, Any]) -> dict[str, Any]:
    """Fire one key: pre-check, call, health, readings, capture, raw."""
    say("\n" + "=" * 70)
    say("KEY " + key)
    say("=" * 70)
    refusal = budget_verdict(_ledger_read()["loads"], MAX_LOADS[key])
    if refusal:
        raise _Anomaly("ledger_refused_before_start", key)
    _CURRENT["key"] = key
    out = await _call(key)
    if not isinstance(out, dict):
        raise _Anomaly("not_a_dict", key)
    raw: dict[str, Any] = {"envelope": out}
    if out.get("error"):
        _write_raw(key, raw)
        say("    ERROR ENVELOPE (" + shape_of(out.get("error"), "error") + ")")
        raise _Anomaly("error_envelope", key)
    await _health(key)
    _print_envelope(out)

    if key == "badge":
        before = await _notifications_badge_here()
        raw["notifications_badge_before"] = before
        carried["notifications_badge_before"] = before
        verdict = notify_cost.notifications_badge(before)
        say("    notifications badge here: state " + shape_of(verdict.get("state"), "state")
            + ", unread " + shape_of(verdict.get("unread")))
        carried["new_since_last_visit"] = out.get("new_since_last_visit")
    elif key == "notifications":
        rows = out.get("results") or []
        kinds = notification_kinds(rows)
        raw["kinds"] = kinds
        say("    kinds: " + shape_of(kinds))
        after = await _notifications_badge_here()
        raw["notifications_badge_after"] = after
        delta = notify_cost.cost_delta(carried.get("notifications_badge_before"), after)
        raw["cost_delta"] = delta
        say("    cost_delta: state " + shape_of(delta.get("state"), "state")
            + ", refused_on " + shape_of(delta.get("refused_on"), "refused_on")
            + ", delta " + shape_of(delta.get("delta")))
    elif key == "activity":
        items = out.get("items") or []
        types = urn_types(items)
        raw["urn_types"] = types
        say("    item urn types: " + shape_of(types))
        page = await _own_page()
        if page is not None:
            polls = int(await page.locator('main [class*="poll"]').count())
            raw["poll_shaped_nodes_in_main"] = polls
            say("    poll-shaped nodes in main: " + str(polls))

    if capture and key != "per_post":
        await _capture(key)
    _write_raw(key, raw)
    say("    RAW written under _state/ (gitignored)")
    return out


async def main() -> int:
    argv = sys.argv[1:]
    keys = _selected(argv)
    capture = "--no-capture" not in argv
    refusal = _environment_refusal()
    if refusal:
        say("REFUSING: " + refusal)
        return 2
    say("### keys: " + ", ".join(keys) + "   capture " + str(capture))
    say("### ledger before this run: " + str(len(_ledger_read()["loads"])) + " of " + str(CEILING))
    _install_counter()
    carried: dict[str, Any] = {}
    outcomes: dict[str, str] = {}
    try:
        for key in keys:
            if key in MESSAGING_KEYS:
                seen = carried.get("new_since_last_visit")
                if not (isinstance(seen, int) and not isinstance(seen, bool) and seen == 0):
                    say("\n--- " + key + ": NOT OPENED -- the messaging badge read "
                        + shape_of(seen) + ", and the rule opens /messaging/ only on exactly 0")
                    outcomes[key] = "HELD-BY-BADGE"
                    continue
            await fire(key, capture, carried)
            outcomes[key] = "RETURNED"
    except _Anomaly as stop:
        say("\n### ANOMALY: " + stop.kind + " at " + stop.where + ". EVERY FURTHER LOAD STOPPED.")
        outcomes[stop.where] = "ANOMALY " + stop.kind
        return 1
    except _LedgerRefusal:
        say("\n### THE LEDGER REFUSED A LOAD. Stopped.")
        return 1
    except Exception as error:  # noqa: BLE001 - type only, never the message
        say("\nRUN ABORTED: " + type(error).__name__)
        return 1
    finally:
        # CLOSE OUR TAB, THEN DROP THE CDP CONNECTION. THE PAGE, NEVER THE
        # CONTEXT -- in attach mode the context is his own signed-in browser.
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
        say("\n### OUTCOMES " + json.dumps(outcomes, sort_keys=True))
        say("### ledger after this run: " + str(len(_ledger_read()["loads"])) + " of " + str(CEILING))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
