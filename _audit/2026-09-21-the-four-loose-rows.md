# THE FOUR LOOSE ROWS -- `shape.invitation_badge`, `hrefs_error`, `pill_label`, `J 57`

Four residuals named by earlier waves and never taken to a verdict. Three are
code and were DRIVEN -- executed against a planted page, not reasoned about.
The fourth is a census row and was RESOLVED against the corpus and the counting
script's own parse; calling that "driven" would overstate it, because no code
of its own exists to run. Nothing live: no browser, no network, no navigation,
no click on a real page. `writes_enabled` untouched.

    stated rows BEFORE   704
    stated rows AFTER    704

Unchanged, and that is the finding rather than an omission: **three of the four
are not census rows**, so the census vocabulary does not apply to them, and the
one that is a census row was already carrying the state the evidence supports.

---

## 0. WHAT THESE FOUR ACTUALLY ARE -- KIND BEFORE RESOLUTION

The brief called them "four rows". Resolving the KIND of each before deciding
anything about it changed the answer for three:

| named as | what it actually is | does the census vocabulary apply? |
|---|---|---|
| `shape.invitation_badge` | a function in `linkedin_server/shape.py`, and a CLAIM in two docstrings | no |
| `hrefs_error` | a dict key returned by `dom.read_company_about_card` | no |
| `pill_label` | a dict key returned by `dom.activate_messaging_filter` | no |
| `J 57` | a census row -- `_audit/_census/jobs.md`, section C | **yes** |

Assigning GAP or MEASURED-ABSENT to a dict key would have been a category
error, and it is the error the brief's own wording invited. Only `J 57` was
ever eligible for a state change, and it did not need one.

### The rulings register was checked first

`_audit/RULINGS.md` at HEAD registers 37 rulings. **None of the four appears
in it by name, and none appears in the alias map.** The register warns in its
own section 4 that its discovery scan reads one marker and has poor recall, so
"absent from the register" is not "unruled" -- each row below therefore names
the ruling that GOVERNS it where one exists, rather than inferring from silence:

* `hrefs_error` is decided by **`ERROR-MESSAGE-RULED-AT-THE-RAISE`**. That
  ruling is not about this field, but it supplies the discriminator this field
  is judged on, and section 2 applies it rather than re-deriving it.
* `pill_label` has no ruling. It is a returned payload field, not an exception
  and not an address, so neither `ERROR-MESSAGE-RULED-AT-THE-RAISE` nor
  `ERROR-URL-ASKED-FOR-OR-NOTHING` reaches it. Recorded as unruled, with the
  fork named.
* `J 57`'s deferral rests on a written decision point (section 4).

---

## 1. `shape.invitation_badge` -- THE PREMISE IS FALSE, THE PUBLICATION IS DELIBERATE

### What the premise was

Two docstrings, both load-bearing. `dom.read_invitation_badge` said the label
is shaped on the way out *"so a nav label that one day carries a name carries
it no further than the page"*, and `shape.invitation_badge` said *"whatever the
nav one day carries, what reaches here is a shape"*.

`_audit/2026-09-21-what-the-browser-said.md` section 6.1 measured that FALSE
and deliberately did not repair it, on the argument that the two honest repairs
are incompatible and *"half of it is worse than none"*.

### What I drove

`shape.census_shape`, directly, with the harness plant and with adversarial
inputs on both sides of its gate:

    census_shape('Exampleperson Markersurname')          -> unchanged
    census_shape('Exampleperson Markersurname, 3 new notifications') -> unchanged
    census_shape('x' * 400)                              -> '<opaque>'
    census_shape('someone.example@example.com')          -> '<opaque>'
    census_shape('')                                     -> ''

Then the whole chain, planted page through reader through shaper:

    reader out: {"links": 1, "badge_links": 1,
                 "label": "Exampleperson Markersurname", "error": null}
    shaper out (REFUSAL branch): saw.shaped_label = "Exampleperson Markersurname"
    shaper out (SUCCESS branch, pending=3, state="read"):
                 saw.shaped_label = "Exampleperson Markersurname, 3 new notifications"

### What came out

**The premise is false and the gate is real -- both.** `census_shape` is a
CHARACTER AND LENGTH gate, exactly as `dom.py` says twice in its own comments.
It converts a long or odd-charactered label to `<opaque>`, and it passes a
short plain name through UNCHANGED. The label is then republished at
`saw.shaped_label` on the success branch and on every refusal branch.

This is the half the earlier wave stated and I add one thing to it: the
publication is **required by the refusal contract**, not incidental to it.
`_unreadable` exists to say WHAT IT SAW so that "the nav did not hydrate"
(`links: 0`) can be told from "the label changed shape"
(`links: 3, badge_links: 0`). Deleting the field would collapse that pair back
into the bare "zero matched" this repository has twice recorded as saying
nothing.

### The state the evidence supports

**A FALSE CLAIM ABOUT A DELIBERATE PUBLICATION -- not a leak, and not safe.**
Those are three distinct things and the corpus had collapsed them into one.

The two repairs the earlier wave named are still incompatible, and I took the
first of them rather than leaving the fork open at the prose level:

* **TAKEN:** correct the claim, keep publishing the label. Both docstrings now
  state the measured truth, name the gate for what it is, and say plainly that
  the field is name-bearing. `tests/test_the_unread_readings_were_never_driven.py`
  pins both halves -- that `census_shape` does not redact a name, and that
  `saw.shaped_label` is published on both branches -- so the stronger claim
  cannot drift back in.
* **NOT TAKEN, and left as a named fork:** publish the label's SHAPE instead of
  the label (`landing.withheld` is the worked precedent, alphabet closed). That
  changes a payload and belongs to whoever owns it.

**Why this is not the "half" the earlier wave warned against.** Its objection
was that a prose-only fix *"would leave the next reader believing the question
was settled"*. What makes the difference is not the prose, it is the pinned
test: a reader who arrives at either docstring now meets an assertion that runs,
plus an explicit statement that the payload fork is open. Prose alone would have
been the half. Prose plus a control that convicts the stronger claim is the
whole of repair (a).

---

## 2. `hrefs_error` -- THE CLAIM HOLDS, AND NOW IT IS DRIVEN

### What it is

`dom.read_company_about_card` stores `out["hrefs_error"] = type(exc).__name__`
when the About-the-company card's link harvest raises. Its purpose, in the
function's own comment: an empty `hrefs` list from a FAILED read and an empty
one from a card with NO links are the same value and different answers.

`_audit/2026-09-21-described-never-built.md` section 4 filed it UNREAD and
called it *"the one worth a follow-up wave"*.

### Does anything consume it?

**No -- and the interesting part is that this was settled by execution rather
than by grep.** A key-string search cannot see a whole-dict spread, which that
same section says in its own words. So the chain was walked hop by hop and each
merge RE-RUN with a poison value:

| hop | what happens | verdict |
|---|---|---|
| `dom.read_company_about_card` -> `linkedin_job_detail` | whole dict bound to a local | present, unread |
| -> `shape.company_about_card(about, ...)` | reads `container` and `lines` only; every return is a fresh literal | **DROPPED** |
| -> `company_page.tally(about.get("hrefs") or [])` | takes the SIBLING key, and its signature takes a list | unreachable by type |
| the tool's return `out` | built from `dom.read_job_posting`; `about` is never spread into it | **never reaches the tool JSON** |

Poison run through `shape.company_about_card`: `POISON_PRESENT_ANYWHERE_IN_REPR:
False`. Zero code anywhere branches on it. Zero tests assert on it.

### Does a page-chosen value reach it?

**No.** Driven on the raise path, with the plant inside the raising exception's
own ARGUMENTS -- which is the discriminator `ERROR-MESSAGE-RULED-AT-THE-RAISE`
names, knowable at the raise and unknowable at the envelope:

    link harvest raises ValueError("Timeout 30000ms resolving selector '<PLANT>'")
      hrefs_error = 'ValueError'        <- the TYPE NAME, no page value
      hrefs       = []
      PLANT in hrefs_error: False

**THE POSITIVE CONTROL, in the same function, on the same dict:**

    inner_text raises ValueError("Timeout 30000ms reading '<PLANT>'")
      error       = "ValueError: Timeout 30000ms reading 'Exampleperson Markersurname'"
      PLANT in error: True

The sibling field `error` stores `f"{type(exc).__name__}: {exc}"` six lines
above `hrefs_error`'s `type(exc).__name__`, and the comment between them calls
that *"a deliberate difference"*. The difference is real, it is the whole
safety property, and the control proves the instrument could have seen a page
value here -- because it saw one, one field over.

### The state the evidence supports

**CORRECT, UNREAD, AND NOW ASSERTED.** The field does what its comment says.
It is not a defect and it does not need a repair. What it needed was a test,
and it had none -- `tests/test_job_detail_wiring.py`'s docstring CLAIMS the
healthy path asserts *"the error field is null"*, and its body asserts no such
thing. A claimed assertion that does not exist is a check that cannot fail
wearing a docstring. That assertion now exists.

---

## 3. `pill_label` -- RAW PAGE TEXT, PUBLISHED, AND UNREACHABLE BY BOTH SHIPPED GUARDS

This is the one the brief described as *named, never driven*, and that
description was exactly right. It is the finding of the wave.

### What it is

`dom.activate_messaging_filter` returns `"pill_label": label`, where `label` is
read from the clicked control by `get_attribute("aria-label")`, falling back to
`inner_text()`. Both are PAGE-CONTROLLED by `plantedpage`'s own taxonomy: the
document chooses them.

### Driven, for the first time

All seven permitted filter names, using the shipped harness with one change --
the click allowed as a no-op (see below for why that change is the whole point):

    focused / other / unread / jobs / connections / inmail / starred
      pill_label = 'Exampleperson Markersurname'   on every one
      pill_label in dom.MESSAGING_FILTERS: False

The value is not bounded by the closed tuple. The locator matches
`name=wanted, exact=False`, so the control's accessible name need only CONTAIN
the permitted word -- and the label is then read back WHOLE.

### It reaches the model's JSON

