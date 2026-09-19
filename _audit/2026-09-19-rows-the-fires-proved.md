# The rows the first fires proved -- and the rows they did not

Banking pass over `_audit/_census/` against `_audit/2026-09-19-tier1-fires.md`,
the writes fired and verified 17:44-17:55 on the operator's own account.

**TWO ROWS MOVED. THREE PROSE CLAIMS WERE SUPERSEDED. NOTHING ELSE.**

    _audit/_census/jobs.md      row 44   Unsave a job       CU -> CP
    _audit/_census/profile.md   row N2   Dark mode change   CU -> CP

    blocker-map.tsv             REGENERATED, BYTE-IDENTICAL

---

## THE REFUTING QUERY, RUN FIRST

The brief's premise was that these four capabilities serve census rows waiting
to be banked. **The query that would refute it: what do those rows ALREADY
say?** Run before any edit, over all four slices.

**It refuted most of the premise.** Of the six rows the four capabilities touch,
**four were already COVERED-PROVEN** and had been for weeks:

    jobs 43     Save a job                        already CP (fired 2026-08-30)
    jobs 45     Read the Saved list               already CP
    jobs 46     Read whether ONE posting is saved already CP
    profile N1  Dark mode current state           already CP (six readings)

**Today's fires re-exercised all four and moved none of them.** Re-proving a
proven row adds a reading, not a state. Had the premise been taken on trust,
four rows would have been "banked" that were banked already -- which is how a
coverage number inflates without anyone lying.

**The blocker map was also queried and returned ONE row across all four
capabilities** (`M C37`, unsave a saved POST -- a different surface, still GAP,
not served by any of these fires). That is because the map enumerates rows that
were GAP at the frozen commit, and neither row that moved today was ever GAP.

---

## THE TWO ROWS THAT MOVED, AND WHY EACH QUALIFIES

A row moves to COVERED-PROVEN only if the capability was **exercised and read
back** -- and, by this campaign's standard, read back on a surface OTHER than
the one acted on. Both qualify on that test, not on a weaker one.

### `profile.md` N2 -- Dark mode change

The row had named its own verification before any fire: *"verification is a
fresh navigation and a re-read of all three radios."* **That is exactly what was
performed** -- so the row's own criterion was met, rather than an easier one
being found after the fact.

    prior state    Always off    3 radios, exactly one checked, 0 forms
    fire           1 click       page RELOADED before the read-back
    read back      Always on     the other two read UNCHECKED
    undo           1 click
    restoration    Always off    identical to the prior state
    audience       NOBODY        no feed, no notification

**The read-back is stronger than re-reading the pressed control:** a control
that redrew wrongly would have to report itself checked AND both others report
themselves unchecked to pass. Two refusals on the way in were correct and both
named what they SAW rather than only what they failed to match.

**It also settles a verdict, not just a row.** Every preview of this action
printed `reversibility_class: STILL-UNKNOWN`, and the gate itself named what
would settle it: *ONE ROUND TRIP, WATCHED.* That round trip has now been
performed and watched.

### `jobs.md` row 44 -- Unsave a job

Six separate places in `_audit/` recorded this as never fired. All six were
accurate when written; they are kept in the file rather than deleted.

    saved-tab count   2 -> 1    read from the saved stage, NOT the control clicked
    posting label     Unsave -> Save
    prior state       established TWO ways before the fire
    re-save           1 -> 2    round trip closed in both directions

**ONE THING STAYS UNSETTLED AND THE GATE IS RIGHT ABOUT IT:** whether re-saving
restores the original saved DATE, and therefore the list's ORDER. Reversible in
membership is not reversible in ordering. The fire could not distinguish the two
hypotheses -- the posting had been saved sixty seconds earlier, so both put it
at position 1 -- and the version that WOULD answer it risks a pre-existing
save's place permanently. **Banked as unresolved rather than quietly omitted.**

---

## THE ROWS I DID NOT BANK, AND WHY -- THE LARGER HALF OF THE PASS

**1. `jobs` 43, 45, 46 and `profile` N1 -- already COVERED-PROVEN.** Moving them
would have been four rows of pure inflation. See the refuting query above.

**2. `jobs` 103 and 104 -- follow / unfollow a company. STAY COVERED-UNFIRED.**
`follow_company` was attempted today and **REFUSED, twice, identically**: prior
state came back `unknown` from both available sources, and the gate will not
guess which way it would move. **A refusal is not a fire.** The refusal was
re-measured on a second, independent target, so it is the gate's standing
behaviour rather than one posting's quirk. These two rows were moved CP -> CU
only this morning by another wave, on the ground that a PERFORMABILITY verdict
is not a live-fire receipt. **That correction stands. A refusal is even weaker
evidence than the verdict that was rejected**, so moving them back would
contradict a ruling made hours ago on better evidence.

**3. `jobs` 58 -- bulk-unsave. STAYS `n/a`.** LinkedIn ships no such control. A
fire on the single-job path says nothing about a capability that does not exist.

**4. Every EXCLUDED-RULED settings row in `profile` K/M/N, `network` R11 and
`messaging` 3.10 -- UNTOUCHED.** Roughly thirty rows sit under one shipped
ruling: *a setting is admitted by name or not at all*. Dark mode is the single
setting admitted by name, on the operator's own 2026-08-31 ruling, whose words
are *ONE NAMED PAGE AT A TIME, NEVER THE FAMILY, NEVER A WILDCARD.*

> **Firing the one admitted setting is the ruling WORKING. A successful fire on
> an admitted page is not an argument for admitting its neighbours** -- it is
> the strongest available demonstration that admitting one page at a time is
> sufficient. The temptation runs the other way and it is worth naming: the
> fire makes the mechanism feel safe, and *feels safe* is not the test the
> ruling applies.

**5. `M C37` -- unsave a saved POST. STAYS GAP.** The only blocker-map row the
capability query returned. It is the content surface, not the jobs surface; no
tool fired against it and `SAVED-POSTS-SURFACE` is untouched by today's work.

---

## WHAT THE COUNTS DID

Recorded as DELTA notes under each slice's count block, following the
convention already in both files: **the frozen block is left UNCHANGED** so
every document citing those numbers still resolves, and the movement is written
beneath it.

    profile.md    COVERED-PROVEN   19 -> 20     COVERED-UNFIRED   7 -> 6
    jobs.md       COVERED-PROVEN   19 -> 20     COVERED-UNFIRED   9 -> 8

`jobs.md` now carries two deltas for one day pointing in opposite directions --
CP 21 -> 19 this morning, 19 -> 20 this evening. **Both applied the identical
standard.** Two rows left COVERED-PROVEN because their evidence was a gate
verdict; one entered it because it was exercised and read back. A ledger that
only ever moves up is not measuring anything.

**Nothing moved out of GAP. The GAP total is untouched at 311**, and
`blocker-map.tsv` regenerated **byte-identical** -- the correct outcome, since
neither row that moved was GAP at the frozen commit `1c08e5f`. The generator's
four assertions all passed.

---

## SUPERSEDED PROSE, CORRECTED IN PLACE RATHER THAN DELETED

Three standing claims in the census were made false by the fires. Each is
marked superseded with its date, and the original left legible:

    jobs.md      "`unsave_job` -- NO. NEVER FIRED."
    jobs.md      "`unsave_job` is the only PERFORMABLE write with no live fire"
    profile.md   "`update_setting` -- WRITE NEVER FIRED."

**Kept, not deleted.** The reasoning under the second is what made this the safe
write to choose first, and it was accurate for twenty days. A census that erases
its superseded claims cannot show that it was ever wrong, and this one's value
is that it can.
