"""ONE EVENT BY ITS NUMERIC ID is admitted, and nothing else under `/events/<id>/`.

REVIEW commit, lane L1, 2026-09-23 -- census ``N 184``, *reach an event through
its URL after it has been shared with you*. The argument is on the line in
``linkedin_server/readonly.py``: the four conditions the lead set for
``/groups/<id>/`` on 2026-09-19, applied to the events family, because the
root-only events entry had listed this address as NOT admitted and
``tests/test_the_events_boundary_is_root_only.py`` enforced that.

WHAT THIS FILE PINS: the numeric id in both slash spellings is admitted; the
SLUG form LinkedIn also draws (the event's title run into its id) is not; the
attendee roster, comments, about, manage, invite and every family spelling stay
refused; removing the line refuses the target again (the rollback); and the
line's blast radius over the shipped corpus plus this file's spellings is
exactly the numeric-event addresses.

Ids are placeholders: five digits, or the root-only file's repdigit.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from linkedin_server import readonly

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import blast_radius  # noqa: E402

B = "https://www.linkedin.com"
ID = "12345"
EVENT = f"{B}/events/{ID}/"
CARRIER = "com/events/[0-9]"

NEIGHBOURS = (
    (f"{B}/events/some-event-placeholder-{ID}/",
     "THE SLUG FORM -- a title run into the id; a title can carry a name"),
    (f"{B}/events/placeholder{ID}/", "a slug glued to the id"),
    (f"{B}/events/{ID}/attendees/",
     "THE ATTENDEE ROSTER -- N 188, out of scope with N 165"),
    (f"{B}/events/{ID}/attendees/?facetConnectionOf=1",
     "the roster filtered -- N 189"),
    (f"{B}/events/{ID}/comments/", "third-party comments -- C 92"),
    (f"{B}/events/{ID}/about/", "the same page's about tab"),
    (f"{B}/events/{ID}/manage/", "the organiser-side manager, a write surface"),
    (f"{B}/events/{ID}/invite/", "an invitation -- `/invite` refuses it first"),
    (f"{B}/events/{ID}/?x=1", "a QUERY"),
    (f"{B}/events/" + "1" * 21 + "/", "TWENTY-ONE digits, past the bound"),
    (f"{B}/events/\u0661\u0662\u0663\u0664\u0665/",
     "ARABIC-INDIC digits -- what `\\d` would admit"),
    (f"{B}/events/\uff11\uff12\uff13\uff14\uff15/", "FULLWIDTH digits"),
    (f"{B}/events/{ID}/../../in/someone-else/",
     "a TRAVERSAL onto a member profile"),
    (f"{B}/events/past/", "a sub-path under the root, not an id"),
    (f"{B}/search/results/events/?keywords=x", "the search vertical -- N 179"),
)


def _carriers():
    return [p for p in readonly._ALLOWED_URL_PATTERNS if CARRIER in p.pattern]


def test_one_event_by_numeric_id_is_admitted_in_both_spellings():
    assert readonly.is_read_url(EVENT)
    assert readonly.is_read_url(EVENT.rstrip("/"))


def test_the_root_is_still_admitted_and_by_its_own_line():
    for url in (f"{B}/events/", f"{B}/events"):
        assert readonly.is_read_url(url), url
        carriers = [p for p in readonly._ALLOWED_URL_PATTERNS if p.match(url)]
        assert len(carriers) == 1 and "[0-9]" not in carriers[0].pattern


@pytest.mark.parametrize("url,why", NEIGHBOURS)
def test_the_neighbours_are_refused(url, why):
    assert not readonly.is_read_url(url), why


def test_exactly_one_line_carries_it_and_removing_it_is_the_rollback():
    carriers = _carriers()
    assert len(carriers) == 1, [p.pattern for p in carriers]
    survivors = tuple(p for p in readonly._ALLOWED_URL_PATTERNS if p is not carriers[0])
    assert not any(p.match(EVENT) for p in survivors)
    assert not any(p.match(EVENT.rstrip("/")) for p in survivors)
    for url, why in NEIGHBOURS:
        assert not any(p.match(url) for p in survivors), why


def test_the_line_newly_admits_only_numeric_event_addresses():
    """Measured with ``blast_radius.newly_admitted`` -- the shipped instrument
    -- with the line taken out and handed back as the candidate. The shipped
    corpus already carries one numeric event spelling of its own, so the
    expected set is that one plus this file's two."""
    carriers = _carriers()
    assert len(carriers) == 1
    original = readonly._ALLOWED_URL_PATTERNS
    corpus = sorted(
        set(blast_radius.corpus())
        | {EVENT, EVENT.rstrip("/")}
        | {url for url, _why in NEIGHBOURS}
    )
    try:
        readonly._ALLOWED_URL_PATTERNS = tuple(
            p for p in original if p is not carriers[0]
        )
        result = blast_radius.newly_admitted(carriers[0].pattern, corpus)
    finally:
        readonly._ALLOWED_URL_PATTERNS = original
    expected = {EVENT, EVENT.rstrip("/")} | {
        u for u in blast_radius.corpus()
        if u.startswith(f"{B}/events/") and u[len(f"{B}/events/"):].strip("/").isdigit()
        and u[len(f"{B}/events/"):].strip("/").isascii()
    }
    assert sorted(result["newly_admitted"]) == sorted(expected), result["newly_admitted"]
    assert result["newly_refused"] == []


def test_the_line_names_nobody():
    """One class, and it is the closed, bounded run of the ten ASCII digits."""
    source = _carriers()[0].pattern
    for token in ("[^", ".*", ".+", r"\w", r"\d", "+", "(", "/in/"):
        assert token not in source, (token, source)
    assert "[0-9]{1,20}" in source, source
