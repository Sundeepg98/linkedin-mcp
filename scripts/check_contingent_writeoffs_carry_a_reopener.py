"""Refuse a CONTINGENT write-off that names no condition which would reopen it.

THE DEFECT, STATED SO IT CAN BE ARGUED WITH. A census row written off
EXCLUDED-RULED asserts that somebody DECIDED not to build a capability. Some of
those decisions rest on a fact about the capability or about this codebase, and
those are durable -- a ruling is its own trigger, and re-ruling it is a visible
act. But 57 of them rest on a fact about the OPERATOR, his ACCOUNT, or the
WORLD: the account is not entitled to a thing, LinkedIn draws no such panel,
the balance is not on the page, the allowance is five a month.

**Those facts change, and nothing sends us a note.** A write-off resting on one
is not permanently excluded; it is excluded WHILE THE CONDITION HOLDS. With no
stated reopener, the distinction is invisible: the row reads exactly like a
permanent exclusion, and the census quietly shrinks its own denominator by an
amount nobody ruled and nobody can measure.

`_audit/2026-09-20-the-contingent-writeoffs.md` s6 put a number on it: **a
contingent write-off carrying a reopener is 15% still GAP; one carrying none is
91% still GAP**, and every contingent write-off yet found wrong sat in the
second group -- 5 of 5. The discipline already existed in this repository and
was applied to exactly one queue: `_audit/2026-09-05-decide-retire-rulings.md`
s6 gives every one of its twelve retirements a concrete reopener AND names who
can establish it. The other queue was exempt, and the exemption was measurable.

WHAT THIS GUARD DOES. It imports `classify_writeoff_reasons` -- the shipped
instrument, never a second parse -- and fails the run if a write-off row is
CONTINGENT and carries no `REOPENER` clause in its RESOLVED text.

RESOLVED, not raw, and that choice is load-bearing. 127 of the corpus's
write-off reason cells are POINTERS, not reasons: `same`, `R3`, a section
heading. Ten rows (`N 119`-`N 128`) have NO REASON CELL AT ALL -- their table
ships four columns. For those, the only place a reopener can live is the ruling
they point at, so the guard must read what the row RESOLVES to or it would
demand the impossible of a fifth of the corpus. The cost is named rather than
hidden: a backreference resolves BY POSITION, so a row inserted above a donor
silently re-points it and a reopener can evaporate without an edit to the row
that relied on it. **That is precisely why this runs as a guard instead of
being checked once** -- the fragility becomes a red run rather than a silent
loss.

    python scripts/check_contingent_writeoffs_carry_a_reopener.py
    python scripts/check_contingent_writeoffs_carry_a_reopener.py --demonstrate-red
    python scripts/check_contingent_writeoffs_carry_a_reopener.py --list

=============================================================================
FOUR WAYS THIS COULD HAVE BEEN A CHECK THAT CANNOT FAIL, AND WHAT STOPS EACH
=============================================================================

This repository found roughly ten distinct shapes of decorative control in one
day -- a control printing FAIL and certifying anyway, an assertion satisfied by
an empty result, a branch made unreachable by a default, a union assertion that
cannot detect a lost source. So each hole is closed deliberately and named:

1. **AN EMPTY RESULT WOULD PASS.** If the walk returned nothing -- a parse
   break, a renamed file, a `CENSUS` path that no longer exists -- there would
   be no offenders and the guard would print ok. So it asserts PER SLICE that
   the file yielded at least one contingent write-off, and a zero is a LOUD
   FAILURE naming the file. Per slice and never over the union, because a union
   assertion over a redundant corpus cannot detect a lost source: if
   `network.md` stopped being read, the other three would still satisfy it.

2. **AN EXEMPTION LIST WOULD GROW INTO A RUBBER STAMP.** Two rows are outside
   this wave's row-set and are pinned below. The pins are SELF-RETIRING: the
   guard fails if a pinned row NO LONGER needs its exemption. An allowlist that
   cannot go stale is the only kind worth having, and this one convicts itself
   the moment somebody fixes a row on it.

3. **IT WOULD CLAIM MORE THAN IT RAN.** Every run prints what it did NOT check
   -- the write-off states outside the enforced set, by name and count. A gate
   that prints PASS over a scope it never states is the half-truth that destroys
   the trust which made it useful.

4. **THE VERDICT LOGIC COULD BE RIGHT WHILE THE WALK FINDS NOTHING.**
   `--demonstrate-red` therefore runs TWO reds, not one. The first injects a
   synthetic row and proves the VERDICT fires. The second writes a planted row
   into a COPY of the real census on disk, repoints the walker at the copy, and
   proves the ROW IS FOUND end to end. Either alone is a control with a blind
   spot the size of the other.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import count_census_states as ccs              # noqa: E402
import classify_writeoff_reasons as cwr        # noqa: E402

#: The states this wave OWNS and enforces hard. Both spellings of the same
#: verdict, because the shipped counter reports `XR` under its own key exactly
#: so a downstream artifact cannot silently merge them.
ENFORCED_STATES = frozenset({"EXCLUDED-RULED", "XR"})

#: Rows that are contingent, carry no reopener, and are KNOWINGLY left so.
#: Each entry is a row id mapped to why. THESE SELF-RETIRE: see check 2 above.
#: Keep this list tiny. An exemption is a debt, not a decision.
PINNED_EXEMPTIONS: dict[str, str] = {
    "M M2": "COVERED-CANNOT-DELIVER, outside the EXCLUDED-RULED/XR row-set this "
            "wave was scoped to. Its contingent fact is the InMail allowance, "
            "the same one `network.md` R9 now carries a reopener for; the row "
            "needs one clause and an owner for that state class.",
    "N 57": "COVERED-CANNOT-DELIVER, outside this wave's row-set. Its "
            "contingent fact is what the account subscribes to, which changes "
            "the day he subscribes to anything.",
}


#: THE MARKER, AND WHY IT IS STRICTER THAN THE SHIPPED REGEX.
#: `classify_writeoff_reasons.REOPENER` is `REOPEN(?:ER|S)\b` CASE-INSENSITIVE.
#: That is right for its job -- reporting, where over-reach costs nothing -- and
#: WRONG for a gate, because it matches the ordinary verb. Found by mutation,
#: not by reading: stripping the real `REOPENER:` clause out of `P D13`/`P D14`
#: left this guard GREEN, because both cells also contain the sentence
#: *"the Help-article half REOPENS NOTHING"*. **A cell can then say, in
#: prose, that nothing reopens it, and satisfy a check whose whole subject is
#: whether something does.** That is a check that cannot fail in the exact case
#: it exists for, and this repo has found about ten shapes of that defect.
#:
#: The house marker is always SHOUTED -- `REOPENER:`, `REOPENER, NAMED:`,
#: `REOPENER, per the ruling:`, `REOPENER a parser over either capture`. The
#: ordinary verb is not. So the discriminator is CASE, and it is measured
#: rather than assumed: over the whole corpus exactly FIVE contingent rows pass
#: the loose regex without a shouted marker, and all five are the `P D13`/`D14`
#: family that prompted this -- so tightening convicts the mutation and moves
#: NOTHING else.
#:
#: NOT NARROWED FURTHER, deliberately. `REOPENER: none plausible` and
#: `REOPENER: nothing that keeps the shape` MUST keep passing: an argued "this
#: is genuinely permanent" is a real answer to "what would reopen this", and it
#: is how `decide-retire-rulings.md` s6 writes three of its twelve. The defect
#: is an UNMARKED sentence, never a negative verdict somebody defended.
REOPENER_MARKER = re.compile(r"REOPENER\b")


def offenders(rows) -> list:
    """Every write-off row that is contingent and names no reopener."""
    return [r for r in rows
            if r.contingent and not REOPENER_MARKER.search(r.resolved)]


def run(rows, verbose: bool = False) -> tuple[bool, list[str]]:
    """(failed, report lines). The whole verdict, with nothing printed."""
    out: list[str] = []
    failed = False

    writeoffs = [r for r in rows if r.state in cwr.WRITEOFF]
    contingent = [r for r in writeoffs if r.contingent]
    bad = offenders(writeoffs)

    out.append(f"write-off rows            : {len(writeoffs)}")
    out.append(f"  of which CONTINGENT     : {len(contingent)}")
    out.append(f"  contingent, no reopener : {len(bad)}")

    # --- HOLE 1: an empty result must be loud, and PER SLICE ----------------
    out.append("")
    out.append("PER-SLICE LIVENESS -- a slice contributing zero contingent write-offs")
    out.append("means it stopped being read, not that it got clean:")
    for letter, name in ccs.SLICES.items():
        n = sum(1 for r in contingent if r.letter == letter)
        if n == 0:
            out.append(f"  FAIL  {name}: 0 contingent write-off rows. Either this "
                       f"file is no longer being parsed, or the census changed "
                       f"shape. Both need a human, neither is a pass.")
            failed = True
        else:
            out.append(f"  ok    {name}: {n} contingent write-off rows read")

    # --- the verdict, split by whether this wave owns the state -------------
    enforced_bad = [r for r in bad if r.state in ENFORCED_STATES]
    other_bad = [r for r in bad if r.state not in ENFORCED_STATES]

    out.append("")
    out.append(f"ENFORCED SCOPE -- states {sorted(ENFORCED_STATES)}")
    if enforced_bad:
        out.append(f"  FAIL  {len(enforced_bad)} contingent write-off(s) name no "
                   f"condition that would reopen them:")
        for r in enforced_bad:
            out.append(f"          {r.key:<9} {r.state:<16} {r.kind}")
            out.append(f"            {r.slice_name()}:{r.lineno}  {r.capability[:64]}")
            out.append(f"            resolves via {r.resolution}")
        out.append("")
        out.append("  A write-off resting on a fact about the account or the world is")
        out.append("  excluded WHILE THAT FACT HOLDS. Add a `REOPENER:` clause naming")
        out.append("  the concrete observable that falsifies it, and WHO can establish")
        out.append("  it -- the shape `_audit/2026-09-05-decide-retire-rulings.md` s6")
        out.append("  uses for all twelve of its retirements. If the row resolves")
        out.append("  through a pointer, the clause belongs where the ARGUMENT is (the")
        out.append("  donor row, or the ruling body), not copied onto the pointer.")
        failed = True
    else:
        out.append(f"  ok    all {sum(1 for r in contingent if r.state in ENFORCED_STATES)}"
                   f" contingent write-offs in scope carry a reopener")

    # --- HOLE 2: exemptions that self-retire --------------------------------
    out.append("")
    out.append("PINNED EXEMPTIONS -- contingent, no reopener, knowingly left")
    unpinned = [r for r in other_bad if r.key not in PINNED_EXEMPTIONS]
    still_bad = {r.key for r in bad}
    for key, why in sorted(PINNED_EXEMPTIONS.items()):
        if key in still_bad:
            out.append(f"  held  {key}: {why[:88]}")
        else:
            out.append(f"  FAIL  {key} is pinned as exempt but NO LONGER NEEDS THE "
                       f"EXEMPTION -- it now carries a reopener, or stopped being "
                       f"contingent, or left the census. Delete the pin. An "
                       f"exemption list that cannot go stale is a rubber stamp.")
            failed = True
    if unpinned:
        out.append(f"  FAIL  {len(unpinned)} contingent write-off(s) outside the "
                   f"enforced states and NOT pinned:")
        for r in unpinned:
            out.append(f"          {r.key:<9} {r.state:<24} {r.capability[:50]}")
        out.append("        Give it a reopener, or pin it with a reason and an owner.")
        failed = True

    # --- HOLE 3: say what was NOT checked -----------------------------------
    out.append("")
    out.append("NOT CHECKED BY THIS RUN, stated rather than left to look like coverage:")
    unenforced_states = sorted({r.state for r in writeoffs} - ENFORCED_STATES)
    for st in unenforced_states:
        n = sum(1 for r in writeoffs if r.state == st)
        nc = sum(1 for r in contingent if r.state == st)
        out.append(f"  {st:<24} {n:3d} rows ({nc} contingent) -- reported, not enforced")
    ours = sum(1 for r in writeoffs if not r.contingent)
    out.append(f"  {'NON-CONTINGENT':<24} {ours:3d} rows -- a US-RULING or US-BOUNDARY")
    out.append(f"  {'':<24}     is its own trigger; re-ruling it is a visible act")
    out.append(f"  {'UNCLEAR kind':<24} "
               f"{sum(1 for r in writeoffs if r.kind == 'UNCLEAR'):3d} rows -- the rule "
               f"could not read them, so")
    out.append(f"  {'':<24}     they are neither convicted nor cleared here")
    return failed, out


def _slice_name(self) -> str:
    return cwr.ccs.SLICES[self.letter]


cwr.Row.slice_name = _slice_name


# --------------------------------------------------------------------------------------
# HOLE 4: TWO REDS, because either alone has a blind spot the size of the other
# --------------------------------------------------------------------------------------
#: A reason cell that is unmistakably CONTINGENT -- it asserts a fact about the
#: account -- and just as unmistakably carries no reopener. Deliberately built
#: from signals already in the shipped table (`he-holds`, `entitlement`) rather
#: than from a word invented for the test, so the red proves the REAL rule
#: fires rather than a rule written to be fired.
PLANTED_REASON = ("he has no Premium subscription on this account, so LinkedIn "
                  "draws no such panel for him and the entitlement is absent")
PLANTED_ROW = ("| 9901 | PLANTED CONTROL ROW -- not a capability | a000000 | "
               "EXCLUDED-RULED | " + PLANTED_REASON + " |")


def demonstrate_red() -> int:
    print("DEMONSTRATE-RED -- this guard must be able to CONVICT. THREE independent")
    print("reds: a verdict that fires on an injected row proves nothing about")
    print("whether the walk would ever hand it one, and neither proves that a")
    print("cell cannot satisfy the check with a sentence saying the opposite.\n")
    ok = True

    # ---- RED 1: the verdict logic ------------------------------------------
    print("RED 1 -- VERDICT LOGIC, on a synthetic row that never touches disk")
    synthetic = cwr.Row(
        letter="J", rid="9901", state="EXCLUDED-RULED", lineno=0,
        capability="PLANTED CONTROL ROW", reason=PLANTED_REASON,
        section="", table_key="J:0", resolved=PLANTED_REASON,
        resolution="own-cell", signals=["AF:he-holds"],
        kinds={"ACCOUNT-FACT"}, kind="ACCOUNT-FACT", source="rule",
        has_reason_cell=True, backref_donor=None, inherited_kinds=set(),
    )
    caught = offenders([synthetic])
    if len(caught) == 1 and caught[0].key == "J 9901":
        print("  ok    the planted row is convicted: contingent, no reopener")
    else:
        print(f"  CONTROL BROKEN: the verdict did not convict the planted row "
              f"(caught {[r.key for r in caught]})")
        ok = False
    # ...and the mirror case, or the rule would convict everything
    cleared = offenders([cwr.Row(
        letter="J", rid="9902", state="EXCLUDED-RULED", lineno=0,
        capability="PLANTED CONTROL ROW WITH A TRIGGER", reason="x",
        section="", table_key="J:0",
        resolved=PLANTED_REASON + " REOPENER: the account acquiring one.",
        resolution="own-cell", signals=["AF:he-holds"],
        kinds={"ACCOUNT-FACT"}, kind="ACCOUNT-FACT", source="rule",
        has_reason_cell=True, backref_donor=None, inherited_kinds=set(),
    )])
    if cleared:
        print("  CONTROL BROKEN: a row CARRYING a reopener was convicted too, so "
              "the rule is not discriminating -- it is just failing.")
        ok = False
    else:
        print("  ok    and the same row WITH a reopener is cleared, so the rule")
        print("        discriminates rather than merely refusing")

    # ---- RED 2: end to end, through the real walk over a planted corpus ----
    print("\nRED 2 -- END TO END, on a COPY of the real census with one row planted")
    real = ccs.CENSUS
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="reopener-red-"))
    try:
        for name in ccs.SLICES.values():
            shutil.copy2(real / name, tmp / name)
        target = tmp / ccs.SLICES["J"]
        lines = target.read_text(encoding="utf-8").splitlines()
        # Plant it directly beneath an existing capability row so it lands
        # INSIDE a live table rather than in prose.
        at = None
        for i, line in enumerate(lines):
            if line.startswith("| 1 |") and "|" in line[5:]:
                at = i + 1
                break
        if at is None:
            print("  CONTROL BROKEN: could not find a table row to plant beside")
            return 1
        lines.insert(at, PLANTED_ROW)
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")

        ccs.CENSUS = tmp
        cwr.ccs.CENSUS = tmp
        # The SHIPPED pipeline end to end -- walk, resolve pointers, classify,
        # apply the pinned adjudications. Reassembling a subset of it here
        # would mean the red exercised a different instrument from the green.
        rows, _wo, _dialects, _stated, _rulings, _problems, _adj = cwr.build()
        planted = [r for r in rows if r.rid == "9901"]
        if not planted:
            print("  CONTROL BROKEN: the walk did not even FIND the planted row, so")
            print("  this control proves nothing about the corpus.")
            return 1
        print(f"  ok    the walk found the planted row: {planted[0].key} "
              f"state={planted[0].state} kind={planted[0].kind}")
        failed, report = run(rows)
        if not failed:
            print("  CONTROL BROKEN: the guard PASSED a corpus containing a")
            print("  contingent write-off with no reopener. It cannot fail, so it")
            print("  certifies nothing.")
            ok = False
        else:
            named = any("J 9901" in line for line in report)
            print(f"  ok    the guard FAILED on the planted corpus")
            if named:
                print("  ok    and it named the planted row rather than failing vaguely")
            else:
                print("  CONTROL BROKEN: it failed, but never named J 9901 -- a red")
                print("  that does not say WHICH row is a red nobody can act on.")
                ok = False
    finally:
        ccs.CENSUS = real
        cwr.ccs.CENSUS = real
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- RED 3: the sentence that says the OPPOSITE must not satisfy it ----
    # This is the mutation that caught the guard's own first version green.
    print("\nRED 3 -- A CELL SAYING 'REOPENS NOTHING' MUST NOT COUNT AS A REOPENER")
    negative = ("`/edit/` family ruling; LinkedIn draws no such article for "
                "this account. **The Help-article half of this cell reopens "
                "nothing**, because the ruling excludes it either way.")
    row = cwr.Row(
        letter="P", rid="9903", state="EXCLUDED-RULED", lineno=0,
        capability="PLANTED CONTROL ROW WITH A NEGATIVE SENTENCE",
        reason=negative, section="", table_key="P:0", resolved=negative,
        resolution="own-cell", signals=["WF:help-centre"],
        kinds={"WORLD-FACT"}, kind="WORLD-FACT", source="rule",
        has_reason_cell=True, backref_donor=None, inherited_kinds=set(),
    )
    loose = cwr.REOPENER.search(negative)
    strict = REOPENER_MARKER.search(negative)
    caught3 = offenders([row])
    print(f"  the shipped case-insensitive regex matches it : "
          f"{'YES -- which is why this guard does not use it' if loose else 'no'}")
    print(f"  this guard's shouted marker matches it        : "
          f"{'YES -- CONTROL BROKEN' if strict else 'no'}")
    if len(caught3) == 1 and not strict and loose:
        print("  ok    the row is CONVICTED: a cell may not satisfy a reopener")
        print("        check with a sentence stating that nothing reopens it.")
    else:
        print("  CONTROL BROKEN: either the negative sentence was accepted as a")
        print("  reopener, or the loose regex stopped matching it and this")
        print("  control no longer exercises the defect it was written for.")
        ok = False

    print("\n" + ("ALL THREE REDS FIRED -- the guard can convict"
                  if ok else "CONTROL BROKEN -- see above"))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--demonstrate-red", action="store_true",
                    help="prove this guard can fail, on a planted row, two ways")
    ap.add_argument("--list", action="store_true",
                    help="list every contingent write-off and its reopener status")
    args = ap.parse_args(argv)

    if args.demonstrate_red:
        return demonstrate_red()

    rows, _wo, dialects, _stated, _rulings, problems, _adj = cwr.build()

    print("CONTINGENT WRITE-OFFS MUST NAME WHAT WOULD REOPEN THEM")
    print("=" * 78)
    if dialects:
        print(f"note  {len(dialects)} state cell(s) in a dialect the counter does not "
              f"speak; those rows are in neither the numerator nor the denominator.")

    if args.list:
        for r in sorted((r for r in rows if r.state in cwr.WRITEOFF and r.contingent),
                        key=lambda r: (r.letter, r.lineno)):
            mark = "R" if REOPENER_MARKER.search(r.resolved) else "-"
            print(f"  [{mark}] {r.key:<9} {r.state:<22} {r.kind:<34} {r.capability[:44]}")
        print()

    failed, report = run(rows)
    for line in report:
        print(line)
    print("\n" + ("FAILED" if failed else "PASS"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
