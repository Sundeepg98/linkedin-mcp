claude-opus-5-5[1m]

# Lane L7 -- WRITES TO HIS OWN PROFILE: the 36 R3 profile-family rows, classed and given one outcome each

Written as the lane runs. Worktree branch cut from `master` at `9c219c8`. Nothing in this lane
touches LinkedIn: no browser is attached, no grant is issued outside fixture tests, and
`writes_enabled()` stays False in every process this lane starts. Fixture tests drive a local
headless Chromium over static HTML with no network.

## 0. Status log

- lane opened; read the governing rulings (`_audit/2026-09-23-rulings-write-class-and-delegated-calls.md`),
  the lane-L4 record, the write machinery in `linkedin_server/writes.py` (spec, grant, preview,
  `_live_control`, `perform`, `_verify_after`), the editor readers in `linkedin_server/dom.py`, and the
  census cells of all 36 rows.
- the denominator derived (section 1): 36, the same set the brief lists.
- **A DEFECT IN THE SHIPPED MECHANISM, REPRODUCED RED BEFORE ANY BUILD (section 3).**
  `linkedin_update_profile_field` fills (or selects) the field and NEVER PRESSES `Save`, and its
  verification re-reads the SAME, still-unsaved dialog -- so it reports `performed: true` on an edit
  that LinkedIn never stored. Driven end to end (real preview, `consume`, `perform`) over a stateful
  frozen world in which a value persists only if the dialog's `Save` was pressed before the next
  navigation: receipt `performed: true`, `observed_state: field_changed`, `clicks_made: 0`, and the
  stored value UNCHANGED afterwards. Every intro-editor write row the census files COVERED-UNFIRED
  (`P A8`, `A11`, `A13`, `A17`, `A19`, `A21`) rests on this tool.
- the family repair built and gated on its own tests: 24 passed; the four tests that carry the defect
  were run against the UNREPAIRED `writes.py` (the file at `9c219c8`, swapped in and swapped back,
  byte-compared after) and all four failed for the reason each names (section 3.3).
- the gate (section 8): the impact selection, 179 files, ran at the second commit -- 24 reds, each tied
  in section 7 to the pin or baseline that clears it. It found three moves this record had not listed
  (the pointer graph, the reader baseline, the shard timings), and one pointer this lane moved is NOT
  its to re-pin (`P G3`, section 6.1, finding 5).
- the one cold verification (section 8, item 7): 21 of 21 PASS, nothing left behind in the worktree.
  Then a read-only merge dry-run against `master`: six files conflict, and no census row was changed
  by both sides (section 7, "at the merge").
- **the integration** (section "Integration 2026-09-24"), on the orchestrator's order: `master` merged,
  the census resolved row by row; **the save gate now refuses before the press unless condition 1 is
  established -- the order assumed it already did, and it did not**; a seam for the amended condition,
  not wired; `P G3` named; the six intro-editor rows' basis recorded; `P I14`'s restore gap and live-fire
  prerequisites in its cell; every pin re-derived on the merged tree; both baselines regenerated; the
  shard timings left for the orchestrator.

## 1. THE DENOMINATOR, DERIVED

Read off `_audit/_census/write-classes.tsv` at `9c219c8` with the brief's filter: class `R3` and act
one of `profile-edit` (9), `open-to-adjacent` (9), `profile-badge` (3), `profile-setting` (2),
`endorsement-visibility` (2), `services-page` (9) and `verification` (2):

    36 rows    P A14 A15 A22 A24 A26 A27 A28 A29 B7 B8 B9 D24 D27 D29 E6 G2
               H1 H2 H3 H4 H5 H6 H7 H8 H10 I13 I14 I15 I16 J1 J2 J3 K9 N14
               N 114, N 176

**It agrees with the brief's list exactly.** `P H9` (request service reviews) is `invite-others`, not
`services-page`, and is correctly outside the slice. Three pairs inside the slice are ONE capability
filed twice, and each pair gets one outcome: `P B8` / `P K9` (the Top Voice badge's show/hide,
`a1577365` both), `P B7` / `P J2` (the #Hiring frame), and `P E6` / `N 114` (hiding an endorsement he
received). Outside the slice, `P I14` has a jobs twin, `J 86` ("I'm interested"), which this lane may
not edit.

## 2. THE CLASS OF EACH ROW, AND THE RULE THAT ASSIGNS IT

Four classes, from the brief, each tied to the ruling that decides its live proof:

* **SELF-PRIVATE** -- an edit to his own profile field or display that targets nobody. Live proof
  permitted on the four conditions of the ruling `SELF-PROFILE-EDITS-NOT-OUTWARD`.
* **VISIBLE-TO-OTHERS** -- an act whose point is other people: a company's recruiters, anyone
  viewing a frame or a public page, or a named third party's endorsement. Built where the DOM is on
  record; its live proof fires only at a target or content the operator names
  (`OPERATOR-NAMES-THE-TARGET`).
