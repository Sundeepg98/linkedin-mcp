"""The receipt must name ITS OWN action's evidence, and never another's.

WHAT THIS GUARDS, AND THE MEASUREMENT THAT PUT IT HERE. ``writes.perform``
returns ONE receipt dict. Until 2026-09-02, five of its fields were chosen by
``if``/``elif`` chains over ``spec.action`` or ``spec.target_kind``, and each
chain ended in an ``else`` carrying text written for the ORIGINAL four job and
company actions. Seven more actions were added over the weeks that followed and
every one of them silently inherited that else. Measured across the five chains
before the repair:

    **8 of the 11 performable actions carried at least one field whose text
    was written for a different action.**

The three clean ones -- ``save_job``, ``unsave_job``, ``unfollow_company`` --
are precisely the actions the chains were written for, which is the signature
of an inherited else rather than of a bad row.

THREE COUNTS FROM THAT SAME MEASUREMENT, because they name the shapes:

* **10 of 11** were sent to HIS SAVED JOBS by ``read_this_if_unsure``. An
  apply, a post, a comment, an invitation, a profile edit and a dark-mode
  change were each told to go and look at a jobs list. Sending him to the
  wrong page to check is how a correct instruction becomes useless.
* **6 of 11** printed the save pair's ``verification.surface`` sentence -- "a
  DIFFERENT surface ... LinkedIn's own saved list with its own per-tab count"
  -- which for all six named evidence that does not exist. One of the six was
  ``publish_post``, whose spec DECLARES that nothing can confirm it: the one
  action in the package that must never claim a confirming surface claimed the
  strongest one in it.
* the toggle warning, "a retry on a toggle that did land performs the opposite
  action", was printed on **all 11** and is true of **5**. On ``apply_job`` it
  does not merely fail to apply, it MISDESCRIBES THE DANGER IN THE SAFER
  DIRECTION: a retry there may file a second application rather than undo the
  first.

Live on one real ``publish_post`` receipt, the post's own text also came back
under the key ``company_id``.

WHY A GREEN SUITE WAS NOT EVIDENCE OF ANY OF THIS. The suite stood at 2534
tests, passing, on the morning the defect was measured. Not one of them read a
receipt field. The defect was never a broken assertion; it was an ABSENT one.
The repair replaced three of those chains with module-level tables in
``writes.py`` -- ``_WHERE_TO_LOOK``, ``_VERIFIED_FROM``, ``_TOGGLE_ACTIONS`` --
and a table is not inherently safer than an if/elif chain. It is only easier to
ENUMERATE. This file is that enumeration, and without it the tables would be
exactly as untested as the chains they replaced.

WHAT IT ASSERTS, IN THREE LAYERS:

1. **COMPLETENESS**, iterated over ``writes.PERFORMABLE`` rather than over a
   list of action names kept here. That iteration is the whole mechanism: all
   seven of the inheriting actions were added to ``PERFORMABLE`` and to
   nothing else, so any check written against a hand-kept list would have gone
   on passing while the receipt went on lying. A twelfth action fails this
   file until somebody writes its rows.

2. **NO ACTION MAY NAME ANOTHER ACTION'S EVIDENCE.** Surface-specific phrases
   are OWNED, and the owners are stated per phrase. This is the layer that
   catches the real defect, because a borrowed row is COMPLETE: it passes
   every completeness check there is and reads as a confident sentence about
   a surface nothing looked at.

3. **THE MUTATION DEMONSTRATIONS**, below, one per distinct shape of the
   defect. This repo's standing rule is that AN INSTRUMENT ENTERS THE REGISTER
   ONLY IF IT HAS BEEN SHOWN FAILING, and one demonstration proves only that a
   check can fire -- it says nothing about what the check is silent on. So the
   shapes are enumerated and one of each is mutated: a MISSING row, a BLANK
   row, a BORROWED ``_VERIFIED_FROM`` text, an action with NEITHER a row nor a
   declaration, an action with BOTH, a ``_WHERE_TO_LOOK`` value borrowed
   verbatim, the same borrowed as a SUBSTRING of a different sentence, and a
   twelfth action arriving with no rows at all. Every mutation is applied with
   ``monkeypatch`` to a COPY, so the shipped tables are never touched, and
   each asserts that the check fires AND that the message names the offender.

HOW THE PHRASES BELOW WERE DERIVED. By reading the shipped ``_VERIFIED_FROM``
and ``_WHERE_TO_LOOK`` values and measuring which actions each candidate phrase
occurs in -- not by guessing what a surface ought to be called. Five candidates
were measured and REJECTED as non-discriminators, and they are recorded here
because a rejected candidate is the part of this that a future reader would
otherwise re-propose:

* ``"a DIFFERENT surface"`` occurs in THREE rows -- ``save_job``,
  ``unsave_job``, ``apply_job`` -- and legitimately: those are the three
  actions verified from a surface other than the one clicked. It describes the
  STRENGTH CLASS of the evidence, not the surface, so it cannot discriminate
  between actions and is not used as one.
* ``"THE SAME PAGE, RELOADED"`` occurs in three rows for the same reason, one
  strength class down.
* ``"per-tab count"`` occurs in three rows: the saved list has one and the
  tracker's tabs have one. Two different surfaces, one true noun.
* ``"weakest"`` occurs in the save pair's rows and, in upper case, in
  ``follow_company``'s. All three are honestly describing how weak their
  evidence is.
* the bare word ``"saved"`` is NOT a save-family discriminator, and this one is
  a trap worth naming: ``apply_job``'s row contains "the SAVED tab", because
  it tells the story of the 2026-08-31 defect where the apply verification
  read the wrong tab. A check owning ``"saved"`` would fire on a correct row.
  ``"saved list"`` is the discriminator; ``"saved"`` is not.

NOTHING HERE LAUNCHES A BROWSER, READS A FIXTURE, OR REACHES LINKEDIN. It is a
statement about three dictionaries, one function, and one string literal in
``writes.py``, read out of the module and out of its AST. ``linkedin_server/``
is not modified by this file.
"""

