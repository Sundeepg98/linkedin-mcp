"""The FIRST-CONTACT path of ``linkedin_message_from_profile`` (lane L5, the
orchestrator's addendum of 2026-09-28 13:03).

WHAT WAS MEASURED LIVE (the live lane's session 3, on a first-degree profile
the operator named; nothing typed or sent). ``linkedin_read_named_profile`` is
proven live, and the rebuilt reader resolved the person: identity confirmed,
exactly one visible owner's Message control, none foreign. The Message act was
REFUSED twice, by ``6_not_their_conversation``: there was NO conversation with
him, so the press opened a NEW-MESSAGE composer, still on the profile, in about
two seconds -- one recipient box, one committed recipient pill, no title with
his name -- and the gate expected a conversation headed by it. And the composer
is inside an OPEN SHADOW ROOT: ``page.content()`` and ``querySelectorAll`` do
not see it; Playwright's piercing locator does.

THE CHAIN THIS FILE HOLDS, each link a condition that refuses on doubt:

1. the target is the link he gave, and the topcard's identity holds;
2. the pressed control is the owner's one visible Message link, and its
   address names the profile's own member;
3. after the press, exactly one bubble holds a composer -- a new-message
   bubble, one recipient box, ONE committed recipient whose text IS the
   topcard's name, the whole of it, an empty search field, and a recipient
   card linking the topcard's own profile;
4. only then are his words typed; Send is pressed only while 3 still holds;
   afterwards a conversation must exist, headed by that name, holding his
   words -- the receipt, read in place, the name never recorded;
5. the bubble is then closed by its header's close control, found by its
   text. Escape is never pressed: it does not close this bubble.

THE FIXTURES. The profile is the page built from the live capture
(``tests/fixtures/synthetic/named_profile_live.html``); the bubble is BUILT
from the live lane's TRACKED COPY of the one the press opened --
``tests/fixtures/live3/m1_composer_bubble.html``, the one live-true source --
into ``tests/fixtures/synthetic/first_contact_bubble.html`` by
``scripts/_build_first_contact_bubble.py``, peopled by the same declared
synthetic person. A script of THIS FILE stands in for LinkedIn's: pressing the
owner's composer link opens the bubble INSIDE AN OPEN SHADOW ROOT, as the live
page does; typing enables Send; Send, where this test says it dispatches,
turns the bubble into a conversation headed by the name, holding the words;
the close control removes it; Escape does nothing. Nothing in linkedin_server
injects a script into a page.

NOTHING HERE REACHES LINKEDIN: a local headless Chromium and ``set_content``.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from linkedin_server import dom, named_profile, writes
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

REPO = Path(__file__).resolve().parent.parent
BUILDER = REPO / "scripts" / "_build_first_contact_bubble.py"
#: THE ONE LIVE-TRUE SOURCE: the live lane's tracked copy of the bubble.
SOURCE = REPO / "tests" / "fixtures" / "live3" / "m1_composer_bubble.html"
BUBBLE_FIXTURE = REPO / "tests" / "fixtures" / "synthetic" / "first_contact_bubble.html"
BUBBLE = BUBBLE_FIXTURE.read_text(encoding="ascii")
PROFILE = (REPO / "tests" / "fixtures" / "synthetic" / "named_profile_live.html").read_text(
    encoding="ascii"
)

MESSAGE = spec_for_action("message_from_profile")
SEGMENT = "casey-example-3f9a"
LINK = "https://www.linkedin.com/in/" + SEGMENT + "/"
OWNER = "Casey Example"
HEADLINE = "Invented headline for a synthetic person"
STRANGER = "Morgan Example"
STRANGER_MEMBER = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000003"
TEXT = "Thursday works for me, speak then."
TARGET = {"profile": LINK, "text": TEXT}

#: THE STRUCTURE THE CAPTURE HAS: tags and nesting, as the builder prints it
#: over the tracked source -- and printed, the same day, over the gitignored
#: skeleton that copy was made from (lane L5, 2026-09-28; the record says so).
#: A structural hand edit of the fixture, or of the source, changes it.
STRUCTURE_DIGEST = "ligiiccbckljhmoo"

#: THE STAND-IN FOR LINKEDIN'S SCRIPT, installed on every load. ``cfg`` says
#: how this world behaves; each key is one test's deviation from the capture.
BEHAVIOUR = r"""
(cfg) => {
  const host = document.createElement('div');
  host.id = 'interop-outlet';
  document.body.appendChild(host);
  const root = cfg.lightDom ? host : host.attachShadow({ mode: 'open' });
  window.__lane = { pressed: 0, closed: 0, escapes: 0 };
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') window.__lane.escapes += 1;
  }, true);
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[href*="/messaging/compose/"]');
    if (!link) return;
    event.preventDefault();
    window.__lane.pressed += 1;
    if (cfg.swapPressedMember) {
      link.setAttribute('href', link.getAttribute('href').replace(/ACoAA[A-Za-z0-9]+/g, cfg.swapPressedMember));
    }
    setTimeout(open, 120);
  }, true);
  function open() {
    const count = cfg.twoBubbles ? 2 : 1;
    for (let i = 0; i < count; i += 1) {
      const wrap = document.createElement('div');
      wrap.innerHTML = cfg.bubble;
      const bubble = wrap.querySelector('.msg-overlay-conversation-bubble');
      root.appendChild(bubble);
      shape(bubble);
      wire(bubble);
    }
  }
  function shape(bubble) {
    const pill = bubble.querySelector('button.artdeco-pill--dismiss');
    if (cfg.asConversation) {
      bubble.querySelector('.msg-connections-typeahead-container').remove();
      bubble.querySelector('.msg-overlay-bubble-header__title').textContent = cfg.owner;
    }
    if (cfg.noPill && pill) pill.remove();
    if (cfg.secondPill && pill) pill.after(pill.cloneNode(true));
    if (cfg.pillText && pill) pill.querySelector('.artdeco-pill__text').textContent = cfg.pillText;
    if (cfg.searchValue) bubble.querySelector('input.msg-connections-typeahead__search-field').value = cfg.searchValue;
    if (cfg.title) bubble.querySelector('.msg-overlay-bubble-header__title').textContent = cfg.title;
    if (cfg.cardHref) {
      for (const a of bubble.querySelectorAll('.msg-s-profile-card a[href]')) a.setAttribute('href', cfg.cardHref);
    }
    if (cfg.noCloseControl) {
      for (const b of bubble.querySelectorAll('.msg-overlay-bubble-header__control')) {
        if (/^Close\b/.test((b.textContent || '').trim())) b.remove();
      }
    }
  }
  function wire(bubble) {
    const editor = bubble.querySelector('.msg-form__contenteditable');
    const send = bubble.querySelector('.msg-form__send-button');
    const form = bubble.querySelector('form.msg-form');
    editor.addEventListener('input', () => {
      send.disabled = editor.textContent.trim().length === 0;
      if (cfg.pillAddedOnTyping && editor.textContent.trim().length) {
        const pill = bubble.querySelector('button.artdeco-pill--dismiss');
        if (pill && bubble.querySelectorAll('button.artdeco-pill--dismiss').length === 1) {
          pill.after(pill.cloneNode(true));
        }
      }
    });
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!cfg.dispatches) return;
      const words = editor.textContent.trim();
      bubble.querySelector('.msg-overlay-bubble-header__title').textContent = cfg.owner;
      const typeahead = bubble.querySelector('.msg-connections-typeahead-container');
      if (typeahead) typeahead.remove();
      const list = document.createElement('ul');
      list.className = 'msg-s-message-list-content';
      const li = document.createElement('li');
      li.className = 'msg-s-message-list__event clearfix msg-s-message-list__last-msg-';
      li.innerHTML = '<div class="msg-s-event-listitem msg-s-event-listitem--last-in-group">'
        + '<p class="msg-s-event-listitem__body t-14"></p></div>';
      li.querySelector('p').textContent = words;
      list.appendChild(li);
      form.before(list);
      editor.textContent = '';
      send.disabled = true;
    });
    for (const b of bubble.querySelectorAll('.msg-overlay-bubble-header__control')) {
      b.addEventListener('click', () => {
        if (/^Close\b/.test((b.textContent || '').trim())) {
          window.__lane.closed += 1;
          bubble.remove();
        }
      });
    }
  }
}
"""


class _Navigator:
    """Serves the live-true profile, installs the stand-in, and LANDS on the
    link; records every address asked for."""

    def __init__(self, **behaviour):
        self.cfg = {"bubble": BUBBLE, "owner": OWNER, "dispatches": True, **behaviour}
        self.gotos: list[str] = []

    async def goto(self, page, url: str, *, named_profile: bool = False) -> str:
        self.gotos.append(url)
        if url != LINK:
            raise AssertionError(f"the act asked for {url!r}, which this test did not freeze")
        await page.set_content(PROFILE, wait_until="domcontentloaded", timeout=60_000)
        await page.evaluate(BEHAVIOUR, self.cfg)
        return LINK


def _clean(value) -> None:
    """No name the page drew -- the person's, a stranger's -- and no headline
    reaches a receipt."""
    text = json.dumps(value)
    for needle in (OWNER, STRANGER, HEADLINE):
        assert needle not in text, f"{needle!r} leaked into: {text[:400]}"


async def _lane(page) -> dict:
    return await page.evaluate("() => window.__lane")


async def _grant(page, **behaviour):
    block = await preview(MESSAGE, target=TARGET, navigator=_Navigator(**behaviour), page=page)
    return consume(block["to_confirm"], action=MESSAGE.action, target=TARGET)


# ---------------------------------------------------------------------------
# 1. The bubble is the capture's structure
# ---------------------------------------------------------------------------


def _rebuild(source: Path, out: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BUILDER), "--source", str(source), "--out", str(out)],
        capture_output=True, text=True, cwd=REPO,
    )


def _lf(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def _printed(stdout: str, label: str) -> str:
    lines = [line for line in stdout.splitlines() if line.startswith(label)]
    assert len(lines) == 1, stdout
    return lines[0][len(label):].strip()


def test_the_bubble_is_a_fixed_point_of_its_committed_builder(tmp_path):
    out = tmp_path / "rebuilt.html"
    run = _rebuild(BUBBLE_FIXTURE, out)
    assert run.returncode == 0, run.stderr
    assert _lf(out.read_bytes()) == _lf(BUBBLE_FIXTURE.read_bytes())
    for label in ("unclassified texts", "unclassified labels", "unclassified attributes",
                  "placeholder texts", "texts to the owner"):
        assert _printed(run.stdout, label) == "0", (label, run.stdout)


def test_the_committed_bubble_is_the_builders_output_from_the_tracked_source(tmp_path):
    """ONE LIVE-TRUE SOURCE, AND THE FIXTURE RE-DERIVED FROM IT: the builder,
    run over the live lane's tracked copy, writes the committed fixture byte
    for byte, and prints the structure digest pinned here. Anyone can re-derive
    both from tracked files."""
    out = tmp_path / "rebuilt.html"
    run = _rebuild(SOURCE, out)
    assert run.returncode == 0, run.stderr
    assert _lf(out.read_bytes()) == _lf(BUBBLE_FIXTURE.read_bytes())
    assert _printed(run.stdout, "structure digest") == STRUCTURE_DIGEST
    assert _printed(run.stdout, "texts to the owner") == "2"
    assert _printed(run.stdout, "derived texts") == "4"
    for label in ("unclassified texts", "unclassified labels", "unclassified attributes"):
        assert _printed(run.stdout, label) == "0", (label, run.stdout)


def test_THIS_CONTROL_CAN_FAIL_a_structural_edit_of_the_source_changes_the_digest(tmp_path):
    source = SOURCE.read_text(encoding="ascii")
    edited_source = re.sub(r"<svg[^>]*>.*?</svg>", "", source, count=1, flags=re.S)
    assert edited_source != source
    edited = tmp_path / "source.html"
    edited.write_text(edited_source, encoding="ascii")
    run = _rebuild(edited, tmp_path / "rebuilt.html")
    assert run.returncode == 0, run.stderr
    assert _printed(run.stdout, "structure digest") != STRUCTURE_DIGEST


def test_THIS_CONTROL_CAN_FAIL_a_structural_hand_edit_changes_the_digest(tmp_path):
    edited = tmp_path / "edited.html"
    stripped = re.sub(r"<svg[^>]*></svg>", "", BUBBLE)
    assert stripped != BUBBLE
    edited.write_text(stripped, encoding="ascii")
    run = _rebuild(edited, tmp_path / "rebuilt.html")
    assert run.returncode == 0, run.stderr
    assert _printed(run.stdout, "structure digest") != STRUCTURE_DIGEST


def test_THIS_CONTROL_CAN_FAIL_a_hand_edit_breaks_the_fixed_point(tmp_path):
    edited = tmp_path / "edited.html"
    edited.write_text(BUBBLE.replace(">New message<", ">New messages<"), encoding="ascii")
    out = tmp_path / "rebuilt.html"
    run = _rebuild(edited, out)
    assert run.returncode == 0, run.stderr
    assert out.read_bytes() != edited.read_bytes()
    assert _printed(run.stdout, "unclassified texts") == "1"


def test_the_words_the_builder_keeps_are_the_words_the_live_lane_kept():
    sys.path.insert(0, str(REPO / "scripts"))
    import _build_first_contact_bubble as builder
    import _probe_live_lane_session_2 as live

    assert builder.KEPT_WORDS <= live.FURNITURE, builder.KEPT_WORDS - live.FURNITURE
    assert builder.KEPT_LABELS <= live.FURNITURE, builder.KEPT_LABELS - live.FURNITURE


def test_the_bubble_draws_what_the_capture_drew():
    """Counts off the committed file: one bubble, one title "New message",
    one recipient box, one committed recipient named for the owner, one card
    linking the owner's profile, one close control, Send disabled."""
    assert BUBBLE.count('class="msg-convo-wrapper msg-overlay-conversation-bubble') == 1
    assert BUBBLE.count(">New message<") == 1
    assert BUBBLE.count("artdeco-pill--dismiss") == 1
    assert BUBBLE.count('aria-label="Remove Casey Example"') == 1
    assert BUBBLE.count('href="/in/' + SEGMENT + '/"') == 2
    assert BUBBLE.count(">Close your draft conversation<") == 1
    sends = re.findall(r'<button class="msg-form__send-button[^>]*>', BUBBLE)
    assert len(sends) == 1 and ' disabled' in sends[0] and 'type="submit"' in sends[0], sends


