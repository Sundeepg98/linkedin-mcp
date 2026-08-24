# Apply-control census - LinkedIn MCP job-posting captures

Slice: read-only census. No code edits, no git operations, no pytest.
Inputs: 13 captures (9 tracked sanitised fixtures + 4 untracked raw probes).
Method: Python `html.parser` + `re`, whole-file reads (no sampling), no added dependencies.

PRIVACY: every value quoted below comes from a TRACKED, SANITISED fixture (invented
identities: "Ashgrove Systems", "Vantrex Systems", job ids 4600000042 / 4600000117 /
4011223344, requisition `JR9900001`). Values seen only in the raw gitignored probes are
written as SHAPES (`<10-digit job id>`, `<ATS vendor name>`, `<opaque token>`).

---

## 0. Headline verdict

A caller CAN positively identify Easy Apply vs off-site from a loaded, HYDRATED posting
page, using ONE field: the apply anchor's `aria-label`, corroborated by its `href` shape
and `target`. Two disjoint, unambiguous values were observed.

A caller CANNOT do anything after that. **No capture in this repo shows the Easy Apply
flow.** There is no modal, no form, no resume picker, no screening question, no
Submit/Review/Next control anywhere in any of the 13 files. See section 5.

Three traps that will silently produce wrong answers, all evidenced below:

1. The string "Easy Apply" NEVER appears in any aria-label. LinkedIn has renamed the
   control to "LinkedIn Apply" and says so in page copy. A parser keyed on "Easy Apply"
   matches zero controls.
2. `data-view-name="job-apply-button"` exists in 1 of 13 captures. Its ABSENCE carries no
   information - it is absent from a HYDRATED off-site page too.
3. `openSDUIApplyFlow=true` appears verbatim in the pre-hydration payload of an OFF-SITE
   posting, on the same job id. Substring-searching the payload classifies nothing.

---

## 1. Full control inventory

"Apply control" = an element whose `aria-label` names an apply action. Total across all 13
captures: **6**, in 6 distinct captures. Two distinct aria-labels. Two distinct href shapes.

### 1a. Posting pages (7 captures)

| capture | tracked | elements | apply controls | tag | aria-label | data-view-name | href shape | target |
|---|---|---|---|---|---|---|---|---|
| `job_detail.html` | yes | 428 | 1 | `a` | `LinkedIn Apply to this job` | ABSENT | `/jobs/view/4600000042/apply/?openSDUIApplyFlow=true&` | none |
| `job_detail_hydrated.html` | yes | 428 | 1 | `a` | `LinkedIn Apply to this job` | `job-apply-button` | same as above | none |
| `job_detail_shell.html` | yes | 117 | 0 | - | - | - | - | - |
| `job_detail_following.html` | yes | 284 | 1 | `a` | `Apply on company website` | ABSENT | `https://www.linkedin.com/safety/go/?url=...` | `_blank` |
| `job_detail_following_hydrated.html` | yes | 722 | 1 | `a` | `Apply on company website` | ABSENT | same wrapper | `_blank` |
| `_probe-job-followed-company-hyd.html` | NO | 2090 | 1 | `a` | `Apply on company website` | ABSENT | same wrapper | `_blank` |
| `_probe-job-followed-company-pre.html` | NO | - | 1 | (payload) | `Apply on company website` | - | same wrapper | - |

Both posting-page fixture pairs also carry a non-apply anchor that matches an apply-shaped
token and MUST NOT be mistaken for a control:

- `a href="https://www.linkedin.com/job-apply-resources/?jobPostingId=4600000042"`,
  text `Tailor my resume`, no aria-label. Present in the Easy-Apply pair and (with job id
  4600000117) in `job_detail_following_hydrated.html`. It is a marketing link.
- `div id="JobDetails_ResumeReview_<job id>"` with an identical `componentkey`, heading
  `Put your best foot forward with your application`. A resume-services upsell card.
  In the raw off-site probe this heading is itself an `aria-label`, so an aria-label
  regex on `/appl/i` picks it up. It is not a control.

