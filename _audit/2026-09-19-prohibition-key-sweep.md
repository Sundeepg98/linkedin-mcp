# The prohibition-key sweep, finished -- the seam is EXHAUSTED at two rows

> **THIS SEAM IS CLOSED. Do not re-run it looking for more.** All nine keys of
> `writes.PERMANENTLY_FORBIDDEN` were swept across all **334** GAP rows on
> 2026-09-19. Total yield: **two rows**, both banked in the first pass
> (`bacecab`). The full pass added **none**. What it produced instead is four
> rows stated precisely for a ruling, and one structural finding that blocks a
> fifth from being bankable at all.

## Why this half was worth running when the other was not

The companion question -- *which GAP rows are already BUILT* -- is undetectable
by any text heuristic; four designs failed and
`scripts/unbanked_row_sweep.py` is committed as a failed instrument that
refuses to run.

**This half is different because the refusals are a small enumerable set with
explicit names.** Nine keys, each with a written reason. No semantics required
to find candidates -- only to adjudicate them.

## The method IS the finding: read the rule, do not match the pattern

Every key was read in full before any row was judged. That step discarded more
candidates than it confirmed, and each discard is a case where pattern-matching
would have banked a row wrongly:

| key | what the rule actually says | what that excluded |
|---|---|---|
| `repost_or_share` | **NARROWED 2026-08-30.** Posting, commenting and reacting are now SANCTIONED specs. Only *"a repost republishes SOMEBODY ELSE'S item"* survives | would have wrongly caught `M C72` "Share a post off LinkedIn" -- sharing your OWN post off-platform is not a repost |
| `endorse_or_recommend` | rests on a MEASUREMENT: zero endorse controls across 13 fixtures; *"you cannot endorse yourself, so the only surface is a THIRD PARTY'S PROFILE"* | `P F2` "Request a recommendation" -- requested from YOUR OWN profile, so the third-party-load ground does not transfer |
| `mark_notifications_read` | keyed to the NOTIFICATIONS surface, with a measured second ground specific to it -- 34 activatable controls across 6 cards, none changing read state | `M M31` "Mark a conversation read or unread" -- messaging is a different surface |
| `any_loop_sweep_or_scheduled_write` | *"one write per invocation"* -- about UNATTENDED WRITES | `M M20` "Start or **schedule** a video meeting" -- scheduling a MEETING is one write, not a scheduled write |
| `delete_or_withdraw_anything` | *"destruction is not a write this design covers, at any confirm level"* | six COMPOUND rows where delete is one verb of several |

**On the compound rows** -- "Set / edit / **delete** the Minimum Pay preference",
"Create / edit / **delete** a newsletter", "List / **delete** stored resumes",
"Edit or **delete** a group post or comment", "Create / **delete** a
secondary-language profile", "**Delete** / turn off a job alert". Only the
delete verb is refused; the rest of each row is not. **Banking them would be
banking a row on a third of its own capability**, which is the `M M32` error in
reverse -- that row was under-banked because its cell had found one third of
the ground.

## The full sweep, all nine keys, 334 GAP rows

    repost_or_share                            0 candidates
    auto_accept_or_auto_reply                  0
    deanonymise_a_viewer                       0
    load_a_third_partys_profile                0
    any_anti_detection_technique               0
    any_loop_sweep_or_scheduled_write          1   discarded (see table)
    mark_notifications_read                    1   flagged, not banked
    endorse_or_recommend                       1   flagged, not banked
    delete_or_withdraw_anything                7   6 compound, 1 unbankable

**NEW ROWS BANKED: ZERO.** The two from the first pass stand:

* **`M C62`** "Withdraw a group membership request" -- the cell rested on
  `/withdraw` catching a url *"incidentally"*; the **ACT** is squarely refused.
  **Prefer the act over the url: a url match is the weak half.**
* **`M M32`** "Bulk delete / archive / mark read" -- the cell had one third of
  the ground. **Bulk is refused for all three thirds**, independently: a bulk
  operation here is not expensive, it is structurally unexpressible.

