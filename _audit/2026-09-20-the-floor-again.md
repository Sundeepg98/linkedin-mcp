# The floor again: the wave that went looking for five seconds and found a floor

Measured 2026-09-20 on this box, in a worktree, by the wave after
`_audit/2026-09-20-the-flat-gate.md`.

**READ THE CONTENTION NOTE BEFORE THE NUMBERS.** Every absolute wall clock here
was taken on a SHARED box with other agents running, and for part of the
session the contention was MINE -- two implementer children of this wave were
running while the worker sweep was in flight. Contention only ever ADDS time,
so a minimum across interleaved passes is the least contaminated estimator, and
that is what every reported figure is. Ratios within one interleaved pass are
defensible; absolute values are upper bounds.

---

## The headline, and it is not a saving

```
THE FLOOR, derived by calling always_run_files(Corpus()), 13 files

  per-file serial, min of 3 interleaved     SUM 32,695 ms   MAX 4,013 ms
  the gate's own invocation, -n auto        WALL 15,209 ms     954 tests
  xdist startup alone, ONE trivial test     WALL  4,280 ms       1 test
  the same trivial test, serial             WALL    120 ms       1 test
```

**The slowest guard in the floor is 4.0 s and the floor costs 15.2 s.** Nothing
in the guard list explains the other 11 seconds. That is the whole finding, and
it retires the axiom this wave was handed.

---

## Axiom 1 is no longer true, and `flat-gate` retired it itself

The brief gave three starting axioms and told me to re-measure any I was about
to depend on. The first one is dead:

> **The floor's wall clock is a MAX, not a SUM.** ... The wall is bounded below
> by the slowest single file.

That was TRUE when it was written and it is FALSE now, and the reason is that
`flat-gate` fixed it. When one file cost 17,996 ms of a 23,131 ms wall, the wall
was obviously that file. After the two quadratic repairs and the four pairings,
the distribution is flat:

```
  min of 3, interleaved, serial single-file, WITH each file's own deselects

     4,013 ms     86 t  test_a_sanitiser_earns_its_entry.py          [4612, 4013, 4528]
     3,237 ms     14 t  test_page_text_is_never_printed.py           [3237, 3946, 4973]
     3,120 ms    131 t  test_ci_shard.py                             [3120, 3649, 3501]
     2,832 ms      6 t  test_readers_outside_dom_are_a_pinned_inventory.py [2832, 3215, 2933]
     2,823 ms    561 t  test_no_committed_credential.py              [3057, 3502, 2823]
     2,786 ms      9 t  test_probe_navigation_budget.py              [2822, 2906, 2786]
     2,702 ms     18 t  test_a_person_name_is_never_a_literal.py     [2702, 5103, 3081]
     2,658 ms      9 t  test_a_correction_is_findable_from_the_claim.py [2658, 3290, 2737]
     2,592 ms     43 t  test_no_committed_identity.py                [2592, 2778, 3141]
     2,416 ms     31 t  test_navigation_is_never_derived.py          [2456, 2597, 2416]
     2,080 ms     20 t  test_the_source_url_split_was_never_ruled.py [2206, 2293, 2080]
       757 ms     18 t  test_every_ignore_entry_is_declared.py       [762, 757, 833]
       679 ms      8 t  test_no_committed_document_defers_to_an_ignored_path.py [685, 977, 679]
```

Eleven of thirteen sit between 2.0 s and 4.0 s. **There is no term left to
attack.** The ratio between the most expensive guard and the median guard is
1.5. `flat-gate` predicted "a long tail, not a term" and the tail is now the
whole animal.

The practical consequence is the inverse of the old advice. The old rule was
"only the top of the sorted list is worth touching". The new rule is that
**touching the top of the sorted list is worth almost nothing**, because the
wall is not made of the list.

---

## So what IS the wall made of? Startup, and it is most of it

A single trivial test -- one `def test_nothing(): pass` -- placed inside
`tests/` so it sees the real `conftest.py` and the real `pytest.ini`:

```
  min of 3, INTERLEAVED (serial, parallel, serial, parallel, ...)

  serial                                   120 ms   [310, 120, 170]
  -n auto --dist loadfile                4,280 ms   [7290, 5510, 4280]
```

**xdist costs 4.3 seconds to start eight workers for one trivial test**, and
the gate pays that on every commit before a single guard has read a byte. That
is 28% of the 15.2 s floor, and it is a fixed cost that no guard repair can
reach. `flat-gate` measured the same quantity at 2,571-2,948 ms on a quieter
box; mine is the same phenomenon on a busier one, so the two corroborate rather
than conflict.

### Worker count is already at the flat part of the curve

Twelve arms, interleaved, same plan and same deselects every time. Pass 2,
which is the pass whose arms are all mutually comparable:

