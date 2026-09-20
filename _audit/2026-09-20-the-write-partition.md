# THE WRITE PARTITION: 101 WRITE-DIRECTION GAP ROWS, AND THE 87 THAT STAY

Scope: the write-direction GAP rows of `_audit/_census/profile.md` and
`_audit/_census/network.md`. `messaging-and-content.md` is a sibling wave's and
`jobs.md` has no direction column; neither was touched.

**HEADLINE: 14 of 101 moved. 87 stay GAP, and that is the finding.** The
reachable-ceiling document reports that over 70% of the answerable GAP is
write-direction and asks whether that backlog is really a ceiling. Measured row
by row against the shipped code, it is mostly neither. It is **unruled** -- 73
of the 101 are capabilities nobody has ever weighed, for which no passage in
this repository says anything at all, and a wave that moved them would have been
inventing product decisions to improve a number. **52 of the 87 stayed rows
contain no phrase the census's own reason classifier recognises as a reason of
any kind**, which is the sharpest single number here.

---

## 1. THE DENOMINATOR, MEASURED

Taken with `scripts/count_census_states.py`'s own row filter and `classify()`,
so the extraction and the counter cannot disagree about where a cell ends.

    WRITE-DIRECTION GAP ROWS IN SCOPE, BEFORE          101

      profile.md                                        46   (45 W + 1 R/W)
      network.md                                        55   (55 W)

The brief said 100. The extra is `P M11` (Resume Builder), whose direction cell
is `R/W` -- the single `R/W` row the reachable-ceiling split already reported.
It is counted here and it did not move.

---

## 2. THE PARTITION, DERIVED FROM THE CODE

Every set below was obtained by importing `linkedin_server.writes` and
`linkedin_server.readonly`, never read off prose. Probe scripts are in the
gitignored `_state/`; the numbers reproduce from a clone by re-running them.

    writes.PERFORMABLE                                  12 actions
    writes.writes_enabled()                             False
    writes.SANCTIONED_WRITES                            13 specs
      (the 12 performable, plus set_open_to_work, which
       holds url_template=None and is NOT performable)
    writes.PERMANENTLY_FORBIDDEN                         9 keys
    writes.UPLOAD_ACTIONS                                0   -- see section 6
    server.READABLE_SETTINGS                             1 key ("dark mode")
    readonly._FORBIDDEN_URL_SUBSTRINGS                  33 entries
    readonly._ALLOWED_URL_PATTERNS                      41 patterns

### The four classes, with exact integers over the 101

    CLASS 1  EXPLICITLY CUT -- an existing ruling names the
             capability, its act-class, or its address family        14   -> MOVED
    CLASS 2  SANCTIONED BUT SWITCHED OFF -- capability is in
             PERFORMABLE and the shipped tool reaches it              0
    CLASS 3  NEVER CONSIDERED -- no tool, no passage                 73   -> STAYS GAP
    CLASS 4  CONTINGENT on a fact about the account or the world,
             and NOT otherwise ruled                                 14   -> STAYS GAP
                                                                    ---
                                                                    101

**CLASS 4 IS NAMED RATHER THAN COUNTED**, so it can be argued with. Measured by
running the SHIPPED signal table (`classify_writeoff_reasons.SIGNALS`) over the
87 stayed rows' reason cells, the fourteen that fire any WORLD-FACT /
ACCOUNT-FACT / PROCESS-FACT signal are:

`P A14`, `P A15`, `P A22`, `P B7`, `P D24`, `P D27`, `P D29`, `P E6`, `P H1`,
`P L6`, `P M11`, `N 114`, `N 169`, `N 187`.

Class 4 rows stayed GAP. **A GAP row owes no reason, so it cannot carry a stale
one and the reopener guard does not reach it** -- which is exactly why parking a
contingent capability in GAP is honest and parking it in EXCLUDED-RULED without
a trigger is not. Nothing was moved into a write-off in order to shrink GAP.

