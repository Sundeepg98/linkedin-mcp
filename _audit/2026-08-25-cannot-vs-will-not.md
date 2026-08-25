# CANNOT vs WILL NOT -- every refusal in the LinkedIn MCP, classified

Date: 2026-08-25. Written because the operator is right that this repo has been
blurring two different statements:

> *"If something is not technically possible, then refusing it is a different
> story. If something is technically possible and still you are refusing it, I
> don't know why."*

He is right, and the blur is mine as much as anyone's. My own report yesterday
said `linkedin_apply_job` "should stay refusing" -- a CHOICE, printed directly
underneath the measurements, in a way that made it read as a consequence of
them. It was not. This document separates the two.

---

## 0. There are THREE buckets, not two, and the third is the honest one

The instruction asked for IMPOSSIBLE vs POSSIBLE-REFUSED-BY-CHOICE. Applying it
strictly to every entry produced a problem: **for most refusals, nobody has
looked.** Filing those as "possible, refused by choice" would claim knowledge
this repo does not have -- and that is the SAME error the operator is
correcting, only pointing the other way. Dressing an unexamined gap as a
decision is what `server_info` had to stop doing yesterday.

So:

| bucket | meaning | may it stay refused? |
|---|---|---|
| **CANNOT** | measured, and the measurement shows there is nothing to drive | yes -- and the entry must say why it cannot be done |
| **CAN** | measured, and it works | **no.** Build it, gated |
| **UNMEASURED** | nobody has looked; it is neither | **no.** Measure it, then it becomes CAN or CANNOT |

UNMEASURED is not a hiding place. Every item in it gets measured; the bucket is
meant to empty. It exists so that "we have not looked" never again gets written
down as "we decided against it".

---

## 1. THE COUNTS

Counting CAPABILITIES (19 distinct things this server does, could do, or
refuses to do), not the 20 url substrings, which are guards rather than
features. `action=` is a guard and is not counted as a capability.

| bucket | count |
|---|---|
| **CANNOT** -- proven impossible | **1** |
| **CAN** -- measured possible | **5** (3 shipped, 2 measured and not yet built) |
| **UNMEASURED** | **11** |
| **POLICY** -- possible, refused to protect third parties | **2** |
| total | **19** |

**Exactly ONE refusal in this entire server is proven impossible.** That is the
headline, and it vindicates the operator's suspicion more sharply than a
softer split would have. Everything else is either done, doable, or unexamined.

---

## 2. CANNOT -- 1 item

### 2.1 Mark notifications read

**The team-lead pre-classified this as IMPOSSIBLE and I am CONFIRMING it, having
re-read the measurement rather than inherited the label.**

- 34 activatable controls enumerated on the notifications surface. **Not one of
  the 34 names read, unread, seen, or a badge.**
- 14 menu items fully enumerated. None changes read state.
- No notification carries a per-item id, so there is nothing to aim an action
  at even if a control existed.
- Unread state is EXPRESSED (a class, an indicator) but has no write path.
- LinkedIn marks the list seen SERVER-SIDE when the page is served.

There is no control and no target. As a discrete addressable action this is
genuinely impossible, not declined.

**And the capability he actually wants already ships.** The badge clears when
the page is read, which `linkedin_notifications` does. "Mark my notifications
read" is not a missing feature here; it is an automatic one. The entry should
say that, instead of sitting in a refusal list looking like a withheld thing.

---

## 3. CAN -- 5 items

| capability | status | evidence |
|---|---|---|
| save a job | **SHIPPED**, gated | performable |
| unsave a job | **SHIPPED**, gated | performable |
| unfollow a company | **SHIPPED**, gated | performable |
| **apply to a LinkedIn-hosted posting** | **measured possible, NOT built** | one screen, one `Submit application`, enabled on arrival, stable test hook |
| **read the message inbox** | **measured possible, NOT built** | renders, 10-11 conversations enumerable, no auth wall |

The last two are the ones the operator's ruling bites on hardest, because they
were measured POSSIBLE and then refused anyway -- by me, in writing, yesterday.

---

## 4. UNMEASURED -- 11 items

These have never been examined. Each is listed with what would settle it.

| # | capability | what would settle it |
|---|---|---|
| 1 | send a message / InMail | does a compose surface exist, and what does it require -- see the collision in section 6 |
| 2 | send a connection invitation | same surface question |
| 3 | **set Open To Work** | **RECLASSIFIED -- see 4.1** |
| 4 | follow a company | the identifier join: postings name an employer by SLUG, the follow surface addresses rows by NUMERIC id, and nothing measured resolves one to the other |
| 5 | edit other profile fields | is any editor url-addressable, or is it all modal |
| 6 | change account settings | `/settings/` is guarded and has never been probed |
| 7 | withdraw an application | a real LinkedIn feature; never looked for |
| 8 | post / share an update | never looked for |
| 9 | comment on a post | never looked for |
| 10 | like / react to a post | never looked for |
| 11 | endorse a member's skill | never looked for. Acts on a third party's profile, so if it is ever built the POLICY line in section 5 governs it, not his preference |

