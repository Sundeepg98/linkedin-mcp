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

**CORRECTED BY:** `_audit/2026-11-27-jobs7.md` -- the table this section and section 4.4 read as the headcount distribution is summarised `Total job openings`, under that module heading. LinkedIn reuses the headcount header words there, so its rows are each function's job openings (row `J 174`). The reader now chooses each table by its summary, and `J 114` is re-based on session 12's load 20 (J114-READS-ITS-OWN-TABLE, 2026-11-27, sections 11.5 and 11.6).

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

---

## 3. Line 1, his resumes and application data page: `P M2` built; ten rows read

Session 11, load 11, `/jobs/application-settings/`, served at its own
address, raw kept in gitignored state (no other member on the page). Tracked
as `tests/fixtures/live11/application_settings.html`; with ten LinkedIn
words and sentences measured by keyed shape (read off the raw capture by
element, then confirmed by key), as `application_settings_words.html`.

WHAT THE PAGE DRAWS, MEASURED, inside its `role="main"` region:

- one `h1`, `Resumes and application data`;
- `Save resumes and application data`: LinkedIn's sentence "Allow LinkedIn to
  save your resumes and answers to application questions. You may change your
  answers with each application.", and ONE switch, an
  `input[role=switch][type=checkbox]` its label names by `for`: `Allow
  LinkedIn to save your resumes and answers`, `aria-checked="true"`;
- `Share resume data with hirers`: LinkedIn's sentence that hirers can view
  skills and experiences from the resumes he chooses to share, and ONE
  switch, `Allow recruiters to view your resumes`, `aria-checked="true"`;
- FOUR resume cards, each an `h3` holding the file's name (his data), a
  paragraph `Last used on <date>` or `Uploaded on <date>`, and an options
  button labelled `Show options for <the file's name>` whose menu is EMPTY
  while closed;
- `Upload resume`, a `label[role=button]` bound by `for` to one
  `input[type=file]`, and the rule `DOC, DOCX, PDF (5MB)`;
- no Save button: each switch stores itself.

### 3.1 `P M2` -- the stored resumes: GAP -> COVERED-UNFIRED

