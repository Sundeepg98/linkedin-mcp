"""THE RECIPIENT GATE'S NAME MATCH IS A BARE SUBSTRING, AND ITS OWN SELECTOR
SUPPLIES HALF THE HAYSTACK.

``writes._recipient_gate`` is the only thing standing between a tool call and
a message arriving in a named human being's inbox. Its docstring states the
safety property in capitals -- **"WHAT MAKES THIS SAFE IS THE NAME MATCH, NOT
THE COUNT"** -- and that claim is correct about the COUNT. This file is about
the other half of the sentence: what the NAME MATCH actually is.

It is ``indexOf``. ``dom.SELECTED_RECIPIENT_JS`` builds

    (aria-label or "") + " " + (textContent or "")

lowercases it, and asks whether the needle appears anywhere inside. That is
the loosest relation available between two strings, and it is being asked to
carry the most irreversible write in this package.

TWO THINGS GO WRONG, AND THEY ARE DIFFERENT
-------------------------------------------
**1. THE HAYSTACK CONTAINS THE FURNITURE THE SELECTOR SELECTED ON.** Every
candidate in ``dom.RECIPIENT_CHIP_SELECTORS`` constrains ``aria-label`` to
carry a remove-control's own label word. The matcher then searches that same
attribute. So a needle that is a substring of the CONTROL's wording matches on
a chip naming a total stranger -- the gate finds its needle in the button, not
in the person. This is
``uniqueness-over-a-filtered-set-measures-the-filter`` one layer down: the
string being searched was chosen BECAUSE it contains the thing being searched
for.

**2. A SHORT NAME IS A SUBSTRING OF A LONGER ONE.** No furniture needed. If he
names someone and LinkedIn commits a different person whose name merely
contains those letters, ``indexOf`` reports a match and the gate proceeds.

WHY THIS FILE DOES NOT FIX IT
-----------------------------
The obvious repair is a stricter matcher -- an anchor, a word boundary, a
whole-token compare. **Every one of those was MEASURED DEAD on the
neighbouring surface**, in ``_audit/2026-09-03-typeahead-name-matching-is-
dead.md``: on the suggestion rows, ``prefix``, ``prefix_then_nonletter``,
``prefix_boundary``, ``prefix_then_space_or_end`` and ``whole`` all read ZERO
against live markup, and a word boundary cannot even separate a name from a
connection degree run onto it.

That measurement is about the SUGGESTION rows and this is the CHIP rail, which
is a different surface -- and **nobody has ever observed a chip.**
``dom.RECIPIENT_CHIP_SELECTORS`` has never matched anything on any real page,
which both ``dom`` and ``tests/test_send_message_gate.py`` say at length. So
choosing a stricter matcher here would be choosing it against an imagined DOM,
and the last time somebody derived a matcher from a fixture built to the only
shape anyone had guessed, it was "correct on the shape the fixtures had, and
dead on the shape the page has."

**A tighter matcher aimed at an unobserved rail could refuse everybody,
including the right person -- which on this gate is safe -- or it could keep
proceeding for a reason nobody measured, which is not.** The honest move is to
make the current relation VISIBLE and let whoever observes a real chip choose,
so the two known-defect tests below assert TODAY'S behaviour and turn RED the
day it is fixed, rather than passing in silence either way.

WHAT THE READER SHOULD TAKE FROM A GREEN RUN OF THIS FILE
---------------------------------------------------------
Green here means: the gate still matches by bare substring, and both
collisions still reach ``proceed: True``. It is a defect RECORDED, not a
defect absent.

NOBODY IN THIS FILE IS ANYBODY. Every name is imported from
``tests/test_send_message_gate.py``'s invented set.
"""

from linkedin_server import dom
from linkedin_server.writes import TARGET_JOIN

