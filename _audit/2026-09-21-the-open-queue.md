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
