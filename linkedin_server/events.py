"""The events he is registered for, off a page that has now been opened twice.

``/events/`` was admitted to the read boundary on 2026-09-05 with an admission
comment recording that it was bought on a THINNER row basis than ``/groups/``:
the census has no row for "the events you are registered for", so the
admission bought a recommendation surface and bought the self-scoped read
"only if LinkedIn draws a 'your events' region that no census row names".

**IT DRAWS ONE, AND IT IS EMPTY.** Measured offline over the capture and then
live, twice, with a control passing at both ends of the session: the root
renders three sibling card sections; the first carries a heading and a list
binding holding nothing, and the other two are full.

    card 0   'Your events'              0 rows    0 event anchors
    card 1   a promoted section          3 rows    9 event anchors
    card 2   'Recommended for you'      15 rows   45 event anchors

That 18/54 split reproduces, from a live DOM walk, exactly the 18 distinct
addresses and 54 anchors an independent regex pass measured over the capture.

**A RENDERED CONTAINER WHOSE LIST BINDING IS EMPTY IS NOT AN UNRENDERED
CONTAINER.** Bounded by element rather than by offset -- which the first
attempt got wrong, producing a plausible 98-character "empty state message"
that was markup -- the first card's body inner HTML is 29 characters, 0 of
text, 0 anchors, holding a framework empty-binding comment. A section that had
not hydrated would carry a skeleton or would not be in the document. This one
is structurally complete and holds a list of length zero.

## THE PRIOR FINDING THIS REFINES, BECAUSE THE DIFFERENCE DECIDES ROWS

``_audit/2026-09-05-groups-events-precondition.md`` s8 records, correctly for
the question it asked, that no "events you are registered for" surface exists:
eighteen distinct events, fifteen of them recommendations by LinkedIn's own
heading, and not one of them his attendance. That pass assigned anchors to
headings, and **a heading with zero anchors under it is invisible to an
anchor-assignment pass.** So the region was not missed by carelessness; it was
outside what that instrument could see.

The refinement matters because the two readings retire census rows
differently. "The platform has no such surface" retires a row as impossible in
principle. "The surface exists, on an address already open, and is empty for
this account" leaves the row REACHABLE and makes its answer today a measured
zero -- which is a different ledger entry and a reversible one.

## WHY IT IS A MODULE AND NOT A BLOCK IN ``dom.py``

``dom.py`` held 121 uncommitted lines from another wave at the moment this was
written, and ``git commit --only`` does not protect a neighbour's LINES inside
a path you name -- measured in this tree three times this week. This block was
in fact appended to ``dom.py`` first and then lifted back out, byte for byte,
leaving that wave's lines untouched. The package already carries focused
modules of this size, and ``newsletters.py`` took the same route the same day
for the same reason.

## WHAT MAY BE SAID

**THE BOUNDARY DECIDES WHAT MAY BE OPENED; THE SHAPER DECIDES WHAT MAY BE
SAID.** This module opens nothing -- it reads a page it is handed -- and it
publishes counts and a key from a closed set. The self-scoped card is
identified by matching its heading against
:data:`EVENTS_HOME_SELF_SCOPED_HEADINGS` INSIDE this process; what leaves is
``known: "your_events"``, a string this module owns. The page's own heading
leaves only through ``census_shape`` and ``census_redact_rare``, fed the
heading's real count.

That is why this reader has no version of the hole recorded on
:func:`shape.membership_row`, where a group named after a person ships that
person's name: **the identification does not travel through the name channel
at all**, so blanking the name costs the answer nothing.
``tests/test_events_home_reader.py`` asserts both halves -- that a
person-shaped heading is redacted, and that a single-token heading is not,
which is declared there as a known limit rather than left to be discovered.

## THE COST OF THE LOAD, MEASURED AND BOUNDED

Read feed -> events -> feed on 2026-09-05, so both ends of the comparison came
off the same nav: the pending-invitation badge and the messaging badge were
both READ at both ends and neither moved.

**THE HONEST BOUND IS NARROWER THAN THAT SOUNDS, AND IT IS STATED HERE RATHER
THAN IN A FOOTNOTE.** Both counters stood at zero, and
:func:`shape.invitation_badge` already records why that is weak: a badge
sitting at zero cannot distinguish "the page consumed nothing" from "there was
nothing to consume". Separately, the events root renders the nav WITHOUT
either count on it, so an after-reading taken on the page itself is a refusal
rather than a number -- which is why the comparison goes back to the feed.
The events root draws no counter of its own: ``aria-haspopup`` 0,
``role="menu"`` 0, ``role="dialog"`` 0 across 1294108 characters.
"""
from __future__ import annotations

