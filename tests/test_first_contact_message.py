"""The FIRST-CONTACT path of ``linkedin_message_from_profile`` (lane L5, the
orchestrator's addendum of 2026-09-28 13:03).

WHAT WAS MEASURED LIVE (the live lane's session 3, on a first-degree profile
the operator named; nothing typed or sent). ``linkedin_read_named_profile`` is
proven live, and the rebuilt reader resolved the person: identity confirmed,
exactly one visible owner's Message control, none foreign. The Message act was
REFUSED twice, by ``6_not_their_conversation``: there was NO conversation with
him, so the press opened a NEW-MESSAGE composer, still on the profile, in about
two seconds -- one bubble on the page, one recipient box, one committed
recipient pill, no title with his name -- and the gate expected a conversation
headed by it. Before the press there was no bubble at all. And the composer is
inside an OPEN SHADOW ROOT: ``page.content()`` and ``querySelectorAll`` do not
see it; Playwright's piercing locator does.

THE CHAIN THIS FILE HOLDS, each link a condition that refuses on doubt:

1. the target is the link he gave, the topcard's identity holds, and no
   composer is open anywhere before the press -- counted by both engines;
2. the pressed control is the owner's one visible Message link, and its
   address names the profile's own member;
3. after the press, exactly one bubble on the page, and it holds the composer
   -- a new-message bubble, one recipient box in it, ONE committed recipient
   of any pill shape, a dismissible one whose drawn text IS the topcard's
   name, the whole of it, an empty search field, a recipient card linking the
   topcard's own profile, and the one Send its own;
4. only then are his words typed; Send is pressed only while 3 still holds;
   afterwards a conversation must exist, headed by that name, holding his
   words -- the receipt, read in place, the name never recorded;
5. the bubble is then closed by its header's close control, found by its
   text. Escape is never pressed: it does not close this bubble.

SESSION 4 FIRED IT (2026-09-28, 17:33): every link held, his words went in,
65 of 65 -- and the last-moment check refused at 4, because Send read DISABLED
straight after the fill. About a second later a skeleton of the same bubble
drew Send without ``disabled``. So (the orchestrator's order of 17:37): the
check now WAITS, bounded, for the bubble's own Send to turn on, then re-reads
everything; and a box that ALREADY holds exactly his words, whole and nothing
else -- a draft LinkedIn kept -- is not typed into again, but goes to that
same wait and check. Any other text in the box refuses, as before. The filled
bubble is BUILT from that session's skeleton, through the same builder.

THE CONVERSATION PATH IS LEFT AS IT WAS, as the addendum ordered: where the
page's own script cannot see the conversation -- in a shadow root -- it
refuses at 6, and where it can see it, it acts as before. Both are held here.

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
the close control removes it; Escape does nothing. Each world below is one
named deviation from that. Nothing in linkedin_server injects a script into a
page.

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
from linkedin_server.errors import WriteAttemptError
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
OWNER_MEMBER = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000002"
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

#: THE SECOND CAPTURE: the same bubble about a second after session 4's fill,
#: Send drawn without ``disabled``, built by ``--kind filled`` from the live
#: lane's gitignored skeleton; the builder printed this digest over that
#: skeleton and prints it over the built file.
BUBBLE_FILLED_FIXTURE = REPO / "tests" / "fixtures" / "synthetic" / "first_contact_bubble_filled.html"
BUBBLE_FILLED = BUBBLE_FILLED_FIXTURE.read_text(encoding="ascii")
FILLED_DIGEST = "ppnjobnklaocacjm"
#: The builder's declared words in the filled editor -- granted as HIS words to
#: model the draft LinkedIn keeps (the builder's TYPED_WORDS; a test says so).
DRAFT_WORDS = "Example words typed into the box and nothing else as they landed."
DRAFT_TARGET = {"profile": LINK, "text": DRAFT_WORDS}

#: THE STAND-IN FOR LINKEDIN'S SCRIPT, installed on every load. ``cfg`` says
#: how this world behaves; each key is one test's deviation from the capture.
BEHAVIOUR = r"""
(cfg) => {
  const host = document.createElement('div');
  host.id = 'interop-outlet';
  document.body.appendChild(host);
  const root = cfg.lightDom ? host : host.attachShadow({ mode: 'open' });
  window.__lane = { pressed: 0, closed: 0, escapes: 0, submitted: 0, preSubmitted: 0, inputs: 0 };
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') window.__lane.escapes += 1;
  }, true);
  if (cfg.unboundLabelled) {
    for (const a of document.querySelectorAll('[id$="Topcard"] a[href*="/messaging/compose/"]')) {
      a.setAttribute('aria-label', 'Message ' + cfg.owner);
      a.setAttribute('href', '/messaging/compose/');
    }
  }
  if (cfg.preOpen) {
    const pre = make();
    pre.querySelector('.msg-connections-typeahead-container').remove();
    pre.querySelector('.msg-overlay-bubble-header__title').textContent = cfg.owner;
    root.appendChild(pre);
    wire(pre, true);
  }
  if (cfg.minimisedBefore) root.appendChild(minimised());
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[href*="/messaging/compose/"]');
    if (!link) return;
    event.preventDefault();
    window.__lane.pressed += 1;
    if (cfg.swapPressedMember) {
      link.setAttribute('href', link.getAttribute('href').replace(/ACoAA[A-Za-z0-9]+/g, cfg.swapPressedMember));
    }
    setTimeout(open, cfg.openDelayMs || 120);
  }, true);
  function make() {
    const wrap = document.createElement('div');
    wrap.innerHTML = cfg.bubble;
    return wrap.querySelector('.msg-overlay-conversation-bubble');
  }
  function minimised() {
    const bubble = make();
    bubble.classList.add('msg-overlay-conversation-bubble--is-minimized');
    bubble.querySelector('.msg-overlay-conversation-bubble__content-wrapper').remove();
    bubble.querySelector('.msg-overlay-bubble-header__title').textContent = cfg.stranger;
    return bubble;
  }
  function open() {
    const count = cfg.twoBubbles ? 2 : 1;
    for (let i = 0; i < count; i += 1) {
      const bubble = make();
      root.appendChild(bubble);
      shape(bubble);
      wire(bubble, false);
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
    if (cfg.extraPill && pill) {
      const other = pill.cloneNode(true);
      other.classList.remove('artdeco-pill--dismiss');
      pill.after(other);
    }
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
    if (cfg.extraCloseLabel) {
      const extra = document.createElement('button');
      extra.className = 'msg-overlay-bubble-header__control artdeco-button';
      extra.setAttribute('aria-label', 'Close all conversations');
      bubble.querySelector('.msg-overlay-bubble-header__controls').appendChild(extra);
    }
    if (cfg.sendOutside) {
      bubble.querySelector('.msg-form__send-button').remove();
      const form = document.createElement('form');
      form.className = 'msg-form';
      form.innerHTML = '<button class="msg-form__send-button" type="submit" disabled>Send</button>';
      root.appendChild(form);
    }
    if (typeof cfg.draftText === 'string') {
      bubble.querySelector('.msg-form__contenteditable p').textContent = cfg.draftText;
    }
    if (cfg.sendDisabledAtOpen) bubble.querySelector('.msg-form__send-button').disabled = true;
  }
  function onTyping(bubble) {
    const pill = bubble.querySelector('button.artdeco-pill--dismiss');
    const kind = cfg.onTyping;
    if (kind === 'secondPill' && pill) pill.after(pill.cloneNode(true));
    if (kind === 'retitle') bubble.querySelector('.msg-overlay-bubble-header__title').textContent = 'Draft';
    if (kind === 'pillText' && pill) pill.querySelector('.artdeco-pill__text').textContent = cfg.stranger;
    if (kind === 'search') bubble.querySelector('input.msg-connections-typeahead__search-field').value = 'Mor';
    if (kind === 'card') {
      for (const a of bubble.querySelectorAll('.msg-s-profile-card a[href]')) a.setAttribute('href', '/in/someone-example-9/');
    }
    if (kind === 'minimise') root.appendChild(minimised());
    if (kind === 'secondBox') {
      const field = bubble.querySelector('input.msg-connections-typeahead__search-field');
      field.after(field.cloneNode(true));
    }
    if (kind === 'boxOutside') {
      const field = document.createElement('input');
      field.className = 'msg-connections-typeahead__search-field';
      root.appendChild(field);
    }
    if (kind === 'sendAway') {
      bubble.querySelector('.msg-form__send-button').remove();
      const form = document.createElement('form');
      form.className = 'msg-form';
      form.innerHTML = '<button class="msg-form__send-button" type="submit">Send</button>';
      root.appendChild(form);
    }
  }
  function wire(bubble, pre) {
    const editor = bubble.querySelector('.msg-form__contenteditable');
    const send = bubble.querySelector('.msg-form__send-button');
    const form = bubble.querySelector('form.msg-form');
    let changed = false;
    let timer = null;
    editor.addEventListener('input', () => {
      window.__lane.inputs += 1;
      const filled = editor.textContent.trim().length > 0;
      if (send && filled && cfg.enableDelayMs) {
        // SESSION 4's TIMING: Send stays disabled as the words land, and turns
        // on a moment later.
        send.disabled = true;
        clearTimeout(timer);
        timer = setTimeout(() => {
          if (editor.textContent.trim().length) send.disabled = false;
        }, cfg.enableDelayMs);
      } else if (send) {
        send.disabled = !filled;
      }
      if (cfg.onTyping && !pre && !changed && editor.textContent.trim().length) {
        changed = true;
        onTyping(bubble);
      }
    });
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      window.__lane.submitted += 1;
      if (pre) window.__lane.preSubmitted += 1;
      if (!cfg.dispatches) return;
      const words = editor.textContent.trim();
      bubble.querySelector('.msg-overlay-bubble-header__title').textContent = cfg.titleAfterSend || cfg.owner;
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
      editor.textContent = cfg.redraftAfterSend || '';
      if (send) send.disabled = true;
      if (cfg.minimisedAfterSend) root.appendChild(minimised());
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


def _cfg(**behaviour) -> dict:
    return {"bubble": BUBBLE, "owner": OWNER, "stranger": STRANGER, "dispatches": True, **behaviour}


class _Navigator:
    """Serves the live-true profile, installs the stand-in, and LANDS on the
    link; records every address asked for."""

    def __init__(self, **behaviour):
        self.cfg = _cfg(**behaviour)
        self.gotos: list[str] = []

    async def goto(self, page, url: str, *, named_profile: bool = False) -> str:
        self.gotos.append(url)
        if url != LINK:
            raise AssertionError(f"the act asked for {url!r}, which this test did not freeze")
        await page.set_content(PROFILE, wait_until="domcontentloaded", timeout=60_000)
        await page.evaluate(BEHAVIOUR, self.cfg)
        return LINK


def _clean(value) -> None:
    """No name the page drew -- the person's, a stranger's -- no headline, and
    no member id reaches a receipt."""
    text = json.dumps(value)
    for needle in (OWNER, STRANGER, HEADLINE, OWNER_MEMBER, STRANGER_MEMBER):
        assert needle not in text, f"{needle!r} leaked into: {text[:400]}"


async def _lane(page) -> dict:
    return await page.evaluate("() => window.__lane")


async def _grant(page, target=None, **behaviour):
    target = TARGET if target is None else target
    block = await preview(MESSAGE, target=target, navigator=_Navigator(**behaviour), page=page)
    return consume(block["to_confirm"], action=MESSAGE.action, target=target)


# ---------------------------------------------------------------------------
# 1. The bubble is the capture's structure
# ---------------------------------------------------------------------------


def _rebuild(source: Path, out: Path, kind: str = "empty") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BUILDER), "--source", str(source), "--out", str(out), "--kind", kind],
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
    """Counts off the committed file. THE CAPTURE'S: one bubble, one title
    "New message", one recipient box holding one committed recipient, one card
    linking the owner's profile, Send disabled. THE BUILDER'S, and DERIVED: the
    close control's words -- the capture reduced them, and the builder wrote
    words fitting their shape; only the first is ever read."""
    assert BUBBLE.count('class="msg-convo-wrapper msg-overlay-conversation-bubble') == 1
    assert BUBBLE.count(">New message<") == 1
    assert BUBBLE.count("artdeco-pill--dismiss") == 1
    assert BUBBLE.count('aria-label="Remove Casey Example"') == 1
    assert BUBBLE.count('href="/in/' + SEGMENT + '/"') == 2
    sends = re.findall(r'<button class="msg-form__send-button[^>]*>', BUBBLE)
    assert len(sends) == 1 and ' disabled' in sends[0] and 'type="submit"' in sends[0], sends
    # DERIVED, written by the builder (its CLOSE_TEXT):
    assert BUBBLE.count(">Close your draft conversation<") == 1


