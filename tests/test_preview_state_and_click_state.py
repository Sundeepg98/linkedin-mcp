"""One field, read at both ends of a write -- pinned, because nobody ruled it.

``WriteSpec.from_state`` is compared against a live reading TWICE, at opposite
ends of a write, and the two readings are not taken off the same thing:

  PREVIEW TIME   ``writes._direction`` compares ``observation.state`` -- what
                 the preview's live read returned, off whichever surface the
                 spec's ``state_from`` names -- against ``spec.from_state``,
                 and raises a wrong-state refusal when they differ.

  CLICK TIME     ``writes.valid_from``, called from ``writes.perform``'s gate
                 5, compares what ``writes._live_control`` returned -- read off
                 THE VERY CONTROL the click will land on, after the write url
                 has been loaded -- against the SAME ``spec.from_state``.

Those are potentially two different surfaces, read minutes apart, compared
against ONE string. For every action shipped today they agree. NOTHING
ANYWHERE REQUIRES THAT. No test asserted it before this file, no comment ruled
it, and the specs carry one field where the design has two questions.

WHY THAT IS WORTH A FILE. This repo has already paid for exactly this shape.
Nine sites assumed that url-presence and performability coincide; nothing had
ruled it; addressing ONE action for a read broke all nine at once. The rule
that came out of it lives in ``tests/test_addressing_is_not_permission.py``,
and it is the reason this file exists: WHEN AN INVARIANT HOLDS, ASK WHETHER
ANYONE RULED IT. IF NOT, IT IS A COINCIDENCE, AND SOMETHING ALREADY DEPENDS ON
IT.

WHAT WAS MEASURED WHILE BUILDING THIS, 2026-09-02, and every number below is a
count off the live objects rather than an estimate:

  11    actions in ``writes.PERFORMABLE``
  10    of them reached, ON THE DAY THIS FILE WAS WRITTEN, through
        ``_live_control``'s SUCCESS path -- the path that also hands back a
        non-empty selector -- over fixtures that already existed in this suite
   1    that could not be reached, ``update_profile_field``, and NOT for want
        of a fixture: its success path was unreachable IN THE SHIPPED CODE,
        because ``dom.read_self_owned_editor_fields`` dropped the ``dom_id``
        its own script produced and the arm aimed from exactly that key
  11    sites in ``linkedin_server/writes.py`` that READ ``.from_state``,
        counted off the AST
   5    functions those sites sit in -- not two. See part 3.

**THE ELEVENTH WAS REPAIRED THE SAME DAY AND THIS FILE NOW REACHES 11 OF 11.**
``CANNOT_REACH`` is empty and kept, because an empty table asserts that nothing
is currently unreachable where a deleted one asserts nothing at all. The
measurement above is left standing rather than rewritten: it is what the
instrument found, and finding it is why the defect was fixed.

THE THREE PARTS.

  PART 1  For every action in ``PERFORMABLE``, drive ``_live_control`` to its
          success path and assert the state it returns is the state the spec
          says the action is valid FROM. For the one multi-state action the
          invariant has a DIFFERENT SHAPE and is asserted differently rather
          than collapsed -- see
          ``test_update_setting_is_checked_against_its_enumeration_instead``.

  PART 2  The check, SHOWN FAILING. A spec's ``from_state`` is mutated so it
          no longer matches what ``_live_control`` reads, on three arms of
          ``_live_control`` that work differently from one another, and the
          part 1 check -- the same function, not a copy of it -- is asserted
          to fire.

  PART 3  Every reader of ``.from_state``, found by AST, pinned by count and
          by enclosing function name. The point is that a future edit adding
          a consumer of this one field fails HERE and has to say what it
          means, rather than inheriting a meaning nobody ever wrote down.

NOTHING HERE REACHES LINKEDIN OR AN ACCOUNT. Every page is frozen markup that
already exists in this suite, served into a local headless Chromium by
``tests/test_apply_modal_fixture.py``'s ``over`` fixture -- one browser, a
FRESH ISOLATED CONTEXT per reading, and ``window.innerWidth`` asserted on every
measurement so no answer is taken at an unrecorded width.

NO FIXTURE MARKUP IS INVENTED IN THIS FILE, deliberately. Inventing a page for
an action that has none would manufacture the coverage this file exists to
count. Every document below is imported from the module that already committed
it, and the source is named in ``REACHED`` so a reader can see at a glance how
wide the instrument really reaches.
"""

from __future__ import annotations

import ast
import dataclasses
from pathlib import Path

import pytest

from linkedin_server import dom, writes
from linkedin_server.writes import (
    PERFORMABLE,
    SANCTIONED_WRITES,
    TARGET_JOIN,
    spec_for_action,
)

# THE HARNESS, from the file that already owns it. ``over`` gives one browser
# per test and a fresh isolated context per READING, with innerWidth asserted
# on each -- which is the standard this package holds every measurement to.
from tests.test_apply_modal_fixture import VIEWPORT, over  # noqa: F401
from tests.test_editor_fields import TWO_DIALOG_HTML
from tests.test_result_verification_block import SHAREBOX_MARKUP
from tests.test_selectors_resolve import PAGE as SELECTOR_RESOLUTION_PAGE
from tests.test_writes import (  # noqa: F401 -- two of these are fixtures
    FOLLOWED_COMPANY,
    JOB,
    SAVED_JOB,
    SAVED_POSTING,
    _bare_grant,
    markup,
    writes_on,
)
from tests.test_writes_nine import (
    DARK_MODE_MARKUP,
    FEED_MARKUP,
    PROFILE_MARKUP,
    TARGETS,
)

WRITES_PY = Path(writes.__file__)

#: The two frozen captures this file serves, read once at import rather than
#: per case. Both are real LinkedIn renders committed in ``tests/fixtures/``.
POSTING = markup("job_detail")
FOLLOWED_PAGES = markup("manage_pages_following_hydrated")

