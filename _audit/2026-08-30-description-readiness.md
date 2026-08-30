# The description readiness wait -- implementing 7.2, and what it cannot yet prove

Date: 2026-08-30. Repo `linkedin`, branch `master`. Follows
`_audit/2026-08-30-jobs-view-reliability.md`, whose section 7.2 specifies this
work, and `_audit/2026-08-30-linkedin-writes.md`, which is the wave before it.

The concurrent agent settled why `/jobs/view/<id>` draws sometimes and not
others: it was never LinkedIn, never throttling, never an expired posting and
never a second reader. **It is a two-branch settle in our own `browser.goto`**,
and the two branches are seven seconds apart. Section 7.2 specified the durable
fix in files that agent deliberately did not touch. This is that fix.

---

## 0. Headline

| what | outcome |
|---|---|
| specification implemented | 7.2 in full, plus all six tests specified in 7.3 |
| new readiness primitive | `dom.wait_for_job_description` -- bounded, one verdict, **three-valued** |
| `SETTLE_MS` changed | **NO.** Not raised, not floored. Section 3 says why |
| read boundary | **UNTOUCHED.** No allowlist pattern, no forbidden substring, no AST digest moved |
| new tests | 16, **every one shown failing** at the mutation it names |
| the anchor | verified INDEPENDENTLY against all five captures before use |
| **re-measurement of `4456021840`** | **DONE.** The operator restarted the server; the posting draws in full, twice. Section 5 |
| the six-day-old anchor | **RETIRED as a risk** -- it attaches on today's live DOM. Section 6 |
| a NEW defect found by the re-measurement | the FOLLOW control is unrendered on both postings tested. Section 8 |
| writes performed | **NONE.** No `confirm_token` passed to anything |

---

## 1. The anchor, re-counted rather than accepted

7.2 said "do not substitute" and gave a table. Taking a selector on trust is
the thing this package refuses to do, so it was re-counted independently before
anything was built:

| capture | `data-sdui-component=...aboutTheJob` | `id="JobDetails_AboutTheJob_<id>"` |
|---|---|---|
| `job_detail_shell` | 0 | 0 |
| `job_detail_following` | **0** | **1** |
| `job_detail` | 1 | 1 |
| `job_detail_hydrated` | 1 | 1 |
| `job_detail_following_hydrated` | 1 | 1 |

Identical to the specification. **The obvious anchor is wrong in the dangerous
direction**: the slot id is drawn before its content, so it is PRESENT on
`job_detail_following` -- the one capture whose description is missing -- and a
wait anchored on it reports READY in precisely the state the wait exists to
detect. The two selectors disagree on exactly one capture, and that capture is
the whole reason the wait exists. That disagreement is now an executable test
(`test_the_slot_id_would_have_been_the_wrong_anchor`), not a sentence.

---

## 2. What was built

**`dom.JOB_DESCRIPTION_SLOT`**, **`dom.JOB_DESCRIPTION_TIMEOUT_MS`** (10 s), and
**`dom.wait_for_job_description(page)`** -- one bounded wait on that selector
attaching, no retry loop, modelled on `dom.wait_for_save_control`.

**It returns a verdict rather than raising**, three-valued:

| `attached` | meaning |
|---|---|
| `True` | the anchor attached; the description is drawn |
| `False` | the wait ran its **full** course and found nothing. A FINDING |
| `None` | the readiness check ITSELF failed. Evidence for NEITHER |

The third value is not decoration. Collapsing it into `False` reports a broken
instrument as a finding about a third party -- and that exact mutation came back
green on first pass in the save wave, which is why
`test_a_locator_failure_is_not_a_timeout` exists rather than a comment saying to
be careful. The dict's **default is `None`**, so a path nobody thought about
cannot arrive claiming to have measured LinkedIn.

**Classified by name, not by class.** `dom.py` has never imported playwright,
and this package already tells a genuine expiry from an instrument failure the
same way (`writes.py:3363`). Python's builtin `TimeoutError`, asyncio's and
playwright's all carry the name and all mean the same thing here.

