# Orchestrator rulings of 2026-11-26 (16:45 to 18:40 IST), registered at integration 5

**Every ruling below is the orchestrator's.** It recorded them in its own merge
notes, which are kept outside this repository's tracked files, in the entries
headed from "2026-11-26 16:45 IST" through "2026-11-26 18:40 IST". Integration
5 registers each one here, in the register's format: a canonical id on a
`RULED:` line, the orchestrator's own words quoted, and the reopener. Where the
words name no reopener, this page says "none stated" rather than writing one.
Where the orchestrator gave a ruling no id, the id here is new. The integrator
adds no ruling of its own.

Nine rulings, in four groups: the navigation ceiling (section 1), two answers
for lane build-net2 (2), five answers on the session-12 plan (3), and his
account's one page-load budget (4). Section 5 lists the register entries that
were already there and that this pass touched. Section 6 lists what the same
entries hold that is not a ruling for this census. Which code and cells each
ruling settles is in this integration's record, section 4.

## 1. The navigation ceiling (16:45 and 17:12, lane infra26's item 2)

RULED: (orchestrator, 2026-11-26) NAVIGATION-CEILING-PER-TOOL-CALL -- at 16:45,
named NAVIGATION-CEILING-PER-CALL-WITH-ONE-DECLARED-FAN-OUT:
"NAVIGATION-CEILING-PER-CALL-WITH-ONE-DECLARED-FAN-OUT (supersedes
NAVIGATION-CEILING-MADE-TRUE's "raise to 3"): measured maximum 5
(linkedin_search_jobs, one page per place, MAX_LOCATIONS 5). The per-call
ceiling is 3 for every tool; linkedin_search_jobs alone declares a per-call
allowance equal to its place count before its first load, hard-capped at
MAX_LOCATIONS; an AST test pins that allowance's only call site, with a
planted-second-caller control. The people-reader loop bound is split into its
own constant (2). READ-CARDS-DELETION executed on an AST caller census (0
callers across 729 files)." And at 17:12, its final form:
"NAVIGATION-CEILING-PER-TOOL-CALL (infra26 item 2, FINAL form, 17:12;
supersedes the per-session note, because the live runner and probes load many
pages in one session): a fastmcp middleware on_call_tool arms a contextvar for
each tools/call; goto counts only while armed and refuses the 4th load; code
outside a tool call (runner, probes, direct test calls) is untouched;
linkedin_search_jobs alone declares a fan-out allowance capped at
MAX_LOCATIONS 5 (AST-pinned); a test proves every registered tool passes
through the middleware." REOPENER: none stated.

One ruling with two names: the 17:12 words are the final form of the 16:45
ones, so the 17:12 id is canonical and the 16:45 id is its alias. Lane
infra26's record calls the same design its option (C), and the orchestrator's
18:23 entry says that option is this ruling. The last sentence of the 16:45
words records an execution, not a new ruling: READ-CARDS-DELETION has been
registered since integration 4.

How much of it the merged head holds was measured clause by clause, in this
integration's record, section 4: all of it. The orchestrator's note of 19:31
added lane infra26's next head to this integration. That head carries the
last two tests: the one that every registered tool passes through the
middleware, and the planted-second-caller control.

THE LEAD'S FOUR ASKS. Lane infra26's record (section 2.4) lists four asks the
lead sent with this ruling: the planted-second-caller control; a test that
every registered tool goes through the middleware; a refusal that names its
tool; and the README's ruled sentence, with the login tools' real path
recorded as inside the ceiling. The first two are the ruling's own clauses.
All four are orders under it, built in that lane's next head, and none is
registered as a ruling of its own.

What it does to NAVIGATION-CEILING-MADE-TRUE (integration 4): that ruling's
"Raise it to the measured maximum, 3" rested on a measured maximum of 3. Lane
infra26 measured 5, reached by the job search's place fan-out alone. The
register now gives NAVIGATION-CEILING-MADE-TRUE the status AMENDED, its claim
names the amending ruling, and its original words are kept, as the register
keeps NO-IRREVERSIBLE-WRITE-IS-FIRED's. What it also said still stands under
the final form: three loads per tool call, enforced in `goto`, the fourth
refused, and the README's "One page load per tool call" put right.

