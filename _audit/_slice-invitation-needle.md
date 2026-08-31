# Slice: aiming one invitation control by a call-time needle

Date: 2026-08-31. Branch `master`, HEAD `b364744`, nothing committed.
Files touched, and they are exactly the three owned:
`linkedin_server/dom.py`, `linkedin_server/writes.py`,
`tests/test_writes_nine.py` (new section 8).

`linkedin_send_invitation` STILL REFUSES. No anchor was wired, no
`SANCTIONED_MUTATIONS` entry was added, `PERFORMABLE` is unchanged, and no grant
can be minted for the action. What this slice delivers is a READER and a
DECISION, both measured against fixtures, plus one blocker that needs a ruling
before the suite can go green.

---

## 0. ESCALATION -- three assertions in a file this slice does not own

The design ruled that the match happens in JavaScript inside the page. That
requires a `page.evaluate`, and `dom.py` carries a boundary contract about
injected scripts that the brief did not mention. Adding the script turns three
assertions in `tests/test_readonly.py` red. **That file is not on this slice's
ownership list**, and at the time the work started a sibling agent had it
checked out dirty.

Measured, after the change:

```
FAILED tests/test_readonly.py::test_only_dom_module_waives_evaluate
E       AssertionError: {'dom.py': 7}
E       assert 7 <= 6
E        +  where 7 = ...get('dom.py', 0)

FAILED tests/test_readonly.py::test_the_scripts_executed_are_exactly_the_ones_declared
E       AssertionError: {'CENSUS_JS', 'HARVEST_BLOCK_CARDS_JS',
E                        'HARVEST_LINKED_CARDS_JS', 'INVITE_NEEDLE_JS',
E                        'READ_PROFILE_JS', 'TRACKER_ROW_SHAPE_JS'}
E         Extra items in the left set:
E         'INVITE_NEEDLE_JS'

FAILED tests/test_readonly.py::test_every_injected_script_is_scanned
E       AssertionError: {'CENSUS_JS', ... 'INVITE_NEEDLE_JS', ...}
E         Extra items in the left set:
E         'INVITE_NEEDLE_JS'
```

These are the ONLY three failures in that file attributable to this slice. It
was also 12-red on unrelated allowlist assertions while the sibling was mid-edit
on `readonly.py`; those cleared on their own and are not this slice's.

### The exact delta, measured not guessed

```
EXECUTED_SCRIPTS count now : 7   (tests/test_readonly.py asserts == 6)
executed names             : CENSUS_JS, HARVEST_BLOCK_CARDS_JS,
                             HARVEST_LINKED_CARDS_JS, INVITE_NEEDLE_JS,
                             READ_PROFILE_JS, TRACKER_ROW_SHAPE_JS
declared INJECTED_SCRIPTS  : the same set MINUS INVITE_NEEDLE_JS
mutation scan of new script: []          <- passes the JS mutation scanner
```

Three edits close it, and the script already passes the scan that matters:

1. `INJECTED_SCRIPTS` gains `"INVITE_NEEDLE_JS": dom.INVITE_NEEDLE_JS,`
2. `assert len(EXECUTED_SCRIPTS) == 6` becomes `== 7`
3. `assert waived_in.get("dom.py", 0) <= 6` becomes `<= 7`

**Decision needed from the lead**, and there are two routes:

* **(a) Apply the three edits.** Keeps the ruled design exactly. Costs one new
  declared entry on the read-only boundary. The script scans clean, so
  `test_every_script_this_package_executes_cannot_mutate` passes once declared.
* **(b) Do the match with a pure locator chain instead** --
  `button[aria-label$=" to connect"][aria-label*="<needle>" i]` counted with
  `.count()`, and the position resolved with `locator.nth(i).and_(...)`. CSS
  `*=` with the `i` flag does the comparison in the page's own selector engine,
  so no label reaches Python either, and NO boundary declaration is needed.
  **This was NOT implemented, because it is a redesign and the brief said
  escalate rather than redesign.** Two costs if it is chosen: the needle would
  have to be escaped into a selector string (a `"` in a needle breaks out of
  the attribute selector, so it would need a validator), and `nth().and_()`
  support in the pinned Playwright version is UNMEASURED.

Route (a) is implemented and tested. Route (b) is a small change to one
function if preferred.

---

## 1. The JS return shape -- integers and nothing else

`dom.INVITE_NEEDLE_JS`, passed the needle as a script ARGUMENT (never spliced
into source, so the script stays a constant the scanner can read whole):

```js
(cfg) => {
  const needle = String(cfg.needle).toLowerCase();
  const nodes = document.querySelectorAll(cfg.selector);
  let total = 0;
  let matches = 0;
  let index = null;
  for (const node of nodes) {
    const label = node.getAttribute('aria-label') || '';
    if (!label.endsWith(cfg.suffix)) continue;
    const position = total;
    total += 1;
    if (label.toLowerCase().indexOf(needle) !== -1) {
      matches += 1;
      index = (matches === 1) ? position : null;
    }
  }
  return {total: total, matches: matches, index: index};
}
```