The apply anchor also carries `componentkey` (a UUID). In the fixtures:
`d2efe31e-251b-49c4-9f72-26ef53e5078e` (Easy Apply) and
`22d78537-223b-4d23-a47c-29ede2a6cebf` (off-site). The off-site value is byte-identical
between the raw pre capture (3 occurrences) and the raw hyd capture (1 occurrence) of the
same page load, but differs between the two postings. There is NO evidence it is stable
across reloads - treat it as per-render and do not select on it.

### 1b. The shell is empty, and that is a distinct finding

`job_detail_shell.html`: 117 elements, **0** apply-shaped elements, 0 occurrences of
`Apply`, `apply`, `safety/go`, or `openSDUIApplyFlow`. It does carry 16 `data-view-name`
attributes - all 13 distinct values are global footer links (`global-footer-about`,
`compact-footer-privacy`, ...). So the shell has the attribute mechanism but no job
content. "Absent from the shell" here means the posting had not rendered at all, NOT that
the posting has no apply control.

### 1c. Search-results pages (3 captures)

**Zero apply CONTROLS.** No anchor or button with an apply aria-label; no `safety/go`; no
`openSDUIApplyFlow`. What exists instead is a non-interactive BADGE in the card footer:

```html
<li class="... job-card-container__footer-item inline-flex align-items-center">
  <svg role="none" aria-hidden="true" class="job-card-list__icon" width="16" height="16"
       data-test-icon="linkedin-bug-color-small"></svg>
  <span dir="ltr"><!---->Apply<!----></span>
</li>
```

| capture | job anchors `/jobs/view/<id>/` | badge count | badge = LinkedIn-bug icon + "Apply" |
|---|---|---|---|
| `jobs_search.html` (pre-hydration) | 7 | 0 | - |
| `jobs_search_hydrated.html` | 7 | 5 | yes, 5 icons / 5 texts, 1:1 |
| `jobs_search_salary.html` | 7 | 3 | yes, 3 icons / 3 texts, 1:1 |

The badge is DIFFERENTIAL, not decoration: 5 of 7 rows carry it in one fixture, 3 of 7 in
the other. `data-test-icon="linkedin-bug-color-small"` occurs 8 times total across the
three fixtures and 0 times in the other 10 captures.

### 1d. Tracker pages (3 captures)

**Zero apply controls, zero apply badges.**

`jobs_tracker_row.html` (tracked): 193 elements. Complete control list -
`button aria-label="Back"`, `a href=".../jobs-tracker/?stage=draft"` text `Delete`,
`button aria-label="Overflow menu"` (x2), `a` text `Add note` (x2),
`button` text `Yes` / `No` (x2 each, the "Discard draft application and remove this job?"
confirm), and 2 anchors to `https://www.linkedin.com/jobs/view/4011223344/` carrying the
row title. The row's status line reads `No longer accepting applications`.
Tab labels are `Applied - 0`. This is the DRAFT stage with an empty Applied tab.

Raw `_probe-tracker-applied-hyd.html`: 455 elements, tabs `Saved - 0`, `Applied - 0`,
`Archived`, and **0** occurrences of `/jobs/view/`. No rows at all.

---

## 2. The discriminator

### 2a. The two observed value sets

| field | Easy Apply / "LinkedIn Apply" | Off-site |
|---|---|---|
| tag | `a` | `a` |
| `aria-label` | `LinkedIn Apply to this job` | `Apply on company website` |
| visible text | `Apply` | `Apply` |
| `href` | `https://www.linkedin.com/jobs/view/<10-digit job id>/apply/?openSDUIApplyFlow=true&<tracking>` | `https://www.linkedin.com/safety/go/?url=<pct-encoded>&urlhash=<4 chars>&mt=<opaque token>&isSdui=true` |
| `target` | absent | `_blank` |
| `data-view-name` | `job-apply-button` in 1 of 2 captures | absent in all 3 captures |
| payload `applyMethod` | not observed | `1` |

Visible text is `Apply` in BOTH cases and is therefore worthless as a discriminator.

### 2b. Robustness ranking (most to least)

1. **`aria-label` (STRONGEST).** Two disjoint values, present in 6 of 6 controls, present in
   BOTH the pre-hydration and hydrated member of every pair, and present in the raw
   payload as well as the DOM. It is the only field that is 100 percent available and
   100 percent unambiguous across every capture that has a control.
