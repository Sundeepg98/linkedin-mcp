# dom.py unread-readings slice

## What ran, over what, and the control

A throwaway AST-walking script (kept outside the repo, in the session
scratchpad, not committed) parsed `linkedin_server/dom.py` and collected two
kinds of "measured field": (1) string keys in dict literals directly inside a
`return {...}` (with nested dict literals recorded as dotted paths, e.g.
`observed.metrics_seen`), and (2) `out["key"] = ...` subscript stores, kept
only when that same variable name is later returned bare (`return out`) from
the same function scope. Nesting and scope were tracked with a function-stack
AST visitor keyed on `(lineno, col_offset)`, so two functions that happen to
share a name are never conflated. This produced 117 raw dict-literal keys and
142 subscript candidates; 2 subscript candidates were dropped because their
variable was a per-row dict appended into a list that was returned (e.g.
`record["shape"] = ...; results.append(record); return results`) rather than
the returned object itself -- out of scope for "a key on the reply", not
analysed further. One instance was excluded per the brief: `("navigated",
activate_messaging_filter)` -- confirmed as the only occurrence of that key
in the file, so no other finding could have been caught by that exclusion.
That left 256 findings over 130 distinct key strings.

For each distinct key, the script counted occurrences of the quoted forms
(`"key"` / `'key'`, which also matches `["key"]` and `.get("key")`) and the
attribute form (`.key`) as regex hits across `linkedin_server/` (excluding
dom.py itself), `tests/`, and `scripts/`, plus a separate bare-word count
across `_audit/` prose. Inside `dom.py` itself, the same quoted/attribute
search ran with the producing function's own line range (or the union of
line ranges, if more than one function produces that key) excluded, so a
key's own definition site never counts as its own consumer.

**Can-fail control, both numbers**: an invented key, `zzz_not_a_real_key`,
returned zero hits in every one of the five counts. The script then
auto-picked the first key with a nonzero `linkedin_server/`-outside-dom.py
hit as its "known consumed" example and landed on `activated` (1 hit).
Manual inspection of that hit showed it was a **false positive for the
control's purpose**: `linkedin_server/server.py:3801` builds its own,
independent `{"activated": False, "why": "no filter asked for"}` default
dict -- it does not read dom.py's value by name at all (the real link is a
`**applied` spread four lines later, discussed below). So the auto-pick was
swapped for a hand-verified one: `headline`, confirmed genuinely read via
`identity.get("headline")` at `linkedin_server/writes.py:3404`. Both control
numbers (0 for the invented key, a real non-mechanical read confirmed by eye
for the positive case) are as required before anything else below was
trusted.

**Method notes worth carrying forward, not just for this slice:**
- `linkedin_server/dom.py` was being live-edited by the slice's requester
  while this ran -- `activate_messaging_filter` grew a `movement`
  classification, a `WriteAttemptError` guard, and a new `url_movement`
  field between this agent's first read of the function and the point the
  AST script executed a few tool calls later. The script re-reads the file
  fresh at run time, and a second read afterward matched the JSON output's
  line numbers exactly, so the results below are against the file's current,
  post-edit state, not a stale snapshot.
- The quoted/attribute search cannot distinguish "this file reads dom.py's
  key" from "this file independently builds a same-named key of its own" in
  any file *outside* the producing function (the `activated` case above).
  This can only ever push a key toward CONSUMED, never manufacture a false
  UNREAD, so the UNREAD table below is not exposed to it -- but the CONSUMED
  count (114 non-ambiguous keys) should be read as an upper bound on genuine
  consumption, not as individually spot-checked.
- A second, more structural gap: **whole-dict carrying is invisible to a
  key-string search.** `server.py:3844` does `{"requested": wanted or None,
  **applied}`, and `server.py:1754` does `extra["insights"] = await
  dom.read_profile_views_insights(page)` followed by `shape.envelope(...,
  extra=extra)`, whose body (`shape.py:4356`) does `out.update(extra)`. Both
  carry a whole dom.py return value into a tool's JSON response without ever
  naming its keys as literals. This is verified, not speculative, for two of
  the three UNREAD findings below -- see the per-finding notes.

## UNREAD keys (zero consumers anywhere except possibly _audit/ prose)

| function | key | line | kind | (a) linkedin_server/ | (b) dom.py elsewhere | (c) tests/ | (d) scripts/ | (e) _audit/ prose |
|---|---|---|---|---|---|---|---|---|
| `read_company_about_card` | `hrefs_error` | 1096 | subscript | 0 | 0 | 0 | 0 | 0 |
| `activate_messaging_filter` | `pill_label` | 3018 | return_dict | 0 | 0 | 0 | 0 | 0 |
| `read_profile_views_insights` | `metrics_seen` (path `observed.metrics_seen`) | 8902 | return_dict | 0 | 0 | 0 | 0 | 1 |

## TEST-ONLY keys (zero in a/b/d, nonzero only in tests/)

