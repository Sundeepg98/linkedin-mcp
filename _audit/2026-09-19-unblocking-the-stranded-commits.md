# Unblocking the stranded commits

Wave `unblock`, 2026-09-19. Written as the work happened, not afterwards.
**Every number below carries the time it was taken.** The single defect this
wave exists to clear is an orphaned red in `scripts/_probe_add_section_menu.py`
that has held three finished repairs out of the tree.

---

## 0. THE STATE I INHERITED, VERIFIED AGAINST DISK AT 13:14

The brief was written from a sample at 13:13. I re-read disk before acting and
it agrees:

    HEAD                      ded0048
    M  scripts/_probe_creator_content_analytics.py    staged
    M  tests/test_no_committed_identity.py            staged
     M tests/test_navigation_is_never_derived.py      modified, not staged
    no .git/index.lock
    no pytest process, no git process, no hook sh.exe

**EVERY STAMP IN THIS DOCUMENT IS THE BOX'S CLOCK, NOT MINE.** My own sense of
elapsed time ran roughly seven minutes FAST during this wave: I had written
"13:31" into a draft of this file while `date` on the box read 13:24:10. Rather
than leave estimates standing, I re-ran every load-bearing measurement in a
single command with `date` printed either side of it, and the stamps below are
those. An agent's clock is not an instrument.

**I am the only writer.** Measured 13:15 by `Get-CimInstance Win32_Process`:
the only `linkedin` python alive is the MCP server itself (pid 23812, started
11:19), not a test run. That is what makes the suite reading below a snapshot
rather than an interval.

---

## 1. THE TAINT RED -- AND THE BRIEF IS WRONG ABOUT WHAT IT IS

