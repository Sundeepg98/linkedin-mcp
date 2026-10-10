"""``send_attachment`` -- census rows ``M M14`` / ``M M15`` / ``M M18`` -- one file
into one conversation he names, built behind the grant and unfired (lane U).

WHAT IS AIMED AT A REAL CAPTURE AND WHAT IS NOT, said once so every test below
can be read against it:

* THE TWO FILE INPUTS: real. ``tests/fixtures/live3/presence.html`` (the live
  lane's session 3) draws a conversation's reply form whose two
  ``input[type=file]`` each share a ``div.msg-form__upload-attachment`` with ONE
  labelled button. ``test_the_aim_resolves_on_the_real_capture`` runs the
  shipped selectors over that capture itself. Its skeleton keeps no attribute
  values, so the ``accept`` declarations -- the aim's cross-check -- come from
  the 2026-09-05 live reading, as the synthetic thread fixture already
  carries them.
* WHAT THE FORM DRAWS ONCE A FILE IS ATTACHED, and how a sent attachment
  draws: NOT captured. The worlds below draw the file's NAME by a script of
  their own -- SYNTHETIC, and declared so -- which is exactly why these rows
  stay GAP: the read-back and the verification are aimed at a property (the
  name drawn), not at markup anyone has seen.

NOTHING HERE REACHES LINKEDIN. Every page is a frozen world served into a
local headless Chromium; no file of the operator's is read -- each test writes
its own bytes into a temporary upload root.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from linkedin_server import attachments, config, server, threads, uploads, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_messaging_threads import OTHER_THREAD_ID, THREAD, THREAD_ID, _derive
from tests.test_send_reply import _Navigator
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

_ACTION = "send_attachment"
_SPEC = spec_for_action(_ACTION)
URL = threads.thread_url(THREAD_ID)
PNG = b"\x89PNG\r\n\x1a\n" + b"benign-test-pixels|" * 30
PDF = b"%PDF-1.7\n" + b"benign test document\n" * 20

_REAL_CAPTURE = pathlib.Path(__file__).parent / "fixtures" / "live3" / "presence.html"

#: THE SYNTHETIC FIXTURE'S TWO BARE INPUTS, exactly as it draws them: each a
#: direct child of the form, beside its button.
_BARE_INPUTS = (
    '    <input type="file" class="msg-form__attachment-upload-input" accept="image/*">\n'
    '    <button type="button" class="msg-form__footer-action artdeco-button" '
    'aria-label="Attach an image for your draft conversation">Attach an image for '
    "your draft conversation</button>\n"
    '    <input type="file" class="msg-form__attachment-upload-input" '
    'accept="image/*,.ai,.psd,.pdf,.doc,.docx,.ppt,.pptx,.pps,.ppsx,.xls,.xlsx,.txt,.eml,.mov,.mp4">\n'
    '    <button type="button" class="msg-form__footer-action artdeco-button" '
    'aria-label="Attach a file for your draft conversation">Attach a file for your '
    "draft conversation</button>\n"
)


def _wrapper(label: str, accept: str) -> str:
    """ONE WRAPPER AS THE REAL CAPTURE DRAWS IT (presence.html lines 2413-2440):
    two hidden inputs, the file input, and one labelled button, as siblings."""
    return (
        '<div class="msg-form__upload-attachment inline-block" '
        'data-test-msg-ui-upload-attachment-presenter="">'
        '<input name="x" value="x" type="hidden"><input name="x" type="hidden">'
        f'<input class="msg-form__attachment-upload-input hidden" accept="{accept}" type="file">'
        f'<button title="{label}" aria-label="{label}" '
        'class="msg-form__footer-action artdeco-button" type="button">'
        f'<span class="artdeco-button__text">{label}</span></button></div>'
    )


_IMAGE_ACCEPT = "image/*"
_FILE_ACCEPT = "image/*,.ai,.psd,.pdf,.doc,.docx,.ppt,.pptx,.pps,.ppsx,.xls,.xlsx,.txt,.eml,.mov,.mp4"
_CAPTURED_WRAPPERS = (
    _wrapper(attachments.ATTACH_IMAGE_LABEL, _IMAGE_ACCEPT)
    + _wrapper(attachments.ATTACH_FILE_LABEL, _FILE_ACCEPT)
)

#: SYNTHETIC: what LinkedIn's composer does once a file is attached -- here it
#: draws the file's NAME in the form and turns Send on -- and, when the form
#: says so, clears both on Send. No capture shows either; see the docstring.
_ATTACH_SCRIPT = (
    "<script>(function () {"
    " var form = document.getElementById('reply-form');"
    " var send = document.getElementById('reply-send');"
    " if (!form || !send) { return; }"
    " form.addEventListener('change', function (event) {"
    "  var input = event.target;"
    "  if (form.getAttribute('data-draws-attachments') !== 'yes') { return; }"
    "  if (!input || input.type !== 'file' || !input.files.length) { return; }"
    "  var chip = document.createElement('div'); chip.className = 'synthetic-attachment';"
    "  var name = document.createElement('span'); name.textContent = input.files[0].name;"
    "  chip.appendChild(name); form.appendChild(chip); send.disabled = false;"
    " });"
    " form.addEventListener('submit', function () {"
    "  if (form.getAttribute('data-sends-attachments') !== 'yes') { return; }"
    "  var chips = form.querySelectorAll('.synthetic-attachment');"
    "  for (var i = 0; i < chips.length; i++) { chips[i].remove(); }"
    "  send.disabled = true;"
    " });"
    "}());</script></body>"
)

_FORM = '<form class="msg-form msg-form--thread-footer-feature" id="reply-form">'

#: The conversation as the real capture draws its inputs, plus the synthetic
#: attach script, which draws nothing until the form opts in.
CAPTURED = _derive(_derive(THREAD, _BARE_INPUTS, _CAPTURED_WRAPPERS), "</body>", _ATTACH_SCRIPT)
#: ... and the world that draws the file's name and sends it.
ATTACHING = _derive(
    CAPTURED,
    _FORM,
    _FORM.replace(
        'id="reply-form"',
        'id="reply-form" data-draws-attachments="yes" data-sends-attachments="yes"',
    ),
)


def _after(file_name: str) -> str:
    """DERIVED: the conversation as a FRESH LOAD draws it after the file
    landed -- a new last message, his (no ``--other`` modifier), drawing the
    file's name. SYNTHETIC in its markup: no sent attachment was captured."""
    return _derive(
        _derive(
            CAPTURED,
            '<li class="msg-s-message-list__event clearfix msg-s-message-list__last-msg-">',
            '<li class="msg-s-message-list__event clearfix">',
        ),
        '<li class="msg-s-message-list__typing-indicator-container--without-seen-receipt" id="typing"></li>',
        '<li class="msg-s-message-list__event clearfix msg-s-message-list__last-msg-">'
        '<div class="msg-s-event-listitem msg-s-event-listitem--last-in-group">'
        f'<div class="synthetic-attachment-card"><span>{file_name}</span></div></div></li>'
        '<li class="msg-s-message-list__typing-indicator-container--without-seen-receipt" id="typing"></li>',
    )


