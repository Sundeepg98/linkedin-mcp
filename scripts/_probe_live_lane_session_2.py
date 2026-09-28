"""FIRE the live lane's session-2 queue, one closed key at a time. PAGE-MAY-VETO-NEVER-SUPPLY.

The plan this runs is ``_audit/2026-09-27-live-session-2-plan.md``: its step
tables name these keys, their loads, the ruling each rests on, and whether a
step needs the operator. NOTHING HERE RUNS until that plan's own go.

## THE RULE THIS FILE IS WRITTEN UNDER, FROM ITS FIRST LINE

``PAGE-MAY-VETO-NEVER-SUPPLY`` (registered 2026-09-24): every navigation
address is composed from ARGUMENTS; page content may only REFUSE a navigation,
never provide one. Here that is three mechanisms, each enforced rather than
remembered:

* **EVERY ADDRESS IS A MODULE CONSTANT, OR ONE OF THE PACKAGE'S OWN COMPOSERS
  FILLED FROM THE CALLER'S ``--item``** -- ``search_verticals.compose``,
  ``member_rosters.compose``, a digit template -- and every item is validated
  as a closed shape (1-20 ASCII digits, or a thread id by ``threads``' own
  rule) before anything loads. Session 1's harness first took his newest
  post's id off a page it had read; this one never does, which is why
  ``tests/test_navigation_is_never_derived.py`` holds no entry for it.
* **A PAGE MAY SAY NO.** Where an item must be HIS -- a group he belongs to, a
  post he wrote -- or must be one a page drew -- an event's own attendees
  list -- the caller's value is checked against what an earlier reading
  returned (:func:`veto_group`, :func:`veto_activity`,
  :func:`veto_attendees`), and a mismatch refuses the key with nothing
  loaded. The reading answers yes or no; it never becomes an address.
* **THE CALLER MAY READ A RESULT AND NAME AN ITEM FROM IT; THIS FILE NEVER
  DOES.** ``job_detail`` writes the organisation id it resolved to
  ``_state/live2/``, and ``n84`` takes an organisation only as ``--item``:
  the choosing is the caller's, outside this code, which is the division the
  rule draws for every tool.

**OUTWARD ACTS ARE NOT HERE.** No key writes, sends, follows or saves. The
plan's outward block runs as individual tool calls after he has seen each
resolved identity once -- never from a harness.

## THE LEDGER, THE SEARCH CAP, ONE DRIVER

``_state/live2/ledger.json`` (gitignored) counts every navigation any key
makes -- a shipped tool's own included -- through a wrapper around
``BROWSER.goto``. It refuses the 41st load BEFORE navigating
(``LIVE-BUDGET-40-LOADS``), waits out 20 s since the ledger's last load across
processes, and refuses a sixth ``/search/`` load before navigating
(``D1-SEARCH-AS-READS``: five test searches a session). A driver lock in the
same directory refuses a second harness process: one driver at a time.

## WHAT LEAVES THIS PROCESS, AND WHAT IS WRITTEN

Printed: integers, booleans, field names, and the package's own closed words.
Written under ``_state/live2/`` (gitignored), never committed:

* a RAW capture of ONE page only -- his "Share profile updates" setting,
  which draws no other person;
* for every other page a SKELETON reduced in this process before anything is
  written (:func:`skeleton_of`): tags, attribute names, classes, roles and
  closed ARIA states kept; every other text node and attribute value replaced
  by its SHAPE and a keyed hash; LinkedIn's own UI words (:data:`FURNITURE`)
  kept verbatim. Lane S's reading of mitigation 3 of
  ``PEOPLE-DATA-MITIGATIONS``, adopted here for every page until the
  orchestrator rules on raw captures;
* tool envelopes RAW where the tool is name-free by its own contract, and
  REDUCED (:func:`reduce_envelope`) where it can carry a person.

**THE ONE STEP THAT WRITES INTO THE TREE, AND IT LOADS NOTHING:**
``--export-fixtures`` (:func:`export_fixtures`) writes each skeleton, and his
settings page reduced to one, as a TRACKED copy under
``tests/fixtures/live2/`` (:func:`tracked_copy`): every keyed shape of a text
becomes one ``x``, so neither a hash nor a length of anybody's words leaves
the box. What reaches a commit is then decided by the identity gate and the two
people guards, as for any fixture.

## THE ANOMALY RULE

An exception, an error envelope, an auth wall or a challenge phrase stops
every further load in the run, and so does any key that stops -- a veto
included: a refusal is an answer, and the lead reads it before more is spent.

Run it as::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 LINKEDIN_MIN_INTERVAL_S=20 \\
        ./venv/Scripts/python.exe scripts/_probe_live_lane_session_2.py \\
        --only setting,in_me,in_me_more [--item group=<digits>] [--no-capture]

and the one offline key, which attaches to nothing and loads nothing::

    ./venv/Scripts/python.exe scripts/_probe_live_lane_session_2.py --only setting_offline
"""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import html as html_escape
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Optional

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

from linkedin_server import (  # noqa: E402
    cdp_bridge,
    config,
    member_rosters,
    press,
    profile_editor,
    readonly,
    search_verticals,
    server,
    threads,
)
from linkedin_server.browser import BROWSER  # noqa: E402

import _probe_disclosure_targets as structure  # noqa: E402
import _probe_l1_admitted_reads_live as l1  # noqa: E402
import _probe_live_lane_session_1 as s1  # noqa: E402

STATE = _ROOT / "_state" / "live2"
LEDGER = STATE / "ledger.json"
DRIVER_LOCK = STATE / "driver.lock"
SHAPE_KEY_FILE = STATE / "shape.key"
LIVE1_ACTIVITY = _ROOT / "_state" / "live1" / "activity.json"

#: LIVE-BUDGET-40-LOADS and its spacing -- session 1's values, read from there
#: so the two sessions cannot disagree about one ruling.
CEILING = s1.CEILING
MIN_GAP_S = s1.MIN_GAP_S

#: D1-SEARCH-AS-READS: at most five test searches in a session. Every search
#: address this harness can reach starts ``/search/``, which is the surface
#: word the ledger records.
SEARCH_CAP = 5
SEARCH_SURFACE = "search"

# ---------------------------------------------------------------------------
# The addresses: constants, and the package's composers filled from --item.
# ---------------------------------------------------------------------------

SETTING_URL = profile_editor.ACCOUNT_SETTING_URL
ACTIVITY_ALL_URL = "https://www.linkedin.com/in/me/recent-activity/all/"
FOLLOWERS_URL = l1.FOLLOWERS_URL
COMPOSE_URL = threads.COMPOSE_URL
OWN_POST_TEMPLATE = s1.POST_URL_TEMPLATE
EVENT_TEMPLATE = l1.EVENT_URL_TEMPLATE

#: Lane S's search words (section F of its record), each generic: no employer
#: of his, no value that identifies him.
VERTICAL_SEARCHES: dict[str, tuple[str, str]] = {
    "n104": ("companies", "robotics"),
    "n161": ("groups", "open source"),
    "n179": ("events", "developer conference"),
}

#: Lane S's N 94 values: a generic keyword and two country-level geo ids --
#: "UNVERIFIED here, from recall" in its own words, neither his city nor his
#: country. A wrong id is itself the finding: ``query_kept`` reads it.
N94_KEYWORDS = "engineer"
N94_GEOS = "103644278,101165590"

#: THE ITEMS A CALLER MAY NAME, each a closed shape. Digits only for every id:
#: a slug is a name, and an id is what the package's composers take.
ITEM_SHAPES: dict[str, str] = {
    "activity": "digits",
    "posting": "digits",
    "org": "digits",
    "past_org": "digits",
    "group": "digits",
    "school": "digits",
    "event": "digits",
    "thread": "thread",
}

MAX_ID_DIGITS = 20

#: THE KEYS. ``kind`` picks the runner; ``loads`` is the most the key may
#: spend (the pre-check prices it); ``searches`` what it takes of the five;
#: ``items`` what the caller must name; ``after`` keys one of which must run
#: EARLIER in the same invocation (a rider presses on that key's page);
#: ``envelope`` raw or reduced for tools.
KEYS: dict[str, dict[str, Any]] = {
    "attach_check": {"kind": "attach", "loads": 0, "rows": "P C8 enabling: lane D LQ-4"},
    "setting": {"kind": "setting", "loads": 1,
                "rows": "P A8 A11 A13 A17 A19 A21, P B9: condition 1"},
    "setting_offline": {"kind": "offline", "loads": 0, "rows": "the (b) reader, on the capture"},
    "in_me": {"kind": "in_me", "loads": 2,
              "rows": "N 76, P J4, P D28, P K1; P F1 H11 K8 D26 read off the capture"},
    "in_me_more": {"kind": "in_me_more", "loads": 0, "after": ("in_me",),
                   "rows": "P C8: lane D LQ-1 (two openings)"},
    "me_menu": {"kind": "me_menu", "loads": 0, "after": ("in_me", "activity_all"),
                "rows": "lane Y item 9 (discovery curve)"},
    "activity_all": {"kind": "capture", "loads": 1, "rows": "M C85"},
    "followers": {"kind": "capture", "loads": 1, "rows": "P L2b"},
    "own_post": {"kind": "capture", "loads": 1, "items": ("activity",),
                 "rows": "M C29, M C42"},
    "m43": {"kind": "tool", "loads": 1, "rows": "M M43; lane L5 C1 rides"},
    "compose_presses": {"kind": "compose", "loads": 1,
                        "rows": "lane L5 C8, C9, C5: M M7 M8 M9 M28, M M22 M27 M29 M31, M M16"},
    "m33": {"kind": "tool", "loads": 2, "rows": "M M33"},
    "m49": {"kind": "tool", "loads": 2, "rows": "M M49"},
    "j18": {"kind": "tool", "loads": 1, "rows": "J 18; J 37 rides"},
    "j39": {"kind": "tool", "loads": 1, "rows": "J 39"},
    "j158": {"kind": "tool", "loads": 1, "rows": "J 158"},
    "n132": {"kind": "tool", "loads": 1, "envelope": "reduced", "rows": "N 132, P S5; P G7"},
    "notifications": {"kind": "tool", "loads": 1, "envelope": "reduced", "rows": "N 20, N 45"},
    "n23": {"kind": "tool", "loads": 2, "envelope": "reduced",
            "rows": "N 23; the named targets among his connections, counted"},
    "job_detail": {"kind": "tool", "loads": 1, "items": ("posting",), "envelope": "reduced",
                   "rows": "an org id for N 84, N 87, N 102; J 124, J 115, P M12 by the capture"},
    "n94": {"kind": "tool", "loads": 1, "searches": 1, "envelope": "reduced", "rows": "N 94, N 79"},
    "n84": {"kind": "tool", "loads": 1, "searches": 1, "items": ("org",), "envelope": "reduced",
            "rows": "N 84"},
    "n87": {"kind": "tool", "loads": 1, "searches": 1, "items": ("past_org",), "envelope": "reduced",
            "rows": "N 87"},
    "presence": {"kind": "tool", "loads": 1, "envelope": "reduced", "rows": "M M53"},
    "recruiter": {"kind": "tool", "loads": 1, "envelope": "reduced", "rows": "N 195"},
    "j107": {"kind": "tool", "loads": 1, "items": ("org",), "envelope": "reduced", "rows": "J 107"},
    "n104": {"kind": "capture", "loads": 1, "searches": 1, "rows": "N 104"},
    "n161": {"kind": "capture", "loads": 1, "searches": 1, "rows": "N 161"},
    "n179": {"kind": "capture", "loads": 1, "searches": 1, "rows": "N 179"},
    "memberships": {"kind": "tool", "loads": 3, "rows": "the ids the group vetoes read"},
    "group_home": {"kind": "tool", "loads": 1, "items": ("group",), "rows": "M C70"},
    "group_members": {"kind": "capture", "loads": 1, "items": ("group",), "rows": "N 165, N 177"},
    "company_people": {"kind": "capture", "loads": 1, "items": ("org",), "rows": "N 102, J 108"},
    "school_people": {"kind": "capture", "loads": 1, "items": ("school",),
                      "rows": "N 99, N 100, J 112"},
    "event": {"kind": "capture", "loads": 1, "items": ("event",), "rows": "N 184"},
    "event_attendees": {"kind": "capture", "loads": 1, "items": ("event",),
                        "rows": "N 188, N 189"},
    "thread": {"kind": "tool", "loads": 2, "items": ("thread",), "envelope": "reduced",
               "rows": "M M47 (C2), M M14 M15 M18 (C3 b), M M30 (C10), M M49 fallback"},
}

