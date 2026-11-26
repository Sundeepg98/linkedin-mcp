# Live session 11 -- campaign L1, the capture session: the prep, written offline

**2026-11-25. The live lane `live-s11`, branch `worktree-agent-live-s11`, base
master `4c62196` (certified, pushed). PREP ONLY: zero LinkedIn page loads, no
browser started or attached, nothing pressed, nothing committed.** The session
runs only on the orchestrator's message `GO session 11`; its record continues
below this prep, in the same file.

It runs under the campaign plan of 2026-11-25 (lane live-prep26, kept outside
this repository): section 1.0 (the rules every session runs under), 1.1, 1.2
(L1: 38 lines, 38 loads plus 2 reserve, 4 searches, 100 queue rows plus riders)
and 5 (the sibling riders); the lane standing rules, all of them but the
OFFLINE clause (this is the live lane); and the orchestrator's four rulings for
L1: **D-1 YES** (the two riders), **D-2 (b)** (the groups), **D-3 YES** (the
composer media controls, file chooser intercepted), **D-4** (the read values,
at runtime, never in a tracked file).

**Every person below is named by ROLE. No name, slug, member id, thread id,
group id, organisation, keyword value or absolute path is written here.**
Evidence classes: VERIFIED = measured by an instrument this lane ran (named);
DERIVED = follows from verified facts; ESTIMATED; UNVERIFIED.

---

## 0. Step 0, and what disk said

* **The worktree:** toplevel is this worktree, HEAD `4c62196`, branch
  `worktree-agent-live-s11`, tree clean (VERIFIED, git).
* **The box, 22:48 IST (VERIFIED, the lane's `os_check.ps1`, OS facts only, no
  contact with any browser):** port 9224 NOT listening; 0 clients connected to
  it; 0 Chrome processes on the dedicated profile (18 other `chrome.exe` are his
  own browser and are not touched); no profile lock; no live-session flag.
  **So Chrome is not up for the session yet** (section 1).
* **The L1 queue on disk agrees with the plan** (VERIFIED, a script over
  `_audit/_census/capture-queue.tsv`): the 38 lines are all present, they list
  **100 distinct rows**, the queue counts **41 loads** for them (38 once the
  three riders share a load) and **3 searches** (the plan counts line 24's jobs
  keyword search as a fourth).
* **Every address the session composes is admitted** by `readonly.is_read_url`
  on this tree: 47 checked -- the 38 lines' own, the company tabs with a numeric
  id, the content search with a hashtag, the people searches, the groups
  search, a thread, a permalink of each urn kind, his experience list -- 0
  refused (VERIFIED).
* **The runners of sessions 3 to 10 are gone.** They lived in the lane's
  scratch folder, which the operating system's temp cleanup empties; only
  session 6's runner, rebuilt for session 7, survives in the previous live
  lane's gitignored state. Every one of them took the tracked harness
  `scripts/_probe_live_lane_session_2.py` by import. This session's runner is
  new (section 2) and does the same.
