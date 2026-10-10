# Lane G2 -- queued debts: a red instrument made green in its records, a reader guard that took a refusal tally for success, a post record

Lane G2 (`lg2-debts-lead`) of the LinkedIn MCP capability census, 2026-10-10,
from master 3c8edc2 (CI green, run 36460989178). Offline throughout: no
LinkedIn load, no Chrome, no CDP port. A live session ran on this box the
whole time, so every test run here was serial and targeted, and from 11:35 the
orchestrator's gate policy bound it: the tests touched, their direct
importers, and the census instruments for the files changed, under two
minutes; the full suite runs on CI.

Each item was first checked against the tree with `git log -S`/`-G` and the
code, because several were queued before a lane that landed them.

## 0. Status, per item

| item | verdict | section |
|---|---|---|
| 1. the asserted-names check, red on 8 sites | fixed in `912cc25`; red test shown | 1 |
| 2. earned-clean, the people-search readers | fixed in `f3b46fb`; 17 readers move, red tests shown (this branch's hashes do not resolve on `master` until it merges) | 2 |
| 3a. a post record in `people_data.py` | built in `d1529ff`; red tests shown | 3 |
| 3b. the root-logger captures that could not fail | done before: `4daa38d`, `de8e95e` | 4.1 |
| 3c. a record path in a comment read as a dependency | done before: `467b52f`, `739c117`; measured | 4.2 |
| 3d. the mutation scan and API replacement | done before: `d618fc8`, `7cec6dd` | 4.3 |
| 3e. `scripts/_check_jobs_gap_directions.py` | done before: deleted in `98e1937` | 4.4 |
| 3f. a failed navigation's error and its address | done before: `3e6fb24` | 4.5 |
| 4. five non-ASCII characters in `network.md` | left: nothing reads that slice as ASCII | 5 |

## 1. The asserted-names check: green, and the checker untouched

`scripts/check_asserted_names_resolve.py` exited 1 at 3c8edc2 on eight sites
(seven pairs of name and document; one name twice). Its test,
`tests/test_an_asserted_name_resolves.py`, pinned exactly those eight as a
two-way ratchet, so CI was green while the script was red: every new finding
was hidden behind eight old ones that nobody acted on.

THE EIGHT, AND WHAT EACH WAS. Five were one shape: a slot phrase ("under")
ending a line and a backticked id opening the next, which the guard has
convicted since the wrap join of 2026-09-23. None of the five names is a
blocker. Four are registered ruling ids, one a census state word:

    record                                     name                                kind
    2026-09-20-the-premium-block.md            EXCLUDED-RULED                      census state
    2026-09-21-the-auth-reason-leak.md         ERROR-URL-ASKED-FOR-OR-NOTHING      ruling
    2026-09-23-bucket1-fires.md                NO-IRREVERSIBLE-WRITE-IS-FIRED      ruling
    2026-09-23-census-cleanup.md               SELF-PROFILE-EDITS-NOT-OUTWARD      ruling
    2026-09-23-lane-l1-refused-reads.md        ONE-NAMED-SETTINGS-PAGE-AT-A-TIME   ruling

The other three sites sit in `_audit/2026-09-20-the-contingent-writeoffs.md`:
replacement cells it proposed for `J 37` (one name) and for `J 40` and `J 57`
(one name, twice). Neither name was ever minted. The record's own header
already said the re-file was deferred, but it never named either, so a reader
who met a replacement cell met a confident name and nothing else.

THE REPAIR, IN THE RECORDS. The five name their kind before the id: "under
the ruling" four times, "in the state" once. The phrase no longer ends the
line, so the id is no longer in the guard's slot, and the sentence now says
what the id is. The contingent record gains a note beside each of its three
proposals, dated and signed: the name was proposed there and never minted,
it does not exist in the blocker ledger, and where the row went instead
(`J 37` never split and stands GAP; `J 40` built and fired live on
2026-09-21, COVERED-PROVEN; `J 57` GAP). The guard reads that sentence as the
disclosure it already knows, so the three sites read `MARKED-ABSENT`. The
blocker map was re-derived over the edited records and did not move.

THE CHECKER WAS NOT TOUCHED. Its pin was emptied, which the ratchet itself
demands on a repair: `PINNED` is now the empty set, with the eight sites
and their fates kept in a comment beside it, so any asserted-and-absent name
is a red from here on.

RED FIRST. The emptied pin, run against the six records as they were at
3c8edc2: 1 failed, 11 passed, the failure naming all eight sites. Against
the repaired records: 12 passed. The script: exit 1 with 94 candidate sites
and 8 findings before; exit 0 with 89 candidate sites, 89 cleared, 0 findings
after (the five reworded sites left the slot; the three disclosed ones stayed
candidates and are cleared by their disclosure, not dropped).

STILL FAILING ON A PLANTED DEFECT, after the repair. Two lines appended to a
tracked record and removed before any commit: a fabricated name in the
`blocker` slot, and a real ruling id wrapped after a bare "under" -- the shape
the five reworded sites had. The script exited 1 and named both, each
`ASSERTED-ABSENT`; with the plants removed it exited 0. So the shape the five
records left is still convicted wherever it is written.

The two names, said once more so this record cannot be read as asserting
them: `ALERTS-PAGE-UNREAD` and `PROXIMITY-NOT-PARSED` do not exist in the
blocker ledger; each was a proposal of the contingent-writeoffs record.

## 2. Earned-clean: a success path leaves something the page made

THE QUEUED ITEM'S FIRST INSTANCE LANDED BEFORE: lane G's rules of 2026-09-27
(`041903b`, `0a7e496`) made clean need a read, a result that is not empty, and
for a reader that builds people records, a record; `d0d2f0b` drove lane S's
`people_results.read_result_people` to its records. The tree was checked for
the general class, and it was still open.

MEASURED FIRST, over the 97 readers the baseline recorded clean, by driving
each signature variant twice -- on the planted page, as the guard does, and on
a page that draws nothing -- and asking what in the planted result the page
made. 17 had nothing, and were clean on what they hand back whatever a page
draws:

    7  script readers whose every value the planted page answered was refused,
       so the only number not zero was the refusal tally: anchors.read_anchors
       (the guard's own control for "clean is earned"), collections_page,
       company_root, group_page, and the three search readers behind
       linkedin_people_search_shape -- read_results, read_filters and
       read_filters_when_settled, the last adding the poll budget of a panel
       that never settled
    8  readers that returned their own refusal sentence or an "unknown", the
       same over the blank page: dom.read_radio_label_binding,
       profile_editor.read_save_gate, server._open_profile_views_filter_menus,
       writes._editor_value_of, and the four tracker and follow state readers
    1  press._take_reading, whose only value was its failure's name
       ({"read": False, "unreadable": "ValueError"})
    1  dom.read_sdui_actions, which raises over a page that draws nothing, so
       nothing can show which of its values the page made

So the people search's readers were clean without ever reaching their
success path, which is the queued item's class.

THE FIRST NULL WAS UNFAITHFUL, and the measurement said so: a blank page whose
waits returned at once read seven wait readers as "attached" on both pages and
would have convicted them for the double's fault. The blank page now raises
`TimeoutError` on every wait, as Playwright does on a page that never draws
the thing; those seven keep clean on what they waited for.

THE RULE (`tests/test_readers_emit_no_page_string.py`, `page_evidence` and
`NOTHING_FROM_THE_PAGE`; the null is `tests/plantedpage.py`'s `BlankPage`). A
signature drive that would be clean is run again over `BlankPage`. A value is
evidence when it is a scalar, is not empty, sits under no refusal or failure
key (`NOT_EVIDENCE_KEY`: refus, error, fail, unreadable), and differs in value
or type from the blank drive's value at the same place. No evidence, or a
blank drive that raises, times out or acts, is
`not_driven:read the page and returned nothing the page made`. Curated drives
(`AS_SHIPPED`, over tracked fixtures) are not compared: their own tests hold
each one's premise and outcome.

RED FIRST, three ways, on the guard as it was:
`test_a_reader_that_returns_before_its_success_path_is_not_clean` -- a stub
dressed as `item_addresses.read_item_addresses` that reads the page and then
returns its own sentence and constants, or only a refusal tally -- 2 failed,
each `('clean', '2 read(s)')`; the coverage comparison against the committed
baseline failed naming the 17; the holding test failed naming 17 untriaged.
After: the stubs read `NOTHING_FROM_THE_PAGE`; the baseline, regenerated by
its own writer, moved exactly those 17 and nothing else (clean 97 -> 80, not
driven 33 -> 50). The pure rule has its own table
(`test_a_clean_drive_shows_something_the_page_made`, 13 rows), and the null
its own fidelity test (`test_the_blank_page_draws_nothing_and_its_waits_run_out`).

THE GUARD'S OWN CONTROL WAS RE-AIMED. `test_a_reader_stubbed_to_return_early_is_not_counted_clean`
used `anchors.read_anchors` as the reader that earns clean, and it never had;
it now uses `item_addresses.read_item_addresses`, whose hrefs the blank page
cannot match.

EVERY MOVED READER SAYS WHAT WOULD DRIVE IT. The holding test requires a drive
or an entry in `WHAT_WOULD_DRIVE_IT`, and the seventeen entries use two new
kinds besides the old ones. A child of this lane drafted sixteen from the
source, the fixtures and the tests, read-only; each was reviewed here, every
cited test, fixture and symbol checked to resolve, and three re-kinded:

    SCRIPT  11  its reading is a script this package runs in the page, which
                the planted page answers with strings: the seven script
                readers, press._take_reading, dom.read_sdui_actions,
                profile_editor.read_save_gate, writes._editor_value_of --
                each names the test that drives its success path, over a
                fake answering the script's shape or in a headless browser
                over a tracked fixture, or says that none does
    WORDS    3  its success path keys on LinkedIn's own words in the page's
                text (a tab strip), which the planted page can only answer
                with the plant: the three tracker-state readers; a tracked
                capture draws them, and a drive over it is buildable, not built
    ACTION   1  server._open_profile_views_filter_menus, whose success path
                presses the filter pills
    RULING   2  dom.read_radio_label_binding and writes._read_followed_state,
                whose success paths return page text outside a record
                (section 6, item 1)

THE OLD CLEAN WAS HIDING TWO TEXT PATHS. The RULING pair is the class lane
G's ruling of 2026-09-28 met in four readers: page text on a success path no
drive reached. One of them was measured here directly: driven with a role its
selector builder admits, `read_radio_label_binding` returns `returns_text` at
`$.why`, the control's id quoted in its own sentence.

## 3. Item 3a: a post record

`linkedin_server/people_data.py` declares `Post`: the author as a `Person`
record (by identity: a subclass could carry a field never declared), the
permalink in `canonical_post_link`'s form, and the words sanitised and capped
at `CAPS["text"]`, 3,000, LinkedIn's own limit for a post -- `ABSENT` where a
reader read none, as a person's headline is. `canonical_post_link` keeps only
`https://www.linkedin.com/feed/update/urn:li:<activity|share|ugcPost>:<id>/`:
a query, a fragment and a sub-page are dropped, and the vanity form, whose
path is the author's slug and the post's own words, is reduced to its urn. A
post with no member author gets no record. Registered with the others:
`RECORD_TYPES`, `POST_SHAPE`, `TEXT_FIELDS` (`text`), `as_record` (which takes
the author only as its own envelope, so an instance or a bent author leaves
the post a plain dict for the page-string guards to walk) and `text_fields`.
The untrusted note now says "their posts" too.

RED FIRST: 26 new tests in `tests/test_people_data.py` failed on the missing
record; after, the file passed (106). Two registries outside the module
named the record classes by hand: the pinned set in
`tests/test_a_name_enters_a_shaper_only_as_a_record.py`, and
`RECORD_CLASSES` in `tests/test_a_people_reader_reads_one_page.py`, by which
the bounded-reader guard finds a reader that builds records -- so a reader
building a post would have been invisible to it. A new test holds
`RECORD_CLASSES` equal to `people_data.RECORD_TYPES`; it failed on `Post`
first, as did the pin.

NOT ADOPTED, AND NO ROW MOVES: no reader builds a post and no tool returns
one. Row `M C70` waited on the post's declared fields; what it still waits on
is where LinkedIn searches inside a group and an admission for that address.
Its cell is not edited here, because lane A is working the refused read rows
in parallel and this row is one of them; its next editor can name
`people_data.Post` there.

## 4. Done before this lane, each checked against the tree

### 4.1 Item 3b: the root-logger captures that could not fail

Landed in `4daa38d` (21 sites lower the `linkedin` logger as well as the
root, each first proving a DEBUG control record is heard; the handler that
raised `NameError` logs) and `de8e95e` (the guard that keeps the shape found:
`tests/test_a_debug_capture_lowers_the_package_logger.py`). The lane G record
gives the red runs: each of the 12 named sites passed with its forbidden
value planted in a DEBUG record, and went red once fixed. Both commits are
ancestors of 3c8edc2, and the guard ran in CI run 36460989178, green.

### 4.2 Item 3c: a record path in a comment

The analyser strips comments and docstrings before matching a data path, in
every candidate file, since the gate's first build (`467b52f`, `code_text`);
and in the package it reads a sentence-valued string as a citation since
`739c117` (`without_sentences`), which is what had coupled lane L5's record to
95 test files -- the premise "a comment" was half right when it was queued.
The read map cannot do it either: it records files a test OPENED, and a
comment opens nothing.

MEASURED HERE, by a scratch probe (disposable): over 260 tracked `_audit`
basenames and the analyser's 603 python candidate files, 178 (record, file)
pairs mention the record only inside `#` comments; 0 of them survive into the
text the analyser matches (`Corpus.data`). The control, the same 178 read
with comments kept, matches all 178.

### 4.3 Item 3d: the mutation scan and API replacement

Landed in `d618fc8` (`scan_js_for_mutations` reports `API replacement` for an
assignment or `delete` on a member reached from a browser global, any
`.prototype` member, `Object.defineProperty` and its relatives, and
`Object.assign` onto a global; 13 plants each red before it) and in the
integration merge `7cec6dd` (`readonly.SANCTIONED_API_REPLACEMENTS`: the live
lane's clipboard script declared with exactly its seven replacements, and an
undeclared script with the same shape refused). Both are ancestors of
3c8edc2; the tests are in `tests/test_readonly.py`
(`test_the_js_scanner_catches_an_api_replacement`,
`test_a_replacement_the_list_does_not_declare_is_still_refused`).

### 4.4 Item 3e: `scripts/_check_jobs_gap_directions.py`

Deleted in `98e1937`, on evidence its message records: nothing ran it, it
crashed on its own run, and its successor `scripts/check_jobs_directions.py`
covers every still-GAP jobs row. It is not on disk at 3c8edc2. Nothing here
wires it back.

### 4.5 Item 3f: a failed navigation's error

Landed in `3e6fb24`: `LinkedInBrowser.goto` raises
`BrowserUnavailableError` naming the exception's type and the address's
first path segment, never the address or the library's message, with the
original chained in-process; red test
`tests/test_a_failed_navigation_withholds_its_address.py`. Checked here for
another path: browser.py's other raises concern starting and attaching, not
a navigation; the people search's own refusal (`people_search.refusal_envelope`)
quotes no value; and the read door's refusals in `readonly.py` quote the
address this server composed, which `ERROR-MESSAGE-RULED-AT-THE-RAISE` makes
publishable (the package's own text) and which is the address it asked for.

## 5. Item 4: the five non-ASCII characters in `network.md`

Left as they are: four em dashes and one arrow in the prose of the
reconciliation paragraph (lines 109-136, written in `762ec23`, 2026-09-21),
outside every table row, and nothing in the repository reads a census slice
as ASCII. The strict ASCII reads are on the TSV tables and on fixtures; every
census instrument and derived-view check ran green over this slice here
(section 7), and CI has been green with these characters since 2026-09-21.

## 6. Open, for other owners and for the orchestrator

1. TWO READERS' SUCCESS PATHS RETURN PAGE TEXT OUTSIDE A RECORD, hidden until
   now because the old rule called their early return clean (held in
   `WHAT_WOULD_DRIVE_IT` under RULING). `dom.read_radio_label_binding`,
   handed a role its selector builder admits ("radio", as
   `writes._live_control` passes it), reaches its success path on the planted
   page alone and returns the control's `id` attribute verbatim, in
   `observed.input_id`, `observed.label_for` and inside its `why` sentence --
   measured here, `returns_text` at `$.why`. `writes._read_followed_state`'s
   success path returns the followed Page's name in its facts (`company`).
   Each needs the orchestrator's call: admit to the text inventory, with a
   reason, or convert (publish whether the binding holds; publish the Page
   by its id).
2. `writes._editor_value_of`, driven over the tracked intro editor, would
   return his field's value verbatim, as its sibling
   `writes:_editor_values_or_refusal` does under `ADMITTED_TEXT` (his own);
   a drive for it would need the same admission.
3. FOUR SCRIPT READERS ARE RUN BY NO TEST IN ANY ENGINE: `anchors.read_anchors`,
   `collections_page.read_collections`, `company_root.read_company_root`
   (its script runs under node in a test, its reader does not) and
   `group_page.read_group_page`. Their success paths run only in
   attach-only live probes. A headless drive over a tracked capture (the live
   lane's `group_home` skeleton, for two of them) is each one's cheapest next
   step.
4. THE FULL SUITE should run on CI for this branch before it merges:
   `linkedin_server/people_data.py` is imported by the server module and so
   by most of the suite, and the local gates here were scoped by policy.
5. ROW `M C70`'s cell can name `people_data.Post` when its owner next edits
   it (section 3).

## 7. Gates run, and what did not run

Every run is local, on Windows, serial while the live session's flag
existed (until about 12:00) and sharded `-n 4 --dist loadfile` after; under
the orchestrator's gate policy of 11:35 none is the full suite.

    item 1   the asserted-name test, red then green      1 failed 11 passed; 12 passed
             the records' readers and the derived views  293 passed (155 s)
             the document guards over this record        125 passed
             the committed-identity sweep after the commit 1044 passed
             the census instruments and derived views     all green: census_completion
                                                          ("every headline figure matches
                                                          its pin"), write classes 389,
                                                          read addresses 98 of 98, jobs
                                                          directions 108 of 108, ruling
                                                          holds, the three --check views
    item 3a  the post tests, red then green              26 failed; 108 passed
             people_data's direct importers and the      1280 passed, 1 xfailed (the
               orphan-module test, sharded, 29 files      declared people-search limit),
                                                          1041 s on a box running seven
                                                          other lanes' suites
             the committed-identity sweep after the commit 1044 passed
    item 2   the new controls, red then green            2 failed; 38 passed
             the coverage and holding tests on the old
               baseline                                  2 failed, naming the 17
             the guard's file and plantedpage's other    8 failed, 1188 passed: the
               direct importers, sharded                  eight were curated drives a
                                                          test calls directly, with the
                                                          comparison on; marked not
                                                          compared, as drive() treats
                                                          them -- 35 passed
             the guard's can-fail scripts                coercion PASS (4 of 80 clean
                                                          readers red under the shipped
                                                          int(), green on its removal);
                                                          refusing grant PASS (5 of 5)

THE COERCION SCRIPT'S SAMPLE SHRANK, AND THE GUARD DID NOT LOSE THE LEAK. It
samples only readers recorded clean, and lane G recorded 15 of 88 red there;
the readers the planted page drives into their coercions are exactly the ones
that never reach their success path, so they left its sample. Measured with
the same plant over the 17 moved readers, by a scratch probe: 9 read `leaks`,
because a leak outranks every not-driven verdict in `drive()`, and
`test_no_reader_carries_a_page_string_out` asserts no leak for every reader,
driven or not.