def test_the_filled_bubble_is_a_fixed_point_of_its_builder_and_keeps_its_digest(tmp_path):
    """The second capture's fixture: rebuilt from itself with ``--kind filled``
    it is byte for byte the committed file, and prints the digest the builder
    printed over the live lane's skeleton."""
    out = tmp_path / "rebuilt.html"
    run = _rebuild(BUBBLE_FILLED_FIXTURE, out, kind="filled")
    assert run.returncode == 0, run.stderr
    assert _lf(out.read_bytes()) == _lf(BUBBLE_FILLED_FIXTURE.read_bytes())
    assert _printed(run.stdout, "structure digest") == FILLED_DIGEST
    for label in ("unclassified texts", "unclassified labels", "unclassified attributes",
                  "placeholder texts", "texts to the owner", "texts to the words"):
        assert _printed(run.stdout, label) == "0", (label, run.stdout)


def test_THIS_CONTROL_CAN_FAIL_a_structural_edit_of_the_filled_bubble_changes_its_digest(tmp_path):
    edited = tmp_path / "edited.html"
    stripped = re.sub(r"<svg[^>]*></svg>", "", BUBBLE_FILLED, count=1)
    assert stripped != BUBBLE_FILLED
    edited.write_text(stripped, encoding="ascii")
    run = _rebuild(edited, tmp_path / "rebuilt.html", kind="filled")
    assert run.returncode == 0, run.stderr
    assert _printed(run.stdout, "structure digest") != FILLED_DIGEST


