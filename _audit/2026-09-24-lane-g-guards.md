claude-opus-5-5[1m]

# Lane G -- security guard hardening: four measured gaps in the checks that keep page text out and page choice out of navigation

Branch `worktree-agent-a31f0ad625f238c58`, cut from `master` at `9c219c8`. Nothing
here went live: no LinkedIn, no browser session, no port 9224. The only browser
this lane started is the suite's own offline headless page over committed
fixtures.

**THIS LANE'S HASHES RESOLVE ONLY ON ITS BRANCH UNTIL IT MERGES.** They are
listed once, in section 6, beside their subjects; no other sentence here cites
one.

## 0. Status log

EVERY TIME HERE IS A READING: the first from `date` at the start, the rest the
commits' own times from `git log`, and the gate's from the process table. An
earlier draft of this log carried times estimated from inside the work, one of
them later than the clock when it was written.

    00:30  worktree clean at 9c219c8; the four gaps read off their source records
    01:08  (b) and (c) committed -- (c)'s slot measurement by an implementer child
    01:12  (d) committed -- built by an implementer child, reviewed here; the
           blocker map regenerated with the fix: 0 lines moved
    01:49  (a) committed -- red run 24 readers laundering, 5 after
    01:57  record, register section 67, generated files at a fixpoint
    01:58  impact gate launched; killed at 02:28:34 by this lane's own 30-minute
           timeout, WITHOUT a verdict, while a sibling lane's full-suite gate ran
           beside it -- see section 6.1
    02:33  the navigation guard's limits restated from a re-measurement; this
           log's times replaced by readings
    02:34  impact gate run 2 launched, after the older sibling gate exited
    03:16  gate run 2 REFUSED on one test (the 250 ms readiness race, section 5
           item 6); the cold verification pass had reported 11 of 11 by then
    03:22  that test's module, run alone while other lanes' suites ran: the same
           red, `1_no_listbox`
    --     master moved to 001f70b while this lane ran (other lanes merging);
           this lane's gates stay --against 9c219c8, as briefed

## 1. (a) PAGE TEXT IN ERROR FIELDS -- THE FIELD NOW CARRIES THE EXCEPTION'S TYPE

### 1.1 The census, re-measured rather than relayed

The brief relayed "13 readers, 4 gates". No disk record carries the 13, so it
was re-measured with an AST census of every `except ... as exc` in `dom.py`,
each use of the bound name classified by the statement it sits in (type-only
uses excluded):

    exception-text renders in dom.py                       69
      RAISE  (message + `from exc`)                         24   the twelve raise sites
      LOG    (logger calls)                                  30
      FIELD  returned `error`                                12
      FIELD  returned `why`                                   3
    FIELD renders: 15, in 11 readers

**THE TWELVE RAISE SITES ARE THE RULED ONES AND WERE NOT TOUCHED.**
`ERROR-MESSAGE-RULED-AT-THE-RAISE` declined making them type-only, and its source
(`_audit/2026-09-21-what-the-browser-said.md` section 3.2) names them: exactly the
twelve readers `scripts/_probe_dom_error_url_field.py` targets, each
`raise ExtractionFailedError(f"...: {type(exc).__name__}: {exc}")`. That decision is
about `$.message`. The FIELDS are a different channel -- a returned dict that write
gates print into their refusals -- and the ruling's own enforcement pattern is
the catch site (`press.disclose` is named in it). So there is no conflict to raise:
the fields are decided where the value enters them, and the raises keep their
ruled text.

The consumers, mapped by instrument over `writes.py`: the four gates the brief
named -- `_comment_submit_gate`, `_publish_submit_gate`, `_typeahead_gate`,
`_send_gate` -- each print a `dom.py` reader's `error` into `out['why']`; three more
functions carry the same fields onward (`_live_control`, `_verify_after`,
`_read_item_comment_box`); and `server._read_connection_rows` copies
`dom.read_recipient_ids`'s `error` into the connections census. Fixing at the
entry covers every one of them. (`company_page_follow_verdict` also carries an
`error` onward, but its only reader, `dom.read_company_page_follow`, renders no
exception text -- and it never laundered in the run below.)

### 1.2 The repair

