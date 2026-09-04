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


def test_the_result_says_the_count_is_a_floor_and_names_the_other_surface():
    """MEASURED 2026-08-26, and the text was updated in the same breath.

    It used to say the InMail question was UNMEASURED. Filtering to inmail
    then returned TEN ENTIRELY DIFFERENT PEOPLE from the default view,
    including a recruiter InMail that never appears in it -- so InMails are a
    SEPARATE SURFACE, not a pagination boundary, and the sentence claiming
    otherwise was falsified by the very call that answered it.

    The floor language stays: one filter is still not everything.
    """
    completeness = shape.messaging_overview(PAIRED, THREAD_URL)["completeness"]

    assert "floor" in completeness
    assert "SEPARATE SURFACE" in completeness
    assert "UNMEASURED" not in completeness, "the stale claim came back"
    # And it tells the caller what to do about it rather than only warning.
    assert "message_filter" in completeness


def test_a_composer_on_the_page_is_disclosed_rather_than_left_to_be_noticed():
    """send_surfaces STOPPED BEING ZERO, and that is why it is counted.

    Every default-view call returned 0/0/0. Filtering to inmail returned a
    page carrying a composer. Nothing was typed and nothing sent -- but
    "reading put no composer in front of you" was true on one path and false
    on another, and only a NUMBER could have shown that. An assurance would
    have gone on being repeated.
    """
    with_composer = shape.messaging_overview(
        '<div contenteditable="true"></div><form></form>', THREAD_URL
    )
    assert with_composer["composer_present"]["on_this_page"] is True
    note = with_composer["composer_present"]["note"]
    # It says what did NOT happen, and why the url guard was silent.
    assert "nothing sent" in note
    assert "client-side state" in note

    without = shape.messaging_overview("<p>quiet</p>", THREAD_URL)
    assert without["composer_present"]["on_this_page"] is False


def test_the_url_guard_still_refuses_compose_even_though_it_was_not_consulted():
    """The guard's claim is narrower than it looked, and both halves matter.

    It blocks NAVIGATING to a compose surface -- still true, asserted here.
    It was never consulted on the filtered page because nothing navigated:
    LinkedIn rendered the composer as client-side state on an allowed url.
    Those were the same sentence until that call and are not any more.

    What still holds is why this is a disclosure and not an incident:
    rendering a composer is not sending. There is no typing call site, and the
    mutation allowlist holds exactly two clicks, neither of which is a send.
    """
    from linkedin_server import readonly

    assert readonly.is_read_url("https://www.linkedin.com/messaging/compose/?body=hi") is False
    assert readonly.is_read_url("https://www.linkedin.com/messaging/") is True
    # THREE SINCE 2026-09-01, when one page.fill entered for publish_post.
    # The number is what this asserts; that none of them is reachable from
    # a READ path is what it means. A fill inside the gated write cannot be
    # reached by this call and the count moving does not change that.
    # FOUR SINCE 2026-09-02, when the profile editor's select_option was
    # sanctioned. The number is what makes growth visible in a diff; the
    # load-bearing half is that an unlisted mutating call still fails.
    # FIVE SINCE 2026-09-04, when set_input_files was sanctioned. That one
    # matters to THIS test more than the others did: the compose surface draws
    # two file inputs, so the entry this count records is reachable in
    # principle from the very page this file is about. It is not reachable
    # from HERE -- writes.UPLOAD_ACTIONS is empty and the call sits behind the
    # two-call token gate -- and that is the property below, asserted rather
    # than assumed.
    assert len(readonly.SANCTIONED_MUTATIONS) == 5
    # NOT ALL CLICKS ANY MORE, and the assertion is re-aimed at the property
    # this test is actually about rather than loosened. It read
    # ``all(kind == "click" ...)`` until 2026-09-01, which was a true
    # statement about the whole allowlist and a PROXY for the thing that
    # matters here: that nothing on a READ path can type. The fill that
    # arrived is inside writes.perform, behind the two-call token gate, and
    # this call cannot reach it -- so the proxy broke while the property held.
    #
    # Asserted directly now: every entry that is NOT a click lives in
    # writes.perform, so no read path owns one.
    for path, function, kind in readonly.SANCTIONED_MUTATIONS:
        if kind != "click":
            assert (path, function) == ("linkedin_server/writes.py", "perform"), (
                path, function, kind,
            )


# ---------------------------------------------------------------------------
# Reconciling 4 -> 0, and settling the InMail surface by READING it
# ---------------------------------------------------------------------------


