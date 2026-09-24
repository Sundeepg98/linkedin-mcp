"""THE VIEW SWITCH, tested against a fake page shaped like the measured popover.

``linkedin_server/view_switch.py`` applies ONE ruled filter, reads the view,
and must prove the view was restored. The fake below is built from the
2026-09-23 capture (``_audit/2026-09-23-live-lane-session-1.md`` Entry 3): a
main-scoped ``div[role=button][aria-expanded]`` pill whose popover, once open,
draws ``div[role=checkbox][aria-label][aria-checked]`` options and its own
"show results" button, which applies the filter AND closes the popover. The
view the page shows is a pure function of the APPLIED options, so a restore
can be proven or refuted exactly.

Every event is recorded in order, so each refusal is asserted by WHEN it was
taken. The refusal inventory at the bottom keeps ``view_switch.py``'s reasons
classified and driven, as ``tests/test_press.py`` does for the gate.
"""
from __future__ import annotations

import ast
import asyncio
import pathlib

import pytest

from linkedin_server import press, readonly, view_switch

BASE = "https://www.linkedin.com"
PV = f"{BASE}/analytics/profile-views/"
KEY = "interesting_viewers_verified"
ALL_ROWS = [{"name": "v1", "tag": "verified"}, {"name": "v2", "tag": ""}, {"name": "v3", "tag": "verified"}]


def run(coro):
    return asyncio.run(coro)


class Loc:
    """One locator over one of the page's element lists, by name."""

    def __init__(self, page, kind, index=None):
        self.page, self.kind, self.index = page, kind, index

    # ---- collection behaviour -------------------------------------------
    def locator(self, selector):
        assert self.kind == "main" and selector == "[aria-expanded]", selector
        return Loc(self.page, "pills")

    def nth(self, index):
        return Loc(self.page, self.kind, index)

    @property
    def first(self):
        return Loc(self.page, self.kind, 0)

    async def count(self):
        return len(self.page.items(self.kind))

    async def wait_for(self, **_kwargs):
        if not self.page.items(self.kind):
            raise TimeoutError("no options drawn")

    # ---- element behaviour -----------------------------------------------
    def _el(self):
        return self.page.items(self.kind)[self.index]

    async def get_attribute(self, name):
        return self._el()["attrs"].get(name)

    async def is_visible(self):
        return self._el().get("visible", True)

    async def inner_text(self):
        return self._el().get("text", "")

    async def click(self, **_kwargs):
        self.page.events.append(("click", self.kind, self.index))
        if self.page.raise_on_click_number == len([e for e in self.page.events if e[0] == "click"]):
            raise TimeoutError("synthetic")
        self.page.on_click(self.kind, self.index)


class Page:
    def __init__(self, url=PV, *, captions=("Past 90 days", "Interesting viewers", "Company"),
                 options=("works at a company you follow", "verified"), checked=(),
                 sticky_option=False, no_apply=False, no_options_on_reopen=False,
                 sticky_server=False, raise_on_click_number=None):
        self.url = url
        self.events: list = []
        self.open_pill = None
        self.opened_times = 0
        self.captions = list(captions)
        self.option_labels = list(options)
        self.checked = {label: (label in checked) for label in options}
        self.applied = {label: (label in checked) for label in options}
        self.sticky_option = sticky_option
        self.no_apply = no_apply
        self.no_options_on_reopen = no_options_on_reopen
        self.sticky_server = sticky_server
        self.raise_on_click_number = raise_on_click_number

    def locator(self, selector):
        self.events.append(("locator", selector))
        if selector == "main":
            return Loc(self, "main")
        if selector == view_switch.OPTION_SELECTOR:
            return Loc(self, "options")
        if selector == "button":
            return Loc(self, "buttons")
        raise AssertionError(selector)

    def items(self, kind):
        if kind == "pills":
            return [{"attrs": {"role": "button", "aria-expanded": "true" if i == self.open_pill else "false"},
                     "text": caption} for i, caption in enumerate(self.captions)]
        if kind == "options":
            if self.open_pill is None or self.captions[self.open_pill] != "Interesting viewers":
                return []
            if self.no_options_on_reopen and self.opened_times > 1:
                return []
            return [{"attrs": {"aria-label": label, "aria-checked": "true" if self.checked[label] else "false"}}
                    for label in self.option_labels]
        if kind == "buttons":
            if self.open_pill is None or self.no_apply:
                return [{"text": "Reset"}]
            return [{"text": "Reset"}, {"text": "Show 12 results"}]
        raise AssertionError(kind)

    def on_click(self, kind, index):
        if kind == "pills":
            if self.open_pill == index:
                self.open_pill = None
            else:
                self.open_pill = index
                self.opened_times += 1
                self.checked = dict(self.applied)
        elif kind == "options":
            if not self.sticky_option:
                label = self.option_labels[index]
                self.checked[label] = not self.checked[label]
        elif kind == "buttons":
            if self.items("buttons")[index]["text"].lower().startswith("show"):
                if not (self.sticky_server and any(self.applied.values())):
                    self.applied = dict(self.checked)
                self.open_pill = None

    async def wait_for_timeout(self, ms):
        self.events.append(("wait", ms))

    def view(self):
        wanted = [label for label, on in self.applied.items() if on]
        rows = [r for r in ALL_ROWS if not wanted or r["tag"] in wanted]
        return {"headline": len(rows), "rows": rows}