The 17:12 words also name "the per-session note". That note is not in the
entries from 16:45 onward, so no text is quoted for it here. Lane infra26's
record (section 2.4) says what it was: the lead had accepted the per-session
counter of the lane's addendum, before the final form. The record's section
2.1 measured why a per-session scope would refuse the live runner's fourth
load.

## 2. Two answers for lane build-net2 (17:10)

RULED: (orchestrator, 2026-11-26) SEARCH-BOX-TYPEAHEAD-DISCLOSURE --
"SEARCH-BOX-TYPEAHEAD-DISCLOSURE (N 95): a sanctioned shape over
`[role=search] input[aria-autocomplete]` on an admitted page (measured: exactly
1 on 62 of 175 fixtures, 0 on 113, never 2; refuse at runtime on 0 or 2 or
more); nothing typed; only the recent-searches group read
(HIS-OWN-TEXT-AT-RUNTIME), people options never read; Escape with the listbox
verified gone." REOPENER: none stated.

RULED: (orchestrator, 2026-11-26) AD-HIDE-AIM-HELD -- "AD-HIDE-AIM-HELD (N 200):
stays GAP; no reader returns an ad urn without pressing ads he did not name;
reopener: a measured disclosure shape for the ad control-menu trigger. Option
(b), pressing un-named ads' menus to search, declined." REOPENER: "a measured
disclosure shape for the ad control-menu trigger".

Both answer lane build-net2, which merges in integration 6. They are
registered now because they are rulings, not code. Neither row's cells are
edited here: `N 95` and `N 200` are build-net2's rows, and an edit on both
sides would be a row moved by two lanes. AD-HIDE-AT-HIS-NAMED-AD (integration
4) still stands: a hide fires only at an ad he names. AD-HIDE-AIM-HELD holds
the build, because no reader returns an ad urn to him without pressing ads he
did not name. Its register entry gains a note that points here.

## 3. The session-12 plan (17:45 and 18:18, lane s12-prep's calls)

RULED: (orchestrator, 2026-11-26) FIFTH-SEARCH-TO-PEOPLE-LABELS --
"search-people-labels takes the 5th search slot (+7 rows; its All-filters
button is outside main)". REOPENER: none stated.

RULED: (orchestrator, 2026-11-26) MESSAGING-LINE-TO-SESSION-13-STANDBY -- at
17:45: "the inbox-search capture-first goes to session 13"; and at 18:18:
"ACCEPTED (its reading of item 2): the M M34 + M M28 line moves whole to "13,
standby" (one queue line, one receipt guard; alone in session 12 it would be 3
loads for 1 row). Session 12 therefore needs NO inbox read, so X-0 is
dropped." REOPENER: none stated.

RULED: (orchestrator, 2026-11-26) EDITOR-TYPEAHEAD-ONLY-ATTENDED -- the
orchestrator's answer to the lane's third call, as the plan's round-2 table
records it: "agreed; editor typeahead goes to a session he attends"; this
integration's brief gives it as "C-B1a stays out (editor typeahead only in a
session he attends)". The 17:45 and 18:18 entries do not carry it in words.
REOPENER: none stated.

The capture C-B1a is sanctioned by EDITOR-TYPEAHEAD-SANCTIONED (2026-11-25),
which moved `P A11`, `P A13` and `P A17` to it. This ruling adds only when it
runs: in a session he attends, and so not in session 12.

RULED: (orchestrator, 2026-11-26) NEWSLETTER-PICKED-FROM-HIS-SUBSCRIPTIONS --
"E14's newsletter is the lane's pick from his own subscriptions, a non-person
publisher only"; the plan's round-2 table records the answer as "the lane
picks one from his own subscriptions, published by LinkedIn or an
organisation, never a person". REOPENER: none stated.

RULED: (orchestrator, 2026-11-26) MSG-THREAD-FOOTER-TO-L2 -- "msg-thread-footer
goes to L2". REOPENER: none stated.

Lane s12-prep's round 2 applied all five, in the capture queue's session cells
and in line 32's plan cell, merged second in this integration. No row moves: a
session cell and a plan cell are not states. The plan's "13, standby" line is
the one queue line that carries `M M34` and `M M28` behind one receipt guard.

