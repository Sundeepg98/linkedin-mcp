"""Deleting one stored resume (census ``P M3``) and uploading one (``P M1``) -- each built behind the grant and REFUSING.

Lane build28, 2026-11-28, on the orchestrator's order in the lane's brief:
"P M3 (delete) and P M1 (upload), each built REFUSING, in the J-19 shape ...
P M1 stays GAP, because its inverse P M3 can only be built refusing and the
rule is inverse-proven-first. Both are built so that a later attended session
can run upload then delete on a file he names."

THE PAGE is the live lane's session-11 capture of his application settings
page, every resume card's menu closed, with LinkedIn's words written by keyed
shape (``tests/fixtures/live11/application_settings_words.html``): four cards,
each one ``button[aria-expanded="false"]``; one ``Upload resume`` label bound
by ``for`` to one file input; the rule ``DOC, DOCX, PDF (5MB)``. The four
names are planted, SYNTHETIC. What the Delete item opens, and what the page
does with a file, are in no capture, and those are the refusals.

NOTHING HERE REACHES LINKEDIN: every load is ``set_content`` of a frozen world,
every request a page would make is refused first, and the upload's file sits
in a temporary folder declared as the upload root for the test.
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest
import pytest_asyncio

from linkedin_server import config, resume_files as rf, server, writes
from linkedin_server.errors import WriteAttemptError
from tests.plantedpage import PlantedPage
from tests.skeleton_page import SkeletonPage, parse
from tests.test_writes import FixtureNavigator, writes_on  # noqa: F401 -- fixtures

_LIVE11 = Path(__file__).parent / "fixtures" / "live11"
_WORDS = (_LIVE11 / "application_settings_words.html").read_text(encoding="ascii")
_NAME = '<h3 class="ui-attachment__filename jobs-resume-card__filedata">\nx\n</h3>'
_NAMES = ["Example resume.pdf", "Example resume two.pdf", "Example cv.docx", "Example cv old.doc"]
_DELETE = "set_resume_deleted"
_UPLOAD = "set_resume_uploaded"


def _planted(names=_NAMES) -> str:
    markup = _WORDS
    assert markup.count(_NAME) == len(names)
    for name in names:
        markup = markup.replace(_NAME, _NAME.replace("\nx\n", "\n" + name + "\n"), 1)
    return markup


#: ONE BROWSER FOR THE MODULE, on the module's event loop; a fresh context per
#: test (the house pattern of ``tests/test_search_vertical_results.py``).
IN_MODULE_LOOP = pytest.mark.asyncio(loop_scope="module")


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def _browser():
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            yield browser
        finally:
            await browser.close()


@pytest_asyncio.fixture(loop_scope="module")
async def page(_browser):
    async def _refuse(route):
        await route.abort("aborted")

    context = await _browser.new_context()
    try:
        tab = await context.new_page()
        await tab.route("**/*", _refuse)
        yield tab
    finally:
        await context.close()


@pytest.fixture(autouse=True)
def _no_grants_survive_a_test():
    yield
    writes.discard_all()


@pytest.fixture
def upload_root(tmp_path, monkeypatch):
    """A declared upload root of this test's own, holding a PDF and a PNG."""
    root = tmp_path / "uploads"
    root.mkdir()
    (root / "example-resume.pdf").write_bytes(b"%PDF-1.4\n" + b"0" * 2048)
    (root / "example-photo.png").write_bytes(b"\x89PNG\r\n" + b"0" * 64)
    monkeypatch.setattr(config, "UPLOAD_ROOT", str(root))
    return root


def _skeleton(markup: str) -> SkeletonPage:
    return SkeletonPage(PlantedPage(), parse(markup), url=rf.PAGE_URL)


# ---------------------------------------------------------------------------
# 1. The two preview readers, counts only, nothing pressed
# ---------------------------------------------------------------------------


async def test_the_delete_reader_finds_the_named_card_closed():
    page = _skeleton(_planted())
    reading = await rf.read_delete_control(page, "Example cv.docx")
    assert page.unmodelled == [] and page.planted_answers == []
    assert (reading["headings"], reading["cards"], reading["named_cards"]) == (1, 4, 1)
    assert (reading["triggers"], reading["expanded"], reading["items"]) == (1, "false", 0)
    assert reading["open_triggers"] == 0 and reading["delete_dialog_read"] is False
    assert rf.delete_state_of(reading)[0] == rf.RESUME_LISTED
    assert "Example" not in json.dumps(reading)


