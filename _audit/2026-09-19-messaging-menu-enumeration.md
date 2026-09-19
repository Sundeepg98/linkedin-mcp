# Messaging menu enumeration, 2026-09-19

**Owner: the `messaging-measure` wave. Scope: 5 blockers, 19 rows
(17 `CONVERSATION-OVERFLOW-MENU` 10, 50 `MESSAGE-REQUESTS-SURFACE` 4,
67 `PER-MESSAGE-OVERFLOW-MENU` 2, 66 `THREAD-REPLY-BOX` 2,
76 `MESSAGE-REACTION` 1).**

**Messages sent: ZERO. Controls pressed: ZERO. Items clicked: ZERO. Composers
typed into: ZERO. Hovers: ZERO. `/messaging/` loads: THREE.**
**Rows retired: ZERO. Row states changed: ZERO -- section 7 says why that is a
measurement and not a shortfall.**

**CORRECTS:** `_audit/2026-09-05-messaging-rows.md` -- its section 2.2 concludes "the items do not need a press to be counted" from 12 live `role=menuitem` elements, and that does not reproduce: three runs today, two passes each, read 0 menus and 0 menu items on a rendered conversation, so enumerating the overflow menus still requires a press and the rows it would have unblocked are not unblocked.

**HEADLINE.** The predecessor asked for one thing and called it the cheapest open
item in the family: a ruling on reading LABELS on a surface where a label is
routinely a person's name. **This wave built the ruling as a mechanism rather
than a permission** -- labels are classified INSIDE the page and only a term from
a closed vocabulary crosses the boundary -- and then discovered that the surface
it was built for no longer draws the elements it was built to read.

---

## 1. THE MECHANISM: enumerate without any label leaving the browser

`shape._CONVERSATION_ROW` records what a row's accessible name is on this
surface: `Select conversation with <a person>`. **A label here IS a name, by
LinkedIn's own design**, which is why the predecessor would not read one at any
price and why "just read them carefully" was never the answer.

`linkedin_server/menus.py` (`d2144bb`) ships the phrase list INTO the page; the
page returns an INTEGER INDEX per element; Python turns the index into a term.
**The accessible names are never marshalled across the CDP boundary -- not
shaped, not redacted, not present.**

**THE OUTPUT ALPHABET IS CLOSED AND THAT IS THE SAFETY PROPERTY**, structural in
the same sense `groups.py` is: every string the module can emit is a literal
defined in it, and `tally` -- the one function a caller publishes through -- never
takes a label as a parameter, asserted on `inspect.signature`. A filter has to
keep up with whatever LinkedIn serves tomorrow; a closed output alphabet does not.

### 1.1 A defect found before any live run, and what it was NOT

    classify("Star Anise")  ->  term `star`      WRONG, and it had shipped

The vocabulary already excluded a bare `mark`, because a given name can be a UI
verb. `star` walked in through the same door: the hazard had been treated as a
property of one WORD rather than of **every single-word term**. **A NAME ADDS
TOKENS**, so a single-word phrase must now match the WHOLE label while multi-word
phrases may still be contained.

**It was a COUNTING error and could not have been a DISCLOSURE one** -- the wrong
branch emitted `star`, the module's own literal. That is precisely why the closed
alphabet sits underneath the vocabulary instead of the design resting on the
vocabulary being right.

### 1.2 The parity control, because the matcher now exists twice

The rule lives in Python and, by hand, in the probe's JavaScript. The probe's
first act on the page is to run its OWN corpus through the JavaScript and compare
every verdict with Python's, refusing to report any classification on a
divergence. **Live: corpus 26, disagreements 0**, on all three runs.

---

## 2. THE READING, and it is stable

`scripts/_probe_messaging_menu_enumeration.py` (`b66ec34`) and
`scripts/_probe_messaging_hidden_controls.py` (`30339cf`, `26286aa`).
Runs at 08:41, 08:44 and 09:20 by the box. Transcripts in `_audit/_scratch/`.

Preconditions, read off `/feed/` before every spend, refusing otherwise:

    messaging new_since_last_visit=0 state='read'   invitation pending=0 state='read'
    redirected into a conversation: True
    elements 1220   settle 'rendered_no_baseline'   CONTROL button 50

| selector | 2026-09-05 | 2026-09-19 |
|---|---:|---:|
| `role=menu` | 4 | **0** |
| `role=menuitem` | 12 | **0** |
| `aria-label*="React"` | 12 | **0** |
| `button[aria-expanded]` | 31 | **24** |
| `aria-expanded="true"` | not stated | **0** |

