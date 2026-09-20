# THE FIVE PROBES UNDER A BANKED ROW, 2026-09-20

**CORRECTS:** `_audit/_census/jobs.md` -- rows 9, 11, 12, 13 and 14 all state
"the drift floor is ZERO" as a property, from one of two runs the same probe
made that hour; the other run measured 4. Row 11's "4 ids moved on a floor of
0" is refuted outright by that second run, which reported the same filter as
WITHIN DRIFT. No row's state changes; five evidence cells are corrected in
place.

The census at `_audit/2026-09-20-control-census.md` found 129 probe controls
that are computed, printed and never branched on, and ranked five files as
TIER 1: the ones sitting under a census row somebody had already banked. This
wave took those five.

## THE HEADLINE, IN FOUR NUMBERS

    banked rows examined                     9   (jobs 9, 11, 12, 13, 14, 15,
                                                  42; messaging C40; network 162)
    rows whose STATE moves                   0
    rows whose EVIDENCE is corrected         5   (jobs 9, 11, 12, 13, 14)
    flagged instances that were real
      decorative controls                    2 of 12

**All nine banked rows hold.** That is the result, and the second number is
why it is worth stating rather than assuming: **ten of the twelve flagged
instances in these five files are not controls at all**, and the two that were
are repaired without moving anything.

**AND THE THING THAT ACTUALLY THREATENED THOSE ROWS WAS NOT A DECORATIVE
CONTROL.** It was found by doing step 3 -- going back to the evidence and
re-reading it -- and it is in section 8.

## 1. `_probe_membership_sections.py` -- network.md row 162

**WHAT THE CONTROL WAS FOR.** The file's own docstring declares two controls
and the second one is this: *"A SECOND CONTROL runs the other way: a heading
pattern that cannot match must find nothing, or the matcher is over-broad
rather than the page rich."* That is a gating claim. `IMPOSSIBLE_HEADING` is
`<h9>` -- the same regex construction as the real `HEADING` matcher, at a
level HTML does not have.

**WHAT IT ACTUALLY DID.** Nothing. `silent` was computed, printed as
`CONTROL must stay silent: {silent} {'PASS' if silent == 0 else 'FAIL'}`, and
read by no branch. The sibling control (parsed anchors against the census
count) produced the return value alone.

**THE RECEIPT, and it is the sharpest line in this wave.** Run against the
pre-repair blob at HEAD `0882d35`, with one `<h9>ZZ</h9>` injected into an
otherwise clean synthetic capture:

    HEAD's own output line: 'CONTROL must stay silent: 1 FAIL'
    HEAD's own return value: True

It printed FAIL and certified the tallies in the same run. That is not an
inference about what could happen; it is what the committed code did when
asked.