from __future__ import annotations

import ast
import dataclasses
from collections import defaultdict
from typing import Iterable, Mapping

import pytest

from linkedin_server import writes

_SOURCE = open(writes.__file__, encoding="utf-8").read()
_TREE = ast.parse(_SOURCE)

#: SNAPSHOTS TAKEN AT IMPORT, and they exist for the mutation tests rather than
#: for the assertions. Every mutation below replaces a module attribute with a
#: COPY; each then asserts against these snapshots that the shipped table still
#: holds the row it deleted or overwrote. A mutation that leaked into the real
#: table would poison every test that ran after it, in an order-dependent way
#: that is very hard to read backwards from a failure.
_REAL_WHERE_TO_LOOK: dict[str, str] = dict(writes._WHERE_TO_LOOK)
_REAL_VERIFIED_FROM: dict[str, str] = dict(writes._VERIFIED_FROM)


# ---------------------------------------------------------------------------
# The ownership tables. Derived by measurement -- see the module docstring.
# ---------------------------------------------------------------------------

#: SURFACE-SPECIFIC PHRASES IN ``_VERIFIED_FROM``, mapped to the ONLY actions
#: entitled to print them. Matching is case-insensitive, and that is safe
#: rather than lax: every phrase here was measured to have the SAME owners
#: case-insensitively as it has exactly, so caselessness costs no precision
#: today and catches a row copied and re-cased tomorrow.
#:
#: A phrase names a SURFACE, or a mechanism unique to one surface. It never
#: names a strength class -- the rejected candidates in the module docstring
#: are all strength classes, and a strength class is shared by construction.
_VERIFIED_FROM_OWNERS: dict[str, frozenset[str]] = {
    # LinkedIn's saved list. The save pair reads it; nothing else may say it
    # did. This is the exact sentence six actions inherited.
    "saved list": frozenset({"save_job", "unsave_job"}),
    # The job tracker's APPLIED tab, and the tracker itself. Only an apply is
    # verified there.
    "APPLIED tab": frozenset({"apply_job"}),
    "tracker": frozenset({"apply_job"}),
    # The one surface on which LinkedIn lists followed Pages.
    # ``follow_company`` is deliberately NOT an owner: its verification reads
    # the control it just clicked and its row says so in words, so a row of
    # its own naming this page would be a claim it did not earn.
    "followed Pages": frozenset({"unfollow_company"}),
    # The dark-mode radio group: LinkedIn's own ``checked`` property read
    # across a group of three inputs.
    "checked property": frozenset({"update_setting"}),
    "group of three": frozenset({"update_setting"}),
}

#: THE SAME, FOR ``_WHERE_TO_LOOK``. These values are short phrases rather
#: than sentences, so the owned strings are the nouns of the place itself.
#:
#: TWO PAIRS SHARE LEGITIMATELY and are encoded as two-owner phrases rather
#: than by weakening the check. ``save_job``/``unsave_job`` both settle in the
#: saved list. ``follow_company``/``unfollow_company`` both point at the
#: followed-companies page, and that is deliberate: ``_verify_after``'s follow
#: branch already ends "Open your followed companies if you want a second
#: opinion", and this field is that sentence in the place built for it.
#:
#: ``"the post"`` has two owners for a third reason -- ``react_to_item`` and
#: ``comment_on_item`` act on the same class of surface, an item permalink.
#: ``publish_post`` is NOT an owner: its answer is on his profile's activity
#: rail, which is a different page, and a row pointing a publish at a post
#: permalink is the shape this whole file exists to catch.
_WHERE_TO_LOOK_OWNERS: dict[str, frozenset[str]] = {
    "saved jobs": frozenset({"save_job", "unsave_job"}),
    "followed companies": frozenset({"follow_company", "unfollow_company"}),
    "Applied tab": frozenset({"apply_job"}),
    "job tracker": frozenset({"apply_job"}),
    "dark-mode": frozenset({"update_setting"}),
    "profile editor": frozenset({"update_profile_field"}),
    "recent activity": frozenset({"publish_post"}),
    "My Network": frozenset({"send_invitation"}),
    "the post": frozenset({"react_to_item", "comment_on_item"}),
}

