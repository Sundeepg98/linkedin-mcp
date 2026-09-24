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
