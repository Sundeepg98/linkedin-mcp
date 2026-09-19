# Three ruling requests from the blocker-map recovery

**What this is.** The recovery took UNASSIGNED from 268 to 64 and 69 of 97
blockers to COMPLETE. What remains is not unfound -- it is unruled. This file
states each question with the candidates, the discriminator that would settle
it, what turns on the answer, and **what I would rule if it were mine**, because
a ruling made against a stated recommendation is cheaper than one made against
silence.

**Nothing here is a measurement request.** Every instrument that could speak has
spoken and is at a fixed point: the section enumerator, singleton and multi-row
mutual-best matching, split-first subset search, the committed-source comment
vein, and a co-occurrence sweep over every tracked file. Each of these is a
CHOICE among candidates.

**State at the time of writing, 2026-09-19 12:25 by the box:** frozen GAP 409,
ASSIGNED 345, UNASSIGNED 64, blockers COMPLETE 69 of 97, EMPTY 19 (47 rows).

---

## REQUEST 1 -- `CONVERSATION-OVERFLOW-MENU`: which ONE write is not this blocker's?

**Published:** 10 rows, `1R/8W/1RW`. **Currently:** 0 of 10, the largest empty
blocker left.

### This is no longer "no source names the rows"

That was the honest state this morning, and it came from a dedicated slice:
*"only one of the seven has an explicit row-id list anywhere in the tracked or
scratch corpus... For the other six -- including all 10 rows of
`CONVERSATION-OVERFLOW-MENU` -- there is no list."* **That remains true: no
source LISTS them.** What has changed is that the candidate set is now bounded
and the split nearly forces the arrangement.

**Every unassigned frozen-GAP row in the messaging slice that could belong:**

| row | dir | capability |
|---|---|---|
| `M M25` | W | Leave a conversation |
| `M M27` | W | Archive a conversation |
| `M M28` | **R+W** | View and restore archived conversations |
| `M M29` | W | Mute or unmute a conversation |
| `M M30` | W | Star a conversation |
| `M M31` | W | Mark a conversation read or unread |
| `M M32` | W | Bulk delete / archive / mark read |
| `M M35` | W | Choose Messaging inbox layout |
| `M M36` | W | Manage how new conversations open |
| `M M10` | W | Reply to a message in a thread |
| `M M49` | R | Read message delivery / read indicators |

Two near neighbours are **excluded by the data, not by me**: `M M33` (inbox
filter pills) is NOT IN THE FROZEN 409 -- it was excluded at the freeze, so the
builder would refuse it; `M M34` (search messages by keyword) is already filed
to `MISSING-PARAM-MESSAGING`.

### What forces most of it

* **The `1RW` is unique.** `M M28` is the only `R+W` row in the slice. Nothing
  else can fill that slot.
* **The `1R` has exactly one candidate.** `M M49` is the only unassigned
  messaging READ.
* That leaves **nine writes for eight slots**, so exactly one must go.

### THE DISCRIMINATOR

**Which of the nine acts on ONE conversation?** Every genuine overflow-menu item
does. Measured against that test, seven pass cleanly (`M25 M27 M29 M30 M31 M32
M36`), and **two do not**: `M M35` is an inbox-level layout setting, and
`M M10` is the reply box rather than a menu item. Nine minus two is seven, which
is one short -- so exactly one of those two is in, and that is the question.

### WHAT I WOULD RULE

**Drop `M M10`, keep `M M35`.** Reasons, weakest last:

1. `M M10` is `THREAD-REPLY-BOX`'s best candidate by a clear margin (0.67
   mutual-best, no rival), and that blocker publishes `2W` and is EMPTY.
   Assigning `M10` here would strand it.
2. With `M10` out, the arithmetic closes **exactly**: `M49` (1R) + `M28` (1RW) +
   `M25 M27 M29 M30 M31 M32 M35 M36` (8W) = `1R/8W/1RW`, the published split, on
   the nose.
3. `M35` is uncomfortable and I am saying so: "Choose Messaging inbox layout" is
   not obviously an overflow-menu item. It is admitted by the count rather than
   by resemblance -- the same basis on which `B7` entered `BADGES-SURFACE`.

**My confidence is moderate, and the weak joint is `M M49` as the read.** Read
receipts are a setting, not a menu item. If you reject `M49`, the blocker cannot
reach `1R` from any unassigned row and the correct answer is that one of its ten
is a row nobody has identified -- in which case **rule it UNLOCATABLE and leave
it at 0**, rather than filing nine and implying the tenth is merely pending.

### WHAT TURNS ON IT

Ten rows, the largest single block left. The ledger queues it MEASURE at cost 6;
`_audit/2026-09-19-messaging-menu-enumeration.md` has it MEASURE-BLOCKED on an
unsanctioned press, so the rows cannot be measured until the disclosing-press
mechanism exists. **Locating them does not unblock them** -- it makes them
schedulable behind that mechanism instead of invisible.

---

## REQUEST 2 -- two blockers where more candidates than slots meet a missing discriminator

### 2a. `PREMIUM-APPLY-SURFACES` -- which of five writes is not this blocker's?

**Published:** 5 rows, `1R/4W`. **Currently:** 0 of 5. Declined three times
today, always for the same reason.

A committed source names SIX: `scripts/_probe_jobs_tail_boundary.py`, *"# 61
PREMIUM-APPLY-SURFACES -- census rows J78-J83."* Six against a published five,
and **unlike the alerts line in the same comment block it makes no R/W claim**,
which is precisely why the alerts entry could be acted on and this one cannot.

