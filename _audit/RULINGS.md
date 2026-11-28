# THE RULINGS REGISTER -- one entry per RULING, not per document

**GENERATED. Do not hand-edit.** `scripts/build_rulings_index.py --write` rebuilds it; `--check` fails when it drifts, when a registered ruling stops resolving in the corpus, or when a `RULED:` declaration is neither claimed nor triaged.

`_audit/INDEX.md` answers *what did wave X report* and *what overtook this claim*. It cannot answer **what has been ruled about X**, and this file is that key. The receipt for why it exists is four payments for one answer -- see `_audit/2026-09-21-what-was-ruled.md`.

**WHERE and WHEN are DERIVED** from the corpus at the SHA this runs against; **CLAIM, BINDS and ALIASES are JUDGED** and hand-authored. Section headings are printed and line numbers are not, because `CANONICAL-RULING-ID` rules that a citation resolves to a symbol.

**THIS REGISTER IS NOT THE CORPUS AND DOES NOT CLAIM TO BE COMPLETE.** Read section 4 before concluding a question is unruled: the scan that keeps it honest reads ONE marker, and the ruling that caused this file to be written does not carry it.

    rulings registered       216
    documents scanned        317
    RULED: declarations      202 claimed, 7 triaged, 0 unclaimed

---

## 1. THE REGISTER, BY WHAT IT BINDS

Scan the CLAIM column against your question. Every claim is a paraphrase written to be matched; the ARGUMENT is in the document, under the section named.

### address family

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `DO-NOT-OPEN-MESSAGING` | SUPERSEDED 2026-09-23 by WRITE-CLASS-B: the operator ruled that messaging MAY be opened. Original: Do not open messaging. Opening it opens a surface whose cost lands on other people, and the row is DEFERRED BY RULING. | /messaging/ | 2026-08-31 | [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md)<br>*#9 send a message / InMail -- `linkedin_send_message`. REFUSING, and now DEFERRED BY RULING.* |
| `ONE-NAMED-SETTINGS-PAGE-AT-A-TIME` | ONE NAMED settings page below `/mypreferences/d/` is admitted, one at a time. | /mypreferences/d/ | 2026-08-31 | [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md)<br>*#6 change a setting -- `linkedin_update_setting`. BUILT, NOT CAPTURED.* |
| `PERMALINK-READ-IS-ALLOWED` | `/feed/update/<urn>/` is allowed and an ordinary read of a post at its permalink is permitted; reacting rests on the same permalink ruling. | /feed/update/<urn>/ | 2026-08-31 | [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md)<br>*#2 comment on an item -- `linkedin_comment_on_item`. STILL REFUSING.* |
| `PROFILE-EDITOR-ADDRESSES-ALLOWED` | `/in/<member>/edit/` and the profile editors are allowed. | the profile editor surfaces | 2026-08-31 | [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md)<br>*#4 edit a profile field -- `linkedin_update_profile_field`. BUILT, NOT CAPTURED.* |
| `MUST-STAY-REFUSED-ENTRIES-COME-OUT` | `MUST_STAY_REFUSED` listing `groups` and `events` is wrong and must come out, or move to a class the admission does not reach. | the guard's must-stay-refused table | 2026-09-19 | [2026-09-19-search-admission-condition-2-amended.md](2026-09-19-search-admission-condition-2-amended.md)<br>*`MUST_STAY_REFUSED` LISTING `groups` AND `events` IS WRONG AND MUST COME OUT* |
| `SEARCH-ADMISSION-APPROVED-FIVE-CONDITIONS` | The search-results admission is APPROVED IN PRINCIPLE under five binding conditions, one of which is that nothing is FIRED from that surface. Condition 1's name-free shaper AMENDED 2026-09-24 by NAMES-AT-RUNTIME for runtime returns. | /search/results/ | 2026-09-19 | [2026-09-19-two-census-conventions-ruled.md](2026-09-19-two-census-conventions-ruled.md)<br>*RULED: APPROVED IN PRINCIPLE. FIVE CONDITIONS, ALL BINDING.* |
| `SEARCH-CONDITION-2-CLOSED` | Condition 2 of the search admission demands CLOSED PATH SEGMENTS, not a NARROW ANCHORED pattern. Anchoring was measured to do none of the work assigned to it. | the shape of any allowlist pattern | 2026-09-19 | [2026-09-19-search-admission-condition-2-amended.md](2026-09-19-search-admission-condition-2-amended.md)<br>*CONDITION 2 IS AMENDED: **CLOSED**, NOT **ANCHORED*** |
| `NOTIFICATIONS-UNREAD-SPEND` | Loading /notifications/ is PERMITTED: it only clears the operator's own unread badge. Answers the question N 20 and N 45 were held on. | /notifications/ | 2026-09-23 | [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md)<br>*Notifications: the unread-spend question* |

### admissions

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `ADMIT-NOW-LANDING-IN-SESSION-14` | A wave-7 admission is made now, one anchored line in ONE commit with its census lines, red first; each admitted address gets one read-only landing-and-capture load in session 14, the first live session on a master carrying it; a failed landing check means the next integration reverts that admission; no row moves on an admission alone. | wave 7's landing checks (/my-items/saved-posts/, /learning/me/my-library/saved/) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*1. Lane msg7's nine (12:35, 13:30 and 17:20)* |
| `CONTACTS-PAGE-FROM-THE-SETTINGS-NAV` | N 32 and N 110 are re-aimed to his contact-syncing settings page, named by the settings navigation's own entry; lane settings7 admits it only if drawn and only if READ-PAST-AN-ACT-SUBSTRING's condition holds, the press gate refusing every control there. | his contact-syncing page (N 32, N 110) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*4. Lane net7's seven (13:25, 17:20 and 17:50)* |
| `GROW-SUGGESTIONS-BY-ADMISSION-NOT-SCROLL` | His full People You May Know lists are reached by admitting /mynetwork/discovery-see-all/, its landing in session 14, never by a scroll: SCROLL-NOT-SANCTIONED stands. | the discovery see-all lists (N 62, N 97, N 98) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*4. Lane net7's seven (13:25, 17:20 and 17:50)* |
| `HASHTAG-ADMISSION-WAITS-FOR-A-REFUSING-BASIS` | The hashtag page /feed/hashtag/ is not admitted: READ-PAST-AN-ACT-SUBSTRING's condition, the press gate still refusing every control, is unmet because SENSITIVITY_BASES matches /feed/ by containment and gives the page the feed's press basis; N 59 and N 60 keep their ADMIT step, and containment matching is a wave-8 design item. | the hashtag page (N 59, N 60) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*1. Lane msg7's nine (12:35, 13:30 and 17:20)* |
| `J175-ADMISSION-PASSES-NO-ACT-SUBSTRING` | J 175's admission of /learning/me/my-library/saved/ stands only if the address passes no act substring of the write guard or the press gate (save the one to check); measured: none of the 33 forbidden substrings, none of the press gate's markers, and no press basis, so both sanctioned shapes are refused there. | his Learning saved list (J 175) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*5. Lane jobs7's nine (13:45, 14:05, 14:30 and 15:51)* |
| `RECEIVED-LEAF-ADMITTED-WITH-ITS-READER` | N 13's received-tab leaf, /mynetwork/invitation-manager/received/, is admitted together with its reader's landing check by the lane that owns the reader, red first: one reader is never split across two lanes. | the invitation manager's received leaf (N 13) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*4. Lane net7's seven (13:25, 17:20 and 17:50)* |

### admissions and presses

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `VOLUNTEERING-FALLBACK-BOUNDARY` | His volunteering page's profileId comes only from his runtime argument, validated by shape and never stored or logged; the card link is pressed only on an exact match with the address formed from it, and the page never supplies the id. | his volunteering page (P D24) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*3. Lane prof7's six (22:21 the day before; 13:00, 13:10 and 17:20)* |

### capability class

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `COMPOSER-IS-THE-REFUSAL-NOT-THE-ADDRESS` | For publishing a post the composer is the wall, not the address. | publish a post | 2026-08-31 | [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md)<br>*#1 publish a post -- `linkedin_publish_post`. STILL REFUSING. **Ruling declined back to him.*** |
| `INVITATION-TARGETING-IS-CALL-TIME` | Targeting an invitation is allowed as a CALL-TIME responsibility. | send a connection invitation | 2026-08-31 | [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md)<br>*#7 send a connection invitation -- `linkedin_send_invitation`. STILL REFUSING, and the blocker is now a different one.* |
| `FEED-CONTENT-READ-RULING` | AMENDED 2026-09-24 by NAMES-AT-RUNTIME for what a read RETURNS at runtime (what is STORED is unchanged). Feed content may be read as COUNTS AND RELATIONS ONLY, never text or names. | reads of feed and post content | 2026-09-05 | [2026-09-05-lead-rulings-round-two.md](2026-09-05-lead-rulings-round-two.md)<br>*5. `FEED-CONTENT-READ-RULING` -- COUNTS AND RELATIONS ONLY* |
| `MENTION-COMPOSITION-RULING` | Build the mention MECHANISM, forbid the SOURCE: composing a mention is permitted as a mechanism, and harvesting the candidate list it would mention from is not. | mentions in posts and comments | 2026-09-05 | [2026-09-05-lead-rulings-round-two.md](2026-09-05-lead-rulings-round-two.md)<br>*1. `MENTION-COMPOSITION-RULING` -- BUILD THE MECHANISM, FORBID THE SOURCE* |
| `MESSAGING-SETTINGS-CAPABILITY-LEVEL` | The settings-family ruling is CAPABILITY-level, not path-level: a setting is admitted BY NAME or not at all, which excludes every page below the settings index whatever its URL spelling. It says 'a setting', not 'a profile setting'. | every persisted account preference | 2026-09-05 | [2026-09-05-decide-retire-rulings.md](2026-09-05-decide-retire-rulings.md)<br>*3.10 `MESSAGING-SETTINGS` -- 5 rows, RE-FILED, NOT RETIRED* |
| `NO-IRREVERSIBLE-WRITE-IS-FIRED` | AMENDED 2026-09-23 by WRITE-CLASS-B: irreversible writes MAY now be fired, but ONLY at a target the operator names -- the consent-per-act half below still binds. Original: No irreversible write is fired at a real target -- not an application, a post, an invitation, a message or a comment. Permission to BUILD a capability is not consent to perform a specific act against a specific person. Writes may be designed, gated, tested against fixtures and left ready. | every write in the server, standing | 2026-09-05 | [2026-09-05-lead-rulings-round-two.md](2026-09-05-lead-rulings-round-two.md)<br>*The line I did NOT cross, and will not without him* |
| `STANDING-SHAPE-OF-A-WRITE-RULING` | Every new write gets the SAME bar the twelve shipped writes meet: design, WriteSpec, gate, consent text, tests against fixtures and synthetic targets, two calls behind a single-use action-bound target-bound token with a 120s TTL. Do not invent a stricter bar for a new capability, and do not weaken it. | the admission shape for any new write | 2026-09-05 | [2026-09-05-lead-rulings-round-two.md](2026-09-05-lead-rulings-round-two.md)<br>*8. The standing shape of every write ruling here* |
| `GATE-IS-SAFE-AND-BLIND` | The gate is SAFE and BLIND, and those are different properties: condition 4 cannot witness disclosure. | the disclosure witness on a press gate | 2026-09-19 | [2026-09-19-two-census-conventions-ruled.md](2026-09-19-two-census-conventions-ruled.md)<br>*DEFECT ONE: CONDITION 4 CANNOT WITNESS DISCLOSURE* |
| `GROUPS-ADDRESS-BUYS-NO-WRITE` | Admitting a group address buys nothing for joining, leaving, posting, commenting or inviting. Each needs its own url, its own write sanction and its own ruling, so those rows stay GAP and no boundary change moves them. The price is three things and an admission pays one. | groups writes, and any address widening | 2026-09-19 | [2026-09-19-groups-admission.md](2026-09-19-groups-admission.md)<br>*The eight writes: the census already ruled this, TODAY, against itself* |
| `WRITE-CLASS-B` | The package may CONNECT, MESSAGE, APPLY, POST and OPEN MESSAGING on the operator's account, behind the single-use grant model and off by default. Lifts the read-only rule, the apply/connect/InMail cut and DO-NOT-OPEN-MESSAGING. | outward writes and opening messaging | 2026-09-23 | [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md)<br>*The write class (b)* |

### captures

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `ARTICLE-COMPOSER-CAPTURE` | One capture load of the article composer is permitted, with nothing typed and nothing published; an empty draft it may leave is his, private and deletable, and the capture records whether one appeared. | the article composer | 2026-10-10 | [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md)<br>*2. One article-composer capture* |
| `CAPTURE-PRESS-UNDER-PROBE-RULE` | A live-lane CAPTURE may press a disclosure control (a menu, a folder, a filter panel, a list) or type into a SEARCH box, never a composer or an editor, on a surface the press gate refuses, when nothing is committed: no save, send, submit, apply or confirm, and Escape closes what was opened. A shipped tool still needs its own per-surface basis entry. | presses and typing on a surface the gate refuses | 2026-10-10 | [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md)<br>*1. A capture may press, under the probe rule* |
| `B5-GROUP-COMPOSER-OPENS-EMPTY` | A capture may open a group's composer with nothing typed (capture C-B5-4), as ARTICLE-COMPOSER-CAPTURE allows for articles. | a group composer opened empty | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*3. The owed registrations* |
| `B5-INVITE-DIALOG-IS-A-LIST` | A group's invite dialog is a list and its filter is a search box (capture C-B5-3): reading them sends nothing. | a group's invite dialog | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*3. The owed registrations* |
| `EDITOR-TYPEAHEAD-SANCTIONED` | A capture may type a benign value from tool arguments into his own editor's autocomplete field, dismiss it with Cancel or Escape and re-read to prove nothing changed; any autosave sign stops everything. | his own editor's typeahead fields (P A11, P A13, P A17) | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*5. Lane build-p26's four (22:50)* |
| `LINKS-ARE-NOT-DISCLOSURES` | A link on his own profile is not a disclosure: the in-me-profile link presses for P D25 and P A25 are vetoed, and both rows go to a ruling on whether the self-profile query variant is admissible. | link presses on his own profile (P D25, P A25) | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*5. Lane build-p26's four (22:50)* |
| `OPEN-TO-WORK-EDITOR-ATTENDED-ONLY` | A capture may press his Open-to-Work Edit only in a session he attends: read the modal, close it, choose nothing, and round-trip read the card before and after; any change to the card stops everything. | his Open-to-Work editor | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*6. Lane admit26's ten (23:35)* |
| `OWN-PROFILE-SCROLL-SANCTIONED` | One scroll pass of his own profile per load is permitted, reading what renders and pressing nothing. | a scroll of his own profile (P D26) | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*5. Lane build-p26's four (22:50)* |
| `RESUME-BUILDER-UNDER-ARTICLE-COMPOSER-CAPTURE` | ARTICLE-COMPOSER-CAPTURE extends to LinkedIn's resume builder, since it serves the job search: one load, nothing typed, once a capture finds where LinkedIn draws it. | the resume builder (P M11) | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*6. Lane admit26's ten (23:35)* |
| `ARTICLE-COMPOSER-ONE-CAPTURE` | The article composer's closed controls are read in ONE capture with nothing typed: onboarding dismissed, then the author toggle, Manage, the embed control and Next, each read and closed; never Publish or Schedule; a draft's appearance recorded (its next step is deleting it), and a stop on any publishing control. | the article composer's disclosures (M C44, M C46, M C50, M C78, M C81, P L3) | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*7. Lane readers-msg26's four questions (14:10)* |
| `EDITOR-TYPEAHEAD-ONLY-ATTENDED` | C-B1a, the editor's typeahead, is captured only in a session he attends, so it stays out of an unattended session. | the editor typeahead line, C-B1a | 2026-11-26 | [2026-11-26-rulings-integration-5.md](2026-11-26-rulings-integration-5.md)<br>*3. The session-12 plan (17:45 and 18:18, lane s12-prep's calls)* |
| `FIFTH-SEARCH-TO-PEOPLE-LABELS` | Session 12's fifth search goes to the search-people-labels capture, whose All-filters button is drawn outside main. | session 12's fifth search | 2026-11-26 | [2026-11-26-rulings-integration-5.md](2026-11-26-rulings-integration-5.md)<br>*3. The session-12 plan (17:45 and 18:18, lane s12-prep's calls)* |
| `J-160-RAW-ONLY-IF-THE-PEOPLE-GATE-KEEPS-IT` | J 160's capture of his career insights keeps a raw page only if PEOPLE-GATE v2 keeps it; otherwise the skeleton and the heading words by key. | the career-insights page (J 160) | 2026-11-26 | [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md)<br>*1. Lane build-jobs2's five (19:25)* |
| `MESSAGING-LINE-TO-SESSION-13-STANDBY` | The one queue line that carries M M34 (the inbox-search capture-first) and M M28 behind one receipt guard moves whole to session 13's standby, so session 12 needs no inbox read. | the guarded messaging line, M M34 and M M28 | 2026-11-26 | [2026-11-26-rulings-integration-5.md](2026-11-26-rulings-integration-5.md)<br>*3. The session-12 plan (17:45 and 18:18, lane s12-prep's calls)* |
| `MSG-THREAD-FOOTER-TO-L2` | The msg-thread-footer capture needs a conversation he names, so it runs in an L2 session once he names it. | msg-thread-footer | 2026-11-26 | [2026-11-26-rulings-integration-5.md](2026-11-26-rulings-integration-5.md)<br>*3. The session-12 plan (17:45 and 18:18, lane s12-prep's calls)* |
| `NEWSLETTER-PICKED-FROM-HIS-SUBSCRIPTIONS` | The newsletter page session 12 captures is one the lane picks at runtime from his own subscriptions, published by LinkedIn or an organisation and never by a person. | the newsletter page's target | 2026-11-26 | [2026-11-26-rulings-integration-5.md](2026-11-26-rulings-integration-5.md)<br>*3. The session-12 plan (17:45 and 18:18, lane s12-prep's calls)* |
| `NEWSLETTER-PUBLISHER-UNPROVEN` | No newsletter page is loaded until a reading proves its publisher an organisation or LinkedIn: of session 12's five kept readings three were person-published and two showed no publisher, so E12 was skipped and its load went to standby. | the newsletter page's target | 2026-11-26 | [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md)<br>*4. Session 12 (22:02)* |
| `NO-RESULTS-STATE-CAPTURES` | Each job-search route's no-results state is captured (C-SRCH-0a classic, C-SRCH-0b AI; one load and one search each, a keyword chosen to draw nothing); until then every zero refuses on both routes. | the job search's two no-results states | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*2. The job search's AI fallback (11:05, lane search-fix26's three questions)* |
| `ARTICLE-EDITOR-PRESSES` | Three article-editor presses are session-14 capture specs: (a) Drafts in Manage, a read of his own lists; (b) Create newsletter, its form read with nothing typed and closed unsubmitted; (c) ATTENDED ONLY, a fixed placeholder title, Next, the publish settings read and closed without Publish, the draft deleted and verified absent; no Publish press is ever in the runner's closed list, and an unverifiable deletion is STOP-ALL. | the article editor (M C44, M C46, M C47, M C50) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*1. Lane msg7's nine (12:35, 13:30 and 17:20)* |
| `JOB-ALERT-ROW-CONTROL-ATTENDED` | J 170's alert-row control is captured in session 14, attended: one row's control pressed once and read only, nothing typed or chosen, closed and verified gone, the alert manager read before and after with no change. | one job alert's own control (J 170) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*5. Lane jobs7's nine (13:45, 14:05, 14:30 and 15:51)* |

