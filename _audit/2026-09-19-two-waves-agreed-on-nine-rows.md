# Two waves reached the same nine assignments independently, and the merge kept one argument each

> **SHA NOTE, added 2026-09-20.** The short hash `12c20e1` cited
> below was committed on a `worktree-agent-*` branch that never merged, so
> it is reachable only from that branch and never from `master`. **The work
> itself landed.** Mapped to its `master` twin -- identical subject, identical
> author date, identical `git patch-id` -- under **"Dead hashes, recovered"**
> at the foot of this file; it is kept in place here because a short hash
> is the key a reader arrives with.

**What this file exists to stop being lost.** `_audit/_census/blocker-assignments.tsv`
holds ONE row per `(blocker, row-id)` key. On 2026-09-19 two waves that never
saw each other's output both filed **nine of the same rows, under the same
blocker**. The merge had to collapse each pair to one row, so the table now
shows a single argument where two were made. **A reader of the table cannot tell
these nine apart from rows nobody cross-checked.** That is the whole point of
this document.

## The two waves, and why their overlap is not redundancy

They approached from **opposite ends of the same table**, which is what makes the
agreement worth something:

| wave | branch | its question |
|---|---|---|
| `route-unassigned` | `worktree-agent-aa255d5b6ed0788c7` | *these rows have no blocker -- where does each belong?* |
| `empty-blockers` | `worktree-agent-ae3487dbfd329de80` | *these blockers have no rows -- what fills each?* |

One walked the unassigned rows outward; the other walked the empty blockers
inward. **Neither could see the other's branch.** An agreement reached from two
directions is a different kind of evidence from an agreement reached twice from
the same direction.

## The nine, and the count that matters

**Blocker agreed on 9 of 9. Evidence class agreed on 8 of 9.**

```
M C43   FEED-CONTENT-READ-RULING     RECON-DOC     both
M C74   FEED-CONTENT-READ-RULING     RECON-DOC     both
M M48   MESSAGE-REACTION             RECON-DOC     both
J 129   INMAIL-COMPOSE-SURFACE       RECON-DOC     both
M M11   PER-MESSAGE-OVERFLOW-MENU    RECON-DOC     both
M C23   POST-COMMENT-CONTROLS        RECON-DOC     both
M C29   POST-COMMENT-CONTROLS        RECON-DOC     both
M C90   POST-COMMENT-CONTROLS        RECON-DOC     both
M M10   THREAD-REPLY-BOX             DIFFERED      see below
```

**All nine reason texts DIFFER in wording** -- 297 to 1732 characters, no two
alike. They are not copies. Each wave wrote its own argument and arrived at the
same disposition.

**Rows unique to one wave are not in dispute and were simply unioned:**
`route-unassigned` alone filed N 33, N 47, N 53, N 54, N 61, J 86, N 104;
`empty-blockers` alone filed J 28 and J 85.

## The one difference, and how it was ruled

**`M M10` -- both said `THREAD-REPLY-BOX`, filed 1-of-2, second slot deliberately
left empty and named. They disagreed only about which source column to print.**

* `route-unassigned` -> `LEDGER-AMENDMENT`, citing the ruling at `12c20e1`
  (branch-only; on `master` at `e72af67`) L68:
  *"M M10 stays available to THREAD-REPLY-BOX, where it is the best candidate."*
* `empty-blockers` -> `RECON-DOC`, citing the census reason cell: *"/messaging/
  thread/<id>/ IS on the read allowlist; nothing writes to it. A REPLY-IN-THREAD
  EDITOR has never been censused."*

**Both entries cite BOTH grounds.** The disagreement is a convention question --
which of two real sources goes in the column -- not a disagreement about the row.

**RULED `RECON-DOC`**, on three grounds, in order of weight:

1. **The census reason cell is the primary artifact**; the ruling is a document
   *about* the row. `empty-blockers` structures it exactly that way: ground 1 the
   cell, ground 2 the ruling.
2. **Consistency**: all eight rows the two waves agreed on use `RECON-DOC` ->
   `_audit/_census/messaging-and-content.md`. A ninth row citing a different
   class for the same kind of evidence would make the column mean two things.
3. **The kept entry records its own reversal.** `empty-blockers` had REFUSED
   M M10 earlier the same day, on a 0.67 mutual-best margin, and says so in the
   cell before arguing the reversal: *"a margin RANKS candidates without
   EXCLUDING any, so it cannot force a row. That reasoning was correct and it
   still is. What changed is not the argument but the evidence: neither ground
   below is a score."* **A reversal that can be audited beats one that has to be
   discovered.**

## How the merge resolved, and how to recover what it dropped

Union keyed on `(blocker, row-id)`. On a duplicate key the **fuller argument was
kept** -- length used only as a tiebreak *between two entries already agreed on
the verdict*, never to decide a verdict.

**Nothing is lost.** Both texts remain permanently reachable:

```
git show worktree-agent-aa255d5b6ed0788c7:_audit/_census/blocker-assignments.tsv
git show worktree-agent-ae3487dbfd329de80:_audit/_census/blocker-assignments.tsv
```

## What this does NOT establish

**Concurrence is not correctness.** Two waves sharing a corpus, a set of
conventions and a model can agree on a mistake; the agreement narrows the space
of *undetected* error, it does not close it. Both read the same reason cells, so
a wrong reason cell would produce agreement, not disagreement.

**The honest claim is the narrow one:** on nine rows, two independent readings of
the same evidence produced the same assignment, and one produced a different
evidence class for the same assignment. **That one difference is the more
informative result** -- it is the only place the method showed any spread at all,
and it turned out to be a convention gap rather than a factual one. A convention
gap that surfaced once will surface again; it is written down here so the next
wave settles it by reading rather than by arguing.

## Dead hashes, recovered

Added 2026-09-20. The hash mapped here was made on a `worktree-agent-*` branch
that never merged, so the citation was never checkable from a clone -- NOT
because history was rewritten, but because the branch carrying the commit was
never published. **The underlying work did reach `master`**, re-applied under a
new hash.

Method, measured per pair rather than inferred from ordering: the live hash is
an ancestor of `master` and the dead hash is not; both commits carry a
byte-identical SUBJECT and a byte-identical author identity and date;
`git patch-id --stable` returns the SAME id for both, so the CONTENT is
identical and not merely the message; that subject occurs EXACTLY ONCE on
`master`, so the key is unambiguous; and the dead hash prefixes exactly one
object, so a reader typing it gets one answer. The four controls that show those
checks can fail, and the whole 22-row table, are in
`_audit/2026-09-20-the-evidence-that-resolves.md`.

| dead hash | subject (the durable reference) | live hash | confidence |
|---|---|---|---|
| `12c20e1` | rule(blockers): the three ruling requests -- fill what is forced, leave what is chosen | `e72af67` | CONFIRMED |