Two of the 14 in class 1 are ALSO contingent (`N A7`, `N A8`: the Premium
entitlement). They are counted once, in class 1, because the boundary is what
holds them; both carry a shouted `REOPENER` anyway, and section 5 says why.

### THE SAME 87, SPLIT BY WHAT THEIR CELLS ACTUALLY SAY

    CONTINGENT signals fire                    14
    ONLY our-own signals fire                  21   (17 of them fire ONLY `no-tool`)
    NO SIGNAL FIRES AT ALL                     52
                                              ---
                                               87

The third line is the honest shape of this backlog: **52 of 87 write-direction
GAP rows contain no phrase the census's own reason classifier recognises as a
reason of any kind.** And the 17 that fire only `no-tool` are cells reading
literally *"no tool, no reason"* -- GAP's own definition restated. So 69 of 87
say, in the corpus's own vocabulary, that nobody has considered them.

**THE CAVEAT IS REAL AND IS NOT HIDDEN.** That classifier is a keyword sweep
and normally reads only WRITE-OFF rows; GAP is deliberately outside its scope.
It cannot tell a cell that CITES a ruling from one that MENTIONS one -- its own
docstring records the `ruling` pattern firing 157 times before it was narrowed
for exactly that reason. So the three-way split above measures WHAT THE CELLS
SAY, and the four-class partition above it is my adjudication, which the
row-by-row disposition in section 4 exposes to checking.

### CLASS 2 IS ZERO, AND THAT IS A RESULT RATHER THAN AN ABSENCE

The brief's second class was expected to be the large one: twelve actions are
BUILT, `writes_enabled()` is False, so any row naming one of them is neither a
gap nor an exclusion. Cross-referenced mechanically (`_state/performable-coverage.md`),
**exactly two of the 101 rows mention a performable action at all**, and each
says in its own cell why the action does not reach it:

| row | action named | why it does not reach the row |
|---|---|---|
| `N 5` | `send_invitation` | *"`linkedin_send_invitation(member, confirm_token)` takes no note parameter"* -- the capability is the NOTE, which the spec has no field for |
| `N 47` | `follow_company` | the tool acts from `/jobs/view/{id}/`, which names an employer by SLUG; this row is the Page route, addressed by numeric id, and `follow_company`'s own `residue` names the gap |

Everything the twelve actually reach is ALREADY banked outside GAP -- `N 1`,
`N 46`, `N 48` and `N A6` COVERED-UNFIRED, `N 155` and `P A2` COVERED-CANNOT-DELIVER,
`P N2` COVERED-PROVEN. **So the write GAP is not the twelve waiting for a flag.
It is the ROUTES and VARIANTS the twelve do not address**, and no amount of
turning writes on would move any of it.

(One caveat on that cross-reference, stated rather than left to be misread: it
matches the needle anywhere in the row, so `update_setting` shows 35 matching
rows -- those are settings-family rulings QUOTING the tool, not coverage.)

---

## 3. THE 14 THAT MOVED, AND WHY EACH IS AN APPLICATION AND NOT AN INVENTION

Every one rests on a passage that already existed. Nine rest on a boundary
entry added to `readonly.py` on **2026-09-03** -- the day after `profile.md` was
written -- which the census has never been re-read against.

### 3.1 The eight profile rows: a blocker cell that asserts an absence the shipped boundary contradicts

`P B4`, `P C2`, `P C3`, `P C4`, `P C5`, `P C6` all sit on
`/public-profile/settings`. `P N12` sits on `/uas/login`. `P O5` sits on
`/badges/profile/create`. Between them those cells assert:

* *"which no forbidden substring catches and no allowlist pattern admits"* (B4)
* *"no tool, no reason"* (C2)
* *"caught by no substring, named nowhere in this repo"* (N12)
* *"caught by no substring, on no allowlist pattern, named nowhere in this repo"* (O5)

and section C's own header asserts *"Nothing else in this repo names it
either."*

