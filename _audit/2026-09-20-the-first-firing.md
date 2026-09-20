# The first firing: two Premium collections opened, and what the numbers cost to believe

Wave `premium-unfired-2`, 2026-09-20, from master `0882d35`, in the MAIN
checkout because `_state/` is gitignored and absent from every worktree.

**A FIRING WAVE.** Four LinkedIn addresses were loaded, read and captured.
`writes_enabled` was false throughout and nothing was connected, messaged,
applied to, followed, saved or posted. Chrome on 9224 and the server on 8322
were left running.

---

## 0. THE LEDGER LINE, FIRST

    rows banked out of GAP                 1    J 125  GAP -> COVERED-PROVEN
    rows inflated (state 0)                0
    census states otherwise edited         1    J 127  GAP -> MEASURED-ABSENT
    tools shipped                          1    linkedin_premium_job_collection
    unwired rulings deleted                2    both named this as their trigger
    shipped-reader DEFECTS found           1    dom.read_profile_views_insights
    live page loads spent                  5
    captures written to _state (gitignored) 4
    raw captures committed                 0
    scripts harvested                      2

**THE LEDGER SAID 2 UNTIL I CHECKED IT, AND THE CORRECTION IS WORTH MORE THAN
THE NUMBER.** I had written *"2 rows banked -- J 125 and its top-choice twin"*.
Both halves were wrong. **There is no census row for top-choice** -- the surface
is real and now read, and nothing in the census corresponds to it, so it cannot
bank one. And **`COVERED-PROVEN` is defined as "a tool exists and is recorded
working"**, while `job_collections.py` had no tool at all: it was ruled
`DELIBERATELY_UNWIRED`. On the evidence I had when I wrote that line, the honest
figure was **zero**, and the wave would have reported two.

That is why this wave also ships the tool. Both rulings that held the module
unwired name the same trigger in their own text -- *"delete this line in the
same commit that fires the reader live and wires the tool"* -- and firing it is
what this wave did first.

**AND THE ONE NUMBER THAT ALMOST WENT OUT WRONG.** The first run reported 25
slots on all three addresses it opened. Three different addresses agreeing to
the posting is what a REDIRECT looks like, and the reading could not tell that
apart from a page window that happens to be 25. **Nothing banked until that was
settled**, and settling it took a second instrument, not a second opinion.

---

## 1. WHAT THE BRIEF GOT WRONG, AND IT MATTERS FOR WHERE THE WORK WENT

The brief's Priority 1 reads *"fire `linkedin_job_collections`, which has never
run against LinkedIn"*. Both halves are wrong, and in opposite directions.

**THE TOOL OF THAT NAME IS NOT THE PREMIUM READER AND HAS ALREADY FIRED.**
`linkedin_job_collections` in `linkedin_server/server.py` targets
`collections_page.COLLECTIONS_URL` -- `/jobs/collections/recommended/` -- and
its own docstring records it firing live on 2026-09-19, in process and then
over the MCP transport against a restarted server.

**THE PREMIUM READER IS `linkedin_server/job_collections.py`, AND NO TOOL
REACHES IT.** It is ruled in
`tests/test_every_orphan_module_is_ruled.DELIBERATELY_UNWIRED`, which says in
as many words: *"What it cannot have is a wired tool... NOT PERMANENT, and the
unblocking step is one page load: see `_audit/2026-09-20-the-premium-four.md`
section 9."*

So there was no tool to call and the firing had to be a script. That is
recorded here because a successor reading the brief cold would spend the
session looking for a tool call that settles nothing.

---

## 2. PER SURFACE -- THE CALL, THE LANDING, BOTH TIERS, AND THE ROW

Fired by `scripts/_probe_premium_collections_live.py`, twice: once at 15:59
and once at 16:02 after the landing check below was added. **Both runs agree on
every count**, which is the only reason the second run is quoted rather than
averaged.

### 2a. The two controls, because a zero here has three causes and not two

    CONTROL 1  the synthetic fixture, via set_content, NO page load
               8 of 8 pinned fields matched, job_ids 3 of 3
               -> the reader can count

    CONTROL 2  /jobs/search/ -- a LIVE LinkedIn job list, through THE SAME
               READER
               slots 25, hydrated 7, list_container_seen True
               -> the selectors measured off captures on 2026-09-20 still
                  match what LinkedIn draws today, on this account

