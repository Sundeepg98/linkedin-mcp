"""For each blocker, WHICH DOCUMENT ARGUES IT -- ranked, with its recall stated.

WHY THIS EXISTS. A reason that exists but cannot be found from the artifact
people open is a reason nobody re-examines. This ranks, for every blocker the
ledger publishes, the documents that ARGUE it rather than merely NAME it.

    ./venv/Scripts/python.exe scripts/find_blocker_reason.py
    ./venv/Scripts/python.exe scripts/find_blocker_reason.py --unreachable
    ./venv/Scripts/python.exe scripts/find_blocker_reason.py --blocker NAME

THE SCORE IS NOT A VERDICT, AND AFTER 2026-09-20 THAT IS A MEASUREMENT RATHER
THAN A DISCLAIMER. Recall was measured against a validation set this tool did
not build -- the six blockers a sibling wave's child researched BY HAND, and the
documents that child named in its own deliverable before any of this work began.
`tests/test_the_blocker_reason_locator_states_its_recall.py` holds that set and
re-measures on every run. The numbers as shipped:

    top-ranked document is the hand-found one       4 of 8
    hand-found document is in the top 3             7 of 8
    hand-found document appears anywhere in rank    8 of 8

**SO THIS RANKS CANDIDATES TO READ. IT DOES NOT IDENTIFY A DOCUMENT.** Half the
time the top-scoring document is not the one a careful human reader chose. The
`reason_doc` column in `_audit/_census/blocker-map.tsv` therefore carries the
candidate's RANK AND SCORE in the cell, never a bare path -- a bare path in a
table reads as data, and this one would be a coin flip wearing a fact's
clothes. See `_audit/2026-09-20-the-three-held-defects.md` section 2.

=== THREE DEFECTS FIXED 2026-09-20, EACH MEASURED SEPARATELY ===

The version before this one scored 1 of 8 found-anywhere and 0 of 8 at rank 1,
and its top answer for 59 of the 97 blockers was `blocker-map.tsv` -- a
generated index that argues nothing. Three independent causes, fixed and
measured one at a time so the repair is aimed rather than tuned to its test:

**F1 -- EVERY STEM IN THE VOCABULARY WAS DEAD.** The word list was written with
stems (`refus`, `measur`, `admit`) and wrapped in `\\b(...)\\b`. A trailing `\\b`
after a stem demands a word boundary immediately after the stem, which never
occurs, so `measur` matched NOTHING -- in a corpus where "measured" alone
appears 1910 times. Measured across `_audit/**/*.md`: measured 1910,
measurement 742, refused 811, refusal 626, admitted 497, rulings 156, proven
292, shown 334. The docstring said "deliberately broad"; the regex delivered
the opposite of what it said. Restoring the intended suffixes adds NO new
concept -- every entry below is a shipped entry with its own word forms back.

**F2 -- THE SCORING UNIT WAS A PHYSICAL LINE IN A HARD-WRAPPED CORPUS.**
Measured: `_audit/**/*.md` has a mean non-blank line length of 70.6 characters
and a median of 75, i.e. it is hard-wrapped at ~76 columns, while
`_audit/**/*.tsv` averages 544.5. A sentence therefore spans several lines, so
requiring the blocker name and the argue-word on ONE line measures TYPOGRAPHY.
It also biases systematically: a `.tsv` record is one line, so the derived
indexes carried every word of a record on the blocker's own line and won.
Scoring is now per PARAGRAPH (blank-line-delimited), the unit an argument is
actually written in.

**F3 -- THE GENERATED MAP COMPETED WITH THE PROSE, AND WOULD HAVE BEEN ITS OWN
INPUT.** `blocker-map.tsv` is DERIVED from `blocker-assignments.tsv` by
`build_blocker_map.py`. It cannot argue a reason; it restates assignments. Worse,
had the proposed `reason_doc` column been added to it, this function's answer
would have depended on a file this function's answer is written into -- a
fixpoint, where a doc path containing "rulings" would raise that blocker's score
for the map itself. It is excluded from CANDIDACY by name, and the exclusion is
printed on every run rather than left implicit. `blocker-assignments.tsv` is NOT
excluded: it is hand-written evidence whose notes genuinely argue.

=== AND THE DEFAULT RUN NOW PRINTS WHAT IT FOUND ===

The previous default printed three aggregate counts and the orphan list -- only
what failed a filter. Two agents in one day, including this file's own author,
read that as a recall bug: the per-blocker mapping existed inside `candidates()`
and was never shown, so a blocker with a perfectly good best document looked
identical to one with none. A refusal that reports only what it did NOT match is
half a measurement. The default now prints the whole ranking and names the files
it did not scan.

PERFORMANCE. The old shape re-read and re-scanned the entire `_audit` corpus
once per blocker -- 97 full passes, over two minutes. The corpus is now read
once, split into paragraphs once, and every blocker is matched in a single pass
with one alternation, because scoring 97 needles over one corpus is one pass,
not 97.
"""
from __future__ import annotations

