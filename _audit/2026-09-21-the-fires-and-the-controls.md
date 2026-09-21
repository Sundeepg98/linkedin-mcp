# THE FIRES AND THE CONTROLS

**CORRECTS:** `_audit/_census/network.md` -- rows `33`, `54` and `175`, all three of which read COVERED-UNFIRED and are re-priced here to COVERED-CANNOT-DELIVER from their first live firing; each cell is corrected in place and none banks. The slice's COVERED-UNFIRED moves 8 to 5 and COVERED-CANNOT-DELIVER 8 to 11, with GAP unchanged at 87.

**CORRECTS:** `_audit/2026-09-21-the-three-readers.md` -- that wave's deliverable states, correctly for its own tree, that `company_root.COUNT_PHRASES` is an unmeasured guess whose first live fire would settle it, and that a wrong phrase could cost only a missing reading. The first live fire happened here and refutes the second half: the shipped phrases match as SUFFIXES of LinkedIn's real lines and publish a number that is wrong. That document is NOT rewritten, because everything it claimed was true of what it could measure; what is corrected is the claim it carried forward, and it is corrected in `company_root.py` and in the tool docstring where a reader will meet it.

**2026-09-21. Wave register section 50.** Base `762ec23`. One browser slot,
attached to the Chrome already running on the persistent profile; no second
Chrome was started and no browser was killed. Read-only throughout:
`writes_enabled` false, nothing connected, messaged, applied, followed, posted,
saved or toggled.

Three jobs queued behind this slot. **The headline is that the third one
closed, the second one came back clean on all five paths, and the first one
banked NOTHING -- because firing the three rows measured a defect worth more
than the rows.**

---

## 0. THE SHORT VERSION

| job | outcome |
|---|---|
| Fire `N 175`, `N 33`, `N 54` | **0 of 3 banked.** All three fired cleanly and all three moved COVERED-UNFIRED to **COVERED-CANNOT-DELIVER**, each with a measured reason. `N 54` returned a clean `count_read` on 6 of 6 Pages with six distinct values -- and the number is not attributable to the Page it was read from. |
| Drive the four `control_fixture()` paths | **All five paths** (four modules, five fixtures) driven through a real engine. **All five pass, and all five were shown going red under a planted defect.** |
| Fix the people-search panel race | **Closed.** Reproduced under load (3 of 6 firings blind), fixed, re-verified under the same load: **8 of 8 clean at the full 83 controls.** The shipped bytes differ from that run by one pacing primitive, forced by a test after it -- see "which bytes were live-verified". |

**GAP is unchanged at 281.** `scripts/count_census_states.py --expect
J=57,P=55,M=82,N=87` matches before and after. What moved inside `network.md`
is COVERED-UNFIRED 8 -> 5 and COVERED-CANNOT-DELIVER 8 -> 11.

**And three of this wave's own instruments had to be repaired mid-wave**, each
after it had already produced an answer. Section 5 is that list, because it is
the most transferable thing here.

---

## 1. `N 54` IS THE ONE TO READ: A ROW THAT LOOKS PROVEN AND IS WRONG BY ONE

`linkedin_company_page_counts` was fired through the registry against six
organisation Pages. `connections_following_page` returned `count_read` on **6
of 6**, `plain_digits` every time, values **6, 11, 8, 8, 2, 6**.

Six distinct values across a 2-to-11 range is exactly the discrimination this
repository demands before banking -- the reader is plainly selecting and not
saluting, and the brief's own warning case (4-true/0-false at n=4 that read 9/2
at n=11) does not apply. **On the evidence a firing wave normally collects, this
row banks.**

It must not. The page's real line, rendered as a SHAPE with every token this
package did not itself write down replaced by `<entity>`, is:

    <entity> & n other connections follow this page        on 6 of 6 Pages

