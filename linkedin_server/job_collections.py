"""The two Premium job collections, read as COUNTS and NUMERIC IDS.

``/jobs/collections/top-applicant`` and ``/jobs/collections/top-choice`` are
the two Premium job surfaces LinkedIn draws on this account's Premium hub. The
first is the Top Applicant signal the standing question names by name.

## NOBODY HAS EVER OPENED EITHER PAGE, AND THIS MODULE SAYS SO IN ITS OUTPUT

There is no capture of either address. This reader is built against the SHAPE
of the two job-list surfaces that HAVE been captured -- ``/jobs/collections/
recommended/`` and ``/jobs/search/``, both admitted, both captured live on
2026-09-20.

**THAT IS A HYPOTHESIS ABOUT THE TARGET, NOT A MEASUREMENT OF IT.** Two
sibling surfaces agreeing is the best evidence available with zero page loads,
and it is still evidence about the siblings. Everything this module publishes
is therefore designed so that a WRONG hypothesis announces itself instead of
returning a confident zero -- see :data:`REFUSALS` and the paragraph on
``list_container_seen`` below.

## THE LIST HAS TWO TIERS, AND ``slots`` IS THE ANSWER WHILE ``hydrated`` IS NOT

**THIS MODULE'S FIRST VERSION COUNTED THE WRONG THING AND WOULD HAVE
UNDER-REPORTED BY 3.4x.** It counted hydrated cards, because that is what a
job card looks like in a DOM. Measured:

    metric                            recommended    search
    list slots       (tier 1)                  24        25
    hydrated cards   (tier 2)                   7         7
    placeholder slots                          17        18
    slots neither hydrated nor placeholder      0         0
    hydration ratio                          7/24      7/25
    cross-tier id equality                    7/7       7/7
    slot tag / list parent                 li / ul   li / ul
    id digit length                         10-10     10-10
    <main> count                                1         1

LinkedIn draws ONE ``li[data-occludable-job-id]`` per posting it has placed in
the list window, hydrated or not, and fills only the few near the viewport.
A reader counting tier 2 reports **7 postings when the collection holds 24**,
with a number attached to make it look measured. That is the exact failure
shape this repository keeps finding: a confident wrong answer that nothing in
the reading contradicts.

So ``slots`` is the headline and ``hydrated`` is published beside it as the
render state. This is ``newsletters.py``'s rule arriving on another surface --
*"``distinct`` IS THE ANSWER, NOT ``anchors``"*, ten anchors and five
newsletters -- and the reason is the same: the smaller number is a fact about
what the page had drawn at one moment, not about what the account holds.

**AND THE IDS COME FROM THE SLOT TIER FOR THE SAME REASON.** Every slot
carries the posting id whether or not its card has rendered, so the slot tier
yields all 24 where the card tier yields 7. Cross-tier equality was measured
7 of 7 on both captures with zero mismatches, so the slot's id IS the posting
id and this is not a substitution of one identifier for another.

## A ZERO AND A PARSE MISS ARE DIFFERENT ANSWERS AND NEVER SHARE A FIELD

This repository has lost rounds to a reader that could not say why it was
empty, and the standing rule is that a refusal reporting only what it did NOT
match is half a measurement. So a caller of this module always gets BOTH:

    cards == 0  and  list_container_seen is True    ->  HIS ACCOUNT HAS NONE
    cards == 0  and  list_container_seen is False   ->  THIS READER COULD NOT SEE

The second case also carries ``refusal``, a literal of :data:`REFUSALS`, and
``empty_state_needles`` -- how many of a vocabulary THIS FILE authors the page
drew. A page that says "nothing here" and a page that says nothing at all are
different findings, and section 11 of the live-capture audit is the case that
made the distinction worth a field: `/learning/role-play/scenarios/` served,
rendered 17 characters in ``main``, and drew no empty-state message at all.

## IT COUNTS TWO SELECTORS, IN AND OUT OF ``main``, AND PUBLISHES ALL FOUR

The obvious implementation counts one selector over the whole document. This
module refuses to, for a reason measured on this exact page family: a live
load of ``/analytics/profile-views/`` parsed **12 viewer rows document-wide
and 0 inside an 1835-character ``main``** -- the reader looking in the wrong
box, confirmed rather than inferred, and the second time that row was nearly
closed on an instrument that could not have seen it.

So the scope is never assumed. Both ``[data-job-id]`` and the
``job-card-container`` class token are counted INSIDE ``main`` and ACROSS THE
DOCUMENT, and the four numbers are published. If the target page nests its
list outside ``main``, ``cards`` is 0 while ``cards_outside_main`` is not, and
that is visible to the caller in the same reading rather than a month later.

**AND THE SCOPING IS PROVED, NOT PROMISED.** The committed fixture carries a
DECOY card OUTSIDE ``main`` -- the newsletter wave's mechanism, reused with its
reason -- and ``tests/test_job_collections.py`` installs the naive
document-wide selector and measures it reporting the wrong count against the
shipped one. On the two real captures ``data-job-id`` measures 7 == 7, so a
document-wide reader would agree with a scoped one there; a scoping claim
proved only against those captures would be proving nothing, which is exactly
why the decoy is synthetic and deliberate.

## WHAT CROSSES THE BOUNDARY, AND WHY A JOB ID IS ALLOWED TO

Integers, booleans, literals of this file, and **NUMERIC POSTING IDS**.

A posting id is not a person. It addresses a public job advertisement, the
shipped ``linkedin_search_jobs`` already returns them, and ``/jobs/view/
<digits>/`` is already on the read allowlist -- so an id handed back here is
consumable by ``linkedin_job_detail`` without widening anything. **That
consumability is the whole capability**: it turns "Top Applicant" from a label
into postings a caller can read.

**AND IT IS THE ONLY PAGE-DERIVED VALUE HERE, SO IT IS GATED ON SHAPE.** Every
candidate is matched against :data:`JOB_ID_SHAPE` in Python before it is
published; anything failing is DROPPED and COUNTED in ``ids_refused``, never
returned and never silently discarded. The output alphabet for that field is
therefore digits, and a page that put a title where the id goes produces a
refusal count rather than a title in a caller's hands.

No job title, company name, recruiter name, location or salary is read,
shaped, redacted or present in this process. There is nothing to redact
because nothing textual is taken.

## IT NAVIGATES NOTHING AND PRESSES NOTHING

It reads the document it is handed. The caller owns reaching the address, owns
checking it through ``readonly.assert_read_url`` first, and owns the
invitation-badge obligation. Nothing here clicks, fills, submits or evaluates.
"""

