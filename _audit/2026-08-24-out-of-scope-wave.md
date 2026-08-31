# The eight refusals, worked -- `445c7a0` .. `5bc0181`

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
Its residue is irreversible in AUDIENCE and a current employer can see it. **No capture of the live
profile was taken. That one needs him watching.**

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

## 6. READING HIS INBOX -- MEASURED 2026-08-24. Reading works, and the finding STRENGTHENS the ban

The brief was right about the asymmetry: `/messaging` is on `_FORBIDDEN_URL_SUBSTRINGS`, and **every
written rationale for that entry is phrased against SENDING.** Whether READING is possible was never
separately argued.

It has now been measured, on two independent runs (mine, and the lead's after the operator granted the
permission). **This section previously said UNMEASURED and blocked by the permission system. That is
no longer true and the section is rewritten rather than annotated.**

### What was measured

1. **Reading IS possible.** No auth wall. The conversation list renders and is enumerable. VERIFIED.

2. **THE AUTO-OPEN HYPOTHESIS IS CONFIRMED.** This section previously carried it in capitals as a
   thing nobody had verified on this account or any other. Asked for `/messaging/`, the browser landed
   on `/messaging/thread/<THREAD-ID>/`. **LinkedIn's desktop messaging opens a specific conversation on
   arrival.** Both runs agree. VERIFIED on the landed url.

3. **The side-effect measurement is INCONCLUSIVE, and must not be upgraded.** The two runs failed to
   measure it for two different reasons, and the second reason is the sharper one:
   - my run: no badge was readable BEFORE, so a drop could not have been observed;
   - the lead's run: the badge read `Messaging, 0 new notifications` before AND after -- **it was
     already at zero, so the control could not fire.** A check that cannot fail certifies nothing.

   The probe reported this correctly rather than reporting a clean run, which is the only reason its
   output is worth anything.

### What it does to the boundary

**It strengthens the forbidden entry, and now on a measurement rather than an argument.** A tool named
`read_inbox` would not return an inbox; it would land inside one correspondent's thread. If opening a
thread marks it read, then an inbox tool MUTATES ON EVERY CALL -- the precise objection that keeps
`mark_notifications_read` forbidden, arriving through something calling itself a read.

**The forbidden list is unchanged, and no guard was loosened.** The remaining unknown is narrow and
specific, and worth stating exactly so nobody re-opens the whole question to answer it:

> **Does opening a thread clear its unread state?** Answerable only with a genuinely unread
> conversation present, so that the badge has somewhere to fall from.

### A count that differs between runs, recorded rather than resolved

My run enumerated **10** conversations; the lead's enumerated **11**. Different times, and both captures
have since been destroyed, so neither can be re-checked. The likeliest explanation is simply that a
message arrived in between. It is recorded as two measurements rather than reconciled into one, because
there is no evidence left that would settle it.

### The probe leaked, and has been fixed

The first version printed every aria-label and a slice of the inbox text, and wrote three full-page
captures to `_audit/`. Running it therefore published real people's names and a live member urn into a
transcript. **The instrument built to answer a privacy question captured the data it was asking about.**
The captures were gitignored and have been destroyed. The probe now:

- writes **no file at all** -- it holds no output path, so there is nothing to forget to delete;
- prints aria-label **templates with counts** (`Select conversation with <NAME> x11`), never labels;
- redacts thread ids, member urns and names, with a redactor guarded by
  `tests/test_probe_redaction.py` in **both** directions -- a redactor that flattened everything to
  `<NAME>` would pass a leak-only test while reporting nothing.

**To re-take the measurement**, with the profile lock free and no other agent holding a browser:

```
D:\workspace\projects\job-hunting\mcp-servers\linkedin\venv\Scripts\python.exe scripts\_probe_messaging.py
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
the natural way -- flat, link and button as siblings -- made it PASS against the DEFECTIVE selector
while the nested form failed. The brief called that test "the most important in the module"; as
specified it was a control that could not fail.

Both fixes are structural rather than textual:

- **One predicate string, consumed twice.** `_FOLLOWED_PAGE_ID_SCOPE` is now literally
  `"xpath=" + _ROW_SCOPE`, so "the read and the write agree about what a row is" is true by construction
  rather than by assertion. `test_the_read_and_write_paths_share_one_row_predicate` pins the
  RELATIONSHIP, not the two strings separately -- pinning them separately would not have caught this.
- **Both markup shapes are tests**, named as a pair, with the flat one documented as the control that
  could not fail.

**A CORRECTION TO MY OWN FRAMING, from the slice that wrote the module, verified here before it was
accepted.** I described the flat form in the present tense -- one that "passes against a selector that
matches nothing on the real page" -- and wrote that into `445c7a0`'s commit message as though it
described the shipped code. **It describes the DEFECTIVE code.** Measured against the REPAIRED
selector, FLAT and NESTED both return count 1 and both reject the member row, because the fixed
predicate climbs to a scope carrying the company link either way. So the flat test cannot hold that
claim as a live assertion, and the slice did not let it: it moved the historical measurement into the
docstrings and gave the flat test an assertion that is true NOW -- a cross-check that fails on
DIVERGENCE between the two shapes, which makes the pair a standing tripwire for nesting-sensitivity
rather than a commemorative plaque. Its mutation run shows the pair still working: with the original
defect restored, the flat twin's own assertions PASS and it goes red only through the cross-check.

**The general point, and it is the one this wave keeps re-teaching:** a test written to reproduce a bug
describes the BUG'S world, and the moment the bug is fixed that description becomes history. Leaving it
in the present tense is how a suite acquires assertions that read as guarantees and check nothing --
the same failure as a comment claiming two strings are identical, arriving through the tense of a
sentence instead of through its content.

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

## Sixty-eight tests about a feature, and none about whether it is plugged in

Checked at the end, after CI was already green twice: **nothing asserted that
`linkedin_job_detail` RETURNS `apply_path`.** The DOM reader is covered, the pure classifier is covered
by 68 tests, and the four lines in `server.py` that put the answer into the result a caller sees were
covered by nothing. `apply_path` appeared in the test suite exactly twice, **both times inside an
assertion about a docstring.**

**The sibling field had the same hole and it is not mine.** `company_follow_state` was added by an
earlier wave in exactly the same shape, and appeared **zero** times in the tests outside the source. It
is covered now too, because the gap is a property of the SEAM rather than of either feature, and
closing half of it would leave the next person believing the seam is tested.

**Shown failing on the real file, and the numbers are the whole argument.** One mutant: the assignment
changed so the field is computed and dropped on the floor -- exactly what "wired wrong" looks like.

| | |
|---|---|
| `tests/test_apply_fixture.py` | 68 tests, **all 68 still passed** |
| `tests/test_job_detail_wiring.py` | 5 tests, **3 failed** |

**Sixty-eight tests about the feature agreed it was fine.** The two that stayed green are the two not
about `apply_path` -- the sibling field and the shell control -- which is the right shape for a mutant
that removed one thing. Mutant reverted; `server.py` byte-identical to its commit.

**The class, stated because it will recur:** a field computed correctly, tested correctly, and never
plumbed is invisible to unit tests BY CONSTRUCTION -- a unit test of a computation passes whether or not
anything calls it. Only exercising the surface a caller touches can catch it. This is the third distinct
thing this wave found by looking at the OUTPUT rather than at the code: the wrong-surface advice, the
wrong-action warning, and now the unplumbed field.

---

---

## After the lead's rulings: build nothing, state the scope, give apply an address

Three rulings came back and two of them changed what shipped.

**BUILD NO PAGED READ.** Ruled on the cost I raised rather than on the gain: the `queryId` is a
build-tied content hash, and this repo has already measured LinkedIn dropping
`data-view-name="job-save-button"` inside 24 hours on this account. A hardcoded persisted-query hash
is that failure one layer deeper, and it fails SILENTLY -- a 4xx reads as "no results" rather than
"your contract expired". Against that, the gain is 58-of-58 instead of 20-of-58, and the tool already
reports `total: 58`, so it is **already honest about what it cannot see**. An honest partial answer
beats a complete one that will quietly become wrong.

**UNFOLLOW VIA API: NO**, on the ground I flagged it under -- every gate in `writes.py` rests on the
click being anchored to a control the operator was shown, and synthesising LinkedIn's own request
discards that anchor entirely. The safety story would become "we constructed a plausible request"
rather than "we pressed the button he saw."

**STATE THE SCOPE, DO NOT INVENT A GATE.** Done, and it cost nothing -- which was measured rather
than hoped for.

### The scope statement, and why it was free

`readonly.py`'s opening claim -- *"`assert_read_url` is the only door to `page.goto`"* -- was always
exact and always read as broader than it is. **Exactness is not clarity:** a reader who takes it for
full coverage has not misunderstood the sentence, they have understood a different sentence that the
true one is easily mistaken for. The closing bullet made it worse by enumerating what the server does
NOT do (*"issues no non-GET request"*) without naming the one thing it does. **Enumerating absences
without naming the presence is how a true list misleads.**

Both now say it outright: the module docstring states NAVIGATION-ONLY, names `ME_API`, says the
allowlist would REFUSE it if consulted, points at the enumeration that does cover it, and records why
the pattern list was not widened. `server_info` gained `read_boundary_scope` beside
`direct_api_reads`, because *"there is one uncovered path"* and *"the boundary covers navigations"*
are different facts -- the first is an exception a reader files away, the second tells them how to
reason about the next thing somebody adds.

**MEASURED TWO WAYS:**

| | |
|---|---|
| digest probe | `7a48ca1e8dd14ec1` before and after, identical under 3.10.19 and 3.13.14, 13/13 functions |
| AST comparison | the module body EXCLUDING its docstring parses **identical** to the previous commit |

The second is the stronger claim, and it is the one pinned in a test: a digest matching proves the
hashed things did not move; this proves **nothing but prose did**. The freeze hashes the four constant
structures as values and each function's token stream with `COMMENT` tokens dropped -- a MODULE
docstring is neither, so the AST invariant never fired and no re-freeze was needed.

**The asymmetry is worth knowing and is pinned:** a FUNCTION docstring is a string token inside a
function body and WOULD move that function's digest. Only the module docstring is free. A future edit
that tidies this paragraph into `assert_read_url`'s own docstring fires the invariant -- correctly.
So `readonly.py` is no longer a zero-line diff for the wave; it is a **docstring-only diff, +32/-1,
with the body proven AST-identical**.

### Apply: the refusal now has an address

Apply's refusal was correct and had a shape I did not like on re-reading. It said the flow has never
been captured and said nothing about how a capture is taken. Open To Work got an exact procedure out
of its census; apply did not -- which left a MEASURED gap reading like a SETTLED decision. The next
person who wants apply then either gives up or improvises a selector, and on the one action this
server can never undo that is precisely what must not happen.

`scripts/_probe_apply_flow.py` is that procedure, and the thing that makes it reasonable to ask him to
run it is structural rather than promised:

- **It navigates, it does not click.** LinkedIn draws the apply control as an `<a href>`, so the flow
  is reachable without pressing anything. Verified with the package's own scanner:
  `readonly.scan_source_for_mutations` finds **zero** mutating calls in it, asserted in a test rather
  than claimed in a comment.
- **It refuses to guess which posting to open.** The job id is a required argument, never a default,
  because which posting acquires a draft is not a decision a default should make. It also stops with
  an explanation if the posting draws the off-site control instead.
- **The side effect is measured, and labelled a hypothesis.** LinkedIn shows "in progress"
  applications, which suggests opening an Easy Apply flow may create a draft. **Nobody here has
  verified that.** Same class of claim as the messaging auto-open, same treatment: read the applied-tab
  count BEFORE and AFTER on a surface the apply navigation does not touch, and report INCONCLUSIVE
  when it cannot be read rather than reporting a clean run. That lesson was applied *before* the
  mistake this time instead of after it.
- **Guarded** with `if __name__ == "__main__"`, for the reason established earlier today.

Wired so it is discoverable from the CODE and not only from the file tree: the refusal and the spec
both name it, both say it has NOT been run, and tests pin that the refusal names it and that the file
exists, scans clean, is guarded, and requires its argument. **A procedure named but absent is worse
than no procedure, because it reads as completed work.**

**It has not been run.** Zero live writes stands for the whole wave.


---

## The paged read: the contract is real, and it does not unblock follow

The lead read the unfollow census's set-aside affordance -- *"the Rest.li `start`/`count` contract via
`voyagerSearchDashClusters`, not a route this server can take as built"* -- and directed me to build the
paged READ instead of asking the operator to follow a company by hand. The reasoning was that if the
list is pageable to all 58, sort order stops mattering, because a newly followed company is reachable
wherever it lands.

**The contract is real.** It is not a schema node, which was worth checking because the same captures
carry a GraphQL type registry that made `followedAt` look like a field when it was a type. This is a
recorded request with its response status:

```
GET /voyager/api/graphql?includeWebMetadata=true
    &variables=(start:0,count:10,origin:CurationHub,
                query:(flagshipSearchIntent:MYNETWORK_CURATION_HUB,
                       includeFiltersInResponse:true,
                       queryParameters:List((key:resultType,value:List(PAGES)))))
    &queryId=voyagerSearchDashClusters.<32-hex persisted-query hash>
  -> status 200
