# The proximity field -- census row `J 40`, read per-job network proximity

**WAVE:** `proximity-field`. **STATUS: IN PROGRESS** -- written incrementally.
**BRANCH:** `worktree-agent-af3d04d2d06ceafc5`, forked at `2571b1f`.

---

## 0. THE MEASUREMENT THAT SETTLED THE DESIGN (taken before any code was written)

The brief left the record-vs-DOM fork open and said the safety rule differs by
answer. It is **RECORD**, and the reason is the whole safety story.

`dom.harvest_linked_cards` run over the committed `jobs_search_hydrated.html`
in a local headless Chromium, card `/jobs/view/4600000014/`:

    RAW record["text"] lines:
        'Software Engineer'
        'Software Engineer with verification'
        'Grandview Networks'
        'Fairhaven, Riverton, Westland (On-site)'
        '1 company alum works here'              <- name-free  (aria-hidden copy)
        '1 <ORG> company alum works here'        <- CARRIES THE EMPLOYER NAME
        'Promoted'

    record["hidden"]:
        'Software Engineer with verification'
        '1 <ORG> company alum works here'        <- the leak, ALREADY ISOLATED

    AFTER shape.strip_screen_reader_copies(text, hidden):
        'Software Engineer'
        'Grandview Networks'
        'Fairhaven, Riverton, Westland (On-site)'
        '1 company alum works here'              <- ONLY the name-free copy survives
        'Promoted'

**The name-carrying copy is removed by a subtraction that already ships, is
already tested, and does not know the phrase.** `strip_screen_reader_copies`
subtracts BY COUNT: each element the page itself marked screen-reader-only
removes one occurrence of its own text. LinkedIn marks the name-carrying copy
`class="visually-hidden"`, which is in `dom.CARD_HIDDEN_SELECTOR`, so the page
hands us the leak already labelled and the existing code deletes it.

So the reader does not have to *choose* the safe copy by a regex of mine. It
reads the line list `parse_job_card` has already computed, at the point where
the only surviving copy is the name-free one. **The brief's instruction "take
the `aria-hidden` copy" is satisfied structurally rather than textually.**

The same probe over the UN-HYDRATED twin `jobs_search.html`: 7 records
harvested, **zero** carrying `alum` in `text` or `hidden`. The negative control
therefore holds at the RECORD level, not merely at the byte level -- a stronger
control than the committed byte-level one.

---

## 1. WHAT DISK SAYS THAT THE BRIEF DID NOT

Recorded per the brief's standing order to trust disk.

**1.1 -- A proximity test file already exists.** `tests/test_proximity_is_on_a_read_surface.py`
(179 lines at `2571b1f`, where this wave forked; 215 after the inversion in
4.2. Committed by the `contingent-writeoffs` wave, receipts in
`_audit/2026-09-20-the-contingent-writeoffs.md`). It pins the evidence that
moved `J 40`'s reason cell: the two hydrated captures carry the field, their
un-hydrated twins and `profile_topcard_hydrated.html` read zero.

**Nothing in this wave withdraws anything in that document.** It prescribed a
parser at boundary cost 0 and this is that parser; the two stand together.

The brief's line "No extractor exists anywhere in `linkedin_server/`" is
**correct as written** -- that file is under `tests/`, not `linkedin_server/`,
and it reads bytes rather than extracting a value into a tool result.

**1.2 -- That file carries a tripwire that my change is designed to trip.**
`test_the_field_is_read_by_nothing_in_the_package` asserts that no line of CODE
in `linkedin_server/*.py` matches `alum` (prose is separated from code with
`tokenize` + `ast`, so the two known docstring/comment mentions are exempt).
Its own docstring rules the succession:

> "The day somebody wires a reader this test goes red and is deleted along with
> the census row: that is the intended end of this file, not a regression."

So landing `J 40` necessarily turns that file red. Handling it is part of this
wave, not a side effect to be left for the merge. See *THE PREDECESSOR
TRIPWIRE: INVERTED, NOT DELETED* in section 4.

**1.3 -- The repo already ships the exact design pattern I was asked to invent.**
`linkedin_server/company_root.py` reads "N connections work here" off a company
Page with: a closed `COUNT_KINDS` alphabet, a `COUNT_PHRASES` table whose
phrases are shipped INTO the page and answered with a POSITION, a closed
`NUMERAL_SHAPES` alphabet, and a closed `READING_STATES` verdict alphabet. It
also states two laws this wave needs:

* **"NO PHRASE MAY CONTAIN ANOTHER"** -- two phrases where one contains the
  other match the same line and produce two readings of one number, "which
  would read as corroboration and is one observation." That is the brief's
  "counting renderings, not facts" hazard, already solved as a design rule.
* **`phrase_not_drawn` IS NOT A COUNT OF ZERO** and is never reported as one.

`company_root.py:153` already holds the literal `"connection works here"`. It
is a **different surface** (company Page, not a job card) and its phrases are
marked **UNMEASURED** -- "no capture in this repository holds a company Page."
Mine are measured against two committed captures. I follow its pattern and do
not import its tables; a job card and a company Page are different pages with
different vocabularies, and fusing them would make one unmeasured table govern
a measured surface.

