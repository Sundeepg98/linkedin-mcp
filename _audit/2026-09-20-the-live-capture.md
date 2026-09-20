# The live capture: six surfaces opened, two rows banked, and three standing reasons refuted

Wave `live-capture`, 2026-09-20, from master `8b58dcb`. A LIVE AUTHENTICATED
SESSION, which no recent wave has had. Read-only throughout: no write was
fired, `writes_enabled` stayed false, nothing was connected, messaged,
applied to, followed or posted. Every address opened was already on the
shipped read allowlist -- **no boundary change was made and none is proposed
without the argument in section 7.**

---

## 0. THE HONEST LEDGER LINE, FIRST

    rows banked out of GAP            2    J 123, N 135 -> COVERED-PROVEN
    rows inflated                     0
    standing census reasons refuted   3    J 136/137/138 share one, and it was wrong
    rows re-diagnosed, not banked     4    J 124, J 126, J 127, N 136
    verdicts left open, with reason   1    N 136, and it is the second time
    surfaces captured                 6    all to _state/, none committed
    offline instruments shipped       1    + 5 controls, all driven into failure
    prior findings live-reproduced    2    the newsletter census, the unlock asymmetry
    prior hypotheses live-confirmed   1    the profile-views scope defect
    defects found in my own work      2    section 9
    allowlist patterns added          0

**THE SCARCE RESOURCE WAS THE SESSION AND IT WAS SPENT ON READS.** Thirteen
tool calls and one six-page capture. Everything else in this document is
offline over `_state/`, re-runnable for ever with the browser switched off.

---

## 1. WHAT WAS OPENED

Thirteen live calls and one capture pass.

| call | tool | what it settled |
|---|---|---|
| 1 | `linkedin_auth_status` | authenticated true, http 200, against the voyager me endpoint |
| 2 | `linkedin_premium_status` | the entitlement premise, measured rather than assumed |
| 3 | `linkedin_who_viewed_me` | **N 135**, and the scope defect, live |
| 4 | `linkedin_search_jobs` | seven live posting ids |
| 5-11 | `linkedin_job_detail` x7 | **J 123**, and the J 124 / J 126 re-diagnosis |
| 12 | capture pass, 6 pages | the Premium inventory, the interview question, the newsletter re-read |

Six admitted addresses, each checked by `assert_read_url` BEFORE the browser
opened, all six served, all six with a `<main>`:

    jobs-recommended    1699332 bytes   25 anchors   46 buttons
    premium-hub          131985 bytes   45 anchors   27 buttons
    newsletters           73822 bytes   26 anchors   23 buttons
    profile-views        143568 bytes   33 anchors   27 buttons
    search-appearances  1520180 bytes   29 anchors   20 buttons
    jobs-search         1551460 bytes   26 anchors   72 buttons

Every capture is in `_state/` (gitignored) and **none may ever be committed**:
measured, they embed a member urn inside the lix `trackingInfo` blob. That is
now a concrete reason rather than a general caution.

---

## 2. THE MEASUREMENT THAT DECIDES EVERY COUNT BELOW

**A NEEDLE IN THE SOURCE IS NOT A NEEDLE ON THE PAGE**, and on this corpus the
difference is total:

| needle | raw source, 6 docs | rendered text, 6 docs |
|---|---:|---:|
| `inmail` | 16, 16, 0, 0, 0, 21 | **0, 0, 0, 0, 0, 0** |
| `credit` | 30, 31, 0, 0, 0, 30 | **0 everywhere** |
| `premium` | up to 1212 | 0 to 9 |

Three of the six captures are about 1.4 MB and **over 99 percent of that is
the Ember bundle, the i18n dictionaries and the lix blob** -- rendered text is
0.2 to 2.5 percent of the document. A census over the raw source would have
reported an InMail balance present on three surfaces. It is present on none.

Had this wave counted the raw document, it would have reported the opposite of
the truth on the single row the operator asked about most. Both counts are
printed side by side by the shipped instrument, because the gap between them
is the finding.

