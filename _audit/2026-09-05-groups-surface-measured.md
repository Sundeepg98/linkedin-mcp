# GROUPS-SURFACE, measured: what is reachable, what needs a spec, what needs a ruling

**CORRECTS:** `_audit/2026-09-03-linkedin-gap-blockers.md` -- the blocker's own row count of 32 cannot be reproduced from the census data; the group family holds 35 rows and no subset of them reconciles.

**CORRECTS:** `_audit/2026-09-05-groups-events-precondition.md` -- its section 7 filed "`Groups listing` is LinkedIn's word for membership" as READ, NOT MEASURED and named the settling test as not taken; the test was taken and the reading is now measured.

Wave: groups-surface. Date: 2026-09-05. Every number below was taken by an
instrument carrying a control that fired, and the two instruments built today
are named with the runs they came from.

---

## 1. THE THING THAT WAS FILED AS UNMEASURED IS NOW MEASURED

`scripts/_probe_groups_menu.py` opened all five per-row overflow menus on the
`/groups/` root, one at a time, pressed nothing inside any of them, closed each
with Escape and checked that it closed:

    A. MENU-ROLE LABELS      NONE. This surface draws no [role=menu] content.
    B. ARRIVED CONTROLS      10  'Update your settings'
                              5  'Copy link to group'
                              5  'Leave this group'

**`Leave this group`, on all five rows under `Groups listing`.** LinkedIn does
not offer to leave something you have not joined. The precondition audit's one
soft reading rested on LinkedIn's choice of the word "listing"; this rests on
LinkedIn's own affordance, and it does not depend on reading anybody's copy.

**No group name crossed to get it.** All three labels repeat across the five
menus, so `census_redact_rare` kept them at their real tally -- and would have
redacted a singleton, which is what a label carrying one group's own name would
have been. That is the count rule working at the only window where it is
available, which is why five menus were opened rather than one.

### Four structural facts now say five, and not one of them is the word "member"

| signal | instrument | count |
|---|---|---:|
| heading boundary, disjoint from suggestions | `_probe_membership_sections.py` | 5 |
| a per-row management control exists | `_probe_membership_sections.py` | 5 |
| the control is ROW-SCOPED by containment | `_probe_groups_menu.py` | 5 |
| the menu offers `Leave this group` | `_probe_groups_menu.py` | 5 |

The disqualified controls separate too. Of ten buttons declaring
`aria-expanded`, five are row-scoped and five are not, with stopping-ancestor
widths `{5: 2, 11: 3}` -- two scoped to the whole five-suggestion block and
three to the page. **The suggestions get list-level controls; only the
memberships get a per-row one.**

`group_anchors_in_document: 11` against the census's 10 is not a disagreement:
this walk counts any anchor whose PATH carries the group segment, which
includes the nav's own link to the root. The reader refuses that one by name
(`group_root_carries_no_identifier`), which is where the eleventh goes.

## 2. THE RULING IS IMPLEMENTED AND HAS A CALLER

`linkedin_server/groups.py` -- counts and identifiers and NO NAMES. The name is
not a parameter of any function in it, which is asserted on the signatures
rather than argued in prose. `tests/test_membership_tally.py`, 23 tests, both
refusal branches proven by mutation on inputs where the branch under test is
the only thing standing.

Run against his real page by `scripts/_probe_membership_tally_live.py`:

    anchors 11, disclosure controls 10, of which 5 row-scoped
    ROWS WITH a row-scoped control      5 groups, 5 DISTINCT
    ROWS WITHOUT one                    5 groups, 5 DISTINCT, root refused
    in common 0, DISJOINT True
    NAMES PUBLISHED BY THIS RUN: 0

A third instrument, sharing no input feature with the other two: no heading is
read and no label is read.

## 3. THE COST INSTRUMENT IS NOT ON THIS PAGE

    feed    invitation badge 0    [mynetwork links 2, carrying a count 1]
    groups  UNREADABLE            [mynetwork links 2, carrying a count 0]