```

`start:0,count:10` is right there, in a call LinkedIn's own page made. One correction to the census's
framing: the path is **`/voyager/api/graphql`**, not a plain Rest.li resource -- `voyagerSearchDash
Clusters` is the `queryId`, not a url segment. There is no `/voyager/api/voyagerSearchDashClusters` in
any capture; the six voyager paths present are graphql, me, premium/featureAccess, launchpad,
notifications badging and chameleon config.

### And it still does not unblock `follow_company`

**MEASURED, and this is the finding that decides it.** A company id taken from the PAYLOAD of the very
same capture -- present in the graphql response, absent from the rendered rows:

```
id <rendered row 1>        -> read_unfollow_control count 1
id <another rendered row>  -> read_unfollow_control count 1
id <in payload, not drawn> -> read_unfollow_control count 0
```

**The unfollow CLICKS A DOM CONTROL.** `perform` calls `page.click(selector)`, and a selector that
resolves to zero nodes cannot be clicked -- gate 5 refuses before it tries. Enumerating all 58 company
ids over the API tells the server the company EXISTS. It does not put that company's button on the
page.

So the lead's inference holds for READING and fails for CLICKING, and the difference is the whole
question. A paged read turns *"20 of 58, and I cannot tell you about the rest"* into a complete list --
real value for a reader, and no help at all to an unfollow.

**That is a third answer**, and it is neither branch the directive offered: the route is not refused,
not capped, and does not need a token the server cannot mint. It works, and it is aimed at the wrong
half of the problem.

### What WOULD close the loop, and why it is not mine to take

Exactly one thing: **an unfollow performed through the API rather than through the control.** Then
enumeration would be sufficient, because knowing the id would be knowing how to act on it.

The cost is not incremental. It is a `POST`, which `readonly._MUTATION_CALL_PATTERNS` catches as
`http_post` and which would need its own `SANCTIONED_MUTATIONS` entry -- and more importantly it moves
this design from *"click the control the operator was shown"* to *"synthesise the request LinkedIn's
own JavaScript would have made"*. Every gate in `writes.py` is built on the first of those. The confirm
block names a control; gate 5 re-reads that control; the click is anchored to a row a human could point
at. An API write has none of that to anchor to. **This is a decision about what kind of program this
is, not a feature, and it is flagged rather than taken.**

### A separate finding, and it bears on the directive's own constraint

The directive said the paged read *"must go through `assert_read_url` like every other read."*
**It would not be like every other read, because the existing API read is not gated either.**

Measured: `assert_read_url` is called in exactly **two** places -- `browser.py:387`, the `goto` path,
and `writes.py:1149`, the write preview's loader. `auth.py:241` calls
`page.request.get(ME_API, ...)` with **no gate at all**, and:

```
readonly.is_read_url(ME_API)        -> False
readonly.is_read_url(<graphql url>) -> False
```

The identity endpoint this server has always used **would be refused by its own read boundary if that
boundary were consulted.** The design never lied -- its claim is precisely that `assert_read_url` is
the only door to `page.goto`, and an API call is not a `goto` -- but the gap was real and undocumented,
and `server_info` did not mention it. Blast radius is nil: one hardcoded constant, GET only, no
caller-supplied url. **The point is that a paged read built on `page.request.get` would land on that
same ungated path**, so satisfying the constraint means first deciding what gates API reads at all.

**CLOSED AT `56e03b0`, in the half that needed no boundary move.** `tests/test_api_call_sites.py`
enumerates every direct HTTP call site in the package **by AST** and pins the set to one entry, as
`(module, verb, first-argument-as-written)` -- the shape of `readonly.SANCTIONED_MUTATIONS`, and one
line long. The first argument is pinned as SOURCE TEXT, so aiming the call at a different url, or at
something a caller supplies, fails even with module and verb unchanged. It also pins that
`assert_read_url` has exactly two callers, and that `ME_API` is NOT on the allowlist -- so adding it
later is a failing test somebody has to come and justify. `server_info` gained `direct_api_reads`,
which names the endpoint, says GET, says why the call exists, and says plainly that the allowlist does
not cover it; a declaration naming the endpoint while implying it was gated would be worse than none.

**AST rather than text, with its own test:** this repo's guard modules are full of prose naming the
calls they hunt -- `readonly.py`'s tables are made of the strings it scans for -- so a text search for
`request.get` counts a docstring. Three can-it-fail controls cover the shapes somebody could really
add: a url from an argument, a verb that writes, and a second endpoint beside the sanctioned one.

**What was deliberately NOT done:** adding `/voyager/api/me` to the read allowlist. That moves a frozen
boundary structure and fires the AST invariant, to authorise something already a constant nobody can
redirect. `readonly.py` stays a zero-line diff for the entire wave.

### The other costs, named rather than discovered later

- **`auto_paging: False` and `max_page_loads_per_call: 2` are ASSERTED FIELDS** in
  `server_info.rate_discipline`, and the README sells the risk posture on *"One page load per tool
  call. No scroll loops, no auto-paging, no fan-out."* Six paged calls to cover 58 rows contradicts
  all three. That is a posture change to be made deliberately and declared, not absorbed.
- **The `queryId` is a build-tied hash.** It is a content hash of a persisted query document, so it
  moves when LinkedIn redeploys the frontend. Whether it rotates is UNMEASURED here -- one capture set
  from one day cannot show rotation -- but this repo has already measured LinkedIn changing
  instrumentation on this account inside 24 hours: `data-view-name="job-save-button"` was present on
  the 2026-08-22 capture and gone from the 2026-08-23 one. A hardcoded hash is that failure one layer
  deeper and less visible. Harvesting it from the page's own payload would be the fix, and costs a page
  load, which is the thing paging was meant to save.
- **`count:10` is what was observed.** The DOM holds 20, so the page made at least two calls. Whether
  `count:` can be raised is unmeasured.

### What I could not do

**Prove any of it live.** The permission classifier refused the browser probe twice earlier in this
wave, so no request was issued and none of the above is certified against LinkedIn. Every claim here
is from captures on disk and from the package's own source. The contract's shape is measured; its
behaviour under a different `start` is not.

### Recommendation

`follow_company` stays gated, and its reason is now **stronger and different** -- not *"nobody can tell
which order the list is in"* but *"reading further down the list does not make a row clickable"*. That
reason survives every sort order, so the census's proposed manual experiment is not needed either:
even its best case, newest-first, gives only a window that decays as roughly twenty further follows
push the row out, which the census itself flagged as not a symmetric pair.

The paged read is worth building **for `linkedin_followed_companies`**, on its own merits, with the
posture costs above declared. It is not worth building to unblock follow, because it does not.

---

## CI STOPPED WORKING MID-SESSION, AND THE THREE RED RUNS ARE NOT ABOUT THIS CODE

Read this before drawing any conclusion from the run list. Three runs at the end of this wave are RED
and **not one of them executed a single test.**

```
07:19  c90469c  success
07:29  6ea78ce  success
07:31  04abadb  success
07:40  4b34c64  success
07:44  eae1740  success   <- last green
08:04  844f5a3  FAILURE
08:14  56e03b0  FAILURE
08:15  4057a6b  FAILURE
```

**MEASURED: all NINE cells of all three red runs report ZERO STEPS.** Two of the three runs completed
in **three seconds**. One of the failing commits, `844f5a3`, changed a single markdown file and nothing
else. The workflow file is unchanged and was green forty minutes earlier. Logs return `BlobNotFound`
and the step arrays are empty, because the jobs were rejected before they started -- there is nothing
to read and nothing ran.

**PROBABLE CAUSE, LABELLED AS PROBABLE.** The Actions allowance on this private repo. August
month-to-date for the account is **3426 Linux + 2363 Windows + 52 macOS minutes** -- roughly **8.7k
Linux-equivalent** once Windows is doubled and macOS multiplied by ten -- every line currently
discounted to `netAmount: 0.0`. This wave alone added about thirteen runs across three cells.

**It is NOT confirmed and it is not mine to confirm.** The billing endpoint that reported a remaining
balance has moved, and the replacement exposes usage rather than headroom, so nothing readable from
here distinguishes "allowance exhausted" from another account-level block. The spending-limit page is
the operator's to look at.

**WHAT IS THEREFORE UNCERTIFIED:** `844f5a3`, `56e03b0`, `4057a6b` -- the paging analysis, the API
call-site guard, and this record. Everything up to and including `eae1740` is green on all three cells,
which covers the whole of the wave as originally reported.

**THIS IS NOT A CLAIM THAT THEY ARE FINE.** Local green is not green, and this wave has catalogued six
distinct mechanisms for that. The honest statement is narrower: those three commits pass everything
this box can run, and the thing preventing certification is not inside them. A green run with a silent
skip would fail the completeness gate; a run that never starts tells you nothing either way, which is
exactly why it is written down here rather than left as three red marks a future reader would take for
a broken suite.


## Measured

All at `5bc0181`, CPython 3.13.14 (win32), on a settled working tree.

| | |
|---|---|
| suite | **1446 collected, 1446 passed, 0 skipped, 0 failed, 0 errors**, 391s |
| `scripts/ci_full_run_check.py` | **exit 0** -- `collected 1446 \| reported 1446 \| executed 1446 \| skipped 0 \| failed 0 \| errors 0` |
| boundary digests | 13 functions + aggregate `7a48ca1e8dd14ec1`, **identical under 3.10.19 and 3.13.14**, re-measured at HEAD |
| `readonly.py` vs pre-wave `a1360d1` | **docstring only**, +32/-1, module body proven **AST-identical** |
| tools registered | 16 -> **17** (reads unchanged at **14**) |
| sanctioned actions | 4 -> **6**; performable 2 -> **3** |
| package mutating calls | **1** sanctioned, **0** unsanctioned |
| identity sweep | **0 hits across 102 swept files**, 191 spellings, 10 classes |
| **live writes executed** | **0** |

### The probe that never ran -- SUPERSEDED, and the check itself no longer works

**As written, this said:** `_audit/` holds no `_probe-messaging-*.html`, which is what the messaging
probe writes on its first successful load; its output is gitignored, so checking the working directory
rather than the index was the only way to tell, and it was empty. The claim that reading his inbox was
UNMEASURED was therefore checkable rather than merely stated.

**Both halves are now dead, and it is worth being precise about which died how.**

1. The probe HAS run -- twice. See section 6.
2. **The check would not work even if it had not.** The probe was hardened after it leaked, and it
   now writes no file under any circumstances. So an empty `_audit/` no longer distinguishes "never
   ran" from "ran and wrote nothing", which is every run from now on.

This is a small example of a general hazard worth naming, since this package leans on file-presence
checks in several places: **a check whose signal is the ABSENCE of a side effect silently stops working
the moment the side effect is removed**, and it keeps passing while it does. It does not fail; it just
stops meaning anything. Nothing replaces it here, because the thing it was guarding -- the claim that
reading was unmeasured -- is no longer true.

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
| **32690453627** | `0979ed8` | **success on all three cells** -- the apply warning written for the wrong action |
| **32691280559** | `460d800` | **success on all three cells** -- the wiring tests and the sibling gap |
| **32700770298** | `f351edf` | **success on all three cells** -- the irreversibility report |
| **32701736950** | `6ea78ce` | the two defensive branches and their reachability |

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