@pytest.mark.parametrize(
    ("names", "asked", "why"),
    [
        (_NAMES, "Example missing.pdf", "0 of the 4"),
        ([_NAMES[0], _NAMES[0], _NAMES[2], _NAMES[3]], "Example resume.pdf", "2 of the 4"),
        (_NAMES, " Example resume.pdf", "not one linkedin_application_settings returns"),
    ],
)
async def test_THIS_CONTROL_CAN_FAIL_the_delete_reader_reads_unknown(names, asked, why):
    reading = await rf.read_delete_control(_skeleton(_planted(names)), asked)
    state, said = rf.delete_state_of(reading)
    assert state == rf.UNKNOWN and why in said


async def test_the_upload_reader_reads_the_control_and_the_pages_own_rule():
    page = _skeleton(_planted())
    reading = await rf.read_upload_control(page)
    assert page.unmodelled == [] and page.planted_answers == []
    assert reading == {
        "headings": 1, "upload_labels": 1, "bound_labels": 1, "file_inputs": 1,
        "rule": {"types": ["doc", "docx", "pdf"], "max_megabytes": 5}, "cards": 4,
        "error": None,
    }
    assert rf.upload_state_of(reading, suffix=".pdf", size_bytes=2048)[0] == rf.UPLOAD_OFFERED


@pytest.mark.parametrize(
    ("suffix", "size", "why"),
    [(".png", 64, "is not one of them"), (".pdf", 6 * 1024 * 1024, "is larger"),
     ("", 10, "is not one of them")],
)
async def test_THIS_CONTROL_CAN_FAIL_the_page_vetoes_a_file_its_rule_refuses(suffix, size, why):
    reading = await rf.read_upload_control(_skeleton(_planted()))
    state, said = rf.upload_state_of(reading, suffix=suffix, size_bytes=size)
    assert state == rf.UNKNOWN and why in said


async def test_THIS_CONTROL_CAN_FAIL_an_unbound_label_reads_unknown():
    markup = _planted()
    bound = '<label class="artdeco-button artdeco-button--secondary artdeco-button--2" tabindex="0" role="button" for="'
    assert markup.count(bound) == 1
    markup = markup.replace(bound, bound + "unbound")
    reading = await rf.read_upload_control(_skeleton(markup))
    assert reading["upload_labels"] == 1 and reading["bound_labels"] == 0
    assert rf.upload_state_of(reading, suffix=".pdf", size_bytes=10)[0] == rf.UNKNOWN


# ---------------------------------------------------------------------------
# 2. The two writes: sanctioned, refusing, minting nothing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("action", "tool", "kind", "parameters"),
    [
        (_DELETE, "linkedin_set_resume_deleted", "resume_file", ["resume", "confirm_token"]),
        (_UPLOAD, "linkedin_set_resume_uploaded", "resume_upload", ["file", "confirm_token"]),
    ],
)
def test_each_action_is_sanctioned_not_performable_and_names_what_lifts_it(action, tool, kind, parameters):
    spec = writes.spec_for_action(action)
    assert spec.tool_name == tool and spec.target_kind == kind
    assert action not in writes.PERFORMABLE and action not in writes.UPLOAD_ACTIONS
    assert spec.url_template is None and spec.url_pattern is None
    assert spec.reversibility_class == "STILL-UNKNOWN" and spec.reversibility_measured is False
    refusal = writes._NINE_REFUSALS[action]
    assert "AT HIS ORDER" in refusal and "WHAT WOULD LIFT IT" in refusal
    assert not writes.grant_is_possible(spec)
    assert writes._SURFACE_READS[spec.state_from][0] == rf.PAGE_URL
    registered = getattr(server, tool)
    assert list(inspect.signature(getattr(registered, "fn", registered)).parameters) == parameters


def test_the_upload_refusal_names_its_inverse_first():
    assert "set_resume_deleted" in writes._NINE_REFUSALS[_UPLOAD]
    assert "inverse-proven-first" in writes._NINE_REFUSALS[_UPLOAD]
    assert writes.spec_for_action(_DELETE).irreversible is True


