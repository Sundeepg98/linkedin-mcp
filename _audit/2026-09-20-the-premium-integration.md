# THE PREMIUM INTEGRATION: a union neither side's CI ever ran, and a refusal one of them reversed without knowing

Merging `worktree-agent-a0080c22085e727a5` (the `premium-four` wave) into
`master`. Base `dc5aaa6`, master `d6b7e4b`, wave tip `94d60ef`.

**THE HEADLINE IS NOT THE ALLOWLIST.** The four entries are argued well and
they survive scrutiny. What this integration found is that the incoming wave
**reversed a deliberate refusal recorded on 2026-09-05** and said in its own
shipped comment that the address had never been recorded here at all -- and
that the tripwire built to catch exactly that arrival fired, correctly, and had
never been run by the wave that tripped it.

Two prior attempts at this merge were aborted rather than ratified. Both stopped
on the same question, and section 4 answers it.

---

## 1. WHAT SHIPS, AND WHAT IT IS THE UNION OF

Counts taken by `ast`-parsing `_ALLOWED_URL_PATTERNS` at each ref, never by
grep over pattern text.

    dc5aaa6   merge base   36 patterns
    d6b7e4b   master       37   (+1)
    94d60ef   wave tip     40   (+4)
    merged                 41   (+5 over master)

    deletions on either side      0
    overlap of the two additions  0
    merged == master | wave       EXACT UNION, no member missing, none extra

**HALF ONE -- `live-capture`, +1, already on master.** `/jobs/jam`: the address
`/jobs/alerts/` LANDS on. `/jobs/alerts/` is ALLOWED by our gate and LinkedIn
redirects away from it -- it does not 404, it serves a page at a different
address, so a load scored pass/fail looks like success. That entry's own comment
pre-authorised the repair. `jam` was not among the sixteen three-letter
spellings a probe had enumerated, and the row sat dead for fifteen days behind a
search space that looked guessable; it was closed by RECORDING THE LANDING URL
of one load.

**HALF TWO -- `premium-four`, +4, arriving here.**

    /jobs/collections/top-applicant     reader ships with it
    /jobs/collections/top-choice        reader ships with it
    /analytics/recruiter-views          NO READER -- section 5
    /premium/profile-key-skills         NO READER -- no captured sibling exists

All four were read off LinkedIn as DRAWN ANCHORS in stripped markup, never as
substrings of the raw document. That distinction is load-bearing on this corpus
and the wave measured it: `inmail` occurs 16-21 times raw and **0** rendered;
`/premium/profile-key-skills` occurs twice raw and **once** drawn, so one of its
two occurrences is bundle text. Sharper still, `top-applicant` and `top-choice`
occur 8-10 times as BARE SUBSTRINGS on four captures that draw **zero** anchors
for either route -- ordinary job-card badge text. **A raw-substring census would
have reported both routes drawn on four surfaces instead of one, and argued two
allowlist entries on evidence that does not exist.**

---

## 2. THE MEASURED BLAST RADIUS, AND TWO KINDS OF ZERO THAT MUST NOT BE ADDED UP

Measured with the shipped `scripts/blast_radius.py`, imported and not
re-implemented, over two corpora: its own (n=67) and the wave's new
`tests/fixtures/synthetic/drawn_routes.txt` (n=44, every route shape a drawn
anchor produced across six live captures, member and id segments replaced by
placeholder tokens).

### 2.1 Each entry admits exactly its own address

| pattern | blast n=67 | drawn n=44 |
|---|---|---|
| `/analytics/recruiter-views/?$` | +0 | +1 (itself) |
| `/premium/profile-key-skills/?$` | +0 | +1 (itself) |
| `/jobs/collections/top-applicant/?$` | +0 | +1 (itself) |
| `/jobs/collections/top-choice/?$` | +0 | +1 (itself) |
| `/jobs/jam/?$` | +0 | +0 (no such address in either corpus) |

### 2.2 The family patterns NOT taken, and what they would have cost