@pytest.fixture()
def root(tmp_path, monkeypatch):
    directory = tmp_path / "uploads"
    directory.mkdir()
    monkeypatch.setattr(config, "UPLOAD_ROOT", directory)
    return directory


@pytest.fixture()
def photo(root):
    path = root / "test-image.png"
    path.write_bytes(PNG)
    return path


def _nav(*worlds: str) -> _Navigator:
    return _Navigator({URL: [(world, URL) for world in worlds]})


async def _preview(page, target, *worlds: str):
    nav = _nav(*(worlds or (CAPTURED,)))
    block = await preview(_SPEC, target=target, navigator=nav, page=page)
    return block, nav


def _no_absolute_path(value, root: pathlib.Path) -> None:
    text = json.dumps(value)
    for needle in (str(root), str(root).replace("\\", "\\\\"), str(pathlib.Path.home())):
        assert needle not in text, f"an absolute path leaked: {text[:300]}"


# ---------------------------------------------------------------------------
# 1. The target: a thread id and a file, the file held root-relative
# ---------------------------------------------------------------------------


def test_the_target_is_the_thread_and_the_file_held_relative_to_the_root(photo, root):
    """An absolute path inside the root canonicalises to its root-relative
    name, which re-normalises to itself; only the thread reaches a url."""
    canonical = writes._target_for(_SPEC, {"thread": THREAD_ID, "file": str(photo)})
    assert canonical == THREAD_ID + writes.TARGET_JOIN + "test-image.png"
    assert writes._target_for(_SPEC, canonical) == canonical
    assert writes.url_target_of(_SPEC, canonical) == THREAD_ID
    assert str(root) not in canonical


