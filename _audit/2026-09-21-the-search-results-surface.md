# THE SEARCH-RESULTS SURFACE -- the largest reader-closable concentration, and what a reader can actually do with it

**CORRECTS:** `_audit/_census/network.md` -- rows `4` and `194` name their blocker as *"no people search"*, which has been false since 2026-09-20, when `/search/results/people/` was admitted with its shaper and its tool; rows `94` and `179` carried EMPTY evidence cells and had never been measured by anybody; row `161`'s citation `readonly.py:547-549` resolves at HEAD to prose about `/in/me/` surviving a redirect, not to the groups comment it names; row `83` states in the present tense that *"the tool reads immediately after the navigation settle"*, which stopped being true when `read_filters_when_settled` landed and `server`'s tool was wired to it. **NO ROW CHANGES STATE** -- nine evidence cells are corrected in place plus five given a built route, the state column is untouched on every one, and `stated rows` is 704 before and after with all four slices identical.

**CORRECTS:** `_audit/_census/messaging-and-content.md` -- row `C70` carries `N 161`'s text verbatim, including the same rotted line citation. Both are repaired to a SYMBOL citation as `CANONICAL-RULING-ID` requires, and both drop the phrase *"NAMED REFUSAL"*, which pointed a reader at `EXCLUDED-RULED` when a comment declining to inherit an address is not one of that state's four admitted grounds. **NO STATE MOVES.**

**No LinkedIn account was touched.** No browser, no navigation, no page load, no
`mcp__linkedin__*` call, `writes_enabled` untouched. Every live number quoted
here was taken by an earlier wave and is cited to the document that took it;
every number this wave took itself was taken offline, against the shipped
instruments, and is printed with the command that produced it.

**NO ROW MOVED STATE.** `stated rows` is 704 before and after, and the census
totals are byte-identical. What this wave produced is one shipped repair, one
shipped instrument, eleven corrected evidence cells and a precisely-named live
requirement for five rows.

---

## 0. THE HEADLINE, FOR A READER WITH ONE MINUTE

1. **A latent name-leak in the search shaper, found, reproduced and repaired.**
   `search_results.tally`'s second parameter reached a bare `int()`, which
   quotes what it refused into its own `ValueError`. On the one surface in
   this server whose control labels read `Connections of <a person>`. It was
   LATENT -- no caller at HEAD passes a raw page value -- and section 3 is
   careful about the difference.
2. **The instrument three documents called "still the smallest unbuilt
   instrument here" is now built, driven and shown failing.** It breaks the
   exact ambiguity that blocks five rows.
3. **Two rows nobody had ever looked at now carry measured blockers**, and
   they were empty because a range in a prior document's wording swept one of
   them along without measuring it.
4. **A citation had rotted into a plausible wrong answer** and was being
   carried by two rows in two slices.
5. **Five rows are NEEDS-LIVE with the exact reading written out** (section 7).
   Nothing was fired.

---

## 1. THE INSTRUMENT, RUN FIRST, AND WHAT ITS CONTROLS PROVE

The brief said not to inherit its numbers. Run here before anything else:

    venv/Scripts/python scripts/reader_closable_blockers.py

```
  CONTROL 1 -- the shipped enumerator agrees with the shipped counter
control jobs.md                      enumerated rows/GAP (150, 56)   shipped (150, 56)   MATCH
control profile.md                   enumerated rows/GAP (203, 55)   shipped (203, 55)   MATCH
control messaging-and-content.md     enumerated rows/GAP (142, 77)   shipped (142, 77)   MATCH
control network.md                   enumerated rows/GAP (209, 87)   shipped (209, 87)   MATCH
  CONTROL 2 -- known answers, across DIFFERENT column layouts
      P A1    want R    got R          OK
      N 1     want W    got W          OK
      M M1    want W    got W          OK
      N 133   want R    got R          OK
  CONTROL 3 -- shown refusing, on cases built to fool it
      want R          got R          OK   the real column
      want unknown    got unknown    OK   no direction cell -- the jobs layout
      want ambiguous  got ambiguous  OK   two direction cells disagree
      want R          got R          OK   column order swapped -- value-based finder is unmoved
  CONTROL 4 -- join accounts for every GAP row
      enumerated GAP 275   joined 274   unjoined 1   OK
```

```
  SEARCH-RESULTS-SURFACE               20   19    0    1    0    0  19
  ...
  TOTAL                               275                           68
  A READER CANNOT BE THE REMAINING COST FOR 207 OF 275 STILL-GAP ROWS.
```

**WHAT THE CONTROLS ACTUALLY BUY, read rather than trusted.** Control 1 is a
borrowed control -- it proves the enumerator agrees with the counter, which is
a property of the *row filter*, not of this file's own work. Control 2 is the
one that matters for the direction column, because it spans four column
layouts including the slice where the direction sits at `c[4]` and the slice
that has no direction column at all; a finder that hardcoded `c[2]` passes
everything else and fails here. Control 3 is the only one shown REFUSING, on
cases built to fool it, and it is what separates a value-based finder from a
plausible string search. Control 4 is an accounting identity, and it is the
one that surfaced the unjoined row below.

**CONTROL 4'S UNJOINED ROW IS NOT A SEARCH ROW, SO IT IS NAMED AND LEFT.**

    P L2b   "Own follower LIST"   direction R   state GAP
    cell: "NOBODY HAS LOOKED. Split from L2 on 2026-09-04 by team-lead ruling."

It is a profile-slice row with no entry in `blocker-map.tsv`. It is the single
row in the whole repository that is GAP, reader-reachable, and assigned to no
blocker at all -- the instrument reports it under `(NOT IN THE MAP)`. **It is
not mine and I did not touch it.** Handing it on: whoever owns the profile
slice should give it a blocker, because at present no blocker-scheduled wave
can ever be sent to it.

