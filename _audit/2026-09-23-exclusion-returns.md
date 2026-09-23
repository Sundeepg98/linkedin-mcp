claude-opus-5-5[1m]

# Exclusion returns -- the hidden work put back into the pending count

**CORRECTS:** `_audit/_census/jobs.md` -- 38 of the slice's 48 exclusions returned to GAP with each blocker named, J 25, J 29 and J 30 re-filed MEASURED-ABSENT, 7 kept on written grounds; GAP 56 to 94.
**CORRECTS:** `_audit/_census/profile.md` -- 98 of the slice's 113 exclusions returned to GAP with each blocker named, the profile editors, Open To Work and the unnamed settings pages among them; 15 kept on written grounds; GAP 55 to 153.
**CORRECTS:** `_audit/_census/messaging-and-content.md` -- 40 of the slice's 50 exclusions returned to GAP with each blocker named, the mention and tag rows among them; 10 kept on written grounds; GAP 77 to 117.
**CORRECTS:** `_audit/_census/network.md` -- 69 of the slice's 97 exclusions returned to GAP with each blocker named, N 23 moved to COVERED-UNFIRED because a shipped tool reads it, 27 kept; GAP 86 to 155.
**CORRECTS:** `_audit/2026-09-23-exclusion-audit.md` -- N 136 has a tracked measurement that audit did not cite, so all 7 MEASURED-ABSENT rows are recorded, not 6; and P M3 cites the delete key in its own cell, so 20 lifted rows are held by nothing, not 21.

**Lane R, 2026-09-23, worktree off `master` at `f89bd29`. OFFLINE throughout: no
browser, no LinkedIn, no page load.**

**THE ANSWER.** Of the 315 rows outside the census denominator, **245 are back in
GAP** with the blocker that stands in each one's way named in its own cell, **1**
(`N 23`) is COVERED-UNFIRED because a shipped tool reads it, **3** move from a
wave's retirement to MEASURED-ABSENT, the state their cells report, and **59
stay EXCLUDED-RULED** -- 51 re-decided and kept on one of the census's four
written grounds, cited, and 8 held by the operator's own 2026-09-04 ruling and
left untouched. `N 136` stays MEASURED-ABSENT and now cites a measurement.
**The pending count moves from 274 to 519 GAP rows, and the achievable surface
from 389 rows to 635.** The operator asked whether the pending count was exact;
it was short by 245 rows of work nothing written ruled out.

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
the row says so; GAP is how the census says "not decided", and 245 rows had
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

**73 return to GAP, 45 stay out on a written ground, 3 move to MEASURED-ABSENT.** Six of
the 45 were re-decided on the cold pass (section 8).

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

