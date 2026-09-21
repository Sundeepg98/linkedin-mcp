"""THE SHAPE READING: telling an ABSENT filter from a DECORATED one.

## THE AMBIGUITY THIS EXISTS TO BREAK

``dom.FILTER_PANEL_JS``'s ``matchPhrase`` requires a SINGLE-WORD phrase to BE
the whole normalised label. That asymmetry is load-bearing -- it is what keeps
the degree filter (``connections``, a closed taxonomy) apart from the
person-valued one (``connections of``, whose value IS A PERSON) -- and it has a
cost this repository measured live on 2026-09-21:

    A single-word term reading 0 cannot distinguish
    "the page does not draw this control" from
    "the page draws it with a decorated label".

Five census rows are blocked on exactly that ambiguity and nothing else --
``N 80``, ``N 81``, ``N 88``, ``N 89``, ``N 93``, the five single-word terms in
the shipped vocabulary other than the one that already banked. Three separate
audit documents name this instrument as unbuilt, one of them calling it "still
the smallest unbuilt instrument here".

## WHAT WAS ADDED, AND WHAT WAS DELIBERATELY NOT

``windowMatch`` is the SAME token window WITHOUT the single-word asymmetry, and
``decorated[i]`` counts controls the shipped matcher REFUSED which nonetheless
carry term ``i`` as a whole word. **``matchPhrase`` is untouched.** Loosening it
is the repair the module refuses in as many words, because loosening is exactly
what would let ``connections`` match ``Connections of <a person>``.

## THE READING IS DECISIVE IN ONE DIRECTION ONLY, AND THAT IS TESTED HERE

``decorated == 0`` with ``counts == 0`` is ABSENT -- a real finding. A nonzero
``decorated`` is UNDECIDED and never *present*, because this vocabulary's own
collision can raise it without the filter existing. :func:`search_results.
shape_verdict` owns that rule so no wave re-derives it in prose, and
``test_a_nonzero_shape_reading_is_never_read_as_present`` is what stops it being
quietly widened later.

## INTEGERS ONLY, STILL

The shape pass runs IN THE PAGE for the same reason the match does: a label on
this surface can be a person's name. ``decorated`` is a count of CONTROLS and
carries no word count, deliberately -- a word count of a label reading
``Connections of <a person>`` is a fact about that person's name.

Shown failing by ``scripts/_check_the_shape_reading_can_fail.py``, on two
plants: the loosening the module refuses, and an instrument that reports
nothing. A check that cannot fail certifies nothing.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import textwrap
from shutil import which
from typing import Any

import pytest

import plantedpage
from linkedin_server import dom, search_results


def _node() -> str | None:
    for name in ("node", "node.exe"):
        found = which(name)
        if found:
            return found
    return None


def _drive(pairs: list[tuple[str, str]]) -> list[list[bool]]:
    """Run the SHIPPED normaliser, matcher and window matcher under V8.

    Lifted by brace-matching, never transcribed -- so this drives THE
    ARTIFACT and not a copy of it, exactly as the matcher's own corpus test
    does.
    """
    driver = textwrap.dedent(
        """
        %s;
        %s;
        %s;
        const pairs = %s;
        console.log(JSON.stringify(pairs.map((p) => [
          matchPhrase(normaliseLabel(p[0]), p[1]),
          windowMatch(normaliseLabel(p[0]), p[1])
        ])));
        """
    ) % (
        search_results.filter_normaliser_source(),
        search_results.filter_matcher_source(),
        search_results.filter_window_matcher_source(),
        json.dumps([list(pair) for pair in pairs]),
    )
    handle, path = tempfile.mkstemp(suffix=".mjs")
    os.close(handle)
    try:
        with open(path, "w", encoding="utf-8") as stream:
            stream.write(driver)
        proc = subprocess.run([_node(), path], capture_output=True, text=True)
    finally:
        os.remove(path)
    assert proc.returncode == 0, proc.stderr[:2000]
    return json.loads(proc.stdout)


_SKIP = (
    "THE SHAPE READING WAS NOT DRIVEN: node is not on PATH, so the shipped "
    "windowMatch in dom.FILTER_PANEL_JS was NOT run under a real engine in "
    "this session. The decorated-label discrimination -- including the "
    "connections / connections-of collision it must NOT resolve -- was not "
    "checked here."
)


def test_the_decorated_case_is_what_separates_absent_from_undecided() -> None:
    """A decorated label reads 0 whole and 1 window. That IS the instrument."""
    if _node() is None:
        pytest.skip(_SKIP)
    (bare, decorated, absent) = _drive(
        [
            ("Connections", "connections"),
            ("Degree of connections", "connections"),
            ("Anise Starfield", "connections"),
        ]
    )
    assert bare == [True, True], "a bare control must match both ways"
    assert decorated == [False, True], (
        "THE WHOLE POINT: the shipped matcher refuses a decorated label and "
        "the window finds it. Without this the zero is uninterpretable."
    )
    assert absent == [False, False], (
        "and a label carrying the word nowhere must fire neither reading, or "
        "ABSENT means nothing"
    )


def test_the_collision_is_not_resolved_by_the_shape_pass() -> None:
    """``Connections of <a person>`` must NOT be readable as a degree filter.

    This is the test that makes the shape reading safe to add at all. The
    window match fires on that label for the bare term ``connections`` -- so
    if a caller read a nonzero ``decorated`` as *present*, the person-valued
    filter would be reported as the degree filter, which is precisely the
    scar the single-word asymmetry exists for.
    """
    if _node() is None:
        pytest.skip(_SKIP)
    (two_word, bare_term) = _drive(
        [("Connections of", "connections of"), ("Connections of", "connections")]
    )
    assert two_word[0] is True, "the two-word term still matches its own label"
    assert bare_term[0] is False, (
        "the single-word asymmetry must still refuse -- if this ever passes, "
        "matchPhrase has been loosened and the two filters have collapsed"
    )
    assert bare_term[1] is True, (
        "the window DOES fire here, which is exactly why a nonzero decorated "
        "is UNDECIDED and never present"
    )
    assert search_results.shape_verdict(0, 1) == "undecided"


def test_the_shape_pass_can_only_fire_for_a_single_word_term() -> None:
    """Structural, over the WHOLE shipped vocabulary -- not a sample.

    A multi-word phrase already matches by containment, so ``decorated`` is 0
    for it by construction. Stating that as a property over every term is what
    turns "we think it only affects the single-word ones" into a measurement,
    and it is the invariant that would break first if ``windowMatch`` were
    quietly widened.
    """
    if _node() is None:
        pytest.skip(_SKIP)
    terms = search_results.FILTER_TERMS
    driven = _drive([("zzz %s zzz" % term, term) for term in terms])
    for term, (whole, window) in zip(terms, driven):
        can_fire = (not whole) and window
        assert can_fire == (len(term.split()) == 1), (
            "term %r: decorated fire-ability must track single-wordness "
            "exactly; got whole=%r window=%r" % (term, whole, window)
        )


def test_a_nonzero_shape_reading_is_never_read_as_present() -> None:
    """The interpretation rule, pinned. Three verdicts, and no collapsing."""
    assert search_results.shape_verdict(1, 0) == "present"
    assert search_results.shape_verdict(1, 5) == "present"
    assert search_results.shape_verdict(0, 0) == "absent"
    assert search_results.shape_verdict(0, 1) == "undecided"
    assert set(search_results.SHAPE_VERDICTS) == {
        "present",
        "absent",
        "undecided",
    }
    for whole in range(3):
        for decorated in range(3):
            assert (
                search_results.shape_verdict(whole, decorated)
                in search_results.SHAPE_VERDICTS
            )


class _StringAnsweringPage:
    """A page that answers the shape key with a STRING, as a page may."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    async def evaluate(self, *_args: Any, **_kwargs: Any) -> dict[str, Any]:
        return self._payload


