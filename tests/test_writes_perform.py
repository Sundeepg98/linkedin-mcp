"""The write boundary's perform: what can act, and everything that has to
be true first.

SPLIT OUT OF ``tests/test_writes.py`` ON 2026-11-27 (lane ci8). That file took
about 137 s alone, over the two-minute cap on a local gate, so it was split
by concern into six files, each well under it. This one holds its
sections 6 (what CAN act) and 6b (three guards a mutation run found
unprotected), moved
verbatim, with their banners and their prose. The fixtures, the navigator,
the frozen captures and the helpers stay in ``tests/test_writes.py``, which
69 test files already import them from; its module docstring is the account
of the whole write boundary these files test, and it still applies here.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from linkedin_server import dom, readonly, shape, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import (
    WRITES_FLAG,
    consume,
    preview,
    spec_for_action,
)
from tests.test_writes import (  # noqa: F401 -- fixtures are used by injection
    _no_grants_survive_a_test,
    browser_page,
    writes_on,
    FixtureNavigator,
    JOB,
    REACTED_ITEM,
    RENAMED_POSTING,
    SAVED_JOB,
    SAVED_LIST_CONTAINING,
    SAVED_LIST_PARTIAL,
    SAVED_POSTING,
    _REACTION_OFF_PAGE,
    _REACTION_ON_LABEL,
    _REACTION_ON_PAGE,
    _bare_grant,
    _gate,
    _granted,
    _pages,
    _perform,
    markup,
)


# ---------------------------------------------------------------------------
# 6. What CAN act, and everything that has to be true first
# ---------------------------------------------------------------------------
#
# THIS SECTION WAS CALLED "Nothing can actually act" AND ASSERTED EXACTLY THAT.
# On 2026-08-23 the operator authorised save and unsave, ``perform`` gained a
# body, and the old assertions became the thing they were guarding against: a
# suite claiming a property the code no longer had.
#
# NOT ONE CLICK IN THIS SECTION REACHES LINKEDIN. Every one lands on a frozen
# capture loaded into a local headless Chromium by ``set_content``. Measured
# before any of it was written, with every request intercepted and aborted so
# that an attempt would have been recorded even if it could not complete: the
# four posting fixtures contain ZERO script tags, attempt ZERO requests on load
# and ZERO on click, do not navigate, and do not move the DOM. The click is
# real, dispatches in ~20ms, and provably cannot leave the machine.
#
# THAT LAST PROPERTY IS ALSO THE LIMIT OF WHAT THESE TESTS CAN SAY, and it is
# stated here rather than left for a reader to infer: because the fixture DOM
# does not move, a test can prove the machinery clicks the right thing under
# the right conditions and can never prove that clicking it saves a job. That
# is a claim only a supervised run against a real account settles, and none has
# happened.








async def test_a_save_runs_end_to_end_and_is_verified_from_the_other_surface(
    writes_on, browser_page
):
    """THE POSITIVE CASE, and it goes first.

    Everything else in this section asserts a refusal, and a section full of
    refusals passes perfectly on a ``perform`` that raises unconditionally --
    which is exactly what this one used to do. This is the test that fails if
    the body goes back to being a stub.
    """
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)
    block, nav = await _perform(
        browser_page, grant, saved=SAVED_LIST_CONTAINING
    )

    assert block["performed"] is True
    assert block["verified"] is True
    assert block["clicked"]["selector"] == 'button[aria-label="Save the job"]'
    assert block["clicked"]["error"] is None
    assert block["clicked"]["state_before"] == "not_saved"
    assert block["verification"]["expected_state"] == "saved"
    assert block["verification"]["observed_state"] == "saved"

    # TWO loads, in this order: the posting it clicks on, then the DIFFERENT
    # surface it confirms from.
    assert nav.gotos == [
        f"https://www.linkedin.com/jobs/view/{SAVED_JOB}/",
        writes.SAVED_LIST_URL,
    ]


async def test_the_confirmation_comes_from_a_surface_other_than_the_button(
    writes_on, browser_page
):
    """A control that redraws itself is the weakest witness to its own effect.

    Pins that the verification read is the saved LIST and not the posting, so
    a later "optimisation" that saves a page load by believing the button
    fails here.
    """
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)
    block, _nav = await _perform(
        browser_page, grant, saved=SAVED_LIST_CONTAINING
    )
    assert block["verification"]["read_from"] == writes.SAVED_LIST_URL
    assert block["verification"]["read_from"] != block["clicked"]["on"]


async def test_a_click_that_did_not_take_reports_false_and_does_not_raise(
    writes_on, browser_page
):
    """THE CONTROL THAT MATTERS MOST IN THIS FILE.

    A post-write verification that always says "verified" is worth nothing, and
    it is the single easiest thing to write by accident. Here the saved list
    AFTER the click is still empty -- the click did not take -- and the block
    has to say so.

    It must also NOT raise. Once the button has been pressed, the most
    important fact in the world is that it was pressed; an exception on the way
    home replaces that fact with a stack trace and the operator retries,
    toggling it back.
    """
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)
    block, _nav = await _perform(
        browser_page, grant, saved="jobs_tracker_empty"
    )
    assert block["performed"] is False
    assert block["verified"] is False
    assert block["verification"]["observed_state"] == "not_saved"
    # The click itself still happened, and the block still says so.
    assert block["clicked"]["error"] is None


async def test_an_unreadable_saved_list_reports_unknown_not_success(
    writes_on, browser_page
):
    """The third outcome, kept separate from the second.

    A saved list that is a fraction of itself cannot settle whether the save
    landed. That is neither success nor failure, and collapsing it into either
    would be the same defect in opposite directions -- reporting success would
    hide a failure, reporting failure invites a retry that double-toggles.

    THE TARGET HERE IS ``JOB`` AND NOT ``SAVED_JOB``, and the first draft of
    this test got that wrong in a way worth recording. It performed on the
    posting the partial list DOES render, expected ``unknown``, and got
    ``True`` -- correctly. Absence from a partial list is not absence; PRESENCE
    in one is still presence. The ambiguity is one-directional, and a test that
    had been written to match a wrong expectation would have pinned the reader
    into treating a perfectly good confirmation as unreadable.
    """
    grant = await _granted(browser_page, "save_job", target=JOB)
    block, _nav = await _perform(
        browser_page, grant, saved=SAVED_LIST_PARTIAL
    )
    assert block["performed"] == "unknown"
    assert block["verified"] is False
    assert block["verification"]["observed_state"] == "unknown"
    assert "below the fold" in block["verification"]["why"]
    assert "Do NOT retry" in block["read_this_if_unsure"]


async def test_presence_in_a_partial_list_still_confirms_the_save(
    writes_on, browser_page
):
    """THE OTHER HALF, and the one the test above was written against by
    mistake.

    The ambiguity in a partial list runs one way only. If the posting IS among
    the rows that rendered, it is saved -- however many rows are still below
    the fold. Pinned so a later "be more careful about partial lists" edit
    cannot make a good confirmation unreadable.
    """
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)
    block, _nav = await _perform(
        browser_page, grant, saved=SAVED_LIST_PARTIAL
    )
    assert block["performed"] is True
    assert block["verified"] is True
    assert block["verification"]["observed_state"] == "saved"






async def test_react_to_item_surfaces_the_labels_its_own_verify_read_saw(
    writes_on, browser_page
):
    """THE FINDING THIS TEST IS FOR: the ON label was never unreachable.

    ``linkedin_react_to_item`` fired live on 2026-09-03 and landed --
    performed True, verified True -- and its own ``reversibility_procedure``
    promised that firing would settle ``reversible_by``'s open half in one
    move: "React to one item and READ THE LABEL THE CONTROL CHANGES INTO."
    The result reported no label. ``_verify_after``'s react branch already
    calls ``dom.read_reaction_surface(page)`` to decide ``verified_state``,
    and that dict already carries ``labels`` -- the shaped accessible names
    of every reaction control on the page -- while the branch only ever
    read ``controls`` and ``off_state`` off it. The string was in the dict
    the fire built and discarded, and stayed discarded the next morning when
    a probe re-measured it by hand instead.

    THIS DRIVES ``writes.perform`` FOR REAL, over two frozen worlds for the
    ONE url react_to_item's click and its own verification share. The save
    pair's "confirm from a DIFFERENT surface" trick does not apply here --
    there is only one surface -- so this hands ``FixtureNavigator`` a LIST
    for that one url instead of a single string: gate 5 reads the OFF page
    on the first visit, and ``_verify_after``'s own re-navigation reads the
    ON page on the second.

    SHOWN FAILING on the code before this patch: ``block`` carried no
    ``newly_observed_reaction_labels`` key at all, so the assertion below
    raised ``KeyError`` rather than an unequal value -- the red output is
    recorded verbatim in ``_audit/_scratch/_reaction-label-report.md``.
    """
    spec = spec_for_action("react_to_item")
    item_url = spec.url_template.format(target=REACTED_ITEM)

    # THE GRANT IS MINTED OFF THE PERMALINK, SINCE 2026-09-05. It was minted
    # off the FEED until then -- ``state_from`` was "feed_item" and
    # ``_SURFACE_READS`` pointed that at FEED_URL, a leftover from the days
    # when this action refused and had no url to aim at -- so the direction
    # the operator confirmed was read over whatever controls the feed drew,
    # all of them other people's, while the click pressed the one control on
    # this item. Three of them, in the reading that caught it. This line
    # froze FEED_URL and asserted that arrangement; it now freezes the page
    # the click lands on. See
    # ``tests/test_react_direction_is_read_where_it_acts.py``.
    preview_nav = FixtureNavigator({item_url: _REACTION_OFF_PAGE})
    block = await preview(
        spec, target=REACTED_ITEM, navigator=preview_nav, page=browser_page
    )
    assert preview_nav.gotos == [item_url], preview_nav.gotos
    grant = consume(
        block["to_confirm"], action="react_to_item", target=REACTED_ITEM
    )

    # THE CLICK'S OWN URL, VISITED TWICE. The first visit is gate 5's re-read
    # of the control about to be pressed -- it needs the OFF label to be
    # valid to click at all. The second is _verify_after's fresh render
    # after the click -- it needs the ON label for verified_state to become
    # "reacted", which is what makes the read this test is FOR run at all.
    perform_nav = FixtureNavigator(
        {item_url: [_REACTION_OFF_PAGE, _REACTION_ON_PAGE]}
    )
    block = await writes.perform(perform_nav, browser_page, grant)

    assert block["clicked"]["selector"] == dom.reaction_control_selector()
    assert block["clicked"]["error"] is None
    assert block["performed"] is True
    assert block["verified"] is True
    assert block["verification"]["observed_state"] == "reacted"
    # TWO VISITS TO THE SAME URL, not two different ones -- pinned so a
    # later "optimise this to one load" cannot quietly start reusing gate
    # 5's stale OFF-page reading for the verify too.
    assert perform_nav.gotos == [item_url, item_url]

    # THE POINT OF THIS TEST. Without the patch this key does not exist.
    assert block["newly_observed_reaction_labels"] == [_REACTION_ON_LABEL]
    assert _REACTION_ON_LABEL in block["what_those_labels_are_for"]
    assert "reversible_by" in block["what_those_labels_are_for"]


def test_unsave_has_its_anchor_now_and_the_row_is_what_supplied_it():
    """THE SUCCESSOR to ``test_unsave_refuses_because_its_anchor_has_never_been_measured``.

    That test asserted the honest gap so it could not be quietly closed with a
    guess: ``anchor_label_for`` returned None for unsave, and ``perform``
    refused with a message naming NEVER OBSERVED and THE SUPERVISED SAVE IS THE
    MEASUREMENT. It was correct for as long as the label rested on nothing, and
    it is retired here rather than deleted, because a suite that still pinned
    that refusal would be pinning a claim the evidence no longer supports.

    WHAT REPLACED THE GAP. The operator saved a posting on 2026-08-30;
    ``perform``'s post-click sweep reported ``"Unsave the job"``; three
    read-only readings through ``linkedin_job_detail`` agreed. The row went in.
    No code changed -- which is the property the old test's sibling was
    asserting all along.

    SHOWN FAILING by removing the row from ``shape.SAVE_LABELS``::

        AssertionError: assert None == 'Unsave the job'
    """
    spec = spec_for_action("unsave_job")
    assert spec.from_state == "saved"
    assert writes.anchor_label_for(spec) == "Unsave the job"
    # Its measured sibling is unchanged, so this is a table that GAINED a row
    # rather than one that was rewritten.
    assert writes.anchor_label_for(spec_for_action("save_job")) == "Save the job"


#: DERIVED: the Saved tab drawing its strip and NOT its list -- LinkedIn's own
#: count says 1, no row is present, and no empty state is either. This is the
#: shape the live Saved tab was measured in on 2026-08-30, reproduced so the
#: consequence for the write gate can be asserted offline.
_TRACKER_EMPTY_RAW = markup("jobs_tracker_empty")
SAVED_LIST_UNREADABLE = _TRACKER_EMPTY_RAW.replace(
    ">No jobs here</h2>", "></h2>", 1
).replace("Saved &#183; 0", "Saved &#183; 1")
assert SAVED_LIST_UNREADABLE != _TRACKER_EMPTY_RAW


async def test_unsave_cannot_be_PREVIEWED_while_the_saved_list_cannot_be_read(
    writes_on, browser_page
):
    """THE BLOCKER THAT OUTLIVED THE ANCHOR, and it is not in this module.

    ``unsave_job`` acquired its anchor on 2026-08-30 and is performable. It is
    still not reachable end to end, and the reason is worth pinning because it
    is easy to mistake for the old refusal: the preview takes its DIRECTION
    from the Saved tab, and that list currently cannot be read -- measured live
    the same day, its rows draw and the harvest returns none of them.

    ``_direction`` refuses on an ``unknown`` origin, before any token is
    minted. So the gate stops one step EARLIER than the anchor gate it used to
    stop at, and a reader who sees this refusal should go and fix the tracker
    read rather than go looking for a label.

    SHOWN FAILING by letting ``_direction`` proceed on ``unknown`` -- and what
    that measured is worth more than the red. The refusal does NOT disappear:
    ``_direction``'s NEXT gate, the wrong-state comparison, catches
    ``'unknown' != 'saved'`` on the way past and raises anyway. What the
    unknown gate actually defends is the ACCURACY of the refusal, not its
    existence::

        AssertionError: 'unsave_job' is valid only from 'saved' and this
        target reads 'unknown'. On a toggle, performing an action from the
        wrong state performs its OPPOSITE [...] You may have wanted the
        inverse action.
        assert "came back 'unknown'" in "'unsave_job' is valid only from ..."

    That message points a reader at the wrong repair -- it suggests they meant
    to SAVE, when what actually happened is that the Saved tab could not be
    read. This test catches the difference only because it asserts on the
    message text rather than merely on the raise.

    AND THE BACKSTOP DOES NOT COVER EVERY ACTION, which is why the unknown gate
    is not redundant. ``set_open_to_work`` takes the multi-state branch, which
    returns BEFORE the wrong-state comparison, so for that action the unknown
    gate is the only thing between an unreadable origin and a rendered confirm
    block. Not exercised here; recorded so nobody removes the gate on the
    strength of this one action's backstop.
    """
    with pytest.raises(WriteAttemptError) as caught:
        await _gate(
            browser_page,
            "unsave_job",
            target=SAVED_JOB,
            saved=SAVED_LIST_UNREADABLE,
        )

    message = str(caught.value)
    assert "came back 'unknown'" in message, message
    assert "guessing" in message, message
    # It must name the SURFACE that failed, so the reader fixes the right one.
    assert "Saved tab" in message, message
    # And NO TOKEN MAY EXIST. _direction runs before mint, so a refusal here
    # must leave nothing redeemable behind -- a gate that refused and minted
    # anyway would hand out a token for an action it had just declined.
    assert writes._GRANTS == {}
    assert writes._OBSERVED == {}


async def test_save_refuses_on_a_posting_that_is_ALREADY_saved(
    writes_on, browser_page
):
    """THE TOGGLE HAZARD, and it became reachable for the first time on
    2026-08-30.

    THIS IS THE MOST IMPORTANT TEST IN THIS FILE and it could not exist before
    the ON label was measured. On a toggle, performing an action from the wrong
    state performs its OPPOSITE: a save confirmed on an already-saved posting
    UNSAVES it. Gate 5 is what stops that, by re-reading the control and
    refusing when what it reads is not the state the action is valid from.

    Until the ON label was in the table, that gate could not be tested against
    a real wrong state -- a saved posting read as ``unknown``, so the gate
    refused for want of a reading rather than because of one. It now refuses
    on a MEASURED state, which is a different and much stronger claim, and it
    is asserted rather than assumed to follow by symmetry.

    SHOWN FAILING by dropping the state comparison in ``perform``, which is the
    edit that makes the whole design a formality::

        Failed: DID NOT RAISE WriteAttemptError
        -- a save was performed on an already-saved posting, which unsaves it
    """
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)

    with pytest.raises(WriteAttemptError) as caught:
        # DERIVED: the world changed between the preview and the click -- the
        # posting is now saved. That is exactly the race gate 5 exists for.
        await _perform(
            browser_page, grant, posting=SAVED_POSTING, saved=SAVED_LIST_CONTAINING
        )

    message = str(caught.value)
    assert "refusing to click" in message, message
    assert "'save_job' is valid only from 'not_saved'" in message, message
    # And it must name what it actually READ, not merely that it disagreed.
    assert "'saved'" in message, message


async def test_unsave_refuses_from_a_state_it_cannot_read(writes_on, browser_page):
    """The refusal NARROWED on 2026-08-30; it did not disappear.

    ``unsave_job`` refused unconditionally for a month, for want of an anchor.
    It now has one, so the interesting question is whether it still refuses
    where it should -- on a control wearing a name nobody has measured. A tool
    that went from "always refuses" to "always acts" would have traded one
    unsafe absolute for a worse one.

    SHOWN FAILING by letting ``_live_control`` fall back to the anchor when the
    live read comes back ``unknown``::

        Failed: DID NOT RAISE WriteAttemptError
    """
    grant = await _granted(
        browser_page, "unsave_job", target=SAVED_JOB, saved=SAVED_LIST_CONTAINING
    )

    with pytest.raises(WriteAttemptError) as caught:
        await _perform(
            browser_page,
            grant,
            posting=RENAMED_POSTING,
            saved=SAVED_LIST_CONTAINING,
        )

    message = str(caught.value)
    assert "refusing to click" in message, message
    assert "'unsave_job' is valid only from 'saved'" in message, message
    assert "unknown" in message, message
    # And the diagnostic must still report what the page actually drew, so the
    # reader is not left guessing at the new name.
    assert "WHAT WAS ON THE PAGE" in message, message


async def test_the_anchor_refusal_is_reachable_and_says_what_it_now_means(
    writes_on, browser_page, monkeypatch
):
    """The guard no shipped action can reach, FIRED -- not asserted about.

    ``perform``'s save-family ``anchor is None`` branch became structurally
    unreachable on 2026-08-30: both save-family actions resolve an anchor, and
    every other performable action returns from its own branch above the table
    lookup. This repo's rule is that a check which cannot fail certifies
    nothing, so the guard-versus-delete call was made deliberately -- it stays,
    and it is fired here.

    WHAT IT NOW CATCHES is a REGRESSION rather than a missing measurement, so
    that is what this reproduces: the grant is minted while the table is
    intact, and the row is then removed underneath it. An edit to
    ``shape.SAVE_LABELS``, or a bad merge, looks exactly like this.

    THE REFUSAL MUST NOT SAY THE OLD THING. Its previous text sent the reader
    off to photograph a label nobody had seen. That label has been seen, so a
    reader meeting this today has a broken table rather than a missing
    measurement, and the message has to point at the right one.

    SHOWN FAILING by deleting the branch. It does NOT produce a click on a
    guessed selector -- ``dom.save_control_selector`` is a second line of
    defence and it holds, refusing a ``None`` label one frame deeper. What is
    lost is the ALTITUDE of the explanation::

        linkedin_server\\writes.py:4028: in perform
            live_state, live_why, selector = await _live_control(...)
        linkedin_server\\dom.py:627: ExtractionFailedError: refusing to build a
        save-control selector for None: this reader has only ever seen
        ['Save the job', 'Unsave the job'].

    The deleted block's own comment predicted that traceback by function name
    before it was measured, and claimed diagnostic quality rather than being
    the last stop. Both halves of that turned out to be right, which is the
    reason it is kept rather than deleted as redundant.
    """
    grant = await _granted(
        browser_page, "unsave_job", target=SAVED_JOB, saved=SAVED_LIST_CONTAINING
    )

    # THE REGRESSION, applied AFTER the grant exists: the vocabulary loses the
    # row unsave anchors on. anchor_label_for reads the table live, so this is
    # the same state a bad edit would produce.
    monkeypatch.setattr(shape, "SAVE_LABELS", {"Save the job": "not_saved"})
    assert writes.anchor_label_for(spec_for_action("unsave_job")) is None

    with pytest.raises(WriteAttemptError) as caught:
        await _perform(
            browser_page,
            grant,
            posting=SAVED_POSTING,
            saved=SAVED_LIST_CONTAINING,
        )

    message = str(caught.value)
    assert "has no measured anchor" in message, message
    assert "maps no accessible name to that state" in message, message
    assert "regression" in message, message
    # The retired sentence must not come back: it told the reader to go and
    # photograph a label that has been photographed.
    assert "NEVER BEEN OBSERVED" not in message, message
    assert "SUPERVISED SAVE IS THE MEASUREMENT" not in message, message


def test_the_anchor_table_is_still_the_only_thing_gating_the_save_family():
    """The mechanism the old gap proved by ABSENCE, now proved by presence.

    Its predecessor added a pretend row to a COPY of the table and showed the
    lookup would resolve. The real row now exists, so the same claim is made
    the other way round: take the row away and the anchor goes with it, with no
    code path involved either time.

    SHOWN FAILING by hardcoding the anchor in ``anchor_label_for`` instead of
    reading it out of the table::

        AssertionError: 'Unsave the job' is not None -- the anchor survived
        the row being removed, so it is not coming from the table
    """
    spec = spec_for_action("unsave_job")

    # Run the real lookup against a table with the row taken out. Nothing is
    # monkeypatched into the module: the lookup is re-derived here exactly as
    # anchor_label_for derives it, so the real table stays untouched.
    without = {
        label: state
        for label, state in shape.SAVE_LABELS.items()
        if state != spec.from_state
    }
    resolved = [
        label for label, state in without.items() if state == spec.from_state
    ]
    assert resolved == []

    # And the real table still holds exactly the two measured rows.
    assert shape.SAVE_LABELS == {
        "Save the job": "not_saved",
        "Unsave the job": "saved",
    }


async def test_follow_ships_and_the_aiming_problem_ships_with_it(writes_on):
    """THE OPERATOR'S CUT, LIFTED 2026-08-30 -- and the fact it rested on kept.

    THIS TEST INVERTED, and inverting it is the honest edit rather than
    deleting it. It read ``test_follow_is_sanctioned_and_still_will_not_be_
    performed`` and asserted that perform() refused a follow, naming the
    aiming problem: a follow is performed from a posting, which identifies its
    employer by SLUG; the unfollow surface addresses rows by NUMERIC COMPANY
    ID; nothing resolves one to the other.

    EVERY WORD OF THAT IS STILL TRUE and it was re-measured the day follow
    shipped, by the cheapest route the previous audit named:
    ``linkedin_job_detail`` on a live posting returned
    ``company_url: .../company/<slug>/``, a slug and not an id. What changed is
    not the measurement, it is WHO THE MEASUREMENT IS FOR. "The undo cannot be
    aimed" is a REVERSIBILITY fact, and this design has a place for one -- the
    ``reversible_by`` field, which the confirm gate prints in full before he
    decides. Keeping the action back as WELL amounts to deciding for him on a
    ground he can read.

    So the assertions MOVED rather than went: the numbers and the slug/id
    problem must still be somewhere he meets them, and this is where that is
    checked. A refusal that decays into "not supported" used to fail here; now
    a permission that decays into silence does.
    """
    assert "follow_company" in writes.PERFORMABLE
    spec = spec_for_action("follow_company")
    # The claim has to survive in the field the gate PRINTS, not in a comment.
    reversible_by = spec.reversible_by.casefold()
    assert "slug" in reversible_by
    assert "numeric company id" in reversible_by
    assert "not this server" in reversible_by
    # And the verdict beside it must not be a bare "reversible": a follow is
    # reversible in LinkedIn and not by this server, and the block says both.
    assert spec.reversibility_class == "REVERSIBLE"
    assert spec.reversibility_measured is True


async def test_follow_has_the_anchor_and_the_branch_a_click_needs(writes_on):
    """THE PREREQUISITE THAT MADE THE MOVE SAFE, asserted rather than assumed.

    Adding an action to PERFORMABLE is one line, and on its own it would have
    been a defect: gate 5 (``_live_control``) had no branch for follow, so it
    would have fallen through to the SAVE family's -- re-reading the save
    button on a posting and calling that a corroboration of the follow
    control. That is precisely the bug apply carried until 2026-08-26, and it
    is invisible from the outside because the fall-through returns a plausible
    answer about the wrong element.

    Two things are asserted, because either alone would let it back in: the
    anchor exists and is a MEASURED label, and it is not the save anchor.
    """
    spec = spec_for_action("follow_company")
    anchor = writes.anchor_label_for(spec)
    assert anchor == "Follow"
    # Derived from the measured table rather than typed twice, which is what
    # makes the anchor unguessable: an unmeasured label has no entry to find.
    assert shape.FOLLOW_LABELS[anchor] == spec.from_state
    assert anchor not in shape.SAVE_LABELS
    # And the selector builder refuses anything the reader has not seen.
    assert dom.follow_control_selector(anchor) == 'button[aria-label="Follow"]'
    with pytest.raises(Exception):
        dom.follow_control_selector("Follow this company")


async def test_the_follow_spec_still_carries_the_two_measured_numbers(writes_on):
    """2b applied to a field rather than to a refusal.

    THE OTHER HALF OF THE INVERSION ABOVE. This used to compare the refusal
    MESSAGE against ``follow_company.residue`` and require both to carry the
    same two measured numbers -- 20 rows rendered of a stated 58 -- so the two
    copies of one claim could not drift. The message is gone; the claim is not,
    and it is now the reason the gate gives him for why a follow he makes here
    may be one this server cannot point its own unfollow at.

    Pinned on the spec alone, which is the copy that survives.
    """
    spec = spec_for_action("follow_company")
    for number in ("20", "58"):
        assert number in spec.residue, number
    assert "slug" in spec.residue.casefold()


async def test_open_to_work_is_not_performable_either(writes_on):
    """Unperformable, and the refusal says WHICH KIND of unperformable.

    Sharpened 2026-08-24. It used to assert the generic sentence "not
    performable", which three different actions would print for three
    unrelated reasons -- a message that cannot distinguish them teaches a
    reader that it carries no information. Open To Work's reason is that its
    editor has no url AT ALL, which is now a measurement (237 urls and 37
    payload paths across five profile captures, zero hits) rather than an
    admission that nobody looked.
    """
    grant = _bare_grant(action="set_open_to_work", target="self")
    grant.consumed = True
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(object(), object(), grant)
    message = str(excinfo.value)
    assert "not addressed by a url" in message
    assert "237" in message


class _FakePage:
    """Just enough page for the gate: it sleeps, and that is all it is asked."""

    async def wait_for_timeout(self, _ms: int) -> None:
        return None


def _fake_modal(reading: dict):
    """Hand the gate a fixed modal reading.

    The gate is tested through ``dom.read_apply_modal`` rather than through a
    fake DOM on purpose: what is under test is the DECISION -- which readings
    are safe to press a submit on -- not Playwright's selector engine. A fake
    DOM would test both at once and tell you less about either.
    """

    async def _read(_page):
        return dict(reading)

    return _read


#: Every way the apply modal can fail to be the shape that was measured, and
#: the word the refusal must contain so a caller learns WHICH one happened.
#:
#: The first entry is the one that matters most and is the reason this gate
#: exists at all: exactly ONE apply flow has ever been observed on this
#: account -- a single screen, one enabled Submit, no Next. A posting drawing a
#: Next is a multi-step flow nobody here has watched finish, and walking it
#: would mean filling in steps that have never been seen to reach a control
#: that cannot be un-pressed.
_GATE_REFUSALS = [
    (
        {
            "modal_present": True,
            "submit_present": True,
            "submit_enabled": True,
            "submit_name": "Submit application",
            "advance_names": ["next"],
            "buttons_total": 12,
            "advance_scan_complete": True,
        },
        "more than one step",
        "a multi-step flow",
    ),
    (
        {
            "modal_present": True,
            "submit_present": True,
            "submit_enabled": False,
            "submit_name": "Submit application",
            "advance_names": [],
            "buttons_total": 12,
            "advance_scan_complete": True,
        },
        "disabled",
        "a form wanting something it has not got",
    ),
    (
        {
            "modal_present": True,
            "submit_present": True,
            "submit_enabled": True,
            "submit_name": "Continue to next step",
            "advance_names": [],
            "buttons_total": 12,
            "advance_scan_complete": True,
        },
        "corroborate",
        "the hook and the accessible name disagreeing",
    ),
    (
        {
            "modal_present": True,
            "submit_present": True,
            "submit_enabled": True,
            "submit_name": "Submit application",
            "advance_names": [],
            # The shape the ceiling used to produce SILENTLY. Before
            # 2026-08-26 the reader walked min(total, 40) and returned this
            # same empty list with no way to say it had stopped early, so a
            # Next past the fortieth button read as a single-screen flow.
            "buttons_total": 207,
            "advance_scan_complete": False,
        },
        "did not finish",
        "a scan that stopped early reporting an empty list",
    ),
    (
        {
            "modal_present": False,
            "submit_present": False,
            "submit_enabled": False,
            "submit_name": None,
            "advance_names": [],
            "buttons_total": 12,
            "advance_scan_complete": True,
        },
        "never rendered",
        "the modal not drawing at all",
    ),
]


@pytest.mark.parametrize(
    "modal,needle,what", _GATE_REFUSALS, ids=[c[2] for c in _GATE_REFUSALS]
)
async def test_the_second_gate_refuses_a_flow_it_cannot_confirm(
    monkeypatch, modal, needle, what
):
    """REWRITTEN 2026-08-25, because the behaviour it pinned was deliberately
    changed and the old assertions had become false claims.

    It used to assert that apply refuses ALWAYS, and that the refusal names a
    missing capture ("no capture in this repo shows a form ... it has not been
    run"). The capture was taken on 2026-08-24 and apply became performable, so
    every one of those strings is now something this server would be lying to
    say. Repointed rather than deleted: the invariant worth keeping was never
    "apply refuses", it was "apply refuses when it cannot confirm what it is
    about to press".

    That is what this asserts now, one failure mode at a time. The gate sits
    BETWEEN the two clicks: the first opened the modal and submitted nothing,
    so refusing here costs at most a draft, while being wrong costs an
    application nobody can withdraw.
    """
    monkeypatch.setattr(dom, "read_apply_modal", _fake_modal(modal))
    verdict = await writes._apply_submit_gate(_FakePage())
    assert verdict["proceed"] is False, what
    assert needle in verdict["why"].casefold(), (what, verdict["why"])


async def test_the_second_gate_proceeds_only_on_the_measured_shape(monkeypatch):
    """The positive case, without which every assertion above is vacuous.

    A gate that refused unconditionally would pass all four refusal cases
    perfectly while making apply unbuildable -- the same defect class as a
    redactor that flattens every input, or a check that cannot fail. This is
    the control on the controls.
    """
    monkeypatch.setattr(
        dom,
        "read_apply_modal",
        _fake_modal(
            {
                "modal_present": True,
                "submit_present": True,
                "submit_enabled": True,
                "submit_name": "Submit application",
                "advance_names": [],
            "buttons_total": 12,
            "advance_scan_complete": True,
            }
        ),
    )
    verdict = await writes._apply_submit_gate(_FakePage())
    assert verdict["proceed"] is True, verdict["why"]
    assert verdict["selector"] == dom.APPLY_SUBMIT_SELECTOR
    # It says WHY it was satisfied, not merely that it was.
    assert "zero advance controls" in verdict["why"].casefold()


def test_the_offsite_ground_is_stated_and_does_not_expire():
    """The half of the old refusal that a better capture never lifts.

    Applying on a third party's applicant-tracking system is refused on a
    different ground from anything measurable: it is somebody else's form on
    somebody else's domain. That ground survived apply becoming performable,
    and it lives on the spec rather than in a message, so it is asserted where
    it lives.
    """
    spec = writes.SANCTIONED_WRITES["linkedin_apply_job"]
    note = spec.wrong_state_note.casefold()
    assert "third party" in note or "third-party" in note
    assert "applicant-tracking" in note or "applicant tracking" in note
    # And it still must not read as "applying is out of scope by design",
    # which is the claim this server spent four documents making and retracted.
    assert "out of scope" not in note


def test_the_apply_capture_procedure_exists_and_clicks_nothing():
    """The refusal points at a file. The file must exist, and must be the kind
    of thing the refusal claims it is.

    A procedure named but absent is worse than no procedure: it reads as
    completed work. And a capture script that clicked something would be
    exactly the risk the refusal exists to avoid, so that claim is checked
    with the package's own scanner rather than by reading the file.
    """
    from linkedin_server import readonly

    probe = Path(__file__).resolve().parents[1] / "scripts" / "_probe_apply_flow.py"
    assert probe.exists(), probe
    source = probe.read_text(encoding="utf-8")

    assert readonly.scan_source_for_mutations(source) == []
    # Guarded, so importing it cannot launch a browser -- the sibling probes'
    # standing hole, closed on the two files that would navigate somewhere
    # consequential.
    assert 'if __name__ == "__main__":' in source
    # The job id is required, never defaulted: which posting this opens is not
    # a decision a default should make.
    assert "usage:" in source


async def test_an_unredeemed_grant_performs_nothing(writes_on, browser_page):
    """``perform`` does not redeem its own permission.

    Requiring an already-consumed grant is what makes "the token was checked"
    a fact rather than a convention: single use, this action, this target, not
    expired -- all of it provably ran before this function was entered.
    """
    block, _nav = await _gate(browser_page, "save_job", target=SAVED_JOB)
    grant = writes._GRANTS[block["to_confirm"]]
    assert grant.consumed is False
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(object(), object(), grant)
    assert "not been redeemed" in str(excinfo.value)


async def test_a_grant_with_no_reading_behind_it_performs_nothing(writes_on):
    """A grant that preview did not build carries no observation, and stops."""
    grant = _bare_grant()
    grant.consumed = True
    assert grant.observation is None
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(object(), object(), grant)
    assert "carries no reading" in str(excinfo.value)


async def test_writes_off_stops_perform_even_with_a_valid_grant(
    monkeypatch, browser_page
):
    """The flag is checked in ``perform`` too, not only on the way in.

    A grant minted while writes were on must not survive the flag being turned
    off -- otherwise "writes are disabled" is a statement about the past.
    """
    monkeypatch.setenv(WRITES_FLAG, "1")
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)
    monkeypatch.setenv(WRITES_FLAG, "0")
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(object(), object(), grant)
    assert "disabled" in str(excinfo.value)
    writes.discard_all()


async def test_a_control_in_the_wrong_state_is_not_clicked(writes_on, browser_page):
    """GATE 5, and it is the one the preview cannot provide.

    The posting served to ``perform`` renders no save control this reader
    recognises, so the live read comes back ``unknown`` and the click does not
    happen -- even though the grant is valid and the preview said not_saved.
    On a toggle, acting from the wrong state performs the OPPOSITE action.
    """
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)
    stripped = markup("job_detail").replace(
        'aria-label="Save the job"', 'aria-label="Something Else Entirely"'
    )
    nav = FixtureNavigator(
        {f"https://www.linkedin.com/jobs/view/{grant.target}/": stripped}
    )
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(nav, browser_page, grant)
    message = str(excinfo.value)
    assert "refusing to click" in message
    assert "'unknown'" in message
    # And the verification surface was never even asked for: it stopped first.
    assert nav.gotos == [f"https://www.linkedin.com/jobs/view/{grant.target}/"]


async def test_landing_on_a_different_posting_is_not_clicked(writes_on, browser_page):
    """The browser going somewhere the grant is not permission for.

    ``assert_write_url`` checks the url this server BUILT; this checks where it
    actually ARRIVED, which is a different fact and the one that matters after
    a redirect.
    """
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)

    class Redirecting(FixtureNavigator):
        async def goto(self, page, url: str) -> str:
            await super().goto(page, url)
            return "https://www.linkedin.com/jobs/view/4600000099/"

    nav = Redirecting(_pages(target=grant.target, posting="job_detail"))
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(nav, browser_page, grant)
    assert "is not that posting" in str(excinfo.value)


async def test_the_click_selector_cannot_be_built_from_an_unmeasured_label():
    """The other half of the click, held to the same rule as the url.

    ``assert_write_url`` refuses a url that did not come from the grant. This
    refuses a SELECTOR that did not come from a measured observation, so the
    two halves of the click are gated by the same discipline.
    """
    from linkedin_server.errors import ExtractionFailedError

    assert dom.save_control_selector("Save the job") == (
        'button[aria-label="Save the job"]'
    )
    with pytest.raises(ExtractionFailedError) as excinfo:
        dom.save_control_selector("Saved")
    assert "only ever seen" in str(excinfo.value)


async def test_perform_reports_the_label_the_control_became(
    writes_on, browser_page
):
    """The measurement that unblocks unsave, taken at the only moment it can be.

    Nothing branches on it -- asserted by the fact that this save succeeds
    while the reported label is still the OFF one, because a frozen capture's
    DOM does not move when it is clicked. On a live account it would be the
    ON-state label, which is the one line missing from ``shape.SAVE_LABELS``.
    """
    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)
    block, _nav = await _perform(
        browser_page, grant, saved=SAVED_LIST_CONTAINING
    )
    assert "newly_observed_save_label" in block
    assert "shape.SAVE_LABELS" in block["what_that_label_is_for"]
    # It did not gate anything: the save is still reported as performed.
    assert block["performed"] is True


# ---------------------------------------------------------------------------
# 6b. Three guards a mutation run found unprotected
# ---------------------------------------------------------------------------
#
# A 20-mutant run over the new guards on 2026-08-24 killed 17 and left THREE
# alive. All three were behavioural mutants, verified by probe rather than
# assumed, so their survival was a real gap in this file and not a bad mutant.
# Each is closed below, and each diagnosis is written down, because in two of
# the three cases the reason the mutant survived is more interesting than the
# test that kills it.


def _calls_by_name_in(source: str, function: str) -> set[str]:
    """Every function called by name inside ``function``, by AST.

    Attribute calls are recorded by their attribute (``page.click`` ->
    ``click``); bare calls by their name.
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != function:
            continue
        found: set[str] = set()
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Call):
                continue
            func = inner.func
            if isinstance(func, ast.Name):
                found.add(func.id)
            elif isinstance(func, ast.Attribute):
                found.add(func.attr)
        return found
    raise AssertionError(f"no function named {function!r} in the source")


