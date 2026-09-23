claude-opus-5-5[1m]

# The completeness probe -- does the census know every address LinkedIn rendered?

Lane Y, 2026-09-23. Worktree branch off master `b0d3ab8`. Offline: no LinkedIn
access, no Chrome, no port 9224, no `_state/chrome-profile`. Nothing in the
census was added or changed; every candidate below is evidence for the operator
and the orchestrator, not a row.

## 0. The answer, in four lines

1. **The census is not complete, and this is now a measurement.** Of 137 route
   shapes LinkedIn drew on 71 captured pages, 96 are carried by no census
   capability row. 68 of those sit inside the app (the rest are footer, Help,
   legal and other linkedin.com hosts). Beside them, 67 control templates carry
   words no single census row carries.
2. **The discovery curve has NOT flattened.** The last five surfaces in capture
   order added 0, 0, 1, 8 and 2 new candidate routes, against a criterion of
   zero declared before the first run. The permutation-averaged curve still
   rises by about 1.6 candidates per surface at its end.
3. **The instrument would have seen the one gap the census missed by accident.**
   Run against the census as frozen at `1c08e5f` (2026-09-03), it flags
   `/search/results/people` -- the people search that had no row -- together
   with 112 other candidates, and 17 of those 113 have since been written into
   census rows by other waves.
4. **The cold verifier's true-gap rate is in section 13.**

## 1. The question

`scripts/census_completion.py` cannot find a capability nobody enumerated. On
2026-09-03, 23 unenumerated gaps were found by accident. Completeness has never
been MEASURED. This probe measures it: harvest what LinkedIn itself rendered in
the captures already on disk, normalise every address to a path SHAPE, and diff
the shapes against every address the census records. Axis-hunting: fitness is a
class the census lacks; the saturation criterion is a measured flattening of the
discovery curve, capture by capture, in chronological order.

## 2. Method

Written BEFORE the first full run, so the criteria below could not be fitted to
the result.

1. **Captures.** Every raw page capture on disk from earlier live fires, found by
   explicit globs that never enter a `chrome-profile*` directory: the main
   checkout's `_state/` (and one level of its subdirectories), its gitignored
   `_audit/_probe-*.html`, the `_state/` directories sibling worktrees left
   behind, and the TRACKED sanitised fixtures under `tests/fixtures/` whose own
   header does not declare them invented, derived or synthetic. Byte-identical
   files are one capture. Nothing is copied out of any of them.
2. **Harvest, drawn only.** Bundles are stripped first with the SHIPPED
   `drawn_route_corpus.strip_bundles` (scripts, styles, `<code>` model payloads,
   templates, noscript), because a needle in the source is not a needle on the
   page. From what remains: every `<a href>`, every `<form action>` with its
   method, and every interactive control -- `button`, `select`, `textarea`,
   non-hidden `input`, and any element whose `role` is a control role -- with
   its accessible name (`aria-label`, else `title`, else `placeholder`, else its
   text).
3. **Shape.** Every address is reduced by the SHIPPED
   `_probe_premium_surfaces_shape.shape_path` at depth 6 (the depth
   `drawn_route_corpus.py` argues for), then hardened: a few more families whose
   next segment is content rather than route (`products`, `pulse`, `posts`,
   `hashtag`, `topics`) are reduced the same way, query VALUES are dropped and
   only parameter NAMES are kept beside the pattern, and the whole pattern is
   vetoed against the exact-value identity wordlist when the key is on disk.
4. **Census addresses.** Every address-shaped token in every census file
   (the four slices, the MCP inventory, and every `.tsv` under `_audit/_census/`
   including `read-addresses.tsv`), located to its row id where it sits in a
   capability row and to its line where it sits in prose. Census placeholders
   (`<id>`, `{id}`, `<slug>`, `NUMERIC-ID`, ...) are driven through the same
   reducer so both sides speak one alphabet; a placeholder segment on the census
   side matches a placeholder segment on the harvested side, and nothing else.
5. **Classes.** `ROW` -- a census capability row carries the pattern exactly.
   `PROSE` -- only census prose or a census table note carries it.
   `FAMILY` -- no exact match, but a census address is a segment-prefix of it or
   it of one, or the two share a literal leading segment. `NEW` -- no census
   address shares even its first segment. **CANDIDATES are PROSE + FAMILY +
   NEW**, reported by class so the reader can draw the line elsewhere.
