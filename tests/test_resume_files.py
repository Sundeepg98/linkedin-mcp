"""``resume_files`` -- census rows ``J 72`` and ``P M4`` -- one stored resume he names, downloaded.

WHAT THE ACT IS. On his application settings page, the ONE resume card whose
name reads the name he gave has its options menu opened by one click, its
``Download`` item pressed once INSIDE the C8 transport's capture, and the menu
read closed again (one Escape if it stayed open). ``Delete`` is never pressed.

THE PAGES ARE REAL. Every world is live session 12's capture of the page with
the FIRST card's menu open (load 9), LinkedIn's words put back by keyed shape:
``tests/fixtures/live12/c_rj26_3_resume_menu-open_words.html``. Three things
are PLANTED, each an asserted edit: the four cards' names and date lines
(SYNTHETIC; the copy reduces them to ``x``); and a script that does what
LinkedIn's dropdown does -- at load every menu closed and empty, as session
11's capture draws them; a click on a card's trigger draws that card's two
items, the capture's own ``Delete`` and ``Download``; a click on an item
records it and closes the menu; Escape closes it -- and counts every press.

THE TRANSPORT IS A DOUBLE. ``cdp_download.capture_download`` is replaced by a
recorder that runs the trigger it is handed and answers like the transport;
``tests/test_cdp_download.py`` is where the transport itself is shown. So these
tests show WHICH press the capture wraps and what the tool does with each of
its answers -- never that LinkedIn serves a file, which only a live fire shows.

NOTHING HERE REACHES LINKEDIN: a local headless Chromium, every request the
page starts refused by its own route. Every name in this file is synthetic.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import pytest_asyncio

from linkedin_server import cdp_download, readonly, resume_files as rf
from linkedin_server.errors import WriteAttemptError

REPO = Path(__file__).resolve().parents[1]
WORDS = (REPO / "tests/fixtures/live12/c_rj26_3_resume_menu-open_words.html").read_text(
    encoding="ascii"
)

_NAME = '<h3 class="ui-attachment__filename jobs-resume-card__filedata">\nx\n</h3>'
_DATE = '<p class="ui-attachment__filesize jobs-resume-card__filedata">\nx\n</p>'

#: Four synthetic resumes, in the capture's card order.
RESUMES = [
    ("Example resume.pdf", "Last used on 9/2/2025"),
    ("Example resume two.pdf", "Last used on 10/14/2025"),
    ("Example cv.docx", "Uploaded on 8/30/2025"),
    ("Example cv old.doc", "Uploaded on 1/5/2024"),
]


def planted(resumes=RESUMES) -> str:
    """The capture with each card's name and date planted, in order."""
    markup = WORDS
    assert markup.count(_NAME) == len(resumes) and markup.count(_DATE) == len(resumes)
    for name, date in resumes:
        markup = markup.replace(_NAME, _NAME.replace("\nx\n", "\n" + name + "\n"), 1)
        markup = markup.replace(_DATE, _DATE.replace("\nx\n", "\n" + date + "\n"), 1)
    return markup


