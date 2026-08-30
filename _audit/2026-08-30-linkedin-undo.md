# The two undo gaps: one closed, one instrumented, one theory killed

**Wave:** linkedin-undo. **Commits:** `c7de11a`, `7591ed6`, `ab14f2f`, `1b09fbd` on `master`,
**not pushed**. **Baseline in:** 1944 passed. **Baseline out:** 1977 passed, zero failures.
**`_state/` unchanged.**

---

## 0. The headline, before the detail

| gap | brief said | what happened |
|---|---|---|
| 1 -- `unsave_job` anchor | re-measure the ON label, then add the row | **NOT closed. The row is NOT added.** The label cannot be re-measured in the running build at all, so the single reading stands alone and nothing was shipped on it. What IS shipped is the read-only route that makes the re-measurement a repeatable READ, costing no write. One restart away. |
| 2 -- tracker read | apply the job-detail readiness treatment | **Treatment applied to all three tabs, and the theory behind it does not survive the measurement.** Saved failed **6 of 6** while Draft went 2 of 2 and Applied 2 of 2, through the same function, in one ten-minute window. A settle race does not do that. The wait ships as real hardening; a second instrument ships to name the actual cause on the next live call. |

**The most important sentence in this document:** the brief's premise that gap 2 is "almost
certainly the same defect `6f08953` just fixed" is **contradicted by the live series below.** I
built the readiness wait as ordered -- it closes a real hole and it is correct -- but I did not
find the defect it was expected to find, and I have not pretended otherwise.

---

## 1. Gap 2, measured before it was touched

Fifteen live calls through **one process** -- pid 9028, `build.code.commit` `42a68aa69057`,
`dirty: false`, started 13:16:20Z, still the same process at wave close (uptime 6350 s). So every
reading below describes one build. Each tracker read paired with `linkedin_search_jobs` as the
control, per the standing rule.

| surface | attempts | read the list | outcome |
|---|---|---|---|
| `linkedin_saved_jobs` | **6** | **0** | every one: *"LinkedIn's own Saved tab says 1, and no empty state was drawn"* |
| `linkedin_draft_applications` | 2 | 2 | 1 row, `tab_counts {saved:1, draft:1, applied:0, interview:0}` |
| `linkedin_my_applications` | 2 | 2 | 0 rows, count 0, empty state `"No matches"`, correctly reported EMPTY |
| `linkedin_search_jobs` (control) | 2 | 2 | full results, opening and closing the window |
| `linkedin_job_detail` (4423880462) | 1 | 1 | the Sprinto posting in full, description, pay, apply route |

**All three tracker tools are ONE function.** `server._read_tracker(stage, ...)` builds
`/jobs-tracker/?stage={stage}` and runs one loader, one text read, one harvest. There is no
per-tab code to differ. So the answer to *"do the siblings share the defect?"* is: they share
every line of it, and **they did not share the symptom.** That is the finding.

**What it rules out.** A `browser.goto` settle race is stage-blind -- it lands where 3.5 s puts it
regardless of the query string. It cannot produce 6-0 on one stage and 4-0 across its siblings
minutes apart.

**What it leaves.** The Saved tab's row shape is unmeasured by this repo, and that is not a
speculation:

> `tests/fixtures/jobs_tracker_row.html` is the **DRAFT** tab (its tab strip reads `Draft . 1`, its
> dialog reads *"Discard draft application and remove this job?"*).
> `tests/fixtures/jobs_tracker_empty.html` is the **SAVED** tab with **nothing in it**.

**A populated SAVED tab has never been captured.** The row parser and the row selector were both
built and tested against a DRAFT row. If LinkedIn draws a saved row whose link is not
`/jobs/view/<id>`, the symptom is exactly what the operator met -- and it is indistinguishable,
from outside, from a page that never drew. That is now the leading suspect, and it is a suspect
rather than a finding because nothing in the running build can see the live saved row.

One corroborating oddity, recorded but not chased: the live DRAFT row parses **degraded** --
`title` swallows the whole card (`"ServiceNow Application Developer Luxoft . India (Remote)No
longer accepting applications"`), `company` and `location` null -- while the same parser over
`jobs_tracker_row.html` produces clean fields. So the live tracker DOM has already drifted from
the capture on the one tab that still works. That is a second, independent reason to believe the
capture set is stale rather than the loader broken.

---

## 2. What was built for gap 2

### `dom.wait_for_tracker_list` -- the third sibling

Same contract as `wait_for_job_description` and `wait_for_save_control`: one bounded wait, one
three-valued verdict, no retry loop, never raises. `attached` True / False / **None**, where None
is the instrument-failed value and the default, so a path nobody thought about cannot arrive
claiming to have measured LinkedIn.