2. **`href` shape (STRONG, as corroboration).** Also present in 6 of 6. Weaker than
   aria-label only because `safety/go` is a GENERIC outbound-link wrapper, not an apply
   marker - see 2c(a).
3. **`target` (MODERATE).** `_blank` on all 4 off-site controls, absent on both Easy-Apply
   controls. Only 6 observations; cheap to include, do not rely on alone.
4. **anchor-vs-button (USELESS).** Both are `a`. Zero apply `button` elements exist in any
   capture.
5. **`data-view-name` (USELESS, actively misleading).** `job-apply-button` occurs once, in
   `job_detail_hydrated.html` only. The attribute is emitted in only 2 of 9 fixtures at
   all, and is entirely absent from `job_detail_following_hydrated.html` and from the
   2090-element raw hydrated off-site capture. Its absence does not mean "not Easy Apply";
   it usually means "this capture's renderer did not emit the attribute".
6. **`componentkey` (USELESS as a selector).** Per-render UUID; differs per posting.

### 2c. Combinations that MUST be classified `unknown`

- **(a) `safety/go` href with no aria-label.** `safety/go` wraps ANY outbound link.
  `job_detail_following_hydrated.html` contains 2 `safety/go` anchors: 1 is the apply
  control, 1 is the `Candidate Application Notice` fraud-disclaimer link to the employer's
  terms page. Same wrapper, same `target="_blank"`, no aria-label. Href shape alone
  produces a false positive here.
- **(b) Any classification derived from a pre-hydration payload substring.** The off-site
  posting's `_pre` payload contains 3 `openSDUIApplyFlow=true` URLs bearing THAT SAME job
  id. See section 5b. Payload substring search must never classify.
- **(c) `data-view-name` present or absent.** Carries no information either way.
- **(d) Visible text `Apply` with no aria-label.** Identical on both branches, and also the
  label of unrelated filter buttons inside bundled JS (9 such hits in one raw capture).
- **(e) A capture with zero apply controls.** `job_detail_shell.html` has none because
  nothing rendered. This is `unknown`, never "no apply available".
- **(f) A `job-apply-resources` href.** Marketing, not a control.

### 2d. Recommended positive-identification rule

Require ALL of a branch; anything else is `unknown`.

```
EASY_APPLY  <=  tag == 'a'
            AND aria-label == 'LinkedIn Apply to this job'
            AND href matches ^https://www\.linkedin\.com/jobs/view/(\d+)/apply/\?openSDUIApplyFlow=true
            AND captured group (1) == the posting's own job id
            AND 'target' attribute absent

OFFSITE     <=  tag == 'a'
            AND aria-label == 'Apply on company website'
            AND href starts with 'https://www.linkedin.com/safety/go/?'
            AND target == '_blank'
            AND the 'url' query param decodes to an absolute http(s) URL
                whose host is not a linkedin.com host
```

Cross-check the job id. It is the one guard against a stale or recycled DOM node.

---

## 3. Anchor or button?

**Anchor, in all 6 observed controls. Zero apply buttons exist in any capture.**

Easy Apply href TEMPLATE (from `job_detail.html`, invented id):

```
https://www.linkedin.com/jobs/view/4600000042/apply/?openSDUIApplyFlow=true&
```

Shape: `https://www.linkedin.com/jobs/view/<10-digit job id>/apply/?openSDUIApplyFlow=true&<tracking param>`

The trailing bare `&` is a sanitisation scar: a parameter's name and value were blanked.
The same URL family in a raw payload carries `&trackingId=<opaque base64 token>` in that
position. In the HTML SOURCE the ampersand is entity-encoded (`...true&amp;"`), so any
regex run over raw file text - rather than over a parsed attribute - must unescape first.

**Following either href is a NAVIGATION, not a click.** Both are plain `a` elements with a
real `href`; no `role="button"`, no `type`, no form. Implications:

- The off-site anchor is unambiguously navigation: `target="_blank"`, and the destination
  is fully recoverable by string parsing (section 4). A caller never needs to click it.
- The Easy-Apply anchor is ALSO navigation as far as the DOM shows: it is a same-tab link
  to a `/jobs/view/<id>/apply/` URL. But navigating there produces a page this repo has
  never captured. The raw payload shows the equivalent action modelled as
  `proto.sdui.actions.core.Navigate` -> `NavigateToUrl` with `openInNewTab: false` and
  `interop: true`. So "clicking Apply" is a route change, and everything that follows the
  route change is unobserved.