# THE HARNESS AND THE FIXTURES, IMPORTED RATHER THAN REBUILT. This repo's own
# rule, paid for twice today: when a corpus already ships an instrument, import
# it -- a reimplementation aimed at the same question disagreed with the
# shipped one both times it was tried, and the reimplementation was wrong.
# ``_with_chips`` and ``_gate`` are underscore-private to that module; they are
# taken here deliberately so that this file and that one exercise the SAME
# guessed chip, and a change to the guess moves both together.
from tests.test_apply_modal_fixture import over  # noqa: F401
from tests.test_send_message_gate import (  # noqa: F401
    MESSAGE_BODY,
    NAMED_RECIPIENT,
    SOMEBODY_ELSE,
    _gate,
    _with_chips,
)

# NO ``pytestmark`` HERE. ``pytest.ini`` sets ``asyncio_mode = auto``, so the
# async tests below are collected without one -- and a module-level asyncio
# mark would be applied to the two SYNCHRONOUS tests as well, which pytest
# warns about and which would be a mark that means nothing where it landed.


# ---------------------------------------------------------------------------
# The furniture, DERIVED from the selectors rather than spelled here
# ---------------------------------------------------------------------------
#
# THE POINT OF DERIVING IT. If somebody rewrites the candidate tuple, a spelled
# literal would leave this file testing a haystack that no longer exists while
# still going green. Derivation makes that a failure instead.


def _aria_label_fragments() -> list[str]:
    """Every literal each candidate selector constrains ``aria-label`` to carry.

    Returns the fragments in candidate order. A candidate that does not
    constrain ``aria-label`` at all contributes nothing, which is itself worth
    seeing -- it is a candidate whose haystack this file cannot predict.
    """
    fragments: list[str] = []
    for selector in dom.RECIPIENT_CHIP_SELECTORS:
        for operator in ('aria-label^="', 'aria-label*="', 'aria-label="'):
            start = selector.find(operator)
            if start == -1:
                continue
            start += len(operator)
            end = selector.find('"', start)
            if end != -1:
                fragments.append(selector[start:end])
            break
    return fragments


#: The longest fragment any candidate pins into ``aria-label``. On the shipped
#: tuple this is the remove control's own label word.
FURNITURE = max(_aria_label_fragments(), key=len, default="")

#: A REAL GIVEN NAME that is a substring of the furniture word. Spelled,
#: because deriving "which slice of this word is a plausible human name" is not
#: something a test can compute -- but both properties it needs are ASSERTED
#: below rather than assumed, so a furniture change fails this file loudly
#: instead of quietly aiming it at nothing.
FURNITURE_NEEDLE = "Mo"

#: A needle that is a proper substring of the STRANGER'S name. This is the
#: everyday collision: he names a short name, LinkedIn commits a longer one
#: containing it.
CONTAINED_NEEDLE = SOMEBODY_ELSE.split()[0][:7]

#: A needle present in neither the furniture nor either invented name. The
#: CONTROL: if this one does not refuse, the harness is broken and nothing else
#: in this file means anything.
ABSENT_NEEDLE = "Zzyxwood"


def _target(needle: str) -> str:
    """A canonical two-part target whose subject half is ``needle``."""
    return needle + TARGET_JOIN + MESSAGE_BODY


# ---------------------------------------------------------------------------
# 1. The structural claim, no browser required
# ---------------------------------------------------------------------------