#: THE FIELD DRIVEN INTO THE PROFILE EDITOR, and it is ``City`` rather than
#: ``headline`` on purpose. ``headline`` is refused one branch earlier -- it is
#: named by its own content, so the reader will not aim at it at all -- and a
#: refusal from THAT branch would leave the branch this file is about untouched
#: while looking like it had been reached. ``City`` is a control the live
#: editor draws (``linkedin_server/dom.py`` records it among the names two
#: agreeing 256-control readings found) and it is one of the controls
#: ``TWO_DIALOG_HTML`` draws with an id on it, so it walks the arm all the way
#: to its last check.
EDITOR_FIELD_TARGET = "City" + TARGET_JOIN + "Springfield"


def _canonical(action: str):
    """The target spelling a real grant for ``action`` would carry.

    Taken through ``writes._target_for`` rather than typed, because three arms
    of ``_live_control`` -- unfollow, invitation, setting -- READ
    ``grant.target``, and a loosely typed one would be handing those readers a
    shape no grant can hold.
    """
    return str(writes._target_for(spec_for_action(action), TARGETS[action]))


# ---------------------------------------------------------------------------
# What this instrument reaches, and what it does not
# ---------------------------------------------------------------------------


#: action -> (where the markup comes from, the markup, the grant target).
#:
#: EVERY DOCUMENT IS IMPORTED, NEVER WRITTEN HERE. The source string is not
#: decoration: it is what makes the reach of this instrument readable without
#: tracing imports, and ``test_the_reachable_table_names_a_real_source`` checks
#: each one really is a file that exists.
REACHED: dict[str, tuple[str, str, str]] = {
    "save_job": ("tests/fixtures/job_detail.html", POSTING, JOB),
    # DERIVED in tests/test_writes.py, and labelled as such there: no capture
    # in this repo shows a SAVED posting, because every one predates the
    # operator's first save on 2026-08-30.
    "unsave_job": ("tests/test_writes.py", SAVED_POSTING, SAVED_JOB),
    "follow_company": ("tests/fixtures/job_detail.html", POSTING, JOB),
    "unfollow_company": (
        "tests/fixtures/manage_pages_following_hydrated.html",
        FOLLOWED_PAGES,
        FOLLOWED_COMPANY,
    ),
    "apply_job": ("tests/fixtures/job_detail.html", POSTING, JOB),
    "react_to_item": (
        "tests/test_writes_nine.py",
        FEED_MARKUP,
        _canonical("react_to_item"),
    ),
    "send_invitation": (
        "tests/test_writes_nine.py",
        PROFILE_MARKUP,
        _canonical("send_invitation"),
    ),
    "update_setting": (
        "tests/test_writes_nine.py",
        DARK_MODE_MARKUP,
        _canonical("update_setting"),
    ),
    # THE TWO THAT COME FROM OUTSIDE THE WRITE SUITE, and both are reused
    # rather than rebuilt for the reason stated in the module docstring.
    # ``PAGE`` carries one control for every selector builder in ``dom``,
    # which happens to be exactly the shape ``dom.read_comment_surface``
    # requires: exactly one editor named ``dom.COMMENT_EDITOR_LABEL``.
    "comment_on_item": (
        "tests/test_selectors_resolve.py",
        SELECTOR_RESOLUTION_PAGE,
        _canonical("comment_on_item"),
    ),
    # The sharebox, with its submit DISABLED on an empty composer -- which is
    # the state ``_live_control`` requires before it will type anything, and
    # the reason no other page in this suite reaches publish_post's success
    # path. ``tests/test_selectors_resolve.py``'s PAGE draws an ENABLED one and
    # is refused: MEASURED, "the publish control is already ENABLED before
    # anything was typed".
    "publish_post": (
        "tests/test_result_verification_block.py",
        SHAREBOX_MARKUP,
        _canonical("publish_post"),
    ),
    # THE ELEVENTH, MOVED OUT OF ``CANNOT_REACH`` ON 2026-09-02 when the
    # defect that put it there was repaired. It sat in that table for one
    # commit, which is exactly as long as the table was true.
    "update_profile_field": (
        "tests/test_editor_fields.py",
        TWO_DIALOG_HTML,
        EDITOR_FIELD_TARGET,
    ),
}

#: WHAT THIS INSTRUMENT CANNOT REACH, WITH THE REASON -- AND THE REASON IS NOT
#: "NO FIXTURE".
#:
#: An instrument that quietly covers ten of eleven while LOOKING like it covers
#: eleven is the defect this repo keeps finding, so the gap is a table with a
#: test under it rather than an absence.
#: ``test_the_unreachable_table_is_what_was_measured`` DRIVES the arm and
#: asserts the refusal it names, so this entry is a measurement and goes red
#: the day the measurement changes.
#:
#: THE REASON IS A DEFECT IN THE SHIPPED CODE, found while building this file
#: and MEASURED on 2026-09-02, not a hole in the test suite:
#:
#:   ``dom.EDITOR_FIELDS_JS`` reads each control's ``id`` into ``dom_id`` --
#:   MEASURED returning ``'e-city'`` over ``TWO_DIALOG_HTML``.
#:
#:   ``dom.read_self_owned_editor_fields`` then rebuilds every control into a
#:   ``fields`` entry from a TEN-KEY dict literal, and ``dom_id`` is not one
#:   of the ten -- MEASURED: the keys that arrive are ``checked``,
#:   ``checked_source``, ``disabled``, ``has_href``, ``name``, ``name_source``,
#:   ``required``, ``role``, ``tag``, ``type``.
#:
#:   ``_live_control``'s ``update_profile_field`` arm aims from
#:   ``control.get("dom_id")`` off one of those ``fields`` entries. It is
#:   therefore ALWAYS empty, and the arm always takes its "carries no id"
#:   refusal, which returns NO SELECTOR.
#:
#: So that arm's success path could not be entered by any page at all.
#:
#: **REPAIRED THE SAME DAY, AND THE TABLE IS NOW EMPTY.**
#: ``read_self_owned_editor_fields`` gained ``include_dom_id``, defaulting to
#: ``False`` so the TOOL path still publishes no DOM id, and
#: ``_live_control`` -- the one caller that needs a selector and never prints
#: what it builds one from -- passes ``True``. The arm now returns ``#e-city``
#: over ``TWO_DIALOG_HTML``, and ``update_profile_field`` moved into
#: ``REACHED`` above, so this file covers eleven of eleven.
#:
#: THE TABLE STAYS, EMPTY, RATHER THAN BEING DELETED. It is the shape that
#: makes a future gap countable instead of absent, and
#: ``test_every_performable_action_is_either_reached_or_declared_unreachable``
#: reads it. An empty table asserts something -- that nothing is currently
#: unreachable -- where a deleted one asserts nothing and would have to be
#: reinvented by whoever next finds an arm they cannot drive.
CANNOT_REACH: dict[str, str] = {}

