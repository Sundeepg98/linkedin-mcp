"""His own FOLLOWER LIST is admitted past `/follow`, and nothing else is.

REVIEW commit, lane L1, 2026-09-23 -- census ``P L2b``. The spec is
``_audit/2026-09-05-network-tail.md`` section 2 ("allowlist +2, exemptions +2,
denylist UNCHANGED"), applied to ONE of its two addresses: the follower list.
The FOLLOWING list is ``N 38``'s and stays refused, and that is pinned here.

THE TWO GATES ARE BOTH NEEDED AND THIS FILE SHOWS IT: remove the exemption and
the address refuses on ``/follow`` (with the sentence saying a pattern WOULD
admit it); remove the allowlist line and it refuses on the allowlist's own
sentence. Either half alone admits nothing.

THE PROOF THE SPEC SAID WAS OWED "BEFORE COMMITTING, AND IT IS NOT OPTIONAL":
the acts ``/follow`` exists to stop, planted, each still refused on the
substring that names it.

Every variable segment is a placeholder (``placeholder-org``, ``someone-else``).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from linkedin_server import readonly
from linkedin_server.errors import WriteAttemptError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import blast_radius  # noqa: E402

B = "https://www.linkedin.com"
FOLLOWERS = f"{B}/mynetwork/network-manager/people-follow/followers/"
CARRIER = "people-follow/followers"

#: (url, the substring that must refuse it, why)
PLANTED_ACTS = (
    (f"{B}/in/me/follow/", "/follow", "following a member"),
    (f"{B}/company/placeholder-org/follow/", "/follow", "following a Page"),
    (f"{B}/company/placeholder-org/unfollow/", "/unfollow",
     "unfollowing a Page"),
    (f"{B}/feed/follows/", "/follow", "a read the exemption does not reach"),
    (f"{B}/mynetwork/network-manager/people-follow/following/", "/follow",
     "THE SIBLING -- the following list, N 38's row, not admitted here"),
    (FOLLOWERS + "?x=1", "/follow",
     "this address with a QUERY -- the anchor is load-bearing"),
    (FOLLOWERS + "unfollow/", "/follow",
     "this address with a SUB-PATH naming the write"),
    (FOLLOWERS + "../../../../in/someone-else/", "/follow",
     "a TRAVERSAL onto a third party's profile"),
    # NOT A /follow CASE, AND THAT IS WHY IT IS HERE: the family root carries
    # no `/follow` at all ("people-follow/" has no slash before "follow"), so
    # the ALLOWLIST is its only refusal -- and still refuses it.
    (f"{B}/mynetwork/network-manager/people-follow/", None,
     "the family root, refused by the allowlist alone"),
)


def _refusal(url: str) -> str:
    with pytest.raises(WriteAttemptError) as caught:
        readonly.assert_read_url(url)
    return str(caught.value)


def _allow_lines():
    return [p for p in readonly._ALLOWED_URL_PATTERNS if CARRIER in p.pattern]


def _exempt_entries():
    return [
        (p, s) for p, s in readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS
        if p.match(FOLLOWERS)
    ]


def test_the_follower_list_is_admitted_through_the_shipped_gate():
    assert readonly.is_read_url(FOLLOWERS)
    assert readonly.is_read_url(FOLLOWERS.rstrip("/"))


def test_exactly_one_line_and_one_exemption_carry_it():
    assert len(_allow_lines()) == 1, [p.pattern for p in _allow_lines()]
    entries = _exempt_entries()
    assert len(entries) == 1, entries
    assert entries[0][1] == frozenset({"/follow"}), entries[0][1]


def test_the_exemption_excuses_exactly_follow_and_only_here():
    assert readonly._pattern_exempted_substrings(FOLLOWERS) == frozenset(
        {"/follow"}
    )
    for url, _bad, why in PLANTED_ACTS:
        assert readonly._pattern_exempted_substrings(url) == frozenset(), why


@pytest.mark.parametrize("url,bad,why", PLANTED_ACTS)
def test_every_planted_act_is_still_refused_on_its_own_substring(url, bad, why):
    assert not readonly.is_read_url(url), why
    message = _refusal(url)
    if bad is None:
        assert "is not on the read-only allowlist" in message, (why, message)
        return
    assert "contains %r" % bad in message, (why, message)
    assert "not a read surface" in message, (why, message)


def test_the_denylist_is_unchanged_and_still_names_both_verbs():
    assert "/follow" in readonly._FORBIDDEN_URL_SUBSTRINGS
    assert "/unfollow" in readonly._FORBIDDEN_URL_SUBSTRINGS
    assert len(readonly._FORBIDDEN_URL_SUBSTRINGS) == 33


def test_without_the_exemption_the_substring_refuses_and_says_a_pattern_would_admit(
    monkeypatch,
):
    """THE FIRST GATE ALONE: the allowlist line cannot admit it by itself."""
    kept = tuple(
        (p, s) for p, s in readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS
        if not p.match(FOLLOWERS)
    )
    assert len(kept) == len(readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS) - 1
    monkeypatch.setattr(readonly, "_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS", kept)
    assert not readonly.is_read_url(FOLLOWERS)
    message = _refusal(FOLLOWERS)
    assert "contains '/follow'" in message, message
    assert "A READ PATTERN DOES ADMIT THIS ADDRESS" in message, message


def test_without_the_allowlist_line_the_allowlist_refuses_it(monkeypatch):
    """THE SECOND GATE ALONE: the exemption cannot admit it by itself -- and
    this is also the proven rollback of the allowlist half."""
    kept = tuple(
        p for p in readonly._ALLOWED_URL_PATTERNS if CARRIER not in p.pattern
    )
    assert len(kept) == len(readonly._ALLOWED_URL_PATTERNS) - 1
    monkeypatch.setattr(readonly, "_ALLOWED_URL_PATTERNS", kept)
    assert not readonly.is_read_url(FOLLOWERS)
    message = _refusal(FOLLOWERS)
    assert "is not on the read-only allowlist" in message, message


def test_the_pair_newly_admits_exactly_its_own_two_spellings():
    """THE BLAST RADIUS of the PAIR, over the shipped corpus plus this file's
    spellings, measured the way ``blast_radius`` measures -- ``is_read_url``
    before and after, on concrete urls, never a grep."""
    corpus = sorted(
        set(blast_radius.corpus())
        | {FOLLOWERS, FOLLOWERS.rstrip("/")}
        | {url for url, _bad, _why in PLANTED_ACTS}
    )
    allow = readonly._ALLOWED_URL_PATTERNS
    exempt = readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS
    after = {url: readonly.is_read_url(url) for url in corpus}
    try:
        readonly._ALLOWED_URL_PATTERNS = tuple(
            p for p in allow if CARRIER not in p.pattern
        )
        readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS = tuple(
            (p, s) for p, s in exempt if not p.match(FOLLOWERS)
        )
        before = {url: readonly.is_read_url(url) for url in corpus}
    finally:
        readonly._ALLOWED_URL_PATTERNS = allow
        readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS = exempt
    gained = sorted(u for u in corpus if after[u] and not before[u])
    lost = sorted(u for u in corpus if before[u] and not after[u])
    assert gained == sorted({FOLLOWERS, FOLLOWERS.rstrip("/")}), gained
    assert lost == [], lost


def test_the_line_names_nobody():
    """No slug class, no wildcard, no group, no query, no member segment."""
    source = _allow_lines()[0].pattern
    for token in ("[", ".*", ".+", r"\w", r"\d", "+", "(", "/in/"):
        assert token not in source, (token, source)