**EVERY ONE OF THOSE CLAIMS IS FALSE, AND TWO OF THE THREE ADDRESSES ARE NAMED
VERBATIM IN THE BOUNDARY'S OWN COMMENT AS THE MEMBERS THAT MOTIVATED THE
ENTRY.** From `readonly.py`, in the block added 2026-09-03:

```
* A SECOND SPELLING. ``/public-profile/settings`` has no trailing
  slash, so ``"/settings/"`` -- slashes on both sides, present since
  the beginning -- does not match it. A gate that turns on a trailing
  slash is a spelling filter, not a ruling.
* A LEGACY NAMESPACE. ``/uas/`` is LinkedIn's old auth tree and the
  exact sibling of the ``/psettings/`` three lines up ...
```

```
THE VERB THAT WAS NEVER ON THIS LIST. ... the verb that MAKES
something has not. ``/badges/profile/create`` is the member that
exposed it, and the class is every creation surface on the account.
```

**NOT INFERRED FROM THE LISTS -- PUT THROUGH THE SHIPPED GATE.**
`readonly.assert_read_url` was called on each address and each refusal names its
own entry (`_state/stale-premises.txt`):

    REFUSED  /public-profile/settings   contains 'settings'
    REFUSED  /badges/profile/create     contains '/create'
    REFUSED  /uas/login                 contains '/uas/'

and the same run carries NEGATIVE CONTROLS that must still refuse and do --
`/mynetwork/invitation-manager/` on `invitation`, `/company/<slug>/people/` on
the allowlist -- so the gate is discriminating rather than refusing everything.

The verdict is **co-location under a ruled address**, which is how all 123 of
`profile.md`'s family-ruling rows are already filed, and `C7` -- one row below
`C6`, on `/psettings/guest-controls` -- is already EXCLUDED-RULED on exactly
this shape. Section 6's arithmetic is carried onto each moved row verbatim:
nobody weighed these capabilities on their merits, and no moved row claims
anybody did.

The section C header is corrected IN PLACE by appending, with the superseded
sentences left standing, because a reader who arrives from a document citing
them needs to find what they were told.

**THE MOVE IS NOT NEW AND THE CENSUS ALREADY NAMES THE BAR.** `N 38` did
exactly this, on exactly this evidence, and wrote the rule down:

> *"THE BLOCKER RECORDED HERE NAMES THE WRONG GATE, AND THE RIGHT GATE IS A
> WRITTEN RULING. ... The real refusal is the SECOND, independent gate: the
> address contains `/follow`, an entry on `readonly._FORBIDDEN_URL_SUBSTRINGS`,
> checked BEFORE the allowlist -- measured by calling `is_read_url` on it. ...
> **A forbidden-substring entry is this census's own named bar for
> EXCLUDED-RULED.**"*

`N 39` and `N 44` are filed the same way and by the same instrument. So these
eight rows are the rows that sweep had not reached, not a new bar.

### 3.2 The six network rows: two rulings taken to their verdict

| row | capability | ruling applied | precedent already in the same table |
|---|---|---|---|
| `N 96` | Clear your search history | **R5** `delete_or_withdraw_anything` -- *"destruction is not a write this design covers, at any confirm level"* | `110` delete all imported contacts; `29` remove a 1st-degree connection |
| `N A14` | Remove an attendee from an event you organize | **R5**, on the identical verb | `29` |
| `N A15` | Withdraw an event invitation | **R5 + R2** -- withdrawal is named by the key, and `/withdraw`, `/invite`, `invitation` are all forbidden substrings | `10` withdraw a pending invitation you sent; `12` |
| `N A2` | Follow another org's Page as your Page | the row's OWN blocker, `/follow` on the forbidden tuple, checked before the allowlist | R2's fifteen rows |
| `N A7` | Turn on automatic invitations (Premium) | the row's OWN blocker, `/settings/` + bare `settings`, plus **R11** | R11's twenty-one rows |
| `N A8` | Turn off automatic invitations (Premium) | same | same |

`N A2`, `N A7`, `N A8` and `N A15` each already NAMED a boundary entry as their
blocker and then recorded GAP anyway. Moving them takes the row's own stated
blocker to the verdict this census's vocabulary says it produces; it adds no
new reason.

