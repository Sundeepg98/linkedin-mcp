r"""THE EVENTS ADMISSION IS ONE ADDRESS, AND THIS IS THE RULE THAT SAYS SO.

`readonly.py` admits `^https://www\.linkedin\.com/events/?$` and the comment
above that pattern lists what it declines to admit **by census row id** --
`N 184`, `C 92`, and "THE ATTENDEE LIST -- census rows `N 188` and `N 189`
... out of scope by the same ruling that put `N 165` out of scope."

**THAT COMMENT IS PROSE, AND PROSE CANNOT FAIL.** The census said so in its own
words and declined to retire the rows on it -- `_audit/_census/
blocker-assignments.tsv`, the `N 181` line, `0aca3d0`:

    NONE of those verdicts is enforced by a shipped rule -- the four
    EXCLUDED-RULED rest on readonly.py's admission COMMENT, which is prose in
    a source file and not a refusal anything can be shown failing against.
    Under the standing bar (a row moves only when a shipped, shown-failing
    rule refuses the capability) they stay GAP.

This file is that rule. It does not widen the boundary, decide anything, or
open a page; it makes the existing refusal **enforced instead of described**,
so that a later edit which quietly admits an attendee roster fails here rather
than shipping.

**WHY THE REFUSALS NEED THE ADMISSION PINNED BESIDE THEM.** A file of
all-refused assertions passes perfectly against a boundary that refuses
EVERYTHING -- including against a typo in the predicate, a renamed module, or
a `readonly.py` whose allowlist was emptied. So
:data:`EVENTS_ROOT_MUST_STAY_ADMITTED` is asserted in the same file: it is the
control that proves the predicate is still discriminating, and without it the
refusals certify nothing.

**AMENDED 2026-09-23 BY A LANE-L1 `REVIEW:` COMMIT, AND THE TITLE ABOVE IS NOW
A DATED CLAIM.** One event BY ITS NUMERIC ID -- census ``N 184``, *reach an
event through its URL* -- is admitted on its own anchored line, under the four
conditions the lead set for ``/groups/<id>/``. Its case moved OUT of the
must-stay-refused table below rather than being deleted, and
:data:`EVENT_BY_ID_ADMITTED` pins it; the SLUG form beside it (a title run into
the id) stays refused, and so do the attendee roster, comments, about, manage
and every sub-path. The title is kept because this file is cited by it; what
it protects -- the roster and the family -- is unchanged.

**EVERY EVENT ID BELOW IS A REPDIGIT AND EVERY SLUG CARRIES A SANCTIONED
SYNTHETIC TOKEN.** No real event was addressed and none was needed --
``is_read_url`` is a pure string predicate, so the ids here are shaped to be
self-evidently invented rather than redacted from something real.
"""

import pytest

from linkedin_server import readonly

BASE = "https://www.linkedin.com"

#: One repeated digit. A real LinkedIn event id is a 19-digit urn suffix, so
#: this is the right LENGTH and self-evidently not the right VALUE -- which is
#: what makes it safe to commit and still exercise the pattern honestly.
SYNTHETIC_EVENT_ID = "7777777777777777777"

#: THE CONTROL, AND IT IS NOT A COURTESY. If these ever go refused, every
#: assertion in the rest of this file starts passing for the wrong reason.
EVENTS_ROOT_MUST_STAY_ADMITTED = (
    f"{BASE}/events/",
    f"{BASE}/events",
)

#: WHAT THE ADMISSION DELIBERATELY DID NOT BUY. Each entry names the census
#: row it holds where it has one, because a refusal that cannot say which
#: capability it refuses is not evidence about the census.
EVENTS_DEEP_MUST_STAY_REFUSED = (
    ("THE ATTENDEE LIST -- census N 188, a second member roster, out of scope "
     "by the same ruling that put the group member list (N 165) out of scope",
     f"{BASE}/events/{SYNTHETIC_EVENT_ID}/attendees/"),
    ("the same roster filtered to 1st-degree connections -- census N 189. The "
     "filter is applied by LinkedIn, so the page is still the roster",
     f"{BASE}/events/{SYNTHETIC_EVENT_ID}/attendees/?facetConnectionOf=1"),
    # THE NUMERIC EVENT PAGE STOOD HERE UNTIL 2026-09-23 -- "an event page --
    # organiser and content. Census N 184". It is ADMITTED by its own line
    # (lane L1, a REVIEW: commit) and pinned in EVENT_BY_ID_ADMITTED below.
    # Its QUERY spelling takes its place: still refused, and still one of the
    # nine a family pattern would turn red, so the count in the test's
    # docstring below is unchanged.
    ("the numeric event page carrying a query -- the admitted line takes "
     "none, and a query is where a filter naming a person would arrive",
     f"{BASE}/events/{SYNTHETIC_EVENT_ID}/?x=1"),
    ("the same page in the form LinkedIn writes when the event has a slug",
     f"{BASE}/events/some-event-placeholder-{SYNTHETIC_EVENT_ID}/"),
    ("third-party comments on an event -- census C 92",
     f"{BASE}/events/{SYNTHETIC_EVENT_ID}/comments/"),
    ("the same page's about tab -- same page, same objection",
     f"{BASE}/events/{SYNTHETIC_EVENT_ID}/about/"),
    ("the organiser-side manager, which is a WRITE surface",
     f"{BASE}/events/{SYNTHETIC_EVENT_ID}/manage/"),
    ("event creation -- census M C57, publish-class",
     f"{BASE}/event-creation/new"),
    # MEASURED, AND NOT HELD BY THE ANCHOR. Installing an `/events/.*` family
    # pattern leaves this one refused, because it contains `/invite` and the
    # substring gate runs first -- so this entry pins THAT gate, not the
    # anchoring, and saying so is the difference between a guard and a guess.
    # Its own refusal message states the independence: "AND NO READ PATTERN
    # ADMITS THIS ADDRESS EITHER ... Both gates refuse it."
    ("the invitation manager. No invitation control exists on the root at all "
     "-- held by the /invite SUBSTRING gate, independently of the anchor",
     f"{BASE}/events/invited/"),
    ("a sub-path under the admitted root. The anchoring is the whole of the "
     "permission, and a sub-path is the obvious later widening",
     f"{BASE}/events/past/"),
    ("the discovery family -- other people's events by construction",
     f"{BASE}/events/discovery/"),
    ("the saved-events shelf, a different surface with its own blocker",
     f"{BASE}/my-items/saved-events/"),
    ("the events SEARCH vertical, which is SEARCH-RESULTS-SURFACE's row N 179 "
     "and not this blocker's to admit",
     f"{BASE}/search/results/events/?keywords=x"),
)


