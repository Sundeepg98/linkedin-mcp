# Live session 12 -- the plan, written offline: 37 loads, 5 searches, 105 rows

Lane s12-prep, 2026-11-26, on the orchestrator's brief of that afternoon.
Branch `s12-prep`, base master at `3c656df` (integration 4, certified).

**OFFLINE PLAN. Zero LinkedIn page loads, no browser started or attached,
port 9224 untouched, the live-session flag never raised.** The session runs
only on the orchestrator's GO; its record is a separate document.

**Every person is named by ROLE. No name, slug, member id, thread id, group
id, organisation, newsletter, keyword value or absolute path is written
here.** Evidence classes: VERIFIED = measured by an instrument this lane ran
(named in section 11); DERIVED = follows from verified facts by the step
stated; MEASURED (a load count) = a past live session spent exactly that on
the same address or shape, cited; ESTIMATED = never loaded live; UNVERIFIED =
not checked here.

**Inputs read:** the lane standing rules (gitignored); the campaign plan of
2026-11-25 (kept outside this repository); session 11's record
(_audit/2026-11-25-live-session-11.md, its section "To session 12");
_audit/_census/capture-queue.tsv and next-step.tsv at the base;
_audit/2026-11-26-integration-4.md; the readers-msg26, readers-jobs26,
readers-net26, selfprofile26, admit5-26 and search-fix26 records; and the
orchestrator's merge notes (outside this repository), every 2026-11-26 entry
from 01:20 to 16:20.

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
   column (VERIFIED). By the brief's own criterion, rows per load, several
   outrank the brief's 1-row lines, so the cut takes them in that order
   (section 3): **18 lines beyond the brief's list are planned**
   (`U-POST-DOCUMENT`, already labelled 12, among them) **and 12 are on
   standby.**
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
   "Follow" is a label the skeleton keeps, as the people search's shows). The plan
   re-reads it live at no cost (they ride C-MSG26-1's load, the keyword a
   hashtag); a reader lane may file the reading.
