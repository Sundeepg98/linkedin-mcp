# Slice: the draft stage (`?stage=draft`) -- read boundary widened by one alternative

Date: 2026-08-26. Branch `master`, baseline commit `5ecfc81`. **Not committed. Tree left dirty.**

---

## 1. Outcome

All four changes landed. The read allowlist admits a third tracker stage, the AST boundary
invariant was deliberately re-frozen with **only the allowlist digest moving**, and
`linkedin_draft_applications` is registered and reads the list.

Nothing was blocked. Two things in the brief were **wrong on the facts** and one thing became
false as a consequence of the change; all three are in section 6 and none of them changed the
shape of the work.

---

## 2. The digest table -- exactly one digest moved

Computed with the invariant module's **own** `ast_digest` (imported, never re-implemented), over
`git show HEAD:linkedin_server/readonly.py` versus the working tree.

| pinned structure | before (`5ecfc81`) | after | |
|---|---|---|---|
| `_ALLOWED_URL_PATTERNS` | `20224a18ccb46283` | `6542383b4619c935` | **MOVED** |
| `_FORBIDDEN_URL_SUBSTRINGS` | `92b02ca73055330f` | `92b02ca73055330f` | same |
| `_MUTATION_CALL_PATTERNS` | `23aece1483afdee9` | `23aece1483afdee9` | same |
| `JS_MUTATION_TOKENS` | `d47e30b67c583c1b` | `d47e30b67c583c1b` | same |
| `SANCTIONED_MUTATIONS` | `b84365077cba813b` | `b84365077cba813b` | same |
| `<functions>` | `199939f7998e8d48` | `199939f7998e8d48` | same |

**One digest moved.** Every denylist digest and every other constant digest is byte-identical.
`<functions>` did not move either -- no function body was touched.

Note on bookkeeping: `_ALLOWED_URL_PATTERNS` is pinned in **two** dicts in that file
(`READONLY_AST_AT_LAST_REFREEZE` and `DENYLISTS_AT_A76FE32`), so the single moved *value* is
written in two places. That follows the convention the 2026-08-26 messaging re-freeze already set
in the same file, and each site carries its own dated comment saying why it moved.

The digests were re-verified **after** a later comment-only edit to `readonly.py`; all six were
unchanged, which is the invariant's stated design working (comments contribute nothing).

---

## 3. Both Pythons

| interpreter | how | result |
|---|---|---|
| **3.13.14** (default `python`) | `python -m pytest tests/test_readonly_boundary_invariant.py -q` | **9 passed** |
| **3.13.14** (`venv/Scripts/python.exe`) | `venv/Scripts/python.exe -m pytest tests/test_readonly_boundary_invariant.py -q` | **9 passed** |
| **3.10.19** (`C:\Users\<user>\.local\bin\python3.10.exe`) | `ast_digest` driven directly (no pytest on that interpreter) | **identical, all six digests** |

All six digests come out **byte-identical under 3.13.14 and 3.10.19**, and the frozen dicts match
the live values under both. The freeze is version-independent, verified rather than asserted.

**But read the middle row carefully -- see 6.1.** The brief's two commands are the *same interpreter
version*, so on their own they verify nothing about version independence. The real 3.10 lives
elsewhere on this box and is the row that earns the claim.

---

## 4. Test counts

| run | result |
|---|---|
| `python -m pytest tests/ -q` (3.13.14) | **1598 passed** in 429.76s, exit 0 |
| `venv/Scripts/python.exe -m pytest tests/ -q` (3.13.14) | **1598 passed** in 371.29s, exit 0 |
| touched files only, current tree, 3.13.14 | **271 passed** in 17.6s |
| `tests/test_readonly_boundary_invariant.py`, both commands | **9 passed** each |

Zero failures, zero errors, zero skips-that-were-not-already-skips in every run. The two full-suite
runs agree exactly. The **venv run is the authoritative one for the tree as it stands**: the first
full run was started before a final comment-only pass over `readonly.py`, `test_readonly.py` and
`test_tools.py`, so I re-ran the four touched files under 3.13 (271 passed) and let the venv run
cover the whole suite against the current tree.

Baseline was 1591 at `5ecfc81`. **1598 = 1591 + 7**, and the seven are accounted for exactly:

- `tests/test_readonly.py` -- 1 new test function, +1 `ALLOWED` case, +2 `BLOCKED` cases = **4 items**
- `tests/test_tools.py` -- 3 new test functions = **3 items**
- `tests/test_server_surface.py` -- 0 new items (one test **renamed**, counts updated)

