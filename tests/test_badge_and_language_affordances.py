"""The badge/language probe's two vocabularies, and its two gate indices.

WHY THIS FILE EXISTS AT ALL. `scripts/_probe_badge_and_language_affordances.py`
defines its needle vocabulary TWICE -- `NEEDLES`, which crosses into
`page.evaluate`, and `REPORT_LABELS`, which does not. That is not duplication
by accident: the shipped taint engine returned `NEEDLES` itself as tainted
because it is passed into a page call, and the taint reached a `print`. The
page-call path and the printing path may not share a name.

The cost of that fix is a NEW failure mode, and this file exists to hold it
shut. Two independent tuples can DRIFT, and if they do, the probe prints one
word beside another word's count -- silently, with every number still looking
like a number.

AND THE SECOND HALF IS WORSE. The same fix replaced two needle NAMES
(`MUST_FIND_ON_CONTROL`, `MUST_BE_ABSENT`) with two INDICES. A wrong name
raises `KeyError` on the first run. **A wrong index does not raise; it reads
a different needle and the control gate passes anyway** -- because most
needles read 0 on the control page, so an off-by-one on the must-be-absent
index checks a needle that is legitimately 0 and reports a healthy gate over
a disarmed control. That is this repository's recurring shape: an instrument
aimed at the wrong thing, reporting a clean absence.

THE DETECTOR IS FACTORED OUT of every assertion below, and
`test_the_detector_can_report_disagreement` feeds it a deliberately-wrong
pair. Without that, every passing assertion here could be passing because the
comparison is inert.
"""

from __future__ import annotations

import importlib.util
import pathlib

_PROBE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "scripts"
    / "_probe_badge_and_language_affordances.py"
)


def _load_probe():
    """Import the probe module by path. It is a script, not a package member."""
    spec = importlib.util.spec_from_file_location("_probe_badge_lang", _PROBE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _same_sequence(left, right):
    """THE DETECTOR, factored out so a passing test cannot be passing because
    the comparison is dead. Returns True only when both are the same length
    AND every position matches."""
    if len(left) != len(right):
        return False
    return all(a == b for a, b in zip(left, right))


def test_the_detector_can_report_disagreement():
    """The shown-failing half. If this passes, `_same_sequence` is not inert."""
    assert _same_sequence(("a", "b"), ("a", "b")) is True
    assert _same_sequence(("a", "b"), ("a", "c")) is False
    assert _same_sequence(("a", "b"), ("a", "b", "c")) is False


def test_the_two_vocabularies_are_byte_identical():
    """`NEEDLES` crosses into the page; `REPORT_LABELS` is printed. If they
    drift, the probe prints one word beside another word's count."""
    probe = _load_probe()
    assert _same_sequence(probe.NEEDLES, probe.REPORT_LABELS), (
        "the probe's two needle vocabularies have drifted; every printed "
        "count would be attributed to the wrong word"
    )


def test_the_gate_indices_still_name_the_needles_they_were_written_for():
    """An index is silently wrong where a name would raise.

    `MUST_FIND_ON_CONTROL_AT` must point at the needle whose presence proves
    the reader works on the control page. `MUST_BE_ABSENT_AT` must point at
    the needle no surface draws. Pointing either at a neighbour leaves a gate
    that passes over a disarmed control.
    """
    probe = _load_probe()
    assert probe.NEEDLES[probe.MUST_FIND_ON_CONTROL_AT] == "dark"
    assert probe.NEEDLES[probe.MUST_BE_ABSENT_AT] == "zzq_no_surface_draws_this"


def test_the_two_gate_indices_are_not_the_same_index():
    """A control needs both directions. One index serving both is a control
    that can only ever agree with itself."""
    probe = _load_probe()
    assert probe.MUST_FIND_ON_CONTROL_AT != probe.MUST_BE_ABSENT_AT


def test_the_must_be_absent_needle_is_not_a_product_string():
    """The must-be-absent needle earns its zero by being unutterable.

    A needle that any real surface might draw would make the control fire on
    a healthy page. This one is checked for the property that makes it safe:
    it is not a substring of any other needle in the vocabulary, so it cannot
    be matched by proximity to a real word.
    """
    probe = _load_probe()
    absent = probe.NEEDLES[probe.MUST_BE_ABSENT_AT]
    others = [n for n in probe.NEEDLES if n != absent]
    assert others, "the vocabulary holds nothing but the control needle"
    for other in others:
        assert absent not in other
        assert other not in absent


def test_no_public_name_in_the_probe_holds_page_text():
    """The probe's published surface is integers and its own literals.

    Asserted on the module rather than promised in prose: every module-level
    string constant is either a url this repository already admits or a
    needle written in the file. Nothing here is derived from a page.
    """
    probe = _load_probe()
    assert probe.CONTROL_URL == "https://www.linkedin.com/mypreferences/d/dark-mode"
    assert probe.PROFILE_URL == "https://www.linkedin.com/in/me/"
    assert isinstance(probe.NEEDLES, tuple)
    assert all(isinstance(n, str) for n in probe.NEEDLES)