## 4. His account's one page-load budget (17:52)

RULED: (orchestrator, 2026-11-26) BUDGET-ONE-ACCOUNT-40 -- "Closes the 15:36
open question. His account gets ONE budget: 40 page loads per trailing 12 h,
shared by the live lane and the job pipeline. This is the stricter reading of
his 09-23 ruling. It is non-outward and reversible, so the orchestrator
decides it (decide-non-outward-calls-myself). Two separate budgets (up to 80
per 12 h) only on his word." And: "How it is applied: the live runner records
every load in the PINNED ledger before the load (the job-pipeline public
contract, budget.load_record / call_refusal; store from hooks/store_pin.json).
No copy, no second ledger. Session 12 READY check: the pinned ledger shows at
least 40 free (37 + 3 reserve) at GO, else the plan shrinks from the bottom of
the rank." And at 18:40, on lane s12-prep's reading of it: "Its reading 2 is
CONFIRMED: the harness's own session file (5-search cap, driver lock,
per-session 40) holds SESSION rules (his 09-23 per-session 40, D1's search
cap), not an account count. It can only refuse more than the store, so it is
not a second ledger and it stays." REOPENER: his word ("Two separate budgets
(up to 80 per 12 h) only on his word").

The 15:36 open question it closes asked whether his account has one budget,
shared by the live lane and the job pipeline, or two separate budgets of 40.
"His 09-23 ruling" is LIVE-BUDGET-40-LOADS, which keeps its status: a session
may still use up to 40 loads, and this ruling adds that those 40 are counted
per trailing 12 hours across the whole account, in one pinned ledger. Its
register entry gains a note that points here. Lane s12-prep's newest head
folds the ruling into the session-12 plan: the ledger hand-off and the READY
check are in the plan's section 6, and the budget is no longer among the
things the plan asks of him.

## 5. Register entries that were already there and that this pass touched

None of these is registered again. Each id, status and anchor is unchanged
unless stated.

| entry | what changed |
|---|---|
| NAVIGATION-CEILING-MADE-TRUE | status STANDING -> AMENDED; its claim opens with the amendment and keeps its original words; its note says what was built (section 1) |
| READ-CARDS-DELETION | note: executed by lane infra26 on an AST caller census, merged in this integration |
| PEOPLE-GATE-COUNTS-NAME-SLOTS | note: built by lane infra26 as the tracked people gate (its rule N1), merged in this integration; the live lane wires it |
| AD-HIDE-AT-HIS-NAMED-AD | note: its aim is held by AD-HIDE-AIM-HELD |
| LIVE-BUDGET-40-LOADS | note: counted per account per trailing 12 hours by BUDGET-ONE-ACCOUNT-40 |

## 6. What the same entries hold that is not registered here

- ORDERS, NOT RULINGS: the 17:45 "PEOPLE-GATE v2 module path is named in the
  runner hand-off", carried out in the plan's section 6; the 18:18 INTEGRATION
  5 SPLIT, which decides what this integration merges; the 18:23 launch of
  this integration and its hand-made worktree; the 18:40 entry's orders to
  merge b16cb67 (never b93cebd) and lane infra26's next head (on top of
  a053645); and the lead's four asks under the ceiling ruling (section 1).
- FOR INTEGRATION 6: the 19:25 entry's rulings for lane build-jobs2, which
  that entry marks to be registered there.
- ASKS OF THE OPERATOR: the 17:45 list of what session 12 needs from him. At
  18:18, X-0 is dropped and the budget answer is BUDGET-ONE-ACCOUNT-40. What is
  left is in the plan's section 7.
- MEASUREMENTS AND STATE: the 17:52 reading of the five wave-3 lanes, and the
  note that the readers-prof lane follows session 12's captures; the 18:18
  totals of the plan's packer and its budget-timing measurement; the 18:23
  summary of lane infra26's four items; the 18:22 fix to the lanes' standing
  rules, which is gitignored state.
- THE PER-SESSION NOTE that the 17:12 words name, which is not in these
  entries (section 1).