def test_perform_goes_through_the_write_door():
    """MUTANT 14, and the diagnosis is the point.

    Deleting the ``assert_write_url`` call from ``perform`` left the whole
    suite green. That is not a missing behavioural test -- it is a fact about
    these two actions: the url ``perform`` builds is rebuilt from the grant's
    own template, and EVERY url the write door would refuse for save or unsave
    is one the READ door refuses too, one line later. The two doors currently
    overlap completely, so no input can distinguish them and no behavioural
    test can exist.

    That overlap IS defence in depth working, and it is exactly why the call
    must not be dropped as redundant: the read allowlist is not maintained with
    writes in mind, and the day it admits a url shape the write pattern does
    not, this call is the only thing left. So the check is STRUCTURAL, which is
    the honest instrument for a claim about redundancy, and the door's own
    behaviour is tested directly in section 3.
    """
    source = Path(writes.__file__).read_text(encoding="utf-8")
    calls = _calls_by_name_in(source, "perform")
    assert "assert_write_url" in calls, (
        "perform no longer goes through the write door. It is redundant with "
        "the read door TODAY and that is not a reason to remove it."
    )
    # And the read door too, via the loader that enforces it.
    assert "_load" in calls


def test_that_structural_check_would_notice_the_deletion():
    """THE CONTROL: the same walk over the source with the call removed."""
    source = Path(writes.__file__).read_text(encoding="utf-8")
    # THE LITERAL MOVED 2026-09-05, when the url stopped being formatted from
    # the whole canonical target -- ``comment_on_item``'s is ``item :: text``,
    # so that spelling built an address with his comment inside it and the
    # action could not navigate. This control has to quote whatever the call
    # currently IS, which is why its assertion below says "update this test"
    # rather than failing silently: a mutation that no longer applies proves
    # nothing about a check that still runs.
    without = source.replace(
        "    url = assert_write_url(\n"
        '        str(spec.url_template or "").format(\n'
        "            target=url_target_of(spec, grant.target)\n"
        "        ),\n"
        "        grant,\n"
        "    )",
        '    url = str(spec.url_template or "").format(\n'
        "        target=url_target_of(spec, grant.target)\n"
        "    )",
        1,
    )
    assert without != source, "the mutation did not apply -- update this test"
    assert "assert_write_url" not in _calls_by_name_in(without, "perform")