**The anchor is a DISJUNCTION**, and that is the design decision worth reading:

```python
def tracker_list_selector() -> str:
    parts = [TRACKER_ROW_LINK]                       # main a[href*="/jobs/view/"]
    parts += ['main :text-is("%s")' % m for m in shape.TRACKER_EMPTY_MARKERS]
    return ", ".join(parts)
```

Three properties, each measured rather than argued:

1. **It waits for exactly the condition the refusal tests.** `_read_tracker` raises when it has
   neither rows NOR a corroborated empty state. Waiting for that same disjunction is what stops
   the wait drifting into waiting for something irrelevant.
2. **An empty tab is not taxed.** Measured over `jobs_tracker_empty.html`: `attached: True` in
   **8 ms**. Waiting only for rows would spend the full 10 s ceiling on every empty tab, and the
   operator has two of them. This is `test_an_empty_tab_is_not_delayed`.
3. **It can fail in the state it detects** -- the law the description anchor was chosen under.
   Over the derived shell: `attached: False`, `failure: TimeoutError`, full bound spent.

**The tab strip is deliberately NOT the anchor, and that is measured, not preferred.** All six
live failures reported LinkedIn's own count of 1, so the strip had demonstrably drawn while the
list had not. An anchor on it reports READY in precisely the state the wait exists to detect --
the same dangerous direction the slot id had on the description. Held by
`test_the_tab_strip_would_have_been_the_wrong_anchor`, which asserts the strip IS present on the
shell.

**The empty half survives the same test**, which matters because a marker LinkedIn always draws
(hidden until needed) would satisfy the wait on an undrawn page and be the identical mistake in
the other half. It does not: all six live failures reported *no empty state drawn*, read out of
the same `<main>` text `shape.tracker_empty_state` matches on. The marker is absent in exactly the
state the wait must fail in.

### `dom.read_tracker_evidence` + `shape.tracker_read_note` -- the half that will name the cause

The refusal reported LinkedIn's tab count and its own zero and nothing whatever about the page
those two disagree over. That is the identical defect the save refusal was rebuilt for earlier the
same day -- *a gate that made a correct decision and then threw away the evidence for it.*

Now it reports `main_present`, `main_chars`, `anchors_total`, `rows_matching`, `scan_complete`,
plus the readiness verdict and `BROWSER.last_settle`. **Counts, never text** -- a tracker row names
a company and a job.

The note is careful about one thing in particular. `anchors_total` **alone cannot** separate a
page that never drew from one that drew rows under a renamed link: measured, the shell and the
legitimately empty page both report `(2 links, 0 rows)`. So the note refuses to read the count
without the readiness verdict beside it and asserts **no threshold**:

> ...it is to be read AGAINST THE READINESS VERDICT BELOW rather than on its own -- no threshold on
> a link count has been measured, and one invented here would be a number that sounds safe.