| candidate | blast n=67 | drawn n=44 | what it newly reaches |
|---|---|---|---|
| `jobs/collections/[a-z-]+/?$` | 0 | **0** | -- |
| `analytics/.*` | 0 | **0** | -- |
| `jobs/.*` | 0 | **1** | `/jobs/` |
| `premium/[a-z-]+/?$` | 0 | **2** | `/premium/premium-perks/`, `/premium/switcher/` |
| `premium/.*` | 0 | **3** | + `/premium/sb/explore/` |

Every address in that last column was defended by NOTHING before --
`newly_admitted_and_defended_by_nothing` reports 1, 2 and 3, matching the
totals. No denylist entry was refusing any of them.

### 2.3 THE TWO ZEROS ARE NOT THE SAME ZERO

**The entire `blast n=67` column is an empty-denominator artifact and certifies
nothing.** That corpus holds **zero** addresses under `/jobs/collections/`,
**zero** under `/premium/`, and **one** under `/analytics/`. It reports +0 for a
bare `/premium/.*` wildcard. A tool that reports zero for everything is
indistinguishable from a broken one, and the wave treated its zero as a question
about the denominator rather than an answer about the pattern -- which is the
only reason the drawn corpus was built.

The two zeros in the `drawn n=44` column are a **different and real** kind:
`jobs/collections/[a-z-]+` and `analytics/.*` measure 0 over a POPULATED
denominator (2 members each), because on today's evidence every member of those
families is already admitted. That is a measurement. **It is still not a reason
to take the family pattern**, because a corpus cannot see an address LinkedIn
has not drawn yet.

### 2.4 An unrelated finding worth recording: `/premium/` has no denylist floor

Measured while checking whether a wildcard is bounded by anything other than the
allowlist. It is, in one family and not the other:

* `jobs/.*` takes `/jobs/` from 3 admitted to 4 of 5. `/jobs/application-settings/`
  **stays refused**, by the denylist substrings `['/jobs/application', 'settings']`.
* `premium/.*` takes `/premium/` from 1 admitted to **4 of 4**. Nothing bounds it.
  **The `/premium/` family has no denylist coverage whatsoever.**

Nothing in this merge depends on that. It is recorded because it means the
narrow `/premium/profile-key-skills/?$` anchor is doing ALL of the work in that
family, and a future wave tempted by `/premium/<class>/` should know there is no
second gate behind it.

### 2.5 The union cross-term: zero, measured

For every address in both corpora plus 7 constructed ones (111 deduped),
`is_read_url` was evaluated under three separately imported modules -- master-37,
wave-40, union-41 -- each asserted to carry the right pattern count.

    addresses the union admits that NEITHER side admitted alone   0
    addresses the union LOSES that either side admitted           0
    refusal TEXT the union produces that neither side produced    0

That last row matters more than it looks: `_ALLOWED_URL_PATTERNS` has **two
executable sites**, and only one is the verdict. One decides admission; the
other runs inside the denylist loop and selects only the refusal *wording*. The
cross-term was measured on both.

### 2.6 Through the real guard, both spellings, clean and not excused

All five addresses, `/` and no-`/`, through the real `is_read_url` /
`assert_read_url`: **10 of 10 False on master, True on merged**, each matched by
**exactly one** pattern -- its own. For every one:

* forbidden substrings present in the url: **`[]`** (none of the 33)
* `_FORBIDDEN_SUBSTRING_EXEMPTIONS`: returns nothing
* `_pattern_exempted_substrings`: empty frozenset

**Neither exemption table is engaged. These addresses are clean, not excused** --
which is exactly what each entry claims about itself, now checked rather than
trusted. `/jobs/collections/`, `/analytics/`, `/premium/` and
`/premium/premium-perks/` all remain refused, and for them no denylist substring
is involved either, so the allowlist anchor is the WHOLE of the refusal.

---

## 3. THE FINDING THIS INTEGRATION EXISTS FOR: A REVERSED REFUSAL, UNNOTICED

The shipped entry for `/analytics/recruiter-views` opened:

    NEVER RECORDED ANYWHERE IN THIS REPOSITORY BEFORE 2026-09-20.