def test_the_draft_words_are_the_builders_declared_words():
    sys.path.insert(0, str(REPO / "scripts"))
    import _build_first_contact_bubble as builder

    assert builder.TYPED_WORDS == DRAFT_WORDS
    assert (len(DRAFT_WORDS), sum(c.isalpha() for c in DRAFT_WORDS)) == (65, 53), (
        "fitted to the shape of the words the capture reduced"
    )


def test_the_filled_bubble_differs_from_the_empty_one_where_the_fill_did():
    """MEASURED, one capture beside the other: after the fill the editor's
    paragraph holds the words where it held a line break, and Send is drawn
    WITHOUT ``disabled``. Everything the chain reads is the same."""
    empty_sends = re.findall(r'<button class="msg-form__send-button[^>]*>', BUBBLE)
    filled_sends = re.findall(r'<button class="msg-form__send-button[^>]*>', BUBBLE_FILLED)
    assert len(empty_sends) == 1 and " disabled" in empty_sends[0]
    assert len(filled_sends) == 1 and " disabled" not in filled_sends[0]
    assert BUBBLE.count("<p><br></p>") == 1 and BUBBLE_FILLED.count("<p><br></p>") == 0
    assert BUBBLE_FILLED.count("<p>" + DRAFT_WORDS + "</p>") == 1
    for drawn in (">New message<", "artdeco-pill--dismiss", 'aria-label="Remove Casey Example"',
                  'href="/in/' + SEGMENT + '/"', ">Close your draft conversation<"):
        assert BUBBLE.count(drawn) == BUBBLE_FILLED.count(drawn), drawn