#: Keys whose item must be HIS, and the veto that says so.
GROUP_VETOED = frozenset({"group_home", "group_members"})

#: Field names whose short ASCII string values are this package's own closed
#: words, printed and kept whole. Session 1's, plus this session's.
LITERAL_FIELDS = s1.LITERAL_FIELDS | frozenset({
    "reading", "relation", "verdict", "url_movement", "reach", "self_assertion",
    "behavior", "direction", "stopped",
})

#: Field names whose ASCII-digit values are an ORGANISATION, GROUP or POSTING
#: id -- never a person's -- and are kept in a reduced envelope so the caller
#: can name the next item from it.
ID_FIELDS = frozenset({"company_id", "identifiers", "group_id", "job_id", "job_ids"})


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
# Items, selection and vetoes -- decided before the browser is touched.
# ---------------------------------------------------------------------------


def _in_shape(shape: str, value: str) -> bool:
    """PURE. ASCII only, whatever the shape: ``isdigit`` alone admits other
    scripts' digits, which the boundary's closed segments exist to refuse."""
    if not value or not value.isascii():
        return False
    if shape == "digits":
        return len(value) <= MAX_ID_DIGITS and all(ch in "0123456789" for ch in value)
    if shape == "thread":
        return threads.valid_thread_id(value)
    return False


def parse_items(argv: list[str]) -> dict[str, str]:
    """``--item name=value`` pairs, each of a closed shape. PURE.

    Refuses via SystemExit, and never echoes the value: whatever was typed
    might be a slug or a pasted address, and a refusal is not a print.
    """
    items: dict[str, str] = {}
    for position, word in enumerate(argv):
        if word != "--item":
            continue
        if position + 1 >= len(argv) or "=" not in argv[position + 1]:
            raise SystemExit("REFUSING: --item needs name=value.")
        name, _, value = argv[position + 1].partition("=")
        shape = ITEM_SHAPES.get(name)
        if shape is None:
            raise SystemExit("REFUSING: unknown item; the closed set is " + str(sorted(ITEM_SHAPES)))
        if name in items:
            raise SystemExit("REFUSING: the " + name + " item is named twice.")
        if not _in_shape(shape, value):
            raise SystemExit("REFUSING: the " + name + " item is not of its closed shape (" + shape + ").")
        items[name] = value
    return items


def selected(argv: list[str], items: dict[str, str]) -> list[str]:
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
        raise SystemExit("REFUSING: unknown key(s); the closed set is " + str(sorted(KEYS)))
    if len(set(wanted)) != len(wanted):
        raise SystemExit("REFUSING: a key is named twice.")
    for alone in ("setting_offline", "attach_check"):
        if alone in wanted and len(wanted) != 1:
            raise SystemExit("REFUSING: " + alone + " runs alone.")
    for position, key in enumerate(wanted):
        missing = [n for n in KEYS[key].get("items", ()) if n not in items]
        if missing:
            raise SystemExit("REFUSING: key " + key + " needs --item " + ",".join(missing)
                             + " -- the caller names every item; no page supplies one.")
        after = KEYS[key].get("after", ())
        if after and not any(k in wanted[:position] for k in after):
            raise SystemExit("REFUSING: " + key + " presses on the page one of "
                             + ",".join(after) + " leaves open; name it earlier in the run.")
    return wanted


def address_for(key: str, items: dict[str, str]) -> Optional[str]:
    """The ONE address a capture key loads. PURE.

    Built from a module constant, or from one of the package's own composers
    filled from the caller's validated items -- never from a page. ``None``
    when a composer refuses (it reports the SHAPE it saw, never the value).
    """
    if key == "activity_all":
        return ACTIVITY_ALL_URL
    if key == "followers":
        return FOLLOWERS_URL
    if key == "own_post":
        return OWN_POST_TEMPLATE.format(digits=items["activity"])
    if key == "event":
        return EVENT_TEMPLATE.format(items["event"])
    if key in VERTICAL_SEARCHES:
        vertical, words = VERTICAL_SEARCHES[key]
        built = search_verticals.compose(vertical, keywords=words)
    elif key == "group_members":
        built = member_rosters.compose("group_members", items["group"])
    elif key == "company_people":
        built = member_rosters.compose("company_people", items["org"])
    elif key == "school_people":
        built = member_rosters.compose("school_people", items["school"])
    elif key == "event_attendees":
        built = member_rosters.compose("event_attendees", items["event"])
    else:
        raise ValueError("no address for key " + key)
    return built["url"] if built.get("built") else None


def veto_group(group: str, memberships_raw: Any) -> Optional[str]:
    """THE PAGE MAY SAY NO. ``None`` when ``group`` is among the MEMBERSHIPS
    his own Groups page returned this session -- not its suggestions; else the
    reason. PURE. The address is composed from the caller's ``group`` either
    way; this list only answers yes or no."""
    if not isinstance(memberships_raw, dict):
        return "no memberships reading from this session -- run the 'memberships' key first"
    block = memberships_raw.get("memberships")
    identifiers = block.get("identifiers") if isinstance(block, dict) else None
    if not isinstance(identifiers, list):
        return "the memberships reading carries no identifiers list"
    if group not in {str(value) for value in identifiers}:
        return "the group is not among the memberships his Groups page returned"
    return None


def veto_activity(activity: str, *raws: Any) -> Optional[str]:
    """``None`` when ``activity`` is one of HIS posts, by a rail reading whose
    authorship was ESTABLISHED; else the reason. PURE."""
    his: set[str] = set()
    for raw in raws:
        his |= s1.own_activity_ids(raw)
    if not his:
        return "no authorship-established reading of his rail on disk"
    if activity not in his:
        return "the post is not among the items his rail returned as his own"
    return None


def veto_attendees(event: str, event_reading: Any, key: bytes) -> Optional[str]:
    """``None`` when THIS session's ``event`` key read THIS event and its page
    drew a link to its own attendees list; else the reason. PURE. Lane S's F.8
    step 2 runs only if step 1 draws that list."""
    if not isinstance(event_reading, dict):
        return "no event reading from this session -- run the 'event' key for this id first"
    if event_reading.get("event_shape") != value_shape(event, key):
        return "the event reading on disk is for another event"
    if event_reading.get("attendees_link_drawn") is not True:
        return "the event page drew no link to its own attendees list"
    return None


def _environment_refusal() -> Optional[str]:
    """``None`` when attach mode and the spacing are set; else the reason."""
    if not config.CDP_ATTACH:
        return "LINKEDIN_CDP_ATTACH is not set; this attaches, it never launches."
    if float(config.MIN_NAVIGATION_INTERVAL_S) < MIN_GAP_S:
        return "LINKEDIN_MIN_INTERVAL_S is below " + str(int(MIN_GAP_S)) + "."
    return None


def _json_or_none(path: Path) -> Any:
    """A JSON file of this lane's own state, or None. Never raises."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _envelope_of(path: Path) -> Any:
    """The tool envelope a key of this harness wrote, or None."""
    written = _json_or_none(path)
    return written.get("envelope") if isinstance(written, dict) else None


# ---------------------------------------------------------------------------
# The ledger: loads, spacing, searches, one driver.
# ---------------------------------------------------------------------------


def _ledger_read() -> dict[str, Any]:
    if not LEDGER.exists():
        return {"session": "live-lane-session-2", "ceiling": CEILING,
                "min_gap_s": MIN_GAP_S, "search_cap": SEARCH_CAP, "loads": []}
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
                + " loads; this run may need " + str(planned))
    return None


def searches_spent(loads: list[dict[str, Any]]) -> int:
    """How many of the session's loads were searches. PURE."""
    return sum(1 for row in loads if row.get("surface") == SEARCH_SURFACE)


def search_verdict(loads: list[dict[str, Any]], planned: int) -> Optional[str]:
    """``None`` when ``planned`` more searches fit under D1's five. PURE."""
    if searches_spent(loads) + planned > SEARCH_CAP:
        return ("the session has spent " + str(searches_spent(loads)) + " of "
                + str(SEARCH_CAP) + " searches; this run may need " + str(planned))
    return None


def gap_remaining(loads: list[dict[str, Any]], now: float) -> float:
    """Seconds still owed before the next load may start. PURE."""
    if not loads:
        return 0.0
    return max(0.0, MIN_GAP_S - (now - float(loads[-1]["at"])))


_CURRENT = {"key": "none"}


def _install_counter() -> None:
    """Wrap ``BROWSER.goto`` so every navigation passes the ledger first."""
    original = BROWSER.goto

    async def counted_goto(page: Any, url: str, **kwargs: Any) -> str:
        # THE SECOND DOOR COUNTS TOO (found live, 2026-09-28): a named-person
        # act loads the one profile its caller named through
        # ``named_profile=True``, an address the READ door refuses -- so the
        # first version of this wrapper waved it through uncounted and
        # unspaced. Only an address NEITHER door admits passes uncounted, and
        # ``original`` refuses it before ``page.goto``.
        second_door = kwargs.get("named_profile") is True
        if not second_door and not readonly.is_read_url(url):
            return await original(page, url, **kwargs)
        loads = _ledger_read()["loads"]
        if len(loads) >= CEILING:
            raise _LedgerRefusal("load " + str(len(loads) + 1) + " would pass the ceiling")
        surface = s1._surface_of(url)
        if surface == SEARCH_SURFACE and searches_spent(loads) >= SEARCH_CAP:
            raise _LedgerRefusal("search " + str(searches_spent(loads) + 1) + " would pass D1's five")
        owed = gap_remaining(loads, time.time())
        if owed > 0:
            await asyncio.sleep(owed)
        try:
            return await original(page, url, **kwargs)
        finally:
            number = _ledger_append(_CURRENT["key"], surface)
            say("    [ledger] load " + str(number) + " of " + str(CEILING) + " (" + surface + ")")

    BROWSER.goto = counted_goto  # type: ignore[method-assign]


