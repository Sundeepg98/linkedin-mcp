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

    00:30  worktree clean at 9c219c8; the four gaps read off their source records
    00:45  (b) prototype measured on the real tree
    01:10  two implementer children launched for (c) and (d), each owning two files
    01:40  (b) and (c) committed
    01:55  (d) reviewed and committed; the blocker map regenerated, 0 lines moved
    02:25  (a) red run: 24 readers launder; repaired; committed
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
`_send_gate` -- each print a `dom.py` reader's `error` into `out['why']`; four more
functions carry the same fields onward (`_live_control`, `_verify_after`,
`_read_item_comment_box`, `company_page_follow_verdict`); and
`server._read_connection_rows` copies `dom.read_recipient_ids`'s `error` into the
connections census. Fixing at the entry covers every one of them.

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
name the convention misses: an over-approximate whole-tree summary counts 102
such call sites across 44 callees. A whole-tree complement was built and
declined: 17.4 s per run, and on this tree its one extra site was a bare-name
collision between two modules' `_url_for` -- an artifact. The url-proven
`_SANITISERS` are not honoured by the reader walk. All of it is written beside the
code.

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

**MEASURED BEFORE WIDENING.** An implementer child folded each other keyword in
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

**THE REPAIR**, by an implementer child and reviewed here: the listing is now
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
6. **A readiness race under load.**
   `tests/test_click_is_not_its_own_evidence.py::test_the_refusal_names_the_ambiguity_when_no_matcher_can_help`
   read `1_no_listbox` in a six-worker batch on a busy box and passed alone (the
   module: 30 passed, 1 xfailed). That branch is decided by whether the listbox
   attached inside its wait, not by any field this lane changed.

## 6. COMMITS, GATES, AND WHAT DID NOT RUN

The commits, on this branch only until it merges (no ancestor of `master` yet):

| hash | subject |
|---|---|
| `1589837` | navigation guard: a value a reader returned is a derived navigation (J 57's blind spot) |
| `0926678` | hash citation guard: every slot keyword is case-folded, the hex class is not |
| `8013a30` | reason locator: a conflicted path is read once, not once per merge stage |
| `54ebb7f` | error fields carry the exception TYPE: fourteen dom.py sites, one write gate, and the guard that holds it |

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
