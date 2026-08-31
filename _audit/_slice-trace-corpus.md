# Slice -- the parse-trace corpus, measured and widened

**File owned:** `tests/test_tracker_harvest_census.py` (only file touched).
**Repo:** `D:\Sundeep\projects\job-hunting\mcp-servers\linkedin`, branch `master`, HEAD `77ecd2b`.
**Not committed, not staged.** `_state/` untouched. No live browser; every reading below comes
from the fixture files through a local headless Chromium via `page.set_content`, which is what
the suite itself does.

---

## 1. The measurement, before anything was changed

The debt line said **"the trace corpus is 13 records but fewer shapes -- 7 of them are identical
`jobs_search` rows."** It was a lead, and it was half right.

**The record count is 14, not 13.** Enumerated by walking exactly what
`test_the_trace_agrees_with_the_parser_it_describes` walks:

| source | records |
|---|---|
| `jobs_tracker_row.html` | 1 |
| `jobs_tracker_empty.html` | 0 |
| `jobs_search.html` | 7 |
| `TRACE_RECORDS` (synthetic) | 6 |
| **total** | **14** |

**The "7 identical `jobs_search` rows" half is exactly right** -- all 7 collapse into one shape
bucket, and they are 50% of the corpus by count.

**Where 13 came from, and it was not a mistake.** `git log -S'"live welded row"'` puts that
record in commit `cef81b8`; `git show cef81b8~1` shows `TRACE_RECORDS` holding **five** entries,
so the corpus was 1+0+7+5 = 13 when the sentence was written. It went stale the moment the
sixth record joined, two hundred lines above the prose that counted it.

### The shape canonicalisation used

Seven dimensions, none of them identity:

```
( number of lines in shape.split_lines(record["text"]),
  bool(record["logo_name"] or record["meta_line"]),   # a lockup anchor is present
  bool(record["hidden"]),                             # screen-reader copies to subtract
  bool(record["href"]),
  any line start-matches shape._JOB_STATUS_LINE,      # the text carries a status
  any line satisfies shape.has_time_ago,              # the text carries a time-ago
  shape.MIDDLE_DOT in text )                          # the text carries a middle dot
```

**BEFORE: 14 records -> 7 distinct shapes.**

| lines | lockup | hidden | href | status | time-ago | dot | n | members |
|---|---|---|---|---|---|---|---|---|
| 0 | - | - | - | - | - | - | 1 | `empty` |
| 1 | - | - | - | - | yes | - | 1 | `live welded row` |
| 1 | - | - | - | yes | - | - | 1 | `every line a status` |
| 1 | - | yes | - | - | - | - | 1 | `subtraction takes the only line` |
| 2 | - | - | - | - | - | - | **2** | `ordinary row`, `chrome only` |
| 4 | yes | yes | yes | - | - | - | **7** | the seven `jobs_search` rows |
| 7 | - | - | yes | yes | - | yes | 1 | `jobs_tracker_row` |

**One honest limit of this key, stated rather than hidden:** `ordinary row` and `chrome only`
share a bucket and produce DIFFERENT verdicts (`parsed` vs `no_lines`), because the key does not
ask whether a line is chrome. Shape buckets undercount the work in that one cell. That is why
the branch census below, not the bucket count, is what each added record had to earn against.

### The branch census -- what the corpus actually reached

Thirteen distinct branches of `parse_job_card` / `parse_job_card_trace`. **Three were reached by
nothing:**

* `welded_SPLIT_fires` -- the welded one-line path is ARMED once (`live welded row`) and FIRES
  never. That record has no middle dot, so `split_welded_card_line` refuses it.
* `time_ago_DISCARDED` -- the `has_time_ago(line) and line != anchor` discard at `shape.py:624`.
  Consequence: of `shape.PARSE_LINE_LABELS`' four words, the corpus could only ever produce
  three. `time_ago` was never emitted by any record.
* `positional_company_refused_as_meta_line`.

### Which records were load-bearing

Seven mutations of the trace were simulated and each record checked for whether it makes the
guard's own assertions go red. On the 14-record corpus:

| mutation of `parse_job_card_trace` | records that catch it |
|---|---|
| drop the `elif not remaining` branch | 1 -- `every line a status` |
| drop `and line != anchor` (the exemption) | 1 -- `live welded row` |
| drop the chrome filter | 1 -- `chrome only` |
| drop the screen-reader subtraction | 1 -- `subtraction takes the only line` |
| drop the status lift | 1 -- `every line a status` |
| swap the two refusal verdict strings | 4 |
| **drop the time-ago discard** | **0 -- NOT CAUGHT** |
| **swap `has_time_ago` for `is_timestamp_line`** | **0 -- NOT CAUGHT** |

