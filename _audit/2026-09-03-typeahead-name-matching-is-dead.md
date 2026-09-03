# Addressing a message recipient BY NAME is dead, and it was measured dead

**2026-09-03. Owner: the typeahead wave. Status: CLOSED, NEGATIVE.**

This file exists so that nobody re-opens this in three weeks with a clever
regex. The answer is not "we tried six patterns and gave up"; it is a
measurement of the string being matched, and the string cannot carry the
relation anybody wanted from it.

Read section 1 and section 5. Everything between them is the evidence.

---

## 1. The finding, in one page

`linkedin_send_message` addresses its recipient by typing a NAME into the
composer's combobox and choosing from the typeahead. Choosing requires
identifying ONE suggestion row, and the only property available for that is the
row's ACCESSIBLE NAME.

**The accessible name of a suggestion row is not the person's name.** Measured
live, on the operator's own account, three separate browser sessions:

    every row LinkedIn returns contains the needle            10 of 10
    no row BEGINS with the needle                              0 of 10
    the needle starts at ELEVEN different character offsets
    the offsets sum to 17 placements across 10 rows
    the labels run 49 to 178 characters

Each line kills a different repair:

| measurement | what it rules out |
|---|---|
| every row contains the needle | a SUBSTRING match. It counts LinkedIn's own result set -- a typeahead returns a row BECAUSE it matched what was typed -- so it can never discriminate inside it. |
| no row begins with the needle | every ANCHORED match. Word boundary, negative lookahead, whole-string: all of them refuse everybody rather than refusing correctly. |
| eleven distinct offsets | a SKIP-N-THEN-ANCHOR match. There is no N. |
| 17 placements across 10 rows | a PER-ROW OFFSET. At least one label carries the needle twice, so even a correct offset does not identify a person. |
| labels 49-178 characters | the whole premise. That is a row DESCRIPTION -- name, degree, headline, more -- so the string is not the person's name and no relation over it is a relation over the person. |

**A NAME IS THE WRONG ADDRESSING PRIMITIVE FOR THIS SURFACE.** Every other
write in this package addresses its target by IDENTIFIER: a job id, a company
id, an item urn. `send_message` was the only one addressing a human being by
the text of their name, and the text is not theirs.

---

## 2. How the question got here

**2026-09-03, earlier.** `linkedin_send_message` shipped expecting to refuse,
and it did. A supervised run typed a correct, first-degree name into an empty
composer; `writes._recipient_gate` returned `1_no_recipient_committed` with all
four chip selectors reading zero. **A bare fill commits nobody.** Typing into a
typeahead is not choosing from it.

That settled one question and opened the next: something has to do the
choosing, and whether the choosing commits anybody had never been observed.
`scripts/_probe_typeahead_commit.py` was built to observe it without sending --
it types a name, presses at most one suggestion, reads the composer, and stops.

---

## 3. What each instrument measured, in order

### 3.1 The chip selectors: a bare fill commits nobody

`dom.RECIPIENT_CHIP_SELECTORS`, four candidate spellings, all zero on a clean
composer with a correct first-degree name. Still the only data anyone has about
how a committed recipient is drawn, and **still unvalidated** -- no instrument
has ever observed a committed recipient on this surface. Whatever replaces the
name path will need its own observation built.

### 3.2 The first live probe run: the dropdown is real and readable

    listbox appeared        True
    options (total)         10
    carrying the needle     10
    per candidate selector  [role="option"] 10
                            [role="listbox"] [role="option"] 10
                            [aria-controls] ~ * [role="option"] 0
    refused                 4_several_options_match

**Settled and worth keeping:** the dropdown opens, its rows are readable, and
two of the three candidate option selectors resolve it. That was unknown before
and it is the part of this work that survives.

**Exposed:** ten-of-ten is not a coincidence. It is the substring matcher
counting the result set.

### 3.3 The pattern census: which matcher COULD discriminate

`dom.read_typeahead_pattern_census` counts, per candidate matcher, how many
rows it WOULD match -- six locator counts through the same role engine the aim
uses, integers only, no accessible name crossing into the process.

Live, three runs, three sessions, identical:

    substring                 10
    prefix                     0
    prefix_then_nonletter      0
    prefix_boundary            0
    prefix_then_space_or_end   0
    whole                      0

**`prefix` at zero is the finding.** The rows do not begin with the name.

