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

Counting CAPABILITIES (20 distinct things this server does, could do, or
refuses to do), not the 20 url substrings, which are guards rather than
features. `action=` is a guard and is not counted as a capability.

| bucket | count |
|---|---|
| **CANNOT** -- proven impossible | **1** |
| **CAN** -- measured possible | **6** (**5 shipped**, 1 measured and not yet built) |
| **UNMEASURED** | **12** |
| **POLICY** -- possible, refused to protect third parties | **1** |
| total | **20** |

**UPDATED 2026-08-25 (third revision) -- THE POLICY BUCKET WAS DISSOLVED BY
THE OPERATOR.** He read its three entries back and ruled: *"if they're
technically possible via the MCP, why should we not do that? Let's do them
also."* Total is unchanged at 20 because nothing appeared or vanished --
entries MOVED:

| capability | from | to |
|---|---|---|
| reading the message inbox | POLICY | **CAN** (to build) |
| looking up one member | POLICY (as "collecting member data") | **UNMEASURED** -- no third-party profile has ever been captured |
| driving an off-site ATS | POLICY | **POLICY, unchanged -- see 5.4** |
| reading the unread count | CAN (to build) | **CAN, SHIPPED** |

**What the bucket got wrong, stated exactly, because "the operator overruled
a safety line" would be the wrong lesson.** Its TEST was sound: an entry
belongs there only if the cost lands on somebody who is not him. Its
MEMBERSHIP was not. His inbox is his own correspondence -- those people wrote
to HIM. An endorsement is a gift to the person receiving it, not an
extraction from them. And looking up ONE named member is what the product is
for; the thing that ever deserved refusing was BULK COLLECTION, which is a
different act rather than a bigger version of the same one.

**The protection did not disappear, it moved into the code** as a hard cap on
the lookup: one member per call, no enumeration, no graph-walking, no
iterating search results into fetches, nothing persisted past the response. A
line in a bucket relies on a caller's restraint; a line in the tool does not.

**UPDATED 2026-08-25 (second revision).** Two things moved and the total grew
by one because a capability SPLIT:

- **apply SHIPPED** -- `linkedin_apply_job` is a registered, gated tool. It
  left `can_be_done_and_is_refused`, which is what that field is for.
- **reading the inbox moved to POLICY** and did not get built. SUPERSEDED HOURS LATER by the third revision above: the operator dissolved that entry and it is a CAN again. Kept rather than deleted so the reversal is legible.
- **reading the unread COUNT is a new CAN**, and it is the half of "check my
  messages" that survives: the badge renders on `/feed/`, already an allowed
  surface, so it opens nobody's conversation and needs no boundary change.
  One capability turned out to be two, which is why 19 became 20.

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

## 3. CAN -- 6 items

| capability | status | evidence |
|---|---|---|
| save a job | **SHIPPED**, gated | performable |
| unsave a job | **SHIPPED**, gated | performable |
| unfollow a company | **SHIPPED**, gated | performable |
| **apply to a LinkedIn-hosted posting** | **SHIPPED 2026-08-25**, gated | one screen, one `Submit application`, enabled on arrival, stable test hook |
| **read the unread message count** | **SHIPPED 2026-08-25** | the badge renders on `/feed/`, already an allowed surface |
| **read the message inbox** | measured possible, NOT built | renders, conversations enumerable, no auth wall -- moved here from POLICY by the operator's ruling |

Apply was the entry the operator's ruling bit on hardest -- measured POSSIBLE
and then refused anyway, by me, in writing. It ships.

The unread count is not a consolation prize for the inbox refusal, it is a
different capability that happens to answer most of the same question. "Do I
have messages waiting" is answerable at zero cost off a surface this server
already loads. "Show me my inbox" is not -- see 5.3.

The unread count SHIPPED as `linkedin_unread_messages`. Its badge
pattern comes from a real capture, but the tool has not yet been
exercised end to end against the live surface -- the session lapsed
again the same day -- and the commit says so rather than implying a
verification that did not happen.

---

## 4. UNMEASURED -- 12 items

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
| 11 | endorse a member's skill | never looked for. THE POLICY CAVEAT THAT WAS HERE IS GONE -- the operator ruled on 2026-08-25 that it gets built, gated, one member and one skill per call. It still needs the control measured on a real profile |
| 12 | look up ONE named member | moved here from POLICY by the same ruling. No third-party profile has ever been captured, so the parser is unproven against one -- `linkedin_my_profile`'s topcard reader is the obvious starting point and may or may not transfer |

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