# ---------------------------------------------------------------------------
# 2. The overlay's shadow root: the page's script cannot see it; the reader can
# ---------------------------------------------------------------------------


async def _open_directly(page, **behaviour) -> None:
    await page.set_content(PROFILE, wait_until="domcontentloaded", timeout=60_000)
    await page.evaluate(BEHAVIOUR, _cfg(**behaviour))
    await page.locator(dom.topcard_message_control_selector()).click()
    await page.locator(named_profile.COMPOSER_EDITOR_SELECTOR).wait_for(state="attached")


async def test_the_page_script_cannot_see_the_shadow_root_and_the_piercing_reader_can(browser_page):
    """THE LIVE FINDING, REPRODUCED: in the overlay's shadow root the page's
    own script counts no composer and no bubble, and the piercing reader finds
    the one bubble and everything the first contact is judged on -- and the
    count "a composer is already open" is now taken by that engine too."""
    await _open_directly(browser_page)
    page_script = await dom.read_named_profile(browser_page)
    assert page_script["composer_editors"] == 0 and page_script["conversation_bubbles"] == 0
    assert page_script["bubble_titles"] == 0
    assert page_script["composer_editors_pierced"] == 1, "the engine the press uses sees it"
    assert page_script["message_member_bound"] is True, "the owner's link names the owner's member"
    facts = await dom.read_bubbles(browser_page)
    assert facts["error"] is None
    assert facts["bubbles"] == [{
        "editor": True, "title_kind": "new_message", "boxes": 1, "pills": 1,
        "pill_names_owner": True, "search_empty": True, "card_matches": True,
        "close_controls": 1, "sends": 1,
    }]


async def test_the_same_bubble_outside_a_shadow_root_reads_the_same(browser_page):
    await _open_directly(browser_page, lightDom=True)
    facts = await dom.read_bubbles(browser_page)
    assert [fact["title_kind"] for fact in facts["bubbles"]] == ["new_message"]
    assert facts["bubbles"][0]["pill_names_owner"] is True


async def test_THIS_CONTROL_CAN_FAIL_the_escape_counter_counts_an_escape(browser_page):
    """The instrument every act below reads as "Escape was never pressed",
    shown counting one -- and the bubble still there after it, as measured
    live."""
    await _open_directly(browser_page)
    await browser_page.keyboard.press("Escape")
    assert (await _lane(browser_page))["escapes"] == 1
    assert len((await dom.read_bubbles(browser_page))["bubbles"]) == 1


@pytest.mark.parametrize(
    "bubble, enabled", [(BUBBLE_FILLED, True), (BUBBLE, False)], ids=["filled", "empty"]
)
async def test_the_send_wait_finds_the_filled_captures_send_and_not_the_empty_ones(
    browser_page, bubble, enabled
):
    """THE WAIT'S ONE CLAIM, on the two captures, each in an open shadow root:
    the Send the filled bubble draws is found without ``disabled`` through the
    piercing engine; the empty bubble's is not, and the wait runs out."""
    await browser_page.set_content("<html><body><div id='host'></div></body></html>")
    await browser_page.evaluate(
        "(markup) => { document.getElementById('host').attachShadow({ mode: 'open' }).innerHTML = markup; }",
        bubble,
    )
    waited = await named_profile.wait_for_send_enabled(browser_page, timeout_ms=600)
    assert waited["enabled"] is enabled, waited
    assert waited["failure"] == (None if enabled else "TimeoutError"), waited


def test_the_send_wait_is_bounded_at_five_seconds():
    assert named_profile.SEND_ENABLED_WAIT_MS == 5_000


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
    assert observed["bubbles"] == 1 and observed["title_kind"] == "new_message"
    assert observed["recipient_boxes_in_bubble"] == 1 and observed["send_in_bubble"] == 1
    assert observed["recipient_pills"] == 1 and observed["recipient_is_theirs"] is True
    assert observed["recipient_search_empty"] is True and observed["recipient_card_is_theirs"] is True
    assert observed["press_names_their_member"] is True
    assert observed["conversation_titles"] == 0, "the page's own script sees no title in the shadow root"
    assert observed["events_with_text"] == 0
    assert receipt["send_gate"]["proceeded"] is True
    assert receipt["send_gate"]["observed"]["first_contact"] is True
    assert receipt["send_gate"]["observed"]["bubbles"] == 1
    assert receipt["clicked"]["clicks_made"] == 3
    assert receipt["clicked"]["opener_clicks"] == 1 and receipt["clicked"]["closer_clicks"] == 1
    assert receipt["typed_text"]["submit_was_pressed"] is True
    assert receipt["verification"]["observed_state"] == named_profile.MESSAGE_SENT
    assert "from 0 to 1" in receipt["verification"]["why"]
    assert receipt["performed"] is True and receipt["verified"] is True
    assert receipt["close_gate"]["proceeded"] is True
    wait = receipt["sent_words_wait"]
    assert wait["appeared"] is True and isinstance(wait["waited_ms"], int) and wait["waited_ms"] >= 0
    assert receipt["send_enabled_wait"]["enabled"] is True
    assert receipt["typed_text"]["text_was_entered"] is True
    assert receipt["typed_text"]["words_left_in_the_box"] is False, "sent, and the bubble closed"
    lane = await _lane(browser_page)
    assert {key: lane[key] for key in ("pressed", "closed", "escapes", "submitted", "preSubmitted")} == {
        "pressed": 1, "closed": 1, "escapes": 0, "submitted": 1, "preSubmitted": 0,
    }
    assert lane["inputs"] >= 1, "his words were typed"
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


