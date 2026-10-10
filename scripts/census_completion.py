"""What "percentage complete" means here -- computed, so it need not be remembered.

THE QUESTION THIS ANSWERS. *How much is left?* It has been answered with a
percentage nobody derived. This prints the derivation instead: the surface, the
denominator, the two different numerators that both have a claim to the word
"done", and a decomposition of what remains.

=============================================================================
THE ONE DISTINCTION EVERYTHING TURNS ON, AND IT IS NOT MINE
=============================================================================

`_audit/2026-09-19-the-read-rows.md` section 4 measured a population that read
as **61%** converting to capability at **11%**, and named the cause in one
sentence:

    The 61% headline survives only because COVERED-CANNOT-DELIVER is a
    COVERED-* state and is not a capability.

So this file reports TWO figures and never lets the larger one stand alone:

    ADJUDICATED   every state except GAP. A human reached the row and
                  recorded a verdict. It says NOTHING about whether anybody
                  can use the capability.
    DELIVERED     the row is a capability a user can exercise.

**AND DELIVERED IS PRINTED TWICE, BECAUSE TWO DEFENSIBLE LINES EXIST.** The
read-rows document draws it at PROVEN + UNFIRED -- its column is headed *"an
actual capability (PROVEN or UNFIRED)"*. A stricter reading counts only
COVERED-PROVEN, on the ground that UNFIRED means the code exists and has never
returned a payload from live LinkedIn. Both are printed with their state-sets
named. Choosing silently between them is how a headline becomes a quotation.

=============================================================================
TWO DENOMINATORS, AND SAYING WHICH ONE IS THE WHOLE POINT
=============================================================================

    PUBLISHED SURFACE   every stated row, including the ones ruled out of
                        scope. Answers "how much of everything LinkedIn
                        offers".
    ACHIEVABLE SURFACE  the published surface minus EXCLUDED-RULED and
                        MEASURED-ABSENT -- rows this repository has decided
                        it will not do, and rows the platform does not have.
                        Answers "how much of what we are willing to build".

A percentage quoted without saying which of these it divides by is not an
answer. The second is far the larger number and it is the honest one for
planning; the first is the honest one for scope.

=============================================================================
WHAT IT REFUSES TO DO
=============================================================================

**IT DOES NOT CLASSIFY BLOCKERS BY THEIR NAMES.** `scripts/
classify_surface_blockers.py` records what that costs: a five-way split of 97
blockers was published from an uncommitted classifier, and its own document
admits *"the SURFACE? class of 22 is a guess about names, not a measurement of
reasons"* -- 186,629,988,917,605 distinct subsets fit the three published
integers. Every split below is either computed by a shipped instrument or is an
ENUMERATED list of row ids taken from a named document, and each is labelled
with which.

**IT DOES NOT INVENT A SCHEDULE.** No duration appears anywhere in this file.
What remains is decomposed by WHAT WOULD UNBLOCK IT, which is a fact about the
work; how long that takes is not derivable from anything in this repository.

    python scripts/census_completion.py
    python scripts/census_completion.py --check     # fail on drift from the pins

**`--check` IS WHY THIS IS AN INSTRUMENT AND NOT A REPORT.** It pins every
headline figure and exits non-zero when one moves. Shown failing:
`scripts/_check_census_completion_can_fail.py`.
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import sys
import textwrap

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import check_jobs_directions as cjd  # noqa: E402
import check_read_addresses as cra  # noqa: E402
import count_census_states as ccs  # noqa: E402
import enumerate_gap_rows as egr  # noqa: E402
import pin_census_rows as pcr  # noqa: E402
import reader_closable_blockers as rcb  # noqa: E402
import ruling_holds as rh  # noqa: E402

#: Short spellings folded to their long form. Taken from the shipped counter's
#: own documented equivalences -- `XR` is `jobs.md`'s EXCLUDED-RULED, `CP`/`CU`
#: are its COVERED-PROVEN / COVERED-UNFIRED, `CANNOT-DELIVER` was messaging's
#: first spelling. The counter deliberately reports them UNFOLDED, so that a
#: reader can see a slice using two spellings; a completion figure must fold
#: them or it double-counts the vocabulary instead of the census.
FOLD = {
    "CP": "COVERED-PROVEN",
    "CU": "COVERED-UNFIRED",
    "CCD": "COVERED-CANNOT-DELIVER",
    "ER": "EXCLUDED-RULED",
    "XR": "EXCLUDED-RULED",
    "CANNOT-DELIVER": "COVERED-CANNOT-DELIVER",
}

#: A row in one of these states is OUT OF THE ACHIEVABLE SURFACE: this
#: repository ruled it will not do it, or measured that LinkedIn does not offer
#: it. Neither is work remaining and neither is a capability delivered.
OUT_OF_SCOPE = ("EXCLUDED-RULED", "MEASURED-ABSENT")

#: The read-rows document's line: an actual capability.
DELIVERED_BROAD = ("COVERED-PROVEN", "COVERED-UNFIRED")
#: The strict line: it has returned a payload from live LinkedIn.
DELIVERED_STRICT = ("COVERED-PROVEN",)

#: THE TWO ROWS THAT ARE NOT ONE CAPABILITY EACH, with the number of
#: capabilities each stands for and the state every one of them carries.
#: Verified against the file at HEAD rather than inherited from the counter's
#: docstring: `O6-O20` names fifteen visibility toggles (the id range
#: O6..O20 is 15, and the capability cell lists 15 items -- two independent
#: counts agreeing), and the `P-R` subsection's header declares 45 with its own
#: closing note that 44 of them are the settings family and `P1` is the 45th.
#:
#: **THE EXTRA CAPABILITIES TAKE THEIR ROW'S STATE**, and are counted in or out
#: of the achievable surface by it: `collapse()` reads each row's state off the
#: census rather than assuming it, and ASSERTS it equals the state written here
#: so that a move is reported by name. Until 2026-09-23 every one of the 58
#: extras was EXCLUDED-RULED, which is why this could be folded into a
#: percentage "by almost nothing".
#:
#: `O6-O20` HAS BEEN GAP SINCE LANE R (2026-09-23, `_audit/2026-09-23-exclusion-
#: returns.md` s4): the fifteen visibility toggles are settings pages awaiting
#: admission by name, one blocker named in the row's cell, so its 14 extras are
#: now inside the achievable surface. Re-read and re-pinned at lane R's merge,
#: 2026-09-24. `P1` stays EXCLUDED-RULED on its own named key.
#:
#: `P1` STOOD FOR 45 UNTIL 2026-09-24, and stands for one since: lane Y2
#: itemized the P-R block's settings-family 44 on the orchestrator's follow-up
#: order (`_audit/2026-09-24-lane-y2-admission.md`, "Follow-up: the P-R
#: settings block"). Of the stated 44, 22 are rows now (P2-P23), 9 were rows
#: already elsewhere, 5 are choices inside a row, 1 is named twice, and 7
#: are named nowhere or disputed. The collapse left with the count it
#: rested on.
COLLAPSED = {
    ("P", "O6-O20"): (15, "GAP"),
}

#: ENUMERATED, not inferred. Rows the corpus names as waiting on a decision no
#: engineering can substitute for. `_audit/2026-09-21-the-open-queue.md` s1
#: calls D3 *"the single highest-yield decision left in this row set"*, quoting
#: `_audit/2026-09-19-the-read-rows.md` s5.2, which listed FIVE rows by id.
#:
#: FOUR SINCE 2026-09-23: `M C83` LEFT THE LIST, and not because D3 moved. D3
#: asks whether a reasoned refusal written into the allowlist counts as an
#: EXCLUDED-RULED ground. For `M C83` the refused spelling was never seen
#: served: the shipped boundary's own newsletters entry says the row is
#: *"waiting on a LIVE READ that establishes which address serves"*, and that
#: an entry written for it today would be *"a guessed address"*. So D3 answered
#: YES could not bank it (the refusal is not about a page it has) and answered
#: NO leaves it where it is. Its real first need is the live read, which the
#: bucket-3 table records as NEEDS-SESSION and bucket 3 below counts.
#: `_audit/2026-09-23-census-cleanup.md` item 3.
#:
#: THREE SINCE THE EVENING OF 2026-09-23: `N 172` LEFT TOO, and this time a
#: ruling moved it. It was filed here for D3's other-people cause alone -- its
#: page, the people search with `connectionOf`, is admitted -- and master
#: 4a57b75 registered OTHER-MEMBER-IDS-AS-READS, which answers exactly that
#: cause for a search facet (the id from tool arguments, never from the page,
#: never stored). With D1-SEARCH-AS-READS it now needs only a reader: the
#: address table gates it READER. `_audit/2026-09-23-census-cleanup.md`
#: section 12. The other three are refused addresses, rosters and a
#: profile, which that ruling does not reach.
#:
#: EMPTY SINCE 2026-09-24: D3 IS ANSWERED. The orchestrator ruled, under the
#: operator's delegation, D3-UNREGISTERED-REFUSAL-IS-NOT-A-RULING
#: (`_audit/2026-09-24-rulings-search-verticals-rosters-passive-costs.md`): a
#: refusal written only into an allowlist comment is a question with its
#: argument recorded, not a ruling. So `N 99`, `N 177` and `N 178` wait on no
#: decision any more; they are GAP, blocked on an admission and a reader, and
#: bucket 3 counts them off the address table like every other read row.
#: MEMBER-ROSTERS-AS-BOUNDED-READS decides the roster question the first two
#: waited on; `N 178`'s live proof loads another member's profile, so the
#: operator names that member. Emptied by lane R at its merge
#: (`_audit/2026-09-23-exclusion-returns.md`, Integration 2026-09-24). The
#: dict is KEPT, empty, because bucket 2 still prints what it holds and a
#: future enumerated question belongs here.
RULING_BLOCKED_NAMED: dict[tuple[str, str], str] = {}

# `PRESS_BLOCKED_NAMED` ({N 134, P O3}, "the remaining cost is a session and
# nothing else") WAS REMOVED 2026-09-23. Both rows are GAP reads, so bucket 3
# counts them already, off a measured table: `_audit/_census/read-addresses.tsv`
# gates them PRESS-PERMITTED together with `M C72`, and its notes name what
# must be BUILT before any session helps -- a name-free shaper for the panel of
# people, a caller wiring the counter. Listing two of the three again under
# bucket 1 as session-only double-counted them and stated a premise the
# measurement does not hold. `_audit/2026-09-23-census-cleanup.md` item 1.


def walk():
    """(letter, row_id, folded_state, direction) for every stated row.

    THE LOOP IS REPLICATED AND EVERY DECISION INSIDE IT IS IMPORTED. `cells`,
    `ROW`, `HEADERS`, `state_of` come from the shipped counter, `ADMIN_ONLY`
    from the shipped enumerator and `direction_of` from the shipped direction
    finder. Only the iteration is local, and `control()` below re-runs the
    shipped enumerator and counter and refuses to report on any disagreement.

    The replication exists because `reader_closable_blockers.main()` does this
    same walk inline with no seam to import, and carving a seam out of a file
    three other waves may be editing is not worth the contention.

    The loop itself lives in `walk_cells()`, which keeps each row's cells for
    the one reader that needs them (bucket 1 reads the hold a cell cites).
    This keeps its four-tuple shape because `check_read_addresses.population`
    and the tests unpack it.
    """
    for letter, rid, state, direction, _cells in walk_cells():
        yield letter, rid, state, direction


def walk_cells():
    """`walk()`, with each row's parsed cells as a fifth element."""
    for letter, name in ccs.SLICES.items():
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
            if not st:
                continue
            yield letter, c[0], FOLD.get(st, st), rcb.direction_of(c), c


def control(rows) -> list[str]:
    """Refuse to report unless the population is BOTH self-consistent and pinned.

    TWO CHECKS THAT LOOK ALIKE AND ARE NOT, AND THE SECOND ONE WAS ADDED
    BECAUSE THE FIRST WAS SHOWN TO BE INCAPABLE OF CATCHING THE CASE THAT
    MATTERS.

    1. AGREEMENT WITH THE SHIPPED ENUMERATOR. It checks the REPLICATION -- that
       the loop in `walk()` did not drift from `enumerate_gap_rows.rows()`. It
       is worth having and it is NOT a second opinion: the two share the parse
       by design, so a defect they share is invisible to it. That is not a
       suspicion, it is written into `enumerate_gap_rows`' own docstring.

    2. AGREEMENT WITH THE PIN. `tests/census_row_pin.json` is the only record
       of the population that is NOT produced by this parse, so it is the only
       witness that can convict the parse.

    **MEASURED, NOT ARGUED.** `scripts/_check_census_completion_can_fail.py`
    demonstration C rewrites one row's state to a word outside the vocabulary.
    The row silently leaves numerator and denominator together. With only check
    1, THIS FILE PRINTED A COMPLETE AND ENTIRELY PLAUSIBLE SET OF PERCENTAGES
    OVER 703 ROWS and reported the census as one row smaller -- the exact
    disease it was written to expose, in its own output. Check 2 turns that
    into a refusal.

    A REFUSAL, NEVER A FOOTNOTE. Every percentage over a drifted denominator
    still looks reasonable, so printing them with a warning above would be the
    worst available behaviour: the numbers would be quoted and the warning
    would not.
    """
    problems: list[str] = []
    dialects: list[str] = []
    shipped = collections.Counter(
        (letter, rid) for letter, rid, *_ in egr.rows(dialects=dialects))
    if dialects:
        problems.append(
            f"{len(dialects)} state cell(s) are spelled in a dialect the "
            f"shipped vocabulary does not hold; every figure below would be "
            f"short by that many rows:\n    " + "\n    ".join(dialects))
    mine = collections.Counter((letter, rid) for letter, rid, *_ in rows)
    if mine != shipped:
        missing = sorted(set(shipped) - set(mine))
        extra = sorted(set(mine) - set(shipped))
        problems.append(
            f"this walk disagrees with `enumerate_gap_rows.rows()` -- "
            f"{len(missing)} row(s) it sees and this does not {missing[:8]}, "
            f"{len(extra)} the other way {extra[:8]}")

    pinned = pcr.load()
    if not pinned:
        problems.append(
            f"the census row population is UNPINNED ({pcr.PIN} is missing or "
            f"empty), so nothing independent of this parse can confirm the "
            f"denominator. Run `python scripts/pin_census_rows.py --write`.")
    else:
        added, removed = pcr.delta(pinned, mine)
        if added or removed:
            problems.append(
                f"THE POPULATION HAS DRIFTED OFF ITS PIN: "
                f"{len(added)} added, {len(removed)} removed "
                f"(pinned {sum(pinned.values())}, live {sum(mine.values())}). "
                f"Every percentage this file would print divides by a "
                f"denominator nobody has agreed to.\n"
                + pcr.describe(added, removed))
    return problems


def tally(rows):
    folded = collections.Counter(st for _l, _r, st, _d in rows)
    return folded


def collapse(rows) -> tuple[int, int, list[str]]:
    """(extra capabilities beyond the row count, how many of those are out of
    scope by their row's state, problems).

    ASSERTS the state of every collapsed row instead of trusting `COLLAPSED`.
    If one of them is ever re-adjudicated -- and `O23` in the same section is
    already GAP, so the settings family is not uniformly closed -- the claim
    that the collapse is entirely out of scope stops being true, and this must
    say so rather than keep printing a figure built on it.
    """
    state = {(l, r): st for l, r, st, _d in rows}
    extra, extra_out, problems = 0, 0, []
    for key, (n, want) in COLLAPSED.items():
        got = state.get(key)
        if got is None:
            problems.append(
                f"collapsed row {key[0]} {key[1]} is no longer in the census, "
                f"so the capability denominator cannot be derived")
            continue
        if got != want:
            problems.append(
                f"collapsed row {key[0]} {key[1]} is {got}, not {want}. It "
                f"stands for {n} capabilities, so {n - 1} capabilities just "
                f"moved into or out of the achievable surface in one edit and "
                f"no row count can show it. RE-READ THE SECTION before "
                f"quoting any figure here.")
        extra += n - 1
        if got in OUT_OF_SCOPE:
            extra_out += n - 1
    return extra, extra_out, problems


def pct(n: int, d: int) -> str:
    return "  n/a" if not d else f"{100.0 * n / d:5.1f}%"


def _row_order(row: str) -> tuple:
    """"P A11" after "P A8": slice, the id's letters, its digits as a number."""
    letter, _sep, rid = row.partition(" ")
    digits = "".join(ch for ch in rid if ch.isdigit())
    return (letter, rid.rstrip("0123456789"), int(digits) if digits else 0, rid)


def _wrap(p, rows_held: list[str], indent: int = 9, width: int = 76) -> None:
    """Print row ids comma-separated, wrapped, so every member is on the page."""
    line = ""
    for row in rows_held:
        piece = row if not line else f", {row}"
        if line and indent + len(line) + len(piece) > width:
            p(" " * indent + line + ",")
            line = row
        else:
            line += piece
    if line:
        p(" " * indent + line)


def bucket3_split(rows) -> tuple[dict[str, int] | None, list[str]]:
    """(the measured split of bucket 3, problems) off the address table.

    COUNTED, NOT RE-DRIVEN. The verdicts in `_audit/_census/read-addresses.tsv`
    were measured through the shipped `readonly.is_read_url`, and
    `scripts/check_read_addresses.py` re-drives every one of them; this file
    counts the table's class and gate columns and does NOT import the boundary,
    because `scripts/_check_census_completion_can_fail.py` runs it inside a
    copy of the tree that carries no `linkedin_server` package.

    WHAT IT DOES CHECK, and it is the half that needs no boundary: that the
    table covers EXACTLY today's bucket 3, one line per row, directions
    agreeing, vocabulary intact. A split over a table that has drifted from
    the census would be a figure about a population nobody has, so on any
    problem the split is WITHHELD -- its figures are missing, and `--check`
    fails naming every pin that has nothing to check.
    """
    pop = {(letter, rid): d for letter, rid, st, d in rows
           if st == "GAP" and d in cra.DIRECTIONS}
    table, problems = cra.load()
    problems += cra.coverage_problems(table, pop)
    problems += cra.shape_problems(table)
    # And no row blocked on nothing where a ruling holds its page: the edge
    # the split first shipped without, which let `M M49` count as blocked on
    # nothing on a messaging page (`_audit/2026-09-23-census-cleanup.md` item
    # 6). Pure -- it reads the holds table, never the register.
    problems += cra.ruling_problems(table)
    if problems:
        return None, problems
    return cra.split(table), []


#: The name the rows no ruling holds are counted under. NOT a hold id -- the
#: absence of one -- and spelled with a space, which no id the HELD BY marker
#: can read carries, so it can never collide with one.
NO_RULING = "NO RULING"