Both navs draw two mynetwork links; only the feed's carries a count, and the
feed's count read ZERO -- so LinkedIn does draw a zero and the element does not
merely vanish when empty. Two readings survive and neither can be eliminated
while his badge sits at 0, which is the degeneracy `shape.invitation_badge`'s
own docstring names.

**CONSEQUENCE FOR ANY GROUPS TOOL:** it cannot certify its own cost from the
page it reads. It returns to a page carrying the instrument for the AFTER
reading, or it declares the cost uncertified. It must not report a missing
instrument as a passing one. Both probes here read the feed at both ends;
both readings were readable and UNMOVED.

## 4. THE ROW COUNT DOES NOT RECONCILE, AND THAT IS ITS OWN FINDING

The ledger publishes `32 | 12R/20W` and does not publish which rows they are.
Walking the group family in `_audit/_scratch/_route-gap-rows.tsv` gives **35**:

    N 63 64                    2      M C60-C70                 11
    N 161-178                 18      M C91                      1
    N A10 A11 A12              3
                                                        TOTAL   35

**No subset of the 35 reconciles to 32 by any rule I can state.** The
candidates for exclusion -- `N 169` (an invite filter), `N 171` (a consequence
rather than an action), `N 172` / `N 177` / `N 178` (third-party reads) -- are
guesses, and a guess about which three rows are absent is not a reconciliation.
This is the newsletter wave's 13-against-12 in a second family: **a census
cannot see a duplicate that a route table cannot miss**, and the largest
blocker in the document has a row count nobody can reproduce from its source.

The classification below therefore covers **all 35**, and is stated per row so
that a reader who prefers a different 32 can subtract their own three.

## 5. THE CLASSIFICATION, ALL 35 ROWS

Against the boundary AS IT STANDS: `/groups/` root only, anchored, no query and
no sub-path. `/groups/<id>/`, `/groups/<id>/members/`, `/groups/<id>/requests/`,
`/groups/discover/` and `/search/results/groups/` are named refusals in
`readonly.py`'s own comment; `/groups/<id>/invite/` is refused TWICE, by the
forbidden substring `/invite` and by the anchored pattern.

### 5.1 REACHABLE NOW -- 3 rows, no boundary change, reader built today

| row | capability | evidence |
|---|---|---|
| `M C60` | access your LinkedIn Groups | 5 distinct, name-free, live |
| `N 173` | access the list of groups you belong to | same reading |
| `N 162` | browse groups recommended from shared attributes | the suggestion section is ON the admitted root: 5 distinct, disjoint |

**`N 162` is the one the ledger did not know it already had.** It was costed
as needing a recommendation surface; LinkedIn draws it on the root that is
already open, and today's split separates it from his memberships structurally.

What remains for all three is a TOOL, not a measurement: `server.py` wiring plus
a `dom` reader that walks the anchors. That file is contended by several waves
today and this wave did not take it -- see section 7.

### 5.2 SETTLED AS UNREACHABLE FOR THIS ACCOUNT -- 3 rows, and this is inference

| row | capability |
|---|---|
| `N A10` | invite your connections to a group you own or manage |
| `N A11` | message an individual group member as owner or manager |
| `N A12` | send a message request as a group admin |

**The per-row menu holds three items and NONE of them is administrative.** A
group he managed would draw manage-group entries there. That is a positive
structural signal rather than an absence of evidence, but it is **READ, NOT
MEASURED**: it assumes LinkedIn draws admin entries in that menu, which nobody
here has seen it do for a group anyone manages.

**The settling test WAS named here and this paragraph RETRACTS it.** It said:
press `Update your settings` on one row and read what it draws, one more press
on an already-admitted address, the cheapest thing left in this blocker.

