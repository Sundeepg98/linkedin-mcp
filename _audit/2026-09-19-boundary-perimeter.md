# The boundary's real perimeter, 2026-09-19

**Owner: the `boundary-perimeter` wave. Scope: measure the mutation scanner's
perimeter, extend its interaction classes, rule on `scripts/` scope, answer the
read-that-writes question, re-freeze the digest.**

**Fired at a live account: NOTHING. No press, hover, click, type or send. No
page was loaded. The hover class was proven by a FIXTURE source, never by
hovering.**

**CORRECTS:** `_audit/2026-09-19-messaging-menu-enumeration.md` -- its section 3 reports the predecessor's refusal to press a menu as a voluntary discipline the fleet holds, and measurement shows otherwise: at least seven probes in `scripts/` open a menu by clicking it and close it with Escape, so the press was unsanctioned IN THE PACKAGE and routine IN THE PROBES, which is a different situation from the one that document describes.

**CORRECTS:** `_audit/2026-09-19-content-tail.md` -- its section 4.4 calls the composer autosave "an unsanctioned, unverifiable write occurring inside an admitted read", and the unverifiable half holds while the unsanctioned half does not: `server.CENSUS_SURFACE_COST` carries the risk for both composer surfaces, records that 17 draft-listing addresses were refused, states that the operator cleared the cost knowingly, and emits it on the answer rather than in a docstring.

---

