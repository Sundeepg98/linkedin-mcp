<!-- secret-scan-allow: sha256-file-hashes-not-secrets -->
# Slice: analytics-list DOM shape (premium-four wave)

Offline shape read of two analytics surfaces (cap-profile-views.html,
cap-search-appearances.html) and one Premium surface (cap-premium-hub.html),
for two never-opened readers: /analytics/recruiter-views and
/premium/profile-key-skills. Probe: `scripts/_probe_analytics_list_shape.py`.
Reducer imported unchanged from `scripts/_probe_premium_surfaces_shape.py`
(`shape_path`, `visible_text`). Row-finding ported from
`linkedin_server/dom.py`'s `HARVEST_LINKED_CARDS_JS` `rowOf()` (same
three-stop rule: container boundary, LI/ARTICLE, data-view-name), since there
is no live DOM here to run the JS itself against.

Run from the worktree root:

    ../../../venv/Scripts/python.exe scripts/_probe_analytics_list_shape.py --state ../../../_state
    ../../../venv/Scripts/python.exe scripts/_probe_analytics_list_shape.py --control
    ../../../venv/Scripts/python.exe scripts/_probe_analytics_list_shape.py --break-demo

`--state` defaults to the main checkout's `_state/` two directories above the
usual worktree location; pass it explicitly if that default does not resolve.

---

## 0. LEAD RULING APPLIED (`_TEAM_LEAD_premium_four.md`, sampled 2026-09-20 12:05)

The ruling named this file directly: `scripts/_probe_analytics_list_shape.py:771
[linkedin slug] x6`. Both items below are FIXED and re-verified; the ruling's
item 1 (hardcoded drive-root path) named two OTHER files, not this one --
checked, this file has no literal path string anywhere in it (it derives
`DEFAULT_STATE` from `Path(__file__).resolve()`, same pattern the ruling
prescribes).

