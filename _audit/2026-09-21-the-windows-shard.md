# The Windows shard: a 60-second `set_content` reported as `KeyError: 'fields'`

Wave: the-windows-shard. Branch: `worktree-agent-a6ae0b6c8c4103168`.

Master went RED on CI run 35592629243 at commit `f729a2a`, in exactly one of
twenty jobs: `pytest (windows-latest, py3.13, shard 3)`. Linux py3.10, Linux
py3.13 and the other five Windows shards all passed. Two things went wrong and
they are different in kind: the suite MISREPORTED the failure, and something
made a local `Page.set_content` take longer than sixty seconds.

## THE ANSWER, UP FRONT

**DEFECT 1 -- FIXED AND SHOWN.** `tests/test_editor_fields.py` states a
convention (`.get` with the whole result as the message) in a comment, and the
function immediately below that comment broke it. A Playwright timeout was
reported as `KeyError: 'fields'`. Every read of `"fields"` now goes through
`fields_of`, which quotes the envelope in the HEADLINE. The sweep found a
SECOND instance of the same shape nobody had reported -- `by_label` in
`tests/test_editor_values.py`, whose docstring promises "a loud failure" while
raising `KeyError` before either of its loud assertions runs. Both fixed;
defect set re-measured at 0.

**DEFECT 2 -- BOTH HYPOTHESES REFUTED. H1 no, H2 no.**

* **H2 is refuted.** All 47 changed lines in `linkedin_server/server.py` are
  docstring and comment prose. The module's AST with docstrings stripped is
  IDENTICAL across all three commits, and `tests/test_editor_fields.py` is
  unchanged since the last green run. Proven with an instrument shown flipping
  its verdict on a one-token mutation.
* **H1 is refuted as stated, in the direction nobody expected.** The failing
  file was in shard 3 at BOTH commits -- it did not move -- and its browser
  company SHRANK from six files to five. The new test file the merge added
  constructs no browser at all. H1's MECHANISM is real, though: 25 of shard 3's
  35 files turned over and it became the heaviest shard by 42%.
* **The cause is resource exhaustion, and it is proven non-code by a
  comparison nobody designed.** Attempt 1 and attempt 2 of the SAME run are the
  same commit, plan, files and command. Attempt 1's parallel phase took
  **343.34s and failed**; attempt 2's took **110.74s and passed**. A 3.1x
  degradation with the code held byte-identical.
* **And it was not simply a slow machine.** Attempt 1 was ~1.7x FASTER at
  single-threaded work (12.74s vs 21.35s collection) and 3.1x slower in
  parallel. The degradation is specific to running many things at once.

**WHAT IS NOT ESTABLISHED, stated plainly:** WHY the parallel phase degraded --
worker count, memory pressure or a noisy co-tenant. The logs cannot separate
them because **no shard job records how many workers `-n auto` resolved to, the
runner's CPU count, or free memory.** That one-line measurement is named in 7.1
and deliberately NOT made, because `ci.yml` is the most-shared file in the repo
and five other waves were live.

**THE FIX FOR DEFECT 2 IS NOT A LARGER NUMBER.** The timeout is still 60000ms,
nothing is retried, nothing is marked flaky. What changed is that when it fires
it takes the DISCRIMINATING reading -- how long an empty document takes on the
same browser in a fresh context -- which separates "the box was starved" from
"this document hung". Shown working on a real forced timeout (5.3). That
control also caught the first version of the discriminator blaming the machine
for what the markup did.

**A HYPOTHESIS OF MY OWN, REFUTED (4.3):** the packer prices the failing file
at 16s and it measures 179s, which looks like a smoking gun. It is not
supported -- on this box a two-test static guard is 29x over its table entry,
higher than any browser file. This box cannot separate a wrong table from a
loaded machine. Recorded rather than dropped.

---

## 0. THE FULL FAILURE, AS THE LOG HAS IT

The run is still an open object at the time of writing, so the numbers below are
stamped with where they came from.

`gh run view 35592629243 --log-failed` does NOT work on this run: the run was
re-run and is IN PROGRESS, and gh answers

    run 35592629243 is still in progress; logs will be available when it is complete

which is why every quotation below comes from the ATTEMPT-1 job log, fetched by
job id rather than by run:

    gh api repos/<owner>/linkedin-mcp/actions/runs/35592629243/attempts/1/jobs
    gh api repos/<owner>/linkedin-mcp/actions/jobs/106310214301/logs

Attempt 1's only failing job is id `106310214301`, started 11:10:23Z, completed
11:21:43Z. (The job id `106315070960` that `gh run view` prints is ATTEMPT 2's
job, not the one that failed.)

### 0.1 The re-run: it started, and it had not concluded

The brief asked me to verify rather than assume. Measured, not relayed:

    gh api .../runs/35592629243 --jq '{status,conclusion,run_attempt}'
    {"conclusion":null,"run_attempt":2,"status":"in_progress"}

So: the re-run DID start, it is attempt 2, and at the time of that measurement
it had reached no conclusion. Its outcome is recorded in section 6 with its own
timestamp. Whatever it concludes, a second sample is evidence about frequency
and not about cause, and nothing in this document rests on it.

