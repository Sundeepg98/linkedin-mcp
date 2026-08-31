# Slice: `linkedin_my_activity_items` -- item keys, for items measured to be his

**Status:** built, tested, UNCOMMITTED. Tree left dirty for review.
**Branch:** `master`, on top of `3940f72`. Nothing committed, nothing pushed, no
`mcp__linkedin__*` tool called, `_state/` untouched, `readonly._ALLOWED_URL_PATTERNS` and
`_FORBIDDEN_URL_SUBSTRINGS` untouched -- the only surface read is `/in/me/`, which was
already admitted and is already loaded by `linkedin_profile_editor_fields`,
`linkedin_my_profile` and `linkedin_surface_census`.

---

## 0. FIVE THINGS THAT DIVERGE FROM THE BRIEF. READ THESE FIRST.

### 0.1 The tree was NOT clean when this slice started, and the dirty file MOVED under it

At session start `git status --short` in this repo read:

```
 M _audit/2026-08-31-linkedin-lift.md
```

At the end of the slice it reads BOTH that file and a second one:

```
 M _audit/2026-08-31-linkedin-lift.md
 M _audit/_slice-editor-fields.md
```

-- and the second one appeared, vanished and reappeared across three `git status` samples
taken during this slice, which is a sibling agent writing, not a flake.

Neither file was touched by this slice. A sibling agent is writing into `_audit/` while
this ran. Nothing here depends on either file and no test reads them, so this was not
escalated mid-flight -- but "tree clean" in the brief was already false at hand-off, and
whoever reviews this diff should expect an `_audit` entry in it that is not mine.

### 0.2 The suite baseline in the brief is 2205 and it CHECKS OUT -- unlike last slice's

