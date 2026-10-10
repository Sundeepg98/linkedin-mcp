"""His own follower list (census ``P L2b``), read as counts and relations only.

THE PAGE IS REAL, AND ONLY ITS SHAPE IS TRACKED. ``tests/fixtures/live2/
followers.html`` is the live lane's session-2 capture of the admitted address,
reduced to a skeleton: every text one ``x``, ids kept as their hash, LinkedIn's
own words (``Following``, ``Follow``) kept. Every test here reads THAT page, or
that page with one thing planted in it; nothing is invented markup alone.

THE PLANTS, each shown changing the verdict (or, for the name, changing
nothing at all):

* a row with TWO follow-state buttons -> that row is ``unknown``;
* a button word OUTSIDE the vocabulary -> that row is ``unknown``;
* a row with NO button -> that row is ``unknown``;
* the ``Following`` tab selected -> the read refuses, not the followers side;
* a strip with no selected tab -> the read refuses, side unreadable;
* a NAME planted in every button's ``aria-label``, every member link and every
  photo's ``alt`` -> the answer is identical and carries no word of it.

THE CONTROLS weaken one check each and show its plant going through, so no
check here is one that cannot fail.

NOTHING HERE REACHES LINKEDIN. A local headless Chromium over ``set_content``,
every request the copy would make refused first (``tests/network_guard.py``).
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import followers_list
from tests.plantedpage import PLANT, carries_a_plant_word
from tests.test_writes import browser_page  # noqa: F401 -- fixture

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests" / "fixtures" / "live2" / "followers.html"
MODULE = REPO / "linkedin_server" / "followers_list.py"

#: One row's follow-state button as the skeleton draws it: its label is the
#: skeleton's ``x`` (live: the member's name), its word in the text slot.
ROW_BUTTON = re.compile(
    r'<button aria-label="x" id="k[0-9a-f]+" class="artdeco-button[^"]*">\s*'
    r'<span class="artdeco-button__text">\s*(Following|Follow)\s*</span>\s*</button>'
)

#: A tab of the strip: its selected state and its text.
TAB = re.compile(
    r'(<button [^>]*aria-selected=")(true|false)("[^>]*role="tab">\s*)(Following|x)(\s*</button>)'
)


def _skeleton() -> str:
    return FIXTURE.read_text(encoding="ascii")


async def _refused(route: Any) -> None:
    await route.abort()


async def _read(page: Any, html: str) -> dict[str, Any]:
    """Serve ``html`` with every request refused first, then read it."""
    await page.route("**/*", _refused)
    await page.set_content(html, wait_until="domcontentloaded")
    return await followers_list.read_followers_list(page)


#: What the reader answers on the tracked skeleton, every key.
SKELETON_READING: dict[str, Any] = {
    "surface": "own_follower_list",
    "side": "followers",
    "refused": None,
    "tabs_seen": 2,
    "lists_seen": 1,
    "rows_seen": 10,
    "rows_read": 10,
    "he_follows_back": 9,
    "he_does_not_follow_back": 1,
    "unknown": 0,
    "unknown_why": {"no_button": 0, "several_buttons": 0, "other_word": 0, "unreadable": 0},
    "one_page": True,
    "beyond_first_render": "not_read",
    "readable": True,
    "scope": followers_list.SCOPE,
}

#: Every string an answer may hold: the module's own closed words.
CLOSED_STRINGS = frozenset(
    {
        "own_follower_list", "not_read", followers_list.SCOPE,
        *followers_list.SIDES, *followers_list.REFUSALS,
    }
)


def page_text_in(answer: Any, path: str = "$") -> list[str]:
    """Every place in ``answer`` holding a string the module did not write:
    a value outside :data:`CLOSED_STRINGS`, or a key outside the reading's
    own. Empty means no field held page text."""
    found: list[str] = []
    if isinstance(answer, dict):
        for key, value in answer.items():
            if key not in SKELETON_READING and key not in followers_list.UNKNOWN_REASONS:
                found.append(f"{path} key {key!r}")
            found += page_text_in(value, f"{path}[{key!r}]")
    elif isinstance(answer, (list, tuple, set, frozenset)):
        for index, value in enumerate(answer):
            found += page_text_in(value, f"{path}[{index}]")
    elif isinstance(answer, str) and answer not in CLOSED_STRINGS:
        found.append(path)
    elif not isinstance(answer, (str, int, bool, type(None))):
        found.append(f"{path} ({type(answer).__name__})")
    return found


# ---------------------------------------------------------------------------
# The premise: the tracked skeleton draws what the reader rests on
# ---------------------------------------------------------------------------


def test_the_skeleton_draws_the_shape_the_reader_rests_on() -> None:
    """Counted off the file, so a fixture that changed fails HERE first."""
    html = _skeleton()
    assert html.count("<main") == 1
    assert html.count('role="tablist"') == 1
    tabs = TAB.findall(html)
    assert sorted((t[1], t[3]) for t in tabs) == [("false", "Following"), ("true", "x")], tabs
    assert html.count(followers_list.ROW_SELECTOR[1:-1]) == 10
    words = ROW_BUTTON.findall(html)
    assert (words.count("Following"), words.count("Follow")) == (9, 1), words
    # Each row draws two member links; the skeleton writes each as /in/x.
    assert html.count('href="https://www.linkedin.com/in/x?miniProfileUrn=x"') == 20


# ---------------------------------------------------------------------------
# The reading, and each plant (four engine launches: this box measured about
# eleven seconds a launch, so plants share a page and each says its own name)
# ---------------------------------------------------------------------------


def _plant_first_button(html: str, into: str) -> str:
    """Replace the FIRST row button that reads Following with ``into``."""
    match = next(m for m in ROW_BUTTON.finditer(html) if m.group(1) == "Following")
    return html[: match.start()] + into + html[match.end():]


def _first_following_button(html: str) -> str:
    return next(m.group(0) for m in ROW_BUTTON.finditer(html) if m.group(1) == "Following")


def _word_button(word: str) -> str:
    return (
        '<button aria-label="x" id="kplanted1" class="artdeco-button artdeco-button--2">'
        f'<span class="artdeco-button__text">{word}</span></button>'
    )


def _select_the_following_tab(html: str) -> str:
    def swap(m: re.Match[str]) -> str:
        selected = "true" if m.group(4) == "Following" else "false"
        return m.group(1) + selected + m.group(3) + m.group(4) + m.group(5)

    out, swapped = TAB.subn(swap, html)
    assert swapped == 2
    return out


def _plant_a_name_everywhere(html: str) -> str:
    """The member's name where the live page draws it: every row button's
    ``aria-label``, every member link (its address and its text) and every
    photo's ``alt``."""
    slug = PLANT.lower().replace(" ", "-")
    html = html.replace('<button aria-label="x" id="k', f'<button aria-label="{PLANT}" id="k')
    html = html.replace("/in/x?miniProfileUrn=x", f"/in/{slug}?miniProfileUrn={slug}")
    html = html.replace('alt="x"', f'alt="{PLANT}"')
    html, linked = re.subn(
        r'(data-test-app-aware-link="">\s*)x(\s*</a>)', rf"\g<1>{PLANT}\g<2>", html
    )
    assert linked == 10, linked
    return html


