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
1175ba5  09-27 15:34  after the merge, found by the final gate: two claims the DevTools declaration moved
dbdc43c  09-27 15:36  lane G record: Foundation: people data (this section, first form)
68d2668  09-27 15:47  lane G record: the branch hashes it cites are disclosed as not yet on master
934a9d0  09-27 16:13  the sanitiser reaches a fixed point, and strips every default-ignorable code point
de826d4  09-27 16:19  the overview reads labels as attributes, decoded; a recipient id only in an id's shape
6c16385  09-27 16:26  the guards harden where the cold verification got past them
b27ecbd  09-27 16:28  the adopters' other text paths are pinned where the cold verification found them
22e6886  09-27 16:29  fixtures: read names where the messaging readers read them
f474851  09-27 16:30  DevTools claims: the scanner and the split see LITERAL calls
```

The last seven are P.16's: what the cold verification found, repaired. This
record's final commit follows them. None of these hashes is on `master`
yet: each does not resolve on `master` until the orchestrator merges this
branch, which is why every one carries its subject.

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
and bidirectional characters, tags, private use, unassigned), and -- since
934a9d0 -- every other default-ignorable code point (the Hangul fillers, the
variation selectors, the combining grapheme joiner and the rest, held to
Unicode's own list); NFC again; runs collapse; a hard cap per field (name
120, headline 220, title 220) cuts and never refuses. It is idempotent, which
is what lets a record REFUSE construction with a field that is not already
its own sanitised form -- an unsanitised record cannot exist. IT WAS NOT, as
first committed, and this section said it was: the cold verification (P.16)
found a strip that joins a base and a combining mark, or two Hangul jamo,
leaving a string that composes only on a second pass, so the record refused
its own builder's output and one such label made both conversation tools fail
with every row lost (4 of 5 planted joins raised). The second NFC pass is the
fix. Links are canonical (`/in/<slug>/` or a member urn; a
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
the record, and -- since de826d4 -- publishes a recipient id only in the
shape the page script captures (`dom.RECIPIENT_ID_SHAPE`, checked again by
`dom.is_recipient_id`): it was published with `str()` alone, beside the
record, so a page answering the id script with the plant published it (P.16).
The landing-interpolation census loses `parse_person_card:slug` with its
ruling entry, with a note. The tool's two other readings are LinkedIn's
aggregates about his viewers, not people, and are pinned as its declared
legacy text paths: `insights`, and `more_analytics` when
`show_more_analytics` is passed (the second found by P.16).

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
Existing verdicts did not move over either committed baseline. ITS LIMITS,
three of them measured by P.16:

- The inventory IS the committed baseline, so a text entry added to it by
  hand passes the ratchet -- the writers refuse it, and only the diff shows
  it; and a text path merged in from another branch's baseline arrives as
  inventory the same way.
- It works PER READER, not per path: a reader already on the inventory can
  return a second field of page text and nothing moves.
- It sees what the default drive reaches. The guards drive every function
  with its defaults, so a path behind an opt-in (`include_names`,
  `show_more_analytics`) is invisible to both baselines: all three people
  tools are `clean` there, no committed entry is `returns_records`, and the
  "lost records" check is armed with nothing to act on. The people tools'
  record paths are held by the invariant file's own drives, not by the
  baselines; `threads.read_conversation_list` returns the raw label in its
  reading with `include_names`, by design -- the reading is not published.

HARDENED on P.16's evidence (6c16385): only an ENVELOPE is the declared
channel (an instance is published without its marker); outside a record the
plant is found by any of its words, case-folded (a first name, a slug,
another case, a no-break space, an entity, a prefix were each
`returns_records` before); the envelope walk descends sets and searches an
object's repr; and a `returns_records` verdict from any tool not in
`PEOPLE_TOOLS` is refused by the envelope guard and its baseline writer,
because an envelope-shaped dict built by hand passes `as_record` by shape.

Each guard shown convicting AFTER the redesign, through its own code: the
reader guard (a record beside page text, a widened record, a plant used as a
key, a record carried out by an exception); the RaisingPage family (a library
message laundered into a record) and its DEBUG log capture (a record's name
in a log record); the page-text rule (a logged record built from the page);
the envelope guard (a record in an `_error` envelope). Plus: the ratchet's
controls, no declared people tool on the text inventory, and no module-level
cache written on the record path (both adopters' functions, with a control
-- which found 1 of the 5 caches P.16 planted until 6c16385 taught it caching
decorators, dotted constructors, `globals()` writes and rooted mutator calls;
5 of 5 after).

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
P.16 found the label slot missing the element the list tool actually reads,
and the open conversation's title: both are read by class token since
22e6886 (3 elements and 1 title, all declared).

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
planted shapes, each convicted by exactly the rules it breaks -- one, or two
for `range(pages)`, which is both a paging parameter and an unbounded loop --
and no other (16af667's message says twelve; the table holds thirteen). 80
passed on 3.13 and on 3.10 at 16af667 (which does not resolve on `master`
until this branch merges); the file has grown since. P.16 built
records through three routes it did not derive -- another module's
`people_data` attribute, `RECORD_TYPES`, `getattr` -- and all three are
derived since 6c16385; a hand-built envelope dict is not, and is held instead
by the envelope guard's `PEOPLE_TOOLS` check (P.4). Its dated census was
re-measured on the merged tree: 157 `page` parameters (152 first, 5 after
`navigator`), 13 `before` and 9 `after`. `linkedin_open_messaging` loads two
pages -- the receipt guard's list, then `/messaging/` -- and its names come
from the second only.

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
into a function each test already reads turns it red (8 of 8, the old
failure kept) and the same parameter annotated as a record turns it green (8
of 8). P.16 measured the other case: a NEW function taking `name: str` turns
only 5 of the 8 red, because the two `groups` tests and the `anchors` test
read fixed lists of functions -- as they did before the rewrite, which kept
their structure. `**kwargs` passes all eight; a class whose metaclass equals
anything was admitted as a record until 6c16385 compared by identity. The
reading's own controls are `tests/test_a_name_enters_a_shaper_only_as_a_record.py`.
On the real tree none of the seven modules takes such a parameter.

### P.10 The one integration: master 2eb90ad

Merged at 10c6f02 (which does not resolve on `master` until this branch
merges), after the foundation's own commits and before the second
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
The fifth was `send_reply`'s kind (P.8); the sixth the timings (P.13). ALL OF
IT READS SYNTAX: P.16 sent an input method over DevTools three ways the
scanner cannot see -- a bound-method alias, a send handed to a helper,
`getattr` -- and 2263 tests passed identically with and without them.
f474851 corrects every sentence that claimed more (the scanner holds every
LITERAL call), including lane D's docstrings, which still said the scanner
had no DevTools pattern at all.

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

WHAT P.16 FOUND HERE, and what was done. The sanitiser crash (P.2) took down
both tools with `include_names` -- fixed. `messaging_overview` read labels
with a pattern over the serialised page, so a message whose words spelled a
label became a row, its "name" the words and markup after it, and no entity
was decoded: it reads labels as ATTRIBUTES with an HTML parser since de826d4.
And `linkedin_open_messaging` publishes the filter controls it finds -- each
one's accessible name and href -- outside any record: pinned since b27ecbd as
its declared legacy path, the plant leaving a record only under `filters`.
That finding's other half is NOT this lane's: asking for a filter can press a
control that is not a pill, because `dom.activate_messaging_filter` matches
the word inside any label (P.15).

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
- **The final gate**, at 33e0c02 (which does not resolve on `master` until
  this branch merges): 113 files -- the post-merge selection plus
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
- **At the first record's head** (68d2668), the ordered guards and the three
  named files again: 920 passed. The record's own files through
  `scripts/impact_gate.py --paths`: 42 files, 2423 tests, PASS -- its first
  run refused on two branch hashes cited "at" a gate, disclosed in 68d2668.
- **Python 3.10.19**, through `uv run --python 3.10`: 26 of the files this
  lane changed -- the foundation's own, the rewritten shaper tests, the
  messaging overview, the boundary freeze, readonly, the reader and envelope
  guards, the landing census, the tool and shape tests, `test_ci_shard.py`
  and the two files the final gate caught -- 1860 passed.
- **After P.16's repairs**, each on the files it touched: the sanitiser's
  consumers 413; the overview, recipient, messaging, viewer, connections,
  reader, envelope, landing and page-text files 1417; the seven guard files
  755; the fixtures guard 56; the DevTools claims' files 474. Each repair was
  also shown by re-running the verifier's own repro on the repaired tree.
- **The final gate, again, over all of it**, at 00cd2cf (a hash which
  does not resolve on `master` until this branch merges): 114 files -- the post-merge
  selection recomputed, every test file naming a changed symbol, the census
  and register instruments -- 5 workers, 701.2 s: 6780 passed, 0 failed, 4
  skipped (symlinks this platform will not make), 1 xfailed.

NOT RUN, deliberately:

- **The full suite.** `scripts/impact_gate.py --against master --plan-only`:
  62 changed paths, 242 of 259 test files (93%), which widens to the whole
  suite. By order, not run locally; CI certifies at merge.
- **The 3.10 cell for the browser-driven files** (the messaging threads, the
  viewer fixtures): under `uv` they would resolve a Playwright whose browser
  build this box's shared cache may not hold. CI's matrix runs 3.10.

### P.15 Open -- and for other owners

- **Mitigation 6's debt.** `send_invitation` and `send_message` are still
  aimed by a name; converting each to a link or member id the caller supplies
  is the direction, and the debt file fails when one converts.
- **HIGH, for `dom.activate_messaging_filter`'s owner (P.16).** Asking
  `linkedin_open_messaging` for a filter can PRESS A CONTROL THAT IS NOT A
  PILL: the activator matches the filter word inside any label
  (`get_by_role(..., exact=False)`), and the composer's list draws no "Other"
  pill, so `message_filter="other"` presses whatever control's label contains
  the word -- on a planted page, a non-pill button. It is a sanctioned click
  on a read path, and it predates this lane; changing a sanctioned mutation
  is not this lane's scope. Repro: the verifier's
  `scratchpad/lane-g/cold2/r03b_filter_click_label.py`.
- **Where a viewer's member id lives.** Mitigation 1's record has one
  identity slot, "profile link or member id"; the viewer row carries both, the
  link inside the record and the recipient id (a member id, now shape-checked)
  beside it. Inside it as a fifth field, or beside it as today, is the
  orchestrator's call.
- **For the next merges, by design.** Every new `target_kind` -- lane L8's
  outward classes among them -- fails `test_no_write_is_aimed_by_a_name.py`
  until it is classified in `TARGET_KIND_CLASS`; a write aimed by a name is a
  ruling change, not a classification. A reader that starts building records
  THROUGH A RECORD CLASS fails the bounded file until it joins
  `PEOPLE_TOOLS`, and the instructions test until the paragraph names it; one
  that hands back envelope dicts built by hand is caught only if the envelope
  guard drives it (P.4, P.6). And after this merges a new tool that returns
  page text cannot be recorded by regenerating the baseline: the writer
  refuses it, by design.
- **Receipts are covered for a library's message, not for page text.** All
  fifteen write tools (lane L5's `send_reply` among them) were `not_driven`
  by the envelope guard; `send_invitation`'s preview (`who_this_would_reach`) quotes the label
  its needle matched, and lane L5's `send_reply` preview prints the
  conversation's title, both in the confirm block. Mitigation 6 REQUIRES the
  tool to report whom it resolved before it acts, and mitigation 3 says no
  name in a receipt: the two meet in a preview, and whether a preview is a
  receipt, or should carry that name as a record, is a ruling this lane did
  not make.
- **The people tools' legacy text paths**, pinned, not converted:
  `linkedin_who_viewed_me`'s `insights` (LinkedIn's labels and view names; its
  `<p>` scan covers viewer rows, and narrowing it needs a live capture) and
  `more_analytics`, and `linkedin_open_messaging`'s `filters`. The pins are
  in the invariant file; the ratchet cannot see them (P.4).
- **The overview's group label** comes back in a person record (P.11).
- **Other readers still return names as text** -- the reader baseline's
  legacy inventory holds 40 `returns_text` readers. Not converted, by order.
- **The DevTools declaration and split** (P.10) were made on the precedent of
  ruling (c); both are the orchestrator's to overturn.
- **`PERMANENTLY_FORBIDDEN` holds nine keys; the rulings name six** as the ones
  whose grounds are mitigations -- the other three are the outward classes
  lane L8 is building behind grants, in flight. Not touched here.
- **`INVENTED_NAMES` holds a real historical person's name**, unused in any
  fixture; the fixtures guard accepts that table, so such a name would pass
  there. For the table's owner.
- **The Write tool decodes `\uXXXX` escapes into the characters they name.**
  Twice in this lane a strict-ASCII file received non-ASCII bytes that way;
  the files now build such characters with `chr()`, and the fixtures guard
  asserts its own file stays ASCII.

### P.16 The one cold verification pass

One general-purpose child, cold and adversarial, launched at 33e0c02 with
this record in draft beside it -- which was not the final code: 1175ba5
landed while it ran, and it said so. It was told to break the three people
tools, the redesigned guards, the ratchet, the derivation, the record-typed
reading, the DevTools split and the conversation slot, and to spot-check this
record's numbers. It edited nothing tracked; its scripts and outputs are in
the scratchpad's `lane-g/cold2/`. It found 4 HIGH, 8 MEDIUM and 6 LOW, and
the spot-checks it ran held (the commit times, the counts in P.8 and P.6's
messages, the pins, the digests, the timings, the caps).

| finding | severity | done |
|---|---|---|
| F1 `open_messaging` publishes filter controls' labels outside records; asking for a filter can press a non-pill | HIGH | labels pinned as a legacy path (b27ecbd); the press reported (P.15) |
| F2 the redesigned verdicts pass respelled plants, sets, instances and hand-built envelopes | HIGH | hardened (6c16385), each shape now convicted; the hand-built envelope held by the `PEOPLE_TOOLS` check |
| F3 the sanitiser is not idempotent; one label crashed both conversation tools | HIGH | fixed (934a9d0), P.2's claim corrected |
| F4 `who_viewed_me(show_more_analytics=True)` leaves text outside records unseen | HIGH | pinned as the tool's second legacy path (b27ecbd) |
| F5 267 default-ignorable code points survived the sanitiser | MEDIUM | stripped, held to Unicode's list (934a9d0) |
| F6 the inventory and ratchet claims overstated | MEDIUM | the limits stated in P.4 |
| F7 records built through three underived routes; no tie between records and `PEOPLE_TOOLS` | MEDIUM | the routes derived and the tie added (6c16385); the hand-built route stated |
| F8 a DevTools send through an alias, a helper or `getattr` passes every check | MEDIUM | the claims corrected to literal calls (f474851); the scanner's limit stated |
| F9 the conversation slot missed the element the list tool reads, and the thread title | MEDIUM | both read by class (22e6886) |
| F10 `recipient_id` published with `str()` only, beside the record | MEDIUM | shape-checked (de826d4); where it lives is for the orchestrator (P.15) |
| F11 overview labels undecoded, and message text could forge a row | MEDIUM | read as attributes, decoded (de826d4) |
| F12 the record-typed reading: new functions in fixed-list tests, `**kwargs`, a metaclass trick | MEDIUM | the metaclass closed (6c16385); the rest stated in P.9 |
| F13 the cache check caught 1 of 5 planted caches | LOW | 5 of 5 (6c16385) |
| F14 P.0 missed 1175ba5; P.16 called 33e0c02 final | LOW | corrected, here and in P.0 |
| F15 P.15 said fourteen write tools | LOW | fifteen, corrected |
| F16 the bounded file's census stale after the merge | LOW | re-measured (6c16385) |
| F17 lane D's docstrings said the scanner had no DevTools pattern | LOW | corrected (f474851) |
| F18 "no other rule" for a plant convicted by two, by design | LOW | P.6 reworded |

Its runs could not settle two things, and it said so: the gate totals
(5740/6 and 6723/2), which it did not repeat, and the pre-adoption "four
viewers, twice" red evidence of P.3, which predates its checkout.

## Order of 2026-09-27 17:05: three fixes, a ruling, and the integration

The orchestrator's order to lane G, 2026-09-27 17:05 IST. It ratified the
three decisions the foundation left overturnable (the `cdp_download`
declaration and the read-path split, integrating before the second adopter,
the member id beside the viewer record); ordered three fixes the lane had
found -- each shown failing first -- and one ruling registered and encoded;
and made one integration conditional on lane L8 landing. It did land, so it
was integrated. Disk agreed with the order's sample at the start (head
ad5b50a, clean, 43 ahead of master 2eb90ad, master an ancestor of it).

### Q.0 Commits, with their times from `git log`

```
6ae18a6  09-27 17:19  messaging filters: a pill is pressed by its EXACT name, and a decoy containing the word is refused
69dab16  09-27 17:46  invented names: the entry that named a real historical figure is replaced, everywhere it was carried, and held out by digest
bc5e735  09-27 17:48  cited-hash guard: a disclosure's wording is read across line wraps
5c524e6  09-27 18:14  PREVIEW-NAMES-THE-RESOLVED-TARGET: registered, and the two previews that name a third party carry a people record
9baf73b  09-27 18:38  merge master 7986ae3 into lane G: lane L8's outward classes meet lane G's foundation
ca5a0f6  09-27 19:15  full gate: two of lane G's own reds, found when the whole suite first ran here
```

This record's commit follows them. None of these hashes is on `master` yet:
each does not resolve on `master` until the orchestrator merges this branch.

### Q.1 Item 1 (HIGH): a filter pill is pressed by its EXACT name

`dom.activate_messaging_filter` found the pill with `get_by_role(name=word,
exact=False)`, a substring match, so `message_filter="other"` -- the
composer's list draws no "Other" pill -- pressed whichever button's name
merely contained the word, and published its whole label.

RED FIRST, in a real headless Chromium,
`tests/test_a_filter_pill_is_pressed_by_its_exact_name.py` on the old
activator: a decoy "Others from <plant>" was PRESSED for `other`; an exact
"InMail" pill beside a decoy "InMail from <plant>" was not pressed (two
substring matches, refused); the rule said True for "InMail messages". 6
failed.

The fix: `dom.filter_name_matches`, the one predicate the activator and the
enumerator share, is exact equality with case and whitespace folded. The
activator still finds candidates by substring, reads each one's accessible
name, and presses only when exactly one EQUALS the word; otherwise it presses
nothing and says what it saw as counts -- `found` (exact) and `containing`
(substring) -- never a label, because a label it did not press is page text.
`pill_label` is now the pressed pill's own spelling of the word. The
enumerator compares the accessible name (aria-label, else text), not the two
joined. The one click line stays in the function, so the sanctioned-mutation
table does not move. After: the new file, 11 passed; on the tracked
compose-list fixture the five measured pills are each pressed by exact name
and `other` is refused. The verifier's r03 and r03b, re-run: nothing pressed
that is not a pill, nothing outside a record. Tests that pinned the old leak
moved to the new truth: the unread-readings file's page-text field set is
now EMPTY, still pinned; the enumerator's agreement test covers both halves;
the open_messaging `filters` pin now asserts nothing leaves at all.

MEASURED, NOT ENDORSED: `focused` IS pressed on the fixture -- the folder
dropdown's trigger is named exactly "Focused", and pressing it opens the
folder menu rather than filtering. Whether the activator should also require
a pill's own markers (`aria-pressed`, the filter-pill hook) is the
activator's owner's call; the test pins what happens now.

### Q.2 Item 2: the invented-names entry that named a real historical figure

The first entry of `INVENTED_NAMES` named a real historical figure, under a
comment reading "People, all invented". It is not named in this record
either.

RED FIRST: three tests in `tests/test_a_person_name_is_never_a_literal.py`
hold retired real names as SHA-256 digests of the folded name, never the
name. On the old tree the table check found the entry (digest prefix
e71d025a0b49) and a sweep of tracked tests/ and scripts/ found it in six
files, ten places: 2 failed. A control retires an invented pair at runtime
and finds it beside another capitalised word.

It is replaced by a plainly invented name, "Wren Fixturewright", in the
table and in every file that carried it: two person constants
(`OTHER_AUTHOR` in `tests/test_activity_items.py`, `MEMBER_NAME` in
`scripts/_probe_interests_entity_shaping.py`) and literal fixtures in
`tests/test_compose_fields.py` (with its split first and last words),
`tests/test_shape.py` and `tests/test_surface_census.py`. The shape each test
reads is unchanged. After: 1362 passed.

### Q.3 Item 3: the cited-hash guard reads a disclosure across a line wrap

`scripts/check_cited_shas_resolve.py` searched its "does not resolve"
vocabulary one line at a time. RED FIRST: three wrapped disclosures --
between words, inside emphasis, and with a list item's indented continuation
-- all came back CANDIDATE: 3 failed. The emphasis-stripped lines are now
searched JOINED, so the vocabulary's own `\s+` folds the newline and any
continuation indent, and a match marks every line it spans. It can only add a
disclosure; `PINNED` holds no bad citation for it to clear. Not read across:
a wrap that inserts a non-space character, such as a blockquote's `> `.
After: the guard, the audit-index and import-safety files, 318 passed.

### Q.4 Item 4: PREVIEW-NAMES-THE-RESOLVED-TARGET

- `_audit/2026-09-27-rulings-previews-and-receipts.md`: the orchestrator's
  document, copied byte-identical (`cmp`). NO DOCUMENT GUARD OBJECTED; not a
  word of it changed.
- REGISTER: the entry with the ordered id, claim, binds, document, anchor
  and note. RULINGS.md regenerated to a fixed point; its RULED declaration is
  claimed.
- ENCODED, RED FIRST: `tests/test_a_preview_names_the_resolved_target.py` on
  the old previews, 3 failed -- prose where a record belongs. Now
  `send_invitation`'s preview carries in `who_this_would_reach` a
  `people_data.Person` envelope holding the name inside the control's label
  ("Invite <name> to connect"; the whole label if drawn otherwise), and
  `send_reply`'s the conversation's title, each sanitised, capped and marked;
  the instruction to CHECK it moves to `who_this_would_reach_check`, prose
  with no page text. The writes.py change is one function's tail and one
  import line, kept minimal for lane L5.
- NOTHING A WRITE KEEPS CARRIES THE NAME, measured where this package keeps
  anything: a write writes nothing to disk, so what outlives a call is the
  grant store, the observation store and the log records. After an
  invitation preview (on a grantable spec, so a grant exists to keep it) and
  after a reply is previewed, redeemed and FIRED, none carries the name, the
  receipt carries none, and each grant's target is the caller's own. Each
  check is shown convicting a planted regression.
- THE BOUNDED-READER DERIVATION STOPS AT THE WRITE DOOR. The preview
  builders are reached by name through `writes.preview` and then
  `server._write_tool`, the one door every write tool calls; crossing it
  declared all fifteen write tools people readers and refused the write
  path's loops (3 failed, measured). The builders only the door reaches are
  declared (`PREVIEW_BUILDERS`) and held equal to what is found behind it; a
  control shows the stop hides nothing else, and that a function of the
  door's name elsewhere re-opens the path loudly, by name.
- After: 1737 passed over the previews, writes, the write door, the bounded
  file, people data, the page-string, log and envelope guards and the
  rulings, audit-index, census and cited-hash instruments.

### Q.5 Item 5: the integration of master 7986ae3 (lane L8)

When items 1-4 were committed, master's log showed lane L8's head, a
fast-forward past 2eb90ad (18 commits). Integrated in one merge commit
(the last row of Q.0).

- (a)-(e) Conflicts, from both sides: perform's `click_error` keeps lane G's
  type-only form for every action, which covers L8's type-only form for its
  menu item actions; `__init__.py` reads sixteen write tools and fifteen
  sanctioned mutating calls, both histories kept; REGISTER keeps L8's two
  entries and this order's one; `PERMANENTLY_FORBIDDEN` is master's six,
  identical by value; the timings table takes both sides' entries (181, none
  priced differently by the two) and re-derives its totals (1638.9 s); the
  generated files come from master's copies, regenerated to a fixed point,
  67 rulings.
- (f) This lane's guards against L8's code: `group_id` classified `id` in
  `tests/test_no_write_is_aimed_by_a_name.py`; the receipt guard convicted
  L8's withdraw verification returning `str(exc)`, now composed from the
  type and the withheld landing; the fixtures guard gains two GROUP slots (a
  group link's text, and the "More options for X" label L8's fixture says
  carries the group's name) and declares L8's six invented group names in
  `SYNTHETIC_GROUPS`; and group_leave's five readers -- `identifier: Any`, so
  the reader guard handed them a page double that four refused on their
  first line, recorded clean having read NOTHING -- are now driven with a
  five-digit numeric id: 0 page reads before, 5 to 6 after, all five clean.
- (g) Counts re-derived on the merged tree, measured off the registry: 57
  tools, 16 write, 17 sanctioned actions. README ("Fifty-seven tools ship.
  Forty-one read. Sixteen write."), the server's instructions and
  `__init__.py` (sixteen write tools, fifteen sanctioned mutating calls)
  say the same, and the tests that read those sentences are green in the
  whole suite (Q.6).
- (h) Pins: the tool surface measured at 57 tools and 90 parameters (master's
  57 and 89, and this branch's `item`); the boundary digests unchanged from
  this branch's -- L8 did not touch `readonly.py`.
- (i) A repeated-key check over every dict and set literal in
  `linkedin_server/`, `tests/` and `scripts/` (4638) and every JSON file:
  two hits, both older than this merge and neither this lane's (Q.8).

### Q.6 The whole suite, first run on this branch: two of this lane's own reds

The merge's impact set widened to the whole suite (57 changed paths select
253 of 264 test files), so the whole suite ran, on the merge commit with a
clean tree: 264 files, 6 workers, 1426.5 s -- 10921 passed, 2 failed, 9
skipped, 1 xfailed. THIS BRANCH HAD NEVER RUN IT: F.12, I.6 and P.14 each
name it as not run, and every gate they list is a selection. Neither
failure came from the merge. Both are this lane's, red since 2026-09-24:

- `tests/test_apply_modal_fixture.py::test_a_proceeding_gate_appends_the_second_click`,
  red since F.3's commit (`da3354d`), proved the two-click loop's second
  click by reading its selector back out of `clicked.error` -- the leak F.3
  closed when that field became the exception's type alone. The proof moves
  to the page: a recorder of every selector `perform` hands `page.click`,
  installed after the preview. The receipt is held to the type
  (`TimeoutError`, measured). A control -- a refusing gate handing back the
  same sentinel -- shows the record saying no, holding one press, the apply
  control's; a plant emptying `TWO_CLICK_ACTIONS` shows the new assertion
  failing.
- `tests/test_an_outage_is_never_filed_as_an_absence.py`, red since I.4's
  commit (`2e3aad2`): `scripts/py_baseline_lint.py`'s `_pieces` answered `[]`
  when the tokenizer refused, a refusal reading as a file with no string
  pieces. It answers None now -- no piece table, not an empty one -- and the
  caller judges by the node's own quote as before, tracking "tokenized once"
  with its own flag. A new test drives the refused branch, which no test
  ran: None, and L7's line convicted by the fallback. The pre-fix module
  fails it, answering `[]`.

Both hashes above are this branch's and do not resolve on `master` until it
merges. BOTH FILES WOULD HAVE BEEN SELECTED by today's `scripts/impact_gate.py`
(measured with `--plan-only`): a `writes.py` change selects the apply file,
which imports it, and a `scripts/` change selects the outage guard, which
sweeps the directory. The impact set widened to the whole suite at every
gate, the whole suite was not run, and the selections built in its place
missed both: F.12's lesson about the items' hand-picked selections holds
for the gates' symbol-built ones too.

### Q.7 Gates run, and what did not run

RUN, with the venv's 3.13 unless said. Each item's red came first (Q.1-Q.4).

    gate                                         result
    item 1: the new file                         11 passed
    item 1: activator, enumerator, thread-id,    476 + 456 passed
      leave-the-address, readonly, surface
      and invariant files
    item 2: the guard and every file that        1362 passed (23 min: another
      carried the name                           session's full suite held the
                                                 CPU at 100%)
    item 3: the guard, audit-index and           318 passed
      import-safety files
    item 4: 24 files -- previews, writes, the    1737 passed, 391 s
      write door, the bounded file, people
      data, the page-string, log and envelope
      guards, the rulings, audit-index, census
      and cited-hash instruments
    the merge, before its fixes: 38 files        2084 passed, 3 failed -- Q.5 (f):
                                                 `group_id` unclassified (the rule and
                                                 its control) and L8's `str(exc)`
    the merge's fixes: the fixtures guard, the   98 passed; the reader guard, 502
      no-name-aim rule and the receipt guard
    THE WHOLE SUITE, on the merge commit         10921 passed, 2 failed (Q.6)
    Q.6's repairs: the three files               67 passed
    Q.6's repairs, CPython 3.10 through uv:      28 passed
      the two non-browser files
    the impact gate over Q.6's three files       58 files, 2898 passed, 696.9 s;
                                                 NOT CHECKED, as it prints: 206 of 264
                                                 files
    CPython 3.10.19 through uv, with the         797 passed, 4 workers, 288 s;
      requirements: the 25 changed test modules  clean tree, head `ca5a0f6`
      that name no browser
    the plants and controls                      each new check shown failing on the
                                                 regression it exists for (Q.1-Q.6)

WHEN EACH RAN, from the stamps: item 4's gate and the merge's first gate
ran on the working tree before their commits (their stamps say tracked-dirty);
so did the impact gate over Q.6's repairs, whose tree `ca5a0f6` committed
unchanged. The whole suite ran on the committed merge, clean.

NOT RUN:

- **The whole suite after Q.6's repairs.** Their impact set ran instead
  (58 files), beside the whole suite on the merge commit.
- **The 3.10 cell for the 15 changed test files that name Playwright or a
  browser page** -- the filter pill, the previews, the apply fixture, the
  messaging overview and the writes files among them: under `uv` they would
  resolve a Playwright whose browser build this box's shared cache may not
  hold. CI's matrix runs 3.10.
- **CI on any platform** (nothing pushed), **a cold verification pass**
  (this order did not ask for one), **anything live**.
- **The timings table** was not re-priced: this order's two new test files
  are unpriced, and it prices 181 of 264 files, five above its two-thirds
  line.

### Q.8 Open, for other owners

- The folder trigger named exactly "Focused" is pressed by `focused` (Q.1).
- A second real historical figure's name, not on `INVENTED_NAMES`, appears
  in `dom.py`'s docstrings (5 lines), five test files (17 lines) and two
  audit documents; no guard fired on it in the whole suite. The
  retired-name digest table (Q.2) can hold it once its owners choose a
  replacement. It is not named here either.
- Both previews' people records carry a name and an empty headline: the
  markup each reads draws none. `send_reply`'s record is a person even for a
  group conversation, whose title may be a group's name or several people's.
- Mitigation 6's two debts stand: `send_invitation` and `send_message` are
  still aimed by a name (P.15), measured again on the merged registry.
- `tests/test_selectors_resolve.py`'s selector table repeats one key, so its
  first entry is silently overwritten and one selector is never resolved;
  `tests/test_api_call_sites.py` repeats a set element (harmless). Both
  predate this merge.
- 19 `_audit/` documents, this record among them, open with a bare model-id
  line above their title. No ruling about it was found in the register or
  the corpus; if it was never ruled, it is model attribution in tracked
  files. Not changed here: it spans every lane's records.
- The ratchet's limits of P.4 stand: per reader, default drives only.

## Order of 2026-09-27 19:52: the residuals

The orchestrator's order to lane G, 2026-09-27 19:52 IST, after master was
fast-forwarded to this branch: five calls on what the 17:05 section left
open. Disk agreed with its sample at the start (head 52b55b6, master the same
commit, a clean tree). The duplicate selector key and the two name-aimed
writes went to lane L5, as the order said, and are not touched here.

This record carried a bare model-id line above its title until this order,
like eighteen others; R.1 removed it, and this section is written without
one.

### R.0 Commits, with their times from `git log`

```
e42f3e2  09-27 20:37  model attribution in files: nineteen records opened with a bare model-id line; removed, and a guard keeps it out
1a8fdea  09-27 20:38  messaging filters: a pill is found inside the one filter bar, by its structure, and only then matched by exact name
9e323b5  09-27 20:39  invented names: the second real historical figure is replaced, everywhere it was carried, and the digest sweep reads the whole tracked tree
4829bac  09-27 20:39  preview records: a headline read where the page draws one, ABSENT where it does not, and a group conversation named by its title record
23dc463  09-27 20:40  tests: the ABSENT-versus-empty test's planted characters are written as escapes
d9425be  09-27 20:41  ci shard timings: this lane's three unpriced test files priced
bde6892  09-27 21:18  model-id guard: its docstring carries the measured count of the records it cleaned
```

This record's commit follows them. None of these hashes is on `master` yet:
each does not resolve on `master` until the orchestrator merges this branch.

### R.1 The model-id lines: removed, and a guard

MEASURED over all 892 tracked files, with the anchored pattern the order
gave on line 1: nineteen, every one under `_audit/` -- twelve dated
2026-09-23 and seven 2026-09-24, twelve of them named for a lane, this one
among them -- each the id, then exactly one blank line, then the title. No
such line anywhere below line 1. Each lost those two lines and nothing else:
19 files, 38 deletions. How any document mentions a model in prose did not
change. (The strip's commit message and the guard's first docstring said
"nine lanes' records": a count nobody had taken. The docstring now carries
the measured one.)

One line pointer into those documents existed, found by a census of every
tracked reference of the form path-and-line: a test docstring citing the
lane L4 record's lines 48-49, now 46-47, the same two lines of text.

`tests/test_no_tracked_file_opens_with_a_model_id.py` enumerates the tracked
set -- so the impact gate derives it onto its corpus-wide floor, which moved
from 23 guards to 24 -- and holds line 1 to the pattern, after removing a
byte-order mark and a CR. RED FIRST: on the tree before the strip, 19
offenders. Its controls convict the measured shape planted in a throwaway
repository and five spellings of a bare header, and pass seven that are not
one: prose on line 1, prose in the body, a sentence opening with an id, an
id below line 1, an indented one, an uppercase one, and a binary file.

THE CALL IS NOT IN THE REGISTER. It reached this lane in an order, not a
tracked document, and a register entry needs a document and an anchor to
resolve against. The guard encodes it; registering it is the orchestrator's.

### R.2 The `focused` mis-aim: a pill is found inside the one filter bar

MEASURED FIRST, off both 2026-09-20 messaging captures (gitignored; hook
names, tags and roles only, no text read): inside `<main>`, exactly one
`div[role=radiogroup]` carries `data-test-messaging-inbox-filters__filter-pill-group`
and holds the five pills, `button[role=button][aria-pressed]` carrying the
pill hook and no aria-label. The folder trigger carries
`...__folder-pill` inside its own `...__folder-dropdown`, beside the bar.

RED FIRST, on the exact-only activator in a real headless Chromium: 5 failed.
The folder trigger named exactly "Focused" was pressed for `focused` (its
recorder read `['folder']`); a namesake outside the bar was pressed; the
pill beside its outside namesake was refused, two exact names found; a
hooked button outside any bar was pressed; two bars were not told apart.
HEAD's enumerator, on the same pages, reported `focused` and the outside
`unread` as pills (scratchpad `lane-g/enum_red.py`).

The fix: `dom.FILTER_BAR_HOOK` and `dom.FILTER_PILL_HOOK`, measured. The
activator needs exactly one bar (`main [bar hook]`); inside it only hooked
buttons are pills; each pill's accessible name is compared by the shared
exact rule. Anything else is refused without a press, with `bars`, `pills`
and `found` as counts. The enumerator reads the same bar, with an HTML
parser rather than a pattern, and reports `filter_bars`. `focused` and
`other` are the folder's choices, not pills: both are refused on the
measured page, and the tool's docstring says so. The synthetic composer
fixture gained the two hooks it lacked. After: the eleven affected test
files, 1099 passed.

AND A CONTROL THIS LANE HAD BROKEN. `scripts/_check_the_unread_readings_guard_can_fail.py`
drives the unread-readings tests by name, and item 1 of the 17:05 order
renamed three of them; the script died on an AttributeError at its pill
section and convicted nothing there. Re-pointed at the tests that exist and
at the path each plant reaches -- the refusal and the success: 11 of 11
convictions.

### R.3 The second real historical name

Replaced by a plainly invented name, "Tamsin Stubworth", wherever it was
carried: `dom.py`'s docstrings, five test files and two audit documents,
with the forms the tests read kept in shape -- a given name and an initial,
a near miss sharing a prefix and in no prefix relation, the split words, the
name followed by a digit. A first choice reused the given name of an existing
synthetic person and was renamed before its commit. The quoted assertion
output in the activity-items slice record carries the new name.

RED FIRST: its folded digest joined `RETIRED_REAL_NAMES_SHA256`, and the
sweep widened from `tests/` and `scripts/` to every tracked text file --
the old sweep could not see the package or the records, where it lived. On
the previous tree: 23 sites in 8 files, every one this digest (prefix
177f85df57ad). The first retired name was found nowhere in the whole tree.
The control now asserts the sweep reaches all four folders.

### R.4 The preview records: a headline where one is drawn, ABSENT where not

`people_data.ABSENT` is `None`: a headline no reading drew, where `""` is
one drawn empty. A `Person` defaults to ABSENT, and `as_record` rebuilds
both. `None` rather than a sentinel string, because a string can be forged
by the page it describes. The viewers list's anonymised row, which draws no
headline, now says ABSENT as well.

- THE REPLY. MEASURED on the one captured conversation header (class tokens
  and a has-text boolean only): its `dl` holds the title's `dt` and exactly
  one `dd.msg-entity-lockup__entity-info`, holding text. That line is now
  read. That it is a member's headline is DERIVED: the captured
  conversation was sponsored. Whether the conversation is a group is read
  off its row in the list, drawn active on the thread page, carrying the
  list reader's multiple-participants facepile -- placement measured on
  both captures: 3 such images, all inside one row's link, the element
  that wears the active marker. One other member names a person; a group,
  or a row the page does not draw, comes back as the conversation's title
  record, the record the list returns for a group row; two lines under the
  title name nobody.
- THE INVITATION. What is read is one control's label, which draws a name
  and no headline: ABSENT. The rail card around the control has never been
  captured, so no headline is guessed at.

RED FIRST, with HEAD's `people_data` and `threads` put back for the run
(only the name `ABSENT` added, so each failed on behaviour): 6 failed. The
seventh new case, a line drawn empty reading `""`, passed on HEAD too: it is
the other side of the distinction. After: 13 passed.

THE BOUNDED-READER GUARD FOUND THE SHARED BUILDER, as it is built to:
`threads.conversation_with` is now reached from behind the write door as
well as from the list reader, and the declared set gains it with that
reason. The derived people tools are unchanged: the viewers list, the
conversation list and open_messaging.

THE 17:05 SECTION'S Q.8 SAID the markup each preview reads draws no
headline. That held for the invitation's label and did not hold for the
reply: the header draws a line under the title, on the capture and in the
fixture, and nothing had read it.

AN ASCII SLIP, CAUGHT AND REPAIRED. The editor wrote this item's two planted
invisible characters into a test as the characters themselves, from the
escapes typed; the staged-line check reported the one line and the commit
went ahead of it. The next commit writes them as escapes. Every line this
order added, measured against 52b55b6: no non-ASCII character.

### R.5 Timings

CI already keeps each shard's junit in that shard's uploaded artifact (the
09-24 step "Keep this shard's junit for the timings table"), so, as the
order said, nothing in CI changed. Priced here: this lane's three unpriced
test files -- the filter-pill and preview files from the 17:05 order, the
model-id guard from this one -- by a junit run of those files alone,
serially, on this laptop: 44 tests, 83.6 s. The table prices 184 files,
1722.5 s.

### R.6 Gates run, and what did not run

RUN, with the venv's 3.13 unless said. Each item's red came first (R.1-R.4).

    gate                                         result
    item 2: the eleven affected test files       1099 passed
    item 2: the unread-readings control script   11 of 11 convictions
    items 1, 3, 4, 5: twenty affected files      1085 passed, 1 failed, 3 skipped:
                                                 the shared builder of R.4, then
                                                 declared -- that file 85 passed
    item 4: the preview file                     13 passed; the people-data file,
                                                 after the escape repair, 79
    item 5: the shard tests over the table       131 passed; the pricing run, 44
    THE IMPACT GATE ON THE FINAL TREE, at        46 changed paths select 242 of 265
      d9425be (which does not resolve on         test files (91%), so it WIDENED TO
      `master` until this branch merges)         THE FULL SUITE: PASS, 10968 tests,
                                                 2029.8 s, a clean tree -- beside
                                                 another session's full-suite gate
    CPython 3.10.19 through uv, with the         630 passed, 3 skipped (symlinks this
      requirements and Playwright pinned to      platform will not make), 4 workers,
      the venv's 1.63.0: every one of the 17     157 s; clean tree
      test files this order changed
    this record and the register entries: the    128 of 265 test files (48%, the
      impact gate over the two documents, on     register couples widely), so it
      their text staged before this commit --    WIDENED TO THE FULL SUITE: PASS,
      the new guard and every document guard     10968 tests, 1344.9 s; the cited-hash
      among it                                   guard alone, OK

WHEN EACH RAN, from the stamps: the item runs and the twenty-file selection
ran on the working tree before their commits; the impact gate and the 3.10
cell ran on committed trees, clean.

THE 3.10 CELL REACHES THE BROWSER FILES NOW. Every earlier section of this
record left the 3.10 cell for the browser-driven files unrun, because `uv`
would resolve the newest Playwright, whose browser build the shared cache may
not hold. Pinning the venv's own version (`playwright==1.63.0`, which the
requirement `>=1.40` admits) resolves the build the cache already holds; a
browser test run that way passed first, alone, before the whole set ran.

NOT RUN:

- **CI on any platform** (nothing pushed), **a cold verification pass**
  (this order did not ask for one), **anything live**.
- **The whole suite on 3.10**: the cell above is this order's changed test
  files, as ordered, not the suite.

### R.7 Open, for other owners

- THE TIMINGS FLAG TAKES ONE JUNIT, AND CI KEEPS ONE PER SHARD.
  `ci_shard.py --write-timings` reads a single report; a green CI run leaves
  one per shard per cell. Rebuilding the table from CI needs one cell's
  shard reports combined, or the flag taught to read several. Not built:
  the order stopped item 5 at the upload.
- WHERE THE INVITATION RAIL DRAWS A HEADLINE is uncaptured; a capture of
  the profile rail's card settles it, and until then its record says ABSENT.
- WHAT THE REPLY HEADER'S LINE SAYS in a conversation with a member is
  derived; a capture of such a header settles it.
- `threads`' list reader reads pills by its own selector, `main` and the
  pill hook, not scoped to the bar. On the measured page the two agree;
  unifying it with `dom.FILTER_PILL_IN_BAR` belongs to that module's owner.
- `focused` and `other` stay in the tool's permitted set and can never be
  activated on the measured page; whether to retire them from what the
  tool accepts is the tool owner's call.

## Order of 2026-09-27 23:36: the suite reaches the network, and three guard and infra items

The orchestrator's order to lane G, 2026-09-27 23:36 IST. Disk agreed with
its sample at the start: master at 687b07c, this branch at ae24426 and an
ancestor of it, a clean tree; the branch was fast-forwarded to 687b07c.

### S.0 Commits, with their times from `git log`

```
a6151e7  09-28 00:02  no test reaches the network: the guard refuses every request off the machine, and fails the test that made it by name
514c6fc  09-28 00:02  tracker readiness: the empty-tab test compares against the ceiling it exists to catch, not a wall-clock constant
4201345  09-28 00:11  network guard test: its local file address names no drive root
041903b  09-28 00:11  reader guard: clean is earned -- a drive counts clean only when the reader read the page and returned something
1e48adb  09-28 00:13  ci shard timings: --write-timings reads every shard's junit, and the table is rebuilt from green run 36338770074
447936d  09-28 00:37  merge master 5354d42 into lane G: lane S's people search meets the network guard and the earned-clean rule
0a7e496  09-28 00:39  reader guard: a people reader's clean is earned only by its records -- lane S's reader, which built none
```

This record's commit follows them. None of these hashes is on `master` yet:
each does not resolve on `master` until the orchestrator merges this branch.

### S.1 Item 1 (HIGH): no test reaches the network, enforced

`tests/network_guard.py`, registered by `tests/conftest.py` through
`pytest_plugins`, so CI and every local run have it with no flag. At
configure time it wraps Playwright's `Browser.new_context`,
`Browser.new_page` and `BrowserType.launch_persistent_context`, async and
sync, and gives every context one route. Loopback and `data:`, `about:`,
`blob:`, `file:` and browser-internal addresses fall back to the test's own
routes and then the browser. Every other request is aborted before it leaves
-- `blockedbyclient`, an error a DNS failure never produces -- and recorded
against the running test, and `pytest_runtest_makereport` fails that test's
report, naming the test and every refused address. A page route a test
registers outranks it, so a page a test serves itself is untouched. The
conftest's opening sentence now says the rule is enforced.

RED FIRST, the guard on and nothing else changed, the two files lane L5 named:
exactly 11 failed -- 7 and 4 -- each naming itself and one address, the apply
anchor's href on the job posting captures
(`https://www.linkedin.com/jobs/view/4600000042/apply/?openSDUIApplyFlow=true&`).
Measured here, and the same eleven L5 measured.

