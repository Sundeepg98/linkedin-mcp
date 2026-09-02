"""The branch that runs when the verification's own READ raised.

``writes.perform`` clicks, and then it reads somewhere else to find out what
the click did. Those two steps are wrapped separately on purpose: the click is
inside its own ``try`` and reports a ``clicked.error``, and the READ is inside
a second ``try`` whose ``except`` arm is the subject of this file. That arm
runs at the one moment in this package where the operator is least able to
work out what happened by himself -- the act has already been performed, it
may not be repeatable, and the surface that was supposed to settle it did not
answer at all.

NOTHING IN THE SUITE HAD EVER EXERCISED IT DELIBERATELY. Grepping ``tests/``
for the sentence it prints, ``"read itself failed"``, returned nothing before
this file existed. One test did reach it as a side effect --
``tests/test_apply_modal_fixture.py::test_a_proceeding_gate_appends_the_second_click``
serves no Applied tab, so the read raises -- but it asserts only
``performed is not True`` and never looks at what the receipt SAYS. So every
string in that arm was unread by any test, which is the exact condition under
which a sentence can be wrong for months.

WHAT IT SAID WRONG, and what it says now. ``state_landed`` used to be assigned
a url in this arm: ``FOLLOWED_PAGES_URL`` for ``unfollow_company``,
``APPLIED_LIST_URL`` for ``apply_job``, and ``SAVED_LIST_URL`` for EVERYTHING
ELSE -- so nine actions were sent to the saved-jobs list, and the url was
reported under ``verification.read_from``, a field whose entire job is saying
where the answer was READ FROM. On this path nothing was read anywhere. A url
in that field is a claim that a read happened there, and it was false in every
one of the eleven cases: the arm only runs BECAUSE the read raised.

THE CORRECTION HAS TWO HALVES AND THIS FILE COVERS BOTH.

  1. ``read_from`` IS NOW THE EMPTY STRING. Empty is not a degraded url and it
     is not a missing value -- it is the accurate answer to "which surface
     produced this reading", when the answer is "none, because the read never
     landed". Every assertion below states that in its own docstring rather
     than asserting ``== ""`` bare, because a bare equality against an empty
     string is exactly the shape a future reader mistakes for an oversight and
     "fixes" by putting the url back.

  2. THE PLACE A HUMAN GOES IS A DIFFERENT QUESTION and is answered
     separately, in words, by ``writes._where_to_look`` over the module-level
     table ``writes._WHERE_TO_LOOK``. It is a phrase and not a url because
     three of these places have no address this server may print --
     ``send_invitation``'s Sent Invitations manager sits behind a url carrying
     a substring on ``readonly._FORBIDDEN_URL_SUBSTRINGS`` -- and because the
     reader is a person who can open a page this server may not.

TWO ACTIONS WITH TWO DIFFERENT PHRASES IS THE WHOLE POINT of Part 1. A single
action would pass identically against the old code, which printed one sentence
for nine of them; only a pair whose phrases DIFFER can tell the table apart
from the else it replaced. ``apply_job`` gets "the Applied tab of your job
tracker" and ``save_job`` gets "your saved jobs", and each test asserts that
its own phrase is present AND that no other action's phrase is.

THE EXCEPTION HERE IS REAL AND IS NOT MONKEYPATCHED. Nothing in this file
replaces ``_verify_after``, and nothing fakes an exception. The read is made to
raise by WITHHOLDING the page it navigates to: ``FixtureNavigator.goto``
raises ``AssertionError`` for any url the test did not freeze, which is the
mechanism ``tests/test_apply_modal_fixture.py`` already documents beside its
Applied-tab fixture ("Without it the navigator has no page for that url, the
verification read RAISES"). Every test below PROVES that is what happened, by
asserting the exception's own class name and the navigator's own refusal text
inside ``verification.why`` -- so a future monkeypatched substitute cannot
quietly take this file's place while it goes on passing.

NOTHING HERE REACHES LINKEDIN OR AN ACCOUNT. The pages are the frozen captures
already in ``tests/fixtures``, served into a local headless Chromium by the
navigator from ``tests/test_writes.py``.
"""

from __future__ import annotations

from linkedin_server import writes
from tests.test_writes import (  # noqa: F401 - three of these are fixtures
    JOB,
    SAVED_JOB,
    _granted,
    _no_grants_survive_a_test,
    _perform,
    browser_page,
    writes_on,
)