**Measured at 17:27 and it is not available.** That control is an ANCHOR whose
href meets two forbidden substrings, so following it is refused before the
allowlist is consulted. A press that navigates to a refused address is not a
cheap measurement -- it is a boundary change wearing one.

The retraction is left visible instead of edited away, because **a
recommendation reads as a STANDING INSTRUCTION**, and this document's own
audience is somebody who will do what it says. This blocker therefore has NO
cheap settling test for the administrative inference, and these three rows stay
READ, NOT MEASURED until `/groups/<id>/` is argued or a modal is observed.

### 5.3 THE ONE WRITE WHOSE AFFORDANCE IS MEASURED PRESENT -- 2 rows

| row | capability | state |
|---|---|---|
| `N 64` | leave a LinkedIn group | control DRAWN, on an ADMITTED address |
| `M C63` | leave a group | the same control, counted twice by two slices |

**This is the most reachable write in the entire blocker and it needs no
boundary change at all.** What it needs is a WriteSpec, a sanction entry, and a
ruling on reversibility -- and the reversibility answer is not obvious:
rejoining a private group requires a manager's approval, so leaving is
effectively irreversible for any group he cannot rejoin unilaterally, and
nothing on the root says which of the five those are.

`N 176` ("prevent your network being updated when you join a group") and
`N 170` ("allow or prevent other group members from messaging you") are
SETTINGS, and the per-row menu draws `Update your settings` five times over on
an admitted address. **That looked one press away and it is not.**

Measured 17:27 by `scripts/_probe_group_settings_route.py`, which classified
the control's href against the two gates INDEPENDENTLY and navigated nowhere:

    5 controls wear that label, all of them <a>, path depth 3
    5  FORBIDDEN x2: ['/psettings/', 'settings']

**So both rows are DOUBLE-refused**, the way `/groups/<id>/invite/` is, and
they move to 5.5. A denylist exemption is a heavier act than an allowlist
addition, and `settings` is one of the broadest substrings on that list.

**A CONTROL BEING DRAWN IS NOT A ROUTE**, and the difference cost nothing to
establish here only because the href could be classified without following it.
Had this been costed off "the control is right there on an open page", two rows
would have been filed one boundary change from reachable when they are two.

### 5.4 NEEDS AN ALLOWLIST CHANGE -- 11 rows

| rows | why |
|---|---|
| `N 161`, `M C70` | search inside Groups -- `/search/results/groups/` belongs to `SEARCH-RESULTS-SURFACE`, which is queued DECIDE and is not this blocker's to inherit |
| `N 175` | a private unlisted group by direct link -- `/groups/<id>/` |
| `N 63`, `N 163`, `M C61` | JOIN and request-to-join. Moved here from 5.7 at 17:29: measured, no join control is drawn on the root's suggestion rows |
| `M C64`, `M C65`, `M C67`, `M C68`, `M C91` | the group FEED -- posting, commenting, editing, approval, reacting. All need `/groups/<id>/`, and the ledger's own ruling stands: **posting in a group is a second broadcast route with a different audience and is `publish_post`'s equal in risk** |

`N 174` is NOT here, and the first draft of this table put it here. It is an
address question only if the section exists, and section 5.7 records that
nobody knows whether it does. **A row cannot be costed as "needs an address"
until somebody has established there is a page at the other end** -- which is
the mistake the events wave found in this same ledger, where eighteen rows were
written against a registered-events surface that does not exist.

### 5.5 DOUBLE-REFUSED, so the ledger's "allowlist +2" is short -- 7 rows

`N 170` and `N 176` joined this list at 17:27, measured rather than assumed:
the `Update your settings` control on every membership row is an `<a>` whose
href meets **two** forbidden substrings, `/psettings/` and `settings`.

`N 166`, `N 168`, `N 169`, `M C69` all live on `/groups/<id>/invite/`, which
fails the anchored pattern AND contains `/invite`, a forbidden substring checked
BEFORE the allowlist. `M C62` (withdraw a membership request) meets `/withdraw`
the same way. **Each of these needs two boundary changes, not one**, and a
denylist removal is a different and heavier act than an allowlist addition.