**1.4 -- The detail surface is worse than the brief said, in the safe direction.**
Confirmed: `job_detail_following_hydrated.html` holds one `<p>` reading
`Company alumni from <ORG>` and **no name-free copy, no count, and no
`visually-hidden` element on the whole page** (`visually-hidden` count = 0).
There is nothing for `strip_screen_reader_copies` to subtract, so on detail the
protective mechanism of section 0 is ABSENT. Detail is boolean-at-best, and the
reason is now measured rather than assumed.

**1.5 -- THE BRIEF'S PRESCRIBED INSTRUMENT DOES NOT FIT THIS SOURCE.** The
brief says: *"Use `linkedin_server/coerce.py::as_int` (line 75), which never
raises and never quotes its input."* `as_int` is the right instrument and the
wrong site. Measured 2026-09-21:

    coerce.as_int("1")                          -> None
    coerce.as_int("12")                         -> None
    coerce.as_int("1 company alum works here")  -> None
    coerce.as_int(1)                            -> 1

Its body is a TYPE GATE, not a parser: `isinstance(value, bool) -> None`,
`isinstance(value, int) -> value`, `return None`. It exists for a value that
already crossed a JS boundary as a JSON number -- which is what
`company_root.read_company_root` feeds it, since `dom.COUNT_LINES_JS` does the
digit classification in JavaScript. **My source is a Python line of page text,
and there is no string-to-integer reader anywhere in `coerce`** (`as_count`,
`counts_only` and `scalars_only` all delegate to `as_int`, so all three answer
0 or None for every string, and `as_count` additionally logs a warning).

Obeying the brief literally would have produced a reader that returns `None`
for every count on every page -- green against a fixture-free unit test, dead
on the surface. So `shape._digits_before` is that missing instrument, written
to `coerce`'s contract rather than around it: **it never calls `int()`, never
calls `float()`, never raises, and never quotes its input**, accumulating the
value from character positions with `ord()`. A test asserts the source, not
just the behaviour -- see `test_no_line_of_this_reader_calls_int_or_float_on_page_text`.

Its natural long-term home is `coerce.py`, which this wave does not own. Left
in `shape.py` deliberately, noted here for whoever consolidates.

**1.6 -- THE BRIEF'S LEAK FIGURE IS OFF BY TWO, AND I PROPAGATED IT BEFORE
CHECKING.** The brief states *"This repo measured 16 of 115 readers leaking
exactly this way."* The repository's own measurement, in `coerce.py:19`, is:

> Measured 2026-09-20 by driving the real readers with a page that answers in
> strings: **14 of 115 readers carried a planted name out through a ValueError.**

A grep of the whole tree finds `16 of 115` in exactly one place -- a docstring
I had just written from the brief -- and `14 of 115` in exactly one place,
`coerce.py`. **Corrected to 14 before commit.** Recorded rather than quietly
fixed because it is the failure mode the number is about: a figure travelling
one hop from its measurement and arriving as a fact nobody re-took. Caught only
because I opened `coerce.py` to check something else.

**AND I DID IT AGAIN IN THIS DOCUMENT, WHICH IS THE point.** Commit `72bb388`'s
message and the first version of section 2.2 both say `shape.py` is **348**
lines added. That was true when I measured it and stopped being true when the
hardening in 4.5 landed -- 371 now, `git show --numstat` on the commit. The
load-bearing half of that claim, **zero removed**, is unchanged and still
verified. The commit message is left as written rather than amended: it is an
unpushed local commit, but rewriting a message to hide a number that moved is
the opposite of what this subsection is about. **A figure is true at a
timestamp, and mine were both quoted past theirs.**

---

## 2. WHAT WAS BUILT, AND WHAT IT RETURNS

All of it in `linkedin_server/shape.py`. **No new MCP tool, no new module, no
edit to any file another wave owns.** The field rides along in the output of
two readers that already exist.

### 2.1 The shape of a reading

    {"state": <position in PROXIMITY_STATES>,
     "relation": <position in PROXIMITY_RELATIONS> or None,
     "count": <int> or None}

**Three integers or None, on every path, for every input.** A relation is a
POSITION in a tuple this package authored; a count is accumulated digit by
digit. There is no code path that returns a substring of a page, which is the
second line of defence behind the subtraction in section 0: if that subtraction
silently stopped working, the cost is a wrong COUNT and never a name.

New public names in `shape.py`:

| name | what it is |
|---|---|
| `PROXIMITY_RELATIONS` | closed alphabet: `company_alum`, `school_alum`, `connection` |
| `PROXIMITY_STATES` | closed verdicts: `not_drawn`, `relation_only`, `numeral_refused`, `disagreement`, `count_read` |
| `PROXIMITY_PHRASES` | `(relation, phrase, a count precedes it)`, 10 rows, 2 MEASURED |
| `relation_for` / `state_for` | position -> literal; out of range REFUSES, never clamps |
| `proximity_alphabet()` | every token a reading can resolve to |
| `read_proximity(lines)` | the reader. Pure, no page, no browser |
| `_digits_before(text, at)` | the count reader described in 1.5 |

