# The open queue, 2026-09-21 at master `9dbaad2`

**A DATED SNAPSHOT, NOT A CLAIM ABOUT THE PRESENT.** Everything below was true
when written and some of it is designed to stop being true. Re-derive any count
through `scripts/count_census_states.py` and any address through
`readonly.is_read_url` before acting on it — this repository has found seven
claims about a moving boundary going stale in two days, and this document is
exactly the shape that does it.

It exists because the items below lived only in an orchestration session's
context. A successor reading `_audit/INDEX.md` would find every wave's report
and none of what is still owed.

## 1. Four decisions nobody has made, in the order I would take them

These are the constraint. The engineering remainder is small, enumerated and in
flight; these are not.

**D3 — does a reasoned allowlist refusal count as "written" for
COVERED-CANNOT-DELIVER?** `_audit/2026-09-19-the-read-rows.md` calls it *"the
single highest-yield decision left in this row set"*. It banks `N 99`,
`N 172`, `N 177`, `N 178` and `M C83` together and settles every future
boundary-blocked row. **A search of all 199 documents finds it named in exactly
one — the one that filed it.** It was correctly identified as the highest-yield
item available and was invisible to everyone, including me, until a triage wave
went looking.

**Is incidental capture a ruling?** The census holds two incompatible
practices. `R2` files 15 rows against forbidden substrings it openly admits
catch them incidentally; `P E6` and `N 114` say in prose that it does not
count. A measurement makes this implementable rather than a matter of taste:
`/company/<slug>/people/` and `/school/<slug>/people/` are refused by an
**anchored pattern written for them**, with zero forbidden substrings — so
"somebody ruled this address" and "a rule for something else caught it" are
mechanically distinguishable. **Recommendation: incidental capture is not a
ruling. It REDUCES reported coverage**, which is why it should be ruled rather
than assumed.

**File upload.** The ban on `set_input_files` rests on its own words — *"the
operator has never been asked about it"* — and the capability census files it as
*"ONE OPERATOR ANSWER FROM OPENING … it needs an answer"*. The verb was
sanctioned at one call site on 2026-09-04 and **no answer is recorded anywhere
in the corpus**. Nothing is reachable (`writes_enabled()` is False, upload is
absent from `PERFORMABLE`), so this is not an incident — but the code and the
stated reason disagree, and only one word fixes that. See
`_audit/2026-09-20-the-sanctioned-seventh.md`.