---

## 2. MY OWN ENUMERATION OF THE SEARCH ROWS

Enumerated by importing the shipped enumerator and the shipped blocker map --
not by re-parsing the census, which is the mistake `reader_closable_blockers`
records a predecessor making by 66 rows.

**21 blocker-map entries name `SEARCH-RESULTS-SURFACE`. 20 are still GAP.
19 of those are reader-reachable. One (`N 83`) already banked.**

| row | direction | reader-reachable | what it is |
|---|---|---|---|
| `M C70` | R | yes | Search for content within Groups |
| `N 4` | **W** | **no** | Send an invitation from a people-search result |
| `N 79` | R | yes | Search for a person by keyword or NL query |
| `N 80` | R | yes | Narrow search results to People |
| `N 81` | R | yes | Filter by Degree of connections |
| `N 82` | R | yes | Filter by Actively hiring |
| `N 83` | R | -- | Filter by Locations -- **COVERED-PROVEN**, banked 2026-09-21 |
| `N 84` | R | yes | Filter by Current company |
| `N 85` | R | yes | Filter by Connections of |
| `N 86` | R | yes | Filter by Followers of |
| `N 87` | R | yes | Filter by Past company |
| `N 88` | R | yes | Filter by School |
| `N 89` | R | yes | Filter by Industry |
| `N 90` | R | yes | Filter by Profile language |
| `N 91` | R | yes | Filter by Open to volunteering |
| `N 92` | R | yes | Filter by Service categories |
| `N 93` | R | yes | Filter by Keywords (decorated label) |
| `N 94` | R | yes | Add more than one location to a single search |
| `N 161` | R | yes | Search for groups by name or keyword |
| `N 179` | R | yes | Search for events by keyword |
| `N 194` | R | yes | Find hiring managers through the #Hiring hashtag |

**THE 19 AGREES WITH THE BRIEF AND THE 1 W IS `N 4`.** That row can never be
moved by a reader -- it is an invitation -- and section 6 records why it does
not move for three independent reasons.

**THE ROWS SORT INTO FOUR BUCKETS, AND ONLY ONE OF THEM IS A BUILD.**

| bucket | rows | what is actually missing |
|---|---|---|
| **A. Waits on an unmade parameter ruling** | `N 79`, `N 93`, `N 94`, `N 194` | the tool takes no parameter BY DESIGN; a keyword is where a name is typed |
| **B. Address not admitted; needs a DECIDE** | `M C70`, `N 161`, `N 179` | measured False through the shipped gate, section 5 |
| **C. Press route terminally closed** | `N 84`-`N 87`, `N 90`-`N 92`, and half of `N 80` | the `All filters` control fails the disclosing-press ruling by ATTRIBUTE |
| **D. A reader could settle it, and now one exists** | `N 80`, `N 81`, `N 88`, `N 89`, `N 93` | the label-SHAPE ambiguity -- **section 4** |

**ONLY BUCKET D IS A READER'S COST.** That is the honest answer to the question
the brief sent me to ask, and it is smaller than 19. The instrument counts a
row as reader-reachable when its DIRECTION is a read; it cannot know that the
remaining cost is a ruling. **A direction column measures what KIND of act the
row is, never who is blocking it** -- and conflating the two would schedule
fourteen waves at decisions nobody has made.

---

## 3. THE REPAIR: A LATENT NAME-LEAK IN THE SHAPER, ON THE WORST POSSIBLE SURFACE

### 3.1 What was wrong

`search_results.tally` shapes the result counts. Its docstring says:

> "COUNTS BY KIND. Its parameters are INTEGERS -- a needle cannot reach it."
>
> **"CANNOT BE HANDED A NEEDLE EVEN BY MISTAKE" IS NOW TRUE OF THE BEHAVIOUR
> AND NOT ONLY OF THE SIGNATURE.** It coerced with `int()` until 2026-09-20 [...]
> It now refuses the same way the readers do.

**That was true of `counts` and false of `queries_present`.** The 2026-09-20
repair routed the first through the coercion family and left the second at a
bare `int()`:

    "queries_present": int(queries_present),

`queries_present` originates page-side -- `dom.py` returns it as
`queriesPresent` from the search script.

### 3.2 The red, reproduced by driving it

Driving beats reading, so this was executed, not argued:

```
PARAMETER 1 (counts) -- the repaired half
  returned, no raise.  by_kind={'company_result': 2, 'person_result': 0, 'school_result': 3}
  NEEDLE IN OUTPUT? False

PARAMETER 2 (queries_present) -- the unrepaired half
  RAISED ValueError: invalid literal for int() with base 10: 'Star Anise Consulting'
  NEEDLE IN MESSAGE? True
```

`server._error` catches that exception and renders it through `config.scrub`,
which substitutes this server's own PATHS and nothing else. **A name has no
shape to scrub.**

### 3.3 Why nothing caught it, stated precisely

`tests/leakwalk.py` discovers its subjects as **every module-level `async def`
with a `page` parameter** -- deliberately, so a reader written tomorrow is in
the subject set with no edit there. **`tally` is synchronous and takes no
page.** It shapes a page's VALUES without touching the page, so the leak class
had walked one layer out of the guard's subject set.

And `tests/test_search_results.py` asserts:

    assert list(signature.parameters) == ["counts", "queries_present"]

**which pins exactly the half the docstring itself says is not enough.** The
signature was correct throughout. The mechanism was not.

### 3.4 It was LATENT and not LIVE, and I will not overstate it

Every caller at HEAD -- `server`'s tool and two probes -- passes
`read_results`'s already-coerced output. **No run has ever carried a name out
through this.** The property was held by the CALLER'S discipline rather than by
the function, which is exactly what "even by mistake" denies.