### census convention

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `D6-CAPABILITY-OVER-AFFORDANCE` | A row named for an affordance is discharged when the package delivers the same capability payload by its own sanctioned routes; the row names them and rests on their proofs (PROVEN if live-proven, else UNFIRED). | rows named for a control or surface | 2026-09-23 | [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md)<br>*D6: a capability delivered without the named affordance* |
| `D3-UNREGISTERED-REFUSAL-IS-NOT-A-RULING` | A refusal written only into an allowlist comment is not a ruling: it makes no row EXCLUDED-RULED or CANNOT-DELIVER, and a row resting on one is GAP, blocked on the decision the refusal asks for, until that decision is registered. | refusals recorded only beside an allowlist entry | 2026-09-24 | [2026-09-24-rulings-search-verticals-rosters-passive-costs.md](2026-09-24-rulings-search-verticals-rosters-passive-costs.md)<br>*D3: is a reasoned allowlist refusal a ruling?* |
| `D5-PASSIVE-COST-IS-NOT-A-ROW` | A consequence of an act with no control of its own is recorded on the act's row, and its own row is EXCLUDED-RULED as NOT-AN-ACT (N 171). A preference he sets is an act, a setting, and stays a GAP write row (N 183). | passive costs | 2026-09-24 | [2026-09-24-rulings-search-verticals-rosters-passive-costs.md](2026-09-24-rulings-search-verticals-rosters-passive-costs.md)<br>*D5: is a passive cost a capability row?* |
| `WHO-WHICH-COUNTS-ARE-NOT-DELIVERY` | A row whose payload is WHO (people) or WHICH (items of other people's content) is not delivered by a count-only reader: GAP. Filters and aggregates are delivered by counts. The operator answered the names-and-titles question 2026-09-24 (NAMES-AT-RUNTIME): such rows now wait on a name-returning reader, not on the doctrine. | count-only readers | 2026-09-24 | [2026-09-24-rulings-notify-veto-and-who-which.md](2026-09-24-rulings-notify-veto-and-who-which.md)<br>*A count-only reader does not deliver WHO or WHICH* |

### census row J 110 and its Posts half

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `J-110-SPLITS-HOME-AND-POSTS` | J 110 splits under COMPOUND-ROW-SPLITS-ONLY-ON-STATE: the Home half goes to COVERED-UNFIRED, and the Posts half is built on the live9 capture. | census row J 110 and its Posts half | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*7. Lane build-jmn26's four (23:40)* |

### census row J 114 and its unbuilt facets (J 169)

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `J-114-SPLITS` | J 114 splits under COMPOUND-ROW-SPLITS-ONLY-ON-STATE on the J 110 -> J 168 precedent: the built facet stays J 114, and the unbuilt facets take the next free numeric id, GAP, next step C-RJ26-1. | census row J 114 and its unbuilt facets (J 169) | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*4. Lane readers-jobs26's three questions (12:50)* |

### census row J 153

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `COURSE-VIDEO-OUTSIDE-PURPOSE` | Watching a LinkedIn Learning course or video is EXCLUDED-RULED by OUTSIDE-THE-PRODUCT-PURPOSE. | census row J 153 | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*6. Lane admit26's ten (23:35)* |

### census row J 155

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `AI-COACH-OUTSIDE-PURPOSE` | Asking LinkedIn Learning's AI coach is EXCLUDED-RULED by OUTSIDE-THE-PRODUCT-PURPOSE. | census row J 155 | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*6. Lane admit26's ten (23:35)* |

### census row J 159

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `AD-LIBRARY-OUTSIDE-PURPOSE` | Searching LinkedIn's Ad Library is EXCLUDED-RULED by OUTSIDE-THE-PRODUCT-PURPOSE. | census row J 159 | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*6. Lane admit26's ten (23:35)* |

### census row J 163

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `J-163-RECEIPT-ONLY-WRITE` | J 163 is a receipt-only write behind the grant, fired only on his order: no inverse exists, so the round-trip rule cannot apply, and the press itself is the proof. | a one-shot recommendation feedback | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*7. Lane build-jmn26's four (23:40)* |

### census row J 174

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `JOB-OPENINGS-BY-FUNCTION-ADDED` | Job openings by function is a capability the census did not hold: a new J row, on load 20's Insights tab, distinct from J 114's headcount by function. | job openings by function | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*5. Lane jobs7's nine (13:45, 14:05, 14:30 and 15:51)* |

### census row J 19

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `J-19-BUILT-BEHIND-THE-GRANT` | J 19 is built behind the grant and refuses until its confirm dialog is captured; it fires only on his order. | clearing his recent job searches | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*7. Lane build-jmn26's four (23:40)* |

### census row M C14

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `SCHEDULED-LIST-AS-A-SHIPPED-READ` | His scheduled posts list is a shipped read: the post composer opened empty, Schedule post, then View all scheduled posts; the list read (zero only on a drawn empty headline), closed with nothing typed or scheduled, no draft verified, and a stop on any autosave sign. | his scheduled posts | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*7. Lane readers-msg26's four questions (14:10)* |

### census row M C18

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `M-C18-EDITOR-OPENS-UNSAVED` | His answer for C-B5-4 covers opening his post editor unsaved, so M C18 becomes a cheap capture. | census row M C18 | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*3. The owed registrations* |

### census row M C29

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `M-C29-DESIGN-FIRST` | M C29 is designed first and queued for the next build wave. | census row M C29 | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*3. The owed registrations* |

### census row M C39

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `COMMENTS-METRIC-NOT-ABSENT-ON-ONE-DROPDOWN` | M C39 is not MEASURED-ABSENT: one metric dropdown on one surface does not measure a capability; under D6 it is re-aimed to a post's own analytics, a CAPTURE, and stays GAP. | comment analytics | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*1. Lane msg7's nine (12:35, 13:30 and 17:20)* |

### census row M C70

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `GROUP-SEARCH-MEASURED-ABSENT` | M C70, a search inside groups, is MEASURED-ABSENT on the two surfaces measured: the content search's All filters panel draws no group facet, and a group's own page draws no group-scoped search control. | searching inside groups | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*1. Lane msg7's nine (12:35, 13:30 and 17:20)* |

### census row M C97

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `M-C97-LINK-KEYED-DELETE` | M C97's delete is keyed by the notification's link and refuses a link that matches more than one card; building it needs a live uniqueness capture first. | a notification delete | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*3. The owed registrations* |

### census row M M31

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `M-M31-READ-BY-COMPOSITION` | M M31's read half is the composition linkedin_open_thread(thread_id, allow_unread=True) under CALLER-COMPOSITION-UNDER-D6: it opens only a conversation he names, and opening marks it read, which is the read's cost. | marking a conversation read | 2026-11-26 | [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md)<br>*5. Lane build-msg2's five (22:33)* |

### census row M M34

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `MESSAGE-SEARCH-CAPTURE-FIRST` | A capture first measures whether his inbox search lands on an address of its own; if it does, the search is composed under D1-SEARCH-AS-READS with no typing; only if not, a new sanctioned shape SEARCH-BOX-TYPING, anchored to a labelled search input and refusing if focus reaches a composer or a send control enables. | searching his inbox | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*7. Lane readers-msg26's four questions (14:10)* |

### census row N 200

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `AD-HIDE-AIM-HELD` | N 200 stays GAP: no reader returns an ad urn without pressing ads he did not name, and pressing un-named ads' menus to search for one is declined. | where a hidden ad's urn comes from | 2026-11-26 | [2026-11-26-rulings-integration-5.md](2026-11-26-rulings-integration-5.md)<br>*2. Two answers for lane build-net2 (17:10)* |
| `AD-HIDE-AT-HIS-NAMED-AD` | Hiding an ad is allowed under HIS-OWN-CURATION-NOT-OUTWARD for an ad he names (an urn a reader returned to him that he hands back); the tool never picks an ad, the undo is captured on the first supervised fire, and Report ad stays outward. | hiding an ad | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*5. Lane readers-net26's section 9 (13:31)* |

### census row N 37

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `FEED-UNFOLLOW-ROUTES-UNDER-D6` | N 37's unfollow is held on the feed (no press on the menu of an item he did not name, AD-HIDE-AIM-HELD's ground) and routed under D6: SIBLING to a shipped route for unfollowing a member he names if one exists, else a CAPTURE on his following list, network's surface, wave 8. | unfollowing from the feed | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*1. Lane msg7's nine (12:35, 13:30 and 17:20)* |

### census row N 6

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `REINVITE-BY-CALLER-COMPOSITION` | N 6 is discharged by CALLER-COMPOSITION-UNDER-D6 on linkedin_sent_invitations and linkedin_connect_from_profile, COVERED-UNFIRED; LinkedIn's re-invite cooldown is honoured because Connect is pressed only where drawn, and Connect stays outward, at named targets only. | a re-invitation | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*5. Lane readers-net26's section 9 (13:31)* |

### census row N 93

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `KEYWORD-FIELDS-MEASURED-ABSENT` | N 93, the people search's keyword fields, is MEASURED-ABSENT: both open All-filters panels draw no text input, with a D6 note to the shipped keyword search rows and the facets. | people-search keyword fields | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*4. Lane net7's seven (13:25, 17:20 and 17:50)* |

### census row P K7

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `VERIFICATION-DELETE-HELD` | P K7, deleting a verification, stays at RULING: the act has no inverse, is visible to others, and its first press may be the act itself. If the captured Delete declares a popup, an attended capture (press, read, Cancel) and then a build in J-19's refuse-until-captured shape; if not, it stays his. | deleting a verification | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*2. Lane settings7's two (12:55)* |

### census row P L7

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `CREATOR-IDEAS-NOT-ABSENT-ON-ONE-SURFACE` | P L7's post ideas are not MEASURED-ABSENT because one landing draws them 0 times: one surface is not a measurement of the capability (the M C39 ground, under D6); P L7 is re-aimed to a capture of the creator hub's own navigation, or a RULING if it shows the feature retired. | creator post ideas | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*3. Lane prof7's six (22:21 the day before; 13:00, 13:10 and 17:20)* |

### census row P O23

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `P-O23-D5-ON-ITS-OWN-WORDS` | P O23 takes D5's NOT-AN-ACT only if D5's own words cover it, and the registering lane checks and quotes them. | census row P O23 | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*2. The absence convention, and P O23* |

### census row P S8

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `KEY-SKILLS-ADD-HELD` | P S8's key-skill add is not built: the skills list draws no Show all and no control on its six items, so the add has no drawn inverse; the row is held at GAP with a session-14 attended capture of the skills section's own edit view, nothing saved. | adding a key skill | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*3. Lane prof7's six (22:21 the day before; 13:00, 13:10 and 17:20)* |

### census rows J 111 and J 176

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `J111-SPLITS-PRODUCTS-FROM-SERVICES` | J 111 splits on state: the Products half, built (linkedin_company_page_tab, tab=products), keeps J 111 at COVERED-UNFIRED; the Services half takes the next free J id at GAP, its step CAPTURE C-J111-1. | a company Page's Products and Services tabs | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*5. Lane jobs7's nine (13:45, 14:05, 14:30 and 15:51)* |

### census rows J 152, J 154, J 156, J 171, J 172, J 175

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `LEARNING-ROWS-SPLIT` | J 152, J 154 and J 156 each split on state where their halves are different capabilities: the captured half keeps the id and builds, the other half takes a new id with a CAPTURE step or, for J 154's saved list, an ADMIT of /learning/me/my-library/saved/ with its landing in session 14. | LinkedIn Learning | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*5. Lane jobs7's nine (13:45, 14:05, 14:30 and 15:51)* |

### census rows J 169 and J 173

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `J169-BY-ITS-OWN-WORDS` | J 169 is headcount over time, notable alumni and openings by seniority, by its own words; it splits only if load 20 makes the first two buildable, the seniority half then a new row. | census rows J 169 and J 173 | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*5. Lane jobs7's nine (13:45, 14:05, 14:30 and 15:51)* |
| `J169-SPLITS-SENIORITY-REAIMED-UNDER-D6` | AMENDED 2026-11-27 by J169-BY-ITS-OWN-WORDS: J 169 keeps its own words' first two halves, and its seniority half is the new row, re-aimed under D6. Original: J 169's function half builds; its seniority half takes a new id at GAP, its step a CAPTURE of the AI job search's experience-level facet; it is not absent on one view. | Premium Page Insights by seniority | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*5. Lane jobs7's nine (13:45, 14:05, 14:30 and 15:51)* |

### census rows J 37 and J 170

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `J-37-SPLITS` | J 37 splits on state: the list half stays J 37, COVERED-UNFIRED on linkedin_job_alerts; the manage half is a new row, J 170, at GAP with its next step BUILD. | the job-alert manager | 2026-11-26 | [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md)<br>*1. Lane build-jobs2's five (19:25)* |

### census rows J 61-J 65

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `APPLY-DRY-WALK-FIRES-THE-STEP-ROWS` | A dry walk of the apply flow on a named posting, every step read back and the draft discarded and verified, fires the step rows J 61 to J 65; the submission row still needs a real send. | the apply flow's steps | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*4. Lane apply-26's seven (22:40, the final head at 23:08)* |

### census rows M C3, M C4, M C6, M C7

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `MEDIA-POST-SAME-REFUSAL` | linkedin_publish_post's audience refusal applies to a media post on the same composer, whose audience is unread, and perform's drain rule stands, so there is no upload after a press: M C3 and M C4, with M C6 and M C7, stay GAP and cite this ruling. | a post with media | 2026-11-26 | [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md)<br>*5. Lane build-msg2's five (22:33)* |

### census rows M M26, M M27, M M29, M M31

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `CONVERSATION-MENU-PREVIEW-PRESS` | A sanctioned preview press opens the one options menu bound to the named conversation, reads the item's word, presses nothing inside and closes on Escape; the confirmed press re-reads and refuses on the inverse; Delete conversation, which has no inverse, is receipt-only behind the grant, on his explicit order for a named conversation. | a conversation's menu acts | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*7. Lane readers-msg26's four questions (14:10)* |

### census rows M M28 and M M54

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `M-M28-SPLITS` | M M28 splits on state: the view half stays M M28, COVERED-UNFIRED on linkedin_archived_conversations; the restore half is a new row, M M54, at GAP with its next step a CAPTURE, its control never captured. | archived conversations | 2026-11-26 | [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md)<br>*5. Lane build-msg2's five (22:33)* |

### census rows N 102 and J 108

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `N-102-MOVES-WITH-J-108` | N 102 moves with J 108 as its sibling: there is no distinct capability (precedent N 173 / M C60). | census rows N 102 and J 108 | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*7. Lane build-jmn26's four (23:40)* |

### census rows N 24 and N 27

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `CONNECTIONS-CONTROLS-MEASURED-ABSENT` | N 27 is MEASURED-ABSENT on three surfaces; N 24 moves the same way only if its spellings include the sort's value labels and the page draws no dropdown trigger. | his connections list's controls | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*4. Lane net7's seven (13:25, 17:20 and 17:50)* |

### census rows N 40, M C52

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `REFOLLOW-FROM-HIS-NAMED-PROFILE` | A re-follow is built from the member's own profile he names by link (N 34's route); the unfollowed list is a read and a veto only, never a target source. | following a member again | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*5. Lane readers-net26's section 9 (13:31)* |

### census rows N 63, M C61

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `B5-RAIL-JOIN-DOES-NOT-DISCHARGE` | A Join button drawn in a page's side rail does not discharge N 63 or M C61: the target would come from the page. | census rows N 63, M C61 | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*3. The owed registrations* |

### census rows P A14, P A15, P K8

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `ABSENT-ON-HIS-ACCOUNT-PER-ROW` | Per row, under the absence convention: a drawn and corroborated empty state answers a READ; a surface not offered to his account is MEASURED-ABSENT; a write needing data he lacks is PRECONDITION with a reopener. | census rows P A14, P A15, P K8 | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*5. Lane build-p26's four (22:50)* |

### census rows P N22 and P N32

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `P-N22-SPLITS` | P N22 splits on state: the subscription half stays P N22, COVERED-UNFIRED on the closed-words read of his Manage Premium account page; the payments half is a new P id at GAP, its step ADMIT of a static named purchases address, never the page-drawn id. | his Premium subscription and payments | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*2. Lane settings7's two (12:55)* |

### census rows P P10 to P P14

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `AD-DATA-GRAIN` | The five grouped Advertising data rows (P P10 to P P14) are kept; they split per setting only when their pages are admitted and their states diverge (COMPOUND-ROW-SPLITS-ONLY-ON-STATE). | their grain | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*5. Lane readers-net26's section 9 (13:31)* |