* **BROADCAST-BY-NATURE** -- the act is itself a broadcast (a share, a new section entry of the kind
  the ruling's own example names). Excluded from live proof by the ruling itself.
* **CREDENTIAL** -- identity verification or account recovery. Never live-proven unless he names
  it (`CREDENTIAL-SETTINGS-NEED-THE-OPERATOR`), and a build is judged separately.

## 3. THE SHIPPED MECHANISM DID NOT COMMIT, AND NOW IT DOES

### 3.1 What was wrong

`writes.perform` filled or selected the field, then ran the gate that follows every fill. For
`update_profile_field` that fell through to `_publish_submit_gate` -- the POST composer's gate --
which looked for a post editor on the intro editor, found none (`1_editor_absent`) and pressed
nothing. A select never reached a gate at all: the select queue drains before the click loop, and the
click queue is only pre-loaded when there is nothing to fill or select. `_verify_after` then read the
field back **on the same, still-open dialog**, found the typed value and returned `field_changed`.
So the write this package describes as its best verified reported `performed: true` for an edit
LinkedIn never received. The restore block had a smaller defect beside it: the prior value, read
BEFORE the change, was described as "read live from the editor after the write".

### 3.2 The repair (`linkedin_server/profile_editor.py`, and three hunks in `writes.py`)

* **A gate of its own, `profile_editor.read_save_gate`,** reached after a fill (a new `elif` ahead of
  the composer's `else`) and after a select (asked once the select queue drains). It reads the SAME
  self-owned container the write aimed in -- `dom.read_self_owned_editor_fields`, whose container
  anchor is `Save` itself -- and proceeds only if exactly one control is named `Save` and it is
  enabled. Its selector is built from `dom.EDITOR_ANCHOR_NAME`, so the container the write aimed in
  and the control it presses cannot come apart. **No new click call site**: the press drains through
  `perform`'s one click, like the composer's submit.
* **Notify-network, condition 1 of the ruling, read in the dialog.** A CHECKABLE control named for
  notifying the network that reads checked (or unreadable) refuses the press; unchecked is reported
  `off`; none is `not_drawn`; and every checkable control with NO accessible name is counted, because
  the measured intro editor draws two such switches and either could be that control. The receipt's
  `notify_network_means` says `CONFIRMED OFF`, `NOT DRAWN` or `NOT CONFIRMED` in words -- and
  `not_drawn` beside a non-zero unnamed count is `NOT CONFIRMED`, never "off".
* **A poll after the press** (`wait_for_editor_to_close`, ten reads half a second apart) so the
  verification's navigation cannot abort LinkedIn's save request mid-flight. It decides nothing.
* **The verification navigates.** `_verify_after` now loads the editor's own address through the
  read door and reads the STORED value on a new render; a dialog nobody saved is discarded by that
  navigation and reads `value_unchanged`. `read_from` is the `/in/me/` address asked for, never the
  slugged landing. `_VERIFIED_FROM` says so.
* **`_editor_value_of` takes `when`**, and the prior read says "before the write".
* **The spec's `reversibility_procedure`** listed as unmeasured two facts that were measured on
  2026-08-31 (the editor renders the current value; its commit control is `Save`) and said the
  address was forbidden, which an exact exemption answered on 2026-09-02. It now names the one thing
  a round trip would add.

### 3.3 Shown failing, then passing

`tests/test_profile_editor_commit.py` drives the real preview, `consume` and `perform` over a world
whose stored value changes ONLY on a Save press before the next navigation. Against the unrepaired
`writes.py` (swapped in from `9c219c8`, swapped back, byte-compared), four tests failed, each for its
own reason:

    test_performed_true_means_the_stored_value_changed   performed true, store 'Oldtownvale'
    test_without_the_press_..._says_not_performed         observed 'field_changed', nothing saved
    test_a_chosen_value_is_saved_too                       the select was never saved
    test_the_restore_path_round_trips_...                  prior value read "after the write"

After the repair: 24 passed -- the four above; LinkedIn declining the value (the dialog stays, the
store is unchanged, `performed: false`); notify-network on (refused `4_notify_network_not_off`, no
press), off (`CONFIRMED OFF`), and an unnamed switch (`NOT CONFIRMED`); a disabled Save; the restore
path as a round trip whose before and after readings are equal; the three grant controls for this
action; seven verdict refusals by code; and the selector matching the one visible Save, nothing after
the dialog closes, and nothing outside a dialog.

### 3.4 What this means for rows outside the slice -- raised, not edited

`P A8`, `A11`, `A13`, `A17`, `A19` and `A21` are COVERED-UNFIRED on this tool. Their state is
unchanged by the repair (the tool existed and would not refuse; it now also commits). Their cells do
not say the tool never committed, and they are not this lane's cells. Their live queue is the same as
this slice's intro-editor rows (section 7) -- and the first live proof of ANY of them should read the
receipt's `editor_save_gate.notify_network_means` before claiming condition 1.

## 4. THE BUILD: `P I14`, "I'M INTERESTED", SIGNALLED FROM A POSTING

**`linkedin_mark_company_interest(job_id, confirm_token="")`** -- spec `mark_company_interest`, the
fourteenth in `writes.PERFORMABLE`. Built to the bar `STANDING-SHAPE-OF-A-WRITE-RULING` sets and no
wider: a spec, a live read of the page the click lands on, a measured anchor, a verification on a fresh
render, and the same two calls behind the single-use, action-bound, target-bound grant with its 120 s
TTL. `writes_enabled()` gates every door; no grant was issued outside fixture tests; nothing was pressed
on LinkedIn. The verdicts live in the new `linkedin_server/company_interest.py`; `writes.py` carries the
spec and thin arms that delegate (`observe`'s `posting_interest` branch, `anchor_label_for`,
`_live_control`, `_verify_after`, `_WHERE_TO_LOOK`, `_VERIFIED_FROM`).

**WHY `mark`, AFTER TWO NAMES THE CONSERVATION LAW REFUSED.** The first build was named
`signal_company_interest`, and `tests/test_writes.py::test_a_sanctioned_write_cannot_evade_the_law_by_being_renamed`
convicted it: a write tool's name must carry a verb from `readonly.WRITE_VERBS`, and `signal` is not
one. The second, `share_company_interest` -- LinkedIn's own word on the card, "Members who share that
they're interested" -- passed that half and failed the other: the verb must be one the ORIGINAL
forbidden list already named (`_ORIGINAL_FORBIDDEN`, frozen), so a new capability cannot walk in under
a new verb. `mark` is on that baseline (`linkedin_mark_notification_read`) and describes the act without
distorting it -- the press marks him as interested, for that employer's recruiters -- so it is the
rename that file's own comment prefers ("the preferred fix ... wherever it did not distort the name")
over growing its ruling-admitted verb list. Both refusals were the law working; neither was relaxed.

### 4.1 Why this row, and the evidence it rests on

It is the one row of the 36 whose three prerequisites were already paid. The ADDRESS: `/jobs/view/<id>/`,
the page `save_job` and `follow_company` act on. The CONTROL: on record in THREE tracked captures
(`tests/fixtures/job_detail.html`, `job_detail_hydrated.html`, `job_detail_following_hydrated.html`) -- one
plain `<button>` whose only name is its own text, `I<U+2019>m interested`, in
`div[componentkey^="JobDetails_AboutTheCompany"]`, beside LinkedIn's Help article `a1380509`.
`linkedin_job_detail` has reported it (`interest_control`) since it shipped; nothing pressed it. The
VERIFICATION: a fresh render of the same posting.

Read over the five posting captures the repository tracks (counts only):

    capture                            card  OFF in card  OFF on page  section controls  verdict
    job_detail                            1            1            1                 1  not_signalled
    job_detail_hydrated                   1            1            1                 1  not_signalled
    job_detail_following_hydrated         1            1            1                 1  not_signalled
    job_detail_following (skeleton)       1            0            0                 0  unknown
    job_detail_shell                      0            0            0                 0  unknown

### 4.2 The anchor: identity from the card, the label from the capture

The control's name carries no company, so identity comes from the CARD: `shape.company_about_card`
must read the card as the posting's OWN employer (not `absent`, `unhydrated` or `unnamed` -- the same
rule `linkedin_job_detail` applies), and exactly ONE control in that card may wear the OFF label. The
click selector is a module CONSTANT (`company_interest.OFF_CONTROL_IN_CARD`); Playwright's strict mode
holds it to one element. Every `why` is built from counts and constants: no page string is quoted.

### 4.3 What is not measured, and which way each gap fails

* **The ON label.** Every capture shows an employer he had not signalled. A card whose interest section
  draws a control that is NOT the OFF label reads UNKNOWN and is refused -- never reported as signalled,
  never pressed. Pressing it could withdraw the interest.
* **Whether one press completes the act.** The verification's NEGATIVE is strong: the OFF label still
  drawn on a fresh render means NOT signalled, `performed: false` -- including when the press opened a
  further step this server did not take (the navigation discards it). Before navigating, the
  verification records what the press left in place (OFF controls, section controls, dialogs open), so
  the first supervised press MEASURES any second step rather than guessing at it.
* **The undo.** `P I15` presses the ON control, which no capture holds; it is not built.
* **The spend.** Census row `J 86` quotes LinkedIn's Help as "max 50, expires 1 year"; the spec's
  `spends` repeats it as a quotation, not a measurement.
* **THE BRIEF'S BUILT BAR, CLAUSE BY CLAUSE, AND THE ONE THIS ROW DOES NOT MEET.** Off by default:
  yes (`writes_enabled()`). Grant-gated where the family is: yes, the same single-use, action-bound,
  target-bound grant. Failing controls: yes, the three in 4.4 plus the derived worlds. **A restore path
  that is itself tested: NO.** The removal is `P I15`, and it presses the ON-state control, which no
  capture holds, so there is no restore through this server and nothing to test. This record does not
  round that off: a live proof of `P I14` leaves the interest signalled until he withdraws it himself in
  LinkedIn, which is one more reason it fires only at a posting he names -- and its first press is also
  the capture (C6) that would let `P I15` be built.

### 4.4 The three controls, and the rest -- `tests/test_mark_company_interest.py`

1. **No grant.** Writes off: preview, `consume` and the tool refuse (`writes_disabled`). Writes on: an
   empty, `None`, `True` or forged token refuses at `consume`; an unredeemed grant and a non-grant refuse
   at `perform`. Zero navigations across every refusal.
2. **A grant for another target.** A token for job `4600000042` is refused for `4600000043`, and refused
   for `follow_company` and `save_job` on the SAME job -- the pairings most worth refusing, since all
   three act on that address.
3. **A second use.** The token cannot be redeemed twice, and the redeemed grant cannot be performed twice
   (zero navigations on the second).

Plus: all three tracked captures read `not_signalled`; the skeleton and the shell read unknown; four
DERIVED worlds (an unmeasured ON label, two OFF controls, a card naming another company, no control) are
refused at the verdict AND at the preview with no grant minted and no page string in the refusal; the
verification verdict's five outcomes; and four end-to-end runs -- a moved control (`performed: true`,
DERIVED after-world), the OFF label still drawn after the press (`performed: false`), a section that
vanished (`unknown`, never "signalled"), and a fresh render of another company's card (`unknown`).

**A DEFECT IN THIS BUILD, CAUGHT BY ITS OWN TEST BEFORE THE COMMIT.** The first version found the
interest section as "the nearest ancestor of the Help link that holds a button". With the control
removed, that climb kept going to the whole card and counted its Follow control and 'more' toggle --
`test_every_derived_world_...[no-control]` read "the section draws 2 control(s)" -- and at the
verification a section drawing controls with no OFF label reads as a control that MOVED, i.e.
`performed: true` for a card that had merely lost the section. The section is now the innermost
`div[componentkey]` INSIDE the card that holds the Help link (the shape all three captures draw), so a
vanished control counts zero and an unkeyed block counts zero -- both fail towards unknown.
`test_the_section_is_bounded_so_a_missing_control_counts_zero` and
`test_a_section_that_vanished_after_the_press_is_unknown_not_moved` hold it.

## 5. THE CLASS TABLE MAY NOW RECORD AN R3 DISPOSITION

