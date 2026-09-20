# The sanitiser scope hole: a proof about urls, spent on page text

2026-09-20. Wave: `agent-af424fc78eff65855`, branch `worktree-agent-af424fc78eff65855`.
Started from `9f50087`; **fast-forwarded to `d6b7e4b` mid-wave** and every measurement
below was re-run on that base -- see section 7 for why, and for what moved.
Written as the work ran, in order.

**One sentence.** `tests/test_page_text_is_never_printed.py` imported the url rule's
`_is_sanitiser_call` and ORed it into a taint walk whose sources are sixteen text
readers, so a page-text site wrapped in any of `_redact`, `_shape_of` or `_relation`
was reported CLEAN on the strength of a certification whose entire corpus is urls --
and one of those three returns an invented display name byte-identical on three of six
realistic page-text shapes. Both halves are fixed: the page-text guard no longer
consults the url-proven set, and the certifier now records what each guarded name is
proven for and asserts structurally that a guard may only stop at entries proven for
its own kind of value. **The live tree moves by zero**, measured pre against post with
a control showing the two walkers genuinely differ.

---

## 1. The red, watched first

Note for anyone reproducing: `venv/` is gitignored, so it does **not** exist inside a
worktree. The interpreter throughout is the MAIN CHECKOUT's
`venv/Scripts/python.exe`, invoked by absolute path with the worktree as cwd. That is
the standing worktree trap, hit again here.

Baseline before anything was touched:

```
$ venv/Scripts/python.exe -m pytest tests/test_page_text_is_never_printed.py \
                                    tests/test_a_sanitiser_earns_its_entry.py -q
100 passed in 15.97s
```

### 1.1 The bypass, reproduced on this tree, and it is WIDER than reported

Section 4c of `_audit/2026-09-20-the-loop-binding-hole.md` demonstrated the hole for
`_redact` in the nested spelling. Re-run here against `B.text_violations`:

```
_SANITISERS      : ['_redact', '_relation', '_shape_of']
TEXT_SANITISERS  : []

STEP 1  wrapped, one-step    -> []
STEP 2  unwrapped control    -> [(2, 'print')]
STEP 3  wrapped, two-step    -> []
STEP 4  _shape_of on text    -> []
STEP 5  _relation on text    -> []
STEP 6  attribute spelling   -> []
```

STEP 2 is the control that makes STEP 1 mean something: the walker still flags the
unwrapped site, so the `[]` above is a silencing and not a walker that has stopped
working. **All three names, both call spellings, and both binding forms** -- the
predecessor reported one name in one spelling.

### 1.2 The red as a check, failing on unfixed code

Five cases added to `tests/test_page_text_is_never_printed.py` as
`_SCOPE_RED_CASES`, run before the fix:

```
FAILED tests/test_page_text_is_never_printed.py::test_a_url_proven_sanitiser_does_not_clear_page_text[0]
FAILED tests/test_page_text_is_never_printed.py::test_a_url_proven_sanitiser_does_not_clear_page_text[1]
FAILED tests/test_page_text_is_never_printed.py::test_a_url_proven_sanitiser_does_not_clear_page_text[2]
FAILED tests/test_page_text_is_never_printed.py::test_a_url_proven_sanitiser_does_not_clear_page_text[3]
FAILED tests/test_page_text_is_never_printed.py::test_a_url_proven_sanitiser_does_not_clear_page_text[4]
5 failed, 1 passed, 14 deselected in 0.26s

E       AssertionError: the attribute spelling, which the predicate also matched
E       assert []
E        +  where [] = text_violations('name = await item.inner_text()\nprint(helper._redact(name))\n')
```

**The one that PASSED is the point of the block.** Every assertion in the new group is
of the form *this is flagged*, and a walker that flagged everything would satisfy all
five while being useless. `test_this_rule_still_flags_something_so_the_block_above_is_not_vacuous`
asserts, in the same breath, that the raw print is still caught AND that `len(name)`
and `"needle" in text` are still clean. It passed then and passes now.

---

## 2. Which direction, and the measurement that decided it

The ruling offered two: narrow the USE, or widen the PROOF. **Both shipped**, and the
reason they are not redundant is that they fail differently -- but the evidence that
picked the order was not an argument, it was three readings.