#: THE ONLY SETS OF ACTIONS ALLOWED TO SHARE A ``_WHERE_TO_LOOK`` VALUE
#: EXACTLY. Encoded as the sharing groups themselves rather than as a count or
#: an exemption flag, so that a THIRD action joining either group fails: the
#: group is compared for equality, not for containment.
_LEGITIMATE_SHARED_PLACES: frozenset[frozenset[str]] = frozenset(
    {
        frozenset({"save_job", "unsave_job"}),
        frozenset({"follow_company", "unfollow_company"}),
    }
)

#: A NAME NO ACTION HAS, for the tests that need to reach a fallback. It is
#: asserted absent from ``PERFORMABLE`` before it is used, so a future action
#: that happened to be called this fails loudly instead of quietly making the
#: fallback tests vacuous.
_SYNTHETIC_ACTION = "an_action_that_was_never_shipped"


# ---------------------------------------------------------------------------
# The checks, factored so the mutation tests can fire the SAME predicate the
# passing tests run. A mutation that fired a different code path would prove
# nothing about the check that guards the tree.
# ---------------------------------------------------------------------------


def declares_unverifiable_map(performable: Iterable[str]) -> dict[str, bool]:
    """``action -> does its spec declare the outcome unconfirmable``.

    Built through the shipped ``writes.spec_for_action`` rather than from a
    list kept here, so that a mutation which swaps ``SANCTIONED_WRITES`` is
    seen by this exactly as the server would see it.
    """
    declares: dict[str, bool] = {}
    for action in sorted(performable):
        try:
            spec = writes.spec_for_action(action)
        except writes.WriteAttemptError as exc:
            raise AssertionError(
                "%r is in writes.PERFORMABLE and has no WriteSpec at all: %s"
                % (action, exc)
            )
        declares[action] = spec.unverifiable is not None
    return declares


def check_every_performable_action_has_a_place_to_look(
    performable: Iterable[str], where_to_look: Mapping[str, str]
) -> None:
    """Every performable action has a NON-EMPTY row in ``_WHERE_TO_LOOK``.

    Two failures, not one, because a row that exists and says nothing passes
    the first check and fails the reader. ``perform`` prints
    ``"Open " + _where_to_look(action) + " and look first."`` whenever the
    lookup is truthy, so a whitespace row ships him the sentence "Open  and
    look first."
    """
    missing = sorted(a for a in performable if a not in where_to_look)
    assert not missing, (
        "no row in writes._WHERE_TO_LOOK for %s. perform() falls back to 'AND "
        "THIS SERVER CANNOT TELL YOU WHERE TO LOOK' for these, which is honest "
        "and useless. Write the row; do NOT let it borrow a neighbour's."
        % missing
    )
    blank = sorted(a for a in performable if not str(where_to_look[a]).strip())
    assert not blank, (
        "the writes._WHERE_TO_LOOK row for %s is empty or whitespace. It is "
        "truthy, so perform() prints 'Open  and look first.' -- worse than the "
        "no-row fallback, which at least says it does not know." % blank
    )


def check_every_performable_action_verifies_or_declares_it_cannot(
    performable: Iterable[str],
    verified_from: Mapping[str, str],
    declares: Mapping[str, bool],
) -> None:
    """EXACTLY ONE of {a ``_VERIFIED_FROM`` row, a declared ``unverifiable``}.

    BOTH DIRECTIONS, because they fail differently and both are live shapes.

    NEITHER is the inheritance defect itself: ``perform`` reaches
    ``_VERIFIED_FROM.get(action, <fallback>)`` for any action whose spec has
    no ``Unverifiable``, so an action with no row prints the NOT RECORDED
    sentence -- honest, but a gap that should be loud at test time rather than
    quiet in a receipt.

    BOTH is dead text that is one edit away from being live. An action
    carrying an ``Unverifiable`` never reaches this table, so a row written for
    it is never printed and never read by anybody checking it -- until the
    branch above it moves, at which point a receipt starts claiming evidence
    for the one class of action that declares it has none. That is the
    ``publish_post`` defect exactly, arriving by a different route.
    """
    actions = sorted(performable)
    uncovered = sorted(a for a in actions if a not in declares)
    assert not uncovered, (
        "no unverifiable declaration could be resolved for %s -- the map "
        "handed to this check does not cover writes.PERFORMABLE." % uncovered
    )
    neither = sorted(
        a for a in actions if a not in verified_from and not declares[a]
    )
    assert not neither, (
        "%s is performable with NO row in writes._VERIFIED_FROM and NO "
        "Unverifiable on its spec. Its receipt will print the NOT RECORDED "
        "fallback: the verification ran and nothing says how strong it is."
        % neither
    )
    both = sorted(a for a in actions if a in verified_from and declares[a])
    assert not both, (
        "%s BOTH declares its outcome unverifiable AND carries a row in "
        "writes._VERIFIED_FROM. perform() takes the declaration branch, so "
        "that row is unreachable text describing evidence that does not "
        "exist -- and it is one branch edit away from being printed." % both
    )
    blank = sorted(
        a
        for a in actions
        if a in verified_from and not str(verified_from[a]).strip()
    )
    assert not blank, (
        "the writes._VERIFIED_FROM row for %s is empty or whitespace, so the "
        "receipt prints an empty 'surface' beside a real verdict." % blank
    )


