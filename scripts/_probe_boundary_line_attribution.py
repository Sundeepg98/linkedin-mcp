"""Does the digest move BECAUSE OF MY LINE, or because of something else?

THE PROBLEM THIS EXISTS FOR. A re-freeze commit says ``old -> new`` and a
reader has to take on trust that the arrow is about the line the commit adds.
In a tree several waves write to, that is exactly the sentence that has been
wrong: a neighbour's entry lands in the same tuple in the same minute and rides
the same digest move, silently.

THE CHECK. Drop the lines carrying a NEEDLE from the source, re-run the SHIPPED
``ast_digest`` over what is left, and compare against the PREVIOUSLY PINNED
value. If the tree minus my line hashes to exactly what was pinned before, then
nothing else rode in.

IT IMPORTS THE INSTRUMENT RATHER THAN REBUILDING IT. ``ast_digest`` lives in
``tests/test_readonly_boundary_invariant.py`` and is imported from there. This
repository has measured, four separate times, that a reimplemented instrument
is broken on its first attempt; the digest is the last place to find that out.

TWO CONTROLS RUN FIRST AND A FAILURE OF EITHER VOIDS THE MEASUREMENT:

    control A  a needle NO LINE CARRIES must drop 0 lines and move 0 digests.
               An instrument that reports a move for a no-op is measuring its
               own edit, not the tree.
    control B  dropping a DIFFERENT, pre-existing entry must land on a digest
               that is neither the old pin nor the new one. A check that
               returns the pinned value for any deletion proves nothing.

Usage:

    python scripts/_probe_boundary_line_attribution.py <needle> <expected-old-digest>

No page is loaded and no address is printed: needles are read from argv and
echoed back only as a COUNT of lines dropped.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "tests"))

from test_readonly_boundary_invariant import ast_digest  # noqa: E402

_SOURCE = _ROOT / "linkedin_server" / "readonly.py"
_STRUCTURE = "_ALLOWED_URL_PATTERNS"

#: A needle that appears in no line of readonly.py. Control A.
_ABSENT_NEEDLE = "zzz-this-string-is-in-no-line-of-the-boundary-zzz"
#: A pre-existing entry unrelated to the line under test. Control B.
_OTHER_ENTRY_NEEDLE = "jobs/collections/recommended"


def _digest_without(source: str, needle: str) -> tuple[str, int]:
    """Digest of the source with every line carrying ``needle`` removed."""
    kept: list[str] = []
    dropped = 0
    for line in source.splitlines(keepends=True):
        if needle in line:
            dropped += 1
            continue
        kept.append(line)
    return ast_digest("".join(kept))[_STRUCTURE], dropped


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[-4].strip())
        return 2
    needle, expected_old = argv[1], argv[2]
    source = _SOURCE.read_text(encoding="utf-8")

    at_tree = ast_digest(source)[_STRUCTURE]

    absent_digest, absent_dropped = _digest_without(source, _ABSENT_NEEDLE)
    if absent_dropped != 0 or absent_digest != at_tree:
        print("CONTROL A FAILED: a needle no line carries changed something.")
        print(f"  lines dropped {absent_dropped} (expected 0)")
        print(f"  digest moved  {absent_digest != at_tree} (expected False)")
        return 1

    other_digest, other_dropped = _digest_without(source, _OTHER_ENTRY_NEEDLE)
    if other_dropped == 0:
        print("CONTROL B FAILED: the control entry is not in this tree.")
        return 1
    if other_digest in {expected_old, at_tree}:
        print("CONTROL B FAILED: dropping an unrelated entry landed on a")
        print("  pinned value, so this check cannot tell lines apart.")
        return 1

    subject_digest, subject_dropped = _digest_without(source, needle)
    if subject_dropped == 0:
        print("NO MEASUREMENT: the needle matched no line in the source.")
        return 1

    print(f"structure            {_STRUCTURE}")
    print(f"digest AT THE TREE   {at_tree}")
    print(f"previously pinned    {expected_old}")
    print(f"lines dropped        {subject_dropped}")
    print(f"digest MINUS them    {subject_digest}")
    print()
    print(f"control A  absent needle -> 0 lines, digest unmoved   PASS")
    print(f"control B  unrelated entry -> {other_digest}  (neither pin)  PASS")
    print()
    if subject_digest == expected_old:
        print("ATTRIBUTED. The tree minus these lines hashes to exactly the")
        print("previously pinned value, so nothing else rode in on this move.")
        return 0
    print("NOT ATTRIBUTED. The tree minus these lines does NOT hash to the")
    print("previous pin -- something else moved this structure too. Do not")
    print("write a single-addition narrative; recompute against the tree as")
    print("it now stands.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