### 2.1 Every claimant, against page text and against the url it was proven for

16 enrolled claimants, six page-text shapes, every needle invented (`Jane Doe`,
`Jane Q Public` and `Northwind` are already committed fixture values in
`tests/test_probe_redaction.py`, `tests/test_surface_census.py` and
`tests/test_apply_fixture.py`; `some-real-slug-99` is in `SYNTHETIC_SLUGS`):

```
claimant                                          leaks    byte-ident  url needle survives
_probe_messaging.py::_redact                      3 of 6   3 of 6      no
...the other fifteen                              0 of 6   0 of 6      no

PER-CASE:
  _probe_messaging.py::_redact   card byline; plain prose; name beside a lowercase word

TOTALS: 16 claimants, 1 leaks at least one page-text shape, 0 leak the url
```

The predecessor's 3-of-6 reproduces exactly. **And the fifteen that hold do not hold
because anyone proved they would** -- `_shape_of` and `_relation` are url-relation
functions whose branches return a literal or an integer path depth, so nothing of any
input survives whatever you hand them. They hold on page text incidentally. That is a
property nobody measured until this file measured it, which is the whole disease.

### 2.2 The decisive reading: the repository had already ruled this, twice, in prose

This is what settled the direction, and it is a documentary measurement rather than a
preference.

* `tests/test_page_text_is_never_printed.py`'s own docstring: *"Only the taint SOURCES
  and the sanitiser list differ, which is exactly the thing that should differ."*
* The same file on `TEXT_SANITISERS`: *"DELIBERATELY EMPTY, AND THAT IS THE FINDING
  RATHER THAN A GAP."*