and it is the only SHAPE on any of the six carrying `follow this page` -- which
is not at all the same as being the only LINE, and the next section is about
that. The shipped phrase `connections follow this page` is a **suffix** of it.
So the match is real, the line is short, the numeral is clean -- and the digit
run nearest the phrase is `n`, which is LinkedIn's count of the connections OTHER
THAN the one it names. The answer the row asks for is `n + 1`.

### AND THEN IT GOT WORSE, WHICH IS WHY THE OFF-BY-ONE IS NOT THE HEADLINE

Counting occurrences rather than testing presence changes the finding entirely.
The shipped phrase `connections follow this page` occurs, per Page:

    7    6    5    8    2    5

**Never once.** A company Page root draws that line for every RECOMMENDED
organisation as well as for the subject -- the "people also follow" module and
its siblings -- and each occurrence names a **different organisation**.

`dom.COUNT_LINES_JS` keeps ONE best match per phrase: a match carrying a number
beats one that does not, and shortest container is the tie-break. It then
publishes that single winner with **no record that anything competed**.

So `connections_following_page` is not merely one short. **It cannot be
attributed to the organisation whose Page was opened.**

**THE NARROWER CLAIM IS THE ONE THAT HOLDS, AND IT IS WORTH SEPARATING.** A
crude cross-check found the published value among the candidates on four Pages
and not among them on two. **That second half is NOT evidence** and is not
relied on here: the cross-check flattens the page into one string, so it cannot
reproduce the adjacency rule `numeralNear` uses when a number and its phrase sit
in sibling elements, and the two runs derive their Page list live, so the sets
may not be identical. Either explains the two misses without any misattribution.

What does hold needs no cross-check at all: **2 to 8 candidates exist, one wins
on container length, and nothing in the payload says the others were there.**
That is enough to make the number unattributable, and it is measured directly
from the occurrence counts rather than inferred from a comparison.

**AND THE MODULE'S OWN GUARD CANNOT SEE IT.** `company_root._verdict_for` ships
a `disagreement` state for exactly this hazard, and it is blind here: it fires
when two different PHRASE POSITIONS of one kind carry different numbers, and
this collapse is between occurrences of the **same** phrase, inside the page,
below the guard. A disagreement that resolves before Python is reached is not a
disagreement anything can report.

### The two rows have DIFFERENT defects, and only one is an off-by-one

`connections work here` occurs **exactly once** on each of the two Pages that
draw it. So `N 33`'s reading IS attributable to the subject organisation, and
its only defect is the suffix off-by-one: published 3, true 4, on both.

`connections follow this page` occurs 2 to 8 times. `N 54`'s reading is
attributable to nothing.

### What this refutes, in the module's own words

`company_root.COUNT_PHRASES` said, and the tool docstring repeated:

> A wrong phrase costs a missing reading, never a wrong number and never a name.

The first half holds. **The second half is false**, and false in the worst
direction: a phrase that is a suffix of a longer construction produces a wrong
number, consistently, plausibly, and with a clean `plain_digits` shape beside
it. Both sentences are corrected in place in this commit. A claim a measurement
refutes may not stay in shipped source because it happened to be load-bearing
prose.

### `N 33`, the same defect with a messier denominator

`connections_at_organisation`: `count_read` on 2 of 6, `phrase_not_drawn` on 4.
The two that read both published **3**; the line is
`<entity> & n other connections work here`, so both pages say four.

The four that did not read are **not one thing**, and the reader is right about
three of them. Presence-testing every shipped phrase against each page's own
normalised text:

| shipped phrase | present on |
|---|---|
| `connections work here` | 2 of 6 |
| `connection works here` | 0 of 6 |
| `connections work at this company` | 0 of 6 |
| `connections follow this page` | 6 of 6 |
| `connection follows this page` | 0 of 6 |
| `connections follow this company` | 0 of 6 |

Three Pages carry no at-organisation line at all -- `phrase_not_drawn` is the
correct answer there. One carries `<entity> <entity> who work here`, which no
shipped phrase reaches. Two further Pages draw `<entity> works here` -- a single
connection, no count, and note that LinkedIn's singular carries **no
`connection` token at all**, so the shipped `connection works here` was never
going to meet it.

