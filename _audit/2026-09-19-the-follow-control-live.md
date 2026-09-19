# The follow control, live: it was RELABELLED. Counts from five hydrated postings.

**Measurement only. NO WRITE WAS FIRED** -- no `confirm_token` was requested or
minted, `linkedin_follow_company` was never called in any form, and nothing in
`dom.py`, `shape.py` or `writes.py` was edited. **No repair is proposed here**;
which repair follows is the next decision and it is not mine.

This takes the read the 17:xx wave named and could not fit
(`_audit/2026-09-19-follow-company-has-no-direction.md`). That wave established
offline that `company_follow_state` and `company_about.follow_state` are two
routes to ONE button inside the About-the-company card, and left three
hypotheses with three different repairs: the attribute was **dropped**, there
are now **two controls**, or it was **relabelled**.

## THE ANSWER: RELABELLED. Not dropped, not doubled.

Five hydrated postings, five identical readings. The control is there, it is a
`<button>`, it is inside the About card, there is exactly ONE of it, and it
**carries an `aria-label`** -- whose value is no longer one of the two the
reader knows.

| posting | `dom.FOLLOW_CONTROL` exact | `button[aria-label^="Follow"]` | `[role=button]` w/ follow | buttons in About card | aria present | aria len | aria shape |
|---|---|---|---|---|---|---|---|
| 1 | 0 | 1 | 0 | 2  | yes | 25 | `W6 W4 W4 W8` |
| 2 | 0 | 1 | 0 | 57 | yes | 26 | `W6 W7 W11`   |
| 3 | 0 | 1 | 0 | 3  | yes | 11 | `W6 W4`       |
| 4 | 0 | 1 | 0 | 2  | yes | 11 | `W6 W4`       |
| 5 | 0 | 1 | 0 | 2  | yes | 21 | `W6 W5 W8`    |

`Wn` = an alphanumeric run of length n; spaces kept. **Shapes only -- no
third-party value is recorded in this file.** On every one of the five the
button's rendered TEXT is exactly `Follow` (6 chars), and the About card holds
exactly ONE element whose exact text is `Follow`/`Following`.

### The three numbers the previous wave asked for

1. **Elements matching `dom.FOLLOW_CONTROL` verbatim: 0.** Five of five.
2. **Buttons in the About-the-company card regardless of `aria-label`: 2, 57,
   3, 2, 2.** Never zero on a hydrated card. Exactly one of them is
   follow-like in every case.
3. **`aria-label` present: YES on all five**, and its value is NOT one of the
   two known ones. `[role="button"]` follow controls: 0 -- it is still a real
   `<button>`, so the element type did not change either.

### What the new label IS, stated as a relation

The label is **`"Follow "` followed by the employer's own name.** Verified
mechanically, not by eye: for each posting, the observed `aria-label` length
was compared against `len("Follow ") + len(<that posting's own company name>)`
and the observed token-length shape against `W6` + the employer name's own
token-length signature. **Both matched on 5 of 5**, and the comparison printed
only booleans. The names themselves came from the same postings' payloads and
are deliberately not written down.

So LinkedIn moved the control from a two-state caption to a per-employer
accessible name. That is why the exact-value union matches nothing.

## WHY THIS KILLS THE OTHER TWO HYPOTHESES, AND ONE DEAD BRANCH IT EXPOSES

- **Not "dropped":** the attribute is present on all five.
- **Not "two controls":** exactly one follow-like button per card; the
  `count > 1` branch never fired.
- The live `company_follow_state.why` on posting 1 read *"no follow control
  rendered ... page had not hydrated yet"*. **That message is now
  misattributing.** The page HAD hydrated -- the card drew its follower line,
  its buttons and its own `Follow` text. `count == 0` here means the SELECTOR
  missed, not that the page was early.
- **`shape.follow_state`'s third branch is unreachable as written.**
  `FOLLOW_CONTROL` matches only the two exact values, so a control the union
  selects can never carry a label outside `FOLLOW_LABELS`. The branch that
  exists to say *"LinkedIn has relabelled it"* is precisely the branch a
  relabelling cannot reach: the relabel lands in the `count == 0` branch and
  is reported as non-hydration. **The one thing that happened is the one thing
  the reader cannot say.** Recorded, not fixed.

## THE HYDRATION TRAP, AND WHY ONE SAMPLE WOULD HAVE LIED

First pass: only 1 of 4 postings had a populated card. The other three showed
`about_container_present: true` with **0 buttons and 0 anchors** -- the
container exists as a skeleton well before its contents. A probe that waits on
the container alone reads an empty card and would have reported "0 buttons in
the About region", which points straight at the wrong hypothesis. The second
pass waited on `ABOUT_COMPANY_CONTAINER + " button"` and all three populated.
**The brief's insistence on three-or-four postings is what caught this**; a
single sample of the skeleton is indistinguishable from a real absence.

## HONEST LIMITS OF THIS MEASUREMENT

- **One boolean in the raw probe output is WRONG and must not be quoted:**
  `aria_contains_employer` reads `false` on all five. Its needle was the card's
  first `h2/h3/a[href*="/company/"]` text, which on this card is the section
  heading, not the employer. The employer relation above is the OFFLINE
  recomputation against the posting's own payload, which is the one that holds.
- Counts come from one render per posting, one account, one session, one
  locale, in the operator's own signed-in browser. Five postings agreeing makes
  a transient unlikely; it does not make this global.
- The reading was taken by **attaching** over CDP to the already-running
  browser (`connect_over_cdp`, port 9224, Chrome 153). Nothing was launched
  against `_state/chrome-profile` and the running MCP server was not restarted.
- That server reports itself **STALE** (`loaded_commit` behind `disk_commit`),
  so its `why` strings are the older code's. The DOM counts above are read off
  the live page and do not depend on the server's version.
- 4 of the 5 postings were also read through `linkedin_job_detail`; where both
  exist they agree -- `company_follow_state.state: unknown` beside
  `company_about.follow_state: "Follow"`, exactly the divergence that started
  this.

## WHAT THIS FILE DOES NOT DECIDE

Whether the fix is a prefix selector, an anchored pattern, a text-route
fallback, or a change to how `count == 0` is explained -- **all of that is out
of scope and deliberately not started here.** The previous wave's standing
warning still applies: the click path builds its selector from
`follow_control_selector(label)`, so any repair that restores a direction
without restoring an addressable selector converts a refusal that reports the
defect into a failure that does not.

## PROVENANCE

Probe scripts (throwaway, session scratchpad, not harvested):
`follow_live_probe.py`, `p2.py`, `relate.py`; raw output
`follow_live_probe.json`, `follow_live_probe2.json`. The raw JSON carries only
shapes, counts and booleans -- it was written that way rather than redacted
afterwards.
