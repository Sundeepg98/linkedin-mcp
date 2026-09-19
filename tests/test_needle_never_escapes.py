"""The needle may live in a grant. It may NOT live anywhere durable.

THE RULING THIS ENFORCES, 2026-09-01. The operator's standing protection reads
"one label, read and discarded -- never stored, never in a grant, never in a
log", and the subject of that sentence is THE LABEL: LinkedIn's own string,
the other person's actual name, discovered by this server off the page. The
NEEDLE is a different thing -- his own word, typed by him, supplied per call --
and the grant holds it deliberately, because that is what lets the label stay
out. ``_name_the_invitation_recipient`` adds the label to a NEW dict after
``grant.preview`` is assigned, so the grant provably never held it.

WHAT THAT LEAVES, AND WHY IT IS THIS FILE. An in-memory value that expires in
120 seconds becomes a durable one by exactly two routes, and this repo's own
words are that "a name that reaches Python can reach a traceback, a log line
or a cache key". So:

  1. THE NEEDLE MUST NEVER APPEAR IN AN EXCEPTION MESSAGE. A traceback is
     written to a terminal, captured by a harness, and pasted into an issue.
  2. THE NEEDLE MUST NEVER APPEAR IN A LOG LINE. A log is a file.

Both are asserted here against the REAL functions, and both are shown failing
at the mutation that puts the needle there -- a check that has never been seen
to fail certifies nothing.

WHAT IS DELIBERATELY NOT ASSERTED: that the needle is absent from the confirm
BLOCK. It is his own word and the block is what he reads; scrubbing it there
would tell him less about what he is confirming, not more. The rule is about
durability, not about secrecy from the person who typed it.
"""

import logging

import pytest

from linkedin_server import dom, writes

#: A needle that could not occur by accident, so a substring test is decisive.
#: It carries no capital letters and no spaces, which matters: it must not be
#: mistaken for a real name by a reader of this file, and it must survive any
#: shaping unchanged so that a leak cannot be excused as "it was redacted".
NEEDLE = "zzqneedlemarkerzz"


def test_the_marker_would_actually_be_visible_if_it_leaked():
    """The control for every assertion below.

    A marker that some shaping step blanks would make every test in this file
    pass by accident. This proves it survives the two transforms this package
    puts strings through before printing them.
    """
    from linkedin_server import shape

    assert shape.census_shape(NEEDLE) == NEEDLE
    assert shape.census_redact_rare(NEEDLE, 1) == NEEDLE


def _aim_refusals():
    """Every refusal ``aim_invitation`` can produce, with a needle in play.

    Each is a ``(verdict, why, index)`` triple. These are the sentences that
    reach a caller when the aim fails, and they are the natural place for a
    needle to be interpolated by somebody trying to be helpful -- "nobody
    matched 'smith'" is a friendlier message and a durable disclosure.
    """
    return [
        ("no needle", writes.aim_invitation({"controls": 9, "matches": None})),
        ("no match", writes.aim_invitation({"controls": 9, "matches": 0})),
        ("ambiguous", writes.aim_invitation({"controls": 9, "matches": 4})),
        (
            "one match, no index",
            writes.aim_invitation({"controls": 9, "matches": 1}),
        ),
    ]


def test_no_aim_refusal_repeats_the_needle_back():
    """The four refusals are built from COUNTS, and must stay that way."""
    seen = 0
    for label, (_verdict, why, _index) in _aim_refusals():
        assert NEEDLE not in why, label
        seen += 1
    # A loop over nothing passes: name the number.
    assert seen == 4, seen


def test_the_selector_builder_cannot_carry_a_needle():
    """A click target is a string, and this one is built from an INDEX.

    The suffix anchor is the whole of what identifies these controls, so the
    person's name never enters the selector -- and neither can the needle,
    because the builder takes an integer and refuses anything else.
    """
    selector = dom.invite_control_selector(3)
    assert NEEDLE not in selector
    assert dom.INVITE_CONTROL_SUFFIX in selector
    with pytest.raises(ValueError):
        dom.invite_control_selector(NEEDLE)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "bad_needle",
    [
        "",
        "   ",
        NEEDLE + writes.TARGET_JOIN + NEEDLE,
        NEEDLE + "\n" + NEEDLE,
        NEEDLE * 500,
    ],
    ids=["empty", "blank", "separator", "newline", "too-long"],
)
def test_a_rejected_needle_does_not_come_back_in_the_exception(bad_needle):
    """THE ROUTE THAT MATTERS MOST, because it fires on the unhappy path.

    Target normalisation is where a caller's string meets a validator, and a
    validator that quotes what it rejected is the most natural code in the
    world to write. Every refusal here must describe the PROBLEM without
    repeating the value.

    The empty and blank cases are exempted from the substring check for a
    reason that is not a loophole: there is nothing in them to leak. They are
    still driven, because a normaliser that accepted them would be the actual
    defect.
    """
    spec = writes.spec_for_action("send_invitation")
    with pytest.raises(writes.WriteAttemptError) as caught:
        writes._target_for(spec, bad_needle)
    message = str(caught.value)
    if bad_needle.strip():
        assert NEEDLE not in message, message


def test_a_needle_that_is_accepted_is_returned_unchanged():
    """The other half, so this file cannot pass by refusing everything.

    A normaliser that mangled or dropped the needle would satisfy every
    assertion above and break the aim. This is the passing case.
    """
    spec = writes.spec_for_action("send_invitation")
    assert writes._target_for(spec, "  " + NEEDLE + "  ") == NEEDLE


def test_nothing_logs_the_needle_while_a_target_is_normalised(caplog):
    """A log is a file. This drives the real code and reads the real records.

    ``caplog`` at DEBUG on the package root catches every logger this package
    owns, so a helpful ``logger.debug("aiming at %s", needle)`` anywhere under
    it fails here rather than shipping.
    """
    spec = writes.spec_for_action("send_invitation")
    with caplog.at_level(logging.DEBUG, logger="linkedin_server"):
        writes._target_for(spec, NEEDLE)
        for _label, _result in _aim_refusals():
            pass
    records = " ".join(record.getMessage() for record in caplog.records)
    assert NEEDLE not in records, records
