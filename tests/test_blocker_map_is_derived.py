"""The blocker map must stay DERIVED, and the UNASSIGNED count must only shrink.

WHY THIS TEST EXISTS. `_audit/2026-09-03-linkedin-gap-blockers.md` divided 409
census GAP rows across 97 blockers and published only the counts; the classifier
was never committed, so for two days no per-blocker number here could be
checked. `_audit/_census/blocker-map.tsv` is the recovered part of that mapping.
**A map that can silently stop matching its own evidence is worse than no map --
it manufactures auditability**, which is the exact failure it was built to fix.
So the map is re-derived here from the evidence file and the census, and
compared line for line against what is committed.

THE RATCHET. `UNASSIGNED` may go DOWN -- somebody finding a committed source
that names more rows is the whole point, and this test must not stand in the way
of it. It may not go UP. A rise means evidence was deleted, an id stopped
resolving, or the ledger's tables moved, and every one of those is a thing
somebody should have to look at.

THE DANGEROUS DIRECTION IS ASSERTED SEPARATELY. No blocker may recount HIGHER
than the count the ledger published for it. A map with MORE rows in a set than
the ledger claims means a committed source and the ledger disagree about set
membership; that is a finding to be adjudicated by a person, never a merge to be
absorbed by a script.

SHOWN FAILING in five directions -- an instrument that has only ever been green
certifies nothing. Four were planted before admission; the fifth arrived on its
own an hour later and is the one worth reading:

    delete one evidence line             ratchet + map-drift red
    double-assign an already-mapped row  DOUBLE-ASSIGNED
    plant an id matching no census row   UNRESOLVED
    plant a 2nd row on a 1-row blocker   over-count + map-drift red
    break the ledger table header anchor "blockers the parse does not know"

The fifth was not a mutation. A neighbouring wave appended 19 lines to the
ledger, both its tables slid 28 rows down, and `ledger_counts()` -- then a
hardcoded line window -- lost one of them. See the comment in
`test_no_blocker_recounts_higher_than_the_ledger_published`.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_blocker_map as bbm  # noqa: E402

#: A CEILING, not a pin: see the module docstring. Lowered 306 -> 287 when two
#: further committed blocker-to-row tables were harvested
#: (`2026-09-05-settings-tail.md` section 2.3 and
#: `2026-09-05-routes-already-admitted.md`), then 287 -> 284 when a recall check
#: on the scan found one row list the equality filter had skipped, then
#: 284 -> 278 from a whole-tracked-corpus scan (not ledger-and-amendments only)
#: whose raw 128-CONTRADICTS / 19-NEW output was cut by a proximity-plus-same-
#: paragraph filter to 22 and 6 respectively, then each of the 6 survivors read
#: by hand before being added -- all six RECON-DOC, none the ledger itself
#: (GROUPS-SURFACE M C61/N 63/N 163, SEARCH-RESULTS-SURFACE M C70/N 161,
#: NEWSLETTER-SURFACE N 57). The 22 refined CONTRADICTS were left for a person,
#: not absorbed. Lowering it is the intended direction and requires no
#: ceremony; raising it needs a reason.
#:
#: 278 -> 268 on 2026-09-19, SEVEN rows, three blockers taken from ABSENT to
#: COMPLETE. `M C2` to PUBLISH-POST-AUDIENCE-PARAM (1 of 1) -- amendment A3 is
#: HEADED with the blocker name and states the row verbatim inside it, so the
#: map's "no committed source names this row against any blocker" was false
#: twice over. `M C10` and `M C28` to MENTION-COMPOSITION-RULING (2 of 2) --
#: `2026-09-05-article-publish.md:130` names the pair and ties it to "exactly
#: blocker 16's count of two", and rank 16 IS that blocker. `M C54 C55 C56 C76`
#: to COLLABORATIVE-CONTENT (4 of 4) -- its section 4 enumerates that blocker's
#: four rows in one sentence.
#:
#: ONE OF THOSE SEVEN WAS REPORTED AGAINST THE WRONG BLOCKER AND THIS CEILING IS
#: WHY IT MATTERS. `M C55` was relayed as assignable to MENTION-COMPOSITION-
#: RULING alongside C10 and C28. That blocker publishes TWO rows, C10 and C28
#: close it exactly, and a third would have tripped the over-count assertion
#: rather than this one -- the two guards catch different halves, and the
#: dangerous half is the other one. C55 is a collaborators row, not a mention
#: row.
#:
#: 268 -> 266 on 2026-09-19. `SEARCH-APPEARANCES-SURFACE` recovered at 2 of 2,
#: ABSENT -> COMPLETE, on three committed sources naming the same pair and a
#: count that closes on BOTH axes: the ledger publishes it at 2 rows / 2R, and
#: `N 132` and `P G7` are both R.
#:
#: THAT WAS THE ONLY SURVIVOR OF A 50-BLOCKER SWEEP, and the ratio is the
#: finding rather than the row. Of five candidates whose id count matched the
#: published count, FOUR were junk -- an analogy, two sentence bleeds and a
#: pointer-cited-as-a-set -- each already named as junk by
#: `_audit/2026-09-05-blocker-map.md`, which says in terms that "an exact-count
#: filter cannot tell an analogy from an assignment". **Closing the count is a
#: weak bar at published=1, where any single mention closes it**, and strong
#: only at 2+. Do not raise this ceiling to admit a pub=1 match.
#:
#: 266 -> 259 on 2026-09-19, seven rows, five more blockers off UNLOCATABLE,
#: from a source class the document sweep had EXCLUDED: the census rows' own
#: notes. A row naming its blocker in its own note is a stronger claim than a
#: document mentioning both, and it is the class that produced `N 194`'s
#: "Blocker: no people search".
#:
#:   MENTION-TAG-CONTROLS   M C87 C88 C89   3 of 3   count AND 3W both close
#:   NO-URL-AT-ALL          P N25           1 of 1   an explicit RE-FILE
#:   ADD-SECTION-MENU       P D25           1 of 1   moderate, R/W carries it
#:   SAVED-POSTS-SURFACE    M C36           1 of 2   partial
#:   ARTICLE-SURFACE        M C48           1 of 6   weakest; C48 is the only R
#:
#: **HAND-READING CHANGED THREE OF EIGHT CANDIDATES**, which is why the notes
#: carry a stated STRENGTH. `M C87` looked like a MENTION-TAG-CONTROLS hit and
#: its note is an argument for filing it ELSEWHERE; taking the mechanical match
#: would have recorded an exclusion as an assignment.
#:
#: 259 -> 247 on 2026-09-19. Twelve lines handed over by the profile-modals
#: wave, verified before pasting rather than inherited:
#:
#:   CONTACT-INFO-PANEL            P A25-A29   5 of 5   count AND 1R/4W close
#:   INTRO-EDITOR-UNREAD-CONTROLS  P A9 A14 A15 A22   4 of 4   elimination, re-run
#:   OPEN-TO-HIRING-MODAL          P J1-J3     4 of 5 with J4   PARTIAL
#:
#: **ELEVEN MORE WERE HANDED OVER AND REFUSED.** `P I2`-`P I12` were
#: EXCLUDED-RULED at the frozen commit AND are EXCLUDED-RULED today -- they
#: never moved, so they were never in the 409-row set the ledger divided, and
#: `test_the_evidence_resolves_and_no_row_carries_two_blockers` would have
#: refused them. The handing wave checked for DUPLICATES, which is a different
#: check and cannot see this: a row can be unique and still not be in the
#: denominator.
#: 247 -> 246. `JOB-COLLECTIONS-SURFACE` recovered at 1 of 1 on APPOSITION --
#: "JOB-COLLECTIONS-SURFACE (J 42) is one row..." -- plus a 1R/1R split match.
#: The count axis is vacuous at published=1 and is NOT what carries that line.
#: 246 -> 243, from a THIRD instrument: a LINE-SCOPED scan of markdown TABLE
#: ROWS carrying exactly one blocker name. The paragraph-scoped scan cannot
#: resolve inside a table, because a whole table is one paragraph and its
#: "nearest blocker name" filter then picks a neighbouring row's blocker --
#: which is the rank-table-scrape junk shape this corpus already records.
#:
#:   NEWSLETTER-SURFACE      N 58    named by SHIPPED CODE (readonly.py:708)
#:   SEARCH-RESULTS-SURFACE  N 179   a contested row, conceded by the claimant
#:   SERVICES-PAGE-SURFACE   P H9    named in the blocker's composition, 11->10
#:
#: THREE MORE WERE FOUND AND LEFT: N 55, N 56 and M C80 are named by the same
#: shipped comment and are on the sweep's three-way self-conflict list.
#: Adjudicating a three-way claim is a RULING, not a recovery.
#: 243 -> 232. Blocker 20 `OPEN-TO-WORK-MODAL` recovered at 11 of 11, ABSENT
#: -> COMPLETE, and it REPLACES eleven lines refused at `3a1e2df`. Those named
#: `P I2`-`I12`, EXCLUDED-RULED AT THE FROZEN COMMIT and so never in the
#: 409-row set. The real rows are `J 92`-`J 98` + `P I13`-`I16`.
#:
#: THE SOURCE IS ITSELF A CORRECTION -- Amendment E is headed "SECTION 1 IS
#: WRONG. Blocker 20 is not a closed door" and retracts its own document's
#: headline. That class keeps earning its rank: `article-publish`'s "THE CAVEAT
#: RESOLVED, AGAINST ME" carried MENTION-TAG-CONTROLS the same way.
#:
#: The blocker reads LIVE at 5 still-GAP rows, not 11: `539752b` moved J 92-97
#: to EXCLUDED-RULED mid-session. MEMBERSHIP is a fact about the FROZEN set;
#: `state_today` is a separate column and moves under you.
#: 232 -> 217, the largest single recovery of the campaign. ADMIN-RIGHTS-NOT-HELD
#: at 15 of 15, ABSENT -> COMPLETE, found by a STRUCTURAL enumerator (census
#: SECTION, not a word list) after the lexical one proved lossy on blocker 20.
#:
#: It closes on four independent axes: a committed source saying the family is
#: "already true of ALL FIFTEEN" and arguing to move "the TABLE WHOLESALE"; the
#: ledger's own reason enumerating the section's three families ("administers no
#: Page, owns no group, organises no event"); the count; and COMPLETENESS -- no
#: other N A-row exists in the frozen set at all.
#:
#: CONTRAST WITH BLOCKER 20, which is why the enumerator matters: there the same
#: method found THIRTEEN candidates for ELEVEN slots, so that set does NOT close
#: by elimination and its lines say so. Here it does, and the difference is
#: measured rather than assumed.
#: 217 -> 207. SERVICES-PAGE-SURFACE at 11 of 11, ABSENT -> COMPLETE. Same
#: structural enumerator; the discriminator is that the section NAME and the
#: blocker NAME agree, which is what separates a real match from the 26 other
#: size coincidences the sweep produced.
#:
#: Count AND R/W close: section H is 1R + 10W, the ledger publishes 1R/10W, and
#: two sources state the split in prose ("TEN WRITES GATED, UNFIRED"; "11 rows
#: as filed and 10 as ruled: 1R + 9W" -- arithmetic that only works if the
#: ruled-out row is one of the W, which P H9 is).
#:
#: THE SWEEP'S CONTESTS ON H1/H2/H10/H11 DISSOLVE ON PUBLISHED COUNTS, not on
#: preference: INVITE-NOTE-PARAM publishes ONE row and is claimed against four;
#: HASHTAG-EXISTENCE publishes three and A13 already named all three, none a
#: profile row, so it can hold zero.
#: 207 -> 201. RECOMMENDATIONS-SURFACE at 6 of 6, ABSENT -> COMPLETE. Section F
#: is 1R+5W and the ledger publishes 1R/5W; F3 F4 F5 were already EXCLUDED-RULED
#: at the frozen commit and are correctly outside the denominator.
#:
#: ACCOUNT-VERIFICATION was the other name-plus-count match and is NOT taken: it
#: is blocker 20's shape again. Its verification rows K1-K7 were EXCLUDED-RULED
#: AT THE FREEZE, so the only frozen-GAP section-K rows are BADGE rows (K8 K9
#: K10). Reported, not assigned.
#: 201 -> 178, the largest single recovery of the campaign. GROUPS-SURFACE to
#: 30 of 32, and it RESOLVES A DISCREPANCY ITS OWN SOURCE DECLARED
#: IRRECONCILABLE: that document walks the group family to 35 against a
#: published 32 and says "No subset of the 35 reconciles to 32 by any rule I
#: can state", calling its exclusion candidates guesses.
#:
#: The rule it could not state is that three of its 35 are ADMIN rows -- its
#: table counts N A10 A11 A12, assigned to ADMIN-RIGHTS-NOT-HELD at 5509166 on
#: four independent axes. 35 - 3 = 32 exactly. A recovery in one blocker
#: reconciled another, which is an argument for doing them in one pass.
#:
#: RESIDUAL: 30 not 32, because N 161 and M C70 are in the same walk and filed
#: to SEARCH-RESULTS-SURFACE -- carved out by that same document. Left open.
#: 178 -> 162. EVENTS-SURFACE to 17 of 18, and it is the strongest source in
#: the recovery because it ENUMERATES THE LEDGER'S OWN SET AND THEN CLOSES ITS
#: OWN ARITHMETIC. _audit/2026-09-05-events-surface-recosted.md section 1
#: recovers blocker 13's rows from _route-gap-rows.tsv and accepts them only
#: because the derivation reproduces the ledger's arithmetic exactly -- not
#: merely the 18, but the 7R/11W SPLIT. A candidate set that reproduces a
#: two-way split of a published count is not a plausible set, it is the set.
#:
#: Section 5 then carries exactly 18 table rows, one per id, and section 6
#: totals them: MISFILED 3 + EXCLUDED-RULED-ALREADY 4 + MEASURED-ABSENT 3 +
#: against-this-surface 8 = 18, every row named in the total.
#:
#: RESIDUAL: 17 not 18. N 179 is filed to SEARCH-RESULTS-SURFACE by THIS SAME
#: DOCUMENT, at the line that assignment cites. The two agree, so the
#: under-count is the agreement rather than a gap.
#:
#: NOTHING IS RETIRED BY THIS. Fourteen of the seventeen carry a verdict there
#: that would move them out of GAP and not one is enforced by a shipped rule --
#: the four EXCLUDED-RULED rest on readonly.py's admission COMMENT, prose in a
#: source file, which nothing can be shown failing against. They stay GAP and
#: the map records where the ledger counts them.
#: 162 -> 145. SEARCH-RESULTS-SURFACE COMPLETE at 21 of 21, the last big
#: blocker, and it was found by FIXING THE ENUMERATOR A SECOND TIME.
#: 2026-09-05-search-results-consent.md scored 3 on every earlier sweep and
#: names 18 unassigned rows, because it writes its set as a DASH RANGE --
#: `N 79-95` is seventeen rows and the pattern saw two. Same defect as the
#: word list: an approximate reader over a structured notation.
#:
#: Its section 4 closes its counts twice. By row: N 79-95 (17R) + 2
#: unattributed (2R) + N 96 (1W) + N 4 (1W) = 21. By SPLIT: 19R/2W, the
#: ledger's published split exactly. The 17 decomposes to its own prose too
#: -- person + People + 13 filters + multi-location + recent = 17.
#:
#: THE TWO IT COULD NOT ATTRIBUTE WERE CLOSED FROM OUTSIDE. It offers three
#: candidates for two slots (N 104, N 161, N 179), which does not eliminate.
#: The groups document gave N 161 to this blocker by name and the events
#: document gave N 179; both were filed here before this source was read, so
#: the fit is not one I arranged. N 104 is the leftover and stays out.
#:
#: THE TWO IT OVER-CLAIMS SETTLE THE COUNT. Its 17R block ends at N 95 and
#: its 1W line is N 96; both are held by SEARCH-HISTORY-SURFACE, which
#: publishes exactly 2 and is COMPLETE holding exactly those two. The source
#: half-concedes it -- of N 96 it says "It is a re-file, not a decision."
#: So the block is sixteen rows, and with that the blocker closes on the
#: nose: 16 + N 4 + the two carve-ins + the two post-freeze re-files (N 194
#: by Amendment A13, M C70 by the groups document) = 21 of 21.
#:
#: THE SPLIT IS NOT CLAIMED FOR THE POST-FREEZE SET. The published 19R/2W
#: describes the FROZEN set, which held N 95 and N 96. Giving those back and
#: taking in two re-files moves the split while leaving the count alone --
#: which is what a re-file does, and A13 says it itself ("taking the
#: ledger's own figure to 22"). The count is the check that survives.
#: 145 -> 133. THREE BLOCKERS GO FROM EMPTY TO COMPLETE IN ONE PASS, off a
#: vein this recovery had not mined: COMMITTED SOURCE FILES. A probe script's
#: comment block names the ledger ROW NUMBER, the blocker NAME and the ROW
#: SET on one line, sitting directly above the addresses it exercised.
#:
#:   scripts/_probe_jobs_tail_boundary.py
#:     # 36 JOB-ALERTS-SURFACE -- census rows J31-J36 and J41, all writes.
#:     # 62 TRACKER-ROW-MENU   -- census rows J54-J56.
#:   scripts/_probe_small_measures_live.py
#:     ALL-FILTERS-PANEL (2 rows: J15, J16)
#:
#: JOB-ALERTS-SURFACE ANSWERS A DECLINE I MADE AT 11:02 ON ITS OWN TERMS. I
#: refused it because section B holds NINE unassigned rows against seven
#: slots and jobs.md CARRIES NO R/W COLUMN, so picking the seven writes would
#: have been my reading rather than a source's. The comment names which seven
#: AND makes the write claim itself. The split is no longer mine.
#:
#: PREMIUM-APPLY-SURFACES IS DECLINED AGAIN FROM THE SAME COMMENT BLOCK, and
#: the consistency is the point: it names J78-J83, which is SIX against a
#: published FIVE, and unlike the alerts line it makes no R/W claim. Only
#: row 82 ("Observe the Easy Apply daily limit") is unambiguously the 1R;
#: choosing which of the five writes leaves would be my inference, which is
#: the ground the alerts decline stood on. Reported, not assigned.
#: 133 -> 123. NEWSLETTER-SURFACE COMPLETE at 12 of 12 from SHIPPED PACKAGE
#: CODE -- readonly.py's boundary comment, which is load-bearing for the
#: entry it documents rather than a retrospective reconstruction. It
#: enumerates the blocker in three named halves: reader-side 5 (N 55-58,
#: M C80, as "this blocker's reader-side rows"), author-side 5 (M C50,
#: C51, C81, C84, P L3, "newsletters he WRITES"), analytics 2 (M C83,
#: P L4). 5 + 5 + 2 = 12, the published count.
#:
#: THE 1R/11W SPLIT IS NOT CONTRADICTED although it reads as if it is:
#: reader-side is a ROLE (newsletters he reads vs writes), not an operation
#: class, and unsubscribing from one he reads is still a write.
#:
#: THIS OVERTURNS MY OWN RESTRAINT AT 990bbd3 -- "N 55, N 56 and M C80 are
#: on the sweep's three-way self-conflict list. Adjudicating a three-way
#: claim is a RULING, not a recovery." That was right then. All three rivals
#: are now dead by MEASUREMENT: EVENTS-SURFACE and GROUPS-SURFACE each
#: enumerate their own full row set and name all ten of these rows ZERO
#: times (measured, whole file, both documents); OWNED-BY-A-SIBLING-SLICE is
#: COMPLETE at 4 of 4 on rows the ledger names explicitly, N 149 150 151 160.
#: Neither document rival lost the argument -- neither ever made the claim.
#: The sweep itself records the claims arising from one A9-adjacent passage
#: where those names sit near these ids, which is the junk shape the
#: evidence file's own header warns about.
#: 123 -> 120. CREATOR-HUB-SURFACE to 3 of 4, and the point of this entry is
#: the row it REFUSES. profile.md section L ("Creator tools, followers and
#: analytics") holds exactly FOUR unassigned frozen-GAP rows against a
#: blocker published at 4 -- an exact count match, and it is WRONG. The
#: ledger publishes 4R, all reads, and the census's own R/W column makes L6
#: ("Audio events") a W. A bare count match is a birthday problem; the
#: split is the discriminator, and here it disqualifies the row the count
#: would have admitted. This is the same test JOB-ALERTS passed and
#: PREMIUM-APPLY-SURFACES failed, applied to a fit I wanted.
#:
#: THE FOURTH READ IS NOT TAKEN. The only other section-L reads GAP at the
#: freeze are held: P L4 by NEWSLETTER-SURFACE on shipped code, P L2 by
#: PARSER-ON-A-LOADED-PAGE. Either closes this at 4; taking one would
#: overturn an existing assignment on a weaker source, which is a ruling.
#:
#: AND THE LIKELIEST FOURTH CANNOT BE FILED AT ALL: P L2b ("Own follower
#: LIST") is GAP today and is NOT in the frozen set -- split out of the
#: compound L2 on 2026-09-04, the day AFTER the freeze. If the published 4R
#: counted the compound row, this under-count is an artifact of a split that
#: postdates the count, and no map edit can reach it.
#: 120 -> 113. COMPANY-PAGE-SURFACE to 8 of 18 on a SIBLING argument, not a
#: name match: J 107 ("Company Page Jobs tab") is already filed to this
#: blocker from routes-already-admitted.md's "filed as" column, and the
#: seven added are its immediate siblings in the same census run, each
#: spelled "Company Page <x> tab" in the capability column. jobs.md
#: section 2 groups the whole run as one shape and marks it R, against a
#: blocker published 13R/5W.
#:
#: J 112 IS LEFT OUT DELIBERATELY -- "School Page Alumni tab", the one row
#: in the run that is not a Company Page. SCHOOL-PAGE-SURFACE is its own
#: published blocker and is empty. The group's own title says "company AND
#: school", so the group is a SHAPE, not a blocker.
#:
#: AND THIS RECORDS A CORRECTION TO MY OWN COMMIT c1a2a46, which said
#: "jobs.md CARRIES NO R/W COLUMN" as the ground for declining
#: JOB-ALERTS-SURFACE. That was true of section 1's table and WRONG about
#: the file: section 2 carries R/W, and its grouping row reads
#: "31-36, 41 | all alert writes" -- the exact seven, named by the census
#: itself. The assignment I made from the probe comment is right and now has
#: a second independent source; the REASON I gave for having declined it
#: earlier was not. Found via a sibling's amendment 5bdebba.
#: 113 -> 110. THREE ONE-ROW BLOCKERS CLOSE, and the instrument's test is
#: UNIQUENESS rather than similarity -- the retire-rulings wave's own
#: deflation is that a singleton's R/W split is a two-bit check, so these
#: rest on capability text being unique in the corpus. Required a MUTUAL
#: BEST MATCH: the blocker's best row beats every other unassigned row AND
#: that row's best blocker beats every other blocker with room. Of THIRTEEN
#: one-row empty blockers, three survived; ten are reported, not filed.
#:
#:   POST-DRAFT-SURFACE     M C12  "Save a post as a draft"   W vs 1W
#:   PROFILE-PDF-DOWNLOAD   P C8   "Save profile as a PDF"    R vs 1R
#:   AUDIO-EVENTS-EXISTENCE P L6   "Audio events"             W vs 1W
#:
#: M C12 scores 1.00 -- it covers every token of its blocker's name.
#:
#: P C8 IS THE AMBIGUOUS-ID TRAP ITSELF: there are two C8 rows, M C8
#: ("Create a poll", W) and P C8 ("Save profile as a PDF", R). The
#: matcher takes the slice letter from the FILE, and the split settles it
#: independently -- a 1R blocker cannot hold the poll write.
#:
#: P L6's only rival is measured out, not out-argued: EVENTS-SURFACE scores
#: on the shared token "events" and has room 1, but its row set is
#: enumerated in full by its own document, which names L6 zero times and
#: contains "audio" zero times. And L6 is the row REFUSED from
#: CREATOR-HUB-SURFACE at f461e9c for being a W against 4R -- the same
#: split that excluded it there admits it here.
#: 110 -> 105. SCHOOL-PAGE-SURFACE 3 of 3 and POLL-SURFACE 2 of 2, both
#: EMPTY -> COMPLETE, by the singleton test generalised to k rows: the top
#: k rows must each name this blocker as their own best, there must be a
#: strict score gap to row k+1, and the R/W split must match the ledger's.
#: The split is checked rather than reported afterwards, because a perfect
#: count match with a wrong split is what CREATOR-HUB-SURFACE turned out
#: to be.
#:
#: SCHOOL-PAGE-SURFACE: three rows at 1.00, next row 0.50, 3R vs published
#: 3R. A THIRD AXIS AGREES -- the ledger charges "allowlist +1" and N 99's
#: census note says what the missing pattern is: "No /school/ pattern; 0
#: grep hits for /school/". Published cost and measured absence are the
#: same fact from opposite ends.
#:
#: AND J 112 IS HERE BECAUSE I CARVED IT OUT AT 5d06446, where I left it
#: out of COMPANY-PAGE-SURFACE as the one row in that census run that is
#: not a Company Page. Taking the run whole would have left this blocker
#: empty permanently.
#:
#: POLL-SURFACE: both rows 1.00, next 0.00 -- the widest edge in the field
#: -- 2W vs published 2W. M C8 "Create a poll", NOT P C8 "Save profile as
#: a PDF" which went to PROFILE-PDF-DOWNLOAD one commit earlier. The two
#: C8s land in different blockers in adjacent commits: the ambiguous-id
#: hazard, met twice in five minutes.
#: 105 -> 99. MESSAGE-REQUESTS-SURFACE 4 of 4 and RESUME-TOOLS-SURFACE 2 of
#: 2, both EMPTY -> COMPLETE, and both rest on the SPLIT rather than on the
#: name score.
#:
#: MESSAGE-REQUESTS-SURFACE, published 1R/3W: M6 Send (W), M7 Accept (W),
#: M8 Decline (W), M9 Review previously declined (R). Exactly 1R/3W.
#: THE SCORER TIED EIGHT ROWS HERE and that is a defect in the scorer, not
#: an ambiguity in the corpus: a bag-of-words normalised over the blocker's
#: own tokens weights "message" and "requests" EQUALLY, and "message"
#: is everywhere in that slice. Of the eight, exactly these four contain
#: the word request. Recorded because the next similarity match will hit it.
#:
#: RESUME-TOOLS-SURFACE, published 1R/1RW: a blocker published 1R/1RW needs
#: a row that is literally R/W, and the R/W class is rare here. P M11
#: "Resume Builder" is R/W, P M12 "Resume Tips" is R. Both carry the
#: same census reason verbatim, which is the census recording them as one
#: unresolved pair.
#:
#: THE MESSAGE-REQUESTS DECLINE IS OVERRIDDEN, NOT CONTRADICTED. I reported
#: it undecidable on messaging-rows.md section 3a -- "there is no list" --
#: which remains TRUE: no source LISTS these ids. This is a reconstruction
#: from the census, the weaker class this map is built on throughout,
#: admitted on split + discriminating word + contiguity. The blocker named
#: in that same sentence, CONVERSATION-OVERFLOW-MENU, still does not close
#: -- only 6 of its 10 have any signal -- and stays declined.
#: 99 -> 90. FEED-ITEM-OVERFLOW-MENU 5 of 5 and COMMENT-IDENTIFIER 4 of 4,
#: argued as ONE SIMULTANEOUS PARTITION rather than two fits. Both draw on
#: overlapping pools and both claim N 148 "Report a post or a comment in
#: your feed". Only one assignment of that row makes EITHER count land,
#: and it makes BOTH land: N 148 in the feed menu gives 5 and 4; N 148 in
#: the comment blocker gives 4 and five-candidates-for-four. Neither
#: closes. The wrong assignment is refuted by arithmetic, not preference,
#: and the row's own text settles it anyway by saying WHERE -- in your feed.
#:
#: The feed five are that menu's actual contents -- Hide, Hide, Unfollow,
#: Mute, Report -- all W against 5W. The comment four are the operations
#: that require naming WHICH comment, which is what the blocker IS: hide,
#: reply, edit, react, all W against 4W.
#:
#: THE INSTRUMENT THAT FOUND THIS IS BLIND TO THE JOBS SLICE, and that is
#: stated so the result is not read as stronger than it is: only 5 of 37
#: unassigned jobs rows carry a parsable R/W (jobs.md's main table has no
#: R/W column) against 23 of 23 in network.md. Its uniqueness is uniqueness
#: among non-jobs rows. It produced two absurd hits for exactly that reason
#: -- it offered "#Hiring photo frame apply / remove" for
#: EASY-APPLY-MULTISTEP, on the token "apply". Both refused.
#:
#: POST-COMMENT-CONTROLS is untouched: 15 candidates for 4 slots, 1R/3W.
#: 90 -> 89. CELEBRATION-COMPOSER 1 of 1 on M C9, and the interesting part
#: is WHY it was not decidable an hour ago. The mutual-best test asks that
#: the row's best blocker be this one among blockers WITH ROOM. M C9 named
#: POST-DRAFT-SURFACE as its best and the pair failed. POST-DRAFT-SURFACE
#: closed at 5dc71d5 on M C12, left the open set, and the pair became
#: mutual. The evidence did not change; the FIELD did. Second cascade of
#: this recovery -- the first was J 112, carved out of COMPANY-PAGE-SURFACE
#: and then closing SCHOOL-PAGE-SURFACE.
#:
#: UNIQUENESS MEASURED, NOT ASSERTED: "celebrat" appears four times in the
#: census and exactly one is a capability that IS a celebration. C33
#: ("Choose WHICH reaction (Celebrate, Support, Love...)") would have been
#: taken by a substring match; reading what the capability DOES excludes it.
#: 89 -> 85. CONTENT-ANALYTICS-SURFACE to 4 of 5, published 5R.
#: The split does the selecting again and excludes a row the name score
#: wanted: M C46 "Embed content within an article" ties at the top and is
#: a W, so a 5R blocker cannot hold it. The four that remain are all R and
#: all analytics. M C38's census note names an /analytics/creator/ address,
#: which is the allowlist +1 the ledger charges -- cost and measured
#: address agreeing from opposite ends, as with SCHOOL-PAGE-SURFACE.
#: The fifth is NOT guessed: every other analytics row is already filed on
#: a stronger source (P L1, P L8 by census section; P L4 by shipped code).
#:
#: BADGES-SURFACE IS DECLINED, AND THE REASON IS A DUPLICATED CAPABILITY.
#: Published 2R/3W with SIX candidates: K8 (R), K10 (R), B7 (W), B8 (W),
#: B9 (W), K9 (W). The two reads are forced, but four writes compete for
#: three slots -- and B8 "Top Voice badge show / hide" and K9 "Show /
#: hide the Top Voice badge" are THE SAME CAPABILITY in two slices. Which
#: id the lost classifier used is exactly the substitution risk the
#: retire-rulings wave flagged for M 24 / M 42, and it called that a
#: RULING. Reported, not assigned.
#: 85 -> 76. SERVED-BY-GMAIL-SKILL 6 of 6, SAVED-POSTS-SURFACE 2 of 2,
#: ARTICLE-SURFACE 5 of 6.
#:
#: SERVED-BY-GMAIL-SKILL IS THE STRONGEST SHAPE THIS RECOVERY FOUND: a
#: STRUCTURAL MARKER IN THE CENSUS'S STATE COLUMN. jobs.md writes the state
#: of rows the linkedin-jobs skill serves as GAP `SKILL`. Counted
#: mechanically, exactly SIX carry it -- 37 38 39 40 57 131 -- against a
#: published 6. And the near miss is excluded BY THE DATA: J 127 carries
#: the SKILL tag but reads MEASURED-ABSENT `SKILL`. Tag alone gives seven;
#: tag plus state gives exactly six.
#: Note what the blocker IS: filed NOT-OURS, "available to him today
#: through linkedin-jobs, with no LinkedIn session at all". Locating these
#: schedules nothing -- it records that six of the 409 are already served.
#:
#: ARTICLE-SURFACE at 5 of 6 with the shortfall's candidates ENUMERATED:
#: C44, C47, C77 are not in the frozen set (EXCLUDED-RULED at the freeze),
#: C45 is filed to FILE-UPLOAD-UNSANCTIONED and C76 to COLLABORATIVE-
#: CONTENT. So the sixth is one of those two on a ruling I am not making,
#: or lies outside the article family.
#: M C46 arrives here having been REFUSED from CONTENT-ANALYTICS-SURFACE in
#: this same pass for being a W against 5R -- the split earning its keep in
#: both directions, as L6 did between CREATOR-HUB and AUDIO-EVENTS.
#:
#: SAVED-POSTS-SURFACE: the census pairs its two rows itself -- C37 cites
#: the same Help source as C36 (its evidence cell reads literally "same")
#: and records "COST CORRECTED 2026-09-19 with C36".
#: 76 -> 74. COMPANY-PAGE-SURFACE to 10 of 18, on the census's own BLOCKER
#: CELL rather than a name match: N 101 and N 102 both read "No /company/"
#: as their reason, and the ledger charges this blocker allowlist +1 -- the
#: /company/ pattern. THIRD time in this recovery that a published cost and
#: a measured absence are the same fact from opposite ends (SCHOOL's
#: /school/, CONTENT-ANALYTICS's /analytics/creator/, now this).
#: N 102 "employee insights on a Page's People tab" is also the same tab
#: as J 108 "Company Page People tab", already filed here at 5d06446.
#:
#: N 104 IS DELIBERATELY NOT TAKEN: a company row by subject, a SEARCH row
#: by act, and named by search-results-consent.md as one of three candidates
#: for that blocker's two unattributed slots. I left it out of
#: SEARCH-RESULTS-SURFACE at 68949ea and will not take it here on a weaker
#: argument than the one I declined to use there.
#:
#: HASHTAG-EXISTENCE NEEDS NOTHING, and the near miss is worth recording:
#: the matcher offered N 59 "Follow a hashtag" + N 60 "Unfollow a
#: hashtag", a clean 2-row fit for room 2. It is WRONG. The ledger names
#: this blocker's three rows EXPLICITLY -- N 194, C 11, C 52 -- and all
#: three are already placed: N 194 to SEARCH-RESULTS-SURFACE, M C11 held
#: here, M C52 to FEED-PREFERENCES on a 2026-09-19 correction. A correctly
#: dispersed set, not an under-count. LEDGER-EXPLICIT beats a name-plus-
#: split match, and this is the one place today the matcher would have
#: written a wrong row had the ledger not been read first.
#: 74 -> 72. PREMIUM-READER-NOT-BUILT 1 of 1 and PEOPLE-FOLLOW-LISTS 4 of 4,
#: both COMPLETE, found by a co-occurrence sweep over EVERY tracked file --
#: a row id and exactly ONE open blocker's name within three lines.
#:
#: PREMIUM-READER-NOT-BUILT: 2026-09-19-read-tail.md section 5 opens a
#: bullet "PREMIUM-READER-NOT-BUILT (J127)" and concludes "Correctly
#: still GAP" -- a source asserting membership while arguing against its
#: own convenience. 1R published, and the row is "Read the InMail credit
#: balance". Its state TODAY is MEASURED-ABSENT; the map enumerates the
#: FROZEN set, as with J 15. It is also the row excluded from
#: SERVED-BY-GMAIL-SKILL this morning for reading MEASURED-ABSENT `SKILL`
#: rather than GAP `SKILL` -- the row that made that count work has a home.
#:
#: PEOPLE-FOLLOW-LISTS: N 44 is named inside the blocker's own probe block,
#: headed "# --- 52 PEOPLE-FOLLOW-LISTS ---" with the ledger's row number,
#: as ("FOLLOW-LISTS", "N 44 / P L2b", "R", .../people-follow/
#: followers/). The split closes exactly: N 38 R, N 39 R, N 40 W, N 44 R =
#: 3R/1W published. Its rival is extinguished by ITS OWN COUNT --
#: SERVICES-PAGE-SURFACE is complete at 11 of 11 and cannot hold another
#: row without tripping the over-count guard, so the sweep's unadjudicated
#: two-way conflict is settled by arithmetic elsewhere.
#: 72 -> 71. ANALYTICS-CONTROLS-UNPRESSED 4 of 4, COMPLETING A SET THE
#: LEDGER ITSELF CALLED PARTIAL. N 133's evidence line is LEDGER-EXPLICIT on
#: the ledger's sentence "N 136 is therefore filed with N 133 134 under
#: ANALYTICS-CONTROLS-UNPRESSED", and it records its own shortfall --
#: "PARTIAL -- three of a published four". The fourth has been sitting in
#: a committed probe since 2026-09-05:
#:   ("P O3 N 133 N 134 N 136", "the profile-views page with a filter in
#:    the url", .../analytics/profile-views/?timeRange=past_90_days)
#: Four ids, one label, one url -- the grouping the code was AIMED at.
#: P O3 "WVYP Premium insights and filters" is the profile slice's name for
#: what the three network rows enumerate, it is marked R, and the ledger
#: publishes 4R.
UNASSIGNED_CEILING = 71
FROZEN_GAP_ROWS = 409
LEDGER_BLOCKERS = 97


@pytest.fixture(scope="module")
def built():
    return bbm.build()


def test_the_evidence_resolves_and_no_row_carries_two_blockers(built):
    _gap, _current, _assign, problems = built
    assert problems == [], (
        "the assignment evidence no longer resolves against the census. Each "
        "line names the exact defect -- an id that matches no census row, an id "
        "that was not GAP at the freeze, or a row claimed by two blockers, "
        "which the ledger's own rule forbids (one blocker per row, the earliest "
        "binding constraint)."
    )


def test_the_frozen_row_set_is_still_the_set_the_ledger_divided(built):
    gap, _current, _assign, _problems = built
    assert len(gap) == FROZEN_GAP_ROWS, (
        f"the frozen census at {bbm.FROZEN_REF} now enumerates {len(gap)} GAP "
        f"rows, not {FROZEN_GAP_ROWS}. That commit is history and cannot have "
        "changed, so this means the ENUMERATOR changed -- which invalidates "
        "every per-blocker comparison in the map until somebody re-derives it."
    )


def test_the_ledger_tables_still_total_97_blockers_and_409_rows():
    published = bbm.ledger_counts()
    assert len(published) == LEDGER_BLOCKERS, (
        f"parsed {len(published)} blockers out of the ledger's tables, not "
        f"{LEDGER_BLOCKERS}. Either the tables were edited or the parse broke; "
        "the map's diff is meaningless against a set it cannot read."
    )
    assert sum(published.values()) == FROZEN_GAP_ROWS


def test_unassigned_only_ever_shrinks(built):
    gap, _current, assign, _problems = built
    unassigned = len(gap) - len(assign)
    assert unassigned <= UNASSIGNED_CEILING, (
        f"{unassigned} rows are UNASSIGNED, up from {UNASSIGNED_CEILING}. The "
        "map recovers row->blocker assignments from committed sources; a RISE "
        "means evidence was removed or stopped resolving. If a source was "
        "genuinely retracted, lower the ceiling deliberately and say why -- do "
        "not raise it to clear this."
    )


def test_no_blocker_recounts_higher_than_the_ledger_published(built):
    _gap, _current, assign, _problems = built
    published = bbm.ledger_counts()
    recount: dict[str, int] = {}
    for blocker, *_rest in assign.values():
        recount[blocker] = recount.get(blocker, 0) + 1
    # SEPARATE THE TWO CAUSES BEFORE REPORTING EITHER. A blocker absent from the
    # parse is not a blocker published at zero, and collapsing them makes a
    # PARSER failure wear a DATA disagreement's costume. Measured 2026-09-05:
    # a neighbouring wave appended 19 lines to the ledger, the cost-0 table slid
    # out of a hardcoded line window, and four blockers read as published 0 --
    # this assertion fired and named the wrong cause. It names both now.
    unknown = sorted(b for b in recount if b not in published)
    assert unknown == [], (
        f"the map holds blockers the ledger parse does not know at all: "
        f"{unknown}. Before treating this as a disagreement, check that BOTH "
        "ledger tables still parse -- `build_blocker_map.ledger_counts()` "
        "locates them by header row, and a renamed or reformatted header "
        "returns a partial parse rather than an error."
    )
    over = {b: (n, published[b]) for b, n in recount.items() if n > published[b]}
    assert over == {}, (
        f"these blockers hold MORE rows in the map than the ledger published "
        f"(map, published): {over}. That is a committed source and the ledger "
        "disagreeing about which rows are in a set. It is a finding for a "
        "person to adjudicate, not a number to absorb -- do not widen the "
        "published count to clear it."
    )


def test_the_committed_map_still_matches_what_the_evidence_derives(built):
    gap, current, assign, _problems = built
    committed = bbm.MAP_OUT.read_text(encoding="utf-8", errors="replace").splitlines()
    assert committed, "the map file is empty or missing"
    assert len(committed) - 1 == len(gap), (
        f"the committed map holds {len(committed) - 1} data lines against "
        f"{len(gap)} frozen GAP rows. Re-run "
        "`scripts/build_blocker_map.py --write`."
    )
    got = {}
    for line in committed[1:]:
        parts = line.split("\t")
        got[parts[0]] = (parts[1], parts[2])
    drift = []
    for rid in gap:
        want_b, want_k = (assign[rid][0], assign[rid][1]) if rid in assign \
            else ("UNASSIGNED", "UNASSIGNED")
        if got.get(rid) != (want_b, want_k):
            drift.append((rid, got.get(rid), (want_b, want_k)))
    assert drift == [], (
        f"{len(drift)} rows in the committed map no longer match what the "
        f"evidence derives, first three {drift[:3]}. The map is a DERIVED "
        "artifact: fix the evidence file, then re-run "
        "`scripts/build_blocker_map.py --write`. Never hand-edit the map."
    )


def test_the_state_today_column_reproduces_the_shipped_gap_total(built):
    """The map's two state columns must still close on the live count.

    409 frozen, less those that left, plus those that entered, is what
    `count_census_states.py` reports today. If this drifts, the map's
    `state_today` column has gone stale and the file is quietly claiming
    a reconciliation it no longer performs.
    """
    gap, current, _assign, _problems = built
    left = sum(1 for k in gap if current.get(k, "ROW-GONE") != "GAP")
    entered = [k for k, v in current.items() if v == "GAP" and k not in gap]
    derived = len(gap) - left + len(entered)
    live = sum(1 for v in current.values() if v == "GAP")
    assert derived == live, (
        f"the map reconciles to {derived} but the census holds {live} GAP rows "
        "today. Re-run `scripts/build_blocker_map.py --write`; the "
        "`state_today` column is stale."
    )
