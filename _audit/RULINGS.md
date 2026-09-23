# THE RULINGS REGISTER -- one entry per RULING, not per document

**GENERATED. Do not hand-edit.** `scripts/build_rulings_index.py --write` rebuilds it; `--check` fails when it drifts, when a registered ruling stops resolving in the corpus, or when a `RULED:` declaration is neither claimed nor triaged.

`_audit/INDEX.md` answers *what did wave X report* and *what overtook this claim*. It cannot answer **what has been ruled about X**, and this file is that key. The receipt for why it exists is four payments for one answer -- see `_audit/2026-09-21-what-was-ruled.md`.

**WHERE and WHEN are DERIVED** from the corpus at the SHA this runs against; **CLAIM, BINDS and ALIASES are JUDGED** and hand-authored. Section headings are printed and line numbers are not, because `CANONICAL-RULING-ID` rules that a citation resolves to a symbol.

**THIS REGISTER IS NOT THE CORPUS AND DOES NOT CLAIM TO BE COMPLETE.** Read section 4 before concluding a question is unruled: the scan that keeps it honest reads ONE marker, and the ruling that caused this file to be written does not carry it.

    rulings registered       37
    documents scanned        234
    RULED: declarations      24 claimed, 7 triaged, 0 unclaimed

---

## 1. THE REGISTER, BY WHAT IT BINDS

Scan the CLAIM column against your question. Every claim is a paraphrase written to be matched; the ARGUMENT is in the document, under the section named.

### address family

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `DO-NOT-OPEN-MESSAGING` | Do not open messaging. Opening it opens a surface whose cost lands on other people, and the row is DEFERRED BY RULING. | /messaging/ | 2026-08-31 | [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md)<br>*#9 send a message / InMail -- `linkedin_send_message`. REFUSING, and now DEFERRED BY RULING.* |
| `ONE-NAMED-SETTINGS-PAGE-AT-A-TIME` | ONE NAMED settings page below `/mypreferences/d/` is admitted, one at a time. | /mypreferences/d/ | 2026-08-31 | [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md)<br>*#6 change a setting -- `linkedin_update_setting`. BUILT, NOT CAPTURED.* |
| `PERMALINK-READ-IS-ALLOWED` | `/feed/update/<urn>/` is allowed and an ordinary read of a post at its permalink is permitted; reacting rests on the same permalink ruling. | /feed/update/<urn>/ | 2026-08-31 | [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md)<br>*#2 comment on an item -- `linkedin_comment_on_item`. STILL REFUSING.* |
| `PROFILE-EDITOR-ADDRESSES-ALLOWED` | `/in/<member>/edit/` and the profile editors are allowed. | the profile editor surfaces | 2026-08-31 | [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md)<br>*#4 edit a profile field -- `linkedin_update_profile_field`. BUILT, NOT CAPTURED.* |
| `MUST-STAY-REFUSED-ENTRIES-COME-OUT` | `MUST_STAY_REFUSED` listing `groups` and `events` is wrong and must come out, or move to a class the admission does not reach. | the guard's must-stay-refused table | 2026-09-19 | [2026-09-19-search-admission-condition-2-amended.md](2026-09-19-search-admission-condition-2-amended.md)<br>*`MUST_STAY_REFUSED` LISTING `groups` AND `events` IS WRONG AND MUST COME OUT* |
| `SEARCH-ADMISSION-APPROVED-FIVE-CONDITIONS` | The search-results admission is APPROVED IN PRINCIPLE under five binding conditions, one of which is that nothing is FIRED from that surface. | /search/results/ | 2026-09-19 | [2026-09-19-two-census-conventions-ruled.md](2026-09-19-two-census-conventions-ruled.md)<br>*RULED: APPROVED IN PRINCIPLE. FIVE CONDITIONS, ALL BINDING.* |
| `SEARCH-CONDITION-2-CLOSED` | Condition 2 of the search admission demands CLOSED PATH SEGMENTS, not a NARROW ANCHORED pattern. Anchoring was measured to do none of the work assigned to it. | the shape of any allowlist pattern | 2026-09-19 | [2026-09-19-search-admission-condition-2-amended.md](2026-09-19-search-admission-condition-2-amended.md)<br>*CONDITION 2 IS AMENDED: **CLOSED**, NOT **ANCHORED*** |

### capability class

