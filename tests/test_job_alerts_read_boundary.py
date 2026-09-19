"""The job-alerts READ half opened, and the write half shown still shut.

WHAT THIS FILE GUARDS. On 2026-09-05 the boundary admitted ONE anchored
address -- the job-alerts manage page -- for census row J37, blocker 36
``JOB-ALERTS-SURFACE``. The blocker gates seven rows and the other six are
WRITES. This file exists so the difference between those two halves is a set of
assertions rather than a paragraph of intent.

THE SPLIT IS THE POINT, and the shipped refusal is what makes it measurable.
``readonly.assert_read_url`` composes its refusal from two clauses: when a
forbidden substring bites it ALSO reports whether an allowlist pattern would
have admitted the address anyway. For the alerts manage page no substring bites
at all; for create, delete and frequency/channel BOTH gates refuse
independently. So the read costs one pattern and the writes cannot be reached
by a pattern, which is a property this file asserts rather than a cost somebody
estimated.

AND THE FAMILY PATTERN IS PLANTED HERE, NOT ARGUED ABOUT. The standing boundary
trap in this repository is that ``close-account`` is defended by NO PATTERN
MATCHING rather than by a denylist entry -- so a FAMILY pattern admits
spellings nothing else defends. ``/jobs/alerts/`` has the identical shape and
nobody had measured it. The mutation below shows the family pattern admitting a
``pause`` VERB: pausing an alert is a write nobody has named and no forbidden
substring covers. That number is measured by running the mutation, because the
last wave to reason about such a count instead of running it got it wrong in
the flattering direction.

NOTHING HERE OPENS A PAGE. Every address is a literal in this file and the only
thing called is the shipped predicate.
"""

from __future__ import annotations

import re

from linkedin_server import readonly


#: The address the pattern was bought for, in both spellings the anchor admits.
MANAGE_URL = "https://www.linkedin.com/jobs/alerts/"
MANAGE_URL_NO_SLASH = "https://www.linkedin.com/jobs/alerts"

#: The three WRITE addresses in the same blocker. Each is refused by a
#: forbidden substring, checked BEFORE the allowlist and not shortened for a
#: write, and each is ALSO unmatched by any pattern -- both gates, separately.
CREATE_URL = "https://www.linkedin.com/jobs/alerts/create"
DELETE_URL = "https://www.linkedin.com/jobs/alerts/delete/1234567890"
FREQUENCY_URL = "https://www.linkedin.com/jobs/alerts/settings/"

#: Addresses under the same root that carry NO forbidden substring and are
#: therefore defended today by nothing but the absence of a rule. This is the
#: close-account shape, and these are what a family pattern would open.
DETAIL_URL = "https://www.linkedin.com/jobs/alerts/1234567890/"
QUERY_URL = "https://www.linkedin.com/jobs/alerts/?origin=JOB_ALERT_EMAIL"
UNCONFIRMED_MANAGE_URL = "https://www.linkedin.com/jobs/alerts/manage/"
#: A WRITE. Pausing an alert changes a value the account holds, and neither
#: gate refuses it today.
PAUSE_URL = "https://www.linkedin.com/jobs/alerts/pause/1234567890"

UNDEFENDED_BY_ANY_RULE = (DETAIL_URL, QUERY_URL, UNCONFIRMED_MANAGE_URL, PAUSE_URL)

NOT_BOUGHT = (
    CREATE_URL,
    DELETE_URL,
    FREQUENCY_URL,
    *UNDEFENDED_BY_ANY_RULE,
    # The neighbouring roots this entry must not have reached.
    "https://www.linkedin.com/jobs/alerts/../mypreferences/d/categories/",
    "https://www.linkedin.com/mypreferences/d/categories/account/",
)

#: THE FAMILY PATTERN NOBODY MAY WRITE.
#:
#: Defined here as a MUTATION -- it is not on the boundary and a test below
#: asserts that it is not -- so that the cost of writing it is a measurement in
#: this file rather than a claim in a comment.
_ALERTS_FAMILY_MUTATION = re.compile(
    r"^https://www\.linkedin\.com/jobs/alerts/.*$"
)

#: The pattern that WAS written, quoted so the survivor test can name it.
_NARROW_PATTERN_TEXT = r"^https://www\.linkedin\.com/jobs/alerts/?$"