### 0.2 The failure itself

    ____________ test_a_label_the_census_refuses_comes_back_named_here ____________
    [gw3] win32 -- Python 3.13.15

        result, _ = await run_tool(RELAXED_HTML)
    >   published = names_of(result)
                    ^^^^^^^^^^^^^^^^

    tests\test_editor_fields.py:347:
    _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

    result = {'error': 'unexpected', 'message': 'TimeoutError: Page.set_content:
    Timeout 60000ms exceeded.\nCall log:\n  - setting frame content, waiting
    until "domcontentloaded"\n'}

        def names_of(result: dict[str, Any]) -> list[str]:
            """The published label of every control in the answer, in document order."""
    >       return [field["name"] for field in result["fields"]]
                                               ^^^^^^^^^^^^^^^^
    E       KeyError: 'fields'

    tests\test_editor_fields.py:323: KeyError
    1 failed, 2108 passed, 1 skipped, 1 xfailed in 343.34s (0:05:43)

Three facts from the same log that matter later:

* the shard ran `python -m pytest -q -rs -n auto --dist loadfile $(cat shard-files.txt)`;
* the shard's own plan, printed by the job, was 35 files / 2111 tests, out of
  `collected_total` 7962 across `files_total` 208;
* the completeness guards were GREEN on this red run -- `collected 2111 |
  reported 2111 | executed 2110 | skipped 1 (1 declared)`. Nothing went missing.
  This was a failing test, not a lost one.

Runner image: `windows-2025-vs2026`, version 20260907.229.1. The playwright
cache HIT (`Cache restored from key: playwright-Windows-1.63.0`), so the browser
binary was present and the 3m42s install step was not a download stall.

---

## 1. DEFECT 1 -- the failure message named the wrong thing

### 1.1 The contradiction, verified against the file

The brief asked me to confirm this reading rather than act on it. Confirmed --
and the two halves are ADJACENT, not merely in the same file.
`tests/test_editor_fields.py` lines 311-323, unbroken:

    #: ``.get("refused")`` rather than ``result["refused"]`` in every refusal check
    #: below, and that is about the FAILURE TEXT rather than about strictness. A
    #: subscript on a result that stopped refusing raises ``KeyError: 'refused'``,
    #: which says nothing about what the tool returned instead; ``.get`` with the
    #: whole result as the assertion message prints the answer a caller would have
    #: received. The check is exactly as strict either way -- ``None`` never equals
    #: a refusal code -- and every one of these is paired with an assertion that
    #: ``"fields"`` is absent, which is the half that would actually be dangerous.
    def names_of(result: dict[str, Any]) -> list[str]:
        """The published label of every control in the answer, in document order."""
        return [field["name"] for field in result["fields"]]

The comment states the module's convention and gives the reason. The function
immediately underneath it is the one place in the module that breaks it.

The convention's own words predicted this exact outcome: a subscript "says
nothing about what the tool returned instead". What the tool returned instead
was a Playwright timeout, and recovering that cost a reader one trip to the log
line above the traceback -- a line that is only there because pytest happens to
print the local variables of the frame.

### 1.2 Why the comment did not cover its own helper

The comment scopes itself to "every refusal check BELOW" -- the paths where the
tool is expected to REFUSE. `names_of` is the success path, and nobody extended
the reasoning to it, even though the reason given (print what came back instead)
is not specific to refusals at all. The convention was written for the case
somebody was thinking about.

The census in section 4 settles that this is the whole story and not a guess:
across this module there are ZERO raw subscripts on a refusal key. Every
refusal check does use `.get`. The rule is honoured exactly where it was
written down and nowhere else, and the place it was not written down is the one
that broke the build.

One more thing worth naming, because it is what made the failure expensive
rather than merely ugly. Both renderings "fail". `result["fields"]` was never
too permissive, and pytest did print the envelope -- as a local-variable dump
above the traceback. What was wrong was the HEADLINE: the last line of the
traceback, the line in the job summary, the line a person greps for, said
`KeyError: 'fields'`. The diagnosis was present and unfindable.

### 1.3 The fix

Every read of `"fields"` in the module now goes through one accessor:

    def fields_of(result: dict[str, Any]) -> list[dict[str, Any]]:
        fields = result.get("fields")
        assert isinstance(fields, list), (
            "the tool published no 'fields' list. It returned: %r" % (result,)
        )
        return fields

    def names_of(result: dict[str, Any]) -> list[str]:
        return [field["name"] for field in fields_of(result)]

`assert` rather than `raise` on purpose: pytest renders it as an assertion
failure with the envelope in the headline, which is the entire point. It is an
`isinstance(..., list)` rather than a `is not None` so that a tool answering
`{"fields": None}` or `{"fields": "..."}` is caught here with its envelope
printed rather than three lines later with a `TypeError`.

Nine call sites now route through it -- `names_of` plus the eight direct
`result["fields"]` reads at (post-edit) lines 644, 656, 878, 888, 1029, 1030,
1061 and 1081. The two remaining textual occurrences of `result["fields"]` in
the file, at lines 346 and 469, are PROSE inside a comment and a docstring and
were deliberately left alone.

The module comment was widened in place, carrying the CI envelope verbatim, so
the next reader finds the reason rather than the rule.

---

## 2. DEFECT 2 -- H1 vs H2

### 2.1 A correction to the brief's framing: `f729a2a` is a MERGE with TWO parents

    git log --format='%H %P' -1 f729a2a
    f729a2a...  09b5f17...  6c24426...

The brief named `6c24426` as "its parent". It is the SECOND parent -- the wave
branch that was merged. The first parent is `09b5f17`.

This matters for which comparison is load-bearing, and CI settles it:

    35592629243  f729a2a  in_progress    <- RED (this failure)
    35591484838  09b5f17  success        <- last fully green run
    35586308400  75a1983  success

**CI never ran on `6c24426` at all.** The green-to-red transition is therefore
`09b5f17 -> f729a2a`, and that is the diff a cause must live in. `6c24426` is
computed too, because the brief asked for it, but it is not the transition.

### 2.2 The real change surface, A = `09b5f17` -> C = `f729a2a`

    A  _audit/2026-09-21-what-the-browser-said.md
    M  _audit/INDEX.md
    M  _audit/RULINGS.md
    A  _audit/_slice-reader-guard-subjects.md
    M  linkedin_server/server.py
    A  scripts/_census_quoting_callees.py
    A  scripts/_census_reader_guard_subjects.py
    A  scripts/_check_the_tool_envelope_guard_can_fail.py
    M  scripts/build_rulings_index.py
    M  tests/test_a_correction_is_findable_from_the_claim.py
    A  tests/test_tool_envelopes_emit_no_page_string.py
    A  tests/tool_envelope_baseline.json

Two corrections to the brief here as well:

* the merge adds **two** test-suite changes, not one: the new
  `tests/test_tool_envelopes_emit_no_page_string.py` AND a modification to
  `tests/test_a_correction_is_findable_from_the_claim.py`;
* it adds **seven new tracked files** in total. That is not cosmetic for this
  suite: `tests/test_no_committed_credential.py` parametrises over `git ls-files`
  PLUS `git ls-files --others --exclude-standard`, so every new tracked file
  brings its own test case with it and changes the collection denominator.

And the single most load-bearing fact for the whole of section 2:

    git diff --stat 09b5f17 f729a2a -- tests/test_editor_fields.py
    (empty)

**The failing test file did not change.**

### 2.3 H2 -- REFUTED, by AST rather than by eyeball

H2 says the commit changed what `linkedin_server/server.py` does on the path
this test drives. `server.py` is the only file under `linkedin_server/` that the
merge touched, and its diff is 47 added / 2 removed lines.

A textual diff cannot answer H2, because a docstring rewrite and a behaviour
change look identical to it. So the two revisions were compared AS CODE:
parse both, delete every docstring, compare the ASTs.

Instrument: `scripts/_check_server_ast_is_docstring_only.py` (see section 5).

    WHOLE-MODULE AST, docstrings stripped: IDENTICAL
    top-level defs: A_09b5f17=86  C_f729a2a=86
    defs only in A_09b5f17: none
    defs only in C_f729a2a: none
    defs whose CODE changed: none
    linkedin_profile_editor_fields: UNCHANGED
    EXIT=0

All 47 lines are prose: a docstring on `_error` and a comment block in
`linkedin_premium_job_collection`. **Zero executable change anywhere in
`server.py`**, and the tool this test drives is untouched.

Taken with 2.2 -- the test file unchanged, the server code unchanged -- H2 is
refuted on both ends of the path at once. The test and the code it drives are
byte-for-byte what they were on the last green run.

The control that makes that verdict mean something is in section 5.1.

### 2.4 Where `set_content` actually lives

Worth stating because it narrows the cause. The timing-out call is not in
`server.py` at all. It is in the TEST's own harness,
`tests/test_editor_fields.py` line 276, inside a function-scoped fixture:

    @pytest.fixture
    async def run_tool(monkeypatch):
        playwright = pytest.importorskip("playwright.async_api")
        async with playwright.async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            ...
                async def render(markup: str) -> None:
                    await page.set_content(...)

The fixture takes no `scope=`, so it is FUNCTION-scoped: every test that uses it
starts a fresh playwright driver process AND launches a fresh chromium. 20 of
the file's 35 test functions take `run_tool` (53 tests collected after
parametrisation). The markup is a local string; no network is involved.