def test_the_matcher_searches_the_attribute_the_selector_selected_on():
    """THE SHAPE OF THE DEFECT, asserted against the shipped constants.

    Three facts, and the collision is their conjunction rather than any one of
    them:

      1. at least one candidate selector constrains ``aria-label`` to a literal;
      2. the matcher concatenates ``aria-label`` into the string it searches;
      3. it searches with ``indexOf``, which is position-free and
         boundary-free.

    Any ONE of these is unremarkable. Together they mean the haystack is
    guaranteed by construction to contain a word nobody chose as a name.
    """
    fragments = _aria_label_fragments()
    assert fragments, (
        "no candidate in RECIPIENT_CHIP_SELECTORS constrains aria-label to a "
        "literal any more. That is not necessarily a fix -- it may mean the "
        "haystack is now unpredictable rather than predictably contaminated. "
        "Re-derive this file's premise before trusting anything below it."
    )
    assert FURNITURE, fragments

    source = dom.SELECTED_RECIPIENT_JS
    assert "getAttribute('aria-label')" in source, source
    assert "textContent" in source, source
    assert "indexOf(needle)" in source, source
    # THE ORDERING IS NOT THE POINT AND IS NOT ASSERTED. Which of the two
    # halves comes first changes nothing: indexOf has no anchor, so a needle
    # found in either half is a match.


def test_the_furniture_needle_premise_holds_in_both_directions():
    """CONTROLLED BOTH WAYS, so this file cannot pass for the wrong reason.

    The furniture needle must be IN the furniture -- otherwise the case below
    proves nothing -- and must be ABSENT from the stranger's name, or the case
    is confounded with the containment case and neither says what it claims.
    """
    assert FURNITURE_NEEDLE.lower() in FURNITURE.lower(), (
        FURNITURE_NEEDLE,
        FURNITURE,
    )
    assert FURNITURE_NEEDLE.lower() not in SOMEBODY_ELSE.lower(), (
        "the furniture needle also appears in the stranger's name, so the "
        "case below would no longer isolate the furniture collision."
    )
    assert FURNITURE_NEEDLE.lower() not in NAMED_RECIPIENT.lower()

    assert CONTAINED_NEEDLE.lower() in SOMEBODY_ELSE.lower()
    assert CONTAINED_NEEDLE.lower() != SOMEBODY_ELSE.lower()
    assert CONTAINED_NEEDLE.lower() not in NAMED_RECIPIENT.lower()

    for needle in (ABSENT_NEEDLE,):
        assert needle.lower() not in SOMEBODY_ELSE.lower()
        assert needle.lower() not in FURNITURE.lower()


# ---------------------------------------------------------------------------
# 2. The control. The detector fires.
# ---------------------------------------------------------------------------


async def test_the_control_a_genuinely_absent_needle_is_refused(over):
    """THE DETECTOR, SHOWN FIRING, and it is factored out of the two assertions
    below rather than being assumed by them.

    Same chip, same page, same gate. Only the needle differs. A refusal here is
    what makes a ``proceed`` in either known-defect case attributable to the
    MATCHER instead of to a fixture that silently stopped drawing a chip -- the
    one failure mode a guessed selector guarantees.
    """
    verdict = await _gate(over, _with_chips(SOMEBODY_ELSE), _target(ABSENT_NEEDLE))

    assert verdict["proceed"] is False, verdict
    assert verdict["refused_condition"] == "3_needle_does_not_match", verdict
    observed = verdict["observed"]
    # THE CHIP WAS SEEN. Without this the refusal could be the empty-composer
    # refusal wearing another condition's name.
    assert observed["total"] == 1, observed
    assert observed["matches"] == 0, observed


# ---------------------------------------------------------------------------
# 3. The two known defects. GREEN HERE MEANS THE DEFECT IS STILL PRESENT.
# ---------------------------------------------------------------------------


