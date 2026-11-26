# readers-jobs26, 2026-11-26: the jobs-side readers on session 11's skeletons

Lane `readers-jobs26`, briefed by the orchestrator on master `7760a5f`
(integration 3, lane-certified, with session 11's 48 skeletons in
`tests/fixtures/live11/`). Built OFFLINE in its own worktree: nothing here
loaded LinkedIn, connected to port 9224 or started a browser against an
account. The live-session flag (`_state/LIVE_SESSION_ON` in the main checkout)
was absent at every check. Standing rules: the canonical lane file, with this
lane's substitutions (server.py block heading "lane readers-jobs26").

THE ROWS: the jobs-side lines session 11 captured -- line 1
(`admit-jobs-application-settings`) and its riders, line 15 (a Page's
Insights tab), lines 25 to 28 (a Page's About, Events, Life and Products
tabs), line 29 (career insights), line 30 (the tracker's clicked_apply
stage), line 21 (`jobs-alerts-manager`, in part) -- and the three rows the
orchestrator ruled BUILD on 2026-11-25: `J 168`, `J 19`, `J 163`.

HOW EACH ROW WAS READ. Its cell and its bar first; then the capture its step
names. Session 11's keyed skeletons and its key sit in the main checkout's
gitignored state; a LinkedIn word was taken as drawn only where hashing it
with that session's key gave the keyed shape at that place. Where the session
kept a raw capture of his own settings page, LinkedIn's interface words were
read off it by element and then confirmed by keyed shape; nothing of his own
data, and no third party's text, is quoted here or in any fixture.

---

## 0. What disk said that the brief did not

1. **The repository has no `CLAUDE.md`.** The brief says to read "the repo's
   CLAUDE.md"; none is tracked and none is on disk in the main checkout or
   this worktree. `README.md` and the lane standing rules were read instead.
2. **Line 1 carries ten rows, not nine.** The capture queue's line
   `admit-jobs-application-settings` and session 11's record list `P M12`
   beside the nine the brief names. `P M12` is read here with the line
   (section 3): it is this lane's line, and no other lane's row.
3. **`J 52`'s tool already exists.** Lane A built
   `linkedin_tracker_stage(stage="clicked_apply")` on 2026-10-10 and left the
   row GAP only because no capture drew the stage. Session 11's capture is
   that capture, so this row needed a proof and no new tool (section 2).

---

## 2. `J 52` -- the tracker's clicked_apply stage: GAP -> COVERED-UNFIRED

THE BAR, in the row's own words: *"no reader for this stage ... Owed: a reader
and an allowlist entry for the stage"*; the address was admitted by lane A
(`?stage=clicked_apply` on its own line), and lane A's record left it GAP
because *"no capture draws a clicked_apply tab, so whether the stage renders a
list at all is unmeasured"*.

THE CAPTURE: session 11, load 12, `/jobs-tracker/?stage=clicked_apply`, tracked
as `tests/fixtures/live11/tracker_clicked_apply.html`. Its words, measured by
keyed shape and written by `scripts/_build_live11_word_skeletons.py` into
`tests/fixtures/live11/tracker_clicked_apply_words.html` (eight words, 13
places, every other text `x`):

- the tab strip, drawn twice, reads `Saved <dot> 0`, `Clicked apply <dot> 0`
  (its pill checked), `Applied <dot> 0`, `Interview <dot> 0` and `Archived`,
  beside `Date posted`, `Job tracker` and the bulk bar's `0 selected`;
- one `h2` reads `No matches`, one of `shape.TRACKER_EMPTY_MARKERS`;
- no job row: no anchor matches `dom.JOB_HREF`.

So the stage IS drawn, WITH its own count, and the tracker's zero rule --
believed only when LinkedIn's count says zero AND the page draws its empty
state -- is met on the real page.