**CONTROL 2 IS THE ONE THE PREMIUM-FOUR WAVE COULD NOT RUN**, and it is the
one that matters. That wave proved its reader against markup that wave
authored. This is a test; it is not a measurement.

### 2b. The three readings

| surface | call | landing | slots (T1) | hydrated (T2) | containers | seen |
|---|---|---|---|---|---|---|
| `/jobs/search/` | `read_job_collection(page)` | path survived, query added | **25** | 7 | 7 | True |
| `/jobs/collections/top-applicant` | `assert_read_url(collection_url(0))`, goto, `read_job_collection(page, expect=0)` | path survived, query added, route word kept | **25** | 9 | 7 | True |
| `/jobs/collections/top-choice` | the same, `collection_url(1)`, `expect=1` | path survived, query added, route word kept | **25** | 9 | 7 | True |

`slots_outside_main` was 0 on all three, so the list is inside `main` on the
live surfaces and the scope control found nothing hiding. `ids_refused` 0 and
`empty_state_needles` 0 on all three. No `refusal`, no `error`.

**BOTH TIERS ARE REPORTED BECAUSE THE FIRST VERSION OF THIS READER COUNTED THE
WRONG ONE.** It counted hydrated cards and would have reported 9 where the
collection holds 25 -- a 2.8x undercount here, 3.4x on the captures that
caught it. `slots` is the posting count; `hydrated` is how much of it LinkedIn
had drawn at that instant.

### 2c. THE LANDING, MEASURED RATHER THAN ASSUMED

The first run printed only `_relation`'s verdict, which compares the WHOLE
url -- so LinkedIn appending a tracking query reads as *"SERVED, same depth,
different url"*, **indistinguishable in that output from a redirect to another
page**. Three addresses reporting 25 made that ambiguity load-bearing.

The second run separates path from query, using comparisons only (a comparison
yields a boolean whatever it compared, which is why neither line needs a
sanitiser):

    path survived        True   on all three -- the PATH was untouched
    query added          True   on all three -- LinkedIn appended one
    route word kept      True   on both targets -- the landed path still
                                contains its own collection's route word

**NO REDIRECT. The 25 is the page window.**

---

## 3. THE COUNT COULD NOT SETTLE IT AND THE SET COULD -- `_compare_collection_captures.py`

A count cannot tell three collections from one page served three times: two
lists of 25 report 25 whether they hold the same 25 or a disjoint 25. **The
IDENTITY of the slot-id set can, and it cost zero page loads** because the
captures were already on disk.

    pair                                  |A|  |B|  shared  jaccard
    ----------------------------------------------------------------
    jobs-search      vs top-applicant      25   25       0    0.000
    jobs-search      vs top-choice         25   25       0    0.000
    top-applicant    vs top-choice         25   25      11    0.282
    top-applicant    vs recommended(prior) 25   24       2    0.043
    top-choice       vs recommended(prior) 25   24       3    0.065

**DISJOINT from the control, and 11 of 25 shared with each other.** That is
exactly the shape two Premium collections drawn from one recommendation pool
must have: neither identical (one page) nor disjoint (unrelated pools). No
pair is identical, so no reading is a restatement of another.

Capture sizes agree: 1,576,043 / 1,711,771 / 1,725,907 chars, and the `<title>`
lengths differ (30 / 50 / 48). Three documents.

**THE INSTRUMENT IS HARVESTED, NOT DISPOSABLE.** It ships as
`scripts/_compare_collection_captures.py`, it prints set sizes and
intersections and never an id, and it reports a named-but-absent capture rather
than silently dropping it from the comparison.

---

## 4. THE RULING ON `J 127` / `M M4` / `N 157` -- AND IT IS NOT THE ONE THE BRIEF EXPECTED

Three rows describe reading the InMail credit balance:

    J 127   Read the InMail credit balance          GAP `SKILL`, re-opened today
    M M4    View available InMail credit balance    EXCLUDED-RULED
    N 157   View your available InMail credits      EXCLUDED-RULED

### 4a. The re-open was right about the instrument and wrong about the conclusion