---

## 3. THE SHARD PLANS -- H1, COMPUTED

### 3.1 How they were computed, and the trap that shapes the method

The packer is `scripts/ci_shard.py`: greedy longest-processing-time-first, sorted
by `(-weight, path)`, each file into the lightest shard so far, ties to the lower
index. Membership comes from a live `pytest --collect-only -q`; weight comes from
the committed table `scripts/ci_shard_timings.json`, with unpriced files charged
the measured mean seconds-per-test. It is fully deterministic and fully offline.

It cannot be computed in a dirty tree, and that is not a detail. This suite's
COLLECTION COUNT depends on the working tree: `tests/test_no_committed_credential.py`
parametrises over `git ls-files` **plus** `git ls-files --others --exclude-standard`,
so untracked files bring their own test cases. A `git archive` export (no `.git`)
or a worktree carrying scratch files both produce a different denominator than
CI's fresh checkout. So all three plans were computed in a clean local CLONE,
`git clean -xdff` between checkouts, `git status --porcelain` empty each time.

### 3.2 THE VALIDATION CONTROL -- the local packer reproduces CI exactly

Everything in this section is worthless unless the local computation agrees with
the packer that actually ran on the runner. The failing job printed its own
shard-3 plan into the log, so that comparison is available:

      index            CI=3        local=3        MATCH
      of               CI=6        local=6        MATCH
      tests            CI=2111     local=2111     MATCH
      collected_total  CI=7962     local=7962     MATCH
      files_total      CI=208      local=208      MATCH
      files (order)    MATCH
      files (set)      MATCH

      VALIDATION CONTROL: PASS -- the local packer reproduces CI exactly

All 35 paths, in order. The plan at `09b5f17` is therefore trustworthy on the
same terms.

### 3.3 The two plans

    A = 09b5f17 (last green)            C = f729a2a (red)
    collected_total 7937, 207 files     collected_total 7962, 208 files

    shard  files  tests  browser files       files  tests  browser files
      0      32    2003        3               33    1450        5
      1      34     717        5               34    1486        4
      2      34    1580        5               34     884        7
      3      35    1527        6  <-- HERE      35    2111        5  <-- STILL HERE
      4      36     948        8               36     921        7
      5      36    1162        8               36    1110        7

### 3.4 H1 -- REFUTED AS STATED, and refuted in the direction nobody expected

**`tests/test_editor_fields.py` was in shard 3 at BOTH commits. It did not move.**

And its browser company did not grow -- it SHRANK, from six browser-constructing
files to five:

    shard 3 at A (6):  test_apply_modal_fixture, test_browser,
                       test_connections_reader, test_editor_fields,
                       test_newsletter_reader,
                       test_profile_pdf_download_is_blocked_on_transport
    shard 3 at C (5):  test_apply_modal_fixture, test_browser,
                       test_connections_reader, test_editor_fields,
                       test_thread_reply_surface

Four of the five are the same four. So the specific story H1 offered -- "H1 put a
new browser-heavy test beside an existing one" -- is false twice over: the file
did not change shards, and the new file the merge added,
`tests/test_tool_envelopes_emit_no_page_string.py`, constructs no browser at all
(zero occurrences of `playwright`, `chromium.launch`, `set_content`,
`new_context`, `async_playwright`), and did not land in shard 3.

### 3.5 What H1's premise DID do, which is not nothing

