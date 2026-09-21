# THE WRITE CEILING: 157 WRITE-DIRECTION GAP ROWS, AND THE 152 THAT STAY

**Scope as briefed:** every `W`-direction `GAP` row in `_audit/_census/profile.md`,
`_audit/_census/network.md` and `_audit/_census/messaging-and-content.md`.
`_audit/_census/jobs.md` was **not touched and not read for adjudication** -- it has
no direction column at all, and `_audit/2026-09-21-the-jobs-direction.md` section 8
argues it should not grow one.

**CORRECTS:** `_audit/_census/messaging-and-content.md` -- five write rows re-filed GAP to EXCLUDED-RULED under the settings-family ruling, and the group-address clause on `C61` corrected as false at this tree.

**CORRECTS:** `_audit/_census/network.md` -- the same group-address clause on rows `63` and `163`, measured false; no state moved.

**HEADLINE: 5 of 157 moved. 152 stay GAP. And the brief's premise is refuted by
disk for 86 of them.**

The brief's model was that 157 write rows "simply never had anyone reach them".
Measured: **86 of the 157 were adjudicated one day ago**, row by row, by
`_audit/2026-09-20-the-write-partition.md`, which moved 14 and ruled that the rest
stay. The genuinely unadjudicated set was one slice -- `messaging-and-content.md`,
71 rows -- which that wave explicitly declared out of scope. **This wave is that
slice**, plus the reconciliation proving the other two are done.

---

## 1. THE COUNTS, RE-DERIVED WITH THE SHIPPED COUNTER

`./venv/Scripts/python.exe scripts/count_census_states.py`, run at this tree
before and after. **Not quoted from the brief**, which was measured before a
merge landed.

                            BEFORE      AFTER     delta
    GAP                        280        275        -5
    EXCLUDED-RULED             280        285        +5
    XR (jobs.md spelling)       23         23         0
    COVERED-PROVEN              52         52         0
    COVERED-UNFIRED             22         22         0
    COVERED-CANNOT-DELIVER      16         16         0
    MEASURED-ABSENT              7          7         0
    CP / CU (jobs.md)        20 / 4     20 / 4         0
    ------------------------------------------------------
    stated rows                704        704         0

**`stated rows` held at 704 through every edit**, which is the invariant the brief
set. It was checked after each batch, and **it caught a defect**: see section 6.1.

Per slice, and only one moved:

    jobs.md                    150 rows   GAP 56 -> 56    (NOT TOUCHED)
    profile.md                 203 rows   GAP 55 -> 55    (no edit)
    messaging-and-content.md   142 rows   GAP 82 -> 77    EXCLUDED-RULED 45 -> 50
    network.md                 209 rows   GAP 87 -> 87    (2 reason repairs, no state move)

### 1.1 THE DIRECTION SPLIT, AND TWO CORRECTIONS TO THE BRIEF'S OWN NUMBERS

Taken with `reader_closable_blockers.direction_of` -- the VALUE-based reader, imported,
because a positional one reads a Help Center reference as a direction and this corpus
has paid for that once.

    GAP 280, BEFORE          brief said        measured
      W                          157              157    agrees
      R                           65               65    agrees
      R+W                          1                2    BRIEF UNDERSTATED BY ONE
      unclassified                57               56    BRIEF OVERSTATED BY ONE

The two disagreements are one row: a row the brief counted as unclassified carries
both directions. The total is 280 either way and **no row in my set changed hands**,
so nothing downstream moves. Recorded because a number nobody re-derives becomes a
quotation.

`EXCLUDED-RULED` write rows, the precedent the brief pointed at: **213 before, 218
after**, plus 38 `R`, 3 `R+W`, 26 unclassified = 280. The 23 `XR` are all `jobs.md`,
which has no direction column, so they are direction-unknown by construction and the
brief's 303 is 280 + 23.

---

## 2. THE RECONCILIATION THAT DECIDED THE SHAPE OF THIS WAVE

`_audit/2026-09-20-the-write-partition.md` took 101 write-direction GAP rows across
`profile.md` and `network.md` -- 46 profile (45 `W` + 1 `R/W`) and 55 network -- moved
14, and left 87. Measured at this tree today:

    profile.md   W GAP now 37   =  45 - 8 moved     MATCHES
    network.md   W GAP now 49   =  55 - 6 moved     MATCHES
                                  --
    my profile + network W GAP   =  86  =  87 - 1   the R/W row, which is not in a W count

