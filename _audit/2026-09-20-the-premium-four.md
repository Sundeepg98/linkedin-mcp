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

## 4. THE MEASUREMENTS -- pending

## 5. THE READERS -- pending

## 6. THE FIXTURES -- pending

## 7. THE BOUNDARY -- pending

## 8. WHAT COULD NOT BE BUILT, AND WHAT IT ACTUALLY COSTS -- pending

## 9. THE EXACT CALL THAT WOULD BANK EACH ROW -- pending

## 10. THE HONEST LEDGER -- pending