| id | what was ruled | binds | when | where (document / section) |
|---|---|---|---|---|
| `COMPOSER-IS-THE-REFUSAL-NOT-THE-ADDRESS` | For publishing a post the composer is the wall, not the address. | publish a post | 2026-08-31 | [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md)<br>*#1 publish a post -- `linkedin_publish_post`. STILL REFUSING. **Ruling declined back to him.*** |
| `INVITATION-TARGETING-IS-CALL-TIME` | Targeting an invitation is allowed as a CALL-TIME responsibility. | send a connection invitation | 2026-08-31 | [2026-08-31-linkedin-finish.md](2026-08-31-linkedin-finish.md)<br>*#7 send a connection invitation -- `linkedin_send_invitation`. STILL REFUSING, and the blocker is now a different one.* |
| `FEED-CONTENT-READ-RULING` | Feed content may be read as COUNTS AND RELATIONS ONLY, never text or names. | reads of feed and post content | 2026-09-05 | [2026-09-05-lead-rulings-round-two.md](2026-09-05-lead-rulings-round-two.md)<br>*5. `FEED-CONTENT-READ-RULING` -- COUNTS AND RELATIONS ONLY* |
| `MENTION-COMPOSITION-RULING` | Build the mention MECHANISM, forbid the SOURCE: composing a mention is permitted as a mechanism, and harvesting the candidate list it would mention from is not. | mentions in posts and comments | 2026-09-05 | [2026-09-05-lead-rulings-round-two.md](2026-09-05-lead-rulings-round-two.md)<br>*1. `MENTION-COMPOSITION-RULING` -- BUILD THE MECHANISM, FORBID THE SOURCE* |
| `MESSAGING-SETTINGS-CAPABILITY-LEVEL` | The settings-family ruling is CAPABILITY-level, not path-level: a setting is admitted BY NAME or not at all, which excludes every page below the settings index whatever its URL spelling. It says 'a setting', not 'a profile setting'. | every persisted account preference | 2026-09-05 | [2026-09-05-decide-retire-rulings.md](2026-09-05-decide-retire-rulings.md)<br>*3.10 `MESSAGING-SETTINGS` -- 5 rows, RE-FILED, NOT RETIRED* |
| `NO-IRREVERSIBLE-WRITE-IS-FIRED` | No irreversible write is fired at a real target -- not an application, a post, an invitation, a message or a comment. Permission to BUILD a capability is not consent to perform a specific act against a specific person. Writes may be designed, gated, tested against fixtures and left ready. | every write in the server, standing | 2026-09-05 | [2026-09-05-lead-rulings-round-two.md](2026-09-05-lead-rulings-round-two.md)<br>*The line I did NOT cross, and will not without him* |
| `STANDING-SHAPE-OF-A-WRITE-RULING` | Every new write gets the SAME bar the twelve shipped writes meet: design, WriteSpec, gate, consent text, tests against fixtures and synthetic targets, two calls behind a single-use action-bound target-bound token with a 120s TTL. Do not invent a stricter bar for a new capability, and do not weaken it. | the admission shape for any new write | 2026-09-05 | [2026-09-05-lead-rulings-round-two.md](2026-09-05-lead-rulings-round-two.md)<br>*8. The standing shape of every write ruling here* |
| `GATE-IS-SAFE-AND-BLIND` | The gate is SAFE and BLIND, and those are different properties: condition 4 cannot witness disclosure. | the disclosure witness on a press gate | 2026-09-19 | [2026-09-19-two-census-conventions-ruled.md](2026-09-19-two-census-conventions-ruled.md)<br>*DEFECT ONE: CONDITION 4 CANNOT WITNESS DISCLOSURE* |
| `GROUPS-ADDRESS-BUYS-NO-WRITE` | Admitting a group address buys nothing for joining, leaving, posting, commenting or inviting. Each needs its own url, its own write sanction and its own ruling, so those rows stay GAP and no boundary change moves them. The price is three things and an admission pays one. | groups writes, and any address widening | 2026-09-19 | [2026-09-19-groups-admission.md](2026-09-19-groups-admission.md)<br>*The eight writes: the census already ruled this, TODAY, against itself* |

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
| `EXCLUDED-RULED-ADMISSION` | A row is EXCLUDED-RULED only on one of FOUR written grounds: a forbidden-substring entry, a writes.PERMANENTLY_FORBIDDEN key, a WriteSpec refusing in its own words, or an audit passage measuring the capability unreachable. Anything a general mechanism merely happens to block is GAP with a NAMED BLOCKER. | the bar for EXCLUDED-RULED on every slice | ~2026-09-03 | [_census/network.md](_census/network.md)<br>*2. HOW A CAPABILITY WAS ASSIGNED A STATE* |

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
| dark mode | `ONE-NAMED-SETTINGS-PAGE-AT-A-TIME` |
| DECIDE not MEASURE | `GROUPS-ADDRESS-BUYS-NO-WRITE` |
| decide-retire-rulings section 2 | `BOUNDARY-IS-NOT-A-REASON` |
| DEFECT ONE | `GATE-IS-SAFE-AND-BLIND` |
| ERROR-MESSAGE-PROVENANCE | `ERROR-MESSAGE-RULED-AT-THE-RAISE` |
| ERROR-URL-PER-SITE | `ERROR-URL-ASKED-FOR-OR-NOTHING` |
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
| one canonical id | `CANONICAL-RULING-ID` |
| OWNED-BY-A-SIBLING-SLICE | `DUPLICATE-ROW-IS-MARKED-NEVER-DELETED` |
| P I12 -> J99 | `CONTAINER-EXCLUSION-PROPAGATES-ONLY-IF-UNREACHABLE` |
| P L2 -> L2 + L2b | `COMPOUND-ROW-SPLITS-ONLY-ON-STATE` |
| press.disclose | `DISCLOSING-PRESS-PERMITTED` |
| R11 | `MESSAGING-SETTINGS-CAPABILITY-LEVEL` |
| R9 | `DO-NOT-OPEN-MESSAGING` |
| request 1 | `CONVERSATION-OVERFLOW-BOTH-WAVES-RIGHT` |
| request 4 | `CENSUS-OUTRANKS-LEDGER` |
| request A | `MAP-CONVENTION-AT-HEAD-MEMBERSHIP` |
| request B | `N61-REMOVED-FROM-HASHTAG-EXISTENCE` |
| request C | `CONVERSATION-OVERFLOW-BOTH-WAVES-RIGHT` |
| request D | `PUBLISHED-SPLIT-REPORT-NOW-GATE-LATER` |
| request E | `CREATOR-HUB-AND-POST-COMMENT-LEDGER-OVERCOUNTS` |
| safety is a property of the code | `STANDING-SHAPE-OF-A-WRITE-RULING` |
| SCROLL | `SCROLL-NOT-SANCTIONED` |
| section 7 of lead-rulings-round-two | `SCROLL-NOT-SANCTIONED` |
| server.py::linkedin_update_setting | `MESSAGING-SETTINGS-CAPABILITY-LEVEL` |
| settings family | `MESSAGING-SETTINGS-CAPABILITY-LEVEL` |
| split or leave whole | `COMPOUND-ROW-SPLITS-ONLY-ON-STATE` |
| the 89 sub-expressions | `ERROR-MESSAGE-RULED-AT-THE-RAISE` |
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
| the write-partition's section 4.4.2 question | `COMPOUND-ROW-SPLITS-ONLY-ON-STATE` |
| third-party exception text | `ERROR-MESSAGE-RULED-AT-THE-RAISE` |
| two capabilities one row | `COMPOUND-ROW-SPLITS-ONLY-ON-STATE` |
| two-census-conventions section 1 | `CANONICAL-RULING-ID` |
| two-census-conventions section 2 | `CONTAINER-EXCLUSION-PROPAGATES-ONLY-IF-UNREACHABLE` |
| two-census-conventions section 3 | `INCIDENTAL-CAPTURE-IS-NOT-A-RULING` |
| what the browser said | `ERROR-MESSAGE-RULED-AT-THE-RAISE` |