from __future__ import annotations

import re
from typing import Any, Optional

#: THE CLOSED SET OF COLLECTIONS THIS MODULE KNOWS. Order is the contract: a
#: caller names a collection by POSITION, so reordering this tuple silently
#: renames every reading ever taken. ``tests/test_job_collections.py`` pins it.
#:
#: **BOTH WERE READ OFF LINKEDIN, NEITHER WAS GUESSED.** Each is an href
#: LinkedIn served to this account on his own Premium hub, measured as a DRAWN
#: ANCHOR in the stripped markup rather than as a substring of the bundle --
#: 1 anchor each on ``cap-premium-hub.html``. That is the standard the
#: newsletter wave set and this module keeps. A third collection LinkedIn adds
#: tomorrow needs a deliberate edit here, plus its own allowlist entry, which
#: is the point.
COLLECTIONS: tuple[str, ...] = (
    "top-applicant",
    "top-choice",
)

_BASE = "https://www.linkedin.com/jobs/collections/"

#: Refusals, each a literal. A reader that cannot say why it is empty is the
#: green this repository distrusts most.
REFUSALS: tuple[str, ...] = (
    "no_card_container_drawn",
    "index_out_of_range",
)

#: **TIER 1, AND THE HEADLINE.** One per posting LinkedIn has placed in the
#: list window, hydrated or not. Chosen over every alternative by measurement
#: rather than taste: it sits on 24 of 24 and 25 of 25 slots, and its
#: DOCUMENT-WIDE count equals the slot count exactly on both captures, while
#: the raw ``class`` attribute counts 733/524 and 1067/557 and the ``id``
#: attribute 249/148 and 350/190 -- a reader aimed at either is a reader whose
#: answer depends on where it happens to look.
SLOT_SELECTOR = "main [data-occludable-job-id]"
SLOT_SELECTOR_ANYWHERE = "[data-occludable-job-id]"

