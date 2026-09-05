"""Show the tool-count guard's CONTROL still failing after the pin moved.

WHY THIS EXISTS. Bumping a pinned count is the cheapest way in this repository
to turn a test green, so the bump from 38 to 41 is only honest if the guard's
control is still demonstrably able to fail afterwards. The rule this repo
already carries is that a check which cannot fail certifies nothing -- applied
here to the check that certifies the tool surface.

THREE DEMONSTRATIONS, and the third is the one that separates a fact from a
fake:

  A  the two RULES, run over the registry as it actually stood while the
     defect was live, must REJECT it. If they pass on a broken reading the
     control is decoration.
  B  with the live registry replaced by that broken reading, the guard's own
     tests must go RED -- all three of them, including the control.
  C  with the live registry INTACT and only the pinned number wrong, ONLY the
     count assertion may move. That is the claim written beside the bump --
     that nothing in the demonstration reads the number -- and it is the half
     a reader would otherwise have to take on trust.

Run from the repo root with the venv interpreter. Prints a PASS/FAIL line per
demonstration and exits non-zero if any of them does not behave as stated.

    ./venv/Scripts/python.exe scripts/_check_tool_count_pin_control.py

**RUN IT AFTER EVERY TOOL-COUNT BUMP, and paste the output beside the bump.**
It is tracked rather than left in a scratch directory for one reason: the pin
moves often -- the sibling assertion in ``tests/test_server_surface.py`` has
been RENAMED at every bump and the renames are visible in its history -- each
bump is a review moment somebody has to earn, and rebuilding this
demonstration from scratch each time is exactly how a review moment turns into
a number edit. (No count of past bumps is given here on purpose: this file
would then carry an unchecked number about a checked one, which is the defect
one level up.)

IT READS THE PIN OUT OF THE TEST FILE rather than carrying a copy: part C
looks for the current ``assert len(_tool_names()) == N`` line, and mutating it
in memory is how the "only the count moves" claim is tested. **So a change to
the SHAPE of that assertion breaks this script rather than silently skipping
the check** -- which is the failure mode worth having, since a demonstration
that quietly stops demonstrating is the thing it exists to catch one level up.
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tests"))

import test_every_tool_is_on_the_surface as guard  # noqa: E402

FAILURES: list[str] = []


def _report(label: str, ok: bool, detail: str = "") -> None:
    print("%-6s %s%s" % ("PASS" if ok else "FAIL", label, detail))
    if not ok:
        FAILURES.append(label)


def _red(callable_, *args) -> bool:
    """True when the assertion FAILS, which is what is being demonstrated."""
    try:
        callable_(*args)
    except AssertionError:
        return True
    return False


def main() -> int:
    broken = list(guard.REGISTRY_WHILE_BROKEN)
    live = guard._tool_names()

    print("live registry: %d tools" % len(live))
    print("broken reading: %r" % (broken,))
    print()

    # ---------------------------------------------------------------- A
    print("A. the two rules, over the registry measured while the defect was live")
    _report(
        "rule 1 (a shipped read tool is missing) rejects the broken reading",
        "linkedin_who_viewed_me" not in broken,
    )
    _report(
        "rule 2 (a private helper is on the surface) rejects the broken reading",
        [name for name in broken if name.startswith("_")] == ["_attach_recipient_ids"],
    )
    print()

    # ---------------------------------------------------------------- B
    print("B. with the live registry REPLACED by that broken reading, the guard goes red")
    original = guard._tool_names
    guard._tool_names = lambda: broken  # type: ignore[assignment]
    try:
        _report(
            "test_every_read_tool_this_package_ships_is_registered goes RED",
            _red(guard.test_every_read_tool_this_package_ships_is_registered,
                 "linkedin_who_viewed_me"),
        )
        _report(
            "test_no_private_helper_is_a_tool goes RED",
            _red(guard.test_no_private_helper_is_a_tool),
        )
        _report(
            "the CONTROL itself goes RED",
            _red(guard.test_both_rules_reject_the_registry_that_was_actually_measured),
        )
    finally:
        guard._tool_names = original  # type: ignore[assignment]
    print()

    # ---------------------------------------------------------------- C
    print("C. live registry INTACT, pinned number WRONG -- only the count may move")
    source = (REPO / "tests" / "test_every_tool_is_on_the_surface.py").read_text(
        encoding="utf-8"
    )
    # DERIVED, NOT TYPED. A hardcoded pin here would have to be edited at every
    # bump, which is the hand-maintenance this script exists to replace -- and
    # it would go stale silently, since a stale needle simply fails to match
    # and the mutation becomes a no-op that still prints PASS.
    found = re.search(r"assert len\(_tool_names\(\)\) == (\d+)", source)
    _report("the pin assertion is present and readable", bool(found))
    if not found:
        print("DEMONSTRATION FAILED: the pin assertion changed shape")
        return 1
    pinned = found.group(0)
    _report(
        "the pin agrees with the live registry (%s)" % found.group(1),
        int(found.group(1)) == len(live),
    )

    wrong = "assert len(_tool_names()) == %d" % (int(found.group(1)) - 2)
    mutated_source = source.replace(pinned, wrong)
    _report("the mutation actually changed the source", mutated_source != source)

    namespace: dict[str, object] = {}
    exec(  # noqa: S102 - executing this repo's own test file, deliberately
        compile(mutated_source, "<pin-mutated>", "exec"),
        namespace,
    )
    mutated = namespace["test_both_rules_reject_the_registry_that_was_actually_measured"]
    _report("the control goes RED on a WRONG pin", _red(mutated))

    # ...and the two rules that do NOT read the number stay green under the
    # same mutation, which is what "nothing in the demonstration reads this
    # number" actually claims.
    _report(
        "rule 1 stays GREEN under the wrong pin",
        not _red(namespace["test_every_read_tool_this_package_ships_is_registered"],
                 "linkedin_who_viewed_me"),
    )
    _report(
        "rule 2 stays GREEN under the wrong pin",
        not _red(namespace["test_no_private_helper_is_a_tool"]),
    )
    print()

    if FAILURES:
        print("DEMONSTRATION FAILED: %r" % (FAILURES,))
        return 1
    print("all demonstrations behaved as stated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