---

## 3. THE TWO ROWS BANKED

### 3a. `N 135` -- the weekly viewer trend graph (Premium) -- **COVERED-UNFIRED -> COVERED-PROVEN**

Proving call: `linkedin_who_viewed_me`, no arguments.

    insights.trend.present        true
    insights.trend.description    present, 31 chars
    insights.headline             value 2 digits, label 15 chars
    insights.delta                value 3 chars, label 16 chars
    insights.filters              5

The description matches the shape `<word> chart with <N> data points.` --
asserted as a regex over the banked payload, so the claim is a shape and no
sentence LinkedIn wrote is reproduced here.

**A PRESENCE IS UNAMBIGUOUS EVEN THOUGH AN ABSENCE ON THIS PAGE IS NOT** --
section 5. The chart sentence was found, so the field reaches a caller with a
value on a live page. That is what COVERED-PROVEN asserts and it is all it
asserts.

### 3b. `J 123` -- Premium hiring-company insights -- **COVERED-UNFIRED -> COVERED-PROVEN**

Proving call: `linkedin_job_detail(job_id=<a live posting>)`, run over **seven**
live postings from one `linkedin_search_jobs` pass.

    postings called                                7
    postings drawing company_insights              3
    of those, heading length                       45 chars each
    of those, lines                                17, 21, 21
    insights_error                                 absent on all 7
    applicant_insights present                     7 of 7

**THREE OF SEVEN IS THE MEASUREMENT AND FOUR NULLS ARE NOT A FAILURE.** The
reader's own docstring records the panel as absent on four of five committed
captures and calls that the normal case; seven live postings agree with it.
The row promotes on the first posting that draws the panel, and a null is a
fact about that employer, never about the capability. Budgeting several ids
was the difference between banking this row and filing a false absence -- a
single unlucky posting had a 4-in-7 chance of producing one.

---

## 4. `J 136` / `J 137` / `J 138` -- THE ROW WHOSE REASON WAS WRONG

These three sat GAP behind a fact filed as *"only the operator knows: has he
taken a LinkedIn practice AI interview"*, with the standing note that the
precondition **"cannot be discharged cheaply"** because it *"requires a
completed session to exist"*.

**That was a technical unknown wearing a permission costume, and it was
readable.** It did not need him, and it did not need a completed session. It
needed one page load, and the page load says three things the census does not.

### 4a. The product IS offered to this account, and LinkedIn draws its address

`/premium/my-premium/` draws exactly one role-play anchor:

    route   /learning/role-play/scenarios/new/
    label   2 words, 16 chars, first word "start" (matched against a closed
            product vocabulary; the second word is not in it and is withheld)
    where   offset 71643 of 123588 after stripping scripts, 5 sections and
            1 h2 deep -- product content, not global chrome

**THE ADDRESS WAS NOT GUESSED.** It is an href LinkedIn served to this account
on his own Premium hub, which is the standard this repository already holds
itself to.

### 4b. The census's stated obstacle is half wrong

All three rows say the product *"opens in LinkedIn Learning in a NEW TAB, on
an address outside this server's allowlist"*, and treat that as the barrier.

Measured: the address is **`www.linkedin.com/learning/role-play/scenarios/new/`**
-- same origin, same host, and it carries **no member segment**. It is refused
today, but it is an ordinary allowlist candidate, not the cross-domain
impossibility the rows imply. The barrier the rows name is not the barrier.

### 4c. The real barrier, and it is a different one

**No results address is drawn anywhere.** Across all six captures:

    learning / role-play route shapes drawn        3
    of those, results / history / transcript-shaped 0
    of those, create-shaped (a /new segment)        1

So the question the rows ask -- *do a past session's readiness score, summary
and transcript have a stable address* -- gets this answer: **on the six
surfaces this account renders, LinkedIn offers a route to START one and no
route to READ one back.**