Two wrong turns are worth recording, because both were reasoned and both were
wrong in the same way:

* **the word boundary.** Proposed as the obvious anchor. It cannot work on a
  label that runs the connection degree onto the name -- `\b` sits between a
  word character and a non-word character, and the last letter of a name and
  the `1` of `1st` are both word characters. It would have matched nobody,
  including the target.
* **the negative lookahead** that replaced it, `^<needle>(?![A-Za-z])`. Correct
  on the shape the fixtures had, and dead on the shape the page has -- because
  it is anchored, and nothing is anchored.

Both derivations came from a fixture built to the only shape any measurement
had shown at the time: name first, degree run on. **That is not a bug in the
fixture. It is the limit of what a fixture can tell you about a page nobody has
read**, and it is why the census was worth building even though it chose
nothing.

### 3.4 The offset scan: why anchoring cannot work

`read_typeahead_needle_offsets`, in `scripts/_probe_typeahead_commit.py`,
returns TWO HISTOGRAMS OF INTEGERS: how
many rows begin the needle at each character position, and how many rows have
each label length. Aggregate rather than per-row, which is strictly less
disclosing and answers the same question.

**It costs no evaluate waiver.** Asking the role engine for rows whose name
begins with exactly *k* arbitrary characters and then the needle, for each *k*,
measures the offset through the same engine the aim uses. The page-function
version was the obvious shape and would have spent the fourteenth injected
script in order to return MORE private data than this returns.

Live:

    rows scanned  10        scanned to 200        error None
    offset  9 -> 7 rows
    offset 15, 16, 17, 20, 21, 26, 28, 31, 40, 50 -> 1 row each
    lengths 49, 56, 59, 87, 94, 143, 151, 152, 178

**IT LIVES IN THE PROBE, AND IT WAS MOVED THERE BY A TEST.** It was written
into `dom.py` beside the other typeahead readers, where
`tests/test_reader_reachability.py` caught it on the full gate: a public
`read_*` in that module must be reachable from the tool surface, and nothing
reaches this one. The choice was an allowlist entry or a move, and the code
decided it -- `UNREACHABLE_BY_DESIGN` is deliberately EMPTY and that file
says empty is the target state, while this reader is STRUCTURALLY probe-only
in two independent ways: it is ~400 locator round-trips, which nothing on
the write path can afford, and its output chooses a MATCHER, which no tool
should ever return. A reader that will never be reachable, in a module whose
rule is that readers are reachable, is in the wrong module. It still calls
into `dom` for the shared escaper, so the one-escaper property that keeps
the census and the aim in agreement is unaffected.

The three verdicts were decided IN THE CODE before the reading, so the answer
could not be fitted to a hope: one offset means constant furniture and a
matcher can skip it; several means no positional matcher will ever work; none
means the substring was matching something else. It returned the second.

---

## 4. What is written into the tree, so this cannot be re-opened by accident

Prose asserting a dead end is a claim nothing checks. These are the checks.

| where | what it holds |
|---|---|
| `tests/test_click_is_not_its_own_evidence.py`, section 2f | `COMPOSER_LIVE_SHAPE` -- markup carrying all three measured properties: furniture of varying width, one row with the needle TWICE, labels long enough to be row descriptions. |
| the same file | `test_no_anchored_matcher_can_work_on_the_shape_the_page_actually_has` -- asserts EVERY anchored candidate reads zero, **derived from `dom.TYPEAHEAD_NAME_PATTERNS` rather than listed**, so a seventh anchored candidate arrives automatically and must answer for itself. |
| the same file | `test_the_offsets_reproduce_the_live_verdict_including_recurrence` -- variable position, recurrence, label width, each asserted. |
| `dom.TYPEAHEAD_SHIPPED_PATTERN` | is `"substring"`, and its comment says the shipped aim is the LOOSEST candidate **because it is the only one that matches anything**, measured rather than chosen. |
| `scripts/_probe_typeahead_commit.py` | prints the census, the offsets, the verdict, the recurrence and the label width, so a future run reports the finding rather than requiring a human to notice it. |

**If somebody adds a seventh anchored pattern, the test goes red and they have
to argue with the live measurement rather than with a comment.** That is the
whole design of section 2f.

---

## 5. What replaces it, and what still has to be built

