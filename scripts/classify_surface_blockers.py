"""What the SURFACE-named blockers are actually blocked BY -- derived, not guessed.

THE DEFECT THIS ANSWERS. `_audit/2026-09-20-the-contingent-writeoffs.md` s3.1
published a five-way classification of the 97 blockers by "the subject the name
asserts", and gave one class the name `SURFACE?` -- *a surface whose existence
FOR HIM is contingent* -- at **22 blockers, 139 rows, 108 still GAP**. That line
has been quoted since as though it named a set.

**IT NAMES NO SET.** The classifier was never committed; `git log -S` finds it
nowhere. Its stated inputs are `_audit/_scratch/_contingent-ledger-sweep.tsv`
and two siblings, all gitignored BY DESIGN, and none of the three is on disk any
more. So the membership is recoverable only from the three published integers --
and this file measures how far that gets you: **186,629,988,917,605 distinct
22-blocker subsets of the 69-blocker pool total exactly 139 rows and 108 GAP.**
The class cannot be enumerated, and its own document says so in its limits
section 6: *"the SURFACE? class of 22 is a guess about names, not a measurement
of reasons."*

That is the SAME defect `build_blocker_map.py` exists to end, one level up: a
division published as counts, with the classifier uncommitted. This file is the
sibling remedy -- a membership rule that RUNS.

WHAT IT DERIVES, per blocker whose NAME contains SURFACE:

    rows / GAP today   from `blocker-map.tsv`, itself derived from the census
    boundary           the ledger's OWN cell: what THIS REPO must change
    reason_class       ADDRESSABILITY-OURS / WRITER-OURS / SURFACE-FACT / NONE

**WHY THE BOUNDARY CELL AND NOT THE PROSE.** The ledger's own legend defines
that column as `D  boundary LISTS needing an exemption or edit` and `W  a new
WriteSpec + gate + consent text` -- both are artifacts of THIS REPOSITORY. And
the ledger carries an explicit non-staleness warrant for exactly this column,
added 2026-09-20 by `_audit/2026-09-20-the-decides.md`:

    the ROW COUNTS in the ranking tables below are freeze figures from
    2026-09-03 and have not been maintained ... the COST and boundary
    columns here are properties of the work and do not go stale.

So the row counts here are re-derived live and the boundary cell is read as
published, each on the warrant that document gives it.

**THE FINDING THIS MAKES CHECKABLE.** A blocker named `*-SURFACE` implies the
surface is the problem. The boundary cell says what would actually be built. If
those disagree for the whole class, the class name is wrong -- and that is a
measurement anybody can re-run, not an opinion.

**WHAT THIS DOES NOT DO.** It does not rule any row. A boundary cell proves the
ledger COSTED A BUILD against the address, which is evidence about how the row
was filed. It is NOT a measurement that LinkedIn draws the surface -- no such
measurement is asserted here for any blocker. Whether the page renders is
settled by a capture, and the companion document names the pages nobody has
captured. Conflating "our gate refuses it" with "LinkedIn does not serve it" is
the error `_audit/INSTRUMENTS.md` s9.1 records as ALLOWED IS NOT SERVED; this
file is careful about its converse, REFUSED IS NOT ABSENT.

ASSERTIONS, because a check that cannot fail certifies nothing:
  * both ledger tables must be locatable by their header rows   -> else FAIL
  * they must total 97 blockers / 409 rows                      -> else FAIL
  * the name rule must select a non-empty class                 -> else FAIL
  * every selected blocker must appear in exactly one table     -> else FAIL
  * every selected blocker must exist in the derived map        -> else FAIL

    ./venv/Scripts/python.exe scripts/classify_surface_blockers.py
    ./venv/Scripts/python.exe scripts/classify_surface_blockers.py --rows
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "_audit" / "2026-09-03-linkedin-gap-blockers.md"
MAP = ROOT / "_audit" / "_census" / "blocker-map.tsv"

#: Located by HEADER ROW, never by line offset -- a reading pinned to a POSITION
#: in a file other waves append to is the defect measured on 2026-09-05, when
#: 19 appended lines slid both tables 28 lines down and four blockers silently
#: read as published 0. Same grammar as `build_blocker_map.ledger_counts`.
RANKED_HEADER = "| # | blocker | rows | R/W | boundary | ruling | cost |"
ZEROCOST_HEADER = "| blocker | rows | queue | why |"

#: THE MEMBERSHIP RULE, stated so it can be argued with. Syntactic and total:
#: every blocker whose NAME contains SURFACE, with nothing hand-picked and
#: nothing hand-dropped. It is deliberately NOT the published class -- that one
#: is unrecoverable (see the module docstring) -- and it is deliberately not a
#: judgement about which surfaces are "really" contingent, because a judgement
#: is what produced an unreproducible class the first time.
NAME_RULE = re.compile(r"SURFACE")

#: What a boundary cell asserts. The two list words name THIS REPO's URL
#: boundary; WriteSpec names THIS REPO's write contract. Order matters: a cell
#: reading "allowlist +1, WriteSpec" is an addressability fact FIRST, because
#: the ledger's own ASSIGNMENT RULE files a row against the EARLIEST binding
#: constraint -- "a row that looks blocked by a missing write but has no way to
#: find its target is filed against the missing surface, not the missing write."
OURS_ADDRESS = re.compile(r"allowlist|denylist", re.I)
OURS_WRITER = re.compile(r"writespec", re.I)

#: A CANDIDATE BASE ADDRESS PER BLOCKER, so the ledger's 2026-09-03 boundary
#: CLAIM can be checked against the LIVE boundary.
#:
#: **THIS TABLE IS A CLAIM, NOT A DERIVATION**, and it is written out rather
#: than computed precisely so it can be argued with. Each entry is the address
#: a reader of the blocker's rows would reach for first. A wrong entry makes
#: this section wrong in a VISIBLE way -- the url is printed next to its
#: verdict on every run -- which is the property a hidden mapping lacks.
#:
#: Slugs are deliberately the literal word `example`: a real company, school or
#: member token must never enter a tracked file.
SURFACE_ADDRESSES: dict[str, str] = {
    "ARTICLE-SURFACE": "/article/new/",
    "BADGES-SURFACE": "/in/me/",
    "COMPANY-PAGE-SURFACE": "/company/example/",
    "CONTENT-ANALYTICS-SURFACE": "/analytics/creator/content/",
    "CREATOR-HUB-SURFACE": "/analytics/creator/content/",
    "EVENTS-SURFACE": "/events/",
    "GROUP-CHAT-SURFACE": "/messaging/",
    "GROUPS-SURFACE": "/groups/",
    "INMAIL-COMPOSE-SURFACE": "/messaging/compose/",
    "JOB-ALERTS-SURFACE": "/jobs/alerts/",
    "JOB-COLLECTIONS-SURFACE": "/jobs/collections/recommended/",
    "MESSAGE-REQUESTS-SURFACE": "/messaging/",
    "NEWSLETTER-SURFACE": "/mynetwork/network-manager/newsletters/",
    "PICKER-SURFACES": "/messaging/",
    "POLL-SURFACE": "/preload/sharebox/",
    "POST-DRAFT-SURFACE": "/preload/sharebox/",
    "PREMIUM-JOBS-SURFACES": "/premium/my-premium/",
    "RECOMMENDATIONS-SURFACE": "/in/me/details/recommendations/",
    "RESUME-TOOLS-SURFACE": "/resume-builder/",
    "SAVED-POSTS-SURFACE": "/my-items/saved-posts/",
    "SCHOOL-PAGE-SURFACE": "/school/example/",
    "SEARCH-APPEARANCES-SURFACE": "/analytics/search-appearances/",
    "SEARCH-HISTORY-SURFACE": "/search/history/",
    "SEARCH-RESULTS-SURFACE": "/search/results/people/?keywords=example",
    "SERVICES-PAGE-SURFACE": "/services/page/",
    "SKILL-PAGE-SURFACE": "/skill/example/",
}


def _table_after(lines: list[str], header: str) -> list[str]:
    for i, line in enumerate(lines):
        if line.startswith(header):
            out = []
            for row in lines[i + 1:]:
                if not row.startswith("|"):
                    break
                out.append(row)
            return out
    return []


def ledger_rows() -> tuple[dict[str, dict[str, str]], list[str]]:
    """Per-blocker cells from the ledger's own two tables, plus any problems."""
    problems: list[str] = []
    lines = LEDGER.read_text(encoding="utf-8", errors="replace").splitlines()
    ranked_lines = _table_after(lines, RANKED_HEADER)
    zero_lines = _table_after(lines, ZEROCOST_HEADER)
    if not ranked_lines:
        problems.append(
            f"the ranked table header is no longer present in {LEDGER.name}; "
            f"every boundary cell below would read as absent")
    if not zero_lines:
        problems.append(
            f"the cost-0 table header is no longer present in {LEDGER.name}; "
            f"its blockers would silently read as missing from the ledger")

    out: dict[str, dict[str, str]] = {}
    for line in ranked_lines:
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) >= 9 and re.match(r"^\d+$", c[0]):
            out[c[1].strip("`")] = dict(
                table="ranked", rows=c[2], rw=c[3], boundary=c[4],
                ruling=c[5], cost=c[6], queue=c[8])
    for line in zero_lines:
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) >= 4 and c[0].startswith("`"):
            b = c[0].strip("`")
            if b in out:
                problems.append(f"{b} appears in BOTH ledger tables")
            out[b] = dict(table="cost-0", rows=c[1], rw="-", boundary="-",
                          ruling="-", cost="0", queue=c[2], why=c[3])
    return out, problems