def check_no_action_names_another_actions_phrase(
    table: Mapping[str, str],
    owners: Mapping[str, frozenset[str]],
    table_name: str,
) -> None:
    """No action's text contains a phrase another action owns.

    THIS IS THE LAYER THAT CATCHES THE ACTUAL DEFECT. A borrowed row is
    COMPLETE -- it is present, non-empty, well written, and confident. Every
    completeness check in this file passes on it. The only thing wrong with it
    is that it describes somebody else's surface, and the only way to detect
    that is to know which surfaces belong to whom.
    """
    trespass: list[tuple[str, str, list[str]]] = []
    for phrase, entitled in sorted(owners.items()):
        for action, text in sorted(table.items()):
            if action in entitled:
                continue
            if phrase.lower() in str(text).lower():
                trespass.append((phrase, action, sorted(entitled)))
    assert not trespass, (
        "writes.%s names another action's evidence. Each entry below is "
        "(phrase, the action printing it, the actions entitled to it): %s. If "
        "the new row is CORRECT and the phrase genuinely applies to it, add "
        "that action to the owner set in this file and say why -- do not "
        "delete the phrase." % (table_name, trespass)
    )


def check_every_owned_phrase_is_still_present(
    table: Mapping[str, str],
    owners: Mapping[str, frozenset[str]],
    table_name: str,
) -> None:
    """The control for the check above: the phrases still exist to be found.

    WITHOUT THIS, A REWRITE EMPTIES THE INSTRUMENT IN SILENCE. If somebody
    rephrases ``save_job``'s row and "saved list" stops appearing anywhere,
    ``check_no_action_names_another_actions_phrase`` keeps passing -- it is
    then searching for a string that no longer exists, which is a check that
    cannot fail. A library of checks that cannot fail manufactures confidence
    at scale, which is the thing this suite is most afraid of.
    """
    absent: list[tuple[str, str]] = []
    for phrase, entitled in sorted(owners.items()):
        for action in sorted(entitled):
            if action not in table:
                absent.append((phrase, "%s (no row at all)" % action))
            elif phrase.lower() not in str(table[action]).lower():
                absent.append((phrase, action))
    assert not absent, (
        "a phrase this file claims is owned no longer appears in its owner's "
        "writes.%s row: %s. The trespass check is now searching for a string "
        "that does not exist and cannot fail. Re-derive the phrase from the "
        "rewritten row." % (table_name, absent)
    )


def check_no_two_actions_share_a_place_by_accident(
    where_to_look: Mapping[str, str],
    legitimate: frozenset[frozenset[str]],
) -> None:
    """Actions sharing a ``_WHERE_TO_LOOK`` value must be a sanctioned group.

    THIS IS THE ORIGINAL DEFECT'S OWN SHAPE. Before the repair, ten of the
    eleven actions carried the identical string "your saved jobs" -- one group
    of ten, which this reports as one line naming all ten.

    Grouping is by EQUALITY of the value, so it says nothing about a borrowed
    phrase inside a longer sentence; that is
    ``check_no_action_names_another_actions_phrase``'s job, and the two are
    demonstrated to be non-redundant below.
    """
    groups: dict[str, set[str]] = defaultdict(set)
    for action, text in where_to_look.items():
        groups[str(text).strip()].add(action)
    unsanctioned = sorted(
        (text, sorted(actions))
        for text, actions in groups.items()
        if len(actions) > 1 and frozenset(actions) not in legitimate
    )
    assert not unsanctioned, (
        "these actions print the IDENTICAL place to look and are not one of "
        "the two groups sanctioned to: %s. The sanctioned groups are the save "
        "pair and the follow pair, and they are compared by equality -- a "
        "third action joining either one fails here too." % unsanctioned
    )


def check_the_tables_name_no_unperformable_action(
    performable: Iterable[str], tables: Mapping[str, Iterable[str]]
) -> None:
    """No table holds a row for an action that cannot be performed.

    The mirror of the completeness check, and it fails on the OTHER edit: an
    action removed from ``PERFORMABLE`` leaves its rows behind, and a stale row
    is how a table starts describing a capability the server no longer has.
    """
    known = set(performable)
    orphans = sorted(
        (name, sorted(set(keys) - known))
        for name, keys in tables.items()
        if set(keys) - known
    )
    assert not orphans, (
        "these tables in writes.py carry rows for actions absent from "
        "writes.PERFORMABLE: %s. Either the action was removed and its rows "
        "were not, or the row is a typo that will never be read." % orphans
    )