* **Re-spelled three invented slugs to the three ALREADY-SANCTIONED tokens.**
  `aa-synth-row` / `bb-synth-row` / `cc-synth-decoy` (6 occurrences: 3 in the
  control document's HTML, 3 repeated in a control assertion) looked
  synthetic by construction (short, hyphenated, digit-free) but were not the
  literal strings this repo's identity guard already allowlists. Replaced
  with `placeholder-slug` / `example-org-slug` / `example-campus-slug` --
  the same three already committed and passing in
  `_probe_premium_surfaces_shape.py`'s own CONTROL 3. Re-verified: CONTROL 2
  below still shows 0 of 3 surviving redaction.
* Left `_TEAM_LEAD_premium_four.md` IN PLACE rather than deleting it on ack.
  It is addressed to "every child in this worktree" and its item 1 names two
  files this agent does not own (`_probe_job_list_shape.py`,
  `_probe_premium_four_routes.py`); deleting a shared instruction sheet
  before every named recipient has applied their part risks hiding it from
  a sibling. Flagging this choice for the lead rather than acting on an
  ambiguous multi-recipient ack unilaterally.

---

## 1. CAPTURE MANIFEST

    file                              bytes mtime (UTC)         sha256
    profile-views                    143680 2026-09-20 04:32:17 c1b69e19e4d35da7d4643373f98b8c45415e9e596f15bb7dadd1eefaccd6d026
    search-appearances              1522974 2026-09-20 04:32:26 bfd0ca088b053cf13a641538c70ae5ea2f7d160dd04261461457f545a21007b8
    premium-hub                      132198 2026-09-20 04:31:59 b80e473e160ede644fe3b3ca11887ba9e9c0794e85d116963a45cb97a312854a

All three present and read from the main checkout's `_state/`; none are
tracked and none exist inside this worktree (gitignored, confirmed absent
before this run).

---

## 2. PART 1 -- ANALYTICS PAGE FRAME, PER CAPTURE

### profile-views

    raw=143568  rendered(shipped visible_text)=2463  (1.7% of raw)
    rendered(tree-walk, same rule, whole doc)=2445  (parity check vs shipped: DIFFERS by -18)
    <main> elements: 1
    main_chars=2256  (91.6% of the page's rendered text)
    <nav> count: 2
    <header> count: 3
    <footer> count: 2
    <aside> count: 2
    <section> count: 2
    headings total: 4  (h1=0, h2=3, h3=0, h4=0, h5=0, h6=1)
    primary-content landmark stack (outermost first): main
    identified via: <main> element, document order 0 (n=1 found)

### search-appearances

    raw=1520180  rendered(shipped visible_text)=2642  (0.2% of raw)
    rendered(tree-walk, same rule, whole doc)=2619  (parity check vs shipped: DIFFERS by -23)
    <main> elements: 1
    main_chars=2035  (77.0% of the page's rendered text)
    <nav> count: 1
    <header> count: 3
    <footer> count: 1
    <aside> count: 3
    <section> count: 9
    headings total: 7  (h1=1, h2=6, h3=0, h4=0, h5=0, h6=0)
    primary-content landmark stack (outermost first): main
    identified via: <main> element, document order 0 (n=1 found)

### The -18 / -23 parity gap is explained, not open

The shipped `visible_text()` (regex-based, operates on the raw string) and
this file's `rendered_text()` (tree-walk, same strip/collapse rule, but scoped
to any subtree) disagree by a small amount on both real captures despite
agreeing EXACTLY on the synthetic control (see CONTROL 3 below). Measured
mechanism, not left as a mystery: `rendered_text()` runs with
`convert_charrefs=True`, so an HTML entity in real visible text (`&amp;`,
`&#8217;`, ...) DECODES to its one-character form; the shipped reducer never
decodes anything, since it only strips tags from the raw string. A
stripped-tag-aware entity count (script/style/code/template/noscript content
excluded on both sides, since neither method's "rendered text" ever included
it) gives:

    capture              entities outside stripped tags   raw chars   decoded chars   shrinkage
    profile-views                       4                     20            4            16
    search-appearances                  5                     28            5            23

search-appearances: 23 == 23, exact. profile-views: 16 vs the observed 18,
off by 2 -- consistent with one leading- and one trailing-boundary space the
two methods place slightly differently, negligible against a base of 2445
characters. Both open/close tag counts (for every STRIPPED_TAGS name) were
checked and balance exactly on both captures, so the gap is NOT under-matched
script/style/code blocks leaking content.

---

## 3. PART 2 -- THE SCOPE DEFECT, MEASURED OFFLINE (profile-views)

    data-view-name elements, document-wide: 0
    data-view-name elements, inside <main>: 0
    row-list resolved: <div> repeated under one parent (24 row(s))
    distinct (parent,tag) signatures the anchors' rows fell into: 1
    row list orderliness (every row carries <=1 distinct member key): yes
    viewer rows, document-wide: 24
    viewer rows, inside <main>: 24
    main_chars on this capture: 2256  (prior live measurement on /analytics/profile-views/: 1835)
    ---
    VERDICT: capture DOES NOT reproduce the defect -- of 24 row(s) document-wide,
    24 are inside <main> (nonzero). What was seen instead: the row list sits
    INSIDE <main> on this capture, contradicting the live document-wide/
    main-scoped gap quoted in the brief. Stated straight, not reconciled by
    adjusting the row-finder.
    viewer-row list container landmark stack (outermost first): main > section > div
    relative to <main>: inside <main>

**Stated plainly, per instruction not to force a reconciliation:** this
capture does not reproduce the live 12-document-wide/0-inside-main split at
all, on either axis nobody expected it to disagree on:

* `data-view-name` is ABSENT everywhere on this capture (0 document-wide, not
  just 0 inside `<main>`), so the attribute the live defect was framed around
  is not available here to be mis-scoped.
* The row count itself differs (24 here vs. 12 live), and the rows are
  `<div>`, not `<li>`/`<article>`.
* `linkedin_server/dom.py`'s own docstring (`HARVEST_LINKED_CARDS_JS`,
  `rowOf`) already documents exactly this shape of surface: "LinkedIn's newer
  surfaces are nested anonymous DIVs with hash-generated class names -- no
  li, no article, and data-view-name is attached by the client AFTER
  hydration, so it is there or not depending on how far the page got before
  we read it." This capture reads as one of those: a DIV-based render taken
  at a hydration/pagination state that never attached data-view-name at all,
  which is a DIFFERENT DOM generation from whatever produced the live
  12/0 reading, not the same page with the same defect reproduced.

This is a finding in its own right: **the profile-views surface itself has
at least two distinct DOM shapes** (data-view-name-bearing vs. not), and a
fixture built from this capture would be silently testing only one of them.

---

## 4. PART 3 -- PER-ROW STRUCTURE OF THE PEOPLE-BEARING LIST (profile-views, 24 rows)

    <a> anchors                    min=0 median=0.5 max=2
    distinct anchor route shapes   min=0 median=0.5 max=2
    <img>                          min=0 median=0.0 max=2
    <button>                       min=0 median=0.0 max=1
    headings                       min=0 median=0.0 max=0
    text nodes                     min=0 median=1.5 max=6
    aria-label-bearing elements    min=0 median=0.0 max=2

    rows carrying a member-route (/in/<entity>) anchor: 7 of 24
    insights/trend/summary panel distinct from the row list: NOT FOUND

**7 of 24 (29%) is the SHAPER number.** 17 of 24 rows (71%) carry NO anchor
to a person at all -- consistent in direction with `dom.py`'s own docstring
("privacy-limited viewers... six of ten viewers were invisible this way"),
and a LARGER fraction here. Any reader for `/analytics/recruiter-views` that
follows `/in/` anchors only will miss the majority of rows on a page shaped
like this one; that is a shaper problem, not only a boundary (main-scoping)
problem, exactly as the brief framed it.

No distinct insights/trend/summary panel was found as a sibling of the row
list inside `<main>` on this capture. Consistent explanation, not forced:
`scripts/_probe_analytics_controls_live.py`'s own docstring records that on
this same surface family, the trend graph / notable viewers / top
locations-industries-companies panels are ALL behind an unpressed control
("Nobody has pressed anything there"). An unpressed capture would show
exactly what was found here: no separate panel in the DOM to report on.

---

## 5. PART 4 -- THE /premium/profile-key-skills BASIS

### premium-hub

    control texts examined (<button>/<a>/role=button|link|tab): 54
    digit-bearing rendered control texts: 7
    aria-label-bearing elements: 27
    digit-bearing aria-labels: 13
    prior wave (premium hub, live): 7 control / 13 aria-label -- control MATCHES, aria-label MATCHES

    /premium/... route shapes drawn: 3
      /premium/premium-perks                   anchors=5  landmark stack(s): main > section > section > section > a
      /premium/sb/explore                      anchors=5  landmark stack(s): main > section > section > a
      /premium/switcher                        anchors=1  landmark stack(s): main > aside > a

    rendered length: unstripped=3346  stripped=3344
    prior wave (premium hub, live): 3346 unstripped / 3344 stripped -- unstripped MATCHES, stripped MATCHES

    empty-state / error needle census (16 needles, author's own):
      needle                         raw  rendered
      no results                       0         0
      nothing to show                  0         0
      nothing here                     0         0
      no data available                0         0
      something went wrong             1         0   <- SOURCE ONLY
      try again                        1         0   <- SOURCE ONLY
      we could not                     0         0
      unable to load                   0         0
      not found                        0         0
      no activity yet                  0         0
      no viewers yet                   0         0
      temporarily unavailable          0         0
      please refresh                   0         0
      no matches found                 0         0
      isn't available                  0         0
      an error occurred                0         0

All three prior-wave numbers reproduce exactly (7, 13, 3346/3344).

### search-appearances

    control texts examined (<button>/<a>/role=button|link|tab): 47
    digit-bearing rendered control texts: 7
    aria-label-bearing elements: 32
    digit-bearing aria-labels: 3

    /premium/... route shapes drawn: 1
      /premium/profile-key-skills              anchors=1  landmark stack(s): main > section > a

    rendered length: unstripped=2642  stripped=2640

    empty-state / error needle census (16 needles, author's own):
      needle                         raw  rendered
      no results                       0         0
      nothing to show                  0         0
      nothing here                     0         0
      no data available                0         0
      something went wrong             1         0   <- SOURCE ONLY
      try again                        1         0   <- SOURCE ONLY
      we could not                     0         0
      unable to load                   0         0
      not found                        0         0
      no activity yet                  0         0
      no viewers yet                   0         0
      temporarily unavailable          0         0
      please refresh                   0         0
      no matches found                 0         0
      isn't available                  0         0
      an error occurred                0         0

`/premium/profile-key-skills` is drawn exactly once on search-appearances,
one anchor, landmark stack `main > section > a` -- this is the fixture basis
for a never-opened page the brief asked for.

Neither capture shows any empty-state/error text once scripts, styles and
`<code>` payloads are stripped: both "something went wrong" and "try again"
hits are SOURCE-ONLY (inside the Ember bundle / lix blob, not drawn).

---

## 6. CONTROL (passing)

    === CONTROL 1  THE EXTRACTOR IS RIGHT ON A KNOWN DOCUMENT
        data-view-name doc-wide:   got=4 expected=4
        data-view-name in <main>:  got=3 expected=3
        rows doc-wide:             got=3 expected=3
        rows in <main>:            got=3 expected=3
        rows with member anchor:  got=2 expected=2
        all five counts matched their authored truth.  PASS
    === CONTROL 2  THE REDUCER STILL REDACTS ON THESE SYNTHETIC SLUGS
        /in/placeholder-slug     -> /in/<entity>
        /in/example-org-slug     -> /in/<entity>
        /in/example-campus-slug  -> /in/<entity>
        0 of 3 survived.  PASS
    === CONTROL 3  THE STRIPPER USED FOR rendered_text() MATCHES visible_text()
        shipped visible_text()=155  tree-walk rendered_text()=155  (within tolerance).  PASS

    control: all three passed -- a zero in the real run is a measurement

The synthetic control document: `<main>` holds a `<section>` holding a `<ul>`
of 3 `<li>` rows (each carrying `data-view-name`; 2 hold a member anchor, one
is a linkless privacy-limited row), plus an `<aside>` panel inside `<main>`
distinct from the list; `<footer>`, OUTSIDE `<main>`, holds one decoy `<div>`
row carrying its own `data-view-name` and a member anchor. Known-by-
construction truth: 4 data-view-name total / 3 inside main, 3 rows / 3 inside
main, 2 of 3 rows carry a member anchor.

## 7. BREAK-DEMO (the control shown able to fail; non-zero exit is correct)

    === BREAK 1  ROW-FINDING WITH THE CONTAINER STOP DISABLED
        (mirrors: a row-walk that never learns it has left one row and entered the next)
        data-view-name doc-wide:   got=4 expected=4
        data-view-name in <main>:  got=3 expected=3
        rows doc-wide:             got=3 expected=3
        rows in <main>:            got=2 expected=3
        rows with member anchor:  UNDEFINED (rows collapsed by the induced break)
        -> FAILED as expected: the corrupted extractor's counts do not match the authored truth
    === BREAK 2  data-view-name SCOPE PREDICATE FORCED TRUE (THE HISTORICAL DEFECT ITSELF)
        (mirrors: a reader that reports every row as 'inside main' regardless of where it is)
        data-view-name doc-wide:   got=4 expected=4
        data-view-name in <main>:  got=4 expected=3
        rows doc-wide:             got=3 expected=3
        rows in <main>:            got=3 expected=3
        rows with member anchor:  got=2 expected=2
        -> FAILED as expected: forcing the scope predicate true produced a main-count that no longer matches the authored truth

    break-demo: both induced breaks were caught (both mismatched truth as they should).
    exiting 1 -- non-zero on purpose, to prove a broken extractor cannot exit clean.

BREAK 1 is worth one extra sentence rather than just a pass/fail: with the
container stop disabled, `rows doc-wide` still landed on 3 -- the RIGHT
NUMBER for the WRONG REASON (the climb substituted the footer decoy row for
the linkless privacy-limited row, a different set of the same size). Only
`rows in <main>` (2 vs. expected 3) exposed it. A single top-line count can
match by coincidence while wrong underneath; that is why this file asserts
more than one number per control pass rather than trusting a single total.

---

## 8. TWO BUGS FOUND WHILE BUILDING THIS PROBE (fixed, not left in)

1. **`control_texts()` first version counted only DIRECT text-node children**
   of a `<button>`/`<a>`/role=button|link|tab element, on the theory that a
   button wrapping an icon plus a nested badge should not be double-counted.
   It returned 0 on cap-premium-hub.html despite 45 anchors and 23 buttons
   existing. Checked by walking the parsed tree and printing CHILD TAG NAMES
   ONLY (never content): every one of the first six anchors wraps its label
   in nested `<span>` children with no direct text at all -- a structural
   fact about this page's component styling, not a stricter definition of
   "control text." Fixed to read the control's own rendered SUBTREE instead
   (excluding a nested control's subtree, so it is not counted twice at both
   levels). After the fix: premium-hub's digit-bearing count reproduces the
   prior wave's 7 exactly.

2. **`_keys_within()` used `shape_path(href, depth=6)` as its distinctness
   key.** `shape_path()` collapses EVERY `/in/<anything>` to the identical
   literal `/in/<entity>` by design (that is what makes it safe to print),
   which also means a set built from it can never exceed size 1 -- the
   "this container spans more than one target" stop inside `row_of()` could
   never fire, for any document. It happened not to change any number in
   this report, because a second, independent check (raw anchor count once
   the accepted row already has text) covered for it on both the real
   capture and the control fixture. That is fixture-specific luck, not a
   property of the check, so it is fixed rather than left: distinctness is
   now a SHA-1 fingerprint of the raw href, held in memory and never
   printed, that is actually distinct per real target. Re-verified: control
   and break-demo transcripts above are unchanged after the fix; the real
   capture's numbers are also unchanged (confirming the fixture never
   depended on the bug), which is why the fix could be applied and verified
   without reopening the real-data section.

---

## 9. HEADLINE NUMBERS

    data-view-name, document-wide (profile-views capture):        0
    data-view-name, inside <main> (profile-views capture):        0
    viewer rows, document-wide (profile-views capture):          24
    viewer rows, inside <main>  (profile-views capture):         24
    rows carrying a member-route (/in/<entity>) anchor:         7 of 24
    main_chars, profile-views capture (live comparison 1835):  2256
    premium-hub digit-bearing control texts (live comparison 7):  7
    premium-hub digit-bearing aria-labels   (live comparison 13): 13
    /premium/profile-key-skills anchors on search-appearances:     1