No test was deleted, skipped or weakened.

---

## 5. `git diff --stat`

```
 linkedin_server/readonly.py               |  23 +++--
 linkedin_server/server.py                 |  53 +++++++++-
 tests/test_readonly.py                    |  51 +++++++++-
 tests/test_readonly_boundary_invariant.py |  29 +++++-
 tests/test_server_surface.py              |  28 +++++-
 tests/test_tools.py                       | 155 ++++++++++++++++++++++++++++++
 6 files changed, 322 insertions(+), 17 deletions(-)
```

`readonly.py` is **15 insertions / 8 deletions = 23 lines**, which is over the "about 15" guidance
in the brief. The composition is why, and it is worth one look before judging it -- **exactly one
line of it is code**:

```
-        r"^https://www\.linkedin\.com/jobs-tracker/\?stage=(saved|applied)$"
+        r"^https://www\.linkedin\.com/jobs-tracker/\?stage=(saved|applied|draft)$"
```

The other 22 lines are the comment rewrite the brief itself specified: record the date, record that
the token was read rather than guessed, record that the label and the token differ, and record that
`interview`, `archived` and `clicked_apply` stay out. Nothing else in the file was touched --
`_FORBIDDEN_URL_SUBSTRINGS`, `SANCTIONED_MUTATIONS` and every other comment are as they were, which
the five unmoved digests independently confirm.

---

## 6. What surprised me

### 6.1 The venv is **not** Python 3.10 -- it is 3.13.14, the same as the default

The brief says *"default python is 3.13.14; the venv is 3.10"* and asks for the two runs so the
digest can be shown version-independent. Measured:

```
python                    -> 3.13.14
venv/Scripts/python.exe   -> 3.13.14
```

`venv/pyvenv.cfg` says `version = 3.13.14`, and its `home` is the Windows Store 3.13 install. **So
the pair of commands in the brief cannot verify version independence** -- they are one interpreter
run twice. Given this file's own history ("this file has three red CI runs in its history saying
so"), silently reporting "both passed" would have been exactly the fake verification the invariant
exists to prevent.

A real 3.10 does exist on this box, just not where the brief says:

```
C:\Users\<user>\.local\bin\python3.10.exe  ->  3.10.19
```

That is the precise version the file's existing comments name. It has **no pytest installed**, so I
could not run the test module through it; instead I imported the invariant module's own
`ast_digest` under it (with a minimal `pytest` stub, since the module imports pytest at module
scope for `@parametrize` -- nothing in `ast_digest` touches pytest) and compared. Identical, all six,
both before and after the change. The version-independence claim in the new comment is therefore
earned; I have written it as verified under 3.13.14 and 3.10.19 and nothing stronger.

**For the lead:** the brief's step-2 command pair should probably become
`python` + `C:\Users\<user>\.local\bin\python3.10.exe` for future slices, or pytest should be
installed into the 3.10. Also worth noting: `venv/pyvenv.cfg` records that the venv was created
for a directory called `linkedin-own`, not `linkedin`.

### 6.2 The tab-count key follows the **label**, not the stage -- and this nearly stopped the slice

This is the one that mattered, and it took the longest to settle.

`_read_tracker` resolves LinkedIn's own count with `tab_counts.get(stage)` -- keyed on the **stage
string it was handed**. But `shape.parse_tracker_tabs` keys the strip on **the label it read off
the page**, normalised (`"In Progress" -> in_progress`). For `saved` and `applied` those two words
are the same word, so nothing has ever exercised the difference. For this stage they are different
words, and the brief's own live read shows the key as `in_progress`:

```
{"saved": 0, "in_progress": 1, "applied": 0, "interview": 0}
```

Read literally, `tab_counts.get("draft")` returns `None`, and the consequences are not cosmetic:
`empty_is_believable(linkedin_count=None, ...)` is `False`, so a **genuinely empty draft list would
raise `ExtractionFailedError` forever** -- the exact failure `_read_tracker` exists to prevent,
inverted. The brief's premise ("`parse_tracker_tabs` already normalises BOTH labels") is true about
the regex but does not carry the conclusion, because the regex accepting both labels only means the
key mirrors whichever label the page drew.

I was one step from escalating. What resolved it is measurable and had not been written down
anywhere: **LinkedIn relabels the tab to match the selected stage.**