`linkedin_open_messaging` does `verdict["active_filter"] = {"requested": ...,
**applied}` and then `return {**verdict, "pages_loaded": 1}`. Both spreads were
re-run against a poisoned stand-in, and the guard's own `plant_positions`
instrument was run over the real driven output:

    plant positions, by the shipped guard's own instrument:
       $.active_filter.pill_label

    "active_filter": {
       "requested": "inmail",
       "activated": true,
       "filter": "inmail",
       "pill_label": "Exampleperson Markersurname",
       "url_before": "https://www.linkedin.com/feed/",
       "url_after":  "https://www.linkedin.com/feed/",
       "navigated": false,
       "url_movement": "none"
    }

`/messaging/` is admitted (`readonly.is_read_url` returns True) and
`linkedin_open_messaging` is a registered tool, so this is a live path, not a
hypothetical one.

### IT SITS BESIDE THE TWO FIELDS THAT WERE REDACTED AFTER A REAL LEAK

`url_before` and `url_after` go through `shape.redact_thread_id` because on
2026-09-03 they shipped raw and a real conversation identifier reached a
transcript. `tests/test_a_thread_id_never_leaves_the_module.py` was written for
exactly that, and its own docstring states the shape: *"a redaction applied at
one site and not at the site beside it, because the second pair was added later
by somebody reading the first as decoration."*

`pill_label` is the third field in that return, unredacted. That guard passes,
correctly: it checks the THREAD-ID class, and a pill label is not a url.

### WHY NEITHER SHIPPED PAGE-STRING GUARD CAUGHT IT -- TWO INDEPENDENT REASONS

This is the part worth carrying forward, because one of the two reasons
produces a verdict that ASSERTS something false-ish.

**The READER guard cannot call it.** `tests/test_readers_emit_no_page_string.py`
supplies `plantedpage.SYNTHETIC_ARGUMENT`, which is not in
`dom.MESSAGING_FILTERS`, so `assert_permitted_filter` refuses it before any
locator exists. The baseline records this honestly:

    "dom:activate_messaging_filter": "not_driven:raises ValueError"

`not_driven` claims nothing. That entry is fine.

**The TOOL guard drives the wrong branch and prints CLEAN.** Its `build_call`
contains `if param.default is not param.empty: continue` -- it skips every
parameter that has a default. `linkedin_open_messaging`'s signature is
`include_names: bool = False, message_filter: str = ''`, **both defaulted**, so
the guard calls it with `message_filter=''`, the `if wanted:` branch is never
entered, `activate_messaging_filter` is never called, and:

    tool_envelope_baseline.json: "linkedin_open_messaging": "clean"

That is the same defect `plantedpage`'s own docstring records one level down --
*"The reader was never driven, and 'not driven' printed as 'clean'."*

**AND SUPPLYING THE ARGUMENT DOES NOT FIX IT, which is the half that stops this
being a one-line repair.** Measured, by patching `build_call` and calling the
guard's own `drive_tool`:

    {"tool": "linkedin_open_messaging", "verdict": "clean", "reason": "",
     "at": [], "page_reads": 1, "navigations": 1}

Still clean. `PlantedLocator.click` raises `NavigationAttempted` by design, the
tool catches it and returns an ERROR ENVELOPE carrying no page string, and the
verdict is clean for a second, unrelated reason. (My first draft of the driving
script printed a line claiming the verdict moved off clean. It did not. The line
was written before the run and the run refuted it; it is corrected here rather
than deleted.)

The click is `readonly.SANCTIONED_MUTATIONS[1]`, the only sanctioned click in
`dom.py`. **A reader behind a sanctioned click is unreachable by a harness
whose safety property is that it never clicks.** That is not a bug in either
instrument; it is the gap between two correct safety properties, and
`pill_label` is what lives in it.

### How general is the skipped-default hole?

Measured over all 49 discovered tools:

    tools with at least one DEFAULTED parameter (skipped by build_call)   28
    tools with NO required parameters at all (driven at pure defaults)    15
    total parameters skipped because they carry a default                 44
    str-typed defaulted parameters                                        23

Having a default is not itself a defect. The defect is a defaulted parameter
that GATES A BRANCH WHICH READS THE PAGE DIFFERENTLY, and exactly one instance
of that is measured here. The other 43 are NOT classified -- see residuals.

**AND THE GUARD IS NOT WEAK -- IT IS BLIND ONLY HERE, which the contrast
proves.** `linkedin_who_viewed_me` calls a reader recorded `returns_text`
(`dom:read_profile_views_insights`, which carries the plant in seven places
including dict KEYS) and the tool is nonetheless recorded `clean`. Its one
parameter is `limit: int = 25`, so driving it at the default still reads the
page, the guard reaches the payload, and `clean` there means the tool genuinely
shapes its reader's text away before publishing. **That is the healthy pattern,
and it is the same guard.** The difference at `linkedin_open_messaging` is not
that the guard is weaker; it is that a defaulted parameter plus a click the
harness must refuse put the field out of reach entirely.

### The state the evidence supports

**A DELIBERATE-LOOKING PUBLICATION THAT NOBODY DECIDED.** No ruling reaches it,
and the only written reason for the field is `described-never-built`'s
*"For a human, not for a branch. Leave it."*