**`dom.read_job_posting` calls it FIRST**, before `read_job_identity`, and
returns the verdict as `description_wait` beside the existing `main_present` /
`main_chars`. The order is the whole of its value: after the text is read,
waiting for the description spends up to ten seconds to produce a field about a
page that was already parsed. Nothing in the returned dict would look different,
which is why that is pinned as ORDER rather than as output.

**`shape.job_detail_failure_note`** now takes `description_wait` and `settle` as
**REQUIRED** keyword arguments, and delegates to a new
`shape.job_read_timing_note`. Required rather than optional: an optional
argument with a `None` default lets a future caller silently produce the old
note, which is the note this change exists to retire.

**Both call sites pass the evidence.** `server.linkedin_job_detail` passes
`BROWSER.last_settle`; `writes._read_posting_facts` gained a `navigator`
parameter and its three callers in `observe` pass it -- so **the apply and save
confirm gates inherit the fix**, which is the half that matters most, since they
read the same page through the same reader.

### What the refusal can now say, and could not before

| situation | the note now says |
|---|---|
| `attached False` | the wait ran its **full bound** after the settle. Not a read taken too early. Two causes: the posting really did not render, **or LinkedIn renamed the component** -- and it names the action that separates them (try a second posting) |
| `attached None` | the check did not complete, so **nothing here is evidence about LinkedIn**. Re-read |
| `attached True`, fields missing | the page **drew** and the parse still failed. A PARSER problem -- the case the old note's three theories omitted entirely |
| settle unrecorded | says so. It does not print `Nonems`, which would be a fabricated measurement |

The `linkedin_search_jobs` control **survives** the rewrite. It answers a
different question from the readiness wait -- whether the SESSION is healthy,
not whether this page drew -- and dropping advice a test pinned with a measured
reason would have been a real loss.

**One instruction was retired, with its reason.** The old note asked the reader
to "repeat this call", because a single reading of this surface could not be
trusted. That is now fixed at the source, so asking for a repeat of a reading
that already waited is asking for ten seconds to learn nothing. It is replaced
by a better instruction -- try a DIFFERENT posting -- and the retirement is
written into the test that used to assert it.

---

## 3. What was deliberately NOT done

**`SETTLE_MS` was not raised and no floor was added.** The other agent's
reasoning is adopted rather than re-derived: the settle is binary by
construction, so nothing measured through the shipped build can distinguish
"2 s would be enough" from "6 s would be enough" -- every candidate number sits
inside an unmeasured bracket of (1 s, 7 s]. Picking one is the
round-number-that-sounds-safe the brief forbids, and it taxes every surface for
one surface's missing readiness check.

`test_a_ready_page_is_not_delayed` is what holds that: it goes RED at exactly
the cost a floor would impose (`assert 3502 < 2000`).

---

## 4. Every test shown failing

All six mutations from 7.3, plus two of my own. Each was applied by temporary
edit or at runtime, run, then reverted -- and every revert was verified by
sha256 against the value taken immediately before that mutation, followed by a
green re-run. `dom.py` came back to `96341ee5462b0366` after each of its four.

**`shape.py`'s sha is deliberately NOT quoted as a single constant**, and the
reason is worth a line rather than a quiet omission: it changed legitimately
between mutations -- the search-jobs control sentence was restored to the note,
a casing fix landed, and the unknown-branch guard in section 4's last entry was
added -- so a single "restored to X" claim would be false for some of them. Each
revert was checked against its own immediately-prior value.

**Anchor swapped to the slot id** -- two tests fire, and the second is the one
that matters:

```
E  AssertionError: {'job_detail_shell': 0, 'job_detail_following': 1, ...}
E  assert [0, 1, 1, 1, 1] == [0, 0, 1, 1, 1]
E    At index 1 diff: 1 != 0
FAILED ..::test_the_description_anchor_separates_drawn_from_not_drawn
E  assert True is False
FAILED ..::test_a_page_that_never_draws_the_description_is_reported_not_attached[job_detail_following]
```

The second is the wrong anchor reporting **READY on the capture whose
description is absent** -- the failure the right anchor exists to prevent.

**Bare `except Exception: attached = False`** (instrument failure reported as a
LinkedIn finding):

