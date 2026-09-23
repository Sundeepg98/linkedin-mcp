claude-opus-5-5[1m]

# READERS FOR THE FOUR ROWS BLOCKED ON NOTHING: P O3, N 134, M C72, M C85

**CORRECTS:** `_audit/2026-09-23-bucket3-addresses.md` -- row `M C85` was gated READER ("no reader exists"); the first thing past its admitted boundary is a RULING on where a poll post's address may come from, so "blocked on nothing" is 4 of 67, not 5 (section 4).

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
defects by the child and four more by me (P1-P4, section 8).

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


**AND A DEFECT IN THE SHIPPED INSIGHTS READER, on `P O3`'s own surface.** The
same capture carries five `<label>` elements: three inside the pills, TWO in
a form inside a closed dialog in the right rail, both under the reader's
40-character cap. The page has no `data-view-name` at all, so
`PROFILE_VIEWS_INSIGHTS_JS` takes its `<label>` fallback and publishes all
five as `insights.filters` -- two of them a feedback form's options. Measured
by my own structure-only census of the capture; L2 reported the same from the
10:02 capture. Fixed in section 3.

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