def test_both_unread_counts_are_reported_and_the_gap_is_explained():
    """4 became 0 between two versions and neither number was wrong.

    The old code counted the word "unread" across the WHOLE document; the new
    code counts it on conversation ROWS. They measure different things, and
    only the row count answers who is waiting -- the page's own filter pill is
    LABELLED "Unread", so the document count sees furniture.

    Both are reported rather than one being chosen, because a tool that
    silently swapped 4 for 0 would leave a reader unable to tell a fixed
    over-count from a new under-count.
    """
    html = (
        '<a aria-label="Unread" href="/messaging/?filter=unread">pill</a>'
        '<div aria-label="Select conversation with A B"><i>UNREAD</i></div>'
        '<div aria-label="Select conversation with C D">quiet</div>'
    )
    out = shape.messaging_overview(html, THREAD_URL)

    assert out["unread"] == 1, "the row count is the one that answers the question"
    assert out["unread_markers_in_document"] > out["unread"]
    assert "furniture" not in out["marker_reconciliation"]  # plain words, not jargon
    assert "ROW count" in out["marker_reconciliation"]
    # And it tells the reader how to report the dangerous direction.
    assert "under-count" in out["marker_reconciliation"]


def test_the_detector_returns_true_on_an_unread_row():
    """A DETECTOR ONLY EVER OBSERVED RETURNING FALSE HAS NOT BEEN SHOWN TO
    WORK. A false zero says "nothing waiting", which he would believe, and it
    is a worse failure than the over-count it replaced.
    """
    for marker in (
        "<i>UNREAD</i>",
        "<span>Unread</span>",
        '<span class="messaging-remove-unread-blue-background"></span>',
    ):
        html = f'<div aria-label="Select conversation with A B">{marker}</div>'
        out = shape.messaging_overview(html, THREAD_URL)
        assert out["unread"] == 1, marker
        assert out["rows"][0]["unread"] is True, marker


@pytest.mark.parametrize(
    "html,seen,navigable",
    [
        (
            '<a href="/messaging/?filter=unread" aria-label="Unread">x</a>',
            ["unread"],
            ["unread"],
        ),
        ('<button aria-label="InMail"><span>InMail</span></button>', ["inmail"], []),
        ("<div>no pills rendered</div>", [], []),
    ],
    ids=["anchor carries the parameter", "button is client-side", "nothing rendered"],
)
def test_the_filter_pills_are_read_not_guessed(html, seen, navigable):
    """SETTLING THE INMAIL QUESTION BY READING, the way apply_route reads the
    apply anchor instead of guessing the apply url.

    A recruiter InMail was visible in the product and absent from the rows
    this server reads. Either it is below the page or InMails are a separate
    surface. Hardcoding a ``?filter=`` guess to chase it would break
    never-ship-a-guessed-body for the sake of looking thorough.

    So the controls are read. An anchor MEASURES the parameter. A button with
    no href means filtering is client-side state and InMails are not reachable
    by navigation at all -- equally a finding, and one the tool states rather
    than hiding behind an empty result.
    """
    out = shape.messaging_filters(html)
    assert out["filters_seen"] == seen
    assert out["navigable_filters"] == navigable
    if navigable:
        assert "MEASURED" in out["verdict"]
    else:
        assert "client-side" in out["verdict"] or "did not render" in out["verdict"]


# ---------------------------------------------------------------------------
# The filter click: narrow, sanctioned, and refusing everything else
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name", ["focused", "other", "unread", "jobs", "connections", "inmail", "starred"]
)
def test_every_permitted_pill_builds_a_selector(name):
    from linkedin_server import dom

    assert dom.assert_permitted_filter(name) == name


@pytest.mark.parametrize(
    "name",
    ["delete", "archive", "send", "report", "block", "", "  ", "button", "*"],
    ids=[
        "delete", "archive", "send", "report", "block",
        "empty", "whitespace", "any button", "wildcard",
    ],
)
def test_anything_outside_the_named_set_is_refused_before_a_selector_exists(name):
    """THE WHOLE OF THE NARROWING. The permission granted is not "may click on
    the messaging page" -- it is "may activate one of these seven pills".

    The name is checked against the fixed list BEFORE any selector is built,
    so an arbitrary string cannot become a click target even in principle.
    Same shape as the launch boundary permitting exactly two Chromium flags
    and refusing a third.
    """
    from linkedin_server import dom

    with pytest.raises(ValueError) as excinfo:
        dom.assert_permitted_filter(name)
    assert "not a messaging filter" in str(excinfo.value)


