# Slice: linkedin_surface_census -- BUILT AND GREEN

Status: **DELIVERED.** Tool, DOM reader, shaper and tests are in; the whole
suite passes; nothing is committed and the tree is left dirty as instructed.
Reported: 2026-08-26 09:05 UTC (14:35 IST).

This file replaces the STOPPED report written at 07:49 UTC. That escalation
was resolved by the lead: the colliding agent's work was committed as
`66f3a1d`, the tree was handed to me alone, and the three asks were answered.
The collision history is kept in section 8 because it is the reason the
baseline number in the original brief was wrong.

---

## 1. The exact tool signature

    @mcp.tool()
    async def linkedin_surface_census(surface: str) -> dict[str, Any]

Registered in `linkedin_server/server.py`. Resolved off the live server:
`async def linkedin_surface_census(surface: 'str') -> 'dict[str, Any]'`.

    CENSUS_SURFACES: dict[str, str] = {
        "feed": FEED_URL,                    # https://www.linkedin.com/feed/
        "profile": f"{BASE_URL}/in/me/",     # as linkedin_my_profile builds it
    }

`feed` uses the existing `config.FEED_URL` constant rather than re-spelling
the f-string; the value is identical (`FEED_URL = f"{BASE_URL}/feed/"`) and
the constant was already imported. `notifications` was DROPPED on the lead's
ruling -- see section 5.

The argument is a KEY. No url is ever built from it, and an unknown key
returns a structured refusal that does not reach a navigation:

    {"error": "unknown_surface", "message": ..., "valid_surfaces": ["feed", "profile"]}

Both urls were already on `readonly._ALLOWED_URL_PATTERNS`, and
`BROWSER.goto` puts every navigation through `readonly.assert_read_url` at
`browser.py:410` -- so the census goes through the same door as every other
read. **`linkedin_server/readonly.py` was not touched.** Verified as a
zero-line diff in section 3.

---

## 2. Files changed, with line counts

| file | change | lines |
|---|---|---|
| `linkedin_server/shape.py` | +287 | `census_shape`, `census_redact_rare`, `census_aggregate`, `census_href_identifies_entity` + their tables |
| `linkedin_server/dom.py` | +191 | `CENSUS_JS` (the 4th injected script), `read_surface_census`, `CENSUS_CONTROL_SELECTOR`, `CENSUS_MAX_CONTROLS` |
| `linkedin_server/server.py` | +137 | `CENSUS_SURFACES` + the tool |
| `tests/test_readonly.py` | +12 / -2 | three pin VALUES (section 6) |
| `tests/test_server_surface.py` | +19 / -2 | three pin VALUES + the mandated rename (section 6) |
| `tests/test_surface_census.py` | **new, 761 lines** (28,612 bytes) | 58 tests |

`git diff --stat`: **5 files changed, 644 insertions(+), 6 deletions(-)**, plus
the one new untracked test file. Nothing committed.

---

## 3. The four verification gates, with actual numbers

Interpreter: **Python 3.13.14** (and per the lead's correction, that is what
`venv/Scripts/python.exe` is too -- no 3.10 claim is made anywhere here).

| # | command | result |
|---|---|---|
| 1 | `python -m pytest tests/ -q` | **1657 passed, 0 failed, 463.87s** |
| 2 | `python -m pytest tests/test_readonly.py -q` | **100 passed, 1.37s** |
| 3 | `python -m pytest tests/test_readonly_boundary_invariant.py -q` | **9 passed, 0.40s**, file UNTOUCHED |
| 4 | `python -c "import ast,pathlib; [ast.parse(p.read_text(encoding='ascii')) ...]"` | **OK -- 18 modules parse as ASCII** |

### Gate 1, reconciled

Baseline **1598** (the lead's number, which I re-ran and confirmed at
`66f3a1d`: 1598 passed, 422.27s). Now **1657**. Delta **+59**, and it
reconciles exactly:

* **+58** -- `tests/test_surface_census.py`.
* **+1** -- `test_every_script_this_package_executes_cannot_mutate` is
  parametrised over the injected scripts, which went from three to four.

### Gate 2, the mutation scanner -- no new hits

`readonly.SANCTIONED_MUTATIONS` is still **exactly 2 entries**, unchanged:

    ('linkedin_server/writes.py', 'perform', 'click')
    ('linkedin_server/dom.py',    'activate_messaging_filter', 'click')

Scanning every module in the package returns **exactly 2 raw hits**, and they
are those two:

    dom.py:1406    click
    writes.py:2479 click

**Zero new hits.** The census adds no click, fill, press, check,
select_option, non-GET request or scroll. `readonly.scan_js_for_mutations`
over `CENSUS_JS` returns `[]`, and `tests/test_surface_census.py` carries a
positive control that plants `.click()` into that same script and asserts the
scanner catches it -- the check is shown able to fail.

### Gate 3, the frozen boundary -- untouched

    git diff --stat -- tests/test_readonly_boundary_invariant.py linkedin_server/readonly.py
    (empty)

