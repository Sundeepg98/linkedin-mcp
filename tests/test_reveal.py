"""THE DECIDED REVEALS, tested against a fake page that records every event.

``linkedin_server/reveal.py`` presses ONE plain control per table entry, named
by a recorded delegated call. Every test runs against a stateful FAKE page, so
the tests can assert WHEN a refusal was taken -- before the page was asked for
anything, after a read with nothing pressed, or after the press -- and not
merely that it was.

THE REFUSAL INVENTORY at the bottom is the ``tests/test_press.py`` discipline,
scoped to this module: every reason ``reveal.py`` hands to ``_refuse`` is
classified by when it is knowable, and every one is driven by a real input
(or, for one, a plant), so a new refusal cannot land unclassified.
"""
from __future__ import annotations

import ast
import json
import pathlib

import pytest

from linkedin_server import dom, press, readonly, reveal

BASE = "https://www.linkedin.com"
PV = f"{BASE}/analytics/profile-views/"
KEY = "profile_views_show_more_analytics"
READING = "profile_views_filter_menu"
PHRASE = "show more analytics"


class Btn:
    def __init__(self, page, index, label, attrs=None, visible=True):
        self.page, self.index, self.label = page, index, label
        self.attrs = dict(attrs or {})
        self.visible = visible

    async def get_attribute(self, name):
        self.page.events.append(("attr", self.index, name))
        return self.attrs.get(name)

    async def is_visible(self):
        return self.visible

    async def inner_text(self):
        return self.label

    async def click(self, **_kwargs):
        self.page.events.append(("click", self.index))
        if self.page.raise_on_click:
            raise TimeoutError("synthetic")
        self.page.revealed = True
        if self.page.navigates:
            self.page.url = self.page.url + "?more=1"


class Buttons:
    def __init__(self, page):
        self.page = page

    async def count(self):
        return len(self.page.buttons)

    def nth(self, index):
        return self.page.buttons[index]


class Counted:
    def __init__(self, value):
        self.value = value

    async def count(self):
        return self.value()


class Main:
    def __init__(self, page):
        self.page = page

    def locator(self, selector):
        assert selector == "button", selector
        return Buttons(self.page)


class Page:
    def __init__(self, url=PV, *, labels=("all filters", "reset", "Show more analytics"),
                 attrs=None, invisible=(), navigates=False, raise_on_click=False):
        self.url = url
        self.revealed = False
        self.navigates = navigates
        self.raise_on_click = raise_on_click
        self.events: list = []
        attrs = attrs or {}
        self.buttons = [Btn(self, i, label, attrs.get(i), i not in invisible)
                        for i, label in enumerate(labels)]

    def locator(self, selector):
        self.events.append(("locator", selector))
        if selector == "main":
            return Main(self)
        if selector == "main *":
            return Counted(lambda: 140 if self.revealed else 100)
        if selector in dict(press.WITNESS_SELECTORS).values():
            return Counted(lambda: 0)
        raise AssertionError(selector)

    async def wait_for_timeout(self, ms):
        self.events.append(("wait", ms))

    async def evaluate(self, script, arg=None):
        assert script == dom.COUNT_LINES_JS
        self.events.append(("reading", "open" if self.revealed else "closed"))
        lines = 30 if self.revealed else 20
        return {"elements": lines * 3, "chunks": lines, "chunks_capped": 0,
                "hidden_skipped": 0, "non_content_skipped": 0, "matches": []}


def steady(values=None):
    values = values or {"headline_viewers": 29, "invitations": 0}

    async def read():
        return dict(values)
    return read


def moving():
    seq = iter([{"headline_viewers": 29}, {"headline_viewers": 30}])

    async def read():
        return next(seq)
    return read


def _clicks(page):
    return [e for e in page.events if e[0] == "click"]


def _run(coro):
    import asyncio
    return asyncio.run(coro)


# --------------------------------------------------------------------------
# The table
# --------------------------------------------------------------------------


def test_every_entry_is_complete_normalised_and_on_an_admitted_priced_surface():
    assert reveal.DECIDED_REVEALS, "an empty table admits nothing and tests nothing"
    for key, entry in reveal.DECIDED_REVEALS:
        for field in reveal._REVEAL_REQUIRED:
            assert entry.get(field), (key, field)
        assert reveal.normalised_label(entry["phrase"]) == entry["phrase"], key
        assert "DECIDED" in entry["decided"], key
        for surface in entry["surfaces"]:
            url = BASE + surface
            assert readonly.is_read_url(url), (key, surface)
            assert not press.check_basis(url).get("refused"), (key, surface)


