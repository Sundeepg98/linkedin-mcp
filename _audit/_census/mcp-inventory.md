# MCP inventory -- what this server ACTUALLY DELIVERS

The inward half of the capability census, 2026-09-03. Read-only pass over the
code at HEAD and over `_audit/*.md`. Nothing was invoked, no page was loaded,
no tracked file was touched, nothing was committed.

Method: the tool surface and every write spec were dumped STRUCTURALLY by
importing `linkedin_server.writes` and `linkedin_server.readonly` under
`venv/Scripts/python.exe`, not transcribed by eye. Evidence classes were
assigned from audit prose, cited to file and line, and every load-bearing
citation was re-read at source before it was written down here.

---

## TWO THINGS THAT BELONG ABOVE THE COUNTS

### ZERO JOB APPLICATIONS HAVE EVER BEEN SUBMITTED THROUGH THIS SERVER

`apply_job` has been fired exactly once, on a real posting with a real
employer, with the operator's authorisation. It did not submit. The Applied
tab still reads zero (`_audit/2026-08-31-linkedin-perform.md:1039`).

The gate held on its own logic, and it is worth being precise about why,
because "it refused" and "it broke" are different claims and the file
distinguishes them. `_apply_submit_gate` has five conditions and one of them
refused -- that is the gate working. The two defects found by that firing were
both about REPORTING the outcome, not about causing the refusal: the
verification read `?stage=saved` while `to_state` is `applied`, so
"`verified_state == \"applied\"` was FALSE on every reading it could ever
take" (`:796-798`); and the gate's own refusal sentence was assigned to a local
and never read, so he got a refusal that could not say what it saw (`:826-828`).
Both are fixed, and the live block was reproduced as a mutation:
`expected_state "applied"`, `observed_state "unknown"`, `read_from ?stage=saved`
(`:844-846`).

**The consequence for planning: the next fire is the first real submit this
server will ever have made.** The earlier firing exercised a path that could
not pass. It is not a rehearsal that de-risks the next one.

### `publish_post` HAS NO AUDIENCE PARAMETER, AND THE CONTROL WAS MEASURED

`linkedin_publish_post(text: str, confirm_token: str = "")`
(`linkedin_server/server.py:4050`). There is no audience, visibility or
recipient argument. Its full docstring contains none of the words *audience*,
*visibility*, *Anyone*, *connections only*, *who sees* or *public* -- verified
by a case-insensitive grep over the whole docstring, zero hits.