Zero-line diff on both, and the file passes 9/9. Nothing I did moved a digest.

### Gate 4, ASCII

18 package modules parse as ASCII. Every file I touched re-checked
individually, including the three test files, all clean.

---

## 4. The privacy property, and what it cost to get right

The requirement was that the tool be STRUCTURALLY incapable of returning a
member, not filtered afterwards. Four layers, in the order a name meets them:

1. **`shape.census_shape`** -- substitution: `urn:li:...` -> `<urn>`,
   `/in/<slug>` -> `/in/<member>/`, `/company/<slug>` -> `/company/<company>/`,
   6+ digit runs -> `<id>`, possessive -> `<member>'s`. Then a POSITIVE gate:
   emitted verbatim only if it matches `^[A-Za-z0-9 ,.:!?&()/'-]+$` and is
   <= 60 chars, else `<opaque>`.
2. **`dom.read_surface_census`** -- shapes every name and href before
   returning, so raw strings die in the only caller of the injected script.
3. **`shape.census_href_identifies_entity`** -- a control pointing at
   `/in/<member>/` or `/company/<company>/` has its name replaced regardless
   of count. Applied in the reader AND again in aggregation.
4. **`shape.census_redact_rare`** -- at `count == 1`, any run of capitalised
   words becomes `<redacted>`. Redacted shapes are then RE-MERGED, so two
   one-off names collapse into one row rather than staying two singletons.

**Shown failing, not just succeeding.** `tests/test_surface_census.py` runs a
table of eight adversarial inputs asserting the IDENTITY substring is gone
(not that the output equals something), plus a control proving the table would
catch a shaper that had been switched off, plus a test that drives the reader
with a PII-laden payload and asserts no planted identity is anywhere in the
returned JSON, plus its control proving that detector fires on the raw payload.

### Two departures from the brief, both deliberate, both flagged

**(a) The cap fires at TWO capitalised words, not three.** The brief specified
three. Three does not hold, and I measured it on this implementation before
moving the rule: both of the brief's OWN example leaks survive a three-word
rule. `census_shape("Reply to Jane Doe")` returns `"Reply to Jane Doe"`, and
`census_shape("Jane Doe")` returns `"Jane Doe"` -- two capitalised words each,
inside the character class, under the length limit, so the gate passes them
and a three-word cap never fires. Two is affordable only because the cap fires
on singletons alone: the repeated control, which is the entire signal a
capability measurement is built on, keeps its shape. Cost accepted: a genuinely
unique two-word heading is blanked. Pinned by
`test_the_cap_fires_at_two_words_not_three` so it cannot drift back.

**(b) The href rule is mine, not the brief's.** The count-based cap rests on
"furniture repeats and a person does not", and that premise is false for a
member linked twice on one page -- they merge to `count == 2`, the cap never
runs, and the name ships. The href rule closes it on the STRUCTURE of the
control instead of on the string or the tally.

If either departure is unwanted, both are one function and are reverted
independently.

---

## 5. Notifications, dropped

Done as ruled. `CENSUS_SURFACES` ships two keys. The tool docstring says why
in the Args block and at the constant, in the terms the lead asked for: loading
`/notifications/` clears the operator's unread badge -- measured, irreversible,
and already documented on `linkedin_notifications`, which pays that cost
knowingly because reading the list is the point of it. A census would pay the
same cost to learn what a notification row carries, which is not worth one
destroyed badge. `test_notifications_is_deliberately_not_a_surface` pins the
absence, because the next person to look will reach for it.

---

## 6. The six pins: what each was protecting

The lead asked what a pin enforced by six different tests was holding up. They
are two independent guards, three assertions each, and neither is bureaucracy:

### `tests/test_readonly.py` -- "no script runs that nobody has read"

| pin | was | now | what it protects |
|---|---|---|---|
| `waived_in.get("dom.py", 0) <= 3` | 3 | **4** | The `# readonly-ok` BUDGET. Every waiver is a place where "we only call read methods in Python" stops being a sufficient argument, because `evaluate()` runs code inside the page. Capping the count forces each new one through a reviewable diff. |
| `INJECTED_SCRIPTS` | 3 entries | **+`CENSUS_JS`** | The scan set. A script absent from here is a script whose JS is never checked for mutating tokens. |
| `len(EXECUTED_SCRIPTS) == 3` | 3 | **4** | The stronger half: `EXECUTED_SCRIPTS` is resolved from the AST of every `evaluate()` CALL SITE, not from a naming convention. It exists because a cold review once shipped a constant called `EVIL_INLINE`, carrying `localStorage.setItem` and `fetch(`, past a convention-based check with the whole suite green. This count is what makes a fourth script announce itself. |

### `tests/test_server_surface.py` -- "the surface cannot grow quietly"