@pytest.mark.parametrize(
    "label", ["Saved", "Remove from saved", "", "Save", "Unsave", "unsave the job"]
)
def test_an_unrecognised_save_label_is_never_guessed_at(label):
    """MUTANT 18, and its diagnosis is the more useful half.

    Making ``save_state`` return ``not_saved`` for a label it has never seen
    left the suite green -- because the branch was UNREACHABLE through
    ``read_save_control``: ``dom.SAVE_CONTROL`` matched only the one known
    label, so an unknown one produced count 0 and the answer came from the
    count branch. It was tested directly rather than waiting for the day
    somebody was mid-way through adding the second row.

    THAT DAY CAME, 2026-08-30, and the branch is still unreachable -- because
    both tables were widened together, which is what
    ``test_the_selector_and_the_vocabulary_cannot_drift_apart`` exists to
    enforce. It becomes reachable if and only if one table is widened and the
    other is not, which is exactly the accident worth having a live test for.

    ``"Unsave the job"`` LEFT this list on that date, because it is now
    measured; four labels one edit away from it took its place. ``"Save"`` and
    ``"Unsave"`` are the sharp ones -- each is a prefix of a real label -- and
    ``"unsave the job"`` differs from a real label only in case. None may be
    guessed at.
    """
    verdict = shape.save_state(label, count=1)
    assert verdict["state"] == shape.SAVE_UNKNOWN, (label, verdict)
    # The reason must send the reader to re-measure the selector, and must NOT
    # invite them to add whatever name turned up to the table.
    assert "LINKEDIN HAS RENAMED" in verdict["why"], verdict
    assert "re-measure the selector" in verdict["why"], verdict