DECIDED (orchestrator-delegated, 2026-09-23): **six acts routed through a
member's profile are KEPT, on ground two as his 2026-09-04 ruling reads it** --
`N 35` (unfollow from their profile), `N 66` (follow an interest from their
Interests section), `N 144` to `N 147` (reports of a member's profile). Each
capability's ONLY route is that member's own profile page, and loading one is
the act `load_a_third_partys_profile_to_measure_a_control` names: the key's own
words say "for a measurement", and `readonly.py` records his 2026-09-04 ruling
taking third-party profiles off the boundary with "`PERMANENTLY_FORBIDDEN` names
the act" -- for any load, because a load leaves the member a viewer record. That
is the same basis as `N 2`, an act the same ruling holds. **These six were GAP
in this lane's first commit and went back on the cold pass (section 8):** a blocker
that reads "a route off the profile is unmeasured" cannot be met for a
capability defined by its profile route, which is the sign it was an exclusion
and not a blocker.

DECIDED (orchestrator-delegated, 2026-09-23): `N 34` and `N 36` return to GAP.
Following a person and unfollowing a connection are also offered off the
profile -- a person's card in the admitted people search, a post's author
controls in the feed -- so his ruling closes one ROUTE of each, not the act.
Blocker: those routes are unmeasured, and follows are acts he approved on
2026-08-23.

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
| a self-only reversible toggle | 25 | `J 76`, `M M24`, `M M35`, `M M36`, `M M41`, `M M50`, `N 78`, `N 117`, `N 140`, `P C7`, `P M10`, `P N4`, `P N5`, `P N6`, `P N7`, `P N8`, `P N10`, `P N11`, `P N15`, `P N16`, `P N17`, `P N18`, `P N20`, `P N23`, `P N24` -- changes only what he sees or receives |
| a toggle that changes what OTHER members see of him or can do toward him | 37 | `J 74`, `J 75`, `M M37`, `M M42`, `M M46`, `M C52`, `M C73`, `M C88`, `M C89`, `N 67` to `N 75`, `N 77`, `N 115`, `N 116`, `N 137`, `N 138`, `N 139`, `N 142`, `N 159`, `N 170`, `P B10`, `P D7`, `P E8`, `P M8`, `P N19`, `P N21`, `P N26`, `P O4`, `P O6-O20`, `P O21` |

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
    N           86         155            97 -> 27                   3 ->  3
    all        274         519           308 -> 59                   7 -> 10

`N 23` adds one COVERED-UNFIRED row on `network.md` (5 to 6). The stated-row
population is 704 before and after: no row entered or left the census.

**EXPECTED PIN MOVES -- NOT RE-PINNED HERE, BY INSTRUCTION.** Each was measured
on this worktree after the moves:

* `scripts/census_completion.py` PINNED: `gap` 274 to 519, `out_of_scope` 315 to
  69, `achievable` 389 to 635, `adjudicated` 430 to 185, `delivered_broad` 96 to
  97, `unfired` 21 to 22, `gap_read` 67 to 101, `gap_write` 151 to 324,
  `gap_unknown` 56 to 94. **`capabilities_achievable` prints 635 and is 649**:
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
  raises on `M M3` for the same reason. Across all four slices **169 of the 245
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

* **`_audit/_census/exclusion-basis.tsv`** loses the 246 lines whose rows left the
  out-of-scope states, re-files 9 kept rows onto the ground that holds them and
  moves the six profile-routed acts of section 3.6 from EXTENDED to his plain
  scope, writes the ground into every kept row's note, and turns `J 25`, `J 29`,
  `J 30` and `N 136` into M+ lines citing tracked measurements. 69 lines, one per
  row.
* **`scripts/check_exclusion_basis.py`**: one new family, ACCOUNT-END-SUBSTRINGS,
  for `P N28` and `P N29`; the `apply_job` WriteSpec added as OFF-DOMAIN-FORM's
  third source, since it is the ground `J 66` and `J 67` stand on; and **an
  `EMPTIED` declaration** for the 29 families that now hold no row, each with its
  reason. A family that holds nothing can no longer fail, and the registry's own
  test demanded each be used "or say why"; deleting them would have taken the
  record of who made each ruling with them. A row filed under a declared-empty
  family is now a problem naming the row. The checker exits 0: 69 rows, 0
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

**The budget was one pass, and it was spent once.** A child re-decided 20 rows
drawn by a seeded random sample (seed 20260923) of the 301 rows this lane
re-decided; the 8 rows held by the operator's own ruling and the 6 recorded
MEASURED-ABSENT rows, which this lane did not touch, were outside the draw. It
read the census and the rulings register only as they stood at `f89bd29`, under
the rule of section 1 written out in full, and was forbidden this document, the
exclusion-basis table, its checker and tests, and every commit after `f89bd29`.
Its file is `_audit/_scratch/exclusion-returns/cold-verify.tsv` in this lane's
worktree, which is gitignored and reaches no clone; every row of it is
summarised below.

**It reported one breach of its blindness, unprompted:** a repository-wide grep
for "/jobs/application" returned three lines of `scripts/check_exclusion_basis.py`
-- the family's source anchors, carrying no verdict -- and it says it relied on
none of them.

    rows sampled                     20    this lane: GAP 17, kept 2, MEASURED-ABSENT 1
    STATE agreement               12/20    60%
    both kept: ground agreement     2/2
    settings class agreement        6/6

**All eight disagreements run one way: the verifier kept a row this lane had
returned.** None ran the other way. Each was re-read against the evidence the
verifier cited:

| row | verifier | its ground | adjudication |
|---|---|---|---|
| `N 66` | KEEP | G2, the third-party-profile key | **THE VERIFIER WAS RIGHT.** The capability is defined by its route -- another member's Interests section -- and the operator's 2026-09-04 ruling reads the key as naming any load. The same reasoning reached `N 35` and `N 144` to `N 147`, and all six went back to EXCLUDED-RULED (section 3.6). `N 34` and `N 36` have a route off the profile and stay GAP |
| `J 73`, `P M7` | KEEP | G1, "/jobs/application" | not upheld. The entry names an ADDRESS and entered with the read-only server's first commit with no argument, so INCIDENTAL-CAPTURE-IS-NOT-A-RULING's general form files what it catches as GAP whether or not ruling (b) lifted it -- and the lift of this entry is the exclusion audit's softest inference, which its own blind verifier disputed on `J 71`. The verifier's confidence on `J 73` was MED: the address is inferred |
| `P D22` | KEEP | G1, "/edit/" | not upheld. The operator ruled on 2026-08-31 that the profile editors are allowed (PROFILE-EDITOR-ADDRESSES-ALLOWED), which the verifier's evidence does not weigh; "/edit/" is the named blocker, as the brief required |
| `J 93`, `P I9` | KEEP | G4, no url of 237 reaches the Open To Work editor | not upheld. No url is not unreachable: the editor opens as a modal from a control on his profile, which Amendment A1 of the 2026-09-19 conventions ruling calls the standing case of a click route where no url route exists; and he approved Open To Work on 2026-08-23 |
| `N 19` | KEEP | G4, R1's badge cost | not upheld. A cost is not unreachability, and the reset of the invitation badge on `/mynetwork/` is DERIVED from the notifications and messaging badges -- `linkedin_connections`' own docstring says the sub-page's cost has never been measured |
| `P K4` | KEEP | G1, "verification" | not upheld. "verification" is one of the six word entries added on 2026-09-03 as the settings family's second gate, a class filter for addresses below `/mypreferences/d/`, and not an entry aimed at verifying a workplace |

**After adjudication the pass agrees on 13 of 20.** The seven that remain are one
disagreement, repeated: the verifier read a boundary entry or a measurement as a
ground wherever it reached the row, and this lane read the census's own general
form, which files an address filter's catch as a blocker. Section 1 draws that
line, and these seven are where it could reasonably be drawn the other way. Each
is a GAP row whose cell names the entry as its blocker, so moving any of them is
one edit, and the orchestrator can make it.

## 9. GATES RUN AND NOT RUN

**RUN, on `ab26c14` and `af677b9`:**

* `scripts/check_exclusion_basis.py`: **exit 0** -- population 69, table 69,
  structural problems 0, **untraced 0, lifted 0**. It shipped red at 26 and 27.
* `tests/test_exclusion_basis.py`: 37 passed; then the same file against three
  mutations of the `EMPTIED` machinery, each red (INSTRUMENTS section 64).
* `scripts/count_census_states.py`: GAP J 94, P 153, M 117, N 155 -- 519 of 704
  stated rows; EXCLUDED-RULED 55 plus `XR` 4; MEASURED-ABSENT 10.
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
* **Run 2, on `e53bfac`: REFUSED on the same nine and nothing else -- 9 failed,
  2162 passed in 273s** over 45 test files; the one file more is the
  register-number guard `_audit/INSTRUMENTS.md` pulls in, green. Run 3 gates
  the commit carrying this section, and its result is in the lane's final
  report, because a document cannot record the gate run on the commit that
  contains it.
* **Beyond the gate's selection**, 20 census-adjacent test files the lane chose
  by hand: 338 passed, 1 failed -- `tests/test_gap_rows_on_refused_addresses.py`,
  `EXPECTED_GAP_ROWS` 4 to 55, section 6.

**NOT RUN:** by the gate, 172 of 216 test files, about 3929 of 6094 tests; it is
a local, Windows-only signal and CI's three platforms are the certifier, and
nothing was pushed. **Deliberately not run:** anything touching LinkedIn, a
browser, port 9224 or `_state/` -- nothing here needs them.

## Integration 2026-09-24

**THE ORDER, AND WHAT DISK SHOWED WHEN IT RAN.** The coordinator's integration
order of 01:15 was conditional on this branch's head being 10c7696 with a clean
tree; 10c7696 is a commit of this branch and does not resolve on master until
this branch merges. Sampled before the first step: that head, a clean tree, and
`master` at `001f70b`, 56 commits past the base `f89bd29`. Master had not moved
again when this section was written, so the order ran as written: `001f70b` was
merged into this branch, and every figure below is re-derived from the merged
tree, none carried over from a forecast.

### I.1 The merge -- eight paths both sides had touched

The four census slices, `_audit/INSTRUMENTS.md`, and the three generated files
`_audit/INDEX.md`, `_audit/RULINGS.md` and `_audit/_census/blocker-map.tsv`.

* **The census, row by row.** Since the base this lane changed 276 rows (J 48,
  P 106, M 41, N 81) and master 44 (J 8, P 12, M 8, N 16). A row one side
  changed took that side. A script then compared every row of the merged
  slices with the side that changed it: no mismatch. Master's four state moves
  arrived as master wrote them -- `J 18`, `J 39`, `P G6` and `N 47`, each GAP to
  COVERED-UNFIRED.
* **ONE ROW CHANGED ON BOTH SIDES, AND IT IS REPORTED HERE AS THE ORDER ASKS:
  `M C42`.** Base EXCLUDED-RULED; this lane GAP (section 2.1); master kept
  EXCLUDED-RULED and rewrote the cell, so this was not an append. Master's text
  narrows the premise to other people's posts -- for his own, the item keys
  come from linkedin_my_activity_items (bucket-1 FIRE 1) -- and then says in
  its own words that the state is not re-decided there and is "left to an
  explicit decision". Master's text is kept whole, and the decision it leaves
  open is taken as section 2.1 took it, in a note appended after master's
  text. DECIDED (orchestrator-delegated, 2026-09-24): `M C42` is GAP; for his
  own posts it waits on one live open of one of his permalinks, for anybody
  else's on a reader that hands out an item key. Undoing it is one state cell.
* **`_audit/INSTRUMENTS.md`**: master's sections 63 and 65 and this lane's 64
  interleave by number, nothing of either side dropped. Section 64.3 is new at
  the merge and registers the own classes of I.3.
* **The generated files** were taken from master, staged with every resolved
  path, and regenerated at the end until a second sweep changed nothing: the
  index, the rulings register and the blocker map.
  `_audit/_census/completeness-candidates.tsv`, which only master had touched,
  was NOT regenerated, and disk is why. The harvest reads the captures of every
  worktree on this box, and a dry run written to the scratchpad measured 35
  candidates added, every one unread, 15 dropped and 86 changed -- other
  lanes' live captures, not this merge. The committed-table test refuses an
  unread candidate, and admitting candidates is another lane's work; master's
  file stands.

### I.2 The read-address table, re-derived rather than pasted

A child re-derived the 34 new bucket-3 lines against the merged census and the
shipped boundary. Reviewed, and applied whole: 98 lines,
`scripts/check_read_addresses.py` GREEN on 98 of 98. 34 lines added (ADMITTED
4, REFUSED 23, NEEDS-SESSION 7); two removed -- `N 171`, NOT-AN-ACT now, and
`N 183`, a setting and so a write row; and the notes of `N 99`, `N 177` and
`N 178` rewritten for the D3 and roster rulings, the boundary itself unchanged.
Every one of the 34 boundary verdicts matched the phase-one draft. Two
judgement cells moved on re-reading the merged cells: `M C42`'s gate READER to
MEASURE (its own-post half waits on the same live open `M C29` names) and
`N 39`'s basis NAMED to MEASURED (its cell says the address was found live).

### I.3 Triage -- a returned row outside the ledger is its own class

The order's rule, applied: a returned row that is not one of the 409 rows the
blocker map's spine holds is tallied as its own class, read off its own cell,
and the ledger is not grown. 169 of the 245 returned rows are outside it.

* `scripts/triage_messaging_gap_rows.py`: the class RETURNED-OUTSIDE-LEDGER
  goes only to a row with no map line whose cell carries this lane's marker
  ("RETURNED TO GAP ... BY LANE R ... BLOCKER, NAMED:"); a row with neither
  still comes back unjoined, and a new test plants exactly that. The slice: 117
  GAP -- R 13, W 101, R+W 3 -- 14 of them in the own class.
* `scripts/triage_read_gap_rows.py`: the verdict RETURNED on the 28 returned
  read rows of P and N, and CONTROL 9, which refuses that verdict on a row
  whose cell lacks the marker, with a plant that proves it fires. `N 171` and
  `N 183` left the read-GAP set; ten rows the registered calls have since
  decided (`N 99`, `N 100`, `N 102`, `N 104`, `N 132`, `N 161`, `N 177`,
  `N 178`, `N 179`, `P C8`) are annotated ruling by ruling.
* `_audit/_census/write-classes.tsv`: 174 new write rows -- 173 returned, and
  `N 183`, a write row since batch 3 -- classed by a child: R1 5, R2 12, R3
  157. Reviewed, one line changed. `N 62` had
  borrowed a ledger name for a different cost (a profile change notifying the
  network); it is queued now with the own class, its cause -- R1's /mynetwork/
  badge cost, and no WriteSpec for topics -- written in its ground. `P O6-O20`
  could not be cited at all, because the checker's own-row form took no range
  id: `scripts/check_write_classes.py` takes one now, and a new test shows a
  range that names no row is convicted by the same resolver. 325 lines --
  16 R1, 35 R2, 274 R3 -- GREEN.
* `_audit/_census/jobs-directions.tsv`: the 38 returned jobs rows directed by a
  child -- R 7, W 28, R+W 3 -- reviewed and applied whole; GREEN on 92 of 92.
  Its close calls were read and kept: the Easy Apply family filed W as one
  refusal, `J 77` a pure read, `J 112` on the alumni tab rather than the
  school root, `J 115` gated MEASURE, `J 134` NEEDS-SESSION.

### I.4 Rulings batch 3, applied to the rows

From `_audit/2026-09-24-rulings-search-verticals-rosters-passive-costs.md`:

* **MEMBER-ROSTERS-AS-BOUNDED-READS.** `N 165`, `N 188`, `N 189` were already GAP
  and had left the exclusion-basis table in this lane's first phase; each
  cell now cites the ruling and names what it waits on: an admission under its
  five conditions, and a reader. The family ROSTER-ENUMERATION stays declared
  empty, its reason extended with the ruling.
* **D5-PASSIVE-COST-IS-NOT-A-ROW.** `N 171` is EXCLUDED-RULED as NOT-AN-ACT, with
  its exclusion-basis line under a new family of that name in
  `scripts/check_exclusion_basis.py` (anchors: the ruling's heading and "It
  governs `N 171`"), and a REOPENER: LinkedIn drawing a control that turns the
  exposure on or off. The cost is recorded on the join rows `N 163` and
  `N 164`. `N 183` is direction W and stays GAP, awaiting admission by name.
  The table: population 70, 70 lines, 0 untraced, 0 lifted, 0 problems.
* **D3-UNREGISTERED-REFUSAL-IS-NOT-A-RULING.** `RULING_BLOCKED_NAMED` in
  `scripts/census_completion.py` is empty and kept, with the reason. `N 99`,
  `N 177` and `N 178` are GAP on an admission and a reader, and their address
  notes say so. `N 178`'s live proof loads another member's profile, so the
  member is one the operator names -- written in its cell and its note.

### I.5 Every pin moved, and the ones that did not

`scripts/census_completion.py` PINNED, 24 of 37 moved, each with its reason in
the file:

    achievable               389 -> 634     gap_write          150 -> 324
    adjudicated              434 -> 190     jobs_admitted        9 ->  11
    b1_no_ruling              15 ->  16     jobs_dir_r          26 ->  33
    b2_d3_rows                 3 ->   0     jobs_dir_rw          3 ->   6
    b3_admitted               40 ->  44     jobs_dir_w          25 ->  53
    b3_blocked_on_nothing      8 ->   9     jobs_gap            54 ->  92
    b3_needs_session           6 ->  13     jobs_needs_session   1 ->   2
    b3_no_address              2 ->   1     jobs_refused        19 ->  26
    b3_refused                16 ->  38     out_of_scope       315 ->  70
    capabilities_achievable  389 -> 648     unfired             25 ->  26
    delivered_broad          100 -> 101
    gap                      270 -> 514
    gap_read                  66 ->  98
    gap_unknown               54 ->  92

Unmoved: stated_rows 704, capabilities 762, delivered_strict 75,
cannot_deliver 19, gap_ambiguous 0, b3_undetermined 2, b1_standing 10,
b1_relayed 0, b1_pending 0, b1_released 6, and the three jobs zeros.

* **`capabilities_achievable` is 648, not the 634 the file would have printed.**
  The file counted every collapsed capability out of scope by assumption, and
  its own check flagged `P O6-O20` as GAP. `COLLAPSED` now asserts GAP for that
  row, and the extras are counted in or out by each row's state: 762 - (70 +
  44) = 648. The printed sentence that all 58 collapsed capabilities are
  EXCLUDED-RULED is derived from the states now.
* `PINNED_B1_ROWS`: `N 23` joins the rows no ruling holds (a read, returned to
  COVERED-UNFIRED). `RULING_BLOCKED_NAMED`: three rows to none.
* `tests/test_triage_instrument.py` `EXPECTED_NOW`: 77 {R 10, W 65, R+W 2} to
  117 {R 13, W 101, R+W 3}. `tests/test_gap_rows_on_refused_addresses.py`
  `EXPECTED_GAP_ROWS`: 4 to 55. `tests/test_write_classes.py`, the split: (11,
  23, 117) to (16, 35, 274).
* `_audit/_census/pointer-graph.tsv`, re-pinned on the merged tree: 30 pointers
  read a different donor kind, the thirty section 6 forecast by name, and 12
  more changed only the pointing row's recorded state (`J 61`-`J 65`,
  `M C14`-`M C16`, `M C66`, `P B3`, `P F4`, `P G3`). `--check` PASS.
