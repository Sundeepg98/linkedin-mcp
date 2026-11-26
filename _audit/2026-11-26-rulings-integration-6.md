# Orchestrator rulings of 2026-11-26 (19:25 to 23:05 IST), registered at integration 6

**Every ruling below is the orchestrator's.** It recorded them in its own merge
notes, which are kept outside this repository's tracked files, in the entries
headed from "2026-11-26 19:25 IST" through "2026-11-26 23:10 IST". Integration
6 registers each one here, in the register's format: a canonical id on a
`RULED:` line, the orchestrator's own words quoted, and the reopener. Where the
words name no reopener, this page says "none stated" rather than writing one.
Where the orchestrator gave a ruling no id, the id here is new, written to
match the question a reader would bring. The integrator adds no ruling of its
own.

Fifteen rulings, in six groups: lane build-jobs2's five (section 1), two for
the live lane (2), lane build-net2's one (3), one in session 12 (4), lane
build-msg2's five (5), and one on a failed re-proof (6). Section 7 lists the
register entries that were already there and that this pass touched; section
8 lists what the same entries hold that is not a ruling for this census. Which
cells each ruling settles is in this integration's record,
`_audit/2026-11-26-integration-6.md`, section 4.

## 1. Lane build-jobs2's five (19:25)

RULED: (orchestrator, 2026-11-26) J-37-SPLITS -- "J-37-SPLITS
(COMPOUND-ROW-SPLITS-ONLY-ON-STATE, the J 114/J 169 precedent): the list half
stays J 37 (COVERED-UNFIRED); the edit half gets a new id (GAP, next BUILD)."
REOPENER: none stated.

The question is the lane-K ledger's `Q-J37-SPLITS`, which is this ruling's
alias. Lane build-jobs2's round 2 applied it: `J 37` keeps "List all alerts"
on `linkedin_job_alerts`, and `J 170`, "Manage all alerts", entered at GAP,
next step BUILD on session 11's capture of the alert manager. The population
moved 775 -> 776 on that lane's branch.

RULED: (orchestrator, 2026-11-26) RECEIPT-RISK-IS-HIS -- "RECEIPT-RISK-IS-HIS
(J 76, P M7): the save switch's live round trip may delete his stored resumes
and answers, which is unmeasured. Never scheduled without his explicit order
naming the direction." REOPENER: his explicit order naming the direction.

It answers the lane's question 2. The rows stay COVERED-UNFIRED, and the save
switch's preview prints the warning and reads his stored resumes before the
press and after the restore.

RULED: (orchestrator, 2026-11-26) WRITE-DOOR-EXCUSAL-ON-THE-SPEC -- "The
WriteSpec excusal is ACCEPTED, with readonly.py untouched." REOPENER: none
stated.

The orchestrator gave it no id. It answers the lane's question 3: the write
door reads only the spec's own exemptions, so the excusal for his application
settings page is keyed by the address on the spec
(`WriteSpec.exempt_substrings_at`), and `readonly.py` and its boundary freeze
are unchanged.

RULED: (orchestrator, 2026-11-26) J-160-RAW-ONLY-IF-THE-PEOPLE-GATE-KEEPS-IT --
"J 160's capture keeps a raw only if PEOPLE-GATE v2 keeps it." REOPENER: none
stated.

The orchestrator gave it no id. It answers the lane's question 4. Lane
build-jobs2's round 2 wrote it into the save cell of the `career-insights`
line in `_audit/_census/capture-queue-reads.tsv`. `J 160` stays GAP.

RULED: (orchestrator, 2026-11-26) READER-LEAK-WRITER-UNDER-THE-PACE-QUEUED --
"The reader-leak baseline writer under the 20 s pace: QUEUED for the guard's
next owner." REOPENER: none stated.

The orchestrator gave it no id. It answers the lane's question 5: run outside
pytest, the reader-leak baseline's writer drives four `server` helpers into a
5 s timeout under the ruled 20 s pace, and regenerates truly only with
`LINKEDIN_MIN_INTERVAL_S=0`. The fix belongs to whichever lane next owns that
guard. Nothing is built here.

## 2. The live lane (20:36, answering integration 5's two questions)