Measured rather than trusted, by the method the previous slice's report records: `git
archive HEAD` into a scratch directory, `git init` plus one commit there so the two
modules that shell out to `git ls-files` can collect, then a full `pytest -q` in that
untouched copy.

```
2 failed, 2203 passed, 6 skipped in 1030.63s (0:17:10)
FAILED tests/test_path_hygiene.py::test_a_cookie_jar_failure_never_returns_an_absolute_path[jar locked by a live Chrome]
FAILED tests/test_path_hygiene.py::test_a_cookie_jar_failure_never_returns_an_absolute_path[jar vanished mid-read]
```

**Both failures are artefacts of the archive copy's location, not of `3940f72`.** That
test asserts an error message carries no absolute path, and the copy lives under a
temp-directory path the real repository does not have; both pass in the working tree, in
the run in section 4. The 6 skips are `tests/test_vendored_buildinfo.py`, which skips when
no `jobcore` checkout sits beside the repository -- deliberately, so a clone of `linkedin`
alone is green.

2203 + 2 = 2205, and 2205 + 6 skipped = 2211 collected. **The brief's number is the
passing count and it is correct.** This is recorded rather than dropped because the
previous slice's report flagged its own baseline as off by two and a reader would
reasonably expect the same again.

### 0.3 `matches_page_owner` is `Optional[bool]`, not `bool`

The brief's return-shape sketch writes `"matches_page_owner": bool`. It is implemented as
a TRI-STATE: `True` compared and matched, `False` compared and different, `None` NOT
COMPARED -- there was no single author to compare, or no single heading to compare it
against.

The reason is the one this package keeps paying for and has three existing precedents:
`checked` and `required` in `EDITOR_FIELDS_JS` and `_ownership_block`'s `same_member`,
all `Optional` for exactly this. `False` for "never measured" is a claim nobody made, and
on this field the wrong reading is specifically "we compared him against the page and he
is not the owner", which is a statement about HIM rather than about the page.

It is load-bearing in the tests, not decorative: A1 asserts `is None` (two authors, so no
comparison happened) and A4 asserts `is False` (one author, one heading, compared and
different). Under mutation M1a those two cases become indistinguishable, which is how the
mutation is caught -- see A1 below.

**If the lead wants `bool`, this is a one-line change in `dom.read_own_activity_items`
plus two assertions.** It is flagged rather than silently taken.

### 0.4 The A1 mutation the brief predicted does NOT produce emission on its own

The brief says: *"MUTATION: drop the C2 unanimity check -> his item is emitted and the
refusal disappears -> red."*

MEASURED: dropping C2 in the SCRIPT alone leaves the refusal in place, because the gate is
in two places. The script decides whether the urn list crosses the boundary at all; the
reader re-derives unanimity in Python from `authors_found` and picks the refusal code.
Either one alone still refuses. The test goes red anyway -- on `matches_page_owner is
None`, because the mutation made a comparison happen that should not have -- but not with
the failure the brief predicted.

So A1 is recorded with **two** unanimity mutations: M1a (script only, the literal reading
of the brief) and M1b (both gates, which produces the predicted emission and is the one
whose failure text carries the other member's urn). Both are below. The defence in depth
is deliberate and is described in the script's own comment; M1b is the mutation that
proves the property, M1a is the one that proves the redundancy is real rather than
decorative.

### 0.5 The tool's docstring names two measured literals instead of quoting them

`readonly.docstring_write_claims` scans every tool description for an unnegated write
verb. `Open control menu for post by ` carries `post` and `/feed/update/` carries
`update`, so the first draft of the docstring made this READ tool fail
`test_no_docstring_claims_a_write` and `test_the_docstring_exemption_does_not_cover_the_reads`.
Measured, not predicted -- the exact contexts the check reported are in section 3.4.

The literals now live only in `dom.ACTIVITY_OVERFLOW_PREFIX` and
`dom.ACTIVITY_PERMALINK_MARKER`, beside the census readings that measured them, and the
docstring names the constants. A comment above the tool records this so an editor does
not paste them back.

---

## 1. What was built

| file | change |
|---|---|
| `linkedin_server/dom.py` | new `ACTIVITY_OVERFLOW_PREFIX`, `ACTIVITY_PERMALINK_MARKER`, `ACTIVITY_MAX_HOPS`, `ACTIVITY_MAX_ANCHORS`, `ACTIVITY_ITEMS_JS`, `ACTIVITY_REFUSALS`, `read_own_activity_items` |
| `linkedin_server/server.py` | new tool `linkedin_my_activity_items`, plus `_authorship_block` beside `_ownership_block` |
| `tests/test_activity_items.py` | NEW, 42 tests |
| `tests/test_readonly.py` | `ACTIVITY_ITEMS_JS` declared in `INJECTED_SCRIPTS`; executed-script count 8 -> 9; `dom.py` evaluate-waiver budget 8 -> 9 |
| `tests/test_server_surface.py` | tool added to `EXPECTED_TOOLS`; count 32 -> 33; non-write count 20 -> 21; test renamed `..._thirtytwo_tools` -> `..._thirtythree_tools` |
| `linkedin_server/server.py` (module docstring) | count corrections, below |
| `README.md` | count corrections and one table row, below |

### Nothing was reused by copying that could have been called

* `server._self_assertion_on` -- reused DIRECTLY for C1. Not re-derived.
* `server._ownership_block` -- NOT reused, and deliberately. The two blocks answer
  different questions and their middle fields are not the same fields: ownership compares
  a member segment across TWO landed urls, authorship compares an author string against a
  heading inside ONE page. Merging them would have produced a block with two fields that
  are `None` on every call, which is the shape a reader stops reading.
  `_authorship_block` is written immediately beside it and its docstring says so.
* `server._member_segment_of` / `_path_without_member` -- NOT used, and this is the call
  most worth a reviewer's eye. The editor tool needs a segment because it compares TWO
  landed urls; this tool loads ONE page, so a lone segment has nothing to be compared
  with. Publishing a redacted landed path would have been a key the brief did not ask
  for. The consequence is that no member segment is read at all, which is why A10's sweep
  for the slug is trivially satisfied -- and A10 asserts it anyway, because "we never read
  it" is a claim that can stop being true.

### The counts my change made false, corrected in the same edit

| where | was | now |
|---|---|---|
| `server.py` line 1 | "thirty-two tools" | "thirty-three tools" |
| `server.py` docstring | "TWENTY read ... Twenty plus seven plus five is thirty-two" | "TWENTY-ONE read ... Twenty-one plus seven plus five is thirty-three" |
| `server.py` docstring | cites `test_the_surface_is_exactly_the_thirtytwo_tools` | cites `..._thirtythree_tools` |
| `README.md` headline | "Thirty-two tools ship. Twenty read." | "Thirty-three tools ship. Twenty-one read." |
| `README.md` derivation note | "thirty-two and twenty are pinned in" | "thirty-three and twenty-one are pinned in" |
| `README.md` file map | "server.py the thirty-two tools" | "the thirty-three tools" |
| `README.md` reads table | "All twenty reads are here" over a table with no row for this tool | "All twenty-one", plus the row |

Each correction records what the line used to say, in the register the surrounding prose
already uses -- and each of the two prose homes now carries a SIXTH correction paragraph
noting that this is the second stale-by-one count in a single day, which is the thing a
reader should take from it rather than the number itself.

**One stale count was left alone, deliberately, for the second slice running:**
`README.md`'s file map says `tests/ 1393 tests`. It is off by roughly nine hundred, it was
stale before this slice touched anything, and correcting it is not this slice's to make.

### The three things the ruling asked for, and where each lives

1. **A key ONLY for an item he authored** -- the emission gate is INSIDE
   `ACTIVITY_ITEMS_JS`. The urn list is attached to the script's return value only when
   `established` is true; the counts cross on every path because every one of them is an
   integer. A caller that has not established authorship never receives an identifier,
   whatever the Python half does or stops doing.
2. **Authorship ESTABLISHED, not inferred from placement** -- three conjunctive
   conditions, all reported. C1 `server._self_assertion_on` on the landed url; C2
   unanimity of the author string across every overflow control on the page; C3 that one
   author against the page's own `h1`, prefix-either-direction.
3. **Never another member's urn, as a TEST** -- A1, with two independent mutations. Under
   M1b the other member's urn appears in `items` and the test prints it; unmutated, it is
   in no part of the serialised answer.

### What it must not do, and where each is asserted rather than described

| claim | assertion |
|---|---|
| no author string, `h1` text or member segment in the answer | A10, over seven paths, sweeping the whole serialised result |
| no control VALUE is read | `test_the_script_never_scrolls_and_reads_no_control_value` -- `".value" not in dom.ACTIVITY_ITEMS_JS` |
| one page, no argument selects a surface | `test_the_tool_reads_one_page_and_takes_no_argument` -- empty `inspect.signature`, and `SELF_PROFILE_URL == CENSUS_SURFACES["profile"]` |
| the docstring warns its output must not be committed | `test_the_tool_warns_that_its_output_must_not_be_committed` |
| the script cannot mutate | `test_the_injected_script_only_reads`, plus its control, plus `tests/test_readonly.py`'s own scan |

---

## 2. A1-A11: every check, shown failing

Each mutation was applied to the working tree, the named test run, the failure captured,
and the tree restored from a snapshot taken immediately before -- automated in
`scratchpad/mutate.py` so no mutation can be left behind. Failure text below is verbatim,
including pytest's own `...` elisions where they occurred; the one place the elision hid
the thing that matters (A1/M1b) was re-run with `-vv`.

### A1 -- THE ONE THAT MATTERS

`test_a_rail_with_two_authors_publishes_no_item_key_at_all`. Fixture: one item his, one
another member's, each with its own urn, plus a stray permalink in a rail footer outside
any item.

**M1a -- C2 relaxed in the SCRIPT only** (`distinct.length === 1` -> `>= 1`):

```
        assert result["authorship"]["authors_found"] == 2
        # NOT COMPARED, and not False: there was no single author to compare.
