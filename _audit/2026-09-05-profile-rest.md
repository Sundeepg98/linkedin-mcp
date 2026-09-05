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
| 43 | `BADGES-SURFACE` | 5 rows, 2R/3W, allowlist +1 | **BOTH R ROWS MEASURED LIVE at allowlist +0** -- K8 on his profile, K10 on a live job posting. The `+1` is refuted for both. **One of the five rows is a DUPLICATE.** |
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
different form on a different surface.

> **SUPERSEDED, four paragraphs down, before this document was pushed.** The
> sentence that stood here read *"the next reading of this row should aim at
> accessible names, not at text. I did not take it."* I then took it, in
> `b88211b`, and **the defect fired.** No `CORRECTS:` marker: a marker naming
> the file it lives in resolves zero documents and turns the suite red, and a
> reader who reaches this line has already reached the correction. The pointer
> is here rather than at the foot of the file because this is where the stale
> claim gets read.

### I TOOK THE READING, AND THE BLIND SPOT WAS REAL

A second corpus was added -- `aria-label`, `alt` and `title` only -- reported
**separately** from the text corpus so the two can disagree in one place
rather than being averaged into one number.

    needle                             TEXT   NAMES
    dark                                  0       0
    top voice                             0       0
    verified                              4       5
    verification                          0       0
    premium                               0      19
    another language                      0       0
    profile language                      1       1
    add profile in another language       0       0
    zzq_no_surface_draws_this             0       0

    name_nodes 167   names_length 4606   (identical on both reads)

**`premium` reads ZERO in text and NINETEEN in accessible names.** The blind
spot I declared was not hypothetical, and a wave that had trusted the text-only
reading would have reported that word absent from a page carrying it nineteen
times.

**AND THIS IS WHAT MAKES THE `top voice` ZERO WORTH SOMETHING NOW.** It stays
**0 in both corpora**. The pair has been *shown able to disagree* -- on this
very page, in this very call -- so its agreement is evidence rather than a
coincidence of one aim. K8's reading survives a strictly stronger instrument:

> **No Top Voice badge is drawn on this account, in text or in accessible
> names.**

This is the day's own law arriving in my favour for once: *agreement between
two instruments sharing a defect is not corroboration; disagreement between
two NOT sharing one is the cheapest signal available.* Here both happened in
one table, and the disagreement is what licenses the agreement.

**The residue, and it is smaller than what it replaced:** accessible names
still do not cover an image with no `alt`, or a badge conveyed by shape alone.
That is a narrower hole than "all non-text content" and I am not claiming it
is closed.

---

## 2b. K10 WAS AN ARGUMENT. IT IS NOW A MEASUREMENT.

This document said, in section 6, that I argued K10 from the address and did
not open a posting. **I opened one** (`9d89134`), and the reading changed what
I would have concluded.

### First, the address, measured rather than recalled

    /jobs/view/<id>/           True
    /jobs/view/<id>            True
    /jobs/view/<id>/?refId=x   FALSE

**The bare spelling is admitted, so `allowlist +0` holds for K10.** But the
QUERY-BEARING spelling is refused, and **LinkedIn's own job links routinely
carry `refId` and `trackingId`** -- so a url copied off a listing verbatim
does not pass. That is not a blocker for this row; it is a trap for whoever
builds the reader, and it is the same shape as the messaging-root reasoning
already written into `_ALLOWED_URL_PATTERNS`. I would have missed it entirely
had I only checked the one spelling I expected to use.

### The reading, on a live posting, reproduced in two runs

    on the job posting          TEXT   NAMES
    top voice                      0       0
    verified                       0       1
    verification                   1       0
    premium                        1       9

    controls 163   text_length 16437   name_nodes 93   names_length 2329
    (identical across both runs; must-be-absent 0)

**`verified` reads ZERO in text and ONE in accessible names.** So a
verification marker IS present on this posting, and **the text-only reader
this probe shipped with two hours ago would have reported it absent.**

> **THE BLIND SPOT I DECLARED AND FIXED HAS NOW FIRED ON TWO DIFFERENT
> SURFACES WITHIN THE HOUR** -- `premium` 0-to-19 on his profile, `verified`
> 0-to-1 on a job posting. It was not an edge case, and declaring it without
> fixing it would have shipped two wrong readings with a caveat attached.