---

## 4. The off-site interstitial, decoded

### 4a. Parameter names and encoding

Live wire shape, 4 params in this order:
`url`, `urlhash`, `mt`, `isSdui`

Measured in the raw hydrated probe:

| param | length | character class | role |
|---|---|---|---|
| `url` | 218 | percent-encoded | the ATS destination |
| `urlhash` | 4 | `[A-Za-z0-9_-]` | short integrity/routing hash |
| `mt` | 91 | `[A-Za-z0-9_-]` | opaque tracking token |
| `isSdui` | 4 | literal `true` | renderer flag |

Encoding is standard percent-encoding, but AGGRESSIVE: `:` -> `%3A`, `/` -> `%2F`,
`?` -> `%3F`, `=` -> `%3D`, and notably **`.` -> `%2E`**. A host-extracting regex written
against a literal dot will fail. Use a real percent-decoder.

The HTML source entity-encodes the separators (`&amp;`), in both the raw capture and the
tracked fixture. Parse the attribute, or unescape before splitting.

### 4b. The sanitisation scar (matters for anyone writing tests)

The tracked fixture BLANKED `urlhash` and `mt` including their names, leaving three
consecutive ampersands:

```
...%3Fsource%3DLinkedIn&&&isSdui=true
```

Splitting that on `&` yields 4 segments, 2 of them empty. A parser that requires `urlhash`
to be present will pass against live LinkedIn and FAIL against this repo's fixture. A
parser that uses `parse_qsl(q, keep_blank_values=True)` handles both: it simply drops the
empty segments and returns `[('url', ...), ('isSdui', 'true')]`.

### 4c. Worked decode, sanitised fixture values only

Input, verbatim from `tests/fixtures/job_detail_following.html`:

```
https://www.linkedin.com/safety/go/?url=https%3A%2F%2Fvantrex-systems%2Ewd1%2Emyworkdayjobs%2Ecom%2FVantrexSystemsCareers%2Fjob%2FRiverton---North-Gateway-campus%2FSettlement-Platform-Analyst---Card-Rails--Terminals---Digital-Wallets_JR9900001%3Fsource%3DLinkedIn&&&isSdui=true
```

Step 1 - split query on `&`:

```
['url=https%3A%2F%2Fvantrex-systems%2Ewd1%2E...%3Fsource%3DLinkedIn', '', '', 'isSdui=true']
```

Step 2 - `parse_qsl(..., keep_blank_values=True)` -> `url`, `isSdui`.

Step 3 - percent-decode `url`:

```
https://vantrex-systems.wd1.myworkdayjobs.com/VantrexSystemsCareers/job/Riverton---North-Gateway-campus/Settlement-Platform-Analyst---Card-Rails--Terminals---Digital-Wallets_JR9900001?source=LinkedIn
```

**The destination is fully recoverable by pure string parsing with NO network request.**
No redirect needs to be followed; `safety/go` is a click-through wrapper whose payload is
the destination itself. The decoded value additionally yields the ATS vendor family
(here a `myworkdayjobs.com` host) and the requisition id (`JR9900001`).

Corroborating field in the raw pre-hydration payload, same posting:
`"applicantTrackingSystemName":"<ATS vendor name>"`, `"applyMethod":1`, alongside a
`companyApplyUrl`-style absolute ATS link. `applyMethod` is observed EXACTLY ONCE, with
EXACTLY ONE value (`1`, on the off-site posting). No Easy-Apply posting's payload was
captured, so the field is UNCALIBRATED: we do not know what value Easy Apply carries and
must not assume `applyMethod != 1` means Easy Apply.

---

## 5. What is NOT in any capture

**The Easy Apply flow is UNOBSERVED. No capture in this repo shows anything that appears
after the apply control is activated.** Stated plainly and without softening: this repo
contains zero evidence of what a submit would have to drive.

### 5a. The measurement

Across all 13 captures, counted with a parser (not a grep):