### 5.6 NEEDS A RULING THAT ALREADY EXISTS ELSEWHERE -- 5 rows

| row | the rule that already answers it |
|---|---|
| `N 165` | the member roster. Put out of scope BY NAME by the team lead; `readonly.py` records it |
| `N 167` | a message request to a stranger -- third party plus messaging |
| `N 177` | finding people through shared membership -- third-party enumeration |
| `N 178` | which groups a member belongs to -- needs a third party's profile, which `PERMANENTLY_FORBIDDEN[load_a_third_partys_profile_to_measure_a_control]` refuses outright |
| `N 172` | a fellow member's connections. Not an action he takes; a LinkedIn behaviour |

### 5.7 UNSETTLED, AND THE ZERO CANNOT SETTLE THEM -- 4 rows

**THREE OF THIS BUCKET WERE SETTLED AT 17:29 AND MOVED TO 5.4.** `N 63`,
`N 163` and `M C61` -- join and request-to-join -- were costed on the guess
that the join control sits on a SUGGESTION row, which is on the admitted root.
`scripts/_probe_group_row_affordances.py` measured it:

    ROWS WITH A DISCLOSURE (memberships)   5   'Update your settings'  x5
    ROWS WITHOUT ONE (suggestions)         5   nothing repeats at all

**NO CONTROL IS DRAWN UNIFORMLY ACROSS THE SUGGESTION ROWS**, and that is what
turns an absence into a measurement. A join affordance would wear one label on
every suggestion row -- exactly as `Update your settings` does on every
membership row -- so it would tally 5 and survive the count rule. Every
suggestion-row label tallied ONE and was redacted as a singleton, which is what
a label carrying a group's own name does. **So the join rows need
`/groups/<id>/` or `/groups/discover/`, and neither is admitted.**

`N 164` ("join by responding to an invitation from a member or manager") stays
here: it needs an invitations surface, and no instrument has looked for one.

**THE PROBE'S OWN CONTROL FAILED FIRST AND THAT IS WHY ITS ANSWER IS WORTH
ANYTHING.** Its first reading was 11 rows and ZERO disclosures against the
button-up walk's five; it printed DISAGREE and refused to publish. The cause:
its control selector included `a[href]`, so the group anchor it climbed from
satisfied "this ancestor holds a control" all by itself. **A conjunct that is
always true is not a stricter rule -- it is the same rule with a longer
comment, and in a diff it reads exactly like the repair it is not.** Corrected,
it resolves 5 and 5 and prints AGREE.

`N 174` (groups requested to join): the root draws two sections and neither is
a pending-requests list. **That is not evidence the surface does not exist**,
because he may have zero pending requests, and a section that is absent when
empty reads identically to a section that does not exist. Same shape as the
badge at zero, one surface along.

`N 171` ("expose your profile to every member of a group you join") is a
CONSEQUENCE of joining rather than an action. It should be re-costed or
retired; it is not a capability this server could implement.

`M C66` (mention group members in a conversation) needs the group composer
AND reaches third parties, so it is behind 5.4 and 5.6 at once.

### 5.8 THE ROLL-UP

    REACHABLE NOW, reader built                              3   C60 173 162
    UNREACHABLE FOR THIS ACCOUNT (inferred, test named)      3   A10 A11 A12
    WRITE, affordance MEASURED PRESENT, needs a spec         2   64 C63
    NEEDS AN ALLOWLIST CHANGE                               11   161 C70 175
                                                                 C64 C65 C67
                                                                 C68 C91
                                                                 63 163 C61
    DOUBLE-REFUSED, needs two boundary changes               7   166 168 169
                                                                 C69 C62
                                                                 170 176
    ANSWERED BY AN EXISTING RULING                           5   165 167 172
                                                                 177 178
    UNSETTLED, and the zero cannot settle them               4   164 174 171
                                                                 C66
                                                              ----
                                                                35