#: THE DROPDOWN, AS LINKEDIN'S ANSWERS A PRESS. At load: the first card's open
#: menu is CLOSED the way session 11 drew every card -- the trigger
#: ``aria-expanded="false"``, its content ``aria-hidden="true"`` and EMPTY --
#: and its two items are kept aside. A trigger's click draws copies of them in
#: that card's content; an item's click is recorded by its word and the card's
#: index and closes the menu, unless the world says it stays; Escape on a
#: trigger closes its menu. ``extra`` adds a third item word to every menu.
_SCRIPT = """(opts) => {
  const cards = Array.from(document.querySelectorAll('div[role=main] h3'))
    .map(h => h.parentElement.parentElement);
  const firstContent = cards[0].querySelector('div[aria-hidden]');
  const kept = Array.from(firstContent.querySelectorAll('div[class*="artdeco-dropdown__item"]'))
    .map(n => n.cloneNode(true));
  if (opts.extra) {
    const more = kept[1].cloneNode(true);
    more.lastChild.textContent = '\\n' + opts.extra + '\\n';
    kept.push(more);
  }
  window.__opens = 0; window.__escapes = 0; window.__keys = 0;
  window.__pressed = [];
  const close = (card) => {
    const trigger = card.querySelector('button[aria-expanded]');
    const content = card.querySelector('div[aria-hidden]');
    trigger.setAttribute('aria-expanded', 'false');
    content.setAttribute('aria-hidden', 'true');
    content.querySelectorAll('div[class*="artdeco-dropdown__item"]').forEach(n => n.remove());
  };
  if (!opts.leaveFirstOpen) close(cards[0]);
  cards.forEach((card, index) => {
    const trigger = card.querySelector('button[aria-expanded]');
    const content = card.querySelector('div[aria-hidden]');
    trigger.addEventListener('click', () => {
      window.__opens += 1;
      if (opts.shut) return;
      let inner = content.querySelector('div.artdeco-dropdown__content-inner');
      if (!inner) { inner = document.createElement('div'); inner.className = 'artdeco-dropdown__content-inner'; content.appendChild(inner); }
      if (!inner.querySelector('div[class*="artdeco-dropdown__item"]')) {
        kept.forEach(n => {
          const item = n.cloneNode(true);
          item.addEventListener('click', () => {
            const word = item.textContent.trim();
            window.__pressed.push([index, word]);
            if (word === 'Download' && opts.onDownload === 'hash') { location.hash = 'moved'; }
            if (word === 'Download' && opts.onDownload === 'drop_card') { cards[3].remove(); }
            if (word === 'Download' && opts.onDownload === 'stay_open') return;
            close(card);
          });
          inner.appendChild(item);
        });
      }
      trigger.setAttribute('aria-expanded', 'true');
      content.setAttribute('aria-hidden', 'false');
    });
    trigger.addEventListener('keydown', (e) => {
      if (e.key !== 'Escape') { window.__keys += 1; return; }
      window.__escapes += 1;
      if (opts.escapeFails) return;
      close(card);
    });
  });
}"""


async def _world(page, markup=None, **opts) -> None:
    await page.set_content(markup or planted(), wait_until="domcontentloaded", timeout=60_000)
    await page.evaluate(_SCRIPT, opts)


async def _witness(page) -> dict:
    return await page.evaluate(
        "() => ({opens: window.__opens, escapes: window.__escapes, keys: window.__keys,"
        " pressed: window.__pressed})"
    )


#: ONE BROWSER FOR THE MODULE, on the module's event loop; a fresh context per
#: test, so nothing a test draws or routes reaches the next (the house pattern
#: of ``tests/test_search_vertical_results.py``).
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
def _fast(monkeypatch):
    monkeypatch.setattr(rf, "POLL_MS", 10)


class _Capture:
    """The transport, doubled: it runs the trigger it is handed and answers
    the way ``cdp_download.capture_download`` answers, from ``answer``."""

    def __init__(self, answer=None):
        self.calls: list[dict] = []
        self.answer = answer or {
            "saved": True, "why": "saved", "file": "_state/downloads/resume-x/resume.pdf",
            "bytes": 2048, "magic_ok": True, "downloads_began": 1, "other_downloads": 0,
            "from_linkedin": True, "final_state": "completed", "behaviour_restored": True,
            "restore_error": None, "error": None, "context_created": False,
            "transport": "cdp:" + cdp_download.SET_DOWNLOAD_BEHAVIOR,
        }

    async def __call__(self, browser, trigger, *, label, suffix="", expect_magic=None, **kw):
        self.calls.append({"browser": browser, "label": label, "suffix": suffix,
                           "magic": expect_magic})
        if self.answer.get("why") in ("downloads_disabled", "not_attached"):
            return dict(self.answer)
        await trigger()
        return dict(self.answer)


@pytest.fixture
def capture(monkeypatch):
    double = _Capture()
    monkeypatch.setattr(rf.cdp_download, "capture_download", double)
    monkeypatch.setenv(cdp_download.DOWNLOADS_FLAG, "1")
    return double


BROWSER = object()  # stands for the attached browser; the double never touches it
URL = rf.PAGE_URL


async def _download(page, name):
    return await rf.download_resume(page, URL, name, browser=BROWSER)


# ---------------------------------------------------------------------------
# 1. The act: the named card's own menu, its Download, inside the capture
# ---------------------------------------------------------------------------