#: **TIER 2, THE RENDER STATE.** Only the slots LinkedIn has actually filled.
#: Published BESIDE tier 1, never instead of it -- see the module docstring for
#: the 3.4x undercount this pair exists to prevent.
CARD_SELECTOR = "main [data-job-id]"
CARD_SELECTOR_ANYWHERE = "[data-job-id]"

#: THE CLASS TOKEN, counted as well rather than instead. LinkedIn names the
#: hydrated card container itself, and if a future deploy drops
#: ``data-job-id`` these numbers diverge and say so, where a single selector
#: would just return 0 and look like an empty collection.
CONTAINER_SELECTOR = "main .job-card-container"
CONTAINER_SELECTOR_ANYWHERE = ".job-card-container"

#: The attributes the ids are read from. THE SLOT ONE IS THE SOURCE, because
#: it is present on every posting and the card one is present only on the few
#: that have rendered; cross-tier equality was measured 7 of 7 on both
#: captures, so this is not a substitution of one identifier for another.
SLOT_ID_ATTRIBUTE = "data-occludable-job-id"
JOB_ID_ATTRIBUTE = "data-job-id"

#: **THE OUTPUT GATE FOR THE ONE PAGE-DERIVED VALUE.** Digits only, and
#: bounded. Measured 10 digits on every card of both captured surfaces; the
#: range is wider than the measurement because a bound read off one day's
#: corpus is a reading with a timestamp, and the shipped allowlist pattern for
#: ``/jobs/view/`` already accepts six or more.
JOB_ID_SHAPE = re.compile(r"^[0-9]{6,20}$")

#: Generic empty-state vocabulary, **AUTHORED HERE** rather than read off a
#: page. Its only use is to turn a zero into a reading: how many of these the
#: page drew is published beside ``cards``, so "he has none" and "I could not
#: see" stop sharing a field. Counted, never returned as text.
EMPTY_STATE_NEEDLES: tuple[str, ...] = (
    "no results",
    "nothing here",
    "no jobs",
    "not available",
    "no longer",
    "try again",
    "page not found",
    "coming soon",
    "check back",
    "we could not",
    "something went wrong",
    "no matches",
)


def collection_url(index: int) -> str:
    """One INDEX into :data:`COLLECTIONS` -> one address. Never a free string.

    A caller cannot hand this module an arbitrary path: the only inputs it
    accepts are positions in a tuple defined in this file, so the set of
    addresses it can ever produce is closed and enumerable by reading the
    constant above.

    OUT OF RANGE RAISES RATHER THAN CLAMPING. A clamp would silently return
    one collection when another was asked for, and a reading filed under the
    wrong collection is worse than no reading -- it is a wrong answer wearing
    a measurement's clothes.
    """
    if isinstance(index, bool) or not isinstance(index, int):
        raise TypeError("collection index must be an int, not %r" % type(index))
    if not 0 <= index < len(COLLECTIONS):
        raise IndexError(
            "no collection at index %d; this module knows %d: %s"
            % (index, len(COLLECTIONS), ", ".join(COLLECTIONS))
        )
    return _BASE + COLLECTIONS[index] + "/"


def term_for(index: int) -> str:
    """One index -> one literal of this module. Out of range REFUSES."""
    if isinstance(index, bool) or not isinstance(index, int):
        return "index_out_of_range"
    if 0 <= index < len(COLLECTIONS):
        return COLLECTIONS[index]
    return "index_out_of_range"


