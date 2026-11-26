# Orchestrator rulings of 2026-11-26 (10:10 to 14:27 IST), registered at integration 4

**Every ruling below is the orchestrator's.** It recorded them in its own merge
notes, which are kept outside this repository's tracked files, in the entries
headed from "2026-11-26 10:10 IST" through "2026-11-26 14:27 IST". One of them,
section 3, rests on the operator's own words of 11:39 and on the orchestrator's
lead ruling L1 of 12:22, which is kept in a design record outside this
repository. Integration 4 (`_audit/2026-11-26-integration-4.md`) registers each
one here, in the register's format: a canonical id on a `RULED:` line, the
orchestrator's own words quoted, and the reopener. Where the words name no
reopener, this page says "none stated" rather than writing one. Where the
orchestrator named a ruling only by the question it answers, the id here is
new and the question's id is kept as its alias. The integrator adds no ruling
of its own.

Twenty-one rulings, in eight groups: his own profile's self-profile spelling
(section 1), the job search's AI fallback (2), job applications under a policy
he ratified (3), and the answers to six lanes' questions: readers-jobs26 (4),
readers-net26 (5), selfprofile26 (6), readers-msg26 (7) and pace20 (8). What
the same entries hold that is not a ruling for this census is in section 9.
Which rows each ruling moved, and why the others moved none, is in that
record's section 4.

## 1. His own profile's self-profile spelling (10:10)

RULED: (orchestrator, 2026-11-26) SELF-PROFILE-QUERY-VARIANT-ADMITTED --
"SELF-PROFILE-QUERY-VARIANT-ADMITTED: his OWN profile address carrying exactly
one query parameter, isSelfProfile=true, is a READ address in its own right.
Anchors: (1) his own profile path only (/in/me/, or his own slug resolved at
runtime from his session, never stored in a tracked file); (2)
isSelfProfile=true is the only parameter; any other parameter or value is
refused; (3) the server composes the address from this ruling, never from a
page's href (PAGE-MAY-VETO-NEVER-SUPPLY stands); (4) the landing must prove
his own profile, or the read refuses. Admitted red-first in readonly.py, with a
control that the same query on another member's profile is refused. P D25: the
capture loads the composed address and reads the Add-section surface that
renders, no press. P A25: the capture loads the contact-info overlay by its own
address (admitted under the same self-only anchors if not admitted already), no
press, labels only, no contact value saved or printed." REOPENER: "a capture
showing the variant draws nothing the bare profile does not."

It answers the lane-K ledger's `Q-SELF-PROFILE-QUERY-VARIANT`. Lane admit5-26
built the admission, red first, in the `/in/me/` form only, and moved both
rows' next step to the capture of the composed address. Anchor (4) is the
self-profile recognition that lane selfprofile26 rebuilt on LinkedIn's own
edit links, merged in the same integration.

## 2. The job search's AI fallback (11:05, lane search-fix26's three questions)

RULED: (orchestrator, 2026-11-26) AI-EASY-APPLY-POST-FILTER -- "the AI fallback
MAY honour easy_apply as a LOCAL post-filter on each card's own measured Easy
Apply mark, from the one load, no re-query; the output names filter_mode
local_post_filter_on_card_mark with counts before and after; never presented
as LinkedIn's filter. The AI page's own toggle stays REFUSED until a capture
measures its effect." REOPENER: for the page's own toggle, "a capture measures
its effect".

RULED: (orchestrator, 2026-11-26) NO-RESULTS-STATE-CAPTURES -- "capture each
route's no-results state (C-SRCH-0a classic, C-SRCH-0b AI; 1 load + 1 search
each, a keyword chosen to draw nothing, naming no person). Until then every
zero refuses on both routes." REOPENER: the two captures, each route's drawn
no-results state.

RULED: (orchestrator, 2026-11-26) READ-CARDS-DELETION -- "after integration 4,
the first lane touching server.py deletes server._read_cards if an AST caller
census shows no caller." REOPENER: none stated.

The first two are built: the local post-filter by lane search-fix26's second
round, and the two capture lines in the capture queue. The third is queued for
the first build lane after this integration.

## 3. Job applications under a policy he ratified (12:22)

The operator wrote "yes, automate max" at 11:39 on 2026-11-26. The
orchestrator's lead ruling L1 of 12:22 reads: "L1 AMENDED for job applications
only. "Automate max" (operator, 11:39) plus his ratification of a policy at his
own console names the targets by rule. That satisfies OPERATOR-NAMES-THE-TARGET
for job applications made under a ratified policy. APPLY-FLOW-IS-THE-APPLICATION
still holds: opening the flow IS applying, and here it happens under the
ratified policy. Every other outward act is unchanged (messages, connects,
posts, InMail)."

RULED: (orchestrator, 2026-11-26) RATIFIED-POLICY-NAMES-APPLICATION-TARGETS --
"For THIS census: L1 amends OPERATOR-NAMES-THE-TARGET for JOB APPLICATIONS
under a ratified policy only; register it in integration 4 alongside the other
new rulings." REOPENER: none stated.