def test_the_normaliser_is_the_one_the_table_assumes():
    assert reveal.normalised_label("  Show  more\nAnalytics! ") == PHRASE
    assert reveal.normalised_label(None) == ""


# --------------------------------------------------------------------------
# Refused before any contact
# --------------------------------------------------------------------------


@pytest.mark.parametrize("url,key,reason", [
    (PV, "a_reveal_nobody_decided", "reveal_not_decided"),
    (f"{BASE}/feed/", KEY, "reveal_not_for_this_surface"),
    (f"{BASE}/pulse/drafts/", KEY, "address_not_admitted"),
])
def test_what_the_address_and_key_decide_is_refused_before_the_page_is_asked(url, key, reason):
    page = Page(url)
    verdict = _run(reveal.reveal(page, key=key, read_counters=steady()))
    assert verdict["refused"] == reason
    assert page.events == [], "the page was touched before a refusal it could have taken first"


def test_no_counter_reader_is_refused_before_contact():
    page = Page()
    verdict = _run(reveal.reveal(page, key=KEY, read_counters=None))
    assert verdict["refused"] == "no_counter_reader_supplied"
    assert page.events == []


def test_a_reading_not_sanctioned_here_is_refused_before_contact():
    page = Page()
    verdict = _run(reveal.reveal(page, key=KEY, read_counters=steady(),
                                 reading="feed_item_share_menu"))
    assert verdict["refused"] == "reading_not_for_this_surface"
    assert page.events == []


# --------------------------------------------------------------------------
# Refused after a read, with nothing pressed
# --------------------------------------------------------------------------


def test_an_unreadable_counter_is_refused_before_the_click():
    page = Page()
    verdict = _run(reveal.reveal(page, key=KEY,
                                 read_counters=steady({"headline_viewers": None})))
    assert verdict["refused"] == "counters_unreadable_before_any_press"
    assert _clicks(page) == []


@pytest.mark.parametrize("labels", [
    ("all filters", "reset"),
    ("show more analytics", "Show More Analytics"),
])
def test_not_exactly_one_matching_control_presses_nothing(labels):
    page = Page(labels=labels)
    verdict = _run(reveal.reveal(page, key=KEY, read_counters=steady()))
    assert verdict["refused"] == "reveal_control_not_unique"
    assert _clicks(page) == []


def test_a_control_carrying_disclosure_state_is_not_a_candidate():
    page = Page(labels=("show more analytics",), attrs={0: {"aria-expanded": "false"}})
    verdict = _run(reveal.reveal(page, key=KEY, read_counters=steady()))
    assert verdict["refused"] == "reveal_control_not_unique"
    assert _clicks(page) == []


def test_an_invisible_match_is_not_a_candidate():
    page = Page(labels=("show more analytics", "show more analytics"), invisible=(0,))
    verdict = _run(reveal.reveal(page, key=KEY, read_counters=steady()))
    assert verdict["permitted"] is True
    assert _clicks(page) == [("click", 1)]


# --------------------------------------------------------------------------
# The press, and what it must show
# --------------------------------------------------------------------------


def test_the_decided_control_and_only_it_is_pressed_and_shown_to_change_no_state():
    page = Page()
    verdict = _run(reveal.reveal(page, key=KEY, read_counters=steady(), reading=READING))
    assert _clicks(page) == [("click", 2)]
    assert verdict["permitted"] is True and verdict["pressed"] is True
    assert "refused" not in verdict
    assert verdict["url_unchanged"] is True
    assert verdict["main_elements"] == {"before": 100, "after": 140}
    assert verdict["reading"]["new_lines"] == 10
    assert ("wait", reveal.REVEAL_SETTLE_MS) in page.events


def test_the_readings_bracket_the_click():
    page = Page()
    _run(reveal.reveal(page, key=KEY, read_counters=steady(), reading=READING))
    order = [e for e in page.events if e[0] in ("reading", "click")]
    assert order == [("reading", "closed"), ("click", 2), ("reading", "open")]


