"""Narrow the READING surface for third-party names added in a commit range.

THIS IS NOT A GUARD, AND THE DAY SOMEBODY CITES IT AS ONE IT HAS DONE HARM.

This repository's own measured law is that **no shape-based predicate catches a
name**: ``census_substitute`` returns a person's name UNCHANGED -- it carries no
urn, no ``/in/`` path, no possessive and no six-digit run, so every marker such
a predicate looks for is absent. That is why the remedy for names is STRUCTURAL
(``groups.py``: no name is a parameter of any function in the module, asserted
on ``inspect.signature``) rather than a filter.

So this does something cheaper and honest. It lists the CAPITALISED TWO-TOKEN
RUNS that a commit range ADDED to tracked files, so that a person can read a few
dozen candidates instead of a few thousand lines. It is a reading aid. The
reading is still the check.

**IT OVER-REPORTS BY DESIGN.** UI labels (``Easy Apply``, ``Top Voice``,
``Saved Items``), product names (``Marketing Solutions``), filenames
(``Last Version``) and ordinary prose all match. That is correct: a list that
suppressed them would need rules about which capitalised pairs are "safe", and
those rules are precisely where a real name would hide.

**IT UNDER-REPORTS STRUCTURALLY, AND THIS IS THE PART TO REMEMBER.** It cannot
see a single-token name, a lowercase name, an ALL-CAPS name, or a name embedded
without a capitalised neighbour. ``--selftest`` demonstrates those misses
deliberately, because an instrument whose blind spot is only described gets read
as if it had none.

**A CLEAN RUN THEREFORE PROVES ONE THING ONLY:** nothing of THIS SHAPE was
added in that range. It never proves no name was added.

WHY THE RANGE MATTERS. Run it over what is NEW. A wave that has been reading
live LinkedIn pages is exactly when a third party's name enters a tree, and the
range since that wave started is a few thousand lines rather than a few hundred
thousand.

    ./venv/Scripts/python.exe scripts/name_shaped_runs_in_range.py <base>
    ./venv/Scripts/python.exe scripts/name_shaped_runs_in_range.py --selftest

MEASURED 2026-09-19 over ``96df35b..HEAD`` -- 4993 added lines across 24 tracked
files reduced to 22 distinct runs, all of which read clean on inspection: six
fictional names a test file declares as invented at the point of use, nine
LinkedIn UI labels, two deliberate non-person substitutes, a filename, and two
nonsense sentinels. Twenty-two lines to read instead of 4993.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections import defaultdict
from typing import Iterable, Iterator

REPO = __file__.rsplit("\\", 2)[0] if "\\" in __file__ else __file__.rsplit("/", 2)[0]

#: Two capitalised word-tokens in a row. Hyphens and apostrophes are allowed
#: INSIDE a token because real surnames carry them, and a pattern that split on
#: them would miss exactly the surnames least likely to be invented.
RUN = re.compile(
    r"\b[A-Z][a-z]{2,}(?:[-'][A-Z][a-z]+)?\s+[A-Z][a-z]{2,}(?:[-'][A-Z][a-z]+)?\b"
)

#: NOT an allowlist of safe VALUES -- a list of line CONTEXTS where a
#: capitalised run is structurally not a person's name in data. Deliberately two
#: entries: every addition here is a place this aid stops looking, and a long
#: list would quietly become the silencer this repo already has a scar about.
#: Comment lines are not dropped, only reported separately, for the same reason.
PROSE_LINE = re.compile(r"^\s*(#|//|\*)|^\s*(import|from)\s")


def runs_in(lines: Iterable[str]) -> dict[str, int]:
    """Every capitalised two-token run in ``lines``, with its count."""
    found: dict[str, int] = defaultdict(int)
    for line in lines:
        for match in RUN.finditer(line):
            found[match.group(0)] += 1
    return dict(found)


def added_lines(base: str) -> Iterator[tuple[str, str]]:
    """``(path, text)`` for every line ADDED in ``base..HEAD``."""
    proc = subprocess.run(
        ["git", "diff", f"{base}..HEAD", "--unified=0", "--no-color",
         "--diff-filter=AM"],
        cwd=REPO, capture_output=True, text=True, errors="replace",
    )
    if proc.returncode != 0:
        raise SystemExit(f"git diff failed:\n{proc.stderr}")
    path = None
    for line in proc.stdout.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
        elif line.startswith("+") and not line.startswith("+++") and path:
            yield path, line[1:]


def selftest() -> int:
    """Show it speaking, AND show it silent where it is blind.

    The second half is the point. An instrument that only demonstrates its
    successes is read as if it had no failures, and this one has large ones.
    """
    ok = True

    def check(label: str, lines: list[str], needle: str, expect_found: bool) -> None:
        nonlocal ok
        found = needle in runs_in(lines)
        verdict = "PASS" if found == expect_found else "FAIL"
        if found != expect_found:
            ok = False
        print(f"  {verdict}  {label}")

    print("IT SPEAKS -- a name of this shape is reported:")
    check("two capitalised tokens in a string",
          ['    recipient = "Quenlow Braithmore"'], "Quenlow Braithmore", True)
    check("a hyphenated surname",
          ['    x = "Quenlow Braithmore-Vask"'], "Quenlow Braithmore-Vask", True)
    check("inside prose, not only in code",
          ["# the row named Quenlow Braithmore was retired"],
          "Quenlow Braithmore", True)

    print("IT IS BLIND -- these are REAL misses, demonstrated not described:")
    check("a SINGLE-token name is invisible",
          ['    recipient = "Quenlow"'], "Quenlow", False)
    check("a lowercase name is invisible",
          ['    slug = "quenlow braithmore"'], "quenlow braithmore", False)
    check("an ALL-CAPS name is invisible",
          ['    x = "QUENLOW BRAITHMORE"'], "QUENLOW BRAITHMORE", False)

    print()
    print("A clean run means: nothing of THIS SHAPE was added.")
    print("It does NOT mean no name was added. Read the structural rule in")
    print("groups.py for the thing that actually holds.")
    return 0 if ok else 1


def main() -> int:
    args = [a for a in sys.argv[1:] if a]
    if "--selftest" in args:
        return selftest()
    base = args[0] if args else "origin/master"

    in_code: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    in_prose: dict[str, int] = defaultdict(int)
    files: set[str] = set()
    total = 0

    for path, text in added_lines(base):
        total += 1
        files.add(path)
        if PROSE_LINE.search(text):
            for value in runs_in([text]):
                in_prose[value] += 1
        else:
            for value, count in runs_in([text]).items():
                in_code[value][path] += count

    print(f"range        {base}..HEAD")
    print(f"added lines  {total} across {len(files)} tracked files")
    print(f"distinct     {len(in_code)} in code, {len(in_prose)} in comments/prose")
    print()
    print("IN CODE (strings, data, assertions) -- READ EVERY ONE:")
    for value, where in sorted(in_code.items(), key=lambda kv: -sum(kv[1].values())):
        paths = ", ".join(sorted(where))
        print(f"  {sum(where.values()):>3}x  {value!r:<34} {paths[:90]}")
    print()
    print(f"IN COMMENTS/PROSE -- {len(in_prose)} distinct:")
    for value, count in sorted(in_prose.items(), key=lambda kv: -kv[1]):
        print(f"  {count:>3}x  {value!r}")
    print()
    print("This is a reading aid, not a guard. A clean run proves only that")
    print("nothing of this SHAPE was added -- never that no name was added.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
