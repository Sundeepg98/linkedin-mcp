"""What the /company/ pattern bought -- and the four spellings that would
have bought far more.

One anchored pattern joined ``_ALLOWED_URL_PATTERNS`` on 2026-09-20 for
``COMPANY-PAGE-SURFACE``, the largest BUILD in the census. The ruling is
recorded on the entry itself and applied here rather than re-sought.

WHY A FILE OF ITS OWN, rather than lines added to ``test_readonly.py``. The
house form for a widening is that the widening ships the test asserting its
own limits -- ``test_school_and_collections_boundary.py``,
``test_analytics_creator_boundary.py`` and ``test_newsletter_route.py`` are
the precedents. A widening whose limits live only in a comment beside the
pattern is a promise; this is the instrument.

## THIS ROOT CARRIES TWO HAZARD CLASSES AND A FAMILY PATTERN OPENS BOTH

The standing boundary trap says a broad family pattern would admit the most
expensive irreversible act on the platform as a side effect of a tidy
refactor, with nothing in the diff naming it. On THIS root the trap has two
distinct faces, and both are planted below rather than argued:

    /company/<x>/people/       A MEMBER ROSTER. Census rows J 108 and N 102,
                               out of scope by the same ruling that put a
                               group's roster out of scope by name.
    /company/setup/new/        THE FLOW THAT CREATES A PAGE, plus
    /company/<x>/admin/        Page ADMINISTRATION.

**NONE OF THOSE THREE WRITE SURFACES CARRIES A FORBIDDEN SUBSTRING.** The
denylist holds ``/create`` and LinkedIn does not spell Page creation with it.
They are refused by the allowlist anchor and by nothing else, which is
asserted below and is the sharpest thing this file has to say.

## AND THREE CHARACTER-CLASS MUTATIONS, EACH SHOWN OPENING SOMETHING

A guard that has only ever passed certifies nothing, so this file plants the
three spellings the entry deliberately did not use -- the bare digit escape,
a dot inside the class, and the family wildcard -- and measures what each one
admits that the shipped entry does not.

Everything here is pure: no browser, no page, no fixture, no network.
"""
from __future__ import annotations

import re

import pytest

from linkedin_server import readonly

BASE = "https://www.linkedin.com"

#: The addresses the pattern was admitted for, in both spellings LinkedIn
#: serves. The numeric id is the one ``tests/fixtures/notifications.html``
#: carries; the slug is synthetic and in the spelling this repository's
#: corpora already use.
SLUG = "a-company"
IDENTIFIER = "5417062"
PAGE_URL = f"{BASE}/company/{SLUG}/"
PAGE_URL_NUMERIC = f"{BASE}/company/{IDENTIFIER}/"

#: THE THREE WRITE SURFACES UNDER THIS ROOT. Named separately from the rest
#: because they are the ones defended by NOTHING but this anchor, which is a
#: different and louder fact than "a neighbour stayed shut".
WRITE_SURFACES = (
    f"{BASE}/company/setup/new/",
    f"{BASE}/company/{SLUG}/admin/",
    f"{BASE}/company/{SLUG}/admin/dashboard/",
)

#: THE MEMBER ROSTER, in both spellings. Out of scope BY NAME.
ROSTERS = (
    f"{BASE}/company/{SLUG}/people/",
    f"{BASE}/company/{IDENTIFIER}/people/",
    f"{BASE}/company/{SLUG}/people/?keywords=x",
)

