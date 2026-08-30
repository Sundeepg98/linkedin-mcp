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

---
---

# Part 2 -- the row went in, and one gap closed while another was named

**Commits:** `75d27ae`, `b9b55ec` on `master`, **not pushed**.
**Baseline in:** 1979 passed. **Baseline out:** 1986 passed, zero failures.
**`_state/` unchanged.** No `confirm_token` passed to anything; no write performed.

---

## 7. The re-measurement Part 1 said was missing

The lead restarted the server onto `b710b1d` -- the build carrying the read-only route
Part 1 shipped -- and called `linkedin_job_detail(4423880462)` twice, sixty seconds apart. I
then read it a third time, later, and confirmed the process was the same one throughout
(pid 17900, `build.code.commit b710b1d36991`, `dirty: false`).

| # | when | route | reading |
|---|---|---|---|
| 1 | ~18:30 | `writes.perform` gate-5 sweep, on the redeemed save | `newly_observed_save_label: "Unsave the job"` |
| 2 | 21:03 | `linkedin_job_detail` -- pure read, no token | `candidates: ["Unsave the job"]` |
| 3 | ~21:04 | same route, repeated | identical |
| 4 | 21:36 | same route, mine | identical, `main_buttons_total: 32`, `scan_complete: true` |

**Four observations, two independent routes, three of them costing no write.** Reading 4
matters for a reason beyond repetition: 32 buttons drawn against the 1-3 this surface was
returning earlier that afternoon, so it is not a reading taken off a page that had barely
rendered.

**That was the condition Part 1 set, and it is met.** `shape.SAVE_LABELS` gains
`"Unsave the job" -> saved`; `dom.SAVE_LABELS_SEEN` gains the mirror. Both, together -- the
selector is built from the second and the meaning from the first, and widening one alone
makes `save_state`'s unrecognised-label branch reachable with a control the reader can see
and cannot name. `test_the_selector_and_the_vocabulary_cannot_drift_apart` is the one test
in this suite written FOR this edit, and it was left untouched.

### Which label it was mattered as much as that one was measured

The measured OFF row establishes that this control is named for the ACTION it performs, not
the state it is in. `"Unsave the job"` obeys that convention and names its own inverse.
`"Saved"` -- the other spelling this repo named as plausible -- would not: it reads equally
as a state and as an imperative, and a label mapped to the wrong state points a click at the
opposite action. **Had the measurement come back `"Saved"`, the row would still be missing.**

That is not a remark. It is `test_an_ambiguous_label_is_reported_without_being_resolved`,
which still drives a page wearing `"Saved"`, still gets `unknown`, and asserts that the
string is not in the table.

---

## 8. What the row actually unlocked -- measured, not assumed by symmetry

The lead asked for this to be tested deliberately rather than inferred. It was worth it: two
of the four answers are not what symmetry predicts.

| claim | verdict |
|---|---|
| `anchor_label_for` resolves for `unsave_job` | **YES.** Returns `"Unsave the job"`. No code changed -- the indirection absorbed it, exactly as its docstring had promised for a month. |
| `unsave_job` goes from always-refusing to refusing-only-on-an-unrecognised-state | **YES.** Pinned by `test_unsave_refuses_from_a_state_it_cannot_read`, driven over a control renamed off the vocabulary. |
| `save_job` REFUSES on an already-saved posting | **YES, and this could not be tested before today.** |
| `unsave_job` is now reachable end to end | **NO. It is capable and still blocked, and not for its own reason.** |

### The toggle hazard, reachable for the first time

`test_save_refuses_on_a_posting_that_is_ALREADY_saved` is the most important test added by
this wave, and it is worth being precise about why it is NEW rather than a rename.

Until the ON label was in the table, a saved posting read as `unknown`, so gate 5 refused a
save on it **for want of a reading** rather than because of one. The refusal looked right and
rested on nothing. It now refuses on a MEASURED state -- `'saved'` against a spec valid only
from `'not_saved'` -- which is a materially stronger claim.

Shown failing by neutralising the one comparison that carries it, `writes.py:4059`
(`if live_state != spec.from_state or not selector:` becomes `if not selector:`):

```
>       with pytest.raises(WriteAttemptError) as caught:
E       Failed: DID NOT RAISE WriteAttemptError
```

`perform` ran to completion with nothing downstream catching it. **That single comparison is
the whole of what stands between a confirmed save and an unsave.**

### The blocker that outlived the anchor

`unsave_job` has its anchor and still cannot be previewed. Its spec declares
`state_from="saved_list"`, so `observe` reads the Saved tab for its DIRECTION -- and that read
is the one measured broken in section 1. `_read_saved_state` returns `unknown`, and
`_direction` refuses on an unknown origin before any token is minted.