That is a bounded finding and not a proof of absence. A results address could
exist and be drawn only after a session completes. What has changed is that
the rows no longer rest on an unasked question about the operator.

### 4d. And the one drawn route is a create route, which this repo has already ruled on

`/learning/role-play/scenarios/new/` is a `/new/` route whose press starts a
session. **That is the same class as `/article/newsletter/new/`**, which the
`build-newsletter` wave refused ten days' worth of reasoning ago on the ground
that opening a composer may autosave something this server has no surface to
detect. The argument transfers without modification, and it is stronger here:
a role-play session needs a microphone and is a live product interaction.

### 4e. LinkedIn's own flag naming settles a conflation the census could not

The jobs surface carries **8 interview-bearing lix flags**, parsed out of 376
flags whose treatments span **26 distinct values** -- so `control` below is a
reading and not a parser default.

| flag | treatment | side |
|---|---|---|
| `hiring-hero-interview-ai-platform-redirect` | enabled | recruiter |
| `hiring-interview-ai` | v5_mobile_video | recruiter |
| `hiring-interview-ai-intro-page-design` | enabled | recruiter |
| `hiring-interview-ai-default-video-off` | control | recruiter |
| `hiring-interview-ai-dynamic-chunking` | control | recruiter |
| `hiring-interview-ai-research-features` | control | recruiter |
| `hiring-interview-ai-research-features-jobs` | control | recruiter |
| **`learning-job-interview-prep-role-play-experiment`** | **control** | **member** |

**SEVEN OF THE EIGHT ARE THE RECRUITER-SIDE PRODUCT** -- the employer's AI
interview platform that screens candidates. They are not what J 135-138
describe and any wave grepping for `interview-ai` will hit them first.

The one member-side flag is LinkedIn's own, and its name joins the two things
the census kept apart: **`job-interview-prep`** and **`role-play`** are one
product in LinkedIn's naming. Its treatment on this account is `control`.

### 4f. Verdict

**All three stay GAP.** Nothing is banked and nothing is inflated. What
changes is the reason, which was wrong, and the next artifact, which was
misdirected:

* WAS: blocked on a precondition only the operator can discharge, by holding a
  live audio interview.
* IS: the member-side entry exists and is Premium-gated; its only drawn route
  is a create route in the refused autosave class; no results route is drawn
  on any surface this account renders; and the member-side experiment flag
  reads `control`.

**The next artifact is no longer a ruling and no longer needs him.** It is a
read of `/learning/role-play/scenarios/` -- the listing, WITHOUT the `/new/`
segment, which is a different address from the one drawn and has never been
opened. That is one allowlist hypothesis and one page load, and it is the only
step that can distinguish "no results page exists" from "no results page is
linked from here".

---

## 5. `N 136` STAYS OPEN, AND THE SCOPE DEFECT IS NO LONGER A HYPOTHESIS

`_audit/2026-09-20-the-premium-block.md` section 5 reported, from the tree
alone, that `PROFILE_VIEWS_INSIGHTS_JS` obeys `main` while its comment says it
reports it, and that no committed fixture of that page has a `<main>` -- so
the live call takes the branch nothing tests. It called the consequence
ambiguity and could go no further offline.

**The live call resolves it, and it is not ambiguity. It is a contradiction.**
One load, two readers:

| | |
|---|---:|
| viewer rows the outer reader parsed | **12** |
| viewer rows returned to the caller | 10 |
| `main_present` | true |
| `main_chars` | **1835** |
| viewer rows the scoped reader saw | **0** |
| `data-view-name` elements the scoped reader saw | **0** |

The page demonstrably carries twelve viewer rows. The scoped reader, on the
same document at the same moment, sees zero of them inside an 1835-character
`main`. **That is not LinkedIn declining to draw something. It is the reader
looking in the wrong box**, confirmed rather than inferred.

Consequences, kept apart:

