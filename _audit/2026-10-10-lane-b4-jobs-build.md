# Lane B4, 2026-10-10: the jobs rows lane K's ledger marked BUILD

Lane `lb4-jobs-build`, briefed by the orchestrator at 15:18 IST on master
`f93104c` (lane CI section 13). Built OFFLINE in its own worktree; nothing here
loaded LinkedIn. Twelve rows, each `next=BUILD` in lane K's ledger
(`_audit/_census/next-step.tsv`; master's copy did not yet carry K's latest, so
it was read READ ONLY from lane K's worktree, 14:54). Two children worked closed
read slices in their own worktrees (`J 110`, `J 108`) and are reviewed and
merged here; a third child for `J 161` could not be spawned (the session's
concurrent-agent ceiling), so the lead built it.

Rulings cited by id. Two are lane K's 2026-10-10 ledger rulings, registered on
lane K's branch and not yet on master: `THIRD-PARTY-TEXT-AT-RUNTIME` (an
organisation's prose and a post's text are returned at runtime, marked,
sanitised, bounded, never stored) and `APPLY-FLOW-IS-THE-APPLICATION` (opening
Easy Apply is the start of an application; this lane never opens it).

---

## 0. What disk said that the brief did not

1. **THE TRACKER FIXTURE DRAWS NO ARCHIVE CONTROL.** Lane K's inventory counted
   "Archive" and "Add note" on `tests/fixtures/jobs_tracker_row.html`. Measured:
   the only `Archive` text there is the `Archived` TAB label (twice, a
   `label` of the stage radios); the row draws `Add note` (an anchor) and an
   `Overflow menu` button whose menu was never opened. The bulk-action bar
   draws `Delete` only (the draft stage). An `Archive` button IS drawn in the
   bulk-action bar of the SAVED stage -- `Unsave`, `Archive`, `Delete` after
   `0 selected` -- on the main checkout's gitignored raw probe of 2026-08-23
   (`_audit/_probe-tracker-saved-hyd.html`), never in a tracked fixture, and
   the Archived tab's own bar (where an unarchive would be) was never captured.
2. **SESSION 8'S POSTING DRAWS NO HIRING TEAM.** The posting kept at load 17
   draws `People you can reach out to` (`1 school alumni works here`,
   `1 connection works here`), and 0 lines with `hiring team`, `Meet the` or
   `Job poster`. So `J 115`'s read half has no capture yet.
3. **THE ALERT SWITCH CHANGED SHAPE.** August (`job_detail_hydrated.html`): a
   `div[role=switch][aria-checked=false]`. Session 8: an
   `input[role=switch][type=checkbox]` with no `aria-checked`, its state its
   checked property and the word `Off` beside it, inside a toggle container
   holding an empty `label` and a knob -- the component `P B9` met in his
   editor, whose input no click could reach.
4. **THE COMPANY PANEL IS J 124's PAYLOAD.** Session 8's posting draws, under
   `Insights about the company` and the shipped heading
   `Exclusive Job Seeker Insights about <employer>`, `Powered by Bing`,
   `Company focus areas` (a titled focus area and its summary), `Hiring &
   headcount` (an 816-character summary), and `Total employees`,
   `2 year growth`, `Company-wide`, `Median employee tenure:`.
5. **THE `j107.html` "DISMISS" LABELS ARE NOT A JOB'S.** All six
   `aria-label="Dismiss"` on the tracked search capture are the filter
   dropdowns' close buttons (`artdeco-hoverable-content__close-btn`). The
   per-card action buttons are drawn, their labels reduced to `x`.
6. **THE FEEDBACK PAIR IS DRAWN.** On session 8's recommended page (keyed
   skeleton, its own key; candidates were LinkedIn UI strings only): exactly
   one control each labelled `Are you finding what you<U+2019>re looking for? Yes`
   and `... No`, beside `Your feedback helps us improve job recommendations.`
   (the straight-apostrophe spellings: 0).

---

## 1. `J 124` -- the posting's AI company intelligence, read whole as third-party text

**THE ROW'S PAYLOAD IS ON THE POSTING, INSIDE THE PANEL ALREADY RETURNED.**
`linkedin_job_detail` returns `insights.company_insights` off
`dom.read_job_insight_panels`, which finds the panel by the shipped heading
prefix `dom.JOB_COMPANY_PANEL_PREFIX`. On session 8's posting that heading is
the `h2` under `Insights about the company`, and the panel holds the row's
three payloads: `Company focus areas` (strategic priorities), `Hiring &
headcount` (the hiring summary), and `Total employees`, `2 year growth`,
`Company-wide`, `Median employee tenure:` (the headcount).