**The reconciliation is exact.** My 86 profile-and-network rows ARE that wave's 87
stayed rows, less the one `R/W` row that a `W` filter cannot see. So they are not
unreached; they are ruled, yesterday, with the argument written into each cell.

**I did not re-litigate them, and that is a decision, not an omission.** That wave's
own finding is the reason: *"73 of the 101 are capabilities nobody has ever weighed,
for which no passage in this repository says anything at all, and a wave that moved
them would have been inventing product decisions to improve a number."* Re-opening 86
rows on the same evidence one day later would be exactly that.

**What I did do to them:** two reason repairs in `network.md` that move no state
(section 5), and one flag (section 6.3).

---

## 3. THE CALIBRATION, AND THE BAR I APPLIED

I read the 213 already-excluded write rows first, as briefed. The accepted grounds,
in the corpus's own vocabulary:

1. **A forbidden-substring entry** on the capability's address, checked BEFORE the
   allowlist. `N 38`: *"A forbidden-substring entry is this census's own named bar
   for EXCLUDED-RULED."*
2. **A `writes.PERMANENTLY_FORBIDDEN` key naming the act** -- `delete_or_withdraw_anything`,
   `endorse_or_recommend`, `auto_accept_or_auto_reply`.
3. **An unsanctioned mutation class** -- `drag_to`, a press shape off
   `press.SANCTIONED_SHAPES`, a `press._COMPOSER_MARKERS` terminal refusal.
4. **Structural impossibility for a browser driver** -- mobile-app-only, microphone
   capture, live streaming.
5. **Propagation from a twin already ruled** under a named standing ruling
   (`network.md` R1-R11, the retirement rulings in `_audit/2026-09-05-decide-retire-rulings.md`).

**THE BOUNDARY MEASURED, NOT READ OFF PROSE.** Imported at this tree:

    writes.writes_enabled()            False
    writes.PERFORMABLE                 12 actions
    writes.PERMANENTLY_FORBIDDEN        9 keys
    readonly._FORBIDDEN_URL_SUBSTRINGS 33 entries
    server.READABLE_SETTINGS            1 key -- 'dark mode'

### 3.1 WHAT I REFUSED TO USE AS A GROUND, AND WHY IT MATTERS MOST

**`writes_enabled()` is False, and that closes nothing.** It is a global switch, not a
per-capability ruling, and the census proves it: `P N2` -- a dark-mode CHANGE -- is
`COVERED-PROVEN`, a write, with writes disabled. If the switch were the bar, the one
proven write row could not exist. Closing 157 rows on it would have been the
rubber-stamp the brief warned about, and it would have been circular.

The write-partition reached the same result from the other side and measured it:
**CLASS 2, "sanctioned but switched off", came out ZERO of 101.** Its sentence is the
one to keep: *"the write GAP is not the twelve waiting for a flag. It is the ROUTES
and VARIANTS the twelve do not address, and no amount of turning writes on would move
any of it."*

---

## 4. THE FIVE THAT MOVED -- ALL ONE RULING, APPLIED WHERE IT HAD NOT REACHED

| row | capability | ground |
|---|---|---|
| `M M35` | Choose Messaging inbox layout | settings-family ruling |
| `M M36` | Manage how new conversations open (conversation windows) | same |
| `M C73` | Allow or disallow your posts being embedded | same |
| `M C88` | Choose whether members can mention, tag or collaborate with you | same |
| `M C89` | Set the visibility of mentions and tags | same |

**THE RULING IS CITED, NOT INVENTED.** `_audit/2026-09-05-decide-retire-rulings.md`
section 3.10 re-filed five of this slice's settings rows and stated the scope itself:

> *"The settings-family ruling is capability-level, not path-level. It says a setting
> is admitted BY NAME or not at all. That excludes every page below the settings index
> whatever its URL spelling."*

> *"The ruling says 'a setting', not 'a profile setting', and these five are settings."*

**The profile slice applied it to 93 rows. This slice applied it to five.** 3.10's own
framing of that asymmetry is the whole argument: *"Same ruling, two slices, opposite
states"* -- and it called its own move a RE-FILE rather than a retirement, because
*"a re-file says the number was wrong, a retirement says somebody has now decided."*
These five are five more rows the enumeration did not reach. **No new decision is
claimed and none was made.**

### 4.1 THE BAR FOR "IS IT A SETTING", TAKEN FROM 3.10 RATHER THAN INVENTED