**That is false, and the tree said so at the merge base.** At `dc5aaa6`:

| where | what it said |
|---|---|
| `tests/test_analytics_creator_boundary.py:83` | the address, in the REFUSED-NEIGHBOURS table, reason: *"DRAWN BY THE PROFILE-VIEWS PAGE, twice, and not admitted"* |
| `tests/test_analytics_creator_boundary.py:137` | the same address again, in that file's two-sided control |
| `tests/test_readonly_boundary_invariant.py:737` | a comment recording the same sighting |
| `tests/fixtures/profile_views_analytics.html` + `_hydrated` | the full drawn url, verbatim, twice each -- TRACKED since before either |

Commit `4c2de7e`, 2026-09-05. A previous wave saw **the same two anchors**,
considered this address, and declined it.

**THE ADMISSION IS KEPT.** The 2026-09-05 row was not a ruling that the page may
never be admitted; its own text says being drawn by an admitted page is a reason
to CONSIDER an address, *"never a reason to have admitted it -- one named page at
a time, never the family."* It was declining inheritance. The premium-four entry
supplies precisely what was missing: its own named argument, its own blast
measurement, a reader costed and declined. **That is the standard being met, not
bypassed.**

But three things had to change, and none of them is a number bump:

1. **The claim is corrected in `readonly.py`.** The entry now states that it
   reverses a prior deliberate refusal, names the commit, and says why the
   reversal stands. An admission is not a first sighting when the tree already
   holds the sighting.
2. **The neighbours row is removed, not edited**, so nobody reads a refusal the
   file no longer makes -- replaced by the QUERY spelling, which that file can
   still legitimately refuse (section 5).
3. **The count tripwire was RAISED, and the raise is argued.**
   `test_the_admitted_analytics_pages_are_exactly_three` existed, in its own
   words, so that *"a fourth analytics page cannot arrive unnoticed."* A fourth
   arrived. **It noticed.** It is now `..._exactly_four`, 4 pages / 5 patterns,
   with an added assertion naming `recruiter-views` specifically so the number
   cannot absorb the next arrival silently. A count like this is RAISED, never
   loosened into a bound.

### 3.1 WHY NOBODY SAW IT: the scoped gate did not run the file

The wave's freeze commit reports *"Impact gate: PASS over 29 files, 1354
tests."* `tests/test_analytics_creator_boundary.py` was not among them. The file
is unchanged at the base AND at the wave tip -- so **the wave's own tree was
already red on it**, before any merge, and the red was invisible because the
gate is scoped to what the diff appears to touch.

This repository wrote that hazard down the same morning, in
`scripts/impact_gate.py`'s own docstring: a name-based impact rule waved a
markdown edit straight through to a red parser. **This is the same defect
arriving through the other door** -- not a file type the analyser skips, but a
COUPLING it cannot see: a test that asserts a refusal is coupled to an
*allowlist entry that does not exist yet*, and no name-based rule can find that
edge, because the name only appears once the entry is written.

The general shape, and it generalises past this repo: **a scoped gate can see
which tests name the code you changed. It cannot see which tests assert the
ABSENCE of what you just added.** A refusal test is exactly that assertion.
Filed as an instrument-register finding, section 32.6.

---

## 4. THE WRITE-PATH QUESTION: A STATIC PIN CONSEQUENCE, AND A CHECK THAT CANNOT SPEAK

Two previous attempts aborted here. The failing test is
`test_the_write_did_not_touch_any_of_the_four_denylists`, whose message reads
*"`_ALLOWED_URL_PATTERNS` moved across the write."* The open question was whether
that is a static-pin consequence or a genuine runtime invariant about write
paths. **It is a static pin consequence, and it is worse than that.**

### 4.1 How it was established

Not by reading the docstring, which is wrong. By reading the machinery:

`ast_digest()` is a **pure function of source text**. The test module's entire
import list is `ast, hashlib, io, re, tokenize, pathlib, pytest`. There is no
`importlib`, no `__import__`, no `exec`, no `eval`, no `subprocess`, no `runpy`;
`linkedin_server` is never imported, only named in strings. The only filesystem
contact in either test is `READONLY.read_text()`. `_function_source` uses
`tokenize` ONLY to locate comment spans by position, never to ask what a string
is made of.

**Nothing in it observes a write path, a browser, a network call or any runtime
behaviour. "The write" in the name refers to the 2026-08-23 arrival of this
package's first mutating call -- a historical code change.** The name misled two
readers; its docstring now says so in its first line.

### 4.2 And the check has no independent power at all

`DENYLISTS_AT_A76FE32` claims to hold *"the four denylist digests as they stood
at `oldsha14`"*. Measured over all 39 commits that have touched the file, both
dicts extracted by `ast` from each committed blob:

    commits where the baseline dict exists            36
    commits where it was REWRITTEN                    25
    commits where a shared key held a DIFFERENT value  0   <-- not once, ever
    every baseline change landed in the same commit
      as the corresponding pin change                YES

The 7 pin-only changes are confirmation, not counter-evidence: every one moved
only a key the baseline does not carry. **There was never even a one-commit
window in which a shared key disagreed.** The lockstep has an origin -- the live
pin was itself named `READONLY_AST_AT_A76FE32` before the baseline was split out
of it.

The dict is named for a commit that **does not resolve in this repository any
more**. Its docstring's claim is true today only of `JS_MUTATION_TOKENS`;
`_ALLOWED_URL_PATTERNS` stopped being its pre-write value at `5681130`
(2026-08-26) and 22 times since, `_FORBIDDEN_URL_SUBSTRINGS` five times,
`_MUTATION_CALL_PATTERNS` at `989e19d`. The test is named for FOUR denylists, the
dict held FIVE keys, and only three of those five were refusals.

**SHOWN, NOT ASSERTED.** Eight single-structure edits applied in memory to
master's `readonly.py`, both test bodies evaluated against each:

    edits that red BOTH tests             5
    edits that red the PIN test only      3
    edits that red the DENYLIST test only 0

The denylist test's failure set is a strict SUBSET of the pin test's. **It
cannot go red on any input that leaves the pin test green.** It is a restatement
of 5 of the 8 assertions the pin test already makes; what it adds is a nicer
failure message.

### 4.3 What was done about it, and what deliberately was not

**`_ALLOWED_URL_PATTERNS` was REMOVED from the baseline dict, 5 keys to 4.** Not
re-synced to the new value, which is what 25 prior commits did and what would
have perpetuated a check that cannot fail. The removal loses **zero** coverage,
and that is checkable rather than asserted: the same structure is pinned at the
same value by `READONLY_AST_AT_LAST_REFREEZE`, which every read admission must
update anyway and which carries the argument. After it, the allowlist digest is
asserted **exactly once**, in the place whose job it is.

What the removal buys: a READ ADMISSION CAN NO LONGER TOUCH THAT DICT AT ALL.
The four remaining keys move only when a refusal moves or a grant widens -- so
the next edit that dict needs is itself the signal.

**NOT OVERSOLD, and this is the part a reviewer should hold me to:** the four
remaining values also equal the live pin's, so the test **still cannot fail on
its own**. Narrowing it did not resuscitate it. That is now stated in its own
docstring rather than left for a reader to discover.

**AND THE REAL DECISION IS DEFERRED ON PURPOSE.** Whether this test should be
redesigned or deleted outright is NOT settled here. Deleting a boundary guard is
a ruling; this was an integration. **OPEN ITEM, for whoever holds the next
boundary wave:** the honest options are (a) delete it, since its coverage is
entirely duplicated; or (b) give it the one job it could uniquely do -- assert
DIRECTION, that no refusal structure has ever SHRUNK -- which a digest cannot
express and which today lives in `test_the_scanner_has_only_ever_gained_detectors.py`
and `test_the_second_gate_covers_the_class.py` instead. Option (b) may mean it
has no job left.

---

## 5. THE `timeRange` DECISION: THE PATTERN STAYS BARE, AND THE STATED REASON WAS WRONG

