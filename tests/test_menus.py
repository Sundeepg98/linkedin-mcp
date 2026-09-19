"""``menus`` -- the closed-vocabulary enumerator, and the ruling it implements.

Mirrors ``tests/test_membership_tally.py``'s own style and section numbering,
because ``menus.py``'s docstring says its design is copied from ``groups.py``
"including the reason", so this file copies the test file the same way.

WHAT IS BEING TESTED IS AN ABSENCE, which is the hard case, same as the
sibling file. The safety claim is that **every string this module can ever
emit is one of its own literals** -- never a page's, never a caller's. A
property asserted only in a docstring is the defect this repository has named
repeatedly, so this file is the enforceable form of the module's own claims.

## HOW THE ADVERSARIAL INPUTS WERE CHOSEN

Every entry in :data:`ADVERSARIAL_LABELS` is built so that it is REFUSED --
``no_label`` or ``unmatched`` -- under the real vocabulary, never matched.
That is checked by hand against every phrase in ``menus.VOCABULARY`` below
and it matters for :func:`test_classify_returns_no_part_of_its_input`: a
label that legitimately MATCHES a single-word term (``classify("Mute")``
returning ``term="mute"``) will naturally share text with its own input --
that is the vocabulary working as designed, not a leak, and asserting
otherwise on that class of input would be asserting a false thing about a
correct implementation. So the no-leak test is scoped to inputs that are
never expected to match, and a SEPARATE tuple,
:data:`SAMPLE_MATCHED_LABELS`, carries a handful of genuine vocabulary hits
used only by the alphabet-closure test, where a real term appearing in
``terms`` is exactly what should happen.

## NO REAL IDENTIFIER OR REAL PERSON IS TYPED INTO THIS FILE, WITH ONE NAMED
## EXCEPTION

Every personal name below is invented -- see ``ADVERSARIAL_LABELS`` -- and
every urn-like and slug-like string is built short enough, or carrying a
token from ``tests/test_no_committed_identity.py``'s own
``SYNTHETIC_SLUG_TOKENS``, that neither that guard's shape rules nor this
project's ``NAMES HAVE NO SHAPE`` limitation has anything to catch, by
construction rather than by luck.

**THERE IS NO EXCEPTION, AND THERE USED TO BE ONE.** An earlier form of
this file carried a real person's full name, copied from the module's own
docstring as the worked example of the bug the single-word asymmetry
fixes. It was flagged for a reviewer's sign-off and the sign-off was the
wrong remedy: a tracked file may not carry a third party's name even as an
illustration, and REMOVAL BEATS DECLARATION, because a declaration
permanently widens what the identity guard tolerates.

So the module's example is a spice now and this file's fixtures are
non-persons throughout. **The property under test never needed a person to
demonstrate it** -- it needs a label whose FIRST TOKEN is a vocabulary term
and which carries more tokens after it, which ``Star Anise`` and ``Mark
Scheme`` both are. That the substitutes read as a spice and a grading
document is the point: a reader who wants the human case can supply it,
and the file does not have to.

## WHAT THE EMOJI FIXTURES ARE BUILT FROM

Emoji characters are assembled from code points with ``chr()``, never typed
literally, so this source file stays strict ASCII. Same convention
``tests/test_no_committed_identity.py`` uses for its non-ASCII-digit control.
"""
from __future__ import annotations

import inspect

import pytest

from linkedin_server import menus

# ---------------------------------------------------------------------------
# Fixtures built from code points, so the file stays strict ASCII.
# ---------------------------------------------------------------------------

_EMOJI_GRIN = chr(0x1F600)
_EMOJI_PARTY = chr(0x1F389)
_EMOJI_ROCKET = chr(0x1F680)

#: A HANDFUL OF GENUINE VOCABULARY HITS, used ONLY by the alphabet-closure
#: test. Each is a real menu label and each is expected to MATCH -- unlike
#: everything in ADVERSARIAL_LABELS below. Kept in a separate tuple rather
#: than folded into the adversarial list because a matched label legitimately
#: shares text with its own term (``"Mute"`` -> ``"mute"``), which would make
#: it the wrong fixture for the no-input-leak test.
SAMPLE_MATCHED_LABELS = (
    "Mute",
    "Archive",
    "Translate",
    "Send",
    "More options",
    "Reply to message",
    "Mark as read",
    "Delete conversation",
)

