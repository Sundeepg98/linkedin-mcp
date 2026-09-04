"""The submit is identified by ARRIVAL, or it is not pressed.

WHY THIS GATE EXISTS AT ALL. On an item permalink the control that POSTS a
comment does not exist until the box has content, and the control that is
already there is named ``Comment`` -- the same name the feed draws seven times
as the affordance that FOCUSES the box. Measured on an empty permalink:

    shape "Comment"   tag button   name_source text   disabled: FALSE   count 1

So "present, visible and enabled, named Comment" is satisfied BEFORE anything
is typed. A gate keyed on that presses the focus affordance and returns
something indistinguishable from success, which is worse than refusing.

THE ASYMMETRY THAT MAKES THIS SURFACE DIFFERENT, and it is one measured
boolean wide:

    /preload/sharebox/     `Post`      DISABLED while empty   -> a transition
    /messaging/compose/    `Send`      DISABLED while empty   -> a transition
    /feed/update/<urn>/    `Comment`   ENABLED  while empty   -> NOTHING

``publish_post`` can gate on the transition. This one has none to observe, so
it identifies the submit by the only property that actually distinguishes it:
**it did not exist until there was something to submit.**

AND IT IS EXPECTED TO REFUSE. Nobody has measured the submit's accessible
name, because measuring it requires the fill and the fill is the act the gate
authorises. If the new control wears ``Comment`` too -- which his own
screenshot suggests -- two controls share a name, only position separates
them, and the gate stops and REPORTS. That report is the measurement.

These tests drive the real gate against constructed readings. They do not
need a browser: the gate's whole input is a name census before and a name
census after.
"""

import pytest

from linkedin_server import dom, writes


class _Reading:
    """A stand-in for ``dom.read_comment_surface``, returning a fixed census.

    Not a mock of the page -- a mock of the READER, because the property under
    test is what the gate concludes from a before/after pair of name counts,
    and putting a fake DOM in between would test the reader instead.
    """

    def __init__(self, names, editors=1, error=None):
        self.payload = {
            "editors": editors,
            "names": dict(names),
            "controls_read": sum(names.values()),
            "error": error,
        }

    async def __call__(self, page):
        return self.payload


#: The empty permalink as MEASURED on 2026-09-01, trimmed to the rows that
#: matter here. `Comment` at 1 is the affordance, and it is the row that makes
#: a name-and-enabled gate unusable on this surface.
BEFORE = {
    "Comment": 1,
    "Reply": 4,
    "Most relevant": 1,
    "Reaction button state: no reaction": 1,
    "33 reactions 33": 1,
}


async def _gate(monkeypatch, after, editors=1, error=None):
    monkeypatch.setattr(
        dom, "read_comment_surface", _Reading(after, editors=editors, error=error)
    )
    return await writes._comment_submit_gate(object(), dict(BEFORE))


async def test_a_genuinely_new_name_is_aimed_at(monkeypatch):
    """THE PASSING CASE, and this file is worthless without one.

    A gate that refused every input would satisfy every other test here while
    making the action permanently dead -- a failure nobody reports, because a
    write that never works looks like a write nobody used.
    """
    after = dict(BEFORE)
    after["Submit comment"] = 1
    result = await _gate(monkeypatch, after)
    assert result["proceed"] is True, result["why"]
    assert result["arrived"] == ["Submit comment"]
    assert result["selector"] == dom.comment_submit_selector("Submit comment")


async def test_a_shared_name_refuses_and_reports_what_it_saw(monkeypatch):
    """THE CASE HIS SCREENSHOT PREDICTS, and the one that must not click.

    ``Comment`` goes 1 -> 2. Something arrived, and it is indistinguishable
    from the affordance already there by every property this package permits
    itself to use. The gate stops -- and the report is the point, because
    ``grew`` naming ``Comment`` is the measurement that could not be taken any
    other way.
    """
    after = dict(BEFORE)
    after["Comment"] = 2
    result = await _gate(monkeypatch, after)
    assert result["proceed"] is False
    assert result["refused_condition"] == "2_nothing_arrived"
    assert result["grew"] == ["Comment"]
    assert result["arrived"] == []
    assert "only position separates them" in result["why"]
    assert "THIS IS THE MEASUREMENT" in result["why"]


async def test_nothing_new_refuses(monkeypatch):
    """A fill that changed nothing must not be read as a comment ready to post."""
    result = await _gate(monkeypatch, dict(BEFORE))
    assert result["proceed"] is False
    assert result["refused_condition"] == "2_nothing_arrived"
    assert result["arrived"] == []


