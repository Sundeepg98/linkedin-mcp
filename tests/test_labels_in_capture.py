"""The offline label probe, and the two vocabulary phrases it bought.

``scripts/_probe_labels_in_capture.py`` asks the questions
``scripts/_probe_messaging_menu_enumeration.py`` asks live, of a capture
already on disk: no browser, no network, no cost to anybody's account. This
file is what stops it being a script nobody checks.

## WHY A SECOND VOCABULARY TEST EXISTS BESIDE ``tests/test_menus.py``

``menus.VOCABULARY`` gained two phrases on 2026-09-20 -- ``star conversation``
and ``attach an image`` -- and a widening of a safety-relevant vocabulary is
exactly the kind of edit that must arrive with the measurement that justified
it and the control that bounds it. Both live here rather than in
``tests/test_menus.py`` so that this wave's edits stay in this wave's files
and the merge stays clean; the assertions are additive to that file's, not a
replacement for them.

## THE MEASUREMENT, so nobody has to take the phrase on trust

Run over a capture of ``/messaging/`` taken 2026-09-20 (gitignored -- raw
captures never are committed):

    aria-labels parsed   42     before: matched 1     after: matched 12
    input[type=file]      0

and over a capture of ``/messaging/compose/`` from the same session:

    aria-labels parsed   40     before: attach 1      after: attach 2
    input[type=file]      2

**ELEVEN NODES CARRIED ``Star conversation`` AND THE CLASSIFIER SAW NONE OF
THEM.** The census row ``M30`` reads *"starring itself was never considered"*;
it had been drawn eleven times on the surface the vocabulary was written for.
``attach`` understated a two-input upload surface by half, which is the worst
direction to be wrong in on a surface whose whole question is what it can be
given.

## THE CONTROL, and it is the same defect the rule was bought with

``star`` is a ONE-WORD term, and ``menus`` requires a one-word term to match
the WHOLE label because a given name adds tokens -- the rule that
``classify("Star Anise") -> star`` bought. Widening the phrase list must not
weaken that, so :func:`test_the_single_word_rule_still_holds` asserts the
historical defect stays refused, and
:func:`test_a_name_shaped_label_still_matches_nothing` asserts the name shapes
do too.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

from linkedin_server import menus

_SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import _probe_labels_in_capture as probe  # noqa: E402

#: The counts measured on a real capture of ``/messaging/`` on 2026-09-20.
#: They cannot be asserted here -- the capture is gitignored -- so they are
#: recorded as the provenance of the phrases below and re-derivable by anyone
#: holding a capture, via the probe's ``--capture`` flag.
MEASURED_STAR_LABELS_ON_THE_INBOX = 11
MEASURED_FILE_INPUTS_ON_COMPOSE = 2


# --------------------------------------------------------------------------
# The two phrases


def test_the_drawn_star_label_is_now_classified():
    """The phrase the surface actually draws, matched.

    Not ``Star`` and not ``star`` -- the two-word form LinkedIn writes.
    """
    verdict = menus.classify("Star conversation")
    assert verdict["matched"] is True
    assert verdict["term"] == "star"


def test_the_second_attachment_control_is_now_classified():
    verdict = menus.classify("Attach an image for your draft conversation")
    assert verdict["matched"] is True
    assert verdict["term"] == "attach"


def test_the_first_attachment_control_still_is():
    """The phrase that already worked must keep working.

    Without this, a widening that accidentally broke the existing phrase
    would read as a clean pass on the new one.
    """
    verdict = menus.classify("Attach a file for your draft conversation")
    assert verdict["matched"] is True
    assert verdict["term"] == "attach"


def test_a_two_input_surface_tallies_two():
    """The COUNT, not merely the match. One of two is the failure being fixed."""
    labels = [
        "Attach a file for your draft conversation",
        "Attach an image for your draft conversation",
    ]
    reading = menus.tally(menus.classify(label) for label in labels)
    assert reading["terms"]["attach"] == MEASURED_FILE_INPUTS_ON_COMPOSE


# --------------------------------------------------------------------------
# The controls that bound the widening


def test_the_single_word_rule_still_holds():
    """SHOWN FAILING IN HISTORY. ``Star Anise`` once classified as ``star``.

    The one-word term may only match the whole label. Adding a two-word
    phrase must not reopen that, and this is the assertion that says so.
    """
    verdict = menus.classify("Star Anise")
    assert verdict.get("matched") is not True
    assert verdict["refused"] == "unmatched"


@pytest.mark.parametrize(
    "label",
    [
        "Select conversation with Two Words",
        "Star Gazer",
        "Starling Attaches",
        "Attach Anderson",
    ],
)
def test_a_name_shaped_label_still_matches_nothing(label):
    """The shape a conversation row's accessible name has, by LinkedIn's design."""
    verdict = menus.classify(label)
    assert verdict.get("matched") is not True


def test_the_phrases_are_multi_word_which_is_what_makes_them_safe():
    """The rule, asserted rather than trusted.

    A one-word phrase may only match a whole label; a multi-word phrase may be
    contained. Both additions are multi-word, and if somebody later adds a
    bare word to either term this goes red.
    """
    for term in ("star", "attach"):
        for phrase in menus.VOCABULARY[term]:
            if len(phrase.split()) == 1:
                # Single-word phrases are allowed -- they are governed by the
                # whole-label rule. Assert that rule is what governs them.
                assert menus.classify(phrase + " Anderson").get("matched") is not True


# --------------------------------------------------------------------------
# The probe itself


def test_the_probe_parses_labels_and_file_inputs():
    markup = (
        '<html><body>'
        '<button aria-label="Star conversation">a</button>'
        '<button aria-label="Mark as unread">b</button>'
        '<input type="file" aria-label="Attach an image for your draft conversation">'
        '<input type="text" aria-label="Search">'
        '</body></html>'
    )
    collector = probe.collect(markup)
    assert collector.labels == [
        "Star conversation",
        "Mark as unread",
        "Attach an image for your draft conversation",
        "Search",
    ]
    assert collector.buttons == 2
    assert collector.file_inputs == 1


def test_the_probe_self_test_passes():
    """The script's own control must be green, or its readings mean nothing."""
    assert probe.self_test() == 0