**WHAT DELIBERATELY DOES NOT HOLD THE THREE ADMIN ROWS.** `network.md`'s own
prose records that the Page-admin absence rests on a FRAGMENT capture and is
*"a fact about the capture, not about the account"*. None of these three
exclusions uses it, and each says so in its cell, so a later re-measurement of
the admin question cannot silently invalidate them.

---

## 4. THE 87 THAT STAY, AND WHAT EACH WOULD NEED

    STAYED GAP                                           87
      profile.md                                         38
      network.md                                         49

### 4.1 DELIBERATE PRIOR ADJUDICATION -- do not re-litigate (10 rows)

A previous wave examined these, wrote the argument into the cell, and chose
GAP. Reversing that on the same evidence is re-litigation, not application.

`P E6`, `P L6`, `N 59`, `N 60`, `N 63`, `N 114`, `N 150`, `N 151`, `N 163`, `N 192`.

**AND THE HARDEST CASE IN THE WHOLE WAVE IS HERE, so it is stated rather than
buried.** `P E6` and `N 114` -- hide or show an endorsement RECEIVED -- both say
the blocker is the `/endorse` forbidden substring, and then argue that the
written reason (`endorse_or_recommend`, about making statements ABOUT another
person) does not reach housekeeping on one's own profile. **That argument
contradicts R2's practice one file over**, where fifteen rows are EXCLUDED-RULED
on substrings the ruling text openly says catch them incidentally -- R2 itself
writes *"two substrings put on the list to stop invitations, catching a read
that has nothing to do with inviting anyone."*

**THE CENSUS THEREFORE HOLDS TWO INCOMPATIBLE PRACTICES ABOUT WHETHER A
FORBIDDEN SUBSTRING ALONE IS A RULING, AND NOBODY HAS RULED BETWEEN THEM.** I
did not, deliberately: the eight rows I moved in 3.1 are ones whose cells assert
the substring does NOT catch them, which is a false-premise correction and needs
no position on this question. **RULING NEEDED. It is worth more than these two
rows** -- it decides the shape of every future boundary-blocked row on both
slices.

### 4.2 PREREQUISITE CHAIN -- a ruling nobody has made (7 rows)

The capability itself sits on an admitted or unruled surface, but reaching it
requires a prior act whose own surface IS ruled out.

| row | capability | the ruled-out prerequisite |
|---|---|---|
| `P A24` | ID name as additional name | an identity verification first (block K, settings-family EXCLUDED-RULED) |
| `P A26` | Website on profile | the contact-info panel, whose own row `A25` was deliberately kept GAP on 2026-09-19 |
| `P A27` | Phone number on profile | same panel |
| `P A28` | Instant messenger accounts | same panel |
| `P A29` | Birthday and its visibility | same panel |
| `N 6` | Re-invite after expiry | knowing an invitation expired, from the Sent surface (R1 + R2) |
| `N 164` | Join a group by responding to an invitation | the invitation itself |

**RULING NEEDED: does a ruling on a capability's PREREQUISITE exclude the
dependent capability?** The census already answers the neighbouring question
YES for CO-LOCATION -- 123 profile rows and R11's twenty-one are filed exactly
that way -- and has never been asked about DEPENDENCY. The two are not the same
shape and I did not assume they were. All seven move together on one word.

### 4.3 SIBLING-OWNED (2 rows)

`N 149` and `N 160` have confirmed twins in `messaging-and-content.md`, which a
sibling wave owns. Their cells already record the twin ids and a queued re-file.
Not touched.

### 4.4 THE REST -- no tool, no passage, nobody considered it

**THE THREE BUCKETS ABOVE ARE CROSS-CUTTING OVERLAYS, NOT A SECOND PARTITION.**
A row can be both deliberately adjudicated and contingent (`P L6`, `N 114`), so
4.1-4.3 do not sum with 4.4 and are not meant to. The partition is section 2's
four classes; these are the reasons a reader would want named.

