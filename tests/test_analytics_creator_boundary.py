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
        # `/analytics/creator/audience/` STOOD HERE UNTIL 2026-09-23, as "A
        # SIBLING LINKED FROM THE ADMITTED PAGE ... a reason to CONSIDER an
        # address, never a reason to have admitted it". Lane L1 considered it
        # and ADMITTED it on its own line in readonly.py, with its own
        # argument and its own blast radius (`tests/test_l1_self_scoped_
        # admissions.py`). The line is removed rather than edited, exactly as
        # the recruiter-views line below was, so nobody reads a refusal this
        # file no longer makes. Its QUERY and SUB-PATH spellings replace it:
        # still refused, and still facts about this tree's discipline.
        (
            "https://www.linkedin.com/analytics/creator/audience/?x=1",
            "THE NEWLY ADMITTED SIBLING WITH A QUERY -- its entry takes none",
        ),
        (
            "https://www.linkedin.com/analytics/creator/audience/detail/",
            "THE NEWLY ADMITTED SIBLING WITH A SUB-PATH -- its entry takes none",
        ),
        (
            "https://www.linkedin.com/analytics/creator/top-posts/",
            "THE OTHER SIBLING DRAWN ON THE CONTENT PAGE. Being drawn is a "
            "reason to CONSIDER an address, never a reason to have admitted "
            "it -- and nobody has argued for this one",
        ),
        # BOTH SPELLINGS ARE KEPT. The wave and the integration each replaced
        # the old row independently -- with the SUB-PATH and with the QUERY --
        # and they are different facts about the same entry: it takes no
        # sub-path, and it takes no query. Neither subsumes the other.
        # ``/analytics/recruiter-views/`` STOOD HERE UNTIL 2026-09-20, as
        # "DRAWN BY THE PROFILE-VIEWS PAGE, twice, and not admitted". It is
        # now ADMITTED, by the `premium-four` wave, on its own anchored
        # pattern and with the argument on the entry in readonly.py -- so the
        # case moved rather than being deleted: this file's job is to pin what
        # the CREATOR-CONTENT pattern does and does not carry, and the
        # address's refusal is no longer one of those facts.
        #
        # WHAT REPLACES IT IS STRONGER, and it is the line below plus
        # test_the_refusals_are_not_carried_by_this_pattern: recruiter-views
        # is asserted there to be admitted by ITS OWN entry and by nothing
        # here. The sibling that is still refused, and still drawn, keeps the
        # case honest.
        (
            "https://www.linkedin.com/analytics/recruiter-views/all/",
            "A SUB-PATH of the newly admitted page -- the entry takes none",
        ),
        # `/analytics/recruiter-views/` WAS ON THIS TABLE FROM 2026-09-05 TO
        # 2026-09-20, with the reason "DRAWN BY THE PROFILE-VIEWS PAGE, twice,
        # and not admitted". IT IS NOW ADMITTED, by the `premium-four` wave,
        # and the line is removed rather than edited so that nobody reads a
        # refusal this file no longer makes.
        #
        # THE ROW WAS NOT WRONG AND IS NOT BEING OVERRULED. Its own reason
        # said the address was CONSIDERED and not argued for -- "being drawn
        # by an admitted page is a reason to CONSIDER an address, never a
        # reason to have admitted it -- one named page at a time, never the
        # family". The new entry supplies precisely the missing half: its own
        # named argument, its own blast-radius measurement, and a reader
        # costed and DECLINED. The argument is on the entry in
        # `linkedin_server/readonly.py`; the integration that moved this line
        # is `_audit/2026-09-20-the-premium-integration.md`.
        #
        # WHAT REPLACES IT HERE is the query spelling, which this file can
        # still legitimately refuse -- the entry is anchored with no query
        # allowance, and the url LinkedIn actually draws carries one.
        (
            "https://www.linkedin.com/analytics/recruiter-views/"
            "?timeRange=WvmpSearchFilterTimeRange_LAST_90_DAYS",
            "THE ADDRESS IS NOW ADMITTED BUT THIS SPELLING IS NOT. It is the "
            "exact href the profile-views page draws, twice; the entry is "
            "anchored with no query group, so the site's own url is refused "
            "by our gate. Deliberate, documented on the entry, and pinned "
            "here so the trap is tested rather than only described",
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
        # `/analytics/creator/audience/` was here until 2026-09-23 and is now
        # ADMITTED by its own entry (lane L1), so it can no longer be asserted
        # refused with only the creator-content pattern removed. Its SUB-PATH
        # stands in, and the admitted page itself is asserted below to be
        # carried by its own line and not by this one.
        "https://www.linkedin.com/analytics/creator/audience/detail/",
        # BOTH SPELLINGS ARE KEPT. The wave and the integration each replaced
        # the old row independently -- with the SUB-PATH and with the QUERY --
        # and they are different facts about the same entry: it takes no
        # sub-path, and it takes no query. Neither subsumes the other.
        # ``/analytics/recruiter-views/`` was in this list until 2026-09-20
        # and has been ADMITTED since, on its own entry. Its SUB-PATH stands
        # in for it: still refused, still under the same tree, and it keeps
        # this control measuring the same thing it always did.
        "https://www.linkedin.com/analytics/recruiter-views/all/",
        # `/analytics/recruiter-views/` was here until 2026-09-20 and is now
        # ADMITTED by its own entry, so it can no longer be asserted refused
        # with only the creator-content pattern removed. The QUERY spelling
        # replaces it: still refused, and refused for a reason that has
        # nothing to do with the pattern this control removes.
        "https://www.linkedin.com/analytics/recruiter-views/"
        "?timeRange=WvmpSearchFilterTimeRange_LAST_90_DAYS",
    ):
        assert not allowed_without(url), url

    # AND THE ADMITTED SIBLING IS ASSERTED TO BE CARRIED BY ITS OWN ENTRY,
    # NOT BY THIS ONE. Without this, removing the creator-content pattern
    # could silently be what admits it and nothing here would notice.
    recruiter = "https://www.linkedin.com/analytics/recruiter-views/"
    assert readonly.is_read_url(recruiter) is True, recruiter
    assert allowed_without(recruiter), (
        "recruiter-views stopped being admitted once the creator-content "
        "pattern was removed, which would mean THAT pattern is what carries "
        "it -- i.e. it is far broader than its comment claims"
    )
    matching = [
        pattern for pattern in readonly._ALLOWED_URL_PATTERNS
        if pattern.match(recruiter)
    ]
    assert len(matching) == 1, matching
    assert "recruiter-views" in matching[0].pattern, matching[0].pattern

    # THE SAME, FOR THE SIBLING ADMITTED 2026-09-23. The audience page must be
    # carried by its OWN entry: if removing the creator-content pattern were
    # what refused it, that pattern would be far broader than it claims.
    audience = "https://www.linkedin.com/analytics/creator/audience/"
    assert readonly.is_read_url(audience) is True, audience
    assert allowed_without(audience), audience
    carriers = [
        pattern for pattern in readonly._ALLOWED_URL_PATTERNS
        if pattern.match(audience)
    ]
    assert len(carriers) == 1, carriers
    assert "creator/audience" in carriers[0].pattern, carriers[0].pattern


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

    The newsletters analytics path the census names beside these rows is
    refused and stays refused. An entry that quietly widened it would be the
    failure this repository has written down more than once: a load argued for
    one purpose reaching a second surface nobody ruled on.

    **``/search/results/people/`` WAS THE FIRST ADDRESS HERE AND IS NOW
    ADMITTED, AND THIS TEST STILL MEANS WHAT IT MEANT.** It was admitted
    2026-09-20 under `09f9961` section 6 -- its own ruling, its own blast
    radius, and a name-free shaper in the same commit -- and NOT by anything
    the creator-analytics entries reach. The thing this test forbids is a
    creator-analytics load being the argument that opens a second surface;
    that did not happen, so the case is REPLACED by search-family spellings
    that are still refused rather than deleted. The sub-path is the sharper
    one: it is the spelling that would address a PERSON, and the admitted
    pattern takes no sub-path.
    """
    for url in (
        "https://www.linkedin.com/search/results/people/example-person-a1b2c3/",
        "https://www.linkedin.com/search/results/companies/?keywords=x",
        "https://www.linkedin.com/analytics/creator/newsletters/",
    ):
        assert not _allowed(url), url


def test_the_admitted_analytics_pages_are_exactly_three():
    """A COUNT, so an analytics page cannot arrive unnoticed.

    **THE NAME IS NOW OFF BY ONE AND IS KEPT ANYWAY.** It reads "three" and
    the answer is four pages over five patterns. Renaming it would rot a
    citation: ``_audit/2026-09-20-newsletter-built.md`` quotes this function
    by name, and this repository has a standing finding that a citation rots
    into a PLAUSIBLE WRONG ANSWER rather than a dangling one. The number lives
    in the assertion, where it is checked; the name is an address.

    Profile views (both spellings), search appearances, creator content, and
    -- since 2026-09-20 -- recruiter views. The ``/me/profile-views/``
    spelling is what makes it five PATTERNS over four PAGES, and the split is
    stated rather than smoothed over because a reader checking this number
    will otherwise find it off by one and assume drift.

    **IT DID ITS JOB.** Its docstring said a fourth analytics page could not
    arrive unnoticed, and when one did -- admitted by the `premium-four` wave
    two commits earlier -- this is the assertion that stopped it, in CI, on
    all three platform cells, after a local gate had missed it.

    A COUNT LIKE THIS IS RAISED, NEVER LOOSENED -- not replaced by a bound
    and never bumped silently, so the next arrival costs the same
    conversation this one did. The integration that merged the wave records
    the raise at `_audit/2026-09-20-the-premium-integration.md` section 3.

    **RAISED AGAIN 2026-09-23, FROM FIVE TO SEVEN PATTERNS**, by lane L1:
    the audience page (census ``P L1``) and ONE post's analytics by its
    activity urn (``P G6``, ``M C38``), each on its own anchored line with
    its own argument and a blast radius of +2, pinned in
    ``tests/test_l1_self_scoped_admissions.py``. It is the same
    conversation the last raise had, held in
    ``_audit/2026-09-23-lane-l1-refused-reads.md``. The analytics HUB that
    lane also admitted is ``/dashboard/``, which this count's pattern does
    not match, and it is named there rather than smuggled in here.
    """
    analytics = [
        pattern.pattern
        for pattern in readonly._ALLOWED_URL_PATTERNS
        if re.search(r"analytics|profile-views", pattern.pattern)
    ]
    assert len(analytics) == 7, analytics
    # AND THE PAGES, NAMED, so the count cannot be satisfied by a duplicate.
    assert sum("recruiter-views" in p for p in analytics) == 1, analytics
    assert sum("creator/content" in p for p in analytics) == 1, analytics
    assert sum("search-appearances" in p for p in analytics) == 1, analytics
    assert sum("profile-views" in p for p in analytics) == 2, analytics
    assert sum("creator/audience" in p for p in analytics) == 1, analytics
    assert sum("post-summary" in p for p in analytics) == 1, analytics