@IN_MODULE_LOOP
async def test_the_named_resume_is_downloaded_through_its_own_cards_menu(page, capture):
    await _world(page)
    result = await _download(page, "Example resume two.pdf")
    seen = await _witness(page)
    assert result["downloaded"] is True and result.get("refused") is None, result
    assert result["pressed"] is True
    assert seen["pressed"] == [[1, "Download"]], seen  # the SECOND card, its Download only
    assert seen["opens"] == 1 and seen["escapes"] == 0 and seen["keys"] == 0
    assert result["pressed_steps"] == {"opens": 1, "downloads": 1, "escapes": 0}
    assert result["menu_closed"] is True
    assert result["file"] == "_state/downloads/resume-x/resume.pdf"
    assert result["bytes"] == 2048 and result["magic_ok"] is True
    assert result["type"] == "pdf"
    assert result["observed"]["menu"] == {
        "menu_items": 2, "menu_words": ["delete", "download"], "unknown_words": 0,
    }
    assert result["transport"]["context_created"] is False
    assert "page_changed" not in result
    # The capture wrapped the press, with THIS server's name and the card's kind.
    assert capture.calls == [
        {"browser": BROWSER, "label": "resume", "suffix": ".pdf", "magic": b"%PDF-"},
    ]


@pytest.mark.parametrize(
    ("name", "suffix", "magic", "index"),
    [
        ("Example cv.docx", ".docx", b"PK\x03\x04", 2),
        ("Example cv old.doc", ".doc", b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", 3),
    ],
)
@IN_MODULE_LOOP
async def test_the_saved_file_is_named_and_checked_by_the_cards_own_kind(
    page, capture, name, suffix, magic, index
):
    await _world(page)
    result = await _download(page, name)
    assert result["downloaded"] is True
    assert capture.calls[0]["suffix"] == suffix and capture.calls[0]["magic"] == magic
    assert (await _witness(page))["pressed"] == [[index, "Download"]]


@IN_MODULE_LOOP
async def test_nothing_the_page_drew_and_not_the_name_he_gave_leaves(page, capture):
    """The result carries counts, closed words and the transport's verdict."""
    await _world(page)
    result = await _download(page, "Example resume two.pdf")
    text = json.dumps(result, default=str)
    assert "Example" not in text and "Last used" not in text
    assert '"Download"' not in text and '"Delete"' not in text  # only this module's keys


# ---------------------------------------------------------------------------
# 2. Refused before any press, naming what it saw
# ---------------------------------------------------------------------------


@IN_MODULE_LOOP
async def test_a_name_no_card_reads_is_refused_with_nothing_pressed(page, capture):
    await _world(page)
    result = await _download(page, "Example missing.pdf")
    assert result["refused"] == "named_card_count" and result["downloaded"] is False
    assert result["observed"]["named_cards"] == 0 and result["observed"]["cards"] == 4
    assert (await _witness(page)) == {"opens": 0, "escapes": 0, "keys": 0, "pressed": []}
    assert capture.calls == []


@IN_MODULE_LOOP
async def test_two_cards_of_one_name_are_refused_rather_than_chosen_by_position(page, capture):
    twins = [RESUMES[0], (RESUMES[0][0], "Uploaded on 1/2/2025"), RESUMES[2], RESUMES[3]]
    await _world(page, planted(twins))
    result = await _download(page, "Example resume.pdf")
    assert result["refused"] == "named_card_count"
    assert result["observed"]["named_cards"] == 2
    assert (await _witness(page))["opens"] == 0 and capture.calls == []


#: Names the list tool cannot return: empty, an end space, a run of spaces, an
#: invisible character, over the cap, not a string.
BAD_NAMES = ["", " Example resume.pdf", "Example resume.pdf ", "Example  resume.pdf",
             "Example" + chr(0x200B) + " resume.pdf", "x" * 256, None, 7]


@pytest.mark.parametrize("bad", BAD_NAMES)
def test_a_name_the_list_tool_could_not_return_is_refused_and_not_repeated(bad):
    name, why = rf.checked_file_name(bad)
    assert name is None and why and "Example" not in why


@IN_MODULE_LOOP
async def test_such_a_name_is_refused_before_the_page_is_asked_anything(page, capture):
    await _world(page)
    for bad in BAD_NAMES:
        result = await _download(page, bad)
        assert result["refused"] == "bad_file_name" and result["downloaded"] is False
    assert (await _witness(page))["opens"] == 0 and capture.calls == []
    assert rf.checked_file_name("Example resume.pdf") == ("Example resume.pdf", "")


@IN_MODULE_LOOP
async def test_a_menu_already_open_is_not_the_state_the_press_starts_from(page, capture):
    """Session 12's capture AS DRAWN: the first card's menu open."""
    await _world(page, leaveFirstOpen=True)
    result = await _download(page, "Example resume two.pdf")
    assert result["refused"] == "menu_not_closed"
    assert result["observed"]["open_triggers"] == 1
    assert (await _witness(page))["opens"] == 0 and capture.calls == []


@IN_MODULE_LOOP
async def test_the_transport_switch_off_refuses_before_any_read(page, monkeypatch):
    monkeypatch.delenv(cdp_download.DOWNLOADS_FLAG, raising=False)
    await _world(page)
    result = await _download(page, "Example resume.pdf")
    assert result["refused"] == "downloads_disabled"
    assert (await _witness(page))["opens"] == 0


@IN_MODULE_LOOP
async def test_no_attached_browser_refuses_before_any_read(page, capture):
    await _world(page)
    result = await rf.download_resume(page, URL, "Example resume.pdf", browser=None)
    assert result["refused"] == "not_attached"
    assert (await _witness(page))["opens"] == 0 and capture.calls == []


@IN_MODULE_LOOP
async def test_any_other_landing_is_refused_before_the_page_is_asked(page, capture):
    await _world(page)
    for landed in ("https://www.linkedin.com/jobs/application-settings/x/",
                   "https://www.linkedin.com/feed/", "", None):
        result = await rf.download_resume(page, landed, "Example resume.pdf", browser=BROWSER)
        assert result["refused"] and result["downloaded"] is False, landed
    assert (await _witness(page))["opens"] == 0 and capture.calls == []


# ---------------------------------------------------------------------------
# 3. After a press: the menu's words, the closure, the refuters
# ---------------------------------------------------------------------------


@IN_MODULE_LOOP
async def test_a_menu_word_nobody_measured_is_never_pressed_and_the_menu_is_closed(page, capture):
    await _world(page, extra="Share")
    result = await _download(page, "Example resume.pdf")
    seen = await _witness(page)
    assert result["refused"] == "menu_word_unknown"
    assert result["observed"]["menu"]["unknown_words"] == 1
    assert seen["pressed"] == [] and seen["escapes"] == 1
    assert result["menu_closed"] is True and capture.calls == []
    assert "Share" not in json.dumps(result)


@IN_MODULE_LOOP
async def test_a_menu_left_open_after_the_download_is_closed_by_one_escape(page, capture):
    await _world(page, onDownload="stay_open")
    result = await _download(page, "Example resume.pdf")
    seen = await _witness(page)
    assert result["downloaded"] is True and result["menu_closed"] is True
    assert seen["pressed"] == [[0, "Download"]] and seen["escapes"] == 1
    assert result["pressed_steps"] == {"opens": 1, "downloads": 1, "escapes": 1}


@IN_MODULE_LOOP
async def test_a_menu_that_will_not_close_is_reported_not_as_found(page, capture):
    await _world(page, onDownload="stay_open", escapeFails=True)
    result = await _download(page, "Example resume.pdf")
    assert result["refused"] == "did_not_close" and result["menu_closed"] is False


@IN_MODULE_LOOP
async def test_a_click_that_draws_no_menu_is_never_escaped(page, capture):
    await _world(page, shut=True)
    result = await _download(page, "Example resume.pdf")
    seen = await _witness(page)
    assert result["refused"] == "did_not_open"
    assert seen["opens"] == 1 and seen["escapes"] == 0 and capture.calls == []


@IN_MODULE_LOOP
async def test_an_address_that_moved_after_the_download_stops_everything(page, capture):
    await _world(page, onDownload="hash")
    result = await _download(page, "Example resume.pdf")
    seen = await _witness(page)
    assert result["refused"] == "address_moved"
    assert seen["escapes"] == 0  # nothing pressed on a page that is not the one found


@IN_MODULE_LOOP
async def test_a_page_that_changed_under_the_download_says_so(page, capture):
    """A download changes no card: a card gone after it is reported, loud."""
    await _world(page, onDownload="drop_card")
    result = await _download(page, "Example resume.pdf")
    assert result["page_changed"] == ["card_count"]
    assert result["observed"]["before"]["cards"] == 4 and result["observed"]["after"]["cards"] == 3


@IN_MODULE_LOOP
async def test_a_transport_that_took_no_file_is_a_refusal_naming_its_why(page, monkeypatch):
    double = _Capture({"saved": False, "why": "no_download_began", "file": None,
                       "bytes": None, "magic_ok": None, "context_created": False})
    monkeypatch.setattr(rf.cdp_download, "capture_download", double)
    monkeypatch.setenv(cdp_download.DOWNLOADS_FLAG, "1")
    await _world(page)
    result = await _download(page, "Example resume.pdf")
    assert result["refused"] == "download_not_saved" and result["downloaded"] is False
    assert "no_download_began" in result["why"] and result["file"] is None
    assert result["menu_closed"] is True
    assert (await _witness(page))["pressed"] == [[0, "Download"]]


# ---------------------------------------------------------------------------
# 4. The closed tables and the one drain point
# ---------------------------------------------------------------------------


@IN_MODULE_LOOP
async def test_the_drain_point_refuses_any_step_but_its_three(page):
    await _world(page)
    trigger = page.locator(rf.ALL_TRIGGERS).first
    with pytest.raises(WriteAttemptError):
        await rf._press(trigger, "delete")
    with pytest.raises(WriteAttemptError):
        await rf._press(trigger, "type")
    assert (await _witness(page))["opens"] == 0


def test_the_menu_vocabulary_is_the_two_words_session_12_measured():
    assert rf.MENU_WORDS == {"Delete": "delete", "Download": "download"}
    assert rf.STEPS == {"open": "click", "download": "click", "close": "Escape"}
    assert "Download" in WORDS and "\nDelete\n" in WORDS  # both drawn on the capture
    assert readonly.is_read_url(rf.PAGE_URL)


def test_the_module_presses_only_in_its_drain_point():
    """Every click and press call in the module sits in ``_press``."""
    import ast

    tree = ast.parse((REPO / "linkedin_server" / "resume_files.py").read_text(encoding="utf-8"))
    sites = []
    for func in ast.walk(tree):
        if isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for node in ast.walk(func):
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                        and node.func.attr in ("click", "press", "fill", "type", "check",
                                               "set_input_files", "dispatch_event")):
                    sites.append((func.name, node.func.attr))
    assert sorted(set(sites)) == [("_press", "click"), ("_press", "press")], sites