Everything not called out in 4.1-4.3 is here: **no tool exists, no passage in
this repository bears on it, and nobody has ever weighed it.** It is the real
answer to the reachable-ceiling question -- the write-direction backlog is not
mostly a ceiling and it is not mostly a switched-off capability. It is unruled.

**THREE SUB-PATTERNS INSIDE IT, EACH ONE A RULING SOMEBODY COULD MAKE
CHEAPLY:**

1. **"An address absent from the allowlist" is not a ruling** -- it is an
   address nobody built. **THIS IS NOT MY POSITION; IT IS THE CENSUS'S**:
   `network.md` section 2 says allowlist silence is not a reason, and the
   `N 38` cell restates it -- *"'Not on the allowlist' is allowlist silence,
   which section 2 of this file says explicitly is NOT a reason."* Rows held
   only by silence: `N 4` (no people search), `N 49`, `N 185`, `N 186`,
   `N 187`, `N 190`, `N 191`, `N A1`. The same discrimination is written onto
   the `N A14` cell I moved, where R5 was available as the stronger reason and
   the allowlist half was recorded rather than relied on.
2. **Two-verb rows that a ruling reaches only HALF of.** `P D27` (create /
   delete a secondary-language profile) and `P L3` (create / edit / delete a
   newsletter): R5 reaches the delete half and nothing reaches the create half.
   Closing them needs a SPLIT, which changes the denominator, and the census
   has a precedent for that (`P L2` -> `L2` + `L2b`). **RULING NEEDED: split,
   or leave whole.**
3. **`P I13` was one inference from moving and is deliberately left.** It says
   *"on that same unreachable page"*, and that page (`P I12`) IS
   EXCLUDED-RULED. But `I12`'s entire reason is *"measured: zero of 237 urls
   reach one"* -- which is a statement that NOTHING BUILDS IT, i.e. GAP's own
   definition wearing an exclusion's state. It also fires no signal at all in
   `classify_writeoff_reasons`, so it sits in the UNCLEAR bucket the reopener
   guard neither convicts nor clears. **Propagating from it would compound a
   miscategorisation rather than apply a ruling.** Flagged for the lead;
   `I12` itself was not touched.

---

## 5. THE GUARD, AND THE TWO ROWS THAT OWE IT A TRIGGER

`tests/test_contingent_writeoffs_carry_a_reopener.py` and its script were run
before and after. Both PASS, and the red demonstration still fires all three
reds on the edited corpus.

    contingent write-offs in enforced scope   BEFORE  57, all carrying a reopener
                                              AFTER   59, all carrying a reopener

**THE EDITS WERE PRE-FLIGHTED RATHER THAN ATTEMPTED.** Every drafted reason cell
was put through the SHIPPED classifier and the guard's own strict
`REOPENER\b` marker BEFORE any tracked file was touched
(`_state/preflight_reasons.py`, `_state/draft_reasons.py`). Twelve came back
non-contingent (US-BOUNDARY + US-RULING) and two came back ACCOUNT-FACT on the
`entitlement` signal -- `N A7` and `N A8`, on the word "Premium".

That is the honest verdict and it was not dodged by rewording. Those two rows
carry a two-clause shouted reopener:

1. the `settings` or `/settings/` entry leaving `_FORBIDDEN_URL_SUBSTRINGS`, or
   an exact-url exemption entering `_FORBIDDEN_SUBSTRING_EXEMPTIONS` -- a
   reviewable one-line edit that `tests/test_readonly.py` pins. WHO: whoever
   edits the boundary.
2. the account acquiring both the entitlement and an administered Page, which
   is what would make the SECOND blocker stop applying. WHO: the operator.

**AND THE TRAP THE BRIEF NAMED WAS CHECKED FOR DIRECTLY.** The guard's own
first version went green on a cell reading *"the Help-article half REOPENS
NOTHING"*. Neither new reopener is a sentence about reopening; both are shouted
`REOPENER, NAMED:` clauses stating a condition and an owner, and the pre-flight
reports the strict marker firing on exactly those two drafts and on no other.