```
E  assert False is None
FAILED ..::test_a_locator_failure_is_not_a_timeout
```

**The wait re-raising instead of returning a verdict:**

```
E  playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 200ms exceeded.
```

**The wait moved below `read_main_text`:**

```
E  AssertionError: ['read_main_text', 'wait']
E  assert 'read_main_text' == 'wait'
```

**An unconditional `wait_for_timeout(3500)` floor substituted for the element
wait** -- the mutation section 3 forbids:

```
E  AssertionError: 3502
E  assert 3502 < 2000
```

**Either piece of timing evidence dropped from the note** -- a TypeError rather
than a quieter, weaker sentence, which is the point of making them required:

```
TypeError: job_detail_failure_note() missing 1 required keyword-only argument: 'settle'
TypeError: job_detail_failure_note() missing 1 required keyword-only argument: 'description_wait'
```

**`if attached is None:` in place of `is not True and is not False`** -- a guard
written the obvious way, which lets any stray value reach the branch that says
the page rendered:

```
E  AssertionError: ('unknown', "The navigation settled on the
   'networkidle_resolved' branch after 4ms, and the description DID attach ...")
E  assert 'nothing here is evidence' in "... the description DID attach (0ms),
   so the page had drawn by the time it was parsed. ..."
FAILED ..::test_a_verdict_that_is_neither_true_nor_false_is_treated_as_unknown
```

That is a confident claim about LinkedIn manufactured out of a local typo --
the same failure class as the read-too-early refusals, one level down.

---

## 5. The re-measurement of `4456021840` -- BLOCKED, then DONE

**It was blocked, and it was not faked.** At the time this fix was written,
`linkedin_server_info` reported the running process at `d0d3e3b65d52` against a
checkout at `0767eb63f7b9` -- **seven commits stale**, holding neither this
readiness wait nor `last_settle`. A call then would have exercised exactly the
code that produced the suspect finding, using a field that was not in the
process. Running it and calling the result a re-measurement would have repeated
the error it was meant to check, so no page loads were spent on it.

**The operator then restarted the server**, and `linkedin_server_info` confirmed
the process at `0767eb63f7b9` with `dirty: true, dirty_files: 6` -- the working
tree, including this readiness wait, loaded. Corroborated independently by the
payload rather than by the version string alone: `writes_available` now lists
`follow_company`, and `known_side_effects` carries the messaging and
`/mynetwork/` entries that only exist in the uncommitted tree.

### What the re-measurement found

**`4456021840` DRAWS IN FULL.** Title, employer, location, workplace type,
employment type, applicant count, hiring status and a description of roughly
2,200 characters. Read **twice consecutively; the two readings are identical**.

**The old conclusion is retired.** "3 buttons under `<main>` and no save control
after a 10 s wait" was taken on a page that had barely begun -- the read landed
on the fast settle branch, and the 10 s save-control wait started against a
document LinkedIn had not filled in. The posting was never broken. **Nothing
about that finding is carried forward.**

Worth noting what the two identical readings mean on this surface specifically:
this is the page whose single readings were "measured disagreeing with
themselves an hour apart". Two consecutive agreeing readings is the readiness
wait doing the job it was specified for.

## 6. The residual risk I introduced -- RETIRED by measurement

When this was written the honest statement was: **the anchor is measured against
captures taken 2026-08-24, six days old, and not against today's live DOM.** If
LinkedIn had renamed that SDUI component, the wait would match nothing on any
posting and every `linkedin_job_detail` call would fail identically -- which
looks exactly like an outage. That is the failure mode 7.2 itself flags, and it
is why the `attached False` refusal names a rename as a live possibility.

**It is retired, and by the cheapest possible evidence.** Both live readings in
section 5 returned a full description. `read_job_posting` runs the readiness
wait FIRST and unconditionally, so a description that parses is a description
whose anchor attached: had the component been renamed, the wait would have spent
its full ten seconds and the refusal would have fired instead. Two postings,
three readings, no refusal.

**The anchor is now verified against today's live site as well as against all
five captures.** Those were different claims, and both are now made.

## 7. Run record

**Full suite: 1940 passed, 0 failed.** `venv\Scripts\python.exe -m pytest -q`,
Python 3.13.14. Baseline before this work was 1924; the 16 added are the file
in section 4.