def fallback_surface_sentence() -> str:
    """The default argument of ``_VERIFIED_FROM.get`` inside ``perform``.

    READ OUT OF THE AST rather than copied into this file. A copy would be a
    second spelling of a string whose exact wording is the thing under test,
    and the two would drift the first time somebody improved one of them.
    """
    perform_node = None
    for node in ast.walk(_TREE):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "perform":
                perform_node = node
                break
    assert perform_node is not None, "perform() not found in writes.py"

    calls = [
        node
        for node in ast.walk(perform_node)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "get"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "_VERIFIED_FROM"
    ]
    assert len(calls) == 1, (
        "expected exactly one _VERIFIED_FROM.get(...) inside perform(); found "
        "%d. If the lookup moved, this test is reading the wrong string."
        % len(calls)
    )
    args = calls[0].args
    assert len(args) == 2, (
        "_VERIFIED_FROM.get(...) inside perform() no longer passes a default. "
        "Without one a missing row raises KeyError in the middle of a receipt."
    )
    default = args[1]
    assert isinstance(default, ast.Constant) and isinstance(
        default.value, str
    ), (
        "the _VERIFIED_FROM.get default is no longer a plain string literal "
        "(%s), so this test can no longer read what a caller would be told."
        % type(default).__name__
    )
    return default.value


# ---------------------------------------------------------------------------
# Part 1 -- completeness, over writes.PERFORMABLE
# ---------------------------------------------------------------------------


def test_the_action_set_is_the_one_this_file_was_measured_against():
    """A control on the corpus, before anything is asserted about it.

    ELEVEN ACTIONS were performable when the 8-of-11 measurement was taken. If
    that number moves, the counts in this file's docstring are stale AND the
    checks below are covering a different population than the one they were
    written for -- so the number is asserted rather than assumed. A twelfth
    action is not an error in itself; it means the docstring's arithmetic and
    the phrase-ownership tables both want re-deriving, and this is the line
    that says so.
    """
    assert len(writes.PERFORMABLE) == 11, (
        "writes.PERFORMABLE holds %d actions, not the 11 this file was "
        "measured against: %s. Re-derive the phrase owners in this file for "
        "the new action, then update this count."
        % (len(writes.PERFORMABLE), sorted(writes.PERFORMABLE))
    )
    assert _SYNTHETIC_ACTION not in writes.PERFORMABLE


def test_every_performable_action_has_a_place_to_look():
    """Part 1.1 -- ``_WHERE_TO_LOOK`` covers ``PERFORMABLE``, non-empty.

    ITERATED OVER THE FROZENSET, deliberately, so the seventh through eleventh
    actions could not have been added the way they were: to ``PERFORMABLE`` and
    to nothing else. A hand-kept list here would have gone on passing while ten
    of the eleven receipts sent him to his saved jobs.
    """
    check_every_performable_action_has_a_place_to_look(
        writes.PERFORMABLE, writes._WHERE_TO_LOOK
    )


def test_every_performable_action_verifies_or_declares_that_it_cannot():
    """Part 1.2 -- a ``_VERIFIED_FROM`` row XOR a declared ``unverifiable``.

    The pairing between ``_verify_after`` and the spec is asserted next door in
    ``tests/test_unverifiable_outcomes.py``. This is the third leg of the same
    triangle and it was the missing one: whether the RECEIPT can describe the
    evidence for the action it just performed.
    """
    check_every_performable_action_verifies_or_declares_it_cannot(
        writes.PERFORMABLE,
        writes._VERIFIED_FROM,
        declares_unverifiable_map(writes.PERFORMABLE),
    )


def test_the_tables_carry_no_row_for_an_unperformable_action():
    """Part 1.3 -- the mirror direction, over all three new tables.

    ``_TOGGLE_ACTIONS`` is included here and nowhere else in this file. Its
    membership is a claim about REVERSIBILITY rather than about a surface, so
    the phrase machinery has nothing to say about it -- but a stale toggle row
    is the same class of defect as a stale surface row, and the receipt's retry
    warning is built from it.
    """
    check_the_tables_name_no_unperformable_action(
        writes.PERFORMABLE,
        {
            "_WHERE_TO_LOOK": writes._WHERE_TO_LOOK,
            "_VERIFIED_FROM": writes._VERIFIED_FROM,
            "_TOGGLE_ACTIONS": writes._TOGGLE_ACTIONS,
        },
    )


# ---------------------------------------------------------------------------
# Part 2 -- no action may name another action's evidence
# ---------------------------------------------------------------------------


def test_the_owned_phrases_are_still_findable_in_both_tables():
    """The instrument's control, run BEFORE the assertions that use it.

    Both trespass checks below search for fixed strings. If a row is rewritten
    and a phrase disappears, those checks silently become searches for nothing.
    This is what makes them fail loudly instead.
    """
    check_every_owned_phrase_is_still_present(
        writes._VERIFIED_FROM, _VERIFIED_FROM_OWNERS, "_VERIFIED_FROM"
    )
    check_every_owned_phrase_is_still_present(
        writes._WHERE_TO_LOOK, _WHERE_TO_LOOK_OWNERS, "_WHERE_TO_LOOK"
    )


