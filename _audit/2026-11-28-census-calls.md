# Lane census-calls28 (lane A): the census calls, no code

Lane A of the census wave plan of 2026-11-28 (`census-plan28`, section 3), branched
from master `9ec91965`. Census only: no file under `linkedin_server/` is touched, nor
`capture-queue.tsv`, `INSTRUMENTS.md` or the rulings register by hand. Nothing loaded
LinkedIn; no browser, port or session was touched.

Evidence classes: VERIFIED means read on disk in this lane, MEASURED means an
instrument counted it on a tracked file in this lane, DERIVED means computed from
what was read, UNVERIFIED means not checked. People by role only.

STATUS: IN PROGRESS. Sections 2 and 3 are final; sections 4 to 6 are held (section 1).

## 1. The order, and what holds what

| item | rows | outcome | where |
|---|---|---|---|
| 1. J 86, the D6 call on P I14 | J 86 | GAP -> COVERED-UNFIRED | section 2, committed |
| 2. the code reads | M C65, M C91 | both stay GAP: neither tool reaches a group post | section 3 |
| 3. D6 calls | N 3, N 50 | held, network.md | section 4 |
| 4. the orchestrator's ruling | N 61 | held, network.md | section 5 |
| 5. the re-judges | M C11, rank 23's 13 rows, J 3, J 17, J 151 | no row moves | section 6 |

THE BASE HOLD. The brief puts `network.md` and `messaging-and-content.md` after
hygiene28's merge, because that lane edits both. Master was `9ec91965` at every check
in this lane, without hygiene28's merge, so every edit to those two slices is written as
a ready patch under the lane's scratch directory and held. `jobs.md`, `profile.md` and
the side tables are not hygiene28's.

## 2. J 86: COVERED-UNFIRED by D6 on P I14's tool

The lane-K ledger (`_audit/2026-09-28-lane-k-ledger.md`, section 3) lists six rows "a
shipped tool may already reach by D6-CAPABILITY-OVER-AFFORDANCE", among them "`J 86` on
`P I14`", as "a census call for the row's owner, not made here". This lane makes it.

The bar (D6, `_audit/2026-09-23-rulings-write-class-and-delegated-calls.md`): the
package delivers the same capability payload by its own sanctioned routes, the row names
them, and it rests on their proofs: PROVEN if live-proven, else UNFIRED.

VERIFIED on this tree, each read in the source:

- `linkedin_mark_company_interest(job_id, confirm_token)` is spec `mark_company_interest`
  in `writes.SANCTIONED_WRITES` and `writes.PERFORMABLE` (36 performable actions,
  imported), behind `writes_enabled()` and the single-use grant. `P I14` rests on it,
  COVERED-UNFIRED since lane L7 (2026-09-24), never fired.
- It presses the control J 86's own Help article documents. The gate requires one
  'I'm interested' button in a posting's About-the-company card, found beside the link
  to `a1380509` (`company_interest.HELP_ARTICLE_FRAGMENT` is `/answer/a1380509`); the
  spec's `direction_source` says this was MEASURED on three tracked posting captures.
  J 86 cites `a1380509` and `a1427386`.