The label is bound to a local, compared, and discarded. It is never returned,
never pushed onto an array, never assigned to a field. The suffix is matched
AS A SUFFIX with `endsWith` -- **no whole label is ever constructed from a
prefix**, because the prefix has never been read and is not guessed here.

`index` is `null` and not `-1` deliberately: `-1` handed to Playwright's `nth`
means THE LAST CONTROL, so an integer sentinel for "do not aim" would aim, at a
stranger.

Measured payload crossing the boundary, from the spy test:

```
[{'total': 4, 'matches': 1, 'index': 1}]
```

Python then holds three integers and the needle the operator typed. Nothing
else.

## 2. The reader and the aiming rule

`dom.read_invitation_surface(page, needle=None)` returns
`{"controls": int, "matches": int|None, "index": int|None}`.

`matches is None` and `matches == 0` are DIFFERENT answers -- nobody asked
versus nobody carried it. An empty or whitespace-only needle is treated as
"nobody asked", because a blank string is a substring of every label and would
otherwise report a match on all nine, indistinguishable from a real ambiguity.

`writes.aim_invitation(reading)` implements the ruling. Its ONLY input is the
three integers -- **it never sees the needle**, which is asserted by signature
inspection, so no branch exists on which a name could reach the text a caller
reads or stores.

| matches | verdict | index |
|---|---|---|
| `None` | `INVITE_UNASKED` | `None` |
| `0` | `INVITE_NO_MATCH` -- nobody here carries that word | `None` |
| `>= 2` | `INVITE_AMBIGUOUS` -- choosing would be choosing by position | `None` |
| `1`, index present | `INVITE_AIMED` | the aim |
| `1`, index missing | `INVITE_AMBIGUOUS` -- an aim is not invented | `None` |

## 3. The no-leak test, and the red receipt that certifies the ruling

**The first version of this test was too weak, and the mutation found it.**
`test_no_planted_name_survives_into_python` sweeps the reader's RETURN VALUE.
With the script altered to return the matched label, it stayed GREEN -- because
the Python reader copies three fields out of the payload and drops the rest.
The name HAD entered the process and was sitting in a local; the only test
watching was looking one step too late. The ruling says the name must never
enter the process, which is a stronger claim than "the reader must not forward
one".

`test_nothing_carrying_a_name_crosses_out_of_the_page` watches the boundary
itself, via a `_RecordingPage` proxy that keeps every `evaluate` return value
verbatim before the reader can filter it. Under the same mutation:

```
MUTATION: INVITE_NEEDLE_JS altered to return the matched label

E   AssertionError: 'Quill Featherstone' crossed out of the page:
E   [{'total': 4, 'matches': 1, 'index': 1,
E     'label': 'Quill Featherstone the Younger to connect'}]
E   assert 'Quill Featherstone' not in "[{'total': ...o connect'}]"
E     'Quill Featherstone' is contained here:
E       'label': 'Quill Featherstone the Younger to connect'}]

E   AssertionError: assert 'return {total: total, matches: matches, index: index};'
E     in '...return {total: total, matches: matches, index: index, label: lastLabel};'

FAILED tests/test_writes_nine.py::test_nothing_carrying_a_name_crosses_out_of_the_page
FAILED tests/test_writes_nine.py::test_the_script_returns_a_fixed_set_of_numeric_fields
2 failed, 2 passed
```

Mutation reverted; both green.

## 4. Every guard shown failing

Each mutation applied to the shipped source, run, reverted.

| # | Mutation | Red |
|---|---|---|
| M1 | script returns the matched label | `'Quill Featherstone' crossed out of the page` (section 3) |
| M2 | suffix predicate removed (selector widened AND `endsWith` dropped) | `AssertionError: the decoy was counted` / `assert 5 == 4` |
| M3a | `label.toLowerCase()` removed | `assert 0 == 1` |
| M3b | `String(cfg.needle).toLowerCase()` removed | `AssertionError: TOBIAS WINTERBOTTOM` / `assert 0 == 1` |
| M4 | aim KEPT on a second match instead of erased | `AssertionError: an index survived an ambiguous read` / `assert 0 is None` |
| M5 | empty-needle guard removed | `AssertionError: '   '` / `assert 0 is None` |
| M6 | `writes`: `matches > 1` weakened to `matches > 2` | `assert 'aimed' == 'ambiguous'` |
| M7 | `writes`: the unasked branch removed | `TypeError: int() argument must be ... not 'NoneType'` |
| M8 | `writes`: one match with no index aimed at position 0 | `TypeError: int() argument must be ... not 'NoneType'` |

**Two checks that could not fail were found this way and repaired**, which is
the reason the protocol is worth its cost:

* `test_the_match_is_case_insensitive` originally used only variations of a
  label that was ALREADY lowercase, so folding the NEEDLE alone satisfied it and
  M3a passed green. A second half was added -- a title-case label reached by a
  lowercase needle -- which only passes if the LABEL is folded too. Both halves
  now go red under their own mutation.
* `test_the_aiming_rule_is_exactly_one_or_nothing` had no row carrying two
  matches AND an index, so the ambiguity refusal was being satisfied by the
  missing-index guard further down rather than by the count check it was meant
  to test. M6 passed green. The row `{"matches": 2, "index": 3}` was added and
  M6 now goes red on it.

