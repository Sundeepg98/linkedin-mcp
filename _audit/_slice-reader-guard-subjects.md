# Reader-leak guard: exact subject set, and what sits outside it

Slice for wave `what-the-browser-said`, child `agent-af566ba1654c61597`. Purpose: give the
lead an exact, verified boundary of `tests/test_readers_emit_no_page_string.py`'s subject
set, for a ruling about what the server's error envelope may publish. Three measurements,
all offline, all read-only (no browser, no MCP server, no edits to the baseline or any test
file). One new file was added to the worktree: `scripts/_census_reader_guard_subjects.py`
(imports the shipped `discover_readers`, does not reimplement it). Two throwaway helper
scripts for measurements 1 and 3 ran from the session scratchpad, outside the worktree, so
this slice stays read-only apart from that one script and this report.

## Measurement 1 -- the guard's own verdicts, as committed in `tests/reader_leak_baseline.json`

Parsed the committed JSON with `json.load` (not grep/regex) and counted verdicts by the
same rule the guard's own `write_baseline()` uses to summarize itself: split each value on
its first `:`.

- **Total entries: 119**
- **Verdict-prefix counts, spellings exactly as stored** (the file uses underscores
  throughout -- `not_driven`, not the hyphenated `not-driven`):
  - `clean` -- 58
  - `returns_text` -- 40
  - `not_driven` -- 21
  - `leaks` -- 0 (absent from the file; consistent with `write_baseline()`'s own source,
    which refuses to write the file at all if any reader measures `leaks`)
  - No prefix outside `{clean, leaks, returns_text, not_driven}` appears.
- **NOT-DRIVEN reasons, grouped and counted** (21 total, 6 distinct reasons; none withheld
  -- scanned every reason string for URL/absolute-path/slug/name shapes and found none, so
  0 were withheld):
  - 9 -- `raises BrowserUnavailableError` -- e.g. `auth:_cookie_records`, `auth:_cookies`,
    `auth:check_auth`, `auth:login_via_browser`, `auth:require_auth`
  - 5 -- `needs grant: WriteGrant -- this harness does not mint write grants (policy, not
    capability; see GRANT_REFUSAL)` -- e.g. `writes:_live_control`,
    `writes:_recipient_gate`, `writes:_typeahead_gate`, `writes:_verify_after`,
    `writes:perform`
  - 4 -- `raises WriteAttemptError` -- e.g. `writes:_load`, `writes:_read_posting_facts`,
    `writes:observe`, `writes:preview`
  - 1 -- `raises ValueError` -- `dom:activate_messaging_filter`
  - 1 -- `raises ExtractionFailedError` -- `dom:read_unfollow_control`
  - 1 -- `needs observation: Observation` -- `writes:_name_the_invitation_recipient`

**Closing counts: 58 + 40 + 21 = 119, matches the total exactly.**

## Measurement 2 -- live discovery, run today at HEAD

Imported `discover_readers` from `tests.test_readers_emit_no_page_string` (not
reimplemented) via a new script, `scripts/_census_reader_guard_subjects.py`, run from the
repo root with the shared venv interpreter. It calls the real function, no fakes.

- **Readers discovered today: 119**, and the result is confirmed sorted and confirmed
  unique-keyed (both properties the guard's own docstring claims, checked rather than
  assumed).
- **Baseline key count: 119.**
- **Live set equals baseline key set: True. Symmetric difference: 0** (nothing appeared,
  nothing vanished).

**Closing counts: live 119 == baseline 119, zero drift today.**

## Measurement 3 -- the gap: everything the guard's own walk does not take

Independent AST walk (own implementation; does not import `discover_readers`, does not
import `linkedin_server` -- pure `ast.parse` over source text) across all 46 `.py` files
under `linkedin_server/`, including `__init__.py` and `__main__.py` (both parse cleanly and
both define zero module-level functions of any kind). Only each module's top-level
statements were inspected -- class bodies and nested-function bodies were never descended
into, so a method or a closure can never be miscounted as a module-level function. No
module-level function was found sitting inside a top-level `if`/`try` block anywhere in the
package (checked before writing the walker), so that edge case does not apply here.

**Package-wide totals** (module-level functions only, all 46 files):

| class | count |
|---|---|
| IN-SUBJECT-SET (`async def` with a `page` param) | 119 |
| OUT-ASYNC-NO-PAGE (`async def`, no `page` param) | 58 |
| OUT-SYNC (a plain `def`) | 414 |
| **total module-level functions** | **591** |