def emitted_alphabet() -> frozenset[str]:
    """Every NON-NUMERIC string this module can publish.

    Named as a function rather than described in prose so the test can compare
    it against what :func:`read_job_collection` actually emits over adversarial
    input. A new literal added below without a thought fails there rather than
    reaching a caller. Posting ids are excluded by construction: they are
    digits, gated by :data:`JOB_ID_SHAPE`, and are the one page-derived value.
    """
    return frozenset(COLLECTIONS) | set(REFUSALS)


async def read_job_collection(page: Any, expect: Optional[int] = None) -> dict[str, Any]:
    """Count the postings this collection drew. Returns integers and ids.

    THE ONLY FUNCTION HERE THAT TOUCHES A PAGE, and it navigates nothing.

    RETURNS::

        {
          "collection": str | None,       # a literal, from `expect`, never the page
          "slots": int,                   # TIER 1, INSIDE main -- THE ANSWER
          "slots_outside_main": int,      # the scope control -- see the module docstring
          "hydrated": int,                # TIER 2, INSIDE main -- the render state
          "hydrated_outside_main": int,
          "containers": int,              # .job-card-container INSIDE main
          "containers_outside_main": int,
          "list_container_seen": bool,    # THE CONTROL a zero is only readable beside
          "job_ids": [str],               # from TIER 1, digits only, gated by JOB_ID_SHAPE
          "ids_refused": int,             # candidates dropped by that gate
          "empty_state_needles": int,     # of EMPTY_STATE_NEEDLES, drawn in main
          "refusal": str | None,          # a literal of REFUSALS
          "error": str | None,
        }

    **``slots`` IS THE POSTING COUNT AND ``hydrated`` IS NOT.** Measured 24 vs
    7 and 25 vs 7 on the two captured siblings. They never share a field, and
    a caller that publishes the second as the first has under-reported this
    surface by more than three times.

    ``expect`` IS AN INDEX, NEVER A NAME, so a label cannot reach this function
    even by mistake and the returned ``collection`` is a literal of this file
    rather than anything the document chose.

    **EVERY FIELD IS RESET ON AN EXCEPTION.** A partial reading is worse than
    none, because nothing downstream can tell the difference -- a count taken
    before a frame detached looks exactly like a count taken after a whole
    successful read. The newsletter reader was given this property by a test
    that caught its absence, and the same test exists here.
    """
    out: dict[str, Any] = {
        "collection": None,
        "slots": 0,
        "slots_outside_main": 0,
        "hydrated": 0,
        "hydrated_outside_main": 0,
        "containers": 0,
        "containers_outside_main": 0,
        "list_container_seen": False,
        "job_ids": [],
        "ids_refused": 0,
        "empty_state_needles": 0,
        "refusal": None,
        "error": None,
    }
    if expect is not None:
        out["collection"] = term_for(expect)
        if out["collection"] == "index_out_of_range":
            out["collection"] = None
            out["refusal"] = "index_out_of_range"
            return out

    try:
        # THREE SELECTORS, BOTH SCOPES, SIX PLAIN PLAYWRIGHT COUNTS. No
        # injection, no evaluate, and no href or label is read by any of them
        # -- only how many there are.
        slots_in_main = int(await page.locator(SLOT_SELECTOR).count())
        slots_anywhere = int(await page.locator(SLOT_SELECTOR_ANYWHERE).count())
        cards_in_main = int(await page.locator(CARD_SELECTOR).count())
        cards_anywhere = int(await page.locator(CARD_SELECTOR_ANYWHERE).count())
        boxes_in_main = int(await page.locator(CONTAINER_SELECTOR).count())
        boxes_anywhere = int(await page.locator(CONTAINER_SELECTOR_ANYWHERE).count())

        out["slots"] = slots_in_main
        out["slots_outside_main"] = max(slots_anywhere - slots_in_main, 0)
        out["hydrated"] = cards_in_main
        out["hydrated_outside_main"] = max(cards_anywhere - cards_in_main, 0)
        out["containers"] = boxes_in_main
        out["containers_outside_main"] = max(boxes_anywhere - boxes_in_main, 0)

        # THE CONTROL. ANY of the three finding anything ANYWHERE proves the
        # reader reached a job-list document. Deliberately not scoped to main,
        # because its job is to separate "nothing here" from "this is not the
        # page I think it is", and a list nested outside main is the first
        # case and not the second. Deliberately taking the SLOT tier too: a
        # window of entirely unhydrated placeholders draws zero cards and is
        # still a populated list, and a control blind to that would call the
        # richest possible page a parse miss.
        out["list_container_seen"] = bool(
            slots_anywhere or cards_anywhere or boxes_anywhere
        )

        # THE IDS, FROM THE SLOT TIER, INSIDE main only, gated on shape in
        # Python before any of them is published. The slot tier is the source
        # because it carries an id for every posting; the card tier carries
        # one only for the few that have rendered -- 7 of 24, measured.
        slots = page.locator(SLOT_SELECTOR)
        for index in range(slots_in_main):
            value = await slots.nth(index).get_attribute(SLOT_ID_ATTRIBUTE)
            candidate = str(value or "").strip()
            if JOB_ID_SHAPE.match(candidate):
                out["job_ids"].append(candidate)
            else:
                out["ids_refused"] += 1

        # WHAT THE PAGE SAID WHEN IT DREW NOTHING. Counted inside main, from a
        # vocabulary this file authors; no page text is returned.
        main = page.locator("main")
        if int(await main.count()):
            text = str(await main.first.inner_text() or "").lower()
            out["empty_state_needles"] = sum(
                1 for needle in EMPTY_STATE_NEEDLES if needle in text
            )

        if not out["list_container_seen"]:
            out["refusal"] = "no_card_container_drawn"
    except Exception as exc:  # noqa: BLE001 -- reported, never swallowed
        out["slots"] = 0
        out["slots_outside_main"] = 0
        out["hydrated"] = 0
        out["hydrated_outside_main"] = 0
        out["containers"] = 0
        out["containers_outside_main"] = 0
        out["list_container_seen"] = False
        out["job_ids"] = []
        out["ids_refused"] = 0
        out["empty_state_needles"] = 0
        out["refusal"] = None
        out["error"] = "%s: %s" % (type(exc).__name__, exc)
    return out


