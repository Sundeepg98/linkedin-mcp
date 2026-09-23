"""What the four Premium patterns bought -- and what the family spellings would.

Four anchored patterns joined ``_ALLOWED_URL_PATTERNS`` on 2026-09-20 for the
``premium-four`` wave, taking it 36 -> 40. The house form for a widening is
that the widening ships the test asserting its own limits --
``test_school_and_collections_boundary.py``, ``test_analytics_creator_boundary.py``,
``test_newsletter_route.py`` and ``test_company_page_boundary.py`` are the
precedents. A widening whose limits live only in a comment beside the pattern
is a promise; this is the instrument.

## TWO OF THESE FOUR SHIP NO READER, AND THIS FILE IS WHERE THAT IS CHECKABLE

``/jobs/collections/top-applicant`` and ``/jobs/collections/top-choice`` ship
with ``linkedin_server/job_collections.py``. ``/analytics/recruiter-views`` and
``/premium/profile-key-skills`` ship with nothing, deliberately -- the evidence
for a reader is unstable for the first and absent for the second. **An
admission that buys no row is a blast radius paid for nothing unless its limits
are pinned**, so the ones with no reader get MORE assertions here, not fewer.

## THE DENOMINATOR IS THE FINDING, AND IT IS NOT THE SHIPPED ONE

``scripts/blast_radius.py`` is the right instrument and it is imported rather
than reimplemented. Run over ITS OWN corpus, every candidate here and every
over-broad mutation of them measures **+0 -- including a bare ``.*`` wildcard
over ``/premium/``**. That corpus holds ZERO addresses under
``/jobs/collections/`` and ``/premium/``, and one under ``/analytics/``, so
there was nothing for a wildcard to hit. The instrument's own docstring names
the state: *"a tool that reports zero for everything is indistinguishable from
a broken one."*

So this file measures against ``tests/fixtures/synthetic/drawn_routes.txt`` --
every route shape a DRAWN ANCHOR produced across six live captures, reduced by
the shipped reducer, name-free, tracked. ``test_the_corpus_discriminates``
below is the assertion that keeps it honest: if that corpus ever stops
separating a narrow pattern from a wildcard, every ``+1`` in this file becomes
meaningless and the suite says so.

## THE SUBTRACTION, AND THE SCAR IT COMES FROM

Every measurement removes THIS WAVE'S OWN ENTRIES FIRST. Without that, each
candidate is measured against a roster that already admits it and reports a
smaller blast radius than it has. ``test_company_page_boundary.py`` records
that its probe made exactly this mistake on its first run; this wave's lead
reproduced it live while writing this file, which is why the helper below
asserts the removal count rather than trusting it.

Everything here is pure: no browser, no page, no fixture, no network.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re

import pytest

from linkedin_server import readonly

_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, _ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


blast_radius = _load("blast_radius", "scripts/blast_radius.py")
drawn_route_corpus = _load("drawn_route_corpus", "scripts/drawn_route_corpus.py")

BASE = "https://www.linkedin.com"

#: The four addresses admitted, and the pattern prefix each is recognised by
#: when this file needs to take it back off the roster.
ADMITTED = (
    (f"{BASE}/jobs/collections/top-applicant/", "top-applicant"),
    (f"{BASE}/jobs/collections/top-choice/", "top-choice"),
    (f"{BASE}/analytics/recruiter-views/", "recruiter-views"),
    (f"{BASE}/premium/profile-key-skills/", "profile-key-skills"),
)

#: THE NEIGHBOURS, and every one of them is a real place. These are the
#: addresses a family pattern would sweep in, named rather than implied.
NOT_BOUGHT = (
    # The roots themselves. A family pattern reaches all three.
    f"{BASE}/jobs/collections/",
    f"{BASE}/analytics/",
    f"{BASE}/premium/",
    f"{BASE}/jobs/",
    # Premium surfaces LinkedIn DRAWS on his own hub that nobody has argued
    # for. These are what `/premium/<class>/` would buy silently.
    f"{BASE}/premium/premium-perks/",
    f"{BASE}/premium/switcher/",
    f"{BASE}/premium/sb/explore/",
    # Collections nobody has opened, in LinkedIn's own naming style.
    f"{BASE}/jobs/collections/recommended-for-you/",
    f"{BASE}/jobs/collections/still-hiring/",
    # Sub-paths of the admitted addresses. None of the four takes one.
    f"{BASE}/jobs/collections/top-applicant/details/",
    f"{BASE}/analytics/recruiter-views/all/",
    f"{BASE}/premium/profile-key-skills/edit/",
    # Queries. None of the four takes one.
    f"{BASE}/jobs/collections/top-applicant/?start=25",
    # THE REAL DRAWN URL, added 2026-09-20 by the integration. The line below
    # it pinned `past_90_days`, WHICH LINKEDIN DOES NOT DRAW ON THIS ROUTE --
    # so the refusal this file asserted was of a url nobody can produce, and
    # the trap the allowlist entry describes at length was not actually
    # tested. The token here is read off two rendered `<a>` anchors and is
    # carried verbatim, twice each, by two TRACKED fixtures
    # (tests/fixtures/profile_views_analytics.html and its _hydrated sibling),
    # so this assertion survives a clone. Both spellings, because the entry's
    # comment asserts both.
    f"{BASE}/analytics/recruiter-views/?timeRange=WvmpSearchFilterTimeRange_LAST_90_DAYS",
    f"{BASE}/analytics/recruiter-views?timeRange=WvmpSearchFilterTimeRange_LAST_90_DAYS",
    # The guess, KEPT: it is still a url this gate must refuse, and keeping it
    # beside the real one is what stops the two being confused again.
    f"{BASE}/analytics/recruiter-views/?timeRange=past_90_days",
    # The analytics neighbour this repository refused by name.
    f"{BASE}/analytics/creator/",
    # And the surface the search-appearances entry says it deliberately did
    # not buy, restated so a later widening cannot quietly reach it.
    #
    # ``{BASE}/search/results/people/`` STOOD HERE UNTIL 2026-09-20 and is now
    # admitted -- **not by any widening this gate watches**, but by its own
    # ruling (`09f9961` section 6), landing with a name-free shaper and the
    # tool `linkedin_people_search_shape` in one commit. This entry's JOB is
    # unchanged: it exists so the PREMIUM-FOUR admission cannot reach the
    # search family. So it is replaced rather than deleted, by two spellings
    # that are still refused and that keep testing exactly that -- and the
    # replacement is STRICTLY STRONGER, because the sub-path is the spelling
    # that would address one PERSON rather than the page listing them.
    f"{BASE}/search/results/people/example-person-a1b2c3/",
    f"{BASE}/search/results/companies/?keywords=x",
)


def _corpus() -> list[str]:
    """The drawn-anchor corpus, from the TRACKED fixture.

    Read from disk rather than regenerated: ``_state/`` is gitignored and
    exists in neither a linked worktree nor a CI checkout, so a test that
    needed the captures could not run where it matters.
    """
    return drawn_route_corpus.corpus_from_file()


def _roster_without_this_wave() -> tuple:
    """The shipped roster with THIS WAVE'S FOUR ENTRIES REMOVED.

    THE SUBTRACTION IS THE WHOLE POINT -- see the module docstring. The count
    is asserted rather than trusted, because a helper that silently removed
    three of four would report a blast radius that is wrong in the reassuring
    direction.
    """
    tokens = tuple(token for _url, token in ADMITTED)
    kept = tuple(
        pattern for pattern in readonly._ALLOWED_URL_PATTERNS
        if not any(token in pattern.pattern for token in tokens)
    )
    assert len(kept) == len(readonly._ALLOWED_URL_PATTERNS) - len(ADMITTED), (
        "this wave's entries were not all found on the roster, so every "
        "measurement in this file would be taken against the wrong baseline"
    )
    return kept


def _admits(roster: tuple, url: str) -> bool:
    """The real predicate's two gates, in the real order, against a roster this
    test supplies. ``is_read_url`` reads the module tuple, so it cannot answer
    a question about a hypothetical roster."""
    lowered = url.lower()
    if any(s in lowered for s in readonly._FORBIDDEN_URL_SUBSTRINGS):
        return False
    return any(pattern.match(url) for pattern in roster)


def _newly_admitted(candidate: str, corpus: list[str]) -> list[str]:
    """What ``candidate`` adds to the roster WITHOUT this wave's entries."""
    roster = _roster_without_this_wave()
    before = {url: _admits(roster, url) for url in corpus}
    with_candidate = roster + (re.compile(candidate),)
    after = {url: _admits(with_candidate, url) for url in corpus}
    return sorted(url for url in corpus if after[url] and not before[url])


