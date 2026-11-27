"""Answering one pending invitation he names -- census ``N 15`` (accept), ``N 16`` (ignore) and ``N 10`` (withdraw) -- built to ready-to-fire, unfired.

WHAT THE THREE ACTS ARE. On his own invitation manager, ONE press of the
row's own control -- ``Accept`` or ``Ignore`` on the received tab,
``Withdraw`` on the Sent tab -- in the ONE row whose member links all name
the profile he linked. Behind ``writes_enabled()`` and the single-use grant.

THE PAGES ARE REAL. Every world is live session 11's tracked copy with
LinkedIn's words put back by keyed shape
(``tests/fixtures/synthetic/live11_invitations_words.html`` and
``live11_invitations_sent_words.html``, lane readers-net26), with SYNTHETIC
member segments planted into the rows' own links by asserted edits (the
capture reduces every segment to ``x``). What a press DRAWS is not measured:
every world below that answers a press -- a row removed, a dialog drawn --
is a fixture CHOICE derived by an asserted edit and named in its label.

WHY SEVERAL SCENARIOS SHARE ONE TEST. A browser launch and close is the
whole price of a test here (``tests/test_leave_group.py`` measured it), so
each check loops over its scenarios on one browser, every assertion carrying
the scenario's label.

NOTHING HERE REACHES LINKEDIN: a local headless Chromium, every request the
page starts refused by its own route before the network guard has to.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from linkedin_server import invitation_acts as ia
from linkedin_server import outward_classes, readonly, server, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

REPO = Path(__file__).resolve().parents[1]
RECEIVED_WORDS = (REPO / "tests/fixtures/synthetic/live11_invitations_words.html").read_text(encoding="ascii")
SENT_WORDS = (REPO / "tests/fixtures/synthetic/live11_invitations_sent_words.html").read_text(encoding="ascii")
RECEIVED_COPY = (REPO / "tests/fixtures/live11/invitations.html").read_text(encoding="ascii")
SENT_COPY = (REPO / "tests/fixtures/live11/invitations_sent.html").read_text(encoding="ascii")

ACCEPT, IGNORE, WITHDRAW = ia.ACCEPT, ia.IGNORE, ia.WITHDRAW
SPECS = {action: spec_for_action(action) for action in ia.ACTIONS}

#: Synthetic members, one per row, in row order. Declared shapes, not people.
INVITERS = ("example-inviter-one", "example-inviter-two")
INVITEES = tuple(f"example-invitee-{n}" for n in ("one", "two", "three", "four", "five"))
_X_LINK = 'href="https://www.linkedin.com/in/x/"'


def _link(segment: str) -> str:
    return f"https://www.linkedin.com/in/{segment}/"


def _row_spans(html: str, marker: str) -> list[tuple[int, int]]:
    """Each row's span, from its ``role="listitem"`` element to the next one,
    for every row holding ``marker``."""
    starts = [m.start() for m in re.finditer(r'<div [^>]*role="listitem"', html)]
    spans = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(html)
        if marker in html[start:end]:
            spans.append((start, end))
    return spans


def plant_members(html: str, marker: str, segments: tuple[str, ...]) -> str:
    """Re-point every ``/in/x/`` link of the k-th row holding ``marker`` to the
    k-th synthetic segment. ASSERTED: the rows and their links are counted."""
    spans = _row_spans(html, marker)
    assert len(spans) >= len(segments), (len(spans), len(segments))
    out, cursor = [], 0
    for (start, end), segment in zip(spans, segments):
        row = html[start:end]
        assert row.count(_X_LINK) >= 1, "a row holding the control links no member"
        out.append(html[cursor:start])
        out.append(row.replace(_X_LINK, f'href="{_link(segment)}"'))
        cursor = end
    out.append(html[cursor:])
    planted = "".join(out)
    assert planted != html
    return planted


def drop_row(html: str, segment: str) -> str:
    """The world after an answer landed: the row linking ``segment`` gone."""
    spans = _row_spans(html, _link(segment))
    assert len(spans) == 1, spans
    start, end = spans[0]
    return html[:start] + html[end:]


def edit_row(html: str, segment: str, old: str, new: str) -> str:
    """One ASSERTED edit inside the row linking ``segment``."""
    start, end = _row_spans(html, _link(segment))[0]
    row = html[start:end]
    assert old in row, old
    return html[:start] + row.replace(old, new, 1) + html[end:]


_RECEIVED_MARK = ">\nwants to connect\n<"
_SENT_MARK = ">\nWithdraw\n<"

RECEIVED = plant_members(RECEIVED_WORDS, _RECEIVED_MARK, INVITERS)
SENT = plant_members(SENT_WORDS, _SENT_MARK, INVITEES)
WORLD = {ACCEPT: RECEIVED, IGNORE: RECEIVED, WITHDRAW: SENT}
MEMBER = {ACCEPT: INVITERS[0], IGNORE: INVITERS[1], WITHDRAW: INVITEES[2]}

#: A press-answering world: the control's click is the page's own witness, and
#: optionally draws a dialog of two buttons whose presses are counted too.
_SCRIPT = """<script>
window.__controlPresses = 0; window.__dialogPresses = 0;
document.addEventListener('click', function (e) {
  var t = e.target.closest('button, a');
  if (!t) return;
  if (t.closest('[role=dialog]')) { window.__dialogPresses += 1; e.preventDefault(); return; }
  var word = (t.textContent || '').replace(/\\s+/g, ' ').trim();
  if (word === '%(word)s') {
    window.__controlPresses += 1; e.preventDefault();
    if (%(dialog)s) {
      var d = document.createElement('div'); d.setAttribute('role', 'dialog');
      d.innerHTML = '<button type="button">%(confirm)s</button><button type="button">Cancel</button>';
      document.body.appendChild(d);
    }
  }
}, true);
</script>"""


def answering(action: str, *, dialog: bool = False) -> str:
    """The action's world with its control's press witnessed (and a dialog
    drawn on the press, if asked). DERIVED: the script is the test's choice."""
    word = ia.CONTROL[action][1]
    confirm = "Withdraw" if action == WITHDRAW else word
    script = _SCRIPT % {"word": word, "dialog": "true" if dialog else "false", "confirm": confirm}
    html = WORLD[action]
    assert html.count("</body>") == 1
    return html.replace("</body>", script + "</body>")