async def test_the_skeleton_reads_nine_followed_back_and_a_planted_name_changes_nothing(
    browser_page,
) -> None:
    """THE READING, and the name the live page draws where the skeleton draws
    ``x``: in every button's ``aria-label``, every member link and every
    photo -- the answer is identical and carries no word of it."""
    answer = await _read(browser_page, _skeleton())
    assert answer == SKELETON_READING, answer
    assert page_text_in(answer) == []

    planted = _plant_a_name_everywhere(_skeleton())
    assert planted.count(PLANT) >= 30
    answer = await _read(browser_page, planted)
    assert answer == SKELETON_READING, answer
    assert not carries_a_plant_word(repr(answer))
    assert page_text_in(answer) == []


#: Each row plant: (what is put where the first Following button was, why
#: that row is unknown). WHICH OF TWO BUTTONS IS THE FOLLOW STATE IS NOT
#: GUESSED; EXACT, NOT NEAR -- ``Follow back`` starts with a vocabulary word
#: and is still another word.
ROW_PLANTS: dict[str, tuple[str, str]] = {
    "two follow-state buttons": ("{original}" + _word_button("Following"), "several_buttons"),
    "the word Follow back": (_word_button("Follow back"), "other_word"),
    "the word Message": (_word_button("Message"), "other_word"),
    "no button": ("", "no_button"),
}