3.10 closed `M50` *Manage LinkedIn message nudges* and `M41` *Manage smart features in
Messaging* on cells reading only *"never named"* -- that is, on the **capability name
stating a persisted account preference**. I applied that same test and nothing wider.

**AND THE CENSUS ALREADY ENCODES THE BOUNDARY OF IT, WHICH IS WHY THE BAR DOES NOT
DRIFT.** The per-item controls in these same tables SAY SO IN THEIR NAMES:

    MOVED (account-level preference)     NOT MOVED (per-item control, says so)
      M35  Choose Messaging inbox layout    C23  Turn off or limit comments ON YOUR POST
      M36  Manage how new conversations..   C90  Verified comments filter ON YOUR POST
      C73  Allow or disallow your posts..   C78  Set the visibility of your articles
      C88  Choose whether members can..
      C89  Set the visibility of mentions..

`C78` is the closest call and it stayed: *"your articles"* reads per-item, and its
nearest neighbour in kind, `C2` (*Choose the post's audience*), is GAP with a LIVE
measurement plan against it. Closing `C78` would have pre-empted that.

`M35` is the other call worth stating: the in-surface control is a **different row** --
`M33`, the filter pill, read-direction, `COVERED-UNFIRED` -- so the census itself
already separates the persisted choice from the control that applies it.

**Each moved row carries `REOPENER, NAMED: the operator admitting this setting BY
NAME`** -- the mechanism by which dark mode became the one writable setting.
`scripts/check_contingent_writeoffs_carry_a_reopener.py` PASSES after the move.

---

## 5. THE 152 THAT STAY, AND WHY

    STAYED GAP                                                    152
      profile.md   37   adjudicated 2026-09-20, not re-litigated
      network.md   49   adjudicated 2026-09-20, not re-litigated
      messaging    66   adjudicated HERE

Of the messaging 66, measured by phrase over the cells:

    CARRY A DATED PRIOR ADJUDICATION that already chose GAP      23
    NO SUCH MARKER -- nobody has weighed them                    43

**23 of 71 messaging write rows had already been examined and deliberately left GAP**,
most of them on 2026-09-19 and 2026-09-20. The largest single group is the ten rows
`_audit/2026-09-20-the-decides.md` section 1.5 ruled on in terms: *"Its 15 rows stay
`GAP`, correctly"* -- `M14`, `M15`, `M18`, `C3`, `C4`, `C5`, `C6`, `C7`, `C27`, `C45`.
**A standing ruling that a row stays GAP outranks a brief that expects it to move.**

### 5.1 TWO REASON REPAIRS IN `network.md`, NO STATE MOVED

Rows touched in `network.md`, by id, for the lead's merge: **`N 63` and `N 163`.**
Both keep `GAP`. The matching messaging row `M C61` was repaired identically, and
`M C63` inherits it by its `same` backreference.

All four asserted: *"this needs `/groups/<id>/` or `/groups/discover/`, and both are
NAMED REFUSALS in `readonly.py`'s own comment (`:540-549`), not merely undeclared."*

**Measured 2026-09-21 through the shipped gate: both are ALLOWED.**

    /groups/discover/   matches ^https://www\.linkedin\.com/groups/discover/?$
    /groups/<id>/       matches ^https://www\.linkedin\.com/groups/[0-9]{1,20}/?$
    NEGATIVE CONTROL: /groups/<id>/members/ still REFUSED   (gate discriminates)

Two allowlist patterns were added **2026-09-19 on the team lead's ruling**, and the
comment those cells cite was REWRITTEN by that admission -- so the citation now points
at the passage that GRANTS the addresses it is quoted as refusing.

**The rows do not move, and the correction pushes them TOWARDS GAP rather than out of
it:** the address third of the price is paid, so the capability is more reachable, not
less. What remains is stated verbatim in that same comment and no boundary change buys
it: *"NO WRITE IS BOUGHT BY THIS. Joining, leaving, posting and inviting all need their
own url, their own sanction and their own ruling."* Still DECIDE, not MEASURE.

---

## 6. WHAT CONTRADICTS THE BRIEF, AND WHAT THE INSTRUMENTS CAUGHT

### 6.1 THE INVARIANT CAUGHT A REAL DEFECT IN MY OWN EDIT

After the first batch the counter read `GAP 276 / EXCLUDED-RULED 284` -- **four moved,
not five**. `C88`'s edit had appended to its REASON cell and never touched its STATE
cell, and the appended text argued the exclusion convincingly enough to read as done.
`stated rows` stayed 704 throughout, so only the per-state arithmetic exposed it.
**A reason cell that argues for a state the row does not carry is invisible to
everything except the count.**

### 6.2 THE CENSUS HOLDS TWO INCOMPATIBLE PRACTICES ABOUT THE FORBIDDEN LIST

`_audit/2026-09-20-the-write-partition.md` section 4.1 found this and called for a
ruling. **I hit it from the opposite side and it is worse than one wave's problem.**

* `N 38`, and 15 rows filed under R2: *"A forbidden-substring entry is this census's
  own named bar for EXCLUDED-RULED."*
* `_audit/2026-09-05-decide-retire-rulings.md` **section 2, titled "THE BOUNDARY IS NOT
  A REASON"**: *"Everything a general mechanism merely happens to block is a GAP with a
  NAMED BLOCKER -- recorded so nobody reads GAP as cheap, but not laundered into a
  decision."*

Those cannot both be applied. **Neither of my two grounds needs the question settled** --
3.10 is explicitly capability-level, and the group repair moves no state -- so this wave
takes no position either. **RULING NEEDED, and it is now requested twice.** It decides
every future boundary-blocked row on all three slices. `M C79` (*Follow or unfollow
member articles*) is the row in my set that turns on it.

### 6.3 AN `EXCLUDED-RULED` ROW WHOSE REASON IS GAP'S OWN DEFINITION

`M C42` -- *Address a specific post by identifier* -- is `EXCLUDED-RULED`, and its
entire reason is *"no tool in this server returns one."* **That is a statement that
nothing builds it, which is GAP's definition wearing an exclusion's state.** It is the
same miscategorisation the write-partition flagged on `P I12` and for the same reason
declined to propagate from.

This matters beyond the one row: `M C26` (*Reply to a comment*) records *"no comment
identifier is read anywhere"* and would close by propagation from `C42`. **I did not
close it, and I did not touch `C42`.** Propagating from a miscategorisation compounds
it. Flagged for the lead, exactly as `P I12` was.

---

## 7. SECTION THE BRIEF ASKED FOR MOST -- ROWS A NAIVE PASS WOULD HAVE CLOSED

Each of these has a visible, plausible ground that does not survive reading.

**1. `M C36` / `M C37` -- saved posts. The cell says the address "refuses".**
It does -- **by ALLOWLIST SILENCE, not by a forbidden substring.** Measured:
`/my-items/saved-posts/` trips no entry on `_FORBIDDEN_URL_SUBSTRINGS`. `network.md`
section 2 and the `N 38` cell both say allowlist silence is **not a reason**. Closing on
"is_read_url returned False" would have laundered an unbuilt address into a decision.

**2. `M C76` -- collaborative articles. Same trap, same measurement.**
`/collaborative-articles/` and `/pulse/collaborative-articles/` both refuse, both by
silence alone. The cell prices it at `allowlist +1`, which is a COST, and a cost is not
a ceiling.

**3. `M C61` / `M C63` -- join and leave a group. The cell says the addresses are
"NAMED REFUSALS".** The strongest-looking ground in the whole set, and it is **false at
this tree** -- both addresses are now allowed (section 5.1). A naive pass closes on the
stale sentence; the measurement reverses its direction entirely.

**4. `M M11` -- edit a sent message. `/edit/` is a forbidden substring.**
The cell already refused this ground and was right: *"`/edit/` is a forbidden substring
but it is a url guard and this control is in-thread."* **A URL gate does not reach a
control that is not addressed by URL.**

**5. `M M25` -- leave a conversation; `M C63` -- leave a group.**
`delete_or_withdraw_anything` looks adjacent. The cell had already ruled: *"adjacent to
but not covered by"*. Leaving is not destroying. `M C62` (*withdraw* a membership
request) IS closed under that key, and the contrast is the point -- the key names
withdrawal, and the census applied it where it lands.