# ---------------------------------------------------------------------------
# 1. The addresses the patterns were bought for
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("url,_token", ADMITTED)
def test_each_admitted_address_reads_allowed(url, _token):
    """Through the SHIPPED predicate rather than a re-implementation -- the
    standing rule after a lead wrote its own exact-value check twice and got
    it wrong twice: when the repository ships an instrument, import it."""
    assert readonly.is_read_url(url) is True, url
    assert readonly.is_read_url(url.rstrip("/")) is True, url


@pytest.mark.parametrize("url,_token", ADMITTED)
def test_each_admitted_address_is_admitted_by_exactly_one_pattern(url, _token):
    """Two matching patterns means one is broader than its comment claims, and
    the survivor test below would then pass while proving nothing."""
    matching = [p.pattern for p in readonly._ALLOWED_URL_PATTERNS if p.match(url)]
    assert len(matching) == 1, matching


@pytest.mark.parametrize("url,_token", ADMITTED)
def test_the_allowlist_anchor_is_the_only_thing_standing(url, _token):
    """SHOWN FAILING: remove the entries and every address refuses again.

    ``_forbidden_hits`` is asserted empty FIRST. If a forbidden substring were
    doing the refusing, this would pass with the patterns deleted and mean
    nothing at all -- which is precisely the state ``/jobs/alerts/``'s
    neighbours are in, and why that entry's comment has to say so.
    """
    hits = [s for s in readonly._FORBIDDEN_URL_SUBSTRINGS if s in url.lower()]
    assert hits == [], (
        f"gate one already refuses {url!r}, so this test would pass for the "
        "wrong reason"
    )
    assert not _admits(_roster_without_this_wave(), url), (
        f"{url!r} is admitted by something other than its own entry"
    )