```
  23,048 ms   -n 13 loadfile
  25,852 ms   -n auto loadfile   <- SHIPPED
  26,342 ms   -n 4  load  (splits files across workers)
  26,994 ms   -n 8  loadfile
  27,416 ms   -n 4  loadfile
  34,394 ms   -n 6  loadfile
  37,161 ms   -n 2  loadfile
  47,579 ms   SERIAL, one process
```

Everything from `-n 4` to `-n 13` lands in a 23-27 s band that is narrower than
this box's own noise, and serial is twice the worst of them. **There is no free
second in the `-n` flag.** The shipped `-n auto --dist loadfile` is already the
right call, and `--dist load` -- which would split a file across workers -- is
no faster AND would trade away the isolation `loadfile` was chosen for. This
arm was run precisely so that "tune the worker count" could be closed rather
than left as a plausible-sounding suggestion.

---

## Three defects in MY OWN instruments, each caught by a disagreement

Reporting these because a measurement wave that hides its own instrument bugs
is worth nothing, and because all three are reusable traps. Every fresh
instrument built in this session had a defect on its first attempt, which is
the standing expectation rather than a surprise.

### 1. An empty test file OUTSIDE rootdir does not measure startup

My first harness put its trivial test in the scratchpad, outside the repo, and
measured:

```
  startup serial     4,721 ms
  startup -n auto   14,833 ms
```

I nearly reported "the entire floor wall is xdist startup", which the numbers
appeared to say outright -- 14,833 ms of startup against a 15,209 ms floor. It
is false. `pytest.ini` sets `testpaths = tests`, and with the target outside
rootdir the run collects far more than the one file. Moving the identical file
to `tests/` gives **0.43 s**, an order of magnitude less. **A startup
measurement must place its probe where the real tests live, or it measures
collection instead.** The honest figure is the 4,280 ms above.

### 2. Whichever arm runs SECOND wins, on a box that is quieting

The before/after pair below is an A/B toggle of one file. The first version of
that harness ran ARM A then ARM B in every pass, and returned:

```
   ARM A (HEAD)     45,285 ms   samples=[48377, 50494, 45285]
   ARM B (fixed)    39,453 ms   samples=[52972, 44624, 39453]
   delta            -5,832 ms   (-12.9%)
```

**It says the fixed file makes the floor 12.9% FASTER, which is impossible.**
ARM B adds 51 lines to a file that every floor guard sweeps; it can only be
slower or neutral. The per-pass deltas are `+4595, -5870, -5832` -- the sign
flips -- and both arms trend downward across passes (`101k, 95k, 85k` per pass)
because the box was quieting all session. ARM B ran second every time, so
"ran second" was worth about 13%.

An impossible result is the cheapest bug detector there is, and it is the only
reason this was caught: had the bias run the other way it would have produced a
plausible "+13%, the fix costs you" and been believed. The harness now
ALTERNATES the order by pass parity, so each arm runs second half the time.
**Interleaving arms is not enough on a drifting box; the ORDER within the
interleave has to alternate too.**

### 3. Writing test files into `tests/` corrupts a corpus-wide measurement

To test whether the per-test overhead was quadratic I wrote 400 trivial tests
into `tests/` -- while the worker sweep was running. The floor guards enumerate
the committable set, which is *tracked plus untracked-not-ignored*, so they
COUNTED MY PROBE FILES. The sweep's test totals drifted between 954 and 957
across arms, and when a probe file was rewritten mid-run one guard went red:

```
  FAILED test_no_committed_identity.py::test_no_tracked_file_pairs_fixture_content_with_anything_else
  FileNotFoundError: tests/test_zz_bulk_probe.py
```

Passes 1 and 2 of the worker sweep are contaminated by this and are reported
only as a band, never as a value. **You cannot measure a corpus by adding files
to it.** Every later experiment in this wave was moved outside the repository
for exactly this reason.

---

## What the guards actually spend their time on

### The autouse fixture is a real per-test tax, and it is smaller than it first looked

`tests/conftest.py` carries `_never_write_the_real_session_store`, an autouse
fixture that requests `tmp_path`. Autouse means **every test in the suite
creates a real temporary directory on disk**, including the floor's 954 tests,
almost all of which are static analysis over source text and never touch disk
state at all.

My first sample said 15.7 ms per test, which over 954 tests would have been the
entire story. It was one contended sample and it was wrong. Min of 3,
interleaved, 50/100/200/400/800 trivial tests:

```
     n    pytest ms   ms/test   marginal ms/test
    50          300      6.00
   100          540      5.40               4.80
   200          780      3.90               2.40
   400        1,430      3.58               3.25
   800        4,150      5.19               6.80
```

