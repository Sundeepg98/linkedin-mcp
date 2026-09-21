# THE UNGRANTABLE READERS: what `GRANT_REFUSAL` was actually refusing

**Subject:** the `not_driven:` block of `tests/reader_leak_baseline.json`, and
specifically the claim that five `writes:` readers are unreachable by the
offline harness because minting a write grant is *"policy, not capability"*.

**HEADLINE: the refusal was plumbing, and it was hiding a live leak.** Four of
the five readers hold no door at all -- no click, no fill, no `goto`, no
`consume`, no `writes_enabled` -- and the grant reaches them as two strings.
Driving them with a grant that refuses everything turned one of them RED
immediately: `writes._recipient_gate` put a page-chosen value into
`ValueError: invalid literal for int() with base 10: '<it>'`, forty lines below
its own docstring's promise not to print that value "because it is somebody's
name and this server does not read one to explain itself".

**WHAT THIS WAVE RETIRED:** the `GRANT_REFUSAL` constant in
`tests/test_readers_emit_no_page_string.py`. Its stated ground ("policy, not
capability") is answered by three measurements in section 4, including the
repository's own `tests/test_writes.py::_bare_grant`, which has built these
objects all along and documents why that is not a way round `mint`. This is a
change to SOURCE, not a claim about another audit document, so it carries no
`CORRECTS:` marker -- those name documents in this corpus and nothing else.

**Read-only wave.** Nothing here connected to LinkedIn, launched a browser or
touched the network; `LINKEDIN_ENABLE_WRITES` was never set and
`writes.writes_enabled()` reads `False` at the end of every script below.

---

## 1. THE DENOMINATOR, DERIVED

Counted off `tests/reader_leak_baseline.json` at the branch point (`f729a2a`)
by loading the JSON and grouping on the exact reason string.

| verdict class | count |
| --- | --- |
| `clean` | 58 |
| `returns_text` | 40 |
| `not_driven:<reason>` | **21** |
| **total discovered readers** | **119** |

The 21, grouped by reason -- this is the only denominator that counts:

| n | reason | readers |
| --- | --- | --- |
| 9 | `raises BrowserUnavailableError` | `auth:_cookie_records`, `auth:_cookies`, `auth:check_auth`, `auth:login_via_browser`, `auth:require_auth`, `auth:session_info`, `server:_establish_self_owned_editor`, `server:_goto_self_profile_asserted`, `server:_resolve_own_item_permalink` |
| 5 | `needs grant: WriteGrant -- this harness does not mint write grants (policy, not capability; see GRANT_REFUSAL)` | `writes:_live_control`, `writes:_recipient_gate`, `writes:_typeahead_gate`, `writes:_verify_after`, `writes:perform` |
| 4 | `raises WriteAttemptError` | `writes:_load`, `writes:_read_posting_facts`, `writes:observe`, `writes:preview` |
| 1 | `raises ValueError` | `dom:activate_messaging_filter` |
| 1 | `raises ExtractionFailedError` | `dom:read_unfollow_control` |
| 1 | `needs observation: Observation` | `writes:_name_the_invitation_recipient` |

**The `writes:` slice is 10, not 5.** The brief names the grant block and the
observation; the four `raises WriteAttemptError` rows are `writes:` readers too
and are adjudicated here on the same terms. The other 11 (`auth:`, `dom:`,
`server:`) are outside this wave and are named in section 7.

### 1.1 WHAT THE REFUSAL WAS COSTING, in the repository's own units

`scripts/_census_page_coercions.py` -- shipped, not written here -- enumerates
every coercion site in `linkedin_server/` and buckets it. Its hazard bucket is
**52 unguarded page-derived sites**, and it closes by naming the guard that
settles which of them actually leak:

> A STATIC BUCKET IS A HYPOTHESIS. Which of these actually leak is settled by
> driving the real readers: `tests/test_readers_emit_no_page_string.py`

That guard could not drive five of the functions holding them:

| reader | hazard sites |
| --- | --- |
| `_live_control` | 12 |
| `_verify_after` | 4 |
| `_recipient_gate` | 2 |
| `_typeahead_gate` | 2 |
| `_name_the_invitation_recipient` | 2 |
| **total** | **22 of 52 (42 per cent)** |

**Forty-two per cent of this repository's own hazard bucket was referred to a
guard whose harness refused to run it.**

---

## 2. THE (a)/(b)/(c) VERDICT PER `writes:` READER

The question per the brief: *does reaching its page-reading code require a
write to actually happen?*

The evidence is an AST walk of `linkedin_server/writes.py` asking two things
per function -- does it call any page ACTION (`click`, `fill`, `press`, `type`,
`set_input_files`, `select_option`, `goto`, `close`), and does it call any
grant DOOR (`consume`, `mint`, `assert_write_url`, `discard_all`,
`writes_enabled`).

| reader | page actions | grant doors | what it does with the grant | verdict |
| --- | --- | --- | --- | --- |
| `_live_control` | **NONE** | **NONE** | `grant.target` only (9 reads) | **(a)** |
| `_verify_after` | **NONE** | **NONE** | `grant.target` only (5 reads) | **(a)** |
| `_typeahead_gate` | **NONE** | **NONE** | `grant.action`, `grant.target` (1 line) | **(a)** |
| `_recipient_gate` | **NONE** | **NONE** | `grant.action`, `grant.target` (1 line) | **(a)** |
| `_name_the_invitation_recipient` | **NONE** | **NONE** | `observation.target`, `observation.facts` | **(b)** |
| `perform` | `click` 8720, `fill` 8748, `set_input_files` 8678, `select_option` 8691 | `writes_enabled` 8320, `assert_write_url` 8403 | consumed-state, target, preview | **(c)** |
| `_read_posting_facts` | NONE | NONE | takes no grant | **(a)**, and it RAN |
| `_load` | `goto`, through the navigator | NONE | takes no grant | **(a)**, ceiling is navigation |
| `observe` | `goto`, in every branch | `writes_enabled` 4126 | takes no grant | **(d)** -- see 2.2 |
| `preview` | via `observe` | `mint` 4772 | mints one | **(d)** -- see 2.2 |

**Of the five readers the grant block fenced off, `perform` is the only one
that touches the page or a door** -- and the walk that says so covers EVERY
function in `writes.py`, not a chosen list, because a claim of the form "only
X does this" is only worth the denominator it was taken over:

```
PAGE ACTIONS   perform  click 8756, fill 8784, set_input_files 8714, select_option 8727
               _load    navigator.goto 3079
GRANT DOORS    consume, mint, observe, perform   writes_enabled
               perform                           assert_write_url
               preview                           mint
```

`_live_control`, `_verify_after`, `_typeahead_gate` and `_recipient_gate` hold
neither. They were refused for standing next to the one function that does.

### 2.1 The exact grant reads, so "data carrier" is not a characterisation

```
_live_control       6273 6432 6705 6761 6767 6778 6794 6796 6838   grant.target
_verify_after       7010 7066 7181 7246 7284                       grant.target
_typeahead_gate     7656   needle = _subject_component_of(spec_for_action(grant.action), grant.target)
_recipient_gate     7886   needle = _subject_component_of(spec_for_action(grant.action), grant.target)
```

Every one is an attribute read of a string. No branch of any of the four asks
whether the grant is valid, live, unconsumed or minted. **The grant check is a
property of the CALL SITE.** `perform` holds it, at line 8320 and again at
8328, before it calls any of them.

### 2.2 `observe` and `preview` are a fourth class, and their refusal is REAL

Neither is (a), (b) or (c). `observe`'s FIRST statement is
`if not writes_enabled(): raise` -- a process-wide flag read from the
environment, which no object can satisfy and which this wave may not set.
`preview` calls `observe` at 4761 before anything else.

That would be a thin finding if the flag were the only obstacle, so it was
measured rather than assumed. With `writes.writes_enabled` replaced in memory
(never the environment variable), `observe` was driven for **all 13 sanctioned
specs against the planted page**:

```
   apply_job              observe NAVIGATES (page.goto)
   comment_on_item        observe NAVIGATES (page.goto)
   follow_company         observe NAVIGATES (page.goto)
   publish_post           observe NAVIGATES (page.goto)
   react_to_item          observe NAVIGATES (page.goto)
   save_job               observe NAVIGATES (page.goto)
   send_invitation        observe NAVIGATES (page.goto)
   send_message           observe NAVIGATES (page.goto)
   set_open_to_work       observe NAVIGATES (page.goto)
   unfollow_company       observe NAVIGATES (page.goto)
   unsave_job             observe NAVIGATES (page.goto)
   update_profile_field   observe NAVIGATES (page.goto)
   update_setting         observe NAVIGATES (page.goto)
   writes_enabled() back to: False
```

**Thirteen of thirteen. Lifting the flag would not drive `observe`, because
every branch loads a page.** These two stay NOT-DRIVEN and that is a correct
ceiling for an offline harness, not a gap. Nothing was manufactured for them.

### 2.3 `_read_posting_facts` was already being driven, and the baseline said otherwise

It takes no grant. Driven, it reads the planted page through
`dom.read_job_posting`, finds no title, description or company, and raises its
own `WriteAttemptError` -- a refusal it reached by looking. The harness walked
that exception for the plant and found none.

`not_driven:raises WriteAttemptError` is therefore two different facts wearing
one string: *"the harness could not reach it"* and *"it ran and refused"*. This
wave does not change the guard's verdict vocabulary -- that touches all 16
remaining rows and wants its own decision -- but the conflation is named in
section 7.

---

## 3. WHAT WAS BUILT, AND WHY IT AUTHORISES NOTHING

`tests/refusinggrant.py` (new). It supplies three things, each derived from the
server's own data rather than invented:

* **`grant_for(spec)`** -- a `RefusingGrant` carrying that spec's own action
  and a synthetic target normalised by `writes._target_for`, the same
  normaliser `mint` and `consume` use.
* **`anchor_for(spec)`** -- the control label `perform` would compute, via the
  shipped `writes.anchor_label_for`.
* **`observation_for(page, spec)`** -- an `Observation` whose `facts` come from
  running the spec's OWN surface reader (`writes._SURFACE_READS` /
  `_PERMALINK_READS`) over the planted page, which is what `observe` does minus
  the page load.