def _take_driver_lock() -> Optional[str]:
    """One driver at a time. ``None`` when taken; else why it was not."""
    STATE.mkdir(parents=True, exist_ok=True)
    try:
        handle = os.open(str(DRIVER_LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return "another harness process holds the driver lock under _state/live2/"
    os.close(handle)
    return None


def _release_driver_lock() -> None:
    try:
        os.remove(str(DRIVER_LOCK))
    except OSError:
        say("    the driver lock could not be released; delete it by hand once no run is live")


# ---------------------------------------------------------------------------
# Shapes: what may be printed, and what a skeleton keeps.
# ---------------------------------------------------------------------------


def shape_of(value: Any, key: str = "", depth: int = 0) -> str:
    """One value, rendered without its content. PURE. Session 1's printer,
    with this session's literal fields."""
    if value is None or isinstance(value, bool) or isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return format(value, ".4g")
    if isinstance(value, str):
        if key in LITERAL_FIELDS and len(value) <= 40 and value.isascii():
            return "'" + value + "'"
        return "str(len=" + str(len(value)) + ")"
    if isinstance(value, (list, tuple)):
        dicts = [v for v in value if isinstance(v, dict)]
        inner = ", item keys " + s1._key_list({k for d in dicts for k in d}) if dicts else ""
        return "list(len=" + str(len(value)) + inner + ")"
    if isinstance(value, dict):
        if depth >= 2:
            return "dict(keys=" + s1._key_list(value) + ")"
        named = sorted((str(k), v) for k, v in value.items() if s1.is_field_name(k))
        withheld = sum(1 for k in value if not s1.is_field_name(k))
        parts = [k + ": " + shape_of(v, k, depth + 1) for k, v in named]
        if withheld:
            parts.append(str(withheld) + " key(s) withheld: not field names")
        return "{" + "; ".join(parts) + "}"
    return type(value).__name__


def _shape_key() -> bytes:
    """This session's hashing key, made once and kept under ``_state/live2/``.

    KEYED, so a shape's hash compares two captures of this session and cannot
    be reversed by hashing a list of names -- a plain truncated digest of a
    name can be.
    """
    STATE.mkdir(parents=True, exist_ok=True)
    if not SHAPE_KEY_FILE.exists():
        SHAPE_KEY_FILE.write_text(os.urandom(32).hex(), encoding="utf-8")
    return bytes.fromhex(SHAPE_KEY_FILE.read_text(encoding="utf-8").strip())


def value_shape(text: str, key: bytes) -> str:
    """A string's SHAPE: its letters, digits and length, and an 8-hex keyed
    hash -- enough to compare, nothing to read. PURE. No angle brackets, so a
    shape inside a skeleton is text and never parses as an element."""
    letters = sum(1 for ch in text if ch.isalpha())
    digits = sum(1 for ch in text if ch.isdigit())
    mark = hmac.new(key, text.encode("utf-8"), hashlib.sha256).hexdigest()[:8]
    return "{L" + str(letters) + "D" + str(digits) + "n" + str(len(text)) + ":" + mark + "}"


#: LinkedIn's own UI words, closed. A text node, or an aria-label, alt, title,
#: placeholder or value EQUAL to one survives a skeleton verbatim; the same
#: set is what an opened menu is counted against. Every entry is a label
#: LinkedIn writes, never his data. The ellipsis is U+2026, built with chr()
#: so this file stays ASCII.
FURNITURE: frozenset[str] = frozenset({
    # the global nav, and the Me menu
    "Home", "My Network", "Jobs", "Messaging", "Notifications", "Me", "For Business",
    "Work", "Premium", "Search", "View Profile", "Account", "Settings & Privacy", "Help",
    "Language", "Manage", "Posts & Activity", "Job Posting Account", "Sign Out",
    "Try Premium for free", "Premium features", "Learning",
    # his profile's sections and rails
    "About", "Activity", "Experience", "Education", "Skills", "Recommendations",
    "Services", "Featured", "Licenses & certifications", "Interests", "Languages",
    "Honors & awards", "Projects", "Volunteering", "Courses", "Publications", "Causes",
    "Organizations", "Test scores", "Patents", "Analytics", "Resources",
    "Suggested for you", "People also viewed", "People you may know", "You might like",
    "Top Voice", "Profile strength", "Open to", "Add profile section", "Enhance profile",
    "Verifications", "Verification", "Verified",
    # the profile's More menu
    "More", "Save to PDF", "Send profile in a message", "Share profile via message",
    "Copy link to profile", "Request a recommendation", "Recommend", "Report / Block",
    "About this profile", "Build a resume", "Create a resume", "Follow", "Unfollow",
    "Following", "Connect", "Remove connection", "Message",
    # posts and comments
    "Show all", "See all", "Show more", "Show less", "See more", "Load more comments",
    "Most relevant", "Most recent", "Comment", "Like", "Repost", "Send", "Share",
    # messaging
    "Focused", "Other", "Unread", "My Connections", "InMail", "Starred", "Archived",
    "Spam", "Message requests", "Sent", "Drafts", "Mark as unread", "Mark as read",
    "Star", "Unstar", "Mute", "Unmute", "Archive", "Unarchive", "Delete",
    "Delete conversation", "Report", "Move to Other", "Move to Focused",
    "Manage settings", "Leave conversation", "Open GIF Keyboard",
    "Open Emoji Keyboard", "Search GIFs", "Attach an image for your draft conversation",
    "Attach a file for your draft conversation", "Maximize compose field",
    "Open send options", "Star conversation", "Unstar conversation",
    "Conversation List", "Write a message" + chr(0x2026), "New message", "Compose message",
    # groups, events, search
    "Members", "People", "Posts", "Events", "Groups", "Companies", "All filters", "Reset",
    "Join", "Request to join", "Attend", "Register", "Attendees", "Show results",
    "Next", "Previous",
    # the settings page: the (b) reader's first name for the switch, and the
    # words the live page drew on 2026-09-28 -- its heading, and the switch's
    # own label, which a skeleton must keep for a label to name its control
    "Sharing profile edits", "Share profile updates", "Share key profile updates",
    "On", "Off", "Back", "Visibility", "Account preferences",
    "Sign in & security", "Data privacy", "Advertising data",
    # everywhere
    "Close", "Dismiss", "Cancel", "Save", "Done", "Edit", "Menu",
})

#: Attributes whose VALUE a skeleton keeps whole: closed vocabularies LinkedIn
#: writes, which a reader's selectors are built on.
CODE_ATTRIBUTES: frozenset[str] = frozenset({
    "class", "role", "type", "tabindex", "dir", "lang", "aria-expanded",
    "aria-haspopup", "aria-checked", "aria-pressed", "aria-hidden", "aria-selected",
    "aria-current", "aria-disabled", "aria-live", "aria-modal", "aria-orientation",
    "aria-level", "aria-busy", "disabled", "checked", "hidden", "method",
    "autocomplete", "loading", "target", "rel",
})

#: Attributes that POINT at an id: each token shaped with the same key as the
#: id it names, so a label still finds its control in the skeleton.
ID_REF_ATTRIBUTES: frozenset[str] = frozenset({
    "id", "for", "aria-labelledby", "aria-describedby", "aria-controls", "aria-owns",
    "headers", "form", "list",
})

#: Attributes that carry an address: the path's own words kept, the rest shaped.
ADDRESS_ATTRIBUTES: frozenset[str] = frozenset({"href", "action", "src", "srcset"})

#: Attributes whose value may be one of LinkedIn's UI words.
LABEL_ATTRIBUTES: frozenset[str] = frozenset({
    "aria-label", "alt", "title", "placeholder", "value", "aria-description",
    "aria-roledescription",
})

_VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input",
                   "link", "meta", "param", "source", "track", "wbr"})
_DROPPED = frozenset({"script", "style", "noscript", "code", "template"})
_VIEW_NAME = re.compile(r"^[a-z]+(-[a-z]+){0,10}$")
_TEST_HOOK_VALUE = re.compile(r"^[A-Z_]{0,40}$")
_PARAM_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,40}$")
_URN = re.compile(r"^urn:li:([A-Za-z_]{1,40}):(.+)$")
_ARIA_NAME = re.compile(r"^aria-[a-z]{1,30}$")

#: LinkedIn's own path words, which an address in a skeleton keeps.
PATH_WORDS: frozenset[str] = frozenset({
    "https:", "www.linkedin.com", "in", "me", "company", "school", "groups", "events",
    "feed", "update", "messaging", "thread", "compose", "mynetwork", "search",
    "results", "people", "companies", "content", "all", "jobs", "view", "mypreferences",
    "d", "settings", "recent-activity", "posts", "members", "attendees", "analytics",
    "overlay", "edit", "details", "network-manager", "people-follow", "followers",
    "following", "invite-connect", "connections", "notifications", "about", "life",
    "verifications", "verification", "trust",
})


def _address_shape(address: str, key: bytes) -> str:
    """An address with LinkedIn's own words kept and every other segment,
    query value and urn id shaped. PURE. The fragment is dropped."""
    base = address.partition("#")[0]
    path, _, query = base.partition("?")
    kept: list[str] = []
    for segment in path.split("/"):
        urn = _URN.match(segment)
        if segment == "" or segment in PATH_WORDS:
            kept.append(segment)
        elif urn:
            kept.append("urn:li:" + urn.group(1) + ":" + value_shape(urn.group(2), key))
        else:
            kept.append(value_shape(segment, key))
    out = "/".join(kept)
    if query:
        pairs = []
        for pair in query.split("&"):
            name, eq, value = pair.partition("=")
            shown = name if _PARAM_NAME.match(name) else value_shape(name, key)
            pairs.append(shown + ("=" + value_shape(value, key) if eq else ""))
        out += "?" + "&".join(pairs)
    return out


def _attribute_shape(name: str, value: str, key: bytes) -> str:
    """One attribute value as a skeleton keeps it. PURE."""
    if name in CODE_ATTRIBUTES:
        return value
    if name in ID_REF_ATTRIBUTES:
        return " ".join(value_shape(token, key) for token in value.split())
    if name in ADDRESS_ATTRIBUTES:
        return _address_shape(value, key)
    if name in LABEL_ATTRIBUTES and " ".join(value.split()) in FURNITURE:
        return value
    if name == "data-view-name" and _VIEW_NAME.match(value):
        return value
    if name.startswith("data-test") and _TEST_HOOK_VALUE.match(value):
        return value
    return value_shape(value, key)


class _Skeleton(HTMLParser):
    def __init__(self, key: bytes) -> None:
        super().__init__(convert_charrefs=True)
        self.key = key
        self.out: list[str] = []
        self.dropping = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag in _DROPPED:
            self.dropping += 1
            return
        if self.dropping:
            return
        parts = [tag]
        for name, value in attrs:
            if value is None:
                parts.append(name)
            else:
                shown = _attribute_shape(name, value, self.key)
                parts.append(name + '="' + html_escape.escape(shown, quote=True) + '"')
        self.out.append("<" + " ".join(parts) + ">")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag in _DROPPED:
            self.dropping = max(0, self.dropping - 1)
            return
        if self.dropping or tag in _VOID:
            return
        self.out.append("</" + tag + ">")

    def handle_data(self, data: str) -> None:
        if self.dropping:
            return
        text = " ".join(data.split())
        if not text:
            return
        shown = text if text in FURNITURE else value_shape(text, self.key)
        self.out.append(html_escape.escape(shown, quote=False))