@IN_MODULE_LOOP
async def test_the_delete_preview_reads_the_page_once_and_issues_no_token(writes_on, page):
    nav = FixtureNavigator({rf.PAGE_URL: _planted()})
    block = await writes.preview(writes.spec_for_action(_DELETE), target="Example cv.docx",
                                 navigator=nav, page=page)
    assert nav.gotos == [rf.PAGE_URL]
    assert block["to_confirm"] is None, block
    assert block["where"]["whose"].startswith("your own application settings page")
    assert block["where"]["resume"] == "Example cv.docx"
    shown = block["where"]["what_the_page_showed"]
    assert (shown["named_cards"], shown["triggers"], shown["expanded"]) == (1, 1, "false")
    assert shown["delete_dialog_read"] is False
    assert block["direction"]["currently"] == rf.RESUME_LISTED
    assert writes._GRANTS == {}
    with pytest.raises(WriteAttemptError):
        writes.mint(_DELETE, "Example cv.docx", receipt="any")


@IN_MODULE_LOOP
async def test_a_name_no_card_reads_is_refused_at_the_delete_preview(writes_on, page):
    nav = FixtureNavigator({rf.PAGE_URL: _planted()})
    with pytest.raises(WriteAttemptError) as caught:
        await writes.preview(writes.spec_for_action(_DELETE), target="Example missing.pdf",
                             navigator=nav, page=page)
    assert "unknown" in str(caught.value)
    assert writes._GRANTS == {}


def test_a_name_the_list_tool_could_not_return_is_refused_before_any_load():
    for bad in (" Example resume.pdf", "Example" + chr(0x200B) + ".pdf", ""):
        with pytest.raises(WriteAttemptError) as caught:
            writes._target_for(writes.spec_for_action(_DELETE), bad)
        assert "Example" not in str(caught.value)


@IN_MODULE_LOOP
async def test_the_upload_preview_checks_the_file_against_the_pages_rule_and_issues_no_token(
    writes_on, page, upload_root
):
    nav = FixtureNavigator({rf.PAGE_URL: _planted()})
    block = await writes.preview(writes.spec_for_action(_UPLOAD), target="example-resume.pdf",
                                 navigator=nav, page=page)
    assert nav.gotos == [rf.PAGE_URL]
    assert block["to_confirm"] is None, block
    assert block["where"]["file"] == "example-resume.pdf"  # root-relative, never absolute
    shown = block["where"]["what_the_page_showed"]
    assert shown["rule"] == {"types": ["doc", "docx", "pdf"], "max_megabytes": 5}
    assert shown["file_suffix"] == ".pdf" and shown["file_handed_over"] is False
    assert block["direction"]["currently"] == rf.UPLOAD_OFFERED
    assert str(upload_root) not in json.dumps(block)
    assert writes._GRANTS == {}


@IN_MODULE_LOOP
async def test_a_file_the_pages_rule_refuses_is_vetoed_at_the_upload_preview(writes_on, page, upload_root):
    nav = FixtureNavigator({rf.PAGE_URL: _planted()})
    with pytest.raises(WriteAttemptError) as caught:
        await writes.preview(writes.spec_for_action(_UPLOAD), target="example-photo.png",
                             navigator=nav, page=page)
    assert "unknown" in str(caught.value)


def test_a_file_outside_the_declared_root_is_refused_before_any_load(upload_root, tmp_path):
    outside = tmp_path / "elsewhere.pdf"
    outside.write_bytes(b"%PDF-1.4\n")
    with pytest.raises(WriteAttemptError):
        writes._target_for(writes.spec_for_action(_UPLOAD), str(outside))
    with pytest.raises(WriteAttemptError):
        writes._target_for(writes.spec_for_action(_UPLOAD), "missing.pdf")
    assert writes._target_for(writes.spec_for_action(_UPLOAD), "example-resume.pdf") == "example-resume.pdf"


@pytest.mark.parametrize(("tool", "argument"), [
    ("linkedin_set_resume_deleted", "Example resume.pdf"),
    ("linkedin_set_resume_uploaded", "example-resume.pdf"),
])
async def test_with_writes_off_each_tool_loads_nothing(monkeypatch, tool, argument):
    monkeypatch.delenv(writes.WRITES_FLAG, raising=False)
    registered = getattr(server, tool)
    out = await getattr(registered, "fn", registered)(argument)
    assert out.get("performed") is not True
    assert "writes" in json.dumps(out).lower()