### census rows proven on the classic job search

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE` | Rows proven on the classic job search stay COVERED-PROVEN while it serves; once a capture shows it no longer serves, each returns to GAP with its next step on the AI route and a reopener. | census rows proven on the classic job search | 2026-11-26 | [2026-11-26-rulings-search-route.md](2026-11-26-rulings-search-route.md)<br>*3. The rows proven on the classic route* |

### census state

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `CENSUS-OUTRANKS-LEDGER` | Where the census and the ledger disagree the CENSUS is right; the ledger's `1R` is the error. | precedence between the census and the ledger | 2026-09-19 | [2026-09-19-the-three-ruling-requests-ruled.md](2026-09-19-the-three-ruling-requests-ruled.md)<br>*RULED: THE CENSUS IS RIGHT. THE LEDGER'S `1R` IS THE ERROR.* |
| `CONTAINER-EXCLUSION-PROPAGATES-ONLY-IF-UNREACHABLE` | A container's exclusion reaches a control ON it only when the container was excluded as UNREACHABLE. An exclusion of the container's own ACT does not propagate to reading its contents. Either way the content row must CITE the container row, so a reopener on the container reaches the content. | inherited exclusions, container to content | 2026-09-19 | [2026-09-19-two-census-conventions-ruled.md](2026-09-19-two-census-conventions-ruled.md)<br>*point opposite ways* |
| `CONVERSATION-OVERFLOW-BOTH-WAVES-RIGHT` | On `CONVERSATION-OVERFLOW-MENU` both waves are right, about different things -- eight rows are forced and the chosen set stays empty. | CONVERSATION-OVERFLOW-MENU | 2026-09-19 | [2026-09-19-the-five-requests-ruled.md](2026-09-19-the-five-requests-ruled.md)<br>*C. `CONVERSATION-OVERFLOW-MENU` -- RULED: both waves are right, about different things* |
| `CREATOR-HUB-AND-POST-COMMENT-LEDGER-OVERCOUNTS` | For `CREATOR-HUB-SURFACE` and `POST-COMMENT-CONTROLS` the LEDGER OVER-COUNTS. | two blocker row counts | 2026-09-19 | [2026-09-19-the-five-requests-ruled.md](2026-09-19-the-five-requests-ruled.md)<br>*E. `CREATOR-HUB-SURFACE` AND `POST-COMMENT-CONTROLS` -- RULED: LEDGER OVER-COUNTS* |
| `GRAIN-FOLLOWS-WHAT-THE-PLATFORM-DRAWS` | The grain of an enumeration follows what the PLATFORM draws, not what a reader finds convenient to count. | how capabilities are enumerated | 2026-09-19 | [2026-09-19-two-census-conventions-ruled.md](2026-09-19-two-census-conventions-ruled.md)<br>*RULED: THE GRAIN FOLLOWS WHAT THE PLATFORM DRAWS* |
| `INCIDENTAL-CAPTURE-IS-NOT-A-RULING` | A denylist substring written for a CLASS of addresses that catches this capability incidentally is a BLOCKER, not a decision. Those rows stay GAP with the blocker named. A rule naming the ACT is EXCLUDED-RULED; a filter catching the ADDRESS is GAP; an address measured UNREACHABLE is neither. | every boundary-blocked row on all four slices | 2026-09-19 | [2026-09-19-two-census-conventions-ruled.md](2026-09-19-two-census-conventions-ruled.md)<br>*RULED: NO. THEY STAY GAP, WITH THE BLOCKER NAMED PRECISELY.* |
| `MAP-CONVENTION-AT-HEAD-MEMBERSHIP` | The blocker map records at-HEAD membership, plus a `RE_FILED` marker. | what the blocker map means by membership | 2026-09-19 | [2026-09-19-the-five-requests-ruled.md](2026-09-19-the-five-requests-ruled.md)<br>*A. THE MAP'S CONVENTION -- RULED: at-HEAD membership, plus `RE_FILED`* |
| `N61-REMOVED-FROM-HASHTAG-EXISTENCE` | `N 61` is removed from `HASHTAG-EXISTENCE`. | one row's blocker assignment | 2026-09-19 | [2026-09-19-the-five-requests-ruled.md](2026-09-19-the-five-requests-ruled.md)<br>*B. `N 61` IN `HASHTAG-EXISTENCE` -- RULED: removed* |
| `DUPLICATE-ROW-IS-MARKED-NEVER-DELETED` | When two census rows describe one capability the duplicate STAYS in the file, marked as a duplicate and naming the row it duplicates. It is not removed and its id is never reused. | every cross-slice re-file and de-duplication | 2026-09-20 | [2026-09-20-the-deduplication-ruling.md](2026-09-20-the-deduplication-ruling.md)<br>*The ruling* |
| `POSITIONAL-DIALECT-SHIP-THE-DETECTOR` | Ship the detector; do not rewrite the 69 cells. | the positional-dialect cells | 2026-09-20 | [2026-09-20-the-pointer-graph.md](2026-09-20-the-pointer-graph.md)<br>*4. THE DECISION ON THE POSITIONAL DIALECT* |
| `COMPOUND-ROW-SPLITS-ONLY-ON-STATE` | When ONE census row describes TWO capabilities it is SPLIT only if the halves require different STATES. A DIRECTION divergence is repaired in the cell as `R+W`, never by a split. Two verbs, two surfaces, two addresses and mere verbosity are not grounds. A row whose halves share a state today but would not once a pending ruling is applied carries a written TRIGGER instead of being split now. | every row whose capability names two acts | 2026-09-21 | [2026-09-21-the-compound-rows.md](2026-09-21-the-compound-rows.md)<br>*THE RULING -- RULED: a compound row is split ONLY when its halves need different STATES* |
| `CALLER-COMPOSITION-UNDER-D6` | A row is discharged under D6-CAPABILITY-OVER-AFFORDANCE when the caller can compose SHIPPED tools to deliver its payload, with no server-side derived navigation; the row's cell names the tools and their arguments, and its state is the weakest of its parts. | rows a composition of shipped tools delivers | 2026-10-10 | [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md)<br>*4. Caller composition counts under D6* |
| `GEOLOCATION-BY-D6` | No browser geolocation permission is granted; searching jobs near him moves under D6 on the shipped location-parameter search, by the row's own bar. | searching from his current location | 2026-10-10 | [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md)<br>*12. Location by D6, not by geolocation* |
| `OUTSIDE-THE-PRODUCT-PURPOSE` | A row whose capability serves neither his job search nor his professional presence is EXCLUDED-RULED, reopened when he asks for it -- unless its own cell shows it tunes his job recommendations or his search. | rows outside the product's purpose | 2026-10-10 | [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md)<br>*17. Rows outside the product's purpose* |
| `P-A9-CANNOT-DELIVER` | The additional name's visibility is COVERED-CANNOT-DELIVER on the P A2 / P A4 precedent: its two switches carry the same label, so no route can aim one; reopened when LinkedIn draws a distinguishing name. | P A9 | 2026-10-10 | [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md)<br>*14. A control no route can aim* |
| `MEASURED-ABSENT-OR-PRECONDITION` | MEASURED-ABSENT means LinkedIn does not offer the capability to this account at all; PRECONDITION means it is offered but needs an account state he lacks, with a named reopener. | MEASURED-ABSENT against a GAP row waiting on a PRECONDITION | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*2. The absence convention, and P O23* |
| `FAILED-REPROOF-DEMOTES` | A COVERED-PROVEN row whose scheduled live re-proof fails moves to COVERED-UNFIRED, citing the failed load, until a fire re-proves it. | rows whose re-proof fails | 2026-11-26 | [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md)<br>*6. A failed re-proof (23:05)* |
| `CAPTURE-SHOWS-READER-BLIND-DEMOTES` | A COVERED-PROVEN row whose shipped reader reads nothing on a live capture of its own surface moves to COVERED-UNFIRED, citing the capture, until a fire re-proves it (FAILED-REPROOF-DEMOTES' shape); its new read is built red first with the old page kept as a control. | rows whose reader is blind on a new capture (M C75, N 20, N 45) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*1. Lane msg7's nine (12:35, 13:30 and 17:20)* |
| `EXCLUDED-RULED-ADMISSION` | A row is EXCLUDED-RULED only on one of FOUR written grounds: a forbidden-substring entry, a writes.PERMANENTLY_FORBIDDEN key, a WriteSpec refusing in its own words, or an audit passage measuring the capability unreachable. Anything a general mechanism merely happens to block is GAP with a NAMED BLOCKER. | the bar for EXCLUDED-RULED on every slice | ~2026-09-03 | [_census/network.md](_census/network.md)<br>*2. HOW A CAPABILITY WAS ASSIGNED A STATE* |

### code

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `NAVIGATION-CEILING-MADE-TRUE` | AMENDED 2026-11-26 by NAVIGATION-CEILING-PER-TOOL-CALL: the measured maximum is 5, not 3, reached by the job search's place fan-out alone, so that one tool declares an allowance capped at 5 and every other tool call keeps the ceiling of 3, enforced in goto, refusing a 4th. Original: MAX_NAVIGATIONS_PER_CALL is raised to the measured maximum, 3, and enforced in BrowserManager.goto by a per-call counter refusing a 4th; the README's 'One page load per tool call' is put right. | page loads per tool call | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*8. The navigation ceiling (14:27, lane pace20)* |
| `NAVIGATION-CEILING-PER-TOOL-CALL` | At most 3 page loads per MCP tool call: a fastmcp middleware arms a budget for each tools/call, goto counts only while one is armed and refuses the 4th load before making it, and code outside a tool call (the live runner, probes, direct test calls) is untouched; linkedin_search_jobs alone declares a fan-out allowance, one load per place, capped at MAX_LOCATIONS 5 and AST-pinned to its one call site; the people readers' loop bound is its own constant, 2. | page loads per tool call | 2026-11-26 | [2026-11-26-rulings-integration-5.md](2026-11-26-rulings-integration-5.md)<br>*1. The navigation ceiling (16:45 and 17:12, lane infra26's item 2)* |
| `READ-CARDS-DELETION` | After integration 4, the first lane touching server.py deletes server._read_cards if an AST caller census shows no caller. | server._read_cards | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*2. The job search's AI fallback (11:05, lane search-fix26's three questions)* |
| `WRITE-DOOR-EXCUSAL-ON-THE-SPEC` | The write door's excusal for his application settings page is keyed by its address on the WriteSpec (exempt_substrings_at), and readonly.py and its boundary freeze stay untouched. | the write door's per-address excusal | 2026-11-26 | [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md)<br>*1. Lane build-jobs2's five (19:25)* |
| `EXACT-MATCH-REFUSES-ANY-WHITESPACE` | The exact match is ONE matcher (volunteering_route.exact_link_verdict) that never normalises its target: any character outside the printable ASCII range refuses, unsafe percent escapes refuse, the comparison is raw exact equality with no case fold, and only an admitted /in/me/ address counts; every session-14 root press imports it. | the exact match for a press from his profile root | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*3. Lane prof7's six (22:21 the day before; 13:00, 13:10 and 17:20)* |
| `J114-READS-ITS-OWN-TABLE` | The company Insights reader selects each table by its summary, never by its header words: Headcount growth by function feeds J 114, re-based on load 20, and Total job openings feeds J 174; red first on both pages. | the company Insights tab's function tables (J 114, J 174) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*5. Lane jobs7's nine (13:45, 14:05, 14:30 and 15:51)* |
| `REFUSE-BEFORE-LOAD-ON-A-RETIRED-ROUTE` | A job search setting any argument the AI route refuses (a place, a filter, an offset or an employer) is refused before any load and any D1 search, naming the arguments and the retired classic route; the plain keyword search runs on the AI route. | linkedin_search_jobs' arguments on the retired classic route | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*5. Lane jobs7's nine (13:45, 14:05, 14:30 and 15:51)* |
| `SELF-LOADER-WAITS-FOR-THE-REWRITE` | The self-profile loader and the press gate wait, bounded, for LinkedIn's client-side rewrite of /in/me/ to his member path (polling the address only), then run the edit-link structure check; red first on a fake page whose address changes after a delay. | loading his own profile at /in/me/ | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*3. Lane prof7's six (22:21 the day before; 13:00, 13:10 and 17:20)* |

### configuration

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `JOBHUNT-HOME-KEEPS-ITS-MEANING` | JOBHUNT_HOME keeps jobcore's meaning, the directory holding jobhunt.json. | the JOBHUNT_HOME variable | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*4. Lane apply-26's seven (22:40, the final head at 23:08)* |
| `JOBHUNT-ROOT-RESOLUTION-ORDER` | The answer bank resolves JOBHUNT_ANSWER_BANK, then JOBHUNT_ROOT, then the .jobhunt-root walk-up (six parents, as jobcore); JOBHUNT_HOME is never read. | how the apply walker finds its answer bank | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*4. Lane apply-26's seven (22:40, the final head at 23:08)* |

### decision routing

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `OUTWARD-ACTS-NEED-THE-OPERATOR` | Only acts toward other people, or irreversible ones, need the operator. Every other call -- search keywords, self-only presses, his own notification state, allowlist and press-gate defaults -- is the orchestrator's, on evidence, recorded here and overridable. | what is escalated to the operator | 2026-09-23 | [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md)<br>*What needs the operator* |

### guards

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `READER-INVENTORY-BY-QUALIFIED-NAME` | The pinned inventory of readers outside dom.py matches a call to module.function, never to a bare name, so a same-named reader in another module cannot pass as wired. | the readers-outside-dom inventory | 2026-11-26 | [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md)<br>*5. Lane build-msg2's five (22:33)* |

### live captures

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `PEOPLE-GATE-COUNTS-NAME-SLOTS` | The live lane's people gate, in its next version, counts name slots as well as profile links before a raw capture is kept. | the people gate on raw pages | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*5. Lane readers-net26's section 9 (13:31)* |

### live lanes

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `LIVE-BUDGET-40-LOADS` | A live session may use up to 40 LinkedIn page loads, serial, at least 20 seconds apart -- a ceiling, not a target; one browser driver at a time. | page loads per session | 2026-09-23 | [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md)<br>*The live-session budget* |
| `LIVE-FLAG-DENIES-LINKEDIN-MCP` | While the live-session flag is up, the user-scope guard denies every non-exempt LinkedIn MCP tool in every session (only server_info, cdp_status, logout and page_plugin_snippet pass), and the live lane drives LinkedIn through its runner only. | LinkedIn MCP tools while a live session runs | 2026-11-26 | [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md)<br>*2. The live lane (20:36, answering integration 5's two questions)* |
| `PLAN-PEOPLE-GATE-LINES-ARE-THE-LIVE-LINES` | For session 12 the live lane applies the people-gate lines of the session plan's section 6, which judge every page, and not lane infra26's generic one-line hand-off. | the runner's people-gate lines | 2026-11-26 | [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md)<br>*2. The live lane (20:36, answering integration 5's two questions)* |
| `INBOX-SEARCH-IS-NOT-A-D1-SEARCH` | M M34's typed inbox search is not a D1 search: it is a load if it navigates, typed under SEARCH-BOX-TYPING, people-gated; it returns to session 13 only if already built, else session 14. | the inbox search (M M34) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*6. The live lane (13:35)* |

### live lanes and the job pipeline

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `BUDGET-ONE-ACCOUNT-40` | His account has ONE budget of 40 page loads per trailing 12 hours, shared by the live lane and the job pipeline; the live runner records every load in the pipeline's one pinned ledger before making it, with no copy and no second ledger, and a session starts only with 40 free, or shrinks its plan from the bottom of the rank. | page loads on his account | 2026-11-26 | [2026-11-26-rulings-integration-5.md](2026-11-26-rulings-integration-5.md)<br>*4. His account's one page-load budget (17:52)* |

### live loads

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `FILTER-REQUERY-COUNTS-AS-A-SEARCH` | A re-query that a filter triggers counts as a search against the 5-per-session search cap. | the per-session search cap | 2026-11-26 | [2026-11-26-rulings-search-route.md](2026-11-26-rulings-search-route.md)<br>*2. The search budget* |

### live proofs

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `CREDENTIAL-SETTINGS-NEED-THE-OPERATOR` | Credential, recovery and session settings -- the seven credential/recovery controls and P N10 (sign out of sessions, which ends this server's own session) -- are never live-proven unless the operator names them. | account security settings | 2026-09-23 | [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md)<br>*Credential and session settings* |
| `OPERATOR-NAMES-THE-TARGET` | A live proof of an outward act fires ONLY at a target the operator names -- whom to connect with or message, which job to apply to, what to post. Never a real person or job chosen by the package or an agent. | every outward write | 2026-09-23 | [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md)<br>*The operator names each live target* |
| `OWN-INBOX-READS-COVERED-BY-B` | Reading the operator's own inbox, including opening threads, is covered by ruling (b) with no per-fire go-ahead; proofs prefer threads already read so no new read receipt is sent. | /messaging/ reads | 2026-09-23 | [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md)<br>*Reading his own inbox* |
| `SELF-PROFILE-EDITS-NOT-OUTWARD` | Edits to the operator's own profile fields are not outward acts: no other person is targeted and each edit reverses. Live proofs are permitted with notify-network off, the field restored in-session and proven by a before/after reading, and never a field that broadcasts by nature. | edits to the operator's own profile fields | 2026-09-23 | [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md)<br>*Edits to his own profile fields* |
| `SHARE-AND-POLL-PROOFS-OWN-POSTS` | Share-link proofs use the operator's own posts only (M C72); a poll post's address (M C85) comes from tool arguments only -- his own poll post, or NEEDS-TARGET. | share links and poll results | 2026-09-23 | [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md)<br>*Share and poll proofs* |
| `SELF-PROFILE-EDIT-NOTIFY-CONDITION-AMENDED` | Amends condition 1 of SELF-PROFILE-EDITS-NOT-OUTWARD: where the edit dialog draws no notify control, his account-level 'Share profile updates with your network' setting read OFF before the edit satisfies it; an unnamed switch blocks until a capture names it; neither established -> NEEDS-OPERATOR. | edits to the operator's own profile fields | 2026-09-24 | [2026-09-24-rulings-notify-veto-and-who-which.md](2026-09-24-rulings-notify-veto-and-who-which.md)<br>*Where the dialog draws no notify control* |
| `RECEIPT-RISK-IS-HIS` | The save switch's live round trip on his application settings may delete his stored resumes and answers, which is unmeasured, so it is never scheduled without his explicit order naming the direction. | J 76 and P M7, the save switch | 2026-11-26 | [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md)<br>*1. Lane build-jobs2's five (19:25)* |

### live proofs and automated runs

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `RATIFIED-POLICY-NAMES-APPLICATION-TARGETS` | For JOB APPLICATIONS only, a policy he ratified at his own console names the targets by rule, and that satisfies OPERATOR-NAMES-THE-TARGET; APPLY-FLOW-IS-THE-APPLICATION still holds, and every other outward act (messages, connects, posts, InMail) still needs a target he names. | job applications under a ratified policy | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*3. Job applications under a policy he ratified (12:22)* |

### live-lane state

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `UNFOLLOWED-RAW-DELETED` | The kept raw capture of his unfollowed page, which held 44 members' names, is deleted by the orchestrator in both its copies; the skeletons are kept. | a raw capture holding people | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*5. Lane readers-net26's section 9 (13:31)* |

### navigation

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `PAGE-MAY-VETO-NEVER-SUPPLY` | Every navigation address is composed from tool arguments; page content may only REFUSE a navigation (e.g. a caller-supplied id that is not his own), never provide the address. | addresses and page content | 2026-09-24 | [2026-09-24-rulings-notify-veto-and-who-which.md](2026-09-24-rulings-notify-veto-and-who-which.md)<br>*The address comes from the caller* |

### press gate

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `IN-ME-NO-BLANKET-BAR` | /in/me/ presses get no blanket sensitivity-basis bar; each control is judged on evidence like any other press. | /in/me/ controls | 2026-09-23 | [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md)<br>*Presses on /in/me/* |
| `REVEAL-BUTTON-IS-A-DISCLOSURE` | A plain button that only reveals content (e.g. 'Show more analytics') is pressed as a disclosure, with before/after readings proving it revealed content and changed no state. | reveal-only buttons | 2026-09-23 | [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md)<br>*A button that only reveals* |
| `VIEW-SWITCH-PRESS-RESTORED` | A press that changes which rows a view shows is permitted if the view is RESTORED afterwards and a before/after reading proves it. | sort and filter controls | 2026-09-23 | [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md)<br>*View-switch presses* |
| `NO-INDEX-PINNED-JUDGEMENTS` | A control is judged by its own accessible name and role, never by its position; controls on his own profile go to capture first, and label-based basis entries follow from it. | how a control is judged | 2026-10-10 | [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md)<br>*3. No position-pinned judgements* |
| `PRESS-GATE-MAY-READ-TO-DECIDE-SELF` | Where the URL alone no longer decides self or other (a member profile root with no marker), the press gate may make its own read-only count of edit links before any press; a caller-supplied reading stays refused, and where the URL decides, the gate still refuses before touching the page. | deciding his own profile | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*6. The press gate's own read (13:40, lane selfprofile26)* |

### presses

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `ONE-ENTRY-IS-ONE-SHAPE` | SEARCH-BOX-TYPEAHEAD-DISCLOSURE's one sanctioned-mutation entry is one sanctioned SHAPE, not one line: one drain function with exactly two call sites, the click that opens and the Escape that closes, so readonly.SANCTIONED_MUTATIONS holds two lines for it; every other key and every fill refused. | the search box's typeahead (N 95) | 2026-11-26 | [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md)<br>*3. Lane build-net2's one (about 20:00; recorded 20:36, 21:46 and 21:55)* |
| `SEARCH-BOX-TYPEAHEAD-DISCLOSURE` | The search box's typeahead is a sanctioned disclosure shape over [role=search] input[aria-autocomplete] on an admitted page, refused at runtime unless exactly one is drawn; nothing is typed, only the recent-searches group is read (HIS-OWN-TEXT-AT-RUNTIME), people options are never read, and Escape closes it with the listbox verified gone. | the search box's recent searches (N 95) | 2026-11-26 | [2026-11-26-rulings-integration-5.md](2026-11-26-rulings-integration-5.md)<br>*2. Two answers for lane build-net2 (17:10)* |
| `SELF-ROOT-LINK-PRESS-BY-EXACT-MATCH` | A link drawn on his own profile root is pressed, attended only, only when its target is EXACTLY the address the read boundary admits, including any constant query the admission carries, with the proven landed member read as me; any other query, parameter or fragment vetoes; a navigating press is a load; nothing typed or saved; closed and verified gone; the root read before and after. | links on his own profile root (session 14) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*3. Lane prof7's six (22:21 the day before; 13:00, 13:10 and 17:20)* |

### read boundary

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `D1-SEARCH-AS-READS` | Search keywords and LinkedIn-written facets are permitted as reads: values from tool arguments only, never an identifying value of the operator, at most 5 test searches per session. | search keywords and facets | 2026-09-23 | [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md)<br>*D1: search keywords and facets* |
| `OTHER-MEMBER-IDS-AS-READS` | Another member's id in a search facet (e.g. connectionOf) is permitted as a read when it comes from the tool's arguments, never from page content, and is never stored in a tracked file. | search facets carrying another member's id | 2026-09-23 | [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md)<br>*Other members' ids as search facets* |
| `D2-SEARCH-VERTICALS-WIDENED` | The search admission widens from people to four CLOSED segments, /search/results/(people\|companies\|groups\|events)/, under D1-SEARCH-AS-READS's three conditions; serves N 104, N 161, M C70 and N 179. | search result verticals | 2026-09-24 | [2026-09-24-rulings-search-verticals-rosters-passive-costs.md](2026-09-24-rulings-search-verticals-rosters-passive-costs.md)<br>*D2: widen the search admission beyond people* |
| `MEMBER-ROSTERS-AS-BOUNDED-READS` | A roster the operator can open himself (a group's members, an event's attendees, a company's or school's People tab) is admitted as a bounded read: one page per call, the id from tool arguments only, no automatic pagination, no member name or id in a tracked file, inside the live budget. | member rosters | 2026-09-24 | [2026-09-24-rulings-search-verticals-rosters-passive-costs.md](2026-09-24-rulings-search-verticals-rosters-passive-costs.md)<br>*Rosters he can open himself* |
| `THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET` | A third party's profile (/in/<slug>/) may be loaded only inside an outward act whose target the operator names in that call: slug from tool arguments only, never for a measurement, the shaper name-free. Search-admission condition 5 stands. | third-party profiles inside outward acts | 2026-09-24 | [2026-09-24-rulings-notify-veto-and-who-which.md](2026-09-24-rulings-notify-veto-and-who-which.md)<br>*A third party's profile, inside his own outward act* |
| `NAMED-PROFILE-READ-BEHIND-A-GRANT` | A read of a member's profile he names in the call -- by link or member id, never a name read off a page -- is built behind the single-use grant, its preview stating that LinkedIn may show the member the view; declared fields leave as people records; never for a measurement. | a third-party profile he names | 2026-09-28 | [2026-09-28-rulings-named-profile-read.md](2026-09-28-rulings-named-profile-read.md)<br>*His answer* |
| `READ-PAST-AN-ACT-SUBSTRING` | A refused substring whose recorded ground is an ACT -- sending, following, applying -- does not bar the READ of his own page that carries it: one exact anchored pattern, a control shown failing, the press gate still refusing every control. Not for a GET that changes state, a credential, recovery, session or security surface, a sign-in challenge, or a refusal grounded in an operator's ruling. | substrings written to stop an act | 2026-09-28 | [2026-09-28-rulings-build-classes.md](2026-09-28-rulings-build-classes.md)<br>*5. Reading past a substring written to stop an act* |
| `APPLY-FLOW-IS-THE-APPLICATION` | Opening the Easy Apply flow is the first step of an application, so its read stays refused; the daily-limit row waits on the limit being reached. | the Easy Apply flow | 2026-10-10 | [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md)<br>*9. Opening the apply flow is the application* |
| `CONTENT-VERTICAL-NOT-ALL-RESULTS` | D2-SEARCH-VERTICALS-WIDENED does not reach the mixed /search/results/all/ page. The hashtag row M C93 is served under D6 by the content vertical, /search/results/content/?keywords=<hashtag>, admitted by its own exact pattern under D1-SEARCH-AS-READS's three conditions with /all/ shown still refused; M C70 shares it, and post text returns under THIRD-PARTY-TEXT-AT-RUNTIME. | the content search vertical | 2026-10-10 | [2026-10-10-rulings-lane-a-questions.md](2026-10-10-rulings-lane-a-questions.md)<br>*5. Content search, not all-results search* |
| `CREDENTIAL-ADJACENT-STAYS-REFUSED` | His stored applicant sign-ins for other sites (P M9, J 77) are treated as credential-adjacent and stay refused -- an inference, held on purpose to be conservative -- reopened when a capture shows the page holds no credential or secret. | stored applicant sign-ins for other sites | 2026-10-10 | [2026-10-10-rulings-lane-a-questions.md](2026-10-10-rulings-lane-a-questions.md)<br>*3. Credential-adjacent pages stay refused* |
| `NAMED-ADDRESS-NEEDS-LOG-REDACTION` | A page whose address carries a person's or a publication's name (M C101's newsletter page) is admitted only after every log line that records a page load writes that route's address as a shape, never the slug; until the redaction is built and shown failing first, the row is GAP on that blocker. | addresses that carry a name | 2026-10-10 | [2026-10-10-rulings-lane-a-questions.md](2026-10-10-rulings-lane-a-questions.md)<br>*4. A page whose address names a person is read only through a redacted log* |
| `NAMED-PROFILE-DETAIL-PAGES` | The read of a profile he names includes that same profile's own detail pages (/in/<the same slug>/details/<section>/), one load per call, behind the same single-use grant and the same preview warning; any other slug and any non-details path stay refused. | a third-party profile he names | 2026-10-10 | [2026-10-10-rulings-named-profile-detail-pages.md](2026-10-10-rulings-named-profile-detail-pages.md)<br>*The ruling* |
| `NAMED-SETTINGS-PAGES-RATIFIED` | Each settings page lane A admitted by its exact address in its own commit -- N 39, P P15 and /jobs/application-settings/ -- is within ONE-NAMED-SETTINGS-PAGE-AT-A-TIME; this is the second decision that one asks for, with HIS-OWN-SETTINGS-NOT-OUTWARD, and no pattern widens. | his named settings pages | 2026-10-10 | [2026-10-10-rulings-lane-a-questions.md](2026-10-10-rulings-lane-a-questions.md)<br>*2. One named settings page per commit is within the ruling* |
| `RECEIVED-INVITATIONS-READ-STAYS-ADMITTED` | His received-invitations tab (N 13, N 14, N 19) stays admitted. A change a read makes to an invitation's seen state is a passive cost, recorded on those rows as UNMEASURED and reopened when a capture shows the sender can see it. | his received invitations | 2026-10-10 | [2026-10-10-rulings-lane-a-questions.md](2026-10-10-rulings-lane-a-questions.md)<br>*1. Received invitations stay admitted* |

### read results

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `NAMES-AT-RUNTIME` | A read whose capability is people, or which items of other people's content, RETURNS them as its result -- names, and group and event titles -- with the risks mitigated at runtime. What is stored is unchanged: no third party's name in a tracked file. | people, groups and events | 2026-09-24 | [2026-09-24-rulings-names-at-runtime.md](2026-09-24-rulings-names-at-runtime.md)<br>*Names at runtime* |
| `PEOPLE-DATA-MITIGATIONS` | People data is returned under six mitigations, each enforced by code and a test: declared fields only; sanitised and marked untrusted; never stored; bounded to one page per call; visible only (no de-anonymising); never a target by itself. | people, groups and events | 2026-09-24 | [2026-09-24-rulings-names-at-runtime.md](2026-09-24-rulings-names-at-runtime.md)<br>*How people data is returned* |

### reads

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `FIXED-UI-LABEL-MATCH` | The people search's Actively-hiring filter is matched by its exact LinkedIn UI label, a fixed product string, with a control showing a near-miss label is refused. | one search filter matched by its product label | 2026-10-10 | [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md)<br>*11. One filter, matched by its fixed label* |
| `THIRD-PARTY-TEXT-AT-RUNTIME` | A post's own text and an organisation Page's prose are returned at runtime as untrusted third-party text -- sanitised, bounded in length, never stored -- under PEOPLE-DATA-MITIGATIONS; the feed-content ruling still governs what is stored. | other people's text, returned at runtime | 2026-10-10 | [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md)<br>*10. A post's text, and an organisation's prose, at runtime* |
| `DOM-WAIVER-25-J110` | dom.py may hold a 25th waived page evaluate, solely J 110's page-root reader read (COMPANY_HOME_JS, moved verbatim from its branch), read-only and argued under THIRD-PARTY-TEXT-AT-RUNTIME; a 26th still needs its own ruling. | the dom.py waived-evaluate budget in tests/test_readonly.py, and its copy in tests/test_the_search_shape_reading.py | 2026-10-26 | [2026-10-26-integration-2.md](2026-10-26-integration-2.md)<br>*6. Orchestrator rulings, 2026-11-25* |
| `NAME-BEARING-ADDRESS-REDACTION-SCOPE` | The redaction of a name-bearing address reaches every tracked or CI- or console-printed record, while gitignored raw state may hold the address; the newsletter page is admitted now on its drawn slug shape, and the article page after a capture spells it. | newsletter and article pages, and what records may hold their addresses | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*6. Lane admit26's ten (23:35)* |
| `ORG-NAME-AT-RUNTIME-LINK-IF-NUMERIC` | An organisation's name may return at runtime as third-party text, and its link only when the link is numeric; N 104's bar is still unmet, so it stays GAP. | organisation identity returned at runtime | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*3. The owed registrations* |
| `RECOMMENDATIONS-DETAIL-PAGE-ADMITTED` | The named /in/me/details/recommendations/ address is admitted (the interests-page precedent); its capture records where it lands. | his recommendations detail page | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*6. Lane admit26's ten (23:35)* |
| `SCREENING-QUESTION-RECORD` | An application's screening question is returned as a new people_data record type, ScreeningQuestion, under THIRD-PARTY-TEXT-AT-RUNTIME. | screening questions as third-party text | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*4. Lane apply-26's seven (22:40, the final head at 23:08)* |
| `VERIFICATIONS-PAGE-ADMITTED` | The exact /mypreferences/d/verifications address is admitted read-only, with zero presses and a per-address exemption for 'verification'; two-step verification stays refused. | his verifications page | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*6. Lane admit26's ten (23:35)* |
| `VOLUNTEERING-BARE-SPELLING-FIRST` | His volunteering-education page is tried in its bare spelling first, the capture recording where it lands; if it does not land, his own profileId comes from tool arguments at runtime and is never stored. | his volunteering-education page (P D24) | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*6. Lane admit26's ten (23:35)* |
| `AI-EASY-APPLY-POST-FILTER` | On the AI job-search fallback, easy_apply may be honoured as a local post-filter on each card's own measured Easy Apply mark, from the one load with no re-query, named as such with counts before and after and never presented as LinkedIn's filter; the AI page's own toggle stays refused. | the job search's AI fallback, one filter | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*2. The job search's AI fallback (11:05, lane search-fix26's three questions)* |
| `RECEIVED-BADGE-IS-THE-READS-COST` | Reading his received invitations clears the pending-invitation badge; that is recorded as the read's passive cost and stated in the tool's docstring, while the sent tab and the following list keep withholding on a badge drop. | his received invitations, and the badge | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*5. Lane readers-net26's section 9 (13:31)* |
| `SEARCH-ROUTE-CLASSIC-PRIMARY` | The classic job search is the primary route while it serves; the AI search page is the fallback, and it refuses every filter not measured on it. | the job search's route, classic or AI | 2026-11-26 | [2026-11-26-rulings-search-route.md](2026-11-26-rulings-search-route.md)<br>*1. The route* |
| `SELF-PROFILE-QUERY-VARIANT-ADMITTED` | His own profile address carrying exactly one query parameter, isSelfProfile=true, is a read address in its own right: his own profile path only, that one parameter, composed by the server and never from a page, and refused unless the landing proves his own profile. | his own profile's self-profile spelling (P D25, P A25) | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*1. His own profile's self-profile spelling (10:10)* |

### reads and writes

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `SESSION-SURFACE` | Reading the active-sessions list stays GAP, admissible only as ONE named settings page after a capture proves the address is the current settings page and that loading it changes nothing; never through the legacy path. Signing out of sessions is EXCLUDED-RULED, reopened when he names it. | the active-sessions surface | 2026-10-10 | [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md)<br>*7. The sessions surface* |
| `SIGN-IN-CHALLENGES-ARE-HIS` | This server never answers a sign-in or account-recovery challenge; password and second-factor entry are the operator's own gate. EXCLUDED-RULED, reopened never by this server -- he completes them himself. | sign-in and recovery challenges | 2026-10-10 | [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md)<br>*8. Sign-in challenges are his* |

### receipts

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `FEED-CURATION-RECEIPT-NEEDS-A-CHANGE` | linkedin_mark_not_interested's receipt reads a change, never a presence (SAVE-RECEIPT-NEEDS-A-CHANGE's shape): an Undo drawn anywhere on the page before the press does not read as the item hidden. | marking a feed item not interested (N 154) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*4. Lane net7's seven (13:25, 17:20 and 17:50)* |
| `SAVE-RECEIPT-NEEDS-A-CHANGE` | linkedin_save_post's receipt reads a change, never a presence: a baseline is read before the press, and saved is reported only on more saved regions than the baseline or on the menu flipping to Unsave; otherwise not_pressed, not_landed or unverified. | saving a feed item (M C36) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*1. Lane msg7's nine (12:35, 13:30 and 17:20)* |

### session model

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `D4-NO-OWN-BROWSER-CONTEXT` | The package does not create its own browser context; it attaches to the operator's signed-in browser. P C8's download transport goes through DevTools download behaviour on the attached browser, which creates no context. | browser contexts | 2026-09-23 | [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md)<br>*D4: the package's own browser context* |

### the capture queue

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `C-J68-IDS-KEPT` | The capture lines C-J68-1 to C-J68-3 keep their ids, in the census family J 60 to J 69. | the apply-flow captures | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*4. Lane apply-26's seven (22:40, the final head at 23:08)* |

### the live plan

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `L1-D1-RIDERS-RIDE` | Live plan L1, D-1: both riders take their hosts' loads (C-B3-2 on the own-post-reactions load, C-B5-4 on C-B5-3's). | session 11's riders | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*1. The live plan's L1 rulings (lane live-prep26's plan, session 11)* |
| `L1-D2-GROUPS-FROM-HIS-MEMBERSHIPS` | Live plan L1, D-2 (b): the groups come from his memberships plus one groups search, which fires N 161. | which groups session 11 opens | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*1. The live plan's L1 rulings (lane live-prep26's plan, session 11)* |
| `L1-D3-MEDIA-CHOOSER-INTERCEPTED` | Live plan L1, D-3: a composer's media control may be pressed with the file chooser intercepted and never answered, then Escape. | composer media presses | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*1. The live plan's L1 rulings (lane live-prep26's plan, session 11)* |
| `L1-D4-NEUTRAL-READ-VALUES` | Live plan L1, D-4: read values are neutral -- session 2's organisation if recorded, else a large Page verified at runtime as not his employer, and generic keywords. | the values a session reads with | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*1. The live plan's L1 rulings (lane live-prep26's plan, session 11)* |
| `L3-OPENS-WITH-A-DRAFT-RESIDUE-READ` | Live session L3 opens with one read of the Draft tab, for any residue an earlier apply walk left. | session L3's first load | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*4. Lane apply-26's seven (22:40, the final head at 23:08)* |

### tool results

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `HIS-OWN-TEXT-AT-RUNTIME` | A tool may return text he authored or uploaded on his own account (his resume file names, his job-alert keywords) to his own session at runtime; fixtures synthetic, never in tracked files, tests, CI or console logs; one narrow door in the tool-envelope ratchet, with a control that third-party text stays refused. | his own text, at runtime | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*4. Lane readers-jobs26's three questions (12:50)* |

### tooling

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `READER-LEAK-WRITER-UNDER-THE-PACE-QUEUED` | The reader-leak baseline's writer, which under the 20 s pace drives four server helpers into a 5 s timeout and regenerates truly only with the pace at zero, is queued for the guard's next owner. | the reader-leak baseline's writer | 2026-11-26 | [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md)<br>*1. Lane build-jobs2's five (19:25)* |

### verb

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `REDACTION-FORK-CLOSED-VOCABULARY` | The redaction fork is ruled: a CLOSED VOCABULARY. | how a redacted value is spelled anywhere in output | 2026-09-03 | [2026-09-03-linkedin-gap-blockers.md](2026-09-03-linkedin-gap-blockers.md)<br>*A9. THE REDACTION FORK IS RULED: A CLOSED VOCABULARY* |
| `BOUNDARY-IS-NOT-A-REASON` | A capability's address being refused today is nearly worthless as evidence for retiring it; eleven of twelve retirement families meet only the default-closed allowlist, which decided nothing about them in particular, so no ruling may cite a no-pattern refusal as its reason. | what may be cited as the ground of a retirement | 2026-09-05 | [2026-09-05-decide-retire-rulings.md](2026-09-05-decide-retire-rulings.md)<br>*2. THE BOUNDARY IS NOT A REASON, AND ELEVEN OF THESE TWELVE CANNOT BORROW IT* |
| `SCROLL-NOT-SANCTIONED` | Infinite scroll is NOT sanctioned. Correct paging already reaches what it would buy, so the objection is SUFFICIENCY rather than safety. Three named conditions reopen it. | scrolling as a page-interaction technique | 2026-09-05 | [2026-09-05-the-scroll-ruling.md](2026-09-05-the-scroll-ruling.md)<br>*The ruling: NO, and revisit only on evidence* |
| `CANONICAL-RULING-ID` | Every ruling has ONE canonical id and every citation resolves to a SYMBOL, never to a line number and never to a re-derived phrase. Aliases are mapped, not deleted. A bare prose reason is not a citation and may not carry a verdict alone. | how any ruling is cited anywhere in this corpus | 2026-09-19 | [2026-09-19-two-census-conventions-ruled.md](2026-09-19-two-census-conventions-ruled.md)<br>*RULED* |
| `DISCLOSING-PRESS-PERMITTED` | Pressing a control that DISCLOSES content on a page already admitted is PERMITTED, under four conditions that must all hold: the page is admitted, the control matches an enumerated disclosure shape by attribute, the press is shown not to move an outward counter, and it is closed with the closure verified. | pressing a control, disclosure only | 2026-09-19 | [2026-09-19-the-disclosing-press-ruling.md](2026-09-19-the-disclosing-press-ruling.md)<br>*RULED: PERMITTED, under four conditions that must ALL hold* |
| `PROBE-MUST-NOT-TRY-REFUSED-VALUES` | The check stands and the probe must not try refused values. | what a probe may submit while measuring a boundary | 2026-09-19 | [2026-09-19-two-census-conventions-ruled.md](2026-09-19-two-census-conventions-ruled.md)<br>*RULED: THE CHECK STANDS. THE PROBE MUST NOT TRY REFUSED VALUES.* |
| `PUBLISHED-SPLIT-REPORT-NOW-GATE-LATER` | The published-split check REPORTS now and GATES once the deliberate over-runs are declared. | when a reporting check becomes a blocking gate | 2026-09-19 | [2026-09-19-the-five-requests-ruled.md](2026-09-19-the-five-requests-ruled.md)<br>*D. THE PUBLISHED-SPLIT CHECK -- RULED: report now, gate once the deliberate over-runs are declared* |
| `ERROR-MESSAGE-RULED-AT-THE-RAISE` | What the error envelope's message may carry is decided WHERE THE VALUE ENTERS THE EXCEPTION, never where it leaves. The provenance classes are not classes of exception -- a page value inside a stdlib ValueError is indistinguishable at server._error from one that is not -- so no per-class policy may live at the envelope. The package's own exception text and a library's own exception text are PUBLISHABLE; a value the PAGE chose is FORBIDDEN inside any exception, whoever authored the class. | what server._error may publish in $.message, and where that is decided | 2026-09-21 | [2026-09-21-what-the-browser-said.md](2026-09-21-what-the-browser-said.md)<br>*3.4 THE RULING, STATED ONCE SO IT CAN BE CITED* |
| `ERROR-URL-ASKED-FOR-OR-NOTHING` | The error envelope's url field carries the address this server ASKED FOR, or nothing at all. A landing is never published there; where a requested address exists in scope publishing it is REQUIRED rather than merely permitted, and where none exists the key is omitted and the landing is DESCRIBED in the hint. A descriptor never goes into the url field. | what ExtractionFailedError.url may carry, per site | 2026-09-21 | [2026-09-21-the-field-beside-the-message.md](2026-09-21-the-field-beside-the-message.md)<br>*5. THE RULING, STATED ONCE SO IT CAN BE CITED* |

### writes

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `FILE-UPLOAD-OPENED` | This server may upload a file from this machine: the operator opened file upload on 2026-09-04, in full -- profile photo, post media and message attachments. The browser's upload verb joined SANCTIONED_MUTATIONS in 615a5c4. The FILE-UPLOAD-UNSANCTIONED blocker retires and its rows do not: each still needs a performable verb and a captured file input on its own surface. No extension allowlist -- one would narrow his decision. | uploading a file from this machine | 2026-09-20 | [2026-09-20-the-decides.md](2026-09-20-the-decides.md)<br>*1. `FILE-UPLOAD-UNSANCTIONED` -- **DECIDED, 2026-09-04, BY THE OPERATOR. THE BLOCKER RETIRES; THE 15 ROWS DO NOT.*** |
| `OUTWARD-CLASSES-BUILT-BEHIND-GRANTS` | Repost or share, endorse or recommend, and delete or withdraw one of his own items are BUILT behind the single-use grant, off by default, fired only at a target he names. PERMANENTLY_FORBIDDEN keeps only entries whose grounds are mitigations. | the classes ruling (b) did not name | 2026-09-24 | [2026-09-24-rulings-names-at-runtime.md](2026-09-24-rulings-names-at-runtime.md)<br>*The outward classes ruling (b) did not name* |
| `ACCOUNT-DESTRUCTION-STAYS-MANUAL` | Merging or closing his account, and deleting the data LinkedIn holds about him, are NOT built: EXCLUDED-RULED, reopened only when he asks for one by name in the call that would make it. | his account and its data | 2026-09-27 | [2026-09-27-rulings-relation-removals-and-account-destruction.md](2026-09-27-rulings-relation-removals-and-account-destruction.md)<br>*Destroying the account or its data* |
| `PREVIEW-NAMES-THE-RESOLVED-TARGET` | A preview names whom the tool resolved -- the page-read name and headline, sanitised, marked untrusted, inside a people record -- and is returned at runtime, never written; a receipt (anything persisted after a write fires) carries only the caller-supplied target. | previews and receipts | 2026-09-27 | [2026-09-27-rulings-previews-and-receipts.md](2026-09-27-rulings-previews-and-receipts.md)<br>*A preview is the identity check, not a receipt* |
| `RELATION-REMOVALS-BUILT-BEHIND-GRANTS` | Removing a relation with a member he names -- removing a 1st-degree connection, blocking a member, removing an attendee from an event he organises -- is BUILT behind the single-use grant, off by default, fired only at the one member he names in the call, with the resolved identity reported before the act. | his relations with another member | 2026-09-27 | [2026-09-27-rulings-relation-removals-and-account-destruction.md](2026-09-27-rulings-relation-removals-and-account-destruction.md)<br>*Removing a relation with a person he names* |
| `EVERY-OUTWARD-CLASS-BUILT-BEHIND-GRANTS` | Every act toward other people -- publishing his own content and its modes, invitations that are not connection requests, RSVPs and group membership requests, reports about another member's content and their undo -- is BUILT behind the single-use grant, off by default, fired only at a target he names. It does not reach measured permanent refusals, the destruction rulings or purchases. | every act toward other people | 2026-09-28 | [2026-09-28-rulings-build-classes.md](2026-09-28-rulings-build-classes.md)<br>*1. Every outward class is built behind the grant* |
| `HIS-OWN-CURATION-NOT-OUTWARD` | Curating his own feed and items -- mute, hide, not interested, follow or unfollow from a feed item, save, a post's notification switch, the per-post controls on his own items -- is not an outward act: built behind the grant and proven with its inverse in the same session, read back. | curation of his own feed and items | 2026-09-28 | [2026-09-28-rulings-build-classes.md](2026-09-28-rulings-build-classes.md)<br>*3. Curating his own feed and items is not outward* |
| `HIS-OWN-SETTINGS-NOT-OUTWARD` | A setting of his own account is not an outward act: built behind the grant, live-proven one setting at a time by read, benign write, read back, exact restore, read back; a failed restore is STOP-ALL. Credential settings, settings that cannot be put back exactly and sensitive self-identification are built and never live-proven unless he names them. | settings of his own account | 2026-09-28 | [2026-09-28-rulings-build-classes.md](2026-09-28-rulings-build-classes.md)<br>*2. His own settings are not outward* |
| `PURCHASES-STAY-MANUAL` | A purchase -- Premium, InMail credits, ads, boosts, any paid upgrade -- is NOT built: its row is EXCLUDED-RULED, reopened when he names a purchase to automate. | purchases | 2026-09-28 | [2026-09-28-rulings-build-classes.md](2026-09-28-rulings-build-classes.md)<br>*4. Purchases stay manual* |
| `CONTACT-IMPORT-STAYS-MANUAL` | An address-book import or sync is not built: it uploads other people's contact data and completes on another domain's consent screen. EXCLUDED-RULED, reopened when he asks to import or sync his address book. | importing or syncing his address book | 2026-10-10 | [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md)<br>*5. Contact import stays manual* |
| `P-D29-BUILT-BEHIND-THE-GRANT` | Adding a LinkedIn Learning certificate to his profile is built behind the grant under EVERY-OUTWARD-CLASS-BUILT-BEHIND-GRANTS and never live-proven unless he names a certificate to add. | P D29 | 2026-10-10 | [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md)<br>*15. A broadcast edit, built behind the grant* |
| `SAFETY-REPORTS-STAY-MANUAL` | A harassment or safety report, an accusation filed through an off-product Help Center form, is not built: EXCLUDED-RULED, reopened when an in-product structured report exists or he names one. | safety reports | 2026-10-10 | [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md)<br>*16. Safety reports stay manual* |
| `AI-GENERATION-IS-A-NON-OUTWARD-WRITE` | A load that starts an AI generation on his own account, toward no person, is a non-outward write: allowed behind the grant, one capture per feature, with its quota effect recorded on the row. | AI generation loads on his own account | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*6. Lane admit26's ten (23:35)* |
| `REFUSED-APPLY-DISCARDS-ITS-DRAFT` | When linkedin_apply_job refuses mid-flow, it dismisses the flow, presses Discard and verifies the Draft tab holds nothing it left. | the apply flow's refusal path | 2026-11-25 | [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md)<br>*4. Lane apply-26's seven (22:40, the final head at 23:08)* |
| `APPLICATION-SETTINGS-WRITE` | The two switches on his application settings page are admitted in principle as his own settings, a reversible on/off pair behind the grant, proven by a live round trip; the build is deferred to the first build lane after integration 4. | his application settings switches | 2026-11-26 | [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md)<br>*4. Lane readers-jobs26's three questions (12:50)* |
| `GROUP-POST-AUDIENCE-FROM-ITS-TRIGGER` | M C64's audience is read off the group page's own trigger, "Start a public post", on two conditions: the preview shows that label verbatim before the grant, and the act fires only on his explicit order for a group he names. | a post in one group (M C64) | 2026-11-26 | [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md)<br>*5. Lane build-msg2's five (22:33)* |
| `RECEIVED-LEAF-SERVES-THE-INVITATION-WRITES` | The shared invitation_manager._RECEIVED_PATHS is accepted as built: the accept and ignore writes (N 15, N 16) proceed on /mynetwork/invitation-manager/received/, where LinkedIn now lands; the target stays the one the operator names, the grant and press gates are unchanged, and the widening is confined to the invitation manager. | the invitation acts' landing veto (N 15, N 16) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*4. Lane net7's seven (13:25, 17:20 and 17:50)* |
| `SAVE-POST-UNDER-OWN-CURATION` | linkedin_save_post saves one feed item he names, behind the grant, in mark_not_interested's shape under HIS-OWN-CURATION-NOT-OUTWARD; the item is the caller's named target, never the page's; M C37 rides M C36's first live fire in session 14 (save, read the drawn Unsave, unsave), attended. | saving a feed item he names (M C36, M C37) | 2026-11-27 | [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md)<br>*1. Lane msg7's nine (12:35, 13:30 and 17:20)* |

---

## 2. THE ALIAS MAP -- every other name a registered ruling wears

`CANONICAL-RULING-ID` rules that aliases are KEPT, not deleted: *"they are how existing readers find the rule, and deleting them would strand every document that uses one. They are mapped, and the map is the artifact."* **This table is that artifact.** If you arrived with a name from an old document, find it here.

| you may have seen it called | canonical id |
|---|---|
| #1 publish a post | `COMPOSER-IS-THE-REFUSAL-NOT-THE-ADDRESS` |
| #2 comment on an item | `PERMALINK-READ-IS-ALLOWED` |
| #3 react to an item | `PERMALINK-READ-IS-ALLOWED` |
| #4 edit a profile field | `PROFILE-EDITOR-ADDRESSES-ALLOWED` |
| #6 change a setting | `ONE-NAMED-SETTINGS-PAGE-AT-A-TIME` |
| #7 send a connection invitation | `INVITATION-TARGETING-IS-CALL-TIME` |
| #9 send a message / InMail | `DO-NOT-OPEN-MESSAGING` |
| $.message | `ERROR-MESSAGE-RULED-AT-THE-RAISE` |
| 3.10 | `MESSAGING-SETTINGS-CAPABILITY-LEVEL` |
| a GAP with a NAMED BLOCKER | `EXCLUDED-RULED-ADMISSION` |
| A9 | `REDACTION-FORK-CLOSED-VOCABULARY` |
| ANALYTICS-CONTROLS-UNPRESSED | `DISCLOSING-PRESS-PERMITTED` |
| blocker 16 | `MENTION-COMPOSITION-RULING` |
| blocker 49 | `FEED-CONTENT-READ-RULING` |
| condition 2 amended | `SEARCH-CONDITION-2-CLOSED` |
| condition 5 | `SEARCH-ADMISSION-APPROVED-FIVE-CONDITIONS` |
| container and content | `CONTAINER-EXCLUSION-PROPAGATES-ONLY-IF-UNREACHABLE` |
| counts and relations only | `FEED-CONTENT-READ-RULING` |
| D1 | `D1-SEARCH-AS-READS` |
| D2 | `D2-SEARCH-VERTICALS-WIDENED` |
| D3 | `D3-UNREGISTERED-REFUSAL-IS-NOT-A-RULING` |
| D4 | `D4-NO-OWN-BROWSER-CONTEXT` |
| D5 | `D5-PASSIVE-COST-IS-NOT-A-ROW` |
| D6 | `D6-CAPABILITY-OVER-AFFORDANCE` |
| dark mode | `ONE-NAMED-SETTINGS-PAGE-AT-A-TIME` |
| DECIDE not MEASURE | `GROUPS-ADDRESS-BUYS-NO-WRITE` |
| decide-retire-rulings section 2 | `BOUNDARY-IS-NOT-A-REASON` |
| DEFECT ONE | `GATE-IS-SAFE-AND-BLIND` |
| ERROR-MESSAGE-PROVENANCE | `ERROR-MESSAGE-RULED-AT-THE-RAISE` |
| ERROR-URL-PER-SITE | `ERROR-URL-ASKED-FOR-OR-NOTHING` |
| FILE-UPLOAD-UNSANCTIONED | `FILE-UPLOAD-OPENED` |
| FORBIDDEN-CLASS-FIX-LANDED | `INCIDENTAL-CAPTURE-IS-NOT-A-RULING` |
| incidental capture | `INCIDENTAL-CAPTURE-IS-NOT-A-RULING` |
| L118-123 | `EXCLUDED-RULED-ADMISSION` |
| lead-rulings-round-two section 8 | `STANDING-SHAPE-OF-A-WRITE-RULING` |
| linkedin_publish_post | `COMPOSER-IS-THE-REFUSAL-NOT-THE-ADDRESS` |
| linkedin_send_message | `DO-NOT-OPEN-MESSAGING` |
| M C10 | `MENTION-COMPOSITION-RULING` |
| M C28 | `MENTION-COMPOSITION-RULING` |
| M C43 | `FEED-CONTENT-READ-RULING` |
| M C74 | `FEED-CONTENT-READ-RULING` |
| MATCH-DETAILS-COLLAPSED | `DISCLOSING-PRESS-PERMITTED` |
| MESSAGING-SETTINGS | `MESSAGING-SETTINGS-CAPABILITY-LEVEL` |
| N 163 re-cost | `GROUPS-ADDRESS-BUYS-NO-WRITE` |
| names at runtime | `NAMES-AT-RUNTIME` |
| NAVIGATION-CEILING-PER-CALL-WITH-ONE-DECLARED-FAN-OUT | `NAVIGATION-CEILING-PER-TOOL-CALL` |
| one canonical id | `CANONICAL-RULING-ID` |
| OWNED-BY-A-SIBLING-SLICE | `DUPLICATE-ROW-IS-MARKED-NEVER-DELETED` |
| P I12 -> J99 | `CONTAINER-EXCLUSION-PROPAGATES-ONLY-IF-UNREACHABLE` |
| P L2 -> L2 + L2b | `COMPOUND-ROW-SPLITS-ONLY-ON-STATE` |
| press.disclose | `DISCLOSING-PRESS-PERMITTED` |
| Q-ABSENT-ON-HIS-ACCOUNT | `ABSENT-ON-HIS-ACCOUNT-PER-ROW` |
| Q-AD-HIDE-TARGET | `AD-HIDE-AT-HIS-NAMED-AD` |
| Q-AD-LIBRARY-PURPOSE | `AD-LIBRARY-OUTSIDE-PURPOSE` |
| Q-AI-COACH-QUESTION | `AI-COACH-OUTSIDE-PURPOSE` |
| Q-AI-GENERATING-LOADS | `AI-GENERATION-IS-A-NON-OUTWARD-WRITE` |
| Q-ARTICLE-COMPOSER-DISCLOSURES | `ARTICLE-COMPOSER-ONE-CAPTURE` |
| Q-ARTICLE-MANAGE-DRAFTS | `ARTICLE-EDITOR-PRESSES` |
| Q-ARTICLE-NEXT-NEEDS-A-TITLE | `ARTICLE-EDITOR-PRESSES` |
| Q-COMMENT-ANALYTICS-METRIC | `COMMENTS-METRIC-NOT-ABSENT-ON-ONE-DROPDOWN` |
| Q-CONVERSATION-MENU-STATE | `CONVERSATION-MENU-PREVIEW-PRESS` |
| Q-COURSE-VIDEO-PROGRESS | `COURSE-VIDEO-OUTSIDE-PURPOSE` |
| Q-EDITOR-TYPEAHEAD | `EDITOR-TYPEAHEAD-SANCTIONED` |
| Q-FEED-UNFOLLOW-AIM | `FEED-UNFOLLOW-ROUTES-UNDER-D6` |
| Q-FILTER-FIRES-SEARCH-CAP | `FILTER-REQUERY-COUNTS-AS-A-SEARCH` |
| Q-GROUP-CONTENT-SEARCH-ABSENT | `GROUP-SEARCH-MEASURED-ABSENT` |
| Q-J169-SENIORITY | `J169-SPLITS-SENIORITY-REAIMED-UNDER-D6` |
| Q-J170-ROW-CONTROL | `JOB-ALERT-ROW-CONTROL-ATTENDED` |
| Q-J37-SPLITS | `J-37-SPLITS` |
| Q-LEARNING-SPLITS | `LEARNING-ROWS-SPLIT` |
| Q-MEDIA-POST-AUDIENCE | `MEDIA-POST-SAME-REFUSAL` |
| Q-MESSAGE-SEARCH-TYPING | `MESSAGE-SEARCH-CAPTURE-FIRST` |
| Q-NAME-BEARING-ADDRESS-REDACTION | `NAME-BEARING-ADDRESS-REDACTION-SCOPE` |
| Q-NEWSLETTER-CREATE-FORM | `ARTICLE-EDITOR-PRESSES` |
| Q-NOTIFICATION-KEY | `M-C97-LINK-KEYED-DELETE` |
| Q-ONE-SHOT-FEEDBACK | `J-163-RECEIPT-ONLY-WRITE` |
| Q-OPEN-TO-WORK-EDITOR | `OPEN-TO-WORK-EDITOR-ATTENDED-ONLY` |
| Q-ORG-IDENTITY | `ORG-NAME-AT-RUNTIME-LINK-IF-NUMERIC` |
| Q-OWN-PROFILE-SCROLL | `OWN-PROFILE-SCROLL-SANCTIONED` |
| Q-P-N22-SPLITS | `P-N22-SPLITS` |
| Q-RECOMMENDATIONS-DETAIL-PAGE | `RECOMMENDATIONS-DETAIL-PAGE-ADMITTED` |
| Q-REFOLLOW-AIM | `REFOLLOW-FROM-HIS-NAMED-PROFILE` |
| Q-REINVITE-COMPOSITION | `REINVITE-BY-CALLER-COMPOSITION` |
| Q-RESUME-BUILDER | `RESUME-BUILDER-UNDER-ARTICLE-COMPOSER-CAPTURE` |
| Q-RETIRED-ROUTE-ROWS | `RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE` |
| Q-SCHEDULED-LIST-PRESS | `SCHEDULED-LIST-AS-A-SHIPPED-READ` |
| Q-SEARCH-ROUTE-POLICY | `SEARCH-ROUTE-CLASSIC-PRIMARY` |
| Q-SELF-PROFILE-QUERY-VARIANT | `SELF-PROFILE-QUERY-VARIANT-ADMITTED` |
| Q-SELF-ROOT-FORM-LINKS | `SELF-ROOT-LINK-PRESS-BY-EXACT-MATCH` |
| Q-VERIFICATION-DELETE | `VERIFICATION-DELETE-HELD` |
| Q-VERIFICATIONS-PAGE | `VERIFICATIONS-PAGE-ADMITTED` |
| Q-VOLUNTEERING-ID-FROM-HIS-ARGUMENTS | `VOLUNTEERING-FALLBACK-BOUNDARY` |
| Q-VOLUNTEERING-PROFILE-ID | `VOLUNTEERING-BARE-SPELLING-FIRST` |
| R11 | `MESSAGING-SETTINGS-CAPABILITY-LEVEL` |
| R9 | `DO-NOT-OPEN-MESSAGING` |
| RECEIVED-BADGE-IS-THE-READ'S-COST | `RECEIVED-BADGE-IS-THE-READS-COST` |
| request 1 | `CONVERSATION-OVERFLOW-BOTH-WAVES-RIGHT` |
| request 4 | `CENSUS-OUTRANKS-LEDGER` |
| request A | `MAP-CONVENTION-AT-HEAD-MEMBERSHIP` |
| request B | `N61-REMOVED-FROM-HASHTAG-EXISTENCE` |
| request C | `CONVERSATION-OVERFLOW-BOTH-WAVES-RIGHT` |
| request D | `PUBLISHED-SPLIT-REPORT-NOW-GATE-LATER` |
| request E | `CREATOR-HUB-AND-POST-COMMENT-LEDGER-OVERCOUNTS` |
| ruling (b) | `WRITE-CLASS-B` |
| safety is a property of the code | `STANDING-SHAPE-OF-A-WRITE-RULING` |
| SCROLL | `SCROLL-NOT-SANCTIONED` |
| section 7 of lead-rulings-round-two | `SCROLL-NOT-SANCTIONED` |
| server.py::linkedin_update_setting | `MESSAGING-SETTINGS-CAPABILITY-LEVEL` |
| settings family | `MESSAGING-SETTINGS-CAPABILITY-LEVEL` |
| split or leave whole | `COMPOUND-ROW-SPLITS-ONLY-ON-STATE` |
| the 89 sub-expressions | `ERROR-MESSAGE-RULED-AT-THE-RAISE` |
| the absence convention | `MEASURED-ABSENT-OR-PRECONDITION` |
| THE BOUNDARY IS NOT A REASON | `BOUNDARY-IS-NOT-A-REASON` |
| the census's own rule | `EXCLUDED-RULED-ADMISSION` |
| the class-filter convention | `INCIDENTAL-CAPTURE-IS-NOT-A-RULING` |
| the compound rows | `COMPOUND-ROW-SPLITS-ONLY-ON-STATE` |
| the deduplication ruling | `DUPLICATE-ROW-IS-MARKED-NEVER-DELETED` |
| the disclosing press | `DISCLOSING-PRESS-PERMITTED` |
| the field beside the message | `ERROR-URL-ASKED-FOR-OR-NOTHING` |
| the groups eight | `GROUPS-ADDRESS-BUYS-NO-WRITE` |
| the guard contradiction | `MUST-STAY-REFUSED-ENTRIES-COME-OUT` |
| the ledger's own rule | `EXCLUDED-RULED-ADMISSION` |
| the line I did not cross | `NO-IRREVERSIBLE-WRITE-IS-FIRED` |
| the operator gate | `NO-IRREVERSIBLE-WRITE-IS-FIRED` |
| the permalink ruling | `PERMALINK-READ-IS-ALLOWED` |
| the positional dialect | `POSITIONAL-DIALECT-SHIP-THE-DETECTOR` |
| the search admission | `SEARCH-ADMISSION-APPROVED-FIVE-CONDITIONS` |
| the standing order | `NO-IRREVERSIBLE-WRITE-IS-FIRED` |
| the standing shape | `STANDING-SHAPE-OF-A-WRITE-RULING` |
| the twenty sites | `ERROR-URL-ASKED-FOR-OR-NOTHING` |
| the upload sanction | `FILE-UPLOAD-OPENED` |
| the write class (b) | `WRITE-CLASS-B` |
| the write-partition's section 4.4.2 question | `COMPOUND-ROW-SPLITS-ONLY-ON-STATE` |
| third-party exception text | `ERROR-MESSAGE-RULED-AT-THE-RAISE` |
| two capabilities one row | `COMPOUND-ROW-SPLITS-ONLY-ON-STATE` |
| two-census-conventions section 1 | `CANONICAL-RULING-ID` |
| two-census-conventions section 2 | `CONTAINER-EXCLUSION-PROPAGATES-ONLY-IF-UNREACHABLE` |
| two-census-conventions section 3 | `INCIDENTAL-CAPTURE-IS-NOT-A-RULING` |
| what the browser said | `ERROR-MESSAGE-RULED-AT-THE-RAISE` |

---

## 3. NOTES ON INDIVIDUAL RULINGS

**`ABSENT-ON-HIS-ACCOUNT-PER-ROW`** -- Orchestrator's call on lane build-p26, applying MEASURED-ABSENT-OR-PRECONDITION. Applied at integration 3: P A14 and P A15 to MEASURED-ABSENT (not drawn for his account), P K8 waiting on a PRECONDITION (a badge he lacks). Reopener: per row, the one the row names.

**`ACCOUNT-DESTRUCTION-STAYS-MANUAL`** -- Orchestrator's call applying the operator's 08:11 principle; overridable. Decides P N27 and P P2, and adds a capability-level ground to P N28.

**`AD-DATA-GRAIN`** -- Orchestrator's call on lane readers-net26's section 9, question 4, applying GRAIN-FOLLOWS-WHAT-THE-PLATFORM-DRAWS. No cell changed. Reopener: a row's pages admitted and its settings' states diverging.

**`AD-HIDE-AIM-HELD`** -- Orchestrator's call for lane build-net2 (17:10), registered at integration 5; option (b) declined. N 200 held at GAP by that lane, merged in integration 6. AD-HIDE-AT-HIS-NAMED-AD still stands: a hide fires only at an ad he names. The row's cells are build-net2's. Reopener: a measured disclosure shape for the ad control-menu trigger.

**`AD-HIDE-AT-HIS-NAMED-AD`** -- Orchestrator's call on the lane-K ledger's question; applied by lane readers-net26's second round (N 200 BUILD behind the grant). Its aim is held by AD-HIDE-AIM-HELD (17:10): no reader returns an ad urn without pressing ads he did not name. Reopener: none stated.

**`AD-LIBRARY-OUTSIDE-PURPOSE`** -- Orchestrator's call on lane admit26, applying OUTSIDE-THE-PRODUCT-PURPOSE. Reopener: he asks.

**`ADMIT-NOW-LANDING-IN-SESSION-14`** -- Orchestrator's answer to lane msg7's question 1 (12:35). Its scope includes lane jobs7's J 175 admission, the Learning saved list (queue line C-LRN-3). The hashtag address was held by HASHTAG-ADMISSION-WAITS-FOR-A-REFUSING-BASIS. Reopener: a landing check that fails (the admission is reverted).

**`AI-COACH-OUTSIDE-PURPOSE`** -- Orchestrator's call on lane admit26, applying OUTSIDE-THE-PRODUCT-PURPOSE. Reopener: he asks.

**`AI-EASY-APPLY-POST-FILTER`** -- Orchestrator's call on lane search-fix26's Q1; built in its second round. Moves no row. Reopener: for the page's own toggle, a capture that measures its effect.

**`AI-GENERATION-IS-A-NON-OUTWARD-WRITE`** -- Orchestrator's call on lane admit26. Its 8 rows are left at their ruling step at integration 3: the read boundary still refuses their addresses, and the ledger has no capture class for a write behind the grant. Reopener: none stated.

**`APPLICATION-SETTINGS-WRITE`** -- Orchestrator's call on lane readers-jobs26's Q3. Built by lane build-jobs2 (J 74, J 76, P M7, P M8 COVERED-UNFIRED; the write door's excusal on the spec, WRITE-DOOR-EXCUSAL-ON-THE-SPEC) and merged in integration 6. Reopener: none stated.

**`APPLY-DRY-WALK-FIRES-THE-STEP-ROWS`** -- Orchestrator's call on lane apply-26. Applies APPLY-FLOW-IS-THE-APPLICATION. Moves no row until the walk is fired. Reopener: none stated.

**`APPLY-FLOW-IS-THE-APPLICATION`** -- Orchestrator's call; overridable. Decides J 82.

**`ARTICLE-COMPOSER-CAPTURE`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable.

**`ARTICLE-COMPOSER-ONE-CAPTURE`** -- Orchestrator's call on the lane-K ledger's question, applying ARTICLE-COMPOSER-CAPTURE; applied by lane readers-msg26's second round as capture C-MSG26-4. Reopener: none stated.

**`ARTICLE-EDITOR-PRESSES`** -- Orchestrator's answer to lane msg7's question 5 (12:35). M C46 rides M C44. Reopener: none stated.

**`B5-GROUP-COMPOSER-OPENS-EMPTY`** -- Lane B5's second answer, registered at integration 3. Applies ARTICLE-COMPOSER-CAPTURE. Reopener: none stated.

**`B5-INVITE-DIALOG-IS-A-LIST`** -- Lane B5's third answer, registered at integration 3. Reopener: none stated.

**`B5-RAIL-JOIN-DOES-NOT-DISCHARGE`** -- Lane B5's first answer, recorded 2026-10-10 19:18, registered at integration 3. Applies PAGE-MAY-VETO-NEVER-SUPPLY. Reopener: none stated.

**`BOUNDARY-IS-NOT-A-REASON`** -- The application of EXCLUDED-RULED-ADMISSION that section 5.4a found. It quotes the census rule rather than restating it.

**`BUDGET-ONE-ACCOUNT-40`** -- Orchestrator's call (17:52), overridable by him; it closes the 15:36 open question and is the stricter reading of LIVE-BUDGET-40-LOADS. Two separate budgets only on his word. Folded into the session-12 plan by lane s12-prep; at 18:40 the orchestrator confirmed that the harness's own session file holds session rules, not an account count, so it is not a second ledger. Moves no row. Reopener: his word.

**`C-J68-IDS-KEPT`** -- Orchestrator's call on lane apply-26. Applied at integration 3: the ids kept, the ranks renumbered on merge. Reopener: none stated.

**`CALLER-COMPOSITION-UNDER-D6`** -- Orchestrator's call applying D6-CAPABILITY-OVER-AFFORDANCE; overridable.

**`CANONICAL-RULING-ID`** -- THIS FILE IS THAT RULING'S ARTIFACT. It is why the register prints a section heading and never a line number, and why the aliases column exists at all.

**`CAPTURE-PRESS-UNDER-PROBE-RULE`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. The capture is the evidence a tool's basis entry is built from.

**`CAPTURE-SHOWS-READER-BLIND-DEMOTES`** -- Orchestrator's answer to lane msg7's question 4 (12:35): M C75 demoted on session 12's server-driven /notifications/ capture (the shipped harvest read 0); N 20 and N 45 kept COVERED-UNFIRED with the evidence; the server-driven read built by that lane, session 5's 9 of 9 the control. Reopener: a fire that re-proves the rows (session 14).

**`COMMENTS-METRIC-NOT-ABSENT-ON-ONE-DROPDOWN`** -- Orchestrator's answer to lane msg7's question 6, first half (12:35), which gave it no id; the id is integration 7's. CREATOR-IDEAS-NOT-ABSENT-ON-ONE-SURFACE rests on it. Reopener: none stated.

**`COMPOUND-ROW-SPLITS-ONLY-ON-STATE`** -- THE EXACT COMPLEMENT OF `DUPLICATE-ROW-IS-MARKED-NEVER-DELETED` above -- that one governs two rows describing one capability, this one governs one row describing two. They were filed together for that reason. The asymmetry it rests on is MEASURED rather than argued: `reader_closable_blockers.DIRECTIONS` normalises four spellings of a both-DIRECTION onto `R+W`, while `count_census_states.classify` answers a two-STATE cell by silently taking the first by textual order or by dropping the row out of the census, raising no dialect either way. Direction can be told the truth in the cell; state cannot. The corpus had already decided this eight times without naming it -- seven non-splits (`P M6` `P M9` `P M11` `M M28` `M C47` `N 125`, plus `J 71` declining in writing) and the one split, `P L2` -> `L2` + `L2b`, whose halves are BOTH reads and which therefore refutes a direction-based rule.

**`CONNECTIONS-CONTROLS-MEASURED-ABSENT`** -- Orchestrator's answer to lane net7 (13:25). N 27 applied; N 24 stays GAP, its second condition failing (13 aria-expanded triggers in main), with a session-14 capture of its two pills. Reopener: none stated.

**`CONTACT-IMPORT-STAYS-MANUAL`** -- Orchestrator's call; overridable. Decides N 106, N 108 and P N21.

**`CONTACTS-PAGE-FROM-THE-SETTINGS-NAV`** -- Orchestrator's answer to lane net7 (13:25), with the 13:21 condition and the 14:12 order to measure it; settings7 admitted /mynetwork/settings/manage-syncing with one exemption and measured no press basis there (14:32); net7 re-aimed both rows onto settings7's queue line. Reopener: none stated.

**`CONTAINER-EXCLUSION-PROPAGATES-ONLY-IF-UNREACHABLE`** -- Built ON `P I12` as a SOUND exclusion: *zero of 237 urls reach one* is ground four of EXCLUDED-RULED-ADMISSION. Two later documents call `P I12` a miscategorisation; see the register's DISPUTED note in the report for this wave.

**`CONTENT-VERTICAL-NOT-ALL-RESULTS`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable.

**`CONVERSATION-MENU-PREVIEW-PRESS`** -- Orchestrator's call on the lane-K ledger's question (the similar-jobs trial-press precedent; the J 163 class for delete); applied by lane readers-msg26's second round (BUILD on its session-11 capture). Built by lane build-msg2 (M M26, M M27, M M29, M M31 COVERED-UNFIRED) and merged in integration 6. Reopener: none stated.

**`COURSE-VIDEO-OUTSIDE-PURPOSE`** -- Orchestrator's call on lane admit26, applying OUTSIDE-THE-PRODUCT-PURPOSE. Reopener: he asks.

**`CREATOR-IDEAS-NOT-ABSENT-ON-ONE-SURFACE`** -- Orchestrator's answer to lane prof7 on rank 111 (13:00). Reopener: none stated.

**`CREDENTIAL-ADJACENT-STAYS-REFUSED`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. Rests on inference, not measurement.

**`CREDENTIAL-SETTINGS-NEED-THE-OPERATOR`** -- The cannot-be-undone arm of OUTWARD-ACTS-NEED-THE-OPERATOR.

**`D1-SEARCH-AS-READS`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable.

**`D2-SEARCH-VERTICALS-WIDENED`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. Question: _audit/2026-09-21-the-read-triage.md D2.

**`D3-UNREGISTERED-REFUSAL-IS-NOT-A-RULING`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. Question: _audit/2026-09-21-the-read-triage.md D3. Governs N 99, N 177 and N 178.

**`D4-NO-OWN-BROWSER-CONTEXT`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. Question: _audit/2026-09-21-the-read-triage.md D4.

**`D5-PASSIVE-COST-IS-NOT-A-ROW`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. Question: _audit/2026-09-21-the-read-triage.md D5.

**`D6-CAPABILITY-OVER-AFFORDANCE`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. Question: _audit/2026-09-21-the-read-triage.md D6. Governs N 132 and J 107.

**`DOM-WAIVER-25-J110`** -- Orchestrator's call, answering integration 2's question about the budget move its J 110 fix made by commit (24 -> 25). Applies THIRD-PARTY-TEXT-AT-RUNTIME.

**`EDITOR-TYPEAHEAD-ONLY-ATTENDED`** -- Orchestrator's answer to lane s12-prep's third call, as that lane's plan records it; the merge-notes entries do not carry it in words. The capture itself is EDITOR-TYPEAHEAD-SANCTIONED's (P A11, P A13, P A17 on C-B1a); this adds only when it runs. Moves no row. Reopener: none stated.

**`EDITOR-TYPEAHEAD-SANCTIONED`** -- Orchestrator's call on lane build-p26. Moves P A11, P A13, P A17 to CAPTURE on C-B1a. Reopener: any autosave sign.

**`ERROR-MESSAGE-RULED-AT-THE-RAISE`** -- THE SIBLING OF `ERROR-URL-ASKED-FOR-OR-NOTHING`, and it goes the OTHER WAY for a stated reason rather than by temperament. The url field could be ruled PER SITE because every value feeding it is an address this package composed or read; `$.message` cannot, because `_error` holds only `type(exc)` and `str(exc)` and the provenance of what that text QUOTES is not among them. So the ruling moves the decision to the raise, which is where the corpus had already put it three times without naming it: `coerce.py`, `press.disclose` and `landing.py`. It also DECLINES the sibling's own recommendation to make the twelve `dom.py` messages type-only -- all twelve are inside `tests/test_readers_emit_no_page_string.py`'s driven subject set and green (4 clean, 8 returns_text, 0 not_driven), so the payload class is already closed for them and type-only would delete twelve diagnoses to close a channel no needle travels. What it SHIPPED is the other end of the pipe: `tests/test_tool_envelopes_emit_no_page_string.py`, because the reader guard discovers only `async def` functions taking a `page` and the 48 tool bodies that funnel into `_error` are therefore outside it, permanently.

**`ERROR-URL-ASKED-FOR-OR-NOTHING`** -- THE FAILURE-PATH COUNTERPART OF THE `source_url` SPLIT RULING in `tests/test_the_source_url_split_was_never_ruled.py`, which is NOT registered here because it lives as a test rather than as an audit passage. Same kind of value -- the address a read landed on -- in several of the SAME functions, and the two were ruled by different files that did not know about each other: `linkedin_my_profile` was declared SHAPED on its success path and published its landing raw on its failure path, in one function, for weeks. That ruling supplied the METHOD used here (a per-site declaration with a written reason, a count per site, a relay pinned as a relay, and drift failing in BOTH directions) and its prohibition is what stopped this wave wrapping all twenty: *wrapping a deliberate publication is as much a defect as leaking an accidental one.* The count each way is 12 withheld, 7 published, 1 relay.

**`EVERY-OUTWARD-CLASS-BUILT-BEHIND-GRANTS`** -- Orchestrator's call applying WRITE-CLASS-B and the operator's 08:11 principle; overridable. Extends OUTWARD-CLASSES-BUILT-BEHIND-GRANTS to every outward class.

**`EXACT-MATCH-REFUSES-ANY-WHITESPACE`** -- Orchestrator's fix-round order (17:20) on the cold verifier's MAJOR (str.strip dropped the Unicode whitespace the URL parser keeps); fixed red first by lane prof7 (4f84353) and merged in integration 7. live-s13's session-14 reviewer re-checks it where the runner imports it. Reopener: none stated.

**`EXCLUDED-RULED-ADMISSION`** -- Written twice, once per slice, in near-identical words; `_audit/_census/profile.md` carries the twin. This is the ORIGIN of the forbidden-substring question and it already answers it: a substring entry counts only when it is one of the four WRITTEN grounds, i.e. when it was aimed at the capability.

**`FAILED-REPROOF-DEMOTES`** -- Orchestrator's call (23:05), for M C41, in the shape of Q-RETIRED-ROUTE-ROWS; applied at integration 6 to M C41, whose re-proof, session 12's E1, refused at loads 1 and 2. CAPTURE-SHOWS-READER-BLIND-DEMOTES (integration 7) applies its shape to M C75, whose shipped reader read nothing on a live capture. Reopener: a fire that re-proves the row.

**`FEED-CONTENT-READ-RULING`** -- The ground `M C85`'s read half would rest on if that row were ever split -- see OPEN-QUESTIONS.

**`FEED-CURATION-RECEIPT-NEEDS-A-CHANGE`** -- Orchestrator's order to lane net7 (17:50), red first, before N 154's first live fire, on lane msg7's finding of the same flaw in feed_curation.verification_verdict (17:47). Reopener: none stated.

**`FEED-UNFOLLOW-ROUTES-UNDER-D6`** -- Orchestrator's answer to lane msg7's question 3 (12:35). Lane msg7 checked: no such route ships, so the step is the following-list capture. Reopener: none stated.

**`FIFTH-SEARCH-TO-PEOPLE-LABELS`** -- Orchestrator's answer to lane s12-prep's second call (17:45); applied in its round 2. Moves no row. Reopener: none stated.

**`FILE-UPLOAD-OPENED`** -- THE OPERATOR'S decision, made 2026-09-04. No committed source records his words: it is recorded by 615a5c4 and _audit/2026-09-20-the-decides.md section 1, and registered on that record. The date shown is the record's, 2026-09-20.

**`FILTER-REQUERY-COUNTS-AS-A-SEARCH`** -- Orchestrator's call, applying D1-SEARCH-AS-READS's cap of 5 test searches per session. Moves no row. Reopener: none stated.

**`FIXED-UI-LABEL-MATCH`** -- Orchestrator's call; overridable. Decides N 82.

**`GEOLOCATION-BY-D6`** -- Orchestrator's call applying D6-CAPABILITY-OVER-AFFORDANCE; overridable. Decides J 17.

**`GROUP-POST-AUDIENCE-FROM-ITS-TRIGGER`** -- Orchestrator's answer to lane build-msg2's question 3 (22:33); M C64 is COVERED-UNFIRED, receipt-only, merged in integration 6. Reopener: none stated.

**`GROUP-SEARCH-MEASURED-ABSENT`** -- Orchestrator's answer to lane msg7's question 6 (12:35), under MEASURED-ABSENT-OR-PRECONDITION; applied by that lane. Reopener: a capture that draws a group facet or a group-scoped search control.

**`GROUPS-ADDRESS-BUYS-NO-WRITE`** -- Stated in `readonly.py`'s own comment and quoted here. The companion rule that a widening is reported by what it BANKS rather than by what it UNBLOCKS sits in the same section.

**`GROW-SUGGESTIONS-BY-ADMISSION-NOT-SCROLL`** -- Orchestrator's answer to lane net7 (13:25); the address admitted by that lane on one anchored line and merged in integration 7. Reopener: none stated.

**`HASHTAG-ADMISSION-WAITS-FOR-A-REFUSING-BASIS`** -- Orchestrator's answer (13:30) to lane msg7's hold on the hashtag admission's press-gate premise. Reopener: a refusing press basis for the page (wave 8's SENSITIVITY_BASES design item).

**`HIS-OWN-CURATION-NOT-OUTWARD`** -- Orchestrator's call applying OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. An undo drawn only once proves the act only through that undo.

**`HIS-OWN-SETTINGS-NOT-OUTWARD`** -- Orchestrator's call applying OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. Settings pages are still admitted one by name.

**`HIS-OWN-TEXT-AT-RUNTIME`** -- Orchestrator's call on lane readers-jobs26's Q2; applied in its second round as the ADMITTED_OWN_TEXT door. Reopener: none stated.

**`IN-ME-NO-BLANKET-BAR`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable.

**`INBOX-SEARCH-IS-NOT-A-D1-SEARCH`** -- Orchestrator's ruling for the live lane (13:35). SEARCH-BOX-TYPING is the shape MESSAGE-SEARCH-CAPTURE-FIRST contemplates. Moves no row. Reopener: none stated.

**`INCIDENTAL-CAPTURE-IS-NOT-A-RULING`** -- THIS IS THE ANSWER TWO WAVES ESCALATED AS UNDECIDED AND A THIRD RE-DERIVED. It carries the three-way GENERAL FORM table that the 2026-09-21 re-derivation reconstructed from measurement. Its own citation is the 2026-09-03 ledger passage, so the chain is: census rule -> ledger asks -> 09-05 applies -> 09-19 RULES -> 09-21 re-derives.

**`J-110-SPLITS-HOME-AND-POSTS`** -- Orchestrator's call on lane build-jmn26, applying COMPOUND-ROW-SPLITS-ONLY-ON-STATE. Reopener: none stated.

**`J-114-SPLITS`** -- Orchestrator's call on lane readers-jobs26's Q1; applied in its second round (J 114 COVERED-UNFIRED, J 169 entered GAP). Reopener: none stated.

**`J-160-RAW-ONLY-IF-THE-PEOPLE-GATE-KEEPS-IT`** -- Orchestrator's answer to lane build-jobs2's question 4 (19:25), which gave it no id; written into the career-insights line's save cell by that lane's round 2. J 160 stays GAP. Reopener: none stated.

**`J-163-RECEIPT-ONLY-WRITE`** -- Orchestrator's call on lane build-jmn26; answers the ledger's Q-ONE-SHOT-FEEDBACK. Reopener: his order.

**`J-19-BUILT-BEHIND-THE-GRANT`** -- Orchestrator's call on lane build-jmn26, applying OUTWARD-CLASSES-BUILT-BEHIND-GRANTS. Reopener: the confirm dialog's capture.

**`J-37-SPLITS`** -- Orchestrator's answer to lane build-jobs2's question 1 (19:25), on COMPOUND-ROW-SPLITS-ONLY-ON-STATE and the J 114 / J 169 precedent; applied by that lane's round 2 and merged in integration 6. The population moved 775 -> 776 on its branch. Reopener: none stated.

**`J111-SPLITS-PRODUCTS-FROM-SERVICES`** -- Orchestrator's ruling (15:51) for integration 7 to apply, under COMPOUND-ROW-SPLITS-ONLY-ON-STATE, so lane jobs7 was not reopened; applied at integration 7: J 176 entered (the Services tab). Reopener: none stated.

**`J114-READS-ITS-OWN-TABLE`** -- Orchestrator's ruling (14:30) on lane jobs7's finding that the shipped reader read the job-openings table as headcount; applied by that lane (J 114 stays COVERED-UNFIRED, re-based, with a CORRECTS / CORRECTED BY pair) and merged in integration 7. Reopener: none stated.

**`J169-BY-ITS-OWN-WORDS`** -- Orchestrator's corrected ruling (14:05) on lane jobs7's hold. Load 20 draws both: J 169 kept them (built, COVERED-UNFIRED) and J 173 entered at GAP. Reopener: none stated.

**`J169-SPLITS-SENIORITY-REAIMED-UNDER-D6`** -- Orchestrator's answer to lane jobs7's question 1 (13:45); held by that lane (J 169 names no function half) and corrected at 14:05. Its D6 re-aim stands: J 173's step is the experience-level facet (C-J173-1). Reopener: none stated.

**`J175-ADMISSION-PASSES-NO-ACT-SUBSTRING`** -- Orchestrator's check (14:30), which gave it no id; the id is integration 7's. Measured by lane jobs7 on the shipped guards and held by tests/test_the_learning_saved_list_presses_nothing.py. Reopener: an act substring found in the address (the admission is reverted).

**`JOB-ALERT-ROW-CONTROL-ATTENDED`** -- Orchestrator's answer to lane jobs7's question 2 (13:45); queue line C-J170-1. Reopener: none stated.

**`JOB-OPENINGS-BY-FUNCTION-ADDED`** -- Orchestrator's corrected ruling (14:05) on lane jobs7's hold; J 174 entered and moved to COVERED-UNFIRED on its own field by that lane. Reopener: none stated.

**`JOBHUNT-HOME-KEEPS-ITS-MEANING`** -- Orchestrator's call on lane apply-26. Reopener: none stated.

**`JOBHUNT-ROOT-RESOLUTION-ORDER`** -- Orchestrator's call on lane apply-26, refined on its final head. Reopener: none stated.

**`KEY-SKILLS-ADD-HELD`** -- Orchestrator's answer to lane prof7 on rank 102 (13:00). Reopener: none stated.

**`KEYWORD-FIELDS-MEASURED-ABSENT`** -- Orchestrator's answer to lane net7 (13:25); applied by that lane. Reopener: none stated.

**`L1-D1-RIDERS-RIDE`** -- Orchestrator's call on the live plan's question D-1. Reopener: none stated. Moves no row: it governs session 11's loads.

**`L1-D2-GROUPS-FROM-HIS-MEMBERSHIPS`** -- Orchestrator's call on D-2. Reopener: none stated. Moves no row by itself; session 11's search fire is N 161's.

**`L1-D3-MEDIA-CHOOSER-INTERCEPTED`** -- Orchestrator's call on D-3. Reopener: none stated. Moves no row: it governs session 11's presses.

**`L1-D4-NEUTRAL-READ-VALUES`** -- Orchestrator's call on D-4. Reopener: none stated. Moves no row.

**`L3-OPENS-WITH-A-DRAFT-RESIDUE-READ`** -- Orchestrator's call on lane apply-26. Reopener: none stated. Moves no row.

**`LEARNING-ROWS-SPLIT`** -- Orchestrator's answer to lane jobs7's question 3 (13:45), re-ruled at 14:05 for J 154 on the lane's hold (load 25 landed on the in-progress tab), under COMPOUND-ROW-SPLITS-ONLY-ON-STATE; applied by that lane and merged in integration 7. Reopener: none stated.

**`LINKS-ARE-NOT-DISCLOSURES`** -- Orchestrator's call on lane build-p26, applying PAGE-MAY-VETO-NEVER-SUPPLY. Reopener: the ruling on the self-profile query variant.

**`LIVE-BUDGET-40-LOADS`** -- Operator's words: "go, 40 loads is fine". Raised from 15 per wave, to feed one live lane from several offline build lanes. Read strictly by BUDGET-ONE-ACCOUNT-40 (2026-11-26): the 40 are his account's, per trailing 12 hours, shared with the job pipeline.

**`LIVE-FLAG-DENIES-LINKEDIN-MCP`** -- The 15:36 rule for the next live lane's brief, registered on the orchestrator's 20:36 answer to integration 5's first question. The guard is the job pipeline's, at user scope outside this repository. Session 12 drove LinkedIn through its runner. Moves no row. Reopener: none stated.

**`M-C18-EDITOR-OPENS-UNSAVED`** -- Orchestrator's call, applying B5-GROUP-COMPOSER-OPENS-EMPTY. Reopener: none stated.

**`M-C29-DESIGN-FIRST`** -- Orchestrator's call. Reopener: the next build wave.

**`M-C97-LINK-KEYED-DELETE`** -- Orchestrator's design call; answers the ledger's Q-NOTIFICATION-KEY. Reopener: the live uniqueness capture.

**`M-M28-SPLITS`** -- Orchestrator's answer to lane build-msg2's question 1 (22:33), on COMPOUND-ROW-SPLITS-ONLY-ON-STATE; applied by that lane's round 2 and merged in integration 6. Reopener: none stated.

**`M-M31-READ-BY-COMPOSITION`** -- Orchestrator's ratification (22:33) of lane build-msg2's question 4, which gave it no id. Reopener: none stated.

**`MEASURED-ABSENT-OR-PRECONDITION`** -- Orchestrator's convention; overridable. Names N 118, P E7 and P K8 for reconciliation. Reopener: none stated.

**`MEDIA-POST-SAME-REFUSAL`** -- Orchestrator's answer to lane build-msg2's question 2 (22:33). The lane-K ledger carries the question as Q-MEDIA-POST-AUDIENCE from integration 6, so the two rows' next step can cite it. Reopener: an audience the server can read.

**`MEMBER-ROSTERS-AS-BOUNDED-READS`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. Decides the roster question the 2026-09-05 refusal recorded in readonly.py and census cells but never registered (D3). Rows it held: N 165, N 188, N 189, J 108, N 102, N 99, N 177.

**`MESSAGE-SEARCH-CAPTURE-FIRST`** -- Orchestrator's call on the lane-K ledger's question; applied by lane readers-msg26's second round as a next step. Reopener: none stated.

**`MESSAGING-LINE-TO-SESSION-13-STANDBY`** -- Orchestrator's answer to lane s12-prep's second call (17:45), and its acceptance of that lane's reading of it (18:18); X-0 is dropped with it. Applied in the lane's round 2. Moves no row. Reopener: none stated.

**`MESSAGING-SETTINGS-CAPABILITY-LEVEL`** -- The ruling CANONICAL-RULING-ID was written about: one sentence wearing three names across three slices. Its census twin is `_audit/_census/profile.md`.

**`MSG-THREAD-FOOTER-TO-L2`** -- Orchestrator's answer to lane s12-prep's fifth call (17:45); applied in the line's session cell. Moves no row. Reopener: none stated.

**`N-102-MOVES-WITH-J-108`** -- Orchestrator's call on lane build-jmn26. Integration 2's section 6 had kept N 102 GAP; this ruling moves it, and that record carries the back-pointer. Reopener: none stated.

**`NAME-BEARING-ADDRESS-REDACTION-SCOPE`** -- Orchestrator's call on lane admit26. Moves the five newsletter rows to ADMIT. Reopener: for the article page, a capture that spells its address.

**`NAMED-ADDRESS-NEEDS-LOG-REDACTION`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR, applying PEOPLE-DATA-MITIGATIONS; overridable.

**`NAMED-PROFILE-DETAIL-PAGES`** -- Orchestrator's application of NAMED-PROFILE-READ-BEHIND-A-GRANT; overridable. Admitted for the four detail sections measured on his own profile; N 178 and N 65 wait on the Interests page's capture.

**`NAMED-PROFILE-READ-BEHIND-A-GRANT`** -- The operator's ruling, verbatim in its document; mitigations as the question put them.

**`NAMED-SETTINGS-PAGES-RATIFIED`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable.

**`NAMES-AT-RUNTIME`** -- The operator's ruling, verbatim in its document. Amends the 2026-09-05 name-free doctrine for runtime returns; answers WHO-WHICH-COUNTS-ARE-NOT-DELIVERY's question.

**`NAVIGATION-CEILING-MADE-TRUE`** -- Orchestrator's call on lane pace20's question 1. Built as amended by lane infra26 and merged in integration 5: three loads per tool call, enforced in LinkedInBrowser.goto, and the README's two statements put right. Moves no row. Reopener: none stated.

**`NAVIGATION-CEILING-PER-TOOL-CALL`** -- Orchestrator's call on lane infra26's item 2: named NAVIGATION-CEILING-PER-CALL-WITH-ONE-DECLARED-FAN-OUT at 16:45 (the alias), final form at 17:12. Lane infra26's record calls it option (C). Built by that lane in two heads, both merged in integration 5, and held there in full: the middleware, the refused 4th load, the capped fan-out with its one-caller pin and a planted-second-caller control, a test that every registered tool passes through the middleware, and the people bound. The lead's four asks under it are orders, not rulings. It amends NAVIGATION-CEILING-MADE-TRUE, whose 'raise it to 3' rested on a measured maximum of 3 where infra26 measured 5. Moves no row. Reopener: none stated.

**`NEWSLETTER-PICKED-FROM-HIS-SUBSCRIPTIONS`** -- Orchestrator's answer to lane s12-prep's fourth call (17:45); applied in queue line 32's plan cell. In session 12 NEWSLETTER-PUBLISHER-UNPROVEN held it: no kept reading proved a non-person publisher. Moves no row. Reopener: none stated.

**`NEWSLETTER-PUBLISHER-UNPROVEN`** -- Orchestrator's call in session 12 (22:02); it holds NEWSLETTER-PICKED-FROM-HIS-SUBSCRIPTIONS to its own 'never a person'. Moves no row. Reopener: he names a newsletter (L2), or a reading proves an organisation or LinkedIn publisher.

**`NO-INDEX-PINNED-JUDGEMENTS`** -- Orchestrator's call; overridable. Session 7 saw LinkedIn move structure under a recorded position.

**`NO-IRREVERSIBLE-WRITE-IS-FIRED`** -- The single widest write ruling in the corpus. It separates BUILD from FIRE, which is the distinction most re-escalations about writes collapse.

**`NO-RESULTS-STATE-CAPTURES`** -- Orchestrator's call on lane search-fix26's Q2; the two capture lines are in the queue. Moves no row. Reopener: the two captures.

**`NOTIFICATIONS-UNREAD-SPEND`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. Registered under the id the census holds used for the open question, so the holds resolve to the answer.

**`ONE-ENTRY-IS-ONE-SHAPE`** -- Orchestrator's answer to lane build-net2's question (about 20:00), recorded at 20:36, 21:46 and 21:55 and written in full in that lane's record; built and merged in integration 6. Reopener: none stated.

**`OPEN-TO-WORK-EDITOR-ATTENDED-ONLY`** -- Orchestrator's call on lane admit26. Moves its 11 rows to CAPTURE. Reopener: the card changing.

**`OPERATOR-NAMES-THE-TARGET`** -- Amended 2026-11-26 for JOB APPLICATIONS only by RATIFIED-POLICY-NAMES-APPLICATION-TARGETS: a policy he ratified names those targets by rule. Every other outward act is unchanged.

**`ORG-NAME-AT-RUNTIME-LINK-IF-NUMERIC`** -- Orchestrator's answer of 2026-10-10 19:22, registered at integration 3. Applies THIRD-PARTY-TEXT-AT-RUNTIME. Reopener: N 104 meeting its own bar.

**`OTHER-MEMBER-IDS-AS-READS`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. Answers the other-members question N 172 was held on.

**`OUTSIDE-THE-PRODUCT-PURPOSE`** -- Orchestrator's call applying the operator's rule that every feature must serve the product's core purpose; overridable.

**`OUTWARD-CLASSES-BUILT-BEHIND-GRANTS`** -- Orchestrator's call applying the operator's 08:11 principle and OUTWARD-ACTS-NEED-THE-OPERATOR; overridable.

**`OWN-PROFILE-SCROLL-SANCTIONED`** -- Orchestrator's call on lane build-p26. Reopener: none stated.

**`P-A9-CANNOT-DELIVER`** -- Orchestrator's call; overridable. Measured on session 7's editor skeleton.

**`P-D29-BUILT-BEHIND-THE-GRANT`** -- Orchestrator's call; overridable.

**`P-N22-SPLITS`** -- Orchestrator's answer to lane settings7's question 1 (12:55), option (a), under COMPOUND-ROW-SPLITS-ONLY-ON-STATE; applied by that lane: P N32 entered at GAP, its step ADMIT of /manage/purchases-payments/purchases/ under NAMED-SETTINGS-PAGES-RATIFIED. Reopener: none stated.

**`P-O23-D5-ON-ITS-OWN-WORDS`** -- Orchestrator's call. Applied at integration 3: D5 covers a consequence with no control of its own, and O23's consequence has one (P O17's switch), so O23 stays GAP. Reopener: a change to D5's words.

**`PAGE-MAY-VETO-NEVER-SUPPLY`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. Reconciles the navigation guard with ownership checks; first applied to linkedin_surface_census feed_item.

**`PEOPLE-DATA-MITIGATIONS`** -- Orchestrator's call applying the operator's ruling; overridable.

**`PEOPLE-GATE-COUNTS-NAME-SLOTS`** -- Orchestrator's call on lane readers-net26's section 9. Specified at 14:05 as six rules (people gate v2), before session 12. Built by lane infra26 as scripts/people_gate.py (rule N1, with the six rules as R1 to R6), merged in integration 5; the live lane wires it into its runner. Reopener: none stated.

**`PERMALINK-READ-IS-ALLOWED`** -- `M C42` records that this ruling DID NOT REACH naming the target -- which is why that row cannot rest on it. See the DISPUTED section of `_audit/2026-09-21-what-was-ruled.md`.

**`PLAN-PEOPLE-GATE-LINES-ARE-THE-LIVE-LINES`** -- Orchestrator's answer (20:36) to integration 5's second question, which gave it no id. Moves no row. Reopener: none stated.

**`PRESS-GATE-MAY-READ-TO-DECIDE-SELF`** -- Orchestrator's call on lane selfprofile26's question 1; the one narrowed row of test_a_refused_press_never_touches_the_page stands under it. Moves no row. Reopener: none stated.

**`PREVIEW-NAMES-THE-RESOLVED-TARGET`** -- Orchestrator's call applying NAMES-AT-RUNTIME and PEOPLE-DATA-MITIGATIONS; overridable. Answers lane G's preview question.

**`PURCHASES-STAY-MANUAL`** -- Orchestrator's call applying the operator's COST-AWARE STAKES-GATING rule; overridable.

**`RATIFIED-POLICY-NAMES-APPLICATION-TARGETS`** -- Orchestrator's lead ruling L1 (12:22) on the operator's 'yes, automate max' (11:39, 2026-11-26). Amends OPERATOR-NAMES-THE-TARGET for job applications only. Moves no row today: no policy for LinkedIn applications has been ratified. Reopener: none stated.

**`READ-CARDS-DELETION`** -- Orchestrator's call on lane search-fix26's Q3. Executed by lane infra26 on an AST caller census that found no caller (717 tracked files and the 12 live-runner files), merged in integration 5. Moves no row. Reopener: none stated.

**`READ-PAST-AN-ACT-SUBSTRING`** -- Orchestrator's call applying OUTWARD-ACTS-NEED-THE-OPERATOR and D3-UNREGISTERED-REFUSAL-IS-NOT-A-RULING; overridable. A page the allowlist refuses by its silence is admitted the same way.

**`READER-INVENTORY-BY-QUALIFIED-NAME`** -- Orchestrator's answer to lane build-msg2's question 5 (22:33); built red first in that lane's round 2 (2 of 12 failed on the bare-name detector) and merged in integration 6. Reopener: none stated.

**`READER-LEAK-WRITER-UNDER-THE-PACE-QUEUED`** -- Orchestrator's answer to lane build-jobs2's question 5 (19:25), which gave it no id. Nothing is built; integration 6 ran the baseline writers with LINKEDIN_MIN_INTERVAL_S=0. Moves no row. Reopener: none stated.

**`RECEIPT-RISK-IS-HIS`** -- Orchestrator's answer to lane build-jobs2's question 2 (19:25). The rows stay COVERED-UNFIRED; the switch's preview prints the risk and reads his stored resumes before the press and after the restore. Reopener: his explicit order naming the direction.

**`RECEIVED-BADGE-IS-THE-READS-COST`** -- Orchestrator's call on lane readers-net26's section 9, question 2 (the linkedin_notifications precedent). The orchestrator's own spelling carries an apostrophe and is kept as the alias. Applied by the lane. Reopener: none stated.

**`RECEIVED-INVITATIONS-READ-STAYS-ADMITTED`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR, applying D5-PASSIVE-COST-IS-NOT-A-ROW; overridable.

**`RECEIVED-LEAF-ADMITTED-WITH-ITS-READER`** -- Orchestrator's answer 6 to lane net7 (13:25), which gave it no id; the id is integration 7's. One anchored line, one pattern exemption excusing exactly invitation, and invitation_manager._RECEIVED_PATHS accepting the leaf. RECEIVED-LEAF-SERVES-THE-INVITATION-WRITES accepts the same tuple's widening onto N 15 and N 16. Reopener: none stated.

**`RECEIVED-LEAF-SERVES-THE-INVITATION-WRITES`** -- Orchestrator's ruling (17:20) on the cold verifier's MAJOR on lane net7 (the write veto widened beyond answer 6's text); without it those writes could never fire. Moves no row. Reopener: none stated.

**`RECOMMENDATIONS-DETAIL-PAGE-ADMITTED`** -- Orchestrator's call on lane admit26. Moves its 13 rows to ADMIT. Reopener: none stated.

**`REFOLLOW-FROM-HIS-NAMED-PROFILE`** -- Orchestrator's call on the lane-K ledger's question; applied by lane readers-net26's second round (both rows read SIBLING N 34). Reopener: none stated.

**`REFUSE-BEFORE-LOAD-ON-A-RETIRED-ROUTE`** -- Orchestrator's answer to lane jobs7's question 4 (13:45); built red first (job_search_route.CLASSIC_ROUTE_RETIRED) and merged in integration 7. The job pipeline's located LinkedIn searches now refuse at once. Reopener: a capture showing the classic route serving again.

**`REFUSED-APPLY-DISCARDS-ITS-DRAFT`** -- Orchestrator's call on lane apply-26. Reopener: none stated.

**`REINVITE-BY-CALLER-COMPOSITION`** -- Orchestrator's call on the lane-K ledger's question; applied by lane readers-net26's second round. Reopener: none stated.

**`RELATION-REMOVALS-BUILT-BEHIND-GRANTS`** -- Orchestrator's call applying the operator's 08:11 principle and OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. Decides N 29, N 141 and N A14, which lane L8 left outside the three classes.

**`RESUME-BUILDER-UNDER-ARTICLE-COMPOSER-CAPTURE`** -- Orchestrator's call on lane admit26, applying ARTICLE-COMPOSER-CAPTURE. Reopener: a capture that finds where LinkedIn draws it.

**`RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE`** -- Orchestrator's call on the classic search's retirement. Its trigger was met in live session 12: load 3, C-SRCH-1, was redirected to the AI route. Applied at integration 6 to the 22 rows of search26's report, section 4.5 (J 1 to J 15, J 17, J 18, J 20, J 40, J 107, J 151, and J 31, built on the classic switch), each to GAP with its next step on the AI route and a reopener. Four of them are COVERED-UNFIRED again, built on the AI route by lane jobs7 and merged in integration 7 (J 1, J 20, J 40, and J 31's AI arm); REFUSE-BEFORE-LOAD-ON-A-RETIRED-ROUTE refuses the classic arguments before any load. Reopener: none stated.

**`REVEAL-BUTTON-IS-A-DISCLOSURE`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable.

**`SAFETY-REPORTS-STAY-MANUAL`** -- Orchestrator's call; overridable. Decides N 152.

**`SAVE-POST-UNDER-OWN-CURATION`** -- Orchestrator's answer to lane msg7's question 2 (12:35); built by that lane (M C36 COVERED-UNFIRED) and merged in integration 7. Reopener: none stated.

**`SAVE-RECEIPT-NEEDS-A-CHANGE`** -- Orchestrator's fix-round order (17:20) on the cold verifier's finding (a saved region drawn before the press read as performed); fixed red first by lane msg7 (7e9f61b) before the first live fire and merged in integration 7. FEED-CURATION-RECEIPT-NEEDS-A-CHANGE is its shape for N 154. Reopener: none stated.

**`SCHEDULED-LIST-AS-A-SHIPPED-READ`** -- Orchestrator's call on the lane-K ledger's question; applied by lane readers-msg26's second round (BUILD on its session-11 capture). Built by lane build-msg2 (M C14, linkedin_scheduled_posts) and merged in integration 6. Reopener: none stated.

**`SCREENING-QUESTION-RECORD`** -- Orchestrator's call on lane apply-26. Applies THIRD-PARTY-TEXT-AT-RUNTIME. Reopener: none stated.

**`SEARCH-ADMISSION-APPROVED-FIVE-CONDITIONS`** -- Condition 2 was AMENDED the same day -- see SEARCH-CONDITION-2-CLOSED. The ruling bars FIRING, not READING; conflating the two cost a later wave a decision it did not need.

**`SEARCH-BOX-TYPEAHEAD-DISCLOSURE`** -- Orchestrator's call for lane build-net2 (17:10), registered at integration 5. Measured by the orchestrator: exactly one such input on 62 of 175 fixtures, none on 113, never two. Built by that lane (N 95, linkedin_recent_searches) and merged in integration 6; its one entry is one shape (ONE-ENTRY-IS-ONE-SHAPE). Reopener: none stated.

**`SEARCH-ROUTE-CLASSIC-PRIMARY`** -- Orchestrator's call on the classic search's retirement (01:20 entry). Moves no row. Reopener: none stated.

**`SELF-LOADER-WAITS-FOR-THE-REWRITE`** -- Orchestrator's build order of 2026-11-26 22:21, after session 12's E1 refusal; not registered at integration 6 (an order answering no question), registered here because session 14's self-anchored lines wait on it. Built first by lane prof7 (self_profile.await_rewrite) and merged in integration 7. Reopener: none stated.

**`SELF-PROFILE-EDIT-NOTIFY-CONDITION-AMENDED`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. Measured cause: the intro editor draws no named notify control (live lane session 1, lane L7).

**`SELF-PROFILE-EDITS-NOT-OUTWARD`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. Narrows OPERATOR-NAMES-THE-TARGET to writes that target other people.

**`SELF-PROFILE-QUERY-VARIANT-ADMITTED`** -- Orchestrator's call on the lane-K ledger's question, raised by LINKS-ARE-NOT-DISCLOSURES. Applied by lane admit5-26 (the readonly.py line, red first, the /in/me/ form only); anchor (4) rests on lane selfprofile26's self-profile recognition. Reopener: a capture showing the variant draws nothing the bare profile does not.

**`SELF-ROOT-LINK-PRESS-BY-EXACT-MATCH`** -- Orchestrator's answer to lane prof7 (13:00), amended at 13:10 to include an admitted constant query ("My 'no query' meant no query the PAGE adds"). Every such press goes through the one matcher EXACT-MATCH-REFUSES-ANY-WHITESPACE names. Reopener: none stated.

**`SESSION-SURFACE`** -- Orchestrator's call applying CREDENTIAL-SETTINGS-NEED-THE-OPERATOR; overridable. Decides P N9 and P N10.

**`SHARE-AND-POLL-PROOFS-OWN-POSTS`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable.

**`SIGN-IN-CHALLENGES-ARE-HIS`** -- Orchestrator's call; overridable. Decides P N13 and P N14.

**`THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET`** -- The orchestrator applying WRITE-CLASS-B and OPERATOR-NAMES-THE-TARGET; overridable. Unblocks N 1, N 4, N 5, M M1 and M M6 as builds.

**`THIRD-PARTY-TEXT-AT-RUNTIME`** -- Orchestrator's call applying NAMES-AT-RUNTIME; overridable. Decides M C43 and J 110.

**`UNFOLLOWED-RAW-DELETED`** -- Orchestrator's call on lane readers-net26's section 9, question 1. An action on gitignored state; moves no row. Reopener: none stated.

**`VERIFICATION-DELETE-HELD`** -- Orchestrator's answer to lane settings7's question 2 (12:55), option (b). Measured offline by that lane: the captured Delete declares no popup and no controlled dialog, so the row stays his. Reopener: his word, or a Delete that declares a popup.

**`VERIFICATIONS-PAGE-ADMITTED`** -- Orchestrator's call on lane admit26. Moves P K1 and P K7 to ADMIT. P K1 is COVERED-UNFIRED on linkedin_my_verifications (lane settings7, merged in integration 7); P K7 is held by VERIFICATION-DELETE-HELD. Reopener: none stated.

**`VIEW-SWITCH-PRESS-RESTORED`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable.

**`VOLUNTEERING-BARE-SPELLING-FIRST`** -- Orchestrator's call on lane admit26. Its reopener was met in live session 12 (load 22: the bare spelling redirected to his root); VOLUNTEERING-FALLBACK-BOUNDARY (integration 7) is the fallback, built by lane prof7. Reopener: the bare spelling not landing.

**`VOLUNTEERING-FALLBACK-BOUNDARY`** -- Orchestrator's answer to lane prof7 (13:10); built now, red first, by that lane (volunteering_route.py and one anchored allowlist line) and merged in integration 7. It is VOLUNTEERING-BARE-SPELLING-FIRST's fallback. Reopener: none stated.

**`WHO-WHICH-COUNTS-ARE-NOT-DELIVERY`** -- Orchestrator's call under OUTWARD-ACTS-NEED-THE-OPERATOR; overridable. Precedent: N 162 and N 180.

**`WRITE-CLASS-B`** -- Operator's word: "b". Supersedes DO-NOT-OPEN-MESSAGING and amends NO-IRREVERSIBLE-WRITE-IS-FIRED; its target condition is OPERATOR-NAMES-THE-TARGET.

**`WRITE-DOOR-EXCUSAL-ON-THE-SPEC`** -- Orchestrator's answer to lane build-jobs2's question 3 (19:25), which gave it no id: "The WriteSpec excusal is ACCEPTED, with readonly.py untouched." Merged in integration 6. Moves no row. Reopener: none stated.

---

## 4. WHAT THIS REGISTER DID NOT SCAN

**The discovery scan reads `RULED:` and nothing else.** It was chosen on precision -- 24 of 25 hits are genuine declarations, the best of fourteen signals measured -- and its recall is poor. The counts below are signals a ruling can be written under that this scan will NEVER see. They are printed every run so that a green check is not read as a complete one.

| signal NOT scanned | files | lines |
|---|---|---|
| a heading naming a ruling | 159 | 338 |
| a bold line opening on RULING/RULED | 67 | 157 |
| the phrase THE RULING | 44 | 74 |
| a named -RULING id | 45 | 115 |
| the phrase standing ruling | 18 | 41 |
| a lead or operator ruling in prose | 44 | 111 |

**The ruling that caused this register to be written is in the first row and not in the scan.** `BOUNDARY-IS-NOT-A-REASON` is phrased as a quoted ledger rule under a heading that carries no marker at all. It is registered because a person read it, and nothing here would have found it.

---

## 5. THE DECLARATIONS THE SCAN FOUND

Every `RULED:` line in the corpus, and what became of it. An UNCLAIMED row fails `--check`.

| document | section | claimed by |
|---|---|---|
| [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md) | **RULED:** the composer (`Start a post` modal, `/article/new/`) is allowed to | `COMPOSER-IS-THE-REFUSAL-NOT-THE-ADDRESS` |
| [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md) | **RULED:** `/feed/update/<urn>/` is allowed, an ordinary read of a post | `PERMALINK-READ-IS-ALLOWED` |
| [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md) | **RULED:** `/in/<member>/edit/` and the profile editors are allowed. His own | `PROFILE-EDITOR-ADDRESSES-ALLOWED` |
| [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md) | **RULED:** ONE NAMED settings page below `/mypreferences/d/` -- one at a time, | `ONE-NAMED-SETTINGS-PAGE-AT-A-TIME` |
| [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md) | **RULED:** targeting is allowed as a CALL-TIME ARGUMENT, never stored. This | `INVITATION-TARGETING-IS-CALL-TIME` |
| [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md) | **RULED: do not open messaging.** Opening it opens a conversation LinkedIn | `DO-NOT-OPEN-MESSAGING` |
| [2026-09-03-linkedin-gap-blockers.md](2026-09-03-linkedin-gap-blockers.md) | ## A9. THE REDACTION FORK IS RULED: A CLOSED VOCABULARY | `REDACTION-FORK-CLOSED-VOCABULARY` |
| [2026-09-19-search-admission-condition-2-amended.md](2026-09-19-search-admission-condition-2-amended.md) | **RULED: those entries come out, or move to a clearly-marked conditional block | `MUST-STAY-REFUSED-ENTRIES-COME-OUT` |
| [2026-09-19-the-disclosing-press-ruling.md](2026-09-19-the-disclosing-press-ruling.md) | ## RULED: PERMITTED, under four conditions that must ALL hold | `DISCLOSING-PRESS-PERMITTED` |
| [2026-09-19-the-five-requests-ruled.md](2026-09-19-the-five-requests-ruled.md) | ## A. THE MAP'S CONVENTION -- RULED: at-HEAD membership, plus `RE_FILED` | `MAP-CONVENTION-AT-HEAD-MEMBERSHIP` |
| [2026-09-19-the-five-requests-ruled.md](2026-09-19-the-five-requests-ruled.md) | ## B. `N 61` IN `HASHTAG-EXISTENCE` -- RULED: removed | `N61-REMOVED-FROM-HASHTAG-EXISTENCE` |
| [2026-09-19-the-five-requests-ruled.md](2026-09-19-the-five-requests-ruled.md) | ## C. `CONVERSATION-OVERFLOW-MENU` -- RULED: both waves are right, about different things | `CONVERSATION-OVERFLOW-BOTH-WAVES-RIGHT` |
| [2026-09-19-the-five-requests-ruled.md](2026-09-19-the-five-requests-ruled.md) | ## D. THE PUBLISHED-SPLIT CHECK -- RULED: report now, gate once the deliberate over-runs ar | `PUBLISHED-SPLIT-REPORT-NOW-GATE-LATER` |
| [2026-09-19-the-five-requests-ruled.md](2026-09-19-the-five-requests-ruled.md) | ## E. `CREATOR-HUB-SURFACE` AND `POST-COMMENT-CONTROLS` -- RULED: LEDGER OVER-COUNTS | `CREATOR-HUB-AND-POST-COMMENT-LEDGER-OVERCOUNTS` |
| [2026-09-19-the-three-ruling-requests-ruled.md](2026-09-19-the-three-ruling-requests-ruled.md) | ### RULED: THE CENSUS IS RIGHT. THE LEDGER'S `1R` IS THE ERROR. | `CENSUS-OUTRANKS-LEDGER` |
| [2026-09-19-two-census-conventions-ruled.md](2026-09-19-two-census-conventions-ruled.md) | ### RULED: NO. THEY STAY GAP, WITH THE BLOCKER NAMED PRECISELY. | `INCIDENTAL-CAPTURE-IS-NOT-A-RULING` |
| [2026-09-19-two-census-conventions-ruled.md](2026-09-19-two-census-conventions-ruled.md) | ### RULED: THE CHECK STANDS. THE PROBE MUST NOT TRY REFUSED VALUES. | `PROBE-MUST-NOT-TRY-REFUSED-VALUES` |
| [2026-09-19-two-census-conventions-ruled.md](2026-09-19-two-census-conventions-ruled.md) | **RULED: the gate is SAFE and BLIND, and those are different properties.** It | `GATE-IS-SAFE-AND-BLIND` |
| [2026-09-19-two-census-conventions-ruled.md](2026-09-19-two-census-conventions-ruled.md) | ### RULED: APPROVED IN PRINCIPLE. FIVE CONDITIONS, ALL BINDING. | `SEARCH-ADMISSION-APPROVED-FIVE-CONDITIONS` |
| [2026-09-19-two-census-conventions-ruled.md](2026-09-19-two-census-conventions-ruled.md) | ### RULED: THE GRAIN FOLLOWS WHAT THE PLATFORM DRAWS | `GRAIN-FOLLOWS-WHAT-THE-PLATFORM-DRAWS` |
| [2026-09-20-the-pointer-graph.md](2026-09-20-the-pointer-graph.md) | **RULED: ship the detector. Do not rewrite the 69 cells.** The brief authorised this | `POSITIONAL-DIALECT-SHIP-THE-DETECTOR` |
| [2026-09-21-the-compound-rows.md](2026-09-21-the-compound-rows.md) | ## THE RULING -- RULED: a compound row is split ONLY when its halves need different STATES | `COMPOUND-ROW-SPLITS-ONLY-ON-STATE` |
| [2026-09-21-the-field-beside-the-message.md](2026-09-21-the-field-beside-the-message.md) | **RULED: the error envelope's url field carries the address this server ASKED | `ERROR-URL-ASKED-FOR-OR-NOTHING` |
| [2026-09-21-what-the-browser-said.md](2026-09-21-what-the-browser-said.md) | **RULED: what the error envelope's message may carry is decided WHERE THE | `ERROR-MESSAGE-RULED-AT-THE-RAISE` |
| [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md) | RULED: (operator, 2026-09-23 17:43, verbatim "go, 40 loads is fine") A live | `LIVE-BUDGET-40-LOADS` |
| [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md) | RULED: (operator, 2026-09-23 18:13) Only actions that act as the operator | `OUTWARD-ACTS-NEED-THE-OPERATOR` |
| [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md) | RULED: (operator, 2026-09-23 18:15, verbatim "b") The package may CONNECT, | `WRITE-CLASS-B` |
| [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md) | RULED: (operator, 2026-09-23 18:15, same ruling) A live proof of an outward | `OPERATOR-NAMES-THE-TARGET` |
| [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md) | RULED: (orchestrator, 2026-09-23, delegated) VIEW-SWITCH PRESSES are | `VIEW-SWITCH-PRESS-RESTORED` |
| [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md) | RULED: (orchestrator, 2026-09-23, delegated) D1, SEARCH KEYWORDS AND | `D1-SEARCH-AS-READS` |
| [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md) | RULED: (orchestrator, 2026-09-23, delegated) Loading /notifications/ is | `NOTIFICATIONS-UNREAD-SPEND` |
| [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md) | RULED: (orchestrator, 2026-09-23, applying (b)) Reading the operator's own | `OWN-INBOX-READS-COVERED-BY-B` |
| [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md) | RULED: (orchestrator, 2026-09-23, delegated) EDITS TO THE OPERATOR'S OWN | `SELF-PROFILE-EDITS-NOT-OUTWARD` |
| [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md) | RULED: (orchestrator, 2026-09-23, delegated) OTHER MEMBERS' IDS IN SEARCH | `OTHER-MEMBER-IDS-AS-READS` |
| [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md) | RULED: (orchestrator, 2026-09-24, delegated) D4 IS ANSWERED NO: the package | `D4-NO-OWN-BROWSER-CONTEXT` |
| [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md) | RULED: (orchestrator, 2026-09-24, delegated) D6 IS ANSWERED YES. A row named | `D6-CAPABILITY-OVER-AFFORDANCE` |
| [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md) | RULED: (orchestrator, 2026-09-24, delegated) A PLAIN BUTTON THAT ONLY | `REVEAL-BUTTON-IS-A-DISCLOSURE` |
| [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md) | RULED: (orchestrator, 2026-09-24, delegated) SHARE-LINK PROOFS USE THE | `SHARE-AND-POLL-PROOFS-OWN-POSTS` |
| [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md) | RULED: (orchestrator, 2026-09-24, delegated) CREDENTIAL, RECOVERY AND SESSION | `CREDENTIAL-SETTINGS-NEED-THE-OPERATOR` |
| [2026-09-23-rulings-write-class-and-delegated-calls.md](2026-09-23-rulings-write-class-and-delegated-calls.md) | RULED: (orchestrator, 2026-09-23, delegated) /in/me/ presses get NO blanket | `IN-ME-NO-BLANKET-BAR` |
| [2026-09-24-rulings-names-at-runtime.md](2026-09-24-rulings-names-at-runtime.md) | RULED: (operator, 2026-09-24 08:11, verbatim) "It's not about returning or not returning. | `NAMES-AT-RUNTIME` |
| [2026-09-24-rulings-names-at-runtime.md](2026-09-24-rulings-names-at-runtime.md) | RULED: (orchestrator, 2026-09-24, applying NAMES-AT-RUNTIME) PEOPLE DATA IS | `PEOPLE-DATA-MITIGATIONS` |
| [2026-09-24-rulings-names-at-runtime.md](2026-09-24-rulings-names-at-runtime.md) | RULED: (orchestrator, 2026-09-24, applying the operator's 08:11 principle) | `OUTWARD-CLASSES-BUILT-BEHIND-GRANTS` |
| [2026-09-24-rulings-notify-veto-and-who-which.md](2026-09-24-rulings-notify-veto-and-who-which.md) | RULED: (orchestrator, 2026-09-24, delegated) CONDITION 1 OF | `SELF-PROFILE-EDIT-NOTIFY-CONDITION-AMENDED` |
| [2026-09-24-rulings-notify-veto-and-who-which.md](2026-09-24-rulings-notify-veto-and-who-which.md) | RULED: (orchestrator, 2026-09-24, delegated) A PAGE MAY VETO A NAVIGATION, | `PAGE-MAY-VETO-NEVER-SUPPLY` |
| [2026-09-24-rulings-notify-veto-and-who-which.md](2026-09-24-rulings-notify-veto-and-who-which.md) | RULED: (orchestrator, 2026-09-24, applying (b)) A THIRD PARTY'S PROFILE | `THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET` |
| [2026-09-24-rulings-notify-veto-and-who-which.md](2026-09-24-rulings-notify-veto-and-who-which.md) | RULED: (orchestrator, 2026-09-24, delegated) A ROW WHOSE PAYLOAD IS WHO (a | `WHO-WHICH-COUNTS-ARE-NOT-DELIVERY` |
| [2026-09-24-rulings-search-verticals-rosters-passive-costs.md](2026-09-24-rulings-search-verticals-rosters-passive-costs.md) | RULED: (orchestrator, 2026-09-24, delegated) D2 IS ANSWERED YES. The search | `D2-SEARCH-VERTICALS-WIDENED` |
| [2026-09-24-rulings-search-verticals-rosters-passive-costs.md](2026-09-24-rulings-search-verticals-rosters-passive-costs.md) | RULED: (orchestrator, 2026-09-24, delegated) D3 IS ANSWERED NO. A refusal | `D3-UNREGISTERED-REFUSAL-IS-NOT-A-RULING` |
| [2026-09-24-rulings-search-verticals-rosters-passive-costs.md](2026-09-24-rulings-search-verticals-rosters-passive-costs.md) | RULED: (orchestrator, 2026-09-24, delegated) MEMBER ROSTERS ARE ADMITTED AS | `MEMBER-ROSTERS-AS-BOUNDED-READS` |
| [2026-09-24-rulings-search-verticals-rosters-passive-costs.md](2026-09-24-rulings-search-verticals-rosters-passive-costs.md) | RULED: (orchestrator, 2026-09-24, delegated) D5 IS ANSWERED: A PASSIVE COST IS | `D5-PASSIVE-COST-IS-NOT-A-ROW` |
| [2026-09-27-rulings-previews-and-receipts.md](2026-09-27-rulings-previews-and-receipts.md) | RULED: (orchestrator, 2026-09-27, applying NAMES-AT-RUNTIME) A PREVIEW NAMES WHOM | `PREVIEW-NAMES-THE-RESOLVED-TARGET` |
| [2026-09-27-rulings-relation-removals-and-account-destruction.md](2026-09-27-rulings-relation-removals-and-account-destruction.md) | RULED: (orchestrator, 2026-09-27, applying the operator's 08:11 principle) REMOVING A RELA | `RELATION-REMOVALS-BUILT-BEHIND-GRANTS` |
| [2026-09-27-rulings-relation-removals-and-account-destruction.md](2026-09-27-rulings-relation-removals-and-account-destruction.md) | RULED: (orchestrator, 2026-09-27, applying the operator's 08:11 principle) ACCOUNT-LEVEL | `ACCOUNT-DESTRUCTION-STAYS-MANUAL` |
| [2026-09-28-rulings-build-classes.md](2026-09-28-rulings-build-classes.md) | RULED: (orchestrator, 2026-09-28, applying WRITE-CLASS-B and the operator's 08:11 principl | `EVERY-OUTWARD-CLASS-BUILT-BEHIND-GRANTS` |
| [2026-09-28-rulings-build-classes.md](2026-09-28-rulings-build-classes.md) | RULED: (orchestrator, 2026-09-28, applying OUTWARD-ACTS-NEED-THE-OPERATOR) HIS-OWN-SETTING | `HIS-OWN-SETTINGS-NOT-OUTWARD` |
| [2026-09-28-rulings-build-classes.md](2026-09-28-rulings-build-classes.md) | RULED: (orchestrator, 2026-09-28, applying OUTWARD-ACTS-NEED-THE-OPERATOR) HIS-OWN-CURATIO | `HIS-OWN-CURATION-NOT-OUTWARD` |
| [2026-09-28-rulings-build-classes.md](2026-09-28-rulings-build-classes.md) | RULED: (orchestrator, 2026-09-28, applying COST-AWARE STAKES-GATING) PURCHASES-STAY-MANUAL | `PURCHASES-STAY-MANUAL` |
| [2026-09-28-rulings-build-classes.md](2026-09-28-rulings-build-classes.md) | RULED: (orchestrator, 2026-09-28, applying OUTWARD-ACTS-NEED-THE-OPERATOR and D3-UNREGISTE | `READ-PAST-AN-ACT-SUBSTRING` |
| [2026-09-28-rulings-named-profile-read.md](2026-09-28-rulings-named-profile-read.md) | RULED: (operator, 2026-09-28 08:01, verbatim) "Yes, I'm giving you permission." | `NAMED-PROFILE-READ-BEHIND-A-GRANT` |
| [2026-10-10-rulings-lane-a-questions.md](2026-10-10-rulings-lane-a-questions.md) | RULED: (orchestrator, 2026-10-10) RECEIVED-INVITATIONS-READ-STAYS-ADMITTED: the received-i | `RECEIVED-INVITATIONS-READ-STAYS-ADMITTED` |
| [2026-10-10-rulings-lane-a-questions.md](2026-10-10-rulings-lane-a-questions.md) | RULED: (orchestrator, 2026-10-10) NAMED-SETTINGS-PAGES-RATIFIED: each settings page lane A | `NAMED-SETTINGS-PAGES-RATIFIED` |
| [2026-10-10-rulings-lane-a-questions.md](2026-10-10-rulings-lane-a-questions.md) | RULED: (orchestrator, 2026-10-10) CREDENTIAL-ADJACENT-STAYS-REFUSED: stored applicant acco | `CREDENTIAL-ADJACENT-STAYS-REFUSED` |
| [2026-10-10-rulings-lane-a-questions.md](2026-10-10-rulings-lane-a-questions.md) | RULED: (orchestrator, 2026-10-10) NAMED-ADDRESS-NEEDS-LOG-REDACTION: a page whose ADDRESS | `NAMED-ADDRESS-NEEDS-LOG-REDACTION` |
| [2026-10-10-rulings-lane-a-questions.md](2026-10-10-rulings-lane-a-questions.md) | RULED: (orchestrator, 2026-10-10) CONTENT-VERTICAL-NOT-ALL-RESULTS: D2-SEARCH-VERTICALS-WI | `CONTENT-VERTICAL-NOT-ALL-RESULTS` |
| [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md) | RULED: (orchestrator, 2026-10-10) CAPTURE-PRESS-UNDER-PROBE-RULE: a live-lane CAPTURE may | `CAPTURE-PRESS-UNDER-PROBE-RULE` |
| [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md) | RULED: (orchestrator, 2026-10-10) ARTICLE-COMPOSER-CAPTURE: one capture load of /article/n | `ARTICLE-COMPOSER-CAPTURE` |
| [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md) | RULED: (orchestrator, 2026-10-10) NO-INDEX-PINNED-JUDGEMENTS: a control is judged by its o | `NO-INDEX-PINNED-JUDGEMENTS` |
| [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md) | RULED: (orchestrator, 2026-10-10) CALLER-COMPOSITION-UNDER-D6: a row is discharged under D | `CALLER-COMPOSITION-UNDER-D6` |
| [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md) | RULED: (orchestrator, 2026-10-10) CONTACT-IMPORT-STAYS-MANUAL: an address-book import or s | `CONTACT-IMPORT-STAYS-MANUAL` |
| [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md) | RULED: (orchestrator, 2026-10-10) SESSION-SURFACE: reading the active-sessions list (P N9) | `SESSION-SURFACE` |
| [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md) | RULED: (orchestrator, 2026-10-10) SIGN-IN-CHALLENGES-ARE-HIS: this server never answers a | `SIGN-IN-CHALLENGES-ARE-HIS` |
| [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md) | RULED: (orchestrator, 2026-10-10) APPLY-FLOW-IS-THE-APPLICATION: opening the Easy Apply fl | `APPLY-FLOW-IS-THE-APPLICATION` |
| [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md) | RULED: (orchestrator, 2026-10-10, applying the operator's NAMES-AT-RUNTIME) THIRD-PARTY-TE | `THIRD-PARTY-TEXT-AT-RUNTIME` |
| [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md) | RULED: (orchestrator, 2026-10-10) FIXED-UI-LABEL-MATCH: N 82's Actively-hiring filter is m | `FIXED-UI-LABEL-MATCH` |
| [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md) | RULED: (orchestrator, 2026-10-10) GEOLOCATION-BY-D6: no browser geolocation permission is | `GEOLOCATION-BY-D6` |
| [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md) | RULED: (orchestrator, 2026-10-10) P-A9-CANNOT-DELIVER: P A9 is COVERED-CANNOT-DELIVER on t | `P-A9-CANNOT-DELIVER` |
| [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md) | RULED: (orchestrator, 2026-10-10) P-D29-BUILT-BEHIND-THE-GRANT: P D29 is built behind the | `P-D29-BUILT-BEHIND-THE-GRANT` |
| [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md) | RULED: (orchestrator, 2026-10-10) SAFETY-REPORTS-STAY-MANUAL: N 152 is EXCLUDED-RULED, wit | `SAFETY-REPORTS-STAY-MANUAL` |
| [2026-10-10-rulings-ledger-questions.md](2026-10-10-rulings-ledger-questions.md) | RULED: (orchestrator, 2026-10-10, applying the operator's rule that every feature must ser | `OUTSIDE-THE-PRODUCT-PURPOSE` |
| [2026-10-10-rulings-named-profile-detail-pages.md](2026-10-10-rulings-named-profile-detail-pages.md) | RULED: (orchestrator, 2026-10-10, applying the operator's 08:01 YES to reading profiles he | `NAMED-PROFILE-DETAIL-PAGES` |
| [2026-10-26-integration-2.md](2026-10-26-integration-2.md) | RULED: (orchestrator, 2026-11-25) DOM-WAIVER-25-J110 -- "dom.py may hold a 25th | `DOM-WAIVER-25-J110` |
| [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md) | RULED: (orchestrator, 2026-11-25) L1-D1-RIDERS-RIDE -- "D-1 yes (both riders)". | `L1-D1-RIDERS-RIDE` |
| [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md) | RULED: (orchestrator, 2026-11-25) MEASURED-ABSENT-OR-PRECONDITION -- "CONVENTION, | `MEASURED-ABSENT-OR-PRECONDITION` |
| [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md) | RULED: (orchestrator, 2026-11-25) ORG-NAME-AT-RUNTIME-LINK-IF-NUMERIC -- the | `ORG-NAME-AT-RUNTIME-LINK-IF-NUMERIC` |
| [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md) | RULED: (orchestrator, 2026-11-25) APPLY-DRY-WALK-FIRES-THE-STEP-ROWS -- "dry walk | `APPLY-DRY-WALK-FIRES-THE-STEP-ROWS` |
| [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md) | RULED: (orchestrator, 2026-11-25) EDITOR-TYPEAHEAD-SANCTIONED -- "(a) | `EDITOR-TYPEAHEAD-SANCTIONED` |
| [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md) | RULED: (orchestrator, 2026-11-25) RECOMMENDATIONS-DETAIL-PAGE-ADMITTED -- | `RECOMMENDATIONS-DETAIL-PAGE-ADMITTED` |
| [2026-11-25-rulings-end-of-wave.md](2026-11-25-rulings-end-of-wave.md) | RULED: (orchestrator, 2026-11-25) N-102-MOVES-WITH-J-108 -- "Q1 N 102 moves WITH | `N-102-MOVES-WITH-J-108` |
| [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md) | RULED: (orchestrator, 2026-11-26) SELF-PROFILE-QUERY-VARIANT-ADMITTED -- | `SELF-PROFILE-QUERY-VARIANT-ADMITTED` |
| [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md) | RULED: (orchestrator, 2026-11-26) AI-EASY-APPLY-POST-FILTER -- "the AI fallback | `AI-EASY-APPLY-POST-FILTER` |
| [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md) | RULED: (orchestrator, 2026-11-26) RATIFIED-POLICY-NAMES-APPLICATION-TARGETS -- | `RATIFIED-POLICY-NAMES-APPLICATION-TARGETS` |
| [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md) | RULED: (orchestrator, 2026-11-26) J-114-SPLITS -- "split under | `J-114-SPLITS` |
| [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md) | RULED: (orchestrator, 2026-11-26) UNFOLLOWED-RAW-DELETED -- "the kept raw | `UNFOLLOWED-RAW-DELETED` |
| [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md) | RULED: (orchestrator, 2026-11-26) PRESS-GATE-MAY-READ-TO-DECIDE-SELF -- "where | `PRESS-GATE-MAY-READ-TO-DECIDE-SELF` |
| [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md) | RULED: (orchestrator, 2026-11-26) MESSAGE-SEARCH-CAPTURE-FIRST -- | `MESSAGE-SEARCH-CAPTURE-FIRST` |
| [2026-11-26-rulings-integration-4.md](2026-11-26-rulings-integration-4.md) | RULED: (orchestrator, 2026-11-26) NAVIGATION-CEILING-MADE-TRUE -- | `NAVIGATION-CEILING-MADE-TRUE` |
| [2026-11-26-rulings-integration-5.md](2026-11-26-rulings-integration-5.md) | RULED: (orchestrator, 2026-11-26) NAVIGATION-CEILING-PER-TOOL-CALL -- at 16:45, | `NAVIGATION-CEILING-PER-TOOL-CALL` |
| [2026-11-26-rulings-integration-5.md](2026-11-26-rulings-integration-5.md) | RULED: (orchestrator, 2026-11-26) SEARCH-BOX-TYPEAHEAD-DISCLOSURE -- | `SEARCH-BOX-TYPEAHEAD-DISCLOSURE` |
| [2026-11-26-rulings-integration-5.md](2026-11-26-rulings-integration-5.md) | RULED: (orchestrator, 2026-11-26) FIFTH-SEARCH-TO-PEOPLE-LABELS -- | `FIFTH-SEARCH-TO-PEOPLE-LABELS` |
| [2026-11-26-rulings-integration-5.md](2026-11-26-rulings-integration-5.md) | RULED: (orchestrator, 2026-11-26) BUDGET-ONE-ACCOUNT-40 -- "Closes the 15:36 | `BUDGET-ONE-ACCOUNT-40` |
| [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md) | RULED: (orchestrator, 2026-11-26) J-37-SPLITS -- "J-37-SPLITS | `J-37-SPLITS` |
| [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md) | RULED: (orchestrator, 2026-11-26) LIVE-FLAG-DENIES-LINKEDIN-MCP -- at 20:36: | `LIVE-FLAG-DENIES-LINKEDIN-MCP` |
| [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md) | RULED: (orchestrator, 2026-11-26) ONE-ENTRY-IS-ONE-SHAPE -- at 20:36: | `ONE-ENTRY-IS-ONE-SHAPE` |
| [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md) | RULED: (orchestrator, 2026-11-26) NEWSLETTER-PUBLISHER-UNPROVEN -- "RULED | `NEWSLETTER-PUBLISHER-UNPROVEN` |
| [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md) | RULED: (orchestrator, 2026-11-26) M-M28-SPLITS -- "M-M28-SPLITS: view half | `M-M28-SPLITS` |
| [2026-11-26-rulings-integration-6.md](2026-11-26-rulings-integration-6.md) | RULED: (orchestrator, 2026-11-26) FAILED-REPROOF-DEMOTES -- "RULING | `FAILED-REPROOF-DEMOTES` |
| [2026-11-26-rulings-search-route.md](2026-11-26-rulings-search-route.md) | RULED: (orchestrator, 2026-11-26) SEARCH-ROUTE-CLASSIC-PRIMARY -- | `SEARCH-ROUTE-CLASSIC-PRIMARY` |
| [2026-11-26-rulings-search-route.md](2026-11-26-rulings-search-route.md) | RULED: (orchestrator, 2026-11-26) FILTER-REQUERY-COUNTS-AS-A-SEARCH -- | `FILTER-REQUERY-COUNTS-AS-A-SEARCH` |
| [2026-11-26-rulings-search-route.md](2026-11-26-rulings-search-route.md) | RULED: (orchestrator, 2026-11-26) RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE -- | `RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE` |
| [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md) | RULED: (orchestrator, 2026-11-27) ADMIT-NOW-LANDING-IN-SESSION-14 -- at 12:35: | `ADMIT-NOW-LANDING-IN-SESSION-14` |
| [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md) | RULED: (orchestrator, 2026-11-27) P-N22-SPLITS -- at 12:55: "the subscription | `P-N22-SPLITS` |
| [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md) | RULED: (orchestrator, 2026-11-27) SELF-LOADER-WAITS-FOR-THE-REWRITE -- queued | `SELF-LOADER-WAITS-FOR-THE-REWRITE` |
| [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md) | RULED: (orchestrator, 2026-11-27) KEYWORD-FIELDS-MEASURED-ABSENT -- at 13:25: | `KEYWORD-FIELDS-MEASURED-ABSENT` |
| [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md) | RULED: (orchestrator, 2026-11-27) REFUSE-BEFORE-LOAD-ON-A-RETIRED-ROUTE -- at | `REFUSE-BEFORE-LOAD-ON-A-RETIRED-ROUTE` |
| [2026-11-27-rulings-integration-7.md](2026-11-27-rulings-integration-7.md) | RULED: (orchestrator, 2026-11-27) INBOX-SEARCH-IS-NOT-A-D1-SEARCH -- at 13:35: | `INBOX-SEARCH-IS-NOT-A-D1-SEARCH` |

### 5.1 Triaged -- a declaration hit that is not a ruling made here

**[2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md)** -- `**RULED:** same permalink ruling.`

> THE SAME RULING APPLIED TO A SECOND ROW, and the line says so in those words. `#3 react to an item` is decided by the permalink ruling declared two rows earlier under `#2 comment on an item`, registered as `PERMALINK-READ-IS-ALLOWED`. Giving it its own entry would put one ruling in the register twice under two ids, which is what `CANONICAL-RULING-ID` exists to stop. **This is the shape a register must get right or it manufactures rulings**: an APPLICATION of a ruling to a new row looks identical to a new ruling, and only reading the line separates them.