def test_a_file_outside_the_root_is_refused_before_any_token(root, tmp_path):
    outside = tmp_path / "elsewhere.png"
    outside.write_bytes(PNG)
    with pytest.raises(WriteAttemptError) as caught:
        writes._target_for(_SPEC, {"thread": THREAD_ID, "file": str(outside)})
    assert "outside the directory this server may upload from" in str(caught.value)


def test_the_tables_name_this_action():
    assert _ACTION in writes.PERFORMABLE
    assert writes.UPLOAD_ACTIONS == frozenset({_ACTION})
    assert _ACTION in writes.ATTACHMENT_SEND_ACTIONS
    assert _ACTION in writes.STRICT_PRESS_ACTIONS
    assert _SPEC.irreversible is True
    assert _SPEC.target_kind == "thread_and_file"
    assert hasattr(server, "linkedin_send_attachment")


# ---------------------------------------------------------------------------
# 2. The aim, on the REAL capture
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("family", "label"),
    [("image", attachments.ATTACH_IMAGE_LABEL), ("document", attachments.ATTACH_FILE_LABEL)],
)
async def test_the_aim_resolves_on_the_real_capture(browser_page, family, label):
    """THE SHIPPED SELECTORS, OVER THE LIVE LANE'S OWN SKELETON. Exactly one
    reply form, exactly one wrapper beside each label, exactly one file input
    in it. The declaration reads ``unrecognised`` there because the skeleton
    blanks every attribute value -- so the aim REFUSES on the skeleton, by its
    cross-check, which is the cross-check shown failing on real markup."""
    html = _REAL_CAPTURE.read_text(encoding="utf-8", errors="replace")

    async def _refused(route):
        # The skeleton keeps its stylesheet and image addresses' shapes, so a
        # browser would fetch them: the page's own route refuses every
        # request first, as tests/network_guard.py asks of a served page.
        await route.abort()

    await browser_page.route("**/*", _refused)
    await browser_page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
    reading = await attachments.read_reply_inputs(browser_page, family)
    assert reading["input_label"] == label
    assert (reading["forms"], reading["labelled_wrappers"], reading["inputs"]) == (1, 1, 1)
    assert reading["wrappers"] == 2
    assert reading["declaration"] == "unrecognised"
    aimed, why = attachments.aim_verdict(reading)
    assert aimed is False and "disagree" in why


async def test_the_aim_passes_where_the_declarations_are_the_measured_ones(browser_page):
    await browser_page.set_content(CAPTURED, wait_until="domcontentloaded")
    for family in ("image", "video", "document", "other"):
        aimed, why = attachments.aim_verdict(
            await attachments.read_reply_inputs(browser_page, family)
        )
        assert aimed is True, why


async def test_swapped_declarations_refuse_the_aim(browser_page):
    """A label and a declaration that disagree name no input: refused."""
    swapped = _derive(
        _derive(CAPTURED, f'accept="{_IMAGE_ACCEPT}"', 'accept="PLACEHOLDER"'),
        f'accept="{_FILE_ACCEPT}"',
        f'accept="{_IMAGE_ACCEPT}"',
    )
    swapped = _derive(swapped, 'accept="PLACEHOLDER"', f'accept="{_FILE_ACCEPT}"')
    await browser_page.set_content(swapped, wait_until="domcontentloaded")
    aimed, why = attachments.aim_verdict(
        await attachments.read_reply_inputs(browser_page, "image")
    )
    assert aimed is False and "disagree" in why