#: The reached actions whose ``from_state`` is a single named state. DERIVED,
#: never typed: the premise this file was handed named ``update_setting`` as
#: the only multi-state action, and a hardcoded list would have been a second
#: place for that to be true rather than a check that it is.
BINARY = tuple(
    sorted(
        action
        for action in REACHED
        if spec_for_action(action).from_state is not None
    )
)

#: The reached actions with no single origin -- ``from_state`` is ``None``, so
#: the invariant has a different shape and is asserted separately.
MULTI_STATE = tuple(
    sorted(
        action for action in REACHED if spec_for_action(action).from_state is None
    )
)


def _tool_name(action: str) -> str:
    """The ``SANCTIONED_WRITES`` key for an action.

    Derived, so part 2's ``monkeypatch.setitem`` cannot be aimed at a key that
    stopped existing -- ``setitem`` on a missing key would install a spec
    nothing reads and every mutation below would silently do nothing.
    """
    names = [
        name for name, spec in SANCTIONED_WRITES.items() if spec.action == action
    ]
    assert len(names) == 1, (action, names)
    return names[0]


async def _live(over, action, *, spec=None, anchor=None):
    """Drive ``_live_control`` for one action. Returns ``(state, why, selector)``.

    THE GRANT IS BUILT DIRECTLY rather than minted, and that is a deliberate
    narrowing rather than a shortcut round the gate. ``_live_control`` reads
    exactly one thing off a grant -- its ``target`` -- and the whole subject of
    this file is the relationship between ONE SPEC FIELD and ONE READER'S
    ANSWER. Driving eleven full preview-mint-consume chains to settle that
    would put a row of unrelated gates between the question and the answer, and
    each of those is already tested where it lives. ``tests/test_writes.py``
    uses ``_bare_grant`` for the same reason and says so.

    ``spec`` and ``anchor`` are overridable because part 2 needs to vary ONE of
    them at a time; see the note on the save family there.
    """
    spec = spec or spec_for_action(action)
    _source, html, target = REACHED[action]
    grant = _bare_grant(action=action, target=target)
    if anchor is None:
        anchor = writes.anchor_label_for(spec, target)

    async def work(page):
        return await writes._live_control(page, spec, grant, anchor or "")

    # A STAR, because one arm returns a fourth element naming its mutation
    # kind. Unpacking three positionally would break the day a second arm has
    # something to say.
    state, why, selector, *_rest = await over(html, work)
    return state, why, selector


def _assert_the_two_ends_agree(spec, state: str, selector: str, why: str) -> None:
    """THE CHECK ITSELF, in one place, so part 2 can fire IT and not a copy.

    A "shown failing" that re-implements the assertion it is demonstrating
    proves only that the copy fires. This is the function part 1 calls and the
    function part 2 wraps in ``pytest.raises``, so what is shown failing is the
    check that ships.

    TWO SHAPES, AND THEY ARE NOT COLLAPSED, for the same reason
    ``writes.valid_from`` does not collapse them: a binary toggle is valid from
    exactly ONE named state, while a multi-state action has ``from_state`` of
    ``None`` and is checked against ``spec.audiences`` -- the enumeration of
    states this server has actually seen LinkedIn render. Comparing a
    multi-state reading against ``None`` is not a strict check, it is a check
    that can never pass; that exact collapse is what made ``update_setting``
    unperformable until 2026-08-31, and it is recorded in ``valid_from``'s own
    docstring.
    """
    assert selector != "", (
        f"{spec.action!r} handed back no selector, so this reading never "
        "reached _live_control's success path and the invariant below was not "
        f"exercised at all. why={why!r}"
    )
    if spec.from_state is not None:
        assert state == spec.from_state, (
            f"{spec.action!r}: the control _live_control read at CLICK time "
            f"reports {state!r}, and the spec says the action is valid only "
            f"from {spec.from_state!r} -- which is the same field "
            "writes._direction compares the PREVIEW's reading against. Those "
            "two ends have now disagreed, and nothing in this package rules "
            "which of them owns the field. why=" + repr(why)
        )
        return
    assert state.strip().casefold() in spec.audiences, (
        f"{spec.action!r} has no single from_state, so writes.valid_from "
        "checks the click-time reading against spec.audiences instead. It "
        f"read {state!r}, which is not in {sorted(spec.audiences)} -- a state "
        "that cannot be named cannot be moved from. why=" + repr(why)
    )


# ---------------------------------------------------------------------------
# Part 0. The instrument declares its own reach before it claims anything
# ---------------------------------------------------------------------------