**THIS MATTERS FOR THE ADMISSION AND I AM BEING CAREFUL WITH IT.**
`tests/test_the_search_shaper_emits_no_name.py` records that the grant names
its own revocation: *"A measured case of the shaper emitting a name, a slug, a
member id or an urn from that surface -- which revokes the admission, not
merely the shaper."* **This is not such a case.** It is a hole through which
one could have occurred, closed before it did. Reporting it as a measured
emission would be an over-claim, and the admission is not in question.

### 3.5 The repair

    "queries_present": coerce.as_count(queries_present),

`as_count` and not a bare `as_int`, because this module's own rule is that a
substitution is **counted or logged, never silent**, and `tally`'s output
schema is fixed and cannot grow a refusal field without changing a tool's
contract. The log names the TYPE and never the value:

```
WARNING linkedin: a page value that should have been a number was a str;
substituted 0 (the value is not logged, by design)
```

### 3.6 A TYPE GATE IS THE RIGHT REPAIR HERE, AND THAT WAS CHECKED, NOT ASSUMED

`coerce.as_int` is a **TYPE GATE, not a parser**: `as_int("1")` is `None` by
design. So a repair built on it is only correct where the value can never
legitimately arrive as page TEXT -- otherwise it silently substitutes 0 for a
real number and the repair costs a reading.

**Checked at the source rather than reasoned about.** `queries_present` is not
read off the page as text. `dom.py` initialises `queriesPresent = 0` and
accumulates `verdict.query` over the anchor loop, where `verdict` comes from
the shipped pure `classifyRoute`. It is a COUNT, constructed by summation in
the page, and there is no legitimate string form of it for a parser to
recover. A digit walk here would be machinery guarding a case that cannot
arise.

**Where the caveat WOULD bite** is a value lifted out of rendered text -- a
badge reading `"3"`, say. `shape._digits_before` is this package's existing
answer for that shape, and it claims *"NEVER CALLS `int()` AND NEVER RAISES"*,
which was independently verified true. This site is not that shape.

### 3.7 IT IS A CLASS, NOT A SITE -- and three siblings are NOT mine to fix

An AST census over every module-level function in `linkedin_server/` that
lacks a `page` parameter and coerces one of its own parameters:

- **LIVE: none.** No production caller anywhere passes a raw page value into
  such a coercion.
- **LATENT, still open:** `chart_labels.is_readable`, `intro_fields.is_answerable`,
  and `writes.aim_invitation`.

**`writes.aim_invitation` is the one to read**, because it repeats this exact
defect including the docstring:

> "THIS FUNCTION NEVER SEES THE NEEDLE, which is not an accident of the
> signature -- it is the signature doing the work. **Its inputs are three
> integers** [...]"

Its actual signature is `aim_invitation(reading: dict[str, Any])` -- one dict,
not three integers -- and it does `int(reading.get("controls") or 0)` and
`int(matches)`. Both production callers pre-coerce via `dom.read_invitation_surface`,
so it is latent for the same reason `tally` was.

**I DID NOT TOUCH IT.** `writes.py` is not a search file and my brief says to
name what another wave owns rather than change it. **Handing it on:** the
cheapest closure is to route those two through `coerce.as_count` and extend
`leakwalk`'s subject set to page-less shapers, which is the change that would
have caught all four at once.

---

## 4. THE BUILD: THE LABEL-SHAPE READING

### 4.1 The ambiguity it breaks, in the prior wave's own words

`dom.FILTER_PANEL_JS`'s `matchPhrase` requires a SINGLE-WORD phrase to BE the
whole normalised label. That asymmetry is load-bearing -- it is what keeps the
degree filter (`connections`, a closed taxonomy) apart from the person-valued
one (`connections of`, whose value IS A PERSON). Its cost, from `N 81`'s cell:

> It read **0**, and that zero CANNOT distinguish `the page does not draw this
> control` from `the page draws it with a decorated label`. [...] **So the
> remaining route for this row is the label-SHAPE measurement**, which is
> still unbuilt.

Three documents name it unbuilt; one calls it *"still the smallest unbuilt
instrument here"*.

### 4.2 What was added

`windowMatch` -- the SAME token window WITHOUT the single-word asymmetry --
and `decorated[i]`, a count of the controls the shipped matcher REFUSED which
nonetheless carry term `i` as a whole word. Surfaced by
`search_results.read_filters` as `decorated`, coerced by `_counts_only` on the
same path as every other page value and added to the same `values_refused`
total.

**FOUR THINGS IT DELIBERATELY DOES NOT DO.**

1. **It does not loosen `matchPhrase`.** That is the repair the module refuses
   in as many words, because loosening is what would let `connections` match
   `Connections of <a person>`. The shape pass is a SECOND, SEPARATELY
   COUNTED reading and the matcher is untouched.
2. **It returns no label**, for the reason the module already gives: the
   matching happens IN THE PAGE precisely because a label here can be a
   person's name.
3. **It returns no WORD COUNT**, which was a real temptation and is refused on
   purpose -- a word count of a label reading `Connections of <a person>` is a
   fact about that person's name. `decorated` is a count of CONTROLS.
4. **It costs no new `evaluate` waiver.** `dom.py` sits at **exactly 22 of 22**
   and the cap is `<= 22`, so a new call site would have needed a ruling. The
   shape pass extends the existing `read_search_filters` evaluate. A committed
   test pins this.

### 4.3 It is decisive in ONE direction only, and that is the whole care

`search_results.shape_verdict(whole, decorated)` owns the interpretation, as a
SYMBOL, so no wave re-derives it in prose -- this repository has paid four
times for one answer re-derived in four places.

