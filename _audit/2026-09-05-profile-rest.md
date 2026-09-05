# profile-rest -- the eight rows two waves handed over

Wave window **19:35:07 -> 20:30 BY THE BOX** (`date`, +0530). Every timestamp
here was taken with `date`. My own sense of elapsed time ran **~18 minutes
fast** at the one point I checked it against the box -- the clock law biting a
third agent, at a third magnitude (company-page ~113 min, the lead ~25 min,
this wave ~18 min). It is not a property of one agent.

    19:35:07   wave start, clock measured
    19:38:42   first live run, both surfaces read
    19:39:24   clock re-measured; the taint engine named its own hit
    19:41      second live run, fresh process, reproduced exactly
    19:45      probe committed  707583b
    19:49      test committed   79e126b

## WHAT THIS WAVE MOVED

| row | blocker | ledger | what happened |
|---|---|---|---|
| 43 | `BADGES-SURFACE` | 5 rows, 2R/3W, allowlist +1 | **MEASURED LIVE at allowlist +0. The `+1` is refuted for both R rows. One of the five rows is a DUPLICATE.** |
| 72 | `MULTILANG-PROFILE` | 2 rows, 1R/1W, allowlist +1 | **MEASURED LIVE at allowlist +0. The `+1` is refuted for the R row.** |
| 78 | `OPEN-PROFILE-SETTING` | 1 row, 1W, allowlist +1 | **NO PATTERN WRITTEN, DELIBERATELY. The row names no address. The trap was converted into an asserted invariant instead.** |

**No row is RETIRED by this wave.** Two boundary costs are refuted with a live
measurement, one duplicate is found, and the settings trap is held shut by a
test rather than by an accident. Nothing was pushed. No write was designed,
gated or fired.

---

## 1. THE HEADLINE: both `allowlist +1` charges are refuted, and it cost zero boundary

A boundary cost written into a ledger row is a **hypothesis about what blocks
the row**, not a unit of work. The `profile-modals` wave established that
shape this afternoon by declining a `denylist x1` it was assigned, on the
grounds that the entry it was told to narrow matched nothing. This is the
same finding on the other side of the ledger: **an `allowlist +1` charged
against a surface that is already drawn on an admitted address.**

`/in/me/` is on `readonly._ALLOWED_URL_PATTERNS`. Both of row 43's READ rows
and row 72's READ row are read off it. I added no address, wrote no pattern,
and recomputed no digest, **because I changed nothing** -- which is a stronger
statement than a re-pin and is checkable in one command.

### The measurement, reproduced in two processes

`scripts/_probe_badge_and_language_affordances.py`, run twice, `707583b`.

    CONTROL PAGE  /mypreferences/d/dark-mode   (admitted; draws neither surface)
      controls 20   text_length 507   distinct_langs 1
      needle dark                            1     <- MUST FIND
      needle top voice                       0
      needle profile language                0
      needle zzq_no_surface_draws_this       0     <- MUST BE ABSENT

    HIS OWN PROFILE  /in/me/      read 1        read 2
      controls                       235           235
      text_length                   9089          9089
      lang_nodes                       1             1
      distinct_langs                   1             1
      langs_other_than_document        0             0
      needle top voice                 0             0
      needle verified                  4             4
      needle verification              0             0
      needle premium                   0             0
      needle another language          0             0
      needle profile language          1             1
      needle add profile in another language  0      0
      needle zzq_no_surface_draws_this 0             0

**Four readings of `/in/me/` across two processes, every number identical.**

### The control gated in both directions, which is what makes a zero worth anything

`dark` read **1** on the control page and `zzq_no_surface_draws_this` read
**0** on every page. So a working reader and a dead aim are distinguishable on
this instrument, and the report is not printed at all if the must-find needle
reads 0. That check exists because `CENSUS_CONTROL_SELECTOR` shipped in this
repository aimed at a role that did not exist, certified nothing, and looked
green throughout.