async def test_several_new_names_refuse(monkeypatch):
    """Two candidates is a refusal, not a shortlist.

    Choosing between them is choosing by position, which is the thing that
    would send a comment to whatever rendered first.
    """
    after = dict(BEFORE)
    after["Submit comment"] = 1
    after["Cancel"] = 1
    result = await _gate(monkeypatch, after)
    assert result["proceed"] is False
    assert result["refused_condition"] == "3_several_arrived"
    assert result["arrived"] == ["Cancel", "Submit comment"]


async def test_a_name_carrying_an_identity_refuses_rather_than_being_pressed(
    monkeypatch,
):
    """THE THIRD-PARTY GUARD, and it is the reason the census is SHAPED.

    LinkedIn writes other members' names into labels on this surface --
    ``View more options for <member>'s comment.`` is measured on it. A shaped
    name carrying a substitution cannot build a selector, and that refusal is
    the CORRECT outcome: a control this server cannot name without naming a
    person is one it does not press.
    """
    after = dict(BEFORE)
    after["Reply to <member>"] = 1
    result = await _gate(monkeypatch, after)
    assert result["proceed"] is False
    assert result["refused_condition"] == "4_name_not_selector_safe"
    assert result["selector"] == ""


async def test_a_missing_editor_refuses_rather_than_reading_the_page_as_ready(
    monkeypatch,
):
    """Zero editors is a page that changed under the gate, not a comment box.

    The same rule the reaction verification uses: an absent control is UNKNOWN
    and never an outcome.
    """
    after = dict(BEFORE)
    after["Submit comment"] = 1
    result = await _gate(monkeypatch, after, editors=0)
    assert result["proceed"] is False
    assert result["refused_condition"] == "1_editor_absent"


async def test_a_failed_read_refuses(monkeypatch):
    """A reader that raised knows nothing, which is not the same as 'not ready'."""
    result = await _gate(monkeypatch, dict(BEFORE), error="TimeoutError: x")
    assert result["proceed"] is False
    assert result["refused_condition"] == "0_read_failed"


def test_the_two_surfaces_are_gated_by_different_instruments():
    """The asymmetry, asserted so the two gates cannot be swapped.

    ``publish_post`` gates on a state transition and ``comment_on_item`` on
    arrival, because one submit is drawn-and-disabled while empty and the
    other does not exist. Using either instrument on the other's surface would
    press the wrong control, so the sets are kept apart and checked.
    """
    assert "comment_on_item" in writes.DELTA_SUBMIT_ACTIONS
    assert "publish_post" not in writes.DELTA_SUBMIT_ACTIONS
    # Every delta action must also be a typing action: the delta is only
    # meaningful across a fill.
    assert writes.DELTA_SUBMIT_ACTIONS <= writes.TYPING_ACTIONS


@pytest.mark.parametrize(
    "unsafe", ["<member>", 'a"b', "x[y]", "", "   ", "line\\nbreak"]
)
def test_the_submit_selector_refuses_anything_that_could_end_its_quoting(unsafe):
    """The builder is the last thing between a page-derived name and a click."""
    with pytest.raises(Exception):
        dom.comment_submit_selector(unsafe)


# ---------------------------------------------------------------------------
# The two defects found 2026-09-04, both driven through the REAL reader
# ---------------------------------------------------------------------------
#
# EVERY TEST ABOVE THIS LINE REPLACES ``dom.read_comment_surface`` WITH
# ``_Reading``, a fixed stand-in, and that is exactly what let ``names`` ship
# permanently empty: the loop inside the real function summed a census key
# (``control_shapes``) that ``read_surface_census`` has never returned,
# against a field (``count``) no control row carries either, and nothing in
# this file's suite ever ran that body to notice. The tests below drive the
# real function -- and the real gate on top of it -- against a raw census
# payload SHAPED THE WAY ``CENSUS_JS`` ACTUALLY SHAPES ONE, through a page
# fake that answers ``.locator(...).count()`` and ``.evaluate(...)`` rather
# than a reader stand-in.


class _CommentCensusPage:
    """A page whose ``evaluate`` returns a raw census payload and whose
    ``locator`` reports a fixed editor count -- the shape ``CENSUS_JS``
    itself hands back, before ``read_surface_census`` shapes it. Driving
    ``dom.read_comment_surface`` against this exercises the REAL function,
    unlike ``_Reading`` above which replaces it outright.
    """

    def __init__(self, controls, *, editors=1, counts=None):
        self._editors = editors
        self._payload = {
            "counts": {
                "forms": 0,
                "buttons": 0,
                "links": 0,
                "contenteditable": 1,
                "file_inputs": 0,
                "dialogs": 0,
                "menus": 0,
                "menu_items": 0,
                **(counts or {}),
            },
            "controls": controls,
            "truncated": False,
        }

    def locator(self, _selector):
        editors = self._editors

        class _Locator:
            async def count(self) -> int:
                return editors

        return _Locator()

    async def evaluate(self, _script, _cfg=None):
        return dict(self._payload)


