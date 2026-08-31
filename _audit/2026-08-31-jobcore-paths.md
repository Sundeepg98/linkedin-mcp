# The leak was upstream: jobcore's first sweep, and the pin that could not move

Date 2026-08-31. Two repos, both PUBLIC, neither pushed by this wave.

* `jobcore` -- baseline `5480246`, suite **707 passed**. Final `fff1438`, suite
  **759 passed, 0 failed**.
* `linkedin` -- baseline `fbe2aef`, suite **1 failed, 2267 passed** (the
  deliberate red). Final `2268 passed, 0 failed`.

**No `DECLARED_PLANTS` entry was added, in either repo.** `linkedin`'s
allowlist is byte-identical to `fbe2aef`: 11 entries, unchanged, all synthetic.
`jobcore`'s new guard has no allowlist mechanism at all, by construction.

**Neither repo was pushed. No history was rewritten in either repo.** The
values fixed below remain in both repositories' pushed history; a clean tree is
not a clean history, and only delete-and-recreate was ever measured to remove
retained objects. That is the operator's call and he has not made it.

**TWO THINGS NEED YOUR DECISION, neither taken here** (detail in section 6):

1. **`ats-jobs` still carries two leaks of this exact class**, measured, at
   `ats_buildinfo.py:5` and `tests/test_no_path_leaks.py:93`. Outside the two
   repos in scope; separately public. Every other sibling repo measured zero.
2. **`linkedin`'s own backslash control has the defect found in jobcore's**
   (section 3.3): it asserts a character class that matches a slash too, so it
   cannot detect a `BACKSLASH` that stopped being one. One line fixes it.

---

## 0. The conflict, and why it had no solution inside `linkedin`

`linkedin`'s identity guard fired on `linkedin_server/paths.py`. That file is a
VENDORED COPY whose header says DO NOT EDIT, and `tests/test_vendored_buildinfo.py`
compares its body against jobcore at the pinned commit `6acc7e6`. Fixing the
copy broke the pin; leaving it broke the guard. Both measured.

There is no third state inside that repository, and that is not a defect in
either check -- **a leak in a vendored library is a leak in every consumer, and
the only place it can be fixed is upstream.** So the work started in jobcore.

---

## 1. The sweep: what jobcore actually had

### 1.1 What the two existing guards cover -- neither is an identity check

The brief asked what `tests/test_stamp_identity.py` and
`tests/test_text_hygiene.py` already cover. **Neither covers identity or
hygiene in the PII sense.** Both names are false friends:

| file | what it actually covers |
|---|---|
| `test_stamp_identity.py` | POLICY-HASH naming: that `policy_hash` means one thing (`scoring`+`candidate`) and `scoring_hash` another. Pure arithmetic-comparability. No PII concept anywhere. |
| `test_text_hygiene.py` | UNICODE SURFACE TEXT in skill strings -- typographic quotes, U+00A0, en/em dashes -- from a capture of 704 recruiter keywords. No PII concept anywhere. |

**So jobcore -- the one repo every other repo vendors -- had no identity guard
of any kind, and had never been swept.**

### 1.2 The instrument, and its control

22 identifier shapes over all 30 tracked files. Because a sweep reporting zero
is indistinguishable from a broken sweep, the instrument was controlled BEFORE
its output was read: every shape shown matching a synthetic probe, and each of
the three path rules shown matching **both** the single- and doubled-separator
spellings, all built from `chr(92)`.

```
shapes: 22, probed: 22
CONTROL PASSED: every shape matched its probe; every path rule matched both
the single and the doubled separator spelling.
```

### 1.3 Classes with hits (3 of 22)

| class | hits | verdict |
|---|---|---|
| drive root | 4 | **2 REAL** (below); 2 benign -- a drive rooted at a generic `opt` directory, and one rooted at the stock stand-in `some`/`path` |
| email | 1 | benign -- a git fixture address on the reserved `.invalid` TLD |
| posix home | 1 | benign -- the GitHub-hosted runner's home, a CI service account, used to demonstrate a cross-root relpath failure |