So the refusal moved one gate EARLIER, and a reader who meets it should go and fix the tracker
read rather than go looking for a label. Pinned by
`test_unsave_cannot_be_PREVIEWED_while_the_saved_list_cannot_be_read`, which also asserts that
nothing redeemable was left behind (`writes._GRANTS == {}`).

**I attempted to confirm this live and was denied**, as the lead predicted: a token-free
`linkedin_unsave_job` preview -- a read by construction -- was refused by the permission
classifier. Not worked around. The fact is pinned offline instead, which is the more durable
place for it.

---

## 9. Gap 2 named its own cause, for free

The lead's instruction was not to chase this unless the row work surfaced it. It surfaced on
the first call: the instrument Part 1 built printed the answer.

```
WHAT WAS ON THE PAGE: a <main> carrying 256 characters, 8 links, and 4 of them ARE job-row
links. So the rows drew and the harvest still returned none -- that is the card walk or the
row parser, not the page and not the timing. The navigation settled on the
'networkidle_timed_out' branch after 7012ms, and the list DID resolve (102ms), so the page
had drawn by the time it was harvested. This is therefore a HARVEST problem rather than a
timing one, and re-reading will return the same answer.
```

Read twice, minutes apart, byte-identical but for the settle timing (7012ms/7015ms, list
resolved 102ms/70ms).

**Three things are now settled that were open at the end of Part 1:**

1. **It is not timing, and it is not the settle.** The navigation took the SLOW branch -- seven
   seconds -- and the list resolved in under 102ms. The readiness wait fired and passed.
2. **The rows DRAW, and their links are `/jobs/view/` links.** Four of them. This **kills the
   leading suspect from Part 1** -- the renamed-row-link theory -- outright. `rows_matching`
   was built to separate exactly these two cases and it did.
3. **`harvest_linked_cards` returns nothing from a page carrying four matching anchors.** That
   is the defect, and it is one function further in than anywhere this investigation had
   looked.

A supporting oddity, unexplained and recorded: `<main>` carries only **256 characters** while
holding 8 links. The empty capture carries 323 and the row capture 559. So the tab strip's text
is present and the row's text is not, on a page whose row anchors ARE present -- consistent
with rows attached but not laid out, which `innerText` would not return and
`state="attached"` would not exclude. **That is a hypothesis, not a finding, and it is the
first thing the next wave should test.**

**What my own instrument cannot do**, stated because it is the limit of what section 9
establishes: the note says "the card walk or the row parser" and it cannot separate the two.
It reports DOM anchors, not how many records the harvest returned or how many the parser
dropped. The next increment is `records_harvested` and `dropped` beside `rows_matching`.

Per the lead's instruction the cause was not chased further and nothing was built for it.

---

## 10. The prose sweep, and why it was one commit

A census over the whole repo found **61 sites** the new row falsified or misled: 52 that became
FALSE, 9 that became misleading. They are corrected in the same commit as the table, and that
is a deliberate sequencing call rather than a large diff: four assertions couple a production
message to a test that asserts its text, so moving prose and test separately would leave an
intermediate commit that reads as a regression.

**Every reversal QUOTES the sentence it replaces.** That is the convention already in force in
this repo -- the apply paragraph took it on 2026-08-25, the seven-that-refuse paragraph on
2026-08-30 -- and it exists because the alternative is a codebase that has always said the
comfortable thing.

The highest-leverage one is not in a docstring. It is the `instructions=` block on the
`FastMCP` constructor, which a client renders as the whole server's description and which an
assistant answers questions FROM. It read *"linkedin_unsave_job currently refuses to act at
all and says why."* A stale denial there is repeated to the operator as fact.

**Historical prose in `_audit/*.md` was deliberately NOT rewritten** -- 16 sites, correctly
past-tense, describing what was true on a date.

---

## 11. Mutation testing, and three more docstrings that lied

Ten mutations, **18 test executions, 18 failures, zero survivals.** Full transcript:
`mutations4.md` in this session's scratchpad. Three docstrings named a red their mutation does
not produce, and were corrected in `b9b55ec`. That is the third time this wave, and the pattern
is worth naming: **a docstring predicting a failure is itself an unverified claim until the
mutation is run.**

**The one worth reading is the `_direction` unknown gate.** Its test claimed
`DID NOT RAISE WriteAttemptError`. Wrong -- the refusal survives, raised by the wrong-state
comparison one gate down catching `'unknown' != 'saved'` on the way past. What the unknown gate
actually defends is the **accuracy** of the refusal: without it, the gate stops saying "the
state came back unknown, go fix the tracker read" and starts saying "you may have wanted the
inverse action", pointing a reader at exactly the wrong repair.

