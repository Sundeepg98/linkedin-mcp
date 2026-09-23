claude-opus-5-5[1m]

# Exclusion returns -- the hidden work put back into the pending count

**CORRECTS:** `_audit/_census/jobs.md` -- 38 of the slice's 48 exclusions returned to GAP with each blocker named, J 25, J 29 and J 30 re-filed MEASURED-ABSENT, 7 kept on written grounds; GAP 56 to 94.
**CORRECTS:** `_audit/_census/profile.md` -- 98 of the slice's 113 exclusions returned to GAP with each blocker named, the profile editors, Open To Work and the unnamed settings pages among them; 15 kept on written grounds; GAP 55 to 153.
**CORRECTS:** `_audit/_census/messaging-and-content.md` -- 40 of the slice's 50 exclusions returned to GAP with each blocker named, the mention and tag rows among them; 10 kept on written grounds; GAP 77 to 117.
**CORRECTS:** `_audit/_census/network.md` -- 75 of the slice's 97 exclusions returned to GAP with each blocker named, N 23 moved to COVERED-UNFIRED because a shipped tool reads it, 21 kept; GAP 86 to 161.
**CORRECTS:** `_audit/2026-09-23-exclusion-audit.md` -- N 136 has a tracked measurement that audit did not cite, so all 7 MEASURED-ABSENT rows are recorded, not 6; and P M3 cites the delete key in its own cell, so 20 lifted rows are held by nothing, not 21.

**Lane R, 2026-09-23, worktree off `master` at `f89bd29`. OFFLINE throughout: no
browser, no LinkedIn, no page load.**

**THE ANSWER.** Of the 315 rows outside the census denominator, **251 are back in
GAP** with the blocker that stands in each one's way named in its own cell, **1**
(`N 23`) is COVERED-UNFIRED because a shipped tool reads it, **3** move from a
wave's retirement to MEASURED-ABSENT, the state their cells report, and **53
stay EXCLUDED-RULED** -- 45 re-decided and kept on one of the census's four
written grounds, cited, and 8 held by the operator's own 2026-09-04 ruling and
left untouched. `N 136` stays MEASURED-ABSENT and now cites a measurement.
**The pending count moves from 274 to 525 GAP rows, and the achievable surface
from 389 rows to 641.** The operator asked whether the pending count was exact;
it was short by 251 rows of work nothing written ruled out.

**AUTHORITY.** The operator ruled at 18:13 (OUTWARD-ACTS-NEED-THE-OPERATOR) that
only acts toward other people, or irreversible ones, need him, and that every
other call is the orchestrator's, made on evidence and overridable. Moving a row
between GAP and EXCLUDED-RULED fires nothing, touches nobody and is one edit to
undo, so each decision below is such a call, made on the orchestrator's behalf
and written as a DECIDED line with its evidence. None is a `RULED:` line:
family-level decisions are for the orchestrator to register at merge.

**A RETURNED ROW IS NOT A CLAIM THAT ANYBODY WANTS IT BUILT.** It is a claim that
nothing written rules it out. The pending count now includes it, and its cell
says what stands in the way -- a boundary entry, a missing reader, an unmeasured
surface, or a question only the operator can answer. Where the answer is his,
the row says so; GAP is how the census says "not decided", and 251 rows had
been saying "decided" without a decider.

---

## 0. THE POPULATIONS, DERIVED

Taken with the shipped parse (`count_census_states.cells` / `state_of`) and
joined to the exclusion-basis table at `f89bd29`, one population per row, no row
in two. The brief's numbers reproduce exactly:

    slice of this lane                              rows   how derived
    1  hidden: class C                               26    class C
       hidden: lifted, nothing else holds it         21    B-lifted, remaining=-
       hidden: lifted, a contradicted basis left      1    M C18, remaining /edit/
       hidden: his recorded words contradict         58    op=CONTRARY
                                                    ---
                                                    106
    3  agent-ruled, never made or contradicted       95    op=NO, plus the four R1-held lifted rows
       his family stretched past its words           26    op=YES and scope not YES, plus M M5
                                                    ---
                                                    121
    4  unnamed settings pages                        73    SETTINGS-BY-NAME, scope=YES
    kept, outside every slice                         8    his 2026-09-04 ruling, plainly in scope
    5  MEASURED-ABSENT without a tracked source       1    N 136
       MEASURED-ABSENT, recorded                      6    untouched
                                                    ---
                                                    315

## 1. THE RULE APPLIED, STATED SO IT CAN BE ARGUED WITH

**A row stays out only on one of the census's four written grounds**, as the
census writes them in its own section 2 (EXCLUDED-RULED-ADMISSION): **(1)** an
entry on `readonly._FORBIDDEN_URL_SUBSTRINGS` aimed at the capability -- a class
filter that catches the address incidentally is a blocker, not a decision
(INCIDENTAL-CAPTURE-IS-NOT-A-RULING); **(2)** a key in
`writes.PERMANENTLY_FORBIDDEN` naming the act; **(3)** a WriteSpec refusing in
its own words; **(4)** an audit passage establishing the capability
unreachable. Everything else went back to GAP with the blocker named.

**THREE READINGS OF THOSE GROUNDS, each a judgement the orchestrator can
override:**