| capture | how it was fetched | tab strip reads | contains "In Progress"? | contains "Draft"? |
|---|---|---|---|---|
| `_audit/_probe-tracker-draft.html` | `?stage=draft` | `Draft <dot> 1` | no (0) | yes (2) |
| `_audit/_probe-tracker-saved.html` | `?stage=saved` | `In Progress <dot> 1` | yes (2) | no (0) |
| `tests/fixtures/jobs_tracker_row.html` (tracked) | draft view | `Draft <dot> 1` | no (0) | yes (2) |
| `tests/fixtures/jobs_tracker_empty.html` (tracked) | non-draft view | `In Progress <dot> 1` | yes (2) | no (0) |

So on the url the tool actually opens, the strip says `Draft`, `tab_counts["draft"]` resolves, and
the reconciliation works exactly as it does for the other two stages. The brief's instruction to
pass `stage="draft"` is **correct** -- for a reason the brief did not state. The counts it quotes
came from a different stage's view.

This is a real coupling that nothing guarded, so I pinned it rather than leaving it as luck:
`test_the_draft_count_resolves_only_because_linkedin_relabels_the_tab` in `tests/test_tools.py`
asserts the working case **and the counterfactual** -- hand the tool the default `In Progress` strip
and it goes loud (`extraction_failed`, "count could not be read") rather than reporting an empty
list. That is the conservative direction, and now it is a documented behaviour instead of an
accident. Existing evidence corroborates it independently: `test_the_populated_tracker_publishes_
its_own_counts` already renders the tracked draft-stage fixture through a real browser and asserts
`{"saved": 0, "draft": 1, ...}`.

`shape.parse_tracker_tabs` was **not** changed, as instructed.

### 6.3 The brief's cited evidence file is gitignored; a tracked one carries the same anchors

The brief points at `_audit/_probe-tracker-draft.html` for the `?stage=draft` token. That file is
matched by `.gitignore:115` (`*_probe-*.html`), so it does not survive a clone -- and this repo's
invariant file explicitly cares about evidence surviving a shallow checkout.

The **tracked** fixture `tests/fixtures/jobs_tracker_row.html` carries the identical LinkedIn
anchors:

```
href="https://www.linkedin.com/jobs-tracker/?stage=draft"
```

So the comments in `readonly.py`, `test_readonly.py` and `test_tools.py` cite the tracked fixture
as the primary evidence and mention the probes as corroboration. The claim is now checkable by
anyone with the repo.

(Related, and left alone as not mine: the gitignore is also what keeps the operator's real draft --
a *ServiceNow Application Developer* posting -- out of the repo. No real identifier entered any file
I touched; the new `DRAFT_CARD` is synthetic in the style of its neighbours.)

### 6.4 One sentence became false, and I repaired it -- the only thing beyond the literal brief

`linkedin_saved_jobs`'s docstring said:

> The tracker also holds In Progress, Interview and Archived tabs. They are not exposed as tools:
> this reads the two lists it names and nothing else.

Adding this tool makes the second sentence false about In Progress. I rewrote those two lines to
name the new tool, because this repo repairs text that a change stales -- the immediately preceding
commit is literally `fix(messaging): the composer is disclosed, and two texts that went stale`, and
`readonly.py`'s own header makes the argument at length. **Flagging it explicitly as scope beyond
the brief**: it is a 3-line docstring edit in `server.py` and is trivially revertible if the lead
disagrees.

### 6.5 The tool count is pinned and had to move

`tests/test_server_surface.py` pins `len(tools) == 21`, the non-write count `== 17`, the exact
`EXPECTED_TOOLS` set, the module headline, **and the test's own name** (that file's stated rule is
that a test name is a claim). Adding a read moved all five to 22 / 18 / +1 name / new headline /
`test_the_surface_is_exactly_the_twentytwo_tools`. The **write count is unmoved at four**, and that
is asserted -- a read arriving must not be able to hide a write arriving beside it.

### 6.6 The server ships two tool counts that nothing pins, and both were already wrong

**Found, deliberately NOT fixed -- flagging for a decision.** These are pre-existing and my change
did not create them; it only made them wronger by one.

`tests/test_server_surface.py` pins the tool count with real rigour -- the set, the total, the
non-write split, the module headline, even the test's own name. But **the two count claims that
ship inside `linkedin_server/server.py` are pinned by nothing at all**, and both were stale at
`5ecfc81`, before I touched anything:

| site | says | true at `5ecfc81` | true now |
|---|---|---|---|
| `server.py:1` (module docstring) | "twenty tools, four of which write" | 21 / 4 | 22 / 4 |
| `server.py:130` (FastMCP `instructions`) | "Fourteen of the eighteen tools read and change nothing" | 17 of 21 | 18 of 22 |

