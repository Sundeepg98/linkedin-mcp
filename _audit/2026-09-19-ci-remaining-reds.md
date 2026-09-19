# The remaining CI reds, 2026-09-19 -- run 35441013901 on `ci-offload`

Wave `ci-green`. Started 17:51, stopped 18:10. Everything below is read off the
run's own `--log-failed`, saved and parsed rather than skimmed.

## THE BRIEF'S FAILURE LIST WAS A SUBSET, AND THAT IS THE FIRST FINDING

I was handed six assertion sites totalling 15 failures. The run holds
**27 failures and 18 errors across 13 of 20 jobs**. The brief's list is what one
job's tail showed; it is not the matrix.

This is the same shape the gate-is-27-red downlink was written to stop -- a
partial capture reported as the state -- and it recurred one level up.
Per-job, from the log:

    ubuntu 3.10 shard 0    "Every test in this shard actually ran" FAILED
    ubuntu 3.10 shard 1    574 passed, 6 errors
    ubuntu 3.10 shard 2    3 failed, 1075 passed
    ubuntu 3.10 shard 3    4 failed, 1126 passed
    ubuntu 3.10 shard 4    f-string SyntaxError, 1 site
    ubuntu 3.10 shard 5    14 failed, 1071 passed
    ubuntu 3.13 shard 1    574 passed, 6 errors
    ubuntu 3.13 shard 2    1 failed, 1076 passed
    ubuntu 3.13 shard 3    2 failed, 1128 passed
    windows 3.13 shard 1   574 passed, 6 errors
    windows 3.13 shard 3   2 failed, 1128 passed

## FIXED -- TWO COMMITS, 13 OF THE 45 CLEARED

### `08ceb1e` -- ten failures were one file that does not compile on 3.10

`scripts/_probe_add_section_menu.py:500-502` put an escaped quote inside an
f-string EXPRESSION. PEP 701 allows that from 3.12; before 3.12 it is a
SyntaxError, and the matrix runs ubuntu py3.10.

**None of the ten was reporting a rule violation.** Every guard that walks the
package with `ast.parse` -- the navigation rule, the page-text sink rule, the
goto census, the sanitiser-claimant sweep, the relation-definition check --
raised SyntaxError on this one file instead of returning a verdict. On 3.13 they
read it fine, so nothing on this box could ever have seen it. Ten names, one
defect, and it is invisible to a local run by construction.

Repair: the three awaits hoisted out of the f-string. Selectors byte-identical.
Verified -- the repo-wide scan for a backslash inside an f-string expression is
now **0 tracked files** (the one remaining textual match,
`tests/test_readonly.py:1850`, is a raw regex string whose text merely looks
like an f-string), and `test_navigation_is_never_derived.py` plus
`test_no_committed_identity.py` are **874 passed** against the edit.

Note the file: `_probe_add_section_menu.py` is the orphaned red two waves called
"not mine". It was never only a tidiness item.

### `c47a070` -- CI writes working files into the repo root and the sweep walked them

    shard-collected.txt: 1 unallowed company id hit(s), 0 declared

on three jobs, never on this box, because the file only exists inside a runner.
The hit is a pytest TEST ID: `--collect-only -q` tees every node id to that
file, and `sweepable()` is tracked + untracked-not-ignored.

Same shape as `.pw-browsers/` one commit earlier, and the same argument for
ignoring rather than declaring: **the ids are DERIVED from the test files, which
are swept directly**, so the artifact is a second copy of text the guard already
reads at its source. Ignored: `collected.txt`, `shard-collected.txt`,
`shard-files.txt`, `shard-plan.json`, `junit.xml`, `reports/` -- every one
written by `ci.yml` during a run, none ever committed.

## REFUSED -- HELD RED ON THE LEAD'S STANDING ORDER

`test_a_click_that_does_commit_reaches_the_body_and_the_send`
(`test_click_is_not_its_own_evidence.py:372`), 3 jobs. Untouched. It is the
positive control for the one tool that reaches another person.

## NOT FIXED, AND TWO OF THEM ENCODE A RULING RATHER THAN A COUNT

### RULING -- the 18 errors are the ORPHAN BRANCH, not a test defect

    subprocess.CalledProcessError: ['git','show','1c08e5f:_audit/_census/jobs.md'] -> 128

6 errors x 3 jobs, at setup of `test_unassigned_only_ever_shrinks`. `ci-offload`
was pushed as an orphan with **no ancestry**, so no historical SHA resolves on
it. Every history-dependent test errors there and will keep doing so on every
future push to that branch.

The repo already holds one precedent, and it points the other way from the gate:
`test_connections_reader.py:735` SKIPS with *"pre-fix commit unresolvable
(history rewritten?)"* -- while `ci.yml`'s full-run check **fails on any skip, by
design**. Those two cannot both hold on an orphan branch.

**This is the lead's call, not mine:** either CI runs on a branch carrying
ancestry, or an unresolvable-SHA path is sanctioned and the no-skip rule is
amended to admit it. I changed nothing.

### RULING -- `test_that_forced_failure_can_actually_fail` is a Windows-only control