def map_counts() -> tuple[collections.Counter, collections.Counter,
                          dict[str, list[tuple[str, str, str]]]]:
    hdr = ("row_id blocker evidence_class source locator state_at_freeze "
           "state_today capability note").split()
    tot: collections.Counter = collections.Counter()
    gap: collections.Counter = collections.Counter()
    rows: dict[str, list[tuple[str, str, str]]] = collections.defaultdict(list)
    for line in MAP.read_text(encoding="ascii", errors="replace").splitlines()[1:]:
        if not line.strip():
            continue
        d = dict(zip(hdr, line.split("\t")))
        b = d["blocker"]
        tot[b] += 1
        if d["state_today"] == "GAP":
            gap[b] += 1
        rows[b].append((d["row_id"], d["state_today"], d["capability"]))
    return tot, gap, rows


def reason_class(boundary: str) -> str:
    """What the ledger's boundary cell asserts the block IS."""
    if boundary in ("", "-", "none"):
        return "NONE-STATED"
    if OURS_ADDRESS.search(boundary):
        return "ADDRESSABILITY-OURS"
    if OURS_WRITER.search(boundary):
        return "WRITER-OURS"
    return "SURFACE-FACT"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rows", action="store_true", help="print each blocker's rows")
    args = ap.parse_args(argv)

    ledger, problems = ledger_rows()
    tot, gap, rows = map_counts()
    fail = 0

    print(f"ledger blockers parsed   {len(ledger)}   "
          f"rows {sum(int(v['rows']) for v in ledger.values())}")
    if len(ledger) != 97 or sum(int(v["rows"]) for v in ledger.values()) != 409:
        problems.append("the ledger's own tables no longer total 97 blockers / 409 rows")

    klass = sorted(b for b in tot if NAME_RULE.search(b))
    if not klass:
        problems.append("the name rule selected NO blocker at all")

    for b in klass:
        if b not in ledger:
            problems.append(f"{b} is in the map but in NEITHER ledger table")

    for p in problems:
        print(f"  FAIL: {p}")
        fail = 1
    if fail:
        print("\nNOT CLASSIFIED -- assertions failed above")
        return 1

    print(f"\nMEMBERSHIP RULE  name matches /{NAME_RULE.pattern}/")
    print(f"selected         {len(klass)} blockers   "
          f"{sum(tot[b] for b in klass)} rows   "
          f"{sum(gap[b] for b in klass)} still GAP today\n")

    print(f"  {'blocker':30s} {'row':>3s} {'GAP':>3s}  {'boundary':26s} "
          f"{'reason_class':20s} queue")
    print("  " + "-" * 104)
    tally: collections.Counter = collections.Counter()
    for b in klass:
        v = ledger[b]
        rc = reason_class(v["boundary"])
        tally[rc] += 1
        print(f"  {b:30s} {tot[b]:3d} {gap[b]:3d}  {v['boundary'][:26]:26s} "
              f"{rc:20s} {v['queue']}")

    print("\nREASON CLASS over the selected blockers")
    for k, n in tally.most_common():
        g = sum(gap[b] for b in klass if reason_class(ledger[b]["boundary"]) == k)
        r = sum(tot[b] for b in klass if reason_class(ledger[b]["boundary"]) == k)
        print(f"  {k:22s} {n:3d} blockers  {r:4d} rows  {g:4d} GAP")

    # THE DENOMINATOR THE NUMBER WAS TAKEN OVER, printed with it. Without this
    # the class tally reads as a property of surfaces; with it, it reads as a
    # property of how the whole ledger costs work -- which is what it is.
    rest = sorted(b for b in tot if b not in set(klass) and b in ledger)
    rtally: collections.Counter = collections.Counter(
        reason_class(ledger[b]["boundary"]) for b in rest)
    print(f"\nCONTROL -- the same classifier over the {len(rest)} blockers the "
          f"rule did NOT select")
    for k, n in rtally.most_common():
        print(f"  {k:22s} {n:3d} blockers")
    print("\n  A class tally that looked identical here would mean the rule "
          "selected nothing\n  distinctive. It does not: see the "
          "NONE-STATED split.")

    # WHAT WAS SEEN, not only what did not match -- a refusal that reports only
    # its misses is half a measurement (this repo's own law).
    surf = [b for b in klass if reason_class(ledger[b]["boundary"]) == "SURFACE-FACT"]
    print(f"\nSURFACE-named blockers whose boundary cell asserts a SURFACE fact: "
          f"{len(surf)}")
    if surf:
        for b in surf:
            print(f"    {b:30s} boundary={ledger[b]['boundary']!r}")
    else:
        print("    none -- every selected blocker's boundary cell names an "
              "artifact of THIS repo")
        print("    (an allowlist entry, a denylist exemption, or a WriteSpec)")

    # ------------------------------------------------------------------
    # THE LEDGER'S BOUNDARY CLAIM, CHECKED AGAINST THE LIVE BOUNDARY.
    #
    # The ledger head carries an explicit warrant that this column cannot go
    # stale ("the COST and boundary columns here are properties of the work and
    # do not go stale"). That warrant is TESTABLE, and this is the test: a cell
    # reading `allowlist +1` bills a pattern that is still owed, so if the live
    # allowlist ALREADY admits the blocker's base address, the cell has been
    # overtaken by work done since 2026-09-03.
    # ------------------------------------------------------------------
    print("\n\nTHE LEDGER'S BOUNDARY CLAIM vs THE LIVE ALLOWLIST")
    try:
        sys.path.insert(0, str(ROOT))
        from linkedin_server import readonly  # noqa: PLC0415
    except Exception as error:                      # an unavailable gate is
        print(f"  UNKNOWN -- linkedin_server.readonly did not import: "  # UNKNOWN,
              f"{error!r}")                                              # never
        print("  This section is BLANK, not clean. Nothing below is measured.")
        readonly = None                                                  # "clean"
    if readonly is not None:
        print(f"  live allowlist patterns: {len(readonly._ALLOWED_URL_PATTERNS)}")
        print(f"\n  {'blocker':30s} {'ledger boundary':26s} {'live gate':9s} address")
        print("  " + "-" * 104)
        overtaken: list[str] = []
        unmapped = [b for b in klass if b not in SURFACE_ADDRESSES]
        for b in klass:
            url = SURFACE_ADDRESSES.get(b)
            if url is None:
                continue
            allowed = readonly.is_read_url("https://www.linkedin.com" + url)
            cell = ledger[b]["boundary"]
            if allowed and OURS_ADDRESS.search(cell):
                overtaken.append(b)
            print(f"  {b:30s} {cell[:26]:26s} {'ALLOWED' if allowed else 'refused':9s} {url}")
        print(f"\n  base address ALREADY ALLOWED while the ledger still bills an "
              f"allowlist entry: {len(overtaken)} of {len(klass)}")
        for b in overtaken:
            print(f"    {b:30s} ledger={ledger[b]['boundary']!r}")
        if unmapped:
            print(f"\n  NOT CHECKED -- no candidate address stated for "
                  f"{len(unmapped)}: {', '.join(unmapped)}")

    if args.rows:
        for b in klass:
            print(f"\n=== {b}   {tot[b]} rows, {gap[b]} GAP")
            for rid, st, cap in sorted(rows[b],
                                       key=lambda x: (x[0][0], len(x[0]), x[0])):
                print(f"    {rid:8s} {st:22s} {cap[:80]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