**THE DIVISION OF LABOUR BETWEEN THAT SWEEP AND THIS DRIVE IS WORTH STATING
EXACTLY, because it is easy to read as a defect in the sweep and it is not
one.** That wave identified the whole-dict spread itself, named it as the limit
of its own method in its own words -- *"a key-string census measures what CODE
consumes, never what a caller sees"* -- and named this field as one of three
worth following up. Everything it claimed is true. What a key-string sweep
cannot answer is what the field CONTAINS, because that needs the function run
against a page, and this function is the one function in the package that a
sweep cannot run: its closed-set check refuses the harness's argument and its
click is refused by the harness's own safety property. So the sweep did the
half that can be done statically and said so. **The remaining half needed a
drive, and the drive is what this wave added.**

**I did not change the payload.** Removing or shaping the field is a payload
decision with a caller-visible cost and it is not this wave's to take
unilaterally. What shipped instead is the thing that was missing: the field set
is now PINNED, class-not-instance, so an eighth raw field fails rather than
ships -- which is the discipline the thread-id file states and could not extend
to this class without a drive.

---

## 4. `J 57` -- RESOLVED, AND IT STAYS GAP

### What it is

`_audit/_census/jobs.md` line 279, under `### C. Saved jobs and the job tracker
(16)`: **"View network connections reachable for a tracked job"**, state `GAP`.

Resolving the kind mattered here too. The string "57" reads as a row in **four**
places in that file, and only one of them is the census row:

| line | section | counted by `count_census_states.py`? |
|---|---|---|
| 107 | `## THE COUNTS` | no -- prose about the row |
| **279** | `### C. Saved jobs and the job tracker` | **YES -- this is `J 57`** |
| 470 | `## 2. WHAT EACH GAP WOULD TAKE` | no -- UNSTATED, no state cell |
| 567 | `## 4. THE CAPABILITIES THE SKILL SERVES...` | no -- only 2 cells, never reaches `classify()` |

Proved against the script's own parse (it reads every `|`-leading line in the
whole file, then `classify()` scans cells 1..n for a state token) and confirmed
by running `count_census_states.py --unstated`, where line 470's row appears
verbatim in the unstated dump and line 567 appears nowhere.

### The verdict

**GAP is CORRECT and the row does not move.** Four documents in two days touched
it and not one moved its state:

| document | date | what it concluded about `J 57` |
|---|---|---|
| `2026-09-20-the-contingent-writeoffs.md` | 09-20 | overturns the write-off: *"FALSE NOW. Overturn."* -- the skill does not serve this row |
| `2026-09-20-the-three-held-defects.md` | 09-20 | re-verifies that and HOLDS it; strips the `SKILL` tag; `census rows whose STATE changed: 0` |
| `2026-09-21-the-jobs-direction.md` | 09-21 | restates it; classes the row *"dependent rather than independent"* |
| `2026-09-21-the-proximity-field.md` | 09-21 | builds `J 40`, the row it was blocked behind, then: *"DID NOT MOVE. Still GAP, but no longer blocked."* |

The reason it stays GAP is not a boundary and not a ruling: **nothing was built
for it.** `J 57` is a JOIN, and a join is not a by-product of either half. Its
two inputs both ship, and a fixture-wide census puts the proximity needle on
zero bytes of `jobs_tracker_row.html`, so the join cannot be done from a tracker
row at all -- the buildable route costs one page load per tracked job and yields
a boolean. That is a design decision with a live cost, and the proximity-field
wave left it for a ruling rather than taking it.

**Moving this row out of GAP would have been the failure the brief warns about.**
It stays.

### The defect found while resolving it -- and why I did not fix it

**The row and its blocker filing disagree at HEAD.** The census cell says, in
capitals, `THE SKILL DOES NOT SERVE THIS ROW`, and carries no `SKILL` tag.
`blocker-map.tsv` and `blocker-assignments.tsv` still file `J 57` under
`SERVED-BY-GMAIL-SKILL`.

That is not an oversight. It is a **deferral with a written decision point**,
from `2026-09-20-the-three-held-defects.md` section 1.4: the prescribed re-file
onto `PROXIMITY-NOT-PARSED` is a LEDGER act, that name exists nowhere in the
repository except the document that proposed it, and creating it breaks three
pinned assertions -- `test_no_blocker_recounts_higher_than_the_ledger_published`
on its FIRST assertion (`unknown` would be `['PROXIMITY-NOT-PARSED']`),
`build_blocker_map.py`'s per-blocker table (which iterates the ledger's
published set, so a new name holds rows INVISIBLY), and
`test_the_ledger_tables_still_total_97_blockers_and_409_rows`. That wave's own
regression control demonstrates it:

    CONTROL    unmodified build                                 exit 0, silent
    MUTATION   J 40 and J 57 filed onto PROXIMITY-NOT-PARSED    exit 1
      FAIL: the map holds 1 blocker(s) the ledger does not publish...

**It needs a ledger amendment or a re-file onto a name the ledger already
knows, and neither is this wave's to choose either.** Confirmed still deferred:
neither 09-21 document mentions `PROXIMITY-NOT-PARSED` or any re-file, and both
TSVs at HEAD are unchanged.