**FOUR INDEPENDENT REFUSALS** make the grant refusing rather than merely
unused, so that losing any one still leaves it unable to authorise anything:

1. `token` is the empty string -- `consume` refuses that by name before any
   lookup;
2. it is never inserted into `writes._GRANTS`, so no lookup can find it;
3. `expired()` always answers `True` and `age()` always answers infinity;
4. `consumed` stays `False`, which is the state `perform` refuses at its third
   statement, before it touches the page.

The `Observation` is inert **by the server's own claim, not this module's**:

> An Observation a caller builds by hand is INERT: it is redeemable only while
> its `receipt` is live in `_OBSERVED`, and the only function that puts one
> there is `observe`, which loads pages.

Its `receipt` is the empty string.

**PAIRED WITH THE SPEC, NEVER VARIED AGAINST IT.** A grant is permission for
ONE action, so a `save_job` grant handed to `follow_company`'s reader is a
state the server cannot be in, and a verdict taken there would be about a
branch nobody wrote -- the argument `_domain_values` already makes for driving
every shipped `WriteSpec`. It is also the difference between 13 variants and
13 x 13 x 13, since `_verify_after` takes a spec, a grant AND an observation.

---

## 4. THE THREE MEASUREMENTS THAT RETIRE `GRANT_REFUSAL`