* `tests/test_navigation_is_never_derived.py`'s drift test, about its sibling: *"their
  sanitiser sets differ (three entries here, a deliberately EMPTY one there, which is
  that file's finding rather than a gap)."*

**All three are false as executed**, and they were false because of one `or`. So
narrowing the use is not a new policy anybody has to weigh: it is making the code obey
a ruling that is already written down in two files, one of which is the very file that
was violating it. It silences nothing, changes no decision anyone made, and the thing
it "breaks" is a behaviour three docstrings deny exists.

That is why NARROW went first and is the half I would ship alone if I could ship only
one.

### 2.3 Why WIDEN could not be the naive version, and what it became instead

The obvious form of "widen the proof" -- *every `_SANITISERS` entry must also survive
prose fixtures* -- is wrong, and measurably so. It would force one of two outcomes on
`scripts/_probe_messaging.py::_redact`:

* drop it from `_SANITISERS`, which breaks the url rule it legitimately serves and for
  which it is correctly proven; or
* over-redact it until it passes, which is the `return ''` failure the certifier
  already has two controls against, and which that function's own source records itself
  making twice while it was being written.

And the repository has already measured the general instrument impossible: *"this
package has no instrument that can decide whether a string is a person's name."*
Demanding a universal prose proof demands that instrument.

So WIDEN shipped as the predecessor's option 2: **an entry declares what it is proven
for, and a guard consults only entries proven for its own kind.** `PROVEN_FOR` maps
each guarded name to its kind; all three say `SCOPE_URL`, because the certifier's
needle table is eight url-bearing lines and that is the only demonstration any of them
has. `GUARD_SCOPE` says which guard taints which kind. A structural test asserts the
two agree.

### 2.4 What I did NOT do, and why

**`_SANITISERS` is still a frozenset of names.** Turning it into a name-to-kind mapping
was the tempting version and I declined it. It is pinned by literal copy in two files,
imported as a symbol by two more, and named in prose in twenty; the URL rule's use of it
is entirely CORRECT; and three sibling waves are appending to `ENROLLED` in the same file
today. Editing a shared symbol across a parallel-wave day to record a fact that belongs
to the certifier buys nothing the separate mapping does not. The name set stays; what a
name PROVES is declared next to the table that proves it.

---

## 3. The fix

### 3.1 NARROW -- `tests/test_page_text_is_never_printed.py`

`_is_sanitiser_call` is no longer imported, and the stop is now
`if _is_text_sanitiser_call(child):` alone. `_COUNTING_CALLS` and `_sink_calls` are
still imported -- the engine stays shared, exactly as that file's docstring says it
should.

The distinction that is now written into `_reads_page_text`: **a carve-out is not one
thing.** `len(x)` is an integer whatever `x` was, and that argument transfers to any
kind of value. *"This function's result carries none of its input"* does not transfer --
it is a claim proved against a specific corpus, and that corpus was urls. Importing the
second kind alongside the first is the whole defect.

### 3.2 WIDEN -- `tests/test_a_sanitiser_earns_its_entry.py`

New: `SCOPE_URL` / `SCOPE_TEXT`, `PROVEN_FOR`, `GUARD_SCOPE`, `URL_PROVEN_PREDICATE`,
`TEXT_NEEDLED`, `_names_used`, and five tests.

`test_a_guard_consults_only_sanitisers_proven_for_its_own_kind` asserts
`consults == (kind == SCOPE_URL)` -- **both directions in one assertion, deliberately.**
Written one-sided ("the text guard must not name it") the check would still pass if the
URL rule LOST its own stop, which would silently forbid that rule's own fix -- the thing
`_SANITISERS` exists to prevent.

`_names_used` parses rather than greps, and counts an import with no call: a symbol
sitting in a namespace is one word from being a stop condition again. It is shown
rejecting a docstring that mentions the name, which is what a grep would have matched --
this file's prose says `_is_sanitiser_call` a dozen times.

### 3.3 One constant renamed before commit, on a measurement

The scope constants were first written `URL` and `TEXT`. `scripts/pre_commit_boundary_gate.py`
couples test files by whole-word uppercase constant name longer than three characters,
so `TEXT` qualified and `URL` did not. Measured: `TEXT` dragged in **zero** files beyond
what `ENROLLED`, `REQUESTED`, `MUST_DISCRIMINATE`, `ONE_ARG`, `TWO_ARG` and
`KNOWN_TEXT_SINKS` already drag -- 6 either way. But that is today's reading, and a
generic four-letter constant will drag files the moment anyone writes the word. Renamed
to `SCOPE_URL` / `SCOPE_TEXT` for nothing. The gate still computes 6 coupled files.

**The rename was done with a regex and the regex over-reached into prose** -- "shapes a
SCOPE_URL safely", "SIXTEEN SCOPE_TEXT READERS", four `:data:` references. Caught by
reading every occurrence back rather than by a test, because no test reads prose.
Repaired; 22 occurrences checked by hand.

---

## 4. Shown failing -- every new check, each mutated on its own

The register's condition of entry, and the fleet's law that two overlapping defences
hide each other's death. This wave ships two mechanisms that both cover the same case,
so they are mutated **separately**.

### 4.1 The structural check, against the REAL pre-fix source

Not a stub -- `git show HEAD:tests/test_page_text_is_never_printed.py`:

```
A.  test_a_guard_consults_only_sanitisers_proven_for_its_own_kind
  HEAD source names _is_sanitiser_call    : True      <- RED
  working source names _is_sanitiser_call : False     <- green
  the url rule itself names it            : True      <- and must
```

### 4.2 The two mechanisms, mutated separately

```
B.  MUTATE THE FIX BACK. Restore the OR in the page-text walker, in memory only.
  mechanism (a), the walker    : 5 of 5 scope red cases go RED under the restored OR
      'print(_redact(name))'                 -> []
      'print(shaped)'                        -> []
      'print(_shape_of(name, ASKED))'        -> []
      'print(_relation(name, ASKED))'        -> []
      'print(helper._redact(name))'          -> []
  mechanism (b), the certifier : structural check RED on ['test_page_text_is_never_printed.py']
```

Each fires on its own. Removing either leaves the other convicting the restored defect.

### 4.3 The remaining new checks

```
C.  each mutated on its own
  test_every_guarded_name_declares_what_it_is_proven_for  (row removed)
      RED  these guarded names declare no proven kind: ['_redact']
  test_no_claimant_declares_page_text_without_surviving_the_text_table  (_redact declared TEXT)
      RED  _probe_messaging.py::_redact declares it is proven for page text and
           returned the display name in a card byline
  test_the_text_table_catches_the_claimant_..._leaking_prose  (only holding shapes left)
      RED  TEXT_NEEDLED no longer catches the claimant it was built from
  test_the_text_table_is_not_a_rejecter_that_rejects_everything  (aimed at the leaker)
      RED  ['a card byline', 'plain prose', 'a display name beside a lowercase word']
  test_the_scope_check_would_notice_a_guard_reaching_outside_its_kind  (_names_used gutted)
      RED  the defect itself, in four lines, and the predicate did not see it

  5 of 5 shown failing
```

### 4.4 The vacuous loop, declared rather than disguised

`test_no_claimant_declares_page_text_without_surviving_the_text_table` **checks zero
claimants today**, because nothing declares `SCOPE_TEXT`. Its docstring says so in the
first line. That is the honest state, and it is armed: declaring the measured leaker
`SCOPE_TEXT` turns it red (4.3, row 2). The two table controls are what make
`TEXT_NEEDLED` real rather than decorative -- one shows it convicting a real shipped
function, the other shows it acquitting a different real function of the same name.

The same file's sibling shows the alternative I avoided: `tests/test_a_verdict_earns_its_entry.py`
has **four tests that SKIP** with *"got empty parameter set"*. A parametrised test over
an empty table does not announce that it checked nothing; it announces a skip, which
reads like a pass. A plain loop with an asserted count does announce it.

---

## 5. What the fix flags that it did not flag before: measured, and it is zero

### 5.0 The children shared this worktree, and that is where 5.1 came from

**Both children ran IN this worktree**, not in isolated ones -- `or-sweep`, which did
the corpus sweep, and `global-binding`, which did section 7's measurement. Each was
briefed to write its deliverable to a FILE in the scratchpad and to touch nothing
tracked, and that held: `git status` through the whole wave showed only my own two
edits, and their outputs live at
`scratchpad/scope/or-sweep.md` and `scratchpad/scope/global-binding.md`.

**What I did NOT do, and should have:** hand the measuring child a FROZEN SNAPSHOT --
`git stash create`, read back through `git show <sha>:<path>` -- instead of telling it
to record `HEAD` and check `git status` was clean. Those are not the same guarantee.
The second says *the corpus was clean when you looked*; only the first says *the bytes
you are measuring cannot move*. I was editing `tests/` while it measured, and although
its swept corpus (`scripts/` + `linkedin_server/`) genuinely did not move, **the
INSTRUMENT it imported did** -- and the instrument is part of the measurement.

That is the whole of 5.1, and it is the one mistake in this wave that a documented
practice would have prevented outright.

### 5.1 The first attempt at this number was INVALID and its own control said so

I briefed a child to sweep the tree with two walker variants, taking "or-on" by
importing `text_violations` from the real module. **I then edited that module
underneath it.** Both of its variants were the fixed walker, so they agreed on all 178
files -- a zero that measured nothing.

The control caught it. The brief required the two variants to be shown DISAGREEING on
planted cases first, and the child reported `CONTROL 2 overall: FAIL` and did not
present the agreement as a result. The defect was in my brief, not its work: a corpus
I told it to read went stale while it read it.

### 5.2 The corrected sweep -- both walkers built from source text

Pre-fix loaded from `git show HEAD:...`, post-fix from disk, neither imported from a
tree in motion:

```
pre-fix  walker names _is_sanitiser_call in its namespace : True
post-fix walker names _is_sanitiser_call in its namespace : False

CONTROL -- the two walkers MUST disagree on a planted case
  wrapped one-step               pre=[]             post=[(2, 'print')] DISAGREE
  wrapped two-step               pre=[]             post=[(3, 'print')] DISAGREE
  _shape_of                      pre=[]             post=[(2, 'print')] DISAGREE
  _relation                      pre=[]             post=[(2, 'print')] DISAGREE
  attribute spelling             pre=[]             post=[(2, 'print')] DISAGREE
  UNWRAPPED -- both must flag    pre=[(2, 'print')] post=[(2, 'print')] agree
  len() -- both must stay clean  pre=[]             post=[]             agree
  -> 5 of 7 planted cases disagree

THE LIVE TREE
corpus: 179 files
pre-fix  total sites: 111 across 25 files
post-fix total sites: 111 across 25 files

FILES THE FIX NEWLY FLAGS   : 0  (none)
FILES THE FIX STOPS FLAGGING: 0  (none)

AND AGAINST THE PINNED INVENTORY (an exact mapping, both directions):
  pinned total  : 111 across 25 files
  post == pinned: True
```

The two "agree" rows are as load-bearing as the five "DISAGREE" ones: they show the
variants agree exactly where they must, so the disagreement is the one condition and
not two different programs.

### 5.3 Why the zero is credible rather than lucky

There are **28 call sites** of the three guarded names across 18 files in the corpus
(`_redact` 3, `_relation` 14, `_shape_of` 11). So the sweep had something to look at and
the zero is not an absence of subject matter. Every one of those 28 sits on a
url-tainted value, never a text-tainted one -- which is exactly what you would expect
from three functions whose job is url relations, and it is the mechanism behind the
zero.

**Live instance count after the fix: 0.** Nothing red; nothing exempted.

---

## 6. Name-based matching: can the stop resolve the actual function?

Asked directly by the brief. **The honest answer is no, not at this instrument's cost,
and the two-`_redact` collision is therefore a documented limitation rather than a
surprise waiting for someone.**

The facts, measured:

* `scripts/_probe_messaging.py::_redact(value: str)` is a pattern list plus a
  capitalised-run collapse. It leaks 3 of 6 page-text shapes.
* `scripts/_probe_search_render_timeline.py::_redact(url: str)` is allowlist-based --
  membership, not absence. It holds all 6.
* The guard sees `func.id in _SANITISERS` and cannot tell them apart.

**Why resolution is not available here.** These guards are pure AST analysis over source
text, per module, and deliberately so: `tests/test_navigation_is_never_derived.py` states
that the rest of the file "must not need the package", and the one test that does import
`linkedin_server` says so at the import. Resolving a call to a definition needs either
(a) an import graph plus scope analysis -- real work, and it still cannot resolve a
rebinding, a dict of functions, or a call through a parameter; or (b) actually importing
all 179 scanned modules, which means executing them, which for a directory of live
browser probes is not a thing a test suite may do. Every scanned file is standalone by
design, which is what makes a name the only handle there is.

**What is available, and what this wave did instead.** The name stays the handle, and
the cost of the name is raised until it is not free:

* ENROLMENT already makes a new claimant of a guarded name fail until somebody writes
  down what it promises (pre-existing).
* `test_every_relation_definition_is_byte_identical` already refuses two different
  bodies under one name -- and has, once, on a wave that shipped a four-branch variant
  (pre-existing). **It covers `_relation` only. Two different `_redact` bodies are
  permitted today**, and that is the collision, unfixed.
* `PROVEN_FOR` (this wave) makes the name carry its corpus, so the name can no longer
  be spent outside what it was measured against.

**The residual, stated plainly:** if someone writes a third `_redact` in a new probe,
enrolment will demand a row and the url table will demand it hold the url needles --
but nothing asserts the three `_redact` bodies are one function, the way `_relation`'s
are. Extending `test_every_relation_definition_is_byte_identical` to `_redact` is NOT
available as a like-for-like: the two bodies are genuinely different functions doing
genuinely different jobs, so the honest repair is the predecessor's option 3, a RENAME,
and a rename vouches for nothing, which is why it is available to anyone and was not
taken unilaterally here. **I am leaving it, named, for its owners.**

---

## 7. The correction to a merged claim -- verified, and ALREADY LANDED BY SOMEBODY ELSE

Separate from the scope fix; folded in because I had the harness. **The measurement
stands and the edit was not mine to make, because a sibling had already made it.** The
sequence is worth keeping, because the failure mode it avoided is the one this whole
repository keeps re-finding.

### 7.1 What I measured

The claim, in `tests/test_navigation_is_never_derived.py`'s `_bindings()` docstring and
in `_audit/2026-09-20-the-loop-binding-hole.md`'s binding table: `global` / `nonlocal`
rebinding is **STILL BLIND**. `binding-census` challenged it. An earlier attempt to
reproduce the challenge got an EMPTY set from both variants -- which distinguishes
nothing -- so the positive control was built first:

```
positive control        : [(2, 'print(landed)')]        <- harness alive
WITH global             flagged=True   tainted=['LEAK', 'landed']
WITHOUT global          flagged=True   tainted=['LEAK', 'landed']
global + For target     flagged=True   tainted=['LEAK']
_bindings classes on WITH global: ['Assign']            <- no Global, as pinned
```

`global LEAK` and `LEAK = landed` are two statements: the declaration is inert and the
`ast.Assign` beneath it is handled like any other. **The claim was false.** The narrow
true fact -- `_bindings` does not dispatch on a bare `ast.Global` node -- survives, and
is what `test_the_two_walkers_bind_the_same_forms` actually pins.

The third row is mine and neither the challenger nor my child ran it: it is the shape
the old claim would NEED in order to be true, a `global` rebinding with no `Assign`
anywhere, and the `for` handling caught it too.

### 7.2 And then I found it already fixed on master, better than I had it

I had written the correction into both files. Before committing, checking my base
against the remote showed I was **32 commits behind and 0 ahead**, and that master
carried `42f55b2 guard: global/nonlocal rebinding is SEEN, and I shipped it as blind`.

Its version is better than mine and I dropped mine for it. It carries a **38-row census
with a positive AND a negative control on every row** where I had four cases, it settles
nine more binding forms I had not touched, and it root-causes the original error in a way
I could not have: the author's probe passed the tainted value in through a **function
parameter**, and parameters genuinely ARE blind -- *"I measured the parameter hole and
filed it under the global row."*

**So this wave's contribution here is a second independent measurement agreeing with
`binding-census`, and nothing else.** I reverted my edits to
`tests/test_navigation_is_never_derived.py` and `_audit/2026-09-20-the-loop-binding-hole.md`,
fast-forwarded to `d6b7e4b`, and re-applied only the scope fix -- which master had not
touched, so it applied clean.

### 7.3 Why this is in the audit rather than quietly dropped

Three things came out of it that are worth more than the edit would have been:

1. **I would have shipped a duplicate correction to two files three waves are editing.**
   Nothing warned me. The only reason I did not is that I checked my base against the
   remote before committing rather than after -- and I only did *that* because the
   identity gate went red and sent me looking at `origin/master`.
2. **The identity gate red was itself stale.** `_audit/2026-09-20-the-loop-binding-hole.md`
   carried an absolute workspace path with the operator's real name at my base
   `9f50087`. It is fixed on master at `710dd08 identity: an absolute workspace path put
   a real name in a public repo`. My branch point predated the fix. **The name was
   published and has since been corrected at the tip; published history retains it,
   which is this repository's own standing finding about force-pushes and is not this
   wave's to re-litigate.** What I verified: the current `origin/master` line reads
   `./venv/Scripts/python.exe`, and no tracked file in my tree carries a drive root now.
3. **My own new audit file had the identical defect** and the gate caught it --
   I had pasted the same absolute interpreter path into section 1. Removed. The gate
   that caught somebody else's instance caught mine in the same run.

---

## 8. The suite

The three guards plus the **six files `scripts/pre_commit_boundary_gate.py` computes as
coupled** to the staged set -- not a list I chose:

```
594 passed, 4 skipped in 31.98s
```

and the guards that READ AUDIT PROSE, because this wave writes an audit file, edits
nothing else's, and appends to the register:

```
tests/test_no_committed_identity.py
tests/test_an_asserted_name_resolves.py
tests/test_a_correction_is_findable_from_the_claim.py
tests/test_the_register_numbers_are_unique.py
tests/test_probe_controls_are_never_decorative.py
    -> 648 passed in 32.06s
```

The last three of those did not exist at my original base; two arrived with the 32
commits I fast-forwarded over. **Running them was not optional and not foresight --
it is the direct consequence of section 7 making me look at the remote.**

The 4 skips are pre-existing empty-parameter-set skips in
`tests/test_a_verdict_earns_its_entry.py`, discussed at 4.4.

---

## 9. The ledger

**What is measured, with the instrument named:**

* The bypass, all three names, both spellings, both binding forms -- `text_violations`
  on synthetic source, with the unwrapped control.
* 3 of 6 page-text shapes returned byte-identical by `_probe_messaging.py::_redact`;
  0 of 6 by the other fifteen claimants; 0 of 16 leak the url. Direct calls through the
  certifier's own `_call`.
* 0 files newly flagged, 0 files unflagged, 179-file corpus, pre-fix walker loaded from
  `git show HEAD:` and shown disagreeing with the post-fix walker on 5 of 7 planted
  cases.
* `post == KNOWN_TEXT_SINKS` exactly, an assertion that fails in both directions.
* 28 call sites of the three names in the corpus, so the zero is not vacuous.
* 5 of 5 new checks shown failing, each mutated separately; both mechanisms mutated
  separately.
* 6 coupled test files, computed by the repository's own gate, before and after the
  constant rename.
* `global` / `nonlocal` seen, not blind, with a positive control.

**What is NOT measured, and is not claimed:**

* **I did not run the full 6110-test suite locally.** Nine files ran; the other ~150 did
  not. CI is the instrument for that, and section 10 carries its reading. Until then the
  honest claim is *the guards and everything the gate computes as coupled are green*,
  not *the tree is green*.
* **No live probe was executed.** Nothing here touches runtime behaviour -- the change
  is to two test files and two prose sites -- but "the probes still work" is not
  something this wave measured.
* **The six page-text shapes are six, not a census.** They are the predecessor's set,
  re-run. A seventh shape that some claimant leaks would not have been seen.
* **`_names_used` is syntactic.** A guard that reached the url-proven set through a
  computed attribute, `getattr`, or a star-import re-export would not be caught. Stated
  rather than discovered: this is the same class of limit as the name-based stop itself.
* **The 0-leak result for the fifteen non-leaking claimants is a property of their
  current bodies**, re-measurable and not asserted anywhere as a standing check. They
  declare `SCOPE_URL`, so nothing depends on it.
* I did not verify the predecessor's historical numbers (the 81-to-79 measurement, the
  "111 sites, 25 files" header). The 111/25 figure I did re-derive, and it matches.