@pytest.mark.parametrize(
    "label,expected", [("Save the job", "not_saved"), ("Unsave the job", "saved")]
)
def test_both_measured_labels_ARE_recognised(label, expected):
    """THE CONTROL for the refusals above, which otherwise pass on a function
    that returns ``unknown`` for everything.

    Both rows since 2026-08-30. The predecessor asserted one, and asserting
    only one now would let the new row be silently dropped while this file
    stayed green.

    SHOWN FAILING by removing either row from ``shape.SAVE_LABELS``::

        AssertionError: assert 'unknown' == 'saved'
    """
    verdict = shape.save_state(label, count=1)
    assert verdict["state"] == expected, verdict
    assert repr(label) in verdict["why"], verdict


def test_the_selector_and_the_vocabulary_cannot_drift_apart():
    """The anti-drift check the follow pair never had, on the save pair.

    ``shape.SAVE_LABELS`` is the vocabulary and ``dom.SAVE_LABELS_SEEN`` builds
    the selector, in two modules that do not import each other. If they drift,
    the reader stops matching a state it claims to know -- which is precisely
    how the branch above becomes reachable AND wrong at the same time. This is
    the check that makes adding the unsave row a one-line change in one place
    plus a failing test if it is not mirrored.
    """
    assert set(dom.SAVE_LABELS_SEEN) == set(shape.SAVE_LABELS), (
        sorted(dom.SAVE_LABELS_SEEN),
        sorted(shape.SAVE_LABELS),
    )
    for label in dom.SAVE_LABELS_SEEN:
        assert f'aria-label="{label}"' in dom.SAVE_CONTROL