Four of the five catchable mutations have exactly ONE catcher. The corpus is thinner than 14
suggests: the seven `jobs_search` rows and `jobs_tracker_row` catch nothing that the synthetic
records do not already catch.

---

## 2. AFTER

**16 records -> 9 distinct shapes -> 15 branches.** Two records added, both re-measured against
the edited file rather than against a simulation.

| | records | distinct shapes | branches reached |
|---|---|---|---|
| before | 14 | 7 | 13 |
| after | 16 | 9 | 15 |

### Record 1 -- `"live welded row, separator intact"`

```
text = link_text = "Senior Full-stack Engineer - Remote Acme <MIDDLE_DOT> India (Remote)Reposted 4d ago"
href = "https://www.linkedin.com/jobs/view/4423880462/"
```

* **Branch newly reached:** `welded_SPLIT_fires`. Before this record the corpus armed the welded
  path and never once fired it.
* **Shape newly reached:** `(1 line, no lockup, no hidden, href, no status, time-ago, middle
  dot)`.
* **Also:** co-catches the `and line != anchor` mutation (not solely -- `live welded row`
  already does).
* **Where this shape was measured on a real page:** the live Saved tab, 2026-08-30. It is the
  same string this file already carried in section 9 as `SAVED_LINE` -- "THE TWO LIVE SHAPES,
  measured 2026-08-30 -- Saved and Draft". `_audit/2026-08-30-linkedin-undo.md` sections 41-44
  and `shape.py:parse_job_card`'s docstring ("Measured live 2026-08-30 on both the Saved and the
  Draft tab").
* **Why it is not a duplicate of `live welded row`:** that record is a **dot-less**
  approximation written before the split existed. The measured row has the separator, and the
  separator is the whole reason the row splits. The corpus was guarding an approximation of the
  row the wave was about.
* **De-duplication done at the same time:** the literal now lives once, as `SAVED_WELDED` in
  section 7, and section 9's `SAVED_LINE` reads from it. The file previously carried three
  separate renderings of this measured line.
* Parses to: `title` "Senior Full-stack Engineer - Remote Acme", `company` None, `location`
  "India (Remote)", `when` "4 days ago", `job_id` 4423880462.

### Record 2 -- `"a content line carrying its own timestamp"`

```
text = "Senior Engineer\n\nRiverton, Fairhaven, United States - 1 week ago - 33 people clicked apply"
link_text = "Senior Engineer"
```

* **Branch newly reached:** `time_ago_DISCARDED` -- the discard at `shape.py:624`, the mirror of
  the anchored-title exemption. With it the corpus produces the `time_ago` label for the first
  time, completing all four words of `shape.PARSE_LINE_LABELS`.
* **Shape newly reached:** `(2 lines, no lockup, no hidden, no href, no status, time-ago, no
  dot)`.
* **Where this shape was measured on a real page:** the line is verbatim the one measured on
  `job_detail_following_hydrated`, quoted in `shape.py:parse_job_card`'s docstring and again in
  this file's `test_the_narrow_repair_was_chosen_over_the_wide_one`. Re-measured for this slice:
  it is the ONE record of 25 that the wide repair would move, and the census names the fixture.
* Trace: `verdict=parsed`, `labels=['content', 'time_ago']`, `has_anchored_title=True`.

---

## 3. Candidates REJECTED as padding

Each was built, measured, and dropped. None of them adds a branch, and none of them makes the
guard able to fail at a mutation it currently survives.

| candidate | provenance | why rejected |
|---|---|---|
| **a card with a lockup anchor (`logo_name` + `meta_line`)** -- the search-card shape | real; `jobs_search.html` | **Already reached, seven times over.** This is precisely the over-represented bucket the debt line complains about. Adding an eighth is the padding this slice exists to avoid. |
| **a card whose only content line after the title is the location** (`lone_line`) | real; measured 2026-08-30, `shape.py` docstring + `test_a_lone_line_after_the_title_is_the_location_not_the_company` | Branch `lone_line_becomes_location` is already reached by `ordinary row`. Its shape differs from `ordinary row` only by carrying an `href`, which no filter reads. Catches zero mutations. |
| **`DRAFT_LINE`, the welded card with an end-anchored status** | real; live Draft tab 2026-08-30 | Reaches `welded_SPLIT_fires`, which record 1 already reaches. Its welded status is lifted by `_WELDED_STATUS`, which `parse_job_card_trace` does not model at all, so the guard cannot see the difference. New shape bucket, zero new branch, zero mutations caught. |
| **a verified-employer screen-reader line, `"<title> with verification"`** | real; 5 of 14 rows measured 2026-08-22 | Two variants tested. With the line in `hidden` it IS the `jobs_search` shape -- already reached seven times. With the line NOT hidden (the 2026-08-22 defect shape) it reaches only `company_positional`, which `jobs_tracker_row` already reaches, and catches zero mutations. What it actually guards is field ASSIGNMENT, which the trace does not model; that coverage belongs in the parser's own tests, where it already exists. |
| **a card whose title contains a time-ago substring** (the `shape.py:624` exemption) | real; live Saved tab 2026-08-30 | **Already reached** by `live welded row`, which is the sole catcher of the exemption mutation. Record 1 co-catches it. |

