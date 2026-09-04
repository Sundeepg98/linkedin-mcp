# Lead record, 2026-09-03 night into 2026-09-04 morning

Written by the orchestrating session, not by a wave. The waves' own records are
in `_audit/_scratch/_progress-*.md`; the instruments are in
`_audit/INSTRUMENTS.md`. This file holds what only the lead saw: the errors the
lead made, and the laws that came out of them.

## 1. The theme: checks that were present, looked correct, and could not fire

**Ten in two days**, by the waves' own running count. Not one announced itself;
every one was found by aiming an instrument at a sample that had to fail.

| # | check | why it could not fire |
|---|---|---|
| 1 | `test_readonly.py:170` | `assert total == len(X) == 4` — a chained comparison hides a constant inside what reads as a relation |
| 2 | a skill-name test | its helper re-implements the loop, so it guards the test's own copy |
| 3 | a headline test | the parser returns before the exclusion clause is ever consulted, on both fixtures |
| 4 | a wave's own test | reported green off a `-k` selector that never matched it |
| 5 | `off_navigations` | `drive` closed over one list, so the second call returned the first's; it read the ON url as the OFF url and **passed asserting nothing** |
| 6 | `output_violations` | `_redact` could be DELETED and it stayed green — one sink (`print`), and the emitter was a closure |
| 7 | `CENSUS_CONTROL_SELECTOR` | no menu role at all, so a delta gate pointed at a menu reports a clean absence |
| 8 | `test_comment_delta_gate` | monkeypatches the exact reader it exists to test |
| 9 | `dom.read_comment_surface` | read a census key that has NEVER been returned; the gate's maps were permanently empty |
| 10 | a reaction probe | read zero controls off a rail that had not drawn, and printed "NOTHING IS REACTED" |

**#10 was written by the agent that had just finished writing the law down.**
That is the honest shape of this defect: knowing about it confers no immunity.

### The structural remedy

**Factor the detector out of the assertion that consumes it.** Logic written
inside an `assert` has no handle and can never be aimed at a known-bad sample.
Then aim it at one, and show it firing.

Two refinements that came with it. A guard reading a historical SHA must SKIP on
a git error rather than go red, or a future rewrite manufactures a false failure
— **and its synthetic control must then run unconditionally**, or that rewrite
silently converts the guard into a check over nothing.

## 2. The lead's own errors, recorded because they are the same disease

Four claims of mine were refuted BY AGENTS, WITH MEASUREMENT. None was caught by
my own review.

1. **"Four real member ids are in unpushed history."** They were synthetic — 39
   chars, 34-character tail, strictly digit/letter alternating, four times over.
   I escalated a guard's RED into a claim about REALITY. **An exact allowlist
   cannot distinguish real from undeclared and should not try; that is what
   makes it an allowlist.** I froze a push and spawned a purge over it.
2. **"`test_uploads.py` carries two urns."** Clean at every commit. I saw the
   FILE was in history and carried the identifiers along with it.
3. **"`server_module` is undefined."** It never was. I was relaying a type
   checker that samples files mid-edit in a tree with six writers; the reported
   line numbers sat exactly one below the committed ones, which DATED the read
   to a ~60-second window. I stopped treating that stream as evidence.
4. **"25 anchors means the page has not finished drawing."** Refuted by a
   33-second watch. The real finding was better: LinkedIn draws 25 rows as
   occludable non-anchor elements until they hydrate.

Also wrong, and corrected by waves I had instructed: ordering a fix to a
substring defect that was already fixed; "one word reaches 62 rows" when that
address REDIRECTS; ordering `UPLOAD_ACTIONS` wired when no `_live_control` arm
can return a file input at all; and generalising "declaring in one place is not
declaring" to a case with a shape half and an exact-value half rather than two
copies of one table.

**Every retraction came from a subordinate challenging the lead with a method.**
That is the control that worked, and it is worth more than the rulings it
overturned. Write rulings so they are cheap to refute, with the evidence
attached.

## 3. Laws earned, stated generally

* **A guard going red means UNDECLARED, never REAL.** The step to "real" needs
  its own positive test — structure, provenance, or membership against
  known-real values.
* **A contradiction between two instruments is a TIMESTAMP question before it is
  a correctness question.** Three times in one session two readings disagreed
  and both were right, having sampled different moments. Date both before
  adjudicating either. **Cite by durable anchor, never by line** — one site wore
  three line numbers in one hour.
* **A number ships with the denominator it was taken over.** The phone row
  closed on "the longest digit run in that file is SIX", not on a zero.
* **A control that returns zero for a reason you have not established is not a
  control.** One planted phone control read zero for TWO independent reasons at
  once: the pattern could not match the grouped spelling, and the value sat on
  the synthetic allowlist.
* **A redaction that erases its own marker is worse than no redaction** — and a
  GREEN run alone would have passed that broken fix. Only the RED/GREEN pair
  catches it.
* **A corrector can name what it corrects; the corrected document cannot name
  its corrector.** A correct measurement sat in this repo for eleven days while
  three later documents restated the claim it refuted. No step was a mistake.
* **A stale honest disclosure is more dangerous than a stale boast, because
  nobody re-reads a sentence that flatters nothing.**
* **A test whose safety rests on the code under test declining to act has no
  safety, it has a coincidence.** One such test opened the operator's real
  browser and put five real names into a pytest assertion the moment the code
  stopped refusing. It was caught only because the assertion failed.
* **A budget is not a containment rule.** A DOM walk capped at eight hops took a
  stranger's member id after two.
* **A grant binds a path, and a path is not a file.** Re-read the digest at the
  moment of use.
* **Mutation testing runs against a COPY, never the shared tree.**
* **Prefer renaming over declaring.** Every declaration permanently widens what a
  guard tolerates; a rename widens nothing. Reach for the allowlist last.
* **A synthetic value should argue for itself** — take the next member of an
  existing series — and must still MATCH the guard's pattern, or it is hiding
  from the check rather than passing it.

## 4. Two live findings this record exists to carry forward

**The running MCP process was 41 commits stale for the whole session**, and the
staleness self-announcement (`9d4d8cf`) landed AFTER the build it would have
announced — so the one instrument built to warn about this could not warn about
itself. Every live reading taken tonight came from that build, including the one
that would have fired a comment through the broken reader at #9.

**`server.py:1095-1097`** states that the vanity slug is never used to build one
of these, even though the allowlist would accept it. Line 2885 builds three of
them from exactly that slug. Defensible only if "one of these" means the
navigation table the sentence sits on — and that distinction is not in the
words. Left unfixed: the file was held by a live writer every time it was
checked.