def reader_for(page):
    async def read_view():
        page.events.append(("read_view",))
        return page.view()
    return read_view


def steady():
    async def read():
        return {"headline_viewers": 29}
    return read


def moving():
    seq = iter([{"headline_viewers": 29}, {"headline_viewers": 30}])

    async def read():
        return next(seq)
    return read


def clicks(page):
    return [(e[1], e[2]) for e in page.events if e[0] == "click"]


def fire(page, key=KEY, counters=None, view="page"):
    reader = reader_for(page) if view == "page" else view
    return run(view_switch.apply_and_restore(page, key=key, read_view=reader,
                                             read_counters=counters or steady()))


# --------------------------------------------------------------------------


def test_every_entry_is_complete_normalised_ruled_and_on_an_admitted_priced_surface():
    assert view_switch.VIEW_SWITCHES
    for key, entry in view_switch.VIEW_SWITCHES:
        for field in view_switch._ENTRY_REQUIRED:
            assert entry.get(field), (key, field)
        assert view_switch.normalised(entry["pill_caption"]) == entry["pill_caption"]
        assert view_switch.normalised(entry["option"]) == entry["option"]
        assert "VIEW-SWITCH-PRESS-RESTORED" in entry["ruling"]
        for surface in entry["surfaces"]:
            assert readonly.is_read_url(BASE + surface)
            assert not press.check_basis(BASE + surface).get("refused")


def test_the_apply_pattern_matches_the_measured_captions_and_nothing_near_them():
    for text in ("Show results", "Show 365 results", "show 1,234 results", "Show 1 result"):
        assert view_switch.APPLY_PATTERN.match(view_switch.normalised(text)), text
    for text in ("Show more analytics", "Reset", "Show", "results", "show all filters"):
        assert not view_switch.APPLY_PATTERN.match(view_switch.normalised(text)), text


# ---- refused before any contact ---------------------------------------------


@pytest.mark.parametrize("url,key,reason", [
    (PV, "a_switch_nobody_ruled", "switch_not_ruled"),
    (f"{BASE}/feed/", KEY, "switch_not_for_this_surface"),
    (f"{BASE}/pulse/drafts/", KEY, "address_not_admitted"),
])
def test_the_address_and_key_refusals_touch_nothing(url, key, reason):
    page = Page(url)
    verdict = fire(page, key=key)
    assert verdict["refused"] == reason
    assert page.events == []


def test_missing_readers_refuse_before_contact():
    page = Page()
    assert run(view_switch.apply_and_restore(page, key=KEY, read_view=None,
                                             read_counters=steady()))["refused"] == "no_view_reader_supplied"
    assert run(view_switch.apply_and_restore(page, key=KEY, read_view=reader_for(page),
                                             read_counters=None))["refused"] == "no_counter_reader_supplied"
    assert page.events == []


# ---- refused after a read, nothing pressed -------------------------------------