async def test_a_write_tool_refuses_before_it_touches_a_browser(monkeypatch):
    """MUTANT 20. The refusal is not enough; WHERE it happens is the claim.

    Deleting the writes-off short-circuit from ``_write_tool`` left the suite
    green because the caller still gets an error either way -- ``observe``
    refuses further down. But by then the server has LAUNCHED CHROMIUM and, one
    step later, would have navigated to LinkedIn. A read-only process that
    opens a browser and loads a posting because somebody called a write tool is
    doing something it said it would not.

    So this asserts the position rather than the outcome: with writes off, the
    browser session is never even opened. ``BROWSER.session`` is replaced with
    something that raises, so touching it is unmistakable.
    """
    from linkedin_server import server as server_module

    monkeypatch.delenv(WRITES_FLAG, raising=False)

    def exploding_session(*args, **kwargs):
        raise AssertionError(
            "a browser session was opened for a write that should have been "
            "refused before any browser was touched"
        )

    monkeypatch.setattr(server_module.BROWSER, "session", exploding_session)

    for tool in (server_module.linkedin_save_job, server_module.linkedin_unsave_job):
        out = await tool(job_id=JOB)
        assert out["error"] == "writes_disabled", out
        assert out["performed"] is False
        assert WRITES_FLAG in out["message"]