`scripts/check_write_classes.py` refused any disposition but `classify-only` on a non-R1 line ("R3 is
classify-only in this lane" -- lane L4's rule for its own lane). This lane took all 36 of its R3 rows to a
build or a named queue, and `P I14` LEFT GAP, which the coverage check accepts only for a `built:` line.
So the rule now reads: R2 stays classify-only; R3 may carry `built:` or `queued:`; and the checks that
make a disposition TRUE are untouched and apply to R3 exactly as to R1 (`built:` must name a performable
action whose row has left GAP; `queued:` must still be a write-direction GAP row). Two plants were added
to `tests/test_write_classes.py`: an R3 queue is not a problem, and an R3 build naming a non-performable
action on a row still GAP is convicted twice, by name. The existing R2 plant still convicts.

## 6. EVERY ROW: ITS CLASS, ITS ONE OUTCOME, AND WHY

    class                 rows   BUILT   NEEDS-CAPTURE   BLOCKED
    SELF-PRIVATE            13       0              10         3
    VISIBLE-TO-OTHERS       19       1               3        15
    BROADCAST-BY-NATURE      2       0               0         2
    CREDENTIAL               2       0               0         2
    ------------------------------------------------------------
                            36       1              13        22

Counted off the table below, row by row. Three pairs are one capability filed twice (`B7`/`J2`,
`B8`/`K9`, `E6`/`N 114`) and are counted as the census counts them, once per row.

The disposition each row now carries in `_audit/_census/write-classes.tsv` is the token in the last
column (`built:<action>` or `queued:<TOKEN>`) -- the lane's own names for what binds each row, not names
from the blocker ledger.

| row | class | outcome | why | token |
|---|---|---|---|---|
| P A14 postal code | SELF-PRIVATE | NEEDS-CAPTURE | the family needs no new code (it aims at any named control, and now commits); the control was NOT DRAWN among eleven on the render-gated 2026-09-19 reading, while the container signature reads `unknown` over four unnamed controls; LinkedIn draws a postal code for some countries only | INTRO-EDITOR-FULL-READ (C1) |
| P A15 location display choice | SELF-PRIVATE | NEEDS-CAPTURE | as A14; the display choice follows a postal code | INTRO-EDITOR-FULL-READ (C1) |
| P A22 primary position | SELF-PRIVATE | NEEDS-CAPTURE | a display choice on his own intro, not a new position; a select the family chooses by option text once named; not drawn 2026-09-19 | INTRO-EDITOR-FULL-READ (C1) |
| P A24 ID name as additional name | CREDENTIAL | BLOCKED | presupposes a completed identity verification (`K2`, settings family); operator-only by `CREDENTIAL-SETTINGS-NEED-THE-OPERATOR`; no control exists to capture, and no build is appropriate before he has a verified name | CREDENTIAL-OPERATOR-ONLY |
| P A26 website | SELF-PRIVATE | NEEDS-CAPTURE | a field of his own contact-info editor, never opened | CONTACT-INFO-EDITOR (C2) |
| P A27 phone | SELF-PRIVATE | NEEDS-CAPTURE | as A26 | CONTACT-INFO-EDITOR (C2) |
| P A28 instant messenger | SELF-PRIVATE | NEEDS-CAPTURE | as A26 | CONTACT-INFO-EDITOR (C2) |
| P A29 birthday and its visibility | SELF-PRIVATE | NEEDS-CAPTURE | as A26; a birthday visible to connections drives LinkedIn's reminders, so value AND audience are restored in the session | CONTACT-INFO-EDITOR (C2) |
| P B7 #Hiring frame | VISIBLE-TO-OTHERS | BLOCKED | the same capability as J2; part of Open to Hiring, which is blocked (J1) | OPEN-TO-HIRING-ENTRY |
| P B8 Top Voice badge show/hide | SELF-PRIVATE | BLOCKED | the same capability as K9; no Top Voice badge on this account (`K8`: zero in text AND in names, on an instrument shown able to disagree with itself) | NO-TOP-VOICE-BADGE |
| P B9 Premium badge show/hide | SELF-PRIVATE | NEEDS-CAPTURE | he is Premium (his profile draws the icon); where its switch lives is not on record; the intro editor's two UNNAMED switches are the candidates | INTRO-EDITOR-FULL-READ (C1) |
| P D24 open to volunteering | VISIBLE-TO-OTHERS | NEEDS-CAPTURE | tells nonprofits he is open to volunteering; its entry is an ANCHOR on his profile render, to `/in/<member>/opportunities/volunteering/education/`; the `/in/me/` spelling is refused today | OPEN-TO-EXPLAINER-PAGES (C3) |
| P D27 secondary-language profile | VISIBLE-TO-OTHERS | BLOCKED | its editor is the anchor to `/in/<member>/edit/secondary-language/`; its only undo is the delete half, which `delete_or_withdraw_anything` refuses, so no live proof can restore in the session | UNDO-IS-A-DELETE |
| P D29 Learning certificate | BROADCAST-BY-NATURE | BLOCKED | a new section entry, the kind of change the ruling's own example names; its form is the excluded `/edit/` certifications editor (`D13`); its undo is a delete | BROADCAST-BY-NATURE |
| P E6 hide an endorsement received | VISIBLE-TO-OTHERS | BLOCKED | the same capability as N 114; it targets one member's endorsement; no endorsement is drawn on his skills page (`E7`, network `118`); an endorsers address carries `/endorse` | NO-ENDORSEMENT-DRAWN |
| P G2 activity default view | SELF-PRIVATE | NEEDS-CAPTURE | a display preference; its control is an ANCHOR, 'Edit default activity', to `/in/<member>/edit/forms/content-collections-star-pill/new/`, whose `/in/me/` spelling is refused by `/edit/` today and admissible by the ruling `PROFILE-EDITOR-ADDRESSES-ALLOWED` | DEFAULT-ACTIVITY-FORM (C4) |
| P H1 create a Service Page | VISIBLE-TO-OTHERS | NEEDS-CAPTURE | a public listing; its entry is an ANCHOR to `/in/<member>/opportunities/services/education/`, also drawn in the tracked `profile_topcard_hydrated.html`; the `/in/me/` spelling is refused today | OPEN-TO-EXPLAINER-PAGES (C3) |
| P H2 service categories | VISIBLE-TO-OTHERS | BLOCKED | no Service Page exists (H1) | NO-SERVICE-PAGE |
| P H3 about text | VISIBLE-TO-OTHERS | BLOCKED | no Service Page exists | NO-SERVICE-PAGE |
| P H4 location / remote | VISIBLE-TO-OTHERS | BLOCKED | no Service Page exists | NO-SERVICE-PAGE |
| P H5 rate / pricing | VISIBLE-TO-OTHERS | BLOCKED | no Service Page exists | NO-SERVICE-PAGE |
| P H6 edit the page | VISIBLE-TO-OTHERS | BLOCKED | no Service Page exists | NO-SERVICE-PAGE |
| P H7 unpublish the page | VISIBLE-TO-OTHERS | BLOCKED | no Service Page exists; an unpublish withdraws a public page, which wants `delete_or_withdraw_anything` read against it first | NO-SERVICE-PAGE |
| P H8 link to a Company Page | VISIBLE-TO-OTHERS | BLOCKED | no Service Page exists | NO-SERVICE-PAGE |
| P H10 manage reviews | VISIBLE-TO-OTHERS | BLOCKED | no Service Page exists | NO-SERVICE-PAGE |
| P I13 minimum pay preference | SELF-PRIVATE | NEEDS-CAPTURE | a matching preference; its page IS url-addressed -- a jobs capture draws `/jobs/preferences?viewType=SEEKING_PREFERENCES` -- and refused today | JOB-SEEKER-PREFERENCES-PAGE (C5) |
| P I14 signal interest in a company | VISIBLE-TO-OTHERS | **BUILT** | section 4; now COVERED-UNFIRED; its live proof fires only at a posting he names | built:mark_company_interest |
| P I15 remove that interest | VISIBLE-TO-OTHERS | NEEDS-CAPTURE | presses the ON control, which no capture holds; I14's first supervised press produces it | INTEREST-ON-LABEL (C6) |
| P I16 share how you found your job | VISIBLE-TO-OTHERS | BLOCKED | LinkedIn asks it after a job change -- a new position, the ruling's broadcast example -- and he has no new job to share | NO-JOB-CHANGE |
| P J1 turn on #Hiring | BROADCAST-BY-NATURE | BLOCKED | a share by nature, excluded by the ruling, and a false public claim for a job seeker; its entry ('Hiring' in the Open-to menu) has no declared activation relation, and the Open-to family's entry is where the Open To Work editor fires `saveAndFetchNextStep` | OPEN-TO-HIRING-ENTRY |
| P J2 #Hiring frame | VISIBLE-TO-OTHERS | BLOCKED | the same capability as B7; blocked with J1 | OPEN-TO-HIRING-ENTRY |
| P J3 which job the frame links | VISIBLE-TO-OTHERS | BLOCKED | blocked with J1, and it needs a job he posted as a hirer; none on record | OPEN-TO-HIRING-ENTRY |
| P K9 Top Voice badge show/hide | SELF-PRIVATE | BLOCKED | the same capability as B8 | NO-TOP-VOICE-BADGE |
| P N14 identity verification for recovery | CREDENTIAL | BLOCKED, no build | account recovery with his government ID and a live selfie through a third party; this server must never present his documents or his face; operator-only | CREDENTIAL-OPERATOR-ONLY |
| N 114 hide an endorsement received | VISIBLE-TO-OTHERS | BLOCKED | the same capability as P E6 | NO-ENDORSEMENT-DRAWN |
| N 176 no network update on joining a group | SELF-PRIVATE | BLOCKED | its only route is `/psettings/group/<id>` ('Update your settings', measured 2026-09-05): two forbidden substrings, and a persisted preference the settings ruling admits by name or not at all; row `170` on the same page is EXCLUDED-RULED | GROUP-SETTINGS-PAGE |

### 6.1 Findings for other owners -- raised, not ruled here

1. **`P I12` and jobs `J 99` rest on "zero of 237 urls reach" the career-interests page -- a count taken
   over PROFILE captures.** A local capture of the job-alerts page draws a 'Preferences' anchor to
   `/jobs/preferences?viewType=SEEKING_PREFERENCES` (role=button), and the completeness probe recorded
   `/jobs/preferences` on 2026-09-23. `J 99`'s own reopener is "a click route to this page"; this is a
   URL route. Both rows are EXCLUDED-RULED and this lane may not edit them.
2. **`N 176` sits on the same settings page as `N 170`**, which is EXCLUDED-RULED by propagation.
   Whether `N 176` follows it by the ruling `MESSAGING-SETTINGS-CAPABILITY-LEVEL` is the exclusions owner's
   call.
3. **`J 86` is `P I14`'s jobs twin** and still reads GAP; its owner decides whether it moves with this
   build (the same tool, the same control).
4. **The six intro-editor rows outside this slice** (`P A8`, `A11`, `A13`, `A17`, `A19`, `A21`) rest on
   the tool this lane repaired (section 3.4).
5. **`P G3` reads its argument off whichever row sits above it, and this lane moved that row.** Its
   cell is `same ruling`, which the census's own resolver (`BACKREF` in
   `scripts/classify_writeoff_reasons.py`) reads off the nearest SUBSTANTIVE row above it. At the base
   that was `P G1` -- a sentence about a reliability defect, not a ruling -- because `P G2`'s "no tool,
   no reason" leaves 14 characters once the furniture is stripped, one short of the 15 the resolver
   calls substantive. This lane's note makes `P G2` substantive, so `P G3` now inherits a note that
   argues an ADMISSIBLE editor address, the opposite of an exclusion. Measured with `--explain "P G3"`
   at the base and on this branch: its kind moves from `US-RULING` to `ACCOUNT-FACT+US-RULING`,
   contingent, with no reopener, and the classifier's re-examine list goes from 2 to 3.
   `scripts/measure_pointer_graph.py --check` convicts it by name (section 7). `P G3` is
   EXCLUDED-RULED and not this lane's to edit. The repair is one cell: name the ruling rather than a
   position. `P G4` and `P G5`, directly below and written in the same commit (`7931cefb`, whose message
   counts 23 rows of the `/edit/` family moved at once), name theirs as the `/edit/` family ruling; the
   owner decides whether that is `P G3`'s too. Until that edit, `P G3`'s edge must not be re-pinned: a
   re-pin would certify an argument nobody wrote for it.
   **DONE AT THE INTEGRATION, on the orchestrator's call:** `P G3` now names the ruling lane R found
   under it -- the upload ban, not the `/edit/` family this paragraph guessed -- and is no longer a
   pointer; the pointer graph was re-pinned at 68 (Integration, I.3 and I.4).
   **ON `master` SINCE THIS BRANCH WAS CUT** (read at `ff98a7f`, 30 commits past the base; nothing
   merged here): lane R returned `P G3`, `G4` and `G5` to GAP, each with a named blocker. `P G3`'s
   cell still OPENS with `same ruling`, so it is still a positional pointer and the merged tree
   re-points it exactly as this branch does. The repair is unchanged -- one cell -- and it now belongs
   to whoever holds `P G3`'s GAP.

## 7. THE PINS THIS LANE MOVES -- NOT RE-PINNED HERE, AS THE BRIEF ORDERS