def test_no_action_claims_another_actions_verification_surface():
    """Part 2.1 -- the real check, over ``_VERIFIED_FROM``.

    SIX ACTIONS PRINTED THE SAVE PAIR'S SENTENCE until 2026-09-02 and this is
    the assertion that would have said so: "saved list" is owned by two
    actions, and six others were printing it.
    """
    check_no_action_names_another_actions_phrase(
        writes._VERIFIED_FROM, _VERIFIED_FROM_OWNERS, "_VERIFIED_FROM"
    )


def test_no_action_sends_him_to_another_actions_page():
    """Part 2.2 -- the same check over ``_WHERE_TO_LOOK``.

    TEN OF ELEVEN were sending him to "your saved jobs", which this would have
    reported as eight separate trespasses on a phrase owned by the save pair.
    """
    check_no_action_names_another_actions_phrase(
        writes._WHERE_TO_LOOK, _WHERE_TO_LOOK_OWNERS, "_WHERE_TO_LOOK"
    )


def test_the_only_actions_sharing_a_place_are_the_two_sanctioned_pairs():
    """Part 2.3 -- exact-value sharing, with the legitimate pairs encoded.

    ENCODED RATHER THAN EXEMPTED. "Two actions may share" would pass the
    ten-way collision that started this. The sanctioned groups are compared for
    EQUALITY, so the check still fires if a third action joins one of them.
    """
    check_no_two_actions_share_a_place_by_accident(
        writes._WHERE_TO_LOOK, _LEGITIMATE_SHARED_PLACES
    )


# ---------------------------------------------------------------------------
# Part 3 -- the mutation demonstrations
#
# THE RULE: an instrument enters the register only if it has been SHOWN
# FAILING. One demonstration would prove that one check can fire and would say
# nothing about the rest, so the shapes are enumerated and one of each is
# mutated. Every mutation is applied to a COPY through monkeypatch; each test
# also asserts, against the import-time snapshot, that the shipped table is
# untouched.
# ---------------------------------------------------------------------------


def test_mutation_a_missing_place_to_look_is_caught(monkeypatch):
    """SHAPE 1 of 8 -- a row deleted from ``_WHERE_TO_LOOK``.

    This is what every one of the seven late actions looked like before the
    repair, and it is the shape ``writes.py``'s own comment promises this file
    catches: "fails on any performable action absent from this table".

    It also asserts what the deletion does to the SHIPPED reader --
    ``writes._where_to_look`` returns ``None`` under the mutation -- so the
    demonstration covers the code path and not merely the dictionary.
    """
    mutated = dict(_REAL_WHERE_TO_LOOK)
    del mutated["publish_post"]
    monkeypatch.setattr(writes, "_WHERE_TO_LOOK", mutated)

    assert "publish_post" in _REAL_WHERE_TO_LOOK, "the snapshot was mutated"
    assert writes._where_to_look("publish_post") is None

    with pytest.raises(AssertionError) as caught:
        check_every_performable_action_has_a_place_to_look(
            writes.PERFORMABLE, writes._WHERE_TO_LOOK
        )
    assert "publish_post" in str(caught.value)
    assert "_WHERE_TO_LOOK" in str(caught.value)


def test_mutation_a_blank_place_to_look_is_caught(monkeypatch):
    """SHAPE 2 of 8 -- a row that EXISTS and says nothing.

    Distinct from shape 1 and not covered by it: the key is present, so the
    membership half of the check passes. ``perform`` guards on truthiness, and
    "   " is truthy, so this is the mutation that ships him "Open  and look
    first."
    """
    mutated = dict(_REAL_WHERE_TO_LOOK)
    mutated["apply_job"] = "   "
    monkeypatch.setattr(writes, "_WHERE_TO_LOOK", mutated)

    assert _REAL_WHERE_TO_LOOK["apply_job"].strip(), "the snapshot was mutated"
    assert writes._where_to_look("apply_job") == "   "

    with pytest.raises(AssertionError) as caught:
        check_every_performable_action_has_a_place_to_look(
            writes.PERFORMABLE, writes._WHERE_TO_LOOK
        )
    assert "apply_job" in str(caught.value)
    assert "empty or whitespace" in str(caught.value)