#: THE ADVERSARIAL LIST. Every entry is checked by hand (see the module
#: docstring) to be REFUSED under the real vocabulary -- none of these is
#: expected to match a term. Categories, in order: absence, fictional
#: personal names, digit-bearing strings, urn-like strings, ``/in/<slug>``-
#: like strings, emoji, very long strings, and shape-diagnostic noise.
ADVERSARIAL_LABELS = (
    # -- absence. classify() special-cases all of these to "no_label". -----
    None,
    "",
    "   ",
    "\t\t",
    "\n \n\t",
    "???!!!...///",  # all punctuation: normalises to nothing, same branch

    # -- realistic-looking FICTIONAL personal names. None of these is a real
    #    person -- invented for this file, same convention as groups.py's
    #    A_SLUG_MADE_OF_A_NAME one module over. Chosen so no single token
    #    equals a single-word vocabulary phrase (archive, mute, star, pin,
    #    send, and so on) and no window of tokens equals a multi-word one.
    "Marisol Fenwick",
    "Devendra Okonkwo-Bright",
    "Priyanka Devereux",
    "Tobias Ashgrove",
    "Rin Katsuragi",
    "Zephyrine Oduya",

    # -- strings with digits, none shaped as a phone/company/urn id under
    #    test_no_committed_identity.py's own rules -- short digit runs in
    #    word context, the shape an overflow label actually carries when it
    #    holds a count or a room number rather than an identifier.
    "Notify me after 3 replies",
    "Save draft #12",
    "Meeting room B204",
    "Q3 2024 targets",

    # -- urn-like strings. Digit and opaque runs are kept well under
    #    test_no_committed_identity.URN_ID_SHAPE's 6-digit floor and
    #    URN_OPAQUE_SHAPE's 8-character floor, so these read as urn-SHAPED
    #    without being mistakable for a real LinkedIn urn under either this
    #    project's guard or a human reading the diff.
    "urn:li:fsd_profile:007",
    "urn:li:activity:42",
    "urn%3Ali%3Amessage%3A9",

    # -- /in/<slug>-like strings. Each slug carries a token from
    #    test_no_committed_identity.SYNTHETIC_SLUG_TOKENS ("test", "example",
    #    "anonymous", "candidate"), so it is self-evidently invented under
    #    that guard's own rule as well as under the human rule this task
    #    states.
    "/in/test-user-example-42/",
    "/in/anonymous-candidate-7/",

    # -- emoji, built from code points above. --
    "Reacted with " + _EMOJI_GRIN + " today",
    _EMOJI_PARTY + _EMOJI_ROCKET,
    "Status: " + _EMOJI_GRIN + _EMOJI_GRIN + _EMOJI_GRIN,

    # -- very long strings, past MAX_LABEL_CHARS (400). --
    "x" * 500,
    "lorem ipsum dolor sit amet " * 20,

    # -- shape-diagnostic noise: all-caps, lowercase gibberish. --
    "URGENT REVIEW NEEDED TODAY",
    "asdkjfh qwoeiur zzt",
)


def _input_text(label) -> str:
    """The text a leak would have to come from. ``None`` carries none."""
    return "" if label is None else str(label)


def _leaks_input(value: str, input_lower: str) -> bool:
    """Does ``value`` contain a run of 4+ chars that also occurs in the input?

    Checked as 4-character windows of ``value`` (always short: a term key, a
    refusal reason, or a band name) tested for containment in the input,
    rather than the other way round. A common run of length >= 4 always
    contains a common run of length exactly 4, so this is equivalent to the
    stated rule and cheap even for the 500-character fixture above.
    """
    lowered = value.lower()
    for start in range(len(lowered) - 3):
        if lowered[start:start + 4] in input_lower:
            return True
    return False


def _ids(labels) -> list:
    """Short, stable parametrize ids -- an emoji or a 500-char string makes an
    unreadable default id, and duplicates among them would collide."""
    return [f"case{i}" for i in range(len(labels))]


# ---------------------------------------------------------------------------
# 1. The closed output alphabet is the safety property.
# ---------------------------------------------------------------------------


def test_emitted_alphabet_is_exactly_vocabulary_keys_plus_refusals():
    """The alphabet is DERIVED, not a separate hand-kept list.

    A term added to VOCABULARY or a reason added to REFUSALS reaches
    ``emitted_alphabet()`` with no edit here -- and a copy that drifted from
    the source would be a test failure rather than a silent gap.
    """
    assert menus.emitted_alphabet() == (
        frozenset(menus.VOCABULARY) | frozenset(menus.REFUSALS)
    )