This is not a surface nobody looked at. The live composer census recorded the
control: "Also in the dialog: `Add media`, `Celebrate an occasion`, `Create an
event`, `Schedule post`, `More`, `Dismiss`, and **an audience control**"
(`_audit/2026-08-31-linkedin-perform.md:166`, `/preload/sharebox/`, 31 controls
read, no redirect). It was seen, recorded in three words, never named, never
read, and never wired.

**The gate therefore tells him HOW MANY people may see a post and never WHO
MAY.** The spec's `residue` quantifies reach precisely -- 275 followers, past
posts at 103, 308 and 1,284 impressions -- and the word "audience" appears
there in a different sense entirely, meaning the people who saw it
("IRREVERSIBLE IN AUDIENCE"). One meaning of the word is present and
quantified; the other, the setting that decides the blast radius before the
post exists, is absent. That collision is why the gap reads as covered.

This is a consent finding as much as a reversibility one. He confirms a token
for an irreversible broadcast without being told, or being able to choose, who
receives it -- the tool presses `Post` against whatever LinkedIn has selected,
and no code path here could read that value back afterwards.

**Cost to close: one read.** The control is already inside a dialog the census
enumerates, on an address already on the allowlist. Capturing its accessible
name and state needs no new mutation, no new boundary and no operator ruling.
It is the cheapest unclaimed capability in this inventory.

---

## COUNTS

### 35 tools by evidence class

| class | count |
|---|---|
| PROVEN-LIVE | 17 |
| TESTED-ONLY | 10 |
| FIRED-GATE-HELD | 1 |
| COVERED-CANNOT-DELIVER | 1 |
| KNOWN-BROKEN | 1 |
| UNKNOWN | 5 |
| **total** | **35** |

**SIX states, not four.** The brief named four and two of the twelve writes
fit none of them. Both additions describe a tool that HAS been fired live,
which is why neither can be called TESTED-ONLY without inverting a
measurement -- "nobody tried" is the one thing that is false about both.

- **FIRED-GATE-HELD** -- `apply_job`. Invoked live, on a real posting, and the
  gate stopped it before it touched LinkedIn. Neither proven-working (nothing
  was submitted) nor broken (the gate did its job). The artefact it leaves is
  the strongest evidence this server has that its safety machinery works
  outside a fixture, and folding it into either neighbour discards that.
- **COVERED-CANNOT-DELIVER** -- `send_message`. The tool exists, was fired
  against a real composer, and cannot do the thing. A surface census joining
  on tool names will count this as covered; it is the opposite. Distinguishing
  it from FIRED-GATE-HELD matters because the two look identical from outside
  -- both fired, both refused -- and one is a working gate while the other is
  a dead approach.

### 12 PERFORMABLE writes by reversibility

| reversibility_class (the code's own verdict) | count |
|---|---|
| REVERSIBLE | 4 |
| STILL-UNKNOWN | 8 |
| IRREVERSIBLE | 0 |

| can this server PERFORM the undo? | count |
|---|---|
| yes -- the undo is a tool call this server can make | 4 |
| no -- the undo tool exists but CANNOT BE AIMED at what the action creates | 2 |
| no -- the undo is permanently forbidden here, or no selector for it exists | 6 |

No action carries the class IRREVERSIBLE. That is not because nothing here is
irreversible. It is because this design splits the question: the CLASS
describes the state (can the bit be flipped back), and a separate `residue`
field carries "IRREVERSIBLE IN AUDIENCE". Five actions are described in
`residue` as irreversible in audience while their class is STILL-UNKNOWN. A
reader who looks only at the class column will undercount the risk by five.

### Unfired writes with a safe live-fire test versus without

11 of the 12 writes have never landed on LinkedIn. `send_message` is settled
and excluded from proposal per the brief, leaving 10 to cost out.

| | count |
|---|---|
| safe test exists, and it is concrete | 5 |
| safe test exists but carries a NAMED UNMEASURED cost | 2 |
| no safe test -- the smallest version is still the full act | 3 |
| **total costed** | **10** |

The single cheapest live-fire available in this whole design is
`update_setting` on dark mode. The corpus says why, in its own words:
"no audience, no other member can observe it, broadcast nowhere, appears in no
feed and no notification, and the same tool sets it back"
(`_audit/2026-08-31-linkedin-perform.md:135-138`).

### Where the team lead's grep hypothesis was wrong

The brief carried a hypothesis from a keyword count: that `save_job`,
`unsave_job`, `follow_company` and `apply_job` have live-fire evidence and
eight of the twelve writes have none. Checked, it is wrong in three of four
places, and wrong in the same direction each time.

| action | hypothesis | measured |
|---|---|---|
| `save_job` | live-fire | CORRECT -- one redeemed save, 2026-08-30 |
| `unsave_job` | live-fire | WRONG -- "`unsave_job` was never fired, including after it became capable" (`_audit/2026-08-30-linkedin-undo.md:1775`) |
| `follow_company` | live-fire | WRONG -- the word matched is a section header reading "**PERFORMED**", which is a CAPABILITY verdict |
| `apply_job` | live-fire | WRONG -- fired once and REFUSED. "IT DID NOT SUBMIT" (`_audit/2026-08-31-linkedin-perform.md:790-791`) |

The mechanism is worth keeping, because it will recur in this repo: **this
corpus uses PERFORMS / PERFORMED / PERFORMABLE as a capability word**, meaning
the gate no longer refuses by design. It never means the action fired. Every
receipts block in the 4145-line `2026-08-31-linkedin-perform.md` reports
`confirm_tokens 0 minted, 0 used`, and its own opening line reads: "No
`confirm_token` was used, by anyone, at any point"
(`_audit/2026-08-31-linkedin-perform.md:7`). A grep for a write verb finds the
capability table, not the firing record, and the two are one word apart.

The real number: **1 of 12 writes has ever landed on LinkedIn.** Not four.

All twelve were checked this way, against a cited line rather than a keyword
hit -- every row in the write ledger below carries a file and line number, and
the four that decide the count (`save_job`, `unsave_job`, `follow_company`,
`apply_job`) plus `send_message` were re-read at source by me personally
before being written down. The `save_job` proof is the clean one and worth
keeping as the pattern for what counts: the ON label "Unsave the job" exists
in this repo only because a real save produced it, so the artefact could not
have been created by anything except the write landing.

---

# DELIVERABLE ONE -- THE TOOL LEDGER

35 tools: 23 read/session, 12 write. Surface = the LinkedIn address or
subsystem the tool touches.

## Read and session tools (23)

| # | tool | R/W | surface | class | evidence |
|---|---|---|---|---|---|
| 1 | `linkedin_auth_status` | R | identity endpoint | PROVEN-LIVE (weak) | "one `linkedin_auth_status`. No `confirm_token` was passed" -- `_audit/2026-08-30-save-label.md:698-699`. Run confirmed; return value never quoted |
| 2 | `linkedin_login` | R | `/login/` + a human | UNKNOWN | zero run records anywhere in the corpus. A session demonstrably exists (cookie read live), so SOMETHING logged in; whether through this tool is unrecorded |
| 3 | `linkedin_login_browser` | R | alias of #2 | UNKNOWN | deprecated alias, forwards to `linkedin_login`. Same absence |
| 4 | `linkedin_session_info` | R | cookie jar, no browser | PROVEN-LIVE | "reports `li_at` expiring 2027-08-21T17:12:37Z, 364.4 days with no browser at all" -- `_audit/2026-08-22-linkedin-preflight.md:10` |
| 5 | `linkedin_logout` | R/W-local | local Chrome profile | TESTED-ONLY | "`linkedin_logout` was never run against the real `_state` Chrome profile" -- `_audit/2026-08-23-linkedin-auth-slice.md:198`. Exercised only against a temp profile |
| 6 | `linkedin_cdp_status` | R | local CDP port | UNKNOWN | two hits in the whole corpus, both table rows. No narrative, no probe, no result |
| 7 | `linkedin_who_viewed_me` | R | `/analytics/profile-views/` | PROVEN-LIVE | "reads the receiving end of exactly that signal, 365 days back on his Premium Career account" -- `_audit/2026-08-30-linkedin-writes.md:198-201` |
| 8 | `linkedin_my_applications` | R | `/jobs-tracker/?stage=applied` | PROVEN-LIVE | "0 rows, count 0, empty state \"No matches\", correctly reported EMPTY" -- `_audit/2026-08-30-linkedin-undo.md:34` |
| 9 | `linkedin_draft_applications` | R | `/jobs-tracker/?stage=draft` | PROVEN-LIVE | "1 row, `tab_counts {saved:1, draft:1, applied:0, interview:0}`" -- `_audit/2026-08-30-linkedin-undo.md:33` |
| 10 | `linkedin_new_messages` | R | `/feed/` badge | PROVEN-LIVE | "badge read ZERO first through `linkedin_new_messages` off `/feed/`, settle verdict `consistent`, 77 controls expected and 77 read" -- `_audit/2026-08-31-linkedin-perform.md:3099-3101` |
| 11 | `linkedin_open_messaging` | R | `/messaging/thread/...` | UNKNOWN | deliberately never called, four waves running: "This wave did NOT call `linkedin_open_messaging`" -- `_audit/2026-08-30-linkedin-writes.md:335`. Every call opens a real thread with a third party |
| 12 | `linkedin_saved_jobs` | R | `/jobs-tracker/?stage=saved` | PROVEN-LIVE | worked 08-23, broke 6-of-6 on 08-30, fixed same day, confirmed 08-31: "count 1, linkedin_count 1, tab_counts {saved:1, in_progress:1, ...}" -- `_audit/2026-08-31-linkedin-finish.md:74-77`. LATEST reading is GOOD |
| 13 | `linkedin_search_jobs` | R | `/jobs/search/` | PROVEN-LIVE | "10 calls, 8s x2, 9s x5, 10s, 12s, 14s -- never once below 8 s", always full rows -- `_audit/2026-08-30-jobs-view-reliability.md:119-124` |
| 14 | `linkedin_job_detail` | R | `/jobs/view/<id>/` | PROVEN-LIVE | 12 of 15 live calls failed `missing: description` on 08-30 AM (`_audit/2026-08-30-jobs-view-reliability.md:53-60`); fixed same day, "4456021840 DRAWS IN FULL ... Read twice consecutively; the two readings are identical" -- `_audit/2026-08-30-description-readiness.md:241-243`. LATEST reading is GOOD |
| 15 | `linkedin_followed_companies` | R | `/mynetwork/network-manager/company/` | PROVEN-LIVE | "renders 20 rows under a heading saying 58 Pages" -- `_audit/2026-08-23-measure-linkedin.md:52-54` |
| 16 | `linkedin_my_profile` | R | `/in/me/` (+ details) | PROVEN-LIVE | "a live load today agrees ... `linkedin_my_profile` now reports the state and the audience" -- `_audit/2026-08-23-measure-linkedin.md:42-46` |
| 17 | `linkedin_notifications` | R | `/notifications/` | UNKNOWN | "`linkedin_notifications` and `linkedin_logout` were never called" -- `_audit/2026-08-23-measure-linkedin.md:69`, still true at `_audit/2026-08-31-linkedin-lift.md:1456`. Opening the page CONSUMES his unread badge, which is why |
| 18 | `linkedin_surface_census` | R | 9 keyed surfaces | PROVEN-LIVE | "counts forms 0 buttons 20 links 7 dialogs 1 contenteditable 2 <- THE FIRST NON-ZERO EVER MEASURED" -- `_audit/2026-08-31-linkedin-perform.md:153-158` |
| 19 | `linkedin_compose_fields` | R | `/messaging/compose/` | KNOWN-BROKEN | "`read_compose_fields` cannot see either of them, by CONTAINMENT ... both radios containers: {\"none\": 1} -- no form ancestor" -- `_audit/2026-08-31-linkedin-perform.md:3113-3118`. A fix is claimed at `:3427-3429`; NO live re-read of the fixed reader exists anywhere. Last LIVE measurement says broken |
| 20 | `linkedin_profile_editor_fields` | R | `/in/me/edit/intro/` | PROVEN-LIVE, with a standing defect | works: "container dialog, anchor \"Save\", 23 controls" -- `_audit/2026-08-31-linkedin-perform.md:2039-2046`. And intermittently refuses falsely: "The first call ... refused: no_self_assertion ... An immediate retry, same code, same page, seconds later, SUCCEEDED ... THIS IS THE SECOND FALSE REFUSAL FROM THIS GATE" -- `:2987-3004`. Unresolved |
| 21 | `linkedin_profile_editor_values` | R | `/in/me/edit/intro/` | PROVEN-LIVE | "Their values read perfectly -- the value reader returned both" -- `_audit/2026-08-31-linkedin-perform.md:2955-2957`. No refusal on record for this one |
| 22 | `linkedin_my_activity_items` | R | `/in/me/` activity rail | PROVEN-LIVE | "run twice, identically: ... authors_found 1 / unanimous true / permalink_anchors 20 / distinct_urns 8" -- `_audit/2026-08-31-linkedin-perform.md:276-285` |
| 23 | `linkedin_server_info` | R | local process | PROVEN-LIVE | "reported the running process at `d0d3e3b65d52` against a checkout at `0767eb63f7b9` -- seven commits stale" -- `_audit/2026-08-30-description-readiness.md:225-237` |

## Write tools (12)

Every one is behind the same two-call gate: a token-free call returns a
PREVIEW built from a live read and mints a single-use `confirm_token`; a
second call carrying that token performs. All of it is behind a per-process
environment flag, `LINKEDIN_ENABLE_WRITES`, off by default
(`linkedin_server/writes.py:189-193`).

| # | tool | surface | class | evidence |
|---|---|---|---|---|
| 24 | `linkedin_save_job` | `/jobs/view/<id>/` | **PROVEN-LIVE** | the only write that has landed. "`writes.perform` gate-5 sweep, on the redeemed save -> `newly_observed_save_label: \"Unsave the job\"`" -- `_audit/2026-08-30-linkedin-undo.md:433`, and "it is the whole reason gap 1 stayed circular after the save landed" -- `:174`. Corroborated by three read-only re-reads at 21:03, 21:04, 21:36 (`:434-436`) |
| 25 | `linkedin_unsave_job` | `/jobs/view/<id>/` | TESTED-ONLY | "`unsave_job` was never fired, including after it became capable" -- `_audit/2026-08-30-linkedin-undo.md:1775` |
| 26 | `linkedin_apply_job` | `/jobs/view/<id>/` | **FIRED-GATE-HELD** | "The operator authorised his first apply; the lead performed it. **IT DID NOT SUBMIT.** The gate held, on an irreversible action, on a real posting with a real employer at the other end" -- `_audit/2026-08-31-linkedin-perform.md:790-791`. One of `_apply_submit_gate`'s five conditions refused; the two defects that firing exposed were both about REPORTING (a verification reading the wrong tab, and a refusal sentence assigned to a local and never read), not about causing the refusal. Both fixed. **The Applied tab reads zero** (`:1039`) -- no application has ever been submitted |
| 27 | `linkedin_unfollow_company` | `/mynetwork/network-manager/company/` | TESTED-ONLY | no receipt, no timestamp, no company id anywhere in the corpus. Not mentioned after 2026-08-24 |
| 28 | `linkedin_follow_company` | `/jobs/view/<id>/` (posting) | TESTED-ONLY | the "**PERFORMED**" header at `_audit/2026-08-30-linkedin-writes.md:273` is capability language: the same section says "The only one of the eight that CAN act" (`:274`) and "**What firing it would cost him:** a follow can surface in his network's feed" (`:317`) -- future-conditional. Never mentioned again in any later document |
| 29 | `linkedin_publish_post` | `/preload/sharebox/` | TESTED-ONLY | "**BUILT, REFUSING.**" -- `_audit/2026-08-30-linkedin-writes.md:57`; later capability-only "PERFORMS" in a table whose wave reports "confirm_tokens 0 minted, 0 used" (`_audit/2026-08-31-linkedin-perform.md:1794`) |
| 30 | `linkedin_comment_on_item` | `/feed/update/<urn>/` | TESTED-ONLY | "**BUILT, REFUSING.**" -- `_audit/2026-08-30-linkedin-writes.md:89`; later "PERFORMS, expecting to refuse" (`_audit/2026-08-31-linkedin-perform.md:1566`), which is a capability verdict |
| 31 | `linkedin_react_to_item` | `/feed/update/<urn>/` | TESTED-ONLY | never invoked, live or refused. The plan deliberately ROUTES AROUND the tool: "In his own browser, not through this server" -- `_audit/2026-08-31-linkedin-lift.md:491`; "the supervised act is the operator's, and it is not scheduled. No token can exist" -- `:1072` |
| 32 | `linkedin_update_profile_field` | `/in/me/edit/intro/` | TESTED-ONLY | shipped performable 2026-09-02. "**Nothing fired. No `confirm_token` for any of the ten.**" -- `_audit/2026-08-31-linkedin-perform.md:2176`. NOTE: it shipped in `a540461` UNABLE TO ACT on three fatal blockers and was repaired the same day in `ea5354d` (`_TEAM_LEAD_SUCCESSOR_BRIEF.md`, correction header). Nothing has exercised the repair |
| 33 | `linkedin_update_setting` | `/mypreferences/d/dark-mode` | TESTED-ONLY | the most explicit non-firing statement in the corpus: "### 1f. It was NOT fired, and I did not call the tool at all" -- `_audit/2026-08-31-linkedin-perform.md:140`; "the round trip is UNPERFORMED" -- `:122` |
| 34 | `linkedin_send_invitation` | `/in/<member>/` | TESTED-ONLY | "STILL REFUSES. No anchor was wired, no `SANCTIONED_MUTATIONS` entry was added" -- `_audit/_slice-invitation-needle.md:8`. Outcome DECLARED unverifiable in code |
| 35 | `linkedin_send_message` | `/messaging/compose/` | **COVERED-CANNOT-DELIVER** | invoked live and refused: "A supervised run typed a correct, first-degree name into an empty composer; `writes._recipient_gate` returned `1_no_recipient_committed` with all four chip selectors reading zero. **A bare fill commits nobody.**" -- `_audit/2026-09-03-typeahead-name-matching-is-dead.md:49-52`. Then measured DEAD, closed negative the same day: "every row LinkedIn returns contains the needle 10 of 10 / no row BEGINS with the needle 0 of 10 / the needle starts at ELEVEN different character offsets" -- `:26-31`. The addressing primitive cannot discriminate. This is not "not yet fired"; it is measured unable to work as designed |

