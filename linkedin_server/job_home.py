"""The jobs home's RECENT SEARCHES list: his own queries, re-runnable, and which carry an alert.

Census ``J 18`` -- *recent searches: view and re-run*. It sat GAP on an
address nobody had seen served (``/jobs/search-history/``, refused), while the
list itself was being drawn on a page this server has been allowed to open
since 2026-09-20: the JOBS HOME, ``/jobs/jam/``, which is where
``/jobs/alerts/`` lands (``_audit/2026-09-20-the-live-capture.md`` 12.1).

## WHAT THE PAGE DRAWS, MEASURED ON THE LIVE CAPTURE OF THAT LANDING

One list in ``main``, six entries, every entry an ``<a>`` whose href is the
SEMANTIC-SEARCH route ``/jobs/search-results/`` carrying the query it would
re-run and the tag ``origin=SEMANTIC_SEARCH_HISTORY``. Inside each anchor two
spans: the query as rendered, and a subtitle joining up to three tokens with a
middle dot -- an ``Alert On`` badge, the PLACE, and workplace or network
words. Three of the six carried the alert badge. The page also draws a list
of top-applicant postings under the SAME element id, which is why nothing here
selects by id: the entries are recognised by their ROUTE and their ORIGIN TAG,
both LinkedIn's own and neither a label.

## WHAT CROSSES THE BOUNDARY, AND THE PRECEDENT FOR EACH STRING

Integers, booleans, literals of this module, and exactly TWO page-derived
strings -- both of them HIS OWN SEARCH INPUTS, echoed back by LinkedIn:

    search_keywords   taken from the href's query by the SHIPPED
                      ``shape.notification_handles``, the same function that
                      already publishes a job alert's keywords off his
                      notifications (``tests/test_notification_handles.py``),
                      for the same reason: "a keyword a caller can pass
                      straight to linkedin_search_jobs".
    location          the one subtitle token that is not a badge, the place
                      he searched in. ``linkedin_search_jobs`` already
                      publishes a place on every row it returns, and takes one
                      as ``location``; that is the whole of the re-run.

Neither is a person. **Nothing else of the page leaves**: not the rendered
title (the href's query is the canonical copy), not the place id or the
salary band the href carries (a salary band is his pay expectation and the
re-run does not need it -- the FILTER'S PRESENCE is published, never its
value), not the href itself. A query that names nothing here cannot make this
reader emit a name, because a name has no field to arrive in.

**A PLACE THAT CANNOT BE ISOLATED IS NOT GUESSED.** The subtitle is tokens
joined by a dot, and the place is whatever is not a badge. Exactly one such
token reads; none reads ``absent``; two or more reads ``ambiguous`` with no
string at all -- joining them would publish a string the page never drew as
one thing.

## A ZERO IS ONLY READABLE BESIDE ``list_label_seen``

    entries 0, list_label_seen True    -> he has no recent searches (or has
                                          cleared them). A fact about him.
    entries 0, list_label_seen False   -> THIS READER COULD NOT SEE, with
                                          ``refusal``. Never an empty list.

## IT NAVIGATES NOTHING AND PRESSES NOTHING

It reads the document it is handed; the tool owns the address and the boundary
check. The entries sit in the DOM whether or not LinkedIn has collapsed them
behind its show-more control, so nothing is pressed to reach them. It never
follows an entry's href: the route it points at, ``/jobs/search-results/``, is
REFUSED by the read boundary, and the re-run goes through
``linkedin_search_jobs``, which builds its own address from the keywords.
"""
from __future__ import annotations

from typing import Any, Optional
from urllib.parse import parse_qs, urlsplit

from linkedin_server import shape

#: The jobs home. ``/jobs/alerts/`` redirects here (live-capture 12.1), and it
#: is on the read allowlist with no sub-path and no query.
HOME_URL = "https://www.linkedin.com/jobs/jam/"

