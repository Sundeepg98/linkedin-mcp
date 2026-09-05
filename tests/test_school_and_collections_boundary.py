"""What the school and job-collection patterns bought -- and what they did NOT.

Two anchored patterns joined ``_ALLOWED_URL_PATTERNS`` on 2026-09-05, one per
surface, for census rows 40 (``SCHOOL-PAGE-SURFACE``) and 75
(``JOB-COLLECTIONS-SURFACE``). The ruling behind them is recorded in
``_audit/2026-09-05-cheap-reads.md`` section 12 and applied here rather than
re-sought.

WHY A FILE OF ITS OWN, rather than three lines added to ``test_readonly.py``.
The house form for a widening is that the widening ships the test asserting
its own limits -- ``test_analytics_creator_boundary.py`` and
``test_newsletter_route.py`` are the precedents. A widening whose limits live
only in a comment beside the pattern is a promise; this is the instrument.

THE TRAP THIS FILE EXISTS TO SIT ON. The wave lead's standing boundary trap
says a broad settings-FAMILY pattern would admit the most expensive
irreversible act on the platform as a side effect of a tidy refactor, with
nothing in the diff naming it. Neither pattern here is a family pattern, and
that claim is asserted below rather than asserted in prose -- including by
PLANTING the family pattern and showing it admitting account deletion, so the
guard is one that has been seen firing rather than one that has only ever
passed.

A SHARPENING OF THAT TRAP, MEASURED AT THIS TREE AND NOT INHERITED. The trap
is stated about ``close-account``. Measured with the shipped predicate:

    /mypreferences/d/close-accounts   PLURAL    forbidden substring hit, AND no pattern
    /mypreferences/d/close-account    SINGULAR  NO forbidden substring, no pattern
    /mypreferences/d/account-closure            NO forbidden substring, no pattern

So the plural spelling has two gates and the singular has ONE. The trap is
real and it is narrower than its headline: the addresses a family pattern
would actually open are the spellings the denylist never learned. That is
this repository's own recurring shape -- a list anchored to the spellings
somebody happened to meet -- and it is the reason the mutation below plants
the SINGULAR form.
"""
from __future__ import annotations

import re

from linkedin_server import readonly

BASE = "https://www.linkedin.com"

#: The two addresses these patterns were admitted for.
SCHOOL_URL = f"{BASE}/school/example-university/"
COLLECTIONS_URL = f"{BASE}/jobs/collections/recommended/"

#: What the two entries DELIBERATELY DID NOT BUY.
#:
#: Each of these is a real neighbour of an admitted address, not a synthetic
#: near-miss: the school tabs are drawn by the school Page itself, the other
#: collections are drawn by the collections rail, and the parents are one
#: path segment up from something now open. A pattern is narrow only if the
#: things beside it stay shut.
NOT_BOUGHT = (
    # The school Page's own tabs. ``/people/`` is the load-bearing one: it is
    # a roster of MEMBERS, which is the one place under this root where the
    # member-profile cause the ruling turns on could start to apply again.
    f"{BASE}/school/example-university/people/",
    f"{BASE}/school/example-university/jobs/",
    f"{BASE}/school/example-university/posts/",
    f"{BASE}/school/example-university/about/",
    # A query, which is where a filter naming a person would arrive.
    f"{BASE}/school/example-university/?foo=1",
    # The parent, and the bare root.
    f"{BASE}/school/",
    f"{BASE}/school",
    # A dotted segment. Refused because ``.`` is outside the character class,
    # and the reason is normalisation rather than taste: ``..`` is normalised
    # away by the browser, turning an admitted address into another page.
    f"{BASE}/school/ex..ample/",
    f"{BASE}/school/../in/someone/",
    # Two segments, which would be a tab under another spelling.
    f"{BASE}/school/example-university/a/",
    # The collections family, which is NOT bought. LinkedIn controls the
    # membership of this namespace, so a family pattern admits addresses that
    # do not exist yet and that nobody has read.
    f"{BASE}/jobs/collections/",
    f"{BASE}/jobs/collections/still-hiring/",
    f"{BASE}/jobs/collections/easy-apply/",
    f"{BASE}/jobs/collections/recommended/?x=1",
    f"{BASE}/jobs/collections/recommended/more/",
)

#: EVERY SPELLING OF ACCOUNT DELETION THIS REPOSITORY HAS MET OR CAN NAME.
#:
#: Two of these carry a forbidden substring and two do not, and the pair is
#: the whole point: a test that only planted the covered spelling would pass
#: for a reason unrelated to the patterns under test.
ACCOUNT_ENDING_URLS = (
    f"{BASE}/mypreferences/d/close-accounts",
    f"{BASE}/mypreferences/d/close-accounts/",
    f"{BASE}/mypreferences/d/hibernate-account",
    f"{BASE}/mypreferences/d/close-account",
    f"{BASE}/mypreferences/d/close-account/",
    f"{BASE}/mypreferences/d/account-closure",
)