`not_drawn` is first in the verdict alphabet for the reason
`company_root.READING_STATES` puts `reader_blind` first: it is the verdict that
asserts nothing about the account's graph. **`not_drawn` IS NOT A COUNT OF
ZERO** and is never reported as one -- a card that draws no insight, a card
whose wording moved, and an account with no connection to that employer are
three different worlds, and this reader separates the first two from a drawn
card but not the third from either.

### 2.2 Where it rides along

* **`parse_job_card`** -- computes `read_proximity(lines)` immediately after
  `lines` is built, and passes it to both `_job_card_out` call sites (the
  ordinary path and the welded one-line-card path). `_job_card_out` emits
  `proximity` **only when the card drew something**, exactly like `status`,
  `when` and `job_id` above it. A row carrying `not_drawn` would be asserting
  something about the graph; an absent key asserts nothing.
* **`parse_job_detail`** -- `read_proximity(header)`, reported as the reading or
  `None`, in the same shape as `salary` and `status` beside it.

**Taken BEFORE the status/time-ago loop, not after.** That loop DISCARDS lines,
and a reader placed downstream of a discard silently inherits its judgement --
a proximity line that ever looked status-shaped would vanish with no trace.

**`linkedin_server/shape.py` IS 371 LINES ADDED AND ZERO REMOVED** (`git show
--numstat`: `371  0  linkedin_server/shape.py`). Not a
stylistic note -- it is the tightest statement available about blast radius.
Not one existing line of the parser was changed, deleted or re-indented, so the
only way this wave can have altered an existing reading is through the new
optional key, and a key nothing reads yet cannot alter one at all. The
anchoring the brief warned me about is untouched by construction, and section
4's check 9a exists because "untouched by construction" is an argument and a
test is a measurement.

### 2.3 What it reads on the real captures

| capture | result |
|---|---|
| `jobs_search_hydrated.html` | 1 of 7 rows: `count_read` / `company_alum` / **1**. The other 6 omit the key |
| `jobs_search.html` (un-hydrated twin) | **0 of 7 rows** carry the field |
| `job_detail_following_hydrated.html` | `relation_only` / `company_alum` / count `None` |
| `job_detail_following.html` (un-hydrated twin) | `None` |

Both hydrated results reproduce in BOTH layouts -- with LinkedIn's
`.visually-hidden` rule and with it stripped. That matters because without the
rule the hidden copy is inline and `innerText` welds it onto its neighbour
rather than giving it a line, so `strip_screen_reader_copies` has to remove it
as a SUBSTRING instead of as a line. The answer does not depend on whether the
stylesheet had loaded.

---

## 3. THE SOURCE OF THE FIELD, AND THE SAFETY CONSEQUENCE

**RECORD, on search. Not DOM.** The full measurement is section 0. The
consequences, stated as the rules they became:

1. **No new DOM read was added, and none was needed.** `record["text"]` and
   `record["hidden"]` already arrive from `dom.harvest_linked_cards`, which
   uses `innerText` -- not `textContent`. The distinction is the whole thing:
   `textContent` is unconditional, ignores `aria-hidden`, clip-styling and
   `display:none` alike, and would MERGE the two copies back together. Nothing
   in this wave calls it.
2. **The reader is handed `lines`, never `record["text"]`, never
   `record["hidden"]`.** `lines` is post-subtraction. This is written into the
   code as a comment at the call site and into `read_proximity`'s docstring as
   an input contract, because it is the kind of thing a later edit breaks by
   reaching for the "more complete" source.
3. **The search page's name-carrying copy is `class="visually-hidden"`**, which
   is in `dom.CARD_HIDDEN_SELECTOR`. LinkedIn labels the leak for us and the
   existing subtraction deletes it, by COUNT, without knowing the phrase.
4. **Detail has no such protection and needs none**, because it offers no count
   to protect -- see 1.4. It reports the relation and stops.

---

## 4. EVERY CHECK ADDED, AND HOW IT WAS SHOWN FAILING

`tests/test_proximity_reader.py` -- **NEW FILE: 27 test functions, 73 cases.**
`tests/test_proximity_is_on_a_read_surface.py` -- 3 functions, 6 cases, one
function INVERTED. **79 cases, all green.**

**EVERY ONE OF THE 30 TEST FUNCTIONS HAS BEEN DRIVEN RED.** 37 mutations across
seven passes. Each was applied to the file, the targeted check was run, and the
file was restored from an in-memory copy in a `finally` block. The captures are
byte-identical afterwards (`git diff --stat tests/fixtures/` is empty) and no
temporary module survives.

**FOUR MUTATIONS SURVIVED on first attempt.** Two were bugs in the mutation
(4.1a), two were real holes in my own checks (4.4). Recording the split matters:
a surviving mutation is either a weak check or a fact about the code, and which
one it is cannot be guessed from the fact that it survived.