#: The route every recent-search entry points at. It is REFUSED by the read
#: boundary and nothing here navigates to it; it is only how an entry is
#: recognised.
SEARCH_ROUTE = "/jobs/search-results/"

#: LinkedIn's own tag for an entry that came from his search HISTORY, carried
#: in the entry's query. The discriminator that keeps a search link elsewhere
#: on the page from being counted as one of his searches.
HISTORY_ORIGIN = "SEMANTIC_SEARCH_HISTORY"

#: The list's accessible name as LinkedIn draws it -- a CONTROL NEEDLE only:
#: whether it is drawn separates "he has none" from "I could not see".
RECENT_LIST_LABEL = "Recent job searches"

#: The badge that marks a search carrying a job alert. Authored here, matched
#: case-blind as a WHOLE subtitle token, never returned as text.
ALERT_BADGE = "alert on"

#: The network badge. Removed from the place tokens; the fact itself is read
#: from the href's ``f_JIYN`` key, which is structural.
NETWORK_BADGE = "in your network"

#: Workplace words that share the subtitle with the place. Measured: Remote.
#: Published as the literal matched, which is what ``linkedin_search_jobs``'
#: ``remote`` parameter speaks.
WORKPLACE_WORDS: tuple[str, ...] = ("remote", "hybrid", "on-site")

#: The query keys an entry may carry that name a FILTER. Their PRESENCE is
#: published as these literals; their values never are.
FACETS: tuple[str, ...] = (
    "distance", "f_AL", "f_C", "f_E", "f_EA", "f_FCE", "f_JIYN", "f_JT",
    "f_SAL", "f_TPR", "f_WT",
)

#: ``location_state`` literals.
LOCATION_STATES: tuple[str, ...] = ("read", "absent", "ambiguous")

#: Refusals, each a literal.
REFUSALS: tuple[str, ...] = ("no_recent_search_list_drawn",)

#: A bound on how many anchors are examined. The page draws six; this is a
#: cost ceiling, not a measured LinkedIn limit.
MAX_ANCHORS = 60

#: Characters kept of either published string.
MAX_KEYWORDS_CHARS = 120
MAX_LOCATION_CHARS = 80

_ANCHORS = "main a[href*='/jobs/search-results']"


def emitted_alphabet() -> frozenset[str]:
    """Every string this module can publish that is NOT one of his two inputs."""
    return (frozenset(WORKPLACE_WORDS) | frozenset(FACETS)
            | frozenset(LOCATION_STATES) | frozenset(REFUSALS))


def _tokens(subtitle: str) -> list[str]:
    text = shape._WS.sub(" ", str(subtitle or "")).strip()
    return [t.strip() for t in text.split(shape.MIDDLE_DOT) if t.strip()]


def recent_search_entry(href: Optional[str],
                        subtitle: Optional[str]) -> Optional[dict[str, Any]]:
    """One anchor -> one entry, or None when it is not a history entry. PURE.

    ``subtitle`` is the text of the anchor's LAST direct child span. The first
    span -- the query as rendered -- is never read: the href's query is the
    canonical copy of it. Nothing here raises on anything the page chose: a
    malformed href is simply not an entry.
    """
    try:
        parts = urlsplit(str(href or ""))
        query = parse_qs(parts.query, keep_blank_values=True)
    except ValueError:
        return None
    if parts.path.rstrip("/") != SEARCH_ROUTE.rstrip("/"):
        return None
    if query.get("origin") != [HISTORY_ORIGIN]:
        return None

    keywords = shape.notification_handles(str(href)).get("search_keywords")
    tokens = _tokens(subtitle or "")
    lowered = [t.lower() for t in tokens]
    workplace = next((w for w in WORKPLACE_WORDS if w in lowered), None)
    places = [t for t, low in zip(tokens, lowered)
              if low not in (ALERT_BADGE, NETWORK_BADGE)
              and low not in WORKPLACE_WORDS]
    if len(places) == 1:
        state, location = "read", shape.trim(places[0], MAX_LOCATION_CHARS)
    elif not places:
        state, location = "absent", None
    else:
        state, location = "ambiguous", None

    return {
        "search_keywords": (shape.trim(keywords, MAX_KEYWORDS_CHARS)
                            if keywords else None),
        "location": location,
        "location_state": state,
        "alert_on": ALERT_BADGE in lowered,
        "in_your_network": query.get("f_JIYN") == ["true"],
        "workplace": workplace,
        "facets": [f for f in FACETS if f in query],
    }