**And the backstop is not general.** `set_open_to_work` takes the multi-state branch, which
returns BEFORE the wrong-state comparison, so for that action the unknown gate is the only
thing between an unreadable origin and a rendered confirm block. No test exercises that; it is
recorded in the docstring so nobody removes the gate on the strength of one action's backstop.

Likewise the `anchor is None` branch does not fail as "DID NOT RAISE": deleting it lets a
`None` anchor reach `dom.save_control_selector`, which refuses it one frame deeper. **The
block's own comment predicted that traceback by function name, in advance, and claimed
diagnostic altitude rather than last-stop status.** Both halves were right, which is the reason
it is kept rather than deleted as redundant now that no shipped action can reach it.

### The guard-versus-dead-code call, made out loud

`perform`'s save-family `anchor is None` branch became **structurally unreachable** by this
change: both save-family actions resolve an anchor, and every other performable action returns
from its own branch above the table lookup. This repo's rule is that a check which cannot fail
certifies nothing, so the call was made deliberately. It stays, its message now describes what
it actually catches -- a table that LOST a row, which is a regression rather than a missing
measurement -- and it is **fired in the suite** by removing the row under a live grant.

---

## 12. Receipts

**Suite.** `venv\Scripts\python.exe -m pytest -q`

* In: **1979 passed** (Part 1's close-out, re-measured).
* Out: **1986 passed, 0 failed**, in 676.94 s.
* The delta is exactly 7 and every one is accounted for: 4 new tests in `test_writes.py`
  (preview blocker, toggle hazard, unsave-on-unrecognised, anchor refusal fired), +1 from the
  unrecognised-label parametrisation going 5 to 6, +1 from the single-label control test
  becoming a two-parameter `test_both_measured_labels_ARE_recognised`, +1 from the ON-label
  test splitting into a saved reading and an inverse check. Retired guards were REPLACED
  one-for-one, so they net zero.

**`_state/` untouched.** Byte-identical at open and close: `sha256 f0892e35688868fa...`,
7813 bytes, Aug 26 00:41. (Prefix only; `test_no_committed_identity` refused a full digest in
an earlier wave. Re-derive with `sha256sum _state/session.json`.)

**No write was performed or attempted.** No `confirm_token` reached any tool. The one write-tool
call made -- a token-free `linkedin_unsave_job` preview, a read by construction -- was denied by
the permission classifier and **not worked around**. `unsave_job` was not fired at the
operator's saved posting, and nothing in this wave touched it.

**The Chrome profile was never launched from a script.** Every offline reading came from the test
suite's own local headless Chromium over frozen local HTML. Every live reading went through the
already-running MCP server, one process (pid 17900, `b710b1d`, clean).

**Commits**, on `master`, **not pushed**, no `Co-Authored-By`:

| sha | what |
|---|---|
| `75d27ae` | `feat(unsave): the measured row, and everything that said it was missing` |
| `b9b55ec` | `test(unsave): three docstrings that predicted the wrong red` |

Files: `linkedin_server/dom.py`, `linkedin_server/shape.py`, `linkedin_server/server.py`,
`linkedin_server/writes.py`, `README.md`, `tests/test_writes.py`,
`tests/test_job_detail_save_state.py`, `tests/test_save_candidates_fixture.py`. **All
ASCII-clean**, verified by byte scan.

---

## 13. What is still open

| debt | what would close it | size |
|---|---|---|
| **The Saved tab cannot be read, and it blocks `unsave_job` end to end** | The cause is now NAMED: rows draw, four `/jobs/view/` anchors are present, and `harvest_linked_cards` returns nothing from them. Leading hypothesis: rows attached but not laid out, so `innerText` is empty where `state="attached"` was satisfied. Needs its own wave with a probe log | a wave |
| **The tracker diagnostic cannot separate the card walk from the row parser** | add `records_harvested` and `dropped` beside `rows_matching`. It currently says "the card walk or the row parser" and means it | small |
| **No capture of a populated SAVED tab, and none of a SAVED posting** | Every fixture predates the first save, so BOTH the ON label and a saved row are modelled by derivation rather than capture. The label is measured live four times, so this is not a correctness gap -- it is the reason offline tests cannot prove the live shape | a capture run |
| **Pre-existing count rot in the prose, NOT caused by this change** | `README.md:5` and its "The three that write" header, `server.py:1` and its module docstring, and `linkedin_server/__init__.py:8` all say three or four writes where **five** ship. `tests/test_server_surface.py` pins the real numbers and derives the word "five" from `writes.PERFORMABLE`. Flagged rather than fixed: out of this wave's scope, and the fix means writing two accurate new table rows | lead's call |
| **`set_open_to_work` has no backstop behind `_direction`'s unknown gate** | Found while mutation-testing something else. Its multi-state branch returns before the wrong-state comparison, so the unknown gate is the only thing between an unreadable origin and a rendered confirm block for that action. No test exercises it | small |