import argparse
import functools
import importlib.util
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
AUDIT = ROOT / "_audit"

#: Documents a reader starting at the blocker table actually reaches: the
#: ledger, the census slices, and the map itself. Anything OUTSIDE this set is
#: where a reason can exist and still be unfindable.
REACHABLE = {
    "2026-09-03-linkedin-gap-blockers.md",
    "blocker-map.tsv",
    "blocker-assignments.tsv",
    "jobs.md",
    "network.md",
    "profile.md",
    "messaging-and-content.md",
}

#: GENERATED artifacts, excluded from candidacy -- see F3 above. Repo-relative,
#: forward slashes, matched exactly. Keep this list to files a SCRIPT writes.
DERIVED_ARTIFACTS = {
    "_audit/_census/blocker-map.tsv",
}

#: Words that mark a paragraph ARGUING a blocker rather than merely naming it.
#: Deliberately broad -- a false positive costs a document a rank in a list a
#: human then reads; a false negative hides the only argument there is.
#:
#: TWO GROUPS ON PURPOSE. Fixed words keep their trailing `\b`. STEMS take
#: `\w*`, because a stem with a trailing `\b` matches nothing at all (F1) --
#: that is the bug this split exists to make unrepeatable. `prove` and `show`
#: are spelled out rather than stemmed: `prov\w*` would match "providing", and
#: this corpus is full of "Providing services". `blocked` is NOT stemmed for the
#: same reason -- bare "block" is a LinkedIn capability ("block a member") and
#: would fire on the whole messaging census.
ARGUES = re.compile(
    r"\b(?:because|therefore|cannot|never|hence|blocked|"
    r"the reason|which is why|so that)\b"
    r"|\b(?:refus|admit|measur|evidenc|rul)\w*"
    r"|\bprove[nsd]?\b|\bshow(?:s|ed|n)?\b",
    re.I,
)

#: A paragraph is a blank-line-delimited block. See F2.
PARAGRAPH = re.compile(r"\n\s*\n")

#: F4 -- THE JOIN KEY WAS THE BLOCKER NAME, AND THIS CORPUS ARGUES BY ROW ID.
#: A build report says "J 40 is GAP because ..." and names its blocker twice in
#: the whole file. Keying only on the name therefore misses the argument even
#: with F1 and F2 fixed. The blocker-to-rows mapping already exists, in the very
#: artifact this feeds, so the join costs nothing to derive.
#:
#: MEASURED, on the hand-built validation set, name-only -> name-or-row:
#:     found anywhere   6 of 8  ->  8 of 8
#:     in the top 3     5 of 8  ->  7 of 8
#:     at rank 1        0 of 8  ->  4 of 8
#: and over the 26 SURFACE-named blockers, documents ranked as a share of
#: documents that mention the blocker: 80.5% -> 85.6%. THAT PAIR ISOLATES F4
#: ALONE -- both sides already carry F1-F3. The END-TO-END figure, against the
#: module at `8b58dcb` on the same denominator a sibling wave used:
#:     BEFORE   99 of 309 mentions ranked   32.0%
#:     AFTER   241 of 309 mentions ranked   78.0%   (85.5% net of the one file
#:                                                   this tool may not rank)
#: Their independent measurement was 93 of 286, 32.5%, on a slightly smaller
#: corpus -- the rate reproduces, which is why their denominator was reused
#: rather than a fresh one invented.
#:
#: IT IS NOT UNIFORMLY BETTER AND THE ONE REGRESSION IS STATED RATHER THAN
#: BURIED: `GROUPS-SURFACE`'s hand-found document fell from rank 7 to rank 14,
#: because that blocker holds 30 rows, so the row net is wide and documents
#: touching any one of the 30 now compete. A blocker with many rows gets a
#: broader net than a blocker with one; the score is comparable WITHIN a
#: blocker, never ACROSS blockers.
#:
#: THE LIMIT, NAMED: the join uses the map's own id spelling (`P H11`, `M C52`).
#: Documents that write a bare `H11` or `C82` without the slice letter are still
#: missed. Widening to bare ids would collide across slices, so it is not done.
_ROW_INDEX: dict[str, list[str]] | None = None