| reading | verdict | what it proves |
|---|---|---|
| `counts >= 1` | `present` | what the shipped matcher already said |
| `counts 0`, `decorated 0` | **`absent`** | **the strong one** -- no control carries the word at all, which eliminates the decorated-label explanation |
| `counts 0`, `decorated >= 1` | `undecided` | a word occurs somewhere; it does NOT say on what |

**`undecided` is never `present`, and this vocabulary's own collision is why.**
The window fires on `Connections of <a person>` for the bare term
`connections`. A caller reading a nonzero `decorated` as *present* would report
the person-valued filter as the degree filter -- precisely the scar the
asymmetry exists for.

### 4.4 Driven, under a real engine, against the shipped artifact

Lifted by brace-matching, never transcribed, using the harness the matcher's
own corpus test already ships:

```
  label                        phrase           whole  window
  Connections                  connections      True   True    OK  the bare control -- present
  Degree of connections        connections      False  True    OK  THE DECORATED CASE -- what the instrument is for
  Locations                    locations        True   True    OK  single word, whole label
  Anise Starfield              connections      False  False   OK  THE ABSENT CASE -- neither reading fires
  Connections of               connections of   True   True    OK  the two-word term matches by containment
  Connections of               connections      False  True    OK  THE COLLISION: whole-label refuses, window does NOT
  Current company              current company  True   True    OK  multi-word, whole
  Filter by current company    current company  True   True    OK  multi-word already matches by containment
```

**AND A STRUCTURAL PROPERTY OVER THE WHOLE SHIPPED VOCABULARY, not a sample:**
`decorated` can only ever fire for a SINGLE-WORD term, because a multi-word
phrase already matches by containment. Measured for all 14 terms, 14 of 14
consistent. The six single-word terms are `keywords` (`N 93`), `connections`
(`N 81`), `locations` (`N 83`, banked), `school` (`N 88`), `industry`
(`N 89`), `people` (`N 80`) -- **which is exactly the five open rows this
instrument serves.**

---

## 5. WHAT THE 2026-09-19 WORK ACTUALLY LEFT IN THE TREE

The brief warned not to trust a WIP commit message as a statement about the
current tree. Checked against the tree, three of the prior framings have moved:

1. **"A PRESS NOBODY HAS RULED ON" is superseded.** The press IS ruled
   (`DISCLOSING-PRESS-PERMITTED`, 2026-09-19) and the `All filters` control
   fails its condition 2 TERMINALLY -- measured live twice, carrying neither
   `aria-expanded` nor `aria-haspopup`, on a reader shown reporting PRESENT
   for two other controls on the same reading. Condition 3 refuses it again
   for want of a declared sensitivity basis. **These are opposite kinds of
   blocker**: an unmade ruling resolves, a terminal mechanism refusal does
   not. The cells already carry the correction; I confirmed it and did not
   redo it.

2. **The panel race is CLOSED, and a cell still described it as live.**
   `search_results.read_filters_when_settled` exists and `server`'s tool calls
   it -- landed in `9093637`. A consolidated reading of the 2026-09-21
   documents still lists "a wait-for-the-panel fix" as unbuilt; **the tree
   disagrees, and the tree wins.** `N 83`'s cell carried the present-tense
   clause *"the tool reads immediately after the navigation settle"*, which is
   no longer true of the tool. Corrected in place; the row does not move and
   the third firing's reading stands exactly as reported.

3. **Condition 5 does not reach the press, and this wave did not need it.**
   Condition 5 is *"NOTHING IS FIRED FROM THAT SURFACE. No connect, no follow,
   no message, no invitation"* -- it governs firing AT A PERSON. Opening a
   filter panel is none of those. The press was refused by the disclosing-press
   ruling's own conditions 2 and 3. **Condition 5 does still bind `N 4`**,
   which names one of its four enumerated acts.

**What the 2026-09-19/20/21 work genuinely left:** the admission of exactly one
vertical, a name-free shaper, a tool that takes no parameter by design, the
first live firing of the surface, one banked row, and a correctly-named
terminal press refusal. I rebuilt none of it.

---

## 6. WHAT I CHECKED IN `RULINGS.md` RATHER THAN DERIVING

Four registered rulings settle questions this wave would otherwise have
re-derived. Cited, not re-argued:

- **`SEARCH-ADMISSION-APPROVED-FIVE-CONDITIONS`** -- the admission and its
  condition 5, which is why `N 4` cannot move and why nothing was fired.
- **`SEARCH-CONDITION-2-CLOSED`** -- CLOSED path segments, not a narrow
  anchored pattern. This is why the allowlist holds exactly one
  `/search/results/` entry and why `N 161`/`N 179`/`M C70` are refused by
  shape rather than by an oversight.
- **`EXCLUDED-RULED-ADMISSION`** -- the four grounds. This is what stops
  `N 179` and `N 161` being filed EXCLUDED-RULED on the strength of a comment.
- **`CANONICAL-RULING-ID`** -- a citation resolves to a SYMBOL, never a line
  number. Section 8 is that rule's own failure mode, found in the wild.

---

## 7. PER ROW: WHAT I BUILT, WHAT I DROVE, AND THE STATE ASSIGNED

**Every row below stays in the state it was in. The 704 is unchanged.**

### 7.1 NEEDS-LIVE -- five rows, with the exact reading written out

`N 80`, `N 81`, `N 88`, `N 89`, `N 93`.

**THE READING THAT WOULD CLOSE THEM, STATED EXACTLY.** Fire
`search_results.read_filters_when_settled` against the live people-search page
with `panel_wait.settled` True and `controls_last` in its measured 73-83 band,
and read the `(counts, decorated)` pair for the term:

| row | term | closes on |
|---|---|---|
| `N 80` | `people` | `decorated` 0 settles the control question; the row also needs its "narrows to" wording answered, and the route half is already proven by 18-against-0 `person_result` |
| `N 81` | `connections` | `counts 0, decorated 0` -> **ABSENT**, a MEASURED-ABSENT candidate |
| `N 88` | `school` | same |
| `N 89` | `industry` | same |
| `N 93` | `keywords` | `decorated >= 1` would CONFIRM the module's own advance prediction of a decorated label -- and still not close it, because UNDECIDED is not present and the row also waits on the parameter ruling |

**A non-zero `decorated` closes nothing**, by construction (section 4.3). Only
the zero is decisive. **I did not fire it.** The brief sequences browser work
elsewhere and eight other waves are running; the instrument is committed
UNFIRED and says so.

### 7.2 Cells corrected in place, no state moved -- eleven rows

| row | what was wrong | now |
|---|---|---|
| `N 94` | **cell was EMPTY** -- swept along by the range wording `80-94` while the fourteen-fired wave measured only `80`-`93` | measured blocker: the address IS admitted (including with a query string); nothing can COMPOSE one; strictly behind `N 79` |
| `N 179` | **cell was EMPTY** -- carries this blocker but sits outside the people block, so every wave passed it | `is_read_url` False, measured; GAP with a NAMED BLOCKER and explicitly NOT EXCLUDED-RULED |
| `N 161` | citation rotted; "NAMED REFUSAL" too strong | symbol citation; the EXCLUDED-RULED distinction spelled out |
| `M C70` | same two, carried verbatim into a second slice | same, plus both address spellings measured False |
| `N 4` | *"no people search exists here at all"* -- **false at HEAD since 2026-09-20** | three independent reasons it still does not move |
| `N 194` | *"Blocker: no people search."* -- same falsehood | replaced with the parameter ruling `N 79` names |
| `N 83` | present-tense claim about a race that has since been closed | corrected; explicitly does NOT upgrade the third firing retroactively |
| `N 80`, `N 81`, `N 88`, `N 89`, `N 93` | named a route as "still unbuilt" | route now built and UNFIRED, with the closing reading written out |

### 7.3 Rows I touched for nothing, and why that is the right answer

`N 82`, `N 84`-`N 87`, `N 90`-`N 92`, `N 79`, `M C70`/`N 161`/`N 179` as
capabilities.

- **`N 84`-`N 87`, `N 90`-`N 92` (multi-word terms behind the panel).** The
  shape reading cannot help them: `decorated` is 0 for a multi-word term by
  construction, because containment already matched. Their route is the press,
  and the press is terminally refused by attribute. **The only remaining route
  measured for them is a reader over response bodies**, which a prior wave
  priced as a HEAVIER ruling request than the press itself -- a raw, unshaped
  read on a third-party-dense surface. Not a reader's cost.
- **`N 82`.** Matched live at 2 and deliberately not banked; a present field is
  not a meaningful one. Settling it needs a SCOPED selector, and scoping
  without reading labels on this surface is the open problem. The shape reading
  does not address scoping and I did not pretend it does.
- **`N 79`, `N 93`, `N 94`, `N 194`.** A ruling, not a measurement.
- **`M C70`, `N 161`, `N 179`.** A DECIDE on an address, not a measurement.

---

## 8. THE CITATION THAT HAD ROTTED INTO A PLAUSIBLE WRONG ANSWER

`N 161` and `M C70` both read:

> `/search/results/groups/` is a NAMED REFUSAL in `readonly.py`'s own groups
> comment (`:547-549`)

**At HEAD, `readonly.py` lines 547-549 are prose about `/in/me/` surviving a
redirect.** The real comment is roughly 200 lines further down. This is the
specific failure mode worth naming: the citation does not dangle, it lands on
*another allowlist comment*, so a reader who follows it finds something
plausible and stops. `CANONICAL-RULING-ID` already rules that every citation
resolves to a SYMBOL and never to a line number -- **this is that rule's own
failure mode, found in the wild, in two slices at once.** Both now cite the
entry by symbol.

**AND "NAMED REFUSAL" WAS POINTING AT THE WRONG STATE.** A comment declining to
inherit an address is not one of the four grounds `EXCLUDED-RULED-ADMISSION`
admits. Left alone, that wording invites a future wave to file both rows
EXCLUDED-RULED on a decision nobody made -- which is exactly what
`INCIDENTAL-CAPTURE-IS-NOT-A-RULING` forbids.

---

## 9. EVERY CHECK, SHOWN FAILING

### 9.1 The shape reading -- two plants

    venv/Scripts/python scripts/_check_the_shape_reading_can_fail.py

```
PLANT 1 -- THE LOOSENING the module refuses (single-word asymmetry deleted)
  bindings rebound: 2
FAILED tests/test_the_search_shape_reading.py::test_the_collision_is_not_resolved_by_the_shape_pass
FAILED tests/test_the_search_shape_reading.py::test_the_decorated_case_is_what_separates_absent_from_undecided
  pytest exit 1 -> RED (wanted RED)   OK

PLANT 2 -- THE INSTRUMENT THAT MEASURES NOTHING (windowMatch == matchPhrase)
  bindings rebound: 2
FAILED tests/test_the_search_shape_reading.py::test_the_decorated_case_is_what_separates_absent_from_undecided
FAILED tests/test_the_search_shape_reading.py::test_the_collision_is_not_resolved_by_the_shape_pass
FAILED tests/test_the_search_shape_reading.py::test_the_shape_pass_can_only_fire_for_a_single_word_term
  3 failed, 5 passed
  pytest exit 1 -> RED (wanted RED)   OK

CLEAN -- the shipped script, unplanted
  bindings rebound: 2
  8 passed
  pytest exit 0 -> green (wanted green)   OK

RESULT: every plant fired and the clean run was green
```

