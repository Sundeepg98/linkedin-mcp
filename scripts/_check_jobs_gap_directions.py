"""THE DIRECTION OF EVERY `jobs.md` GAP ROW, AND WHETHER ITS READS ARE REACHABLE.

WHY THIS EXISTS. `_audit/2026-09-20-the-reachable-ceiling.md` split the census's
GAP rows by direction and got `W 171 / R 70 / R/W 1` over the 242 rows that
carry an `R/W` COLUMN -- and recorded `jobs.md`'s GAP rows as UNMEASURED,
because its per-row tables run `| # | capability | source | state | reason |`
and have no direction column. That was the right call and it left the ceiling
uncomputed for a fifth of the GAP.

WHAT THE CEILING ARGUMENT NEEDS, AND WHY A ROW COUNT IS NOT IT. The ceiling
claim is that a write-direction GAP row is not work waiting to be done, because
this server is read-only and `writes_enabled()` is False. That argument is only
as good as the direction split under it, so the split has to be re-derivable
from the files by somebody who does not trust the person who published it.

THE DIRECTION DATA FOR `jobs.md` ALREADY EXISTED AND WAS KEYED WRONG.
Section 2, `| rows | gap | shape | R/W | REV |`, carries a direction per
ROW-RANGE. `scripts/_check_jobs_range_directions.py` already reads it. But a
range direction is a claim about a BLOCK: it resolves 42 of today's 57 GAP rows
and leaves 14 under a compound cell (`R + W`) plus 1 named by no range at all.
Worse, a block direction can be WRONG FOR A ROW INSIDE IT, and this file found
three: `J 56` ("Filter the tracker by date posted") and `J 82` ("OBSERVE the
Easy Apply daily limit") both sit in ranges filed `W` while their own verbs
read, and `J 37` ("List AND MANAGE all alerts") sits in a range filed `R` while
its own text names a write. So this file classifies PER ROW off the row's own
capability text, and prints the three disagreements rather than hiding them.

THE SECOND AND MORE USEFUL QUESTION. Of the rows that are READS, how many could
a reader over an ALREADY-ADMITTED address actually close? That is answered
against `readonly.is_read_url` AT HEAD and never against what a census cell
claims, because cells go stale: section 2 costs rows 31-36 and 41 with
*"`/jobs/alerts` is not on the read allowlist"* and pattern 39 admits exactly
that address today. A row blocked by an expired premise is real coverage
movement and this is how it is found.

    <python> scripts/_check_jobs_gap_directions.py
    <python> scripts/_check_jobs_gap_directions.py --emit-tsv <path>

CONTROLS, because a check that cannot fail certifies nothing:
  * `--control-stub-admits` replaces `is_read_url` with a stub that admits
    everything. Every REFUSED address must become ADMITTED and the run must
    FAIL -- which is the only proof that the reachability column is read off
    the shipped boundary rather than off the table in this file.
  * `--control-drift` deletes one row from the classification table below and
    requires the census/table reconciliation to NAME the missing row. Without
    it, a row leaving GAP tomorrow would leave a silently stale split here --
    the same disease the ceiling document was written against.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import count_census_states as census  # noqa: E402
from linkedin_server import readonly  # noqa: E402

JOBS = ROOT / "_audit" / "_census" / "jobs.md"

#: A PLACEHOLDER slug and a PLACEHOLDER posting id, never a real one. These
#: strings are probed against the boundary and printed, so a real company slug
#: or a real posting id here would be an identifier in a tracked file.
SLUG = "example-company"
POSTING = "1234567890"

#: The direction of every GAP row, classified from the row's OWN capability
#: text and its reason cell. `R` reads, `W` changes something LinkedIn stores
#: or shows to somebody, `RW` is a row whose own text names both acts, and
#: `AMBIGUOUS` is a row the text does not settle -- counted separately on
#: purpose, because an honest `AMBIGUOUS 1` is worth more than a forced split.
#:
#: The fourth field is the address a READER would open to close the row, or
#: None when the row names no readable address (it sits behind a press, an
#: upload, or a surface nobody has located). It is probed against
#: `readonly.is_read_url` below; nothing here asserts its own verdict.
DIRECTIONS: dict[int, tuple[str, str, str | None]] = {
    # (direction, why, address a reader would open)
    16: ("R", "read an adaptive suggestion strip; changes nothing",
         "https://www.linkedin.com/jobs/search/?keywords=engineer"),
    18: ("R", "view and re-run a past search; a search changes nothing but history",
         "https://www.linkedin.com/jobs/search-history/"),
    19: ("W", "CLEAR history -- destructive, and `clear`/`delete` are denylisted", None),
    28: ("W", "report a job as closed; section 2 says outright `28, 30 are W`", None),
    31: ("W", "CREATE an alert", None),
    32: ("W", "CREATE an alert from a company Page", None),
    33: ("W", "EDIT an alert", None),
    34: ("W", "DELETE / turn off an alert", None),
    35: ("W", "SET alert frequency", None),
    36: ("W", "SET alert delivery channel", None),
    # ADMITTED IS NOT SERVED. The gate admits this address and LinkedIn
    # REDIRECTS AWAY FROM IT -- `readonly.py` records the measurement two
    # lines above the pattern: "requested /jobs/alerts/ landed /jobs/jam".
    # The reachability column below will read ADMITTED for both rows and that
    # is the honest answer to the question it asks; it is not a claim that a
    # reader would land where it aimed. Do not file either row as parser-only.
    37: ("RW", "the row names BOTH: `List` (read) AND `manage` (write). Its range "
               "is filed R, which under-reads it; its write half duplicates 33-34. "
               "ADMITTED-BUT-REDIRECTED: LinkedIn serves /jobs/jam here, so the "
               "landing surface needs capturing before any reader is written",
         "https://www.linkedin.com/jobs/alerts/"),
    38: ("R", "READ the jobs an alert delivered. ADMITTED-BUT-REDIRECTED, same "
              "as 37: the gate allows /jobs/alerts/ and LinkedIn lands /jobs/jam",
         "https://www.linkedin.com/jobs/alerts/"),
    39: ("R", "READ job recommendations",
         "https://www.linkedin.com/jobs/collections/recommended/"),
    40: ("R", "READ per-job network proximity off a page already loaded",
         f"https://www.linkedin.com/jobs/view/{POSTING}/"),
    41: ("W", "SUBSCRIBE / UNSUBSCRIBE a digest", None),
    54: ("W", "CHANGE a tracker stage", None),
    55: ("W", "ADD notes", None),
    56: ("R", "FILTER a list by date posted. Its range is filed W; filtering "
              "changes nothing, and section 2 files an ordinary search as R",
         "https://www.linkedin.com/jobs-tracker/?stage=applied&dateposted=week"),
    57: ("R", "a JOIN over two reads this repo already performs",
         "https://www.linkedin.com/jobs-tracker/?stage=applied"),
    68: ("W", "SAVE an application draft", None),
    70: ("W", "UPLOAD a resume", None),
    72: ("R", "DOWNLOAD a stored resume; retrieving a file changes nothing",
         "https://www.linkedin.com/jobs/application-settings/"),
    78: ("W", "AI drafts a cover letter onto an application", None),
    79: ("W", "MARK Top Choice; spends a non-refunding credit", None),
    80: ("W", "ATTACH a message to the poster", None),
    81: ("W", "VERIFY the account to raise a limit", None),
    82: ("R", "OBSERVE a limit / rate-pause state. Its range is filed W; the "
              "row's own verb is `Observe`", None),
    83: ("W", "SAVE self-identification answers for reuse", None),
    85: ("W", "UNDO a dismissal", None),
    86: ("W", "SIGNAL interest to a company", None),
    98: ("W", "SET / EDIT / DELETE a pay preference", None),
    100: ("W", "SIGNAL interest to recruiters", None),
    106: ("R", "read the About tab", f"https://www.linkedin.com/company/{SLUG}/about/"),
    107: ("R", "read the Jobs tab", f"https://www.linkedin.com/company/{SLUG}/jobs/"),
    108: ("R", "read the People tab", f"https://www.linkedin.com/company/{SLUG}/people/"),
    109: ("R", "read the Life tab", f"https://www.linkedin.com/company/{SLUG}/life/"),
    110: ("R", "read the Home tab -- which IS the Page root",
          f"https://www.linkedin.com/company/{SLUG}/"),
    111: ("R", "read the Products / Services tabs",
          f"https://www.linkedin.com/company/{SLUG}/products/"),
    113: ("R", "read the Insights tab", f"https://www.linkedin.com/company/{SLUG}/insights/"),
    114: ("R", "read Premium Page Insights",
          f"https://www.linkedin.com/company/{SLUG}/insights/"),
    116: ("R", "read a top-applicant flag rendered on the posting page",
          f"https://www.linkedin.com/jobs/view/{POSTING}/"),
    117: ("R", "read skills associated with the job, on the posting page",
          f"https://www.linkedin.com/jobs/view/{POSTING}/"),
    118: ("R", "read matching profile skills, on the posting page",
          f"https://www.linkedin.com/jobs/view/{POSTING}/"),
    119: ("R", "read missing skills, on the posting page",
          f"https://www.linkedin.com/jobs/view/{POSTING}/"),
    120: ("R", "read additional applicant skills, on the posting page",
          f"https://www.linkedin.com/jobs/view/{POSTING}/"),
    124: ("R", "read Premium AI company intelligence; section 2 says 123-126 "
               "need OTHER surfaces and names none", None),
    126: ("R", "read Premium AI job-fit tips; same, no surface named", None),
    129: ("W", "SEND an InMail; spends a credit, not reversible", None),
    131: ("R", "rank who to message over two reads; the skill's own tool "
               "`recommends only. It never sends`",
          "https://www.linkedin.com/premium/my-premium/"),
    136: ("R", "RECEIVE a readiness score -- the census calls these three "
               "`the READ half`", "https://www.linkedin.com/learning/role-play/scenarios/"),
    137: ("R", "RECEIVE a summary -- the READ half",
          "https://www.linkedin.com/learning/role-play/scenarios/"),
    138: ("R", "RECEIVE a transcript -- the READ half",
          "https://www.linkedin.com/learning/role-play/scenarios/"),
    146: ("W", "UPLOAD a resume for analysis. NOTE: the `set_input_files` ban "
               "is an OPEN question nobody has answered; this row is filed W "
               "and stays GAP, and nothing here treats the ban as settled",
          None),
    147: ("R", "RECEIVE insights -- but gated behind 146's upload", None),
    148: ("AMBIGUOUS", "`Refine sections of your resume with suggested language`. "
                       "Section 2's REV cell says `it produces a file; nothing "
                       "is sent`, which argues R. But LinkedIn STORES resumes "
                       "(rows 70-73), and whether a refinement persists to the "
                       "stored copy is UNMEASURED. Nobody has captured the "
                       "surface, so the direction is not decidable from the "
                       "file", None),
    149: ("RW", "the row names BOTH: `Export the result` (read) OR `attach it "
                "to a LinkedIn application` (write)", None),
    150: ("W", "SEND an enhanced recruiter message", None),
}

ORDER = ("R", "W", "RW", "AMBIGUOUS")


def gap_rows() -> list[int]:
    """Today's GAP row numbers, off the SHIPPED census parser.

    Imported rather than re-implemented: `cells()` honours the markdown escape
    for a literal pipe, and four lines in THIS file carry one. A hand-rolled
    `split('|')` reads the tail of those reasons and looks like it worked.
    """
    out: list[int] = []
    for line in JOBS.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("|"):
            continue
        cl = census.cells(line)
        if len(cl) < 3 or (cl[0] and set(cl[0]) <= set("-: ")):
            continue
        if not census.ROW.match(line) or cl[0].lower() in census.HEADERS:
            continue
        state, _dialects = census.classify(cl)
        if state == "GAP" and re.fullmatch(r"\d+", cl[0]):
            out.append(int(cl[0]))
    return sorted(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit-tsv", default="",
                    help="write the classification to this path as TSV")
    ap.add_argument("--control-stub-admits", action="store_true",
                    help="admit every address; the refused set must empty and the run must FAIL")
    ap.add_argument("--control-drift", action="store_true",
                    help="drop a row from the table; the reconciliation must NAME it")
    args = ap.parse_args(argv)

    table = dict(DIRECTIONS)
    if args.control_drift:
        table.pop(110, None)

    admits = readonly.is_read_url
    if args.control_stub_admits:
        admits = lambda _url: True  # noqa: E731

    gap = gap_rows()
    print(f"jobs.md GAP rows, re-derived off the census    {len(gap)}")
    print(f"rows classified in this file                   {len(table)}")

    # ---- reconciliation, and it can fail ------------------------------
    missing = [n for n in gap if n not in table]
    extra = [n for n in table if n not in gap]
    drifted = bool(missing or extra)
    if missing:
        print(f"  DRIFT: GAP rows this file does not classify: "
              f"{' '.join('J %d' % n for n in missing)}")
    if extra:
        print(f"  DRIFT: classified rows that are no longer GAP: "
              f"{' '.join('J %d' % n for n in extra)}")
    if not drifted:
        print("  reconciliation: the table and the census name the SAME rows")

    if args.control_drift:
        named = missing == [110]
        print(f"\ncontrol-drift: dropped J 110 from the table -- "
              f"{'NAMED as missing, the reconciliation can fail' if named else 'NOT NAMED -- BROKEN'}")
        return 0 if named else 1

    # ---- the split ----------------------------------------------------
    counts = {k: 0 for k in ORDER}
    for n in gap:
        counts[table[n][0]] += 1
    print("\nTHE SPLIT")
    for k in ORDER:
        print(f"  {k:10s} {counts[k]:3d}")
    print(f"  {'total':10s} {sum(counts.values()):3d}")

    # ---- reachability of the reads ------------------------------------
    readish = [n for n in gap if table[n][0] in ("R", "RW")]
    print(f"\nREACHABILITY of the {len(readish)} rows that read "
          f"(R plus the read half of RW), against readonly.is_read_url AT HEAD")
    admitted: list[int] = []
    refused: list[int] = []
    noaddr: list[int] = []
    for n in readish:
        _d, _why, url = table[n]
        if url is None:
            noaddr.append(n)
            print(f"  J {n:<4} NO READABLE ADDRESS   (behind a press, an upload, "
                  f"or a surface nobody has located)")
            continue
        ok = admits(url)
        (admitted if ok else refused).append(n)
        print(f"  J {n:<4} {'ADMITTED' if ok else 'REFUSED '}  {url}")
    print(f"\n  ADMITTED at HEAD      {len(admitted):3d}  "
          f"{' '.join('J %d' % n for n in admitted)}")
    print(f"  REFUSED at HEAD       {len(refused):3d}  "
          f"{' '.join('J %d' % n for n in refused)}")
    print(f"  no readable address   {len(noaddr):3d}  "
          f"{' '.join('J %d' % n for n in noaddr)}")

    if args.control_stub_admits:
        # THE ASSERTION IS ON THE REPORT, not on the stub. Checking that the
        # stub returns True would be a tautology; the question is whether the
        # printed reachability follows the boundary it was handed. The real
        # boundary refuses some of these addresses, so a report that still
        # prints REFUSED here is reading the table in this file, not the gate.
        ok = not refused and len(admitted) == len(readish) - len(noaddr)
        verdict = ("was non-empty on the real boundary -- THE COLUMN FOLLOWS "
                   "THE BOUNDARY") if ok else (
                   "STALE -- the column is read off this file, BROKEN")
        print(f"\ncontrol-stub-admits: every address admitted by a stub; "
              f"refused set is now {len(refused)} -- {verdict}")
        return 0 if ok else 1

    if args.emit_tsv:
        dest = pathlib.Path(args.emit_tsv)
        lines = ["row\tdirection\treachable_at_head\taddress\twhy"]
        for n in gap:
            d, why, url = table[n]
            if d in ("R", "RW") and url is not None:
                reach = "ADMITTED" if admits(url) else "REFUSED"
            elif d in ("R", "RW"):
                reach = "NO-ADDRESS"
            else:
                reach = "n/a-write"
            flat = why.replace("\t", " ").replace("\n", " ")
            lines.append(f"J {n}\t{d}\t{reach}\t{url or ''}\t{flat}")
        dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\nwrote {dest}")

    return 1 if drifted else 0


if __name__ == "__main__":
    sys.exit(main())