**~3.6-5.2 ms per test**, so roughly 3.8 s across the floor's 954 tests out of
about 25 s of total work -- real, about 15%, and not five seconds. The marginal
column rises at n=800 but dips in the middle, so **the quadratic hypothesis is
noise-dominated and I am not claiming it.** It is the one loose thread in this
wave and it is written up below as a priced item rather than a finding.

One fact about that fixture IS firm and is worth recording:
**no test consumes its yield.** A search across `tests/` for anything naming
`_never_write_the_real_session_store` returns zero files other than the
conftest that defines it. The per-test `tmp_path` therefore mints a unique
directory that nothing ever reads. The guarantee the fixture exists for --
redirect `SESSION_PATH` and `SESSION_STORE.path` away from the operator's real
session file -- does not depend on that directory being per-test or even on it
being unique.

**IT IS STILL NOT SAFE TO SHARE ONE PATH**, and this wave did not change it.
No test naming the fixture is not the same as no test depending on its
isolation: production code under test writes through the redirected path, so
test A's write would be visible to test B if they shared a file. The
cheap-and-sound version keeps a unique path per test and stops creating a
DIRECTORY per test (a session-scoped parent plus a per-test filename). That is
a change to infrastructure shared by all 6,094 tests, its payoff is bounded at
about 15% of the floor's work, and it belongs to a wave that can measure it on
a quiet box. Priced below, not smuggled in here.

---

## Job 2: a control that printed FAIL and certified anyway

`scripts/_probe_events_surface_shape.py` was reported by the `build-newsletter`
wave as carrying the same gap it had just found in its own probe: the
must-stay-silent control's result is printed and never branched on.

**The report was correct and it was also incomplete. There were TWO.**

That is the argument for the method the brief mandated. Reading the file finds
the reported one. Driving every control into its failing state finds both --
and the second one is the interesting one, because it is a control that the
author wrote a sentence about (*"a zero here voids this whole sweep"*) and then
did not implement.

### The three controls, driven into their failing states

The harness mutates the INPUT -- the gitignored capture -- and runs the SHIPPED
probe unmodified, restoring the pristine capture in a `finally`. Mutating the
probe would have proved something about a copy.

Note the worktree hazard the brief warned about, hit exactly as predicted: the
capture matches `.gitignore:140` (`*_probe-*.html`), **a worktree carries no
gitignored files**, and the probe therefore ran DISARMED here, returning 2 and
saying so. It had to be armed from the main checkout before any of this could
be measured. It stays untracked and uncommittable in the worktree, which
`git status --porcelain` confirms and which is why no capture content appears
in this document.

```
                                                    BEFORE FIX      AFTER FIX
  PRISTINE, no mutation                             exit 0 certify  exit 0 certify
  C1  plant the impossible attribute                exit 0 CERTIFY  exit 1 REFUSE
  C2  remove one event anchor (53 != 54)            exit 1 refuse   exit 1 refuse
  C3  pad hrefs past ANY_HREF's 400-char bound      exit 0 CERTIFY  exit 1 REFUSE
```

**C1**, the reported one. The probe printed `--- CONTROL, must stay silent: 1
FAIL` and then printed its entire Q1/Q2/Q3/Q4 tally and exited 0.

**C3**, the one that was not reported. Its failing state needed constructing,
and constructing it is what proves the control is not redundant with C2.
`EVENT_HREF` is unbounded (`[^"]*`); `ANY_HREF` is bounded (`[^"]{1,400}`). So
an href longer than 400 characters is counted by the anchor control and is
INVISIBLE to the needle sweep. Padding every event href past that bound gives:

```
  --- CONTROL, must fire: 54 anchors, census measured 54 -- AGREE
      54 of 54 anchors agree ... and then
       0  /events/  <- must fire; a zero here voids this whole sweep
  exit 0
```

The probe announced its own invalidity in its own words and published the
tally. Worse, the tally had silently moved: `WINDOW 1500` reported
**38 of 54** anchors carrying a labelled control instead of 54, which is
precisely the corrupted reading the void was supposed to prevent. A reader
would have taken that 38 as a fact about LinkedIn.

### The failing-state output, verbatim

An instrument enters the register only if it has been SHOWN failing, so here is
what the harness printed. BEFORE the fix, C1 driven red:

```
--- C1 must-stay-silent: plant the impossible attribute
    expectation: silent == 1 -> the probe MUST refuse
    EXIT 0
      | --- CONTROL, must stay silent: 1 FAIL
      | --- CONTROL, must fire: 54 anchors, census measured 54 -- AGREE
      | === Q1  WHAT ADDRESSES DOES THE ROOT OFFER?
      | === Q4  DOES ANY HREF LEAVE TOWARDS A SELF-SCOPED EVENTS SURFACE?
      |        54  /events/  <- must fire; a zero here voids this whole sweep
```

