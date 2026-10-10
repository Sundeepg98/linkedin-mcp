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

RED FIRST: (RUN PENDING -- filled at the commit)

---

## C. P L2b -- child lb1-followers

(filled at merge)

## D. P L8 -- child lb1-dashboard

(filled at merge)

## E. P L1 -- child lb1-audience

(filled at merge)

---

## F. The rows left GAP, each with its exact reason

(filled with the census edit)

---

## G. The census moves and the pins

(filled with the census edit)

---

## H. The live-proof specs

(filled at the end)

---

## I. Gates run

(filled as run)

---

## J. Instruments

(INSTRUMENTS.md section 89, filled at the end)

---

## K. Questions for the orchestrator

(filled at the end)