**`bindings rebound: 2` IS PART OF THE PROOF.** `search_results` binds
`_MATCH_IN_PAGE = dom.FILTER_PANEL_JS` at import, so rebinding
`dom.FILTER_PANEL_JS` alone would have reached nothing the lifters ever read
and this script would have reported a check that "cannot fail" while never
handing it a defect. A count of zero is a loud failure of the script.

**PLANT 2 IS THE ONE WORTH HAVING.** An instrument whose output is well-formed,
integer-valued, and empty is the failure a green suite never shows.

### 9.2 The leak repair -- shown red at its own site

The new tests, run with `coerce.as_count` rebound to a bare `int()`:

```
CLEAN -- the repair in place                       2 passed    -> green
PLANTED -- coerce.as_count restored to a bare int()
E   ValueError: invalid literal for int() with base 10: 'Exampleperson Markersurname'
E   AssertionError: tally raised an exception quoting a value the page chose
E    +  where ['$(str) carries a plant', '$(repr) carries a plant',
E              '$.args[0] carries a plant'] = _carries_a_plant(ValueError(...))
  2 failed                                                     -> RED
RESTORED -- the repair back in place               2 passed    -> green
RESULT: the new tests DO fail without the repair
```

### 9.3 One of my own checks was wrong and is recorded

`test_the_page_script_returns_no_label_on_the_shape_path` first swept the
return block for the substring `label` and convicted `empty_labels:` -- a key
that legitimately contains it and counts labels that were EMPTY. **A check
that fails for the wrong reason is as useless as one that cannot fail.** It
now parses the return object and tests the right-hand SIDES against a closed
set of integer-bearing expressions, which is both correct and stricter.

### 9.4 Suites run

```
tests/test_search_results.py
tests/test_readonly.py
tests/test_readers_emit_no_page_string.py
tests/test_the_search_shape_reading.py        481 passed in 243.56s
tests/test_the_search_shaper_emits_no_name.py  42 passed in 35.40s
```

---

## 9.5 THE DERIVED FILES -- TWO REGENERATED, ONE DELIBERATELY NOT, AND WHY

`_audit/INDEX.md` and `_audit/RULINGS.md` were rebuilt with their own build
scripts and their diffs are **entirely caused by this document existing**:
tracked audit documents 217 -> 218, documents scanned 216 -> 217, headings
naming a ruling 102 -> 103. Those are mine and they are committed.

**`_audit/_census/blocker-map.tsv` WAS REGENERATED, MEASURED, AND THEN PUT
BACK.** Running `scripts/build_blocker_map.py --write` produced a 403-row
diff. Measured rather than eyeballed, against the committed version:

    GATED columns (row_id / blocker / evidence_class) differing:   0
    column reason_doc      rows changed                          369
    column state_today     rows changed                           34
    rows citing THIS document as their reason_doc                  0

**None of it is mine, and none of it is checked by anything.**
`tests/test_blocker_map_is_derived.py::test_the_committed_map_still_matches_what_the_evidence_derives`
compares exactly three of the map's ten columns, so the committed file is
correct on everything any guard reads. The 403 moved rows are other waves'
census movement and the natural drift of a reason-locator ranking over a
corpus that has grown since the map was last built.

**THE RULE SAYS "REGENERATE, NEVER HAND-MERGE", AND PUTTING IT BACK IS NOT A
HAND-MERGE.** That rule exists to stop a human editing a derived file into
agreement. I am doing the opposite: declining to carry 403 rows of other
waves' work inside my commit, where it would collide with every sibling wave
that regenerates, during a SERIAL merge, for zero content of my own. **The
integrator should regenerate this file ONCE after the last merge** -- one
rebuild against the settled corpus is strictly better than eight waves each
carrying a conflicting 400-row churn of the same ungated columns.

**AND THE MEASUREMENT IS ITSELF A FINDING** -- see RESIDUAL item 10.

---

## 9.6 THE FULL-SUITE GATE, AND THE ONE RED I CAUSED AND DID NOT PAPER OVER

`scripts/impact_gate.py` widened to the full suite -- impact set 172 of 209
test files (82%), above its 45% line -- so the data-change blind spot the brief
warns about (name-based coupling returning an empty set for `.md`/`.tsv`) does
not apply: everything ran.

    6 failed, 7967 passed, 8 skipped, 1 xfailed in 1941.29s (0:32:21)

**ALL SIX WERE DIAGNOSED. FIVE ARE RESOLVED; ONE IS REAL, IS MINE, AND IS
REPORTED RATHER THAN SILENCED.**

**TWO WERE MINE AND ARE FIXED.**

1. `test_an_asserted_name_resolves::test_no_new_asserted_name_is_absent` --
   my `N 179` cell wrote *"under `EXCLUDED-RULED-ADMISSION`"*, and the
   checker's `_SLOT_BEFORE` treats the word **under** as a BLOCKER slot. That
   name is a RULING id, not a blocker, so it resolved nowhere and the guard
   reported it as *"a plausible wrong answer"* -- precisely the defect class
   it was built for, catching me. Rephrased to *"The ruling
   `EXCLUDED-RULED-ADMISSION` admits that state on four grounds only"*, which
   is also the more accurate sentence. **9 passed.**