def test_an_unreadable_counter_presses_nothing():
    async def unreadable():
        return {"headline_viewers": None}
    page = Page()
    assert fire(page, counters=unreadable)["refused"] == "counters_unreadable_before_any_press"
    assert clicks(page) == []


@pytest.mark.parametrize("captions", [("Past 90 days", "Company"),
                                      ("Interesting viewers", "Interesting  Viewers")])
def test_not_exactly_one_pill_presses_nothing(captions):
    page = Page(captions=captions)
    assert fire(page)["refused"] == "pill_not_unique"
    assert clicks(page) == []


# ---- the switch --------------------------------------------------------------


def test_the_switch_applies_reads_restores_and_proves_it():
    page = Page()
    verdict = fire(page)
    assert verdict["permitted"] is True and verdict["restored"] is True
    assert "refused" not in verdict
    assert verdict["applied_view_differs"] is True
    assert verdict["view_applied"]["rows"] == [r for r in ALL_ROWS if r["tag"] == "verified"]
    assert verdict["closed_after_apply"] and verdict["closed_after_restore"]
    assert verdict["path_unchanged"] and not verdict["left_applied"]
    assert clicks(page) == [("pills", 1), ("options", 1), ("buttons", 1),
                            ("pills", 1), ("options", 1), ("buttons", 1)]
    assert page.view()["rows"] == ALL_ROWS


def test_an_absent_option_closes_the_pill_and_selects_nothing():
    page = Page(options=("works at a company you follow",))
    verdict = fire(page)
    assert verdict["refused"] == "option_not_unique"
    assert clicks(page) == [("pills", 1), ("pills", 1)]
    assert page.open_pill is None and page.view()["rows"] == ALL_ROWS


def test_an_option_already_applied_is_refused_and_left_alone():
    page = Page(checked=("verified",))
    verdict = fire(page)
    assert verdict["refused"] == "option_already_applied"
    assert clicks(page) == [("pills", 1), ("pills", 1)]


def test_an_option_that_does_not_select_is_undone_and_nothing_applied():
    page = Page(sticky_option=True)
    verdict = fire(page)
    assert verdict["refused"] == "option_did_not_select"
    assert page.open_pill is None and page.view()["rows"] == ALL_ROWS


def test_no_apply_control_deselects_and_closes():
    page = Page(no_apply=True)
    verdict = fire(page)
    assert verdict["refused"] == "apply_control_not_unique"
    assert page.open_pill is None and page.view()["rows"] == ALL_ROWS
    assert page.checked["verified"] is False


def test_a_restore_that_cannot_find_the_option_says_it_left_the_filter_applied():
    page = Page(no_options_on_reopen=True)
    verdict = fire(page)
    assert verdict["refused"] == "switch_left_applied"
    assert verdict["left_applied"] is True and verdict["permitted"] is False
    assert page.open_pill is None, "the popover was left open"


def test_a_view_that_does_not_come_back_is_not_restored():
    page = Page(sticky_server=True)
    verdict = fire(page)
    assert verdict["refused"] == "switch_not_restored"
    assert verdict["restored"] is False and verdict["left_applied"] is False


def test_a_moving_counter_refuses_even_a_restored_view():
    page = Page()
    verdict = fire(page, counters=moving())
    assert verdict["refused"] == "switch_moved_a_counter"
    assert verdict["restored"] is True and verdict["permitted"] is False


def test_a_raising_click_names_its_stage_and_whether_it_left_the_filter_on():
    page = Page(raise_on_click_number=4)
    verdict = fire(page)
    assert verdict["refused"] == "press_failed"
    assert "reopening" in verdict["why"] and "synthetic" not in verdict["why"]
    assert verdict["left_applied"] is True and verdict["pressed"] is True


def test_the_one_click_is_reached_only_from_apply_and_restore():
    """``_activate`` holds the module's only click, and the sanctioned entry is
    keyed to it; a second caller would be a second press path under one entry."""
    tree = ast.parse(pathlib.Path(view_switch.__file__).read_text(encoding="utf-8"))
    callers = set()
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for node in ast.walk(fn):
                if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "_activate":
                    callers.add(fn.name)
    assert callers == {"apply_and_restore"}, callers
    clicks_in_source = [n for n in ast.walk(tree) if isinstance(n, ast.Attribute) and n.attr == "click"]
    assert len(clicks_in_source) == 1