### Why the phrase list was NOT widened

Widening it is the move that banks two rows this afternoon and is wrong twice
over:

1. It would convert a genuine absence into a false positive on the three Pages
   that draw no such line.
2. The measured line **contains** the shipped phrase, so adding it breaks
   `company_root`'s own invariant that *no phrase may contain another* -- whose
   stated reason is that two phrases matching one line produce two readings of
   one number, "which would read as corroboration and is one observation."

The repair is a replacement plus a rule about the `other` qualifier; it changes
what `COUNT_KINDS` means, and it is owed its own wave. It is named here rather
than half-done under a freeze.

---

## 2. `N 175`: A VERDICT WHOSE POSITIVE BRANCH CANNOT FIRE

`linkedin_group_page` fired against three groups this account belongs to:

| fire | verdict | same group | anchors | feed | member | other | refused |
|---|---|---|---|---|---|---|---|
| 0 | `ambiguous` | True | 86 | 0 | 16 | 57 | 0 |
| 1 | `ambiguous` | True | 35 | 0 | 3 | 26 | 0 |
| 2 | `ambiguous` | True | 47 | 0 | 9 | 28 | 0 |

The module documents `ambiguous` as its honest branch, and the wording is
honest. But three of three, on groups the account is a member of, over pages
drawing 86, 35 and 47 anchors, is not the shape of an occasional ambiguity.

`feed_drawn` is gated on `anchors.ROUTE_CLASSES`'s `feed_update`, the
fixed-segment rule over `/feed/update/`. A route census of the three captures --
**resolving absolute hrefs to their paths**, which the first pass of that
instrument failed to do (section 5) -- finds:

    /feed/            6   across all three pages (the nav home link, twice each)
    /feed/update/     0

A group feed's post permalinks do not wear that route. So `ambiguous` here is
not an ambiguity: **a verdict whose positive case cannot occur is the same
defect as a check that cannot fail, seen from the other side**, and this
repository has spent two days counting the first.

**What the firing does prove, and it is not nothing:** the address is navigable
by a built numeric url; the landing is reduced to a digit run and compared as
one; the shipped classifier ran on a real group feed; and no name, slug,
heading, post or author crossed the boundary on any of the three.

Closing the row needs `anchors.ROUTE_TABLE` to learn whatever shape a group post
permalink wears -- an edit to a script three other readers run, and still not
this row's to make.

---

## 3. THE FOUR CONTROL PATHS: FIVE OF THEM, AND ALL FIVE WORK

`control_fixture()` is declared in `anchors.py`, `search_results.py`,
`collections_page.py` and `company_root.py`, and had **never been driven through
any JS engine**. Node has no `DOMParser`; every test that named a fixture
asserted on the markup **string**. So the line that makes a fixture a control --
`new DOMParser().parseFromString(html, "text/html")` inside the shipped script --
was the one line nothing had executed.

That is sharper than a check that cannot fail. **A check that cannot fail has at
least run.**

### The precise shape of the gap, because "nothing ran" would overstate it

`search_results` and `company_root` DO have tests that execute shipped JS under
V8 -- and those tests name their own seam, in the file, in capitals:

> THIS IS THE SEAM AND IT IS NAMED: the shipped script gets its anchors from a
> DOM, and node has no DOM, so the test does that half. What is therefore NOT
> covered below is `querySelectorAll` and `getAttribute`.

So the decision functions were driven; the **DOM half was not, and was declared
not to be.** The existing tests extract hrefs with a *Python* regex and feed the
strings to a brace-matched pure function. `company_root`'s V8 tests drive
`control_tree()`, the synthetic node structure -- never `control_fixture()`, the
markup. `anchors` and `collections_page` drive nothing through any engine at
all: grepping either test file for `evaluate|subprocess|node|V8` returns zero.

