"""Sweep the BLOBS of a commit range for known-real identity values.

WHY THIS EXISTS, and it is a scar rather than a feature request.

``sweep_tracked_for_identity.py`` reads tracked files AS THEY ARE ON DISK. A
clean working tree therefore says NOTHING about what a push would publish: a
value can be removed in a follow-up commit -- which is the correct remedy in a
tree several waves are writing to -- and still sit in every earlier blob.

On 2026-09-05 three separate people needed that reading, could not get it from
the shipped sweep, and each wrote their own. **All three were broken**, and the
first two were caught only because a control fired. The third printed

    sweeping blobs with 0 spellings
      <sha> ... classes hit: NONE   (and five more, all NONE)

**An empty needle set matches nothing, and its NONE is not a result.** Six
all-clear lines under one line that said the instrument was mute.

The repo already had the rule -- *when a repo ships an instrument, IMPORT IT;
do not reimplement it to point at a different corpus* -- and the rule did not
prevent its own violation three times in one day. **A rule that keeps being
broken from the same motive is a MISSING TOOL, not a missing reminder.** The
motive was identical every time: wanting the sweep aimed somewhere its
enumeration does not reach. This file is that somewhere.

WHAT MAKES IT DIFFERENT FROM THE THREE BROKEN ONES

1. It IMPORTS ``load_wordlist`` and ``redact`` from the shipped sweep. It does
   not parse the key, does not filter values, does not build spellings. Every
   one of the three failures was in exactly that re-derivation -- the key's
   prose fields swallowed as values, ``_ignore_values`` not applied, or (the
   third) the already-expanded return value re-parsed as raw json, yielding
   nothing at all.
2. **IT REFUSES TO REPORT A GREEN IT CANNOT BACK.** If the needle set is empty
   it exits NON-ZERO saying it cannot speak, instead of printing a clean sweep.
   A zero from a working instrument and a zero from a mute one are the same
   character, and this is the one defect this file exists to make impossible.
3. It prints the needle COUNT on every run, above the findings, so the reading
   arrives with its own denominator.
4. It never prints a matched value -- file, line number and class only, plus
   the shipped ``redact`` shape.

USAGE

    ./venv/Scripts/python.exe scripts/sweep_blobs_for_identity.py <range>

``<range>`` is anything ``git rev-list`` accepts; it defaults to the unpushed
commits (``@{upstream}..HEAD``), falling back to all of ``HEAD`` when there is
no upstream. Exit status is 0 for a clean sweep, 1 for hits, 2 for a mute
instrument.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from sweep_tracked_for_identity import load_wordlist, redact  # noqa: E402

#: Blob paths worth sweeping. The key itself and the denylists legitimately
#: hold real values; the shipped sweep exempts them by exact path and so does
#: this one, by the same names, so the two agree about what is exempt.
SKIP_SUFFIXES = ("_sanitisation_key.json",)


def _git(*args: str) -> str:
    out = subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True, errors="replace"
    )
    return out.stdout


def _default_range() -> str:
    if _git("rev-parse", "--abbrev-ref", "@{upstream}").strip():
        return "@{upstream}..HEAD"
    return "HEAD"


def main(argv: list[str]) -> int:
    rev_range = argv[1] if len(argv) > 1 else _default_range()

    wordlist = load_wordlist()
    spellings = [(cls, s) for cls, values in wordlist.items() for s in values]

    # ------------------------------------------------------------------
    # THE MUTE CHECK. This is the whole reason the file exists and it runs
    # BEFORE anything is swept, so no reassuring output can precede it.
    # ------------------------------------------------------------------
    print(f"needles: {len(spellings)} spellings across {len(wordlist)} classes")
    if not spellings:
        print(
            "REFUSING TO SWEEP: the needle set is EMPTY.\n"
            "  A sweep with no needles matches nothing and its clean result\n"
            "  would be a statement about this instrument, not about the\n"
            "  blobs. Three hand-rolled versions of this check reported\n"
            "  exactly that all-clear on 2026-09-05. Fix the key, not this\n"
            "  message."
        )
        return 2

    commits = _git("rev-list", rev_range).split()
    print(f"range  : {rev_range} -> {len(commits)} commit(s)")

    seen: set[str] = set()
    hits: list[tuple[str, str, int, str, str]] = []
    blobs = 0
    for commit in commits:
        for row in _git("ls-tree", "-r", commit).splitlines():
            meta, _, path = row.partition("\t")
            parts = meta.split()
            if len(parts) < 3 or parts[1] != "blob":
                continue
            sha = parts[2]
            if sha in seen or path.endswith(SKIP_SUFFIXES):
                continue
            seen.add(sha)
            blobs += 1
            text = _git("cat-file", "-p", sha)
            if not text:
                continue
            folded = text.casefold()
            found = {cls for cls, s in spellings if s.casefold() in folded}
            if not found:
                continue
            for number, line in enumerate(text.splitlines(), 1):
                low = line.casefold()
                for cls, s in spellings:
                    if s.casefold() in low:
                        hits.append((sha[:9], path, number, cls, redact(line)))
                        break

    print(f"swept  : {blobs} distinct blob(s)")
    print()
    if not hits:
        print(f"PASS: 0 hits across {blobs} blobs, {len(spellings)} needles.")
        return 0

    paths = sorted({h[1] for h in hits})
    print(f"FAIL: {len(hits)} hit(s) in {len(paths)} distinct path(s).")
    print("PURGE SCOPE -- the blobs a rewrite would have to reach:")
    for sha, path, number, cls, shape in hits:
        print(f"  {sha}  {path}:{number}  [{cls}]  {shape}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