### 1.4 Classes with ZERO hits (19 of 22)

`phone (IN)`, `phone (E.164)`, `linkedin slug`, `company id`, `member token`,
`urn id`, `jwt`, `li_at-shaped cookie`, `generic session cookie`,
`windows user path`, `aws key`, `github token`, `slack token`, `private key`,
`ipv4`, `url userinfo`, `unc path`, `file uri`, `mac address`.

### 1.5 The two REAL path hits

| file | spelling | what it was |
|---|---|---|
| `src/jobcore/paths.py` | **DOUBLED** separators | a drive root whose first segment is the operator's given name, in the prose of a docstring explaining that this exact shape leaks -- quoting the real path in order to warn about it |
| `tests/test_report_display.py` | **SINGLE** separator | the same drive root as the test data proving a drive-path detector fires |

One of each spelling, which is the finding rather than a curiosity: **a rule
with a one-character separator would have found one of the two and reported a
number.** That is exactly how the leak survived in `linkedin`.

The second is the shape worth naming: a hygiene fixture that proves itself by
carrying the thing it forbids is self-refuting. The detector it feeds is
`(?<![A-Za-z])[A-Za-z]:[<sep>]` -- it tests the drive letter and the separator
and **never looks at the segment**, so the name was noise in the assertion.

### 1.6 THE CLASS THE SHAPE SWEEP STRUCTURALLY CANNOT SEE

An exact-value scan run beside the shape sweep found **three more real hits, in
files the shape sweep had just certified clean**:

| file | what |
|---|---|
| `tests/test_config.py` | the operator's real name as a `candidate` fixture |
| `tests/test_policy.py` | the same |
| `tests/test_safety_invariant.py` | the same |

No pattern could have found these. `G. Aldridge` and an invented
`G. Whitfield` are the same shape, the same length, the same character
classes. **Names have no shape**, so the only instrument that works is a human
with a known string -- which is a method that finds what you already suspect
and nothing else.

Two further occurrences were adjudicated **deliberate and left untouched**:
`LICENSE` (the copyright line) and `pyproject.toml` (`authors`). These are an
author asserting authorship of his own public package. Rewriting them would
change the package's declared identity, which is not a leak and not this
wave's call.

---

## 2. The fixes, with verified counts

Applied on **bytes**, not text. The five files do not agree on line endings --
four CRLF, one LF, with `core.autocrlf=true` and no `.gitattributes` -- so a
text-mode read/write would have normalised whole files to fix one character on
one of them. Every replacement asserts: needle count before, zero needles
after, replacement present, byte delta, and CRLF count unmoved.

```
OK  src/jobcore/paths.py            1 replaced, 0 needle left, 1 present, +5 bytes, CRLF 180 unchanged
OK  tests/test_report_display.py    1 replaced, 0 needle left, 1 present, +2 bytes, CRLF   0 unchanged
OK  tests/test_config.py            1 replaced, 0 needle left, 1 present, +2 bytes, CRLF 943 unchanged
OK  tests/test_policy.py            1 replaced, 0 needle left, 1 present, +2 bytes, CRLF 527 unchanged
OK  tests/test_safety_invariant.py  1 replaced, 0 needle left, 1 present, +2 bytes, CRLF 604 unchanged
```

The byte deltas are the arithmetic check: `+5` is a 12-character angle-bracket
placeholder replacing a 7-character given name; `+2` is `workspace` for that
name, and `G. Whitfield` for the real one. Resulting diff: **five files, five
insertions, five deletions** -- one line each.

Post-fix re-sweep: the only remaining occurrences of the name anywhere in the
tree are `LICENSE` and `pyproject.toml`, both deliberate.

---

## 3. The new guard, shown failing before it was allowed to pass

`jobcore/tests/test_no_committed_path.py` ports `linkedin`'s three path rules
upstream. Every separator is a **run**, not one character. No allowlist: every
plant is composed from `chr(92)` or `chr(47)`, so the file's own text carries
no path shape and needs no exemption from its own sweep.

### 3.1 Rule 1 -- drive root, red on both REAL hits at HEAD

