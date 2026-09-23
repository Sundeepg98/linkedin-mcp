claude-opus-5-5[1m]

# READERS FOR THE FOUR ROWS BLOCKED ON NOTHING: P O3, N 134, M C72, M C85

**CORRECTS:** `_audit/2026-09-23-bucket3-addresses.md` -- its "blocked on nothing" five are one: `M C85` is gated RULING (no sanctioned source for a poll post's address, section 4), and `P O3`, `N 134` and `M C72` are gated PRESS, each measured live (sections 3.0.1 and 5.1). Only `M M49` remains.

**CORRECTS:** `_audit/2026-09-21-what-is-reachable-now.md` -- section 4.3's "THE WITNESS FIRED. THE PANEL OPENS." rests on a press at page-wide `[aria-expanded]` index 0, measured here to be the header nav's account menu (section 2.2).

**CORRECTS:** `_audit/_census/profile.md` -- row `O3` carried that witness as "the panel opens" and one name-free shaper as its whole blocker; it is blocked by "Show more analytics" carrying no sanctioned attribute and by filter application being a submission (section 3.0.1).

**CORRECTS:** `_audit/_census/network.md` -- row `134` likewise; the pill it names opens into a filter form whose payload needs APPLYING (section 3.0.1).

**EIGHT OF THE SHAS IN THIS DOCUMENT ARE BRANCH-ONLY TODAY.** `652cd2f`,
`aba78f7`, `2bc3720`, `d912b25`, `1df9061`, `7ad55ed`, `1c55694`, `9b4dd6b` are
this wave's commits on its worktree branch and do not resolve on `master`
until that branch merges.
Their subjects, which survive a rewrite: `652cd2f` *"press: read what a press
disclosed, through two more closed tables"*; `aba78f7` *"who_viewed_me: open
the filter pills through the gate; filters skip a dialog"*; `2bc3720`
*"server: the pill opener's names no longer spread taint through the
module"*; `d912b25` *"record the zero-press load; aim the feed fire by
position with two refusing interlocks"*; `1df9061` *"record the fires: P O3,
N 134 and M C72 are gated PRESS, each measured live"*; `7ad55ed`
*"readers-four-rows: name the verdict basis, the probe table and the
branch-only SHAs"*; `1c55694` *"readers-four-rows: read the requests against
the new rulings; forecast the merge"*; `9b4dd6b` *"tests: press is wired, so
its orphan ruling is spent; three readers get verdicts"*.

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

### 0.5 THE ORCHESTRATOR'S NOTE ON THE 2026-09-21 WITNESS -- RECEIVED, AND HOW EACH POINT IS ANSWERED

A note from the orchestrator (a `_TEAM_LEAD_*.md` ruling at this worktree's
root, written ~18:02, acknowledged by deleting it once recorded here) relayed
L2's DERIVED finding -- that the 2026-09-21 press may have landed on a
header-nav button -- and set three conditions. Each, and where it is met:

1. **"Before any press, take a ZERO-PRESS reading of the `[aria-expanded]`
   node list on /analytics/profile-views/: order, text, and whether each node
   is inside <main>."** Section 2.1 (DERIVED, from a capture) and section 2.2
   (LIVE, one load, nothing pressed). *Text* is recorded as a TERM from a
   closed vocabulary plus shape facts (length band, token count), never
   verbatim: `tests/test_page_text_is_never_printed.py` binds every probe,
   and on this page a control's name can be a stranger's ("Send a message to
   <a person>").
2. **"Claim the row only if the node you press is the analytics control
   inside <main>, and the reading after the press shows the analytics
   content, not a nav menu."** The reader presses only through
   `press.disclose(scope="main")` -- the gate itself looks for the control
   inside `main`, not index arithmetic by the caller -- and each row is judged
   on the reading's `appeared` terms, which a nav menu cannot produce: the
   phrases are time ranges, viewer categories and the menu's own controls.
3. **"If the press cannot be scoped to <main> under the current gate, do not
   claim the row."** It can, as of `652cd2f` (`press.PRESS_SCOPES`, key
   `main`), shown failing when the scope is ignored (section 1, defect E).
   **The note's own last clause applies: the scope and the reading were
   already built for exactly this, and say so here.**

### 0.6 FORCED PREDICTION, logged before the first load

**1 of 4 moves to COVERED-PROVEN, and it is not `N 134`.** `M C85` stops at
the address. `N 134` stays GAP because its payload is a filter's effect (F4),
which a disclosure cannot deliver. One of `P O3` / `M C72` proves; the other
is stopped by what the structural load shows about targeting (F2) or content
(F3).

---

## 1. THE GATE, EXTENDED OFFLINE -- `652cd2f`

*"press: read what a press disclosed, through two more closed tables"*

**`press.OPEN_READINGS`** -- a caller NAMES a reading and cannot supply one,
exactly as it names a shape. An entry fixes the surfaces (EXACT paths, not a
prefix) and the phrases; the page answers through `dom.read_count_lines`, a
script already declared and waived, with phrase positions and integers. **So
the reading costs ZERO new `# readonly-ok` waivers** -- the budget stays at 22
of 22 -- and no page string crosses the boundary. It is taken immediately
before the click and again at the open moment, before the Escape; `appeared`
credits the press only with terms that were not on the page before it.
It rides alongside the verdict like the witness and never decides it.

**`press.PRESS_SCOPES`** -- narrows the candidates to `<scope> <shape>` before
the index applies, so a package caller can aim at a control inside a
structural container instead of at a page-wide position the chrome controls.
One entry so far, `main`.

**Three new refusals, all before any contact**: `reading_not_sanctioned`,
`reading_not_for_this_surface`, `scope_not_sanctioned`. Classified in
`tests/test_press.py`'s exhaustive `WHEN_KNOWABLE` and driven through its
`_REACHES` harness (taught to pass the two keys). With both keys `None` the
gate is byte-for-byte what it was, and a test asserts that.

**SHOWN FAILING**, seven planted defects in `press.py`, each run against
`tests/test_press.py` + `tests/test_press_open_reading.py`, each restored by
sha256 (`fed03ec4a42819cb`) before the next:

    BASELINE                                                  94 passed
    A  the open reading taken AFTER the Escape                6 failed
    B  an unknown reading key accepted                        2 failed (one is the
                                                              inventory's own row)
    C  the reading decides the verdict                        2 failed
    D  an out-of-range phrase position clamped onto phrase 0  1 failed
    E  the scope ignored                                      2 failed
    F  a reading's surface matched by prefix                  1 failed
    G  a value carried on a refused numeral shape             1 failed
    RESTORED                                                  94 passed

Also run on the change: `tests/test_the_press_gate_cannot_witness_disclosure.py`
and `tests/test_the_presser_control_is_a_pair.py` (116 passed with the two
above), and `tests/test_readonly.py` (290 passed -- the scanner reads
`press.py` and the waiver budget).

---

## 2. THE STRUCTURE OF THE TWO PAGES, BEFORE ANY PRESS

### 2.1 `/analytics/profile-views/`, DERIVED from a capture at zero page loads

Source: the gitignored raw capture `_state/cap-profile-views-captions.html` in
the main checkout (2026-09-20 16:03), read by a scratch parser (declared
disposable) that prints tags, roles, attribute presence, landmark ancestry and
label LENGTHS, never a label or text. Phrase identity was tested locally by
normalised equality against phrases the parser supplied, and only the phrase
index is printed. Reached independently of the sibling lane L2, whose
structure-only reading of the 10:02 capture (its
`_audit/2026-09-23-lane-l2-refused-presses.md`, Entry 2 item 3, in its own
worktree) says the same thing.

    [aria-expanded], document order -- 8 nodes in this capture
    idx  tag     role    landmark ancestry        what it is (by structure)
      0  button  -       nav < header             a 2-character name
      1  button  -       nav < header             a 12-character aria-label
      2  button  -       main                     aria-haspopup=dialog, 48-char label
      3  div     button  main                     a filter pill; wraps <label> (12 chars)
      4  div     button  main                     a filter pill; wraps <label> (19 chars)
      5  div     button  main                     a filter pill; wraps <label> (7 chars)
      6  div     button  footer < aside < main    a right-rail footer dropdown
      7  div     button  footer < aside < main    the same

    phrase matched locally -> innermost element, and its nearest control
      "show more analytics"   span < span < button   the button carries NEITHER
                                                     aria-expanded NOR aria-haspopup
      "all filters"           span < span < button   the same
      "past 90 days"          label < div < div[role=button]{aria-expanded}  = node 3
      "interesting viewers"   label < div < div[role=button]{aria-expanded}  = node 4
      "company"               label < div < div[role=button]{aria-expanded}  = node 5

    data-view-name attributes anywhere in the capture: 0

**THREE CONSEQUENCES, all DERIVED from one capture until the live load below
confirms them:**

1. **The 2026-09-21 press, `index=0` page-wide, pressed a NAV BUTTON.** Node
   0 is in the header's nav with a two-character name -- the account menu's
   shape -- and nothing of his analytics precedes it. Its witness
   (`moved: ["expanded_true", "menus"]`) is what a nav dropdown opening looks
   like. **So "the panel opens" is not evidence about any analytics panel.**
2. **"Show more analytics" cannot be pressed by this gate at all.** It carries
   neither sanctioned attribute, so condition 2 refuses it TERMINALLY -- the
   position the All-filters control on the people search is in. If the
   Premium insights live behind it, they are NEVER reachable by this route; a
   third shape is a ruling request with a measured blast radius
   (`press.py` docstring), not an edit.
3. **The filter pills ARE reachable, but only through a scope.** Inside `main`
   the `[aria-expanded]` order is: the info button, the three pills, then the
   two footer dropdowns -- so a main-scoped index is not a filter-bar index,
   and a page-wide one lands in the nav.

### 2.2 BOTH PAGES LIVE, NOTHING PRESSED -- see the entry below, written when the load ran

The instrument is `scripts/_probe_disclosure_targets.py`, written by an
implementer child to a closed spec and reviewed here before it ran: one load
per page, no click, keyboard, fill, scroll or hover; every `[aria-expanded]`
and `[aria-haspopup]` node in the order `page.locator(shape)` resolves them,
with landmark ancestry, `visible`, component names and safe class tokens
confined by shape, the feed-item ordinal by `[data-urn]`/`[data-id]` AND by
`article`/`[role=article]`, and the accessible name reduced IN THE PAGE to a
term from a closed vocabulary or to shape facts. A detector control on a local
headless Chromium gates the live load. Its offline test: 14, including the
closed alphabet over synthetic names; shown failing under three planted
defects by the child (its report, `_state/readers4/probe-slice-report.md`)
and four more by me, on the additions it did not cycle, each restored by
sha256 (`615199cf4d7ebf10`):

    BASELINE                                             14 passed
    P1  role and type crossing the boundary raw          3 failed
    P2  visible always true                              1 failed
    P3  article detected by tag only, not by role        1 failed
    P4  the comments term missing                        1 failed
    RESTORED                                             14 passed

**THE LOAD -- 18:56-18:58 IST, attach on 127.0.0.1:9224, 2 page loads,
NOTHING PRESSED.** Detector control PASS (8 of 8). Both pages: `walled`
False, challenge terms 0. Structured record in the worktree's gitignored
`_state/readers4/disclosure-targets.json`.

`/analytics/profile-views/` -- 8 `[aria-expanded]` nodes to the page's own
query, stable across two readings 4 s apart:

    idx  tag     role    landmark       term                 visible
      0  button  -       nav            nav_me               True
      1  button  -       nav            nav_for_business     True
      2  button  -       main           (unmatched, 7 words) True   haspopup=dialog
      3  div     button  main           time_range           True
      4  div     button  main           interesting_viewers  True
      5  div     button  main           company_filter       True
      6  div     button  footer<main    (unmatched)          True
      7  div     button  footer<main    (unmatched)          True
    [aria-haspopup]: 1 node, idx 2 above.  No node classifies as
    show_more_analytics or all_filters.  items 0, articles 0.

**So the 2026-09-21 press at page-wide index 0 MEASURABLY landed on page
chrome** -- the nav account menu, or the shadow-root node below; either way
not an analytics control. *"The panel opens"* in the census cells of `P O3`
and `N 134`, and in `_audit/2026-09-21-what-is-reachable-now.md` section 4.3,
is not evidence about any analytics panel. The three pills are live exactly
where the capture put them.

**AND PLAYWRIGHT COUNTS ONE MORE THAN THE PAGE: 9 against 8** (`order_basis_ok`
False). Playwright's CSS engine pierces open shadow roots and
`querySelectorAll` does not, so one `[aria-expanded]` node sits in a shadow
root -- which is also why the 2026-09-19/21 runs measured `shape_total` 9.
**A page-wide Playwright index therefore does not map onto the page's own
order**, and nothing recorded says where the ninth node sits. The analytics
reader is unaffected: it enumerates AND presses through the same scoped
Playwright locator.

`/feed/` -- 47 `[aria-expanded]` to the page (48 to Playwright, the same
one-node gap) and 19 `[aria-haspopup]`:

    idx 0-1  nav_me, nav_for_business (nav)
    idx 2    sort          div role=button, main  -- the FEED-level sort
    idx 3    (no name)     a, main
    idx 4    post_control_menu  button, main, visible  -- the first post's menu
    then per post: reactions_menu, repost, an unlabelled anchor,
                   post_control_menu -- 7 control menus drawn in all
    video player menu buttons (vjs-*): 10 in [aria-expanded], all INVISIBLE
    [aria-haspopup]: 19 -- unlabelled anchors (haspopup=dialog) and the
                   invisible player buttons; the control menu is NOT one
    items 0, articles 0

**THE FEED DRAWS NO PER-POST CONTAINER A SCOPE COULD NAME** -- no
`data-urn`, no `data-id`, no `article` -- and the control-menu trigger shares
its only class token with the `repost` button, which carries `[aria-expanded]`
too. **So nothing structural lets the package aim at ONE post's control menu:**
it can only be told from its neighbours by its accessible name, which
condition 2 forbids, or by a position in `main`. That is a measured blocker
for `M C72` in its own right (section 5).

**For the sibling lane L2 (`M C29`, sort a post's comments):** one node
classifies as `sort` and it precedes the first post, so it is the feed-level
sort; no node classifies as `comments`, and no comment-sort control is drawn
among the disclosure-shaped nodes on first render. Sent to L2.

**A TWO-WRITER COLLISION ON THIS FILE, AND IT WAS MY SEQUENCING.** The child
reported at 18:42 and had not ended its turn. I then ran my own
planted-defect cycle over the probe while it was still re-running its tests;
it read the red from my P4 plant (the `comments` term removed) as a real gap
and, AFTER my byte-for-byte restore, added its own `comments` entry -- so the
file briefly carried the key twice (same value, so every test stayed green,
which is why only `git status` showing the staged file modified again caught
it). Nothing was committed from that state. The rule this cost: **a lead does
not plant defects in a file a child can still read, until the child's turn
has measurably ended** -- its transcript quiet, not its report written.

**AND THE REGISTER ALREADY SAID IT, MORE STRICTLY.** `_audit/INSTRUMENTS.md`,
under "How a red-proof is run here": never in the live tree; copy
`linkedin_server`, `tests`, `scripts` and `pytest.ini` to a scratch
directory and plant there. All 23 of this wave's plants (sections 1, 2.2 and
3, the child's three included) were made in this worktree's own files and
restored by sha256. The collision above is what that rule exists to prevent,
arriving on schedule. Each cycle ended on the RESTORED run printed with it,
and section 10.4 records the full-suite gate over the committed files.


**AND A DEFECT IN THE SHIPPED INSIGHTS READER, on `P O3`'s own surface.** The
section 2.1 capture carries five `<label>` elements: three inside the pills,
TWO in a form inside a closed dialog in the right rail, both under the
reader's 40-character cap. The page has no `data-view-name` at all, so
`PROFILE_VIEWS_INSIGHTS_JS` takes its `<label>` fallback and publishes all
five as `insights.filters` -- two of them a feedback form's options. Measured
by my own structure-only census of the capture; L2 reported the same from the
10:02 capture. The two "undocumented filters" in section 9.2 of
`_audit/2026-09-20-the-profile-views-recapture.md` are those dialog labels,
and the document-level record of that is L2's, not this wave's: its markers
sit at both ends, written on its own branch and on `master` since the lane L2
merge `62a8f0f` (both read there by 20:23); this wave adds no second
back-pointer. This wave fixes the CODE (section 3), and the live fire read 3
(section 3.0.1).

---

## 3. THE ANALYTICS READER, BUILT OFFLINE

**`linkedin_who_viewed_me(open_filter_menus=True)`** -- an opt-in on the tool
that already loads the page, so it costs no page load of its own, and the
first package caller of `press.disclose`. Default `False` is the tool
byte-for-byte as it was (asserted at tool level).

* **Which controls:** the `[aria-expanded]` controls inside `main` that are
  `role="button"`, visible, and wrap a `<label>` -- the pills, by STRUCTURE,
  re-enumerated before every press. Never a label's text, never a page-wide
  index (page-wide, index 0 is the nav).
* **How:** `press.disclose(shape="[aria-expanded]", scope="main",
  reading="profile_views_filter_menu", read_counters=...)` per pill, at most
  three, stopping at the first press the gate does not permit.
* **Priced by:** the page's own HEADLINE viewer count -- the number that would
  move if a press APPLIED a filter, which is the weak write the surface's
  structural argument concedes -- plus each nav badge that reads at the first
  read. Both badges were measured unreadable today by the bucket-1 preflight,
  and `check_counters` refuses on any unreadable counter AFTER the click, so
  the caller checks its counters first and presses NOTHING if they do not
  read (`counters_unreadable_before_any_press`).
* **Published per pill:** the gate's verdict fields, the witness, the reading's
  `appeared` / `held` terms from `press.OPEN_READINGS`, any value drawn beside
  an appeared term, and `new_lines`. The package's own words and integers.

**`dom.PROFILE_VIEWS_INSIGHTS_JS`**: the `<label>` fallback now skips a label
inside `dialog` / `[role="dialog"]` -- by where it sits, never by what it
says. Same script, same call site, no waiver moved.

**A GATE WEAKNESS FOUND WHILE WRITING THE CALLER, recorded and NOT repaired
here:** `press.disclose` reads its BEFORE counters and then clicks, even when
that reading has already doomed the press (`no_counter_reading`,
`counter_unreadable`, a sensitive counter missing). All three are knowable
before the click -- the same class the 2026-09-21 repair moved for the
url-derivable refusals. A caller can guard it (this one does); the gate
should refuse them before the click itself. That is a change to the
exhaustive refusal inventory's classifications and belongs to its own commit.

Tests, all offline: `tests/test_who_viewed_me_filter_menus.py` (10: structure
not labels, scope `main`, an invisible control is never a pill, the cap, stop
at the first refusal, no press on unreadable counters, the published
alphabet, the counter set fixed at the first read, and the two tool-level
cases), `tests/test_profile_views_filters_skip_dialogs.py` (3, the real script
in a local headless Chromium, with a control that the same labels OUTSIDE a
dialog are still read), and `tests/test_press_open_reading.py` gains the
vocabulary-miss case (`new_lines`).

**SHOWN FAILING**, nine planted defects, each restored by sha256 before the
next (`server.py` `2afa3f4294b603f4`, `dom.py` `4cdeb6ee06343ef4`):

    BASELINE                                                   13 passed
    S1  the press not scoped to main                           1 failed
    S2  a control without a label counted as a pill            1 failed
    S3  an invisible control counted as a pill                 1 failed
    S4  no stop after a refused press                          1 failed
    S5  no counter check before the first press                1 failed
    S6  the counter set re-chosen at every read                1 failed
    S7  the summary copying the reading's per-moment detail    1 failed
    S8  the tool opening the pills by default                  1 failed
    D1  labels inside a dialog read as filters                 2 failed
    RESTORED                                                   13 passed

(The first attempt planted NOTHING and said so -- all nine anchors missed
because `server.py` and `dom.py` are CRLF in the working tree and the anchors
were written with LF. The script reports an anchor found zero times as NOT
PLANTED rather than as a pass, which is why that was visible.)

### 3.0 THE VERDICT RULES FOR `P O3` AND `N 134`, REGISTERED BEFORE THE FIRE

* **`N 134` (see notable or interesting viewers) is PROVEN only if** the pill
  the structural load classified `interesting_viewers` opens under a PERMITTED
  press with its closure verified, and the reading shows viewer CATEGORIES
  (`recruiters`, `hiring_managers`, `your_network`, `your_company`,
  `senior_leaders`, `decision_makers`) that APPEARED with a VALUE beside at
  least one -- the notable viewers at counts resolution, name-free by
  construction. If it discloses only a viewer-type choice (`all_viewers` /
  `interesting_viewers`), seeing them means APPLYING that filter, which is a
  submission the ruling refuses by name (`N 133`'s blocker): NOT PROVEN. If
  lines arrive and nothing matches, it is a vocabulary miss: NOT PROVEN, and
  said so.
* **`P O3` (WVYP Premium insights and filters) is NOT PROVEN if** the reading
  shows "show more analytics" DRAWN (`held`): the structural load found it
  carrying no sanctioned attribute, so whatever insights sit behind it are
  unreachable by any sanctioned press -- condition 2, terminal by this route.
  The filters half (their options read name-free) and the header insights the
  tool already returns do not make the row by themselves while its
  Premium-insights half is walled off.
* **Either row is claimed only on the orchestrator's two conditions** (section
  0.5): the pressed node inside `main`, and a reading of analytics content,
  not a nav menu.

### 3.0.1 THE FIRE -- 19:10:23-19:11:03 IST, one call, one page load

`scripts/_probe_readers_four_fires.py analytics` at `d912b25`: the SHIPPED
`linkedin_who_viewed_me(limit=10, open_filter_menus=True)`, attach on
127.0.0.1:9224, its own tab, closed after. Raw result (viewer rows carry
names) in the worktree's gitignored `_state/readers4/fire-analytics-raw.json`;
what is quoted here is the package's own literals and integers, printed by the
harness and nothing else.

    pages_loaded 1          rows 10          challenge terms none
    insights  headline 39   delta 25%   trend present   filters COUNT 3
    pills_found 3           stopped none

    pill  permitted  witness            appeared        new_lines  values
      0   True       expanded_true      show_results        32     show_results 365
      1   True       expanded_true      show_results        22     -
      2   True       expanded_true      show_results        37     -
    held at every press (drawn before AND while open):
        all_filters, interesting_viewers, recruiters, reset,
        show_more_analytics, time_range
    priced by (read at both ends, unmoved): headline_viewers, invitations,
        notifications_unread -- the two nav badges READ on this load

**WHAT IT ESTABLISHES, MEASURED:**

1. **The three pills open, under the gate, and close.** Three PERMITTED
   presses, each with its closure verified and its witness moving
   `expanded_true` at the open moment; no counter moved, the headline among
   them. This is the first press on this page that is KNOWN to have hit an
   analytics control -- by the structural load's order, by the `main`
   scope, and by what the reading saw arrive.
2. **Every pill reads as a FILTER FORM -- DERIVED, from one phrase.** At each
   pill's open moment the phrase "show results" came into view (`appeared`),
   and nowhere before. Read here as the form's apply control; the reading
   does not say which element drew the phrase. Choosing an option and
   applying it is the submission the disclosing-press ruling refuses by name
   -- `N 133`'s blocker, which the census measured by other means.
3. **"Show more analytics" is DRAWN** (held at every moment), and the
   zero-press load found it carrying neither sanctioned attribute. What it
   discloses is unreachable by any sanctioned press.
4. **The dialog fix holds live:** `insights.filters` read 3, where the
   pre-fix fallback would publish the dialog's two labels too.

**WHAT IT DOES NOT ESTABLISH, AND TWO LIMITS OF THE READING THAT THIS FIRE
MEASURED ABOUT ITSELF:**

* **A term already on the page cannot APPEAR.** `recruiters` was held
  before any press (the page draws a "view all recruiters" control), and
  `time_range` too (the first pill's own caption), so a disclosed option
  carrying either word is invisible to the term diff. The reading counts
  PRESENCE per phrase, not occurrences.
* **A number beside a phrase can belong to a neighbour.** `show_results`
  carried 365 on the time-range pill -- almost certainly the digits of the
  adjacent "Past 365 days" option inside the same short line, not a result
  count. DERIVED, not measured; published by the reading as a value, and
  read here as nothing.
* **22 new lines arrived on the interesting-viewers pill and none matched the
  vocabulary.** What they say is not known here, and a counts-resolution
  reading of viewer categories -- if the pill draws counts at all -- would
  need an occurrence-counting reading, which the declared script does not
  do. Not attempted: one fire per reader.

**VERDICTS, by the rules registered in 3.0 before the fire:**

* **`N 134` -- NOT PROVEN, on the registered clause it failed:** the pill
  opened under a permitted press and NO viewer category appeared with a
  value; its 22 new lines matched nothing in the vocabulary. The DERIVED
  context (point 2): it reads as a filter form, whose payload -- the
  interesting viewers themselves -- arrives only after APPLYING it, a
  submission. Gate PRESS-PERMITTED -> PRESS.
* **`P O3` -- NOT PROVEN.** Its Premium-insights half sits behind a control
  drawn on the page with no sanctioned attribute (condition 2, terminal by
  this route); its filters half is the same three filter forms. Gate
  PRESS-PERMITTED -> PRESS.

### 3.1 A GUARD CAUGHT MY OWN COMMIT, AND IT WAS RIGHT

`aba78f7` turned `tests/test_navigation_is_never_derived.py` RED on
`server.py` -- on `PROFILE_DETAIL_URLS[section]`, an untouched navigation in
`linkedin_my_profile`. That guard tracks taint PER MODULE AND BY NAME, and
`verdict` is already a tainted name elsewhere in `server.py`; my summary
helper bound `witness`, `reading`, `term` and `entry` off a parameter named
`verdict`, and the taint spread by name until the unrelated loop variable
`section` read as page-chosen. Measured with the guard's own
`_tainted_names` against the base: **24 names newly tainted by `aba78f7`, 0
after `2bc3720`**, which renames every binding in the three helpers and
changes no behaviour. **Found by the implementer child's full guard run** (it
flagged a red in a file it was forbidden to touch rather than staying
silent), not by my own run, which had not included that guard -- the scoped
gate at the end is what would otherwise have caught it.

---

## 4. `M C85` -- STOPPED AT THE ADDRESS. ZERO PAGE LOADS.

**The row:** *Vote in a poll / view poll results*, `R+W`, GAP. Its READ half
is the results, as COUNTS, under `FEED-CONTENT-READ-RULING`. Its address shape,
`/feed/update/urn:li:activity:<id>/`, is admitted (`PERMALINK-READ-IS-ALLOWED`).
A reader needs ONE SPECIFIC POLL POST, and the brief's rule is that the package
never navigates to an address the browser chose.

### 4.1 Every source this package has for a post's address, searched

| source | what it can address | why it cannot address a poll to VIEW RESULTS OF |
|---|---|---|
| `server._resolve_own_item_permalink` (the census keys `feed_item`, `feed_item_commented`) | ONE OF HIS OWN items, authorship established by the own-activity reader, chosen by the rule `first` or `most_anchors` | no rule selects a POLL, and no capture has ever measured a poll marker on his rail. And it takes no urn BY DESIGN: *"a caller handing in a urn would be handing in an identifier this server never read"* (its caller, `linkedin_surface_census`) |
| `linkedin_my_activity_items` keys, handed to `linkedin_react_to_item(item=...)` / `linkedin_comment_on_item` | his own items, at call time (*"Get it from linkedin_my_activity_items, which returns keys only for items established to be yours"*) | his own items only; and those are writes |
| `linkedin_job_detail(job_id)` | a caller-supplied id | jobs only |
| `item_addresses.py` | urns drawn on `/analytics/creator/content/`, his own, published only on opt-in | it navigates nowhere |

**The READ half of this row is reader-side.** The row's own cell: *"voting is
the reader-side act"*; the author-side poll row is a different row. The poll
whose results a reader views is SOMEBODY ELSE'S post, and **no source in the
package reaches another member's post address -- deliberately**. The one way
left to get such an address is to take it off a page the browser loaded (the
feed draws other people's posts), which is precisely the derivation
`tests/test_navigation_is_never_derived.py` exists to forbid: *"a page that can
choose the next url can choose a stranger's."*

**And the reader could not be designed from evidence even with an address.**
No capture of poll-result markup exists anywhere in this tree (every `poll`
hit in the census and audits concerns CREATING a poll, blocker
`POLL-SURFACE`), and whether per-option results render at all before a vote --
the irreversible write -- is recorded as UNVERIFIED by the bucket-3 wave and is
still unmeasured. **So no reader was built for this row**: a reader over
imagined markup would be a claim, not a check.

### 4.2 What would make it reachable -- any ONE of these, named precisely

1. **THE OPERATOR NAMES A POLL POST, and a ruling admits a caller-supplied
   item urn as a READ target at call time.** That is the targeting shape
   `INVITATION-TARGETING-IS-CALL-TIME` rules for invitations and
   `linkedin_job_detail(job_id)` already uses for jobs -- and the exact thing
   the census resolver refuses today, by design. Then one capture of that
   permalink, to write the reader against measured markup.
2. **A POLL OF HIS OWN**, found on his own rail by a structural poll marker
   (unmeasured). This reaches the AUTHOR'S view of results, which is not the
   reader-side capability this row names -- it would bank the author-side row,
   if any, not this one.
3. **Results read IN PLACE on `/feed/`**, with no navigation at all, from
   whatever poll the feed happens to draw. The page would choose the poll.
   Named because it is the one route that needs no address; NOT BUILT, because
   it is a source the brief forbids improvising, and because a reading whose
   subject the page picks cannot be pointed at the poll anybody asked about.

**State: GAP, unchanged.** The row's bucket-3 gate moves READER -> RULING in
`_audit/_census/read-addresses.tsv` (section 6), because the first thing past
the admitted boundary is not "write a reader" but "decide where a poll post's
address may come from". That moves `b3_blocked_on_nothing` by -1, recorded in
section 7 and not re-pinned.

---

## 5. `M C72` -- WHAT A PERMITTED PRESS CAN AND CANNOT DELIVER HERE, DECIDED BEFORE THE FIRE

**The row's READ half, in its own cell's words:** *"obtaining the link or
embed is done ON LinkedIn, on pages already admitted."* The census measured
the share triggers drawn on `/feed/` and the off-platform ITEMS (`Copy link`,
`Share via`, `Embed this post`) absent until a menu opens.

**THE READER** is the gate's `feed_item_share_menu` reading, taken at the
open moment of ONE press on the first feed item's own menu control, priced by
`off_state` (the `/feed/` surface's declared sensitive counter: a reaction
would move it, and a reaction is visible to the post's author). The scope
that aims at a feed item's control, rather than at page chrome, is fixed from
the structural load (section 2.2).

**WHY NO TOOL IS BUILT FOR IT -- a judgement recorded before the evidence,
not after:** a disclosure press can show that the menu OFFERS the link and
the embed. It cannot OBTAIN either. The link is copied by pressing the
menu's copy item and the embed code sits behind the menu's embed item --
both a SECOND press, on a menu item rather than a disclosure control, which
condition 2 refuses by shape (`[role=menuitem]` is on `tests/test_press.py`'s
off-list, refused terminally). **A tool built on this press would ship unable
to deliver the row's READ half**, and the tool surface does not shrink again
(`menus.py`'s ruling on exactly that). So this fire is a MEASUREMENT through
the shipped gate, and COVERED-PROVEN -- which needs a tool -- is not available
to it whatever it shows.

**THE VERDICT RULE, REGISTERED NOW:**

* **The off-platform terms APPEAR at the open moment, press permitted** -> the
  row stays GAP with its blocker re-filed from "a press" to "the SECOND
  press": reached through a permitted press, not obtained. What would close
  it: a ruling on a third sanctioned shape for a menu item, with its measured
  blast radius; or a non-press route -- for HIS OWN posts the permalink
  already addresses the post (`linkedin_my_activity_items` keys and the item
  permalink template), which banks only if that permalink is accepted as the
  share link.
* **They do not appear, or the press is refused** -> GAP, re-filed on what the
  witness and the refusal say opened, or did not.

### 5.1 THE FIRE -- 19:12:31-19:13:25 IST, one page load, one press

`scripts/_probe_readers_four_fires.py feed` at `d912b25`, attach on
127.0.0.1:9224, its own tab, closed after. Verdict in the worktree's
gitignored `_state/readers4/fire-feed-verdict.json`; every field quoted is a
package literal or an integer.

    pre-press    permitted_to_attempt, basis sensitive, scope main,
                 reading feed_item_share_menu
    load         walled False, challenge terms none, settle wait TimeoutError
                 (the feed never goes network-idle; the 15 s bound ran out)
    interlocks   in main: Playwright 48, in-page 48 -- ALIGNED
                 candidate 2 is the control menu: True, visible: True
    counter      off_state 8 before the gate took over
    VERDICT      permitted True, pressed True, priced_by [off_state]
                 (read at both ends, unmoved), closure verified
    witness      disclosed True, moved [expanded_true]
    reading      appeared [], held [], new_lines 0 (1391 -> 1391),
                 new_elements 12 (1990 -> 2002)

**THE MENU OPENED AND ITS ITEMS HAD NOT BEEN DRAWN WHEN THE GATE READ.** The
witness saw the trigger go expanded and twelve elements arrive; the reading,
taken in the same instant, found not one new line of text. The 2026-09-19
census of this page counted 10 menu triggers against exactly 1 menu item --
LinkedIn builds these menus ON DEMAND -- and a menu whose items are fetched
after it opens is empty at the only moment `press.disclose` looks. **So this
fire does not say whether "copy link" or "embed" is in the menu: UNDETERMINED,
not absent.** The analytics pills, whose content is client-side, delivered
22-37 new lines to the same reading moments before, which is the control.

**A MEASURED LIMIT OF THE GATE, RECORDED AND NOT REPAIRED HERE:** the
open-moment reading has no settle. A bounded wait between the click and the
reading -- until new lines stop arriving, capped well under a second or two --
would let an on-demand menu draw before the dismissal. It lengthens the time
a disclosure is held open and changes a safety module's timing, so it wants
its own tests and its own commit, and it would be first exercised by the
wave that needs it, not by this one.

**VERDICT, by the rule registered above -- `M C72` NOT PROVEN, and three
blockers now stand in front of it, each measured:**

1. **AIMING.** The feed draws no per-post container (section 2.2), and the
   control menu shares its only class token with the repost button, so the
   package cannot aim at one post's menu without a label (condition 2) or a
   position in `main`. This fire aimed by position behind a refusing label
   veto -- acceptable for a probe, not a shape for a package reader.
2. **THE MENU'S CONTENT ARRIVES AFTER IT OPENS**, past the gate's only read.
3. **OBTAINING needs a second press**, on a menu item rather than a
   disclosure control -- condition 2, refused by shape.

Gate in the bucket-3 table: PRESS-PERMITTED -> PRESS ("a second press that
is not a disclosure"), with the other two named in its note.

---

## 6. WHAT CHANGED IN THE CENSUS AND THE BUCKET-3 TABLE

**No row changed STATE.** `scripts/count_census_states.py --expect
J=56,P=55,M=77,N=86` MATCHES on all four slices, GAP 274, stated rows 704.

`_audit/_census/read-addresses.tsv`, my four lines only, class ADMITTED
unchanged on each (the address is admitted; `is_read_url` re-driven by the
checker):

    row     gate before        gate after   the first thing past the boundary, measured
    P O3    PRESS-PERMITTED    PRESS        "Show more analytics" carries no sanctioned
                                            attribute; filters apply by submission
    N 134   PRESS-PERMITTED    PRESS        the pill is a filter form; the viewers need
                                            APPLYING it, a submission
    M C72   PRESS-PERMITTED    PRESS        obtaining is a second press on a menu item;
                                            no per-post aiming; items drawn on demand
    M C85   READER             RULING       no sanctioned source for a poll post's address

`scripts/check_read_addresses.py`: GREEN, 67 of 67; BLOCKED ON NOTHING 1 (`M M49`,
excluded from this wave by `DO-NOT-OPEN-MESSAGING`).

Census cells, each gaining a dated paragraph that cites this document:
`profile.md` `O3`, `network.md` `134`, `messaging-and-content.md` `C72` and
`C85`. The messaging census carries no marker: its two cells never stated
that either row was blocked on nothing, and the `C72` cell had already
recorded its live measure stopping at the press boundary on 2026-09-19.

Correction markers, both ends: this document CORRECTS
`2026-09-23-bucket3-addresses.md`, `2026-09-21-what-is-reachable-now.md`,
`_census/profile.md` and `_census/network.md`, and each carries its CORRECTED
BY. The correction guard's three table-row-proximity candidates (the census
files citing this document back) are triaged on `NOT_A_CORRECTION` with the
line that produced each, as that list requires.

## 7. EXPECTED PIN MOVES -- NOT RE-PINNED; THE ORCHESTRATOR RE-PINS AT MERGE

`scripts/census_completion.py --check` at this worktree's head:

    b3_blocked_on_nothing   pinned 5   now 1   (-4)

and nothing else. Every other pin holds -- no row proved, so `delivered_*`,
`gap`, `gap_read`, `unfired` and the other five `b3_` figures are unchanged.
The tool-surface pin DID move and was re-pinned in the same commit that moved
it, as that guard requires: `PINNED_PARAMETER_COUNT` 66 -> 67
(`linkedin_who_viewed_me("open_filter_menus")`, `aba78f7`), with the row
decision stated in the commit and in the pin's own comment.

## 8. THE LEDGER

    rows in scope                                   4   P O3, N 134, M C72, M C85
    rows moved to COVERED-PROVEN                    0
    rows NOT proven, each with a measured reason    4   sections 3.0.1, 3.0.1, 5.1, 4
    rows excluded and untouched                     1   M M49 (DO-NOT-OPEN-MESSAGING)
    LinkedIn page loads, serial, paced            4 of 15
                                                        2 zero-press structure (18:57, 18:58)
                                                        1 analytics fire (19:10)
                                                        1 feed fire (19:12)
    presses                                         4   3 pills + 1 feed menu, ALL through
                                                        press.disclose, ALL permitted,
                                                        closure verified, no counter moved
    clicks outside the gate, keys, fills, scrolls   0   (the gate's own Escape after each press)
    /messaging/ or /notifications/ loaded           0
    writes                                          0   writes_enabled False throughout
    tabs leaked                                     0   own tab closed; Chrome left serving
    auth walls, checkpoints, challenges seen        0
    raw captures committed                          0   _state/readers4/ only (gitignored)
    new waivers spent                               0   the open-moment reading reuses
                                                        dom.read_count_lines' call site
    planted defects shown red                      23   7 gate, 9 reader, 7 probe
                                                        (3 planted by the child, 4 by me)

**FORCED PREDICTION (0.6): 1 of 4. ACTUAL: 0 of 4. The miss is the useful
part.** I expected one of `P O3` / `M C72` to prove and blamed the other on
targeting or content. Both failed, and on DIFFERENT walls from the ones I
priced: `P O3` on a control drawn WITHOUT a sanctioned attribute (a shape
question I had marked as merely DERIVED until the load measured it), and
`M C72` on two things no offline reading could have shown -- the feed draws
no per-post container at all, and its menu fills after it opens. The
prediction was right about `N 134` and `M C85`, and for the reasons given.

## 9. WHAT NEEDS AN OPERATOR RULING

**Superseded in part: read 9.1 first.** The four requests below were written
before `master`'s `53ba1b6` registered the 2026-09-23 rulings at 20:06, after
every fire in this document had run.

1. **A third sanctioned press shape, or not.** "Show more analytics" (the
   gate to `P O3`'s Premium insights) is a plain button carrying neither
   `[aria-expanded]` nor `[aria-haspopup]` -- the position the people search's
   All-filters control is in. `press.py`'s own docstring says a third shape is
   a RULING REQUEST with a measured blast radius. A NO should be written down
   so `P O3` stops being re-priced.
2. **May a filter be APPLIED on his own analytics page?** Every pill is a
   form with an apply control; `N 133` and `N 134` (and `P O3`'s filters half)
   all wait on applying one. The disclosing-press ruling refuses submission
   by name, so this is his call, not a mechanism.
3. **May a caller-supplied item urn be a READ target at call time?** The one
   route to `M C85` with a poll he names (section 4.2).
4. **Nothing for `M C72` until 1 is decided** -- and even then aiming at one
   post's menu has no structural handle on today's feed (section 2.2).

**AND ONE GATE REPAIR FOR THE NEXT WAVE, NOT A RULING:** the open-moment
reading has no settle, so a menu built on demand reads empty (section 5.1);
and `press.disclose` reads its before-counters and THEN clicks even when that
reading has already doomed the press (section 3). Both are the "refuse before
the click" class, and both belong in `press.py` with their own tests.

### 9.1 THE SAME REQUESTS, READ AGAINST `53ba1b6` (written 20:26, after its registration)

`master` moved twice while this wave was gating: the lane L2 merge `62a8f0f`,
then `53ba1b6`, which registers the 2026-09-23 rulings. Measured at 20:26,
with `master` at `53ba1b6`, by
`git diff --stat b0d3ab8 master -- linkedin_server/`: **empty**. No press
mechanism beyond the one this wave fired under exists on `master` either.

- **Request 2 is ANSWERED.** Ruling `VIEW-SWITCH-PRESS-RESTORED` (the
  orchestrator's, delegated, overridable) permits a press that changes which
  rows a view shows, provided the view is RESTORED and a before/after reading
  proves it. Applying a viewer filter is that press. So `N 134` and `P O3`'s
  filters half now wait on a BUILD, not on anyone (`N 133`, lane L2's row on
  the same surface, is not assessed here): open the pill (the
  disclosing press, shipped and fired here), choose the option and press
  "Show results" (the view switch), read the viewers, then reset and prove the
  reset by reading the same surface before and after. Nothing ships it today.
  This wave's brief admitted only presses the shipped gate permits, so it was
  neither built nor fired here, and the four cells stay as measured.
- **Request 1 is no longer the operator's.** Ruling
  `OUTWARD-ACTS-NEED-THE-OPERATOR` routes press-gate defaults and self-only
  presses to the orchestrator. "Show more analytics" reveals more of the page
  rather than switching which rows a view shows, so the view-switch ruling
  does not obviously reach it (DERIVED, from the control's measured shape and
  its label); the third-shape decision stands, now the orchestrator's.
- **Request 3 is the orchestrator's too**, by the same routing ruling. The
  nearest registered precedent is `D1-SEARCH-AS-READS`: values taken from the
  tool's arguments only, never from page content, with the
  navigation-derivation guard unchanged. That is the shape a caller-named
  poll urn has; no registered ruling decides it as of `53ba1b6`.
- **Request 4 moves with request 1.** `M C72`'s obtaining step (copy a post's
  link, embed it) is a press on a menu item whose effect, by its label, is his
  own clipboard or a dialog -- a self-only press, so the orchestrator's call.
  That is DERIVED from the labels: whether LinkedIn counts a link copy toward
  the post author's share figures, which would make it an act that reaches
  another person, is not measured. The aiming problem does not move with any
  ruling: today's feed draws no per-post container (section 2.2).
- **`M M49`.** `DO-NOT-OPEN-MESSAGING` is SUPERSEDED by `WRITE-CLASS-B`, and
  `OWN-INBOX-READS-COVERED-BY-B` covers opening his own threads. This wave's
  brief excluded `M M49` by name, on the old ruling; it is untouched here, and
  whether a live lane takes it is the orchestrator's to brief.
- **The live rules this wave ran under were its brief's** (budget 15, never
  `/messaging/`, never `/notifications/`) and held for every load; they are
  narrower than `LIVE-BUDGET-40-LOADS` and `NOTIFICATIONS-UNREAD-SPEND` allow,
  and nothing in this document relied on the difference.

## 10. THE MERGE AND THE GATES

### 10.1 THE MERGE, FORECAST BY A DRY RUN -- no ref moved, nothing merged

`git merge-tree --write-tree --name-only master HEAD`, run between 20:16 and
20:23 with `master` at `53ba1b6` and this branch at `7ad55ed`: **five
conflicts**.

    _audit/INDEX.md                    generated -- regenerate to a fixpoint
    _audit/RULINGS.md                  generated -- regenerate to a fixpoint
    _audit/_census/blocker-map.tsv     generated -- regenerate to a fixpoint
    _audit/_census/network.md          ONE hunk: rows 133 and 134
    _audit/_census/read-addresses.tsv  ONE hunk: rows N 133 and N 134

Both real conflicts are the same shape: lane L2 rewrote row 133, this wave
rewrote row 134, and the two sit on adjacent lines. **Resolution: keep the
dry-run merge and replace its one hunk with `master`'s row 133 followed by
this branch's row 134.** Checked mechanically by a scratch script against the
dry-run tree, all seven checks true in both files: `master` left row 134 as
the base had it; this branch left row 133 as the base had it; exactly one
hunk; every line this branch added survives (2 in `network.md`, 4 in the
table); every line `master` added survives (8 and 9); no line is invented; no
marker is left. **The first version of that check failed, and it was right
to:** it built "`master` plus this branch's row 134", which drops this
branch's OTHER edits to the same two files (the back-pointer in the network
census header, and the `P O3`, `M C72` and `M C85` lines of the table); its
merge-equality check did not hold on either file, and the recipe was rebuilt
before this section was written.

The messaging census and the correction guard's own test file merge cleanly.

After the merge, `scripts/check_read_addresses.py` and
`scripts/census_completion.py --check` need a run on the MERGED tree, since
both sides moved lines of the table; the pin moves in section 7 are this
branch's alone.

**RE-RUN BETWEEN 21:30 AND 21:33 AGAINST `867ae38`, THIS BRANCH AT `9b4dd6b`.** `master` had
moved 17 commits past `53ba1b6` (the census cleanup, lane X, lane L1).
**Six conflicts now:** the five above, plus
`_audit/2026-09-23-bucket3-addresses.md`, where both sides added a
back-pointer at the same header position -- `master`'s from the census
cleanup, this branch's from this document. Both stay. The table now has
THREE hunks (`master` moved `P L8`, `M C38` and `M C48` to MEASURE and edited
other columns of `N 133` and `N 161`; this branch moved its four rows), and
`network.md` still has one.

**The rule, row-wise, for every hunk in all three files: each row takes the
side that differs from the base `b0d3ab8`, and no row was changed on both
sides.** Checked by a second scratch script over the dry-run tree: 0 rows
changed on both sides, 0 lines lost from either side, 0 invented, 0 markers.
Shown failing first: a planted resolution that always takes `master`'s side
reports 4, 1 and 1 of this branch's lines lost. (Its first control swapped
the base instead, which disarmed the check along with the resolution and
passed; it proved nothing and was replaced by the plant.)

Auto-merged, and checked where a check is possible offline:
`tests/reader_leak_baseline.json` merges to a valid union of 123 readers
(`master`'s 120 plus this branch's three), keys still sorted.
`linkedin_server/server.py` auto-merges beside `master`'s 9 added lines; the
navigation-derivation guard (per module, by name) and the page-string family
guard need a run on the MERGED tree, which only a gate there can give.

`master` still pins `b3_blocked_on_nothing` at 5 at `867ae38`, and all four of
this wave's rows are still READER or PRESS-PERMITTED in its table, so the merge
moves the measured figure by -4 from whatever `master` measures (DERIVED, not
run on a merged tree).

### 10.2 THE GATES -- what ran, on which tree, and what did not

**The code this wave fired is the code it committed.** `d912b25` was
committed at 19:10:08; the two fire outputs are stamped 19:11:03 and
19:13:25. Since `d912b25`, `git diff --stat d912b25 HEAD -- linkedin_server/
scripts/ tests/` shows one file, 28 added lines of triage entries in the
correction guard's list. No reader, gate or probe changed after its fire, so
no fire is re-run.

    run                                          tree                          result
    scripts/impact_gate.py --against b0d3ab8     1df9061, from 19:28:18        KILLED by my own 30-minute
      widened to the full suite (189 of 219      beside a sibling's full        bound at 19:58:18; no
      files impacted, 86%, over its 45% line)    suite on 8 cores               verdict of any kind
    tests/test_a_cited_sha_resolves.py           working-tree text that         28 passed
                                                 became 7ad55ed, ~20:00
    the 12 files the gate selects for a change   working tree, 20:29:40 to      450 passed, 1 failed
      to this document alone, serially           20:36:41, with 9.1 and 10.1

**The one failure was real and was mine.** The correction guard's
candidate-pair test found two pairs from this document with correction
vocabulary within two lines of a citation and neither declared nor triaged:
this document to the 2026-09-20 profile-views recapture (section 2.2,
reporting lane L2's record), and this document to the messaging census
(section 6, which had stood since `1df9061` -- the killed gate would have
caught it). **Neither is a correction by this document**, so each sentence
was reworded rather than triaged. A `NOT_A_CORRECTION` entry mutes its pair
for good; a reworded sentence leaves the guard fully armed for a real
correction between the same two documents later. Re-checked with the
guard's own `_candidates()` and `_declarations()`: zero untriaged pairs touch
this document.

The full-suite gate on this branch's final code is recorded in 10.4: red on
its first complete run, then PASS on the repaired tree.

### 10.3 INSTRUMENTS -- register candidates, and what is disposable

Not appended to `_audit/INSTRUMENTS.md` on this branch: `master` changed that
file too, and an append here is a sixth conflict at the merge. The three
candidates below each name the mutations that killed them, as the register
requires; the orchestrator appends them at merge or declines them.

    candidate                                   shown failing by           tests that die
    press.py: OPEN_READINGS, PRESS_SCOPES,      7 plants, A-G, section 1   test_press.py,
      the open-moment reading                                              test_press_open_reading.py
    server.py: the filter-pill opener and       9 plants, S1-S8 and D1,    test_who_viewed_me_filter_menus.py,
      its fixed counter set                     section 3                  test_profile_views_filters_skip_dialogs.py
    scripts/_probe_disclosure_targets.py        7 plants, P1-P4 and the    test_probe_disclosure_targets.py
      (which control sits at each index)        child's three, 2.2

**NOT a candidate:** `scripts/_probe_readers_four_fires.py`. Its two
interlocks (Playwright's count against the in-page count inside `main`, and
the label veto) fired once, live, and passed; neither was ever shown
refusing. It is committed as the record of how the fires were aimed.

**DISPOSABLE, in the session scratchpad, never tracked:** the three live-tree
planters (the method the register forbids -- not to be reused), the
generator-fixpoint loop, the structure and label censuses of the capture,
the taint diff, the table-line editor, the SHA census of this document, the
box-load snapshot, the merge-resolution check of 10.1 (shown failing once, on
its own first recipe), and a bounded wait on process handles (shown both
ways: a gone pid returns at once, a live pid under a 2-second bound reports
the bound; it waits on a handle, so a pid reused after it opens cannot fool
it, but one reused BEFORE it opens can -- a pid measured at 20:12:40 named a
different process by 20:14:59).

### 10.4 THE FULL-SUITE GATE -- red on its first complete run, and that was the gate working

**Queued, not piled on.** At 20:12:40 the box carried three other full-suite
gates, 24 xdist workers on 8 cores and 100% CPU -- over the local ceiling of
about two -- so this gate waited on the two oldest (a bounded wait on their
process handles, 20:16:49 to 20:36:35), then on the next (to 20:41:58), and
launched when no other gate was running (none at 20:43:14, none but this one
at 20:44:51; the box was not sampled again during the run).

`scripts/impact_gate.py --against b0d3ab8` at `1c55694`, 20:43:16 to
21:09:02: widened to the full suite (189 of 219 files impacted). **REFUSED -- 2 failed, 8371 passed, 8 skipped, 1 xfailed,
in 1514 s.** Both failures are this wave's, both follow from `aba78f7`, and no
complete run had reached them before, because the only earlier full run was
killed at 30 minutes by my own bound.

1. `tests/test_every_orphan_module_is_ruled.py`,
   `test_every_ruling_is_still_about_a_real_orphan[press]`. That file held
   `press.py` as deliberately unwired, with the instruction "NOT PERMANENT:
   delete this entry when it is wired"; `aba78f7` wired it. **The entry is
   deleted on its own instruction**, and a dated note in that file's own form
   (its `search_results` precedent) names the one call site and the opt-in
   parameter it sits behind. The tool's docstring already said the wiring
   was deliberate, so `server.py` is not touched.
2. `tests/test_readers_emit_no_page_string.py`,
   `test_the_driven_set_has_not_silently_shrunk`. Three new page readers had
   no recorded verdict: `press:_take_reading`,
   `server:_open_profile_views_filter_menus` and
   `server:_profile_views_press_counters`. The per-reader test in the same run
   had already DRIVEN all three with hostile page strings and passed them;
   only the baseline lacked them. **Regenerated with that file's own writer,
   which refuses to write while any reader leaks:** the diff of
   `tests/reader_leak_baseline.json` is exactly three added lines, all three
   `clean`, and none of the other 119 verdicts moved.

**THE RE-RUN, ON THE REPAIRED TREE: PASS.** `scripts/impact_gate.py --against
b0d3ab8` at `9b4dd6b`, 21:15:44 to 21:30:00, beside one other gate (lane L3's,
running since 21:03:17 -- two gates, the ceiling, not over it): widened to the
full suite again, **PASS over the FULL SUITE, 8380 tests, in 813.6 s.** The
count is the red run's 8382 less exactly two: the `[press]` cases of the two
tests parametrized over the deleted table entry
(`test_every_ruling_is_still_about_a_real_orphan`,
`test_every_ruling_gives_an_actual_reason`).

**And the wave's new and changed test files, run on their own** at `9b4dd6b`
after the gate: 184 passed, 0 failed, 0 skipped --
`test_press.py` 77, `test_the_tool_surface_is_pinned_so_a_row_must_move.py`
51, `test_press_open_reading.py` 18, `test_probe_disclosure_targets.py` 14,
`test_every_orphan_module_is_ruled.py` 11, `test_who_viewed_me_filter_menus.py`
10, `test_profile_views_filters_skip_dialogs.py` 3.

**`scripts/census_completion.py --check` at `9b4dd6b`:** exactly one pinned
figure moved, `b3_blocked_on_nothing` 5 -> 1 (-4), as section 7 says; not
re-pinned.

**NOT RUN, and why:**

- **CI.** This branch is not pushed; the brief forbids it. CI's three
  platforms remain the certifier, and everything above is one Windows box.
- **Any gate on the MERGED tree.** Nothing is merged; 10.1 names what that
  run must include.
- **Any live fire after 19:13.** None is needed for what this wave claims: no
  file under `linkedin_server/` or `scripts/` changed after `d912b25`, the
  commit the fires ran on.
- **The final commit of this document,** which only appends this section,
  gets the doc-scoped gate (`--against 9b4dd6b`) rather than a third full
  suite; its result is in the wave's report, not here, because a document
  cannot record the gate over its own last commit.