| # | what was broken | check that went RED |
|---|---|---|
| 1 | added a phrase containing another (`"alum works here"`) | `test_no_shipped_phrase_contains_another` |
| 2 | reader grew a fourth, string-valued field | `test_a_reading_carries_no_text_from_the_line_it_was_read_from` |
| 3 | raw `record["text"]` emitted on the row | `test_no_parsed_row_carries_the_employer_named_only_in_the_hidden_copy` |
| 4 | de-duplication set changed to a list (matches, not facts) | `test_the_same_fact_rendered_twice_is_one_fact` |
| 5 | decimal guard disabled | `test_a_numeral_this_reader_will_not_commit_to_is_refused_not_guessed` |
| 6 | `int(digits)` put back into the count reader | `test_no_line_of_this_reader_calls_int_or_float_on_page_text` |
| 7 | the insight DELETED from a copy of the capture | `test_the_hydrated_search_card_reads_the_fact_the_page_states` |
| 8 | the negative control pointed at its hydrated twin | `test_no_row_of_the_un_hydrated_twin_carries_the_field` |
| 9a | proximity made to displace the `company` field | `test_the_new_field_moved_no_existing_field_on_any_row` |
| 10 | detail reader widened from `header` to the whole page | `test_the_detail_reader_does_not_read_the_job_description` |
| 11 | the field named in CODE in a second module | `test_the_field_is_read_in_exactly_one_module` (leg 3) |
| 12 | the measured phrase corrupted so it cannot match | `test_the_hydrated_search_card_reads_the_fact_the_page_states` |
| 13a | needle changed to a token in no file | same check, leg 1 (`in_prose`) |
| 13b | needle changed to a PROSE-ONLY token (`2026-08-22`) | same check, leg 2 (`in_code`) |

And the second pass, one mutation per remaining test function:

| # | what was broken | check that went RED |
|---|---|---|
| A | a phrase given an undeclared relation | `test_the_phrase_table_is_not_empty_and_every_relation_is_declared` |
| B | a phrase given a capital and a double space | `test_every_phrase_is_already_in_the_form_the_reader_compares_against` |
| C | the state alphabet reordered | `test_the_named_state_positions_still_name_those_states` |
| D | `relation_for` made to CLAMP to position 0 | `test_a_position_resolver_refuses_out_of_range_and_never_clamps` |
| E | the alphabet helper stopped publishing states | `test_the_alphabet_helper_covers_everything_a_reading_resolves_to` |
| F | the count reader made to always answer "no numeral" | `test_one_line_reads_as_the_fact_it_states` |
| I | a clean count allowed to beat a refused one | `test_a_refused_numeral_suppresses_a_clean_one_elsewhere_on_the_card` |
| J | the `str()` guard removed, so `None` raises | `test_the_reader_never_raises_on_hostile_input` |
| K | `lines or ()` reduced to `lines` | `test_the_reader_tolerates_a_non_list_and_an_empty_one` |
| L | `None` counts folded into the fact set | `test_the_leaked_copy_and_the_safe_copy_read_as_one_fact_not_two` |
| M | the walk-back widened from digits to a whole word | `test_the_word_before_the_phrase_is_never_read_as_a_count` |
| N | every row tagged, drawn or not | `test_exactly_one_row_of_the_hydrated_search_carries_the_field` |
| O | the detail phrase corrupted | `test_the_hydrated_detail_page_reads_a_relation_and_no_count` |
| P | the detail control pointed at its hydrated twin | `test_the_un_hydrated_detail_twin_reads_nothing` |
| G2 | the "no digit run" branch made to report a refusal | `test_a_relation_with_no_numeral_is_not_reported_as_a_refusal` |
| H2 | the RELATION-disagreement branch disabled | `test_two_different_relations_on_one_card_are_refused_rather_than_picked` |
| H3 | the COUNT-disagreement branch disabled | `test_two_different_counts_for_one_relation_are_refused_rather_than_picked` |

Verbatim, from check 2: `AssertionError: field 'matched' came back as str. A
reading is integers and None; any other type is a channel a page can write to.`
From check 10: `a sentence in the job description was read as a proximity fact:
{'state': 4, 'relation': 0, 'count': 4}`.

### 4.1a TWO MUTATIONS THAT SURVIVED BECAUSE THE MUTATION WAS WRONG

Not findings, and named so they are not mistaken for any. One injected a string
into a field that a later line overwrites, so it never reached the return; one
used an anchor whose indentation did not match. Both re-run correctly -- checks
2 and 9 -- and both went red.

### 4.1 TWO MUTATIONS STAYED GREEN, AND BOTH ARE RESULTS RATHER THAN HOLES

Recorded because a mutation that does not go red is either a weak check or a
fact, and saying which is the whole value of running them.

**(a) Removing `strip_screen_reader_copies` from `parse_job_card` did NOT move
any field.** The anchoring check stayed green. That is not the check failing to
discriminate -- check 9a shows it goes red the moment a field actually moves --
it is `parse_job_card`'s own docstring claim holding up under a direct
experiment: `title`, `company` and `location` come from ANCHORS (`logo_name`,
`meta_line`), so a card that HAS anchors does not care whether the subtraction
ran. The subtraction matters for the anchor-less card, which is a different row.