**[2026-09-19-the-four-absent-blockers.md](2026-09-19-the-four-absent-blockers.md)** -- `> RULED: THE CENSUS IS RIGHT. THE LEDGER'S `1R` IS THE ERROR. [...] **That `1R``

> A QUOTATION OF A RULING MADE ELSEWHERE, marked as one by its blockquote. The ruling is CENSUS-OUTRANKS-LEDGER, declared in `_audit/2026-09-19-the-three-ruling-requests-ruled.md` and registered under that id. Registering the quotation too would give one ruling two entries, which is precisely what CANONICAL-RULING-ID forbids.

**[2026-09-21-the-open-queue.md](2026-09-21-the-open-queue.md)** -- ``_audit/2026-09-19-two-census-conventions-ruled.md`): *"RULED: NO. THEY STAY`

> A THIRD QUOTATION OF `INCIDENTAL-CAPTURE-IS-NOT-A-RULING`, in section 5.4b -- the correction that exists BECAUSE that ruling was missed. The lead's 5.4a claimed the question had been re-derived three times and named only the 2026-09-03 origin; 5.4b cites the 2026-09-19 ruling it had overlooked, which is the one that says `RULED:` in a file named `...-ruled.md`. Registering the citation would put that ruling in the register a second time, which `CANONICAL-RULING-ID` forbids. **The entry is worth reading for what it records rather than what it silences**: this register was merged and, within minutes, refused the very document written to explain why the corpus could not be searched -- the instrument convicting its own commissioner on its first working day.