The second one is the one that matters: `instructions=` is the text **every MCP client reads** --
it is what my own tool-surface briefing showed. It has been wrong by three and is now wrong by four.

The first is sharper still as a lesson, because the paragraph directly beneath it is a lament that
this exact count "has now been wrong three times, in both directions", and it carries the sentence
*"Counts in this docstring are re-measured per wave, not carried"* -- while being wrong a fourth
time. The discipline was written down; the instrument that would enforce it was never built, and it
was built one file over instead.

**Suggested follow-up slice** (small, and it closes the class rather than the instance): assert in
`tests/test_server_surface.py` that both strings agree with `len(tools)` and the write split --
parse the numbers out of `server.__doc__` and `mcp.instructions` and compare against the live
surface. Then the next tool to arrive cannot leave either behind, and the count stops being
something a human has to remember. I did not do it here because it is a different change with its
own controls to write, and because the `instructions` paragraph carries other claims that deserve
their own read.

---

## 7. What changed, file by file

**`linkedin_server/readonly.py`** -- one alternative added to one pattern
(`(saved|applied)` -> `(saved|applied|draft)`); the comment above it rewritten to carry the date,
the read-not-guessed provenance, the label/token divergence and the three stages that stay out.
`_FORBIDDEN_URL_SUBSTRINGS`, `SANCTIONED_MUTATIONS` and all other prose untouched.

**`tests/test_readonly_boundary_invariant.py`** -- `_ALLOWED_URL_PATTERNS` re-frozen to
`6542383b4619c935` in both dicts, each with a dated `RE-FROZEN` comment in the file's existing
style, recording what moved, that the other five did not, and the two interpreters it was verified
under.

**`linkedin_server/server.py`** -- `linkedin_draft_applications(limit=DEFAULT_LIMIT)` added directly
below `linkedin_my_applications`, calling `_read_tracker("draft", tab_label="Draft",
surface="draft applications")`. `tab_label="Draft"` is deliberate: it is what the page the tool
opens actually shows, so the error text ("open the url yourself and compare") lines up with what
the operator will see. The docstring carries all four required facts and passes
`readonly.docstring_write_claims` with **zero claims** and `name_implies_write` **False** -- verified
before the code was written, not after. Plus the 6.4 repair.

**`tests/test_readonly.py`** -- `?stage=draft` added to `ALLOWED`; `?stage=interview` and
`?stage=clicked_apply` added to `BLOCKED` (`?stage=withdraw` and `?stage=archived` were already
there); the "exactly two addresses" comment corrected to three; the built-url list gained the draft
url; and a new `test_the_tracker_allowlist_admits_three_stages_and_no_more`.

That new test is the narrowness proof the brief asked for. It pins the permitted set **exactly**,
refuses five stages **individually**, and then shows it cannot pass vacuously: it compiles the
wildcard somebody would reach for (`\?stage=[a-z_]+`) and asserts that wildcard matches every one
of the five refused urls -- so the enumeration is demonstrably the only thing refusing them, and the
test fails the day it stops being an enumeration.

**`tests/test_server_surface.py`** -- counts, headline, `EXPECTED_TOOLS` entry, and the test rename
per 6.5.

**`tests/test_tools.py`** -- `DRAFT_URL`, `DRAFT_TABS`, `DRAFT_TABS_EMPTY`, a synthetic `DRAFT_CARD`,
and three tests: the stage-draft url is what gets built; a corroborated empty draft list is a result
and not an error; and the relabel-coupling test of 6.2 with its counterfactual.

---

## 8. Hygiene

- **Strict ASCII** verified on all six touched files (the middle dot is written `chr(0xB7)`).
- **CRLF preserved** on all six -- 0 bare LF. One self-inflicted scare: my first scripted edit
  rewrote `readonly.py` as LF (every other file in the repo is CRLF); caught by the git warning and
  restored before anything else touched it.
- **Not committed.** No browser launched. Nothing under `scripts/` run. `shape.py` untouched.
- Untracked `_audit/_slice-surface-census-tool.md` is a sibling agent's file -- left alone.
- Scratch harnesses (`digest_probe.py`, `freeze_check.py`) live in the session scratchpad, not the
  repo. They are worth 10 minutes to promote into the repo if the lead wants a standing
  cross-interpreter digest check, since the box has no pytest on 3.10 and the pytest route
  therefore cannot verify version independence at all today.
