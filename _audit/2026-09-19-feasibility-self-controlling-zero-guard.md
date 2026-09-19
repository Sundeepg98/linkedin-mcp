# FEASIBILITY: a guard for the self-controlling zero — NOT TRACTABLE, and the proof is a row

**THE ANSWER IS NO, and it took an hour rather than a day.** A mechanical guard
enforcing *"a row whose evidence is an absence must cite a presence from the same
read"* cannot be built over census cells without semantics. Three measurements
say so, and a real row demonstrates the failure of the best candidate design.

**Nothing was built. No cell was edited. No form was invented.**

---

## 1. A CELL IS NOT A READ, AND THAT IS THE WHOLE PROBLEM

The law binds a zero to a positive **from the same read**. A guard must
therefore recover which read a number came from. Measured over 698 census rows:

    cells carrying 0 distinct dates    551   (79%)
    carrying 1                         110   (16%)
    carrying 2                          27   (4%)
    carrying 3                           9   (1%)
    carrying 4                           1

**37 cells demonstrably span two or more reads**, and **79% carry no date at
all**, so for four rows in five the read is unrecoverable by any means. A census
cell is an **accumulation** — `jobs 9` carries measurements from 2026-09-04,
-09-05 and -09-19 in one string.

**"Same read" is exactly the relation that is not in the text.**

## 2. THE POSITIVE IS HARDER TO FIND THAN THE ZERO, AND FINDING IT DOES NOT HELP

62 of 698 rows (9%) assert a zero lexically. Detecting a *count* among them
means stripping help-article ids (`a541878`), commit shas, dates, `file.py:line`
references, section numbers, ruling ids, row ids and percentages. **That is
doable** — after stripping, 39 of the 62 retain a positive number.

**And it proves nothing.** `jobs 9`'s surviving positives are `6` (from *"6
tests"*) and `13` (from *"13 loads"*) — **both real counts, and neither from the
same read as that row's zero.** A guard satisfied by them would certify a
pairing that does not exist.

> **The tractable half is the useless half.** Finding a positive in the cell is
> mechanical; establishing that it belongs to the zero's read is not.

## 3. THE BEST NARROW DESIGN FAILS ON A REAL ROW — and the row is the good one

The brief's suggested escape is a recognisable measured-form. One is already
emerging organically: **`**MEASURED <date>`, six instances, all written today.**
So the convention exists and I did not have to invent it.

Guarding it — *within a `MEASURED` block, if any count is 0 at least one must be
greater than 0* — **fires on `network.md` row 174**, whose text reads:

> ***MEASURED AND DELIBERATELY NOT CLOSED — A ZERO CANNOT SETTLE THIS ROW.***

**That is the one row in the corpus doing exactly the right thing.** Its author
measured a zero, recognised it could not carry a verdict, and said so. The guard
fires on it because the row contains a zero and no positive — which is the
correct lexical reading and the wrong conclusion.

**The distinction the guard needs is between a zero that CARRIES A VERDICT and a
zero that is MENTIONED.** That is semantic, and this is the fourth semantic
sweep this week to founder on the same rock.

**It is also the discriminator problem recurring one level down.** I spent this
round separating *a row that states a ruling's premise and files GAP anyway*
(`M C69`, a propagation failure) from *a row that argues the ruling does not
reach it* (`P E6`, a considered exception) — **and no mechanical test separated
those either.** A guard for zeros needs the same judgement and has the same
ceiling.

## 4. WHAT WOULD MAKE IT TRACTABLE, stated so the cost is visible

Only a form that binds the pair **structurally**, so the author asserts the
same-read relation rather than a parser inferring it:

    MEASURED 2026-09-19 <instrument>: aria-expanded 0; aria-haspopup 0; fields 11; labelled 8

A guard over that is trivial, purely lexical, and real. **The cost is that it
governs nothing until waves write it**, and the corpus has **six** free-prose
`MEASURED` blocks, none parseable past its heading — my own block extractor
could not even find their ends.

**I did not create that form.** Inventing a notation nobody cites is precisely
the failure measured this morning: one shipped ruling already wears **three**
names across three slices, and the reason it never propagated is that each wave
coined its own. **A fourth notation with no adopters would repeat that at the
schema level**, and the decision to mint one belongs to whoever can also require
its use.

## 5. WHAT IS REAL AND SURVIVES

The law is sound and paid for itself today — every profile row of mine survived
a retracted shell report because each carried a positive from the same read
(*"a shell cannot draw a labelled form"*; *"a shell returns `named=0`"*).

**It is enforceable by a reader and not by a parser**, and the honest form is a
review question rather than a test:

> **When a row's verdict rests on a zero, what positive from the same read shows
> the surface was there?**

**That is a better outcome than a guard that fires on `network.md` 174.** A
check that convicts the most careful row in the corpus would train waves to
write vaguer notes, which is the opposite of the law's purpose.

## 6. WHAT I DID NOT DO

No guard written, no test admitted, no census cell touched, no notation minted.
**The 79 prose-only rows were not graded** — that is the larger job the brief
explicitly excluded, and this result does not change its size.