`J 127`'s re-open argues that `read_premium_surface` **never looked**: it
tallies 16 self-authored needles, 8 entitlement and 8 upsell, not one about a
balance, a credit or a number, and it returns an integer, a boolean, `None` or
one of our needle names by construction. **That is correct and it is the right
kind of catch** -- a verdict resting on an instrument that could not have
produced it.

**But "this instrument could not have seen it" is a fact about the instrument.
It is not evidence that the thing is there.** Banking GAP on it makes the same
move the original cell made, in the opposite direction: it converts a
statement about a reading into a statement about LinkedIn.

### 4b. Three instruments have now looked, and each one could speak

1. `9a140a3` s13.3 -- whole-document **rendered-text** census of
   `/premium/my-premium/`: `inmail` 0, `credit` 0, on a pass that named
   `premium` 9, `insight` 3, `applicant` 1, `top applicant` 1, `interview` 1,
   `recruiter` 1, `manage` 2, `edit` 1. The control fires.
2. `9a140a3` s12.6 -- `/messaging/compose/`: `credit` 0, `premium` 0,
   `subject` 0 in text and in the accessibility tree; `inmail` 4, which is the
   conversation filter pill and not a balance.
3. **This wave, corpus-wide, all 25 captures in `_state/`, raw AND rendered:**

    needle       RAW                              RENDERED
    ---------------------------------------------------------------------
    balance      0 on all 25                      0 on all 25
    remaining    5 on one capture                 0 on all 25
    credit       17-31 on 19 captures             1, on ONE capture
    inmail       4-24 on many                     4 on compose, 4 on messaging
    digits adjacent to a credit word, RENDERED    0 on all 25

   The rendered control needles are non-zero on every one of the 25, so no
   pass was blind. The single rendered `credit` is word-bounded on both sides
   with no digit within 40 characters -- a word, not a balance.

### 4c. THE RAW COUNTS ARE THE TRAP, AND THIS IS THE MEASUREMENT OF IT

`credit` measures **30 raw and 0 rendered** on the composer capture; `premium`
measures 790 raw and 0 rendered there. Those are the JS bundle. **A raw census
of that surface would argue an InMail balance that the page does not draw** --
which is the brief's own warning, now with a number against it.

The brief states the string counts *"16-21 times RAW and 0 times RENDERED"*.
Half right, and the half that is wrong is the half that matters: `credit` is 0
rendered, **`inmail` is 4 rendered** on compose and messaging. Conflating the
two needles is precisely how a wave nearly reported the opposite.

### 4d. THE RULING

**CORRECTS:** `_audit/_census/jobs.md` -- row `J 127` was re-opened to GAP on
2026-09-20 on the ground that `read_premium_surface` could not have seen an
InMail balance. That ground is correct and does not support the conclusion: it
is a fact about the instrument, not evidence the balance exists. Three
instruments have since looked, including a raw-versus-rendered sweep over all
25 captures with firing controls, and the balance is drawn nowhere. The row
returns to MEASURED-ABSENT with a named reopener.

**The three rows AGREE ON SUBSTANCE and the disagreement was `J 127` alone.**
`J 127` is edited to **MEASURED-ABSENT `SKILL`**, with the reopener named
rather than implied: *a capture of a Premium surface not among the 25 -- the
subscription and manage pages are the untested candidates -- drawing a digit
beside an InMail or credit word.* Both corrections are left standing in the
cell, because a row that records only its latest state cannot be audited.

**THEY STILL DIFFER IN STATE WORD, AND THAT IS A REAL DEFECT I AM NAMING
RATHER THAN QUIETLY FIXING.** `M M4` and `N 157` read EXCLUDED-RULED, which
means *somebody decided not to build this*. Their reasons are not decisions --
they are measurements: *"the balance is not on the page"*, *"the balance is not
on the composer"*. **`9a140a3`'s own kind-classification proves it**: it files
`M 4` as **WORLD-FACT**, not US-RULING, in the table whose whole purpose is
that distinction.

I am not re-stating two rows another wave committed four hours ago on a
vocabulary question that is bigger than this wave. The evidence is recorded
here and the owner of the state vocabulary can rule it in one line. **What is
settled: all three describe one capability, the capability reads nothing
because nothing is drawn, and no page load was needed to establish it.**