---

## 4. Two mutations the corpus still does NOT catch -- for the lead

Reported rather than papered over, because closing them would have meant inventing a shape.

**`no_time_ago_discard`** (delete the time-ago discard from the trace) and **`wide_repair`**
(swap `has_time_ago` for `is_timestamp_line` in the trace) both remain uncaught even after
record 2. Record 2 reaches the branch, but on a card with a surviving title the verdict is
`parsed` either way, and the guard's assertion is over the verdict.

**The record that WOULD catch both is a welded tracker line with NO anchored title** -- measured
as red on both mutations, and the sole catcher of each. I did not add it, because it is a
**synthesis, not a measurement**:

* the welded Saved/Draft line is measured (2026-08-30), and
* `parse_job_card`'s docstring records that `anchored_title` is None on "most tracker rows", and
  `jobs_tracker_row.html` is a measured tracker row with no anchor,
* **but the live Saved row that was measured had `has_anchored_title` true**
  (`_audit/2026-08-30-linkedin-undo.md` section 44: "75 characters, one line, `has_anchored_title`
  true, claimed by `time_ago`"). The combination has not been seen.

To catch those two mutations by verdict you need a card where EVERY surviving line carries a
timestamp and none of them is the anchor. No documented card is that shape. **The honest options
are a capture of a populated Saved tab -- still the missing artefact the audit's own debt list
names -- or accepting the gap.** Not a record invented to fill it.

**A cheaper partial fix that stays in evidence, if the lead wants it:** the guard already asserts
`seen == set(shape.PARSE_VERDICTS)`. The same assertion over labels --
`seen_labels == set(shape.PARSE_LINE_LABELS)` -- is now REACHABLE for the first time because of
record 2, and would make deleting the discard from the trace go red. I did not add it: the slice
scoped me to the corpus, not the guard.

---

## 5. Prose counts checked, and only one was wrong

| line (post-edit) | claim | verdict |
|---|---|---|
| 946 (was 896) | "Measured across all **13** records this file drives" | **WRONG -> corrected to 16**, with the staleness and its commit recorded in the docstring |
| 1101, 1104 | "across all **25** records the fixtures produce ... zero of 25" | **CORRECT.** Measured: 25 records across every fixture; the wide repair moves exactly 1, and it is `job_detail_following_hydrated`, exactly as written; the anchored-title exemption changes 0 of 25 |
| 1283 | "the welded path fires on **ZERO** of the 25 records" | **CORRECT.** Measured 0 |
| 1304 | "Of the 25 records ... the two whose lines split at all are not the ones carrying a lockup" | **CORRECT.** Measured: exactly 2 (`job_detail_following_hydrated[0]`, `jobs_tracker_row[0]`), both lockup-free. 21 of 25 carry a lockup, matching the audit |

The three "25" figures were left alone. Adding records to `TRACE_RECORDS` cannot move them --
those are fixture records, and `TRACE_RECORDS` is synthetic.

---

## 6. The drift guard

```
venv\Scripts\python.exe -m pytest -q tests/test_tracker_harvest_census.py
33 passed in 11.93s
```

**`test_the_trace_agrees_with_the_parser_it_describes` passes over all 16 records.** The trace
and the parser agree on both new records:

* `live welded row, separator intact` -- trace `parsed`, parser returns a row.
* `a content line carrying its own timestamp` -- trace `parsed` with
  `labels=['content', 'time_ago']`, parser returns a row.

No record was adjusted to make the guard pass; neither needed it. Nothing in `shape.py` was
touched. The full suite was NOT run -- sibling agents are editing other files in this tree.

---

## 7. One incidental, flagged not acted on

`tests/fixtures/profile_views_analytics.html` and `profile_views_analytics_hydrated.html` are
**not ASCII**. This file's `markup()` helper reads with `encoding="ascii"`, so any test that
loads either of them through `markup()` will raise `UnicodeDecodeError` rather than fail a
readable assertion. Neither is loaded by this file today. Outside my slice; not touched.