#: THE TABLE AS THE MODULE SHIPS IT, snapshotted at import.
#:
#: Part 2 monkeypatches ``writes._WHERE_TO_LOOK``, so a test that read the live
#: attribute to work out what the OTHER actions say would be reading its own
#: mutation and comparing the receipt against itself. That is the shape of a
#: control that cannot fail. This copy is the unmutated reference every
#: comparison below is made against.
_REAL_WHERE_TO_LOOK: dict[str, str] = dict(writes._WHERE_TO_LOOK)

#: The stem of the sentence, split out because three tests assert it and one
#: asserts it survives a mutation. Reproduced from ``writes.perform``'s except
#: arm rather than paraphrased: a paraphrase here would pass while the receipt
#: said something else.
RAISED_STEM = "the verification read itself failed"
SAYS_NOTHING = "so this says nothing about whether the click landed"
NOT_AN_EMPTY_READING = (
    "nothing was read anywhere -- this is not a reading that came back empty"
)
NO_SURFACE_STEM = "AND THIS SERVER CANNOT TELL YOU WHERE TO LOOK"
NO_SURFACE_GAP = (
    "That is a gap in this package, not a statement that no surface exists"
)

#: The url each action's verification navigates to, and therefore the page a
#: test WITHHOLDS to make that read raise. Read off ``writes`` rather than
#: typed, so a moved surface fails here loudly instead of leaving a test that
#: withholds a page nobody asks for.
WITHHELD_SURFACE: dict[str, str] = {
    "apply_job": writes.APPLIED_LIST_URL,
    "save_job": writes.SAVED_LIST_URL,
}


def _phrases_of_other_actions(action: str) -> set[str]:
    """Every OTHER action's phrase, minus any that legitimately reads the same.

    THE CARVE-OUT IS BY VALUE AND NOT BY A HAND-WRITTEN PAIR LIST. Two pairs
    share a phrase as of 2026-09-02 -- ``save_job``/``unsave_job`` both say
    "your saved jobs", and ``follow_company``/``unfollow_company`` both say
    "your followed companies" -- and in both cases that is correct rather than
    an inherited else: the two halves of a toggle really are settled by looking
    at the same list. Excluding by equality means a THIRD action that started
    borrowing one of those sentences would be excluded too, which would be a
    hole; so the callers below additionally assert this set is non-empty, which
    is what keeps the check from passing on a receipt that says anything at
    all.
    """
    mine = _REAL_WHERE_TO_LOOK[action]
    return {
        phrase
        for other, phrase in _REAL_WHERE_TO_LOOK.items()
        if other != action and phrase != mine
    }


async def _receipt_with_the_read_withheld(page, action: str, *, target: str):
    """Drive preview -> consume -> perform with the verification's page absent.

    The real chain, the long way round: ``_granted`` runs the gate and burns
    the token it printed, and ``_perform`` runs the real ``perform`` over a
    navigator holding ONLY the posting. The surface ``_verify_after`` wants is
    deliberately not frozen, so the read raises where it reads rather than
    being intercepted anywhere.

    Both assertions below are about the MECHANISM rather than the receipt, and
    they are here rather than in each test because a mechanism that quietly
    changed would leave three tests passing for the wrong reason: the first
    fails if the page turns out to be served after all, the second fails if the
    verification never asked for it, and between them the only way to reach the
    return statement is a read that was attempted and could not be answered.

    Returns ``(block, navigator)``.
    """
    grant = await _granted(page, action, target=target)
    block, nav = await _perform(page, grant)

    withheld = WITHHELD_SURFACE[action]
    assert withheld not in nav.pages, (
        f"{withheld!r} was frozen after all, so the verification could read "
        "and this test proves nothing about the arm that runs when it cannot."
    )
    assert withheld in nav.gotos, (
        "the verification never asked for "
        f"{withheld!r}, so whatever raised was not the read this file is "
        f"about. gotos={nav.gotos}"
    )
    return block, nav