SERVED LOCALLY. `tests/test_writes.py`'s `FixtureNavigator`, which serves the
posting, now answers its apply anchor too: `APPLY_NAVIGATION`, fulfilled with
`204 No Content`, which a browser treats as a navigation that lands nowhere --
the page stays on the capture, as on LinkedIn, where script opens the apply
flow in place -- and each answer is recorded in `.answered`. The two files,
guard on: 45 passed.

THE GUARD SHOWN WORKING, `tests/test_no_test_reaches_the_network.py`: it is
registered with no flag; a planted request to an `.invalid` address -- a name
that can never resolve, so a broken guard would still send nothing -- is
refused with the guard's own error and recorded, through `new_page` and
through `new_context`; a loopback request and a page the test serves itself
are not refused; and a test that reaches out FAILS, in its own pytest process,
naming itself and the address. 17 passed. Three mutations of the guard, each
in a scratch copy of the tree -- it never refuses; a refusal never fails the
test; `new_page` left unwrapped -- each turned its tests red, and the clean
copy passed 17.

AND A SLIP OF THIS LANE'S, FOUND BY ITS CHILD. That test file's table of local
addresses held a file URL rooted at a Windows drive, and
`tests/test_no_committed_identity.py`'s drive-root rule refuses one in any
tracked file. The guard's own gate had run its own files and not the corpus
sweeps; the child ran them. `4201345` makes the address POSIX.