* **`N 136` -- the top-locations panel -- stays OPEN.** Its instrument is
  `view_names`, that list is empty, and the emptiness is now a proven scope
  artifact. **This is the second time this row has been closed or nearly
  closed on an instrument that could not have seen it**, and it must not be
  banked MEASURED-ABSENT until the scope is fixed.
* **`N 135` is untouched by this**, because a presence found inside a wrong
  scope is still a presence -- section 3a.

The fix stays where premium-block put it: one line in `dom.py`, plus a fixture
of this page WITH a `<main>` so the live branch is the tested branch. Shipped
failing first. **`dom.py` is contended and this wave did not edit it.**

---

## 6. THE PREMIUM INVENTORY -- the evidence-backed answer to the standing question

*"Why does this MCP cover none of my Premium, when I hold Premium Career?"*

### 6a. The entitlement itself, measured for the first time

    linkedin_premium_status ->
      state            entitled
      strength         thin
      entitled_hits    1        needle: "manage subscription"
      unentitled_hits  0
      controls_scanned 72
      redirected       false

`thin` is the tool's own honesty: one management verb, no sales verbs
alongside it. State A is refuted; the verdict does not overclaim.

### 6b. The surfaces LinkedIn draws, against what the server may read

**43 distinct route shapes across the six captures. 6 admitted, 37 refused.**
Every row below is an address LinkedIn SERVED to this account -- none is
guessed, which is the standard the newsletter wave set and this table keeps.

| Premium surface | drawn on | admitted | is the data in the DOM | verdict |
|---|---|---|---|---|
| `/analytics/profile-views` | premium-hub, search-appearances | **yes** | yes | **reader exists** -- `linkedin_who_viewed_me`, 365-day depth, 12 rows this load |
| `/analytics/recruiter-views` | profile-views | no | unread | **reader COULD exist** -- not previously recorded anywhere in this repo |
| `/jobs/collections/top-applicant` | premium-hub | no | unread | **reader COULD exist** -- this is the Top Applicant signal the question names |
| `/jobs/collections/top-choice` | premium-hub | no | unread | reader could exist; sibling of the admitted `/recommended` |
| `/learning/role-play/scenarios/new` | premium-hub | no | n/a | **create route, refused class** -- section 4d |
| `/premium/profile-key-skills` | search-appearances | no | unread | reader could exist |
| `/premium/premium-perks` | premium-hub | no | unread | reader could exist, low value |
| `/premium/sb/explore`, `/premium/switcher` | premium-hub | no | unread | plan chrome, not member data |
| `/manage/purchases-payments/purchases` | premium-hub | no | unread | billing; deliberately not pursued |
| `/explore-career-insights` | search-appearances | no | unread | reader could exist |
| `/jobs/application-settings` | search-appearances | no | unread | a settings surface, write-adjacent |
| InMail credit balance | **nowhere** | -- | **NO** | **not in the DOM** -- 6c |
| salary insights | **nowhere** | -- | **NO** | `salary` rendered 0 on all six |
| Top Applicant *as rendered text* | premium-hub only, 1 occurrence | -- | as a link label | the collection is the route above |

**So the answer to the question is not "Premium is uncovered".** It is: one
Premium surface is covered and fired today; **four more are named, drawn, and
one allowlist line plus one reader away**; two are not in the DOM at all; and
one is a create route this repository has already ruled it will not press.

### 6c. `J 127` -- the InMail balance -- the absence is now measured by an instrument that could have seen it

The premium-block wave found this row wrongly closed: the only instrument that
had ever opened `/premium/my-premium/` reads accessible names of `a` and
`button` against 16 needles and returns no page text by construction, so it
**could not have reported a balance if one were there.**

This wave used a different instrument -- a whole-document rendered-text census
-- and it reports what it DID see, not only what it did not:

    on /premium/my-premium/, rendered text, 3346 chars
      RENDERED-PRESENT   premium 9, insight 3, applicant 1, top applicant 1,
                         interview 1, recruiter 1, manage 2, edit 1
      RENDERED-ABSENT    inmail, credit, salary, unlock, upgrade,
                         who viewed, subscribe, unsubscribe, delete

