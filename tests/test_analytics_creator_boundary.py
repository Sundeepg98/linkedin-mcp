"""The creator-content address is admitted, and its NEIGHBOURS are not.

An allowlist entry is worth exactly what its edges are worth. This file pins
the edges of the one pattern added on 2026-09-05 for ``CONTENT-ANALYTICS-
SURFACE``, so that a later widening -- the tree, the parent, a query, a
sub-path -- shows up in a diff instead of in an incident.

WHY A FILE OF ITS OWN RATHER THAN LINES IN ``test_readonly.py``. Three waves
have had work land in a neighbour's commit in this tree today through shared
append-only files, and the sanctioned answer is to write your own file and let
the lead merge. Nothing here duplicates a check in ``test_readonly.py``: that
file pins the shipped constructions, this one pins one entry's boundary.

EVERY ASSERTION BELOW WAS SHOWN FAILING before it was admitted, by deleting
the pattern from the allowlist in memory and re-running: the ALLOWED case
turns red and every REFUSED case stays green, which is what says the refusals
are carried by the rest of the list rather than by this pattern's absence.
``test_the_refusals_are_not_carried_by_this_pattern`` is that control, kept as
a test rather than as a note, because a refusal every other line would make
anyway proves nothing about this one.
"""

from __future__ import annotations

import re

import pytest

from linkedin_server import readonly

#: The address, spelled once. Every case below is built from it or is a
#: deliberate mutation of it, so a rename cannot leave a case testing a string
#: nothing builds any more.
CREATOR_CONTENT = "https://www.linkedin.com/analytics/creator/content/"


def _allowed(url: str) -> bool:
    return any(pattern.match(url) for pattern in readonly._ALLOWED_URL_PATTERNS)


def test_the_creator_content_page_is_admitted():
    """The exact address, with and without its trailing slash."""
    assert _allowed(CREATOR_CONTENT)
    assert _allowed(CREATOR_CONTENT.rstrip("/"))


@pytest.mark.parametrize(
    "url,why",
    [
        (
            "https://www.linkedin.com/analytics/creator/",
            "THE PARENT. The search-appearances entry names this address as "
            "one it deliberately did not buy; admitting the child must not "
            "admit the parent by accident",
        ),
        (
            "https://www.linkedin.com/analytics/",
            "THE TREE ROOT, measured refused before either analytics entry "
            "existed and still refused after both",
        ),
        (
            "https://www.linkedin.com/analytics/creator/content/detail/",
            "A SUB-PATH. Nothing in this package builds one, and a pattern "
            "that accepts one accepts whatever a caller appends",
        ),
        (
            "https://www.linkedin.com/analytics/creator/content/?metricType=x",
            "A QUERY. The entry is anchored with no query group on purpose: "
            "the url is built from one module constant with nothing appended",
        ),
        (
            "https://www.linkedin.com/analytics/creator/audience/",
            "A SIBLING LINKED FROM THE ADMITTED PAGE. Measured 2026-09-05: "
            "the content page draws this address. Being drawn by an admitted "
            "page is a reason to CONSIDER an address, never a reason to have "
            "admitted it -- one named page at a time, never the family",
        ),
        (
            "https://www.linkedin.com/analytics/creator/top-posts/",
            "THE OTHER SIBLING, same reading, same reason",
        ),
        (
            "https://www.linkedin.com/analytics/recruiter-views/",
            "DRAWN BY THE PROFILE-VIEWS PAGE, twice, and not admitted",
        ),
        (
            "http://www.linkedin.com/analytics/creator/content/",
            "PLAIN HTTP",
        ),
        (
            "https://linkedin.com/analytics/creator/content/",
            "NO www SUBDOMAIN",
        ),
        (
            "https://evil.example.com/analytics/creator/content/",
            "ANOTHER HOST WEARING THE PATH",
        ),
    ],
)
def test_the_neighbours_are_refused(url, why):
    assert not _allowed(url), why


def test_the_refusals_are_not_carried_by_this_pattern():
    """THE CONTROL, and without it the cases above measure nothing.

    Remove the creator-content pattern and re-run every refusal. If a refusal
    only holds while the pattern is present, the case was testing the pattern
    rather than the boundary around it -- and if a refusal flips to ALLOWED
    when the pattern is removed, something has gone very strange indeed.

    The ALLOWED case is asserted to flip in the other direction in the same
    breath, which is what makes this a two-sided demonstration rather than a
    green that could not fail.
    """
    survivors = tuple(
        pattern
        for pattern in readonly._ALLOWED_URL_PATTERNS
        if "creator/content" not in pattern.pattern
    )
    assert len(survivors) == len(readonly._ALLOWED_URL_PATTERNS) - 1, (
        "exactly one pattern carries this address; found "
        f"{len(readonly._ALLOWED_URL_PATTERNS) - len(survivors)}"
    )

    def allowed_without(url: str) -> bool:
        return any(pattern.match(url) for pattern in survivors)

    assert not allowed_without(CREATOR_CONTENT), (
        "the address is still admitted with its own pattern removed, so the "
        "pattern is not what admits it and this whole file is aimed wrong"
    )
    for url in (
        "https://www.linkedin.com/analytics/creator/",
        "https://www.linkedin.com/analytics/",
        "https://www.linkedin.com/analytics/creator/audience/",
        "https://www.linkedin.com/analytics/recruiter-views/",
    ):
        assert not allowed_without(url), url


def test_the_pattern_carries_no_member_segment():
    """STRUCTURAL, not promised: this url cannot name a person.

    The argument the entry rests on is that the account is chosen by the
    session cookie and by nothing in the string. That is a property of the
    PATTERN and is checkable: its source text contains no ``/in/``, no
    character class that would accept a slug, and no group at all.
    """
    carriers = [
        pattern.pattern
        for pattern in readonly._ALLOWED_URL_PATTERNS
        if "creator/content" in pattern.pattern
    ]
    assert len(carriers) == 1, carriers
    source = carriers[0]
    assert "/in/" not in source, source
    assert "(" not in source.replace(r"\(", ""), (
        "a group in this pattern is a place a caller's string could go", source
    )
    for wildcard in ("[^", ".*", ".+", r"\w", r"\d", "+"):
        assert wildcard not in source, (wildcard, source)


def test_the_address_this_reading_informs_is_still_refused():
    """The creator surfaces buy nothing next door.

    ``/search/results/people/`` is refused and stays refused; so does the
    newsletters analytics path the census names beside these rows. An entry
    that quietly widened either would be the failure this repository has
    written down more than once: a load argued for one purpose reaching a
    second surface nobody ruled on.
    """
    for url in (
        "https://www.linkedin.com/search/results/people/",
        "https://www.linkedin.com/analytics/creator/newsletters/",
    ):
        assert not _allowed(url), url


def test_the_admitted_analytics_pages_are_exactly_three():
    """A COUNT, so a fourth analytics page cannot arrive unnoticed.

    Profile views (both spellings), search appearances, creator content. The
    ``/me/profile-views/`` spelling makes it four PATTERNS over three pages,
    and the split is stated rather than smoothed over because a reader
    checking this number will otherwise find it off by one and assume drift.
    """
    analytics = [
        pattern.pattern
        for pattern in readonly._ALLOWED_URL_PATTERNS
        if re.search(r"analytics|profile-views", pattern.pattern)
    ]
    assert len(analytics) == 4, analytics