def test_escape_is_never_used():
    """The measured failure: a popover holding an input stayed open after
    Escape. This module closes by 'show results' or by the pill's toggle, and
    the code -- not the docstring, which names Escape to explain its absence --
    holds no keyboard at all."""
    tree = ast.parse(pathlib.Path(view_switch.__file__).read_text(encoding="utf-8"))
    attributes = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert "keyboard" not in attributes
    assert "press" not in attributes


# ---- the refusal inventory ---------------------------------------------------

WHEN_KNOWABLE: dict[str, str] = {
    "switch_not_ruled": "before_any_contact",
    "switch_entry_incomplete": "before_any_contact",
    "switch_not_for_this_surface": "before_any_contact",
    "no_view_reader_supplied": "before_any_contact",
    "no_counter_reader_supplied": "before_any_contact",
    "counters_unreadable_before_any_press": "after_a_read",
    "pill_not_unique": "after_a_read",
    "option_not_unique": "after_the_press",
    "option_already_applied": "after_the_press",
    "option_did_not_select": "after_the_press",
    "apply_control_not_unique": "after_the_press",
    "press_failed": "after_the_press",
    "switch_left_applied": "after_the_press",
    "switch_not_restored": "after_the_press",
    "switch_moved_a_counter": "after_the_press",
}


def _reasons_in_source():
    tree = ast.parse(pathlib.Path(view_switch.__file__).read_text(encoding="utf-8"))
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name == "_refuse" and node.args:
                assert isinstance(node.args[0], ast.Constant)
                found.add(node.args[0].value)
    return found


def test_the_inventory_is_exactly_what_the_module_can_emit():
    assert _reasons_in_source() == set(WHEN_KNOWABLE)


REACHES = {
    "switch_not_ruled": {"key": "nobody_ruled_this"},
    "switch_not_for_this_surface": {"url": f"{BASE}/feed/"},
    "counters_unreadable_before_any_press": {"counters": "unreadable"},
    "pill_not_unique": {"captions": ("Company",)},
    "option_not_unique": {"options": ("verified", "verified")},
    "option_already_applied": {"checked": ("verified",)},
    "option_did_not_select": {"sticky_option": True},
    "apply_control_not_unique": {"no_apply": True},
    "press_failed": {"raise_on_click_number": 2},
    "switch_left_applied": {"no_options_on_reopen": True},
    "switch_not_restored": {"sticky_server": True},
    "switch_moved_a_counter": {"counters": "moving"},
}
_NEEDS_OTHER_INPUT = {"switch_entry_incomplete", "no_view_reader_supplied", "no_counter_reader_supplied"}


@pytest.mark.parametrize("reason", sorted(REACHES))
def test_every_reason_is_reached_when_it_says(reason):
    spec = dict(REACHES[reason])
    key = spec.pop("key", KEY)
    counters = {"unreadable": None, "moving": moving()}.get(spec.pop("counters", None))
    if REACHES[reason].get("counters") == "unreadable":
        async def counters():
            return {"headline_viewers": None}
    page = Page(spec.pop("url", PV), **spec)
    verdict = fire(page, key=key, counters=counters)
    assert verdict.get("refused") == reason
    when = WHEN_KNOWABLE[reason]
    if when == "before_any_contact":
        assert page.events == []
    elif when == "after_a_read":
        assert clicks(page) == []
    else:
        assert clicks(page)


def test_the_incomplete_entry_is_refused_by_a_plant(monkeypatch):
    monkeypatch.setattr(view_switch, "VIEW_SWITCHES", ((KEY, {"surfaces": ("/analytics/profile-views/",)}),))
    page = Page()
    assert fire(page)["refused"] == "switch_entry_incomplete"
    assert page.events == []


def test_every_classified_reason_is_driven():
    assert set(REACHES) | _NEEDS_OTHER_INPUT == set(WHEN_KNOWABLE)