**[2026-09-21-the-open-queue.md](2026-09-21-the-open-queue.md)** -- `### 5.4 RULED: incidental capture is not a ruling -- and the discriminator is real, 08:40`

> A RE-DERIVATION, NOT A NEW RULING, and its own document says so. Section 5.4a: *'5.4 below presents itself as a new ruling. It is not one ... The ruling stands; the attribution in 5.4 is wrong.'* The ruling is INCIDENTAL-CAPTURE-IS-NOT-A-RULING, declared 2026-09-19. Filing 5.4 as an entry would record a fourth payment as a fourth ruling, which is the defect this register was built to end. The MEASUREMENTS in 5.4 -- the three-way discriminator and the anchor-termination finding -- are new and are good; they are evidence under the existing ruling, not a new one.

**[2026-09-21-what-was-ruled.md](2026-09-21-what-was-ruled.md)** -- `'> ### RULED: NO. THEY STAY GAP, WITH THE BLOCKER NAMED PRECISELY.'`

> TWO QUOTATIONS OF `INCIDENTAL-CAPTURE-IS-NOT-A-RULING` IN THE REPORT THAT BUILT THIS REGISTER -- once as a blockquote of the ruling under question Q1, once inside sample `--find` output. Neither decides anything. **Recorded rather than reworded, because this pair is the discovery half's only live demonstration**: the document was untracked while the register was being built, `--check` was green, and the instant it was staged the scan refused to stay green until somebody accounted for it. That is the whole mechanism, on a real document, and deleting the evidence to tidy the register would spend it.