**The uncovered half is exactly the half a fixture exists for.** A fixture is a
string of markup; the only thing that makes it a control rather than a constant
is a parser reading it. This wave supplied the parser.

One thing that fell out: `tests/test_collections_page.py`'s docstring claims
*"the fixture is run through the real in-page matcher during a live read --
measured 2026-09-19: 5 matched, 1 unmatched"*. The test does not execute that.
The live run reports **5 matched, 1 unmatched**. The claim was true and
unverified, and is now verified.

There are **five** paths, not four: `search_results` ships two fixtures, one per
reader. Driven in one attached tab, navigating nowhere:

| path | script | result | denominators |
|---|---|---|---|
| `anchors.control_fixture` | `ANCHOR_CLASSIFY_JS` | **PASS 13/13** | 13 anchors, 0 refused |
| `search_results.control_fixture` | `SEARCH_RESULTS_JS` | **PASS 14/14** | 14 anchors, 1 query, 0 refused |
| `search_results.filter_control_fixture` | `FILTER_PANEL_JS` | **PASS 14/14** | 17 controls, 14 matched, 1 empty label |
| `collections_page.control_fixture` | `COLLECTION_GROUPINGS_JS` | **PASS 5/5** (see note) | 6 headings, 1 unmatched |
| `company_root.control_fixture` | `COUNT_LINES_JS` | **PASS 2/2** | 9 elements, **2 hidden subtrees skipped** |

"All four work" was worth measuring precisely because it is as informative as
"two are broken" -- but only if the driver could have said otherwise. So each
path carries a planted defect, and `--plant` runs those instead:

| path | planted defect | result |
|---|---|---|
| `anchors` | every href removed | **RED 0/13** (13 fall to `no_href`) |
| `search_results` routes | every href removed | **RED 0/14** |
| `search_results` filters | controls demoted to spans | **RED 1/14**, controls 17 -> 1 |
| `collections_page` | headings demoted to spans | **RED 0/5**, headings 6 -> 0 |
| `company_root` | screen-reader class renamed | **RED 1/2**, and see below |

**The company_root plant is the one worth the browser slot.** It renames
`visually-hidden` and changes nothing else. The reading moves from **11 to 41**
and `hidden_subtrees_skipped` falls **2 to 1**. That is the accessible-copy
exclusion -- the property the whole module is built around, and the place a
third party's name most likely sits on that surface -- demonstrated
load-bearing in a real DOM for the first time, rather than in a synthetic node
list.

**One finding of absence, and it is closed in this commit.** Of the four
modules, `collections_page` was the only one shipping **no written expectation**
beside its fixture. Its existing test asserts that the fixture still *contains*
the right strings -- a claim about the INPUT -- so nothing said what the output
had to be, and once the fixture was finally driven there was nothing for the
result to disagree with.

**THE NOTE ON THE TABLE ROW ABOVE, because a receipt that does not reproduce is
the thing this wave spent its day objecting to.** That run scored `5/5` against
the expectation the probe DERIVED, before the constant existed. Re-running the
same command at this commit scores **`6/6`** -- five groupings plus the decoy --
because the probe now reads the shipped constant and the shipped constant
predicts one more thing. Same fixture, same engine, same result; one more
prediction made about it. The `5` is left in the table as the reading that was
actually taken, and this paragraph is why the number a reader gets back will be
larger.

`collections_page.CONTROL_EXPECTATION` now ships, with `unmatched: 1` in it,
and that entry is the discriminating half: five matches is also the shape a
matcher that salutes every heading makes, so the DECOY is predicted rather than
merely present. Two tests were added, one of them the partner red showing a
saluting matcher satisfying a decoyless table and failing the shipped one. The
probe reads the shipped constant instead of deriving its own -- **a derived
expectation is a prediction the probe makes about itself; a shipped one is a
prediction the module makes**, and only the second can be contradicted by a
future edit to the module.

Instrument: `scripts/_probe_control_paths_live.py`. Re-runnable, attach-only,
navigates nowhere, prints its own git head and the sha256 of all five modules it
exercises.