**THE ROUTE:** LinkedIn's own compose-by-identifier url, found in a committed
fixture, drawn for a first-degree connection at zero live cost:

    /messaging/compose/?profileUrn=urn:li:fsd_profile:<id>&recipient=<id>&screenContext=...

It is currently REFUSED by the read boundary, correctly. Three neighbouring
spellings are admitted by accident and are being closed first, so that the
identifier route arrives as a deliberate admission rather than through a gap.
That work is not this file's.

**WHAT STILL LANDS ON WHOEVER TAKES IT:** *no instrument has ever observed a
committed recipient.* The chip selectors in section 3.1 have never matched
anything on any page. Addressing by identifier removes the CHOOSING problem; it
does not remove the OBSERVING one. A route that commits a recipient this server
cannot then read back is a route that cannot verify its own precondition, and
`writes._recipient_gate` -- which is unchanged, and which is still the only
thing that lets his words be typed -- would refuse it for exactly the reason it
refuses today.

**AND THE NEGATIVE IS WORTH HAVING EITHER WAY.** If identifiers work, this file
records that the name path was proven dead rather than abandoned. A measured
death and an abandoned attempt look identical in a diff and are completely
different artefacts to inherit.

---

## 6. Procedure: pinning a live co-writer, and what it costs

Adopted during this wave and recorded as PROCEDURE rather than as an anecdote,
because a discipline whose cost is written down is trusted more than one that
claims none.

**THE RULE.** When a second builder is writing in the same tree, their
uncommitted work is PINNED -- reviewed, committed alone, credited as not yours
-- before you make any edit of your own. Interleaved uncommitted edits are the
only unrecoverable state; after the pin, an alien change is a diff.

**THE COST, MEASURED.** The full suite at `f6ddfe3` reported four failures.
THREE were the direct cost of the pin: the regex-form change had landed in
`dom.py` while the test asserting the old quoted spelling had not, so the pin
captured a file pair mid-edit. All four were green individually within the
hour. A reader who did not know about the pin would have gone looking for a bug
that did not exist.

**THE MITIGATION, WHICH IS THE PROCEDURE.**

1. Snapshot the contested files OUTSIDE the repo first. Instant, no clobber
   risk, and it survives whatever happens next.
2. Compile-check before staging, so the snapshot is coherent rather than a
   half-written file.
3. Stage the exact paths BY NAME. Never `git add -A` while another builder may
   be in the tree.
4. **Immediately run the tests that OWN the pinned files, and record the result
   in the pin commit message.** This is the step that was missing. It records
   the inconsistency at the moment it is created rather than leaving it to be
   discovered twenty minutes later by a suite, at which point it looks like a
   defect.
5. Credit it. The first line of a pin commit says whose work it is.
6. **GREP THE PINNED CONTENT FOR IDENTITY BEFORE COMMITTING IT.** Added
   2026-09-03, having stepped on it: a live measurement table was pinned
   with the operator's real needle in it, and quoted onward in commit
   messages, because the pin was reviewed for CORRECTNESS and not for
   DISCLOSURE. Adopting somebody else's work adopts their disclosure too,
   and `tests/test_no_committed_identity.py` says in its own first line
   that it cannot catch a name for you.

---

## 6a. A real name reached three tracked files, and the guard was not wrong

Recorded as its own section because the sharpest thing in this episode is a
DISTINCTION, and a distinction stated in passing is a distinction that gets
paraphrased away.

**WHAT HAPPENED.** A real third party's given name -- the needle used in the
live measurements -- was in `linkedin_server/dom.py` (6 occurrences),
`linkedin_server/writes.py` (1) and `tests/test_typeahead_gate.py` (1), and in
commit messages across the unpushed range. It reached origin/master ZERO times.
It was caught before the push, the tip was substituted, and the whole unpushed
history was rewritten.

**THE IDENTITY GUARD WAS NOT WRONG, AND SAYING SO MATTERS MORE THAN THE FIX.**

`tests/test_no_committed_identity.py` opens by declaring this exact limitation
in capitals: *NONE OF THESE CHECKS DETECTS A PERSONAL NAME. NAMES HAVE NO
SHAPE.* It hunts identifier SHAPES -- a session cookie, a member urn, a
key-shaped table -- because a shape can be hunted and a name cannot. It ran
green through every gate on the day this happened and it was CORRECT to. A
guard that documents its own blind spot, and whose blind spot then arrives
exactly where it said it would, is a guard working as designed. Filing this as
"the identity check missed it" would teach the wrong lesson and would make the
next reader trust the check less than they should.