`build_blocker_map.py --check` was run in CHECK MODE ONLY and is green on this
blocker:

    SERVED-BY-GMAIL-SKILL   6   6   +0   COMPLETE -- every published row recovered

which is worth reading precisely: the map is INTERNALLY consistent with the
ledger and still disagrees with the census row it points at. A derived view
cannot detect that, because the disagreement is with its input's meaning rather
than with its arithmetic.

### A CORRECTION TO MY OWN BRIEF

My brief told this wave that `blocker-map.tsv` and `blocker-assignments.tsv`
are both derived views to be regenerated and never hand-merged. **Half of that
is wrong and the measurement says so.** `scripts/find_blocker_reason.py`'s
`DERIVED_ARTIFACTS` set contains exactly one entry, `blocker-map.tsv`, and its
docstring states: *"`blocker-assignments.tsv` is NOT excluded: it is
hand-written evidence whose notes genuinely argue."* No script regenerates
`blocker-assignments.tsv`; it is the hand-maintained INPUT that
`build_blocker_map.py` derives the map FROM. Recorded because acting on the
brief's version would have meant looking for a build script that does not
exist, and concluding from its absence that the file was unmanaged.

---

## 5. WHAT SHIPPED, AND EVERY CHECK SHOWN FAILING

Two files added, two docstrings corrected, one allowlist triaged, two derived
views regenerated. No payload changed, no census row changed, no allowlist of
addresses, blocker map, ledger or frozen digest touched.

* `tests/test_the_unread_readings_were_never_driven.py` -- ADDED. 9 assertions
  (15 with parametrisation), all green, all shown failing below.
* `scripts/_check_the_unread_readings_guard_can_fail.py` -- ADDED. The control.
* `linkedin_server/dom.py`, `linkedin_server/shape.py` -- docstrings only. No
  executable line changed in either; the diff is 39 insertions over 8
  deletions, all prose.
* `tests/test_a_correction_is_findable_from_the_claim.py` -- CHANGED: four
  `NOT_A_CORRECTION` entries added, one per pair the guard refused to pass.
  **This change is already shown failing**: the guard went red on this
  document before the entries existed, its four-line refusal is quoted in
  section 5A, and the file's own design makes a STALE entry fail as loudly as a
  missing one -- so these four cannot rot into a silencer.
* `_audit/INDEX.md`, `_audit/RULINGS.md` -- REGENERATED by their own build
  scripts, never hand-edited. See section 5A.

The control mutates ONE LINE of the real source in a re-executed copy of the
module, rebinds in process, and restores; nothing is written to disk. Several
mutations are the variant the source's own comments say was deliberately
avoided, and one is the defect that actually shipped on 2026-09-03.

    THE UNREAD-READINGS CHECKS, SHOWN FAILING
    ==============================================================================

    1. hrefs_error -- the field that tells an empty read from a failed one
       CONVICTED  healthy path stops being null
       CONVICTED  marker gains the sibling's formula
       CONVICTED  the positive control is blinded

    2. pill_label -- the page string published at active_filter.pill_label
       CONVICTED  an eighth raw field is added
       CONVICTED  the label becomes the argument
       CONVICTED  url_before loses its redactor
       CONVICTED  the closed set admits the harness argument

    3. the premise shape.invitation_badge rests on
       CONVICTED  census_shape redacts everything
       CONVICTED  census_shape redacts nothing at all
       CONVICTED  shaped_label stops being published

    ==============================================================================
    convictions           10 of 10
    every binding restored True
    PASS: every assertion in the guard was shown convicting a defect.

### THE CONTROL CONVICTED ITSELF TWICE BEFORE IT CONVICTED ANYTHING ELSE

Both are kept rather than tidied away, because they are the only evidence that
the exact-count assertion does any work:

    CONTROL BROKEN: 'out["error"] = f"{type(exc).__name__}: {exc}"' occurs 11
    times in linkedin_server.dom, expected 3. The source moved and this
    mutation would have planted nothing.

    CONTROL BROKEN: '    return shaped\n' occurs 2 times in
    linkedin_server.shape, expected 1. The source moved and this mutation
    would have planted nothing.

The first: I had counted an idiom inside one function and assumed it was that
function's habit; it is a package-wide idiom at 11 sites. The second: a bare
`return shaped` ends `census_substitute` as well as `census_shape`, so the
mutation would have changed the substituter the subject calls and convicted for
the wrong reason. Both were caught by the control refusing to plant, not by
review. A mutation that silently applies to nothing is a control that reports
"cannot fail" about a guard it never handed a defect to.

A third self-conviction, on the harness rather than the counts: `_convict`
crashed on its seventh mutation because a bare `assert x` carries no message and
`str(exc).splitlines()[0]` indexes an empty list. The conviction was real; the
reporter was not ready for it.

---

## 5A. THE IMPACT GATE -- IT REFUSED, AND THE REFUSAL WAS CORRECT