def test_mutation_a_borrowed_verification_sentence_is_caught(monkeypatch):
    """SHAPE 3 of 8 -- THE ORIGINAL DEFECT, reproduced exactly.

    ``react_to_item`` is pointed at ``save_job``'s row, which is what the
    inherited ``else`` did to six actions. The row is present, non-empty, and
    beautifully written; the ONLY thing wrong with it is that it names
    LinkedIn's saved list on an action that read a post permalink.

    A verifiable action is chosen on purpose. Pointing ``publish_post`` at the
    save row would reproduce the live defect more literally but would trip TWO
    checks at once -- it also declares ``unverifiable`` -- and a mutation that
    fires two checks demonstrates neither cleanly. So this asserts, in the same
    test, that the exclusivity check STILL PASSES under this mutation: the
    trespass check is the only thing standing between a borrowed row and a
    receipt.
    """
    mutated = dict(_REAL_VERIFIED_FROM)
    mutated["react_to_item"] = _REAL_VERIFIED_FROM["save_job"]
    monkeypatch.setattr(writes, "_VERIFIED_FROM", mutated)

    assert (
        "saved list" not in _REAL_VERIFIED_FROM["react_to_item"]
    ), "the snapshot was mutated"

    check_every_performable_action_verifies_or_declares_it_cannot(
        writes.PERFORMABLE,
        writes._VERIFIED_FROM,
        declares_unverifiable_map(writes.PERFORMABLE),
    )

    with pytest.raises(AssertionError) as caught:
        check_no_action_names_another_actions_phrase(
            writes._VERIFIED_FROM, _VERIFIED_FROM_OWNERS, "_VERIFIED_FROM"
        )
    message = str(caught.value)
    assert "react_to_item" in message
    assert "saved list" in message


def test_mutation_an_action_with_neither_a_row_nor_a_declaration_is_caught(
    monkeypatch,
):
    """SHAPE 4 of 8 -- performable, no ``_VERIFIED_FROM`` row, no declaration.

    ``publish_post``'s spec is rebuilt with ``unverifiable=None`` and swapped
    into a COPY of ``SANCTIONED_WRITES``, so the shipped
    ``writes.spec_for_action`` resolves the mutated spec exactly as the server
    would. The action keeps its (absent) row, so it now has neither -- the
    state in which its receipt prints the NOT RECORDED fallback.
    """
    real_spec = writes.spec_for_action("publish_post")
    assert real_spec.unverifiable is not None

    stripped = dataclasses.replace(real_spec, unverifiable=None)
    mutated_specs = dict(writes.SANCTIONED_WRITES)
    mutated_specs["linkedin_publish_post"] = stripped
    monkeypatch.setattr(writes, "SANCTIONED_WRITES", mutated_specs)

    assert writes.spec_for_action("publish_post").unverifiable is None
    assert "publish_post" not in writes._VERIFIED_FROM

    with pytest.raises(AssertionError) as caught:
        check_every_performable_action_verifies_or_declares_it_cannot(
            writes.PERFORMABLE,
            writes._VERIFIED_FROM,
            declares_unverifiable_map(writes.PERFORMABLE),
        )
    message = str(caught.value)
    assert "publish_post" in message
    assert "NO row" in message


def test_mutation_an_action_with_both_a_row_and_a_declaration_is_caught(
    monkeypatch,
):
    """SHAPE 5 of 8 -- the other direction of the exclusivity rule.

    ``publish_post`` keeps its ``Unverifiable`` and GAINS a row. Nothing prints
    that row today, which is exactly why it is dangerous: it is unreachable
    text asserting a confirming surface for the one action that declares none
    can exist, sitting one branch edit away from being printed.
    """
    mutated = dict(_REAL_VERIFIED_FROM)
    mutated["publish_post"] = "your profile's activity rail, re-read."
    monkeypatch.setattr(writes, "_VERIFIED_FROM", mutated)

    assert "publish_post" not in _REAL_VERIFIED_FROM, "the snapshot was mutated"
    assert writes.spec_for_action("publish_post").unverifiable is not None

    with pytest.raises(AssertionError) as caught:
        check_every_performable_action_verifies_or_declares_it_cannot(
            writes.PERFORMABLE,
            writes._VERIFIED_FROM,
            declares_unverifiable_map(writes.PERFORMABLE),
        )
    message = str(caught.value)
    assert "publish_post" in message
    assert "BOTH" in message


def test_mutation_a_place_borrowed_verbatim_is_caught(monkeypatch):
    """SHAPE 6 of 8 -- an identical ``_WHERE_TO_LOOK`` value on a third action.

    This is the ten-of-eleven collision in miniature: ``publish_post`` is given
    the save pair's exact string, making a group of three where only the pair
    is sanctioned. The group is compared for EQUALITY, which is what makes the
    third member fail rather than pass as "a sanctioned pair plus one".
    """
    mutated = dict(_REAL_WHERE_TO_LOOK)
    mutated["publish_post"] = _REAL_WHERE_TO_LOOK["save_job"]
    monkeypatch.setattr(writes, "_WHERE_TO_LOOK", mutated)

    assert (
        _REAL_WHERE_TO_LOOK["publish_post"] != _REAL_WHERE_TO_LOOK["save_job"]
    ), "the snapshot was mutated"

    with pytest.raises(AssertionError) as caught:
        check_no_two_actions_share_a_place_by_accident(
            writes._WHERE_TO_LOOK, _LEGITIMATE_SHARED_PLACES
        )
    message = str(caught.value)
    assert "publish_post" in message
    assert "save_job" in message