## 1. THE PERIMETER, MEASURED BEFORE IT WAS CHANGED

    18 detector classes;  5 sanctioned mutations, in 2 functions in 2 files
    31 modules scanned  (linkedin_server/*.py, non-recursive, nothing hidden)
    98 probe scripts, 139 test modules, 1 root entrypoint -- ALL OUT OF SCOPE

**THE MODULE STATES ITS OWN GUARANTEE THREE TIMES AND ALL THREE ARE STALE.**

    readonly.py:44   "the package contains exactly ONE mutating call"
    readonly.py:74   "exactly two ... BOTH INSIDE writes.perform"
    MEASURED          FIVE, across TWO files, in TWO functions

Wrong in the count and wrong in the location: one of the five is
`dom.activate_messaging_filter`. `select_option` and `set_input_files` -- a
dropdown choice and a FILE UPLOAD -- are permitted and named in no prose
anywhere in the module.

**NOTHING TESTS THE PROSE AGAINST THE LIST.** The list cannot rot; the sentence
a reader actually reads can, and has. The module names the defect it commits:
its own line 99 warns that *"enumerating what this server does not do, without
naming the things it does, is how a true list misleads."*

`linkedin.py`, the repo-root entrypoint, is not scanned. It is 32 lines and
holds zero mutating calls, so the hole is real and empty -- and nothing would
report it if that changed.

---

## 2. THE SCANNER MATCHED SPELLINGS, NOT CAPABILITIES

Playwright's public async surface was enumerated from the INSTALLED library --
`Locator`, `Page`, `Frame`, `ElementHandle`, `Keyboard`, `Mouse` -- and every
interaction-shaped name run through the shipped scanner as a fixture source.

    SEEN 19    MISSED 26, of which FOUR are reads that MUST be missed
               (input_value, is_checked, count, screenshot -- the
                false-positive control, and it passed)

**22 genuine interaction, injection and interception methods were invisible,
and they were not independent.** They cluster as near-miss siblings:

| caught | missed sibling |
|---|---|
| `press` | `press_sequentially` -- it TYPES |
| `check`/`uncheck` | `set_checked` |
| `drag_to` | `drag_and_drop` |
| `route` | `unroute`, `route_from_har`, `route_web_socket` |
| `add_init_script` | `add_script_tag`, `add_style_tag` |

**AND THE SHARPEST CASE WAS AN ASYMMETRY INSIDE ONE MODULE.**
`readonly.JS_MUTATION_TOKENS` already refuses `.focus(` and `.blur(` in the
JavaScript this package injects. **The same act was a mutation written one way
and invisible written the other**, decided by two tables in one file that never
met. Adding them to the Python side is not a new policy; it is making one
scanner agree with a policy the other already enforces. Every other JS token
either has a Python class or is reachable only through `evaluate`, which is
classed -- so the asymmetry was exactly two tokens.

**Eleven classes added. Cost measured with the scanner's REAL semantics (which
skip comments, `re.compile(` lines, bare string literals and `# readonly-ok`):
ZERO hits across all 31 modules.** No sanction needed; the package still holds
exactly five mutating calls against five sanctioned entries.

### 2.1 Two candidates REJECTED, and both reasons generalise

* **`clear`** -- a bare `\.clear\s*\(` matches `_CACHE.clear()`,
  `_GRANTS.clear()` and `_OBSERVED.clear()`. **PLAYWRIGHT'S METHOD NAMES COLLIDE
  WITH PYTHON'S CONTAINER API**, so a text scanner cannot take a bare verb
  without asking what else in the language owns that name. A pattern firing on
  ordinary Python forces noise-suppression, and suppressed output is where a
  real hit goes unseen.
* **`goto`/`go_back`/`reload`** -- 31 hits. This package navigates as its whole
  job; the class would demand 31 sanction entries and would change what the
  guarantee MEANS, from "it does not act on LinkedIn" to "it does not move".
  **Reported to the operator, not taken.**

Both absences are now pinned by tests, so they stay decisions rather than
becoming oversights.

---

## 3. `scripts/` -- THE PROBES WERE NEVER ABSTAINING

    scripts/  99 files, 21 with hits, 45 hits
              evaluate 24, click 12, press 7, http_post 1, fill 1

Read line by line: **ten real `.click()` on a live page, seven
`page.keyboard.press("Escape")`, one `page.fill()` typing a name into a message
composer**, one `.click(trial=True)` dry run, one false positive.

**At least seven probes open a menu by clicking it and close it with Escape.**
That is the established way this repository enumerates a menu -- and it is the
act my own messaging wave declined this morning while reporting the refusal as
a fleet-wide discipline. Nobody had ruled; everybody assumed, and I assumed
with them and wrote it down as a finding.

### 3.1 `tests/` settles the scope question by reductio

Its 94 hits include **exactly one of each of the eleven new classes**, because
`tests/test_the_scanner_has_only_ever_gained_detectors.py` carries one fixture
call per class BY DESIGN, to prove each detector fires. **A test that proves the
scanner catches `.click(` must contain `.click(`.** Extending the package rule
to `tests/` would make the guard unfalsifiable by construction. `tests/` stays
out of scope as an argued ruling rather than an accident.

### 3.2 THE PROBE RULE: split the VERBS, not the FILES

`tests/test_probe_interaction_budget.py`. A `(path, function, kind)` allowlist
over 99 churning probe files would be stale the day it landed, and its first
stale week would teach every wave to route around it.

**OPEN** -- `click`, `evaluate`, `hover`, `focus_or_blur`, `select_text`,
`scroll_into_view`, `keyboard`, `mouse`: a read in effect, or the means of
reaching one.

**GATED** -- everything else the scanner knows, **DERIVED BY SUBTRACTION**, so a
class added tomorrow is gated by default rather than silently open. A probe may
use one; it must be declared with its reason, so it arrives in a diff rather
than in an incident.

**`press` IS SPLIT BY ITS ARGUMENT.** `press("Escape")` closes a menu;
`press("Enter")` submits. Same call, opposite acts. The one place this guard
reads an argument rather than a verb, so both sides are pinned.

Two declarations: the typeahead probe's `fill` (bounded in its own docstring --
never a body, never a send control, refuses a non-empty composer), and a FALSE
POSITIVE declared as one -- `langValues.delete("")`, JavaScript inside a Python
string, which `http_post` cannot tell from an HTTP DELETE. **That is the
existing scanner's real precision limit, written down instead of rediscovered.**

**NO PROBE WAS EDITED. Nothing was mass-fixed.** A red probe is a measurement.

---

## 4. THE READ THAT MAY WRITE: unmeasurable, and already ruled

**Does loading `/article/new/` autosave a draft? UNMEASURABLE WITHOUT CREATING
ONE -- and the cost is already cleared.**

* The only reliable instrument is a before/after read of a draft surface, and
  **every draft surface is refused.** `server.py` records 17 candidates run
  against the boundary on 2026-08-31, all refused; five re-verified
  independently here (`/pulse/drafts/`, `/drafts/`, `/content/drafts/`,
  `/my-items/posts/`, `/in/me/recent-activity/all/` all False) while
  `/article/new/` and `/feed/` are True, so the reader was alive when it spoke.
* **`/article/new/` has never been loaded by this repository.** Three waves
  declined it; the only probe naming the address is a pure offline verdict
  check with **no `goto` in it**. A measurement would be the FIRST occurrence.

So the read that would settle it is the read that would cause it, and the
counter that would price it sits on a page the boundary refuses. **The load was
not taken.**

**AND THE RULING ALREADY EXISTS.** `CENSUS_SURFACE_COST` carries, for both
composers, that a composer may autosave, that no reachable surface could detect
or remove such a draft, and that *"the operator cleared this cost knowingly"* --
emitted on the answer as `out["cost"]`, because *"a cost written where the
caller does not look is a cost the caller was not told about"*.

**The exposure is live and callable** -- `server.py:5116` navigates to
`CENSUS_SURFACES[key]` and `article_composer` is an accepted key -- but
reachable AND disclosed is a different situation from reachable and unruled.

### 4.1 What IS unguarded: the NEXT surface

    12 census surfaces, 5 priced, 7 silent, and no test requiring either.

The table has an explicit rule, stated while explaining one of the silences:
*"absent from CENSUS_SURFACE_COST ... means 'believed to cost nothing' --
BELIEVED, NOT MEASURED."* **An absence is an assertion made by omission**, and
the emit path is `if key in CENSUS_SURFACE_COST` -- so an unpriced surface tells
the caller nothing at all. Add a third composer tomorrow, forget the line, and
the rule silently reclassifies the omission as free.

`tests/test_every_census_surface_prices_itself.py` requires every key to be
priced or argued free, and pins both composer disclosures **by substance**, so
rewording is free and deletion is not. The seven existing silences are
transcribed rather than re-adjudicated -- with `search_appearances` carried
across as believed-free **with its stated doubt**, since whether that surface
has a counter of its own has never been looked at.

---

## 5. THE RE-FREEZE

    _MUTATION_CALL_PATTERNS   23aece1483afdee9 -> 10a0e8e2bb4d7812

**Seven of eight digests byte-identical** -- all three denylists, both exemption
tables, `JS_MUTATION_TOKENS`, `SANCTIONED_MUTATIONS` and `<functions>`. That
last is load-bearing: `readonly.py` gained no function and no function body
changed, so this is a detector change and nothing else in the module.

Two maps held the old value and **only one was updated**. The superseded map
records what the values WERE at a past freeze; re-baselining it would have
falsified history. Which dict each line belonged to was established by PARSING,
not by eye.

**A digest cannot tell a table that grew from one that shrank.** That erosion is
already named in that file for the forbidden roster, with the remedy already
chosen -- pin the contents when direction matters.
`tests/test_the_scanner_has_only_ever_gained_detectors.py` applies it here:
all 29 class names as a SUBSET, each detector shown FIRING on a fixture, reads
shown NOT flagged, and the two rejections pinned. Otherwise the only thing
establishing the direction of my own change was a count I typed into a terminal.

---

## 6. PROVENANCE

    ff150b6  readonly.py + re-freeze + the direction pin      444 ins, 2 del
    026f0f1  tests/test_probe_interaction_budget.py           280 ins
    01f1dce  tests/test_every_census_surface_prices_itself.py 187 ins
    + the commit carrying this document.

    mutations shown killing   14 across the three test files, each
                              diff-confirmed to have applied before its run
                              counted. One did NOT apply and printed exactly
                              that rather than being scored as a pass; it was
                              re-run once the anchor was fixed (a CRLF line
                              ending defeated the first attempt).
    restores                  byte-identical after every mutation, from a
                              COPY taken beforehand rather than by retyping.
    gate                      2227 passed, 1 failed across every test file
                              that touches `readonly`. The failure is
                              `_probe_add_section_menu.py` on the navigation
                              taint guard -- owned by `edd24f8`, clean in my
                              status, untouched by all three of my commits.
    identity sweep            PASS after every staging.
    AI attribution            0, verified at the end.
    contention                every commit via `git commit --only -- <path>`
                              against an index read immediately before. It
                              mattered twice: a neighbour's blocker-map and a
                              census slice were staged inside my window and
                              stayed out of my commits.

**`server.py` WAS NEVER MUTATED, even to show a check failing.** It is
permanently contended, and the two discriminating cases for the composer
disclosure were aimed at other real keys instead -- a surface with no cost entry
and a priced surface whose cost is not an autosave. Both went red, which proves
the predicate discriminates rather than passing on whatever it is handed.