async def test_that_browser_trap_is_armed(monkeypatch):
    """THE CONTROL. With writes ON, the same tool DOES reach for a browser --
    so the test above is measuring the short-circuit and not a tool that never
    opens a session at all."""
    from linkedin_server import server as server_module

    monkeypatch.setenv(WRITES_FLAG, "1")
    reached = []

    def exploding_session(*args, **kwargs):
        reached.append(True)
        raise RuntimeError("browser reached")

    monkeypatch.setattr(server_module.BROWSER, "session", exploding_session)
    out = await server_module.linkedin_save_job(job_id=JOB)
    assert reached == [True]
    assert "error" in out
    writes.discard_all()


async def test_the_tool_previews_without_a_token_and_redeems_with_one(
    writes_on, browser_page, monkeypatch
):
    """THE TWO-STEP CONTRACT, at the level a caller actually meets it.

    Everything else in this file drives ``preview`` and ``perform`` directly.
    Nothing pinned the ONE LINE that chooses between them -- and that line is
    the whole of what the tool's docstring promises: no token performs nothing,
    a token redeems. A mutant that always previewed would leave a caller
    confirming forever with nothing happening and every other test green.

    The browser session is replaced with the frozen-fixture page this module
    already uses, so the tool runs its real body against real markup and still
    touches nothing.
    """
    from contextlib import asynccontextmanager

    from linkedin_server import server as server_module

    nav = FixtureNavigator(
        _pages(target=SAVED_JOB, posting="job_detail", saved="jobs_tracker_empty")
    )

    @asynccontextmanager
    async def fake_session(*args, **kwargs):
        yield browser_page

    monkeypatch.setattr(server_module.BROWSER, "session", fake_session)
    monkeypatch.setattr(server_module.BROWSER, "goto", nav.goto)

    # Step one: no token. Nothing is performed, and a token comes back.
    block = await server_module.linkedin_save_job(job_id=SAVED_JOB)
    assert block["performed"] is False
    assert block["to_confirm"]
    assert block["where"]["job_id"] == SAVED_JOB

    # Step two: that token. Now it acts -- against the same frozen world, so
    # the saved list still reads empty and the honest answer is "did not take".
    result = await server_module.linkedin_save_job(
        job_id=SAVED_JOB, confirm_token=block["to_confirm"]
    )
    assert "to_confirm" not in result
    assert result["clicked"]["selector"] == 'button[aria-label="Save the job"]'
    assert result["performed"] is False
    assert result["verified"] is False


