"""The filter probe's two channels, its KEY KEPT reading, and its denominators.

WHY THIS FILE EXISTS. ``scripts/_probe_job_search_filter_params.py`` asks
whether LinkedIn honours five job-search url parameters. Its first live run
answered three questions wrongly, and every one of the three was found by
reading the probe's OWN OUTPUT rather than by any instrument:

1. **A CHANNEL WAS LABELLED WITH A WORD IT DOES NOT MEASURE.** "Survived into
   the landed url" was read as evidence the filter was HONOURED. The run's own
   value control refutes that: ``f_JT=ZZ`` -- a job-type value the filter has
   never had -- survived VERBATIM and was inert on every other channel, while
   ``f_ZZQQX`` was STRIPPED. Url survival measures whether LinkedIn RECOGNISES
   THE KEY. Whether the VALUE was applied is a different question and that
   channel cannot answer it.
2. **THE ARIA GATE REPORTED A CLEAN ABSENCE FOR A CONTROL IT CANNOT SEE.**
   ``_read_buttons`` kept a button only if it carried ``aria-pressed``,
   ``aria-checked`` or ``aria-expanded``. ``Reset selected Job type`` -- the
   single control on the page that evidences ``f_JT`` having applied -- carries
   ``pressed=- checked=- expanded=-``, so the gate excluded it structurally.
   The probe printed ``(none)`` differing for ``f_JT=F`` and that zero was read
   as a negative. **A ZERO FROM A GATE THAT CANNOT SEE THE THING IS NOT A
   NEGATIVE READING**, and it is the defect this repository hit all week.
3. **A VERBATIM COMPARISON PRODUCED A FALSE NEGATIVE.** Survival was
   ``parameter in landed_url``, a raw substring test. ``f_JT=F,C`` was reported
   ``SURVIVED: NO`` for one reason only: LinkedIn percent-encoded the comma and
   returned ``f_JT=F%2CC``, which was accepted.

## What is asserted, and the one property every assertion has

**EVERY TEST BELOW FAILS AGAINST THE PRE-FIX BEHAVIOUR.** That is the bar, not
a nicety: a guard written after the fact that would have passed before it is a
guard certifying nothing, and this package has a standing rule that an
instrument enters the register only once it has been shown failing. Each test
names, in its own body, what the old code did that makes it go red.

**NO BROWSER, NO NETWORK, NO LIVE PAGE.** The probe's gate ladder was extracted
into :func:`_button_reading`, a pure function over ``(name, aria-values)``
pairs, for exactly this reason -- the async ``_read_buttons`` now does the I/O
and nothing else. Everything here is a synthetic input to a pure helper.

## The literals

**A SELF-TEST NEEDS A SHAPE-VALID LITERAL, NEVER A TRUE ONE.**
``tests/test_probe_redaction.py`` exists in this repository because an earlier
version of it carried a real member urn and a thread id truncated from a real
one -- the test written to prove a redactor removes real identifiers contained
two of them. Nothing below is anybody's: the control names are LinkedIn's own
chrome, which carries no identity and is what the probe is allowed to print
verbatim; the long name is invented word by word and names no employer and no
role; and no url goes beyond ``https://www.linkedin.com/jobs/search/`` with the
probe's own fixed keyword and its own ``f_`` parameters.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_PROBE = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "_probe_job_search_filter_params.py"
)


def _probe_module():
    """Import the probe by path, as ``test_probe_redaction`` does.

    Imported fresh per test rather than once at module scope, which is that
    file's convention and matters here for the same reason: importing a script
    must not DO anything, and doing it repeatedly is the cheapest standing
    demonstration that it does not.
    """
    spec = importlib.util.spec_from_file_location(
        "_probe_job_search_filter_params", _PROBE
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# The literals. Every one invented or LinkedIn's own furniture -- see the
# docstring; none is anybody's.
# ---------------------------------------------------------------------------

#: THE CONTROL THIS WHOLE FILE IS ABOUT. Measured on the live run wearing
#: ``pressed=- checked=- expanded=-``: it is the one control that evidences
#: ``f_JT`` having applied, and the aria gate could not see it.
ARIA_LESS_NAME = "Reset selected Job type"

#: Ordinary chrome that DOES carry an aria state, so the aria channel has
#: something to see and a green result is never just the empty set passing.
STATEFUL_NAME = "Show more options"

#: A second aria-less control, so the plural branch of the absence line is
#: exercised rather than assumed.
SECOND_ARIA_LESS_NAME = "Contract"

#: A name at or over ``NAME_LIMIT`` (60) that ALSO carries no aria state --
#: the combination that fell out of the denominator entirely before the fix,
#: because the blind count was incremented in two of the three branches.
#: Invented word by word; it names no employer and no listing.
LONG_NAME = "Save the placeholder listing at the invented employer number seven"

#: aria (pressed, checked, expanded) exactly as ``_read_buttons`` collects
#: them. ``None`` means the attribute is ABSENT, which is a different fact
#: from an attribute present and reading ``false`` -- collapsing the two would
#: delete the vocabulary this probe needs.
NO_ARIA = [None, None, None]
HAS_ARIA = [None, None, "false"]

#: The probe's own baseline address, and its own fixed keyword.
JOBS_SEARCH = "https://www.linkedin.com/jobs/search/?keywords=node.js%20developer"

#: What LinkedIn actually returned for the comma-joined address: the pair was
#: ACCEPTED, with the comma percent-encoded.
LANDED_ENCODED_COMMA = JOBS_SEARCH + "&f_JT=F%2CC"

#: The value-level control, kept verbatim and inert on every other channel.
LANDED_VALUE_CONTROL = JOBS_SEARCH + "&f_JT=ZZ"


def _row(**over) -> dict:
    """A pass-one row with every channel silent, for :func:`_verdict`."""
    row = {
        "cards_delta": 0,
        "differing": [],
        "names_appeared": [],
        "names_disappeared": [],
        "failed": "",
        "buttons": {"no_aria_state": 0},
    }
    row.update(over)
    return row


# ---------------------------------------------------------------------------
# DEFECT 2 -- the aria gate reported a clean absence for a control it cannot see
# ---------------------------------------------------------------------------


def test_a_control_with_no_aria_state_reaches_the_name_presence_channel():
    """THE CENTRAL ONE. ``Reset selected Job type`` must be REPORTED.

    PRE-FIX THERE WAS NO SUCH CHANNEL: the only comparison was
    ``_differing_names`` over the aria-state mapping, which this control could
    not enter, so the probe printed ``(none)`` and the zero was read as a
    negative.
    """
    probe = _probe_module()
    baseline = probe._button_reading([(STATEFUL_NAME, HAS_ARIA)])
    candidate = probe._button_reading(
        [(STATEFUL_NAME, HAS_ARIA), (ARIA_LESS_NAME, NO_ARIA)]
    )

    delta = probe._name_presence_delta(baseline, candidate)

    # ASSERTED DIRECTLY, NOT VIA A COUNT. A count would go green on any
    # control appearing -- including one the aria gate could already see --
    # which is precisely the confusion this file exists to end.
    assert ARIA_LESS_NAME in delta["appeared"]
    assert delta["disappeared"] == []


def test_the_aria_channel_is_blind_to_that_same_control():
    """THE OTHER HALF, AND IT IS WHY THE FIRST CHANNEL IS NOT ENOUGH.

    The aria channel is not wrong here, it is BLIND: the control carries no
    aria state, so it cannot appear on that channel however the diff is
    written. Asserting the blindness explicitly stops a future author
    "fixing" the aria channel to cover this and deleting the second one.
    """
    probe = _probe_module()
    baseline = probe._button_reading([(STATEFUL_NAME, HAS_ARIA)])
    candidate = probe._button_reading(
        [(STATEFUL_NAME, HAS_ARIA), (ARIA_LESS_NAME, NO_ARIA)]
    )

    assert probe._differing_names(baseline, candidate) == []
    assert ARIA_LESS_NAME not in candidate["states"]
    # ... and yet it IS on the page, and the name channel holds it.
    assert ARIA_LESS_NAME in candidate["names"]


def test_a_bare_none_cannot_be_printed_while_controls_are_unmatchable():
    """AN ABSENCE ON THE ARIA CHANNEL MUST NAME ITS DENOMINATOR.

    PRE-FIX ``_cell`` took one argument and returned the string ``(none)``,
    with no way to say that 51 controls on that page were invisible to the
    channel reporting the zero.
    """
    probe = _probe_module()
    reading = probe._button_reading(
        [
            (STATEFUL_NAME, HAS_ARIA),
            (ARIA_LESS_NAME, NO_ARIA),
            (SECOND_ARIA_LESS_NAME, NO_ARIA),
            (LONG_NAME, NO_ARIA),
        ]
    )
    assert reading["no_aria_state"] == 3

    cell = probe._cell([], reading)

    assert cell != "(none)"
    assert "3 controls carry no aria state" in cell
    assert "invisible" in cell


def test_the_blind_count_includes_a_control_the_name_gates_also_dropped():
    """THE DENOMINATOR IS COMPLETE, NOT MERELY PRESENT.

    PRE-FIX the blind count was incremented in two of the three branches, so a
    control with a 60-character name AND no aria state fell out of it
    entirely -- an undercount in the one number whose whole job is to say how
    blind the aria channel was.
    """
    probe = _probe_module()
    reading = probe._button_reading([(LONG_NAME, NO_ARIA)])

    assert reading["too_long"] == 1
    assert reading["no_aria_state"] == 1


def test_a_no_change_verdict_names_the_controls_it_could_not_see():
    """``_verdict`` may not return a NO-CHANGE off a channel that dropped
    controls without saying so.

    PRE-FIX it returned the bare string with no count in it at all.
    """
    probe = _probe_module()
    verdict = probe._verdict(_row(buttons={"no_aria_state": 51}), True)

    assert "NO CHANGE" in verdict
    assert "51" in verdict
    assert verdict != "NO CHANGE on the two channels this rule reads -- see pass two"


def test_a_name_presence_difference_is_not_folded_into_no_change():
    """A CHANGE THE ARIA CHANNEL CANNOT SEE IS STILL A CHANGE.

    PRE-FIX this row -- aria channel silent, name-presence channel carrying
    ``Reset selected Job type`` -- returned NO CHANGE, which is the reading
    that made ``f_JT=F`` look ignored.
    """
    probe = _probe_module()
    verdict = probe._verdict(
        _row(names_appeared=[ARIA_LESS_NAME], buttons={"no_aria_state": 51}),
        True,
    )

    assert "NO CHANGE" not in verdict
    assert "NAME-PRESENCE" in verdict


# ---------------------------------------------------------------------------
# DEFECT 3 -- a verbatim comparison produced a false negative
# ---------------------------------------------------------------------------


def test_a_percent_encoded_comma_reads_as_key_kept():
    """``f_JT=F,C`` against a landed ``f_JT=F%2CC`` is KEPT.

    PRE-FIX the test was ``parameter in landed_url``, and the first assertion
    below is the false negative spelled out rather than described: as raw
    bytes the parameter really is absent, and the probe reported NO on that
    basis while LinkedIn had accepted the pair.
    """
    probe = _probe_module()
    assert "f_JT=F,C" not in LANDED_ENCODED_COMMA

    reading = probe._key_kept("f_JT=F,C", LANDED_ENCODED_COMMA)

    assert reading["kept"] is True
    assert reading["key_present"] is True
    # THE ENCODING IS REPORTED AS A RELATION, never by echoing the landed
    # value: `_shape_of`'s ruling binds here, and a cold verifier measured
    # that no charset or length rule separates a vanity slug from an enum.
    assert reading["byte_identical"] is False

    rendered = " ".join(probe._key_kept_lines("f_JT=F,C", reading))
    assert "KEY KEPT" in rendered
    assert "YES" in rendered
    assert "IS NOT byte-identical" in rendered
    # THE LANDED VALUE ITSELF IS NEVER PRINTED, only its length.
    assert "F%2CC" not in rendered


def test_a_key_linkedin_strips_reads_as_not_kept():
    """THE NEGATIVE CONTROL, so the check can still say no.

    Normalising a comparison is exactly the change that can turn a test into
    one that answers YES to everything. ``f_ZZQQX`` is a parameter LinkedIn
    has never had and its key is absent from the landed query, so a reading
    of NOT KEPT here is what proves the YES above was discriminating.
    """
    probe = _probe_module()
    reading = probe._key_kept("f_ZZQQX=true", JOBS_SEARCH)

    assert reading["kept"] is False
    assert reading["key_present"] is False

    rendered = " ".join(probe._key_kept_lines("f_ZZQQX=true", reading))
    assert "KEY KEPT" in rendered
    assert "NO" in rendered
    assert "ABSENT" in rendered


# ---------------------------------------------------------------------------
# DEFECT 1 -- a channel labelled with a word it does not measure
# ---------------------------------------------------------------------------


def test_the_key_kept_channel_never_says_honoured():
    """NOTHING MAY PRINT HONOURED ON THE STRENGTH OF KEY SURVIVAL ALONE.

    PRE-FIX this channel was called "survived", and a survival of YES was read
    as the filter having been honoured. The value control refutes it:
    ``f_JT=ZZ`` was kept verbatim and changed nothing.
    """
    probe = _probe_module()
    for parameter, landed in (
        ("f_JT=F,C", LANDED_ENCODED_COMMA),
        ("f_JT=ZZ", LANDED_VALUE_CONTROL),
        ("f_ZZQQX=true", JOBS_SEARCH),
    ):
        reading = probe._key_kept(parameter, landed)
        rendered = " ".join(probe._key_kept_lines(parameter, reading))
        assert "HONOURED" not in rendered.upper(), parameter


def test_the_channel_says_in_its_own_words_what_it_cannot_answer():
    """THE CAVEAT IS EMITTED, NOT MERELY IMPLIED BY A SILENCE.

    An absence of the word HONOURED would also be satisfied by a channel that
    said nothing at all, so the positive half is asserted too: the reading
    states that the VALUE question is a different one, and cites the instance
    that proves it.
    """
    probe = _probe_module()
    reading = probe._key_kept("f_JT=ZZ", LANDED_VALUE_CONTROL)
    rendered = " ".join(probe._key_kept_lines("f_JT=ZZ", reading))

    assert reading["kept"] is True
    assert "WHETHER THE VALUE WAS APPLIED IS A DIFFERENT QUESTION" in rendered
    assert "f_JT=ZZ" in rendered