### 5.1 THE SELF-CHECK I RAN ON MY OWN TWELVE NON-CONTINGENT VERDICTS

Twelve rows were filed NON-CONTINGENT, which means no reopener is owed. That
verdict is not mine, it is the classifier's -- and the classifier decides
ACCOUNT-FACT from a **closed verb list**, `he (has|had|holds|owns|never|wants)`.
A reason stating a fact about the account with any other verb is called
non-contingent and leaves the guard's scope without anybody noticing. So the
question *"is that list tight enough to be trusted?"* is load-bearing for this
freeze, not a tangent.

Measured over all 324 write-off rows (`_state/probe_accountfact_verbs.py`):

    NON-CONTINGENT write-offs                                257
    of those, saying `he <verb>` with a verb the set misses    17
    of those 17, carrying no shouted reopener                  16

**AND THEN THE NUMBER DEFLATES ALMOST ENTIRELY, WHICH IS THE POINT OF
DISAGGREGATING IT BEFORE REPORTING IT.** Fourteen of the seventeen are the verb
`chooses`, and all fourteen are R4's rows inheriting R4's own sentence --
*"Whether HE chooses to open a profile is his own affair"* -- which is a clause
of OUR prohibition, not a fact about the account. `N 15` is R8's *"a reply in
his name that he did not read"*, the same shape. `N 38` is a US-BOUNDARY row
and correctly non-contingent.

**THAT LEAVES ONE REAL INSTANCE AND IT IS ALREADY PROTECTED.** `P L5` states
*"he clears the >150-follower gate at 275"* -- a numeric account fact, and a
follower count is precisely a thing that changes -- and is classified
NON-CONTINGENT because the verb is `clears`. The same cell also says *"LinkedIn
says outright that no native path exists"*, which the `linkedin-says` needle
misses too (it knows `does not / draws no / offers / no longer / cannot /
makes / retired / redesigns`, not `says`). **The row carries a reopener anyway,
so there is no casualty at HEAD.**

**VERDICT: the mechanism is real, the live casualty count is ZERO, and this
wave's own fourteen are all clean** -- the probe reports `clean` for all
fourteen and confirms the walk found 14 of 14, so a green result there is not a
walk that found nothing. Registered as instrument 43 with the probe, because a
mechanism with no casualties today is exactly the thing that acquires one
quietly.

### 5.2 THREE OTHER GUARDS WENT RED, EACH FOR A CORRECT REASON, AND ONE OF THEM FOUND A ROW INHERITING A FALSE ARGUMENT

The fast gate (`scripts/impact_gate.py`) ran 1588 tests against this change and
refused it on four. None was a false alarm, and none was routed around.

**(a) `test_pointer_graph_guard` -- A ROW NOBODY EDITED NOW RESTS ON A DIFFERENT
ARGUMENT, AND THAT IS THE FINDING.** Three pinned pointers moved:

    P B5 still points at P B4, but P B4's verdict moved
      US-BOUNDARY -> US-BOUNDARY+US-RULING
    P C5 and P C6 still point at P C4, whose verdict moved
      (no signal at all) -> US-BOUNDARY+US-RULING

`P C5`/`P C6` are rows this wave edited, so that half is expected. **`P B5` is
not.** It reads *"Background / banner image add / change / delete -- same
ruling"*, it is EXCLUDED-RULED, and it resolves BY POSITION to `P B4` -- which
until today asserted *"no forbidden substring catches it and no allowlist
pattern admits it"*. **So an already-closed row was inheriting, as its whole
argument, a claim about the boundary that was false.** It now inherits the
corrected one. Nothing about `P B5`'s state changes and its contingency does
not move -- both the old and new verdicts are ours -- but the census was one
edit away from `P B4` being rewritten in a way that silently re-argued a row
two lines below it. Re-pinned deliberately with `--pin`, which the guard's own
failure text instructs and which the commit message states.