Two harness-level refusals are on record and are NOT counted as evidence about
this server, because they never reached it: `linkedin_send_invitation`,
`linkedin_send_message` and `linkedin_update_setting` were each blocked by the
Claude Code permission classifier on 2026-08-31, "which sits outside" the
LinkedIn server (`_audit/2026-08-31-linkedin-lift.md:34-39`). No page loaded,
no gate ran.

---

# DELIVERABLE TWO -- THE REVERSIBILITY TABLE

The repo already reasons about this and I did not invent a scheme. Every
sanctioned write carries seven fields on its `WriteSpec`: `reversibility`
(the sentence), `reversibility_class` (one word), `reversibility_measured`,
`reversibility_evidence`, `reversible_by`, `residue`, and
`reversibility_procedure`. The rule they serve is stated in the module
docstring at `linkedin_server/writes.py:65-82`:

> "A GATE MAY NOT PRINT A REVERSIBILITY CLAIM THAT HAS NOT BEEN MEASURED."

There are THIRTEEN write specs and TWELVE write tools. The thirteenth,
`linkedin_set_open_to_work`, is a spec with no `@mcp.tool()` and is not in
`PERFORMABLE`. It is out of scope for this table and is named so nobody later
reads 13 against 12 as an arithmetic error.

| action | class | measured | exact counter-action | is the undo PERFORMABLE here? |
|---|---|---|---|---|
| `save_job` | REVERSIBLE | yes | `linkedin_unsave_job` on the same posting | **YES** -- sanctioned and performable |
| `unsave_job` | REVERSIBLE | yes | `linkedin_save_job` on the same posting | **YES** -- sanctioned and performable |
| `update_setting` | STILL-UNKNOWN | no | the SAME tool with a different destination named | **YES** -- "THIS SERVER, by calling this same tool with a different destination" |
| `update_profile_field` | STILL-UNKNOWN | no | the SAME tool, with the previous value the tool itself returns | **YES** -- see defect D4 below; the spec's own prose denies this |
| `follow_company` | REVERSIBLE | yes | `linkedin_unfollow_company` | **NO -- CANNOT BE AIMED.** A posting names its employer by SLUG; the unfollow surface addresses rows by NUMERIC id; "a census of every capture in this repo on 2026-08-24 found zero postings carrying a numeric id and zero Manage-Pages rows carrying a slug" |
| `unfollow_company` | REVERSIBLE | yes | `linkedin_follow_company` | **NO -- CANNOT BE AIMED**, same gap in the other direction. `follow_company` is addressed by `job_id`, so re-following needs a live posting from that company |
| `apply_job` | STILL-UNKNOWN | no | withdrawing the application | **NO** -- withdrawing is in `PERMANENTLY_FORBIDDEN`, and `/withdraw` is on the forbidden URL list |
| `publish_post` | STILL-UNKNOWN | no | deleting the post | **NO** -- deletion permanently forbidden; `/delete` on the forbidden URL list |
| `comment_on_item` | STILL-UNKNOWN | no | deleting the comment | **NO** -- same two grounds |
| `send_invitation` | STILL-UNKNOWN | no | withdrawing the invitation | **NO** -- and the Sent-invitations manager is doubly unreachable: its address contains `invitation` (forbidden), and reaching it via `/mynetwork/` CONSUMES his pending-invitation badge |
| `send_message` | STILL-UNKNOWN | no | recalling the message | **NO** -- "deletion is permanently forbidden here and `/messaging/compose` is on the read boundary's forbidden list" |
| `react_to_item` | STILL-UNKNOWN | no | un-reacting -- **the control for it has never been observed** | **NO** -- "with the ON label unmeasured there is no selector for the inverse, so nothing here could aim an un-react even if LinkedIn offers one" |

