# The Premium four: what a drawn address is worth before anybody opens it

Wave `premium-four`, 2026-09-20, from master `dc5aaa6`, in a linked worktree.
**A BUILD WAVE.** No browser was opened, no LinkedIn address was loaded, no
session was touched, `writes_enabled` was never true, and nothing was
connected, messaged, applied to, followed or posted. Everything below is
offline over captures a sibling wave already paid for.

---

## 0. THE LEDGER LINE, FIRST

    rows banked out of GAP                 0    NOTHING FIRES IN THIS WAVE
    rows inflated                          0
    allowlist patterns added               see section 7
    readers shipped                        see section 7
    surfaces PRICED and declined           see section 7
    fixtures committed                     synthetic only; zero captures committed
    captures read                          6, by absolute path, read-only
    live page loads spent                  0

**THE THING THIS WAVE CANNOT DO, SAID FIRST.** Not one of the four target
addresses has ever been opened by anybody. There is no capture of any of
them. Every fixture here is built from the shape of a SIBLING surface that
HAS been captured, and that makes each reader a HYPOTHESIS about a page
nobody has seen. A reader proven against such a fixture is a reader that
works IF the target uses the sibling's template. That is a real deliverable
and it is not a banked row, which is why section 9 names the exact call that
would bank each one and why every count in this document stays GAP.

---

## 1. RE-DERIVED BEFORE ANYTHING WAS BUILT

The brief handed me four routes and an allowlist count. Both were re-taken
from the tree rather than believed, because a number relayed between agents
is a reading with a timestamp the receiver cannot see.

    _ALLOWED_URL_PATTERNS                  36
    digest of the pattern texts            01a3e6b6255aa7e2
    route shapes drawn across 6 captures   43
    of those, admitted                      7
    of those, refused                      36

Taken by running the SHIPPED instrument, not a reimplementation:

    scripts/_probe_premium_surfaces_shape.py --control      4 of 4 controls pass
    scripts/_probe_premium_surfaces_shape.py --state <main>/_state

All four target routes reproduce as DRAWN and REFUSED:

    refused   /analytics/recruiter-views                   1 surface(s)
    refused   /jobs/collections/top-applicant              1 surface(s)
    refused   /jobs/collections/top-choice                 1 surface(s)
    refused   /premium/profile-key-skills                  1 surface(s)

### 1a. AND THE REFUSAL IS THE ALLOWLIST ANCHOR, NOT THE DENYLIST

Measured through the shipped predicate for all four, because a boundary test
that does not establish this passes for the wrong reason -- if a forbidden
substring were doing the refusing, removing a candidate pattern would change
nothing and the "only thing standing" assertion would certify nothing:

    url                                            forbidden_hits   is_read_url
    /analytics/recruiter-views/                    []               False
    /jobs/collections/top-applicant/               []               False
    /jobs/collections/top-choice/                  []               False
    /premium/profile-key-skills/                   []               False

Four empty lists. Gate one has nothing to say about any of these addresses,
so gate two is the whole of the refusal and a candidate pattern is the whole
of the admission.

### 1b. ARE THEY DRAWN, OR ARE THEY BUNDLE STRINGS? -- ASKED, BECAUSE THE SHIPPED PROBE DOES NOT ASK IT

The four routes arrive from `scripts/_probe_premium_surfaces_shape.py`, whose
route inventory is built by `re.findall(r'href="..."')` over the **RAW**
document -- scripts, styles and LinkedIn's `<code>` model payloads included.
That is the exact extraction class this wave is warned about, applied by the
instrument the warning came from. Its own census strips those tags; its route
section does not.

So the premise was re-tested rather than inherited. Anchors were re-extracted
from the STRIPPED markup only, and matched as `<a href=...>` rather than as a
substring:

    capture              route                               raw  strip anchor
    premium-hub          /jobs/collections/top-applicant       1      1      1
    premium-hub          /jobs/collections/top-choice          1      1      1
    profile-views        /analytics/recruiter-views            2      2      2
    search-appearances   /premium/profile-key-skills           2      1      1

**ALL FOUR ARE DRAWN ANCHORS.** The premise holds and the wave proceeds.

**AND THE RAW/RENDERED GAP IS REAL EVEN HERE, ONCE:**
`/premium/profile-key-skills` occurs TWICE raw and ONCE rendered on
`search-appearances`. One of its two occurrences is a bundle string. Counting
raw would have reported that surface drawing the route twice as often as it
does.

### 1c. AND THE DEFECT I WENT LOOKING FOR IS NOT THERE -- REPORTED STRAIGHT