def _matching_patterns(url: str) -> list[str]:
    """Which allowlist entries match, by pattern text."""
    return [p.pattern for p in readonly._ALLOWED_URL_PATTERNS if p.match(url)]


def _forbidden_hits(url: str) -> list[str]:
    """Which forbidden substrings this url carries. Gate one, read directly."""
    return [s for s in readonly._FORBIDDEN_URL_SUBSTRINGS if s in url]


# ---------------------------------------------------------------------------
# 1. The one address the pattern was bought for
# ---------------------------------------------------------------------------


def test_the_manage_page_reads_allowed():
    """Open, through the SHIPPED predicate rather than a re-implementation."""
    assert readonly.is_read_url(MANAGE_URL) is True
    assert readonly.is_read_url(MANAGE_URL_NO_SLASH) is True


def test_the_manage_page_is_admitted_by_exactly_one_pattern():
    """One surface, one pattern, and no accidental second admitter.

    Two admitters would mean one of them is broader than its comment claims,
    and the survivor test below would then pass while proving nothing.
    """
    assert _matching_patterns(MANAGE_URL) == [_NARROW_PATTERN_TEXT]
    assert _matching_patterns(MANAGE_URL_NO_SLASH) == [_NARROW_PATTERN_TEXT]


def test_the_new_pattern_is_the_only_thing_standing():
    """SHOWN FAILING: remove the entry and the address refuses again.

    A pattern whose removal changes nothing is not load-bearing, and a test
    that cannot tell those apart certifies nothing. The two gates are applied
    by hand in the real predicate's order -- gate one asserted empty FIRST,
    because if a forbidden substring were doing the refusing this test would
    pass with the pattern deleted and mean nothing at all.
    """
    for url in (MANAGE_URL, MANAGE_URL_NO_SLASH):
        assert _forbidden_hits(url) == [], (
            "gate one already refuses the manage page, so this test would "
            "pass for the wrong reason"
        )
        survivors = [
            p
            for p in readonly._ALLOWED_URL_PATTERNS
            if p.pattern != _NARROW_PATTERN_TEXT
        ]
        assert len(survivors) == len(readonly._ALLOWED_URL_PATTERNS) - 1
        assert not any(p.match(url) for p in survivors), (
            "the manage page is admitted by something other than its own entry"
        )


# ---------------------------------------------------------------------------
# 2. The write half, refused by BOTH gates and shown so
# ---------------------------------------------------------------------------


def test_the_three_write_addresses_stay_refused():
    for url in (CREATE_URL, DELETE_URL, FREQUENCY_URL):
        assert readonly.is_read_url(url) is False, url


def test_each_write_address_is_refused_by_a_named_substring():
    """A refusal that reports only what it did NOT match is half a measurement."""
    assert _forbidden_hits(CREATE_URL) == ["/create"]
    assert _forbidden_hits(DELETE_URL) == ["/delete"]
    assert _forbidden_hits(FREQUENCY_URL) == ["/settings/", "settings"]


def test_the_shipped_refusal_says_BOTH_gates_refuse_each_write():
    """The clause that makes the cost split real.

    ``assert_read_url`` reports, when a substring bites, whether a read
    pattern would have admitted the address anyway. For all three writes it
    says no -- so an exemption ALONE does not open any of them, and the
    ledger's ``allowlist +1, denylist x1`` charges one of two costs, once, for
    a set of addresses that each need both.
    """
    for url in (CREATE_URL, DELETE_URL, FREQUENCY_URL):
        try:
            readonly.assert_read_url(url)
        except Exception as exc:  # noqa: BLE001 - the message is the measurement
            message = str(exc)
        else:  # pragma: no cover - guarded by the test above
            raise AssertionError(f"{url!r} was not refused at all")
        assert "NO READ PATTERN ADMITS THIS ADDRESS EITHER" in message, message
        assert "the ONLY thing refusing it" not in message, message


def test_the_manage_page_is_refused_by_neither_gate_before_this_entry():
    """The other half of the split, and it is what makes the read cheap.

    The manage page trips no forbidden substring at all, so it needed one
    allowlist pattern and no exemption of any kind. Asserted as a property of
    the roster rather than read off the comment that claims it.
    """
    assert _forbidden_hits(MANAGE_URL) == []
    assert _forbidden_hits(MANAGE_URL_NO_SLASH) == []


