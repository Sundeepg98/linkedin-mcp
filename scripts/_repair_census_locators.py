"""ONE-SHOT, ALREADY APPLIED: line-number locators -> row-label locators.

Applied 2026-09-21 to `_audit/_census/blocker-assignments.tsv`, converting the
76 census-sourced locators that cited LINE NUMBERS into citations of the
census's own ROW LABELS. Kept in the tree as the receipt for that conversion,
because the table below is the only place the reasoning for each one is
written down, and a migration nobody can audit is how the lost 2026-09-03
classifier became unauditable in the first place.

IDEMPOTENT. Re-running it on the repaired file changes nothing: every entry
asserts the OLD locator it expects to find, and a row already carrying the new
value is skipped. Run it against a file that has moved and it REFUSES rather
than guessing.

    venv/Scripts/python.exe scripts/_repair_census_locators.py --check
    venv/Scripts/python.exe scripts/_repair_census_locators.py --apply

HOW EACH NEW VALUE WAS DERIVED, and NONE of them is a fresh line number.
A freshly-computed line number is a defect with a later expiry date, not a fix.

The five classes, and `--check` prints these counts off the table itself so a
drift between this paragraph and the code shows up as a number, not as prose.

  SELF, 39 rows. `git blame` the TSV line, read the source slice AS OF THAT
  COMMIT, take the label of the row at the cited line. On these the label IS
  the assignment's own row id, so the conversion confirms itself and needs no
  judgment: `J 57`'s `L200` was row 57 at eb11edd, and becomes `57`.

  RANGE, 21 rows. Same method over every line in the range, then the resulting
  label span was read against the slice to check the rows are the family the
  blocker is about. `L406-L418` covered profile rows L1..L8, which is section
  L "Creator tools", which is CREATOR-HUB-SURFACE.

  ANNOT, 9 rows. Three distinct locators carry their own words --
  `(section 2 grouping)`, `rows 24-30`, `rows 85-86` -- and on all three the
  derived label CONTRADICTED the words. Checked by hand: in each case the words
  name a real row and the line number was already stale at the commit that
  wrote it. The words are the half of the citation that does not rot, and they
  were written by the same author in the same cell, so they are preferred.
  Each carries a comment below saying what the derivation said instead.

  BIRTH, 1 row. `M C49`'s `L439` named row `C50` at the commit that wrote it --
  an off-by-one on the day, not drift. Its note reads "as M C46", and M C46's
  own locator resolved correctly to C46. Converted to `C49`, which is what the
  assignment is about.

  GROUP, 6 rows. Locators pointing at a roll-up row whose first cell is bold
  text running to forty words. Cited by the bold text alone.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TSV = ROOT / "_audit" / "_census" / "blocker-assignments.tsv"

#: row_id -> (the locator this expects to find, the locator it writes, why).
#: WHY IS A CODE, not prose, so the classes above can be counted from here:
#:   SELF     the derived label is the row's own id
#:   RANGE    a label span, read against the slice to confirm the family
#:   ANNOT    the locator's own words beat the derived label (see docstring)
#:   BIRTH    the line number was wrong on the day it was written
#:   GROUP    a roll-up row cited by its bold name
REPAIRS: dict[str, tuple[str, str, str]] = {
    # -- profile -------------------------------------------------------
    "P L1":  ("L406-L418 (section L)", "L1-L8 (section L)", "RANGE"),
    "P L7":  ("L406-L418 (section L)", "L1-L8 (section L)", "RANGE"),
    "P L8":  ("L406-L418 (section L)", "L1-L8 (section L)", "RANGE"),
    "P C8":  ("L242", "C8", "SELF"),
    "P L6":  ("L416", "L6", "SELF"),
    "P G6":  ("L314", "G6", "SELF"),
    "P O23": ("L485", "O23", "SELF"),
    "P M11": ("L434-L435", "M11-M12", "RANGE"),
    "P M12": ("L434-L435", "M11-M12", "RANGE"),
    "P K8":  ("L223-L225, L399-L401", "B7-B9, K8-K10", "RANGE"),
    "P K10": ("L223-L225, L399-L401", "B7-B9, K8-K10", "RANGE"),
    "P B9":  ("L223-L225, L399-L401", "B7-B9, K8-K10", "RANGE"),
    # -- jobs ----------------------------------------------------------
    # ANNOTATION: the derivation read L389 as row `78-83` (Premium apply
    # extras) at bc721dc. The words say "section 2 grouping", and section 2's
    # grouping row for these rows is `106-114`, three lines further down. The
    # line number was already stale at that commit.
    "J 106": ("L269-L278 (section G), L389 (section 2 grouping)",
              "106-115 (section G), 106-114 (section 2 grouping)", "ANNOT"),
    "J 108": ("L269-L278 (section G), L389 (section 2 grouping)",
              "106-115 (section G), 106-114 (section 2 grouping)", "ANNOT"),
    "J 109": ("L269-L278 (section G), L389 (section 2 grouping)",
              "106-115 (section G), 106-114 (section 2 grouping)", "ANNOT"),
    "J 110": ("L269-L278 (section G), L389 (section 2 grouping)",
              "106-115 (section G), 106-114 (section 2 grouping)", "ANNOT"),
    "J 111": ("L269-L278 (section G), L389 (section 2 grouping)",
              "106-115 (section G), 106-114 (section 2 grouping)", "ANNOT"),
    "J 113": ("L269-L278 (section G), L389 (section 2 grouping)",
              "106-115 (section G), 106-114 (section 2 grouping)", "ANNOT"),
    "J 114": ("L269-L278 (section G), L389 (section 2 grouping)",
              "106-115 (section G), 106-114 (section 2 grouping)", "ANNOT"),
    "J 112": ("L275", "112", "SELF"),
    "J 39":  ("L177", "39", "SELF"),
    "J 40":  ("L178", "40", "SELF"),
    "J 57":  ("L200", "57", "SELF"),
    "J 131": ("L311", "131", "SELF"),
    "J 124": ("L292-L294 (section H)", "124-126 (section H)", "RANGE"),
    "J 125": ("L292-L294 (section H)", "124-126 (section H)", "RANGE"),
    "J 126": ("L292-L294 (section H)", "124-126 (section H)", "RANGE"),
    # Both tokens derived to the SAME label `68`: the capability row and
    # section 2's grouping row carry the same first cell. One token now.
    "J 68":  ("L216, L387", "68", "SELF"),
    "J 71":  ("L217-L219, L388", "69-71, 70-73 (section 2 grouping)", "RANGE"),
    "J 72":  ("L217-L219, L388", "69-71, 70-73 (section 2 grouping)", "RANGE"),
    "J 73":  ("L217-L219, L388", "69-71, 70-73 (section 2 grouping)", "RANGE"),
    "J 129": ("L357, L443", "129", "SELF"),
    # ANNOTATION: L435 derived to row `68`; the words say "rows 24-30", which
    # is a real section 2 row and the one that holds row 28 (report-closed).
    "J 28":  ("L207, L435 rows 24-30", "28, 24-30", "ANNOT"),
    # ANNOTATION: L437 derived to `78-83`; the words say "rows 85-86", which
    # is the next row down and the one holding row 85 (undo a dismissal).
    "J 85":  ("L286, L437 rows 85-86", "85, 85-86", "ANNOT"),
    "J 86":  ("L287, L438", "86, 85-86", "SELF"),
    "J 18":  ("L428", "18-19", "SELF"),
    "J 19":  ("L428", "18-19", "SELF"),
    # -- messaging-and-content ----------------------------------------
    "M C12": ("L401", "C12", "SELF"),
    "M C8":  ("L397", "C8", "SELF"),
    "M C9":  ("L398", "C9", "SELF"),
    "M C85": ("L474", "C85", "SELF"),
    "M C37": ("L426", "C37", "SELF"),
    "M C38": ("L427", "C38", "SELF"),
    "M C39": ("L428", "C39", "SELF"),
    "M C40": ("L429", "C40", "SELF"),
    "M C46": ("L435", "C46", "SELF"),
    "M C49": ("L439", "C49", "BIRTH"),
    "M C74": ("L463", "C74", "SELF"),
    "M C78": ("L467", "C78", "SELF"),
    "M C79": ("L468", "C79", "SELF"),
    "M M16": ("L347-L348", "M16-M17", "RANGE"),
    "M M17": ("L347-L348", "M16-M17", "RANGE"),
    "M M48": ("L379, L480, L496",
              "M48, C91, Message composition beyond plain text", "GROUP"),
    "M C29": ("L418, L500", "C29, Comment surface", "GROUP"),
    "M C90": ("L479, L500", "C90, Comment surface", "GROUP"),
    "M M35": ("L498 (group of 11), L366 (M35 row), L365 (M34 filed elsewhere)",
              "Conversation management (group of 11), M35 (M35 row), "
              "M34 (M34 filed elsewhere)", "GROUP"),
    "M M49": ("L498 (group of 11), L380 (M49 row), L368 (M37 is the setting)",
              "Conversation management (group of 11), M49 (M49 row), "
              "M37 (M37 is the setting)", "GROUP"),
    # The ONE line number in this file that never rotted, because it was
    # COMMIT-ANCHORED. Rewritten in words rather than in the `L<n>` shape, so
    # the guard does not have to special-case an exception to its own rule.
    "M M5":  ("L336@1c08e5f (ledger L326)",
              "M5 (the ledger's own line 326, as of 1c08e5f)", "SELF"),
    # -- network -------------------------------------------------------
    "N 99":  ("L355", "99", "SELF"),
    "N 100": ("L356", "100", "SELF"),
    "N 37":  ("L265", "37", "SELF"),
    "N 43":  ("L271", "43", "SELF"),
    "N 148": ("L456", "148", "SELF"),
    "N 153": ("L461", "153", "SELF"),
    "N 154": ("L462", "154", "SELF"),
    "N 101": ("L357-L358", "101-102", "RANGE"),
    "N 102": ("L357-L358", "101-102", "RANGE"),
    "N 6":   ("L200-L202", "6-8", "RANGE"),
    "N 7":   ("L200-L202", "6-8", "RANGE"),
    "N 8":   ("L200-L202", "6-8", "RANGE"),
    "N 5":   ("L199", "5", "SELF"),
    "N 33":  ("L250, L286, L287", "33, 53, 54", "SELF"),
    "N 53":  ("L286", "53", "SELF"),
    "N 54":  ("L287", "54", "SELF"),
    "N 47":  ("L280", "47", "SELF"),
    "N 104": ("L360, L584", "104, Company pages", "GROUP"),
}


def rewrite(text: str) -> tuple[str, list[str], list[str]]:
    """(new text, rows changed, complaints). Refuses by reporting, not raising."""
    out: list[str] = []
    changed: list[str] = []
    complaints: list[str] = []
    hit: set[str] = set()
    for line in text.splitlines():
        if line.startswith(">") or "\t" not in line:
            out.append(line)
            continue
        fields = line.split("\t")
        if len(fields) < 5 or fields[0] == "blocker":
            out.append(line)
            continue
        row_id, locator = fields[1], fields[4]
        spec = REPAIRS.get(row_id)
        if spec is None:
            out.append(line)
            continue
        want, new, _why = spec
        hit.add(row_id)
        if locator == new:
            out.append(line)
            continue
        if locator != want:
            complaints.append(
                "%s: expected locator %r, found %r. NOT rewritten -- the file "
                "has moved since this repair was derived, and rewriting on a "
                "guess is the defect this repair exists to remove."
                % (row_id, want, locator))
            out.append(line)
            continue
        fields[4] = new
        out.append("\t".join(fields))
        changed.append("%s  %s -> %s" % (row_id, want, new))
    missing = sorted(set(REPAIRS) - hit)
    if missing:
        complaints.append(
            "these row_ids are in the repair table and NOT in the file: %s"
            % missing)
    return "\n".join(out) + "\n", changed, complaints


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true", help="write the file")
    ap.add_argument("--check", action="store_true", help="report only")
    args = ap.parse_args(argv)

    text = TSV.read_text(encoding="utf-8")
    new, changed, complaints = rewrite(text)
    why: dict[str, int] = {}
    for _old, _new, code in REPAIRS.values():
        why[code] = why.get(code, 0) + 1
    print("repair table: %d rows -- %s" % (len(REPAIRS), why))
    print("rows this run would change: %d" % len(changed))
    for c in changed:
        print("  %s" % c)
    for c in complaints:
        print("REFUSED %s" % c)
    if complaints:
        return 1
    if args.apply and changed:
        TSV.write_text(new, encoding="utf-8", newline="\n")
        print("\nwritten.")
    elif not changed:
        print("\nalready repaired; nothing to do.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