def bucket1_holds(rows, texts: dict | None = None):
    """({"L id": hold id or None} for every COVERED-UNFIRED row, problems).

    DERIVED FROM THE CENSUS, NEVER TYPED HERE -- `ruling_holds.hold_of` reads
    the row's R/W cell and the hold its own cell cites, and says why for every
    rule it applies. `texts` maps (letter, row id) to the row's cells joined
    and defaults to a fresh read of the census; it is a parameter so a control
    can plant a cell without writing one.

    WITHHELD, NEVER GUESSED. A row whose hold cannot be read -- an id this
    census does not know, a read row citing the write ruling, an R+W row --
    withholds the whole split, as bucket 3's does, so each `b1_` pin reports
    nothing to check rather than a figure somebody would quote.
    """
    unfired = [(letter, rid, d) for letter, rid, st, d in rows
               if st == "COVERED-UNFIRED"]
    if texts is None:
        texts = {(letter, rid): " | ".join(c)
                 for letter, rid, st, _d, c in walk_cells()
                 if st == "COVERED-UNFIRED"}
    holds: dict[str, str | None] = {}
    problems: list[str] = []
    for letter, rid, direction in unfired:
        text = texts.get((letter, rid))
        if text is None:
            problems.append(f"{letter} {rid}: COVERED-UNFIRED, and no cells were "
                            f"read for it")
            continue
        hold, row_problems = rh.hold_of(direction, text)
        problems += [f"{letter} {rid}: {p}" for p in row_problems]
        holds[f"{letter} {rid}"] = hold
    if problems:
        return None, problems
    return holds, []


def bucket1_moves(holds: dict) -> list[str]:
    """Every COVERED-UNFIRED row whose hold differs from `PINNED_B1_ROWS`.

    THE COUNT PINS CANNOT DO THIS. Two rows swapping holds leave every count
    where it was; a row entering the state as another leaves it moves nothing
    either. This compares ROW BY ROW and names each row: entered, left, or
    moved from one hold to another.
    """
    pinned = {row: hold for hold, members in PINNED_B1_ROWS.items()
              for row in members}
    live = {row: (hold or NO_RULING) for row, hold in holds.items()}
    out: list[str] = []
    for row in sorted(set(live) - set(pinned)):
        out.append(f"{row}: ENTERED COVERED-UNFIRED, held by {live[row]} -- "
                   f"not pinned")
    for row in sorted(set(pinned) - set(live)):
        out.append(f"{row}: LEFT COVERED-UNFIRED (pinned as held by "
                   f"{pinned[row]})")
    for row in sorted(set(live) & set(pinned)):
        if live[row] != pinned[row]:
            out.append(f"{row}: pinned as held by {pinned[row]}, now held by "
                       f"{live[row]}")
    return out


def report(rows, out) -> dict:
    """Print the decomposition and return the headline figures as a dict."""
    folded = tally(rows)
    total = sum(folded.values())
    gap = folded["GAP"]
    proven = folded["COVERED-PROVEN"]
    unfired = folded["COVERED-UNFIRED"]
    cannot = folded["COVERED-CANNOT-DELIVER"]
    out_of_scope = sum(folded[s] for s in OUT_OF_SCOPE)
    achievable = total - out_of_scope
    adjudicated = total - gap
    broad = sum(folded[s] for s in DELIVERED_BROAD)
    strict = sum(folded[s] for s in DELIVERED_STRICT)

    p = out.append
    p("=" * 78)
    p("1. THE SURFACE, AND WHAT IT IS A SURFACE OF")
    p("=" * 78)
    p("The four capability slices under `_audit/_census/`. Row counts are the")
    p("shipped counter's; nothing here is quoted from a document.")
    p("")
    per_slice = collections.Counter(letter for letter, *_ in rows)
    for letter in sorted(ccs.SLICES):
        p(f"    {letter}  {ccs.SLICES[letter]:30s} {per_slice[letter]:4d} rows")
    p(f"       {'':30s} {'':4s} ----")
    p(f"       {'stated rows, all four slices':30s} {total:4d}")
    p("")
    p("  `_audit/_census/mcp-inventory.md` is a FIFTH file in that directory and")
    p("  is NOT counted above. It runs a different state vocabulary")
    p("  (PROVEN-LIVE / TESTED-ONLY / KNOWN-BROKEN) over a different")
    p("  population -- tools, not capabilities -- and the shipped counter")
    p("  excludes it by name. Adding it would sum two different things.")
    p("")
    p("=" * 78)
    p("2. THE DENOMINATOR")
    p("=" * 78)
    p(f"    PUBLISHED SURFACE   {total:4d}   every stated row")
    p(f"    out of scope        {out_of_scope:4d}   EXCLUDED-RULED {folded['EXCLUDED-RULED']}"
      f" + MEASURED-ABSENT {folded['MEASURED-ABSENT']}")
    p(f"    ACHIEVABLE SURFACE  {achievable:4d}   what is left to be built or ruled")
    p("")
    p("  ROWS ARE NOT CAPABILITIES. `profile.md` collapses one block into a")
    p("  single row, so the CAPABILITY total is larger than the row total:")
    p("")
    extra, extra_out, collapse_problems = collapse(rows)
    for key, (n, _want) in sorted(COLLAPSED.items()):
        p(f"    {key[0]} {key[1]:8s} stands for {n:3d} capabilities in 1 row"
          f"   (+{n - 1})")
    cap_total = total + extra
    cap_out = out_of_scope + extra_out
    cap_achievable = cap_total - cap_out
    p(f"    {'':12s} {'':12s} collapse bonus        +{extra}")
    p(f"    CAPABILITIES, published surface   {cap_total:4d}   computed at HEAD")
    p("")
    p("  THREE CAPABILITY TOTALS CIRCULATE AND THIS FILE CORRECTS NONE OF THEM.")
    p(f"    {cap_total}   stated rows + declared collapses, computed above")
    p("    761   published, and quoted as the denominator under every coverage")
    p("          ratio in this campaign. It has never reconciled with its own")
    p("          stated terms: `_audit/2026-09-19-cross-slice-rulings.md`")
    p("          measured that `705 + 59 - 2` evaluates to 762, not 761.")
    p("    760   the shipped counter's docstring, which keeps a `- 2 stateless`")
    p("          term. THE TWO STATELESS ROWS ARE `J 58` AND `M C53`, AND")
    p("          NEITHER IS INSIDE THE 704 -- they carry no state, so the")
    p("          counter never counted them. Subtracting them removes them a")
    p("          second time.")
    p("")
    p("  THE P-R BLOCK IS ITEMIZED, 2026-09-24. Its settings-family 44 were")
    p("  prose bullets carrying no row ids, counted as a +44 collapse on `P1`.")
    p("  Itemized at the grain LinkedIn draws, 22 are rows now (P2-P23), 9")
    p("  were rows already elsewhere -- so the +44 DID double-count, which")
    p("  this paragraph said until then it could not -- 5 are choices inside")
    p("  a row, 1 is named twice, and 7 are named nowhere or disputed. The")
    p("  capability total falls by 22 with it; the rows are counted as rows.")
    p("  The unexplained term in the 761 is still the `- 2`.")
    p("  Reported, not corrected: this denominator's owner is the counter's,")
    p("  and moving it silently is how the 761 became unreproducible.")
    if collapse_problems:
        for problem in collapse_problems:
            p(f"    !! {problem}")
    p("")
    p(f"  {extra_out} OF THE {extra} COLLAPSED CAPABILITIES ARE OUT OF SCOPE BY"
      f" THEIR ROW'S")
    p("  STATE, read off the census and asserted above, so they leave the")
    p("  achievable surface the moment they enter it; the other"
      f" {extra - extra_out} are inside it")
    p("  (`P O6-O20`, GAP since 2026-09-23). The capability reading of the")
    p("  achievable surface is printed beside the row reading:")
    p("")
    p(f"    delivered / published surface    rows {pct(broad, total)}"
      f"   capabilities {pct(broad, cap_total)}")
    p(f"    delivered / achievable surface   rows {pct(broad, achievable)}"
      f"   capabilities {pct(broad, cap_achievable)}")
    p("")
    p("  So the figures below divide by ROWS, and the capability reading is")
    p("  printed beside them wherever it would differ.")
    p("")
    p("=" * 78)
    p("3. ADJUDICATED IS NOT DELIVERED")
    p("=" * 78)
    p("  Each figure names the state-set that defines it. The larger one never")
    p("  stands alone -- that is the whole finding of")
    p("  `_audit/2026-09-19-the-read-rows.md` section 4.")
    p("")
    p(f"    ADJUDICATED        {adjudicated:4d} / {total:4d}  {pct(adjudicated, total)}"
      f"   everything except GAP")
    p(f"    DELIVERED, broad   {broad:4d} / {total:4d}  {pct(broad, total)}"
      f"   COVERED-PROVEN + COVERED-UNFIRED")
    p(f"    DELIVERED, strict  {strict:4d} / {total:4d}  {pct(strict, total)}"
      f"   COVERED-PROVEN only")
    p("")
    p("  Against the ACHIEVABLE surface instead, which is the number to plan on:")
    p("")
    p(f"    DELIVERED, broad   {broad:4d} / {achievable:4d}  {pct(broad, achievable)}")
    p(f"    DELIVERED, strict  {strict:4d} / {achievable:4d}  {pct(strict, achievable)}")
    p("")
    p("  THE GAP BETWEEN THE FIRST LINE AND THE OTHER TWO IS THE ENTIRE POINT.")
    p(f"  {adjudicated} rows carry a verdict. {broad} of them are a capability anybody can")
    p(f"  use. The difference is {adjudicated - broad} rows that were REASONED ABOUT and")
    p("  then ruled out, measured absent, or found undeliverable -- real work,")
    p("  and not one unit of it is a thing the server can do.")
    p("")
    p("=" * 78)
    p("4. WHAT REMAINS, DECOMPOSED BY WHAT WOULD UNBLOCK IT")
    p("=" * 78)
    not_delivered = total - broad - out_of_scope
    p(f"  NOT DELIVERED (achievable surface minus delivered-broad): {not_delivered}")
    p(f"    GAP                       {gap:4d}   no verdict yet")
    p(f"    COVERED-CANNOT-DELIVER    {cannot:4d}   a tool fired and cannot do it")
    p("")
    gap_rows = [(l, r, d) for l, r, st, d in rows if st == "GAP"]
    by_dir = collections.Counter(d for _l, _r, d in gap_rows)
    reader = by_dir["R"] + by_dir["R+W"]
    p("  -- BUCKET 1: COVERED, NEVER FIRED -- AND WHAT HOLDS EACH ROW ------")
    p(f"     COVERED-UNFIRED                         {unfired:4d}   DERIVED from the state")
    p("       The code exists and has never returned a payload from live")
    p("       LinkedIn. THE STATE SAYS NOTHING ABOUT WHY. Until 2026-09-23 this")
    p("       bucket said a session was the entire remaining cost; measured row")
    p("       by row that day, a session was the whole cost for none of them")
    p("       (`_audit/2026-09-23-bucket1-fires.md` section 3). So what holds each")
    p("       row is DERIVED here from the census and never typed: a W row by its")
    p("       R/W cell, any other row by the hold its own cell cites as HELD BY.")
    p("       `scripts/ruling_holds.py` resolves every cited id; this file only")
    p("       counts them. THE RULINGS MOVED THE SAME DAY: the operator's ruling")
    p("       (b) at 18:15 (`WRITE-CLASS-B`) lifted the messaging ruling and the")
    p("       read-only rule, and every write now fires only at a target he")
    p("       names (`OPERATOR-NAMES-THE-TARGET`). The orchestrator's delegated")
    p("       calls of the same day put his own inbox reads under (b),")
    p("       answered the notifications question, and took edits to his own")
    p("       profile fields out of the write hold")
    p("       (`SELF-PROFILE-EDITS-NOT-OUTWARD`, cited as RELEASED BY). All")
    p("       registered.")
    holds, b1_problems = bucket1_holds(rows)
    split1 = None
    released1 = 0
    if holds is None:
        p("     BUCKET 1 SPLIT WITHHELD -- a row's hold cannot be read, so any")
        p("     split would count a guess:")
        for problem in b1_problems[:12]:
            p(f"       !! {problem}")
        if len(b1_problems) > 12:
            p(f"       !! ... and {len(b1_problems) - 12} more")
    else:
        direction = {f"{l} {r}": d for l, r, _st, d in rows}
        members: dict[str, list[str]] = collections.defaultdict(list)
        for row, hold in holds.items():
            members[hold or NO_RULING].append(row)
        split1 = {"standing": 0, "relayed": 0, "pending": 0, "none": 0}
        headings = (
            ("STANDING", "standing",
             "held by a STANDING ruling -- made, registered, in force:"),
            ("RELAYED", "relayed",
             "held by a RELAYED ruling -- made, not yet in the register:"),
            ("PENDING", "pending",
             "waiting on a PENDING question to the operator -- NOT a ruling:"),
        )
        for status, key, heading in headings:
            p(f"     {heading}")
            ids = [i for i, h in rh.ROW_HOLDS.items() if h.status == status]
            if not ids:
                p("       none")
            for hold_id in ids:
                hold = rh.ROW_HOLDS[hold_id]
                rows_held = sorted(members.get(hold_id, []), key=_row_order)
                split1[key] += len(rows_held)
                how = "DERIVED  cited"
                if hold.binds == "write":
                    by_cell = sum(1 for r in rows_held
                                  if direction.get(r) == "W")
                    how = (f"DERIVED  W {by_cell} by the R/W cell, "
                           f"{len(rows_held) - by_cell} cited")
                p(f"       {hold_id:37s} {len(rows_held):4d}   {how}")
                p(f"         {hold.gist}")
                _wrap(p, rows_held)
        free = sorted(members.get(NO_RULING, []), key=_row_order)
        split1["none"] = len(free)
        p(f"     {'held by NO ruling -- the cell says what':39s} "
          f"{len(free):4d}   DERIVED")
        p("       remains for each: a press, a build, or a session")
        _wrap(p, free)
        # A W row can only be held by nothing when its own cell cites a
        # release, so the released rows are exactly the W rows in this group.
        released = [r for r in free if direction.get(r) == "W"]
        released1 = len(released)
        if released:
            p(f"       of which WRITES RELEASED by a registered ruling    "
              f"{released1:4d}   DERIVED  cited")
            for release_id, release in rh.ROW_RELEASES.items():
                p(f"         {release_id}")
                for piece in textwrap.wrap(release.gist, 64):
                    p(f"           {piece}")
            _wrap(p, released, indent=11)
        total1 = sum(split1.values())
        p(f"     CHECK: {split1['standing']} + {split1['relayed']} + "
          f"{split1['pending']} + {split1['none']} = {total1}, and "
          f"COVERED-UNFIRED is {unfired}")
        p("     LIFTED, and cited by no row as a hold (a stale citation withholds")
        p("     this split):")
        for hold_id, entry in rh.LIFTED_ROW_HOLDS.items():
            p(f"       {hold_id}  (the register says {entry.register_status})")
            for piece in textwrap.wrap(entry.why, 66):
                p(f"         {piece}")
    p("")
    p("  -- BUCKET 2: BLOCKED ON AN OPERATOR RULING -----------------------")
    named_ruling = [k for k in RULING_BLOCKED_NAMED
                    if any((l, r) == k and st == "GAP" for l, r, st, _d in rows)]
    p(f"     one undecided question (D3)             {len(named_ruling):4d}   ENUMERATED"
      f" {sorted(named_ruling)}")
    p(f"     write-direction still-GAP rows          {by_dir['W']:4d}   DERIVED from the"
      f" census R/W cell")
    # Counted, not assumed: a still-GAP write leaves the target condition only
    # the way a bucket-1 write does, by citing a release in its own cell.
    released_gap = sum(
        1 for _l, _r, st, d, cells in walk_cells()
        if st == "GAP" and d == "W"
        and rh.cited(" | ".join(cells), rh.RELEASED_BY_MARKER))
    p("       Governed until 18:15 on 2026-09-23 by `NO-IRREVERSIBLE-WRITE-IS-FIRED`,")
    p("       and since then by the operator's ruling (b), `WRITE-CLASS-B`, with")
    p("       `OPERATOR-NAMES-THE-TARGET`: an outward write may be designed, gated")
    p("       and left ready, and fired only at a target HE names. So the last")
    p("       step of each OUTWARD one is his decision, whatever is built first.")
    p("       Edits to his own profile fields are not outward")
    p("       (`SELF-PROFILE-EDITS-NOT-OUTWARD`), and which of these rows are such")
    p("       edits is NOT counted here: a row says so only by citing the release")
    p(f"       in its own cell, and {released_gap} still-GAP write row(s) do. This is a")
    p("       CEILING on the bucket, not a claim that each row is otherwise")
    p("       ready -- most are not.")
    p("")
    p("  -- BUCKET 3: BLOCKED ON NOTHING AT ALL ---------------------------")
    p("     THE ONLY BUCKET WHOSE SIZE IS A STATEMENT ABOUT WORK.")
    p(f"     read-direction still-GAP rows           {reader:4d}   DERIVED"
      f"  (R {by_dir['R']} + R+W {by_dir['R+W']})")
    p("       That is the UPPER BOUND: the set a reader could close in")
    p("       principle. EACH ROW'S PAGE ADDRESS IS NOW MEASURED through the")
    p("       shipped read boundary -- `_audit/_census/read-addresses.tsv`, one")
    p("       line per row, re-driven by `scripts/check_read_addresses.py`.")
    p("       Counted off that table; this file does not re-drive it:")
    split3, split3_problems = bucket3_split(rows)
    if split3 is None:
        p("     BUCKET 3 SPLIT WITHHELD -- the address table no longer covers")
        p("     today's bucket 3, so any split of it would describe a")
        p("     population the census does not have:")
        for problem in split3_problems[:12]:
            p(f"       !! {problem}")
        if len(split3_problems) > 12:
            p(f"       !! ... and {len(split3_problems) - 12} more; run "
              f"`scripts/check_read_addresses.py`")
    else:
        refused_why = (f"forbidden substring {split3['refused:forbidden']}, "
                       f"allowlist silence {split3['refused:no_pattern']}")
        p(f"     the boundary ADMITS the row's page      "
          f"{split3['class:ADMITTED']:4d}   MEASURED")
        p(f"     the boundary REFUSES it                 "
          f"{split3['class:REFUSED']:4d}   MEASURED  ({refused_why})")
        p(f"     NO-ADDRESS: no page of its own          "
          f"{split3['class:NO-ADDRESS']:4d}   ENUMERATED, each row says what"
          f" it derives from")
        p(f"     NEEDS-SESSION: address unknown offline  "
          f"{split3['class:NEEDS-SESSION']:4d}   ENUMERATED, each row says what"
          f" is unknown")
        p(f"     UNDETERMINED                            "
          f"{split3['class:UNDETERMINED']:4d}   ENUMERATED, reason per row")
        p(f"     of the {split3['class:ADMITTED']} ADMITTED, the first thing past the"
          f" boundary -- ENUMERATED in the")
        p("     table's gate column, a judgement that names its source per row:")
        labels = {
            "READER": "a reader over the admitted page",
            "PRESS-PERMITTED": "a press the shipped gate permits",
            "MEASURE": "a live measurement first",
            "BUILT-UNFIRED": "the reader ships, never fired",
            "PRESS": "a press the shipped gate refuses",
            "RULING": "a decision nobody has made",
            "STANDING-RULING": "a ruling made holds the page",
        }
        for gate in cra.GATES:
            p(f"       {gate:16s} {labels[gate]:34s} {split3['gate:' + gate]:4d}")
        p(f"     BLOCKED ON NOTHING, MEASURED            "
          f"{split3['blocked_on_nothing']:4d}   of {reader}: ADMITTED, and a"
          f" reader could be")
        p("       written today -- no ruling made or pending holds the page, no")
        p("       boundary edit, no refused press. Read off the table's gate")
        p("       column; that no ruling holds their pages is checked on every")
        p("       run against `scripts/ruling_holds.py`, since 2026-09-23:")
        # LISTED, not pointed at. This line used to send the reader to the
        # bucket-3 audit, which names the five of its own day; the table has
        # moved since and a pointer cannot say so.
        table3, _problems3 = cra.load()
        _wrap(p, sorted((f"{r['slice']} {r['row']}" for r in table3
                         if r["class"] == "ADMITTED"
                         and r["gate"] in cra.BLOCKED_ON_NOTHING),
                        key=_row_order))
    p(f"     of those {reader}, named elsewhere here as needing a ruling"
      f"    "
      f"{len([k for k in named_ruling if any((l, r) == k and d in ('R', 'R+W') for l, r, _s, d in rows)]):4d}")
    p("")
    p("  -- JOBS: DIRECTION BY SIDE TABLE, NOT BY CENSUS CELL ----------")
    p(f"     direction unknown in the census cell    {by_dir['unknown']:4d}")
    p(f"     direction ambiguous                     {by_dir['ambiguous']:4d}")
    p("       `jobs.md` has no per-row R/W column, by the argument of")
    p("       `_audit/2026-09-21-the-jobs-direction.md` section 8; the")
    p("       per-row reading lives in `_audit/_census/jobs-directions.tsv`,")
    p("       checked by `scripts/check_jobs_directions.py`:")
    # WITHHELD RATHER THAN ZEROED, as bucket 3: a jobs table that has
    # drifted from the census returns None and each `jobs_` pin reports
    # nothing to check. Pure -- no boundary import, so the can-fail copy runs.
    jobs, jobs_problems = cjd.census_figures(rows)
    for line in cjd.report_lines(jobs, jobs_problems):
        p(line)
    p("")
    p(f"     CHECK: {by_dir['R']} + {by_dir['R+W']} + {by_dir['W']} + "
      f"{by_dir['unknown']} + {by_dir['ambiguous']} = "
      f"{sum(by_dir.values())}, and still-GAP is {gap}")
    p("")
    p("=" * 78)
    p("5. WHAT THIS INSTRUMENT CANNOT SAY")
    p("=" * 78)
    p("  * HOW LONG. Nothing here measures duration and nothing should be read")
    p("    as a schedule.")
    p("  * WHETHER BUCKET 3 IS BLOCKED ON NOTHING BEYOND THE BOUNDARY. What is")
    p("    measured since 2026-09-23 is the per-row ADDRESS through")
    p("    `readonly.is_read_url` -- the census kept it in prose, and")
    p("    `_audit/_census/read-addresses.tsv` is now the column, re-driven by")
    p("    `scripts/check_read_addresses.py`. That settles whether the page is")
    p("    one this server may OPEN, and nothing more: ALLOWED IS NOT SERVED,")
    p("    so an admitted address is not evidence that the page draws what the")
    p("    row wants, and the gate column past the boundary is a judgement")
    p("    enumerated from committed sources rather than a measurement. One")
    p("    part of that judgement IS checked, since 2026-09-23: no row may be")
    p("    blocked on nothing on a page a ruling holds -- the holds that bind a")
    p("    SURFACE, in `scripts/ruling_holds.py`. A hold that binds an ACT,")
    p("    such as the one on every write, cannot be read off an address, so a")
    p("    row it holds must say so in its note and no instrument checks that.")
    if split3 is not None:
        unaddressed = (split3["class:NO-ADDRESS"]
                       + split3["class:NEEDS-SESSION"]
                       + split3["class:UNDETERMINED"])
        p(f"    {unaddressed} of the {split3['rows']} rows carry no address at all"
          f" (NO-ADDRESS {split3['class:NO-ADDRESS']},")
        p(f"    NEEDS-SESSION {split3['class:NEEDS-SESSION']}, UNDETERMINED"
          f" {split3['class:UNDETERMINED']}); for those the boundary question")
        p("    itself is still open, and each row says why.")
    p("  * WHETHER A ROW IS THE RIGHT ROW. Every count here is over the census")
    p("    as written. If a capability is missing from the census entirely, it")
    p("    is missing from every figure above, and no instrument in this")
    p("    repository can find what nobody enumerated.")

    figures = {
        "stated_rows": total,
        "capabilities": cap_total,
        "capabilities_achievable": cap_achievable,
        "out_of_scope": out_of_scope,
        "achievable": achievable,
        "adjudicated": adjudicated,
        "delivered_broad": broad,
        "delivered_strict": strict,
        "gap": gap,
        "cannot_deliver": cannot,
        "unfired": unfired,
        "gap_read": reader,
        "gap_write": by_dir["W"],
        "gap_unknown": by_dir["unknown"],
        "gap_ambiguous": by_dir["ambiguous"],
        "b2_d3_rows": len(named_ruling),
    }
    # WITHHELD RATHER THAN ZEROED, for the same reason as bucket 3 below: a
    # hold that cannot be read would otherwise count as a zero somewhere.
    if split1 is not None:
        figures.update({
            "b1_standing": split1["standing"],
            "b1_relayed": split1["relayed"],
            "b1_pending": split1["pending"],
            "b1_no_ruling": split1["none"],
            "b1_released": released1,
        })
    # WITHHELD RATHER THAN ZEROED. When the address table does not cover
    # today's bucket 3 these keys are simply absent, so `--check` reports each
    # of their pins as having nothing to check -- a zero here would read as a
    # measurement.
    if split3 is not None:
        figures.update({
            "b3_admitted": split3["class:ADMITTED"],
            "b3_refused": split3["class:REFUSED"],
            "b3_no_address": split3["class:NO-ADDRESS"],
            "b3_needs_session": split3["class:NEEDS-SESSION"],
            "b3_undetermined": split3["class:UNDETERMINED"],
            "b3_blocked_on_nothing": split3["blocked_on_nothing"],
        })
    # THE JOBS SLICE, BY SIDE TABLE -- withheld, never zeroed, when
    # `_audit/_census/jobs-directions.tsv` has drifted from the census.
    if jobs is not None:
        figures.update(jobs)
    return figures