| pin | was | now | what it protects |
|---|---|---|---|
| `EXPECTED_TOOLS` | 22 names | **+`linkedin_surface_census`** | Set EQUALITY, so a tool cannot appear without a reviewer seeing the name. |
| `len(tools) == 22` | 22 | **23** | The total. Belt to the set's braces. |
| `len(set(tools) - SANCTIONED_WRITE_TOOLS) == 18` | 18 | **19** | The SPLIT. Without it a new tool arriving as a WRITE would only have to bump the total; this asserts which side of the write boundary it landed on. |

Plus the rename the file's own convention demands --
`test_the_surface_is_exactly_the_twentytwo_tools` ->
`..._twentythree_tools`, the module docstring headline, and a paragraph saying
why this tool is counted even though it is an instrument rather than a
capability. The file states outright that "a test name is a CLAIM like any
other"; leaving a name saying twenty-two over a body asserting twenty-three is
the exact stale claim it exists to catch.

**No pin's strictness moved.** Every one is still an exact `==` or an exact set
equality. No `>=`, no subset check, no skip, no relaxation.

---

## 7. Things that surprised me

1. **The tool count in the ruling was off by one.** The message said "the tool
   count is now 21, so your tool lands at 22". Measured on the live server at
   `66f3a1d`: **22 tools**, and `tests/test_server_surface.py` pinned
   `len(tools) == 22`. `linkedin_draft_applications` was already registered. So
   the census lands at **23**, and 19 non-writes. I used the measured values.
2. **The brief's three-word cap does not hold**, and it fails on the brief's
   own examples. Section 4(a).
3. **The count-based cap has a blind spot the brief's design cannot see** -- a
   member appearing twice. Section 4(b).
4. **The curly apostrophe cost the measurement, not the name.** LinkedIn serves
   U+2019 in "Jane Doe's post". The possessive rule fired correctly on it; the
   captured apostrophe stayed in the output; the character gate does not admit
   U+2019; so the whole shape became `<opaque>`. The name was never leaked --
   every reaction control on the feed collapsed into one meaningless bucket,
   which would have made the census useless on the surface it exists to
   measure, while looking like it was working. Now normalised first thing and
   pinned as a regression.
5. **The structural href rule missed ABSOLUTE hrefs on its first cut.**
   LinkedIn writes member links both ways on one page. An anchored
   `startswith` caught `/in/<member>/` and let
   `https://www.linkedin.com/in/<member>/` through with the name attached. The
   new test caught it, not review.
6. **`pathlib.write_text(..., encoding="ascii")` truncates before it encodes**
   and destroyed my test file at 26,748 bytes -- exactly as the lead's downlink
   described. I had already hit it, diagnosed it and moved to encode-first
   before the ruling arrived, and independently arrived at the same shape
   (`data = text.encode("ascii")` before any open). The file was rewritten from
   scratch; nothing of it was lost beyond the time.
7. **Bash heredocs are unreliable in this shell.** Two separate `<<'EOF'`
   blocks were mangled -- one died with an unmatched-quote parse error on
   content that contained no unmatched quote, and one silently failed to apply
   a `str.replace`. Every file edit here was done through a script file or the
   editing tools instead. Worth knowing for the next slice on this box.
8. **The docstring guard caught the NOUN "update".** `readonly.WRITE_VERBS`
   holds `update`, and "reacting to an update" has no negator within the
   80-character window, so the tool failed
   `test_no_docstring_claims_a_write` until the sentence was reworded. The
   guard is doing exactly what it should; noting it because the phrase was
   descriptive prose about a thing the tool refuses to do, and the next person
   writing an honest docstring will hit the same wall.
9. **`_TEAM_LEAD_CENSUS.md` was read at a boundary and deleted as the
   acknowledgement**, per its own instruction. Disk agreed with the ruling in
   every particular.

---

## 8. Why the original brief's baseline was wrong (kept from the stopped report)

The brief said "1591 passing at commit `5ecfc81`". It was not reproducible:
my run returned 1589 passed / 2 failed, and both failures were another agent's
mid-edit window -- they had modified `readonly.py` at 13:09 and had not yet
re-frozen the digests in `test_readonly_boundary_invariant.py`, which they did
at 13:13. The same file gave 2 failed at 07:36 UTC and 9 passed at 07:44 UTC
with no action from me. That agent then added `linkedin_draft_applications` to
`server.py` at 13:15 and began editing both test files I needed at ~13:18,
which is when I stopped.

The lead has since confirmed the cause (two children in one tree), committed
that work as `66f3a1d`, and confirmed the true baseline as 1598 -- which I
re-measured myself at 1598 passed, 422.27s, zero failures, before making any
edit.

---

## 9. State of the tree

Not committed, as instructed. `git status --porcelain`:

     M linkedin_server/dom.py
     M linkedin_server/server.py
     M linkedin_server/shape.py
     M tests/test_readonly.py
     M tests/test_server_surface.py
    ?? tests/test_surface_census.py
    ?? _audit/_slice-surface-census-tool.md

Also untracked and NOT mine: `.claude/` and `_audit/_slice-draft-stage.md`
(the other slice's report). `_TEAM_LEAD_CENSUS.md` was deleted as its own
acknowledgement.
