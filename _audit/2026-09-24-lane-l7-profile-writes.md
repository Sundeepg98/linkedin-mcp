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

## 7. THE PINS THIS LANE MOVES -- NOT RE-PINNED HERE, AS THE BRIEF ORDERS

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
| `tests/test_the_other_two_count_claims_are_pinned_too.py` (headline, module listing) | `README.md`: "Fifty-two tools ship. Thirty-eight read. Fourteen write." and "the fifty-two tools"; the module listing gains `profile_editor.py` and `company_interest.py` |
| `tests/test_prose_that_makes_a_claim.py::test_the_server_docstring_numbers_are_derived`, `::test_the_server_docstring_accounts_for_the_action_that_has_no_tool` | `server.py`'s module docstring: fifty-two tools, fourteen of which write, fifteen sanctioned (the fifteenth being `set_open_to_work`, the one with no tool) |
| `tests/test_tool_envelopes_emit_no_page_string.py::test_the_driven_set_has_not_silently_shrunk` | regenerate `tests/tool_envelope_baseline.json` (`python -m tests.test_tool_envelopes_emit_no_page_string --write-baseline`); the new tool is expected `not_driven:never read the page`, as every write's is |
| `tests/test_writes.py::test_what_ships_is_narrower_than_what_is_sanctioned` | add `mark_company_interest` to both set literals |
| `tests/test_writes.py::test_the_gate_prints_every_measured_verdict_with_its_evidence`, `::test_every_verdict_is_pinned_to_ITS_ACTION_not_to_the_set_of_verdicts` | `_UNMEASURED_REVERSIBILITY` gains it; `REVERSIBILITY_CLASS[...] = "STILL-UNKNOWN"`; `REVERSIBILITY_MEASURED[...] = False` |
| `tests/test_preview_state_and_click_state.py::test_every_performable_action_is_either_reached_or_declared_unreachable` | `len(PERFORMABLE) == 14`, `len(REACHED) == 14` (the `REACHED` entry itself is in this lane) |
| `tests/test_receipt_names_its_own_action.py::test_the_action_set_is_the_one_this_file_was_measured_against` | 13 -> 14. Its phrase owners need no new entry: the rest of that file passes with the new rows in place, so neither new row prints a phrase another action owns |

**NOT A PIN, AND APPLIED HERE:** `tests/test_preview_state_and_click_state.py`'s `REACHED` gained the
new action (a coverage table, not a count: without it the action would be performable and driven by
nothing in that file), and `tests/test_write_classes.py` gained two plants.

## Live queue

Loads counted off the code: `linkedin_profile_editor_values` and `linkedin_profile_editor_fields`
each load `/in/me/` (the self-ownership assertion) and the editor, 2 loads; an intro-editor write's
preview loads `/in/me/`, 1 load, and its confirm loads the editor and then re-renders it for the
verification, 2 loads; `linkedin_mark_company_interest`'s preview loads the posting, 1 load, and its
confirm loads the posting and re-renders it, 2 loads; `linkedin_job_detail` is 1 load. Every write
below runs in a process started with `LINKEDIN_ENABLE_WRITES=1`, one agent driving the browser,
loads spaced 20 s apart, inside the 40-load session budget.

**Ready now -- one row.**

| row | tool call | field | restore step | before / after reading | target | loads |
|---|---|---|---|---|---|---|
| P I14 | `linkedin_mark_company_interest(job_id=<posting>)`, he reads the block (it names the employer), then the same call with `confirm_token=<token>` within 120 s | none -- the target is that posting's employer | none through this server (`P I15` unbuilt); by hand in LinkedIn if he wants it withdrawn. The receipt's after-press counts and fresh render are the capture `P I15` waits on (C6) | before: the preview's own reading (`not_signalled`) and `linkedin_job_detail(job_id)` `interest_control: true`; after: the receipt's `verification` and `linkedin_job_detail` `interest_control: false` | a posting HE names, at an employer he chooses to signal -- `OPERATOR-NAMES-THE-TARGET` | 3 (+2 for the two `linkedin_job_detail` readings) |

**Ready once a capture names the control -- no new code for the intro-editor rows.** Each is a
SELF-PRIVATE live proof on the four conditions of the ruling `SELF-PROFILE-EDITS-NOT-OUTWARD`: condition 1 is read off the receipt's
`editor_save_gate.notify_network_means` (only `CONFIRMED OFF`, or `NOT DRAWN` with no unnamed switch,
satisfies it -- `NOT CONFIRMED` does not); conditions 2 and 3 are the restore call and the two
readings; condition 4 is met because none of these fields adds an entry.

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

**C6 -- THE ON LABEL OF "I'M INTERESTED"** (`P I15`).
No separate capture: it is produced by `P I14`'s first supervised press, on a posting HE names. The
receipt's `verification.why` carries what the press left in place (OFF controls, section controls,
dialogs open) and the fresh render's reading. Then ONE shape census of that posting's
About-the-company card (the census tool, or `linkedin_job_detail` if its card reading is widened)
records the ON control's name shape -- a LinkedIn UI word, not a person. PRESSES: none beyond I14's
own confirmed one. LOADS: 0 extra (+1 for the census).