**What I chose not to do, deliberately:**

* Did not reshape `_SANITISERS` into a mapping (2.4).
* Did not touch either `_redact`, or rename one (6).
* Did not add an entry to `TEXT_SANITISERS`. It remains empty, which is now true in
  effect as well as in prose.
* Did not merge the two walkers and did not add `AugAssign` to one side. The drift
  detector is untouched and still fires in both directions -- `_bindings` was not
  edited, only the prose above it.
* Did not edit `linkedin_server/readonly.py` or the allowlist.

**A defect found and counted rather than re-reported:** the file
`tests/test_navigation_is_never_derived.py` carries a section header reading
*"`_why_refused` -- admitted to _SANITISERS 2026-09-19"*. It is **not** in
`_SANITISERS`, which is `{_shape_of, _redact, _relation}` and nothing else. Nor is it
in the sibling `VERDICTS` list, which is empty and which
`tests/test_a_verdict_earns_its_entry.py` records measuring it and **REFUSING** it
("one return interpolates a runtime token"). What it actually has is its own
adversarial test in the navigation guard file, which is real and which passes. So the
header names an admission that never happened, to a list the function is not on. One
header, one wrong claim, not this wave's to fix -- logged here so the next reader of
that file does not act on it. It is the same class as section 7's correction: prose
asserting something about the code that the code does not do.

