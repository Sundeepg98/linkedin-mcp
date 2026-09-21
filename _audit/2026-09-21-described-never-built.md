# A gate that was described and never built -- and the obvious repair was wrong

Wave `described-never-built`, 2026-09-21. Subject:
`dom.activate_messaging_filter`, the package's only click on a read path
outside `writes.perform` and `press.disclose`.

**THE DEFECT, as handed over.** The function's docstring said that a pill which
moves the page would mean *"the control does more than filter, and the read
classification that permits this click would no longer hold."* It measured
exactly that, as `navigated = page.url != before`, returned it, and **nothing
anywhere read it.** Found by the act-then-decide sweep in
`_audit/2026-09-21-refuse-before-the-click.md` section 8, reported rather than
fixed because it was not that wave's file.

**THE VERDICT, in one line.** The reading is not dead -- it is TRUE on the only
live activation this repository has ever recorded -- and the gate the docstring
describes could not be built on it, because a gate raising on `navigated` would
refuse the one run that ever worked. The reading now drives a refusal, on a
CLASSIFIED form of the same comparison. Commit `b73783a`.

---

## 1. CAN `navigated` BE TRUE IN PRODUCTION? YES, AND IT HAS BEEN

**VERIFIED-BY-RECORD**, from two independent files that agree, both written by
the wave that fixed the leak in question.

`_audit/2026-08-31-linkedin-perform.md` section 106, and the module docstring
of `tests/test_a_thread_id_never_leaves_the_module.py`, record the same live
`linkedin_open_messaging(message_filter="inmail")` reading taken on
2026-09-03:

    thread_opened.landed_url   ".../messaging/thread/<THREAD-ID>/"   safe
    active_filter.url_before   the whole id                          RAW
    active_filter.url_after    the whole id, plus ?filter=inmail     RAW

`url_after` is `url_before` with a query string appended. The comparison is a
raw string inequality taken before redaction, so on that run `navigated` was
**True**. That is the only live activation of this path on record; there is no
recorded run in which it was False.

**SO THE HONEST REPAIR IS NOT "DELETE IT AS DEAD".** The brief asked for a
control on that branch if it were taken, and the branch is not taken: one
positive observation settles it, and no control for a negative is owed.

**WHAT THE MEASURED CHANGE ACTUALLY IS.** The pill is client-side -- all seven
are `<button>` with no `href`, which is why a click exists at all -- and what
changed is a query parameter on the SAME thread address. LinkedIn wrote the
filter state into the url bar. The path did not move. The three loads recorded
in `_audit/2026-09-03-linkedin-gap-blockers.md` confirm the surrounding shape:
`/messaging/` redirects 1 -> 3 path segments on every load, so `before` is
always a thread address and never the root.

**AND THE SHIPPED TEST MODELLED THE CASE THAT HAS NEVER BEEN SEEN.**
`test_the_navigated_signal_survives_redaction` drives a fake whose url does not
change and asserts `navigated is False`. It is a correct test of redaction. It
is also the only place in the repository that touched the field, and it pinned
the one outcome production has never produced.

---

## 2. DOES THE READ CLASSIFICATION DEPEND ON IT? THE DOCSTRING OVERSTATES

The permission was verified at its source rather than inherited from the
sentence. `readonly.SANCTIONED_MUTATIONS` carries the entry
`("linkedin_server/dom.py", "activate_messaging_filter", "click")` and argues
for it in line, verbatim:

> *"A pill SENDS NOTHING and CHANGES NOTHING on LinkedIn's servers; it alters
> which rows are displayed. Counted by EFFECT rather than by verb, which is how
> this family classifies everything, a view filter is a read."*

plus the narrowing (`dom.MESSAGING_FILTERS` is a closed set matched before any
selector exists) and the comparative argument (the tool already opens somebody's
conversation, so refusing the lesser act while performing the greater one is
backwards).

**A QUERY APPENDED TO THE SAME ADDRESS IS THAT EFFECT, SPELLED IN THE URL BAR.**
"Which rows are displayed" is precisely what `?filter=inmail` records. It does
not touch the classification, and a gate that refused it would refuse the
permission working as designed.