def test_mutation_a_place_borrowed_as_a_substring_is_caught(monkeypatch):
    """SHAPE 7 of 8 -- the borrow that exact-value grouping CANNOT see.

    ``publish_post`` is given "open your saved jobs first", which is a distinct
    string, so every value in the table is still unique and shape 6's check
    passes. The phrase check fires. Both facts are asserted here, because the
    point of this mutation is that the two ``_WHERE_TO_LOOK`` checks are NOT
    redundant -- dropping either one leaves a live hole.
    """
    mutated = dict(_REAL_WHERE_TO_LOOK)
    mutated["publish_post"] = "open your saved jobs first"
    monkeypatch.setattr(writes, "_WHERE_TO_LOOK", mutated)

    assert "saved jobs" not in _REAL_WHERE_TO_LOOK["publish_post"]

    check_no_two_actions_share_a_place_by_accident(
        writes._WHERE_TO_LOOK, _LEGITIMATE_SHARED_PLACES
    )

    with pytest.raises(AssertionError) as caught:
        check_no_action_names_another_actions_phrase(
            writes._WHERE_TO_LOOK, _WHERE_TO_LOOK_OWNERS, "_WHERE_TO_LOOK"
        )
    message = str(caught.value)
    assert "publish_post" in message
    assert "saved jobs" in message


def test_mutation_a_twelfth_action_with_no_rows_is_caught(monkeypatch):
    """SHAPE 8 of 8 -- the action added to ``PERFORMABLE`` and nowhere else.

    THE SHAPE THAT PRODUCED THE WHOLE DEFECT. Seven actions arrived this way
    between August and September, each inheriting somebody else's else. The
    mutation adds a twelfth to the frozenset and touches no table, which is the
    exact edit those seven were.

    ``PERFORMABLE`` is mutated rather than a table, so this fires on the
    iteration itself: it is the one check in this file that could not be
    satisfied by a hand-kept list of actions.
    """
    mutated = frozenset(writes.PERFORMABLE | {_SYNTHETIC_ACTION})
    monkeypatch.setattr(writes, "PERFORMABLE", mutated)

    assert _SYNTHETIC_ACTION not in _REAL_WHERE_TO_LOOK

    with pytest.raises(AssertionError) as caught:
        check_every_performable_action_has_a_place_to_look(
            writes.PERFORMABLE, writes._WHERE_TO_LOOK
        )
    assert _SYNTHETIC_ACTION in str(caught.value)


# ---------------------------------------------------------------------------
# Part 4 -- the unreachable fallback, made reachable
# ---------------------------------------------------------------------------


def test_the_not_recorded_fallback_says_so_and_claims_nothing():
    """The default nobody reaches, read anyway -- with a synthetic action.

    PART 1 ASSERTS THIS SENTENCE IS UNREACHABLE through any shipped action:
    every performable action either has a ``_VERIFIED_FROM`` row or declares
    ``unverifiable`` and never reaches the lookup. Under the same standing rule
    that produced Part 3, an unreachable string still has to be READ, because
    the sentence sitting there is what a future twelfth action will print on
    the day somebody adds it -- and the sentence that USED to sit there, the
    save pair's inherited else, is the entire defect this file is about.

    WHAT IS ASSERTED, against the literal read out of ``perform``'s AST:

    * it says NOT RECORDED, so the gap reads as a gap in the package rather
      than as a finding about the evidence;
    * it does not CLAIM a different surface. The phrase "a different surface"
      does occur, exactly once, inside the clause "Do not read this as 'a
      different surface'" -- a negation naming the false sentence in order to
      forbid it. Removing that clause must leave the phrase gone entirely,
      which is the difference between disclaiming a claim and making one;
    * it is nobody's real row, so a receipt carrying it cannot be mistaken for
      a receipt carrying evidence.

    THE LOOKUP IS EXERCISED, not just the string: the shipped
    ``_VERIFIED_FROM`` is queried with an action name no spec has, and the
    fallback is what comes back. It does not drive ``perform`` end to end --
    that would need a synthetic spec, a grant and a navigator, and the thing
    under test is which string the lookup yields.

    ``writes._where_to_look`` is asked the same question in the same breath:
    its documented contract is to return ``None`` rather than a default, and
    Part 1 makes that branch unreachable too.
    """
    fallback = fallback_surface_sentence()

    assert "NOT RECORDED" in fallback

    negation = "Do not read this as 'a different surface'"
    assert negation in fallback, (
        "the fallback no longer disclaims the inherited sentence. That clause "
        "is what stops this string being read as the claim six actions used "
        "to print."
    )
    remainder = fallback.replace(negation, "")
    assert "a different surface" not in remainder.lower(), (
        "the fallback names 'a different surface' outside the clause that "
        "forbids it, so it can be read as a claim: %r" % remainder
    )

    assert fallback not in _REAL_VERIFIED_FROM.values()

    assert _SYNTHETIC_ACTION not in writes.PERFORMABLE
    assert _SYNTHETIC_ACTION not in writes._VERIFIED_FROM
    assert writes._VERIFIED_FROM.get(_SYNTHETIC_ACTION, fallback) == fallback
    assert writes._where_to_look(_SYNTHETIC_ACTION) is None