async def test_the_real_reader_harvests_names_off_a_census_payload():
    """DEFECT 1, ITSELF. FAILS ON THE UNPATCHED CODE with ``names == {}``.

    The unpatched loop read ``census.get("control_shapes", [])`` where
    ``read_surface_census`` returns exactly ``counts``, ``controls``,
    ``controls_read`` and ``truncated`` -- no ``control_shapes`` key has ever
    existed at that layer -- so it iterated ``[]`` on every call regardless
    of what the page carried. Three named, distinct controls go in; the fixed
    reader must come back with all three counted once each.
    """
    controls = [
        {"tag": "button", "name": "Comment", "href": None},
        {"tag": "button", "name": "Reply", "href": None},
        {"tag": "button", "name": "Submit comment", "href": None},
    ]
    page = _CommentCensusPage(controls)
    result = await dom.read_comment_surface(page)
    assert result["names"] == {"Comment": 1, "Reply": 1, "Submit comment": 1}
    assert result["controls_read"] == 3
    assert result["unnamed"] == 0


async def test_an_unnamed_control_is_counted_rather_than_dropped_silently():
    """The companion half of the same fix: an empty shape still cannot become
    a selector, so it still does not enter ``names`` -- but it must not
    vanish without a trace either, or a page that changed under the gate
    reads identically to a page that truly held still."""
    controls = [
        {"tag": "button", "name": "Comment", "href": None},
        {"tag": "button", "name": "", "href": None},
    ]
    page = _CommentCensusPage(controls)
    result = await dom.read_comment_surface(page)
    assert result["names"] == {"Comment": 1}
    assert result["unnamed"] == 1
    assert result["controls_read"] == 2


async def test_menus_and_menu_items_reach_the_real_readers_return():
    """DEFECT 2's PLUMBING. FAILS ON THE UNPATCHED CODE: the keys are absent
    from ``read_comment_surface``'s return entirely, because neither
    ``CENSUS_JS``'s ``counts`` block nor its Python mirror in
    ``read_surface_census`` carried a menu count of any kind before this fix.
    """
    controls = [{"tag": "button", "name": "Comment", "href": None}]
    page = _CommentCensusPage(controls, counts={"menus": 1, "menu_items": 3})
    result = await dom.read_comment_surface(page)
    assert result["menus"] == 1
    assert result["menu_items"] == 3


async def test_the_gate_names_menu_items_when_nothing_arrived_and_a_menu_is_open():
    """DEFECT 2's CONSEQUENCE, at the gate. FAILS ON THE UNPATCHED GATE: with
    no menu branch, this reading refuses the ordinary ``2_nothing_arrived``
    and reports the absence as clean, which is exactly the claim this reader
    cannot back up when the page carries menu items its census cannot name.

    MEASURED 2026-09-04: opening a comment's own overflow menu draws three
    ``[role="menuitem"]`` nodes (``Copy link to comment``, ``Edit``,
    ``Delete``). Driven through the REAL ``dom.read_comment_surface`` via
    ``_CommentCensusPage``, exactly like the two tests above -- a
    monkeypatched reader would prove nothing about whether the gate actually
    consults what that function now reports.
    """
    before = {"Comment": 1}
    controls = [{"tag": "button", "name": "Comment", "href": None}]
    page = _CommentCensusPage(controls, counts={"menus": 1, "menu_items": 3})
    result = await writes._comment_submit_gate(page, dict(before))
    assert result["proceed"] is False
    assert result["refused_condition"] == "2b_menu_items_present"
    assert result["arrived"] == []
    assert "3 menu item" in result["why"]
    assert "does not enumerate" in result["why"]
    assert "UNKNOWN" in result["why"]


async def test_the_gate_still_reports_the_ordinary_absence_with_no_menu_open():
    """THE CONTROL for the test above: the same empty ``arrived`` list, with
    ``menu_items`` at zero, must still take the ordinary branch. Otherwise
    the new branch would not be adding a case, it would be replacing one."""
    before = {"Comment": 1}
    controls = [{"tag": "button", "name": "Comment", "href": None}]
    page = _CommentCensusPage(controls, counts={"menus": 0, "menu_items": 0})
    result = await writes._comment_submit_gate(page, dict(before))
    assert result["proceed"] is False
    assert result["refused_condition"] == "2_nothing_arrived"