def test_every_performable_action_is_either_reached_or_declared_unreachable():
    """THE COVERAGE LEDGER, and it is the first test in the file on purpose.

    Everything below asserts something about the actions in ``REACHED``. That
    is worth nothing unless ``REACHED`` is known to be the whole of
    ``PERFORMABLE`` minus a declared, reasoned gap -- otherwise a twelfth
    action could ship tomorrow, be covered by nothing here, and this file would
    stay green while looking like the thing that checks it.

    THE FAILURE THIS PREVENTS HAS A NAME IN THIS REPO. Three parametrised
    checks in ``tests/test_writes_nine.py`` silently stopped running on
    2026-09-01 when their corpus emptied; pytest reported them SKIPPED with
    "got empty parameter set", which in a run of 2361 passing tests reads
    exactly like a pass. A table that is not asserted against the registry is
    the same failure one step earlier.
    """
    covered = set(REACHED) | set(CANNOT_REACH)
    assert covered == set(PERFORMABLE), {
        "in PERFORMABLE and covered by nothing here": sorted(
            set(PERFORMABLE) - covered
        ),
        "claimed here and not performable": sorted(covered - set(PERFORMABLE)),
    }
    assert not (set(REACHED) & set(CANNOT_REACH)), sorted(
        set(REACHED) & set(CANNOT_REACH)
    )
    # THE NUMBERS THIS FILE REPORTS, pinned so the report and the code cannot
    # drift.
    #
    # THEY MOVED ON 2026-09-02, WITHIN A DAY OF BEING WRITTEN, and the reason
    # is the point: they read ELEVEN PERFORMABLE, TEN REACHED, ONE NOT, and
    # that one -- ``update_profile_field`` -- was unreachable because of a
    # DEFECT rather than a missing fixture. The defect was repaired in the same
    # commit that moved these numbers, so the count is now eleven of eleven and
    # ``CANNOT_REACH`` is empty.
    #
    # An empty ``CANNOT_REACH`` still asserts something -- that nothing is
    # currently unreachable -- which is why it is a table and not a deletion.
    assert len(PERFORMABLE) == 11, sorted(PERFORMABLE)
    assert len(REACHED) == 11, sorted(REACHED)
    assert len(CANNOT_REACH) == 0, sorted(CANNOT_REACH)


def test_no_corpus_this_file_fans_out_over_is_empty():
    """A parametrised test over an empty tuple SKIPS, and a skip reads as a pass.

    Both corpora below are DERIVED from ``REACHED`` by asking each spec whether
    ``from_state`` is None, so either could empty without anybody typing
    anything -- which is precisely how the 2026-09-01 gap happened.
    """
    for name, corpus in (("BINARY", BINARY), ("MULTI_STATE", MULTI_STATE)):
        assert corpus, (
            "%s is empty, so every test parametrised over it now SKIPS "
            "instead of running. That is not coverage." % name
        )


def test_exactly_one_performable_action_is_multi_state():
    """The premise the two-shaped check rests on, asserted rather than assumed.

    ``_assert_the_two_ends_agree`` branches on ``from_state is None``. If a
    second multi-state action shipped, the ``audiences`` branch would start
    covering it silently -- and ``audiences`` is a WEAKER check than a named
    origin, so coverage would quietly soften. That should be a decision, so it
    fails here first.
    """
    multi = sorted(
        action
        for action in PERFORMABLE
        if spec_for_action(action).from_state is None
    )
    assert multi == ["update_setting"], multi
    # And its enumeration is not empty, or the audiences branch is vacuous.
    assert spec_for_action("update_setting").audiences


def test_the_reachable_table_names_a_real_source_for_every_document():
    """An entry's ``source`` is a CLAIM, so it is checked like one.

    A stale source string is worse than none: it tells a reader the instrument
    reaches further into the committed fixtures than it does. Each is asserted
    to name a file that exists, and the two frozen captures are asserted to be
    the documents actually being served.
    """
    root = WRITES_PY.parent.parent
    for action, (source, html, _target) in REACHED.items():
        assert (root / source).exists(), (action, source)
        assert html, action
    assert REACHED["save_job"][1] is POSTING
    assert REACHED["unfollow_company"][1] is FOLLOWED_PAGES
    # SAVED_POSTING is job_detail with ONE attribute rewritten. If that
    # derivation ever silently no-ops, save_job and unsave_job would be driven
    # over the same document and asserted to read two different states off it.
    # One of them would fail, but for a reason nobody could read.
    # tests/test_writes.py asserts the derivation at import; this asserts the
    # consequence this file depends on.
    assert SAVED_POSTING != POSTING


# ---------------------------------------------------------------------------
# Part 1. The invariant, for every performable action
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("action", BINARY)
async def test_the_preview_state_and_the_click_state_are_the_same_string(
    writes_on, over, action
):
    """THE UNRULED INVARIANT, pinned for one action per case.

    ``writes._direction`` compares the PREVIEW's reading against
    ``spec.from_state``. ``writes.valid_from``, from gate 5, compares
    ``_live_control``'s CLICK-TIME reading against the same field. This asserts
    the second half: the state ``_live_control`` returns on the path that also
    yields a selector IS ``spec.from_state``.

    WHY THE SELECTOR IS ASSERTED FIRST. Several arms return a state that
    happens to equal ``from_state`` while REFUSING -- ``update_profile_field``
    returns ``editor_addressed`` from four different places, only one of which
    is a success -- so a check that looked only at the state would pass on a
    refusal and certify nothing. The non-empty selector is what makes this the
    SUCCESS path rather than a coincidence about a string.

    THE ARMS ARE NOT ONE MECHANISM, which is the whole reason this is
    parametrised over the registry rather than written once. ``save_job`` and
    ``unsave_job`` fall through to a shared save-family reader and take their
    state from ``shape.save_state``; ``follow_company`` reads its own control
    and compares against ``spec.from_state`` INSIDE the arm; ``apply_job``
    classifies a route; ``react_to_item``, ``send_invitation``,
    ``comment_on_item`` and ``publish_post`` each return a CONSTANT written
    into the function body, which their readers never compare against the spec
    at all. Four ways of arriving at one string, and nothing makes them arrive
    at the same one.
    """
    spec = spec_for_action(action)
    state, why, selector = await _live(over, action)
    _assert_the_two_ends_agree(spec, state, selector, why)