# ---------------------------------------------------------------------------
# 2. The overlay's shadow root: the page's script cannot see it; the reader can
# ---------------------------------------------------------------------------


async def _open_directly(page, **behaviour) -> None:
    await page.set_content(PROFILE, wait_until="domcontentloaded", timeout=60_000)
    cfg = {"bubble": BUBBLE, "owner": OWNER, "dispatches": True, **behaviour}
    await page.evaluate(BEHAVIOUR, cfg)
    await page.locator(dom.topcard_message_control_selector()).click()
    await page.locator(named_profile.COMPOSER_EDITOR_SELECTOR).wait_for(state="attached")


async def test_the_page_script_cannot_see_the_shadow_root_and_the_piercing_reader_can(browser_page):
    """THE LIVE FINDING, REPRODUCED: in the overlay's shadow root the page's
    own script counts no composer and no bubble, and the piercing reader finds
    the one bubble and everything the first contact is judged on."""
    await _open_directly(browser_page)
    page_script = await dom.read_named_profile(browser_page)
    assert page_script["composer_editors"] == 0 and page_script["conversation_bubbles"] == 0
    assert page_script["bubble_titles"] == 0
    assert page_script["message_member_bound"] is True, "the owner's link names the owner's member"
    facts = await dom.read_bubbles(browser_page)
    assert facts["error"] is None
    assert facts["bubbles"] == [{
        "editor": True, "title_kind": "new_message", "boxes": 1, "pills": 1,
        "pill_names_owner": True, "search_empty": True, "card_matches": True,
        "close_controls": 1,
    }]