**Two passes with a 3s settle between them, and nothing moved.** That is the
render gate applied to a menu instead of a tab: a single pass cannot separate
"LinkedIn does not draw this" from "LinkedIn had not drawn it YET", and those two
answers retire opposite sets of rows.

### 2.1 The zeros are not reported as absence, and one cheaper cause was ruled out

A CSS attribute substring match is CASE-SENSITIVE on its value, and the
predecessor recorded that exact trap on this surface. So the second probe repeats
every label selector with the CSS `i` flag and counts each twice -- total, and how
many are not displayed:

    label ~ react (i)      total 0   hidden 0
    label ~ reaction (i)   total 0   hidden 0
    label ~ emoji (i)      total 0   hidden 0
    label ~ delete (i)     total 0   hidden 0
    label ~ archive (i)    total 0   hidden 0
    label ~ request (i)    total 0   hidden 0
    hidden="true"          total 89  hidden 38    <- the firing control
    CONTROL button         total 50  hidden  6

**THE HIDDEN COLUMN IS THE CONTROL AND IT FIRED.** 6, 38 and 1 are non-zero, so
the not-displayed detector is alive; that is what makes `react total=0 hidden=0`
mean "NOT IN THE DOM AT ALL, case-insensitively" rather than "present but my
visibility test broke".

So three candidate causes reduce to one: **the control does not exist in the
document until an interaction creates it.** Hover-injection fits the
predecessor's twelve. A static read cannot separate hover-injection from "not
drawn on this conversation", and this document does not claim to have.
**Row 76 must not be retired on this zero.**

### 2.2 The 12-versus-12 question: instrument built, inputs gone

The predecessor declined to spend one observation twice, correctly: an equal
count is a correlation and not an identity. The probe therefore intersects the
two sets **AS ELEMENTS** in the page. It returns `A 0, B 0, shared 0`. **The
instrument works and its inputs no longer exist**; whoever next sees a page that
draws them gets the answer for one page load.

---

## 3. WHAT ACTUALLY BLOCKS THESE ROWS

The triggers are present -- 24 collapsed, none expanded. So the blocker is no
longer "nobody has looked". **It is a press this package does not sanction.**

### 3.1 The precedent for sanctioning it is this repository's own

`readonly.SANCTIONED_MUTATIONS` already carries a READ-PATH CLICK,
`("linkedin_server/dom.py", "activate_messaging_filter", "click")`, whose in-line
argument is exactly the one needed here: *"A pill SENDS NOTHING and CHANGES
NOTHING on LinkedIn's servers; it alters which rows are displayed. Counted by
EFFECT rather than by verb ... a view filter is a read."*

**I did not add an entry.** The file is contended by two live waves; a widening
needs its digest RECOMPUTED rather than overwritten; and decisively, **a menu's
CONTENTS are unknown in a way the seven filter pills are not.** The pill sanction
is safe because `dom.MESSAGING_FILTERS` is a closed set matched before any
selector is built. An overflow menu is a plausible home for `Delete`.

**THE PROPOSAL, so the next wave does not re-derive it:** a fourth entry
`("linkedin_server/dom.py", "open_overflow_menu", "click")` where (1) the TRIGGER
is chosen from a closed set, (2) contents are returned through `menus.tally` so no
label can come back, (3) the function **takes no item argument at all**, so
activating an item is structurally impossible rather than merely not done, and
(4) it closes what it opened and re-reads `aria-expanded` at both ends. Cost: one
digest recompute, tests shown failing, one page load. Pay-off: **13 of these 19
rows.**

### 3.2 Two boundary facts found on the way, both VERIFIED-BY-INSTRUMENT

**(a) THE MUTATION SCANNER HAS NO `hover` CLASS.**

    readonly.scan_source_for_mutations("await page.hover(..)\nawait loc.hover()") -> []

and the instrument is not mute -- the same scanner over this wave's probe returns
`[(313, 'evaluate'), (478, 'evaluate')]`. **So the single measurement that would
most advance rows 67 and 76 is the one the boundary would not refuse.** It would
pass the letter of the check while routing around its intent, which is the scar
this package already carries. Not used. **Whether `hover` belongs in that tuple is
a ruling somebody should make deliberately rather than discover.**

**(b) THE SCANNER COVERS `linkedin_server/*.py` AND NOT `scripts/`**
(`tests/test_readonly.py:21`, 31 modules). The much-quoted guarantee that this
package holds "exactly two calls that can change anything on LinkedIn" is **a
guarantee about the package, not about what this repository's own probes can do
to a live signed-in account.** That reframes the predecessor's refusal to press as
a VOLUNTARY discipline rather than an enforced boundary -- which deserves more
credit than it has had, and is one careless probe away from being lost with no
test going red.

