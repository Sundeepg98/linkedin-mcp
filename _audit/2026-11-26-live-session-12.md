# Live session 12 -- the live lane's record, written as it runs

**2026-11-26. Lane `live-s12`, branch `live-s12`, base master `f4fa447`
(integration 5; master CI run 45846283301, success, on that sha). PHASE A,
OFFLINE: zero LinkedIn page loads, no browser started or attached, port 9224
untouched, the live-session flag never raised, nothing committed.** PHASE B
runs only on the orchestrator's GO, a `_TEAM_LEAD_GO.md` at this worktree's
root; its record continues below READY, in this file.

It runs under the lane standing rules (gitignored) and the plan,
`_audit/2026-11-26-session-12-plan.md` (on master `f4fa447`): section 2 (the
rules every load runs under), 3 (the ordered load list), 4 (fill and shed), 5
(STOP), 6 (the runner hand-off and READY), 7 (what needs him).

**Every person is named by ROLE. No name, slug, member id, urn, organisation,
newsletter, keyword value or absolute path is written here.** Evidence
classes: VERIFIED = measured by an instrument this lane ran (section 7 names
it); DERIVED = follows from verified facts by the step stated; ESTIMATED;
UNVERIFIED.

---

## 0. What disk said that the brief and the plan did not

1. **E12 cannot be cleared from any kept reading.** The plan's E12 takes "ONE
   newsletter his own subscriptions page already draws (a kept reading,
   gitignored), published by LinkedIn or by an organisation's Page, never by a
   person". The two kept captures of his subscriptions page (the main
   checkout's gitignored state, 2026-09-05 and 2026-09-20) draw the same five
   newsletters. Card by card (VERIFIED, counts only): **three** draw a person's
   profile link and a person's profile photo, so they are person-published;
   **two** draw no publisher at all -- no profile link, no Page link, no
   photo, only the title anchor's two paragraphs. The absence of a person is
   not the presence of an organisation, so no newsletter is cleared, and the
   runner's E12 phase refuses without a positive clearance (refusal 8, section
   2.3). This is the one decision for the orchestrator (section 9).
2. **C-RJ26-2's organisation comes off a measured capture.** Session 11's
   organisation draws no Products tab (readers-jobs26, section 4.5). Of the 68
   kept raw captures scanned, exactly ONE draws a company Page's Products tab:
   session 1's capture of a large organisation's Page (a five-digit employee
   figure; nine tabs drawn, `products` among them) (VERIFIED). It is the lane's
   value for E26 (L1-D4-NEUTRAL-READ-VALUES), cleared offline against the
   identity key (its slug and its name, as words and as whole phrases), and
   cleared again live on E5 against his experience entries. Its name is the
   Page's own heading as the new markup draws it: no `h1`; the one `main h2`
   whose slug is the Page's slug, and with which the page title begins.
