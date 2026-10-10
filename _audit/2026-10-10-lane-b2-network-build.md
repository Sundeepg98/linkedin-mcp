# Lane B2 -- the network build: seventeen BUILD rows read against their captures

Lane B2 (`lb2-network-build`) of the LinkedIn MCP capability census,
2026-10-10, from master `f93104c`, fast-forwarded at 15:52 to `71d83ca` (lane
K's ledger and its rulings, merged). Offline throughout: no LinkedIn load, no
Chrome, no CDP port. The live-session flag was absent when this lane started,
and every local gate here was the tests touched, their direct importers and the
census instruments, each under two minutes, serially; the full suite ran on CI
(section 9).

The brief named seventeen network rows, each `BUILD` in lane K's next-step
ledger (`_audit/_census/next-step.tsv`), each on a capture. Each row was first
read against its own capture -- the tracked skeleton where one exists, and the
live lane's gitignored keyed skeleton where none does -- BEFORE anything was
built, because a BUILD step names a capture and says nothing about whether the
capture draws what the row needs. Twelve captures did not draw it; two rows
needed no build at all, their payload already delivered and proven by a
shipped route; three were built.

**CORRECTS:** `_audit/2026-09-28-lane-k-ledger.md` -- section 12.7 moved `N 37`, `N 43`, `N 51`, `N 153`, `N 154`, `N 200`, `N 80`, `N 88`, `N 89` and `N 93` to BUILD on session 8's skeletons, and section 5 counted "unsubscribe" on the newsletter list for `N 56`; read against the captures, ten of those eleven steps had nothing to build on (sections 2, 3 and 5), and the eleventh, `N 80`'s, is discharged under D6.

## 0. Status, per row

    row    capability (short)                    state before -> after      section
    N 37   unfollow a person from a feed post    GAP -> GAP                 2
    N 43   mute a person from a feed post        GAP -> GAP                 2
    N 51   mute a company                        GAP -> GAP                 2
    N 153  hide a network update                 GAP -> GAP                 2
    N 154  hide a single post                    GAP -> GAP                 2
    N 200  hide or report an ad                  GAP -> GAP                 2
    N 80   narrow search results to People       GAP -> COVERED-PROVEN      3 (D6)
    N 88   filter by School                      GAP -> GAP                 3
    N 89   filter by Industry                    GAP -> GAP                 3
    N 93   filter by Keywords (fielded)          GAP -> GAP                 3
    N 133  filter profile-viewer data            GAP -> COVERED-PROVEN      4 (D6)
    N 56   unsubscribe from a newsletter         GAP -> GAP                 5
    N 103  other similar profiles                GAP -> GAP                 5
    N 104  find a Page by searching              GAP -> GAP                 5
    N 161  search for groups                     PENDING                    6
    N 179  search for events                     PENDING                    6
    N 102  a Page's People-tab insights          PENDING                    7

## 1. How a hashed label was read, and what that method may not do

The live lane's skeletons (`scripts/_probe_live_lane_session_2.py`,
`skeleton_of`) keep tags, classes, roles and closed ARIA states, keep a closed
list of LinkedIn's own words verbatim (`FURNITURE`), and replace every other
text and attribute value by its SHAPE: letters, digits, length and an 8-hex
HMAC under a per-session key kept beside the skeleton. So a label that is not
on that list reads, for example, `{L13D0n14:<hash>}`.

THE METHOD. For a CLOSED LIST of LinkedIn's fixed product strings -- menu
entries, filter labels, dialog buttons; no person's, company's or post's text
-- the keyed shape of each candidate was computed with that session's key and
compared with every shape in the skeleton. An equal shape is the label,
measured: the key makes a collision of an 8-hex mark and identical letter,
digit and length counts a negligible event, and the test is exact, so a
decorated variant (`School (3)`) is NOT matched and NOT excluded. The ruling
this rests on is `FIXED-UI-LABEL-MATCH`: a fixed product label is not
third-party text.

WHAT IT MAY NOT DO, and did not do: test a name, a company, a title or any
string that is somebody's; print or commit a hash or the key. The method is
committed as `scripts/verify_fixed_labels.py` (`_audit/INSTRUMENTS.md`
section 90): it tests only its own closed vocabulary, takes no label from a
caller, and prints counts. Every label reading in this record was re-taken
with it over the three skeletons it rests on; the scratch readers that found
them first are declared disposable in section 11.

## 2. The feed item menu: N 37, N 43, N 51, N 153, N 154, N 200