#: ONE EVENT BY ITS NUMERIC ID, admitted 2026-09-23 (lane L1, REVIEW). Both
#: slash forms. The slug form stays in the refused table above.
EVENT_BY_ID_ADMITTED = (
    f"{BASE}/events/{SYNTHETIC_EVENT_ID}/",
    f"{BASE}/events/{SYNTHETIC_EVENT_ID}",
)


@pytest.mark.parametrize("url", EVENT_BY_ID_ADMITTED)
def test_one_event_by_numeric_id_is_admitted_by_its_own_line(url):
    """The admission is the numeric id and exactly one line carries it."""
    readonly.assert_read_url(url)
    carriers = [p for p in readonly._ALLOWED_URL_PATTERNS if p.match(url)]
    assert len(carriers) == 1, [p.pattern for p in carriers]
    assert "[0-9]{1,20}" in carriers[0].pattern, carriers[0].pattern


@pytest.mark.parametrize("url", EVENTS_ROOT_MUST_STAY_ADMITTED)
def test_the_events_root_is_still_admitted_in_both_slash_forms(url):
    """THE VACUITY CONTROL. Asserted first because everything else depends on
    the predicate still being able to say yes.

    Both slash forms, for the reason the newsletter guard states: this project
    has already lost a diagnosis to a trailing slash, resolved zero, and read
    the absence as a finding.
    """
    readonly.assert_read_url(url)


@pytest.mark.parametrize(
    "why,url",
    EVENTS_DEEP_MUST_STAY_REFUSED,
    ids=[c[1] for c in EVENTS_DEEP_MUST_STAY_REFUSED],
)
def test_the_anchoring_is_the_whole_of_the_events_permission(why, url):
    """Each of these must be refused before any events widening and after it.

    `readonly.py` line 642 is anchored to the root with `$`. If one of these
    ever goes readable, the pattern was rewritten as a family -- and an event
    page is the most third-party-dense address in this census, because it
    draws an organiser and an attendee roster.

    **WHICH GATE HOLDS WHICH, MEASURED RATHER THAN ASSUMED.** Installing an
    `/events/.*` family pattern in memory turns 9 of these 13 red. Of the four
    that survive it, three are simply not under `/events/` -- and the fourth,
    `/events/invited/`, is held by the `/invite` SUBSTRING gate instead. So
    this file pins two mechanisms, not one, and an entry is annotated where it
    is not the anchoring that holds it. A guard that cannot say WHICH rule
    refuses an address will later be read as evidence for the wrong one.
    """
    with pytest.raises(Exception):
        readonly.assert_read_url(url)


def test_this_guard_can_fail_and_is_therefore_worth_having():
    """SHOWN FAILING. A guard whose every assertion is `raises` passes just as
    well against a predicate that refuses everything, against a typo'd url
    matching nothing, and against an allowlist somebody emptied.

    So this proves the two directions are really distinguishable HERE, in this
    file, over this module -- rather than asserting that they are.
    """
    admitted = f"{BASE}/events/"
    refused = f"{BASE}/events/{SYNTHETIC_EVENT_ID}/attendees/"

    assert readonly.is_read_url(admitted) is True, (
        "the control address stopped being admitted -- every refusal in this "
        "file is now passing for the wrong reason"
    )
    assert readonly.is_read_url(refused) is False

    # AND THE INVERSE, so a reader does not have to take the pair on trust:
    # feeding the guard's own assertion an address it must NOT refuse makes it
    # fail. This is the line that would catch an all-refusing predicate.
    with pytest.raises(BaseException):
        with pytest.raises(Exception):
            readonly.assert_read_url(admitted)