BEFORE the fix, C3 driven red -- note the anchor control still AGREEING, which
is what proves the two controls are not redundant:

```
--- C3 must-fire /events/ needle: pad hrefs past ANY_HREF's bound
    expectation: anchors still AGREE but /events/ hits == 0 -> the probe MUST refuse
    EXIT 0
      | --- CONTROL, must stay silent: 0 PASS
      | --- CONTROL, must fire: 54 anchors, census measured 54 -- AGREE
      |     WINDOW 1500: 38 of 54 anchors have a labelled control after them
      |         0  /events/  <- must fire; a zero here voids this whole sweep
```

AFTER the fix, the same two mutations:

```
--- C1 ...                                    --- C3 ...
    EXIT 1                                        EXIT 1
      | --- CONTROL, must stay silent: 1 FAIL       | --- CONTROL, must fire: 54 anchors ... AGREE
      |     VOID. An attribute that cannot          | --- CONTROL, must fire: 0 of 76 hrefs
      |     exist was found, so this                |     carry '/events/' -- SILENT
      |     matcher is matching itself              |     VOID. The needle sweep cannot see
```

And the summary line, both arms, which is the part that matters:

```
  BEFORE                                AFTER
  exit 0  CERTIFIED  PRISTINE           exit 0  CERTIFIED  PRISTINE
  exit 0  CERTIFIED  C1                 exit 1  REFUSED    C1
  exit 1  REFUSED    C2                 exit 1  REFUSED    C2
  exit 0  CERTIFIED  C3                 exit 1  REFUSED    C3
```

`PRISTINE` stays green in both arms. A fix that turned the probe red on good
input would have produced the same three REFUSALs and meant nothing.

### The fix

All three controls now run in one block before anything is tallied, and each
branches. C3 was HOISTED rather than patched in place: a control that runs
after the thing it guards has already been printed can only annotate a reading
it failed to prevent, and its own text always said it voided *the whole sweep*.
The duplicated `"/events/"` literal became `Q4_MUST_FIRE_NEEDLE`, used both as
the table's first entry and as the control's needle, so a rename cannot
silently disarm the control.

**The fix is precise, not loud:** the pristine capture still exits 0 and still
certifies. A fix that turned the probe red on good input would have been a
different defect wearing the same receipt.

---

---

## Job 1 step 3: re-deriving the irreducible list, and the one that is not

`flat-gate` named five guards as genuinely irreducible in whole or part. The
brief told me to re-derive rather than inherit, and hinted one might not
survive. **Four survive. One does not, and for a reason worth keeping.**

| guard | flat-gate's reason | my verdict |
|---|---|---|
| `test_a_correction_is_findable_from_the_claim.py` | a back-pointer between two documents | **HOLDS.** All 9 of its test functions are cross-document pair relations. Staging A cannot see B. |
| `test_readers_outside_dom_are_a_pinned_inventory.py` | call-graph reachability | **HOLDS.** `test_the_unwired_readers_are_exactly_the_pinned_inventory` is an inventory EQUALITY plus "is this reader called from anywhere". |
| `test_a_person_name_is_never_a_literal.py` | a usage total over the corpus | **HOLDS.** `test_every_declared_name_is_actually_used` builds `used` from every person-assignment in the corpus; deleting the last use in an unstaged file flips it. |
| `test_every_ignore_entry_is_declared.py` | a property of the tree | **HOLDS.** `test_every_derived_source_is_actually_swept` asks whether ANY committable file still lives under a declared source -- an existence claim over the whole set. |
| `test_a_sanitiser_earns_its_entry.py` | `test_every_enrolled_file_is_tracked_by_git` is a property of the tracked SET | **DOES NOT HOLD as stated.** |

### Why the fifth is different, and the distinction it exposes

`test_every_enrolled_file_is_tracked_by_git` walks `ENROLLED` -- a STATIC TABLE
declared in the test module, about forty entries -- and asks of each whether git
tracks it. That is not a property of the corpus. It is a **bounded query over a
declared list**, and a plain script could answer it in one `git ls-files` call
without sweeping anything.

The taxonomy `flat-gate` used has two boxes, PER-FILE and SET-SHAPED, and this
assertion is in neither. It needs git state, so it is not answerable from staged
CONTENT; but its denominator is a fixed table, not the tree, so it does not need
the corpus either. **There is a third category -- BOUNDED-EXTERNAL-QUERY -- and
collapsing it into SET-SHAPED is how a cheap check gets filed as impossible.**

**It buys nothing to act on.** That assertion costs 50 ms. The correction
matters for the taxonomy, not for the clock, and it is recorded so the next
reader does not inherit "irreducible" for something that is merely external.

---