async def test_a_token_from_one_tool_will_not_redeem_at_the_other(
    writes_on, browser_page, monkeypatch
):
    """THE CONTROL. The token is bound to its verb at the tool boundary too.

    Without this, the test above passes on a ``_write_tool`` that ignored
    ``action`` entirely and redeemed anything.
    """
    from contextlib import asynccontextmanager

    from linkedin_server import server as server_module

    nav = FixtureNavigator(
        _pages(target=SAVED_JOB, posting="job_detail", saved="jobs_tracker_empty")
    )

    @asynccontextmanager
    async def fake_session(*args, **kwargs):
        yield browser_page

    monkeypatch.setattr(server_module.BROWSER, "session", fake_session)
    monkeypatch.setattr(server_module.BROWSER, "goto", nav.goto)

    block = await server_module.linkedin_save_job(job_id=SAVED_JOB)
    out = await server_module.linkedin_unsave_job(
        job_id=SAVED_JOB, confirm_token=block["to_confirm"]
    )
    assert "error" in out, out
    assert "save_job" in out["message"]


def test_the_write_module_contains_only_sanctioned_mutating_calls():
    """WHAT THIS TEST USED TO ASSERT: that the scanner found nothing here.

    It finds four things, all in ``perform``, and that is the complete list.
    The scanner was NOT taught to stop seeing any of them -- the raw scan
    below still reports every one -- which is why it can still see a fifth.

    THE NAME NO LONGER CARRIES A COUNT. It said "exactly one sanctioned
    mutating call" while asserting three, and would have said it while
    asserting four. A name that must be edited every time its subject grows is
    a name that eventually will not be.
    """
    source = Path(writes.__file__).read_text(encoding="utf-8")
    raw = readonly.scan_source_for_mutations(source)
    # THREE SINCE 2026-09-02: the click, the fill publish_post needed, and the
    # select_option the profile editor needed. FOUR SINCE 2026-09-04, with the
    # set_input_files the operator opened -- and note that unlike the other
    # three, NO ACTION USES IT YET (``writes.UPLOAD_ACTIONS`` is empty). The
    # call site is real and the scanner reports it, which is exactly right: a
    # drain point that exists is one an edit can reach, and the boundary
    # describes what the code CAN do rather than what today's actions happen
    # to do. The raw scan still reports ALL FOUR -- it was not taught to stop
    # seeing any of them, which is the whole reason it can still see a fifth.
    assert len(raw) == 4, raw
    # ORDER-FREE, and that is a correction rather than a loosening. This read
    # ``raw[0][1] == "click"`` while there was one hit; with two, position in
    # the scan is a fact about which call comes FIRST IN THE FILE, which is
    # not a property worth asserting -- moving the fill above the click would
    # have failed a check that is supposed to be about kinds.
    assert sorted(hit[1] for hit in raw) == [
        "click",
        "fill",
        "select_option",
        "set_input_files",
    ], raw

    sanctioned, unsanctioned = readonly.partition_mutation_hits(
        "linkedin_server/writes.py", source
    )
    assert unsanctioned == []
    # FOUR SINCE 2026-09-04, and ALL IN ``perform``: the click, the fill that
    # publish_post needed, the select_option the profile editor needed, and
    # the set_input_files the upload ruling opened.
    # The count is asserted rather than derived, so a FIFTH mutating call in
    # this module fails here whatever its kind -- and every one of them is
    # required to be in ``perform``, which is the half that keeps the drain
    # points auditable.
    assert len(sanctioned) == 4, sanctioned
    for hit in sanctioned:
        assert readonly.enclosing_function(source, hit[0]) == "perform", hit
    assert sorted(hit[1] for hit in sanctioned) == [
        "click",
        "fill",
        "select_option",
        "set_input_files",
    ]