class Navigator:
    """Serves frozen worlds for the ONE address an act loads, in order, records
    every ask, and reads THE PAGE'S OWN WITNESS of what was pressed before the
    next world replaces it (the actor never grades itself)."""

    def __init__(self, url: str, *worlds: str, landed: str = ""):
        self.url = url
        self.worlds = list(worlds)
        self.gotos: list[str] = []
        self.landed = landed
        self.pressed: list[dict[str, int]] = []

    async def goto(self, page, url: str, **_kwargs) -> str:
        self.gotos.append(url)
        if url != self.url:
            raise AssertionError(f"the gate asked for {url!r}, which this test did not freeze")
        self.pressed.append(
            await page.evaluate(
                "() => ({control: window.__controlPresses || 0, dialog: window.__dialogPresses || 0})"
            )
        )
        html = self.worlds.pop(0) if len(self.worlds) > 1 else self.worlds[0]
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return self.landed or url


@pytest.fixture
async def page(browser_page):
    """The shared local page, refusing every request it would start. An abort
    that lands nowhere, so a press whose link navigates leaves the page put."""

    async def _refuse(route):
        await route.abort("aborted")

    await browser_page.route("**/*", _refuse)
    return browser_page


@pytest.fixture(autouse=True)
def _no_grants_survive_a_test():
    yield
    writes.discard_all()


async def _read(page, html: str, action: str, segment: str):
    await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
    return ia.row_verdict(await ia.read_rows(page, action, segment), action)


def _no_member(text: str, label: str = "") -> None:
    """No planted member's segment leaves through a refusal or a sentence."""
    for segment in INVITERS + INVITEES:
        assert segment not in text, f"[{label}] a member segment leaked: {text[:300]}"


# ---------------------------------------------------------------------------
# 0. The target: a link or a member id he gives, never a name (no browser)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("action", ia.ACTIONS)
def test_the_target_is_his_link_canonicalised_and_a_name_is_refused(action):
    spec = SPECS[action]
    assert spec.target_kind == "invitation_profile"
    assert writes._target_for(spec, "www.linkedin.com/in/example-inviter-one") == _link("example-inviter-one")
    for name in ("Example Inviter", "example", ""):
        with pytest.raises(WriteAttemptError):
            writes._target_for(spec, name)