**And the zeros are not uniform, which is the second half of the argument.**
`verified` reads 4 and `top voice` reads 0 **on the same page, through the
same reader, in the same call**. An instrument that returned the same answer
for every input would be reporting its own shape; this one disagrees with
itself across needles.

### THE COUNT SETTLED, AND THAT CORROBORATES THE MODALS WAVE RATHER THAN ADDING TO IT

`profile-modals` measured `/in/me/` at 67, then 80, then 235 census controls
in one process with nothing pressed and nothing navigated, and established by
a spaced series that **235 is the settled value and the earlier numbers are
pre-hydration reads**. My probe waits 2500ms after `domcontentloaded` and read
**235 on the first read, four times out of four.** That is an independent
confirmation of its remedy -- *make the reader wait* -- taken with a different
reader on a different day's session. I am claiming corroboration of ITS
finding, not a finding of my own.

---

## 2. ROW 43 `BADGES-SURFACE` -- what the five rows actually are, and one of them is counted twice

The ledger says 5 rows, 2R/3W. Matched to the census, they are:

| census | capability | R/W |
|---|---|---|
| K8 | Top Voice blue badge on the profile | R |
| K10 | Verification badge as it appears on job posts | R |
| K9 | Show / hide the Top Voice badge | W |
| B8 | Top Voice badge show / hide | W |
| B9 | Premium profile badge show / hide | W |

### B8 AND K9 ARE THE SAME CAPABILITY, IN TWO CENSUS BLOCKS

    B8 | Top Voice badge show / hide | W | GAP | a1577365; no tool, no reason
    K9 | Show / hide the Top Voice badge | W | GAP | a1577365; no tool, no reason

Same Help Center article id, same R/W, same state, same note text, same words
in a different order. **This is a duplicate, and the lead's own arithmetic
rule says what it costs: a duplicate inflates BOTH the numerator and the
denominator**, because the census builds 761 from the same table rows as 409.
Four duplicates were subtracted from the numerator and never from the
denominator earlier today; two more were found after. This is a seventh.

**Row 43's honest size is 4 rows, 2R/2W, not 5 rows 2R/3W.** I am not editing
the ledger -- three waves have committed to it today and its re-costing is the
lead's -- I am recording the measurement against it.

### The `allowlist +1` buys nothing for either READ row

* **K8 is read on `/in/me/`.** Admitted. Measured above.
* **K10 is read on `/jobs/view/<id>`.** Admitted, and already loaded by
  `linkedin_job_detail` -- this is the same route the `company-page` wave used
  this afternoon to move three rows off a posting's About card at zero
  boundary cost.

### The three WRITE rows are not blocked by the allowlist either

They are blocked by a **ruling that already exists**. `/mypreferences/d/verifications`
is a page below the settings index, and census block K states the
settings-family ruling reaches it -- which is why K1 through K7 are
EXCLUDED-RULED while K8/K9/K10 sit as GAP. The operator's shipped settings
ruling (`server.py:6874`) is *a setting is admitted by name or not at all*.

**So no part of row 43 is waiting on an allowlist pattern.** The reads need
none; the writes need an operator ruling, which is a different instrument.

### WHAT THE READING SAYS ABOUT K8, STATED AS NARROWLY AS IT DESERVES

`top voice` reads **0** on his profile, four times, through a reader that
found `verified` at 4 on the same page and `dark` at 1 on a control page.
The natural reading is that **no Top Voice badge is drawn on this account.**

**AND HERE IS THE DEFECT IN MY OWN INSTRUMENT, WHICH I FOUND BY ASKING WHAT
THE READER CANNOT SEE.** The needle is matched over `document.body.innerText`.
**`innerText` excludes `alt` attributes and `aria-label` values.** A badge is
exactly the kind of thing drawn as an icon carrying an accessible name and no
text node. So:

> A zero from this instrument is a fact about the page's TEXT, not about the
> page. If LinkedIn draws the Top Voice badge as an icon with an aria-label,
> this probe reads 0 and is wrong.