| surface | count across all 13 |
|---|---|
| `<form>` elements | **0** |
| `<textarea>` | **0** |
| `<input type="file">` (resume upload) | **0** |
| `role="dialog"` / `role="alertdialog"` | **0** |
| `aria-modal` | **0** |
| `artdeco-modal` | **0** |
| `jobs-easy-apply` / `easy-apply` class hooks | **0** |
| literal `Submit application` | **0** |
| literal `Review your application` | **0** |
| `Upload resume` / `Choose resume` / `Add a resume` | **0** |
| `screening question` | **0** |
| a `Next` / `Review` / `Submit` control element | **0** |
| a rendered `openSDUIApplyFlow` page | **0** |

Every `<input>` that exists is unrelated: one `role="switch"` checkbox per posting page (a
toggle), 12-14 checkboxes on tracker pages (tab/filter controls), and one `type="text"`
with placeholder `I'm looking for...` (the global nav search box). One `<select>`: a footer
language picker.

### 5b. The near-miss that is NOT evidence of the flow

`_probe-job-followed-company-pre.html` DOES contain apply-flow vocabulary. It is all
route-registry and state-machine metadata, not rendered content, and it belongs to an
OFF-SITE posting:

- Screen registrations (`screenHash` / `screenId`), each with `presentationStyle:
  PresentationStyle_MODAL`, a `pageKey`, and `url: ""`:
  `jobs.ApplyInterceptModal#4e38fb36` (pageKey `job_match_friction`),
  `jobs.PreApplySafetyTipsModal#3aa65c2e` (pageKey `pre_apply_safety_tips_modal`),
  `jobs.OffsitePostApplyModal#5db0579` (pageKey `postapply_next_best_action`),
  `jobs.ShareYourProfileModal#3dc66eec` and `#d987a357`
  (pageKey `flagship3_job_details_apply_starters_modal`),
  `jobs.PreferencesAndSkillsModal#d7ea31ae`.
  These are `NavigateToScreen` ACTION DESCRIPTORS - "if clicked, go to screen X". Not one
  of them has a rendered body, a field, or a submit control in this capture. None of them
  is an Easy Apply form screen.
- State-machine string values shipped for the posting:
  `OnsiteApplying`, `OffsiteApplyClicked`, `OffsiteDidNotApply`, `Applied`, `Saved`,
  `Unsaved`, `Viewed`, plus a `JobDetailsPage_ClosedState_<10-digit job id>` binding.
- SDUI request ids: `com.linkedin.sdui.requests.jobSeeker.confirmOffsiteApply` (payload
  `{jobId, updateStateToApplied: true}`) and
  `...jobseeker.opportunityTrackerOffsiteClickedApplyRequest`.
- Tracking breadcrumb type `JOB_APPLY_CLICK`.

**The trap.** All 3 `openSDUIApplyFlow=true` URLs in this file sit on the `"OnsiteApplying"`
state variant, whose button text is `"Continue"`, and they bear the SAME single job id as
the off-site `confirmOffsiteApply` payload and the `jdpApplyState_<id>` key. Verified:
the file contains exactly 1 distinct `/jobs/view/<id>/` id, and the id in the
`openSDUIApplyFlow` URLs, the id in `confirmOffsiteApply`, and the `jdpApplyState_` key id
are all equal. LinkedIn ships the FULL apply state machine as a template on every posting
regardless of the posting's actual apply method. Substring-searching a payload for
`openSDUIApplyFlow` would classify this off-site posting as Easy Apply.

Note also: `"Applied"` appears as a state-variant NAME in this payload for a posting the
operator has not applied to. Finding the string `Applied` in a payload proves nothing.

### 5c. What a capture would have to contain before a submit could be attempted

None of the following is currently held anywhere in this repo:

1. The page or modal rendered AFTER navigating to
   `/jobs/view/<id>/apply/?openSDUIApplyFlow=true` - captured both pre- and post-hydration.
2. A form root: some container element that actually groups the fields (there are zero
   `<form>` elements today, so its real selector is unknown and must not be guessed).
3. The resume selection control - whether it is `input[type=file]`, a radio list of stored
   resumes, or an SDUI component - plus the labels of the operator's existing resumes.
4. The contact-info step: which fields are prefilled, which are required, their names.
5. Screening questions: their input kinds (radio / select / free text / numeric), their
   required-ness, and how validation failure is surfaced.