**6. `M M13` -- forward a message.** `repost_or_share` looks like it reaches
republishing somebody else's words. Read in full, it does not: it was **NARROWED** in
2026-08-30 and what survives is bound to BROADCAST -- *"republishes SOMEBODY ELSE'S item
to his network under his name ... the thing broadcast is not his and the audience is."*
A forward is point-to-point. The entry closes with *"it is not quietly added here"*,
which reads as an instruction to later waves.

**7. `M M47` -- respond to a Recruiter InMail.** R9 covers InMail. Read in full, R9 is
about **spending**: *"He has 5 InMail credits a month ... Automating five actions a
month is not engineering, it is ceremony."* Responding to a received InMail spends
nothing. **It stays GAP, and it is the single most job-hunt-relevant row in the
slice** -- the cell says so and I agree.

**8. `M M31` -- mark a conversation read or unread.** `mark_notifications_read` is a
`PERMANENTLY_FORBIDDEN` key whose ground -- destroying unseen signal -- transfers
cleanly. But the key names NOTIFICATIONS, and the cell says so: *"a different surface,
though its reasoning transfers."* Extending a prohibition to a surface it does not name
is a new ruling. **Escalated, not taken.**

**9. `M C9`, `M C2`, `M C12`, `M M30`, `M C54`, `M C56`, `M C87`, and the ten under
`the-decides` 1.5.** Each carries a dated wave's explicit verdict that it stays GAP.
**These are the rows the brief's premise most clearly misdescribes:** they were reached,
weighed, and left, with the argument in the cell.

