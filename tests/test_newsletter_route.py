"""The newsletters root: that the boundary admits it, and that LinkedIn writes it.

TWO CLAIMS, AND THEY ARE DIFFERENT CLAIMS. An allowlist entry says an address
MAY be opened. It says nothing about whether that address is the one LinkedIn
actually serves -- and this repository has the counter-example on the shelf:
``/in/me/details/interests/`` is on the allowlist, was admitted for exactly
this blocker's precondition, and REDIRECTS. So the gate assertions below are
paired with a FIXTURE assertion, taken over a page LinkedIn served, that the
spelling in the pattern is the spelling on the page.

WHAT THAT PAIR STILL DOES NOT PROVE, said here rather than left to be assumed:
nobody has opened ``/mynetwork/network-manager/newsletters/``. The fixture
carries the NAV LINK to it, not the page behind it. These tests establish that
the door is open and that the handle is where the pattern reaches for it; the
first live read is what establishes there is a room.

AND THE NAV LINK IS NOT EVIDENCE OF A SUBSCRIPTION. It would require LinkedIn
to omit the link for a member who subscribes to nothing, and there is no
known-empty account to test that against. **A reading no instrument can fail
is not a reading** -- the same trap as a tab strip drawing a Groups tab.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from linkedin_server import readonly

BASE = "https://www.linkedin.com"

#: THE ADDRESS THIS WAVE ADMITTED. Not typed from memory: it is the literal
#: ``dom.INVITATION_BADGE_HREF``'s neighbour, recorded in ``dom.py`` from a
#: live nav read on 2026-09-04 and carried in the fixture below.
NEWSLETTERS_ROOT = f"{BASE}/mynetwork/network-manager/newsletters/"

#: A TRACKED CAPTURE, i.e. a page LinkedIn served -- not a synthetic fixture.
#: It is the connections list, and the newsletters link is on it because the
#: Manage-my-network nav renders on every page in that family.
FIXTURE = Path(__file__).parent / "fixtures" / "connections_list.html"


def _fixture_text() -> str:
    return FIXTURE.read_text(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# The gate
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "url",
    [
        NEWSLETTERS_ROOT,
        f"{BASE}/mynetwork/network-manager/newsletters",
    ],
)
def test_the_newsletters_root_is_admitted_in_both_slash_forms(url):
    """The nav writes the trailing slash; the pattern accepts either.

    Both are asserted because this project has already lost a diagnosis to
    exactly this: the invitation-badge aim required a trailing slash the
    badged control does not carry, resolved zero, and read as an absence.
    """
    readonly.assert_read_url(url)


#: WHAT THE ADMISSION DELIBERATELY DID NOT BUY. Each is named because a
#: widening is only narrow if its refusals are stated, and because the obvious
#: later "fix" is to reach for one of these.
MUST_STAY_REFUSED = (
    ("one newsletter's own page -- its SLUG IS ROUTINELY ITS AUTHOR'S NAME",
     f"{BASE}/newsletters/weekly-123456/"),
    ("the same in the word-slug form the page actually writes",
     f"{BASE}/newsletters/a-made-up-letter/"),
    ("the product root, which is a family and not a page",
     f"{BASE}/newsletters/"),
    ("per-newsletter analytics -- census M C83, P L4",
     f"{BASE}/newsletters/weekly-123456/analytics/"),
    ("the creator-hub analytics form of the same rows",
     f"{BASE}/analytics/newsletter/"),
    ("a query on the admitted root -- where a filter naming a person arrives",
     f"{NEWSLETTERS_ROOT}?filter=subscribed"),
    ("a sub-path under the admitted root",
     f"{NEWSLETTERS_ROOT}subscribed/"),
    ("MY NETWORK ITSELF, the parent believed to consume the invitation badge",
     f"{BASE}/mynetwork/"),
    ("a member's own newsletter tab -- a page about that member",
     f"{BASE}/in/priya-sharma-12ab34/recent-activity/newsletters/"),
)


@pytest.mark.parametrize("why,url", MUST_STAY_REFUSED, ids=[c[1] for c in MUST_STAY_REFUSED])
def test_the_anchoring_is_the_whole_of_the_permission(why, url):
    with pytest.raises(Exception):
        readonly.assert_read_url(url)


def test_creating_a_newsletter_is_refused_by_BOTH_gates_and_the_count_matters():
    """Census ``M C50`` and ``M C81`` need TWO boundary changes, not one.

    Worth knowing rather than discovering: ``/newsletters/create/`` contains
    ``/create``, which is on the forbidden list and checked FIRST, and no
    pattern admits it either. A wave that shortened the substring would still
    find the address refused, and a wave that added a pattern would still find
    the substring firing.
    """
    url = f"{BASE}/newsletters/create/"
    with pytest.raises(Exception) as caught:
        readonly.assert_read_url(url)
    message = str(caught.value)
    assert "/create" in message, message
    # The gate's own second-gate sentence, which distinguishes "the substring
    # is the only thing refusing" from "both gates refuse".
    assert "AND NO READ PATTERN" in message, message


def test_the_admitted_root_carries_NO_forbidden_substring_so_the_pattern_is_alone():
    """The disclosure that belongs with a widening rather than buried.

    The member roster taught this shape on 2026-09-05: an address refused by
    ONE gate is a different risk from one refused by two, and the count is the
    finding. Nothing on the forbidden list touches this address, so the anchor
    on the pattern is the only thing between this server and the family under
    it.
    """
    lowered = NEWSLETTERS_ROOT.lower()
    hits = [bad for bad in readonly._FORBIDDEN_URL_SUBSTRINGS if bad in lowered]
    assert hits == [], hits
    # THE CONTROL, because an empty list is what a broken loop also returns.
    sibling = f"{BASE}/mynetwork/network-manager/people-follow/following/".lower()
    assert [bad for bad in readonly._FORBIDDEN_URL_SUBSTRINGS if bad in sibling], (
        "the people-follow sibling no longer trips a forbidden substring, so "
        "the empty result above is not evidence of anything"
    )


def test_MUTATION_removing_the_pattern_refuses_the_route(monkeypatch):
    """Planted: drop this wave's pattern and the address must go dark.

    Without this, the two admission tests above would pass just as happily if
    some OTHER pattern were admitting the address -- which is not hypothetical
    here, since a sibling under the same ``/mynetwork/network-manager/`` prefix
    is already on the list.
    """
    needle = "network-manager/newsletters"
    kept = tuple(
        pattern
        for pattern in readonly._ALLOWED_URL_PATTERNS
        if needle not in pattern.pattern
    )
    assert len(kept) == len(readonly._ALLOWED_URL_PATTERNS) - 1, (
        "the newsletters pattern was not found by its own needle, so this "
        "mutation removed nothing"
    )
    monkeypatch.setattr(readonly, "_ALLOWED_URL_PATTERNS", kept)
    with pytest.raises(Exception):
        readonly.assert_read_url(NEWSLETTERS_ROOT)


# ---------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------


def test_a_page_linkedin_served_carries_exactly_this_address():
    """THE ANCHOR. The pattern aims at a spelling a real capture uses.

    If LinkedIn moves this address, this is the test that says so -- and it
    says so as a failure rather than as a reader silently finding nothing,
    which is the failure mode this project pays for most often.
    """
    text = _fixture_text()
    assert NEWSLETTERS_ROOT in text, (
        "the tracked capture no longer carries the address the allowlist "
        "admits, so the entry is aiming at a spelling the page does not use"
    )
    readonly.assert_read_url(NEWSLETTERS_ROOT)


def test_the_capture_carries_the_link_ONCE_and_as_an_anchor():
    """A count, not a presence, because the two answer different questions.

    One anchor is the nav item. Several would mean the surface is drawn more
    than once and a reader aiming with ``.first`` would be choosing by
    POSITION between controls that are not interchangeable -- the exact defect
    ``dom.invitation_badge_selector`` was written to avoid.
    """
    text = _fixture_text()
    anchors = re.findall(
        r'<a[^>]+href="' + re.escape(NEWSLETTERS_ROOT) + r'"', text
    )
    assert len(anchors) == 1, len(anchors)


def test_the_capture_does_NOT_carry_a_subscription_row_and_that_is_the_finding():
    """The nav link is not the page, and this asserts the gap rather than
    letting a later reader assume the fixture covers the surface.

    ``/newsletters/<slug>`` is the shape a subscription row's own anchor would
    have. ZERO of them in the corpus means no reader can be fixture-driven
    here yet, and no test in this file may be quoted as evidence about what
    the newsletters page contains.
    """
    text = _fixture_text()
    rows = re.findall(r'href="[^"]*?/newsletters/[A-Za-z0-9\-_%.]+/', text)
    assert rows == [], rows
    # THE CONTROL, so the zero is legible: the same expression finds the nav
    # link when the trailing segment is not required.
    assert re.findall(r'href="[^"]*?/newsletters/', text), (
        "the needle finds nothing at all, so the zero above is a fact about "
        "this expression rather than about the capture"
    )