**And the two corpora disagree in the OTHER direction on the same page**:
`verification` reads 1 in text and 0 in names. Neither corpus dominates, which
is exactly why they are reported side by side and never summed. A single
merged number would have hidden both disagreements.

**What this does NOT establish.** One posting, chosen because it is the only
job saved on the account -- so this is a sample of one, and a posting whose
poster happens to be unverified would read 0 through a perfectly working
reader. K10 asks what the badge looks like *as a class*; I have one instance.
And I did not determine WHOSE verification the marker refers to, which is the
question that decides whether this row can ever publish anything.

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
ever writes the pattern.

### IT LANDED: `tests/test_the_settings_boundary_refuses_account_deletion.py`, `85364e7`

Delegated as a closed-form slice, reviewed against the shipped predicate
before admission. The load-bearing test **passes today and that is the
point**: it monkeypatches a plausible settings-family pattern into
`_ALLOWED_URL_PATTERNS` and asserts the close-account address **becomes
admitted**, documenting the hazard as a reproducible fact rather than a
warning in prose. `readonly.py` is not edited, and monkeypatch restores the
tuple so no later test in the process inherits a widened boundary.

Shown failing before admission: the refusal test run with the allowlist
widened at import time gave **1 failed, 3 passed**, and **4 passed** after
reverting.

### THE SLICE FOUND SOMETHING MY BRIEF DID NOT KNOW, AND IT SHARPENS THE RULE

I briefed it that close-account is refused by no pattern matching. That is
true of the SINGULAR spelling. It read `readonly.py`'s own settings-audit
comment and found that **LinkedIn's real address is the PLURAL**,
`/close-accounts`, and that the plural is the spelling sitting on the
forbidden-substrings tuple. So under one widened allowlist:

    /mypreferences/d/close-accounts   REFUSED -- the denylist names it
    /mypreferences/d/close-account    ADMITTED -- nothing names it

Both halves are asserted, and the contrast is worth more than either:

> **A name-based refusal survives a widened allowlist. A shape-based one does
> not.**

It also verified the GATE each refusal comes from rather than accepting a
shared `False`: the four singular spellings refuse at the allowlist gate,
`/psettings/close-account` refuses at the denylist gate. Two urls returning
the same boolean for different reasons is precisely the reading this
repository keeps catching being taken as one fact.

**I did not know the plural existed when I wrote the brief.** A slice that had
obeyed the brief instead of reading the artifact would have shipped a test
asserting the weaker half only.

### ANOTHER WAVE FOUND THE SAME THING INDEPENDENTLY, AND THAT IS THE STRONGEST PART

`db0dc40` (`boundary: two anchored reads, and the family pattern shown
admitting deletion`) landed from a different wave while mine was in flight. It
carries `test_the_family_pattern_the_trap_names_does_admit_account_deletion`
and `test_every_account_ending_spelling_is_still_refused`, and its docstring
records **the same plural/singular split**, reached separately.

**Two waves, not sharing an instrument, converged on the same measurement.**
Mine came from a slice interrogating the shipped predicate; theirs from
reading `readonly.py` and re-measuring. This is the day's corroboration law
satisfied properly for once -- *agreement between instruments sharing a defect
is not corroboration*, and these two share no defect because they share no
method.

**BOTH FILES SHOULD STAY, and a consolidator should know why before deleting
either.** They are scoped differently:

* theirs is anchored to **their own widening** (school and collections) and
  asks whether those two new patterns can reach deletion;
* mine is anchored to **the settings family in general** and is tied to no
  widening, so it still asserts something after their patterns are gone.

**AND MINE WAS EXERCISED BY A REAL WIDENING WITHIN THE HOUR, WHICH IS BETTER
THAN ANY MUTATION I COULD PLANT.** It was written against an allowlist of
**29** patterns. Re-measured at freeze, the allowlist stands at **31** -- two
patterns added by another wave after my test landed -- and close-account is
**still refused**, with my file green at 4 passed. A guard that survives an
independent, unannounced boundary change is doing the thing it was built for.