async def test_a_first_contact_whose_bubble_is_not_headed_by_the_name_after_send_is_not_read_sent(
    writes_on, browser_page
):
    """SENT needs a conversation headed by the name, read in place: a bubble
    still titled otherwise after the press is no receipt, and nothing is
    closed."""
    grant = await _grant(browser_page)
    receipt = await writes.perform(_Navigator(titleAfterSend="New message"), browser_page, grant)
    assert receipt["send_gate"]["proceeded"] is True
    assert receipt["verification"]["observed_state"] == named_profile.UNKNOWN
    assert receipt["close_gate"] is None
    assert receipt["clicked"]["clicks_made"] == 2 and receipt["clicked"]["closer_clicks"] == 0
    assert (await _lane(browser_page))["closed"] == 0
    _clean(receipt)


# ---------------------------------------------------------------------------
# 3b. Session 4: Send turns on after the words land (the order of 17:37)
# ---------------------------------------------------------------------------


async def test_a_send_that_turns_on_after_the_words_land_is_waited_for_then_pressed(
    writes_on, browser_page
):
    """SESSION 4, REPRODUCED OFFLINE: every link held and the words went in, and
    Send turned on about a second later. The check now waits for it, bounded,
    through the piercing engine, then re-reads everything -- and the message
    goes, is read SENT in place, and the bubble is closed."""
    grant = await _grant(browser_page)
    receipt = await writes.perform(_Navigator(enableDelayMs=1_000), browser_page, grant)
    send = receipt["send_gate"]
    assert send["proceeded"] is True, send
    assert send["observed"]["send_enabled"] is True and send["observed"]["words_exact"] is True
    wait = receipt["send_enabled_wait"]
    assert wait["enabled"] is True and wait["waited_ms"] >= 500, wait
    assert receipt["verification"]["observed_state"] == named_profile.MESSAGE_SENT
    assert receipt["clicked"]["clicks_made"] == 3 and receipt["close_gate"]["proceeded"] is True
    lane = await _lane(browser_page)
    assert lane["submitted"] == 1 and lane["closed"] == 1 and lane["escapes"] == 0
    _clean(receipt)


async def test_a_send_that_never_turns_on_is_refused_after_the_bounded_wait(
    writes_on, browser_page, monkeypatch
):
    """The wait decides nothing: a Send still disabled at its end refuses at 4,
    as before, nothing pressed, and the receipt says his words are in the box."""
    monkeypatch.setattr(named_profile, "SEND_ENABLED_WAIT_MS", 1_500)
    grant = await _grant(browser_page)
    receipt = await writes.perform(_Navigator(enableDelayMs=600_000), browser_page, grant)
    send = receipt["send_gate"]
    assert send["proceeded"] is False and send["refused_condition"] == "4_fill_not_landed", send
    wait = receipt["send_enabled_wait"]
    assert wait["enabled"] is False and wait["waited_ms"] >= 1_400, wait
    assert receipt["clicked"]["clicks_made"] == 1
    assert receipt["typed_text"]["text_was_entered"] is True
    assert receipt["typed_text"]["submit_was_pressed"] is False
    assert receipt["typed_text"]["left_in_the_composer"] is True
    # SESSION 4'S RECEIPT READ "unknown", do not retry, about a message that
    # never left. SEND WAS NEVER PRESSED, SO IT IS "not sent" (the
    # orchestrator's call of 2026-09-28 19:48): the words are still in the
    # box, and a retry is safe.
    verification = receipt["verification"]
    assert verification["observed_state"] == named_profile.MESSAGE_NOT_SENT, verification
    assert "SEND WAS NEVER PRESSED" in verification["why"]
    assert "A RETRY IS SAFE" in verification["why"] and "Do NOT retry" not in verification["why"]
    assert "Your words are still in the box" in verification["why"]
    assert receipt["typed_text"]["words_left_in_the_box"] is True
    assert (await _lane(browser_page))["submitted"] == 0
    _clean(receipt)