The shipped entry is anchored with no query allowance, while the href LinkedIn
draws carries one. The entry documented this as a deliberate trap and said the
values were unknown, requiring a page load to settle.

**THE VALUE WAS NEVER UNKNOWN. IT IS TRACKED IN THIS REPOSITORY AND HAS BEEN
ALL ALONG.**

    timeRange=WvmpSearchFilterTimeRange_LAST_90_DAYS

ONE distinct value, drawn TWICE as a real `<a>` anchor in RENDERED markup -- both
hits outside all 16 `<script>` spans of the capture, verified by computing the
span offsets rather than by eye. And it sits, verbatim and twice each, in
`tests/fixtures/profile_views_analytics.html` and its `_hydrated` sibling,
**tracked on master and on the wave branch**. A repo-wide sweep found the token
in exactly two tracked paths and one untracked capture, and nowhere else.

**`past_90_days` IS A GUESS THAT DOES NOT WORK ON THIS ROUTE**, and this repo's
own tests had been pinning it. Two vocabularies live under one parameter name:
an enum token here (WVMP = who-viewed-my-profile), and snake_case `past_7_days`
on the `/analytics/creator/...` routes. Reading one route's values tells you
nothing about another's. It is the `?stage=draft` label/address split again,
pointing the same way: the page's control reads "Past 90 days", the address
reads `..._LAST_90_DAYS`, and the words on the control are once more the one
guess that fails.

### 5.1 THE RULING: keep the pattern bare

The jobs-tracker precedent sets three requirements. Two are now met with zero
page loads -- the token is read off a drawn anchor, and its evidence is in a
tracked fixture, so it survives a clone. **The third is not met, and it is
decisive:** admit only what something actually opens. Measured across the whole
package, **no caller exists** -- zero occurrences of this route in
`linkedin_server/` outside `readonly.py` itself; no `page.goto`, no url
construction, no tool.

And the condition the entry set for widening -- *"if the bare address does not
serve"* -- **is still a hypothesis. Nobody has loaded it.** Admitting a second
spelling to pre-empt a failure nobody has observed would be the `/jobs/alerts/`
error run backwards: guessing where an address lands instead of recording it.
That wave's whole lesson was that enumerating candidates is not a substitute for
reading where the browser went.

So: **bare, and the entry now says plainly that it admits a spelling the page
does not draw.** The blocker is restated correctly -- not "unknown values" but
"no caller, and an unloaded address" -- and the repair is written out as a
one-line edit for whoever opens the page, enumerating the one token that is
drawn and explicitly NOT a `(\?[^#]*)?` group.

### 5.2 THE TRAP IS NOW TESTED, WHICH IT WAS NOT

This is the part that was actually broken. `tests/test_premium_four_boundary.py`
pinned the refusal using `past_90_days` -- **a url LinkedIn never produces on
this route.** The test passed, and certified nothing: the trap its own entry
describes at length was not asserted anywhere. The REAL drawn url is now pinned
as refused, in both spellings, in that file and in
`tests/test_analytics_creator_boundary.py`. The guess is kept beside it, because
it is still a url the gate must refuse and keeping the pair together is what
stops the two being confused again.

**One thing is NOT fixed and is flagged rather than quietly left:** the refusal
message does not name what it matched -- it echoes the url and names the table.
With the pattern bare, that message is the entire trap-disarming mechanism for a
caller who hits it, and it does not disarm anything. That is a standing defect
against `refusals-must-name-what-they-saw`, it is not this merge's to fix, and
it is now pinned by a test either way.

---

## 6. THE RE-FREEZE

    _ALLOWED_URL_PATTERNS   3561b00ed3a817bc -> 286c233a7db458c7   37 -> 41

    <functions>                              d7e1d0922e3af446   UNCHANGED
    JS_MUTATION_TOKENS                       d47e30b67c583c1b   UNCHANGED
    SANCTIONED_MUTATIONS                     3676d309ead50c61   UNCHANGED
    _FORBIDDEN_SUBSTRING_EXEMPTIONS          43e2bf7f3db0dbed   UNCHANGED
    _FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS  419e64a3cd92ec7e   UNCHANGED
    _FORBIDDEN_URL_SUBSTRINGS                b0291a66ec9bd51e   UNCHANGED
    _MUTATION_CALL_PATTERNS                  10a0e8e2bb4d7812   UNCHANGED

