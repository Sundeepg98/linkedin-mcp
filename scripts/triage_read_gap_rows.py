"""The READ-direction GAP rows of `profile.md` and `network.md`, by REMAINING COST.

WHY THIS EXISTS, AND WHY IT IS NOT THE MESSAGING TRIAGE AGAIN.
`scripts/triage_messaging_gap_rows.py` splits a slice by DIRECTION and by
BLOCKER. Both of those are columns somebody else wrote; that script joins and
does not judge, which is why it can refuse on an unjoined row and stop. This
one answers a different question -- **what is the remaining cost of each read
row** -- and the answer is a JUDGEMENT, taken row by row in
`_audit/2026-09-21-the-read-triage.md` and written down here so it can be
checked against the census instead of quoted from prose.

A verdict in a document is a number nobody can re-derive. A verdict in a table
whose KEY SET is re-computed from the shipped census on every run goes RED the
moment the census moves underneath it -- a row leaving GAP, a row entering it,
a direction cell edited from W to R. That tripwire is the whole point of the
file; the tally is a by-product.

## THE CLOSED ALPHABET, AND WHY EACH VERDICT NAMES A COST AND NOT A FEELING

    BUILDABLE      a shipped @mcp.tool() already reaches the payload, or a
                   reader over an ALREADY-ADMITTED address would. No boundary
                   edit, no ruling, no press.
    ADDRESS        the surface exists and nothing admits it. Sub-labelled
                   REFUSED (a forbidden substring names it, which fires BEFORE
                   the allowlist and therefore needs a pattern AND an
                   exemption) or ABSENT (no pattern names it; nothing refuses
                   it either). Those are different costs and the census has
                   repeatedly recorded one as the other.
    RULING         somebody has to decide something first. The decision is
                   named in the deliverable, never the row.
    PRESS          behind a control this package does not sanction clicking --
                   off `press.SANCTIONED_SHAPES`, or a submit/navigate that
                   `_audit/2026-09-19-the-disclosing-press-ruling.md` refuses
                   outright.
    SERVED         the payload is reachable today. The row's recorded reason is
                   stale. **NO STATE IS MOVED BY THIS FILE OR BY THE DOCUMENT
                   THAT QUOTES IT** -- a state move needs a fire or a ruling,
                   and this script has neither.

**THE VERDICT IS THE BINDING GATE, NOT EVERY GATE.** Several rows carry two:
`P C8` needs a press AND a transport this package does not have. The verdict
names the EARLIEST one, because that is the one a wave would hit first, and the
row's line says so.

## WHAT IT IMPORTS RATHER THAN REIMPLEMENTS

`count_census_states` for the parse, `enumerate_gap_rows` for the counter
control, `reader_closable_blockers.direction_of` for the R/W column -- which is
VALUE-based because a positional reader read a Help Center reference as a
direction. Four waves on 2026-09-05 wrote a second copy of a shipped instrument
and three of the copies had a bug. The standing rule is to import.

## IT SWEEPS NO CORPUS, AND CONTROL 6 PROVES IT

`_audit/INDEX.md` is a DERIVED view of `_audit/`, and three sweeping
instruments have already needed an explicit exclusion for it (INSTRUMENTS.md
45.9) because a derived view of a corpus must not be an input to the
instruments that measure that corpus. This script reads the TWO census slices
of its `SCOPE` (`profile.md`, `network.md`), taken from
`count_census_states.SLICES`, and nothing else. Control 6 prints the
census files the module opens and refuses if any of them is an index file, so
the exclusion is a measured property rather than a promise: if a future edit
points this file at `_audit/` it goes red rather than quiet.

USAGE

    python scripts/triage_read_gap_rows.py
    python scripts/triage_read_gap_rows.py --verdict BUILDABLE
    python scripts/triage_read_gap_rows.py --plant drop-a-row
    python scripts/triage_read_gap_rows.py --plant bad-verdict
    python scripts/triage_read_gap_rows.py --plant stale-annotation

`--plant` is how this file is SHOWN FAILING. An instrument that has only ever
been seen passing certifies nothing, and a triage table is exactly the shape
that passes forever by accident.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import count_census_states as ccs  # noqa: E402
import enumerate_gap_rows as egr  # noqa: E402
import reader_closable_blockers as rcb  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]

#: The two slices this triage covers. `messaging-and-content.md` was triaged by
#: `_audit/2026-09-20-the-messaging-gap.md` and `jobs.md` carries no per-row
#: direction column at all, so neither is in scope here and neither is silently
#: folded in.
SCOPE = ("P", "N")

#: The closed verdict alphabet. Control 4 refuses anything off it.
VERDICTS = ("BUILDABLE", "ADDRESS", "RULING", "PRESS", "SERVED")

#: row key -> (verdict, sub-label or '', the binding gate in one line).
#: Taken row by row in `_audit/2026-09-21-the-read-triage.md`, which carries the
#: evidence for every line. No identifier of any person, employer, campus or
#: profile appears here or there: every address is written with a placeholder.
TRIAGE: dict[str, tuple[str, str, str]] = {
    # ---- profile.md ----
    "P A25": ("PRESS", "", "entry control declares neither aria-expanded nor "
                          "aria-haspopup, so it is OFF press.SANCTIONED_SHAPES; "
                          "the overlay address is unadmitted as well"),
    "P C8": ("RULING", "", "blocked on TRANSPORT: in ATTACH mode the package "
                           "never creates a context and accept_downloads is a "
                           "context-creation option"),
    "P D25": ("ADDRESS", "ABSENT", "the add-section anchors measure "
                                   "is_read_url False with zero forbidden "
                                   "tokens; the operator must name the address"),
    "P D28": ("PRESS", "", "measured distinct_langs 1 and the measuring "
                           "document states it pressed nothing and proves no "
                           "pressable control exists"),
    "P F1": ("ADDRESS", "ABSENT", "the /in/me/details/ admission is restricted "
                                  "to experience, education and skills; "
                                  "recommendations.py ships and is UNWIRED"),
    "P G6": ("ADDRESS", "ABSENT", "no per-post analytics address is admitted "
                                  "and no module builds one from a urn"),
    "P H11": ("ADDRESS", "ABSENT", "the services detail address is unadmitted; "
                                   "the phrase is in an EXCLUSION set on the "
                                   "topcard path, discarded before parsing"),
    "P J4": ("PRESS", "", "the hiring state is behind the Open-to menu; two "
                          "independent measurements read the hiring control "
                          "NAMED BUT INERT and the opener AMBIGUOUS"),
    "P K8": ("SERVED", "", "measured live at allowlist +0 on an instrument "
                           "shown able to disagree with itself: no such badge "
                           "is drawn on this account"),
    "P L1": ("ADDRESS", "ABSENT", "the audience surface is unadmitted and is "
                                  "pinned refused by a committed test"),
    "P L2b": ("ADDRESS", "REFUSED", "every follower-list spelling carries the "
                                    "forbidden substring /follow, which no "
                                    "exemption covers"),
    "P L4": ("ADDRESS", "ABSENT", "the newsletter analytics address is named "
                                  "in readonly.py among those NOT admitted"),
    "P L7": ("ADDRESS", "ABSENT", "creator hub; the blocker's address is "
                                  "DISPUTED in the corpus and unadmitted "
                                  "either way"),
    "P L8": ("ADDRESS", "ABSENT", "same hub, same dispute; the analytics tree "
                                  "root is refused"),
    "P M12": ("ADDRESS", "REFUSED", "the application-settings address carries "
                                    "the FIRST entry on the forbidden tuple; "
                                    "reopening it is the operator's"),
    "P O3": ("BUILDABLE", "", "address admitted and already loaded by a shipped "
                              "tool; the press is RULED permitted, the guard "
                              "and its witness are BUILT; one shaper is missing"),
    "P O23": ("RULING", "", "measurable only by firing a profile write and "
                            "observing another account; writes_enabled is "
                            "False"),
    # ---- network.md ----
    "N 61": ("ADDRESS", "REFUSED", "both followed-hashtag spellings contain "
                                   "/follow, matching inside the word "
                                   "'followed' -- a substring hit, not a "
                                   "ruling anybody wrote"),
    "N 76": ("PRESS", "", "named by the disclosing-press ruling as a consumer; "
                          "nothing has pressed the control and no tool builds "
                          "a personal follow link"),
    "N 79": ("RULING", "", "the shipped tool takes NO parameter by design; "
                           "passing a keyword is a decision the shaper names "
                           "and nobody has made"),
    "N 80": ("BUILDABLE", "", "served by the shipped people-search tool's "
                              "filter vocabulary"),
    "N 81": ("BUILDABLE", "", "served by the shipped people-search tool's "
                              "filter vocabulary"),
    "N 82": ("BUILDABLE", "", "served by the shipped people-search tool's "
                              "filter vocabulary"),
    "N 84": ("BUILDABLE", "", "served by the shipped people-search tool's "
                              "filter vocabulary"),
    "N 85": ("BUILDABLE", "", "served by the shipped people-search tool's "
                              "filter vocabulary"),
    "N 86": ("BUILDABLE", "", "served by the shipped people-search tool's "
                              "filter vocabulary"),
    "N 87": ("BUILDABLE", "", "served by the shipped people-search tool's "
                              "filter vocabulary"),
    "N 88": ("BUILDABLE", "", "served by the shipped people-search tool's "
                              "filter vocabulary"),
    "N 89": ("BUILDABLE", "", "served by the shipped people-search tool's "
                              "filter vocabulary"),
    "N 90": ("BUILDABLE", "", "served by the shipped people-search tool's "
                              "filter vocabulary"),
    "N 91": ("BUILDABLE", "", "served by the shipped people-search tool's "
                              "filter vocabulary"),
    "N 92": ("BUILDABLE", "", "served by the shipped people-search tool's "
                              "filter vocabulary"),
    "N 93": ("BUILDABLE", "", "served by the shipped people-search tool's "
                              "filter vocabulary"),
    "N 94": ("RULING", "", "NO term serves it -- the shaper's own rule says a "
                           "row with no term is a row it cannot serve; a "
                           "multi-value query is the keyword decision again"),
    "N 95": ("ADDRESS", "ABSENT", "no search-history address is admitted and "
                                  "none is refused either; the row is also "
                                  "unrouted in the blocker map"),
    "N 99": ("RULING", "", "the school root is admitted and the alumni tab is "
                           "refused by the member-roster cause; overturning "
                           "that is a decision"),
    "N 100": ("RULING", "", "same tab, same cause, same decision"),
    "N 102": ("RULING", "", "the Page root is admitted and the People tab is "
                            "refused by the same member-roster ruling, by the "
                            "anchor and by nothing else"),
    "N 104": ("RULING", "", "the non-search half SHIPPED 2026-09-20; the "
                            "'by searching' half needs the companies vertical, "
                            "which the admission deliberately left out"),
    "N 132": ("RULING", "", "both sides of the switch are reachable today by "
                            "two shipped tools; whether that discharges a row "
                            "named for the CONTROL is a census convention "
                            "nobody has ruled"),
    "N 133": ("PRESS", "", "applying a filter SUBMITS, and the disclosing-press "
                           "ruling refuses submits by name"),
    "N 134": ("BUILDABLE", "", "address admitted, press RULED permitted, guard "
                               "and witness BUILT, sanctioned shapes measured "
                               "present on the page; one shaper is missing"),
    "N 161": ("RULING", "", "the groups vertical was deliberately left out of "
                            "the search admission, which names the "
                            "request-to-widen route instead"),
    "N 171": ("RULING", "", "a passive COST of an act, not an act; whether a "
                            "cost is a capability row is a census convention "
                            "nobody has ruled"),
    "N 172": ("RULING", "", "needs another member's connection list, refused "
                            "by the boundary's sharpest cause in its own words"),
    "N 174": ("RULING", "", "the surface is unobservable until a pending "
                            "request exists, and creating one is a WRITE at a "
                            "real group"),
    "N 177": ("RULING", "", "needs a group's member directory, refused here "
                            "and, in the boundary's own words, anywhere"),
    "N 178": ("RULING", "", "needs another member's profile, the boundary's "
                            "sharpest refusal"),
    "N 179": ("RULING", "", "the events vertical was deliberately left out of "
                            "the search admission"),
    "N 183": ("RULING", "", "a SETTING, which the boundary's own comment says "
                            "lives under preferences; whether the standing "
                            "settings ruling reaches it is unruled"),
    "N 184": ("ADDRESS", "ABSENT", "the events family admits the root only -- "
                                   "one segment narrower than the groups "
                                   "family, which admits the id"),
    "N 194": ("RULING", "", "its recorded blocker has EXPIRED; what remains is "
                            "the keyword decision, since the needle is a "
                            "hashtag typed into a search"),
    "N A3": ("ADDRESS", "REFUSED", "carries /follow, which fires before the "
                                   "allowlist, so it needs a pattern AND an "
                                   "exemption; and admin rights are unmeasured"),
    "N A5": ("ADDRESS", "REFUSED", "carries /invite, same double cost, same "
                                   "unmeasured precondition"),
}

#: LEFT GAP SINCE THE 2026-09-21 TRIAGE, measured 2026-09-23 with
#: census_completion.walk():
#:
#:     N 33   COVERED-CANNOT-DELIVER   (its triage verdict was BUILDABLE)
#:     N 53   COVERED-PROVEN           (was SERVED)
#:     N 54   COVERED-CANNOT-DELIVER   (was BUILDABLE)
#:     N 83   COVERED-PROVEN           (was BUILDABLE)
#:     N 175  COVERED-CANNOT-DELIVER   (was BUILDABLE)
#:
#: They were removed rather than kept because CONTROL 4 refuses a verdict for
#: a row that is not a read-GAP row, and that refusal is the tripwire this
#: file exists to carry.

#: These four 2026-09-21 verdicts were measured past by the bucket-3 address
#: table (`_audit/_census/read-addresses.tsv`, audit
#: `_audit/2026-09-23-bucket3-addresses.md`, whose CORRECTS line names exactly
#: these four); this triage's closed alphabet has no class for MEASURE or
#: NEEDS-SESSION, so the verdict letters are kept as that day's reading and
#: the table that measured past them is named instead of being overwritten.
MEASURED_PAST_BY_BUCKET3: dict[str, str] = {
    "P F1": "the section sits on the ADMITTED /in/me/; bucket-3 gate MEASURE "
            "(render unmeasured), not ADDRESS/ABSENT",
    "P H11": "the section sits on the ADMITTED /in/me/; bucket-3 gate "
             "MEASURE (render unmeasured), not ADDRESS/ABSENT",
    "P L4": "waits on a LIVE READ of which address serves newsletter "
            "analytics (bucket-3 NEEDS-SESSION), not on a refused address "
            "anybody has seen served",
    "N 61": "waits on a LIVE READ of where followed hashtags are drawn "
            "(bucket-3 NEEDS-SESSION), not on a refused address anybody has "
            "seen served",
}


def read_rows() -> dict[str, str]:
    """Row key -> direction, for every stated GAP row in the two scoped slices.

    The filter is the SHIPPED one, copied from
    `reader_closable_blockers.main` rather than re-invented, including the
    admin-only forcing that lives inside the counter's `main()` and has no seam.
    """
    out: dict[str, str] = {}
    for letter, name in ccs.SLICES.items():
        if letter not in SCOPE:
            continue
        path = ccs.CENSUS / name
        for line in path.read_text(encoding="utf-8",
                                   errors="replace").splitlines():
            if not line.startswith("|"):
                continue
            c = ccs.cells(line)
            if len(c) < 3:
                continue
            if c[0] and set(c[0]) <= set("-: "):
                continue
            if not ccs.ROW.match(line) or c[0].lower() in ccs.HEADERS:
                continue
            st = ccs.state_of(c)
            if not st and letter == "N" and egr.ADMIN_ONLY.fullmatch(c[0]):
                st = "GAP"
            if st != "GAP":
                continue
            out[f"{letter} {c[0]}"] = rcb.direction_of(c)
    return out


def files_read() -> set[str]:
    """Every census file this module opens. Control 6 prints it and refuses
    if any member is an index file."""
    return {name for letter, name in ccs.SLICES.items() if letter in SCOPE}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verdict", default="",
                    help="list only the rows carrying this verdict")
    ap.add_argument("--plant", default="", choices=["", "drop-a-row",
                                                    "bad-verdict",
                                                    "stale-census",
                                                    "stale-annotation"],
                    help="SHOW THIS INSTRUMENT FAILING on a planted defect")
    args = ap.parse_args(argv)

    triage = dict(TRIAGE)
    if args.plant == "drop-a-row":
        victim = sorted(triage)[0]
        del triage[victim]
        print(f"PLANTED: {victim} removed from the verdict table. "
              f"Control 4 must refuse.\n")
    if args.plant == "bad-verdict":  # noqa: SIM114 -- distinct planted defect
        victim = sorted(triage)[0]
        triage[victim] = ("PROBABLY-FINE", "", "a verdict off the alphabet")
        print(f"PLANTED: {victim} given a verdict off the closed alphabet. "
              f"Control 5 must refuse.\n")

    # A COPY, NEVER THE MODULE DICT -- CONTROL 7 reads this, and the
    # stale-annotation plant must not be able to touch MEASURED_PAST_BY_BUCKET3
    # itself, or a planted defect would outlive the process that planted it.
    annotations = dict(MEASURED_PAST_BY_BUCKET3)
    if args.plant == "stale-annotation":
        annotations["N 99999"] = "planted: no row carries this key"
        print("PLANTED: an annotation for a row with no verdict. "
              "Control 7 must refuse.\n")

    failures = 0

    print("  CONTROL 1 -- the shipped enumerator agrees with the shipped counter")
    if egr.control(None):
        print("  REFUSING: the enumerator disagrees with the counter.")
        return 1

    if rcb.control_negative():
        print("  REFUSING: the direction reader could not be shown refusing.")
        return 1

    gap = read_rows()
    reads = {k for k, d in gap.items() if d == "R"}
    if args.plant == "stale-census":
        # THE OTHER DIRECTION, AND IT IS THE ONE THIS FILE EXISTS FOR. A row
        # LEAVING the read-GAP set -- banked, re-ruled, or its direction cell
        # corrected from R to W -- leaves a verdict behind pointing at nothing.
        # A control that only catches a MISSING verdict cannot see that, and a
        # stale verdict is the failure a triage table decays into.
        victim = sorted(reads)[0]
        reads.discard(victim)
        print(f"PLANTED: {victim} removed from the census-derived read-GAP "
              f"set, as a bank or a direction correction would. Control 4 "
              f"must refuse.\n")

    # CONTROLS 1-3 ARE IMPORTED AND PRINT THEIR OWN LABELS -- the counter
    # agreement from `enumerate_gap_rows.control` and the direction reader
    # shown refusing from `reader_closable_blockers.control_negative`. This
    # file's own controls start at 4 so a reader can tell whose is whose.
    print("\n  CONTROL 4 -- the verdict table's key set IS the read-GAP set")
    missing = sorted(reads - set(triage))
    extra = sorted(set(triage) - reads)
    print(f"      read-direction GAP rows in {'+'.join(SCOPE)}  {len(reads):3d}")
    print(f"      rows carrying a verdict                 {len(triage):3d}")
    if missing or extra:
        failures += 1
        for key in missing:
            print(f"      NO VERDICT for {key} -- it is a read GAP row today")
        for key in extra:
            print(f"      VERDICT for {key}, which is NOT a read GAP row today")
    else:
        print("      identical -- OK")

    print("\n  CONTROL 5 -- every verdict is on the closed alphabet")
    off = sorted(k for k, v in triage.items() if v[0] not in VERDICTS)
    if off:
        failures += 1
        for key in off:
            print(f"      {key} carries {triage[key][0]!r}, which is not one "
                  f"of {VERDICTS}")
    else:
        print(f"      {len(triage)} verdicts, all on {VERDICTS} -- OK")

    print("\n  CONTROL 6 -- this instrument sweeps no corpus")
    want = files_read()
    print(f"      census files read: {sorted(want)}")
    if "INDEX.md" in want or any("INDEX" in n for n in want):
        failures += 1
        print("      REFUSING: a derived view is an input to this instrument.")
    else:
        print("      _audit/INDEX.md is NOT among them -- OK")

    print("\n  CONTROL 7 -- every MEASURED_PAST_BY_BUCKET3 key still carries "
          "a verdict")
    orphaned = sorted(k for k in annotations if k not in triage)
    if orphaned:
        failures += 1
        for key in orphaned:
            print(f"      {key} carries an annotation but NO VERDICT in the "
                  f"triage table -- an annotation for a row that has left "
                  f"must not outlive the row")
    else:
        print(f"      {len(annotations)} annotations, every key carries a "
              f"verdict -- OK")

    if failures:
        print(f"\n  REFUSING TO REPORT: {failures} control failure(s). A triage "
              f"that cannot be shown to cover every row should not print a "
              f"tally at all.")
        return 1

    counts: dict[str, int] = {v: 0 for v in VERDICTS}
    per_slice: dict[str, dict[str, int]] = {
        s: {v: 0 for v in VERDICTS} for s in SCOPE}
    for key, (verdict, _sub, _why) in triage.items():
        counts[verdict] += 1
        per_slice[key.split(" ")[0]][verdict] += 1

    print("\n" + "=" * 74)
    print("  THE READ-GAP TRIAGE, BY REMAINING COST")
    print("=" * 74)
    print(f"  {'verdict':12s} {'P':>4s} {'N':>4s} {'total':>7s}")
    for v in VERDICTS:
        print(f"  {v:12s} {per_slice['P'][v]:4d} {per_slice['N'][v]:4d} "
              f"{counts[v]:7d}")
    print(f"  {'TOTAL':12s} {sum(per_slice['P'].values()):4d} "
          f"{sum(per_slice['N'].values()):4d} {sum(counts.values()):7d}")

    print(f"\n  {len(MEASURED_PAST_BY_BUCKET3)} OF THESE VERDICTS WERE "
          f"MEASURED PAST BY THE BUCKET-3 ADDRESS TABLE "
          f"(_audit/_census/read-addresses.tsv):")
    for key in sorted(MEASURED_PAST_BY_BUCKET3):
        verdict = triage[key][0]
        note = MEASURED_PAST_BY_BUCKET3[key]
        print(f"    {key}  {verdict}  -- {note}")

    if args.verdict:
        want_v = args.verdict.upper()
        print(f"\n  ROWS CARRYING {want_v}")
        for key in sorted(triage, key=_sort_key):
            verdict, sub, why = triage[key]
            if verdict != want_v:
                continue
            label = f"{verdict}{'/' + sub if sub else ''}"
            print(f"    {key:8s} {label:18s} {why}")

    print("\n  NO STATE IS MOVED BY THIS FILE. SERVED means the payload is "
          "reachable and the\n  row's recorded reason is stale; banking it "
          "needs a fire or a ruling, and this\n  script has neither.")
    return 0


def _sort_key(key: str) -> tuple[str, int, str]:
    letter, _sep, rid = key.partition(" ")
    digits = "".join(ch for ch in rid if ch.isdigit())
    return (letter, int(digits) if digits else 0, rid)


if __name__ == "__main__":
    sys.exit(main())
