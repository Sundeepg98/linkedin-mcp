"""His target may live in a grant. It may NOT live anywhere durable.

THE RULING THIS ENFORCES, 2026-09-01. The operator's standing protection reads
"one label, read and discarded -- never stored, never in a grant, never in a
log", and the subject of that sentence is THE LABEL: LinkedIn's own string,
the other person's actual name, discovered by this server off the page. HIS
TARGET is a different thing -- supplied by him, per call -- and the grant holds
it deliberately, because that is what lets the label stay out.
``_name_the_invitation_recipient`` adds the person to a NEW dict after
``grant.preview`` is assigned, so the grant provably never held the label.

THE TARGET CHANGED KIND ON 2026-09-27, AND THIS FILE IS NAMED FOR THE OLD ONE.
It was a NEEDLE -- his own word for the person, compared in the page against
the controls' labels. It is the person's PROFILE LINK now (lane L5, the
orchestrator's order of 23:36; PEOPLE-DATA-MITIGATIONS, mitigation 6: an
outward act fires at the exact member he names, by link or id). A link names a
person at least as surely as his word did, so the rule moves with it
unchanged. An in-memory value that expires in 120 seconds becomes a durable one
by exactly two routes, and this repo's own words are that "a name that reaches
Python can reach a traceback, a log line or a cache key". So:

  1. THE LINK MUST NEVER APPEAR IN AN EXCEPTION MESSAGE. A traceback is
     written to a terminal, captured by a harness, and pasted into an issue.
  2. THE LINK MUST NEVER APPEAR IN A LOG LINE. A log is a file.

Both are asserted here against the REAL functions -- the normaliser, the aim,
the selector builder and the rail reader -- and the reader is driven over a
page whose library error QUOTES the selector, which is how Playwright words its
errors and so the one route by which his segment could come back.

WHAT IS DELIBERATELY NOT ASSERTED: that the link is absent from the confirm
BLOCK, the grant, the press's selector or the receipt. It is his own argument;
the block is what he reads, and a receipt carries the caller-supplied target
and nothing the page drew (PREVIEW-NAMES-THE-RESOLVED-TARGET). The selector
MUST carry his segment, because the comparison runs in the page. The rule is
about durability, not about secrecy from the person who supplied it.
"""

import logging

import pytest

from linkedin_server import dom, writes
from linkedin_server.config import logger as package_logger
from linkedin_server.errors import WriteAttemptError

#: A segment that could not occur by accident, so a substring test is
#: decisive. Lower-case letters only, so it survives any shaping unchanged and
#: a leak cannot be excused as "it was redacted"; it carries ``example``, a
#: declared synthetic slug token.
SEGMENT = "zzqexamplelinkzz"
LINK = "https://www.linkedin.com/in/" + SEGMENT + "/"
#: A member id this repository already declares synthetic
#: (``tests/test_no_committed_identity.py``).
MEMBER_ID = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000002"

SPEC = writes.spec_for_action("send_invitation")


def test_the_marker_would_actually_be_visible_if_it_leaked():
    """The control for every assertion below.

    A marker that some shaping step blanks would make every test in this file
    pass by accident. This proves it survives the two transforms this package
    puts strings through before printing them.
    """
    from linkedin_server import shape

    assert shape.census_shape(SEGMENT) == SEGMENT
    assert shape.census_redact_rare(SEGMENT, 1) == SEGMENT


def _aim_answers():
    """Every answer ``aim_invitation_by_link`` can give, with a target in play.

    These are the sentences that reach a caller when the aim fails, and they
    are the natural place for a target to be interpolated by somebody trying
    to be helpful -- "nobody on your rail is /in/<segment>/" is a friendlier
    message and a durable disclosure.
    """
    return [
        ("no segment", writes.aim_invitation_by_link({"controls": 9, "matches": None}, SEGMENT)),
        ("no match", writes.aim_invitation_by_link({"controls": 9, "matches": 0}, SEGMENT)),
        ("a member id", writes.aim_invitation_by_link({"controls": 9, "matches": 0}, MEMBER_ID)),
        ("ambiguous", writes.aim_invitation_by_link({"controls": 9, "matches": 4}, SEGMENT)),
        ("aimed", writes.aim_invitation_by_link({"controls": 9, "matches": 1}, SEGMENT)),
    ]


def test_no_aim_answer_repeats_the_target_back():
    """The five answers are built from COUNTS, and must stay that way."""
    seen = []
    for label, (aim, why) in _aim_answers():
        assert SEGMENT not in why and MEMBER_ID not in why, label
        seen.append(aim)
    # A loop over nothing passes: name the number, and the answers.
    assert seen == [
        writes.INVITE_NO_MATCH,
        writes.INVITE_NO_MATCH,
        writes.INVITE_NO_MATCH,
        writes.INVITE_AMBIGUOUS,
        writes.INVITE_AIMED,
    ], seen