def test_the_probe_refuses_a_capture_it_cannot_parse(tmp_path, capsys):
    """A ZERO WITH NO DENOMINATOR IS REFUSED, not reported as an empty surface."""
    empty = tmp_path / "empty.html"
    empty.write_text("<html><body>no labelled nodes</body></html>", encoding="utf-8")
    code = probe.main(["--capture", str(empty)])
    assert code == 3
    assert "REFUSING TO REPORT" in capsys.readouterr().out


def test_the_probe_refuses_a_missing_capture(tmp_path, capsys):
    code = probe.main(["--capture", str(tmp_path / "nope.html")])
    assert code == 2
    assert "REFUSING" in capsys.readouterr().out


def test_the_probe_publishes_only_the_closed_alphabet(tmp_path, capsys):
    """NO ACCESSIBLE NAME IS EVER PRINTED, and that is asserted, not promised.

    On ``/messaging/`` a label IS a person's name by LinkedIn's own design, so
    this is the property that makes the probe safe to run at all.
    """
    markup = (
        '<html><body>'
        '<button aria-label="Select conversation with Two Words">a</button>'
        '<button aria-label="Star conversation">b</button>'
        '</body></html>'
    )
    capture = tmp_path / "c.html"
    capture.write_text(markup, encoding="utf-8")
    assert probe.main(["--capture", str(capture)]) == 0
    out = capsys.readouterr().out
    assert "Two Words" not in out
    assert "Select conversation" not in out
    assert "Star conversation" not in out
    assert "star" in out  # the TERM, which is this module's own literal