# ---------------------------------------------------------------------------
# 3. The preview: the file, its type from its bytes, who it would reach
# ---------------------------------------------------------------------------


async def test_the_preview_names_the_file_its_type_and_who_it_reaches(
    writes_on, browser_page, photo, root
):
    block, nav = await _preview(browser_page, {"thread": THREAD_ID, "file": "test-image.png"})
    assert nav.gotos == [URL]
    assert block["to_confirm"], block.get("why")
    facts = block["file"]
    assert facts["file_name"] == "test-image.png"
    assert str(len(PNG)) in facts["size"]
    assert facts["type_from_bytes"].startswith("image/png")
    assert facts["the_name_and_the_bytes"] == "they agree"
    assert len(facts["sha256_prefix"]) == uploads.DIGEST_CHARS
    assert block["where"]["file"] == "test-image.png"
    reach = block.get("who_this_would_reach")
    assert reach, "the preview must name who the file would reach"
    seen = block["where"]["what_the_page_showed"]["the_input_this_file_goes_to"]
    assert seen["input_label"] == attachments.ATTACH_IMAGE_LABEL
    assert seen["declaration"] == "images"
    _no_absolute_path({k: v for k, v in block.items() if k != "who_this_would_reach"}, root)


async def test_a_document_goes_to_the_file_input(writes_on, browser_page, root):
    (root / "notes.pdf").write_bytes(PDF)
    block, _nav_ = await _preview(browser_page, {"thread": THREAD_ID, "file": "notes.pdf"})
    seen = block["where"]["what_the_page_showed"]["the_input_this_file_goes_to"]
    assert seen["input_label"] == attachments.ATTACH_FILE_LABEL
    assert block["file"]["type_from_bytes"].startswith("application/pdf")


async def test_a_preview_over_an_enabled_send_mints_nothing(writes_on, browser_page, photo):
    """Send already on means something is waiting in the composer -- words or
    an earlier attachment -- and it would go with the file."""
    pending = _derive(CAPTURED, 'id="reply-send" disabled>', 'id="reply-send">')
    with pytest.raises(WriteAttemptError) as caught:
        await _preview(browser_page, {"thread": THREAD_ID, "file": "test-image.png"}, pending)
    assert "Send is already enabled" in str(caught.value)


# ---------------------------------------------------------------------------
# 4. The act, end to end, and every way it stops
# ---------------------------------------------------------------------------


async def _confirmed(page, worlds, target=None):
    target = target or {"thread": THREAD_ID, "file": "test-image.png"}
    block, _nav_ = await _preview(page, target)
    assert block["to_confirm"], block
    grant = consume(block["to_confirm"], action=_ACTION, target=target)
    return grant, block


async def test_an_attachment_that_lands_reports_sent_from_a_fresh_load(
    writes_on, browser_page, photo, root
):
    grant, block = await _confirmed(browser_page, None)
    nav = _nav(ATTACHING, _after("test-image.png"))
    out = await writes.perform(nav, browser_page, grant)
    assert out["clicked"]["error"] is None, out["clicked"]
    assert out["clicked"]["clicks_made"] == 1
    assert out["uploaded"]["files_handed_to_the_browser"] == 1
    assert out["uploaded"]["handed_over"] == "the verified bytes, not the path"
    assert out["uploaded"]["sha256_prefix"] == block["file"]["sha256_prefix"]
    assert out["send_gate"]["proceeded"] is True
    assert out["verification"]["observed_state"] == attachments.ATTACHMENT_SENT, out
    assert out["performed"] is True
    _no_absolute_path(out, root)