**SEVEN OF EIGHT UNCHANGED, measured across all four trees** -- base, master,
wave tip and merge -- not asserted from the two ends. `<functions>` unchanged
means `assert_read_url` is BYTE-IDENTICAL across a change that admitted five
addresses: the whole change is DATA, which is the only shape of boundary change
a reviewer can check by reading a list.

**THE WAVE'S OWN PIN `0225ae77ddcefe2e` IS NOT RECORDED IN THE LEDGER, AND THAT
IS DELIBERATE.** It was computed over a 40-pattern roster branched from
`dc5aaa6` (36 entries, `85e821d1af9060f3`) which never carried `/jobs/jam`. The
transition `85e821d1af9060f3 -> 0225ae77ddcefe2e` describes a tree that never
shipped, and writing it into master's ledger would record a move master never
made. The ledger entry names both waves' admissions instead, so a reviewer can
see two waves inside one value without reading git history.

Digest-neutrality of the comment corrections in sections 3 and 5 was verified:
`286c233a7db458c7` before and after, which is what the instrument promises and
what `test_a_comment_or_an_identity_swap_does_not_move_the_digest` exists for.

---

## 7. WHAT ELSE THE MERGE BROKE, AND WHY THE FIXES ARE NOT SILENCING

Four tests went red on the integration. Each is recorded with what it was
measuring and why the repair is legitimate rather than a value edit.

| test | why red | repair |
|---|---|---|
| `test_the_read_only_boundary_is_where_it_was_re_frozen` | the roster genuinely grew by 5 | re-freeze, section 6 |
| `test_the_write_did_not_touch_any_of_the_four_denylists` | duplicate assertion of the above | key REMOVED, section 4.3 |
| `test_the_roster_grew_by_exactly_four` | hard-coded `== 40` and `== 36` | rewritten as a DELTA |
| `test_the_admitted_analytics_pages_are_exactly_three` + 2 in that file | a fourth analytics page arrived | tripwire RAISED with argument, section 3 |

On the roster count: it asserted two absolutes that were a proxy for "36 + 4",
and held only while the wave's own base was the shipped roster. `/jobs/jam`
landing on master in parallel broke both assertions on a merge that had weakened
nothing. **A count that any unrelated wave can break is not measuring this
wave.** It now asserts the subtraction, which is invariant under other
admissions and is what the test's name always promised. The protection the
absolutes really carried -- that the helper finds all four entries rather than
silently three -- lives inside `_roster_without_this_wave()` and is untouched;
the roster's total size is pinned with its argument in the boundary invariant.
It was the **only** absolute roster-length assertion in either tree.

---

## 8. HONEST LEDGER

    allowlist, master -> merged                    37 -> 41
    of those, buying a row today                   2   (both collections, reader ships)
    of those, buying NO row today                  2   (recruiter-views, profile-key-skills)
    readers shipped                                1   (job_collections.py)
    readers WIRED to a tool                        0   (ruled unwired in two places)
    pages anyone has actually opened                0   of the four
    cross-term the union introduced                0   over 111 deduped addresses
    exemption tables engaged                       0
    digests moved                                  1   of 8

    defects found in the INCOMING work             3
      - a false "never recorded" claim, reversing a 2026-09-05 refusal
      - a trap described at length but pinned on a url LinkedIn never draws
      - a stated blocker ("values unknown") that the tree already answered
    defects found in the STANDING guard suite      2
      - the denylist baseline dict is a mirror, 0 of 8 mutations red it alone
      - the scoped gate cannot see a test that asserts an ABSENCE
    tests repaired rather than silenced            4
    guards deleted                                 0
    rulings deferred to a human                    1   (section 4.3, option a or b)