**RE-DERIVED AT THE INTEGRATION, 2026-09-24.** This section is the lane's PRE-MERGE measurement, every
move taken against the base. The orchestrator's integration order then asked for every pin to be
re-derived on the merged tree rather than added as a delta; section "Integration 2026-09-24" records
what was set, and where the two differ, that section is the current one.

Every figure below was measured on this branch after the census edit, by the instrument that owns it.
None was edited; each is the orchestrator's to re-pin at the merge, where sibling lanes move the same
lines.

**The census** (`scripts/census_completion.py --check`, exit 1 on exactly these and nothing else):

    adjudicated        434 -> 435
    b1_standing         10 ->  11     P I14 enters bucket 1
    delivered_broad    100 -> 101
    gap                270 -> 269
    gap_write          150 -> 149
    unfired             25 ->  26
    PINNED_B1_ROWS      + P I14, held by OPERATOR-NAMES-THE-TARGET (derived by
                        ruling_holds.hold_of for a W row, as N 47's was)

**The pointer graph** (`scripts/measure_pointer_graph.py --check`, and with it BOTH tests in
`tests/test_pointer_graph_guard.py` -- the second because its calibration control expects the tree to
pass the pin, so it fails whenever the first does): 4 of 69 pinned pointers moved; none gone, none new.

    P A27, P A28, P A29   still point at P A26; P A26's verdict moved  - -> ACCOUNT-FACT|US-RULING
    P G3                  re-pointed: P G1 -> P G2

The first three are this lane's rows and the move is intended: each carries its own note saying "As
`A26`", and `P A26`'s note is the argument they now inherit. Re-pin them at the merge. The fourth is
NOT intended and must not be re-pinned as it stands -- section 6.1, finding 5.

`scripts/count_census_states.py --expect J=54,P=53,M=77,N=85` MATCHES at 269 (it was `P=54`, 270).
`scripts/check_write_classes.py` is GREEN on 151 lines: the write-direction GAP population is 149 and
two lines are builds (`N 47`, `P I14`). `scripts/check_read_addresses.py` (66 of 66),
`scripts/ruling_holds.py` and `scripts/pin_census_rows.py --check` (no drift, 704 rows) are green.

**The tool surface and the write registry** -- one new tool, `linkedin_mark_company_interest(job_id,
confirm_token)`, one new spec and one new performable action. Measured by the gate in section 8:

    tools on the surface              51 -> 52    + linkedin_mark_company_interest
    of which write                    13 -> 14    (reads stay 38)
    writes.PERFORMABLE                13 -> 14    + mark_company_interest
    writes.SANCTIONED_WRITES          14 -> 15
    pinned tool parameters            69 -> 71    + job_id, confirm_token

Each red test, with the edit that re-pins it (none applied here):

| test | the edit |
|---|---|
| `tests/test_server_surface.py::test_the_surface_is_exactly_the_fifty_one_tools` | `len(tools) == 52`; rename and docstring to fifty-two |
| `tests/test_server_surface.py::test_no_tool_name_implies_a_write`, `::test_the_exemption_covers_only_the_names_on_it` | add `linkedin_mark_company_interest` to `SANCTIONED_WRITE_TOOLS` |
| `tests/test_server_surface.py::test_server_info_stops_claiming_read_only_once_writes_are_on`, `::test_the_capability_is_reported_even_with_the_flag_off` | add `mark_company_interest` to the pinned sorted list of performable actions |
| `tests/test_server_surface.py::test_the_server_instructions_name_every_write_that_ships` | `words[14] = "fourteen"`; in `server.py`'s instructions, "thirteen write" -> "fourteen write" and name `linkedin_mark_company_interest` beside the other writes |
| `tests/test_every_tool_is_on_the_surface.py::test_both_rules_reject_the_registry_that_was_actually_measured` | 51 -> 52 |
| `tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py::test_no_tool_appeared_or_vanished_without_a_census_decision` | add the tool to `PINNED_TOOL_SURFACE` (52 tools, 71 parameters); the census decision it asks for is `P I14`, banked in this lane |
| `tests/test_the_other_two_count_claims_are_pinned_too.py::test_the_readme_headline_agrees_with_the_registry`, `::test_the_readme_module_listing_names_the_right_number` | `README.md`: "Fifty-two tools ship. Thirty-eight read. Fourteen write." and "the fifty-two tools"; the module listing gains `profile_editor.py` and `company_interest.py` |
| `tests/test_prose_that_makes_a_claim.py::test_the_server_docstring_numbers_are_derived`, `::test_the_server_docstring_accounts_for_the_action_that_has_no_tool` | `server.py`'s module docstring: fifty-two tools, fourteen of which write, fifteen sanctioned (the fifteenth being `set_open_to_work`, the one with no tool) |
| `tests/test_tool_envelopes_emit_no_page_string.py::test_the_driven_set_has_not_silently_shrunk` | regenerate `tests/tool_envelope_baseline.json` (`python -m tests.test_tool_envelopes_emit_no_page_string --write-baseline`). The new tool's verdict was MEASURED in-lane through that file's own `drive_tool`, standalone with its `sandbox_session_store` applied and the baseline left unwritten: `not_driven:never read the page`, the verdict `linkedin_update_profile_field` and `linkedin_follow_company` also drive to today |
| `tests/test_readers_emit_no_page_string.py::test_the_driven_set_has_not_silently_shrunk` | five new page readers with no recorded verdict: `company_interest:read_after_press`, `:read_interest_control`, `:read_state`, `profile_editor:read_save_gate`, `:wait_for_editor_to_close`. Regenerate `tests/reader_leak_baseline.json` (`python -m tests.test_readers_emit_no_page_string --write-baseline`). All five were DRIVEN in-lane through that file's own `drive`, baseline unwritten: all five `clean`. The same pass found three recorded readers whose baseline says `returns_text` and which drive `clean` today (`dom:read_follow_control`, `writes:_read_follow_state`, `writes:_verify_after`) -- not a failure in that direction, and the first is in a file this lane did not touch, so the baseline was already behind before this lane; a regeneration records all three |
| `tests/test_ruling_holds.py::test_bucket_one_is_derived_and_sits_on_its_pins`, `::test_a_write_row_whose_direction_flips_is_named` | none of their own: both clear with the census re-pin above. The second picks as its victim the FIRST COVERED-UNFIRED write held by `OPERATOR-NAMES-THE-TARGET` in walk order, which is now `P I14`, and it expects that victim to be pinned. PROVEN IN MEMORY, nothing written: the six figures and the `PINNED_B1_ROWS` entry applied to the imported module, then `census_completion --check` exits 0 and the whole of `tests/test_ruling_holds.py` passes, 55 of 55 |
| `tests/test_pointer_graph_guard.py::test_the_committed_census_still_matches_its_pin`, `::test_every_failure_class_is_convicted_and_the_calibration_is_not` | the pointer-graph block above: re-pin `P A27`, `P A28`, `P A29`; do NOT re-pin `P G3` until its cell names its ruling |
| `tests/test_ci_shard.py::test_the_timings_table_still_prices_most_of_the_suite` | the paragraph below: one regeneration after the merge, from a full-suite junit report |
| `tests/test_writes.py::test_what_ships_is_narrower_than_what_is_sanctioned` | add `mark_company_interest` to both set literals |
| `tests/test_writes.py::test_the_gate_prints_every_measured_verdict_with_its_evidence`, `::test_every_verdict_is_pinned_to_ITS_ACTION_not_to_the_set_of_verdicts` | `_UNMEASURED_REVERSIBILITY` gains it; `REVERSIBILITY_CLASS[...] = "STILL-UNKNOWN"`; `REVERSIBILITY_MEASURED[...] = False` |
| `tests/test_preview_state_and_click_state.py::test_every_performable_action_is_either_reached_or_declared_unreachable` | `len(PERFORMABLE) == 14`, `len(REACHED) == 14` (the `REACHED` entry itself is in this lane) |
| `tests/test_receipt_names_its_own_action.py::test_the_action_set_is_the_one_this_file_was_measured_against` | 13 -> 14. Its phrase owners need no new entry: the rest of that file passes with the new rows in place, so neither new row prints a phrase another action owns |

**A COMMITTED MEASUREMENT THIS LANE TIPS, AND CANNOT REGENERATE ON THIS BOX:**
`tests/test_ci_shard.py::test_the_timings_table_still_prices_most_of_the_suite` goes red. It asks that
`scripts/ci_shard_timings.json` price at least two thirds of the live `tests/test_*.py` files. At the
base it priced 157 of 234 against a line of 156 -- ONE file of headroom -- and this lane adds two test
files (`tests/test_profile_editor_commit.py`, `tests/test_mark_company_interest.py`): 157 of 236
against a line of 157.33. Measured by `ci_shard.load_timings()` against the glob, on this branch and
again with the two files left out (157 of 234, green). It is a merge-level item, not a lane-level one:
every sibling lane that adds a test file moves the same ratio, and the repair is ONE regeneration
after the merge by the recipe in `scripts/ci_shard.py`'s docstring, which needs a full-suite junit
report -- the run the brief forbids on this shared box. Writing two entries by hand was refused: the
table's `_measured` line names the one run that produced every figure in it, and two figures that run
never measured would sit beside it as if it had.

**AT THE MERGE -- measured, nothing merged.** A read-only `git merge-tree --write-tree` of this
branch against `master` at `ff98a7f` (30 commits past the base) conflicts in six files and merges the
other twelve cleanly -- `linkedin_server/writes.py`, `linkedin_server/server.py`,
`_audit/_census/write-classes.tsv` and every test file among them. Three of the six are generated
(`_audit/INDEX.md`, `_audit/RULINGS.md`, `_audit/_census/blocker-map.tsv`): regenerate them after the
merge. `_audit/INSTRUMENTS.md` collides where two sections were appended at the same end: keep both.
The two census files collide by ADJACENCY ONLY. Compared row by row across the base, `master` and
this branch, `master` changed 105 rows of the profile slice and 95 of the network slice, this lane 34
and 2, and NOT ONE row was changed by both -- so each file resolves row by row: `master`'s text for
every row outside the 36, this lane's for the 36. Every move in this section was measured against
the base, and `master` has re-pinned since, with the lanes merged into it: apply each as a delta, or
re-measure on the merged tree.

**NOT A PIN, AND APPLIED HERE:** `tests/test_preview_state_and_click_state.py`'s `REACHED` gained the
new action (a coverage table, not a count: without it the action would be performable and driven by
nothing in that file), and `tests/test_write_classes.py` gained two plants.

## 8. COMMITS, GATES, AND WHAT DID NOT RUN

**Commits** -- on the worktree branch only; nothing pushed; no attribution line in any message. A hash
of this lane's names a commit on that branch and nowhere on `master` until the orchestrator merges it,
so each is listed here by its SUBJECT, which survives a squash or a rebase where a hash does not:

* *lane L7: update_profile_field now presses Save and verifies on a fresh render; P I14 "I'm
  interested" built, unfired; 36 profile-family rows classed* -- the family repair, the build, the
  class-checker rule, the census cells and class lines, INSTRUMENTS section 70, this record, and the
  three generated files at a fixed point.
* *lane L7: triage the two census pairs citing the lane record; route spellings made exact; P I14's
  missing restore path stated* -- two `NOT_A_CORRECTION` entries written after reading every site,
  the `/in/<member>/` route spellings, and section 4.3's paragraph on the missing restore path.
* *lane L7: the gate record -- the selection's 24 reds each tied to the pin that clears it; P G3's
  moved pointer raised; section 8* -- section 6.1's finding 5, section 7's additions, this section,
  and INSTRUMENTS 70.4-70.5. No code.
* *lane L7: record the cold verification (21 of 21) and the merge dry-run against master* -- this
  record only, written AFTER the one cold pass the brief budgets, so it is gated by the document
  selection (item 6) and not by a second cold pass.

**Gates that ran, and what each said.**

1. **The census instruments, at the tip.** `census_completion --check`: red on exactly the six figures
   and the one bucket-one entry of section 7 and nothing else -- and PROVEN COMPLETE rather than only
   listed: applied in memory to the imported module, nothing written, the same check exits 0 and
   `tests/test_ruling_holds.py` passes 55 of 55 (INSTRUMENTS 70.5). `count_census_states --expect
   J=54,P=53,M=77,N=85`: MATCH at 269. `check_write_classes`: GREEN, 151 lines.
   `check_read_addresses`: 66 of 66. `ruling_holds`: green. `pin_census_rows --check`: no drift, 704
   rows. `measure_pointer_graph --check`: RED on 4 of 69 pinned pointers, each named in section 7.
   `classify_writeoff_reasons --check`: exit 0, and its per-row table against the base differs in
   exactly one row, `P G3` (section 6.1, finding 5).
2. **The impact gate.** `scripts/impact_gate.py --against 9c219c8 --plan-only`, run by a child at the
   first commit: 17 changed paths, 174 of 236 test files (74%) -- WIDENED TO THE FULL SUITE past its
   45% line. So, as the brief orders, the full suite did NOT run here; the SELECTION did, with the
   corpus-wide guards. The plan prints 40 of its selected files and none of its 17 corpus-wide guards
   by name, so the child stopped rather than guess, correctly; the list was then written from the
   gate's own `impact_set()`: 179 test files, the 17 guards among them. Recomputed at the tip (18
   changed paths): the same 179, byte for byte.