**THERE IS NO `NOT CHECKED` LINE TO QUOTE: THE GATE WIDENED.** Editing
`dom.py` pulls in a large fraction of the suite, exactly as the previous wave
on these keys recorded. Its notice, verbatim:

      WIDENING TO THE FULL SUITE, because the impact set is 168 of 209 test files (80%), at or above the 45% line where running everything costs about the same and answers more.

    + 15 CORPUS-WIDE guard(s), run unconditionally -- they sweep the tracked set and take no input from the diff,
      so no impact analysis can ever select them. Omitting them is how a fast gate ships a real name.

**THE FIRST RUN REFUSED**, and it is quoted rather than summarised because the
four reds are the whole point:

      REFUSED: a test this change can reach is RED.
          FAILED tests/test_the_audit_index_is_derived.py::test_the_committed_index_is_what_the_corpus_derives
          FAILED tests/test_the_audit_index_is_derived.py::test_there_is_a_corpus_and_the_index_covers_all_of_it
          FAILED tests/test_the_rulings_register_is_derived.py::test_the_committed_register_is_what_the_corpus_derives
          FAILED tests/test_a_correction_is_findable_from_the_claim.py::test_every_candidate_pair_is_declared_or_triaged
          4 failed, 7973 passed, 8 skipped, 1 xfailed in 1969.60s (0:32:49)

Three of the four are the derived views refusing to stay green once a new
document entered the corpus. They were repaired the only sanctioned way --
`scripts/build_audit_index.py --write` (218 tracked documents) and
`scripts/build_rulings_index.py --write` (37 rulings registered). **Neither
file was hand-edited**, and the register's count is unchanged at 37 because
this wave declared no new ruling.

The fourth is the more interesting one and it is `a-correction-is-findable`
working as designed. It found **4** candidate pairs where this document uses
correction vocabulary near a citation, and refused to pass until a human read
each line and said which it was. All four are triaged as NOT corrections, with
written reasons, on `NOT_A_CORRECTION`:

* three are rows of ONE chronology table in section 4, where the matched words
  (*overturns*, *FALSE NOW*, *re-verifies*, *HOLDS*) are QUOTED FROM the cited
  documents describing what they did to EACH OTHER. That correction is already
  declared as a different pair -- contingent-writeoffs carries `CORRECTED BY:`
  three-held-defects, which carries the matching `CORRECTS:` -- and this wave
  disturbs neither end of it;
* the fourth cites `2026-09-21-what-the-browser-said.md`, and the relationship
  is AGREEMENT. That section measured the premise false and declined the
  repair; this wave reproduced the measurement and then took the first of the
  two repairs that section itself named. **Acting on a document's own
  recommendation is not correcting it**, and a `CORRECTED BY:` marker would
  tell a reader that section was wrong when it was right.

**THE TRIAGE TOOK THREE ROUNDS, AND THE SECOND AND THIRD ARE THE INSTRUMENT
EARNING ITS KEEP.** Later edits to this document created three MORE candidate
pairs -- two derived-view names in one bullet, and a citation of `jobs.md` in
the locator-drift measurement -- which the guard refused all over again. Those
three are triaged too. Then, with all seven entries written, the guard's OTHER
half fired:

      AssertionError: 1 NOT_A_CORRECTION entr(ies) for pairs the scan no longer
      produces. The prose that made them candidates is gone, so the exception is
      stale and must be deleted -- a stale exception is how an allowlist becomes
      a silencer:
          2026-09-21-the-four-loose-rows.md -> _census/jobs.md

I had keyed that entry `_census/jobs.md` and the scan produces `jobs.md`. **An
allowlist entry that silences nothing is indistinguishable from one that
silences the wrong thing**, and this file asserts both directions, so a
mis-keyed exception failed exactly as loudly as a missing one. Fixed to the key
the scan actually emits.

**A NOTE ON READING THE GATE'S RESULT.** The background wrapper reported the
command's exit as 0 while the gate's own text said `REFUSED`. The verdict is in
the output, not in the exit code, and this is recorded because a wrapper's zero
is exactly the shape that gets mistaken for a pass.

### 5A.1 THE SECOND GATE RUN ALSO REFUSED, ON TWO TESTS THAT ARE NOT THIS WAVE'S

Re-run after the repairs above. The three derived-view reds were gone. Two
different tests were red, in a subsystem this wave never touched:

      WIDENING TO THE FULL SUITE, because the impact set is 169 of 209 test files (81%), at or above the 45% line where running everything costs about the same and answers more.

      REFUSED: a test this change can reach is RED.
          FAILED tests/test_click_is_not_its_own_evidence.py::test_the_refusal_says_when_a_matcher_would_have_separated_them
          FAILED tests/test_tracker_readiness.py::test_an_empty_tab_is_not_delayed
          FAILED tests/test_a_correction_is_findable_from_the_claim.py::test_every_candidate_pair_is_declared_or_triaged
          3 failed, 7974 passed, 8 skipped, 1 xfailed in 2419.49s (0:40:19)

The third is explained above -- the triage entries were being written WHILE
that suite ran, and the file is green now. **The other two were not expected
and were not assumed away.** Two measurements settled them.