### 4.1 Open To Work -- I am OVERTURNING the pre-classification

**The instruction offered Open To Work as a worked example of IMPOSSIBLE. It
does not qualify, and the repo's own census says so.**

The measurement is real and I am not disputing it: 237 distinct urls and 37
payload paths across five profile captures, and **zero reach an editor**. But
what that proves is precisely:

> Open To Work is not reachable BY NAVIGATION.

That is not the same claim as "cannot be done". It opens as a modal, and a
modal opens by CLICKING. The existing census goes further and already names a
safe way in -- its own control table lists a `Show details` control whose action
list contains **one `Navigate` and no `ServerRequest`**, and rates it:

> *"low -- read-shaped. Capture here FIRST."*

A census that names a low-risk first click, and recommends capturing there, is
not describing an impossibility. It is describing an unfinished measurement.

**This is exactly the blur the operator is objecting to, caught in the act:** a
real measurement ("no url reaches it") was allowed to stand in for a stronger
claim ("it cannot be done"), and it hardened into a refusal. `set_open_to_work`
moves to UNMEASURED, and the measurement is the `Show details` click.

The one genuine caution, which is a RISK and must be labelled as one rather
than promoted into an impossibility: **this is the only setting here a current
employer can see.** That argues for the gate being loud, not for refusing.

---

## 5. POLICY -- 2 items, and these stay

Possible, and refused anyway. Both protect somebody other than him, which is
what distinguishes them from everything above.

1. **Collecting data about other members.** Stays. This is the one refusal that
   is not his to overrule, because the person it protects is not him.
2. **Driving an off-site applicant-tracking system.** A third party's form on a
   third party's domain. `apply_path` already reports the route and names the
   destination host; reporting and stopping is the correct behaviour.

---

## 6. A COLLISION IN THE INSTRUCTION, surfaced rather than resolved quietly

The instruction says build InMail and invitations, and also says:

> *"Anything whose request shape you would have to guess ... A write with a
> guessed body is worse than no tool."*

**I have zero measurements of the InMail or invitation surface.** Building them
now would mean guessed selectors and a guessed request body, which the same
instruction forbids. So they must be MEASURED first -- that is not a stall, it
is the only order that satisfies both halves.

But measuring them runs into the POLICY line: **the send surface only renders
on another member's profile.** To measure the control I would have to load a
third party's profile page, which is the one refusal the instruction says stays.

**The resolution I propose, and will build to unless overruled:** the recipient
is a REQUIRED, CALLER-SUPPLIED argument. The server never discovers, searches,
enumerates or browses to find a person -- it acts only on a target he names. On
that design, no data about members is collected: one profile is loaded because
he pointed at it, exactly as `linkedin_job_detail` loads a posting he names.

That keeps the policy line intact (no enumeration, no scraping, no discovery)
while making the capability real. I am flagging it rather than assuming it,
because it is the one place where "build everything possible" and "protect
third parties" actually touch.

---

## 7. What this changes in `server_info`

`cannot` and `will not` become separate fields, so he never has to ask which
kind of refusal he is looking at:

- `cannot_be_done` -- 1 entry, each stating the measurement that proves it
- `can_be_done_and_is_refused` -- must be EMPTY once the build lands, and any
  entry in it needs a named human reason
- `not_yet_measured` -- with the instrument that would settle each
- `refused_as_policy` -- 2 entries, each naming who it protects

---

## 8. Order of work

1. This classification. **Done -- it is the deliverable before any code.**
2. Build the two measured-CAN items: `linkedin_apply` and `linkedin_read_inbox`,
   both gated preview-then-confirm.
3. Solve the follow identifier join, or state exactly which identifier space is
   missing and what would produce it.
4. Measure the UNMEASURED ten, cheapest and safest first, starting with the
   `Show details` click the OTW census already nominated.
5. Build whatever those measurements show is possible.

**A constraint on all browser work, stated because it bounds the schedule:**
there is ONE Chrome profile behind a cross-process lock, so browser probes
CANNOT run in parallel. Fanning out agents against it would serialise on the
lock anyway, and two writers in one profile is how the profile got corrupted
yesterday. Measurement here is serial by construction.
