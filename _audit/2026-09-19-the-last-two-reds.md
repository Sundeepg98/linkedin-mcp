# The last two reds, and the third one that was hiding behind them

Wave `last-two`, 2026-09-19. **Every number carries the time it was taken.**

The brief: clear `test_a_person_name_is_never_a_literal` and
`test_page_text_is_never_printed`, then land
`tests/test_navigation_is_never_derived.py`, held since 13:00.

**All three landed.** A fourth commit was needed that the brief did not
anticipate, and it is the most interesting thing in this file.

---

## 0. WHAT LANDED

    db453e7  14:27:05  guard(probes)      the page-text inventory, 34 sites
    36cbb19  14:27:40  guard(identity)    the needle declaration
    4cc53f9  14:38:44  guard(identity)    a diff marker is not a local part
    889f488  14:42:39  guard(navigation)  THE HELD FILE

`889f488` is verified present at `HEAD`: `_relation_arity` appears twice in
`git show HEAD:tests/test_navigation_is_never_derived.py`, and
`git status` reports the path clean.

**AI attribution across `origin/master..HEAD`: 0.**

---

## 1. THE BRIEF'S COUNT WAS STALE, AND SAYING SO IS THE POINT

The brief said **35 sites**, with `_probe_add_section_menu.py` at **6**.
Measured with the guard's own engine at 14:05: **34**, with that file at **5**.

`5655bf1` took one of them at **13:41**, between the reading and the brief.
Nothing was wrong with the brief; a relayed count is a reading with a
timestamp the receiver cannot see. Re-measured rather than assumed.

---

## 2. THE 34 WERE THREE DIFFERENT DEFECTS WITH THREE OPPOSITE REPAIRS

The brief's instruction to check each site with the guard's own engine rather
than by eye is what produced this split. Reading the lines would have
produced one repair applied 34 times, and it would have been wrong wherever
the value was never the page's.

> **CORRECTION TO `db453e7`'s COMMIT MESSAGE, RECORDED HERE BECAUSE HISTORY IS
> NOT REWRITTEN FOR IT.** That message gives the three classes as *11 + 21 +
> 3 sites*, which sums to **35** against a measured **34**.
>
> The error is not the total -- **34 -> 0 is the measured number and it is
> right** -- it is that the message presents the classes as a PARTITION of the
> sites. They are not one. Several sites carried two defects at once: the four
> `partition_word` prints in `_probe_small_measures_followup.py` needed BOTH a
> rename (`part` was shared with the control) AND `len()` on the returned
> pieces, so counting them under each class counts them twice.
>
> **They are kinds of defect, not buckets of sites**, and a site could hold
> two. The only exact counts in this file are **34 flagged, 0 remaining, 3 of
> them real leaks.**

### 2a. NAME COLLISIONS. NOT LEAKS AT ALL.

The analysis is **per module and keyed on the NAME**. Two cases:

* `run_detector_control` in `_probe_add_section_menu.py` binds `label`,
  `href`, `haspopup`, `expanded` from `CONTROL_CASES`, a fixture in the file.
  **It runs offline with no page open.** The live scanner below binds those
  same four names from `node.get_attribute`, and a name tainted anywhere in a
  module is tainted everywhere in it.
* `_probe_small_measures_followup.py` bound a page's `aria-label` to `label`
  -- which is the **PARAMETER NAME** of `_page_control` and `_goto`, two
  surface labels this repository wrote. Three prints that never touched a
  page were flagged. Same for `partition_word`'s `html` parameter and its
  internal `total`, and for `part` shared between the control and two live
  readers.

**REPAIR: RENAME.** Shaping these would have asserted they were the page's.

### 2b. COUNTS THE ENGINE CANNOT SEE.

`_COUNTING_CALLS` is `frozenset({"len"})` and matches only a bare `ast.Name`.
So `html.count(needle)` is an **integer** that the guard flags, and so is a
helper: handing a tainted name to **any** call taints that call's result.

**Taint does not cross a function boundary here, so no helper can ever launder
it.** A first attempt at the ARIA repair used a tidy
`_one_of(value, allowed, label)`; the engine correctly flagged
`pop_shown`/`exp_shown`/`role_shown` instead, and the helper was removed with
the reason recorded at the site. The same finding is written into `_count`'s
docstring in `_probe_small_measures_live.py`, which is kept for the control
and is unusable on page text.

