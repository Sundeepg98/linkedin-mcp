"""``M C43``: an item's own words, read off its permalink -- lane B3, 2026-10-10.

Driven through a real engine over the ONE tracked item-permalink capture,
``tests/fixtures/live2/own_post.html`` (his own item, live session 2). Every
plant is synthetic and is written into that capture by the test's own page
script, so the structure under test is the captured one.

WHAT IS HELD:

* the reader returns ONE ``people_data.Post`` record whose words are the
  item's, sanitised and capped at ``CAPS["text"]``, its link the permalink the
  caller's key composed;
* a comment's words never reach the record (the scope is the description);
* a second item drawn on the page, an organisation author, or a missing
  description each return NO record, and the planted words appear nowhere;
* a control inside the description reads ``expanded: False``;
* the key is validated by shape, and a refusal never repeats the value;
* nothing reaches a log record.

CONTROLS, each weakening one check and showing its plant getting through
(``test_control_each_check_weakened_lets_its_plant_through``), so no check
here is one that could not fail.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from linkedin_server import item_text, people_data
from tests.test_writes import browser_page  # noqa: F401 -- a fixture

CAPTURE = Path(__file__).parent / "fixtures" / "live2" / "own_post.html"

#: A synthetic key: four digits, under the six-digit run the identity guard
#: refuses in a tracked file.
ITEM = "urn:li:activity:1234"
LINK = "https://www.linkedin.com/feed/update/urn:li:activity:1234/"

WORDS_PLANT = "SYNTHETIC ITEM WORDS PLANT 7f3a"
COMMENT_PLANT = "SYNTHETIC COMMENT PLANT 9c1e"


async def _refuse(route) -> None:  # noqa: ANN001 - playwright route
    # THE CAPTURE KEEPS ITS IMAGE AND TRACKER ADDRESSES' SHAPES, so a browser
    # loading it would fetch them: every request is refused in the page's own
    # route first, as the reaction test over this capture does.
    await route.abort()


async def _load(page, script: str = "", arg=None) -> None:
    await page.unroute("**/*")
    await page.route("**/*", _refuse)
    await page.set_content(
        CAPTURE.read_text(encoding="utf-8"), wait_until="domcontentloaded", timeout=60_000
    )
    if script:
        await page.evaluate(script, arg)


#: The item's words replaced by a plant, inside the captured container.
SET_WORDS = """(t) => {
  const el = document.querySelector('main .feed-shared-update-v2__description .update-components-update-v2__commentary');
  el.textContent = t;
}"""

#: A comment's words replaced by a plant, and the item's words by another.
SET_COMMENT = """(t) => {
  const c = document.querySelector('main .comments-comment-item__main-content');
  c.textContent = t[0];
  document.querySelector('main .update-components-update-v2__commentary').textContent = t[1];
}"""

#: A second item description drawn in main -- a repost's shape.
SECOND_ITEM = """(t) => {
  const d = document.querySelector('main .feed-shared-update-v2__description');
  d.querySelector('.update-components-update-v2__commentary').textContent = t;
  d.parentElement.appendChild(d.cloneNode(true));
}"""

#: A second words container inside the one description.
SECOND_WORDS = """(t) => {
  const w = document.querySelector('main .update-components-update-v2__commentary');
  w.textContent = t;
  w.parentElement.appendChild(w.cloneNode(true));
}"""

#: The actor link pointed at an organisation Page instead of a member.
PAGE_AUTHOR = """(t) => {
  document.querySelector('main .update-components-update-v2__commentary').textContent = t;
  const a = document.querySelector('main a.update-components-actor__meta-link');
  a.setAttribute('href', 'https://www.linkedin.com/company/x/');
}"""

#: A control drawn inside the description -- a see-more toggle's shape.
SEE_MORE = """() => {
  const d = document.querySelector('main .feed-shared-update-v2__description');
  const b = document.createElement('button');
  b.textContent = 'x';
  d.appendChild(b);
}"""

#: The description removed altogether.
NO_DESCRIPTION = """(t) => {
  const d = document.querySelector('main .feed-shared-update-v2__description');
  d.remove();
}"""


def _flat(value) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


# --------------------------------------------------------------------------
# The read itself
# --------------------------------------------------------------------------


async def test_the_capture_reads_as_one_record_with_its_words(browser_page):
    await _load(browser_page)
    out = await item_text.read_item_text(browser_page, link=LINK)
    assert out["readable"] is True, out["why"]
    assert out["descriptions_drawn"] == 1
    assert out["words_drawn"] == 1
    assert out["words_in_main"] == 1
    assert out["expanded"] is True
    assert out["truncated"] is False
    record = people_data.as_record(out["item"])
    assert type(record) is people_data.Post
    assert type(record.author) is people_data.Person
    assert record.link == LINK
    # The captured words are reduced to x's; they are read, not invented.
    assert record.text and set(record.text) <= {"x", " "}
    assert out["why"] == item_text.WHY["read"]


async def test_planted_words_come_back_sanitised_inside_the_record(browser_page):
    dirty = "‮" + WORDS_PLANT + "​\n\n  tail"
    await _load(browser_page, SET_WORDS, dirty)
    out = await item_text.read_item_text(browser_page, link=LINK)
    assert out["readable"] is True, out["why"]
    record = people_data.as_record(out["item"])
    # How the engine collapses the whitespace around a zero-width space is
    # the engine's business; what is held is that nothing invisible survives,
    # the words are their own sanitised form, and the plant is in them.
    assert WORDS_PLANT in record.text and record.text.endswith("tail")
    assert "‮" not in record.text and "​" not in record.text
    assert record.text == people_data.sanitise(record.text, cap=people_data.CAPS["text"])
    assert out["item"][people_data.UNTRUSTED_KEY] == people_data.UNTRUSTED_NOTE


async def test_long_words_are_cut_at_the_cap_and_say_so(browser_page):
    await _load(browser_page, SET_WORDS, "y" * 3500)
    out = await item_text.read_item_text(browser_page, link=LINK)
    record = people_data.as_record(out["item"])
    assert len(record.text) == people_data.CAPS["text"]
    assert out["truncated"] is True


async def test_a_comment_never_reaches_the_record(browser_page):
    await _load(browser_page, SET_COMMENT, [COMMENT_PLANT, WORDS_PLANT])
    out = await item_text.read_item_text(browser_page, link=LINK)
    assert out["readable"] is True, out["why"]
    assert WORDS_PLANT in _flat(out)
    assert COMMENT_PLANT not in _flat(out)


@pytest.mark.parametrize(
    "script, why",
    [
        (SECOND_ITEM, "no_single_description"),
        (SECOND_WORDS, "no_single_words"),
        (PAGE_AUTHOR, "no_member_author"),
        (NO_DESCRIPTION, "no_single_description"),
    ],
    ids=["second_item", "second_words", "page_author", "no_description"],
)
async def test_an_ambiguous_page_returns_no_record_and_no_words(browser_page, script, why):
    await _load(browser_page, script, WORDS_PLANT)
    out = await item_text.read_item_text(browser_page, link=LINK)
    assert out["readable"] is False
    assert out["item"] is None
    assert out["why"] == item_text.WHY[why]
    assert WORDS_PLANT not in _flat(out)


async def test_a_control_in_the_description_reads_not_expanded(browser_page):
    await _load(browser_page, SEE_MORE)
    out = await item_text.read_item_text(browser_page, link=LINK)
    assert out["expanded"] is False
    assert out["readable"] is True


class _CountFails:
    """A page whose every locator count raises: the module logs it at DEBUG."""

    def locator(self, _selector):
        return self

    async def count(self):
        raise TypeError("synthetic control")


async def test_nothing_reaches_a_log_record(browser_page, caplog):
    # The PACKAGE logger is lowered by name: a root-only capture cannot hear
    # it (tests/test_a_debug_capture_lowers_the_package_logger.py).
    caplog.set_level(logging.DEBUG, logger="linkedin")
    # THE CONTROL: a failed read is logged at DEBUG, by its type only -- so
    # this capture is shown receiving this module's DEBUG records before an
    # absence is asserted over it.
    await item_text.read_item_text(_CountFails(), link=LINK)
    assert any(
        record.levelno == logging.DEBUG and "a count did not read" in record.getMessage()
        for record in caplog.records
    ), "no DEBUG control record came back: the capture cannot hear this module"
    assert "synthetic control" not in caplog.text
    await _load(browser_page, SET_WORDS, WORDS_PLANT)
    await item_text.read_item_text(browser_page, link=LINK)
    await _load(browser_page, PAGE_AUTHOR, WORDS_PLANT)
    await item_text.read_item_text(browser_page, link=LINK)
    assert WORDS_PLANT not in caplog.text


# --------------------------------------------------------------------------
# The key and the landing
# --------------------------------------------------------------------------


def test_the_permalink_is_composed_from_the_key_alone():
    assert item_text.permalink(ITEM) == LINK
    assert item_text.permalink("urn:li:ugcPost:99") == (
        "https://www.linkedin.com/feed/update/urn:li:ugcPost:99/"
    )


@pytest.mark.parametrize(
    "bad",
    [
        "",
        None,
        12,
        ITEM + "/",
        " " + ITEM,
        ITEM + "?x=1",
        "urn:li:activity:abc",
        "urn:li::1234",
        "urn:li:activity:" + "1" * 26,
        LINK,
        "urn:li:activity:12%34",
        "SYNTHETIC-NAME-LIKE-VALUE",
    ],
)
def test_a_wrong_key_is_refused_and_never_repeated(bad):
    with pytest.raises(ValueError) as caught:
        item_text.permalink(bad)
    if isinstance(bad, str) and bad:
        assert bad.strip() not in str(caught.value)


@pytest.mark.parametrize(
    "landed, expected",
    [
        (LINK, True),
        (LINK.rstrip("/"), True),
        (LINK + "?trk=x", True),
        ("https://www.linkedin.com/feed/update/urn:li:activity:4321/", False),
        ("https://www.linkedin.com/feed/", False),
        ("", False),
        (None, False),
    ],
)
def test_the_landing_must_be_the_address_asked_for(landed, expected):
    assert item_text.landed_on_the_item(landed, LINK) is expected


# --------------------------------------------------------------------------
# Controls: each check weakened lets its plant through
# --------------------------------------------------------------------------


#: A second words container drawn in main OUTSIDE the description, with the
#: plant in the description's own words: only the main-wide count refuses it.
WORDS_OUTSIDE = """(t) => {
  const w = document.querySelector('main .update-components-update-v2__commentary');
  w.textContent = t;
  const root = document.querySelector('main .feed-shared-update-v2');
  root.appendChild(w.cloneNode(true));
}"""


async def test_a_words_container_outside_the_description_is_refused(browser_page):
    await _load(browser_page, WORDS_OUTSIDE, WORDS_PLANT)
    out = await item_text.read_item_text(browser_page, link=LINK)
    assert out["readable"] is False
    assert out["descriptions_drawn"] == 1 and out["words_drawn"] == 1
    assert out["words_in_main"] == 2
    assert WORDS_PLANT not in _flat(out)


#: Each control replaces selectors with ones that count AT MOST one match --
#: the uniqueness a check relies on, removed -- and shows the plant the check
#: refuses getting through.
_FIRST_DESCRIPTION = "main .feed-shared-update-v2__description >> nth=0"
_FIRST_WORDS = _FIRST_DESCRIPTION + " >> .update-components-update-v2__commentary >> nth=0"


@pytest.mark.parametrize(
    "patches, script",
    [
        # Both uniqueness checks dropped: a second item's words get through.
        (
            {"DESCRIPTION": _FIRST_DESCRIPTION, "WORDS": _FIRST_WORDS,
             "WORDS_IN_MAIN": "main .update-components-update-v2__commentary >> nth=0"},
            SECOND_ITEM,
        ),
        # Only the main-wide count dropped: a container outside gets past.
        (
            {"WORDS_IN_MAIN": "main .update-components-update-v2__commentary >> nth=0"},
            WORDS_OUTSIDE,
        ),
    ],
    ids=["uniqueness_dropped", "main_wide_count_dropped"],
)
async def test_control_each_check_weakened_lets_its_plant_through(
    browser_page, monkeypatch, patches, script
):
    for constant, weakened in patches.items():
        monkeypatch.setattr(item_text, constant, weakened)
    await _load(browser_page, script, WORDS_PLANT)
    out = await item_text.read_item_text(browser_page, link=LINK)
    assert WORDS_PLANT in _flat(out), (
        "the weakened check still refused its plant, so this control cannot "
        "show the check doing any work"
    )