# ---------------------------------------------------------------------------
# 5. The tool: three refusals before any load, then one load and the act
# ---------------------------------------------------------------------------


def _tool_drive(monkeypatch, page, *, mode: str = "attach"):
    """The real tool over ``page``: its session and its one load faked, the
    navigations recorded, and the attach mode as given."""
    from contextlib import asynccontextmanager

    from linkedin_server import browser as browser_module

    navigations: list[str] = []

    @asynccontextmanager
    async def fake_session():
        yield page

    async def fake_goto(target_page, url, **kwargs):
        navigations.append(url)
        return url

    monkeypatch.setattr(browser_module.BROWSER, "session", fake_session)
    monkeypatch.setattr(browser_module.BROWSER, "goto", fake_goto)
    monkeypatch.setattr(type(browser_module.BROWSER), "mode", property(lambda self: mode))
    monkeypatch.setattr(type(browser_module.BROWSER), "attached",
                        property(lambda self: mode == "attach"))
    monkeypatch.setattr(rf.cdp_download, "attached_browser",
                        lambda p, *, attached: BROWSER if attached else None)
    return navigations


@IN_MODULE_LOOP
async def test_the_tool_refuses_three_ways_before_it_loads_anything(page, capture, monkeypatch):
    from linkedin_server.server import linkedin_download_resume

    await _world(page)
    navigations = _tool_drive(monkeypatch, page)
    assert (await linkedin_download_resume(" Example resume.pdf"))["refused"] == "bad_file_name"
    monkeypatch.delenv(cdp_download.DOWNLOADS_FLAG)
    assert (await linkedin_download_resume("Example resume.pdf"))["refused"] == "downloads_disabled"
    monkeypatch.setenv(cdp_download.DOWNLOADS_FLAG, "1")
    _tool_drive(monkeypatch, page, mode="launch")
    refused = await linkedin_download_resume("Example resume.pdf")
    assert refused["refused"] == "not_attached" and refused["loaded"] is False
    assert navigations == [] and capture.calls == []
    assert (await _witness(page))["opens"] == 0


@IN_MODULE_LOOP
async def test_the_tool_loads_the_one_admitted_page_and_downloads_the_named_resume(
    page, capture, monkeypatch
):
    from linkedin_server.server import linkedin_download_resume

    await _world(page)
    navigations = _tool_drive(monkeypatch, page)
    result = await linkedin_download_resume("Example cv.docx")
    assert navigations == [rf.PAGE_URL]
    assert result["pages_loaded"] == 1 and result["downloaded"] is True, result
    assert capture.calls[0]["suffix"] == ".docx"
    assert (await _witness(page))["pressed"] == [[2, "Download"]]
