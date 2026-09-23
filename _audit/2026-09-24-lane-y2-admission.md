claude-opus-5-5[1m]

# Lane Y2 -- completeness admission: one verdict for every app-scope candidate

Lane Y2, 2026-09-24. Worktree branch off master `9c219c8`. OFFLINE: no LinkedIn,
no Chrome, no port 9224, no `_state/chrome-profile`. Captures were READ on disk;
nothing of theirs entered a tracked file beyond name-free route shapes and control
templates, and the harvester's exact-value veto was ARMED on every run. This lane's
commits are named by position, never by SHA (they are not on master and a merge may
rewrite them).

## 0. The answer

**The pending count was not right: there are more gaps, and now they are counted.**
Every one of the 121 app-scope candidates lane Y raised has one verdict:

    ADMIT      51   a user capability no census row carried, in words or synonyms
    RECORDED   61   a row carried it in words; the row gained the address or control
    OUT         9   not a user capability (a promo, a label, a presentation toggle)

The 51 admitted candidates are **35 new census rows** (J 15, P 8, M 8, N 4): several
candidates are one capability (five Learning discovery pages are one row, four
presence labels are one row). All enter at GAP with their blocker named in the cell.

**The one re-harvest over all 95 captures -- the live lane's 24 new ones included --
found 38 more app-scope candidates**: ADMIT 12 (8 more rows), RECORDED 22, OUT 4.
**Total admitted: 43 rows. The census row population moves from 704 to 747.** One of
the 43, `J 158`, is already served by a shipped tool (section 5), so the capability
gap this lane adds is 42 rows.

**THE DISCOVERY CURVE HAS NOT FLATTENED.** The last five surfaces in capture order
added 0, 0, 1, 6 and 1 new candidate routes against a declared criterion of zero; the
settings index alone added 14. Read as capabilities, the same five added 0, 0, 0, 2
and 1 admitted rows.

**THE COLD VERIFIER AGREED ON 20 OF 24 (83 percent)** -- all 9 sampled ADMITs, 11 of 15
sampled RECORDEDs, and every disagreement ran the same way: this lane had called
RECORDED what the verifier, reading the census cold, found no row plainly carries.
Three of the four were accepted, and the verifier's standard was then applied to every
unsampled RECORDED verdict, which moved six more to ADMIT (section 10). The counts
above are after that review; before it they read ADMIT 42, RECORDED 70.

Lane Y estimated 40 to 48 true gaps among the 121 (interval 18 to 78). The count is 51
candidates -- above the point estimate, inside the interval -- and 35 rows, because the
address axis counts one capability once per page it has.

## 1. What was asked, and what "app-scope" meant

The charter: every APP-SCOPE line of `_audit/_census/completeness-candidates.tsv` gets
ADMIT, RECORDED or OUT; then ONE re-harvest over all captures without writing tracked
files, its new app-scope candidates adjudicated the same way, and the curve printed;
then one cold verification of at least 20 verdicts. The fitness: **an ADMIT is a user
capability no census row carries in words or in synonyms.**

**THE DENOMINATOR, CONFIRMED.** The committed table held 163 lines: 121 app-scope
(68 addresses, 53 controls) and 42 others -- a11y 8, docs 11, chrome 11 (5 addresses,
6 controls), off-app 12 -- exactly the charter's classes. The 42 were not adjudicated.

**THIRTEEN LINES HAD ALREADY MOVED BEFORE THIS LANE STARTED.** Regenerated over the same
71 captures against the census at `9c219c8`, eight app-scope addresses were no longer
candidates -- other waves had written them into side-table lines keyed to rows
(`jobs-directions.tsv` for four company tabs, `/jobs/search-results`,
`/jobs/view/<id>/apply` and `/job-apply-resources`; `exclusion-basis.tsv` for
`/mynetwork`) -- and five of the 42 others had become RECORDED by coincidence of
words. The eight still got verdicts, RECORDED against the rows that carry them.

## 2. How a verdict was decided

* **RECORDED needs a row, not prose**, and the row must PLAINLY cover the capability,
  in words or true synonyms (`photo` covers `image`). A row about a neighbouring act
  or object does not count: a company's Products tab is not one product's own page,
  a subscriptions read is not changing the plan. The row gains the drawn address or
  control as one appended sentence (`**DRAWN, 2026-09-24 (lane Y2 ...):**`).