3. **E5's read before GO, at zero loads** (the line's own condition;
   selfprofile26's method, session 11's shape key, LinkedIn path words only):
   * editor routes: the landing skeleton draws 4, the hydrated one (the photo
     press's open state) 13, of which **nine are three-segment**, the plan's
     count (VERIFIED). Matched by keyed shape: `edit/forms/education/new/`
     (P D11's add form), `edit/forms/certification/new/` (P D13),
     `edit/forms/project/new/` (P D15), `edit/forms/summary/new/` (E34's line)
     and four `edit/forms/position/<digits>/` (existing positions); one
     three-segment route (26 letters in 29 characters) matches no word of the
     closed list; two more are two-segment `edit/forms/<digits>/`. So P D11,
     P D13 and P D15 have their drawn add-form spellings before the load; the
     rest of P D11-P D23 and P D29 are left to E5's scroll pass and E18's
     Add-section surface;
   * **the photo control:** in the top card one `div[role=button]` wraps his
     photo and one link does; no `<button>` does (VERIFIED). E5 presses the
     role-button once, as the plan says ("only if exactly one BUTTON wraps
     it"); the link is never pressed (LINKS-ARE-NOT-DISCLOSURES);
   * **`Add custom button`** is drawn on neither skeleton (0 by keyed shape);
   * **skills:** neither skeleton draws any `/details/skills/` link, so E23's
     skill id rests on what E5's scroll pass draws live; none drawn sends E23
     to standby, by the plan's own rule.
4. **The pinned account ledger is empty.** The installed pin names the
   job pipeline's store; the store exists and holds 0 events -- no LinkedIn
   load on record, ever -- so the trailing 12 hours hold 0 and **40 are free**
   (VERIFIED, `budget.usage`, 21:16 IST).
5. **Two import hazards, closed before they could bite.** The job-pipeline
   skill ships its own `tests/` directory; it and this worktree's `tests` are
   both namespace packages, and the people gate imports
   `tests.test_fixtures_hold_only_synthetic_people` for its N1 slot reader. A
   `tests` resolved from the skill would make N1 withhold every page. So the
   runner never puts the skill on `sys.path`: it loads `jobpipe` by file
   location, and its `provenance` phase prints, as booleans, where each gate
   module came from -- all five where they must be (section 2.1).
6. **E18's landing is proven by structure alone (the lane's call).** Its
   composed address carries `isSelfProfile=true`. If LinkedIn keeps the query
   on its redirect, the url marker would echo the lane's own parameter, which
   proves nothing. So E18's landing must pass `self_profile`'s structural rule
   on its own (edit controls for the landed member, none for another member),
   and its member must be the slug E5 proved. It refuses only what the marker
   alone could have let through.
7. **E19 is skeleton only (the lane's call).** The plan's row reads S+R and
   "no contact value saved or printed". A raw of the contact-info overlay would
   save his contact values, so the stricter half binds: the skeleton, and
   closed label words.
8. **The start script** (`scripts/start_chrome.ps1`, unchanged since
   `27aa37e`) still passes exactly two flags, `--remote-debugging-port` and
   `--user-data-dir` (VERIFIED, read).
9. **E37 is replaced by queue line 24, his Open-to-Work editor** (the
   orchestrator's message of the evening: he runs session 12 tonight and is
   ATTENDED, so plan section 7, item 2 applies; 1 load, 11 rows: P B6,
   P I2-P I11). Its ruling, OPEN-TO-WORK-EDITOR-ATTENDED-ONLY: "a capture may
   press Edit ONLY in a session he attends; read the modal, close it, choose
   nothing, round-trip read of the OTW card before and after; STOP-ALL if the
   card changed." The census (`_audit/_slice-otw-census.md`, C3 and section 6)
   names the aim and the danger: Edit is the page's ONLY button labelled
   exactly `Edit`, inside the card's carousel item, and its action is two
   SetStates and then a ServerRequest named `saveAndFetchNextStep`, to be
   treated as a write until a supervised capture says otherwise. **The aim on
   session 11's keyed skeletons of his profile (VERIFIED, under its key):** the
   card's text, under one of LinkedIn's three audience words (the one the
   census read in September), drawn exactly once; its list item holding
   exactly ONE `button[aria-label="Edit"]`, the page's only one; both
   `Open to` buttons hydrated (`aria-expanded` drawn). The card's text carries
   his own preferences, places among them, so it crosses into the process only
   to be digested there, and is never printed or written.

## 1. The runner

| file | where | role |
|---|---|---|
| `runner_s12.py` | the main checkout's gitignored `_state/live-runner/s12/`, copied from `s11/` (30 files), as plan section 6 says | the session: 24 phases for section 3 (E37' among them), 9 for the standby, `flag_on`, `flag_off`, `provenance` |
| `gate_checks_s12.py` | beside it | section 6's red checks, run against `runner_s11` (red) and `runner_s12` (green) |
| `otw_checks_s12.py` | beside it | E37''s red checks: against `runner_s11` (red), `runner_s12` (green), and six mutants of `runner_s12`, each disabling ONE guard (its own check red) |
| `test_runner_s12_offline.py` | beside it | session 11's 35 checks, ported: the import, and the store, cache and self file redirected |
| `prepare_items.py`, `name_items.py` | beside it | section 3's items prepared and vetoed; the caller naming an item off a reading |
| `os_check.ps1`, `front_chrome.ps1` | beside it | session 11's, unchanged |
| `scripts/people_gate.py` | tracked, master `f4fa447` | PEOPLE-GATE v2, IMPORTED from this worktree, never copied |
| `scripts/_probe_live_lane_session_2.py` | tracked | imported: the session ledger, the driver lock, the counter around `BROWSER.goto`, skeletons, the health check |
| the job-pipeline skill's `jobpipe/track.py`, `jobpipe/budget.py` | user scope, installed | the ONE account ledger: `read_pin`, `open_store`, `Store.lock`/`append`/`events`, `call_refusal`, `usage`, `load_record` |

**WHAT CHANGED FROM SESSION 11'S RUNNER (plan section 6, items 1-6):**

1. lane `live-s12`, `LIVE_LANE_SESSION_DIR=live12`, its import root this
   worktree at `f4fa447`;
2. the self stand-in is gone: E5 lands through
   `server._goto_self_profile_asserted` and prints which signal answered;
   `self.json` is written only off a TRUE landing, marked proven, and the
   people gate's slug is read only from a proven one;
3. PEOPLE-GATE v2 in the plan's three lines: `import people_gate`; on EVERY
   page, right after `html = await page.content()`,
   `verdict = people_gate.judge(html, slug=_self_slug(), page_url=landed,
   page_key=key, own_cache=h.STATE / "people_gate_own.json")`;
   `raw = s_plus_r and others == 0 and verdict.keep_raw and
   verdict.covers(html)`; the line after prints the verdict's counts. The
   skeleton is written first, so a gate that raises still leaves it, and the
   raise stops the phase;
4. All filters, and the first-degree pills, are found page-wide (finding 0.3);
5. every phase refuses BEFORE ANY BROWSER CONTACT unless: its items are of
   their closed shapes and pass their vetoes; the attach environment is set;
   the flag stands and is this lane's (another lane's flag is STOP-ALL); the
   session ledger has room for its most loads and searches (the five counted
   across `/search/` and the three job searches); the pinned account ledger
   has room for its most loads; the OS facts show 9224 held by the dedicated
   profile's browser with no other client (otherwise STOP-ALL); the driver
   lock is free;
6. **the account meter**, a wrapper around `BROWSER.goto` OUTSIDE the
   harness's counter, so a shipped tool's own loads (E1's) pass it too: the
   session's own refusals first (the ceiling, the five searches, 20 s); then,
   under the store's lock, `budget.call_refusal(events, "live_census", None, 1,
   now)`; on None ONE of the ledger's LinkedIn call records (platform `linkedin`,
   `loads` 1, kind `live_census`, the capture key, no address) is appended, and only then
   is the load made. A spacing refusal waits the seconds it names, ONCE, then
   asks again; any other refusal stops the phase (a budget refusal sheds from
   the bottom of the plan, never waits). A press that loads a document is
   counted by hand in BOTH ledgers.

**ALSO, THE LANE'S OWN:** ONE click site, NO typing site (nothing is typed in
session 12, so session 11's `_type` is gone) and ONE `BROWSER.goto` site,
counted on the file's syntax tree (1, 0, 1); a press aim whose own words are a
publishing or committing word is never pressed (STOP-ALL); a commit sign (a
toast saying saved, sent, posted, and so on) after a press is STOP-ALL; the
article composer stops on any autosave word or on its address leaving
`/article/new/`, and presses Next only when its words are exactly `Next`; the
post editor on E9 must close to the post as it was, or STOP-ALL.

## 2. Shown offline, red first

### 2.1 Provenance (`runner_s12.py provenance`)

All five TRUE: the harness, the package and the people gate from this
worktree; the gate's slot reader (`tests.test_fixtures_hold_only_synthetic_people`)
from this worktree's `tests`; `jobpipe` from the installed skill. Importing
the runner wrote nothing.

### 2.2 Section 6's red checks (`gate_checks_s12.py`)

Each check drives the runner's REAL `load()` and its real counters around
`BROWSER.goto`, in a local headless Chromium with every request aborted, on
SYNTHETIC pages (every name synthetic); only the innermost navigation is a
fake that sets the page's content. The harness's writers, the session ledger,
the self file, the gate's cache, the flag and the account store all point at a
temp directory beside the file before anything runs, the store's redirection
asserted. The real store read 0 bytes before and after every run.

| check | `runner_s11` | `runner_s12` |
|---|---|---|
| R1, a foreign member urn in a payload, planted alone on a page of his own, withholds the raw | FAIL | PASS (R1 1) |
| R2, a foreign profile-display photo | FAIL | PASS (R2 1) |
| R3, a picture label naming someone | FAIL | PASS (R3 1) |
| R4, a link-less social-proof line | FAIL | PASS (R4 1) |
| R5, an events page by its address | FAIL | PASS (R5 1) |
| N1, a name in a profile-card slot | FAIL | PASS (N1 1) |
| until a page has taught the cache, his avatar alone on a server-driven page is withheld | FAIL | PASS (R2 1) |
| R6, the raw written is the string judged (its digest) | FAIL | PASS |
| R6, a string other than the one judged fails `covers` | FAIL | PASS |
| every load recorded in the pinned store BEFORE it is made | FAIL | PASS |
| a store holding 40 in the window refuses before navigating, and does not wait | FAIL | PASS |
| a spacing refusal waits the seconds it names ONCE, then records | FAIL | PASS |
| a second spacing refusal after the one wait refuses | FAIL | PASS |
| an unreadable store line refuses every load (fail closed) | FAIL | PASS |
| a pin that cannot be read, or no pin, refuses | FAIL | PASS |
| the phase pre-check refuses before any browser contact when the account ledger lacks room | FAIL | PASS |
| a press that loads a document is counted by hand in BOTH ledgers | FAIL | PASS |
| one click site, no typing site, one goto site | FAIL (1, 1, 1) | PASS (1, 0, 1) |
| CONTROL: his own clean page keeps its raw | PASS | PASS |
| CONTROL: L1, a foreign profile link, withholds | PASS | PASS (L1 1) |
| CONTROL: a clean page of his own keeps its raw once the cache is taught | PASS | PASS |
| CONTROL: an S line never keeps a raw | PASS | PASS |
| CONTROL: the pre-check refuses with no flag of this lane's | -- | PASS |

**Totals (VERIFIED, the final run, 21:50-21:52 IST):** `runner_s11`, 22
checks, 18 of 18 red-class FAIL, 4 controls pass; `runner_s12`, 23 of 23 pass.
Every planted rule fired exactly its own rule and no other.

### 2.3 The real entry point's refusals, each before any browser contact

1. a wrong session directory; 2. no attach environment; 3. no flag; 4. a
missing item; 5. a post that is not the kept one; 6. the kept post with no
re-proof this session; 7. E4 with no C-SRCH-1 reading; 8. a newsletter not
cleared; 9. a company tab before E5's employer check; 10. an unknown item; 11.
`own_pages` with no `--lines`. All eleven refused as named (VERIFIED); no flag
was raised and the real store stayed at 0 bytes.

### 2.4 Session 11's 35 checks

* the original file, unchanged, against `runner_s11`: **35 of 35 pass**;
* ported to `runner_s12` (the import, and the store, cache and self file
  redirected; no assertion changed): **35 of 35 pass**.

### 2.5 One defect of the lane's own, caught by the 35

The first port read 34 of 35: "a menu closed by Escape while an unrelated
dialog appears reads as closed" raised `did_not_close`. The lane had added to
`close_all` that a flipped trigger's NEW POPUPS must also be gone, which
re-opened session 11's live stop of load 27 (the feed drawing dialogs of its
own during a press). Reverted to session 11's rule -- a flipped trigger is
closed when it reads its before-value again -- and the 35 read 35 again.

### 2.6 E37', his Open-to-Work editor: red first (`otw_checks_s12.py`)

The REAL `otw_capture` (the press, the read, the close, the round trip) runs
on SYNTHETIC profiles in a local headless Chromium with every request
aborted; `BROWSER.session` is booby-trapped, so nothing can reach 9224. In the
fake editor every selectable control -- two radios, a checkbox, a select,
Next, Save, Delete from profile -- records a click, so "nothing selectable is
pressed" is MEASURED, not read off the code. The phase's guards are separate
functions, and each mutant disables ONE of them. The final run (22:05-22:08
IST, runner `9739fe153a1feb94...`):

| check | `runner_s11` | `runner_s12` | the mutant that disables its guard |
|---|---|---|---|
| V1 nothing selectable pressed; the editor read, closed by Escape and verified gone; the card unchanged | FAIL (no phase) | PASS | `reader` (a reader that presses a radio): FAIL |
| V2 an editor that ignores Escape closes by its own exact Dismiss, verified gone | FAIL | PASS | -- |
| V3 an editor that will not close is STOP-ALL, never reported closed | FAIL | PASS (`otw_editor_not_closed`) | `close` (no close, no verification): FAIL, the phase read "ok" |
| V4 the card changed across the press is STOP-ALL | FAIL | PASS (`otw_card_changed`) | `card` (the round trip compares nothing): FAIL, "ok" |
| V5 a save or confirm control drawn as pressed is STOP-ALL; nothing selectable pressed | FAIL | PASS (`save_drawn_pressed`) | `saved` (no such check): FAIL, "ok" |
| V8 a commit sign after the close is STOP-ALL | FAIL | PASS (`commit_sign`) | `toast` (no commit-sign check): FAIL, "ok" |
| V6 no Open-to-Work card drawn: nothing pressed | FAIL | PASS | -- |
| V7 an Edit outside the card: nothing pressed | FAIL | PASS (nothing clicked) | `aim` (the page's first Edit): FAIL, the outside Edit clicked |
| the real entry point refuses without `--attended`, before any browser contact | -- | PASS | -- |
| with `--attended`, it still refuses without E1's re-proof and E5's proven slug | -- | PASS | -- |

**Totals (VERIFIED):** `runner_s11` 0 of 8; `runner_s12` 10 of 10; six
mutants, each 0 of 1 on its own check, every one an assertion failing on an
"ok" outcome or a recorded click, none an error. The real store read 0 bytes
after the run; no flag was raised.

**What E37' does live** (`otw_editor`, `--attended` required): his profile
through the shipped self loader, the landing proven his and its member the
slug E5 proved, E1's re-proof established; the skeleton only. It waits for
`Open to` to gain `aria-expanded` (the census's hydration proof, 15 s at
most); reads the card (closed words and counts, its text a digest held in the
process only); presses the card's own `Edit` ONCE, only when exactly one is
visible inside the card's list item; reads the editor as it settles (controls
by kind and state, LinkedIn's own labels counted, the skeleton kept) and
presses NOTHING in it; closes it by Escape, else by its one exact `Dismiss`,
and verifies no modal is left; then reads the card again. STOP-ALL on a card
that changed, a save or confirm control drawn as pressed, a commit sign, a
`saveAndFetchNextStep` request fired by the close, or an editor that will not
close. It records how many requests the Edit press fired and whether one was
`saveAndFetchNextStep`, as evidence for the census's open question.

## 3. The ledgers at READY

* **The account ledger** (BUDGET-ONE-ACCOUNT-40): the pinned store, 0 events,
  0 LinkedIn loads in the trailing 12 hours: **40 free**, so the plan does not
  shrink (plan section 6, "THE READY CHECK").
* **The session ledger** (`_state/live12/ledger.json`): not yet created; 0 of
  40 loads, 0 of 5 searches.

## 4. The box (`os_check.ps1`, 21:45 IST; OS facts only, no contact with Chrome)

Port 9224 NOT listening; 0 clients; 0 Chrome processes on the dedicated
profile (the other Chrome processes are his own and untouched); no profile
lock; no live-session flag. So the dedicated Chrome is not up, and 9224 is
down, as READY requires.

## 5. The items (no value written here)

Prepared by `prepare_items.py` into the session's gitignored
`_state/live12/items_prepared.json` (VERIFIED: every value of its closed shape;
the identity-key veto PASSED over every keyword item, singly and together;
every composed address admitted by `readonly.is_read_url`; the own-page and
standby addresses admitted):

| item | for | how chosen |
|---|---|---|
| `job_kw` | E2 | generic role words (session 11's cleared value) |
| `zero_kw` | E3, E4 | a nonsense token drawn at runtime: 14 lower-case consonants, so no word and no name |
| `people_kw` | E7 | a generic role word (session 11's) |
| `hashtag` | E16 | a generic technology hashtag (session 11's) |
| `org`, `org_name` | E25 | the large organisation session 11 cleared |
| `org2`, `org2_name` | E26 | 0.2's organisation |
| `activity` | E9 | session 2's post with comments, in his authorship-established rail (VERIFIED); E9 also needs it among E1's fresh keys |
| `newsletter` | E12 | NOT prepared: 0.1 |
| `skill`, `member_post`, `page_post`, `skill_index` | E23, E22, N 51, standby 2 | off this session's readings, named by the caller with `name_items.py` |
| `product`, `showcase` | standby 4, 5 | NOT prepared: no kept capture draws a LinkedIn-owned product or showcase address (0 of 73 raw captures, a wider scan than 0.2's 68, the previous live lane's state searched recursively); prepared only if those lines are reached |

## 6. Pins

Shortened here; the full values are in the session's gitignored
`_state/live12/pins.json` (a full sha or digest trips the tracked-file guards).

| what | value |
|---|---|
| master | `f4fa447`, this worktree's HEAD, tree clean; master CI run 45846283301 success on it |
| `scripts/people_gate.py`, sha256 | `6ff3afb732ed1546...` (blob `fd6bb743`, master's own) |
| `runner_s12.py`, sha256 | `9739fe153a1feb94...`, with E37' (the first READY's, before E37': `573c2e8f9f835732...`) |
| the harness, `scripts/_probe_live_lane_session_2.py`, sha256 | `a9f0cba2c0b995f8...` |
| `gate_checks_s12.py`, `test_runner_s12_offline.py`, `otw_checks_s12.py`, sha256 | `24ebd6fb2057e0a0...`, `088a5adae881a8e2...`, `c5281209cbc0dbb2...` |

## 7. Instruments

**Candidates for INSTRUMENTS section 110**, each shown failing offline (2.2),
to enter only if they also hold live: PEOPLE-GATE v2 wired into the runner's
`load()` (the string judged is the string written, every page judged, fail
closed until taught); the account meter around `BROWSER.goto` (recorded before
the load; one wait on spacing; refusals that never wait; fail closed on a pin
or store it cannot read); the hand count in both ledgers; the syntax-tree
count of click, typing and goto sites.

**Disposable:** `aim_probe.py`, `aim_probe_keyed.py`, `e5_preread.py` and the
newsletter and organisation-heading readers in the lane's scratch folder; none
was shown failing on a planted defect.

## 8. The commands for PHASE B, on GO

From this worktree's root, with `LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224
LINKEDIN_MIN_INTERVAL_S=20 LIVE_LANE_SESSION_DIR=live12` and the main
checkout's venv interpreter; `$R` is the runner, `$I` the prepared items, `$T`
the runtime items (both in `_state/live12/`):

    the main checkout's scripts/start_chrome.ps1 (its two flags only)
    os_check.ps1; $R flag_on; the harness's --only attach_check          (0 loads)
    $R reproof                                              E1
    $R srch_classic --items $I                              E2
    $R srch_zero_ai --items $I                              E3
    $R srch_zero_classic --items $I                         E4, only if E2 shows classic serving
    $R profile --items $I                                   E5 (+ $R experience --items $I if no experience drawn)
    $R recommendations; $R people_search --items $I; $R article          E6, E7, E8
    $R own_post --items $I; $R mynetwork; $R app_settings                E9, E10, E11
    $R newsletter ...                                       E12, only on the orchestrator's word (0.1)
    $R own_pages --lines privacy,contact_info_form,position_form         E13-E15
    $R content_search --items $I; $R connections; $R self_variant        E16, E17, E18-E19
    $R own_pages --lines verifications                      E20
    $R feed; name_items member_post; $R permalink_member --items $T      E21, E22 (if found)
    name_items skill; $R skill_form --items $T              E23 (if drawn)
    $R own_pages --lines job_prefs                          E24
    $R company_insights --items $I; $R company_products --items $I       E25, E26
    $R own_pages --lines volunteering,learning,learning_journey,learning_library,premium_matches   E27-E31
    $R sharebox_document                                    E32
    $R own_pages --lines invitation_manager,summary_form,secondary_language,services                E33-E36
    $R otw_editor --attended                                E37' (queue line 24, in E37's place; he attends)
    standby, in section 4's order, only on loads the plan frees; then the CLOSE

E37's own line (`following`, N 61, 1 row) joins the standby; and E37'
carries 11 rows, so in the shed order it goes AFTER the one-row lines, never
first (plan section 4: each shed costs its line's rows).

## The GO, measured before obeying it (22:10 IST)

`_TEAM_LEAD_GO.md` stood at this worktree's root, written 21:59 (its header
says 22:02 IST). Its calls: E12 SKIPPED (NEWSLETTER-PUBLISHER-UNPROVEN, the
lane's default: "E12 skipped: publisher unproven"); queue line 24 REPLACES
E37 "as you prepared it"; the lane's calls on E18 and E19 stand. Its order,
"IMMEDIATELY BEFORE LOAD 1, re-check READY. If any check fails, STOP and
report without loading", lists "the pins are unchanged: master f4fa447,
runner_s12.py, scripts/people_gate.py".

**MEASURED: the runner's pin is not the READY pin.** READY (21:58) pinned
`runner_s12.py` at `573c2e8f9f835732...`; preparing E37', which the
orchestrator's message of the same evening ordered ("Prepare that phase as
part of Phase A ... Report READY with it in place, then HOLD ... GO still
comes ONLY ... after I read your READY"), moved it to `9739fe153a1feb94...`.
Master `f4fa447` and `people_gate.py` `6ff3afb732ed1546...` are unchanged;
the flag is absent; the pinned ledger shows 40 free. By the GO's own rule the
lane did NOT load: no flag raised, no Chrome started, the GO file left in
place (deleting it is the ack of a start), and READY reported again with the
new pin, for a GO that names it.

## Lessons (for the orchestrator to harvest; the standing rules' 2026-11-26 line)

1. **A full sha or a 64-hex digest in a tracked record is blocked by the
   pre-write secret scan** (and full shas trip the identity guard): pin short
   in the record, the full values in gitignored state (`_state/live12/pins.json`).
2. **The identity gate run by hand reads the MAIN checkout's index.** In a
   worktree, git hands the hook `GIT_INDEX_FILE` at commit time; a manual run
   without it reports "examined NO staged content" even with a file staged.
   Run it with `GIT_INDEX_FILE` naming the worktree's own index to see it armed.
3. **A skill that ships its own `tests/` can shadow the worktree's `tests`**
   when both are namespace packages: load such a package by file location,
   never by putting its directory on `sys.path`, and print where each gate
   module came from.
4. **Session 11's 35 checks are a real regression net**: they caught a
   tightening of the close rule that would have re-opened session 11's live
   stop of load 27 (2.5).

## 9. What needs the orchestrator

1. **E12 (5 rows: M C101, M C80, M C82, N 55, N 56): DECIDED by the GO**,
   skipped as the lane's default proposed (NEWSLETTER-PUBLISHER-UNPROVEN):
   "E12 skipped: publisher unproven"; its load goes to standby in section 4's
   fill order.
2. **A GO that names the runner's new pin** (`9739fe153a1feb94...`, the
   runner with E37'): the GO on disk lists the READY pin of 21:58 among the
   checks that must hold immediately before load 1, and that pin moved when
   E37' was added (the GO section above).

---

## READY (first, 2026-11-26, 21:58 IST)

Runner `573c2e8f9f835732...`, before E37'; every other line as below.

## READY, with E37' in place (2026-11-26, 22:12 IST)

* the runner in place: `_state/live-runner/s12/runner_s12.py`, sha256
  `9739fe153a1feb94...`, E37' (queue line 24, `otw_editor --attended`) in
  E37's place;
* PEOPLE-GATE v2 wired and its red checks shown, on THIS runner: 18 of 18 red
  on `runner_s11`, 23 of 23 green on `runner_s12`; session 11's 35 green on
  both;
* E37''s own red checks (2.6): 0 of 8 on `runner_s11`, 10 of 10 on
  `runner_s12`, and each of six mutants red on its own check -- nothing
  selectable pressed, the editor closed and verified gone, STOP-ALL on a save
  or confirm control drawn as pressed, on a commit sign and on a changed card;
* the pinned account ledger read: 0 LinkedIn loads in the trailing 12 hours,
  **40 free**;
* `os_check`: 9224 down, no client, no Chrome on the dedicated profile;
* section 3's items prepared and vetoed by the identity key; E12 skipped by
  the GO;
* the pre-commit identity gate ARMED in this worktree: this record, staged and
  run with the worktree's own index, "examined 1 staged file(s) against 226
  spellings; 0 hits"; unstaged again, nothing committed;
* pins: master `f4fa447`, `people_gate.py` `6ff3afb732ed1546...`,
  `runner_s12.py` `9739fe153a1feb94...` (full values in
  `_state/live12/pins.json`).

HOLD: PHASE B starts only on a GO that names this runner's pin.

---

## Live session 12, the run -- written as it runs

### The GO, and the start (zero loads)

* **22:14** the orchestrator REISSUED the GO naming runner `9739fe153a1feb94...`
  (it replaced the 21:59 GO the lane had refused; section "The GO, measured
  before obeying it"). Its calls: E12 skipped (NEWSLETTER-PUBLISHER-UNPROVEN);
  E37' replaces E37; the lane's E18 and E19 calls stand.
* **22:15:35** the GO file deleted as the ack. **22:16** the pre-load re-check,
  every item as the GO names it: master `f4fa447`; `runner_s12.py`
  `9739fe153a1feb94...`; `people_gate.py` `6ff3afb732ed1546...`; 9224 down, 0
  clients, no Chrome on the dedicated profile, no lock; the flag absent; the
  pinned ledger 0 used, **40 free**.
* **22:16:50** the dedicated Chrome started BY THIS LANE with the main
  checkout's `scripts/start_chrome.ps1` (outcome `started`, Chrome 158, its two
  flags only). **22:18** `os_check`: 9224 held by the dedicated profile's one
  browser process, 0 clients, no lock. His own Chrome untouched.
* **22:18:34** the live-session flag raised by this lane. **attach_check:
  PASS `[0, 1, 0]`**, restored, 0 loads.

### E1, the re-proof: loads 1 and 2 -- REFUSED

* `linkedin_my_activity_items`, in-process (22:19:17-22:19:43): **refused
  `self_assertion_unreadable` after 2 loads**; its evidence (closed words and
  integers): url marker absent, `landed_on_member_path` false, structure not
  read, no self signal. Each load recorded in the pinned ledger before it was
  made.
* **Diagnosed at zero loads** in the dedicated profile's own browsing history
  (a copy, closed classes only): 22:19:19 `/in/me/`, then 22:19:20 `/in/<member>/`
  as a SEPARATE link-type visit with no redirect qualifier, then 22:19:41
  `/in/me/` again. No wall, no checkpoint, no challenge path. So LinkedIn now
  serves `/in/me/` as its own document and rewrites the address to his member
  path client-side, about a second later; the shipped loader reads the
  landing before the rewrite, sees the self alias, and refuses -- fail closed,
  as designed (UNVERIFIED beyond the history: the second load's rewrite is not
  in the copy). A finding for the self-profile owner (selfprofile26's rule
  holds; the loader's moment of reading does not).
* **By plan section 5 ("The re-proof decides a block")**: E5's presses, E18
  and E19 are skipped, and with them every line resting on the same proof:
  E37' (his Open-to-Work Edit is NOT pressed tonight), E9 (it needs E1's fresh
  keys), E23 (it needs E5's reading). E5's own load is not spent: the same
  loader would refuse again. No slug is proven, so people gate v2 learns no
  identity and every raw is withheld this session (fail closed); skeletons
  serve. D-4 for E25 and E26 moves to his experience list (one reserve load).
  The lead was told at 22:21.

### E2 to E17: loads 3 to 14 (every load recorded in the pinned ledger before it was made; every page walled False, 0 challenge terms)

| load | IST | E | line | landing | what it read (closed words, counts) |
|---|---|---|---|---|---|
| 3 | 22:23 | E2 | `C-SRCH-1`, the decision load | **REDIRECTED to the AI route** (same depth, another address) | route `ai_search`, the query kept; 25 AI cards; NO classic list, NO deprecation banner, 0 classic anchors harvested, no alert switch. **The classic jobs search no longer serves.** So E4 is SKIPPED and its load and search go to standby line 1 |
| 4 | 22:23 | E3 | `C-SRCH-0b`, the AI route's zero | served exact | **a nonsense token draws 18 results** (18 AI cards, "18 results" drawn), no empty state among the candidates: the semantic search returns near matches, so its no-results wording is not reachable by a nonsense token |
| -- | -- | E4 | `C-SRCH-0a` | not loaded | skipped by E2's reading (the runner's veto) |
| -- | -- | E5 | `in-me-profile` | not loaded | the re-proof's block (E1 above) |
| 5 | 22:24 | E6 | his recommendations page | served exact | no control named exactly `Received` or `Given` (tab or button): nothing pressed; the skeleton keeps the tabs' form |
| 6 | 22:24 | E7 | `search-people-labels` | served exact | All filters found page-wide, exactly one, PRESSED: its panel opened (the open skeleton gains `Show results`, `Reset` and 11 checkboxes) but is drawn OUTSIDE any dialog, so the close rule read `nothing_opened` and pressed no Escape; nothing chosen; the panel closed with the tab |
| 7 | 22:26 | E8 | `C-MSG26-4` + `article-composer` | served exact, no draft redirect | the onboarding dismissed (0 visible after); the author toggle opened and closed by Escape; **Manage: 8 items**, closed by Escape (M C47's drafts link is in its open skeleton); **the embed control: its dialog drawn** (`Cancel` drawn), closed by Escape; **Next: draws nothing on the empty article** (no dialog, no Cancel, no Back: the publish settings are not reachable empty); no draft appeared, the status still `Draft`, no autosave or publishing sign |
| -- | -- | E9 | his own post | not loaded | its veto: E1's fresh keys are absent |
| 8 | 22:27 | E10 | `/mynetwork/` | redirected one level deeper | the pending-invitation badge 0 on landing and after settling; `Show all` 6, `Manage my network` 1; links to the grow (4), network-manager (3), connections (1), invitation-manager (1) and catch-up (1) views; no contacts or import-contacts link drawn |
| 9 | 22:28 | E11 | `C-RJ26-3`, his application settings | served exact | the first resume card's options menu: **2 items**, closed by Escape, nothing chosen (neither is exactly `Download` or `Delete`; the open skeleton keeps them); raw WITHHELD by v2 (R1: with no proven slug his own ids count as another's) |
| -- | -- | E12 | a newsletter | not loaded | the GO: "E12 skipped: publisher unproven" |
| 10 | 22:28 | E13 | his privacy settings (+ the C-PRIVACY riders) | served, same depth, another address | 0 form controls in `main`; 15 settings links, 9 distinct paths, 2 to sign-in and security |
| 11 | 22:29 | E14 | the contact-info form | **REDIRECTED to his profile root** (depth 6 to 2) | no editor drawn: no dialog, no Save, no Cancel; raw withheld (11 other members) |
| 12 | 22:29 | E15 | the new-position form | **REDIRECTED to his profile root** (depth 6 to 2) | the same: no editor drawn |
| 13 | 22:30 | E16 | `C-MSG26-1` + the content search | served exact | All filters pressed, its panel drawn outside any dialog again; **the facets drawn: Posted by, Date posted, Sort by, Content type, From member, From company, Mentioning member, Mentioning company, Author industry, Author company -- NO group facet** (M C70's question answered: a group page's own search is next); N 59/N 60: 0 hashtag-feed links, 0 exact `Follow` buttons |
| 14 | 22:30 | E17 | his connections | served exact | no sort control by its closed names, no `Talks about` or `Open to` button: nothing pressed |
| -- | -- | E18, E19 | the self-profile variant, the contact overlay | not loaded | the re-proof's block |

### E20 to E36: loads 15 to 31

| load | IST | E | line | landing | what it read |
|---|---|---|---|---|---|
| 15 | 22:31 | E20 | his verifications page | served exact | 1 control; 8 settings links, 7 distinct; no two-step link followed |
| 16 | 22:32 | E21 | `feed-menus` | served exact | **the left rail draws `/my-items/saved-posts/` once** (M C36, M C37: the spelling was NAMED only before; now drawn); 7 items with a control menu; **the first member's item menu draws `Unfollow`** (a followed author), `Not interested`, and its urn (written to gitignored state, never printed); one Page item's menu read for its urn (N 51's standby); each closed by Escape |
| 17 | 22:32 | E22 | `feed-item-permalink-menu`, the member half | served exact | that post's own control menu: 10 items, `Not interested` 1, `Embed` 1, **`Unfollow` 0, `Mute` 0** -- the same author's item menu on the feed draws Unfollow, its permalink's does not (N 37, N 43) |
| -- | -- | E23 | a skill's edit form | not loaded | it needs E5's reading |
| 18 | 22:33 | E24 | his job-seeking preferences | served, same depth, another address | 0 form controls in `main`; 1 other member drawn (raw withheld) |
| 19 | 22:33 | -- | D-4's fallback: his experience list (a reserve load) | served exact | **D-4 CLEARED for both organisations**: neither among his entries, by id, by its name's slug or by its name (booleans in the page) |
| 20 | 22:34 | E25 | `C-RJ26-1`, the insights headcount view | served on its named address | the first tab names the organisation; landed on insights; **the job-openings card's Functions dropdown opened: 11 items**, closed by Escape, nothing chosen (its open skeleton holds the options, J 114) |
| 21 | 22:34 | E26 | `C-RJ26-2`, the second organisation's Products tab | served exact | the first tab names the organisation; eight tabs drawn, products among them; **9 product links in `main`** (J 111's capture) |
| 22 | 22:35 | E27 | his volunteering page, the bare spelling | **REDIRECTED to his profile root** (depth 5 to 2) | VOLUNTEERING-BARE-SPELLING-FIRST's reopener met: the bare spelling does not land |
| 23-26 | 22:35-22:37 | E28-E31 | Learning, career journey, my library; premium matches | served (learning exact; journey same depth; library one level deeper; matches exact) | skeletons only |
| 27 | 22:37 | E32 | `U-POST-DOCUMENT` | served exact | More opened: **`Add a document` drawn behind it, exactly one, visible** (M C5); NOT pressed -- the runner's closed name set held that name twice (once with a trailing space) and an accessible name is trimmed, so the one control counted twice and the exactly-one rule refused: the lane's own defect, no act; the file chooser's input is not measured |
| 28 | 22:38 | E33 | his invitation manager (the badge is the read's cost, RECEIVED-BADGE-IS-THE-READS-COST) | redirected one level deeper | the type words drawn: `Received` 4, `Sent` 4; no People, Events, Pages or Newsletters pill (N 14) |
| 29-31 | 22:39 | E34-E36 | the summary form; the secondary-language page; the services page | **each REDIRECTED to his profile root** | no form drawn |
| -- | -- | E37' | his Open-to-Work editor | not loaded | the re-proof's block: his Edit was not pressed |

**A pattern across E14, E15, E27, E34, E35, E36 (VERIFIED, six of six):** every
`/in/me/edit/...`, `/in/me/opportunities/...` and `/in/me/edit/secondary-language/`
address lands on his profile root and draws no form, while `/in/me/details/...`
(E6, D-4's list) serves exact. With E1's finding, LinkedIn's handling of the
self alias changed: the sub-surfaces are no longer served under it.

### The standby (plan section 4's order): loads 32 to 39

E4, E5, E9, E12, E18, E19, E23 and E37' freed eight loads; the lane spent
them in section 4's order and left the last load unspent, so a press counted
by hand could never pass 40.

| load | IST | standby | line | landing | what it read |
|---|---|---|---|---|---|
| 32 | 22:40 | 1 | `search-people-first-degree` (search 5, E4's freed one) | served exact | no Industry or School pill; All filters' panel opened outside any dialog again (N 26b's input) |
| -- | -- | 2 | `admit-in-me-skill-insights-skill` | not loaded | it needs E5's index |
| 33 | 22:41 | 3 | his Premium account page | served exact | skeleton only (a billing page); 0 form controls in `main` |
| -- | -- | 4, 5 | LinkedIn's own product and showcase pages | not loaded | no such address on disk (0 of 73 raw captures) |
| 34 | 22:41 | 6 | `C-P26-1`, his key skills | served, same depth | no `Show all` button in `main`: nothing pressed |
| 35 | 22:42 | 7 | `C-JMN-2`, the tracker's saved stage | served exact | **the `Date posted` pill opened**, closed by Escape, nothing chosen |
| 36 | 22:42 | 8 | `comments-metric-spelling` | served exact | **the metric selector opened** and closed by Escape; only IMPRESSIONS drawn as a metricType link (M C39's options are in its open skeleton) |
| 37 | 22:43 | 9 | `creator-hub-on-the-dashboard` | **REDIRECTED two levels deeper** | the hub is no longer served at `/dashboard/` |
| 38 | 22:43 | 10 | `C-I3-1`, his notifications (NOTIFICATIONS-UNREAD-SPEND: it clears his own unread badge) | served exact | the card reader found 0 `article` cards: the link-sharing count is not taken in-page; the skeleton is the input |
| 39 | 22:44 | N 51 | `feed-item-permalink-menu`, the Page half | served exact | the Page post's own menu: 10 items, Not interested and Embed, no Unfollow, no Mute |

E37's own line (`following`, N 61) was not reached: the last load was kept unspent.

### The ledgers, the flag, Chrome's end

**39 of 40 loads** by the session ledger, every door; **5 of 5 searches**
(two job searches, three `/search/` loads); the closest two loads 22.3 s
apart. **The pinned account ledger: 39 records, all this session's, each made
before its load; 39 LinkedIn loads in the trailing 12 hours** (BUDGET-ONE-
ACCOUNT-40, shared with the job pipeline, which made none). **No wall, no
checkpoint, no challenge on any page; no STOP-ALL; nothing saved, sent,
submitted, applied, followed, reacted to or confirmed; no conversation
opened.** The flag lowered at **22:45:09**, this lane's. At 22:45 the dedicated
Chrome still served on 9224, 0 clients, its one browser process; it is left
serving. His own Chrome was never touched.

### What session 12 captured, by line (a capture moves no row by itself)

* **CAPTURED, the press made and closed:** E7 (All filters' panel), E8 (the
  onboarding, the author toggle, Manage, the embed dialog), E11 (the resume
  card's menu), E16 (All filters' facets: no group facet), E21 (a followed
  author's item menu, the saved-items link, a Page item's menu), E22 and N 51
  (each permalink's own menu), E25 (the Functions dropdown), standby 7 (the
  Date posted pill), standby 8 (the metric selector), standby 1 (All filters).
* **CAPTURED, a page read, no press asked:** E2, E3, E10, E13, E20, E24, E26
  (9 product links), E28-E31, E33, standby 3, the experience list (D-4).
* **SERVED, but its control not drawn by name, so nothing pressed:** E6 (the
  tabs), E17 (sort and filters), standby 6 (Show all), standby 10 (the card
  reader).
* **REDIRECTED, no page to capture at the address:** E14, E15, E27, E34, E35,
  E36 (each to his profile root), standby 9 (`/dashboard/`).
* **DRAWN, NOT PRESSED (the lane's own defect):** E32's `Add a document`.
* **NOT LOADED:** E4 (E2's route decision), E5, E9, E18, E19, E23, E37' (the
  re-proof's block), E12 (the GO), standby 2, 4, 5, and `following`.

### Findings for the orchestrator

1. **The self alias changed.** `/in/me/` is served as its own document and its
   address rewritten client-side about a second later; the shipped loader reads
   before the rewrite and refuses (`self_assertion_unreadable`, 2 of 2). And
   every `/in/me/edit/...` and `/in/me/opportunities/...` address lands on his
   profile root with no form (6 of 6), while `/in/me/details/...` serves. M
   C41's re-proof failed tonight, and every press resting on his profile with
   it. The self-profile owner's question.
2. **The classic jobs search no longer serves** (C-SRCH-1, load 3): its
   address redirects to the AI route, with no classic list and no banner. This
   is the trigger RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE waits on.
3. **The AI route has no reachable zero for a nonsense token** (18 results):
   C-SRCH-0b's no-results wording needs another way in.
4. **All filters' panel is drawn outside any dialog** on both people searches
   and the content search: the press opens it, the runner's close rule cannot
   see it. Its facets on the content search hold no group facet (M C70).
5. **Next draws nothing on an empty article** (M C44, M C78 not reached that
   way); the embed dialog and Manage are drawn.
6. **On the feed a followed author's item menu draws Unfollow; on that post's
   permalink the menu does not** (N 37, N 43). The left rail draws
   `/my-items/saved-posts/` (M C36, M C37).
7. **`/dashboard/` redirects** (P L7's surface moved).

### The rows

**No census row moved by this lane.** A capture moves no row by itself, and
every line tonight was a capture. Two rows' grounds changed and are reported
rather than moved:

* **RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE's trigger is MET** (finding 2):
  "when a capture shows classic no longer serves, each returns to GAP with its
  next step on the AI route and a reopener." The set it governs, "the 21
  COVERED-PROVEN rows on the classic page (search26 4.5)" plus J 31, is not
  enumerated anywhere in this repository (the ruling's record and the census
  cells name none; the plan counted them "UNVERIFIED here"), so the lane moved
  none: the move is the ledger owner's, on that list, citing load 3.
* **M C41** (COVERED-PROVEN) failed its re-proof (finding 1): left as it is, a
  demotion being no cell's bar the lane holds.

### The close-out

* **Preserved before anything else:** the session's state, 129 files,
  byte-identical, in the main checkout's gitignored
  `_state/preserved/live12-2026-11-26/`.
* **Tracked:** 47 skeletons in `tests/fixtures/live12/`, each through the
  harness's own `tracked_copy` (strict ASCII, no keyed shape); the six that
  redirected to his profile root stay in gitignored state (duplicates of his
  profile). `LIVE_FIXTURE_COUNTS` counts them (47).
* **The capture queue:** 37 `captured_already` cells written in the queue's own
  form, each line asserted by rank and surface id, no other cell changed;
  `scripts/check_next_step.py` GREEN.
* **INSTRUMENTS section 110** registers the runner's instruments (110.1-110.5).
* **For the next live session:** E32's name set carries `Add a document`
  twice; the fix (one name, and distinct elements counted once) belongs in the
  runner before its next load, red first. And the close rule needs the shape
  of a panel drawn outside a dialog.

### Gates (local, each under the 2-minute cap, serially, the flag down)

| gate | result |
|---|---|
| the harness's fixture guards (`tests/test_live_lane_session_2_harness.py -k "fixture or counted"`) | 16 passed (`live12`: 47 counted) |
| `tests/test_fixtures_hold_only_synthetic_people.py --people-guard-scope=changed` | 66 passed, 17 skipped: the 47 changed fixtures read; the corpus-wide tests are CI's |
| `scripts/check_next_step.py` | GREEN: every GAP row once (513), every source resolving, the queue agreeing |
| `scripts/census_completion.py --check` | every headline figure matches its pin (no row moved, no pin moved) |
| the three derived views | `--write`, then `--check` clean, twice |
| `tests/test_the_audit_index_is_derived.py`; `tests/test_the_register_numbers_are_unique.py` | 33 passed; 6 passed |
| `tests/test_a_correction_is_findable_from_the_claim.py` | 15 passed |
| the pre-commit identity gate | at the commit, its output below |

NOT RUN locally, by the standing rules: the full suite (lane CI runs it on
`ci/live-s12`).

**Lane CI, first run** (45867937888, the close-out's head `0796e7a`): failure,
1 test -- `tests/test_an_asserted_name_resolves.py::test_no_new_asserted_name_is_absent`.
This record and INSTRUMENTS section 110 named the pinned ledger's record type
in backticks, which the checker reads as a TOOL name resolving nowhere; it is a
record type, not a tool. Fixed at the cause: both sentences reworded to "the
ledger's LinkedIn call records", the checker untouched. The same test ran red
locally on the unfixed tree first, then green.
