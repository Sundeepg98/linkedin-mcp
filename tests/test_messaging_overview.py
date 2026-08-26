"""The messaging surface: the cost of the call is a field, not a footnote.

WHY THIS TOOL IS NAMED FOR OPENING RATHER THAN READING. Asking LinkedIn for
``/messaging/`` does not stay on a list. It redirects into ONE SPECIFIC
CONVERSATION that LinkedIn chooses -- measured twice, on two runs by two
actors. A tool called ``read_inbox`` would describe an operation the product
does not offer, which is the same defect as the badge field that shipped
called ``unread``: a true number under a false heading.

THE UNKNOWN IS SHIPPED RATHER THAN BLOCKING. Whether opening marks the
message read is unmeasured, and three designs failed for three distinct
reasons -- badge at zero twice, then the discovery that the badge tracks
VISIT rather than READ. The signal that would settle it lives on the page
that cannot be reached without the redirect, so measuring it requires
performing the act being measured. An honest unknown at the point of decision
beats no tool.
"""
from __future__ import annotations

import pytest

from linkedin_server import shape

LIST_URL = "https://www.linkedin.com/messaging/"
THREAD_URL = "https://www.linkedin.com/messaging/thread/2-NjY1ZDkwYWEt==/"

HTML = (
    '<div aria-label="Select conversation with Dana Whitfield"></div>'
    '<div aria-label="Select conversation with Ivo Karlsson"></div>'
    '<div aria-label="Select conversation with Dana Whitfield"></div>'
    '<span class="messaging-remove-unread-blue-background">Unread</span>'
    "<span>UNREAD</span>"
)


def test_names_are_placeholders_unless_the_caller_asks():
    """Counts answer the question that gets asked; names outlive it.

    "Is anything waiting, and how much" needs no identities. The default is
    not about protecting him from his own inbox -- it is that this output
    lands in a model's context and in transcripts, where a name persists long
    after the question that fetched it.
    """
    out = shape.messaging_overview(HTML, THREAD_URL)

    assert out["conversations"] == 2, "duplicate rows should collapse"
    assert out["participants"] == [shape.NAME_PLACEHOLDER] * 2
    assert out["names_included"] is False
    for real in ("Dana", "Whitfield", "Ivo", "Karlsson"):
        assert real not in str(out), real


def test_opting_in_returns_the_real_names():
    """The control. A redactor that could never be turned off would make the
    tool useless for the one thing he opens it for."""
    out = shape.messaging_overview(HTML, THREAD_URL, include_names=True)

    assert out["participants"] == ["Dana Whitfield", "Ivo Karlsson"]
    assert out["names_included"] is True


def test_the_thread_id_is_always_redacted_even_when_names_are_wanted():
    """The identifier names one private conversation and no tool here accepts
    it -- of no use to a caller and every use to a leak. So it is redacted on
    BOTH paths, unlike the names."""
    for include in (False, True):
        out = shape.messaging_overview(HTML, THREAD_URL, include_names=include)
        landed = out["thread_opened"]["landed_url"]
        assert "<THREAD-ID>" in landed
        assert "NjY1ZDkwYWEt" not in str(out)


def test_the_redirect_is_reported_as_a_cost_with_its_evidence():
    out = shape.messaging_overview(HTML, THREAD_URL)
    opened = out["thread_opened"]

    assert opened["opened"] is True
    assert "did not choose" in opened["why"]
    # The unknown is stated where a caller meets the cost, not in an audit file.
    assert "UNMEASURED" in opened["marks_it_read"]
    assert "act being measured" in opened["marks_it_read"]


def test_staying_on_the_list_is_flagged_as_unexpected():
    """If LinkedIn ever stops redirecting, that is a CHANGE and should read as
    one rather than silently looking like success."""
    out = shape.messaging_overview(HTML, LIST_URL)

    assert out["thread_opened"]["opened"] is False
    assert "not the measured behaviour" in out["thread_opened"]["why"]


@pytest.mark.parametrize(
    "markup,expected",
    [
        ('<div contenteditable="true"></div>', {"contenteditable": 1}),
        ('<button aria-label="Send message"></button>', {"send_controls": 1}),
        ("<form></form>", {"forms": 1}),
        ("<p>nothing</p>", {"contenteditable": 0, "send_controls": 0, "forms": 0}),
    ],
    ids=["editor", "send control", "form", "none of them"],
)
def test_send_shaped_things_are_COUNTED_not_promised_absent(markup, expected):
    """"Reading put no composer in front of you" should be a number.

    Sending is blocked at the boundary -- /messaging/compose is on the
    forbidden list, checked before the allowlist -- but a caller cannot see
    that from here. A count they can read beats an assurance they must trust,
    and it is the same discipline as reporting the redirect rather than
    describing the surface as an inbox.
    """
    out = shape.messaging_overview(markup, THREAD_URL)
    for key, value in expected.items():
        assert out["send_surfaces"][key] == value


def test_the_boundary_still_refuses_the_composer():
    """The claim the docstring makes, asserted against the real guard."""
    from linkedin_server import readonly

    assert readonly.is_read_url(LIST_URL) is True
    assert readonly.is_read_url(THREAD_URL) is True
    assert (
        readonly.is_read_url(
            "https://www.linkedin.com/messaging/compose/?body=hi&interop=msgOverlay"
        )
        is False
    )