---

## 3. NOTES ON INDIVIDUAL RULINGS

**`BOUNDARY-IS-NOT-A-REASON`** -- The application of EXCLUDED-RULED-ADMISSION that section 5.4a found. It quotes the census rule rather than restating it.

**`CANONICAL-RULING-ID`** -- THIS FILE IS THAT RULING'S ARTIFACT. It is why the register prints a section heading and never a line number, and why the aliases column exists at all.

**`COMPOUND-ROW-SPLITS-ONLY-ON-STATE`** -- THE EXACT COMPLEMENT OF `DUPLICATE-ROW-IS-MARKED-NEVER-DELETED` above -- that one governs two rows describing one capability, this one governs one row describing two. They were filed together for that reason. The asymmetry it rests on is MEASURED rather than argued: `reader_closable_blockers.DIRECTIONS` normalises four spellings of a both-DIRECTION onto `R+W`, while `count_census_states.classify` answers a two-STATE cell by silently taking the first by textual order or by dropping the row out of the census, raising no dialect either way. Direction can be told the truth in the cell; state cannot. The corpus had already decided this eight times without naming it -- seven non-splits (`P M6` `P M9` `P M11` `M M28` `M C47` `N 125`, plus `J 71` declining in writing) and the one split, `P L2` -> `L2` + `L2b`, whose halves are BOTH reads and which therefore refutes a direction-based rule.

**`CONTAINER-EXCLUSION-PROPAGATES-ONLY-IF-UNREACHABLE`** -- Built ON `P I12` as a SOUND exclusion: *zero of 237 urls reach one* is ground four of EXCLUDED-RULED-ADMISSION. Two later documents call `P I12` a miscategorisation; see the register's DISPUTED note in the report for this wave.