async def test_each_row_plant_makes_that_row_unknown(browser_page) -> None:
    html = _skeleton()
    original = _first_following_button(html)
    for name, (into, reason) in ROW_PLANTS.items():
        answer = await _read(browser_page, _plant_first_button(html, into.replace("{original}", original)))
        got = (answer["he_follows_back"], answer["he_does_not_follow_back"], answer["unknown"])
        assert got == (8, 1, 1), (name, answer)
        assert answer["unknown_why"][reason] == 1, (name, answer)
        assert answer["rows_seen"] == answer["rows_read"] == 10, (name, answer)
        assert page_text_in(answer) == [], name


async def test_each_side_plant_refuses_the_read(browser_page) -> None:
    """THE SIBLING LIST IS OTHER PEOPLE: with the Following tab selected the
    rows are the people HE follows, so no relation is counted at all; a strip
    that selects no tab cannot say which side is open. The denominators stay,
    so a refusal says what was drawn."""
    answer = await _read(browser_page, _select_the_following_tab(_skeleton()))
    assert (answer["side"], answer["refused"]) == ("following", "not_the_followers_side"), answer
    assert answer["he_follows_back"] == answer["he_does_not_follow_back"] == 0, answer
    assert (answer["rows_seen"], answer["rows_read"], answer["readable"]) == (10, 0, False)
    assert page_text_in(answer) == []

    no_selected = _skeleton().replace('aria-selected="true"', 'aria-selected="false"')
    answer = await _read(browser_page, no_selected)
    assert (answer["side"], answer["refused"]) == ("unknown", "side_unreadable"), answer
    assert answer["he_follows_back"] == 0 and answer["readable"] is False, answer


# ---------------------------------------------------------------------------
# Controls: each check weakened lets its plant through
# ---------------------------------------------------------------------------


async def test_control_each_check_weakened_lets_its_plant_through(browser_page, monkeypatch) -> None:
    html = _skeleton()
    two_buttons = _plant_first_button(html, _first_following_button(html) + _word_button("Following"))

    async def first_button_wins(row: Any) -> str:
        slot = row.get_by_role("button").first.locator(followers_list.WORD_SLOT_SELECTOR)
        return followers_list.classify_word(await slot.first.inner_text())

    with monkeypatch.context() as m:
        m.setattr(followers_list, "_relation_of", first_button_wins)
        answer = await _read(browser_page, two_buttons)
    assert answer["he_follows_back"] == 9 and answer["unknown"] == 0, answer

    def prefix_match(word: Any) -> str:
        text = str(word).strip()
        if text.startswith("Following"):
            return "he_follows_back"
        return "he_does_not_follow_back" if text.startswith("Follow") else "other_word"

    with monkeypatch.context() as m:
        m.setattr(followers_list, "classify_word", prefix_match)
        answer = await _read(browser_page, _plant_first_button(html, _word_button("Follow back")))
    assert answer["he_does_not_follow_back"] == 2 and answer["unknown"] == 0, answer

    async def any_selected_tab(main: Any) -> tuple[str, int]:
        selected = await main.get_by_role("tab", selected=True).count()
        return ("followers" if selected == 1 else "unknown"), await main.get_by_role("tab").count()

    with monkeypatch.context() as m:
        m.setattr(followers_list, "_side", any_selected_tab)
        answer = await _read(browser_page, _select_the_following_tab(html))
    assert answer["side"] == "followers" and answer["refused"] is None, answer


