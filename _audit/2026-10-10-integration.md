# Integration, 2026-10-10: lanes B5, NP, B2 and B3 onto master

Integrator lane (`lint-integrator`), briefed by the orchestrator at 19:23 IST:
merge already-certified lane heads onto master a457819 (lane S), in order, one
`git merge --no-ff` each, resolving every conflict once. No feature was built
here. Standing rules: `_state/LANE-STANDING-RULES.md` (gitignored). Offline:
no LinkedIn load, no port 9224, no Chrome.

## 1. Merged, in order

| # | lane | head | certified on | merge commit |
|---|---|---|---|---|
| 1 | B5 (groups: `N 165`, `N 177`, `N 197`) | c8bf057 | ci/ run 38056745268 | d5cf13c |
| 2 | NP (`M C35` / `M C35b`, `linkedin_withdraw_reaction`) | 6bc6aac | ci/ run 38056748099 | 101b5de |
| 3 | B2 (`N 161`, `N 179` built; `N 80`, `N 133` by D6) | 3eaf679 | ci/ run 38057019466 | e8197aa |
| 4 | B3 (`M C43`, `M C48`, `M C38`) | 06693d4 | ci/ run 38057169716 | 7b1b707 |
| 5 | master (live session 10's record) | 63ffea2 | ci/ run 38058046169 | the commit adding this record |

Merge 5 was clean (notes on `P B9`, `N 47`, `N 20`, `N 45`; no row moved); it
keeps this branch a fast-forward of master.

## 2. How the conflicts were resolved

- **Derived views** (`_audit/INDEX.md`, `_audit/RULINGS.md`,
  `_audit/_census/blocker-map.tsv`): regenerated with each script's `--write`
  to a fixed point after every merge, then `--check`; never hand-merged.
- **Prose and registration** (`server.py`, `__init__.py`, `README.md`): every
  lane's paragraph and registration block kept. The headline counts were
  re-derived off the merged registry, never taken from either side.
- **Equal moves that merged as one.** Where two lanes had each written the same
  new count from the same base (sixty-three tools, 772 stated rows, 711 in
  scope, PERFORMABLE 19, the census row pin's `total`), git merged the two
  edits as ONE change, with no conflict. Each such site was found by search or
  by its guard and re-derived on the merged tree.
- **Census pins** (`scripts/census_completion.py`): both lanes' comments kept;
  each value set to the figure `census_completion.py` MEASURED on the merged
  tree, never a sum of the two sides.
- **Census rows edited on both sides** (`network.md` rows 176 and 177 at merge
  1): each side had left the other's row at base, verified against the base
  blob, so row 176 takes lane S's paragraph and row 177 lane B5's move. No
  single row was edited by two lanes.
- **Union tables** (surface tests, `test_writes.py`, the correction table):
  the union of both lists.

Resolved by judgement, one line each:
- Merge 1, `network.md` rows 176/177: adjacent rows, each moved by one lane
  only (checked against the base blob); each row takes the side that moved it.
- Merge 2, `writes.py`: lane S's and lane NP's verification branches both
  kept, each an early return on its own action.
- Merge 2, `server.py` actions-versus-tools note: twenty-one sanctioned
  actions against twenty write tools (each lane had added one to each).
- Merge 3, `triage_read_gap_rows.py` and `test_every_orphan_module_is_ruled.py`:
  lane B5 and lane B2 each deleted a different entry in one hunk; both
  entries go and both lanes' LEFT comments stay.
- Merge 3, `server.py`'s split history: lane B2 had put its own
  "(Forty-four, eighteen and sixty-two until ...)" at the head of the history
  list; it moved to the list's end, in merge order, with the other lanes'.
- Merge 4, `server.py` registration: lane B2's and lane B3's blocks, both
  appended at the file's end, came back interleaved across two hunks; each
  block was rebuilt whole (B2's, then B3's) rather than taking ours+theirs per
  hunk, which would have split two functions.

## 3. Measured on the merged tree

| after | tools | read | write | parameters | stated rows | adjudicated | delivered_broad | unfired |
|---|---|---|---|---|---|---|---|---|
| merge 1 (B5) | 64 | 45 | 19 | 105 | 772 | 217 | 139 | 24 |
| merge 2 (NP) | 65 | 45 | 20 | 107 | 773 | 218 | 140 | 25 |
| merge 3 (B2) | 67 | 47 | 20 | 109 | 773 | 222 | 144 | 27 |
| merge 4 (B3) | 70 | 50 | 20 | 111 | 773 | 225 | 147 | 30 |
| merge 6 (B4) | 72 | 50 | 22 | 115 | 773 | 227 | 149 | 32 |

Other pins re-derived the same way: `gap` 555 -> 551 -> 548, `gap_read`
89 -> 85 -> 82, `b3_admitted` 38 -> 34 -> 31, `b1_no_ruling` 9 -> 11 -> 14,
`achievable` 712, write classes 372 = 16 R1 + 34 R2 + 322 R3. At merge 6:
`gap` 546, `b1_no_ruling` 16, `delivered_strict` 117.

**Same row edited on both sides:** none. Every census-table hunk (merge 1's
`network.md`, merge 4's `messaging-and-content.md` and `next-step.tsv`) was
resolved per row against the base blob 6c65815, and in every row exactly one
side had moved; a row moved by both would have stopped the script.

**INSTRUMENTS.md:** lanes B2 (90), B3 (91) and B5 (93) appended sections; they
stand in that order. Master's older 88-then-84 order is untouched.

## Merge 6: lane B4

Lane B4's certified head 0f7e6d0 (`J 161`, the similar-jobs alert pair, and
`J 124`; ci/ run 38058465627; merge base a457819), merged onto 4c3c001 at the
coordinator's order of 19:59 IST. The SHA was merged, not the branch; the
branch stood at 0f7e6d0 itself, so nothing after it exists to exclude.

Measured on the merged tree: 72 tools (50 read, 22 write), 115 parameters,
PERFORMABLE and REACHED 22, 23 sanctioned actions against 22 write tools, 16
sanctioned mutating calls (lane B4's one trial click), 773 stated rows. The
census pins are in section 3's table, row "merge 6".

Resolved by judgement, one line each:
- `server.py` registration: the three lanes' blocks at the file's end came
  back interleaved across three hunks; B2's and B3's are kept whole as on
  4c3c001, then lane B4's block whole, ending at its own end marker.
- `server.py` actions-versus-tools note: lane B4's pair adds two to each
  (twenty-three actions, twenty-two tools). The history clause now gives
  each event the values BEFORE it. Merge 2 had written the values after it
  for lanes NP and S, and that is corrected here.
- `__init__.py`: twenty-two write tools and sixteen sanctioned mutating calls,
  both measured. Lane B4's own "(nineteen and fifteen until ...)" became
  "(twenty and fifteen ...)", because lane NP's write came first on this tree.
- `writes.py`: lane NP's and lane B4's sanctioned entries and retry-unsafe
  entries are kept as a union.
- `test_receipt_names_its_own_action.py`: the reaction pair and the alert
  pair are both kept as sanctioned shared places; PERFORMABLE is 22.
- `test_server_surface.py`: the number-word map gains 21 and 22, so the
  instructions' "TWENTY-TWO WRITE" is the word the test derives.

## 4. Gates

After each merge commit: `census_completion.py --check` ("every headline
figure matches its pin"), `check_next_step.py`, `check_write_classes.py`, the
three derived-view `--check`s, the tests in the conflicted files and their
count guards, and `tests/test_no_committed_identity.py` on the committed blob.
The full suite ran on lane CI only (`scripts/lane_ci.py push` / `wait`).
