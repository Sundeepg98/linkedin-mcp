# Lane B1, 2026-10-10: fifteen profile rows on real captures -- what the captures draw, the one select that was waiting, and three readers

Lane `lb1-profile-build`, briefed by the orchestrator at 15:18 IST on master
`f93104c` (origin/master `1027bf8` an ancestor; the merge of it was a no-op).
Built OFFLINE in its own worktree: nothing here loaded LinkedIn, connected to
the browser port, or started a browser outside the test engine. Three children
built closed slices in their own worktrees (sections C to E); each was reviewed
and merged here by the lead.

THE ROWS (15), each `next=BUILD` in lane K's next-step ledger (read READ-ONLY
from lane K's worktree, its latest not yet on master):

    P A11, A13, A17        intro editor, autocomplete fields     tests/fixtures/live4/editor.html
    P A14, A15, A22        intro editor, full read               live-lane _state/live7/editor.skeleton.html
    P D25, D26, F1, K8     his own profile                       live-lane _state/live8/lk_inme.html (+ skeleton)
    P L8                   /dashboard/                           live-lane _state/l1-overview.html
    P S8                   /premium/profile-key-skills/          live-lane _state/live8/lk_keyskills.skeleton.html
    P L2b                  his followers list                    tests/fixtures/live2/followers.html
    P A25                  /in/me/overlay/contact-info/          live-lane _state/l1-contact.html
    P L1                   /analytics/creator/audience/          live-lane _state/l1-audience.html

---

## A. What each capture draws, measured before anything was built

Every reading below was taken offline by the lead with a counts-only probe
(disposable, section J): on a RAW capture it compares text nodes and
accessible labels against a CLOSED list of LinkedIn's words and prints the word
and integers only; on a SKELETON it computes a candidate word's keyed shape
under that session's own gitignored key and counts the exact shape. No text of
a page was printed.

### A.1 The intro editor (P A11, A13, A14, A15, A17, A22)

Two captures of the ONE dialog holding Save: session 1's RAW
(`_state/live1/editor_fields.html`, 2026-09-23) and session 7's SKELETON
(`_state/live7/editor.skeleton.html`, 2026-10-10).

    control (by its label)   kind                          session 1   session 7
    (unnamed) x2             text input                    yes         yes      P A4's name fields
    Additional name          text input                    yes         yes
    Pronouns                 select of 5                   yes         yes
    Country/Region           input, aria-autocomplete=list yes         yes      P A11
    City                     input, aria-autocomplete=list yes         yes      P A13
    Organization             select of 2                   NO          YES      P A22
    Education                select of 2                   yes         yes
    Industry                 input, aria-autocomplete=list yes         yes      P A17
    Tap to toggle setting    switch x2                     yes (+2 div wrappers with role=switch)   yes

Session 7: ELEVEN controls, every one accounted for. MEASURED, both captures:

- THE THREE AUTOCOMPLETE INPUTS NAME NO LIST. Each carries
  `aria-autocomplete="list"` and nothing else that points at a list: no
  `role`, no `aria-controls`, `aria-owns`, `aria-expanded` or
  `aria-haspopup`, no `list` attribute; the dialog draws 0 `role=listbox` and
  0 `role=option`. LinkedIn draws the entry list only after typing, and no
  capture has typed.