**SO THE DOCSTRING IS OVERSTATED IN ONE DIRECTION AND THE FIELD IS UNDER-
MEASURED IN THE OTHER.** The docstring says *any* movement invalidates the
permission; that is false for the measured case. `navigated` is a bare string
inequality; it cannot tell the measured case from the one the docstring is
really about. Both halves are now corrected in place rather than argued around.

**WHAT DOES INVALIDATE IT** is the browser ending up at a DIFFERENT ADDRESS --
another host or another path. Two things follow, and the second is the one that
makes it a gate rather than an opinion:

1. The control did more than filter the view in front of it. The most plausible
   real instance is a filter that auto-selects the first conversation in the
   filtered list, which opens a SECOND person's thread. This tool prices opening
   one conversation as its unavoidable cost, in its own name; it does not price
   two.
2. The server is about to READ that page. `server.py`'s messaging tool takes
   `page.content()` and a reply-surface reading AFTER the filter. So a departure
   means the reading returned to the caller describes a page the read boundary
   never admitted, while `active_filter.activated: true` reports that the filter
   worked. `readonly.py`'s own allowlist comment names this gap already: *"the
   landed url is never re-checked"*.

---

## 3. WHAT WAS BUILT

### 3.1 The classification, in `linkedin_server/dom.py`

`FILTER_MOVEMENT_CLASSES` -- a closed tuple of three -- and
`classify_filter_movement(before, after)`, a pure function of two strings that
compares scheme, host and path (trailing slash normalised) and returns:

| class | what it means | response |
|---|---|---|
| `none` | the url is identical | permitted, reported |
| `filter_state` | query or fragment changed, same page | permitted, reported. **This is the 2026-09-03 measurement.** |
| `left_the_address` | host or path changed | **raises `WriteAttemptError`** |

The function returns members of a closed tuple and never a fragment of either
argument, so no page string can leave through it. `navigated` is KEPT, exactly
as it was, as the raw comparison behind the classification; the new field is
`url_movement`.

**UNMEASURABLE RESOLVES AGAINST THE CLICK, WITH NO BRANCH WRITTEN FOR IT.** An
empty or missing url shares no path with a real address, so it falls out as
`left_the_address` through the same comparison as everything else. No defensive
`except` was added: a malformed pair raises out of the classifier into the
caller's error path, which refuses the reading anyway, so writing a branch
production could never reach would have been the same defect this wave came to
fix.

### 3.2 What the raise gates, stated precisely

**It does not un-click the pill, and the code says so in the refusal text.**
Where a pill lands is not derivable before pressing it -- the pills carry no
`href`, which is the measured fact that made the click necessary. In the
`press.py` vocabulary this refusal is `after_the_act` and **cannot** be hoisted
to a zero-contact gate the way that wave hoisted its condition-3 pair.

What it does stop is the READING. The raise lands before the return, and the
only caller reads the page only after this call, so a page the classification
no longer covers is never read, never shaped and never returned. That ordering
is asserted by AST over `server.py` -- not by a hand-written mirror of it,
because a mirror drifts and then certifies nothing.

**THE REFUSAL NAMES NO ADDRESS AT ALL**, not even the redacted form: which
surface he was on is itself a fact about him, and this string reaches a model's
context through the caller's error envelope. It carries the filter name (closed
tuple) and the class name (closed tuple) and nothing else. A test asserts the
absence of both fabricated thread ids, of `https://`, of the host, and of the
surface path.

### 3.3 The controls, quoted failing

Eleven of the twelve tests in
`tests/test_the_filter_click_cannot_leave_the_address.py` were written first and
run against the unmodified module:

    11 failed, 1 passed in 0.74s

The one that passed is the structural claim about the caller's ordering, which
was already true and is not what this wave changes. The headline failure,
verbatim:

    ___________ test_a_pill_that_opens_another_conversation_is_refused ____________
            page = _Page(THREAD_URL, url_after_click=OTHER_THREAD_URL)
    >       with pytest.raises(WriteAttemptError) as caught:
    E       Failed: DID NOT RAISE WriteAttemptError
    1 failed in 2.07s

After the repair, the same file:

    12 passed in 0.33s