async def test_the_same_bubble_outside_a_shadow_root_reads_the_same(browser_page):
    await _open_directly(browser_page, lightDom=True)
    facts = await dom.read_bubbles(browser_page)
    assert [fact["title_kind"] for fact in facts["bubbles"]] == ["new_message"]
    assert facts["bubbles"][0]["pill_names_owner"] is True


# ---------------------------------------------------------------------------
# 3. The act, end to end
# ---------------------------------------------------------------------------


async def test_a_first_contact_is_sent_read_in_place_and_closed(writes_on, browser_page):
    grant = await _grant(browser_page)
    act = _Navigator()
    receipt = await writes.perform(act, browser_page, grant)
    assert act.gotos == [LINK], "one load; the new message is read where it opened"
    opened = receipt["opened_conversation_gate"]
    assert opened["proceeded"] is True and opened["refused_condition"] is None, opened
    assert receipt["message_path"] == "first_contact"
    observed = opened["observed"]
    assert observed["title_kind"] == "new_message"
    assert observed["recipient_pills"] == 1 and observed["recipient_is_theirs"] is True
    assert observed["recipient_search_empty"] is True and observed["recipient_card_is_theirs"] is True
    assert observed["press_names_their_member"] is True
    assert observed["conversation_titles"] == 0, "the page's own script sees no title in the shadow root"
    assert observed["events_with_text"] == 0
    assert receipt["send_gate"]["proceeded"] is True
    assert receipt["send_gate"]["observed"]["first_contact"] is True
    assert receipt["clicked"]["clicks_made"] == 3
    assert receipt["clicked"]["opener_clicks"] == 1 and receipt["clicked"]["closer_clicks"] == 1
    assert receipt["typed_text"]["submit_was_pressed"] is True
    assert receipt["verification"]["observed_state"] == named_profile.MESSAGE_SENT
    assert "from 0 to 1" in receipt["verification"]["why"]
    assert receipt["performed"] is True and receipt["verified"] is True
    assert receipt["close_gate"]["proceeded"] is True
    lane = await _lane(browser_page)
    assert lane == {"pressed": 1, "closed": 1, "escapes": 0}
    assert await browser_page.locator(named_profile.BUBBLE_SELECTOR).count() == 0
    _clean(receipt)