@pytest.mark.asyncio
async def test_the_shape_reading_is_coerced_like_every_other_page_value() -> None:
    """A string in ``decorated`` is REFUSED AND COUNTED, never carried out.

    The hazard is the sharper one on this surface: the thing a filter control
    holds that is not an integer is its LABEL, and a label here reads
    ``Connections of <a person>``.
    """
    reading = await search_results.read_filters(
        _StringAnsweringPage(
            {
                "controls": 8,
                "counts": [0] * len(search_results.FILTER_TERMS),
                "decorated": [plantedpage.PLANT, 1]
                + [0] * (len(search_results.FILTER_TERMS) - 2),
                "matched_controls": 0,
                "unmatched_controls": 8,
                "empty_labels": 0,
            }
        )
    )
    assert plantedpage.PLANT not in json.dumps(reading), (
        "a page string reached the reader's return value"
    )
    assert reading["decorated"][0] == 0, "the refused entry is substituted"
    assert reading["decorated"][1] == 1, "and POSITION is preserved"
    assert reading["values_refused"] >= 1, (
        "the substitution must be COUNTED -- a reader that cannot say why it "
        "is empty is the green this repository distrusts most"
    )


@pytest.mark.asyncio
async def test_the_shape_reading_survives_a_page_that_omits_it() -> None:
    """An older page shape answering no ``decorated`` key is not a crash.

    ``read_filters`` runs against whatever the page returns, and a missing key
    must read as a zero-length list rather than raising -- the same contract
    ``counts`` already has.
    """
    reading = await search_results.read_filters(
        _StringAnsweringPage(
            {
                "controls": 3,
                "counts": [1] + [0] * (len(search_results.FILTER_TERMS) - 1),
                "matched_controls": 1,
                "unmatched_controls": 2,
                "empty_labels": 0,
            }
        )
    )
    assert reading["decorated"] == []
    assert isinstance(reading["values_refused"], int)