3. **That selection, run** at the second commit (`-n 4`, verbose, one process): **24 failed, 7824
   passed, 4 skipped, 1 xfailed, no errors, 28 min 37 s.** The 24 reds are exactly the 24 ids of
   section 7's table: none unlisted, and no listed id passed. The skips are the three symlink tests of
   `tests/test_uploads.py` and one in `tests/test_the_audience_reader_arrives_with_its_contract.py`, and
   the xfail is in `tests/test_click_is_not_its_own_evidence.py` -- no file of the three is this
   lane's. The exact-value identity sweep was ARMED in this worktree (its key path resolves to the
   main checkout's gitignored key) and passed on all 18 paths this lane changed. The third
   commit changes only this record and the instrument register, so the code-level result stands for the
   tip; the guards that read those two documents were re-run there (6 below).
4. **Measured in-lane where a baseline would otherwise be regenerated:** the five new page readers
   through the reader family's own harness, all `clean`, and the new tool through the envelope family's
   own harness, `not_driven:never read the page` -- both baselines left unwritten (section 7).
5. **The lane's own tests, and the targeted runs while building** (not gates; each red repaired before
   the commit it would have entered, or listed in section 7): the two new files alone (24, then 30-odd
   passing); the write, surface and guard files around them in three batches -- 7 reds, then 7, then
   1 -- whose non-pin reds were the naming law twice (`signal`, then `share`: section 4), a new reader
   of `from_state` in `_live_control` (replaced by the verdict's own constant), the unbounded section
   count (section 4.4) and a test constant carrying LinkedIn's trailing full stop. The identity and
   hygiene guards: 1777 passed. The page-string guards and the readers inventory: 78 passed.
6. **The diff itself, and the documents** -- run at the third commit after its last edit, and again
   at the fourth. At the third: the diff from the base, 2771 added lines, all ASCII, none carrying an
   absolute workspace path, a user directory or the operator's name (a byte scan, and a pattern scan
   whose four planted controls each fire); `scripts/check_cited_shas_resolve.py` OK, every cited SHA
   an ancestor of `master`; the impact gate's own selection for this record and the instrument
   register -- 31 test files, the 17 corpus-wide guards among them -- **3 failed, 3274 passed**, the
   three being the shard-timings test and the two `tests/test_ruling_holds.py` tests, all in section
   7's table; and the three generators' `--check` at a fixed point. At the fourth, on the staged tree
   before its commit: its own 46 added lines, all ASCII and none carrying a machine path; the
   cited-SHA guard OK, the `master` hash cited here resolving as an ancestor of `master`; the same
   31-file selection, **3 failed, 3274 passed**, the same three; the generators at a fixed point.
7. **The cold verification** -- ONE pass, as the brief budgets, by an implementer child cold to this
   work, at the third commit, against a closed 21-item checklist, writing nothing in the worktree (its
   closing status read was empty): **21 PASS, 0 FAIL, 0 NOT RUN.** Measured independently of this
   lane's own runs: the 24 claimed reds are exactly the reds of the 13 files that hold them (703
   collected; 24 failed, 679 passed; none extra, none missing), and each is named in section 7's
   table; the census and pointer-graph moves match section 7 figure for figure; only `P I14` changed
   state; 2771 added lines scanned, none non-ASCII and none carrying a machine path; one literal call
   site each of `click`, `fill`, `select_option` and `set_input_files` (an AST walk); the save gate
   called twice inside `perform`; the lane's three test files, 82 passed; the identity and hygiene
   guards, 934 passed; `writes_enabled()` False with the flag unset. None of its surprises was a
   defect.

**NOT RUN, and why:**

* **the full suite** -- the plan widened to it and the brief forbids it on this shared box. It runs on
  CI after the merge.
* **CI on any platform** -- nothing was pushed.
* **any live run of anything** -- no browser, no LinkedIn, no grant outside fixture tests.
* **any re-pin, or any baseline regeneration** -- the brief forbids the first; section 7 lists every
  one of both with its edit.
* **the shard-timings regeneration** -- it needs a full-suite junit report (section 7).
* **`scripts/build_read_map.py`** -- the impact gate notes that its observed read map was recorded at an
  older commit; the static rules selected this lane's files without it, and rebuilding it is a
  measurement over the whole suite.

## Integration 2026-09-24

On the orchestrator's integration order (04:58). Sampled first, as the order asks: the worktree at the
lane's fourth commit and clean, `master` at `ff98a7f` -- 30 commits past the base, CI green -- and
`master` had not moved again when the merge ran. Everything below was measured on the MERGED tree. No
live run of anything; no browser.

### I.1 The merge -- six conflicts, the six the dry-run predicted

| path | resolution |
|---|---|
| `_audit/_census/profile.md`, `_audit/_census/network.md` | ROW BY ROW, three-way, from the index stages. `master` changed 105 and 95 rows since the base, the lane 34 and 2, and no row was changed by both -- so the result is `master`'s file with the lane's 36 rows substituted, and every non-row line and every row order is `master`'s. The resolver refused on any collision, any lane change outside a row, or any result differing from `master` outside the lane's rows; none occurred. |
| `_audit/INSTRUMENTS.md` | `master`'s file, then the lane's section 70 after `master`'s 66 and 67 -- the lane's change was a pure append. Six places where `master`'s own section numbers do not ascend (16 then 14, and five more between 38 and 47) predate the lane and were left alone. |
| `_audit/INDEX.md`, `_audit/RULINGS.md`, `_audit/_census/blocker-map.tsv` | `master`'s copies, then regenerated by their own generators after every resolved path was staged; two sweeps, the second changing nothing. The same two sweeps were run after every later commit that touched a document or a census cell. |

Every other path merged cleanly, `linkedin_server/writes.py` and `server.py` among them.

### I.2 Condition 1: THE GATE DID NOT REFUSE WHERE THE ORDER SAID IT DID -- it does now

The order described the save gate as already refusing when notify-network is not confirmed. On disk it
did not. Where the edit dialog drew no notify control, the gate PRESSED Save and only the receipt's
words said "NOT DRAWN" or "NOT CONFIRMED" -- leaving condition 1 of `SELF-PROFILE-EDITS-NOT-OUTWARD` to
be judged after the press, which is the wrong side of it. This lane's own live queue compounded it by
reading "NOT DRAWN with no unnamed switch" as satisfying the condition. The order's operative ask -- a
test showing the gate refuses when neither basis is established -- could only pass with a behaviour
change, so the change was made (it is fail-safe: more refusal, never less) and is reported here.

* **Condition 1 is now established before the press, by one of two routes, or the gate refuses.** A
  notify control named in the dialog, read off (`condition_1: dialog_control_off`); or -- the
  amendment, registered after the live lane merges -- his account-level "Share profile updates with
  your network" setting read OFF before the edit (`account_setting_off`). Neither established:
  `5_condition_1_not_established`, NEEDS-OPERATOR, nothing pressed.
* **The seam, not wired:** one keyword, `account_share_updates`, on `profile_editor.save_gate_verdict`
  and `read_save_gate`, default `None` ("not read"), closed set `profile_editor.ACCOUNT_READINGS`.
  `writes.perform` passes nothing; the call sites say so. Anything but the exact reading `off`
  establishes nothing.