The mechanism H1 named is real and it fired hard. Adding files reshuffles LPT,
and **25 of shard 3's 35 files changed between A and C -- a 71% turnover**:

    files 35 -> 35 ; tests 1527 -> 2111 (+584)
    joined: 25 files, 1000 tests   (1 of them browser: test_thread_reply_surface)
    left:   25 files,  423 tests   (2 of them browser)
    stayed-but-grew: test_no_committed_identity.py 753 -> 760 (+7)

The single largest arrival is `tests/test_navigation_is_never_derived.py` at
**519 tests**. Shard 3 went from the third-largest shard by test count to
**the largest by a wide margin** -- 2111 against a 884-1486 range for its five
siblings, i.e. 42% above the next-heaviest.

So the commit did make shard 3 substantially heavier, and it did so through
exactly the mechanism H1 describes. What it did NOT do is change the failing
file's shard or crowd it with new browsers. H1 as a causal story is refuted;
H1 as a description of how this plan moves is confirmed.

---

## 3A. THE CAUSE -- what the two ATTEMPTS prove, which is more than the plans do

Sections 2 and 3 refute both offered hypotheses. What actually settles the
question is the re-run, and not in the way a re-run usually is used.

A re-run that passes is normally worth nothing -- it says an intermittent thing
was intermittent. This one is worth something because it is a CONTROLLED
EXPERIMENT that nobody designed: attempt 1 and attempt 2 are the SAME commit,
the SAME shard plan, the SAME 35 files, the SAME command, the SAME runner
image. Every input this repository controls is held byte-identical. The only
free variable is the machine and what was running on it.

### 3A.1 The numbers

    ATTEMPT 1  job 106310214301   11:10:23Z -> 11:21:43Z   FAILED
    ATTEMPT 2  job 106315070960   11:27:42Z -> 11:34:25Z   SUCCESS

    the pytest step, -n auto --dist loadfile, same 35 files:
      attempt 1:  343.34s   1 failed, 2108 passed, 1 skipped, 1 xfailed
      attempt 2:  110.74s   2109 passed, 1 skipped, 1 xfailed

**The failing run's parallel phase took 3.1x as long as the passing run's.**

### 3A.2 And it was NOT simply a slower machine -- this is the part that matters

The obvious reading is "attempt 1 landed on a slow runner". The single-threaded
steps refute it. Collection is one process, no xdist, no browser:

                              attempt 1 (FAILED)   attempt 2 (passed)
      full-suite collection        12.74s               21.35s
      shard collection              6.00s               12.40s
      pip install step               47s                  35s

**Attempt 1's machine was about 1.7x FASTER at single-threaded work and 3.1x
SLOWER at the parallel browser phase.** A uniformly slow box does not do that.
Whatever went wrong was specific to running many things at once, not to the
machine's raw speed.

### 3A.3 What that leaves, stated as exactly as the evidence allows

ESTABLISHED, with the evidence in this document:

* it is not the code -- `linkedin_server/server.py` is AST-identical across all
  three commits and `tests/test_editor_fields.py` is unchanged since the last
  green run (2.2, 2.3);
* it is not the shard plan -- the failing file did not move shards and lost a
  browser neighbour (3.4), and both attempts ran the identical 35-file plan;
* it is not deterministic at this commit -- the same commit, plan and command
  passed on the retry, and passed locally;
* the failing run was degraded specifically in its PARALLEL phase, by 3.1x,
  while being faster single-threaded (3A.2);
* EVERY OTHER TEST IN THE SAME FILE PASSED IN THE SAME FAILING RUN. The shard
  reported exactly one failure out of 2111, so all 52 of the module's other
  collected tests passed -- including every other test driven by the same
  browser fixture (20 of the module's 35 test functions take `run_tool`, and
  each one launches its own Playwright driver and its own Chromium, because the
  fixture is function-scoped). One `set_content` hung and dozens of others on
  the same fixture did not. That is a tail event inside a degraded run, not a
  property of the markup, and not a property of the fixture either.

**NOT ESTABLISHED, and I am not going to pretend otherwise:** WHY the parallel
phase was degraded. The candidates are a different `-n auto` resolution (fewer
or more workers than attempt 2), memory pressure under N concurrent Chromium
instances, or a noisy co-tenant on the physical host. The logs cannot separate
them, for one specific and fixable reason given in 7.1: **the workflow never
records how many xdist workers it used, how many CPUs the runner had, or how
much memory was free.** `-n auto` is resolved inside pytest and printed nowhere
under `-q`. So the single number that would discriminate these candidates was
never written down, on either attempt.

So the honest verdict is: **this is resource exhaustion, proven to be
non-deterministic and non-code, with the specific resource unidentified.** It
is fixed below as resource exhaustion -- by making the next occurrence say what
it saw, rather than by enlarging the number it exceeded.

---

## 4. WHAT THE LOCAL REPRODUCTION SHOWED

Run as CI runs it -- shard 3's 35-file set, `-n auto --dist loadfile`, not the
single test in isolation.

    python -m pytest -q -rs -n auto --dist loadfile $(cat shard3-files.txt)
    2110 passed, 1 xfailed in 662.34s (0:11:02)

It did not reproduce. That is a real result and not a null one: this box took
662s against the runner's 343s -- it is roughly TWICE as loaded as the machine
that failed, five sibling waves were running on it throughout, and the shard
still passed. Whatever the runner hit is not simply "a busy box", which is
consistent with 3A.2 and narrows the residual in 7.1.

A note on safety, since this suite launches browsers: the worktree resolves
`CHROME_PROFILE` to `<worktree>/_state/chrome-profile`, which does not exist,
because a git worktree carries no gitignored files. The operator's signed-in
profile lives in the main checkout and was unreachable from here. Separately,
`tests/test_browser.py` -- the only file in shard 3 that mentions the
persistent profile -- drives a FAKE chromium stub and monkeypatches
`CHROME_PROFILE` to a `tmp_path`. Nothing in this wave launched the persistent
profile or went near linkedin.com.