@pytest.mark.parametrize("url,_token", ADMITTED)
def test_no_exemption_table_was_needed_or_touched(url, _token):
    """An admission that arrived through an exemption is a different and much
    wider change than one that arrived through a pattern."""
    assert url.lower() not in readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS
    assert not any(
        pattern.match(url)
        for pattern, _reason in readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS
    )


# ---------------------------------------------------------------------------
# 2. What the entries did not buy
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("url", NOT_BOUGHT)
def test_the_neighbours_stay_refused(url):
    assert readonly.is_read_url(url) is False, url


def test_no_sub_path_of_any_admitted_address_is_reachable():
    """Stated as a property over the four rather than as four cases, so a
    fifth entry added later without a sub-path test fails here."""
    for url, _token in ADMITTED:
        for tail in ("details/", "edit/", "all/", "new/", "1234567890/"):
            assert readonly.is_read_url(url + tail) is False, url + tail


def test_no_query_on_any_admitted_address_is_reachable():
    """None of the four is built with a query anywhere in this package, and a
    pattern that accepts one accepts whatever a caller appends."""
    for url, _token in ADMITTED:
        for query in ("?start=25", "?a=1", "?", "?action=delete"):
            assert readonly.is_read_url(url + query) is False, url + query


# ---------------------------------------------------------------------------
# 3. The blast radius, over a corpus that can actually see this wave
# ---------------------------------------------------------------------------