# ---------------------------------------------------------------------------
# 3. The family pattern, PLANTED
# ---------------------------------------------------------------------------


def test_the_family_pattern_is_not_on_the_boundary():
    """The mutation is a mutation. If this ever fails, read the next test."""
    assert _ALERTS_FAMILY_MUTATION.pattern not in {
        p.pattern for p in readonly._ALLOWED_URL_PATTERNS
    }


def test_the_family_pattern_admits_four_addresses_nothing_else_defends():
    """SHOWN FAILING, by planting the pattern rather than reasoning about it.

    Each of these carries NO forbidden substring, so today it is refused for
    exactly one reason: no pattern matches it. A family pattern removes that
    reason and there is nothing behind it. That is the ``close-account`` shape
    -- an address defended by nothing but the absence of a rule -- arriving on
    a second root.

    The count is asserted as FOUR because a wave that reasoned about this
    class instead of running it was wrong in the flattering direction, and the
    correction came from the run.
    """
    opened = [u for u in UNDEFENDED_BY_ANY_RULE if _ALERTS_FAMILY_MUTATION.match(u)]
    assert len(opened) == 4, opened
    for url in UNDEFENDED_BY_ANY_RULE:
        assert _forbidden_hits(url) == [], (
            f"{url!r} carries a forbidden substring, so it is not in this class"
        )
        assert readonly.is_read_url(url) is False, url


def test_the_family_pattern_opens_a_write_verb():
    """The single sharpest reason not to write it.

    Pausing an alert changes a value the account holds. It is refused today by
    the absence of a rule and by nothing else, and it is the address a family
    pattern would open while its author believed they were buying a read.
    """
    assert _forbidden_hits(PAUSE_URL) == []
    assert readonly.is_read_url(PAUSE_URL) is False
    assert _ALERTS_FAMILY_MUTATION.match(PAUSE_URL) is not None


def test_the_narrow_pattern_opens_none_of_them():
    """The entry that WAS written, asked the same question."""
    narrow = re.compile(_NARROW_PATTERN_TEXT)
    for url in UNDEFENDED_BY_ANY_RULE:
        assert narrow.match(url) is None, url


# ---------------------------------------------------------------------------
# 4. What this widening did not buy
# ---------------------------------------------------------------------------


def test_the_neighbours_stay_refused():
    for url in NOT_BOUGHT:
        assert readonly.is_read_url(url) is False, url


def test_the_pattern_admits_no_query_no_subpath_and_no_id():
    """The narrowness as a PROPERTY, not as a list somebody thought of.

    A list of neighbours only ever covers the spellings that came to mind.
    This asserts the shape, so a future widening is caught even for an address
    nobody has met.
    """
    narrow = re.compile(_NARROW_PATTERN_TEXT)
    for suffix in ("x", "1", "?a=b", "#frag", "manage", "manage/", "../"):
        assert narrow.match(MANAGE_URL + suffix) is None, suffix
    assert narrow.match(MANAGE_URL) is not None
    assert narrow.match(MANAGE_URL_NO_SLASH) is not None


def test_this_widening_bought_no_forbidden_substring_exemption():
    """The denylist and both exemption tables are untouched by this entry.

    A digest cannot tell a list that grew from one that shrank, which is why
    the direction is asserted here rather than left to whoever diffs two
    commits.
    """
    assert len(readonly._FORBIDDEN_URL_SUBSTRINGS) == 33
    assert len(readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS) == 2
    assert len(readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS) == 2
    for url in (CREATE_URL, DELETE_URL, FREQUENCY_URL):
        assert url not in readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS


def test_the_account_ending_spellings_are_still_refused():
    """The standing trap, re-asked from this file's own root.

    ``close-account`` lives under a different root and this entry does not go
    near it. The assertion is here anyway, because the reason this entry is
    narrow is that trap, and a guard that only lives beside the surface it was
    written for stops being consulted.
    """
    for url in (
        "https://www.linkedin.com/mypreferences/d/close-account",
        "https://www.linkedin.com/mypreferences/d/close-account/",
        "https://www.linkedin.com/psettings/close-account",
    ):
        assert readonly.is_read_url(url) is False, url