5. **msg-thread-footer's session cell reads 12, but the line needs a
   conversation he names** (whose last message is the other member's). The
   brief puts operator-named targets in L2/L3, so it is not scheduled. Its
   cell is outside this plan's edit scope (the lines it schedules) and is
   left as it is.
6. **infra26's branch held no commit past the base when this was written**,
   so PEOPLE-GATE v2 is not yet a file. Section 6 names the hand-off as a
   contract, a call site and a READY check, not as a module path.
7. **The runner keeps a raw page in exactly one place, and the harness in
   one more.** The rescued runner writes a raw page only in its `load()`
   (one `.html` write); the tracked harness writes one more through
   `_save_page(..., raw=True)`, in its settings step. Both are in section 6.
8. **A risk in the queued navigation ceiling.** NAVIGATION-CEILING-MADE-TRUE
   (a per-call counter in `BrowserManager.goto`, a 4th load refused) is
   queued for the same infra lane. The runner calls `BROWSER.goto` itself,
   several loads inside one `BROWSER.session()` (its own-pages phase ran 7
   in session 11, VERIFIED by reading it). A counter that counts those as
   one call refuses the runner's 4th load. Section 6 makes it a READY check.
9. **J 31 and J 1 are not GAP rows** (absent from the next-step ledger,
   VERIFIED). C-SRCH-1's worth is the route decision for the rows proven on
   the classic search (RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE; the merge notes
   count 21 jobs rows plus J 31, UNVERIFIED here), and C-SRCH-0a/0b's is the
   zero state every job search refuses without (NO-RESULTS-STATE-CAPTURES).
10. **Session 11's photo press drew no dialog, confirmed offline.** The
    photo-open skeleton draws the same four `dialog` elements as the landing;
    its 13 editor links against the landing's 4 are the lower sections the
    page drew meanwhile (VERIFIED, counted; selfprofile26 counts 11 of them
    under the landed member, which agrees). The photo press is retried only
    on a BUTTON; a link stays vetoed (LINKS-ARE-NOT-DISCLOSURES).

---

## 1. The session at a glance

| | |
|---|---|
| loads | **37 planned** (5 of them conditional) **+ 3 reserve = the ceiling of 40**; at least 20 s apart |
| searches | **5** (2 of them conditional), the cap |
| GAP rows on the planned lines | **105** distinct (101 unconditional, 4 on conditional loads), each row's next step naming its line (VERIFIED) |
| riders | **15** settings-queue rows on the privacy load (C-PRIVACY: 14 `SIBLING:lane-S` rows and M M39's switch reading) |
| not GAP | J 31 (C-SRCH-1), J 1 (C-SRCH-0a, C-SRCH-0b); the re-proof of M C41 (COVERED-PROVEN) |
| standby | 12 lines, 19 rows, plus N 51 (the Page half of line 95) -- run only on loads the plan frees |
| opens when | integration 5 has landed PEOPLE-GATE v2 on master; the runner is READY (section 6); the dedicated Chrome is up; his inbox at 0 unread just before GO (for E1-E3 only) |
| needs him | section 7: one inbox read, one answer, reachable for a checkpoint |

Rows per planned load: 105 / 37 = 2.8 (DERIVED). By tier: the brief's lines
19 loads, 61 rows; the disk lines of 2 rows or more a load, 10 loads, 36
rows; the brief's 1-row lines (Learning, premium matches) 4 loads, 4 rows;
1-row disk lines 4 loads, 4 rows (VERIFIED by the packer).

---

## 2. The rules every load runs under

| rule | what it does here |
|---|---|
| LIVE-BUDGET-40-LOADS | at most 40 loads, serial, at least 20 s apart, one browser driver; a ceiling, not a target. The server's own default spacing is 20 s since integration 4 (pace20), and the runner still sets `LINKEDIN_MIN_INTERVAL_S=20` |
| D1-SEARCH-AS-READS, FILTER-REQUERY-COUNTS-AS-A-SEARCH | at most 5 searches, every keyword from the runner's arguments and vetoed against the gitignored identity key; a filter panel is opened and read, never applied, so no re-query is spent |
| CAPTURE-PRESS-UNDER-PROBE-RULE, VIEW-SWITCH-PRESS-RESTORED | **disclosures only**: a menu, a folder, a filter panel, a list, opened, read and closed; a folder or a tab switched only when it is read before, restored and read after; typing only into a SEARCH box. Nothing saved, sent, submitted, applied, scheduled or confirmed. The ruled cheap captures ride as ruled: ARTICLE-COMPOSER-ONE-CAPTURE, M-C18-EDITOR-OPENS-UNSAVED, L1-D3-MEDIA-CHOOSER-INTERCEPTED, MESSAGE-SEARCH-CAPTURE-FIRST, OWN-PROFILE-SCROLL-SANCTIONED |
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
page lands, except E4 and E8, whose loader retries an unread self assertion
once (the retry is paid from the reserve). `S` = skeleton only; `S+R` = the
raw page kept gitignored only if PEOPLE-GATE v2 reads 0 on every rule (his
own pages that draw no other person). The rows are the queue's own `rows`
cell.

| E | line (queue rank) | loads (run.) | srch | count | presses (nothing committed) | save | rows it unblocks |
|---|---|---|---|---|---|---|---|
| 1 | the receipt guard: the badge, `linkedin_new_messages` | 1 (1) | 0 | MEASURED (s11 loads 5, 37) | none | -- | -- (if X-0) |
| 2 | the receipt guard: the composer's list, `linkedin_list_conversations` | 1 (2) | 0 | MEASURED (s11 loads 6, 38) | none | -- | -- (if X-0) |
| 3 | `messaging-guarded` (6) | 1 (3) | 1 | MEASURED (s11 load 39) | the folder pill, Archived, then the options menu of ONE archived row that reads as read, read for the item that restores it, Escape; the folder back, verified; the inbox search: one benign keyword, Enter within that input only, the landing recorded, the box cleared, the list verified | S | M M28, M M34 (if X-0) |
| 4 | the re-proof: `linkedin_my_activity_items` | 1 (4) | 0 | ESTIMATED (the tool's own words: once, twice on a retry) | none | -- (the envelope reduced) | re-proves M C41; its item keys aim E11 |
| 5 | `C-SRCH-1` (116) | 1 (5) | 1 | MEASURED (the last classic load on record, 2026-09-28) | none | S | J 31 (not GAP): decides the route |
| 6 | `C-SRCH-0b` (119) | 1 (6) | 1 | MEASURED (s11 load 18, the AI page) | none; a nonsense token, letters only | S | J 1 (not GAP) |
| 7 | `C-SRCH-0a` (118), only if E5 shows classic serves | 1 (7) | 1 | MEASURED shape (as E5) | none; a nonsense token | S | J 1 (not GAP) |
| 8 | `in-me-profile` (3) | 1 (8) | 0 | MEASURED (s11 load 3) | the top card's opener (More or Resources) once; his photo only if exactly one BUTTON wraps it; Add custom button if exactly one is drawn; one scroll pass; the add-form links read, never pressed | S | N 76, P B3, P C8, P S4, P D11-P D23, P D26, P D29 (19) |
| 9 | `admit-in-me-details-recommendations` (23) | 1 (9) | 0 | ESTIMATED | the received and given tabs: the one not drawn pressed as a tab, read, the first pressed back, verified | S | N 121-N 123, N 125-N 128, P F1, P F5-P F9 (13) |
| 10 | `C-MSG26-4` (130) + `article-composer` (1) | 1 (10) | 0 | MEASURED (s11 load 24) | ARTICLE-COMPOSER-ONE-CAPTURE: onboarding dismissed; the author toggle, Manage (its drafts link read for M C47), the embed control and Next, each read and closed; never Publish or Schedule | S | M C44, M C46, M C50, M C78, M C81, P L3; M C47 (7) |
| 11 | `own-post-reactions` (5) + `C-B3-2` (101) + `C-JMN-4` (107), his own post | 1 (11) | 0 | MEASURED (s11 load 30) | readers-msg26's aims: the post's own `Open reactions menu`; the comment sort trigger; the control menu (the card's first expandable button, scrolled into view) and its "Who can comment on this post?"; LAST, its Edit post, the editor opened and closed with nothing typed | S | M C33, M C35b, M C18, M C23, M C90, M C29 (6) |
| 12 | `admit-mynetwork` (27) | 1 (12) | 0 | ESTIMATED | none; the invitation badge read before and after | S | N 22, N 32, N 62, N 97, N 98, N 110 (6) |
| 13 | `C-RJ26-3` (122) | 1 (13) | 0 | MEASURED (s11 load 11) | one resume card's options menu, read, Escape | S+R | J 71, J 72, P M1, P M3, P M4 (5) |
| 14 | `admit-newsletters-id` (32) | 1 (14) | 0 | ESTIMATED | none; its subscribe and share controls read | S | M C101, M C80, M C82, N 55, N 56 (5) |
| 15 | `admit-mypreferences-d-categories-privacy` (28) + C-PRIVACY | 1 (15) | 0 | ESTIMATED | none; no toggle pressed | S+R | J 87, N 143, N 96, P O22, P P3 (5); riders: 14 lane-S rows and M M39's switch |
| 16 | `admit-in-me-edit-contact-info` (30) | 1 (16) | 0 | ESTIMATED | none; labels and states, nothing typed | S+R | P A26, P A27, P A28, P A29 (4) |
| 17 | `admit-in-me-edit-forms-position-new` (31) | 1 (17) | 0 | ESTIMATED | none; labels and states, nothing typed | S+R | P D5, P D6, P D8, P D9 (4) |
| 18 | `C-MSG26-1` (128) + `admit-search-results-content` (93) | 1 (18) | 1 | MEASURED (s11 load 33) | All filters, found page-wide (0.3), its panel read for a group facet, Escape, nothing chosen; a generic technology hashtag | S | M C70; N 59, N 60 (3) |
| 19 | `connections-sort-and-filters` (109) | 1 (19) | 0 | ESTIMATED | the sort control and the Talks-about and Open-to filters, each opened, read, closed; none applied | S | N 24, N 27, N 28 (3) |
| 20 | `admit-in-me-isselfprofile-true` (117), its first load | 1 (20) | 0 | ESTIMATED | none; the landing must be proven his by the shipped self rule, or the read refuses | S | P D25 |
| 21 | the same line, its second load: the contact-info overlay | 1 (21) | 0 | MEASURED (session 1: it redirected to his profile) | none; labels only, no contact value saved or printed | S+R | P A25 |
| 22 | `admit-mypreferences-d-verifications` (46) | 1 (22) | 0 | ESTIMATED | none; the two-step verification entry never followed | S+R | P K1, P K7 (2) |
| 23 | `feed-menus` (7) | 1 (23) | 0 | MEASURED (s11 load 28) | the left rail's Saved items link read, not followed; up to three members' item menus opened and closed, each read for Unfollow (a followed author) | S | M C36, M C37 (2) |
| 24 | `feed-item-permalink-menu` (95), the member half, only if E23 drew a followed author's post | 1 (24) | 0 | MEASURED (s11 load 29) | that post's own control menu, opened and closed | S | N 37, N 43 (2) |
| 25 | `admit-in-me-details-skills-edit-forms-1` (40) | 1 (25) | 0 | ESTIMATED | none; the skill id off E8's reading, named by the caller | S+R | P E2, P E3 (2) |
| 26 | `admit-jobs-preferences-viewtype-seeking-preferences` (73) | 1 (26) | 0 | ESTIMATED | none; labels and states | S+R | P I12, P I13 (2) |
| 27 | `C-RJ26-1` (120) | 1 (27) | 0 | MEASURED (s11 load 19) | the job-openings card's Functions dropdown, read, Escape | S | J 169 |
| 28 | `C-RJ26-2` (121) | 1 (28) | 0 | MEASURED shape (s11 load 23) | none | S | J 111 |
| 29 | `admit-in-me-opportunities-volunteering-education` (69) | 1 (29) | 0 | ESTIMATED | none; the bare spelling (VOLUNTEERING-BARE-SPELLING-FIRST), the landing recorded | S+R | P D24 |
| 30 | `admit-learning` (77) | 1 (30) | 0 | ESTIMATED | none | S | J 152 |
| 31 | `admit-learning-career-journey` (78) | 1 (31) | 0 | ESTIMATED | none | S | J 156 |
| 32 | `admit-learning-me-my-library` (81) | 1 (32) | 0 | ESTIMATED | none | S | J 154 |
| 33 | `admit-premium-matches` (88) | 1 (33) | 0 | ESTIMATED | none | S | N 199 |
| 34 | `U-POST-DOCUMENT` (129) | 1 (34) | 0 | MEASURED (s11 load 25, the same composer) | More opened and read; the document control with the file chooser intercepted, never answered; Escape | S | M C5 |
| 35 | `admit-mynetwork-invitation-manager` (26) | 1 (35) | 0 | MEASURED (s11 load 14) | none; the type pills' words read against the closed type words | S | N 14 |
| 36 | `admit-in-me-edit-forms-summary-new` (64) | 1 (36) | 0 | ESTIMATED | none; nothing typed | S+R | P D2 |
| 37 | `admit-in-me-edit-secondary-language` (67) | 1 (37) | 0 | ESTIMATED | none; nothing typed | S+R | P D27 |
| -- | reserve | 3 (40) | -- | -- | the loader's retry (E4, E8); a press that loads a document, counted by hand; D-4's fallback (his experience list) | -- | -- |

**Totals: 37 loads, 5 searches, 105 GAP rows** (VERIFIED by the packer:
every row on its line, none twice, each row's ledger next step naming the
line). Without X-0, E1-E3 are skipped: 34 loads, 4 searches, 103 rows, and
the freed loads go to standby. If classic no longer serves, E7 is skipped
and its search goes to standby line 1.

**Why this order.** The receipt guard first, closest to the moment he read
his inbox (session 11's lesson). The re-proof next, because every line
anchored on his own profile (E8, E20, E21) rests on the rule it re-proves.
The route decision (C-SRCH-1) before anything else that serves the job
search, as session 11 handed over. Then rows per load, falling, with each
dependency kept: E8 before E25 (the skill id), E27 and E28 (the D-4
clearance) and every S+R line (his own identifiers for the gate); E4 before
E11 (his own post); E23 before E24.

**The values each read takes** (L1-D4-NEUTRAL-READ-VALUES; runner items,
vetoed by the identity key, never in a tracked file):

* C-SRCH-1: generic role words; C-SRCH-0a/0b: a nonsense token, letters
  only, naming no person; E3: one benign word; E18: a generic technology
  hashtag.
* C-RJ26-1: the large organisation session 11 cleared (its insights page is
  known to draw the dropdown); C-RJ26-2: a second large organisation whose
  Page draws a Products tab. Both are cleared again on E8 against his own
  experience entries the scroll pass draws (by id, by name slug, by name;
  booleans only). If the scroll draws none, his experience list costs one
  reserve load, as session 11's E2 did. Each company phase stops if its
  first tab does not name the organisation.
* E11: his own post, the kept authorship-established one session 11 used
  (session 2's post with comments), and it must also be among E4's fresh
  item keys, or E11 is not loaded.
* E14: one newsletter his own subscriptions page already draws (a kept
  reading, gitignored), published by LinkedIn or by an organisation's Page,
  never by a person; chosen by the lane at runtime (section 8).
* E25: one skill id his profile's skills section draws on E8, written to
  gitignored state and passed by the caller; if none is drawn, E25 is not
  loaded and the load returns to standby.
* E24: the first item on E23 whose own menu draws Unfollow; its urn is
  written to gitignored state and passed by the caller.

**Inside E8, read before GO at zero loads** (the line's own condition, "after
an offline read of its session-11 skeleton"): the photo control's shape on
the kept keyed skeleton (a button or a link), and the hydrated skeleton's nine
three-segment editor routes matched under session 11's shape key against the
closed list of section words (selfprofile26's method). A matched spelling is
that P D row's drawn address before the load; the load reads only what
remains, and the variant on E20 reads the Add-section surface for the rest.

---

## 4. The fill order and the shed order

**Standby, in order**, run only on a load the plan frees (a conditional line
skipped, the reserve untouched at the end) and only while the ledger has
room:

| # | line (rank) | loads | rows | note |
|---|---|---|---|---|
| 1 | `search-people-labels` (2) | 1 | 8: N 82, N 86, N 88-N 93 | **needs a free search** (E3 or E7 skipped); All filters page-wide (0.3) |
| 2 | `admit-in-me-opportunities-services-education` (68) | 1 | P H1 | stops at the first control into the Open-to flow |
| 3 | `admit-in-me-skill-insights-skill` (71) | 1 | P S3 | a skill index off E8's reading |
| 4 | `admit-mynetwork-network-manager-people-follow-following` (83) | 1 | N 61 | |
| 5 | `admit-mypreferences-d-premium-manage-account` (85) | 1 | P N22 | skeleton only: a billing page (section 8) |
| 6 | `admit-products-product` (89) | 1 | J 166 | LinkedIn's own product page |
| 7 | `admit-showcase-showcase` (94) | 1 | J 167 | LinkedIn's own showcase page |
| 8 | `C-P26-1` (102) | 1 | P S8 | Show all on his key skills, Escape |
| 9 | `C-JMN-2` (105) | 1 | J 56 | the Date posted pill, read, Escape |
| 10 | `comments-metric-spelling` (110) | 1 | M C39 | the metric selector read |
| 11 | `creator-hub-on-the-dashboard` (111) | 1 | P L7 | |
| 12 | `C-I3-1` (115) | 1 | M C97 | loading notifications clears his unread badge (NOTIFICATIONS-UNREAD-SPEND) |
| -- | `feed-item-permalink-menu` (95), the Page half | 1 | N 51 | only if E23's feed drew a Page post |

**Shed, from the bottom of section 3, if a load is needed beyond the plan**
(a retry, a document load counted by hand, an anomaly re-read the lead
orders): E37, E36, E35, E34 (the 1-row disk lines), then E33 to E30 (the
brief's "if they still fit" lines), then upward. Each costs its line's rows.

---

## 5. STOP rules

**STOP-ALL, his to clear or the lead's to read; the session ends, the flag
is lowered, Chrome is left serving:**

* any sign-in wall, checkpoint or challenge, on any page (the harness's
  health check after every load);
* a failed restore: the messaging folder, the recommendations tab, any
  sort, filter or tab not back on the state read before it;
* any publishing control met in the article composer, any autosave sign in
  an editor, or a save, send, submit, apply or confirm drawn as pressed;
* the post editor on E11 not closing to the post as it was;
* the flag not this lane's, a second client on 9224, or anything touching
  his own Chrome.

**The phase stops, and the lead reads before more is spent:** an error
envelope; an exception; a menu or dialog that does not close by its own
evidence (instrument 103); a press that loads a document (counted into the
ledger by hand); a landing that is not the address asked where the address
is a target (his profile variant not proven his; an organisation's first tab
not naming it); PEOPLE-GATE v2 raising, or its own-identifiers file absent
(it fails closed: skeleton only, and the phase stops).

**The re-proof decides a block.** If E4 refuses his own profile, the lines
anchored on the self rule (E8's presses, E20, E21) are skipped and the
lead is told at once; the rest of the plan runs.

**The receipt guard decides E3** (session 11's section 7, every condition):
the badge exactly 0; the list rendered with nothing opened;
`threads.receipt_guard` proceeding with 0 unread rows; again 0 unread right
before `/messaging/` opens and right before each press. No conversation is
opened while any rendered row reads unread, nothing is ever marked read, and
the archived row whose menu is read must itself read as read. On Enter in the
inbox search: refuse if focus reaches a composer or a send control enables.

**Refused before navigating** (the ledger's own refusals): a 41st load; a
6th search; a phase whose most loads would pass 40; an address
`readonly.is_read_url` refuses; a keyword item the identity key vetoes.

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
   live lane's worktree at the certified master that carries
   PEOPLE-GATE v2 (integration 5);
2. the self stand-in goes: session 11 asserted his profile by the redirect
   plus owner-only words because the url marker was gone; selfprofile26's
   rule is on master, so E8 lands through the shipped loader
   (`server._goto_self_profile_asserted`, which E4's tool also uses) and
   prints which signal answered;
3. PEOPLE-GATE v2 replaces `people_gate()` (below);
4. the search triggers are found page-wide (0.3);
5. the new phases of section 3, each refusing unless the flag stands and is
   this lane's, the ledger has room for its most loads, the driver lock is
   free and the attach environment is set, all before any browser contact.

**PEOPLE-GATE v2: THE EXACT HAND-OFF.**

* **Who:** lane infra26 builds it as a tracked module (the six rules of the
  orchestrator's 14:05 entry; PEOPLE-GATE-COUNTS-NAME-SLOTS; the defect is
  INSTRUMENTS 107.5) and it lands on master in integration 5. The session-12
  live lane wires it. Nobody copies it into gitignored state: the runner
  IMPORTS it from the worktree's tree, so the code that gates is the code CI
  certified.
* **Where it is called:** in the runner's `load()`, the one raw write.
  Today it reads the live DOM (`people_gate(page)`), then takes
  `page.content()` and writes it. v2 reverses that: the HTML string is read
  ONCE, the gate is run on that string, and that same string is the one
  written (rule 6: gate the string actually written). The harness's
  `_save_page(..., raw=True)` path goes through the same gate, or the runner
  never calls the step that uses it.
* **What it is given:** the HTML string; his own identifiers (his slug, his
  member urn and id, his photo asset ids), read in-process off a landing the
  shipped self rule proved his (E8) and kept in gitignored state, never
  printed; and the line's page class, so an events page is withheld by class
  (rule 5).
* **What it returns:** keep the raw page only when every rule reads 0 (a
  member urn or id not his; a photo asset not his; a picture's accessible
  text equal to a name; the link-less social-proof templates; an events page;
  plus profile links and name slots); otherwise the skeleton alone, and the
  record states the counts per rule, never a value. An exception or a
  missing own-identifiers file fails closed.
* **Shown failing before READY** (red first, in the runner's offline checks,
  on synthetic pages, no LinkedIn load): each of the six rules planted alone
  on a page of his own withholds the raw page; a clean page of his own keeps
  it; a page whose DOM changes between the gate and the write cannot slip
  (one string); the 35 checks session 11 left are re-run green.
* **Pinned at READY and at GO:** the master sha, the module's sha256, the
  runner's sha256.

**THE CEILING CHECK (0.8), at READY.** On the merged master, one offline
check drives seven loads through the runner's `load()` inside one
`BROWSER.session()` on a fake page, and none refuses. If the counter refuses
the 4th, either the counter's scope is fixed in the infra lane or the runner
opens a fresh per-call scope for each load; the session does not start on a
red check.

**IF HE RULES ONE SHARED BUDGET** (section 7): the runner appends each load
to the pipeline's pinned ledger through its public contract (`load_record`,
`call_refusal`) and refuses on its refusal. That wiring is the pipeline
lane's contract, named here so it is not missed.

**READY means:** the runner copy in place and pinned; v2 wired and its red
checks shown; the ceiling check green; `os_check` reading 9224 down or held
only by the dedicated profile; the plan's items prepared (the values of
section 3, each vetoed by the identity key).

---

## 7. What needs him before GO

1. **X-0: his inbox read to 0 unread, just before GO.** E1-E3 only: 2 rows,
   3 loads and 1 search. Without it they are skipped and the plan runs.
2. **His answer to the open budget question** (the orchestrator's 15:36
   entry): one LinkedIn budget shared with the job pipeline (40 loads per 12
   hours in all, the recommendation) or two. If shared, the session's
   ceiling is 40 less what the pipeline spent in the same 12 hours, read off
   the pinned ledger at GO.
3. **Reachable for a checkpoint.** No presence otherwise: nothing in this
   session needs him watching.
4. **Optional, only if he can watch:** the Open-to-Work editor capture
   (queue line 24, OPEN-TO-WORK-EDITOR-ATTENDED-ONLY): 1 load, 11 rows, the
   modal read and closed with nothing chosen. It replaces E37 if he says yes.

**What he should know, none of it outward:** nothing is sent, followed,
reacted to, applied for or saved, and no other member's profile is opened.
Loading his invitation manager (E35) clears his pending-invitation badge, and
`/mynetwork/` (E12) may (RECEIVED-BADGE-IS-THE-READS-COST). The article
composer (E10) may leave an empty draft of his own; if it does, the record
says so, and deleting it is his or a later build's. `/messaging/` (E3) lands
in a conversation LinkedIn picks, which the guard has already proven read.

---

## 8. The calls this plan made (each reversible; the lead may strike any)

1. **Disk lines beyond the brief's list** (0.2), taken by rows per load:
   lines 1, 5, 7, 26, 27, 28, 30, 31, 40, 64, 67, 73, 93, 95, 101, 107, 109
   and 129. Struck, the session is the brief's 19 loads plus Learning and
   premium matches (23 loads), and the 18 lines wait for session 13.
2. **The fifth search.** When both conditional searches run, the brief's
   inbox search keeps its slot and `search-people-labels` (8 rows) waits on
   standby. Swapping them buys 7 rows; say the word.
3. **C-B1a is not scheduled.** Typing a value into an editor field is not a
   disclosure, so the brief's "disclosures only" keeps it out although
   EDITOR-TYPEAHEAD-SANCTIONED would allow it (2 loads, 3 rows).
4. **The newsletter** (E14) comes from his own subscriptions, an
   organisation's or LinkedIn's, chosen by the lane at runtime, where the
   queue's cell reads "a newsletter he names". It is a read, not an outward
   act, so OPERATOR-NAMES-THE-TARGET does not bind it. Struck, E14 moves to
   L2 (5 rows).
5. **Skeleton only on every page that may show people**, stricter than the
   queue's S+R on the Learning pages, premium matches, his network pages and
   his profile (the brief's rule); and skeleton only on his billing page
   (standby 5), whose raw would carry payment details and whose labels the
   skeleton keeps.
6. **The riders**: M C47 on C-MSG26-4's load; N 59 and N 60 on C-MSG26-1's;
   C-B3-2 and C-JMN-4 on own-post-reactions' load, as L1-D1-RIDERS-RIDE took
   them in session 11 and C-JMN-4's own cell proposes.

---

## 9. Not scheduled, and why

| lines | why |
|---|---|
| every `t-named-*` line; msg-thread-footer (11); C-B5-1, C-B5-2, C-B5-3 (96-98: groups he names; L1-D2's choice bound session 11 only); C-JMN-1 (104: a job he archives by hand); C-JMN-3 (106); t-named-search-card (108); C-J68-1 to -3 (112-114) | operator-named targets: L2 and L3 |
| `admit-in-me-opportunities-job-opportunities-edit` (24) | his presence (section 7, item 4) |
| `search-people-first-degree` (9) | a sixth search; standby behind line 2 if two searches free |
| C-B1a (103) | section 8, item 3 |
| `admit-in-me-details-featured` (34) | no address serves (session 11: it lands on his profile root) |
| `admit-jobs-search-results-keywords` (43) | captured; its offline build is next |
| `sessions-surface` (10), the five ads-settings pages (123-127), the AI-generating loads (29, 70, 86, 87), `admit-pulse-article` (38), `admit-resume-builder` (91) | each address refused today, or waiting on its ruling |

---

## 10. Census edits

**Only the capture queue's `session` cells, keyed by surface id, each old
value asserted before the write, no other cell and no reflow** (VERIFIED by
a diff of every other column after the write):

* to `12`, the lines section 3 schedules whose cell did not already read 12:
  1, 5, 7, 23, 26, 27, 28, 30, 31, 32, 40, 46, 64, 67, 69, 73, 77, 78, 81,
  88, 93, 95, 101, 107, 109, 117 (26 lines);
* to `12, standby`, the twelve standby lines: 2, 68, 71, 83, 85, 89, 94,
  102, 105, 110, 111, 115.

Unchanged because they already read 12: lines 3, 6, 116, 118-122, 128-130.
No row moved: a capture moves no census row by itself, and a session cell is
not a state.

---

## 11. Instruments (all DISPOSABLE)

The lane's scratch, in the main checkout's gitignored state: a queue
printer and full-cell reader; a row cross-check against the ledger; the
verdict re-driver (`readonly.is_read_url` over every queue address, 0
disagreements); a button census over the tracked skeletons; the
`main`-ancestry counter behind finding 0.3; and the packer behind sections 1
and 3, which fails on a row assigned twice, a row not on its line, or a row
whose ledger next step names another line. None was shown failing on a
planted defect, so none enters INSTRUMENTS.

---

## 12. Gates

Run on the staged tree before the commit; the live-session flag absent at
every check.

| gate | result |
|---|---|
| `scripts/check_next_step.py` | GREEN: every GAP row once (513), every source and payload resolving, the queue agreeing (its verdicts re-driven through the boundary) |
| `scripts/census_completion.py --check` | every headline figure matches its pin; no pin moved, because no row moved |
| the three derived views | written twice to a fixed point, then checked clean: the audit index over 299 documents; the rulings register at 158 rulings, every declaration accounted for; the blocker map, where this record joins the candidate counts and is no row's first candidate |
| `scripts/check_cited_shas_resolve.py` | every cited SHA an ancestor of master |
| `scripts/check_asserted_names_resolve.py` | 95 candidate sites: 94 cleared by an author's mark, 1 asserted and absent, the site master already pins in its own test; none from this record |
| eleven guard files that read the queue or every audit document, one process each | 186 passed, the slowest 85 s |
| `tests/test_a_cited_sha_resolves.py` | over the two-minute cap on its own (stopped at 115 s, nothing failed before the stop): left to lane CI; the script it wraps passed above |
| the identity gate | the pre-commit gate at the commit; the committed-blob test and lane CI after it, reported by head sha in the lane's report to the orchestrator |

NOT RUN locally: the full suite (lane CI runs it on the lane's ci/ ref).