async def test_KNOWN_DEFECT_a_needle_inside_the_button_wording_proceeds(over):
    """A NEEDLE FOUND IN THE REMOVE CONTROL, NOT IN THE PERSON, AND THE GATE
    PROCEEDS ANYWAY.

    The composer holds exactly one committed recipient and it is a STRANGER --
    byte-for-byte the state ``test_the_gate_refuses_one_wrong_recipient``
    refuses. The only thing that changed is that the needle happens to be a
    substring of the control's own label, which every candidate selector
    guarantees is present.

    ``matches`` reads 1 and ``total`` reads 1, so the gate returns
    ``proceed: True`` and his words would be typed next -- addressed to
    somebody he never named. The needle used here is a real, common given name,
    so this is not a contrived string.

    **THIS TEST IS A RECORD OF A DEFECT, NOT A SPECIFICATION.** When the
    matcher is tightened it goes RED, which is the point: the alternative is a
    fix landing with nothing to notice it, or the defect surviving a rewrite
    because no test ever described it.
    """
    verdict = await _gate(
        over, _with_chips(SOMEBODY_ELSE), _target(FURNITURE_NEEDLE)
    )

    observed = verdict["observed"]
    assert observed["total"] == 1, observed
    assert observed["matches"] == 1, observed
    assert verdict["proceed"] is True, (
        "the furniture collision no longer reaches proceed. If the matcher was "
        "deliberately tightened, DELETE this test and say so in the commit -- "
        "do not relax it. If nobody tightened anything, the chip fixture has "
        "stopped matching and the control test above should have caught it.",
        verdict,
    )


async def test_KNOWN_DEFECT_a_needle_inside_a_longer_name_proceeds(over):
    """THE EVERYDAY COLLISION, needing no furniture at all.

    He names a short name; LinkedIn commits a DIFFERENT person whose name
    contains those letters. ``indexOf`` cannot tell that apart from naming the
    person, and there is no count to fall back on -- exactly one recipient is
    committed, which is the state the gate was built to act from.

    This is the case that makes the fix hard rather than obvious: no relation
    over the label alone distinguishes "this is the person" from "this person's
    name contains that", which is why the identifier route in the typeahead
    audit's section 5 exists.

    RED MEANS FIXED. See the sibling test above.
    """
    verdict = await _gate(
        over, _with_chips(SOMEBODY_ELSE), _target(CONTAINED_NEEDLE)
    )

    observed = verdict["observed"]
    assert observed["total"] == 1, observed
    assert observed["matches"] == 1, observed
    assert verdict["proceed"] is True, (
        "the containment collision no longer reaches proceed -- see the "
        "sibling test's message before editing this one.",
        verdict,
    )


# ---------------------------------------------------------------------------
# 4. THE REACH OF THE ONE NARROWING THAT NEEDS NO OBSERVATION
# ---------------------------------------------------------------------------
#
# Section 1 of _audit/2026-09-05-messaging.md says a fix is available without
# observing a real chip: STOP SEARCHING THE ATTRIBUTE THE SELECTOR SELECTED ON.
# That is a claim about a repair nobody has applied, and a claim about a repair
# is worth exactly as much as a measurement of its reach. These two measure it.
#
# THE ANSWER IS UNCOMFORTABLE AND THAT IS WHY IT IS HERE: on the guessed chip
# the name and the contaminant are THE SAME STRING, so "search a different
# field" is not an available move at all.


#: A COUNT-ONLY READER, in the house style. The comparison happens IN THE PAGE
#: and three integers come back, so no invented name and no label crosses into
#: this process -- the same argument ``SELECTED_RECIPIENT_JS`` makes for
#: itself, kept here so this file does not weaken it while measuring it.
WHERE_DOES_THE_NAME_LIVE_JS = """
(cfg) => {
  const node = document.querySelector(cfg.selector);
  if (!node) { return {found: 0, in_aria: 0, in_text: 0, furniture_in_aria: 0}; }
  const aria = (node.getAttribute('aria-label') || '').toLowerCase();
  const text = (node.textContent || '').toLowerCase();
  const needle = String(cfg.needle).toLowerCase();
  const furniture = String(cfg.furniture).toLowerCase();
  return {
    found: 1,
    in_aria: aria.indexOf(needle) === -1 ? 0 : 1,
    in_text: text.indexOf(needle) === -1 ? 0 : 1,
    furniture_in_aria: aria.indexOf(furniture) === -1 ? 0 : 1
  };
}
"""