* **The kept readings this session's vetoes rest on** (the previous live lane's
  gitignored state, read only; VERIFIED by booleans and counts, no value
  printed): his rail (8 items, authorship ESTABLISHED, 2026-09-23); session 2's
  post with comments, which is among them; session 2's
  `linkedin_group_memberships` reading (5 memberships, 2026-09-28); the thread
  sessions 5 and 6 resolved for the conversation he named (his brother's), the
  same id in both.
* **Measured offline on session 8's kept raw capture of his profile**
  (2026-10-10, a local headless Chromium, JavaScript off, every request
  aborted; counts only): the first render draws **no Experience section** (0
  "Experience", "Education" or "Skills" words; 16 company links, all slugs); 0
  links to a Page's admin view; the top card draws More 1 and Resources 1, no
  "Add custom button", one image inside a LINK to his profile root and one
  inside a `div[role=button]`; 11 distinct member slugs. Two consequences,
  both taken in below: D-4's check needs a fallback load (section 5), and the
  raw capture of his profile will be withheld by the people gate (section 5).

## 1. The browser: how it is launched, and how the session attaches

* **The dedicated persistent profile:** `_state/chrome-profile` of the MAIN
  checkout (gitignored). His signed-in LinkedIn session lives there; his
  everyday Chrome is another profile, another process, and is never touched.
* **THE LAUNCH COMMAND**, run from the main checkout's root:

      powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start_chrome.ps1

  (`scripts/start_chrome.ps1`, sha256 `c1a3ee44ed5a`). It is idempotent: a
  browser already answering 9224 means nothing is started. It refuses a live
  profile lock (the stdio server holding the profile), refuses a Chrome already
  on the profile without the port (Chrome's singleton would swallow the second
  start and open no port), and warns before a profile re-stamp. **Its flag list
  is exactly two entries: `--remote-debugging-port=9224` and
  `--user-data-dir=<the profile>`; no automation flag.**
* **`readonly.assert_launch_flags_permitted`** is the server's LAUNCH-mode
  gate: every launch puts `config.LAUNCH_ARGS`
  (`--disable-blink-features=AutomationControlled`,
  `--remote-debugging-port=9224`) through `PERMITTED_LAUNCH_FLAGS`, and
  `tests/test_launch_boundary.py` holds it. **This session does not launch.**
  It runs in ATTACH mode (`LINKEDIN_CDP_ATTACH=1`): the package connects over
  CDP to `127.0.0.1:9224`, opens a tab of its own, and passes no flag at all.
  The launch path would refuse this profile anyway
  (`profile_version.assert_no_downgrade`: playwright's chromium is older than
  the stamp real Chrome put on it -- measured 2026-09-19, per the start
  script's own notes; not re-measured here).
* **Who starts it.** In every precedent the orchestrator started it with that
  command (2026-09-28, 08:03 and 12:41) and this lane never started, restarted
  or closed it. If the GO finds 9224 down and says the lane may, the lane runs
  the same command and nothing else.
* **Before the first load:** `os_check.ps1` must read 9224 listened on by the
  dedicated profile's browser process, **0 other clients** on 9224 (one
  driver), no lock holder; the window is fronted (`front_chrome.ps1`, the
  profile's browser process by PID, never by image name -- session 2 measured
  that a covered window draws a fraction of the page: 7 `[aria-expanded]`
  controls behind other windows, 44 in front); then the harness's
  `attach_check` (0 loads) must PASS `[0, 1, 0]` as in sessions 7 to 10.
* **The environment of every run:** `LINKEDIN_CDP_ATTACH=1`,
  `LINKEDIN_CDP_PORT=9224`, `LINKEDIN_MIN_INTERVAL_S=20`,
  `LIVE_LANE_SESSION_DIR=live11`; the main checkout's venv interpreter.
* **Chrome's end:** every run closes only its own tab, never the browser's
  last (`close_tab_keeping_the_window`, session 2's fix 1), then drops CDP;
  Chrome is left serving.

## 2. The runner, its source files, and what was shown offline

| file | where | sha256 (12) | role |
|---|---|---|---|
| `runner_s11.py` | the lane's scratch folder; the copy that RUNS is in the gitignored `_state/live11/tools/` (on the repository's own drive, out of reach of the temp cleanup that took sessions 3-10's runners) | `9647d316c27f` (at GO; `510ec4e30cbb` at READY) | the session: 15 phases, plus `flag_on` and `flag_off` |
| `scripts/_probe_live_lane_session_2.py` | tracked, at `4c62196` | `00552db3366e` | imported: the ledger, the driver lock, the counter around `BROWSER.goto` (all three doors), the keyed shapes and skeletons, `tracked_copy` and `--export-fixtures`, the health check (auth wall, challenge phrases), `attach_check`, the top card's opener (`_in_me`, `_in_me_more`) |
| `scripts/_probe_live_lane_session_1.py` | tracked | `df378e2c2e76` | imported through the harness: `CEILING` 40, `MIN_GAP_S` 20, the permalink template, `own_activity_ids` |
| shipped tools and modules | tracked | -- | `linkedin_new_messages`, `linkedin_list_conversations`, `linkedin_search_groups`, `linkedin_my_activity_items`; `threads` (`receipt_guard`, `read_conversation_list`, `thread_url`, `landed_on_thread`, `read_thread`); `people_search.compose`; `readonly.is_read_url` (`77b67f6e2b76`) |
| `os_check.ps1`, `front_chrome.ps1` | beside the runner | -- | the OS facts before and after; the window fronted |
| `test_runner_offline.py` | beside the runner | -- | the offline checks below |

**THE LEDGER** is the harness's, in `_state/live11/`: `ledger.json` counts every
navigation any phase makes -- a shipped tool's own included -- refuses the 41st
load and a sixth `/search/` load BEFORE navigating, and waits out 20 s since the
last load across processes; `driver.lock` refuses a second driver;
`shape.key` keys this session's shapes.

**WHAT THE RUNNER ENFORCES:**

* every phase refuses unless the attach environment is set, the session
  directory is `live11`, **the live-session flag stands and is this lane's**,
  the ledger has room for the phase's most loads and searches, and the driver
  lock is free -- each checked before any browser contact;
* `PAGE-MAY-VETO-NEVER-SUPPLY`: every address is a constant, a package
  composer (`people_search.compose`), or a template filled from a `--item` the
  caller passes, each item a closed shape and never echoed. The readings may
  only refuse: his own post must be among his authorship-established rail; the
  member group among his memberships reading; the two other groups among THIS
  session's groups search and not his; the two permalinks among THIS session's
  feed reading, of the right actor kind; the thread must be the one recorded
  for the conversation he named; the company tabs need THIS session's employer
  check. Where the plan takes an item off a reading (the feed's urns, the
  search's group ids), the runner WRITES the reading to gitignored state and
  the caller names the item in the next run;
* **ONE click site, ONE typing site, ONE `goto` site** in the file (counted on
  its syntax tree: 1, 1, 1). Line 5's top-card opener is the harness's own key
  and goes through the harness's one click site. A document request during any
  press is an uncounted load: it is counted into the ledger by hand at once and
  the phase stops;
* a trigger is pressed only when EXACTLY ONE visible control matches, by a
  closed set of LinkedIn's own names or by structure; otherwise nothing is
  pressed and the counts are the reading. Every opening is closed by Escape
  (the trigger pressed once more only when Escape leaves it expanded, session
  2's fix 4), and must return the page to its state before the press -- no more
  dialogs, our added words gone, the trigger's state and the address back --
  or the phase stops. A press that drew nothing is not Escaped (an Escape then
  would close the composer it sits in);
* the keyword items are vetoed against the gitignored identity key (section 5);
* printed: closed words, booleans, counts. Never a name, link, id, urn,
  keyword or organisation.

**SHOWN OFFLINE** (`test_runner_offline.py`, 32 checks, 32 pass, run against
both copies; no LinkedIn load, nothing written to `_state/live11/`): every item
shape refuses its wrong forms (a slug for a digit id, non-ASCII digits, an
unknown item, an item named twice, a hashtag with a space, a urn of another
kind, a thread id with a path in it, words with a slash); his kept post passes
the activity veto and a foreign one is refused; the recorded thread passes and
another is refused; groups, permalinks and the organisation are refused with no
reading of this session; and, in a local headless Chromium on SYNTHETIC pages
with every request aborted: a menu opened, read and closed by Escape; a press
that draws nothing is not Escaped; a menu that will not close raises
`did_not_close`; **a link press that loads a document raises and is counted by
hand** (into a fake ledger); the people gate counts distinct other members and
excludes `/in/me/` and his own slug. Refusals run on the real entry point: a
wrong thread is VETOED, no attach environment is REFUSED, no flag is REFUSED, a
missing item is REFUSING, a wrong session directory is refused -- each before
any browser contact.

**ONE INSTRUMENT OF MINE WAS WRONG, AND THE CHECK SAID SO.** The first keyword
veto matched every word of every class of the identity key, and refused a
generic people keyword and a generic hashtag: one of their words sits in a page
he follows and in a page slug, another pair in a denied-terms class (VERIFIED,
by class name only). It now refuses a keyword that shares ANY word with the
classes that name him, the people he named, his places or employers, or EQUALS
any key value as a whole phrase. Re-run: green, and a planted identity word and
a planted whole value are still refused.

**NOT SHOWN, NAMED:** anything live. Each trigger is either measured on a kept
capture where LinkedIn's label survived (All filters 1 on both people searches;
the messaging folder pill 1 and the message search box 1 on the composer; the
sharebox's "Schedule post" 1 and "Add media" 1; the comment box's
"Open Emoji Keyboard" 1 beside one other control; the feed's header search
input 1; the menu link carrying `targetUrn`), or a closed name set that a live
page may not draw. A miss refuses without a press and costs that capture, never
an act.

## 3. The flag

`runner_s11.py flag_on` writes `_state/LIVE_SESSION_ON` in the MAIN checkout --
a JSON body naming this lane and session 11 -- before the first load; every
loading phase refuses without it. While it stands, every other lane runs only
targeted tests, serially (the standing rules). `flag_off` deletes it at the
close, and only if it is this lane's. A session cut short leaves it standing,
which is the safe direction; the record says so.

## 4. The ordered load list

Execution order (E), numbered against the plan's section 1.2 table (#). The
plan orders by rows per load; this order honours its three dependencies --
`messaging-guarded` (#20) before `msg-thread-footer` (#8) and `C-B3-1` (#7);
`feed-menus` (#14) before `feed-item-permalink-menu` (#12); `C-B5-3` (#18) then
`C-B5-4` (#38) on one group page -- and two more of its own: `in-me-profile`
(#5) first, because D-4's check reads it and every later people gate needs his
own slug off its landing; and the messaging block early, closest to the moment
he read his inbox (section 7).

| E | phase | # | line | loads (run.) | srch | presses (nothing committed) | save | rows |
|---|---|---|---|---|---|---|---|---|
| 0 | `os_check`, `flag_on`, `attach_check`, the window | -- | -- | 0 (0) | -- | none | -- | -- |
| 1 | `profile` | 5 | in-me-profile | 1 (1); 2 if the self-assertion retries | -- | the top card's opener (More or Resources, the harness's key); his photo (the top card's one image BUTTON; the image link is never pressed); 'Add custom button' if drawn; the Me menu | S+R, gated | N 76, P B3, P C8, P S4; rider page-admin-precondition (admin anchors counted on the page and in the open Me menu, never followed); D-4's check |
| 2 | `experience` | -- | D-4's fallback: his experience list | 1 (2), only if E1 drew no Experience section | -- | none | S+R, gated | none (D-4) |
| 3a | `messaging` | 20 | messaging-guarded | 3 (5): the badge off his feed; the composer's list; `/messaging/` | -- | the requests entry read; the folder pill, then Archived (a folder), then back to the folder it read, verified; the message search box, one benign keyword typed, cleared, Escape | S | M M28, M M34, M M7, M M8, M M9 |
| 3b | (same run) | 8 | msg-thread-footer | 1 (6) | -- | none: the footer's controls and any suggestion chips | S | M M20, M M40, M M51 |
| 3c | (same load) | 7 | C-B3-1 | 0 (6) | -- | the active row's options menu, or the header's own, opened, read, Escape | S | M M26, M M27, M M29, M M31 |
| 4 | `own_pages` A | 9, 23, 11, 35, 1, 30, 29 | featured; sessions-surface; unfollowed; ads (+C-ADS); application settings (+O-JOB-APPLICATION-SETTINGS, +U-RESUME-MANAGER); tracker clicked_apply; career insights | 7 (13) | -- | none | S+R gated (23: S) | 3 + 1 + 3 + 1 + 10 + 1 + 1 = 20; siblings 5 + 5 + 1 = 11 |
| 5 | `own_pages` B | 2, 10, 34, 31, 32, 33 | invitation manager; sent; following; learning; career journey; my library | 6 (19) | -- | none | S+R gated | 10 + 3 + 1 + 1 + 1 + 1 = 17 |
| 6 | `jam` | 21 | jobs-alerts-manager (+O-JOB-ALERTS) | 1 (20) | -- | the alert manager's list, if exactly one disclosure trigger draws it | S | J 37; siblings J 35, J 36, J 100 |
| 7 | `jobs_search` | 24 | the jobs keyword search | 1 (21) | 1 by the plan's count (the ledger files it under jobs) | none | S+R gated | J 16 |
| 8 | `company` | 15, 25, 26, 27, 28 | insights headcount; about; events; life; products | 5 (26) | -- | none; the first tab must name the organisation, else stop | S+R gated | 2 + 1 + 1 + 1 + 1 = 6 |
| 9 | `composers` | 4, 6 | article-composer; sharebox-scheduled (+U-POST-MEDIA) | 2 (28) | -- | article: none, nothing typed; sharebox: the media control with the file chooser intercepted and never answered, FIRST; then Schedule, then its scheduled list; Escape | S | 6 + 4; siblings M C3-M C7 (D-3) |
| 10 | `feed` | 14 | feed-menus | 1 (29) | -- | the global search box (recent searches); one member's item menu and one Page's item menu, each read for the urn its link carries (written, never printed); an ad's own control, then its Hide-or-report dialog, nothing chosen | S | N 95, N 200 |
| 11 | `permalinks` | 12 | feed-item-permalink-menu | 2 (31) | -- | each item's own control menu: which of Not interested, Unfollow and Mute it draws | S | N 37, N 43, N 51, N 153, N 154 |
| 12 | `own_post` | 13, 19 | own-post-reactions; C-B3-2 (+U-COMMENT-MEDIA) | 1 (32) | -- | the reactions count control (its list of reactors); the item's control menu, then 'Who can comment on this post?'; the comment box's image control with the file chooser intercepted; Escape | S | 2 + 2; sibling M C27 (D-3) |
| 13 | `searches` | 3, 22, 16 | search-people-labels; search-people-first-degree; the content search | 3 (35) | 3 (3) | All filters, its panel read, Escape; the Industry and School pills (if neither is drawn, the All-filters panel instead); none | S; S; S+R gated | 8 + 1 + 2 = 11 |
| 14 | `groups_search` | -- | the reserve: ONE groups search (D-2 b) | 1 (36) | 1 (4) | none | S (reduced envelope) | fires N 161 |
| 15 | `groups` | 17, 37, 18, 38 | C-B5-1; C-B5-2; C-B5-3 + C-B5-4 | 3 (39) | -- | none; none; the invite control, its dialog's search box given the brother's name, nothing selected or sent, Escape; then the share box's trigger, the group composer read with nothing typed, Escape | S | 2 + 1 + 2 + 1 = 6; sibling N 169 (follows N 168) |
| 16 | `own_pages` | 36 | premium matches | 1 (40), if the ledger has room | -- | none | S+R gated | N 199 |
| 17 | `flag_off`; export; Chrome's end | -- | -- | 0 (40) | -- | -- | -- | -- |

**THE ARITHMETIC (DERIVED from the table):** 39 loads without E2, **40 with
it**; searches 4 by the ledger's `/search/` count, 5 by the plan's (line 24
counted); 100 queue rows; siblings 15, or 21 with D-3's six; N 161 fired.
**THE OVERFLOW RULE is the plan's:** if a load is needed beyond 40 -- the
self-assertion retry on E1, the own-post reserve (`linkedin_my_activity_items`,
one or two loads, then E12 again), an anomaly's re-read -- line 36 (E16) moves
to L2 first, then line 37 (E15 runs without its second candidate). Each costs
one row.

**THE EXACT COMMANDS**, from this worktree's root, with the environment of
section 1 and the main checkout's interpreter (`$R` is the runner's copy in
`_state/live11/tools/`; every `<...>` is a value passed at runtime and kept only
in gitignored state):

    powershell -NoProfile -ExecutionPolicy Bypass -File _state/live11/tools/os_check.ps1
    $PY $R flag_on
    $PY scripts/_probe_live_lane_session_2.py --only attach_check
    $PY $R profile --item org=<digits> --item org_name=<its name>
    $PY $R experience --item org=<digits> --item org_name=<its name>      # only if E1 drew no Experience
    $PY $R messaging --item msg_kw=<one benign word> --item thread=<the recorded id>
    $PY $R own_pages --lines featured,sessions_surface,unfollowed,ads,application_settings,tracker_clicked_apply,career_insights
    $PY $R own_pages --lines invitations,invitations_sent,following,learning,learning_journey,learning_library
    $PY $R jam
    $PY $R jobs_search --item job_kw=<generic role words>
    $PY $R company --item org=<digits> --item org_name=<its name>
    $PY $R composers
    $PY $R feed
    $PY $R permalinks --item member_post=<kind:digits> --item page_post=<kind:digits>   # off E10's reading
    $PY $R own_post --item activity=<digits>                                            # the kept post
    $PY $R searches --item people_kw=<a generic role word> --item hashtag=<a generic technology hashtag>
    $PY $R groups_search --item groups_kw=<a generic keyword>
    $PY $R groups --item open_group=<id> --item gated_group=<id> --item member_group=<id>
    $PY $R own_pages --lines premium_matches                                            # if the ledger has room
    $PY $R flag_off
    $PY scripts/_probe_live_lane_session_2.py --export-fixtures

## 5. The rulings applied, and the lane's own calls

* **D-1 YES:** `C-B3-2` rides `own-post-reactions`' load (E12); `C-B5-4` rides
  `C-B5-3`'s (E15).
* **D-2 (b):** C-B5-3/-4's group comes from his memberships as
  `linkedin_group_memberships` returned them -- the KEPT reading (session 2): a
  fresh fire costs three loads (the tool brackets the Groups page with the feed
  at both ends) that this session does not have. A group he has since left
  draws no invite control, so C-B5-3 then refuses without a press and the record
  says so. C-B5-1/-2's groups come from ONE `linkedin_search_groups` fire (E14,
  N 161's first), the lane naming two result ids that are not his memberships;
  open or gated shows only on the page, so each candidate is CLASSIFIED by what
  it draws (`Join` serves C-B5-1, `Request to join` serves C-B5-2) and the
  record says which line each served -- a wrong guess costs that line, never an
  extra load. The name typed into the invite dialog's search box is the
  brother's spelling LinkedIn draws, read from the gitignored key at runtime;
  nothing is selected or sent.
* **D-3 YES:** U-POST-MEDIA and U-COMMENT-MEDIA press one media control with
  the page's file chooser INTERCEPTED (a Playwright `filechooser` listener
  registered before the press) and never answered. On the sharebox the media
  control goes FIRST: an intercepted chooser draws nothing, so nothing is
  Escaped and the composer stays for Schedule; the other order risks the rider,
  since an Escape that closes Schedule's dialogs may close the composer too.
* **D-4:** session 2's PLAN recorded a method, not an organisation (its
  session RECORD holds one, cleared then against his resume -- the employer of
  one posting, not a Page known to draw every tab), so the ruling's "otherwise"
  applies: **one large company Page that draws every tab, chosen by the lane at
  runtime**, cleared twice before any company tab loads -- offline against the
  identity key (whole phrase against every class; word against the classes that
  name him, his places and employers: the planned candidate passes, and under the first, all-class word match 20 of 21 large-company candidates did) and
  live against his own profile's experience entries in the page (by id, by its
  name's slug, by its name; booleans only). Because session 8's capture of his
  profile draws NO Experience section on the first render, the live half runs
  on E1 if the section is drawn and otherwise on E2, his experience list (one
  load, his own page). The `company` phase refuses without that clearance, and
  stops if the first tab does not name the organisation. **The other values:**
  a generic role word for the people search, generic role words for the jobs
  search, a generic technology hashtag, a generic two-word keyword for the
  groups search, one benign word for the message search -- all five, and the
  organisation's name, passed the identity-key veto today; none is written in
  a tracked file.
* **THE LANE'S OWN CALLS** (none outward, each reversible):
  * **RAW ONLY WHERE THE PAGE DRAWS NO OTHER MEMBER.** The queue writes S+R on
    pages that draw people -- the invitation managers, the following list, the
    content results, a company's Life tab, his own profile's people rails --
    and the brief's hard rule says "Raw pages showing other people are never
    kept, only skeletons". The rule binds. Every S+R line keeps its raw only if
    the people gate reads 0 OTHER members (distinct `/in/<slug>` links other
    than `/in/me/` and his own slug, read off line 5's landing and kept in
    gitignored state); otherwise the skeleton alone, and the record says how
    many were drawn. The gate cannot see a person drawn without a profile link;
    that residue is stated, not smoothed.
  * **The thread for #8 and #7 is opened by the id sessions 5 and 6 resolved
    for the conversation he named** -- a caller item, vetoed against that
    record -- never by a row chosen off the page, which lane B3 measured as the
    page supplying the target. The page vetoes by its landing and its header.
  * **His own post for #13 and #19** is session 2's post with comments (his, by
    the authorship-established rail); the reserve fires only if it no longer
    serves.
  * **Two fallbacks, each the same class of press:** line 22's Industry and
    School pills not drawn (session 8's first render drew neither) -- the
    All-filters panel on the same page instead; any trigger not exactly one --
    not pressed.

## 6. Where each capture is saved

* **Gitignored, `_state/live11/` of this worktree** (the live lane's state):
  per key, `<key>.skeleton.html` for every page, `<key>-open.skeleton.html` for
  every opened control, `<key>.html` raw only for an S+R line whose gate read 0,
  and `<key>.json` (readings: counts, booleans, closed words; tool envelopes
  reduced where they can carry a person). Session files beside them:
  `ledger.json`, `driver.lock` (during a run), `shape.key`, `self.json` (his
  slug, for the gate), `employer_check.json` (shapes and booleans),
  `feed_urns.json`, `groups_search_ids.json`, `items_used.json` (the runtime
  values), `own_activity.json` (the reserve only).
* **The keys, by line:** 5 `in_me` (the harness's skeleton), `in_me_more-open`,
  `in_me_photo-open`, `me_menu-open`, `in_me_profile` (raw, if gated in);
  E2 `in_me_experience`; 20 `messaging_list`, `messaging_guarded`,
  `messaging_folder-open`, `messaging_archived`, `messaging_search`;
  8 and 7 `msg_thread`, `c_b3_1_menu-open`; 9 `featured`; 23
  `sessions_surface`; 11 `unfollowed`; 35 `ads`; 1 `application_settings`;
  30 `tracker_clicked_apply`; 29 `career_insights`; 2 `invitations`; 10
  `invitations_sent`; 34 `following`; 31 `learning`; 32 `learning_journey`;
  33 `learning_library`; 36 `premium_matches`; 21 `jobs_alerts_manager`;
  24 `jobs_search_keywords`; 15, 25-28 `company_insights_headcount`,
  `company_about`, `company_events`, `company_life`, `company_products`;
  4 `article_composer`; 6 `sharebox`, `u_post_media-open`,
  `sharebox_schedule-open`, `sharebox_scheduled_list-open`; 14 `feed_menus`,
  `feed_search_box-open`, `feed_member_menu-open`, `feed_page_menu-open`,
  `feed_ad_control-open`, `feed_ad_hide_or_report-open`; 12
  `permalink_member_post`, `permalink_page_post` and their `_menu-open`;
  13 and 19 `own_post`, `own_post_reactions-open`, `own_post_menu-open`,
  `own_post_who_can_comment-open`, `u_comment_media-open`; 3
  `search_people_labels`, `search_people_all_filters-open`; 22
  `search_people_first_degree` and its pills' `-open`; 16 `search_content`;
  the reserve `groups_search`; 17 and 37 `group_candidate_a`,
  `group_candidate_b`; 18 and 38 `group_member_c_b5_3_4`, `group_invite-open`,
  `group_invite-typed`, `group_composer-open`.
* **Tracked, after GO:** `tests/fixtures/live11/<key>.html`, written by the
  harness's `--export-fixtures` (`tracked_copy`: every keyed shape reduced to
  `x`, an id reference to `k` and its hash, strict ASCII), committed through the
  pre-commit identity gate (armed: its output names the wordlist it loaded),
  then `tests/test_no_committed_identity.py` on the committed blob.
* **The capture queue, after GO:** each captured line's `captured_already`
  cell names its skeleton and session 11, in the form sessions 8's lines use;
  `scripts/check_next_step.py` must pass. **A capture moves no census row by
  itself.**

## 7. The receipt-guard check, before line 7 (and lines 8 and 20)

Run inside the `messaging` phase, in this order; **every condition must hold**,
or lines 7, 8 and 20 are skipped (12 rows) and nothing more in Messaging is
opened:

1. **The badge** (load 1): `linkedin_new_messages()` reads
   `new_since_last_visit` EXACTLY 0 -- `None` (the badge not drawn) is not 0.
2. **The composer's list** (load 2, `linkedin_list_conversations(include_names=True)`,
   which opens nothing): `opened_a_conversation.opened` is False, and at least
   one row is rendered (re-read on the same page once the rows draw, as session
   6 did: session 2 read a list before it drew).
3. **The guard itself:** `threads.receipt_guard(threads.read_conversation_list(page),
   allow_unread=False, landed=<the composer's address>)` must PROCEED, with
   `unread_positions` empty. Session 8 refused here on one unread row -- the
   guard working as designed beside a badge of 0, which counts only
   new-since-last-visit.
4. **The conversation he named, resolved:** the rendered rows whose label
   carries a brother spelling (the key's positions 2, 3 and 6; whole word,
   casefolded, compared in this process, never printed) number 0 or exactly 1,
   and if 1 it is one-to-one and reads READ. More than one stops lines 7 and 8.
5. **Again, at zero loads, right before the thread** (on `/messaging/`, after
   the folder and search presses): no rendered row reads unread.
6. **The thread** (load 4), by the recorded id: `threads.landed_on_thread` true,
   and exactly one header title carrying a brother spelling. Otherwise the
   messaging phase stops, nothing pressed there.
7. **Right before line 7** (the GO's order), on the thread's own page, at zero
   loads: no rendered row of the list reads unread. Otherwise line 7 is skipped
   and nothing is pressed. Nothing is ever marked read: no conversation is
   opened while any rendered row reads unread, and no menu item is pressed.

**THE PRECONDITION IS HIS (X-0):** just before the session, he reads, or marks
as read, every unread conversation in his inbox. The guard cannot see a
placeholder row, an older conversation or a folder the default view does not
draw (its own `residue`); X-0 is what covers them.

## 8. STOP-ALL, and the stops

* **STOP-ALL, his to clear:** any sign-in wall, checkpoint or challenge (the
  harness's health check on every page); a failed restore (the messaging
  folder not back on the folder it read).
* **The phase stops, and the lead reads before more is spent:** an error
  envelope; an exception; a menu or dialog that does not close; a press that
  loads a document (counted by hand); a landing that is not the address asked
  where the address is a target (the thread; the organisation's first tab).
* **Refused before navigating:** a 41st load; a sixth search; a phase whose
  most loads would pass 40.

## 9. What GO needs

* **From him:** Chrome up on the dedicated profile (section 1), and his inbox
  read to 0 unread just before (X-0).
* **From the orchestrator:** `GO session 11`, and whether the lane may run
  `start_chrome.ps1` itself if 9224 is still down.
* **Nothing else:** no target he must name; nothing outward; every value is the
  lane's under D-4.

## 10. After GO, in the brief's order

1. Run L1 (section 4). 2. Save the captures (section 6). 3. Commit the
skeletons, the identity gate armed. 4. Update the capture queue per its
conventions. 5. Write the record below this prep. 6. `scripts/lane_ci.py push`,
then `wait <sha>`, the conclusion read by sha.

## 11. Instruments: section 103 candidates, and the disposable

**Candidates for INSTRUMENTS section 103**, each shown failing offline above
and entered only if it also holds live: the people gate (raw withheld when
another member is drawn); the click site's document guard (a press that loads
a document is counted by hand and stops); the close rule (a press that drew
nothing is not Escaped); the keyword veto scoped by class (shown failing first
on two generic words, then fixed).

**Disposable:** the scratch probes of this prep (a queue printer, a member-link
counter over kept raw captures, the offline page loader and its in-page
readers). The runner and its helpers are the session's; their copy stays in the
gitignored state.

---

## The GO, measured before obeying it

**The orchestrator's `GO session 11`**, on the operator's word at 22:31 IST that
his LinkedIn inbox is at 0 unread and that he is reachable for any checkpoint.
Its orders, beyond the brief: the flag at the start; the receipt guard
re-checked by the lane right before line 7, lines 7, 8 and 20 skipped if it is
not 0; never mark anything read; the flag deleted at the finish or the stop;
one report at the end, or at once on an early stop. And its HARD RULE: never
attach to, drive, raise or kill the operator's own Chrome; the dedicated
persistent profile only, as the precedent sessions did.

**Measured at 23:15 IST, before anything started:** one Chrome browser process
on the box, started 19:42 IST and NOT on the dedicated profile -- his own,
untouched by everything below; 9224 not listening. No precedent session used
his own Chrome (sections 1 and 0).

**Changed after READY, each before any load:**

* **`front_chrome.ps1` sends no input of any kind.** It had tapped ALT to win
  Windows' foreground lock, and that keystroke lands in whatever window has
  focus -- possibly his own Chrome. It now restores and switches to the
  dedicated window's handle only (`SwitchToThisWindow`, `SetForegroundWindow`),
  reports whether it became the foreground, and works around nothing
  (sha256 `8861d0962677`).
* **The re-check right before line 7** (section 7, item 7) is in the runner,
  at zero loads; the offline checks re-ran 32 of 32 and the three call sites
  still count one each (runner sha256 `9647d316c27f`).
* **The profile will be re-stamped on start:** it reads 155 (last opened
  2026-10-10), the installed Chrome is 158. An upgrade, which every Chrome
  update makes for any profile; the launch path that a re-stamp turns into a
  downgrade is refused by `profile_version.assert_no_downgrade`, and the
  cutover's profile copies stand. No new copy is taken.

---

## Live session 11, the run -- written as it runs

### The start, zero loads

* **23:17:47** the live-session flag raised by this lane.
* **23:17:56** the dedicated Chrome started BY THIS LANE with the main
  checkout's `scripts/start_chrome.ps1` (outcome `started`, Chrome 158; the
  script's re-stamp warning printed as expected: the profile read 155).
* **23:18:13** `os_check.ps1`: 9224 held by the dedicated profile's one browser
  process, started 23:17:56; **0 clients**; no profile lock. Its DevTools
  target list, read over HTTP with nothing attached: 2 pages, 0 on LinkedIn,
  1 new tab. His own Chrome (started 19:42) untouched.
* **23:18:33** the harness's `attach_check`: **PASS `[0, 1, 0]`**, restored.

### E1, line 5 (in-me-profile): loads 1 to 3

* **Loads 1-2 (23:18:58, 23:19:26): REFUSED by the harness's own self gate.**
  `_in_me` loads `/in/me/` and needs LinkedIn's `isSelfProfile=true` on the
  landing; it read `absent` twice and stopped before any press. **Diagnosed at
  zero loads**, in the dedicated profile's own browsing history (closed words
  only): both landings were a member path, `/in/<member>/`, with NO query at
  all. **So the redirect of LinkedIn's self alias no longer carries the
  parameter the package's self-assertion is built on** -- 2 of 2 today, where
  2026-09-02 measured it absent once and true once (VERIFIED, the history; the
  cause is LinkedIn's, UNVERIFIED). Everything anchored on it refuses his own
  profile today: `server._self_assertion_state`'s readers, `press.self_landing`
  (the press gate on his profile), and `linkedin_my_activity_items`'s
  authorship -- so the own-post reserve of the plan is unavailable this
  session. **A finding for the orchestrator** (an offline fix: another anchor
  for "his own profile").
* **Load 3 (23:23:11), by the runner's own load of `/in/me/`**, his own by two
  readings instead: the self alias's redirect to a member path, and **3
  owner-only controls visible in the top card**. Health clean (walled False, 0
  challenge terms). **10 other members drawn, so the raw was WITHHELD: skeleton
  only.** 35 `[aria-expanded]` in main; Recommendations, Services and
  Verifications 0 as section words. **D-4: the Experience section is NOT drawn
  on the first render** (as on session 8's capture), so his profile could not
  clear the organisation: E2 decides. **page-admin-precondition: 0 admin links
  on his profile.** The top card's opener was **Resources** (More not visible):
  pressed once, its menu read -- 5 items, **Save to PDF 1** -- closed by
  Escape.
* **Then a FALSE STOP, mine.** His photo (the top card's one image button) was
  pressed once and drew **no dialog** (0 on the open skeleton); meanwhile the
  page went on drawing its own lower sections -- sections 17 to 22, images 39
  to 53, the words Experience, Education and Show all newly drawn. The close
  check counted those page words as the press's and called the press not
  closed: `did_not_close`, and the phase stopped before 'Add custom button'
  and the Me menu. Nothing was committed: one press and Escapes, and the tab
  closed. **Fixed offline, red first:** a synthetic page that draws its own
  sections during an inert press -- red on the old check, green on the new
  (the words still drawn count as the opening's only if a popup holds them,
  and the page is let settle before each press); the menu that will not close
  still raises. Offline checks 33 of 33. The Me menu rides E2's page (the
  header is on every page).
* **The budget:** 3 loads where 1 was planned. By the plan's overflow rule,
  **line 36 and line 37 move to L2** (one row each); the rest of the order is
  unchanged.

### E2, D-4's fallback: load 4

* **Load 4 (23:27:32), his experience list, `/in/me/details/experience/`:**
  SERVED exact; health clean; 0 other members, so its raw is kept (his own
  page). **D-4 CLEARED:** 4 company links drawn, the organisation among none of
  them by id, by its name's slug or by its name (booleans in the page); the
  identity key had cleared it offline. **page-admin-precondition: the Me menu
  pressed once, 0 admin links while open**, closed by Escape -- with 0 on his
  profile, he administers no Page that either draws (N A1-N A9's precondition,
  first reading).
* **The window:** fronted at the start of E1; at E2's start Windows' foreground
  lock refused the switch (`not_fronted`; the script works nothing around), and
  it was fronted again at 23:28. From here every page records
  `document.visibilityState` -- Chrome marks a fully covered window hidden and
  throttles it.

### E3, the receipt guard: loads 5 and 6 -- lines 20, 8 and 7 SKIPPED

* **Load 5 (23:28:35), the badge off his feed:** `new_since_last_visit` 0.
* **Load 6 (23:28:58), the composer's list** (`linkedin_list_conversations`,
  names compared in this process only): nothing opened (0 message events, the
  composer's address); **10 rows rendered, 2 of them read UNREAD**; the
  conversation he named was resolved -- exactly one row carries a brother
  spelling, at position 3, one-to-one, read. **`threads.receipt_guard`
  refused** (`proceed` false, 2 unread positions). By the GO's order and the
  plan's rule, **lines 20, 8 and 7 are SKIPPED (12 rows)**; `/messaging/` was
  not opened, no thread was opened, nothing was pressed, nothing marked read.
  2 of the block's 4 loads spent.
* **What it says:** the operator's inbox read 0 unread for him at 22:31, and the
  badge reads 0, while the list's own markers draw 2 unread rows -- the shape
  session 8 met (a badge of 0 counts only what arrived since his last visit).
  Whether the 2 are new since 22:31 or are rows whose unread state his own
  reading did not clear is UNVERIFIED. The composer's skeleton with the 2 rows
  is kept (`messaging_list`): the second capture of LinkedIn's unread markup,
  and it corroborates the guard offline -- exactly 2 rows wear
  `msg-conversation-card__message-snippet--unread` and
  `msg-conversation-card__unread-count`, and they are rows 1 and 2, the two
  most recent conversations (VERIFIED, counts over the skeleton).
* **The orchestrator was told at 23:30**, with one decision for him: if he
  reads those 2 himself, the block re-runs at the end in 4 loads, the four
  1-row lines 31, 32, 33 and 36 moving to L2 to pay for it. Those four now
  run last.

### E4, his own pages: loads 7 to 13

| load | time | # | line | landing | raw | readings |
|---|---|---|---|---|---|---|
| 7 | 23:30:05 | 9 | `admit-in-me-details-featured` | **REDIRECTED to his profile root** (path depth 4 to 2) | withheld, 10 other members | no featured page served: nothing of the line's to capture |
| 8 | 23:30:33 | 23 | `sessions-surface` | redirected to a settings category page (depth 2 to 4) | S line | 13 settings links, 7 distinct paths, 2 to sign-in and security |
| 9 | 23:30:55 | 11 | `admit-mypreferences-d-unfollowed` | served exact | kept, 0 other members | -- |
| 10 | 23:31:23 | 35 | `admit-mypreferences-d-categories-ads` (+C-ADS) | served (same depth) | kept | 0 form controls in main; 12 settings links, 6 distinct paths |
| 11 | 23:31:54 | 1 | `admit-jobs-application-settings` (+O-JOB-APPLICATION-SETTINGS, +U-RESUME-MANAGER) | served exact | kept | 4 controls: 2 switches (both checked), 1 file input, 1 text area; no Save in main; the file input single, 3 of its accept tokens closed words |
| 12 | 23:32:22 | 30 | `admit-jobs-tracker-stage-clicked-apply` | served exact | kept | -- |
| 13 | 23:32:50 | 29 | `admit-explore-career-insights` | served exact | withheld, 3 other members | -- |

Every page: walled False, 0 challenge terms.

### The restart, and the resume

The machine rebooted at **23:48:57** (its boot time), and the Claude Code
process with it, after E4 had ended cleanly (`exit 0`, 23:32:55) and before the
lane's wake-up for the next phase arrived. The orchestrator measured the state
at 23:53 and ordered the RESUME; **disk agreed at 00:25**: ledger 13 of 40, 0
searches, the last load 23:32:50; no driver lock; the flag standing, this
lane's; no Chrome on the dedicated profile, 9224 silent. **00:26:05** the
dedicated Chrome relaunched by this lane, the same command and two flags (his
own Chrome, restarted 23:50:50, untouched); **00:26:14** `os_check.ps1`: 9224
held by it alone, 0 clients, 1 page, 0 on LinkedIn; **00:27:06**
`attach_check`: **PASS `[0, 1, 0]`**. Windows' foreground lock refused the
switch to its window, so `front_chrome.ps1` now raises the window to the top
of the z-order WITHOUT activating it (topmost, then not topmost,
`SWP_NOACTIVATE`; still no input of any kind), and every page after read
`document.visibilityState` "visible". From here every phase ran as a
foreground command, by the orchestrator's order.

### E5 to E9: loads 14 to 25

| load | time | # | line | landing | raw | readings |
|---|---|---|---|---|---|---|
| 14 | 00:28:15 | 2 | `admit-mynetwork-invitation-manager` | served exact | withheld, 21 other members | -- |
| 15 | 00:28:38 | 10 | `admit-mynetwork-invitation-manager-sent` | served exact | withheld, 5 | -- |
| 16 | 00:29:00 | 34 | `admit-mynetwork-network-manager-people-follow-following` | served exact | withheld, 20 | -- |
| 17 | 00:29:49 | 21 | `jobs-alerts-manager` (+O-JOB-ALERTS) | served exact | S line | 0 form controls in main; no alert-manager trigger by any of five names, so nothing pressed |
| 18 | 00:30:15 | 24 | `admit-jobs-search-results-keywords` | served exact | kept, 0 | generic role words (D-4) |
| 19-23 | 00:31:10-00:33:22 | 15, 25, 26, 27, 28 | the organisation's insights (headcount), about, events, life, products | each served, the numeric id answered by its named address; life redirected within its tab | withheld (3, 3, -, 4, 3); events kept, 0 | **the first tab names the organisation** (the phase's stop condition); each landed on its own tab |
| 24 | 00:34:07 | 4 | `article-composer` | served exact, **no draft redirect** | S line | 3 editors drawn; nothing typed |
| 25 | 00:34:39 | 6 | `sharebox-scheduled` (+U-POST-MEDIA) | served exact | S line | **U-POST-MEDIA first:** `Add media` pressed with the file chooser INTERCEPTED -- it fired once and was never answered; LinkedIn's media dialog drew 1 file input taking multiple files (image and video accept tokens), closed on Escape. **Then `Schedule post`:** its dialog read, then `View all scheduled posts`: **Scheduled posts, 0 items**; closed on Escape, the composer left as it was |

### E10, the feed: loads 26 to 28, and two stops of the runner's own

* **Load 26 (00:35:32): ABORTED, TimeoutError.** The header's search input was
  found visible, and the click's actionability wait timed out: nothing was
  dispatched. The phase lost its presses. **Fix, red first:** a click that
  cannot be made is now a reading -- the control reported not pressed, nothing
  Escaped -- with a focus of the search box as its fallback (the same
  disclosure: a search box shows its recent searches when focused). A covered
  control: TimeoutError on the old runner, "not pressed" on the new.
* **Load 27 (00:40:50): STOPPED, `did_not_close` -- a false stop.** The search
  box opened and closed; the first member's item menu opened -- its trigger
  `aria-expanded` "true", its menu container drawn with the link that carries
  the item's urn -- and Escape closed it (the container gone, the trigger
  "false": measured offline on the two kept skeletons). But the feed kept
  drawing itself -- 11 popup containers at the load, 16 open, 15 after Escape,
  new closed dialogs among them -- and the close check, counting page-wide,
  gave that growth to the press. The urn read was lost with the stop. **Fix,
  red first:** an opening is closed by ITS OWN evidence: a trigger whose
  `aria-expanded` flipped is closed when it reads its before-value again; any
  other opening is the set of popups that became visible on the press, held by
  reference (nothing is written into the page), closed when each is hidden or
  gone; nothing flipped and nothing appeared is nothing opened, and is not
  Escaped; nested openings close innermost first. A menu closed by Escape while
  an unrelated dialog appears: `did_not_close` on the old runner, closed on the
  new. **And one defect in my own check, found on the way:** `set_content`
  re-writes the same window, so a synthetic page's top-level `const` threw on
  its second write and left that page without handlers -- the case first read
  as the fix failing. The page script is wrapped now; 35 of 35 offline checks
  pass, both runner copies.
* **Load 28 (00:56:00): complete.** The search box opened its recent searches
  and closed (**N 95**). 6 items drew a control menu: 4 members' posts, **0
  Pages' posts**, 2 promoted. The first member's item menu opened, its urn
  read (1, written to gitignored state, never printed), closed on Escape. No
  Page post, so no Page urn. An ad's own control opened and closed; its menu
  drew no control named exactly "Hide or report this ad", so **N 200's dialog
  was not reached**.

### E11, E12: loads 29 and 30

* **Load 29 (00:57:10), a member's post by the urn its own menu carried**
  (`feed-item-permalink-menu`, the member half): served exact; its control menu
  opened -- **10 items: Not interested 1, Unfollow 0, Mute 0**, Embed 1 --
  closed. The Page half had no urn: the feed drew no Page post on either full
  render.
* **Load 30 (00:57:59), his own post** (session 2's post with comments, vetoed
  against his authorship-established rail): served exact, **but the permalink
  now draws LinkedIn's new markup** -- none of the classes session 8's capture
  of a permalink carried (0 `social-details`, 0 `comments-comment-box`, 0
  `feed-shared-control-menu`). So no reactions count control by name or class
  (line 13 not pressed), the one control-menu trigger found could not be
  clicked (line 19, C-B3-2, not pressed), and no comment-box icons
  (U-COMMENT-MEDIA not pressed). The skeleton is kept for the offline reading.

### E13, E14, E15: loads 31 to 36

* **Loads 31-33 (00:59:14-01:00:01), searches 1-3:** the people search with a
  generic role word (line 3): served; **no button named exactly "All filters"**
  -- the panel the line waits on was not opened. The first-degree search
  (line 22): served; no Industry or School button, and no All-filters button
  either. The content search with a generic technology hashtag (line 16):
  served, skeleton only (3 other members).
* **Load 34 (01:01:21), search 4: N 161 FIRED** through
  `linkedin_search_groups`, its first live fire: `ok` True, landed on the
  vertical, **9 result cards seen, 9 tried, 9 returned**, 0 skipped, 0 failed;
  the 9 group ids written to gitignored state, 9 of them not his.
* **Loads 35-36 (01:02:59, 01:03:41), the groups (line 37 SHED** -- the
  plan's overflow rule, after E1's and E10's extra loads): one non-member group
  from that search (line 17's candidate) served, and **it draws no control
  named exactly Join or Request to join** -- unclassified, its skeleton kept.
  His member group (the kept memberships reading; D-2 b): served; **no control
  named Invite, Invite connections or Invite members** (line 18, C-B5-3, not
  pressed, nothing typed); **its share box ("Start a public post") opened the
  group composer** -- 2 editors, Add media, More, Dismiss -- read and closed on
  Escape with nothing typed (line 38, C-B5-4, captured; D-1's rider).

### The messaging retry: loads 37 to 40 -- the guard PASSED

At the point reserved for it, after the orchestrator asked him to read the two
conversations. **Every condition of section 7 held:**

1. load 37 (01:05:23), the badge: 0;
2. load 38 (01:06:03), the composer's list: nothing opened, 10 rows rendered;
3. **the guard: proceeds, 0 unread rendered rows**;
4. the conversation he named: exactly one row, position 3, one-to-one, read;
5. on `/messaging/`, right before the thread: 0 unread rendered rows;
6. load 40, the thread by its recorded id: landed on it, its header the
   conversation he named;
7. **right before line 7, on the thread's page: 10 rendered rows, 0 unread.**

* **Load 39 (01:06:37), line 20 (`messaging-guarded`):** `/messaging/` landed
  in the conversation LinkedIn chose (redirected, depth 1 to 3), read; **no
  Message requests entry drawn**; the folder pill opened its menu -- Archived,
  Focused, Other, Spam -- **Archived pressed (a folder): 20 rows drawn; the
  folder pressed back to the one it read: restored, verified**; the message
  search box given one benign word, read, cleared.
* **Load 40 (01:07:39), line 8 (`msg-thread-footer`):** the first opened
  conversation on disk -- its footer 7 buttons, 1 editor (Send, Open Emoji
  Keyboard, Open GIF Keyboard, Maximize compose field, Open send options, and
  2 more), **0 suggestion chips, 0 video-meeting controls**.
* **Line 7 (C-B3-1), on the same load:** the active row's options menu --
  **8 items: Archive, Delete conversation, Manage settings, Mark as unread,
  Move to Other, Mute, Star**, and one more -- closed on Escape, still on the
  thread. Nothing pressed inside it; nothing marked read.

Lines 31, 32 and 33 (Learning) and 36 (premium matches) move to L2, as the
orchestrator ordered on a passing guard.

### The ledger, the flag, Chrome's end

**40 of 40 loads** (the ledger's own count, every door), **4 `/search/`
loads** -- 5 of 5 by the plan's count, which adds line 24's jobs keyword
search -- the closest two 22.1 s apart. By surface: feed 7, in 5, company 5,
messaging 4, search 4, mypreferences 3, jobs 3, mynetwork 3, groups 2, and one
each of article, preload, jobs-tracker and explore-career-insights. **No wall,
no checkpoint, no challenge on any page; no STOP-ALL; nothing saved, sent,
submitted, applied or confirmed.** The flag was lowered at **01:08:55**. At
01:09 the dedicated Chrome still served, 0 clients, 1 page, 0 on LinkedIn:
every run closed its own tab. It is left serving; his own Chrome was never
touched.

### What L1 captured, line by line

| # | line | rows | session 11 |
|---|---|---|---|
| 1 | `admit-jobs-application-settings` | 10 | CAPTURED (raw kept), its two riders' readings with it |
| 2 | `admit-mynetwork-invitation-manager` | 10 | CAPTURED (skeleton) |
| 3 | `search-people-labels` | 8 | NOT: no All-filters button by that name |
| 4 | `article-composer` | 6 | CAPTURED |
| 5 | `in-me-profile` | 4 | IN PART: the opener's menu (Save to PDF found); the photo button drew no dialog; Add custom button not reached |
| 6 | `sharebox-scheduled` | 4 | CAPTURED, U-POST-MEDIA with it |
| 7 | `C-B3-1` | 4 | CAPTURED |
| 8 | `msg-thread-footer` | 3 | CAPTURED |
| 9 | `admit-in-me-details-featured` | 3 | NOT SERVED: redirected to his profile root |
| 10 | `admit-mynetwork-invitation-manager-sent` | 3 | CAPTURED (skeleton) |
| 11 | `admit-mypreferences-d-unfollowed` | 3 | CAPTURED (raw kept) |
| 12 | `feed-item-permalink-menu` | 5 | IN PART: the member's post; no Page post on the feed |
| 13 | `own-post-reactions` | 2 | NOT: the new markup, no reactions control found |
| 14 | `feed-menus` | 2 | IN PART: N 95's search box; N 200's dialog not reached |
| 15 | company insights (headcount) | 2 | CAPTURED |
| 16 | `admit-search-results-content` | 2 | CAPTURED (skeleton) |
| 17 | `C-B5-1` | 2 | NOT: no Join control by that name |
| 18 | `C-B5-3` | 2 | NOT: no invite control by those names |
| 19 | `C-B3-2` | 2 | NOT: the menu trigger could not be clicked |
| 20 | `messaging-guarded` | 5 | CAPTURED |
| 21 | `jobs-alerts-manager` | 1 | IN PART: the page; no manager trigger |
| 22 | `search-people-first-degree` | 1 | NOT: no pills, no All filters |
| 23 | `sessions-surface` | 1 | CAPTURED |
| 24 | jobs keyword search | 1 | CAPTURED (raw kept) |
| 25-28 | company about, events, life, products | 4 | CAPTURED |
| 29 | career insights | 1 | CAPTURED (skeleton) |
| 30 | tracker, clicked apply | 1 | CAPTURED (raw kept) |
| 31-33 | Learning (three) | 3 | MOVED TO L2 (the messaging retry took their loads) |
| 34 | following | 1 | CAPTURED (skeleton) |
| 35 | ads (+C-ADS) | 1 | CAPTURED (raw kept) |
| 36 | premium matches | 1 | MOVED TO L2 |
| 37 | `C-B5-2` | 1 | SHED to L2 (the overflow rule) |
| 38 | `C-B5-4` | 1 | CAPTURED |

**The arithmetic (DERIVED from the table; 100 rows):** **63 rows on lines
captured whole** (22 lines); 12 on lines captured in part (lines 5, 12, 14,
21); 20 on lines not captured (lines 3, 9, 13, 17, 18, 19, 22); 5 on lines
moved or shed to L2 (31, 32, 33, 36, 37). **Siblings:** C-ADS (5) and
O-JOB-APPLICATION-SETTINGS (5) rode their pages, U-RESUME-MANAGER (J 70) the
application settings, U-POST-MEDIA (5, D-3) the sharebox: **16 sibling rows**;
O-JOB-ALERTS (3) only as a page with 0 controls in main; U-COMMENT-MEDIA (1)
and N 169 (after N 168) not; page-admin-precondition read (0 admin links on
his profile, 0 in his open Me menu). **N 161 fired.** A capture moves no
census row by itself, and no census row was moved by this lane: each captured
line's next step is its offline build. N 161's fire is the ledger owner's to
bank against its cell's bar.

### Findings for the orchestrator

1. **`/in/me/` no longer lands with `isSelfProfile`** (2 of 2 landings today,
   the profile's own history). Everything anchored on it refuses his own
   profile: `server._self_assertion_state`'s readers, `press.self_landing` (the
   press gate on his profile), `linkedin_my_activity_items`' authorship.
   **Recorded as a finding only: lane selfprofile26 owns the fix.** This session used
   two readings in its place, for a capture only: the self alias's redirect to
   a member path, and owner-only controls in the top card (3 visible).
2. `/in/me/details/featured/` redirects to his profile root: line 9 has no
   page to capture at that address.
3. His post's permalink draws the new markup now: every reader keyed on the
   older classes there (the reactions count, the comment box) is aimless on
   it; the skeleton of line 13's load is the input for the rebuild.
4. The people search draws no button named exactly "All filters", and the
   first-degree search no Industry or School button (lines 3 and 22): their
   skeletons are the input for the next press's aim.
5. The feed drew no Page post on two full renders: the Page half of line 12
   needs another source, or a later render.
6. The runner's three stops of its own -- a gone self marker, a page that
   hydrates during a press, a click that cannot be made -- each fixed red
   first; the close rule is now each opening's own evidence.

### Instruments: section 103, harvested at the close

Each was shown failing offline and then held live through loads 28 to 40 (its
press closed by its own evidence every time, 0 false stops): **the click
site's document guard; the not-actionable reading; the close rule by the
opening's own evidence** (flipped `aria-expanded`, or the popups that
appeared, by reference); **the people gate** (raw withheld on the 11 S+R loads
that drew another member, kept on the 7 that drew none); **the keyword veto
scoped by class**. They stay in the runner, which stays in the lane's
gitignored state; none is a tracked module, so section 103 records them and
the next live lane takes the runner from there. **Disposable:** the probes,
patchers and summarisers of this session.

### The rows, one by one (100)

By the outcome of the queue line each row sits on (DERIVED from the line
table above and the queue's own `rows` column; a capture moves no row):

* **Captured (63):** J 71, J 72, J 73, P M1, P M12, P M2, P M3, P M4, P M5,
  P M6 (line 1); N 9, N 11, N 13, N 14, N 15, N 16, N 17, N 18, N 19, N 21
  (2); M C44, M C46, M C50, M C78, M C81, P L3 (4); M C14, M C15, M C16, M C17
  (6); M M26, M M27, M M29, M M31 (7); M M20, M M40, M M51 (8); N 6, N 10,
  N 12 (10); M C52, N 39, N 40 (11); J 113, J 114 (15); M C70, M C93 (16);
  M M7, M M8, M M9, M M28, M M34 (20); P N9 (23); J 16 (24); J 106 (25);
  J 165 (26); J 109 (27); J 111 (28); J 160 (29); J 52 (30); N 38 (34);
  P P15 (35); M C64 (38).
* **On a line captured in part (12):** N 76, P B3, P C8, P S4 (5: the
  opener's menu only); N 37, N 43, N 51, N 153, N 154 (12: the member's post
  only); N 95, N 200 (14: N 95's search box, not N 200's dialog); J 37 (21:
  the page, not the manager).
* **Not captured (17):** N 82, N 86, N 88, N 89, N 90, N 91, N 92, N 93 (3);
  M C33, M C35b (13); N 63, M C61 (17); N 168, M C69 (18); M C23, M C90 (19);
  N 26b (22).
* **Not served (3):** P G4, P G5, P S1 (9: the address lands on his profile
  root).
* **Moved to L2 (4):** J 152 (31), J 156 (32), J 154 (33), N 199 (36). **Shed
  to L2 (1):** N 163 (37).

**Fired:** N 161 (`linkedin_search_groups`, load 34), its first live fire.
**Siblings:** 16 rode their pages (P P10-P P14 on line 35; P M7, P M8, J 74,
J 75, J 76 on line 1; J 70 on line 1; M C3-M C7 on line 6); J 35, J 36 and
J 100 only as a page with no control in main; M C27 and N 169 not.

### The finding, recorded here as a finding only

**The `/in/me/` redirect no longer carries `isSelfProfile`** (section E1).
Lane selfprofile26 owns the fix; this record moves nothing on it.

### To session 12

1. **C-SRCH-1, first** (lane search26's spec, queued by this close-out at
   rank 105 of the capture queue, session 12): ONE classic jobs search, 1 load
   and 1 search -- does `/jobs/search/` still serve? It records the landed
   path (withheld), whether the classic deprecation banner is drawn, the
   shipped harvest's anchors and the alert switch's reading, and it decides
   the route policy and whether J 31's classic fire is still possible.
2. The lines moved or shed to L2: 31, 32, 33 (Learning), 36 (premium
   matches), 37 (C-B5-2, an approval-gated non-member group).
3. The lines this session could not aim, each to be READ OFFLINE FIRST on its
   new skeleton before another load is spent: 3 and 22 (the people search's
   filter controls), 13 and 19 (his post's reactions and control menu on the
   new markup), 17 and 18 (a group's join and invite controls), 14's N 200
   (the ad's own menu), 21's manager, 5's photo editor and custom button.
4. Line 12's Page half needs a Page post's urn the feed did not draw.
5. Line 9 needs an address that serves: an admission question, not a load.

### The close-out (2026-11-26, after the machine's second reboot)

The CLI exited at about 01:30 and the machine rebooted at about 08:57; the
orchestrator's RESUME of 09:03 ordered ZERO loads. **Disk agreed at 09:26**:
HEAD `4c62196`, nothing committed since the base; the queue and the harness
test modified, this record and `tests/fixtures/live11/` untracked; the lane's
gitignored state last written 01:07; no flag; 123 raw captures preserved by the
orchestrator in the main checkout's gitignored state. No page was loaded and no
browser was started in the close-out.

* **The tracked copies:** 48 skeletons in `tests/fixtures/live11/`, each
  through the harness's own `tracked_copy`; the runner's diagnostic skeletons
  (the not-closed states, the earlier feed loads) and the redirected featured
  page (a duplicate of his profile's) stayed in gitignored state.
  `LIVE_FIXTURE_COUNTS` in `tests/test_live_lane_session_2_harness.py` counts
  them (48), as its directory guard requires.
* **The capture queue:** 33 L1 lines' `captured_already` and `plan` cells
  written in the queue's own form; C-SRCH-1 added for session 12 (its needs
  cell a decision load, so J 31's own step is not read off it: J 31 is a BUILD
  row on master and the end-of-wave integration moves it).
  `scripts/check_next_step.py`: GREEN.