@pytest.mark.parametrize(
    "bad",
    [
        "",
        SEGMENT + "'",
        SEGMENT + "]",
        SEGMENT + " x",
        SEGMENT + "/x",
        SEGMENT * 13,
    ],
    ids=["empty", "quote", "bracket", "space", "slash", "too-long"],
)
def test_the_selector_builder_refuses_without_repeating_what_it_refused(bad):
    """A press target is a string, and this one is built from HIS segment --
    so the builder refuses anything that could close the expression, and
    its refusal describes the problem without repeating the value."""
    with pytest.raises(ValueError) as caught:
        dom.rail_invite_control_selector(bad)
    if bad:
        assert SEGMENT not in str(caught.value), str(caught.value)


def test_the_selector_carries_the_segment_because_the_page_compares_it():
    """The other half, so the builder cannot pass by refusing everything: an
    accepted segment is IN the selector, folded, and nothing else of his is."""
    selector = dom.rail_invite_control_selector(SEGMENT.upper())
    assert "'" + SEGMENT + "'" in selector
    assert dom.INVITE_CONTROL_SUFFIX in selector


@pytest.mark.parametrize(
    "bad_target",
    [
        "",
        "   ",
        SEGMENT,
        "https://www.linkedin.com/in/" + SEGMENT + "/details/skills/",
        "https://elsewhere.invalid/in/" + SEGMENT + "/",
        LINK + "\n" + LINK,
        "https://www.linkedin.com/in/" + SEGMENT * 8 + "/",
    ],
    ids=["empty", "blank", "bare-word", "sub-page", "off-host", "newline", "too-long"],
)
def test_a_rejected_target_does_not_come_back_in_the_exception(bad_target):
    """THE ROUTE THAT MATTERS MOST, because it fires on the unhappy path.

    Target normalisation is where a caller's string meets a validator, and a
    validator that quotes what it rejected is the most natural code in the
    world to write. Every refusal here must describe the PROBLEM without
    repeating the value -- the bare word most of all, since a bare word may
    BE a name.
    """
    with pytest.raises(WriteAttemptError) as caught:
        writes._target_for(SPEC, bad_target)
    message = str(caught.value)
    assert SEGMENT not in message, message


def test_a_target_that_is_accepted_is_his_link_made_canonical():
    """The other half, so this file cannot pass by refusing everything.

    A normaliser that mangled or dropped the target would satisfy every
    assertion above and break the aim. These are the passing cases.
    """
    assert writes._target_for(SPEC, "  " + LINK + "  ") == LINK
    assert writes._target_for(SPEC, "www.linkedin.com/in/" + SEGMENT) == LINK
    assert writes._target_for(SPEC, MEMBER_ID).endswith("/in/" + MEMBER_ID + "/")


class _QuotingLocator:
    """A locator whose count fails the way Playwright's do: QUOTING the
    selector it was handed -- which carries his segment."""

    def __init__(self, selector):
        self._selector = selector

    async def count(self):
        raise RuntimeError("waiting for locator(%r)" % self._selector)


class _QuotingPage:
    def locator(self, selector):
        return _QuotingLocator(selector)


async def test_a_library_error_quoting_the_selector_reaches_neither_the_reading_nor_a_log(
    caplog,
):
    """THE ONE ROUTE BY WHICH HIS SEGMENT COULD COME BACK: a library error
    whose message quotes the selector. The reader keeps the error's TYPE."""
    with caplog.at_level(logging.DEBUG, logger=package_logger.name):
        reading = await dom.read_invitation_rail(_QuotingPage(), SEGMENT)
    assert reading["error"] == "RuntimeError", reading
    assert SEGMENT not in repr(reading)
    records = " ".join(record.getMessage() for record in caplog.records)
    assert records, "the unreadable rail was not logged at all"
    assert SEGMENT not in records, records


def test_nothing_logs_the_target_while_it_is_normalised_or_aimed(caplog):
    """A log is a file. This drives the real code and reads the real records.

    ``caplog`` at DEBUG on THE PACKAGE'S LOGGER -- ``linkedin``, the one every
    module logs through (``config.logger``) -- so a helpful
    ``logger.debug("aiming at %s", link)`` anywhere in the package fails here
    rather than shipping.

    THE NAME IS THE FINDING. Until 2026-09-27 this test set DEBUG on a logger
    called ``linkedin_server``, which nothing logs through: the package logger
    stayed at INFO and every DEBUG line was dropped before capture, so the
    absence this asserts could not fail for a debug record. Measured when the
    rewrite's first control -- "was the unreadable rail logged at all?" -- read
    an empty channel. The control record below keeps the channel honest.
    """
    with caplog.at_level(logging.DEBUG, logger=package_logger.name):
        package_logger.debug("caplog control: the package logger is heard at DEBUG")
        writes._target_for(SPEC, LINK)
        writes._target_for(SPEC, MEMBER_ID)
        for bad in (SEGMENT, LINK + "\n" + LINK):
            with pytest.raises(WriteAttemptError):
                writes._target_for(SPEC, bad)
        answers = _aim_answers()
        dom.rail_invite_control_selector(SEGMENT)
    assert len(answers) == 5
    records = " ".join(record.getMessage() for record in caplog.records)
    assert "the package logger is heard at DEBUG" in records, "the channel is deaf"
    assert SEGMENT not in records and MEMBER_ID not in records, records