def test_the_corpus_is_the_tracked_one_and_is_not_empty():
    """AN EMPTY CORPUS MAKES EVERY MEASUREMENT BELOW REPORT ZERO, which is the
    exact state this whole file exists because of."""
    corpus = _corpus()
    assert len(corpus) >= 40, len(corpus)
    assert all(url.startswith(BASE) for url in corpus)
    assert all("<" not in url and ">" not in url for url in corpus), (
        "a placeholder reached the corpus; no allowlist regex can match one, "
        "so every verdict would be a false refusal"
    )


def test_the_corpus_discriminates_a_narrow_pattern_from_a_wildcard():
    """THE ASSERTION THAT KEEPS EVERY +1 IN THIS FILE MEANINGFUL.

    If this corpus ever stops separating these two, the numbers below are
    indistinguishable from a broken instrument's and the suite must say so
    rather than keep reporting reassuring zeros.
    """
    corpus = _corpus()
    narrow = _newly_admitted(
        r"^https://www\.linkedin\.com/premium/profile-key-skills/?$", corpus
    )
    wildcard = _newly_admitted(r"^https://www\.linkedin\.com/premium/.*$", corpus)
    assert len(narrow) == 1, narrow
    assert len(wildcard) > len(narrow), (narrow, wildcard)


def test_the_shipped_corpus_cannot_see_this_wave_and_that_is_recorded():
    """THE FINDING, PINNED SO IT CANNOT ROT INTO A FALSE REASSURANCE.

    If somebody later adds `/premium/` addresses to ``blast_radius.corpus()``,
    this test fails and the module docstring above has to be rewritten -- which
    is the correct outcome, because the reason this file carries its own corpus
    would no longer hold.
    """
    shipped = blast_radius.corpus()
    assert sum(1 for url in shipped if "/jobs/collections/" in url) == 0
    assert sum(1 for url in shipped if "/premium/" in url) == 0
    assert sum(1 for url in shipped if "/analytics/" in url) == 1
    # And the consequence, measured rather than asserted from the counts:
    assert _newly_admitted(r"^https://www\.linkedin\.com/premium/.*$", shipped) == []


@pytest.mark.parametrize("url,token", ADMITTED)
def test_each_entry_admits_exactly_its_own_address_and_nothing_else(url, token):
    """+1, and the one is itself."""
    escaped = re.escape(url.rstrip("/"))
    gained = _newly_admitted("^" + escaped + "/?$", _corpus())
    assert gained == [url], gained


@pytest.mark.parametrize(
    "candidate,at_least",
    [
        (r"^https://www\.linkedin\.com/jobs/collections/[A-Za-z0-9%\-_]{1,60}/?$", 2),
        (r"^https://www\.linkedin\.com/premium/[A-Za-z0-9%\-_]{1,60}/?$", 3),
        (r"^https://www\.linkedin\.com/premium/.*$", 4),
        (r"^https://www\.linkedin\.com/jobs/.*$", 3),
    ],
)
def test_the_family_spellings_are_shown_opening_more(candidate, at_least):
    """THE MUTATIONS, PLANTED AND SHOWN FIRING rather than described.

    A guard that has only ever passed certifies nothing. Each spelling below
    is one this wave deliberately did not use, and each is measured opening
    addresses LinkedIn DRAWS that no entry here bought -- ``/premium/`` reaches
    the perks page and the plan switcher, and the wildcard adds a sub-path on
    top.
    """
    gained = _newly_admitted(candidate, _corpus())
    assert len(gained) >= at_least, (candidate, gained)


def test_a_family_pattern_would_reach_premium_surfaces_nobody_argued_for():
    """NAMED, not counted. The two addresses are the concrete cost."""
    gained = _newly_admitted(
        r"^https://www\.linkedin\.com/premium/[A-Za-z0-9%\-_]{1,60}/?$", _corpus()
    )
    assert f"{BASE}/premium/premium-perks/" in gained
    assert f"{BASE}/premium/switcher/" in gained