**`ERROR-MESSAGE-RULED-AT-THE-RAISE`** -- THE SIBLING OF `ERROR-URL-ASKED-FOR-OR-NOTHING`, and it goes the OTHER WAY for a stated reason rather than by temperament. The url field could be ruled PER SITE because every value feeding it is an address this package composed or read; `$.message` cannot, because `_error` holds only `type(exc)` and `str(exc)` and the provenance of what that text QUOTES is not among them. So the ruling moves the decision to the raise, which is where the corpus had already put it three times without naming it: `coerce.py`, `press.disclose` and `landing.py`. It also DECLINES the sibling's own recommendation to make the twelve `dom.py` messages type-only -- all twelve are inside `tests/test_readers_emit_no_page_string.py`'s driven subject set and green (4 clean, 8 returns_text, 0 not_driven), so the payload class is already closed for them and type-only would delete twelve diagnoses to close a channel no needle travels. What it SHIPPED is the other end of the pipe: `tests/test_tool_envelopes_emit_no_page_string.py`, because the reader guard discovers only `async def` functions taking a `page` and the 48 tool bodies that funnel into `_error` are therefore outside it, permanently.

**`ERROR-URL-ASKED-FOR-OR-NOTHING`** -- THE FAILURE-PATH COUNTERPART OF THE `source_url` SPLIT RULING in `tests/test_the_source_url_split_was_never_ruled.py`, which is NOT registered here because it lives as a test rather than as an audit passage. Same kind of value -- the address a read landed on -- in several of the SAME functions, and the two were ruled by different files that did not know about each other: `linkedin_my_profile` was declared SHAPED on its success path and published its landing raw on its failure path, in one function, for weeks. That ruling supplied the METHOD used here (a per-site declaration with a written reason, a count per site, a relay pinned as a relay, and drift failing in BOTH directions) and its prohibition is what stopped this wave wrapping all twenty: *wrapping a deliberate publication is as much a defect as leaking an accidental one.* The count each way is 12 withheld, 7 published, 1 relay.

**`EXCLUDED-RULED-ADMISSION`** -- Written twice, once per slice, in near-identical words; `_audit/_census/profile.md` carries the twin. This is the ORIGIN of the forbidden-substring question and it already answers it: a substring entry counts only when it is one of the four WRITTEN grounds, i.e. when it was aimed at the capability.

**`FEED-CONTENT-READ-RULING`** -- The ground `M C85`'s read half would rest on if that row were ever split -- see OPEN-QUESTIONS.

**`GROUPS-ADDRESS-BUYS-NO-WRITE`** -- Stated in `readonly.py`'s own comment and quoted here. The companion rule that a widening is reported by what it BANKS rather than by what it UNBLOCKS sits in the same section.

**`INCIDENTAL-CAPTURE-IS-NOT-A-RULING`** -- THIS IS THE ANSWER TWO WAVES ESCALATED AS UNDECIDED AND A THIRD RE-DERIVED. It carries the three-way GENERAL FORM table that the 2026-09-21 re-derivation reconstructed from measurement. Its own citation is the 2026-09-03 ledger passage, so the chain is: census rule -> ledger asks -> 09-05 applies -> 09-19 RULES -> 09-21 re-derives.

**`MESSAGING-SETTINGS-CAPABILITY-LEVEL`** -- The ruling CANONICAL-RULING-ID was written about: one sentence wearing three names across three slices. Its census twin is `_audit/_census/profile.md`.

**`NO-IRREVERSIBLE-WRITE-IS-FIRED`** -- The single widest write ruling in the corpus. It separates BUILD from FIRE, which is the distinction most re-escalations about writes collapse.

**`PERMALINK-READ-IS-ALLOWED`** -- `M C42` records that this ruling DID NOT REACH naming the target -- which is why that row cannot rest on it. See the DISPUTED section of `_audit/2026-09-21-what-was-ruled.md`.

**`SEARCH-ADMISSION-APPROVED-FIVE-CONDITIONS`** -- Condition 2 was AMENDED the same day -- see SEARCH-CONDITION-2-CLOSED. The ruling bars FIRING, not READING; conflating the two cost a later wave a decision it did not need.

---

## 4. WHAT THIS REGISTER DID NOT SCAN

**The discovery scan reads `RULED:` and nothing else.** It was chosen on precision -- 24 of 25 hits are genuine declarations, the best of fourteen signals measured -- and its recall is poor. The counts below are signals a ruling can be written under that this scan will NEVER see. They are printed every run so that a green check is not read as a complete one.

| signal NOT scanned | files | lines |
|---|---|---|
| a heading naming a ruling | 108 | 240 |
| a bold line opening on RULING/RULED | 53 | 117 |
| the phrase THE RULING | 35 | 55 |
| a named -RULING id | 23 | 52 |
| the phrase standing ruling | 13 | 24 |
| a lead or operator ruling in prose | 32 | 66 |

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