### 4.1 Isolated baseline

    python -m pytest -q tests/test_editor_fields.py
    53 passed in 179.05s (0:02:59)

The file PASSES alone, and costs 179 seconds to do it. Both halves matter.

### 4.2 The packer prices this file at 16 seconds

`scripts/ci_shard_timings.json` is the committed weight table the shard packer
balances against. Its provenance line:

    "f65ec88, 2026-09-19, one Windows laptop (3.13.14), serial run in a detached
     worktree, NOT a quiet box -- short foreground test batches overlapped parts
     of it"
    "_files": 157, "_tests": 5736, "_total_seconds": 946.1

and its entry for the failing file:

    "tests/test_editor_fields.py": 16.083

The file is byte-identical between `f65ec88` and `f729a2a`:

    git log --oneline f65ec88..f729a2a -- tests/test_editor_fields.py
    (empty)

So the table is not stale in the sense of describing an older file. It describes
THIS file, and it is out by an order of magnitude against a direct measurement
on a comparable box. Two further facts about the table:

* it prices **157** files; the suite at `f729a2a` collects **208**. Fifty-one
  files are unpriced and estimated at the measured mean seconds-per-test.
* `tests/test_tool_envelopes_emit_no_page_string.py`, the file this merge added,
  is one of the unpriced ones.

---

### 4.3 THE RATIO CONTROL -- which refuted MY hypothesis, not the table

Section 4.2 looks like a smoking gun: the packer prices the failing file at
16.083s and it measures 179.05s. The obvious story is "the table underprices
browser files, so LPT stacked work on top of one". I went looking for that and
the measurement did not support it.

The control: run five files from shard 3 with known table entries, serially,
with a junit report, and compare RATIOS rather than absolute seconds -- because
this box is neither the box the table was measured on nor a quiet one, so
absolute seconds measure the laptop. Per-file seconds parsed with
`ci_shard.py`'s own `seconds_per_file()`, imported rather than re-implemented.

    file                                       table(s)   measured    ratio
    tests/test_result_verification_block.py       1.706       49.7    29.2x
    tests/test_editor_values.py                  16.795      418.5    24.9x
    tests/test_editor_fields.py                  16.083      371.4    23.1x
    tests/test_no_committed_identity.py          10.575      147.2    13.9x
    tests/test_browser.py                         0.713        3.0     4.2x

**Every file is far over its table entry, including a two-test static guard at
29.2x -- the highest ratio in the set, and it launches nothing.** The browser
files are not the outliers. The spread runs 4.2x to 29.2x with no relationship
to whether a browser is involved.

So this box cannot separate a wrong table from a loaded machine, and the
hypothesis is NOT ESTABLISHED. Two confounds, both real: five sibling waves were
running throughout (the same file measured 179.05s alone earlier and 371.4s
here, so contention alone moves it 2x), and fixed per-file overhead inflates
small files' ratios, which is exactly what the 2-test file at the top of that
table is showing.

I am recording this as a refuted hypothesis of my own rather than quietly
dropping it, because the 16-vs-179 number in 4.2 is genuinely striking and the
next person will notice it too. What it needs is in 7.2.

### 4.4 THE SUBSCRIPT SWEEP -- count, method, and why the big number is not the answer

**Method.** `scripts/_census_result_subscripts.py` parses every `tests/**/*.py`
with `ast` -- 212 files, 0 parse errors -- and finds every `ast.Subscript` whose
slice is a string CONSTANT and whose base is a `Name` that is RESULT-BOUND in
its enclosing scope. Result-bound means bound by one of: `x = await ...`; a
tuple-unpack of an `await` (element positions tracked, so only the names
actually assigned); a call to `run_tool`/`call_tool`/`invoke`/`tool`/`_run`; a
parameter named `result`/`results`/`answer`/`envelope`/`payload`/`reply`/
`response`; or `json.loads(...)` in a scope that already holds such a binding
(recorded separately as `indirect`).

Nothing here is decided by grep. That was a requirement and it earns itself:
`result["fields"]` occurs as PROSE inside a comment and a docstring in the very
file being fixed, and a textual sweep would have "fixed" both. The parse also
distinguishes `assert result["x"], result` (the subscript is the subject) from
`assert cond, result["x"]` (it is the message), which no line-oriented tool does.

**The wide count: 1943 records across 63 of 212 files.** That number is REAL and
it is NOT the defect. It is what the suite's ordinary idiom looks like, and
"fix 1943 sites" would be a rewrite of the test suite justified by one CI
failure. Two narrower cuts were taken instead.

**Cut one -- does the module practise the convention?** Classifying each file by
whether it has sites of the form `assert x.get("k") ..., x` (convention-honoured)
versus string subscripts on a result-bound name (convention-broken):

    PRACTISES       1
    MIXED           6
    PURE-SUBSCRIPT 57
    NEITHER       148

`tests/test_editor_fields.py` classifies correctly, and the finding that settles
section 1.2 is this: it has **zero** raw subscripts on a refusal key. Every one
of its refusal checks does use `.get`. The convention is honoured exactly where
it is written down. The 27 result-subscripts in that file are all on the SUCCESS
path -- outside the comment's stated scope, and the success path is what broke.

**Cut two -- THE DEFECT CLASS, which is what was actually fixed.** The shape that
destroyed the diagnosis is narrower than "a subscript": it is a subscript inside
a FUNCTION THAT WAS HANDED THE RESULT, because then the traceback's headline
names a missing key while the envelope sits one frame up, behind a helper's
name. Enumerated suite-wide: functions that are not tests and not fixtures,
which take a result-shaped parameter and subscript it with a string constant.

    candidates suite-wide  2
    guarded                1
    DEFECT SET             2   (names_of, and one nobody had reported)

The second was `by_label` in `tests/test_editor_values.py:286`, whose docstring
promises *"or a loud failure"* while raising `KeyError: 'fields'` before either
of its two loud assertions is reached. Both are now fixed; the count is 2, and
the sweep is what found the one that was not in the brief.