1. **The four gates hold no door.** Section 2's AST walk: zero page actions and
   zero grant doors in `_live_control`, `_verify_after`, `_typeahead_gate`,
   `_recipient_gate`. `perform` holds all of them.
2. **The test tree already builds grants.** `writes.WriteGrant(...)` is
   constructed at 9 sites across 5 test files, and inserted into
   `writes._GRANTS` at 6 more in `tests/test_writes_nine.py`.
   `tests/test_writes.py::_bare_grant` is the shipped helper, and its docstring
   answers the objection in advance:

   > A grant object built directly, for the tests about the URL DOOR and the
   > refusal in `perform` rather than about minting. **Deliberately not a way
   > round `mint`.**

   One file's local refusal is not a repository ruling when the write-boundary
   suite settled the same question the other way and wrote down why.
3. **The server declares a hand-built `Observation` inert**, quoted in section
   3.

`GRANT_REFUSAL` named itself as the citation for its own claim
(*"see GRANT_REFUSAL"*). Nothing outside that constant ever ruled it.

---

## 5. WHAT THE DRIVE CARRIED OUT -- AND THE LEAK

### 5.1 The leak, found the hour the reader could first be driven

```
FAILED tests/test_readers_emit_no_page_string.py::test_no_reader_carries_a_page_string_out[writes:_recipient_gate]
E       AssertionError: writes:_recipient_gate carried the planted page string
        out of the process: ValueError carries it at $(str). An exception is not
        a return value -- coerce through a helper that never raises and never
        quotes its input: linkedin_server.coerce.as_count / as_int / counts_only.
E       assert 'leaks' != 'leaks'
```

