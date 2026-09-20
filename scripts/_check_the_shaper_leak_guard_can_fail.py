"""Show `tests/test_the_search_shaper_emits_no_name.py` going RED, then green.

A CHECK THAT CANNOT FAIL CERTIFIES NOTHING, and this repository has found
roughly ten distinct shapes of that defect -- including an identity sweep that
accepted ``--help`` as a git range and printed ``PASS: 0 hits across 0 blobs``.
So the name-freedom guard is not admitted to the register on the strength of a
green run; it is admitted because THIS script drives it red on a planted
defect and green again on removal, in one process, and prints both.

## THE PLANT IS NOT AN INVENTED MUTATION. IT IS THE CODE THAT SHIPPED.

Until 2026-09-20 both readers coerced with ``int(value)``. ``int()`` puts the
value it refused verbatim into its ValueError, that exception leaves the
reader, and ``server._error`` renders it through ``config.scrub`` -- which
substitutes this server's own PATHS and nothing else, because a name has no
shape to scrub. The plant below restores exactly that behaviour by pointing
``search_results._as_int`` back at ``int``.

**A control whose defect is the real previous state is the strongest kind
available**, because nobody has to argue that the mutation is representative.

    venv/Scripts/python scripts/_check_the_shaper_leak_guard_can_fail.py

Exit: 0 both directions behaved, 1 the guard failed to fire, 2 it could not run.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from linkedin_server import search_results  # noqa: E402
from tests import test_the_search_shaper_emits_no_name as guard  # noqa: E402

#: The assertions that must go red under the plant. Each takes the same two
#: parameters the suite parametrises them on, so the plant is exercised at the
#: real call site rather than at a convenient one.
UNDER_TEST = (
    ("read_results", "a string inside counts"),
    ("read_results", "a string in the anchors scalar"),
    ("read_filters", "a string inside counts"),
)


def _plant() -> None:
    """Restore the pre-2026-09-20 coercion: ``int()``, which quotes its input."""
    search_results._as_int = lambda value: int(value)  # noqa: E731


def _remove_plant() -> None:
    search_results._as_int = _SHIPPED


_SHIPPED = search_results._as_int


def _verdict(reader_name: str, case: str) -> str:
    """Run the guard once. ``red`` means it caught the leak, which is the win."""
    try:
        guard.test_no_plant_crosses_the_reader_by_any_path(reader_name, case)
    except AssertionError as exc:
        return "red" if "planted name or slug" in str(exc) else "red(other)"
    except BaseException as exc:  # noqa: BLE001
        return f"error:{type(exc).__name__}"
    return "GREEN"


def main() -> int:
    print("PLANT: search_results._as_int -> int(), the coercion that shipped")
    print()
    planted: dict[tuple[str, str], str] = {}
    _plant()
    try:
        for case in UNDER_TEST:
            planted[case] = _verdict(*case)
    finally:
        _remove_plant()

    restored = {case: _verdict(*case) for case in UNDER_TEST}

    width = max(len(f"{a}/{b}") for a, b in UNDER_TEST)
    print(f"  {'case'.ljust(width)}   planted   restored")
    for case in UNDER_TEST:
        label = f"{case[0]}/{case[1]}".ljust(width)
        print(f"  {label}   {planted[case]:9s} {restored[case]}")
    print()

    failed_to_fire = [c for c in UNDER_TEST if planted[c] != "red"]
    failed_to_clear = [c for c in UNDER_TEST if restored[c] != "GREEN"]

    if failed_to_fire:
        print("FAIL: the guard stayed green on the defect it exists to catch:")
        for case in failed_to_fire:
            print(f"  {case} -> {planted[case]}")
        return 1
    if failed_to_clear:
        print("FAIL: the guard did not go green once the plant was removed, so")
        print("      the red above is not attributable to the plant:")
        for case in failed_to_clear:
            print(f"  {case} -> {restored[case]}")
        return 1

    print(f"PASS: {len(UNDER_TEST)} of {len(UNDER_TEST)} went RED under the")
    print("      shipped-until-today coercion and GREEN again on its removal.")
    print("      The guard fires on a real defect and clears on its repair.")
    print()
    return _sibling_survey()


# ---------------------------------------------------------------------------
# THE SAME DEFECT IN THE SIBLING READERS -- NOW MEASURED ACROSS THE FAMILY
# ---------------------------------------------------------------------------
#
# THIS SURVEY USED TO LIE, AND THE WAY IT LIED IS WORTH KEEPING WRITTEN DOWN.
#
# Until 2026-09-20 it drove the siblings with a hand-written superset payload:
#
#     {"anchors": 1, "counts": [plant], "headings": 1, "groupings": [plant],
#      "collections": [plant]}
#
# and reported `collections_page.read_collections` **clean**. It was not clean.
# That reader reads `raw.get("matches")` -- and `matches` was not a key in that
# payload, so the list came back empty, the comprehension iterated nothing, and
# the coercion never ran. THE READER WAS NEVER DRIVEN, AND "NOT DRIVEN" PRINTED
# AS "CLEAN". The audit `_audit/2026-09-20-the-search-admission.md` section 7
# inherited that as a measured fact, and it was not one.
#
# A HAND-WRITTEN PAYLOAD CAN ONLY EXERCISE THE KEYS ITS AUTHOR THOUGHT OF --
# the same defect as a leak detector that is a list of known-bad strings, which
# `tests/leakwalk.py` already records having learned twice.
#
# So the payload is gone. This now calls the family harness in
# `tests/plantedpage.py`, whose page answers EVERY key and whose key vocabulary
# is harvested from the package source rather than typed out, and it surveys
# EVERY page reader in the package rather than three named ones.
#
# IT IS A SURVEY AND NOT A GATE, unchanged: it prints and does not fail the
# script. The gate is `tests/test_readers_emit_no_page_string.py`, and the
# proof that THAT can fail is `scripts/_check_the_coercion_family_guard_can_fail.py`.


def _sibling_survey() -> int:
    from tests.test_readers_emit_no_page_string import (
        CLEAN,
        LEAKS,
        RETURNS_TEXT,
        discover_readers,
        drive,
    )

    print("FAMILY SURVEY -- every page reader in the package, driven by a")
    print("page that answers in strings. See tests/plantedpage.py.")
    print()

    verdicts = {name: drive(fn)[0] for name, fn in discover_readers()}
    buckets: dict[str, int] = {}
    for verdict in verdicts.values():
        key = verdict.split(":")[0]
        buckets[key] = buckets.get(key, 0) + 1

    print(f"  {len(verdicts)} readers discovered")
    for label, count in sorted(buckets.items(), key=lambda kv: -kv[1]):
        print(f"    {label:14s} {count:4d}")
    print()

    leaking = sorted(n for n, v in verdicts.items() if v == LEAKS)
    if leaking:
        print(f"LEAKING VIA AN EXCEPTION -- {len(leaking)} reader(s):")
        for name in leaking:
            print(f"  {name}")
        print("  The repair is linkedin_server/coerce.py: as_count, as_int,")
        print("  counts_only, scalars_only. See")
        print("  _audit/2026-09-20-the-coercion-leak.md.")
    else:
        print("No reader carries a page string out through an exception.")
    print()
    returns_text = sum(1 for v in verdicts.values() if v == RETURNS_TEXT)
    clean = sum(1 for v in verdicts.values() if v == CLEAN)
    print(f"  {clean} clean, {returns_text} return page text BY CONTRACT")
    print("  (a text reader returning text is the shapers' subject, not this")
    print("  one -- see the note on RETURNS_TEXT in the guard).")
    # The survey never fails the script: see the note above.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