#: THE FAMILY PATTERN NOBODY MAY WRITE.
#:
#: This is the pattern a wave would naturally reach for to discharge seven
#: settings rows at once. It is defined here as a MUTATION -- it is not on
#: the boundary and the test below asserts that it is not -- so that the
#: cost of writing it is a measurement in this file rather than an argument
#: in a comment.
_SETTINGS_FAMILY_MUTATION = re.compile(
    r"^https://www\.linkedin\.com/mypreferences/d/[A-Za-z0-9\-]+/?$"
)


def _matching_patterns(url: str) -> list[str]:
    """Which allowlist entries match, by pattern text."""
    return [p.pattern for p in readonly._ALLOWED_URL_PATTERNS if p.match(url)]


def _forbidden_hits(url: str) -> list[str]:
    """Which forbidden substrings this url carries. Gate one, read directly."""
    return [s for s in readonly._FORBIDDEN_URL_SUBSTRINGS if s in url]


# ---------------------------------------------------------------------------
# 1. The two addresses the patterns were bought for
# ---------------------------------------------------------------------------


def test_the_two_admitted_addresses_read_allowed():
    """Both open, through the SHIPPED predicate rather than a re-implementation.

    The standing rule after a lead wrote its own exact-value check twice and
    got it wrong twice: when the repository already ships an instrument,
    import it.
    """
    assert readonly.is_read_url(SCHOOL_URL) is True
    assert readonly.is_read_url(COLLECTIONS_URL) is True
    # The slashless spellings, because the pattern makes the trailing slash
    # optional and a reader should not have to infer that from the regex.
    assert readonly.is_read_url(SCHOOL_URL.rstrip("/")) is True
    assert readonly.is_read_url(COLLECTIONS_URL.rstrip("/")) is True


def test_each_address_is_admitted_by_exactly_one_pattern():
    """One surface, one pattern -- and no accidental second admitter.

    An address matched by two patterns means one of them is broader than its
    comment claims, and the survivor test below would then pass while proving
    nothing.
    """
    assert len(_matching_patterns(SCHOOL_URL)) == 1, _matching_patterns(SCHOOL_URL)
    assert len(_matching_patterns(COLLECTIONS_URL)) == 1, _matching_patterns(
        COLLECTIONS_URL
    )


def test_the_new_patterns_are_the_only_thing_standing():
    """SHOWN FAILING: remove the entry and the address refuses again.

    A pattern that is not load-bearing is a pattern whose removal changes
    nothing, and a test that cannot tell those apart certifies nothing. This
    rebuilds the allowlist without each new entry and re-asks.

    ``is_read_url`` is not used here because it reads the module tuple; the
    two gates are applied by hand in the same order the real predicate applies
    them, which is why ``_forbidden_hits`` is asserted empty first -- if a
    forbidden substring were doing the refusing, this test would pass with the
    pattern deleted and mean nothing at all.
    """
    for url in (SCHOOL_URL, COLLECTIONS_URL):
        assert _forbidden_hits(url) == [], (
            f"gate one already refuses {url!r}, so this test would pass for "
            "the wrong reason"
        )
        mine = _matching_patterns(url)[0]
        survivors = [
            p for p in readonly._ALLOWED_URL_PATTERNS if p.pattern != mine
        ]
        assert len(survivors) == len(readonly._ALLOWED_URL_PATTERNS) - 1
        assert not any(p.match(url) for p in survivors), (
            f"{url!r} is admitted by something other than its own entry"
        )


# ---------------------------------------------------------------------------
# 2. What the two entries did not buy
# ---------------------------------------------------------------------------


def test_the_neighbours_stay_refused():
    """Fifteen addresses beside the two that opened, all still shut."""
    for url in NOT_BOUGHT:
        assert readonly.is_read_url(url) is False, url


def test_the_school_pattern_admits_one_path_segment_only():
    """The narrowness restated as a property rather than a list of examples.

    A list of neighbours can only ever cover the ones somebody thought of --
    this asserts the shape, so a future widening of the character class is
    caught even for a spelling nobody has met.
    """
    school = [
        p
        for p in readonly._ALLOWED_URL_PATTERNS
        if p.match(SCHOOL_URL)
    ][0]
    for tail in ("people", "jobs", "posts", "life", "admin", "a"):
        assert not school.match(f"{BASE}/school/example-university/{tail}/")
        assert not school.match(f"{BASE}/school/example-university/{tail}")
    assert not school.match(f"{BASE}/school/example-university/?q=1")
    assert not school.match(f"{BASE}/school//")


def test_the_collections_pattern_names_one_collection_and_not_the_family():
    """It is a NAMED address, not a namespace.

    Written as a property for the same reason as the test above: the set of
    collection names is LinkedIn's to change, so an example list cannot cover
    it and only the shape can.
    """
    collections = [
        p
        for p in readonly._ALLOWED_URL_PATTERNS
        if p.match(COLLECTIONS_URL)
    ][0]
    for name in ("still-hiring", "easy-apply", "top-applicant", "remote", "x"):
        assert not collections.match(f"{BASE}/jobs/collections/{name}/"), name
    assert not collections.match(f"{BASE}/jobs/collections/")


# ---------------------------------------------------------------------------
# 3. Account deletion, planted -- and the family pattern shown ADMITTING it
# ---------------------------------------------------------------------------