- The spec cites J 86 by id twice: `reversibility_evidence` ("a1380509, cited by census
  row J 86") and `spends` ("census row J 86 quotes its Help article as 'max 50, expires
  1 year'. Not measured here").
- The payload: the tool's docstring says the signal goes to that employer's recruiters,
  is not a post, and his network is not told -- J 86's "privately signal interest".

So D6 holds, and more strongly than it needs to: the route is not a substitute for
J 86's affordance, it is that affordance, on a posting. The route is a posting by that
employer, named by its job id; whether a company Page draws the same control is not
measured here, and no shipped tool presses it there, so the cell names the one route
that delivers. The two rows are one capability counted in two slices, as J 72 and P M4
are (the plan, section 5).

THE STATE IS COVERED-UNFIRED, because the route never fired. THE HOLD IS
OPERATOR-NAMES-THE-TARGET: the act is for one employer's recruiters, so its proof fires
only at a posting he names, after `P I14`'s two prerequisites (a company he names, and
`P I15`'s ON-state control captured so that the undo exists before the act). The jobs
slice's per-row table has no R/W column, so `reader_closable_blockers.direction_of`
reads J 86 as `unknown` and `ruling_holds.hold_of` adds no write hold by itself; the
cell cites `HELD BY` `OPERATOR-NAMES-THE-TARGET` in the marker form, as J 128 and
J 163 do.

What moved with it, each MEASURED:

- `jobs.md`: the cell, and a DELTA paragraph from `scripts/count_census_states.py`
  (COVERED-UNFIRED 27 -> 28, GAP 104 -> 103, stated rows 175).
- `next-step.tsv` and `jobs-directions.tsv`: J 86's line leaves each, because both hold
  still-GAP rows only.
- `write-classes.tsv`: no J 86 line existed (its class read `-`), so nothing changes.
- `blocker-assignments.tsv` is the committed evidence the map is derived from and is
  unchanged, as at the N 93 precedent; `blocker-map.tsv` is regenerated.
- The pins, section 7.

## 3. The code reads: M C65 and M C91 stay GAP

The question (brief, item 2): do `linkedin_comment_on_item` and `linkedin_react_to_item`
reach a GROUP post by their own route? The answer is NO for both, so the two D6 calls
the ledger named ("`M C65` on `M C25`", "`M C91` on `M C32`") fail and both rows stay
GAP.

VERIFIED in the source on this tree:

1. BOTH TOOLS ACT ONLY ON ONE ADDRESS SHAPE. Each spec's `url_pattern` is
   `^https://www\.linkedin\.com/feed/update/urn:li:[A-Za-z]+:[0-9]+/$`
   (`writes.py`, `linkedin_comment_on_item` and `linkedin_react_to_item`), enforced at
   the write door by `assert_write_url`. The read boundary admits the same permalink and
   nothing wider (`readonly.py`, the ONE ITEM PERMALINK entry), and the readers that
   emit an item key require the same shape (`dom.py`, `urnShape` in
   `ACTIVITY_ITEMS_JS` and in the named profile's activity read, and `NAMED_ITEM_KEY`).
2. NO SHIPPED TOOL HANDS OUT A GROUP POST'S KEY.
   - `linkedin_group_page` returns "A verdict and counts, never a post" (its docstring).
   - `linkedin_publish_group_post` is receipt-only: what Post leaves in a group is not
     captured, and no key comes back.
   - `linkedin_my_activity_items` reads his own activity page and
     `linkedin_read_named_profile` the Activity section of a profile he names; no
     capture on disk shows a group post on either.
   - `linkedin_group_memberships`, `linkedin_group_members` and
     `linkedin_search_groups` return groups or members, not posts.
3. THE GROUP FEED DOES NOT DRAW THAT ADDRESS AT ALL. `N 175`'s cell records a live
   fire of 2026-09-21 on three groups this account belongs to: a route census of those
   pages, 86, 35 and 47 anchors, found `/feed/update/` zero times -- "A group feed's
   post permalinks do not wear that route" (`linkedin_server/group_page.py` says the
   same, with its receipt `scripts/_probe_group_feed_permalinks.py`). Session 11's
   group skeletons on disk blank every entity path and `data-urn`, so they can neither
   confirm nor contradict that.

So the address these two tools are confined to is not the one a group post wears on its
own surface, and no route in the package supplies a group post's key: the payload is
not delivered by the package's own sanctioned routes, and D6 does not discharge either
row. Whether a group post also has a `/feed/update/` permalink somewhere else is
UNVERIFIED; no capture shows one.

WHAT EACH ROW NEEDS FIRST: the route a group post's permalink wears, and its comment and
reaction controls, captured on the feed of a group he belongs to. That is also `N 175`'s
reopener ("`anchors.ROUTE_TABLE` gaining the route a group post permalink actually
wears"). The cell text and the re-pointed step are held (sections 1 and 6.4): the cells
are in `messaging-and-content.md`, and a step to a capture needs a capture-queue line,
which this lane does not write.

## 4. N 3 and N 50 (held)

To be written with the held patch.

## 5. N 61 (held)

To be written with the held patch.

## 6. The re-judges (no row moves)

To be written.

## 7. Pins re-derived

`scripts/census_completion.py --check` after J 86's move, MEASURED, never summed: eight
pinned figures moved, and `PINNED` was re-pinned from those values with one history line
each.

    adjudicated        278 -> 279
    b1_standing         28 ->  29
    delivered_broad    187 -> 188
    gap                506 -> 505
    gap_unknown        104 -> 103
    jobs_dir_w          54 ->  53
    jobs_gap           104 -> 103
    unfired             92 ->  93

`PINNED_B1_ROWS`: J 86 entered COVERED-UNFIRED held by OPERATOR-NAMES-THE-TARGET, as
`--check` reported it, and joins that tuple. After the re-pin `--check` ends "every
headline figure matches its pin".

## 8. Gates

### 8.1 J 86's commit

No live session was on (`_state/LIVE_SESSION_ON` absent at each check).

- `scripts/census_completion.py --check`: "every headline figure matches its pin",
  rc 0, after the re-pin (rc 1 before it, naming the eight figures and J 86).
- `scripts/check_next_step.py` GREEN (505 = census_completion's gap);
  `check_jobs_directions.py` GREEN (103 of 103); `check_write_classes.py` GREEN (365
  lines); `check_read_addresses.py` GREEN (56 of 56); `ruling_holds.py` GREEN.
- The three derived views, `--check` rc 0 after `--write`: `build_audit_index.py`,
  `build_rulings_index.py` (only its "documents scanned" count moved, for this
  record) and `build_blocker_map.py`. The map moved 92 lines: J 86's `state_today`,
  and the reason locator's candidate count on rows whose top candidate is unchanged
  (`CANDIDATE-1-OF-17` -> `1-OF-18` on J 9). Without this record staged it moved 12, so
  80 of the 92 are the new document entering the locator's corpus, not a row moving.
- pytest, the 35 test files that read a changed file (the impact gate's read map,
  `scripts/impact_gate_read_map.json`, used as a list of direct readers and not
  widened), with `-n 4 --dist loadfile -p no:randomly --durations=15`: 2352 passed in
  285 s. That is over the 2-minute local cap. Sampled while it ran: CPU 100% busy and
  disk 91.2% idle, with two other lanes' pytest runs on the box. The five slowest were
  corpus-wide guards (58 s, 57 s, 56 s, 29 s, 27 s). Later gates in this lane run the
  census instruments for the changed tables only; the corpus-wide guards run on CI.

## 9. Questions for the orchestrator

To be written.

## 10. Lessons

- On this box, `grep -c $'\r'` in Git Bash counted every line of a file as
  CR-bearing, before and after `sed -i` had rewritten that file to LF-only (Python
  read 0 CRLF in 506 lines). The commit was unaffected, because the index stores LF,
  but the check could not fail. Count line endings on bytes, and edit CRLF tables
  with a bytes-aware script, not `sed -i`.