THE CAPTURE. Session 8, load 14 (the live lane's record, section "Live session
8, re-issued"): `/feed/`, one item's control menu pressed open through the
shipped gate (`permitted`, priced by `off_state`, the witness saw it
disclose), kept as `_state/live8/lk_feed-item-menu-open.skeleton.html` beside
the feed before the press, `lk_feed.skeleton.html`.

WHAT THE OPEN MENU DRAWS, measured by section 1's method. One `role=menu`, in
a portal at the end of the body, holding 7 `role=menuitem` entries, in order:

    1  Save                      verbatim (on the skeleton's own list)
    2  Copy link to post         verified
    3  Embed this post           verified; a link carrying a targetUrn parameter
    4  19 letters, 21 characters NOT identified
    5  Not interested            verified
    6  15 letters, 18 characters NOT identified
    7  Report post               verified; a link

THE ITEM WHOSE MENU IS OPEN is a `role=listitem` headed `Feed post`
(verified), whose actor links `/company/<slug>/` -- a PAGE's post, not a
member's. Entry 4 fits `Unfollow <the actor>` by letter and length arithmetic
alone: the actor's name is drawn as 11 letters in 12 characters, and
`Unfollow ` adds 8 letters and 9 characters. That is DERIVED, not measured,
and it is a Page's unfollow. Entry 6 does not fit `Mute <the actor>`: 4 + 11
letters is right, but 5 + 12 characters is 17, not 18.

THE TARGET CANNOT BE AIMED THERE, measured on both feed skeletons: of the 8
items the page heads `Feed post`, one anchor in all carries an activity
address -- so a tool cannot find on `/feed/` the item a caller names, and
choosing one for him is the page supplying the target, which
`PAGE-MAY-VETO-NEVER-SUPPLY` forbids. The one route that takes the target from
the caller is the item's own permalink, `/feed/update/<urn>/`, admitted and
priced by its own reaction toggles in `press.SENSITIVITY_BASES`; NO capture
shows a permalink's control menu open on another member's post, so whether
the permalink draws `Not interested`, `Unfollow <a person>` or `Mute ...` is
unmeasured. And the undo LinkedIn draws after a hide -- the only proof
`HIS-OWN-CURATION-NOT-OUTWARD` accepts where the undo is drawn once -- is in
no capture at all.

THE AD. The same skeleton holds an ad's flow as two CLOSED `dialog`
elements: the first draws two buttons verified as `Why am I seeing this ad?`
and `Hide or report this ad`; the second is a form with one two-choice radio
group and a submit, whose title and both choices are unverified. The ad item's
own control was not pressed.

SO NO ROW MOVES, and each keeps a dated note with its own reason:

    N 154  `Not interested` measured; cannot be aimed at a named item; no undo captured
    N 153  the same entry, on a Page's post, not a network update
    N 37   `Unfollow <actor>` derived only, on a Page; no route aims it; no re-follow route
    N 43   no Mute entry measured; a member's post's menu in no capture
    N 51   a Page's post's menu captured, no Mute entry measured
    N 200  the ad flow drawn closed; ends in a form; the ad is LinkedIn's choice

THE CAPTURE THAT UNBLOCKS FIVE OF THEM, added to the capture queue as
`feed-item-permalink-menu` (`CAPTURE-PRESS-UNDER-PROBE-RULE` permits a capture
to open a menu; nothing in it is pressed): two permalinks, one member's post
and one Page's post, each urn read off the live lane's own reading (the open
menu's `Embed this post` link carries one), the control menu opened and closed,
skeleton only. It says, per item kind, which of `Not interested`,
`Unfollow <actor>` and `Mute <actor>` the permalink draws -- the reading every
build of these rows stands on. `N 200` goes to the `feed-menus` line: the ad's
own control opened and closed and its dialog read, nothing chosen or submitted.

## 3. The people-search labels: N 80, N 88, N 89, N 93

THE CAPTURE. Session 8, load 16: the people search with a keyword, the panel
settled at 92 controls, the shipped label reading fired (`by_term`), kept as
`_state/live8/lk_search_labels.skeleton.html` with its receipt.

MEASURED by section 1's method over every text and attribute value of that
skeleton: `Actively hiring`, `Current companies`, `Locations`, `1st`, `2nd`
and `3rd+` each match once, `All filters` and `People` stand verbatim, and
`School`, `Schools`, `Industry`, `Industries`, `Keywords`, `First name`,
`Last name`, `Title` and `Company` match 0 times. So the first render draws no
control labelled exactly `School`, `Industry` or `Keywords` -- the second
reading of that, beside the live reading's own `by_term` 0 for each.

N 80 MOVES, BY D6, WITH NO NEW CODE. The row is named for an affordance, the
vertical control, and `D6-CAPABILITY-OVER-AFFORDANCE` discharges such a row
when the package delivers the same payload by its own sanctioned route:
search results narrowed to people, which `linkedin_people_search_shape`
delivers by composing `/search/results/people/` and landing on it. That route
is live-proven as a tool -- `N 79` (session 2: 10 people records from 10 of 10
result cards) and `N 194` (session 3: 11 person results) are COVERED-PROVEN on
it -- and session 8's load 16 read it again (landed on the people search; 6
person results, 0 all-results anchors). The control half this row's cell asks
for is measured as well: the toolbar draws the vertical selector as a
`radiogroup` whose pill is labelled exactly `People`, over a checked
checkbox. Why the live label reading counted `people` 0 is not settled here:
that pill's input carries an accessible name of its own, 16 characters, not
the visible word. COVERED-PROVEN, resting on those proofs.

N 88, N 89 AND N 93 STAY GAP: the control each needs is not drawn on the
first render, and it sits behind `All filters`, which a shipped tool cannot
open (no `aria-expanded`, the disclosing-press ruling's condition 2) and a
capture now may (`CAPTURE-PRESS-UNDER-PROBE-RULE`). An exact check does not
exclude a decorated label, and session 8 took no `decorated` reading, so none
of the three is a MEASURED-ABSENT candidate on this evidence. Each goes to the
capture queue's `search-people-labels` line, beside `N 82`, `N 86` and `N 90`
to `N 92`: the All-filters panel opened and closed.

THE PLANNED FIXTURE `tests/fixtures/live8/search_labels.html` WAS NOT BUILT:
no row this lane holds is built on that page.

## 4. N 133: the press it waits on was built, and fired

The cell's last step: "what remains is that press, as for 134" -- the
view-switch press `VIEW-SWITCH-PRESS-RESTORED` permits. It shipped as
`view_switch.apply_and_restore`, reached through
`linkedin_who_viewed_me(view_switch=...)`, and on 2026-09-23 23:08 it filtered
his profile-viewer data live: the 'Interesting viewers' pill's 'verified'
option applied, 6 rows under the filter, `applied_view_differs` True, then
`restored` True with three counters held (`N 134`, COVERED-PROVEN; the live
lane's record, Entry 7). Filtering his viewer data and putting the view back
is this row's payload, so `D6-CAPABILITY-OVER-AFFORDANCE` discharges it on
that route: COVERED-PROVEN.

The ledger's BUILD step for it named `tests/fixtures/synthetic/
profile_views_pill_open.html`: that fixture IS the 'Interesting viewers' pill
open, with the two options the view-switch table already carries
(`interesting_viewers_verified`, `interesting_viewers_company_you_follow`).
The `Company` and `Past 90 days` pills (measured present 2026-09-05) have no
captured options; a filter on either is a new table entry built on a capture
of its own, and nothing in this row waits on it.

## 5. N 56, N 103 and N 104: each capture read, and each short of its bar

N 56, UNSUBSCRIBE FROM A NEWSLETTER. The ledger's step read BUILD on
`tests/fixtures/synthetic/newsletter_subscriptions.html`, with
`'unsubscribe' on the newsletter list` counted on the fixture. The fixture's
one unsubscribe sits in its header comment, and that comment says the
capture draws NO unsubscribe control. Outside its comments the fixture holds
0 occurrences of `subscrib`; the raw capture it was built from (the main
checkout's gitignored newsletters probe, 74,315 bytes) holds 0 of
`nsubscrib`. The list draws no control to press. Where one is drawn -- a
newsletter's own page is the candidate, INFERRED -- that address is not
admitted, so the row joins lane A's `admit-newsletters-id` queue line: ADMIT.

N 103, OTHER SIMILAR PROFILES. A third first render without the section:
session 7's named read (`_state/live7/named.skeleton.html`, read offline)
draws `People you may know` and `You might like` verbatim, once each, and
neither `People also viewed` nor any other heading on the skeleton's closed
list; sessions 2 and 3 read the same. A build on `tests/fixtures/live7/
named.html` would be built on a page without the section. The rail is below
the first render (a scroll, `SCROLL-NOT-SANCTIONED`) or on the profile's
overlay sub-page, which the named-profile door does not admit -- both on lane
NP's route: SIBLING lane-NP.

N 104, FIND A PAGE BY SEARCHING. The row's own cell set the bar: an id reader
delivers it if the results page draws a numeric organisation id per result,
and "If the result cards carry slugs only, it does not deliver". Measured on
session 2's skeleton of the companies search (`tests/fixtures/live2/n104.html`
is its tracked copy): 10 distinct `/company/<segment>/` result links, nine
drawn three times and one twice, and every segment carries letters -- nine
letters only, one of 8 letters and 3 digits -- with 0 numeric. No id reader
delivers it. Whether `NAMES-AT-RUNTIME`, and `THIRD-PARTY-TEXT-AT-RUNTIME`
(which returns an organisation Page's prose at runtime), make an
organisation's own name and Page link returnable as a search result is the
orchestrator's call, put to him as `Q-ORG-IDENTITY` in the ledger's record.

## 6. N 161 and N 179: the groups and events searches

THE CAPTURES, measured offline by shape (session 2's groups search, session
3's events search; tracked copies `tests/fixtures/live2/n161.html` and
`tests/fixtures/live3/n179.html`): the groups page draws NINE results, each a
relative `/groups/<digits>/` link (5 to 8 digits) wrapping one
`role=listitem`, the title its first paragraph, a Join control beside it; the
events page draws THIRTEEN, each a `role=listitem` holding an
`/events/<19 digits>/` link that holds a second link to the same event, the
title that inner link's own text. Both are what `people_data.Group` and
`people_data.Event` declare: a title and a canonical link.

THE BUILD (child A, section 12): `linkedin_server/search_vertical_results.py`,
`read_group_results` and `read_event_results`, modelled on
`people_results.read_result_people` -- every card resolved once to a handle
before any text is read, the title read only from the measured node, the
link read again after the text and a moved card skipped and counted, one
record per canonical link, visible only, at most 25 cards, failures counted
by exception type, every skip reason a closed literal, nothing loaded,
pressed or stored. Two tools in this lane's server block,
`linkedin_search_groups(keywords)` and `linkedin_search_events(keywords)`,
each composing its one page with `search_verticals.compose`, putting it to
the read boundary before a session opens, loading it once and returning the
records with non-text denominators; both joined `people_data.PEOPLE_TOOLS`,
and `search_verticals`' orphan entry was deleted in the same commit, as its
own docstring required of its first importer. The fixtures
`tests/fixtures/synthetic/search_groups_live.html` and
`search_events_live.html` are written from the keyed skeletons by
`scripts/_build_search_vertical_fixtures.py`, which extends the named-profile
builder: synthetic ids of the same length, every title reduced to shape, a
fixed point, and a structure digest equal to the tracked copy's.

RED FIRST AND THE MITIGATIONS: `tests/test_search_vertical_results.py` holds
each behaviour and each of the six `PEOPLE-DATA-MITIGATIONS`, with a control
that can fail beside each (section 12 has the child's red runs).

## 7. N 102: a Page's People-tab insights

MEASURED BEFORE THE BUILD, by section 1's method over session 2's keyed
skeleton of the People tab: inside `main` the first page draws the insights
module -- `h3` headings `Where they live`, `Where they studied`, `What they
do`, `What they are skilled at` and `What they studied`, each verified, under
an `h2` of 17 letters and 4 digits in 24 characters -- and one section holding
0 member links and 27 digit-only text nodes, the bucket counts, beside the
roster's own section of 225 member links. The counts are drawn on the first
page, which is this row's own condition.

THE STRUCTURE, measured by child B on the same skeleton: the module is one
carousel section of six list items, one per category, each an `h3` and its
buckets; a bucket is an `a[role=checkbox]` (a facet filter of the roster,
never pressed) holding exactly two paragraphs, the label then the count, on
all 27 buckets -- five each under the five verified headings, two under a
sixth heading of 18 letters that is not read. The only further control is the
carousel's `Next`, a press, never pressed. The roster sits in another list:
75 cards, 225 member links, in no heading's container.

THE BUILD (child B, section 12): a declared record, `people_data.Aggregate`
-- a category from a closed vocabulary of the five headings, a label
sanitised and capped as a title, a non-negative integer count -- and
`linkedin_server/company_people_insights.py`, whose reader finds the module by
its exact headings, reads buckets only inside a heading's own container,
parses a count only from a digit run, and never reads a member link; and the
tool `linkedin_company_people_insights(organization_id)` in this lane's
server block, composing the People tab with `member_rosters.compose` (its
first importer; the orphan entry deleted with it) and loading one page. The
fixture `tests/fixtures/synthetic/company_people_insights.html` is written
from the keyed skeleton by `scripts/_build_company_people_insights_fixture.py`,
which extends the named-profile builder: the five headings verbatim, every
count a synthetic number of the same digit count, every label reduced to
shape, the roster cut to three synthetic cards; a fixed point, and a source
digest equal to the tracked copy's.

## 8. The census moves, and the pins

ROUND 1, `2b3a0ee`. `N 80` and `N 133` GAP -> COVERED-PROVEN under D6;
twelve rows keep GAP with a dated note each, newest first in the cell. By
`scripts/count_census_states.py`, the network slice: GAP 155 -> 153,
COVERED-PROVEN 22 -> 24. `scripts/census_completion.py --check` then named
six figures, each re-pinned on its measured value, never by a delta:

    adjudicated         210 -> 212
    delivered_broad     132 -> 134
    delivered_strict    111 -> 113
    gap                 561 -> 559
    gap_read             92 -> 90
    b3_admitted          41 -> 39

THE LEDGER, by the same commit. `_audit/_census/next-step.tsv` lost `N 80`
and `N 133`; twelve steps were rewritten: `N 37`, `N 43`, `N 51`, `N 153` and
`N 154` to CAPTURE `feed-item-permalink-menu` (a new queue line, five rows,
two loads), `N 200` to CAPTURE `feed-menus` (its line now two rows), `N 88`,
`N 89` and `N 93` to CAPTURE `search-people-labels` (five rows to eight),
`N 56` to ADMIT on lane A's `admit-newsletters-id` line (four rows to five),
`N 103` to SIBLING lane-NP, `N 104` to RULING `Q-ORG-IDENTITY`, a question
added to the ledger's record. `_audit/_census/read-addresses.tsv` lost the
two rows that left GAP; `N 104`'s gate went MEASURE -> RULING, and four notes
gained a dated line. `check_next_step` GREEN at 559 and `check_read_addresses`
GREEN at 90 of 90; the blocker map, the audit index and the rulings register
regenerated.

## 9. Gates, run and not run

PENDING.

## 10. The live-proof specs

PENDING.

## 11. Instruments and scratch

REGISTERED: `scripts/verify_fixed_labels.py` with
`tests/test_verify_fixed_labels.py`, `_audit/INSTRUMENTS.md` section 90.
Shown failing before it was trusted: with its keyed-shape lookup removed (a
one-line mutation, reverted), the planted-label test fails `assert 0 == 1` on
`Not interested`; the control reads the same planted skeleton with another
key and counts 0 for every shaped label and 1 for the verbatim one; a
decorated `School (3)` counts 0 for `School`. 7 passed once restored.

DECLARED DISPOSABLE, in the lane's scratch folder: the first label checker
the instrument replaced, the label locator, the markup excerpter, the open
item's tree printer, the feed aim probe, the People-tab outline probe, and the
census, ledger, pin and register editors. Each answered one question once;
the answers are above, and every label reading was re-taken with the
registered instrument.

## 12. Children

PENDING.

## 13. Questions for the orchestrator

1. `Q-ORG-IDENTITY` (`N 104`), put in the ledger's record: the cell's own bar
   says a slug-only results page does not deliver, and the capture draws
   slugs only. May a search return each organisation it found as its name and
   its Page link at runtime, as the rulings `NAMES-AT-RUNTIME` and
   `THIRD-PARTY-TEXT-AT-RUNTIME` return other content? Master gained an
   organisation record during this lane (`people_data.Organisation`, lane G2):
   a name and a link, and the link is the Page's NUMERIC address by design,
   because "a slug can be a name". So the declared record already refuses
   this capture's links, and a yes would have to say whether a slug link may
   ride in it for a search result. The build would sit on the tracked capture
   `tests/fixtures/live2/n104.html`.
2. `N 200`'s target. An ad is chosen by LinkedIn, not named by him; a tool
   that hides "an ad in the feed" takes its target from the page unless he
   names the ad. Is hiding the ad LinkedIn shows at the moment of the call his
   own curation of his own feed, or does `PAGE-MAY-VETO-NEVER-SUPPLY` require a
   named ad?
3. Two discharges under D6 that went to COVERED-PROVEN, not to the
   COVERED-UNFIRED the brief named: `N 80` rests on the people search's live
   proofs and `N 133` on `N 134`'s view-switch fire. D6 says PROVEN where the
   route is live-proven; both are the orchestrator's to override.
