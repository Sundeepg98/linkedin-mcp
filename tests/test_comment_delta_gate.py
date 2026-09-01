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