## The inherited five-second projection does not survive contact

`flat-gate` closed by pricing the next wave -- this wave -- at roughly 5 s, via
two named items. **Both fail, and they fail for different reasons.**

### Item (a): pair `test_page_text_is_never_printed`. BUILDABLE -- and I got this wrong first.

**I recorded this as NOT PAIRABLE and a cross-check refuted me. The refutation
is right, and the correction is more useful than the original claim.**

Its sweep, `test_no_file_prints_page_text_beyond_its_pinned_inventory`, measures
every python file and reconciles against `KNOWN_TEXT_SINKS` in **two
directions**:

```
  gained  a file has MORE violations than pinned   <- per-file, staged-checkable
  lost    a pinned file has FEWER than pinned      <- I claimed this needs the corpus
```

My argument was that `lost` reads files nobody staged: pinned file B dropping to
zero is a red, and B need never appear in the commit. **That is wrong, and the
reason it is wrong is one line of the implementation.** `text_violations(source,
label)` is a pure function of one file's bytes plus its name -- verified by
reading it, not inferred:

```python
def text_violations(source: str, label: str = "<source>") -> list[tuple[int, str]]:
    tree = ast.parse(source, filename=label)
    tainted = _tainted_names(tree)
    ...
```

So a pinned file's count **cannot change unless that file's bytes change**, and
a file whose bytes change is in the staged set -- including deletion and
rename, both of which stage the old path. The sound staged form of `lost` is
therefore to intersect `KNOWN_TEXT_SINKS`'s keys with the staged set and check
only those. Nothing is given up.

I had reasoned from what the test's CODE iterates (the whole corpus) instead of
from what its VERDICT depends on, and those are different questions. That is
the same error in miniature as measuring a corpus by adding files to it: a
property of the instrument mistaken for a property of the subject.

**It still does not deliver five seconds**, and that conclusion is unchanged.
The file costs 3,237 ms and is not even the slowest guard, so deselecting its
sweep cannot move a wall bounded by a 4,013 ms guard and a 4,280 ms startup.
Item (a) is buildable and worth roughly 2 s of SERIAL work and roughly nothing
of WALL.

### Item (b): memo-audit `test_a_sanitiser_earns_its_entry`. NOT A MEMO PROBLEM.

It is the most expensive guard in the floor at 4,013 ms, and `--durations`
shows where that goes:

```
  2.85s  test_each_enrolled_sanitiser_is_shown_holding_the_needle[... _probe_compose_file_inputs.py::_relation]
  1.40s  test_every_claimant_of_a_sanitiser_name_is_enrolled
  0.11s  ...everything else
```

A single parametrised case costs 2.85 s while its siblings cost 0.02 s. That is
not repeated work and no memo fixes it: `_module()` is **already cached**. The
2.85 s is the one-time IMPORT of that probe, and `-X importtime` says what the
import is:

```
  import time:  2,027,291 |  9,058,686 | linkedin_server.server
  import time:         48 |  4,733,106 |   fastmcp.server.server
  import time:      1,154 |  1,592,153 |     mcp
```

**`linkedin_server.server` costs 9.06 s to import cold, almost all of it
`fastmcp` and `mcp`.** Four probes bind a module-level constant from it --
`TARGET_URL = server.CENSUS_SURFACES["messaging_compose"]` -- so importing any
of those probes for a pure helper function drags the whole MCP stack in.

For completeness, because a plausible cause had to be excluded: the autouse
fixture's own imports are innocent. `linkedin_server.browser` is **127 ms** and
`linkedin_server.session_store` is **70 ms**. `fastmcp` arrives only through
`linkedin_server.server`, which `conftest.py` never imports.

The fix is real but it is not a latency tweak: `CENSUS_SURFACES` is defined at
line 4976 of a 6,000-line module, built from `BASE_URL`/`FEED_URL`, with 11
consumers across the repo. Extracting it into a light module is a change to the
package's constant layer and deserves its own wave, for the same reason
`flat-gate` gave when it declined the floor narrowing.

### And the structural reason both items were mispriced

Even a total success on either would move the wall by under a second, **because
the wall is no longer bounded by the slowest file.** The projection was computed
under axiom 1, and `flat-gate`'s own repairs falsified axiom 1 in the same
commit that produced the projection. That is the honest account of why this wave
does not deliver five seconds: the five seconds was priced with a model that its
own author had just retired.

---

## A claim that did not survive parsing, and a real defect underneath it

The lead's cross-check note carried a sibling agent's finding that four floor
guards *"share a common bespoke AST taint engine with no staged-content-only
counterpart -- if that engine can be driven from a staged file list, it is
leverage across four guards at once."* That was the single largest lead in the
note, so it was checked by parsing the four files' import statements rather
than by reading them for resemblance.

