"""Show `tests/test_tool_envelopes_emit_no_page_string.py` going RED, then green.

A CHECK THAT CANNOT FAIL CERTIFIES NOTHING. The tool-envelope guard reports
`leaks 0` on the repaired tree, and a green run is exactly what a guard that
cannot fire also produces. So it is not admitted to the register on that run;
it is admitted because THIS script drives it red on a planted defect and green
again on the defect's removal, in one process, and prints both.

## THE PLANT IS NOT AN INVENTED MUTATION. IT IS THE CODE THAT SHIPPED.

Until 2026-09-20 every reader in the coercion family used ``int(...)``, which
writes the value it refused verbatim into its own ``ValueError``. That
exception leaves the reader, travels up through the tool's ``except
Exception``, and ``server._error`` renders it into ``$.message`` through
``config.scrub`` -- which substitutes this server's own PATHS and nothing else,
because a name has no shape to scrub.

**AND THE PLANT IS IMPORTED, NOT RE-WRITTEN.** ``scripts/_check_the_coercion_
family_guard_can_fail.py`` already owns this plant, including the part that is
easy to get wrong: ``dom.py`` does ``from linkedin_server.coerce import
as_count``, so rebinding ``coerce.as_count`` alone changes nothing the call
site will ever reach.

    PATCHING THE DEFINITION IS NOT PATCHING THE CALL SITE
    WHEN THE CALL SITE USED ``from ... import``.

Two copies of that walk would drift, and the drift would be invisible -- this
script would report a guard that "cannot fail" when in truth it had never been
handed a defect. So the sibling's ``_plant`` is imported and its count of
replaced bindings is printed. **A count of zero is a loud failure of THIS
script, never a pass of the guard.**

## WHAT RED LOOKS LIKE HERE, AND WHY IT IS THE RIGHT RED

The needle is supplied BY THE PAGE: ``tests.plantedpage`` answers every page
read with ``PageString(PLANT)``, and the planted ``int()`` quotes whatever it
is handed. Nothing in this script puts the plant into an exception by hand --
that would prove the envelope can carry a string, which was never in doubt.
What it proves is that a value THE PAGE CHOSE travels a real tool's real
failure path into ``$.message``, and that the guard sees it.

    venv/Scripts/python scripts/_check_the_tool_envelope_guard_can_fail.py

Exit: 0 both directions behaved, 1 the guard failed to fire, 2 it could not run.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts._check_the_coercion_family_guard_can_fail import (  # noqa: E402
    _import_everything,
    _plant,
    _remove_plant,
)
from tests.test_tool_envelopes_emit_no_page_string import (  # noqa: E402
    CLEAN,
    LEAKS,
    NOT_DRIVEN,
    RETURNS_TEXT,
    drive_all,
    sandbox_session_store,
)


def _tally(rows: list[dict]) -> dict[str, int]:
    counts = {CLEAN: 0, RETURNS_TEXT: 0, LEAKS: 0, NOT_DRIVEN: 0}
    for row in rows:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    return counts


def _print(label: str, rows: list[dict]) -> dict[str, int]:
    counts = _tally(rows)
    print(
        "  %-34s %d tools -- clean %d, returns_text %d, LEAKS %d, not_driven %d"
        % (
            label,
            len(rows),
            counts[CLEAN],
            counts[RETURNS_TEXT],
            counts[LEAKS],
            counts[NOT_DRIVEN],
        )
    )
    for row in rows:
        if row["verdict"] == LEAKS:
            print(
                "      LEAKS  %-40s %s  at %s"
                % (row["tool"], row["reason"], ",".join(row["at"]))
            )
    return counts


def main() -> int:
    with tempfile.TemporaryDirectory() as scratch:
        sandbox_session_store(scratch)
        _import_everything()

        print("BASELINE: the repaired tree, before anything is planted")
        before = drive_all()
        counts_before = _print("repaired", before)
        if counts_before[LEAKS]:
            print("\nFAIL: the tree is already leaking; nothing to prove.")
            return 2
        if counts_before[CLEAN] == 0:
            print("\nFAIL: nothing was driven clean; the harness is broken.")
            return 2

        planted = _plant()
        print("\nPLANTED: the shipped int() coercion, at %d binding(s)" % planted)
        if planted == 0:
            print("FAIL: the plant reached NOTHING. This proves nothing.")
            _remove_plant()
            return 2
        try:
            during = drive_all()
            counts_during = _print("planted", during)
        finally:
            _remove_plant()

        print("\nREMOVED: the plant is off, the tree is back")
        after = drive_all()
        counts_after = _print("repaired again", after)

        fired = counts_during[LEAKS] > 0
        recovered = counts_after[LEAKS] == 0
        print(
            "\nGUARD FIRED ON THE PLANT: %s (%d leaking)"
            % ("YES" if fired else "NO", counts_during[LEAKS])
        )
        print(
            "GUARD WENT GREEN AGAIN:   %s (%d leaking)"
            % ("YES" if recovered else "NO", counts_after[LEAKS])
        )
        if fired and recovered:
            print("\nPASS: the guard can fail, and does so only on the defect.")
            return 0
        print("\nFAIL: a guard that does not move under the shipped defect.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