**TWO OF THE FOUR ENTRIES BUY NOTHING TODAY, and that stays on the ledger line
rather than in a footnote.** By this repository's own standard -- *"a surface
admitted and unusable is not a partial win; it is a blast radius paid for
nothing"* -- the honest accounting is that this merge admits four addresses and
can read two of them, against a reader that is itself a hypothesis about pages
nobody has opened. What the two reader-less entries buy is the removal of our own
refusal: you cannot capture a page you refuse to open.

### 8.1 My own process defects, both mine and both recorded

1. **I spawned three children WITHOUT `isolation: "worktree"`**, so they ran in
   my mid-merge tree and two of them correctly escalated that another writer was
   active in it. No damage: all three were briefed read-only against committed
   git objects, and the index and working tree were verified byte-intact
   afterwards (41 patterns, no conflict markers, status unchanged). It was luck
   that the briefs were read-only, not design.
2. **A `sed` I used to patch a scratch script ate a backslash and injected a
   literal BEL into a path** -- the same class as this repo's own recorded
   heredoc defect. Caught immediately because the script then failed loudly.
   Scratchpad only; no tracked file touched.

### 8.2 The register number

The incoming wave wrote its instrument-register section as **29**, from a
maximum of 28 at `dc5aaa6`, and said in its own text that it should be
renumbered if it collided.