6. The multi-step control set - the exact `Next` / `Review` / `Back` / `Submit application`
   elements, their tags, their aria-labels, and how "final step" is distinguished from an
   intermediate step. Submitting from the wrong step is the obvious catastrophic failure.
7. The terminal confirmation state, so success can be positively asserted rather than
   inferred from absence of error.
8. The interstitials that can pre-empt the flow, all named but never rendered here:
   `ApplyInterceptModal`, `PreApplySafetyTipsModal`, `ShareYourProfileModal`,
   `PreferencesAndSkillsModal`. Any of these can appear between the click and the form.
9. The already-applied refusal state (section 6), which is also unobserved.

Until at least items 1, 2, 6 and 9 exist as captures, an apply implementation would be
written against guessed selectors, and its first real execution would be its first test -
against an irreversible action.

---

## 6. The already-applied state

**No capture shows a posting the operator has already applied to.**

- `_probe-tracker-applied-hyd.html` (the applied tracker, hydrated): tabs read
  `Saved - 0`, `Applied - 0`, `Archived`. **0** occurrences of `/jobs/view/`. No rows.
- `_probe-tracker-applied-pre.html` (same page, pre-hydration, 1.3 MB): also **0**
  occurrences of `/jobs/view/`. Its 9 `Apply` hits were each inspected in context and are
  all bundled i18n strings and SDUI component prop templates - e.g. a media-editor
  `"media_editor_apply":"Apply"` string and repeated
  `buttonProps {... "text":["Apply"] ...}` filter-button templates. None is a job apply
  control. (Methodological note for the wave: token-counting `Apply` on a pre-hydration
  capture measures the JS bundle, not the page.)
- `jobs_tracker_row.html` (tracked): the Applied tab reads `Applied - 0`; the single row
  shown belongs to the DRAFT stage (`?stage=draft`) and its status line is
  `No longer accepting applications` - a CLOSED posting, which is a different condition
  from an applied one.
- Both posting pages show a live, enabled apply control.

Consequence for the wave: **the state an apply action must refuse to act from has never
been observed.** We do not know what the control's `aria-label` or text reads once
applied, nor whether it becomes a disabled `button`, nor whether it disappears. The
payload does expose the vocabulary - a state named `Applied`, and a
`JobDetailsPage_ClosedState_<10-digit job id>` boolean binding that drives an
`isDisabledExpression` - so a disabled rendering demonstrably exists, but this repo holds
no capture of it. A refusal guard cannot be written from these captures, only from a new
capture of an already-applied posting.

---

## 7. Search-result rows and tracker rows

### 7a. Search rows: a PARTIAL yes, unconfirmed

Search rows do carry a signal, but it is not the posting-page signal and its meaning is
inferred, not observed:

- The signal is the footer badge of section 1c: an `svg` with
  `data-test-icon="linkedin-bug-color-small"` (the LinkedIn logo mark) followed by
  `<span>Apply</span>`, inside `li.job-card-container__footer-item`.
- It is differential - 5 of 7 rows, then 3 of 7 rows - so it marks a subset, exactly as an
  Easy-Apply badge would.
- **It is NOT confirmed.** This repo holds no posting-page capture for ANY of the 14 job
  ids that appear in the three search fixtures, so the correspondence "badge present <=>
  posting page shows `LinkedIn Apply to this job`" is UNVERIFIED. It is a strong
  hypothesis, not a measurement.
- Rows WITHOUT the badge cannot be called off-site. Absence is not evidence; a badge can
  be missing for layout or truncation reasons.
- The badge is hydration-dependent: `jobs_search.html` has the same 7 job anchors and
  **0** badges.

So: a caller could triage a search page into "probably LinkedIn Apply" (badge present) and
"undetermined" (badge absent) WITHOUT loading each posting - but only after the badge's
meaning is confirmed by capturing one badged and one unbadged posting page and comparing
their apply anchors. That capture pair does not exist yet and is cheap to obtain.

Structural caveat: the search fixtures and the posting fixtures come from **two different
rendering stacks**. Search rows are Ember/artdeco (`job-card-container__footer-item`,
`data-test-icon`, `artdeco-*`); posting pages are SDUI with hashed class names and carry
**zero** `data-test-icon` attributes. A selector strategy built for one does not transfer
to the other.