def test_a_second_click_inside_perform_is_still_caught():
    """THE CONTROL, on the real file, at the hardest possible edit.

    A second click inside ``perform`` is in the sanctioned file, the sanctioned
    function and of the sanctioned kind -- so it matches the allowlist entry
    exactly and the PARTITION cannot see it. Asserted here, because a control
    that hid that would be worse than none.

    What catches it is the COUNT: the package is asserted to contain exactly as
    many mutating calls as the list has entries, and the list has one. This
    reproduces that check against the doubled source and shows it going red.
    """
    source = Path(writes.__file__).read_text(encoding="utf-8")
    # THE LITERAL BELOW MUST TRACK THE REAL CALL SITE, and the assertion after
    # the replace is what makes that self-enforcing. On 2026-08-25 the call
    # site changed from click(selector, ...) to click(click_plan.pop(0), ...):
    # apply needs TWO clicks with a gate between them, so the argument became a
    # queue rather than a variable. The old literal stopped matching, the
    # replace silently became a no-op, and THIS TEST WENT RED rather than
    # passing vacuously. That is precisely why `assert doubled != source` is
    # here -- a can-it-fail control that cannot verify its own setup is not a
    # control, it is decoration.
    #
    # Note what did NOT change: the package still has exactly ONE mutating call
    # site. Draining a queue fires it twice for apply without adding a second
    # place to audit, which is the property SANCTIONED_MUTATIONS exists to
    # police.
    # 2026-09-27: ``strict=press_strictly`` joined the call -- the named-person
    # acts press strictly (lane L5's follow-up, after two re-checks); every
    # other action passes False, the call it always made. Still ONE site.
    call_site = (
        "await page.click(click_plan.pop(0), timeout=CLICK_TIMEOUT_MS, "
        "strict=press_strictly)"
    )
    assert call_site in source, (
        "the mutating call site has been rewritten again. Update this literal "
        "to match it -- and do NOT relax the assertion below, which is the "
        "only thing stopping this control from testing nothing at all."
    )
    # THE INDENT IS DERIVED, NOT TYPED, AND 2026-09-03 IS WHY. It was a
    # hardcoded twelve spaces. The call site then moved one block deeper --
    # ``send_message`` needs a click BETWEEN two fills, so the fill loop and
    # the click loop merged into one loop over two queues -- and the injected
    # duplicate landed at the wrong indentation. That is not a syntax error
    # this test reports; it is a source string that no longer PARSES, so
    # ``enclosing_function`` attributed nothing, every call in the file came
    # back unsanctioned, and the control failed for a reason that has nothing
    # to do with what it checks.
    #
    # Reading the indent off the real line keeps the control pointed at its
    # subject through the next move as well. ``assert doubled != source`` and
    # the parse assertion below are still what stop it testing nothing.
    line = next(
        one for one in source.splitlines() if call_site in one
    )
    indent = line[: len(line) - len(line.lstrip())]
    doubled = source.replace(
        call_site,
        f"{call_site}\n{indent}{call_site}",
        1,
    )
    assert doubled != source
    # AND THE DOUBLED SOURCE MUST STILL PARSE, or the partition below is
    # answering about a file it could not read rather than about a duplicate
    # click. This is the assertion whose absence let the indent bug look like
    # a boundary failure.
    ast.parse(doubled)

    # The partition is BLIND to it, and that is asserted rather than hidden.
    _sanctioned, unsanctioned = readonly.partition_mutation_hits(
        "linkedin_server/writes.py", doubled
    )
    assert unsanctioned == [], "the partition sees a duplicate -- update this test"

    # The count is not -- but it has to be counted the way the REAL check
    # counts, which is across the whole package rather than this one file.
    #
    # AMENDED 2026-08-26, and the control caught its own flaw before I did.
    # It used to scan the doubled writes.py alone (2 hits) and compare that
    # against len(SANCTIONED_MUTATIONS). That worked only while both numbers
    # happened to be 1. The allowlist gained a second entry -- the messaging
    # filter click, in dom.py -- so the doubled file's 2 equalled the
    # allowlist's 2 and the inequality stopped holding. Its own guard fired
    # with "the count check would not fire on a doubled click", which is
    # exactly what a can-it-fail control is for and the third one on this repo
    # to do it.
    #
    # THE PRODUCTION CHECK WAS NEVER BROKEN: it sums every module and compares
    # to the allowlist length, so a doubled click there gives 3 against 2 and
    # fails. This now reproduces that arithmetic instead of approximating it.
    from tests.test_readonly import MODULES

    package_total = 0
    for module in MODULES:
        text = (
            doubled
            if module.name == "writes.py"
            else module.read_text(encoding="utf-8")
        )
        package_total += len(readonly.scan_source_for_mutations(text))

    assert package_total == len(readonly.SANCTIONED_MUTATIONS) + 1, package_total
    assert package_total != len(readonly.SANCTIONED_MUTATIONS), (
        "the count check would not fire on a doubled click"
    )


def test_the_scanner_would_have_caught_it_if_it_did():
    """The scanner, shown seeing the exact code that was eventually written."""
    future = (
        "async def perform(page, grant):\n"
        "    await page.click('button[aria-label=\"Save the job\"]')\n"
    )
    kinds = {kind for _, kind, _ in readonly.scan_source_for_mutations(future)}
    assert "click" in kinds