def _assert_the_exception_was_real(why: str, action: str) -> None:
    """Pin that the raise came from a WITHHELD page, not from a fake.

    A monkeypatched ``_verify_after`` would reach the same arm and print the
    same stem, and a reader could not tell the two apart from a green run. The
    navigator's refusal has a signature -- it is an ``AssertionError`` and its
    message names the url it was asked for and did not have -- and the arm
    interpolates ``type(exc).__name__`` and ``exc`` verbatim, so that signature
    survives into the receipt and can be asserted on.
    """
    assert f"{RAISED_STEM} (AssertionError:" in why, why
    assert "which this test did not freeze" in why, why
    assert WITHHELD_SURFACE[action] in why, why


# ---------------------------------------------------------------------------
# Part 1. The branch, reached for real, for two actions with different places
# ---------------------------------------------------------------------------


async def test_an_apply_whose_verification_could_not_read_names_the_applied_tab(
    writes_on, browser_page
):
    """The irreversible one, and the reason this arm's wording matters at all.

    ``apply_job`` is the action in this package that cannot be taken back, and
    this is the receipt he reads when the server has just pressed a submit and
    then failed to find out whether it took. Until 2026-08-31 this arm sent him
    to ``SAVED_LIST_URL`` -- a tab whose three readings are ``saved`` /
    ``not_saved`` / ``unknown`` and which therefore cannot settle an
    application no matter how long he looks at it.

    ``read_from`` MUST BE EMPTY HERE and a url would be a false claim. The
    field answers "which surface produced this reading". This arm exists
    because the read RAISED, so no surface produced anything; printing
    ``APPLIED_LIST_URL`` there would tell him the Applied tab was consulted,
    and the Applied tab is exactly what was never reached. Empty is the fact.

    The place to GO is answered separately and in words -- "the Applied tab of
    your job tracker" -- which is a sentence for a human rather than an address
    for this server.
    """
    action = "apply_job"
    block, _nav = await _receipt_with_the_read_withheld(
        browser_page, action, target=JOB
    )
    verification = block["verification"]
    why = verification["why"]

    _assert_the_exception_was_real(why, action)
    assert verification["read_from"] == "", (
        "read_from carried a url on a path where nothing was read anywhere. "
        "That field says where the answer came from; there is no answer. "
        f"read_from={verification['read_from']!r}"
    )
    assert SAYS_NOTHING in why, why
    assert NOT_AN_EMPTY_READING in why, why

    mine = _REAL_WHERE_TO_LOOK[action]
    assert mine == "the Applied tab of your job tracker", (
        "the phrase this test was written against has moved. Re-read the row "
        "and decide whether the new sentence is right before editing this."
    )
    assert f"Open {mine} and look." in why, why

    others = _phrases_of_other_actions(action)
    assert others, (
        "no other action has a distinct phrase, so the check below cannot "
        "fail and this test is asserting nothing about which sentence it got."
    )
    for phrase in sorted(others):
        assert phrase not in why, (
            f"the apply receipt carried {phrase!r}, which belongs to another "
            "action. That is the inherited-else defect this table replaced."
        )

    assert block["performed"] is not True, (
        "a verification that could not read reported a POSITIVE verdict. This "
        "is the assertion that matters most in this file: the only evidence "
        "for 'it happened' is a reading, and there was no reading."
    )


async def test_a_save_whose_verification_could_not_read_names_the_saved_jobs(
    writes_on, browser_page
):
    """The second action, and it exists to prove the sentence is not constant.

    A one-action version of this file would pass byte-identically against the
    OLD code, because the old else printed the saved-jobs surface for nine of
    the eleven actions -- ``save_job`` among them. So a save alone cannot tell
    a table lookup from the fall-through it replaced. It can only do that
    beside an action whose phrase DIFFERS, which is why the apply test above is
    its pair and why each of the two asserts the other's phrase is absent.

    ``read_from`` MUST BE EMPTY HERE for the same reason as above: the arm runs
    only when the read raised, so no surface was read, and ``SAVED_LIST_URL``
    in that field would be a claim that LinkedIn's own saved list had been
    consulted and had answered.

    NOTE WHAT IS DELIBERATELY NOT ASSERTED: that ``performed`` is ``False``. A
    click that raised on the way out may still have dispatched, and a click
    that returned cleanly may still have changed nothing. Here the reading that
    would decide between them never happened, so ``unknown`` is the honest
    verdict and ``True`` is the only forbidden value.
    """
    action = "save_job"
    block, _nav = await _receipt_with_the_read_withheld(
        browser_page, action, target=SAVED_JOB
    )
    verification = block["verification"]
    why = verification["why"]

    _assert_the_exception_was_real(why, action)
    assert verification["read_from"] == "", (
        "read_from carried a url on a path where nothing was read anywhere. "
        f"read_from={verification['read_from']!r}"
    )
    assert SAYS_NOTHING in why, why
    assert NOT_AN_EMPTY_READING in why, why

    mine = _REAL_WHERE_TO_LOOK[action]
    assert mine == "your saved jobs", (
        "the phrase this test was written against has moved. Re-read the row "
        "and decide whether the new sentence is right before editing this."
    )
    assert f"Open {mine} and look." in why, why

    others = _phrases_of_other_actions(action)
    assert others, (
        "no other action has a distinct phrase, so the check below cannot fail."
    )
    for phrase in sorted(others):
        assert phrase not in why, (
            f"the save receipt carried {phrase!r}, which belongs to another "
            "action."
        )

    assert block["performed"] is not True, (
        "a verification that could not read reported a POSITIVE verdict."
    )