def test_every_string_in_a_tally_over_adversarial_input_is_in_the_closed_alphabet():
    """THE WHOLE RULING IN ONE ASSERTION, over both refusals and real hits.

    Run over ADVERSARIAL_LABELS (expected to refuse) and SAMPLE_MATCHED_LABELS
    (expected to match) together, so the closure claim is checked in both
    directions: a term this module actually returns must be in the alphabet,
    and so must a refusal reason. Includes real-looking invented names, urn-
    and slug-shaped noise, emoji, and both kinds of absence.
    """
    alphabet = menus.emitted_alphabet()
    classifications = [
        menus.classify(label)
        for label in ADVERSARIAL_LABELS + SAMPLE_MATCHED_LABELS
    ]
    result = menus.tally(classifications)

    # Not vacuous: both dicts are non-empty, so the loops below actually run.
    assert result["terms"], "the matched samples should have produced terms"
    assert result["refused"], "the adversarial labels should have refused"

    for term in result["terms"]:
        assert term in alphabet, (term, sorted(alphabet))
    for reason in result["refused"]:
        assert reason in alphabet, (reason, sorted(alphabet))


def test_the_adversarial_list_is_actually_large():
    """A vacuous list would pass every assertion above. COUNTED, not felt."""
    assert len(ADVERSARIAL_LABELS) >= 20, len(ADVERSARIAL_LABELS)


# ---------------------------------------------------------------------------
# 2. No label is a parameter of tally. Mirrors groups.membership_tally's own
#    test, same file, same reason.
# ---------------------------------------------------------------------------


def test_tally_takes_exactly_one_parameter_the_classifications_iterable():
    """THE SIGNATURE IS THE SAFETY PROPERTY, read rather than argued.

    A future edit adding a second parameter -- a label to echo, a filter, a
    default term -- turns this red, which is the point: the fix would look
    reasonable in a diff and would silently reopen the hole ``tally`` exists
    to close.
    """
    parameters = list(inspect.signature(menus.tally).parameters)
    assert len(parameters) == 1, parameters
    assert parameters == ["classifications"], parameters
    assert not any("label" in parameter.lower() for parameter in parameters), (
        parameters
    )


# ---------------------------------------------------------------------------
# 3. classify never returns any part of its input.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("label", ADVERSARIAL_LABELS, ids=_ids(ADVERSARIAL_LABELS))
def test_classify_returns_no_part_of_its_input(label):
    """No STRING value in the verdict contains a 4+ char run of the input.

    Scoped to ADVERSARIAL_LABELS and not SAMPLE_MATCHED_LABELS -- see the
    module docstring for why a genuine match is a different question. Ints
    and bools are skipped, per the task's own note: ``matched`` is a bool and
    would trivially fail an unguarded ``in`` check against a string input.
    """
    verdict = menus.classify(label)
    input_lower = _input_text(label).lower()
    for key, value in verdict.items():
        if not isinstance(value, str):
            continue
        assert not _leaks_input(value, input_lower), (label, key, value)


# ---------------------------------------------------------------------------
# 4. The single-word asymmetry. Pinned at both the private matcher and the
#    public classify(), because the private function is where the asymmetry
#    actually lives and classify() is the contract a caller sees.
#
#    WHY: a person's name is tokens that were never meant to be one word --
#    "Mark" the verb and a person called Mark differ by exactly the tokens
#    a name adds. Requiring a single-word phrase to be the WHOLE label
#    (never merely contained) is what stops a name that happens to start with
#    a menu verb from being counted as that menu item; a multi-word phrase
#    may still be contained, because a real multi-word menu label is never
#    itself a person's name.
# ---------------------------------------------------------------------------


def test_contains_phrase_requires_whole_label_equality_for_a_single_word():
    assert menus._contains_phrase("star", "star") is True
    assert menus._contains_phrase("star anise", "star") is False


def test_contains_phrase_allows_containment_for_a_multi_word_phrase():
    assert menus._contains_phrase("show more options", "more options") is True


def test_a_bare_single_word_menu_verb_matches_its_term():
    assert menus.classify("Star") == {"matched": True, "term": "star"}


def test_the_same_word_followed_by_another_token_is_refused_not_matched():
    """A NAME ADDS TOKENS. ``Star`` alone is the whole label of a real
    reaction-picker item; ``Star Anise`` is two tokens, and the single-
    word rule requires the WHOLE label, so this falls through to unmatched
    rather than being counted as a click on the ``star`` control."""
    verdict = menus.classify("Star Anise")
    assert verdict["matched"] is False
    assert verdict["refused"] == "unmatched"


def test_a_two_token_label_starting_with_mark_does_not_become_a_bare_mark():
    """``mark`` is deliberately absent from the single-word vocabulary -- only
    ``mark as read`` / ``mark as unread`` exist -- because a given name can be
    a UI verb. This pins that a label OPENING with that token is refused, so
    the guarantee does not rest on the vocabulary gap alone.

    The fixture is a grading document rather than a person, deliberately; see
    this file's docstring. The branch under test cannot tell the difference,
    which is exactly why it does not need to be handed one."""
    verdict = menus.classify("Mark Scheme")
    assert verdict["matched"] is False
    assert verdict["refused"] == "unmatched"