**AND THE SWEEP PASSED FOR A SECOND, DIFFERENT REASON.** The wave lead's
exact-value sweep also passed, and not because it shares the shape limitation:
its wordlist is the OPERATOR's identity -- his name, city, employer, campus.
This was a THIRD PARTY's name. Two independent instruments, two independent
reasons for silence, and neither of them broken. **A name that belongs to
somebody who is not the operator was outside the reach of every check in the
repository**, and that is the finding rather than the near miss.

**HOW IT PROPAGATED, WHICH IS THE PART THAT IS ACTIONABLE.** The regex-form
measurement was recorded VERBATIM in a selector builder's docstring, needle
included. That file was PINNED by the other builder in this tree, and the same
table was then quoted onward in a pin commit message. Reviewing a pin for
CORRECTNESS is not reviewing it for DISCLOSURE, and only the first was done.
Hence step 6 of the procedure in the section above.

**THE RECURRENCE FIX IS IN, AND IT CLOSES THE CLASS RATHER THAN THE INSTANCE.**
The identity key now carries a `measurement_needles` class and the real name is
in it, so this string can never be committed silently again -- and the check is
CONTROLLED IN BOTH DIRECTIONS, so it fails if the string reappears and fails if
the entry goes stale. The substituted placeholder is admitted DELIBERATELY as a
synthetic value rather than tolerated by accident, which is the convention every
other allowlist in that file already keeps.

The principle it encodes is worth stating plainly, because it generalises past
this needle: **a name the operator hands an instrument is, by definition, a real
person.** Any measurement that takes a person's name as input will want to
record that input beside its numbers, and that instinct is exactly what put a
name in a docstring here. The numbers are the evidence; the name was only ever
the input.

## 7. What did NOT move

Verified across the whole wave -- a commit RANGE and not `HEAD`,
deliberately, because a boundary claim written against a moving tip goes
false without anybody editing it. The range is named by its endpoints'
SUBJECTS first and their hashes second:

    from   fix(probe): /in/me is served, not redirected     e923355
    to     docs(typeahead): addressing a recipient BY NAME
           is dead, and it was measured dead                5a4117f

**THE SUBJECTS ARE THE DURABLE HALF AND THIS FILE LEARNED IT THE SAME DAY.**
The range was first written as `e923355..c4e7cd3`. Hours later the unpushed
history was rewritten to substitute a name out of every blob and message,
every hash after the first changed, and `c4e7cd3` became a commit on a
backup branch and nowhere on `master`. **It still RESOLVED**, which is the
trap: `git cat-file -e` said yes, and the reference was already wrong. When
the backup branch is deleted after the push it will stop resolving
altogether. A subject line survives a rewrite; a hash does not.

    linkedin_server/readonly.py       0 diff lines -- never opened
    SANCTIONED_MUTATIONS              4      unchanged
    PERFORMABLE                       12     unchanged
    _ALLOWED_URL_PATTERNS             22     unchanged
    _FORBIDDEN_URL_SUBSTRINGS         23     unchanged
    _FORBIDDEN_SUBSTRING_EXEMPTIONS    2     unchanged
    evaluate waivers in dom.py        13     unchanged
    injected _JS constants            12     unchanged

A new mutating capability, a second mutating path through `perform`, a mutating
probe, and two new measuring instruments all landed, and the boundary did not
move by one entry.

**AND WHAT MOVES IT NEXT MOVES IT INWARD.** Immediately after the range
above closed,
`readonly.py` was opened for the first time in this wave to NARROW
`_ALLOWED_URL_PATTERNS`: three sibling spellings --
`/messaging/thread/new/?recipient=`, `/messaging/?composeTo=` and
`/messaging/?recipient=` -- reached a composer with a recipient attached while
`/messaging/compose/?recipient=` correctly refused. *A ruling one spelling
cannot express is not a ruling, it is a spelling filter.* That change is a
tightening and it is not this wave's; it is recorded here only so that the
numbers above are read as a range rather than as a standing state.

The typeahead click reuses the existing
`(writes.py, perform, click)` sanction by draining the same queue through the
same call site; the name matching and both censuses run through Playwright's
role engine rather than through an injected script.

Nothing was sent to anybody at any point.