**REPAIR: `len(h.split(n)) - 1`** -- the same integer, since `str.count` and
`str.split` are both non-overlapping -- in the one counting form the guard
reads through.

**`.count` WAS NOT ADDED TO `_COUNTING_CALLS`**, though one line would have
cleared most of these. That list matches **BY SPELLING** and the carve-out does not
descend, so the exemption would cover every `.count` in the repository and
everything inside one. This repo already paid for an exemption earned by a
name when the engine trusted a classifier called `_relation`. **The instrument
is unchanged; only the probes moved.**

### 2c. REAL LEAKS -- 3 sites, and they are exactly 3. THE GUARD WAS RIGHT.

Three prints handed a heading or a legend to `shape.census_shape`. The guard
measured that function and recorded what it is: a **length and charset gate
that returns a short plain name UNCHANGED**.

`_probe_small_measures_followup.py` carries the incident **in its own printed
output**:

> "The first version of this block printed `shape.census_shape(name)` and THAT
> LEAKED THE OPERATOR'S OWN NAME TO STDOUT."

**The identical call sat uncaught in `_probe_small_measures_live.py`** -- its
twin, written the same morning -- under a heading that promised *"No option
text is printed."* The wave that fixed the first did not know to look at the
second.

**The instrument found it, not a person.** That is the whole argument for the
guard, arriving on its first real sweep.

---

## 3. EVERY SITE, AND WHAT IT NOW EMITS

| file | site | now emits |
|---|---|---|
| add_section_menu | 211 | control loop **renamed** (`case_*`); collision, not a leak |
| | 285 | `len(split)-1` counts |
| | 344 | aria matched vs file-owned tuples; `controls` via a membership compare |
| | 411 | cleared by the count fix (`count`, `index` untainted) |
| | 421 | `runs` matched vs `RUN_COUNTS`; `tail` reduced to a length |
| creator_content_analytics | 237, 238 | `hits` dict via `len(split)`; `word`, `n` cleared |
| | 250, 281 | `EXPECTED_VOCAB` match + `len(raw)`, replacing `census_shape` |
| | 284 | `feed_hits` via `len(split)` |
| off_platform_controls | 141, 146 | `len(split)-1` counts |
| small_measures_followup | 162, 164 | cleared by the `partition_word` renames |
| | 180, 195, 199 | cleared by renaming the aria read to `aria_label` |
| | 187 | `len(split)-1` counts |
| | 221 | cleared by removing the internal `total` collision |
| | 257 | `expanded` matched, `runs` matched, `tail` -> length |
| | 274, 349, 350, 351 | partition **pieces**, counted with `len()` |
| | 315, 354, 359 | `len(split)-1` counts |
| small_measures_live | 236, 251 | `len(split)-1` counts |
| | 327, 423 | cleared by the `total` fix |
| | 337 | `legend_len`, replacing `census_shape(raw)` |
| | 400, 401 | `len(split)-1` counts |

**`KNOWN_TEXT_SINKS` is unchanged. `TEXT_SANITISERS` is still empty. Nothing
was declared anywhere.**

---

## 4. `partition_word` RETURNS THE PIECES NOW, AND WHY THAT WAS THE ONLY OPTION

It is called on `CONTROL_HTML` by the control and on live content by the
readers, so its result was tainted and **no caller could print it**.

* Duplicating the arithmetic at the live sites would have left the control
  certifying code the live path no longer runs -- **worse than the red**.
* Declaring it a sanitiser would have been an exemption earned by its name.

Returning the pieces keeps **one implementation under the control** and puts
the count in `len()`. The partition arithmetic becomes visible at the call
site, which is where it is checked anyway.

**SHOWN EQUIVALENT, AND THE CHECK SHOWN FAILING** (14:24):

    detector control, CONTROL_HTML   total 4, in_script 3, outside 1, sums PASS
    4000 randomised documents        0 mismatches vs the HEAD implementation
    a variant with the NUL join
    separator removed                caught on 19 of them

