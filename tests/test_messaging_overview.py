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
    assert [r["name"] for r in out["rows"]] == [shape.NAME_PLACEHOLDER] * 2
    assert out["names_included"] is False
    for real in ("Dana", "Whitfield", "Ivo", "Karlsson"):
        assert real not in str(out), real


def test_opting_in_returns_the_real_names():
    """The control. A redactor that could never be turned off would make the
    tool useless for the one thing he opens it for."""
    out = shape.messaging_overview(HTML, THREAD_URL, include_names=True)

    assert [r["name"] for r in out["rows"]] == ["Dana Whitfield", "Ivo Karlsson"]
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


# ---------------------------------------------------------------------------
# Unread paired to the row -- the refinement he asked for directly
# ---------------------------------------------------------------------------

PAIRED = (
    '<div aria-label="Select conversation with Dana Whitfield">'
    '<span class="messaging-remove-unread-blue-background">Unread</span></div>'
    '<div aria-label="Select conversation with Ivo Karlsson">read</div>'
    '<div aria-label="Select conversation with Mo Chen"><i>UNREAD</i></div>'
)


def test_unread_is_attached_to_the_conversation_not_counted_beside_it():
    """"Four are waiting" without saying WHICH four is barely better than
    nothing -- he still has to open LinkedIn, which is the trip this exists to
    save. The marker and the name are on the same row, so they come back
    together."""
    out = shape.messaging_overview(PAIRED, THREAD_URL)

    assert out["conversations"] == 3
    assert out["unread"] == 2
    assert [(r["position"], r["unread"]) for r in out["rows"]] == [
        (1, True),
        (2, False),
        (3, True),
    ]


def test_the_pairing_survives_redaction():
    """Position plus unread state is actionable with no identities at all --
    which is why the default stays redacted rather than being forced open to
    make the tool useful."""
    out = shape.messaging_overview(PAIRED, THREAD_URL)

    assert all(r["name"] == shape.NAME_PLACEHOLDER for r in out["rows"])
    unread_positions = [r["position"] for r in out["rows"] if r["unread"]]
    assert unread_positions == [1, 3]


def test_a_marker_does_not_bleed_into_the_next_conversation():
    """The row boundary has to hold or every row below an unread one reads
    unread too -- a wrong answer that would look plausible and inflate every
    count this tool produces."""
    out = shape.messaging_overview(PAIRED, THREAD_URL)
    assert out["rows"][1]["unread"] is False


def test_the_last_row_is_not_marked_unread_by_the_page_footer():
    """The tail row has no next-label to stop at, so its span is BOUNDED. A
    naive slice-to-end-of-document would hand it every 'unread' string in the
    footer, scripts and analytics payload below the list."""
    html = (
        '<div aria-label="Select conversation with Solo Person">quiet</div>'
        + "<footer>" + ("x" * 5000) + "unread</footer>"
    )
    out = shape.messaging_overview(html, THREAD_URL)
    assert out["rows"][0]["unread"] is False, "the footer marked the last row"


def test_the_result_says_the_count_is_a_floor():
    """A recruiter InMail was seen in the product that did not appear in these
    rows. Either it sits below this page or InMails are a separate surface --
    UNMEASURED, and reported as such rather than guessed. A tool whose whole
    credibility rests on its numbers must not present a floor as a total.
    """
    out = shape.messaging_overview(PAIRED, THREAD_URL)
    completeness = out["completeness"]
    assert "floor" in completeness
    assert "UNMEASURED" in completeness
    assert "InMail" in completeness
