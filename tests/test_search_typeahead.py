"""``search_typeahead`` -- census row ``N 95`` -- his recent searches, read from his own search box.

WHAT THE ACT IS. On the feed, the one ``[role=search] input[aria-autocomplete]``
is clicked once, its typeahead's recent-searches group is read -- ONLY it --
and one Escape closes the box, the closure verified. Nothing is typed.
SEARCH-BOX-TYPEAHEAD-DISCLOSURE (orchestrator, 2026-11-26).

THE PAGES ARE REAL. Every world is live session 11's tracked copy of the feed
with the box open (load 28), LinkedIn's words put back by keyed shape --
``tests/fixtures/synthetic/live11_search_box_words.html``, whose one restored
address word, ``search-results``, is what makes the recent jobs search a
search address at all. THREE THINGS ARE PLANTED, each an asserted edit: the
two recent searches' keywords (SYNTHETIC; the copy reduces them to ``x``);
a NEEDLE in the first recently viewed person's option -- a synthetic name and
slug -- so a reading that touched the people group would carry it out; and,
for a world that answers presses, a script that does what LinkedIn's box does
(the listbox the capture draws, put back on a click with its popover shown,
and taken away on Escape) and counts what was pressed and typed.

NOTHING HERE REACHES LINKEDIN: a local headless Chromium, every request the
page starts refused by its own route.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from linkedin_server import readonly, search_typeahead as st, server
from linkedin_server.errors import ExtractionFailedError, WriteAttemptError
from tests.test_writes import browser_page  # noqa: F401 -- the shared engine

REPO = Path(__file__).resolve().parents[1]
WORDS = (REPO / "tests/fixtures/synthetic/live11_search_box_words.html").read_text(encoding="ascii")

#: Synthetic keywords for the two recent searches, and the needle.
JOBS_WORDS = "example role title"
ALL_WORDS = "example topic words"
NEEDLE_SLUG = "example-needle-person"
NEEDLE_NAME = "Example Needle Person"


def _after(markup: str, anchor: str, old: str, new: str) -> str:
    """Replace the first ``old`` after the one ``anchor``, both asserted."""
    assert markup.count(anchor) == 1, (anchor, markup.count(anchor))
    at = markup.index(anchor)
    found = markup.index(old, at)
    return markup[:found] + new + markup[found + len(old):]


def _planted(markup: str) -> str:
    markup = _after(
        markup, 'id="kebcadf46"',
        'href="https://www.linkedin.com/jobs/search-results/?keywords=x&amp;',
        'href="https://www.linkedin.com/jobs/search-results/?keywords=example%20role%20title&amp;',
    )
    markup = _after(
        markup, 'id="k48a30174"',
        'href="https://www.linkedin.com/search/results/all/?keywords=x&amp;',
        'href="https://www.linkedin.com/search/results/all/?keywords=example+topic+words&amp;',
    )
    markup = _after(
        markup, 'id="k6235f4ec"',
        'href="https://www.linkedin.com/in/x/"',
        f'href="https://www.linkedin.com/in/{NEEDLE_SLUG}/"',
    )
    return _after(markup, 'id="k6235f4ec"', ">\nx\n<", f">\n{NEEDLE_NAME}\n<")


#: THE OPEN CAPTURE, planted: the box as captured, its listbox owned.
OPEN = _planted(WORDS)

#: THE BOX, AS LINKEDIN'S ANSWERS A PRESS: closed at load (its listbox taken
#: out, the input owning nothing), opened by a click (the listbox put back,
#: its popover shown), closed by Escape -- unless the world says it stays.
_SCRIPT = """(leave) => {
  const input = document.querySelector('input[aria-autocomplete]');
  const listbox = document.querySelector('[role=listbox]');
  const pop = listbox.closest('[popover]');
  const parent = listbox.parentElement;
  const owns = input.getAttribute('aria-owns');
  listbox.remove();
  input.removeAttribute('aria-owns');
  window.__opens = 0; window.__escapes = 0; window.__keys = 0;
  window.__typed = 0; window.__inListbox = 0;
  input.addEventListener('click', () => {
    window.__opens += 1;
    if (leave === 'shut') return;
    if (!listbox.isConnected) {
      parent.appendChild(listbox);
      input.setAttribute('aria-owns', owns);
      if (pop && !pop.matches(':popover-open')) pop.showPopover();
    }
  });
  input.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') { window.__keys += 1; return; }
    window.__escapes += 1;
    if (leave === 'open') return;
    listbox.remove();
    input.removeAttribute('aria-owns');
    if (pop && pop.matches(':popover-open')) pop.hidePopover();
  });
  input.addEventListener('input', () => { window.__typed += 1; });
  document.addEventListener('click', (e) => {
    if (e.target.closest && e.target.closest('[role=listbox]')) window.__inListbox += 1;
  }, true);
}"""


async def _world(page, markup: str = OPEN, leave: str = "close") -> None:
    await page.set_content(markup, wait_until="domcontentloaded", timeout=60_000)
    await page.evaluate(_SCRIPT, leave)


async def _witness(page) -> dict[str, int]:
    return await page.evaluate(
        "() => ({opens: window.__opens, escapes: window.__escapes, keys: window.__keys,"
        " typed: window.__typed, in_listbox: window.__inListbox})"
    )


@pytest.fixture
async def page(browser_page):
    async def _refuse(route):
        await route.abort("aborted")

    await browser_page.route("**/*", _refuse)
    return browser_page


@pytest.fixture(autouse=True)
def _fast(monkeypatch):
    monkeypatch.setattr(st, "POLL_MS", 20)


def _no_needle(value) -> None:
    text = json.dumps(value, default=str)
    assert NEEDLE_SLUG not in text and NEEDLE_NAME not in text
    assert "/in/" not in text


# ---------------------------------------------------------------------------
# 0. Pure: the table, the page, the verdicts, the parser
# ---------------------------------------------------------------------------


def test_the_closed_table_holds_one_ruled_entry_and_no_word():
    assert [name for name, _ in st.TYPEAHEADS] == ["recent_searches"]
    entry = st.typeahead("recent_searches")
    assert "SEARCH-BOX-TYPEAHEAD-DISCLOSURE" in entry["ruling"]
    assert entry["condition_3"]["route"] == "structural_argument"
    assert entry["condition_3"]["refuters"]
    assert st.typeahead("anything else") is None
    assert st.TARGET == '[role="search"] input[aria-autocomplete]'
    for selector in (st.TARGET, st.OWNED_LISTBOX, st.RECENT_GROUP, st.RECENT_LINKS):
        for word in ("Recent", "Try searching", "Clear all", "Jobs"):
            assert word not in selector, (word, selector)


def test_the_page_must_be_admitted_and_the_measured_surface():
    assert st.check_page(st.PAGE_URL) == {"pressed": False, "page_ok": True}
    assert st.check_page("https://www.linkedin.com/mynetwork/")["refused"] == "typeahead_not_for_this_surface"
    assert st.check_page("https://www.linkedin.com/jobs/")["refused"] == "address_not_admitted"
    assert st.check_page("")["refused"] == "no_address"
    assert st.check_page(st.PAGE_URL, key="people")["refused"] == "typeahead_not_ruled"


def test_the_target_verdict_names_the_count():
    ok = {"targets": 1, "targets_visible": 1}
    assert st.target_verdict(ok).get("target_ok") is True
    for n in (0, 2, 3):
        refusal = st.target_verdict({"targets": n, "targets_visible": n})
        assert refusal["refused"] == "target_count" and f"draws {n} input(s)" in refusal["why"]
    assert st.target_verdict(dict(ok, owned_listboxes=1))["refused"] == "already_open"
    assert st.target_verdict({"error": "TimeoutError"})["refused"] == "unreadable"


def test_the_parser_takes_only_a_search_address_with_keywords():
    assert st.parse_search_address(
        "https://www.linkedin.com/jobs/search-results/?keywords=a%20b&origin=SUGGESTION"
    ) == {"keywords": "a b", "vertical": "jobs"}
    assert st.parse_search_address(
        "https://www.linkedin.com/search/results/all/?keywords=a+b&origin=HISTORY&position=0"
    ) == {"keywords": "a b", "vertical": "all"}
    assert st.parse_search_address(
        "https://www.linkedin.com/search/results/people/?keywords=c"
    ) == {"keywords": "c", "vertical": "other"}
    for href in (
        "https://www.linkedin.com/in/example-harness-person/",
        "https://www.linkedin.com/jobs/x/?keywords=x",
        "https://www.linkedin.com/search/results/all/?origin=HISTORY",
        "http://www.linkedin.com/search/results/all/?keywords=a",
        "https://example.com/search/results/all/?keywords=a",
        None,
    ):
        assert st.parse_search_address(href) is None, href
    assert len(st.clean_keywords("a" * 999)) == st.KEYWORDS_CAP
    assert st.clean_keywords(" a\t\nb\x00 ") == "a b"


# ---------------------------------------------------------------------------
# 1. The reading, over the real capture
# ---------------------------------------------------------------------------


async def test_the_recent_group_is_found_by_its_structure_and_read_alone(page):
    await page.set_content(OPEN, wait_until="domcontentloaded", timeout=60_000)
    box = await st._read_box(page)
    assert (box["targets"], box["owned_listboxes"]) == (1, 1)
    assert await st._count(page, st.RECENT_GROUP) == 1
    reading = await st._read_recent_searches(page)
    assert reading["recent_searches"] == [
        {"keywords": JOBS_WORDS, "vertical": "jobs"},
        {"keywords": ALL_WORDS, "vertical": "all"},
    ]
    _no_needle(reading)
    # THE LINKS READ ARE THE RECENT GROUP'S OWN: none sits in the people group
    # or under the suggestions' heading.
    outside = await page.evaluate(
        """(xpath) => {
          const hits = document.evaluate(xpath, document, null, 7, null);
          let n = 0;
          for (let i = 0; i < hits.snapshotLength; i++) {
            const g = hits.snapshotItem(i).closest('[role=group]');
            if (g.querySelector('a[href*="/in/"]') || g.querySelector(':scope > p')) n += 1;
          }
          return [hits.snapshotLength, n];
        }""",
        st.RECENT_LINKS[len("xpath="):],
    )
    assert outside == [2, 0]


async def test_the_tracked_copy_without_its_address_word_reads_no_group(page):
    """THE RED: the copy as committed reduces ``search-results`` to x, so the
    recent jobs search is no search address and no group has the structure."""
    copy = (REPO / "tests/fixtures/live11/feed_search_box_open.html").read_text(encoding="ascii")
    await page.set_content(copy, wait_until="domcontentloaded", timeout=60_000)
    assert await st._count(page, st.RECENT_GROUP) == 0
    with pytest.raises(ExtractionFailedError):
        await st._read_recent_searches(page)


async def test_an_attempt_to_read_the_people_options_fails(page, monkeypatch):
    """THE PEOPLE OPTIONS ARE NEVER READ OR RETURNED. Pointed at the people
    group itself, the reader refuses -- its links are no search addresses --
    and its refusal carries no name, slug or link."""
    await page.set_content(OPEN, wait_until="domcontentloaded", timeout=60_000)
    people = st.OWNED_LISTBOX + "//*[@role='group'][.//a[contains(@href, '/in/')]]"
    monkeypatch.setattr(st, "RECENT_GROUP", people)
    monkeypatch.setattr(st, "RECENT_LINKS", people + "//*[@role='option']//a[@href]")
    with pytest.raises(ExtractionFailedError) as raised:
        await st._read_recent_searches(page)
    _no_needle(str(raised.value))


# ---------------------------------------------------------------------------
# 2. End to end: one click, one Escape, nothing typed
# ---------------------------------------------------------------------------


async def test_one_click_one_escape_and_his_recent_searches(page):
    await _world(page)
    result = await st.disclose_recent_searches(page, st.PAGE_URL)
    assert result.get("refused") is None, result.get("why")
    assert result["pressed"] is True and result["closed"] is True
    assert result["pressed_steps"] == {"clicks": 1, "escapes": 1}
    assert [s["vertical"] for s in result["recent_searches"]] == ["jobs", "all"]
    assert result["recent_searches"][0]["keywords"] == JOBS_WORDS
    assert await _witness(page) == {"opens": 1, "escapes": 1, "keys": 0, "typed": 0, "in_listbox": 0}
    assert await page.locator("[role=listbox]").count() == 0
    _no_needle(result)


async def test_an_autocomplete_input_outside_role_search_is_refused(page):
    outside = OPEN.replace('role="search" data-expanded="x"', 'data-expanded="x"', 1)
    assert outside != OPEN
    await _world(page, outside)
    result = await st.disclose_recent_searches(page, st.PAGE_URL)
    assert result["refused"] == "target_count" and "draws 0 input(s)" in result["why"]
    assert "1 autocomplete input(s)" in result["why"]
    assert (await _witness(page))["opens"] == 0


async def test_a_second_matching_input_refuses(page):
    await _world(page)
    await page.evaluate(
        """() => { const d = document.createElement('div'); d.setAttribute('role', 'search');
                   d.innerHTML = '<input aria-autocomplete="list">'; document.body.prepend(d); }"""
    )
    result = await st.disclose_recent_searches(page, st.PAGE_URL)
    assert result["refused"] == "target_count" and "draws 2 input(s)" in result["why"]
    assert (await _witness(page))["opens"] == 0


async def test_a_box_already_open_is_not_pressed(page):
    await page.set_content(OPEN, wait_until="domcontentloaded", timeout=60_000)
    result = await st.disclose_recent_searches(page, st.PAGE_URL)
    assert result["refused"] == "already_open"


async def test_a_box_that_does_not_close_withholds_what_it_read(page):
    await _world(page, leave="open")
    result = await st.disclose_recent_searches(page, st.PAGE_URL)
    assert result["refused"] == "did_not_close" and result["closed"] is False
    assert "recent_searches" not in result
    assert (await _witness(page))["escapes"] == 1


async def test_a_click_that_opens_nothing_is_not_escaped(page):
    await _world(page, leave="shut")
    result = await st.disclose_recent_searches(page, st.PAGE_URL)
    assert result["refused"] == "did_not_open"
    assert result["pressed_steps"] == {"clicks": 1, "escapes": 0}
    assert await _witness(page) == {"opens": 1, "escapes": 0, "keys": 0, "typed": 0, "in_listbox": 0}


async def test_a_typing_step_is_refused_before_the_page_is_touched(page):
    await _world(page)
    target = page.locator(st.TARGET)
    for step in ("type", "Enter", "fill", "a"):
        with pytest.raises(WriteAttemptError):
            await st._press(target, step)
    assert await _witness(page) == {"opens": 0, "escapes": 0, "keys": 0, "typed": 0, "in_listbox": 0}


# ---------------------------------------------------------------------------
# 3. The call sites and the tool
# ---------------------------------------------------------------------------


def test_the_module_presses_at_two_sites_and_types_nowhere():
    path = "linkedin_server/search_typeahead.py"
    mine = sorted(entry for entry in readonly.SANCTIONED_MUTATIONS if entry[0] == path)
    assert mine == [(path, "_press", "click"), (path, "_press", "press")]
    source = (REPO / path).read_text(encoding="utf-8")
    for spelling in (".fill(", ".type(", ".press_sequentially(", ".keyboard", ".insert_text("):
        assert spelling not in source, spelling
    assert st.STEPS == {"open": "click", "close": "Escape"}


def test_the_tool_is_registered_and_its_name_reads():
    assert callable(getattr(server, "linkedin_recent_searches", None))
    assert not readonly.name_implies_write("linkedin_recent_searches")