### 7b. Tracker rows: no

Tracker rows carry NO Easy-Apply-vs-off-site signal at all. Their posting link is a bare
`https://www.linkedin.com/jobs/view/<id>/` with no apply parameters, no badge, no icon and
no apply aria-label. The only status text observed is `No longer accepting applications`.
Triage from the tracker is impossible; the posting must be loaded.

---

## 8. Counts

| quantity | count |
|---|---|
| captures examined | 13 (9 tracked fixtures, 4 raw untracked) |
| posting-page captures | 7 (5 tracked, 2 raw) |
| search-results captures | 3 (all tracked) |
| tracker captures | 3 (1 tracked, 2 raw) |
| apply CONTROLS found (by apply aria-label) | 6 |
| captures containing an apply control | 6 of 13 |
| distinct apply-control aria-labels | 2 |
| - `LinkedIn Apply to this job` | 2 occurrences, in 2 captures |
| - `Apply on company website` | 4 occurrences, in 4 captures |
| distinct apply href shapes | 2 |
| - `/jobs/view/<id>/apply/?openSDUIApplyFlow=true...` | 2 |
| - `safety/go/?url=...` wrapper | 4 |
| apply controls that are `<a>` | 6 of 6 |
| apply controls that are `<button>` | 0 |
| apply controls with `target="_blank"` | 4 (all off-site) |
| occurrences of `data-view-name="job-apply-button"` | 1, in 1 of 13 captures |
| captures emitting ANY `data-view-name` | 2 of 9 fixtures (15 and 16 attributes) |
| occurrences of the literal string "Easy Apply" in any aria-label | **0** |
| `safety/go` anchors that are NOT apply controls | 1 (T&C link, `job_detail_following_hydrated.html`) |
| LinkedIn-bug apply badges in search rows | 8 total (5 + 3 + 0) |
| search rows carrying the badge | 5 of 7, then 3 of 7, then 0 of 7 |
| `<form>` elements, all captures | **0** |
| `<textarea>`, all captures | **0** |
| `input[type=file]`, all captures | **0** |
| `role="dialog"` / `aria-modal`, all captures | **0** |
| apply-flow modal SCREEN REGISTRATIONS in one raw payload | 6 (0 rendered) |
| distinct job ids in `_probe-job-followed-company-pre.html` | 1 |
| `openSDUIApplyFlow` URLs in that OFF-SITE payload | 3, all bearing that same job id |
| observed values of payload `applyMethod` | 1 distinct value (`1`), 1 posting, uncalibrated |
| captures showing an already-applied posting | **0** |

---

## 9. Anomalies and escalations

1. **Two rendering stacks in one repo** (section 7a). Not a contradiction, but it means
   "the apply selector" is really two selectors, and no fixture ties them together.
2. **`data-view-name` is unreliable** and the only attribute difference between
   `job_detail.html` and `job_detail_hydrated.html` is that attribute on the apply anchor
   (both files have 428 elements and identical href/aria-label/componentkey). If any
   existing parser or test keys on it to tell hydrated from pre-hydrated, it is keying on
   a renderer accident.
3. **The sanitiser's `&&&` and trailing `&` scars** (sections 3, 4b) make the tracked
   fixtures NOT byte-faithful to live URLs. Tests asserting exact hrefs will encode the
   scar; tests requiring `urlhash` / `trackingId` will pass live and fail on fixtures.
4. **`applyMethod` is uncalibrated** - one value, one posting, off-site only.
5. **The page copy confirms a product rename**, which is why "Easy Apply" matches nothing:
   `job_detail.html` carries the notice "Easy Apply is now LinkedIn Apply. Same
   experience, with a name that reflects LinkedIn's focus on quality applications." In the
   file the apostrophe is the numeric entity `&#8217;`, decoding to U+2019 - so a text
   match on that sentence must use the correct character, and a match on file bytes must
   use the entity.
6. **Tooling note, not a repo issue:** the shared session scratchpad file
   `.../scratchpad/census.py` was overwritten by another agent mid-run and its output
   leaked into one of this slice's command results. All work was redone under a
   slice-private directory (`.../scratchpad/applycensus_slice/ac.py`) and re-verified.
   No file in the repository was written by this slice other than this deliverable.