**(b) Dropping BOTH anchors as well still did not move any field** on these
rows. That reproduces an existing shipped finding rather than contradicting
one: `tests/test_job_search_fixture.py::test_the_hidden_subtraction_alone_fixes_the_field_shift`
already records that *"with every anchor gone, the page's own hidden list still
saves it."* Two independent mechanisms cover this row, which is why the
proximity line -- a decoration of exactly the class that shifted 5 of 14 live
rows -- does not shift it either.

**The safety argument does not rest on either of them.** It rests on the type
of the return value (check 2), which holds even if both mechanisms fail at once.

### 4.2 THE PREDECESSOR TRIPWIRE: INVERTED, NOT DELETED

`test_the_field_is_read_by_nothing_in_the_package` went red on landing, naming
ten lines of `shape.py` -- exactly as its author designed, and its docstring
prescribed deleting it along with the census row.

**It was inverted instead, and renamed `test_the_field_is_read_in_exactly_one_module`.**
Deleting it is a worse trade than it looks: the old check had a real job --
knowing WHERE in the package this field is named -- and that job did not end
when the reader landed, it changed sign. A reader concentrated in one module
can be audited for the thing that matters (no employer name leaves it); the
same matching scattered across four modules cannot, and would arrive silently.
It now asserts that code names the field, and only inside `shape.py`. All three
of its legs were shown able to fire (checks 11, 13a, 13b).

**This is a deviation from the brief's file-ownership line**, which granted me
`shape.py`, NEW files under `tests/`, the census and this report. That file is
an existing one. Taken because it is the direct predecessor of this row, no
live wave owns it (the owned list names `tests/test_company_root.py` only), and
leaving it red would have handed the merge a broken suite. Flagging it rather
than burying it.

### 4.3 THE SECOND OWNERSHIP DEVIATION, AND IT IS SMALLER

One entry added to the `NOT_A_CORRECTION` data dict in
`tests/test_a_correction_is_findable_from_the_claim.py`, keyed
`("jobs.md", "2026-09-21-the-proximity-field.md")`, with the reason written
after reading the line that produced the pair.

**Why it was not avoidable by rewording.** The correction vocabulary is
`stale`, and it is not in anything this wave wrote: it is two lines below my
census row, inside ROW 42 -- job collections -- reading *"all four are the
staleness diagnostic"*, about the string content of a JSON payload. A markdown
table has no blank lines, so another capability's prose sits inside my row's
window. This is the TABLE-ROW PROXIMITY shape that dict's own docstring names
first, and its own failure message prescribes the entry: *"add it to
NOT_A_CORRECTION with the reason, AFTER READING THE LINE."*

**The alternative was worse.** I could have dropped the audit-document citation
from the census row, which would have silenced the pair -- and made the row
stop naming its own evidence in order to quiet a guard. Triaging a false
positive the guard asked to have triaged is the honest move; editing the row to
dodge the scan is not.

No check was weakened: the entry is one key in a data dict, every other pair
still has to be declared or triaged, and the entry names what would make it
wrong.

### 4.4 TWO OF MY OWN CHECKS COULD NOT FAIL, AND ONLY MUTATION FOUND IT

The most useful thing in this section. Both checks were GREEN, looked
reasonable, and were certifying nothing.

**(1) `test_a_relation_with_no_numeral_is_not_reported_as_a_refusal`.** I set
the "no digit run" branch of `_digits_before` to report a refusal on every
input. **The test stayed green.** Reading it back: both of its cases returned
BEFORE that branch -- one put the phrase at position 0, where the function
exits on `gap == 0`, and the other used a `counted=False` phrase, which never
calls the function at all. **The branch the check is named after was never
executed by it.** Fixed by adding the case that reaches it: a phrase preceded
by a WORD rather than a numeral -- *"several company alums work here"* -- which
is also the realistic shape. Re-proved red.

**(2) `test_two_different_facts_on_one_card_are_refused_rather_than_picked`.**
I disabled the relation-disagreement branch outright. **The test stayed green**,
because its case used counts 1 and 3: the reading was refused by the COUNT
branch and the relation branch was never reached. The check could not tell the
two refusals apart, so it could not fail for the reason in its name. Split into
two checks, and the relation one now uses **the same count on both lines** so
only the relation branch can produce the refusal. Both re-proved red.

**The shape is the same twice, and it is this repository's own recurring one:**
a check that passes through a path other than the one it claims. Neither would
have been found by reading the test, by coverage (both lines were executed, by
the OTHER case), or by the suite being green. Only breaking the code on purpose
and watching what did not complain.

### 4.5 A GAP FOUND IN SELF-REVIEW, AND THE BUG THE FIX INTRODUCED

Recorded in full because the second half is the more useful half.