## A STRUCTURAL FINDING: one row cannot be banked at all

**`N A15` "Withdraw an event invitation before the invitee responds" is not
bankable in the census's current shape**, whatever anybody rules about it.

It sits in the network slice's admin-only table, whose header is:

    | # | capability | R/W |

**Three columns. There is no state column.** All fifteen `A`-rows are GAP by
SECTION PROSE -- *"All fifteen are GAP: no tool, and no written reason"* -- and
`enumerate_gap_rows.py:89` hard-codes that, forcing `N A<digits>` to GAP.

So moving `A15` alone requires either adding a state column to that table or
rewriting the prose that covers all fifteen at once. **A ruling on A15 cannot
be applied to A15 without a structural edit to the table**, and that edit
touches fourteen other rows.

## Stated precisely for a ruling -- four rows, none stretched

### 1. `M C56` "Remove yourself from a collaborative post" (`messaging-and-content.md:445`, W, NOT reversible)

* **What refuses it, and how nearly:** `delete_or_withdraw_anything` --
  *"destruction is not a write this design covers, at any confirm level."*
* **For:** the act permanently removes content, and the row's own
  reversibility column reads NOT.
* **Against:** that entry's working purpose is taking back things FIRED AT
  OTHERS -- five shipped specs cite it in `reversible_by` for an application,
  a post, a comment, an invitation and a message. Removing YOURSELF from a
  shared artefact is self-withdrawal, not destruction of something you
  published. A sibling wave measured on 2026-09-19 that *"removing YOURSELF
  names no third party"* (`_audit/2026-09-19-content-tail.md` s2).
* **What turns on it:** covered -> EXCLUDED-RULED, row closes, nothing to
  build. Not covered -> stays GAP needing an allowlist pattern, a WriteSpec
  and a gate.

### 2. `N A15` "Withdraw an event invitation before the invitee responds" (`network.md:569`, W)

* **What refuses it:** two candidates, and they are independent.
  `delete_or_withdraw_anything` reaches the act directly. But the row is also
  in the `ADMIN-RIGHTS-NOT-HELD` family -- the account does not hold the Page
  admin rights the whole table presumes.
* **What turns on it:** which blocker owns it, and **whether it can be
  expressed at all** -- see the structural finding above. If the answer is
  "excluded by admin rights", that is already true of all fifteen and argues
  for moving the table wholesale rather than this row.

### 3. `M M31` "Mark a conversation read or unread" -- FLAGGED, NOT STRETCHED

The prohibition names NOTIFICATIONS. Its first ground transfers cleanly by
analogy -- *"clearing his unread badge destroys signal he has not seen, and
the act is server-side on page serve so it cannot even be confirmed first"* is
just as true of a messaging thread. **Its measured second ground does not**:
that census counted controls on the notifications surface.

**I have not applied it.** Extending a prohibition to a surface it does not
name is exactly the stretch that makes a narrow rule wide, and this document's
whole method is that the rule's own words decide.

### 4. `P F2` "Request a recommendation" -- FLAGGED, NOT STRETCHED

Not covered by `endorse_or_recommend`: that refusal survives on a measurement
about ENDORSE controls, whose force is that endorsing requires loading a third
party's profile. **A recommendation is REQUESTED from your own profile**, so
the ground does not transfer.

But the row's own note says *"it reaches another member"*, which puts it in the
class the standing order protects. It is not refused by any existing
prohibition; it needs a WriteSpec and a gate like every other person-reaching
write. **Correctly GAP, and not a candidate for this seam.**

## What this bounds

Two seams have now been run to exhaustion:

* **already BUILT** -- undetectable by heuristic, ~11 instances found by hand,
  and the tool parameter surface is now pinned so the class cannot grow
  (`tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py`).
* **already RULED** -- enumerable, swept completely, **two rows total.**

**Neither seam is where the remaining GAP lives.** 334 rows are still GAP and
the great majority are genuinely unbuilt and genuinely unruled.