**One correction to my own commit message while I am here:** `85364e7` says
the slice found something the brief did not know. True of *my* wave. It was
not the only wave to find it, and saying so is cheaper than letting a reader
infer sole discovery from a commit message.

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
* ~~**K8's reading is text-only.**~~ **DONE in `b88211b`** -- see section 2.
  The accessible-name corpus was added, the blind spot fired on `premium`
  (0 in text, 19 in names), and `top voice` stayed 0 in both.
* ~~**K10 was never read.**~~ **DONE in `9d89134`** -- see section 2b. What
  remains on K10 is narrower and is stated there: **a sample of one posting**,
  and I did not determine whose verification the marker refers to.
* **The probe was NOT admitted to any instrument register**, and I am not
  registering it. Its two declared defects are fixed and it now carries a
  two-corpus control that has been shown disagreeing -- but it has never been
  run against a surface where the answer is independently known for the
  needles that matter, only against a control page chosen for absence. The bar
  for the register is that an instrument has been shown FAILING; this one has
  been shown reporting absence, which is weaker.
* **I did not press any control on either surface**, so `profile language 1`
  says a phrase renders and nothing about whether it is actionable.
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
not a reading*, and half of this pair could not have failed.

### FIXED IN `b88211b`, AND THE OBLIGATION IS NOW DISCHARGED

Both readings are taken on the SAME address, bracketing the second load of it:

    BEFORE (on the profile)  {'links': 2, 'badge_links': 1, 'label': 'My Network, 0 new notifications'}
    AFTER  (on the profile)  {'links': 2, 'badge_links': 1, 'label': 'My Network, 0 new notifications'}

**Identical at both ends, across three page loads of his profile.** The
counter did not move under this wave's reads.

**The caveat that must travel with it, because this repository has written it
down twice:** a badge at zero cannot distinguish *the page consumed nothing*
from *there was nothing to consume*. `0 new` at both ends is consistent with
both, and I am claiming only the first -- that nothing this wave did moved it.

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

**THE FREEZE READING, taken at 20:01 with the boundary tests added:**

    1 failed, 980 passed in 23.62s

The single failure is `test_every_claimant_of_a_sanitiser_name_is_enrolled`,
another wave's, named below. **No red in this tree is mine**, and that is a
statement about a reading taken at 20:01 in THIS CHECKOUT -- not "at HEAD",
because pytest imports from the working tree and in a tree a dozen waves are
writing those are different objects.

**The full suite was NOT run and no clone was taken.** A 29-minute suite does
not fit inside this wave's window, and an enumeration violation is invisible
to every run I did make. That is a hole in this reading, stated rather than
papered over.

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

### A SECOND RED APPEARED AT FREEZE AND WAS NOT REAL. I NEARLY REPORTED IT.

The freeze reading, taken at 20:00, returned **2 failed, 987 passed**. The
second was the taint guard -- the same one I had fixed an hour earlier and had
green at 262 passed twenty minutes before.

Three readings settled it, and the ORDER is the finding:

    20:00   combined set     2 failed, 987 passed
    20:01   guard ALONE      1 passed
    20:01   combined set     1 failed, 980 passed   <- did not reproduce

**It was a neighbour's file mid-write.** This guard SCANS THE TREE, so its
result is a photograph of a repository a dozen agents are writing, and two
untracked probes belonging to other waves sat in `scripts/` throughout.

**AND THE STRUCTURAL CORROBORATION IS BETTER THAN MY REASONING:** the two
combined runs, one minute apart, collected **987 and 980 tests**. I changed
nothing between them. *A count that moves under no change of mine is a number
about the tree, not about my code* -- which is this day's "compare the SETS,
never the totals" law arriving from the other direction. The totals moving is
itself the evidence.

    RULE: a red on a TREE-SCANNING guard, in a repo with many writers, is
          re-taken before it is routed. Running it ALONE distinguishes a real
          hit from a neighbour's file caught mid-write, and costs seconds.

**I would have reported two reds at freeze, one of them owed by nobody.**
Re-taking the reading caught it; re-reading the output could not have.

## 8. COST, RECOMPUTED RATHER THAN RECALLED

