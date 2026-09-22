"""Show `tests/test_the_search_shape_reading.py` going RED, then green.

A CHECK THAT CANNOT FAIL CERTIFIES NOTHING, and this repository has had to
remove several that could not. So the shape reading is not admitted on the
strength of a green run; it is admitted because this script drives it red on
TWO planted defects and green again on their removal, in one process, and
prints every verdict.

## THE TWO PLANTS ARE THE TWO WAYS THIS INSTRUMENT COULD HAVE BEEN WRONG

**PLANT 1 -- THE LOOSENING.** The obvious way to make a decorated label match
is to drop the single-word asymmetry from ``matchPhrase`` itself. That is the
repair ``search_results`` refuses in as many words, because ``connections`` is
a prefix of ``connections of`` and loosening collapses the degree filter into
the one whose value IS A PERSON. The plant restores that collapse.
``test_the_collision_is_not_resolved_by_the_shape_pass`` must go red.

**PLANT 2 -- THE INSTRUMENT THAT MEASURES NOTHING.** Make ``windowMatch``
identical to ``matchPhrase``. Everything still runs, ``decorated`` is
computable, every count is an integer -- and the reading adds exactly nothing,
because it can no longer see a decorated label. This is the failure mode a
green suite would never show, and it is the one worth planting: an instrument
whose output is well-formed and empty.

## PATCHING THE DEFINITION IS NOT PATCHING THE CALL SITE

``search_results`` does ``_MATCH_IN_PAGE = dom.FILTER_PANEL_JS`` at import, so
rebinding ``dom.FILTER_PANEL_JS`` alone changes nothing the lifters will ever
read, and this script would report a check that "cannot fail" when in fact it
had never been handed a defect. :func:`_plant` rebinds EVERY module-level name
bound to the script and prints how many it replaced -- **a count of zero is a
loud failure of this script, not a pass of the check.**

    venv/Scripts/python scripts/_check_the_shape_reading_can_fail.py

Exit: 0 every plant fired and the clean run was green, 1 a plant did not fire,
2 the script could not run at all.
"""

from __future__ import annotations

import pathlib
import sys
from shutil import which

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import pytest  # noqa: E402

from linkedin_server import dom, search_results  # noqa: E402

TEST_FILE = str(ROOT / "tests" / "test_the_search_shape_reading.py")

#: The shipped single-word branch, and the loosening that would delete it.
_ASYMMETRY = "      return words.length === 1 && words[0] === needle[0];"
_LOOSENED = "      return words.indexOf(needle[0]) !== -1;"

#: The shape pass's own body, and the version that measures nothing.
_WINDOW_DECL = "  const windowMatch = (haystack, phrase) => {"
_WINDOW_NOOP = (
    "  const windowMatch = (haystack, phrase) => "
    "matchPhrase(haystack, phrase);\n"
    "  const windowMatchUnused = (haystack, phrase) => {"
)


def _bindings() -> list[tuple[object, str]]:
    """Every module-level name currently bound to the panel script."""
    found: list[tuple[object, str]] = []
    for module in list(sys.modules.values()):
        name = getattr(module, "__name__", "") or ""
        if not name.startswith("linkedin_server"):
            continue
        for attribute in list(vars(module)):
            value = vars(module)[attribute]
            if isinstance(value, str) and "const windowMatch" in value:
                found.append((module, attribute))
    return found


def _plant(transform) -> int:
    replaced = 0
    for module, attribute in _bindings():
        current = getattr(module, attribute)
        setattr(module, attribute, transform(current))
        replaced += 1
    return replaced


def _run() -> int:
    return int(pytest.main(["-q", "-p", "no:cacheprovider", TEST_FILE]))


def _round(title: str, transform, expect_red: bool) -> bool:
    print("=" * 74)
    print(title)
    print("=" * 74)
    sites = _plant(transform)
    print("  bindings rebound: %d" % sites)
    if sites == 0:
        print("  THIS SCRIPT FAILED: the plant reached nothing, so the check")
        print("  was never handed a defect. That is not a pass.")
        return False
    code = _run()
    red = code != 0
    ok = red == expect_red
    print("  pytest exit %d -> %s (wanted %s)   %s"
          % (code, "RED" if red else "green",
             "RED" if expect_red else "green", "OK" if ok else "FAIL"))
    return ok


def main() -> int:
    if which("node") is None and which("node.exe") is None:
        print("REFUSING TO REPORT: node is not on PATH, so the cross-engine")
        print("tests would SKIP and a skip is not a red. This script cannot")
        print("show the check failing without an engine to fail it in.")
        return 2

    original = dom.FILTER_PANEL_JS
    assert _ASYMMETRY in original, "the shipped asymmetry moved; update this plant"
    assert _WINDOW_DECL in original, "the shipped shape pass moved; update this plant"

    good = True
    good &= _round(
        "PLANT 1 -- THE LOOSENING the module refuses "
        "(single-word asymmetry deleted)",
        lambda s: s.replace(_ASYMMETRY, _LOOSENED),
        expect_red=True,
    )
    _plant(lambda _s: original)

    good &= _round(
        "PLANT 2 -- THE INSTRUMENT THAT MEASURES NOTHING "
        "(windowMatch == matchPhrase)",
        lambda s: s.replace(_WINDOW_DECL, _WINDOW_NOOP),
        expect_red=True,
    )
    _plant(lambda _s: original)

    good &= _round(
        "CLEAN -- the shipped script, unplanted",
        lambda _s: original,
        expect_red=False,
    )

    print()
    print("RESULT: %s" % ("every plant fired and the clean run was green"
                         if good else "AT LEAST ONE ROUND MISBEHAVED"))
    return 0 if good else 1


if __name__ == "__main__":
    raise SystemExit(main())