* **Ground four includes LinkedIn's own documentation, read directly, when it
  says the capability cannot be done from a desktop browser** -- a live stream
  that needs an external encoder, a voice-only mode, a mobile address book --
  and a capability defined as somebody else's act. No page load could measure
  those more directly than the article that defines them.
* **A key or entry whose recorded ground a later operator ruling withdrew does
  not hold a row.** Ruling (b) permits connect, message, apply, post and opening
  messaging, so a refusal whose recorded reason was that the package does not do
  those acts no longer stands; his 2026-08-30 dissolution of the policy bucket,
  recorded in `writes.py`, does the same for a ground that is taste. A key that
  still names an act nobody has withdrawn -- deletion above all -- keeps its row,
  and moving it is his.
* **A compound row goes to GAP when any half of it is open work**, and its note
  says which half a written ground still refuses: "add / edit / delete" returns,
  and the delete half stays refused by `delete_or_withdraw_anything`.

**HOW EACH BLOCKER IS NAMED.** The census's convention, from the
INCIDENTAL-CAPTURE ruling: a filter catching the address is named as *refused by
a class filter written for a different purpose*, with the entry and what it was
written for; otherwise the note names the code symbol, the missing artifact, the
unmeasured surface, or the question that is his. Every moved cell opens its note
with `RETURNED TO GAP 2026-09-23 BY LANE R` and this document's section number,
so a reader of the row reaches the reasoning without a second search.

## 2. SLICE 1 -- THE 106 HIDDEN ROWS

**103 return to GAP. `P M3` and `P I11` stay out on the delete key, and `N 23`
moves to COVERED-UNFIRED (section 2.5).**

### 2.1 The rows with no traceable basis -- 14 of the 26 (11 more are in 2.4, and N 23 is in 2.5)

DECIDED (orchestrator-delegated, 2026-09-23): `J 50`, `J 51`, `J 52` return to
GAP. The job-tracker stage allowlist admits saved, applied and draft and calls
the rest "deliberately absent -- nothing builds them": allowlist silence, which
the census's own section 2 says is not a reason. Blocker: a reader and an
allowlist entry per stage.