The third line is the point. Without it the first two only prove the harness
agrees with itself. The separator stops a needle being manufactured across two
joined script blocks, and the check can tell when it is gone.

---

## 5. THE ARIA QUESTION IS STILL OPEN AND WAS NOT ANSWERED

The anchor line prints `role`, `haspopup`, `expanded`, `controls`, all read
with `get_attribute` -- which the **page-text** guard treats as a source and is
right to: a nav control's aria-label is his own name on the Me control. The
sibling **url** rule does not flag them, which is why that line survived
`5655bf1`. Two guards, two questions.

Whether ARIA roles are a closed set **in the spec** remains open in the
verdict-function filing. **The repair does not need it settled.** The tuples
added are not a claim about ARIA; they are *the tokens these files will
print*. Anything else renders `UNKNOWN-<attr>`, which holds whether the spec
is closed or not and whether or not the tuple is complete. `absent` stays
distinct from `UNKNOWN`, so `str(None)` does not lose its meaning.

That the question would have been convenient to settle is exactly why it was
not.

---

## 6. THE NEEDLE: DECLARED, WITH THE DISTINCTION THAT ALLOWS IT

`ZZQXNEEDLE7` is on `INVENTED_NAMES`, declared by somebody other than its
author. The lead's ruling, applied and recorded in the table itself:

> An **enrolment** asserts a behavioural **contract** and needs its author.
> An `INVENTED_NAMES` entry asserts only that a string **is not a real
> person's name**, which is decidable **from the string**.

**Verified from the string before declaring it**, as the brief required:
eleven upper-case characters carrying the literal word NEEDLE, behind a
vowel-free `ZZQX` cluster, closed with a bare digit, with no
given-name/surname split -- unlike every person already on that table. **No
human being is named this.** Had it read as a real name the answer would have
been a refusal, because the remedy for a real name is not a declaration.

**The cost changed, which the original hold could not have weighed.** Two
weeks ago the red stood alone. Today the coupling hook made it refuse three
finished repairs by three separate authors.

---

## 7. THE THIRD RED -- NOT IN THE BRIEF, AND THE REASON THE FILE WAS STILL STUCK

At **14:31** the held file was refused again. **Neither of my two reds was in
the refusal.** A new one was:

    FAILED test_no_committed_identity.py::
           test_no_tracked_file_carries_a_real_identifier[_RECOVER_groups_admission.patch]
    4 unallowed email hits, 0 declared

The `unfired-bank` wave had measured and routed it at 14:34, correctly, as
foreign -- and left the advice *"whoever holds that patch should declare or
rename before applying."* It also said, honestly, that it could not name an
owner and was offering a lead rather than an attribution.

**I opened the file. Neither remedy applied, because there is no identifier.**
All four hits are the same token on four lines:

    +@pytest.mark.parametrize

25 characters, matching the guard's own redaction. **A Python decorator on a
diff-added line.**

### Why it matches, and why only in a patch

`EMAIL_SHAPE` allows `+` in a local part -- correctly, for `name+tag@`. In a
diff the `+` marking an added line is glued to the decorator, so it binds as
the local part, `pytest.mark` reads as a domain, `parametrize` as an
11-letter TLD.

**It cannot fire in ordinary Python**: there the character before `@` is a
newline, which is not in the local-part class. It needs a diff marker. That is
why it went unseen for weeks.

### It is structural, not a one-off

> Every wave saves `_RECOVER_*.patch` at the tree root, untracked. And
> `sweepable()` was deliberately widened on 2026-09-01 to sweep
> untracked-not-ignored files, so the guard sees what is ABOUT to be
> committed.
>
> **Both practices are right. They collide by construction the moment a saved
> patch adds a parametrised test** -- and four commits across three waves were
> refused by that collision today.

### The change, and why it cannot hide a real address

`_email_ok` now exempts a match whose **local part carries no letter and no
digit**. Nobody's mailbox has a local part made only of punctuation.
`name+tag@`, `a@`, `1@` all still carry an alphanumeric and are still checked.

Alternatives were worse: **declaring** would have written into
`DECLARED_PLANTS` that a transient untracked file "deliberately contains a
violation" -- false, and it would rot the moment the patch is deleted.
**Exempting `.patch` files** would blind the guard to real ids in diffs, which
is precisely what it should see.