>       assert result["authorship"]["matches_page_owner"] is None
E       assert True is None
tests\test_activity_items.py:473: AssertionError
```

The refusal did NOT disappear -- the reader's own Python check on `authors_found` still
caught it. See section 0.4.

**M1b -- C2 dropped in BOTH gates** (script `>= 1`, and `if authors != 1:` -> `if False:`).
This is the mutation the brief predicted, and its failure text carries the other member's
item key, which is the whole point:

```
>       assert result.get("refused") == "mixed_authors", result
E       AssertionError: {'authorship': {'established': True, 'how': "LinkedIn's own
    isSelfProfile=true assertion on /in/me/, plus ONE author string across every overflow
    control on the page, plus that string and the page's h1 standing in a prefix relation.
    All three are required and the comparison happens inside the page",
    'self_assertion_present': True, 'authors_found': 2, ...},
    'items': ['urn:li:activity:7400000000000000001', 'urn:li:activity:7400000000000000003'],
    'anchors_per_item': {'urn:li:activity:7400000000000000001': 1,
    'urn:li:activity:7400000000000000003': 1},
    'counts': {'overflow_controls': 2, 'owner_headings': 1, 'permalink_anchors': 3,
    'distinct_urns': 2, ...}, ...}
E       assert None == 'mixed_authors'
tests\test_activity_items.py:460: AssertionError
```

`...7400000000000000003` is the OTHER member's item. Unmutated it is in no part of the
answer.

**M1c -- the pairing rule stops requiring an overflow control**
(`hasOverflowInside` -> `(root) => !!root`), unanimity left intact. This is the brief's
second A1 mutation, and it lands on a different assertion of the same test:

```
        assert result["counts"]["overflow_controls"] == 2
        assert result["counts"]["permalink_anchors"] == 3