**[2026-09-21-what-was-ruled.md](2026-09-21-what-was-ruled.md)** -- `> ### RULED: NO. THEY STAY GAP, WITH THE BLOCKER NAMED PRECISELY.`

> TWO QUOTATIONS OF `INCIDENTAL-CAPTURE-IS-NOT-A-RULING` IN THE REPORT THAT BUILT THIS REGISTER -- once as a blockquote of the ruling under question Q1, once inside sample `--find` output. Neither decides anything. **Recorded rather than reworded, because this pair is the discovery half's only live demonstration**: the document was untracked while the register was being built, `--check` was green, and the instant it was staged the scan refused to stay green until somebody accounted for it. That is the whole mechanism, on a real document, and deleting the evidence to tidy the register would spend it.

**[2026-09-21-what-was-ruled.md](2026-09-21-what-was-ruled.md)** -- `SECTION: RULED: NO. THEY STAY GAP, WITH THE BLOCKER NAMED PRECISELY.`

> TWO QUOTATIONS OF `INCIDENTAL-CAPTURE-IS-NOT-A-RULING` IN THE REPORT THAT BUILT THIS REGISTER -- once as a blockquote of the ruling under question Q1, once inside sample `--find` output. Neither decides anything. **Recorded rather than reworded, because this pair is the discovery half's only live demonstration**: the document was untracked while the register was being built, `--check` was green, and the instant it was staged the scan refused to stay green until somebody accounted for it. That is the whole mechanism, on a real document, and deleting the evidence to tidy the register would spend it.

