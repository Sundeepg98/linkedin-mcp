# The eight refusals, worked -- `445c7a0` .. `0979ed8`

The operator lifted the scope restriction and asked for `out_of_scope_by_design`'s eight entries
listed, built, tested and completed, in a stated order of value. This is what each one turned out to
be. **Two shipped as capability. Three are refused for reasons that are now MEASURED rather than
assumed. One could not be measured at all, because the permission system declined the probe, and it
is recorded as UNMEASURED rather than left looking finished. Two were named as not-to-build and were
not built.**

---

## 1. APPLY -- the identification ships, the submission refuses

**The first question the brief asked -- Easy Apply or off-site ATS, per posting -- is answerable, and
the answer was already sitting in the frozen fixtures.** Two routes, six controls, thirteen captures,
two disjoint accessible names:

| route | control | destination |
|---|---|---|
| `linkedin_apply` | `<a aria-label="LinkedIn Apply to this job">` | `/jobs/view/{id}/apply/?openSDUIApplyFlow=true` |
| `offsite` | `<a target="_blank" aria-label="Apply on company website">` | `linkedin.com/safety/go/?url=<percent-encoded ATS url>` |

**Every apply control in every capture is an ANCHOR, not a button. Zero apply `<button>` elements
exist.** That is the property the whole feature rests on: the destination is legible *before* anything
is activated, so the route can be identified and the third-party site named without touching the
control. `linkedin_job_detail` now reports `apply_path` off the page it already has open, at no extra
load, decoding the outbound wrapper by string alone -- no redirect followed, no third-party host
contacted.

**WHY THE CLASSIFIER DEMANDS A CONJUNCTION.** Each candidate discriminator was measured and each fails
alone. This is the section worth keeping, because the obvious single field looks sufficient in every
case:

- **`data-view-name="job-apply-button"`** is present on **1 of 13** captures and ABSENT from a fully
  hydrated off-site posting. Its absence therefore carries no information whatever. It is not used.
- **The `/safety/go/` href** is a GENERIC outbound wrapper. One capture holds **two** of them and only
  one is the apply control, so href shape alone false-positives on an unrelated external link.
- **The accessible name** is the strongest single field and is still not enough: it is the one thing
  LinkedIn has already changed on this surface. **The string "Easy Apply" appears in ZERO accessible
  names** and twice in prose on the same page -- the page carries LinkedIn's own banner "Easy Apply is
  now LinkedIn Apply." A parser keyed on the name everybody knows the feature by matches nothing, and
  a substring search over the markup would look like it worked.