The exception itself, with the plant (synthetic, from `tests/plantedpage.py`):

```
TYPE : ValueError
STR  : invalid literal for int() with base 10: 'Exampleperson Markersurname'
ARGS : ("invalid literal for int() with base 10: 'Exampleperson Markersurname'",)
WALK : ['$(str)', '$(repr)', '$.args[0]']
```

The site, `writes.py` 7913-7914 as it shipped:

```python
total = int(reading.get("total") or 0)
matches = int(reading.get("matches") or 0)
```

**WHY THIS ONE AND NOT ITS TWIN.** `_typeahead_gate` holds two lines that are
character-for-character the same shape and does NOT leak. They are not the same
hazard:

* `_typeahead_gate` reads `dom.read_typeahead_options`, whose `total` and
  `matches` are `await page.locator(...).count()` -- **Playwright-typed**. A
  document cannot make a `count()` answer with a string.
* `_recipient_gate` reads `dom.read_selected_recipients`, which is
  `dict(await page.evaluate(...))` returned unshaped -- **page-controlled**.
  Whatever that document's JavaScript returns arrives at the `int()`.

That is `tests/plantedpage.py`'s own fidelity rule holding up under a third
independent test, and it is why the harness could convict one twin and clear
the other rather than painting both red.

**WHERE IT WENT.** The `try` in `_recipient_gate` wraps only the read, so the
`ValueError` escapes the function, leaves `perform`, and is rendered by
`server._error` through `config.scrub` -- which substitutes this server's own
paths and nothing else, because a name has no shape to scrub. The value being
coerced is a recipient chip's accessible name on `send_message`, the action
this package's own spec calls the most irreversible in audience. Forty lines
below the leak, the same function refuses to print that label:

> Refused, and the label is not reported here, because it is somebody's name
> and this server does not read one to explain itself.

**THE REPAIR** is the one the guard's own failure message prescribes:
`coerce.as_count`, which answers identically on every value
`SELECTED_RECIPIENT_JS` can produce (`total: seen.length`, `matches: matches`
are JS numbers) and substitutes a LOGGED zero on anything else. A zero total
refuses, which is the direction this gate already fails in.

### 5.2 Verdicts after the repair

| reader | was | now | what it carried |
| --- | --- | --- | --- |
| `writes:_live_control` | `not_driven:needs grant` | `returns_text` | control labels it reads back into its own `why` -- contract, shapers govern |
| `writes:_verify_after` | `not_driven:needs grant` | `returns_text` | same |
| `writes:_recipient_gate` | `not_driven:needs grant` | `returns_text` | the page's `per_selector` payload in `observed` -- contract |
| `writes:_typeahead_gate` | `not_driven:needs grant` | `clean` | nothing |
| `writes:_name_the_invitation_recipient` | `not_driven:needs observation` | `clean` | nothing |
| `writes:perform` | `not_driven:needs grant` | `not_driven:raises WriteAttemptError` | reason corrected -- the real door is the flag |
| `writes:_load` | `not_driven:raises WriteAttemptError` | `not_driven:navigates (page.goto)` | reason corrected -- see 5.4 |

### 5.3 How much of the hazard bucket is now MEASURED

Line-level, with a tracer over `linkedin_server/writes.py` while the guard
drives the five readers -- not inferred from the verdict:

* 22 hazard sites at the branch point;
* 2 of them are the repaired lines, and they executed -- that is how the leak
  was found;
* of the 20 that remain, **15 execute** under the drive.

**17 of 22 executed. Five did not, and they are named in section 7** rather
than counted as covered.

### 5.4 `_load`'s reason was describing the harness