from typing import Any, Optional

from linkedin_server import shape
from linkedin_server.dom import ELEMENT_READ_TIMEOUT_MS

#: The three sibling cards at the events root. A class CONTAINMENT match, and
#: the choice is deliberate: the three carry different structural classes
#: (two share one, the promoted one has its own) and agree on exactly this
#: token, so matching it finds all three where matching either of the others
#: finds a subset. Measured on the capture: 3 sections, 3 headings, 18 rows.
EVENTS_HOME_CARD_SELECTOR = 'section[class*="events-home__card-container"]'

#: One event row inside a card. A CLASS-TOKEN match (``~=``), not a substring
#: match, AND THAT IS THE WHOLE OF THE CORRECTNESS HERE.
#:
#: The first version of this line used ``[class*="discovery-card"]`` and read
#: **54 rows where there are 18**, live, because each row contains two
#: descendants whose own class tokens begin with the row's class and a double
#: underscore -- a details section and a controls section. A substring match
#: counts a row three times.
#:
#: **AND IT LOOKED CORROBORATED, WHICH IS WHY IT IS WRITTEN UP RATHER THAN
#: QUIETLY FIXED.** The same run reported ``rows`` and ``event_links`` as 9/9
#: and 45/45 -- two numbers from two different selectors AGREEING exactly. They
#: agreed because this page draws three anchors per row and the broken
#: selector counted three sections per row, so both were the same multiple of
#: the truth. Two instruments agreeing is evidence only when their errors are
#: independent, and here one number was right and the other was wrong by a
#: factor that made them equal.
EVENTS_HOME_ROW_SELECTOR = 'section[class~="events-components-shared-discovery-card"]'

#: An event link inside a card. CONTAINMENT rather than ``startswith``: this
#: page writes RELATIVE hrefs, measured, which is the same fact
#: :func:`shape.census_href_identifies_entity` records at its own site and the
#: same one that made a sibling probe's first matcher find zero of 54.
EVENTS_HOME_LINK_SELECTOR = 'a[href*="/events/"]'

#: The heading of a card.
EVENTS_HOME_HEADING_SELECTOR = "h2"

#: THE CLOSED SET, AND IT IS THE WHOLE OF THE IDENTIFICATION.
#:
#: The self-scoped card is recognised by matching its heading against this
#: tuple INSIDE this process, and what leaves is the KEY -- a string this
#: module owns -- never LinkedIn's text. That is the difference between
#: emitting a RELATION and emitting a VALUE, and it is why this reader has no
#: version of the hole recorded on :func:`shape.membership_row`: a name cannot
#: escape through a field that never carries one.
#:
#: A LABEL CHANGE MUST BE VISIBLE AS A REFUSAL, NEVER AS A ZERO. When nothing
#: matches, this function returns ``cards_read`` and each card's shaped
#: heading and row count, so a reader can tell "LinkedIn renamed the section"
#: from "the page did not load" without opening a browser.
EVENTS_HOME_SELF_SCOPED_HEADINGS: tuple[str, ...] = ("your events",)


def _events_home_verdict(
    *, found: bool, own_rows: int, other_rows: int, cards: int
) -> tuple[Optional[int], str]:
    """How many events he is registered for, and why that is or is not known.

    Split out from the reader so the whole decision table is testable without
    a browser, which is the only way its ZERO branch can be shown FAILING --
    and a zero that cannot be shown failing is the defect this function was
    written to avoid.
    """
    if cards <= 0:
        return None, "no_cards"
    if not found:
        return None, "heading_unmatched"
    if own_rows > 0:
        return own_rows, "rows_present"
    if other_rows <= 0:
        # EVERY CARD EMPTY. The page did not hydrate, or LinkedIn restructured
        # it. Either way the zero is about the read.
        return None, "page_unhydrated"
    return 0, "empty_beside_full_siblings"