# ---------------------------------------------------------------------------
# 4. The two that ship no reader
# ---------------------------------------------------------------------------


def test_the_two_reader_less_entries_have_no_reader_in_the_package():
    """ASSERTED, BECAUSE THE LEDGER CLAIM DEPENDS ON IT.

    ``_audit/2026-09-20-the-premium-four.md`` reports two of four admissions as
    buying no row. If somebody later lands a reader for either address without
    revisiting that ledger, this fails and points at the document.
    """
    package = _ROOT / "linkedin_server"
    sources = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in package.glob("*.py")
    )
    for address in ("/analytics/recruiter-views", "/premium/profile-key-skills"):
        navigating = re.findall(
            r'["\']https://www\.linkedin\.com' + re.escape(address) + r'/?["\']',
            sources,
        )
        assert navigating == [], (address, navigating)


def test_the_collections_reader_is_the_only_thing_that_builds_an_admitted_address():
    """The counterpart: the two that DO ship a reader are reachable from it,
    and the shaper and the boundary agree address for address."""
    from linkedin_server import job_collections

    built = {
        job_collections.collection_url(index)
        for index in range(len(job_collections.COLLECTIONS))
    }
    # THE THIRD ADDRESS IS NOT ONE OF THIS WAVE'S FOUR, and it is named so the
    # equality stays EXACT rather than loosening to a subset: `recommended`
    # joined `job_collections.COLLECTIONS` on 2026-09-23 (census J 39), at the
    # address admitted 2026-09-05 and loaded by `linkedin_job_collections`.
    from linkedin_server import collections_page

    assert built == (
        {url for url, _token in ADMITTED[:2]} | {collections_page.COLLECTIONS_URL}
    )
    for url in built:
        assert readonly.is_read_url(url) is True, url


# ---------------------------------------------------------------------------
# 5. The roster as a whole
# ---------------------------------------------------------------------------


def test_the_roster_grew_by_exactly_four():
    """THE DELTA, WHICH IS WHAT THIS TEST'S NAME PROMISES.

    IT WAS WRITTEN AS TWO ABSOLUTE COUNTS -- ``== 40`` and ``== 36`` -- and
    those were a proxy for "36 + 4" that only held while this wave's own base
    was the shipped roster. It stopped holding the moment the wave was merged:
    the `live-capture` wave had admitted `/jobs/jam` to master in parallel, so
    the integrated roster is 41 and the roster without this wave is 37. Both
    assertions went red on a merge that had weakened nothing at all.

    A COUNT THAT ANY UNRELATED WAVE CAN BREAK IS NOT MEASURING THIS WAVE.
    The subtraction below is, and it is invariant under other admissions. The
    protection the absolute was really carrying -- that the helper found all
    four entries rather than silently three -- lives inside
    ``_roster_without_this_wave`` itself and is untouched, and the roster's
    total size is pinned, with its argument, by
    ``tests/test_readonly_boundary_invariant.py``.
    """
    grew_by = len(readonly._ALLOWED_URL_PATTERNS) - len(_roster_without_this_wave())
    assert grew_by == len(ADMITTED) == 4, grew_by


def test_every_admitted_address_still_carries_no_member_segment():
    """The property every entry's comment claims for itself, checked once over
    all four rather than trusted four times.

    A member-bearing prefix followed by anything is what makes an address able
    to name a person, and ``linkedin_who_viewed_me`` has MEASURED that loading
    a third party's page leaves them a durable record.
    """
    member_bearing = ("/in/", "/company/", "/school/", "/pub/", "/profile/",
                      "/newsletters/", "/organization/", "/showcase/")
    for url, _token in ADMITTED:
        for prefix in member_bearing:
            assert prefix not in url, (url, prefix)