WHAT IT DOES NOT COVER, named in the module: a request made outside a browser
(`urllib`, `requests`, Playwright's `APIRequestContext`), and a browser a test
starts in a subprocess -- no test does either today.

### S.2 Item 2: the reader guard counts a reader clean only when its success path ran

MEASURED FIRST over the 109 readers the committed baseline called clean, with
the guard's own variants and a page that counts its reads: 86 read the page
and returned something; 13 returned without one read; 10 read and returned
only an empty shape. Ten of the thirteen returned a refusal with a sentence in
it -- `{"refused": ..., "why": ...}` -- which is not empty and read nothing, so
a non-empty result alone is not the proof. Three read by hand to check the
counter: an argument refused on the first line (a section name, an activity
id), and a refused navigation caught and returned as a normal-looking dict.

- `tests/plantedpage.py`: `PlantedPage` counts its reads, through
  `__getattribute__` over its read entry points, so an overriding subclass is
  counted too.
- The guard: `classify_drive` takes the drive's OWN reads -- a paired
  Observation's are the harness's and are subtracted -- and a clean drive must
  show a read AND a result that is not an empty shape. Otherwise it is a
  not-driven reason, never a pass: "returned without reading the page", or
  "read the page and returned only an empty shape". A plant in the result
  already shows both.
- THIS LANE'S TWO PREVIEW NAMERS -- the reply's and the invitation's -- were
  two of the vacuous cleans. They get as-shipped drives beside L5's for
  `named_profile`: the reply namer over a group conversation and a
  one-member one, the invitation namer over a rail holding one matched
  control. Both now drive to `returns_records`.

RED FIRST: the new rule against the committed baseline named every reader that
had been clean on nothing. Regenerated with the baseline's own writer: 23
verdicts moved -- 21 from clean to an honest not-driven reason, the two namers
to `returns_records` -- and no other verdict moved. Clean 86, text 40, not
driven 39, records 3.

THE CONTROL THE ORDER NAMED: `anchors.read_anchors` is clean; stubbed to return
a refusal before reading, or to read and return an empty shape, it is not; and
with the stub in the package the coverage comparison fails, naming it. With
`classify_drive` put back to the old rule, the stub control and both rule-table
rows go red. The guard and its neighbours: 770 passed.

AND THE RULE AS FIRST BUILT DID NOT CATCH THE READER THE ORDER NAMED. Lane S's
`people_results.read_result_people` arrived with the merge of master 5354d42
(S.5), and "a read and a non-empty result" counted it clean: SHOWN, it read the
planted page once, skipped its one card for want of a member link, and returned
its denominators -- non-empty, and no record in them. The order's own words
cover it: "records, or a non-empty result". A reader whose code reaches a
people-record builder -- `record_readers()`, from the bounded-reader guard's own
closure, stopped at the write door as there -- earns clean only with a record:
"not_driven:reaches a people-record builder and built no record". Of the 7
discovered readers that reach a builder, lane S's was the only one recorded
clean. Regenerated: that one verdict moved. Its drive that reaches the records
is its owner's to build, as `named_profile`'s was.

### S.3 Item 3: the timings table is written from every shard's junit

Built by this lane's child to a closed spec and reviewed here line by line.
`--write-timings` takes one or more reports; `slowest_seconds_per_file`
prices a file found in several -- it ran in several cells -- at the LARGEST of
its per-report totals, because every cell runs the same split and the slowest
cell sets the wall clock; a report that prices nothing is refused by name.
RED FIRST on the unchanged script: 4 failed ("unrecognized arguments"), the
fifth -- the single-report output, pinned to the character -- passing, as a
regression pin should. Eight wrong combining rules planted in scratch copies,
each caught.

SHOWN ON GREEN RUN 36338770074 (head 687b07c): 18 artifacts' junits, 3 cells x
6 shards, no failure and no error in any. The table rebuilt from them prices
271 files, 3258.6 s, `_tests` 11396 -- the run's own collected count. It was
regenerated a second time here from the downloaded artifacts with the reviewed
code, and is byte-identical. It replaced a table of 186 files, 1810.6 s,
measured serially on one laptop, pricing only 4.7 files above its own
two-thirds line. Windows is the slowest cell for 231 of the 271 files. The
shard tests over it: 378 passed.

### S.4 Item 4: the empty-tab test measures the ceiling, not a wall clock

RED FIRST, deterministically: the wait over the empty tab capture in a real
headless Chromium with 320 ms of round-trip latency added to its locator, as
the load: `attached=True`, 444 ms, and the test's 300 ms assertion failed on a
tab that had resolved. Without the latency: 126 ms.

CHOSEN: compare against the delay the test exists to catch. That delay is the
ceiling -- a wait that ignores the empty half of the disjunction pays all of
it on every empty tab -- so the test waits under a 4 s ceiling and asserts the
tab resolved and paid under half: load adds hundreds of milliseconds, the
defect adds the whole ceiling. NOT isolation from `-n` load, which hides the
latency rather than tolerating it. IT STILL FAILS WHEN THE DELAY IS REAL,
driven in a new test: with 350 ms of added latency the rule holds, and the old
assertion on the same verdict would not; with the empty half removed from the
selector, under a 1 s ceiling, the wait pays the whole bound and the rule
fails. The file: 21 passed.

### S.5 Integration: master 5354d42

At the end of the four items master had moved from 687b07c to 5354d42, lane
S's merge: its people search reader, names tests and fixture, census moves and
the tool-surface pin, 10 commits. Integrated once, in one merge commit, after a
dry run.

- ONE CONFLICT, `scripts/ci_shard_timings.json`: lane S had added one file,
  `tests/test_people_search_names.py`, priced serially on a laptop, to the old
  table. Resolved to this branch's table whole, so the table stays one
  measurement from one CI run; lane S's file is priced at the mean rate until
  the next regeneration, one command over a green run's artifacts. It prices
  271 of the merged tree's 273 test files.
- `tests/reader_leak_baseline.json` merged cleanly with lane S's reader recorded
  clean -- the vacuous verdict S.2's refinement then moved.
- LANE S'S BROWSER TESTS UNDER THE GUARD: its files, with the reader guard and
  its neighbours, 1201 passed, 1 xfailed, and no test refused for reaching the
  network.

### S.6 Gates run, and what did not run

    gate                                         result
    item 1: the two files, guard on, before       11 failed, 34 passed: the eleven,
      the local answer                            each by name
    item 1: the same, after                       45 passed
    item 1: the guard's own tests                 17 passed; 3 mutations, each red
    item 2: the rule against the committed        red, naming every vacuous clean
      baseline
    item 2: the guard and its neighbours          770 passed; the rule's mutation red
    item 3: the child's red, reviewed on disk     4 failed, 132 passed
    item 3: the shard tests over the new table    378 passed
    item 4: the file                              21 passed
    before the merge: THE IMPACT GATE at 1e48adb  it WIDENED TO THE FULL SUITE (the
      (does not resolve on `master` until this    conftest is runner-wide): PASS,
      branch merges), guard on                   11434 tests, 1226.3 s; no test
                                                 refused for the network
    the merge: lane S's files and the guards     1201 passed, 1 xfailed
    THE FINAL GATE: the impact gate against      WIDENED TO THE FULL SUITE: PASS,
      master 5354d42, on this branch's head      11532 tests, 950.0 s, a clean tree;
      0a7e496, which does not resolve on         no test refused for the network
      `master` until this branch merges;
      sharded under xdist, guard on
    CPython 3.10.19 through uv, Playwright       721 passed on the same head, a clean
      pinned to the venv's 1.63.0: the three     tree (714 before the merge)
      changed test files that use no browser,
      and the guard's own test file
    this record and the register entries: the    1189 passed, on their text as
      twelve document, register and identity     staged before this row was added;
      guards; nothing else changed since the     then the cited-hash guard alone on
      final gate                                 the final text, OK

NOT RUN:

- **CI on any platform** (nothing pushed), **a cold verification pass**,
  **anything live**.
- **The 3.10 cell for the browser-driven files this order changed**
  (`tests/test_writes.py`, `tests/test_tracker_readiness.py`); CI's matrix
  runs 3.10, and the guard's own browser tests did run on 3.10 above.
- **The whole suite on 3.10.**

### S.7 Open, for other owners

- 21 READERS ARE NOW RECORDED NOT DRIVEN, each with its reason in
  `tests/reader_leak_baseline.json`: they had been clean having read nothing,
  or having read and returned only empty shapes. Each needs a drive that
  reaches its success path, the way this lane's two namers and
  `named_profile`'s got one; their owners know which values unlock them.
- THE SHARD SPLIT MOVES WHEN ANY PRICED FILE GAINS A TEST, measured by the
  child: an unpriced file is weighted by test count times a mean rate whose
  denominator includes the priced files' tests. Under the new table, pricing
  271 of 272 files, 7 added tests moved no file; under the old one they moved
  155 of 271. The rule remains.
- THE WINDOWS WALL CLOCK IS BOUNDED BY ONE FILE, not by this table:
  `tests/test_writes.py` took 185.7 s of its shard's 200.1 s, and `--dist
  loadfile` keeps a file on one worker.

## Order of 2026-09-28 01:30: every column checked, the 22 readers triaged, three more false cleans

The orchestrator's order to lane G, 2026-09-28 01:30 IST, after master was
fast-forwarded to this branch's 64afa6c and pushed. Disk agreed with its
sample: this branch and master both at 64afa6c, a clean tree.

### T.0 Commits, with their times from `git log`

- `ef6c6cb`, 2026-09-28 01:34:20 -- item 1, the blocker map's check over
  every column; a hash which does not resolve on `master` until this branch
  merges.
- `d0d2f0b`, 2026-09-28 02:29:09 -- item 2, the 22 readers triaged and the
  three false cleans found on the way; a hash which does not resolve on
  `master` until this branch merges.
- `d9dc4e9`, 2026-09-28 02:40:20 -- the one failure the impact gate found
  on it, repaired (T.4); a hash which does not resolve on `master` until
  this branch merges.

This record's commit follows them.

### T.1 Item 1: the blocker map's check compares every column

MEASURED: `scripts/build_blocker_map.py --check` asserted the map's structure
and never read the committed file; the one test that read it compared two
columns of ten. Mutating the committed map one cell at a time, that comparison
noticed 1227 of 4100 cells -- the row id, blocker and class columns -- and none
of `source`, `locator`, `state_at_freeze`, `state_today`, `capability`, `note`
or `reason_doc`, nor the header line.

RED FIRST, ON THE EXACT CASE: master 5354d42's map and `_audit` documents put
back in this tree and restored after. HEAD's `--check` exited 0 and HEAD's
test passed; the new `--check` exited 1, naming 64 rows, each "column(s)
reason_doc", and the new test failed.

The fix: `render()` is the whole file exactly as `--write` writes it, and both
modes use it; `--check` compares it with the committed file (line endings
normalised, as the other two generators do) and prints each differing row with
the columns that moved. The test holds the committed map to the derived one,
whole; its controls plant the stale value master carried, a change in each of
the ten columns, and a trailing byte -- each caught, by row and column.

THE OTHER TWO DERIVED VIEWS, the same comparison: `build_audit_index` and
`build_rulings_index` already compare the whole rendered text with the
committed file, in `--check` and in their tests. Every cell mutated one at a
time: `INDEX.md` 1873 of 1873 noticed, `RULINGS.md` 951 of 951, the new
blocker-map comparison 4100 of 4100; each `--check`, run on one right-most
cell, exited 1. Nothing to close in those two.

The generators' dependents: 432 passed.

### T.2 Item 2: the 22 readers, triaged -- (a) 6, (b) 16

Four children triaged the readers in parallel (general-purpose; each wrote
only under the lane's scratch area and committed nothing); every drive below
was re-run by the lead and rebuilt into `tests/shipped_drives.py`, whose
drives each re-read their fixture and raise if the shape they rest on is gone.

RED FIRST: the holding test,
`test_every_vacuous_reader_is_driven_or_names_what_would_drive_it`, run
against the committed guard with an empty table, failed naming all 22.

**(a) 6 -- driven over a tracked fixture, and the verdict earned:**

    reader                                  was            now      over
    dom:read_any_save_control_label         empty shape    clean    job_detail_hydrated.html
    named_profile:composer_holds            empty shape    clean    synthetic/named_profile.html
    people_results:read_result_people       no record      records  synthetic/people_search_results.html
    server:_attach_recipient_ids            empty shape    clean    profile_views_analytics.html
    server:_profile_views_press_counters    no read        clean    profile_views_analytics.html
    threads:composer_holds                  empty shape    clean    synthetic/messaging_thread.html

Lane S's people reader is one of them: over its own skeleton it returns one
record with the plant inside it, and
`test_lane_s_people_reader_is_driven_to_its_records` holds both halves --
the signature variants alone still NO RECORD, the drive RETURNS_RECORDS.
For each of the six (and
`read_premium_badge`, T.2b), a test holds that the signature variants alone
stay not driven and the drive is what earns it.

SAID ONCE, WHERE A SUCCESS PATH NEVER MEETS THE PLANT: the two composer
readers compare the box with the caller's words and return a boolean; the id
join returns ids the capture draws; the counters return integers. Those
drives prove the success path runs and carries nothing else out; the plant
reaches those readers through their signature variants, which still run.

**(b) 16 -- not driven, each with what would drive it**
(`WHAT_WOULD_DRIVE_IT`, under a declared kind):

* NAVIGATES, 5 -- recorded with their action, which is what would drive them:
  `auth:_warm_session_cookies` and `writes:_read_account_share_updates`
  (each had swallowed the harness's refusal of a page load and read
  "returned without reading"); `press:disclose`, `reveal:reveal`,
  `share_link:copy_own_post_link` (driven as far as their click over the
  profile-views capture and `own_post_menu.html`, so every read before the
  press is now hunted; beyond it, a stand-in for the click).
* CAPTURE, 4 -- `view_switch:_pill_positions`, `_option_positions`,
  `_apply_positions`, `_wait_for_option`: a committed skeleton of
  /analytics/profile-views/ with the Interesting viewers pill open. The
  tracked captures strip `aria-expanded` and draw no `main`. The capture
  the audit cites (`_audit/2026-09-23-live-lane-session-1.md` Entry 3) IS
  on this box, gitignored, in a sibling lane worktree's `_state/live1/`
  (`pv-open-pill-1.html`, with `pv-closed.html` and `pv_switch.html`
  beside it). What is missing is a committed skeleton built from it, in
  the pattern of `scripts/_build_people_search_skeleton.py` -- keeping
  `main`, the pills and the popover's closed vocabulary, and nothing of
  the viewer list. That is the cheapest next step to four more drives.
* ACTION, 3 -- `view_switch:apply_and_restore`,
  `server:_profile_views_switch`, `server:_profile_views_more_analytics`:
  clicks, and the page after them.
* NOT A PAGE READER, 2 -- `auth:_arm_session_store` (touches only
  `page.context` and writes the session store), `auth:_maybe_corroborate`
  (loads the feed, or reads nothing but an address).
* RULING, 2 -- `dom:read_profile_detail_entries`,
  `profile_views_more:read_profile_views_more_insights`. A tracked fixture
  drives each to its success path, and what comes back is page text outside
  a people record (`returns_text`). Both predate the 2026-09-24 inventory,
  which missed them because nothing drove them; the inventory may not grow,
  so their drives are held (`HELD_FOR_A_RULING`, pinned by a test that they
  still return text). DECISION FOR THE ORCHESTRATOR, with the two below:
  admit them to the inventory, or convert the readers.

### T.2b Found while triaging, each shown failing first

1. A REFUSAL AFTER A READ WAS COUNTED CLEAN. Measured over the 86 readers
   recorded clean: four were clean only by returning a whole-call refusal
   after reading -- `dom:read_compose_fields`,
   `dom:read_self_owned_editor_fields`, `dom:read_self_owned_editor_values`,
   `profile_editor:read_premium_badge`. `REFUSED_AFTER_READ` makes that
   not driven (a top-level `refused` that is truthy and is not a tally, so
   `item_addresses`' per-href tally is untouched). RED: three of the new
   control rows fail on the prior guard's `classify_drive` (the four
   tally-and-falsy rows pass on both); the coverage comparison against the
   prior baseline fails naming the three readers it takes from clean. The
   four were triaged the same way -- (a) 1: `read_premium_badge`, over
   `synthetic/intro_editor_switches.html`; (b) 3: `read_compose_fields`
   (CAPTURE: the composer's two send-mode radios, which no tracked page
   draws), and the two self-owned editor readers (RULING: driven over the
   same intro editor, they publish a label ungated and a value verbatim --
   page text outside a record -- held with the two above).
2. A FAILURE ENVELOPE WAS COUNTED CLEAN. Three readers --
   `named_profile:read_opened_conversation`,
   `profile_editor:read_account_share_updates`,
   `profile_editor:recognise_intro_editor_switches` -- were clean on
   `{"error": "AttributeError", ...}`: the planted locator lacked
   Playwright's `and_`, `or_` and `filter`, and each reader's own handler
   caught the miss. The planted and failing locators now answer all three
   (a failing locator narrows to a failing one); all three reach their
   readings, error-free, and stay clean -- now earned. `ERRORED_AFTER_READ`
   makes the next such gap a not-driven verdict. RED: with the three
   methods removed, the new per-reader test fails on all three and the rule
   records each "returned an error"; one control row fails on the prior
   guard, two pass on both.
3. THE HARNESS'S REFUSAL OF AN ACTION COULD BE SWALLOWED. `NavigationAttempted`
   was a `RuntimeError`, so a reader's `except Exception` caught it.
   Measured: no reader was clean that way; five not-driven reasons were
   wrong (the two above among them). It is a `BaseException` now. RED: a
   control reader that reads, clicks inside `except Exception` and returns
   what it had was clean on HEAD. Effects measured before the change: the
   failing-page family's returned count 113 -> 111 (floor 78), five of its
   verdicts to navigates; the tool-envelope guard, 59 tools, none moved.
4. AMONG NOT-DRIVEN VARIANTS, THE ONE THAT GOT FURTHEST NAMES THE READER --
   read, then action, then the rest. On the tree before the drives the read
   rank alone moved nothing; with them the action rank moved four, each to
   the truer reason (the three press readers, and
   `writes:_load_named_profile`, whose page load one variant reaches past
   another's raise). RED: four of its six rows fail on the prior `_worst`.
5. THE STANDALONE BASELINE WRITER now sandboxes the session store, as the
   tool-envelope guard's standalone path does; `_arm_session_store` was
   unreachable only because the planted page's `context` is `None`.
6. NAMED, NOT CHANGED: `empty_shape` reads `[0]` -- a match at position 0 --
   as empty, so a view_switch helper finding its target first would read
   not driven (the safe direction). The CAPTURE entry says to keep the
   controls before the pill.

THE BASELINE, regenerated by its own writer: 18 verdicts move -- the 6
driven, the 3 refusal-only readers not driven, the 5 navigating by the
re-base, the 3 press readers and `writes:_load_named_profile` by the rank.
clean 86 -> 88, records 3 -> 4, text 40 (unchanged), not driven 40 -> 37.

THE DECISION THIS NEEDS FROM THE ORCHESTRATOR, one: four readers --
`dom:read_profile_detail_entries`,
`profile_views_more:read_profile_views_more_insights`,
`dom:read_self_owned_editor_fields`, `dom:read_self_owned_editor_values`
-- return page text outside a record on their success paths, each by design
with a stated reason (his own skills; the viewer aggregates; the
self-owned-container ruling). Admit them to the text inventory, which they
predate, or convert them. Their drives are ready either way.

### T.3 Integration

`master` was 64afa6c at 01:34, at 02:26 and at 02:42, when this record was
written: it had not moved since the order, so there was nothing to merge. It
is read once more before the final gate, and the report says what it was.

WHAT THIS BRANCH WILL MEET: lane S is building people-search readers and
lane L5 is converting name-aimed sends. If either lands first and changes
`people_results`, the planted page or a reader named in
`WHAT_WOULD_DRIVE_IT`, the holding test and the drive tests fail by name at
the merge -- which is what they are for.

### T.4 Gates run, and what did not run

Every run below is local, on Windows, with the network guard on (it is
registered by `tests/conftest.py`, so every pytest run carries it).

* ITEM 1: the generators' dependents, nine files -- 432 passed; the same
  three generator test files on CPython 3.10 -- 73 passed.
* ITEM 2, while it was built: the reader guard, whole file, sharded -- 587
  passed; the planted page's twelve dependents after the re-base -- 432
  passed, 1 xfailed (the people-search reader's declared limit); after the
  locator algebra, the seven that read the baseline or the planted locator
  hardest -- 167 passed.
* THE THREE CAN-FAIL SCRIPTS the planted page stands under, on this tree:
  the coercion family's -- 15 readers red under the coercion that shipped
  and green on its removal, the other 73 clean not convicted; the refusing
  grant's -- all 5 sections red on a defect and green without it; the tool
  envelopes' -- fired (3 leaking) and green again (0), over 59 tools.
* THE IMPACT GATE, `scripts/impact_gate.py --against master`, sharded, on
  the code-complete tree (`d0d2f0b`, a hash which does not resolve on
  `master` until this branch merges), 02:30:09 to 02:38:45: 7 changed
  paths, 69 files selected and 26 corpus-wide, 74 in all -- 4616 passed,
  1 skipped, 1 xfailed, 1 FAILED, in 489.7 s; by its own count 199 of 273
  test files not checked (the corpus-wide sweeps did run).
  THE FAILURE WAS RIGHT TO LOOK:
  `test_no_tracked_file_pairs_fixture_content_with_anything_else` flagged
  the new module's `_EDITOR_CONTROLS`, tuples of strings some of which a
  committed fixture draws (input, text, checkbox, button) and some of which
  it does not (label-for, native, state_not_value) -- the shape of a
  de-anonymisation key. Every string there is structural vocabulary and the
  only page text is the plant, so nothing is a pre-image; but the rule's own
  first remedy is a rename, not an exemption, so the controls became
  mappings with named fields (`d9dc4e9`, a hash which does not resolve on
  `master` until this branch merges). That test passes, the two held drives
  return what they returned, and the gate over the final tree re-runs the
  whole impact set.
* CPython 3.10 through uv, sharded, on `d9dc4e9` (a hash which does not
  resolve on `master` until this branch merges) with a clean tree: the
  reader guard, the orphan ruling, the tool envelopes, the unread readings
  and the people-record channel -- five files, 666 passed in 148.1 s. It is
  the check that a `BaseException` raised inside `asyncio.wait_for` still
  reaches the harness on the oldest Python the package supports.

NOT RUN: the full suite (the gate scoped, and says what it left out); CI's
three platforms (nothing was pushed, by order); anything live (offline, by
order); the whole-tree identity sweeps the gate deselects in favour of the
staged form (their base case runs on every push in CI); the browser tests on
3.10. The impact gate over the FINAL tree, this record's commit included,
runs after it; its counts are in the lane's report.

### T.5 The gate over the final tree, the premise control, two corrections

THE FULL SUITE: `scripts/impact_gate.py --against master` on `830e169` (a
hash which does not resolve on `master` until this branch merges), with
`master` read at 02:46:40 and still 64afa6c, so nothing was merged. 9
changed paths selected 149 files and 26 corpus-wide, 153 of 273 (56 per
cent), at or above the gate's 45 per cent line, so it WIDENED TO THE FULL
SUITE: 02:46:54 to 03:17:14 -- 11570 passed, 9 skipped, 2 xfailed, 1
FAILED, in 1777.0 s. Two commits follow that tree; both are below.

THE ONE FAILURE, AND WHY IT IS NOT THIS BRANCH'S -- the facts measured,
the mechanism DERIVED:
`tests/test_typeahead_gate.py::test_an_empty_listbox_refuses_separately_from_an_absent_one`.
The branch touches neither `linkedin_server/`, nor that test, nor
`tests/conftest.py`: the diff against `master` over those paths is empty.
The whole file ran three times in isolation straight after, on the same
tree -- 11 passed each time. The test waits for the listbox with its own
400 ms (`TYPEAHEAD_TIMEOUT_MS`, patched short on purpose), and the gate
ran on a saturated box: at 03:05, CPU load 100 per cent, 64 Python and 51
Chromium processes, other lanes' suites running beside it -- which is also
why this full suite took 1777 s where the last one took 950 s. A listbox
drawn after 400 ms reads as absent (`1_no_listbox`), the other half of the
pair this test asserts. Recorded as a flake under load, for the
orchestrator to watch in CI.

THE HOLDING TEST, EVERY BRANCH SHOWN FAILING (T.2 showed one), each run
in-process against the guard as committed: an empty table fails it naming
the 14 readers the table holds (untriaged -- the branch that named the 22
before any drive existed); the prior baseline fails it naming three
(unrecorded); a driven reader added to the table fails it naming that
reader (stale); an entry stripped of its kind fails it naming that entry
(kindless).

TWO DRIVES DID NOT KEEP THEIR OWN RULE, and the control that found them is
new. Every drive is to RAISE when its fixture stops drawing the shape it
rests on. Run for all 14, each as the guard runs it with ONE needle of its
shape broken in a scratch copy of `tests/fixtures`: 12 raised and were
recorded not driven; the `press:disclose` and `reveal:reveal` drives did
not, with the capture's headline broken -- disclose went on to its click,
reveal came back refused. Both read the headline inside the double's
`evaluate`, that is inside the counter reader's own `except Exception`,
which swallowed the check. A premise checked inside a double runs inside
the reader's handlers; it has to be checked in the drive, before the
reader runs. Moved there (`29b67ff`, a hash which does not resolve on
`master` until this branch merges); re-run, 14 of 14 raise, and every
drive's verdict on the real fixtures is unchanged. The control is a test
now, so the rule holds for the next drive too:
`test_a_drive_on_a_fixture_that_stopped_drawing_its_shape_raises`, one case
per drive, each needle named in `FIXTURE_BREAKS` and checked present before
it is broken; `test_every_drive_has_its_premise_broken_below` fails a drive
added without one. RED FIRST: on the module as committed in `830e169` (a
hash which does not resolve on `master` until this branch merges), those
two cases fail and the other twelve pass.

TWO CORRECTIONS TO T.4, both mine:

* "the planted page's twelve dependents": eleven of those twelve files
  import `tests/plantedpage.py`; the twelfth is
  `tests/test_profile_views_more.py`, run because a held drive rests on its
  synthetic page. The count, 432 passed and 1 xfailed, stands.
* "NOT RUN: the full suite" held for the gate on `d0d2f0b` (a hash which
  does not resolve on `master` until this branch merges) and no longer
  holds: the gate over `830e169` ran it, above.

THE TWO COMMITS AFTER THE FULL SUITE -- the premise fix and this section --
are gated by `scripts/impact_gate.py --against 830e169`: the impact set of
exactly what changed since the tree the full suite passed. Its count is in
the lane's report.

### T.6 Integration of master 6bc63e2, at the end

THE FULL SUITE ABOVE PASSED ON THE HEAD BEFORE THE MERGE: `8a8fd43` (a
hash which does not resolve on `master` until this branch merges), gated
by `scripts/impact_gate.py --against 830e169` (a hash which does not
resolve on `master` until this branch merges) -- 4 changed paths, 145 of
273 files, which widened it: PASS over the FULL SUITE, 11597 tests, in
1852.1 s, 03:27:02 to 03:57:54. The typeahead test that failed under load
in T.5 passed in it.

`master` HAD MOVED meanwhile: read at 03:58:14, it was 6bc63e2, lane L5's
seven commits since 64afa6c (retiring `linkedin_send_message`, aiming the
invitation by the profile link; 71 files). Merged once, as the order says,
in `aa191c4` (a hash which does not resolve on `master` until this branch
merges). ONE CONFLICT, `tests/reader_leak_baseline.json`, resolved by its
own writer on the merged tree rather than by hand: 160 readers -- master's
set exactly, L5 having removed ten readers and renamed one -- carrying this
branch's 18 verdict moves exactly and no other difference, each checked
against both parents. The guard file and the register merged cleanly; the
derived views are at a fixed point. The reader guard on the merged tree:
575 passed.

THE GATE OVER THE MERGED TREE, this section's commit included, is
`scripts/impact_gate.py --against master`; it runs after this commit, and
its counts are in the lane's report.

## Order of 2026-09-28 04:25: the rulings on what lane G held, two gaps lane L5 found, and the network guard's reach

The orchestrator's order to lane G, 2026-09-28 04:25 IST. Its sample: master
being fast-forwarded to this branch's 0867bda and pushed, CI running. Disk at
04:21:55: this branch and local master both 0867bda, a clean tree; the remote
still at 6bc63e2 and no CI run for 0867bda yet. At 04:41:03 the remote was
0867bda and its CI run had completed with success -- disk agreed, and the
work went on. An addendum at 06:20 added item 6, the network guard's reach
(U.7).

### U.0 Commits, with their times from `git log`

Every hash in this section is a commit on this branch, which does not
resolve on `master` until this branch merges; the times are the commits' own.

    1e51c3e  04:40:52  reader guard: the ruling on the four held readers --
                       three of his own admitted, one aggregate admitted,
                       one field that could name a member converted
    c9277bd  05:19:12  profile-views skeletons: a committed builder, four
                       states of the page, every other member's text reduced
                       to shape
    4daa38d  05:29:31  log capture: 21 sites that could not hear a DEBUG
                       record now do, and the one handler that raised
                       NameError logs
    4e0114d  05:37:07  reader guard: the profile-views readers driven over
                       their skeletons, and the click stand-in taken to
                       every press a capture shows
    ee9ad11  05:45:50  page double's test: its member link takes the slug
                       shape the builder writes, which the identity sweep
                       reads as a shape
    de8e95e  06:02:17  log capture: a guard on the shape the 18 root-only
                       DEBUG captures had, and conftest's docstring told the
                       level half
    739c117  06:10:25  impact gate: in the package a sentence that names a
                       document cites it, and no longer couples it; every
                       real read keeps its plan
    955adbc  06:13:16  merge master ff42daa into lane G: lane S's offline
                       frontier meets the rulings of 04:25
    6a419b6  07:01:18  network guards: the docstring says what the network
                       guard covers, a socket census finds nothing outside a
                       browser but loopback, and the CDP guard stops putting
                       the package log on the console

and this record, on the commit that carries it.

### U.1 Ruling (1): the four readers held for a ruling

THE RULING: PEOPLE-DATA-MITIGATIONS binds OTHER members' data. His own text
is admitted to the text inventory; anything identifying another member
leaves only as a people record (the reader is converted); an aggregate that
identifies no one is admitted. Each reader's success-path output was read
FIELD BY FIELD on its drive, not decided from its name:

    reader                                  fields on its drive, and whose                  applied
    dom:read_profile_detail_entries         entries, evidence: his skills and the lines     ADMITTED, his own
                                            under them; endorsements: see below;            + one field
                                            observed, why: counts, this package's words     CONVERTED
    dom:read_self_owned_editor_fields       container; each control's label, type,          ADMITTED, his own
                                            role, states -- his own editor's
    dom:read_self_owned_editor_values       container; each field's label and the value     ADMITTED, his own
                                            he typed
    profile_views_more:                     sections_found (closed words); highlights:      ADMITTED, an
      read_profile_views_more_insights      top location, industry, company over all his    aggregate
                                            viewers; details: company names and shares;
                                            unparsed_lines (a count). No field is a viewer.

THE ONE FIELD CONVERTED. `read_profile_detail_entries` published every card
line containing "endors" verbatim, in `endorsements.lines` and among the
card's `evidence`. LinkedIn draws none today (measured 2026-09-04), but a line
it could draw -- "Endorsed by <a member> and 2 others" -- names ANOTHER
member, and a sentence is not a record. Now a bare count ("3 endorsements")
is still published, and any other endorsement line is counted
(`endorsements.lines_withheld`) and published nowhere. RED FIRST:
`test_an_endorsement_line_that_names_a_member_leaves_as_a_count_only` put a
declared synthetic endorser on a card; on the unconverted reader the name came
back in `evidence` and in `endorsements.lines`; after, it is nowhere, the
count line is kept, and the existing control that a count is reported still
passes.

THE DOOR. `tests/plantedpage.py`'s `text_ratchet` and
`text_paths_a_baseline_may_not_record` take the admissions: a reader named in
the guard's `ADMITTED_TEXT`, with its ruled reason, may join the inventory;
every other new text path is refused as before. RED FIRST: HEAD's ratchet took
no admission at all (TypeError) and called the admitted case a new text path;
the new test shows the same case refused without the table and let through
with it, while another member's path in the same table is still refused. The
four drives moved from `HELD_FOR_A_RULING` (removed) into `DRIVES`;
`test_a_reader_joins_the_text_inventory_only_by_the_ruling` holds each one
driven, recorded as text, for a ruled reason, and refused without its
admission. The baseline moved by exactly those four, each to `returns_text`.

THE FIFTH READER RULED THE SAME WAY, later the same day: once ruling (2)
drove it, `server:_profile_views_more_analytics` came back with page text
too, and its fields were read the same way -- `reveal` (the gate's counts
and verdicts), `insights_after` (`dom.read_profile_views_insights` on his
own analytics page: the headline and its label, the chart's description,
the filter labels; it reads no viewer row) and `revealed_insights` (the
aggregates above). ADMITTED, for both reasons.

### U.2 Ruling (2): the click stand-in

THE RULING: the leak harness's page double may stand in for a click by
moving the fixture to the state the real page draws after it -- a test
double only; no real press exists anywhere -- each transition recorded with
its source, and a transition no capture shows stays not driven.

THE DOUBLE. `tests/skeleton_page.py` (built by a child of this lane,
reviewed and applied by the lead): a pure-Python page that answers locators
from a parsed skeleton -- locators LAZY, as Playwright's are, so a locator
built before a press reads the page after it; Playwright's strictness; a
grammar of exactly the 18 selectors its readers use, harvested from their
source by a test, anything else refused AND recorded in `page.unmodelled`
(every drive requires it empty); each page read counted on the planted page
beneath it; every script it has no stand-in for answered by the planted
page. `tests/test_skeleton_page.py`: 252 cases, each seen failing under at
least one of 67 deliberate mutations of the double.

THE TRANSITIONS (`shipped_drives.TRANSITIONS`, each source a live-lane
capture, `_audit/2026-09-23-live-lane-session-1.md`):

    press                          before (skeleton of)            after (skeleton of)
    the Interesting viewers pill   pv-closed.html, Entry 3's load   pv-open-pill-1.html, the same load
    its 'verified' option          pv-open-pill-1.html              NONE -- no capture draws it checked
    Show more analytics            pv_verify.html, Entry 7's fresh  pv_switch.html, the switch run's end
                                   load (the run's rows, headline)

APPLIED TO THE THREE READERS THE RULING NAMED, and one more it reaches:

* `view_switch:apply_and_restore` and `server:_profile_views_switch` (one
  drive, the server's call): the counters read (headline 39), the pill found,
  the view read, the pill's press stood in for; the option found and read
  unchecked; its press REFUSED -- no capture shows the after-state -- so both
  stay not driven, recorded `navigates (locator.click)`, the transition named.
  A test holds that it is the option's press the drive stops at, not the
  pill's.
* `server:_profile_views_more_analytics`: the reveal pressed (stood in for),
  then the insights and the revealed sections read -- `returns_text`,
  admitted (U.1).
* `reveal:reveal`, the same press: PERMITTED -- the counters equal at both
  ends, `main` grown from the fresh load's elements to the revealed page's --
  `clean`. Its reading (`COUNT_LINES_JS`) has no stand-in, so the planted
  page answers it and the reading is unreadable at both moments, which the
  gate records and does not gate on.

SHOWN DOING THE WORK: with the double's stand-in removed, the reveal's drive
ends at its click; with it, the one press is the decided one and the reveal
is permitted. NOT DONE, and said: `press:disclose` closes its popover with
the Escape key, and the page after that key is shown by no capture of that
moment; it stays driven to its click.

### U.3 Ruling (3): the profile-views skeleton, and the four view_switch readers

THE BUILDER, `scripts/_build_profile_views_skeleton.py` (built by a child of
this lane from the live lane's gitignored captures, read in place and never
printed; reviewed by the lead), the way
`scripts/_build_people_search_skeleton.py` builds its own:

* KEPT: the body's tags and nesting; `class`, `role`, `type`, `tabindex`,
  `disabled`, `hidden`, `data-view-name` and every `aria-*`, each checked
  against its own vocabulary; LinkedIn's interface words from a declared
  allowlist (51 phrases and 7 templates whose only variable is a number,
  each phrase from a source that cannot hold a person: the readers' own
  phrases, the audit's recorded vocabulary, the tracked sanitised fixture);
  plain numbers.
* REDUCED TO SHAPE: every other text and label (every letter X or x, digits
  and punctuation kept); a member link keeps only its slug's shape; any other
  link keeps its route words.
* It prints counts and a structure digest, is a fixed point over its own
  output, and refuses a page with no `main`. No raw capture is committed.

THE FOUR SKELETONS, each the state it is named for (measured by counts on
the captures first): `profile_views_closed` (984 body elements kept 663),
`_pill_open` (the Interesting viewers popover: two options, both unchecked,
and its Reset and Show results), `_verify` and `_revealed` (Highlights and
Details drawn), 69,526 to 78,505 bytes each.
`tests/test_profile_views_skeletons.py` pins the fixed points and the four
digests the captures printed, each state, and that every text, label and
link is an interface word, a number, a shape or a route -- each shown
failing on a plant.

TWO PRIVACY GUARDS HAD TO LEARN WHAT A SHAPE IS, narrowly. HEAD's exact-
identity sweep found 6 "linkedin slug" hits per skeleton and the
synthetic-people guard 6 undeclared people per skeleton: the shaped member
links and names. A slug made ONLY of x, 0, - _ % and a value whose EVERY
letter is X or x identify no one (the alphabet is the argument), and each
guard now says so -- with a control that keeps it narrow: one real letter
left unshaped and each fires again. Patched: 0 and 0.

THE FOUR READERS, driven over the skeletons (`tests/shipped_drives.py`),
each from EMPTY SHAPE to CLEAN:

    view_switch:_pill_positions      closed page     [2]  (a dialog button, then the three pills)
    view_switch:_option_positions    pill open       [1]  ("Verified", after "Works at a company you follow")
    view_switch:_wait_for_option     pill open       [1]
    view_switch:_apply_positions     pill open       [24] (Show results, of 25 buttons)

Each drive checks its skeleton's builder header and the state it rests on
before the reader runs, and raises if they are gone (a case each in the
premise test); another member's shaped text is answered as the plant.
`read_profile_views_more_insights` moved from the test's inline markup to
the revealed skeleton, the capture's own structure.

### U.4 Lane L5's first: log-capture sites that could not fail

THE FINDING: 12 log-capture sites whose "no record contains X" passes
whatever the code logs. MEASURED FIRST, AND THE MECHANISM WAS NOT THE ONE
NAMED. The order said the sites do not hear the `linkedin` logger. They do:
pytest 9.1.1 attaches caplog's handler to the non-propagating `linkedin`
logger itself, and conftest's fixture does too. What they lacked was the
LEVEL: `linkedin` runs at its own INFO, and each site lowered only the root
(`caplog.at_level(DEBUG)` or `set_level(DEBUG)` with no `logger=`), so a
DEBUG record on `linkedin` was dropped before any handler saw it. Each of the
12 passed with a DEBUG record carrying its forbidden value planted inside the
call it guards, and went red on the same record at INFO.

THE FIX, per site: lower the root AND `linkedin` to DEBUG, and first prove a
DEBUG control record comes back, so a site that cannot hear says so instead
of passing. Every site shown: red on a planted DEBUG record after, green on
the real code, red again with the fix reverted at run time.

    the 12 named        test_a_preview_names_the_resolved_target 2, test_auth 3,
                        test_auth_reason_withholds_the_request 4, test_leakwalk 3
    THE SAME SHAPE, 9   test_auth_lifecycle 3, test_people_search_names 3, and three
    more, by census     WARNING-level captures that could not hear a DEBUG record
                        (test_cdp_attach, test_landing, the reader guard's as_count)
    ruled out           test_needle_never_escapes 2 (already red on a planted DEBUG
                        record) and the two log-capture controls (each plants a
                        record and asserts it IS heard, so each can fail)

The census: every function in `tests/` that takes a capture fixture, reads
or hands one on, or sets a level on it -- parsed, its level calls and their
`logger=` read, 107 functions over 25 files; each candidate then run with a
planted record at DEBUG and at INFO.

THREE MORE THE SAME HUNT FOUND:

* `scripts/credential_echo_control.py`, the echo control behind six auth
  leak tests: its `in_log` plant wrote to `linkedin_server.auth`, a logger no
  module of the package writes to, so the controls it drives certified a
  channel the package never uses. It writes to `linkedin` now, pinned by a
  test (red against HEAD's control, green against the patched one); the leak
  matrix is 0 green cells of 54 either way.
* The reader guard's failing-page family collected records on `linkedin`
  only; `threads` logs through `getLogger(__name__)`, at the root's WARNING.
  The family now listens on both package loggers: red on a planted record,
  green after.
* `linkedin_server/writes.py`: the invitation namer's handler for a label
  that did not read called `logger`, which writes.py never defined, so its
  "never raised" branch raised NameError. It imports the package logger now.
  RED FIRST: a label that raises on read took the call down with NameError;
  after, the namer returns and logs the failure by type. A census of the
  package for any other name read and bound nowhere found none.

The sites and their proofs were built by a child of this lane in a shadow
tree, and reviewed and applied by the lead.

AND KEPT FOUND. The census was a one-off; the shape is now a guard,
`tests/test_a_debug_capture_lowers_the_package_logger.py`: every function
under `tests/`, parsed; a caplog level call at DEBUG (or at a level the parser
cannot read) that names no logger must sit, in the same function, beside one
that names a logger at DEBUG. RED FIRST: over the test modules at master
0867bda it finds 18 hits in 23 level calls -- exactly the 12 named sites and
the 6 root-only ones the census added; over this branch, 0 in 17. Nine planted
sources hold it to its verdict both ways. It does not read the WARNING-level
shape (whether such a capture is vacuous depends on the level the code logs
at, which no parse of the test sees). And `tests/conftest.py`'s docstring
said caplog's handler sits on the root only; a probe on pytest 9.1.1 with no
conftest heard an INFO record on a non-propagating logger (DEBUG with the
root lowered: not heard; with the logger named: heard). The docstring now
says the handler is half and the level is the other, and names the guard.

### U.5 Lane L5's second: the impact analyser read prose as a data read

THE FINDING: a prose-only edit to lane L5's record selected 118 test files
and a 22-28 minute gate, because a comment mentioning a document counted as
a dependency. MEASURED FIRST, AND THE PREMISE WAS HALF RIGHT. `code_text`
already strips comments and docstrings, and four of the five places in the
package that mention the record are there (docstrings of `named_profile.py`
and `threads.py`, comments in `server.py` and `writes.py`): they coupled
nothing. The fifth is a SENTENCE THAT IS A VALUE, which the strip keeps on
purpose (a value can be a path): the `reversibility_procedure` of
`SANCTIONED_WRITES["linkedin_send_reply"]` in `linkedin_server/writes.py`,
"... (capture spec C6 in <the record>) ...". That one string coupled the
record to `writes.py`, and through its importers to 95 test files: at
c9277bd (a hash which does not resolve on `master` until this branch
merges), 118 selected, a plan of 132 of 271 test files, over the 45% line,
so the gate widened to the full suite.

THE RULE (`scripts/impact_gate.py`, `without_sentences`, applied by
`Corpus.data` to `linkedin_server/` only): in the package, a string literal
whose VALUE holds whitespace is a sentence, and a path inside a sentence is a
citation, not a read. It goes before the data-read match; an f-string's
literal parts go and its expressions stay, read again by the same rule, so
`f"reading {ROOT / 'x.md'} now"` still shows `'x.md'`; a literal with no
whitespace is a path and stays. Read by the parser on each literal's own
text, so 3.10's one-token f-string and 3.12's token run give one verdict.
WHY WHITESPACE: no tracked path holds any (0 of 913, held by a test). WHY THE
PACKAGE ONLY, measured: no package module names any of the 337 tracked data
files outside a sentence, and 14 are named inside sentences, every one a
citation -- while `tests/` and `scripts/` plant data paths inside spaced
literals that their checkers resolve at run time (a `path row N` in
`tests/test_jobs_directions.py`, a `path::phrase` in
`scripts/check_write_classes.py`), so there the same rule would cut real
reads. A package module the parser cannot separate is read WHOLE, and its
edge and the report say so: a fallback may widen a plan and never narrow it.

SHOWN, with the plans:

    data file                                    selected  plan (of 271)
    lane L5's record (the order's case)          118 -> 23  132 -> 41, full suite -> scoped
    the blocker ledger, read through composed
      Path segments (the names-alone trap)       28 -> 28   identical set
    its assignments TSV, the same script         28 -> 28   identical set
    a fixture named by an f-string               43 -> 43   identical set
    a data file a script loads by path           29 -> 29   identical set

The record's 23 are there for a reason other than prose: 22 reach it through
readers that sweep `_audit/`, and one through a real reference in code, a
dictionary key.

Over 51 data files probed (the ones the tests pin, and every file a literal
with whitespace names anywhere in the tree), 14 plans shrank and none grew;
the corpus-wide floor never moved. A data file read in code keeps its plan
file for file -- the names-alone trap, caught from the other side.

THE LEAD'S OWN CHECK, on the 14 that shrank: every node the rule drops, and
every edge leaving one. 0 of them is a text edge onto a citing module (names
the path, sweeps the directory, composes, pins): each is "imports it", or
"loads it by path" (33, a module executed, which is behaviour too). So no
test the rule drops reads a citing module's text and resolves the citation
against the file: an edit to a cited file cannot reach any of them.
`pyproject.toml` is among the 14 and runs the full suite regardless (a
runner-wide trigger).

THE TESTS (`tests/test_impact_gate_selects_data_dependencies.py`, 18 new):
(a) a package sentence naming a data file does not couple it, plain and as
an f-string; (b) a package path still does, plain, as an f-string and inside
a sentence's expression; the control, every plant coupling with the rule
off; (c) lane L5's record under a bound DERIVED from the gate's own widening
line, with its rule-off control; (d) the four real reads identical with the
rule on and off; (e) an unseparable module read whole and reported; and the
PREMISE held, not believed: the test fails the day a package module names a
tracked data file outside a sentence, or a tracked path holds whitespace,
with a control that catches a planted read by name and passes a planted
citation. RED FIRST, on the unpatched analyser: 15 of the 18 fail; the
three that pass are (b), which guard the fix itself and go red under the
mutants that strip too much. Five mutants of the patch, each turned red by
the new tests: every package literal read as a sentence; that, in every
source; the on/off switch ignored; the token filter dropping every string;
nothing ever a sentence. The fourth is the certifying case for 3.10: there
an f-string is one token, and 3.10 caught losses 3.13 could not see.

NOT COVERED, and said: `tests/` and `scripts/` still read their sentences as
reads (a real over-selection there, and the only safe reading); the dynamic
loader rule still reads package sentences whole, so `writes.py` "loads" the
probe scripts its sentences name -- a false edge, wider and never narrower;
and a path assembled only from pieces that each hold whitespace would be
missed, which the whitespace premise makes impossible for a tracked path.
THE COST, measured: the test file went from 97.5 s to 129.5 s run alone, and
it runs on every gate; about 10.7 s of that is one cold reading of the tree
that each of its older tests already pays separately, so sharing one reading
across the file would make it faster than before. Not done; named.

Built by a child of this lane; reviewed by the lead, who replaced two
line-number citations in its docstrings with the symbol, since the line had
already moved on this branch.

### U.6 Integration

Master at 06:10:54 was ff42daa, local and remote agreeing: lane S's offline
frontier, nine commits over 0867bda. Merged once, as 955adbc (06:13:16).

Six files changed on both sides. Four merged cleanly --
`linkedin_server/dom.py` (lane S's engagement cards live in
`SEARCH_APPEARANCES_JS`, far from the endorsement conversion),
`tests/conftest.py` (lane S's CDP-port guard beside this branch's docstring
paragraph), `tests/shipped_drives.py` and
`tests/test_fixtures_hold_only_synthetic_people.py` (each side's additions
in different places). Two conflicted, both by adjacency:

* `tests/test_readers_emit_no_page_string.py`, `DRIVEN_TO`: this branch's
  admitted readers (`returns_text`) and lane S's two people readers
  (`returns_records`, `presence:read_suggested_presence` and
  `recruiter_views:read_recruiter_views`) -- both kept.
* `tests/reader_leak_baseline.json`: resolved by hand, then regenerated
  with `--write-baseline` on the merged tree -- byte-identical to the hand
  resolution. 162 readers: clean 88, returns_text 41, not_driven 27,
  returns_records 6.

Lane S's two drives brought their own premise entries, so the premise
table still covers every drive, as this branch's stricter form of that test
(no exempt drive) requires. This branch touched no `_audit` file before the
merge, so master's derived views held; the commit that adds this record
regenerates them to a fixed point.

### U.7 The addendum of 06:20: what the network guard covers, and every connection the suite makes outside a browser

THE ADDENDUM, verified before it was obeyed: master ff42daa with CI green,
run 36362999033 -- checked, conclusion success, head ff42daa, the master
this branch had merged at 06:13.

THE DOCSTRING. `tests/network_guard.py` said a request made outside a browser
was not covered, and that "no test does either today". That was false:
lane S measured the envelope test's CDP probe. It now says exactly what it
covers -- a request Playwright routes, a page's, in a context THIS process
created through one of the three wrapped calls, loopback admitted at every
port -- and names what it does not: a connection outside a browser (the
probe, and this census), the contexts a browser already holds when a test
reaches it with `connect` or `connect_over_cdp`, a browser in a subprocess,
and a browser's own background traffic.

THIS LANE REACHED FOR THE PORT ONCE IN THIS ORDER, found by reading this
lane's own command history for the envelope test: the gate on ruling (1),
04:46:28, ran `tests/test_tool_envelopes_emit_no_page_string.py` as a
dependent of `dom.py`, before lane S's stub reached this branch, so its
probe opened `http://127.0.0.1:9224/json/version` once. Whether anything
listened at that moment was not measured. No child of this lane ran that
file. Every full suite this lane ran under earlier orders made the same
attempt once, as lane S found for every lane. From the merge on, the probe is
stubbed and `tests/cdp_port_guard.py` refuses the port.

THE CENSUS, a scratch instrument (disposable), in two halves:

* A `sitecustomize` on PYTHONPATH for the whole run, so pytest, every xdist
  worker and every Python subprocess a test starts loads it. An AUDIT HOOK
  sees every `socket.connect` and `connect_ex` at the C level, whatever
  library called them, every name resolved and every datagram sent; and
  asyncio's proactor connect on Windows -- an overlapped `ConnectEx`, which
  raises no audit event -- is wrapped when asyncio loads it. It RECORDS each
  attempt against the running test and REFUSES every address off the
  machine, every loopback port in 9222-9229 and every name that is not
  loopback: the measurement could observe an escape, never make one.
* A TCP SAMPLER for what no Python hook sees -- Playwright's Node driver,
  Chromium: every pass, each TCP connection held by any process in the run's
  tree whose remote end is off the machine or on a loopback CDP port.

CONTROLS, each shown seeing. Ten planted attempts -- an off-machine connect,
`connect_ex`, a public name, `urllib`, 9224, 9222, a loopback listener, UDP,
an asyncio connect, a Python subprocess -- each recorded, and each off-machine
or CDP-range one refused. THE CONTROL CAUGHT THE CENSUS'S OWN BLIND SPOT: on
its first run the asyncio connect went unrecorded (the proactor's
`ConnectEx`, and asyncio skips name resolution for a numeric address), and
went out toward 203.0.113.9, a documentation address that routes nowhere;
the proactor wrap closed it, and the second run recorded and refused all
ten. The sampler, rooted at a process holding a connection to its own LAN
address (which never leaves the machine but is not loopback) and one to
loopback 9227, reported both.

THE COUNT, the full suite at 955adbc (which does not resolve on `master`
until this branch merges) under the census, 1,246 s: 11,954 passed,
9 skipped, 1 xfailed, 18 FAILED -- and the 18 are the census's own fault,
found and re-run. A scratch script of this lane's, named `numbers.py`,
written into the census's directory eight minutes into the run, shadowed the
standard library's `numbers` module in every Python process started after
it; the 18 tests whose gate subprocess started later (the staged identity
and staged navigation gates) died at import. Renamed, those two files ran
again under the census: 29 passed, and not one socket event.

6,022 connection attempts, all from the 8 xdist workers -- no Python
subprocess a test started made one -- by 2,479 tests in 128 files. EVERY ONE
a `socket.connect` to 127.0.0.1 on a port in the dynamic range (49159 and
up): the self-pipe of an asyncio loop on Windows, which is a loopback socket
pair -- one `asyncio.run` makes exactly one, shown on the census alone --
and the tests' own local listeners.

    off the machine                        0
    a loopback CDP port (9222-9229)        0
    a name that is not loopback, resolved  0
    a datagram                             0

The sampler, 532 passes (one every 2.3 s) over a process tree of up to 34
Chromium processes and 9 Node drivers, saw 0 connections off the machine or
to a CDP port. 3 census lines were torn by processes appending at once; the
raw text holds no refusal anywhere.

THE DECISION, by the addendum's own rule: no destination besides the known
probe appears, so no socket-level guard is added -- the count above is what
says so. What stands between a test and the network outside a browser is
`tests/cdp_port_guard.py` for the one port and nothing for the rest, and
nothing needs it today. NAMED, NOT BUILT: that guard's wrap of
`socket.connect` is one condition away from refusing every address off the
machine. And the census cannot see a socket opened below CPython's socket
module, nor Node or Chromium between two of the sampler's passes, nor the two
subprocess pytest runs that the network and CDP guards' own controls start
with PYTHONPATH replaced -- those plant their own refused attempts.

AND THE CENSUS FOUND SOMETHING ELSE: the package's log on the console. The
census run's output held 5,343 package log lines at INFO or WARNING and 770
at DEBUG. Like for like: the 3.10 cell over this order's test files printed
none at ee9ad11 (a hash which does not resolve on `master` until this branch
merges), before the merge, and 5,208 and 768 at the merge. Measured, not
guessed: a planted PASSING test that logs a sentinel through the package
logger, run under `-n 2` with only `tests/cdp_port_guard.py` loaded,
puts the sentinel on the console; without that plugin, or without xdist, it
does not. The mechanism: the guard's configure hook read the port by
importing `linkedin_server.config`, which built the package logger's
`StreamHandler` in an xdist worker before that worker's capture began, so
the handler held the worker's REAL stderr. Every `-n auto` run since
the merge printed the suite's package log, a passing test's included -- on
this branch, with the echo control's planted fake session cookie and the
log-capture controls' synthetic names, which the DEBUG sites of U.4 now
emit. CI's shards run `-n auto` too (`ci.yml`): master's CI run
36362999033, on ff42daa, carries 5,932 package log lines in its log, read
back with `gh run view --log` -- type-only diagnostics and
the runner's temp paths, no planted value, because the DEBUG sites are this
branch's and never ran in CI before the fix. CORRECTION: the fix's own
commit message, 6a419b6, says CI's shards run without xdist. They do not;
this paragraph is the measurement.

FIXED, in the guard: it reads the port at the first connection it sees
(`_port()`), which happens in collection or in a test, under capture. The
new `test_the_guard_leaves_a_passing_tests_package_log_in_pytests_capture`
runs the planted test passing (no sentinel on the console) and failing (the
control: the sentinel shows, because pytest prints what it captured) -- RED
on the guard as merged, green on the fix. Both guards' test files: 24 passed;
the xdist run of the people-search log controls printed 5 package lines
before and 0 after.

### U.8 Gates run, and what did not run

PER COMMIT, each on its own tree before the next (the main venv, sharded;
every hash here does not resolve on `master` until this branch merges):

    1e51c3e   the endorsement test's file, the tool envelopes,
              test_tools, the orphan-module ruling              287 passed
              (the run that reached for the CDP port, U.7)
    c9277bd   the skeletons' test, the two privacy guards,
              the import-safety sweep                           1291 passed
    4daa38d   the patched log-capture files                     1079 passed, 1 xfailed
    4e0114d   the reader guard, the double's and the
              skeletons' tests -- HAND-PICKED                   878 passed
    ee9ad11   the identity sweep, the double's test, the
              synthetic-people guard                            1277 passed
    de8e95e   the new capture guard                             10 passed
    739c117   RED: the 18 new tests on the unpatched analyser   15 failed, 3 passed
              GREEN: every test file that exercises the gate    97 passed
    955adbc   the merge: the reader baseline regenerated,
              byte-identical to the hand resolution; then the
              gate on the merge, below
    6a419b6   RED: the log-capture test on the guard as merged  1 failed
              GREEN: both guards' test files                    24 passed

A HAND-PICKED GATE MISSED ONE, AND THE 3.10 CELL CAUGHT IT. The gate on
4e0114d was chosen by hand and left out the exact-identity sweep, which reads
every file rather than importing anything. The CPython 3.10 cell over the
order's files ran it: 2028 passed, 1 failed -- two synthetic `/in/Xxxx/`
hrefs in the double's own test, upper case, which the sweep's shape exemption
(lower case, as the builder writes) does not cover. ee9ad11 lowered them and
kept the assertion discriminating (a mutant that answers the href is red at
it). The analyser would not have missed it: its plan for that one file holds
the sweep twice over, as a sweeper of `tests/` and as a corpus-wide guard. A
gate is chosen by the analyser, not by hand.

THE GATE ON THE MERGE, `scripts/impact_gate.py --against master` at
955adbc (which does not resolve on `master` until this branch merges): 31
changed paths, 262 selected + 26 corpus-wide = 264 test files, WIDENED TO
THE FULL SUITE (`tests/conftest.py` is runner-wide, so scoping would be a
guess) -- PASS, 11982 tests, 1008 s (`-n auto --dist loadfile`).

THE FINAL GATE, on the code-final tree:
`scripts/impact_gate.py --against master` at 6a419b6 (which does
not resolve on `master` until this branch merges): 34 changed paths, 263
selected + 26 corpus-wide = 265 test files, WIDENED TO THE FULL SUITE
(`tests/conftest.py` again) -- PASS, 11983 tests, 954 s. This record's own
commit changes `_audit/` only; its scoped gate is in the report to the
orchestrator, which cannot be written into the commit it gates.

CPYTHON 3.10, through uv (the requirements, pytest-xdist, playwright
1.63.0): at ee9ad11 (which does not resolve on `master` until this branch
merges), every test file the order had touched by then (15), 2422 passed,
1 xfailed (the declared people-search limit), 337 s.
At the merge (tracked-dirty only by the network guard's docstring,
then uncommitted): 17 files -- the 15 and the two new ones -- 2505
passed, 1 xfailed, 516 s. At 6a419b6 (which does not resolve on `master`
until this branch merges), the two guard test files, the new log test's
own `-n 2` run included: 24 passed, 63 s.

THE CENSUS RUN, the full suite at 955adbc (which does not resolve on
`master` until this branch merges) under the socket census (U.7), its
refusals armed: 11,954 passed, 9 skipped, 1 xfailed, 18 failed -- the
census's own stray script (U.7); those two files re-ran under it, 29
passed -- 1,246 s.

NOT RUN, and named: CI's three platforms (this branch is not pushed; the
orchestrator pushes); anything live -- no LinkedIn, no Chrome, and port 9224
only in the one probe U.7 names, before the stub; the full suite on 3.10
(only the files this order touched); the stand-ins for `press:disclose` (its
Escape key) and `share_link:copy_own_post_link`, which no capture of the
after-state supports -- both stay driven to their click; the option's press
in the Interesting viewers switch, which no capture draws checked; the
shared cold reading that would make the analyser's test file cheaper (U.5).