**THE GAP.** Re-reading `_digits_before` before freezing, the decoration
refusal was `before == "." or before.isalpha()`. A decimal was refused and a
letter was refused -- and a DATE, a FRACTION and a CLOCK TIME were not. On
`2026-09-21 company alums work here` the walk-back stops at `21` and the `-`
before it was never examined, so the reader would have answered **21**: a
plausible wrong number in a real field, which nothing downstream can tell from
a right one.

**THIS IS THE SAME ASYMMETRY THIS REPOSITORY HAS ALREADY PAID FOR ONCE.**
`company_root.NUMERAL_SHAPES` carries `percent_refused` with a note that it was
APPENDED after a cold review found `%` falling through a suffix check that
already caught `k`/`m`/`b` -- one separator remembered and the rest not. I had
written the identical shape. Fixed by naming the set as data,
`_PROXIMITY_DECORATIONS = ".-/:%"`, and four cases added.

**THE GAP WAS REAL, NOT HYPOTHETICAL:** restoring the narrow version turns 3 of
the refusal cases red (proof S), removing the guard turns 4 red (proof T).

**AND THE FIX SHIPPED A BUG, WHICH THE SUITE CAUGHT IN ONE RUN.** The new
expression was `if before in _PROXIMITY_DECORATIONS or before.isalpha()`.
`before` is the EMPTY STRING when the digit run starts the line -- and
**`"" in ".-/:%"` is `True` in Python, because every string contains the empty
string.** So the reader refused every count at the start of a line, which is
exactly where the measured line puts it: `1 company alum works here`. **13
checks went red in one run**, including both browser checks and the positive
fixture assertion. Fixed by testing the emptiness first; the guard is now
`if before and (...)`, with the reason written at the site.

**Proofs U and V drop that one guard: 8 pure checks and both browser checks go
red.** So the `before and` is load-bearing and is pinned.

**Why this belongs in the report rather than in a tidy final diff.** A hardening
edit made at the end, after every check was green, is the most dangerous kind --
it arrives with the confidence of a finished wave and none of its scrutiny. The
only reason it cost nothing here is that the checks built earlier were sharp
enough to convict it immediately, and the `1 company alum works here` case was
pinned by name rather than by "some row has proximity".

---

## 5. THE CENSUS

### 5.1 `J 40` -- **GAP `SKILL` -> CU (COVERED-UNFIRED)**

`_audit/_census/jobs.md` row 40, plus a THIRD DELTA in the count bloc:

    GAP               99  ->  98    row 40, BUILT
    COVERED-UNFIRED    8  ->   9    same row

Running totals on this slice after all three deltas: **CP 20, CU 9, XR 23, GAP 98.**
The count block itself is UNCHANGED, per this file's standing convention that a
count which silently rewrites itself cannot be cited.

**THE EXACT EVIDENCE:**

| claim | how it is known |
|---|---|
| the reader exists and runs | `shape.read_proximity`, called from `parse_job_card` and `parse_job_detail` |
| it reads the search card | `jobs_search_hydrated.html`, 1 of 7 rows, `count_read`/`company_alum`/1, in BOTH layouts |
| it reads the detail page | `job_detail_following_hydrated.html`, `relation_only`/`company_alum`/None |
| it is not matching prose | the un-hydrated twins: 0 of 7 rows, and `None`. Same reader, same pages |
| it returns no name | every field is `int` or `None`, asserted structurally; shown failing |
| it displaced nothing | title/company/location on 3 named rows unchanged; shown failing |
| 65 + 6 checks, all shown able to fail | section 4 |

**CU AND NOT CP.** The reader has never run against LinkedIn. By this slice's own
standard -- which cost rows 103 and 104 their CP two days ago -- a fixture is not
a fire. It moves to COVERED-PROVEN on one live `linkedin_search_jobs` call whose
result carries a `proximity` key. **That is the single outstanding item on this
row, and it needs a session, which this wave did not have.**

### 5.2 `J 57` -- **DID NOT MOVE. Still GAP, but no longer blocked.**

Checked, not forced. Its cell said *"BLOCKED behind row 40, which is itself
buildable."* Row 40 is now built, so that blocker is lifted -- and the row is
still a GAP, because **nothing was built for it**: `J 57` is a JOIN (connections
reachable for a TRACKED job), and a join is not a by-product of either half.

What this wave added to it is a measured route where there was an assumption. A
fixture-wide census of the proximity needle over **all 20 committed captures**:

    jobs_search_hydrated.html            2 byte hits  (= ONE fact, rendered twice)
    job_detail_following_hydrated.html   1 byte hit
    the other 18 captures                0
    -- including jobs_tracker_row.html and jobs_tracker_empty.html

**The tracker card does not render the insight.** So `J 57` cannot be served by
reading a tracker row, which is what "both halves already exist" implied. The
buildable route is: tracker -> job ids (`linkedin_my_applications` /
`linkedin_draft_applications`, rows 47-49, all CP) -> `linkedin_job_detail` per
job, one page load each -- and what proximity yields there is `relation_only`, a
**BOOLEAN with no count**, because the detail page states no number.