async def test_the_two_receipts_do_not_print_the_same_place(
    writes_on, browser_page
):
    """The pair, compared directly, because two green tests are not a contrast.

    Each test above proves its own receipt carries its own phrase and none of
    the others. Neither of them, alone or together, states the thing the change
    was made FOR: that these two actions get DIFFERENT sentences out of the
    same arm. Asserting the inequality here says it once, in one place, against
    two receipts produced by the same code path in the same session.

    This is the check that goes red if the table is ever collapsed back to a
    default -- including a default that happens to be spelled correctly for one
    of these two, which is precisely the shape the old code had.
    """
    apply_block, _ = await _receipt_with_the_read_withheld(
        browser_page, "apply_job", target=JOB
    )
    save_block, _ = await _receipt_with_the_read_withheld(
        browser_page, "save_job", target=SAVED_JOB
    )

    apply_why = apply_block["verification"]["why"]
    save_why = save_block["verification"]["why"]

    assert _REAL_WHERE_TO_LOOK["apply_job"] != _REAL_WHERE_TO_LOOK["save_job"], (
        "the two rows now say the same thing, so this comparison cannot fail. "
        "Pick a different pair rather than deleting the test."
    )
    assert _REAL_WHERE_TO_LOOK["apply_job"] in apply_why
    assert _REAL_WHERE_TO_LOOK["apply_job"] not in save_why
    assert _REAL_WHERE_TO_LOOK["save_job"] in save_why
    assert _REAL_WHERE_TO_LOOK["save_job"] not in apply_why

    assert apply_block["performed"] is not True
    assert save_block["performed"] is not True


# ---------------------------------------------------------------------------
# Part 2. The mutations, because an assertion nobody has seen fail proves
#         nothing about the code it points at
# ---------------------------------------------------------------------------


async def test_pointing_apply_at_the_save_phrase_makes_the_wrong_place_check_fire(
    writes_on, browser_page, monkeypatch
):
    """MUTATION 1: the borrowed-sentence defect, planted and caught.

    The check in Part 1 -- "the receipt contains no OTHER action's phrase" --
    is the one that would have caught the original defect, where nine actions
    printed the saved-jobs sentence out of a shared else. An assertion of that
    shape is also the easiest kind to write vacuously: if the phrases were
    substrings of one another, or if the set of others came out empty, it would
    pass forever on a receipt saying anything at all.

    So the defect is put back, in the smallest possible form: ``apply_job``'s
    row is repointed at ``save_job``'s phrase and nothing else changes. The
    receipt then carries "your saved jobs" for an application, which is
    precisely the sentence that sent him to a tab that cannot settle an apply
    -- and the assertion here is that this is now DETECTABLE, not merely that
    the mutation was accepted.

    THE TABLE IS COPIED, NEVER EDITED IN PLACE. ``monkeypatch.setattr``
    rebinds the module attribute to a new dict, so the real table is untouched
    and ``tests/test_receipt_names_its_own_action.py``, which walks every
    performable action's row, is unaffected in the same session.
    """
    action = "apply_job"
    borrowed = _REAL_WHERE_TO_LOOK["save_job"]
    assert borrowed != _REAL_WHERE_TO_LOOK[action], (
        "the two rows already agree, so this mutation changes nothing and "
        "cannot demonstrate anything."
    )

    mutated = dict(_REAL_WHERE_TO_LOOK)
    mutated[action] = borrowed
    monkeypatch.setattr(writes, "_WHERE_TO_LOOK", mutated)

    block, _nav = await _receipt_with_the_read_withheld(
        browser_page, action, target=JOB
    )
    why = block["verification"]["why"]

    _assert_the_exception_was_real(why, action)

    # THE CHECK FIRING, expressed as the thing Part 1 asserts being FALSE now.
    # Part 1 says every phrase in this set is absent; here exactly one of them
    # is present, which is the same statement with the sign flipped.
    others = _phrases_of_other_actions(action)
    present = sorted(phrase for phrase in others if phrase in why)
    assert present == [borrowed], (
        "the borrowed phrase did not reach the receipt, so the Part 1 check "
        "would have stayed green through this mutation and is not testing "
        f"what it claims to. present={present!r}"
    )

    # AND THE RIGHT SENTENCE IS GONE, which is the other half of the damage:
    # the receipt does not merely gain a wrong place, it loses the real one.
    assert _REAL_WHERE_TO_LOOK[action] not in why, why
    assert block["performed"] is not True