async def test_a_first_contact_whose_words_never_left_the_box_is_not_closed(writes_on, browser_page):
    grant = await _grant(browser_page)
    receipt = await writes.perform(_Navigator(dispatches=False), browser_page, grant)
    assert receipt["opened_conversation_gate"]["proceeded"] is True, receipt["opened_conversation_gate"]
    assert receipt["message_path"] == "first_contact"
    assert receipt["clicked"]["clicks_made"] == 2 and receipt["clicked"]["closer_clicks"] == 0
    assert receipt["verification"]["observed_state"] == named_profile.MESSAGE_NOT_SENT
    assert receipt["close_gate"] is None
    assert receipt["performed"] is False
    assert (await _lane(browser_page))["closed"] == 0
    editor = browser_page.locator(named_profile.COMPOSER_EDITOR_SELECTOR)
    assert await editor.inner_text() == TEXT, "his words stay in the box on his screen"
    _clean(receipt)


# ---------------------------------------------------------------------------
# 4. Every doubt refuses, before a word is typed
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "behaviour, condition",
    [
        ({"noPill": True}, "7_recipient_box"),
        ({"title": "Draft"}, "6f_not_a_new_message"),
        ({"secondPill": True}, "6f_not_one_recipient"),
        ({"pillText": STRANGER}, "6f_recipient_not_theirs"),
        ({"pillText": OWNER + " Jr"}, "6f_recipient_not_theirs"),
        ({"searchValue": "Mor"}, "6f_another_recipient_on_the_way"),
        ({"swapPressedMember": STRANGER_MEMBER}, "6f_press_not_bound_to_them"),
        ({"cardHref": "/in/someone-example-9/"}, "6f_card_not_theirs"),
        ({"twoBubbles": True}, "5_not_one_conversation"),
    ],
    ids=[
        "nobody-committed", "not-a-new-message", "two-recipients", "a-stranger-committed",
        "more-than-the-name", "a-second-recipient-being-typed", "the-pressed-link-not-theirs",
        "the-card-not-theirs", "two-bubbles",
    ],
)
async def test_every_doubt_about_the_recipient_refuses_before_a_word_is_typed(
    writes_on, browser_page, behaviour, condition
):
    grant = await _grant(browser_page)
    receipt = await writes.perform(_Navigator(**behaviour), browser_page, grant)
    opened = receipt["opened_conversation_gate"]
    assert opened["proceeded"] is False and opened["refused_condition"] == condition, opened
    assert receipt["clicked"]["clicks_made"] == 1
    assert receipt["typed_text"]["text_was_entered"] is False
    assert receipt["performed"] is False
    assert receipt["close_gate"] is None
    _clean(receipt)