`writes._load` was recorded `not_driven:raises WriteAttemptError`, which reads
as the write module refusing. It was not: the harness passes its generic
synthetic string for a `str` parameter, and `readonly.assert_read_url` refuses
that before `_load` runs a line of its own. Given the server's own `FEED_URL`
it reaches its true ceiling -- it navigates. Blast radius of the rule that
fixes this is exactly one reader; `_load` is the only discovered reader with a
`url` parameter.

---

## 6. THE CONTROLS, SHOWN FAILING

`scripts/_check_the_refusing_grant_can_fail.py`. Every section prints its own
red and its own green. Full run, with the logger's substitution warnings
stripped:

```
1. THE FOUR REFUSALS

  the refusing grant:
      (none -- this object carries all four refusals)

  a grant holding a non-empty token
      CONVICTED: token: it is not empty, so consume() would look it up
      CONVICTED: expired: expired() answers False, so a TTL check admits it
  a grant present in writes._GRANTS
      CONVICTED: token: it is not empty, so consume() would look it up
      CONVICTED: unregistered: it IS in writes._GRANTS, so a lookup finds it
  a grant whose TTL has not run out
      CONVICTED: expired: expired() answers False, so a TTL check admits it
  a grant already marked consumed
      CONVICTED: unconsumed: consumed is True, the state perform acts from

  PASS: all four refusals convict an object that lacks them, and
        the supplied grant carries every one.

2. THE DOORS, WITH THE PROCESS FLAG NEUTRALISED IN MEMORY

  CONTROL: consume() ADMITTED a registered, fresh grant --
           so a refusal below is about the object, not the door.

  REFUSED: consume() -- no confirm token. A write performs nothing until it is
           handed the token from its own preview -- a boolean cannot stand in,
           because a boolean can be set by a caller that never saw a preview.
  REFUSED: perform() -- this grant has not been redeemed. A write is performed
           against a grant that consume() has already burned, so the token
           checks -- single use, this action, this target, not expired -- have
           provably run. perform does not redeem its own permission.

  PASS: both doors refused the grant for ITS OWN reasons, with the
        process flag neutralised; LINKEDIN_ENABLE_WRITES was never set,
        and writes_enabled() reads False again.

3. THE LEAK, PLANTED BY RESTORING THE COERCION THAT SHIPPED

  before the plant: writes:_recipient_gate -> returns_text
  under the plant : writes:_recipient_gate -> leaks
  after restoring : writes:_recipient_gate -> returns_text

  PASS: the guard goes RED on the exact line this wave replaced and
        clears on its repair.

4. THE DERIVED ANCHOR

  DIFFERS  save_job: derived=read the page  generic=raises ExtractionFailedError
  DIFFERS  unsave_job: derived=read the page  generic=raises ExtractionFailedError

  PASS: 2 of 13 actions reach
        their readings only with the anchor the server derives.

5. THE READ URL

  with the generic synthetic string : raises WriteAttemptError
  with the server's own FEED_URL    : navigates (page.goto)

  PASS: the generic string was refused by the READ DOOR before the
        reader ran, which the baseline recorded as the write module
        refusing. The shipped address reaches the real ceiling.

======================================================================
PASS: all 5 sections went red on a defect and green on its absence.
```

**Section 2 is the one worth arguing about, so its limits are stated rather
than implied.** "This grant refuses" is trivially true in a process where the
flag is off, and a control that only ever runs behind the closed door proves
the DOOR. So that section replaces `writes.writes_enabled` **in memory**, runs
the two doors, and asserts afterwards that the environment variable was never
set and that `writes_enabled()` reads `False` again. Nothing in it can act: the
page handed to `perform` is `tests.plantedpage.PlantedPage`, whose `goto`,
`click` and `fill` raise, and the section counts a reached browser call as a
FAILURE rather than a pass. Its control half -- `consume()` admitting a
registered, fresh grant -- is what makes the two refusals below it about the
object rather than about the door.

**Section 3's plant is not an invented mutation.** It restores
`int(value or 0)` by rebinding `coerce.as_count`, which is the line that
shipped until this wave; `writes.py` reaches the helper through the module, so
the rebind lands at the call site. No other reader went red under it.

---

## 6.2 THE SCRIPT IS NOT A RUNNER, SO THE PROPERTY IS ALSO A TEST