def skeleton_of(page_html: str, key: bytes) -> str:
    """A page reduced before anything is written. PURE.

    Tags, attribute names, classes, roles and closed ARIA states are kept --
    a reader's selectors are built on those. Every other attribute value and
    every text node becomes its shape (:func:`value_shape`); an address keeps
    LinkedIn's own path words and query parameter NAMES; an id and every
    attribute naming it are shaped with one key, so a label still finds its
    control. A text node or a label EQUAL to a :data:`FURNITURE` word is kept.
    Scripts, styles and templates are dropped with their contents; comments
    are dropped. What stays is a document a browser still parses.
    """
    parser = _Skeleton(key)
    parser.feed(page_html)
    parser.close()
    return "<!doctype html>\n" + "\n".join(parser.out)


#: A keyed shape as :func:`value_shape` writes it: letters, digits, length, hash.
_KEYED_SHAPE = re.compile(r"\{L(\d{1,7})D(\d{1,7})n(\d{1,7}):([0-9a-f]{8})\}")

#: An id-reference attribute as :class:`_Skeleton` writes one: after a space,
#: its value in double quotes. The longest names first, so ``for`` never
#: claims the tail of a longer name.
_ID_REF_WRITTEN = re.compile(
    r'(?<= )(' + "|".join(sorted(ID_REF_ATTRIBUTES, key=len, reverse=True)) + r')="([^"]*)"'
)

#: Where the TRACKED copies of this session's skeletons live.
FIXTURES = _ROOT / "tests" / "fixtures" / "live2"


def tracked_copy(skeleton: str) -> str:
    """A session skeleton as a TRACKED file may hold it. PURE.

    THE KEYED HASHES STAY ON THIS BOX. Every shape of a non-empty value
    becomes ONE ``x`` (an empty one stays empty) -- the alphabet both of the
    repository's people guards admit as a value reduced to shape
    (``is_reduced_to_shape`` in
    ``tests/test_fixtures_hold_only_synthetic_people.py``, ``SHAPED_SLUG`` in
    ``tests/test_no_committed_identity.py``). So a tracked copy says of
    anybody's text only that it was there: not its length, which a name's
    shape would leak, and no hash, which whoever holds the key could test
    against a list of names. Rendering the LENGTH was tried first and
    rejected on its size: a shape stands for values of any length, and
    written out in full the 28 copies came to 14 MB. The one exception is an
    id reference: ``k`` and the 8-hex hash, the same for an id and every
    attribute naming it, because an id names a control, never a person, and
    a label must still find its control in the copy.

    Anything outside ASCII becomes a character reference, which a parser
    reads back as the same character: the copy is strict ASCII and draws the
    same document. Tags, attributes, classes, roles, ARIA states, LinkedIn's
    path words and :data:`FURNITURE` are the skeleton's, untouched.
    """
    def ids(match: "re.Match[str]") -> str:
        tokens = []
        for token in match.group(2).split():
            keyed = _KEYED_SHAPE.fullmatch(token)
            tokens.append("k" + keyed.group(4) if keyed else token)
        return match.group(1) + '="' + " ".join(tokens) + '"'

    reduced = _KEYED_SHAPE.sub(lambda m: "x" if int(m.group(3)) else "", _ID_REF_WRITTEN.sub(ids, skeleton))
    return reduced.encode("ascii", "xmlcharrefreplace").decode("ascii")


def export_fixtures() -> dict[str, int]:
    """Every skeleton of this session, and his settings page reduced to one,
    written as TRACKED copies (:func:`tracked_copy`) under
    ``tests/fixtures/live2/``. Zero loads; attaches to nothing. Returns each
    copy's name and size -- the only things printed."""
    FIXTURES.mkdir(parents=True, exist_ok=True)
    written: dict[str, int] = {}
    for path in sorted(STATE.glob("*.skeleton.html")):
        name = path.name[: -len(".skeleton.html")]
        text = tracked_copy(path.read_text(encoding="utf-8"))
        (FIXTURES / (name + ".html")).write_text(text, encoding="ascii", newline="\n")
        written[name] = len(text)
    raw = STATE / "setting.html"
    if raw.exists():
        text = tracked_copy(skeleton_of(raw.read_text(encoding="utf-8"), _shape_key()))
        (FIXTURES / "setting.html").write_text(text, encoding="ascii", newline="\n")
        written["setting"] = len(text)
    return written


def reduce_envelope(value: Any, key: bytes, field: str = "") -> Any:
    """A tool envelope with every person-bearing string shaped. PURE.

    Integers, booleans and None are kept; a string is kept whole only where
    its FIELD is one of this package's literal-word fields (a closed word, at
    most 40 ASCII characters) or an organisation, group or posting id field
    (1-20 ASCII digits); every other string is shaped. A key that is not a
    field name -- an item urn, say -- is withheld and counted.
    """
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        if field in LITERAL_FIELDS and len(value) <= 40 and value.isascii():
            return value
        if field in ID_FIELDS and _in_shape("digits", value):
            return value
        return value_shape(value, key)
    if isinstance(value, (list, tuple)):
        return [reduce_envelope(inner, key, field) for inner in value]
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        withheld = 0
        for name, inner in value.items():
            if s1.is_field_name(name):
                out[str(name)] = reduce_envelope(inner, key, str(name))
            else:
                withheld += 1
        if withheld:
            out["_withheld_keys"] = withheld
        return out
    return type(value).__name__


def _print_envelope(out: dict[str, Any]) -> None:
    for field in sorted(str(k) for k in out if s1.is_field_name(k)):
        say("    " + field + ": " + shape_of(out[field], field))
    withheld = sum(1 for k in out if not s1.is_field_name(k))
    if withheld:
        say("    " + str(withheld) + " top-level key(s) withheld: not field names")


def _write(key: str, suffix: str, text: str) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    (STATE / (key + suffix)).write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Readings on an open page. Every one returns counts, booleans or our words.
# ---------------------------------------------------------------------------


async def _health(page: Any, where: str) -> None:
    """Auth wall and challenge phrases on the page open now."""
    walled = any(marker in (page.url or "") for marker in config.AUTHWALL_MARKERS)
    hits = await structure._challenge_phrases_hit(page)
    matched = [p for p, hit in zip(structure.CHALLENGE_PHRASES, hits) if hit]
    say("    health: walled " + str(walled) + ", challenge terms " + str(len(matched)))
    if walled or matched:
        raise _Anomaly("auth_wall_or_challenge", where)


async def _save_page(page: Any, key: str, capture: bool, *, raw: bool = False) -> None:
    if not capture:
        return
    page_html = await page.content()
    if raw:
        _write(key, ".html", page_html)
        say("    RAW capture written under _state/ (gitignored): his own settings page")
    else:
        _write(key, ".skeleton.html", skeleton_of(page_html, _shape_key()))
        say("    skeleton written under _state/ (gitignored); no raw page")


#: Counts every VISIBLE text node and every visible element's aria-label
#: EQUAL to one of OUR words. Visible, because a menu LinkedIn keeps in the
#: DOM while closed must count as opened only when it shows. What crosses
#: back is our words and integers; the page's text never does.
_FURNITURE_JS = """
(words) => {
  const want = new Set(words);
  const counts = {};
  const norm = (s) => (s || "").replace(/\\s+/g, " ").trim();
  const shown = (el) => !!el && (!el.checkVisibility || el.checkVisibility({visibilityProperty: true}));
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) {
    const t = norm(node.textContent);
    if (want.has(t) && shown(node.parentElement)) counts[t] = (counts[t] || 0) + 1;
  }
  for (const el of document.querySelectorAll("[aria-label]")) {
    const t = norm(el.getAttribute("aria-label"));
    if (want.has(t) && shown(el)) counts["aria:" + t] = (counts["aria:" + t] || 0) + 1;
  }
  return counts;
}
"""


async def furniture_counts(page: Any) -> dict[str, int]:
    """How many times each of OUR words is drawn, as text or as an
    aria-label. Keys are only ever our own words."""
    counted = await page.evaluate(_FURNITURE_JS, sorted(FURNITURE))
    known = FURNITURE | {"aria:" + w for w in FURNITURE}
    return {str(k): int(v) for k, v in (counted or {}).items() if k in known}


def counts_delta(opened: dict[str, int], before: dict[str, int]) -> dict[str, int]:
    """What an opening ADDED, word by word. PURE."""
    return {w: opened[w] - before.get(w, 0) for w in sorted(opened)
            if opened[w] - before.get(w, 0) > 0}


def closed_again(added: dict[str, int], after: dict[str, int], before: dict[str, int],
                 expanded_after: Any, expanded_before: Any) -> bool:
    """Did the opening close? PURE. Every word it ADDED is gone again, and
    the trigger's aria-expanded reads what it read before the press. A word
    that appears for another reason -- a focus tooltip -- is not the menu."""
    gone = all(after.get(w, 0) <= before.get(w, 0) for w in added)
    return gone and expanded_after == expanded_before


#: THE OPENED MENU, READ BY ATTRIBUTE. From the trigger, its container (by
#: aria-controls, else its dropdown's content, else the one open dropdown),
#: then per item: tag, role, which aria-* attributes it carries, its
#: data-view-name, whether its componentkey is set, href or button, whether
#: its text is EXACTLY one of our words (the word returned is ours), and one
#: boolean per needle. Its label is compared inside the page, never returned.
_MENU_JS = """
(trigger, arg) => {
  const norm = (s) => (s || "").replace(/\\s+/g, " ").trim();
  const words = new Set(arg.words);
  let box = null;
  const ctl = trigger.getAttribute("aria-controls");
  if (ctl) box = document.getElementById(ctl);
  if (!box) {
    const dd = trigger.closest(".artdeco-dropdown");
    if (dd) box = dd.querySelector(".artdeco-dropdown__content");
  }
  if (!box) box = document.querySelector(".artdeco-dropdown__content--is-open");
  if (!box) return {container: false, items: []};
  let items = Array.from(box.querySelectorAll('[role="menuitem"]'));
  if (!items.length) items = Array.from(box.querySelectorAll(".artdeco-dropdown__item"));
  if (!items.length) items = Array.from(box.querySelectorAll("li"));
  return {container: true, items: items.map((e) => {
    const text = norm(e.innerText);
    const low = text.toLowerCase();
    return {
      tag: e.tagName.toLowerCase(),
      role: e.getAttribute("role"),
      aria: Array.from(e.attributes).map((a) => a.name).filter((n) => n.startsWith("aria-")).sort(),
      view: e.getAttribute("data-view-name"),
      componentkey: !!e.getAttribute("componentkey"),
      href: e.hasAttribute("href") || !!e.querySelector("a[href]"),
      button: e.tagName === "BUTTON" || e.getAttribute("role") === "button" || !!e.querySelector("button"),
      word: words.has(text) ? text : null,
      save_to_pdf: low === "save to pdf",
      needles: arg.needles.map((n) => low.includes(n)),
    };
  })};
}
"""