**The rows are named rather than only counted**, because a bucket that reports
a total and not its members is a number nobody can check -- which is the exact
defect section 4 records in the ledger this document corrects.

**Ten of the 35 need no new ruling from anybody**: three are built, two need a
WriteSpec against a control that is already on the screen, and five are already
answered. **It was twelve until 17:27**, when the two settings rows were
measured to be double-refused rather than one press away -- the number went
DOWN because something was measured, which is the direction this document
should be trusted in.

## 6. WHAT THE MEASUREMENT COST, AND WHAT IT DID NOT

**SIXTY-FIVE page loads, counted per probe rather than remembered.** This
section said "four runs of the menu probe and two of the tally probe" until
17:55, which was true when written and had stopped being the whole story two
probes later. **A cost section that is merely out of date is the same defect as
one that is wrong**, because a reader cannot tell them apart.

    _probe_groups_menu.py            4 runs x 4 loads   16
    _probe_membership_tally_live.py  2 runs x 5 loads   10
    _probe_group_row_affordances.py  3 runs x 5 loads   15
    _probe_group_settings_route.py   3 runs x 5 loads   15
    _probe_groups_events_capture.py  3 runs x 3 loads    9
    the tab-close control study      6 runs, session only, no navigation
                                                      ----
                                                        65

The five ABORTED attach attempts navigated nowhere and are not counted.

Control `dark-mode` read 20 at both ends of every single run. The invitation
badge read 0 on the FEED before and 0 on the FEED after every run that took
one, readable at both ends -- and the bound on that is narrower than it sounds
and is stated in section 3: a badge at zero cannot distinguish "consumed
nothing" from "nothing to consume".

Nothing was pressed inside any menu, no navigation occurred during any press
sequence, and every menu closed on Escape with `aria-expanded` back to 0.

**Nothing was written to LinkedIn. No group was joined, left, or altered.**

## 7. WHAT THIS WAVE DID NOT DO, NAMED

* **No tool.** `server.py` and `dom.py` both hold other waves' uncommitted
  lines today, and `--only` does not protect a neighbour's LINES inside a path
  you name. The reader went into a module of its own -- the route
  `newsletters.py` and `events.py` both took today for the same reason.
* **No write, no WriteSpec.** `Leave this group` is measured present and is
  specified for whoever takes it, not built.
* **The `Update your settings` press was not taken, AND THIS ENTRY CORRECTS
  ITSELF.** An earlier draft of this section called it "the cheapest thing
  left". It is not available at all: measured at 17:27, the control is an
  ANCHOR whose href meets two forbidden substrings, so following it is refused
  by `assert_read_url` before the allowlist is even consulted. **A press that
  navigates to a refused address is not a cheap measurement; it is a boundary
  change wearing one.**

  The correction is left visible rather than edited away, because the earlier
  sentence is the more dangerous kind of stale: **a recommendation reads as a
  standing instruction, and whoever opens this next would have tried it.**
  What remains available is the modal question -- whether LinkedIn draws
  anything in place before navigating -- and nothing measured today says it
  does.
* **No page was closed by the probes until 17:26.** Measured: in ATTACH mode
  `BROWSER.session()` opens a tab and its own `finally` only touches an idle
  timer, so every probe run on this project leaks one. Twenty-four had
  accumulated across the fleet and `connect_over_cdp` enumerates every target
  during the handshake, which is what made attach fail five times running. All
  three probes here now close in a `finally`; `browser.py` was deliberately NOT
  changed, because the MCP server keeps its page across tool calls on purpose.
* **`shape.membership_row` was not changed.** Its hole is real, tested, and
  still has no consumer; this wave built the alternative rather than editing a
  function whose limit is deliberately asserted by its own tests.
