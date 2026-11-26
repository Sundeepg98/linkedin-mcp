# Live session 12 -- the plan, written offline: 37 loads, 5 searches, 113 rows

Lane s12-prep, 2026-11-26, on the orchestrator's brief of that afternoon and
its answers of the same evening (round 2). Branch `s12-prep`, base master at
`3c656df` (integration 4, certified).

**OFFLINE PLAN. Zero LinkedIn page loads, no browser started or attached,
port 9224 untouched, the live-session flag never raised.** The session runs
only on the orchestrator's GO; its record is a separate document.

**Every person is named by ROLE. No name, slug, member id, thread id, group
id, organisation, newsletter, keyword value or absolute path is written
here.** Evidence classes: VERIFIED = measured by an instrument this lane ran
(named in section 11), or read in the code named; DERIVED = follows from
verified facts by the step stated; MEASURED (a load count) = a past live
session spent exactly that on the same address or shape, cited; ESTIMATED =
never loaded live; UNVERIFIED = not checked here.

**Inputs read:** the lane standing rules (gitignored); the campaign plan of
2026-11-25 (kept outside this repository); session 11's record
(_audit/2026-11-25-live-session-11.md, its section "To session 12");
_audit/_census/capture-queue.tsv and next-step.tsv at the base;
_audit/2026-11-26-integration-4.md; the readers-msg26, readers-jobs26,
readers-net26, selfprofile26, admit5-26 and search-fix26 records; the
orchestrator's merge notes (outside this repository), every 2026-11-26 entry
from 01:20 to 16:20; and lane infra26's branch as it stood that evening (its
people gate and navigation ceiling commits, and its record's hand-off
section, not yet merged).

---

## Round 2: the orchestrator's answers, and what they changed

Round 1 (this branch's first commit, certified by lane CI run 45816638923)
put five calls to the orchestrator, and named one open question of his. The
orchestrator answered all six, the last as BUDGET-ONE-ACCOUNT-40, his to
override. Applied here:

| # | the call | the answer | applied |
|---|---|---|---|
| 1 | 18 disk lines beyond the brief's list | KEEP, by rows per load | unchanged |
| 2 | the fifth search | `search-people-labels` (8 rows) takes it; the inbox-search capture-first moves to session 13's standby | the people search planned (E7); the messaging line to "13, standby" (below) |
| 3 | C-B1a left out | agreed; editor typeahead goes to a session he attends | unchanged |
| 4 | the newsletter value | agreed: the lane picks one from his own subscriptions, published by LinkedIn or an organisation, never a person | the line's plan cell now says so |
| 5 | msg-thread-footer's session cell | it needs a conversation he names: L2 | the cell now reads "L2, once he names it" |
| 6 | the budget question, his to answer | BUDGET-ONE-ACCOUNT-40: his account gets ONE budget of 40 page loads per 12 hours, shared by the live lane and the job pipeline (the stricter reading of his 2026-09-23 words), recorded in the pipeline's pinned ledger before each load | section 6's ledger hand-off and its READY check; no longer asked of him (section 7) |

**One reading of mine in applying answer 2.** The inbox search and the
archived row's restore item (M M34 and M M28) are ONE queue line behind ONE
receipt guard, and a session cell is per line. Kept alone, M M28 would cost
the guard's three loads for one row, below every standby line, and session 13
would pay the guard again for M M34. So the whole line moved to session 13's
standby, where both rows share one guard. Kept in session 12 instead, it is 3
loads for 1 row and puts his inbox read back among the asks; say the word.

**And two facts from lane infra26's branch** (VERIFIED by reading it):
PEOPLE-GATE v2 is `scripts/people_gate.py` (section 6 names the exact
lines), and the navigation ceiling is armed per MCP tool call by middleware,
so the runner's own loads are not counted. The risk round 1 recorded, a
ceiling counting the runner's own loads as one call, is resolved (section 6).

**What moved:** loads 37 planned (5 conditional) -> 37 planned (2
conditional); searches 5 (2 conditional) -> 5 (1 conditional); GAP rows on
the planned lines 105 -> **113**; standby 12 lines, 19 rows -> 10 lines, 10
rows; his inbox read is no longer needed (VERIFIED by the packer, section
11). The two standby lines that need no value off a reading moved into the
plan (E36, E37); `search-people-first-degree` joined the standby as the
claimant of a search the classic branch frees. Answer 6 moves no line: it
adds the pinned ledger to every load and a READY check that shrinks the
plan when the pipeline has already spent part of the 12-hour window.

---

## 0. What disk said that the brief did not

1. **Two of the brief's bullets are one set.** "The 23 rows admit5-26 moved
   to CAPTURE" and "the five queue lines integration 4 unblocked" are the
   same five lines, the ones whose session cell read "after admit5-26's
   merge": the recommendations page (13 rows), the newsletter page (5),
   verifications (2), volunteering (1) and the self-profile variant (2) = 23
   rows (VERIFIED: a script over the queue and the ledger; every row's next
   step names its line).
2. **More is unblocked than the brief names.** Thirteen lines admit26
   admitted (merged in integration 3) still read "after admit26's merge";
   six lane-A lines beyond the four the brief names still read "after lane
   A's merge" and serve; and ten lines labelled for sessions 9 or 11 or "the
   next live session" were never run or not captured, among them the three
   own-post lines readers-msg26 re-aimed offline (section 8.4 of its record).
   Every one is ADMITTED: `readonly.is_read_url` re-driven over all 87 queue
   addresses on this tree reads **0 disagreements** with the queue's verdict
   column (VERIFIED). The cut takes them by rows per load (section 3).
3. **The All-filters button is drawn, outside `main`.** On all three search
   skeletons of session 11 (the people search, the first-degree search, the
   content search), exactly ONE button's text is "All filters", and it sits
   outside the page's single `main` element (VERIFIED: a structure count
   over the tracked copies). Session 11's runner looked for it inside `main`
   and read 0 (its `one_named(page.locator("main"), ...)`; DERIVED). The same
   holds for the one button whose text is exactly "Join" on the non-member
   group page. So queue lines 2 and 9 are aimable again (the press is
   page-wide, exactly one visible), and C-MSG26-1's press must be aimed the
   same way.
