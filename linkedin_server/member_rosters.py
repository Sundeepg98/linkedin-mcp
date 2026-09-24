"""Compose ONE page of a member roster from a tool's arguments -- and open none.

## WHAT DECIDED IT

``MEMBER-ROSTERS-AS-BOUNDED-READS`` (the orchestrator's delegated call,
2026-09-24, ``_audit/2026-09-24-rulings-search-verticals-rosters-passive-
costs.md``) decided the question a 2026-09-05 refusal recorded in
``readonly.py`` and census cells but never registered: a roster the operator
can open himself -- a group's members, an event's attendees, a company's or a
school's People tab -- is read as a BOUNDED READ, under five conditions:

1. one page per call, with no automatic pagination;
2. the group, event, company or school id comes from the tool's arguments only;
3. no member's name or id is stored in a tracked file;
4. the read stays inside the live-session budget;
5. the rows it held become GAP, blocked on an admission and a reader.

The admission is the four roster entries at the end of
``readonly._ALLOWED_URL_PATTERNS``. This module is conditions 1, 2 and 4 in
code, and it is the ONLY place this package assembles a roster address.

## WHY NOTHING IN THE PACKAGE CALLS THIS YET

READERS HERE ARE BUILT AGAINST CAPTURES ONLY, and no roster page has ever been
captured. So this is the address half of each row -- the exact page a capture
must load, composed by the code the reader will later be handed. Nothing in the
package imports this module; ``tests/test_every_orphan_module_is_ruled.py``
records that as a ruling, and the first tool that imports it lands with its
reader, built against a capture, in the same commit.

A roster is a list of PEOPLE, and this server does not publish names (the
name-free shaper doctrine, ``_audit/2026-09-05-lead-rulings-round-two.md``).
Whatever reader lands owes that doctrine a shaper; which rows a count can
deliver is decided row by row in ``_audit/2026-09-24-lane-s-people-search.md``,
Follow-up section D.

## THE CONDITIONS, AS THIS FILE CARRIES THEM

**ONE PAGE PER CALL.** :func:`compose` returns exactly one address, takes no
page, offset or count argument, and the roster entries admit no query string
-- so a second page spelled ``?page=2`` or ``?start=25`` is refused by the read
boundary before any browser sees it. LinkedIn serves a roster's further rows
by scrolling or by a "show more" control, and neither is done here or anywhere
(``SCROLL-NOT-SANCTIONED``). :data:`LOADS_PER_CALL` is 1, and the tests hold
this module to containing no loop, no await and no navigation at all.

**THE ID FROM THE TOOL'S ARGUMENTS ONLY.** :func:`compose` takes the id as its
argument and nothing else; it reads no page. A group id goes through
``group_page.group_page_url`` and an organisation id through
``company_page.company_identifier`` -- the validators those surfaces' own tools
use, called rather than copied -- and an event or school id through the same
rule: the TEN ASCII DIGITS, at most twenty. A slug is refused, because a slug is
a name; the refusal describes the value's SHAPE and never quotes it.

**NOTHING STORED.** This module writes nothing anywhere -- no file, no store,
no log line carrying a value -- and the tests hold it to that on its AST.

**INSIDE THE LIVE BUDGET.** One call is one page load, so every roster read a
live session makes is counted against ``LIVE-BUDGET-40-LOADS`` like any other
load; the capture specs price each one.

## THE ASYMMETRY WITH THE BOUNDARY, IN THE SAFE DIRECTION

The company and school People-tab entries admit a slug as well as a number,
for the reason the ``/company/`` root entry gives: LinkedIn draws the People
tab by its slug (measured on two captures) and serves an organisation's
numeric address by redirecting to it. This module ASSEMBLES ONLY THE NUMERIC
FORM -- the boundary admits what the product serves; the package builds only
what names nobody.
"""

from __future__ import annotations

from typing import Any

from linkedin_server import company_page, group_page, jobfilter

#: ``roster -> (path word, tab word, census rows)``. The rows are the ones
#: ``MEMBER-ROSTERS-AS-BOUNDED-READS`` names, placed by the page each row's
#: own words ask for; ``J 112`` and ``N 100`` share the school tab with ``N 99``
#: and are listed there.
ROSTERS: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "group_members": ("groups", "members", ("N 165", "N 177")),
    "event_attendees": ("events", "attendees", ("N 188", "N 189")),
    "company_people": ("company", "people", ("J 108", "N 102")),
    "school_people": ("school", "people", ("N 99", "N 100", "J 112")),
}