**ONE: THE SOURCE DIFF CANNOT CHANGE BEHAVIOUR, PROVEN RATHER THAN ASSERTED.**
Both edited modules were parsed at HEAD and in the working tree and compared as
ASTs with docstrings stripped:

    linkedin_server/dom.py       AST identical with docstrings stripped: True
    linkedin_server/shape.py     AST identical with docstrings stripped: True
                                 raw text identical: False

Raw text differs, executable structure does not. A docstring cannot make a
listbox fail to render or a wait exceed its bound.

**TWO: THE SAME TEST FAILS AT CLEAN HEAD.** A detached worktree was checked out
at `f729a2a` -- this wave's parent commit, none of its changes present -- and
the tracker test run three times:

    1 failed in 48.98s
    1 passed in 34.62s
    1 failed in 62.00s

**Two of three, at HEAD, with this wave absent.** Its assertion is a wall clock
against a 300ms bound, and the numbers it reported across runs were 316ms,
583ms and a passing one -- a logic break returns the same answer every time,
and this does not. `test_click_is_not_its_own_evidence` behaved the same way:
red twice, then green in this worktree on re-run, and green at HEAD.

**SO THE GATE'S REFUSAL IS HONEST AND THE REDS ARE NOT MINE.** Recorded rather
than smoothed over, because the tempting move here is to call two unexplained
reds "flaky" and move on, and the difference between that and this is the HEAD
baseline. The box was running several waves' full suites concurrently, which is
the standing hazard for any gate that asserts wall-clock time. **This wave did
not commit through a bypass**: the pre-commit hook runs the identity gate only,
the impact gate is a manual instrument, and no hook was skipped.

**LEFT AS A RESIDUAL, NOT FIXED:** `test_an_empty_tab_is_not_delayed` asserts a
wall-clock bound and is load-sensitive enough to fail 2 of 3 runs on a busy
box. That is a real defect in a shipped check -- a test that fails without a
defect trains people to ignore it -- but it belongs to whoever owns
`tracker_readiness`, and inventing a repair for it inside this wave would be
scope this brief did not grant.

---

## 6. WHAT THIS WAVE DID NOT DO

* **Nothing live.** No browser, no network, no navigation, no click on a real
  page. Every measurement is a planted page, a pure function, or a record on
  disk. `writes_enabled` untouched.
* **No payload changed.** `pill_label` is still published raw; `saw.shaped_label`
  is still published unredacted. Both are now pinned and both forks are named.
* **No census row moved.** 704 before, 704 after.
* **No derived view hand-merged.** `_audit/INDEX.md` and `_audit/RULINGS.md`
  were regenerated by `build_audit_index.py --write` and
  `build_rulings_index.py --write`. `blocker-map.tsv` was NOT regenerated at
  all -- `build_blocker_map.py --check` was run, write mode was not, and
  nothing this wave did changes its input.
* **No ruling declared.** The register still registers 37. This wave applied
  `ERROR-MESSAGE-RULED-AT-THE-RAISE` to `hrefs_error` and recorded that no
  ruling reaches `pill_label`; applying a ruling and declaring one are
  different acts, and the register exists to stop the second being done by
  accident.
* **No ledger act.** The `J 57` blocker re-file stays deferred on its written
  decision point.
* **No new instrument registered** in `_audit/INSTRUMENTS.md`. The control is a
  can-fail script in the established `scripts/_check_*_can_fail.py` family; the
  test file is an ordinary guard. Neither is a reusable instrument.
* **`hrefs_error`, `pill_label` and `metrics_seen` were not "fixed"** in the
  sense `described-never-built` meant. Two were driven and one (`metrics_seen`)
  was out of scope and is untouched.

---

## 7. RESIDUALS

Ordered by what I would take first.

1. **`pill_label`: decide the payload.** A page-chosen string reaches a model's
   JSON at `active_filter.pill_label`, unruled. The field's only stated purpose
   is that an empty label beside `activated: true` should not read like a
   contradiction -- which is a BOOLEAN's job, and `navigated` in the same return
   is the worked precedent for replacing a string with one at zero cost to the
   caller. Three options: leave it and rule it a deliberate publication; replace
   it with a presence boolean; or pass it through a closed vocabulary. **Not
   taken here because it changes a published payload.**

2. **The tool-envelope guard's defaulted-parameter hole.** 28 of 49 tools have
   at least one defaulted parameter that `build_call` skips; 44 parameters
   total. Exactly ONE is measured to gate a page-reading branch. **The other 43
   are NOT classified and that residual is not forced to zero.** Classifying
   them is a bounded sweep. Note the repair is not one line: even with the
   argument supplied, the click refusal keeps the verdict `clean`, so a tool
   behind a sanctioned mutation needs a driving decision, not just an argument.

3. **`linkedin_open_messaging` is recorded `clean` on a run that could not reach
   its page-text field.** Whatever is decided for residual 1, that baseline
   entry asserts more than the run supports. The honest vocabulary already
   exists one level down -- `not_driven` -- and the reader baseline uses it for
   this very function.

