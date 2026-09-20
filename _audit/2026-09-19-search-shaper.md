# The search-results shaper: both halves, controls shown red, and nothing admitted

Built 2026-09-19 by the `search-shaper` wave, on
`worktree-agent-a4a7c41bdf3ec4b68`, off `b5a2bc0`.

**ATTRIBUTION: 0**, measured over every commit below on message and trailers
(case-insensitive count of `co-authored-by`, `claude-session`,
`generated with`, `claude code`).

| commit | what |
|---|---|
| `fa5a314` | the route half: closed segments, traversal refused, query closed |
| `f85e959` | this deliverable's first version |
| `0f711c1` | the cross-engine layer -- `CONTROL_EXPECTATION` computed for the first time |
| `76caeb6` | the filter half: sixteen census rows the route table never touched |

**NONE OF THE FOUR SHAs ABOVE RESOLVES ON `master`, NOTED 2026-09-20.** Each
returns exit 1 on `git merge-base --is-ancestor <sha> master`; each resolves
only via `integrate-1821` and `worktree-agent-a4a7c41bdf3ec4b68`. The content
is not missing: `master` carries it, folded into one commit, `fa13985`
("integrate: eight waves' work, replayed as content onto the purged
history"). The route-half docstring (`fa5a314`), the `CONTROL_EXPECTATION`
table and its two limits (`0f711c1`), and the filter half's
`FILTER_CONTROL_EXPECTATION` / `tally_filters` / sixteen-row section
(`76caeb6`) are verbatim or near-verbatim in `master`'s
`linkedin_server/search_results.py` today, confirmed with `git blame`. This
document's own text was itself rewritten before that replay (`f85e959`'s 189
lines became a further branch commit's 266 before landing here), so the table
above names what each commit DID, not a byte-for-byte ancestor of this page.
Row-by-row evidence and the branches' disposition:
`_audit/2026-09-20-the-six-unremapped.md`.

**`readonly.py` IS UNTOUCHED ACROSS ALL FOUR.** No address admitted, no write
fired, no browser opened, no page loaded on any path. Every number here comes
from fixtures and from the shipped scripts' own source, executed under node
v25.2.1.

---

## 1. THE BRIEF'S COUNT WAS WRONG, AND THE ERROR MATTERS

My brief said **"21 rows, every one a READ."** Enumerated off
`_audit/_census/blocker-map.tsv` -- which `tests/test_blocker_map_is_derived.py`
certifies as re-derivable from `_audit/_census/blocker-assignments.tsv`, and
which I had re-run fresh rather than trusted (**7 passed**) -- the blocker holds:

> **21 rows: 20 READS and ONE WRITE.**

`N 4` -- *send an invitation from a people-search result* -- is the write.
`blocker-map.tsv`'s own note on the shared block says its ruling **"must not
ride along with the reads... A DIFFERENT RULING. Not this one."** The ruling in
section 6 says **20 rows**, and so does
`_audit/2026-09-19-what-a-reader-could-actually-close.md`. **"21 rows, every one
a READ" conflates the total with the read count**, and the two are kept
deliberately separate by every published source.

This is not pedantry. A shaper written against "all reads" is a shaper with no
reason to prove it cannot fire. **Condition 5 is now a test** (section 4).

*Note on drift:* `_audit/2026-09-05-search-results-measured.md` records this
blocker as **19R/2W**. The certified map today reads 20R/1W. Both were right
when written; `N 194` was re-filed into this blocker as a LEDGER-AMENDMENT
since. **The certified map governs.**

---

## 2. THE ROUTE HALF SERVED FIVE OF TWENTY READS. THAT WAS THE REAL GAP.

The reads split in two and the split is not even:

| rows | what they ask | served by |
|---|---|---|
| `N 79`, `N 161`, `N 179`, `N 194`, `M C70` (5) | *which search is this, what shapes does it hold* | the route table |
| **`N 80`-`N 94` (16)** | **which FILTERS does this search offer** | **the filter panel** |

**Sixteen of twenty are filter rows**, and a route classifier answers none of
them -- filters are pressable controls with labels, not routes. Shipping the
route half alone and calling the blocker addressed would have been a 5/20
answer wearing a 20/20 headline.

`_audit/_census/network.md` on rows 79-93, verbatim:

> **"the largest single hole in the slice and the only one that is pure
> silence. Fifteen consecutive rows, all READ, all reversible by construction,
> and the repository contains ZERO SENTENCES about any of them."**

These are the first.

---

## 3. THE SHAPER, AND THE FOUR PROPERTIES THE BRIEF NAMES

`groups.py` -> `menus.py` -> `anchors.py`, each sharper than the last, all one
engine: **vocabulary shipped INTO the page, an integer index returned, the
mapping back done in Python, a closed output alphabet.** Both halves keep it.

* **Structurally name-free on `inspect.signature`.** No function in
  `linkedin_server/search_results.py` takes `href`, `url`, `slug`, `id`, `urn`,
  `profile`, `member`, `name`, `person`, `people`, `keywords`, `query`, `q`,
  `needle`, `search`, `term` or `text`. Both readers are `(page, html)` where
  `html` is the documented control path; `tally` and `tally_filters` -- the
  functions a caller publishes -- take INTEGERS and cannot be handed a needle.
* **Closed output alphabets.** 14 route kinds, 14 filter terms, 6 value
  classes, plus `index_out_of_range`. Asserted over adversarial indices
  including negatives and 10,000. Out of range **REFUSES, never clamps** --
  index 0 of each tuple is a hazard class, so a clamp could rename a page of
  people into a page of companies, or a person-valued filter into a degree one.
* **Vocabulary in, index out.** Neither script returns a string it was given,
  on any path. The filter matching happens **in the page** precisely because a
  people-search filter label can read `Connections of <a person>`.
* **A slug is refused BECAUSE A SLUG IS A NAME**, restated in the module
  docstring because a search page is exactly where a reader will want to cross
  that line. A non-route segment's SHAPE is counted; its value never leaves.

`person_result` is route index 0; `connections of`, `followers of`, `keywords`
are filter indices 0-2. The hazards are first so that anything misclassifying
into or out of them is the defect the rules exist to prevent.

---

## 4. WHAT IS NEW HERE, BEYOND FOLLOWING THE PATTERN

### a. CLOSED PATH SEGMENTS -- the amended condition 2, in code

Condition 2 was amended because anchoring was measured to do none of the work:

    ^https://www.linkedin.com/search/.*$  anchored both ends -> 18 admitted
    /search/ wildcard, unanchored                            -> 18 admitted

`RESULT_TABLE` closes **three** segments by equality at fixed positions.

### b. A TRAVERSAL IS REFUSED, NEVER RESOLVED -- the closure `anchors.py` lacks

    /search/results/people/../../mypreferences/d/close-account

Its first three segments are a people search; its normalised form ends his
account; **no forbidden substring names it** and the denylist refuses its
siblings. A dot segment anywhere is counted `traversal_refused` and never
normalised. **Resolving it would mean the shaper deciding what a traversal
means** -- the browser's job, and a shaper that guesses has invented a second,
disagreeing URL parser inside the guard.

### c. THE QUERY IS WHERE THE NAME IS TYPED

Cut before any segment is read (asserted by string position in the shipped
source); only its PRESENCE is counted. A caller can learn results were
filtered, never by what.

### d. THIS VOCABULARY BUILDS IN ITS OWN `Star Anise`, ON THE HAZARD

`connections` is a **prefix** of `connections of`, and they are different rows
with different value classes: `N 81` is a degree taxonomy, **`N 85`'s value IS
A PERSON.** Two things keep them apart and **both** are needed -- longest-first
ordering (computed in Python, where it can be tested) and `menus.py`'s
single-word asymmetry. Section 5 shows what happens without the second.

### e. CONDITION 5 IS A TEST, NOT A SENTENCE

An AST walk over the module refuses any call to a page-acting verb (`click`,
`press`, `fill`, `submit`, `goto`, ...) and any `confirm`/`token` parameter.
**It reads the TREE, not the text** -- the module's prose says "press" and
"send" while describing what it will not do, and a grep cannot tell a sentence
from a statement.

---

## 5. CONTROLS SHOWN FAILING

An instrument enters only if it has been shown failing. **39 tests, 0 skipped.**

### THE ONE THAT MATTERED MOST: A PREDICTION NOTHING HAD EVER PRODUCED

The route half shipped with `CONTROL_EXPECTATION`, a table of fixture counts.
**The classifier is JavaScript and the suite was structural, so nothing had
ever computed it.** A control whose result nobody computed cannot fail; the
register's second law was being broken by the very file asserting it.

The fix was structural: **the decision is now a pure function.**
`classifyRoute` closes over nothing -- every input is a parameter, no DOM in it
-- so the SHIPPED source can be lifted by brace-matching and run under V8. The
anchor loop that remains holds no policy, so a green control on `classifyRoute`
is a green control on the rule.

**The instrument is imported, not invented:** `tests/test_compose_fields.py`
already lifts `shapeOf` this way, and this repository has a scar for writing a
second copy of a check it already ships.

### MEASURED: 22 ROUTES, EVERY PREDICTION CONFIRMED BY V8

Including, on the row the ruling turns on:

    /search/results/people/../../mypreferences/d/close-account -> traversal_refused

### MEASURED: TWO ENGINES, ONE RULE, **AGREEMENT 20/20**

The filter rule must exist in JS (the label must not cross) and already exists
in Python (`menus._contains_phrase`). Two implementations that agree today can
disagree tomorrow, so agreement is measured over a 20-case corpus rather than
argued. Every case agreed, including the collision and the `Star Anise` shape.

### THE REDS

| control | shown red | how |
|---|---|---|
| traversal rule, **under the real engine** | the SAME V8 calls the account-ending address `person_result` | dot test stripped from the lifted source |
| traversal rule's presence | the source reader returns False | rule stripped from the script |
| traversal rule, live mutation | `1 failed, 20 passed`; restored -> `21 passed` | `dom.py` edited on disk, then restored from the commit |
| **single-word asymmetry** | the SAME V8 matches `Connections of` against `connections` **and** `School Anise` against `school` | asymmetry replaced with containment |
| kind order | `term_for(0)` stops being `person_result` | index 0 swapped |
| fixture tally | an unpredicted anchor changes the tally | extra anchor appended |
| **firing guard (condition 5)** | finds `click` and `confirm_token` | aimed at a synthetic module that presses a control |

That last one matters: run only against the shipped file, the firing guard is
green whether it works or not, because the shipped file has nothing to find.

### AND ONE GUARD FIRED FOR REAL, MID-BUILD

During the V8 refactor the table-lookup helper was renamed to a bare
`indexOf`, which made `indexOf(row[0])` indistinguishable on sight from a
containment match against a table row. The containment guard went red.
**The fix was the rename, not a softer assertion.**

---

## 6. THREE LIMITS, MEASURED AND DECLARED

A limit nobody measured is indistinguishable from a limit nobody has.

1. **Matching is CASE SENSITIVE**, and the miss lands on the safe side:
   `/SEARCH/RESULTS/PEOPLE/` is `off_search` -- unrecognised, never admitted. A
   case-insensitive repair would widen what matches a table whose whole job is
   to be narrow.
2. **A PERCENT-ENCODED TRAVERSAL IS NOT REFUSED.**
   `/search/results/people/..%2f..%2fmypreferences` classifies as its vertical.
   `%2f` is not a path separator to this classifier **and is not one to a
   browser either**, so it does not traverse. It stays unfixed because the
   repair would be a decode step, **and decoding is normalising** -- the same
   reason a traversal is refused rather than resolved. If a user agent is ever
   shown to decode it, the repair is a refusal of the encoded form, never a
   decode.
3. **A DECORATED SINGLE-WORD LABEL MISSES.**
   `Keywords (first name, last name)` does not match `keywords`, and the
   census's own wording for `N 93` is exactly that decorated form. The miss is
   reported in `unmatched_controls`, a visible number. **The repair is another
   vocabulary phrase, never a looser matcher** -- looser is precisely the
   mutation that collapses the hazard collision.

---

## 7. WHAT REMAINS BEFORE CONDITION 1 IS SATISFIABLE

Condition 1 is **satisfiable and still unsatisfied.** The shaper exists; the
admitting commit is the other half and **it is not mine to fire.**

1. **Both halves in ONE diff.** The shaper is committed separately because it
   admits nothing and therefore cannot violate condition 1 alone. The admitting
   commit must add the allowlist entry AND wire this module in the same diff.
   **A shaper nobody calls is not a shaper** -- `76caeb6` existing on the
   branch (not on `master`; its content is in `master` via `fa13985`, see the
   note above) does not discharge condition 1 by itself.
2. **The pattern must use CLOSED SEGMENTS, not anchors.** `RESULT_TABLE` is the
   vocabulary it should mirror. Four addresses are needed, not one: people,
   groups, events, and content/hashtag -- and **`N 194`'s address is still
   UNSETTLED** between `/search/results/content/?keywords=%23...` and
   `/feed/hashtag/<tag>/`, which is a different family entirely.
3. **`MUST_STAY_REFUSED` must drop `groups` and `events`** (or move them to a
   conditional block naming S1). Those entries forbid 3 of the reads the
   admission exists to serve.
4. **The revert test is REWRITTEN AND INVERTED, not deleted.**
5. **`N 4` MUST NOT RIDE ALONG.** It is the one write; its ruling is not
   inherited. The firing guard in this suite is the shaper-side half of that,
   but the boundary side is the admitting commit's to hold.
6. **The identity gate reads the INDEX, not the worktree**, and in a worktree
   only its shape half is live. Every commit here passed it; the admitting
   commit carries fixture and pattern strings and must be checked the same way.

**NOT CLAIMED:** that this shaper has ever seen a live search page. It has not,
and the emission question the 2026-09-05 measurement left open
(*"the evidence path is CIRCULAR: the measurement that would justify opening
the surface can only be completed by opening it"*) is untouched by this work.
That is prong (b) and it is an operator decision. This is prong (c) --
*the boundary decides what may be OPENED, the shaper decides what may be
SAID* -- and it is done.