**Controls on the census itself.** Positive: the known instance at
`test_editor_fields.py:323` must appear -- it did, printed. Negative/mutation: a
synthetic module carrying (i) a result-bound subscript, (ii) a `.get` on the
same name, (iii) a subscript on a name that is NOT result-bound -- exactly (i)
was reported and neither (ii) nor (iii). Going-quiet: `names_of` rewritten in
memory to `.get`, and the record for that line disappeared.

A fourth control arrived unplanned and is worth recording. Midway through, the
census's positive control went to ZERO matches -- because I had landed the
`fields_of` fix underneath it. The instrument was right, its PIN had rotted, and
it was reported as a surprise rather than adapted to. The lesson is general
enough to keep: **a control pinned to a defect's continued existence rots the
moment the defect is fixed** -- and a SECOND control in the same script was
independently stale the same way. Both were re-pinned to a synthesised module
held inside the script, carrying the original pre-fix shape, parsed in memory
and never read off disk. That was then confirmed the hard way: the tree moved
under the census twice more (another edit, then the commit) and the re-pinned
controls did not notice, because they no longer look at that file.

**After both fixes the defect set is 0, re-measured rather than assumed** -- 6
of 6 controls passing across all three passes.

One correction to my own expectation, reported as measured rather than shaded
to fit: I predicted `by_label` would now classify as GUARDED. It does not. It is
ABSENT from the candidate list entirely, exactly like `names_of`, because the
`.get` extraction routes through a local `fields` variable and leaves no
`result[...]` subscript in the function for a guard to attach to. The
guarded-candidate path is real and its own control fires on a constructed case
that keeps a subscript -- but no instance in this repository currently
exercises it. Whether GUARDED and ABSENT should be tracked separately going
forward is left open rather than decided here.

Pass B after the fixes: `tests/test_editor_values.py` did not change class
(still MIXED); its convention-breaking count dropped 19 -> 17, which is exactly
the two sites `by_label` no longer has.

---

## 5. CONTROLS

### 5.1 The AST comparator, shown failing

A comparator that answers IDENTICAL is worthless until it is shown capable of
answering DIFFERENT. One token was changed in a copy of the `A` revision --
`isinstance(exc, LinkedInReaderError)` to `isinstance(exc, KeyError)` inside
`_error` -- with the line count held constant, and the comparator re-run:

    line counts equal (so this is not a size change)
    1028:    if isinstance(exc, KeyError):

    WHOLE-MODULE AST, docstrings stripped: DIFFERENT
    top-level defs: A_09b5f17=86  A_MUTATED=86
    defs only in A_09b5f17: none
    defs only in A_MUTATED: none
    defs whose CODE changed: ['_error']
    linkedin_profile_editor_fields: UNCHANGED
    EXIT=1

It flips its verdict, NAMES the function that changed, and flips its exit code
0 -> 1. The IDENTICAL verdict in 2.3 is therefore a measurement and not a
default.

The probe ships with that control built in (`--self-test`, four controls) and it
caught a defect in ITSELF on the first run: `--focus` originally printed
`unchanged-or-absent` for any name not in the changed list, so a misspelled
`--focus` produced the same reassuring word as a real comparison. Control 4 now
distinguishes UNCHANGED from NOT A TOP-LEVEL DEF IN EITHER REVISION.

### 5.2 THE FORCED TIMEOUT -- the new message on a real one