def test_the_click_is_on_the_sanctioned_list_and_the_list_is_still_short():
    """A click that is not on the allowlist does not exist; one that is has to
    be readable there. The COUNT stays pinned so a third has to argue for
    itself rather than arriving quietly."""
    from linkedin_server import readonly

    assert (
        "linkedin_server/dom.py",
        "activate_messaging_filter",
        "click",
    ) in readonly.SANCTIONED_MUTATIONS
    # THREE SINCE 2026-09-01, when one page.fill entered for publish_post.
    # The number is what this asserts; that none of them is reachable from
    # a READ path is what it means. A fill inside the gated write cannot be
    # reached by this call and the count moving does not change that.
    # FOUR SINCE 2026-09-02, when the profile editor's select_option was
    # sanctioned. The number is what makes growth visible in a diff; the
    # load-bearing half is that an unlisted mutating call still fails.
    # FIVE SINCE 2026-09-04, when set_input_files was sanctioned. That one
    # matters to THIS test more than the others did: the compose surface draws
    # two file inputs, so the entry this count records is reachable in
    # principle from the very page this file is about. It is not reachable
    # from HERE -- writes.UPLOAD_ACTIONS is empty and the call sits behind the
    # two-call token gate. THE COUNT IS ALL THIS TEST ASSERTS ABOUT IT: the
    # reachability property is asserted in
    # test_the_url_guard_still_refuses_compose_even_though_it_was_not_consulted
    # above, and is not repeated here as prose.
    assert len(readonly.SANCTIONED_MUTATIONS) == 5


def test_the_compose_surface_is_still_refused_after_all_of_this():
    """The boundary that must survive every widening in this file.

    Filtering became permitted; SENDING did not. Compose stays on the
    forbidden substring list, which is checked BEFORE the allowlist.
    """
    from linkedin_server import readonly

    assert (
        readonly.is_read_url(
            "https://www.linkedin.com/messaging/compose/?body=hi&interop=msgOverlay"
        )
        is False
    )


# ---------------------------------------------------------------------------
# The invariant that would have caught the enumerator/activator split
# ---------------------------------------------------------------------------

#: Labels LinkedIn could plausibly put on a pill. Only the first is what the
#: old activator demanded; every other one made the two paths disagree.
REAL_LABELS = [
    "InMail",
    "InMail messages",
    "InMail 1 new",
    "Filter by InMail",
    "inmail",
]


@pytest.mark.parametrize("label", REAL_LABELS)
def test_whatever_the_enumerator_SEES_the_activator_can_FIND(label):
    """THE BUG CLASS, PINNED. Not the specific pattern -- the disagreement.

    On his live page, in a single response, the enumerator reported an
    ``inmail`` pill and the activator reported "found 0". Two components read
    the same page and gave opposite answers about whether an element exists.

    The cause was two matchers asking different questions: the enumerator
    asked whether the accessible name CONTAINS the term, the activator rebuilt
    a selector demanding it be EXACTLY "InMail", from a guess about LinkedIn's
    capitalisation. Any real label satisfies the first and fails the second.

    There is one predicate now and both call it, so this asserts the property
    rather than the implementation: anything enumerated as present must be
    findable.
    """
    from linkedin_server import dom

    html = f'<button aria-label="{label}"><span>x</span></button>'
    seen = shape.messaging_filters(html)["filters_seen"]

    assert seen == ["inmail"], f"enumerator missed {label!r}"
    assert dom.filter_name_matches(label, "inmail") is True, (
        f"the enumerator reports {label!r} present but the activator's rule "
        "would not find it -- the two paths have diverged again"
    )


def test_the_shared_rule_still_says_no_to_a_different_pill():
    """A predicate that matched everything would make the test above vacuous
    and would let the activator click the wrong pill."""
    from linkedin_server import dom

    assert dom.filter_name_matches("Focused", "inmail") is False
    assert dom.filter_name_matches("", "inmail") is False
    assert dom.filter_name_matches("Starred", "unread") is False


@pytest.mark.parametrize(
    "html,name,source",
    [
        ('<button aria-label="InMail messages">x</button>', "InMail messages", "aria-label"),
        ('<button class="pill">InMail</button>', "InMail", "text"),
    ],
    ids=["labelled", "text only"],
)
def test_the_enumerator_reports_the_ACCESSIBLE_NAME_and_says_where_it_came_from(
    html, name, source
):
    """A NULL THAT LOOKED LIKE A BUG AND WAS NOT.

    On his live page every pill reported ``aria_label: null`` while the
    activator located and clicked them by name -- which read as the
    enumerator/activator split all over again, in a third component. It was
    not. His pills carry VISIBLE TEXT and no aria-label, so null was correct
    and the FIELD NAME was the defect: it named one attribute while the
    matching uses the ACCESSIBLE NAME, which is aria-label or text.

    ``name_source`` is here so nobody has to ask that question twice: a reader
    can tell "this pill has no aria-label" from "the reader failed".
    """
    out = shape.messaging_filters(html)
    assert out["detail"]["inmail"]["accessible_name"] == name
    assert out["detail"]["inmail"]["name_source"] == source


def test_the_verdict_no_longer_claims_inmails_are_unreachable():
    """The clause the operator challenged, and it was false the moment
    activation shipped. A verdict that contradicts the capability sitting
    beside it in the same response is the going-stale defect this wave keeps
    finding."""
    out = shape.messaging_filters('<button aria-label="InMail">x</button>')
    verdict = out["verdict"]

    assert "which it does not do" not in verdict
    assert "STILL REACHABLE" in verdict
    assert "message_filter" in verdict