- NO POSTAL CODE AND NO LOCATION DISPLAY CHOICE. None of 70 candidate labels
  beyond the eleven above matched (among them "Postal code", "ZIP code",
  "Location", "Location display", "Show my location as", "Use current
  location").
- THE NEW SELECT IS "Organization": its label's shape equals that word's under
  session 7's key (one occurrence); two options, "Please select" (empty value)
  and one entry whose value is a ten-digit company id. DERIVED, from Help
  `a550169` ("If you've already added Primary Position(s) select the company
  you want to show in your intro") and its placement beside "Education", its
  school counterpart (P A21): this select is the act P A22 names.

### A.2 His own profile (P D25, D26, F1, K8)

Session 8's RAW first render of `/in/me/` (`_state/live8/lk_inme.html`,
2026-10-10 14:15, 360 text nodes, 190 labels), and sessions 2 and 3's tracked
copies (`tests/fixtures/live2/in_me.html`, `live3/in_me.html`), which keep
"Recommendations", "Experience", "Skills", "Top Voice", "Profile strength" and
"Add profile section" verbatim as furniture:

    word                  session 8 raw: text / label / anywhere     sessions 2, 3 tracked
    Add section           3 / 0 / 3 (the three links)                (not furniture)
    Recommendations       0 / 0 / 1 (outside text and labels)        0, 0
    Top Voice             0 / 0 / 0                                  0, 0
    Profile strength      0 / 0 / 0                                  0, 0
    All-Star              0 / 0 / 0                                  --
    Intermediate          0 / 0 / 0                                  --
    Suggested for you     0 / 0 / 0                                  --
    Experience, Skills    no heading (0 exact text nodes)            0, 0

What the first render does draw: About, Featured, Activity, the analytics
block ("Private to you" twice), and the top card ("Open to" x3, "Enhance
profile" x3, "Add section" x3). The read boundary admits `/in/me/details/`
for skills, experience, education and interests only -- not recommendations.

### A.3 The contact-info overlay (P A25)

Session 1's load of `/in/me/overlay/contact-info/` (`_state/l1-contact.html`,
2026-09-23) redirected to his profile. Skeletoned into scratch under a fresh
key: four `dialog` elements, two holding the same pair of radio inputs the
editor capture holds, two holding no control; 0 of "Email", "Phone",
"Website", "Websites", "Birthday", "Address", "Connected", "Your Profile",
"Contact Info". Its ONE "Contact info" is a text inside the top card's link to
the overlay, outside every dialog. THE PANEL IS NOT DRAWN.

### A.4 The key-skills page (P S8)

Session 8's skeleton of the page (`_state/live8/lk_keyskills.skeleton.html`,
kept "as a variant of the address"), 0 dialogs. `main` holds: a Premium mark
and the page heading; a first section whose heading is 15 characters, holding
ONE `input[role=combobox]` with `aria-autocomplete` and `aria-expanded=false`
(the add-a-skill typeahead); a second section (heading 21 characters) listing
SIX items, each an icon and a skill's name, NO control in any item, then a
"Show all" button; "Suggested for you" with THREE buttons, each named four
characters longer than its visible word (DERIVED: "Add <skill>"); and a fourth
section of prose. THE CHOOSER IS DRAWN.

### A.5 The two analytics pages (P L8, P L1)

Skeletoned into scratch under a fresh key. `/dashboard/`: an analytics nav
(Overview, content, audience) and ONE section of FOUR metric cards, each a
link to its analytics page holding a value, a label, a delta and a comparison
period ("Total followers" matched on one card). `/analytics/creator/audience/`:
"Total followers", "Top demographics", and each of "Job title", "Location",
"Industry", "Seniority", "Company size" twice.

### A.6 His followers list (P L2b)

The tracked `tests/fixtures/live2/followers.html`: one `[role=tablist]` (a
"Following" tab, not selected, and the selected one); ONE `ul[role=list]` of
TEN rows, each a `search-entity-result-universal-template` with two member
links and ONE follow-state button reading "Following" (nine rows) or "Follow"
(one row).

---

## B. P A22 -> COVERED-UNFIRED: the select was the missing piece, and the shipped write already chooses it

Lane L7 (2026-09-24) wrote the row's bar: "The family delivers it with no new
code once the control is named -- a select, chosen by its own option text."
Section A.1 names it. Built here:

- `scripts/_build_intro_editor_live7_fixture.py` -> `tests/fixtures/live7/editor.html`
  (lane K's PLANNED copy). From session 7's skeleton: every text of his one
  `x`, ids `k<hash>` (the session-2 `tracked_copy` rule); LinkedIn's labels
  restored ONLY where their keyed shape stands (Organization, Pronouns,
  Additional name, Country/Region, City, Industry, ...); LinkedIn's option
  words only as an option's text (the pronoun words also stand once on his top
  card and are NOT restored there); `aria-autocomplete` values from its closed
  vocabulary; the organization and school options INVENTED ("Example
  Organisation", "Example School"). `--check` re-derives byte for byte on this
  box (its inputs stay on the live lane's box); CI holds the pinned digest.
- ONE FORMAT CORRECTION, found by the first red: the skeleton writes every
  node on its own line, so an option's text carried two line breaks, and the
  shipped value reader returns a select's text untrimmed by design. The first
  drive read the original as a newline-wrapped string, the choice never read
  equal, and the write -- rightly -- withheld Save (`the_field_did_not_move`).
  LinkedIn's live options carry no such whitespace (P A21's live proof read the
  chosen option equal at the first poll), so the builder writes each option's
  text inline.
- `tests/test_the_intro_editor_draws_his_organization_select.py`: the pinned
  digest; the C1 reading held on the tracked copy (the eleven controls by name
  and kind -- the evidence for A14, A15 and A22 together); and the REAL CALLS
  over the real-capture skeleton -- `preview` (names the resolved target:
  field `Organization`, value `Please select`), `consume`, `writes.perform` --
  in a world that renders the stored choice, plants a notify control read off
  (condition 1, as every editor world in this suite) and persists the chosen
  TEXT on Save: the unset option SAVED and verified on a fresh render, then
  the receipt's own `to_put_it_back` run as the INVERSE, restoring "Example
  Organisation" exactly.

RED FIRST, three reds, each kept:

1. The first drive over the copy as first built (15:55), the act failing for a
   reason in the FIXTURE, caught by the shipped path itself:

        AssertionError ... "performed": false ... "previous_value":
        "\nExample Organisation\n" ... "field_press": {"waited_for_the_requested_state":
        {"reached": false, "polls": 25}, "only_the_field_moved": {"proceed": false,
        "code": "the_field_did_not_move", "why": "the field does not read the
        requested value after the change; Save was not pressed."}}
        1 failed, 4 passed

   Fixed in the BUILDER (options inline), never in the test or the package.
2. THE CONTROL: the same write over session 4's editor, where no
   "Organization" select is drawn, refuses before anything is chosen:
   `WriteAttemptError: refusing to click: ... 0 controls in this editor are
   named 'Organization', where exactly one is required` -- and stores nothing.
   So the pass is the control's presence, not the harness's
   (`test_red_session_4s_editor_refuses_the_same_write`).
3. The builder's `--check`, on a copy with one word planted ("Example
   Organisatioz"): `the committed fixture is STALE`, exit 1; restored: current,
   exit 0.

GREEN: 7 passed (the pin, the eleven controls, session 4's absence, the
preview's target, the write, its inverse, the control), 43 s.

---

## C. P L2b -- child lb1-followers: built, NOT merged, the row left GAP

Child `lb1-followers` built in its own worktree, on its own branch: the
reader, then a followers-list tool, two commits over the tracked session-2
skeleton -- rows,
relations and denominators only, never a name, the button's aria-label never
read (no `get_attribute`, no evaluate, held by an AST test). Red first
(`ImportError`), then 33 passed; every plant shown changing the verdict and
three weakened checks shown letting their plants through.

ITS FIRST QUESTION DECIDED THE ROW, and the lead ruled it: by
`WHO-WHICH-COUNTS-ARE-NOT-DELIVERY` ("A ROW WHOSE PAYLOAD IS WHO ... IS NOT
DELIVERED by a reader that publishes only counts") and `NAMES-AT-RUNTIME`,
both later than this row's cell, counts do not deliver an "own follower
LIST". The name-returning half -- people records, under the ruling on
people data's six mitigations, over a fixture of declared synthetic people --
was ordered at about 16:55 and COMMITTED on the branch at 17:11 (its third
commit: each follower as a people record beside its relation). It was neither reviewed nor
merged here: the box's clock stood still from about 17:13 to 19:00 (both the
lead and the child measured the jump), and the coordinator's wrap-up order of
19:02 stopped new merges. This section first said the half was unfinished; at
19:16 the branch's own log showed the commit, and the text was rewritten.
NOTHING of the branch is merged. Both halves are the next lane's to review
and merge, and with them this row's move.

Its live-proof spec, for when it lands: 3 loads -- his feed, the list, his
feed -- because the allowlist line brackets the invitation badge around this
address's first load; a read, no inverse; STOP-ALL on a landing elsewhere, a
wall or a challenge, or the "Following" tab selected.

## D. P L8 -> COVERED-UNFIRED -- child lb1-dashboard

Built by child `lb1-dashboard` in its own worktree (commits `d9dea2c`,
`ef2af22`, `05efa66`), reviewed and merged here; its report is the source of
the reds below.

- THE FIXTURE: `scripts/_build_dashboard_fixture.py` -> `tests/fixtures/live1/overview.html`
  (lane K's PLANNED path), from session 1's raw capture through the session-2
  `skeleton_of` and `tracked_copy` under a secret key kept off the tree. Every
  text one `x` except what the reader reads, each restored only where its
  keyed shape stands at that node inside one card: four path words, three
  labels ("Post impressions in 7 days", "Total followers", "Profile viewers
  in 90 days"), the period "vs. prior 7 days" three times, two icon names.
  DECLARED SYNTHETIC: every value (41, 512, 63, 27), every delta, and the
  search card's dated label and period. The build REFUSES on a wrong card
  count or a label naming another metric than its address.
- MEASURED on the raw (keyed hash, never a printed value): one `main`, ONE
  metric `section` holding no `/in/` link, FOUR cards, each an `a` to its
  analytics page holding exactly four `p` (value, label, delta, period) and,
  on three of them, an `svg[id]` icon; his profile card in an `aside`
  outside the section. The icons' geometry: `caret-up-small` points up,
  `caret-small` down. DERIVED: up means increase (the CSS is never read).
- THE READER: `linkedin_server/analytics_hub.py`, locator reads only (no
  evaluate). A card is returned only when its link's analytics address AND
  its label name the same metric, both closed vocabularies; integers and
  closed words out (value, delta signed by a named icon only, window,
  period), with `cards_seen`, `cards_parsed`, `labels_unrecognised`,
  `paths_unrecognised`, `metrics_drawn_twice` and `readable`. Every string it
  can publish is in its own `emitted_alphabet()`, tested over nine variants.
- THE TOOL: `linkedin_analytics_hub()`, one load of `/dashboard/`,
  `assert_not_authwall`, the reader. Envelope verdict `clean` (measured by the
  envelope guard's own `drive_tool` at the merge, where the child had not
  recorded one); reader-leak verdict `clean`.
- RED FIRST: `ImportError` before the module (16:15); GREEN 26, then 34 after
  `05efa66` (a plain "1234" read None under the first value pattern: red,
  `1 failed, 33 passed`, then green). SEVEN mutations, each turning its tests
  red (any href a card: 8 failed; a label naming another metric: 1; an
  unrecognised label kept: 3; the card texts carried out: 3; a worded value
  parsed: 5; no icon read as increase: 1; the scope reaching the aside: 3).
- EVIDENCE CLASSES: the four addresses, three labels, the period and the icon
  names MEASURED; values beyond three digits and a period crossing a month
  UNVERIFIED (accepted, no capture shows them); the sign DERIVED.

## E. P L1 -> COVERED-UNFIRED -- child lb1-audience

Built by child `lb1-audience` in its own worktree (commits `40da8b5`,
`90ad323`, `d9c45a2`), reviewed and merged here; its report is the source of
the reds below.

- THE FIXTURE: `scripts/_build_audience_fixture.py` -> `tests/fixtures/live1/audience.html`
  (lane K's PLANNED path), from session 1's raw capture through the session-2
  `skeleton_of`, `tracked_copy` and `value_shape` under a secret key kept off
  the tree. Eight UI words restored only where their keyed shape stands
  ("Total followers", "All", six dimension words); DECLARED SYNTHETIC: the
  total (1,250), six label and share pairs, and one planted RARE entry; both
  asides emptied. Its own `--verify` was shown failing on the child's first
  build, whose every restore had landed one line early (`HTMLParser.getpos()`
  in `handle_data` reports the PRECEDING tag's line), which a round-trip
  `--check` could not see because it re-derives by the same rule; `--check`
  was shown failing on a planted one-letter change.
- MEASURED on the raw: ONE nav whose buttons are the dimension words -- SIX,
  where this row's cell named five ("Company" as well) -- plus "All", the only
  button with `aria-current="true"`; six `role=progressbar` entries, each a
  dimension word, a label and a share whose digits equal the bar's
  aria-label; "Total followers" beside one integer. The first render draws
  the "All" view, one top entry per dimension; each dimension's own list
  needs a tab press, which is not sanctioned.
- THE READER: `linkedin_server/audience_analytics.py`, locator reads only. The
  total as an integer; the dimensions (closed vocabulary) and the current
  view; each entry `{dimension, label, share_percent}` with the label through
  `census_shape` then `census_redact_rare` (count = entries of the same shape
  in this read), shaped in one place; every other dimension reported
  present-but-unread; denominators for an empty read.
- THE TOOL: `linkedin_audience_analytics()`, one load, `assert_not_authwall`,
  the reader; envelope and reader-leak verdicts `clean`.
- RED FIRST: the tool's tests failed before it was registered
  (`AttributeError ... no attribute 'linkedin_audience_analytics'`); then 13
  passed. FOUR weakenings, each turning tests red: redaction off (5 of 11 --
  a planted name left the reader), any drawn word accepted (2), entries read
  page-wide (1 -- the aside read), the view taken from the first tab (2).
- THE RESIDUAL, put to the orchestrator (section K): `census_redact_rare`'s
  own contract lets a shape that is exactly ONE capitalised word survive, so
  on this surface a one-word label -- an employer under "Company" -- can come
  back verbatim at runtime.

---

## F. The rows left GAP, each with its exact reason

Each cell carries its paragraph (2026-10-10, lane B1); the reason, the evidence
section above, and the step that would lift it:

    row    the reason, measured                                     next step
    A11    the pick has no measured list to aim at: Country/Region  capture C-B1a
           is aria-autocomplete=list with no list relation, and
           no capture draws a listbox or an option (A.1)
    A13    the same, City                                           capture C-B1a
    A17    the same, Industry                                       capture C-B1a
    A14    session 7's eleven controls hold no postal code (A.1)    the orchestrator:
                                                                    MEASURED-ABSENT?
    A15    nor a location display choice (A.1)                      the same question
    D25    the capture draws the control (3 links), not the menu;   the operator names
           the target address is on no allowlist line (A.2)         the address
    D26    no capture draws a meter: 0 everywhere in session 8's    a capture below the
           first render, 0 in sessions 2 and 3 (A.2)                first render
    F1     no Recommendations section on the first render, and      ADMIT
           /in/me/details/recommendations/ is not admitted (A.2)    /in/me/details/recommendations/
    K8     re-read: 0 "Top Voice" in text, labels and markup of     the orchestrator:
           session 8's first render, top card included (A.2)        MEASURED-ABSENT?
    S8     the chooser is drawn, but the add path is the same       capture C-B1a on this
           unmeasured pick and no removal is drawn, so no inverse   page, and the removal
           can be aimed (A.4)
    A25    the panel is not drawn: the address redirected and no    a sanctioned route to
           dialog is the panel (A.3)                                the panel

WHY NOTHING WAS BUILT FOR THEM ON SYNTHETIC MARKUP. Every one of these would
have needed a list, a meter, a badge, a section or a panel that no capture
draws. A reader or a pick built on invented markup moves no row -- a reader
built that way has failed live here before -- and it would be the code most
likely to be trusted wrongly the day a capture disagrees with it.

### F.1 Capture C-B1a: the entry list of one autocomplete field

The one measurement that would unblock four rows (A11, A13, A17, and S8's add
half). NEEDS A SANCTION: it types into his own editor without saving, which no
shipped tool does.

- WHERE: `/in/me/edit/intro/` (admitted), his own intro editor.
- WHAT: on ONE autocomplete field (City first: no other person is named by it),
  read the field's stored value (never written to a tracked file), type its
  first three characters, wait up to 5 s for an element with `role=listbox`
  or `role=option` to appear anywhere in the document, and keep a SKELETON of
  the page (keyed shapes, as sessions 2 to 8). Then press Escape, close the
  dialog by its Dismiss control -- NEVER Save -- and load the editor again.
- RECORD (counts and shapes only): the input's `aria-expanded`,
  `aria-controls`, `aria-owns`, `aria-activedescendant` after typing; where
  the list sits (inside the dialog or at the body); the option count, each
  option's role, and the shape of its accessible name; whether the stored
  value's own entry is among them (by keyed shape).
- LOADS: 2 (the editor; the re-read). PRESSES: none but Escape and Dismiss.
- STOP-ALL: the re-read shows the field's stored value changed; a Save
  pressed or drawn as pressed; any wall or challenge.

---

## G. The census moves and the pins

THREE ROWS MOVED, each on its own cell's bar:

    row     from -> to                   the evidence
    P A22   GAP -> COVERED-UNFIRED       section B: the control named by session 7's capture;
                                         the shipped write driven over its tracked copy
    P L8    GAP -> COVERED-UNFIRED       section D: a reader and a tool over the tracked
                                         skeleton of session 1's capture
    P L1    GAP -> COVERED-UNFIRED       section E: the same, the audience page

TWELVE STAYED GAP with their reasons: section F, and `L2b` in section C.

THE PINS, re-derived each time from `scripts/census_completion.py`'s measured
figures, never added by hand: at A22 (adjudicated 187, delivered_broad 131,
gap 584, unfired 22, gap_write 378, b1_no_ruling 10, b1_released 2); again on
the tree merged with master `0103810` (214, 136, 557, 25, 361); then at L8 and
L1 (adjudicated 216, b1_no_ruling 12, b3_admitted 39, delivered_broad 138,
gap 555, gap_read 90, unfired 27). `PINNED_B1_ROWS` gains `P A22`, `P L1` and
`P L8` under no ruling (A22 cites RELEASED BY SELF-PROFILE-EDITS-NOT-OUTWARD,
as A8 does). The ledger loses the three (`check_next_step` GREEN at 555); A22's
write-class line reads `built:update_profile_field`; L8 and L1 leave bucket 3
(`check_read_addresses` 90 of 90). The DELTA block in `profile.md` section 1
is re-derived on the merged tree. Every checker and derived view is green.

---

## H. The live-proof specs

Every load 20 s or more apart, inside the session's 40; the live-session flag
up and the attach check passed first; nothing any step returns is written to a
tracked file.

### H.1 P A22 -- the Organization select, by A21's pattern (session 6)

- READ FIRST (1 load, his editor): the select's current option. If it reads
  his one entry, the test value is "Please select" (no company in the intro);
  if it already reads "Please select", the test value is the entry and the
  restore is "Please select". Either way the original is read, never assumed.
- THE ACT (about 4 loads, as session 6 measured per edit):
  `linkedin_update_profile_field(field="Organization", value=<the test
  value>)`: the preview names the field and the value; on confirm, his "Share
  key profile updates" setting read OFF, the editor, the choice, Save only if
  no other field moved, the fresh render reading the test value.
- THE INVERSE (about 4 loads): the receipt's own `to_put_it_back` -- the same
  tool with the exact original option text -- previewed and confirmed; the
  fresh render must read the original.
- OPTIONAL (1 load): a read-only re-read of the editor.
- BUDGET: 9 loads, 0 searches.
- STOP-ALL: the sharing setting reads anything but OFF (nothing is written);
  the inverse's fresh render does not read the original (his intro would show
  no company: the orchestrator is told at once, no other step runs); a wall
  or a challenge.
- THE BAR: both writes SAVED and verified on a fresh render, the select back
  at its original, no other field moved -- COVERED-PROVEN.

### H.2 P L8 -- the analytics hub

- 1 load: `linkedin_analytics_hub()`, one navigation to `/dashboard/`.
- A read: no inverse, no press.
- STOP-ALL: a landing at any other address; a wall or a challenge;
  `cards_seen` 0 (the page changed shape: stop and capture).
- THE BAR: `readable` true and `cards_parsed` at least 1, each metric's value
  an integer -- COVERED-PROVEN. Record integers and closed words only.

### H.3 P L1 -- the audience page

- 1 load: `linkedin_audience_analytics()`, one navigation to
  `/analytics/creator/audience/`.
- A read: no inverse, no press, no scroll.
- STOP-ALL: a landing at any other address; a wall or a challenge; zero
  dimensions drawn (`navs_matched` not 1).
- THE BAR: `readable` true, `total_followers` an integer, the dimensions
  within LinkedIn's six -- COVERED-PROVEN. Record integers, closed words and,
  for labels, only how many came back redacted or opaque and their lengths --
  never a label: they are other people's attributes.

SESSION TOTAL for the three moved rows: 11 loads (9 + 1 + 1), 0 searches.

---

## I. Gates run

LOCAL, targeted, serial (`-p no:randomly`, never `-n`); the live-session
flag was absent at every run; the full suite only on CI.

    gate                                                        result
    tests/test_the_intro_editor_draws_his_organization_select   red (1 failed, 4 passed), then
                                                                1 failed (the control's
                                                                expectation), then 7 passed
    tests/test_no_committed_identity.py,                        1150 passed (3 min: over the
      test_fixtures_hold_only_synthetic_people.py (after b693d54)  2-minute cap, the mandated
                                                                  post-commit check)
    tests/test_a_literal_repeats_no_member.py,                  1097 passed
      test_no_committed_identity.py (after d1d2881)
    scripts/census_completion.py                                every headline figure matches
                                                                its pin (after each census edit
                                                                and after the merge of master)
    check_next_step, check_write_classes, check_read_addresses, GREEN
      check_jobs_directions, ruling_holds
    build_audit_index, build_blocker_map, build_rulings_index   regenerated; --check clean
    pre-commit identity gate                                    ARMED: 226 spellings, 0 hits,
                                                                every commit
    surface guards after the hub's merge (server_surface,       343 passed (7 min 25 s: over the
      every_tool, tool_surface_pinned, other_two_count_claims,    cap; these files read the whole
      prose_that_makes_a_claim, analytics_hub, the harness)       registry)
    the same after the audience's merge, with audience_analytics GREEN (exit 0)
    census checkers after L8 and L1                             all GREEN; every figure matches
                                                                its pin

ON CI (`scripts/lane_ci.py`): run `38047037803` on `1d4c483` FAILED on two of
this lane's own -- the new `live7` directory uncounted, and the census
paragraphs' citation beside older correction words -- each fixed in `dbb18b0`
(2 failed, 5341 passed). Run `38048024843` on `d67d6c3` (A22, the census
step, master `2b165fd` merged): SUCCESS, 6 jobs, 5 min 56 s. The certifying
run over the merged children is the one named in the lane's final message.

---

## J. Instruments

Registered in `_audit/INSTRUMENTS.md`, section 89: the live7 builder's
`--check`, the A22 drive and its control, the dashboard builder's `--check`
and the reader's seven mutations, the audience builder's `--verify` and
`--check` and its four weakenings -- each shown failing. The lead's scratch
probes are declared disposable there.

---

## K. Questions for the orchestrator

1. MEASURED-ABSENT FOR `A14`, `A15` AND `K8`? Ground: A14's own cell, "if C1
   finds none, this row's candidate state is MEASURED-ABSENT for this
   account"; K8's, "the next holder of the signed-in profile can settle it in
   one re-read"; the state's definition, "no tool, and a LIVE READING of the
   surface says LinkedIn does not draw the thing". Session 7's editor and
   session 8's profile are live readings, and both read zero (A.1, A.2). This
   lane's brief moves rows only to COVERED-UNFIRED, so it did not move them.
2. CAPTURE C-B1a (F.1): typing into his own editor field WITHOUT Save, to
   capture the entry list, is an act no shipped tool makes. It is the one
   measurement behind `A11`, `A13`, `A17` and `S8`'s add half. Sanction it?
3. `F1`: admit `/in/me/details/recommendations/` (the `/in/me/` form only)?
   The first render never draws the section (A.2).
4. `L1`'s residual (E): `census_redact_rare`'s contract lets a label that is
   exactly one capitalised word survive, so an employer under "Company" can
   come back verbatim at runtime. A stricter rule for demographics labels is
   a ruling, not a reader change.
5. `L2b` (C): both halves -- counts and people records -- are committed on
   the child's branch, unreviewed and unmerged. The next lane
   reviews and merges them, then moves the row.
6. Children ran as general-purpose agents, per the standing rules, not
   `implementer` (the operator's model pin).