That is the single-aim caveat the contact-info probe declared, arriving in a
different form on a different surface. It costs nothing on the three needles
that read non-zero, and it is the whole of what is owed on K8: **the next
reading of this row should aim at accessible names, not at text.** I did not
take it.

---

## 3. ROW 72 `MULTILANG-PROFILE` -- the affordance is drawn, the content is not

Census D27 (W, create / delete a secondary-language profile) and D28 (R, view
a profile in multiple languages). 1R/1W, and both cite `a541878`.

    needle profile language                  1     on /in/me/, four times
    needle another language                  0
    needle add profile in another language   0
    distinct_langs                           1
    langs_other_than_document                0

**Two separable claims, and I am making both narrowly.**

1. **The phrase naming this capability renders on an admitted address.** So
   D28's `allowlist +1` is refuted the same way row 43's is. Whatever reads
   this row does not need a new address.
2. **Nothing on the page declares a language other than the document's.**
   `distinct_langs 1`, `langs_other_than_document 0`. That is a purely
   structural reading carrying no text at all, and it is consistent with him
   having **no secondary-language profile**.

**WHAT I DID NOT ESTABLISH, and the gap matters.** A word-boundary hit on
`profile language` proves the PHRASE renders. It does **not** prove a
pressable control exists, and I did not press anything. The `profile-modals`
wave's aim reader is the right instrument for that next step -- *named is not
pressable* -- and its finding on the neighbouring `open_to` control is the
reason to use it: three of five named controls carried an activation relation,
so a press there would have been **a guess wearing a selector**. I declined to
guess here for the same reason.

