# Slice: correct write-count prose rot

Date: 2026-08-31
Files owned and touched: `README.md`, `linkedin_server/server.py` (nothing else).
Repo HEAD at slice start: `77ecd2b`, branch `master`.
NOT committed, NOT staged. `tests/` untouched.

---

## 1. Ground truth, derived before any prose was edited

Every number below was derived twice: once by reading the pinned assertions in
`tests/test_server_surface.py`, and once by enumerating the LIVE tool registry
through `mcp.list_tools()` plus `writes.PERFORMABLE`. The two agree exactly.

| Quantity | Value | Where the number comes from |
|---|---|---|
| Registered tools, total | **31** | `tests/test_server_surface.py:356` -- `assert len(tools) == 31`. Independently: `len(await mcp.list_tools())` == 31. |
| Distinct capabilities | 30 | `tests/test_server_surface.py:352` docstring -- "THIRTY-ONE NAMES OVER THIRTY CAPABILITIES"; `linkedin_login` / `linkedin_login_browser` are one tool under two names. |
| Reads (non-write-shaped) | **19** | `tests/test_server_surface.py:413` -- `assert len(set(tools) - SANCTIONED_WRITE_TOOLS) == 19`. Independently: `set(tools) - (set(tools) & writes.SANCTIONED_WRITES)` == 19. |
| Write-shaped tools registered | 12 | `tests/test_server_surface.py:369-382` -- set equality against the twelve names. Independently: `set(tools) & set(writes.SANCTIONED_WRITES)` == 12. |
| **Writes that can act** | **5** | `linkedin_server/writes.py:3036-3044` -- `PERFORMABLE` frozenset. Pinned at `tests/test_server_surface.py:1252` -- `assert f"{words[len(writes.PERFORMABLE)]} write" in text`. |
| Write-shaped that CANNOT act | **7** | 12 - 5. Named in the `tests/test_server_surface.py:369-382` set and in its docstring: "The other seven are BUILT, GATED AND REFUSING". |

19 + 7 + 5 = 31. Checked arithmetically against the live registry.

The five performable writes, by tool name: `linkedin_save_job`,
`linkedin_unsave_job`, `linkedin_unfollow_company`, `linkedin_apply_job`,
`linkedin_follow_company`.

The seven that refuse: `linkedin_publish_post`, `linkedin_comment_on_item`,
`linkedin_react_to_item`, `linkedin_update_profile_field`,
`linkedin_update_setting`, `linkedin_send_invitation`, `linkedin_send_message`.

Derivation script (throwaway, not harvested):
`C:\Users\<user>\AppData\Local\Temp\_derive.py`. Output reproduced above.

---

## 2. Claims changed

### 2.1 `README.md:6` -- headline

OLD:
```
**Fourteen of its seventeen tools read and change nothing. Three write.**
```
NEW (now `README.md:6-16`):
```
**Thirty-one tools ship. Nineteen read. Five write. The other seven are
write-shaped, gated, and cannot act at all.**

This line said *"Fourteen of its seventeen tools read and change nothing.
Three write"* until 2026-08-31, and it is corrected rather than quietly
widened: every one of those three numbers was stale, and the write count was
stale in the direction that matters. ...
```
NUMBERS FROM: 31 = `test_server_surface.py:356`; 19 = `test_server_surface.py:413`;
5 = `writes.PERFORMABLE` (`writes.py:3036`), pinned `test_server_surface.py:1252`;
7 = 12 (`test_server_surface.py:369-382`) minus 5.

NOTE: I did NOT reuse the old sentence's "read and change nothing" framing,
because it forces a two-way split (reads vs writes) onto a surface that is
actually a three-way split. Collapsing the seven refusers into "reads" would
have produced a number (26) that no test pins and that misdescribes what those
tools are.

### 2.2 `README.md:65` -- exposure-table row

OLD:
```
| Reads, except for three named writes | Nothing is applied to, sent, posted,
endorsed, invited or edited. Saving, unsaving and unfollowing are the
exceptions: ... This row said "Reads only" until 2026-08-23 and the sentence is
corrected rather than quietly widened. |
```
NEW: heading reads "Reads, except for five named writes"; the enumeration now
names all five (saving, unsaving, unfollowing, following, applying); the clause
"Nothing is applied to" is REMOVED; the existing 2026-08-23 correction note is
kept and a second correction clause is appended in the same house style.