* `tests/census_row_pin.json`: no move, 704 rows.

### I.6 The figures, measured on the merged tree

    GAP                514 of 704 rows    J 92, P 152, M 117, N 153
    out of scope        70                EXCLUDED-RULED 56 + XR 4, MEASURED-ABSENT 10
    achievable         634                capabilities 648 of 762
    delivered, strict   75                COVERED-PROVEN, CP included
    delivered, broad   101                with COVERED-UNFIRED 26

### I.7 Unresolved, and handed back

* **The P-R block's 44 settings-family capabilities in `profile.md` were NOT
  re-decided.** Read by this lane's rule they would await admission by name, as
  34 of the 35 settings rows now do; but they carry no row ids, the block's
  bullets group them rather than list them, and at least one (Delete Data) is
  a deletion that ground two keeps. They have to be itemized into rows before
  they can be decided one at a time. Until then they are counted with `P1`,
  outside the achievable capability surface; no row figure depends on them,
  and `capabilities_achievable` would rise by at most 44. The block's own
  paragraph and section 6 of `profile.md` now say this in-line, with no line
  added, so no row moved a line.
* **The seven cold-verifier disagreements of section 8 stand as adjudicated.**
  Each is a GAP row whose cell names its entry, one edit to move.
* **Informational:** the returned profile-editor rows cite their `/edit/` entry
  as the blocker and do not cite SELF-PROFILE-EDITS-NOT-OUTWARD as a release, so
  bucket 2 counts 0 such rows; it will matter when one of them is built.
  `write-classes.tsv`'s split of settings rows between profile-setting and
  notification-preference is the classing child's granularity, not a
  precedent.

### I.8 The children at the merge

Three implementer children, each given one closed table, a copy to write, and
the rule that they commit nothing: the read addresses, the write classes, the
jobs directions. Every output was reviewed against its checker and by diff
before it replaced a tracked table. Two applied whole; one with the single
`N 62` line changed.

### I.9 Gates

Recorded in the next commit on this branch: a document cannot record the gate
run on the commit that contains it, and the house rule is commit first, then
gate.