async def test_update_setting_is_checked_against_its_enumeration_instead(
    writes_on, over
):
    """THE OTHER SHAPE, asserted as a different thing rather than folded in.

    ``update_setting`` is a MULTI-STATE action: dark mode has three states and
    there is no single origin, so its ``from_state`` is ``None``. Asserting
    ``state == spec.from_state`` here would be asserting ``state is None``,
    which no real reading can satisfy -- a check that cannot pass rather than a
    strict one.

    WHY THE TWO ARE NOT COLLAPSED INTO ONE ASSERTION. That exact collapse
    already shipped once. ``perform``'s gate 5 read ``live_state !=
    spec.from_state`` directly, which refused EVERY reading a multi-state
    action could ever take, and it stayed invisible for as long as no such
    action was performable. ``writes.valid_from`` exists to hold the two shapes
    apart and says so in its own docstring. A test that flattened them would be
    asserting that a distinction the shipped code makes does not matter.

    So what is checked here is what ``valid_from`` checks: the click-time
    reading is a member of ``spec.audiences``, the closed set of states this
    server has actually seen LinkedIn render. ``audiences`` is casefolded, so
    the comparison is too -- ``valid_from`` casefolds, and a test comparing raw
    would pass or fail on a detail the gate does not care about.
    """
    spec = spec_for_action("update_setting")
    assert spec.from_state is None
    state, why, selector = await _live(over, "update_setting")

    _assert_the_two_ends_agree(spec, state, selector, why)

    # And the same reading, put through the SHIPPED gate rather than through
    # this file's copy of the question. Without this, the assertion above could
    # drift away from what gate 5 actually asks.
    _source, _html, target = REACHED["update_setting"]
    ok, refusal = writes.valid_from(spec, state, target)
    assert ok, refusal
    # MEASURED, and named so a fixture that stopped drawing what it draws fails
    # here rather than passing on some other state.
    assert state == "Always off", state


async def test_the_editor_id_reaches_the_aimer_and_never_the_tool(writes_on, over):
    """THE REPAIRED BLOCKER, AND ITS PRIVACY PROPERTY, ASSERTED TOGETHER.

    THIS TEST REPLACED ``test_the_unreachable_table_is_what_was_measured`` on
    2026-09-02, which is the day the defect it pinned was repaired. That test
    drove ``_live_control``'s ``update_profile_field`` arm and asserted the arm
    returned NO SELECTOR, because ``dom.read_self_owned_editor_fields``
    rebuilt every control into a ten-key dict that dropped the ``dom_id`` its
    own script produced. The arm's success path could not be entered by any
    page at all -- which is why the eleventh capability shipped unable to act.

    **IT WENT RED THE INSTANT THE FIX LANDED**, naming the selector it had just
    started returning and telling the fixer to move the row into ``REACHED``.
    That is a known defect recorded in a form that FAILS when the defect is
    fixed, and it worked: the repair could not land quietly.

    WHAT IS ASSERTED NOW IS THE SHAPE OF THE FIX, and both halves matter
    because either alone would be a different design:

      the AIMER gets the id       -- ``_live_control`` passes
                                     ``include_dom_id=True`` and builds a real
                                     selector. Without this the capability is
                                     back where it started.
      the TOOL never does         -- the default projection still has no
                                     ``dom_id`` key, so
                                     ``server.linkedin_profile_editor_fields``
                                     cannot publish one.

    WHY THAT SPLIT RATHER THAN A SUBSTITUTION. This projection is a PRIVACY
    BOUNDARY -- rebuilding each control into a fixed key set is what makes it
    one. A DOM id is not identity IN THE IDS THAT HAVE BEEN SEEN (``e-city``),
    which is not the same statement as "is not identity"; LinkedIn also writes
    ids of the form ``ember-view-urn:li:fsd_profile:<id>``. Publishing the id
    and then shaping it would make the substitution's correctness load-bearing.
    Not publishing it means NO SUBSTITUTION HAS TO BE CORRECT -- the exposure
    is removed rather than guarded, and a guard is one edit from being an
    absent guard.

    The arm still REFUSES rather than sanitising an id that looks like
    identity or would break the selector's quoting; that pair is asserted in
    ``tests/test_a_performable_action_can_reach_its_control.py``, beside the
    rest of the reachability chain.
    """
    spec = spec_for_action("update_profile_field")
    grant = _bare_grant(action="update_profile_field", target=EDITOR_FIELD_TARGET)

    async def work(page):
        return await writes._live_control(page, spec, grant, "")

    state, why, selector, *_rest = await over(TWO_DIALOG_HTML, work)

    assert state == spec.from_state == "editor_addressed", (state, why)
    # THE AIMER GETS A REAL SELECTOR, built from the id the reader used to
    # drop. ``e-city`` is the id the fixture draws and the script was always
    # producing; what changed is that it now survives the rebuild.
    assert selector == "#e-city", (selector, why)
    assert "carries no id" not in why, why

    # AND THE TOOL PATH STILL SEES NO ID AT ALL. Default arguments, which is
    # what ``server.linkedin_profile_editor_fields`` calls with.
    async def read_default(page):
        return await dom.read_self_owned_editor_fields(page)

    reading = await over(TWO_DIALOG_HTML, read_default)
    fields = list(reading.get("fields") or [])
    assert fields, reading
    assert all("dom_id" not in field for field in fields), [
        sorted(field) for field in fields
    ]

    # ... and the flag is what makes the difference, rather than some other
    # change having quietly made the id available everywhere.
    async def read_flagged(page):
        return await dom.read_self_owned_editor_fields(page, include_dom_id=True)

    flagged = list((await over(TWO_DIALOG_HTML, read_flagged)).get("fields") or [])
    assert flagged, "the flagged read returned no fields"
    assert any(field.get("dom_id") for field in flagged), [
        sorted(field) for field in flagged
    ]