### Shown in both directions, and shown failing

    planted, must be CAUGHT   a PLUS-TAGGED address at a real-looking domain
    benign, must be IGNORED   +@pytest.mark.parametrize("name", sorted(...))

The planted value is deliberately **not written out here.** The first draft of
this file spelled it in full and the identity guard flagged this document --
1 unallowed email hit, 0 declared -- before it was ever staged. That is this
repo's own recorded lesson landing on the file describing it: *prose
explaining a leak is a place the leak can live.* The literal lives in the
control list in `tests/test_no_committed_identity.py`, which is declared.

The planted row is load-bearing: if the exemption is ever widened from "no
alphanumerics" to "contains a plus", it goes red. And the predicate was
reverted in place and re-measured:

    with the narrowing      decorator IGNORED, both real addresses caught
    narrowing removed       decorator CAUGHT   <- the false positive returns
    the two real addresses  IDENTICAL either way

`DECLARED_PLANTS` email `2 -> 3` for that module -- the guard's own mechanism
making a new plant cost a visible declaration.

    before   1 failed, 526 passed   14:35:25
    after    529 passed             14:36:51

**THE PRESSURE IS NAMED RATHER THAN HIDDEN.** I narrowed an identity guard
while it was blocking a commit I had been sent to land. That is the exact
shape this campaign has twice recorded as the mechanism of its worst calls.
The defence is not that it looked fine: the token is quoted in full, the rule
is one checkable sentence about local parts, and the controls run both ways.
If any of those three is wrong, revert `4cc53f9` and the four hits return.

---

## 8. WHAT I DID NOT DO

* **No `--no-verify`.** The hook refused twice and both refusals were obeyed.
  The second one is the reason section 7 exists.
* **No `git add -A`.** Every commit used `git commit --only <paths>`, and each
  was verified after by SHA -- not by exit status, and not by `HEAD`, because
  a neighbour committed between my commit and my check at 14:27 and `HEAD`
  was already theirs.
* **Nothing of a neighbour's was touched.** `_RECOVER_groups_admission.patch`
  is another wave's only copy of in-flight work; it was read and never edited.
  `linkedin_server/readonly.py` and the two readonly tests were dirty with a
  neighbour's uncommitted work throughout and were left alone.
* **No browser, no writes fired.**

---

## 9. THE GATE

Measured on a **detached worktree at `889f488`**, not on the working tree.
The working tree carried a neighbour's uncommitted `readonly.py` changes
throughout, so a suite run there measures their work in progress, not the gate
at `HEAD`. A separate worktree is single-writer **by construction**, which is
the only way this number can be honest while somebody else is live.

    worktree   scratchpad/gate-889f488, clean, 0 dirty files
    collected  5648 tests
    ran        14:44:53 - 15:02:20, nothing committed across it

    11 failed, 5625 passed, 11 skipped, 1 xfailed in 1053.77s (17:33)

### The eleven, named. NONE OF THEM IS MINE.

    test_a_correction_is_findable_from_the_claim   every_marker_names_one_document
    test_a_correction_is_findable_from_the_claim   every_candidate_pair_is_declared
    test_a_probe_closes_its_own_tab                the_tab_leak_only_ever_shrinks
    test_ci_shard                                  the_timings_table_still_prices
    test_click_is_not_its_own_evidence             a_click_that_does_commit_reaches
    test_every_tool_is_on_the_surface              both_rules_reject_the_registry
    test_messaging_overview                        the_url_guard_still_refuses
    test_messaging_overview                        the_click_is_on_the_sanctioned
    test_server_surface                            the_surface_is_exactly_fortytwo
    test_server_surface                            no_docstring_claims_a_write
    test_server_surface                            the_exemption_does_not_cover

**All three guards this wave touched are green and absent from that list:**
`test_page_text_is_never_printed`,
`test_a_person_name_is_never_a_literal`, `test_no_committed_identity`.

### The delta, stated as narrowly as it can honestly be stated

