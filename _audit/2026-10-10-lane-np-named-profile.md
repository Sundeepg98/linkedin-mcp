# Lane NP, 2026-10-10: the named profile's handles, its detail pages, the reaction's inverse, and a restore that can clear

Lane `lnp-named-profile-lead`, briefed by the orchestrator at 11:47 IST on master
`3c8edc2` (CI green). Built OFFLINE in its own worktree; nothing here loaded
LinkedIn. Two children worked closed slices in their own worktrees and are
merged here after review: child B (the reaction tool, item B) and child C (the
clear-restore, item C). The ruling of item D is registered in its own document,
`_audit/2026-10-10-rulings-named-profile-detail-pages.md`.

WHY THE LANE EXISTS. The live lane's session 7 (2026-10-10, 11:38 to 11:45)
proved `N 25`, `N 81` and `N 26`, and hit four walls, each an offline build:

1. `N 30`, `N 85`, `N 172` and `N 31` need the named first-degree member's
   member token for `linkedin_people_search_shape(connections_of=...)`, and
   `linkedin_read_named_profile` returned only a name, a headline and a link.
   The live lane rightly refused to lift an id off the page inside a tool
   (PAGE-MAY-VETO-NEVER-SUPPLY).
2. `M C32` (react to that member's post) had no route to a post id, though the
   profile's first render draws an Activity section.
3. `N 178` and `N 65` (groups, Interests) are not drawn on the first render.
4. `P A8`'s original is EMPTY, and the fill path refused to write "" back.

---

## A. The read he names hands back two handles

### A.1 What was built

`linkedin_read_named_profile` (ruling NAMED-PROFILE-READ-BEHIND-A-GRANT) now
returns, beside the person record, two DECLARED fields for the CALLER to pass
back as tool arguments. Nothing in the package consumes them -- that is the
sanctioned pattern, and two tests hold it: one module imports the composer
(`named_profile`), and the composer names no navigation and keeps no state.

- `member_token`: the PROFILE OWNER'S member id, exactly as LinkedIn writes it
  in the owner's own topcard links. Returned ONLY when two chains close on the
  same load:
  1. M M1's Message chain, as the engine the press would use reads it
     (`dom.read_named_profile`): the topcard draws ONE visible Message control,
     it is the owner's, it is the composer LINK, and its address names the
     member the topcard's own id names (`message_member_bound`);
  2. the page's own chain over EVERY topcard link (`dom.NAMED_HANDLES_JS`):
     the topcard id carries a member; at least one composer link; every
     composer link's `recipient` and `profileUrn` name that member; every
     people-search link carrying `connectionOf` holds exactly `[<member>]`.
  Absent (`None`) otherwise, with the first step that failed, in a closed
  vocabulary (`dom.NAMED_MEMBER_WHY`). Never an id of anyone else on the page.
- `activity_items`: the item keys (`urn:li:<type>:<digits>`, the shape
  `linkedin_my_activity_items` returns and `linkedin_react_to_item` takes) of
  the posts the first render's ONE Activity section draws, at most ten, each
  with `author`: `owner`, `another_member` or `unknown`. `owner` needs exactly
  one overflow control in the item whose name and the owner's (the title's)
  stand in a prefix relation -- the rule `linkedin_my_activity_items` applies --
  AND every ACTOR the item links before its first permalink to be one of the
  topcard's own member links. `another_member` is either half failing (a
  repost, a comment, a post the owner appears on). `unknown` is anything else.
  `None` when the page draws no single Activity section; `[]` when it draws
  one with no item.

Files: `linkedin_server/named_handles.py` (new), `dom.NAMED_HANDLES_JS` and
`dom.read_named_profile_handles` (new; one evaluate call site, so the
executed-script pin moved 24 -> 25 and the dom.py waiver budget 23 -> 24, each
with its argument in `tests/test_readonly.py`), and the read's integration in
`named_profile.read_the_confirmed_profile` and `read_preview`.

### A.2 Evidence classes