2. `test_a_correction_is_findable_from_the_claim::test_every_candidate_pair_is_declared_or_triaged`
   -- three untriaged candidate pairs. Two are the documented SHADOW shape:
   this document declares `CORRECTS:` against both slices and both slices
   carry the matching `CORRECTED BY:`, and the proximity scan additionally
   sees the reverse arrow, because a markdown table has no blank lines so a
   row's own re-priced prose sits inside the citation's two-line window. The
   third is not a shadow at all: my in-place correction of `N 194`'s blocker
   line landed within two lines of that row's PRE-EXISTING citation of the
   hashtag evidence document, which the row AGREES with and withdraws nothing
   from. All three are declared on `NOT_A_CORRECTION` with reasons and with
   the *"what would make this entry wrong"* clause the file requires -- and
   that file checks its own entries, so those claims were verified, not
   merely asserted. **13 passed.**

**THREE WERE ENVIRONMENTAL, and re-run green on a quiet box.**
`test_stale_process_is_announced` (two tests) and `test_typeahead_gate` (one).
The first inspects RUNNING PROCESSES; during the gate run this machine carried
**five concurrent `impact_gate` runs and 48 xdist workers** from sibling
waves. Re-run afterwards: **31 passed.**

**ONE IS REAL AND IT IS MINE.**
`test_the_blocker_reason_locator_states_its_recall::test_recall_against_a_hand_built_set_does_not_regress`

    5 of 9 hand-found documents are in the top 3, below the floor of 7

**MEASURED BY BISECTION RATHER THAN ARGUED**, restoring pieces one at a time:

| tree | result |
|---|---|
| corpus at `HEAD~1` (master) | **PASSES** |
| + my census edits, my document ABSENT | 6 of 9 -- fails |
| + my census edits + my document | 5 of 9 -- fails |

**So both halves cost one displacement each, and the baseline was green. I
caused this.** The mechanism is the one this repository already has a scar
for: a new document that is genuinely a strong reason for
`SEARCH-RESULTS-SURFACE` pushes the hand-found documents out of the top 3, so
CORPUS GROWTH READS AS A RECALL REGRESSION. The existing repair
(*"on a tie the EARLIER document wins"*) handles TIES; this is not a tie --
the new material scores higher on merit.

**I DID NOT LOWER THE FLOOR, AND I WILL NOT.** A wave that weakens a guard to
make its own commit green is the exact move this repository removes checks
for, and the fix is not mine to choose: the locator and its hand-built recall
fixture are not search artifacts. RESIDUAL item 3 states the options.

---

## 10. THE 704, BEFORE AND AFTER

    venv/Scripts/python scripts/count_census_states.py

**BEFORE** and **AFTER** are identical:

```
  COVERED-CANNOT-DELIVER       19
  COVERED-PROVEN               52
  COVERED-UNFIRED              19
  CP                           20
  CU                            4
  EXCLUDED-RULED              285
  GAP                         275
  MEASURED-ABSENT               7
  XR                           23
  stated rows                 704
```

Per slice, also identical: `jobs 150/56`, `profile 203/55`,
`messaging-and-content 142/77`, `network 209/87`. `reader_closable_blockers.py`
re-run after every edit: all four controls pass and
`SEARCH-RESULTS-SURFACE` still reads `20 GAP / 19 reader-reachable`.

**I am not arguing for a different number.** Eleven cells gained evidence and
none gained or lost a state, which is the outcome the invariant is there to
protect.

---

## 11. RESIDUAL

**Things this wave found and did not do, each with who should do it.**

1. **`writes.aim_invitation` repeats the leak defect, docstring and all.**
   LATENT, two production callers, both pre-coercing. Not a search file, so
   not mine. **The durable fix is not the third local repair** -- it is
   extending `leakwalk`'s subject set beyond "async def with a page
   parameter" to page-less shapers, which would have caught all four at once.
   `chart_labels.is_readable` and `intro_fields.is_answerable` are the other
   two.

2. **`P L2b` is GAP, reader-reachable, and in no blocker at all.** Control 4's
   unjoined row. Profile slice. No blocker-scheduled wave can ever reach it.

3. **I LEFT ONE RED AND IT IS THE FIRST THING TO LOOK AT.**
   `test_the_blocker_reason_locator_states_its_recall::test_recall_against_a_hand_built_set_does_not_regress`
   is GREEN at `HEAD~1` and RED at my commit, 5 of 9 against a floor of 7,
   bisected in section 9.6: my census edits cost one displacement and this
   document costs a second. **Nothing is broken** -- the locator still finds
   every hand-found document, it just ranks newer, more specific material
   above them, which is the corpus-growth-reads-as-regression shape the tie
   rule already half-addresses.

   **THREE OPTIONS, and the choice belongs to whoever owns the locator:**
   (a) accept that a document named for a blocker outranks older ones and
   refresh the hand-built set -- honest, but it re-baselines recall every
   time a wave writes a good document; (b) make the floor a RATIO over the
   corpus size rather than an absolute 7, so growth does not eat it;
   (c) rank on something less filename-sensitive, since this document's
   filename contains the blocker's name almost verbatim, which is a large
   part of why it scores where it does.

   **A FOURTH OPTION EXISTS AND IT DOES NOT WORK, WHICH IS WORTH KNOWING
   BEFORE SOMEBODY TRIES IT.** The test's own convention is a by-hand
   adjudication of `HAND_FOUND` -- its third entry for this blocker was added
   by hand on 2026-09-21 -- so the obvious move is to add THIS document to
   `HAND_FOUND["SEARCH-RESULTS-SURFACE"]`. It is circular (a wave entering
   its own deliverable into the fixture that judges it) and, separately, it
   is **arithmetically insufficient**: the set is 9 documents and 5 are in
   the top 3, so adding a tenth that ranks well gives 6 of 10 against a floor
   of 7. It still fails. If a hand-adjudicated set cannot clear the floor,
   that is evidence about the RANKER, not about the fixture.

   **I did not pick one, and I did not lower the floor.** My brief scopes me
   to search rows, and choosing here would mean editing a guard's expectation
   to make my own commit pass.

