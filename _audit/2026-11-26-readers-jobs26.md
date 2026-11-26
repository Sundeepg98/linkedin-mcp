# readers-jobs26, 2026-11-26: the jobs-side readers on session 11's skeletons

Lane `readers-jobs26`, briefed by the orchestrator on master `7760a5f`
(integration 3, lane-certified, with session 11's 48 skeletons in
`tests/fixtures/live11/`). Built OFFLINE in its own worktree: nothing here
loaded LinkedIn, connected to port 9224 or started a browser against an
account. The live-session flag (`_state/LIVE_SESSION_ON` in the main checkout)
was absent at every check. Standing rules: the canonical lane file, with this
lane's substitutions (server.py block heading "lane readers-jobs26").

THE ROWS: the jobs-side lines session 11 captured -- line 1
(`admit-jobs-application-settings`) and its riders, line 15 (a Page's
Insights tab), lines 25 to 28 (a Page's About, Events, Life and Products
tabs), line 29 (career insights), line 30 (the tracker's clicked_apply
stage), line 21 (`jobs-alerts-manager`, in part) -- and the three rows the
orchestrator ruled BUILD on 2026-11-25: `J 168`, `J 19`, `J 163`.

HOW EACH ROW WAS READ. Its cell and its bar first; then the capture its step
names. Session 11's keyed skeletons and its key sit in the main checkout's
gitignored state; a LinkedIn word was taken as drawn only where hashing it
with that session's key gave the keyed shape at that place. Where the session
kept a raw capture of his own settings page, LinkedIn's interface words were
read off it by element and then confirmed by keyed shape; nothing of his own
data, and no third party's text, is quoted here or in any fixture.

---

## 0. What disk said that the brief did not

1. **The repository has no `CLAUDE.md`.** The brief says to read "the repo's
   CLAUDE.md"; none is tracked and none is on disk in the main checkout or
   this worktree. `README.md` and the lane standing rules were read instead.
2. **Line 1 carries ten rows, not nine.** The capture queue's line
   `admit-jobs-application-settings` and session 11's record list `P M12`
   beside the nine the brief names. `P M12` is read here with the line
   (section 3): it is this lane's line, and no other lane's row.
3. **`J 52`'s tool already exists.** Lane A built
   `linkedin_tracker_stage(stage="clicked_apply")` on 2026-10-10 and left the
   row GAP only because no capture drew the stage. Session 11's capture is
   that capture, so this row needed a proof and no new tool (section 2).

---

## 2. `J 52` -- the tracker's clicked_apply stage: GAP -> COVERED-UNFIRED

THE BAR, in the row's own words: *"no reader for this stage ... Owed: a reader
and an allowlist entry for the stage"*; the address was admitted by lane A
(`?stage=clicked_apply` on its own line), and lane A's record left it GAP
because *"no capture draws a clicked_apply tab, so whether the stage renders a
list at all is unmeasured"*.

THE CAPTURE: session 11, load 12, `/jobs-tracker/?stage=clicked_apply`, tracked
as `tests/fixtures/live11/tracker_clicked_apply.html`. Its words, measured by
keyed shape and written by `scripts/_build_live11_word_skeletons.py` into
`tests/fixtures/live11/tracker_clicked_apply_words.html` (eight words, 13
places, every other text `x`):

- the tab strip, drawn twice, reads `Saved <dot> 0`, `Clicked apply <dot> 0`
  (its pill checked), `Applied <dot> 0`, `Interview <dot> 0` and `Archived`,
  beside `Date posted`, `Job tracker` and the bulk bar's `0 selected`;
- one `h2` reads `No matches`, one of `shape.TRACKER_EMPTY_MARKERS`;
- no job row: no anchor matches `dom.JOB_HREF`.

So the stage IS drawn, WITH its own count, and the tracker's zero rule --
believed only when LinkedIn's count says zero AND the page draws its empty
state -- is met on the real page.

THE PROOF: `tests/test_tracker_clicked_apply_live11.py`, 7 passed. In a local
headless Chromium (every request the skeleton would start aborted by the
page's own route), the shipped `dom.read_main_text`,
`shape.parse_tracker_tabs` and `shape.tracker_empty_state` read the strip and
the empty state; `dom.wait_for_tracker_list` attaches at once;
`dom.harvest_linked_cards` finds no row; and the TOOL, end to end through
`server._read_tracker`, returns `empty: True`, `linkedin_count: 0`,
`empty_state: "No matches"`. THREE CONTROLS, each a failed read: the same
capture with its words reduced (the committed copy), the stage's count planted
at 3 with no row, and the stage's count removed. A fourth test holds the
fixture to the committed copy: the two differ on 13 lines, and each differing
line is the copy's once its declared word is reduced.

RED FIRST, as the test was written: two of the three controls first PASSED
the tool as an empty list, because the plant replaced the words where the
fixture's provenance comment lists them rather than in the markup. The plant
helper (`tests/live11_words.py::plant`) now edits the markup only and requires
the exact count it was told; both controls then fail the tool as designed.

THE CHANGE TO SHIPPED CODE: one sentence of the tool's docstring, which said
the captures draw no clicked_apply tab; it now says the stage's own page draws
its tab with a count and its empty state. The chain guard
(`tests/test_a_covered_row_names_the_artifact_that_covers_it.py`) binds
`J 52` to the tool beside `J 50` and `J 51`.

NOT SHOWN, and so not claimed: a clicked_apply stage holding rows renders the
row component the other stages do. The capture holds none. The first fire
settles it -- the same scope `J 50` entered COVERED-UNFIRED with.

THE CENSUS: `J 52` GAP -> COVERED-UNFIRED; its next-step and jobs-directions
lines left the side tables; the capture queue's single-row line
`admit-jobs-tracker-stage-clicked-apply` left the queue (its next step is a
fire, not a capture); `J 52` joins `PINNED_B1_ROWS[NO_RULING]`.
