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

Built by child B in its own worktree (two commits, `d352ffc` and `0b2367f`),
reviewed and merged here; its report is the source of the reds below.

- B1, THE ITEM IS THE CALLER'S ARGUMENT, FOR ANY POST: walked end to end
  (`server.linkedin_react_to_item` -> `writes._write_tool` -> `preview` ->
  `observe` -> `_target_for` -> `_opaque_target` -> `_clean_target_part`; the
  permalink read; `_direction`; `mint`; `perform` -> `assert_write_url`,
  `_assert_landed_on_target`, `_live_control`, `valid_from`): NOTHING checks
  whose post it is, only the urn's anchored shape. No refusal existed, so none
  was removed. The tool's text said "Get it from linkedin_my_activity_items,
  which returns keys only for items established to be yours" -- where keys
  came from, read as a gate it never was. It now says the item is the caller's
  argument, names both key sources (his own items; `activity_items` of a profile
  he names) and that reacting to another member's post notifies them.
- B2, PREVIEW-NAMES-THE-RESOLVED-TARGET: the react preview adds, ONLY to the
  block it returns -- never the grant, the observation, a log or a receipt,
  each held by a test -- `who_this_would_reach` (the post's author as a people
  record, name and headline read off the permalink's one actor block, its link
  null by `people_seam`'s contract), `author_kind` (`you`, `another_member`,
  `unknown`) and the sentence saying where it was read.
  `linkedin_server/item_author.py`: locator reads only, no new evaluate.
  EVIDENCE CLASS: on his own post's permalink capture
  (`tests/fixtures/live2/own_post.html`, the only permalink capture) no
  author-only affordance is drawn without a press -- the post-analytics link
  the order suggested is MEASURED ABSENT in `main` -- so `author_kind` compares
  the actor's profile link with his own identity card's (the sidebar card beside
  his private analytics widget). That returns `you` on his own post; that it
  returns `another_member` on another member's is DERIVED (every name in the
  captures is sanitised, and none shows another member's post page), and the
  block says so.
- B3, THE INVERSE, IS NOT BUILT. Under the lane's time box child B committed
  only what was green; the un-react moves a dozen pinned tables across about
  fifteen test files. ITS DESIGN IS BUILD-READY in child B's report and is
  summarised here: action `unreact_to_item`, the react spec's address and
  pattern, from `reacted` to `no_reaction`, aimed ONLY at the two MEASURED ON
  labels ("Reaction button state: Like", his profile rail, 2026-09-04;
  "Unreact Like", his own liked post's permalink, 2026-09-23/24), verified by
  a fresh render reading the measured OFF label; registered in PERFORMABLE,
  `_TOGGLE_ACTIONS`, `_WHERE_TO_LOOK`, `_VERIFIED_FROM`,
  `item_author.REACTION_ACTIONS` and an outward-class record; the react spec's
  `reversible_by`, `wrong_state_note` and `reversibility_procedure` made
  truthful in the same change. ITS NAME NEEDS A RULING: `tests/test_writes.py`'s
  verb conservation law refuses `unreact` by name
  (`test_the_ruling_carve_out_admits_exactly_two_verbs_and_no_derivative`); the
  choice is to admit it in `_VERBS_ADMITTED_BY_RULING` (LinkedIn's own word,
  "Unreact Like") or to name the tool by an original verb
  (`linkedin_withdraw_reaction`).

RED FIRST (child B's runs): B1's two docstring tests failed on the shipped text
(and a check that could not fail -- the old sentence wraps across two lines --
was caught on the first draft and fixed by flattening whitespace); B2's preview
tests failed on the shipped gate (`assert None == 'another_member'`,
`assert None == 'you'`, `assert None == 'unknown'`, no record), and its module
tests with `ImportError` against an export of the previous commit. GREEN: the
file (renamed at this merge to
`tests/test_a_reaction_takes_any_item_and_names_its_author.py`, so its name no
longer claims the inverse) 16 passed, and the react-touching and static guards
child B ran, each under two minutes.

---

## C. A fill path that can restore an empty original (child C)

Built by child C in its own worktree (two commits, `cdcc06e` and `2ba23c1`),
reviewed and merged here; its report is the source of the reds below.

- `linkedin_server/field_restore.py` (new): a PROCESS-LOCAL restore record per
  canonical field -- the field, what the write typed (kept out of the repr),
  when, used -- with ONE writer, single use, thirty minutes of life
  (`RESTORE_TTL_SECONDS`), never on disk and never logged.
- `writes._clear_target` is the ONE admission of an empty value:
  `update_profile_field` asking for exactly "" for a field a live, unused record
  names. Its canonical target is `<field> :: ` -- the one unambiguous spelling
  of an empty second half -- and the token binds it like any other. Refused as
  before, now with the reason: no record, another field's, a used or expired
  one, the Premium badge switch, `None`, every other action and composite kind.
- `writes.perform` WRITES the record only on the fill path, only for a write
  VERIFIED stored, only when the value it overwrote was read as EXACTLY "" (a
  string; `None` records nothing). At the click (`_live_control`) a clear
  proceeds only if its control is a typed field, its record is live, and the
  field holds EXACTLY what this server's write typed -- THIS SERVER ONLY CLEARS
  WHAT IT WROTE. The fill types the empty slice of the canonical target, the
  fill path's wait waits for "", Save is pressed only if no other field moved,
  and the verdict is verified only when the fresh render reads "". Then the
  record is spent. The first write's receipt names the clear call and its terms
  (once, thirty minutes, this process), and no longer offers `value=''` where
  no record was made. The receipt's target block asks the KIND whether a target
  has two parts, where it asked the VALUE (a clear printed subject "" before).

RED FIRST (child C's runs): with nothing wired, 18 failed and 19 passed, among
them `WriteAttemptError: 'update_profile_field' needs 'value' and got ''` at
`_clean_target_part` with a recorded empty prior -- the red the order asked for;
with the admission wired and perform not, 9 failed. THREE GUARDS SHOWN FAILING by
one-line mutations, each reverted: the click-time check skipped (a field changed
since is cleared -- `DID NOT RAISE`), a `None` prior recorded, the old
target-block split restored. GREEN: `tests/test_an_empty_value_is_admitted_only_as_a_clear.py`
(29) and `tests/test_an_empty_original_is_restored_by_a_clear.py` (13), over the
intro-editor fixtures and the tracked live4 skeleton of his editor -- whose one
optional field holding "" the shipped readers find.

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
- `M C32` (messaging-and-content): the cell names the new route -- the item
  key from `activity_items`, passed back as `item`; nothing checks whose post
  it is; the preview names the author and its kind -- and says the inverse is
  NOT built and that the live proof waits on it.
- `P A8` (profile): the cell names the clear-restore -- the record a write over
  an empty original leaves, the one admission of the empty value as a CLEAR,
  the click's "only what this server wrote", the read-back that must read "".
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

STEPS 6-11 WAIT ON THE INVERSE. His YES was to react AND take the reaction
back; `linkedin_unreact_to_item` (or the name the ruling picks) is not built
(B3). Until it is on master and green, steps 6-11 are NOT RUN -- a reaction
this server cannot take back is not fired -- and the session spends 14 loads,
2 searches.

---

## Gates run (local, targeted, serial)

PENDING -- listed at the close.