4. **The shape reading is UNFIRED.** It is committed as an instrument with no
   live reading behind it, which is the honest state. Section 7.1 has the
   exact reading. **One browser slot closes up to four rows** (`N 81`, `N 88`,
   `N 89`, and the control half of `N 80`) if the zeros come back zero.

5. **Fourteen rows are blocked on decisions, not on readers**, and the reader-
   closable count cannot see that. Bucket A (4 rows) waits on one parameter
   ruling; bucket B (3 rows) waits on address DECIDEs; bucket C (7-8 rows) is
   terminally press-refused. **If the parameter ruling alone were made, four
   rows would become buildable in one wave.** That is the highest-leverage
   single decision on this surface.

6. **`N 82`'s real blocker is selector SCOPE, and nobody owns it.** Telling a
   filter pill from a jobs-side badge needs either a scoped selector or a
   label read, and the label read is forbidden here. The shape reading does
   not solve it.

7. **`tests/test_search_results.py` pins a signature the docstring says is
   insufficient.** It is not wrong, but it reads as coverage of a property it
   does not cover. Worth a comment pointing at the behavioural test.

8. **WHAT A BEHAVIOURAL-CLAIM GUARD WOULD HAVE TO LOOK LIKE** -- asked of me
   by a lead note at this worktree root, which independently verified the
   `tally` defect and named it the THIRD instance this session of one class:
   *prose asserting a safety property the adjacent code does not have.*
   `tests/test_prose_that_makes_a_claim.py` polices derivable COUNTS and
   MEMBERSHIP; a claim about behaviour is not a number, so nothing reads it.
   **My view, from the one instance I just repaired:**

   **(a) Do not try to parse the claim. Parse the SUBJECT out of it.** What
   made `tally` findable was not the English -- it was that the docstring
   named its own parameters (*"Its parameters are INTEGERS"*) and the
   parameters are enumerable. A guard that extracts *which named things a
   docstring makes a claim about* and then drives THOSE is tractable; a guard
   that tries to decide what "cannot be handed a needle" means is not.

   **(b) The claim should nominate its own test, and the guard should check
   the nomination resolves.** Cheap, mechanical, and it inverts the burden:
   the author who writes a behavioural claim names the symbol that holds it,
   and the guard fails when that symbol does not exist or does not mention
   the subject. This repository already has the precedent in
   `CANONICAL-RULING-ID` -- a citation resolves to a SYMBOL -- and this is
   the same rule pointed at code instead of rulings.

   **(c) The highest-yield version needs no natural language at all.** Every
   one of the four sites in section 3.7 is findable by the AST census I
   already ran: a function that coerces one of its own parameters without
   going through `coerce`. **That census is the guard**, and it would have
   caught all four with no prose reading whatsoever. A docstring-claim guard
   is the general case; the coercion census is the 80 per cent, available
   today, and I would build it first.

   **(d) The trap to design around.** Such a guard's subject set is exactly
   what `leakwalk`'s was -- and `leakwalk` was *correct and complete for what
   it enumerated* while this defect sat one layer outside it. So whatever the
   guard enumerates, **it must print what it did NOT read**, or it becomes
   the next piece of prose asserting a property nothing checks.

9. **A FOURTH INSTANCE OF THE SAME CLASS, FOUND WHILE CHECKING MY OWN WORK
   AGAINST THE STRICT-ASCII RULE -- and it is the cleanest specimen yet.**
   `tests/test_the_rulings_register_is_ascii` reads exactly one file,
   `_audit/RULINGS.md`. Its docstring says:

   > "Strict ASCII, like every other generated file here."

   **Nothing checks "every other generated file here."** Measured across the
   four census slices: `_audit/_census/network.md` carries **four** non-ASCII
   lines (U+2014 at three, U+2192 at one), in the delta prose around lines
   103-130; the other three slices are clean. My own 245 added lines are
   ASCII, verified.

   **I did not fix them.** They are not in a search row, they sit in prose a
   recent wave wrote, and my brief says to name what another wave owns rather
   than change it. **The point is not the four characters.** It is that this
   is the same shape as the `tally` defect one more time: a guard that is
   correct and complete for what it enumerates, a sentence claiming a wider
   subject, and the gap between them invisible because the guard is green.
   **That makes three instances named by the lead note plus this one, in four
   different files, in one session** -- which is the strongest argument for
   item 7 being worth building.

10. **A FIFTH INSTANCE, AND THE BIGGEST BY ROW COUNT.**
    `test_the_committed_map_still_matches_what_the_evidence_derives` is named
    for a property it does not check. Its assertion message says:

    > "N rows in the committed map no longer match what the evidence derives
    > [...] The map is a DERIVED artifact"

    **It compares three of ten columns.** 403 rows currently differ from what
    a fresh build derives, in `reason_doc` and `state_today`, and the test is
    green -- correctly, because those columns are outside its subject.
    **Measured this wave and left alone**, because the map is not a search
    artifact and widening that test would fail it immediately on 403 rows of
    other waves' work, which is not a thing to drop on a serial merge.

    **The honest repair is not to widen the comparison.** It is to make the
    test PRINT WHAT IT DID NOT COMPARE -- the same discipline the impact gate
    already applies to itself when it names the tests it did not run. A
    derived-file guard that silently checks 30 per cent of the columns is the
    same defect as a docstring claiming a behaviour, one layer up, and it is
    the fifth instance of that class this session.

11. **Not checked by me:** whether `decorated` should eventually be published
   on the tool envelope. I deliberately did not change `server.py`'s payload,
   because that changes a tool's contract on an admitted surface and the
   instrument is complete without it -- a probe can call `read_filters`
   directly, which is how the live reading would be taken anyway.