So for a job application, and for nothing else, a policy he ratified at his
own console names the target by rule, and that satisfies the
operator-names-the-target condition. A message, a connection request, a post or
an InMail still fires only at a target he names himself.

## 4. Lane readers-jobs26's three questions (12:50)

RULED: (orchestrator, 2026-11-26) J-114-SPLITS -- "split under
COMPOUND-ROW-SPLITS-ONLY-ON-STATE on the J 110 -> J 168 precedent; the unbuilt
facets take the next free numeric id, GAP, next C-RJ26-1." REOPENER: none
stated.

RULED: (orchestrator, 2026-11-26) HIS-OWN-TEXT-AT-RUNTIME -- "a tool may return
text he authored or uploaded on his own account (his resume file names, his
job-alert keywords) to his own session at runtime; fixtures synthetic; never in
tracked files, tests, CI or console logs; a narrow door in the tool-envelope
ratchet, with a control that third-party text stays refused." REOPENER: none
stated.

RULED: (orchestrator, 2026-11-26) APPLICATION-SETTINGS-WRITE -- "admitted in
principle (his own switches, a reversible on/off pair behind the grant, proven
by a live round trip); BUILD deferred to the first build lane after
integration 4 (the write door's excusal lives in readonly.py, changed by
admit5-26's held branch)." REOPENER: none stated.

Lane readers-jobs26's second round applied the first two: `J 114` keeps its
built facet, and the three unbuilt facets entered as `J 169`; the tool-envelope
guard gained the one door, `ADMITTED_OWN_TEXT`, with its control. The third is
queued for the first build lane after this integration.

## 5. Lane readers-net26's section 9 (13:31)

RULED: (orchestrator, 2026-11-26) UNFOLLOWED-RAW-DELETED -- "the kept raw
unfollowed.html (44 members' names) is deleted by the orchestrator, both copies
(the live-s11 lane state and the preserved set); skeletons kept." REOPENER:
none stated.

RULED: (orchestrator, 2026-11-26) PEOPLE-GATE-COUNTS-NAME-SLOTS -- "the people
gate's next version counts name slots as well as profile links (queued for the
next live-lane owner)." REOPENER: none stated.

RULED: (orchestrator, 2026-11-26) RECEIVED-BADGE-IS-THE-READS-COST --
"RECEIVED-BADGE-IS-THE-READ'S-COST: reading his received invitations clears the
pending badge (linkedin_notifications precedent); recorded as the passive cost;
the docstring states it; the sent tab and following list keep withholding on a
badge drop." REOPENER: none stated.

RULED: (orchestrator, 2026-11-26) REINVITE-BY-CALLER-COMPOSITION --
"Q-REINVITE-COMPOSITION (N 6): discharged by CALLER-COMPOSITION-UNDER-D6
(sent_invitations + connect_from_profile), COVERED-UNFIRED; LinkedIn's
re-invite cooldown honoured because Connect is pressed only where drawn;
Connect stays outward, at named targets only." REOPENER: none stated.

RULED: (orchestrator, 2026-11-26) REFOLLOW-FROM-HIS-NAMED-PROFILE --
"Q-REFOLLOW-AIM (N 40, M C52): the re-follow is built from the member's own
profile he names by link (N 34's route); the unfollowed list is a read and
veto only, never a target source." REOPENER: none stated.

RULED: (orchestrator, 2026-11-26) AD-HIDE-AT-HIS-NAMED-AD -- "Q-AD-HIDE-TARGET
(N 200): YES under HIS-OWN-CURATION-NOT-OUTWARD for an ad he names (an urn a
reader returned to him that he hands back); the tool never picks an ad; undo
captured on the first supervised fire; Report ad stays outward." REOPENER: none
stated.

RULED: (orchestrator, 2026-11-26) AD-DATA-GRAIN -- "AD-DATA-GRAIN (P P10-P
P14): keep the five grouped rows; split per setting only when pages are
admitted and states diverge (COMPOUND-ROW-SPLITS-ONLY-ON-STATE)." REOPENER: a
row's pages admitted and its settings' states diverging.

The orchestrator spelled the third id with an apostrophe,
`RECEIVED-BADGE-IS-THE-READ'S-COST`, and the package's code and the network
slice cite it so. A register id is a closed alphabet, so the id here drops the
apostrophe, and that spelling is kept as its alias. Lane readers-net26's second
round applied the four that move rows or code: the received tab's docstring
and its bracket, `N 6` to COVERED-UNFIRED by composition, `N 40` and `M C52`
pointed at `N 34`'s route, and `N 200` at a build behind the grant.

## 6. The press gate's own read (13:40, lane selfprofile26)

RULED: (orchestrator, 2026-11-26) PRESS-GATE-MAY-READ-TO-DECIDE-SELF -- "where
the URL alone no longer decides self vs other (a member root with no marker),
the press gate may make its OWN read-only count of edit links before any press;
a caller-supplied reading stays refused ("a basis a caller can assert is a
basis a caller can invent"). Where the URL decides, the gate still refuses
before touching the page. test_a_refused_press_never_touches_the_page's one
narrowed row stands under this ruling." REOPENER: none stated.

It answers the first question of lane selfprofile26's record, section 6, and
the narrowed test row is that lane's.

## 7. Lane readers-msg26's four questions (14:10)

RULED: (orchestrator, 2026-11-26) MESSAGE-SEARCH-CAPTURE-FIRST --
"Q-MESSAGE-SEARCH-TYPING (M M34): CAPTURE FIRST whether the inbox search lands
on an address of its own; if it does, D1-SEARCH-AS-READS (no typing). Only if
not: a new sanctioned shape SEARCH-BOX-TYPING, anchored: role search/searchbox
input with its own label (never a contenteditable composer); Enter within that
input only; read; clear; verify the list restored; refuse if focus reaches a
composer or a send control enables." REOPENER: none stated.

RULED: (orchestrator, 2026-11-26) SCHEDULED-LIST-AS-A-SHIPPED-READ --
"Q-SCHEDULED-LIST-PRESS (M C14): YES as a shipped read: the post composer
opened EMPTY, Schedule post, then View all scheduled posts; read the list (zero
only on a drawn empty headline); close with nothing typed or scheduled; verify
no draft; STOP on any autosave sign." REOPENER: none stated.

RULED: (orchestrator, 2026-11-26) ARTICLE-COMPOSER-ONE-CAPTURE --
"Q-ARTICLE-COMPOSER-DISCLOSURES (M C44, C46, C50, C78, C81, P L3): YES as ONE
CAPTURE, nothing typed: dismiss onboarding, then the author toggle, Manage, the
embed control and Next, each read and closed; never Publish or Schedule; a
draft's appearance recorded (next step: delete it, his own, reversible);
STOP-ALL on any publishing control." REOPENER: none stated.

RULED: (orchestrator, 2026-11-26) CONVERSATION-MENU-PREVIEW-PRESS --
"Q-CONVERSATION-MENU-STATE (M M26, M27, M29, M31): YES, a sanctioned PREVIEW
press (the similar-jobs trial-press precedent): open that one options menu
bound to the named conversation, read the item's word, press nothing inside,
close on Escape, verify closed; the confirmed press re-reads and refuses on the
inverse. DELETE CONVERSATION (no inverse): RECEIPT-ONLY behind the grant (the J
163 class), only on his explicit order for a named conversation." REOPENER:
none stated.

Lane readers-msg26's second round wrote each answer under its question in the
lane-K ledger and moved each row's next step: `M M34` to the guarded messaging
capture, `M C14` and the four conversation rows to builds on their session-11
captures, and the six article-composer rows to one new capture, `C-MSG26-4`.

## 8. The navigation ceiling (14:27, lane pace20)

RULED: (orchestrator, 2026-11-26) NAVIGATION-CEILING-MADE-TRUE --
"MAX_NAVIGATIONS_PER_CALL is documented as a ceiling but enforced nowhere, and
tools reach 3 (group_memberships, surface_census, the profile editors). Raise
it to the measured maximum, 3, and ENFORCE it in BrowserManager.goto (a
per-call counter refusing a 4th); correct the README's "One page load per tool
call". Owner: the first build lane after integration 4 (browser.py is in
pace20's diff)." REOPENER: none stated.

It answers the first question of lane pace20's record, section 10. Nothing is
built yet: the build is queued for the first build lane after this
integration.

## 9. What the same entries hold that is not registered here

- ORDERS, NOT RULINGS, each already carried out by its lane or queued: the
  `J 40` spelling ("N school alumni works here") joining `PROXIMITY_PHRASES`,
  built red first in lane search-fix26's second round; the instrument
  register's numbering, which integration 4 settles in merge order; the read
  boundary's comment on the content vertical, amended by lane readers-msg26's
  second round; and `M M28`'s entry in `SANCTIONED_MUTATIONS`, queued for the
  first build lane after this integration.
- THE PEOPLE GATE'S NEXT VERSION, specified at 14:05 in six rules (a member
  urn or member id not his anywhere in the HTML; a photo asset id not his; a
  photo picture's accessible text equal to a name; link-less social-proof
  templates; an events page skeleton-only by page class; the gate run on the
  HTML string actually written). It is the specification of
  PEOPLE-GATE-COUNTS-NAME-SLOTS's next version, queued for the next live-lane
  owner before session 12, and the instrument defect it closes is
  INSTRUMENTS 107.5 (104.5 on lane readers-net26's branch).
- ACTIONS ON UNTRACKED STATE: the deletion of session 11's kept raw events page
  (14:05), and the copy of session 11's live runner into gitignored state
  (14:27). Neither is a file in this repository.
- OTHER REPOSITORIES: the Naukri, Uplers and Instahyre parts of the 12:22
  entry, and the refusal of a claude.ai connector in the 12:50 entry.