def _empty() -> dict[str, Any]:
    return {
        "searches": [],
        "entries_seen": 0,
        "anchors_scanned": 0,
        "alerts_on": 0,
        "list_label_seen": False,
        "refusal": None,
        "error": None,
    }


async def read_recent_searches(page: Any) -> dict[str, Any]:
    """Read the recent-searches list off the jobs home it is handed.

    RETURNS::

        {
          "searches": [ {                 # one per history entry, page order
              "position": int,
              "search_keywords": str | None,   # his query, off the href
              "location": str | None,          # his place, one subtitle token
              "location_state": str,           # a literal of LOCATION_STATES
              "alert_on": bool,                # the entry carries a job alert
              "in_your_network": bool,         # the href's f_JIYN
              "workplace": str | None,         # a literal of WORKPLACE_WORDS
              "facets": [str],                 # literals of FACETS, present keys
          } ],
          "entries_seen": int,        # history entries recognised
          "anchors_scanned": int,     # every search-route anchor in main
          "alerts_on": int,           # entries carrying the alert badge
          "list_label_seen": bool,    # THE CONTROL a zero is only readable beside
          "refusal": str | None,      # a literal of REFUSALS
          "error": str | None,        # an exception's TYPE NAME only
        }

    **``text_content``, NEVER ``inner_text``, AND IT IS NOT A STYLE CHOICE.**
    Half the entries on the measured page sit in LinkedIn's COLLAPSED state
    behind its show-more control, and HOW that state hides them is not
    measured -- the capture carries the class, not the stylesheet.
    ``inner_text`` follows rendering: under ``visibility:hidden`` it returns
    an empty string, so a reader built on it could read those entries' badges
    and places as absent on the live page while passing every test over a
    fixture with no stylesheet. (Under ``display:none`` it happens to fall
    back to the full text, which is why a test that only tried that mode was
    shown unable to tell the two apart, and was rewritten.) ``text_content``
    is the DOM's text whatever the styling; ``tests/test_job_home.py`` hides
    the collapsed entries both ways and requires them read.

    **EVERY FIELD IS RESET ON AN EXCEPTION**, and the error is the exception's
    type name and never its message, because a message can carry what the page
    chose and ``ERROR-MESSAGE-RULED-AT-THE-RAISE`` forbids that anywhere.
    """
    out = _empty()
    try:
        anchors = page.locator(_ANCHORS)
        total = int(await anchors.count())
        out["anchors_scanned"] = total
        for index in range(min(total, MAX_ANCHORS)):
            anchor = anchors.nth(index)
            href = await anchor.get_attribute("href")
            spans = anchor.locator(":scope > span")
            count = int(await spans.count())
            subtitle = (str(await spans.nth(count - 1).text_content() or "")
                        if count else "")
            entry = recent_search_entry(href, subtitle)
            if entry is None:
                continue
            entry = {"position": len(out["searches"]), **entry}
            out["searches"].append(entry)
        out["entries_seen"] = len(out["searches"])
        out["alerts_on"] = sum(1 for e in out["searches"] if e["alert_on"])
        label = page.locator(f'main [aria-label="{RECENT_LIST_LABEL}"]')
        out["list_label_seen"] = bool(int(await label.count()))
        if not out["searches"] and not out["list_label_seen"]:
            out["refusal"] = "no_recent_search_list_drawn"
    except Exception as exc:  # noqa: BLE001 -- reported, never swallowed
        out = _empty()
        out["error"] = type(exc).__name__
    return out