def test_a_selector_is_never_built_from_an_unsafe_segment():
    for bad in ("a'b", "a]b", "a b", "", "x" * 201):
        assert ia.checked_segment(bad) is None
        with pytest.raises(ValueError):
            ia.control_selector(ACCEPT, bad)
    assert ia.checked_segment("Example-Inviter-One") == "example-inviter-one"


def test_no_selector_names_a_label():
    """Every button's and link's aria-label carries the member's name live; the
    aim is structural and LinkedIn's whole visible words, never a label."""
    for action in ia.ACTIONS:
        for selector in (ia.control_selector(action, "example-x"), ia.rows_selector(action),
                         ia.member_rows_selector("example-x")):
            assert "aria-label" not in selector and "@name" not in selector


def test_a_reader_failure_is_reported_by_type_only():
    _f, state, why = ia.row_verdict({"error": "TimeoutError"}, ACCEPT)
    assert state == ia.UNKNOWN and "TimeoutError" in why
    _f, _s, why = ia.row_verdict({"error": "x'); drop"}, ACCEPT)
    assert "an exception" in why


def test_the_verification_needs_exactly_one_row_fewer():
    before = {"invitation_rows_on_the_tab": 2}
    gone = {"sent_links": 1, "sent_current": 0, "any_current": 1, "rows": 1, "rows_for_target": 0}
    assert ia.verification_verdict(before, gone, ACCEPT)[1] == ia.NOT_PENDING
    assert ia.verification_verdict(before, dict(gone, rows=0), ACCEPT)[1] == ia.UNKNOWN
    assert ia.verification_verdict(before, dict(gone, rows=2), ACCEPT)[1] == ia.UNKNOWN
    still = dict(gone, rows=2, rows_for_target=1)
    assert ia.verification_verdict(before, still, ACCEPT)[1] == ia.PENDING


def test_the_after_press_note_says_what_opened_and_never_decides():
    opened = ia.after_press_note(
        {"dialogs": 1, "buttons_in_dialogs": 2, "dialog_buttons_by_word": {"Withdraw": 1, "Cancel": 1},
         "address_moved": False}, WITHDRAW)
    assert opened["further_step_opened"] is True
    assert "A FURTHER STEP OPENED AND WAS NOT TAKEN" in opened["what_this_means"]
    moved = ia.after_press_note({"address_moved": True}, WITHDRAW)
    assert moved["further_step_opened"] is False and "ADDRESS MOVED" in moved["what_this_means"]
    broken = ia.after_press_note({"error": "TimeoutError"}, ACCEPT)
    assert broken["further_step_opened"] is None


# ---------------------------------------------------------------------------
# 1. The captures draw what the readers read
# ---------------------------------------------------------------------------