**WHAT I DID.** Both controls now produce ONE verdict in one place:

    census_agrees = len(anchors) == expected
    ...
    if silent:
        print("    THE TALLIES ABOVE ARE VOID. A heading pattern that cannot
               match matched anyway, ...")
    return census_agrees and silent == 0

**DOES ROW 162 SURVIVE?** YES, and this is the one of the nine that could be
settled by RE-RUNNING rather than by reading. The probe is offline. Its two
captures are gitignored, so a worktree carries none -- they were copied in
from the main checkout (read-only; nothing in that checkout was touched) and
the probe was run before and after the repair:

    exit 0 both times, and the two outputs are BYTE-IDENTICAL

    groups  anchors 10, 10 distinct   CONTROL must stay silent: 0 PASS
            5 links, 5 DISTINCT  'Groups listing'
            5 links, 5 DISTINCT  'Groups you might be interested in'
            OVERLAP between the two sections: 0
            CONTROL against the census: parsed 10, census measured 10 -- AGREE
    events  anchors 54, 18 distinct   CONTROL must stay silent: 0 PASS
            CONTROL against the census: parsed 54, census measured 54 -- AGREE

Row 162 cites `_audit/2026-09-05-groups-surface-measured.md:49`, whose table
reads *"heading boundary, disjoint from suggestions | 5"* and *"a per-row
management control exists | 5"*. Both reproduce exactly, fifteen days later,
with the control now able to refuse.

**THE HONEST LIMIT, stated because the green was the colour I expected.**
`<h9>` cannot appear in a real LinkedIn capture, so this control reads 0 by
construction on any real input. What the repair proves is that the WIRING now
refuses; it does not make the needle strong. An assertion satisfied by an
empty result still cannot fail, and the injected-`<h9>` demonstration exists
precisely because the live reading could not have told me the difference.

## 2. `_probe_creator_content_analytics.py` -- messaging-and-content.md row C40

Two flagged instances.

**`vocab` (line 275) -- DISPLAY, and it exists for a privacy reason.** The
heading text is never printed; only the matched subset of `EXPECTED_VOCAB`, a
word list this repository wrote, because a heading can carry a person's name.
The detector's marker is that constant's NAME. Labelled, not changed.

**`feed_hits` (line 315) -- HALF OF A REAL CONTROL, and the half that was
never used.** The file calls the /feed/ comparison *"THE CONTROL THAT DECIDES
IT"*. Its structural half (`feed_sig`, region counts) is compared. Its
vocabulary half was computed, printed fifteen lines above the number it exists
to be weighed against, and nothing put the two side by side. A reader had to
hold both and do the subtraction -- which is the reader gating.

**WHAT I DID, and what I deliberately did not.** I did NOT invent the
threshold the prose leaves to the reader (*"IF THAT IS MOST OF THEM"*).
Picking a number nobody ruled would be worse than the decoration. The one
statement this comparison supports with no threshold at all is the
positive-control law, so that is the one the verdict now makes:

    if feed_hits is not None:
        vocab_discriminates = sum(hits.values()) > feed_hits
        print("      analytics vocabulary here / on the feed: %s / %s")
        if not vocab_discriminates:
            print("      THE VOCABULARY SIGNAL DOES NOT DISCRIMINATE: ...")

A discriminator that scores its own negative control as high as its target
cannot discriminate, and the probe now says so instead of leaving it to be
noticed.

**DOES ROW C40 SURVIVE?** YES. The row banks on `linkedin_creator_analytics`
called over the tool path, returning a seven-point impressions series, and on
`linkedin_server/chart_labels.py` (23 tests, shown REFUSING on the live nav
before accepting). The probe is cited as the CAPTURE behind that build, and
the row already records what this control measured: *"The headings are a trap
and are recorded as one: `h2` here reads FEED-shaped chrome, identical to the
feed's own, and the first reading of this surface went that way."* The
control's conclusion reached the row; only the arithmetic was left to a human.

**PROVISIONAL-UNSMOKED, declared.** This probe needs a live browser session
and one is not available to this wave, so the new branch is proven to be a
real use of the value and proven reachable only by reading. What would smoke
it: one run with `LINKEDIN_CDP_ATTACH=1` in which the /feed/ control
completes, printing the two vocabulary totals on one line.

## 3. `_probe_job_search_result_sets.py` -- jobs.md rows 9, 11, 12, 13, 14

The highest-stakes entry in the ranking: one finding, five banked rows.

**IT IS NOT A CONTROL.** `lines` is the report accumulator. The nested
`emit()` appends to it; `_write(lines)` writes the transcript to
`_audit/_scratch/`. `_write` calls `print`, so the detector read the only real
use of the name as print-only. The marker is the word "control" inside an
`emit("    positive control keyword: %r")` string sitting ten lines into a
28-line window.

**THE FILE'S REAL CONTROLS BRANCH, AND HARD.** `_verdict_lines()` reads them
first and returns early:

    if not _differs(positive):
        out.append("    ***  THE INSTRUMENT IS BLIND. ...  NO FILTER VERDICT.")
        return out

That branch is the gate the five rows rest on, and it existed and ran during
the banked session: the recorded reading is `POSITIVE ... shared 0,
baseline-only 7, this-only 7`, so `_differs` was True and the gate correctly
did not fire.

**DOES ANYTHING CHANGE FOR THESE FIVE ROWS?** Not from the census finding --
nothing was ever gated on `lines`. What changed came from re-reading the
evidence, and it is section 8.

## 4. `_probe_small_measures_live.py` -- jobs.md row 15

Five flagged instances, and not one of them is a control:

| instance | what it is | where the marker came from |
|---|---|---|
| `run_detector_control` -> `verdict` | the printed LABEL beside a real gate | the label's own PASS/FAIL literal |
| `_needles` -> `main_text` | the probe's INPUT | the bare Python `pass` statement |
| `read_feed_hashtag_context` -> `main_text` | the probe's INPUT | the bare Python `pass` statement |
| `read_jobs_search` -> `census` | a page measurement it PRINTS | the word `controls` in `controls_read` |
| `read_events` -> `census` | a page measurement it PRINTS | the word `controls` in `controls_read` |

`verdict` is the interesting one: `verdict = "PASS" if actual == expected else
"FAIL"` really is a control verdict, rendered as text. The GATE is its sibling
`ok`, set `False` in the same loop, returned, and branched in `main()` as
`if not await run_detector_control(): print("DETECTOR BROKEN"); return 1`.
Being vetted on the gate does not vet the label, and the census was right to
list it -- it is just not a defect.

**DOES ROW 15 SURVIVE?** YES. The row cites *"Page control PASS (Easy Apply /
Date posted / Experience level non-zero in the rail beside the trigger)"* --
that is `_page_control`, whose result `control_ok` IS bound and IS branched at
the end of `read_jobs_search`, printing SUSPECT and withdrawing the panel
reading. The row's instrument is the one that gates.