async def test_a_recipient_added_while_typing_stops_send(writes_on, browser_page):
    """The chain's third link, held again with his words in the box: a second
    recipient appears as the words land, and Send is not pressed."""
    grant = await _grant(browser_page)
    receipt = await writes.perform(_Navigator(pillAddedOnTyping=True), browser_page, grant)
    assert receipt["opened_conversation_gate"]["proceeded"] is True
    send = receipt["send_gate"]
    assert send["proceeded"] is False and send["refused_condition"] == "6f_recipient_changed"
    assert receipt["clicked"]["clicks_made"] == 1
    assert receipt["verification"]["observed_state"] == named_profile.MESSAGE_NOT_SENT
    assert receipt["close_gate"] is None
    _clean(receipt)


async def test_no_close_control_leaves_the_bubble_and_the_message_still_reads_sent(
    writes_on, browser_page
):
    grant = await _grant(browser_page)
    receipt = await writes.perform(_Navigator(noCloseControl=True), browser_page, grant)
    assert receipt["verification"]["observed_state"] == named_profile.MESSAGE_SENT
    assert receipt["close_gate"]["proceeded"] is False
    assert receipt["close_gate"]["refused_condition"] == "2_not_one_close_control"
    assert receipt["clicked"]["clicks_made"] == 2 and receipt["clicked"]["closer_clicks"] == 0
    lane = await _lane(browser_page)
    assert lane["closed"] == 0 and lane["escapes"] == 0, "and nothing else was pressed instead"
    _clean(receipt)


# ---------------------------------------------------------------------------
# 5. The existing path, in the shadow root the live overlay lives in
# ---------------------------------------------------------------------------


async def test_a_conversation_headed_by_the_name_in_a_shadow_root_is_found_and_not_closed(
    writes_on, browser_page
):
    """The one fix the existing path was given: its "whose conversation"
    takes the piercing reading too. DERIVED world: the capture's bubble with
    its recipient box removed and its title the person's name -- the shape of
    a conversation that already exists."""
    grant = await _grant(browser_page)
    receipt = await writes.perform(_Navigator(asConversation=True), browser_page, grant)
    opened = receipt["opened_conversation_gate"]
    assert opened["proceeded"] is True, opened
    assert receipt["message_path"] == "conversation"
    assert opened["observed"]["conversation_titles"] == 0
    assert opened["observed"]["conversation_names_the_owner"] is True
    assert receipt["verification"]["observed_state"] == named_profile.MESSAGE_SENT
    assert receipt["close_gate"] is None and receipt["clicked"]["clicks_made"] == 2
    _clean(receipt)