`linkedin_application_settings()` (`linkedin_server/application_settings.py`)
loads the one admitted address and, if the landing kept it, returns: the two
switches by key, each `on`, `off` or `unknown`, read off the input its own
label names (compared in this process, never built into a selector); one
entry per resume -- its file type (`pdf`, `docx`, `doc`, `other`, from the
name's own suffix), which date the card shows, and that date as an ISO date;
and whether the file control is drawn, with the types and size its rule
names. A zero is never "you have none": no empty state of this page has been
captured, so no card read raises.

SCOPE, STATED: THE FILE NAMES DO NOT LEAVE. A resume's name is his own
data, but no declared channel carries his own document names: `people_data`
records are other members' words, and the tool-envelope guard's inventory of
page text outside a record may shrink and may not grow (its ratchet, since
2026-09-24). So a name is read only to take its suffix, and the options
button's label, which repeats it, is never read. Whether his own document
names may leave is question 2.

`tests/test_application_settings.py`, 16 passed, over the words fixture
through `tests/skeleton_page.py`: both switches and four synthetic resumes
read; no planted name leaves in any field; turning the second switch off on
its own input moves only its key; a label bound to no input reads
`unknown`; the committed copy with its words reduced, and cards whose dates
do not read, each raise; an unknown suffix is `other`; the landing vetoes;
and the tool loads exactly the admitted address, and refuses to read a
landing elsewhere. The first docstring quoted LinkedIn's switch label ("to
save your resumes") and named the file control "upload"; the write-claim
scanner read both as claims, and the docstring now names neither.

### 3.2 The other nine rows on the line, and the six riders

THE OPTIONS MENU IS WHERE FIVE ROWS WAIT. Download (`J 72`, `P M4`), delete
(`P M3`, and the delete half of `J 71`) and the upload's inverse (`P M1`)
can only be behind the resume card's options button, whose menu is not in
the document while closed. NEXT: CAPTURE `C-RJ26-3`, one resume card's
options menu opened as a disclosure, its items read, closed on Escape,
nothing chosen. `J 71`'s list half is `P M2`'s reader; the row stays GAP as
one compound row until that capture.

THE PAGE TIES NO RESUME TO AN APPLICATION. Each card dates the resume's last
use or its upload and names no job (`J 73`, `P M5`). Whether LinkedIn shows
the resume an application carried is for a job he applied to: NEXT TARGET,
on the queue line `t-named-job`, "a job he applied to, and its poster".

THE PAGE DRAWS TWO SWITCHES, AND NEITHER SHARES HIS FULL PROFILE. `J 75`
("Share your full profile when you click Apply") waited on this very
surface (`O-JOB-APPLICATION-SETTINGS`), and its capture draws exactly the two
switches above. MEASURED-ABSENT under the orchestrator's
`MEASURED-ABSENT-OR-PRECONDITION` and `ABSENT-ON-HIS-ACCOUNT-PER-ROW`: not
offered to his account. REOPENER: a capture that draws such a switch.

NO SAVED ANSWER IS LISTED. `P M6` ("Saved screening-question answers") is
named by the page only as what the first switch saves, beside LinkedIn's
own words that he "may change your answers with each application"; no
answer, list or editor of answers is drawn. MEASURED-ABSENT on the same two
rulings. REOPENER: a capture that draws his saved answers outside an
application.

THE TWO SWITCHES ARE MEASURED AND NOT ADMITTED FOR WRITING. `J 74` and
`P M8` (share resume data with hirers), and `J 76` and `P M7` (save resumes
and application data), wait on lane S's writer, `linkedin_set_admitted_setting`
(next step `SIBLING:lane-S`). Its capture is now taken, and both controls
are switches -- the kind that writer sets. Admitting the page by name into
`settings_writer.ADMITTED_PAGES` is NOT done here, for two reasons recorded
as question 3: the writer's `audiences()` refuses, at import, two admitted
controls holding the same value words with different meanings (both
switches hold `on` and `off`), so it must be re-keyed first; and the write
door's exemptions would have to excuse `/jobs/application` for this
address, a boundary call lane admit5-26 owns.

`J 70` (upload a new resume) stays `SIBLING:lane-U`: the control is drawn,
and its inverse waits on `C-RJ26-3`. `P M12` (resume tips): this page draws
none. Session 2's posting, the capture its cell names, draws `Use AI to
assess how you fit` with `Tailor my resume` (keyed shapes, session 2's
key): that is row `J 147`'s capability, so `P M12`'s step becomes
`SIBLING:J 147`.

---

## 5. `J 168` -- the Page's posts: GAP -> COVERED-UNFIRED

THE RULING: `J-110-SPLITS-HOME-AND-POSTS` (the orchestrator, 2026-11-25),
"the Posts half BUILD on the live9 capture". Built as a fourth tab of the
same tool, `linkedin_company_page_tab(organisation_id, tab="posts")`, over
`tests/fixtures/live9/company_root_posts_view.html` (lane B4's tracked
skeleton of session 9's Page root, which drew the Posts view).

THE ADDRESS IS THE ROOT. The read boundary refuses `/company/<x>/posts/`; the
admitted root drew the Posts view on 2026-10-10 and the Home view on
2026-09-23, so the tool loads the root (the landing may be the root or the
Posts tab) and the reader says which view it read first. MEASURED on the
capture: the Posts view marks `aria-current="true"` on two anchors to the
Posts tab, so `current_tab` now takes agreeing marked anchors as one tab, and
anchors naming different tabs as `tabs_disagree` (a test moves one anchor to
the About tab and reads the disagreement).

THE ITEMS, MEASURED: thirteen `role="listitem"` items each hold exactly one
`h2` reading `Feed post`; eleven hold exactly one
`[data-testid="expandable-text-box"]`, one holds none (an item without
words), and the sixth holds two (a reshare: its own words and the reshared
item's). The reader returns each one-box item's words as a
`people_data.OrganisationProse` record, `read_from` `page_post` (a new
source); the box-less item and the two-box item are counted and not read --
which of two boxes is the Page's own is not attributable by structure, so
neither leaves. The view draws no permalink on an item, so no link is
returned. No feed item read raises.

`tests/test_company_tabs.py` gains five tests (44 passed): the eleven
records; each box planted with its own number, the two of the two-box item
never come back (`[0, 1, 2, 3, 6, ..., 12]` returned, measured order); no
`Feed post` heading raises; agreeing and disagreeing marked anchors; the
root address and its landings.

---

## 6. `J 37` -- the alert manager: read offline, the next step re-pointed

The brief asked for the skeleton to be read offline first. IT DRAWS THE
MANAGER, OPEN, OUTSIDE MAIN. Session 11's load of `/jobs/jam/` (load 17) drew
in `main` only the jobs discovery feed (three discovery modules), which is
why the live runner counted 0 controls there and found no trigger by name.
Outside `main`, the page draws a `role="dialog"` modal, `aria-hidden="false"`,
its header `h2` reading `Manage job alerts` (keyed shape; the jobs home of
session 2 draws the same heading), and in it a list of FIVE alert rows (one
drawn `hidden`), each: an anchor to the alert's own job search
(`/jobs/<x>/?keywords=...&distance=...&geoId=...`, with `f_TPR` or `f_SAL` on
some), the alert's query words and a second line (his own words, `x` here),
one button whose title and label are unmatched by the candidates tried, and a
detail line. The modal's `Done` button is drawn.

So the LIST half is on a real capture and buildable: the alert rows and
their search parameters. Two things stand in the way of building it here,
each recorded rather than decided: the alert's query words are his own text,
which faces the same channel question as his resume names (question 2), and
the edit button's label and what it opens are unmeasured (the MANAGE half).
NEXT: BUILD the list on `tests/fixtures/live11/jobs_alerts_manager.html`,
reading the alert rows inside the open `Manage job alerts` dialog; the
capture line `jobs-alerts-manager` leaves the queue, its capture taken.

---

## 7. `J 109` and `J 160` -- read offline, each re-pointed at its own capture

`J 109` (the Life tab, load 22, redirected within the tab). MEASURED: a hero
video; an `h3` reading `Trending employee content` over a carousel of
members' feed items (each with its author's profile link and its words, `x`
here); an interest section (`I'm interested`, LinkedIn's curly apostrophe);
an `h3` reading `Company spotlights` over the Page's own video modules.
NEXT: BUILD on `tests/fixtures/live11/company_life.html`: the two sections by
their headings, the trending items as post records (author and words, under
THIRD-PARTY-TEXT-AT-RUNTIME), the spotlights' titles as the Page's prose.