>       assert result["counts"]["distinct_urns"] == 2
E       assert 3 == 2
tests\test_activity_items.py:477: AssertionError
```

The refusal is unchanged and no urn is published, which is exactly why A1 asserts the
pairing counts as well as the absence: without them, the refusal would hide the fact that
the pairing rule had stopped running. Three is the stray, now paired to the rail footer.

### A2 -- an all-his rail

`test_an_all_his_rail_yields_exactly_his_item_keys_deduped`. **M3 -- dedupe removed**
(`const index = seen.indexOf(segment);` -> `const index = -1;`):

```
>       assert result["items"] == [HIS_ITEM_ONE, HIS_ITEM_TWO], result["items"]
E       AssertionError: ['urn:li:activity:7400000000000000001',
    'urn:li:activity:7400000000000000001', 'urn:li:activity:7400000000000000002']
E       At index 1 diff: 'urn:li:activity:7400000000000000001' != 'urn:li:activity:7400000000000000002'
E       Left contains one more item: 'urn:li:activity:7400000000000000002'
tests\test_activity_items.py:525: AssertionError
```

### A3 -- no self-assertion, and nothing else read

`test_without_the_self_assertion_nothing_at_all_is_read`. **M4 -- the C1 early return
removed from the tool** (`if not self_assertion:` -> `if False:`):

```
>       assert result.get("refused") == "no_self_assertion", result
E       AssertionError: {'authorship': {'established': True, ...},
    'counts': {'overflow_controls': 2, 'owner_headings': 1, 'permalink_anchors': 2,
    'distinct_urns': 2, ...}, ...}
E       assert None == 'no_self_assertion'
tests\test_activity_items.py:...: AssertionError
```

The "nothing else is read" half is stronger than "no counts came back": the harness puts a
proxy in front of the page and records every script injected, and A3 asserts `scripts ==
[]`. Its control, `test_the_same_markup_reads_when_the_assertion_is_there`, asserts the
identical document DOES inject exactly `dom.ACTIVITY_ITEMS_JS` when the assertion is
present -- so the empty list is a fact about C1 rather than about the fixture.

### A4 -- an `h1` naming a different person

`test_an_h1_naming_somebody_else_refuses`. C1 and C2 both hold; only C3 catches it.
**M5 -- the C3 comparison replaced by an unconditional match** (`ownerMatch = true;`):

```
>       assert result.get("refused") == "author_is_not_the_page_owner", result
E       AssertionError: {'authorship': {'established': True, ...},
    'counts': {'overflow_controls': 2, 'owner_headings': 1, 'permalink_anchors': 3,
    'distinct_urns': 2, ...}, ...}
E       assert None == 'author_is_not_the_page_owner'
```

### A5 -- no `h1` at all

`test_no_h1_at_all_refuses`. **M6 -- a missing heading falls back to the author**, which is
the tempting shape of this bug (one inserted line:
`if (!owners.length && soleAuthor) owners.push(soleAuthor);`):

```
>       assert result.get("refused") == "no_page_owner_heading", result
E       AssertionError: {'authorship': {'established': True, ...},
    'counts': {'overflow_controls': 2, 'owner_headings': 1, 'permalink_anchors': 3,
    'distinct_urns': 2, ...}, ...}
