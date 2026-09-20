# The source-chain verification: 8 claims, 6 clean, 1 real drift, and 1 DRIFT THAT WAS NOT ONE

**2026-09-20. Verifier: a cold agent, briefed to trace eight claims to their
symbols. Adjudicated here by the integrator against the source.**

The verifier's own deliverable was written to a session scratchpad, which does
not survive the session. This file is the durable record; the distilled result
is below, not a pointer to a temp path.

## The headline is the false positive, not the drifts

The verifier reported **two drifts**. One of them is real. **The other is a
correct measurement of the wrong population**, and had it been relayed rather
than checked, it would have "corrected" a correct claim in **six census rows**.

---

## THE DRIFT THAT WAS NOT A DRIFT

**Reported:** *"`read_job_insight_panels` returns 7 top-level keys — the 4 named
in the claim are all present verbatim, but the claimed total of 'six' is wrong
(actual is 7). VERIFIED keys / DRIFTED count."*

**The claim it was checking**, repeated verbatim across six rows of
`_audit/_census/jobs.md`:

> *one reader, six fields, six rows that all sat GAP because nothing joined the
> code to the census*

**Both statements are true, and they are not about the same thing.** The
function's return dict does carry seven top-level keys:

| key | kind |
|---|---|
| `applicant_insights` | capability field |
| `company_insights` | capability field |
| `promoted` | capability field |
| `responses_managed_off_linkedin` | capability field |
| `verified_job` | capability field |
| `more_behind_a_control` | capability field |
| **`observed`** | **telemetry** — `headings`, `heading_count`, `view_names`, `main_present`, `main_chars` |

`observed` is the reader's account of *what it saw while reading*: how many
headings the page had, which `data-view-name` values were present, whether
`main` existed and how many characters it held. It is provenance, and it maps
to no capability and no census row.

**Six capability fields. And exactly six census rows rest on this reader** —
`J 24`, `J 26`, `J 27`, `J 121`, `J 122`, `J 123`, confirmed by a count of the
citations in `jobs.md`. The claim is exactly right on both halves.

### The law

**A count is comparable to another count only if both count the same kind of
thing.** The verifier counted *dict keys*; the claim counted *capability
fields*. Neither measurement is wrong. The comparison is.

This is the same shape this corpus has been finding all day under other names:
decide what a token IS before asking a resolver about it (280 "dangling
commits" were help-article ids); a uniqueness test over a pre-filtered set
measures the filter. Here the population was never stated, so the verifier
chose the one its tool made easy — **top-level keys are what `dict.keys()`
returns, and "capability fields" is a judgement the code does not label.**

### What this costs if it is not caught

Nothing about the verifier's process was sloppy — it cited the symbol, quoted
the keys verbatim, and flagged exactly the discrepancy it saw. **A careful,
correct, well-cited finding that is nonetheless wrong is the expensive kind**,
because every signal says relay it. The only thing that caught it was opening
`dom.py` and looking at what the seventh key contained.

**A claim of the form "N of X" should name X.** Had the census row said "six
*capability* fields", the verifier would have had the population and would not
have reported a drift.

---

## THE DRIFT THAT IS REAL

**Reported:** the `sortBy=DD` value is correct, but it is not carried by a named
constant.

**Confirmed.** `server.py:3829` is `params.append(("sortBy", "DD"))` — an inline
literal inside the function body. Its siblings are module-level constants:

```
server.py:3400   _DATE_POSTED = {
server.py:3406   _WORKPLACE = {"any": None, "on_site": "1", "remote": "2", "hybrid": "3"}
server.py:3407   _EXPERIENCE = {
```

So a claim phrased as *"whatever constant carries sort-by"* is wrong in kind,
not in value. The URL parameter is right; there is no symbol to cite for it.
**Recorded, not repaired** — making it a constant is a code change with no
measurement behind it, and the four filters it would join are not obviously one
family.

---

## THE SIX THAT VERIFIED EXACTLY

1. `linkedin_job_detail` assigns the whole reader result to `out["insights"]`
   and returns `out` unmodified — traced statement by statement to the final
   `return out`.
2. `company_id` routes through `jobfilter.company_filter_param` to
   `COMPANY_FILTER_KEY = "f_C"`.
3. `locations` routes through `jobfilter.locations_plan` (always called) to
   `jobfilter.merge_location_reads` (**only on the `fanout` state** — single-place
   calls skip it) with `jobfilter.MAX_LOCATIONS = 5`. The fanout-only nuance is
   the verifier's, and it is the kind of qualification a claim usually loses.
4. `_DATE_POSTED` (4 values → `f_TPR`), `_WORKPLACE` (4 → `f_WT`) and
   `_EXPERIENCE` (6 → `f_E`) map exactly as claimed.
5. Keywords reach the URL through `urllib.parse.urlencode` inside the nested
   `_search_url`, with only `.strip()` applied — boolean, phrase and paren
   operators pass through unaltered in content.
6. All five tools (`linkedin_notifications`, `linkedin_my_activity_items`,
   `linkedin_open_messaging`, `linkedin_compose_fields`,
   `linkedin_page_plugin_snippet`) are registered `@mcp.tool()`s, absent from the
   server's own TWELVE-WRITE list, and read-only under the
   `_write_tool`/confirm-token apparatus.

### Two things worth keeping from those six

- **`linkedin_notifications` and `linkedin_open_messaging` each carry a
  disclosed server-side side effect** — badge clearing and opening a thread.
  Neither is a write under this repo's gate, and the distinction is correct:
  the gate governs *our* mutations, and LinkedIn marking a badge read because
  we looked is a consequence of reading. It is disclosed rather than hidden,
  which is the right treatment, but **"read-only" and "causes no change on the
  server" are not the same sentence** and this corpus should not let them
  collapse.
- **`linkedin_page_plugin_snippet` opens no browser session at all** — a pure
  local string builder over `page_id`, with no network or browser import in
  `page_plugin.py`. **It is fireable entirely offline**, which makes it the
  cheapest firing target in the census and worth knowing when the signed-in
  profile is contended.

`linkedin_open_messaging`'s `message_filter` is the closed set
`dom.MESSAGING_FILTERS` — focused, other, unread, jobs, connections, inmail,
starred — guarded by `dom.assert_permitted_filter`, which raises `ValueError`
before any locator is built for anything outside that 7-tuple.

---

## Disposition

- **No census row is changed by this verification.** The six rows on the
  insight-panel chain stand exactly as written.
- The sort-by drift is recorded above and repaired nowhere.
- **No instrument is admitted from this pass**, and none is claimed: this was a
  reading, not a check, and nothing here has been shown failing.