**IT COLLIDED THREE TIMES, AND THE THIRD HAPPENED DURING THIS INTEGRATION.**

    written as      29   (max was 28 at the wave's base)
    collision 1     29   live-capture published it first
    collision 2     30   names-that-do-not-exist published it first
    taken           31   at 13:05, correct against master at d6b7e4b
    collision 3     31   reason-kinds landed it on master at 13:12
    PUBLISHED AS    32

I took 31 at 13:05 having seen `reason-kinds` staging its own 31 in an
uncommitted scratch file, and recorded the prediction that the guard would
catch them at their merge. **It caught me instead** -- they committed first, at
13:12, while this integration was still writing its deliverable. That is the
rule working exactly as written (the wave that publishes first keeps its
number), applied to the wave that had just invoked it against somebody else.

**FOUR WAVES HAVE NOW COMPUTED "THE NEXT INTEGER" FROM THE SAME STALE MAXIMUM
FOR THIS ONE SECTION.** The guard's own docstring says the collision exists only
in the merge and no wave's green run can see it; this is the strongest specimen
of that yet, because the two renumbers happened twenty minutes apart on one
desk. It is not an argument for a different numbering scheme in this document,
but it is the evidence anybody proposing one should start from.

All citations moved with it: three to 32.2 in `readonly.py`'s sibling documents
and the correction-findability table, plus this document's own references to
32.6 and 32.7.

### 8.3 AND MASTER MOVED UNDER THIS INTEGRATION, WHICH IS WHY IT WAS RE-MEASURED

Master was `d6b7e4b` when this merge began and `1ab1ca8` when it was ready to
land -- nine commits from the `reason-kinds` wave, arriving between 12:53 and
13:12. **The re-freeze in section 6 rests entirely on master's content, so it
was re-verified rather than assumed:**

    linkedin_server/readonly.py                    IDENTICAL d6b7e4b -> 1ab1ca8
    tests/test_readonly_boundary_invariant.py      IDENTICAL
    tests/test_analytics_creator_boundary.py       IDENTICAL

So `286c233a7db458c7` still describes the union against the new master, and the
`37 -> 41` arithmetic is unchanged. The only file the two integrations both
touched is `_audit/INSTRUMENTS.md`, and that conflict is section 8.2.

**Had any of those three files moved, the pin in this commit would have been
stale the moment it was written** -- a digest is a claim about a tree, and the
tree it was computed against stopped being master forty minutes into the work.

---

## 9. THE RATCHET I GREW, AND WHY I WROTE THIS SECTION BEFORE I TOUCHED IT

`tests/test_probe_controls_are_never_decorative.py` went red on the merge. It
is the guard behind register section 27 -- *129 controls that print FAIL and
certify anyway* -- and it fails when the detector finds a never-branched probe
control that is not already in
`scripts/probe_controls_known_decorative_baseline.json`. The merge brings four
new findings, all in the incoming wave's `scripts/_probe_analytics_list_shape.py`.

**THE RED WAS REAL AND IT WAS MINE**, in the sense that nothing on master had
these and my merge introduces them.

**WHAT I WAS ABOUT TO DO, WRITTEN DOWN BEFORE I DID ANYTHING.** I was about to
add four rows to that JSON to turn the red green -- to a file whose own
`_comment` says, in those words, that it is *"a RATCHET, not an allowlist to
grow"*. That is the shape of edit this whole day has been about, so it stopped
here and each of the four was read first.

### 9.1 What the four actually are

    _probe_analytics_list_shape.py:733  part4()      -> digit_controls   REAL
    _probe_analytics_list_shape.py:886  control()    -> expected         FALSE POSITIVE
    _probe_analytics_list_shape.py:925  break_demo() -> expected         FALSE POSITIVE
    _probe_analytics_list_shape.py:925  break_demo() -> html             FALSE POSITIVE

**THREE OF THE FOUR ARE THE DETECTOR FLAGGING A CONTROL'S INPUTS, NOT ITS
RESULT.** At both line 886 and line 925 the statement is
`html, expected = _build_control_doc()` -- a tuple unpack of the control
FIXTURE. The results are branched, and thoroughly:

* `control()` runs three controls and each one is `if <bad>: print VOID; return 1`.
  Three branches, three non-zero exits.
* `break_demo()` accumulates `overall_ok = overall_ok and not ok` across two
  induced breaks and then branches `if overall_ok:`, returning 1 either way it
  can fail.

The detector is scoped by the ENCLOSING FUNCTION's name and marker words, so
every local inside a function called `control()` is a candidate. **The ratchet
already carries this exact class** -- `_probe_add_section_menu.py / main / html`
is the same shape, and it has been in the baseline since the census. So this is
not a new discovery about the probe; it is a known imprecision in the detector,
visible in its own baseline.

**THE FOURTH IS GENUINE and is not dressed up.** `part4()` computes
`digit_controls`, prints it, and compares it to a prior wave's live numbers,
printing `MATCHES` or `DIFFERS (%d)` -- and then carries on identically either
way. That is precisely the decorative pattern section 27 exists to name. It is
NOT branched here, deliberately: `part4()` is a SHAPE REPORT over whatever
capture it is handed, and a DIFFERS against another capture's numbers is an
expected outcome, not a fault. Making it exit non-zero would manufacture
failures on correct runs, which is the opposite of the law.

### 9.2 Why the baseline, and what it costs

The guard's own failure message names the two permitted responses: *branch on
its result*, or *if it is a genuinely decorative reading that was reviewed and
accepted, add it to the baseline with a one-line reason*. Branching is wrong for
all four -- three are not results at all, and the fourth would fail on correct
input. So: baseline, 129 -> 133, reviewed.

**AND THE FILE HAS NO FIELD FOR A REASON.** All 129 existing entries are bare
`(file, function, variable, line)` tuples. The message asks for a one-line
reason that the format cannot hold, so the reasons live here and a pointer to
them was written into the file's `_comment` and `generated_from`. **A triage
table whose entries cannot carry their triage is a census wearing a ratchet's
name**, and that is worth more than the four rows.

### 9.3 What I did NOT do

* I did not delete the probe to make the finding go away. It is cited by the
  wave's audit, and `tests/test_an_asserted_name_resolves.py` would have gone
  red on the dangling reference -- trading a disclosed finding for a broken
  citation.
* I did not "fix" the detector. Three false positives in one probe is a real
  signal about `scripts/detect_unbranched_probe_controls.py`, but changing a
  detector that produced a 129-row published census is a wave, not a merge
  step. Filed at INSTRUMENTS.md 32.8.
* I did not claim the ratchet is undamaged. It grew, on my commit, by four.