`test_path_hygiene.py`, 2 ubuntu jobs, windows green. Its own failure message
states the finding exactly:

> the unscrubbed message carried no drive letter, so the assertion above proves
> nothing on this platform

It is a control: an unscrubbed message must trip the same assertion. On Linux
there is no drive letter to scrub, so the control cannot fire. **That is new
information about the control, not a defect to paper over.** The two repairs
answer different questions -- synthesise a drive-letter-bearing message, after
which it tests the REGEX and no longer tests the platform, or mark it
Windows-only, which the gate's no-skip rule forbids. Choosing is a ruling.

### DIAGNOSED, NOT REPAIRED -- the 7 `test_the_split_is_a_partition[seconds-ofN]`

Not a timings table and not a threshold. `partition_problems`
(`test_ci_shard.py`, the `packed`/`expected` comparison):

    packed   = sum(weights[path] for path in placement if path in weights)
    expected = sum(weights.values())
    if packed != expected: ...

Two float sums **accumulated in different orders** -- `placement` is in shard
order, `weights` in collection order -- compared with `!=`. The message
`'1007.130000... tests packed'` is float associativity, and the file-level
partition checks immediately above it already prove the partition exhaustively
by file identity, so this line adds nothing the others do not already say.

The function's own signature declares `weights: dict[str, int]`; the `seconds`
shape hands it floats. **The contract is violated by the caller, and `!=` is the
wrong comparator for floats.** Two candidate repairs -- make the check
order-independent, or make weights integral (milliseconds) -- and the second
changes the packer's unit, so it is not a drive-by. Left for a wave with time to
prove it.

I could not reproduce it locally: this box is 3.13 only, where it passes. Why
the same data and the same code diverge by interpreter is **not established**,
and I am recording that rather than guessing.

### SETTLED BY MEASUREMENT, EDIT NOT LANDED -- `test_feed_tally`, 2 sites, py3.10 only

    feed.urlsplit accepts ['url','scheme','allow_fragments'], outside _PERMITTED_PARAMETER_NAMES
    a public callable was added or removed and this sweep was not updated: ['urlsplit']
    assert {'author_kind...y','overlap'} == {'author_kind...','urlsplit'}

`PUBLIC_CALLABLES` (`test_feed_tally.py:36`) is *every non-underscore name in
`vars(feed)` that `inspect.isfunction`*. `feed.py:200` does
`from urllib.parse import urlsplit`. Measured on this box:

    3.13.14  isfunction(urlsplit) = False   <class 'functools._lru_cache_wrapper'>
    PUBLIC_CALLABLES: ['author_kind', 'authorship_concentration', 'feed_tally', 'overlap']

**CPython wrapped `urlsplit` in an lru_cache after 3.10.** On 3.13 the wrapper
is not a function, so the stdlib import silently drops out of the set and the
sweep matches. On 3.10 it is a plain function, so it enters -- and the sweep
then inspects a stdlib signature and reports its parameters as an unpermitted
widening of this repo's closed set.

So `inspect.isfunction` is being used as the test for *"is this one of ours"*,
and it is not one -- it is a test of how CPython happens to implement a stdlib
function this release. **The three-parameter "widening" it reported is
`urllib.parse.urlsplit`'s own signature and has nothing to do with this repo.**

The repair is one clause, and it makes the set mean what the assertion already
says it means:

    and getattr(value, "__module__", None) == feed.__name__

It changes no product code, admits nothing, and leaves 3.13's coverage exactly
as it is today -- it makes 3.10 agree with 3.13 rather than lowering either.
The message's own warning against widening `_PERMITTED_PARAMETER_NAMES` is
respected: nothing is widened.

**I did not land it.** It is a `tests/` edit, which fires the ~142s boundary
hook over itself plus every coupled file, and there was not enough clock left to
stage it and still be able to hand back a clean tree if the hook refused on a
foreign red. A dirty `tests/` file in this shared tree is the hazard the
downlink is mostly about. One line, fully specified above, for the next wave.

## STATE AT THE STOP

    commits           08ceb1e, c47a070   (on master, local)
    AI attribution    0  -- grep over ALL history, not just these two
    pushed            NO. Local only. I opened no browser, fired no write, and
                      did not re-run CI. The next push to `ci-offload` measures
                      them.
    local verify      874 passed (navigation + identity guards) against the edits
    NOT verified      the full suite. I ran two files and I am naming exactly
                      which, because a subset reported as a gate is the failure
                      this file opens with.

## WHY THERE IS NO RE-MEASUREMENT ON CI

The brief said to push from "the existing clone at the scratchpad path named in
the downlink". **The downlink names no such path**, and this session's
scratchpad holds six `clone-*` directories of which exactly one is a git repo,
sitting on an unrelated commit. The `ci-offload` push at 17:16 was an ORPHAN
with no ancestry and `master` untouched; getting that recipe wrong publishes the
working history that is under freeze. I did not reconstruct it from guesswork
with minutes left. **The two fixes are local and unmeasured on CI, and I am
saying so rather than implying a green.**