**MEASURED 13:24:33 BY THE BOX**, by running the repo's own engine
(`tests/test_navigation_is_never_derived.output_violations`) over the file
rather than by reading the source:

    TAINTED NAMES in _probe_add_section_menu.py (6):
        ['admitted', 'here', 'landed', 'pressable', 'rel', 'target']

    OUTPUT VIOLATIONS:
      line 287: print(f"anchor {index}: rel={rel:20s} haspopup={str(haspopup):6s}
                expanded={str(expanded):6s} controls={('yes' if controls else 'no'):3s}
                role={str(role):8s} EVIDENCED-DISCLOSURE={pressable}")
      line 310: print(f"boundary: is_read_url={admitted}  path_depth={depth}
                forbidden_tokens_present={trips}")

    DECLARED: []

### THE ARIA QUESTION IS NOT ON THE CRITICAL PATH, AND NEVER WAS

The brief says line 287 fires on `rel`, `haspopup`, `expanded`, `controls`,
`role` and `pressable`, and rules -- correctly, and I am not disturbing the
ruling -- that whether ARIA roles are a closed set must NOT be settled here.

**The measurement says the guard flags exactly two of those six names: `rel`
and `pressable`.** `role`, `haspopup`, `expanded` and `controls` are NOT
tainted by this engine and never were. The reason is in the engine's own
roots:

    _TAINTED_ATTRS = frozenset({"url"})
    _TAINTED_CALLS = frozenset({"goto"})

`role` is bound from `await node.get_attribute("role")`. `get_attribute` is
not a taint root, so nothing downstream of it is tainted. The six names the
brief lists are the names *printed on that line*, not the names the guard
objects to.

> **The open ARIA question does not need sidestepping, because it was never
> what this red was about.** It stays open, untouched, and for a better reason
> than that settling it would have been convenient: it is not load-bearing for
> anything this wave does.

`rel` and `pressable` are tainted because `here = str(landed)` (line 255) is a
`goto` return, and `rel = href_relation(href, here)` reads it. The taint is
real and the engine is right to track it.

### THE REPAIR, AND WHY IT IS NOT A DECLARATION

`KNOWN_TAINTED_OUTPUT` is untouched. No entry added. No name added to
`_SANITISERS`. The repair uses the engine's own sanctioned shape, which is the
shape `content-tail` had already established this morning in the sibling probe
(`_RECOVER_taint_fix.patch`):

> "A COMPARISON is the engine's own sanctioned shape, so the branch that
> matters prints as a boolean." ... "NAMED BY ITS BRANCH, NOT BY ITS VALUE"

and the warning that governs why `href_relation` must NOT be admitted to
`_SANITISERS` even though it demonstrably returns a closed alphabet:

> "While this function wore the name `_relation` the engine trusted the call
> BY SPELLING, and because the call looked sanitised it never examined this
> print at all. **A GUARD SILENCED BY A NAME DOES NOT MERELY STOP CHECKING
> THAT FUNCTION. IT STOPS CHECKING EVERYTHING DOWNSTREAM OF IT.**"

Measured facts the repair rests on (13:24:33 by the box):

* `is_read_url` returns a literal `True`/`False` -- `linkedin_server/readonly.py`
  `is_read_url`. So `admitted is True` is `admitted`, and the printed text does
  not change by one byte.
* `is_disclosure_control` returns `goes_nowhere and says_it_opens`, both
  booleans. So `pressable is True` is `pressable`.
* `href_relation` returns one of **eight** string literals defined in that same
  file, and its docstring already says "The value is never returned ... nothing
  it returns contains any part of it."

---

## 2. THE DOCSTRING NUMBERS -- MEASURED, NOT TRUSTED

The brief says a wave wrote "forty-four" and that the lead counted 46 by AST at
13:03, and tells me to trust neither. **Measured 13:24:33 by the box, off the live registry**
(`mcp.list_tools()`, the same source the guard uses):

    total tools           44
    performable writes    12
    refusing (write-shaped, gated, unable)     0
    toolless sanctioned actions                1   (set_open_to_work)
    reads (derived: 44 - 12 - 0)              32

So **44 is correct** and the AST count of 46 was counting something else.
`len(SANCTIONED_WRITES)` is 13 and `len(writes.PERFORMABLE)` is 12; the
thirteenth is `set_open_to_work`, which has no registered tool.

What the three sentences in `linkedin_server/server.py` actually say, matched
with the guard's own three regexes (13:24:33 by the box):

    headline : "forty-four tools, twelve of which write"        CORRECT
    split    : "THIRTY read, TWELVE write, and ZERO are write-shaped"   STALE
    total    : "Thirty plus twelve plus zero is forty-two"              STALE

**This is the exact failure the guard's docstring predicts:** *"Arithmetic that
is internally consistent is exactly what a hand-maintained count looks like
just before it rots."* 30 + 12 + 0 = 42 adds up perfectly and disagrees with
the registry in two places. The wave that moved the headline 42 -> 44 moved
README fully and `server.py`'s first line, and did not touch the two sentences
a hundred lines down.

**Every place the count is stated, checked 13:22-13:24 by the box:**

| file | claim | state |
|---|---|---|
| `linkedin_server/server.py:1` | forty-four tools, twelve write | correct |
| `linkedin_server/server.py:104` | THIRTY read / TWELVE / ZERO | **stale -> THIRTY-TWO** |
| `linkedin_server/server.py:105` | Thirty plus twelve plus zero is forty-two | **stale -> Thirty-two ... forty-four** |
| `README.md:6` | Forty-four ship. Thirty-two read. Twelve write. None write-shaped | correct |
| `README.md:823` | "server.py  the forty-four tools" | correct |
| `linkedin_server/__init__.py:33` | twelve write tools, **five** sanctioned mutating calls | **stale -> seven** |

### THE SECOND RED: IT IS THE SAME CLASS, AND I TOOK IT

The brief told me to take `test_the_package_docstring_agrees_about_writes_and_mutations`
**only if** it is genuinely the same stale-number class, and to file a ruling
instead if it turns on whether a call counts as mutating.

**It does not turn on a classification. Measured 13:23-13:24:33 by the box:**

* the guard derives the number as `len(readonly.SANCTIONED_MUTATIONS)`, which
  is **7**;
* the table went 5 -> 7 in `75b7ba6` at **12:12 today**, whose own subject line
  is *"the guard I wrote at 09:00 missed two stale counts I wrote at 11:00"*;
* the two new entries are `('linkedin_server/press.py', 'disclose', 'click')`
  and `('linkedin_server/press.py', 'disclose', 'press')` -- **two real calls in
  a new module**, `press.py`, added by `5be109a` ("the disclosing press, bounded
  by four conjunctive conditions").

Two calls were ADDED to the code and the front-door docstring was not updated.
Nothing was reclassified; no line was argued about. That is a rotted count,
not a ruling, so it is repaired rather than filed.

---

## 3. TASK 5 -- THE PAGE-TEXT INVENTORY. MEASURED, NOT REPAIRED.

**The brief orders: establish one fact and stop. Do not fix. I did not fix
it, and nothing in this wave edits `tests/test_page_text_is_never_printed.py`
or its `KNOWN_TEXT_SINKS`.**

The question was: are the 35 sites across five files NEW sites added today, or
sites that were always there with an inventory nobody updated? Those have
opposite repairs.

**ANSWER, MEASURED 13:23 BY THE BOX -- THEY ARE NEW, AND MORE SPECIFICALLY THEY ARE NEW
FILES.** All five probe files were ADDED today; not one existed when the
inventory was pinned.

    git log --diff-filter=A --follow -- <path>

    _probe_small_measures_live.py          ADDED a402c35  2026-09-19 09:00
    _probe_small_measures_followup.py      ADDED ddbd65d  2026-09-19 09:17
    _probe_add_section_menu.py             ADDED edd24f8  2026-09-19 09:22
    _probe_off_platform_controls.py        ADDED fb0bdb6  2026-09-19 10:06
    _probe_creator_content_analytics.py    ADDED a6efc4b  2026-09-19 12:09

    tests/test_page_text_is_never_printed.py
      ONE commit in its whole history: 881a11f  2026-09-05 17:04

**The detector and its inventory have not been touched since 2026-09-05.** So
a third possibility that had to be excluded -- that the detector was widened
today and old files newly trip it -- is excluded by the same measurement: the
detector has not changed in fourteen days.

**The lead's rename hypothesis is not needed and does not hold.** The brief
notes "two of the five files are ones a rename touched today ... the other
three were not touched by any rename, which argues against it." Correct that
it argues against it, and the simpler fact settles it: all five files are
younger than the inventory, so no rename is required to explain anything.

**THE REPAIR THIS IMPLIES, STATED AND NOT PERFORMED:** these are new sites in
new files, so the direction is FIX, not DECLARE -- the test's own instruction
("emit a count, a relation or a marker") applies, and `KNOWN_TEXT_SINKS` must
not grow. Five files by five different authors; it is not this wave's to take,
and a single wave repairing thirty-five sites it did not write is how the
attribution discipline in this repo gets lost.

**ONE CAUTION FOR WHOEVER TAKES IT.** `_probe_add_section_menu.py` is both one
of the five AND the file this wave edits for the taint red. Its page-text count
before and after my edit is recorded in section 5 below, so the next wave
starts from a number rather than from an assumption.

---

*(sections 4-7 -- the commits, the full failure list and the attribution
count -- are appended as they are measured)*

---

## 4. THE FIRST SINGLE-WRITER GATE READING OF THE DAY

    ./venv/Scripts/python.exe -m pytest tests/ -q --tb=short -rf -p no:randomly

    START  13:15:49   HEAD ded0048 + the three stranded repairs in the tree
    END    13:33:33
    16 failed, 5616 passed, 4 skipped, 1 xfailed in 1062.18s (0:17:42)

**Nothing was committed and no file was edited between those two stamps.** I
held every edit until the run finished precisely so this would be a snapshot.
I was the only writer: measured at 13:15 before launching, re-confirmed by the
absence of any git process or `index.lock` throughout.

### THE GATE IS SIXTEEN RED, NOT TWENTY-SEVEN

> The lead's 27 and the other wave's 23 were both taken across ~24 minutes
> during which 14 commits landed. **They were intervals, and an interval over a
> moving tree can report a failure that was already fixed and a fix that had
> not yet landed.** 27 was not a pessimistic reading of 16; it was a different
> measurement. The pass count moved too -- 5549 then, 5616 now -- so the
> denominator was moving as well as the numerator.

### ALL SIXTEEN, NAMED. NOTHING IS UNSEEN ANY MORE.

    tests/test_a_correction_is_findable_from_the_claim.py
        test_every_marker_names_one_document_and_carries_a_reason
        test_every_candidate_pair_is_declared_or_triaged
    tests/test_a_person_name_is_never_a_literal.py          ** IDENTITY **
        test_every_person_constant_holds_a_declared_invented_name
    tests/test_a_probe_closes_its_own_tab.py
        test_the_tab_leak_only_ever_shrinks
    tests/test_ci_shard.py
        test_the_timings_table_still_prices_most_of_the_suite
    tests/test_click_is_not_its_own_evidence.py
        test_a_click_that_does_commit_reaches_the_body_and_the_send
    tests/test_every_tool_is_on_the_surface.py
        test_both_rules_reject_the_registry_that_was_actually_measured
    tests/test_messaging_overview.py
        test_the_url_guard_still_refuses_compose_even_though_it_was_not_consulted
        test_the_click_is_on_the_sanctioned_list_and_the_list_is_still_short
    tests/test_navigation_is_never_derived.py               ** MINE, task 1 **
        test_no_navigation_derived_value_reaches_an_output_sink[_probe_add_section_menu.py]
    tests/test_page_text_is_never_printed.py                ** measured, not fixed **
        test_no_file_prints_page_text_beyond_its_pinned_inventory
    tests/test_prose_that_makes_a_claim.py                  ** MINE, task 2 **
        test_the_server_docstring_numbers_are_derived
    tests/test_server_surface.py
        test_the_surface_is_exactly_the_fortytwo_tools
        test_no_docstring_claims_a_write
        test_the_docstring_exemption_does_not_cover_the_reads
    tests/test_the_other_two_count_claims_are_pinned_too.py ** MINE, task 2b **
        test_the_package_docstring_agrees_about_writes_and_mutations

### WHAT THE COMPARISON AGAINST THE LEAD'S FOURTEEN SHOWS

**NINE of these were among the thirteen nobody had ever seen.** They are the
first eight files above, minus the two the lead had already named.

**FOUR THINGS THE LEAD NAMED ARE NOW GREEN and should be struck from any
successor's list:**

    test_stale_process_is_announced           3 failures -> 0
    test_publish_post_names_its_audience      1 failure  -> 0
    test_no_committed_identity                1 failure  -> 0  (the stranded
                                                 REGIONS declaration fixes it,
                                                 and it is in the tree)
    test_the_other_two_count_claims...        3 failures -> 1

**ONE IS AN IDENTITY GUARD AND IS NOT MINE.**
`test_a_person_name_is_never_a_literal::test_every_person_constant_holds_a_declared_invented_name`
is in the same family as the guard that fired on `blast_radius.py` this
morning. A red on that family means UNDECLARED, never REAL -- but it is a
safety guard standing red at HEAD and it was in nobody's report, so it is
named here at the top of the successor's list rather than buried in a count.

---

## 5. THE COMMITS -- FOUR LANDED, ONE WAS TAKEN BY A NEIGHBOUR, ONE IS STILL HELD

Every one verified with `git log --oneline -1` against the message subject
immediately after committing, never from an exit status. The commit helper
compares HEAD before and after AND matches the landed subject against the
message file, which is what caught the case below where HEAD moved for
somebody else's reason.

| # | commit | file | author whose reasoning it carries |
|---|---|---|---|
| 1 | `5655bf1` 13:41:15 | `scripts/_probe_add_section_menu.py` | mine -- the orphaned red |
| 2 | `1211794` 13:41:24 | `linkedin_server/server.py` | mine -- the stale split and sum |
| 3 | `5d15c15` 13:41:37 | `linkedin_server/__init__.py` | mine -- the front-door mutations count |
| 4 | `8944d2e` 13:41:53 | `tests/test_no_committed_identity.py` | **small-measures**, `sm-msg-declare.txt` used verbatim, not rewritten |

Each commit holds **exactly one file**. Commits 1-3 are prerequisites, not
scope creep: the hook that refused commit 4 named exactly two failures, and
1 and 2 are those two.

### THE HOOK LET COMMIT 4 THROUGH, WHICH WAS THE WHOLE POINT

    pre-commit[boundary]: 1 test file(s) staged -> themselves + 18 coupled
    [master 8944d2e] guard(identity): declare REGIONS not a pre-image ...

No `--no-verify`, at any point, on any commit. The bypass was never used and
never offered upward.

### COMMIT 5 WAS SWEPT INTO A NEIGHBOUR'S COMMIT AT 13:45:45

`scripts/_probe_creator_content_analytics.py` -- **content-tail's** taint fix
-- is in the tree, but not under its author's message. It was swept into
`8c42866 audit(events): what ran, what did not, and the three reds that are
not mine`, a commit about an events surface that says nothing about a taint
fix. That commit holds three files by three different waves.

**This is precisely the hazard the brief names**, and the brief's own account
of it is that the lead nearly did the same thing and was stopped by a lock,
"which was luck". Nothing stopped this one.

The neighbour wave measured and recorded the mechanism itself, in `d9bfff7`,
and its diagnosis is better than mine so it is cited rather than restated: a
`git add` is unavoidable for an UNTRACKED file, `--only` protects the commit
but not the index, and the file sat in the shared index for 11 seconds
between the two. Nothing was lost; the blob is byte-identical. **What is
wrong is the attribution, and history is evidence while the push is frozen,
so it is recorded rather than rewritten.**

**WHAT IS AT RISK OF BEING LOST IS NOT THE CODE BUT THE REASONING.**
content-tail's commit message for that change exists at
`scratchpad/msg_wave7b.txt` and is now attached to nothing. Its load-bearing
paragraph, preserved here because a scratchpad file is not a record:

> `_landing_class` returns a closed alphabet of five string constants, so no
> input survives it and printing one leaks nothing. It is SAFE IN FACT and
> UNDECLARABLE IN FORM -- the engine can see "returns a constant" but has no
> way to say "closed alphabet". A permanent exemption entry for diagnostic
> output in a probe buys a green at the price of a standing claim nobody
> re-checks, and the cheaper repair removes the need for the claim.

**AND ONE THING WENT RIGHT BECAUSE OF A TIMING DECISION, NOT BECAUSE OF
JUDGEMENT.** `tests/test_no_committed_identity.py` was also sitting staged in
that same shared index. It landed at **13:41:53** as `8944d2e`; the sweep was
at **13:45:45**. Had I stopped to report the live neighbour before committing
-- which the brief's own escape clause would have permitted -- small-measures'
declaration would have been swept as well, and two waves would have lost
their attribution instead of one.

> **When the hazard is a shared index, "stop and report" is not the safe
> option. Landing the work IS the mitigation.** That is why I reported the
> disagreement and kept committing rather than the other way round.

### COMMIT 6 CANNOT LAND, AND THE REASON IS NEW INFORMATION

`tests/test_navigation_is_never_derived.py` -- the arity-discriminating
failure message -- **is still held, and still uncommitted.** The work is
intact and safe: 40 insertions in the working tree, matching
`_RECOVER_arity_message.patch` line for line.

The hook refused it at 13:47. **The brief's condition was "it lands when the
foreign reds clear", and the foreign reds are not the ones anyone thought.**
The lead inferred them from the refusal seen on
`tests/test_no_committed_identity.py`, which named the taint red and the
docstring red -- both of which this wave cleared. But the coupling is
COMPUTED PER STAGED FILE, and this file's coupled set is a different set of
eight. Run directly, 13:48:34:

    FAILED test_a_person_name_is_never_a_literal.py::
           test_every_person_constant_holds_a_declared_invented_name
    FAILED test_page_text_is_never_printed.py::
           test_no_file_prints_page_text_beyond_its_pinned_inventory
    2 failed, 1012 passed, 1 skipped in 35.36s

**ONE OF THE TWO THINGS BLOCKING IT IS THE ONE THING THIS BRIEF FORBIDS ME TO
TOUCH.** Task 5 says of the page-text inventory: *"Do not fix this. Report
it."* Task 3 says land all three stranded commits. Those two instructions are
in direct tension, and the tension is not resolvable from inside this wave:
the only routes through are to fix the page-text inventory (forbidden), or
`--no-verify` (banned, and rightly). **So the third commit stays held. That is
a finding, not a failure to finish.**

**THE OTHER BLOCKER IS ONE LINE AND IS FULLY ROUTED HERE**, so the next wave
does not re-derive it:

    tests/test_recommendation_tally.py:71   NEEDLE = "ZZQXNEEDLE7"
    owner, by `git log -1 -- <path>` and not by inference:
        fc10b99   2026-09-05 19:15   feat(recommendations): a name-free reader

The guard's own message prescribes the repair and says the edit IS the check:
*"If it is invented, add it to the table."* The constant is documented in
place as "the exact needle the brief specifies" and carries no person's name.
**It is also the same shape as task 5**: the guard (`9138cca`, 09-03) and its
amendment (`a5a988a`, 09-05 21:32) are both OLDER than nothing here -- the
constant landed 09-05 19:15, two hours before the amendment whose subject is
*"declare this wave's needle, and leave the neighbour's red standing"*. **The
neighbour's red it left standing is this one.** It has been red and known for
two weeks, by deliberate decision, and it is not this wave's to overturn.

---

## 6. WHAT I DELIBERATELY DID NOT DO

* **I did not settle whether ARIA roles are a closed set.** The measurement
  showed the question is not on the critical path at all, which is a stronger
  reason to leave it alone than the one I was given.
* **I did not fix the page-text inventory** -- 35 sites, five files, five
  authors. Measured and reported, per the order.
* **I did not add anything to `KNOWN_TAINTED_OUTPUT` or to `_SANITISERS`.**
  Both are byte-identical to what they were at `ded0048`.
* **I did not use `--no-verify`**, and did not offer it upward.
* **I did not rewrite history** to correct the misattributed commit. The push
  is frozen, a neighbour wave is actively committing, and a rebase under a
  live writer would turn a recorded attribution error into a lost one.
* **I did not run a second full suite and call it a gate reading.** A
  neighbour landed four commits between 13:41 and 13:47; any full run started
  now is an interval, and an interval reported as a gate is the exact failure
  this wave was sent to stop repeating.
* **I did not touch `test_server_surface.py`** (three reds, the same count
  class) or `test_recommendation_tally.py`. Both are routed above instead.
* **I did not open a browser**, launch chromium, or fire any write.

## 7. THE CLOSING NUMBERS, EACH WITH ITS STAMP

    13:15:49-13:33:33   FULL SUITE, single writer, snapshot
                        16 failed, 5616 passed, 4 skipped, 1 xfailed
                        all 16 named; 9 of them never seen by anyone before

    13:51:07            the twelve files that held those 16, re-run
                        13 failed, 665 passed, 1 xfailed
                        -> EXACTLY THREE CLEARED, all three by this wave:
                             test_no_navigation_derived_value_reaches_an_output_sink
                             test_the_server_docstring_numbers_are_derived
                             test_the_package_docstring_agrees_about_writes_and_mutations

    13:52:16            co-authored lines, all 414 unpushed commits:   0
                        claude-session / generated-with lines:         0

**I DO NOT CLAIM THE TREE IS 13 RED.** Thirteen is the count over the twelve
files that held run 1's failures. Since run 1 a neighbour has landed commits
and added `tests/test_the_events_boundary_is_root_only.py`, a test file that
did not exist when run 1 collected. The only full-tree number I will stand
behind is the 16 at 13:33:33, and it was true of that tree.

**AND A CORRECTION OF MY OWN, MADE BEFORE IT REACHED A REPORT.** My first
capture of the delta above was piped through `tail -12` and cut two failures
off the top, which would have let me claim five tests cleared instead of
three. It is the same truncation defect that left thirteen failures unseen
this morning. Re-taken in full rather than reported from the fragment.

---

## 8. AMENDMENT: THE PRIVATE-INDEX ROUTE HAS A SECOND EDGE, MEASURED AT 13:54

`d9bfff7` identifies the private index as the route for committing a NEW file
in a contended tree, and it is right: `GIT_INDEX_FILE` at a scratch path plus
`git read-tree HEAD` means the shared index is never touched and the
eleven-second sweep window never opens. This document was committed that way,
as `6382c56`, and the window did not open.

**BUT IT LEAVES THE SHARED INDEX STALE AGAINST THE NEW HEAD, AND THE STALENESS
HAS A DIRECTION THAT MATTERS.** Measured immediately after, with
`GIT_INDEX_FILE` unset:

    $ git status --porcelain
    D  _audit/2026-09-19-unblocking-the-stranded-commits.md

The shared index still held the pre-commit tree, which does not contain the
new file, while HEAD now does. Git reads that difference as a **STAGED
DELETION**. A neighbour running a plain `git commit` in that window would not
merely have missed the file -- **it would have committed its removal**, under
their message, which is the same sweep hazard with the sign flipped and a
worse outcome: the sweep preserved the bytes and lost the attribution, this
would lose the bytes.

**THE REPAIR IS ONE SURGICAL COMMAND, AND THE SURGICAL PART IS LOAD-BEARING:**

    git reset -q -- <the one path>

A bare `git reset` would have done it too and would have been wrong: it resets
every path, so in a shared tree it silently unstages whatever a neighbour has
staged at that moment. **The remedy for a multi-writer hazard must not itself
be a multi-writer hazard.** Pathspec-scoped, the working tree is untouched and
no other writer's staging is disturbed. Verified after: `git diff --cached`
empty, the file present on disk and resolvable at `HEAD`.

**THE RULE, SO THE NEXT WAVE DOES NOT PAY FOR IT:** a private-index commit is
two steps, not one. Commit with `GIT_INDEX_FILE` set, then `git reset -- <the
same path>` with it unset. Between those two steps the shared index carries a
staged deletion of the file you have just committed, so keep the gap as short
as one command.

**AND IT IS ONLY NEEDED ONCE PER FILE.** `git add` is unavoidable for an
untracked path, which is what opens the window at all. Once the file is
tracked, `git commit --only -- <path>` needs no add and has no window -- which
is how this amendment itself was committed.