- **The pre-hydration payload is worse than useless.** An OFF-SITE posting was measured carrying
  `openSDUIApplyFlow=true` on an `"OnsiteApplying"` state variant **for the same job id**. LinkedIn
  ships the whole apply state machine as a per-posting template, so a payload substring search
  classifies nothing. Only the RENDERED control answers. (Measured in a raw gitignored capture; the
  tracked fixtures strip payloads, so **no test in this repo guards that paragraph** and
  `shape.apply_route`'s docstring says so rather than letting it look like the others.)

**THE SUBMISSION IS REFUSED, AND THE THREE REASONS ARE NOT THE SAME KIND.**

1. **The apply FLOW has never been captured.** Across the same thirteen captures: **0 forms, 0
   textareas, 0 `input[type=file]`, 0 `role="dialog"`, 0 Submit/Review/Next controls, 0 rendered apply
   pages.** Nothing in this repo has ever seen what a caller would have to fill in or press. That is
   the `unsave_job` standard applied to the action that deserves it most.
2. **It cannot be undone from here.** Withdrawing is in `PERMANENTLY_FORBIDDEN` and `/withdraw` is on
   the read boundary's forbidden list, so whatever LinkedIn's product permits, an application this
   server sent is one it can never take back.
3. **Half of it is not this server's to do at any capture quality.** The off-site route submits on a
   third party's ATS, on their domain, under their terms.

So `apply_job` is **sanctioned, fully specced, gated -- and registers no tool and holds no
`url_template`**, which is precisely the condition `set_open_to_work` is in and which `mint()` already
refuses at issue. Registering a tool that could only refuse would have moved a name off
`FORBIDDEN_TOOLS` to buy nothing.

**Its reversibility is `STILL-UNKNOWN`, not `IRREVERSIBLE`, and that distinction is deliberate.** The
surface that would settle it is his applied list, and **both captures of `?stage=applied` read a count
of zero with no job rows at all** -- the absence of a withdraw control in an empty list is evidence
about nothing. `irreversible=True` is carried separately, on the certain ground in (2). This makes
`apply_job` the first spec to exercise the renderer's UNMEASURED branch, which was live code with no
live spec behind it and could have been deleted with the suite staying green.

**Not shipped, recorded for whoever wants it:** search-result rows carry a differential badge
(`data-test-icon="linkedin-bug-color-small"` + "Apply", 5/7 then 3/7 rows) that would let a whole
search be triaged without loading each posting. Its meaning is **UNVERIFIED** -- no posting capture
exists for any of the 14 search job ids -- and search rows and posting pages come from **two different
rendering stacks** (Ember/artdeco vs SDUI), so one selector strategy will not cover both.

---

## 2. UNFOLLOW -- shipped, performable

**The anchor was already measured and is the strongest in the package.** `aria-label="Click to stop
following <Page>"`, **80 instances across 5 captures**, both hydration states. LinkedIn writes the
inverse action into the control's own accessible name, which is better evidence than the save control
ever had.

`linkedin_unfollow_company` is registered and performable, addressed by **numeric company id** and
never by name. The row key is stable: 80/80 rows carry exactly one `<li>` per id and exactly one
button in it.

**A SAFETY REQUIREMENT THAT IS NOT THEORETICAL.** `/feed/following/` renders the **identical label
template over PEOPLE** -- 20 rows, `urn:li:member:` urns, zero company links -- and
`dom.FOLLOWED_PAGE_BUTTON` matched all twenty. This server cannot reach that surface (not on the read
allowlist), so nothing was ever at risk. The row is required to carry a `/company/<id>/` link anyway,
because the day the selector meets an unexpected page is too late to add the condition. It
discriminates **80 company rows from 20 member rows with no exceptions in either direction.**

**THE VERIFICATION IS WEAKER THAN THE SAVE PAIR'S AND SAYS SO.** There is exactly one surface listing
followed Pages, so confirmation comes from RELOADING it -- a fresh navigation and a fresh render, which
is materially stronger than reading a button that redrew itself in place and weaker than an independent
surface. To stop a row's mere absence carrying the verdict on a list that is never complete, **the
evidence is LinkedIn's own stated total: the row must be gone AND the count must have dropped by
exactly one.** A row that vanished while the total held is reported `unknown`.

---

## 3. FOLLOW -- the objection was removed and replaced by a measured one

The brief's premise was that building unfollow removes the objection blocking follow. **It removes that
objection and exposes a different one, which the census measured:**

- **The identifier mismatch is total.** Manage-Pages rows carry **0 slugs**; `/jobs/view/` carries **0
  numeric company ids and 0 company urns anywhere, including embedded JSON.** A posting names its
  employer by slug; the unfollow surface addresses rows by numeric id; **no in-page resolution exists**
  on either surface. **A follow cannot be undone by id.**
- **Pagination: 20 of 58 rendered, ZERO show-more or pagination controls in the entire document**, in
  all five captures. About two thirds of the list is unreachable in one page load.

One exception, recorded because it is the shape of a future fix: `/jobs/search/` carries **both** forms
and joins them for one company via a shared logo-artifact digest between an `included[]` record and the
employer card `<img>`. Slug-to-id with no network call -- **on that surface only**, and fragile.

**So `follow_company` stays out of `PERFORMABLE`.** The refusal names the aiming problem, both numbers,
and what would lift it. `reversible_by` still reads "NOT this server" -- and it nearly did not: building
unfollow made it tempting to soften that to "possibly by this server", which would have been a
capability claim resting on a resolution step nobody has. **The guard that caught that is
`test_a_follow_says_plainly_that_this_server_cannot_take_it_back`, and it did the job it was written
for.** It now also pins the two measured numbers, so the reason cannot drift back to a comfortable
sentence.

---

## 4. OPEN TO WORK -- `url_template=None` is correct, for a stronger reason than the comment gave

**Measured: 237 distinct urls + 37 payload path strings across all five profile captures. ZERO reach an
OTW editor, a job-preferences page, or a career-interests page.** The strings `opentowork` and
`open-to-work` occur **0 times anywhere**. It is not url-addressed AT ALL: its screens are addressed by
an internal screen id, and even the sibling screen-navigate on the same card carries `"url": ""`.

**AND THE SPEC WAS CITING THE WRONG CONTROL.** `reversibility_evidence` said the editor "sits on that
card and is present in both frozen renders as `aria-label="Open to"`". **That is false.** The `Open to`
button's menu resolves to exactly three `role="menuitem"` children -- Hiring / Providing services /
Finding volunteer opportunities -- and **none is the audience editor**; the entry LinkedIn would use is
absent precisely BECAUSE the setting is already on. **A capture attempt starting from that control would
have failed invisibly.**

The real entry point is `button[aria-label="Edit"]`, unique on the page, no href, whose activation fires
`saveAndFetchNextStepRequest` with `isEditFlow:true` -- **not a navigation**. It IS pinned in the tracked
sanitised fixtures at both hydration states, so the evidence survives, attached to the right control. The
old sentence is quoted verbatim in the field so the mistake stays legible.

**Consequence for the capture procedure, and why it was not taken:** `Show details` first (a Navigate,
no ServerRequest, safe), then `Edit` -- and that single click is simultaneously the first step that
SHOWS the editor and the first that could CHANGE it. The RPC is literally named `saveAndFetchNextStep`.
Its residue is irreversible in AUDIENCE and a current employer can see it. **No capture of his live profile
was taken. That one needs him watching.**

Also measured, and useful later: a real DOM discriminator for the public badge exists --
`profile-framedphoto` vs `profile-displayphoto` in the img src, plus an `alt` naming it. His topcard is
`displayphoto`, no frame. **The tracked fixtures strip photo urls entirely, so a frame check written
against them cannot fail** -- worth knowing before somebody writes one.

Only **1 of 3** audience states has ever been observed on this account.

---

## 5. MARK NOTIFICATIONS READ -- unbuildable for want of a target

**34 activatable controls across 6 cards (22 buttons, 12 anchors, 0 `role="button"`) and not one changes
read state.** The per-card overflow menu holds **14 items, 3 distinct labels** -- change preferences,
delete notification, show less like this -- and **the dropdown is in the static DOM BEFORE activation**,
so its emptiness is not a lazy-render artefact. That is the load-bearing negative.

**No notification carries an id of any kind.** 0 articles have an `id`, the only `data-*` name is
`data-view-name`, and 2 of 6 cards carry no urn at all. **So there is no target even for a hypothetical
control.** Unread is expressed only as page state: a class, an aria-label, a blue-dot figure and a
visually-hidden span.

The prohibition keeps its original ground and gains two more: no control, no target, and **the read tool
already causes the full effect** -- opening the page clears the badge, so a write could only ever run
after its own consequence had landed.

**One caveat carried rather than buried:** the fixture root is `<main>` and retains no header or filter
strip, and no other capture in the repo holds notifications markup, so a header-level "mark all as read"
is **UNVERIFIED, not disproven**.

---

## 6. READING HIS INBOX -- UNMEASURED, and blocked by the permission system

The brief was right about the asymmetry: `/messaging` is on `_FORBIDDEN_URL_SUBSTRINGS`, and **every
written rationale for that entry is phrased against SENDING.** Nobody has measured whether reading is
possible.

**I could not measure it either.** `scripts/_probe_messaging.py` is written, committed and reviewable.
It was refused by the permission classifier on two attempts -- once via bash, once via PowerShell -- and
**has not been run**. I did not work around the refusal.

The probe is worth reading even unrun, because it measures **two** things and the second is the one the
question usually skips. **LinkedIn's desktop messaging view opens a conversation on arrival, and opening
a conversation marks it read.** If that is what happens, a "read-only" inbox tool destroys unread state
on every call -- the exact objection that keeps `mark_notifications_read` forbidden, arriving through a
tool that calls itself a read. Asking the inbox about itself would be circular, so the probe reads the
messaging badge from `/feed/` (already an allowed surface) BEFORE the load and again AFTER, and treats an
absent badge as INCONCLUSIVE rather than as a clean run.

**The forbidden list is unchanged.** A boundary does not move on an unmeasured claim, and `server_info`
now files this under its own `UNMEASURED` label rather than among the design decisions.

**To take the measurement**, with the profile lock free and no other agent holding a browser:

```
D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\venv\Scripts\python.exe scripts\_probe_messaging.py
```

---

## 7. NOT BUILT, as instructed, and I agree with both

- **Collecting data about other members.** A policy line, not a scoping one. It stays, and it is
  labelled POLICY in `server_info` so it cannot be mistaken for a gap somebody might close.
- **InMail and connection invitations.** Not built. They spend his credits and his network, neither is
  on the critical path to a job, and the three above did not all land -- so the precondition the brief
  set was not met either.

---

## The bug I wrote, and the slice that refused to certify it

`dom._ROW_SCOPE` carried a comment saying it was **"reused verbatim"** from the reader's
`_FOLLOWED_PAGE_ID_SCOPE`. **It was not.** It had dropped `[.//a[contains(@href,'/company/')]]` -- the
one condition the reader's own long comment exists to explain. Measured consequence on the real capture:
the nearest non-landmark ancestor holding exactly one unfollow button is a **bare wrapping `<div>` with
zero company links**, so the trailing predicate could never be satisfied and **all twenty rows returned
count 0. The selector matched nothing.** Every unfollow would have refused, quietly, for a reason nobody
would have found.

It was caught by a slice that **instrumented the scope resolution instead of reading the comment**, and
that same slice then **refused to write the safety test I had specified**, because building its markup
the natural way -- flat, link and button as siblings -- makes it PASS against a selector that matches
nothing on the real page. The brief called that test "the most important in the module"; as specified it
was a control that could not fail.

Both fixes are structural rather than textual:

- **One predicate string, consumed twice.** `_FOLLOWED_PAGE_ID_SCOPE` is now literally
  `"xpath=" + _ROW_SCOPE`, so "the read and the write agree about what a row is" is true by construction
  rather than by assertion. `test_the_read_and_write_paths_share_one_row_predicate` pins the
  RELATIONSHIP, not the two strings separately -- pinning them separately would not have caught this.
- **Both markup shapes are tests**, named as a pair, with the flat one documented as the control that
  could not fail.

**A comment asserting that two strings are the same is worth nothing; being the same string is worth
what the comment claimed.** That is the same defect class as a gate printing an unmeasured
reversibility claim, one layer down, and it is the third instance of it this wave found.

---

## Corrections to claims this package was already making

| claim | was | now |
|---|---|---|
| `set_open_to_work.reversibility_evidence` | named `aria-label="Open to"` as the editing control | FALSE; corrected to `"Edit"`, old sentence quoted |
| `set_open_to_work` surface | "has never been loaded" (an admission) | a measurement: 237 urls + 37 payload paths, 0 hits |
| `follow_company` refusal | "no unfollow is sanctioned" | one is; the undo cannot be AIMED (slug vs id, 20 of 58) |
| `mark_notifications_read` | one ground | three, two of them new and independent |
| `dom.FOLLOW_CONTROL` | class carries nothing, `aria-pressed` nowhere, universally | true of `/jobs/view/`; **refuted by a capture in this repo** -- `/jobs/search/` renders `class="follow is-following" aria-pressed="true"` |
| README "Reads only" | false from the day `save_job` shipped, survived a wave | corrected, old wording named |
| README counts | "thirteen tools", "986 tests" for three waves | 17 and 1407 |
| `mcp.instructions` | "TWO WRITE", no apply guidance | three, plus an apply paragraph; the test now DERIVES the count from `PERFORMABLE` |

---

## The boundary did not move

**`readonly.py` is a zero-line diff.** No allowlist pattern was added, no forbidden substring was
shortened, `SANCTIONED_MUTATIONS` is still one line, and the AST invariant **did not need re-freezing.**

That was a design choice, not luck. Two things made it possible:

1. **Unfollow's surface was already on the read allowlist** (`/mynetwork/network-manager/company/`) and
   contains none of the twenty forbidden substrings. Its `url_template` carries **no `{target}`** -- the
   action is performed on a LIST and the target selects a ROW -- and `str.format` ignores an unused
   keyword, so `assert_write_url` rebuilds the constant from the grant exactly as it rebuilds an
   interpolated one.
2. **ONE click site, N actions.** `perform` computes a per-action selector and clicks once, so a second
   performable action added **zero** mutating calls to the package.

**Verified rather than asserted**, with `mcp-servers/_audit/_instruments/boundary_digest_option2_probe.py`
under both interpreters at `063c9b7`:

```
agg 3.10.19 = 7a48ca1e8dd14ec1
agg 3.13.14 = 7a48ca1e8dd14ec1
13 functions compared, 0 mismatches
```

A single-version local run cannot verify a version-independent claim, which is why both were run.

---

---

## The click path had no test, and writing one found a defect

After the first CI run went green I checked what the suite actually covered and found the gap that
mattered: **`perform` was exercised only against a POSTING.** Everything about the unfollow that is
NEW branches on the difference -- the landing check (a list has one address and no id in its url), the
live control read (a row predicate rather than a name), and the whole verification (a reload plus
LinkedIn's own count) -- and none of those branches had run. The gate and preview were covered; the
click was not.

**The fixture navigator could not express the situation, and that is worth recording rather than
patching around.** `FixtureNavigator` maps one url to one page, which is exactly right for the save
pair -- it clicks on a posting and confirms from the saved list, two urls, so before and after are two
frozen worlds by construction. An unfollow loads **one url twice** across a world the click just
changed. A one-page-per-url fake serves either the before-world to the verification (which then always
reports failure) or the after-world to the click (which then always refuses at gate 5, because the row
it was about to press is not there). **Both were observed while writing these tests, and both look like
a code defect rather than a fixture that cannot say what is being asked.** `SequencedNavigator` pops
from a per-url queue, so the two readings are two worlds.

Seven tests, and the one that carries the others is
`test_a_vanished_row_with_an_unchanged_total_is_unknown_not_success`. **A verification that concluded
"row gone, therefore unfollowed" would pass both the happy path and the failure path** and would report
success every time this partial list merely reordered. Only a world where the row vanished and the
total held distinguishes them.

**AND IT FOUND A REAL DEFECT.** On `performed == "unknown"`, the block told him to
**"Open your saved jobs and look first"** -- after an UNFOLLOW. The advice not to retry is the same for
both actions and is the important half; sending him to the wrong page to check is how a correct
instruction becomes useless. The surface is now named per action, and the test pins that the unfollow
block does not mention saved jobs at all.

**Then the same defect turned up a second time, in the other new block** (`0979ed8`). Both surface-less
actions render the same no-token warning, and its prose fitted only one of them: *"its EDITOR has never
been loaded"*, closing with *"change it yourself in LinkedIn if you want it CHANGED"*. True of a profile
setting sitting behind an editor; **nonsense on an application, which has no editor and is not a
change.** Found by rendering the block and reading it, not by a failing test -- so the test came second
and asserts the PROPERTY (the string must fit both actions that reach the branch) rather than the
sentence.

**Two instances in one afternoon makes it a class rather than a slip:** when one code path serves two
actions, its PROSE silently keeps the shape of whichever action it was written for, and no type, no
assertion and no reviewer's eye catches it -- only rendering the thing and reading it does. Both are
now pinned by property. It is the same failure as a gate printing an unmeasured reversibility claim,
moved from the fields into the sentences around them.

---

## Measured

All at `0979ed8`, CPython 3.13.14 (win32), on a settled working tree.

| | |
|---|---|
| suite | **1416 collected, 1416 passed, 0 skipped, 0 failed, 0 errors**, 289s |
| `scripts/ci_full_run_check.py` | **exit 0** -- `collected 1416 \| reported 1416 \| executed 1416 \| skipped 0 \| failed 0 \| errors 0` |
| boundary digests | 13 functions + aggregate `7a48ca1e8dd14ec1`, **identical under 3.10.19 and 3.13.14**, re-measured at HEAD |
| `readonly.py` vs pre-wave `a1360d1` | **0 changed lines** |
| tools registered | 16 -> **17** (reads unchanged at **14**) |
| sanctioned actions | 4 -> **6**; performable 2 -> **3** |
| package mutating calls | **1** sanctioned, **0** unsanctioned |
| identity sweep | **0 hits across 99 swept files**, 191 spellings, 10 classes |
| **live writes executed** | **0** |

### A correction to `445c7a0`'s own commit message

**It says 1393. The measured number is 1407**, and the 14 are not new tests I forgot -- they are the
`git ls-files` parametrisation growing when seven new files were STAGED. I reached 1393 by ADDING a
module's 20 cases to an earlier run's 1373 instead of measuring the tree I was about to commit.

**A sixth way local green is not green, and it is my own arithmetic rather than the tooling:** the
previous wave's lesson was that a stable HEAD is not sufficient and a stable WORKING TREE is required.
Both were true here. What was not stable was **the INDEX** -- two parametrised modules enumerate
`git ls-files`, which counts staged files, so `git add` alone moves the collection. A total computed
rather than measured cannot notice that. The number in this file and in the gate output is the measured
one.

## CI

| run | at | result |
|---|---|---|
| **32688677004** | `063c9b7` | **success on all three cells** -- ubuntu/3.10, ubuntu/3.13, windows/3.13 |
| **32689900525** | `6e11109` | the click-path tests and the wrong-surface fix |
| **32690453627** | `0979ed8` | the apply warning written for the wrong action |

<https://github.com/Sundeepg98/linkedin-mcp/actions/runs/32688677004>

The 3.10 cell is the one that matters most here and it is the one that went red three times on
`readonly.py`'s digest two days ago. `readonly.py` is untouched this wave, so its passing is a
consistency check rather than a new result -- but the OS axis is covered, and every local run on this
box is win32.

Pushed `a1360d1..063c9b7`, then the rest as a fast-forward.

## Hygiene, left for the operator or a later lead

Four `_audit/_slice-*.md` files from EARLIER waves remain untracked and un-ignored -- `_slice-click-probe`,
`_slice-cold-review-2026-08-23`, `_slice-mutation-kill`, `_slice-py310-run` -- which is `git add -A`
exposure. I tracked my own four census files (swept clean, 0 hits) because they are the receipts for
numbers now frozen into code, and left the other four alone because they are not mine to decide. A
blanket `_slice-*.md` ignore is still the wrong fix: six are now tracked, so the rule's own set would
contradict it.
