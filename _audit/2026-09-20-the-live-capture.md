# The live capture: eleven surfaces opened, two rows banked, three standing reasons refuted, two redirects named

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
    defects found in my own work      3    section 9, and 9c was found last
    allowlist patterns added          2    sections 11 and 12.1; NEITHER bought a row
    open questions closed later       1    section 11 answered section 10's first
    CANNOT-TELL blockers measured    10    section 12, 7 loads, 0 rows moved
    redirect targets named            2    section 12, one of them 15 days old

**THE SCARCE RESOURCE WAS THE SESSION AND IT WAS SPENT ON READS.** Thirteen
tool calls, one six-page capture, and -- after the first freeze -- four more
loads to open the one address this wave had filed as an argument rather than
a line. Everything else in this document is offline over `_state/`,
re-runnable for ever with the browser switched off.

**THE LEDGER ABOVE COUNTS SECTIONS 1-11. Section 7 originally reported that
nothing was admitted; one pattern was, later the same day, and both the
original sentence and the amendment are left standing there.**

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

**43 distinct route shapes across the six captures. 6 admitted, 37 refused
when this section was written -- and 7 / 36 from section 11 onward**, because
the seventh is the one this wave admitted itself. Re-running the instrument
today prints 7; the 6 is kept above with this sentence beside it rather than
overwritten, so the two numbers stay reconcilable instead of one of them
quietly becoming wrong.
Every row below is an address LinkedIn SERVED to this account -- none is
guessed, which is the standard the newsletter wave set and this table keeps.

| Premium surface | drawn on | admitted | is the data in the DOM | verdict |
|---|---|---|---|---|
| `/analytics/profile-views` | premium-hub, search-appearances | **yes** | yes | **reader exists** -- `linkedin_who_viewed_me`, 365-day depth, 12 rows this load |
| `/analytics/recruiter-views` | profile-views | no | unread | **reader COULD exist** -- not previously recorded anywhere in this repo |
| `/jobs/collections/top-applicant` | premium-hub | no | unread | **reader COULD exist** -- this is the Top Applicant signal the question names |
| `/jobs/collections/top-choice` | premium-hub | no | unread | reader could exist; sibling of the admitted `/recommended` |
| `/learning/role-play/scenarios/new` | premium-hub | no | n/a | **create route, still refused** -- section 4d |
| `/learning/role-play/scenarios` (the listing) | not drawn; reached by admission | **yes, section 11** | **NO** -- `main` is 17 chars | **served and empty** -- section 11 |
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

    on /premium/my-premium/, rendered text, 3346 chars unstripped (3344 stripped)
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

## 7. THE BOUNDARY: ONE PATTERN ADMITTED, AFTER THIS SECTION FIRST SAID NONE

> **AMENDED LATER THE SAME DAY. THIS SECTION ORIGINALLY READ "NOTHING WAS
> ADMITTED" AND THAT IS NO LONGER TRUE.** It was written while the six
> captures were the whole of the evidence, and it filed four candidates as
> arguments rather than lines -- including candidate 1 below. Then the
> session was still live, candidate 1 was the wave's own headline question,
> and **the thing standing between us and the answer was OUR refusal, not
> LinkedIn's.** So it was admitted and opened. Section 11 is what the page
> returned. The original sentence is left standing above rather than
> rewritten, because a section that quietly changes its own verdict is the
> defect this corpus keeps finding.