6. **Controls** are a second, noisier axis and are reported apart from
   addresses. A label is reduced to a TEMPLATE -- the leading literal words, one
   `<X>` for the varying middle, the trailing literal words -- where a word
   survives only if the census slice files themselves use it, and only if it is
   the label's first word or is written in lowercase; digits become `<n>`; a
   label with non-ASCII left after punctuation folding, or longer than 16 words,
   is withheld and counted. A template is RECORDED when some census capability
   row carries every one of its content words; otherwise it is a candidate.
7. **THE SATURATION CRITERION, DECLARED HERE BEFORE ANY CURVE WAS COMPUTED.**
   Captures are ordered by capture time and repeat captures of one surface are
   folded into that surface's first appearance, so a re-capture cannot flatten
   the curve by construction. **The curve has flattened if the LAST FIVE
   distinct surfaces, in capture order, added ZERO new candidate address
   patterns.** Anything else is "not flattened", and the per-surface counts are
   printed either way. A permutation-averaged accumulation curve and the
   singleton count are printed beside it, because capture order was chosen by
   earlier waves for their own reasons and one ordering can flatten by accident.

Two refinements were added after the first run, each because a run over the real
captures produced a reading that was not true, and both only ever make the
output say LESS or say it more narrowly:

* **Placeholder matching was made strict.** The first version let a census
  placeholder match any literal segment, and one generic `/in/<member>/<x>`
  token then credited every profile sub-route LinkedIn draws as recorded. The
  probe was measuring the looseness of our own placeholders. Strict matching
  moved 17 routes from ROW to FAMILY.
* **Surface identity.** Repeat captures fold by name first (hydration and timing
  suffixes, a `control-` prefix) and then by content: a capture whose drawn
  address set is at least 0.95 Jaccard-similar to an earlier surface's is that
  surface. A `-control` SUFFIX is not a repeat marker: `cap-roleplay-control` is
  the premium hub captured as the control arm of the role-play experiment, and
  treating the suffix as a repeat merged the role-play page into the hub.