def control_fixture() -> str:
    """A synthetic job-list DOM that MUST produce a known reading.

    **THIS EXISTS BECAUSE THE TARGET PAGE HAS NEVER BEEN OPENED.** A zero from
    this reader on a live surface is two different findings -- the collection
    is empty, or the card shape is not what the two captured siblings drew --
    and nothing in the reading separates them. A control that must fire does.

    It is SYNTHETIC and carries no page text: every string in it is markup, a
    literal of this module, or a digit run. Its card count, its decoy and its
    id shapes are the measurement off ``cap-jobs-recommended.html`` and
    ``cap-jobs-search.html``, never their content.

    FOUR SLOTS INSIDE ``main`` -- two hydrated, one bare placeholder, one whose
    id is not a digit run -- plus ONE DECOY SLOT OUTSIDE ``main`` carrying a
    hydrated card of its own. A single run therefore exercises the tier pair,
    both scope pairs, the shape gate and the refusal counter at once, and the
    placeholder is what proves the reader does not need a card to count a
    posting.
    """
    def slot(identifier, hydrated):
        card = (
            '<div><div class="job-card-container" data-job-id="%s">'
            '<a href="/jobs/view/%s/"></a><span></span></div></div>'
            % (identifier, identifier)
        ) if hydrated else ""
        return ('<li data-occludable-job-id="%s">%s</li>' % (identifier, card))

    inside = (
        slot("1000000001", True)
        + slot("1000000002", True)
        + slot("1000000003", False)
        + slot("not-a-posting-id", False)
    )
    decoy = (
        '<aside><ul>'
        + slot("1000000099", True)
        + "</ul></aside>"
    )
    return (
        "<html><body>"
        + decoy
        + "<main><ul>"
        + inside
        + "</ul></main></body></html>"
    )
