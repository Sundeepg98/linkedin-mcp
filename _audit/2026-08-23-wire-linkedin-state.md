# Wiring the preview to a live read -- `oldsha18` (parent `oldsha14`)

**What a caller can no longer do.** Describe the target. `render_preview(spec, facts=..., state=...)`
is gone; `preview(spec, target, navigator, page, to_state)` performs the reads itself and has no
`facts=` and no `state=` to pass. Measured at `oldsha14`, the defect in one call: a made-up title, a
made-up employer and `state="not_following"` produced `not_following -> following, reversible by
unfollowing`. The reading now arrives as a single-use TTL'd RECEIPT that only a page load mints, and
`mint()` issues no grant without one -- a state string can be typed by a caller that never read,
exactly as a boolean can be set by one that never previewed.

**Both shapes, kept apart.** Follow reads off the posting page (1 load, state and action share a
rendering). Save reads off `linkedin_saved_jobs` (2 loads, different surface, because the save
control's ON state does not exist on this account to photograph). The block prints which it got, both
urls, and `page_loads`. `reversible_by` survives and is now asserted in both directions: two of four
are undoable by this server, two are not.

**Four cold-review findings closed en route** (`_slice-cold-review-2026-08-23.md`): 2a the `unknown`
refusal was asserted with a phrase the WRONG refusal also contains -- deleting the branch left 73
green; 2b `assert "this server" in by_server` passed on its own inverse; 2c `reversibility_class` was
asserted against the set of values that exist, so all four could be flipped to IRREVERSIBLE beside
prose reading "reversible by..." -- now pinned per action AND refused at render when the two fields
disagree; 3+6+9 `set_open_to_work` returned before the unknown check, took a job id for a profile
setting, and could hold a grant for a surface nobody has opened -- it is now `target="self"`, is
refused a grant at issue, and its gate says plainly it is a warning rather than an offer.

**Measured, all at `oldsha18`.** 1059 -> **1083 passed** locally. Runtime, measured on both sides
rather than inferred: this module went **73 tests / 2.25s -> 97 tests / 38s**, and the suite 177s ->
215s. The cost is real and it is the point -- the gate now drives a headless Chromium over frozen
captures instead of being handed a description. One browser per test rather than per gate call cut
that module from 90s to 38s (a cold launch-and-close is 1.35s; five loads on a live browser are
0.89s between them, so essentially the whole price is the launch).
**17 mutants applied to the new guards, 17 killed** --
honestly: two came back green on the first pass because they were bad mutants of mine, editing a
message rather than behaviour, and were redone behaviourally. `readonly.py`, `test_readonly.py`,
`test_launch_boundary.py` are **zero-line diffs** (`git diff --numstat oldsha14` empty). Package scans
**zero mutating calls**. No new fixture file; the single derived string is the frozen tracker capture
with LinkedIn's own Saved count edited 0 -> 1, labelled DERIVED, because a self-consistent non-empty
saved list cannot be photographed on an account with nothing saved.

**What still stands between here and one supervised save on a throwaway posting.** Three things, and
only the first is a decision. (1) The permission classifier still refuses LinkedIn writes -- unlifted,
correctly. (2) `perform()` is still a `raise`: no `page.click` exists, so the click and its
post-conditions have never run once. (3) `unsave_job` cannot render a gate at all today -- nothing on
the account is in the state it is valid from -- so the round trip has to start with the save, and the
saved-list read is the only thing that would confirm it landed. Not blocking: the anchors are frozen
at both hydration states and the observation's age is recorded on the grant for `perform` to re-check.

**Not mine, still open, and the most urgent thing in that review**: finding 1 MUST-FIX -- the
de-anonymisation key for the four sanitised fixtures is committed and pushed (`scripts/_build_follow_fixtures.py`,
two probe scripts, one id in `notifications.html`). Findings 4, 5, 7 are read-side (`shape.py`/`dom.py`)
and untouched here; 4 still stands (`complete` accepts `rendered > total`). Separately, `ci.yml`'s
header comment is stale -- I measured 1083 collected and, with `PLAYWRIGHT_BROWSERS_PATH` pointed at
an empty directory, **105 failed / 940 passed / 38 errors**; I did not edit it because `ci-for-newest`
may own that file.

**Sequel, same day:** the cold review re-ranked a MUST-FIX above this seam -- the de-anonymisation
key for the fixtures was committed and pushed. See [2026-08-23-privacy-key-and-guard.md](2026-08-23-privacy-key-and-guard.md).
