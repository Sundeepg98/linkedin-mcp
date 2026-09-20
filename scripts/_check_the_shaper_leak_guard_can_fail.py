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
# THE SAME DEFECT IN THE SIBLING READERS -- FILED, NOT FIXED
# ---------------------------------------------------------------------------
#
# `search_results.py` was repaired 2026-09-20. `anchors.py` and
# `collections_page.py` carry the same `int((raw or {}).get(...))` shape. This
# drives THEIR real reader functions with the same plant, so the filing in
# `_audit/2026-09-20-the-search-admission.md` section 7 is REPRODUCIBLE FROM A
# CLONE rather than a number somebody wrote down.
#
# IT IS A SURVEY AND NOT A GATE. It prints and does not fail the script,
# because those modules are another surface's and repairing them inside an
# admission commit would widen that commit's blast radius past the surface it
# was sent to close. A future wave repairs them and this turns green on its
# own -- which is the point of leaving it runnable.

#: The plant. Long, and carrying ``example`` so the identity guard passes it on
#: sight -- the same reasoning as the guard file's own plants.
_SIBLING_PLANT = "Exampleperson Markersurname"

#: A superset payload: every key any of these readers reads, one a string.
_SIBLING_PAYLOAD = {
    "anchors": 1,
    "counts": [_SIBLING_PLANT],
    "headings": 1,
    "numeric_entity": 0,
    "non_numeric_entity": 0,
    "groupings": [_SIBLING_PLANT],
    "collections": [_SIBLING_PLANT],
}


class _PlantedPage:
    async def evaluate(self, script, arg=None):
        return _SIBLING_PAYLOAD


def _sibling_survey() -> int:
    import asyncio

    from tests.leakwalk import walk

    from linkedin_server import anchors, collections_page

    def carries(obj) -> bool:
        return any(_SIBLING_PLANT in text for _, text in walk(obj))

    print("SIBLING SURVEY -- the same coercion, in readers this wave did NOT fix")
    print()
    rows = (
        ("search_results.read_results (REPAIRED)", search_results.read_results),
        ("anchors.read_anchors", anchors.read_anchors),
        ("collections_page.read_collections", collections_page.read_collections),
    )
    leaking = []
    for label, reader in rows:
        try:
            out = asyncio.run(reader(_PlantedPage()))
            verdict = "LEAKS in result" if carries(out) else "clean"
        except BaseException as exc:  # noqa: BLE001 -- the exception is the subject
            verdict = (
                f"LEAKS via {type(exc).__name__}" if carries(exc)
                else f"raises clean ({type(exc).__name__})"
            )
        if "LEAKS" in verdict:
            leaking.append(label)
        print(f"  {label:42s} {verdict}")
    print()
    if leaking:
        print(f"FILED, NOT FIXED: {len(leaking)} sibling reader(s) still carry it:")
        for label in leaking:
            print(f"  {label}")
        print("  The repair is _as_int / _counts_only / _scalars_only in")
        print("  linkedin_server/search_results.py, copied. See")
        print("  _audit/2026-09-20-the-search-admission.md section 7.")
    else:
        print("No sibling leaks. If this was non-empty before, somebody fixed them;")
        print("delete section 7's filing rather than leaving a closed row open.")
    # The survey never fails the script: see the note above.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
