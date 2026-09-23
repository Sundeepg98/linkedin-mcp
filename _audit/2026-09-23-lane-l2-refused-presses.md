claude-opus-5-5[1m]

# Lane L2: nine refused presses, and none of them is a narrow extension away

**CORRECTS:** `_audit/2026-09-20-the-profile-views-recapture.md` -- its section 9.2 reports two undocumented filters of 32 and 31 characters on the profile-views page; they are the two radio labels of a closed `<dialog>` form on that page, collected by the reader's every-`<label>` fallback, and are not filters.

Wave `lane-l2-refused-presses`, 2026-09-23, from master `b0d3ab8`. **OFFLINE
THROUGHOUT.** No browser was started or attached to, no page was loaded, no
session was touched, and nothing was pressed. Every DOM fact below comes from
a raw capture already on disk in the main checkout's gitignored `_state/`,
read by a structure-only parser, or from committed fixtures, code and audits.

---

## 0. THE DENOMINATOR -- DERIVED, AND IT AGREES

**N = 9, no discrepancy.** Taken from `_audit/_census/read-addresses.tsv` by
keeping class `ADMITTED` with gate `PRESS` -- **12 rows** -- and removing the
three the order excludes (P D28, P J4, N 76: they wait on the pending ruling
about a sensitivity basis for `/in/me/`). None of the remaining nine sits under
`/messaging/` or `/notifications/`, so that exclusion removes nothing.

    M C29   /feed/update/urn:li:activity:12345/   (sort a post's comments)
    N 84    /search/results/people/               (All-filters: current company)
    N 85    /search/results/people/               (All-filters: connections of)
    N 86    /search/results/people/               (All-filters: followers of)
    N 87    /search/results/people/               (All-filters: past company)
    N 90    /search/results/people/               (All-filters: profile language)
    N 91    /search/results/people/               (All-filters: open to volunteering)
    N 92    /search/results/people/               (All-filters: service categories)
    N 133   /analytics/profile-views/             (the viewer filters)

---

## 1. THE ANSWER, FIRST

    row     verdict          the reason, in one line
    N 84    LEFT REFUSED     All filters fails condition 2 for good; the filter is a URL facet -> D1
    N 85    LEFT REFUSED     the same press; the filter is the connectionOf spelling -> D1 (and D3's cause)
    N 86    LEFT REFUSED     the same press; no facet on record
    N 87    LEFT REFUSED     the same press; the filter is a URL facet -> D1
    N 90    LEFT REFUSED     the same press; no facet on record
    N 91    LEFT REFUSED     the same press; no facet on record
    N 92    LEFT REFUSED     the same press; no facet on record
    N 133   NEEDS-CAPTURE    opening a pill is ALREADY permitted; what it opens is uncaptured;
                             applying a filter is a view switch no sanctioned press reaches
    M C29   NEEDS-CAPTURE    its control is in no capture (its state is); its only reachable
                             host is the feed; choosing an order is a view switch no
                             sanctioned press reaches

    permitted and built    0
    NEEDS-CAPTURE          2
    left refused           7
                          --
                           9

**`linkedin_server/press.py` IS UNCHANGED, AND THAT IS THE FINDING, NOT AN
OMISSION.** An extension is narrow only if it names the control by an
attribute and permits nothing beside it. Of the nine, the seven All-filters
rows need a control that carries no attribute to name (measured live twice),
on a surface whose basis would be keyed by SURFACE and so would open every
disclosure on a page made of other people's cards. The other two need a VIEW
SWITCH -- a changed selection -- which the disclosing mechanism cannot close
(`disclose` dismisses with Escape and requires `aria-expanded` equal before
and after) and which no enumerated shape names; the one place the package
already presses that class is `dom.activate_messaging_filter`, admitted for
seven named pills on one surface, matched by accessible name, which condition
2 forbids for presses. Neither is a narrowing of what exists; both are new
permissions, and section 7 files the second as one ruling request.

**No reader was built.** A reader needs a press that can be taken or a DOM
that has been recorded, and no row here has both: the seven have no press, and
the two have no capture of the thing a reader would read.

**The order's premise held for one row of the nine** -- section 2.

**Expected pin moves: NONE.** No census state moved and no table class moved.
Three rows (N 84, N 85, N 87) moved gate PRESS to RULING in the address table,
and no pin counts gates: `check_read_addresses.py` now prints PRESS 9 and
RULING 12 (was 12 and 9), and `b3_blocked_on_nothing` stays 5.

**One cross-lane finding outweighs everything above** -- section 6.1: the
press P O3 and N 134 rest on may have opened the header navigation menu, not
the analytics panel. It was sent to the live readers wave, which found the same
independently and is settling it with a zero-press live reading.

---

## 2. THE ORDER'S PREMISE, CHECKED AGAINST DISK

The order: *"Nobody ruled these presses unsafe; the gate refuses them by
default."* On disk:

* **N 84-N 92, seven rows: RULED ON AND REFUSED.** The `All filters` control
  was put through the 2026-09-19 ruling on 2026-09-21 and failed it, measured
  live twice (`_audit/2026-09-21-the-all-filters-press.md` section 2):
  neither `aria-expanded` nor `aria-haspopup`, position -1 in both node lists,
  no `aria-label`, so condition 2 refuses it for good; condition 3 refuses it
  independently.
* **N 133: the refusal named a reason the recorded DOM does not show.** The
  address table said applying a filter SUBMITS. The page's only submit belongs
  to a closed feedback dialog (section 4). The press is still refused -- for a
  different reason.
* **M C29: the premise is literally true.** The control was never named,
  measured or captured; nothing has ruled on it either way.

---

## 3. THE SEVEN ALL-FILTERS ROWS: N 84, N 85, N 86, N 87, N 90, N 91, N 92

**WHAT THE CONTROL DOES.** It opens the panel holding the rest of the people
filters: shut, the page draws 83 controls, `show results` (the panel's own
apply) reads 0 and `dialogs` reads 0 (same audit, section 2). A panel-opener,
then -- disclosure-like in effect -- **that declares no disclosure attribute.**

**WHY NO NARROW EXTENSION EXISTS.**

1. **Nothing names it but its label.** Condition 2 matches by attribute, and
   the control carries neither sanctioned attribute nor an `aria-label`. The
   two matchers left are its label text (condition 2 forbids it) and the
   presence of a click listener (`press.py` refuses that by name: it would
   admit nearly every interactive node on the page).
2. **A basis for this surface cannot be narrow.** `press.SENSITIVITY_BASES` is
   keyed by SURFACE, and `disclose` presses `page.locator(shape).nth(index)`
   page-wide. A basis for `/search/results/people/` would therefore license an
   index press on every `[aria-expanded]` / `[aria-haspopup]` node of a page
   whose body is other people's result cards. The only structural argument on
   record bars itself from exactly this surface by its own bound.
3. **Corroborated on a second surface (DERIVED).** On the profile-views
   capture, that page's `All filters` control is likewise a plain
   `button[type=button]` with neither attribute -- the same control family
   declaring nothing on a second page.

**THE ROUTE THAT CAN RESOLVE IS NOT A PRESS.** LinkedIn writes people-search
URLs itself, and the query keys it uses are countable. Every people-search
href in the 25 raw captures and the 24 tracked HTML fixtures, parsed for
parameter NAMES only (values never printed):

    source                          hrefs   parameter names
    25 raw captures, 8 with hrefs      25   activelyHiring 2, activelyHiringForJobTitles 2,
                                            currentCompany 16, geoUrn 4, industry 6,
                                            keywords 21, origin 22, schoolFilter 1
    24 tracked fixtures, 3 with hrefs  25   currentCompany 25, keywords 24, origin 25,
                                            pastCompany 1

    N 84  current company     currentCompany   MEASURED -- 16 hrefs on 5 raw captures
    N 87  past company        pastCompany      one committed job-detail fixture; the
                                               search-admission audit's 4.3a counts it
    N 85  connections of      connectionOf     NAMED -- a shipped test's route set, the
                                               spelling N 172 rests on; never LinkedIn-authored
    N 86  followers of        --               none on record
    N 90  profile language    --               none on record
    N 91  open to volunteering --              none on record
    N 92  service categories  --               none on record

The shipped people pattern admits the LinkedIn-authored spellings
(`_audit/2026-09-20-the-search-admission.md` section 4.3a, pinned by
`test_the_pattern_admits_the_spellings_LINKEDIN_ITSELF_EMITS`). What no reader
can do is COMPOSE one, because every reader takes a page and nothing else --
which is D1, the filing N 94 already carries for its `geoUrn` facet.

**SO THREE ROWS ARE RE-GATED PRESS TO RULING (D1)** in the address table:
N 84 and N 87 on facets LinkedIn itself emits, and N 85 on the `connectionOf`
spelling, whose value is another member's identifier -- D1's needle, under
D3's other-people cause, exactly as N 172 is filed. A gate that points at a
route which can never resolve is a deferral that consumes a future wave; these
three now point at the decision that can move them.

**The other four stay PRESS, marked terminal**, because the press is the only
route on record for them. What would move them: a facet spelling appearing on
record (a LinkedIn-authored href, or the panel's own anchors if it is ever
captured open), and then D1.

---

## 4. N 133 -- FILTER YOUR PROFILE-VIEWER DATA

**THE RECORDED DOM**, read from `_state/cap-profile-views.html` (2026-09-20
10:02, 143,568 characters; the recapture wave measured the same page at
143,554) by a throwaway stdlib parser that printed tags, roles, `aria-*` names
and values, input types, and text LENGTHS or letter-shapes -- never page text
outside a closed vocabulary of control captions, never an href, id or
accessible-name value:

    [aria-expanded] nodes, document order (8; the settled live count is 8-9)
      [0] button            header > nav > ul > li   OUTSIDE <main>   2-char text
      [1] button            header > nav > ul > li   OUTSIDE <main>   12-char aria-label
      [2] button aria-haspopup="dialog"               in <main>        the page's info button
      [3] div[role=button]  the filter bar            in <main>        caption "Past 90 days"
      [4] div[role=button]  the filter bar            in <main>        caption "Interesting viewers"
      [5] div[role=button]  the filter bar            in <main>        caption "Company"
      [6] div[role=button]  main > aside > footer     in <main>        15-char text
      [7] div[role=button]  main > aside > footer     in <main>        17-char text

    each filter pill wraps  div[aria-label="Filter by ..."] > input[type=checkbox][tabindex=-1] + label
    "All filters", "Reset"  plain button[type=button], neither sanctioned attribute
    "Show more analytics"   plain button[type=button], neither sanctioned attribute
    sort                    div[role=tablist] > button[role=tab] x2 (aria-selected, aria-controls);
                            both div[role=tabpanel] are EMPTY (0 descendants)
    forms                   1 -- inside a CLOSED <dialog> (no `open` attribute), holding a
                            fieldset of 2 input[type=radio] with ENUM_STYLE values, a
                            disabled button[type=submit], labels of 32 and 31 characters
    person affordances      4 "Send a message" anchors, 1 invite, 1 follow, 7 /in/ links --
                            none inside either tabpanel
    popover content         none in the document: no listbox, option, menu or menuitem role

**WHAT THE CONTROLS DO.**

* **Opening a filter is ALREADY permitted.** Each pill is a member of the
  `[aria-expanded]` node set, the surface declares a structural basis, and the
  address is admitted, so `press.evaluate` permits the attempt before any
  contact. No extension is needed for that press, and none was made.
* **What a pill opens is built on demand and appears in no capture.** Whether
  applying a filter is an immediate toggle, an option list with an apply
  button, or a form submit is NOT RECORDED ANYWHERE.
* **Applying a filter is a view switch whatever its DOM turns out to be.** It
  changes which viewer rows are displayed. That is not a disclosure:
  `disclose` presses once, dismisses with Escape and requires `aria-expanded`
  to read the same before and after, and Escape does not restore a changed
  selection, so condition 4 has no way to be met; and an option control is not
  a member of either sanctioned set by any evidence on record.
* **The submit the address table named is not the filter's.** The page's only
  `button[type=submit]` sits in the closed feedback-style dialog above, not in
  the filter bar. Refused still; for the reason just given, not that one.
* **The tabs sort; they do not filter.** Most recent / Most relevant are a
  `role=tab` pair whose panels are empty, so switching them re-renders the
  viewer list from the server. A second view switch on the same surface, and
  not this row's capability.

**Is applying provably read-only?** Counted by effect -- the operator's own
test for the messaging pills, *"a view filter is a read"* -- it sends nothing
to anyone. **Provably, no:** its control has never been seen, so nothing about
it can be cited. That is the capture this row needs, and section 7 is the
permission it needs after that.

**Verdict: NEEDS-CAPTURE**, gate stays PRESS, the address table's note and the
census cell revised to say all of the above.

---

## 5. M C29 -- SORT COMMENTS (MOST RELEVANT / MOST RECENT)

* **Its control is in no capture; its STATE is.** No rendered comment-sort
  control appears in any of the 25 raw captures or in any tracked fixture:
  `Most recent` / `Most relevant` occur only as the profile-views viewer tabs.
  But the company-root capture's server-driven payload carries **380
  `commentSortOrder`-prefixed keys** -- five distinct keys, 76 occurrences
  each, every one followed by an opaque value -- beside 190
  `sortOrderFromClient` keys, 4 `sortOrder-value` tokens, and a feed-level
  `FeedSortOrder` enum whose two values are `RELEVANCE` and `REV_CHRON`. So a
  comment-sort state slot rides on post surfaces; what renders it, and what
  pressing it sends, is in no capture. (Entry 6 records how this paragraph
  first read.)
* **The permalink is admitted and unaddressable.** C42 is EXCLUDED-RULED
  because no tool in this server returns a post urn, so the address table's
  permalink (INFERRED) is a page nothing can name. The feed, also driven and
  admitted, is the only host a reader can reach -- and there a post's comments
  stay collapsed until a press whose render is unrecorded. If that render
  draws a comment box, the press opens an editor, which the ruling refuses
  regardless.
* **Choosing an order is a view switch**, for the reason section 4 gives, and
  the census cell's own words agree: *"a pure view filter, the same class the
  messaging pills were admitted under"*. That class is admitted by name, for
  seven pills, on the messaging surface only.
* **The reader's return is bounded.** `FEED-CONTENT-READ-RULING`: counts and
  relations only, never text or names. A sort changes ORDER, so what a reader
  could return is how many comments each order draws and the relations it
  already may. Whether that discharges a row named for sorting is for whoever
  takes the row next to argue, not for this lane to assume.

**Verdict: NEEDS-CAPTURE**, gate stays PRESS. The shut-state half of the
capture is already in flight at zero extra loads: the live readers wave
agreed to count `sort` and `comments` terms, by structure and never by label,
on the `/feed/` load it was taking anyway (its deliverable,
`_audit/2026-09-23-readers-four-rows.md` section 2.2).

---

## 6. WHAT THE RECORDED DOM SHOWED BEYOND THESE NINE ROWS

### 6.1 P O3 AND N 134: THE PRESS ON RECORD MAY HAVE OPENED THE HEADER MENU

The "witness fired, the panel opens" reading P O3 and N 134 rest on
(`_audit/2026-09-21-what-is-reachable-now.md` section 4.3) came from
`scripts/_probe_first_sanctioned_press.py`, which calls `press.disclose(page,
shape="[aria-expanded]", index=0, ...)`. `disclose` presses
`page.locator(shape).nth(index)` PAGE-WIDE. On the only raw capture of that
page, node 0 is a header-navigation dropdown button outside `<main>`, and the
witness moved `menus` -- what a dropdown menu opening looks like. **"Show more
analytics" carries neither sanctioned attribute in that capture**, so it is in
neither node set a caller can name.

**Evidence class: DERIVED** -- a capture one day older than the fire, plus
the probe's source -- not measured on the fire. **Sent to the live readers
wave**, whose lead had reached the same conclusion independently from the
2026-09-05 controls census and is taking the zero-press reading that settles
it (the `[aria-expanded]` node list in document order, landmark ancestry, tag
and role; never a label). **P O3 and N 134 are that wave's rows and are not
edited here.** If the reading holds, two things outside this lane follow:
the address table's PRESS-PERMITTED gate on both rows, and
`census_completion.PRESS_BLOCKED_NAMED`, which lists both as a session and
nothing else. The cleanup wave owns the second; neither is touched here.

### 6.2 TWO OF THE FIVE VIEWER "FILTERS" ARE DIALOG RADIO LABELS

`dom.read_profile_views_insights` falls back, when no `[data-view-name]`
holder exists -- and the live page has none -- to reading every `<label>` in
`<main>`. The page has five: three in the filter pills (12, 19 and 7
characters) and two in the closed dialog's radio fieldset (32 and 31). The
reader publishes all five as `filters`. `innerText` of an element that is not
rendered returns its `textContent`, so a closed dialog hides nothing from it.
Those are LinkedIn's own option texts, not a third party's, so this is a
mislabel and not a leak. It is the finding the recapture audit's section 9.2
read as two new filters; that pair is declared at the head of this document,
with its back-pointer at the claim. `dom.py` is not this lane's file and is
not edited.

### 6.3 D1'S REACH IS WIDER THAN THE FIVE ROWS BUCKET 3 COUNTED

The facet table in section 3 also carries `activelyHiring` (N 82),
`schoolFilter` (N 88), `industry` (N 89) and `geoUrn` (N 83, N 94) -- facets
LinkedIn itself emits, for rows outside this lane. With N 84, N 85 and N 87
re-gated, D1 is the first gate of eight admitted rows in the address table,
and a URL route for three more. Reported for whoever prices D1.

---

## 7. ONE RULING REQUEST: MAY THE PACKAGE PRESS A VIEW SWITCH?

**THE QUESTION.** May a read path press a control that changes which rows are
displayed, or their order -- sending nothing, and restored to its prior
selection afterwards, the restoration verified -- on an admitted surface with
a declared basis?

**THE PRECEDENT IS ALREADY IN THE PACKAGE.** `dom.MESSAGING_FILTERS` and
`dom.activate_messaging_filter`, entered in `readonly.SANCTIONED_MUTATIONS`
on the operator's own argument: *"A filter pill SENDS NOTHING and CHANGES
NOTHING on LinkedIn's servers -- it alters which rows are displayed. Counted by
EFFECT rather than by verb ... a view filter is a read."*

**WHAT IS NEW, and why it is a ruling rather than an edit here:**

1. **The surfaces.** The messaging pills are admitted for one surface.
2. **The closure.** A view switch is closed by selecting the prior state
   again and verifying it (`aria-selected` on the viewer tabs is measured and
   would carry that), never by Escape.
3. **Identification.** The pills match by accessible name inside a closed
   vocabulary; condition 2 forbids that for presses, so a view switch would
   need an attribute shape -- `role=tab` with `aria-selected` is measured on
   the viewer tabs; the pill popovers' option controls are not measured.
4. **The code.** Any click outside `press.disclose` and
   `activate_messaging_filter` needs its own `readonly.SANCTIONED_MUTATIONS`
   entry, which is lane L1's file.

**THE BLAST RADIUS, measured where it can be.** On `/analytics/profile-views/`:
2 tabs (measured), plus the options behind 3 filter pills (unmeasured until a
pill is captured open). On the feed: nothing is recorded. **Rows behind it in
this lane:** N 133 and M C29.

**A ruling of NO is as useful as a YES:** both rows would then leave the queue
as decided rather than sit in it -- the same shape as the pending `/in/me/`
basis question the order excluded.

---

## 8. WHAT THIS LANE DID NOT DO

* **Did not touch a browser**, port 9224, or any browser profile, and spawned
  no child that could.
* **Did not change `press.py`** -- section 1 says why -- **nor build a
  reader.**
* **Did not build an open-moment structural instrument**, although N 133's
  capture wants one (`disclose` exposes only the witness counts at the open
  moment, and those name the container kind, not the controls inside it).
  Building it before section 7 is ruled would be building ahead of the
  decision it serves.
* **Did not edit** `linkedin_server/readonly.py` (L1), `writes.py` (L4), the
  jobs modules (L3), `scripts/census_completion.py`,
  `scripts/check_read_addresses.py`, `scripts/triage_read_gap_rows.py`
  (cleanup), `dom.py`, or the P O3, N 134, M C72, M C85 rows.
* **Did not declare** anything about the what-is-reachable-now reading in
  section 6.1: the live readers wave is measuring it and owns that call.
* **Did not commit a raw capture or quote one.** The only facts that crossed
  from `_state/` are structural: tags, roles, attribute names and values of
  `aria-*` and `type`, counts, lengths, and the captions of controls already
  named in committed fixtures and census cells.

---

## 9. THE INSTRUMENT, REGISTERED AS A METHOD

`_audit/INSTRUMENTS.md` section 59: **which control an index press reaches**,
read offline from a raw capture -- the sanctioned-shape node list in document
order, with landmark ancestry and dialog and form containment, text reduced to
lengths and letter-shapes. Registered as a method, following section 33,
because the scripts that ran it read a gitignored capture and the value is the
reading, not the file. The throwaway scripts themselves are declared
disposable there.

---

## 10. GATES RUN, AND GATES NOT RUN

**RUN, all on this worktree, all offline** (per commit in Entries 7 and 8):

    scripts/check_read_addresses.py          GREEN, 67 of 67 -- after the table edit, and on
                                             each commit
    scripts/census_completion.py --check     exit 0, every headline figure matches its pin
    tests/test_a_correction_is_findable_from_the_claim.py
                                             13 passed; its first run was red on exactly the
                                             two pairs predicted, both triaged
    five citation and register guards        79 passed
    the three generators, twice per commit   INDEX, RULINGS and the blocker map at a fixpoint --
                                             the second sweep changed nothing. The blocker map's
                                             first sweep moved 7 rows' rank-1 locator document to
                                             this audit (M C23, M C29, M C90, N 133, N 134, N 136,
                                             P O3) and 74 rows' candidate denominators, and no
                                             other column
    the pre-commit identity gate             0 hits on every commit
    scripts/impact_gate.py --against b0d3ab8 PASS over 48 files (2157 tests); NOT CHECKED 167 of
                                             215 test files, said by the gate itself
    one cold verification pass               briefed on 9facb53; outcome in Entry 9

**NOT RUN, and why:**

* **The full suite.** The scoped gate chose what this change can break and
  says what it did not run; CI runs the whole suite on three platforms on
  push, and this lane does not push.
* **Any new press test.** `press.py` is unchanged, so the order's "one
  negative control per extension" has no extension to attach to.
* **Anything live.** No reading here came from a browser.

---

## Log

(appended as rows land)

### Entry 1 -- denominator confirmed

Derived by a throwaway script reading the tsv's `class` and `gate` columns
(12 ADMITTED/PRESS, minus the 3 excluded = 9). It matches the order.

### Entry 2 -- the order's premise checked against disk, and the recorded DOM read

**THE ORDER SAYS "NOBODY RULED THESE PRESSES UNSAFE; THE GATE REFUSES THEM BY
DEFAULT." ON DISK THAT IS TRUE OF ONE ROW OF THE NINE.**

* **N 84-N 92 (seven rows).** The `All filters` control was put through the
  2026-09-19 ruling on 2026-09-21 and FAILED IT, measured live twice
  (`_audit/2026-09-21-the-all-filters-press.md` section 2): it carries neither
  `aria-expanded` nor `aria-haspopup` (position -1 in both node lists) and no
  `aria-label`, so condition 2 refuses it TERMINALLY; condition 3 refuses it
  independently (no basis for `/search/results/people/`, and the only
  structural argument on record is barred from a surface made of other people
  by its own bound). That is a measured refusal on a ruling's terms, not a
  default.
* **N 133.** The bucket-3 note says "Applying a filter SUBMITS, and the
  disclosing-press ruling refuses submission by name." The ruling does refuse
  submission by name (`_audit/2026-09-19-the-disclosing-press-ruling.md`,
  REFUSED regardless). Whether applying a viewer filter IS a submission is
  examined below, and the recorded DOM does not support the claim.
* **M C29.** Never named, never measured, never captured. This is the one row
  where "the gate refuses by default" is literally the situation.

**THE RECORDED DOM FOR N 133** is the table now in section 4, read from the
main checkout's gitignored raw capture `_state/cap-profile-views.html` by a
throwaway stdlib parser that printed tags, roles, `aria-*` names and values,
input types and text LENGTHS or letter-shapes. Nothing from it enters a
tracked file except structural facts.

**THREE THINGS FOLLOW, AND ONLY THE FIRST IS ABOUT MY ROW.**

1. **N 133's "applying a filter SUBMITS" rests on a submit that belongs to a
   different control.** The page's only `button[type=submit]` sits in a closed
   feedback-style `<dialog>` form, not in the filter bar. The filter pills are
   `[aria-expanded]` popover triggers whose popovers are built on demand -- no
   popover content is in the document -- so what applying a filter entails
   is NOT RECORDED ANYWHERE. The row's reason is revised, not its gate:
   whatever the popover holds, APPLYING a filter changes which rows are
   displayed, which is a view switch and not a disclosure, and no press the
   shipped gate sanctions reaches it.
2. **The two "filters this repository has never documented"** (the recapture
   audit's section 9.2, label lengths 32 and 31) **are the two radio labels
   inside that closed dialog.** Section 6.2 has the mechanism.
3. **CROSS-LANE, AND IT IS THE MOST CONSEQUENTIAL THING I HAVE FOUND.** The
   P O3 / N 134 press on record may have opened the header navigation menu.
   Section 6.1 has the evidence and its class (DERIVED).

### Entry 3 -- notified, answered, and the facet vocabulary counted

* **readers-lead** was sent 6.1 and 6.2 with the evidence. It replied that its
  own derivation (its F2, from the 2026-09-05 controls census) agrees, and that
  it is taking the zero-press node-order reading on the live page inside its
  wave. It asked whether L2 drives the 9224 browser: **no, not at all** -- this
  lane is offline by construction. It then agreed to add comment-sort terms to
  its `/feed/` load at zero extra loads, which is M C29's shut-state capture.
* **The orchestrator** was sent 6.1 and a status line.
* **The facet vocabulary** in section 3 was counted by a throwaway script over
  every people-search href in the 25 raw captures and 24 tracked fixtures,
  printing parameter names and counts only. It is what re-gated N 84, N 85 and
  N 87.
* **M C29's host.** C42 (EXCLUDED-RULED: no tool returns a post urn) makes the
  permalink unaddressable; recorded in section 5.

### Entry 4 -- the table, the census and the markers edited

* `_audit/_census/read-addresses.tsv`: the nine rows' `note` rewritten, and
  `gate` PRESS to RULING on N 84, N 85, N 87, by a script that refuses to
  write if any other field of any line would change. `check_read_addresses.py`
  GREEN, 67 of 67, straight after.
* `_audit/_census/network.md` rows 84, 85, 86, 87, 90, 91, 92, 133 and
  `_audit/_census/messaging-and-content.md` row C29: one dated LANE L2
  paragraph appended to the evidence cell, by a script that refuses to write
  if any cell but the last would change. **Every state cell reads GAP before
  and after.**
* `_audit/INSTRUMENTS.md` section 59 appended, and the back-pointer written
  at the recapture audit's section 9.2 claim.

### Entry 5 -- a ruling file arrived, and its action set was empty

A `_TEAM_LEAD_PRESS_PY.md` appeared at this worktree's root (file time 17:49,
read at 18:21 by the box clock). It reported the live readers wave editing
`press.py` in its own worktree -- new structures named `_READING_REQUIRED`
and `_SCOPE_REQUIRED`, possibly a changed entry schema -- and told any lane
with `press.py` work ahead of it to keep that work additive, entries only.
**Verified before obeying:** master is still `b0d3ab8` (0 commits since), so
the live wave's version is not on master. **This lane has no `press.py`
change at all**, by the decision in section 1, so there is nothing to keep
additive and nothing for the orchestrator to reconcile at merge. Acknowledged
by deleting the file; it was never staged.

### Entry 6 -- a number of mine that did not hold, found by re-auditing it

Committed in `9facb53`, section 5 read: *"The company root's 582 `sortOrder`
hits are `sortOrderFromClient` server-driven state keys."* **Both halves were
unsound, and the verdict did not rest on either.**

* **582 was a case-insensitive count** reported as the case-sensitive token.
  Case-sensitive, `sortOrder` occurs 194 times: 190 `sortOrderFromClient` and
  4 `sortOrder-value`.
* **The classification was drawn from the first eight lines of a sorted
  listing.** Counted whole, the 582 case-insensitive hits are 190
  `sortOrderFromClient`, 380 `commentSortOrder`-prefixed keys, 4
  `sortOrder-value` and 8 `feedSortOrder` / `FeedSortOrder_*` tokens -- and
  the 380 are the interesting ones: comment-sort STATE on a post surface.

**WHAT MOVED:** section 5's paragraph, the M C29 line of section 1, the M C29
note in the address table, and one clause of the census C29 cell -- each now
says "no rendered control" and names the state keys. **WHAT DID NOT:** the
verdict. NEEDS-CAPTURE rests on no capture showing the CONTROL, which remains
true; the state keys make a comment sort more certainly real, not more
reachable. The cold verifier was briefed on `9facb53` and will read the
unsound sentence; that is the point of pinning it there.

### Entry 7 -- the gates on `9facb53`

    scripts/check_read_addresses.py          GREEN, 67 of 67
    scripts/census_completion.py --check     exit 0, every headline figure matches its pin
    five citation and register guards        79 passed: test_an_asserted_name_resolves,
                                             test_the_register_numbers_are_unique,
                                             test_a_cited_sha_resolves,
                                             test_a_census_locator_names_its_row,
                                             test_read_addresses
    scripts/impact_gate.py --against b0d3ab8 PASS over 48 files (2157 tests), and by its own
                                             statement NOT CHECKED 167 of 215 test files;
                                             395.2 s wall clock

---

## Live queue

**No row of this lane is ready to fire.** Nothing below is a reader. Each line
is a CAPTURE that a NEEDS-CAPTURE row waits on, in the order's own fields --
row, tool, page address, expected loads, press -- with the condition that
makes the load worth taking.

    M C29 | the live readers wave's structural probe, ALREADY IN FLIGHT (its
          |   deliverable 2026-09-23-readers-four-rows, section 2.2)
          | /feed/
          | 0 extra loads -- it rides the load that wave is taking anyway
          | none: a shut-state reading of [aria-expanded] / [aria-haspopup]
          |   membership with the terms sort and comments, never a label

    N 133 | press.disclose with its shipped witness -- ONLY AFTER section 7 is
          |   ruled YES; before that, the load buys nothing a ruling needs
          | /analytics/profile-views/
          | 1 load
          | one [aria-expanded] press on the Company pill, which the shipped
          |   gate ALREADY PERMITS, at the index the zero-press node-order
          |   reading gives (never index 0); the witness names the popover's
          |   container kind, and the controls inside it need an open-moment
          |   reading no shipped instrument takes