That is a materially worse deliverable than row 40's, it costs one page load per
tracked job, and it is a design decision with a live cost. Left for a ruling
rather than taken here.

---

## 6. WHAT I FOUND THAT THE BRIEF DID NOT SAY

Sections 1.1-1.5 hold the five that changed the work. The rest, briefly:

1. **The harvester uses `innerText`, never `textContent`** (`dom.py`). The
   brief's warning about `textContent` is right and the repo had already acted
   on it; the relevant trap here is subtler -- `innerText` DOES carry
   clip-hidden text, which is why the name-carrying copy reaches
   `record["text"]` at all and why the COUNT-based subtraction is load-bearing
   rather than decorative.
2. **2 of 20 committed captures carry the field**, and the byte count on the
   search capture is **2 for ONE fact**. That is the "counting renderings, not
   facts" hazard sitting in the corpus as a measurable, and it is the reason
   de-duplication is on the fact rather than on the match.
3. **`impact_gate.py` exits 0 and prints `nothing staged; nothing to check`
   when the index is empty.** My first run did exactly that and would have read
   as a PASS. Its subject is the git INDEX, so the correct order is
   `git add` -> gate -> `git commit --only`, and a gate run after the commit
   checks nothing. Quoted in section 7.
4. **`J 40` is in two TSVs this wave does not own** --
   `_audit/_census/blocker-map.tsv` and `_audit/_census/blocker-assignments.tsv`
   -- both filing it under `SERVED-BY-GMAIL-SKILL` and both pointing at
   `jobs.md L178`. That line pointer does not resolve to the row, which this
   repository had already noticed and written down:
   `_audit/2026-09-20-the-contingent-writeoffs.md:686` lists `J 40 | jobs.md
   L178 | the TABLE HEADER`. The row itself was at line 228 before this wave.
   **Not touched -- outside the grant, and re-filing a blocker is a ledger act
   that document explicitly deferred. Flagged for the merge.**
5. **The `SKILL` tag was dropped from row 40**, because the table's own legend
   scopes it: *"`SKILL` marks a GAP the `linkedin-jobs` skill serves."* The row
   is no longer a GAP. The skill still serves the same need from mail and the
   cell says so; the tag would have been the legend stretched rather than
   applied.
6. **Two deliberate mutations did not go red, and both are facts about the
   parser rather than holes in the checks** -- see 4.1. One of them reproduces
   a finding this repo already ships a test for.
7. **Nothing navigates, clicks or writes.** No tool was registered, `server.py`
   was not opened, `writes_enabled` is untouched, and the only page interaction
   anywhere in this wave is `page.set_content` over a committed local file in
   the test harness that already existed.
8. **A corpus guard caught two real defects in my own prose**, which is worth
   recording because it is the guard working rather than the guard being in
   the way. `tests/test_a_correction_is_findable_from_the_claim.py` scans for
   correction vocabulary within 2 lines of a citation and demands the pair be
   either DECLARED with markers or TRIAGED. It flagged five candidates across
   three passes. Three were my own wording claiming more than I meant -- I had
   written that the predecessor document "overturned" a reason and labelled my
   own evidence pointer `CORRECTED BY`, when this wave corrects neither
   document and withdraws nothing in either. **Reworded, because the accurate
   sentence and the passing sentence were the same sentence.** The remaining
   two were the table-row false positive described in *THE SECOND OWNERSHIP
   DEVIATION* in section 4.

---

## 7. THE GATES

### 7.1 A GATE ON AN EMPTY INDEX IS NOT A PASS

The first `scripts/impact_gate.py` run printed, in full:

    impact-gate: nothing staged; nothing to check.

and exited **0**. Its subject is the git INDEX, and nothing was staged yet.
Reported as a PASS that would have been a measurement of nothing. The order
this gate requires is `git add <paths>` -> gate -> `git commit --only <paths>`;
run after the commit it checks nothing and says so quietly.

A second run was started, then **killed and discarded** rather than quoted: I
edited three of the files while it was running, so it was measuring a tree that
no longer existed. The quoted run below is the third, started only after the
final content was staged.

### 7.2 THE SCOPED GATE ON THE FINAL STAGED SET

Six changed paths:

* `_audit/_census/jobs.md`
* `linkedin_server/shape.py`
* `tests/test_proximity_reader.py`
* `tests/test_proximity_is_on_a_read_surface.py`
* `_audit/2026-09-21-the-proximity-field.md`
* `tests/test_a_correction_is_findable_from_the_claim.py`

**That list is ORDERED, not alphabetised, and the reason is a property of the
instrument worth knowing.** Written as one prose line, it put the last filename
two lines from the census slice's name -- and that filename CONTAINS a word in
`CORRECTION_VOCABULARY`. The guard duly flagged a candidate pair whose entire
evidence was its own name. **Merely LISTING that file beside another document
manufactures a pair**, so anything mentioning the guard needs its references
spaced out. It fired twice more while this paragraph was being written, on the
paragraph itself, which is the tightest demonstration of the effect available.
Recorded rather than triaged: the fix is formatting, and a `NOT_A_CORRECTION`
entry for it would be an entry about nothing.