## 5. POLICY -- 1 item after the operator dissolved the other two

Possible, and refused anyway. Both protect somebody other than him, which is
what distinguishes them from everything above.

1. **Collecting data about other members.** Stays. This is the one refusal that
   is not his to overrule, because the person it protects is not him.
2. **Driving an off-site applicant-tracking system.** A third party's form on a
   third party's domain. `apply_path` already reports the route and names the
   destination host; reporting and stopping is the correct behaviour.

### 5.4 What remains, and why it was not dissolved with the rest

**Driving an off-site applicant-tracking system stays, and it was NOT part of
the ruling.** The operator was asked about three LINKEDIN capabilities and
ruled on those. This is not a LinkedIn capability at all -- it is somebody
else's form on somebody else's domain, under their terms. A ruling is not
extended past what it covered, least of all to remove a protection nobody was
asked about. If it should go too, that is a separate question to put to him.

### 5.3 Reading the message inbox -- DISSOLVED 2026-08-25, and my call was wrong

**It was in CAN, measured possible and unbuilt, which under this document's
own rule meant "build it rather than justify it". It could not stay there, and
it did not get built. This is the argument for the third option.**

Protects: **the correspondent whose conversation gets opened.**

THE MEASUREMENT, and it is the whole case: asking for `/messaging/` does not
stay on an inbox. LinkedIn redirects it into ONE SPECIFIC CONVERSATION THREAD
-- verified twice, on two runs by two different actors. **And the caller does
not choose which. LinkedIn does.**

So a tool named `linkedin_read_inbox` would not return an inbox. It would open
a named person's conversation, on every call, selected by somebody other than
the person calling it. That is a cost landing on a third party, which is the
only test for belonging on this list -- the same test that keeps
member-data collection here and that let posting, liking, InMail and
invitations OFF it.

**Why this is not the convenient answer.** The obvious objection is that an
inbox is his own correspondence, so no third party is involved and this fails
the test. That objection is right about the INBOX and wrong about what
`/messaging/` actually does. If the surface returned a list, this would be a
CAN and it would get built. It returns a thread.

**WHAT IS NOT CLAIMED.** Whether opening a thread sends that person a READ
RECEIPT is **UNMEASURED**. It would make this materially worse and it is the
first thing to establish if anyone reopens the question -- but the refusal
does not rest on it, and stating it as though it were measured would be the
same error this document exists to correct. Two attempts to settle it failed
because the unread badge was already at zero and had nowhere to fall from.

**WHAT SURVIVES.** The unread COUNT, read off `/feed/` -- an already-allowed
surface, no boundary change, nobody's conversation opened. Section 3.

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

## 7b. WITHDRAW IS BLOCKED ON APPLY, not on effort

Measured 2026-08-25, and it inverts the order the work was requested in.

Withdrawing an application was nominated as the place to start: a real
LinkedIn feature, never looked for, directly useful. There is a stronger
reason than usefulness -- **if an application can be undone, applying is a
different risk**, so withdraw changes what the apply gate has to say.

**It cannot be measured yet.** `linkedin_my_applications` reports:

```
count 0, tab_counts {saved 0, in_progress 1, applied 0, interview 0}
empty_state "No matches"   -- an empty list, not a failed read
```

Measuring withdraw means enumerating the controls on an APPLIED row. There are
no applied rows. Getting one means applying. So:

> measure withdraw -> needs an applied row -> needs an apply -> and how safe
> that apply is depends partly on whether withdraw exists.

That is circular, and it resolves in only one direction: **the first
application made through this server is one it cannot undo, and whether
LinkedIn itself offers a withdraw is UNMEASURED.** Any apply gate must say
exactly that, rather than the softer "this server cannot withdraw it", which
invites the reader to assume LinkedIn can.

## 7c. THE APPLY WIRING WAS BLOCKED BY THE PERMISSION SYSTEM

Stated here because a report that omitted it would misrepresent why the
`can_be_done_and_is_refused` field is not empty.

The wiring was designed and written: the posting page as the address (no
denylist change needed, no new allowlist entry), `apply_job` into
`PERFORMABLE`, and a second gate between two clicks. **The permission system
declined the change, twice.**