#: What the entry DELIBERATELY DID NOT BUY. Each is a real neighbour of the
#: admitted address -- the tabs are drawn by the Page itself, the traversals
#: are the class measured normalising onto an account-ending address -- rather
#: than a synthetic near-miss. A pattern is narrow only if the things beside
#: it stay shut.
NOT_BOUGHT = WRITE_SURFACES + ROSTERS + (
    # Every other tab, each a census row this admission did not close.
    f"{BASE}/company/{SLUG}/about/",
    f"{BASE}/company/{SLUG}/jobs/",
    f"{BASE}/company/{SLUG}/life/",
    f"{BASE}/company/{SLUG}/posts/",
    f"{BASE}/company/{SLUG}/products/",
    f"{BASE}/company/{SLUG}/services/",
    f"{BASE}/company/{SLUG}/insights/",
    f"{BASE}/company/{SLUG}/insights/?insightType=HEADCOUNT",
    f"{BASE}/company/{SLUG}/events/",
    f"{BASE}/company/{SLUG}/videos/",
    # A query on the admitted root, which is where a filter naming a person
    # would arrive.
    f"{BASE}/company/{SLUG}/?foo=1",
    f"{BASE}/company/{SLUG}/?trk=x",
    # The parent and the bare root, which are not a Page.
    f"{BASE}/company/",
    f"{BASE}/company",
    # Traversals. The first normalises onto an ACCOUNT-ENDING address and the
    # second onto a member profile, and no forbidden substring names either.
    f"{BASE}/company/{SLUG}/../../mypreferences/d/close-account",
    f"{BASE}/company/{SLUG}/../../in/someone-else/",
    f"{BASE}/company/../mypreferences/d/",
    # Dotted segments, refused because the dot is outside the character class.
    f"{BASE}/company/a.company/",
    f"{BASE}/company/a..company/",
    f"{BASE}/company/./",
    # A urn spelling.
    f"{BASE}/company/urn:li:organization:12345/",
)

#: THE THREE SPELLINGS NOBODY MAY WRITE, defined here as MUTATIONS -- none is
#: on the boundary and the tests below assert that -- so the cost of writing
#: one is a measurement in this file rather than an argument in a comment.
_FAMILY_MUTATION = re.compile(r"^https://www\.linkedin\.com/company/.*$")
_DIGIT_ESCAPE_MUTATION = re.compile(
    r"^https://www\.linkedin\.com/company/\d+/?$"
)
_DOTTED_CLASS_MUTATION = re.compile(
    r"^https://www\.linkedin\.com/company/[A-Za-z0-9%\-_.]{1,100}/?$"
)

#: THE FOUR OTHER SCRIPTS' DIGITS, as code points so this file stays ASCII.
#: ``str.isdigit()`` is True of every one and the bare digit escape matches
#: every one, which is why the shipped entry names the ten explicitly.
NON_ASCII_IDS = tuple(
    "".join(chr(base + n) for n in range(4))
    for base in (0x0661, 0x06F1, 0x0967, 0xFF11)
)


def _matching_patterns(url: str) -> list[str]:
    """Which allowlist entries match, by pattern text."""
    return [p.pattern for p in readonly._ALLOWED_URL_PATTERNS if p.match(url)]


def _forbidden_hits(url: str) -> list[str]:
    """Which forbidden substrings this url carries. Gate one, read directly."""
    return [s for s in readonly._FORBIDDEN_URL_SUBSTRINGS if s in url]


def _with(mutation: re.Pattern[str]) -> tuple:
    """The shipped roster WITHOUT this wave's entry and WITH a mutation.

    The wave's own entry is removed first, or every mutation below would be
    measured against a roster that already admits the target and would report
    a smaller blast radius than it has. That is not hypothetical: the probe
    this file's numbers come from made exactly that mistake on its first run.
    """
    kept = tuple(
        p for p in readonly._ALLOWED_URL_PATTERNS
        if not p.pattern.startswith("^https://www\\.linkedin\\.com/company/")
    )
    assert len(kept) == len(readonly._ALLOWED_URL_PATTERNS) - 1, (
        "this wave's entry was not found on the roster, so every measurement "
        "below would be taken against the wrong baseline"
    )
    return kept + (mutation,)


def _admits(roster: tuple, url: str) -> bool:
    """The real predicate's two gates, applied in the real order, against a
    roster this test supplies. ``is_read_url`` reads the module tuple, so it
    cannot answer a question about a hypothetical roster."""
    lowered = url.lower()
    if any(s in lowered for s in readonly._FORBIDDEN_URL_SUBSTRINGS):
        return False
    return any(p.match(url) for p in roster)


# ---------------------------------------------------------------------------
# 1. The address the pattern was bought for
# ---------------------------------------------------------------------------