---

## 4. THE PANEL RACE: REPRODUCED UNDER LOAD, FIXED, RE-VERIFIED UNDER LOAD

### Reproduction

The full suite was run at `-n auto --dist loadfile` to pin the box, and the tool
fired eight times against the pre-fix tree:

| fire | controls_seen | filters offered | terms nonzero |
|---|---|---|---|
| 0, 1 | (attach timed out -- see section 5) | | |
| 2 | 62 | 3 | 2 |
| 3, 4, 5 | **45** | **0** | **0** |
| 6 | 73 | 3 | 2 |
| 7 | 62 | 3 | 2 |

**Three of six completed firings read every filter as zero.** The correlation is
exact both ways and matches the prior wave's single observation: 45 controls ->
no filter, 62 or 73 -> three.

### Why load makes it worse rather than better

`BROWSER.goto` navigates on `domcontentloaded`, then waits for `networkidle`
with a flat fallback, and its own docstring says that settle is **not a
readiness check**. On a pinned box the renderer is starved, fewer requests are
in flight, and a 500 ms network lull arrives **earlier** -- so the settle
SHORTENS against a panel that has drawn less. That is why both quiet runs looked
deterministic: the defect hides on exactly the machine a fix would naturally be
verified on.

### The fix

`search_results.read_filters_when_settled` re-reads until `controls_seen` has
been unchanged for three consecutive polls (350 ms apart, 20 polls maximum),
and `linkedin_people_search_shape` calls it instead of `read_filters`.

Three properties made this the right shape rather than a `wait_for_selector`:

- **No new selector and no new vocabulary.** A selector here would be a guess at
  LinkedIn's class names on a surface this package has barely met, and a wrong
  guess fails quietly -- it times out and reads the half-drawn page anyway,
  which is today's behaviour with extra steps. The wait uses the shipped
  reader's own number, so the instrument measuring readiness is the instrument
  that takes the reading.
- **No pinned constant moves.** `wait_for_timeout` and the polling re-enter the
  same `page.evaluate` call site inside `dom.read_search_filters`, so the
  `# readonly-ok` waiver budget (pinned at 22) and the declared-script count
  (also 22, independently) are both untouched.
- **A zero is never a plateau.** Without that guard the stability rule settles
  instantly on the blind reading it exists to prevent.

### Verification, under the same load

| fire | controls_seen | offered | nonzero | polls | settled |
|---|---|---|---|---|---|
| 0-7 (all eight) | **83** | 3 | 2 | 5 or 3 | **True** |

**8 of 8, zero blind, zero partial, every one at 83** -- the full panel count the
prior wave had only ever seen as a denominator. The suite was still running at
82% throughout.

### WHICH BYTES WERE LIVE-VERIFIED, STATED BECAUSE THEY ARE NOT THE SHIPPED ONES

**The 8-of-8 run above used `page.wait_for_timeout` to pace its polling. The
shipped code uses `asyncio.sleep`.** The change came after that run, and a test
forced it: `tests/test_the_search_shaper_emits_no_name.py` drives the tool
against a hostile page implementing `evaluate` **and nothing else**, which is
the narrowness every shipped reader in this package already keeps. Calling
`page.wait_for_timeout` raised `AttributeError` there, the tool swallowed it
into `_error`, and three name-safety proofs became `KeyError: 'denominators'`.
So a reader that quietly widened its demands on the page disarmed the proofs
that it publishes no name.

What differs between the run and the shipped bytes is the pacing primitive and
nothing else: same loop, same `PANEL_STABLE_READS`, `PANEL_POLL_MS` and
`PANEL_MAX_POLLS`, same stop condition, same payload. No selector, count or
verdict is touched.