* **The three ledger rows that would reconcile 35 to 32 were not identified.**
  Guessing them would have produced a reconciliation nobody could check.

## 7A. THE READER THAT IS MISSING, SPECIFIED RATHER THAN LEFT AS "BUILD A TOOL"

Three rows are REACHABLE NOW and what stands between them and a tool is a DOM
walk plus `server.py` wiring. This section is what that walk has to do, written
so the next wave implements rather than researches. **Every rule below was
measured today by an instrument that carried a control.**

### The walk

    1. GOTO the feed. Read shape.invitation_badge. Refuse if state != "read"
       -- the groups page cannot certify a cost, section 3.
    2. GOTO https://www.linkedin.com/groups/  (already on the allowlist).
    3. Collect every anchor whose href PATH contains "/groups/". EXPECT 11 on
       this account, of which one is the nav's own link to the root.
    4. For every button declaring aria-expanded, walk UP. The first ancestor
       holding at least one group anchor is the row; the control QUALIFIES
       only if that ancestor holds EXACTLY ONE.
    5. The group anchor inside a qualifying row's ancestor is a MEMBERSHIP.
       Every other group anchor is a suggestion or the root.
    6. Hand both lists to groups.membership_tally and the pair to
       groups.disjoint. Emit counts and identifiers. EMIT NO NAME.
    7. Read the badge again ON THE FEED, not on the groups page.

### The four rules that are NOT obvious and each cost a wrong reading

* **WALK FROM THE CONTROL, NEVER FROM THE ANCHOR.** The identical stopping rule
  run from the anchor resolved ZERO membership rows against five, on one page
  in one hour. A containment rule is not symmetric.
* **IF YOU ADD "and holds a control" TO THE STOPPING RULE, EXCLUDE THE GROUP
  ANCHOR FROM WHAT COUNTS AS A CONTROL.** An `a[href]` control selector makes
  that conjunct vacuous and silently collapses the rule back into the anchor
  walk.
* **DO NOT LOOK FOR `[role=menu]`.** This surface draws none. The overflow
  content arrives as ordinary controls and is visible only to a census DELTA.
* **DO NOT COUNT THE ROOT LINK.** `groups.group_identifier` already refuses it
  by name; a walk that pre-filters must refuse it for the same reason or it
  inflates every tally by exactly one.

### The control the reader must pass before its number is believed

**It must find exactly FIVE membership rows and FIVE suggestions with ZERO
identifiers in common.** Four independent instruments agree on that today. A
different number is a finding about the reader until proven otherwise -- and
the reader should PRINT the comparison rather than leave it to a reader of its
output, which is what caught two wrong rules on this surface already.

### What the tool may say

Counts, distinct counts, overlap, and the identifiers. **No name, and the
signature should make that structural rather than filtered** -- the reader can
hand `groups.membership_tally` a list of hrefs and never hold a name at all.
That is the ruling this surface was opened under, and a tool that takes names
"just in case" has re-opened the hole its module exists to close.

## 8. PROVENANCE

| instrument | control | outcome |
|---|---|---|
| `_probe_groups_menu.py` | dark-mode 20 at both ends; refuses without CDP attach | passed, 4 runs; refusal shown firing |
| `_probe_membership_tally_live.py` | dark-mode 20 at both ends; feed badge readable at both ends | passed, 2 runs |
| `_probe_group_row_affordances.py` | must resolve exactly 5 disclosure rows | RUN GREEN at 17:29 -- and its FIRST reading FAILED that control at 0, which is how the vacuous conjunct was caught |
| `tests/test_membership_tally.py` | both refusal branches killed by planted mutation | passed, 23 tests |
| `tests/test_no_committed_identity.py` | shown red on a real-looking slug, green after the rename, red again when it is restored | passed |

The captures are raw and gitignored -- `.gitignore:140` matches
`*_probe-*.html`, verified with `git check-ignore` before a byte was written.