**MY OWN DEFECT, COUNTED RATHER THAN REPORTED TWICE.** I renamed a constant with a
blind regex and it over-reached into prose -- "shapes a SCOPE_URL safely", "SIXTEEN
SCOPE_TEXT READERS", four `:data:` references. I repaired that, and then **made the
identical mistake an hour later** on a scratchpad probe, turning
`C.URL_PROVEN_PREDICATE` into `C.SCOPE_URL_PROVEN_PREDICATE` and breaking the receipt
run. **Two instances, same tool, same hour, and the second one happened after I had
written the first one up.** Neither reached a tracked file, because both were caught by
reading every occurrence back -- which is the only control there was, since no test in
this repository reads prose for sense. The general form, worth more than the instances:
**a rename by pattern is a rename of every STRING that matches, and identifier renames
in a corpus this prose-heavy need the match anchored or the occurrences read back.**

**HARVESTED:** `_audit/INSTRUMENTS.md` section **31** -- 31.1 the scope law and its
both-directions assertion, 31.2 the before/after sweep instrument and the stale-corpus
trap that convicted it, 31.3 the declared-vacuous loop against the silently-skipping
parametrize, 31.4 the name-based stop and its named residual. Numbered 31 as max-plus-one
after re-reading the register at `d6b7e4b` (master had added 30 while this wave ran);
`tests/test_the_register_numbers_are_unique.py` green.
