# The Windows shard: a 60-second `set_content` reported as `KeyError: 'fields'`

Wave: the-windows-shard. Branch: `worktree-agent-a6ae0b6c8c4103168`.

Master went RED on CI run 35592629243 at commit `f729a2a`, in exactly one of
twenty jobs: `pytest (windows-latest, py3.13, shard 3)`. Linux py3.10, Linux
py3.13 and the other five Windows shards all passed. Two things went wrong and
they are different in kind: the suite MISREPORTED the failure, and something
made a local `Page.set_content` take longer than sixty seconds.

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
* 19 of the 20 browser tests in the same file passed in the same failing run.
  One `set_content` hung; the other nineteen did not. This is a tail event
  inside a degraded run, not a property of the markup.

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

---

## 6. THE RE-RUN

(pending -- see RESIDUAL if absent)

---

## 7. RESIDUAL

(pending)