def test_only_the_write_path_asks_for_the_editor_id(writes_on):
    """ONE CALLER PASSES THE FLAG, read off the source rather than promised.

    The whole privacy argument for ``include_dom_id`` is that the tool path
    never passes it. That is a claim about CALL SITES, so it is checked as one:
    a second ``include_dom_id=True`` anywhere in the package fails here and has
    to argue for itself, exactly as a second ``page.fill`` would.

    Read off the AST rather than by substring, because ``include_dom_id=True``
    inside a comment or a docstring is not a call and should not count -- and a
    substring check would have counted the paragraph above.
    """
    import ast
    import pathlib as _pathlib

    package = _pathlib.Path(writes.__file__).parent
    sites = []
    for path in sorted(package.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            for keyword in node.keywords:
                if keyword.arg != "include_dom_id":
                    continue
                value = keyword.value
                if isinstance(value, ast.Constant) and value.value is True:
                    sites.append((path.name, node.lineno))

    assert sites == [("writes.py", sites[0][1] if sites else 0)], sites


# ---------------------------------------------------------------------------
# Part 2. The check, SHOWN FAILING -- three arms, three mechanisms
# ---------------------------------------------------------------------------
#
# THE RULE THIS SECTION SERVES: an instrument enters this repo's register only
# if it has been SHOWN FAILING. A check that cannot fail certifies nothing, and
# a suite of such checks is worse than none, because it manufactures confidence
# at scale.
#
# WHAT IS MUTATED AND WHAT IS NOT. ``SANCTIONED_WRITES`` holds FROZEN
# dataclasses, so a spec cannot be edited in place; a replacement is built with
# ``dataclasses.replace`` and installed with ``monkeypatch.setitem``, which is
# the pattern ``tests/test_writes_nine.py``'s ``_grantable_invitation`` already
# uses. ``linkedin_server/writes.py`` is not touched, and the substitution is
# undone by monkeypatch at the end of each test.
#
# THREE ARMS, CHOSEN BECAUSE THEY WORK DIFFERENTLY. ``_live_control`` is not
# one mechanism wearing nine names:
#
#   save_job          FALLS THROUGH to the shared save-family reader at the
#                     bottom of the function. Its state comes from
#                     ``shape.save_state`` reading an accessible name, and that
#                     reader has never heard of ``spec.from_state``.
#   react_to_item     ITS OWN BRANCH, returning a hardcoded constant after
#                     counting controls. Nothing in it consults the spec.
#   unfollow_company  ITS OWN BRANCH, over a different reader again
#                     (``dom.read_unfollow_control``, keyed by company id and
#                     anchored on a label PREFIX rather than an exact name).
#
# All three mutations were run and all three fired. Where a mutation did
# something OTHER than fire the check, it is recorded below rather than tuned
# away -- see the save family's anchor note.


def _mutated(monkeypatch, action: str, new_from_state):
    """Install a spec whose ``from_state`` is a state nothing on the page says.

    Returns the replacement so a test can pass it to ``_live`` explicitly.
    ``spec_for_action`` would find it anyway; passing it makes the substitution
    visible at the call site rather than implied by a fixture two screens up.
    """
    spec = spec_for_action(action)
    assert new_from_state != spec.from_state, new_from_state
    replacement = dataclasses.replace(spec, from_state=new_from_state)
    monkeypatch.setitem(SANCTIONED_WRITES, _tool_name(action), replacement)
    # The substitution really is what the registry now serves. Without this a
    # mis-keyed setitem would leave every mutation below inert and green.
    assert spec_for_action(action).from_state == new_from_state
    return replacement


async def test_the_check_fires_on_the_save_familys_shared_fall_through(
    writes_on, over, monkeypatch
):
    """MUTATION 1 of 3: ``save_job``, whose arm is the fall-through.

    ``save_job`` has no branch of its own. It drops past all nine to the
    save-family reader at the bottom of ``_live_control``, which waits for the
    control, reads its accessible name and hands it to ``shape.save_state``.
    Nothing on that path has ever seen ``spec.from_state``, so a spec claiming
    a different origin changes NOTHING about what is read -- which is exactly
    the shape the invariant is about, and exactly what makes it a coincidence
    rather than a consequence.

    THE ANCHOR IS HELD FIXED, and that is not a convenience. ``save_job``'s
    anchor is DERIVED from ``from_state``: ``anchor_label_for`` reads
    ``shape.SAVE_LABELS`` backwards, from the state the action is valid from to
    the accessible name that state wears. Mutating ``from_state`` therefore
    ALSO destroys the anchor, and a naive mutation does not fire this check at
    all -- MEASURED: it raises out of ``dom.save_control_selector``, which
    refuses to build a selector for a ``None`` label one frame deeper. That is
    a safe failure and it is the WRONG one: it would demonstrate that the
    selector builder holds, not that this check does.

    So the anchor is computed from the REAL spec and passed in, which isolates
    the single variable this file is about: one field, two ends, nothing else
    moved.
    """
    real = spec_for_action("save_job")
    anchor = writes.anchor_label_for(real, JOB)
    assert anchor == "Save the job", anchor

    replacement = _mutated(monkeypatch, "save_job", "bookmarked")
    # The anchor really did collapse -- stated here so the paragraph above is a
    # measurement rather than a claim.
    assert writes.anchor_label_for(replacement, JOB) is None

    state, why, selector = await _live(
        over, "save_job", spec=replacement, anchor=anchor
    )
    # The reader is untouched by the mutation: it still reads the button.
    assert state == "not_saved", (state, why)
    assert selector != "", why

    with pytest.raises(AssertionError) as caught:
        _assert_the_two_ends_agree(replacement, state, selector, why)
    assert "'bookmarked'" in str(caught.value), str(caught.value)
    assert "not_saved" in str(caught.value), str(caught.value)


async def test_the_check_fires_on_react_to_items_own_arm(
    writes_on, over, monkeypatch
):
    """MUTATION 2 of 3: ``react_to_item``, whose arm returns a CONSTANT.

    A different mechanism from mutation 1 in the way that matters here. The
    save family derives its state from a label lookup; this arm counts the
    reaction controls on the permalink, checks that exactly one is wearing the
    OFF label, and then returns the string ``"no_reaction"`` written into the
    function body. Nothing connects that literal to the spec field the gate
    will compare it against -- they are two independent spellings of one
    string, in two places, and the only thing keeping them equal is that
    somebody typed them the same.

    THE ANCHOR IS NOT AT RISK HERE, which is why none is passed:
    ``anchor_label_for`` answers ``react_to_item`` from
    ``dom.REACTION_OFF_LABEL``, a constant, without consulting ``from_state``
    at all. So the mutation moves exactly one thing.
    """
    replacement = _mutated(monkeypatch, "react_to_item", "already_reacted")
    # Asserted, not assumed: the anchor is untouched, so the arm runs exactly
    # as it does in production and the only difference is the field compared.
    assert (
        writes.anchor_label_for(replacement, REACHED["react_to_item"][2])
        == dom.REACTION_OFF_LABEL
    )

    state, why, selector = await _live(over, "react_to_item", spec=replacement)
    assert state == "no_reaction", (state, why)
    assert selector != "", why

    with pytest.raises(AssertionError) as caught:
        _assert_the_two_ends_agree(replacement, state, selector, why)
    assert "'already_reacted'" in str(caught.value), str(caught.value)


async def test_the_check_fires_on_unfollows_own_arm(writes_on, over, monkeypatch):
    """MUTATION 3 of 3: ``unfollow_company``, over a third reader again.

    Chosen because its arm differs from both of the others in the two ways that
    could plausibly matter. It READS ``grant.target`` -- the numeric company id
    -- and scopes to ONE ROW of a list rather than to a control on a posting;
    and it is anchored on a PREFIX (``Click to stop following ``) rather than
    an exact accessible name, because LinkedIn writes the Page's own name into
    the label. Neither of those touches ``from_state``, and the state it
    returns is again a constant in the function body.

    THREE ARMS IS THE POINT, not three tests. If ``_live_control`` were one
    mechanism, one mutation would be evidence about all of it. It is nine
    branches plus a fall-through over six different readers, so a mutation on
    one says nothing about the next, and part 1's claim is a claim about all of
    them.
    """
    replacement = _mutated(monkeypatch, "unfollow_company", "subscribed")
    assert (
        writes.anchor_label_for(replacement, FOLLOWED_COMPANY)
        == writes.UNFOLLOW_ANCHOR_PREFIX
    )

    state, why, selector = await _live(over, "unfollow_company", spec=replacement)
    assert state == "following", (state, why)
    assert selector != "", why

    with pytest.raises(AssertionError) as caught:
        _assert_the_two_ends_agree(replacement, state, selector, why)
    assert "'subscribed'" in str(caught.value), str(caught.value)


async def test_the_unmutated_specs_still_pass_the_same_check(writes_on, over):
    """THE CONTROL FOR ALL THREE MUTATIONS ABOVE.

    Without it, the three tests above pass perfectly against an
    ``_assert_the_two_ends_agree`` that raises unconditionally. That would make
    every case in part 1 fail too -- but a reader meeting only this section
    would have no way to tell a working check from a broken one, and a control
    is what proves the instrument can still say YES.
    """
    for action in ("save_job", "react_to_item", "unfollow_company"):
        spec = spec_for_action(action)
        state, why, selector = await _live(over, action)
        _assert_the_two_ends_agree(spec, state, selector, why)


# ---------------------------------------------------------------------------
# Part 3. Who reads this field, by name, off the AST
# ---------------------------------------------------------------------------
#
# THE TWO CONSUMERS THIS FILE WAS WRITTEN ABOUT:
#
#   writes._direction   reads ``observation.state`` -- the PREVIEW's reading,
#                       taken off whichever surface ``spec.state_from`` names,
#                       before any write url has been loaded -- and refuses
#                       when it is not ``spec.from_state``.
#
#   writes.valid_from   reads the state ``_live_control`` returned -- taken off
#                       THE CONTROL the click will land on, after the write url
#                       has been loaded -- and refuses when it is not
#                       ``spec.from_state``. Called from ``perform``'s gate 5.
#
# AND THE THREE MORE THE AST FOUND, which is the finding rather than the
# preamble. The premise this file was built on was that there are two. There
# are FIVE functions and ELEVEN sites, MEASURED 2026-09-02:
#
#   writes.anchor_label_for   does not COMPARE against ``from_state`` at all.
#                             It reads ``shape.FOLLOW_LABELS`` and
#                             ``shape.SAVE_LABELS`` BACKWARDS -- from the state
#                             an action is valid from, to the accessible name
#                             that state wears -- and returns it as the anchor a
#                             selector is then built from. So this one field
#                             does not merely gate the write; for the save pair
#                             and for follow it SELECTS THE CONTROL. That is a
#                             third meaning, and it is why part 2's save-family
#                             mutation has to hold the anchor fixed.
#
#   writes._live_control      ``follow_company``'s arm compares its own reading
#                             against ``spec.from_state`` INSIDE the reader and
#                             returns no selector when they differ. For that one
#                             action the comparison therefore happens TWICE --
#                             once here and again in ``valid_from``, on the same
#                             value.
#
#   writes.perform            twice. One is the anchor refusal's message text.
#                             The other is ``unchanged_state =
#                             spec.not_performed_state or spec.from_state or
#                             live_state``, which uses the field as "the state
#                             the target would still read if the write did NOT
#                             happen" -- a fourth meaning, and the one deciding
#                             whether the receipt says ``performed: False`` or
#                             ``performed: "unknown"``.
#
# So the field already carries at least four meanings across five functions,
# and not one of them is ruled anywhere. The pin below is what makes a fifth
# arrive loudly.

#: MEASURED off the AST of ``linkedin_server/writes.py`` on 2026-09-02:
#: function name -> how many times it READS ``.from_state``.
#:
#: A PER-FUNCTION COUNT RATHER THAN A BARE TOTAL, and the tradeoff is stated
#: rather than hidden. A total alone is satisfied by a read MOVING between
#: functions, which is exactly the change worth catching. The cost is that
#: rewording a refusal message inside one of these functions also fires this
#: check -- and when it does, the right response is to read the change and
#: update the number, never to loosen the assertion.
#:
#: WRITES ARE NOT COUNTED HERE. ``from_state=`` in a spec literal or in a
#: ``dataclasses.replace`` is an ``ast.keyword``, and the dataclass field
#: declaration is an ``ast.AnnAssign`` over a bare name; neither is an attribute
#: read. Both are counted separately below, so the distinction is asserted
#: rather than assumed.
FROM_STATE_READERS: dict[str, int] = {
    "_direction": 3,
    "valid_from": 3,
    "anchor_label_for": 2,
    "_live_control": 1,
    "perform": 2,
}

#: The two ends the design is written around, named so the test can assert they
#: are still here even if the counts move.
THE_TWO_ENDS = ("_direction", "valid_from")


def _from_state_reads() -> dict[str, int]:
    """Every ``<something>.from_state`` READ in writes.py, by enclosing function.

    AST, NOT GREP, and the difference is the whole reason this can be trusted:
    the text ``from_state`` occurs 40 times in that file, of which 13 are spec
    literals, 1 is the dataclass field declaration, and the rest are prose in
    docstrings and comments. A count off text would be counting the
    documentation of the field alongside its use.

    Attributed to the INNERMOST enclosing function, following
    ``tests/test_writes.py``'s ``_functions_assigning_into``: a read hidden in a
    nested helper is counted as itself rather than as its parent, so moving one
    scope down does not make it disappear.
    """
    tree = ast.parse(WRITES_PY.read_text(encoding="utf-8"))
    parents: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node

    def enclosing(node: ast.AST) -> str:
        cur = parents.get(node)
        while cur is not None:
            if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return cur.name
            cur = parents.get(cur)
        return "<module>"

    found: dict[str, int] = {}
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and node.attr == "from_state"
            and isinstance(node.ctx, ast.Load)
        ):
            name = enclosing(node)
            found[name] = found.get(name, 0) + 1
    return found