| row | capability |
|---|---|
| `J 78` | Cover Letter Assistance (Premium AI drafting) |
| `J 79` | Mark a job "Top Choice" (Premium, 3/month) |
| `J 80` | Attach an optional message to the poster with a Top Choice mark |
| `J 81` | Verify account to raise the Easy Apply daily limit |
| `J 82` | Observe the Easy Apply daily limit / rate-pause state |
| `J 83` | Save voluntary self-identification answers for reuse |

**THE DISCRIMINATOR:** the published `1R` is unambiguous -- `J 82` is the only
row that merely *observes*. The question is which of `J 78 79 80 81 83` is not
one of the four writes.

**WHAT I WOULD RULE: drop `J 81`.** "Verify account to raise the Easy Apply
daily limit" is an **account-verification** act that happens to have an apply
consequence; the other four are things done inside the apply flow itself. It is
also the only one of the six whose subject is the account rather than an
application. `ACCOUNT-VERIFICATION` is EMPTY at 3 and is the natural home,
though I am **not** proposing to file it there -- see 2b, which is the same
family and has its own problem.

Confidence: moderate. The counter-argument is that `J 81`'s *purpose* is
apply-throughput, and the census groups it in section D "Applying".

### 2b. `INVITATION-SUBSTRING-BLOCKED` -- and here the discriminator cannot be made to exist

**Published:** 3 rows, **no split published at all** -- its ledger entry is in
the cost-0 table, which has no R/W column. **Currently:** 0 of 3.

Four candidates, all W, all in `network.md` section A:

| row | capability |
|---|---|
| `N 5` | Add a personalized note to an invitation |
| `N 6` | Re-invite a member after the previous invitation expired |
| `N 7` | Invite your connections to follow your employer's Page (30/month) |
| `N 8` | Invite your connections to follow a Page you do not manage (50/month) |

The ledger's own "why" says *"`/invite` and `invitation` are forbidden
substrings and the network slice's R2 is written for exactly these"* -- but
**every row R2 actually cites (`N 9`-`N 19`) is already EXCLUDED-RULED**, so that
sentence does not reach these four.

**THIS IS THE STRUCTURAL DEAD END, and it is worth stating as a class.** Four of
the remaining blockers sit in the cost-0 table, which publishes no R/W. The
split is the discriminator that broke every other tie in this recovery --
including one case where it overruled a *perfect* count match. **For these four
it does not exist and cannot be made to exist**, short of the deferred jobs-style
R/W column being extended to the cost-0 entries.

**WHAT I WOULD RULE: `N 5`, `N 6`, `N 7`** -- the three whose act is *sending an
invitation*, which is what the blocker is named for. `N 8` differs on the one
axis the blocker cares about: it invites to a Page **the operator does not
manage**, which is an admin-adjacent act and sits closer to
`ADMIN-RIGHTS-NOT-HELD` (already COMPLETE at 15, so it cannot take it -- which
means `N 8` would stay UNASSIGNED).

Confidence: **low.** All four contain a forbidden substring and all four are
writes. I would rather you rule this one cold than adopt my reading.

---

## REQUEST 3 -- `BADGES-SURFACE`: `B8` or `K9`, and it is NOT a subtraction

**Published:** 5 rows, `2R/3W`. **Now at 4 of 5** -- committed at `a604394`,
because collapsing one duplicate forced four of the five.

**The duplicate is evidenced by an identical source citation, not by my reading
of the prose:**

    B8   Top Voice badge show / hide        a1577365
    K9   Show / hide the Top Voice badge    a1577365

Same Help Center article, same act, inverted word order, censused once under
`profile.md` section B ("Photo, banner, frames, badges") and again under section
K ("Verification and badges").

Collapse the pair to one slot and the set closes exactly: `K8` (R), `K10` (R),
`B7` (W), `B9` (W), and **one of `B8`/`K9`** (W) = `2R/3W`.

### THE ONLY QUESTION: which id did the lost classifier use?

### AND IT DOES NOT INHERIT THE HOLD -- please check this reasoning

The standing hold is that the 13 confirmed cross-slice duplicates are **NOT
subtracted until the 761 derivation reconciles**, because moving a denominator
on a reconstruction while its baseline is in question produces a number wrong in
two unknown ways. **That hold is about SUBTRACTION. This is not a subtraction.**

* Both `B8` and `K9` stay in the frozen 409 whichever way it goes. One lands in
  this blocker; the other stays UNASSIGNED.
* **No denominator moves.** 409 untouched, 761 untouched, no count changes.
* The pair is also **INTRA-slice** -- both rows are in `profile.md` -- where the
  hold covers cross-slice pairs.

So this is a narrower question than the class it resembles. **If you read it
otherwise, it stays at 4 of 5 and nothing is lost.**

**WHAT I WOULD RULE: `K9`.** Reason: section K is "Verification **and badges**"
and this blocker is `BADGES-SURFACE`, so K is the section whose subject matches
the blocker's name; section B's subject is "Photo, banner, frames, badges",
where badges are the last of four. Both of the blocker's certain reads (`K8`,
`K10`) are already section-K rows, so `K9` keeps the blocker's centre of gravity
in one section rather than splitting it.

Confidence: **moderate, and the counter-argument is real** -- `B7` and `B9` are
section-B rows and are certain, so this blocker already spans both sections and
the tidiness argument is weaker than it looks.

---

## A NOTE ON WHAT IS NOT HERE

The remaining EMPTY blockers not listed above fail on the same three axes and
are enumerated with their candidate counts in
`_audit/_scratch/_progress-unlocatable-recovery.md` section 47. They are not
raised individually because each is one or two rows and the answers would be
guesses of the same kind. **If the three classes above are ruled, the method
generalises to most of them.**

**The three classes close the remaining rows exactly, which is how I know the
routing is complete:** needs a ruling 31, no published split 10, no source at
all 10 -- totalling the 51 empty rows counted before `BADGES-SURFACE` moved four
of them.