async def test_a_send_pressed_but_unconfirmed_stays_unknown_and_says_do_not_retry(
    writes_on, browser_page
):
    """THE OTHER SIDE OF THE CALL OF 19:48: Send WAS pressed, the box emptied,
    and the bubble is not a conversation headed by the name -- the message
    may have gone. That alone stays "unknown", with its do-not-retry: a retry
    could send it twice."""
    grant = await _grant(browser_page)
    receipt = await writes.perform(_Navigator(titleAfterSend="New message"), browser_page, grant)
    assert receipt["typed_text"]["submit_was_pressed"] is True
    verification = receipt["verification"]
    assert verification["observed_state"] == named_profile.UNKNOWN, verification
    assert "Do NOT retry" in verification["why"] and "A RETRY IS SAFE" not in verification["why"]
    assert receipt["typed_text"]["words_left_in_the_box"] is False
    assert (await _lane(browser_page))["submitted"] == 1
    _clean(receipt)


# ---------------------------------------------------------------------------
# 3c. The draft rule (the order of 17:37): his words already in the box
# ---------------------------------------------------------------------------


async def test_a_draft_holding_exactly_his_words_is_not_typed_again_and_is_sent(
    writes_on, browser_page
):
    """DERIVED WORLD, from the second capture: the press opens the new message
    with his words already in the box -- the shape session 4's fill left, as a
    draft LinkedIn kept. Nothing is typed; the same wait and the same
    last-moment check run; Send is pressed; SENT is read in place."""
    grant = await _grant(browser_page, target=DRAFT_TARGET)
    receipt = await writes.perform(_Navigator(bubble=BUBBLE_FILLED), browser_page, grant)
    opened = receipt["opened_conversation_gate"]
    assert opened["proceeded"] is True, opened
    assert opened["observed"]["editor_empty"] is False
    assert opened["observed"]["editor_holds_the_words"] is True
    typed = receipt["typed_text"]
    assert typed["text_was_entered"] is False and typed["words_were_already_in_the_box"] is True
    assert typed["submit_was_pressed"] is True
    assert receipt["send_gate"]["proceeded"] is True
    assert receipt["send_enabled_wait"]["enabled"] is True
    assert receipt["verification"]["observed_state"] == named_profile.MESSAGE_SENT
    assert receipt["clicked"]["clicks_made"] == 3 and receipt["close_gate"]["proceeded"] is True
    lane = await _lane(browser_page)
    assert lane["inputs"] == 0, "nothing was typed"
    assert lane["submitted"] == 1 and lane["closed"] == 1
    _clean(receipt)


@pytest.mark.parametrize(
    "target, behaviour",
    [
        (TARGET, {"bubble": BUBBLE_FILLED}),
        (DRAFT_TARGET, {"bubble": BUBBLE_FILLED, "draftText": DRAFT_WORDS + " PS"}),
        (DRAFT_TARGET, {"bubble": BUBBLE_FILLED, "draftText": DRAFT_WORDS[:30]}),
    ],
    ids=["other-words", "his-words-and-more", "part-of-his-words"],
)
async def test_any_other_text_already_in_the_box_refuses_as_before(
    writes_on, browser_page, target, behaviour
):
    grant = await _grant(browser_page, target=target)
    receipt = await writes.perform(_Navigator(**behaviour), browser_page, grant)
    opened = receipt["opened_conversation_gate"]
    assert opened["proceeded"] is False and opened["refused_condition"] == "8_not_empty", opened
    assert opened["observed"]["editor_holds_the_words"] is False
    assert receipt["clicked"]["clicks_made"] == 1
    assert receipt["typed_text"]["text_was_entered"] is False
    assert receipt["send_enabled_wait"] is None and receipt["send_gate"] is None
    lane = await _lane(browser_page)
    assert lane["inputs"] == 0 and lane["submitted"] == 0
    _clean(receipt)


async def test_a_draft_whose_send_never_turns_on_is_refused_after_the_wait(
    writes_on, browser_page, monkeypatch
):
    monkeypatch.setattr(named_profile, "SEND_ENABLED_WAIT_MS", 1_500)
    grant = await _grant(browser_page, target=DRAFT_TARGET)
    receipt = await writes.perform(
        _Navigator(bubble=BUBBLE_FILLED, sendDisabledAtOpen=True), browser_page, grant
    )
    assert receipt["opened_conversation_gate"]["proceeded"] is True
    send = receipt["send_gate"]
    assert send["proceeded"] is False and send["refused_condition"] == "4_fill_not_landed", send
    assert receipt["send_enabled_wait"]["enabled"] is False
    typed = receipt["typed_text"]
    assert typed["text_was_entered"] is False and typed["words_were_already_in_the_box"] is True
    assert typed["submit_was_pressed"] is False and typed["left_in_the_composer"] is True
    assert typed["words_left_in_the_box"] is True
    verification = receipt["verification"]
    assert verification["observed_state"] == named_profile.MESSAGE_NOT_SENT, verification
    assert "sends them without typing them again" in verification["why"]
    assert receipt["clicked"]["clicks_made"] == 1
    lane = await _lane(browser_page)
    assert lane["inputs"] == 0 and lane["submitted"] == 0
    _clean(receipt)