**MEASURED ON THE RAW CAPTURE, OFFLINE** (a local headless Chromium, every
request aborted; counts and LinkedIn's own words printed, never a line of the
capture's text):

    reader      lines  payload words present                       tenure  marker
    shipped       21   focus areas, hiring, Total employees,       cut     none
                       Company-wide, 2 year growth
    this lane     26   the same five                               kept    untrusted, truncated False

The 816-character hiring summary carries none of the words `open`,
`opening`, `role`, `position` (counted on the raw line, counts only): its
"openings" half is a summary of hiring and headcount, not a list of open
roles -- recorded so the row's word "openings" is not over-read.

**WHAT WAS BUILT** (`b0b236a`):

- `dom.read_job_insight_panels`: the company panel is read POSITIONALLY FIRST
  (`lines_after_heading`, bounded by the panel's own end -- the next heading or
  `Show Premium Insights`), with its own cap `dom.JOB_COMPANY_PANEL_MAX_LINES`
  (40); the structural walk is the fallback. On the August captures the walk
  returned nothing and the positional read was already what ran, so their
  result is unchanged (`tests/test_free_read_panels.py`, 22 passed).
- `linkedin_server/company_panel_text.py` (new): `THIRD-PARTY-TEXT-AT-RUNTIME`
  in code for this panel -- every line through `people_data.sanitise` (the
  package's one sanitiser), cut at `LINE_CAP` (1,000; the longest measured line
  is 816), `truncated` when a line or the run was cut, and
  `people_data.UNTRUSTED_KEY` on the panel. Nothing stored or logged.

**RED FIRST**, on the shipped reader over the tracked skeleton
(`tests/test_job_company_insights_session8.py`):

    >       assert any(line.startswith("Median employee tenure") for line in lines)
    E       assert False
    >       assert company[people_data.UNTRUSTED_KEY] == people_data.UNTRUSTED_NOTE
    E       KeyError: 'untrusted_third_party_text'
    2 failed, 4 deselected

GREEN: the file 6 passed with `tests/test_free_read_panels.py` 22 (28 passed).
The six: the three payloads and the panel's four boundaries; the marker and
`truncated: False`; an over-long line cut to 1,000 with `truncated: True`; a
zero-width space and a right-to-left override removed; a line repeating the
employer shaped to `<company>`; every line its own sanitised form.

**ONE THING THE FIXTURE HAD TO BE TAUGHT, AND IT WAS A FALSE RED FIRST.** The
first red ("Total employees" missing) was an ARTIFACT: `tracked_copy` makes
every keyed text one `x`, so every keyed HEADING equalled every keyed body line,
and a reader bounded by "the next heading" stopped at the first `x` line. No
live page does that -- the raw capture's run reaches the tenure line. The
builder now writes a heading's keyed text as `Example heading`, and the red
above is the one that survives on a faithful fixture.

---

## 2. `J 161` -- the similar-jobs alert, set and unset

**BUILT, READY TO FIRE, NOT FIRED** (`9f77e03`), under
`HIS-OWN-CURATION-NOT-OUTWARD`: `linkedin_set_similar_jobs_alert(job_id)` and
its inverse `linkedin_unset_similar_jobs_alert(job_id)`, in one change, in
server.py's block headed `lane B4`. Both behind `writes_enabled()` and the
single-use, action-bound, target-bound grant; the job id from the argument
only (`PAGE-MAY-VETO-NEVER-SUPPLY`). Named on LinkedIn's own verb, `set`, which
the naming law admits, and `unset` (un + an original verb) -- measured with
`tests/test_writes.py`'s `_verb_is_admissible` before the names were chosen.

- `linkedin_server/job_alert_switch.py` (new): exactly one block whose `h2`
  reads `Set alert for similar jobs`; exactly one `input[role=switch]` in it,
  and on the page, wearing `dom.JOB_ALERT_HEADING_PREFIX`; the state is the
  word beside it (`Off` MEASURED, `On` DERIVED) AND the input's checked
  property, which must agree. The label carries the posting's title, so it is
  matched by prefix INSIDE the page and never read into Python. The August
  `div[role=switch]` shape reads `unknown` (asserted).
- THE AIM: the toggle container -- the switch input's own parent -- because
  the same LinkedIn toggle in his editor drew an input no click could reach
  and a 52 x 32 container that was trial-actionable (`P B9`, session 8). The
  preview and the click each run a TRIAL press on it (Playwright's
  actionability checks, nothing dispatched) and refuse if it fails.
- `writes`: two specs on `/jobs/view/<id>/`, `state_from` `posting_alert_switch`
  (one load, the state read off the page the click acts on), in
  `PERFORMABLE`, `STRICT_PRESS_ACTIONS`, `_TOGGLE_ACTIONS`, `_WHERE_TO_LOOK`,
  `_VERIFIED_FROM`; the anchor label, `observe`, `_live_control` and
  `_verify_after` arms. Verified on a FRESH RENDER of the posting: one control
  carries both states, so the reading is strong both ways. REVERSIBILITY
  `STILL-UNKNOWN` -- the gate refuses a measured class on an unmeasured claim,
  and the On shape is unmeasured; the inverse is built and named in
  `reversible_by`.

**RED FIRST:** with the pair unwired, the test file did not collect --
`WriteAttemptError: 'set_similar_jobs_alert' is not a sanctioned write`.
GREEN: `tests/test_similar_jobs_alert.py` 25 passed -- the session-8 posting
reads `alert_off` and its toggle takes a trial press; the August shape reads
`unknown`; a DERIVED On world reads `alert_on`; four derived worlds refused
(word and property disagree, two switches, a label without the prefix, no
block); set previews from Off and mints, is refused from On; unset mirrors it;
writes off refuses before any load; a grant binds its posting and its verb; a
grant is used once; set verified On, set left Off (`performed: false`), unset
verified Off, a fresh render with no switch `unknown`; the tables name both.

**THE FIXTURE HAD TO CARRY THE POSTING READER'S ANCHORS.** Every posting write
reads the posting's title, employer and description before any gate renders,
and the plain reduction had erased all four anchors (the `<title>`, the
`Company, <employer>.` label, `About the job`, the SDUI component names). The
builder keeps or synthesises exactly those. MEASURED on the raw capture: it
carries NO `data-sdui-component` attribute at all, so
`dom.JOB_DESCRIPTION_SLOT` never attaches on today's markup and every posting
read spends the readiness wait's full bound (10 s) before reading the page in
full. The tests shorten the bound; the reader is unchanged. This is a finding
for every posting tool, not this row's (question 3).

---

## 3. The tracked fixture: `tests/fixtures/live8/posting.html`

Built by `scripts/_build_live8_posting_skeleton.py` from the live lane's
gitignored RAW capture of session 8's load 17, through the session-2 pipeline
imported unchanged (`skeleton_of`, then `tracked_copy`), with six additions
stated in its docstring: seventeen LinkedIn words `FURNITURE` lacks, each
counted in the capture (20 hits, the build refusing on a zero); four
name-carrying values rewritten to their LinkedIn prefixes plus declared
synthetic values (`Example Org`, `Example Job Title`); the AI prose replaced by
invented sentences after its anchors; every number replaced in format; a
heading's keyed text written `Example heading`; the posting reader's anchors
kept. A fixed public key makes it a fixed point (built twice, sha256
`b7363a3a791313f5` both times). The script prints counts only; the identity
gate examined every commit's staged files against 226 spellings, 0 hits.

---

## 5. The rows left GAP, each with its exact reason

    row    the reason, MEASURED unless marked                         next step
    J 53   the tracked fixture draws no Archive control (section 0.1);  CAPTURE: the Archived tab with a
           the bulk bar's Archive is on a gitignored raw probe only,   row, and a saved row selected --
           and the Archived tab, where an unarchive would be, was       inside the act at a tracked job
           never captured: the inverse cannot be built on markup       he names
    J 55   `Add note` is drawn (an anchor on the draft row); the note   CAPTURE: the opened note editor,
           editor it opens -- its field, its Save -- never captured:   at a tracked job he names
           a typed write cannot aim at an unmeasured field
    J 56   `Date posted` is a pill (`div[role=button][aria-expanded=   CAPTURE under CAPTURE-PRESS-UNDER-
           false]`) whose options were never drawn open; the press     PROBE-RULE (a filter panel), then
           gate declares no basis for /jobs-tracker/                    a view_switch entry and a basis
    J 84   all six `Dismiss` labels on j107 are filter close buttons   CAPTURE: one recommendation
           (0.5); the per-card action buttons' labels are reduced to   dismissed, with its undo drawn
           x, and the undo (the inverse) was never captured
    J 115  session 8's posting draws no hiring team (0.2)               CAPTURE: a posting that draws
                                                                        "Meet the hiring team"
    J 31   BUILDABLE NEXT, not reached in the time box: the classic    BUILD on tests/fixtures/live2/
           search's alert toggle is drawn on j107 (`input[role=        j107.html, the J 161 pattern,
           switch][aria-checked=false]` in `jobs-search-create-        plus a closed write-url shape
           alert__artdeco-toggle`), its label reduced to x; the write  over the search query
           needs a closed url shape over a search query from tool
           arguments, which no write has yet
    J 19   BUILDABLE NEXT, not reached: the real jobs-home capture     BUILD a tracked skeleton, then a
           (main checkout `_state/cap-ct-jobsalerts.html`, gitignored)  delete-own-item write under
           draws one `Clear` beside `Recent job searches`; the tracked OUTWARD-CLASSES-BUILT-BEHIND-
           fixture is synthetic, which moves no row. Irreversible: no  GRANTS; fired only when he
           inverse exists to build                                      names it
    J 163  the pair IS drawn (0.6); only a keyed skeleton exists, and  BUILD a tracked skeleton (the
           the act sends feedback that nothing measured can withdraw   two labels restored by key), a
                                                                        one-shot write, no inverse
    J 108  see section 4 (child b4-j108)
    J 110  see section 4 (child b4-j110)

`APPLY-FLOW-IS-THE-APPLICATION` was obeyed by construction: nothing here
presses, opens or reads the Easy Apply flow; the posting fixture keeps the
words `Easy Apply` only as drawn text.

(Sections 4, 6 to 9 follow.)