## The risk class the class column does not show

Five actions are described in their own `residue` field as IRREVERSIBLE IN
AUDIENCE while their class reads STILL-UNKNOWN, and one REVERSIBLE action
carries the same residue. This is the design working, not failing -- but it
means the class column alone understates the risk on half the table.

- `apply_job` -- "An application is READ BY A HUMAN at the employer, usually within a day."
- `publish_post` -- "his profile reports 275 followers and LinkedIn's own analytics on that page show past posts reaching 103, 308 and 1,284 impressions ... a post is the one artefact here a CURRENT EMPLOYER sees without looking."
- `comment_on_item` -- "A COMMENT SITS UNDER SOMEBODY ELSE'S ITEM ... it notifies the author, and it stays attached to their content."
- `send_invitation` -- "AN INVITATION IS A REQUEST TO A REAL PERSON ... LinkedIn restricts accounts whose invitations are frequently ignored."
- `send_message` -- "This is the most irreversible-in-audience action in the whole design."
- `follow_company` (class REVERSIBLE) -- "A follow can surface in his network's feed, so the data is restorable and the impression is not."

**And on `publish_post` the residue quantifies the audience it cannot choose.**
See the finding at the top of this file: the spec states reach precisely (275
followers; 103, 308 and 1,284 impressions) while the tool has no audience
parameter and its docstring never names one, and the composer's audience
control was measured and left unread. Every impression figure in that residue
is conditioned on a setting nobody here reads, so the residue's own numbers
are the reach of PAST posts under whatever audience those were published to,
not a prediction about the next one. That is a reversibility claim resting on
an unmeasured variable, and it is the only one in the table that does.

## PROSE THAT CLAIMS WHAT THE CODE DOES NOT DELIVER

Four found. All four are in `reversible_by` or `residue`, which is exactly the
text the confirm gate prints to the operator before he approves a write.

The existing guard cannot catch any of them. `_assert_reversibility_disagreement`
(`linkedin_server/writes.py:3937-3965`) checks only that the class word and the
FIRST WORD of the sentence agree -- REVERSIBLE requires prose starting
"reversible", IRREVERSIBLE requires prose not starting "reversible". It never
compares `reversible_by` or `residue` against `PERFORMABLE`, against the
forbidden lists, or against the exemption table. **There is no test in
`tests/` that binds any of this prose to `PERFORMABLE` membership.** The
tests that do touch `reversible_by` (`tests/test_writes.py:1639-1677`,
`:2191-2194`, `tests/test_writes_nine.py:1487-1502`) pin literal phrases --
`"NOT this server"`, `"slug"`, `"numeric company id"`, `"NOBODY"` -- which
means they LOCK the stale text in place rather than detecting it.

### D1 -- `follow_company.residue` says the action is not performed. It is.

Current text, live at HEAD:

> "SECOND, AND IT IS WHY THIS ACTION IS STILL NOT PERFORMED: THE UNDO CANNOT
> BE AIMED."

`follow_company` IS in `writes.PERFORMABLE` (verified by importing the module).
Commit order settles it: the sentence was last written in `c89d0b2`
(commit 69 of 315); `follow_company` was added to `PERFORMABLE` in `050349f`
(commit 148); nothing since corrected the residue. The repo's own
`tests/test_server_surface.py:1180-1187` documents the change explicitly --
"FOLLOW_COMPANY LEFT THIS FIELD ON 2026-08-30 ... Follow left because it
became performable; the blocker it carried ... now lives on the spec in
`reversible_by`" -- so the demotion of the blocker from a gate to a disclosure
was deliberate and recorded, and the residue was simply not updated with it.
**Severity: the safety conclusion is unchanged, the reason he would read is
false.** Same shape as trap 4 in the successor brief.

### D2 -- `unfollow_company.reversible_by` says follow is not performed. It is.

> "linkedin_follow_company is sanctioned but is not performed, so a re-follow
> through this server does not exist."

The clause "is not performed" is false at HEAD. The CONCLUSION -- that a
re-follow cannot be aimed -- remains true, for the slug-versus-numeric-id
reason, and `follow_company`'s `target_kind` is `job_id`, so a re-follow needs
a live posting from that company. **Severity: conclusion right, stated
mechanism wrong.** A reader who checks the claim finds the tool performable and
has no way to tell which half of the sentence survived.

### D3 -- `save_job` prints a failure that has since been fixed.

Two places, both live at HEAD (`linkedin_server/writes.py:452`, `:473`):

> "Measured 2026-08-30, it is also currently FAILING that way: the Saved tab's
> rows draw and the harvest returns none, so this direction source reports
> 'unknown' and the gate refuses."

> "the undo's own preview reads the Saved tab for its direction, and that read
> is currently failing, so the undo may have to be done by hand until it is
> fixed."