**THE GATE'S OWN SCOPE LINE, VERBATIM. There is no "NOT CHECKED" line, and the
reason is the answer to the question that line exists to ask:**

    impact-gate: 6 changed path(s) -> 134 SELECTED + 15 corpus-wide = 134 test file(s).

    WIDENING TO THE FULL SUITE, because the impact set is 134 of 201 test files
    (67%), at or above the 45% line where running everything costs about the
    same and answers more.

So the honest answer to *"what did it not run"* is **nothing**: the gate
declined to be a subset. That is the gate behaving exactly as its own design
requires -- it prints what it did NOT run every time, and here the list is
empty because it widened rather than because it was quiet. A subset reported as
a gate would have been a different measurement wearing the gate's name; this is
the full one.

`linkedin_server/shape.py` alone pulls in 134 of 201 test files, which is worth
recording on its own: this module is the repository's widest blast radius, and
any wave touching it should expect the scoped gate to decline to scope.

**RESULT: the run was still in progress when this wave froze.** The full suite
was measured at roughly 20 minutes on a quiet box; this run was started with
**65 python processes alive** on the box, three waves plus the lead. The log is
at `scratchpad/gate_frozen.log` in this session's scratchpad. **Recorded as
IN PROGRESS rather than as a pass** -- a gate whose result I did not see is not
a gate I may quote, which is the same rule as section 7.1 in the other
direction.

**WHAT DID COMPLETE, and it is not nothing:**

* `tests/test_proximity_reader.py` + `tests/test_proximity_is_on_a_read_surface.py`
  -- **79 passed**, run explicitly on the committed content.
* The corpus-wide guards most exposed to this change, each run explicitly and
  green on the final content: `test_a_person_name_is_never_a_literal`,
  `test_a_sanitiser_earns_its_entry` (116 passed together),
  `test_a_covered_row_names_the_artifact_that_covers_it`,
  `test_an_asserted_name_resolves`, `test_every_orphan_module_is_ruled`,
  `test_a_cited_sha_resolves` (74 passed together), and
  `test_a_correction_is_findable_from_the_claim` (13 passed, after it caught
  two real defects in my prose).
* The **pre-commit identity gate**, which ran for real on the commit -- 7.4.

### 7.4 THE IDENTITY GATE WAS NOT DISARMED IN THIS WORKTREE

The brief says: *"the identity sweep's wordlist is gitignored, so the exact-value
identity gate reports ALLOWING in your worktree and only its shape half is live.
Do not read that as a pass. I will run the real gate at merge."*

**Disk disagrees.** The commit printed:

    pre-commit: identity gate examined 6 staged file(s) against 218 spellings; 0 hits.

That is the LOADED path. The disarmed path prints something else --
`pre_commit_identity_gate.py:129` reads *"identity wordlist absent (it is
gitignored); ALLOWING."* -- and it did not fire.

**Why it is armed.** The hook resolves its interpreter and its scripts against
the MAIN checkout, not the worktree: `COMMON=$(git rev-parse --git-common-dir)`
then `ROOT=$(dirname "$COMMON")`. `pre_commit_identity_gate.py` sets
`REPO = Path(__file__).resolve().parent.parent`, so `REPO` is the main checkout
-- where the gitignored wordlist lives. The hook's own comment dates this fix to
**2026-09-19**, written because worktree agents were hitting "interpreter not
found" and reaching for `--no-verify`. **The brief's caution describes the
behaviour that fix removed.**

**ONE THING THE LEAD SHOULD CONFIRM, because I cannot.** `_staged_paths()` runs
`git diff --cached` with `cwd=str(REPO)` -- the MAIN checkout -- and each
worktree has its own index. It reported **6** staged files, which is exactly
what this wave staged, and git sets `GIT_INDEX_FILE`/`GIT_DIR` for hook
subprocesses, so the inherited environment is almost certainly why it read this
worktree's index despite the `cwd`. I cannot verify the main checkout's index
from here -- a worktree-isolated agent's git calls outside its own worktree are
refused -- so the file COUNT matching is my evidence and not a proof. If that
`cwd` ever wins over the environment, this gate silently examines the wrong
tree, which is worth one check from somewhere that can see both.

### 7.3 THE BOX WAS CONTENDED, AND WHICH READINGS THAT AFFECTS

A lead ruling `_TEAM_LEAD_BOX_IS_CONTENDED.md` landed at this worktree root
mid-wave (read and deleted, per the ack convention): three waves plus the
lead's own gate were live, and a gate measured at 74s earlier ran past 400s.

**Quoted readings, with which run each came from.** The proximity file ran
`65 passed in 20.56s` on a quiet box and `71 passed in 296.50s` for both files
under load -- **the same assertions, the same results, a 14x wall clock**. No
reading in this report is a timing assertion, and every red in section 4 failed
on a VALUE -- a wrong count, a wrong state, a leaked string, a displaced field
-- which contention cannot manufacture. Nothing here rests on a clock.

---