`J 160` (career insights, load 13, three other members drawn, skeleton only).
MEASURED by structure: two filter pills (the job title and the location),
a chart, three organisation cards (each a `/company/<slug>/` anchor beside a
`/company/<slug>/jobs/` link), three LinkedIn Learning cards, and three
member cards (`/in/<slug>/` anchors) -- the people and the companies the
row's cell names. No raw capture was kept and none of the section headings
matched the candidates tried, so the build's first step is measuring them
by key. NEXT: BUILD on `tests/fixtures/live11/career_insights.html`: the
members as person records and the organisations as organisation records
(name; a slug is not a numeric link, so no link), under NAMES-AT-RUNTIME.

---

## 8. `J 19` and `J 163` -- ruled BUILD, NOT BUILT by this lane

Both are writes, and both stay GAP with their next steps as integration 3
left them (`BUILD:tests/fixtures/live2/j18.html` and
`BUILD:tests/fixtures/live8/recommended.html`). This lane spent its run on
the reads above and did not reach them; nothing of either is half-built on
this branch. What each build is, from its ruling and its capture, so the
next lane starts from it:

- `J 19`, `J-19-BUILT-BEHIND-THE-GRANT` ("BUILD behind the grant, REFUSING
  until its confirm dialog is captured; it fires only on his order"): the
  refusing shape `set_tracker_stage` set (`J 54`) -- a spec sanctioned and
  NOT in `writes.PERFORMABLE`, its preview reading the jobs home (one `h2`
  `Recent job searches`, one button `Clear` beside it, session 2's keyed
  shapes) and minting no token, its refusal in `_NINE_REFUSALS` naming the
  capture that lifts it: the dialog the press opens, captured at his order.
  The fixture needs those two words written by key (session 2's key) into a
  tracked copy of `j18`.
- `J 163`, `J-163-RECEIPT-ONLY-WRITE` ("a RECEIPT-ONLY WRITE behind the grant,
  fired only on his order ... proven by that press"): a PERFORMABLE write on
  `/jobs/collections/recommended/`, its preview counting the pair inside
  `div[data-view-name="jobs-search-list-feedback"]` once each (the two
  buttons `Are you finding what you<U+2019>re looking for? No` / `... Yes`,
  session 8's keyed shapes), the press the chosen button, strict, and its
  receipt the press and the render it leaves, recorded as the row's proof.
  No inverse is built because none exists.

---

## 9. The rows, one by one

    row     from  to                 evidence (this record)
    J 52    GAP   COVERED-UNFIRED    s2: the shipped tracker tool over session 11's stage page
    J 106   GAP   COVERED-UNFIRED    s4.1: linkedin_company_page_tab(tab="about")
    J 113   GAP   COVERED-UNFIRED    s4.3: linkedin_company_page_tab(tab="insights")
    J 165   GAP   COVERED-UNFIRED    s4.2: linkedin_company_page_tab(tab="events")
    J 168   GAP   COVERED-UNFIRED    s5: linkedin_company_page_tab(tab="posts"), the live9 capture
    P M2    GAP   COVERED-UNFIRED    s3.1: linkedin_application_settings(), names withheld
    J 75    GAP   MEASURED-ABSENT    s3.2: the page it waited on draws two switches, neither this one
    P M6    GAP   MEASURED-ABSENT    s3.2: the page lists no saved answer
    J 114   GAP   GAP                s4.4: one of four facets built; CAPTURE C-RJ26-1
    J 111   GAP   GAP                s4.5: the captured Page has no Products tab; CAPTURE C-RJ26-2
    J 71    GAP   GAP                s3.2: list half built (P M2); delete behind C-RJ26-3
    J 72    GAP   GAP                s3.2: download behind C-RJ26-3
    P M1    GAP   GAP                s3.2: upload drawn; its inverse behind C-RJ26-3
    P M3    GAP   GAP                s3.2: delete behind C-RJ26-3
    P M4    GAP   GAP                s3.2: download behind C-RJ26-3
    J 73    GAP   GAP                s3.2: no tie to an application; TARGET t-named-job
    P M5    GAP   GAP                s3.2: as J 73
    J 74    GAP   GAP                s3.2: switch measured, not admitted for writing (question 3)
    J 76    GAP   GAP                s3.2: as J 74
    P M7    GAP   GAP                s3.2: as J 76
    P M8    GAP   GAP                s3.2: as J 74
    J 70    GAP   GAP                s3.2: control drawn; SIBLING:lane-U
    P M12   GAP   GAP                s3.2: none on this page; SIBLING:J 147
    J 37    GAP   GAP                s6: the manager drawn open; BUILD on its capture
    J 109   GAP   GAP                s7: BUILD on its capture
    J 160   GAP   GAP                s7: BUILD on its capture
    J 19    GAP   GAP                s8: not built here
    J 163   GAP   GAP                s8: not built here

EIGHT ROWS MOVED: six to COVERED-UNFIRED, two to MEASURED-ABSENT. Twenty left,
each with its next step re-pointed at what its capture showed.

---

## 10. Tools added

- `linkedin_company_page_tab(organisation_id, tab)` -- a READ, `tab` one of
  `about`, `events`, `insights`, `posts`; one load; a people tool (its About
  and posts values in `OrganisationProse` records, its events in `Event`
  records). Module `linkedin_server/company_tabs.py`.
- `linkedin_application_settings()` -- a READ, no parameter; one load; no
  page string leaves. Module `linkedin_server/application_settings.py`.

`linkedin_tracker_stage` (lane A) is unchanged but for one docstring
sentence. THE SURFACE, off `mcp.list_tools()`: 83 -> 85 tools, 134 -> 136
parameters, 56 -> 58 that do not write; the write side unmoved (24 write,
three write-shaped). `people_data.PEOPLE_TOOLS` gains the tab tool;
`PROSE_SOURCES` gains six sources after `overview_card`.

---

## 11. Instruments

`_audit/INSTRUMENTS.md` section 106 (numbered 104 on this lane's branch, 106
from integration 4's merge) registers three, each shown failing:

1. `scripts/_build_live11_word_skeletons.py` -- writes a LinkedIn word into a
   tracked copy only where its keyed shape matched, and REFUSES when a
   declared word matches nowhere or when the keyed skeleton's tracked copy is
   not the committed one. Shown failing, both ways, on the clicked_apply
   skeleton: a declared count the page does not draw (`Clicked apply <dot> 7`)
   refused the build, and a measured word under another session's key
   refused it too ("1 declared word(s) matched no keyed shape; refusing").
2. `tests/live11_words.py::plant` -- an asserted edit of the MARKUP only,
   with the exact count. Shown failing as it was written: its first form
   edited the words fixture's provenance comment, and two controls of
   section 2 passed the tool as an empty list; it now refuses a count that
   is not the markup's.
3. The chain guards in `tests/test_a_covered_row_names_the_artifact_that_covers_it.py`
   for `J 52`, the four tab rows and `P M2` -- each tool must call its row's
   reader by name; the tab guard's control renames one call on a copy and
   watches the set lose it.

Declared disposable: this lane's scratch probes (the keyed-shape matcher,
the raw-capture UI reader that prints element text by class, the outline
printer) and its edit scripts, kept outside the repository.

---

## 12. Pins, re-derived from what `census_completion.py` measured

Each commit re-pinned the figures its moves changed, each to the value the
script printed, never summed (`scripts/census_completion.py`, the comment
above each pin). Net over the lane, base -> head:

    adjudicated      245 -> 253      delivered_broad  160 -> 166
    unfired           43 -> 49       gap              529 -> 521
    gap_unknown       93 -> 87       gap_read          77 -> 75
    out_of_scope      68 -> 70       achievable       706 -> 704
    capabilities_achievable 719 -> 717
    b1_no_ruling      27 -> 33       b3_admitted       46 -> 44
    jobs_gap          93 -> 87       jobs_dir_r        30 -> 25
    jobs_dir_w        56 -> 55       jobs_admitted     29 -> 24

`PINNED_B1_ROWS[NO_RULING]` gains `J 52`, `J 106`, `J 113`, `J 165`, `J 168`,
`P M2`. The capture queue loses nine lines whose captures session 11 took
(the clicked_apply stage, the About, Events, Insights, Products, Life and
career-insights addresses, the application settings page and the alert
manager -- each line leaving when its last row's step stopped being its
capture) and gains three (`C-RJ26-1` to `C-RJ26-3`); `t-named-job` gains
`J 73` and `P M5`. `exclusion-basis.tsv` gains `J 75` and `P M6` (class M+).

---

## 13. Gates

LOCAL, targeted and backgrounded, the live-session flag absent at every
check; the full suite runs on CI only. Per commit: the lane's own test files
(7 + 44 + 16 passed at the head), the surface and page-string guards
(tool surface pin, server surface, every tool on the surface, people
reader, readers inventory, reader-leak and tool-envelope guards with their
baselines regenerated by their own writers, navigation never derived, error
url per site, people data), the census guards (next step, jobs directions,
read addresses, exclusion basis, write classes, ruling holds, census rows,
row total, literal repeats, correction findability, covered-row artifacts),
the three derived views written and checked, and the identity gates: the
pre-commit gate on every commit (226 spellings, 0 hits) and
`tests/test_no_committed_identity.py` after each.

LANE CI, by head sha:

    head      run           verdict
    71b3970   45768580137   failure, three tests: the instructions did not
                            name the tab tool among the people tools; the
                            tab tests used an organisation id not on the
                            identity guard's synthetic list; the new readers'
                            raises were not declared to the error-url guard.
                            All three fixed in 43221ff.
    fb15538   45771696426   failure, three tests: the read-gap triage
                            instrument still held a verdict for P M2, which
                            left the read-GAP set (two of its tests); and
                            J 75's MEASURED-ABSENT note wrote its reopener
                            in lower case, which the contingent write-off
                            checker does not read (it takes the shouted
                            REOPENER). Both fixed in the record commit.

The later heads' runs are in section 16 and the final report.

---

## 14. Questions for the orchestrator, each with its ground

1. `J 114` -- SPLIT IT, OR HOLD IT WHOLE. Ground: section 4.4; one of its
   four facets (distribution and growth by function) is built and read on a
   real capture, the other three are not drawn on the admitted view or sit
   behind a closed dropdown; COMPOUND-ROW-SPLITS-ONLY-ON-STATE splits a row
   whose halves need different states, and these do.
2. HIS OWN DOCUMENT NAMES AND ALERT WORDS -- MAY THEY LEAVE. Ground: section
   3.1 and section 6; his resume file names and his job alerts' query words
   are his own data, but `tests/test_tool_envelopes_emit_no_page_string.py`'s
   ratchet admits no new path for page text outside a `people_data` record,
   and those records are other members' words. `P M2` ships with the names
   withheld; `J 37`'s list would ship without its query words. A ruling that
   admits his own text (as `ADMITTED_TEXT` already does for the reader guard,
   under HIS_OWN) would let both carry it.
3. THE APPLICATION SETTINGS PAGE'S TWO SWITCHES -- ADMIT THE PAGE BY NAME FOR
   WRITING. Ground: section 3.2; both controls are switches, the kind
   `linkedin_set_admitted_setting` sets, but its `audiences()` refuses two
   admitted controls sharing the value words `on` and `off` with different
   meanings, and the write door would need `/jobs/application` excused for
   this one address -- the second is the boundary, lane admit5-26's.

---

## 15. Open items

- `J 19` and `J 163` (section 8): not built.
- `J 37`, `J 109`, `J 160`: each a BUILD on its own session-11 capture.
- `C-RJ26-1` to `C-RJ26-3`: three session-12 captures, each one load on an
  admitted address, the first and third one disclosure each.
- The new readers are `not_driven` in the reader-leak baseline (the planted
  page reads no structure, so each raises its uncorroborated zero); a
  shipped drive over each words fixture, as `company_people_insights` has,
  would drive them to their success path.
- INSTRUMENTS section 106 (104 on this lane's branch) and the live11 fixture
  count (53 on this branch) may meet
  another wave-2 lane's equal edit at integration 4.

---

## 16. Certification

Round 1's head, `7c5969f`, was certified by lane CI run 45772883625 (success,
six jobs, 9m45s). The final head and its run are in the lane's final report:
a commit cannot carry its own run.

---

## 17. Round 2: the orchestrator's three answers, applied

The orchestrator answered sections 14's three questions on 2026-11-26
(integration 4 registers the rulings).

- `J-114-SPLITS`: YES, on the `J 110` -> `J 168` precedent. `J 114` keeps the
  built facet ("distribution and growth by function"), COVERED-UNFIRED, never
  fired; the three unbuilt facets ("headcount over time, notable alumni, job
  openings by seniority") enter as `J 169`, GAP, next step `C-RJ26-1`, which
  now lists `J 169`. The population moves 774 -> 775 (`jobs.md` 167 -> 168
  rows), re-derived by `scripts/pin_census_rows.py --write` and
  `census_completion.py`; `J 114` joins `PINNED_B1_ROWS[NO_RULING]`.
- `HIS-OWN-TEXT-AT-RUNTIME`: YES. The tool-envelope guard gains ONE door,
  `ADMITTED_OWN_TEXT`, naming each tool, the page it reads and the fields it
  returns, with one reason; no people tool may hold it. RED FIRST, its control:
  the same new text path is refused for a tool the door does not name and
  admitted for the one it does (a third party's text arriving through any
  other tool stays a new text path). The reader guard's own door,
  `ADMITTED_TEXT`, is NOT used: it admits only a reader a shipped drive takes
  to its success path, and the planted page drives this one to its raise, so
  it is recorded `not_driven` and needs no door (an entry added first failed
  `test_a_reader_joins_the_text_inventory_only_by_the_ruling`, "an admission
  must be earned by a drive", and was withdrawn). `P M2`'s reader now returns each stored
  resume's `file_name`, sanitised and bounded; the scope clause of section
  3.1 is lifted, and the tests plant synthetic names (one with a zero-width
  space, which comes back removed).
- `APPLICATION-SETTINGS-WRITE`: ADMITTED IN PRINCIPLE -- his own switches, a
  reversible on/off pair, behind the grant, proven by a live round trip. THE
  BUILD IS DEFERRED to the first build lane after integration 4: the write
  door's excusal is in `readonly.py`, which lane admit5-26's held branch has
  changed. Not built here, and `readonly.py` is not edited. `J 74`, `J 76`,
  `P M7`, `P M8` keep their next step.

NOT REACHED IN ROUND 2, each still at the next step section 9 gives it, and
nothing of any of them half-built on this branch: `J 37` (the alert list, on
its capture; its query words may now leave through the door above, by its
tool's own entry), `J 109`, `J 160`, `J 19` and `J 163` (section 8). This
lane's context ran out before them; the round's three answers are applied
and certified instead.