* **Entry points**: where the census splits an act by entry point -- job alerts from a
  search (`J 31`) and from a Page (`J 32`) -- a third entry point is a third row
  (`J 161`). Where it does not, a new entry point is RECORDED (`/messaging/thread/new`
  under `M M1`).
* **Grain, `GRAIN-FOLLOWS-WHAT-THE-PLATFORM-DRAWS`.** One capability reached at several
  addresses is one row (the Learning catalogue's five pages; four games). Different
  controls are different rows: the job tracker's rating, the recommendations' yes/no
  and the AI-answer thumbs are three (`J 162`-`J 164`), people search's own yes/no a
  fourth (`N 198`). A control that sets a parameter the capability already has --
  clearing a filter pill -- is that capability ("a parameter value is not a
  capability").
* **OUT is narrow**: a promotion (partner perks, a feature tour, a sponsored message's
  button, a promo card), a label (a group's privacy badge), a presentation toggle (a
  lightbox, a collapsible rail list, a media player's caption menu, a toast's close),
  an explainer.

## 3. Verdicts, per slice

The 121 (an ADMIT or RECORDED verdict counts in the slice of the row that now carries
it; an OUT keeps lane Y's annotated slice):

    slice    ADMIT   RECORDED   OUT    new rows
    J           26         25     3          15   (152-164, 166, 167)
    P           10         19     1           8   (S1-S5, S8-S10)
    M           11         13     1           8   (M52, M53, C93-C97, C101)
    N            4          4     3           4   (195-197, 200)
    none         -          -     1           -
    ------------------------------------------------
    total       51         61     9          35

The re-harvest's 38 new app-scope candidates:

    slice    ADMIT   RECORDED   OUT    new rows
    J            1          1     -           1   (165)
    P            2         12     -           2   (S6, S7)
    M            6          6     -           3   (C98-C100)
    N            3          3     -           2   (198, 199)
    none         -          -     4           -
    ------------------------------------------------
    total       12         22     4           8

Every verdict is written in `_audit/_census/completeness-annotations.tsv`, in three
new columns (`verdict`, `verdict_rows`, `verdict_basis`); section 8 describes the check
that holds them.

## 4. The 43 admitted rows

    J 152  Browse LinkedIn Learning (home, catalogue, certifications, topics, showcases)
    J 153  Watch a Learning course or video
    J 154  View the Learning library, saved and in progress
    J 155  Ask Learning's AI coach                                              R+W
    J 156  See and set career goals, "My career journey"                        R+W
    J 157  Change Learning settings                                              W
             152-157: New blocker `LEARNING-SURFACE`, every /learning/ page refused
    J 158  Read the Premium "Top choice" collection -- SERVED, entered GAP (section 5)
    J 159  Search the Ad Library for a company's ads      New blocker `AD-LIBRARY-SURFACE`
    J 160  Premium career insights for a target job   New blocker `CAREER-INSIGHTS-SURFACE`
    J 161  Create a job alert from a posting                        `JOB-ALERTS-SURFACE`
    J 162  Rate the job tracker                            New blocker `FEEDBACK-CONTROLS`
    J 163  Feedback on job recommendations                            `FEEDBACK-CONTROLS`
    J 164  Rate AI-generated jobs content                             `FEEDBACK-CONTROLS`
    J 165  Company Page Events tab (re-harvest)                     `COMPANY-PAGE-SURFACE`
    J 166  One product's own page                       New blocker `PRODUCT-PAGE-SURFACE`
    J 167  A company's affiliated showcase Pages                    `COMPANY-PAGE-SURFACE`
    P S1   Read the Featured section's items          New blocker `FEATURED-DETAILS-SURFACE`
    P S2   AI "Enhance profile" rewriting (Premium)          New blocker `AI-PROFILE-ASSIST`
    P S3   Where a skill is used on the profile          New blocker `SKILL-INSIGHTS-SURFACE`
    P S4   Add a custom button to the intro (Premium)     New blocker `CUSTOM-BUTTON-EDITOR`
    P S5   Profile-section engagement insights                    `PARSER-ON-A-LOADED-PAGE`
    P S6   Personal demographic information (re-harvest)      a settings page, no pattern
    P S7   Content language (re-harvest)                      a settings page, no pattern
    P S8   Key skills for recruiter search (Premium)             New blocker `KEY-SKILLS-EDITOR`
    P S9   Change the Premium plan                           New blocker `PREMIUM-PLAN-SWITCHER`
    P S10  Post a job as a hirer                                  New blocker `JOB-POSTING-FLOW`
    M M52  The composer's send options                   New blocker `COMPOSER-SEND-OPTIONS`
    M M53  Another member's messaging presence                    `PARSER-ON-A-LOADED-PAGE`
    M C93  Search all of LinkedIn (all-results page)               `SEARCH-RESULTS-SURFACE`
    M C94  Send a post in a private message (R2, outward)     New blocker `SEND-POST-DIALOG`
    M C95  Watch a LinkedIn Live broadcast or replay        New blocker `VIDEO-EVENT-SURFACE`
    M C96  An image's Content Credentials             New blocker `CONTENT-CREDENTIALS-PANEL`
    M C97  Delete a notification                         New blocker `NOTIFICATION-CARD-MENU`
    M C98  Read a LinkedIn News story (re-harvest)                New blocker `NEWS-SURFACE`
    M C99  See and play LinkedIn's daily games (re-harvest)      New blocker `GAMES-SURFACE`
    M C100 The feed's default view (re-harvest)               a settings page, `/settings/`
    M C101 Read a newsletter's own page and its editions             `NEWSLETTER-SURFACE`
    N 195  Recruiter insights (Premium)                          `PREMIUM-READER-NOT-BUILT`
    N 196  Report an organization Page                                     `REPORTING-FLOWS`
    N 197  Copy a group's link                                              `GROUPS-SURFACE`
    N 198  Feedback on people-search results (re-harvest)      the feedback-control blocker
    N 199  Premium networking suggestions (re-harvest)  New blocker `PREMIUM-MATCHES-SURFACE`
    N 200  Hide or report an ad in the feed                        `FEED-ITEM-OVERFLOW-MENU`

Directions: J 152-154, 158-160 and 165-167 read, J 155-156 read and write, J 157 and
161-164 write; P S1, S3 and S5 read, the other seven write; M M53, C93, C95, C96, C98
and C101 read, C99 read and write, the other four write; N 195, 197 and 199 read,
196, 198 and 200 write. Every row names its drawn address or control, the surface and
capture date it was drawn on, the nearest rows it was measured against, and why each
does not carry it. Twenty blocker names are new, each minted in its own row with
"New blocker:" so the asserted-names guard reads them as marked.

## 5. Four things the admission found that are not rows

* **`J 158` IS SERVED TODAY.** `linkedin_premium_job_collection(1)` opens
  `/jobs/collections/top-choice/`, and `_audit/2026-09-20-the-first-firing.md` read it
  live through that tool's reader and declined to write a row. It enters GAP because
  this lane admits at GAP and banks nothing; on `J 125`'s own bar it reads
  COVERED-PROVEN -- a state decision for the jobs slice's owner.
* **`P I12`'s EXCLUSION RESTS ON A PREMISE A DRAWN ADDRESS CONTRADICTS.** Its cell reads
  "measured: zero of 237 urls reach one", and `CONTAINER-EXCLUSION-PROPAGATES-ONLY-IF-
  UNREACHABLE` is built on that row as a sound exclusion. The jobs nav draws
  `/jobs/preferences/` as 'Preferences' (captured 2026-09-20). The address is now
  appended to `P I12`; its state is lane R's, untouched.
* **`N 136` (MEASURED-ABSENT, "no such panel is drawn")**: the recruiter-insights page
  admitted as `N 195` draws each RECRUITER viewer's company and industry. Not the
  all-viewer panel `N 136` measured absent, and not acted on; noted in `N 195` for its
  owner.
* **THE ADDRESS AXIS OVER-REPORTS AGAIN, BY A MEASURED MARGIN.** Of the re-harvest's 31
  new routes, 21 are capabilities a row already names (the settings index alone drew 11
  of them); the control axis, 7 new templates, is 4 presentation controls, 1 recorded,
  2 admitted.

## 6. What was appended to existing rows, and whose rows they are

Evidence sentences, one per row, appended to the row's last cell and never touching
its state. **Rows other lanes own** (one line each, per the charter):

    lane R  (EXCLUDED-RULED)  J 66, J 132, P D5, P G4, P I12, P K1, P K2, P N15, P N16,
                              P N17, P N18, P N19, P N20, P N22, P N28, P N29, M M42,
                              N 97, N 103
    lane D                    J 107
    lane L5                   M M1
    lane L7 (if among its 36 profile R3 rows)   P D24, P D27, P H1, P J1
    the live lane (edits seen on its unmerged branch)   M C72

Other rows: J 1, J 3, J 4, J 6, J 15, J 27, J 59, J 78, J 109, J 110, J 111, J 146,
P A25, P L2b, P N3, M M14, M M18, M M29, M M45, M C1, M C38, M C40, M C41, M C64,
N 4, N 57, N 129.

**ONE PIECE OF EVIDENCE COULD NOT GO IN ITS ROW, AND A GUARD SAID WHY.** 'Edit default
activity' (`/in/<me>/edit/forms/<id>/new/`) is `P G2`'s editor. Appended to `P G2`, it
made that row's cell substantive, and `P G3`'s positional `same` walked one row shorter
and re-pointed from `P G1` to `P G2`: `scripts/measure_pointer_graph.py --check` went
RED with "RE-POINTED ... NOTHING IN P G3's OWN LINE HAD TO CHANGE". The append was
reverted and the address recorded in `P G2`'s line of `_audit/_census/
blocker-assignments.tsv` -- a `row_id`-keyed line, so the harvester reads it as that
row's evidence -- with the reason in its note.

Every other append was checked the same way: the pointer graph passes all 69 pinned
pointers, and `scripts/classify_writeoff_reasons.py` derives the SAME kind for all 334
write-off rows as at `9c219c8`, diffed row by row -- no appended sentence carries a
classifier signal. Four appends made before the review (on `P E2`, `N 154`, `N 162`
and part of `P N22`, `P J1`, `J 110`, `J 111`) were taken back when their candidates
moved to ADMIT; `P E2`, `N 154` and `N 162` are byte-identical to master again.

## 7. Side tables

    _audit/_census/jobs-directions.tsv    +16   J 152-167 (R 9, W 5, R+W 2)
    _audit/_census/read-addresses.tsv     +13   P S1, S3, S5; M M53, C93, C95, C96,
                                                C98, C99, C101; N 195, 197, 199
    _audit/_census/write-classes.tsv      +14   P S2, S4, S6-S10; M M52, C94 (R2),
                                                C97, C100; N 196, 198, 200
    _audit/_census/blocker-assignments.tsv  one note (P G2, section 6)
    scripts/check_write_classes.py        two acts, `feedback` (N 198) and `purchase`
                                          (P S9), both R3 -- no act in the closed
                                          vocabulary named either

`check_jobs_directions`, `check_read_addresses` and `check_write_classes` are GREEN on
the result. Bucket 3 has 79 rows; three new ones are READER-gated (`P S5`, `M M53`,
`N 195`: admitted pages a shipped tool already loads, or of which a capture now
exists), so "blocked on nothing" moves 8 -> 11.

## 8. The instrument: the verdict layer, a corpus cutoff and a fixed-point check

`scripts/completeness_harvest.py` gains three things (registered as section 71 of
`_audit/INSTRUMENTS.md`):

* **`--captured-before <UTC stamp>`** names the adjudicated corpus. The committed table
  records ONE corpus, but a live lane writes captures every session, so a plain
  `--write` would rewrite the table over whatever arrived that hour. With
  `--captured-before 2026-09-23T00:00:00` the run keeps exactly lane Y's 71 captures
  (reproduced: 71 captures, 35 surfaces, 137 routes, 250 templates) and prints the rest
  as set aside.
* **`verdict_problems`** needs no capture, so CI runs it. Red when an app-scope line in
  the table has no verdict, when an ADMIT or RECORDED route is still a candidate (the
  row it names does not carry it), when a verdict names a row no slice writes, or when
  an OUT has no reason.
* **`--check`**: the committed table is byte for byte what `--write` would write over
  the named corpus, and the verdict layer holds.

`OWN_DOCS` also keeps this document and lane Y's out of the `known_elsewhere` column,
for the reason the two tables are kept out of the census: an instrument's own report
naming a route is not somebody else knowing it.

**THE CHECK EARNED ITS PLACE BEFORE IT WAS COMMITTED.** The census's closed vocabulary
is built from the census itself, so every word a new row brings can re-key a harvested
control label. The re-harvest's rows brought "zip" (from `/games/zip/`) and "hired",
and the regeneration turned two unannotated templates up -- 'City, state, or zip code'
and 'Get hired faster' -- which `verdict_problems` and lane Y's committed-table test
both named. The first is now RECORDED under `J 3` with the word in its evidence; the
second was avoided by rewording `N 199`.

**THE TABLE AFTER ADMISSION: 46 lines** -- the 9 OUT app-scope lines and 37 of the 42
others (five had already become RECORDED at `9c219c8`). Every ADMIT and RECORDED route
now classifies ROW and every such control RECORDED, and every OUT stays a candidate:
63 ADMIT, 83 RECORDED and 13 OUT annotations across both passes, 0 mismatches.

## 9. The one re-harvest, and the curve

Run once, over all captures, with no `--write` (its table went to scratch only):

    captures            95   (+24: the live lane's `_state/live1/` and `_state/l1-*`,
                              in its own worktree -- NOT the main checkout's `_state/`,
                              where the brief placed them; the harvester's worktree glob
                              reaches them)
    surfaces            53   (+18; six new captures folded into profile-views and one
                              post page by content)
    route shapes       175   (+38 drawn for the first time)
    control templates  313   (+63)
    candidates          61 routes, 23 controls against the admitted census;
                        31 routes and 7 controls are new

The new surfaces, in capture order (new candidate routes each):

    activity 1, post-closed 1, editor_fields 1, l1-contact 0, l1-audience 0,
    l1-overview 1, l1-articles 0, l1-post_summary 2, people_search 1, cap_prefs 14,
    cap_recruiter_views 0, cap_connections 0, cap_company_large 2,
    cap_company_services 0, pv_switch 0, own_link 1, badge 6, notifications 1

**NOT FLATTENED.** Last five: 0, 0, 1, 6, 1; the criterion was zero. The
permutation-averaged curve still rises about 0.7 candidates per surface at its end
(58.9, 59.7, 60.3, 61.0), and 37 of the 61 route candidates were drawn on exactly one
surface, 4 on two (Chao1 about 232, ESTIMATED, on an assumption this corpus violates).
**Read as capabilities**, the same five surfaces added 0, 0, 0, 2 and 1 admitted rows.

**Where the yield was.** Lane Y's list put the settings index second; it drew 14 new
routes, 11 of them settings the census already names row by row (RECORDED) and three
new rows (`P S6`, `P S7`, `M C100`). The page the live lane saved as `badge` drew games
and a news rail (`M C99`, `M C98`). The connections list, the recruiter-views page and
the second company root drew nothing new.

## 10. Cold verification

**THE DRAW.** The population was the 112 ADMIT and RECORDED verdicts as first written
(42 and 70), sorted by (kind, pattern); 24 drawn with `random.Random(20260924).sample`
-- 9 ADMIT, 15 RECORDED.

**THE VERIFIER.** One `implementer` child, run once, cold: it read the census as it
stood at `9c219c8` (the four slices, the inventory and the side tables, copied before
this lane's first edit), a neutral input file (the route or template, what it was
drawn as, the surface, and a description with lane Y's verdict markers stripped) and a
five-verdict rubric -- TRUE-GAP, CAPABILITY-RECORDED, ADDRESS-RECORDED,
NOT-A-CAPABILITY, UNCLEAR -- with the strictness rule that a neighbouring row does not
count unless it plainly covers the item. It was forbidden this document, the
annotations, the tables and the lane's scratch key. Every verdict came back citing a
file, a row and a line.

    as judged    TRUE-GAP 13   CAPABILITY-RECORDED 7   ADDRESS-RECORDED 4
    agreement    20 of 24 (83 percent) -- ADMIT 9 of 9, RECORDED 11 of 15; and on
                 all 11 agreed RECORDEDs the verifier cited the same row

**THE FOUR, EACH RECONCILED ON THE CENSUS TEXT.**

* `/newsletters/<entity>` (lane: RECORDED `N 57`) -- `N 57` lists WHICH newsletters he
  subscribes to; reading one newsletter's own page is not it. **Accepted: ADMIT,
  `M C101`.**
* `/premium/profile-key-skills` (lane: RECORDED `P E2`) -- the page was never opened,
  and "Add key skills ... helps you appear in recruiter searches" may be a Premium
  key-skills list rather than the editor's add. **Accepted: ADMIT, `P S8`.**
* 'Hide or report this ad ...' (lane: RECORDED `N 154`) -- `N 154` hides a post
  "without unfollowing its author", an organic item; an ad's own hide-or-report
  control is not it. **Accepted: ADMIT, `N 200`.**
* 'Cancel <X> filter' (lane: RECORDED `J 15`) -- the verifier found no row naming a
  filter pill's remove control. **Kept RECORDED**: clearing a filter sets the filter's
  own parameter to none, and `GRAIN-FOLLOWS-WHAT-THE-PLATFORM-DRAWS` says "a parameter
  value is not a capability"; the filter rows `J 3`-`J 15` carry it. The two sibling
  pills ('... level filter', '... posted filter') stand on the same reading.

**AND THE DIRECTION OF THE MISSES MATTERED MORE THAN THEIR NUMBER.** All four ran one
way -- RECORDED where the verifier saw no plain row -- so the verifier's standard was
applied to all 55 unsampled RECORDED verdicts. Six more moved to ADMIT, each on the
same test (the row covers a neighbouring object or act): one product's own page, three
spellings (`J 166`; `J 111` is the Products tab); a company's showcase Pages (`J 167`;
`J 110` is its own Home and Posts); changing the paid plan (`P S9`; `P N22` is the
subscriptions read); posting a job (`P S10`; `P J1` is the #Hiring signal).
After review the sample agrees on 23 of 24. **What this does not establish**: that the
remaining 61 RECORDED verdicts would all survive a second cold pass. The review found
6 of 55 lenient; a second sample was not drawn, because the charter allows one pass.

## 11. Expected pin moves

**The row population is re-pinned in its own commit** (`tests/census_row_pin.json` and
the two literals in `tests/test_the_census_row_total_is_pinned.py`): 704 -> 747,
J 150 -> 166, P 203 -> 213, M 142 -> 153, N 209 -> 215, no row removed, no state
vocabulary moved. It is separate so a merge can take the population move apart from
the rows.

**`scripts/census_completion.py` is NOT re-pinned.** Measured with the row pin moved,
`--check` is red on exactly these 17 of its pins and on nothing else (no bucket-1 row
moves):

    stated_rows              704 ->  747   +43
    capabilities             762 ->  805   +43
    capabilities_achievable  389 ->  432   +43
    achievable               389 ->  432   +43
    gap                      270 ->  313   +43
    gap_read                  66 ->   79   +13   P S1, S3, S5; M M53, C93, C95,
                                                 C96, C98, C99, C101; N 195, 197, 199
    gap_write                150 ->  164   +14   P S2, S4, S6-S10; M M52, C94, C97,
                                                 C100; N 196, 198, 200
    gap_unknown               54 ->   70   +16   J 152-167 (jobs rows carry no
                                                 direction cell)
    b3_admitted               40 ->   45    +5   P S5, M M53, M C96, N 195, N 197
    b3_refused                16 ->   24    +8   P S1, S3; M C93, C95, C98, C99,
                                                 C101; N 199
    b3_blocked_on_nothing      8 ->   11    +3   P S5, M M53, N 195 (READER)
    jobs_gap                  54 ->   70   +16
    jobs_dir_r                26 ->   35    +9
    jobs_dir_w                25 ->   30    +5
    jobs_dir_rw                3 ->    5    +2
    jobs_admitted              9 ->   10    +1   J 158
    jobs_refused              19 ->   29   +10

Unmoved and checked: out_of_scope 315, adjudicated 434, delivered 100 and 75,
cannot_deliver 19, unfired 25, gap_ambiguous 0, the other b3 classes (2, 6, 2), every
b1 pin, b2_d3_rows 3, and the other jobs pins (0, 1, 0, 0). **These are this lane's
moves against master `9c219c8`; other lanes moving states in parallel (lane R returns
exclusions to GAP) will move several of the same pins, so the train re-pins once, on
the merged tree.**

**THREE TEST PINS MOVED WITH THE ROWS, AND THOSE WERE RE-PINNED**, in the lane's fourth
commit, each with its arithmetic in the pin's own comment. The impact gate found them
(section 13); none is read by a census instrument:

    tests/test_a_census_locator_names_its_row.py  stated rows      704 -> 747
    tests/test_write_classes.py                   R1, R2, R3       (11, 23, 117) -> (11, 24, 130)
    tests/test_triage_instrument.py               slice M GAP      77 (R 10, W 65, R+W 2)
                                                                   -> 88 (R 16, W 69, R+W 3)

Like the row pin, each is a literal that another lane's rows can move too, so a merge
that touches two of them re-derives the figure rather than adding the deltas.

## 12. Gates

**CENSUS INSTRUMENTS, on the tree after the admission and the row re-pin:**

    check_jobs_directions         GREEN   70 of 70 still-GAP jobs rows
    check_read_addresses          GREEN   79 of 79 bucket-3 rows, every verdict
                                          re-driven through the live boundary
    check_write_classes           GREEN   165 lines for 164 write-direction GAP rows
                                          (the one extra is N 47's built line)
    measure_pointer_graph --check PASS    all 69 pinned pointers (after the P G2
                                          revert, section 6)
    classify_writeoff_reasons     ok      334 write-off rows, every kind identical
                                          to 9c219c8 row by row
    check_census_locators_resolve GREEN
    build_blocker_map --check     GREEN   44 rows entered GAP since the freeze (this
                                          lane's 43 and P L2b), today's GAP 313
    pin_census_rows --check       GREEN   after the re-pin (747)
    census_completion --check     RED on exactly the 17 pins of section 11
    completeness_harvest --control         all five controls pass
    completeness_harvest --check --captured-before 2026-09-23T00:00:00
                                  GREEN   fixed point, verdict layer 0 problems
    check_exclusion_basis         RED, as at master: 26 untraced and 27 lifted
                                  EXCLUDED-RULED rows, 0 structural problems; its
                                  own text says it stays red until the operator
                                  decides, and lane R owns those rows
    check_asserted_names_resolve  RED, as at master: 8 ASSERTED-ABSENT names, all in
                                  other lanes' documents; none in this lane's files,
                                  whose twenty new blocker names are all minted

THE IMPACT GATE, THE TESTS OUTSIDE ITS PLAN AND WHAT DID NOT RUN: section 13.

## 13. The impact gate, the red it found, and what did not run

**RED ON THE FIRST RUN, AND EIGHT OF THE NINE WERE THIS LANE'S.**
`scripts/impact_gate.py --against 9c219c8` on the third commit: 20 changed paths, 52
test files with the 17 corpus-wide guards among them -- not the full suite. **9 failed,
2402 passed, 1080 s.** Eight were figures or joins the admitted rows moved and that
none of section 12's census instruments reads:

    tests/test_a_census_locator_names_its_row.py  a second literal of the row
        population, 704, that the row re-pin did not know about -> 747
    tests/test_write_classes.py                   the pinned class split,
        (11, 23, 117) -> (11, 24, 130): M C94 is R2, the other thirteen admitted
        writes are R3
    tests/test_triage_read_gap_rows.py, 2 tests   the six admitted P and N reads
        had no triage verdict. Now P S1, P S3 and N 199 ADDRESS/ABSENT, P S5 and
        N 195 BUILDABLE, N 197 PRESS -- each the bucket-3 gate of section 7 in that
        triage's alphabet
    tests/test_triage_instrument.py, 4 tests      the messaging triage joins every
        GAP row of its slice to the blocker map, whose spine is the census frozen
        at 1c08e5f, so the eleven admitted M rows could never join; and its
        pinned headline split, 77 -> 88

The fixes are the lane's fourth commit: three pins re-pinned (section 11), six triage
lines written, and one rule the join did not have.

**THE JOIN NEEDED A RULE, NOT A NUMBER.** A row that entered GAP after the map's freeze
has no map line by construction. The messaging triage now derives those rows from the
census read AT the map's own `FROZEN_REF` from git -- never from the map, which would
turn every hole in it into an exemption -- exempts them from the join, and prints them
by id in a bucket of their own. An empty freeze read refuses, and so, since the fifth
commit, does a state cell spelled in a dialect at the freeze, which the enumerator
drops: a row that was GAP then would otherwise read as entered since. A cold reviewer
found that one (0 defects, 1 risk, on the fourth commit; inert today, because the
census at the freeze parses clean) and the fifth commit closes it. A rename cannot hide
behind the exemption either: the row pin holds an ID SET and names both ids. Shown
failing, four mutations of the committed script, each restored from git: exempting
every row (3 failed), no refusal on an empty freeze read (1 failed), the join ignoring
the exemption (3 failed), no refusal on a dialect at the freeze (1 failed); restored,
11 passed. Any lane that puts an M row into GAP after this -- an exclusion returned, a later
admission -- lands in that bucket instead of turning the triage red; what still moves,
by design, is the pinned split. Registered as section 71.6.

**THE NINTH WAS NOT THIS LANE'S: IT IS A RACE BETWEEN LANES.**
`tests/test_pointer_graph_guard.py::test_every_failure_class_is_convicted_and_the_calibration_is_not`
failed inside that gate, then passed alone on the same tree and inside the next gate.
`scripts/measure_pointer_graph.py --selftest` builds its sandbox at ONE fixed path
under the user's temp directory, `pointer-graph-selftest`, and deletes whatever is
there first, so two worktrees running the selftest at once delete each other's sandbox
mid-check -- and five lanes were gating on this box. DERIVED from the code and the
three runs, not reproduced on purpose (doing so would break other lanes' gates); not
repaired here, since the file is not this lane's. The repair is a per-run
`tempfile.mkdtemp`.

**AFTER THE FIXES**, on the fourth commit:

    impact gate --against 9c219c8      25 changed paths, 55 test files, PASS over
                                       2642 tests, 758 s. NOT CHECKED: 180 of 235
                                       test files
    the census-reading test files      34 files, chosen by a text search for the
      the plan does not select         census modules and paths: 1593 passed,
                                       3 skipped, 1 xfailed, 730 s
    the whole-tree forms of the four   the identity file and the navigation file in
      sweeps the gate answers on the   full over the tracked set, on the third
      change                           commit: 1470 passed; later commits touched
                                       only scripts, tests and this document, each
                                       through the pre-commit identity gate (0 hits)
    the candidate table                FIXED POINT on the committed tree, verdict
                                       layer 0 problems

**THE CANDIDATE TABLE'S FIXED POINT IS NOT MERGE-STABLE, AND CI CANNOT SEE THAT.** Its
`known_elsewhere` column is derived from every audit document, script, test and the
package, so another lane's document naming a candidate route moves the column. Measured:
an untracked document planted under `_audit/` naming `/legal/eula` (a docs-scope
candidate nobody else names) turned `--check` red with "would CHANGE address
/legal/eula"; removed, the fixed point came back and the tree was clean. The verdict
layer stayed at 0 problems throughout -- `verdict_problems`, the half CI runs, does not
read that column -- and `--check` needs captures that exist on this box only. **After
the train merges, regenerate the table here with `--write --captured-before
2026-09-23T00:00:00`, then `--check`.**

**NOT RUN:** 149 of the suite's 235 test files -- the gate's plan (55) and the extra
set (34) overlap on three, so 86 ran; CI's three-platform matrix, since nothing was
pushed; anything live, since this lane was offline; and `census_completion`'s re-pin,
deliberately (section 11). The gate of the commit that adds this section is reported in
the lane's final message: a document cannot hold the gate of the commit that writes it.