async def test_the_readers_over_the_captures(page):
    # THE RECEIVED TAB: three invitations on the capture, but the Page's
    # newsletter invitation has no member and no 'wants to connect' line, so
    # two rows are invitations to connect.
    facts, state, why = await _read(page, RECEIVED, ACCEPT, INVITERS[0])
    assert state == ia.PENDING, why
    assert (facts["tab_read"], facts["invitation_rows_on_the_tab"]) == ("received", 2)
    assert facts["rows_of_the_member_you_linked"] == 1 and facts["names_read"] is False
    # THE SENT TAB: five.
    facts, state, why = await _read(page, SENT, WITHDRAW, INVITEES[2])
    assert state == ia.PENDING, why
    assert (facts["tab_read"], facts["invitation_rows_on_the_tab"]) == ("sent", 5)

    # THE AMBIGUITY RULE ON THE REAL CAPTURE: every segment is the skeleton's
    # x, so every row carries "that member" -- refused, never chosen.
    _f, state, why = await _read(page, RECEIVED_WORDS, ACCEPT, "x")
    assert state == ia.UNKNOWN and "2 invitation rows" in why
    _f, state, why = await _read(page, SENT_WORDS, WITHDRAW, "x")
    assert state == ia.UNKNOWN and "5 invitation rows" in why

    # THE RED: the tracked copies, whose Accept, Ignore and Withdraw are the
    # skeleton's x, draw no invitation row by LinkedIn's words.
    for action, copy in ((ACCEPT, RECEIVED_COPY), (WITHDRAW, SENT_COPY)):
        planted = copy.replace(_X_LINK, f'href="{_link(MEMBER[action])}"')
        facts, state, _why = await _read(page, planted, action, MEMBER[action])
        assert (state, facts["invitation_rows_on_the_tab"]) == (ia.UNKNOWN, 0), action

    # A member on no row; the other tab read as this one's.
    assert (await _read(page, RECEIVED, ACCEPT, "example-nobody"))[1] == ia.NOT_PENDING
    facts, state, _why = await _read(page, SENT, ACCEPT, INVITEES[0])
    assert (state, facts["tab_read"]) == (ia.UNKNOWN, "sent")
    facts, state, _why = await _read(page, RECEIVED, WITHDRAW, INVITERS[0])
    assert (state, facts["tab_read"]) == (ia.UNKNOWN, "received")
    # THE STRIP DECIDES THE TAB, not only the rows' shape: the received page
    # with the strip's Sent link current -- its invitation rows still drawn --
    # is not the received tab, and the row is not answered there. (Added when
    # the mutation that disabled the strip check came back GREEN: on the two
    # captures the rows' shapes alone had kept the tabs apart.)
    sent_current = RECEIVED.replace(' aria-current="true" href="https://www.linkedin.com/mynetwork/invitation-manager/received"',
                                    ' href="https://www.linkedin.com/mynetwork/invitation-manager/received"', 1)
    sent_current = sent_current.replace(' href="https://www.linkedin.com/mynetwork/invitation-manager/sent">',
                                        ' aria-current="true" href="https://www.linkedin.com/mynetwork/invitation-manager/sent">', 1)
    assert sent_current != RECEIVED
    facts, state, _why = await _read(page, sent_current, ACCEPT, INVITERS[0])
    assert (state, facts["tab_read"]) == (ia.UNKNOWN, "sent")
    assert facts["rows_of_the_member_you_linked"] == 1, "the row is drawn; the strip refuses it"

    # A row whose links name the member AND somebody else is no row of his.
    stranger = edit_row(RECEIVED, INVITERS[0], f'href="{_link(INVITERS[0])}"',
                        'href="https://www.linkedin.com/in/example-stranger/"')
    facts, state, _why = await _read(page, stranger, ACCEPT, INVITERS[0])
    assert state == ia.NOT_PENDING and facts["list_items_linking_that_member"] == 1
    # A row with a third button is not an invitation.
    third = edit_row(RECEIVED, INVITERS[0], "</button>",
                     '</button><button type="button"><span>x</span></button>')
    assert (await _read(page, third, ACCEPT, INVITERS[0]))[1] == ia.NOT_PENDING
    # A row without the 'wants to connect' line is not an invitation to connect.
    no_line = edit_row(RECEIVED, INVITERS[0], "\nwants to connect\n", "\nx\n")
    assert (await _read(page, no_line, ACCEPT, INVITERS[0]))[1] == ia.NOT_PENDING


# ---------------------------------------------------------------------------
# 2. The preview: one load, the constant tab, a token minted, no name
# ---------------------------------------------------------------------------


async def test_the_preview_mints_on_the_tab_it_acts_on_and_refuses_every_other_world(writes_on, page):
    for action, spec in SPECS.items():
        nav = Navigator(spec.url_template, WORLD[action])
        block = await preview(spec, target=_link(MEMBER[action]), navigator=nav, page=page)
        assert nav.gotos == [spec.url_template], action
        assert block["where"]["profile"] == _link(MEMBER[action])
        assert block["where"]["what_the_page_showed"]["rows_of_the_member_you_linked"] == 1
        assert (block["direction"]["currently"], block["direction"]["after"]) == (ia.PENDING, ia.NOT_PENDING)
        assert block["read"]["same_page_as_the_action"] is True
        assert block["reversibility_class"] == "STILL-UNKNOWN"
        assert isinstance(block["to_confirm"], str) and block["to_confirm"], action
        writes.discard_all()

        unplanted = RECEIVED_WORDS if spec.url_template == ia.RECEIVED_URL else SENT_WORDS
        for label, html, target in (
            ("member-on-no-row", WORLD[action], "example-nobody"),
            ("the-unplanted-capture", unplanted, "x"),
            ("the-other-tab", SENT if action != WITHDRAW else RECEIVED, MEMBER[action]),
        ):
            with pytest.raises(WriteAttemptError) as raised:
                await preview(spec, target=_link(target), navigator=Navigator(spec.url_template, html), page=page)
            assert not writes._GRANTS, f"[{action} {label}] a refused preview minted a grant"
            _no_member(str(raised.value), f"{action} {label}")

    # A LANDING OFF THE TAB vetoes, and is not quoted. (LinkedIn's own strip
    # spelling of the received tab, `.../invitation-manager/received/`, stood
    # here until 2026-11-27: live session 12 LANDED there (load 28), and lane
    # net7 admitted it and made `invitation_manager.landed_on_received` --
    # which this act's landing check reads -- accept it, on the orchestrator's
    # ruling for N 13. A sub-path of it is off the tab.)
    spec = SPECS[ACCEPT]
    elsewhere = "https://www.linkedin.com/mynetwork/invitation-manager/received/elsewhere/"
    with pytest.raises(WriteAttemptError) as raised:
        await preview(spec, target=_link(INVITERS[0]),
                      navigator=Navigator(spec.url_template, RECEIVED, landed=elsewhere), page=page)
    assert "elsewhere/" not in str(raised.value)
    assert not writes._GRANTS