async def test_the_name_and_the_contaminant_are_the_same_string(over):
    """**THE FIX CANNOT BE "SEARCH A DIFFERENT FIELD."**

    Measured on the chip this suite draws: the recipient's name is present in
    ``aria-label`` and ABSENT from ``textContent``, while the furniture word is
    in ``aria-label`` too. The only field carrying the name is the field
    carrying the contaminant.

    So dropping ``aria-label`` from the haystack -- the obvious reading of
    "stop searching what you selected on" -- would leave the matcher searching
    a string with no name in it, and the gate would refuse EVERY recipient
    including the right one. That is safe and it is also useless.

    **The available repair is therefore narrower than it sounded: STRIP the
    pinned furniture from the front of the attribute, then search the
    remainder.** The sibling test measures how many candidates that is even
    defined for.

    CAVEAT WITH THE SAME FORCE AS EVERYWHERE ELSE IN THIS SUITE: this is the
    GUESSED chip. Whether LinkedIn puts the name in ``aria-label``, in
    ``textContent``, in both or in neither is unobserved. What is measured here
    is the shape this repo has been reasoning against, which is the shape any
    repair would be written against today.
    """

    async def work(page):
        return await page.evaluate(  # readonly-ok
            WHERE_DOES_THE_NAME_LIVE_JS,
            {
                "selector": dom.RECIPIENT_CHIP_SELECTORS[0],
                "needle": SOMEBODY_ELSE,
                "furniture": FURNITURE,
            },
        )

    seen = await over(_with_chips(SOMEBODY_ELSE), work)

    assert seen["found"] == 1, (
        "the chip was not drawn at all, so nothing below is a reading about "
        "where a name lives.",
        seen,
    )
    # THE READER IS SHOWN BOTH FIRING AND NOT FIRING IN ONE CALL, which is
    # what keeps ``in_text == 0`` from being the reading of a broken reader.
    # Same function, same needle, same node: one field answers 1 and the other
    # answers 0. A reader stuck at zero fails the line above; a reader stuck at
    # one fails the line below.
    assert seen["in_aria"] == 1, seen
    assert seen["in_text"] == 0, seen
    assert seen["furniture_in_aria"] == 1, seen


def test_only_a_prefix_pinned_candidate_admits_a_principled_strip():
    """HOW MANY CANDIDATES THE STRIP IS EVEN DEFINED FOR. An integer, not a hope.

    A strip needs a KNOWN position for the furniture. ``aria-label^="X"`` pins
    it at the front, so the remainder is well defined. ``aria-label*="X"``
    pins only that it occurs SOMEWHERE, and there is no defined point to cut
    -- stripping the first occurrence would eat a name that happens to contain
    those letters, which is the very collision being repaired.

    **So the repair is partial by construction**, and the number of candidates
    it cannot serve is the number recorded here. A future editor who adds a
    fifth candidate with ``*=`` moves this number and has to say why.
    """
    anchored = [s for s in dom.RECIPIENT_CHIP_SELECTORS if 'aria-label^="' in s]
    unanchored = [s for s in dom.RECIPIENT_CHIP_SELECTORS if 'aria-label*="' in s]
    no_aria = [
        s
        for s in dom.RECIPIENT_CHIP_SELECTORS
        if "aria-label" not in s
    ]

    assert len(anchored) == 1, anchored
    assert len(unanchored) == 1, unanchored
    assert len(no_aria) == 2, no_aria
    assert len(anchored) + len(unanchored) + len(no_aria) == len(
        dom.RECIPIENT_CHIP_SELECTORS
    ), dom.RECIPIENT_CHIP_SELECTORS

    # THE TWO WITHOUT aria-label ARE NOT SAFE EITHER, and saying so is the
    # point of counting them separately rather than folding them into "fine".
    # They put NO constraint on the haystack, so what those chips carry is
    # simply unknown -- which is a different problem from a known contaminant
    # and is not fixed by any strip.