RULED: (orchestrator, 2026-11-26) LIVE-FLAG-DENIES-LINKEDIN-MCP -- at 20:36:
"Q1, LIVE-FLAG-DENIES-LINKEDIN-MCP (the 15:36 rule): while the flag is up, the
user-scope guard denies every non-exempt LinkedIn MCP tool; the live lane
drives LinkedIn through its runner only." The 15:36 rule it names: "RULE FOR
THE NEXT LIVE-LANE BRIEF (session 12): while _state/LIVE_SESSION_ON is up, the
user-scope guard DENIES every non-exempt LinkedIn MCP tool in every session;
only server_info, cdp_status, logout, page_plugin_snippet pass. The live lane
drives LinkedIn through its RUNNER only, as session 11 did (measured 15:35: 0
LinkedIn MCP tool calls in its transcript, 0 mcp__ references in
runner_s11.py). Plus PEOPLE-GATE v2 before any load (the 14:05 entry)."
REOPENER: none stated.

Integration 5's record (section 9) read the 15:36 rule as an order to the
live lane's brief and asked whether to register it; the orchestrator's 20:36
answer registers it here. The guard it names is the job pipeline's, installed
at user scope outside this repository. Lane live-s12 drove session 12 through
its runner, recording every load in the pinned account ledger first.

RULED: (orchestrator, 2026-11-26) PLAN-PEOPLE-GATE-LINES-ARE-THE-LIVE-LINES --
"Q2: plan section 6's people-gate lines are the only ones the live lane
applies (every page judged); infra26's section 4.5 is the generic hand-off,
which the plan supersedes for session 12." REOPENER: none stated.

The orchestrator gave it no id. Integration 5's record (section 9) found two
hand-offs for the runner's people-gate lines on master: lane infra26's
one-line form, which under `and` judges only the pages whose raw may be kept,
and the session-12 plan's section 6, which judges every page first. The plan's
lines are the ones the live lane applies.

## 3. Lane build-net2's one (about 20:00; recorded 20:36, 21:46 and 21:55)

RULED: (orchestrator, 2026-11-26) ONE-ENTRY-IS-ONE-SHAPE -- at 20:36:
"build-net2's N 95 shape (two triples, one drain function)"; at 21:46:
"SANCTIONED_MUTATIONS 16 -> 18 (the two triples ruled at ~20:00)"; and at
21:55, naming the lane's record of it: "ONE ENTRY IS ONE SHAPE, NOT ONE LINE".
Lane build-net2's record (section 4) writes the orchestrator's acceptance in
full: "the ruling's "one entry" meant one sanctioned SHAPE -- the one
`[role=search] input[aria-autocomplete]` -- not one triple; one drain
function, exactly two call sites, the click that opens as load 28 measured it
and the Escape that closes it, verified gone; every other key and every fill
refused; no Shift-key or focus open, since nothing measured one." REOPENER:
none stated.

The ~20:00 words themselves are not in the merge-notes entries; the ruling is
quoted from the three entries that record it and from the lane's record, and
this page says so. It reads SEARCH-BOX-TYPEAHEAD-DISCLOSURE's "one
sanctioned-mutation entry" (integration 5): `readonly.SANCTIONED_MUTATIONS`
keys a call by `(path, function, kind)`, so the one shape takes two lines, the
click and the Escape, 16 -> 18 on that lane's branch.

## 4. Session 12 (22:02)

RULED: (orchestrator, 2026-11-26) NEWSLETTER-PUBLISHER-UNPROVEN -- "RULED
NEWSLETTER-PUBLISHER-UNPROVEN: E12 is SKIPPED, its load goes to standby. Of 5
kept readings, 3 are person-published and 2 show no publisher; loading an
unproven one would gamble his "never a person" rule. Reopener: he names a
newsletter (L2), or a reading proves an organisation or LinkedIn publisher."
REOPENER: "he names a newsletter (L2), or a reading proves an organisation or
LinkedIn publisher".