#: One call, one page load. The number the live budget is counted in.
LOADS_PER_CALL = 1

#: The ten ASCII digits, written out: ``str.isdigit()`` is true of several
#: other scripts' digits and ``\\d`` of every Unicode decimal digit, and the
#: read allowlist spells its digit segments ``[0-9]`` for that reason.
_ASCII_DIGITS = frozenset("0123456789")

#: The bound every numeric segment in this package is held to -- the groups
#: and organisation validators' own number, taken rather than restated.
MAX_ID_DIGITS = company_page.MAX_IDENTIFIER_DIGITS

_SCHEME_HOST = "https://www.linkedin.com"


def _refused(refused: str, value: str, why: str) -> dict[str, Any]:
    return {
        "built": False,
        "argument": "identifier",
        "refused": refused,
        "saw": jobfilter.describe_shape(value),
        "why": why,
    }


def _digits(text: str, what: str) -> dict[str, Any]:
    """``{"ok": True, "value": text}`` or a refusal, for an event or school id."""
    if not text:
        return _refused(
            "no_identifier", text,
            f"{what} cannot be addressed by an empty value, and this gate "
            "refuses what it cannot establish.",
        )
    if not set(text) <= _ASCII_DIGITS:
        return _refused(
            "identifier_is_not_numeric", text,
            f"{what} must be LinkedIn's NUMERIC id: the TEN ASCII DIGITS, at "
            "most twenty. Anything else is a SLUG, and a slug is a name -- an "
            "event's slug is its title, and a title can carry a person's "
            "name. The value is described, never quoted.",
        )
    if len(text) > MAX_ID_DIGITS:
        return _refused(
            "identifier_too_long", text,
            f"a digit run longer than {MAX_ID_DIGITS} characters is not a "
            "LinkedIn id, and an unbounded run on caller-shaped input is a "
            "cost nobody chose.",
        )
    return {"ok": True, "value": text}


def compose(roster: Any, identifier: Any) -> dict[str, Any]:
    """ONE page of one roster, or a refusal.

    Returns one of::

        {"built": True,  "url": <address>, "roster": <name>,
         "loads": 1, "rows": [<census row>, ...]}
        {"built": False, "argument": "roster" | "identifier",
         "refused": <literal>, "saw": <shape>, "why": <sentence>}

    ``url`` is the only field that carries the caller's value, and it exists to
    be handed to ``BROWSER.goto`` by the reader that does not exist yet.

    PURE: arguments in, a dict out. It reads no page, no file, no clock and no
    network, and it never raises.
    """
    name = str(roster or "").strip()
    if name not in ROSTERS:
        return {
            "built": False,
            "argument": "roster",
            "refused": "not_a_roster",
            "saw": jobfilter.describe_shape(name),
            "why": (
                "the rosters composed here are exactly "
                + ", ".join(sorted(ROSTERS))
                + " -- the four MEMBER-ROSTERS-AS-BOUNDED-READS names."
            ),
        }
    path_word, tab_word, rows = ROSTERS[name]
    text = str(identifier or "").strip()

    if name == "group_members":
        built = group_page.group_page_url(text)
        if not built.get("built"):
            return _refused(
                str(built.get("refused") or "identifier_refused"), text,
                str(built.get("why") or "not a numeric group id"),
            )
        value = str(built["identifier"])
    elif name == "company_people":
        verdict = company_page.company_identifier(text)
        if not verdict.get("identified"):
            return _refused(
                str(verdict.get("refused") or "identifier_refused"), text,
                str(verdict.get("why") or "not a numeric organisation id"),
            )
        value = str(verdict["identifier"])
    else:
        what = "an event" if name == "event_attendees" else "a school"
        verdict = _digits(text, what)
        if not verdict.get("ok"):
            return verdict
        value = verdict["value"]

    return {
        "built": True,
        "url": f"{_SCHEME_HOST}/{path_word}/{value}/{tab_word}/",
        "roster": name,
        "loads": LOADS_PER_CALL,
        "rows": list(rows),
    }