def test_the_shape_pass_adds_no_evaluate_waiver() -> None:
    """It extends an existing call site. The waiver budget is at its cap.

    ``tests/test_readonly.py`` caps ``dom.py`` at 22 waived ``evaluate``
    lines and the file sits at exactly 22. An instrument that cost a
    twenty-third would have needed a ruling, not a commit.
    """
    source = dom.__file__
    with open(source, encoding="utf-8") as stream:
        waived = sum(
            1
            for line in stream.read().splitlines()
            if line.strip().endswith("# readonly-ok")
        )
    assert waived <= 22, (
        "the shape reading must extend the existing read_search_filters "
        "evaluate, never add one; waivers now %d" % waived
    )


def test_the_page_script_returns_no_label_on_the_shape_path() -> None:
    """``decorated`` is a count of CONTROLS and carries no label, no word count.

    Read off the shipped script's own source rather than asserted about it, so
    a future edit that starts returning a label has to break this.
    """
    script = dom.FILTER_PANEL_JS
    start = script.index("return {")
    tail = script[start:script.index("};", start)]
    emitted = {
        line.split(":", 1)[1].strip().rstrip(",")
        for line in tail.splitlines()
        if ":" in line and not line.strip().startswith("//")
    }
    # THE VALUES, NOT THE KEYS. ``empty_labels`` is a key containing the
    # substring "label" and a count of labels that were empty -- a naive
    # substring sweep over this block convicts it, which is why this reads
    # the right-hand sides.
    allowed = {
        "controls.length",
        "counts",
        "decorated",
        "matchedControls",
        "unmatchedControls",
        "emptyLabels",
    }
    assert "decorated" in emitted, "the shape reading must be returned"
    assert emitted <= allowed, (
        "the panel script's RETURN must carry integers only; unexpected "
        "value expressions %r" % (emitted - allowed)
    )
    # AND THE SHAPE PASS MUST NOT HAVE STARTED CARRYING A WORD COUNT, which
    # is the one integer here that would be a fact about a person's name.
    assert "words.length" not in tail