def test_every_account_ending_spelling_is_still_refused():
    """The plant. Six spellings, all refused, with the boundary as it ships."""
    for url in ACCOUNT_ENDING_URLS:
        assert readonly.is_read_url(url) is False, url


def test_neither_new_pattern_can_reach_account_deletion():
    """Stronger than the test above, and it is the one that survives a change.

    ``is_read_url`` returning False could be the work of any of the 31
    patterns or of gate one. This asks the narrower question these two entries
    are actually responsible for: does EITHER of them match an account-ending
    address? A future edit that widens one of them fails here even if some
    other gate happens to still refuse.
    """
    mine = [
        p
        for p in readonly._ALLOWED_URL_PATTERNS
        if p.match(SCHOOL_URL) or p.match(COLLECTIONS_URL)
    ]
    assert len(mine) == 2
    for pattern in mine:
        for url in ACCOUNT_ENDING_URLS:
            assert not pattern.match(url), (pattern.pattern, url)


def test_the_family_pattern_the_trap_names_does_admit_account_deletion():
    """THE MUTATION, and it is the reason this file exists.

    A guard that has only ever passed certifies nothing. This one is shown
    FIRING: the settings-family pattern a wave would naturally write to
    discharge seven rows at once is applied here to the account-ending
    addresses, and it MATCHES ALL SIX -- three of which carry no forbidden
    substring at all, so nothing else in the boundary would have stopped
    them.

    THE COUNTS WERE MEASURED, NOT PREDICTED, and the first version of this
    assertion was WRONG IN THE FLATTERING DIRECTION: it said four matched and
    two were undefended. The run said six and three. The author had forgotten
    that the hibernation address is a ``/mypreferences/d/`` sibling like the
    rest and that the trailing-slash spellings are separate strings. **The
    trap is 50 percent larger than the person writing its guard believed**,
    which is the argument for planting the mutation rather than reasoning
    about it.

    THE SPLIT IS THE FINDING, and it sharpens the trap as written:

        close-accounts    PLURAL     matched by the family pattern, but ALSO
                                     carries a forbidden substring -- two gates
        hibernate-account            same: matched, and also on the denylist
        close-account     SINGULAR   matched by the family pattern and carries
                                     NO forbidden substring -- ONE gate, and
                                     the family pattern removes it
        account-closure              same: matched, and undefended

    So the danger is not the spelling the denylist already learned. It is the
    sibling it never met.
    """
    matched = [u for u in ACCOUNT_ENDING_URLS if _SETTINGS_FAMILY_MUTATION.match(u)]
    assert matched, "the mutation matched nothing; it is not the pattern claimed"

    undefended = [u for u in matched if not _forbidden_hits(u)]
    assert undefended, (
        "every address the family pattern admits is also caught by gate one, "
        "which would make the trap harmless -- it is not, and this assertion "
        "is what would tell us the world had changed"
    )
    # The count is stated so a change in either direction is visible in a diff
    # rather than absorbed silently.
    assert len(matched) == 6, matched
    assert len(undefended) == 3, undefended


def test_the_family_pattern_is_not_on_the_boundary():
    """And it must never be. The mutation above is a local object only."""
    live = {p.pattern for p in readonly._ALLOWED_URL_PATTERNS}
    assert _SETTINGS_FAMILY_MUTATION.pattern not in live
    # No shipped pattern may admit any account-ending address, whoever wrote it.
    for url in ACCOUNT_ENDING_URLS:
        assert _matching_patterns(url) == [], (url, _matching_patterns(url))


# ---------------------------------------------------------------------------
# 4. What this change did NOT do to the rest of the boundary
# ---------------------------------------------------------------------------


def test_this_widening_bought_no_forbidden_substring_exemption():
    """An allowlist entry is not permission to carry a forbidden substring.

    Both admitted addresses carry none, so neither exemption table needed an
    entry -- and the assertion is that they did not GET one, because the
    cheapest way to make a stubborn address open is to reach for a table that
    was never part of the ruling.
    """
    assert _forbidden_hits(SCHOOL_URL) == []
    assert _forbidden_hits(COLLECTIONS_URL) == []
    keys = set(readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS)
    assert SCHOOL_URL not in keys and COLLECTIONS_URL not in keys
    for pattern, _substrings in readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS:
        assert not pattern.match(SCHOOL_URL), pattern.pattern
        assert not pattern.match(COLLECTIONS_URL), pattern.pattern


def test_a_slug_carrying_a_forbidden_substring_still_fails_closed():
    """Gate one is not excused, and the failure is the correct direction.

    A school whose slug contains one of the refused substrings refuses. That
    is a real limitation rather than a hypothetical -- it is recorded so the
    next reader meets it as a known, deliberate fail-closed rather than as a
    bug to route around by shortening a denylist, which is the most dangerous
    edit available in this package.
    """
    for slug in ("connect-institute", "invite-college", "follow-academy"):
        url = f"{BASE}/school/{slug}/"
        assert _forbidden_hits(url), slug
        assert readonly.is_read_url(url) is False, slug