**There is no shared engine.** What exists is a thinning hierarchy:

| guard | what it actually imports from the others |
|---|---|
| `test_navigation_is_never_derived` | nothing. It DEFINES the only real taint-propagation engine: source/sink tables and a fixed-point tainted-name walker. |
| `test_page_text_is_never_printed` | three symbols (`_COUNTING_CALLS`, `_is_sanitiser_call`, `_sink_calls`) -- **not** the walker. It then defines its OWN `_tainted_names`, `_reads_page_text` and `text_violations`, and re-defines `_python_files` byte-for-byte rather than importing it. |
| `test_a_sanitiser_earns_its_entry` | two symbols: the `_SANITISERS` constant and `_python_files`. It performs no taint analysis at all -- it imports the probe modules and CALLS the real functions against a needle table. |
| `test_the_source_url_split_was_never_ruled` | nothing from any of them. It scans a different universe (`linkedin_server/` only, never `scripts/`) and its `SHAPERS` set shares zero members with `_SANITISERS`. |

So the "leverage across four guards at once" does not exist, and a wave that had
taken the claim on trust would have spent itself building a shared driver for an
engine with one user.

### The defect that turned up while disproving it

The two walkers have **diverged**, and one of them is behind. The
`test_page_text_is_never_printed` copy treats a for-loop target and a
comprehension target as BINDINGS; the `test_navigation_is_never_derived`
original does not, and the page-text file's own docstring says so outright --
the gap was found, fixed in the copy, and never carried back.

**That is a live correctness gap in the navigation guard, not a latency
finding**, and it is reported rather than fixed for the same reason
`flat-gate` reported the `pytest-xdist` pin: it is somebody else's file and a
taint-walker change deserves its own reproduction with its own shown-failing
control. Concretely: a navigation-derived value that reaches a sink only via a
loop variable or a comprehension target is invisible to
`test_navigation_is_never_derived` today, and visible to its sibling.

---

## Job 2, part 2: is the shape present in other probes?

A child agent swept all 88 `scripts/_probe_*.py` with an AST detector, calibrated
against a FROZEN snapshot of `_probe_events_surface_shape.py` at HEAD (the file
this wave repaired, so the live copy is now a NEGATIVE and would have made a
broken detector indistinguishable from a clean corpus). The detector reproduced
all three calibration verdicts: both known positives found, the correctly
branched `agree` excluded.

```
  corpus                                     88 files globbed, 0 parse failures
  files with >= 1 never-branched control     56
  files with NO control markers at all        2
  files with controls, all branched          30
  total findings                            129
```

**56 of 88 is an UPPER BOUND and should not be quoted as the defect count.**
I checked it against the one file where I have ground truth, and the false
positives are structural rather than random: these probes census LinkedIn's UI
*controls*, so the word "control" is domain vocabulary, not a self-check marker.
On the repaired file the detector flags three names, and on inspection:

```
  hits           a Q4 needle tally    <- correctly NOT branched; the must-fire
                                         control was hoisted above and IS branched
  rows_with_any  a Q2 display tally   <- FALSE POSITIVE, marker is the word "control"
                                         in the section title "WHAT CONTROLS SIT ON A ROW"
  note           a display string     <- FALSE POSITIVE
```

A hand inspection of 16 findings, opening the source at each reported line and
reading the whole enclosing function, returned **14 true positives**. Several
are unambiguous and are the same defect this wave fixed, for example:

```
  _probe_groups_menu.py           stuck       "menus still expanded after Escape"
                                              -- computed, displayed, and nothing
                                              checks it, while the same block DOES
                                              gate on control_ok and navigated
  _probe_membership_tally_live.py overlap     a disjoint-sets dict whose boolean
                                              `disjoint` key is only interpolated
                                              into a print, never tested
  _probe_job_search_result_ceiling.py viewport_w  a -1 sentinel meaning "viewport
                                              never captured", only ever displayed
```

**But the precision is not as high as 14/16, and I can show it on the one file
where I have ground truth.** That inspection lists `note` in
`_probe_events_surface_shape.py` as a true positive, reading it as an unfixed
copy of the Q4 control. It is not: `note` is the annotation STRING beside the
control, and in the repaired file the control itself is hoisted and branched.
Two of the three names the detector flags in that file (`note`,
`rows_with_any`) are display values, not results of a check.

So the honest statement is: **the shape is real and present well beyond the one
file the `build-newsletter` wave named -- on the order of dozens of probes --
and 56 of 88 is an upper bound, not a defect count.** The residual error is
systematic rather than random: these probes census LinkedIn's UI *controls*, so
the word "control" is domain vocabulary, and a detector keyed on it cannot tell
a self-check from a button. A triage wave needs a marker vocabulary that
separates the two before any number here is quotable. The raw census, the
detector and the per-finding records are on disk for that wave. Reporting 56 as
a verified count would be manufacturing a number, which is the failure this
whole document set exists to avoid.