async def read_events_home(page: Any) -> dict[str, Any]:
    """The events root, card by card, with the zero corroborated or refused.

    LOCATOR-ONLY. No ``page.evaluate`` and therefore no ``# readonly-ok``
    waiver: the waiver count on this module is pinned, and claiming an
    exemption a call does not need is a boundary change wearing a read's
    costume.

    WHAT IT RETURNS, and every field is a count or a key from a closed set:

    ``cards`` -- one record per sibling card. ``known`` is ``"your_events"``
    or ``None``; ``heading_shape`` is the heading through ``census_shape``
    then ``census_redact_rare`` fed the heading's ACTUAL number of occurrences
    among the cards. At the measured one-each that redacts every heading,
    which is correct and is why ``known`` exists: the identification travels
    as a key this module owns and the page's own text travels as a marker.

    ``registered_events`` -- an integer, or ``None`` when it is not known.
    ``verdict`` -- one of four closed strings saying which.

    THE ZERO IS NEVER RETURNED ALONE. ``empty_beside_full_siblings`` is the
    only verdict that carries one, and it requires the self-scoped card to be
    present AND at least one sibling card to be non-empty. Every other shape
    of page returns ``None`` and says what it saw.
    """
    out: dict[str, Any] = {
        "cards_read": 0,
        "cards": [],
        "rows_total": 0,
        "registered_events": None,
        "verdict": "no_cards",
        "error": None,
    }
    try:
        cards = page.locator(EVENTS_HOME_CARD_SELECTOR)
        count = await cards.count()
    except Exception as error:  # noqa: BLE001
        out["error"] = f"{type(error).__name__}: {error}"
        return out

    out["cards_read"] = int(count)
    raw_headings: list[str] = []
    records: list[dict[str, Any]] = []
    for index in range(int(count)):
        card = cards.nth(index)
        heading = ""
        try:
            headings = card.locator(EVENTS_HOME_HEADING_SELECTOR)
            if await headings.count():
                heading = (
                    await headings.first.inner_text(
                        timeout=ELEMENT_READ_TIMEOUT_MS
                    )
                    or ""
                ).strip()
        except Exception:  # noqa: BLE001
            heading = ""
        try:
            rows = await card.locator(EVENTS_HOME_ROW_SELECTOR).count()
        except Exception:  # noqa: BLE001
            rows = 0
        try:
            links = await card.locator(EVENTS_HOME_LINK_SELECTOR).count()
        except Exception:  # noqa: BLE001
            links = 0
        raw_headings.append(heading)
        records.append(
            {
                "known": (
                    "your_events"
                    if heading.strip().lower()
                    in EVENTS_HOME_SELF_SCOPED_HEADINGS
                    else None
                ),
                "rows": int(rows),
                "event_links": int(links),
            }
        )

    # THE COUNT ``census_redact_rare`` NEEDS, taken over the headings actually
    # read rather than assumed. Fed a guess it is not the shipped rule.
    tally: dict[str, int] = {}
    for text in raw_headings:
        tally[text] = tally.get(text, 0) + 1
    for record, text in zip(records, raw_headings):
        record["heading_shape"] = shape.census_redact_rare(
            shape.census_shape(text), tally.get(text, 1)
        )

    own = [record for record in records if record["known"] == "your_events"]
    own_rows = sum(int(record["rows"]) for record in own)
    other_rows = sum(
        int(record["rows"]) for record in records if record["known"] is None
    )
    registered, verdict = _events_home_verdict(
        found=bool(own),
        own_rows=own_rows,
        other_rows=other_rows,
        cards=int(count),
    )
    out["cards"] = records
    out["rows_total"] = own_rows + other_rows
    out["registered_events"] = registered
    out["verdict"] = verdict
    return out