The hypothesis was that the shipped probe's raw extraction inflates its route
inventory with addresses no anchor draws. It was measured, over all six
captures, by building both sets through the SAME shipped reducer:

    route shapes from ANY href= anywhere (the shipped probe's set): 43
    route shapes from a DRAWN <a href=> in stripped markup        : 43
    shapes the shipped set holds that NO drawn anchor produces    :  0

**THE TWO SETS ARE IDENTICAL AND MY HYPOTHESIS IS REFUTED.** On this corpus
every `href=` outside an anchor resolves to a shape some anchor also draws,
and the anchor count equals the raw anchor count on all six captures
(25/45/26/33/29/26, stripped == raw). The shipped inventory of 43 is right.

It is right **by luck of this corpus and not by construction**, which is a
different sentence and the one worth keeping: the extraction would admit a
`<link href=>` or a bundled string on a capture that carried one, and nothing
in the probe would say so. That is a named limit of an instrument that is
currently correct, not a defect to fix, and it is recorded rather than acted
on.

---

## 1d. THE BLAST-RADIUS INSTRUMENT IS BLIND TO THIS WAVE, AND THAT IS A FACT ABOUT ITS CORPUS

`scripts/blast_radius.py` is this repository's shipped answer to "what would
this candidate pattern newly admit". It was imported rather than
reimplemented, and run over its own corpus for the four candidates and five
deliberately over-broad mutations:

    candidate / mutation             newly_admitted   newly_refused
    /jobs/collections/top-applicant           0             0
    /jobs/collections/top-choice              0             0
    /analytics/recruiter-views                0             0
    /premium/profile-key-skills               0             0
    MUT /jobs/collections/<class>/            0             0
    MUT /analytics/<class>/                   0             0
    MUT /premium/<class>/                     0             0
    MUT /jobs/collections/.*                  0             0
    MUT /premium/.*                           0             0

**A `.*` WILDCARD OVER `/premium/` MEASURED A BLAST RADIUS OF ZERO.** The
instrument's own docstring names this failure by name -- *"a tool that reports
zero for everything is indistinguishable from a broken one"* -- so the zero was
treated as a question rather than as an answer, and the corpus was counted:

    corpus size                                    67
    addresses under /jobs/collections/              0
    addresses under /premium/                       0
    addresses under /analytics/                     1   (already admitted)

**THE INSTRUMENT IS NOT BROKEN AND ITS ANSWER IS HONEST.** Its docstring
states the limit in advance: *"a diff over a corpus is a LOWER BOUND on the
blast radius, never the whole of it... an address nobody thought to put in the
corpus is invisible here, and its absence from the output is a fact about the
corpus."* This wave is the case that limit was written for. The corpus is
assembled from the forbidden roster plus the families this package has argued
about, and nobody has ever argued about `/premium/`.

**SO THE ZERO IS NOT EVIDENCE AND MAY NOT BE CITED AS ONE.** What this wave
does about it is section 7.

## 1e. THE DENOMINATOR THIS WAVE BUILT, AND THE TWO DEFECTS IT EXPOSED IN THE SHIPPED PROBE

`scripts/drawn_route_corpus.py` -- new, and the answer to 1d. It extracts every
route shape a **DRAWN ANCHOR** produced across the six captures, reduces it
through the SHIPPED reducer (imported, never re-written), substitutes tokens
this repository already sanctions for the member-bearing and id-bearing
segments, and writes a **tracked, name-free** corpus to
`tests/fixtures/synthetic/drawn_routes.txt`.

The tracked file is the whole point: `_state/` is gitignored, carries a member
urn in its lix blob, and exists in neither a worktree, a clone nor a CI
checkout. A boundary test that needed the captures could not run anywhere that
matters.

    surfaces read                     6
    distinct route shapes (depth 6)  44
    concrete addresses emitted       44
    digest                           ffce941a69018a19
    controls                          6, all shown failing when broken

### 1e-i. IT RESTORES THE DISCRIMINATION THE SHIPPED CORPUS COULD NOT PRODUCE

Same instrument, same candidates, two denominators:

    candidate / mutation              shipped(67)   drawn(44)   combined(104)
    /jobs/collections/top-applicant        +0          +1           +1
    /jobs/collections/top-choice           +0          +1           +1
    /analytics/recruiter-views             +0          +1           +1
    /premium/profile-key-skills            +0          +1           +1
    MUT /jobs/collections/<class>/         +0          +2           +2
    MUT /analytics/<class>/                +0          +1           +1
    MUT /premium/<class>/                  +0          +3           +3
    MUT /premium/.*                        +0          +4           +4
    MUT /analytics/.*                      +0          +1           +1
    MUT /jobs/.*                           +0          +3           +3
    MUT top-applicant with a query group   +0          +1           +1

**EVERY NARROW CANDIDATE ADMITS EXACTLY ITS OWN ADDRESS AND NOTHING ELSE.**
And the mutations now separate, which is what makes the +1s mean something:

* `/premium/<class>/` reaches **`/premium/premium-perks/` and
  `/premium/switcher/`** -- two surfaces nobody has argued for, drawn on the
  Premium hub.
* `/premium/.*` reaches a **fourth**, `/premium/sb/explore/`, because a
  wildcard takes sub-paths and a character class does not.
* `/jobs/.*` reaches **`/jobs/`**, the product root.

On the shipped corpus all eleven of those numbers were zero, including the
wildcards. The difference is entirely the denominator.

### 1e-ii. DEFECT ONE: THE SHIPPED PROBE TESTS PLACEHOLDERS AGAINST THE ALLOWLIST

`_probe_premium_surfaces_shape.py` reduces an href to a shape and then asks
`is_read_url("https://www.linkedin.com" + shape + "/")` -- **with the literal
`<entity>` and `<opaque>` placeholders still in the string.** No pattern on the
allowlist can match an angle bracket, so every shape carrying a placeholder is
reported REFUSED by construction.

Measured, on this corpus, it under-reports by two:

    address                              shipped probe says   truth
    /jobs/view/<opaque>                  refused              ADMITTED
    /messaging/thread/<opaque>           refused              ADMITTED

`^.../jobs/view/\d{6,}/?$` and the thread pattern both match a real id. The
probe's "7 admitted, 36 refused" is therefore a **lower bound on admitted and
an upper bound on refused**, not the count it presents itself as. This wave's
corpus substitutes concrete sanctioned tokens before asking, which is why it
reports 8.

### 1e-iii. DEFECT TWO: DEPTH-3 TRUNCATION TURNED A REFUSED CREATE ROUTE INTO AN ADMITTED LISTING

This is the sharper one. The probe's route table lists

    ADMITTED   /learning/role-play/scenarios

and read alone that says LinkedIn draws the admitted listing address. **It does
not.** The only role-play anchor drawn on any of the six surfaces is the
CREATE route:

    /learning/                                  drawn
    /learning/<opaque>/<opaque>/                drawn
    /learning/role-play/scenarios/new/          drawn
    /learning/role-play/scenarios/              NOT DRAWN, on any surface

`shape_path`'s default depth is 3, so the drawn `/new/` segment is **truncated
away**, and what is left is the sibling address this repository admitted -- and
the probe then correctly reports that sibling as admitted. A refused create
route, in the same autosave class as `/article/newsletter/new/`, is displayed
as an admitted read.

**THE WAVE THAT OWNS THAT PROBE GOT THIS RIGHT IN PROSE AND THIS IS NOT A
CORRECTION OF ITS CONCLUSION.** `_audit/2026-09-20-the-live-capture.md`
section 6b states plainly that the `/new/` route is drawn and refused and that
the listing is *"not drawn; reached by admission"*. The defect is in the
TABLE its instrument prints, which a later reader will consult without the
prose beside it. Depth 6 is this wave's corpus default for exactly this
reason, and the constant carries the argument in the source.

Neither defect is edited here. Both belong to another wave's file, and a
one-line fix arriving with the evidence attached is cheaper for its owner than
a surprise in their diff.

---

## 2. THE MEASUREMENT DISCIPLINE INHERITED, AND WHERE IT BINDS HERE

**A NEEDLE IN THE SOURCE IS NOT A NEEDLE ON THE PAGE.** The sibling wave
measured `inmail` at 16-21 raw and 0 rendered on all six captures; a raw
census would have reported the opposite of the truth on the row the operator
asked about most. Every text-derived number in this document is printed raw
and rendered side by side, and every child brief in this wave carried the
same rule as a review criterion.

**A REFUSAL THAT REPORTS ONLY WHAT IT DID NOT MATCH IS HALF A MEASUREMENT.**
This binds the READERS here, not only the probes -- see section 5. A reader
built for a page nobody has opened will meet a DOM it does not recognise
sooner or later, and the difference between "this account has nothing" and
"I could not see" is the whole value of the reading.

**IMPORT THE SHIPPED INSTRUMENT.** Four waves reimplemented this repo's
census parse and three got a broken one. This wave imports
`_probe_premium_surfaces_shape.shape_path` / `visible_text` for reduction,
`readonly.is_read_url` for the boundary predicate, and
`scripts/blast_radius.newly_admitted` for the widening measurement. It wrote
none of those.

---

## 3. THE CAPTURES, AND WHY NOTHING DERIVED FROM THEM IS COMMITTED VERBATIM

Six files in the MAIN checkout's gitignored `_state/`, read by absolute path.
They embed the operator's name, his connections' names, his employer, his
campus, his member id, profile slugs, and a member urn inside a lix
`trackingInfo` blob. **None may ever be committed and none was.**

Every fixture in this wave is SYNTHETIC: its STRUCTURE is a measurement off a
capture and its CONTENT is invented, in the convention
`tests/fixtures/synthetic/newsletter_subscriptions.html` already established
and this repository already ships.

    (per-capture sha256, size and mtime: section 4)

---

## 4. THE MEASUREMENTS, AND THE CAPTURES THEY WERE TAKEN FROM

Three closed-form slices, each run by a child in this worktree, each reading
the captures by absolute path out of the main checkout, read-only. Every child
recorded the sha256 of every capture it read, because `_state/` is a directory
another wave may overwrite and a number pinned to no bytes is a number that
cannot be re-derived.

    capture                      sha256 (first 16)   bytes
    cap-jobs-recommended.html    979aadcf0f24e2f5    1702493
    cap-jobs-search.html         1804f0b660b57591    1555561
    cap-profile-views.html       (per slice file)     143680
    cap-search-appearances.html  (per slice file)    1522974
    cap-premium-hub.html         (per slice file)     132198
    cap-newsletters.html         (per slice file)      73903

Slice files, all name-free and derived:

    _audit/_slice-premium-four-jobshape.md
    _audit/_slice-premium-four-analyticsshape.md
    _audit/_slice-premium-four-anchors.md

### 4a. THE FINDING THAT CHANGED THE BUILD -- THE LIST HAS TWO TIERS

**IT ARRIVED FROM A SLICE I BOUNCED FOR AN UNRELATED REASON**, which is worth
recording because it is the argument for bouncing at all. The jobshape slice
came back with good numbers and no control transcript. The bounce asked for
the control and, separately, for one number it had not taken -- the
`job-card-container` CLASS TOKEN count, document-wide against inside-`main`.
Taking that number is what surfaced the second tier.

    metric                            recommended    search
    list slots       (tier 1)                  24        25
    hydrated cards   (tier 2)                   7         7
    placeholder slots                          17        18
    slots neither hydrated nor placeholder      0         0
    hydration ratio                          7/24      7/25
    cross-tier id equality                    7/7       7/7
    slot tag / list parent                 li / ul   li / ul
    id digit length                         10-10     10-10

LinkedIn draws ONE `li[data-occludable-job-id]` per posting it has placed in
the list window -- hydrated or not -- and fills only those near the viewport.

**MY FIRST READER COUNTED TIER 2, AND IT WAS ALREADY WRITTEN, TESTED AND
GREEN.** It would have reported **7 postings where the collection holds 24**: a
3.4x undercount, with a number attached to make it look measured, on the
single surface the operator named. Twenty-three tests passed against it.

Nothing in the reading would have contradicted it. That is the exact failure
shape this corpus keeps finding, and the only reason it did not ship is that a
bounce for a missing control returned a measurement nobody had asked for.

### 4b. THE SELECTOR WAS CHOSEN BY MEASUREMENT, NOT BY TASTE

Four candidates, counted document-wide and inside `main` on both captures:

    attribute                    doc-wide / in-main     doc-wide / in-main
                                    (recommended)            (search)
    class                            733 / 524             1067 / 557
    id                               249 / 148              350 / 190
    data-occludable-job-id            24 /  24               25 /  25
    data-job-id                        7 /   7                7 /   7

A reader aimed at `class` or `id` is a reader whose answer depends on where it
happens to look. `data-occludable-job-id` is on every slot and its document-wide
count equals the slot count exactly on both captures.

**AND THAT LAST FACT IS WHY THE FIXTURE NEEDS A DECOY.** Every candidate agrees
across the two scopes on every real page this wave can see. A scoping claim
proved against the captures alone would be proving nothing at all.

---

## 5. THE READERS

### 5a. `linkedin_server/job_collections.py` -- SHIPPED

One reader serving both collections. What it publishes:

    slots                    tier 1, inside main -- THE POSTING COUNT
    slots_outside_main       the scope control
    hydrated                 tier 2, inside main -- the render state
    hydrated_outside_main
    containers               the class token, inside main
    containers_outside_main
    list_container_seen      THE CONTROL a zero is only readable beside
    job_ids                  from tier 1, digits only, shape-gated
    ids_refused              candidates the gate dropped
    empty_state_needles      of a vocabulary this module authors
    refusal                  a literal of REFUSALS
    error

**`slots` IS THE ANSWER AND `hydrated` IS NOT**, and they never share a field.

**THE ONE PAGE-DERIVED VALUE IS A NUMERIC POSTING ID, AND IT IS GATED.** A
posting id is not a person: it addresses a public advertisement, the shipped
`linkedin_search_jobs` already returns them, and `/jobs/view/<digits>/` is
already admitted -- so an id handed back here is consumable by
`linkedin_job_detail` without widening anything. That consumability is the
capability: it turns "Top Applicant" from a label into postings a caller can
read. Every candidate is matched against a digits-only shape in Python before
publication; anything else is DROPPED and COUNTED. No job title, company name,
recruiter name, location or salary is read at all.

**A ZERO AND A PARSE MISS NEVER SHARE A FIELD:**

    slots == 0  and  list_container_seen True   ->  HIS ACCOUNT HAS NONE
    slots == 0  and  list_container_seen False  ->  THIS READER COULD NOT SEE

and the second carries `refusal` plus `empty_state_needles`. A page that says
"nothing here" and a page that says nothing at all are different findings --
section 11 of the live-capture audit is the case that earned that field: the
role-play listing served, rendered 17 characters in `main`, and drew no
empty-state message at all.

### 5b. THE SCOPING PROOF, WITH THE NAIVE SELECTOR SHOWN GETTING IT WRONG

The fixture carries a DECOY slot outside `main`, hydrated so that it decoys
both tiers. `tests/test_job_collections.py` installs the naive document-wide
selector and measures it:

                              shipped      naive
    slots                          10         11
    slots_outside_main              1          0
    hydrated                        3          4
    hydrated_outside_main           1          0
    job_ids                         9         10

**THE NAIVE READER DOES NOT ONLY MISCOUNT, IT CORRUPTS THE PAYLOAD** -- it
publishes the decoy's posting id as though it were one of his.

Driven the other way, with the SHIPPED reader's scope removed, every shipped
assertion fails:

    cards == 8                       FAIL
    cards_outside_main == 1          FAIL
    containers == 8                  FAIL
    containers_outside_main == 1     FAIL
    len(job_ids) == 7                FAIL

    ALL 5 SHIPPED ASSERTIONS FAILED when the scope was removed.

(That transcript is from the pre-two-tier reader; the tier rewrite kept the
same decoy mechanism and the suite's current numbers are the table above. The
older transcript is left standing rather than re-typed, because it is what was
actually run at that moment.)

### 5c. AND THE HAZARD IS NOT HYPOTHETICAL ON THIS PAGE FAMILY

A live load of `/analytics/profile-views/` parsed **12 viewer rows
document-wide and 0 inside an 1835-character `main`** -- a reader looking in
the wrong box, confirmed rather than inferred, and the second time that census
row had been closed or nearly closed on an instrument that could not have seen
it. The scope pair in this reader exists because of that measurement.

---

## 6. THE FIXTURE, AND ITS PROVENANCE STATED AS A WEAKNESS

`tests/fixtures/synthetic/job_collection.html`. Its STRUCTURE is the
measurement in section 4a; its CONTENT is invented and carries **no page text
at all** -- no job title, company name, location, salary or recruiter name.
Not redacted, not shaped: absent. Two tests assert that, one as an allowlist
over the whole document (two nav words this repository authors) and one as a
hard emptiness assertion over the list region.

Ids are a synthetic band (`1000000001` upward) chosen so nothing here could
collide with a real posting.

**IT IS A FIXTURE FOR A SIBLING'S SHAPE, STANDING IN FOR A PAGE NOBODY HAS
SEEN**, and the header says so before it says anything else. A reader proven
against it is proven to work IF the target draws what its two siblings draw.

Three deliberate divergences from the captures, each with a job:

* **the decoy slot outside `main`** -- section 5b; without it the scoping
  assertions pass while testing nothing;
* **one slot whose id is not a digit run** -- the shape gate has no reaching
  input otherwise;
* **a hydration ratio of 3/10** against the measured 7/24 and 7/25 -- close
  enough that a reader which swapped the tiers produces a visibly wrong number
  here rather than a plausible one.

And one deliberate ABSENCE: **no empty-state message.** All twelve needles
measured zero rendered on both captures; three of them (`try again`, `sorry`,
`something went wrong`) appear once each in the SOURCE and zero times rendered,
which is the bundle, not the page. Drawing one would be inventing copy LinkedIn
does not show -- the failure the newsletter fixture's header refuses by name.

---

## 7. THE BOUNDARY

    _ALLOWED_URL_PATTERNS        36 -> 40
    ast digest                   85e821d1af9060f3 -> 0225ae77ddcefe2e
    other seven digests          BYTE-IDENTICAL

No denylist, no exemption table, no `SANCTIONED_MUTATIONS`, no `<functions>`.

    pattern                                          reader   blast radius
    /jobs/collections/top-applicant/?                  yes      +1
    /jobs/collections/top-choice/?                     yes      +1
    /analytics/recruiter-views/?                       NO       +1
    /premium/profile-key-skills/?                      NO       +1

Each `+1` is exactly its own address, measured over the drawn corpus with this
wave's four entries SUBTRACTED FIRST.

### 7a. THE SUBTRACTION, AND THE SCAR -- WHICH I REPRODUCED

`tests/test_company_page_boundary.py` records that its probe measured mutations
against a roster that already admitted the target, and so reported a smaller
blast radius than it had. **I reproduced that exact mistake while writing this
wave**, re-running the measurement after installing the patterns and getting
`+0` across the board. The numbers above are the pre-installation run; the
shipped test rebuilds the roster by subtraction and asserts the removal count
rather than trusting it.

### 7b. WHAT THE FAMILY SPELLINGS WOULD HAVE COST, MEASURED

    MUT /jobs/collections/<class>/       +2   reaches BOTH collections, i.e.
                                              these two entries with the
                                              argument deleted
    MUT /analytics/<class>/              +1
    MUT /premium/<class>/                +3   reaches /premium/premium-perks/
                                              and /premium/switcher/ --
                                              surfaces nobody has argued for
    MUT /premium/.*                      +4   adds /premium/sb/explore/
    MUT /jobs/.*                         +3   reaches /jobs/ itself

**ALL FIVE MEASURE +0 AGAINST THE SHIPPED CORPUS**, including both wildcards.
That is section 1d, and it is why this wave built a denominator.

### 7c. THE TWO ENTRIES THAT SHIP NO READER, AND WHY THAT IS THE HONEST ANSWER

The brief hoped for four surfaces one line and one reader away. **TWO ARE. TWO
ARE NOT, AND SAYING SO IS THE FINDING RATHER THAN A SHORTFALL.**

**`/analytics/recruiter-views` -- the evidence is UNSTABLE.**
The page is made of recruiters, so a reader for it is a people-bearing reader,
this boundary's highest hazard class. Costed against the only captured sibling:

    data-view-name, document-wide (capture)        0
    data-view-name, inside main   (capture)        0
    viewer rows, document-wide    (capture)       24
    viewer rows, inside main      (capture)       24
    main chars                    (capture)     2256
    ---- the LIVE reading of the same address, the same morning ----
    viewer rows, document-wide                    12
    viewer rows, inside main                       0
    main chars                                  1835

**THE CAPTURE DOES NOT REPRODUCE THE LIVE DEFECT ON EITHER AXIS**, and the
slice reported that straight rather than adjusting its row-finder until the two
agreed. `dom.py`'s own `HARVEST_LINKED_CARDS_JS` docstring already predicts
why: `data-view-name` is attached by the client AFTER hydration. So **this
surface has at least two DOM generations**, and a fixture built from one would
silently test one of them.

And the shaper problem is sized: **only 7 of 24 rows carry an `/in/` anchor at
all.** A reader following member anchors misses 71% of the rows -- wrong in the
direction that looks like a clean measurement.

**`/premium/profile-key-skills` -- the evidence is ABSENT.**
No captured sibling resembles it. `cap-premium-hub.html` and
`cap-search-appearances.html` are chrome-plus-a-few-controls surfaces (3346 and
2642 rendered characters) holding no list of skills, no ranking, nothing a
key-skills reader would parse. A reader would be built from imagination.

**SO BOTH ADMISSIONS BUY NO ROW TODAY AND THE LEDGER SAYS SO.** By this
corpus's own standard -- *"a surface admitted and unusable is not a partial
win; it is a blast radius paid for nothing"* -- that is declared rather than
dressed up.

**WHAT THEY DO BUY:** you cannot capture a page you refuse to open, and the
refusal was ours. The argument, the drawn-anchor evidence and the blast radius
are the expensive half and they are done. The role-play listing was admitted on
exactly this reasoning on 2026-09-20, and the load is what settled it.

**AND IF THAT TRADE IS JUDGED WRONG, THE REVERSAL IS TWO DELETED LINES.** Each
entry is its own pattern, not an alternation, precisely so that retiring either
costs one line and disturbs no argument but its own.

---

## 7d. THE PATTERN I SHIPPED REFUSES THE EXACT URL LINKEDIN DRAWS

Found by the anchors slice AFTER the boundary had already frozen, which is
why it is a section of its own rather than a line in 7a.

Both `/analytics/recruiter-views` anchors on `cap-profile-views.html` carry a
query parameter -- **named `timeRange`; the VALUE was never read.** The shipped
pattern is anchored with no query allowance. Put to the live predicate:

    .../recruiter-views                      True
    .../recruiter-views/                     True
    .../recruiter-views?timeRange=<value>    FALSE
    .../recruiter-views/?timeRange=<value>   FALSE

**SO A CALLER THAT COPIED THE HREF OFF THE PAGE WOULD BE REFUSED BY OUR OWN
READ GATE.** The other three admitted addresses draw no query at all, and
`/premium/profile-key-skills` is drawn with no trailing slash -- both spellings
of all four are asserted in the boundary test.

**THE PATTERN IS KEPT AS IT IS, AND THE FINDING IS WRITTEN INTO THE ENTRY.**
The reasons, in order:

1. Nothing in this package builds that url yet, so there is no query to strip
   and no caller to break today.
2. A `(\?[^#]*)?` group is what the search-appearances entry exists to refuse:
   *"a pattern that accepts a query accepts whatever a caller appends."*
3. The legal values of `timeRange` are unknown, because reading the value was
   correctly out of scope for the measurement that found the parameter. An
   enumeration written from a guess would be the same error one layer down.

**IF THE BARE ADDRESS DOES NOT SERVE, THE REPAIR IS A DELIBERATE EDIT THAT
ENUMERATES THE PARAMETER** -- the `?stage=(saved|applied|draft)` shape the
jobs-tracker entry already uses -- and one page load settles the values.

This is the `/jobs/alerts/` discipline applied to a query instead of a path:
*"the address is a hypothesis and this comment will not pretend otherwise...
if the first load 404s, the correct response is to CHANGE THIS PATTERN."* The
difference is that here the mismatch is MEASURED IN ADVANCE rather than waiting
to be met as a puzzling refusal.

### 7e. AND THE BARE-SUBSTRING COLUMN IS THE BEST CONFIRMATION OF THIS WAVE'S RULE

From the same slice, and it needs no commentary:

    route                              captures drawing an ANCHOR   bare substring
    /jobs/collections/top-applicant              1                  8-10 on FOUR
    /jobs/collections/top-choice                 1                  10 on FOUR

`top-applicant` and `top-choice` occur eight to ten times as bare substrings on
captures that draw **ZERO anchors** for either route. It is ordinary job-card
badge text. **A RAW SUBSTRING CENSUS WOULD HAVE REPORTED BOTH ROUTES DRAWN ON
FOUR SURFACES INSTEAD OF ONE**, and would have argued the allowlist entries on
evidence that does not exist.

---

## 8. WHAT I GOT WRONG, IN THIS WAVE, FOUND BY MY OWN INSTRUMENTS

Four, and the first is the one that would have shipped.

**8a. MY READER COUNTED THE WRONG TIER** -- section 4a. Written, tested, green,
and wrong by 3.4x on the operator's headline surface. Caught by a bounce issued
for an unrelated reason.

**8b. MY BRIEFS PUT A REAL PERSON'S NAME IN THREE CHILD SCRIPTS.** I instructed
every child to read the captures at an absolute path whose second segment is
the operator's first name. The shape guard classified it `[drive root]` in
three files and refused the wave's commit. My error, in the brief, not the
children's. Corrected by a disk ruling at the worktree root -- and **the
ruling's own first version quoted the path in order to explain the rule, and
was refused by the rule.**

**8c. MY FIRST CONTROL CONVICTED A CLEAN REDUCER.** `drawn_route_corpus.py`'s
control 3 derived its needle by segment position -- index `[1]`, which is the
identifying segment after a member-bearing prefix and is the literal `view` in
`/jobs/view/<id>`. It reported a leak, voided a clean run, and the leak was in
the control. **A needle derived by position from the input is a rule about the
inputs that happened to be listed.** Fixed by naming the needle per case; the
scar is in the source.

**8d. I RE-MEASURED BLAST RADIUS AGAINST A ROSTER THAT ALREADY HELD MY
ENTRIES** -- section 7a -- reproducing a mistake a sibling test documents in
its own source, an hour after reading it.

**AND ONE HYPOTHESIS OF MINE, REFUTED AND REPORTED STRAIGHT** -- section 1c. I
expected the shipped probe's raw `href=` extraction to inflate its route
inventory. Measured: 43 and 43, difference 0. It is right.

---

## 8bis. THREE STANDING GUARDS WENT RED ON THIS CHANGE, AND ALL THREE WERE RIGHT

The impact gate refused the freeze with three reds. None was a false alarm and
none was worked around; each is recorded here because what a guard catches is
a better description of a wave than what its author meant to do.

### 8bis-a. A SWALLOWED EXCEPTION WOULD HAVE MISCLASSIFIED A PERSON AS NOT-A-PERSON

`tests/test_an_outage_is_never_filed_as_an_absence.py` flagged
`scripts/_probe_analytics_list_shape.py:273`:

    try:
        return shape_path(href, depth=2) == "/in/<entity>"
    except Exception:
        return False

That is `is_member_route`, and its callers read `False` as **"this anchor does
not address a person"**. So a reducer that raised would have silently
reclassified a MEMBER anchor as a non-member one -- **the unsafe direction, on
the one classification that file exists to get right, and indistinguishable
from an honest negative.**

Fixed by DELETING the handler rather than by returning `None`: `shape_path`
takes a string and does not raise on one, and if it ever does that is a defect
which must stop the run. The probe's three controls still pass and its
break-demo still exits 1.

### 8bis-b. THE READER IS UNWIRED, AND THAT NOW HAS TO BE SAID TWICE

`tests/test_readers_outside_dom_are_a_pinned_inventory.py` and
`tests/test_every_orphan_module_is_ruled.py` both refused
`linkedin_server/job_collections.py`: a reader imported by nothing, ruled by
nobody. **Both are correct and the module is deliberately unwired** -- it
shapes a page nobody has ever opened, so wiring a tool to it would hand a
caller a posting count indistinguishable from a measured one.

Entered in both tables with the reason, the cross-reference between them, and
the un-blocking step: one page load, section 9. Neither entry is permanent and
both say so.

**THE GUARDS ARE WHY THIS IS A RULING RATHER THAN A LOOSE END.** An orphan
nobody has ruled on is how a backlog grows: the code is not wrong and it is not
reachable, and nothing records which of those was intended.

### 8bis-c. A DISCLAIMER READ AS A CORRECTION

`tests/test_a_correction_is_findable_from_the_claim.py` flagged this document
citing `2026-09-20-the-live-capture.md` with correction vocabulary nearby. The
line it caught is section 1e-iii's **"THIS IS NOT A CORRECTION OF ITS
CONCLUSION"** -- the sentence refusing to do the thing the scan suspects.

Triaged onto `NOT_A_CORRECTION` with that reading, because inserting a
`CORRECTED BY:` marker into the live-capture audit would tell every future
reader its conclusion was wrong when this document says it was right. The
defect is against the SCRIPT and is filed at `INSTRUMENTS.md` 29.2.

**THE TABLE ASKS FOR TRIAGE AFTER READING THE LINE, AND THE LINE IS THE
ANSWER.** A scan that cannot tell an attribution from a correction is doing its
job by asking; answering it without reading would have published a false
retraction of somebody else's correct work.

---

## 8ter. CI WENT RED, TWICE, AND THE ROOT CAUSE IS THAT I NEVER GATED THE FILE THAT MATTERED

The wave froze green locally and went red in CI on all three platform cells.
Both reds are mine. The second one has a root cause worth more than the fix.

### 8ter-a. THE FILE CARRYING THE BOUNDARY CHANGE WAS NEVER PUT THROUGH THE IMPACT GATE

`scripts/impact_gate.py` reads the INDEX and selects tests by what the staged
diff can reach. The order I worked in:

    1. edited linkedin_server/readonly.py  (the four new patterns)
    2. ran FOUR HAND-PICKED test files, all green
    3. committed fce0843
    4. THEN staged the audit + instruments and ran the impact gate
    5. the gate analysed the AUDIT FILES, because readonly.py was already
       committed and no longer in the staged set

**SO THE ONE FILE IN THIS WAVE WITH A BLAST RADIUS NEVER REACHED THE
INSTRUMENT BUILT TO MEASURE BLAST RADIUS.** The gate was green twice and both
greens were about different bytes.

Step 2 is where the damage was done: I substituted my own guess for the
impact analysis, picked the four files whose names I associated with "the
boundary", and missed `tests/test_analytics_creator_boundary.py` -- which
has both *analytics* and *boundary* in its name and pins the analytics family
by COUNT. It failed three ways:

    a parametrized neighbour case asserting recruiter-views is REFUSED
    test_the_refusals_are_not_carried_by_this_pattern
    test_the_admitted_analytics_pages_are_exactly_three   (4 -> 5 patterns)

**THAT LAST ONE IS A TRIPWIRE THAT DID EXACTLY WHAT ITS DOCSTRING PROMISED**
-- *"A COUNT, so a fourth analytics page cannot arrive unnoticed"* -- and the
fourth analytics page was mine. It is updated deliberately, with the reason
and with the pages named individually so the count cannot be satisfied by a
duplicate. Its NAME still says "three" and is KEPT: `_audit/2026-09-20-newsletter-built.md`
cites this function by name, and this repository's own finding is that a
citation rots into a PLAUSIBLE WRONG ANSWER rather than a dangling one.

### 8ter-b. THE SAME ROOT SHAPE, TWICE, AND I DOCUMENTED THE FIRST BEFORE COMMITTING THE SECOND

Section 8bis was written about amending a document AFTER the gate had read
the index. This is the same defect one level up: gating a set that is not the
set being committed. **I wrote the first one down and then did it again in
the next commit**, which is the honest measure of how much a written lesson is
worth without a mechanism.

    THE RULE THAT WOULD HAVE CAUGHT BOTH: the gate must run on the EXACT
    staged set that becomes the commit, and any edit after it runs voids it.
    "The gate passed" is a claim with a timestamp and a byte range.

### 8ter-c. THE SECOND RED: A BASELINE RATCHET, AND WHAT IT ASKS FOR

`tests/test_probe_controls_are_never_decorative.py` gained four findings, all
in the analytics slice's probe. Its message forbids the lazy repair by name:
*"do NOT add it here to clear the red; branch on its result, or if it is a
genuinely decorative reading that was reviewed and accepted, add it to the
baseline with a one-line reason."*

Reviewed, one at a time:

* `part4() -> digit_controls` is a COUNT of digit-bearing control texts that
  the report PRINTS. It is a measured datum about the page, not a control over
  the instrument; the detector matched the substring `control` in its NAME.
  Branching on it would mean asserting a page's content, which is the opposite
  of this probe's job. Its correctness is checked by the cross-instrument
  agreement printed beside it -- premium-hub reproduces a prior wave's live
  7 and 13 exactly.
* `control() -> expected`, `break_demo() -> expected`, `break_demo() -> html`
  are INPUTS to a check whose result IS branched on. `_run_control_pass`
  returns `ok`; `control()` does `if not ok: return 1` and `break_demo()` does
  `overall_ok = overall_ok and not ok` then `if overall_ok: return 1`. The
  detector flags the binding because the name is never itself a condition,
  while the value it carries decides the exit code. **Verified by running both
  modes rather than by reading: `--control` exits 0, `--break-demo` exits 1.**

Baselined with that reasoning in the file's own `_comment`, because
`test_baseline_file_is_well_formed` pins the entry schema to exactly four
keys -- so the reason goes where the file already keeps prose rather than
widening a schema a guard holds.

### 8ter-d. WHAT CI IS FOR, DEMONSTRATED

Three platform cells, one shard, the same three failures on each. A local gate
that read the wrong bytes said PASS twice. **CI is the certifier and a green
local gate is not a reason to trust it.** The workflow's own header says so;
this wave is the case.

---

## 9. THE EXACT CALL THAT WOULD BANK EACH ROW

**NOTHING FIRES IN THIS WAVE.** Every row below stays GAP. Each line is the one
call that would move it, named precisely enough that whoever next holds the
signed-in profile spends no thought on what to run.

    surface                        the call                             banks
    ---------------------------------------------------------------------------
    /jobs/collections/top-applicant
        assert_read_url(job_collections.collection_url(0))
        navigate, then read_job_collection(page, expect=0)
        BANKS IF: list_container_seen is True and slots > 0.
        A zero with list_container_seen True is a fact about HIS ACCOUNT and
        banks the row MEASURED-EMPTY, not GAP.
        A zero with list_container_seen False banks NOTHING and means the
        target does not draw the sibling shape -- fix the reader, do not
        report that he has no top-applicant postings.

    /jobs/collections/top-choice
        the same, with collection_url(1) and expect=1.

    /analytics/recruiter-views
        assert_read_url, navigate, and CAPTURE THE PAGE to _state/.
        BANKS NOTHING BY ITSELF. Its deliverable is the capture, because the
        reader cannot honestly be built until the target's own shape is
        known -- section 7c. Build the reader from that capture, then fire.

    /premium/profile-key-skills
        the same: one load, one capture, and the reader afterwards.

**ONE MORE READ IS WORTH MORE THAN ALL FOUR OF THESE AND COSTS THE SAME.**
Re-open `/analytics/profile-views/` and capture it. The capture this wave read
and the live reading taken the same morning disagree on both axes (section
7c), so that surface has at least two DOM generations and nobody knows which
one is normal. `N 136` has now been nearly closed twice on an instrument that
could not have seen it. A second capture is what tells the two generations
apart, and it unblocks the recruiter-views reader as a side effect.

---

## 10. THE HONEST LEDGER

    rows banked out of GAP                      0    nothing fired
    rows inflated                               0
    allowlist patterns added                    4    36 -> 40
    of those, shipping a reader                 2
    of those, buying no row today               2    section 7c, declared
    readers shipped                             1    serving two addresses
    synthetic fixtures committed                1    plus one in-module control
    captures committed                          0    and none may ever be
    live page loads spent                       0
    browser sessions touched                    0
    writes enabled                              0    at any point
    tests added                                79    50 boundary + 29 reader
    standing guards that went RED on me         3    8bis -- all three right
    guard tables amended with a ruling          3    2 unwired, 1 triage
    defects found AFTER the freeze              1    7d, kept and documented
    CI reds caused by me                        2    8ter, both fixed
    coupled tests my hand-picking missed        1    and its name said so
    instruments shipped                         1    + 6 controls, all shown failing
    defects found in my own work                4    section 8
    of those, that would have shipped           1    the tier undercount
    hypotheses of mine refuted                  1    section 1c
    defects found in other waves' work          2    section 1e, neither edited
    prior-wave numbers reproduced exactly       3    7, 13, 3346/3344
    prior-wave numbers CONTRADICTED             2    section 7c, reported straight
    surfaces priced and declined for a reader   2

**THE DELIVERABLE IS TWO WORKING SURFACES AND TWO HONEST REFUSALS**, not four
readers. The brief asked for that trade explicitly and this is it: an honest
"two of four, and the other two need one page load each" beats four readers
built on a sibling's guess, one of which would have been built on a surface
whose two captures disagree with each other.

**THE NUMBERS IN THIS DOCUMENT WERE RE-DERIVED FROM THE ARTIFACTS BEFORE IT
WAS FROZEN**, because a wave that writes numbers into prose should re-take them
from the tree rather than from its own earlier sentences -- the discipline that
caught a stale admitted-count and an understated needle count in the wave
before this one.