## 5. FINDING: does the confirm-token target persist the member argument?

**No -- not anywhere that outlives the call, and the reason is structural
rather than careful.** Measured by driving a real `writes.preview` for
`send_invitation` over fixtures:

```
url_template                : None
grants after preview        : 0
observations after preview  : 0
confirm_token in block      : None
member arg echoed in block  : True     <- at where.target, a RETURN value
what_the_page_showed        : {'controls': 1, 'matches': None, 'index': None}
consume message             : unknown or already-discarded confirm token
member arg in that message  : False
```

The chain, each link verified:

* `writes.py` contains **zero `logger.` calls and zero file writes**. Grepped:
  both return nothing. So no target can reach a log or a file from this module.
* `_GRANTS` and `_OBSERVED` are module-level dicts, documented never-to-disk.
* `mint()` raises on `spec.url_template is None` **before** `_target_for` is
  reached, so no invitation target is ever canonicalised into a grant.
* `preview()` calls `observe()` first, which does put the member string into
  `_OBSERVED` as `Observation.target` -- but pops it in a `finally`. Measured
  above: 0 observations remain.
* `consume()`'s mismatch message
  `f"token was minted for target {grant.target!r}, not {str(target)!r}"` WOULD
  echo a member identity into an error string. It is unreachable for
  `send_invitation` today because no grant can exist.

**Three conditional hazards, live the moment this action becomes grantable.**
None of them is a defect today; all three are things a future wiring must
handle, and none is fixed in this slice:

1. **`consume()`'s mismatch message echoes both targets.** For a grantable
   invitation that is a stranger's name in an exception string returned to the
   caller.
2. **`_GRANTS` has no sweeper.** Enumerated every reference: written at
   `mint`, removed only by `consume` (success or the expiry branch) and by
   `discard_all`. No timer, no task, no `atexit`. A minted-but-never-confirmed
   grant therefore holds its `target` in process memory for the lifetime of the
   process. TTL bounds when it can be USED, not how long it is HELD.
3. **`_render` prints `where["target"] = observation.target` and
   `where["what_the_page_showed"] = observation.facts` for the seven**, and a
   minted grant keeps that whole rendered block in `grant.preview`. So for a
   grantable action the target is retained in memory twice over.

**Therefore: the needle must never be routed through the `target` channel.**
This slice deliberately did NOT extend `_read_profile_invitations` to take a
needle, because the only thing it could take one from is the spec's target --
which is `Observation.target`, `where["target"]`, `grant.target`,
`grant.preview` and `consume`'s error text. A future wiring must pass the
needle as a SEPARATE argument that never becomes the target.

## 6. What remains UNMEASURED

Stated plainly because none of it is closed by this slice:

1. **The real prefix of the live label.** Never read, still not read, and not
   guessed. Everything here matches ` to connect` as a suffix. What LinkedIn
   actually writes in front of it -- and whether the needle the operator would
   naturally type appears there at all, in that spelling, with that
   capitalisation -- is unknown.
2. **Whether a needle can be unique on the live surface.** The 9-control census
   never read the labels, so nobody knows whether the nine names are distinct,
   whether any is a substring of another, or whether a plausible needle resolves
   to one. The ambiguity refusal may be the ORDINARY outcome live rather than
   the exception. This is measurable only by running the reader on the live
   page with a needle the operator supplies.
3. **Whether index N in the suffix-matched list is stable across a re-render.**
   The rail is a suggestion rail. Nothing has measured how often it redraws or
   whether it reorders. The index is treated as describing the list AS READ,
   which is why nothing acts on a stored one.
4. **Re-verification before a click is NOT built**, because no click is wired.
   The reader is re-runnable and re-running it immediately before an action IS
   the re-verification instrument, but there is no `_live_control` branch, no
   selector builder, and no `anchor_label_for` entry for `send_invitation`.
   `perform` would refuse it on the missing anchor before reaching a click.
5. **Whether an invitation can be withdrawn.** Unchanged and still unmeasured;
   the sent-invitations manager is on the forbidden-url list.
6. **Route (b) feasibility** (section 0): `locator.nth(i).and_(...)` in the
   pinned Playwright version, and CSS `[attr*="v" i]` behaviour in the page
   engine, are both unmeasured.

## 7. Verification run

```
tests/test_writes.py + tests/test_writes_nine.py   319 passed   (2:00)
tests/test_no_committed_identity.py                165 passed
tests/test_readonly.py                             141 passed, 3 failed
                                                   (the three in section 0)
```

The identity guard is green with **no new `DECLARED_PLANTS` entry**. The
fixture carries display names only -- no slug, no urn, no company id, no email,
no phone -- so no identifier shape was planted and none had to be allowlisted.
All fixture names are nonsense on purpose, and their prefixes are deliberately
inconsistent so that no assertion can come to depend on a prefix form nobody
has measured.

Strict ASCII verified on all three edited files. `_state/` untouched. Nothing
committed, nothing staged.