A control that lives only in `scripts/` is executed by nobody. If a later edit
weakened `RefusingGrant` -- a live timestamp, a real token, `consumed=True` --
every section above would still pass in its own script and the suite would be
green while the harness handed `writes.perform` an object one step from being
permission.

So `tests/test_the_harness_grant_cannot_authorise_a_write.py` asserts the
property where the suite reaches it: the four refusals hold for all 13
sanctioned actions, building grants registers nothing in `writes._GRANTS`,
building observations mints no receipt in `writes._OBSERVED`, and neither
harness module names the writes flag or rebinds `writes_enabled`.

**BOTH HALVES SHOWN FAILING**, by mutation, without editing a tracked file (a
pytest plugin loaded with `-p` from a scratch directory):

`refusal_failures` stubbed to return `[]` -- the in-file control goes red:

```
E       AssertionError: refusal_failures() convicted nothing on a grant holding
        a live timestamp and a token, so it cannot fail and its empty list
        above certifies nothing.
E       assert []
1 failed, 16 passed
```

`grant_for` replaced with a plain `WriteGrant` carrying a live timestamp and a
token-shaped string -- every action's assertion goes red:

```
FAILED ...::test_every_supplied_grant_carries_all_four_refusals[apply_job]
FAILED ...::test_every_supplied_grant_carries_all_four_refusals[comment_on_item]
   ... 11 more, one per sanctioned action ...
13 failed, 4 passed
```

---

## 6.1 THE IDENTITY GATE CONVICTED THIS WAVE'S OWN FIXTURE

Worth recording because it is the guard working on the author rather than on
somebody else. The first version of `SYNTHETIC_RAW_TARGETS` addressed the two
item-shaped kinds with a LinkedIn activity urn, on the reasoning that a target
should look like the thing it stands for. Two independent guards refused it:

```
FAILED tests/test_no_committed_identity.py::test_no_tracked_file_carries_a_real_identifier[tests/refusinggrant.py]
E   AssertionError: tests/refusinggrant.py: 2 unallowed urn id hit(s), 0 declared.

FAILED tests/test_no_committed_identity.py::test_the_exact_value_sweep_actually_runs
E   the exact-value sweep found 1 hit(s) in tracked files:
E     HIT tests/refusinggrant.py:82 [withdrawn_identifiers]
```

A red on that gate means UNDECLARED, never "this is real" -- so the question
was whether the urn shape was needed at all. It was not: `item_urn` is in
`writes._OPAQUE_TARGET_KINDS`, which accepts any string, and the readers treat
it as opaque. The placeholders are now `example-harness-item`, and the verdict
table above is unchanged by the swap (re-measured: 0 readers changed). **A
shape-valid literal is required when the SHAPE is what the code reads; here it
was not, and an unmistakable placeholder is strictly better** -- which is the
sentence `tests/test_a_person_name_is_never_a_literal.py` already carries.

---

## 7. RESIDUAL -- what this wave did NOT reach, and why

**16 readers remain NOT-DRIVEN** (was 21):

| n | reason | readers |
| --- | --- | --- |
| 9 | `raises BrowserUnavailableError` | the `auth:` six and the `server:` three. **Untouched by this wave and not adjudicated.** They need a browser or a session store, which is a different instrument from a planted page. |
| 4 | `raises WriteAttemptError` | `writes:_read_posting_facts` (ran and refused -- see 2.3), `writes:observe` and `writes:preview` (the process flag, and 13 of 13 branches navigate anyway -- see 2.2), `writes:perform` (the flag first, the unconsumed grant second) |
| 1 | `navigates (page.goto)` | `writes:_load` -- the honest ceiling |
| 1 | `raises ValueError` | `dom:activate_messaging_filter` -- not examined |
| 1 | `raises ExtractionFailedError` | `dom:read_unfollow_control` -- not examined |

**Five hazard coercion sites are inside driven readers but never execute** on
the planted page. Reachable by the guard; not exercised by it:

```
  4857  if int(reading.get("matches") or 0) != 1:          # _name_the_invitation_recipient
  6591  if int(send.get("textboxes") or 0) != 1:           # _live_control
  6601  if int(send.get("controls") or 0) != 1:            # _live_control
  7070  controls = int(reading.get("controls") or 0)       # _verify_after, dark mode
  7071  off = int(reading.get("off_state") or 0)           # _verify_after, dark mode
```

