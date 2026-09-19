"""A forbidden-substring refusal must say whether the OTHER gate would refuse too.

WHY THIS EXISTS, and it is a measured cost rather than a tidiness argument.
``assert_read_url`` checks the forbidden substrings FIRST and raises on the
first hit. So the refusal names a substring and stops -- and every reader takes
the substring for the wall.

**IT IS USUALLY NOT THE WALL.** The allowlist is closed by default, so an
address that trips a substring has almost always failed the pattern table as
well. Measured 2026-09-04: of the addresses this project had filed against
``/invite`` and ``/follow``, not one had an allowlist pattern either.

THREE READERS WERE MISLED BY THE HALF-ANSWER, which is what makes it a property
of the message rather than an anecdote:

1. ``_audit/2026-09-03-linkedin-gap-blockers.md`` section 2 filed ``/invite``
   and ``/follow`` as the blocker for rows they do not gate.
2. A measurement wave reported the same two the next morning as "the defect".
3. The team lead relayed that upward as an instruction to narrow the guards.

All three read a refusal that told them half of what it knew. The fix adds a
sentence; it removes no refusal, and the raise is unconditional either way.

## What is asserted here

BOTH BRANCHES, because a message that can only say one of two things is not
reporting a fact -- it is printing a constant, and a check that cannot fail
certifies nothing. The second branch needs an address that a pattern ADMITS and
a substring still refuses, which the shipped boundary deliberately has none of
(the exemption tables exist precisely to remove them). So it is CONSTRUCTED, by
emptying the exemption table for the length of one test -- the same technique
``tests/test_readonly.py`` already uses to reach its own hard-to-reach branch.

AND THE WORDING CONSTRAINT IS ASSERTED TOO. Two tests in
``tests/test_readonly.py`` tell the two gates apart BY THE MESSAGE: the
forbidden sentence must contain "not a read surface", and it must NOT contain
the allowlist's own sentence. A later edit that phrased this clause by
borrowing the allowlist's words would pass its own test and silently break
theirs, so the prohibition is pinned here, beside the thing that could break it.
"""
from __future__ import annotations

import pytest

from linkedin_server import readonly
from linkedin_server.errors import WriteAttemptError

BASE = "https://www.linkedin.com"

#: THE ALLOWLIST'S OWN SENTENCE. Pinned as a literal because the prohibition is
#: about this exact string: ``tests/test_readonly.py`` asserts it is ABSENT
#: from a forbidden refusal, and that is the only thing telling the two gates
#: apart in a message.
ALLOWLIST_SENTENCE = "not on the read-only allowlist"

#: Addresses that trip a forbidden substring AND have no pattern. Every one was
#: measured on 2026-09-04 rather than assumed, and each is a real address this
#: project has argued about.
BOTH_GATES = (
    (f"{BASE}/feed/follows/", "/follow"),
    (f"{BASE}/groups/12345678/invite/", "/invite"),
    (f"{BASE}/mynetwork/network-manager/people-follow/following/", "/follow"),
)


@pytest.mark.parametrize("url,substring", BOTH_GATES)
def test_a_double_blocked_address_says_the_substring_is_not_the_wall(url, substring):
    """The branch that fires for almost everything, and the one that misled."""
    with pytest.raises(WriteAttemptError) as caught:
        readonly.assert_read_url(url)
    message = str(caught.value)

    assert repr(substring) in message, message
    assert "NO READ PATTERN ADMITS THIS ADDRESS EITHER" in message, message
    # The reader's actual takeaway, in the message rather than in a comment.
    assert "would not make it readable" in message, message

    # AND THE FACT IT ASSERTS IS TRUE, checked independently of the sentence.
    # Otherwise this test pins a string rather than a measurement.
    assert not any(p.match(url) for p in readonly._ALLOWED_URL_PATTERNS)


def test_the_other_branch_can_fire_at_all(monkeypatch):
    """A pattern-admitted address that a substring still refuses.

    THE SHIPPED BOUNDARY HAS NONE, and that is the point of the exemption
    tables. So one is constructed: ``/in/me/edit/intro/`` is admitted by a
    pattern and contains ``/edit/``, and it reaches the door today only because
    an exemption excuses that substring. Empty the exemptions and the second
    branch is exactly the state the message must describe.

    WITHOUT THIS TEST the clause above is a constant. Both observed branches of
    a two-branch message have to be shown, or the instrument has been proven
    only able to say one thing.
    """
    url = f"{BASE}/in/me/edit/intro/"
    # It is ALLOWED as shipped -- stated first, so the monkeypatch below is
    # visibly what changes the answer.
    assert readonly.assert_read_url(url) == url

    monkeypatch.setattr(readonly, "_FORBIDDEN_SUBSTRING_EXEMPTIONS", {})
    monkeypatch.setattr(readonly, "_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS", ())

    with pytest.raises(WriteAttemptError) as caught:
        readonly.assert_read_url(url)
    message = str(caught.value)

    assert "A READ PATTERN DOES ADMIT THIS ADDRESS" in message, message
    assert "ONLY thing refusing it" in message, message
    assert repr("/edit/") in message, message
    # The fact, checked independently of the sentence.
    assert any(p.match(url) for p in readonly._ALLOWED_URL_PATTERNS)


@pytest.mark.parametrize("url,_substring", BOTH_GATES)
def test_the_clause_does_not_borrow_the_allowlist_sentence(url, _substring):
    """The wording constraint that two OTHER tests depend on.

    ``tests/test_readonly.py`` distinguishes the two gates by the message, and
    asserts the allowlist's sentence is absent from a forbidden refusal. A
    later edit phrasing this clause with those words would break that test from
    a different file. Pinned here, beside the code that could do it.
    """
    with pytest.raises(WriteAttemptError) as caught:
        readonly.assert_read_url(url)
    message = str(caught.value)
    assert "not a read surface" in message, message
    assert ALLOWLIST_SENTENCE not in message, message


def test_the_allowlist_refusal_still_carries_its_own_sentence():
    """The other side of the same discrimination, so this file pins both.

    An address with no forbidden substring and no pattern must still refuse
    with the allowlist's own words -- otherwise the clause added above could
    have been achieved by making every refusal say the same thing, which would
    destroy the distinction rather than sharpen it.
    """
    url = f"{BASE}/company/example/"
    assert not any(bad in url.lower() for bad in readonly._FORBIDDEN_URL_SUBSTRINGS)
    with pytest.raises(WriteAttemptError) as caught:
        readonly.assert_read_url(url)
    message = str(caught.value)
    assert ALLOWLIST_SENTENCE in message, message
    assert "not a read surface" not in message, message