DECIDED (orchestrator-delegated, 2026-09-23): `J 115` returns to GAP.
`linkedin_job_detail`'s docstring says the hiring-team rail is not read; a
docstring that declines a field rules nothing out. Blocker: a shaped reader (the
rail is third parties' names), and a connect or message to a team member is an
outward act ruling (b) permits, fired only at a member he names.

DECIDED (orchestrator-delegated, 2026-09-23): `P D26` returns to GAP -- the same
shape: `linkedin_my_profile` declines the strength meter in its docstring, and
whether `/in/me/` still draws one is unmeasured.

DECIDED (orchestrator-delegated, 2026-09-23): `M C33` and `M C35` return to GAP.
The reactions menu has never been opened, so no reaction but the default is
aimable; the ON-state label has never been observed, so no selector exists for
the inverse. The delete key's own text says `react_to_item` does not lean on it.

DECIDED (orchestrator-delegated, 2026-09-23): `M C42` returns to GAP. The
permalink address is admitted on the operator's 2026-08-31 ruling and no tool
returns an item's urn to put in it. Blocker: a reader that publishes the urn of
an item it read.

DECIDED (orchestrator-delegated, 2026-09-23): `M C47` returns to GAP: the three
drafts addresses are refused by allowlist silence alone.

DECIDED (orchestrator-delegated, 2026-09-23): `M C13` returns to GAP. The
"Schedule post" control is recorded in `publish_post`'s own caveat as a BUTTON
opening a modal, so the control is drawn; nobody has opened the modal and no
WriteSpec schedules. `any_loop_sweep_or_scheduled_write` forbids this server
scheduling its own writes; one attended write that asks LinkedIn to publish
later is read here as outside it -- the reading most open to his override.

DECIDED (orchestrator-delegated, 2026-09-23): `M M3` returns to GAP. Its only
citation is an untracked lead brief that tells its reader not to act on it, and
the cited line is a build instruction for `send_message`, not an exclusion.
Blocker: no WriteSpec switches the dispatch radio; an InMail spends a metered
credit whose balance LinkedIn does not draw (`N 157`).

DECIDED (orchestrator-delegated, 2026-09-23): `P B3`, `P B5`, `P G3` return to
GAP. `P B5` and `P G3` read "same ruling" and point by position at a different
address and at a COVERED row; the upload ban under all three was opened by the
operator on 2026-09-04. Blocker: a WriteSpec each, and the photo editor's and
the Featured add flow's controls, which nobody has opened. `P B5`'s delete half
stays refused by the delete key.

### 2.2 The 22 lifted rows -- 21 return, `P M3` stays (section 2.5)

Ruling (b) withdrew the read-only rule, the apply, connect and InMail cut, and
DO-NOT-OPEN-MESSAGING. Every row below rested on one of them and nothing else.

DECIDED (orchestrator-delegated, 2026-09-23): `N 9`, `N 11`, `N 24`, `N 25`,
`N 26`, `N 27`, `N 28`, `N 168`, `M C69` return to GAP. The "invitation",
"/invite" and "/connect" entries exist, in `readonly.py`'s own words, to stop
this server SENDING invitations -- the purpose ruling (b) withdrew. Blockers:
the Sent tabs need a reader and the badge gate `linkedin_connections` already
carries for a `/mynetwork/` sub-page; sort, search and filter of the connections
list are query variants the anchored exemption does not admit; inviting to a
group needs its own url, write sanction and ruling (GROUPS-ADDRESS-BUYS-NO-WRITE)
and goes only to connections he names.

DECIDED (orchestrator-delegated, 2026-09-23): `J 71`, `J 73`, `P M1`, `P M2`,
`P M4`, `P M5`, `P M6`, `P M7` return to GAP. "/jobs/application" entered with
the read-only server's first commit, no argument recorded; it fenced a read-only
server and ruling (b) withdrew both halves of its purpose. Blockers: a reader
each, a WriteSpec for the upload and the opt-out; `J 71`'s delete half stays
refused by the delete key.

DECIDED (orchestrator-delegated, 2026-09-23): `N 156`, `N 158` return to GAP.
R9's root is the operator's own 2026-08-23 cut, which ruling (b) withdrew.
Blocker: the compose route to a member outside his network is unmeasured, an
InMail spends a credit whose balance is not drawn, and a send goes only to a
member he names.

DECIDED (orchestrator-delegated, 2026-09-23): `N A2` returns to GAP: "/follow"
is a read-only-era fence with no argument recorded, and the account administers
no Page on record, which is the second blocker.

DECIDED (orchestrator-delegated, 2026-09-23): `M C18` returns to GAP. "/post/"
fell with the read-only rule; "/edit/" still refuses every editor but the intro
editor. Editing a published post is an outward write ruling (b)'s POST reaches,
and no WriteSpec exists.

### 2.3 The 58 rows his words contradict -- 57 return, `P I11` stays

DECIDED (orchestrator-delegated, 2026-09-23): the 22 profile editors return to
GAP -- `P D2`, `P D5`, `P D6`, `P D8`, `P D9`, `P D11` to `P D23`, `P E2`, `P E3`,
`P G4`, `P G5`. The operator ruled on 2026-08-31 that `/in/<member>/edit/` and
the profile editors are allowed (PROFILE-EDITOR-ADDRESSES-ALLOWED in the rulings
register), his own profile only. **The blocker, named as the brief asked: the
"/edit/" entry on `readonly._FORBIDDEN_URL_SUBSTRINGS`**, which still refuses
every editor but the intro editor -- the one exact-url exemption -- because the
implementing wave declined to narrow it on 2026-08-31. The `update_profile_field`
WriteSpec also refuses until a field inside the editor has been observed.
`readonly.py` is lane L1's and was not touched here. Compound rows carry their
delete or remove half as still refused by the delete key; three carry `drag_to`,
an unsanctioned mutation class.

DECIDED (orchestrator-delegated, 2026-09-23): 19 Open To Work rows return to GAP
-- `J 89` to `J 97`, `P B6`, `P I2` to `P I10`. The operator approved Open To
Work on 2026-08-23, and the 2026-08-25 audit files it UNMEASURED, to be measured
rather than refused. Blocker: the `set_open_to_work` WriteSpec refuses in its own
words -- NEVER LOADED, no capture of the modal exists and the click that would
first show it could also change it -- and no tool is registered. Owed: one
capture of the modal with him watching, as the 2026-09-05 profile-modals audit
already lists. The frame and audience rows note the frame his employer can see.

DECIDED (orchestrator-delegated, 2026-09-23): 16 recommendation rows return to
GAP -- `N 119` to `N 124`, `N 126` to `N 128`, `P F2` to `P F4`, `P F6` to
`P F9`. `endorse_or_recommend` names recommendations, but its surviving ground
counted ENDORSE controls (profile.md finding 7.4), and the operator dissolved its
policy ground on 2026-08-25. Blocker: the key in `writes.py` (lane L4's), and no
census of recommendation controls has ever been taken; a recommendation goes
only to a member he names. `N 125` and `P F5`, deleting a recommendation, stay
out on the delete key.

### 2.4 The specific contradictions the brief named

**The 22 profile editors** -- section 2.3; the "/edit/" refusal is named in every
cell and `readonly.py` is untouched.

DECIDED (orchestrator-delegated, 2026-09-23): **`P B2`** returns to GAP. The
operator was asked on 2026-09-04 and opened uploads FULLY -- profile photo, post
media, message attachments -- as `readonly.py` records. The row's remaining
blocker is plain: the upload verb is sanctioned at one call site and is not in
`writes.PERFORMABLE`, so a WriteSpec, a gate and a consent line are owed. Its
delete half stays refused by the delete key.

DECIDED (orchestrator-delegated, 2026-09-23): **the eight rows moved on
2026-09-20** -- `P B4`, `P C2` to `P C6`, `P N12`, `P O5` -- return to GAP. The
registered ruling INCIDENTAL-CAPTURE-IS-NOT-A-RULING names exactly these
addresses and rules the rows stay GAP with the blocker named; each moved
2026-09-20 citing neither that ruling nor the same-day verdict beside it. The
blockers, in the ruling's own form: refused by a class filter written for a
different purpose -- the bare "settings" word (six rows), "/uas/" (`P N12`),
"/create" (`P O5`). A narrowing needs a measured blast radius, which that ruling
says, and nobody has scoped it.

DECIDED (orchestrator-delegated, 2026-09-23): **`J 53` and `J 84`** return to
GAP. They cited "the mutation-verb denylist", which is `readonly.WRITE_VERBS`, a
check on tool NAMES: it also lists apply, save and follow, whose writes ship, so
it refuses no capability. Blocker: no tool and no WriteSpec for archiving or for
the per-job hide; the control for the second is drawn in this repository's own
fixtures.

### 2.5 The three rows of the 106 that do not go to GAP

DECIDED (orchestrator-delegated, 2026-09-23): **`P M3` stays out, on ground two.**
Deleting a saved resume is a deletion, and the row's own cell cites
`delete_or_withdraw_anything` and "/delete" beside the lifted "/jobs/application".
The exclusion audit's table records nothing else holding it; its own cell says
otherwise. Re-filed to the delete-key family.

DECIDED (orchestrator-delegated, 2026-09-23): **`P I11` stays out, on ground
two.** Deleting the Open To Work card is a deletion, and its cell already cites
the delete key; the NEVER LOADED half no longer holds it. Re-filed.

DECIDED (orchestrator-delegated, 2026-09-23): **`N 23` moves to COVERED-UNFIRED,
not GAP.** GAP means no tool, and a tool exists: `linkedin_connections` loads
`/mynetwork/invite-connect/connections/`, which the boundary admits through an
anchored exemption for "/invite" and "/connect", and returns one row per
connection behind a before-and-after badge gate. No live fire of it is on
record, so the state is UNFIRED, and one call that returns rows moves it on.

## 3. SLICE 3 -- THE 121 CONTESTABLE ROWS

**79 return to GAP, 39 stay out on a written ground, 3 move to MEASURED-ABSENT.**

### 3.1 The R1 and R2 rows

DECIDED (orchestrator-delegated, 2026-09-23): the ten R1 rows return to GAP --
`N 3`, `N 15`, `N 17`, `N 18`, `N 21`, `N 22`, `N 32`, `N 62`, `N 97`, `N 98`.
R1 is a wave's refusal of an ADDRESS, `/mynetwork/`, on a badge cost DERIVED
from sibling surfaces; the cost to the inviters is unmeasured, and measuring it
spends the badge. A decision about an address is a blocker for the capabilities
living at it. Two facts weigh against keeping it closed: `linkedin_connections`
already loads a `/mynetwork/` sub-page behind a before-and-after badge gate, and
the orchestrator's NOTIFICATIONS-UNREAD-SPEND call of today permits clearing his
own unread badge. The acts among these are ruling (b)'s CONNECT and MESSAGE,
fired only at members he names; the reads return third parties and need a shaper.
**If the inviters' side of the cost is real, admitting the address is his call,
because the cost lands on other people.** That is the question each cell names.

DECIDED (orchestrator-delegated, 2026-09-23): `N 13`, `N 14`, `N 16`, `N 19`
return to GAP. Their R2 half was lifted by ruling (b) and their R1 half is the
paragraph above; `N 16`, ignoring an invitation, is an act toward the inviter.

### 3.2 Agent rulings whose own words do not reach the row

DECIDED (orchestrator-delegated, 2026-09-23): `J 60` to `J 65` return to GAP.
`linkedin_apply_job` refuses a form that draws an advance control because steps
never observed are "the one guess this server does not make" -- a refusal that
measuring the steps would lift, not an exclusion of applying, which ruling (b)
permits. Blocker: a capture of a multi-step form and a reading per step.

DECIDED (orchestrator-delegated, 2026-09-23): `M C14`, `M C15`, `M C16` return to
GAP. The measurement found no LINK from the composer to the scheduled list; the
same passage records "Schedule post" as a button opening a modal, so the list's
route is unmeasured rather than closed.

DECIDED (orchestrator-delegated, 2026-09-23): `P I12` and `J 99` return to GAP.
"Zero of 237 urls reach one" measures url routes only; the Open To Work editor is
the standing case of a surface reached by a click with no url, Amendment A1 of
the 2026-09-19 conventions ruling already narrowed `J 99`'s reopener to a click
route, and none has been tried. This moves the example the container-propagation
ruling was built on; the propagation rule itself is untouched.

DECIDED (orchestrator-delegated, 2026-09-23): `P A9` returns to GAP. The control
is one of two unnamed switches with no attribute this server reads; a write route
is unbuilt, not measured closed. The A2 and A4 precedent would file it
COVERED-CANNOT-DELIVER once `linkedin_update_profile_field` has fired.

DECIDED (orchestrator-delegated, 2026-09-23): `M C44` returns to GAP -- the
article route is unused because its publish control has no measured anchor,
which rules nothing out -- and `M M39` returns to GAP: an away message is text he
writes and reads first, so `auto_accept_or_auto_reply`'s "did not read" does not
reach it; it is a messaging setting awaiting admission by name.

### 3.3 `N 106`

DECIDED (orchestrator-delegated, 2026-09-23): `N 106` returns to GAP. A Gmail
import completes on Google's consent screen, and the off-site sentence it was
retired on was written about applicant-tracking systems and never put to him.
Importing uploads other people's contact data, so firing it is his; building it
is not ruled out. `N 108` follows it (section 3.5).

### 3.4 Agent families the census's grounds do reach, and the ones they do not

DECIDED (orchestrator-delegated, 2026-09-23): **KEPT on ground two** -- the 20
rows filed under the delete key: `M C17`, `M C19`, `M C22`, `M C31`, `M C62`,
`M C77`, `M M12`, `M M26`, `N 10`, `N 12`, `N 29`, `N 96`, `N 110`, `N 113`,
`N 125`, `N A14`, `N A15`, `P E5`, `P F5`, `P K7`. `delete_or_withdraw_anything`
names the act. The exclusion audit found the key meets neither survival bar the
`writes.py` header attributes to him, impossible with a measurement or
unattended, and five reversibility claims rest on it; **deletion is
irreversible, which OUTWARD-ACTS-NEED-THE-OPERATOR reserves to him, so the key
stays until he moves it.** Also kept on ground two: `N 131` and `P O2`
(`deanonymise_a_viewer`), `M M32` (`any_loop_sweep_or_scheduled_write`),
`P P1` (`mark_notifications_read`, measured impossible).

DECIDED (orchestrator-delegated, 2026-09-23): **`J 69` is kept on ground two,
re-filed by act-class.** Discarding a draft application destroys it; the delete
key covers destruction "at any confirm level", the act-class `N 96` and `N A14`
are already filed on. Its old citation, "never pressed from here", was the
weaker half.

DECIDED (orchestrator-delegated, 2026-09-23): **`J 66` and `J 67` are kept on
ground three.** The `apply_job` WriteSpec refuses the off-site route in its own
words -- "THE OFF-SITE ROUTE IS NOT THIS SERVER'S TO PERFORM". Ruling (b) permits
applying on his LinkedIn account; a form on another company's domain is not that.
The 2026-08-25 audit records this refusal was never put to him, so each cell now
names his ruling as the reopener.

DECIDED (orchestrator-delegated, 2026-09-23): `M C20` and `M C21` return to GAP.
`repost_or_share` still refuses in code, but its recorded grounds are "not among
the capabilities asked for" -- ruling (b) now asks for posting -- and that the
item republished is not his, a taste ground the operator dissolved on
2026-08-30; its menu has never been opened. Blocker: the key in `writes.py`
(lane L4's) and an unmeasured menu; a repost goes only for an item he names.

DECIDED (orchestrator-delegated, 2026-09-23): `M C43`, `N 165`, `N 188`, `N 189`
return to GAP. Each rests on a LEAD's ruling -- post text read as counts and
relations only; member rosters not enumerated -- that the operator never made,
and a lead's ruling is not one of the four grounds. Both rulings still ship
(`feed.py`'s signature; the events boundary's root-only test) and are now the
rows' named blockers; a text or roster read returns third parties' names, so it
needs his ruling and a shaper.

DECIDED (orchestrator-delegated, 2026-09-23): `J 112` returns to GAP. The lead
refused DERIVING a school slug from a name read off his profile; the row's own
reopener -- a caller supplying the identifier -- needs no new rule, and the
school address is admitted. Blocker: no tool takes a caller-supplied school id.

DECIDED (orchestrator-delegated, 2026-09-23): `N 38` returns to GAP. "/follow"
was written against follow ACTS and catches the people-follow list; `readonly.py`
calls that capture "luck, not design" and asks that the filter never be
shortened for it -- an argument about the filter, not about the list. An
exact-url exemption, as the connections list has, is the route.

### 3.5 The twelve retirement families -- 31 rows here, `N 106` in 3.3

The 2026-09-05 retirements were a wave's answers to a queue defined as needing
his. Each was re-decided on the four grounds; the strongest survive.

DECIDED (orchestrator-delegated, 2026-09-23): **KEPT on ground four** --
`J 133` (practice by voice: a voice-only mode), `J 140` (a hirer's voice or
video screening, `a10376002`), `J 141` (a control inside that session; an
unreachable container carries to the controls on it), `P L5` and `M C59` (a
Live needs an external encoder, `a568503`), `P A23` (desktop cannot record,
`a550527`, and its one desktop verb is a deletion), `N 105` (a mobile address
book) and `N 107` (a step inside that flow), `P N30` and `P N31` (a form
LinkedIn defines as filed by another person about a deceased member). **Kept on
ground two:** `N 109`, re-filed to `any_loop_sweep_or_scheduled_write`, which its
cell already cited.

DECIDED (orchestrator-delegated, 2026-09-23): **MEASURED-ABSENT, re-filed** --
`J 25`, `J 29`, `J 30`. Their cells report a measurement -- the control at 1/1/0
on four settled captures and two live reads, every target needle zero -- not a
decision, which is the `N 157` precedent. Out of scope either way; the state now
says why.

DECIDED (orchestrator-delegated, 2026-09-23): **returned to GAP** --
`J 132`, `J 134`, `J 135` (the practice product documents a typed mode, "read
and type out your responses", so the voice-only ground does not reach them;
`J 134` is the retirement's own reopener, and its hand adjudication in
`reason-kind-adjudications.tsv` is retired with it); `J 139` (whether the
hirer's practice accepts typing is unmeasured); `J 142` (declining is an act
toward a hirer, fired only for an invitation he names); `J 143`, `J 144`,
`J 145` (messages to a hirer: ruling (b) permits messaging, the route is
unmeasured, and `linkedin_send_message` cannot deliver at HEAD); `N 108` (a step
after `N 106`'s import); `N 152` (a report accusing another member: his to file);
`N 50` (a button on another domain, the follow itself shipped as
`linkedin_follow_company`); `M M40`, `M M51` (whether the assist fills an
editable composer is unmeasured); `J 17` (a persistent geolocation grant against
a parameter that already serves); `P N13` (a challenge page the boundary does not
admit; ANSWERING one stays refused by `any_anti_detection_technique`); `M M19`
(an audio file is unmeasured and message attachments were opened on 2026-09-04);
`M C71` (an irreversible spend, his per act).

### 3.6 His family rulings, stretched past their words -- 26 rows

DECIDED (orchestrator-delegated, 2026-09-23): the six mention and tag rows and
`M C11` return to GAP -- `M C10`, `M C11`, `M C28`, `M C55`, `M C66`, `M C86`,
`M M23`. His typing ruling says text the caller supplied; an agent read it as
forbidding an entity the server commits through a typeahead, while
MENTION-COMPOSITION-RULING, a lead's, permits the mechanism. **Whether a mention
the caller NAMES is text the caller supplied is his question**, and until he
answers it these rows are open, not ruled. Blocker: that question, the shipped
surface promise in `tests/test_no_write_tool_names_a_third_party.py`, and a
typeahead name match measured dead on 2026-09-03. `M C11` is simpler: a '#' he
types is his own text, and whether LinkedIn makes it an entity is unmeasured.

DECIDED (orchestrator-delegated, 2026-09-23): the eight acts routed through a
member's profile return to GAP -- `N 34`, `N 35`, `N 36`, `N 66`, `N 144`,
`N 145`, `N 146`, `N 147`. His 2026-09-04 ruling removed third-party profile
pages from the boundary, because a load leaves the member a viewer record; that
closes the ROUTE the census names, not the act. Blocker: a route from an admitted
surface, unmeasured; follows are acts he approved on 2026-08-23, and reports are
accusations whose text and target are his.

DECIDED (orchestrator-delegated, 2026-09-23): **`N 141` is kept on ground two,
by act-class.** Blocking destroys the connection and removes the member's
endorsements and recommendations, and unblocking restores none of them
(network.md section 8.6) -- destruction, which the delete key covers, the
act-class `N 29` is already filed on.

DECIDED (orchestrator-delegated, 2026-09-23): `M M5` returns to GAP: its InMail
half was his 2026-08-23 cut, which ruling (b) withdrew, and its profile route is
the paragraph above.

DECIDED (orchestrator-delegated, 2026-09-23): the nine settings-family rows his
words do not reach return to GAP -- `P K1` (a section of his own profile, not a
setting at all), `P K2` to `P K6` (verification flows that complete off-platform
-- DigiLocker, a work inbox, Microsoft, a licence, an SMS code -- each his to
complete), `P N25` (a data-sharing setting awaiting admission by name), `N A7`
and `N A8` (Page-admin settings on an account that administers no Page; turning
automatic invitations on starts invitations to other people, which is his call).

## 4. SLICE 4 -- THE UNNAMED SETTINGS PAGES

His ruling, 2026-08-31, admits ONE NAMED settings page below the settings index
at a time. **It admits by name; it rules none out.** So every unnamed page is
open work waiting on his naming, and "awaiting admission by name" is the blocker
each of these cells now carries.

DECIDED (orchestrator-delegated, 2026-09-23): **69 of the 73 return to GAP**, the
blocker "awaiting admission by name", each classed for the build lanes:

| class | rows | what it means for a build |
|---|---:|---|
| a pure read | 7 | `J 77`, `N 39`, `N 143`, `P M9`, `P N9`, `P N22`, `P O22` -- reads his own settings state; `J 77` and `P M9` carry a delete half the delete key still refuses |
| a self-only reversible toggle | 26 | `J 76`, `M M24`, `M M35`, `M M36`, `M M41`, `M M50`, `M C52`, `N 78`, `N 117`, `N 140`, `P C7`, `P M10`, `P N4`, `P N5`, `P N6`, `P N7`, `P N8`, `P N10`, `P N11`, `P N15`, `P N16`, `P N17`, `P N18`, `P N20`, `P N23`, `P N24` -- changes only what he sees or receives |
| a toggle that changes what OTHER members see of him or can do toward him | 36 | `J 74`, `J 75`, `M M37`, `M M42`, `M M46`, `M C73`, `M C88`, `M C89`, `N 67` to `N 75`, `N 77`, `N 115`, `N 116`, `N 137`, `N 138`, `N 139`, `N 142`, `N 159`, `N 170`, `P B10`, `P D7`, `P E8`, `P M8`, `P N19`, `P N21`, `P N26`, `P O4`, `P O6-O20`, `P O21` |

**Two flags the table cannot carry.** Seven of the self-only rows are CREDENTIAL
or recovery controls -- `P N4`, `P N5`, `P N6`, `P N7`, `P N8`, `P N10`,
`P N11` -- and `P N10` can end this server's own session; they are self-only and
not low-risk. And the visible-to-others class is read broadly: a toggle deciding
who may invite, message, follow, endorse or embed him changes what other members
can do, even where it changes nothing they see. `P N25` and `M M39` (section 3)
are settings too: self-only and visible-to-others respectively.

DECIDED (orchestrator-delegated, 2026-09-23): **four of the 73 stay out**, because
they are not unnamed settings awaiting admission at all. `P N28` (close the
account): "/close-accounts" entered the forbidden tuple aimed at it, and closing
an account is destruction the delete key covers -- grounds one and two. `P N29`
(hibernate): "/hibernate-account" entered aimed at it, with its argument beside
it -- one of "the only two on it that are not undoable by re-running the opposite
tool" -- ground one. `P N27` (merge or close a duplicate account) and `J 87`
(delete the expressed-interest record): destruction by act-class, ground two.

## 5. `N 136` -- SOURCED, AND THE STATE STANDS

DECIDED (orchestrator-delegated, 2026-09-23): **`N 136` stays MEASURED-ABSENT and
its class becomes M+.** The brief said return it unless the measurement can be
sourced. It can: the profile-views recapture of 2026-09-20, section 6, is a live
rendered-text and raw-source census of `/analytics/profile-views/` -- 14 control
hits, so the probe could speak; "location" zero in 143,556 characters of served
source; every non-zero target structurally a filter caption or a viewer
headline. The exclusion audit read the row as unrecorded because the row's cell
cited the two earlier sources and not this one. **Its limit is one press wide**
and is now the row's reopener: the unpressed Show more analytics button, whose
own view name says it reveals a further section.

## 6. TOTALS, THE NEW GAP, AND THE PIN MOVES

    slice   GAP before  GAP after   EXCLUDED-RULED (XR incl.)   MEASURED-ABSENT
    J           56          94            48 ->  7                   1 ->  4
    P           55         153           113 -> 15                   2 ->  2
    M           77         117            50 -> 10                   1 ->  1
    N           86         161            97 -> 21                   3 ->  3
    all        274         525           308 -> 53                   7 -> 10

`N 23` adds one COVERED-UNFIRED row on `network.md` (5 to 6). The stated-row
population is 704 before and after: no row entered or left the census.

**EXPECTED PIN MOVES -- NOT RE-PINNED HERE, BY INSTRUCTION.** Each was measured
on this worktree after the moves:

* `scripts/census_completion.py` PINNED: `gap` 274 to 525, `out_of_scope` 315 to
  63, `achievable` 389 to 641, `adjudicated` 430 to 179, `delivered_broad` 96 to
  97, `unfired` 21 to 22, `gap_read` 67 to 101, `gap_write` 151 to 330,
  `gap_unknown` 56 to 94. **`capabilities_achievable` prints 641 and is 655**:
  `P O6-O20` stands for fifteen capabilities and is GAP now, and the file's
  COLLAPSED check says so with a "!!" line -- the fourteen extra are counted out
  of scope by an assumption the check exists to catch. That file is the cleanup
  wave's. The six bucket-3 pins go unchecked until the address table covers the
  34 new read rows (next item).
* `_audit/_census/read-addresses.tsv` (not touched, by instruction): 34
  read-direction rows entered bucket 3 with no line -- bucket 3 goes 67 to 101.
  A proposed table with the 34 lines appended is in section 7.
* `tests/test_gap_rows_on_refused_addresses.py`, `EXPECTED_GAP_ROWS` 4 to 55: 51
  returned rows backtick an address the read gate refuses on a forbidden
  substring. That reporter reads a forbidden-substring entry as the census's bar
  for EXCLUDED-RULED; INCIDENTAL-CAPTURE-IS-NOT-A-RULING reads a class filter
  catching an address as a blocker. The rows are GAP under the second, which is
  the registered one; the pin moves.
* `tests/test_triage_instrument.py`, `EXPECTED_NOW` for the messaging slice: 77
  GAP `{R 10, W 65, R+W 2}` to 117 `{R 13, W 101, R+W 3}`. **Its join test is
  not a count and will not re-pin away**: it requires every messaging GAP row to
  join `_audit/_census/blocker-map.tsv`, whose spine is the 409 rows that were
  GAP at the 2026-09-03 freeze. 14 returned messaging rows were already
  excluded at that freeze, so they have no line (`C13`-`C16`, `C18`, `C20`,
  `C21`, `C33`, `C35`, `C42`, `C44`, `C47`, `M3`, `M39`), and the headline test
  raises on `M M3` for the same reason. Across all four slices **175 of the 251
  returned rows were never in the 409-row ledger at all; 76 were**, and those 76
  still carry their ledger blocker in the map. Whether the map's spine grows or
  the triage treats a row outside it as its own class is a decision for whoever
  holds those two files.
* `_audit/_census/pointer-graph.tsv` (`scripts/measure_pointer_graph.py`): 30
  pinned positional pointers read a different donor verdict, because this lane
  appended a note to the donor row. The donors are `J 50`, `J 66`, `J 74`,
  `J 89`, `M C20`, `P B4`, `P C4`, `P D9`, `P D14`, `P I2`, `P I4` and `P M1`;
  26 of the 30 pointing rows are returned rows themselves, and the other four
  are `J 67`, `P I11` and `P M3`, kept on grounds their own cells now state, and
  `P D10`, a COVERED-CANNOT-DELIVER row whose "same shape as D4" the resolver
  reads by position as `P D9`.
* `tests/census_row_pin.json`: no move.

## 7. WHAT ELSE THIS LANE CHANGED, AND WHY EACH HAD TO

* **`_audit/_census/exclusion-basis.tsv`** loses the 252 lines whose rows left the
  out-of-scope states, re-files 9 kept rows onto the ground that holds them,
  writes the ground into every kept row's note, and turns `J 25`, `J 29`, `J 30`
  and `N 136` into M+ lines citing tracked measurements. 63 lines, one per row.
* **`scripts/check_exclusion_basis.py`**: one new family, ACCOUNT-END-SUBSTRINGS,
  for `P N28` and `P N29`; the `apply_job` WriteSpec added as OFF-DOMAIN-FORM's
  third source, since it is the ground `J 66` and `J 67` stand on; and **an
  `EMPTIED` declaration** for the 29 families that now hold no row, each with its
  reason. A family that holds nothing can no longer fail, and the registry's own
  test demanded each be used "or say why"; deleting them would have taken the
  record of who made each ruling with them. A row filed under a declared-empty
  family is now a problem naming the row. The checker exits 0: 63 rows, 0
  untraced, 0 lifted, 0 structural problems.
* **Four test files re-pointed, none weakened.** `tests/test_exclusion_basis.py`
  planted into `P D5`, `N 119` and `N 23`, which left the table -- now `N 10` and
  `N 111`, and its used-or-says-why test asserts both directions against
  `EMPTIED`, with a new test that convicts a row filed under a declared-empty
  family. `tests/test_a_retired_row_rests_on_a_live_assertion.py` and
  `tests/test_c43_rests_on_the_feed_content_ruling.py` bound seven rows to
  EXCLUDED-RULED; they now require GAP AND that each cell names the shipped
  assertion as its blocker, so deleting the assertion still turns them red.
  Emptying the first table was not available: an empty parameter set is a skip,
  and an undeclared skip fails this repository's CI.
  `tests/test_writeoff_kinds_are_derivable.py`'s moot-adjudication control used
  `J 134`, the one real row-level adjudication, which this lane retired with its
  row -- the control now plants its own adjudication, proves the plant green,
  then moves the row out and expects the red.
* **`_audit/_census/reason-kind-adjudications.tsv`**: the `J 134` judgement is
  retired because its row left the write-offs, on the very fact it named.
* **The exclusion audit** carries a back-pointer to this document for the two
  counts section 5 and the table's `P M3` line gave.
* **The read-addresses proposal** -- the full table plus 34 proposed lines,
  produced by a child against a copy and checked green by
  `scripts/check_read_addresses.py --table` -- is at
  `_audit/_scratch/exclusion-returns/read-addresses-proposal.tsv` in the main
  checkout, which is gitignored and reaches no clone; it is offered to whoever
  owns the tracked table, and nothing here depends on it.

## 8. VERIFICATION -- ONE COLD PASS

IN PROGRESS.

## 9. GATES RUN AND NOT RUN

**RUN, on `ab26c14` and `af677b9`:**

* `scripts/check_exclusion_basis.py`: **exit 0** -- population 63, table 63,
  structural problems 0, **untraced 0, lifted 0**. It shipped red at 26 and 27.
* `tests/test_exclusion_basis.py`: 37 passed; then the same file against three
  mutations of the `EMPTIED` machinery, each red (INSTRUMENTS section 64).
* `scripts/count_census_states.py`: GAP J 94, P 153, M 117, N 161 -- 525 of 704
  stated rows; EXCLUDED-RULED 49 plus `XR` 4; MEASURED-ABSENT 10.
* `scripts/pin_census_rows.py --check`: no drift, 704 rows. Not re-pinned, and
  nothing asked it to be.
* `scripts/classify_writeoff_reasons.py --check` and
  `scripts/check_contingent_writeoffs_carry_a_reopener.py`: PASS; the three
  generated files regenerated until a second sweep changed nothing, then each
  `--check`ed clean; the pre-commit identity gate, 0 hits on both commits.
* **`scripts/impact_gate.py --against f89bd29`, run 1 on `ab26c14`: REFUSED --
  9 failed, 2156 passed in 243s**, 44 test files plus the 17 corpus-wide guards.
  All nine are the expected moves of section 6 and nothing else:
  `tests/test_read_addresses.py` 3 (the 34 uncovered bucket-3 rows),
  `tests/test_triage_instrument.py` 4 (`EXPECTED_NOW` and the frozen-map join),
  `tests/test_pointer_graph_guard.py` 2 (the 30 moved pointers). No wall-clock
  budget test refused, so none needed a lone re-run.
* **Beyond the gate's selection**, 20 census-adjacent test files the lane chose
  by hand: 338 passed, 1 failed -- `tests/test_gap_rows_on_refused_addresses.py`,
  `EXPECTED_GAP_ROWS` 4 to 55, section 6.

**NOT RUN:** by the gate, 172 of 216 test files, about 3929 of 6094 tests; it is
a local, Windows-only signal and CI's three platforms are the certifier, and
nothing was pushed. **Deliberately not run:** anything touching LinkedIn, a
browser, port 9224 or `_state/` -- nothing here needs them.