Derived from the probe's own control flow, not from memory -- `_read` is
called once at the control page and twice at the profile, so **three
`goto` calls per run**:

    /mypreferences/d/dark-mode, /in/me/, /in/me/

    run 1  19:38   3 loads   completed   (text corpus only)
    run 2  19:41   3 loads   completed   (reproduced run 1 exactly)
    run 3  19:48   3 loads   completed   (accessible-name corpus, badge fix)
    run 4  20:00   4 loads   completed   (K10 added: + the job posting)
    run 5  20:05   4 loads   completed   (badge pair reordered; reproduced)
    ---------------------------------------------------------------------
    TOTAL         17 page loads, 0 presses, 0 writes, 0 addresses added

Plus **one MCP call** (`linkedin_saved_jobs`, limit 3) to obtain a real
posting id, since every job id in this repository's tracked files is a
synthetic fixture and navigating to one would have read a 404 and reported a
clean absence.

**RECOMPUTED AT FREEZE, NOT RE-READ.** The section as first written said
`TOTAL 6` against two runs, and a third run happened after it. Six was correct
when written and wrong when read, which is the shape this repository keeps
paying for -- and it is the *flattering* direction, since it makes the wave
look cheaper than it was. Re-reading the sentence could not have caught it;
recomputing from the control flow did.

One tab per run, opened and closed. `page.is_closed()` read **True** on all
three runs -- a presence reading about the one object each run created, not a
count over a pool a dozen waves share. The PAGE was closed, never the context.

## 9. COMMITS, AND EVERY BLOB VERIFIED AGAINST ITS REPORTED COUNT

    707583b  probe: the badge/language reader                +241  -0
    79e126b  test: the two vocabularies and two gate indices +125  -0
    57117d4  audit: this document                            +419  -0
    b88211b  probe: accessible names, badge pair, escape      +55 -12
    85364e7  test: the settings boundary refuses deletion    +158  -0
    7700cc6  audit: corrections (blind spot fired, plural)   +191 -27
    9d89134  probe: K10 on a live job posting                 +49  -0
    10c02b6  audit: K10 measured, blind spot fired twice      +68  -6
    ae2ed91  audit: another wave converged independently      +35  -0
    2956c05  audit: a freeze red that was not real            +45  -0
    ----------------------------------------------------------------
    TEN COMMITS, FOUR DISTINCT PATHS

**Each was verified with `git show HEAD:<path> | wc -l` against the insertion
count the commit reported**, because a failed `git commit --only` rolls the
working tree back and two waves lost ~70 and ~90 finished lines to it today.
Every message was passed as a FILE PATH, never on stdin -- the other half of
that same scar.

**Zero AI attribution across all five**, recomputed at freeze by grepping the
five commit messages for the co-author, session and generated-with markers:
**0 matches**. The repo is public.

Nothing pushed. **The union of paths across all TEN commits is FOUR distinct
files** -- recomputed with `git show --numstat` at freeze, because the
sentence that first stood here said "two scripts" and there is only one,
committed three times:

    scripts/_probe_badge_and_language_affordances.py    (707583b, b88211b)
    tests/test_badge_and_language_affordances.py        (79e126b)
    tests/test_the_settings_boundary_refuses_account_deletion.py  (85364e7)
    _audit/2026-09-05-profile-rest.md                   (57117d4, and this update)

`readonly.py`, `dom.py`, `server.py` and `writes.py` are untouched by this
wave, which is a stronger statement than a re-pinned digest and is checkable
in one command. **Another wave committed two allowlist patterns
(`/school/<slug>/` and `/jobs/collections/recommended/`) while this wave ran**
-- that is why my measured count of 29 already exceeded the freeze file's 28,
and it is theirs, not mine.

## 10. WHAT THE NEXT WAVE ON THIS SURFACE SHOULD TAKE FIRST

1. **Read K10 on a live job posting.** It is the one row here I argued rather
   than measured, and the address is already admitted and already loaded by
   `linkedin_job_detail`. Cheapest remaining row on this surface.
2. **Aim the `profile-modals` aim reader at the `profile language` hit.**
   *Named is not pressable.* One phrase renders; whether a control exists is
   unmeasured, and that wave's reader answers exactly this question without
   pressing anything.
3. **Do NOT write a settings-family pattern.** Row 78 names no address, so
   there is nothing to admit; and `85364e7` now makes the cost of writing one
   visible as a red rather than as a silent admission.
4. **The ledger's row 43 is one row too big** (B8 == K9) and both its
   `allowlist +1` charges are refuted. Re-costing is the lead's; the
   measurement is here.