async def test_a_conversation_whose_send_was_never_pressed_reads_not_sent_too(
    writes_on, browser_page
):
    """The call of 19:48 is about the press, not the path: where the page's own
    script sees the conversation and its title changes as his words land, the
    last-moment check refuses, Send is never pressed -- "not sent", a retry
    safe, and this path's box must be cleared first (it has no draft rule)."""
    grant = await _grant(browser_page)
    receipt = await writes.perform(
        _Navigator(asConversation=True, lightDom=True, onTyping="retitle"), browser_page, grant
    )
    assert receipt["message_path"] == "conversation"
    send = receipt["send_gate"]
    assert send["proceeded"] is False and send["refused_condition"] == "6_not_their_conversation"
    verification = receipt["verification"]
    assert verification["observed_state"] == named_profile.MESSAGE_NOT_SENT, verification
    assert "SEND WAS NEVER PRESSED" in verification["why"]
    assert "refused until it is cleared" in verification["why"]
    assert receipt["typed_text"]["words_left_in_the_box"] is True
    assert (await _lane(browser_page))["submitted"] == 0
    _clean(receipt)


async def test_the_draft_rule_is_the_first_contacts_only(writes_on, browser_page):
    """A conversation that already exists is left as it was: its box holding
    his words -- even exactly -- refuses at 8, where the page's own script can
    see the conversation."""
    grant = await _grant(browser_page, target=DRAFT_TARGET)
    receipt = await writes.perform(
        _Navigator(bubble=BUBBLE_FILLED, asConversation=True, lightDom=True), browser_page, grant
    )
    opened = receipt["opened_conversation_gate"]
    assert receipt["message_path"] == "conversation"
    assert opened["proceeded"] is False and opened["refused_condition"] == "8_not_empty", opened
    assert (await _lane(browser_page))["submitted"] == 0
    _clean(receipt)


# ---------------------------------------------------------------------------
# 4. Every doubt refuses, before a word is typed
# ---------------------------------------------------------------------------


async def test_a_composer_already_open_before_the_press_is_refused_before_anything_is_pressed(
    writes_on, browser_page
):
    """THE COLD REVIEW'S DEFECT (2026-09-28): a conversation already open in the
    shadow root, titled with the name, and the press's own bubble slow to draw.
    The page's own count saw no composer, so the act pressed, found the old
    conversation, and sent into it. The count is now taken by the engine the
    press uses, before the press, and nothing is pressed."""
    grant = await _grant(browser_page)
    with pytest.raises(WriteAttemptError, match="already open"):
        await writes.perform(_Navigator(preOpen=True, openDelayMs=3000), browser_page, grant)
    lane = await _lane(browser_page)
    assert lane["pressed"] == 0 and lane["submitted"] == 0 and lane["preSubmitted"] == 0


async def test_the_preview_refuses_a_composer_already_open_in_the_shadow_root(writes_on, browser_page):
    """The same count at the preview: no confirmation is issued."""
    with pytest.raises(WriteAttemptError, match="already open") as refused:
        await preview(MESSAGE, target=TARGET, navigator=_Navigator(preOpen=True), page=browser_page)
    _clean(str(refused.value))


@pytest.mark.parametrize(
    "behaviour, condition",
    [
        ({"noPill": True}, "7_recipient_box"),
        ({"title": "Draft"}, "6f_not_a_new_message"),
        ({"secondPill": True}, "6f_not_one_recipient"),
        ({"extraPill": True}, "6f_not_one_recipient"),
        ({"pillText": STRANGER}, "6f_recipient_not_theirs"),
        ({"pillText": OWNER + " Jr"}, "6f_recipient_not_theirs"),
        ({"searchValue": "Mor"}, "6f_another_recipient_on_the_way"),
        ({"swapPressedMember": STRANGER_MEMBER}, "6f_press_not_bound_to_them"),
        ({"unboundLabelled": True}, "6f_press_not_bound_to_them"),
        ({"cardHref": "/in/someone-example-9/"}, "6f_card_not_theirs"),
        ({"sendOutside": True}, "6f_send_not_in_the_bubble"),
        ({"minimisedBefore": True}, "6f_not_one_bubble"),
        ({"twoBubbles": True}, "5_not_one_conversation"),
    ],
    ids=[
        "nobody-committed", "not-a-new-message", "two-recipients",
        "a-second-recipient-of-another-pill", "a-stranger-committed", "more-than-the-name",
        "a-second-recipient-being-typed", "the-pressed-link-not-theirs",
        "a-labelled-link-naming-no-member", "the-card-not-theirs", "the-send-outside-the-bubble",
        "a-minimised-bubble-beside-it", "two-bubbles",
    ],
)
async def test_every_doubt_about_the_recipient_refuses_before_a_word_is_typed(
    writes_on, browser_page, behaviour, condition
):
    grant = await _grant(browser_page, **behaviour)
    receipt = await writes.perform(_Navigator(**behaviour), browser_page, grant)
    opened = receipt["opened_conversation_gate"]
    assert opened["proceeded"] is False and opened["refused_condition"] == condition, opened
    assert receipt["clicked"]["clicks_made"] == 1
    assert receipt["typed_text"]["text_was_entered"] is False
    assert receipt["performed"] is False
    assert receipt["close_gate"] is None
    _clean(receipt)