NUMBERS FROM: `writes.PERFORMABLE` (5). The removal of "Nothing is applied to"
is forced by `apply_job` being in `PERFORMABLE` -- the clause denied a shipped
write outright.

### 2.3 `README.md:140` -- section heading, and the table under it

OLD: `## The three that write`, over a three-row table listing only
`linkedin_save_job`, `linkedin_unsave_job`, `linkedin_unfollow_company`.

NEW: `## The five that write`, plus a correction paragraph naming what the
heading used to say, plus TWO ADDED TABLE ROWS for `linkedin_apply_job` and
`linkedin_follow_company`, plus a closing paragraph naming the seven that are
write-shaped and cannot act.

WHY THE TABLE ROWS WERE ADDED rather than only the heading: the brief requires
that a sentence enumerating the writes by name must name all five. Changing the
heading to "five" over a three-row table would have replaced one false claim
with a fresher false claim. The two new row descriptions are paraphrased from
the tools' own docstrings (`server.py` `linkedin_apply_job` and
`linkedin_follow_company`) -- specifically the irreversibility warning on apply
and the slug-vs-numeric-id undo asymmetry on follow. No new claim is made that
those docstrings do not already carry.

### 2.4 `README.md:622` -- file tree

OLD: `  server.py                  the seventeen tools`
NEW: `  server.py                  the thirty-one tools`
NUMBER FROM: `test_server_surface.py:356`.

### 2.5 `linkedin_server/server.py:1` -- module docstring headline

OLD: `"""The tool surface: twenty tools, four of which write to LinkedIn.`
NEW: `"""The tool surface: thirty-one tools, five of which write to LinkedIn.`
NUMBERS FROM: as 2.1.

### 2.6 `linkedin_server/server.py:3` -- the self-referential rot counter