**BUT THE SAME FILE CARRIES A DEFECT OF THE SAME FAMILY THAT THE DETECTOR
CANNOT SEE** -- section 5.

## 5. TWO CLASSES A VARIABLE-BASED DETECTOR STRUCTURALLY CANNOT FIND

**(a) A DISCARDED RETURN BINDS NO VARIABLE.** This file's docstring states a
contract: *"If a page control fails, this file prints SUSPECT against that
surface and does not offer its target counts as a reading."* It held on ONE
surface of three. `read_events` and `read_feed_hashtag_context` both called
`await _page_control(...)` as a bare statement and threw the boolean away.
The detector looks for a variable nobody branches on; here there is no
variable, so the class does not appear in the 129 at all -- not as a
low-priority row, not as a false positive, simply not as anything. Both sites
now bind and branch, exactly as `read_jobs_search` does.

**AND A SIBLING WAVE HIT (b) THE SAME AFTERNOON, INDEPENDENTLY.** Commit
`9d8bcdb` on master repairs `scripts/_probe_premium_collections_live.py`,
whose verdict block ended with `print(analytics.get('count'))` and nothing
else -- so a boundary refusal, an auth wall and a reader exception would all
have rendered as `None` beside the word "drawn" and the probe would still have
exited 0. Two things about that are worth carrying: it reached the same
sentence this wave did from a different file (*"a reading taken and never
branched on is not a control"*), and **its red came from the detector's GAINED
direction on CI, on a test a local impact gate did not select.** The ratchet
built by the census is already catching new instances rather than only
describing old ones.

**(b) A VERDICT PRINTED FOR A READER TO EVALUATE.** Section 2's `feed_hits` is
one instance. `_probe_creator_content_analytics.py` also prints *"structural
fields EQUAL to the feed: N of M"* followed by *"IF THAT IS MOST OF THEM,
THIS ADDRESS IS SERVING THE FEED"*, and returns 0 either way. That is
deliberate for a capture and is NOT repaired here; it is recorded so the next
reader knows the sentence is an instruction to a human, not a branch.

## 6. WHAT THE 129 IS PARTLY MEASURING, WITH COUNTS

Across the twelve instances in these five files, the marker that made a value
"control-like" came from a verdict in only three cases. The other nine split
into four mechanisms, two of which were not previously written down:

| mechanism | instances here | corpus-wide |
|---|---|---|
| the bare Python `pass` STATEMENT in an `except` handler, inside the window | 2 | **4 of 133 (3.0%)**, measured before the repairs; the same 4 of 131 (3.1%) after |
| the window reaching an unrelated banner or `emit()` string | 3 | not measured |
| LinkedIn-UI vocabulary (`controls_read`, `controls`) in a field or variable name | 3 | see below |
| a marker-bearing CONSTANT name (`EXPECTED_VOCAB`) | 1 | not measured |

The `pass`-STATEMENT mechanism is larger than the one already disclosed in the
detector's docstring (the `passes` parameter name, 1.6%) and is now disclosed
beside it, with the sweep that measured it described. Its shape:

    main_text = ""
    try:
        main_text = await page.inner_text("main")
    except Exception:
        pass                      # <- the only marker in the window
    print(f"... {len(main_text.split(needle)) - 1}")

**A PROXY MEASUREMENT FOR THE OPEN DISPUTE, offered and not ruled on.** The
guard test records an unresolved question about three
`_probe_events_surface_shape.py` entries where the marker vocabulary collides
with LinkedIn UI "control". Counted 2026-09-20: **56 of the 131 live findings
(42.7%) have `control` as their ONLY marker, with no PASS / FAIL / VOID /
must-fire / must-stay-silent / sanity / agree vocabulary anywhere in the name
or the window.** That is an upper bound on the class, not a verdict on it --
a genuine control can be named without verdict words. The three disputed
entries are inside that 56. Handed up; not decided here.

**THE DETECTOR IS NOT CHANGED BY THIS WAVE.** Narrowing the marker rule would
move a published 129-row census, which is a wave of its own, and the
word-boundary alternative was already tried and rejected for over-rejecting
legitimate inflections. Disclosure is what this wave owes; the rules stay.

## 7. THE RATCHET, UPDATED IN BOTH DIRECTIONS

    entries 133 -> 131
    GAINED   0  (the repairs introduced no new decorative control)
    LOST     2  (removed, not left to rot)
               _probe_membership_sections.py       _analyse -> silent
               _probe_creator_content_analytics.py main     -> feed_hits

**Before touching it, I wrote down what I was about to do, as this file's own
comment demands.** I was about to grow the baseline by ten entries' worth of
argument and had nowhere to put the argument. `_audit/INSTRUMENTS.md` 34.8 had
already diagnosed that exact hole -- *"a triage table whose entries cannot
carry their triage is a census wearing a ratchet's name"* -- named the shape to
copy (`NOT_A_CORRECTION`, key plus written reason), and declined to build it
because migrating the ratchet *"is a wave and not a merge step"*. This is a
wave.

So the baseline gained an **optional** `reason` string. Ten entries carry one;
121 do not, and that difference is the point: an entry without a reason is
visibly untriaged rather than silently assumed reviewed.
`test_baseline_file_is_well_formed` asserts the field's SHAPE and that it has
not been wiped -- deliberately NOT a count, because a floor is an incentive to
write reasons in bulk, which is the rubber stamp 34.8 warned about.

**AND THE BASELINE'S OWN COMMENT WAS STALE.** It said the test *"does NOT
require this file to shrink when an old one is fixed (removing a fixed entry
is encouraged but optional -- the test does not enforce it)"*. The test has
been a two-way ratchet since the peer review that caught it being one-way; a
LOST entry fails. A reader following the comment would have left both repaired
entries in place and gone red. Rewritten.

## 8. THE THING THAT ACTUALLY THREATENED FIVE ROWS

Rows 9, 11, 12, 13 and 14 all cite one instrument, one session and one
evidence document. Reading that document against the raw outputs on disk:

**(i) THE DOCUMENT IS A COMPOSITE OF TWO RUNS AND NAMES ONLY ONE.** Its
section 5 describes *"THE RESULT-SET RUN, 16:20-16:26 ... Thirteen loads, one
session"* -- nine loads of pass one plus four of pass two. Its section 8,
answering a different question, quotes numbers that match a **seventeen**-load
run made at 16:45, all three passes, which section 5 never mentions.

**(ii) THE PATH IT POINTS AT NO LONGER HOLDS THAT RUN.** The probe writes to
one fixed `OUT_PATH`. Timestamps on disk:

    16:45:37   _probe-jobsearch-result-sets-run2-17loads.txt   (copied aside)
    16:49:48   _probe-jobsearch-result-sets.txt                (a third run)
    17:29:58   _progress-job-search-params.md                  (written last)

The thirteen-load run's own output was overwritten twice, forty minutes before
the document that cites it was written. It survives only in that document's
prose.

**AND THAT DOCUMENT IS GITIGNORED.** `.gitignore:156` quarantines
`_audit/_scratch/` unconditionally and `git ls-files _audit/_scratch/` returns
nothing, so **for rows 9, 11, 12, 13 and 14 the entire evidence chain ends
outside the repository**: the raw output is destroyed, and the document
holding the surviving prose reaches no clone and no worktree. What a reader of
a fresh checkout actually has is the cell text -- which is why correcting the
cells, rather than only writing this file, is the whole remedy.

The five cells CITE rather than DEFER, so
`tests/test_no_committed_document_defers_to_an_ignored_path.py` is right to
pass them: the numbers are stated in the row. The point is narrower and worse
than a guard violation. The numbers are stated in the row AND NOWHERE
CHECKABLE, so an over-stated one survives until somebody opens a machine that
still has the file.

**(iii) THE TWO RUNS DISAGREE ABOUT THE DRIFT FLOOR, AND THE ROWS QUOTE THE
FRIENDLIER ONE.**

| control | 13-load run, quoted by all five rows | 17-load run, same hour |
|---|---|---|
| POSITIVE (another profession) | shared 0, moved 14 | shared 0, moved 14 |
| NEGATIVE (a parameter LinkedIn never had) | moved **0** | moved **2** |
| STABILITY (baseline retaken LAST) | moved **0** -> floor **0** | moved **4** -> floor **4** |

**(iv) ON THE STRICTER FLOOR, FOUR ROWS GET STRONGER AND ONE FLIPS.** The
17-load run's own verdict lines:

    EASY APPLY             f_AL=true      MOVED 14, above the 4-id drift floor
    UNDER TEN APPLICANTS   f_EA=true      MOVED 14, above the 4-id drift floor
    IN YOUR NETWORK        f_JIYN=true    MOVED 12, above the 4-id drift floor
    FAIR CHANCE            f_FCE=true     MOVED 14, above the 4-id drift floor
    JOB TYPE full-time     f_JT=F         moved 2 -- WITHIN DRIFT (4), not evidence

Rows 9, 12, 13 and 14 are corroborated twice, on a floor four times stricter
than the one they quote. Only the phrase *"the drift floor is ZERO"* was
overstated in them.

Row 11's *"4 ids moved on a floor of 0"* is refuted: the same instrument, on
the same surface, twenty minutes later, called that filter drift.

**ROW 11 DOES NOT MOVE, AND HERE IS WHY -- I looked for the reason to move it
first.** The row has a second leg, and the probe itself says that leg is the
real measurement: *"f_JT is a dropdown whose default is ANY ... so f_JT=F asks
the corpus to narrow to what it already is. A small movement there is EXPECTED
and says little either way. PASS THREE is f_JT's real measurement."* Pass
three reproduces in BOTH later runs -- `f_JT=F` alone and `f_JT=C` alone share
ZERO postings, and `f_JT=ZZ` draws nothing -- so the parameter is honoured. A
capability row about an exposed, mapped, honoured filter is not overturned by
one leg of its corroboration being drift. **The call to move it anyway remains
available to whoever owns the census; the measurement is above and the
correction is in the cell.**

**THE LAW.** *A THRESHOLD MEASURED PER SESSION MUST BE QUOTED WITH ITS
SESSION, OR THE FRIENDLIEST SESSION BECOMES A PROPERTY OF THE SURFACE.* The
probe understood this -- it takes the stability control LAST, on purpose, so
it spans the session -- and then five census cells copied one session's number
across as though it described LinkedIn.

**AND NONE OF THIS CAME FROM THE CENSUS FINDING.** The flagged control in that
file was an accumulator. The threat was in the evidence document, reachable
only by opening it. A decorative control is a defect you can grep for; this
one is not.

## 9. THE LEDGER

| row | state before | state after | what happened |
|---|---|---|---|
| jobs.md 9 | COVERED-PROVEN | COVERED-PROVEN | corroborated on a 4-id floor; "floor is ZERO" corrected |
| jobs.md 11 | COVERED-PROVEN | COVERED-PROVEN | one leg REFUTED; stands on pass three; cell corrected |
| jobs.md 12 | COVERED-PROVEN | COVERED-PROVEN | corroborated on a 4-id floor; "floor is ZERO" corrected |
| jobs.md 13 | COVERED-PROVEN | COVERED-PROVEN | corroborated on a 4-id floor; "floor is ZERO" corrected |
| jobs.md 14 | COVERED-PROVEN | COVERED-PROVEN | corroborated on a 4-id floor; "floor is ZERO" corrected |
| jobs.md 15 | COVERED-PROVEN | COVERED-PROVEN | its cited control was always branched; unchanged |
| jobs.md 42 | COVERED-PROVEN | COVERED-PROVEN | both cited controls `return 1`; unchanged |
| messaging C40 | COVERED-PROVEN | COVERED-PROVEN | control half repaired; row banks on the tool and the parser |
| network 162 | COVERED-CANNOT-DELIVER | COVERED-CANNOT-DELIVER | RE-RUN after the repair; byte-identical output |

**Rows moved: 0. Evidence cells corrected: 5. Claims refuted: 1.**

## 10. TWO THINGS THIS WAVE'S OWN RECEIPT GOT WRONG

Both caught by the full suite rather than by reading, which is the argument
for running it.

**(i) THE RECEIPT WAS PINNED TO `HEAD:` AND PASSED TEN OF TEN -- UNTIL THE
COMMIT LANDED.** Demonstration B compares the flagged variable's verdict
before and after. Reading the "before" side from `HEAD` worked right up to the
moment the repair became HEAD, at which point two of the ten went red because
the before side and the after side were the same blob.

    A receipt pinned to a moving reference stops being a receipt at the
    moment it is most likely to be believed.

Now pinned to `0882d35` -- the commit the census measured and this repair
landed on -- and if that blob stops resolving the demonstration says so and
FAILS rather than skipping.

**(ii) A STRING `.replace()` AT MODULE LEVEL IS A WRITE, TO A GUARD THAT
MATCHES BY NAME.** `tests/test_scripts_are_import_safe.py` flagged
`BROKEN = CLEAN.replace(...)` as "replace at import time". A pure string
operation is not a write -- this is the same name-matching family the register
records four times over in 34.10 -- but the remedy here is to stop acting at
import rather than to argue with the guard, so the injection moved into
`broken_capture()`. Recorded because this wave spent a section counting other
instruments' name-matching and then tripped one.

## 11. WHAT IS NOT CLAIMED

* Nothing about the other 51 flagged files. They sit under GAP or
  EXCLUDED-RULED rows or are cited nowhere, exactly as the ranking said.
* No ruling on the marker-vocabulary dispute, and no change to the detector.
  Section 6 adds a count and two disclosures; the rules are untouched.
* `feed_hits`'s new branch is UNSMOKED against a live session (section 2).
* The 17-load run is not asserted to be *more correct* than the 13-load run.
  Both are readings of a surface that ranks. The claim is narrower and harder
  to argue with: two runs exist, they disagree about the floor, and five cells
  quote one of them as a property.
* No claim that the drift floor is 4 either. It was 0 once and 4 once.

## 12. FILES

    scripts/_probe_membership_sections.py               the silent control now gates
    scripts/_probe_creator_content_analytics.py         feed_hits enters the verdict
    scripts/_probe_small_measures_live.py               two discarded returns now branch
    scripts/_check_repaired_probe_controls_can_fail.py  NEW -- the receipt, 10 checks
    scripts/detect_unbranched_probe_controls.py         docstring: two more mechanisms
    scripts/probe_controls_known_decorative_baseline.json  133 -> 131, + reason field
    tests/test_probe_controls_are_never_decorative.py   reason field, shown failing
    tests/test_a_correction_is_findable_from_the_claim.py  one triage entry
    _audit/_census/jobs.md                              five cells corrected + back-pointer
    _audit/INSTRUMENTS.md                               entry 36

The two gitignored captures copied into this worktree to re-run section 1
(`_audit/_probe-groups-hyd.html`, `_audit/_probe-events-hyd.html`) are ignored
here as they are everywhere and are not part of this commit. The main
checkout was read and not written.
