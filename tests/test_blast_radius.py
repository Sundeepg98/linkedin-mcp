"""THE BLAST-RADIUS INSTRUMENT, shown separating a narrow pattern from a wide one.

``scripts/blast_radius.py`` answers "what would this candidate allowlist pattern
newly admit" by running the SHIPPED predicate over concrete urls twice -- once
with the candidate installed, once without -- and diffing. Never a grep over the
pattern source, which is the error this repository has paid for twice.

**A TOOL THAT REPORTS ZERO FOR EVERYTHING IS INDISTINGUISHABLE FROM A BROKEN
ONE**, so the first thing asserted here is that it separates: a narrow anchored
pattern admits exactly its own address, a wildcard over the same corpus admits
several, and the two answers differ.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "blast_radius",
    pathlib.Path(__file__).resolve().parents[1] / "scripts" / "blast_radius.py",
)
blast_radius = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(blast_radius)

from linkedin_server import readonly  # noqa: E402

BASE = "https://www.linkedin.com"

#: A corpus THIS FILE controls, so the discrimination test does not depend on
#: which real addresses happen to be on the denylist today.
SYNTHETIC = [
    f"{BASE}/zzz-probe-surface/one",
    f"{BASE}/zzz-probe-surface/two",
    f"{BASE}/zzz-probe-surface/three/deeper",
    f"{BASE}/feed/",
]


def test_a_narrow_pattern_admits_exactly_its_own_address():
    result = blast_radius.newly_admitted(
        r"^https://www\.linkedin\.com/zzz-probe-surface/one$", SYNTHETIC
    )
    assert result["newly_admitted"] == [f"{BASE}/zzz-probe-surface/one"]
    assert result["newly_refused"] == []
    assert result["tested"] == len(SYNTHETIC)


def test_a_family_wildcard_admits_the_whole_family():
    """THE DISCRIMINATION, which is what makes a zero elsewhere meaningful."""
    narrow = blast_radius.newly_admitted(
        r"^https://www\.linkedin\.com/zzz-probe-surface/one$", SYNTHETIC
    )
    wide = blast_radius.newly_admitted(
        r"^https://www\.linkedin\.com/zzz-probe-surface/.*$", SYNTHETIC
    )
    assert len(wide["newly_admitted"]) == 3
    assert len(narrow["newly_admitted"]) == 1
    assert wide["newly_admitted"] != narrow["newly_admitted"], (
        "the instrument returns the same answer for a single-address pattern "
        "and a family wildcard, so it cannot price a widening at all."
    )


def test_the_undefended_field_can_actually_fire():
    """**A FIELD THAT CANNOT FIRE CERTIFIES NOTHING**, and the first version of
    this one could not.

    It originally reported which newly-admitted addresses were on the FORBIDDEN
    ROSTER -- structurally almost always empty, because ``assert_read_url``
    consults the denylist BEFORE the allowlist, so an allowlist pattern cannot
    re-admit a refused address. Measured, not assumed: a ``.*settings.*``
    wildcard admits ZERO of the real corpus for exactly that reason.

    The field now reports the opposite and correct hazard -- newly admitted AND
    defended by nothing -- and this asserts it is non-empty on a corpus where
    that is true, which the old field could never have been.
    """
    wide = blast_radius.newly_admitted(
        r"^https://www\.linkedin\.com/zzz-probe-surface/.*$", SYNTHETIC
    )
    assert wide["newly_admitted_and_defended_by_nothing"], (
        "the field reports nothing even where three addresses were admitted "
        "with no denylist entry refusing them."
    )
    assert len(wide["newly_admitted_and_defended_by_nothing"]) == 3


def test_the_denylist_bounds_a_wildcard_and_that_is_measured():
    """The finding that corrected the instrument, pinned so it stays true.

    A settings-family wildcard over the REAL corpus admits nothing, because
    every address in that corpus matching it is already refused by a denylist
    substring. That is the denylist doing its job and it is why a blast-radius
    number is a LOWER BOUND rather than a verdict.
    """
    result = blast_radius.newly_admitted(
        r"^https://www\.linkedin\.com/.*settings.*$"
    )
    assert result["newly_admitted"] == [], (
        "a settings wildcard now admits something in the real corpus. That is "
        "a real finding rather than a test failure -- read what it admits "
        "before changing this assertion."
    )
    assert result["tested"] > 50, "the real corpus has shrunk"


def test_the_tuple_is_restored_even_when_the_measurement_raises():
    """A CRASH MID-MEASUREMENT MUST NOT LEAVE A WIDENED BOUNDARY BEHIND.

    The candidate is installed onto the live tuple and removed in a
    ``finally``. If that ever stopped being true, a failed blast-radius run
    would leave the process permitting more than the repository does -- and
    every subsequent check in the same process would be measuring a boundary
    nobody wrote.
    """
    before = readonly._ALLOWED_URL_PATTERNS
    with pytest.raises(Exception):
        blast_radius.newly_admitted("([unclosed", SYNTHETIC)
    assert readonly._ALLOWED_URL_PATTERNS is before, (
        "the allowlist tuple was not restored after a failed measurement."
    )


def test_the_corpus_is_concrete_urls_and_not_patterns():
    """Every corpus entry must be an ADDRESS, because the whole design is that
    the question is answered on addresses rather than on pattern text."""
    for url in blast_radius.corpus():
        assert url.startswith("http"), url
        for metacharacter in ("\\d", "[A-Za-z", "(?:", ".*"):
            assert metacharacter not in url, (
                f"{url!r} is a pattern fragment, not an address. A corpus of "
                "patterns would make this instrument the grep it exists to "
                "replace."
            )
