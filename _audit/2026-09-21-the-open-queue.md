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