---

## 5. PRIORITY 3 -- THE TWO "UNDOCUMENTED FILTERS" ARE NOT FILTERS

`dom.py` documents three filter captions on `/analytics/profile-views/`. A
sibling wave measured **five**, printed their lengths `[12, 19, 7, 32, 31]`,
and concluded *"two filters this repository has never documented"*.

**THEY ARE NOT FILTERS. They are the two options in an advertisement's feedback
form**, swept in by a fallback route. Read live, and then confirmed offline:

    caption 0  chars 12  'Past 90 days'           documented
    caption 1  chars 19  'Interesting viewers'    documented
    caption 2  chars  7  'Company'                documented
    caption 3  chars 32  an ad-feedback option    NOT A FILTER
    caption 4  chars 31  an ad-feedback option    NOT A FILTER

They are named in this file only after **both halves of the shipped identity
gate** were run over them with a firing positive control (a planted profile-slug
url matched class `linkedin slug`): `hits_in` shape classes empty on all five,
and the exact-value wordlist -- 16 names, 218 spellings -- matching none. The
raw strings are in gitignored `_state/profile-views-captions-raw.json` and
nowhere else.

### 5a. THE MECHANISM, PROVEN, AND IT IS A DEFECT IN A SHIPPED READER

`PROFILE_VIEWS_INSIGHTS_JS` takes filters by a precise anchor --
`[data-view-name="search-filter-top-bar-select"]` -- and falls back, **only if
that finds nothing**, to *every `<label>` in the document* under 40 chars.

Running the shipped reader over the captures in a local headless browser, no
LinkedIn load:

    artifact                     precise holders  <label>  filters  view_names  viewer_rows
    ---------------------------------------------------------------------------------------
    today live capture                         0        5        5           0            0
    prior live capture                         0        5        5           0            0
    committed HYDRATED fixture                 3        3        3          17           11

**The live page carries ZERO `data-view-name` attributes of ANY kind** -- not
zero of the filter name, zero of the family: `line-chart` 0, `viewer-list-item`
0, `search-filter-top-bar-select` 0, on **two live captures taken days apart**.
The only artifact in this repository that has them is the committed hydrated
fixture, which has 45.

So **the tests take the precise branch and production takes the fallback**, and
the fallback is document-wide since the scope was widened to `document.body` on
2026-09-20. This is the SECOND instance of that exact shape in the same
function: its own comment records the first -- *"No fixture caught it: every
committed capture of this page has zero `<main>` elements, so the tests took
one branch and production took the other."*

### 5b. What that costs, stated as a defect and not as a curiosity

* `filters` is **contaminated** on the live page: 3 real captions plus whatever
  else the document labels, capped at 10. Any caller diffing it is diffing ad
  furniture.
* `view_names`, `view_name_counts` and `viewer_rows` are **structurally 0** on
  the live surface -- not because the page is empty, but because the attribute
  family they key on is absent. `main_chars` was 1835, the same figure
  `job_collections.py` already records for this surface.
* `dom.py`'s documented three captions are **correct and complete**. The
  sibling's inference was the reasonable reading of a length list and the
  length list could not have settled it.

**NO ROW IS BANKED OR MOVED ON THIS.** Naming the defect is the deliverable;
the reader belongs to whoever owns that surface, and changing an extraction
route on evidence this wave gathered in its last half hour is how a green test
suite gets shipped over a page nobody re-read.

---

## 6. THE CONTROL THAT DID NOT DO ITS JOB, REPORTED BECAUSE IT DID NOT

The invitation badge is read before and after as a counter that must not move.
**In the first run it appeared to move, 0 -> 1, and it had not.** The "before"
read was taken while the page still held CONTROL 1's synthetic markup -- a
document with no LinkedIn nav in it -- so the baseline was 0 by construction.
My defect, in my probe, caught by reading my own output.

The second run moves the baseline to after the first real navigation. It then
reads `badge_links=0, links=1` on `/jobs/search/` and `badge_links=1, links=1`
on the analytics page. **That is still not a clean control**, because the two
reads are on DIFFERENT SURFACES and the nav differs between them.

