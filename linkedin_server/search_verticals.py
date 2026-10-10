"""Compose a COMPANIES, GROUPS or EVENTS search from a tool's arguments -- and
open none of them.

## WHAT DECIDED IT

``D2-SEARCH-VERTICALS-WIDENED`` (the orchestrator's delegated call,
2026-09-24, ``_audit/2026-09-24-rulings-search-verticals-rosters-passive-
costs.md``) widened the search admission from the people vertical to four
CLOSED words, ``/search/results/(people|companies|groups|events)/``, and
carried ``D1-SEARCH-AS-READS``'s three conditions to every vertical: values
come from the tool's arguments and never from page content; no test search
uses a value that identifies the operator; a live session makes at most five
test searches. It serves ``N 104`` (companies), ``N 161`` and ``M C70``
(groups) and ``N 179`` (events), and says of them: "Each then needs a reader."

The people vertical is ``people_search.py``'s, and this module does not
compose it.

## WHO CALLS THIS, SINCE 2026-10-10

The live lane captured a groups and an events results page (sessions 2 and
3), and lane B2 built their reader over those captures,
``search_vertical_results``, and the two tools that open them,
``server.linkedin_search_groups`` (``N 161``) and
``server.linkedin_search_events`` (``N 179``) -- reader and tools in ONE
commit, as the condition below requires, with the orphan ruling deleted in it.
The companies word is still opened by nothing: no companies page has been
captured. What follows was written while nothing called this module, and
still holds for that word.

## WHY NOTHING IN THE PACKAGE CALLED THIS UNTIL THEN

READERS HERE ARE BUILT AGAINST CAPTURES ONLY, AND NONE OF THESE THREE PAGES
HAD BEEN CAPTURED. So this is the ADDRESS half of each row and nothing more:
the exact page a capture must load, composed by the code the reader will
later be handed, so that the capture and the reader can never disagree about
which address they meant.

The search admission's CONDITION 1 is the other reason, and it binds:
*"ADMISSION AND A NAME-FREE SHAPER LAND IN THE SAME COMMIT, OR NEITHER
LANDS"* (``_audit/2026-09-19-two-census-conventions-ruled.md`` section 6).
``NAMES-AT-RUNTIME`` (registered 2026-09-24) amended condition 1 for what a
read RETURNS at runtime: a reader may return the items it finds -- a group or
an event as its title and its link -- held to ``PEOPLE-DATA-MITIGATIONS``. What
still binds is the pairing. The admission landed; what the condition protects
-- nothing a results page shows leaving this server except through that
reader, shaped to the declared fields -- is held by the absence of any route:
no module in the package imports this one, and
``tests/test_every_orphan_module_is_ruled.py`` records that as a ruling rather
than an accident. **The first tool that imports this module lands with its
reader in the same commit**, held to the six mitigations, and that entry is
deleted then.

## THE SAME KEYWORD RULES AS THE PEOPLE SEARCH, BY THE SAME CODE

A keyword is validated by ``people_search.validated_keywords`` -- the function
``people_search.compose`` calls -- so the length budget, the control-character
refusal and the refusal's shape cannot drift between the four verticals. It is
sent under the same key, ``keywords``, in the same encoding (``urlencode``,
space written ``+``), with no ``origin``: exactly the composition
``people_search.compose`` performs for a keyword and nothing else.

**NO FACET IS TAKEN.** The people facets are LinkedIn-written spellings read
off captures; no capture of these three verticals exists, so no facet of theirs
is on record, and a facet guessed here would be a spelling nobody measured.
The four rows need a keyword and nothing more: finding a Page, a group or an
event BY SEARCHING is the keyword search itself, and ``N 179``'s "filter
results to the Events tab" IS the vertical.

**A KEYWORD IS REQUIRED**, unlike the people search, whose bare address is what
``linkedin_people_search_shape`` opened before it took arguments. None of the
four rows asks for a vertical with no query in it, and that page is an address
nobody has captured either.

## IT TOUCHES NO PAGE

No function here takes a page, imports the browser or ``dom``, or navigates.
:func:`compose` is a pure function of its arguments, so nothing a page drew
can reach the address it returns. ``tests/test_d2_search_verticals.py`` asserts
that on the module's AST, and the repository's navigation-derivation guard
(``tests/test_navigation_is_never_derived.py``) scans this file like every
other in the package.

NOTHING COMES BACK BUT THE ADDRESS. A refusal describes the SHAPE of a
rejected value with ``jobfilter.describe_shape`` (through
``people_search``) and never quotes it.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from linkedin_server import jobfilter, people_search

#: The three words ``D2-SEARCH-VERTICALS-WIDENED`` added, in the ruling's
#: order. The fourth word, ``people``, is ``people_search.py``'s.
VERTICALS: tuple[str, ...] = ("companies", "groups", "events")

#: The census rows the RULING NAMES for each word -- not the rows each word's
#: page delivers, which is a different claim. ``M C70`` is the case that
#: separates them: D2 names it among the groups rows, and its own census cell
#: says a groups search lists GROUPS while the row asks for content WITHIN
#: them. Renamed from ``ROWS_SERVED`` on 2026-09-24 for that reason. Read by
#: the tests, never by a page.
ROWS_NAMED_BY_THE_RULING: dict[str, tuple[str, ...]] = {
    "companies": ("N 104",),
    "groups": ("N 161", "M C70"),
    "events": ("N 179",),
}

#: Every address this module composes starts here, and continues with one of
#: :data:`VERTICALS` and a slash -- the spelling the admission's closed
#: alternation matches.
_RESULTS_ROOT = "https://www.linkedin.com/search/results/"


def compose(vertical: Any, *, keywords: Any = "") -> dict[str, Any]:
    """The search address for one vertical and a keyword, or a refusal.

    Returns one of::

        {"built": True,  "url": <address>, "vertical": <word>,
         "applied": {"keywords": 1}}
        {"built": False, "argument": <name>, "refused": <literal>,
         "saw": <shape>, "why": <sentence>}

    ``url`` is the ONLY field that carries a caller's value, and it exists to
    be handed to ``BROWSER.goto`` by the reader that does not exist yet.
    ``vertical`` is one of this module's own three words.

    PURE: arguments in, a dict out. It reads no page, no file, no clock and
    no network, and it never raises.
    """
    word = str(vertical or "").strip()
    if word not in VERTICALS:
        why = (
            "the search verticals composed here are exactly "
            + ", ".join(VERTICALS)
            + " -- the three words D2-SEARCH-VERTICALS-WIDENED added. "
        )
        if word == "people":
            why += "The people vertical is people_search.compose's."
        else:
            why += "Any other vertical is refused by the read boundary."
        return {
            "built": False,
            "argument": "vertical",
            "refused": "not_a_d2_vertical",
            "saw": jobfilter.describe_shape(word),
            "why": why,
        }
    checked = people_search.validated_keywords(keywords)
    if not checked.get("ok"):
        return checked
    text = checked["text"]
    if not text:
        return {
            "built": False,
            "argument": "keywords",
            "refused": "keywords_required",
            "saw": jobfilter.describe_shape(text),
            "why": (
                "a companies, groups or events search is composed only WITH "
                "a keyword: every row it serves is a search by keyword, and "
                "the bare vertical page is an address nobody has captured."
            ),
        }
    url = (
        _RESULTS_ROOT
        + word
        + "/?"
        + urlencode([(people_search.KEYWORDS_KEY, text)])
    )
    return {
        "built": True,
        "url": url,
        "vertical": word,
        "applied": {"keywords": 1},
    }