def test_a_reveal_that_navigates_is_refused_and_still_says_it_pressed():
    page = Page(navigates=True)
    verdict = _run(reveal.reveal(page, key=KEY, read_counters=steady()))
    assert verdict["refused"] == "reveal_moved_the_url"
    assert verdict["pressed"] is True and verdict["permitted"] is False
    assert verdict["url_unchanged"] is False


def test_a_moving_counter_is_refused_and_still_says_it_pressed():
    page = Page()
    verdict = _run(reveal.reveal(page, key=KEY, read_counters=moving()))
    assert verdict["refused"] == "reveal_moved_a_counter"
    assert verdict["pressed"] is True and verdict["permitted"] is False


def test_a_raising_click_is_press_failed_and_names_only_the_type():
    page = Page(raise_on_click=True)
    verdict = _run(reveal.reveal(page, key=KEY, read_counters=steady()))
    assert verdict["refused"] == "press_failed"
    assert "TimeoutError" in verdict["why"] and "synthetic" not in verdict["why"]


def test_no_label_the_page_wrote_leaves_in_the_verdict():
    page = Page(labels=("a label only the page wrote", "Show more analytics"))
    verdict = _run(reveal.reveal(page, key=KEY, read_counters=steady(), reading=READING))
    rendered = json.dumps(verdict, default=str)
    assert "a label only the page wrote" not in rendered
    assert "Show more analytics" not in rendered


# --------------------------------------------------------------------------
# The refusal inventory for this module
# --------------------------------------------------------------------------

#: Every reason reveal.py hands to _refuse, by when it becomes knowable.
WHEN_KNOWABLE: dict[str, str] = {
    "reveal_not_decided": "before_any_contact",
    "reveal_entry_incomplete": "before_any_contact",
    "reveal_not_for_this_surface": "before_any_contact",
    "no_counter_reader_supplied": "before_any_contact",
    "counters_unreadable_before_any_press": "after_a_read",
    "reveal_control_not_unique": "after_a_read",
    "press_failed": "after_the_press",
    "reveal_moved_the_url": "after_the_press",
    "reveal_moved_a_counter": "after_the_press",
}


def _reasons_in_source() -> set[str]:
    tree = ast.parse(pathlib.Path(reveal.__file__).read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name == "_refuse" and node.args:
                first = node.args[0]
                assert isinstance(first, ast.Constant) and isinstance(first.value, str)
                found.add(first.value)
    return found


def test_the_inventory_is_exactly_what_the_module_can_emit():
    assert _reasons_in_source() == set(WHEN_KNOWABLE)


#: One input per reason, driven below. The incomplete-entry reason needs a
#: plant (the committed table has no such entry, and the test above keeps it so).
REACHES: dict[str, dict] = {
    "reveal_not_decided": {"key": "nobody_decided_this"},
    "reveal_not_for_this_surface": {"url": f"{BASE}/feed/"},
    "no_counter_reader_supplied": {"reader": None},
    "counters_unreadable_before_any_press": {"reader": steady({"invitations": None})},
    "reveal_control_not_unique": {"labels": ("reset",)},
    "press_failed": {"raise_on_click": True},
    "reveal_moved_the_url": {"navigates": True},
    "reveal_moved_a_counter": {"reader": moving()},
}


@pytest.mark.parametrize("reason", sorted(REACHES))
def test_every_reason_is_reached_when_it_says(reason):
    spec = dict(REACHES[reason])
    key = spec.pop("key", KEY)
    reader = spec.pop("reader", steady())
    page = Page(spec.pop("url", PV), **spec)
    verdict = _run(reveal.reveal(page, key=key, read_counters=reader))
    assert verdict.get("refused") == reason
    when = WHEN_KNOWABLE[reason]
    if when == "before_any_contact":
        assert page.events == []
    elif when == "after_a_read":
        assert _clicks(page) == []
    else:
        assert _clicks(page), "classified after_the_press but nothing was pressed"


def test_the_incomplete_entry_is_refused_by_the_plant(monkeypatch):
    monkeypatch.setattr(reveal, "DECIDED_REVEALS", ((KEY, {"surfaces": ("/analytics/profile-views/",), "phrase": PHRASE}),))
    page = Page()
    verdict = _run(reveal.reveal(page, key=KEY, read_counters=steady()))
    assert verdict["refused"] == "reveal_entry_incomplete"
    assert page.events == []


def test_every_classified_reason_is_driven():
    assert set(REACHES) | {"reveal_entry_incomplete"} == set(WHEN_KNOWABLE)