**THE CONTROL ON THE OBVIOUS FIX** is the one worth keeping.
`test_the_naive_gate_refuses_the_only_live_reading` implements
`raise if navigated` as a local mutant and runs it against the measured live
shape, where it fires. A gate whose only known firing is a false positive is the
act-then-decide defect inverted, and the test says so, so nobody re-derives it
from the docstring.

Three more controls that exist so the instrument cannot go quietly inert:

* `test_every_declared_class_is_reachable` -- each of the three classes is
  produced from a real pair of urls, and the produced set is compared against
  the declared tuple. No class exists that nothing can return.
* `test_the_class_vocabulary_is_exactly_what_the_function_can_emit` -- **by
  AST**, over the returned string constants of `classify_filter_movement`. A
  fourth class added in the code and not in the tuple fails here; so does a
  tuple entry nothing returns. Not by grep: a class name is a returned constant
  and a line scan cannot tell one from the same word in the prose above it.
* `test_every_class_is_classified_by_when_it_becomes_knowable` -- the
  `WHEN_KNOWABLE` map covers the vocabulary exactly, and the single refusing
  class is pinned as `after_the_act`.

### 3.4 The finding found while building the control

The first draft of the compose-surface test asserted that
`https://www.linkedin.com/messaging/compose/` is off the read boundary. **It is
not.** `readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS` holds that exact string, so
the composer ROOT is admitted for READING while every other compose spelling is
refused:

    is_read_url("https://www.linkedin.com/messaging/compose/")              True
    is_read_url("https://www.linkedin.com/messaging/compose/?context=pill") False

That turned a wrong assertion into the strongest argument in the file: **the
cheaper repair of re-checking `is_read_url` after the click would have permitted
a pill that landed the browser on the composer root.** Admissibility is not the
class that catches this; movement is. Both facts are now asserted in the test,
with a message telling the next reader to re-derive the argument rather than
delete the line if the exemption ever moves.

### 3.5 Cost

* **No new `evaluate` call site.** The `dom.py` waiver budget stays at 22 and no
  waiver was spent. The classification is a string comparison.
* **`readonly.py` is byte-identical.** No allowlist grew, no forbidden list
  moved, no frozen digest in `tests/test_readonly_boundary_invariant.py`
  changed, and `SANCTIONED_MUTATIONS` is unchanged at seven entries.
* **`server.py` and `errors.py` were not touched** -- a live wave owns both.
  `WriteAttemptError` is imported, not defined or modified; `server.py` is read
  by AST in one test and not otherwise consulted.
* Suites run green beyond the new file: the directly coupled six
  (`380 passed in 12.84s`), and the identity / taint / prose guards
  (`1280 passed in 49.68s`).

---

## 4. OTHER READINGS IN `dom.py` THAT ARE MEASURED AND UNUSED

**REPORTED, NOT FIXED**, per the brief. Swept mechanically by a delegated slice
and reviewed here; full method and tables in
`_audit/_slice-dom-unread-readings.md`. The rule: every string key in a dict
literal a function returns, plus every `out["key"] = ...` store on a bare-
returned dict, then a consumer count across `linkedin_server/`, `tests/`,
`scripts/` and `_audit/` prose, with the producing function's own line range
excluded. 256 findings over 130 distinct keys. Can-fail control: an invented key
scored zero in all five counts, and the positive case was hand-verified after
the auto-picked one turned out to be a same-named field a caller builds itself.

**UNREAD -- no code anywhere names them:**

| function | key | what it measures |
|---|---|---|
| `read_company_about_card` | `hrefs_error` | the exception TYPE NAME when the about-card link harvest raises. A condition, not decoration: its own comment records that the logging site was removed when a taint guard caught it leaking page text, and the field was never wired to a reader instead. The caller reads the sibling `hrefs` directly and discards this one. |
| `read_profile_views_insights` | `observed.metrics_seen` | how many metric rows the insights extractor recognised -- built, per its own docstring, so a page that rendered nothing recognisable still says so. It reaches the tool's JSON whole, via `extra` and `shape.envelope`'s `update`, but nothing branches on it and nothing could notice it silently going to zero. |
| `activate_messaging_filter` | `pill_label` | the matched accessible name. The descriptive one of the three: captured so an empty label beside `activated: true` does not read like a contradiction. For a human, not for a branch. Leave it. |

