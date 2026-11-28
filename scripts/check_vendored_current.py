"""Is each vendored jobcore module still what jobcore MASTER holds?

WHY THIS IS NOT PART OF THE DRIFT GUARD. ``tests/test_vendored_buildinfo.py``
answers a question about THIS BRANCH: does each copy match the jobcore commit
its own vendor header pins? That answer cannot change unless the branch
changes, which is what makes it safe to run on every lane.

This script answers a question about TIME: has jobcore moved on since the copy
was taken? Until 2026-11-28 the two were one comparison, made against a fresh
clone of jobcore master on every branch -- so an upstream merge that touched a
vendored module turned every branch red on its next CI run, a lane's included,
for a change that lane never made (jobcore 50da018 reached master at 13:06:38Z
that day, and the next lane run on ci/census-calls28 failed twice for it). The
question still matters -- jobcore 6acc7e6 was a path-scrubber fix a copy here
did not have -- so it is asked HERE, by ``.github/workflows/vendored-current.yml``
on master pushes and on a daily schedule, never on a ci/ ref, as its own job,
so that its red is its own and never a lane's.

WHAT IT COMPARES. For each vendored module: the copy's body below its vendor
header, against ``git show <rev>:src/jobcore/<module>.py`` in the jobcore
checkout (``--rev`` defaults to ``origin/master``, which a fresh clone has).
Line endings are normalised and nothing else, exactly as the drift guard does.

EXIT STATUS, and every answer is printed, never only implied:
    0  every copy matches jobcore at REV
    1  at least one copy differs: re-vendor it (fix upstream first)
    2  the question cannot be answered here -- no jobcore checkout, a REV that
       does not resolve, a copy with no vendor header. That is LOUD on
       purpose: an alarm that cannot look must not report all-clear.

Usage::

    python scripts/check_vendored_current.py [--jobcore DIR] [--rev REV]

``--jobcore`` defaults to the first ``<parent>/jobcore`` holding
``src/jobcore``, walking up from this file -- the sibling layout CI clones and
the one this box carries. Pure stdlib, so the workflow installs nothing.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

REPO = Path(__file__).resolve().parent.parent
PACKAGE_DIR = REPO / "linkedin_server"

#: The line every vendor header ends with; the body is everything after it.
SENTINEL = "# --- END VENDOR HEADER; everything below is verbatim from jobcore ---"

#: The jobcore modules this package vendors, as tests/test_vendored_buildinfo.py
#: names them.
VENDORED = ("buildinfo", "paths")

CURRENT, BEHIND, UNANSWERABLE = "current", "BEHIND", "UNANSWERABLE"


def find_jobcore(start: Path = REPO) -> Optional[Path]:
    """The jobcore checkout beside this repo, found the way the drift guard finds it."""
    for parent in (start, *start.parents):
        candidate = parent / "jobcore"
        if (candidate / "src" / "jobcore").is_dir():
            return candidate
    return None


def split_header(text: str) -> Tuple[Optional[str], Optional[str]]:
    """``(header, body)``, or ``(None, None)`` when there is no vendor header."""
    if SENTINEL not in text:
        return None, None
    header, _, body = text.partition(SENTINEL)
    return header, body.lstrip("\r\n")


def normalise(text: str) -> str:
    """Line endings only -- see the drift guard's ``normalise``."""
    return text.replace("\r\n", "\n")


def pinned_commit(header: str) -> Optional[str]:
    for line in header.splitlines():
        if "Vendored from jobcore commit:" in line:
            return line.split(":", 1)[1].strip()
    return None


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, encoding="utf-8",
    )


def compare(jobcore: Path, rev: str, package_dir: Optional[Path] = None,
            modules=VENDORED) -> List[Tuple[str, str, str]]:
    """``[(module, verdict, why)]`` for each vendored module, against jobcore at REV."""
    package_dir = PACKAGE_DIR if package_dir is None else package_dir
    resolved = _git(jobcore, "rev-parse", "--verify", "--short", f"{rev}^{{commit}}")
    if resolved.returncode != 0:
        why = f"{rev} does not resolve in the jobcore checkout"
        return [(module, UNANSWERABLE, why) for module in modules]
    at = resolved.stdout.strip()
    verdicts = []
    for module in modules:
        copy = package_dir / f"{module}.py"
        if not copy.is_file():
            verdicts.append((module, UNANSWERABLE, "there is no vendored copy"))
            continue
        header, body = split_header(copy.read_text(encoding="utf-8"))
        if body is None:
            verdicts.append((module, UNANSWERABLE, "the copy has no vendor header"))
            continue
        pin = pinned_commit(header) or "(no pin)"
        upstream = _git(jobcore, "show", f"{rev}:src/jobcore/{module}.py")
        if upstream.returncode != 0:
            verdicts.append((module, UNANSWERABLE, f"jobcore {rev} ({at}) has no {module}.py"))
        elif normalise(body) == normalise(upstream.stdout):
            verdicts.append((module, CURRENT, f"pin {pin} matches jobcore {rev} ({at})"))
        else:
            verdicts.append((module, BEHIND,
                             f"pin {pin} differs from jobcore {rev} ({at}): re-vendor it, "
                             f"fixing anything wrong upstream first"))
    return verdicts


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--jobcore", type=Path, default=None)
    parser.add_argument("--rev", default="origin/master")
    args = parser.parse_args(argv)
    jobcore = args.jobcore if args.jobcore is not None else find_jobcore()
    if jobcore is None or not (jobcore / "src" / "jobcore").is_dir():
        print(f"{UNANSWERABLE}: no jobcore checkout to compare against", file=sys.stderr)
        return 2
    verdicts = compare(jobcore, args.rev)
    for module, verdict, why in verdicts:
        print(f"{verdict:<12} {module:<10} {why}")
    if any(verdict == UNANSWERABLE for _, verdict, _ in verdicts):
        return 2
    return 1 if any(verdict == BEHIND for _, verdict, _ in verdicts) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