`7070`/`7071` sit on `update_setting`'s verification path, which navigates on
this page. `4857` is unreachable behind the rail described next.

**`_name_the_invitation_recipient`'s naming branch is not reached, measured
rather than assumed:**

```
   observation.facts        : {'controls': 0, 'matches': 0, 'index': 0}
   reading (reveal=True)    : {'controls': 0, 'matches': 0, 'index': 0, 'label': None}
   rail: reading.controls=0  vs  facts.controls-or-minus-one=-1  -> EARLY RETURN
   matches == 1 ?           : False
   returned                 : {'seed': 1}
```

The planted page's control count reaches the reader as `0` (the `dom` layer's
own `coerce.as_count` substitutes it for a `PageString`), and the rail spells
its absent-default `or -1`, so a real `0` can never equal a recorded `0`. The
`matches != 1` guard would bail regardless, so nothing turns on it here -- this
is recorded as a measurement, not as a defect claim. **The branch that prints a
person's name is therefore driven up to its rail and no further, and that is
the one part of this reader a future wave still owes a measurement on.** What
IS now driven: `dom.read_invitation_surface(..., reveal_single_match=True)`,
which nothing else in the guard reaches.

**The `bool` optional gap, named and measured empty.** `_argument_for` answers
every `bool` parameter with `False`, so four flags are never driven `True` --
and all four are the flags that turn identifier emission ON:

```
     dom:harvest_linked_cards              sibling_rows=False
     dom:read_invitation_surface           reveal_single_match=False
     dom:read_self_owned_editor_fields     include_dom_id=False
     item_addresses:read_item_addresses    include_identifiers=False
```

Driven with `True` through the harness's own argument builder, all four come
back **clean**. The gap is real, it is currently EMPTY at this tree, and
closing it is a one-line change whose value is protecting a future edit -- left
for a wave that can absorb whatever it convicts, rather than folded in here.

**`dom.read_selected_recipients` still claims more than it delivers.** Its
docstring opens *"RETURNS INTEGERS AND NOTHING ELSE"*; it returns
`dict(await page.evaluate(...))` unshaped, and the baseline has recorded it
`returns_text` all along. This wave repaired the CONSUMER, which is where the
red was. Shaping the reader itself is the wider fix and it has one production
caller; it is not done here and is not claimed.

**Six of the thirteen observations carry empty facts, and `observe` cannot
produce that.** `refusinggrant.observation_for` builds facts by running the
spec's own surface reader, but only for the specs whose `state_from` is in
`writes._SURFACE_READS` or `_PERMALINK_READS`. The other six --
`apply_job`, `follow_company`, `save_job`, `unsave_job`, `unfollow_company`,
`set_open_to_work` -- have their facts built by a BRANCH of `observe` (one of
them behind `_read_posting_facts`, which refuses on this page, and one behind
a navigator this harness does not have), so they get `facts={}` and a
`state_why` saying so.

Nothing in this wave turns on it: the only reader that consults
`observation.facts` for one of those six is `_verify_after` on the unfollow
branch, reading `total_followed` -- and `{}.get("total_followed")` is `None`,
which is exactly what `_read_followed_state` returns when the Manage-Pages
list renders partially, the state its own docstring says is the normal one. It
is recorded because an argument from fidelity has to name where its fidelity
stops.

**Two `not_driven` meanings still share one string.** `raises <X>` is recorded
both for a reader the harness could not reach and for a reader that ran, looked
and refused (section 2.3). Splitting them touches all 16 remaining rows and
wants its own decision.

---

## 8. THE DELTA

| | before (`f729a2a`) | after |
| --- | --- | --- |
| `clean` | 58 | 60 |
| `returns_text` | 40 | 43 |
| `not_driven` | 21 | 16 |
| `leaks` | 0 recorded, 1 unmeasurable | 0, measured |
| unguarded page-derived coercion sites (census) | 52 | 50 -- the two repaired ones are no longer coercions |
| of those, inside a reader the guard could not drive | 22 | 0 |

Five readers moved from NOT-DRIVEN to a real verdict. Two more kept
NOT-DRIVEN with a corrected reason. One live leak was found and repaired, on
the gate standing between a typed recipient and a message to a named person.