def set_row_index(mapping: dict[str, list[str]]) -> None:
    """Inject blocker -> [row id]; avoids re-running the map build downstream."""
    global _ROW_INDEX
    _ranking.cache_clear()
    _ROW_INDEX = {k: list(v) for k, v in mapping.items()}


def _row_index() -> dict[str, list[str]]:
    if _ROW_INDEX is not None:
        return _ROW_INDEX
    _gap, _current, assign, _problems = _bbm().build()
    out: dict[str, list[str]] = {}
    for rid, (blocker, *_rest) in assign.items():
        out.setdefault(blocker, []).append(rid)
    return out


def _bbm():
    spec = importlib.util.spec_from_file_location(
        "bbm", str(ROOT / "scripts" / "build_blocker_map.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bbm"] = mod
    spec.loader.exec_module(mod)
    return mod


@functools.lru_cache(maxsize=1)
def corpus() -> tuple[tuple[str, str], ...]:
    """(repo-relative path, text) for every audit document, read ONCE.

    An unreadable file is UNKNOWN and says so on stderr; it is never silently
    absent, because a file that vanished from the scan and a file that argues
    nothing produce the same score and must not produce the same report.
    """
    # TRACKED FILES ONLY, and this is a correctness rule rather than a filter.
    #
    # `_audit/_scratch/` is gitignored (.gitignore:156) and holds 113 markdown
    # files in the MAIN checkout and ZERO in any worktree or clone. Enumerating
    # the filesystem therefore gave this tool a different corpus depending on
    # where it ran: measured 2026-09-20, two blockers had a `_scratch/` progress
    # file ranked THIRD on master while the same tool in a worktree never saw it.
    # The recall floor was built in a worktree and went red the moment it ran on
    # master -- not because the ranking got worse, but because the corpus grew by
    # 113 files nobody else can read.
    #
    # The deeper reason is this repo's own standard: a measurement nobody else
    # can take is a measurement on its way to becoming a quotation. A reason_doc
    # naming `_audit/_scratch/_progress-groups-surface.md` sends every reader to
    # a file that does not exist in their checkout -- strictly worse than naming
    # nothing, because it looks like an answer. A sibling audit established the
    # same point about `_progress-unlocatable-recovery.md`: standing verdicts
    # were resting on a file no reader could open.
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "_audit"],
        capture_output=True, check=True,
    ).stdout.decode("utf-8", "replace").splitlines()
    wanted = sorted(
        r for r in tracked if r and (r.endswith(".md") or r.endswith(".tsv"))
    )
    out: list[tuple[str, str]] = []
    for rel in wanted:
        path = ROOT / rel
        try:
            out.append((rel, path.read_text(encoding="utf-8", errors="replace")))
        except OSError as error:
            print(f"  ! unreadable {rel}: {error}", file=sys.stderr)
    return tuple(out)


@functools.lru_cache(maxsize=1)
def _ranking() -> dict[str, list[tuple[int, str]]]:
    """blocker -> ranked [(score, doc)], from ONE pass over the corpus.

    The score is the count of ARGUING PARAGRAPHS that name the blocker, not the
    count of mentions: a table listing every blocker once scores zero, which is
    exactly right -- it names them and argues nothing.
    """
    blockers = sorted(_bbm().ledger_counts())
    names = re.compile("(" + "|".join(re.escape(b) for b in blockers) + ")",
                       re.I)
    rows = _row_index()
    #: rid -> blocker, as ONE alternation, so the row join is also a single pass
    #: rather than 97 more. Longest first: no id is a prefix of another under
    #: `\b`, but sorting makes that independent of dict order.
    owner = {rid: b for b, rids in rows.items() for rid in rids}
    row_re = (re.compile("(" + "|".join(
        r"\b" + re.escape(r) + r"\b"
        for r in sorted(owner, key=len, reverse=True)) + ")")
        if owner else None)

    tally: dict[str, dict[str, int]] = {b: {} for b in blockers}
    for rel, text in corpus():
        if rel in DERIVED_ARTIFACTS:
            continue
        for para in PARAGRAPH.split(text):
            if not ARGUES.search(para):
                continue
            hits = {m.upper() for m in names.findall(para)}
            if row_re is not None:
                hits |= {owner[m] for m in row_re.findall(para) if m in owner}
            for hit in hits:
                if hit in tally:
                    tally[hit][rel] = tally[hit].get(rel, 0) + 1
    return {b: sorted(((s, d) for d, s in docs.items()), reverse=True)
            for b, docs in tally.items()}