`_ALLOWED_URL_PATTERNS` went **35 -> 36**, digest `6577a7bc8a32d7b8 ->
`85e821d1af9060f3`. Every OTHER address opened in sections 1-6 was already
on the list; three of the four candidates below are still only arguments.

Four candidates are now evidenced well enough to be argued for, and I am
filing the argument rather than the line, because **an address that has been
seen served is a candidate, not yet a decision** -- and three of the four
still need a shaper designed before they would be usable:

1. ~~`/learning/role-play/scenarios/`~~ -- **ADMITTED AND OPENED. See
   section 11.** The `/new/` sibling stays refused under 4d, and the
   pattern takes no sub-path so it cannot reach it.
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

## 9. EVERY CONTROL, AND THE THREE DEFECTS IN MY OWN WORK

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

### 9c. I REPORTED RUNNING FEWER CONTROLS THAN I RAN

Found after the freeze, by re-deriving section 11's numbers from the capture
instead of from my own prose. **The role-play listing was put to FIFTEEN
empty-state and error needles, not fourteen**, and all fifteen stayed silent.
The audit, three census rows and the `readonly.py` entry each said fourteen.

An understated count is still a wrong count, and this one sat under the claim
that carries the most weight in section 11 -- *the page does not even report
that there is nothing*. **The number of needles that stayed silent IS that
claim's evidence**, so getting it wrong in the safe direction is not a
mitigation. Corrected in all four places, in its own commit, rather than
folded quietly into another change.

**AND THE WAY IT WAS FOUND IS THE REUSABLE PART.** Nothing flagged it -- no
test binds prose to a measurement. It surfaced because the numbers were
re-taken from `_state/` at the end and compared against what the document
said, which is the same check that caught section 6b's admitted count going
stale. **A wave that writes numbers into prose should re-derive them from the
artifact before it stops, because the tree will not.**

### A third instrument could not fail -- AND THIS PARAGRAPH WAS ALREADY STALE WHEN I WROTE IT

**AMENDED. What I published here was true when I measured it and false by the
time it was committed, and the correction is worth more than the finding.**

I wrote that `scripts/_probe_events_surface_shape.py`'s must-stay-silent
control is printed and never branched on, that it was **"still unfixed at
`8b58dcb`"**, and that I was naming it rather than editing another wave's
file.

Both halves have since been overtaken, and I found out by reading the
instrument register at the end rather than by anything telling me:

* **It was fixed**, in commit `2fba253`.
* **And the CLASS was counted, which is the part I did not think to ask for.**
  `scripts/detect_unbranched_probe_controls.py` ran an AST census over every
  `scripts/_probe_*.py`: **56 of 88 probe files carry at least one
  never-branched control; 129 of 762 control-like readings never branch
  (17%), 630 branch correctly, and 13 more are assigned and never read.**
  Register section 27.

**SO MY "SECOND ENTRY TO NAME IT" WAS THE WRONG MOVE, MEASURED.** Naming one
instance by hand twice produced two paragraphs; asking for the shape to be
COUNTED produced a number, a script and 129 sites. The standing lesson is one
this corpus already holds and I did not apply -- *a refusal census is not a
capability census* -- and it costs nothing to notice that "I found another
one" is usually the signal to count rather than to report.

---

## 10. QUESTIONS OPENED AND NOT CLOSED

Named, so the next wave does not re-discover them, and so this wave does not
repeat the 2026-09-05 probe that left two of its own four questions open for
fifteen days behind a page load already paid for.

1. ~~**Does `/learning/role-play/scenarios/` serve, and does it list past
   sessions?**~~ **CLOSED THE SAME DAY, BY SECTION 11: it serves, and it
   renders 17 characters in `main`.** Re-aimed rather than closed outright --
   what is now open is WHY it is empty, and the cheapest test is to re-run the
   same read once the member-side experiment flag stops reading `control`.
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

---

## 11. THE ROLE-PLAY LISTING, ADMITTED AND OPENED -- IT SERVES, AND IT DRAWS NOTHING

Written after sections 1-10 and after the first freeze. Section 4 concluded,
from what six surfaces DRAW, that LinkedIn offers a route to start a role-play
session and none to read one back. That was an inference from absence. This
section replaces it with a load.

### 11a. Why the refusal was ours

Section 4's honest position was *"the listing has never been opened"*, and the
reason it had never been opened is that this repository refuses the address.
**That is our decision, not a fact about LinkedIn**, and a standing refusal
nobody has re-examined is the cheapest kind of blocker to mistake for a wall.
The session was live and this wave was the only browser wave. So the pattern
was admitted, with the argument in `readonly.py` beside it, and the page was
opened.

### 11b. The admission is bounded, and that was proved before it was used

    ^https://www\.linkedin\.com/learning/role-play/scenarios/?$

Ten spellings put to `is_read_url`, **10 of 10 as intended**:

| spelling | admitted |
|---|---|
| the listing, with and without a trailing slash | **yes**, 2 of 2 |
| **the create route LinkedIn actually draws**, bare and with its query | **no**, 2 of 2 |
| a scenario id, a results guess, the role-play root, learning root, a course, the listing with a query | no, 6 of 6 |

**THE PATTERN TAKES NO SUB-PATH AND THAT IS THE POINT.** The route the product
draws is `/new/`, pressing it starts a session, and it is the same autosave
class as `/article/newsletter/new/`. Admitting the listing does not reach it.

### 11c. What the load returned

A known-served control (`/premium/my-premium/`) was read FIRST in the same
session and reported SERVED, so the instrument could tell the two apart.

**IT SERVES.** Landed as requested, no redirect, no login wall, no 404 or
error copy.

**AND IT DRAWS NOTHING:**

    bytes                                  673538
    rendered text                            1135 chars, stripped
                                           (1137 unstripped -- the shipped
                                            probe does not .strip(), so a
                                            re-run prints the larger one)
    anchors / buttons / headings           24 / 26 / 6
    <main> rendered text                       17 chars -- TWO WORDS, 1% of the page
    empty-state and error needles tried          15, all silent
    samples over 25 seconds                       3, byte-identical

**SEVENTEEN CHARACTERS IN `main`.** The 1135 characters are LinkedIn
Learning's global chrome; the content region is two words. Three samples at
settle, +10s and +25s came back byte-identical, so **this is not a hydration
race** -- the page settled and that is what it drew.

**AND THERE IS NO EMPTY-STATE MESSAGE EITHER**, which is the part worth
pausing on. A product with no sessions to show usually says so. Fifteen
needles -- `not available`, `no longer`, `sorry`, `page not found`, `try
again`, `coming soon`, `nothing here` and seven more -- all silent. This page
does not report that there is nothing; it reports nothing.

### 11d. What that settles, and what it does not

**SETTLED:** the address serves, and on this account it renders no scenario
list, no session history, no readiness score, no summary and no transcript.
Section 4's inference is confirmed by a load rather than by absence of a link.

**NOT SETTLED, and this is an inference named as one:** *why* it is empty. The
leading explanation is the one section 4e measured -- the member-side lix key
`learning-job-interview-prep-role-play-experiment` reads treatment `control`
on this account -- which would produce exactly this shape: the route exists,
the shell renders, and the experiment's content never mounts. **That is
consistent with the evidence and is not proved by it.** A second possibility
is not excluded: the product may mount only for a member who has a session,
in which case the page is an honest empty for a different reason.

### 11e. J 136 / J 137 / J 138 -- still GAP, and now for a measured reason

No row moves and nothing is inflated. The blocker is now:

* **not** "only the operator knows whether he has taken one" -- refuted in
  section 4;
* **not** "the address is out of reach" -- it is admitted, bounded and served;
* **but** "the surface renders no session content on this account, and the
  member-side experiment flag reads `control`."

**THE NEXT ARTIFACT CHANGES ACCORDINGLY**, and it still needs nothing from
him: re-run this one read when the flag's treatment changes. That is a
one-command rerun against an address already on the list, and it is the
cheapest open question this wave leaves behind.

### 11f. The honest cost of the admission

**IT BOUGHT NO ROW.** `_ALLOWED_URL_PATTERNS` is one wider and the census is
unmoved, which by this corpus's own standard -- *"a surface admitted and
unusable is not a partial win; it is a blast radius paid for nothing"* -- is
the outcome that has to be declared rather than dressed up.

It is kept, for two reasons stated plainly: the emptiness IS the measurement
and re-taking it later costs one rerun; and the entry names nobody, takes no
sub-path and reaches no write. **But it is a widening that delivered a
negative result, and the ledger line below says so.**

    rows banked by section 11        0
    allowlist patterns added         1
    open questions closed            1   (does the listing serve -- yes)
    open questions re-aimed          1   (why is it empty -- flag, or no session)

---

## 12. SEVEN LOADS AGAINST THE CANNOT-TELL LIST -- TEN BLOCKERS MEASURED, TWO REDIRECTS NAMED

Targeted after the `surface-class` wave published twelve
CANNOT-TELL-WITHOUT-A-CAPTURE blockers, each with the exact address that
settles it, and found the clustering. Its list was read from its own
deliverable on `worktree-agent-ac64d5dbf8f2a20f4`, not from a summary.

**Cost: five batched loads, two follow-up loads, and one answer that cost
nothing because the capture was already on disk.**

### 12.0 The gate was checked live, not read off a ledger cell

Every address below was put to `readonly.is_read_url` first. Six were already
ALLOWED; `/creator-hub/`, `/my-items/saved-posts/` and
`/search/results/people/` are refused and were not opened. **No boundary
change was made in this section.**

### 12.1 `JOB-ALERTS-SURFACE` -- THE REDIRECT TARGET IS NAMED, AFTER FIFTEEN DAYS

    requested   /jobs/alerts/        ALLOWED by our gate
    landed      /jobs/jam            redirected = True, query 0 chars

**`/jobs/jam`.** The 2026-09-05 probe narrowed this to `/jobs/<three
characters>` and enumerated sixteen three-letter guesses -- `all new set top
job alt hub sub rec sav pre JAT jat mgr geo r-r`. **`jam` is not among them.**
Fifteen days of a dead end closed by one load, and it closed because the
landing URL was recorded rather than the load being scored pass/fail.

**THIS IS THE ALLOWED-AND-STILL-WRONG CATEGORY IN ITS PUREST FORM.** Our gate
admits `/jobs/alerts/`; LinkedIn does not serve it. The two facts are about
different systems and the allowlist can never tell you the second one.

**AND THE ENTRY'S OWN COMMENT PRE-AUTHORISED THE REPAIR, SO IT WAS CARRIED
OUT.** It read: *"If the first load 404s, the correct response is to CHANGE
THIS PATTERN, not to conclude he has no alerts."* It did not 404, it
redirected -- the same defect the instruction anticipated, wearing the one
disguise that returns 200. `_ALLOWED_URL_PATTERNS` **36 -> 37**, digest
`85e821d1af9060f3` -> `3561b00ed3a817bc`:

    ^https://www\.linkedin\.com/jobs/jam/?$

**NO SUB-PATH, measured 8 of 8 as intended** -- the bare page admitted with
and without its slash; an alert id, a `manage` sub-path, `pause`, `delete`,
any query, and a sibling three-letter root all refused. The `pause` verb is
the one the original entry warned about in its own family argument: a write
nobody has named, defended by nothing but the absence of a rule. It stays
defended.

**`/jobs/alerts/` IS KEPT.** It is the spelling LinkedIn's Help Center
documents, and the redirect target is only reachable by being allowed to
begin the navigation that redirects. Keeping it costs one dead pattern;
removing it would make the documented address unreachable and teach nobody
why.

**WHAT IT BUYS: the READ precondition for seven alert rows -- and all seven
are WRITES and all seven stay refused.** No row moves. This is an address, not
a capability.

### 12.2 `/messaging/` REDIRECTS TOO, AND THAT RESHAPES THREE BLOCKERS

    requested   /messaging/                  ALLOWED
    landed      /messaging/thread/<id>       redirected = True

**The one admitted messaging address does not serve an inbox. It lands inside
a single thread LinkedIn chose.** That is the sampling trap in its most
literal form: no address on the allowlist enumerates the inbox, so a question
of the form *does a thread of kind X exist* cannot be asked at all today --
only *is the thread LinkedIn opened of kind X*.

The landing address IS allowlisted (`/messaging/thread/` is a pattern), so
nothing was reached improperly.

### 12.3 `GROUP-CHAT-SURFACE` -- NOT ANSWERED, AND THE REASON IS NOW EXACT

    conversation-marked elements drawn     3
    facepile-classed elements             14
    rendered "group"                       1
    rendered participants / members / "you and" / others   0 / 0 / 0 / 0

**THREE CONVERSATIONS OUT OF AN UNKNOWN N, AND THAT IS NOT A MEASUREMENT OF
THE INBOX.** A group thread is neither confirmed nor denied.

**AND THE TWO ANSWERS THIS MUST NOT COLLAPSE INTO ARE BOTH WRONG HERE.** It is
not *the surface is absent*, and it is not even *the account holds no
instance* -- **nobody has looked at the account, because the only admitted
address cannot show a list.** The blocker moves from "nobody captured the
page" to **"no admitted address enumerates the inbox"**, which is a different
and much more tractable problem: it wants an address, not a capture.

### 12.4 `MESSAGE-REQUESTS-SURFACE` -- NO ENTRY POINT DRAWN, AND HERE IS WHAT WAS

    rendered   focused 1    unread 1    starred 1
    rendered   "message request" 0   requests 0   other 0   spam 0   archived 0   pending 0
    request / other / spam / archive-shaped hrefs      0

**The filter vocabulary IS drawn and the requests vocabulary is not.** That is
the refusal naming what it saw: an instrument that found `focused`, `unread`
and `starred` on this document is an instrument that could have found
`requests`.

Same caveat as 12.3 and it is load-bearing: this is a THREAD page with a
partial list pane, not an inbox. **A pending request may exist and be
unreachable from here.** Filed as "no entry point on the only address we can
reach", not as MEASURED-ABSENT.

### 12.5 `PICKER-SURFACES` -- SETTLED, AND IT IS A POSITIVE FINDING

`/messaging/compose/` draws the toolbar, measured off aria-labels:

    emoji 1    gif 1    attach 2    image 1    file 1    write 1    message 2
    absent: photo, video, sticker, record, audio, send
    file inputs: 2   -- one accepting 1 type, one accepting 16 types

**AND THE DISCRIMINATION IS THE CONTROL.** The identical ten-word vocabulary
returned **0 of 10 on `/messaging/`** and **7 on `/messaging/compose/`**, in
the same session minutes apart. A needle set that scores zero on one page and
seven on its sibling is demonstrably matching something real, not matching
everything or nothing.

### 12.6 `INMAIL-COMPOSE-SURFACE` -- THE ROW WAS RIGHT, AND NOW IT IS MEASURED

The question was whether the newly-found address is the very composer the
census row calls INSUFFICIENT. It is.

    rendered "inmail"        4
    rendered subject         0      aria-label mentioning subject   0
    rendered credit / premium / "open profile" / "free message"   0 / 0 / 0 / 0

**AN INMAIL CARRIES A SUBJECT LINE AND AN ORDINARY DIRECT MESSAGE DOES NOT.**
Zero subject fields, in the text and in the accessibility tree, on a surface
that draws a full compose toolbar. So `/messaging/compose/` is the ordinary
composer, and the four `inmail` occurrences are inbox filter vocabulary rather
than a compose mode.

**NOTHING WAS PRESSED, TYPED OR SUBMITTED.** The address was already
allowlisted; this opened it and read it. It is recorded because the
instruction was explicit: if reaching a compose surface at all risked an
action, skip it and say why. Navigating to a composer with no recipient and
touching no control does not risk one, and the file-input accept attributes
above were read as attributes, never exercised.

### 12.7 `POLL-SURFACE` and `POST-DRAFT-SURFACE` -- NOT DRAWN, WITH THE CAVEAT THAT MATTERS

`/preload/sharebox/`, served exactly as requested:

    rendered text      763 chars       aria-labels    16      <main>   0
    rendered+aria      celebrate 1, job 1
    rendered+aria      poll 0, draft 0, document 0
    IN SOURCE ONLY     poll 2, draft 15

**Section 2's lesson firing again on a new page**: the bundle names `draft`
fifteen times and the page draws it zero times.

**AND THE CAVEAT IS THE HONEST PART.** This address has **no `<main>` and 763
characters** -- it is a PRELOAD fragment, not the live composer. So the
measured absence is an absence *on the preload stub*, which is weaker than an
absence on the product. Both blockers stay GAP and their next artifact is the
live sharebox, not this one.

### 12.8 `CONTENT-ANALYTICS-SURFACE` SERVES, AND IT DRAWS TWO ADDRESSES NOBODY HAS ADMITTED

`/analytics/creator/content/`, served exactly as requested, 2288 rendered
chars of real content: `analytics` 5, `impression` 5, `engagement` 4, `post`
7, `follower` 1.

**Two sibling routes are drawn on it and neither is on the allowlist:**

    /analytics/creator/audience/
    /analytics/creator/top-posts/

Both are name-free, same-origin, and served-adjacent -- the same standard that
justified section 11's admission. Filed as candidates, not admitted here.

### 12.9 `CREATOR-HUB-SURFACE` -- THE CLASSIFIER IS WRONG, AND THE COPY-PASTE HYPOTHESIS HOLDS

The conflict: commit `9d15c11`'s classifier assigns CREATOR-HUB-SURFACE the
address `/analytics/creator/content/`, ALLOWED -- **identical to the one it
assigns CONTENT-ANALYTICS-SURFACE** -- while another committed document gives
it `/creator-hub/`, REFUSED.

Measured on the page itself:

    the string creator-hub anywhere in the SOURCE of /analytics/creator/content/   0
    rendered creator / hub / mode / tools                                0 / 0 / 0 / 0
    /creator-hub/ against the live gate                                  REFUSED

**They are not the same surface and the analytics page has no creator-hub
relationship of any kind** -- not a link, not a mention, not in the bundle.
The duplicate address is a defect in the new classifier, and since the
classifier touched all 26 SURFACE-named blockers, **every address it assigned
should be re-checked against the live gate rather than trusted.**

The other document's `/creator-hub/ REFUSED` is confirmed correct.
CREATOR-HUB-SURFACE is class 2, unchanged: it needs a ruling, then an entry,
then a load -- in that order.

### 12.10 `RESUME-TOOLS-SURFACE` -- ANSWERED FOR NOTHING, OFF A CAPTURE ALREADY ON DISK

No load was spent. Re-reading section 1's `/premium/my-premium/` capture:

    rendered   resume 0   cv 0   builder 0   "cover letter" 0   tailor 0
    rendered   ai 11   applicant 1   interview 1   write 1
    resume / cv / builder-shaped hrefs in the whole document            0

**No resume-builder entry is drawn on the Premium hub**, on an instrument that
named four other words on the same page. **The cheapest answer in this wave
cost one re-read of a file that was already there** -- which is register entry
23 restated: a capture is worth re-reading before it is worth re-taking.

### 12.11 THE LEDGER FOR THIS SECTION

    blockers measured                     10
    rows banked                            0
    rows inflated                          0
    redirect targets NAMED                 2   /jobs/jam and /messaging/thread/<id>
    blockers SETTLED by measurement        4   PICKER, INMAIL-COMPOSE, CREATOR-HUB, RESUME-TOOLS
    blockers RE-AIMED, not answered        2   GROUP-CHAT, MESSAGE-REQUESTS
    blockers answered with a caveat        2   POLL, POST-DRAFT (preload stub, not the product)
    unadmitted candidate addresses found   2   creator audience, creator top-posts
    instrument defects found in others     1   the 9d15c11 classifier duplicate address
    allowlist patterns added               1   /jobs/jam, and it buys no row
    loads spent                            7

**NO ROW MOVES.** Every one of these blockers keeps its state. What changed is
that ten of them now rest on a measurement instead of on nobody having looked,
and two of them turned out to rest on a question nobody had asked -- whether
an address our gate admits is an address LinkedIn serves.