**So this run has no working badge control, and that is stated rather than
dressed up.** Nothing in either run clicks, fills, submits or presses -- that is
guaranteed by the code, which is the stronger guarantee -- but the instrument
that was supposed to corroborate it did not. A before/after control must be
read on the same surface; the next wave to use it should read the badge on the
control page at both ends.

---

## 7. THE HONEST LEDGER

**BANKED -- 1 row:**

* **`J 125` "Jobs where you're a top applicant", GAP -> COVERED-PROVEN.** 25
  slots, 9 hydrated, `list_container_seen` True, path survived, route word
  kept. Section 9's rule -- *"BANKS IF list_container_seen is True and slots >
  0"* -- is met, and the state is COVERED-PROVEN rather than COVERED-UNFIRED
  because `linkedin_premium_job_collection` ships in the same commit and was
  run against live LinkedIn, not only offline.

**READ AND NOT BANKED, BECAUSE THERE IS NOTHING TO BANK IT INTO:**

* `/jobs/collections/top-choice` -- the same reading (25 slots, 9 hydrated,
  `list_container_seen` True), on an id set disjoint from the control and
  overlapping its twin 11 of 25. **No census row describes this surface.** The
  tool reaches it at index 1 and the evidence is recorded here; whoever owns
  the jobs slice can decide whether a row should exist. **I am not writing one
  -- inventing a census row to have something to bank is the inflation this
  ledger exists to prevent**, and it would also move the denominator.

**NOT BANKED, AND WHY:**

* `/analytics/recruiter-views` and `/premium/profile-key-skills` -- not
  attempted. Section 9 says their deliverable is a capture and a reader built
  afterwards, and building a reader on a capture taken in the same hour is how
  the premium-four hypothesis happened in the first place.
* The profile-views defect -- named, not fixed, and not banked. See 5b.
* `M M4` / `N 157` state-word correction -- evidence recorded, ruling left to
  the vocabulary's owner. See 4d.

**WHAT I COULD NOT SETTLE:**

* Whether the 25 is LinkedIn's window or this account's holdings. Every
  captured job list reads 24 or 25 and none has ever read more, so 25 is
  almost certainly the window and the collections are **at least** 25. A
  scrolling reader would settle it; this reader does not scroll and says so.
* Whether `data-view-name` is absent from the live analytics page because
  LinkedIn stopped emitting it or because the page had not hydrated at capture
  time. Two captures days apart agree, which makes a timing coincidence
  unlikely, and it is not proof.
* The census source-ref column (`a7474394`, `a543685`, `a569649`) resolves to
  no git object in this repository. All three behave identically, so this is a
  convention I do not understand rather than a rot I found. Recorded, not
  claimed.

* Whether the wire carries the new tool. **It does not yet, and that is a
  deliberate hold rather than an oversight.** The tool is proven END TO END in
  process against live LinkedIn -- index gate refusing 4 bad inputs including
  `True` and a string, one live call, payload checked on itself -- but the
  running server on 8322 holds the code it started with, so a caller there
  still sees 45 tools. **I did not restart it**: two `linkedin.py --http`
  processes are up and another agent is running `measure_pointer_graph.py
  --selftest` on this tree, and restarting a shared server out from under a
  live wave is not mine to do on my own judgement. NEXT STEP, one line: restart
  8322 at a quiescent moment and call `linkedin_premium_job_collection` over
  the transport, which is what made `linkedin_job_collections`' name-freedom a
  property of the wire rather than of its unit tests.
* **Two `linkedin.py --http` processes are running** (pids 10800, 29200). Only
  one can hold 8322. Observed and left alone -- neither is mine, and killing a
  process another wave may own is exactly the class of action that costs a
  session. Worth somebody's look.

## 8. WHAT MOVED, AND BY HOW MUCH

**One row out of GAP, on evidence that survived its own disconfirming test.**
`J 125` GAP -> COVERED-PROVEN, with a tool shipped to reach it and two unwired
rulings deleted on the trigger they named themselves. Plus: one census state
corrected by measurement rather than by argument (`J 127`), one shipped-reader
defect found with its mechanism proven on two captures, and two instruments
harvested.

**The wave was aimed at moving GAP and it moved it by one.** It could have
reported two by not checking what `COVERED-PROVEN` requires, and four by
counting top-choice and the analytics surface as rows. One is the number that
is true.