`linkedin_saved_jobs` was fixed later the same day and confirmed working on
2026-08-31: "count 1, linkedin_count 1, tab_counts {saved:1, in_progress:1,
...}" (`_audit/2026-08-31-linkedin-finish.md:74-77`). **Severity: understates
capability.** It tells him the undo may need doing by hand when the undo tool
works. Mitigating: the prose dates itself ("Measured 2026-08-30"), so it is
stale rather than unfalsifiable.

### D4 -- `update_profile_field.reversible_by` denies a restore path the code ships. This is the worst of the four.

> "HIM, by hand, in LinkedIn's own interface -- and only if he still knows the
> previous value, WHICH NOTHING HERE RECORDS. NOT this server: '/edit/' is on
> the read boundary's forbidden list, so IT CANNOT REACH THE EDITOR IN EITHER
> DIRECTION."

Both capitalised clauses are false at HEAD, and I verified each against code
rather than against prose:

1. "nothing here records [the previous value]" -- `writes.py:7724-7736` reads
   the prior value BEFORE anything is typed ("the ONE thing it owes him is the
   exact string it is about to overwrite, verbatim, while it still exists to
   be read"), and `writes.py:8010-8024` builds a `restore_block` carrying
   `previous_value`, `how_it_was_read` and `to_put_it_back` -- a
   copy-pasteable `linkedin_update_profile_field(field=..., value=...)` call.
2. "it cannot reach the editor in either direction" -- `/in/me/edit/intro/` is
   the one exact-URL entry in `readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS`, and
   `update_profile_field` is in `PERFORMABLE`. The restore is the same tool
   call, through the same two-call gate.

**Severity: highest of the four.** D1-D3 misstate a reason. D4 tells him a
recovery path does not exist when the code built one for him and the tool
hands him the exact call. The code's own comment beside the restore block
(`writes.py:7997-8000`) says what the field should say: "THIS SERVER RESTORES
NOTHING ON ITS OWN. What it owes him is the exact string it overwrote and the
exact call that puts it back." "This server will not restore for you" and
"this server cannot reach the editor to restore" are different claims, and the
spec prints the second.

**What would settle all four permanently:** one test asserting, for every spec,
that `reversible_by` and `residue` do not assert the non-performability of any
action currently in `PERFORMABLE`, and do not cite as forbidden any URL family
that appears in `_FORBIDDEN_SUBSTRING_EXEMPTIONS`. That test does not exist.
It has four demonstrable failing cases available today, which satisfies the
instrument-register rule that a check enters only if it has been shown failing.

---

# DELIVERABLE THREE -- WHAT A SAFE LIVE-FIRE WOULD COST

11 writes have never landed. `send_message` is excluded per the brief (measured
dead by name-addressing, `_audit/2026-09-03-typeahead-name-matching-is-dead.md`),
and Open To Work is not a tool at all. That leaves 10.

Consent is per-fire for ALL of them, without exception. Every write is
token-free-preview then token-carrying-perform, the grant is single-use
against a live read receipt (`writes.mint`, `writes.consume`), and the whole
door is behind `LINKEDIN_ENABLE_WRITES=1` per process, off by default. There
is no batching, no queue and no standing authorisation anywhere in this design.

## Group A -- safe test exists, concrete (5)

**1. `update_setting` -- the cheapest live-fire in the entire design.**
- Smallest test: `linkedin_update_setting` to move dark mode off its current
  reading of `Always off`, confirm the token, then call it again to set it
  back. Two fires, one round trip.
- What it does to his account: a display preference on his own session. The
  corpus, having ruled dark mode specifically: "The least of any write in this
  package. Dark mode is a per-account DISPLAY preference: no audience, no
  other member can observe it, broadcast nowhere, appears in no feed and no
  notification, and the same tool sets it back."
  (`_audit/2026-08-31-linkedin-perform.md:135-138`)
- Undoable by a tool: YES, the same tool.
- Consent: per-fire, twice.
- What it buys beyond itself: this is the only unfired write whose round trip
  settles a `reversibility_class`. The class is STILL-UNKNOWN today ONLY
  because "Nobody has performed a dark-mode change and read it back"
  (`:121-124`). One round trip converts a STILL-UNKNOWN to a measured verdict
  at essentially zero cost. **This should be fired first.**
- Caution worth carrying: two of the 33 addresses in this URL family are
  "Close and delete account" and "Hibernate account". Dark mode is admitted BY
  NAME, not by family, and it must stay that way.

**2. `unsave_job` -- the second cheapest, and it completes an existing pair.**
- Smallest test: job `4423880462` (the Sprinto posting) is saved right now and
  confirmed present. `linkedin_unsave_job(4423880462)`, confirm; then
  `linkedin_save_job(4423880462)`, confirm.
- What it does: removes and restores one bookmark on a private list. No
  audience, no notification, no third party.
- Undoable by a tool: YES, and both halves are already PROVEN or near it --
  the save half is the one write that has landed.
- Consent: per-fire, twice.
- What it buys: settles the one open residue on the save/unsave pair --
  "whether re-saving restores the original saved DATE, and therefore the
  list's order. Reversible in membership is not reversible in ordering."
  Read the `when` field before and after; the round trip answers it.
- Note: a preview of this exact call was already run and its output recorded
  (`_audit/2026-08-30-linkedin-undo.md:1634`), so the preview half is known
  good. Only the redemption is untested.

**3. `unfollow_company` -- safe, with the undo living outside this server.**
- Smallest test: pick a company from the rows `linkedin_followed_companies`
  actually renders, unfollow it, re-read the list and confirm the row left.
- What it does: silently reduces one Page's follower count by one. Not
  broadcast. Residue: "whether the company is told" is STILL-UNKNOWN and
  unmeasurable by reading; a Page admin sees a follower count, so the number
  moves.
- Undoable by a tool: NO -- he re-follows by hand from the company page or a
  posting. Trivial by hand, impossible to aim from here.
- Consent: per-fire, once.
- Pick a company he does not care about keeping, because the re-follow will
  not restore the original follow date and nothing distinguishes a restored
  follow from a fresh one.

**4. `react_to_item` -- the safe test is NOT a tool call, and must not be one.**
- Smallest test, verbatim from the corpus's own numbered procedure
  (`_audit/2026-08-31-linkedin-lift.md:491-505`): "In his own browser, not
  through this server ... React to TWO of his own posts ... His own posts, so
  no third party is notified by the act ... Press the reaction control itself,
  NOT the `Open reactions menu` control beside it ... Report which of these
  two things happened: did the press apply a reaction IMMEDIATELY, or did a
  picker open first? ... Leave both reactions in place until this server has
  re-read the page."
- Why TWO and not one: "a reaction on exactly one post may be BLANKED by the
  census before it can be read ... Reacting to two posts puts the label at
  count == 2, past the singleton trigger entirely" (`:509-520`). A one-post
  test would produce nothing readable. This is a trap in the instrument, not
  in LinkedIn.
- Why the TOOL must not be fired first: two unknowns compound. The ON label
  has never been observed, so there is no selector for the inverse -- an
  un-react cannot be aimed. AND it is unmeasured whether pressing the control
  applies a default reaction immediately or opens a picker; "NOBODY HAS
  MEASURED WHICH ONE THAT IS". Firing the tool would be an unaimable,
  un-undoable write of an unknown reaction type.
- Cost of the by-hand act: two reactions on his own content. No third party
  notified. Undoable by him in the same interface.
- Consent: not applicable -- it is his own act, not a tool call.

**5. `comment_on_item` -- safe ONLY in the own-item variant, and only after a free read.**
- Prerequisite, and it costs nothing: the corpus's own proposal -- "open the
  overflow menu on one of his OWN existing comments and read whether a delete
  exists" (`_audit/2026-08-30-linkedin-writes.md:113-115`). Deletability of a
  comment is currently UNMEASURED and permanently forbidden to this server; if
  no delete exists, this drops to Group C and should not be fired at all.
- Smallest test, if the delete exists: comment on one of HIS OWN posts. The
  audience is his own followers rather than a stranger's, and the notified
  author is himself.
- What it does: publishes attributable text under his own item.
- Undoable by a tool: NO. Deletion is in `PERMANENTLY_FORBIDDEN`; the undo is
  his, by hand, and only if the read above confirms one exists.
- Consent: per-fire, once.
- Known side effect even on refusal: "a comment draft may be left in the box,
  and whether that draft is local to this browser or saved to your account is
  UNMEASURED" -- 17 candidate draft-listing addresses are all refused by the
  read boundary. So even a REFUSED comment can leave residue he must clear by
  hand. He should be told this before the fire, not after.

## Group B -- safe test exists but carries a NAMED UNMEASURED cost (2)

**6. `follow_company`.**
- Smallest test: follow a company from a posting he would have been happy to
  follow anyway, then read Manage Pages and check the row appeared.
- What it does: "a follow can surface in his network's feed. The data is
  restorable and the impression is not."
- Undoable by a tool: NO, and this is the named unknown -- the undo cannot be
  aimed from here, and by hand it depends on the new row appearing among the
  20 of a stated 58 rows Manage Pages renders with no pagination control in
  five captures. Whether a fresh follow lands in those rendered rows is
  UNMEASURED. It is plausible that a recent follow sorts to the top; nothing
  in this repo has measured it.
- What would settle it: the test itself. Read Manage Pages immediately after
  the follow. If the row is there, the undo is reachable by hand and this
  action moves to Group A permanently.
- Consent: per-fire, once.

**7. `update_profile_field`.**
- Smallest test: change one low-stakes field in the intro editor -- the
  exempted `/in/me/edit/intro/` surface -- and use the `restore_block` the
  tool returns to put it straight back. The tool reads the prior value before
  typing and hands back the exact restoring call (defect D4 above notwithstanding).
- What it does: "his profile is what recruiters read, and they read it
  continuously -- it reports 29 profile views. An edit reverted an hour later
  was live for an hour."
- The named unmeasured cost: "LinkedIn also notifies a network about some
  profile changes, which this server has not measured and would not control."
  WHICH fields trigger that notification is unknown. A no-op write -- setting
  a field to the value it already holds -- would exercise aiming, mutation,
  verification and the restore block while changing nothing, but it is NOT
  provably free, because whether LinkedIn treats a same-value save as an edit
  worth broadcasting is exactly the thing nobody has measured.
- Undoable by a tool: YES -- the same tool with the returned previous value,
  through its own preview and its own token.
- Consent: per-fire, twice (change, then restore).
- Additional caution specific to this action: it shipped 2026-09-02 unable to
  act on three separate fatal blockers and was repaired the same day. Nothing
  has exercised the repair. The first fire is therefore also the first test of
  code that has never run correctly end to end.

## Group C -- no safe test; the smallest version is still the full act (3)

**8. `publish_post`.** There is no small post. Any post is a broadcast to
274-275 followers with measured past reach of 103-1,284 impressions, deletion
is UNMEASURED and permanently forbidden to this server, and it is "the one
artefact here a CURRENT EMPLOYER sees without looking." The only honest framing
is that the test cannot be made cheap, only made worthwhile -- he fires it on a
post he wanted to publish anyway. Undoable by a tool: NO. Consent: per-fire.

TWO pieces of FREE evidence should be taken before it is ever fired, and
neither costs a write:
- open one of his own existing posts' overflow menu by hand and read whether a
  delete item exists. That settles the reversibility class outright.
- **read the composer's audience control** -- see the finding at the top of
  this file. It is already inside a dialog the census enumerates, on an
  allowlisted address. Until it is read, he is being asked to confirm an
  irreversible broadcast without being told who receives it, and the smallest
  safe version of this action is not definable, because its blast radius is
  the one variable nobody has measured. **This read should precede any
  publish_post fire, not follow it.**

**9. `send_invitation`.** An invitation is a request to a real person and lands
as a notification with his name on it. Withdrawal is unmeasured, the Sent
manager is doubly unreachable, the outcome is DECLARED unverifiable in code, and
repetition has a consequence for the account itself -- "LinkedIn restricts
accounts whose invitations are frequently ignored." No variant spends less than
one stranger's attention. Fire it only on somebody he intended to invite.
Undoable by a tool: NO. Consent: per-fire.

**10. `apply_job`.** Irreversible in audience and certain to be so -- "An
application is READ BY A HUMAN at the employer, usually within a day."
Withdrawing is in `PERMANENTLY_FORBIDDEN`. It has been fired once and the gate
held, on a defect that is now fixed, so **the next fire would be the first real
submit this server has ever made.** That is worth stating plainly: the earlier
firing is not a rehearsal that de-risks the next one; it exercised a path that
could not pass. Fire it only on a job he wants. Undoable by a tool: NO.
Consent: per-fire.

## Ordering recommendation

Fire `update_setting` (dark mode) first and alone. It is the only unfired write
that is measurably costless, it converts a STILL-UNKNOWN reversibility class to
a measured one, and it exercises `perform`, `mint`, `consume`, the fill/select
mutation path and `_verify_after` end to end on a surface where a defect costs
nothing. Every later fire is safer for having run it. Then `unsave_job`, then
the by-hand `react_to_item` calibration, which costs nothing and unblocks a
whole action.

---

# DELIVERABLE FOUR -- THE REFUSAL INVENTORY

## A REFUSAL CENSUS IS NOT A CAPABILITY CENSUS

Read this before the tables. **You can grep a codebase for what it refuses. You
cannot grep it for what nobody considered.** Everything below is a refusal
somebody wrote down, which means somebody thought of it. The gap between what
LinkedIn offers and what this server delivers is made of two parts: the
refusals, which are enumerable, and the never-considered, which are not
enumerable from inside the repo at all -- they are visible only by walking
LinkedIn's own surface from the outside, which is what the four sibling agents
on this census are doing.

On a sibling server in this family, counting refusals undercounted the real gap
**EIGHT-FOLD**. This inventory is therefore the FLOOR of the gap, never its
size. Any number derived from it is a lower bound, and reporting it as a
measurement of the gap would repeat the exact error that memory records.

## 1. Permanently forbidden acts -- 9

From `writes.PERMANENTLY_FORBIDDEN`. These are refused at the design level, not
gated. Each carries its reason in the code; grounds are summarised here.

| # | act | ground |
|---|---|---|
| 1 | `repost_or_share` | a repost republishes SOMEBODY ELSE'S item to his network under his name. Menu never opened, so what a repost offers is unobserved. MEASUREMENT + not-asked-for |
| 2 | `endorse_or_recommend` | IMPOSSIBLE AS SPECIFIED, not unwanted. Zero endorse controls across 13 fixtures and 222 live controls; you cannot endorse yourself, so the only surface carrying the control is a third party's profile. MEASUREMENT |
| 3 | `deanonymise_a_viewer` | six of ten profile viewers chose anonymity. POLICY |
| 4 | `load_a_third_partys_profile_to_measure_a_control` | a profile view is an EMISSION; this server can read the receiving end of that signal 365 days back. The cost lands entirely on somebody who is not him. POLICY, measured |
| 5 | `delete_or_withdraw_anything` | destruction is not a write this design covers, at any confirm level. **FIVE specs cite this entry in `reversible_by`** -- shortening it would silently make five reversibility claims wrong at once |
| 6 | `mark_notifications_read` | clearing his unread badge destroys signal he has not seen, server-side on page serve so it cannot be confirmed first. Plus: 34 activatable controls on that surface, not one changes read state, no notification carries an id. POLICY + MEASUREMENT |
| 7 | `auto_accept_or_auto_reply` | a reply in his name that he did not read. POLICY |
| 8 | `any_loop_sweep_or_scheduled_write` | -- |
| 9 | `any_anti_detection_technique` | -- |

Note the shape of 2 and 6: both were POLICY refusals that were re-grounded on
MEASUREMENT when the operator dissolved the taste bucket. A refusal that
survives only on distaste is treated here as a defect. That is why this
inventory is short: the design converts refusals into measurements wherever it
can, and a converted one stops being a refusal.

## 2. Forbidden URL substrings -- 23

From `readonly._FORBIDDEN_URL_SUBSTRINGS`. Checked BEFORE the allowlist is
consulted, so a substring hit refuses even an otherwise-allowed address.

`/jobs/application`, `easyapply`, `easy-apply`, `/messaging/compose`,
`/invite`, `invitation`, `/connect`, `/follow`, `/unfollow`, `/endorse`,
`/post/`, `sharing/share`, `/settings/`, `opentowork`, `open-to-work`,
`/mypreferences/d/categories/`, `/psettings/`, `/close-accounts`,
`/hibernate-account`, `/edit/`, `action=`, `/delete`, `/withdraw`

## 3. Exemptions to that list -- 2

From `readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS`. EXACT urls, never patterns.

| url | substring it is exempted from |
|---|---|
| `https://www.linkedin.com/in/me/edit/intro/` | `/edit/` |
| `https://www.linkedin.com/messaging/compose/` | `/messaging/compose` |

Both exemptions buy READ access to a surface, not permission to act on it. The
second is the sharper case: `/messaging/compose` stays on the forbidden tuple
and the exemption admits exactly one address, so sending remains impossible by
address even though the composer can be looked at.

## 4. The read allowlist -- 22 patterns

`readonly._ALLOWED_URL_PATTERNS`. This is the positive half and it is the more
useful number for a gap analysis: **22 addressable LinkedIn surfaces, total.**
Anything not matching one of these 22 patterns cannot be loaded by this server
at all, and no refusal is written for it anywhere -- which is precisely the
"never considered" category the warning above is about.

`/messaging/`, `/messaging/thread/<id>`, `/analytics/profile-views/`,
`/me/profile-views/`, `/jobs-tracker/?stage=(saved|applied|draft)`,
`/jobs/search/`, `/jobs/view/<id>/`, `/in/me/`, `/in/<member>/`,
`/in/<member>/details/(skills|experience|education)/`, `/in/me/edit/intro/`,
`/mynetwork/network-manager/company/`, `/mypreferences/d/`,
`/mypreferences/d/dark-mode/`, `/feed/update/<urn>/`, `/preload/sharebox/`,
`/article/new/`, `/messaging/compose/`, `/premium/my-premium/`,
`/notifications/`, `/feed/`, `/login/`

### What those 22 patterns do not reach at all

Read off the list by inspection. None of these has a pattern, and none has a
refusal written for it anywhere either -- they are the "never considered"
category made concrete:

- **Groups** -- no `/groups/` pattern.
- **Events** -- no `/events/` pattern. Note the composer dialog carries a
  `Create an event` control that was measured and recorded
  (`_audit/2026-08-31-linkedin-perform.md:166`); the surface it would open is
  unreachable.
- **Newsletters** -- no `/newsletters/` pattern.
- **Hashtags and topic feeds** -- no `/feed/hashtag/` pattern.
- **Company Pages** -- no `/company/<slug>/` pattern. This one is easy to
  misread: `/mynetwork/network-manager/company/` is HIS followed-Pages
  manager, not a company page. It is also exactly the gap behind the
  follow/unfollow aiming failure -- a posting names its employer by slug, and
  the slug has no reachable address here.
- **Articles / Pulse** -- `/article/new/` is on the list, `/pulse/` is not.
  This server can reach the surface for writing an article and no surface for
  reading one.
- **Schools, Services, Learning, Sales Navigator, Recruiter** -- nothing.
- **The `/mynetwork/` tree** -- nothing except the network-manager company
  list. Reaching any of it consumes his pending-invitation badge, which is the
  measured reason.
- **Every search except job search.** `/jobs/search/` is the only search
  pattern. People search, company search and content search have no address
  here at all, which is a sharper limit than it first reads: several
  capabilities that look blocked by a missing write are actually blocked
  earlier, by having no way to FIND the target.

## 5. Sanctioned mutations -- 5

`readonly.SANCTIONED_MUTATIONS`. The whole of what this server can do to
LinkedIn. Widening this is a test failure, not a judgement call.

**This heading said "-- 4" and the table carried four rows until 2026-09-04.**
Corrected in place: `set_input_files` was sanctioned that day (the fifth row
below), and the answer to the open question section 5a used to ask is
recorded there now. All five rows are verified against the live module.

| path | function | kind |
|---|---|---|
| `linkedin_server/writes.py` | `perform` | `click` |
| `linkedin_server/writes.py` | `perform` | `fill` |
| `linkedin_server/writes.py` | `perform` | `select_option` |
| `linkedin_server/writes.py` | `perform` | `set_input_files` |
| `linkedin_server/dom.py` | `activate_messaging_filter` | `click` |

**RESOLVED 2026-09-04.** The question section 5a asks below was put to the
operator, and he opened it FULLY -- profile photo, post media and message
attachments, all three, not a narrower subset. `SANCTIONED_MUTATIONS`'s fifth
entry, `("linkedin_server/writes.py", "perform", "set_input_files")` in the
table above, is that answer. The guard the answer required is
`linkedin_server/uploads.py`: a declared root, a refusal on any symlink
anywhere in the path chain, a check that the target is a regular readable
file, and a sha256 digest read at preview time and re-read immediately
before the browser is handed the file.

**This does not ship the 16 rows `FILE-UPLOAD-UNSANCTIONED` names in
`_audit/2026-09-03-linkedin-gap-blockers.md:309,327-336` -- it UNBLOCKS
them.** `writes.UPLOAD_ACTIONS` ships EMPTY, verified live 2026-09-04: no
action has joined it, so no composer is wired to the new drain point yet.
Each of the 16 still needs its own composer surface measured and built
before it ships.

The original write-up below is left intact rather than deleted or rewritten,
because it is the record of the question being askable in the first place,
not a stale claim about the present.

## 5a. EVERY UPLOAD PATH IS CLOSED BY ONE OMISSION -- and it is an OPEN OPERATOR QUESTION, not an oversight

`set_input_files` is on `readonly._MUTATION_CALL_PATTERNS`
(`linkedin_server/readonly.py:680`) and appears in NO entry of
`SANCTIONED_MUTATIONS`. That single absence closes every upload this server
could ever do -- profile photo, post video, message attachment, resume
document. There is no separate refusal for any of them, and no spec.

**I was briefed that this had never been discussed anywhere. Checked, that is
half right and the half that is wrong changes what it is.** It is absent from
every audit document -- one mention in 51 files, and that one is a count of
zero (`_audit/_slice-apply-census.md:314`, `<input type="file">` (resume
upload) | **0**, on the apply modal). But the discussion exists, in a test,
with its reasoning written out: `tests/test_readonly.py:310-341`.

> "UPLOADING IS A DIFFERENT CAPABILITY FROM TYPING. A fill puts his words in a
> box; a file input puts a FILE from this machine into somebody else's inbox,
> chosen by a path string. Nothing in this package should be one edit away
> from that, **and the operator has never been asked about it.**"

The test does the whole job properly: it scans every module and asserts no
`set_input_files` call exists, it plants one to prove the pattern still bites
("A rule that cannot fire certifies nothing"), and it asserts separately that
the kind is not in `SANCTIONED_MUTATIONS`. It also names the controls it is
guarding, which have been MEASURED and are live on a surface this server now
loads: `Attach a file for your draft conversation` and `Attach an image for
your draft conversation`, both in `form#0`, beside the Send control.

So the correct classification is **a deliberate, reasoned, test-enforced
exclusion carrying an explicit unanswered operator question** -- not a gap
nobody weighed. That is a better finding than the one I was handed, and it is
also the reason a document-level grep finds nothing: the reasoning lives in a
test file, so it is invisible to anyone auditing the prose. Worth carrying as
a general point about this repo -- **several of its sharpest rulings are in
test docstrings rather than in audits**, and a census that reads only `_audit`
will score them as never-considered.

What it costs to resolve: one operator ruling. Nothing needs measuring first.

## 6. Outcomes DECLARED unverifiable -- 3

Actions where the code states, in a structured `Unverifiable` record, that
nothing this server may read can confirm the outcome, plus what he must do
himself.

| action | the surface that would confirm it | why it cannot |
|---|---|---|
| `publish_post` | his own activity rail | it "RENDERS INTERMITTENTLY" -- 233 controls on one reading, 67 on another, same session minutes apart. A scheduled-posts surface would fix it and does not exist for this server |
| `comment_on_item` | the item permalink | "NOTHING ON THAT PAGE COUNTS COMMENTS" -- 91 controls enumerated, the complete numeric inventory is four per-row zeros, one reactions count, two impressions links, a viewers link and five nav badges |
| `send_invitation` | Sent Invitations manager | its address contains `invitation` (forbidden, checked before the allowlist), and reaching it via `/mynetwork/` consumes his pending-invitation badge |

`send_message` is deliberately NOT on this list even though nothing can confirm
a send. Marking it unverifiable would short-circuit `_verify_after` to UNKNOWN
before the `not_performed_state` comparison feeds, deleting the NOT-SENT answer
while keeping the flag that says there is no answer. It reports NOT SENT and can
never report SENT.

## 7. Refusals that are structural rather than listed

Not in any constant, and therefore invisible to a grep of the refusal lists:

- **The write flag.** `LINKEDIN_ENABLE_WRITES` is off by default, per process.
  "a fresh clone of this repo cannot write to LinkedIn at all."
- **The two-call gate.** No write fires without a preview built from a LIVE
  read, a single-use token minted against that read receipt, and a second call
  redeeming it. `mint` refuses any action not in `PERFORMABLE`.
- **Direction refusal.** A write whose live-read direction is `unknown`
  refuses. This is why `save_job` refused for a period when the Saved-tab read
  was broken -- the gate refused on an instrument failure, not on policy.
- **The name-match refusal on `send_message`.** Exactly one committed recipient
  whose accessible name carries the operator's own needle, compared inside the
  page. A count of one with the wrong name refuses; a count of zero refuses.
  This is the refusal that turned out to be a MEASUREMENT: it fired, and what
  it measured killed the whole addressing approach.
- **`_verify_after` has no catch-all.** Adding an action to `PERFORMABLE`
  without a verification arm RAISES, after the click. Enforced statically by
  `tests/test_unverifiable_outcomes.py`.

## What this inventory does NOT tell you

It does not tell you the size of the gap. It tells you that 9 acts were
considered and forbidden, 23 URL substrings were considered and blocked, and
22 surfaces were considered and allowed. Every LinkedIn capability outside
those 54 decisions is unrepresented here in either direction -- not refused,
not allowed, not thought about. The sibling agents' outward census is the only
thing that can size it, and the honest arithmetic when their numbers arrive is
"outward count minus 22 allowed surfaces", never "9 refusals".

### AND THE OUTWARD NUMBER IS ITSELF A FLOOR

Passed to me by the team lead from the outward slices, and it constrains what
the joined figure may be called: **two LinkedIn Help TOPIC pages render `0
articles` for products that demonstrably exist** -- Events and LinkedIn Live.
An empty topic page is indistinguishable from a product with no features, and
it fails silently in the direction that shrinks the count.

So both halves of this census undercount, for different reasons and in the
same direction:

- the INWARD half undercounts because you cannot enumerate what nobody
  considered -- refusals are a floor, and on a sibling server that floor was
  **eight-fold** below the real gap;
- the OUTWARD half undercounts because an empty help topic reads as an absent
  product.

**The joined number is therefore a LOWER BOUND on the gap and must be reported
as one.** It is not a measurement of it, and any figure quoted from this
census without that qualifier is wrong in a way that will read as precision.
This paragraph exists so that the qualifier travels with the number instead of
being reconstructed later by whoever notices.

---

## UNKNOWNS, and what would settle each

| # | unknown | what would settle it |
|---|---|---|
| 1 | Has `linkedin_login` / `linkedin_login_browser` ever run? | one grep of the operator's shell history or one deliberate re-auth. A session exists, so something logged in; nothing records what |
| 2 | Does `linkedin_cdp_status` work? | one call. It reads a local CDP port and touches LinkedIn not at all -- this is a free measurement that has simply never been taken |
| 3 | Is `linkedin_compose_fields` fixed? | one live call. The fix is claimed at `_audit/2026-08-31-linkedin-perform.md:3427-3429`; the last LIVE reading said broken by containment. A read-only call on an already-allowed surface settles it |
| 4 | Does `linkedin_notifications` work? | one call, which COSTS his unread badge. Not free, and it is his to spend |
| 5 | Does `linkedin_open_messaging` work? | one call, which opens a real thread with a third party. Deliberately unpaid for four waves |
| 6 | Is the `linkedin_profile_editor_fields` false-refusal fixed? | it is non-deterministic and has fired twice. Repeated calls, counted -- a single success proves nothing about an intermittent gate |
| 7 | Does a re-save restore the original saved DATE? | the `unsave_job` round trip in Group A |
| 8 | Does a fresh follow appear in Manage Pages' rendered 20 of 58? | one read immediately after a follow |
| 9 | Can a post / comment / invitation / application / message be deleted or withdrawn? | UNMEASURED for all five, and unmeasurable from here -- all the undo addresses are forbidden. Only he can look |
| 10 | Does pressing the reaction control apply a default reaction or open a picker? | the by-hand two-post calibration in Group A item 4 |
| 11 | Does LinkedIn broadcast a profile-field edit to his network, and for which fields? | UNMEASURED. Nothing readable reports it. This is the one blocker on making `update_profile_field` a Group A action |
| 12 | What does an InMail cost him, and does he have credits? | UNMEASURED here by design -- five independent readings put `InMail` as a filter pill and no balance exists in 77 controls. He can settle it by looking at his own screen in seconds |