- MEASURED on the live lane's session-7 skeleton (gitignored; read, never
  copied): the topcard container's id is the 80-character shape of
  `com.linkedin.sdui.profile.card.ref<member id>Topcard`; the topcard draws two
  composer links whose `recipient` is one 39-character member value and whose
  `profileUrn` is that value percent-encoded under `urn:li:fsd_profile:`; it
  draws three people-search links carrying `connectionOf` (one raw JSON list of
  43 characters, two percent-encoded of 51) and `network` (`["F","S"]` raw, 9
  characters; `["F"]` encoded, 13); the Activity section is one `section`
  whose `h2` reads `Activity`, holding two items (`[role="listitem"]` each) and
  five permalinks between them, two distinct keys; each item links the topcard's
  own member three times before its first permalink; the first item's text
  links six other members AFTER it (mentions); both items' overflow labels are
  the 40-character shape of the measured prefix plus a name of the topcard
  heading's 10-character shape.
- DERIVED: that the topcard id's suffix is `Topcard` (its shape fits, as lane L5
  derived on 2026-09-28); that the `connectionOf` value names the owner (its
  length fits the owner's id in a list; lane S and lane L5 read the links as the
  member's own connections and shared connections); that a repost or a comment
  in this section names another actor or author -- NO capture shows one, and the
  rule refuses toward `another_member`.

### A.3 The fixture

`tests/fixtures/synthetic/named_profile_activity.html`, built by
`scripts/_build_named_profile_activity_skeleton.py` -- a subclass of the
session-2 builder that keeps every one of its rules and adds only the two
handles' addresses and labels -- from the session-7 skeleton. Declared synthetic
values only (the owner `casey-example-3f9a` / `ACoAASYNTHETICSYNTHETICSYNTHETIC0000002`,
others `someone-example-<n>` / `...0000001,3,4`, activity ids
`7400000000000000001` and `...0002`). It is a FIXED POINT: run over its own
output it reproduces it byte for byte (SHA-256 identical, measured), and its
structure digest is `abeadociamddhpai` both ways. Builder counts: 1400 elements,
0 unclassified text, labels or attributes.

### A.4 Red, then green

RED, before the read was wired (12:08):

    tests/test_named_profile_handles.py:75: KeyError
    >       assert out["member_token"] == OWNER_MEMBER, out["member_token_why"]
    E       KeyError: 'member_token'
    1 failed, 31 deselected in 19.53s

GREEN after wiring: `tests/test_named_profile_handles.py` 12 passed (37 s).
Its plants, each refused: a stranger's composer link in the hidden row
(`a_composer_link_names_another_member`), a stranger in a connections link
(`a_connections_link_names_another_member`), a topcard id with no member, no
composer link, and a stranger in the VISIBLE Message link (M M1's chain fails
first) -- in every case no token and no stranger's id anywhere in the answer,
and the items unchanged. Whose item: another actor, another author, a mention
moved before the permalink -> `another_member`; two overflow controls, none, no
actor -> `unknown`; a shortened owner name -> `owner`. Twelve extra items ->
ten returned, `truncated`. A key of another shape -> counted, never returned.
CONTROLS, each shown failing: with the composer check, the connections check,
the actor check, the author check or the stop at the first permalink weakened
in the script, its plant goes through (`test_control_each_check_weakened_lets_its_plant_through`).

---

## B. `M C32`'s react tool (child B)

PENDING CHILD B'S REPORT -- filled at its merge.

---

## C. A fill path that can restore an empty original (child C)

PENDING CHILD C'S REPORT -- filled at its merge.

---

## D. One detail page of the profile he names

### D.1 The ruling, and the door

Registered as `NAMED-PROFILE-DETAIL-PAGES` in its own document, verbatim:
"the read of a profile he names includes that SAME profile's own detail pages
(/in/<the same slug>/details/<section>/), one load per call, behind the same
single-use grant and the same preview warning." (the orchestrator, 2026-10-10,
applying the operator's 08:01 YES to reading profiles he names). The register
reads 69 rulings, every anchor resolving.

Built: a THIRD check, `readonly.assert_named_profile_details_url(url, segment)`,
taking the segment the caller NAMED; the composer
`readonly.named_profile_details_url(segment, section)`; the section a word of a
CLOSED vocabulary, `readonly.NAMED_PROFILE_DETAIL_SECTIONS` = experience,
education, skills, interests -- the four detail pages this boundary already
admits on HIS OWN profile, each loaded there, so no word is guessed. The
browser asks it only for `goto(named_profile_details_of=<segment>)`, never
together with the profile door. `linkedin_server/named_details.py` holds the
preview (nothing loaded, the same warning, a token bound to that one address),
the one load, the landing veto and a counts-only answer.
`linkedin_read_named_profile` gains `section`.

CONTROLS, each refused at the door and none quoted in the refusal: another
member's detail page asked under the named segment; the named page in another
ASCII case; the profile itself; `recent-activity`, `overlay/contact-info`,
`edit/intro`; `details/recommendations`, `details/connections`; a query, a
fragment, a deeper path, no trailing slash, another host, whitespace, a segment
carrying a refused word, no segment. And the two that show the CHECK, not the
shape, refuses: the anchored shape alone matches another member's page and a
section off the vocabulary; only the segment comparison and the vocabulary
refuse them. The read door and the profile door still refuse every detail page.
A token minted for the profile loads no detail page, and the other way round.

### D.2 The capture spec, NEEDS-CAPTURE C-NP1: a named member's Interests page

- WHAT: `https://www.linkedin.com/in/<the named member's segment>/details/interests/`,
  through `linkedin_read_named_profile(profile=<his link>, section="interests")`:
  the preview (0 loads), then the confirmed call (1 load). Never a load of its
  own outside that read.
- EXPECT A REDIRECT, AND RECORD IT: on his own account `/in/me/details/interests/`
  REDIRECTED to the profile (2026-09-04). If it does here, the read returns
  `landed_on_the_details_page: false` and reads nothing; the lane records the
  landing's PATH DEPTH only (2 = the profile), and there is no second load.
- IF SERVED, SAVE: the skeleton, by the same `skeleton_of` as sessions 2 and 7
  (texts and attribute values to keyed shapes, LinkedIn's words kept), to the
  live worktree's gitignored `_state/live8/named_interests.skeleton.html`, and
  these counts beside it: tabs (`[role="tab"]`) with their words (LinkedIn's:
  Top Voices, Companies, Groups, Newsletters, Schools, whichever are drawn) and
  which one is `aria-selected`; whether a tab is a LINK (and its address shape,
  e.g. a `detailScreenTabIndex` query) or a button; per tab panel drawn, its
  list items and how many link `/groups/<digits>/`, `/company/`, `/in/`,
  `/newsletters/`, `/school/`. The read's own `what_the_page_showed` returns
  most of these as counts.
- NO SCROLL AND NO PRESS. A tab press is not sanctioned; if Groups is not the
  default tab, that is the finding, and its address shape (if the tab is a
  link) is the input to a ruling on a tab address.
- AFTER: the live lane commits a TRACKED copy reduced the way
  `tests/fixtures/live2/first_degree_profile.html` was (every keyed text one x),
  and the reader of D.3 is built over the gitignored skeleton through a builder,
  as A's fixture was.

### D.3 The reader design, `N 178` and `N 65` (not built: no tracked skeleton exists)

- A new module, `linkedin_server/named_interests.py`, one reader
  `read_interests_entries(page)` over the served page, called by
  `named_details.read_the_confirmed_details` for `section == "interests"` and
  filling its `entries` (today ABSENT).
- Per tab DRAWN on the first render (the default tab; others only by a
  sanctioned address): its LinkedIn word, and its entries as people-data records
  under the six PEOPLE-DATA-MITIGATIONS -- groups as `people_data.Group` (title,
  `https://www.linkedin.com/groups/<digits>/`), which is `N 178`'s payload; Top
  Voices as `people_data.Person` records; companies, newsletters and schools as
  title-and-link records (a record type people_data does not have yet: an
  `Organisation`-shaped record is a decision for whoever owns people_data, and
  until then those tabs return counts only).
- Bounded: first render, no scroll, at most 50 entries, `truncated` said.
- Census: `N 178` GAP -> COVERED-UNFIRED on the tracked skeleton read by that
  reader, then PROVEN by a live read of a member he names; `N 65` the same, for
  the tabs the record types can carry.

---

## E. The census

NO STATE MOVES IN THIS LANE, so no pin is re-derived: `scripts/census_completion.py`
ends "every headline figure matches its pin" after every census edit and after
the merge of master `53908ea`.

- `N 30`, `N 85`, `N 172`, `N 31` (network): each cell gains the paragraph
  "BLOCKER, NAMED: member token from the named read (lane NP)" -- the route
  takes the named member's token as `connections_of`, and the named read now
  returns it as `member_token`. They move only when proven live (F). At the
  merge of master these four cells had ALSO gained live session 7's paragraph;
  resolved keyed by row, master's cell whole and this lane's paragraph after it.
- `M C32` (messaging-and-content): the cell names the new route -- see the
  merge of child B below.
- `P A8` (profile): the cell names the clear-restore -- see the merge of child C
  below.
- NOT EDITED, and why: `N 178` and `N 65` keep their cells -- their blocker is
  still a capture (C-NP1 now, on the detail page the new door admits), which D.2
  specifies; `M C35` ("Remove or change a reaction") is a candidate for the next
  session's un-react and is left to its own cell's bar.

---

## F. The next live session's spec (session 8): 40 loads and 5 searches assumed

PRECONDITIONS, ZERO LOADS. Master carries lane NP (A to D) and is CI-green by
its sha; the live lane merges it and its harness tests pass; the live-session
flag is up; the attach check passes. The targets are the operator's, by role:
the first-degree member he named for sessions 2 to 7 (his link from the
gitignored identity key), and his own profile. THE OUTWARD ACTS ARE COVERED by
the orchestrator's reading of 2026-10-10 (session 7's go): his YES of 10:56 to
"react to one of the brother's posts, then remove the reaction". No value any
step returns -- a token, a key, a name -- is written to a tracked file; the
ledger keeps key POSITIONS only.

THE ORDER, AND EACH STEP'S LOADS (20 s or more apart, as always):

    n      step                                                        rows
    1      signin check off his feed (as session 7's load 1)           --
    2      linkedin_read_named_profile(<his link>): preview (0 loads),  A
             confirm (1). RECORD: member_token present or not, and
             member_token_why; the chain's counts; activity_items'
             count and each item's author kind by position.
             IF NO TOKEN: record why, skip 3 and 4 (2 searches saved).
    3      search 1: linkedin_people_search_shape(                     N 30, N 85, N 172
             connections_of=<the token>, include_names=True)
    4      search 2: the same with network="F"                         N 31
    5      linkedin_read_named_profile(<his link>, section="interests"): N 178, N 65
             preview (0), confirm (1). The capture C-NP1 of D.2. A        (capture only)
             landing elsewhere is recorded (path depth) and NOT retried.
    6      linkedin_react_to_item(item=<the FIRST item whose author    M C32
             is "owner">): preview (1). It must read no_reaction and
             name the member's own post. IF IT READS REACTED -- his own
             earlier reaction -- take the next owner item; if none,
             STOP: a reaction that predates the session is never taken
             back.
    7-8    confirm: the press (1) and the verification's fresh render  M C32
             (1); verified "reacted".
    9      linkedin_unreact_to_item(item=<the same key>): preview (1);  M C35 (candidate)
             it must read reacted.
    10-11  confirm: the press and the fresh render; verified          M C32's inverse
             "no_reaction" -- the post back as it was.
    12-15  linkedin_update_profile_field(field="Additional name",     P A8
             value=<the value the orchestrator names>): his sharing
             setting read OFF, the editor, Save, the fresh render --
             session 6 measured four loads per edit. The prior must read
             EXACTLY "" (else STOP: no restore record is made).
    16-19  linkedin_update_profile_field(field="Additional name",     P A8
             value=""): the preview says CLEAR and that the record is
             live; four loads; the fresh render reads "".
    20     optional: a read-only re-read of his editor.

BUDGET: 20 loads of 40 (19 without the re-read), 2 searches of 5. Spare: 20
loads and 3 searches, spent on nothing unless ordered.

THE BARS, each row on its own cell's:

    N 30    search 1 returns people records -- the member's own connections -- and
            query_kept reads connections_of verbatim or same_values
    N 172   the same fire: the payload is WHO, as people records
    N 85    the same fire: the facet kept (query_kept), the filter applied
    N 31    search 2: both facets kept, every record at 1st degree
    M C32   a reaction performed and verified on a post of the member he named
    M C35   the inverse performed and verified -- a candidate; its cell decides
    P A8    the test and the clear both SAVED and verified, the field reading its
            empty original on a fresh render
    N 178,  no move on a capture: the reader of D.3 is built offline over the
    N 65    tracked skeleton, then fired

STOP RULES, as every session: any wall, challenge or unexpected landing stops
the session; a refused step is recorded and the next INDEPENDENT step runs
(2-4 hang on 2's token; 6-11 on 2's items; 16-19 on 12-15).

---

## Gates run (local, targeted, serial)

PENDING -- listed at the close.