**10. `M C67` -- edit or delete a group post or comment.** The delete half meets
`delete_or_withdraw_anything`; the edit half meets nothing. Closing the row closes a
verb nobody ruled. This is the write-partition's pattern 2 exactly (`P D27`, `P L3`), and
it needs a SPLIT, which changes the denominator. **Escalated with them.**

---

## 8. A READ CAPABILITY HIDING INSIDE A WRITE ROW

**`M C85` -- "Vote in a poll / view poll results".** One row, two capabilities, one
direction cell reading `W`. *Vote* is an irreversible write. **"View poll results" is a
READ**, and because the row is filed `W` the read half is invisible to every
direction-based sweep this census runs -- including the one that produced the backlog
this wave was pointed at.

It is not merely a read, it is **the kind this repository has already ruled
admissible**: poll results are COUNTS, and the feed-content ruling that `C43` and `C74`
rest on is *"counts and relations only, never text or names."*

**I named it in the cell and left the row GAP.** A split changes the denominator; the
precedent exists (`P L2` -> `L2` + `L2b`) and so does a queue -- the write-partition has
two rows waiting on the identical question. It belongs with them, not decided alone.

**Two more, already named by their own cells and confirmed here:** `N 169` and `N 187`
-- *filter the connections you invite* / *filter your invitee list* -- whose cells read
*"A filtered read over his own connections"*. The connections list is on the allowlist,
so the read half sits on an **admitted** surface. Left GAP, unchanged.

**The generator that found these produced two false positives**, which is why the
adjudication is by hand: `M M31` (*mark a conversation read*) and `P G2` (*Activity
section default view*) match on `read` and `view` as NOUNS.

---

## 9. FOR THE OPERATOR -- FIVE THINGS I DID NOT DECIDE

1. **Is a forbidden-substring entry alone a ruling?** Section 6.2. The census holds two
   incompatible practices; the write-partition asked first and nobody has answered.
   Decides every future boundary-blocked row. Reaches `M C79` here.
2. **Groups: join, leave, post, comment.** `M C61`, `M C63`, `M C64`, `M C65`,
   `N 63`, `N 163`. The address is now BOUGHT (section 5.1); what remains is a write
   sanction and a ruling, which `readonly.py` states verbatim is not bought by any
   boundary change. **DECIDE, not MEASURE.**
3. **Does `mark_notifications_read` extend to messaging read-state?** `M M31`. One word.
4. **Split or leave whole:** `M C67` (edit / delete a group post), joining `P D27` and
   `P L3` on the write-partition's identical queue. A split changes the denominator.
5. **`M C42`** is `EXCLUDED-RULED` on a reason that is GAP's own definition (section
   6.3). Not touched, not propagated from. Same class as `P I12`.

**One observation, offered and NOT acted on:** `P G2` *Activity section default view*
is a persisted preference, which is what 3.10 calls a setting -- yet it sits in
`profile.md` as GAP class 3. Profile's write rows were adjudicated yesterday and
re-opening one of them on my reading is not my call. **Flagged only.**

---

## 10. GATES

`scripts/count_census_states.py` -- run after every batch. `stated rows` 704 throughout.

`scripts/check_contingent_writeoffs_carry_a_reopener.py` -- **PASS**. All 59 contingent
write-offs in scope carry a reopener; per-slice liveness ok on all four.

`scripts/impact_gate.py` -- **REFUSED on first run with 4 reds, all caused by this
change**, which is the gate working:

* `test_the_audit_index_is_derived` -- this document was not yet written.
* `test_every_marker_names_one_document_and_carries_a_reason` -- my `CORRECTED BY:`
  marker named FOUR documents on one line; a marker must name exactly one.
* `test_every_candidate_pair_is_declared_or_triaged` -- two pairs, both mine, one
  purely by **adjacency**: a markdown table has no blank lines, so my `N 163` prose
  landed inside `N 162`'s two-line citation window. Both triaged onto
  `NOT_A_CORRECTION` with reasons.
* `test_the_headline_split_is_the_one_the_report_quotes` -- the messaging triage
  constant is pinned to the split a report quotes; moving 5 rows moved it.
  `EXPECTED_NOW` updated to `(77, {"R": 10, "W": 66, "R+W": 1})`, with the arithmetic
  written beside it and the prior value KEPT under its own name rather than
  overwritten. **The `R` and `R+W` counts are unchanged, which is the check that this
  write-direction wave stayed inside its scope.**

After the four fixes the gate PASSES: `PASS over the 43 file(s) above (1954 tests)
-- AND OVER NOTHING ELSE.`

**The gate's own NOT CHECKED line, verbatim, from the FINAL (green) run:**

    NOT CHECKED: 161 of 204 test files (78.9% of the suite by file).
    The corpus-wide guards DID run, so the identity, credential and page-text
    sweeps cover the whole tree. Everything else above is unexamined.
    That is roughly 4140 of 6094 tests unrun (67.9%), against a suite count taken 2026-09-20 at 970a276.
    Wall clock: 180.3s.
    THIS IS A LOCAL, WINDOWS-ONLY SIGNAL. CI runs three platforms and is the
    certifier; a green gate here is not a reason to shrink that matrix.

And from the FIRST (red) run, kept because the scope differed and a reader
comparing the two should not have to guess why: `NOT CHECKED: 174 of 204 test
files (85.3% of the suite by file)`, `roughly 4630 of 6094 tests unrun (76.0%)`,
wall clock 88.6s. **The green run checks MORE**, because staging the new document
and the two test files pulled 13 more files into the impact set.

**A NOTE ON THE GATE'S OWN SHAPE, since it bit me:** `scripts/impact_gate.py`'s
subject is the git INDEX. Run with nothing staged it prints `impact-gate: nothing
staged; nothing to check.` and exits 0 -- a clean-looking pass over zero files. It
must be run AFTER `git add` and BEFORE the commit.

---

## 11. FOR THE MERGE

Files touched, and every census row by id:

| file | rows touched | state moved? |
|---|---|---|
| `_audit/_census/messaging-and-content.md` | `M35` `M36` `C73` `C88` `C89` | **YES**, GAP -> EXCLUDED-RULED |
| `_audit/_census/messaging-and-content.md` | `C61`, `C85` | no -- reason only |
| `_audit/_census/network.md` | `63`, `163` | no -- reason only |
| `tests/test_triage_instrument.py` | -- | `EXPECTED_NOW` re-pinned |
| `tests/test_a_correction_is_findable_from_the_claim.py` | -- | 2 `NOT_A_CORRECTION` entries |
| the derived audit index | -- | regenerated, `scripts/build_audit_index.py --write` |

**MASTER MOVED WHILE THIS WAVE RAN -- MEASURED, NOT ASSUMED.** Four commits landed
(`9093637`, `b42a52c`, `eef1a15`, `73cd137`). Diffed against this tree:

* `messaging-and-content.md` -- **master did not touch it.** All five state moves
  and both reason repairs merge clean.
* `network.md` -- master moved rows `33`, `54` and `175` from COVERED-UNFIRED to
  COVERED-CANNOT-DELIVER and added one `CORRECTED BY:` line near the top.
  **All three are READ rows and none is mine.** Per the lead's standing note they
  are left exactly as this base has them; master is right about them.
  **The expected conflict is the `CORRECTED BY:` marker block near line 40**, where
  master inserted one and so did this wave. Both are additive and both should
  survive; my rows `63` and `163` are at lines 404 and 602 and are untouched by
  master.

**Counts in this document are taken at THIS tree**, which is `master` as of the fork
plus this wave. After the merge they must be re-derived; `scripts/count_census_states.py
--expect J=56,P=55,M=77,N=87` is the control this wave leaves armed, and the `N=87`
term is the one master's three read-row moves do NOT change.