**The census named eight words on that document, so the zeros are readings.**
And the surface is not numerically barren: it draws **7 digit-bearing control
texts and 13 digit-bearing aria-labels**, so what is absent is the InMail
LABEL, not numbers in general. A numeric reader is buildable there; it would
have nothing to bind to.

**HONEST LIMIT, STATED RATHER THAN BURIED:** this is the DOM at settle. A
panel that renders only after a press, or lazily below the fold, is absent
from the capture without being absent from the product. What is established is
that the balance is not in the initial render of the surface most likely to
carry it. Whether LinkedIn's current Premium Career tier includes InMail
credits at all is a product question this capture does not settle, and I am
not answering it from memory.

### 6d. The upsell asymmetry, independently reproduced

premium-block measured, from a session script it could not run, that
`/analytics/search-appearances/` carries an upgrade control while
`/analytics/profile-views/` carries none -- on the same Premium account.

A different instrument, on captures taken today, agrees exactly:

    rendered text        unlock   upgrade
    search-appearances        1         0
    profile-views             0         0

**Two analytics addresses, one entitled account, and only one of them
upsells.** This is the concrete case `premium.py`'s five-state model exists
for, and it is the live hint that holding Premium Career does not unlock
every surface labelled Premium. Cross-instrument agreement, recorded.

---

## 7. THE BOUNDARY: NOTHING WAS ADMITTED

`_ALLOWED_URL_PATTERNS` is unchanged. Every address opened was already on it.

Four candidates are now evidenced well enough to be argued for, and I am
filing the argument rather than the line, because **an address that has been
seen served is a candidate, not yet a decision** -- and three of the four
still need a shaper designed before they would be usable:

1. `/learning/role-play/scenarios/` -- the listing, not the drawn `/new/`
   route. No member segment. **Would close section 4's open question.** The
   `/new/` sibling stays refused under 4d.
2. `/jobs/collections/top-applicant` -- no member segment; sibling of an
   already-admitted collection; the Top Applicant signal the operator named.
3. `/analytics/recruiter-views` -- no member segment, but the page is made of
   recruiters, so it needs the profile-views shaper treatment before a reader.
4. `/premium/profile-key-skills` -- no member segment.

**None of these is one line from a capability**, and saying so is the point:
the ledger costs several of them at "allowlist +1", and that costing is wrong
in the same way section 3a of the newsletter audit found it wrong.

---

## 8. THE NEWSLETTER WRITE SURFACE, RE-READ LIVE

The `build-newsletter` wave banked 0 rows because nine of its eleven GAP rows
are writes whose controls sit on a page nobody had opened since 2026-09-05.
That page was opened today and **the shipped instrument was run over the fresh
capture rather than a new one being written**:

    ./venv/Scripts/python.exe scripts/_probe_newsletter_surface_shape.py \
        --capture _state/cap-newsletters.html

| | 2026-09-05 capture | 2026-09-20 live | |
|---|---:|---:|---|
| `/newsletters/` anchors | 10 | **10** | agrees |
| `/article/newsletter/new` | 1 | **1** | agrees |
| member paths in the product section | 3 | **3** | agrees |
| buttons | 19 | **19** | agrees |
| forms | 1 | **1** | agrees |
| the word `analytics` | 0 | **0** | agrees |
| the word `subscribe` | 0 | **0** | agrees |
| the word `unsubscribe` | 0 | **0** | agrees |

The probe's `--control` passes, so those three zeros are measurements.

**EVERY NEWSLETTER CONCLUSION THAT WAS OFFLINE IS NOW LIVE-VERIFIED.** `N 56`
does not shorten -- no unsubscribe control is drawn. `M C83` and `P L4` are
not one allowlist line from anything -- the page still links no analytics
address and still says the word zero times, fifteen days later. `M C51`,
`M C84` and `P L3` still have no manage, edit or delete route on this surface.