def test_both_admitted_spellings_read_allowed():
    """Through the SHIPPED predicate rather than a re-implementation -- the
    standing rule after a lead wrote its own exact-value check twice and got
    it wrong twice: when the repository ships an instrument, import it."""
    for url in (PAGE_URL, PAGE_URL_NUMERIC):
        assert readonly.is_read_url(url) is True, url
        # The slashless spelling, because the trailing slash is optional and
        # a reader should not have to infer that from the regex.
        assert readonly.is_read_url(url.rstrip("/")) is True, url


def test_each_admitted_address_is_admitted_by_exactly_one_pattern():
    """An address matched by two patterns means one of them is broader than
    its comment claims, and the survivor test below would then pass while
    proving nothing."""
    for url in (PAGE_URL, PAGE_URL_NUMERIC):
        assert len(_matching_patterns(url)) == 1, _matching_patterns(url)


def test_the_new_pattern_is_the_only_thing_standing():
    """SHOWN FAILING: remove the entry and the address refuses again.

    A pattern that is not load-bearing is one whose removal changes nothing,
    and a test that cannot tell those apart certifies nothing.

    ``_forbidden_hits`` is asserted empty FIRST -- if a forbidden substring
    were doing the refusing, this would pass with the pattern deleted and mean
    nothing at all.
    """
    for url in (PAGE_URL, PAGE_URL_NUMERIC):
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


def test_no_exemption_table_was_needed_or_touched():
    """The admitted address carries no forbidden substring, so neither
    exemption table has anything to say about it. Asserted because an
    admission that arrived through an exemption is a different and wider
    change than one that arrived through a pattern."""
    for url in (PAGE_URL, PAGE_URL_NUMERIC):
        assert url.lower() not in readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS
        assert not any(
            p.match(url)
            for p, _ in readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS
        )


# ---------------------------------------------------------------------------
# 2. What the entry did not buy
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("url", NOT_BOUGHT)
def test_the_neighbours_stay_refused(url):
    assert readonly.is_read_url(url) is False, url


@pytest.mark.parametrize("url", WRITE_SURFACES + ROSTERS[:2])
def test_the_dangerous_neighbours_are_refused_by_this_anchor_and_nothing_else(
    url,
):
    """**THE SHARPEST ASSERTION IN THIS FILE.** Page creation, Page
    administration and the member roster carry NO forbidden substring -- the
    denylist has ``/create`` and LinkedIn does not spell Page creation with
    it. So the count of gates refusing each is ONE, and that one is the
    anchor. A future widening of this entry has nothing behind it."""
    assert _forbidden_hits(url) == [], url
    assert _matching_patterns(url) == [], url
    assert readonly.is_read_url(url) is False, url


def test_a_slug_carrying_a_forbidden_substring_refuses_at_gate_one():
    """Nothing about this entry excuses gate one, and the right response to
    a company whose slug contains ``connect`` is to leave it unread -- never
    to shorten the forbidden list."""
    for slug in ("connect-solutions", "invite-partners", "follow-house"):
        url = f"{BASE}/company/{slug}/"
        assert _forbidden_hits(url) != [], url
        assert readonly.is_read_url(url) is False, url


def test_the_pattern_admits_one_path_segment_only():
    """The narrowness as a PROPERTY rather than a list of examples, so a
    future widening of the character class is caught even for a spelling
    nobody has met."""
    entry = _matching_patterns(PAGE_URL)[0]
    compiled = re.compile(entry)
    for suffix in ("about", "people", "jobs", "life", "admin", "x", "1"):
        assert not compiled.match(f"{BASE}/company/{SLUG}/{suffix}/")
        assert not compiled.match(f"{BASE}/company/{SLUG}/{suffix}")


# ---------------------------------------------------------------------------
# 3. The three spellings nobody may write, each shown opening something
# ---------------------------------------------------------------------------


def test_the_mutations_are_not_on_the_boundary():
    """A planted pattern that turned out to be shipped would make every
    measurement below a statement about the real boundary."""
    sources = {p.pattern for p in readonly._ALLOWED_URL_PATTERNS}
    for mutation in (
        _FAMILY_MUTATION, _DIGIT_ESCAPE_MUTATION, _DOTTED_CLASS_MUTATION
    ):
        assert mutation.pattern not in sources