**THE RE-RUN ON THE SHIPPED BYTES WAS ATTEMPTED AND IS BLOCKED.** Six firings
at 09:32 returned `browser_unavailable` on a 180 s attach budget while the
suite loaded the box; the standing lead ruling is that an attach that will not
come up under contention is contention until re-measured serially. The serial
re-measure could not follow: **port 9224 stopped answering.** 52 Chrome
processes remain and nothing listens on the DevTools port, so the automation
instance is gone while a browser survives. This wave issued no kill of any
kind at any point, and deliberately did not start Chrome on the persistent
profile to recover -- that is the one action whose failure mode (a downgraded
profile and a lost signed-in session) only the operator can undo.

So the honest scorecard for the race is: **the defect is measured live, the fix
is measured live in the form that was current at 08:0x, and the shipped form is
proven by six offline tests plus two planted defects rather than by a browser.**

The same caveat, smaller, applies to section 3: the five control paths were
driven live BEFORE the probe gained its teardown and was rewired to read
`collections_page.CONTROL_EXPECTATION`. That refactor is verified offline --
signature, plant-effectiveness, expectation wiring and `compare()` scoring both
ways -- and not re-run in a browser, for the same reason.

### What is deliberately still not claimed

`panel_wait.settled` means the count stopped moving. **It does not mean the
panel is complete**: nothing in this process knows how many controls the page
intends to draw, so a panel wedged low settles exactly like a finished one. The
trajectory (`controls_first`, `controls_last`, `polls`, `settled`) travels in
the payload so a caller can tell them apart. And the tool's docstring bullet
claiming it "has never been run against" a live page is corrected -- it has now
been run fourteen times.

**A separate honest result:** the best live firing offers **3** of the 14 shipped
filter terms. Whether the other eleven live behind the "All filters" button, are
worded differently, or are not offered to this account is unmeasured, and
nothing is pressed here to find out. That is now stated in `not_claimed` rather
than left to be inferred from a small number.

### Tests, shown failing

Six tests in `tests/test_search_results.py`, driving the shipped coroutine
against a fake page whose control count rises on a schedule the test sets -- the
one thing a live firing cannot give you, a reproducible trajectory. Two defects
were planted and the flip recorded:

| test | plant 1: `STABLE_READS = 1` | plant 2: wait removed |
|---|---|---|
| returns the settled reading | **RED** | **RED** |
| unwaited reader returns the blind page | green (by design) | green (by design) |
| a page stuck at zero never settles | green | **RED** |
| a wedged panel settles but shows it never grew | green | **RED** |
| the wait is bounded | **RED** | **RED** |

The wedged-panel test passed under **both** plants on its first draft -- a
wedged panel and a removed wait produce the same first/last pair. It was
strengthened with an assertion on `polls` and now flips. **That was found by
planting, not by reading it back**, which is the only reason it was found at
all.

---

## 5. THE INSTRUMENTS THIS WAVE HAD TO REPAIR MID-WAVE

Three of this wave's own instruments produced an answer and then turned out to
be wrong. All three are the same class -- **a filter reasoned about rather than
tested against the thing it must stop** -- and all three were caught only
because something downstream disagreed.

**(1) A frequency filter cannot separate a name from boilerplate on this
surface.** The wording probe published any text run appearing on three or more
different Pages, on the argument that LinkedIn's boilerplate repeats and a
person's name does not. It published a real connection's given name **on all
six Pages** -- because the line is *"<a connection> and N others follow this
page"*, LinkedIn names one of the account's own connections, and that person
follows many Pages. The name repeated for exactly the reason the boilerplate
does. **No threshold fixes this.** Replaced with a closed-vocabulary allowlist:
a run is published only if every token is one this package wrote down, and the
withheld count is published so the filter cannot hide how much it drops.

**(2) A route census rendered the entity segment it promised never to render.**
The group-page probe took the first two path segments. `/in/<slug>/` is two
segments, so it printed a member's vanity slug -- for the account's own profile
and three third parties -- while its docstring said the entity segment "is never
rendered". Fixed with an allowlist on segment two; then the **same class was
found a third time** on single-segment routes, and segment one was allowlisted
as well. A `leaks()` self-check now runs over every rendered route **before the
result is returned**, and stops the probe rather than tidying.