OLD: `THIS PARAGRAPH HAS NOW BEEN WRONG THREE TIMES, ...` ending
`the live surface was twenty and four.`
NEW: `... WRONG FOUR TIMES ...`, with the fourth instance recorded ("twenty
tools, four of which write" while the live surface was thirty-one and five),
followed by a new paragraph stating the three-way split and citing the exact
test line each number is pinned at.
NUMBER FROM: the docstring's own record -- it listed three prior wrong states
and was itself in a fourth.

### 2.7 `linkedin_server/server.py:29` -- the write enumeration (the named rot site)

OLD:
```
The four writes are ``linkedin_save_job``, ``linkedin_unsave_job``,
``linkedin_unfollow_company`` and ``linkedin_apply_job``, all registered
below and all behind the same two-call gate.
```
NEW: "The five writes are ..." naming all five including
``linkedin_follow_company``, with a one-clause correction note.
NUMBER FROM: `writes.PERFORMABLE` (`writes.py:3036-3044`).

### 2.8 `linkedin_server/server.py:40` -- the negative enumeration

OLD:
```
* Nothing here sends a message, edits the profile, toggles
  Open To Work, follows a company, or marks anything read on purpose.
```
NEW: "follows a company" struck from the list, with the correction stated and a
clause noting that message / profile-edit / Open-To-Work now have REGISTERED
tools that all refuse, so the list is a claim about what can be PERFORMED.

WHY THIS IS IN SCOPE and not scope creep: this is the same enumeration defect
as 2.7 wearing a negative sign. `linkedin_follow_company` is in
`writes.PERFORMABLE`, so the sentence asserted the absence of a write that is
registered 2200 lines below it, three lines from the list I was correcting.
The remaining clauses were verified still true: `send_message`,
`update_profile_field` and `update_setting` are registered but are NOT in
`PERFORMABLE`; `set_open_to_work` registers no tool at all.
**Flagging this one explicitly for the lead as the single judgment call in the
slice** -- it is a one-word strike plus a note, revertible in one edit.

### 2.9 `linkedin_server/server.py:1884` -- the section banner

OLD:
```
# The two writes
# ...
# EVERYTHING ABOVE THIS LINE READS. These two do not, and they are the only two
# in the package.
```
NEW: `# The five writes`, with the correction recorded and the five named.

FOUND BY SWEEP, not in the brief. This banner sits directly above the five
write tool definitions (`save_job`, `unsave_job`, `apply_job`,
`unfollow_company`, `follow_company` -- verified by reading the `async def`
sequence following line 1884), so it said "the only two in the package" while
standing on top of five. The next banner down, `# The seven that are built,
gated, and refuse`, was checked and is CORRECT -- left alone.
NUMBER FROM: `writes.PERFORMABLE`.

---

## 3. Found suspicious, deliberately NOT changed

These are real staleness. None is a count claim, and each is a multi-paragraph
narrative rewrite rather than a number correction, so all are left for the lead
to route as a separate slice.

1. **`README.md:41-48`** -- bullet `**It does not submit applications, and that
   is not a shrug.**` `linkedin_apply_job` has been in `writes.PERFORMABLE`
   since 2026-08-25, so this is false. NOT CHANGED: it is a capability
   narrative with a section link, not a count, and correcting it properly means
   rewriting the section it points to (below).
2. **`README.md:~186-250`** -- section `### Applying: the half that ships, and
   the half that does not`, including `**1. The apply FLOW has never been
   captured.** Across thirteen job captures ...`. The flow WAS captured on
   2026-08-24 and apply ships. This whole section's rationale is obsolete.
   NOT CHANGED: multi-paragraph rewrite, outside a write-COUNT slice.
3. **`README.md:~292-301`** -- `**Following is the interesting one** ... It is
   still not performable, because the undo cannot be aimed`. False:
   `follow_company` is the fifth performable write. The underlying FACT (the
   undo cannot be aimed) is still true and now lives on the spec in
   `reversible_by`; what changed is who decides. NOT CHANGED: same reason as 2.
   Note this now visibly contradicts my corrected headline, which is an
   argument for scheduling it soon.
4. **`README.md:112-138`** -- the "What it can do" read table lists 14 tools
   but 19 reads are registered. Missing: `linkedin_login`,
   `linkedin_new_messages`, `linkedin_draft_applications`,
   `linkedin_surface_census`, `linkedin_open_messaging`. NOT CHANGED: this is
   an enumeration of READS, and the brief scoped the enumeration requirement to
   the writes; adding five rows means writing five accurate descriptions, which
   is content work rather than count correction. **This is the largest
   remaining gap and the obvious next slice.**
5. **`README.md:624` and `README.md:630`** -- `1393 tests`. Suite baseline in
   the brief is 2023 passed. NOT CHANGED: I was instructed not to run the full
   suite (three siblings editing concurrently), so I CANNOT DERIVE this number,
   and the brief says escalate rather than guess. Flagging, not guessing.
6. **`README.md:79`** (`Four dependencies`), **`README.md:70`** (`all 105
   tracked files`), **`README.md:412`** (`the three read-only DOM harvesters`).
   Number-word hits from the sweep that are NOT tool/read/write counts. Left
   alone deliberately, per the brief.

---

## 4. Verification

Commands run from the repo root with `venv\Scripts\python.exe`:

| Command | Before edits | After edits |
|---|---|---|
| `-m pytest -q tests/test_server_surface.py` | 49 passed | **49 passed** |
| `-m pytest -q tests/test_shape.py tests/test_tools.py` | (not run) | **193 passed** |

Full suite deliberately NOT run, per brief.

Additional checks:
- **Strict ASCII**: both files scanned byte-wise, 0 bytes > 127 in each.
- **No code touched**: `git diff -U0 -- linkedin_server/server.py` filtered for
  non-comment lines returns only module-docstring lines. No executable
  statement, no AST call site changed. `linkedin_server/readonly.py` is not
  touched, so no boundary digest is at risk.
- **MCP instructions string NOT touched** (`server.py:157`, `"nothing. FIVE
  WRITE: linkedin_save_job, "`). Verified already correct and pinned at
  `test_server_surface.py:1252`; left exactly as found, per brief.
- **`tests/` NOT touched.** `git status` shows `README.md` and
  `linkedin_server/server.py` as my only modifications. (`linkedin_server/
  writes.py` and `tests/test_writes.py` also show modified -- those are sibling
  agents' concurrent work in the shared tree, not mine.)
- Nothing committed, nothing staged, `_state/` untouched, no browser launched.