```
AssertionError: src/jobcore/paths.py: 1 machine path(s) in a tracked file:
  [('drive root', 'D:..ep <11 chars>')]. Replace the value with a generic root
  or a placeholder -- not with an allowlist entry, and not by escaping it
  differently.

AssertionError: tests/test_report_display.py: 1 machine path(s) in a tracked
  file: [('drive root', 'D:..ep <10 chars>')].

2 failed, 48 passed
```

The `<11 chars>` / `<10 chars>` difference is the doubled and single spellings
of the same value -- direct evidence the rule sees both. The failure never
prints the path: a CI log is a publication channel.

### 3.2 Rules 2 and 3 -- no real hits in this repo, so each broken at the defect that matters

Each rule's separator was reduced from a run to a single character -- the exact
2026-08-31 defect -- and the control caught it:

```
RULE 2  AssertionError: WINDOWS_USER_PATH is blind to a separator run of 2
        FAILED test_the_path_rules_can_match_a_backslash_at_all
        FAILED test_every_rule_can_actually_fail[user path-<doubled account path>]

RULE 3  AssertionError: POSIX_HOME_PATH is blind to a separator run of 2
        FAILED test_the_path_rules_can_match_a_backslash_at_all
```

### 3.3 The mutation battery: 9 run, 9 killed

| mutation | check that went red |
|---|---|
| drive-root separator one char, not a run | `..._can_match_a_backslash_at_all` + `..._can_actually_fail` |
| windows-user separator one char, not a run | same pair |
| posix-home separator one char, not a run | `..._can_match_a_backslash_at_all` |
| `BACKSLASH` is a slash (transport failure) | `..._can_match_a_backslash_at_all` |
| the guard REFUSES everything | `..._forms_are_allowed` + the sweep |
| the guard ALLOWS everything | `..._can_actually_fail` + `..._drive_root_rule_catches...` |
| the sweep looks at NO files | `..._sweep_actually_looked` + `..._guard_is_itself_swept` |
| a failure prints the path it caught | `..._never_prints_the_path` |
| the name-gap warning deleted | `..._name_gap_is_stated...` |

**The first pass killed only eight.** Mutating `BACKSLASH` to `chr(47)`
SURVIVED -- because the control asserted `re.match(r"[<backslash-or-slash>]",
BACKSLASH)`, and that character class matches a slash too. It could not tell a
backslash from what a broken transport had turned one into, which is the single
failure it exists to catch. Every composed value silently became a
slash-spelled path, the rules matched them all, and the control went green
while proving nothing about the spelling that actually leaks.

Now pinned with `ord(BACKSLASH) == 92`, and the mutation dies. **This defect is
also present in `linkedin`'s copy of the control, which was the model** -- see
section 6.

### 3.4 THE GUARD CAUGHT ITS OWN AUTHOR

Two plants in the new guard were written as literals rather than composed:
a drive root at an invented surname, and a POSIX home at an invented account.
The backslash plants were composed from the start because a backslash does not
survive transport; the slash forms were not, because a slash needs no escaping
-- and that reasoning missed the other half of why composition is there: **not
so the value survives, but so the file does not become the thing it hunts.**

They stayed invisible because `sweepable()` reads `git ls-files`, and **an
untracked file is not swept**. A new test file is untracked for exactly as long
as it takes to write it and run it. The guard ran green through 50 tests, a
nine-mutation battery and two full-suite runs; every one of those greens
excluded the single file guaranteed to contain path-shaped test data. The hits
appeared on the first run after the file entered the index:

```
AssertionError: tests/test_no_committed_path.py: 2 machine path(s) in a
  tracked file: [('drive root', 'D:..ft <14 chars>'),
  ('user path', '/h..ti <16 chars>')].
```

Fixed by composition from `chr(47)`, not by an allowlist -- which is what the
failure message tells the reader to do, and its author was exactly the reader
it was written for. `test_this_guard_is_itself_swept` now asserts the file is
in `git ls-files`, so "green because nothing was looked at" fails here rather
than certifying one fewer file than the reader believes.