async def test_a_labelled_link_naming_no_member_is_refused_on_the_member_not_the_label(
    writes_on, browser_page
):
    """The pressed link's LABEL names the owner, so it is the owner's control;
    its ADDRESS names no member, so the recipient LinkedIn commits cannot be
    tied to the link he gave. The chain's second link is the address."""
    grant = await _grant(browser_page, unboundLabelled=True)
    receipt = await writes.perform(_Navigator(unboundLabelled=True), browser_page, grant)
    observed = receipt["opened_conversation_gate"]["observed"]
    assert observed["recipient_is_theirs"] is True and observed["recipient_card_is_theirs"] is True
    assert observed["press_names_their_member"] is False
    _clean(receipt)


@pytest.mark.parametrize(
    "kind",
    ["secondPill", "retitle", "pillText", "search", "card", "minimise", "secondBox",
     "boxOutside", "sendAway"],
)
async def test_a_change_to_the_recipient_while_typing_stops_send(writes_on, browser_page, kind):
    """The chain's third link, held again with his words in the box: each of
    its readings changes as the words land -- a second recipient, a title that
    is not a new message, somebody else's name, a search being typed, a card
    linking somebody else, a second bubble, a second box in the bubble or
    beside it, the Send moved out of the bubble -- and Send is not pressed."""
    grant = await _grant(browser_page)
    receipt = await writes.perform(_Navigator(onTyping=kind), browser_page, grant)
    assert receipt["opened_conversation_gate"]["proceeded"] is True
    send = receipt["send_gate"]
    assert send["proceeded"] is False and send["refused_condition"] == "6f_recipient_changed", send
    assert receipt["clicked"]["clicks_made"] == 1
    assert receipt["verification"]["observed_state"] == named_profile.MESSAGE_NOT_SENT
    assert receipt["close_gate"] is None
    assert (await _lane(browser_page))["submitted"] == 0
    _clean(receipt)


# ---------------------------------------------------------------------------
# 5. The close step refuses on doubt too, and presses nothing in its place
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "behaviour, condition",
    [
        ({"noCloseControl": True}, "2_not_one_close_control"),
        ({"minimisedAfterSend": True}, "1_not_one_bubble"),
        ({"extraCloseLabel": True}, "3_selector_count"),
        ({"redraftAfterSend": "Example draft"}, "4_words_in_the_box"),
    ],
    ids=["no-close-control", "a-second-bubble-after-send", "a-second-close-name",
         "words-back-in-the-box"],
)
async def test_the_close_step_refuses_on_doubt_and_the_message_still_reads_sent(
    writes_on, browser_page, behaviour, condition
):
    grant = await _grant(browser_page)
    receipt = await writes.perform(_Navigator(**behaviour), browser_page, grant)
    assert receipt["verification"]["observed_state"] == named_profile.MESSAGE_SENT
    assert receipt["close_gate"]["proceeded"] is False
    assert receipt["close_gate"]["refused_condition"] == condition, receipt["close_gate"]
    assert receipt["clicked"]["clicks_made"] == 2 and receipt["clicked"]["closer_clicks"] == 0
    lane = await _lane(browser_page)
    assert lane["closed"] == 0 and lane["escapes"] == 0, "and nothing else was pressed instead"
    _clean(receipt)


# ---------------------------------------------------------------------------
# 6. The conversation path, left as it was
# ---------------------------------------------------------------------------


async def test_a_conversation_in_a_shadow_root_is_refused_as_the_conversation_path_always_was(
    writes_on, browser_page
):
    """THE CONVERSATION PATH IS LEFT AS IT WAS (the addendum of 13:03). Its
    "whose conversation" is the page's own reading, which cannot see into the
    shadow root, so a conversation drawn there -- DERIVED: the capture's bubble
    with its recipient box removed and its title the person's name -- is
    refused at 6 with nothing typed. The piercing reading, which this path does
    not act on, is reported beside it."""
    grant = await _grant(browser_page)
    receipt = await writes.perform(_Navigator(asConversation=True), browser_page, grant)
    opened = receipt["opened_conversation_gate"]
    assert opened["proceeded"] is False, opened
    assert opened["refused_condition"] == "6_not_their_conversation"
    assert receipt["message_path"] == "conversation"
    assert opened["observed"]["conversation_titles"] == 0
    assert opened["observed"]["title_kind"] == "owner"
    assert receipt["typed_text"]["text_was_entered"] is False
    assert receipt["clicked"]["clicks_made"] == 1 and receipt["close_gate"] is None
    assert (await _lane(browser_page))["submitted"] == 0
    _clean(receipt)


async def test_the_same_conversation_where_the_page_script_sees_it_is_taken_as_before(
    writes_on, browser_page
):
    """And where the page's own script CAN see it, the path is what it was:
    the conversation headed by the name takes his words, reads SENT in place,
    and is not closed."""
    grant = await _grant(browser_page)
    receipt = await writes.perform(
        _Navigator(asConversation=True, lightDom=True), browser_page, grant
    )
    opened = receipt["opened_conversation_gate"]
    assert opened["proceeded"] is True, opened
    assert receipt["message_path"] == "conversation"
    assert opened["observed"]["conversation_titles"] == 1
    assert opened["observed"]["conversation_names_the_owner"] is True
    assert receipt["verification"]["observed_state"] == named_profile.MESSAGE_SENT
    assert receipt["close_gate"] is None and receipt["clicked"]["clicks_made"] == 2
    assert receipt["sent_words_wait"] is None
    _clean(receipt)