#: EVERY headline figure this file prints, pinned. `--check` fails on any
#: movement and NAMES it. This is what makes the file an instrument rather than
#: a report: a report that cannot disagree with the tree certifies nothing.
#: Re-pin only alongside a statement of what moved the census.
PINNED = {
    #: RE-DERIVED AT LANE R'S MERGE, 2026-09-24, from the merged tree and not
    #: from any forecast (`_audit/2026-09-23-exclusion-returns.md`, its
    #: Integration 2026-09-24 section, holds the whole list). Lane R returned
    #: 245 exclusions to GAP with each blocker named in its row's cell, kept 59
    #: on the census's written grounds, and rulings batch 3 then filed `N 171`
    #: EXCLUDED-RULED as NOT-AN-ACT on D5-PASSIVE-COST-IS-NOT-A-ROW. So:
    #:   out_of_scope   315 ->  70   (-246: 245 returned to GAP and `N 23` to
    #:                               COVERED-UNFIRED; +1: `N 171`)
    #:   achievable     389 -> 634   gap 270 -> 514, adjudicated 434 -> 190
    #:   gap_read        66 ->  98   gap_write 150 -> 324, gap_unknown 54 -> 92
    #:   unfired         25 ->  26   and delivered_broad 100 -> 101: `N 23`,
    #:                               returned to COVERED-UNFIRED, not to GAP
    #:   capabilities_achievable 389 -> 648: 634 rows plus `P O6-O20`'s 14
    #:                               extra, GAP since lane R (see COLLAPSED)
    #: A GAP count that grows here is not work that appeared; it is work that
    #: was always there and was filed out of scope without one of the census's
    #: four written grounds.
    #:
    #: RE-DERIVED AT LANE L7'S MERGE, 2026-09-24, from the tree merged with
    #: master ff98a7f, MEASURED there and not added as deltas
    #: (`_audit/2026-09-24-lane-l7-profile-writes.md`, Integration 2026-09-24).
    #: Lane L7 built `P I14` (`linkedin_mark_company_interest`, a WRITE, behind
    #: the flag and the single-use grant, never fired): GAP -> COVERED-UNFIRED.
    #: A W row, so it enters bucket 1 held by OPERATOR-NAMES-THE-TARGET with no
    #: marker, and leaves the write-direction GAP count. So:
    #:   adjudicated 194 -> 195, delivered_broad 105 -> 106, unfired 30 -> 31
    #:   gap 510 -> 509, gap_write 324 -> 323, b1_standing 10 -> 11
    #: The same lane's other 35 rows kept their states, and its six intro-
    #: editor notes and `P G3`'s named ruling moved no figure.
    #: AND RE-DERIVED AGAIN AT THE LANE'S MERGE OF MASTER 9b9a4d0, which had
    #: meanwhile taken the live lane's four proven rows (below): measured on
    #: that merged tree, `P I14` is the only move against master's pins --
    #:   adjudicated 197 -> 198, delivered_broad 108 -> 109, unfired 29 -> 30,
    #:   gap 507 -> 506; gap_write 323 and b1_standing 11 as this branch had
    #:   them, because the live lane's rows were reads.
    #:
    #: RE-DERIVED AT LANE S'S MERGE, 2026-09-24, from the tree merged with
    #: master d65759f and not as deltas from the lane's base
    #: (`_audit/2026-09-24-lane-s-people-search.md`, Integration 2026-09-24).
    #: Lane S built the people-search readers for seven rows, and the WHO
    #: rule (the orchestrator's census call, 03:20) kept only the four FILTER
    #: rows delivered: `N 84`, `N 85`, `N 87`, `N 94` GAP -> COVERED-UNFIRED.
    #: `N 79`, `N 172` and `N 194` stay GAP -- their payload is WHO and the
    #: reader publishes counts -- re-gated RULING in the address table. So:
    #:   adjudicated 190 -> 194, delivered_broad 101 -> 105, unfired 26 -> 30
    #:   gap 514 -> 510, gap_read 98 -> 94, b3_admitted 44 -> 40
    #:   b3_blocked_on_nothing 9 -> 2 (four left bucket 3, three re-gated)
    #:   b1_no_ruling 16 -> 20 (the four enter bucket 1, held by no ruling)
    #:
    #: RE-DERIVED AT LANE Y2'S INTEGRATION, 2026-09-24, on the tree merged
    #: with master four times as it moved (ff98a7f, the live lane's d9ec640,
    #: the rulings at 9b9a4d0, lane L7's 603f4d3), never as deltas from the
    #: lane's base (`_audit/2026-09-24-lane-y2-admission.md`, Integration
    #: 2026-09-24). Lane Y2 admitted 43 capability rows LinkedIn draws that no
    #: row carried, all at GAP; on the orchestrator's delegated call `J 158`
    #: then moved GAP -> COVERED-UNFIRED (a shipped tool reaches it, its call
    #: at that index never fired). Under WHO-WHICH-COUNTS-ARE-NOT-DELIVERY ten
    #: of the 43 stay GAP on the doctrine and `N 195` does not: its third part
    #: is an aggregate. Against lane L7's figures (master 603f4d3):
    #:   stated_rows 704 -> 747, capabilities 762 -> 805,
    #:   capabilities_achievable 648 -> 691, achievable 634 -> 677 (+43)
    #:   gap 506 -> 548 (+43 admitted, -1 `J 158`); adjudicated 198 -> 199,
    #:   delivered_broad 109 -> 110, unfired 30 -> 31 (`J 158`) -- the three
    #:   git merged as ONE change, because lane L7's `P I14` moved them by the
    #:   same one: two rows moved them, the tree holds both
    #:   gap_read 91 -> 104 (+13), gap_write 323 -> 337 (+14),
    #:   gap_unknown 92 -> 107 (+16 jobs rows, -1 `J 158`)
    #:   b3_admitted 37 -> 42, b3_refused 38 -> 46,
    #:   b3_blocked_on_nothing 2 -> 5 (`P S5`, `M M53`, `N 195`)
    #:   b1_no_ruling 19 -> 20 (`J 158`, a read no ruling holds)
    #:   jobs_gap 92 -> 107, jobs_dir_r 33 -> 41, jobs_dir_w 53 -> 58,
    #:   jobs_dir_rw 6 -> 8, jobs_refused 26 -> 36; jobs_admitted stays 11
    #:   (`J 158` entered admitted and left GAP); delivered_strict stays 79
    #:
    #: RE-DERIVED AT LANE L5'S MERGE, 2026-09-24, from the tree merged with
    #: master ff98a7f and not as deltas from the lane's base
    #: (`_audit/2026-09-24-lane-l5-messaging.md`, Integration 2026-09-24).
    #: Lane L5 built the reply (`linkedin_send_reply`) and the receipt-safe
    #: inbox: `M M10` and, by D6-CAPABILITY-OVER-AFFORDANCE, `M M17` GAP ->
    #: COVERED-UNFIRED, two W rows held by OPERATOR-NAMES-THE-TARGET; and
    #: `M M49` GAP -> COVERED-UNFIRED, an R row no ruling holds (the read
    #: indicator on his own last message, read with no target). So:
    #:   adjudicated 194 -> 197, delivered_broad 105 -> 108, unfired 30 -> 33
    #:   gap 510 -> 507, gap_read 94 -> 93, gap_write 324 -> 322
    #:   b3_admitted 40 -> 39, b3_blocked_on_nothing 2 -> 1 (`M M49` left)
    #:   b1_standing 10 -> 12, b1_no_ruling 20 -> 21
    #: AND AT LANE L5'S SECOND MERGE, of master 9b9a4d0 (the live lane's four
    #: proven rows and a rulings commit), the same three rows over the live
    #: lane's figures, each MEASURED on the merged tree and equal to the sum:
    #:   adjudicated 197 -> 200, delivered_broad 108 -> 111, unfired 29 -> 32
    #:   gap 507 -> 504, gap_read 91 -> 90, b3_admitted 37 -> 36
    #:   b1_no_ruling 19 -> 20; b1_standing 12, gap_write 322 and
    #:   b3_blocked_on_nothing 1 as at the first merge (the live lane moved
    #:   no write row and none of the rows those count)
    #: AND AT LANE L5'S THIRD MERGE, of master 66aaa95 (lane L7's merge,
    #: with `P I14` above, and a CI fix after it that moved no figure here),
    #: the same three rows over lane L7's figures, each MEASURED on
    #: the merged tree and equal to the sum:
    #:   adjudicated 198 -> 201, delivered_broad 109 -> 112, unfired 30 -> 33
    #:   gap 506 -> 503, gap_write 323 -> 321, b1_standing 11 -> 13
    #:   gap_read 90, b3_admitted 36, b1_no_ruling 20 and
    #:   b3_blocked_on_nothing 1 as at the second merge (lane L7 moved no
    #:   read row and none of the rows those count)
    #: AND AT LANE L5'S FOURTH MERGE, of master 530227e (lane Y2's 43
    #: admitted rows and `J 158`, above), the same three rows over lane Y2's
    #: figures, each MEASURED on the merged tree and equal to the sum:
    #:   adjudicated 199 -> 202, delivered_broad 110 -> 113, unfired 31 -> 34
    #:   gap 548 -> 545, gap_read 104 -> 103, gap_write 337 -> 335
    #:   b3_admitted 42 -> 41, b3_blocked_on_nothing 5 -> 4 (`M M49` left)
    #:   b1_standing 11 -> 13, b1_no_ruling 20 -> 21 -- the last GIT MERGED
    #:   CLEAN AND WRONG: both sides moved it 19 -> 20, lane Y2 by `J 158`
    #:   and this lane by `M M49`, and the tree holds both
    #: RE-DERIVED AT LANE D'S MERGE, 2026-09-24, from the tree merged with
    #: master 9b9a4d0 and not as deltas from the lane's base
    #: (`_audit/2026-09-24-lane-d-d6-pdf.md`, Integration 2026-09-24). Lane D
    #: applied D6-CAPABILITY-OVER-AFFORDANCE: `N 132` GAP -> COVERED-UNFIRED --
    #: both views it switches between are served by their own tools, and one
    #: of the two tools has never been called live -- and it leaves bucket 3,
    #: where it was ADMITTED. `J 107` stays GAP and is re-gated RULING ->
    #: READER in the jobs side table: its route refuses a call with no
    #: keyword, and the fix is a tool change no ruling holds. So:
    #:   adjudicated 197 -> 198, delivered_broad 108 -> 109, unfired 29 -> 30
    #:   gap 507 -> 506, gap_read 91 -> 90, b3_admitted 37 -> 36
    #:   b1_no_ruling 19 -> 20 (N 132 enters bucket 1, held by no ruling)
    #:   jobs_blocked_on_nothing 0 -> 1 (J 107)
    #: AND RE-DERIVED AGAIN AT THE LANE'S MERGE OF MASTER 603f4d3, which had
    #: meanwhile taken lane L7's `P I14`. Both lanes had moved adjudicated,
    #: delivered_broad, unfired and gap by one from the same 197 / 108 / 29 /
    #: 507, so git merged the two IDENTICAL edits as one and left 198 / 109 /
    #: 30 / 506 -- one row short on each, and `--check` said so. Measured on
    #: the merged tree:
    #:   adjudicated 199, delivered_broad 110, unfired 31, gap 505
    #: (b1_standing 11 is lane L7's and b1_no_ruling 20 lane D's; each moved
    #: once, so git's merge of them is right.)
    #: AND AGAIN AT THE LANE'S MERGE OF MASTER 530227e (lane Y2: 43 rows
    #: admitted, `J 158` moved to COVERED-UNFIRED). Measured on that merged
    #: tree against lane Y2's pins, `N 132` is the only move:
    #:   adjudicated 199 -> 200, delivered_broad 110 -> 111, unfired 31 -> 32,
    #:   gap 548 -> 547, gap_read 104 -> 103, b3_admitted 42 -> 41,
    #:   b1_no_ruling 20 -> 21; jobs_blocked_on_nothing stays 1 (`J 107`).
    #: RE-DERIVED AT LANE Y2'S FOLLOW-UP, 2026-09-24, on master 1902fcb and
    #: MEASURED, not summed (`_audit/2026-09-24-lane-y2-admission.md`,
    #: "Follow-up: the P-R settings block"). The P-R block's settings-family
    #: 44, a +44 collapse on `P1` until then, were itemized into 22 rows,
    #: `P2`-`P23`, and the collapse left (see COLLAPSED). `P2` is
    #: EXCLUDED-RULED on ground two; the other 21 are GAP -- 19 writes, and
    #: two reads, `P3` (NEEDS-SESSION) and `P15` (REFUSED). Lane R's handback
    #: bounded the rise of capabilities_achievable at 43; measured, it is 21.
    #:   stated_rows 747 -> 769 (+22); capabilities 805 -> 783 (-22: the +44
    #:   collapse left and 22 rows entered); capabilities_achievable
    #:   691 -> 712 (+21); achievable 677 -> 698 (+21)
    #:   out_of_scope 70 -> 71 and adjudicated 199 -> 200 (`P2`)
    #:   gap 548 -> 569 (+21), gap_read 104 -> 106, gap_write 337 -> 356
    #:   b3_refused 46 -> 47 (`P15`), b3_needs_session 13 -> 14 (`P3`)
    #: 769 AT THE ORCHESTRATOR'S MERGE OF LANE Y2'S FOLLOW-UP (2026-09-27), MEASURED:
    #: the P-R settings block itemized into 22 rows (P2-P23; Delete Data EXCLUDED-RULED).
    #: 770 AT LANE L8'S MERGE OF MASTER (2026-09-27), MEASURED: `P A23b`
    #: entered, split from `P A23` (COMPOUND-ROW-SPLITS-ONLY-ON-STATE).
    #: 771 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:46 (lane S), MEASURED:
    #: `N 26b` entered, split from `N 26` (COMPOUND-ROW-SPLITS-ONLY-ON-STATE):
    #: school and industry, GAP, where location and company went
    #: COVERED-UNFIRED by D6.
    "stated_rows": 771,
    #: 762 = 704 stated rows + 58 declared collapses, computed at HEAD. NOT the
    #: published 761 and NOT the counter docstring's 760: those two differ only
    #: by a `- 2 stateless` term whose two rows are already outside the 704.
    #: Pinned at what the tree computes, with the other two named in the output.
    #: 203 AT THE ORCHESTRATOR'S MERGE OF LANE D (2026-09-27), MEASURED: lane D
    #: moved `N 132` GAP -> COVERED-UNFIRED under D6-CAPABILITY-OVER-AFFORDANCE.
    #: 783 SINCE THE P-R BLOCK WAS ITEMIZED, 2026-09-24: 769 stated rows + 14
    #: for `O6-O20`, the only collapse left.
    #: 783 AT THE ORCHESTRATOR'S MERGE OF LANE Y2'S FOLLOW-UP (2026-09-27), MEASURED:
    #: the P-R settings block itemized into 22 rows (P2-P23; Delete Data EXCLUDED-RULED).
    #: 712 AT THE ORCHESTRATOR'S MERGE OF LANE Y2'S FOLLOW-UP (2026-09-27), MEASURED:
    #: the P-R settings block itemized into 22 rows (P2-P23; Delete Data EXCLUDED-RULED).
    #: 71 AT THE ORCHESTRATOR'S MERGE OF LANE Y2'S FOLLOW-UP (2026-09-27), MEASURED:
    #: the P-R settings block itemized into 22 rows (P2-P23; Delete Data EXCLUDED-RULED).
    #: 698 AT THE ORCHESTRATOR'S MERGE OF LANE Y2'S FOLLOW-UP (2026-09-27), MEASURED:
    #: the P-R settings block itemized into 22 rows (P2-P23; Delete Data EXCLUDED-RULED).
    #: 204 AT THE ORCHESTRATOR'S MERGE OF LANE Y2'S FOLLOW-UP (2026-09-27), MEASURED:
    #: the P-R settings block itemized into 22 rows (P2-P23; Delete Data EXCLUDED-RULED).
    #: LANE L7'S P B9 BUILD (2026-09-24), integrated over master 0e4f4b3,
    #: MEASURED on the merged tree: `P B9` GAP -> COVERED-UNFIRED, the Premium
    #: badge switch pressed through `linkedin_update_profile_field` and aimed
    #: by its block's title compared in the page, never fired
    #: (`_audit/2026-09-24-lane-l7-profile-writes.md`, Follow-up F.5). A W row
    #: whose cell cites RELEASED BY SELF-PROFILE-EDITS-NOT-OUTWARD, as the six
    #: intro-field edits do, so it enters bucket 1 held by no ruling. One row
    #: changing class moves seven figures: adjudicated, delivered_broad and
    #: unfired +1; gap and gap_write -1; b1_no_ruling and b1_released +1.
    #: 784 AT LANE L8'S MERGE OF MASTER (2026-09-27), MEASURED: `P A23b`
    #: entered; no collapse moved.
    #: 785 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:46 (lane S), MEASURED:
    #: `N 26b` entered (see `stated_rows`); no collapse moved.
    "capabilities": 785,
    #: 741 AT LANE L8'S MERGE OF MASTER (2026-09-27), MEASURED: the achievable
    #: move, with `O6-O20`'s 14 unchanged.
    #: 742 AT LANE L5'S MERGE OF MASTER 52b55b6 (2026-09-27), MEASURED: `N 2` left the exclusions.
    #: 746 ON LANE L5'S ORDER OF 2026-09-28 12:32, MEASURED: `N 30`, `N 31`, `N 65`
    #: and `N 103` EXCLUDED-RULED -> GAP, their R4 ground narrowed by
    #: NAMED-PROFILE-READ-BEHIND-A-GRANT (the orchestrator's call).
    #: 747 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:46 (lane S), MEASURED:
    #: `N 26b` entered, in scope (see `stated_rows`).
    #: 745 ON LANE K's PURCHASES-STAY-MANUAL EXCLUSIONS (2026-10-10), MEASURED:
    #: `P S9` and `M C71` GAP -> EXCLUDED-RULED; `O6-O20`'s 14 unchanged.
    #: 724 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED: the
    #: same 21 rows; `O6-O20`'s 14 unchanged.
    "capabilities_achievable": 724,
    #: 43 AT LANE L8'S MERGE OF MASTER (2026-09-27), MEASURED: 29 rows returned
    #: to GAP when OUTWARD-CLASSES-BUILT-BEHIND-GRANTS retired their key, and
    #: `P P2` at the merge (-30); `P N27` and `P P2` then EXCLUDED-RULED on
    #: ACCOUNT-DESTRUCTION-STAYS-MANUAL (+2).
    #: 42 AT LANE L5'S MERGE OF MASTER 52b55b6 (2026-09-27), MEASURED: `N 2` EXCLUDED-RULED -> COVERED-UNFIRED, its R4 ground
    #: dissolved by THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET.
    #: 38 ON LANE L5'S ORDER OF 2026-09-28 12:32, MEASURED: `N 30`, `N 31`, `N 65`
    #: and `N 103` EXCLUDED-RULED -> GAP, their R4 ground narrowed by
    #: NAMED-PROFILE-READ-BEHIND-A-GRANT (the orchestrator's call).
    #: 40 ON LANE K's PURCHASES-STAY-MANUAL EXCLUSIONS (2026-10-10), MEASURED:
    #: `P S9` (the Premium plan) and `M C71` (a paid boost) GAP ->
    #: EXCLUDED-RULED on the orchestrator's ruling of 2026-09-28.
    #: 61 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED: 21
    #: rows EXCLUDED-RULED -- CONTACT-IMPORT-STAYS-MANUAL 3, SESSION-SURFACE 1,
    #: SIGN-IN-CHALLENGES-ARE-HIS 2, SAFETY-REPORTS-STAY-MANUAL 1,
    #: OUTSIDE-THE-PRODUCT-PURPOSE 14.
    "out_of_scope": 61,
    #: 727 AT LANE L8'S MERGE OF MASTER (2026-09-27), MEASURED: stated rows 770
    #: less out_of_scope 43: the returns, `P A23b`, and the two re-exclusions.
    #: 728 AT LANE L5'S MERGE OF MASTER 52b55b6 (2026-09-27), MEASURED: stated rows 770 less out_of_scope 42 (`N 2`).
    #: 732 ON LANE L5'S ORDER OF 2026-09-28 12:32, MEASURED: `N 30`, `N 31`, `N 65`
    #: and `N 103` EXCLUDED-RULED -> GAP, their R4 ground narrowed by
    #: NAMED-PROFILE-READ-BEHIND-A-GRANT (the orchestrator's call). Stated rows 770
    #: less out_of_scope 38.
    #: 733 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:46 (lane S), MEASURED:
    #: stated rows 771 less out_of_scope 38 -- `N 26b` entered, in scope.
    #: 731 ON LANE K's PURCHASES-STAY-MANUAL EXCLUSIONS (2026-10-10), MEASURED:
    #: stated rows 771 less out_of_scope 40 (`P S9`, `M C71`).
    #: 710 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED:
    #: stated rows 771 less out_of_scope 61.
    "achievable": 710,
    #: 205 AT THE ORCHESTRATOR'S MERGE OF LANE L7'S P B9 (2026-09-27), MEASURED: P B9
    #: (Premium badge) moved GAP -> COVERED-UNFIRED, released like the intro edits.
    #: 179 AT LANE L8'S MERGE OF MASTER (2026-09-27), MEASURED: the 30 returned
    #: rows left an adjudicated state, `M C63` and `N 64` entered
    #: COVERED-UNFIRED, and `P N27` / `P P2` re-entered EXCLUDED-RULED.
    #: 180 AT LANE L5'S MERGE OF MASTER 52b55b6 (2026-09-27), MEASURED: `N 4` left GAP; `M M1` and `N 2` moved between
    #: adjudicated states.
    #: 182 AT LANE S'S NAMES ADOPTION (2026-09-27), MEASURED: `N 79`, `N 172`
    #: and `N 194` GAP -> COVERED-UNFIRED, now that
    #: `linkedin_people_search_shape(include_names=True)` returns WHO as people
    #: records (`people_results.read_result_people`, NAMES-AT-RUNTIME and the
    #: six PEOPLE-DATA-MITIGATIONS), never fired. Three R rows that were
    #: ADMITTED and gated READER in bucket 3, so they leave it and enter bucket
    #: 1 held by no ruling.
    #: 183 AT LANE S'S MERGE OF MASTER 687b07c (2026-09-27), MEASURED on the
    #: merged tree, not summed: lane S's `N 79`, `N 172`, `N 194` and lane L5's
    #: `N 2`, `N 4`, `M M1` both carried. Each side had moved this figure by
    #: three from the same base, and git merged the two equal value lines as
    #: one -- three short -- which the measurement caught.
    #: 179 ON LANE L5'S ORDER OF 2026-09-27 23:36, MEASURED:
    #: `linkedin_send_message` RETIRED (aimed by a name): `M M2` returned to
    #: GAP, its only tool retired.
    #: 182 AT LANE L5'S MERGE OF MASTER 64afa6c (2026-09-27), MEASURED on the merged tree: master's figure with this branch's `M M2` back to GAP.
    #: 187 AT LANE S'S OFFLINE FRONTIER (2026-09-28, on its branch), MEASURED:
    #: the five rows bucket 3 called blocked on nothing, taken one by one.
    #: `M M53`, `N 195` and `P S5` (three R rows ADMITTED and gated READER)
    #: and `J 107` (the one jobs row) GAP -> COVERED-UNFIRED, each built over
    #: a capture or on a shipped page and never fired, so they leave buckets 3
    #: and 1-by-side and enter bucket 1 held by no ruling. `P K1` stays GAP
    #: and is re-gated READER -> MEASURE: no capture draws its section.
    #: 186 AT LANE S'S MERGE OF MASTER 0867bda (2026-09-28), MEASURED on the
    #: merged tree: master's `M M2` back to GAP with this branch's four.
    #: 182 ON LANE L5'S ORDER OF 2026-09-28 12:32, MEASURED: `N 30`, `N 31`, `N 65`
    #: and `N 103` EXCLUDED-RULED -> GAP, their R4 ground narrowed by
    #: NAMED-PROFILE-READ-BEHIND-A-GRANT (the orchestrator's call).
    #: 184 ON THE ORCHESTRATOR'S ORDER OF 2026-09-28 15:10 (lane S), MEASURED:
    #: `N 30` (by D6, his ruling) and `N 31` (the people search's new
    #: `network` facet) GAP -> COVERED-UNFIRED, each the people search a
    #: first-degree profile's topcard links to, never fired. Two R rows that
    #: were ADMITTED in bucket 3 (`N 31` BLOCKED ON NOTHING), so they leave it
    #: and enter bucket 1 held by no ruling.
    #: 185 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:02 (lane S), MEASURED:
    #: `N 81` GAP -> COVERED-UNFIRED -- the same `network` facet ALONE, a
    #: people search filtered by degree, as the connections page writes it;
    #: never fired. An R row ADMITTED in bucket 3, so it leaves it and enters
    #: bucket 1 held by no ruling.
    #: 187 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:46 (lane S), MEASURED:
    #: `N 25` (a name search of his first degree) and `N 26` (its location
    #: and company halves) GAP -> COVERED-UNFIRED by D6 on the degree filter,
    #: never fired. Two R rows REFUSED in bucket 3 (the connections page's
    #: query variants), so they leave it and enter bucket 1 held by no ruling;
    #: `N 26b`, split from `N 26`, enters GAP.
    #: 184 AT THE LIVE LANE'S MERGE OF MASTER c2825a4 (2026-09-28), MEASURED on the
    #: merged tree: master's figure with this branch's `P A11`, `P A13` and `P A17`
    #: COVERED-UNFIRED -> GAP (session 4: autocomplete inputs the one tool can only
    #: type into, now refused by it).
    #: 186 ON LANE K's PURCHASES-STAY-MANUAL EXCLUSIONS (2026-10-10), MEASURED:
    #: `P S9` and `M C71` GAP -> EXCLUDED-RULED -- adjudicated, delivered by
    #: neither line.
    #: 210 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED: the
    #: 21 exclusions, `P A9` COVERED-CANNOT-DELIVER (P-A9-CANNOT-DELIVER), and
    #: `J 17` and `J 57` COVERED-PROVEN by D6 (GEOLOCATION-BY-D6,
    #: CALLER-COMPOSITION-UNDER-D6).
    #: 189 ON LANE U'S MOVE OF 2026-10-10, MEASURED:
    #: `M M14`, `M M15` and `M M18` GAP -> COVERED-UNFIRED -- adjudicated now.
    #: 213 AT LANE U'S MERGE OF ORIGIN/MASTER 71d83ca, MEASURED: lane K's
    #: 210 with lane U's three rows (+3).
    #: 214 AT LANE B1'S MERGE OF ORIGIN/MASTER 0103810, MEASURED: master's figure with `P A22` GAP -> COVERED-UNFIRED (the Organization select, session 7).
    #: 216 ON LANE B1 (2026-10-10), MEASURED: `P L8` and `P L1` GAP -> COVERED-UNFIRED (the analytics hub and the audience page, on session 1's captures).
    "adjudicated": 216,
    #: THE LIVE LANE'S FOUR ROWS, RE-DERIVED AT EACH OF ITS MERGES OF MASTER
    #: (2026-09-24; last over lane S): four rows fired live and banked
    #: (`_audit/2026-09-23-live-lane-session-1.md`). `P G6` COVERED-UNFIRED ->
    #: COVERED-PROVEN, so it leaves `unfired` and bucket 1 and joins
    #: delivered_strict; `N 134`, `P O3` and `M C72` GAP -> COVERED-PROVEN, so
    #: each is newly adjudicated and delivered, and each leaves `gap`,
    #: `gap_read` and bucket 3 (all three were ADMITTED). Every figure below
    #: that the four move is measured on the merged tree, not summed.
    #: 434 / 100 / 270 / 25, and gap_write 150, since the lane-L4 merge
    #: (2026-09-23): `N 47` was built -- `linkedin_follow_company_page`, a
    #: WRITE, behind the flag and the single-use grant, never fired (GAP ->
    #: COVERED-UNFIRED, `_audit/2026-09-23-lane-l4-writes.md`). It is a W row,
    #: so it enters bucket 1 held by OPERATOR-NAMES-THE-TARGET with no marker
    #: (b1_standing 9 -> 10), and it leaves the write-direction GAP count.
    #: 433 / 99 / 271 / 24 since the lane-L3 merge (2026-09-23): `J 18` and
    #: `J 39` were built (GAP -> COVERED-UNFIRED, `_audit/2026-09-23-lane-l3-
    #: jobs.md`); both enter bucket 1 held by no ruling (b1_no_ruling 7 -> 9),
    #: and gap_unknown 56 -> 54 because both were jobs rows. gap_read stays 66:
    #: jobs rows are counted by the side table, below, not in bucket 3.
    #: 431 / 97 / 273 / 22 / 66 since the lane-L1 merge: `P G6` was built
    #: (GAP -> COVERED-UNFIRED, `_audit/2026-09-23-lane-l1-refused-reads.md`).
    #: One row changing class moves all five; b3 admitted/refused 40/16 are
    #: L1's allowlist admissions, and b1_no_ruling 7 is P G6 entering bucket 1.
    #: 114 AT THE ORCHESTRATOR'S MERGE OF LANE D (2026-09-27), MEASURED: lane D
    #: moved `N 132` GAP -> COVERED-UNFIRED under D6-CAPABILITY-OVER-AFFORDANCE.
    #: 115 AT THE ORCHESTRATOR'S MERGE OF LANE L7'S P B9 (2026-09-27), MEASURED: P B9
    #: (Premium badge) moved GAP -> COVERED-UNFIRED, released like the intro edits.
    #: 117 AT LANE L8'S MERGE OF MASTER (2026-09-27), MEASURED: `M C63` and
    #: `N 64` built (`linkedin_withdraw_from_group`), never fired.
    #: 120 AT LANE L5'S MERGE OF MASTER 52b55b6 (2026-09-27), MEASURED: `M M1` (COVERED-CANNOT-DELIVER), `N 4` (GAP, by D6) and `N 2`
    #: (EXCLUDED-RULED, moved at the merge on the orchestrator's application of
    #: THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET) all COVERED-UNFIRED.
    #: 120 AT LANE S'S NAMES ADOPTION (2026-09-27), MEASURED: `N 79`, `N 172`
    #: and `N 194` GAP -> COVERED-UNFIRED, now that
    #: `linkedin_people_search_shape(include_names=True)` returns WHO as people
    #: records (`people_results.read_result_people`, NAMES-AT-RUNTIME and the
    #: six PEOPLE-DATA-MITIGATIONS), never fired. Three R rows that were
    #: ADMITTED and gated READER in bucket 3, so they leave it and enter bucket
    #: 1 held by no ruling.
    #: 123 AT LANE S'S MERGE OF MASTER 687b07c (2026-09-27), MEASURED on the
    #: merged tree, not summed: lane S's `N 79`, `N 172`, `N 194` and lane L5's
    #: `N 2`, `N 4`, `M M1` both carried. Each side had moved this figure by
    #: three from the same base, and git merged the two equal value lines as
    #: one -- three short -- which the measurement caught.
    #: 121 ON LANE L5'S ORDER OF 2026-09-27 23:36, MEASURED:
    #: `linkedin_send_message` RETIRED (aimed by a name): `N 155`
    #: COVERED-CANNOT-DELIVER -> COVERED-UNFIRED on
    #: `linkedin_message_from_profile`.
    #: 124 AT LANE L5'S MERGE OF MASTER 64afa6c (2026-09-27), MEASURED on the merged tree: master's figure with this branch's `N 155`.
    #: 127 AT LANE S'S OFFLINE FRONTIER (2026-09-28, on its branch), MEASURED:
    #: `M M53`, `N 195`, `P S5` and `J 107` GAP -> COVERED-UNFIRED (see
    #: `adjudicated`).
    #: 128 AT LANE S'S MERGE OF MASTER 0867bda (2026-09-28), MEASURED on the
    #: merged tree: master's `N 155` with this branch's four.
    #: 130 ON THE ORCHESTRATOR'S ORDER OF 2026-09-28 15:10 (lane S), MEASURED:
    #: `N 30` and `N 31` GAP -> COVERED-UNFIRED (see `adjudicated`).
    #: 131 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:02 (lane S), MEASURED:
    #: `N 81` GAP -> COVERED-UNFIRED (see `adjudicated`).
    #: 133 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:46 (lane S), MEASURED:
    #: `N 25` and `N 26` GAP -> COVERED-UNFIRED (see `adjudicated`).
    #: 130 AT THE LIVE LANE'S MERGE OF MASTER c2825a4 (2026-09-28), MEASURED on the
    #: merged tree: master's figure with this branch's `P A11`, `P A13` and `P A17`
    #: COVERED-UNFIRED -> GAP (session 4: autocomplete inputs the one tool can only
    #: type into, now refused by it).
    #: 132 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED: `J
    #: 17` and `J 57` COVERED-PROVEN by D6, every part proven.
    #: 133 ON LANE U'S MOVE OF 2026-10-10, MEASURED:
    #: `M M14`, `M M15` and `M M18` GAP -> COVERED-UNFIRED on `linkedin_send_attachment`.
    #: 135 AT LANE U'S MERGE OF ORIGIN/MASTER 71d83ca, MEASURED: lane K's
    #: 132 with lane U's three rows (+3).
    #: 136 AT LANE B1'S MERGE OF ORIGIN/MASTER 0103810, MEASURED: master's figure with `P A22` GAP -> COVERED-UNFIRED (the Organization select, session 7).
    #: 138 ON LANE B1 (2026-10-10), MEASURED: `P L8` and `P L1` GAP -> COVERED-UNFIRED (the analytics hub and the audience page, on session 1's captures).
    "delivered_broad": 138,
    #: 79 since the live lane's merge (see `adjudicated`): P G6, N 134, P O3
    #: and M C72 COVERED-PROVEN.
    #: 75 and 21 since the bucket-1 merge: `M C41` fired live and moved from
    #: COVERED-UNFIRED to COVERED-PROVEN (`_audit/2026-09-23-bucket1-fires.md`).
    #: One row changing class moves both, and leaves delivered_broad at 96.
    #: 91 AT THE LIVE LANE'S SESSION 2 (2026-09-28), MEASURED: twelve rows
    #: fired live and banked, each on its own cell's bar -- `J 18`, `J 39`,
    #: `J 158`, `M M43`, `N 23`, `N 79`, `N 84`, `N 87`, `N 94`, `N 132`,
    #: `N 195`, `P S5` -- COVERED-UNFIRED -> COVERED-PROVEN. delivered_broad
    #: does not move: a row changing class within it.
    #: 94 AT THE LIVE LANE'S SESSION 3 (2026-09-28), MEASURED: `J 107`, `M M53`
    #: and `N 194` fired live and banked, each on its own cell's bar.
    #: 96 AT THE LIVE LANE'S SESSION 5 (2026-09-28), MEASURED: `M M1` (sent on the
    #: first-contact path, verified) and `P B9` (both directions, one restore
    #: failed before the recovery held) fired live and banked.
    #: 101 AT THE LIVE LANE'S SESSION 6 (2026-09-28), MEASURED: `M M17` (the reply
    #: with its emoji, sent and verified), `M M33` (the starred pill applied), `M M49`
    #: (the read indicator read) and `P A21`, `P A19` (tested and restored exactly)
    #: fired live and banked.
    #: 105 AT THE LIVE LANE'S SESSION 7 (2026-10-10), MEASURED: `N 25` (a
    #: 1st-degree connection found by name), `N 81` (the degree facet applied to
    #: the results) and `N 26` (his connections filtered by place) fired live and
    #: banked; `N 155` moved on the orchestrator's call of that day, by D6 on
    #: `M M1`'s session-5 send.
    #: 109 AT THE LIVE LANE'S SESSION 8 (2026-10-10), MEASURED: `N 48` and `J 104`
    #: (the unfollow through LinkedIn's confirmation, the row gone and a posting
    #: reading not-following) and `N 46` and `J 103` (the follow from a posting
    #: that restored it, verified on Manage Pages) fired live and banked.
    #: 107 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED on its
    #: branch: `J 17` and `J 57` COVERED-PROVEN by D6, every part proven.
    #: 111 AT LANE K's MERGE OF MASTER 66eb699 (2026-10-10), MEASURED on the
    #: merged tree, not summed: session 8's four rows and lane K's two.
    #: 113 AT THE LIVE LANE'S SESSION 9 (2026-10-10), MEASURED: `N 30`, `N 85`
    #: and `N 172` (a named member's connections, as people, by the
    #: Connections-of filter) and `N 31` (the connections he and that member
    #: share) fired live, read-only, and banked.
    #: 115 AT THE LIVE LANE'S MERGE OF MASTER 0103810 (2026-10-10), MEASURED on the
    #: merged tree, not summed: the live lane's session 9 and the lanes
    #: master carried (K's rulings, U's attachments).
    "delivered_strict": 115,
    #: The live lane's merge: N 134, P O3 and M C72 left GAP.
    #: Lane D's merge: N 132 left GAP, for COVERED-UNFIRED under D6.
    #: 544 AT THE ORCHESTRATOR'S MERGE OF LANE D (2026-09-27), MEASURED: lane D
    #: moved `N 132` GAP -> COVERED-UNFIRED under D6-CAPABILITY-OVER-AFFORDANCE.
    #: 35 AT THE ORCHESTRATOR'S MERGE OF LANE D (2026-09-27), MEASURED: lane D
    #: moved `N 132` GAP -> COVERED-UNFIRED under D6-CAPABILITY-OVER-AFFORDANCE.
    #: 102 AT THE ORCHESTRATOR'S MERGE OF LANE D (2026-09-27), MEASURED: lane D
    #: moved `N 132` GAP -> COVERED-UNFIRED under D6-CAPABILITY-OVER-AFFORDANCE.
    #: 106 since the P-R block was itemized: `P3` and `P15` entered.
    #: 565 AT THE ORCHESTRATOR'S MERGE OF LANE Y2'S FOLLOW-UP (2026-09-27), MEASURED:
    #: the P-R settings block itemized into 22 rows (P2-P23; Delete Data EXCLUDED-RULED).
    #: 564 AT THE ORCHESTRATOR'S MERGE OF LANE L7'S P B9 (2026-09-27), MEASURED: P B9
    #: (Premium badge) moved GAP -> COVERED-UNFIRED, released like the intro edits.
    #: 591 AT LANE L8'S MERGE OF MASTER (2026-09-27), MEASURED: +30 returned,
    #: +1 `P A23b`, -2 built (`M C63`, `N 64`), -2 re-excluded (`P N27`,
    #: `P P2`).
    #: 590 AT LANE L5'S MERGE OF MASTER 52b55b6 (2026-09-27), MEASURED: `N 4` built (`linkedin_connect_from_profile`), by D6.
    #: 588 AT LANE S'S NAMES ADOPTION (2026-09-27), MEASURED: `N 79`, `N 172`
    #: and `N 194` GAP -> COVERED-UNFIRED, now that
    #: `linkedin_people_search_shape(include_names=True)` returns WHO as people
    #: records (`people_results.read_result_people`, NAMES-AT-RUNTIME and the
    #: six PEOPLE-DATA-MITIGATIONS), never fired. Three R rows that were
    #: ADMITTED and gated READER in bucket 3, so they leave it and enter bucket
    #: 1 held by no ruling.
    #: 587 AT LANE S'S MERGE OF MASTER 687b07c (2026-09-27), MEASURED on the
    #: merged tree, not summed: lane S's `N 79`, `N 172`, `N 194` and lane L5's
    #: `N 2`, `N 4`, `M M1` both carried. Each side had moved this figure by
    #: three from the same base, and git merged the two equal value lines as
    #: one -- three short -- which the measurement caught.
    #: 591 ON LANE L5'S ORDER OF 2026-09-27 23:36, MEASURED:
    #: `linkedin_send_message` RETIRED (aimed by a name): `M M2`
    #: COVERED-CANNOT-DELIVER -> GAP.
    #: 588 AT LANE L5'S MERGE OF MASTER 64afa6c (2026-09-27), MEASURED on the merged tree: master's figure with this branch's `M M2`.
    #: 583 AT LANE S'S OFFLINE FRONTIER (2026-09-28, on its branch), MEASURED:
    #: `M M53`, `N 195`, `P S5` and `J 107` left GAP (see `adjudicated`).
    #: 584 AT LANE S'S MERGE OF MASTER 0867bda (2026-09-28), MEASURED on the
    #: merged tree: master's `M M2` back in GAP, this branch's four out.
    #: 588 ON LANE L5'S ORDER OF 2026-09-28 12:32, MEASURED: `N 30`, `N 31`, `N 65`
    #: and `N 103` EXCLUDED-RULED -> GAP, their R4 ground narrowed by
    #: NAMED-PROFILE-READ-BEHIND-A-GRANT (the orchestrator's call).
    #: 586 ON THE ORCHESTRATOR'S ORDER OF 2026-09-28 15:10 (lane S), MEASURED:
    #: `N 30` and `N 31` left GAP (see `adjudicated`).
    #: 585 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:02 (lane S), MEASURED:
    #: `N 81` left GAP (see `adjudicated`).
    #: 584 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:46 (lane S), MEASURED:
    #: `N 25` and `N 26` left GAP and `N 26b` entered it (see `adjudicated`).
    #: 587 AT THE LIVE LANE'S MERGE OF MASTER c2825a4 (2026-09-28), MEASURED on the
    #: merged tree: master's figure with this branch's `P A11`, `P A13` and `P A17`
    #: COVERED-UNFIRED -> GAP (session 4: autocomplete inputs the one tool can only
    #: type into, now refused by it).
    #: 585 ON LANE K's PURCHASES-STAY-MANUAL EXCLUSIONS (2026-10-10), MEASURED:
    #: `P S9` and `M C71` left GAP (see `adjudicated`).
    #: 561 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED: 24
    #: rows left GAP (see `adjudicated`).
    #: 582 ON LANE U'S MOVE OF 2026-10-10, MEASURED:
    #: `M M14`, `M M15` and `M M18` left GAP (see `adjudicated`).
    #: 558 AT LANE U'S MERGE OF ORIGIN/MASTER 71d83ca, MEASURED: lane K's
    #: 561 with lane U's three rows (-3).
    #: 557 AT LANE B1'S MERGE OF ORIGIN/MASTER 0103810, MEASURED: master's figure with `P A22` GAP -> COVERED-UNFIRED (the Organization select, session 7).
    #: 555 ON LANE B1 (2026-10-10), MEASURED: `P L8` and `P L1` GAP -> COVERED-UNFIRED (the analytics hub and the audience page, on session 1's captures).
    "gap": 555,
    #: 18 AT LANE L5'S MERGE OF MASTER 52b55b6 (2026-09-27), MEASURED: `M M1` built (`linkedin_message_from_profile`).
    #: 16 ON LANE L5'S ORDER OF 2026-09-27 23:36, MEASURED:
    #: `linkedin_send_message` RETIRED (aimed by a name): `M M2` to GAP and `N
    #: 155` to COVERED-UNFIRED.
    #: 16 AT LANE L5'S MERGE OF MASTER 64afa6c (2026-09-27), MEASURED on the merged tree: master moved none of these.
    #: 16 AT LANE S'S MERGE OF MASTER 0867bda (2026-09-28), MEASURED on the
    #: merged tree: lane S moved none of these.
    #: 17 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED: `P
    #: A9`, on the P A2 / P A4 precedent.
    "cannot_deliver": 17,
    #: 36 AT THE ORCHESTRATOR'S MERGE OF LANE L7'S P B9 (2026-09-27), MEASURED: P B9
    #: (Premium badge) moved GAP -> COVERED-UNFIRED, released like the intro edits.
    #: 38 AT LANE L8'S MERGE OF MASTER (2026-09-27), MEASURED: `M C63` and
    #: `N 64` built, never fired.
    #: 41 AT LANE L5'S MERGE OF MASTER 52b55b6 (2026-09-27), MEASURED: `M M1` (COVERED-CANNOT-DELIVER), `N 4` (GAP, by D6) and `N 2`
    #: (EXCLUDED-RULED, moved at the merge on the orchestrator's application of
    #: THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET) all COVERED-UNFIRED.
    #: 41 AT LANE S'S NAMES ADOPTION (2026-09-27), MEASURED: `N 79`, `N 172`
    #: and `N 194` GAP -> COVERED-UNFIRED, now that
    #: `linkedin_people_search_shape(include_names=True)` returns WHO as people
    #: records (`people_results.read_result_people`, NAMES-AT-RUNTIME and the
    #: six PEOPLE-DATA-MITIGATIONS), never fired. Three R rows that were
    #: ADMITTED and gated READER in bucket 3, so they leave it and enter bucket
    #: 1 held by no ruling.
    #: 44 AT LANE S'S MERGE OF MASTER 687b07c (2026-09-27), MEASURED on the
    #: merged tree, not summed: lane S's `N 79`, `N 172`, `N 194` and lane L5's
    #: `N 2`, `N 4`, `M M1` both carried. Each side had moved this figure by
    #: three from the same base, and git merged the two equal value lines as
    #: one -- three short -- which the measurement caught.
    #: 42 ON LANE L5'S ORDER OF 2026-09-27 23:36, MEASURED:
    #: `linkedin_send_message` RETIRED (aimed by a name): `N 155` on
    #: `linkedin_message_from_profile`, never fired.
    #: 45 AT LANE L5'S MERGE OF MASTER 64afa6c (2026-09-27), MEASURED on the merged tree: master's figure with this branch's `N 155`.
    #: 48 AT LANE S'S OFFLINE FRONTIER (2026-09-28, on its branch), MEASURED:
    #: `M M53`, `N 195`, `P S5` and `J 107` COVERED-UNFIRED, never fired
    #: (see `adjudicated`).
    #: 49 AT LANE S'S MERGE OF MASTER 0867bda (2026-09-28), MEASURED on the
    #: merged tree: master's `N 155` with this branch's four.
    #: 37 AT THE LIVE LANE'S SESSION 2 (2026-09-28), MEASURED: the twelve rows
    #: named at `delivered_strict` fired live and banked, leaving
    #: COVERED-UNFIRED.
    #: 34 AT THE LIVE LANE'S SESSION 3 (2026-09-28), MEASURED: `J 107`, `M M53`
    #: and `N 194` fired live and banked, each on its own cell's bar.
    #: 36 ON THE ORCHESTRATOR'S ORDER OF 2026-09-28 15:10 (lane S), MEASURED:
    #: `N 30` and `N 31` COVERED-UNFIRED, never fired (see `adjudicated`).
    #: 37 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:02 (lane S), MEASURED:
    #: `N 81` COVERED-UNFIRED, never fired (see `adjudicated`).
    #: 39 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:46 (lane S), MEASURED:
    #: `N 25` and `N 26` COVERED-UNFIRED, never fired (see `adjudicated`).
    #: 36 AT THE LIVE LANE'S MERGE OF MASTER c2825a4 (2026-09-28), MEASURED on the
    #: merged tree: master's figure with this branch's `P A11`, `P A13` and `P A17`
    #: COVERED-UNFIRED -> GAP (session 4: autocomplete inputs the one tool can only
    #: type into, now refused by it).
    #: 34 AT THE LIVE LANE'S SESSION 5 (2026-09-28), MEASURED: `M M1` (sent on the
    #: first-contact path, verified) and `P B9` (both directions, one restore
    #: failed before the recovery held) fired live and banked.
    #: 29 AT THE LIVE LANE'S SESSION 6 (2026-09-28), MEASURED: `M M17` (the reply
    #: with its emoji, sent and verified), `M M33` (the starred pill applied), `M M49`
    #: (the read indicator read) and `P A21`, `P A19` (tested and restored exactly)
    #: fired live and banked.
    #: 25 AT THE LIVE LANE'S SESSION 7 (2026-10-10), MEASURED: `N 25` (a
    #: 1st-degree connection found by name), `N 81` (the degree facet applied to
    #: the results) and `N 26` (his connections filtered by place) fired live and
    #: banked; `N 155` moved on the orchestrator's call of that day, by D6 on
    #: `M M1`'s session-5 send.
    #: 21 AT THE LIVE LANE'S SESSION 8 (2026-10-10), MEASURED: `N 48` and `J 104`
    #: (the unfollow through LinkedIn's confirmation, the row gone and a posting
    #: reading not-following) and `N 46` and `J 103` (the follow from a posting
    #: that restored it, verified on Manage Pages) fired live and banked.
    #: 28 ON LANE U'S MOVE OF 2026-10-10, MEASURED:
    #: `M M14`, `M M15` and `M M18` entered COVERED-UNFIRED, never fired.
    #: 24 AT LANE U'S MERGE OF ORIGIN/MASTER 1027bf8, MEASURED: session 8's
    #: four banked out (25 - 4) and lane U's three in (+ 3).
    #: 17 AT THE LIVE LANE'S SESSION 9 (2026-10-10), MEASURED: `N 30`, `N 85`
    #: and `N 172` (a named member's connections, as people, by the
    #: Connections-of filter) and `N 31` (the connections he and that member
    #: share) fired live, read-only, and banked.
    #: 20 AT THE LIVE LANE'S MERGE OF MASTER 0103810 (2026-10-10), MEASURED on the
    #: merged tree, not summed: the live lane's session 9 and the lanes
    #: master carried (K's rulings, U's attachments).
    #: 23 AT LANE B1'S MERGE OF ORIGIN/MASTER 6c65815, MEASURED on the merged tree: master's figure (session 9) with lane B1's `P A22`, `P L8` and `P L1` COVERED-UNFIRED (+3).
    "unfired": 23,
    #: 104 AT THE ORCHESTRATOR'S MERGE OF LANE Y2'S FOLLOW-UP (2026-09-27), MEASURED:
    #: the P-R settings block itemized into 22 rows (P2-P23; Delete Data EXCLUDED-RULED).
    #: 101 AT LANE S'S NAMES ADOPTION (2026-09-27), MEASURED: `N 79`, `N 172`
    #: and `N 194` GAP -> COVERED-UNFIRED, now that
    #: `linkedin_people_search_shape(include_names=True)` returns WHO as people
    #: records (`people_results.read_result_people`, NAMES-AT-RUNTIME and the
    #: six PEOPLE-DATA-MITIGATIONS), never fired. Three R rows that were
    #: ADMITTED and gated READER in bucket 3, so they leave it and enter bucket
    #: 1 held by no ruling.
    #: 98 AT LANE S'S OFFLINE FRONTIER (2026-09-28), MEASURED: the five rows
    #: bucket 3 called blocked on nothing, taken one by one. `M M53`, `N 195`
    #: and `P S5` (three R rows ADMITTED and gated READER) and `J 107` (the one
    #: jobs row) GAP -> COVERED-UNFIRED, each built over a capture or on a
    #: shipped page and never fired, so they leave buckets 3 and 1-by-side and
    #: enter bucket 1 held by no ruling. `P K1` stays GAP and is re-gated
    #: READER -> MEASURE: no capture draws its section.
    #: 102 ON LANE L5'S ORDER OF 2026-09-28 12:32, MEASURED: `N 30`, `N 31`, `N 65`
    #: and `N 103` EXCLUDED-RULED -> GAP, their R4 ground narrowed by
    #: NAMED-PROFILE-READ-BEHIND-A-GRANT (the orchestrator's call). All four are R
    #: rows, and all four enter bucket 3.
    #: 100 ON THE ORCHESTRATOR'S ORDER OF 2026-09-28 15:10 (lane S), MEASURED:
    #: `N 30` and `N 31`, two R rows, left GAP and bucket 3 (see `adjudicated`).
    #: 99 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:02 (lane S), MEASURED:
    #: `N 81`, an R row, left GAP and bucket 3 (see `adjudicated`).
    #: 98 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:46 (lane S), MEASURED:
    #: `N 25` and `N 26` left GAP and bucket 3, and `N 26b`, an R row, entered
    #: both (see `adjudicated`).
    #: 92 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED: `P
    #: N13`, `M C95`, `M C96`, `M C98`, `M C99` (R+W) and `P J4` left GAP.
    #: 90 ON LANE B1 (2026-10-10), MEASURED: `P L8` and `P L1` GAP -> COVERED-UNFIRED (the analytics hub and the audience page, on session 1's captures).
    "gap_read": 90,
    #: 151, not the 152 published by `_audit/2026-09-21-the-write-ceiling.md`.
    #: That document scoped itself to `profile.md`, `network.md` and
    #: `messaging-and-content.md`; measured at HEAD those three carry W 151 and
    #: R+W 3, and `jobs.md` contributes no direction at all. The compound-rows
    #: wave repaired `M C85` from `W` to `R+W` IN PLACE, which is a -1 on W and
    #: is CONSISTENT WITH the difference rather than proof of it -- stated that
    #: way because I did not re-derive that document's population.
    #: 150 since the lane-L4 merge: `N 47` was built and left GAP. The same
    #: lane classed all 151 in `_audit/_census/write-classes.tsv`, which keeps
    #: the built row's line, and `scripts/check_write_classes.py` re-walks it.
    #: 324 since lane R's merge: 173 write-direction rows returned, and `N 183`,
    #: a read row until rulings batch 3 named it a setting -- every one classed
    #: in the same table by its act (16 R1, 35 R2, 274 R3 over 325 lines, the
    #: built `N 47` keeping its line).
    #: 323 since lane L7's merge: `P I14` was built and left GAP; its line
    #: stays, built.
    #: 322 since lane L5's merge: `M M10` and `M M17` were built
    #: (`linkedin_send_reply`) and left GAP; both keep their lines, built.
    #: 321 since lane L5's merge of master 66aaa95, the two over
    #: lane L7's one.
    #: 335 since lane L5's merge of master 530227e: lane Y2's fourteen
    #: admitted write rows (337 on master) less this lane's two.
    #: 356 since the P-R block was itemized, 2026-09-24: nineteen settings
    #: and data-rights rows entered, each classed R3 in the same table (16 R1,
    #: 36 R2, 306 R3 over 358 lines).
    #: 354 AT THE ORCHESTRATOR'S MERGE OF LANE Y2'S FOLLOW-UP (2026-09-27), MEASURED:
    #: the P-R settings block itemized into 22 rows (P2-P23; Delete Data EXCLUDED-RULED).
    #: 353 AT THE ORCHESTRATOR'S MERGE OF LANE L7'S P B9 (2026-09-27), MEASURED: P B9
    #: (Premium badge) moved GAP -> COVERED-UNFIRED, released like the intro edits.
    #: 378 AT LANE L8'S MERGE OF MASTER (2026-09-27), MEASURED: the returned
    #: write rows and `P A23b`, less the two built and the two re-excluded;
    #: `N 125` counted as a W row once its R/W cell read `W`.
    #: 377 AT LANE L5'S MERGE OF MASTER 52b55b6 (2026-09-27), MEASURED: `N 4`, a W row, left GAP; its write-classes line stays,
    #: built.
    #: 378 ON LANE L5'S ORDER OF 2026-09-27 23:36, MEASURED:
    #: `linkedin_send_message` RETIRED (aimed by a name): `M M2`, a W row,
    #: classed R2 in write-classes.tsv, queued on C-P5.
    #: 381 AT THE LIVE LANE'S MERGE OF MASTER c2825a4 (2026-09-28), MEASURED on the
    #: merged tree: master's figure with this branch's `P A11`, `P A13` and `P A17`
    #: COVERED-UNFIRED -> GAP (session 4: autocomplete inputs the one tool can only
    #: type into, now refused by it).
    #: 379 ON LANE K's PURCHASES-STAY-MANUAL EXCLUSIONS (2026-10-10), MEASURED:
    #: `P S9` and `M C71`, two W rows, left GAP; their write-classes lines go.
    #: 365 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED: 14 W
    #: rows left GAP; their write-classes lines go.
    #: 376 ON LANE U'S MOVE OF 2026-10-10, MEASURED:
    #: `M M14`, `M M15` and `M M18`, three W rows, left GAP; their write-classes lines go.
    #: 362 AT LANE U'S MERGE OF ORIGIN/MASTER 71d83ca, MEASURED: lane K's
    #: 365 with lane U's three rows (-3).
    #: 361 AT LANE B1'S MERGE OF ORIGIN/MASTER 0103810, MEASURED: master's figure with `P A22` GAP -> COVERED-UNFIRED (the Organization select, session 7).
    "gap_write": 361,
    #: All 54 are `jobs.md`, which has no per-row R/W column (56 until the
    #: lane-L3 merge built J 18 and J 39). Not a coincidence
    #: and not a defect in the finder: it is the whole of that slice's still-GAP
    #: population. 92 since lane R's merge, which returned 38 jobs rows.
    #: 109 AT LANE L8'S MERGE OF MASTER (2026-09-27), MEASURED: `J 69` and
    #: `J 87` returned; a jobs row carries no R/W column.
    #: 108 AT LANE S'S OFFLINE FRONTIER (2026-09-28), MEASURED: the five rows
    #: bucket 3 called blocked on nothing, taken one by one. `M M53`, `N 195`
    #: and `P S5` (three R rows ADMITTED and gated READER) and `J 107` (the one
    #: jobs row) GAP -> COVERED-UNFIRED, each built over a capture or on a
    #: shipped page and never fired, so they leave buckets 3 and 1-by-side and
    #: enter bucket 1 held by no ruling. `P K1` stays GAP and is re-gated
    #: READER -> MEASURE: no capture draws its section.
    #: 104 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED: `J
    #: 17`, `J 57`, `J 162` and `J 164` left GAP.
    "gap_unknown": 104,
    "gap_ambiguous": 0,
    #: BUCKET 3, MEASURED 2026-09-23 (`_audit/2026-09-23-bucket3-addresses.md`),
    #: counted off `_audit/_census/read-addresses.tsv`, whose every verdict
    #: `scripts/check_read_addresses.py` re-drives through the shipped
    #: boundary. The six sum to nothing on their own: the first five
    #: partition `gap_read` (33 + 24 + 2 + 6 + 2 = 67) and the sixth is the
    #: subset of the 33 a reader could be written for today. Pinned so that a
    #: row entering or leaving bucket 3, or a boundary edit that moves a
    #: verdict and is carried into the table, cannot move the headline
    #: "blocked on nothing" figure without somebody re-pinning it out loud.
    #: 44 / 38 / 1 / 13 / 2 SINCE LANE R'S MERGE (sum 98, `gap_read`): 34
    #: returned read rows entered bucket 3, each driven through the shipped
    #: boundary (ADMITTED 4, REFUSED 23, NEEDS-SESSION 7), and two left it --
    #: `N 171` (NO-ADDRESS; NOT-AN-ACT now) and `N 183` (REFUSED; a setting, so
    #: a write row). The boundary itself did not move.
    #: 40 / 38 / 1 / 13 / 2 SINCE LANE S'S MERGE (sum 94, `gap_read`): the
    #: four FILTER rows lane S built (`N 84`, `N 85`, `N 87`, `N 94`) left
    #: bucket 3 for COVERED-UNFIRED, all four ADMITTED; the boundary did not
    #: move.
    #: THE LIVE LANE'S MERGE, 2026-09-24: N 134, P O3 and M C72 were proven
    #: live and their address lines left the table; all three were ADMITTED.
    #: 36 / 38 / 1 / 13 / 2 SINCE LANE L5'S MERGE OVER THE LIVE LANE'S (sum 90,
    #: `gap_read`): `M M49` left bucket 3 for COVERED-UNFIRED, ADMITTED; the
    #: boundary did not move.
    #: 41 / 46 / 1 / 13 / 2 SINCE LANE L5'S MERGE OF MASTER 530227e (sum
    #: 103, `gap_read`): lane Y2's admitted reads, less `M M49`.
    #: 43 / 35 / 1 / 13 / 2 SINCE LANE S'S FOLLOW-UP, ITEM 1 (2026-09-24): THE
    #: BOUNDARY MOVED. `D2-SEARCH-VERTICALS-WIDENED` widened the search line
    #: to four closed words, and the three rows whose recorded page is one of
    #: the new words -- `N 104` (companies), `N 161` (groups), `N 179` (events)
    #: -- went REFUSED -> ADMITTED, each gated MEASURE (no capture exists).
    #: No row entered or left bucket 3 and no state moved; `M C70` stays
    #: REFUSED on its content-vertical address, its groups spelling now an
    #: admitted also-driven line.
    #: 49 / 29 / 1 / 13 / 2 SINCE ITEM 2 OF THE SAME FOLLOW-UP: THE BOUNDARY
    #: MOVED AGAIN. `MEMBER-ROSTERS-AS-BOUNDED-READS` put four rosters on lines
    #: of their own, and the six rows whose recorded page is one of them went
    #: REFUSED -> ADMITTED, each gated MEASURE: `N 165` and `N 177` (a group's
    #: members), `N 188` (an event's attendees), `N 102` (a company's People
    #: tab), `N 99` and `N 100` (a school's). `N 189` stays REFUSED on its
    #: filtered spelling -- the roster line takes no query -- and `N 178` on
    #: its third-party profile. No row entered or left bucket 3; no state
    #: moved.
    #: THE GATES THEN MOVED AGAIN, AND NO FIGURE HERE DID: item 3 of the same
    #: follow-up (the WHO/WHICH rule, row by row) re-gated six of the rows
    #: above MEASURE -> RULING -- `N 161`, `N 179`, `N 165`, `N 177`, `N 188`,
    #: `N 100`, whose payload is WHO or WHICH -- so "each gated MEASURE" is
    #: that commit's reading, not HEAD's. Class counts do not see a gate.
    #: 51 / 37 AT LANE S'S FOLLOW-UP MERGE OF MASTER 1902fcb (2026-09-24),
    #: MEASURED on the merged tree and not summed: master stood at 42 / 46
    #: (the live lane's three ADMITTED rows gone, and lanes L7 and Y2's rows
    #: in), and this lane's nine REFUSED -> ADMITTED lines -- the three D2
    #: verticals and the six roster rows above -- move it by +9 / -9.
    #: 50 AT THE ORCHESTRATOR'S MERGE OF LANE S INTO MASTER 96c1165 (2026-09-27),
    #: MEASURED: lane L5's merge had moved `M M49` out of bucket 3 (COVERED-UNFIRED).
    #: LANE D'S MERGE, 2026-09-24: N 132 left for COVERED-UNFIRED under D6
    #: and its line left the table; it was ADMITTED, gated RULING, so
    #: b3_blocked_on_nothing does not move.
    #: 49 AT THE ORCHESTRATOR'S MERGE OF LANE D (2026-09-27), MEASURED: `N 132`
    #: left bucket 3 (COVERED-UNFIRED under D6) and its address line went with it.
    #: 42 / 47 / 1 / 14 / 2 SINCE THE P-R BLOCK WAS ITEMIZED, 2026-09-24 (sum
    #: 106, `gap_read`): `P15` REFUSED on the forbidden substring
    #: /mypreferences/d/categories/, and `P3` NEEDS-SESSION, no committed
    #: source spelling its page. The boundary did not move.
    #: 46 AT LANE S'S NAMES ADOPTION (2026-09-27), MEASURED: `N 79`, `N 172`
    #: and `N 194` GAP -> COVERED-UNFIRED, now that
    #: `linkedin_people_search_shape(include_names=True)` returns WHO as people
    #: records (`people_results.read_result_people`, NAMES-AT-RUNTIME and the
    #: six PEOPLE-DATA-MITIGATIONS), never fired. Three R rows that were
    #: ADMITTED and gated READER in bucket 3, so they leave it and enter bucket
    #: 1 held by no ruling.
    #: 43 AT LANE S'S OFFLINE FRONTIER (2026-09-28), MEASURED: the five rows
    #: bucket 3 called blocked on nothing, taken one by one. `M M53`, `N 195`
    #: and `P S5` (three R rows ADMITTED and gated READER) and `J 107` (the one
    #: jobs row) GAP -> COVERED-UNFIRED, each built over a capture or on a
    #: shipped page and never fired, so they leave buckets 3 and 1-by-side and
    #: enter bucket 1 held by no ruling. `P K1` stays GAP and is re-gated
    #: READER -> MEASURE: no capture draws its section.
    #: 45 ON LANE L5'S ORDER OF 2026-09-28 12:32, MEASURED: `N 30`, `N 31`, `N 65`
    #: and `N 103` EXCLUDED-RULED -> GAP, their R4 ground narrowed by
    #: NAMED-PROFILE-READ-BEHIND-A-GRANT (the orchestrator's call). `N 30` and `N
    #: 31`: their lists are people searches the read door admits, gated
    #: BUILT-UNFIRED and READER.
    #: 43 ON THE ORCHESTRATOR'S ORDER OF 2026-09-28 15:10 (lane S), MEASURED:
    #: `N 30` and `N 31` GAP -> COVERED-UNFIRED, so their two ADMITTED lines
    #: left the address table (see `adjudicated`).
    #: 42 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:02 (lane S), MEASURED:
    #: `N 81` GAP -> COVERED-UNFIRED, so its ADMITTED line left the table.
    #: 43 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:46 (lane S), MEASURED:
    #: `N 26b` entered ADMITTED -- the people search filtered to his first
    #: degree -- gated MEASURE: the school and industry facets' spelling needs
    #: a capture first.
    #: 41 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED: `P
    #: J4` and `M C96` left GAP.
    #: 39 ON LANE B1 (2026-10-10), MEASURED: `P L8` and `P L1` GAP -> COVERED-UNFIRED (the analytics hub and the audience page, on session 1's captures).
    "b3_admitted": 39,
    #: 38 AT THE ORCHESTRATOR'S MERGE OF LANE Y2'S FOLLOW-UP (2026-09-27), MEASURED:
    #: the P-R settings block itemized into 22 rows (P2-P23; Delete Data EXCLUDED-RULED).
    #: 40 ON LANE L5'S ORDER OF 2026-09-28 12:32, MEASURED: `N 30`, `N 31`, `N 65`
    #: and `N 103` EXCLUDED-RULED -> GAP, their R4 ground narrowed by
    #: NAMED-PROFILE-READ-BEHIND-A-GRANT (the orchestrator's call). `N 65` and `N
    #: 103`: sections of a member's profile, a page this table's read door refuses.
    #: 38 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:46 (lane S), MEASURED:
    #: `N 25` and `N 26`, REFUSED on the connections page's query variants,
    #: left the table for COVERED-UNFIRED by D6 (see `adjudicated`).
    #: 34 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED: `P
    #: N13`, `M C95`, `M C98` and `M C99` left GAP.
    "b3_refused": 34,
    "b3_no_address": 1,
    "b3_needs_session": 14,
    "b3_undetermined": 2,
    #: ITS HISTORY ON 2026-09-23 IS THE RULINGS AND THE LIVE READINGS MOVING
    #: UNDER IT, one line per move:
    #:   5   the bucket-3 wave, which asked the boundary and not the rulings
    #:   4   while `DO-NOT-OPEN-MESSAGING` held `M M49`'s messaging page
    #:   5   after the operator's ruling (b) at 18:15 lifted it
    #:   1   the live readers wave: P O3, N 134 and M C72 each need a press
    #:       the gate does not yet reach, M C85 a caller-supplied poll
    #:       address; only M M49 was left a reader could close
    #:   12  on the census-cleanup branch, before it merged that wave: the
    #:       calls registered at 4a57b75 (D1-SEARCH-AS-READS,
    #:       OTHER-MEMBER-IDS-AS-READS) decided what eight rows were gated
    #:       RULING on; seven need only a reader (N 79, N 84, N 85, N 87,
    #:       N 94, N 172, N 194) and N 93 a live look first
    #:   8   MEASURED at the merge of the two: M M49 and those seven
    #:   9   at lane R's merge, 2026-09-24: `P K1`, returned from an
    #:       exclusion, reads the Verifications section on the admitted
    #:       /in/me/ page, and only a reader stands in its way
    #:   2   at lane S's merge, 2026-09-24: lane S built the seven people-
    #:       search readers. The four FILTER rows left for COVERED-UNFIRED;
    #:       under the WHO rule `N 79`, `N 172` and `N 194` stay GAP, re-gated
    #:       RULING on the name-free shaper doctrine, pending the operator's
    #:       question on returning names at runtime. Left: `M M49`, `P K1`
    #:   5   at lane Y2's integration, 2026-09-24: three admitted reads on pages
    #:       already admitted and loaded, each waiting only on a reader --
    #:       `P S5`, `M M53`, and `N 195`, whose third part is an AGGREGATE
    #:       that WHO-WHICH-COUNTS-ARE-NOT-DELIVERY says counts deliver
    #:   1   at lane L5's merge, 2026-09-24 (on its branch): `M M49` was built -- the read
    #:       indicator on his own last message, returned by
    #:       `linkedin_open_messaging` and `linkedin_open_thread`. Left: `P K1`
    #:   4   at lane L5's merge of master 530227e: the two together --
    #:       `P K1`, `P S5`, `M M53` and `N 195`
    #:   8   at lane S's follow-up integration, 2026-09-24: NAMES-AT-RUNTIME
    #:       (the operator's, 08:11) answered the question `N 79`, `N 172` and
    #:       `N 194` were gated RULING on. Each now waits on a name-returning
    #:       reader held to PEOPLE-DATA-MITIGATIONS, and their page is
    #:       captured (the live lane's session 1), so each is re-gated READER.
    #:       The six follow-up rows re-gated the same day went to MEASURE --
    #:       no capture exists -- and are not in this count.
    #: The gates past the boundary are re-judged BY HAND when a ruling lands;
    #: what `ruling_problems` asks on every run is only that no row blocked on
    #: nothing sits on a page a hold binds.
    #: `_audit/2026-09-23-census-cleanup.md` items 6 and 7, sections 11-13.
    #: 7 AT THE ORCHESTRATOR'S MERGE OF LANE S INTO MASTER 96c1165 (2026-09-27),
    #: MEASURED: `M M49` left bucket 3 at lane L5's merge.
    #: 4 AT LANE S'S NAMES ADOPTION (2026-09-27), MEASURED: `N 79`, `N 172` and
    #: `N 194` GAP -> COVERED-UNFIRED, now that
    #: `linkedin_people_search_shape(include_names=True)` returns WHO as people
    #: records (`people_results.read_result_people`, NAMES-AT-RUNTIME and the
    #: six PEOPLE-DATA-MITIGATIONS), never fired. Three R rows that were
    #: ADMITTED and gated READER in bucket 3, so they leave it and enter bucket
    #: 1 held by no ruling.
    #: 0 AT LANE S'S OFFLINE FRONTIER (2026-09-28), MEASURED: the five rows
    #: bucket 3 called blocked on nothing, taken one by one. `M M53`, `N 195`
    #: and `P S5` (three R rows ADMITTED and gated READER) and `J 107` (the one
    #: jobs row) GAP -> COVERED-UNFIRED, each built over a capture or on a
    #: shipped page and never fired, so they leave buckets 3 and 1-by-side and
    #: enter bucket 1 held by no ruling. `P K1` stays GAP and is re-gated
    #: READER -> MEASURE: no capture draws its section.
    #: 1 ON LANE L5'S ORDER OF 2026-09-28 12:32, MEASURED: `N 30`, `N 31`, `N 65`
    #: and `N 103` EXCLUDED-RULED -> GAP, their R4 ground narrowed by
    #: NAMED-PROFILE-READ-BEHIND-A-GRANT (the orchestrator's call). `N 31`,
    #: ADMITTED and gated READER: people search composes `connectionOf` but not
    #: LinkedIn's `network` facet, and nothing blocks building it.
    #: 0 ON THE ORCHESTRATOR'S ORDER OF 2026-09-28 15:10 (lane S), MEASURED:
    #: the facet was built and `N 31` is COVERED-UNFIRED, never fired, so
    #: bucket 3 again holds no read row blocked on nothing.
    "b3_blocked_on_nothing": 0,
    #: BUCKET 1 BY WHAT HOLDS EACH ROW, DERIVED from the census and the
    #: holds in `scripts/ruling_holds.py`, BY THE STATUS OF THE HOLD: standing,
    #: relayed, pending, or none. They sum to `unfired`, and `PINNED_B1_ROWS`
    #: below pins WHICH rows, because a count cannot see two rows swap.
    #:
    #: WHAT MOVED, AND WHY, three times on 2026-09-23:
    #:   first build          15 standing (the write ruling) + 2 standing (the
    #:                        messaging ruling) / 0 / 2 pending / 2 none --
    #:                        the bucket-1 audit's section 3, row for row
    #:   ruling (b), relayed  0 / 17 relayed (the writes and M M33, M M43) /
    #:                        2 pending / 2 none
    #:   master 53ba1b6       15 standing / 0 / 0 / 6 none. The register made
    #:                        `OPERATOR-NAMES-THE-TARGET` STANDING (+15 here);
    #:                        `OWN-INBOX-READS-COVERED-BY-B` released M M33 and
    #:                        M M43 and the notifications question was answered
    #:                        PERMITTED, releasing N 20 and N 45 (+4 to none).
    #:   master 4a57b75       9 standing / 0 / 0 / 12 none, 6 of them RELEASED
    #:                        writes: SELF-PROFILE-EDITS-NOT-OUTWARD took the
    #:                        six edits to his own profile fields (P A8, A11,
    #:                        A13, A17, A19, A21) out of the write hold, each
    #:                        cell citing it with RELEASED BY (-6 standing,
    #:                        +6 none).
    #:   merge of master      9 standing / 0 / 0 / 15 none, 6 released, of 24:
    #:   cab6995              lanes L1 and L3 had built three reads no ruling
    #:                        holds (P G6; J 18, J 39), +3 none.
    #:   merge of lane L4     10 standing / 0 / 0 / 15 none, 6 released, of 25:
    #:                        N 47 was built, a W row, held by the write hold
    #:                        with no marker (+1 standing).
    #:   lane R's merge       10 standing / 0 / 0 / 16 none, 6 released, of 26:
    #:                        N 23 was returned from an exclusion to
    #:                        COVERED-UNFIRED, a read no ruling holds (+1 none).
    #:   lane S's merge       10 standing / 0 / 0 / 20 none, 6 released, of 30:
    #:                        the four people-search FILTER readers (N 84,
    #:                        N 85, N 87, N 94), reads no ruling holds -- D1
    #:                        and OTHER-MEMBER-IDS permit, they hold nothing
    #:                        (+4 none).
    #:   live lane merge      10 standing / 0 / 0 / 19 none, 6 released, of 29:
    #:   (2026-09-24)         P G6 fired live and was banked COVERED-PROVEN,
    #:                        leaving bucket 1 (-1 none).
    #:   lane L7's merge      11 standing / 0 / 0 / 19 none, 6 released, of 30:
    #:   (2026-09-24)         P I14 was built, a W row, held by the write hold
    #:                        with no marker (+1 standing).
    #:   lane Y2's integration 11 standing / 0 / 0 / 20 none, 6 released, of 31:
    #:   (after lane L7's     `J 158`, a read no ruling holds, entered
    #:   merge)               COVERED-UNFIRED (+1 none).
    #:   lane L5's merge      12 standing / 0 / 0 / 20 none, 6 released, of 32,
    #:   (over the live lane) measured on the tree merged with 9b9a4d0:
    #:                        the reply, `M M10` and by D6 `M M17`, two W rows
    #:                        the write hold binds with no marker (+2
    #:                        standing); `M M49`, a read no ruling holds (+1
    #:                        none).
    #:   lane L5's third      13 standing / 0 / 0 / 20 none, 6 released, of 33,
    #:   merge (over L7)      measured on the tree merged with 66aaa95: the
    #:                        same three rows over lane L7's figures.
    #:   lane L5's fourth     13 standing / 0 / 0 / 21 none, 6 released, of 34,
    #:   merge (over Y2)      measured on the tree merged with 530227e:
    #:                        `J 158` and this lane's three rows together.
    #:   lane D's merge       11 standing / 0 / 0 / 21 none, 6 released, of 32:
    #:   (2026-09-24)         N 132 GAP -> COVERED-UNFIRED under D6, a read no
    #:                        ruling holds (+1 none). Counted on the tree merged
    #:                        with master 530227e, after lane Y2's line above.
    #:   lane L7's P B9       13 standing / 0 / 0 / 22 none, 7 released,
    #:   build (over 0e4f4b3)  measured on the merged tree: `P B9`, a W row
    #:                        whose cell cites RELEASED BY
    #:                        SELF-PROFILE-EDITS-NOT-OUTWARD (+1 none,
    #:                        +1 released).
    #:   lane L5's follow-up  15 standing / 0 / 0 / 23 none, 7 released, of 38,
    #:   (merge of 2eb90ad,   measured on the merged tree: `M M1` and `N 4`,
    #:   2026-09-27)          two W rows the write hold binds with no marker
    #:                        (+2 standing) -- Message and Connect on the
    #:                        profile of a person he names.
    #:   lane L5's merge      18 standing / 0 / 0 / 23 none, 7 released, of 41,
    #:   of master 52b55b6    measured on the merged tree: master's 15 (lane
    #:   (2026-09-27)         L8's `M C63` and `N 64` in) with this lane's
    #:                        `M M1` and `N 4`, and `N 2`, moved at the merge
    #:                        (+3 standing).
    #: `b1_relayed` is the count this file called `b1_named_target` until the
    #: target condition was registered: a name for what a status COUNTS, not
    #: for which ruling happens to have it today. `b1_released` is a SUBSET of
    #: `b1_no_ruling`: the writes held by nothing because a release says so.
    #: 15 AT LANE L8'S MERGE OF MASTER (2026-09-27), MEASURED: `M C63` and
    #: `N 64` entered bucket 1, W rows the write hold binds with no marker
    #: (OPERATOR-NAMES-THE-TARGET).
    #: 18 AT LANE L5'S MERGE OF MASTER 52b55b6 (2026-09-27), MEASURED: `M M1`, `N 4` and `N 2`, three W rows the write hold
    #: binds with no marker (OPERATOR-NAMES-THE-TARGET).
    #: 19 ON LANE L5'S ORDER OF 2026-09-27 23:36, MEASURED:
    #: `linkedin_send_message` RETIRED (aimed by a name): `N 155` entered
    #: bucket 1, held by OPERATOR-NAMES-THE-TARGET.
    #: 18 AT THE LIVE LANE'S SESSION 5 (2026-09-28), MEASURED: `M M1` (sent on the
    #: first-contact path, verified) and `P B9` (both directions, one restore
    #: failed before the recovery held) fired live and banked.
    #: 17 AT THE LIVE LANE'S SESSION 6 (2026-09-28), MEASURED: `M M17` (the reply
    #: with its emoji, sent and verified), `M M33` (the starred pill applied), `M M49`
    #: (the read indicator read) and `P A21`, `P A19` (tested and restored exactly)
    #: fired live and banked.
    #: 16 AT THE LIVE LANE'S SESSION 7 (2026-10-10), MEASURED: `N 25` (a
    #: 1st-degree connection found by name), `N 81` (the degree facet applied to
    #: the results) and `N 26` (his connections filtered by place) fired live and
    #: banked; `N 155` moved on the orchestrator's call of that day, by D6 on
    #: `M M1`'s session-5 send.
    #: 12 AT THE LIVE LANE'S SESSION 8 (2026-10-10), MEASURED: `N 48` and `J 104`
    #: (the unfollow through LinkedIn's confirmation, the row gone and a posting
    #: reading not-following) and `N 46` and `J 103` (the follow from a posting
    #: that restored it, verified on Manage Pages) fired live and banked.
    #: 19 ON LANE U'S MOVE OF 2026-10-10, MEASURED:
    #: `M M14`, `M M15` and `M M18` entered, held by OPERATOR-NAMES-THE-TARGET.
    #: 15 AT LANE U'S MERGE OF ORIGIN/MASTER 1027bf8, MEASURED: session 8's
    #: four banked out (16 - 4) and lane U's three in (+ 3).
    "b1_standing": 15,
    "b1_relayed": 0,
    "b1_pending": 0,
    #: 22 AT THE ORCHESTRATOR'S MERGE OF LANE D (2026-09-27), MEASURED: lane D
    #: moved `N 132` GAP -> COVERED-UNFIRED under D6-CAPABILITY-OVER-AFFORDANCE.
    #: 23 AT THE ORCHESTRATOR'S MERGE OF LANE L7'S P B9 (2026-09-27), MEASURED: P B9
    #: (Premium badge) moved GAP -> COVERED-UNFIRED, released like the intro edits.
    #: 26 AT LANE S'S NAMES ADOPTION (2026-09-27), MEASURED: `N 79`, `N 172`
    #: and `N 194` GAP -> COVERED-UNFIRED, now that
    #: `linkedin_people_search_shape(include_names=True)` returns WHO as people
    #: records (`people_results.read_result_people`, NAMES-AT-RUNTIME and the
    #: six PEOPLE-DATA-MITIGATIONS), never fired. Three R rows that were
    #: ADMITTED and gated READER in bucket 3, so they leave it and enter bucket
    #: 1 held by no ruling.
    #: 30 AT LANE S'S OFFLINE FRONTIER (2026-09-28), MEASURED: the five rows
    #: bucket 3 called blocked on nothing, taken one by one. `M M53`, `N 195`
    #: and `P S5` (three R rows ADMITTED and gated READER) and `J 107` (the one
    #: jobs row) GAP -> COVERED-UNFIRED, each built over a capture or on a
    #: shipped page and never fired, so they leave buckets 3 and 1-by-side and
    #: enter bucket 1 held by no ruling. `P K1` stays GAP and is re-gated
    #: READER -> MEASURE: no capture draws its section.
    #: 18 AT THE LIVE LANE'S SESSION 2 (2026-09-28), MEASURED: twelve of the
    #: thirty fired live and banked, each on its own cell's bar, so they left
    #: bucket 1 -- `J 18`, `J 39`, `J 158`, `M M43`, `N 23`, `N 79`, `N 84`,
    #: `N 87`, `N 94`, `N 132`, `N 195`, `P S5`. `J 107`, `M M53`, `N 20` and
    #: `N 45` fired and stay: not banked, each cell says why.
    #: 15 AT THE LIVE LANE'S SESSION 3 (2026-09-28), MEASURED: `J 107`, `M M53`
    #: and `N 194` fired live and banked, each on its own cell's bar.
    #: 17 ON THE ORCHESTRATOR'S ORDER OF 2026-09-28 15:10 (lane S), MEASURED:
    #: `N 30` and `N 31` entered, two reads no ruling holds, each fired only
    #: at a member he names (see `adjudicated`).
    #: 18 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:02 (lane S), MEASURED:
    #: `N 81` entered, a read no ruling holds, which names nobody.
    #: 20 ON THE ORCHESTRATOR'S CALL OF 2026-09-28 17:46 (lane S), MEASURED:
    #: `N 25` and `N 26` entered, reads no ruling holds (see `adjudicated`).
    #: 17 AT THE LIVE LANE'S MERGE OF MASTER c2825a4 (2026-09-28), MEASURED on the
    #: merged tree: master's figure with this branch's `P A11`, `P A13` and `P A17`
    #: COVERED-UNFIRED -> GAP (session 4: autocomplete inputs the one tool can only
    #: type into, now refused by it).
    #: 16 AT THE LIVE LANE'S SESSION 5 (2026-09-28), MEASURED: `M M1` (sent on the
    #: first-contact path, verified) and `P B9` (both directions, one restore
    #: failed before the recovery held) fired live and banked.
    #: 12 AT THE LIVE LANE'S SESSION 6 (2026-09-28), MEASURED: `M M17` (the reply
    #: with its emoji, sent and verified), `M M33` (the starred pill applied), `M M49`
    #: (the read indicator read) and `P A21`, `P A19` (tested and restored exactly)
    #: fired live and banked.
    #: 9 AT THE LIVE LANE'S SESSION 7 (2026-10-10), MEASURED: `N 25` (a
    #: 1st-degree connection found by name), `N 81` (the degree facet applied to
    #: the results) and `N 26` (his connections filtered by place) fired live and
    #: banked; `N 155` moved on the orchestrator's call of that day, by D6 on
    #: `M M1`'s session-5 send.
    #: 5 AT THE LIVE LANE'S SESSION 9 (2026-10-10), MEASURED: `N 30`, `N 85`
    #: and `N 172` (a named member's connections, as people, by the
    #: Connections-of filter) and `N 31` (the connections he and that member
    #: share) fired live, read-only, and banked.
    #: 8 AT LANE B1'S MERGE OF ORIGIN/MASTER 6c65815, MEASURED on the merged tree: master's figure (session 9) with lane B1's `P A22`, `P L8` and `P L1` COVERED-UNFIRED (+3).
    "b1_no_ruling": 8,
    #: 7 AT THE ORCHESTRATOR'S MERGE OF LANE L7'S P B9 (2026-09-27), MEASURED: P B9
    #: (Premium badge) moved GAP -> COVERED-UNFIRED, released like the intro edits.
    #: 4 AT THE LIVE LANE'S MERGE OF MASTER c2825a4 (2026-09-28), MEASURED on the
    #: merged tree: master's figure with this branch's `P A11`, `P A13` and `P A17`
    #: COVERED-UNFIRED -> GAP (session 4: autocomplete inputs the one tool can only
    #: type into, now refused by it).
    #: 3 AT THE LIVE LANE'S SESSION 5 (2026-09-28), MEASURED: `M M1` (sent on the
    #: first-contact path, verified) and `P B9` (both directions, one restore
    #: failed before the recovery held) fired live and banked.
    #: 1 AT THE LIVE LANE'S SESSION 6 (2026-09-28), MEASURED: `M M17` (the reply
    #: with its emoji, sent and verified), `M M33` (the starred pill applied), `M M49`
    #: (the read indicator read) and `P A21`, `P A19` (tested and restored exactly)
    #: fired live and banked.
    #: 2 ON LANE B1 (2026-10-10), MEASURED: `P A22` GAP -> COVERED-UNFIRED (the Organization select, session 7).
    "b1_released": 2,
    #: D3's enumerated list: FOUR once `M C83` left it, and THREE since
    #: `N 172` left it the same evening on OTHER-MEMBER-IDS-AS-READS -- see
    #: `RULING_BLOCKED_NAMED`. It was printed as "five rows" and pinned
    #: nowhere, which is how a list edit could have moved it silently.
    #: ZERO since lane R's merge, 2026-09-24: D3 is answered
    #: (D3-UNREGISTERED-REFUSAL-IS-NOT-A-RULING), the list is empty, and the
    #: three rows are GAP blocked on an admission and a reader.
    "b2_d3_rows": 0,
    #: THE JOBS SLICE BY SIDE TABLE, 2026-09-23 (lane L3), counted off
    #: `_audit/_census/jobs-directions.tsv`, whose every verdict and deciding
    #: phrase `scripts/check_jobs_directions.py` re-checks. `jobs_gap` equals
    #: `gap_unknown` and the three directions partition it; the five classes
    #: partition its R + R+W rows (26 + 3 = 29). Kept OUT of `gap_read` and
    #: `gap_write` deliberately: `gap_read` feeds bucket 3, whose address
    #: table does not carry jobs rows.
    #: 92 SINCE LANE R'S MERGE, 2026-09-24: 38 jobs rows returned, each given
    #: a line -- directions R 7, W 28, R+W 3 (so 33 / 53 / 6), and of the ten
    #: with a read half ADMITTED 2 (`J 17`, `J 115`), REFUSED 7, NEEDS-SESSION
    #: 1 (`J 134`). 11 + 26 + 0 + 2 + 0 = 39 = 33 + 6.
    #: 13 / 24 SINCE LANE S'S FOLLOW-UP, ITEM 2 (2026-09-24): THE BOUNDARY
    #: MOVED. `MEMBER-ROSTERS-AS-BOUNDED-READS` put the company and school
    #: People tabs on lines of their own, and the two jobs rows whose recorded
    #: page is one of them went REFUSED -> ADMITTED, gated MEASURE: `J 108`
    #: (the company People tab) and `J 112` (a school's alumni tab). No row
    #: left the table and no state moved. 13 + 24 + 0 + 2 + 0 = 39.
    #: 107 / 41 / 58 / 8 AND 13 / 34 AT LANE S'S FOLLOW-UP MERGE OF MASTER
    #: 1902fcb, MEASURED on the merged tree: master's lanes had grown the
    #: table to 107 rows (11 admitted, 36 refused), and this lane's two
    #: People-tab rows move it by +2 / -2. 13 + 34 + 0 + 2 + 0 = 49 = 41 + 8.
    #: 109 AT LANE L8'S MERGE OF MASTER (2026-09-27), MEASURED: `J 69` and
    #: `J 87` returned to GAP, each given a line in jobs-directions.tsv.
    #: 108 AT LANE S'S OFFLINE FRONTIER (2026-09-28), MEASURED: the five rows
    #: bucket 3 called blocked on nothing, taken one by one. `M M53`, `N 195`
    #: and `P S5` (three R rows ADMITTED and gated READER) and `J 107` (the one
    #: jobs row) GAP -> COVERED-UNFIRED, each built over a capture or on a
    #: shipped page and never fired, so they leave buckets 3 and 1-by-side and
    #: enter bucket 1 held by no ruling. `P K1` stays GAP and is re-gated
    #: READER -> MEASURE: no capture draws its section.
    #: 104 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED: `J
    #: 17`, `J 57`, `J 162` and `J 164` left GAP.
    "jobs_gap": 104,
    #: 40 AT LANE S'S OFFLINE FRONTIER (2026-09-28), MEASURED: the five rows
    #: bucket 3 called blocked on nothing, taken one by one. `M M53`, `N 195`
    #: and `P S5` (three R rows ADMITTED and gated READER) and `J 107` (the one
    #: jobs row) GAP -> COVERED-UNFIRED, each built over a capture or on a
    #: shipped page and never fired, so they leave buckets 3 and 1-by-side and
    #: enter bucket 1 held by no ruling. `P K1` stays GAP and is re-gated
    #: READER -> MEASURE: no capture draws its section.
    #: 38 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED: `J
    #: 17` and `J 57`.
    "jobs_dir_r": 38,
    #: 60 AT LANE L8'S MERGE OF MASTER (2026-09-27), MEASURED: `J 69` and
    #: `J 87`, both W.
    #: 58 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED: `J
    #: 162` and `J 164`.
    "jobs_dir_w": 58,
    "jobs_dir_rw": 8,
    #: 12 AT LANE S'S OFFLINE FRONTIER (2026-09-28), MEASURED: the five rows
    #: bucket 3 called blocked on nothing, taken one by one. `M M53`, `N 195`
    #: and `P S5` (three R rows ADMITTED and gated READER) and `J 107` (the one
    #: jobs row) GAP -> COVERED-UNFIRED, each built over a capture or on a
    #: shipped page and never fired, so they leave buckets 3 and 1-by-side and
    #: enter bucket 1 held by no ruling. `P K1` stays GAP and is re-gated
    #: READER -> MEASURE: no capture draws its section.
    #: 10 ON LANE K's APPLICATION OF THE RULINGS OF 2026-10-10, MEASURED: `J
    #: 17` and `J 57`, both on admitted pages.
    "jobs_admitted": 10,
    "jobs_refused": 34,
    "jobs_no_address": 0,
    "jobs_needs_session": 2,
    "jobs_undetermined": 0,
    #: 1 since lane D's merge, 2026-09-24: `J 107` (the Company Page Jobs tab)
    #: was re-gated RULING -> READER. D6 applied, and the replacing route,
    #: `linkedin_search_jobs(company_id=...)`, refuses a call with no keyword,
    #: so what stands in the way is that guard in the tool -- no ruling, no
    #: boundary edit and no press.
    #: 0 AT LANE S'S OFFLINE FRONTIER (2026-09-28), MEASURED: the five rows
    #: bucket 3 called blocked on nothing, taken one by one. `M M53`, `N 195`
    #: and `P S5` (three R rows ADMITTED and gated READER) and `J 107` (the one
    #: jobs row) GAP -> COVERED-UNFIRED, each built over a capture or on a
    #: shipped page and never fired, so they leave buckets 3 and 1-by-side and
    #: enter bucket 1 held by no ruling. `P K1` stays GAP and is re-gated
    #: READER -> MEASURE: no capture draws its section.
    "jobs_blocked_on_nothing": 0,
}