---

## Cross-check against the lead's independent classification

A `_TEAM_LEAD_*.md` note at the worktree root carried a sibling agent's
classification and a second independent per-file timing, explicitly as a thing
to test rather than inherit, with the instruction to trust disk on any
disagreement. **Disk disagrees in four places, and three of them are the note
being older than the tree rather than being wrong.**

| the note said | disk says | reading |
|---|---|---|
| `test_no_committed_identity.py` **17.54 s**, 546 parametrize cases, 93% of the file | **2,592 ms**, 43 tests | The note's own caveat is correct: this predates the `flat-gate` merge at `dda2e47`. The 546 cases are DESELECTED now, answered by `staged_identity_shapes.py`. **The repair landed and this is the receipt.** |
| `test_readers_outside_dom_are_a_pinned_inventory.py` **8.72 s** | **2,832 ms** | Same cause: the O(n^2) `ast.walk` per ordered module pair was fixed in place. |
| "the ONLY existing incremental sibling is `scripts/pre_commit_identity_gate.py`" | **three** sibling scripts, **four** registered pairings | `staged_identity_shapes.py` and `staged_navigation_guard.py` shipped with `flat-gate`. Derived by calling `pairings_for(always_run_files(Corpus()))`, not read off a list. |
| "files 3, 6, 10 and 13 share a common bespoke AST taint engine ... leverage across four guards at once" | **no shared engine** | Not a staleness problem -- a wrong reading. Disproved by parsing the four files' imports, section above. This was the note's largest lead and it does not exist. |

And one place where the note was right and **I** was wrong: it classified
`test_page_text_is_never_printed.py` as SET-SHAPED-dominant, I first agreed for
the `lost`-direction reason, and the recon refuted us both -- the sweep is
pairable. Two independent readings agreeing is not evidence when both read the
same way.

---

## Before and after, and why the AFTER table is not the answer

The brief asks for the sorted per-file measurement before and after. Here is
the after table, min of 3 interleaved, taken later in the same session:

```
  AFTER, min of 3 interleaved, serial single-file      BEFORE, for reference
  14,397 ms  562 t  test_no_committed_credential.py          2,823 ms
  14,327 ms   86 t  test_a_sanitiser_earns_its_entry.py      4,013 ms
  12,327 ms   14 t  test_page_text_is_never_printed.py       3,237 ms
  11,543 ms    9 t  test_probe_navigation_budget.py          2,786 ms
  10,781 ms   31 t  test_navigation_is_never_derived.py      2,416 ms
   9,951 ms   18 t  test_a_person_name_is_never_a_literal.py 2,702 ms
   9,821 ms  131 t  test_ci_shard.py                         3,120 ms
   9,715 ms    6 t  test_readers_outside_dom...py            2,832 ms
   9,603 ms    9 t  test_a_correction_is_findable...py       2,658 ms
   9,289 ms   43 t  test_no_committed_identity.py            2,592 ms
   7,448 ms   20 t  test_the_source_url_split...py           2,080 ms
   2,344 ms   18 t  test_every_ignore_entry_is_declared.py     757 ms
   1,940 ms    8 t  test_no_committed_document...py            679 ms

  SUM 123,486 ms   MAX 14,397 ms   FLOOR WALL 39,868 ms
```

**Do not read that as a 3.8x regression. It is a measurement of the box.**
Every row inflated by roughly the same factor, and the proof that it is
contention rather than this wave is in the A/B arms: ARM A is the code at HEAD,
unchanged, and it measured 15,209 ms early in the session and 48,377 ms at the
same moment the after table was taken. The subject did not change; the box did.
The test count also moves 954 -> 955 for an honest reason -- this very audit
file is untracked-not-ignored, so the committable-set guards now count it.

**The shape survives the contention, and the shape is the finding.** Excluding
the two cheap members, before spans 2.0-4.0 s (2.0x) and after spans
7.4-14.4 s (1.9x). The floor was flat and stayed flat.

### The comparison the box CAN support

Toggling one file between HEAD and this wave's version, alternating arm order,
min of 4:

```
   ARM A (HEAD)     22,075 ms   samples=[27745, 22075, 25735, 23368]
   ARM B (fixed)    22,601 ms   samples=[25517, 24790, 22601, 23741]
   delta               +526 ms  (+2.4%)
```

`+526 ms` is the honest cost of this wave, it is in the physically correct
direction (51 more lines for thirteen guards to sweep), and it is well inside
the 5,670 ms spread of ARM A's own four samples. **The floor is unchanged.**