An earlier draft of that sentence did assert a threshold ("a page that never drew carries few
links"). It was removed before commit: the surface may not print a claim it cannot derive.

### The write gate inherits it, where it matters more

`writes._read_saved_state` reads the same page and is where **`unsave_job` takes its DIRECTION**.
A list read before it drew does not merely return nothing there -- it returns `unknown` and the
gate refuses. Measured 2026-08-30, that is exactly what the operator met. It now gets the same
wait and the same note.

### Where the wait is NOT

`_read_tracker` calls it once, immediately after the authwall check and **before** the text read --
the order is the whole of its value, exactly as with `read_job_posting`. After the harvest, waiting
buys a field describing a page already parsed. Pinned by
`test_the_wait_runs_before_the_rows_are_harvested`.

**It reports and never gates.** `empty_is_believable` still decides. That separation is what stops
a future LinkedIn rename of the empty-state wording turning every legitimately empty tab into an
error. Pinned by `test_the_wait_is_reported_and_never_gates`, driven over a page whose marker is
split across two nodes so the anchor cannot see it and the text parser still can.

`SETTLE_MS` was not raised and no floor was added. That ruling was not re-opened.

---

## 3. Gap 1 -- why the label could not be re-measured, and what shipped instead

### The brief's step 1 is not performable in the running build

The brief said: *"Read the control on 4423880462 and confirm the label, more than once. If you
cannot make a live call, say so and ship nothing on the single reading."*

I can make live calls -- fifteen of them are tabulated above. **I cannot make one that reads the
save control.** Enumerated against the running build, `42a68aa`:

| candidate route | verdict |
|---|---|
| `writes.perform` gate-5 sweep (`read_save_candidates`) | the only instrument that sees the label. Reached ONLY by redeeming a `confirm_token`. **Forbidden to me, and correctly so.** |
| `linkedin_job_detail` | reads the FOLLOW control off the posting. Read no save control. |
| `linkedin_save_job` / `linkedin_unsave_job` preview (token-free, a genuine read) | `state_from="saved_list"` -- reads the posting's title/employer and then the **Saved tab**. It never touches the control. And its list read is broken by gap 2, so it returns `unknown` regardless. |
| `linkedin_surface_census` | closed key set `{feed, profile, settings}`; takes a KEY and never a url. Cannot be pointed at a posting. |

`_audit/2026-08-30-save-label.md` reached the same conclusion independently ("I checked for a
read-only route and there is none"). It is still true, and it is the whole reason gap 1 stayed
circular after the save landed: **the ON label could only be read by performing another write.**

**Therefore: the row is not added.** `shape.SAVE_LABELS` still holds one entry.
`dom.SAVE_LABELS_SEEN` still holds one string. `writes.anchor_label_for` still returns `None` for
`unsave_job`, and it still refuses. Asserted, not promised, by
`test_the_vocabulary_is_untouched_by_this_route` and `test_unsave_still_has_no_anchor_and_says_so`.

### What shipped: the route that makes it a READ

`linkedin_job_detail` already loads the posting and already reads the follow control off it.
`server._read_save_control_state` reads the SAVE control off the same rendering -- no navigation,
no write, no second surface, symmetric with `company_follow_state` beside it.

The wider sweep runs **only on `unknown`** -- the rule `writes._live_control` already runs on,
not a new one. A known state was read off a label the verdict already names.

Driven over a DERIVED page wearing the reported label, the payload is:

```
{'state': 'unknown',
 'why':   "no save control rendered in a state this reader recognises. ...",
 'observed': {'candidates': ['Unsave the job'], 'matched_total': 1,
              'buttons_total': 7, 'labelled_buttons': 5, 'scan_complete': True}}
```

That is `test_the_on_label_would_be_reported_if_a_posting_wore_it`, and it is the proof the route
works. **It is not evidence about LinkedIn** -- the page wears that string because the test put it
there.

### The exact address for closing gap 1

1. Restart the MCP client's `linkedin` server (the running process holds `42a68aa`; confirm with
   `linkedin_server_info` -> `build.code.commit` and compare against `git rev-parse --short=12 HEAD`).
2. `linkedin_job_detail(job_id="4423880462")` -- the Sprinto posting, still saved. Read
   `save_state.observed.candidates`. **Repeat at least twice**, paired with `linkedin_search_jobs`
   as the control, per the standing rule.
3. If it reads `["Unsave the job"]` on every reading, add `"Unsave the job": "saved"` to
   `shape.SAVE_LABELS` **and** `"Unsave the job"` to `dom.SAVE_LABELS_SEEN` -- both, or the
   selector still refuses. `unsave_job` acquires its anchor with no other code change.
4. Two guards will go red at that edit, by design. They are the ones that exist to make the change
   deliberate; update them in the same commit rather than around them.

Cost: **zero writes.** That is the whole point of the route.

### On the one reading that exists

The label reported by the operator's save was `"Unsave the job"`. Two things about it, kept
separate because they are different strengths of claim:

* **The string is ONE reading and stays that way.** Not re-measured, not shipped.
* **Its MEANING, if the string holds, is well-supported by evidence already on disk.** The measured
  row `"Save the job" -> not_saved` establishes that this control's accessible name is the
  IMPERATIVE ACTION, not the state. `"Unsave the job"` fits that convention exactly and names its
  own inverse -- which is why `_audit/2026-08-30-save-label.md` ruled it unambiguous where `Saved`
  is not. And independently: `jobs_tracker_empty.html`, a SAVED-tab capture in this repo, draws
  LinkedIn's own bulk action as **`Unsave`**, so "Unsave" is measurably LinkedIn's word for
  removing a save.

That reasoning is why I am confident about the mapping and still did not ship it. The mapping is
not the risk; **the string is.** A label mapped correctly is worthless if the label is wrong, and
one reading of a page cannot establish a string in a repo that has been burned five times today by
exactly that.

---

## 4. Tests, and the three that could not fail

**29 new tests** across two modules. Every one was driven against a mutation of the thing it
protects. Full transcripts: `mutations.md`, `mutations2.md`, `mutations3.md` in this session's
scratchpad.

### The red reproduction for gap 2

`test_the_refusal_the_operator_saw_now_says_when_it_looked` drives the **real** `linkedin_saved_jobs`
over a DERIVED shell through a real DOM -- real readiness wait, real anchor walk, real harvest JS
returning a real zero. Against the pre-fix refusal (the `tracker_read_note` term deleted), the
first three assertions pass and the fourth is the red:

```
    assert "no saved jobs could be read" in message      # passes
    assert "Saved tab says 1" in message                 # passes
    assert "no empty state was drawn" in message         # passes
>   assert "WHAT WAS ON THE PAGE" in message, message
E   AssertionError: no saved jobs could be read, and the page does not corroborate an empty
E   list: LinkedIn's own Saved tab says 1, and no empty state was drawn. Reporting nothing here
E   would be indistinguishable from you genuinely having none, so it is reported as a failure
E   instead.
```

That message is the operator's live failure, character for character.

### The red reproduction for gap 1

Dropping the `observed` sweep from `_read_save_control_state`:

```
E   AssertionError: 'observed' not in {'state': 'unknown', 'why': "no save control rendered in
E   a state this reader recognises..."}
```

And the mutation that matters most -- hand-adding the unmeasured row, the change a future session
will be tempted to make. **Three guards across two files** go red:

```
E   AssertionError: assert {'Save the jo...job': 'saved'} == {'Save the job': 'not_saved'}
E     Left contains 1 more item:
E     {'Unsave the job': 'saved'}

E   AssertionError: assert 'Unsave the job' is None
E    +  where 'Unsave the job' = anchor_label_for(WriteSpec(action='unsave_job', ...))
```

The second is the sharp one: the hand-added row **silently arms `linkedin_unsave_job` with a live
click anchor**, because `anchor_label_for` reads the table backwards. That is the mechanism working
as designed, caught by a guard rather than by a reviewer.

### THREE GUARDS SURVIVED THEIR OWN MUTATION. All three are now repaired.

This is the part of the wave I would most want a successor to read. Each was found by running the
mutation, never by reading the test.

**(a) The `main` scoping was unguarded.** Dropping `main ` from the anchor walk -- or from
`TRACKER_ROW_LINK` -- left **every test in the file green**. The reason is the corpus, not the code:
both tracker captures keep every anchor inside the single `<main>` (shell 2/2, empty 2/2, row 6/6
identical under both selectors), so the two selectors cannot disagree. A real LinkedIn page carries
a nav that links to jobs. Repaired with a derived page that does too, carrying a `/jobs/view/` href
**outside** `<main>` so a dropped scope shows in BOTH numbers.

**(b) The privacy guard covered one branch of three.** `shape._tracker_evidence_sentence` has three
returns. Driven over the row capture alone it only ever reached the `rows_matching > 0` one, so a
leak planted in the final branch was invisible -- **and that final branch is the one the operator's
real refusal renders.** Repaired by parametrizing over a second derived page: rows drawn under a
link shape this reader does not match, the only way to have real row text present AND a zero row
count. That page earns its keep twice -- it is also the live suspect from section 1, and
`test_rows_drawn_under_another_link_shape_are_not_a_page_that_never_drew` now pins the one reading
that would tell it apart.

**(c) A docstring named an unreachable mutation.** `test_an_ambiguous_label_is_reported_without_
being_resolved` claimed it was shown failing by mutating `shape.save_state`'s unrecognised-label
branch. Measured: it stays green. `dom.SAVE_CONTROL` is built from a one-string `SAVE_LABELS_SEEN`,
so a page wearing any other label matches ZERO elements and `save_state` returns from its
`count == 0` guard, **never reaching that branch at all**. It is unreachable through this route
today. The docstring now says so, and names the mutation a future session would actually reach for
-- promoting a lone observed candidate to a state -- which takes two tests red:

```
E   AssertionError: {'state': 'saved', ..., 'observed': {'candidates': ['Saved'],
E   'matched_total': 1, ...}}
E   assert 'saved' == 'unknown'
```

**Two docstrings also quoted a failure their named mutation cannot produce.** Both claimed "shown
failing against the unfixed production code"; reverting the commit removes
`dom.TRACKER_LIST_TIMEOUT_MS`, so both tests die in their own `monkeypatch.setattr` line before
reaching the assertions they quote. Both now name the narrow mutation that does produce the quoted
text. A third had predicted counts that were simply wrong (`[1, 1, 4]`; measured `[1, 2, 4]`).

One mutation I briefed was itself bad rather than survived, and the record says so: it leaked the
text of the *last* anchor (`"Add note"`, page chrome) rather than a row's, so it could not reach the
strings the guard hunts for. Re-run against the right anchor, the guard goes red as documented.

### The repo caught me once

The first draft of the `linkedin_job_detail` docstring failed
`test_no_docstring_claims_a_write` -- an unnegated `save` inside the phrase *"save-worded accessible
names"*. A read tool's docstring may say what it cannot do; it may not claim a write. **The wording
changed; the guard was not touched and no exemption was declared.**

---

## 5. Receipts

**Suite.** `venv\Scripts\python.exe -m pytest -q`

* In: **1944 passed** (the brief's number, and what I measured).
* At `1b09fbd`, before this audit was tracked: **1977 passed, 0 failed**, in 540.59 s.
* **At final HEAD, with this audit tracked: 1979 passed, 0 failed**, in 532.88 s.
* The delta is 35, not 29, and the extra six are not tests I wrote:
  `test_no_committed_identity` and `test_path_hygiene` are parametrized over TRACKED files, so
  each newly committed file adds two cases. Three files (two test modules + this audit) x 2 = 6.
  29 + 6 = 35. Anyone re-deriving the delta by subtraction should expect that gap rather than
  read it as coverage from nowhere.

**`_state/` untouched.** Byte-identical at wave open and close:

```
before  sha256 f0892e35688868fa...  7813 bytes  Aug 26 00:41
after   sha256 f0892e35688868fa...  7813 bytes  Aug 26 00:41
```

(Digest printed as a 16-character prefix, not in full: further into it sits a run of ten decimal
digits that `test_no_committed_identity` cannot tell from an Indian mobile number, and it refused an
earlier wave's audit for exactly that. Re-derive with `sha256sum _state/session.json`.)

**The Chrome profile was never launched from a script.** Every offline reading was taken by the test
suite's own local headless Chromium over frozen local HTML -- no profile, no network. Every live
reading went through the already-running MCP server, one process, pid 9028, `42a68aa`, confirmed
unchanged at wave close.

**No `confirm_token` was passed to anything.** No write was performed or attempted. The write tools
were called zero times, in preview form or otherwise.

**Commits**, on `master`, **not pushed**, no `Co-Authored-By`:

| sha | what |
|---|---|
| `c7de11a` | `fix(tracker): wait for the list, and say what the page held` |
| `7591ed6` | `test(tracker): three guards that could not fail, and now can` |
| `ab14f2f` | `feat(job-detail): a read-only route to the save control's label` |
| `1b09fbd` | `test(save-state): name a mutation the guard can actually catch` |

Files: `linkedin_server/dom.py`, `linkedin_server/shape.py`, `linkedin_server/server.py`,
`linkedin_server/writes.py`, `tests/test_tracker_readiness.py`,
`tests/test_job_detail_save_state.py`. **All ASCII-clean**, verified by byte scan.

**Tree clean at `1b09fbd`.** No `_TEAM_LEAD_*.md` ruling was present at the worktree root or its
parent at any point in this wave.

**One working-tree note, no action needed.** `core.autocrlf=true` and there is no `.gitattributes`,
so `git checkout --` (used to revert every mutation) normalises working files to CRLF. Four
production files were LF on disk before the mutation runs and are CRLF after. The committed blobs
are LF-normalised and unchanged; `git diff` against HEAD is empty; the files are now in git's
canonical working form for this repo.

---

## 6. The debt, with its address

| debt | what would close it | cost |
|---|---|---|
| **`unsave_job` still has no anchor** | restart the server, `linkedin_job_detail("4423880462")` twice with a search control, read `save_state.observed.candidates`, then add the row to BOTH `shape.SAVE_LABELS` and `dom.SAVE_LABELS_SEEN` | zero writes, two reads |
| **The Saved tab's real cause is unknown** | the next live `linkedin_saved_jobs` failure now prints `anchors_total` / `rows_matching` / the readiness verdict / the settle branch. Many anchors + zero rows + a resolved list = a renamed row link. Few anchors + an unresolved list = a page that did not draw | one call, after a restart |
| **No populated SAVED-tab capture exists** | the row parser and the row selector were both built against a DRAFT row. A capture of the Saved tab **with the Sprinto row in it** would settle the suspect outright, and it is the single highest-value artefact this surface is missing | a capture run, operator-driven |
| **`shape.save_state`'s unrecognised-label branch is unreachable** | it needs `SAVE_LABELS_SEEN` to hold a name `SAVE_LABELS` does not map. It becomes reachable the moment step 3 above is done in the wrong order -- SEEN widened without LABELS. Worth knowing before that edit, not before | nothing; a note |

**On the third row.** If the lead wants gap 2 genuinely closed rather than instrumented, that
capture is the shortest path, and it is worth more than any further reasoning from here: every
theory in section 1 is a theory precisely because nothing in this repo has ever seen a saved row.