## 3. Captures found

    tier                 captures   where
    state                   23      main checkout _state/cap-*.html, 2026-09-20
    audit-probe             15      main checkout _audit/_probe-*.html, 2026-08-23..09-05
    worktree-state          15      three sibling worktrees' _state/ subdirectories, 2026-09-21
    fixture                 18      tests/fixtures/*.html, sanitised, dated by first commit
    ---------------------------------------------------------------
    distinct captures       71
    set aside                6      4 byte-identical to another capture;
                                    2 fixtures whose own header says LinkedIn did
                                    not serve them (one invented, one derived)

The 71 captures are 35 distinct SURFACES after folding (7 content folds, listed
by the instrument on every run). The sibling-worktree captures are a company
root read six times (`company-root-wording`), three group feeds
(`group-feed-permalinks`) and three job postings read twice each
(`how-you-match`). No capture is of `/feed/`, `/mypreferences/d/`, `/mynetwork/`,
`/jobs/`, `/learning/` or `/notifications/` unsanitised.

## 4. Harvest

    anchors drawn (bundles stripped)                  1762
    external anchors (another host; counted only)       15
    forms                                               32   all 32 carry no action:
                                                             LinkedIn handles them in script
    controls                                          2478   332 with no accessible name
    distinct address patterns                          137
    distinct control templates                         250   41 labels withheld
    exact-value veto                                 ARMED   (the key reached across
                                                             the worktree, as
                                                             tests/repo_paths.py does)

The forms contribute nothing to the address axis: not one of the 32 carries an
`action`. Every address below came from a drawn anchor.

## 5. Diff against the census

    census address tokens          947   631 in capability rows, 316 in prose
    distinct census shapes         192

    ROW       41   carried by a census capability row
    PROSE      4   carried only by census prose or a table note
    FAMILY    62   the census knows the family, not this route
    NEW       30   the census knows nothing under the first segment
    ------------------------------------------------------------
    CANDIDATES 96

**By scope** -- LinkedIn's own placement (another linkedin.com host; drawn only
in the site footer landmark), then a hand reading for Help, legal and site
furniture:

    app       68   a member capability surface
    docs      11   Help Center articles and forms, legal pages
    off-app   12   about, business, careers, learning-for-business, mobile,
                   premium offers and safety hosts
    chrome     5   the logo link to the home feed, accessibility, advertise,
                   get-the-app, the external-link interstitial

**A SECOND, WORD-LEVEL READING PER ADDRESS.** A route can be absent as an address
and present as a capability the census describes in words -- the company-page
tabs are the plainest case: `J 106-114` describe tabs without writing their
addresses. So every candidate also carries `word_rows`: the census rows that
carry EVERY literal word of the route. **32 of the 68 app-scope candidates carry
neither the address nor its words anywhere in a census row** -- that is the
stronger subset.

The shipped read boundary refuses 64 of the 68 app-scope candidates on a
name-free spelling. That is expected, not a finding about them: nothing admits
an address nobody enumerated.

## 6. Candidates per slice (app scope)

Slice is the lead's reading where the derived one (the nearest census rows) was
ambiguous; every line carries both its derived relation and its hand reading in
`_audit/_census/completeness-candidates.tsv`.

    slice   addresses (PROSE/FAMILY/NEW)    controls
    J          35  (0 / 31 / 4)                22
    P          21  (2 / 17 / 2)                 5
    M           7  (0 /  6 / 1)                20
    N           5  (1 /  3 / 1)                 5
    none        -                               1
    -------------------------------------------------
    total      68                              53    (+14 a11y or chrome controls)

What the classes hold, by family (the table has one line per route):

* **J -- jobs and the families the jobs slice already owns.** Twelve LinkedIn
  Learning routes (home, browse, certifications, career journey, the AI coach,
  my library, settings, showcases, topics) under a census that knows only the
  role-play scenarios; ten company-page tabs and product pages; the AI job
  search results route `/jobs/search-results`, apart from `/jobs/search/`;
  `/jobs/preferences`; the Top choice collection; the apply entry route; the
  resume-tailoring route `/job-apply-resources`; career insights; four Premium
  pages (perks, explore, change plan, and the hub's offers); job posting on the
  hiring side; the ad library.
* **P -- profile, settings, account.** The profile's Featured detail page, the
  add-experience and add-section editors, the second-language profile, the
  'Open to' explainer pages, the AI 'Enhance profile' overlay, per-skill insight
  pages; the settings index and five of its category pages (account, ads, data
  privacy, visibility, sign-in and security); recruiter views (Premium); key
  skills (Premium); subscription management; identity verification; the
  followers list.
* **M -- content.** Creator top posts, a member's all-posts activity, newsletter
  pages, the report-abuse modal, all-results search reached from a hashtag, the
  new-thread messaging route, LinkedIn Live event pages.
* **N -- network.** The My Network hub itself (census prose only), its Discover
  hub and discovery lists, showcase pages, a group's own settings page.

Control candidates with the clearest capability shape: create a cover letter,
tailor a resume, enhance a profile, add a custom profile button, set an alert for
similar jobs from a posting, share that you're hiring, attach a file or image to
a message draft, send a post in a private message, start a post in a group,
delete a notification, change notification preferences, dismiss a
people-you-may-know promo, hide or report an ad, the content-credentials badge,
the verified-hiring badge, and five kinds of feedback control on AI answers.

## 7. The discovery curve

    surface                            first captured       pats   new  newC   cumC
    fixture:profile_views_analytics    2026-08-21T18:06:48     4     4     1      1
    fixture:jobs_tracker_empty         2026-08-21T19:34:55     2     2     0      1
    fixture:jobs_tracker_row           2026-08-21T19:34:55     2     1     0      1
    fixture:notifications              2026-08-21T19:34:55     5     4     2      3
    fixture:profile_skills             2026-08-21T19:34:55     2     2     1      4
    fixture:profile_topcard            2026-08-21T19:34:55    12    11     3      7
    fixture:jobs_search                2026-08-22T01:43:33     1     0     0      7
    fixture:job_detail                 2026-08-22T17:56:38    24    20    19     26
    tracker-saved                      2026-08-23T05:50:28    15     9     6     32
    job-followed-company               2026-08-23T05:57:44    28     0     0     32
    fixture:manage_pages               2026-08-23T07:15:59     1     0     0     32
    tracker-inprogress                 2026-08-24T17:26:55    14     0     0     32
    tracker-draft                      2026-08-24T17:58:02     7     0     0     32
    tracker-in_review                  2026-08-24T17:59:06     9     0     0     32
    groups-menu                        2026-09-05T10:58:26    15     4     2     34
    darkmode                           2026-09-05T12:02:24    14     7     6     40
    events                             2026-09-05T12:02:51    12     1     0     40
    newsletters                        2026-09-05T12:06:09    15     3     2     42
    jobs-recommended                   2026-09-20T04:31:49    11     0     0     42
    premium-hub                        2026-09-20T04:31:59    32    10     9     51
    profile-views                      2026-09-20T04:32:17    17     1     1     52
    search-appearances                 2026-09-20T04:32:26    20     6     4     56
    roleplay                           2026-09-20T05:22:04    20    15    15     71
    ct-messaging                       2026-09-20T06:15:06    11     0     0     71
    ct-sharebox                        2026-09-20T06:15:25     6     0     0     71
    ct-creator                         2026-09-20T06:16:04    19     5     2     73
    ct-jobsalerts                      2026-09-20T06:16:24    21     2     1     74
    company-root                       2026-09-20T06:56:26    32     6     5     79
    rc-badges                          2026-09-20T07:04:53    44     7     5     84
    rc-school                          2026-09-20T07:05:52    26     1     1     85
    collection-top-applicant           2026-09-20T10:33:18    12     0     0     85
    collection-top-choice              2026-09-20T10:33:28    13     0     0     85
    how-you-match                      2026-09-21T00:19:23    35     1     1     86
    company-root-wording               2026-09-21T01:41:13    42     9     8     94
    group-feed-permalinks              2026-09-21T01:47:34    23     6     2     96

(`pats` routes drawn on the surface; `new` routes no earlier surface drew;
`newC` of those, candidates; `cumC` candidates known so far. Times are UTC.)

**NOT FLATTENED.** The last five surfaces added 0, 0, 1, 8, 2 new candidates;
the declared criterion was zero. Two independent readings agree:

* **Permutation average** over 400 random orderings of the 35 surfaces: the
  mean number of candidates known after k surfaces is still rising at the end
  -- 89.6, 91.0, 92.8, 94.2, 96.0 for k = 31..35, about 1.6 per surface.
* **Singletons.** 54 of the 96 candidates were drawn on exactly one surface, 11
  on exactly two. A population in which most classes have been seen once has
  not been sampled to saturation. The Chao1 richness estimate from those two
  counts is 96 + 54^2 / (2 x 11) = 228.5, about 229 candidate routes --
  **ESTIMATED**, and on
  an assumption this corpus violates (surfaces were chosen by waves, not drawn
  at random), so read it as "the unseen part is of the same order as the seen
  part", not as a count.

What a single surface can still add is the plainest evidence: the premium hub
added 9, the role-play page 15, the six company roots read on 2026-09-21 added 8
that the first company root had not drawn.

## 8. Live-capture list

Ten pages whose capture would extend the curve most, chosen from what the
harvest shows and what the shipped boundary admits TODAY (every one below was
driven through `readonly.is_read_url` offline and returned True, except the two
that are presses, not pages). Ordered by expected yield.

    1  /feed/                                   never captured; 14 captured
                                                surfaces link to it; the largest
                                                content surface -- posts, comments,
                                                reactions, reposts, ads
    2  /mypreferences/d/                        the settings index, never captured;
                                                five of its category pages are
                                                already candidates, seen only in a
                                                side nav
    3  /notifications/                          only a sanitised, trimmed fixture
                                                exists; per-card controls surfaced
                                                two control candidates from it alone
    4  /search/results/people/?keywords=<term>  the family found by accident on
                                                2026-09-03; never captured as a page
    5  /feed/update/urn:li:activity:<id>/       a post permalink with comments; the
                                                census itself says comment-level
                                                controls were never enumerated
    6  /mynetwork/invite-connect/connections/   the only fixture of it is invented;
                                                connection-card menus never read
    7  /analytics/recruiter-views/              itself a candidate; a Premium page
                                                never captured
    8  two or three more /company/<slug>/ roots of other kinds (a large org with
       showcase pages, a services firm): six company roots on 2026-09-21 still
       added 8 routes the first had not drawn
    9  the Me menu, opened (a PRESS, not a page): it sits in the header of every
       capture and its items render only on press, so no capture holds them.
       Needs a press the disclosing-press ruling admits
    10 the jobs search All filters panel, opened (a PRESS): its controls are the
       jobs slice's filter rows; take it only if the press is already sanctioned

**Would extend it, and the boundary refuses them today** -- a decision for the
orchestrator, not the live lane: `/mynetwork/` (the hub; census prose only),
`/jobs/` (jobs home), `/learning/` (twelve candidate children),
`/my-items/`, the company tabs (`/company/<slug>/about/` and siblings), and
`/search/results/all/`.

## 9. The instrument and its control

`scripts/completeness_harvest.py`. Reusable: `--write` regenerates the table,
`--control` runs five planted controls and then drives each into its failing
state. The hand readings live in `_audit/_census/completeness-annotations.tsv`,
keyed by (kind, pattern), and are merged at write time so a regeneration never
loses one; the instrument never reads either of its own files back as census.

**THE TEST, SHOWN FAILING.** `tests/test_completeness_harvest.py`, five tests,
green on the real census and red under each of three mutations of the
instrument, run 2026-09-23 against the committed script and restored from git
after each:

    MUTATION A  census_index returns an empty list
      FAILED test_a_planted_route_is_a_candidate_and_a_recorded_one_is_not
        /analytics/profile-views is carried by census capability rows and came
        out 'NEW' -- the census parse or the matcher has stopped seeing it
      FAILED test_a_route_written_into_a_census_row_stops_being_a_candidate
        a route written into a census row still came out 'NEW'
      2 failed, 3 passed

    MUTATION B  OWN_FILES emptied: the probe reads its own output as census
      FAILED test_its_own_output_is_never_read_back_as_census
        the probe read its own candidates file as census and called a planted
        route 'PROSE' -- a second run would report zero candidates
      1 failed, 4 passed

    MUTATION C  the shipped reducer bypassed inside reduce_path
      FAILED test_no_name_no_query_value_and_no_bundled_route_leaves
        'placeholder-member' left the reducer
      1 failed, 4 passed

**MUTATION B FIRST PASSED, AND THAT WAS THE TEST'S DEFECT.** Its plant wrote into
the files named by `OWN_FILES` -- the very set the mutation emptied -- so the
mutation emptied the plant too and the test passed vacuously. The plant now
names the two files the instrument WRITES, from their output paths, and asserts
those names separately. A plant derived from the thing under test cannot test it.

## 10. Leaks and misreadings the instrument's own first runs produced

Each was found by running a draft over the real captures and reading the output,
not by reading the code:

* **A control-label rule based on capitals printed the operator's own first
  name** -- it begins every conversation label that lists him first, so it began
  two or more distinct labels -- and a third party's surname written in
  lowercase. The identity key holds only longer spellings of the first name, so
  the exact-value veto did not fire. The rule was replaced by a closed alphabet:
  a word leaves only if the census slice files use it. Neither word occurs in
  them; nor does any of the fixture sanitiser's invented names. Nothing from the
  leaking run was ever written to a tracked file.
* **A census placeholder matched any segment**, which credited the whole profile
  family as recorded (section 2).
* **A card's own `<footer>` was read as the site footer**, which filed a My
  Network list under site chrome. Scope now follows HTML-AAM: a `<footer>` or
  `<header>` is contentinfo or banner only when no sectioning element encloses it.
* **A `-control` suffix merged two surfaces** (section 2).

## 11. What this does not tell you

* The segment directly after a member-bearing prefix is `<entity>` on BOTH
  sides, so a new route in exactly that position (`/groups/<something>/`) is
  invisible here. The shipped reducer replaces it unconditionally because a slug
  is indistinguishable from a word, and that price is paid on purpose.
* Only DRAWN addresses count. A control that navigates by script leaves no
  address; it appears as a control template or not at all.
* The control axis matches by co-occurrence: a template is recorded when one
  census row carries all its content words. Synonyms miss, coincidences hit, and
  a word the census never uses leaves as `<X>`, so this axis UNDER-reports new
  vocabulary. The verifier's sample in section 13 is the only measure of it.
* A zero is a fact about the captures. 35 surfaces is a small sample of
  LinkedIn, which is what section 7 says in numbers.

## 12. Side effect on a generated file, for the orchestrator

`scripts/find_blocker_reason.py` treats every tracked `_audit/**/*.tsv` except
`blocker-map.tsv` as a candidate argument document, and the candidates table
names census row ids beside words its ARGUES pattern matches. So the table now
appears as a low-scoring candidate for many blockers, and every
`CANDIDATE-1-OF-N` denominator in `blocker-map.tsv` that it touches grows by
one. No rank-1 document moves: the table scores 1 and ties go to the earlier
document. The right repair is one line in that script's `DERIVED_ARTIFACTS` --
the table is a file a script writes -- and that script is outside this lane's
ownership, so it is reported here rather than made.

## 13. Cold verification

(pending)

## 14. Gates

(pending)
