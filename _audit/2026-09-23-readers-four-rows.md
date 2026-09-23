claude-opus-5-5[1m]

# READERS FOR THE FOUR ROWS BLOCKED ON NOTHING: P O3, N 134, M C72, M C85

**2026-09-23. Wave `readers-four-rows`, base `b0d3ab8`. WRITTEN AS THE WAVE
RUNS, not at its end.** The four rows `_audit/2026-09-23-bucket3-addresses.md`
measured as ADMITTED with nothing but a reader between the page and the row
(its section 8), less `M M49`, which is excluded by the standing ruling
`DO-NOT-OPEN-MESSAGING` and is not touched here.

Live rules this wave runs under: the attached Chrome on `127.0.0.1:9224` only,
its own tab only; read-only, `writes_enabled` false; no press but one the
shipped press gate permits; never `/messaging/`, never `/notifications/`; page
loads serial and paced, budget 15 for the whole wave; stop at the first login
page, checkpoint, captcha or challenge; raw captures only under this
worktree's gitignored `_state/`.

---

## 0. THE PLAN, WRITTEN BEFORE ANY BUILD OR FIRE

### 0.1 The four rows, as their cells stand at `b0d3ab8`

| row | page | the cell's stated blocker | gate (bucket 3) |
|---|---|---|---|
| `P O3` | `/analytics/profile-views/` | one unbuilt artifact: a NAME-FREE content shaper for the disclosed panel | PRESS-PERMITTED |
| `N 134` | `/analytics/profile-views/` | the same artifact, same surface | PRESS-PERMITTED |
| `M C72` | `/feed/` | a caller wiring `read_reaction_surface` (`off_state`) as the counter, then a fire | PRESS-PERMITTED |
| `M C85` | `/feed/update/urn:li:activity:<id>/` | a reader for the READ half (poll results as counts) | READER |

### 0.2 What reading the shipped code found BEFORE anything was built

These four findings change the plan, so they are recorded before it.

**F1. THE PRESS GATE HAS NO MOMENT AT WHICH A READER COULD READ.**
`press.disclose` clicks, takes its closed witness count, reads the control's
own `aria-expanded`, and presses Escape -- in that order, with nothing between
the witness and the dismissal. The witness is deliberately a CLOSED SET and
"never a caller's callable" (`press.WITNESS_SELECTORS`, and
`_audit/2026-09-19-the-first-sanctioned-press.md` section 6: *"A seam that
accepts arbitrary code at the open moment is a press seam wearing an
observer's clothes"*). So "a name-free shaper" is not the whole unbuilt
artifact for `P O3` / `N 134` / `M C72`: **no package code can read disclosed
content through the gate as it ships.** The read has to be added to the gate,
and by the gate's own rule it has to be a closed table, not a callable.

**F2. `disclose` AIMS BY PAGE-WIDE INDEX, AND THE CONTROL PRESSED ON
2026-09-21 WAS NEVER IDENTIFIED.** `disclose` presses
`page.locator(shape).nth(index)` over the WHOLE page. The 2026-09-21 witness
(`scripts/_probe_first_sanctioned_press.py`, `index=0`) reported
`disclosed: true, moved: ["expanded_true", "menus"]`, and both census cells
now read *"the panel opens"*. **Nothing in that run records WHICH of the
page's nine `[aria-expanded]` controls index 0 is.** Document order puts the
page chrome ahead of `main`, and the page's own chrome is measured to carry
disclosure controls: the 2026-09-05 controls census of this very page
(`_audit/_scratch/_live-analytics-controls*.txt`, gitignored, main checkout)
shows presses on it surfacing the global nav's business menu (the names that
appeared were the nav's product links, `menus +1`), and on the sibling
search-appearances page the account menu. Its control list also names a
skip-link JUMP MENU (`Close jump menu`, four `Skip to ...` links). **So "the
panel opens" is not established: SOMETHING at page-wide index 0 opened a
menu, and which control that was is unrecorded.** This is recorded as an
attribution gap, not as a refutation -- it is measured below, with no press.

**F3. THE EXISTING NAME-FREE READER IS NOT NAME-FREE AT THE OPEN MOMENT OF A
FILTER.** `dom.read_profile_views_insights` (the single already-declared
script this surface spends) publishes up to ten `<label>` texts as
`filters`, by design: on the unpressed page those are the three filter
captions (`Past 90 days`, `Interesting viewers`, `Company`, per the constant
block above `PROFILE_VIEWS_INSIGHTS_JS`). **With the Company filter's
dropdown OPEN, the `<label>` elements in the document would include its
options -- the employers of the people who viewed him.** Running that reader
at the open moment of that dropdown would publish third-party employers.
So reusing it at the open moment is only safe for a disclosure whose content
is measured to carry no labels of that kind, and the reading published must
be restricted to its count fields.

**F4. "INTERESTING VIEWERS" IS A FILTER, NOT A PANEL.** The constant block
above `PROFILE_VIEWS_INSIGHTS_JS` records three
`data-view-name="search-filter-top-bar-select"` holders, each wrapping a
`<label>`: `Past 90 days`, `Interesting viewers`, `Company`. The 2026-09-05
census names a `Submit` and a `Reset` beside them, and a form. So `N 134`
(*See notable or interesting viewers*) is, on the evidence in the tree, a
FILTER'S effect on the viewer list -- and APPLYING a filter is the act `N 133`
is refused for (the ruling refuses submission by name). Whether OPENING that
control discloses anything row-worthy, before any option is chosen, is
exactly what is unmeasured.

### 0.3 Consequences for the plan

1. **Measure before building, pressing nothing.** One load of
   `/analytics/profile-views/` and one of `/feed/`, each enumerating every
   `[aria-expanded]` and every `[aria-haspopup]` node IN THE SAME ORDER
   `page.locator(shape)` resolves them, with: landmark, form membership,
   LinkedIn's own component names (`data-view-name`) on and around it, safe
   class tokens, whether its `aria-controls` region exists and is hidden and
   what COUNTS it holds, and its accessible name reduced IN THE PAGE to a
   term from a closed vocabulary written in the probe (never the name).
   This is the step that says which index is which, and it settles F2.
2. **Build the open-moment read into the gate as a CLOSED TABLE**, keyed like
   `SANCTIONED_SHAPES` and `SENSITIVITY_BASES`: a caller names a reading, it
   cannot supply one. Plus, if F2 shows it is needed, a closed table of
   narrowing SCOPES so a package caller can aim without reading a label.
   Shown failing before it is relied on.
3. **Fire each reader once**, only if the measurement shows a control whose
   disclosure is (a) the row's payload and (b) shapeable name-free.
4. **`M C85` stops at the address** unless a sanctioned source for a poll
   post's address exists (section 4 below records the search).

### 0.4 Page-load budget, allotted before any load

    step 0 + structure      2   /analytics/profile-views/, /feed/ -- no press
    fires                   <= 3   one per reader; P O3 and N 134 share one if the
                                   measurement puts them on one control
    reserve                 10   not to be spent without a written reason here

### 0.5 FORCED PREDICTION, logged before the first load

**1 of 4 moves to COVERED-PROVEN, and it is not `N 134`.** `M C85` stops at
the address. `N 134` stays GAP because its payload is a filter's effect (F4),
which a disclosure cannot deliver. One of `P O3` / `M C72` proves; the other
is stopped by what the structural load shows about targeting (F2) or content
(F3).
