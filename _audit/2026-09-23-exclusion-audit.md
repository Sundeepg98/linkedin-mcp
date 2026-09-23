claude-opus-5-5[1m]

# Who ruled each exclusion -- the 315 rows outside the denominator, traced

**Lane X, 2026-09-23, worktree off `master` at `b0d3ab8`. REPORT ONLY: no census
cell was edited and no row changed state.** Whether any row below returns to GAP
is the operator's decision; this document is the evidence for it.

**STATUS: IN PROGRESS -- written as the wave runs.** Sections marked PENDING are
not yet measured and carry no figures.

---

## 0. THE QUESTION, AND WHY IT WAS PARSED RATHER THAN GREPPED

The operator asked whether the census's pending count is exact, or whether more
work is hidden. `scripts/census_completion.py` removes two states from the
achievable surface -- EXCLUDED-RULED and MEASURED-ABSENT -- and nobody had
checked who ruled each exclusion. A grep had found 345 lines against 308 rows and
only 5 cells naming the operator in their first 90 characters.

### 0.1 The denominator, derived -- 315, as briefed

Taken with the shipped parse (`count_census_states.cells/ROW/HEADERS/state_of`),
the admin-row rule from `enumerate_gap_rows`, and the fold table from
`census_completion.FOLD`, then cross-checked against `census_completion.walk()`:
the two populations are EQUAL, and no (slice, row) key occurs twice.

    slice  EXCLUDED-RULED  (of which XR)  MEASURED-ABSENT  total
    J              48            23              1           49
    P             113             -              2          115
    M              50             -              1           51
    N              97             -              3          100
    all           308            23              7          315

`XR` is `jobs.md`'s own spelling of EXCLUDED-RULED; the counter reports it under
its own key and the completion instrument folds it. Folded, the 308 matches the
brief and the pinned `out_of_scope` 315.

### 0.2 Why the grep said 345, measured

A line containing the word is not a row in the state. Over the four slices the
word occurs on **345** lines: **285** EXCLUDED-RULED row lines, **18** other
table lines (GAP rows citing an excluded twin, the prior text a MEASURED-ABSENT
cell keeps, roll-up tables) and **42** prose lines. The **23** `XR` rows never
contain the word at all. 345 - 18 - 42 = 285 = 308 - 23. So the grep
over-counted by 60 and under-counted by 23 at once, and its net error of 37
looked like one number.

---

## 1. METHOD

**Each row was traced, not grepped.** The population and every row's text come
from the shipped parse: `census_completion.walk()` for the population, and
`classify_writeoff_reasons.build()` for each row's RESOLVED text -- its own
reason cell, the donor a positional `same` resolves to, the body of any network
`R<n>` it cites (including the four-column tables whose only citation sits in
the state cell), and its section heading. The two walks are cross-checked on
every run of the checker.

**Who made each ruling was traced to the tree, not to the census's word for
it.** Two closed-form slices were delegated and reviewed before use:

* **Git archaeology** of every code refusal the rows cite -- 65 literals in
  `writes.py`, `readonly.py`, `server.py` and two tests: the commit that
  introduced each and any attribution in its message, its comment or its
  wave's document. OPERATOR 9, SELF 24, NONE 32. Three of its SHAs were
  re-checked here and hold (`1a94cf9`, `817f1d5`, `615a5c4`); its report of a
  Git-Bash path-conversion trap that silently empties `git log -S'/invite'`
  was confirmed on the first re-check, which returned nothing until the
  pre-rename path was used. Evidence file, gitignored:
  `_audit/_scratch/exclusion-audit/code-provenance.tsv`.
* **An attribution register** -- every passage in the corpus attributing a
  decision to the operator, a lead, or the writing wave itself. PENDING at
  the time this line was written; section 4 is reconciled against it.

**The classes.** Stated once in `scripts/check_exclusion_basis.py` and repeated
here so the counts can be read:

| class | meaning |
|---|---|
| **A** | the operator's own ruling reaches THIS row -- names the capability, act or address -- with no agent step between |
| **B** | an agent placed the row under a family or area ruling; carries `op=` (did the operator make that family ruling: YES / NO / CONTRARY) and `scope=` (does the family's own wording reach the row: YES / EXTENDED / NO) |
| **C** | no traceable basis: NONE cited, only SILENCE (allowlist silence, an unmeasured state), the only ground REFUTED at HEAD, a registered ruling that names the row OVERRULED it, or the citation is DANGLING from a clone |
| **M+ / M-** | MEASURED-ABSENT, the measurement recorded in a tracked document, or not |

**CONTRARY is not a synonym for NO.** It means an operator ruling or
instruction on record -- or the document recording it -- classes the capability
or its family as something to BUILD or MEASURE. It is used for four families
and every use quotes the passage.

**The C line was drawn to be checkable, and it is narrower than it could have
been.** A row is C only when the fact that sinks its basis is objective: a
measurement at HEAD, a registered ruling that names the row or its exact
address, a cited list that demonstrably refuses nothing, a citation that does
not resolve. Rows where the sinking fact is a JUDGEMENT -- a class filter that
catches an address "incidentally" under the registered general form of
`INCIDENTAL-CAPTURE-IS-NOT-A-RULING` -- are B with `scope=NO` instead, so the
checker's hard failure never rests on this wave's reading.

## 2. COUNTS PER CLASS

Reconciled against the attribution register (189 passages: OPERATOR 88, LEAD
72, SELF 28, UNCLEAR 1; evidence file
`_audit/_scratch/exclusion-audit/attribution-register.tsv`, gitignored). The
register moved ONE family's `op=`: R9 rests at the root on the operator's own
2026-08-23 cut, not on the agent research report the census quotes, so it is
`op=YES` -- and lifted (section 2a).

    EXCLUDED-RULED   308    A 0   A-lifted 0   B 255   B-lifted 27   C 26
    MEASURED-ABSENT    7    M+ 6   M- 1

    per slice          J     P     M     N
      B               40    93    41    81
      B-lifted         2     7     3    15
      C                6    13     6     1
      M+ / M-        1/0   2/0   1/0   2/1

**A IS ZERO.** No out-of-scope row rests on an operator ruling that names it.
Every mention of the operator in these cells is either a REOPENER naming him as
the one who could reopen the row -- **30 cells name him in their own REOPENER
clause**, while none names a ruling of his that closed it -- or a family ruling
an agent applied. That is the direct answer to "who ruled each
exclusion": **agents ruled every one, and in 106 cases they were applying a
family ruling he made.**

**THE 282 B ROWS, lifted included, by who made the family and whether its
wording reaches the row:**

                         scope=YES  EXTENDED   NO   total
    op=YES                   78        27       1    106
    op=NO                    75        13      27    115
    op=CONTRARY              45         0      16     61

**Only 78 rows -- 25% of the 308 -- rest on a family ruling the operator made
AND plainly reach the row, and 73 of those 78 are one family, the settings
ruling, whose words ADMIT settings one at a time rather than rule any out**
(section 4). The other five are third-party profile reads his 2026-09-04
narrowing plainly covers.

### 2.1 IS THE PENDING COUNT EXACT? NO -- AND HERE IS THE DECOMPOSITION

Every figure is a row count off `_audit/_census/exclusion-basis.tsv`, and the
tiers do not overlap. Each is a statement about the BASIS, not a prediction of
what the operator will decide.

| tier | rows | what holds the row today |
|---|---:|---|
| no traceable basis (C) | 26 | nothing written that decides against it |
| basis withdrawn today, nothing else holds it (B-lifted) | 21 | nothing, since ruling (b) |
| basis withdrawn today, one other basis remains (B-lifted) | 6 | R1, the 2026-09-04 profile ruling, or `/edit/` |
| his recorded words point the other way (B, `op=CONTRARY`) | 61 | an agent's reading he has contradicted |
| an agent's family, its wording does not reach the row (B, `op=NO`, `scope=NO`) | 13 | an agent's ruling, stretched |
| an agent's family, reached only by widening (B, `op=NO`, `scope=EXTENDED`) | 12 | an agent's ruling, widened |
| an agent's family, plainly in scope (B, `op=NO`, `scope=YES`) | 66 | an agent's ruling he never made |
| his family, reached only by widening or not at all (B, `op=YES`, `scope` EXTENDED or NO) | 25 | his ruling, stretched by an agent |
| his family, plainly in scope (B, `op=YES`, `scope=YES`) | 78 | his own ruling |
| | **308** | |

**Read it from the top.** The first two tiers -- **47 rows** -- are held by
nothing at all today. The next two add **67** where the only thing holding the
row is a basis he has withdrawn in part or contradicted. That is **114 rows,
37% of the exclusions**, that the pending count leaves out and the corpus gives
no current ground to leave out. The census's achievable surface of 389 is an
UNDERCOUNT by up to that much; how much of it is real work is his to rule, and
section 4 gives one line per family to rule on.

## 2a. THE OPERATOR'S RULING (b), 2026-09-23 18:15, AND THE ROWS IT LIFTS

**The ruling as it reached this wave.** A disk note from the orchestrator,
written about 18:20 IST on 2026-09-23 and deleted by this wave after acting on
it, as instructed. Its words, verbatim:

> At 18:15 the OPERATOR ruled "(b)": the linkedin MCP may connect, message,
> apply, post and open messaging on his account. That LIFTS three bases that
> exclusions may cite: the read-only / no-writes rule; the apply / connect /
> InMail cut; DO-NOT-OPEN-MESSAGING.

**Evidence class: RELAYED.** The operator's own words are not in the tracked
corpus; this section is the first tracked record of the relay. Nothing on disk
contradicts it. Three facts on disk bear on it and are stated so it is not read
wider than it is:

* **The apply / connect / InMail cut WAS the operator's.**
  `_audit/2026-08-23-build-linkedin.md`: *"The operator **cut apply, connect
  and InMail** and approved **save/unsave, follow, Open To Work** behind an
  off-by-default flag."* So the rows it lifts rested, at the root, on a
  ruling he made and has now withdrawn.
* **No out-of-scope row cites DO-NOT-OPEN-MESSAGING.** Measured over every
  row's resolved text: zero. Lifting it moves nothing in this table.
* **Only nine rows cite the no-writes rule in words** (`writes_enabled()` is
  False): `P B2`, `P B3` and `P M1`-`M7`. The rest of the lifted set rests on
  code refusals whose RECORDED PURPOSE is one of the three -- the `/invite` and
  `/connect` entries exist, in `readonly.py`'s own words, "to stop this server
  SENDING invitations"; `/jobs/application`, `/post/` and `/follow` entered in
  the read-only server's first commit, `1a94cf9`.

**THE LIFTED ROWS: 27, all B -- `B-lifted` in the table.** None is A-lifted,
because no out-of-scope row rested on an operator ruling that named it.

| family | rows | lifted basis | another basis remains? |
|---|---|---|---|
| R2 invitation substrings | `N 9 11 24 25 26 27 28 168`, `M C69` | the connect cut; the read-only rule | no |
| R2 invitation substrings | `N 13 14 16 19` | the connect cut; the read-only rule | YES -- R1, the `/mynetwork/` badge ruling |
| `/jobs/application` substring | `P M1`-`M7`, `J 71 73` | the apply cut; the read-only rule (`M1`-`M7` also cite writes disabled) | no |
| R9 InMail and outreach | `N 156 158` | the InMail cut | no |
| R9 InMail and outreach | `M M5` | the InMail cut | YES -- the operator's 2026-09-04 no-third-party-profile ruling |
| `/post/` and `/edit/` | `M C18` | the read-only rule (`/post/`) | YES -- `/edit/`, kept by the implementing wave on 2026-08-31 |
| `/follow` substring | `N A2` | the read-only rule | no |

**21 rows are fully lifted -- nothing else on record holds them -- and 6 keep
one other basis.** A row is tagged only when the basis it is PRIMARILY filed
under is withdrawn. Eight more rows cite R2 as a SECOND basis while their first
still stands, and they stay `B`: `N 10 12 29 A15` (the delete key), `N 30` (the
operator's 2026-09-04 profile ruling) and `N 72 73 75` (the settings ruling). Two C rows are touched as well: `P B2` and `P B3` had
already lost their upload-ban ground, and the one clause left standing in
their cells, writes disabled, is the no-writes rule (b) withdraws.

**ADJACENT, NOT TAGGED.** (b) plausibly reaches these, but none rests on one of
the three named bases, so none is tagged. Each is his to rule or the
orchestrator's to route: the multi-step apply rows `J 60`-`65` (the no-guessed-
steps rule); the off-site apply rows `J 66 67` (the off-domain rule, which
2026-08-25 records was never put to him); the connect acts filed under R1,
`N 3 15 17 18 21 22`; `N 2` (connect via a member's profile, held by his own
2026-09-04 ruling); the repost rows `M C20 C21`; and `M M3`, the dispatch-mode
row, already C.

## 3. THE 26 C ROWS -- NO TRACEABLE BASIS

**Recommendation for all 26: return to GAP with the blocker named**, the
remedy `INCIDENTAL-CAPTURE-IS-NOT-A-RULING` prescribes. None of them is an
argument that the capability is wanted; each is an exclusion nothing written
supports. `scripts/check_exclusion_basis.py` names every one and stays red
until each is decided.

| why | row | what it cites | why that is no basis |
|---|---|---|---|
| NONE | `J 115` | `server.py` job_detail docstring | says the tool does not read the hiring team: not a refusal, key, spec or measurement |
| NONE | `P D26` | `my_profile` docstring | says the tool does not report the strength meter: not a refusal, key, spec or measurement |
| SILENCE | `J 50 51 52` | the jobs-tracker stage allowlist | the allowlist names three stages; the rest are "absent -- nothing builds them" |
| SILENCE | `M C33` | `server.py` reaction passage | says nobody measured which reaction the toggle applies; the same passage records the operator ruled react ships with the default (`writes.py`, 2026-09-01). It refuses nothing |
| SILENCE | `M C35` | `delete_or_withdraw_anything` text | the cited text says react_to_item does NOT lean on the key; the ground is an ON label never observed |
| SILENCE | `M C42` | `finish.md` permalink passage | no tool returns a urn -- a missing tool; the register itself notes the permalink ruling does not reach it |
| SILENCE | `M C47` | `lift.md`, not on the allowlist | allowlist silence, which `BOUNDARY-IS-NOT-A-REASON` rules out as a reason |
| REFUTED | `J 53`, `J 84` | "the mutation-verb denylist" | the list is `readonly.WRITE_VERBS`, a check on tool NAMES -- it also lists apply, save and follow, whose writes ship |
| REFUTED | `P B2`, `P B3` | the upload ban | the operator was asked 2026-09-04 and "opened it FULLY: profile photo, post media and message attachments" (`readonly.py`, commit `615a5c4`). B2's own cell says no operator answer is recorded anywhere; it is recorded in code |
| REFUTED | `P B5`, `P G3` | `same ruling` | each resolves by POSITION to a different row (`B4`, a different address; `G1`, a COVERED row with no ruling); the section-6 roll-up files them under the upload ban, which the operator lifted |
| REFUTED | `M C13` | the scheduled-posts measurement | the cited passage records `Schedule post` as a BUTTON opening a modal: the control is drawn |
| REFUTED | `N 23` | R2 | the connections list is ADMITTED at HEAD (`is_read_url` True, measured offline this wave); `readonly.py` says the substrings "were hitting the wrong url" |
| OVERRULED | `P B4`, `P C2`-`C6`, `P N12`, `P O5` | the `settings`, `/uas/`, `/create` substrings | `INCIDENTAL-CAPTURE-IS-NOT-A-RULING` (2026-09-19) names exactly these eight addresses and rules "they stay GAP"; a second wave the same day (`2026-09-19-unfired-but-built.md` s6) read the operator's settings ruling over `B4`/`C2`-`C6` and also concluded "They stay GAP". All eight moved to EXCLUDED-RULED on 2026-09-20 citing neither |
| DANGLING | `M M3` | `_TEAM_LEAD_SUCCESSOR_BRIEF.md:63-80` | an untracked file that marks itself "SUPERSEDED ... DO NOT ACT ON THIS FILE"; its line is a lead's build instruction for `send_message` ("use the checked default"), not an exclusion. A 2026-09-20 table (`the-live-capture.md` 13.2) labels it an operator ruling and cites nothing |

**Two locators were found rotted while tracing, and neither row is C for it.**
`M M26` and `M C31` cite `writes.py:1801-1814`, a LINE RANGE that at HEAD lands
inside `send_message`'s spec. `M26` reaches the key through `M12`, which it
names; `C31` only through the key's own content ("the five specs that lean on
the entry"). The checker links both by content and says why in the registry --
the `CANONICAL-RULING-ID` failure, found by the instrument rather than by a
reader.

## 4. THE B ROWS, BY FAMILY -- WHO MADE IT, AND ONE RECOMMENDATION EACH

"Made by" is from the archaeology and the register: OPERATOR (his recorded
ruling), LEAD, WAVE (a wave's own ruling), CODE (a code entry an agent wrote,
with no attribution in its commit, comment or wave document). `op` and `scope`
are the table's flags; section 1 defines them. The two families that carry
most of the weight get a paragraph after the table.

| family | rows | made by | op | scope | recommendation |
|---|---:|---|---|---|---|
| `SETTINGS-BY-NAME` | 82 | OPERATOR, 2026-08-31 | YES | 73 YES, 9 EXT | Ask him the one question his words leave open (below). Re-file the 9 EXTENDED -- `P K1`-`K6` verification flows, `P N25` a nav path, `N A7 A8` Page-admin settings -- on their own grounds; his words do not reach them |
| `EDIT-FAMILY` | 22 | CODE, `/edit/` from `1a94cf9`; narrowing refused by the 2026-08-31 wave | CONTRARY | 22 YES | Return to GAP, blocker "`/edit/` kept refusing by the implementing wave". He allowed the profile editors 2026-08-31 and dissolved the profile-edit prohibition 2026-08-30; one passage of the 2026-08-31 perform record calls a WRITE admission for `/in/<member>/edit/` still owed, since met for the intro editor |
| `OTW-SPEC-NEVER-LOADED` | 20 | CODE, 2026-08-23 | CONTRARY | 20 YES | Return to GAP, blocked on capturing the modal. He approved Open To Work 2026-08-23; 2026-08-25 files it UNMEASURED; `2026-09-05-profile-modals.md` records the capture awaits one operator ruling "not yet taken" |
| `PF-DELETE-OR-WITHDRAW` | 20 | CODE, 2026-08-23 | NO | 20 YES | Put to him once. It meets neither survival bar the `writes.py` header attributes to him -- impossible with a measurement, or unattended -- and five `reversible_by` claims rest on it |
| `PF-ENDORSE-OR-RECOMMEND` | 19 | CODE, 2026-08-23; policy ground dissolved by him | CONTRARY | 3 YES, 16 NO | Return the 16 RECOMMENDATION rows to GAP -- the surviving measurement counted endorse controls, a different object. Keep the 3 endorse rows only while the zero-control reading stands; he ruled 2026-08-25 that endorsing gets built |
| `NO-THIRD-PARTY-PROFILE-LOAD` | 14 | OPERATOR, 2026-09-04 | YES | 5 YES, 9 EXT | Keep the 5 reads of a member's profile content. Re-examine the 9 acts: the census routes them through the member's profile, and network.md s6 R4 says the key's text does not cover acting |
| `R2-INVITATION-SUBSTRINGS` | 13 | CODE, `1a94cf9` (read-only first commit) | NO | 8 YES, 5 NO | Lifted by (b) -- move at merge. `N 13 14 16 19` stay held by R1 |
| `RETIRE-AI-INTERVIEW-PRODUCT` | 11 | WAVE, 2026-09-05 | NO | 11 YES | Put to him with the other eleven retirements as ONE ruling: the queue was defined as "needs his answer", and a wave answered it. The grounds -- a live spoken session, a hirer's screening -- are strong |
| `R1-MYNETWORK-BADGE` | 10 | WAVE, 2026-08-30 | NO | 10 EXT | Return to GAP with the badge cost as the blocker. R1 refused a census KEY on a DERIVED cost; `linkedin_notifications` already pays the same badge knowingly for a tool whose purpose is reading; (b) lets the server connect |
| `JOBS-APPLICATION-SUBSTRING` | 9 | CODE, `1a94cf9` | NO | 8 NO, 1 EXT | Lifted by (b) -- move at merge |
| `TYPING-RULING-MENTIONS` | 7 | OPERATOR (the typing ruling), read by a wave | YES | 6 EXT, 1 NO | Ask him once whether "text the caller supplied" forbids a mention the caller names. `M C11` is not reached at all: a hashtag he types is his own text, as the row says |
| `APPLY-NO-GUESSED-STEPS` | 6 | CODE, 2026-08-25 | NO | 6 NO | Return to GAP, blocked on measuring the multi-step form. The rule forbids guessing, not applying, and (b) lets the server apply |
| `RETIRE-CONTACT-IMPORT` | 5 | WAVE, 2026-09-05 | NO | 4 YES, 1 EXT | Include in the one retirement ruling. `N 106` leans on the off-domain rule, which he was never asked |
| `RETIRE-PANEL-NOT-OBSERVED` | 3 | WAVE, 2026-09-05 | NO | 3 YES | Re-file as MEASURED-ABSENT: it rests on a measurement, not a decision -- the `N 157` precedent |
| `RETIRE-HELP-CENTER-FORM` | 3 | WAVE, 2026-09-05 | NO | 3 YES | Include in the one retirement ruling |
| `MEASURED-NO-LINK` | 3 | WAVE, 2026-09-01 | NO | 3 NO | Return to GAP: the measurement shows no LINK to the scheduled list and records the Schedule control as a modal button |
| `R9-OUTREACH-AUTOMATION` | 3 | OPERATOR, the 2026-08-23 cut | YES | 3 EXT | Lifted by (b) -- move at merge. `M M5` stays held by the 2026-09-04 profile ruling |
| `ROSTER-ENUMERATION` | 3 | LEAD, 2026-09-05 | NO | 3 YES | Put to him: a lead ruled `N 165` out by name on a privacy stance he has not recorded |
| `OFF-DOMAIN-FORM` | 2 | CODE, 2026-08-25 | NO | 2 YES | Put to him: 2026-08-25 records this refusal was left out of his ruling and "is a separate question to put to him" |
| `URL-UNREACHABLE-237` | 2 | WAVE | NO | 2 NO | Return to GAP: "no URL reaches it" is the inference 2026-08-25 rejected for the same 237-url measurement |
| `RETIRE-LIVE-BROADCAST` | 2 | WAVE | NO | 2 YES | Include in the one retirement ruling |
| `PF-DEANONYMISE-A-VIEWER` | 2 | CODE, 2026-08-23 | NO | 2 YES | Keep; ask him to ratify -- the key names the act |
| `PF-REPOST-OR-SHARE` | 2 | CODE, 2026-08-30 | NO | 2 YES | Put to him: the key's own ground is "not among the capabilities asked for", and (b) asks for posting |
| `RETIRE-AI-ASSIST-MESSAGING` | 2 | WAVE | NO | 2 YES | Include in the one retirement ruling |
| `NO-ROUTE-MEASURED` | 1 | WAVE, 2026-09-19 | NO | EXT | Return to GAP: the write route is unbuilt, not measured closed |
| `ARTICLE-ROUTE-NOT-USED` | 1 | CODE, 2026-09-01 | NO | NO | Return to GAP: an unmeasured anchor rules nothing out |
| `PF-AUTO-ACCEPT-OR-REPLY` | 1 | CODE, 2026-08-23 | NO | NO | Return `M M39` to GAP: its own cell says the key's hinge, "did not read", does not reach an away message he writes |
| `POST-EDIT-SUBSTRINGS` | 1 | CODE, `1a94cf9` | NO | YES | Lifted by (b) for `/post/`; decide with `EDIT-FAMILY` for `/edit/` |
| `FOLLOW-SUBSTRING` | 1 | CODE, `1a94cf9` | NO | NO | Lifted by (b) -- move at merge |
| `PF-MARK-NOTIFICATIONS-READ` | 1 | CODE; measured impossible 2026-08-24 | NO | YES | Keep: no control and no target |
| `PF-LOOP-SWEEP-SCHEDULED` | 1 | CODE, 2026-08-23 | NO | YES | Keep: meets the unattended bar |
| `FEED-CONTENT-READ` | 1 | LEAD, 2026-09-05, "on his behalf" | NO | YES | Keep; ask him to ratify |
| `NAV-FROM-PAGE-CONTENT` | 1 | LEAD, 2026-09-19 | NO | YES | Keep; the lead ruled the row by name |
| `FOLLOW-PEOPLE-LIST` | 1 | CODE | NO | YES | Keep; the argument is aimed at this list |
| `DRAFT-DELETE-NOT-PRESSED` | 1 | CODE, 2026-08-26 | NO | YES | Decide with `PF-DELETE-OR-WITHDRAW` |
| `RETIRE-DEVICE-GEOLOCATION`, `-MOBILE-APP-ONLY`, `-SIGNIN-INTERSTITIAL`, `-PAID-BOOST`, `-VOICE-CAPTURE`, `-OFF-PLATFORM-WIDGET` | 6 | WAVE, 2026-09-05 | NO | 6 YES | Include in the one retirement ruling |

**THE SETTINGS FAMILY, 82 ROWS, AND THE QUESTION HIS WORDS LEAVE OPEN.** His
ruling, 2026-08-31: *"ONE NAMED settings page below `/mypreferences/d/` -- one
at a time, never the family, never a wildcard."* That is an ADMISSION rule. It
does not say any unnamed setting is ruled out; it says each needs its own
naming -- *"A second page needs a second ruling"*. The census filed the
unnamed ones EXCLUDED-RULED and made "the operator names it" the reopener,
which is the same fact written as a closure. **The question for him is one
line: does "never the family" mean these 73 stay out until he names one, or
that they are open work waiting on his naming?** The first keeps the
denominator; the second puts 73 rows back into it.

**THE TWELVE RETIREMENT FAMILIES, 32 ROWS, AND WHY THEY ARE ONE QUESTION.**
`_audit/2026-09-03-linkedin-gap-blockers.md` s4 defined the DECIDE-RETIRE queue
as *"Needs his answer, and the answer is almost certainly 'no'"*, costed each
with `R`, "an operator ruling". `_audit/2026-09-05-decide-retire-rulings.md`
answered it -- *"32 rows are retired by a ruling written here"* -- and the
2026-09-05 lead record closes it as a wave output. **No operator answer is
recorded.** The grounds are the strongest in this table; the authority is not
his. One ratification settles all twelve.

## 5. MEASURED-ABSENT -- 7 ROWS, 6 WITH EVIDENCE, 1 WITHOUT

"With evidence" means the reading -- instrument, surface, date, counts -- is
recorded in a TRACKED document a clone can open. Raw captures stay local by
design and are not required.

| row | the measurement | recorded in | class |
|---|---|---|---|
| `N 118` | live 2026-09-04, `/in/me/details/skills/`: 20 cards, 2,359 chars of `main`, 0 `endors` | `2026-09-03-linkedin-gap-blockers.md` Amendment B2 | M+ |
| `P E7` | the same reading (the same capability), plus the `endorsements` field emitted on every call | the same table | M+ |
| `P L2` | live 2026-09-04, `/in/me/` topcard: 1 relationship line, CONNECTIONS; 0 followers lines. Topcard only, as the row says | the same table | M+ |
| `N 157`, `M M4`, `J 127` | InMail balance: three instruments, the last a raw-versus-rendered sweep of all 25 captures | `2026-09-20-the-first-firing.md` 4b; `2026-09-20-the-live-capture.md` 13.3 | M+ |
| `N 136` | an unpressed control tally of `/analytics/profile-views/`, 2026-09-05 | its cited evidence is in gitignored `_scratch`. The tracked `2026-09-20-the-premium-block.md` 1.2 records that source saying "still not established", an `analytics-section-show-more` control never pressed on a surviving reading, and the shipped reader declaring absence on that page UNKNOWN | **M-** |

**Recommendation: return `N 136` to GAP**, blocked on pressing
`analytics-section-show-more` -- a press `DISCLOSING-PRESS-PERMITTED` allows
only if that control meets its four conditions, which nobody has checked.

## 6. THE CHECKER -- `scripts/check_exclusion_basis.py`

It fails when an EXCLUDED-RULED row has no traceable basis, and on everything
that would make a basis untraceable while the table still looked complete:
coverage drift in either direction, a family it does not know, an `op=` that
contradicts the registry, a link the census does not carry, a source file or
anchor that no longer resolves, a family whose own source rots, a malformed
lifted row. Lifted rows fail under their own heading. **At the commit that
ships it, it exits 1: 26 untraced, 27 lifted, 0 structural problems.**

It imports the shipped parse -- `census_completion.walk()` for the population,
`classify_writeoff_reasons.build()` for each row's resolved text -- and
cross-checks the two walks. Its family registry is its vocabulary, like
`STATES` is the counter's, and every attribution in it is anchored to verbatim
text the checker re-reads on every run.

**Shown failing, twice over.** `tests/test_exclusion_basis.py`, 36 tests: every
failure mode planted into a world built in the test and, where the real corpus
can exhibit it, into a copy of the real table -- each red AND naming its row.
Then the tests themselves, run against five broken checkers (link check
always true, coverage blind, sources never read, untraced verdict dropped,
lifted verdict dropped): **control 36 passed; every mutation red, 3 to 5
failures each.**

**What it cannot check.** The class of a row is a recorded judgement; the
checker proves the judgement cites something real and reachable, not that it
is right. Section 7 is the only check on that.

## 7. VERIFICATION -- PENDING

## 8. GATES RUN AND NOT RUN -- PENDING