# ---------------------------------------------------------------------------
# 3. THE THREE CONTROLS -- writes off, another target or verb, a second use
# ---------------------------------------------------------------------------


async def test_control_1_every_tool_refuses_with_writes_off(monkeypatch):
    monkeypatch.delenv(writes.WRITES_FLAG, raising=False)
    spec = SPECS[ACCEPT]
    nav = Navigator(spec.url_template, RECEIVED)
    with pytest.raises(WriteAttemptError, match="disabled"):
        await preview(spec, target=_link(INVITERS[0]), navigator=nav, page=object())
    assert nav.gotos == []
    for tool in (server.linkedin_accept_invitation_to_connect,
                 server.linkedin_ignore_invitation_to_connect,
                 server.linkedin_withdraw_invitation):
        off = await tool(_link(INVITERS[0]))
        assert off["error"] == "writes_disabled" and off["performed"] is False


async def test_controls_2_and_3_a_grant_binds_member_and_verb_and_is_used_once(writes_on, page):
    spec = SPECS[ACCEPT]
    block = await preview(spec, target=_link(INVITERS[0]), navigator=Navigator(spec.url_template, RECEIVED), page=page)
    with pytest.raises(WriteAttemptError, match="minted for target"):
        consume(block["to_confirm"], action=ACCEPT, target=_link(INVITERS[1]))
    block = await preview(spec, target=_link(INVITERS[0]), navigator=Navigator(spec.url_template, RECEIVED), page=page)
    for verb in (IGNORE, WITHDRAW, "connect_from_profile"):
        with pytest.raises(WriteAttemptError, match="minted for 'accept_invitation_to_connect'"):
            consume(block["to_confirm"], action=verb, target=_link(INVITERS[0]))

    spec = SPECS[IGNORE]
    target = _link(MEMBER[IGNORE])
    block = await preview(spec, target=target, navigator=Navigator(spec.url_template, RECEIVED), page=page)
    grant = consume(block["to_confirm"], action=IGNORE, target=target)
    first = Navigator(spec.url_template, answering(IGNORE), drop_row(RECEIVED, MEMBER[IGNORE]))
    receipt = await writes.perform(first, page, grant)
    assert receipt["clicked"]["clicks_made"] == 1
    second = Navigator(spec.url_template, RECEIVED)
    with pytest.raises(WriteAttemptError, match="already been used once"):
        await writes.perform(second, page, grant)
    assert second.gotos == []


# ---------------------------------------------------------------------------
# 4. End to end: one press, a fresh render decides
# ---------------------------------------------------------------------------


async def _run(page, action: str, before: str, after: str) -> tuple[dict, Navigator]:
    spec = SPECS[action]
    target = _link(MEMBER[action])
    block = await preview(spec, target=target, navigator=Navigator(spec.url_template, WORLD[action]), page=page)
    grant = consume(block["to_confirm"], action=action, target=target)
    act = Navigator(spec.url_template, before, after)
    receipt = await writes.perform(act, page, grant)
    assert act.gotos == [spec.url_template, spec.url_template], "the press and the fresh render"
    return receipt, act