THE PROOF: `tests/test_tracker_clicked_apply_live11.py`, 7 passed. In a local
headless Chromium (every request the skeleton would start aborted by the
page's own route), the shipped `dom.read_main_text`,
`shape.parse_tracker_tabs` and `shape.tracker_empty_state` read the strip and
the empty state; `dom.wait_for_tracker_list` attaches at once;
`dom.harvest_linked_cards` finds no row; and the TOOL, end to end through
`server._read_tracker`, returns `empty: True`, `linkedin_count: 0`,
`empty_state: "No matches"`. THREE CONTROLS, each a failed read: the same
capture with its words reduced (the committed copy), the stage's count planted
at 3 with no row, and the stage's count removed. A fourth test holds the
fixture to the committed copy: the two differ on 13 lines, and each differing
line is the copy's once its declared word is reduced.

RED FIRST, as the test was written: two of the three controls first PASSED
the tool as an empty list, because the plant replaced the words where the
fixture's provenance comment lists them rather than in the markup. The plant
helper (`tests/live11_words.py::plant`) now edits the markup only and requires
the exact count it was told; both controls then fail the tool as designed.

THE CHANGE TO SHIPPED CODE: one sentence of the tool's docstring, which said
the captures draw no clicked_apply tab; it now says the stage's own page draws
its tab with a count and its empty state. The chain guard
(`tests/test_a_covered_row_names_the_artifact_that_covers_it.py`) binds
`J 52` to the tool beside `J 50` and `J 51`.

NOT SHOWN, and so not claimed: a clicked_apply stage holding rows renders the
row component the other stages do. The capture holds none. The first fire
settles it -- the same scope `J 50` entered COVERED-UNFIRED with.

THE CENSUS: `J 52` GAP -> COVERED-UNFIRED; its next-step and jobs-directions
lines left the side tables; the capture queue's single-row line
`admit-jobs-tracker-stage-clicked-apply` left the queue (its next step is a
fire, not a capture); `J 52` joins `PINNED_B1_ROWS[NO_RULING]`.

---

## 4. An organisation Page's tabs: `J 106`, `J 113`, `J 165` built; `J 114`, `J 111` read

Session 11 loaded five tabs of one organisation's Page (loads 19 to 23), the
organisation the live lane chose under `L1-D4-NEUTRAL-READ-VALUES`. Every
address was admitted by lane A on 2026-10-10. Built here: ONE tool,
`linkedin_company_page_tab(organisation_id, tab)`, `tab` one of `about`,
`events`, `insights`, over a new module, `linkedin_server/company_tabs.py`.
LOCATOR-ONLY, in the skeleton grammar (tags, attributes, the descendant
combinator, the parent step): no `evaluate`, so no `dom.py` waiver and no
edit there. The address is `company_page.company_page_url(<ten digits>)`
plus a constant path of the module; the landing may veto (it must keep the
tab), never supply.

THE WORDS, each measured by keyed shape and written by
`scripts/_build_live11_word_skeletons.py`:

- `company_about_words.html` (10 words): `Overview`, `Details`, the six
  definition terms `Website`, `Verified page`, `Industry`, `Company size`,
  `Headquarters`, `Specialties`, LinkedIn's size band `10,001+ employees`, and
  `Locations (45)`.
- `company_events_words.html` (3): `Upcoming events`, `Past events`,
  `Show more events`.
- `company_insights_headcount_words.html` (21): the two module headings
  `Hiring trends` and `Total job openings`; the screen-reader table's five
  header cells `Function`, `Number of employees`,
  `Percentage of total headcount`, `3 month growth`, `6 month growth`; the
  visible table's `Job openings growth`; the eleven job functions the table
  drew (LinkedIn's taxonomy); the current tab's path word `insights` and its
  query value `HEADCOUNT`.

The Page's own values, every event's words and every figure stay `x`; the
tests plant synthetic ones where the capture drew the real ones.

### 4.1 `J 106` -- the About tab: GAP -> COVERED-UNFIRED

MEASURED: the tab navigation marks `About` current; one `h2` reading
`Overview` opens the details card, whose own paragraph is the description and
whose definition list draws each term as an `h3` inside a `dt`, followed by
its `dd` values. THE CARD NESTS A CARD: the Page's "interested in working
here" section sits inside the details card with a paragraph of its own, so
the description is the one paragraph no nested section holds -- found by
subtraction, compared as text, never by position.

THE READER returns, under THIRD-PARTY-TEXT-AT-RUNTIME, the description and
the website, industry, headquarters and specialties, each in a
`people_data.OrganisationProse` record whose `read_from` names the fact
(`PROSE_SOURCES` gains `about_overview`, `about_website`, `about_industry`,
`about_headquarters`, `about_specialties`, after `overview_card`, which
`company_home` reads at position 0); the size as one of LinkedIn's nine size
bands, or withheld; the `<n> associated members` link's count and the
`Locations (<n>)` count as integers; the `Verified page` date as an ISO date.
A term not in the measured six is counted and its values are never read.
SCOPE, STATED: the tab draws its locations as a map and a count, not as a
list, so "locations" is the headquarters and the count.

### 4.2 `J 165` -- the Events tab: GAP -> COVERED-UNFIRED

MEASURED: a sub-page with its own `h2` reading `Events`; an `Upcoming events`
card that, on the capture, holds no event and the sentence
`<the Page's name> has no upcoming events planned` (read off the raw capture
by element and confirmed by keyed shape; the name is not written here); a
`Past events` card of six anchors to `/events/<title>-<id>/`, each holding
exactly two spans, the start and the title; a `Show more events` button.

THE READER returns each event as a `people_data.Event` record -- the title
and the canonical link, the title dropped from the address -- beside `starts`,
an ISO local date-time parsed from the span that reads as one; the title is
the one other span. An anchor that does not draw exactly one start and one
title is withheld and counted. The attendee line, which on one card named a
member, is never read. An empty tab is believed only on the Upcoming card's
own sentence, matched on LinkedIn's tail and never returned; otherwise a
zero raises. `Show more events` is reported, never pressed. NAMES-AT-RUNTIME
is the ruling the row's cell waited on ("such rows now wait on a
name-returning reader, not on the doctrine").

### 4.3 `J 113` -- the Insights tab (Premium): GAP -> COVERED-UNFIRED

MEASURED at `insightType=HEADCOUNT`: the tab navigation marks the Insights
tab current; two Premium modules, `Hiring trends` and `Total job openings`;
and a screen-reader data table whose header cells read `Function`,
`Number of employees`, `Percentage of total headcount`, `3 month growth` and
`6 month growth`, one row per job function, each growth cell's own words
`<n>% increase` or `-<n>% decrease`, every cell naming its header through its
`headers` attribute.

THE READER returns the modules drawn and each row: a function from
LinkedIn's fixed taxonomy (a function outside it withholds its row), the
employee count, the percentage of headcount (bounded at 100), and the two
growth figures, signed by their word (a sign that disagrees with the word is
withheld, never flipped). EACH CELL IS READ UNDER THE HEADER ITS OWN
`headers` ATTRIBUTE NAMES: a test swaps two header ids and the values follow
the ids, not the positions.

### 4.4 `J 114` -- four Premium facets: STAYS GAP, one of four built

On the HEADCOUNT view, "distribution and growth by function" is drawn as the
function table that `J 113`'s reader reads. The Hiring trends module draws a
chart and two summary figures that this reader does not read; "job openings
by seniority" sits behind the job-openings card's `Functions` dropdown, drawn
closed; "notable alumni" is not drawn on this view. The row is compound, and
COMPOUND-ROW-SPLITS-ONLY-ON-STATE is the orchestrator's to apply: question 1
below. NEXT: CAPTURE `C-RJ26-1`, the job-openings card's Functions dropdown
opened as a disclosure, its options read, closed, nothing chosen.

### 4.5 `J 111` -- Products and Services: STAYS GAP, the captured Page has none

Session 11's load of the products address drew the Page's tab navigation
with no Products or Services tab and no tab marked current, and an empty
body between the navigation and the footer. That organisation has no
Products tab to read; the capability is the tab of an organisation that has
one. NEXT: CAPTURE `C-RJ26-2`, the products tab of an organisation whose
Page navigation draws a Products or Services tab.

### 4.6 The tests and the controls

`tests/test_company_tabs.py`, 39 passed, through `tests/skeleton_page.py`
with no browser (every locator answered from the parsed capture,
`unmodelled` and `planted_answers` empty). THE CONTROLS, each a reading the
reader refuses: each tab's committed copy with its words reduced raises (the
words are the anchor); an unmeasured term (`Founded` planted for `Industry`)
is counted and its value never read; a size outside the bands and a date
that is not one are withheld; two `Overview` headings read no card and the
zero raises; no readable event and a silent Upcoming card raise; a function
outside the taxonomy withholds its row; a growth sign that disagrees with its
word is withheld. A synthetic name planted in the description, the
headquarters, the Upcoming sentence or an event title leaves only inside a
record, or not at all.

RED FIRST, as it happened: the first wiring dispatched the three readers
through a table, and two guards went red on it --
`tests/test_readers_outside_dom_are_a_pinned_inventory.py` (three readers no
other module calls by name) and `tests/test_a_people_reader_reads_one_page.py`
(the record builder, then named `_record`, sat behind the write door by a
name another module also defines). The tool now calls each reader by name
and the builder's name is the module's own; both guards are green on it. The
tool's docstring first said "share of headcount", and the write-claim
scanner in `tests/test_server_surface.py` read "share" as a write; it now
says "percentage of the Page's headcount".