**This is why the suite number moved from 757 to 759.** The 757 was measured
with the guard untracked and therefore unswept; **759 is the first honest
number.**

---

## 4. The pin, bumped and shown load-bearing

`linkedin_server/paths.py`: the leaked line re-vendored and the pin moved
`6acc7e6` -> `b2f5d16`. Diff is **two lines in one file**.

The body was then checked the way the pin's own test checks it -- split on the
sentinel, normalise line endings, compare nothing else:

```
OK  the leaked line   1 replaced, 0 needle left, 1 replacement present
OK  the vendor pin    1 replaced, 0 needle left, 1 replacement present

body vs canonical: IDENTICAL (8150 vs 8150 chars after newline normalisation)
non-ASCII bytes: 0
```

**The pin verifies, and it is not a decoration.** `test_vendored_buildinfo.py`
runs `git show <commit>:src/jobcore/paths.py` and compares -- and it SKIPS if
the commit will not resolve, so a green run could have meant "not checked".
Confirmed it did not skip (`8 passed`, 0 skipped), and confirmed it is
load-bearing by reverting only the pin to the old commit:

```
FAILED tests/test_vendored_buildinfo.py::
       test_the_header_pins_the_commit_it_was_copied_from[paths]
1 failed, 7 passed
```

Restored, and re-verified at `8 passed`.

**Why the pin names `b2f5d16` and not jobcore's HEAD `fff1438`:** `fff1438`
touches only `tests/test_no_committed_path.py`, which is not vendored;
`src/jobcore/paths.py` is byte-identical between the two commits (verified).
`b2f5d16` is the commit whose `paths.py` this body equals, which is what the
header claims.

---

## 5. Commits and final state

| repo | commit | contents |
|---|---|---|
| jobcore | `b2f5d16` | the 5 value fixes + the new guard |
| jobcore | `fff1438` | the guard's own literal plants composed; the self-sweep assertion |
| linkedin | `dcf0a68` | re-vendored body + pin bump |
| linkedin | this document | the audit |

Neither repo was pushed. jobcore is 2 commits ahead of `origin/master`,
linkedin 2 (this document included).

Suites:

| repo | before | after |
|---|---|---|
| jobcore | 707 passed, 0 failed | **759 passed, 0 failed** |
| linkedin | **1 failed**, 2267 passed | **2268 passed, 0 failed** |

The two checks that could not both be green are now green together
(`test_vendored_buildinfo.py` + `test_no_committed_identity.py`: 195 passed).

**HOW TO READ THE LINKEDIN NUMBER -- another agent is writing in this tree.**
At commit time the worktree also held 353 uncommitted lines across five files
this wave never touched (`dom.py`, `server.py`, `shape.py`,
`test_activity_items.py`, `test_surface_census.py`), plus a
`dom.py.mutbak` -- a live mutation-battery backup. `server.py` was modified at
18:22, during the suite run that started at 18:05.

Two things follow, and both are checkable:

* **Nothing of theirs was captured.** Every `git add` in this wave named
  explicit paths; `git status` after `dcf0a68` still shows all five of their
  files modified and unstaged, which is the receipt.
* **The number is still attributable.** Baseline was 2267 passed + 1 failed =
  **2268 collected**; the final run is **2268 passed** -- the same collected
  total, so their in-flight test additions (142 new lines in
  `test_activity_items.py`, written at 18:18) landed after collection and are
  not in either figure. The only delta between the two runs is the identity
  guard flipping from red to green.

Their WIP was left strictly alone -- not committed, not reverted, not gated.
Adopting another agent's in-flight mutation backup would have been the one
unrecoverable move available here.

`jobcore` has **no `_audit/` convention** -- checked; the directory does not
exist and no equivalent is tracked. This document is the sole record for both
repos rather than being duplicated there.

---

## 6. WHAT THIS DID NOT COVER

The brief asked for this section to be honest rather than reassuring. jobcore
is a public repo nobody had swept until today, and one sweep does not make a
repo clean.