It was not re-attempted through a different tool. The rule that governs this
is not a preference: **only the permission system or the operator's own words
are approval.** An agent relaying "the operator has ruled" is not a
substitute, and the permission system declining the exact thing being relayed
is the case that rule exists for. Routing the same edit through a different
tool would be defeating the check rather than satisfying it.

What landed instead is `dom.read_apply_modal` -- a READER, committed
separately and wiring nothing. `PERFORMABLE` is unchanged, the apply spec
still has `url_template=None`, and the mutation scanner still counts exactly
one `page.click` call site.

**The design, so it is not lost and so a human can judge it rather than
rebuild it:**

1. Address the action at the POSTING page, not the apply url. Navigating to
   the apply url LANDS BACK on the posting with the flow drawn as a modal, so
   the posting page IS the apply surface. This is why apply needs no boundary
   change at all -- the four frozen denylists stay byte-identical.
2. Gate 5 as today: re-read the apply control's live label before clicking.
3. Click one. Opens the modal. Submits nothing.
4. **THE SECOND GATE**, which is the whole safety argument. Re-read the modal
   and require all five of: it rendered; exactly one control carries
   LinkedIn's submit test hook; that control is visible and enabled; its
   accessible name corroborates the hook; and **zero advance controls are
   visible**. The last one catches the case nobody has measured -- a
   multi-step posting -- because exactly ONE flow has been observed and
   generalising from one observation to every posting is a guess about
   something that cannot be undone.
5. Click two, only if all five hold.

An abort between the clicks is cheap and that is why it is the right place to
stop: click one may leave a draft, and a draft is not an application.
Stopping costs a draft; being wrong costs an application nobody can withdraw.

The single `page.click` call site is preserved by draining a queue rather than
adding a second literal call -- the scanner counts call sites, and the
guarantee it was written to give is "one place in this package clicks, and a
reviewer reads it". That property survives; the fact that it fires TWICE for
apply has to be stated loudly wherever it is written, or the one-entry
allowlist misleads.

## 7d. THE 12 UNMEASURED, RANKED -- and the tail is named

Ranked against the operator's measured bottleneck, which is **conversion, not
discovery**. He does not need more postings found; he needs the ones already
in motion to move.

**The shape worth copying** comes from a sibling server: the most valuable
route built in this family recorded what replies **ASKED FOR** rather than
that they arrived, and surfaced two that were waiting on something specific
from him. So the ranking question for each item below is not "is this a
capability" but **"does this surface something that is waiting on him?"**

| # | capability | why here |
|---|---|---|
| 1 | **read the inbox** | The direct analogue of that shape. A recruiter message asking him something IS a thing waiting on him, and it is the only surface here that holds one. Already a CAN. |
| 2 | **pending connection invitations** | Incoming invites are literally queued on his decision. Unmeasured, and the cheapest of the network items to check. |
| 3 | **set Open To Work** | The strongest passive recruiter signal LinkedIn offers, and the census already names the safe first click. Employer-visible, so a loud gate. |
| 4 | **look up ONE member** | Research before an interview or before answering a recruiter. Supports conversion rather than producing it. |
| 5 | **withdraw an application** | Changes how safe applying is, which is worth more than the action itself. Blocked on a real applied row -- do not manufacture one. |
| 6 | **follow a company** | Weak signal, but the obstacle is understood: the slug/id join. Solvable engineering rather than a measurement. |
| 7 | **send InMail** | Outbound and it spends credits. Real, but it costs something and the surface is uncaptured. |
| 8 | **endorse a skill** | A gift, and relationship maintenance rather than conversion. Cheap once the control is measured. |

**THE TAIL, NAMED RATHER THAN LEFT TO TRAIL OFF -- items 9 to 12, and I am
deprioritising all four:**

| # | capability | why it is last |
|---|---|---|
| 9 | edit other profile fields | Nothing is waiting on him here, and the profile that matters (Open To Work) is item 3. |
| 10 | change account settings | Same, and `/settings/` is the least-explored surface in the package -- highest measurement cost, lowest return. |
| 11 | post / share an update | Broadcasting. It reaches nobody in particular and converts no conversation already in motion. |
| 12 | comment / react on a post | The furthest from a job of anything on this list. Cheap to build and worth almost nothing to him. |

If the ranking is wrong it is most likely wrong about item 2: pending
invitations are a guess about volume, since nobody has looked at that surface
and it may simply be empty.

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