def test_every_reader_of_from_state_is_named_and_counted():
    """A NEW CONSUMER OF THIS FIELD CANNOT ARRIVE QUIETLY.

    That is the whole purpose. ``from_state`` is one string that already means
    at least four different things across five functions (see the block above),
    and not one of those meanings is ruled anywhere in the package. The next
    edit that reads it will inherit whichever meaning its neighbours happen to
    have -- which is exactly how nine call sites came to share an assumption
    nobody had made, and how addressing one action broke all nine.

    So the set is pinned. Adding a read fails here, and whoever adds it has to
    come to the comment above and say which of the four meanings they meant.
    That is a cheap conversation to force and an expensive one to skip.

    WHAT A FAILURE HERE MEANS, in order of likelihood: a refusal message was
    reworded (update the number); a read moved between functions (say why); a
    new function started reading the field (say WHICH MEANING it is using, in
    the block above, before changing the number).
    """
    measured = _from_state_reads()
    assert measured == FROM_STATE_READERS, {
        "measured": dict(sorted(measured.items())),
        "pinned": dict(sorted(FROM_STATE_READERS.items())),
    }
    assert sum(measured.values()) == 11, sum(measured.values())
    # The two ends this file is about must be among them, whatever else moves.
    for name in THE_TWO_ENDS:
        assert name in measured, (name, sorted(measured))
    # And every pinned name must be a REAL function in the module, not one that
    # survived a rename in this table only.
    for name in FROM_STATE_READERS:
        assert callable(getattr(writes, name, None)), name


def test_the_field_is_written_only_where_specs_are_declared():
    """The other half of the count, so "reads" is a claim about reads.

    One ``from_state=`` keyword per entry in ``SANCTIONED_WRITES``, plus one
    dataclass field declaration. Asserting this is what makes the read count
    above meaningful: without it, a read silently reclassified as a write would
    shrink the pinned set with nothing going red.

    COUNTED AGAINST THE REGISTRY, not typed, so adding a fourteenth spec updates
    both sides at once while a fourteenth ``from_state=`` anywhere else does
    not.
    """
    tree = ast.parse(WRITES_PY.read_text(encoding="utf-8"))
    keywords = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.keyword) and node.arg == "from_state"
    ]
    declarations = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == "from_state"
    ]
    assert len(keywords) == len(SANCTIONED_WRITES), (
        len(keywords),
        len(SANCTIONED_WRITES),
    )
    assert len(declarations) == 1, len(declarations)
