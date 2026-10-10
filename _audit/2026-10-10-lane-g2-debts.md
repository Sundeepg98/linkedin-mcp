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
| 1. the asserted-names check, red on 8 sites | fixed in its records; red test shown | 1 |
| 2. earned-clean, the people-search readers | in progress | 2 |
| 3a. a post record in `people_data.py` | in progress | 3 |
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
(section 6), and CI has been green with these characters since 2026-09-21.