async def test_send_is_not_pressed_when_the_form_never_draws_the_file(
    writes_on, browser_page, photo
):
    """THE READ-BACK, REFUSING: the attachment never names itself (as an image
    preview might), so Send is not pressed and nothing is sent."""
    grant, _block = await _confirmed(browser_page, None)
    silent = _derive(
        CAPTURED,
        _FORM,
        _FORM.replace('id="reply-form"', 'id="reply-form" data-sends-attachments="yes"'),
    )
    nav = _nav(silent, silent)
    out = await writes.perform(nav, browser_page, grant)
    assert out["clicked"]["clicks_made"] == 0
    assert out["send_gate"]["proceeded"] is False
    assert out["send_gate"]["refused_condition"] == "2_one_attachment_naming_the_file"
    assert out["uploaded"]["files_handed_to_the_browser"] == 1
    assert out["performed"] is False
    assert out["verification"]["observed_state"] == attachments.ATTACHMENT_HELD


async def test_send_is_not_pressed_when_words_appeared_in_the_box(
    writes_on, browser_page, photo
):
    grant, _block = await _confirmed(browser_page, None)
    wordy = _derive(
        ATTACHING,
        "send.disabled = false;",
        "send.disabled = false; document.getElementById('reply-editor').textContent = 'stray';",
    )
    out = await writes.perform(_nav(wordy, wordy), browser_page, grant)
    assert out["clicked"]["clicks_made"] == 0
    assert out["send_gate"]["refused_condition"] == "3_no_words"


async def test_a_sent_attachment_drawn_without_its_name_is_unknown_not_sent(
    writes_on, browser_page, photo
):
    """Send was pressed and the fresh load does not draw the name: UNKNOWN --
    no sent attachment has been captured, so absence of the name proves
    nothing either way."""
    grant, _block = await _confirmed(browser_page, None)
    out = await writes.perform(_nav(ATTACHING, CAPTURED), browser_page, grant)
    assert out["clicked"]["clicks_made"] == 1
    assert out["verification"]["observed_state"] == "unknown"
    assert "do NOT retry" in json.dumps(out) or out["performed"] == "unknown"


async def test_a_file_changed_after_the_preview_is_refused_and_nothing_is_attached(
    writes_on, browser_page, photo
):
    grant, block = await _confirmed(browser_page, None)
    photo.write_bytes(PNG + b"changed")
    out = await writes.perform(_nav(ATTACHING, ATTACHING), browser_page, grant)
    assert "has changed since you were shown it" in out["clicked"]["error"]
    assert out["clicked"]["clicks_made"] == 0
    assert out["uploaded"] is None


async def test_the_click_refuses_over_something_that_appeared_after_the_preview(
    writes_on, browser_page, photo
):
    """The preview saw an empty box; by the confirm, Send is on -- something
    is waiting in the composer. The live re-read refuses BEFORE the hand-off:
    nothing is attached and nothing is pressed."""
    grant, _block = await _confirmed(browser_page, None)
    pending = _derive(ATTACHING, 'id="reply-send" disabled>', 'id="reply-send">')
    with pytest.raises(WriteAttemptError) as caught:
        await writes.perform(_nav(pending, pending), browser_page, grant)
    assert "Send is already enabled" in str(caught.value)
    handed = await browser_page.evaluate(
        "() => Array.from(document.querySelectorAll('input[type=file]'))"
        ".map(el => el.files.length).reduce((a, b) => a + b, 0)"
    )
    assert handed == 0


async def test_it_refuses_a_grant_for_another_file(writes_on, browser_page, photo, root):
    (root / "other.png").write_bytes(PNG)
    block, _nav_ = await _preview(browser_page, {"thread": THREAD_ID, "file": "test-image.png"})
    with pytest.raises(WriteAttemptError):
        consume(block["to_confirm"], action=_ACTION, target={"thread": THREAD_ID, "file": "other.png"})


async def test_it_refuses_a_grant_for_another_conversation(writes_on, browser_page, photo):
    block, _nav_ = await _preview(browser_page, {"thread": THREAD_ID, "file": "test-image.png"})
    with pytest.raises(WriteAttemptError):
        consume(
            block["to_confirm"],
            action=_ACTION,
            target={"thread": OTHER_THREAD_ID, "file": "test-image.png"},
        )


async def test_the_tool_refuses_a_malformed_thread_id_before_anything(writes_on, root):
    out = await server.linkedin_send_attachment("not a thread id", "test-image.png")
    assert out.get("error") or out.get("refused"), out