* **14 of the 15 field renders now write `type(exc).__name__`**, one line each,
  in `read_company_about_card` (2), `read_radio_label_binding` (2, keeping the
  caller's own `name`), `read_post_composer`, `read_sdui_actions`,
  `read_compose_fields`, `read_typeahead_options`, `read_recipient_ids`,
  `read_compose_send_state`, `read_comment_surface`, `read_thread_reply_surface`
  and `read_invitation_badge` (2). One comment block at the first site says why,
  and cites the ruling and the guard.
* **ONE IS KEPT AS TEXT, AND SAYS WHY.** `read_typeahead_options` narrowly catches
  `ExtractionFailedError` around `typeahead_option_selector(needle)`, a pure
  builder that reads no page. Its only two raises compose their own message
  (one refuses a needle carrying a quote, slash or backslash without quoting it;
  the other quotes a package constant). That is "a reason the package composed",
  and type-only would delete the most useful sentence the gate can print.
* **`writes._recipient_gate` rendered the text itself** -- it catches the ruled
  raise site in `dom.read_selected_recipients` and re-published that message in a
  gate refusal, a second channel for text the ruling had decided only for
  `$.message`. It now names the type, worded exactly like L4's `_typeahead_gate`
  repair beside it.

Every `dom.py` hunk is one line (plus the two comments); the live lane's edits
there stay mergeable line by line.

### 1.3 The guard -- a page whose every read fails

`tests/plantedpage.py` gains `RaisingPage` and `RaisingLocator`: every read
FAILS, with a distinct marker (`RAISED_PLANT`, not name-shaped, distinct from the
planted string) in the message; actions still refuse; the one timer still
returns. The failing methods are DERIVED from `PlantedPage`/`PlantedLocator`, so a
read added to the ordinary double tomorrow fails here the same day.

`tests/test_readers_emit_no_page_string.py` drives every discovered reader
against it. No read can return the marker, so a RETURNED value holding it holds
an exception's text, whatever the spelling. A RAISED exception is the ruled
channel and is recorded as `raises`, never failed. Controls: a synthetic reader
is convicted in five spellings (the dom shape, `str`, `repr`, `args`, `%`); the
type-only repair and a raise with the text are not; the double is shown failing
every read and refusing every action.

**SHOWN FAILING on the unrepaired tree: 24 readers laundered.** Ten in `dom.py`,
eight in `writes.py` (the four gates among them), `server._read_connection_rows`,
and five in modules this lane does not own. **After: those five, and no
others** -- declared in `KNOWN_LAUNDERERS` and asserted exactly in both
directions. Of 126 discovered readers, 78 returned under the failing page (73
clean, 5 launder); 47 raised; 1 not driven. 78 is the floor.

**ONE READER THE FAMILY CANNOT DISCRIMINATE, AND A CONTROL FOR IT.**
`read_radio_label_binding` read `clean` before AND after: the harness hands its
`role` the synthetic argument, `named_role_selector` refuses that before any read,
and the handler returns a package-composed message. Its one shipped caller passes
`"radio"`, so a targeted control drives it that way and asserts the handler was
reached through the library failure. Shown red with one original line restored
(`launders` at `$.why`), green after.

### 1.4 What the repair broke, and how each was mended

* `tests/test_the_unread_readings_were_never_driven.py`'s POSITIVE CONTROL used
  `read_company_about_card`'s `error` field as its proof that the instrument can
  see a leak -- the defect was its subject. It now drives the retired handler
  verbatim over the same double, and the repaired field has its own record
  (`error == "ValueError"`, no plant). 16 passed.
* `scripts/_check_the_unread_readings_guard_can_fail.py` blinded that control by
  making the field type-only -- now the shipped code, so it would have planted
  nothing (0 occurrences against an expected 11). Two mutations replace it: the
  repaired field regains the retired formula (14 exact occurrences), and
  `carries_the_plant` is blinded. **11 of 11 convictions**, every binding restored.

## 2. (b) THE NAVIGATION GUARD NOW SEES A VALUE A READER RETURNED

**THE GAP.** `tests/test_navigation_is_never_derived.py` tainted a `goto` return
and a `.url`. Lane L3's `J 57` read job ids off the tracker through
`_read_tracker`, moved them into a list with `ids.append(job_id)`, and opened
`/jobs/view/<id>` per id. The ids never passed through either source.

**THE PLANT IS THE WITHDRAWN CODE.** The withdrawal commit still resolves
locally; the route was lifted from it, trimmed, and embedded as a string --
including the comment its author wrote above the navigation ("Built from digits
proven above ... nothing the page chose reaches the url"). **Shown failing on the
unmodified engine: 11 failed, 5 passed** -- ten red plants and the same-module
pair failed; the five green cases passed trivially, which is why they only mean
something after the change. After: 16 passed.

    red plants (must be flagged)              green plants (must not be)
    j57-verbatim                              caller-supplied-id
    j57-visit-loop-renamed  (append only)     reading-gates-a-constant
    j57-reader-renamed      (summary only)    count-as-offset
    dom-reader-per-urn                        key-is-not-a-receiver
    evaluate-hrefs                            comparison-against-caller-id
    get-attribute-href
    script-composes-two-tools                 plus: one module holding J 57 AND
    closure-over-a-reading                    the caller-supplied twin, both
    augassign-accumulation                    naming their id job_id -> exactly
    landed-url-through-a-helper               one finding, on the J 57 line

**FOUR DECISIONS, EACH MEASURED FIRST** (prototypes in the session scratchpad):

    decision                              measured on                  without it
    taint scoped lexically, not per       the withdrawn server.py      15 findings, 11 of them one
      module by name                                                     `url` collision; scoped: 2
    a subscript target's KEY receives     this tree                    2 false convictions (a
      nothing (`out[k] = v` taints out)                                  caller's section, a loop key)
    `.append`/`+=` carry a value          the renamed-loop J 57        missed entirely
    sources derivable from one file's     scripts/staged_navigation_   the staged guard would stop
      own text (a reader-name convention    guard.py's premise           being an induction step
      + the file's page-returning fns)

The sources for the navigation sink are now: a `goto` return, `.url`, Playwright's
page reads (`_PAGE_CALLS`, held equal to the page-text rule's `TEXT_CALLS` by a
drift test), a call to a reader-named function (`read_`, `harvest_`, `linkedin_`),
and a call to a function in the same file whose return value asks the page. The
url walk is unchanged; `violations()` returns the union. `_bindings` is not
widened (its parity with the page-text walker holds); the two extra forms live
in `_accumulations` and are pinned by their own test.

**WHAT IT CANNOT SEE, PRICED.** A page-returning function in ANOTHER module whose
name the convention misses: an over-approximate whole-tree summary counts 89
such call sites across 37 callees under the convention as shipped (a first
measurement, 102 across 44, was taken before `linkedin_` joined the convention).
A whole-tree complement was built and declined: 17.4 s per run, and on this
tree its one extra site was a bare-name collision between two modules'
`_url_for` -- an artifact. The convention is a name, so it cuts both ways: a url
BUILDER named `linkedin_*`, or a same-file page-returning function named like a
common method, would be convicted -- loudly. The url-proven `_SANITISERS` are
not honoured by the reader walk. All of it is written beside the code.

**THE INDUCTION STEP, RUN RATHER THAN ARGUED.** `scripts/staged_navigation_guard.py
--paths` over the three declared files and one untouched module: exit 0, "both
rules agree with their declarations".

**COST.** Reader walk 2.4-2.8 s of CPU over 276 files after a type-dispatch fix
(4.9 s before it). The whole file, same box: HEAD's version 597 passed in 44.1 s,
this version 616 passed in 39.8 s -- the addition is inside wall-clock noise.

**WHAT IT FOUND ON ITS FIRST RUN: THREE ROUTES, NONE NEW, DECLARED NOT WAIVED.**

    server.py                          item_url                           SHIPPED -- linkedin_surface_census's
                                                                           feed_item keys, through
                                                                           _resolve_own_item_permalink
                                                                           (present since 2026-08-31, three
                                                                           days before the rule existed)
    _probe_comment_overflow_menu.py    ITEM_PERMALINK_URL.format(urn=urn)  every item on his rail (2026-09-04)
    _probe_comment_identifier.py       ITEM_PERMALINK_URL.format(urn=urn)  every item on his rail (2026-09-05)

All three read HIS OWN activity rail through `dom.read_own_activity_items` and
open a permalink built from a urn it returned. **This needs a ruling, not an
edit.** The rule says never navigate to what the page chose, and `J 57` was
withdrawn for ids read off his own tracker; `_resolve_own_item_permalink`'s
docstring refuses the opposite hazard on purpose -- a caller-supplied urn would be
"an identifier this server never read". Each rule is right about the hazard it
names. `KNOWN_DERIVED_NAVIGATIONS` carries that argument and is asserted exactly,
so a fix forces its entries out.

## 3. (c) THE HASH CITATION GUARD READS A CAPITALISED KEYWORD

**THE GAP.** `scripts/check_cited_shas_resolve.py`'s `committed` slot was
lowercase-only, so "Committed `d111560`" (lane L3's record, line 888) was never a
candidate. Every other keyword slot had the same property.

**MEASURED BEFORE WIDENING.** An implementer child (`claude-sonnet-5`, measured afterwards -- see the Follow-up) folded each other keyword in
isolation over the tracked corpus: 35 (token, site) pairs added that nothing had
checked -- 33 resolve, and the two that do not are already suppressed at the same
site (`56e03b0` in a document declaring its SHAs dead; `c4d2be2` already
MARKED-MAPPED through the lowercase `at`). Zero new findings, so all ten keyword
slots were folded, with `(?i:...)` scoped to the keyword so the hex class stays
lowercase-only.

**SHOWN FAILING.** The sentence-initial plant failed on the unmodified guard
(`assert [] == ['deadbee']`); with only `committed` folded, the per-slot
capitalised plants failed on 9 of 10 slots; after, 13 passed, and a completeness
test fails if a keyword slot is ever added without a plant. The module: **41
passed** in 172 s, including the empty pin -- the corpus-wide confirmation that no
new unresolvable citation appeared. `d111560` itself resolves: it is an ancestor
of `master`.

## 4. (d) THE REASON LOCATOR READ A CONFLICTED PATH THREE TIMES

**THE GAP.** `scripts/find_blocker_reason.py` built its corpus from
`git ls-files _audit` with repeats kept; an unmerged path is listed once per
stage. The census cleanup lane measured 33/30/24 against 11/10/8 for one document
(`_audit/2026-09-23-census-cleanup.md` section 13.5).

**THE REPAIR**, by an implementer child (`claude-sonnet-5`, measured afterwards -- see the Follow-up) and reviewed here: the listing is now
`tracked_audit_paths(root)`, collapsed with a set exactly as
`scripts/build_audit_index.py` already does -- not `--deduplicate`, which older git
lacks under `check=True`.

**SHOWN FAILING** on the extracted, undeduped listing: a conflict manufactured in
a throwaway repository (the premise measured -- git 2.52 lists the path three
times, stages 1, 2 and 3) returned it three times, and a planted tripled listing
scored the known document 6 against 2. Both pass after; the module is 32 passed.
The child caught its own first draft patching the whole function, which would
have stayed red forever, and re-proved red by reverting only the set.

**HOW MUCH THE MAP MOVED: ZERO LINES.** Regenerated with the fix and before this
record was tracked, `_audit/_census/blocker-map.tsv` is byte-identical -- nothing is
unmerged in a clean tree, which is the only place the old listing differed. The
regeneration after this record was staged is in section 6.

## 5. WHAT THE FIXES EXPOSED ELSEWHERE -- NOT REPAIRED HERE

1. **Three derived navigations needing a ruling** -- section 2. The shipped one is
   the census tool's `feed_item` surface.
2. **Five readers still laundering exception text**, one handler each (two in
   `notify_cost.read_notifications_badge`): `events.read_events_home`,
   `job_collections.read_job_collection`, `newsletters.read_newsletter_subscriptions`,
   `notify_cost.read_notifications_badge`, `premium.read_premium_surface`. The
   repair is the one `dom.py` took; each forces its `KNOWN_LAUNDERERS` entry out.
3. **`writes.perform` renders exception text twice** -- `click_error` and
   `verified_why`, receipt text rather than a gate refusal. The failing-page
   family cannot see them: `perform` is not driven (the `writes_enabled` door).
4. **Thirty `dom.py` log calls interpolate exception text.** A log record is
   another way out of the process; no guard here reads logs for this marker.
5. **The same multi-stage listing, in two count-sensitive places.**
   `scripts/check_asserted_names_resolve.py::tracked` returns repeats, and its
   ratchet pins a per-document occurrence COUNT, so mid-merge a conflicted pinned
   document would read as both appeared and repaired (DERIVED by reading, not
   run). `tests/test_a_correction_is_findable_from_the_claim.py`'s `_documents`
   also returns repeats; its consumers were not audited. Safe by construction:
   the hash guard (a dict keyed by path), `check_banked_evidence_is_reachable`
   and the sanitiser census (sets).
6. **A readiness race with a known mechanism, in a file this lane does not own.**
   `tests/test_click_is_not_its_own_evidence.py`'s `_fast_wait` fixture sets
   `dom.TYPEAHEAD_TIMEOUT_MS` from 5000 to **250 ms**, and its docstring says it is
   "for the one test that WANTS it to time out" -- the one asserting
   `1_no_listbox`. **Seventeen tests take it.** At least two of them assert
   `4_several_options_match`, which needs the listbox to ATTACH inside those 250 ms:
   `test_the_refusal_names_the_ambiguity_when_no_matcher_can_help` and
   `test_the_refusal_says_when_a_matcher_would_have_separated_them`. Under a box
   running other lanes' suites, it does not. Measured three times this session,
   each reading `1_no_listbox`: a six-worker batch, gate run 2, and the module run
   alone at 03:23 while other lanes' suites ran; each passed when re-run alone
   (13.7 s for the test; the module passed whole at 01:42 when the box was
   quieter). Already on record on 2026-09-21, reproduced by another lane at a
   clean HEAD (`_audit/2026-09-21-the-four-loose-rows.md` section 5A.1). **Not
   this lane's change, by construction:** `appeared` is set by
   `page.wait_for_selector(..., timeout=TYPEAHEAD_TIMEOUT_MS)`, which runs before
   both lines this lane edited in `read_typeahead_options`, and every consumer of
   the `error` field tests only its truthiness or prints it -- a type name is as
   truthy as the message it replaced. The repair is the owner's: give those tests
   the real bound, or their own.

## 6. COMMITS, GATES, AND WHAT DID NOT RUN

The commits, on this branch only until it merges (no ancestor of `master` yet):

| hash | subject |
|---|---|
| `1589837` | navigation guard: a value a reader returned is a derived navigation (J 57's blind spot) |
| `0926678` | hash citation guard: every slot keyword is case-folded, the hex class is not |
| `8013a30` | reason locator: a conflicted path is read once, not once per merge stage |
| `54ebb7f` | error fields carry the exception TYPE: fourteen dom.py sites, one write gate, and the guard that holds it |
| `447a838` | lane G record and register section 67; generated files regenerated to a fixpoint |
| `9512fd1` | lane G: the navigation guard's limits restated from a re-measurement; the record's times read from git |

Gates are recorded in section 6.1 as they complete.

### 6.1 Gates

    each fix's shown-failing test          sections 1-4, red then green, every one
    reader page-string guard               279 passed (whole file, after the repair)
    tool-envelope page-string guard        in the 976-test batch below, green
    navigation guard + its three users     747 passed (+ page-text, staged, sanitiser)
    hash guard                             41 passed
    reason locator + blocker map tests     32 + 7 passed (the child's run)
    every test touching a changed reader   974 passed, 2 failed, 1 skipped,
                                            1 xfailed -- one failure was the retired
                                            positive control (mended, 1.4), the
                                            other the readiness race (5, item 6)
    staged navigation guard, fast path     exit 0 on the three declared files + one
    impact gate --against 9c219c8, run 1   NO VERDICT. 16 changed paths selected 197
                                            of 234 test files (84%, above the 45%
                                            line), so it widened to the full suite;
                                            killed at 02:28:34 by this lane's own
                                            `timeout 1790` while a sibling lane's
                                            full-suite gate shared the box. A gate
                                            killed by its caller is not a red and not
                                            a green, and is not counted as either.
    impact gate --against 9c219c8, run 2   REFUSED on ONE test, on the final code
                                            tree (the table's last row): 1 failed,
                                            9123 passed,
                                            8 skipped, 1 xfailed in 2462.5 s, full
                                            suite, launched 02:34 after the older
                                            sibling gate exited, no timeout wrapper.
                                            The one red is the 250 ms readiness race
                                            of section 5 item 6, attributed there.
    cold verification pass                 11 of 11 PASS -- section 7

**NOT RUN, and what that leaves open:** a third full gate to turn run 2's single
red green (the race is load-dependent, and the owner's repair, not a re-run, is
what would settle it); CI on any platform (nothing was pushed); anything live.
No gate ran on the commit that adds sections 6.1 and 7: that commit changes this
record alone, with the generated files re-run to a fixpoint.

## 7. THE ONE COLD VERIFICATION PASS

One implementer child (`claude-sonnet-5`, measured afterwards -- see the Follow-up), cold to this work, ran an 11-item closed checklist over
the tree at the section 6 table's last row, from disk, read-only, reporting facts
for the lead to judge. **11 of 11
PASS**, no CANNOT-TELL. The report stays in the session scratchpad; what it found:

* six lane commits, and no attribution line in any message body;
* 1827 added lines: no non-ASCII character (checked per character, per byte and by
  regex); no drive path, user directory or name. Its one raw hit, `C:\`, was
  fixture text -- the identifier `SRC` then `:` then an escaped newline -- and it
  said so; the one address is `control@example.invalid`;
* no census slice, no census file other than the generated map, and no rulings
  register source among the 16 changed paths;
* all 15 `dom.py` hunks are an `error`/`why` assignment, its continuation, or a
  comment;
* **the twelve ruled raise sites: every one IDENTICAL, and more than asked -- each
  of the twelve functions' whole body is byte-identical to `9c219c8`**;
* the three generated files' `--check` modes all exit 0;
* the red proofs re-derived from the old revisions, not taken from this record:
  the old hash guard finds no candidate in the capitalised plant and the new one
  finds `deadbee`; the old navigation module finds nothing in the `J 57` route and
  the new one finds exactly the marked line; the locator's two tests and the
  failing-page selection pass; `KNOWN_LAUNDERERS` holds five keys, none in
  `dom.py`, `writes.py` or `server.py`;
* this record's first line, its commit table against `git log` (the four rows it
  then held, subjects equal), and no status-log time later than the commit that
  wrote it;
* section 67's entry paths all exist; the worktree clean.

As briefed, that was the one pass; nothing was re-verified after it. The gate run
2 result and this section are the only changes since.

## Follow-up 2026-09-24

The orchestrator's follow-up order, stamped 03:48, after lane G merged as
`209a831`: ten items, one commit each, each with a test shown failing first.
STEP 0 fast-forwarded this branch to `209a831`; every commit below sits on it.
Two children did closed slices (items 6 and 7), both `general-purpose`, both
reporting `claude-opus-5-5`; each was told this lead was writing in the same
worktree, which files were its own, and not to commit. Both reports stay in the
session scratchpad; this lead reviewed each diff before committing it.

**A CORRECTION TO THIS RECORD'S EARLIER SECTIONS, measured rather than
assumed.** The original lane's three children -- slice (c)'s measurement,
slice (d)'s build, and section 7's cold verification -- were `implementer`-typed,
and every model field in their transcripts reads `claude-sonnet-5` (54, 90 and
163 fields respectively; no other model appears). Sections 3, 4 and 7 name no
model; this is the model. The orchestrator measured the same leak tonight and
barred the type; the two follow-up children's transcripts read
`claude-opus-5-5` throughout (115 and 152 fields).

### F.0 Commits, with their times from `git log`

| time | hash | item | subject |
|---|---|---|---|
| 04:41 | `c6486f2` | 1 | census feed_item: the caller names the item, and his own rail may only veto it |
| 04:42 | `da3354d` | 3 | write receipts: perform's click_error and verified_why carry the exception TYPE |
| 04:47 | `e88ed47` | 1 | reader baseline: record _own_item_veto, which replaced the census resolver |
| 04:47 | `2c1a676` | 2 | five readers' error fields carry the exception TYPE; KNOWN_LAUNDERERS is empty |
| 04:48 | `3e6fb24` | 4 | browser: a failed navigation names its type and the address's family, never the address |
| 04:48 | `892f7d5` | 6 | two more ls-files listings read a conflicted path once, not once per merge stage |
| 04:52 | `fd5fc78` | 7 | typeahead tests: the 250 ms cut goes to the one test that wants the timeout, and checks its own premise |
| 05:00 | `a90a7a0` | 5 | logs: every record that carried a caught exception's text now carries its type |
| 05:08 | `d618fc8` | 8 | mutation scan: replacing a browser API is a mutation, and the scan now sees it |
| 05:12 | `98e1937` | 9 | retire scripts/_check_jobs_gap_directions.py: a stale, crashing subset of a maintained table |
| 05:37 | `845b38c` | 10 | navigation guard: a whole-tree complement resolves calls through imports, and runs in CI |
| 05:55 | `73ed8e5` | record | lane G follow-up record: per item, the failing test, the fix and the passing result |
| 06:41 | `3cea7a0` | 3, 4 | items 3 and 4, second round: the gate found a deleted reason and a vanished site |

The commit that adds F.12 and F.13 follows these and changes this record, the
register and the generated files alone.

### F.1 Item 1 -- the census `feed_item` route: the caller names the item, his rail may only veto it

THE RULING, delegated by the orchestrator: THE PAGE MAY VETO A NAVIGATION,
NEVER SUPPLY ONE.

* **Failing test.** With the three `KNOWN_DERIVED_NAVIGATIONS` declarations
  removed, the navigation guard went red on all three routes: 3 failed. The
  retired code, driven through the same rail from `209a831`'s `server.py`,
  opened the page's FIRST item for `feed_item` and its RICHEST for
  `feed_item_commented`, and refused an `item` argument outright.
* **Fix.** `linkedin_surface_census(surface, item)`. `feed_item` requires
  `item`, one of the keys `linkedin_my_activity_items` returned; a missing or
  malformed one is refused before any page loads (`pages_loaded` 0) and is
  never echoed, and a fixed surface refuses an item. `_own_item_veto` replaces
  `_resolve_own_item_permalink`: it reads his rail, inherits every authorship
  refusal, answers one membership question and RETURNS NO ADDRESS; an item not
  on the rail is refused with its page never loaded, naming none of the rail's
  other keys. The permalink is built from the caller's argument. The anchor
  count is coerced (the retired resolver called `int()` on a page value).
  `feed_item_commented` and `CENSUS_ITEM_RULES` are retired -- they differed
  only in how the page chose; the caller now picks the richest item from
  `anchors_per_item`. The two comment probes take the items on the command
  line, verify each on the rail, and visit in the operator's order. The tool
  surface moves from 69 to 70 parameters; the README's census row is corrected.
* **Passing.** Seven new census tests (the named item and no other; an item off
  the rail refused before its page; a rail refusal still stops the census; no
  item or a malformed one refused before any load, eight shapes; a fixed
  surface refuses an item; the item shape is the reader's own regex; the veto
  cannot supply an address). The whole navigation file and the staged guard's
  tests 629 passed; the census and pin files green; `KNOWN_DERIVED_NAVIGATIONS`
  empty again.
* **MISSED, AND OWNED.** That commit's gate selection did not include the
  reader guard, and the renamed reader broke
  `test_the_driven_set_has_not_silently_shrunk` ("a new reader with no recorded
  verdict"). Repaired in `e88ed47` with `--write-baseline`, which also moved
  three entries from `returns_text` to `clean` that were ALREADY stale at
  `209a831` -- the guard does not fail on an improvement, so nothing had said so.

### F.2 Item 2 -- five readers write the exception's type; `KNOWN_LAUNDERERS` is empty

* **Failing test.** With `KNOWN_LAUNDERERS` emptied first, the failing-page
  family went red on exactly these five: 5 failed, 121 passed.
* **Fix.** `out["error"] = type(exc).__name__`, one line per handler:
  `events.read_events_home`, `job_collections.read_job_collection`,
  `newsletters.read_newsletter_subscriptions`,
  `notify_cost.read_notifications_badge` (two handlers),
  `premium.read_premium_surface`.
* **Passing.** The reader guard, the five modules' own tests, and the envelope
  and page-text guards: 496 passed.
* **The cost this order accepted, written down rather than deleted.** Three tests
  pinned the old message (`RuntimeError: frame was detached`); they now assert
  the class and the message's absence. The newsletter test is renamed, and its
  docstring keeps the argument it made for the message -- a diagnostic that
  named its own cause.

### F.3 Item 3 -- `writes.perform`'s `click_error` and `verified_why` carry the type

* **Failing test.** `tests/test_a_write_receipt_carries_no_library_message.py`:
  a failing click and a failing verification read, each quoting a marker,
  driven end to end through the follow-a-Page harness on a local headless page,
  plus a structural scan that `writes.py` renders a caught exception's text
  nowhere but a `raise`, with its own control. On the unrepaired module: 3
  failed, 1 passed -- the click receipt carried the selector and the marker,
  the verification receipt the marker, and the scan named both lines.
* **Fix.** Two hunks, line-local for lanes L5 and L7: `click_error` is the
  type; `verified_why` names the type and says why its message is not repeated.
* **Passing.** 4 passed. `tests/test_verification_that_could_not_read.py` had
  proved its raise was real by reading the navigator's refusal back OUT OF THE
  RECEIPT -- the leak itself; that proof now rests on the navigator's own
  record, and the receipt is asserted to carry the type and NOT the address.
* **SECOND ROUND -- THE FOLLOW-UP'S GATE FOUND WHAT THIS ITEM'S OWN SELECTION
  MISSED.** Type-only erased reasons this package COMPOSES: the upload gate
  raises three refusals inside the same block (no digest on the grant, the file
  changed since the preview, a control not classified as a file input), and
  `tests/test_uploads.py` pins their text in `click_error`: 4 failed on
  `73ed8e5`, each reading `'WriteAttemptError'` where the reason should be.
  The item's selection had not included that file. Repaired with
  `_PerformRefused(WriteAttemptError)`, raised by exactly those three and caught
  in one place, the only handler whose text `click_error` keeps; every other
  exception there still keeps its type. What its messages may interpolate is
  pinned -- `spec.action`, the two digest prefixes, the control kind and the one
  kind a file may go to -- and a plant interpolating a selector or a needle, by
  f-string, `%` and `format`, is shown failing. After: the four upload tests and
  the whole receipt guard green (numbers in F.12).

### F.4 Item 4 -- a failed navigation names its type and the address's family

* **Failing test.** `tests/test_a_failed_navigation_withholds_its_address.py`
  drives `goto` with a page whose navigation fails quoting its address, over two
  admitted addresses carrying a keyword: the keyword appeared twice in the
  unrepaired message (once from the f-string, once inside Playwright's text).
* **Fix.** `BrowserUnavailableError(f"navigation to a /{family}/ page failed:
  {type} (the address and the library's message are withheld ...)")`, the
  family being the address's first path segment; the original stays chained
  in-process for a debugger.
* **Passing.** 3 passed; the browser, auth, preflight, CDP, envelope and
  error-url suites 235 passed.
* **SECOND ROUND, ALSO FOUND BY THE GATE.** `tests/test_no_message_publishes_a_landing.py`
  keeps a baseline of every message that interpolates an address, and
  `browser.py:goto:url` -- ruled `ASKED_FOR` there -- VANISHED, which that guard
  reports as coverage lost: 1 failed on `73ed8e5`. The site vanished because the
  address left the message, so the baseline moved (`--write-baseline`: that one
  line, nothing else) and the `ASKED_FOR` ruling for `browser.py:goto` left with
  it, with a comment saying why: putting the address back now arrives as a site
  with no verdict and has to be ruled again, where a lingering entry would have
  filed it as allowed.

### F.5 Item 5 -- logs: where they land was measured, then type-only was chosen

    where a record goes                  measured
    the linkedin logger                  one StreamHandler to stderr, propagate
                                         False, level LINKEDIN_LOG_LEVEL,
                                         default INFO
    LINKEDIN_LOG_LEVEL                   unset in the process, user and machine
                                         scopes; set by no launcher; absent
                                         from the MCP registration (type http,
                                         a url, no env)
    the server's stderr                  scripts/start_server.ps1 redirects it
                                         to _state/http-server.err.log --
                                         gitignored, ON DISK; it held 5 INFO
                                         lifecycle lines, none from these sites
    at the default level                 41 DEBUG sites land nowhere; 4 land in
                                         that file when they fire (auth INFO x2,
                                         profile_lock WARNING x2)
    at DEBUG, the level one diagnoses at all 45 land there

* **Decision: type-only, and 45 sites rather than the order's 30.** Redaction is
  not honestly available: `config.scrub` substitutes paths only, and the
  page-text rule records that this package has no instrument that can tell a
  name. The sites that land BY DEFAULT were outside `dom.py`, so the scope
  widened: `dom.py` 30, `browser.py` 8, `auth.py` 3, `cdp_bridge.py` 2,
  `profile_lock.py` 2, each rewritten by AST position, one line each.
* **Failing test.** `tests/test_no_log_record_carries_a_library_message.py`, a
  structural pin over every module with its own control (a planted module, red
  on lines 5, 9 and 13), named all 45. The failing-page drive, now capturing the
  `linkedin` logger at DEBUG, convicted 35 readers whose records carried the
  marker: 36 failed.
* **Passing.** 409 passed; the caplog, profile-lock, browser, auth and CDP
  suites 779 passed; the page-text and navigation sink inventories 636 passed,
  unmoved.

### F.6 Item 6 -- two more `ls-files` listings read a conflicted path once

* **Failing test.** A conflict manufactured in a throwaway repository (git lists
  the path three times -- the premise, measured): `tracked()` and `_documents()`
  both returned it three times. For `_documents()` the symptom is a verdict: a
  planted tripled listing turned the corpus check's basename-uniqueness
  assertion red on a duplicate that does not exist (249 == 247).
* **Fix.** `tracked()` dedupes by `dict.fromkeys` (git's order kept -- stage
  repeats are adjacent); `_documents()` by a set over git's exact strings,
  taken before they become case-blind Windows paths, then sorted as before.
* **Passing.** Both modules 27 passed.
* **THE HONEST HALF, from the child's measurement.** In the asserted-names guard
  the repeat changed no verdict -- `load_corpus` keys by path -- so the symptom
  test written for it passed on the unrepaired code and was not kept. The real
  mid-merge hazard for that ratchet is the conflict-marked WORKING COPY: a name
  inside a conflicting hunk counts twice, and no listing dedupe reaches it.
  Suggested, not built: refuse while `git ls-files -u` is non-empty.

### F.7 Item 7 -- the 250 ms cut goes to the one test that wants the timeout

* **Measured by instrument first** (each reading followed by a count of
  `[role="listbox"]` on its page): of the seventeen tests that took `_fast_wait`,
  ONE reads a page with no wrapper and asserts `1_no_listbox`; seven read pages
  that DO draw the wrapper, where 250 ms is a race (four assert a refusal that
  needs the wait, three assert counts only and raced silently -- one was caught
  reading `1_no_listbox` and passing); nine never took a typeahead reading.
* **Failing test.** The fixture now fails a test, by name, at teardown if any
  reading under the cut was taken on a wrapper page, or if none was taken.
  Against the seventeen-test list it failed exactly the sixteen non-takers,
  twice, under two load profiles (`-n 2` and serial).
* **Fix.** `_fast_wait` removed from the sixteen; it also requests `over`, so a
  machine without Playwright skips before the fixture exists.
* **Passing.** The module 30 passed, 1 xfailed (pre-existing, strict). The
  mechanism, shown in scratch: a wrapper attaching 300 ms late reads
  `1_no_listbox` under the 250 ms bound and passes under 5000 ms; the former
  racers' waits returned in 24 to 69 ms on the real bound.

### F.8 Item 8 -- replacing a DOM or browser API is a mutation, and the scan sees it

* **Failing test.** 13 plants in `tests/test_readonly.py` -- the clipboard shape
  (`navigator.clipboard.writeText` swapped for a capturing function), a
  replaced `window.fetch`, `Element.prototype.click`, `Object.defineProperty`,
  `delete`, `Reflect.set`, a bracketed member and more -- each scanned CLEAN on
  the token list: 13 failed. Ten reads of the same globals stay clean before
  and after.
* **Fix.** `scan_js_for_mutations` also reports `API replacement: <what
  matched>` for an assignment or `delete` on a member reached from a browser
  global, any `.prototype` member, `Object.defineProperty` and its relatives,
  and `Object.assign` onto a global -- `JS_API_REPLACEMENT_PATTERNS`, five
  compiled patterns. The token list is untouched. Measured before adoption over
  the 58 JavaScript strings in this repository (every executed script, every
  `*_JS` constant, every inline `evaluate` in `scripts/`): zero detections, so
  no shipped script changes verdict.
* **Passing.** The plants and reads green; the read-only boundary re-frozen with
  a note -- `<functions>` `d7e1d0922e3af446` -> `ff43e832d6f2b685`, the other
  seven digests byte-identical, HEAD hashing to exactly the prior pin. A
  refusal grew; no permission moved.
* **The first control was wrong, and the file says so.** `window.location.href
  === x` was written as a read that must stay clean; the token list's substring
  rule already flags it (`location.href =`). It was replaced by a comparison no
  token covers.

### F.9 Item 9 -- `scripts/_check_jobs_gap_directions.py`: deleted, on evidence

    jobs.md GAP rows today                                     92
    rows it classified                                         57
      still GAP                                                54
        covered by _audit/_census/jobs-directions.tsv          54   0 disagree
      no longer GAP (J 18, J 39, J 40)                          3
    today's GAP rows it did not classify                       40
    its own run                                                crashed: KeyError on row 17
    anything that ran it (tests, scripts, CI)                  nothing
    its successor, scripts/check_jobs_directions.py            GREEN, 92 of 92

* **Failing test.** None was possible for a script nothing ran: its own run
  crashed, and the comparison (a scratch instrument, keyed on slice AND row
  after its first draft keyed on slice alone) showed it a stale subset.
* **Fix.** Deleted rather than wired: wiring it would have kept the second copy
  of the data its own author warned against. Its one distinctive proof -- a
  boundary stub that admits everything -- already lives in the successor's tests.
  Register section 67.5 records the retirement.
* **Passing.** The successor green over 92 of 92.

### F.10 Item 10 (optional) -- built: a whole-tree complement, run in CI

**THE CALL, AND WHY.** Built, because the gap it closes was named and priced
but not covered anywhere, and CI is where walking the whole tree is free. The
declined first complement matched callees by bare name; this one resolves every
call THROUGH THE CALLING FILE'S IMPORTS (from-imports, module aliases, the
package's relative imports, re-exports followed to their definition), so the
`_url_for` artifact cannot recur.

* **Failing test.** With the resolver stubbed to resolve nothing: the seven red
  plants (from-import, module alias, package-relative module and name, two hops,
  re-export, the J 57 accumulation fed from another file) 7 failed, 11 passed
  (four green plants, seven premise tests), and the tree test under `CI=1` failed
  on its planted control (`assert [] == ['ITEM_PERMALINK_URL.format(urn=urn)']`).
* **Fix.** `derived_across_modules` runs the reader walk's own pass --
  factored out as `_reader_pass`, so the per-file verdicts are unchanged -- over
  every scanned file at once; `_Facts` gains the receiver of each call it
  already recorded, which nothing else reads. The tree test asserts three
  things, each able to fail alone: the complement adds exactly
  `KNOWN_DERIVED_ACROSS_MODULES` (empty); a planted module pair added to the real
  tree is convicted and nothing else moves; and calls on this tree do resolve
  (the premise -- a dead resolver would look like a clean tree).
* **Passing.** 19 passed under `CI=1`, the tree test 6.09 s. The navigation
  file and its three dependents: 763 passed, 1 skipped (the tree test, locally,
  saying why).
* **WHERE IT RUNS.** `skipif(not os.environ.get("CI"))`: GitHub Actions sets
  `CI=true` on every runner, and `scripts/ci_full_run_check.py` fails a shard on
  any skip not declared in `scripts/ci_expected_skips.json` -- so it cannot
  quietly skip in CI. `CI=1` runs it locally. The first CI run after merge
  should show the node `test_no_navigation_is_derived_through_another_module`
  PASSED in a shard's junit, not skipped.

      measured on this tree (a shared, loaded box)
      files                                             275
      module-level functions                            2306
        page-returning under the reader convention       476
          of them only because they read a FILE          181  (re-run without
                                                               read_text/read_bytes
                                                               as readers: 295)
      distinct calls resolving into another file         435
        into a page-returning function                    65  (38 functions)
      navigations carrying one                             0
      parse and scope / each fixed point           6.7 s / 0.14 s

* **THE RECORDED 89 WAS NOT REPRODUCED, AND IS NOT CLAIMED AS COVERED.** "89
  call sites across 37 callees" came from an over-approximate bare-name summary
  whose exact definition was not kept; two recomputations here under stated
  definitions gave 1107 across 63 and 1189 across 99. The instrument's own count
  is the 65 above.
* **A BARE-NAME COMPLEMENT IS WRONG ON TODAY'S TREE IN A NEW WAY.** Run by name
  over the tree as it stands, it convicts three sites, all by coincidence: both
  item-1 probes -- `pathlib.Path(__file__).resolve()` inside
  `sys.path.insert(...)` matched some module's page-returning `resolve`, which
  tainted `sys`, then `sys.argv`, then the operator's own items -- and the
  `_url_for` probe. Import resolution convicts none of them.
* **Not seen, said in the file:** a method on an instance (a prototype that
  matched methods by name found nine page-returning ones, and the two that reach
  a page, `goto` and `evaluate`, are direct sources already), a dotted receiver,
  `import *`, `importlib`, anything outside `SCANNED`.

### F.11 What the follow-up exposed -- open, not repaired here

1. **`tests/test_ci_shard.py::test_the_timings_table_still_prices_most_of_the_suite`
   is red on this branch ALONE, and passes after the merge with nothing to
   spare.** Here: 157 priced of 237 test files against a line of 158 -- this
   branch adds three test files (items 3, 4, 5) to a table whose label names
   `f65ec88` -- a commit that does not resolve on `master`.
   Master has moved: at `d9ec640` it prices 162 of 240, because the live lane
   added five files' seconds at its merge from a junit run of those five alone
   and wrote that into the table's `_measured` label. Merged: 243 test files
   against 162 priced, and the line is 162.0 -- green by zero; the next lane to
   add a file turns it red. Computed with the test's own expression over
   `git ls-tree master` plus this branch's three names, not by running a merge.
   A full regeneration is the real repair (the recipe is in
   `scripts/ci_shard.py`'s docstring), and it needs the full junit run this
   order bars on the shared box.
2. **Census row `C85`** (`_audit/_census/messaging-and-content.md`) names
   `server._resolve_own_item_permalink` behind the keys `feed_item` /
   `feed_item_commented`; both are retired by item 1. Prose in a census row, so
   left for its owner.
3. **The live lane's clipboard-capturing script is now convicted by the
   mutation scan (item 8)** -- the finding that started the item. The scan runs
   at TEST time, not as a runtime gate: once that script sits where a test
   asserts it scans clean (`tests/test_readonly.py`'s executed-script check, or a
   module's own `scan_js_for_mutations(...) == []` pin), that test fails until
   the script reads instead of replacing.
4. **The asserted-names ratchet's conflict-marked working copy** (item 6):
   named, not repaired.
5. **`profile_lock`'s two WARNING records still carry `_LOCK_FILE`**, the lock
   path from package config -- not exception text, so outside item 5's order,
   and they land in the gitignored stderr log when they fire.
6. **A TRIAL MERGE WITH MASTER, RUN WITHOUT TOUCHING ANY TREE**
   (`git merge-tree --write-tree master HEAD`, master at `d9ec640`): four
   content conflicts, each with its resolution --
   * `tests/reader_leak_baseline.json` -- both sides regenerated it; regenerate
     once more on the merged tree with `--write-baseline`.
   * `tests/test_readonly_boundary_invariant.py` -- both sides re-froze
     `readonly.py`'s digests; recompute them on the merged module and re-freeze
     with a note naming both changes.
   * `tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py` -- both moved
     the pinned parameter count; merged, it is master's plus this branch's one
     (`item`).
   * `tests/test_navigation_is_never_derived.py` -- **master DECLARED A FOURTH
     derived navigation** into the dict this branch emptied:
     `_probe_live_lane_session_1.py: ["url", "url"]`, "held here under the same
     pending ruling". That harness takes the newest id from
     `linkedin_my_activity_items`' raw output and, by its own comment, "never
     from a command line or a page" -- the opposite of the shape item 1 gave the
     two comment probes. **A RULING'S APPLICATION FOR THE MERGE, NOT AN EDIT FOR
     THIS LANE** (the file is the live lane's and exists only on master): either
     the harness takes the id from its caller and lets the rail veto it, or the
     declaration returns with an argument that survives THE PAGE MAY VETO A
     NAVIGATION, NEVER SUPPLY ONE.

   Seven more files changed on both sides merged cleanly, among them `server.py`,
   `readonly.py` and the register; the generated index and rulings register
   need their usual fixpoint after the merge. **The whole-tree complement, run
   over master's 282 files, adds nothing beyond the per-file findings** (the
   four declared sites; reach 72), so item 10's CI test holds after the merge
   however the fourth site is settled.

### F.12 Gates run, and what did not run

    gate                                         result
    each item's shown-failing test               F.1-F.10, red then green, every one
    impact gate --against 209a831, plan only     WIDENED: 36 changed paths (one a
                                                 deletion) select 206 of 237 test files
                                                 (87%, above the 45% line), so it would
                                                 run the full suite -- NOT RUN, as ordered
    the follow-up's gate, on the record commit   99 of 237 test files, -n 3, 932 s:
      every test changed on the branch, every    7 failed, 6024 passed, 8 skipped,
      test naming a symbol a changed item        1 xfailed
      touched, and the impact gate's 18
      corpus-wide guards
        the shard-timings coverage test          known -- F.11 item 1
        four upload tests                        item 3's deleted reason -- F.3, repaired
        the landing-message baseline             item 4's vanished site -- F.4, repaired
        the correction guard's triage            this record's own F.11 text: a correction
                                                 word inside a test FILE NAME, within two
                                                 lines of a cited document; rewritten
    after the second round, its six suites       upload, receipt, landing, verification,
                                                 performable action, writes: 295 passed,
                                                 3 skipped (symlink privilege)
    the document guards over this record         a first run convicted a new citation of a
                                                 hash that does not resolve on `master`
                                                 (the timings table's label); the sentence
                                                 now says so. Over the text as committed,
                                                 save this row's last line: ten document,
                                                 register and identity guards, 1032 passed
    whole-tree complement under CI=1             19 passed (item 10); 5.20 s in the cold pass
    generated files --check                      0 / 0 / 0, at every record commit
    cold verification                            16 of 17 PASS -- F.13

**THREE COUPLINGS THE ITEMS' OWN SELECTIONS MISSED.** Item 1's renamed reader
and the reader baseline (caught at the next commit, repaired in `e88ed47`);
item 3's composed refusals and `tests/test_uploads.py`; item 4's vanished site
and the landing-message baseline. Each item ran a hand-picked selection. The
gate's was built by symbol -- a test is in if it names something a changed
item touched -- and it found the other two on its first run.

**NOT RUN, and what that leaves open:** the full suite -- 138 test files
outside the gate's selection, 54 of which import `dom.py`, `browser.py`,
`server.py` or `writes.py`; CI on any platform (nothing pushed); the merge with
master, which F.11 item 6 measured without performing; anything live.

### F.13 The one cold verification pass

One `general-purpose` child, cold to this work, ran a 17-item closed checklist
over `209a831`..`73ed8e5` from 05:57 to 06:30, read-only, reporting facts for
the lead to judge; its transcript reads `claude-opus-5-5` throughout (221
fields). **16 PASS, 1 FAIL, 0 CANNOT-TELL.** The report stays in the session
scratchpad. What it found:

* **THE FAIL IS ITS CLEAN-TREE CHECK, AND THE CAUSE IS THIS LEAD.** The tree was
  clean at its start and dirty at its end: the second-round edits (F.3, F.4)
  landed at 06:16:52 while the pass ran -- after its last run, by the files'
  mtimes -- and it re-ran the two checks that read a now-dirty file against the
  committed blobs, with the same results. It also flagged the new
  `click_error = str(exc)` as exception text in a receipt: the carve-out F.3
  describes, uncommitted when it looked and pinned since.
* 12 commits, no attribution line (one literal hit, "generated with" inside the
  word "regenerated"); 2591 added lines, no non-ASCII character; the one
  drive-letter-shaped hit is fixture text; no user directory; nothing under the
  census directory changed, and the only rulings path is the generated one.
* **THE RED PROOFS RE-DERIVED FROM THE OLD REVISIONS, not taken from this
  record:** the five readers' handlers (6 renders at `209a831`, 0 at HEAD); the
  log sites (dom 30, browser 8, auth 3, cdp_bridge 2, profile_lock 2 at
  `209a831`; 0 at HEAD, and 0 across all 48 modules); the two listings (4
  entries at `209a831` on a stubbed tripled listing, 2 at HEAD); the mutation
  scan (the clipboard plant clean at `209a831`, convicted at HEAD); and the
  complement (7 of 7 red plants empty with the resolver stubbed, 7 of 7 found
  with it restored, the four green plants empty both ways).
* `_fast_wait` requested by exactly one test (seventeen at `209a831`); the census
  file 178 passed; the boundary invariant 14 passed; the three generated files'
  checks 0, 0, 0; every path in register section 67.6 exists.
* Beyond the checklist, measured by its own instrument and shown failing on its
  own plant: two shapes the log scan does not look for -- `exc_info=True` in a
  handler, and an exception copied to another name before it is logged -- occur
  0 and 0 times across the package.

As briefed, that was the one pass; the second round and this section are the
only changes since, and the second round was gated by its own six suites.

## Integration (follow-up) 2026-09-24

The orchestrator's integration order, stamped 07:05: merge master `66aaa95`
into this branch, with a ruling for each predicted conflict. Checked on disk
first, at 07:02: the tree was clean at this branch's previous record commit
(`72879f2`, which does not resolve on `master` until this branch merges), and
master was at `66aaa95`.
Since `209a831`, master had taken lane S, the live lane's session 1, rulings
batch 4, lane L7, and the orchestrator's fix for L7's two CI reds.

### I.0 Commits, with their times from `git log`

| time | hash | subject |
|---|---|---|
| 07:48 | `7cec6dd` | merge master 66aaa95 into lane G's follow-up: six conflicts resolved, two semantic ones found by lane G's guards |
| 07:56 | `2e3aad2` | floor lint: an f-string expression is judged by its own piece's quote, not the first piece's |

This record, the register and the generated files follow in one more commit.

### I.1 The textual conflicts, each resolved as ruled

The trial merge against `d9ec640` (F.11 item 6) predicted four. Against
`66aaa95` there were SIX: the register and the rulings register joined them,
because L7 appended section 70 and rulings batch 4 moved the generated file.

* **The navigation declarations (ruling a).** `KNOWN_DERIVED_NAVIGATIONS` keeps
  ONE entry: the live lane's session-1 harness, `["url", "url"]`. It carries the
  ordered note verbatim: pending PAGE-MAY-VETO-NEVER-SUPPLY (rulings batch 4),
  the live lane converts this harness to the caller-names-the-item shape before
  session 2, and this entry is debt, not a waiver. The three entries this
  branch retired stay retired. The harness is not edited.
* **The reader baseline (ruling b).** Regenerated with `--write-baseline` on the
  merged tree: 143 readers (86 clean, 40 returns_text, 17 not driven), none
  leaking. It differs from master's by the census rename alone.
* **The tool-surface pin (ruling b).** Measured off the merged registry at 53
  tools and 81 parameters, and the pin table equals it tool for tool. That is
  master's 53 and 80, plus `item`.
* **The boundary freeze (ruling b).** Both sides' re-freeze notes are kept, and
  the digests were re-derived with the file's own `ast_digest` (I.2).
* **The register and the generated files (ruling d).** Both appended sections
  are kept (67.5-67.7, and 70). `_audit/RULINGS.md`, `_audit/INDEX.md` and the
  blocker map were regenerated after every resolved path was staged, and a
  second pass changed nothing.

### I.2 The live lane's clipboard capture (ruling c) -- declared, and the scan kept whole

* **Failing test.** On the merged tree, test_readonly's check that a declared
  replacement script is invisible to the scan went red: 1 failed. The scan now
  reports seven replacements in `share_link.CLIPBOARD_JS`:
  - `navigator.clipboard.writeText` and `.write`;
  - `document.execCommand`;
  - one listener flag;
  - three `Object.defineProperty` calls.
* **Fix.** `readonly.SANCTIONED_API_REPLACEMENTS` is the scanner's sanctioned
  list. It has one entry: exactly those seven, keyed by
  `("linkedin_server/share_link.py", "CLIPBOARD_JS")`. Beside it are the
  ruling, SHARE-AND-POLL-PROOFS-OWN-POSTS, and the evidence:
  - the one sanctioned `evaluate` it runs from;
  - everything it replaces lives in this server's own tab;
  - `M C72` was proven on it live (the live lane's session-1 record, entry 12).

  The scan itself is untouched. The test now holds each declared script to
  EXACTLY its entry: no mutation token, no replacement beyond the list, and none
  of the list missing. A second test holds the list and the test-side
  declaration to the same scripts.
* **Shown refusing, on plants:**
  - the capture plus `window.fetch = ...` is refused, naming that one
    replacement;
  - the capture minus its listener flag is refused as a stale declaration;
  - the clipboard shape in an undeclared script is refused by the plain scan.
* **The freeze.** Five more names are pinned:
  - the new permission table;
  - the replacement scan's pattern tuple, and the three fragments it is built
    from BY NAME. `_literal` renders a name as a constant, so pinning the tuple
    alone would have frozen nothing of the fragments. Item 8 left all four
    unpinned when it built them, while `JS_MUTATION_TOKENS` had been pinned
    from the start.

  Thirteen digests in all, each attributed:

      <functions>                  ff43e832d6f2b685   this branch (the replacement scan)
      SANCTIONED_MUTATIONS         e79a701b37ae9c39   master (the live lane's five presses)
      six other tables             byte-identical on both sides
      _JS_BROWSER_ROOTS            75b6af8aaa6e187d   }
      _JS_MEMBER_CHAIN             c5d9d0c2da7553b0   } as item 8 built them
      _JS_ASSIGNMENT               40d484166bfbebbc   }
      JS_API_REPLACEMENT_PATTERNS  98a46c7ce6183658   }
      SANCTIONED_API_REPLACEMENTS  c1608a90b6669d78   new, one entry

  The merged file equals the branch on every key except SANCTIONED_MUTATIONS,
  and equals master on every key except `<functions>`. Removing the new table
  moves exactly its own digest. Controls: a planted eighth replacement moves that
  digest and no other, and dropping `navigator` from the browser roots moves
  `_JS_BROWSER_ROOTS`.
* **Passing.** The readonly suite and the boundary invariant: 342 passed.

### I.3 Lane L7's verification receipts, found by this branch's receipt guard

* **Failing test.** On the merged tree, the structural scan named two lines in
  `writes._verify_after`, both of the form `return (UNKNOWN, str(exc)...)`. Both
  render the landing gate's refusal: `mark_company_interest`'s fresh render, and
  `update_profile_field`'s editor.
* **The same site, driven.** A new driven test replays L7's own press through a
  navigator whose fresh render lands on another posting. With L7's lines put
  back, it failed. The receipt read "refusing to click: the grant is for job
  ... and the browser landed somewhere that is not that posting", AFTER the
  click had landed: 2 failed.
* **MEASURED, AND IT IS NOT A LEAK.** The gate's own message already withheld the
  landing: the planted landing's marker and its job id appeared nowhere. So the
  finding is two things:
  - the form this guard forbids;
  - a sentence that is wrong after the click.
* **Fix.** Each site composes its own sentence: the exception's type, and what
  `landing.withheld(landed)` says is safe to say about the landing.
* **Passing.** The receipt guard with L7's two suites: 75 passed.
* **The cost.** The editor branch no longer carries the gate's two route tails
  (what the page was expected to show, and what it showed). The landing's safe
  description replaces them.

### I.4 The floor lint's false positive -- and its worse mirror

The orchestrator suspected the oldest-Python guard of a false positive on L7's
f-string, which it had fixed in `66aaa95`.

**Measured on CPython 3.10.19 (through `uv`) and on 3.13.** L7's line as it
shipped, `f'<input ... value="{self.store["City"]}">'`, PARSES ON BOTH, and
the lint convicted it on both.

**THE CAUSE.** Implicit concatenation merges several literal pieces into ONE
`JoinedStr`, and the lint took the quote of the node's FIRST piece for every
expression inside it. L7's concatenation opened with `"`.

**THE WORSE HALF, found by building the mirror.** Take a first piece in `'...'`
and a later `f"{d["k"]}"`. That is a SyntaxError on 3.10.19, and the lint, on
3.13, reported NOTHING: the defect class it exists for, passed green.

* **Fix.** Each expression is judged by the quote of the innermost piece that
  contains it, read from the tokenizer:
  - on 3.12+, an f-string piece runs from its START token to its matching END;
  - before 3.12, a piece is one STRING token;
  - where the tokenizer refuses, the node-level quote is the fallback.

  A file is tokenized only if one of its expressions quotes something at all.
* **Failing test.** 2 failed on the unfixed lint: L7's line convicted, and the
  mirror passed.
* **Passing.** The file: 18 passed on 3.13. Also 18 passed on CPython 3.10
  through `uv`, where the mirror is refused by the parser instead, as every
  fixture there is judged. The whole-tree scan (534 files, loaded box) took
  8.1-9.4 s before and 9.9-10.5 s after, and no file was convicted either way.

### I.5 The shard timings -- the merge did not tip them

`test_the_timings_table_still_prices_most_of_the_suite` passes on the merged
tree: 164 of 245 test files priced, against a line of 163.33. The live lane
and L7 each priced their own files, so the order's condition was not met and
nothing was repriced. This branch's three new test files stay unpriced.

**The margin is two test files.** At 247 files the line is 164.67. The real
repair is queued to this lane by the next order: regenerate the table from a
green CI run's junit artifacts.

### I.6 Gates run, and what did not run

    gate                                           result
    each ruling's and finding's shown-failing test I.2-I.4, red then green
    impact_gate --against 66aaa95, plan only       WIDENED: 40 changed paths select
                                                   213 of 245 test files (87%), so it
                                                   would run the full suite -- NOT
                                                   RUN locally, as ordered; CI
                                                   certifies at merge
    the integration gate, on 2e3aad2               130 of 245 test files, -n 3,
      every test this branch changes against     2472 s on a loaded box:
      master; the 18 corpus-wide guards; 24      7044 passed, 8 skipped, 1 xfailed,
      census instruments; every test naming a    0 failed. The skips: the CI-only
      symbol a change touched; and the 28 test   complement (below), three symlink-
      files of lane S's, the live lane's and     privilege skips, four empty-
      L7's new modules, under every hardened     parameter declared skips. Both
      guard                                      files the next order names as
                                                 missed by recent selections
                                                 (the gap-rows pin, the floor
                                                 lint) were in it
    the whole-tree navigation complement (CI=1)  1 passed, 8.85 s, on the merged
                                                 tree: nothing beyond the per-file
                                                 walk, and the planted pair caught
    twelve document, register and identity       over this text: 1091 passed, 1
      guards                                     failed -- the SHA guard, on this
                                                 branch's own record commit cited
                                                 in an "at" slot; the sentence now
                                                 says it resolves only on this
                                                 branch. Then the SHA, correction,
                                                 rulings and blocker-map guards:
                                                 84 passed
    generated files --check                      0 / 0 / 0

**NOT RUN, and what that leaves open:**
- the full suite: 115 test files outside the gate's selection;
- CI on any platform (nothing pushed);
- a cold verification pass, which this order did not ask for;
- anything live.

### I.7 Open, for other owners

1. **The live lane's session-1 harness** is the one remaining derived navigation.
   Converting it fails the navigation file until its entry goes. That is the
   mechanism the entry's note describes.
2. **Census row `C85`** still names the retired resolver and census key. It goes
   to the live lane, as ordered.
3. **The shard-timings margin**, I.5.

## Foundation: people data

Two orders, both the orchestrator's. **2026-09-24 08:34** applied the
operator's NAMES-AT-RUNTIME (08:11, verbatim: "It's not about returning or not
returning. The functionality is to return people's names as the result.
During runtime, if you want to be careful, then follow the best procedure and
practice to mitigate the risk.") as PEOPLE-DATA-MITIGATIONS -- six
mitigations, one worked adopter (`linkedin_who_viewed_me`), the shaper tests
rewritten around the record type, and three queued items. **2026-09-27 13:25**
resumed the lane after a usage-limit restart: pin the WIP, finish the
foundation, make lane L5's two `include_names` readers the SECOND worked
adopter, integrate the then-current master ONCE, no new scope. The rulings
document is `_audit/2026-09-24-rulings-names-at-runtime.md`.

Every child was `general-purpose` -- four of them, one slice each, each told it
shared the worktree, which files were its own, and not to commit. None of them
could write a report file (the harness returns a child's findings as text), so
their reports arrived as notifications and were reviewed against the files
before anything was committed. Their model, measured rather than assumed:
every assistant message in each of the four transcripts carries
`claude-opus-5-5` (four of this lane's commit messages said so before it was
measured; it held).

### P.0 Commits, with their times from `git log`

```
e2e6273  09-24 09:41  impact gate: the oldest-Python lint and the refused-address pin run on every gate, declared
6a14864  09-24 09:49  mutation scanner: a DevTools session is a mutation (lane D's 5.3)
950cac8  09-24 10:00  ci: each shard keeps its junit in its artifact
90e087b  09-27 13:21  WIP, pinned after the restart: the record, its sanitiser and marker, a record-aware walk
26d32cc  09-27 14:23  the first worked adopter: linkedin_who_viewed_me
2c1e41b  09-27 14:28  mitigation 6: no write is aimed by a name, except two declared debts
b4c796d  09-27 14:29  mitigation 3: tracked fixtures render only declared synthetic people
16af667  09-27 14:29  mitigation 4: a people reader reads one page
f4bff5f  09-27 14:32  the guard redesign: a page string leaves only through a people record
10c6f02  09-27 14:42  merge master 2eb90ad -- the one integration
9af1506  09-27 15:04  after the merge: lane D's transport meets lane G's DevTools patterns; send_reply classified
aca479d  09-27 15:06  the second worked adopter: the conversation readers
3742ce9  09-27 15:12  the "no name parameter" shaper tests, rewritten around the record type
33e0c02  09-27 15:14  ci shard timings: the nine new test files priced
```

The 09-24 merge of master 1902fcb (38ba8df, 09:01) brought the rulings in
before any of it.

### P.1 The resume: the WIP was pinned before anything else

Five files were dirty at the resume; reviewed, coherent (the record module,
its tests, the walk's skip predicate, the plant helper, the instructions
paragraph), and committed as 90e087b, marked WIP, with "the suite is not
claimed green on this commit" in its message. Nothing was integrated before
the foundation's own commits were in.

### P.2 The record: mitigations 1 and 2

`linkedin_server/people_data.py`. A person is a frozen, slotted `Person`
(name, headline, link, degree); a group or an event is a `Group` or an `Event`
(title, link). `sanitise` is NFC; every whitespace character becomes a space;
Unicode categories Cc, Cf, Co, Cs and Cn are removed (controls, zero-width
and bidirectional characters, tags, private use, unassigned); runs collapse;
a hard cap per field (name 120, headline 220, title 220) cuts and never
refuses. It is idempotent, which is what lets a record REFUSE construction
with a field that is not already its own sanitised form -- an unsanitised
record cannot exist. Links are canonical (`/in/<slug>/` or a member urn; a
group's or an event's id only, an event's title dropped from its address).
Every envelope carries `untrusted_third_party_text`, and the server's
instructions name that key and say the fields are data, never instructions
(`tests/test_people_data.py` holds both, and, since the second adopter, that
the paragraph names exactly the tools in `PEOPLE_TOOLS`). `as_record`
re-validates a dict against an exact envelope shape, so a dict with the
marker and one extra key is no record. Tested on planted headlines: an
instruction-shaped one, zero-width and direction tricks, an over-length name.

THE COST, stated in the module: zero-width joiners go with the rest, so a
name in a script that uses them inside words keeps its letters and may render
differently. The order named zero-width characters without exception, and a
selective rule would be the first place a direction trick survived.

### P.3 The first worked adopter: `linkedin_who_viewed_me`

`shape.parse_person_card` returns `{"person": <Person envelope>, "viewed",
"anonymous"}`. RED FIRST, on the pre-adoption parser, driven on a planted
viewer list: four "viewers" where the page drew three (a page heading with a
zero-width character inside "viewed" passed as a person), the plant found
twice outside any record, and the zero-width character kept. After: three
records, nothing outside them. The parser now sanitises every line BEFORE it
classifies, keeps the degree badge it used to discard, gives an anonymous row
no link, and the view switch's `viewers_when_applied` is cut to the caller's
limit (it was every parsed row). `_attach_recipient_ids` reads the slug from
the record. The landing-interpolation census loses `parse_person_card:slug`
with its ruling entry, with a note.

SURPRISE 1, measured: no leak guard had ever driven this tool's success path.
The plant page answers `evaluate` with a dict, the viewer harvest expects a
list, so the tool was certified clean on its extraction-failure path alone.
`tests/test_page_strings_leave_only_as_people_records.py` drives it on a
list-answering page.

### P.4 The guard redesign: a page string leaves only through a record

The order: "page strings leave ONLY through the declared record, and NEVER
through an error field, a log record, a receipt, a cache or a fixture." Both
driven guards learn one verdict, `returns_records`: the plant came back, and
only inside records (`plantedpage.carries_the_plant_outside_records`, the
record-aware walk). The leak checks run first and stay on the PLAIN walk, so a
record in an exception or an `_error` envelope is a leak like any page string.
`returns_text` becomes a legacy inventory dated 2026-09-24 that may shrink and
may not grow: `text_ratchet`, asserted beside each guard's shrink check,
refuses a new text path, a stale inventory entry and a converted reader that
fell back, and both baseline writers refuse to record a new text path.
Existing verdicts did not move over either committed baseline. ITS LIMIT: the
inventory IS the committed baseline, so a text entry added to it by hand
passes the ratchet -- the writers refuse it, and only the diff shows it; and
a text path merged in from another branch's baseline arrives as inventory the
same way.

Each guard shown convicting AFTER the redesign, through its own code: the
reader guard (a record beside page text, a widened record, a plant used as a
key, a record carried out by an exception); the RaisingPage family (a library
message laundered into a record) and its DEBUG log capture (a record's name
in a log record); the page-text rule (a logged record built from the page);
the envelope guard (a record in an `_error` envelope). Plus: the ratchet's
controls, no declared people tool on the text inventory, and no module-level
cache written on the record path (both adopters' functions, with a control).

### P.5 Mitigation 3, fixtures: a slot reader, not a name detector

`tests/test_fixtures_hold_only_synthetic_people.py` (the fixtures child).
Names have no shape, so it reads the PLACES LinkedIn's markup puts a person
-- a member link's first visible text, heading and picture alt, and
aria-label templates -- over `git ls-files tests/fixtures`, and requires every
value found there to be declared: `SYNTHETIC_PEOPLE` here, or
`INVENTED_NAMES`, imported. Slots measured holding interface text were
rejected; a member-link label no template knows is taken whole, so a new
label shape fails closed. A failure prints the path, line, slot and a
SHA-256 prefix, never the value: a CI log is a publication channel. Twelve
places the guard does NOT read are planted and shown unseen. With the second
adopter it gained the conversation label as a slot, split into participants
so a declared name cannot vouch for one beside it, and declared the compose
list's four names on that fixture's own "Its CONTENT is invented" header.

### P.6 Mitigation 4: a people reader reads one page

`tests/test_a_people_reader_reads_one_page.py` (the bounded child). The
people-tool set is DERIVED -- functions referencing a record class through
`people_data`, a fixed point over every module, the `@mcp.tool()` functions
in it -- and held equal to `PEOPLE_TOOLS`. By reference, not by call,
measured: the first adopter hands its builder to `dom.parse_all` as a value,
so a call-only derivation finds no reader at all. No paging parameter, in the
signature or the published schema; no pagination-shaped definition anywhere;
every navigating loop a people tool reaches a plain `for` over a slice bounded
by a config ceiling of at most 2; navigating recursion refused; thirteen
planted shapes, each convicted by the rule it breaks and no other (16af667's
message says twelve; the table holds thirteen). 80 passed on 3.13 and on
3.10. `linkedin_open_messaging` loads two pages -- the receipt guard's
list, then `/messaging/` -- and its names come from the second only.

### P.7 Mitigation 5: visible only

"LinkedIn Member" comes back as exactly that, with no link and no recipient
id; a viewer drawn as a role at an employer comes back as drawn; `Person`
never looks anywhere else for who a row was; `deanonymise_a_viewer` stays in
`PERMANENTLY_FORBIDDEN` (asserted).

### P.8 Mitigation 6: no write is aimed by a name -- except two debts

`tests/test_no_write_is_aimed_by_a_name.py` (the writes child). Every
`target_kind` in `writes.SANCTIONED_WRITES` is classified into a closed
vocabulary with a one-line reason; the name-aimed actions are exactly
`NAME_AIMED_DEBT`: `send_invitation` (`member`, his word for a person,
matched against control labels) and `send_message` (the `member` half of its
target, typed into the recipient typeahead). Both predate the ruling; they
are declared as debt, not waived, and converting either fails the file until
its entry goes. No write tool takes a name-shaped parameter beyond the two
debt pairs, found off the syntax tree by two routes that must agree and held
equal to the registered schema. Twelve controls -- fourteen cases -- and four
link-or-id parameters that must pass (2c1e41b's message says seventeen
controls; counted here from the file). The older
`tests/test_no_write_tool_names_a_third_party.py` said a needle "is not
forbidden and must not be"; that sentence now says "not forbidden by THIS
file", with a dated paragraph pointing at the debt. At the merge, lane L5's
`send_reply` (`thread_and_text`) was classified `id_and_own_text`: a thread
id the caller supplies, never read off a page.

### P.9 The "no name parameter" shaper tests, rewritten around the record type

Eight tests over seven modules -- `groups` (twice), `search_results`,
`anchors`, `company_root`, `group_page`, `recommendations`, `feed` -- each
held its module name-free on `inspect.signature`. NAMES-AT-RUNTIME amended
that doctrine for what a read returns, and the order said rewrite, not
delete. `tests/record_typed.py` is the one reading all eight now apply: a
parameter named like a person, a name or an address of one is refused unless
its annotation is a people record (alone, in a container, or optional; an
unresolvable annotation fails closed); needles, page text and a company stay
refused outright. Shown both ways, per test: a BARE name parameter planted
into each module turns its test red (8 of 8, the old failure kept) and the
same parameter annotated as a record turns it green (8 of 8). The reading's
own controls are `tests/test_a_name_enters_a_shaper_only_as_a_record.py`.
On the real tree none of the seven modules takes such a parameter.

### P.10 The one integration: master 2eb90ad

Merged at 10c6f02, after the foundation's own commits and before the second
adopter -- the adopter's code existed only on master, which is why the one
integration came here rather than last. Eight conflicts, each from both
sides: the instructions (master's pages_loaded sentence, then the people
paragraph); `writes.py` (the composed fresh-render refusal, then lane L7's
badge branch); the boundary freeze (both histories, and a note: the merged
`readonly.py` equals the branch on every key but `_ALLOWED_URL_PATTERNS`,
and master on every key it pins but `<functions>` and
`_MUTATION_CALL_PATTERNS`, computed on each side's own copy of the test);
the tool pin (56 tools and 88 parameters, MEASURED off the merged registry);
the landing baseline (regenerated, equal to the union, 38 sites); the
register (both sides); `RULINGS.md` and the blocker map (regenerated to a
fixed point).

The post-merge gate (81 files) found what the merge had joined: 5740 passed,
6 failed. Four were one meeting -- lane D's `cdp_download` (P C8's download
transport, on D4-NO-OWN-BROWSER-CONTEXT) under the DevTools patterns this
lane added at lane D's own request; 6a14864's message had predicted exactly
this ("its merge sanctions the three calls and rewords the docstring"). So:
the docstring's call-shaped prose reworded; the one send and two sessions
declared in `SANCTIONED_MUTATIONS` by function, with their argument, on the
precedent of integration ruling (c); a control that one more send or session
anywhere else in that module is refused; `SANCTIONED_MUTATIONS`
e79a701b37ae9c39 -> e9d953efc8ab8d0e, the tree minus exactly the 35 added
lines hashing to the prior pin on every key. `tests/test_messaging_overview.py`'s
read-path gate imports a taxonomy in which both DevTools classes are gated by
default; they stay gated everywhere else, and on that one module are judged by
the METHODS its send can carry (one: `Browser.setDownloadBehavior`), shown
refusing an input method in the table, an empty table, and any other module.
The fifth was `send_reply`'s kind (P.8); the sixth the timings (P.13).

### P.11 The second worked adopter: the conversation readers

`linkedin_list_conversations` and `linkedin_open_messaging` with
`include_names`. A row now carries `with`, a people record, and never the raw
label; without `include_names` it keeps its `name` placeholder, unchanged.
The reader still reads the raw label into its reading, which is not returned,
and the shaper builds the record -- the first adopter's pattern:
`threads.conversation_with` makes a `Person` of a one-to-one row and a title
record of a group row (the row's group marker says which); `list_result`
publishes it. `shape.messaging_overview` makes a `Person` of every label;
ITS LIMIT, stated where a caller meets it: `/messaging/`'s label does not say
how many people it names, so a group's label comes back in a person record
too. Both tools joined `PEOPLE_TOOLS`, which the bounded file derives and
holds.

SURPRISE 2, the same blind spot by another route: the guards drive every tool
with its defaults, `include_names` defaults to False, so no guard had ever
seen a name cross either tool (both clean in the baseline). Section 1b of the
invariant file drives both with `include_names`, on a page whose two rows are
labelled with the plant, laced with a zero-width space and a direction
override: only inside records, sanitised, a person and a title record;
without `include_names` neither carries it; and each drive is shown failing
-- with the builder swapped for the raw label, the same envelope is text.
Lane L5's two tests moved to the record form without weakening: the names
are read out of the records, a bare name beside one fails, the group row must
be a title record.

### P.12 The three queued items of 08:34

- **The impact gate's floor** (e2e6273): `test_the_package_compiles_on_its_
  oldest_python.py` and `test_gap_rows_on_refused_addresses.py` run on every
  gate as DECLARED members -- what makes each corpus-wide lives in the script
  it runs, which no detector reads; derived detection was measured and pulled
  in eight files (one at 716 s) while still missing the census walker. Held,
  with the control that clearing the declaration drops both.
- **Lane D's 5.3** (6a14864): `cdp_session` and `cdp_send` in the mutation
  scanner; three plants that scanned clean before are caught after.
- **The CI junit artifact** (950cac8). DISK DISAGREED with the premise that CI
  already uploaded each shard's junit: the artifact carried the JSON reports
  only, which record counts, not per-file seconds. Each shard now keeps its
  junit under a unique name; the totals job reads only JSON, so it counts
  nothing new. The table can be rebuilt from the first green master run
  after the merge.

### P.13 Timings

The merge left the table pricing 170 of 259 test files, under its two-thirds
line. The nine files this branch added were measured by a junit run of those
nine alone, serially, on a busy box (high rather than low): 292 tests, 36.6 s,
the largest the write-receipt guard at 18.9 s. 179 of 260 priced after.

### P.14 Gates run, and what did not run

RUN, with the interpreter the repository's venv holds (3.13) unless said:

- **The post-merge gate**, at 10c6f02: 81 files (every test file the branch
  changes against master, the impact gate's corpus-wide floor, every
  page-string, log, envelope and identity guard, the tool pin, the boundary
  freeze, the three files the order names, the census instruments, the
  adopter's tests), 5 workers, 514.5 s: 5740 passed, 6 failed, 1 skipped, 1
  xfailed. The six are P.10's four and one, and P.13.
- **Slices on the way**, each on the files it touched: the four foundation
  children's files, 170 passed; the redesign's four, 550; the repair, the
  second adopter and the invariant file, 716; the fixtures and identity
  guards, 992; the eight rewritten shaper tests and their controls, 264;
  `test_ci_shard.py`, 131.
- **The final gate**, at 33e0c02: 113 files -- the post-merge selection plus
  every test file that names `threads`, `messaging_overview`, `list_result`,
  `people_data`, `cdp_download`, the server's instructions, either
  conversation tool or `SANCTIONED_MUTATIONS` -- 5 workers, 970.1 s: 6723
  passed, 2 failed, 4 skipped (symlinks this platform will not make), 1
  xfailed. The two failures were claims the DevTools declaration moved: the P
  C8 transport's vocabulary named in `readonly.py`'s prose (red since the
  merge commit -- the post-merge gate had not selected that file, which reads
  the package's TEXT, the data-dependency blind spot a name-scoped selection
  has) and the package docstring's mutation count. Repaired in 1175ba5;
  those two files and six neighbours re-run: 449 passed.
- **The three files the order names** ran in both gates:
  `test_the_package_compiles_on_its_oldest_python.py`,
  `test_gap_rows_on_refused_addresses.py`, `test_ci_shard.py`.

NOT RUN, deliberately:

- **The full suite.** `scripts/impact_gate.py --against master --plan-only`:
  62 changed paths, 242 of 259 test files (93%), which widens to the whole
  suite. By order, not run locally; CI certifies at merge.
- **The 3.10 cell**, except the bounded file (80 passed on 3.10, run by its
  child) and the oldest-Python lint, which reads the source rather than
  running it. CI's matrix runs 3.10.
- **The final gate on the record commit.** The record touches `_audit/` only;
  the census instruments and the register's own tests were re-run on it.

### P.15 Open -- and for other owners

- **Mitigation 6's debt.** `send_invitation` and `send_message` are still
  aimed by a name; converting each to a link or member id the caller supplies
  is the direction, and the debt file fails when one converts.
- **For the next merges, by design.** Every new `target_kind` -- lane L8's
  outward classes among them -- fails `test_no_write_is_aimed_by_a_name.py`
  until it is classified in `TARGET_KIND_CLASS`; a write aimed by a name is a
  ruling change, not a classification. A reader that starts building records
  fails the bounded file until it joins `PEOPLE_TOOLS`, and the instructions
  test until the paragraph names it.
- **Receipts are covered for a library's message, not for page text.** All
  fourteen of the branch's write tools were `not_driven` by the envelope
  guard; `send_invitation`'s preview (`who_this_would_reach`) quotes the label
  its needle matched, and lane L5's `send_reply` preview prints the
  conversation's title, both in the confirm block. Mitigation 6 REQUIRES the
  tool to report whom it resolved before it acts, and mitigation 3 says no
  name in a receipt: the two meet in a preview, and whether a preview is a
  receipt, or should carry that name as a record, is a ruling this lane did
  not make.
- **The insights reader** under `linkedin_who_viewed_me` returns LinkedIn's
  labels and view names as page text: a baselined legacy path, pinned so the
  plant may appear only under `$.insights`. Its `<p>` scan covers viewer rows;
  narrowing it needs a live capture.
- **The overview's group label** comes back in a person record (P.11).
- **Other readers still return names as text** -- the reader baseline's
  legacy inventory holds 40 `returns_text` readers. Not converted, by order.
- **The DevTools declaration and split** (P.10) were made on the precedent of
  ruling (c); both are the orchestrator's to overturn.
- **`PERMANENTLY_FORBIDDEN` holds nine keys; the rulings name six** as the ones
  whose grounds are mitigations. Not touched here: the rulings register is
  another owner's.
- **`INVENTED_NAMES` holds a real historical person's name**, unused in any
  fixture; the fixtures guard accepts that table, so such a name would pass
  there. For the table's owner.
- **The Write tool decodes `\uXXXX` escapes into the characters they name.**
  Twice in this lane a strict-ASCII file received non-ASCII bytes that way;
  the files now build such characters with `chr()`, and the fixtures guard
  asserts its own file stays ASCII.

### P.16 The one cold verification pass

One general-purpose child, cold, adversarial, launched on the final code
(33e0c02) with this record in draft beside it: to break the three people
tools, the redesigned guards, the ratchet, the derivation, the record-typed
reading, the DevTools split and the conversation slot, and to spot-check this
record's numbers. Its findings, and what was done about each, follow in the
next commit.