**TEST-ONLY -- returned, asserted on, never branched on by any code:**
`url_before`, `url_after` and (as of this wave) `url_movement` on
`activate_messaging_filter`; `residue_suspected` on `read_sdui_actions`;
`observed.heading_count` on `read_job_insight_panels`.

**THE SHAPE WORTH CARRYING FORWARD, and it is a limit of the sweep rather than a
finding:** a whole-dict spread is invisible to a key-string search.
`server.py` merges this function's entire return with `**applied`, and
`shape.envelope` merges `extra` with `update`, so a field can be simultaneously
present in the tool's JSON and unnamed by any Python. That is exactly how
`navigated` managed to be shipped, returned, read by a model, and enforced by
nothing. **A key-string census measures what CODE consumes, never what a caller
sees**, and the two questions are different.

**`hrefs_error` is the one worth a follow-up wave.** It is a measured condition
about a failed read, discarded on the floor, in a reader whose whole point is
that an unreadable card must not look like an empty one.

---

## 5. THE IMPACT GATE

Staged first, then run. **There is no `NOT CHECKED` line to quote: the gate
widened.** Its notice, verbatim:

      WIDENING TO THE FULL SUITE, because the impact set is 157 of 207 test files (76%), at or above the 45% line where running everything costs about the same and answers more.

      PASS over the FULL SUITE (7933 tests) in 756.6s.
      Still windows-only. CI runs three platforms and remains the certifier.

`dom.py` is imported by a large fraction of the suite, so any edit to it widens.
The pre-commit identity gate ran armed rather than disarmed in this worktree and
said so: *"identity gate examined 2 staged file(s) against 218 spellings; 0
hits."*

---

## 6. WHERE DISK DISAGREED WITH THE BRIEF

The brief invited this. Three items, all verified on disk.

1. **"Do not assume the answer is raise on navigated" -- correct, and for a
   sharper reason than the brief supposed.** The brief framed the fork as
   *"can it be true in production, or is it dead code"*. Disk answers a third
   way: it is true in production ON EVERY RECORDED RUN, and that is precisely
   what makes the naive gate wrong. The dead-code branch never opened.
2. **"Refusing after the click has already happened does not un-click it ...
   only knowable after is a legitimate answer and changes the repair to a REPORT
   rather than a gate."** Half right, and the half that is wrong matters. The
   condition is indeed only knowable after the act -- that is recorded as
   `after_the_act` and not smoothed over. But a post-act refusal still gates a
   real thing here, because the caller has not read the page yet. It refuses the
   READING, not the click. So the repair is a gate AND a report, and the
   distinction is written into the code rather than claimed in a summary.
3. **The compose surface is not the boundary case it looks like** (section 3.4).
   The composer root is admitted for reading by an exact-equality exemption,
   which is what killed the cheaper repair.

---

## 7. WHAT THIS WAVE DID NOT DO

* **Nothing live.** No browser, no port 9224, no navigation, no click on any
  real page. Every measurement is a fake page, a pure function, or a record
  already on disk.
* **No page string, name, url or id left any module.** The new refusal carries a
  closed vocabulary only; the classifier returns tuple members.
* **`server.py` and `errors.py` were not edited.** One test reads `server.py` by
  AST; nothing writes to either.
* **No allowlist, forbidden list, sanction list or frozen digest moved.**
* **`hrefs_error`, `metrics_seen` and `pill_label` were not fixed** (section 4).
* **No instrument was filed** in `_audit/INSTRUMENTS.md`. The sweep behind
  section 4 is declared DISPOSABLE with its rule written out: it counts key
  strings, it cannot see a dict spread, and its output needs a human to read
  each row. Registering a check whose result always needs a human is how a
  register stops meaning anything. What is durable from this wave is
  `WHEN_KNOWABLE` plus the AST vocabulary check in the new test file, which ask
  their question of one function mechanically and cannot be satisfied by
  relabelling.
* **Nothing was pushed.**