**A pre-push hook refusing any ref but `master`.** Eight local-only branches
carry the three purged identity blobs, kept deliberately because
`integrate-1821` is the only ref under which 22 cited SHAs resolve
(`_audit/2026-09-20-the-six-unremapped.md`: *"KEEP, do not delete, do not
push"*). Nothing published carries them — every remote branch is an ancestor of
master and master sweeps clean. **The protection is currently a sentence in an
audit file**, and `git push --all` or `--mirror` would republish. A force-push
does not undo that: retained objects stay resolvable by SHA, and only
delete-and-recreate was measured to remove them, which cost this account a
sibling repo's entire PR history once.

Five further decisions are enumerated in
`_audit/2026-09-21-the-read-triage.md` section 5, and one in
`_audit/2026-09-21-the-jobs-direction.md` section 8 (whether `jobs.md` should
grow an `R/W` column — the wave argues it should not).

## 2. Build work that is named, measured and NOT yet commissioned

**`J 40`, the network-proximity extractor.** The highest-value single row found
so far, and the reason is external: the operator's separate job-alert-email
channel documents this field as *"the payload is worth having for one reason
above all … no scraper and no job-board API can produce that field. Rank on
it."* This server discards it — as collateral of a parser defending three
adjacent fields, **not by any ruling**. Both status vocabularies were read in
full and neither names alum, alumni, connection or proximity.

Its safety answer is measured and counterintuitive, and must survive into
whatever gets built: on the search card the insight renders **twice and the
copies differ** — the `aria-hidden="true"` visible span is name-free, the
`visually-hidden` screen-reader span **carries the employer name**. The
job-detail page has **no** name-free rendering, only `Company alumni from
<ORG>`. Safe shape: `{count, relation-index}` through `coerce.as_int`, never
the line; on detail, a boolean at best.

**Wire `CARD_HIDDEN_SELECTOR` into the filter-panel reader.** `dom.py` defines
`CARD_HIDDEN_SELECTOR` and `NOTIFICATION_HIDDEN_SELECTOR` for exactly the
hidden-span hazard and **they are not wired to `FILTER_PANEL_JS`**, which
builds its label as `aria-label || textContent` — and `textContent` is
unconditional. This is a **correctness** hazard and not a disclosure one:
verified that both scripts return integers only, so no page string crosses the
boundary; hidden text can only inflate a count by matching shipped vocabulary.
Deferred while a wave was firing against that surface.

**`N 134` and `P O3` need a press.** The disclosing press was RULED permitted,
`press.disclose` exists, the disclosure witness its first firing was called
blind for is now built — and **`press.disclose` has zero callers among the 47
shipped tools.** A sanctioned, built mechanism nothing invokes.

## 3. Residues carried deliberately

Recorded rather than silently held, each with its reason in the register:

- **2 lopsided correction edges and 15 reasons wrapping past a line**, printed
  by the index on every regeneration (register 45.11).
- **52 coercion sites unswept**, of which 42 are `writes.py` gates left alone
  deliberately: a gate that raises on a malformed page is failing closed, and an
  uncertified edit to a send gate is worse than the leak it closes. Measured:
  all 46 `int`/`float` calls there sit outside any `try` and would propagate,
  but they sit behind `writes_enabled()` (False) and a grant the offline harness
  could not obtain. **Latent, not live** — and "no leak" and "a leak nothing can
  currently reach" are different claims.
- **Three rows unrouted** (`P L2b`, `N 61`, `N 95`), which makes one triage
  script refuse to print. No assignment was invented to make it green.

## 4. What the shape of the campaign now is

Of **285 GAP rows**, **182 are write-direction** — capabilities this read-only
server rules out by design. That is a ceiling, not a backlog. Of the reachable
remainder, a triage of 59 read rows found **19 buildable**: 14 needing only a
browser slot, 3 needing a reader, 2 needing a press.

**The engineering remainder is small and enumerated. The decisions in section 1
are the constraint.** That is the finding, and it took refuting the opposite
hypothesis to reach it: I expected the campaign to be gated everywhere, and
network was not — because sixteen rows sat blocked on a `/search/results/`
pattern that had already been admitted, with its shaper and its tool, by a wave
that never went back to re-price what it unblocked.

---

## 5. Addendum, 2026-09-21 07:20 — what has moved since the sections above

**This corrects the sections above; it does not rewrite them.** The snapshot
stays as written, because a count is evidence of what was true when it was
taken. It lives in this file rather than a new one so that a reader arriving at
a stale claim above can find its corrector — a corrector names what it corrects,
and the corrected document cannot name its corrector unless somebody puts it
here.

**`J 40` IS COMMISSIONED.** Section 2 files it under build work *"named,
measured and NOT yet commissioned"*; that stopped being true at 07:20. Wave
`proximity-field` owns it in an isolated worktree, working offline against the
two committed fixtures, and will report to
`_audit/2026-09-21-the-proximity-field.md`. It was briefed to check `J 57` as
well, which `_audit/2026-09-21-the-jobs-direction.md` records as blocked behind
it.

Four things were verified before commissioning rather than inherited from the
row, because a row's reason is a reading with a timestamp:

- both hydrated fixtures carry the needle and **both un-hydrated twins read 0**,
  so the negative control is already committed and no browser slot is needed;
- the search card's two copies differ exactly as recorded — the
  `aria-hidden="true"` span is name-free, the `visually-hidden` span carries the
  employer name;
- `coerce.as_int` exists, so the wave has a coercion that cannot quote its input
  back out through an exception;
- the parsers live in `shape.py`, which no live wave owns, so the field can ride
  along in readers that already exist and **no new MCP tool and no edit to
  `server.py` is required.**

**The two `22`s in `tests/test_readonly.py` are NOT a coincidence.** A survey
filed them as *"different metric, coincidentally same number"* and I restated
that before checking it. Measured: they are the same 22 `page.evaluate(` call
sites in `dom.py`, counted twice — every `# readonly-ok` sits on one of those
calls and there are no evaluate call sites outside the module. Both sites now
say so, and say why a line-number cross-check reads 12 of 22 rather than 22:
the waiver is counted where the comment is, the call site where the argument
is, one line below whenever the call wraps. No check was added — asserting the
two counts equal would convert a deliberate independence into a coupling.

**The exact-value identity gate was silent on its clean path.** It returned 0
with no output, so *examined every staged file* and *examined nothing* printed
identically — and that second case is reachable: this gate was run and recorded
as passing four times in one session **after** the commits had already been
made, reading zero bytes each time. Four clean receipts for four unexamined
commits. It now names its denominator on a pass and prints `THIS IS NOT A PASS`
on an empty index. Refusal semantics deliberately unchanged: a shipped guard is
not given a new way to block work without a ruling, so it became loud instead.

**Nothing in section 1 has moved. Every decision there is still open**, and the
sentence that section opens with still holds: those are the constraint, not the
engineering.

### 5.1 Correction to section 1, and to the paragraph above it, 07:45

**The pre-push decision is no longer open: it is built.** And section 1's
factual premise for it was wrong, which is why it gets its own heading rather
than a quiet edit.

Section 1 states *"every remote branch is an ancestor of master and master
sweeps clean."* The first half is **false**, measured against the remote refs
rather than the local branches that share their names:

- `origin` serves **13 refs besides master**.
- **`origin/ci-offload` is NOT an ancestor of master.** It is an ORPHAN commit
  — `58a7c13`, no parent, *"integrated tree for CI verification, no ancestry"*,
  2026-09-19 — carrying **498 blobs master does not have**, on a PUBLIC repo.
- It was swept: **PASS, 0 hits across 498 blobs against all 218 spellings.** So
  the conclusion section 1 drew survives; the reason it gave for it does not.

**The threat the section named is real, and now measured exactly rather than
asserted.** `git push --all` in this checkout offers **45 refs**. All ten
non-ancestor local branches were swept, not sampled:

    9 of 10  FAIL: 3 hit(s) in 1 distinct path(s)   <- incl. integrate-1821
    1 of 10  PASS: 0 hits across 498 blobs          <- ci-offload

Those 9 carry the blobs `scripts/purge_denied_term.py` removed from the history
master publishes. **The single branch that sweeps clean is also the only one
that is published** — which is luck rather than design, and was the whole
argument for building the gate rather than trusting the pattern to hold.

`scripts/pre_push_ref_gate.py` now refuses any REMOTE ref but
`refs/heads/master`, deletes included, installed by `install_git_hooks.py` and
overridable for one command with `LINKEDIN_MCP_ALLOW_ANY_REF=1`. It refuses on
the remote ref deliberately, so `git push origin master:anything` is caught
where a local-ref check would wave it through — a mutation run proved that
distinction was NOT yet tested, because the first version of the test used
`HEAD` as the local ref and `HEAD` is not allowlisted either, so the test
passed for the wrong reason.

**Two things this does NOT do**, stated so nobody reads more into it. It does
not sweep a ref's CONTENT — a ref it allows has been named, not cleared. And it
is per-checkout: `.git/hooks` is untracked, so a fresh clone has no protection
until `install_git_hooks.py` is run. The repo-wide half is
`tests/test_pre_push_ref_gate.py`, which runs on three CI platforms because the
gate's decision is a pure function of git's stdin and needs no wordlist.

### 5.2 Two items added to section 2, from survey children, 08:25

**`collections_page.py` has no written `CONTROL_EXPECTATION`** — the one gap of
four modules; `anchors`, `search_results` and `company_root` each have one.
Found by the `control-expect` survey. Small, uncontested, and deliberately NOT
bolted onto a wave that is already firing: it wants its own slot.

**The `DOMParser` branch of all five `dom.*_JS` scripts is uncertified by
`tests/`.** All 8 test call sites of a `control_fixture()` are string-only
substring asserts, or a "seam" where Python regex lifts hrefs and labels out of
the fixture and feeds them to a pure JS function under node — and **node has no
DOM**, so `DOMParser`/`querySelectorAll` is never reached. All five scripts
HAVE that branch. The only thing that drives it is
`scripts/_probe_control_paths_live.py`, which was **untracked**; it has been run
clean (5 PASS) and planted (5 correctly FAIL), and the lead has ruled it gets
committed. Until that lands, "the html branch is certified" has no artifact.

Its sharpest measurement is worth carrying forward on its own: renaming ONLY
the `visually-hidden` class flips `connections_at_organisation` from **11 to 41**
in a real browser, matching the V8 synthetic-tree prediction exactly. That is
the accessible-copy hazard demonstrated live rather than argued — the
screen-reader copy inflating a count by nearly 4x — on the same surface `J 40`
reads.
### 5.3 The `All filters` block may not need the ruling at all, 08:30

**A twice-reported block is a backlog item, not an answer.** Section 1 files the
`All filters` press as an operator decision worth 12 rows, and that is correct
as far as it goes: opening the panel is a press, and condition 5 of the search
admitting ruling is that nothing is fired from that surface. **That is a
refusal somebody actually ruled, so it is not mine to void.**

**But the ruling bars FIRING, not READING, and the two have been conflated.**
`_audit/2026-09-21-the-fourteen-fired.md` establishes it: the same wave read
**83 drawn controls** off that surface under that ruling, and banked `N 83`
(Locations) from it. Reading is plainly permitted. What it found was that the
blocked filters *"are not among the 83 drawn"* — and **that is a statement about
the DOM**, because the measurement was a containment test over rendered
controls.

**THE QUESTION NOBODY HAS ASKED: does the filter vocabulary ship in an embedded
PAYLOAD even though the DOM does not render it?** LinkedIn hydrates these pages
from JSON, and a vocabulary present in the payload would be readable with no
press, under the existing ruling, changing nothing about condition 5. If the
answer is yes, the operator decision in section 1 **dissolves** rather than
waiting — 12 rows reachable by a read. If no, section 1's decision is confirmed
as the only route, which is worth knowing at the same cost.

**Why this cannot be settled offline, measured:** there is **no committed
capture of the people-search surface at all**. `tests/fixtures/` holds
`jobs_search.html`, `jobs_search_hydrated.html` and `jobs_search_salary.html`
and nothing for people. So this needs one live READ of an already-admitted
address, with the panel left shut — a browser slot, not a ruling.

**Evidence class, stated honestly:** no document in the corpus names a
payload-level filter enumeration for this surface. That is a search over what
people WROTE; this repository has already established that you cannot grep for
what nobody considered, so "unasked" is the best available reading and not a
proof.

**Status: NAMED AND MEASURED, NOT COMMISSIONED.** The browser slot is held by
the wave firing that same surface, and a second browser builder on one
signed-in profile is the thing this repo does not do. Take it when the slot
frees.

### 5.4b CORRECTION TO 5.4a, WHICH WAS ITSELF INCOMPLETE, 13:10

**5.4a says the question was re-derived three times. It is four, and 5.4a is
the fourth.** It found ONE of the two prior rulings and missed the other — the
one that says `RULED:` in a file named `...-ruled.md`:

- **`EXCLUDED-RULED-ADMISSION`** (~2026-09-03), the origin, which 5.4a quotes.
- **`INCIDENTAL-CAPTURE-IS-NOT-A-RULING`** (2026-09-19,
  `_audit/2026-09-19-two-census-conventions-ruled.md`): *"RULED: NO. THEY STAY
  GAP, WITH THE BLOCKER NAMED PRECISELY."* With a three-way discriminator table
  already written out.

**A correction about findability, itself incomplete for want of findability.**
The defect convicting itself, which is the most honest evidence available that
it is real and not a story about one careless afternoon.

**AND 5.4 SIMPLIFIED THE RULE IT RESTATED.** It treats the question as binary —
aimed or incidental. The origin ruling is a **FOUR-GROUND TEST**: a row is
`EXCLUDED-RULED` only on a forbidden-substring entry, a
`writes.PERMANENTLY_FORBIDDEN` key, a `WriteSpec` refusing in its own words, or
an audit passage measuring the capability unreachable. Everything a general
mechanism merely happens to block is GAP with a named blocker. So 5.4's
conclusion is right and its rule is coarser than the one already on disk.

**WHY NOBODY COULD FIND IT, measured rather than guessed:** the origin lives in
`_audit/_census/network.md` section 2 — **inside the data file it governs**,
not in any document named for rulings. No search of rulings documents could
ever have reached it. `_audit/RULINGS.md` now indexes it, and asking the
question in its own words returns it ranked first of 34.

### 5.4a CORRECTION TO 5.4: IT WAS ALREADY RULED, ON 2026-09-05, 11:25

**5.4 below presents itself as a new ruling. It is not one.** The same question
was answered sixteen days earlier and the answer is quoted inside
`_audit/2026-09-05-decide-retire-rulings.md` section 2, *"THE BOUNDARY IS NOT A
REASON"*, citing the ledger's own rule:

> *"Everything a general mechanism merely happens to block is a GAP with a
> NAMED BLOCKER — recorded so nobody reads GAP as cheap, **but not laundered
> into a decision**."*

That is 5.4's conclusion, word for word in substance. **The ruling stands; the
attribution in 5.4 is wrong**, and everything measured under it — the
three-way discriminator, the anchor-termination finding, the refusal to read
`0 matches` as `nobody ruled it` — remains good and is new.

**THE ACTUAL DEFECT IS FINDABILITY, NOT AN OPEN QUESTION.** Two separate waves
have now escalated this same question to the lead as undecided, and the lead
then re-derived it a third time. Three independent readers reached "nobody has
ruled this" about a ruling that exists, is written down, and is cited in a file
named for rulings. A corpus of 207 documents with an index keyed on DOCUMENTS
has no way to ask *"what has been ruled about X"*, and this is what that costs:
not a wrong answer, but the same answer paid for three times.

Recorded here rather than by editing 5.4, because a count — and a claim of
authorship — is evidence of what was believed when it was written.

### 5.4 RULED: incidental capture is not a ruling — and the discriminator is real, 08:40

**This one is decided rather than returned.** Section 1 files it as an open
decision, the analysis there already recommends an answer, and the recommended
answer moves reported coverage DOWN. A convention that can only understate is
one a lead can take; it is also reversible, and leaving it open is not neutral,
because the census is currently running **two incompatible practices at once**
(`R2` files 15 rows on forbidden substrings it admits catch them incidentally;
`P E6` and `N 114` say in prose that it does not count).

**THE RULING: a refusal counts as EXCLUDED-RULED only when the refusal was
AIMED AT THAT ADDRESS. A forbidden substring that catches an address as
collateral of a rule written for something else is not a ruling, and a row
resting on one goes back to GAP.**

**The discriminator was verified, not assumed** — and there are THREE outcomes,
not two. Measured against the shipped tables (42 allow patterns, 33 forbidden
substrings; synthetic slugs only):

    /in/<slug>/edit/            substring `/edit/` matched   -> a NAMED rule fired
    /company/<slug>/people/     0 allow, 0 substrings        -> see below
    /search/results/people/     1 allow pattern              -> ADMITTED

**A CORRECTION TO THIS DOCUMENT'S OWN WORDING, and I nearly published the
opposite.** Section 1 says the company and school rosters are *"refused by an
anchored pattern written for them"*. Mechanically there is **no deny-pattern
table at all** — `_ALLOWED_URL_PATTERNS` is an ADMIT list, so a non-match is a
default deny, and a probe reports `0 matches` for a roster exactly as it would
for an address nobody ever thought about. **That measurement cannot see design
intent, and reading "0 matches" as "nobody ruled it" would have been the error
this repository keeps finding: the resolver answered truthfully and the wrong
meaning was nearly taken from it.**

Reading the source settles it the other way. The allow anchor for a company
root is deliberately terminated (`/?$`) so that it stops BEFORE `/people/`, and
the comment above it states the exclusion by name: *"WHAT THIS DELIBERATELY
DOES NOT ADMIT, each named because a widening is only narrow if its refusals
are stated … A MEMBER ROSTER. Census rows `J 108` and `N 102`, and it is out of
scope by the same ruling that put a group's roster out of scope by name. It is
refused by this anchor and by nothing else."*

So the honest phrasing is **not** "an anchored pattern written for them" but
**"excluded by the deliberate END of an anchor written for the adjacent
address, with the exclusion stated by name and attributed to a ruling."** Same
conclusion, and the substring test still separates it cleanly from incidental
capture — because incidental capture means a substring DID match.

**What is NOT done here, and why.** The ruling is recorded; it is **not applied
to any census row**. Re-filing `R2`'s 15 rows means editing census files two
live waves may touch, and it wants the evidence in front of whoever does it.
Expect reported coverage to fall and GAP to rise when it lands — that is the
point of the ruling, not a regression.

### 5.5 A NEW decision for section 1: `server._error` publishes a url nothing scrubs, 09:20

Landed with the `scrub-the-landing` merge, which repaired the landing at the
raise site and **deliberately did not repair this**. It is the strongest
unrepaired disclosure finding in the corpus and it needs a ruling, so it belongs
with section 1's decisions rather than section 2's build work.

**What is measured.** `ExtractionFailedError.url` is published by `server._error`
with **no scrubber at all** — `out["url"] = url`, sitting beside a `message` and
a `hint` that both go through `scrub()`. **20 sites feed that field. All 12 of
the `dom.py` sites were DRIVEN to their own raise, and all 12 published a
planted slug verbatim at `$.url`** — each `reached` asserted from the traceback
rather than inferred, with a per-reader negative control that returned without
raising in all 12.

**Three things that make the obvious remedies wrong, each measured:**

- **Reachability is structural, not incidental.** Every site is
  `try: await page.evaluate(...) except Exception: raise ...(url=_url_of(page))`.
  **The guard is on the CALL, not on the answer** — a page double that answers
  empty reaches none of them, because an empty answer has already returned and
  walks past the `except`. Reachability reduces to "can `evaluate` raise", which
  it always can. A first attempt measured nothing for exactly that reason.
- **A remedy scoped to `_url_of(page)` misses seven more sites**, which feed the
  same field with a LANDED url: `dom.require_rows` (both callers pass
  `final_url`) and five in `server.py` — `_read_tracker`,
  `linkedin_who_viewed_me`, `linkedin_job_detail`,
  `linkedin_followed_companies`, `linkedin_my_profile`.
- **`out["message"]` is a second unscrubbed channel**, and `$.hint` a third. A
  needle planted only inside the exception `evaluate` raised landed at
  `$.message` in all 12 drives; `scrub()` runs there and removes only paths, and
  a name has no shape to scrub. The hint channel is
  `hint=f"headings seen: {...}"` in `linkedin_my_profile`, carrying page heading
  text, driven through `_error` to confirm it survives.

**Why the wave refused to fix it, and the refusal is right.** It is a DECLARED
CONTRACT whose success-path twin carries a standing fourteen-row per-site ruling
that explicitly forbids reflexive wrapping. Putting every url through
`landing.withheld()` would overturn that ruling by side effect, on a weaker
basis than the one that made it. **It needs a ruling, and it needs a browser** —
whether a LIVE authwall actually makes `evaluate` raise on these surfaces is the
one thing not established.

**What holds it shut meanwhile, so the severity is not overstated:** the same
wave measured that not one real landing on this account carries an
`/in/<member>/` path or an organisation slug — 31 events, 14 of 14
predecessor-to-parameter agreements, `/checkpoint/` never fired. The field is
unscrubbed and its worst case is unwitnessed. "A landing can be a name" remains
DERIVED.