* **ONE QUESTION THE SEAM REFUSES ON RATHER THAN ANSWERS, AND IT DECIDES WHETHER THE AMENDMENT HELPS
  THE INTRO EDITOR AT ALL:** an account-level OFF beside a switch with NO accessible name refuses
  (`6_unnamed_switch_unresolved`). The measured intro editor draws two such switches and no named notify
  control. So, as built, **even with the account-level reader wired, no intro-editor field can be saved
  until capture C1 identifies those two switches or the amendment's text says the account-level reading
  covers them.** That is the conservative reading of "a dialog that draws no notify control"; the
  amendment's author may rule the other way, and the change is one line.
* **Receipts** gain `editor_save_gate.condition_1`, naming what established the condition.
* **Tests** (`tests/test_profile_editor_commit.py`, 36 passed): the happy paths plant the dialog control
  read off -- the only basis the unwired gate accepts; the failing-safe test drives the real preview,
  `consume` and `perform` over a dialog with no notify control and is refused before the press with
  nothing stored; the seam is pinned (keyword-only, default `None`, the closed set) and driven through
  every refusal. **SHOWN FAILING** against the gate as committed before the change (both files swapped in
  from the parent commit and restored byte-identical): 18 failed, the behaviour-level ones asserting
  `proceeded` false on a gate that pressed.

### I.3 The census, on the orchestrator's calls

* **`P G3`** opened `same ruling`, which the census's resolver reads off the nearest substantive row
  above -- `P G1` until this lane's `P G2` note, then `P G2`. It now names the ruling lane R found under
  it: **the upload ban**, the package-wide ban on `set_input_files` the operator opened on 2026-09-04.
  State GAP, exactly as `master` has it; every other word of the cell unchanged. It is no longer a
  pointer.
* **`P A8`, `A11`, `A13`, `A17`, `A19`, `A21`** each record that their COVERED-UNFIRED rested on a
  `linkedin_update_profile_field` that never pressed Save, and that the basis is now the repaired gate --
  condition 1 established before the press, NEEDS-OPERATOR until it is. States unchanged; their release
  markers untouched. **What this means for their live proofs is section I.2's last bullet.**
* **`P I14`** stays BUILT and COVERED-UNFIRED (the orchestrator's call). Its cell names the missing
  tested restore and the two prerequisites to its live fire: a company HE names, and `P I15`'s control
  captured first. See the live queue.
* **The correction guard.** Its triage entry for (profile.md, this record) was rewritten after reading
  all 41 citing sites on the merged tree: 17 have a matched word near, all in the three groups the
  entry already named; the new notes carry none of their own. 13 passed.

### I.4 Every pin, re-derived on the merged tree -- not added as deltas

    census_completion     adjudicated 195   delivered_broad 106   gap 509   gap_write 323
                          unfired 31        b1_standing 11
                          PINNED_B1_ROWS + P I14 (OPERATOR-NAMES-THE-TARGET)
                          (the lane's own deltas were against 434 / 100 / 270 / 150 / 25 / 10;
                           master had re-pinned to 194 / 105 / 510 / 324 / 30 / 10)
    count_census_states   --expect J=92,P=151,M=117,N=149  MATCH at 509
    pointer graph         68 pinned pointers (69 before: P G3 is no longer a pointer);
                          P A27-A29 re-pinned on P A26's new verdict; the selftest's
                          calibration needle named the count, 69 -> 68 with it
    tool surface          52 tools: 38 read, 14 write, 0 unable to act
                          PINNED_TOOL_COUNT 52, PINNED_PARAMETER_COUNT 76 (master's 74 --
                          lane S added five -- plus job_id and confirm_token)
    write registry        SANCTIONED_WRITES 15 actions, PERFORMABLE 14

Sites moved with them, each to the measured value: `tests/test_server_surface.py` (the test renamed
`..._fifty_two_tools`, `len(tools) == 52`, `EXPECTED_TOOLS`, `SANCTIONED_WRITE_TOOLS`, the write-shaped
set, both hand-typed performable lists, the number word `fourteen`); `tests/test_every_tool_is_on_the_
surface.py` (52); `tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py` (the tool, 52, 76);
`tests/test_writes.py` (the sanctioned and performable sets, `_UNMEASURED_REVERSIBILITY`,
`REVERSIBILITY_CLASS` STILL-UNKNOWN, `REVERSIBILITY_MEASURED` False);
`tests/test_preview_state_and_click_state.py` (14 and 14); `tests/test_receipt_names_its_own_action.py`
(14, with the acknowledgement that file asks for); `linkedin_server/server.py`'s docstring (52 / 14 /
15) and its INSTRUMENTS -- the client-facing instructions -- which now name the fourteenth write, say
that until 2026-09-24 `linkedin_update_profile_field` never pressed Save so a success it reported
before that date stored nothing, and say it refuses before the press, NEEDS-OPERATOR, unless
notify-network is confirmed off; `linkedin_server/__init__.py` (fourteen write tools); `README.md`
(the headline, with a line on the Save repair, and the tree diagram).

### I.5 Baselines, regenerated by their own generators

* `tests/reader_leak_baseline.json` -- 131 readers: 75 clean, 40 returns_text, 16 not_driven. Moved:
  the lane's five new readers, all `clean`; and three existing readers `returns_text` -> `clean`
  (`dom:read_follow_control`, `writes:_read_follow_state`, `writes:_verify_after`), as section 7
  predicted.
* `tests/tool_envelope_baseline.json` -- one line added: `linkedin_mark_company_interest`,
  `not_driven:never read the page`.
* **`scripts/ci_shard_timings.json` -- LEFT, NOT HAND-EDITED, as the order says.** On the merged tree
  it prices 157 of 237 live test files against a line of 158, so
  `tests/test_ci_shard.py::test_the_timings_table_still_prices_most_of_the_suite` is RED here and
  stays red until the orchestrator regenerates the table after the merge train.

### I.6 Gates run, and not run

**Commits** -- on the worktree branch; nothing pushed; no attribution line in any message; each listed
by its subject:

* *merge master ff98a7f into lane L7: six conflicts, resolved row by row*
* *lane L7: the save gate refuses unless condition 1 is established; a seam for the amended
  condition, not wired*
* *lane L7 integration: P G3 names its ruling; the six intro rows rest on the repaired gate; P I14's
  restore gap and live-fire prerequisites; census and pointer graph re-pinned on the merged tree*
* *lane L7 integration: the tool surface re-pinned on the merged tree; both baselines regenerated by
  their generators*
* *lane L7 integration: the record -- Integration 2026-09-24, the live queue under the amended
  condition 1, C6 before P I14* (this section), and a last record-only commit carrying the final
  gate's numbers.

**Ran:**

1. **The census instruments, on the merged and edited tree.** `census_completion --check` exit 0 after
   the re-pin; `count_census_states --expect J=92,P=151,M=117,N=149` MATCH at 509;
   `check_write_classes` GREEN, 325 lines; `check_read_addresses` 94 of 94; `ruling_holds` GREEN;
   `pin_census_rows --check` no drift; `classify_writeoff_reasons --check`, `check_exclusion_basis` and
   `check_jobs_directions` exit 0; `measure_pointer_graph --check` PASS on 68.
2. **While building, each red repaired or re-pinned before its commit:** the lane's commit tests, 36
   passed, and the seam's 18-failure demonstration against the gate before it; the pointer-graph guard
   3 passed; `tests/test_ruling_holds.py` 55 passed; the correction and asserted-name guards 24 passed.
   The tool-surface pin files went red on exactly the 17 pins section 7 predicted for them, then on
   three it had not -- the module headline `tests/test_server_surface.py` derives from its constants,
   the package docstring's write count in `linkedin_server/__init__.py`, and the new tool's docstring,
   which the docstring-claim check did not read as saying it writes -- all three repaired, and those
   files 86 passed. The page-string guards, lane G's hardened guards, the reader inventories and the
   tool envelopes: 1007 passed. **Lane G's failing-page guard drives all five of this lane's readers**
   (collected by name), and the navigation-taint guard reads its two new `_verify_after` branches; both
   green.
3. **The impact gate against the master merged** (`scripts/impact_gate.py --against ff98a7f
   --plan-only`, in the background): 31 changed paths, 220 of 237 test files (93%) -- **WIDENED TO THE
   FULL SUITE**, so, by the order, the full suite was NOT run here; CI certifies at the merge.
4. **The order's gate list, instead** -- the gate's own 18 corpus-wide guards, the lane's three test
   files, the tool-surface and census pin files the integration moved, and the page-string and lane G
   guards: 38 files in one run, on the committed tip. **1 failed, 4069 passed, no skips, no errors,
   10 min 30 s.** The one red is
   `tests/test_ci_shard.py::test_the_timings_table_still_prices_most_of_the_suite`, the table the
   order keeps for the orchestrator (I.5). After it, every census instrument in item 1 was re-run at
   the tip with the same results, and the three generators' `--check` pass.