The standing law here is that a better message must be SHOWN, not asserted. So
`scripts/_check_the_editor_fields_failure_names_the_envelope.py` makes the
timeout actually happen: a local headless Chromium, the real tool, the real
`browser.BROWSER.session`/`.goto` replacement the fixture uses, and an editor
document whose opening synchronous script spins the parser past the deadline.
`domcontentloaded` cannot fire while a synchronous script runs, so
`set_content(..., wait_until="domcontentloaded")` genuinely times out -- same
call, same wait condition, same exception class. Nothing is simulated: no
exception is constructed by hand and no result dict is written by hand. The
timeout is 3000ms rather than 60000ms because the only thing that changes is
the integer printed inside the message.

    THE TOOL RETURNED:
        {'error': 'unexpected', 'message': 'TimeoutError: Page.set_content:
         Timeout 3000ms exceeded.\nCall log:\n  - setting frame content,
         waiting until "domcontentloaded"\n'}

    --- BEFORE (the implementation that shipped)
        return [field["name"] for field in result["fields"]]
    KeyError: 'fields'
        HEADLINE: KeyError: 'fields'

    --- AFTER (fields_of)
        assert isinstance(fields, list), (
    AssertionError: the tool published no 'fields' list. It returned:
    {'error': 'unexpected', 'message': 'TimeoutError: Page.set_content: Timeout
    3000ms exceeded.\nCall log:\n  - setting frame content, waiting until
    "domcontentloaded"\n'}
        HEADLINE: AssertionError: the tool published no 'fields' list. It
        returned: {'error': 'unexpected', 'message': 'TimeoutError: ...'}

    VERDICT
      old headline names only the absent key : yes
      new headline quotes the real envelope  : yes

    CONTROL: PASS -- the failure now names what the tool returned

The envelope this control produced is structurally identical to the one CI
produced -- same keys, same exception class, same call log -- differing only in
the timeout integer. The script also REFUSES rather than comparing if the tool
happens to publish `fields`, because then no timeout occurred and the
comparison would be of two things that never happened.

### 5.3 THE DIAGNOSIS ITSELF, and the defect the control found in it

Section 1.3 fixes the reporting. The remaining half of Defect 2 is that a bare
`Timeout 60000ms exceeded` cannot be attributed by anyone who reads it: it does
not say whether the BROWSER was starved or whether THAT DOCUMENT hung, and those
call for opposite responses. `render` now takes the discriminating reading at
the moment of failure -- how long it waited, the exception's type, the markup's
LENGTH (never its content -- that is
`ERROR-MESSAGE-RULED-AT-THE-RAISE`, the ruling this very merge landed), the
xdist worker, and how long an EMPTY document takes on the same browser
immediately afterwards.

The timeout is still 60000ms. It was not raised, nothing is retried, and nothing
is marked flaky.

**AND THE CONTROL CAUGHT THE FIRST VERSION BEING WRONG.** `_trivial_render_seconds`
originally reused the page that had just failed. Run against a hanging document,
it reported

    An empty document on this same browser immediately afterwards took:
    ALSO FAILED (>5s) -- the browser is not drawing at all

which indicts the MACHINE for what the MARKUP did -- the precise confusion the
reading exists to prevent, shipped inside the fix for it. A wedged parser is
still wedged a moment later, so the control render on that same page cannot
succeed. Taking the reading in a FRESH CONTEXT, which gets its own renderer,
fixes it. Same script, same fixture, after the change:

    ... It waited 3.1s for 'domcontentloaded' on 161 bytes of LOCAL markup
    -- no network is involved in this call, so a wait like that is about what
    else was running, not about the page. An empty document on this same
    browser immediately afterwards took: 0.64s in a fresh context.
    xdist worker: none (serial run).

    VERDICT
      old headline names only the absent key   : yes
      new headline quotes the real envelope    : yes
      new message names the exception kind     : yes
      new message carries the CONTROL reading  : yes
      new message names the xdist worker       : yes
      CONTROL READING BLAMES THE MARKUP, NOT
      THE MACHINE (this fixture hangs a page,
      it does not starve the box)              : yes

    CONTROL: PASS -- the failure now names what the tool returned

0.64s against a 3.1s timeout on the same browser: the discriminator
discriminating, on a fixture where the right answer is known because the script
built it. That last verdict line is now part of the control, so the wrong-page
version cannot come back silently. The check asserts the reading's PRESENCE and
shape and never its value -- asserting a number would make this control fail on
a slow machine, which is the one machine it most needs to keep working on.

### 5.4 The edited modules, run

    python -m pytest -q -rs tests/test_editor_fields.py tests/test_editor_values.py
        tests/test_browser.py tests/test_result_verification_block.py
        tests/test_no_committed_identity.py
    869 passed in 1005.39s (0:16:45)

Both edited modules pass, alongside the three files section 4.3 prices. The
exception path added to `render` is not exercised by that run -- no timeout
occurred -- which is exactly why 5.3 drives it directly instead of trusting a
green suite to have covered it.

### 5.5 TWO OF THIS REPOSITORY'S OWN GATES CAUGHT THIS WAVE, and both were right

Recorded because a wave that reports only the gates it passed is reporting on
its luck.

**`tests/test_the_audit_index_is_derived.py` refused this very document.**

    assert len(table) == len(docs), (len(table), len(docs))
    E   AssertionError: (217, 218)
    2 failed, 44 passed

`_audit/INDEX.md` is DERIVED from the corpus and the gate asserts the identity
"every tracked document has a row, and every row names a tracked document".
Adding this audit file broke it -- as it should. Regenerated with the command
the failure itself names, `python scripts/build_audit_index.py --write`, which
wrote one row and moved three derived counts (217 -> 218 documents, 181 -> 182
dated, 130 -> 131 untouched by a correction marker). Re-run: 46 passed.

**`tests/test_scripts_are_import_safe.py` refused one of my new instruments.**

    AssertionError: scripts/_probe_diff_is_docstring_only.py:
      [(158, 'replace at import time'), (160, 'replace at import time')]
    1 failed, 1110 passed

The probe built its two control variants with `.replace` at MODULE level, and
the rule is that no script may act because something imported it. Moved inside
`self_test()`, which is the only thing that uses them. Re-run: 206 passed, and
the probe's own four controls still pass.

Both are worth more than the fixes they forced. The audit index gate is the one
that makes `_audit/` navigable rather than a directory of orphans, and it fired
on the first document added to it by someone who had not read it. The
import-safety gate caught a side effect in a file whose entire purpose is to be
imported and asked a question.

---

## 6. THE RE-RUN, VERIFIED RATHER THAN ASSUMED

The brief asked me to establish whether the requested re-run actually started
and what it concluded, instead of assuming either. Both readings are stamped.

    12:0x UTC : {"conclusion":null,"run_attempt":2,"status":"in_progress"}
    12:15 UTC : {"conclusion":"success","run_attempt":2,"status":"completed",
                 "updated_at":"2026-09-21T11:34:35Z"}

    windows-latest py3.13 shard 3, attempt 2, job 106315070960:
      started 11:27:42Z, completed 11:34:25Z, conclusion SUCCESS
      2109 passed, 1 skipped, 1 xfailed in 110.74s

So: it started, and it concluded GREEN. Two things follow, and only two.

It does NOT mean the defect is absent. A green retry of an intermittent failure
is the expected outcome of an intermittent failure; it measures frequency, not
cause, and nothing in section 1 or section 3A rests on it.

What it DOES buy is the controlled comparison in 3A, which is worth considerably
more than a verdict: the same commit, plan and command, passing and failing, with
the code held byte-identical. That is what let H2 be refuted by elimination
rather than merely by inspection.

One practical consequence for whoever reads the log next: `gh run view
35592629243 --log-failed` returns "run ... is still in progress" while a re-run
is live, and once it completes, the failing ATTEMPT-1 logs are not what that
command returns. Attempt 1's logs have to be fetched by attempt and job id:

    gh api repos/<owner>/linkedin-mcp/actions/runs/<run>/attempts/1/jobs
    gh api repos/<owner>/linkedin-mcp/actions/jobs/<job id>/logs

Requesting a re-run therefore makes the evidence for the failure HARDER to
reach, which is worth knowing before requesting one.

---

## 7. RESIDUAL

### 7.1 THE MEASUREMENT THAT WOULD SETTLE THE CAUSE, and it is one line

The mechanism behind 3A.2 -- a run that was faster single-threaded and 3.1x
slower in parallel -- cannot be separated from these logs into "fewer xdist
workers", "memory pressure under N Chromiums" or "noisy co-tenant", because
**no shard job records how many workers `-n auto` resolved to, how many CPUs the
runner had, or how much memory was free.** Under `-q`, xdist prints no banner,
so the number that decides between the candidates was never written down on
either attempt.

The fix is a diagnostic step in `.github/workflows/ci.yml`, before "Run this
shard":

    - name: What this runner is, and how wide the shard will run
      run: |
        python -c "import os; print('cpu_count', os.cpu_count())"
        python -c "import psutil; print(psutil.virtual_memory())"  # or wmic/free
        python -m pytest -n auto --collect-only -q 2>&1 | head -3

**I have NOT made this change, on purpose.** `.github/workflows/ci.yml` is the
most-shared file in this repository and five other waves were running in their
own worktrees while this one ran; the brief's rule is to name a change in
another wave's file rather than make it. It is named here, with its exact
content, so it costs whoever owns that file one paste.

Until it exists, a recurrence is diagnosable only from the test side -- which is
what section 1.3's `_trivial_render_seconds` now provides, and it answers the
narrower question (was the BROWSER starved) rather than the broader one (was the
RUNNER).

### 7.2 NOTHING EVER CHECKS THE PACKER'S WEIGHT TABLE -- which is the finding, and it is not the one I went looking for

Stated in the shape the evidence actually supports, not the shape I first wrote.
Section 4.3 refuted my hypothesis that the table specifically underprices
browser files; what survives is narrower and more durable.

`scripts/ci_shard_timings.json` prices `tests/test_editor_fields.py` at
**16.083s**. Measured directly on this box, alone:

    python -m pytest -q tests/test_editor_fields.py
    53 passed in 179.05s (0:02:59)

The file is byte-identical between the table's measurement commit (`f65ec88`)
and `f729a2a`, so it is not a table describing an older file. But per 4.3 a
two-test static guard measures 29x its entry on this box, higher than any
browser file, so **this box cannot tell a wrong table from a loaded machine**
and no claim about the entry's correctness is made here.

The claim that does stand needs no calm box: **nothing in this repository ever
compares the committed table against a measured run**, so nobody would know
either way. And the table's own provenance line concedes the same weakness on
the other side -- it was taken on *"one Windows laptop ... NOT a quiet box --
short foreground test batches overlapped parts of it."* A packer that balances
by SECONDS is steered by a number that was measured under load and has never
been re-checked under any conditions at all.

That matters because of what the packer is. LPT sorts heaviest-first and fills
the lightest shard; an under-priced heavy file does not merely land in a
slightly-wrong shard, it invites the packer to stack more work on top of it.
`scripts/ci_shard.py`'s own docstring names this failure mode -- *"a new file is
as likely to be a browser module as a static guard, and under-pricing one of
those is the mistake that lands two 180s files in the same shard"*.

And one number here IS solid, because it comes from the plans rather than from
any clock: shard 3 at `f729a2a` holds **2111 tests against a 884-1486 range**
for its five siblings -- 42% above the next-heaviest -- in a scheme whose whole
purpose is balance. Whether that is correct depends entirely on a weight table
nothing validates.

Two things are missing and both are nameable:

* **nothing compares the committed table against reality.** The repo ships
  `--write-timings` to regenerate it and `--plan --seconds junit.xml` to price a
  plan against a real run, but no gate ever runs either, so the table can drift
  arbitrarily far while every partition test stays green -- the tests assert
  that the split is a PARTITION, which stays true at any weights.
* **the table covers 157 files; the suite at `f729a2a` collects 208.** Fifty-one
  files are priced at the mean seconds-per-test, including the file this merge
  added.

RECOMMENDED, NOT DONE: a gate that fails when a file's measured seconds diverge
from its table entry by more than some factor, naming the file. I did not
regenerate the table and I did not touch `scripts/ci_shard.py` or the timings
file: regenerating needs a quiet box and a full serial run, it would reshuffle
every shard for every wave mid-flight, and those files may be another wave's.

### 7.3 The sweep's wider set, deliberately not fixed

`scripts/_census_result_subscripts.py` finds **1943** string-literal subscripts
on result-bound names across 63 of 212 files under `tests/`. That is the
suite's ordinary idiom, not a defect list, and it is NOT the number this wave
fixed. The reasoning is in section 4.4. The full 1943-record census is
regenerable from the committed script and was deliberately left untracked: at
roughly 1 MB it is noise in a repository where **every new tracked file adds a
parametrised case to two guards and perturbs the shard plan** -- the mechanism
section 3.5 measures.

### 7.4 One known instance left unfixed, named so it is findable

`for field in result["fields"]:` inside
`tests/test_editor_values.py::test_the_ten_fields_are_present_on_every_returned_control`
is a raw subscript in a TEST BODY rather than in a helper, so it falls outside
the defect class this wave defined and fixed (functions that are HANDED a result
and subscript it, where the envelope disappears behind the helper's name). Its
headline on a missing key would still be `KeyError: 'fields'`, but the failing
test's own name and frame are right there, which is the difference the class
turns on. Recorded rather than fixed.

CITED BY SYMBOL, AND THE REASON IS THIS DOCUMENT'S OWN MISTAKE. I first wrote it
down as line 689. It is line 708. Nothing moved it but me: expanding
`by_label`'s docstring three sections earlier added nineteen lines above it in
the same edit. A line number in an audit does not rot into a dangling
reference, it rots into a PLAUSIBLE WRONG ANSWER -- line 689 still exists and
still holds code -- so the symbol is the citation and the number is a
convenience.

### 7.5 What a green master does not mean here

Master is green again because attempt 2 passed, not because anything was
repaired -- the repair in this branch had not landed when that retry ran. The
conditions that produced the failure are not understood (7.1) and are not under
this repository's control. The honest expectation is that this recurs. What has
changed is that when it does, the failure will name the timeout and say whether
the browser was being starved, instead of reporting a missing key.