async def test_deleting_the_row_makes_the_receipt_say_it_cannot_tell_him(
    writes_on, browser_page, monkeypatch
):
    """MUTATION 2, and it is the ONLY execution the ``None`` arm ever gets.

    ``_where_to_look`` returns ``Optional[str]`` and the except arm branches on
    it, so there are two sentences in that arm and only one of them is
    reachable while every performable action has a row. Every action does have
    one today -- ``tests/test_receipt_names_its_own_action.py`` fails if one
    goes missing -- which means the ``None`` sentence is unreachable in
    production AND unrunnable by any ordinary test. Deleting a row is therefore
    not a trick to make an assertion fire; it is the only way that branch runs
    at all, and this repo's standing rule is that a branch which has never been
    shown running certifies nothing.

    WHAT THE ARM MUST SAY, and why each clause is asserted separately:

      * it must state plainly that this SERVER cannot tell him where to look --
        not that there is nowhere to look. Those are different sentences and
        only one of them is true;
      * it must name the action whose row is missing, so the gap is
        attributable rather than atmospheric;
      * it must call it a gap in THIS PACKAGE, which is the difference between
        an admission and a claim about LinkedIn;
      * and it must issue no "Open ... and look" instruction, because a missing
        row may not borrow a neighbour's. A default here would send him to a
        page that cannot answer his question, which is strictly worse than no
        sentence: he reads it, opens it, sees nothing, and concludes something
        about an irreversible act from the silence of a surface that was never
        going to speak.
    """
    action = "apply_job"
    mutated = dict(_REAL_WHERE_TO_LOOK)
    del mutated[action]
    monkeypatch.setattr(writes, "_WHERE_TO_LOOK", mutated)

    assert writes._where_to_look(action) is None, (
        "the row was deleted and the lookup still answered, so this arm is "
        "reached through something other than the table and the deletion "
        "cannot exercise the None branch."
    )

    block, _nav = await _receipt_with_the_read_withheld(
        browser_page, action, target=JOB
    )
    why = block["verification"]["why"]

    _assert_the_exception_was_real(why, action)
    assert block["verification"]["read_from"] == "", (
        "read_from carried a url on a path where nothing was read anywhere."
    )

    assert NO_SURFACE_STEM in why, why
    assert f"no surface is recorded for {action!r}" in why, why
    assert NO_SURFACE_GAP in why, why

    # NO INSTRUCTION, ASSERTED TWO WAYS. "Open " alone would be satisfied by a
    # sentence that merely avoided the word, and " and look." alone by one that
    # named a place without an imperative; together they cover the shape of the
    # arm that was NOT taken.
    assert "Open " not in why, (
        "the no-surface arm still issued an Open instruction, which means a "
        f"missing row borrowed a sentence from somewhere. why={why!r}"
    )
    assert " and look." not in why, why

    # AND IT BORROWED NOBODY'S PHRASE, which is the failure mode a default
    # would produce and the one the two assertions above exist to exclude.
    for phrase in sorted(set(_REAL_WHERE_TO_LOOK.values())):
        assert phrase not in why, (
            f"a receipt with no row of its own carried {phrase!r}."
        )

    assert block["performed"] is not True, (
        "an action with no recorded surface and no reading at all still "
        "reported a positive verdict."
    )
