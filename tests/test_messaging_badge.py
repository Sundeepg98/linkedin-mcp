"""The messaging badge: NEW is not UNREAD, and zero is not unreadable.

THE FIELD SHIPPED CALLED "unread" AND THAT WAS WRONG. Measured 2026-08-26
with a genuinely unread recruiter InMail on screen, the badge read 0 -- it
counts NEW-SINCE-LAST-VISIT and RESETS when the Messaging tab is opened, so
sitting in Messaging zeroes it while every conversation stays unread. The
docstring beside the field was already honest and it did not help: a reviewer
still read "unread: 0" as "nothing waiting", which is what any caller would
do. A FIELD NAME IS READ FAR MORE OFTEN THAN THE PROSE BESIDE IT.

WHY THIS READER EXISTS AT ALL. "Check my messages" splits into two questions
with very different costs. *Do I have messages waiting* is answerable off the
global-nav badge on ``/feed/``, a surface this server already loads, opening
nobody's conversation. *Show me my inbox* is not: asking LinkedIn for
``/messaging/`` does not stay on an inbox, it redirects into one specific
conversation thread chosen by LinkedIn rather than by the caller.

WHY THE THREE OUTCOMES ARE THE POINT. A badge reading 0 and a nav that never
hydrated look identical to any reader that returns a bare integer. That
confusion is not hypothetical here: two separate attempts to measure whether
opening a thread marks it read came back INCONCLUSIVE precisely because the
badge sat at 0 and had nowhere to fall from -- a check that could not fail. A
reader collapsing those two states would have reported both as a clean zero
and turned an unanswerable question into a false answer.
"""
from __future__ import annotations

import pytest

from linkedin_server import shape

BADGE = 'aria-label="Messaging, {} new notifications"'


@pytest.mark.parametrize(
    "rendered,expected",
    [
        (BADGE.format("0"), 0),
        (BADGE.format("1"), 1),
        (BADGE.format("7"), 7),
        (BADGE.format("1,024"), 1024),
    ],
)
def test_a_rendered_badge_is_read_as_its_number(rendered, expected):
    verdict = shape.messaging_badge(f"<nav>{rendered}</nav>")
    assert verdict["new_since_last_visit"] == expected
    assert verdict["state"] == "read"


def test_zero_is_a_read_answer_and_not_an_unreadable_one():
    """The distinction the whole reader exists for."""
    verdict = shape.messaging_badge(f"<nav>{BADGE.format('0')}</nav>")
    assert verdict["state"] == "read"
    assert verdict["new_since_last_visit"] == 0


@pytest.mark.parametrize(
    "html",
    [
        "",
        "<nav>no badge here</nav>",
        '<nav aria-label="Notifications, 3 new notifications"></nav>',
        '<nav aria-label="Messaging"></nav>',
    ],
    ids=["empty", "no badge", "different badge", "badge with no count"],
)
def test_an_absent_badge_is_unreadable_and_never_zero(html):
    """Absence of a count is not a count of zero.

    The third case matters most: the NOTIFICATIONS badge has the same shape as
    the messaging one and a looser pattern would happily read 3 unread
    messages off it. A reader that answers the wrong question confidently is
    worse than one that declines.
    """
    verdict = shape.messaging_badge(html)
    assert verdict["new_since_last_visit"] is None
    assert verdict["state"] == "unreadable"
    assert verdict["why"]


def test_the_reason_says_zero_is_not_the_same_as_unread():
    """An unreadable verdict has to TELL the caller not to read it as zero,
    because the caller is usually a model and will otherwise summarise it as
    'no messages'."""
    verdict = shape.messaging_badge("<nav></nav>")
    assert "not the same as zero" in verdict["why"].casefold()