And the order effect is now visible rather than inferred. In **four passes out
of four, the arm that ran SECOND won**, whichever arm that was:

```
  pass 1  AB   A 27,745   B 25,517   second wins by 2,228
  pass 2  BA   B 24,790   A 22,075   second wins by 2,715
  pass 3  AB   A 25,735   B 22,601   second wins by 3,134
  pass 4  BA   B 23,741   A 23,368   second wins by   373
```

That is a clean measurement of the artefact that produced the impossible
-12.9% above, and balancing the order is what cancels it.

---

## The ledger

### What the floor IS, now

```
  the gate's floor, -n auto --dist loadfile, least contended sample   15,209 ms
     of which xdist startup for 8 workers, min of 3                    4,280 ms   28%
     of which collection of the 13 files, serial                       1,237 ms
     of which the autouse fixture tax, ~4 ms x 954 tests               ~3,800 ms  (spread over workers)
     the rest is the guards' own work and box contention
  the same floor on a heavily contended box (this wave's own children) 23,598 ms
  the slowest single guard                                             4,013 ms
  serial, one process                                                 47,579 ms
```

**The floor is a floor.** Not because the guards are optimal, but because the
wall is now dominated by fixed costs that no guard repair reaches: process and
worker startup, collection, and a per-test fixture tax. The guards themselves
are flat between 0.7 s and 4.0 s, and the gap between the slowest guard and the
wall is larger than the slowest guard.

### What this wave changed

It shipped **no latency change**, deliberately. Every candidate was measured and
each one was either worth under a second, or was a package refactor wearing a
latency costume, or would have deleted half of a guard's property. Shaving
200 ms and implying more was coming was the alternative, and the brief was right
that it is worth less than this.

### What the NEXT wave could price, with numbers

| lever | worth | what it costs | why not here |
|---|---|---|---|
| **Folder narrowing** | the largest remaining. Five guards (`test_a_person_name_is_never_a_literal`, `test_navigation_is_never_derived`, `test_page_text_is_never_printed`, `test_readers_outside_dom_are_a_pinned_inventory`, `test_the_source_url_split_was_never_ruled`) never read `_audit`, never read `.md`, and never enumerate the tracked set -- **13,267 ms of the 32,695 ms serial floor, 41%** -- so a commit touching only `_audit/*.md` cannot change their verdict. | Must be derived STRUCTURALLY, never by the grep above. The sound instrument is an audit hook recording every path each guard opens, plus its glob patterns, because an observed read-set from one tree misses a file that does not exist yet. | Safety-relevant: it changes what the gate RUNS. `flat-gate` declined it for the same reason and named the control it would fire. It needs its own reproduction, not a footnote in a latency wave. |
| **Constant-layer extraction** | `test_a_sanitiser_earns_its_entry` 4,013 -> ~1,200 ms, and removes a 9 s cold `fastmcp` import from four probes. Under 1 s of WALL. | Move `CENSUS_SURFACES` out of `linkedin_server/server.py` into a light module, re-exported. 11 consumers. | A package change, and the wall payoff is under a second. Fund it as a structure wave, not a latency one. |
| **Autouse `tmp_path`** | ~3,800 ms of the floor's ~25 s of work (~15%), and ~24 s across CI's 6,094 tests. | Keep a unique path per test, stop creating a DIRECTORY per test: a session-scoped parent plus a per-test filename. | Must be measured on a quiet box, and needs a positive proof that no test depends on the isolation. **No test names the fixture** (verified, zero hits across `tests/`), but production code under test writes through the redirected path, so that is necessary and not sufficient. |
| **Anything below the startup floor** | zero | -- | Eight of thirteen guards are within 1.5x of the 4.3 s xdist startup they each help pay. Retiring them entirely would not reach the startup cost. |

**Zero remains unreachable, and the reason is now sharper than `flat-gate` had
it.** It is not only that a pytest file costs ~2.6 s; it is that **xdist costs
4.3 s to start eight workers for one trivial test**, and the floor needs xdist
because serial is 47.6 s. The floor is therefore bounded below by
`xdist_startup + slowest_worker`, and on this box that is about 8 s even if
every guard became free.

### Honest ledger of what this wave did not establish

* **The quadratic hypothesis on the autouse fixture is unproven.** The marginal
  cost per test rises at n=800 and dips at n=200; that is noise, not a curve. It
  is written as a priced item and not as a finding.
* **Absolute wall clocks are upper bounds.** The box was shared throughout, and
  for the worker sweep the contention was this wave's own two children. Passes 1
  and 2 of that sweep are additionally contaminated by probe files I wrote into
  `tests/`. Ratios within a pass are defensible; values are not.
* **56 of 88 probes is an upper bound**, not a defect count, for the marker
  vocabulary reason given above.