E       assert None == 'no_page_owner_heading'
```

Note `owner_headings: 1` in the mutated answer where the document has none -- the fallback
makes C3 unconditionally true on any page LinkedIn renders without a heading.

### A5b -- two `h1` elements

NOT in the brief's list, and added because the design had to answer "which `h1`" and the
only alternatives were "the first" (picking by position, which this package refuses
everywhere) or "any that matches" (weaker than the rule). The reader refuses instead, with
its own code `ambiguous_page_owner_heading`, and the fixture's FIRST heading is his -- so a
take-the-first implementation establishes here rather than refusing by accident.

`test_two_h1_elements_refuse_rather_than_take_the_first`. **M7 -- two headings resolved by
taking the first** (three edits, one idea: `owners.length === 1` -> `>= 1` in the
comparison guard and in `established`, and `if headings > 1:` -> `if False:`):

```
>       assert result.get("refused") == "ambiguous_page_owner_heading", result
E       AssertionError: {'authorship': {'established': True, ...},
    'counts': {'overflow_controls': 2, 'owner_headings': 2, 'permalink_anchors': 3,
    'distinct_urns': 2, ...}, ...}
E       assert None == 'ambiguous_page_owner_heading'
```

### A6 -- zero overflow controls

`test_zero_overflow_controls_refuses`. **M8 -- the empty-rail refusal removed**
(`if overflow == 0:` -> `if False:`):

```
>       assert result.get("refused") == "no_overflow_controls", result
E       AssertionError: {'refused': 'mixed_authors', 'reason': '0 control(s) on this page
    name an author and 0 distinct names are among them. ...0, ...},
    'counts': {'overflow_controls': 0, 'owner_headings': 1, 'permalink_anchors': 2,
    'distinct_urns': 0, ...}, ...}
E       assert 'mixed_authors' == 'no_overflow_controls'
E         - no_overflow_controls
E         + mixed_authors
```

This one lands on the refusal CODE rather than on emission, and that is the defence in
depth again: the script's `established` still requires `distinct.length === 1`, so an
empty rail cannot publish even with the Python branch gone. What the mutation destroys is
the ANSWER -- "0 controls name an author and 0 distinct names are among them" is a
nonsense sentence, and A6 is what stops it shipping.

### A7 -- the prefix rule

`test_the_prefix_rule_in_both_directions`, three rows.

**M9 -- the prefix rule replaced by exact equality** (`soleAuthor === owner`), which is the
rule the measurement rules out:

```
>           assert result.get("refused") is None, result
E           AssertionError: {'refused': 'author_is_not_the_page_owner', 'reason': 'the page
    carries exactly one author and exactly one h1, and nei...1, ...},
    'counts': {'overflow_controls': 1, 'owner_headings': 1, 'permalink_anchors': 1,
    'distinct_urns': 1, ...}, ...}
E           assert 'author_is_not_the_page_owner' is None
FAILED ...::test_the_prefix_rule_in_both_directions[overflow shortened, h1 full -- the MEASURED asymmetry]
```

The third row -- `Adam Lovelace` against `Ada Lovelace`, which must NOT establish -- is
covered by M5 above, which forces `ownerMatch = true` and makes that row red.

### A8 -- the anchored urn shape

`test_a_permalink_that_is_not_urn_shaped_is_counted_never_emitted`. Two malformed
permalinks sit INSIDE a properly rooted item, so the pairing rule admits them and only the
shape check keeps them out. The second is the realistic near miss: the percent-encoded urn
spelling, which has never been observed in this position.

**M10 -- the anchored shape check removed** (`if (!urnShape.test(segment))` -> `if (false)`):

```
>       assert result["items"] == [HIS_ITEM_ONE, HIS_ITEM_TWO], result["items"]
E       AssertionError: ['urn:li:activity:7400000000000000001', 'not-a-urn-at-all',
    'urn%3Ali%3Aactivity%3A7400000000000000001', 'urn:li:activity:7400000000000000002']