4. **Blocker-assignment locator drift -- MEASURED CORPUS-WIDE, AND IT IS NOT A
   TYPO.** `J 57`'s filing cites `_audit/_census/jobs.md` `L200`. At HEAD that
   is a BLANK LINE. At `bf275cf` the same pointer was measured landing on
   **row 21, a COVERED-PROVEN row** -- so the citation has not been stably
   wrong, it has kept moving, and it passed through the most dangerous state on
   the way: *it does not dangle, it lands on a different row that reads
   COVERED-PROVEN, so a reader checking the provenance of a GAP finds a covered
   row and stops.*

   Because two known-wrong pointers is an anecdote, the whole file was counted.
   `_audit/_census/blocker-assignments.tsv` holds **390** assignment rows.
   **126** carry a locator shaped exactly `L<number>` (the rest are ranges,
   comma-separated multiples, row-id shorthands and one line-plus-commit; every
   one of the 390 landed in a named kind and the UNCLASSIFIED bucket reads 0
   rather than being omitted). Of those 126:

       RESOLVES        0        (0.00%)
       WRONG-ROW      25
       BLANK           5
       NOT-A-ROW      95
       OUT-OF-RANGE    1
       MISSING-FILE    0

   Narrowed to the **35** whose `source` is one of the four census files --
   the only ones where "resolves to the census row it claims" is even a
   meaningful question -- **0 of 35 resolve. All 35 have drifted**, 25 of them
   into the WRONG-ROW bucket. `J 18` and `J 19` both cite `jobs.md` `L428`;
   at most one could ever have been right and neither is -- line 428 is row
   143. The offsets are not constant (`N 99` -> row 24, `M C38` -> `M33`,
   `P C8` -> `B2`, a different section letter entirely), which is what
   distinguishes real document restructuring from a parser artifact.

   **I verified four of the 25 by hand before accepting the count** --
   `network.md` L355 is row 24, `messaging-and-content.md` L427 is `M33`,
   `jobs.md` L428 is row 143, `profile.md` L242 is `B2` -- and all four match.
   Full table, method and the classifier's positive control at
   `_audit/_scratch/_slice-locator-drift.md`.

   **A line number is not a citation.** The corpus already ruled that principle
   for rulings -- `CANONICAL-RULING-ID`: *"every citation resolves to a SYMBOL,
   never to a line number"* -- and this is the same argument for row provenance,
   now with a number behind it. I did not hand-patch `L200` to `L279`: fixing
   one cell makes it correct today, wrong at the next edit, and leaves 34
   siblings broken. **The repair is a locator that resolves to a symbol (the
   row id is already in the adjacent column), and it is a wave, not a cell
   edit.** Note also that no shipped check fails on any of this -- 
   `build_blocker_map.py --check` is green, because a derived view can only
   check its own arithmetic against its input, never whether its input's
   pointers still point anywhere.

5. **`tests/test_job_detail_wiring.py`'s docstring claimed an assertion its body
   does not make.** The missing assertion now exists in the new file, but the
   docstring is still in the wrong file describing coverage it does not have.
   One-line prose repair, not taken here to keep this wave's diff to its subject.

6. **A second false load-bearing claim, found in passing and NOT repaired.**
   `linkedin_open_messaging`'s docstring says the filter click *"is the SECOND
   entry in `readonly.SANCTIONED_MUTATIONS` and the ONLY ONE OUTSIDE
   `writes.perform`"*. Measured at HEAD, the entries outside `writes.perform`
   are `dom.activate_messaging_filter` AND `press.disclose` twice -- three, not
   one. The docstring half-anticipates its own drift (*"and four widenings
   ago"*) but still states the false sentence in the present tense. Same shape
   as row 1: a claim that was true when written, is load-bearing now, and is the
   sentence a reader would cite.

7. **A SHIPPED CHECK THAT FAILS WITHOUT A DEFECT.**
   `tests/test_tracker_readiness.py::test_an_empty_tab_is_not_delayed` asserts
   a wall-clock bound (`waited_ms < 300`) and was measured failing **2 of 3
   runs at clean HEAD** on a box running several waves' suites, reporting
   316ms, 583ms and one pass. `test_click_is_not_its_own_evidence.py::test_the_refusal_says_when_a_matcher_would_have_separated_them`
   is red-then-green the same way. Neither is caused by this wave -- see 5A.1
   for the AST proof and the HEAD baseline. **A check that goes red without a
   defect is worse than no check, because it teaches people to bypass the
   gate**, and this repository's own pre-commit hook carries a comment about
   exactly that habit. Not repaired here: it belongs to whoever owns
   `tracker_readiness`, and the fix is a design question (a relative bound, a
   retry, or a different property) rather than a number to raise.

8. **`metrics_seen` -- DRIVEN AND CLOSED, no residual.** It was the third key
   `described-never-built` named, and the question worth asking of it was
   whether it is a count (safe by construction) or a string. Driven on the
   planted page:

       observed.metrics_seen = 1        type: int
       plant paths in metrics_seen: []

   **It is an integer and a page cannot make it a string** -- the same
   PLAYWRIGHT-TYPED property `plantedpage`'s fidelity rule rests on. It stays
   unread and unbranched-on, which is what its own docstring says it is for,
   and it carries nothing. Its HOST reader carries the plant in seven places,
   but that is already banked and not a new finding:
   `reader_leak_baseline.json` records `dom:read_profile_views_insights` as
   `returns_text`, a deliberate publication.