The lead's single-writer baseline was **16 at ~13:33**, at an **earlier HEAD**.
This is **11 at 889f488**. **That five is NOT this wave's.** Several waves
committed across that interval -- the surface pin and the docstring guard were
being repaired by a neighbour while this suite ran -- and attributing a tree
delta to whoever measured it last is the error this file has already recorded
twice in other forms.

**What this wave can claim is the three names above, each measured before and
after.** The rest of the movement belongs to whoever did it.

### A METHOD FINDING THAT COST NOTHING HERE AND COULD COST A LOT

The gate run above reports `test_no_committed_identity` green, **and that was
worth less than it looks.** Its own skip message said so:

> "THE EXACT-VALUE SWEEP DID NOT RUN, so nothing in this session checked any
> tracked file for a real name, city, employer or campus. The wordlist
> `_audit/_sanitisation_key.json` is absent -- it is gitignored on purpose."

**A detached worktree gives single-writer isolation by dropping exactly the
files git does not track -- and one of those is the de-anonymisation key that
arms the strongest half of the identity guard.** The isolation and the
disarming are the same mechanism. Nothing warned about it except the test,
which said it plainly and would have been read as a routine skip.

That matters here specifically because **this wave modified that guard.** So
the key was copied into the worktree and the module re-run:

    tests/test_no_committed_identity.py   519 passed, 0 failed   15:03:40
                                          WITH the exact-value key present

**Anyone measuring a gate in a fresh worktree is measuring a weaker suite than
they think**, and the difference is invisible unless the skip lines are read.

---

## 10. THE INSTRUMENTS, DECLARED RATHER THAN LEFT IN A TEMP DIRECTORY

Four were built. **None is harvested into the repository** -- that is a
decision for whoever owns the register, not something to take unilaterally in
a tree with live neighbours -- so they are described here precisely enough to
rebuild, which is the alternative the standing rule allows.

**TWO ARE WORTH KEEPING. They turned a 34-line list into a 3-line diagnosis
and they are not specific to this wave:**

* **`why.py` -- name the exact tainted sub-expression at each sink.** Walks a
  flagged `print`'s arguments with the guard's own stopping conditions and
  reports every MINIMAL tainted node: `TAINTED NAME <id>` or
  `TEXT-CALL .<attr>()`. This is the thing the brief asked for in prose
  ("a neighbour found the engine flagged two names on a line where six looked
  suspicious"), as a command.

* **`chain.py` -- trace each taint to its root.** Re-runs `_tainted_names`'
  fixed point one round at a time and prints `r<round> L<line> <name> <= <the
  expression that bound it>`. **This is what found the name collisions.**
  Without it, `run_detector_control`'s `label` and `_page_control`'s `label`
  parameter look like page text, and the repair would have been to shape a
  value that never touched a page.

Both are ~40 lines, import the guard rather than reimplementing it, and would
work unchanged on the sibling url rule.

**TWO WERE SINGLE-USE AND ARE DISPOSABLE:** `equiv.py`, the 4000-document
differential for `partition_word` with its broken-variant control (result in
section 4); and `email_control.py`, which reverts `_email_ok` in place to show
the narrowing is load-bearing (result in section 7). Both results are
recorded; neither harness has a second customer.

**THE ONE THAT ALREADY EXISTED AND WAS NOT REWRITTEN:** the guard engines
themselves. Every measurement in this file comes from
`tests/test_page_text_is_never_printed.py` and
`tests/test_no_committed_identity.py` imported and called, never from a
reimplementation of their rules. Writing a second copy of a taint walk is how
two rules drift, and this repo keeps the note about that in the file it would
have drifted from.

---

## 11. ONE HAZARD FOR WHOEVER WRITES THE NEXT BRIEF

**THE SESSION SCRATCHPAD IS SHARED BETWEEN TEAMMATES, NOT PRIVATE.** Two of
this wave's commit-message files were overwritten by another wave's files of
the same name while they sat there -- `msg-a.txt` and `msg-b.txt` both came
back holding a neighbour's surface-pin and docstring-guard messages.

Nothing was lost here because both had already been committed, and that is
luck rather than design: a message file written and used ten minutes later
would have committed a neighbour's text under this wave's changes. **Same
class as the shared index, one directory over.** Use a wave-specific filename,
or read the file back immediately before the commit that consumes it.