E       At index 1 diff: 'not-a-urn-at-all' != 'urn:li:activity:7400000000000000002'
E       Left contains 2 more items, first extra item: 'urn%3Ali%3Aactivity%3A7400000000000000001'
```

### A9 -- unpaired

`test_a_urn_in_no_item_root_is_counted_never_emitted`. The stray anchor's only
overflow-bearing ancestor is `body`.

**Covered by M1c** (`hasOverflowInside` -> `(root) => !!root`), which pairs the stray to
the rail footer and takes `counts.unpaired` from 1 to 0.

**A DEFECT THIS FIXTURE FOUND, recorded because it was nearly shipped.** The first version
of the climb had only the twelve-hop ceiling, and the comment beside
`ACTIVITY_MAX_HOPS` claimed the ceiling was what stopped a climb reaching `body`. It is
not: a shallow document reaches `body` in TWO hops, well inside twelve, and `body`
contains every overflow control on the page -- so every stray urn would have paired to the
whole render and been published. The script now refuses `body` and `documentElement` by
name (`isDocumentLevel`), the constant's comment says what it used to say and why it was
wrong, and A9 is the test that would have caught it.

### A10 -- no name anywhere, on every path

`test_no_name_or_member_segment_is_anywhere_in_the_answer`, parametrised over all seven
paths the tool has -- the success path and all six refusals -- sweeping the whole
`json.dumps` of the answer for the short author name, the full owner name, the other
member's name and the member slug.

**M11 -- the author string returned in the authorship block's `how` text** (three edits:
the script returns `sole_author`, the reader carries it into `authorship_facts`, and
`_authorship_block` appends it to `how`):

```
>           assert secret not in rendered, (label, secret, rendered)
E           AssertionError: ('established', 'Ada L', '{"anchors_per_item": {...}')
E           assert 'Ada L' not in '{"anchors_p..._loaded": 1}'
E             'Ada L' is contained here:
E               the page: Ada L", "matches_page_owner": true, "self_assertion_present": true,
    "unanimous": true}, "counts": {...}, "item_root_source": {...}, "items": [...]