1. **`linkedin`'s control carries the same `BACKSLASH` defect found in 3.3.**
   Its `test_the_path_rules_can_match_a_backslash_at_all` asserts only the
   character class, which matches a slash as well, so mutating its `BACKSLASH`
   to `chr(47)` would leave it green. **Not fixed here** -- it is a live guard
   in a repo whose suite this wave was asked to bring to green, and changing a
   control is not a re-vendor. Recommended as a one-line follow-up:
   `assert ord(BACKSLASH) == 92`.

   **MEASURED here, not inferred**, by loading the guard module and rebinding
   its `BACKSLASH` in memory -- the repository was not modified:

   ```
   unmutated control passes: True
   MUTATED to chr(47) -> control STILL PASSES  <-- the defect, measured
   ```

   So `linkedin`'s path rules are currently certified by a control that would
   not notice if every value it tests had silently become slash-spelled. The
   rules themselves are fine; the control guarding them is the weak link, and
   it is the same weak link this wave found and fixed upstream.

2. **Personal names, beyond one known wordlist.** Names have no shape. The
   three real hits in 1.6 were found by scanning for strings already known to
   be the operator's. **Any OTHER real person's name -- a recruiter, a
   colleague, a reference -- would not have been found by anything run today**,
   and nothing now in either repo would catch one being added tomorrow.

3. **The rest of the personal-data cluster around those fixtures.** The
   candidate fixtures also carry real locations, a real notice period, and real
   salary expectations in two currencies. Only the NAME was replaced, which
   de-attributes the cluster; the figures were left because they are not
   identifiers on their own and changing scoring inputs risks interacting with
   the golden-score gate. **Flagged for a decision, not fixed.**

4. **Git history in both repos.** Everything above is the working tree at HEAD.
   The values remain in pushed history in both repositories.

5. **Classes nobody has enumerated.** The 22 shapes were chosen by porting
   `linkedin`'s set and adding the obvious credential/network families. That is
   an inherited list, not a derived one -- the discovery curve was never
   measured, so **there is no evidence the class inventory is saturated.** The
   one class added by looking rather than by porting (1.6) was the one that
   found three hits the ported classes could not see, which is the argument
   against trusting the list.

6. **Semantic content.** Dates of birth, physical addresses, employer names,
   and third-party identifiers in prose were not swept for. jobcore's README
   (405 lines) was swept by shape and grepped for identifying markers; every
   hit was a role reference ("the operator's box") naming nobody. **It was not
   read end to end.**

7. **The other consumers -- MEASURED, and one of them is still leaking.**
   This started as "nothing in this wave looked" and was replaced by a scan,
   because the unknown was cheap to close. All eight sibling repos under
   `mcp-servers/` were swept over their TRACKED files for the three path
   shapes, matching only where the captured segment IS the given name:

   | repo | path-shaped leaks |
   |---|---|
   | **ats-jobs** | **2** |
   | instahyre, jobcore, jobspy, linkedin, naukri, unipile, uplers | 0 |

   `linkedin` is the ONLY repo carrying a vendored copy of jobcore's
   `paths.py` (`instahyre`'s same-named file is its own, with no vendor
   header), so the re-vendor in section 4 covers the vendoring completely.

   **But `ats-jobs` carries two of the same class, and this wave did not touch
   it** -- it is outside the two repos in scope, it is separately public, and
   the push is not this wave's to make:

   * `ats_buildinfo.py:5` -- a comment quoting the machine's full absolute
     path, introduced to say where the sibling checkout sits "on this box"
   * `tests/test_no_path_leaks.py:93` -- the full absolute path as test data,
     **in a file named `test_no_path_leaks.py`**

   Both are the single-separator spelling. The second is the third instance
   today of the self-refuting fixture: a check proving it detects path leaks
   by carrying one. That shape has now appeared in `jobcore`, in `linkedin`
   (per the previous wave), and here -- it is a pattern in how these guards
   get written, not three coincidences.

   **Recommended as its own slice**, with the same two rules this wave used:
   replace the value rather than the escaping, and port the guard so the
   repo can never regress. Not taken here.
