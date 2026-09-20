"""Three captures, or one page captured three times? OVERLAP ANSWERS IT.

## THE AMBIGUITY THIS EXISTS FOR, AND IT IS NOT HYPOTHETICAL

``_probe_premium_collections_live.py`` fired ``read_job_collection`` at
``/jobs/search/``, ``/jobs/collections/top-applicant`` and
``/jobs/collections/top-choice`` on 2026-09-20 and all three reported
**exactly 25 slots**. Three different addresses agreeing to the posting is the
signature of a REDIRECT -- one page served three times -- and it is also what
LinkedIn's own page window looks like if the window is 25. **Nothing in the
reading separated those.**

A count cannot. Two pages holding 25 postings each report 25 whether they hold
the same 25 or a disjoint 25. **The identity of the set is the discriminator,
and it is available offline, on captures already paid for, for zero page
loads.**

    disjoint sets        ->  different collections. The count agreeing is the
                             window size, not a redirect.
    identical sets       ->  ONE PAGE. Every per-collection number is a
                             restatement of one reading and NOTHING BANKS.
    partial overlap      ->  different collections drawn from a shared pool,
                             which is what two Premium job collections ARE.

## IT READS GITIGNORED CAPTURES AND PUBLISHES INTEGERS

A capture holds his name, his connections' names and his account ids, which is
why captures live in ``_state/`` and are never committed. **Nothing that
crosses this process boundary is page-derived except integers**: set sizes,
intersection sizes and a ratio. No posting id is printed, no title, no href --
the ids are read, compared, counted, and discarded.

**AND IT PRINTS WHAT IT DID NOT FIND.** A capture named here and absent from
disk is reported as ABSENT rather than skipped, because a missing file that
silently drops out of a comparison turns a two-way agreement into a one-way
one and nothing in the output says so.

    ./venv/Scripts/python.exe scripts/_compare_collection_captures.py
"""

from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

STATE = pathlib.Path(__file__).resolve().parent.parent / "_state"

#: THE SLOT TIER, which is the only tier whose id is present for every posting.
#: The same attribute ``linkedin_server/job_collections.py`` counts, and the
#: same digit shape: a non-numeric segment is a slug and a slug is a name.
SLOT_ID = re.compile(r'data-occludable-job-id="([0-9]{6,20})"')

#: The captures to compare, label -> filename. An entry is a CLAIM that the
#: file is a capture of that surface; a missing one is reported, never skipped.
CAPTURES: dict[str, str] = {
    "control jobs-search": "cap-control-jobs-search.html",
    "top-applicant": "cap-collection-top-applicant.html",
    "top-choice": "cap-collection-top-choice.html",
    "recommended (prior)": "cap-jobs-recommended.html",
    "jobs-search (prior)": "cap-jobs-search.html",
}


def _ids(path: pathlib.Path) -> set[str]:
    """Every slot id in a capture, as a SET. The file's text goes no further."""
    return set(SLOT_ID.findall(path.read_text(encoding="utf-8", errors="replace")))


def main() -> int:
    print("=== PER CAPTURE. Sizes only.")
    sets: dict[str, set[str]] = {}
    for label, name in CAPTURES.items():
        path = STATE / name
        if not path.exists():
            print(f"    {label:<22}: ABSENT from _state -- not compared below")
            continue
        found = _ids(path)
        sets[label] = found
        print(f"    {label:<22}: chars={path.stat().st_size:>9}  distinct slots={len(found):>3}")

    if len(sets) < 2:
        print("\n    FEWER THAN TWO CAPTURES. Nothing to compare, and that is")
        print("    a fact about this disk rather than about the surfaces.")
        return 1

    print("\n=== PAIRWISE OVERLAP. An IDENTICAL set means one page.")
    labels = list(sets)
    identical: list[tuple[str, str]] = []
    for index, left in enumerate(labels):
        for right in labels[index + 1:]:
            a, b = sets[left], sets[right]
            shared = len(a & b)
            union = len(a | b)
            ratio = (shared / union) if union else 0.0
            note = ""
            if a and a == b:
                note = "  <-- IDENTICAL SET: THESE ARE ONE PAGE"
                identical.append((left, right))
            elif not shared:
                note = "  <-- DISJOINT: different collections"
            print(f"    {left:<22} vs {right:<22} "
                  f"|A|={len(a):>3} |B|={len(b):>3} shared={shared:>3} "
                  f"union={union:>3} jaccard={ratio:.3f}{note}")

    print("\n=== VERDICT")
    if identical:
        print("    AT LEAST ONE PAIR IS THE SAME PAGE. Every per-collection")
        print("    number taken from that pair is one reading restated, and")
        print("    NOTHING BANKS for the duplicated surface:")
        for left, right in identical:
            print(f"      {left} == {right}")
        return 1
    print("    NO PAIR IS IDENTICAL. The counts agreeing across addresses is")
    print("    the PAGE WINDOW, not a redirect, and each surface's reading is")
    print("    its own.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