| function | key | line | kind | (a) linkedin_server/ | (b) dom.py elsewhere | (c) tests/ | (d) scripts/ | (e) _audit/ prose |
|---|---|---|---|---|---|---|---|---|
| `activate_messaging_filter` | `url_before` | 3019 | return_dict | 0 | 0 | 4 | 0 | 0 |
| `activate_messaging_filter` | `url_after` | 3020 | return_dict | 0 | 0 | 4 | 0 | 0 |
| `activate_messaging_filter` | `url_movement` | 3023 | return_dict | 0 | 0 | 3 | 0 | 0 |
| `read_sdui_actions` | `residue_suspected` | 5770 | subscript | 0 | 0 | 6 | 0 | 0 |
| `read_job_insight_panels` | `heading_count` (path `observed.heading_count`) | 8639 | return_dict | 0 | 0 | 1 | 0 | 2 |

All five were spot-checked: every test hit is a genuine `assert
result["key"] == ...` / `assert x["key"] is ...` read, not a coincidental
re-production, e.g. `tests/test_the_filter_click_cannot_leave_the_address.py:254:
assert result["url_movement"] == "filter_state", result` and
`tests/test_the_payload_read_is_a_race.py:87: assert out["residue_suspected"]
is True, (...)`.

## AMBIGUOUS-NAME keys (generic words, counts unreliable, pulled out of the tables above)

All 8 landed CONSUMED even under the swamping risk, so none of them changes
the UNREAD picture -- listed for completeness per the brief, not
individually verified beyond that.

| key | bucket | (a) | (b) | (c) | (d) | (e) |
|---|---|---|---|---|---|---|
| `count` | CONSUMED | 57 | 53 | 236 | 203 | 1790 |
| `error` | CONSUMED | 66 | 0 | 150 | 89 | 229 |
| `found` | CONSUMED | 0 | 0 | 1 | 4 | 752 |
| `label` | CONSUMED | 18 | 18 | 123 | 58 | 904 |
| `reason` | CONSUMED | 41 | 0 | 41 | 52 | 1328 |
| `rows` | CONSUMED | 23 | 3 | 66 | 60 | 3745 |
| `total` | CONSUMED | 7 | 1 | 31 | 20 | 296 |
| `why` | CONSUMED | 223 | 0 | 237 | 35 | 753 |

(`url`, `name`, `note`, `source`, `text`, `value`, `kind`, `position`,
`title` are in the ambiguous word list but did not occur as a return-dict or
returned-subscript key anywhere in `dom.py`, so they do not appear here.)

## Closing counts

- Total return-dict-literal keys found (raw, before any filtering): **117**
- Total subscript-store candidates found (raw): **142**, of which **140**
  were kept (2 dropped: per-row fields on a dict appended to a returned
  list, not the returned object itself)
- Excluded per the brief (`navigated` on `activate_messaging_filter`): **1**
- **Total findings kept: 256**, over **130 distinct key strings**
- Bucket counts (non-ambiguous keys, 122 of the 130):
  - CONSUMED: **114**
  - TEST-ONLY: **5**
  - UNREAD: **3**
- AMBIGUOUS-NAME (pulled out separately): **8** (all happened to be CONSUMED)

## Top 3 UNREAD findings, read against their surrounding code

1. **`hrefs_error`** (`read_company_about_card`, line 1096) is a measurement
   of a condition, not decoration, and the surrounding comment says so in its
   own words: `out["hrefs_error"] = marker` stores `type(exc).__name__` when
   the about-card's link harvest (`container.locator("a[href]")`) raises,
   and the comment directly above records that this field used to be
   *logged* until a taint test caught it leaking page text, at which point
   "the site is gone rather than pinned" -- the print was removed but the
   field was never wired to a reader. This is the cleanest of the three: its
   caller (`server.py:4878`) passes the object into `shape.company_about_card(about, ...)`
   and separately reads the sibling key directly (`about.get("hrefs") or
   []`, `server.py:4899`), so `hrefs_error` is not even carried onward
   whole -- it is discarded on the floor, confirmed both by the sweep and by
   reading the call site.
2. **`metrics_seen`** (`read_profile_views_insights`, line 8902, under
   `observed`) is also a measurement of a condition -- `"metrics_seen":
   len(metrics)` counts how many metric rows the page's insights extractor
   recognised, and the function's own docstring frames the whole `observed`
   block as existing so "a page that rendered nothing this reader
   recognises still says how big main was" -- i.e. built specifically to
   detect a degraded/empty extraction. Unlike `hrefs_error`, this one *does*
   reach a live tool response structurally: `server.py:1754` stores the
   whole return value as `extra["insights"]`, which `shape.envelope()`
   merges verbatim (`shape.py:4356: out.update(extra)`) into what the tool
   returns -- so `metrics_seen` is visible in the JSON at
   `insights.observed.metrics_seen`, but no Python code anywhere names it,
   branches on it, or could notice if the count silently went to zero.
3. **`pill_label`** (`activate_messaging_filter`, line 3018) is the
   descriptive one of the three, not a condition: `label` is the pill's
   matched accessible name/text, captured (per the comment two lines above
   its assignment) because "an empty label beside activated:true reads like
   a contradiction" -- i.e. for a human reading a log or a failure report,
   not for a caller to branch on. It sits in the exact same return statement
   as the slice's motivating, already-excluded `navigated` field, and reaches
   the tool response the same way `navigated` used to: via `server.py:3844`'s
   `{"requested": wanted or None, **applied}` spread, which is verified in
   this file's own text and is invisible to any key-string search -- the
   spread is the mechanism by which a field can be simultaneously "in the
   API response" and "UNREAD" by this analysis's definition.