def test_the_family_pattern_admits_page_creation_and_page_administration():
    """SHOWN FIRING. The standing boundary trap, on this root, measured.

    Every address here is refused today and admitted by the family spelling,
    and every one of them is defended by NOTHING ELSE -- asserted rather than
    asserted-in-prose, by checking the forbidden roster is silent on each.
    """
    roster = _with(_FAMILY_MUTATION)
    for url in WRITE_SURFACES:
        assert readonly.is_read_url(url) is False, url
        assert _forbidden_hits(url) == [], url
        assert _admits(roster, url) is True, (
            f"the family pattern was expected to open {url!r}; if it no "
            "longer does, this guard has stopped measuring the trap"
        )


def test_the_family_pattern_admits_the_member_roster_and_two_traversals():
    """SHOWN FIRING, on the two classes the anchor exists to refuse."""
    roster = _with(_FAMILY_MUTATION)
    for url in (
        f"{BASE}/company/{SLUG}/people/",
        f"{BASE}/company/{IDENTIFIER}/people/",
        f"{BASE}/company/{SLUG}/../../mypreferences/d/close-account",
        f"{BASE}/company/{SLUG}/../../in/someone-else/",
    ):
        assert readonly.is_read_url(url) is False, url
        assert _admits(roster, url) is True, url


def test_the_digit_escape_admits_four_spellings_the_closed_class_does_not():
    """SHOWN FIRING. ``\\d`` matches ANY Unicode decimal digit, which is the
    defect ``groups.py`` found in ``str.isdigit()`` arriving on this root.

    SIX admitted against the closed class's TWO, and the four extras are
    below. The control is the ASCII id, which both spellings admit -- without
    it, a mutation that admitted nothing at all would pass this test.
    """
    roster = _with(_DIGIT_ESCAPE_MUTATION)
    assert _admits(roster, PAGE_URL_NUMERIC) is True
    for value in NON_ASCII_IDS:
        url = f"{BASE}/company/{value}/"
        assert value.isdigit() is True
        assert readonly.is_read_url(url) is False, "shipped entry admits it"
        assert _admits(roster, url) is True, "the digit escape does not"


def test_a_dot_in_the_class_admits_a_traversal_segment():
    """SHOWN FIRING. A dotted slug is a real if uncommon spelling, and
    admitting it also admits a segment of ``..`` -- which the browser
    normalises AWAY, turning an admitted organisation address into some other
    page entirely."""
    roster = _with(_DOTTED_CLASS_MUTATION)
    for url in (
        f"{BASE}/company/a.company/",
        f"{BASE}/company/a..company/",
        f"{BASE}/company/./",
    ):
        assert readonly.is_read_url(url) is False, url
        assert _admits(roster, url) is True, url


def test_the_numeric_only_spelling_would_refuse_the_slug_landing_page():
    """THE MEASUREMENT BEHIND THE ENTRY'S CENTRAL ARGUMENT.

    ``/company/[0-9]{1,20}/?$`` admits TWO addresses against the shipped
    entry's FOUR, so it looks strictly safer. What it also does is refuse the
    SLUG spelling -- which is the form LinkedIn canonicalises an organisation
    address to, and therefore the form a numeric request LANDS on. A boundary
    that refuses its own landing page raises through
    ``assert_read_url``, whose refusal INTERPOLATES THE URL, and that is how
    a third party's slug reaches a traceback.
    """
    numeric_only = re.compile(
        r"^https://www\.linkedin\.com/company/[0-9]{1,20}/?$"
    )
    roster = _with(numeric_only)
    assert _admits(roster, PAGE_URL_NUMERIC) is True
    assert _admits(roster, PAGE_URL) is False
    # And the shipped entry admits both, which is the whole trade.
    assert readonly.is_read_url(PAGE_URL_NUMERIC) is True
    assert readonly.is_read_url(PAGE_URL) is True


def test_the_refusal_still_names_the_url_it_refused():
    """The ruling recorded in ``test_navigation_is_never_derived.py`` stands:
    the url STAYS in the refusal, because a navigation refusal that will not
    name what it refused makes every boundary bug harder to find. This test
    exists so the entry's argument above is anchored to real behaviour rather
    than to a remembered one."""
    blocked = f"{BASE}/company/{SLUG}/people/"
    with pytest.raises(Exception) as caught:
        readonly.assert_read_url(blocked)
    assert blocked in str(caught.value)
