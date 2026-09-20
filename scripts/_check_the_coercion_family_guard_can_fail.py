"""Show `tests/test_readers_emit_no_page_string.py` going RED, then green.

A CHECK THAT CANNOT FAIL CERTIFIES NOTHING. This repository has found roughly
ten distinct shapes of that defect, including an identity sweep that accepted
``--help`` as a git range and printed ``PASS: 0 hits across 0 blobs``. So the
family guard is not admitted to the register on the strength of a green run; it
is admitted because THIS script drives it red on a planted defect and green
again on its removal, in one process, and prints both.

## THE PLANT IS NOT AN INVENTED MUTATION. IT IS THE CODE THAT SHIPPED.

Until 2026-09-20 every reader in the family coerced with ``int(...)``. ``int()``
puts the value it refused verbatim into its ValueError, that exception leaves
the reader, and ``server._error`` renders it through ``config.scrub`` -- which
substitutes this server's own PATHS and nothing else, because a name has no
shape to scrub. The plant below restores exactly that behaviour.

**A control whose defect is the real previous state is the strongest kind
available**, because nobody has to argue that the mutation is representative.

## WHY THE PLANT REBINDS AT EVERY IMPORT SITE, WHICH IS THE SUBTLE PART

``linkedin_server/dom.py`` does ``from linkedin_server.coerce import as_count``.
That copies the function OBJECT into ``dom``'s namespace, so rebinding
``coerce.as_count`` alone changes nothing that ``dom`` will ever call, and this
script would report a guard that "cannot fail" when in fact it had never been
given a defect.

    PATCHING THE DEFINITION IS NOT PATCHING THE CALL SITE
    WHEN THE CALL SITE USED ``from ... import``.

So :func:`_plant` walks every loaded ``linkedin_server`` module and rebinds the
helper wherever it is bound. :func:`_planted_sites` prints HOW MANY bindings it
replaced -- a count of zero is a loud failure of this script rather than a pass
of the guard, because a plant that reached nothing proves nothing.

    venv/Scripts/python scripts/_check_the_coercion_family_guard_can_fail.py

Exit: 0 both directions behaved, 1 the guard failed to fire, 2 it could not run.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from linkedin_server import coerce  # noqa: E402
from tests.test_readers_emit_no_page_string import (  # noqa: E402
    CLEAN,
    LEAKS,
    discover_readers,
    drive,
)

#: The names the plant replaces, and the pre-2026-09-20 behaviour of each --
#: which is ``int()`` reached by one route or another.
SHIPPED_DEFECT: dict[str, Callable[..., Any]] = {
    "as_int": lambda value: int(value),
    "as_count": lambda value, default=0: int(value),
    "counts_only": lambda values, default=0: (
        [int(v) for v in (values or [])],
        0,
    ),
    "scalars_only": lambda raw, names: (
        {out: int((raw or {}).get(key) or 0) for out, key in names},
        0,
    ),
}

_ORIGINALS: list[tuple[Any, str, Any]] = []


def _targets() -> list[tuple[Any, str]]:
    """Every module attribute currently bound to one of the helpers."""
    out: list[tuple[Any, str]] = []
    for name, module in list(sys.modules.items()):
        if not name.startswith("linkedin_server"):
            continue
        if module is None:
            continue
        for attr in SHIPPED_DEFECT:
            shipped = getattr(coerce, attr, None)
            if shipped is not None and getattr(module, attr, None) is shipped:
                out.append((module, attr))
    # ``search_results`` reaches the helper through its own ``_as_int``, which
    # the sibling script also plants at. Named explicitly because it is bound
    # under a DIFFERENT name and the identity scan above cannot see it.
    import linkedin_server.search_results as sr

    if hasattr(sr, "_as_int"):
        out.append((sr, "_as_int"))
    return out


def _plant() -> int:
    """Restore the shipped coercion everywhere it is bound. Returns how many."""
    for module, attr in _targets():
        _ORIGINALS.append((module, attr, getattr(module, attr)))
        replacement = SHIPPED_DEFECT.get(attr) or SHIPPED_DEFECT["as_int"]
        setattr(module, attr, replacement)
    return len(_ORIGINALS)


def _remove_plant() -> None:
    while _ORIGINALS:
        module, attr, original = _ORIGINALS.pop()
        setattr(module, attr, original)


def _import_everything() -> None:
    """Import the whole package so ``_targets`` can see every binding."""
    import importlib
    import pkgutil

    import linkedin_server

    for info in pkgutil.iter_modules(linkedin_server.__path__):
        if info.name.startswith("__"):
            continue
        try:
            importlib.import_module(f"linkedin_server.{info.name}")
        except Exception:  # noqa: BLE001
            continue


def main() -> int:
    _import_everything()
    readers = dict(discover_readers())

    print("BASELINE: the repaired tree, before anything is planted")
    before = {name: drive(fn)[0] for name, fn in readers.items()}
    leaking_before = sorted(n for n, v in before.items() if v == LEAKS)
    clean_before = sorted(n for n, v in before.items() if v == CLEAN)
    print(f"  {len(readers)} readers, {len(clean_before)} clean, "
          f"{len(leaking_before)} leaking")
    if leaking_before:
        print("  STILL LEAKING (this wave did not close these):")
        for name in leaking_before:
            print(f"    {name}")
    print()

    planted_count = _plant()
    print(f"PLANT: the shipped ``int()`` coercion, restored at "
          f"{planted_count} binding(s)")
    if planted_count == 0:
        print("FAIL: the plant reached NOTHING, so nothing below is evidence.")
        return 2
    try:
        after = {name: drive(fn)[0] for name, fn in readers.items()}
    finally:
        _remove_plant()

    restored = {name: drive(fn)[0] for name, fn in readers.items()}

    # THE SUBJECT SET IS THE READERS THIS WAVE REPAIRED: clean now, and the
    # guard must convict them the moment the shipped coercion comes back.
    subjects = [n for n in clean_before if after.get(n) == LEAKS]
    stayed_clean = [n for n in clean_before if after.get(n) != LEAKS]

    print(f"  {len(subjects)} of {len(clean_before)} clean readers went RED "
          f"under the plant")
    print()
    for name in subjects[:20]:
        print(f"    RED   {name}")
    if len(subjects) > 20:
        print(f"    ... and {len(subjects) - 20} more")
    print()

    if not subjects:
        print("FAIL: not one reader went red under the coercion that shipped.")
        print("      The guard cannot fail, so its green certifies nothing.")
        return 1

    not_cleared = [n for n in subjects if restored.get(n) != CLEAN]
    if not_cleared:
        print("FAIL: these did not go green again once the plant was removed,")
        print("      so the red above is not attributable to the plant:")
        for name in not_cleared:
            print(f"    {name} -> {restored.get(name)}")
        return 1

    print(f"PASS: {len(subjects)} reader(s) went RED under the coercion that")
    print("      shipped until 2026-09-20, and GREEN again on its removal.")
    print("      The guard fires on a real defect and clears on its repair.")
    print()
    print(f"NOT CONVICTED BY THE PLANT: {len(stayed_clean)} clean reader(s).")
    print("      That is expected and is not a gap: a reader whose values are")
    print("      already integers -- a Playwright ``count()``, a ``len()`` --")
    print("      cannot leak through a coercion, and the plant proves it by")
    print("      failing to make it leak.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