5. **The diff and the documents:** the branch's diff against `ff98a7f` -- 31 files, 3454 added lines --
   is all ASCII and carries no absolute workspace path, user directory or operator name (the byte and
   pattern scans, the pattern's four planted controls each firing); no commit message on the branch
   carries an attribution line; `scripts/check_cited_shas_resolve.py` OK at the tip.

**Not run, and why:**

* **the full suite** -- the impact gate widened to it; the order says CI certifies at the merge.
* **CI on any platform** -- nothing was pushed.
* **any live run of anything** -- no browser, no LinkedIn, no grant outside fixture tests.
* **the shard-timings regeneration** -- the order keeps it for the orchestrator (I.5).
* **`scripts/build_read_map.py`** -- the impact gate again notes its observed read map predates this
  commit; rebuilding it is a whole-suite measurement.
* **a cold re-check of the integration** -- not asked for, and the one cold pass the brief budgets was
  spent at the lane's third commit (I.7 on the type it ran on).

### I.7 What this integration leaves for others

* **The amendment's text** decides whether an account-level OFF covers an unnamed switch (I.2). Until
  it does, the six intro-editor rows and the three NEEDS-CAPTURE intro rows cannot be proven live
  whatever reader is wired. **ANSWERED THE SAME MORNING (I.8):** it does not; the amendment ratifies
  code 6 until a capture identifies the switch.
* **`P I14`'s live fire** waits on a capture of `P I15`'s control that must be taken WITHOUT pressing
  `P I14` -- which needs a posting at an employer he has already signalled by hand, or a listing
  surface; if neither exists, the two prerequisites deadlock and the call is his (live queue, C6).
* **The shard timings table** (I.5).
* **The cold pass of this lane ran on the `implementer` type**, which the orchestrator measured tonight
  running Sonnet 5 despite the operator's Opus pin (relayed, not re-measured here). Its checklist was
  closed and its 21 results are measurements that do not depend on the model; no re-check was run for
  the integration, and any that is wanted goes to a `general-purpose` child.

### I.8 The second merge: master `9b9a4d0` (the re-integration order, 06:03)

Sampled first: the worktree at the lane's integration tip and clean, `master` at `9b9a4d0` -- the live
lane's session 1 and rulings batch 4 on top of `ff98a7f`. `master` did not move again before this
section was written. Everything below was measured on the tree merged with `9b9a4d0`.

**What the order settled.** The gate's refusal before the press, and its refusal beside an unnamed
switch (code 6), are RATIFIED and written into the amendment itself:
`SELF-PROFILE-EDIT-NOTIFY-CONDITION-AMENDED`, in `_audit/2026-09-24-rulings-notify-veto-and-who-which.md`
-- "a switch the dialog draws but cannot NAME is not evidence either way ... until a capture
identifies that switch". I.7's first bullet is therefore answered; `profile_editor.py`'s seam comment
now cites the registered ruling.

**The merge -- fourteen conflicted paths.**

| path | resolution |
|---|---|
| `_audit/_census/profile.md` | ROW BY ROW, three-way. `master` changed 11 rows since the last merge, the lane 41. **Six were changed on both sides** -- `P A8`, `A11`, `A13`, `A17`, `A19`, `A21`: the live lane's dated NOT SAVED paragraph, and this lane's note on the repaired gate. In each, the lane's change was a pure append to the base cell, so the result is **`master`'s cell verbatim, then the lane's note, last**. The resolver refused on any other kind of collision; none occurred. **ONE DIFFERENCE FROM THE ORDER'S WORDING, stated rather than smoothed:** the order listed the layers as master's cell (the RELEASED BY citation), then the NOT SAVED paragraph, then this lane's note. On disk the live lane placed its paragraph at the START of the cell, before the RELEASED BY text, so the three layers read NOT SAVED, RELEASED BY, then this lane's note. The live lane's text was not reordered; all three layers are kept and this lane's note is last. |
| `README.md`, `linkedin_server/server.py`, `linkedin_server/__init__.py`, `tests/test_server_surface.py`, `tests/test_every_tool_is_on_the_surface.py`, `tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py` | every number re-derived off the merged registry, never summed (below); each keeps both branches' history lines |
| `scripts/census_completion.py` | the values measured on the merged tree (below); both branches' history lines kept |
| `scripts/measure_pointer_graph.py`, `tests/test_pointer_graph_guard.py` | the count measured on the merged tree: 66 |
| `tests/reader_leak_baseline.json` | regenerated by its generator (below) |
| `_audit/INDEX.md`, `_audit/RULINGS.md`, `_audit/_census/blocker-map.tsv` | `master`'s copies, regenerated after every resolved path was staged; two sweeps, the second changing nothing |

**Every pin, re-derived on the merged tree:**

    tool surface          53 tools: 39 read, 14 write, 0 unable to act -- measured off
                          mcp.list_tools(); 80 parameters. The two branches had each made a
                          different tool their fifty-second: linkedin_own_item_link (the live
                          lane, a read that presses) and linkedin_mark_company_interest (this
                          lane, a write).
    write registry        SANCTIONED_WRITES 15 actions, PERFORMABLE 14
    census_completion     adjudicated 198, delivered_broad 109, gap 506, unfired 30 -- P I14 the
                          only move against master's pins (197 / 108 / 507 / 29); gap_write 323,
                          b1_standing 11, b1_no_ruling 19 as measured. --check exits 0.
    count_census_states   --expect J=92,P=150,M=116,N=148  MATCH at 506
    pointer graph         66 pinned pointers: master's 67 after the live lane, less P G3. A fresh
                          --pin on the merged tree was byte-identical to the auto-merged pin.

**Baselines, by their generators on the merged tree:** `tests/reader_leak_baseline.json` -- 143 readers
(86 clean, 40 returns_text, 17 not_driven); against `master` it moves only this lane's five readers
(`clean`) and the three existing readers `returns_text` -> `clean` that section I.5 named.
`tests/tool_envelope_baseline.json` -- one line against `master`, `linkedin_mark_company_interest`,
`not_driven:never read the page`.

**The shard timings -- priced the live lane's way, as the order asks.** A junit run of the lane's two
test files ALONE on the merged tree (68 passed, serial, the box shared with other lanes' suites, so
the seconds are high rather than low), turned into per-file seconds by the shipped
`ci_shard.seconds_per_file`: `tests/test_mark_company_interest.py` 66.773 s,
`tests/test_profile_editor_commit.py` 80.442 s. The provenance is appended to `_measured`; `_files`
162 -> 164 and `_total_seconds` 1164.6 -> 1311.8 move by exactly what was added; `_tests` stays the
base run's count, as the live lane left it. The two-thirds line did not move: the table now prices 164
of 242 live test files against a line of 161.33, and `tests/test_ci_shard.py` passes, 131 of 131.

**Gates:**

1. **The census instruments, at the merged tip:** `census_completion --check` exit 0;
   `count_census_states` MATCH at 506; `check_write_classes` GREEN, 325 lines; `check_read_addresses`
   91 of 91; `ruling_holds` GREEN; `pin_census_rows --check` no drift; `measure_pointer_graph --check`
   PASS on 66; `classify_writeoff_reasons --check`, `check_exclusion_basis`, `check_jobs_directions`
   exit 0.
2. **The correction guard's triage entry** for (profile.md, this record) was re-read site by site on
   the merged tree: the same 41 citing sites and the same 17 with a matched word near, in the same
   three groups -- the live lane's NOT SAVED paragraphs add no matched word beside this record's
   citations -- so the entry stands as written.
3. **The impact gate against `9b9a4d0`** (`--plan-only`, in the background): 32 changed paths, 225 of
   242 test files (93%) -- WIDENED TO THE FULL SUITE, so, by the order, the full suite was NOT run here;
   CI certifies at the merge.
4. **The order's gate list, on the committed tip:** the gate's own 18 corpus-wide guards, the lane's
   three test files, lane G's hardened guards and the page-string guards over this lane's modules, the
   tool-surface and census pin files, and `tests/test_ci_shard.py` -- 38 files in one run.
   **4138 passed, 0 failed, no skips, no errors, 16 min 24 s** -- the shard-timings test among them,
   green now that the two files are priced.

**Not run, and why:** the full suite (widened; CI certifies); CI (nothing pushed); anything live;
`scripts/build_read_map.py` (a whole-suite measurement); a cold re-check (not asked for).

**Left for others, from this merge:**

* **The live lane's capture has identified the intro editor's two unnamed switches offline -- 'Open
  Profile' and 'Profile Premium Badge'** (its session-1 record, Entry 5, quoted in the six rows'
  NOT SAVED paragraphs). By the amendment's own words that identification is what lifts the block.
  But this gate classifies by ACCESSIBLE NAME and those two switches have none, so it cannot yet tell
  them from any other unnamed switch: code 6 still refuses the intro editor. **Lifting it is a build**
  -- recognise the two by what the capture measured, pinned against that capture -- and it is the
  last offline step before the six intro rows' live proofs need only the account-level reader.
* **`P B9`** (the Premium badge show/hide) now has its control on record: the 'Profile Premium Badge'
  switch is that capture's second switch. Its cell still says the switch is not on record; the row
  stays NEEDS-CAPTURE until a way exists to aim a switch with no accessible name, which is the same
  build as the bullet above.

## Live queue

Loads counted off the code: `linkedin_profile_editor_values` and `linkedin_profile_editor_fields`
each load `/in/me/` (the self-ownership assertion) and the editor, 2 loads; an intro-editor write's
preview loads `/in/me/`, 1 load, and its confirm loads the editor and then re-renders it for the
verification, 2 loads; `linkedin_mark_company_interest`'s preview loads the posting, 1 load, and its
confirm loads the posting and re-renders it, 2 loads; `linkedin_job_detail` is 1 load. Every write
below runs in a process started with `LINKEDIN_ENABLE_WRITES=1`, one agent driving the browser,
loads spaced 20 s apart, inside the 40-load session budget.

**NOT READY: TWO PREREQUISITES FIRST (the orchestrator's call at the integration, 2026-09-24).** This
row read "Ready now" until then, with the undo left to a first press. The order reverses that: the
undo must exist before the act. Its sequence is therefore (1) he names the company; (2) capture C6
records `P I15`'s control WITHOUT pressing `P I14` (see C6 for the only two routes that allow that);
(3) `P I15` is built offline from C6 and its restore tested, which also gives `P I14` the tested
restore its BUILT bar lacked; (4) this row fires, and `P I15` restores it in the same session.

| row | tool call | field | restore step | before / after reading | target | loads |
|---|---|---|---|---|---|---|
| P I14 | `linkedin_mark_company_interest(job_id=<posting>)`, he reads the block (it names the employer), then the same call with `confirm_token=<token>` within 120 s -- ONLY after prerequisites (1) to (3) | none -- the target is that posting's employer | `P I15`, built from C6, in the same session; until C6 and that build exist this row does not fire | before: the preview's own reading (`not_signalled`) and `linkedin_job_detail(job_id)` `interest_control: true`; after: the receipt's `verification` and `linkedin_job_detail` `interest_control: false`; after the restore: `interest_control: true` again | a posting HE names, at an employer he chooses to signal -- `OPERATOR-NAMES-THE-TARGET` | 3 (+2 for the two `linkedin_job_detail` readings, +the restore's own) |