_TAGS = ("a", "button", "div", "span", "li", "input")
_ROLES = ("menuitem", "button", "option", "link", "menuitemcheckbox", "menuitemradio")
_HASPOPUP_WORDS = ("true", "false", "dialog", "menu", "listbox", "tree", "grid")


def item_record(raw: Any) -> dict[str, Any]:
    """One menu item, reduced to closed words, counts and booleans. PURE."""
    if not isinstance(raw, dict):
        return {"readable": False}
    tag = raw.get("tag")
    role = raw.get("role")
    view = raw.get("view")
    word = raw.get("word")
    aria = raw.get("aria") if isinstance(raw.get("aria"), list) else []
    return {
        "tag": tag if tag in _TAGS else "other",
        "role": role if role in _ROLES else ("none" if role is None else "other"),
        "aria_attributes": sorted(a for a in aria if isinstance(a, str) and _ARIA_NAME.match(a)),
        "view": view if isinstance(view, str) and _VIEW_NAME.match(view) else ("none" if view is None else "other"),
        "componentkey": raw.get("componentkey") is True,
        "href": raw.get("href") is True,
        "button": raw.get("button") is True,
        "word": word if word in FURNITURE else None,
        "save_to_pdf": raw.get("save_to_pdf") is True,
        "needles": [n is True for n in (raw.get("needles") or [])],
    }


def handle_signature(menu_items: list[dict[str, Any]]) -> Optional[tuple[Any, ...]]:
    """The attribute-only handle of THE Save-to-PDF item, or None when not
    exactly one item's text is that phrase. PURE. What lane D's LQ-1 asks to
    be stable across two openings."""
    matching = [one for one in menu_items if one.get("save_to_pdf")]
    if len(matching) != 1:
        return None
    one = matching[0]
    return (one.get("tag"), one.get("role"), one.get("view"), one.get("href"),
            one.get("button"), tuple(one.get("aria_attributes") or ()))


async def press_and_read(page: Any, key: str, handle: Any, capture: bool, *,
                         needles: tuple[str, ...] = (), messaging: bool = False) -> dict[str, Any]:
    """ONE press of ONE disclosing trigger, read open, then closed again.

    The trigger is an element handle the caller found as EXACTLY ONE match.
    The press is a click -- an OPEN verb by the probe rule
    (``tests/test_probe_interaction_budget.py``) -- and the close is Escape.
    Read: our words the opening ADDED (:func:`counts_delta`) and the opened
    menu's items by attribute (:data:`_MENU_JS`). Refused as an anomaly: a
    menu that did not close, and -- on ``/messaging/`` -- any message event on
    the page, which is a conversation opened.

    THE CLOSE STEP, FIX 4 OF SESSION 2. Live on 2026-09-28 the composer's
    folder menu (C8) opened and was still open after Escape, and the key
    stopped. Its skeleton, taken open, draws no close control of its own:
    four items, each a folder CHOICE -- pressing one would change his view --
    and a trigger that reads ``aria-expanded="true"`` while the menu is open,
    an artdeco dropdown's trigger, which toggles its own menu. A click outside
    was the other way, and on ``/messaging/`` there is no outside the
    skeleton can certify: the list beside the pill is conversations, and a
    click on one opens it. So when Escape leaves the trigger reading
    ``"true"`` -- and only then, and only if it read ``"false"`` before the
    press, so the click can only CLOSE what the first one opened -- the SAME
    trigger is pressed ONCE more. Never a third time: a menu still open after
    it is the same anomaly as before. ``closed_by`` says which step closed
    it: ``"escape"``, ``"trigger"``, or None. The trigger step's first live
    use is a session-3 fire.
    """
    expanded_before = await handle.get_attribute("aria-expanded")
    events_before = int(await page.locator(threads.EVIDENCE_EVENT_SELECTOR).count()) if messaging else 0
    if events_before:
        raise _Anomaly("a_conversation_is_open_before_the_press", key)
    before = await furniture_counts(page)
    await handle.click(timeout=5_000)
    await asyncio.sleep(s1.OPEN_SETTLE_S)
    opened = await furniture_counts(page)
    menu = await handle.evaluate(_MENU_JS, {"needles": list(needles), "words": sorted(FURNITURE)})
    events_open = int(await page.locator(threads.EVIDENCE_EVENT_SELECTOR).count()) if messaging else 0
    await _save_page(page, key + "-open", capture)
    added = counts_delta(opened, before)
    await page.keyboard.press("Escape")
    await asyncio.sleep(s1.OPEN_SETTLE_S)
    after = await furniture_counts(page)
    expanded_after = await handle.get_attribute("aria-expanded")
    closed_by = "escape" if closed_again(added, after, before, expanded_after, expanded_before) else None
    if closed_by is None and expanded_after == "true" and expanded_before == "false":
        await handle.click(timeout=5_000)
        await asyncio.sleep(s1.OPEN_SETTLE_S)
        after = await furniture_counts(page)
        expanded_after = await handle.get_attribute("aria-expanded")
        if closed_again(added, after, before, expanded_after, expanded_before):
            closed_by = "trigger"
    events_after = int(await page.locator(threads.EVIDENCE_EVENT_SELECTOR).count()) if messaging else 0
    menu_items = [item_record(raw) for raw in ((menu or {}).get("items") or [])]
    result = {
        "pressed": True,
        "container_found": (menu or {}).get("container") is True,
        "items": menu_items,
        "words_added": added,
        "closed_again": closed_by is not None,
        "closed_by": closed_by,
        "message_events": [events_before, events_open, events_after],
    }
    say("    pressed; menu items " + str(len(menu_items)) + ", our words added "
        + str(len(result["words_added"])) + ", closed again " + str(result["closed_again"])
        + (" (by its trigger)" if closed_by == "trigger" else ""))
    if events_open or events_after:
        raise _Anomaly("a_conversation_opened", key)
    if not result["closed_again"]:
        raise _Anomaly("the_menu_did_not_close", key)
    return result


async def _one_handle(locator: Any) -> tuple[Optional[Any], int]:
    """``(handle, count)``: an element handle when exactly one matches."""
    count = int(await locator.count())
    if count != 1:
        return None, count
    return await locator.element_handle(), count


# ---------------------------------------------------------------------------
# attach_check -- lane D's LQ-4, zero loads.
# ---------------------------------------------------------------------------

ARTIFACTS_PREFIX = "playwright-artifacts-"
DOWNLOAD_METHOD = "Browser.setDownloadBehavior"
_BEHAVIOURS = ("allowAndName", "allow", "deny", "default")
_MESSAGE_ID = re.compile(r'"id":\s*([0-9]+)')


def artifacts_count() -> int:
    """How many of the library's artifact folders sit in the OS temp dir."""
    folder = Path(tempfile.gettempdir())
    return sum(1 for entry in folder.iterdir() if entry.name.startswith(ARTIFACTS_PREFIX))


def _json_tail(text: str) -> Optional[dict[str, Any]]:
    at = text.find("{")
    if at < 0:
        return None
    try:
        payload = json.loads(text[at:])
    except ValueError:
        return None
    return payload if isinstance(payload, dict) else None