#: BUCKET 1, ROW BY ROW -- the control that goes RED WHEN A ROW MOVES, and
#: names it. `bucket1_moves()` compares every COVERED-UNFIRED row's DERIVED
#: hold with this table: a row entering or leaving the state, or changing
#: hold, is reported by id. Re-pin only in the commit that says why it moved.
PINNED_B1_ROWS: dict[str, tuple[str, ...]] = {
    #: `N 47` entered with the lane-L4 merge, 2026-09-23: a write to an
    #: organisation Page, built offline and never fired, held until the
    #: operator names the Page -- the same hold as its twin `N 48`.
    #: `P I14` entered with lane L7's merge, 2026-09-24: "I'm interested",
    #: built offline and never fired; it tells one employer's recruiters, so
    #: it fires only at a company he names -- and, on the orchestrator's call,
    #: only once `P I15`'s undo control has been captured.
    #: `M M10` and `M M17` entered with lane L5's merge, 2026-09-24: the
    #: reply inside a conversation he names (`linkedin_send_reply`), built
    #: offline and never fired; `M M17` rests on it by D6 (an emoji is a
    #: character of the words it types). Held until he names the
    #: conversation and the words.
    #: `M C63` and `N 64` entered AT LANE L8'S MERGE OF MASTER (2026-09-27),
    #: MEASURED: leaving one group he names (`linkedin_withdraw_from_group`),
    #: one capability counted twice, built offline under
    #: OUTWARD-CLASSES-BUILT-BEHIND-GRANTS and never fired. Held until he names
    #: the group -- by numeric id, and not his last membership.
    #: `M M1`, `N 2` and `N 4` entered AT LANE L5'S MERGE OF MASTER 52b55b6
    #: (2026-09-27), MEASURED: Message and Connect on the profile of a person he
    #: names by link or member id (`linkedin_message_from_profile`,
    #: `linkedin_connect_from_profile`; `N 4` by D6, `N 2` on the orchestrator's
    #: application of THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET), built offline and
    #: never fired. Held until he names the person -- never a stranger.
    #: `N 155` entered ON LANE L5'S ORDER OF 2026-09-27 23:36, MEASURED:
    #: COVERED-CANNOT-DELIVER -> COVERED-UNFIRED once `linkedin_send_message`
    #: was RETIRED (aimed by a name) -- the same capability as `M M1`, on
    #: `linkedin_message_from_profile`, never fired. Held until he names the
    #: person.
    #: `M M1` LEFT AT THE LIVE LANE'S SESSION 5 (2026-09-28): sent to the target
    #: he named, on the first-contact path, and verified -- COVERED-PROVEN.
    #: `M M17` LEFT AT SESSION 6 (2026-09-28): the reply in that conversation,
    #: its emoji among his words, sent and verified -- COVERED-PROVEN.
    #: `N 155` LEFT ON THE ORCHESTRATOR'S CALL OF 2026-10-10, by D6 on `M M1`'s
    #: session-5 send to a first-degree connection -- COVERED-PROVEN.
    #: `N 48`, `J 104`, `N 46` and `J 103` LEFT AT SESSION 8 (2026-10-10): the
    #: first-by-rule Page unfollowed through LinkedIn's confirmation and followed
    #: again from one of its postings, each verified -- COVERED-PROVEN.
    #: `M M14`, `M M15` and `M M18` entered ON LANE U'S MOVE OF 2026-10-10,
    #: MEASURED: one file from the declared upload root into one conversation
    #: he names (`linkedin_send_attachment`), built offline under the
    #: operator's upload decision (FILE-UPLOAD-OPENED) and never fired; a
    #: photo, a video and a document each aimed at its own input on the live
    #: lane's session-8 composer capture. Held until he names the conversation
    #: and the file.
    "OPERATOR-NAMES-THE-TARGET": (
        "J 128",
        "M C1", "M C25", "M C32", "M C63", "M M10", "M M14", "M M15", "M M18",
        "N 1", "N 2", "N 4", "N 47", "N 64",
        "P I14",
    ),
    #: `J 18` and `J 39` entered with the lane-L3 merge, 2026-09-23: reads
    #: built offline, which no ruling holds. The six P A rows are the writes
    #: SELF-PROFILE-EDITS-NOT-OUTWARD releases, each by its own cell.
    #: `N 23` entered with lane R, 2026-09-23: returned from an exclusion to
    #: COVERED-UNFIRED, because `linkedin_connections` already reads his
    #: connections list behind a before-and-after badge gate and no live fire
    #: is on record. A read of his own list, which no ruling holds.
    #: `N 84`, `N 85`, `N 87` and `N 94` entered with lane S's merge,
    #: 2026-09-24: people-search FILTER readers built offline and never
    #: fired, from the tool's arguments under D1-SEARCH-AS-READS (and, for
    #: `N 85`, OTHER-MEMBER-IDS-AS-READS). Both rulings permit; neither holds.
    #: `P G6` entered with the lane-L1 merge and LEFT with the live lane's
    #: merge, 2026-09-24: fired live and banked COVERED-PROVEN.
    #: `J 158` entered at lane Y2's integration, 2026-09-24: admitted at GAP,
    #: then COVERED-UNFIRED on the orchestrator's delegated call --
    #: `linkedin_premium_job_collection(1)` reaches it, its reader read the
    #: page live on 2026-09-20, and the tool's call at index 1 never fired.
    #: `M M49` entered with lane L5's merge, 2026-09-24: the read indicator on
    #: his own last message, read off his own inbox with no target
    #: (OWN-INBOX-READS-COVERED-BY-B permits; it holds nothing).
    #: `N 132` entered with lane D's merge, 2026-09-24: the switch between
    #: Search appearances and Who viewed your profile, discharged under D6 by
    #: two shipped tools, one of which has never been called live. A read of
    #: his own analytics, which no ruling holds.
    #: `P B9` entered with lane L7's P B9 build, 2026-09-24, integrated over
    #: master 0e4f4b3: the Premium badge switch, built offline and never
    #: fired, a write its own cell releases by SELF-PROFILE-EDITS-NOT-OUTWARD --
    #: the seventh, beside the six P A rows.
    #: `N 79`, `N 172` and `N 194` entered with lane S's names adoption,
    #: 2026-09-27: the people search returns WHO as people records when its
    #: caller passes include_names (`people_results.read_result_people`),
    #: built offline over the one captured results page and never fired.
    #: NAMES-AT-RUNTIME and PEOPLE-DATA-MITIGATIONS permit and shape it;
    #: neither holds it.
    #: TWELVE LEFT AT THE LIVE LANE'S SESSION 2, 2026-09-28, MEASURED: `J 18`,
    #: `J 39`, `J 158`, `M M43`, `N 23`, `N 79`, `N 84`, `N 87`, `N 94`,
    #: `N 132`, `N 195` and `P S5` fired live and banked COVERED-PROVEN, each
    #: on its own cell's bar (`_audit/2026-09-23-live-lane-session-1.md`,
    #: "Live session 2, 2026-09-28"). `J 107`, `M M53`, `N 20` and `N 45`
    #: fired and stay here, not banked; `M M33`, `M M49`, the six P A rows and
    #: `P B9` did not fire.
    #: `N 30` and `N 31` entered on the orchestrator's order of 2026-09-28
    #: 15:10 (lane S): the people searches a first-degree profile's topcard
    #: links to -- a member's connections (`N 30`, by D6 on his ruling) and
    #: the ones he shares with them (`N 31`, the new `network` facet) --
    #: composed from the tool's arguments and never fired. Reads no ruling
    #: holds; each fires only at a member he names.
    #: `N 81` entered on the orchestrator's call of 2026-09-28 17:02 (lane S):
    #: the same `network` facet alone, a people search filtered by degree, as
    #: the connections page writes it; never fired. A read no ruling holds.
    #: `N 25` and `N 26` entered on his call of 17:46 (lane S), by D6 on that
    #: degree filter: a name search of his first degree, and his first degree
    #: filtered by place or employer; never fired. Reads no ruling holds.
    NO_RULING: (
        #: `P L8` and `P L1` entered on lane B1 (2026-10-10): his analytics hub's
        #: metric cards (`linkedin_analytics_hub`) and his audience page's follower
        #: count and demographics (`linkedin_audience_analytics`), each read off one
        #: admitted page over the tracked skeleton of session 1's capture; never
        #: fired. Reads of his own analytics, which no ruling holds.
        "P L1", "P L8",
        #: `P A22` entered on lane B1 (2026-10-10): the intro editor's
        #: Organization select, drawn since session 7, chosen and put back by
        #: `linkedin_update_profile_field` over the tracked copy of that capture;
        #: never fired. RELEASED BY SELF-PROFILE-EDITS-NOT-OUTWARD, beside `P A8`.
        "P A22",
        "J 121", "J 122",
        "N 20", "N 45",
        "P A8",
        #: `J 107` and `M M53` entered with lane S's offline frontier,
        #: 2026-09-28, fired at session 2 without banking, and LEFT at
        #: session 3 (2026-09-28), fired again and banked -- with `N 194`.
        #: `P A11`, `P A13` and `P A17` LEFT at session 4 (2026-09-28) for GAP:
        #: autocomplete inputs, which the one tool can only type into.
        #: `P B9` LEFT at session 5 (2026-09-28): both directions measured live.
        #: `M M33`, `M M49`, `P A21` and `P A19` LEFT at session 6 (2026-09-28), fired
        #: live and banked, the two edits tested and restored exactly.
        #: `N 25`, `N 81` and `N 26` LEFT at session 7 (2026-10-10), fired live and
        #: banked: the name search, the degree facet, the place filter.
        #: `N 30`, `N 85`, `N 172` and `N 31` LEFT at session 9 (2026-10-10),
        #: fired live at the member he named, read-only, and banked: his
        #: connections as people, and the ones the two of them share.
    ),
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="The completion decomposition.")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any headline figure has moved off its pin")
    args = ap.parse_args(argv)

    rows = list(walk())
    problems = control(rows)
    if problems:
        print("REFUSING TO REPORT -- a control failed, so no figure below "
              "would mean anything:")
        for problem in problems:
            print(f"  {problem}")
        return 1

    out: list[str] = []
    figures = report(rows, out)
    print("\n".join(out))

    moved = {k: (PINNED[k], v) for k, v in figures.items()
             if k in PINNED and PINNED[k] != v}
    print()
    print("=" * 78)
    if moved:
        print(f"{len(moved)} PINNED FIGURE(S) MOVED:")
        for key, (was, now) in sorted(moved.items()):
            print(f"    {key:22s} pinned {was:5d}   now {now:5d}   "
                  f"({now - was:+d})")
        print("  Every document quoting one of these is now quoting a number "
              "that is\n  no longer true. Re-pin in the same commit that says "
              "what moved.")
    else:
        print("every headline figure matches its pin")
    missing = sorted(set(PINNED) - set(figures))
    if missing:
        print(f"  PINS WITH NO FIGURE TO CHECK: {missing} -- a pin that "
              f"checks nothing is worse than none.")
        moved = moved or {"_": (0, 1)}
    holds, _problems = bucket1_holds(rows)
    b1_moved = bucket1_moves(holds) if holds is not None else []
    if b1_moved:
        print(f"{len(b1_moved)} BUCKET-1 ROW(S) MOVED OFF THEIR PINNED HOLD:")
        for line in b1_moved:
            print(f"    {line}")
        print("  Re-pin PINNED_B1_ROWS in the same commit that says why.")
    return 1 if (args.check and (moved or missing or b1_moved)) else 0


if __name__ == "__main__":
    sys.exit(main())
