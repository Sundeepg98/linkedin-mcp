"""Refuse a commit that would put a KNOWN-REAL identity value into history.

WHY THIS EXISTS, with two receipts from one afternoon.

The exact-value sweep (``scripts/sweep_tracked_for_identity.py``) is correct and
was being run -- but a sweep is a READING WITH A TIMESTAMP, and in a tree with a
dozen concurrent writers that timestamp expires in minutes. Both receipts have
the same shape: a PASS, then a FAIL two to ten minutes later, with files
committed in the window.

    ~16:47  PASS: 0 hits across 291 files
    ~16:57  FAIL: 3 hits.  Three probe scripts entered the index between.

    ~18:57  PASS: 0 hits across 314 files
    ~18:59  FAIL: 1 hit.   Eighteen files entered the index between.

Each was caught by a person or an agent choosing to re-run the sweep at the
right moment. **That is a discipline, and a discipline does not survive a
session nobody is supervising.** This hook is the same rule as a MECHANISM: it
runs at the one instant that actually matters, which is the moment a blob is
about to be written.

WHAT IT CHECKS, and what it deliberately does not.

It checks the STAGED CONTENT of the files this commit would write, against the
exact-value wordlist only. It is fast because it reads the index rather than the
tree, and precise because a value from that list is a LITERAL EQUALITY rather
than an inference.

**It does NOT run the shape-based guard.** ``tests/test_no_committed_identity``
covers that, it is slower, and it produces judgement calls -- a hook that asks a
committer to adjudicate a shape at commit time will be bypassed within the hour.
**A hook that is bypassed is worse than no hook**, because its presence implies
a check nobody is running.

THE ONE THING IT MUST NEVER DO: print the matched value. A hook's output goes to
a terminal, a transcript and often a CI log. It reports the FILE, the LINE and
the CLASS, and it masks the span exactly as the sweep does. The whole point is to
keep the value out of places like this one.

FAIL-OPEN, DELIBERATELY, IN EXACTLY TWO CASES.

If the wordlist is missing (it is gitignored, so a fresh clone has no copy) or
the sweep module cannot be imported, this hook ALLOWS the commit and says so on
stderr. It is a second line of defence, not the boundary: refusing every commit
in a checkout that legitimately lacks the key would train everybody to pass
``--no-verify``, and that habit would then be in place on the day it mattered.
Any other error still refuses.

INSTALL (local, not tracked, per-checkout):

    printf '#!/bin/sh\\nexec ./venv/Scripts/python.exe scripts/pre_commit_identity_gate.py\\n' \\
        > .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit

BYPASS, when you genuinely need it: ``git commit --no-verify``. Documented rather
than hidden -- an undocumented bypass gets discovered at the worst moment.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SWEEP = REPO / "scripts" / "sweep_tracked_for_identity.py"
#: A value shorter than this matches ordinary prose. The sweep uses the same
#: floor and for the same reason.
MIN_LENGTH = 5


def _load_wordlist():
    """Return {class: {spelling}}, or None when the key is legitimately absent."""
    if not SWEEP.exists():
        return None
    spec = importlib.util.spec_from_file_location("_sweep", SWEEP)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_wordlist()


def _staged_paths() -> list[str]:
    """Paths this commit would write. Deletions are not content and are skipped."""
    proc = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=str(REPO), capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise SystemExit("pre-commit: git diff --cached failed:\n" + proc.stderr)
    return [line for line in proc.stdout.splitlines() if line.strip()]


def _staged_content(path: str) -> str | None:
    """The content AS STAGED, which is what the blob will hold.

    Reading the working tree here would be the exact mistake this repo already
    recorded: a clean tree says nothing about what a commit contains.
    """
    proc = subprocess.run(
        ["git", "show", ":" + path], cwd=str(REPO),
        capture_output=True, text=True, errors="replace",
    )
    return None if proc.returncode != 0 else proc.stdout


def _mask(line: str) -> str:
    """The line's SHAPE, never its content -- same rule as the sweep."""
    return re.sub(r"[A-Za-z0-9]", "x", line.strip())[:70]


def main() -> int:
    try:
        wordlist = _load_wordlist()
    except SystemExit:
        # load_wordlist() exits when the gitignored key is absent.
        wordlist = None
    except Exception as exc:  # noqa: BLE001 - a broken import must not block work
        print(f"pre-commit: identity gate could not load ({type(exc).__name__}); "
              f"ALLOWING. tests/test_no_committed_identity still applies.",
              file=sys.stderr)
        return 0

    if not wordlist:
        print("pre-commit: identity wordlist absent (it is gitignored); ALLOWING. "
              "The shape-based guard still applies.", file=sys.stderr)
        return 0

    hits: list[tuple[str, int, str, str]] = []
    for path in _staged_paths():
        content = _staged_content(path)
        if content is None:
            continue
        folded_lines = content.splitlines()
        for number, line in enumerate(folded_lines, start=1):
            low = line.casefold()
            for klass, spellings in wordlist.items():
                for value in spellings:
                    if len(value) >= MIN_LENGTH and value.casefold() in low:
                        hits.append((path, number, klass, _mask(line)))
                        break
                else:
                    continue
                break

    if not hits:
        return 0

    print("", file=sys.stderr)
    print("COMMIT REFUSED: staged content carries a KNOWN-REAL identity value.",
          file=sys.stderr)
    print("", file=sys.stderr)
    for path, number, klass, shape in hits:
        print(f"  {path}:{number}  [{klass}]  {shape}", file=sys.stderr)
    print("", file=sys.stderr)
    print("This is an EXACT-VALUE match against the de-anonymisation key, so it is",
          file=sys.stderr)
    print("a literal equality rather than an inference: the usual 'a red guard means",
          file=sys.stderr)
    print("UNDECLARED, never REAL' caution does not apply to this class.",
          file=sys.stderr)
    print("", file=sys.stderr)
    print("Fix the CONTENT, not the guard. Prefer a rename or a placeholder over a",
          file=sys.stderr)
    print("declaration -- a declaration permanently widens what the guard tolerates.",
          file=sys.stderr)
    print("The value is deliberately not printed above; run the sweep if you need",
          file=sys.stderr)
    print("to find it, and do not paste it anywhere.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Deliberate bypass: git commit --no-verify", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