**(3) The same probe's headline was unsound for a second, independent reason.**
It bucketed every absolute href as `(external-or-absolute)` -- 108, 58 and 70 of
them -- and then concluded from the remainder that no anchor wears a `/feed`
route. An absolute `https://www.linkedin.com/feed/update/...` would have sat
inside the bucket it never looked in. **The measurement could not have refuted
its own conclusion.** Absolute hrefs are now resolved to their paths first, and
the re-derived `/in/<entity>/` counts (3 and 9) now agree with the shipped
classifier's `member_profile_anchors` (3 and 9), which is the cross-check that
says the resolver is right.

**And the suite caught a fourth.** `tests/test_page_text_is_never_printed.py`
failed the wording probe for printing page text, with its own red saying *"do
NOT add it here to clear the red; emit a count, a relation or a marker."* It is
right: a vocabulary-clean run is still something LinkedIn wrote. The runs now go
to the gitignored `_state/` and stdout gets counts. **The guard was not
widened.**

The transferable lesson is not "be careful with names". It is that **every one
of these filters was defended by an argument, and the argument was the
problem.** A filter that decides what to REMOVE has to anticipate what it is
removing; a filter that decides what to KEEP does not. All three repairs are the
same move in the end -- ship a vocabulary in and let nothing else out, which is
what the readers in this package already do.

---

## 6. EVIDENCE, AND WHERE IT IS RE-DERIVABLE FROM

Nine rows were once found resting on gitignored scratch paths. Every instrument
here is a tracked, re-runnable script that **derives its own inputs live**, so
no identifier had to be written down anywhere to make the evidence reachable.

| instrument | what it re-derives | inputs |
|---|---|---|
| `scripts/_probe_control_paths_live.py` | section 3, both modes | none; navigates nowhere |
| `scripts/_probe_the_three_fires.py` | sections 1 and 2, the firings | group and organisation ids, live, from `linkedin_group_memberships` and `linkedin_followed_companies` |
| `scripts/_probe_company_root_wording.py` | section 1, the wording | organisation ids, live; `--from-raw` re-derives offline at zero page loads |
| `scripts/_probe_group_feed_permalinks.py` | section 2, the route census | group ids, live |
| `scripts/_probe_people_search_panel_race.py` | section 4, both runs | none |
| `scripts/count_census_states.py --expect J=57,P=55,M=82,N=87` | the census control | tracked files |

Every probe prints its own git head and the sha256 of each module it exercises.
Raw captures and the identifiers are written under the gitignored `_state/` and
appear in no tracked file: **a company Page and a group are both lists of
people, and an organisation slug is an employer name.**

---

## 7. WHAT THE NEXT WAVE IS OWED

1. **The `COUNT_PHRASES` repair, which is TWO repairs and not one.**
   `N 33` needs the suffix fixed: replace the phrase with the measured line and
   decide what the `other` qualifier means for `COUNT_KINDS`. `N 54` needs
   something harder -- a way to tell the SUBJECT Page's line from the 1 to 7
   recommended-organisation lines beside it, which is a scoping question about
   the container the line sits in, not a vocabulary question at all. Either
   repair alone leaves the other row wrong.
2. **`dom.COUNT_LINES_JS` should publish HOW MANY matched per phrase**, not
   only the winner. One extra integer makes the whole class visible, and
   `company_root._verdict_for` could then refuse a phrase that matched more
   than once instead of being structurally unable to see it. This is the
   cheapest of everything listed here and it is what would have caught the
   defect on the first fire.
3. **A group post permalink's real route**, which unblocks `N 175` and is an
   edit to `anchors.ROUTE_TABLE` that three other readers run.
4. **The eleven unoffered filter terms.** Three of fourteen render without a
   press; whether the rest are behind "All filters", worded differently, or not
   offered to this account is open, and opening that panel is a press this
   surface's admitting ruling does not sanction.