def candidates(blocker: str) -> list[tuple[int, str]]:
    """Documents that NAME the blocker, ranked by how many paragraphs ARGUE it.

    RECALL IS MEASURED, NOT ASSUMED: 4 of 8 at rank 1, 7 of 8 in the top 3,
    8 of 8 anywhere, against a hand-built validation set. Callers may use this
    to decide WHAT TO READ. A caller that writes the top answer into a derived
    artifact as a fact is making a claim this function's recall does not support.
    """
    return list(_ranking().get(blocker.upper(), []))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--unreachable", action="store_true",
                    help="only blockers whose best argument is OUTSIDE the "
                         "documents a reader starting at the table reaches")
    ap.add_argument("--blocker", metavar="NAME",
                    help="print the full ranking for one blocker")
    args = ap.parse_args(argv)

    ranking = _ranking()
    blockers = sorted(ranking)

    if args.blocker:
        key = args.blocker.upper()
        if key not in ranking:
            print(f"  {args.blocker!r} is not a blocker the ledger publishes. "
                  f"{len(blockers)} are; nearest spellings: "
                  f"{[b for b in blockers if key[:6] in b][:5]}")
            return 1
        print(f"  {key} -- {len(ranking[key])} candidate document(s)")
        for score, doc in ranking[key]:
            mark = "  " if pathlib.Path(doc).name in REACHABLE else " *"
            print(f"  {score:5d}{mark} {doc}")
        print("\n  * = outside the documents a reader starting at the blocker "
              "table reaches")
        return 0

    unreachable, orphaned, reachable = [], [], []
    for b in blockers:
        c = ranking[b]
        if not c:
            orphaned.append(b)
        elif pathlib.Path(c[0][1]).name not in REACHABLE:
            unreachable.append((b, c[0][0], c[0][1]))
        else:
            reachable.append((b, c[0][0], c[0][1]))

    if args.unreachable:
        print(f"  {'blocker':34s} {'score':>5s}  best argument lives in")
        for b, s, d in sorted(unreachable, key=lambda x: (-x[1], x[0])):
            print(f"  {b:34s} {s:5d}  {d}")
    else:
        # WHAT IT FOUND, not only what failed a filter. The previous default
        # printed three totals and the orphan list, and two readers in one day
        # mistook a blocker it had simply not printed for one it had missed.
        print(f"  {'blocker':34s} {'score':>5s} {'cands':>5s}  "
              f"best-scoring candidate")
        for b in blockers:
            c = ranking[b]
            if not c:
                print(f"  {b:34s} {'-':>5s} {0:5d}  NO-ARGUMENT-FOUND")
                continue
            mark = " " if pathlib.Path(c[0][1]).name in REACHABLE else "*"
            print(f"  {b:34s} {c[0][0]:5d} {len(c):5d} {mark} {c[0][1]}")
        print("\n  * = best argument is OUTSIDE the documents a reader starting "
              "at the blocker table reaches")

    print(f"\n  blockers                                   {len(blockers)}")
    print(f"  best argument IS in a reachable document   {len(reachable)}")
    print(f"  best argument NOT in a reachable document  {len(unreachable)}")
    print(f"  NO-ARGUMENT-FOUND -- argued nowhere at all {len(orphaned)}")
    for b in orphaned:
        print(f"    {b}")
    print(f"\n  corpus scanned   {len(corpus())} files under _audit/")
    print(f"  NOT scanned      {len(DERIVED_ARTIFACTS)} generated artifact(s): "
          f"{', '.join(sorted(DERIVED_ARTIFACTS))}")
    print("  RECALL, against a set this tool did not build: 4 of 8 at rank 1, "
          "7 of 8 in the top 3, 8 of 8 anywhere.")
    print("  This RANKS CANDIDATES TO READ. It does not identify a document, "
          "and no derived artifact may carry its top answer as a fact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