**IN-SUBJECT-SET (119) agrees exactly with Measurement 1's baseline total and Measurement
2's live count.** Three independently-built measurements -- a committed file, the shipped
instrument's own live run, and this slice's from-scratch AST walk -- land on the same
number. No disagreement to report here.

**Per-module breakdown, `linkedin_server/server.py`:**

| class | count |
|---|---|
| IN-SUBJECT-SET | 6 |
| OUT-ASYNC-NO-PAGE | 52 |
| OUT-SYNC | 28 |
| **module total** | **86** |

(Cross-checked against a column-0 `grep -c "^async def "` / `"^def "` on the same file: 58
async + 28 sync = 86, and 58 async splits into 6 + 52 -- agrees.)

**MCP-tool narrowing, `server.py` only**, exactly as specified -- `ast.unparse()` on each
decorator, substring match on `mcp.tool` (cross-checked against `ast.get_source_segment`
on the same decorators: 0 disagreements between the two methods):

- Of `server.py`'s 52 OUT-ASYNC-NO-PAGE functions, **49** carry a decorator whose unparsed
  source contains `mcp.tool` (cross-checked against a raw `grep -c "^@mcp\.tool"` on the
  file: also 49).
- Of those 49 tool functions, **48** have the substring `_error(` somewhere in their own
  source (signature + body; decorators excluded from this check). The one exception:
  `linkedin_login_browser`.
- For context (read-only lookup, not part of the counted classes): `_error` itself is
  defined at `server.py:1026` as a plain, synchronous `def _error(exc: Exception) -> dict`
  -- i.e. it is doubly outside the guard's subject set (OUT-SYNC, not even
  OUT-ASYNC-NO-PAGE), which is structurally why the reader-leak guard can never discover it
  no matter how the package grows: the guard only ever looks at `async def`.

**Closing counts: package 119 / 58 / 414 (591 total); `server.py` 6 / 52 / 28 (86 total);
49 of `server.py`'s 52 non-page async functions are MCP tools; 48 of those 49 call
`_error(`.**

## What this means for the coverage boundary (measured, not a ruling)

- The guard's subject set is **119 of 591** module-level functions in the package (about
  20%), and by construction it can only ever be `async def` functions that take a `page`
  parameter directly.
- Within the 119 it does take, **40 (`returns_text`) are certified only against THIS
  guard's property** (no page string escapes via an exception or a laundered coercion). The
  guard's own docstring is explicit that whether those 40 readers' return values are safe to
  publish is a separate, different guard's question (`shape.py`, `menus.py`, the redaction
  tests) -- not this one's.
- Also within the 119, **21 (`not_driven`) carry no verdict at all**, positive or negative
  -- the guard's own comment calls this "never a pass." These are concentrated in
  `auth.py`'s `BrowserUnavailableError` paths (9) and `writes.py`'s write-grant-gated
  functions (10 combined: 5 `GRANT_REFUSAL`, 4 `WriteAttemptError`, 1 `Observation`), plus
  two singletons in `dom.py`.
- Outside the 119 entirely: **58 OUT-ASYNC-NO-PAGE functions package-wide, 52 of them in
  `server.py`.** 49 of those 52 are the MCP tool entry points themselves, and 48 of the 49
  call `_error(` -- which is where the guard's own docstring says a laundered exception
  actually reaches a caller (`server._error` catches it, `config.scrub` redacts only this
  server's own paths). **That call site, and the 48 tool functions that reach it, are
  entirely outside this guard's subject set and always will be**, because the guard only
  ever discovers `async def` functions and `_error` is a plain `def`.
- One structural note beyond the numbers: the guard's own `_modules()` helper skips any
  module whose name starts with `__` (via `pkgutil.iter_modules`), so `__main__.py` is
  excluded from the guard's traversal regardless of contents. In this repo that exclusion is
  currently moot -- `__main__.py` defines no module-level functions -- but it is a gap in
  the guard's reach, not merely an empty one today.

## Files touched

- Added: `scripts/_census_reader_guard_subjects.py` (measurement 2; imports the shipped
  `discover_readers`).
- Read-only: `tests/reader_leak_baseline.json`, `tests/test_readers_emit_no_page_string.py`,
  all 46 `.py` files under `linkedin_server/`.
- Not touched: no edits to the baseline, no edits to any test file, no `git add`/commit, no
  browser, no MCP server, no full test-suite run.