async def test_one_press_and_a_fresh_render_decide(writes_on, page):
    for action in ia.ACTIONS:
        # PERFORMED: the fresh render draws one invitation row fewer, none his.
        receipt, act = await _run(page, action, answering(action), drop_row(WORLD[action], MEMBER[action]))
        assert receipt["clicked"]["clicks_made"] == 1, action
        assert receipt["clicked"]["selector"] == ia.control_selector(action, MEMBER[action])
        assert receipt["clicked"]["error"] is None, (action, receipt["clicked"]["error"])
        assert receipt["clicked"]["state_before"] == ia.PENDING
        # THE PAGE'S OWN WITNESS: one press of the control, none anywhere else.
        assert act.pressed[-1] == {"control": 1, "dialog": 0}, (action, act.pressed)
        after = receipt["invitation_after_press"]
        assert after["further_step_opened"] is False and after["address_moved"] is False, after
        assert receipt["verification"]["observed_state"] == ia.NOT_PENDING
        assert receipt["performed"] is True and receipt["verified"] is True, action
        _no_member(json.dumps(receipt["verification"]), action)
        _no_member(after["what_this_means"], action)

        # NOT PERFORMED: the fresh render still draws the row.
        receipt, _act = await _run(page, action, answering(action), WORLD[action])
        assert receipt["verification"]["observed_state"] == ia.PENDING, action
        assert receipt["performed"] is False, action

    # A HALF-DRAWN FRESH RENDER is unknown, never an answer.
    empty = drop_row(drop_row(RECEIVED, INVITERS[0]), INVITERS[1])
    receipt, _act = await _run(page, ACCEPT, answering(ACCEPT), empty)
    assert receipt["verification"]["observed_state"] == ia.UNKNOWN
    assert receipt["performed"] == writes.UNKNOWN


async def test_the_withdraw_confirmation_is_counted_and_never_answered(writes_on, page):
    """THE J-19 SHAPE: Withdraw draws LinkedIn's documented pop-up (DERIVED
    here: a dialog of 'Withdraw' and 'Cancel'), and NOTHING in it is pressed --
    the page's own counters say so -- so the fresh render still draws the row
    and the receipt says not performed, with the pop-up's reading."""
    receipt, act = await _run(page, WITHDRAW, answering(WITHDRAW, dialog=True), SENT)
    assert receipt["clicked"]["clicks_made"] == 1
    assert act.pressed[-1] == {"control": 1, "dialog": 0}, act.pressed
    after = receipt["invitation_after_press"]
    assert after["further_step_opened"] is True
    assert after["dialogs"] + after["alertdialogs"] == 1
    assert after["buttons_in_dialogs"] == 2
    assert after["dialog_buttons_by_word"]["Withdraw"] == 1
    assert after["dialog_buttons_by_word"]["Cancel"] == 1
    assert "A FURTHER STEP OPENED AND WAS NOT TAKEN" in after["what_this_means"]
    assert receipt["verification"]["observed_state"] == ia.PENDING
    assert receipt["performed"] is False


# ---------------------------------------------------------------------------
# 5. The tables, the tools and the records name the three acts
# ---------------------------------------------------------------------------


def test_the_tables_name_all_three():
    for action, spec in SPECS.items():
        assert action in writes.PERFORMABLE
        assert action in writes.STRICT_PRESS_ACTIONS
        assert action not in writes._TOGGLE_ACTIONS
        assert action in writes._WHERE_TO_LOOK
        assert "RE-RENDERED" in writes._VERIFIED_FROM[action]
        assert writes.anchor_label_for(spec) == ia.CONTROL[action][1]
        assert writes.grant_is_possible(spec)
        assert spec.exempt_substring == "invitation"
        assert spec.state_from == "invitation_manager"
        assert readonly.name_implies_write(spec.tool_name)
        assert callable(getattr(server, spec.tool_name, None))
        assert spec.url_pattern.match(spec.url_template)
    assert SPECS[ACCEPT].url_template == SPECS[IGNORE].url_template == ia.RECEIVED_URL
    assert SPECS[WITHDRAW].url_template == ia.SENT_URL


def test_the_withdraw_record_is_built_and_the_page_invitation_waits_on_its_own():
    record = outward_classes.OUTWARD_CLASS_SPECS["withdraw_invitation"]
    assert record.status == "BUILT" and record.census_rows == ("N 10",)
    page_record = outward_classes.OUTWARD_CLASS_SPECS["withdraw_page_follow_invitation"]
    assert page_record.status == "BLOCKED" and page_record.census_rows == ("N 12",)