`tests/reader_leak_baseline.json` was regenerated through its own documented
path -- `python -m tests.test_readers_emit_no_page_string --write-baseline` --
and never hand-edited. That path REFUSES to write while any reader leaks, which
is why the repair in section 5.1 had to land before the baseline could move.

### The gate

`python scripts/impact_gate.py` selected **133 test files by impact plus 15
corpus-wide guards = 134 of 208**, then said so and widened:

```
WIDENING TO THE FULL SUITE, because the impact set is 134 of 208 test files
(64%), at or above the 45% line where running everything costs about the same
and answers more.
```

**So there is no un-run remainder to name: it ran all 208 files.** The scoped
set is still worth reading, because it shows how the change reaches the corpus:
`linkedin_server/writes.py` by import, `tests/plantedpage.py` by import,
`tests/reader_leak_baseline.json` by directory sweep, and the new audit document
and script by the corpus-wide sweeps that enumerate the tracked set.

**ONE RED IS LEFT AND IT IS NOT THIS CHANGE'S**, which is a claim with evidence
rather than a dismissal. `tests/test_click_is_not_its_own_evidence.py` failed
in both full-suite runs, with a DIFFERENT member each time:

| run | failing member |
| --- | --- |
| first | `test_the_refusal_says_when_a_matcher_would_have_separated_them`, `test_a_prefixed_listbox_reproduces_the_live_census_signature` |
| second | `test_the_counts_can_differ_so_the_instrument_has_been_shown_to_speak` |

Three facts settle it:

* all three route through that file's `_census` helper, which calls
  **`writes._typeahead_gate`** -- the twin this wave did NOT touch. The
  function this wave changed, `_recipient_gate`, is reached by a different
  test in the same file, and that test passed in both runs;
* the file passes whole in isolation (31 passed, then the three named above
  re-run green);
* the tests drive a real local headless browser under a `_fast_wait`
  monkeypatch that shortens its timeouts, and both full-suite runs happened
  with **9 concurrent pytest processes on the box** from other worktrees
  (measured with `Get-CimInstance Win32_Process`). A shortened wait on a
  saturated box is the classic shape, and a varying failing member is what
  distinguishes it from a defect.

The other failures the first run reported were real and are fixed: an
undeclared urn placeholder (section 6.1), a marker naming a source file rather
than a document in this corpus, and two derived registers that needed
regenerating.

One more is worth reporting because it happened TWICE, the second time to the
sentence describing the first. `test_a_correction_is_findable_from_the_claim`
pairs any citation of a document in this corpus with a deliberately loose
vocabulary within two lines, and demands that the pair be either declared or
triaged. A bullet listing the regenerated registers sat two lines from a word
on that list, so the pair went untriaged -- and the paragraph written here to
explain that then quoted the word beside the same filename and tripped it
again. Both were prose, neither was a correction claim, and the guard was
right to stop a human both times: that is what a loose vocabulary buys, and
the cost of it is exactly two rewordings.

### Files

* `tests/refusinggrant.py` -- new; the refusing grant, the inert observation,
  the derived anchor, and `refusal_failures`.
* `tests/test_readers_emit_no_page_string.py` -- `GRANT_REFUSAL` retired;
  `PAIRED_OBJECTS`, `_Paired`, `_PairedObservation`, `_pair_with_spec`,
  `resolve_paired_observations`; the `anchor` and `url` rules.
* `linkedin_server/writes.py` -- `_recipient_gate`'s two coercions routed
  through `coerce.as_count`.
* `scripts/_check_the_refusing_grant_can_fail.py` -- new; the five controls.
* `tests/test_the_harness_grant_cannot_authorise_a_write.py` -- new; the
  same property where the suite reaches it, with its own control.
* `tests/reader_leak_baseline.json` -- regenerated through its own
  documented path.
* `_audit/INSTRUMENTS.md` -- section 52 appended. **The number was the
  current maximum plus one, which is exactly the collision
  `tests/test_the_register_numbers_are_unique.py` exists to catch:
  every parallel worktree computes the same next key from the same
  already-outdated maximum. If the merge finds another 52, renumber this
  one -- nothing cites it yet.**
* `_audit/INDEX.md`, `_audit/RULINGS.md` -- regenerated by
  `scripts/build_audit_index.py --write` and
  `scripts/build_rulings_index.py --write`; both are derived files with
  a guard that re-derives them.