**Ready once a capture names the control -- no new code for the intro-editor rows.** Each is a
SELF-PRIVATE live proof on the four conditions of the ruling `SELF-PROFILE-EDITS-NOT-OUTWARD`.
**CONDITION 1 IS ENFORCED BY THE GATE SINCE THE INTEGRATION, BEFORE THE PRESS** (Integration, I.2):
it presses only on a notify control in the dialog read off, or -- once the amended condition's
account-level reader is wired -- on that setting read OFF before the edit with no unnamed switch in
the dialog; otherwise it refuses, NEEDS-OPERATOR, and the receipt's `editor_save_gate.condition_1`
names which basis it used. **Until 2026-09-24 this paragraph read "NOT DRAWN with no unnamed switch"
as satisfying condition 1; the order registering the amendment says it does not.** The measured intro
editor draws two unnamed switches and no named notify control, so every row in this table waits on C1
naming those switches, or on the amendment's text covering them. Conditions 2 and 3 are the restore
call and the two readings; condition 4 is met because none of these fields adds an entry. The six
intro-editor rows outside the slice (`P A8`, `A11`, `A13`, `A17`, `A19`, `A21`) wait on the same.

| row | tool call | field | restore step | before / after reading | target | loads |
|---|---|---|---|---|---|---|
| P A14 | `linkedin_update_profile_field(field=<the name C1 records>, value=<a value HE picks>)`, then confirm | postal code, if C1 finds it drawn | the receipt's `restore.to_put_it_back`, previewed and confirmed within the session | `linkedin_profile_editor_values()` before and after; equal | self | 10 |
| P A15 | as A14 | the location display choice (a select, chosen by its own option text) | as A14 | as A14 | self | 10 |
| P A22 | as A14 | the primary-position select | as A14 | as A14 | self | 10 |
| P B9 | a toggle kind in the same family, NOT BUILT -- designed after C1 shows how the switch's row names it | the Premium-icon switch | the same call with the opposite state | the editor values reader, which reads a switch's checked state | self | 10 once built |
| P A26 / A27 / A28 / A29 | an editor spec for the contact-info editor, NOT BUILT -- it needs C2's address and field names; then the same two calls | website / phone / messenger / birthday and its audience | the receipt's restore block, within the session; A29 restores the audience too | the values reader over that editor | self | ~10 each, fixed by C2 |
| P G2 | an editor spec for the default-activity form, NOT BUILT -- it needs C4 | which activity type shows first | the same call with the prior option | the values reader over that form | self | ~10, fixed by C4 |
| P I13 | NOT BUILT -- it needs C5 to say whether the control is a field, a modal or a flow | minimum pay | as the build decides | as the build decides | self | fixed by C5 |

**Not queued, and why.** `P D24`, `H1`: C3 first, and their content is his to name (VISIBLE-TO-OTHERS).
`P I15`: C6 first. Every BLOCKED row -- `A24`, `N14` (operator only), `B7`, `J1`-`J3` (Open to Hiring),
`B8`, `K9` (no badge), `D27` (undo is a delete), `D29` (broadcast), `E6`, `N 114` (nothing drawn; a
person's endorsement), `H2`-`H8`, `H10` (no Service Page), `I16` (no job change), `N 176` (settings
page) -- has no live proof until its blocker lifts, and section 6 names each.

## Capture queue

Every spec below states its presses and why they cannot save. "Shapes only" means names through
`shape.census_shape`, tags, types, counts and route shapes with the member segment substituted --
never a value, never an href, never a person's name.

**C1 -- THE INTRO EDITOR, READ TO ITS LAST CONTROL** (`P A14`, `A15`, `A22`, `B9`; and condition 1 for
every intro-editor live proof, in or out of this slice).
Address `https://www.linkedin.com/in/me/edit/intro/` -- ADMITTED (exact exemption,
`PROFILE-EDITOR-ADDRESSES-ALLOWED`). Take `linkedin_profile_editor_fields()` (2 loads: the
self-ownership read, then the editor) and, on the same page, for each control whose `name_source` is
`none`, the shaped text of its nearest ancestor that carries text OUTSIDE the control's own subtree,
stopping at the dialog; skip any `div[role=textbox]` (its text is his headline -- a value). Report
per control: tag, type, role, checked, required, disabled, and that shaped text; plus
`intro_fields.signature`. PRESSES: none. No field is typed into, no option chosen, no control
clicked, and no scroll is needed (the editor was measured server-rendered and flat from 1.5 s to 20
s on 2026-09-19). Nothing is entered, so nothing exists for any control to commit, and the next
navigation discards the dialog. SETTLES: whether the postal-code, location-display and
primary-position controls are drawn for this account (drawn and named -> the shipped tool acts on
them; not drawn -> each row's candidate state is MEASURED-ABSENT for this account, the census
owner's call); which unnamed switch is the Premium-icon toggle; and whether either unnamed switch is
a notify-network control. LOADS: 2.

**C2 -- THE CONTACT-INFO EDITOR** (`P A26`-`A29`).
Stage 1: `https://www.linkedin.com/in/me/overlay/contact-info/` -- ADMITTED 2026-09-23 (lane L1; the
live lane's `_probe_l1_admitted_reads_live.py` key `contact` already costs this load). Shapes only:
every control in the overlay, and for its edit affordance -- is it an ANCHOR, and to which route
shape (for example `/in/<member>/edit/contact-info/`)? No email, phone, website or birthday may
cross back. PRESSES: none. Stage 2, ONLY if stage 1 shows an anchor: that exact address admitted in
its `/in/me/` spelling by the ruling `PROFILE-EDITOR-ADDRESSES-ALLOWED` (the read boundary's owner's act),
then one navigation and `dom.read_self_owned_editor_fields` over its dialog (anchor `Save`): labels,
tags, types, required, disabled, checked -- including the birthday audience control. No values.
PRESSES: none. If stage 1 shows a BUTTON instead, the capture STOPS: the control measured WIRED AND
UNDECLARED on 2026-09-19 (a click listener, no ARIA relation) is a press whose handler nobody has
named, and that is a decision, not this spec. Nothing is entered in either stage, so nothing can be
saved. LOADS: 1 + 1.

**C3 -- THE OPEN-TO EXPLAINER PAGES** (`P D24`, `H1`).
Addresses `https://www.linkedin.com/in/me/opportunities/volunteering/education/` and
`https://www.linkedin.com/in/me/opportunities/services/education/` -- the `/in/me/` spellings of two ANCHORS on his profile
render (a local capture; the services one also in the tracked
`tests/fixtures/profile_topcard_hydrated.html`).
REFUSED by the read boundary today; prerequisite: both exact addresses admitted, `/in/me/` spelling
only (the read boundary's owner's act, on the orchestrator's delegated call -- a page about his own
profile, read without a press). Then one navigation each, shapes only: controls, tags, `has_href`,
each anchor's route shape, and which controls carry `aria-expanded` / `aria-haspopup`. PRESSES: none.
STOP LINE: the first control that leads further is RECORDED, never pressed -- if an anchor, its route
shape is the next admission; if a button, the capture stops, because the Open-to family's entry is
where the Open To Work editor fires `saveAndFetchNextStep` (recorded 2026-08-24) and no press into it
can be shown not to save. LOADS: 2.

**C4 -- THE DEFAULT-ACTIVITY FORM** (`P G2`).
Address `https://www.linkedin.com/in/me/edit/forms/content-collections-star-pill/new/` -- the `/in/me/`
spelling of the 'Edit default activity' ANCHOR on his profile render (a local capture). REFUSED by `/edit/` today;
prerequisite: that exact address admitted by the ruling `PROFILE-EDITOR-ADDRESSES-ALLOWED`, `/in/me/`
spelling (the read boundary's owner's act). Then one navigation and
`dom.read_self_owned_editor_fields` over its dialog (anchor `Save`): the option controls' names
(LinkedIn's own activity types), which one is checked, and the Save control. PRESSES: none; nothing
chosen, so nothing to commit. LOADS: 1. THE BUILD AFTER IT: `update_profile_field`'s spec is pinned to
the intro editor's url, so a second editor needs its own spec and exemption -- decided when C4 shows
the form.

**C5 -- THE JOB-SEEKER PREFERENCES PAGE** (`P I13`).
Address `https://www.linkedin.com/jobs/preferences?viewType=SEEKING_PREFERENCES` -- an anchor
(role=button) on a local capture of the job-alerts page; `/jobs/preferences` is in
`_audit/_census/completeness-candidates.tsv`. REFUSED today; prerequisite: that one address with its
one query parameter admitted (the jobs and read-boundary owners' act). Then one navigation, shapes
only: the minimum-pay control's name shape, tag, `has_href`, route shape if an anchor,
`aria-expanded` / `aria-haspopup`. PRESSES: none -- whether this page's edit controls share the Open
To Work editor's `saveAndFetchNextStep` is unknown, so the capture stops before any. LOADS: 1.

**C6 -- THE ON LABEL OF "I'M INTERESTED"** (`P I15`) -- **A PREREQUISITE OF `P I14`'S LIVE FIRE SINCE
THE INTEGRATION** (the orchestrator's call: the undo exists before the act). Until 2026-09-24 this
spec said the label would come from `P I14`'s own first press; that is now ruled out, so it must be
captured WITHOUT pressing `P I14` on his account, and only two read-only routes allow it:
(a) **a posting at an employer he has ALREADY signalled by hand in LinkedIn** -- that card draws the
ON-state control, the lane's reader reads it as `unknown` (a section control, no OFF label) and
refuses it, and ONE shape census of the card (the census tool, admitted address) records the control's
name shape -- a LinkedIn UI word, not a person. PRESSES: none. LOADS: 1. It needs him to name such a
posting; (b) **a surface that lists his interest signals**, if one exists -- the job-seeker preferences
page of C5 is the candidate, refused today. **If he has signalled no employer and no listing surface
exists, the two prerequisites deadlock**: nothing can show the ON label without a first press, and
whether to accept a first press with an undo by hand is his call, not this lane's. Once C6 has the
label, `P I15` is an offline build (the label, the section bound already in `company_interest`, the
same grant) and its restore can be tested before `P I14` fires.