FAILED ...::test_no_name_or_member_segment_is_anywhere_in_the_answer[established]
```

Its control, `test_every_one_of_those_names_really_is_in_its_markup`, asserts each hunted
string IS in the fixture it is hunted on -- and checks the slug separately, because it
lives in the landed URL rather than in the document and is therefore the one a
document-oriented reader would forget.

### A11 -- `item_root_source`

`test_the_route_that_found_each_item_root_is_reported`, three rows: `data-urn`, `data-id`
and `climb`, all publishing the SAME two urns -- which is what makes the route a report
rather than a behaviour change.

**M12 -- LinkedIn's own root markers ignored** (both `closest` blocks deleted from
`rootOf`):

```
>       assert result["item_root_source"] == expected, result["item_root_source"]
E       AssertionError: {'data-urn': 0, 'data-id': 0, 'climb': 3}
E       assert {'data-urn': ...0, 'climb': 3} == {'data-urn': ...0, 'climb': 0}
E         Differing items:
E         {'climb': 3} != {'climb': 0}
E         {'data-urn': 0} != {'data-urn': 3}
FAILED ...::test_the_route_that_found_each_item_root_is_reported[data-urn]
```

`test_the_root_marker_value_is_never_what_gets_published` is the second half: the
fixture's two item roots carry each OTHER'S urn in `data-urn`, so a reader that published
the attribute returns the same two urns in the opposite order.
**M13 -- the marker's VALUE published instead of the href segment**
(`segment = attrOf(paired.root, 'data-urn') || segment;`):

```
>       assert result["items"] == [HIS_ITEM_ONE, HIS_ITEM_TWO], result["items"]
E       AssertionError: ['urn:li:activity:7400000000000000002', 'urn:li:activity:7400000000000000001']
E       At index 0 diff: 'urn:li:activity:7400000000000000002' != 'urn:li:activity:7400000000000000001'
```

---

## 3. Design calls worth reviewing rather than skimming

### 3.1 The name chain is written a THIRD time, and the matcher is a UNION rather than the chain

`ACTIVITY_ITEMS_JS` carries a third copy of `CENSUS_JS`'s name-resolution chain. The
duplication is forced for the reason recorded above `EDITOR_FIELDS_JS`: the census script
is document-wide and returns raw names for the whole page, and a script assembled from a
shared fragment cannot be certified by `tests/test_readonly.py`'s call-site resolver.
`test_the_activity_chain_resolves_the_same_names_as_the_census` holds the copy to
agreeing, by appending a probe branch to the script's own text so the probe cannot drift
from what the reader runs.

**But the overflow MATCH does not use the chain's single answer.** `CENSUS_JS` resolves
ONE name per control, the first route that answers; this script asks whether ANY of the
five routes yields a name carrying the prefix. That difference is deliberate and it is the
safety direction: a control whose `aria-label` is generic while its `title` names an author
is invisible to the chain, and an author the matcher cannot see is an author C2 cannot
count -- unanimity would hold over a page that is not unanimous, which is the A1 failure
exactly.

`test_the_matcher_sees_an_author_the_chain_would_miss` measures that rather than asserting
it: a fixture with one such control is shown resolving to `More` in the census's answer,
with `OTHER_AUTHOR` in none of the census's names, and the reader refuses it as mixed with
`authors_found: 2`.

### 3.2 The emission gate is in the SCRIPT, not only in the reader

The urn list is attached to the script's return value only when the three conditions hold
inside the page. The counts cross on every path because every one of them is an integer.
This is why several mutations above land on a refusal CODE rather than on emission -- and
it is why M1a and M1b are recorded separately.

### 3.3 A percent-encoded urn is REFUSED, not decoded

The measured `href_shape` carried the literal `urn:li:...` spelling. The encoded form has
never been observed in this position, and admitting a spelling nobody has seen is how a
reader starts accepting shapes it was never shown. It is counted `unrecognised` exactly
like plain junk, and A8 asserts both. **If LinkedIn ever serves the encoded form this tool
silently returns fewer items**, which is the refusal direction, and `counts.unrecognised`
is the field that says so.

### 3.4 The docstring guard fired, and this is what it said

Verbatim from `readonly.docstring_write_claims` on the first draft:

```
('message', '<type>:<six or more digits> -- and will fail the\nbuild. quoting one in a
    commit message, a fixture, an audit note or')
('update', 'is published only if it is anchored-shape and paired. the segment\nbetween
    /feed/update/ and the next delimiter must')
('post', 'control on the page whose accessible name starts with\n   "open control menu for
    post by " carries the same author,')
```

and the surface test:

```
E       AssertionError: {'linkedin_saved_jobs': [...], 'linkedin_my_activity_items': [...]}
E       assert {'linkedin_my...n_saved_jobs'} == {'linkedin_saved_jobs'}
E         Extra items in the left set:
E         'linkedin_my_activity_items'
```

Fixed by naming the two constants instead of quoting them, and by dropping the word
`message`. Recorded in a comment above the tool.

### 3.5 The identity guard was NOT widened, and did not need to be

Every identifier-shaped literal in `tests/test_activity_items.py` is drawn from the
`SYNTHETIC_IDS` and `SYNTHETIC_SLUGS` families `tests/test_no_committed_identity.py`
already sanctions -- the nineteen-digit `74`/`749` activity ids already committed in
`tests/fixtures/notifications.html` and `tests/test_sdui_surfaces_fixture.py`, and the
slug `test_surface_census.py` commits.

**Verified with the file actually TRACKED**, because `git ls-files` is what both sweeps
read and an untracked file is invisible to them. `git add -N tests/test_activity_items.py`,
then:

```
tests/test_no_committed_identity.py tests/test_no_committed_credential.py tests/test_path_hygiene.py
351 passed in 16.98s
```

then `git reset -- tests/test_activity_items.py` to put the index back. **No
`DECLARED_PLANTS` entry, no allowlist entry, no exemption.** That is the right outcome: a
declared plant is a hole in that guard for the whole file and should be earned, not spent
on fixtures that had a sanctioned form available.

### 3.6 Four keys beyond the brief's return sketch, and why each is there

| key | why |
|---|---|
| `pages_loaded: 1` | the editor slice's precedent; lets a caller cost the call |
| `anchors_per_item` | the brief's C4 says "report how many anchors carried each" and the sketch had nowhere to put it |
| `counts.owner_headings` | C3 has TWO failing shapes, zero headings and two, and a caller branching on the refusal code should be able to see which without parsing the reason |
| `truncated` / `truncated_note` | only when the anchor ceiling is hit; the editor slice's precedent |

---

## 4. Numbers

### The suite

```
venv\Scripts\python.exe -m pytest -q
2254 passed in 908.04s (0:15:08)
```

Zero failures, zero skips, zero xfails.

| | collected | passed |
|---|---|---|
| `3940f72`, real working tree (derived, below) | **2211** | **2211** |
| this tree, `tests/test_activity_items.py` UNTRACKED | **2254** | **2254** |
| this tree, with the new file `git add -N`'d | **2256** | not run as a full suite |

**The +43 decomposes exactly, with no residue:**

* **+42** -- `tests/test_activity_items.py`, the new file. Measured:
  `pytest --collect-only tests/test_activity_items.py` -> `42 tests collected`.
* **+1** -- `test_every_script_this_package_executes_cannot_mutate` is parametrised over
  `EXECUTED_SCRIPTS`, which went from eight scripts to nine. Measured:
  `pytest --collect-only "tests/test_readonly.py::test_every_script_this_package_executes_cannot_mutate"`
  -> `9 tests collected`.

**The further +2 when the file is COMMITTED**, which this slice does not do but the review
will: `tests/test_no_committed_identity.py` and `tests/test_no_committed_credential.py` are
each parametrised over `git ls-files`, so a new tracked file adds one case to each.
Measured by `git add -N` (2254 -> 2256 collected) and then `git reset`, which is also how
section 3.5's guard run was done. **Expect 2256 after the commit, not 2254.**

### Why the brief's 2205 and the derived 2211 are BOTH right

`tests/test_vendored_buildinfo.py` holds 8 tests, 6 of which SKIP when no `jobcore`
checkout sits beside this repository. In this working tree `jobcore` IS beside it
(`mcp-servers/jobcore`), so all 8 run:

```
pytest -q tests/test_vendored_buildinfo.py
8 passed in 1.39s
```

In the scratch archive copy used for the baseline in section 0.2 there is no sibling, so 6
of them skipped -- which is exactly the gap between the brief's 2205 and the 2211 this
tree's HEAD produces. That file imports `subprocess`, `pathlib` and `pytest` and nothing
from `linkedin_server`, so this slice cannot have moved it either way.

So: **HEAD in this working tree = 2211 passed** (2203 archive passes + the 2
location-artefact path-hygiene failures that pass here + the 6 vendored-buildinfo tests
that run here), and 2254 - 2211 = **+43**, which is the decomposition above.

### The scan the brief asked for by name

```
>>> readonly.scan_js_for_mutations(dom.ACTIVITY_ITEMS_JS)
[]
```

Asserted twice -- in `tests/test_readonly.py` through `INJECTED_SCRIPTS`, and again in
`tests/test_activity_items.py::test_the_injected_script_only_reads`, which carries its own
control showing the scanner catching a `.click(` planted in this very script.

### Hygiene

* Strict ASCII: `linkedin_server/dom.py`, `linkedin_server/server.py`,
  `tests/test_activity_items.py`, `tests/test_readonly.py`,
  `tests/test_server_surface.py`, `README.md` and this report all `.isascii()` True.
  `tests/test_path_hygiene.py` passes, which is the enforcing check.
* No mutation residue: every mutation anchor was re-counted in the tree after the campaign
  (`distinct.length === 1`, `if authors != 1:`, `if (!urnShape.test(segment))`,
  `if overflow == 0:`, `if headings > 1:`, `closest('[data-urn]')`,
  `root.querySelectorAll(cfg.controlSelector)`, `owner.indexOf(soleAuthor) === 0`,
  `owners.length === 1` x2, `seen.indexOf(segment)`) and `sole_author` appears **0** times
  in both modules.
* `git status --short` at hand-off:

```
 M README.md
 M _audit/2026-08-31-linkedin-lift.md   <- NOT MINE, see section 0.1
 M _audit/_slice-editor-fields.md       <- NOT MINE, see section 0.1
 M linkedin_server/dom.py
 M linkedin_server/server.py
 M tests/test_readonly.py
 M tests/test_server_surface.py
?? _audit/_slice-activity-items.md
?? tests/test_activity_items.py
```

The two `_audit` entries were dirty BEFORE this slice and moved under it while it ran --
at hand-off both are modified where at session start only the first was. A sibling agent
owns them. **Six paths in that list are mine: `README.md`, the two modules, the two test
files I edited, and the new test file, plus this report.** Nothing in `_audit/` other than
this report was written by this slice.