class ProtocolFilter:
    """``DEBUG=pw:protocol`` lines in; ONLY the download-behaviour sends and
    their answers kept, each reduced to closed words. Every other line names
    his open tabs and is dropped as it arrives: nothing of it is kept, not
    even the line."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self._sent: dict[int, int] = {}

    def feed(self, text: str) -> None:
        if "SEND" in text and DOWNLOAD_METHOD in text:
            payload = _json_tail(text)
            if payload is None or payload.get("method") != DOWNLOAD_METHOD:
                self.events.append({"direction": "send", "parsed": False})
                return
            params = payload.get("params") if isinstance(payload.get("params"), dict) else {}
            behavior = params.get("behavior")
            self.events.append({
                "direction": "send", "parsed": True,
                "behavior": behavior if behavior in _BEHAVIOURS else "other",
                "download_path": "downloadPath" in params,
                "context_id": "browserContextId" in params,
            })
            if isinstance(payload.get("id"), int):
                self._sent[payload["id"]] = len(self.events) - 1
            return
        if "RECV" not in text or not self._sent:
            return
        found = _MESSAGE_ID.search(text)
        if found is None or int(found.group(1)) not in self._sent:
            return
        payload = _json_tail(text)
        if payload is None or payload.get("id") not in self._sent:
            return
        self.events.append({
            "direction": "answer", "parsed": True,
            "answers": self.events[self._sent[payload["id"]]].get("behavior"),
            "error": "error" in payload,
        })


def protocol_events(lines: Any) -> list[dict[str, Any]]:
    """:class:`ProtocolFilter` over a sequence of lines. PURE."""
    kept = ProtocolFilter()
    for text in lines:
        kept.feed(text)
    return kept.events


def attach_verdict(events: list[dict[str, Any]], before: int, during: Optional[int],
                   after: int, restored: Any, error: Any) -> str:
    """Lane D's LQ-4 rule, as one closed word. PURE.

    PASS: ``allowAndName`` sent WITH a path, then ``default`` sent with NONE,
    both answered without error, in that order; the artifacts folder appears
    at the attach and is gone after; the reset record reads restored with no
    error. Anything else FAILS, and the word says which part.
    """
    sends = [e for e in events if e.get("direction") == "send"]
    answers = [e for e in events if e.get("direction") == "answer"]
    order = [(e.get("behavior"), e.get("download_path")) for e in sends]
    if order != [("allowAndName", True), ("default", False)]:
        return "FAIL-ORDER"
    if len(answers) != 2 or any(a.get("error") for a in answers):
        return "FAIL-ACKNOWLEDGEMENT"
    if during is None or during <= before or after != before:
        return "FAIL-FOLDER"
    if restored is not True or error is not None:
        return "FAIL-RECORD"
    return "PASS"


async def _attach_child() -> int:
    """THE CHILD: attach, read, detach. Opens no tab and loads no page."""
    await BROWSER.start()
    try:
        during = artifacts_count()
        reset = dict(cdp_bridge.LAST_DOWNLOAD_RESET)
    finally:
        await BROWSER.stop()
    error = reset.get("error")
    say(json.dumps({"during": during, "restored": reset.get("restored") is True,
                    "error": error if isinstance(error, str) and error.isidentifier() else None}))
    return 0


def _attach_check() -> dict[str, Any]:
    """Run the attach in a CHILD with the driver's protocol log on, and keep
    only the download-behaviour lines of its stderr, as they arrive."""
    before = artifacts_count()
    env = dict(os.environ)
    env["DEBUG"] = "pw:protocol"
    child = subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), "--attach-child"],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace",
    )
    kept = ProtocolFilter()
    for text in child.stderr:
        kept.feed(text)
    child_out = child.stdout.read()
    child.wait(timeout=120)
    after = artifacts_count()
    lines_out = child_out.strip().splitlines()
    report = _json_tail(lines_out[-1]) if lines_out else None
    during = report.get("during") if isinstance(report, dict) else None
    restored = report.get("restored") if isinstance(report, dict) else None
    error = report.get("error") if isinstance(report, dict) else "no_child_report"
    verdict = attach_verdict(kept.events, before, during if isinstance(during, int) else None,
                             after, restored, error)
    out = {"verdict": verdict, "events": kept.events, "artifacts": [before, during, after],
           "restored": restored, "error": error, "child_exit": child.returncode}
    _write("attach_check", ".json", json.dumps(out, indent=2))
    say("    events " + str(len(kept.events)) + "; artifacts before/during/after "
        + str(out["artifacts"]) + "; restored " + str(restored) + "; verdict " + verdict)
    return out


# ---------------------------------------------------------------------------
# setting / setting_offline -- the (b) reader, live and on its own capture.
# ---------------------------------------------------------------------------


def named_setting_control(page: Any) -> Any:
    """The reader's own locator, restated: controls of role switch or
    checkbox named exactly :data:`profile_editor.ACCOUNT_SETTING_NAME`. A
    test holds the two equal on the (b) worlds."""
    name = profile_editor.ACCOUNT_SETTING_NAME
    return page.get_by_role("switch", name=name, exact=True, include_hidden=True).or_(
        page.get_by_role("checkbox", name=name, exact=True, include_hidden=True))


async def state_in_markup(page: Any) -> dict[str, Optional[int]]:
    """Can a CAPTURE carry the switch's state? For the one named control, the
    ``checked`` PROPERTY (what the reader reads) against the ``checked``
    ATTRIBUTE (what ``page.content()`` writes). Counts."""
    named = named_setting_control(page)
    if int(await named.count()) != 1:
        return {"checked_property": None, "checked_attribute": None}
    return {
        "checked_property": int(await named.and_(page.locator(":checked")).count()),
        "checked_attribute": int(await named.and_(page.locator("[checked]")).count()),
    }


async def _setting(capture: bool) -> dict[str, Any]:
    async with BROWSER.session() as page:
        landed = await BROWSER.goto(page, SETTING_URL)
        relation = l1._relation(landed, SETTING_URL)
        setting_served = profile_editor.served_at_account_setting(landed)
        served_now = setting_served is True
        say("    relation: " + shape_of(relation, "relation") + "; served " + str(served_now))
        await _health(page, "setting")
        live_reading = await profile_editor.read_account_share_updates(page)
        in_markup = await state_in_markup(page)
        await _save_page(page, "setting", capture, raw=True)
    out = {
        "relation": relation,
        "served": served_now,
        "reading": live_reading.get("reading") if served_now else "unknown",
        "named": live_reading.get("named"),
        "input": live_reading.get("input"),
        "aria": live_reading.get("aria"),
        "error": live_reading.get("error"),
        **in_markup,
    }
    _write("setting", ".json", json.dumps(out, indent=2))
    say("    reading: " + shape_of(out["reading"], "reading") + "; named " + str(out["named"])
        + "; input " + str(out["input"]) + "; checked property/attribute "
        + str(out["checked_property"]) + "/" + str(out["checked_attribute"]))
    if not served_now:
        say("    REDIRECTED: the other candidate needs its own admission; nothing more is read.")
        out["stopped"] = "setting_page_redirected"
    return out


def offline_verdict(live: Any, offline: Any) -> str:
    """Does the reader read its own capture as it read the live page? PURE.

    AGREES              the same control, found the same way, the same reading.
    STATE-NOT-IN-MARKUP the same control, but its state lives in the checked
                        PROPERTY alone, which a capture cannot hold; the live
                        reading stands on its own (the orchestrator's call).
    STRUCTURE-DIFFERS   the capture does not reproduce the control.
    DISAGREES           the same control, its state in the markup, and a
                        different reading: the reader is wrong somewhere.
    LIVE-UNKNOWN        the live reading was not off or on.
    NO-LIVE-READING     the page was not served, or no live reading exists.
    NO-OFFLINE-READING  the capture could not be read.
    """
    if not isinstance(live, dict) or live.get("served") is not True:
        return "NO-LIVE-READING"
    if live.get("reading") not in ("off", "on"):
        return "LIVE-UNKNOWN"
    if not isinstance(offline, dict):
        return "NO-OFFLINE-READING"
    for field in ("named", "input", "aria"):
        if offline.get(field) != live.get(field):
            return "STRUCTURE-DIFFERS"
    if live.get("input") == 1 and live.get("checked_property") != live.get("checked_attribute"):
        return "STATE-NOT-IN-MARKUP"
    if offline.get("reading") == live.get("reading"):
        return "AGREES"
    return "DISAGREES"


async def replay_reading(captured: str) -> dict[str, Any]:
    """The (b) reader over a captured document, in a local headless Chromium
    whose context is OFFLINE and runs NO script. Attaches to nothing."""
    from playwright.async_api import async_playwright

    async with async_playwright() as pw:
        local_chromium = await pw.chromium.launch(headless=True)
        try:
            offline_context = await local_chromium.new_context(offline=True, java_script_enabled=False)
            replay = await offline_context.new_page()
            await replay.set_content(captured, wait_until="domcontentloaded")
            return await profile_editor.read_account_share_updates(replay)
        finally:
            await local_chromium.close()


async def _setting_offline() -> dict[str, Any]:
    """The reader on the CAPTURE. Zero loads; attaches to nothing."""
    capture_path = STATE / "setting.html"
    live = _json_or_none(STATE / "setting.json")
    if not capture_path.exists() or not isinstance(live, dict):
        say("    NO CAPTURE ON DISK: run the 'setting' key first. Nothing read.")
        return {"verdict": "NO-CAPTURE"}
    offline = await replay_reading(capture_path.read_text(encoding="utf-8"))
    verdict = offline_verdict(live, offline)
    out = {"verdict": verdict, "offline_reading": offline.get("reading"),
           "offline_named": offline.get("named"), "live_reading": live.get("reading")}
    _write("setting_offline", ".json", json.dumps(out, indent=2))
    say("    offline reading " + shape_of(offline.get("reading"), "reading") + " (named "
        + str(offline.get("named")) + "); live " + shape_of(live.get("reading"), "reading")
        + "; verdict " + shape_of(verdict, "verdict"))
    return out


# ---------------------------------------------------------------------------
# His own pages.
# ---------------------------------------------------------------------------

#: The needles for N 76's step 4, as the 2026-09-19 plan wrote them.
N76_NEEDLES = ("copy link", "follow link", "share profile", "personal link")

#: THE TOP CARD'S MORE, BY ITS NAME -- lane D's LQ-1 -- taken inside the top
#: card and only when exactly ONE is VISIBLE (:func:`topcard_control`).
#:
#: FIX 3 OF SESSION 2. The first handle was page-wide and blind to drawing:
#: ``main button[aria-label="More"][aria-expanded="false"]``, one match on
#: session 1's capture. On 2026-09-28 his profile drew that one match and it
#: never became actionable -- twice with the window in front, and a scroll
#: into view timed out before any click. Today's skeleton says why: the new
#: markup draws the top card's actions TWICE, in two bars, of which the page
#: shows one at a time. On his profile the bar holding the labelled More is
#: the one his window width does not show; the bar it shows holds
#: "Resources" where the other holds More. On the brother's profile both bars
#: hold a More -- one by its label, one by its text -- and one was visible.
MORE_NAME = "More"

#: The top card's own words, counted drawn and visible on every ``in_me``
#: load: which bar his window shows, read, never pressed.
TOPCARD_WORDS = ("More", "Resources", "Open to", "Enhance profile", "Add profile section")


def topcard_of(page: Any) -> Any:
    """THE TOP CARD, BY STRUCTURE: the nearest section around the first
    ``h2`` in main. Measured on today's skeletons of both profiles: the new
    markup draws no ``h1``; the name is the top card's one ``h2``, and its
    section holds both action bars and nothing else a name can match. No
    class is used -- the classes are hashed and move with LinkedIn's
    builds."""
    return page.locator("main h2").first.locator("xpath=ancestor::section[1]")


async def topcard_control(page: Any, name: str) -> tuple[Optional[Any], int, int]:
    """``(handle, drawn, visible)``: the top card's button named exactly
    ``name``, as a handle ONLY when exactly one is VISIBLE; ``drawn`` counts
    hidden ones too. A duplicate the page keeps for another width is drawn
    and not visible, so it is never the one taken, and two visible refuse."""
    named = topcard_of(page).get_by_role("button", name=name, exact=True, include_hidden=True)
    drawn = int(await named.count())
    shown = named.filter(visible=True)
    visible = int(await shown.count())
    if visible != 1:
        return None, drawn, visible
    return await shown.element_handle(), drawn, visible

#: The section words P F1, P H11, P K8, P D26 and P K1 ask about, counted in main.
PROFILE_SECTION_WORDS = ("Recommendations", "Services", "Top Voice", "Profile strength",
                         "Verifications")

#: P K1 (lane S's capture spec L.4): every control in main whose accessible
#: label mentions a verification -- the badge on his name, or a section's --
#: read by STRUCTURE, the label compared inside the page and never returned:
#: its tag, its role, whether it sits in the top card's heading, and where its
#: link (its own or its nearest anchor's) points, as a closed word.
_VERIFY_JS = """
() => Array.from(document.querySelectorAll("main [aria-label]"))
  .filter((e) => /verif/i.test(e.getAttribute("aria-label") || ""))
  .map((e) => {
    const a = e.closest("a") || e.querySelector("a");
    const h = (e.getAttribute("href") || (a && a.getAttribute("href")) || "");
    const kind = h === "" ? "none"
      : h.includes("/mypreferences/d/verifications") ? "mypreferences_verifications"
      : h.includes("/trust/verification") ? "trust_verification"
      : h.includes("/overlay/") ? "profile_overlay"
      : "other";
    return {
      tag: e.tagName.toLowerCase(),
      role: e.getAttribute("role"),
      in_heading: !!e.closest("h1, h2"),
      link: kind,
      haspopup: e.getAttribute("aria-haspopup"),
      expanded: e.hasAttribute("aria-expanded"),
    };
  })
"""

_LINK_KINDS = ("none", "mypreferences_verifications", "trust_verification", "profile_overlay", "other")


def verify_record(raw: Any) -> dict[str, Any]:
    """One verification control, reduced to closed words and booleans. PURE."""
    if not isinstance(raw, dict):
        return {"readable": False}
    tag, role, popup, link = raw.get("tag"), raw.get("role"), raw.get("haspopup"), raw.get("link")
    return {
        "tag": tag if tag in _TAGS + ("svg", "img", "li-icon") else "other",
        "role": role if role in _ROLES + ("img", "dialog") else ("none" if role is None else "other"),
        "in_heading": raw.get("in_heading") is True,
        "link": link if link in _LINK_KINDS else "other",
        "haspopup": popup if popup in _HASPOPUP_WORDS else ("none" if popup is None else "other"),
        "expanded": raw.get("expanded") is True,
    }

_EXPANDED_JS = """
() => Array.from(document.querySelectorAll("main [aria-expanded]")).map((e) => ({
  tag: e.tagName.toLowerCase(),
  type_button: e.getAttribute("type") === "button",
  href: e.hasAttribute("href"),
  haspopup: e.getAttribute("aria-haspopup"),
  svg: !!e.querySelector("svg"),
  more: e.getAttribute("aria-label") === "More",
}))
"""


def expanded_record(raw: Any) -> dict[str, Any]:
    """One main-scope [aria-expanded] control, by structure. PURE."""
    if not isinstance(raw, dict):
        return {"readable": False}
    popup = raw.get("haspopup")
    tag = raw.get("tag")
    return {
        "tag": tag if tag in _TAGS else "other",
        "type_button": raw.get("type_button") is True,
        "href": raw.get("href") is True,
        "haspopup": popup if popup in _HASPOPUP_WORDS else ("none" if popup is None else "other"),
        "svg": raw.get("svg") is True,
        "more": raw.get("more") is True,
    }


async def _in_me(capture: bool) -> dict[str, Any]:
    """His profile through the package's self-profile loader: once, and once
    more only when LinkedIn's self-assertion did not ride (never on false)."""
    async with BROWSER.session() as page:
        _profile, assertion, loads = await server._goto_self_profile_asserted(page)
        say("    self-assertion " + shape_of(assertion, "state") + " after " + str(loads) + " load(s)")
        if assertion != server.SELF_ASSERTION_TRUE:
            raise _Anomaly("self_assertion_not_true", "in_me")
        await _health(page, "in_me")
        census = [expanded_record(raw) for raw in (await page.evaluate(_EXPANDED_JS) or [])]
        sections = {word: int(await page.locator("main").get_by_text(word, exact=True).count())
                    for word in PROFILE_SECTION_WORDS}
        verifications = [verify_record(raw) for raw in (await page.evaluate(_VERIFY_JS) or [])]
        topcard: dict[str, list[int]] = {}
        for word in TOPCARD_WORDS:
            _handle, drawn, visible = await topcard_control(page, word)
            if _handle is not None:
                await _handle.dispose()
            topcard[word] = [drawn, visible]
        await _save_page(page, "in_me", capture)
    out = {"self_assertion": assertion, "loads": loads, "expanded": census,
           "more_triggers": sum(1 for row in census if row["more"]), "sections": sections,
           "verification_controls": verifications, "topcard_drawn_visible": topcard}
    say("    main [aria-expanded] " + str(len(census)) + "; labelled More " + str(out["more_triggers"])
        + "; section words " + shape_of(sections))
    say("    top card, drawn/visible: " + "; ".join(
        word + " " + str(topcard[word][0]) + "/" + str(topcard[word][1]) for word in TOPCARD_WORDS))
    by_link: dict[str, int] = {}
    for control in verifications:
        by_link[str(control.get("link"))] = by_link.get(str(control.get("link")), 0) + 1
    say("    P K1: controls labelled with a verification " + str(len(verifications))
        + "; by link " + shape_of(by_link))
    return out


async def _in_me_more(capture: bool) -> dict[str, Any]:
    """Lane D's LQ-1: the top card's More, opened TWICE on the page ``in_me``
    left open, read by attribute; the Save-to-PDF item's handle compared."""
    openings: list[dict[str, Any]] = []
    async with BROWSER.session() as page:
        on_his_profile = press.self_landing(page.url)
        if not on_his_profile:
            return {"stopped": "not_on_his_profile"}
        for _opening in range(2):
            handle, drawn, visible = await topcard_control(page, MORE_NAME)
            if handle is None:
                say("    More in the top card: " + str(drawn) + " drawn, " + str(visible)
                    + " visible. NOT EXACTLY ONE VISIBLE. Nothing pressed.")
                return {"stopped": "more_visible_" + str(visible) + "_drawn_" + str(drawn),
                        "openings": openings}
            openings.append(await press_and_read(page, "in_me_more", handle, capture,
                                                 needles=N76_NEEDLES))
            await handle.dispose()
    first = handle_signature(openings[0]["items"])
    second = handle_signature(openings[1]["items"])
    out = {"openings": openings, "save_to_pdf_handle_found": first is not None,
           "stable_across_openings": first is not None and first == second,
           "needle_items": [sum(1 for one in openings[0]["items"] if one["needles"][i])
                            for i in range(len(N76_NEEDLES))]}
    say("    Save to PDF handle found " + str(out["save_to_pdf_handle_found"])
        + "; stable across two openings " + str(out["stable_across_openings"])
        + "; items per N 76 needle " + str(out["needle_items"]))
    return out


async def _me_menu(capture: bool) -> dict[str, Any]:
    """Lane Y's item 9: the Me menu, opened once on the page left open."""
    async with BROWSER.session() as page:
        trigger = page.locator("header").get_by_role("button", name="Me", exact=True)
        handle, count = await _one_handle(trigger)
        if handle is None:
            say("    Me triggers matching: " + str(count) + ". NOT EXACTLY ONE. Nothing pressed.")
            return {"stopped": "me_trigger_count_" + str(count)}
        out = await press_and_read(page, "me_menu", handle, capture)
        await handle.dispose()
    return out


# ---------------------------------------------------------------------------
# Captures by address, and what each reads in the session.
# ---------------------------------------------------------------------------

_VOTES = re.compile(r"^\s*[0-9][0-9,]*\s+votes?\s*$", re.I)
_COMMENTS = re.compile(r"^\s*[0-9][0-9,]*\s+comments?\s*$", re.I)


async def _capture_readings(page: Any, key: str, items: dict[str, str]) -> dict[str, Any]:
    """The in-session readings each capture key's spec asks for. Counts only."""
    main = page.locator("main")
    if key == "activity_all":
        return {
            "activity_permalinks": int(await main.locator('a[href*="/feed/update/urn:li:activity:"]').count()),
            "poll_shaped_nodes": int(await main.locator('[class*="poll"]').count()),
            "votes_phrases": int(await main.get_by_text(_VOTES).count()),
        }
    if key == "own_post":
        return {
            "comment_items": int(await page.locator(
                '[class*="comments-comment-entity"], [class*="comments-comment-item"]').count()),
            "comments_phrases": int(await page.get_by_text(_COMMENTS).count()),
            "comments_list": int(await page.locator('[class*="comments-comments-list"]').count()),
        }
    if key == "event":
        target = 'a[href*="/events/' + items["event"] + '/attendees"]'
        drawn = int(await page.locator(target).count())
        return {"attendees_links": drawn, "attendees_link_drawn": drawn > 0,
                "event_shape": value_shape(items["event"], _shape_key())}
    return {"anchors": await l1._anchors_reading(page)}


async def _capture_key(key: str, items: dict[str, str], capture: bool) -> dict[str, Any]:
    url = address_for(key, items)
    if url is None:
        say("    THE PACKAGE'S COMPOSER REFUSED THE ITEM. Nothing loaded.")
        return {"stopped": "not_composed"}
    if not readonly.is_read_url(url):
        say("    REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return {"stopped": "address_not_admitted"}
    async with BROWSER.session() as page:
        landed = await BROWSER.goto(page, url)
        relation = l1._relation(landed, url)
        say("    relation: " + shape_of(relation, "relation"))
        await _health(page, key)
        readings = await _capture_readings(page, key, items)
        await _save_page(page, key, capture)
    say("    readings: " + shape_of(readings))
    return {"relation": relation, **readings}


# ---------------------------------------------------------------------------
# Tools, as a caller would call them; and the page each leaves open.
# ---------------------------------------------------------------------------


async def _tool(key: str, items: dict[str, str]) -> dict[str, Any]:
    """The shipped tool for ``key``. Arguments are constants or the caller's
    items; nothing is read off a page to make one."""
    if key == "m43":
        return await server.linkedin_list_conversations()
    if key == "m33":
        return await server.linkedin_open_messaging(message_filter="inmail")
    if key == "m49":
        return await server.linkedin_open_messaging()
    if key == "j18":
        return await server.linkedin_recent_job_searches()
    if key == "j39":
        return await server.linkedin_premium_job_collection(collection=2)
    if key == "j158":
        return await server.linkedin_premium_job_collection(collection=1)
    if key == "n132":
        return await server.linkedin_search_appearances()
    if key == "notifications":
        return await server.linkedin_notifications()
    if key == "n23":
        return await server.linkedin_connections()
    if key == "job_detail":
        return await server.linkedin_job_detail(job_id=items["posting"])
    if key == "n94":
        # A KEYWORD SEARCH WITH NAMES: N 94's two locations, and N 79 -- a person
        # found by keyword -- off the same load (the orchestrator's go order).
        return await server.linkedin_people_search_shape(
            keywords=N94_KEYWORDS, location_ids=N94_GEOS, include_names=True)
    if key == "n84":
        return await server.linkedin_people_search_shape(
            current_company_ids=items["org"], include_names=True)
    if key == "n87":
        return await server.linkedin_people_search_shape(
            past_company_ids=items["past_org"], include_names=True)
    if key == "presence":
        return await server.linkedin_messaging_presence()
    if key == "recruiter":
        return await server.linkedin_recruiter_insights()
    if key == "j107":
        # J 107: every posting at ONE employer -- the employer the caller named,
        # standing in for the keyword. A jobs search, not one of D1's five.
        return await server.linkedin_search_jobs(keywords="", company_id=items["org"])
    if key == "memberships":
        return await server.linkedin_group_memberships()
    if key == "group_home":
        return await server.linkedin_group_page(group_id=items["group"])
    if key == "thread":
        return await server.linkedin_open_thread(thread_id=items["thread"])
    raise ValueError("no tool for key " + key)


#: The star's labels, compared inside the page (lane L5's C10).
STAR_LABELS = ("Star conversation", "Unstar conversation")


# ---------------------------------------------------------------------------
# The operator's named live targets: matched IN THIS PROCESS, never printed.
# ---------------------------------------------------------------------------

#: The identity key's class holding the people he named for live proofs. The
#: words live ONLY in the gitignored key; here they are read, compared and
#: counted, and nothing of them leaves this process but an index and a count.
TARGET_CLASS = "operator_named_live_targets"


def _key_data() -> dict[str, Any]:
    """The gitignored identity key, found from a worktree the way the identity
    sweep finds it. Empty when absent: then every count below is None."""
    from tests.repo_paths import sanitisation_key_path

    loaded = _json_or_none(sanitisation_key_path(_ROOT))
    return loaded if isinstance(loaded, dict) else {}


def name_tokens(text: Any) -> list[str]:
    """A name as its words: NFKC, casefolded, split on anything not a letter.
    PURE."""
    import unicodedata

    folded = unicodedata.normalize("NFKC", str(text or "")).casefold()
    return [w for w in re.split(r"[^\w]+|[\d_]+", folded) if w]


def person_matches(name: Any, first: str, surnames: Any = ()) -> bool:
    """Does a drawn name carry ``first`` as a whole word -- and, when surnames
    are given, one of them too? PURE. Whole words only: a first name inside a
    longer word is not that name."""
    tokens = name_tokens(name)
    if not first or first.casefold() not in tokens:
        return False
    wanted = [s.casefold() for s in surnames if s]
    return not wanted or any(s in tokens for s in wanted)


def family_names(key: dict[str, Any]) -> list[str]:
    """The last word of each multi-word spelling of the operator's own name, of
    three letters or more: the family name a relative's drawn name carries.
    PURE. Read from the key, never written anywhere."""
    out: list[str] = []
    for value in key.get("operator") or []:
        words = str(value).split()
        if len(words) >= 2 and len(words[-1]) >= 3 and words[-1].casefold() not in out:
            out.append(words[-1].casefold())
    return out


def names_in(envelope: Any) -> list[str]:
    """Every string under a ``name`` key anywhere in an envelope. PURE. What a
    people record calls the person; read here only to be counted."""
    found: list[str] = []
    stack = [envelope]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            for field, inner in node.items():
                if field == "name" and isinstance(inner, str):
                    found.append(inner)
                else:
                    stack.append(inner)
        elif isinstance(node, (list, tuple)):
            stack.extend(node)
    return found


def named_target_counts(names: list[str], words: list[str]) -> dict[str, int]:
    """For each word of the key's class, by its 1-based INDEX, how many drawn
    names carry it as a whole word. PURE. Indices and counts only."""
    return {"T" + str(i): sum(1 for n in names if person_matches(n, w))
            for i, w in enumerate(words, 1)}


async def _left_open(key: str, capture: bool, envelope: dict[str, Any]) -> dict[str, Any]:
    """Health, readings and a skeleton, on the page the tool left open."""
    extra: dict[str, Any] = {}
    async with BROWSER.session() as page:
        await _health(page, key)
        if key == "thread":
            star = page.locator("main button.msg-thread__star-icon")
            extra["star_controls"] = int(await star.count())
            extra["star_pressed"] = [int(await star.and_(page.locator('[aria-pressed="' + v + '"]')).count())
                                     for v in ("true", "false")]
            extra["star_labels"] = [int(await star.and_(page.locator('[aria-label="' + v + '"]')).count())
                                    for v in STAR_LABELS]
        if key == "m43":
            extra["c1_unread_rows_drawn"] = int(envelope.get("unread_rendered") or 0)
        await _save_page(page, key, capture)
    return extra


async def _run_tool(key: str, items: dict[str, str], capture: bool) -> dict[str, Any]:
    out = await _tool(key, items)
    if not isinstance(out, dict):
        raise _Anomaly("non_dict_envelope", key)
    if out.get("error"):
        say("    ERROR ENVELOPE: " + shape_of(out.get("error")))
        raise _Anomaly("error_envelope", key)
    _print_envelope(out)
    extra = await _left_open(key, capture, out)
    if key == "n23":
        # THE NAMED TARGETS AMONG HIS CONNECTIONS, COUNTED (the order of
        # 2026-09-28 08:04, for session 3): by the key word's index, never by
        # the word; read-only, no outward act.
        words = [str(w) for w in (_key_data().get(TARGET_CLASS) or [])]
        extra["named_target_counts"] = named_target_counts(names_in(out), words) if words else None
        say("    named targets among the connections drawn, by key index: "
            + shape_of(extra["named_target_counts"]))
    if key == "notifications":
        extra["kinds"] = s1.notification_kinds(out.get("results") or [])
        say("    kinds: " + shape_of(extra["kinds"]))
    if key == "job_detail":
        # D-4, THE ORCHESTRATOR'S CALL: an organisation id is shown to him BY
        # NAME before any search or roster fires on it. So the ORGANISATION --
        # its name and resolved id, never a person -- is written beside the
        # reduced envelope, gitignored, for the lead to read and send; nothing
        # of it is printed here.
        resolved = out.get("company_id") if isinstance(out.get("company_id"), dict) else {}
        _write("job_detail", ".org.json", json.dumps({
            "company": out.get("company"), "company_id": resolved.get("company_id"),
        }, indent=2))
        say("    the organisation, by name and id, written for D-4 under _state/ (gitignored)")
    reduced = KEYS[key].get("envelope") == "reduced"
    written = reduce_envelope(out, _shape_key()) if reduced else out
    _write(key, ".json", json.dumps({"envelope": written, **extra}, indent=2, default=str))
    say("    envelope written under _state/ (gitignored), " + ("reduced" if reduced else "raw"))
    return {"returned": True, **extra}


# ---------------------------------------------------------------------------
# compose_presses -- lane L5's C8, C9 and C5 on the composer, one load at most.
# ---------------------------------------------------------------------------

#: C8's trigger: the folder pill reading Focused, closed.
FOLDER_TRIGGER = 'main [data-test-messaging-inbox-filters__folder-pill][aria-expanded="false"]'
#: C9's trigger, inside ONE READ row.
ROW_OPTIONS = 'button.msg-thread-actions__control[aria-expanded="false"]'
#: C5's trigger, inside the composer's own form.
GIF_TRIGGER_LABEL = "Open GIF Keyboard"


def first_read_row(listing: Any) -> Optional[int]:
    """The 1-based position of the first RENDERED row the list reader reads
    as READ, or None. PURE. A placeholder or an unread row is never chosen."""
    for row in (listing or {}).get("rows") or []:
        if row.get("rendered") is True and row.get("unread") is False:
            position = row.get("position")
            return position if isinstance(position, int) and position >= 1 else None
    return None


async def _compose_presses(capture: bool) -> dict[str, Any]:
    """The composer draws the list and opens no conversation (lane L5, 1.2).
    Rides on the page ``m43`` left open when it is still the composer;
    otherwise loads it once."""
    results: dict[str, Any] = {}
    async with BROWSER.session() as page:
        on_compose = threads.is_the_compose_address(page.url)
        if not on_compose:
            await BROWSER.goto(page, COMPOSE_URL)
        await _health(page, "compose_presses")

        folder = page.locator(FOLDER_TRIGGER).filter(has_text="Focused")
        handle, count = await _one_handle(folder)
        if handle is None:
            return {"stopped": "c8_trigger_count_" + str(count), **results}
        results["c8"] = await press_and_read(page, "compose_c8", handle, capture, messaging=True)
        await handle.dispose()

        listing = await threads.read_conversation_list(page)
        position = first_read_row(listing)
        if position is None:
            return {"stopped": "c9_no_read_row", **results}
        row = page.locator(threads.ROW_SELECTOR).nth(position - 1)
        await row.hover(timeout=5_000)
        handle, count = await _one_handle(row.locator(ROW_OPTIONS))
        if handle is None:
            return {"stopped": "c9_trigger_count_" + str(count), **results}
        results["c9"] = await press_and_read(page, "compose_c9", handle, capture, messaging=True)
        await handle.dispose()

        gif = page.locator("main form.msg-form").get_by_role("button", name=GIF_TRIGGER_LABEL, exact=True)
        handle, count = await _one_handle(gif)
        if handle is None:
            return {"stopped": "c5_trigger_count_" + str(count), **results}
        results["c5"] = await press_and_read(page, "compose_c5", handle, capture, messaging=True)
        await handle.dispose()
    return results


# ---------------------------------------------------------------------------
# One key, and main.
# ---------------------------------------------------------------------------


def _veto_for(key: str, items: dict[str, str]) -> Optional[str]:
    """The page's veto for ``key``, from this lane's own readings on disk."""
    if key in GROUP_VETOED:
        return veto_group(items["group"], _envelope_of(STATE / "memberships.json"))
    if key == "own_post":
        return veto_activity(items["activity"], _json_or_none(LIVE1_ACTIVITY))
    if key == "event_attendees":
        return veto_attendees(items["event"], _json_or_none(STATE / "event.json"), _shape_key())
    return None


async def fire(key: str, items: dict[str, str], capture: bool) -> dict[str, Any]:
    """One key. Returns its result; raises _Anomaly to stop the session."""
    refused = _veto_for(key, items)
    if refused is not None:
        say("    VETOED: " + refused + ". Nothing loaded.")
        return {"stopped": "vetoed"}
    kind = KEYS[key]["kind"]
    if kind == "setting":
        return await _setting(capture)
    if kind == "tool":
        return await _run_tool(key, items, capture)
    if kind == "in_me":
        result = await _in_me(capture)
    elif kind == "in_me_more":
        result = await _in_me_more(capture)
    elif kind == "me_menu":
        result = await _me_menu(capture)
    elif kind == "compose":
        result = await _compose_presses(capture)
    else:
        result = await _capture_key(key, items, capture)
    _write(key, ".json", json.dumps(result, indent=2))
    return result


async def _run_keys(keys: list[str], items: dict[str, str], capture: bool) -> int:
    loads = _ledger_read()["loads"]
    say("### keys: " + ", ".join(keys) + "   capture " + str(capture))
    say("### ledger before this run: " + str(len(loads)) + " of " + str(CEILING)
        + "; searches " + str(searches_spent(loads)) + " of " + str(SEARCH_CAP))
    _install_counter()
    outcomes: dict[str, str] = {}
    try:
        for key in keys:
            _CURRENT["key"] = key
            say("")
            say("=" * 70)
            say("KEY " + key + "   rows: " + KEYS[key]["rows"])
            say("=" * 70)
            result = await fire(key, items, capture)
            if result.get("stopped"):
                outcomes[key] = "STOPPED " + str(result["stopped"])
                say("    STOPPED: " + str(result["stopped"]) + " -- no further key this run.")
                return 1
            outcomes[key] = "RETURNED"
    except (_Anomaly, _LedgerRefusal) as stop:
        outcomes[_CURRENT["key"]] = "ANOMALY " + type(stop).__name__
        say("    STOPPED: " + type(stop).__name__ + " -- every further load is stopped.")
        return 1
    except Exception as exc:  # noqa: BLE001 - the TYPE only, never the message
        outcomes[_CURRENT["key"]] = "ABORTED " + type(exc).__name__
        say("    RUN ABORTED: " + type(exc).__name__)
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
        spent = _ledger_read()["loads"]
        say("")
        say("### OUTCOMES " + json.dumps(outcomes, sort_keys=True))
        say("### ledger after this run: " + str(len(spent)) + " of " + str(CEILING)
            + "; searches " + str(searches_spent(spent)) + " of " + str(SEARCH_CAP))
    return 0


async def main_async(argv: list[str]) -> int:
    if "--attach-child" in argv:
        return await _attach_child()
    if "--export-fixtures" in argv:
        for name, size in export_fixtures().items():
            say("    tracked copy " + name + ": " + str(size) + " characters")
        return 0
    items = parse_items(argv)
    keys = selected(argv, items)
    capture = "--no-capture" not in argv
    if keys == ["setting_offline"]:
        offline = await _setting_offline()
        return 0 if offline.get("verdict") == "AGREES" else 1
    refusal = _environment_refusal()
    if refusal:
        say("REFUSED: " + refusal)
        return 2
    loads = _ledger_read()["loads"]
    over = budget_verdict(loads, sum(int(KEYS[k]["loads"]) for k in keys))
    over = over or search_verdict(loads, sum(int(KEYS[k].get("searches", 0)) for k in keys))
    if over:
        say("REFUSED BEFORE ANY LOAD: " + over)
        return 2
    held = _take_driver_lock()
    if held:
        say("REFUSED: " + held + ".")
        return 2
    try:
        if keys == ["attach_check"]:
            checked = _attach_check()
            return 0 if checked.get("verdict") == "PASS" else 1
        return await _run_keys(keys, items, capture)
    finally:
        _release_driver_lock()


def main() -> int:
    return asyncio.run(main_async(sys.argv[1:]))


if __name__ == "__main__":
    raise SystemExit(main())