It holds NEWSLETTER-PICKED-FROM-HIS-SUBSCRIPTIONS (integration 5) to its own
"never a person": no kept reading proved a non-person publisher, so session 12
loaded no newsletter page. Session 12 skipped E12 (its record, "The GO, and
the start").

## 5. Lane build-msg2's five (22:33)

Lane build-msg2's record (section 10) quotes the orchestrator's fuller answers
to its section 6; each is quoted here from the merge notes first, then from
that record.

RULED: (orchestrator, 2026-11-26) M-M28-SPLITS -- "M-M28-SPLITS: view half
COVERED-UNFIRED; the restore half a new id at GAP (CAPTURE)." As the lane's
record quotes it: "the view half stays M M28 and moves to COVERED-UNFIRED via
linkedin_archived_conversations. The restore half is a NEW id at GAP, next
step CAPTURE (the restore control has never been captured)." REOPENER: none
stated.

Lane build-msg2's round 2 applied it under COMPOUND-ROW-SPLITS-ONLY-ON-STATE:
`M M28` reads "View archived conversations", and `M M54`, "Restore an
archived conversation to the inbox", entered at GAP with its next step on the
messaging-guarded capture.

RULED: (orchestrator, 2026-11-26) MEDIA-POST-SAME-REFUSAL -- "MEDIA-POST-SAME-REFUSAL:
the audience is unread, and there is no upload after a press. M C3/C4/C6/C7
stay GAP." As the lane's record quotes it: "linkedin_publish_post's refusal
... applies to a media post on the same composer, because the audience is
still unread. perform's drain rule 'AND IT IS BEFORE ANY CLICK' stands, so
there is NO upload after a press. M C3 and M C4 (with M C6 and M C7) stay GAP
and cite this ruling." REOPENER: an audience the server can read (this
integration's brief, 23:10: "the reopener is an audience the server can
read").

The question is the lane's section 6, question 2. The lane-K ledger carries
it from this integration as `Q-MEDIA-POST-AUDIENCE`, the ruling's alias, so
the two rows' next step can cite it (section 7).

RULED: (orchestrator, 2026-11-26) GROUP-POST-AUDIENCE-FROM-ITS-TRIGGER --
"GROUP-POST-AUDIENCE-FROM-ITS-TRIGGER: "Start a public post" is accepted,
verbatim in the preview, on his explicit order for a named group." As the
lane's record quotes it: "the exact trigger text 'Start a public post' is
ACCEPTED as M C64's audience reading, on two conditions. The preview shows
that label VERBATIM to him before the grant, and the act fires only on his
explicit order for a group he names (OUTWARD-ACTS-NEED-THE-OPERATOR)."
REOPENER: none stated.

`M C64` is COVERED-UNFIRED on `linkedin_publish_group_post`, receipt-only. The
first condition is held by `tests/test_group_composer.py`, which requires the
preview to carry the trigger's words before any grant; the second by the
row's bucket-1 hold, OPERATOR-NAMES-THE-TARGET.

RULED: (orchestrator, 2026-11-26) M-M31-READ-BY-COMPOSITION -- "M M31 read
half ratified under CALLER-COMPOSITION-UNDER-D6 (a named conversation; opening
marks it read)." As the lane's record quotes it: "It opens only a
conversation he names, and its record says that opening marks it read (the
read's cost)." REOPENER: none stated.

The orchestrator gave it no id. `M M31`'s read half is the composition
`linkedin_open_thread(thread_id, allow_unread=True)` under
CALLER-COMPOSITION-UNDER-D6: opening the conversation marks it read, which is
the act and its cost.

RULED: (orchestrator, 2026-11-26) READER-INVENTORY-BY-QUALIFIED-NAME --
"READER-INVENTORY-BY-QUALIFIED-NAME (the guard gap; red first)." As the lane's
record quotes it: the inventory guard "must match module.function, not the
bare name. Build it red first in this round: a planted same-named reader in
another module must be caught." REOPENER: none stated.

Built by lane build-msg2's round 2 in
`tests/test_readers_outside_dom_are_a_pinned_inventory.py`, red first (2 of
12 failed on the bare-name detector); the qualified match found
`analytics_hub.read_card`, which the bare name had hidden, now pinned with its
reason.

## 6. A failed re-proof (23:05)

RULED: (orchestrator, 2026-11-26) FAILED-REPROOF-DEMOTES -- "RULING
FAILED-REPROOF-DEMOTES (orchestrator, 23:05), for M C41: a COVERED-PROVEN row
whose scheduled live re-proof FAILS moves to COVERED-UNFIRED, citing the
failed load, until a fire re-proves it. This is the shape of
Q-RETIRED-ROUTE-ROWS, and a census must not keep a PROVEN it cannot
reproduce. Integration 6 applies it." REOPENER: a fire that re-proves the row
("until a fire re-proves it").

Integration 6 applies it to `M C41`, whose scheduled re-proof was session 12's
E1 (loads 1 and 2, refused `self_assertion_unreadable`).

## 7. Register entries that were already there and that this pass touched

None of these is registered again. Each id, status and anchor is unchanged;
only the note moved, because each note would otherwise be untrue at this
head.

| entry | what changed in its note |
|---|---|
| RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE | it said no capture had been taken; its trigger was met in session 12 (load 3), and integration 6 applied it to the 22 rows of search26's report, section 4.5 |
| SEARCH-BOX-TYPEAHEAD-DISCLOSURE | "registered before that lane merges": built by lane build-net2 and merged here; its one entry is one shape (ONE-ENTRY-IS-ONE-SHAPE) |
| AD-HIDE-AIM-HELD | "registered before that lane merges": `N 200` held at GAP by lane build-net2, merged here |
| NEWSLETTER-PICKED-FROM-HIS-SUBSCRIPTIONS | held in session 12 by NEWSLETTER-PUBLISHER-UNPROVEN |
| CONVERSATION-MENU-PREVIEW-PRESS | built by lane build-msg2 (`M M26`, `M M27`, `M M29`, `M M31`), merged here |
| SCHEDULED-LIST-AS-A-SHIPPED-READ | built by lane build-msg2 (`M C14`), merged here |
| APPLICATION-SETTINGS-WRITE | it said not built; built by lane build-jobs2 (`J 74`, `J 76`, `P M7`, `P M8`), merged here |

BUDGET-ONE-ACCOUNT-40 is registered (integration 5) and is not registered
again. Session 12 applied it: every one of its 39 loads was recorded in the
pinned account ledger before it was made, and the job pipeline made none.

THE LANE-K LEDGER gains one question from this pass, `Q-MEDIA-POST-AUDIENCE`,
in its section 7, so `M C3` and `M C4` can cite their holding ruling the way
`N 200` cites `Q-AD-HIDE-AIM`: the next-step checker resolves a RULING step
only to a `### Q-...` heading there.

## 8. What the same entries hold that is not registered here

- ORDERS, NOT RULINGS: the 19:25 and 22:33 "Round 2 ordered" lines, carried
  out by the lanes; the 20:36 INTEGRATION 6 QUEUE and the 22:33 INTEGRATION 6
  SET; the 20:52 and 22:02 orders to the live lane (its Phase A, the GO and
  its re-issue); the 23:10 launch of this integration; the 23:22 note on
  disk naming the head to merge for lane live-s12.
- SELF-LOADER-WAITS-FOR-THE-REWRITE (22:21), a build the orchestrator
  QUEUED for the next wave: `server._goto_self_profile_asserted` and
  `press.self_landing` to wait, bounded, for LinkedIn's client-side rewrite of
  `/in/me/`, red first on a fake page whose address changes after a delay. It
  is a specification of work, like the round-2 orders, and it answers no
  question; this integration cites it in `M C41`'s cell as the fix queued,
  and does not register it.
- SESSION-12 CALLS ON PLAN ITEMS, each executed in session 12 and binding no
  later session: line 24 (his Open-to-Work editor) replacing E37, his own
  20:56 answer applying OPEN-TO-WORK-EDITOR-ATTENDED-ONLY; "E18 is accepted
  on page structure; E19 is skeleton-only"; the plan's section 5 skips after
  E1's refusal.
- THE 23:10 CORRECTION, which says RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE's
  registered text binds (GAP, not COVERED-UNFIRED): an application of a
  registered ruling, not a new one. Integration 6 applied the registered text.
- LESSONS AND MEASUREMENTS: the 19:25 fleet-quiet diagnosis, the 20:36
  message-loss measurement and its rule that a running integrator's orders
  go on disk first, the 22:14 lesson that a GO names its exact pins, the
  22:02 memory fold, session 12's findings and its runner defect for the
  session-13 owner.