**The `another language` needle reading 0 while `profile language` reads 1 is
itself a result**: the Help Center article's wording (`Add profile in another
language`) is **not** what this account's page draws. A wave aiming at the
article's phrasing would have measured a clean zero and concluded the
affordance is absent.

---

## 4. ROW 78 `OPEN-PROFILE-SETTING` -- I wrote no pattern, and that is the deliverable

The brief offered a fork: write a narrow anchored settings pattern with an
asserted close-account exclusion, or build the reads and hand the setting
back. **I did neither, because measuring first dissolved the fork.**

### The row names no address at all

Census `P B10`, `profile.md:226`:

    | B10 | Open Profile setting (who may message without connecting) | W | GAP | a541684; no tool, no reason

The evidence column holds a **Help Center article id and nothing else**. The
freeze file already records this for all seven settings rows: *not one of the
eight rows names an in-product address, so the `allowlist +1` charged against
each is not a unit of work; it is a placeholder for an unknown.*

**There is no pattern to write, because there is no address to admit.** A wave
that discharged its assigned boundary cost without checking would have widened
the allowlist toward a surface whose address nobody has.

### What I built instead, and why it is worth more than the pattern would have been

`close-account` is refused **by no pattern matching it**, not by any denylist
entry. I measured that directly against the shipped predicate at 19:47 rather
than taking it from the freeze file:

    /mypreferences/d/close-account       False
    /mypreferences/d/close-account/      False
    /psettings/close-account             False
    /mypreferences/d/verifications       False
    /badges/profile/create               False
    /mypreferences/d/dark-mode           True
    /in/me/                              True

    allowlist patterns   29        forbidden substrings   33

**Note the allowlist reads 29, where the freeze file's last entry records 28.**
A pattern landed after that entry was written. I am not adjudicating whose --
recording it so the next wave computing a digest does not derive `new` from a
stale `old`, which the freeze file says has already gone wrong once.

The refusal of account deletion is **an accident of the allowlist's shape**.
Nothing asserts it, nothing would notice if it changed, and the family-shaped
pattern that discharges seven settings rows at once would admit it silently,
with nothing in the diff naming it.

**So the highest-value thing on this row is not a pattern. It is a test that
turns that accident into an invariant**, and it is owed whether or not anybody
ever writes the pattern. That slice is `tests/test_the_settings_boundary_refuses_account_deletion.py`
-- see section 6 for its state at freeze.

---

## 5. THE TAINT GUARD WENT RED ON MY PROBE, AND THE DIAGNOSIS IS NEW

    scripts/_probe_badge_and_language_affordances.py   0 -> 1
    test_no_file_prints_page_text_beyond_its_pinned_inventory   1 failed, 251 passed

Running the guard's own engine over the file named the cause in one call, and
it is **not** the mechanism the two prior instances had:

    tainted names: ['NEEDLES', 'probe_count', 'probe_word', 'raw', 'slot', 'tally']

**`NEEDLES` is a tuple of literals I wrote in that file, and it is tainted.**
Not because anything from the page was assigned to it -- because it is passed
**INTO** `page.evaluate`. The engine follows the binding, not the content, and
it is right to. Taint then flowed `NEEDLES -> probe_word -> probe_count` and
reached a print of two integers.

The two prior instances (`196394d`'s `before`/`after`, the contact-info
probe's `key`/`value`) were both **outputs** of a page call tainting a name
reused elsewhere. **This one is an INPUT.** A file can be red because of a
constant it authored itself, and no rename of a page-derived local reaches it.

**THE FIX: the page-call path and the printing path may not share a name.**
The vocabulary is defined twice -- `NEEDLES` crosses into the page,
`REPORT_LABELS` never does. The engine's verbatim output is quoted at the
constant so the next reader does not collapse them back as duplication.
Guards after: **252 passed.**

### The fix bought a new failure mode, and I held it shut before shipping

Two independent tuples can drift, and the same fix replaced two needle NAMES
with two INDICES. **A wrong name raises `KeyError` on the first run. A wrong
index does not raise** -- it reads a different needle, and because most needles
legitimately read 0 on the control page, an off-by-one on the must-be-absent
index reports a healthy gate over a **disarmed control**. That is this
repository's recurring shape arriving inside my own remedy.

`tests/test_badge_and_language_affordances.py` (`79e126b`), **shown failing
under two mutations before admission:**

    MUST_BE_ABSENT_AT 8 -> 7      2 failed, 4 passed
    REPORT_LABELS drift by one    1 failed, 5 passed
    restored                      6 passed

The detector is factored out as `_same_sequence` and fed a deliberately-wrong
pair by its own test, so a green cannot be green because the comparison is
inert.

---

## 6. WHAT I DID NOT DO

* **No row is retired.** Eight rows were handed to me; **zero** are closed.
  Two boundary charges are refuted and one duplicate is found, which changes
  what the rows COST, not whether they are done.
* **No allowlist pattern was written and no boundary digest was recomputed**,
  because nothing this wave did touches `readonly._ALLOWED_URL_PATTERNS`.
  There is no chain step to append.
* **No write was designed, gated or fired** on any of the eight rows. Row 43's
  two remaining W rows and row 72's one W row have no WriteSpec, and row 78
  still has none.
* **I pressed nothing.** No control on either surface was activated. The
  `profile language` hit proves a phrase renders, not that a control exists.
* **K8's reading is text-only.** `innerText` excludes `alt` and `aria-label`,
  so a badge drawn as an icon would read 0 through this instrument. Section 2
  states this as a defect rather than a caveat, and the re-read is owed.
* **K10 was never read.** I argued from the address that a verification badge
  on a job posting needs no allowlist entry; I did not open a posting to look.
  That is an argument, not a measurement, and it is labelled as one.
* **The probe was NOT admitted to any instrument register.** It has been shown
  able to report an absence in both directions, which is the bar for believing
  this run, but it has a declared blind spot (accessible names) and an
  instrument with a known blind spot should not be registered for reuse until
  that is fixed.
* **The full suite was not run and no clone was taken.** Targeted runs clear
  SHAPE violations, never ENUMERATION violations -- if this probe or this test
  file should have been enrolled somewhere by name, no run scoped to these
  files could tell me. See section 7 for what did run.
* **I did not edit the ledger or the census**, including the duplicate in
  section 2. Both files were contended today and the re-costing is the lead's.
* **Nothing was pushed.**

## 6b. THE BADGE OBLIGATION WAS NOT DISCHARGED, AND MY PAIR IS THE REASON

The brief required `read_invitation_badge` before and after any load. Both
runs printed:

    BEFORE   {'links': 0, 'badge_links': 0, 'label': None}
    AFTER    {'links': 2, 'badge_links': 1, 'label': 'My Network, 0 new notifications'}

**That pair does not discharge the obligation, and reporting it as though it
did would be worse than not taking it.** The BEFORE reading was taken on a
freshly-created page **before any navigation** -- there was no LinkedIn
document to read, so `links 0` is a fact about a blank tab. The pair is not
before-and-after of one instrument; it is *no page* against *a page*.

The honest residue: **where the badge could be read at all, it read `0 new`**,
and no counter is observed moving. But *a reading no instrument can fail is
not a reading*, and half of this pair could not have failed. **The fix is one
line -- take the BEFORE reading after the first navigation, not before it --
and I am recording it rather than silently claiming the check.**

## 7. WHAT RAN, AND ITS EXACT SCOPE

    tests/test_page_text_is_never_printed.py       ]
    tests/test_navigation_is_never_derived.py      ]  252 passed  (after the fix)
    tests/test_badge_and_language_affordances.py      6 passed, and 2 mutations shown red
    scripts/sweep_tracked_for_identity.py             PASS 0 hits / 342, then 343

The sweep was run **immediately before each commit**, never once at the start.
It moved 342 -> 343 files between my two commits, which is this session's
standing finding about that instrument holding at a one-wave scale.

A broader run of the enumeration-risk guards -- the two taint guards plus
`test_no_committed_identity.py`, `test_a_sanitiser_earns_its_entry.py` and
`test_readonly.py` -- returned **1 failed, 958 passed in 40.17s**.

### THE ONE RED IS NOT MINE, AND I CHECKED RATHER THAN ASSUMED

    tests/test_a_sanitiser_earns_its_entry.py::test_every_claimant_of_a_sanitiser_name_is_enrolled
    AssertionError: these functions claim a _SANITISERS name and are not
    enrolled: [('_probe_premium_entitlement.py', '_relation')]

    owner, by path:  ae469cc  measure(premium): the admitted door opens ...

Two checks, neither of them a guess. My probe contains **zero** occurrences of
`_relation`, `_redact` or `_sanit` -- it defines no sanitiser and claims no
name, so it cannot be a claimant. And the owner is named by
`git log --oneline -3 -- <path>`, which is the only thing that names an owner
here; not the agent name, not the surface name.

**AND THE FREEZE FILE'S LIST OF CLAIMANTS IS STALE.** It names four
unenrolled claimants -- the two groups probes, the uploads probe and the
newsletter probe. All four are now enrolled, and the sole survivor is a
**fifth** that entry does not mention. Anyone triaging this red from the
freeze file alone will go looking for four files that are already clean.

**Do not clear it by widening the name pin.** The freeze file is explicit that
adding a name to a list to turn a test green is the exact thing the enrolment
half exists to prevent -- `_redact` was once admitted on the strength of its
NAME and carried no slug rule at all. It is one line, owed by one owner.

## 8. COST, RECOMPUTED RATHER THAN RECALLED

Derived from the probe's own control flow, not from memory. **Three loads per
run** -- one control page, then `/in/me/` twice:

    /mypreferences/d/dark-mode, /in/me/, /in/me/

    run 1  19:38   3 loads   completed
    run 2  19:41   3 loads   completed
    -----------------------------------------
    TOTAL          6 page loads, 0 presses, 0 writes

One tab per run, opened and closed. `page.is_closed()` read **True** on both
runs -- a presence reading about the one object each run created, not a count
over a pool a dozen waves share. The PAGE was closed, never the context.