def test_a_multi_word_phrase_may_be_contained_in_a_longer_label():
    verdict = menus.classify("Show more options")
    assert verdict["matched"] is True
    assert verdict["term"] == "overflow_trigger"


def test_delete_this_conversation_matches_its_multi_word_phrase():
    verdict = menus.classify("Delete this conversation")
    assert verdict["matched"] is True
    assert verdict["term"] == "delete_conversation"


# ---------------------------------------------------------------------------
# 5. The unmatched branch reports shape, not content.
# ---------------------------------------------------------------------------

_KNOWN_BAND_NAMES = frozenset(name for _, name in menus._BANDS)


def test_an_unmatched_verdict_carries_shape_facts_and_a_known_band():
    verdict = menus.classify("Marisol Fenwick")
    assert verdict["matched"] is False
    assert verdict["refused"] == "unmatched"
    assert {"band", "tokens", "has_digits", "all_capitalised"} <= set(verdict)
    assert verdict["band"] in _KNOWN_BAND_NAMES, verdict["band"]


@pytest.mark.parametrize(
    "label",
    # Each chosen so character length != token count != 0/1, so a
    # coincidental numeric collision cannot masquerade as a pass. "A" is
    # deliberately excluded: its length (1) equals its token count (1), which
    # would make the check below vacuous rather than wrong -- but also not a
    # real test of anything.
    ["Zephyrine", "Marisol Fenwick", "asdkjfh qwoeiur zzt", "x" * 37],
)
def test_the_exact_character_length_never_appears_as_a_verdict_value(label):
    """LENGTH IS BANDED DELIBERATELY. An exact length over a small known
    vocabulary is itself an identifier -- see the module docstring -- so
    nothing in the verdict may equal it, compared both as the int and as its
    string form (a band value is always a range name like ``"9-20"``, never
    a bare number, so this also guards against a future ``_band`` that
    quietly switches to one)."""
    verdict = menus.classify(label)
    exact = len(label)
    for value in verdict.values():
        assert value != exact, (label, value)
        assert str(value) != str(exact), (label, value)


@pytest.mark.parametrize(
    "length,expected_band",
    [
        (0, "empty"),
        (1, "1-8"),
        (8, "1-8"),
        (9, "9-20"),
        (20, "9-20"),
        (21, "21-40"),
        (40, "21-40"),
        (41, "41-plus"),
    ],
)
def test_band_edges_match_the_modules_own_table(length, expected_band):
    """Every floor in ``_BANDS``, not a sample of them -- an edit to the
    table that shifts a boundary by one fails here rather than in the field."""
    assert menus._band(length) == expected_band


def test_all_capitalised_is_true_for_a_name_shaped_label_and_false_for_noise():
    """THE TELL THE MODULE DOCSTRING NAMES -- the field that separates a UI
    verb LinkedIn has not taught this table yet from a conversation row
    wearing a person's name."""
    named = menus.classify("Marisol Fenwick")
    assert named["all_capitalised"] is True

    noise = menus.classify("asdkjfh qwoeiur zzt")
    assert noise["all_capitalised"] is False


def test_has_digits_is_true_only_when_the_label_actually_carries_a_digit():
    with_digits = menus.classify("Save draft #12")
    assert with_digits["has_digits"] is True

    without_digits = menus.classify("Marisol Fenwick")
    assert without_digits["has_digits"] is False


# ---------------------------------------------------------------------------
# 6. tally reports items and matched separately.
# ---------------------------------------------------------------------------


def test_items_and_matched_differ_when_something_is_refused():
    """A caller shown ``matched`` alone cannot tell five-of-five from
    five-of-twelve. ``items`` is what makes the difference visible."""
    result = menus.tally(
        [menus.classify(label) for label in ("Mute", "Marisol Fenwick")]
    )
    assert result["items"] == 2
    assert result["matched"] == 1
    assert result["items"] != result["matched"]


def test_items_and_matched_are_equal_only_when_nothing_is_refused():
    result = menus.tally(
        [menus.classify(label) for label in ("Mute", "Archive", "Send")]
    )
    assert result["items"] == result["matched"] == 3


def test_an_empty_classification_list_is_zero_and_says_so():
    """Mirrors groups.py's own empty-input control, same reason: a caller
    handed nothing should see zero rather than a surface's worth of
    plausible-looking absence."""
    result = menus.tally([])
    assert result["items"] == 0
    assert result["matched"] == 0
    assert result["terms"] == {}
    assert result["refused"] == {}