Both of this wave's probes were therefore scanned BY HAND: two `evaluate` calls
and one `evaluate` call respectively, and **no other interaction verb** -- no
click, fill, press, hover, `.mouse` or `.keyboard`.

---

## 4. ROW 50 `MESSAGE-REQUESTS-SURFACE` -- the button-side census the predecessor asked for

Its hand-off: *"The next cheapest is NOT an href census ... If row 50's surface
exists, that is where it is [drawn as a button]."* That census is now taken. All
50 buttons:

    compose 1   filter 6   overflow_trigger 1   message_requests 0
    no_label 4  unmatched 38

**Two independent mechanisms now read zero** for a message-requests destination on
this surface -- their href census and my button census -- joined by
`label ~ request (i) total 0`.

**WHAT MUST NOT BE CONCLUDED.** 38 of 50 are unmatched, so a requests control
wearing a label the vocabulary lacks is invisible to me. **A vocabulary zero is a
fact about the vocabulary.** What the shapes report:

    1-8 chars   1 token   capitalised    7
    9-20 chars  2 tokens  capitalised    2
    9-20 chars  3 tokens  capitalised    4
    41+ chars   13 tokens not capitalised 7

The 2-and-3-token capitalised runs are the shape of a person's name -- which is
what a conversation row's accessible name is -- and the 41+/13-token entries are
sentence-shaped message previews. **The surface reporting what it contained
without reporting who is on it** is the whole point of the shape branch.

**Row 50's `allowlist +1` remains a measured PLACEHOLDER FOR AN UNKNOWN**, and I
added no pattern: after two waves and two mechanisms **nobody has named an address
for it to admit**, and writing a speculative pattern would invent the address the
entry exists to have found.

---

## 5. ROW-BY-ROW

| blocker | rows | classification | evidence |
|---|---:|---|---|
| 17 `CONVERSATION-OVERFLOW-MENU` | 10 | MEASURE-BLOCKED on an unsanctioned press | triggers 24, items 0, stable x3 runs |
| 67 `PER-MESSAGE-OVERFLOW-MENU` | 2 | MEASURE-BLOCKED on a press; hover-suspect | same, plus s2.1 |
| 76 `MESSAGE-REACTION` | 1 | MEASURE-BLOCKED, hover-suspect. **Do not retire on my zero** | React 0 today vs 12 on 09-05 |
| 66 `THREAD-REPLY-BOX` | 2 | ALREADY ANSWERED by the predecessor; I add nothing | its s2.1 |
| 50 `MESSAGE-REQUESTS-SURFACE` | 4 | UNKNOWN; the `+1` is a measured placeholder | s4 |

---

## 6. INSTRUMENTS ADMITTED, each shown failing first

* `linkedin_server/menus.py` -- closed-alphabet menu enumerator. 57 tests,
  **six mutations each shown KILLING a test**, every mutation diff-confirmed to
  have applied before its run counted, module restored from a pre-mutation COPY
  and verified byte-identical after each.
* `scripts/_probe_messaging_menu_enumeration.py` -- in-page classification,
  element-identity intersection, parity control, two-pass render gate.
* `scripts/_probe_messaging_hidden_controls.py` -- absent versus merely
  invisible, with the not-displayed detector's own firing control.

One non-kill is recorded rather than smoothed: the single-word containment
mutation does not turn the `mark` case red, because `mark` was never a
single-word phrase. That case's safety comes from a DIFFERENT layer -- the
vocabulary's deliberate omission -- and both layers now have their own test.
**A mutation that fails to kill a test is a different result, not a weaker one,
and it is about the test.**

---

## 7. WHAT I DID NOT DO

* **No press, hover, click, type or send.** Section 3.
* **No boundary change.** `readonly.py` untouched: no allowlist entry, no
  denylist entry, no digest recomputed, no `SANCTIONED_MUTATIONS` edit.
* **NO CENSUS ROW-STATE EDIT, and this is a measurement rather than a
  shortfall.** Nothing measured MOVES a row: 17/67/76 stay GAP with a
  better-characterised blocker, 50 stays GAP, and 66 was answered by somebody
  else whose retirement is theirs to claim. Editing states to show activity is
  the retirement-is-not-coverage error. Decisively,
  `_audit/2026-09-05-messaging-rows.md` section 3a establishes that **nobody can
  name which row ids sit behind six of these seven blockers**, so a state edit
  would be applied to rows chosen by reconstruction. **A state change nobody can
  address to a row is worse than none.**