**`_state/`** -- nothing in this work read, wrote or opened it.
`session.json` is byte-identical: size 7813, sha256 first 32
`f0892e35688868faef6a3525e54b93e4`, mtime 2026-08-26 00:41:24.087579.

**Three page loads were spent, all reads, all after the restart** and all
reported rather than folded away: `linkedin_job_detail` twice on `4456021840`
and once on `4447654264`. The browser was launched by the SERVER to serve them,
which is the sanctioned path every read tool uses; **no browser was launched
from a script**. No `confirm_token` was passed to anything.

**The read boundary did not move.** No allowlist pattern, no forbidden
substring, no new click, no injected script -- `wait_for_job_description` is a
locator chain, so `test_readonly.py`'s `INJECTED_SCRIPTS` needs no new entry.

**Files touched:** `linkedin_server/dom.py`, `linkedin_server/shape.py`,
`linkedin_server/server.py`, `linkedin_server/writes.py`,
`tests/test_save_candidates_fixture.py`, and the new
`tests/test_job_description_readiness.py`. All LF, all pure ASCII, no
`Co-Authored-By`.

---

## 8. A DEFECT THE RE-MEASUREMENT FOUND, in work shipped earlier today

The re-measurement was aimed at the description. It also produced a finding
nobody was looking for, and it is about a capability I made performable four
commits ago.

### The measurement

| posting | description | `apply_path` | `company_follow_state` |
|---|---|---|---|
| `4456021840` (read 1) | **drawn in full** | `unknown` | **`unknown`** |
| `4456021840` (read 2) | **drawn in full** | `unknown` | **`unknown`** |
| `4447654264` | **drawn in full** | **`linkedin_apply`**, with destination | **`unknown`** |

Two things fall out, and they are different.

**The apply reader is not broken.** It resolved a full route on `4447654264`
seconds after returning `unknown` twice on `4456021840`, in the same session.
So that posting's `unknown` is a property of the posting, not a race -- which is
exactly what the control this package prescribes ("call a second posting") is
for, and it is the first time that instruction has actually been executed.

**THE FOLLOW CONTROL DID NOT RENDER ON EITHER POSTING.** Three readings, two
postings, `unknown` every time.

### Why that matters more than it looks

`follow_company` was moved into `writes.PERFORMABLE` in commit `050349f`, and
its gate reads the direction off `dom.FOLLOW_CONTROL` on the posting page. Gate
5 refuses on anything that is not the exact measured state. So on this evidence
**every follow preview would refuse with `unknown`, and the capability is
effectively unreachable in practice.**

**The design is behaving correctly** -- it refuses rather than clicking a
control it cannot see, which is the whole point of the gate, and no wrong action
is possible. But "sanctioned, performable, and refuses every time" is not what
shipping it was meant to mean, and reporting it as delivered without this
paragraph would be the stale-claim failure this package keeps finding.

### It is the same defect, one layer over, and the fix is the same primitive

`read_job_posting` now waits for the DESCRIPTION. Nothing waits for the CONTROL
LAYER, and this measurement shows the two hydrate on different schedules: a page
can carry 2,200 characters of drawn description and still have no follow button.
`browser.goto`'s own comment already records the control half of it -- "measured
2026-08-23, the same posting drew no control before it settled and Following
after" -- so this is a race that was observed a week ago and never given a wait.

The fix is `dom.wait_for_job_description` pointed at `dom.FOLLOW_CONTROL`: same
shape, same three-valued return, roughly twenty lines. The captures support it
(`job_detail.html` and `job_detail_following_hydrated.html` each carry one follow
control), so the anchor is measured and the wait would be waiting for something
known to exist.

**NOT BUILT HERE, and deliberately.** The task was 7.2, which specifies the
description. Extending a fix into a second reader on my own initiative is scope
I should be asked for rather than take -- and there is a real question inside it
that a measurement should settle first: whether the apply and follow controls
want ONE readiness wait or two, given that on `4456021840` the apply control may
genuinely be absent rather than late. Filed here with its evidence so it is a
decision rather than a hole.