4. **N 59 and N 60's question is already on disk.** Session 11's hashtag
   content search (load 33, tracked skeleton) draws 0 links into a hashtag
   feed and no element whose text is exactly "Follow" (VERIFIED, counted;
   "Follow" is a label the skeleton keeps, as the people search's shows). The
   plan re-reads it live at no cost (they ride C-MSG26-1's load, the keyword
   a hashtag); a reader lane may file the reading.
5. **J 31 and J 1 are not GAP rows** (absent from the next-step ledger,
   VERIFIED). C-SRCH-1's worth is the route decision for the rows proven on
   the classic search (RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE; the merge notes
   count 21 jobs rows plus J 31, UNVERIFIED here), and C-SRCH-0a/0b's is the
   zero state every job search refuses without (NO-RESULTS-STATE-CAPTURES).
6. **Session 11's photo press drew no dialog, confirmed offline.** The
   photo-open skeleton draws the same four `dialog` elements as the landing;
   its 13 editor links against the landing's 4 are the lower sections the
   page drew meanwhile (VERIFIED, counted; selfprofile26 counts 11 of them
   under the landed member, which agrees). The photo press is retried only
   on a BUTTON; a link stays vetoed (LINKS-ARE-NOT-DISCLOSURES).
7. **The runner keeps a raw page in exactly one place, and the harness in
   one more.** The rescued runner writes a raw page only in its `load()`
   (one `.html` write); the tracked harness writes one more through
   `_save_page(..., raw=True)`, in its settings step, which this plan never
   calls. Section 6 wires the gate into the first.

---

## 1. The session at a glance

| | |
|---|---|
| loads | **37 planned** (2 of them conditional) **+ 3 reserve = the ceiling of 40**; at least 20 s apart |
| searches | **5** (1 of them conditional), the cap |
| GAP rows on the planned lines | **113** distinct (111 unconditional, 2 on a conditional load), each row's next step naming its line (VERIFIED) |
| riders | **15** settings-queue rows on the privacy load (C-PRIVACY: 14 `SIBLING:lane-S` rows and M M39's switch reading) |
| not GAP | J 31 (C-SRCH-1), J 1 (C-SRCH-0a, C-SRCH-0b); the re-proof of M C41 (COVERED-PROVEN) |
| standby | 10 lines, 10 rows, plus N 51 (the Page half of line 95) -- run only on loads the plan frees |
| opens when | integration 5 has landed infra26's branch on master; the runner is READY (section 6); the pinned ledger shows 40 loads free in the trailing 12 hours, or the plan shrinks first (section 6); the dedicated Chrome is up |
| needs him | section 7: reachable for a checkpoint; the Open-to-Work capture only if he can watch |

Rows per planned load: 113 / 37 = 3.1 (DERIVED). By tier: the brief's lines
with the orchestrator's swap, 17 loads, 67 rows; the disk lines of 2 rows or
more a load, 10 loads, 36 rows; the brief's 1-row lines (Learning, premium
matches), 4 loads, 4 rows; 1-row disk lines, 6 loads, 6 rows (VERIFIED by the
packer). If the classic search no longer serves, E4 is skipped (it carries no
GAP row) and its load and search go to standby line 1.

---

## 2. The rules every load runs under

| rule | what it does here |
|---|---|
| LIVE-BUDGET-40-LOADS | at most 40 loads, serial, at least 20 s apart, one browser driver; a ceiling, not a target. The server's own default spacing is 20 s since integration 4 (pace20), and the runner still sets `LINKEDIN_MIN_INTERVAL_S=20` |
| BUDGET-ONE-ACCOUNT-40 (the orchestrator's, 2026-11-26; his to override) | ONE budget of 40 page loads per 12 hours for his account, shared by this session and the job pipeline, kept in the pipeline's ONE pinned ledger and recorded there before each load (section 6); whichever of it and the session's 40 is smaller binds |
| D1-SEARCH-AS-READS, FILTER-REQUERY-COUNTS-AS-A-SEARCH | at most 5 searches, every keyword from the runner's arguments and vetoed against the gitignored identity key; a filter panel is opened and read, never applied, so no re-query is spent |
| CAPTURE-PRESS-UNDER-PROBE-RULE, VIEW-SWITCH-PRESS-RESTORED | **disclosures only**: a menu, a folder, a filter panel, a list, opened, read and closed; a tab switched only when it is read before, restored and read after. Nothing typed into any box this session, nothing saved, sent, submitted, applied, scheduled or confirmed. The ruled cheap captures ride as ruled: ARTICLE-COMPOSER-ONE-CAPTURE, M-C18-EDITOR-OPENS-UNSAVED, L1-D3-MEDIA-CHOOSER-INTERCEPTED, OWN-PROFILE-SCROLL-SANCTIONED |
| SIGN-IN-CHALLENGES-ARE-HIS | any wall, checkpoint or challenge is STOP-ALL; he completes it himself |
| the browser | the dedicated persistent profile (the main checkout's gitignored `_state/chrome-profile`), started by `scripts/start_chrome.ps1`, CDP on 9224, ATTACH mode (`LINKEDIN_CDP_ATTACH=1`). Never his own Chrome: never attached to, fronted, typed into or closed |
| the flag | `_state/LIVE_SESSION_ON` in the main checkout, raised by the runner before load 1 and lowered at the close, only if it is this lane's |
| the job-pipeline guard (installed 2026-11-26 at user scope) | while the flag is up it DENIES every LinkedIn MCP tool but `server_info`, `cdp_status`, `logout` and `page_plugin_snippet`, in every session. The lane drives LinkedIn through its RUNNER only, calling the package's functions in-process, as session 11 did (0 LinkedIn MCP calls) |
| PEOPLE-GATE v2 | wired before load 1 (section 6); and the brief's rule: **any page that may show people is kept as a skeleton only**, whatever the gate reads |
| PAGE-MAY-VETO-NEVER-SUPPLY | every address is a constant, a package composer, or a template filled from a runner item; where a value comes off a reading (a urn, a skill id), the reading is written to gitignored state and the caller names it in the next run, as in session 11 |
| NAMES-AT-RUNTIME, PEOPLE-DATA-MITIGATIONS, NAME-BEARING-ADDRESS-REDACTION-SCOPE | names never leave the process; the runner prints closed words, booleans and counts; the newsletter address is never printed to the console or written to a tracked file |

---

## 3. The ordered load list

`E` is the order of execution. Every line is one `goto` by the runner's
design (the ledger counts gotos), so a count is ESTIMATED only in how the
page lands, except E1 and E5, whose loader retries an unread self assertion
once (the retry is paid from the reserve). `S` = skeleton only; `S+R` = the
raw page kept gitignored only if PEOPLE-GATE v2 keeps it (his own pages that
draw no other person). The rows are the queue's own `rows` cell.

| E | line (queue rank) | loads (run.) | srch | count | presses (nothing committed) | save | rows it unblocks |
|---|---|---|---|---|---|---|---|
| 1 | the re-proof: `linkedin_my_activity_items` | 1 (1) | 0 | ESTIMATED (the tool's own words: once, twice on a retry) | none | -- (the envelope reduced) | re-proves M C41; its item keys aim E9 |
| 2 | `C-SRCH-1` (116) | 1 (2) | 1 | MEASURED (the last classic load on record, 2026-09-28) | none | S | J 31 (not GAP): decides the route |
| 3 | `C-SRCH-0b` (119) | 1 (3) | 1 | MEASURED (s11 load 18, the AI page) | none; a nonsense token, letters only | S | J 1 (not GAP) |
| 4 | `C-SRCH-0a` (118), only if E2 shows classic serves | 1 (4) | 1 | MEASURED shape (as E2) | none; a nonsense token | S | J 1 (not GAP) |
| 5 | `in-me-profile` (3) | 1 (5) | 0 | MEASURED (s11 load 3) | the top card's opener (More or Resources) once; his photo only if exactly one BUTTON wraps it; Add custom button if exactly one is drawn; one scroll pass; the add-form links read, never pressed | S | N 76, P B3, P C8, P S4, P D11-P D23, P D26, P D29 (19) |
| 6 | `admit-in-me-details-recommendations` (23) | 1 (6) | 0 | ESTIMATED | the received and given tabs: the one not drawn pressed as a tab, read, the first pressed back, verified | S | N 121-N 123, N 125-N 128, P F1, P F5-P F9 (13) |
| 7 | `search-people-labels` (2) | 1 (7) | 1 | MEASURED (s11 load 31) | All filters, found page-wide (0.3), its panel read, Escape, nothing chosen; a generic role word | S | N 82, N 86, N 88-N 93 (8) |
| 8 | `C-MSG26-4` (130) + `article-composer` (1) | 1 (8) | 0 | MEASURED (s11 load 24) | ARTICLE-COMPOSER-ONE-CAPTURE: onboarding dismissed; the author toggle, Manage (its drafts link read for M C47), the embed control and Next, each read and closed; never Publish or Schedule | S | M C44, M C46, M C50, M C78, M C81, P L3; M C47 (7) |
| 9 | `own-post-reactions` (5) + `C-B3-2` (101) + `C-JMN-4` (107), his own post | 1 (9) | 0 | MEASURED (s11 load 30) | readers-msg26's aims: the post's own `Open reactions menu`; the comment sort trigger; the control menu (the card's first expandable button, scrolled into view) and its "Who can comment on this post?"; LAST, its Edit post, the editor opened and closed with nothing typed | S | M C33, M C35b, M C18, M C23, M C90, M C29 (6) |
| 10 | `admit-mynetwork` (27) | 1 (10) | 0 | ESTIMATED | none; the invitation badge read before and after | S | N 22, N 32, N 62, N 97, N 98, N 110 (6) |
| 11 | `C-RJ26-3` (122) | 1 (11) | 0 | MEASURED (s11 load 11) | one resume card's options menu, read, Escape | S+R | J 71, J 72, P M1, P M3, P M4 (5) |
| 12 | `admit-newsletters-id` (32) | 1 (12) | 0 | ESTIMATED | none; its subscribe and share controls read | S | M C101, M C80, M C82, N 55, N 56 (5) |
| 13 | `admit-mypreferences-d-categories-privacy` (28) + C-PRIVACY | 1 (13) | 0 | ESTIMATED | none; no toggle pressed | S+R | J 87, N 143, N 96, P O22, P P3 (5); riders: 14 lane-S rows and M M39's switch |
| 14 | `admit-in-me-edit-contact-info` (30) | 1 (14) | 0 | ESTIMATED | none; labels and states, nothing typed | S+R | P A26, P A27, P A28, P A29 (4) |
| 15 | `admit-in-me-edit-forms-position-new` (31) | 1 (15) | 0 | ESTIMATED | none; labels and states, nothing typed | S+R | P D5, P D6, P D8, P D9 (4) |
| 16 | `C-MSG26-1` (128) + `admit-search-results-content` (93) | 1 (16) | 1 | MEASURED (s11 load 33) | All filters, found page-wide (0.3), its panel read for a group facet, Escape, nothing chosen; a generic technology hashtag | S | M C70; N 59, N 60 (3) |
| 17 | `connections-sort-and-filters` (109) | 1 (17) | 0 | ESTIMATED | the sort control and the Talks-about and Open-to filters, each opened, read, closed; none applied | S | N 24, N 27, N 28 (3) |
| 18 | `admit-in-me-isselfprofile-true` (117), its first load | 1 (18) | 0 | ESTIMATED | none; the landing must be proven his by the shipped self rule, or the read refuses | S | P D25 |
| 19 | the same line, its second load: the contact-info overlay | 1 (19) | 0 | MEASURED (session 1: it redirected to his profile) | none; labels only, no contact value saved or printed | S+R | P A25 |
| 20 | `admit-mypreferences-d-verifications` (46) | 1 (20) | 0 | ESTIMATED | none; the two-step verification entry never followed | S+R | P K1, P K7 (2) |
| 21 | `feed-menus` (7) | 1 (21) | 0 | MEASURED (s11 load 28) | the left rail's Saved items link read, not followed; up to three members' item menus opened and closed, each read for Unfollow (a followed author) | S | M C36, M C37 (2) |
| 22 | `feed-item-permalink-menu` (95), the member half, only if E21 drew a followed author's post | 1 (22) | 0 | MEASURED (s11 load 29) | that post's own control menu, opened and closed | S | N 37, N 43 (2) |
| 23 | `admit-in-me-details-skills-edit-forms-1` (40) | 1 (23) | 0 | ESTIMATED | none; the skill id off E5's reading, named by the caller | S+R | P E2, P E3 (2) |
| 24 | `admit-jobs-preferences-viewtype-seeking-preferences` (73) | 1 (24) | 0 | ESTIMATED | none; labels and states | S+R | P I12, P I13 (2) |
| 25 | `C-RJ26-1` (120) | 1 (25) | 0 | MEASURED (s11 load 19) | the job-openings card's Functions dropdown, read, Escape | S | J 169 |
| 26 | `C-RJ26-2` (121) | 1 (26) | 0 | MEASURED shape (s11 load 23) | none | S | J 111 |
| 27 | `admit-in-me-opportunities-volunteering-education` (69) | 1 (27) | 0 | ESTIMATED | none; the bare spelling (VOLUNTEERING-BARE-SPELLING-FIRST), the landing recorded | S+R | P D24 |
| 28 | `admit-learning` (77) | 1 (28) | 0 | ESTIMATED | none | S | J 152 |
| 29 | `admit-learning-career-journey` (78) | 1 (29) | 0 | ESTIMATED | none | S | J 156 |
| 30 | `admit-learning-me-my-library` (81) | 1 (30) | 0 | ESTIMATED | none | S | J 154 |
| 31 | `admit-premium-matches` (88) | 1 (31) | 0 | ESTIMATED | none | S | N 199 |
| 32 | `U-POST-DOCUMENT` (129) | 1 (32) | 0 | MEASURED (s11 load 25, the same composer) | More opened and read; the document control with the file chooser intercepted, never answered; Escape | S | M C5 |
| 33 | `admit-mynetwork-invitation-manager` (26) | 1 (33) | 0 | MEASURED (s11 load 14) | none; the type pills' words read against the closed type words | S | N 14 |
| 34 | `admit-in-me-edit-forms-summary-new` (64) | 1 (34) | 0 | ESTIMATED | none; nothing typed | S+R | P D2 |
| 35 | `admit-in-me-edit-secondary-language` (67) | 1 (35) | 0 | ESTIMATED | none; nothing typed | S+R | P D27 |
| 36 | `admit-in-me-opportunities-services-education` (68) | 1 (36) | 0 | ESTIMATED | none; the capture stops at the first control into the Open-to flow | S+R | P H1 |
| 37 | `admit-mynetwork-network-manager-people-follow-following` (83) | 1 (37) | 0 | MEASURED (s11 load 16) | none; the network manager's own nav read for followed hashtags | S | N 61 |
| -- | reserve | 3 (40) | -- | -- | the loader's retry (E1, E5); a press that loads a document, counted by hand; D-4's fallback (his experience list) | -- | -- |

**Totals: 37 loads, 5 searches, 113 GAP rows** (VERIFIED by the packer:
every row on its line, none twice, each row's ledger next step naming the
line). If classic no longer serves, E4 is skipped: 36 loads, 4 searches, the
same 113 rows, and the freed load and search go to standby line 1.

**Why this order.** The re-proof first, because every line anchored on his
own profile (E5, E18, E19) rests on the rule it re-proves. The route decision
(C-SRCH-1) before anything else that serves the job search, as session 11
handed over. His own profile (E5) before the first S+R line, because it is the
page that teaches the people gate who he is (section 6). Then rows per load,
falling, with each dependency kept: E5 before E23 (the skill id), E25 and E26
(the D-4 clearance); E1 before E9 (his own post); E21 before E22.

**The values each read takes** (L1-D4-NEUTRAL-READ-VALUES; runner items,
vetoed by the identity key, never in a tracked file):

* C-SRCH-1: generic role words; C-SRCH-0a/0b: a nonsense token, letters
  only, naming no person; E7: a generic role word; E16: a generic technology
  hashtag.
* C-RJ26-1: the large organisation session 11 cleared (its insights page is
  known to draw the dropdown); C-RJ26-2: a second large organisation whose
  Page draws a Products tab. Both are cleared again on E5 against his own
  experience entries the scroll pass draws (by id, by name slug, by name;
  booleans only). If the scroll draws none, his experience list costs one
  reserve load, as session 11's E2 did. Each company phase stops if its
  first tab does not name the organisation.
* E9: his own post, the kept authorship-established one session 11 used
  (session 2's post with comments), and it must also be among E1's fresh
  item keys, or E9 is not loaded.
* E12: ONE newsletter his own subscriptions page already draws (a kept
  reading, gitignored), published by LinkedIn or by an organisation's Page,
  never by a person, chosen by the lane at runtime (the orchestrator's
  answer 4).
* E23: one skill id his profile's skills section draws on E5, written to
  gitignored state and passed by the caller; if none is drawn, E23 is not
  loaded and the load returns to standby.
* E22: the first item on E21 whose own menu draws Unfollow; its urn is
  written to gitignored state and passed by the caller.

**Inside E5, read before GO at zero loads** (the line's own condition, "after
an offline read of its session-11 skeleton"): the photo control's shape on
the kept keyed skeleton (a button or a link), and the hydrated skeleton's nine
three-segment editor routes matched under session 11's shape key against the
closed list of section words (selfprofile26's method). A matched spelling is
that P D row's drawn address before the load; the load reads only what
remains, and the variant on E18 reads the Add-section surface for the rest.

---

## 4. The fill order and the shed order

**Standby, in order**, run only on a load the plan frees (a conditional line
skipped, the reserve untouched at the end) and only while the ledger has
room:

| # | line (rank) | loads | rows | note |
|---|---|---|---|---|
| 1 | `search-people-first-degree` (9) | 1 | N 26b | **needs a free search** (E4 skipped); its pills by name page-wide, else All filters page-wide (0.3) |
| 2 | `admit-in-me-skill-insights-skill` (71) | 1 | P S3 | a skill index off E5's reading |
| 3 | `admit-mypreferences-d-premium-manage-account` (85) | 1 | P N22 | skeleton only: a billing page (section 8) |
| 4 | `admit-products-product` (89) | 1 | J 166 | LinkedIn's own product page |
| 5 | `admit-showcase-showcase` (94) | 1 | J 167 | LinkedIn's own showcase page |
| 6 | `C-P26-1` (102) | 1 | P S8 | Show all on his key skills, Escape |
| 7 | `C-JMN-2` (105) | 1 | J 56 | the Date posted pill, read, Escape |
| 8 | `comments-metric-spelling` (110) | 1 | M C39 | the metric selector read |
| 9 | `creator-hub-on-the-dashboard` (111) | 1 | P L7 | |
| 10 | `C-I3-1` (115) | 1 | M C97 | loading notifications clears his unread badge (NOTIFICATIONS-UNREAD-SPEND) |
| -- | `feed-item-permalink-menu` (95), the Page half | 1 | N 51 | only if E21's feed drew a Page post |

**Shed, from the bottom of section 3, if a load is needed beyond the plan**
(a retry, a document load counted by hand, an anomaly re-read the lead
orders): E37 to E32 (the 1-row disk lines), then E31 to E28 (the brief's "if
they still fit" lines), then upward. Each costs its line's rows.

---

## 5. STOP rules

**STOP-ALL, his to clear or the lead's to read; the session ends, the flag
is lowered, Chrome is left serving:**

* any sign-in wall, checkpoint or challenge, on any page (the harness's
  health check after every load);
* a failed restore: the recommendations tab, any sort, filter or tab not
  back on the state read before it;
* any publishing control met in the article composer, any autosave sign in
  an editor, or a save, send, submit, apply or confirm drawn as pressed;
* the post editor on E9 not closing to the post as it was;
* the flag not this lane's, a second client on 9224, or anything touching
  his own Chrome.

**The phase stops, and the lead reads before more is spent:** an error
envelope; an exception; a menu or dialog that does not close by its own
evidence (instrument 103); a press that loads a document (counted into the
ledger by hand); a landing that is not the address asked where the address
is a target (his profile variant not proven his; an organisation's first tab
not naming it); `people_gate.judge` raising (it fails closed by design: a
page it cannot read is withheld, and the skeleton is always kept).

**The re-proof decides a block.** If E1 refuses his own profile, the lines
anchored on the self rule (E5's presses, E18, E19) are skipped and the lead
is told at once; the rest of the plan runs.

**No conversation is opened this session.** The messaging line moved to
session 13 (round 2), so `/messaging/` is not loaded and no receipt guard
runs; nothing can be marked read.

**Refused before navigating** (the ledgers' own refusals): a load the
pinned account ledger refuses (section 6: a spacing refusal waits the seconds
it names, once; a budget refusal sheds from the bottom of the plan and never
waits); a 41st load; a 6th search; a phase whose most loads would pass 40;
an address `readonly.is_read_url` refuses; a keyword item the identity key
vetoes. A pinned ledger that cannot be read refuses every load (fail
closed).

---

## 6. The runner hand-off

**WHERE IT LIVES.** The main checkout's gitignored `_state/live-runner/s12/`,
copied from the rescued `_state/live-runner/s11/` (the orchestrator's copy of
2026-11-26 14:27; `runner_s11.py` byte-identical to session 11's). **Never
OS temp**: sessions 3 to 10 lost their runners there. The session's own
state is the live lane's worktree `_state/live12/` (the harness keys its
state to the checkout it is imported from), and at the close it is copied
to the main checkout's gitignored `_state/preserved/live12-<date>/` BEFORE
any worktree is retired, as the orchestrator did for session 11. The kept
readings it vetoes against are read only: the previous live lane's state
(his authorship-established rail) and the preserved session-11 set.

**WHAT CHANGES FROM SESSION 11'S RUNNER:**

1. the lane name, `LIVE_LANE_SESSION_DIR=live12`, and its import root: the
   live lane's worktree at the certified master that carries infra26's
   branch (integration 5);
2. the self stand-in goes: session 11 asserted his profile by the redirect
   plus owner-only words because the url marker was gone; selfprofile26's
   rule is on master, so E5 lands through the shipped loader
   (`server._goto_self_profile_asserted`, which E1's tool also uses) and
   prints which signal answered, and his slug for `self.json` comes off that
   proven landing;
3. PEOPLE-GATE v2 (below);
4. the search triggers are found page-wide (0.3);
5. the new phases of section 3, each refusing unless the flag stands and is
   this lane's, the pinned account ledger and the session's own ledger both
   have room for its most loads, the driver lock is free and the attach
   environment is set, all before any browser contact;
6. every load recorded in the pinned account ledger before it is made
   (below).

**PEOPLE-GATE v2: THE EXACT HAND-OFF.**

* **The module:** `scripts/people_gate.py`, lane infra26's (the six rules of
  the orchestrator's 14:05 entry as R1 to R6, plus v1's member links as L1
  and PEOPLE-GATE-COUNTS-NAME-SLOTS as N1; the defect it closes is
  INSTRUMENTS 107.5). It lands on master in integration 5. The runner
  IMPORTS it from its worktree's `scripts/`, which it already puts on
  `sys.path`, so the code that gates is the code CI certified; nobody copies
  it into gitignored state.
* **The entry point:** `people_gate.judge(html, *, slug, page_url, page_key,
  own_cache)` returns a `Verdict`: `keep_raw` true only on "keep-raw";
  `counts` per rule; `reasons` as closed sentences with counts, never a
  value; and `covers(text)`, true only for the exact string judged (R6). His
  own identity is learned at runtime and held as digests only in
  `own_cache`, the module's one write.
* **The lines, in `runner_s12.py`** (infra26's hand-off gives the import and
  a one-line form of the other two; split as below, every page is judged, so
  skeleton-only pages teach the cache too):
  1. `import people_gate`, after the `BROWSER` import;
  2. in `load()`, right after `html = await page.content()`, on EVERY page,
     S lines included: `verdict = people_gate.judge(html, slug=_self_slug(),
     page_url=landed, page_key=key, own_cache=h.STATE /
     "people_gate_own.json")`;
  3. `raw = s_plus_r and others == 0 and verdict.keep_raw and
     verdict.covers(html)` replaces `raw = s_plus_r and others == 0`, so the
     string judged is the string written, and v1's live count stays as a
     further condition. The line after it prints the verdict's counts.
* **Why every page is judged:** infra26 measured that server-driven pages
  cannot teach his identity, so until a page carrying his own entity has
  been judged, every raw is withheld (fail closed). E5, his own profile, is
  judged first among his pages for that reason: its verdict keeps no raw
  (an S line), but it teaches the cache before E11, the first S+R line. If it
  teaches nothing, every S+R raw is withheld, the skeletons still serve, and
  the record says which page taught the cache.
* **Shown failing before READY** (red first, in the runner's offline checks,
  on synthetic pages, no LinkedIn load): each rule planted alone on a page
  of his own withholds the raw page; a clean page of his own keeps it once
  the cache is taught; a string other than the one judged fails `covers`;
  the 35 checks session 11 left are re-run green.
* **Pinned at READY and at GO:** the master sha, the module's sha256, the
  runner's sha256.

**THE NAVIGATION CEILING IS NOT THE RUNNER'S (round 1's ceiling risk,
resolved).** On infra26's branch (VERIFIED by reading it):
`call_ceiling.PerCallCeiling`, a middleware, arms a three-load budget around
every MCP tool call; `LinkedInBrowser.goto` counts each load against it
through `call_ceiling.count_load` (named `spend` on infra26's branch when
this plan read it, renamed by that lane before its certified head), which
does nothing when no budget is armed; and the
browser module's own words say that outside a tool call, for the live
lane's runner and the probes, nothing is counted. The runner calls the
package in-process, never through MCP (the job-pipeline guard denies MCP
while the flag stands), so its phases of 5 to 7 loads are bounded by the
pinned ledger and the session's own limits only. No ceiling check is owed.

**THE ACCOUNT BUDGET IS THE PINNED LEDGER (BUDGET-ONE-ACCOUNT-40).** One
budget of 40 page loads per 12 hours covers his account, shared by this
session and the job pipeline, and it lives in ONE place: the job pipeline's
pinned store, whose path is in the user-scope job-pipeline skill's
`hooks/store_pin.json`. The runner never copies the store and never keeps a
second account count. The public contract, read in the skill's
`jobpipe/budget.py` and `jobpipe/track.py` (VERIFIED by reading them):

* `track.read_pin()` gives the pinned store's path and `track.Store(path)`
  opens it, with `lock()` and an `append()` that stamps the time and syncs
  to disk. No pin, or a pin or store that cannot be read, and the session does
  not start (fail closed).
* **Before every load**, at the site where the harness already counts loads
  (a wrapper around `BROWSER.goto`, so a shipped tool's own loads, E1's
  included, are recorded too), under the store's lock:
  `budget.call_refusal(store.events(), "live_census", None, 1, now)`, with
  `now` in UTC. On None, the runner appends one call record in the store's
  own vocabulary (the event the pipeline's hook writes for a LinkedIn call,
  platform `linkedin`, `loads` 1: the shape `budget.load_record` counts as one
  call), and only then makes the load. On a refusal it makes no load: a
  spacing refusal waits the seconds its sentence names, once, then asks
  again; a budget refusal sheds from the bottom of the plan (section 4) and
  never waits for the window to roll.
* The harness's own session file keeps only what the store does not: the
  5-search cap, the driver lock and the per-session 40. It can only refuse
  more than the store, and never grants a load the store refuses.
* While the flag stands, the pipeline's own guard denies every LinkedIn MCP
  call, so nothing else spends the window during the session; what the store
  held before GO is what the READY check reads.

**THE READY CHECK THE BUDGET ADDS, at GO:** `budget.usage(store)` gives the
LinkedIn page loads on record in the trailing 12 hours, and the plan needs 40
free (37 planned and 3 in reserve). With fewer free, the plan shrinks from
the bottom of the rank (section 4's shed order) to the free count less the 3
in reserve, and the session starts at once: it does not wait for the window.
With 3 or fewer free there is no session, and the lead is told.

**READY means:** the runner copy in place and pinned; v2 wired and its red
checks shown; the pinned ledger read and its trailing-12-hour count taken;
`os_check` reading 9224 down or held only by the dedicated profile; the
plan's items prepared (the values of section 3, each vetoed by the identity
key).

---

## 7. What needs him before GO

1. **Reachable for a checkpoint.** No presence otherwise, and no inbox read:
   nothing in this session opens a conversation (the messaging line moved to
   session 13 in round 2).
2. **Optional, only if he can watch:** the Open-to-Work editor capture
   (queue line 24, OPEN-TO-WORK-EDITOR-ATTENDED-ONLY): 1 load, 11 rows, the
   modal read and closed with nothing chosen. It replaces E37 if he says yes.

The budget question is answered (BUDGET-ONE-ACCOUNT-40, his to override);
what it asks of the session is section 6's READY check, not of him.

**What he should know, none of it outward:** nothing is sent, followed,
reacted to, applied for or saved, and no other member's profile is opened.
Loading his invitation manager (E33) clears his pending-invitation badge, and
`/mynetwork/` (E10) may (RECEIVED-BADGE-IS-THE-READS-COST). The article
composer (E8) may leave an empty draft of his own; if it does, the record
says so, and deleting it is his or a later build's.

---

## 8. The calls this plan makes on its own (each reversible)

1. **The riders**: M C47 on C-MSG26-4's load; N 59 and N 60 on C-MSG26-1's;
   C-B3-2 and C-JMN-4 on own-post-reactions' load, as L1-D1-RIDERS-RIDE took
   them in session 11 and C-JMN-4's own cell proposes.
2. **Skeleton only on every page that may show people**, stricter than the
   queue's S+R on the Learning pages, premium matches, his network pages and
   his profile (the brief's rule); and skeleton only on his billing page
   (standby 3), whose raw would carry payment details and whose labels the
   skeleton keeps.
3. **The messaging line moved whole** to session 13's standby (round 2,
   above).
4. **The classic branch's freed search** goes to `search-people-first-degree`
   (standby 1), the next line that needs a search, by rows per load.

---

## 9. Not scheduled, and why

| lines | why |
|---|---|
| every `t-named-*` line; msg-thread-footer (11: L2, the orchestrator's answer 5); C-B5-1, C-B5-2, C-B5-3 (96-98: groups he names; L1-D2's choice bound session 11 only); C-JMN-1 (104: a job he archives by hand); C-JMN-3 (106); t-named-search-card (108); C-J68-1 to -3 (112-114) | operator-named targets: L2 and L3 |
| `messaging-guarded` (6) | session 13's standby (answer 2), both rows behind one receipt guard |
| `admit-in-me-opportunities-job-opportunities-edit` (24); C-B1a (103) | a session he attends (section 7, item 3; answer 3) |
| `admit-in-me-details-featured` (34) | no address serves (session 11: it lands on his profile root) |
| `admit-jobs-search-results-keywords` (43) | captured; its offline build is next |
| `sessions-surface` (10), the five ads-settings pages (123-127), the AI-generating loads (29, 70, 86, 87), `admit-pulse-article` (38), `admit-resume-builder` (91) | each address refused today, or waiting on its ruling |

---

## 10. Census edits

**Only keyed cells of the capture queue, each old value asserted before the
write, no other cell and no reflow** (VERIFIED by a diff of every column
after each write):

* round 1, `session` cells: to `12`, lines 1, 5, 7, 23, 26, 27, 28, 30, 31,
  32, 40, 46, 64, 67, 69, 73, 77, 78, 81, 88, 93, 95, 101, 107, 109, 117;
  to `12, standby`, lines 2, 68, 71, 83, 85, 89, 94, 102, 105, 110, 111, 115;
* round 2, `session` cells: line 2 and lines 68 and 83 to `12`; line 9 to
  `12, standby`; line 6 to `13, standby`; line 11 to `L2, once he names it`;
* round 2, line 32's `plan` cell: "a newsletter he names" now reads as the
  orchestrator answered (one newsletter the lane picks at runtime from his
  own subscriptions, published by LinkedIn or by an organisation and never by
  a person).

Unchanged because they already read 12: lines 3, 116, 118-122, 128-130. No
row moved: a capture moves no census row by itself, and neither a session
cell nor a plan cell is a state.

---

## 11. Instruments (all DISPOSABLE)

The lane's scratch, in the main checkout's gitignored state: a queue
printer and full-cell reader; a row cross-check against the ledger; the
verdict re-driver (`readonly.is_read_url` over every queue address, 0
disagreements); a button census over the tracked skeletons; the
`main`-ancestry counter behind finding 0.3; the two keyed cell writers; and
the packer behind sections 1 and 3, which fails on a row assigned twice, a
row not on its line, or a row whose ledger next step names another line.
None was shown failing on a planted defect, so none enters INSTRUMENTS.

---

## 12. Gates

Run on the staged tree before each commit; the live-session flag absent at
every check.

| gate | result |
|---|---|
| `scripts/check_next_step.py` | GREEN: every GAP row once (513), every source and payload resolving, the queue agreeing (its verdicts re-driven through the boundary) |
| `scripts/census_completion.py --check` | every headline figure matches its pin; no pin moved, because no row moved |
| the three derived views | written twice to a fixed point, then checked clean |
| `scripts/check_cited_shas_resolve.py` | every cited SHA an ancestor of master |
| `scripts/check_asserted_names_resolve.py` | 1 asserted and absent, the site master already pins in its own test; none from this record |
| the guard files that read the queue or every audit document, one process each | round 1: eleven files, 186 passed, the slowest 85 s; round 2: the same eleven, 186 passed (ten side by side, the slowest 82 s; the recall guard alone in 74 s, after contention pushed its side-by-side run past the cap); and again with answer 6 folded in, 186 passed (the ten side by side, the slowest 66 s; the recall guard alone in 86 s) |
| `tests/test_a_cited_sha_resolves.py` | over the two-minute cap on its own (stopped at 115 s, nothing failed before the stop): left to lane CI; the script it wraps passed above |
| the identity gate | the pre-commit gate at each commit; the committed-blob test and lane CI after it, reported by head sha in the lane's report to the orchestrator |

NOT RUN locally: the full suite (lane CI runs it on the lane's ci/ ref).