def test_control_the_page_text_check_finds_a_string_it_did_not_write() -> None:
    leaky = {**SKELETON_READING, "unknown_why": {"other_word": 0, "label": PLANT}}
    assert page_text_in(leaky) == ["$['unknown_why'] key 'label'", "$['unknown_why']['label']"]
    assert page_text_in({**SKELETON_READING, "side": PLANT}) == ["$['side']"]


# ---------------------------------------------------------------------------
# Pure halves
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "landed,on_the_list",
    [
        (followers_list.FOLLOWERS_URL, True),
        (followers_list.FOLLOWERS_URL.rstrip("/"), True),
        (followers_list.FOLLOWERS_URL + "?x=1", True),
        ("https://www.linkedin.com/mynetwork/network-manager/people-follow/following/", False),
        ("https://www.linkedin.com/mynetwork/network-manager/people-follow/", False),
        ("https://www.linkedin.com/mynetwork/", False),
        ("https://www.linkedin.com/authwall?trk=x", False),
        ("http://www.linkedin.com/mynetwork/network-manager/people-follow/followers/", False),
        ("https://linkedin.example/mynetwork/network-manager/people-follow/followers/", False),
        ("", False),
        (None, False),
    ],
)
def test_a_landing_is_the_list_only_at_its_own_path(landed: Any, on_the_list: bool) -> None:
    assert followers_list.landed_on_the_list(landed) is on_the_list


def test_the_landing_refusal_reads_nothing_and_says_nothing_of_the_landing() -> None:
    refusal = followers_list.landed_elsewhere()
    assert refusal["refused"] == "landed_elsewhere" and refusal["readable"] is False
    assert refusal["rows_seen"] == 0 and page_text_in(refusal) == []


@pytest.mark.parametrize(
    "word,relation",
    [
        ("Following", "he_follows_back"),
        ("\n  Following \n", "he_follows_back"),
        ("Follow", "he_does_not_follow_back"),
        ("following", "other_word"),
        ("Follow back", "other_word"),
        ("Unfollow", "other_word"),
        ("", "other_word"),
        (None, "other_word"),
        (PLANT, "other_word"),
    ],
)
def test_a_word_maps_to_a_relation_only_exactly(word: Any, relation: str) -> None:
    assert followers_list.classify_word(word) == relation


#: Calls that act on a page, and the one read that could take a label.
_FORBIDDEN_CALLS = frozenset(
    {
        "click", "dblclick", "tap", "press", "type", "fill", "check", "uncheck",
        "hover", "focus", "select_option", "set_input_files", "dispatch_event",
        "scroll_into_view_if_needed", "goto", "go_back", "go_forward", "reload",
        "evaluate", "evaluate_all", "evaluate_handle", "get_attribute", "wheel",
    }
)


def _method_calls(source: str) -> set[str]:
    """Every ``<x>.<method>(...)`` name called in ``source``. Docstrings and
    comments cannot vote: only ``ast.Call`` nodes count."""
    return {
        node.func.attr
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }


def test_the_module_presses_scrolls_loads_and_evaluates_nothing() -> None:
    """ONE PAGE, FIRST RENDER, NO ACT: no call that presses, types, scrolls,
    navigates or runs a script, and no ``get_attribute`` at all -- so the
    button's ``aria-label``, which live is the member's name, cannot be read."""
    called = _method_calls(MODULE.read_text(encoding="utf-8"))
    assert not called & _FORBIDDEN_CALLS, sorted(called & _FORBIDDEN_CALLS)
    assert {"count", "inner_text", "get_by_role", "locator"} <= called


def test_control_the_act_check_finds_a_label_read_and_a_press() -> None:
    """The check above, shown failing: a label read and a press are found,
    and the same words in a docstring are not."""
    planted = (
        "async def read(row):\n"
        "    '''row.click() and row.get_attribute() in prose do not count'''\n"
        "    await row.get_attribute('aria-label')\n"
        "    await row.locator('button').click()\n"
    )
    assert _method_calls(planted) & _FORBIDDEN_CALLS == {"get_attribute", "click"}