* **NO WRITESPEC**, and it follows from section 3 rather than being a separate
  decision. 16 of these 19 rows are writes whose TARGETS I cannot enumerate. A
  spec for "delete a conversation" written without having seen the menu is a spec
  against an IMAGINED DOM -- the exact scar `RECIPIENT_CHIP_SELECTORS` already
  carries, having never matched anything on any real page. Writing five more with
  confident consent text would manufacture the appearance of coverage over the
  same void. What is settled and needs no re-derivation: the shipped model is two
  calls behind a single-use, action-bound, target-bound token with a 120s TTL;
  twelve shipped writes meet it; the bar is neither to be raised per-capability
  nor lowered; and `writes._NINE_REFUSALS` is measured shut and must not be
  routed into. **The blocking input is the enumeration, which is section 3.1.**

  **BUT ONE OF THE SIXTEEN IS NOT BLOCKED, AND IT IS THE ONE WORTH WRITING
  FIRST.** Row 66's two writes are the exception to everything in this bullet,
  because their DOM has actually been measured -- by the predecessor, twice, with
  two independent readers:

      recipient_boxes  0     <- a thread has nobody to choose
      editors          1     contenteditable
      send_controls    1
      send_disabled    True  <- on an empty box

  A reply into an existing thread is therefore **ADDRESSLESS** -- there is no
  recipient to commit, which is exactly the step that makes the rest of this
  surface unmeasurable by any read -- and the disabled-on-empty Send is the
  transition signal `publish_post` and `send_message` already gate on, so a fill
  that lands is observable without reading what was typed. The census calls the
  addressless-reply route the most job-hunt-relevant messaging action in all 761
  rows.

  **So the honest split of the write half is 14 blocked and 2 available**, and
  the two available ones need no menu, no press and no hover. I did not write
  that spec -- it belongs in `writes.py` beside the twelve shipped writes, it is
  the most safety-critical file in this package, and starting it in the last
  forty minutes of a session is how a gate gets written that nobody re-reads.
  **It is the first thing to pick up, and it starts from a measured DOM rather
  than an imagined one, which is the whole difference.**
* **The full suite was not run** (29 minutes). Run: `test_readonly.py` +
  `test_readonly_boundary_invariant.py` (249 passed), `test_menus.py` (57
  passed), the taint guard, and the tracked-file identity sweep after every
  staging.
* **One account, three loads, one conversation LinkedIn chose.** Every count here
  is a sample of one conversation.

---

## 8. PROVENANCE

    d2144bb  linkedin_server/menus.py                      368 ins
    30339cf  scripts/_probe_messaging_hidden_controls.py   194 ins
    36c250c  tests/test_menus.py                           451 ins
    26286aa  the boundary reduction on the hidden probe     78 ins / 18 del
    b66ec34  scripts/_probe_messaging_menu_enumeration.py  590 ins
    + the commit carrying this document.

    AI attribution    0 across every commit, verified with
                      git log origin/master..HEAD --format=%B | grep -ci co-authored
    identity sweep    run AFTER every staging, per the gate-time rule.
                      PASS 0 hits at 391, 396 and 397 files.
    taint guard       both of this wave's probes CLEAN. Three files remain
                      flagged and all three are other waves'.
    commits           every one via `git commit --only -- <path>`, against an
                      index READ immediately before. That mattered once: at the
                      test-file commit the index carried FOUR of a neighbour's
                      files, staged between two of my own readings; `--only`
                      kept them out and they were still staged afterwards.

**A known imprecision in a commit message, recorded rather than rewritten.**
`b66ec34`'s body cites the scanner result as `[(313, 'evaluate'), (437,
'evaluate')]`; the taint reduction moved the second call and the true current
reading is line **478**. The claim it supports -- two evaluates and no other
interaction verb -- is unchanged. History is not rewritten in a multi-writer tree
for a stale line number.

**One instrument in this wave was built by a delegated slice** (`tests/test_menus.py`
and the boundary reduction in the enumeration probe). It **flagged a real
person's full name in a fixture that had come from my own spec**, and asked for
sign-off. The sign-off was the wrong remedy: a tracked file may not carry a third
party's name even as an illustration, and **removal beats declaration, because a
declaration permanently widens what the identity guard tolerates.** The name was
removed from the module, the probe corpus and the tests; the module's worked
example is a spice now. The renamed fixtures were then re-verified SENSITIVE --
with the single-word rule mutated back to containment both go red, and both go
green on a byte-identical restore -- because a renamed fixture that was never
re-checked is a test nobody has run.

The rewritten enumeration probe was verified behaviour-preserving by running it
live and diffing: **byte-identical to the pre-rewrite transcript**, which also
makes that the third independent run of the same measurement.
