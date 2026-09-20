# The unfired twenty-seven

**Wave 38. Written as the wave ran, not at its end.**

The census carries 27 rows as `COVERED-UNFIRED` -- jobs 7, profile 7, messaging
7, network 6 -- plus 8 more in `jobs.md`'s short spelling `CU`, which the
shipped counter reports under its own key. Thirty-five rows in all.
`COVERED-UNFIRED` means the tool SHIPS and has never been fired to prove it
works, which makes these the cheapest coverage movement in the census: no
building, only firing.

This is the reading. It is deliberately shorter on banked rows than the
arithmetic allows, and every subtraction is stated with its measurement.

## 0. THE ROUTE, AND PROVING WHICH CODE RAN

The `linkedin` MCP server refused connection to this session. A server process
IS alive and listening on `127.0.0.1:8322`, but **a running MCP server holds
the code it started with**, so anything fired through it is not necessarily the
code on disk. Nothing in this wave went through it.

Everything here was fired through the **direct CDP attach path**, in-process,
importing `linkedin_server` from this worktree. The provenance is printed by
every probe before it touches the browser:

    linkedin_server package file: <this worktree>/linkedin_server/__init__.py
    git HEAD: e6b11e5 (this wave's base)
    CDP_ATTACH: True     CDP endpoint port: 9224

**ATTACH, NEVER LAUNCH.** A Chrome was already running on the persistent
profile. Playwright's bundled chromium is a full major version behind that
profile, so a LAUNCH would run Chrome's downgrade migration and throw the
signed-in session away. Nothing in this wave launched a browser.

## 1. THE THIRTY-FIVE ROWS, CLASSIFIED BEFORE ANY WERE FIRED

The split that governs everything below is **read vs write**, because a row
whose capability is inherently a write CANNOT be fired against a real
professional identity and is not a candidate for banking at any price.

| class | count | rows |
|---|---|---|
| READ -- fireable in principle | 19 | J 2, 4, 5, 6, 7, 10, 24, 26, 27, 121, 122, 151; P K10; M M33, M43, M45, C41; N 20, 45 |
| WRITE -- cannot be fired, ever | 15 | J 103, 104, 128; P A8, A11, A13, A17, A19, A21; M C1, C25, C32; N 1, 46, 48 |
| READ but no input exists | 1 | N A6 |

Of the **27 `COVERED-UNFIRED`** rows specifically: 14 are reads, 13 are writes
or have no input. **So the honest ceiling on this wave was never 27.**

## 2. THE DEADLOCK THAT HAD TO BE FOUND FIRST

`BROWSER.session()` holds a **single-flight lock for the whole of its body**,
and every shipped tool opens a session of its own. A probe that holds a session
and then calls a shipped tool deadlocks -- measured twice here as a silent hang
indistinguishable from a slow page load.

**Anything firing a shipped tool must own no session at the moment it does so.**
Every probe in this wave is therefore three phases: our session for the control
and the opening badge, NO session while the shipped tools run, our session
again for the closing readings.

## 3. THE FIRST CLUSTER: SIX ROWS, ONE READER, FOUR BANKED

`J 24`, `J 26`, `J 27`, `J 121`, `J 122` and `P K10` all describe fields
emitted by ONE reader, `dom.read_job_insight_panels`, reached through ONE tool,
`linkedin_job_detail`. Every one was banked `COVERED-UNFIRED` on a SOURCE
trace -- the field is emitted, therefore it reaches a caller. True about the
tree, and not a fire.

Verified first by AST parse rather than grep, because a field-name grep cannot
see a dict that passes through by reference: the reader's return dict holds
exactly seven keys -- `applicant_insights`, `company_insights`, `promoted`,
`responses_managed_off_linkedin`, `verified_job`, `more_behind_a_control`,
`observed`.

Fired by `scripts/_probe_unfired_job_detail_insights.py` over **11 live
postings** harvested through the shipped search tool.

### THE DISTINCTION THAT DECIDED IT

**A FIELD THAT IS PRESENT IS NOT A FIELD THAT WORKS.** `verified_job` is
`bool(markers.get("verified"))`; a reader with a broken selector returns False
for every posting on earth and is indistinguishable from a correct reader over
a sample of unverified jobs. So each boolean is reported as a THREE-WAY tally,
and only a field observed BOTH true and false has proved it discriminates.

| field | true | false | verdict | row |
|---|---|---|---|---|
| `promoted` | 9 | 2 | OBSERVED-BOTH | J 26 |
| `verified_job` | 5 | 6 | OBSERVED-BOTH | J 27, P K10 |
| `responses_managed_off_linkedin` | 5 | 6 | OBSERVED-BOTH | J 24 |

All three discriminate. **J 24, J 26, J 27 and P K10 are banked.**

### THE TWO THAT ARE NOT BANKED, AND WHY

`applicant_insights` arrived on 11 of 11 -- and that is NOT evidence for the
rows as written. The panel carries `heading`, `metrics`, `seniority`,
`education`. Measured over all 11 postings:

    percentile   0 of 11
    rank         0 of 11
    skill        0 of 11
    %           11 of 11        (the seniority and education splits)
    postings drawing "Show Premium Insights":  7 of 11

* **`J 121` -- your ranking percentile vs other applicants. NOT DELIVERED.**
  No percentile and no rank token appears in any panel; `metrics` carries
  applicant COUNTS. The percentile sits behind the gated control counted above,
  which this reader does not open. **Stays COVERED-UNFIRED.**
* **`J 122` -- top skills among applicants, experience/education levels.
  PARTIAL.** The experience/education half arrives, with percentage splits.
  The "top skills" half does not: zero skills tokens in 11 panels.
  **Stays COVERED-UNFIRED.**

A probe that reported only "the panel arrived" would have banked both on
evidence for neither.

## 4. THE BADGE INSTRUMENT WAS WRONG, AND IT SHOUTED

This repo requires `dom.read_invitation_badge` before and after any live read,
to prove a read did not consume a counter it passed. This probe's FIRST version
compared `len(str(reading))` -- the character length of the whole dict's repr --
and on the n=4 run reported:

    invitation badge BEFORE: a reading of 60 characters
    invitation badge AFTER:  a reading of 89 characters
    CONSUMPTION: THE BADGE MOVED. Something was spent.

**That was a false alarm produced by a crude instrument.** The reader returns
`{links, badge_links, label, error}` and leaves `label` None whenever the nav
has not hydrated or draws a number of badge links other than one. An unhydrated
first read followed by a hydrated second read lengthens the repr by exactly the
label -- and reads as a spend, on a run that opened four job postings and could
not have consumed an invitation.

Replaced with a structured comparison that reports UNKNOWN unless BOTH ends are
readable. On the n=11 run it reports, correctly:

    badge BEFORE: UNREADABLE (badge_links is not exactly 1)  (links=1, badge links=0)
    badge AFTER:  READABLE                                   (links=1, badge links=1)
    CONSUMPTION: UNKNOWN -- one end could not be read, so this says nothing
                 rather than saying nothing was spent

## 5. THE SECOND CLUSTER: SEVEN JOB-SEARCH FILTERS, ALL SEVEN BANKED

`J 2`, `J 4`, `J 5`, `J 6`, `J 7`, `J 10` and `J 151`. Every one had been
banked UNFIRED on the strength of a CONSTANT -- the code holds `f_TPR` and four
values, therefore the filter exists. A fact about this repository, silent about
LinkedIn.

Fired by `scripts/_probe_unfired_job_search_filters.py`.

### THE MEASURE IS DISCRIMINATION, AND THE NUMBERS SHOW WHY

**Every filter value returned exactly 7 rows** -- the measured per-page window.
So "the search responded" and "the search returned results" discriminate
NOTHING here: a parameter LinkedIn ignores, or one appended to the wrong query
key, returns a perfectly healthy set of 7 that is simply the unfiltered one.

The probe therefore compares the returned JOB ID SETS across every permitted
value. And because LinkedIn reshuffles its own results between two identical
requests, the baseline query is fired TWICE back to back first, to establish a
DRIFT FLOOR that every verdict is judged against.

    DRIFT FLOOR, main run:  2 of 7 ids
    DRIFT FLOOR, J 7 re-fire an hour later:  0

**THAT THRESHOLD IS QUOTED WITH ITS SESSION ON PURPOSE.** The same quantity
measured 2 and then 0 within an hour. A drift floor taken once and carried
forever would quietly become a property of the friendliest session.

| row | filter | result | verdict |
|---|---|---|---|
| J 2 | boolean operators | 5 distinct id sets, widest disagreement 12 | DISCRIMINATES |
| J 4 | `f_TPR`, 4 values | 3 distinct id sets, widest 12 | DISCRIMINATES |
| J 5 | `f_WT`, 4 values | 4 distinct id sets, widest 14 | DISCRIMINATES |
| J 6 | `f_E`, 6 values | 6 distinct id sets, widest 14 | DISCRIMINATES |
| J 7 | `sortBy=DD` | 2 FULLY DISJOINT sets, 14 of 14, drift floor 0 | DISCRIMINATES |
| J 10 | `f_C` | filtered vs unfiltered overlap only 1 of 7 | DISCRIMINATES |
| J 151 | multi-location | 2 searches, 12 rows, 12 ids, 2 distinct `found_in` | DISCRIMINATES |

**All seven banked.** `J 10`'s company id was not typed in: it was RESOLVED off
a real posting by the shipped `linkedin_job_detail` and fed back to the search
tool, so the row's whole chain fired end to end.

### THE ONE THAT LOOKED LIKE A SERVER BUG AND WAS MY ERROR

`J 7`'s first run reported `sort_by="recent"` returning **zero rows**, against
`relevance` returning 7. That reads as a defect in the shipped code, and it is
not one. **The permitted values are `relevance` and `date`**; `recent` is
LinkedIn's UI label, which the census row is worded in. The tool refused the
argument correctly and `_ids()` returned that refusal as an empty set --
indistinguishable from "LinkedIn served nothing."

**The argument was wrong, the server was right, and the instrument could not
say so.** `_ids()` now announces an argument refusal distinctly. Re-fired with
`date`, the row banks on the strongest result in the whole table.

## 6. THE THIRD CLUSTER: TWO SELF-READS, ONE BANKED

Fired by `scripts/_probe_unfired_self_reads.py`.

* **`M M45` -- open a blank compose window. BANKED.**
  `linkedin_compose_fields` RETURNED rather than refused:
  `recipients_selected` **0** -- the composer is empty, which is the guard's
  own precondition -- `pages_loaded` **1**, **exactly 2 dispatch modes with
  exactly 1 checked**, and a body editor reporting `present` / `is_editable` /
  `name_source`. That is the exact shape the tool documents itself as requiring
  before it will report anything. The 2026-09-02 run that returned
  `refused: name_shaped_label_present` is superseded. Nothing was typed and
  nothing was dispatched.

* **`M C41` -- view your own activity feed. STILL REFUSES. NOT BANKED.**
  `linkedin_my_activity_items` refused with `self_assertion_unreadable` --
  *the landed profile url carried no isSelfProfile parameter at all, on 2
  attempt(s)* -- after one page load. That is a THIRD distinct refusal reason
  for this tool, alongside the recorded `no_page_owner_heading` and
  `no_self_assertion`. **It has still never returned an item.** A tool that
  ships expecting to refuse is not banked by refusing again.

## 7. `N A6` -- FIRED OFFLINE, AND MOVED TO CANNOT-DELIVER

`linkedin_page_plugin_snippet` was the one tool here that needed no browser:
its body is `page_plugin.follow_plugin_snippet(page_id)`, that module imports
nothing that can reach a network, and the function is a plain `def`.

Fired three times, and it DISCRIMINATES:

    synthetic all-digits id  ->  refused None,               html 177 chars, carries the id
    "not-a-page-id"          ->  refused not_ascii_digits,   html 0 chars
    ""                       ->  refused not_ascii_digits,   html 0 chars

Its refusal reports a SHAPE (`saw`: length band, ascii-digit count, letter
count, looks-like-a-url) and never echoes the value it rejected.

**So the builder is proven and the capability still cannot be delivered.** The
row is about *your organization's* Page and no organization Page id exists to
build one from -- an absent INPUT, not a code gap. The state now matches the
reason the row already gave. Separately the tool reports `verified_live: False`:
no snippet it has built has ever been confirmed working on a live page.

## 8. FOUR ROWS NOT FIRED, BECAUSE THE COST LANDS ON SOMEBODY ELSE

`N 20`, `N 45`, `M M33` and `M M43` are READ-ONLY by this codebase's write-gate
classification: no `_write_tool` call, no `confirm_token` parameter, and absent
from the server's own twelve-name write list. **They were still not fired.**

* `linkedin_notifications` loads `/notifications/`, which CLEARS THE UNREAD
  BADGE. Its own docstring: *"this is the only server-side change any READ in
  this package causes WITHOUT BEING ASKED FOR IT."*
* `linkedin_open_messaging` opens a LinkedIn-chosen conversation thread and may
  reset the messaging badge. `_audit/2026-08-30-linkedin-writes.md` already
  declined it in as many words: *"The cost lands on somebody who is not him, so
  it is his to spend."*

**READ-ONLY BY THE GATE IS NOT THE SAME AS FREE.** A tool that destroys
information the operator holds -- which notifications he has not yet seen -- is
spending something, whatever the classifier says. That reasoning had not
expired, and a second wave spending it quietly would be worse than the first
declining it loudly.

## 9. THE EVIDENCE-REACHABILITY AUDIT, WITH ITS CRITERION ATTACHED

Measured over all 35 rows by reusing the shipped parser in
`scripts/count_census_states.py` rather than writing a second one. The row
count was reproduced independently: 35, split jobs 15 (7 long-form + 8 `CU`),
profile 7, messaging 7, network 6.

    unique paths cited across the 35 rows                       9
    rows citing at least one path in the audit/scripts/tests/
      linkedin_server namespace                                 5 of 35
    rows whose cited paths are ALL tracked                      3 of 35
    rows whose evidence chain ends in a MISSING file            2 of 35
    git ls-files _audit/_scratch/                               0

**THE TWO DEAD ENDS ARE `J 27` AND `J 151`**, both citing an
`_audit/_scratch/` file. That directory is gitignored, nothing in it is
tracked, and a worktree does not carry it -- so those numbers were stated in a
row and checkable nowhere. Both rows were banked by this wave on FIRED evidence
that replaces the dead reference, and both cells now say so.

**THE 30-OF-35 FIGURE NEEDS ITS CRITERION OR IT WILL BE MISREAD, so here it
is.** Those 30 rows cite no path inside that four-prefix namespace. That is NOT
the same as having unreachable evidence: many cite a bare `server.py:1189` or
`dom.py:8309-8314`, which a reader CAN resolve with mild effort. **An imprecise
citation is a different defect from a missing file**, and collapsing the two
would overstate the problem by an order of magnitude. Only 2 rows are dead
ends.

Line-number citations carry their own rot, and it bit here: several rows cite
`server.py:3410` for `linkedin_job_detail`, which sits at **4008** at this
HEAD, with the insights assignment at 4290. A line citation does not dangle --
it degrades into a plausible wrong answer, which stops a reader instead of
sending them looking. **Every evidence cell this wave wrote cites SYMBOLS**
(`server._search_url`, `jobfilter.company_filter_param`,
`page_plugin.follow_plugin_snippet`), and the six insight fields were verified
by AST parse of the reader's return dict rather than by grep -- a field-name
grep returns ZERO for a dict passed through by reference and reads exactly like
a dead field.

## 10. THE LEDGER

| state | before | after |
|---|---|---|
| COVERED-PROVEN | 39 | **51** |
| COVERED-UNFIRED | 27 | **19** |
| `CU` (short form) | 8 | **3** |
| COVERED-CANNOT-DELIVER | 15 | **16** |
| GAP | 300 | 300 |
| stated rows | 704 | 704 |

**12 rows banked, 1 moved to CANNOT-DELIVER, 3 fired and deliberately NOT
banked, 4 deliberately not fired, 15 inherently unfireable writes.**

The arithmetic reconciles: 12 banked = 7 from the long-form 27 plus 5 from the
short-form `CU` 8; COVERED-UNFIRED falls by 8 because `N A6` also left it.
GAP and the row total are untouched, which is the check that nothing was
quietly reclassified to make a number move.

## 11. WHAT A LATER READER SHOULD RE-RUN

Every figure above is re-derivable. The three probes are tracked in `scripts/`
and each re-harvests its own inputs from a live search, so none depends on a
gitignored capture:

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 LINKEDIN_CDP_ATTACH_TIMEOUT_MS=90000 \
        ./venv/Scripts/python.exe scripts/_probe_unfired_job_detail_insights.py 12
    ... scripts/_probe_unfired_job_search_filters.py
    ... scripts/_probe_unfired_self_reads.py

**RAISE THE ATTACH TIMEOUT OR THE ATTACH WILL FAIL AND BLAME CHROME.** Measured
this wave: `connect_over_cdp` reports `<ws connected>` and then times out at
the 15000ms default, because the handshake enumerates every target and the
shared browser was carrying 56. The attach that finally succeeded took **93
seconds**. Three tabs this wave's own aborted runs had leaked were closed BY
TARGET ID -- never by killing a browser image, which would reach the operator's
own Chrome running in a separate process tree on a different profile.

The controls are `tests/test_unfired_probe_verdicts.py`, 13 tests, run with:

    ./venv/Scripts/python.exe -m pytest tests/test_unfired_probe_verdicts.py -q
