"""Refuse a COMMIT that is about to carry an identifier.

WHY THIS EXISTS, AND IT IS NOT THAT THE RULES WERE MISSING
----------------------------------------------------------
On 2026-09-04 four identity exposures were reported here. Two of them were
prose about the guard rather than values. Of the two that were real, the shape
guard ``tests/test_no_committed_identity.py`` **already had a rule for each**
-- ``MEMBER_TOKEN_SHAPE`` and ``URN_ID_SHAPE``, over tracked AND untracked
files -- and it was RED, naming ``tests/test_writes.py`` by path and by class.

It stayed red across EIGHT commits.

Nothing read it. ``.git/hooks`` is empty, and ``.github/workflows/ci.yml`` runs
the whole suite but only ``on: push`` -- and this repository is under a push
freeze, so CI had not seen a single one of those commits. Between a commit and
the disk there was nothing at all. **A guard nobody runs is not weaker than no
guard; it is worse, because its green is quoted.**

WHAT THIS ASKS THAT NEITHER EXISTING INSTRUMENT ASKS
-----------------------------------------------------
* the shape guard reads the WORKING TREE;
* the exact-value sweep reads TRACKED FILES ON DISK;
* this reads the INDEX -- the bytes ``git commit`` is about to write.

Those are three different questions and the third is the one that was failing.
A staged blob can differ from both of the others: ``git add`` a file, edit it
back, and the tree is clean while the commit still carries the identifier.

IT OWNS NO RULES OF ITS OWN, deliberately. Every shape comes from
``hits_in``; every exemption comes from ``DECLARED_PLANTS``; the exact-value
half reuses the sweep's own ``load_wordlist`` and its path allowlist. A gate
carrying a second copy of the rules would drift from the guard, and the drift
would show up as this passing while the suite is red -- which is precisely the
state it exists to end.

Usage:
    python scripts/identity_gate.py             # gate the staged change
    python scripts/identity_gate.py --show      # ...and print matched lines

Install (the lead's call, not a script's -- it gates every writer in a shared
tree, and this repo runs many at once):
    printf '#!/bin/sh\nexec python scripts/identity_gate.py\n' \
        > .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

Exit: 0 clean, 1 the commit carries something, 2 the gate could not run.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tests.test_no_committed_identity import (  # noqa: E402
    BINARY_SUFFIXES,
    DECLARED_PLANTS,
    HASHY,
    hits_in,
)

SWEEP_PATH = REPO / "scripts" / "sweep_tracked_for_identity.py"


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(REPO), capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def staged_paths() -> list[str]:
    """Paths this commit will add, copy, modify or rename.

    ``D`` is absent on purpose: a deletion carries no bytes forward.
    """
    proc = _git("diff", "--cached", "--name-only", "--diff-filter=ACMR")
    if proc.returncode != 0:
        raise SystemExit(f"git diff --cached failed: {proc.stderr}")
    return [line for line in proc.stdout.splitlines() if line.strip()]


def staged_blob(rel: str) -> str | None:
    """The INDEX version of ``rel``, which is what a commit writes.

    Not the working-tree version. ``git add`` a file and edit it back and the
    two disagree; the commit takes this one.
    """
    proc = _git("show", f":{rel}")
    return proc.stdout if proc.returncode == 0 else None


def redact(line: str) -> str:
    """The line's SHAPE. A pre-commit hook prints to a terminal and a log."""
    return re.sub(r"[A-Za-z0-9]", "x", line.strip())[:70]


def _sweep_module():
    spec = importlib.util.spec_from_file_location("_identity_sweep", SWEEP_PATH)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def shape_findings(rel: str, text: str) -> list[tuple[str, str]]:
    """Unallowed shape hits in one staged blob, minus this file's declared plants."""
    if Path(rel).suffix.lower() in BINARY_SUFFIXES or HASHY.search(rel):
        return []
    counted: dict[str, list[str]] = {}
    for name, value in hits_in(text):
        counted.setdefault(name, []).append(value)
    out: list[tuple[str, str]] = []
    for name, values in sorted(counted.items()):
        allowed = DECLARED_PLANTS.get((rel, name), 0)
        for value in values[allowed:]:
            out.append((name, value))
    return out


def value_findings(module, rel: str, text: str) -> list[tuple[str, str]]:
    """Exact-value hits, using the sweep's own wordlist and path allowlist."""
    if module is None or rel in module.ALLOWED:
        return []
    lowered = text.lower()
    out: list[tuple[str, str]] = []
    for name, spellings in module.load_wordlist().items():
        for spelling in spellings:
            if spelling.lower() in lowered:
                out.append((name, "<exact value, class %s>" % name))
                break
    return out


def main() -> int:
    show = "--show" in sys.argv
    paths = staged_paths()
    if not paths:
        print("identity gate: nothing staged.")
        return 0

    module = None
    if SWEEP_PATH.exists():
        try:
            module = _sweep_module()
            module.load_wordlist()
        except SystemExit:
            # The wordlist is gitignored and absent on a fresh clone. SAY SO --
            # a silent half-run is the defect this whole family is about.
            print(
                "identity gate: the EXACT-VALUE half did not run (the wordlist "
                "_audit/_sanitisation_key.json is absent). The SHAPE half below "
                "ran and needs nothing."
            )
            module = None

    findings: list[tuple[str, str, str]] = []
    for rel in paths:
        text = staged_blob(rel)
        if text is None:
            continue
        for name, value in shape_findings(rel, text):
            findings.append((rel, name, value))
        for name, value in value_findings(module, rel, text):
            findings.append((rel, name, value))

    print(f"identity gate: {len(paths)} staged path(s) read from the INDEX")
    if not findings:
        print("PASS: the staged change carries no identifier this gate can see.")
        return 0

    for rel, name, value in findings:
        print(f"  BLOCKED {rel} [{name}]  {value if show else redact(value)}")
    print(
        f"\nFAIL: {len(findings)} finding(s) in the staged change.\n"
        "Substitute a synthetic value OF THE SAME SHAPE and declare it -- do not\n"
        "delete the value, which stops the test testing what it was built for.\n"
        "If the value is genuinely synthetic, declare it where its class is\n"
        "allowlisted rather than widening a rule."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