**(b) `test_writeoff_kinds_are_derivable::test_a_deleted_ruling_section_is_reported`
-- A RULING HEADING THAT DOES NOT MOVE WITH ITS ROW SET.** R5's heading says
*"Produces 6 rows"* and its row list names six; this wave filed three more
under it. The test convicted the heading within the hour. **R5, R2 and R11 now
carry their new members and their counts** -- 6->9, 15->16, 21->23 -- and the
test's literal moved 6->9 with the reason written into its docstring. The
literal is deliberately NOT derived from the heading: a test that reads its
expectation out of the thing it checks cannot convict a wave that updates both
or neither.

**(c) `test_a_correction_is_findable_from_the_claim` -- A CORRECTION NOBODY
COULD FIND FROM THE CLAIM.** Section 7 of this document says R2's headline
claim is false, which IS a correction, and it was written as prose. The guard
demanded the declared pair, and it is right to: **a corrector names what it
corrects; the corrected document cannot name its corrector**, so every reader
arriving at R2 would have met the false sentence and nothing else. There is now
a `CORRECTS:` marker here and a `CORRECTED BY:` back-pointer inside R2 itself.

**The pattern across all three: every red was a downstream consequence of a row
moving, and no red was a defect in the move.** That is what a census with
standing guards is supposed to feel like, and it is the argument for section 43
being wired to a test rather than left as a script.

---

## 6. WHAT THIS WAVE DID NOT RESOLVE, BY INSTRUCTION

**THE FILE-UPLOAD QUESTION IS UNTOUCHED AND STAYS OPEN.** `writes.UPLOAD_ACTIONS`
is EMPTY (n=0) while `UPLOAD_CONTROL_KIND` is `set_input_files` and
`readonly.SANCTIONED_MUTATIONS` holds one `set_input_files` call site. The ban
rests on *"the operator has never been asked about it"*
(`_audit/2026-09-20-the-sanctioned-seventh.md`). **No row in this wave was filed
as though that were settled**, and the rows it would touch (`P B2`, `P B3`,
`P B5`, `P G3`) are already EXCLUDED-RULED and were outside this scope anyway.

---

## 7. THREE PREMISES MEASURED STALE, OUTSIDE THIS WAVE'S SCOPE TO FIX

Found while cross-referencing addresses, verified through
`readonly.assert_read_url`, and **not acted on** -- every one of them concerns
READ rows or EXCLUDED-RULED rows this wave was not scoped to.

    ADMITTED  /mynetwork/invite-connect/connections/
    ADMITTED  /company/<slug>/
    ADMITTED  /school/<slug>/

**CORRECTS:** `_audit/_census/network.md` -- R2's headline claim that the ruling removes the connections list, measured false at HEAD through the shipped read gate; the back-pointer is written into R2 itself.

1. **R2's headline claim is false at HEAD.** R2 says *"This is the
   ruling that removes his connections list"*, and the connections address is
   now BOTH on `_ALLOWED_URL_PATTERNS` and in
   `_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS`, exempted for `/invite` and
   `/connect` by an anchored pattern. Somebody admitted it deliberately.
   **R2 produces 15 EXCLUDED-RULED rows, and rows `23`-`28` are the connections
   list.** Two of my in-scope rows (`N 169`, `N 187`) rest on the same premise
   and stay GAP; their state is unaffected because no tool reads that list
   either way, but their BLOCKER text is wrong.
2. **`N 47`'s blocker *"no `/company/` pattern"* is false** -- there is one.
   `/company/<slug>/people/` is still refused, so the row may still be correct;
   its stated reason is not.
3. **`network.md`'s surface table says `/school/<x>/` is ABSENT with *"zero
   grep hits for `/school/` in the package"*** -- there is a pattern.

**THE GENERAL DEFECT, which is worth more than the three instances: a blocker
cell that asserts what the boundary does NOT catch is a measurement with a
timestamp, and nothing in this census re-takes it.** Four such claims were found
false in the 101 rows alone. The repair is mechanical and is registered as
instrument 43.