Two shapes the fresh capture adds, both in `main>section>section`: a singular
`/newsletter/new` (1) and `/article/new` (1), the already-admitted composer.

**No row moves.** A write cannot be tested with writes disabled, and they must
stay disabled. What has changed is that nine rows' standing reason is no
longer "nobody has opened this page."

---

## 9. EVERY CONTROL, AND THE TWO DEFECTS IN MY OWN WORK

### The instrument

`scripts/_probe_premium_surfaces_shape.py`, offline over `_state/cap-*.html`.
Five controls, **each driven into its failing state in-process and each
returning non-zero**, then passing again afterwards:

| control | mechanism | driven state | result |
|---|---|---|---|
| the census can speak | 19 needles over a synthetic document carrying all of them | `visible_text` blinded | exit 1, VOID |
| the stripper removes a bundle | a needle x400 inside a script block, plus a drawn word that must survive | `STRIPPED_TAGS` emptied | exit 1, VOID |
| the reducer changes a name | four member/org/campus/numeric paths | reverted to the version that leaked | exit 1, VOID, **3 of 4 leaked** |
| a non-`control` treatment is reportable | a two-flag blob | parser pinned to one value | exit 1, VOID |
| an absent capture is not a zero | a missing state dir | run against a nonexistent path | **exit 2**, nothing tallied |

### 9a. MY REDUCER LEAKED A REAL PERSON'S SLUG INTO MY OWN STDOUT

The first version replaced a path segment only when it was long or
digit-bearing. **A profile slug is neither**, so `/in/<a real person>` printed
verbatim -- a third party's and the operator's own -- before I caught it.

The rule that works is the opposite one: **the segment after a member-bearing
prefix is replaced unconditionally, whatever it looks like.** Control 3 is
built from exactly that failure and reproduces it on demand.

**It was found by reading my own output, not by reading my own code**, which
is why the control exists rather than a comment. Nothing leaked into a tracked
file; the captures that carry names are gitignored and stayed there.

### 9b. I ALMOST REPORTED AN INMAIL BALANCE THAT IS NOT THERE

My first census counted the raw document and returned `inmail` 16 to 21 on
three surfaces. Those are bundle strings. Had I stopped there I would have
reported the opposite of the truth on the row the operator asked about most,
with a number attached to make it look measured. Section 2 is that mistake
turned into the instrument's primary output.

### A third instrument still cannot fail, and it is not mine

`scripts/_probe_events_surface_shape.py`'s must-stay-silent control is printed
and never branched on -- the identical gap the newsletter wave found and fixed
in its own probe. **Still unfixed at `8b58dcb`**, named here rather than
edited, because it belongs to another wave and a one-line fix with the
evidence attached is cheaper for its owner than a surprise in their diff.

---

## 10. QUESTIONS OPENED AND NOT CLOSED

Named, so the next wave does not re-discover them, and so this wave does not
repeat the 2026-09-05 probe that left two of its own four questions open for
fifteen days behind a page load already paid for.

1. **Does `/learning/role-play/scenarios/` (no `/new/`) serve, and does it
   list past sessions?** One allowlist hypothesis, one page load. This is the
   whole remaining cost of J 136-138 and it needs nothing from the operator.
2. **Does `/analytics/recruiter-views` serve, and what is on it?** Drawn on
   his own profile-views page, never recorded in this repo before today.
3. **What is on `/jobs/collections/top-applicant`?** The Top Applicant signal,
   named in the standing question, drawn, unopened.
4. **Is the InMail balance anywhere behind a press?** Section 6c establishes
   it is not in the initial render of the Premium hub; it does not establish
   that no surface carries it.
5. **Does the profile-views scope fix change `view_names` from 0?** It should,
   and it would settle `N 136` in one run -- but the fix belongs to whoever
   owns `dom.py`.

None of the five needs a ruling, a consent or a measurement only the operator
can authorise. All five need a browser.
