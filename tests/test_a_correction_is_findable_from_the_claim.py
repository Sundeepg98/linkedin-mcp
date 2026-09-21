"""A correction can name what it corrects. A corrected document cannot name its
corrector -- so THE ARROW ONLY POINTS ONE WAY, and every reader who starts at
the claim reaches the wrong document first.

THE INSTANCE, three documents in ``_audit/``:

1. ``2026-08-22-parity-linkedin.md:18`` ranked skill endorsement counts as the
   smallest real win left, at **0 extra page loads**. Reasonable when written.
   Nobody had opened the page.
2. ``2026-08-23-build-linkedin.md:229`` corrected it THE NEXT DAY, by name and
   with a measurement -- *"That is mis-specified, measured"*: the committed
   capture carries ZERO endorsement counts, so the build needs a fresh live
   load and a re-freeze, not zero.
3. ``_audit/_census/network.md:365`` and ``2026-09-03-linkedin-gap-blockers.md``
   (section 5, and A7 under the heading WHAT DID NOT CHANGE) then RESTATED the
   original claim, citing the parity audit by path and never the file that had
   corrected it. A wave was dispatched on that basis to build something that
   does not exist.

Every step was individually defensible. ``network.md`` quoted its source
exactly; the ranking pass ranked on the census's own numbers. The structural
fault is that **the correction lived in a different file from the claim and
nothing joined them**, and the parity audit could not, on its own, name its
corrector.

## Why this is not a lexical classifier, which was MEASURED before it was built

The wave lead ran the lexical scan first, over the 91 documents then in
``_audit/``. A LOOSE correction vocabulary near a citation gave **15**
(corrector, target) pairs; a TIGHT one gave **6**, of which exactly **1** was a
genuine "document X corrects document Y" -- the parity chain above. The rest
were self-corrections ("MY ARITHMETIC WAS WRONG"), corrections of a HYPOTHESIS
rather than of the cited document, and later documents QUOTING the original
correction.

This file's own scan is stated exactly rather than described, so it can be
re-run: the vocabulary in :data:`CORRECTION_VOCABULARY` within :data:`WINDOW`
lines of a citation that resolves. Over the 94 documents present at 2026-09-04
09:26 that gives **27** candidate pairs -- and still exactly **1** genuine one.
The totals differ from the lead's because the window and the word list are
CHOICES, and they are written down here where they were only described there;
the same corpus scanned with a tight vocabulary at +-1 reproduces the lead's 6
exactly. **What does not differ is the ratio, and the ratio is the whole
argument: 26 of 27 hits are mentions.** No threshold separates them, so a check
built on the vocabulary alone would either miss corrections or cry wolf.

**CORRECTED 2026-09-05 -- THE 94 WAS A COUNT OF THE WRONG CORPUS.** The scan
reached ``_audit/`` with ``rglob``, which reads the WORKING COPY, and 37 of
those 94 documents were ignored ``_audit/_scratch/`` working notes that no
clone has. The domain is now the 57 documents git TRACKS at this SHA -- see
:func:`_documents` for why, and for the local-passes/clone-fails divergence
that found it. Re-measured over that corpus: **24** candidate pairs, still
exactly **1** genuine one, so 23 of 24 are mentions. The ratio the argument
rests on is unchanged; only the denominator moved, and it moved to the one a
reader of the repository can reproduce.

**ALL OF THESE ARE DATED READINGS, NOT PROPERTIES.** ``_audit/`` grew from 91 to
94 documents during the hour this file was written, because concurrent waves
write into it continuously. So no test below asserts a total. What they assert
is an IDENTITY that survives the corpus moving: every candidate is declared or
triaged, and every triage entry is still a candidate. A wave that adds a real
correction turns this file red, which is the design working, not a collision.

## So this file does not classify. It does two things.

**(A) ASSERT the back-pointer for every DECLARED correction.** A corrector
declares itself with a marker line::

    **CORRECTS:** `_audit/2026-08-22-parity-linkedin.md` -- <the claim>

and the named target MUST carry the matching back-pointer::

    **CORRECTED BY:** `_audit/2026-08-23-build-linkedin.md` -- <what changed>

Zero false positives, and it cannot rot: the assertion is over MARKERS, not
over prose. Both directions are checked, so a half-finished edit -- a
declaration with no back-pointer, or a back-pointer no document declares --
fails rather than reading as a joined pair.

**(B) FORCE TRIAGE of everything the lexical scan finds.** Every candidate pair
must be EITHER declared under (A) OR listed on :data:`NOT_A_CORRECTION` with a
written reason. A new correction appearing in prose then FAILS this test until
somebody either declares it or explains why it is not one. That is the half
that keeps working after today.

**AN ENTRY ON ``NOT_A_CORRECTION`` IS A CLAIM, AND IT IS ITSELF CHECKED** -- the
discipline ``test_reader_reachability.py::UNREACHABLE_BY_DESIGN`` and
``test_selectors_resolve.py::NOT_RESOLVED_HERE`` already keep. An entry claims:
*the scan does produce this pair, and having read the line that produced it, it
is a mention rather than a correction, for the reason given.* All three halves
are asserted. A STALE ENTRY -- one for a pair the scan no longer produces --
FAILS AS LOUDLY AS A MISSING ONE, because an allowlist nobody re-checks is a
silencer, and this file would then be the thing it was written to catch.

Nothing here reaches LinkedIn, an account, or a browser. It reads committed
markdown and nothing else.
"""

from __future__ import annotations

import ast
import collections
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
AUDIT = ROOT / "_audit"

#: A citation as this corpus actually spells them: a backticked path ending in
#: ``.md``, optionally carrying the line or line-range it points at (``:229``,
#: ``:229-231``). The corpus writes the same target three ways --
#: ``_audit/x.md``, ``x.md`` and ``_census/x.md`` -- and all three resolve
#: below. Spellings that name nothing here (``_audit/*.md``, a bare ``.md``, a
#: path into a SIBLING repository's audit directory) resolve to None and are
#: IGNORED rather than failing: this file is about corrections between the
#: documents in THIS corpus, and a dangling citation is a different defect.
CITATION = re.compile(r"`([^`\n]*?\.md)(?::\d+(?:-\d+)?)?`")

#: The declaration channel. The keyword plus its colon must OPEN the line --
#: leading whitespace and markdown emphasis are allowed, so ``**CORRECTS:**``,
#: an indented ``   **CORRECTED BY:**`` and a bare ``CORRECTS:`` all count.
#:
#: **IT USED TO MATCH THE KEYWORD ANYWHERE IN A LINE, AND THAT WAS WRONG IN A
#: WAY ONLY THIS FILE'S OWN SUBJECT MATTER EXPOSES.** A sentence DESCRIBING the
#: mechanism -- "a corrector writes a ``CORRECTS:`` marker; the named target
#: must carry ``CORRECTED BY:``" -- was read AS a marker, and reported as one
#: naming zero documents. It was found the hour the register entry describing
#: this check was written, which is exactly when it would be found: **prose
#: about a mechanism is indistinguishable from the mechanism to a pattern that
#: does not care where on the line it sits.** That is this repository's own
#: recurring defect, committed by the check written to catch a cousin of it.
#:
#: Anchoring at line-start is the fix rather than a workaround, because a
#: DECLARATION is a line, not a phrase: every real marker in this corpus opens
#: its line, and nothing that merely mentions one does.
MARKER = re.compile(r"^\s*(?:\*\*)?(CORRECTS|CORRECTED BY):")

#: How many lines from a citation the vocabulary may sit. THE REAL INSTANCE
#: NEEDS AT LEAST 1: the citation is at ``build-linkedin.md:229`` and the words
#: "mis-specified, measured" are at :230, so a same-line rule would miss the one
#: correction this whole file exists for. It is 2 rather than 1 for margin --
#: the same paragraph re-wrapped two columns narrower would push the verb to
#: :231 -- and the cost of the extra reach is paid honestly, in triage entries
#: below rather than in silence.
WINDOW = 2

#: The LOOSE vocabulary. Deliberately loose: its job is not to be right, it is
#: to make sure a real correction cannot appear in prose without SOMEBODY
#: having to look at it. Terms that match nothing in the corpus today are kept
#: on purpose -- they cost no triage entries and they cover a future correction
#: spelled that way.
CORRECTION_VOCABULARY = (
    "mis-specified",
    "misspecified",
    "corrects",
    "corrected",
    "correction",
    "wrong",
    "incorrect",
    "stale",
    "refuted",
    "refutes",
    "superseded",
    "supersedes",
    "mistake",
    "retract",
    "overturn",
    "false",
)

#: Candidate pairs the scan produces that are NOT corrections, each with the
#: reason, keyed ``(corrector_filename, target_filename)``. EVERY REASON BELOW
#: WAS WRITTEN AFTER READING THE LINE THAT PRODUCED THE PAIR, not inferred from
#: the filenames -- several of them turn on which of three adjacent table rows
#: the matched word actually sits in, which a filename cannot tell you.
#:
#: The recurring shapes, since they are the answer to "why is this list long":
#: TABLE-ROW PROXIMITY (a markdown table has no blank lines, so a verdict on
#: one tool's row lands within two lines of another tool's citation); a
#: correction of a HYPOTHESIS rather than of a document; a later document
#: QUOTING the original correction; an OPEN QUESTION that declines to rule; a
#: NEGATION ("no later file supersedes them"); and -- five times -- a report
#: about a document that ALREADY CARRIES ITS CORRECTION IN PLACE, which is the
#: outcome this file exists to require and so cannot also be a violation of it.
NOT_A_CORRECTION: dict[tuple[str, str], str] = {

    # 2026-09-21, the WRITE-CEILING wave. The correction is REAL, and its
    # TARGET IS THE CENSUS CELL ITSELF rather than either cited document --
    # which is the case this dict exists to distinguish and the one a
    # proximity scan cannot.
    ("network.md", "2026-09-05-groups-surface-measured.md"): (
        "THE CORRECTION TARGETS THE CITING CELL, NOT THE CITED DOCUMENT. "
        "Census row 63 asserted that `/groups/<id>/` and `/groups/discover/` "
        "are *'NAMED REFUSALS in `readonly.py`'s own comment'*. Measured "
        "2026-09-21 through the shipped gate, both are ALLOWED: two allowlist "
        "patterns were added 2026-09-19 and the cited comment was rewritten "
        "BY that admission. So the false clause is the ROW'S OWN, written "
        "before the boundary moved under it. "
        "`2026-09-05-groups-surface-measured.md` is cited by that row as "
        "EVIDENCE for a different and still-true finding -- that no join "
        "control is drawn on any suggestion row on `/groups/` -- and nothing "
        "in this correction touches it. Declaring a CORRECTS: pair would "
        "send a reader to a document that got nothing wrong."
    ),

    # 2026-09-21, the WRITE-CEILING wave. The TABLE-ROW proximity shape this
    # dict's docstring names FIRST, and a second instance of it.
    ("network.md", "2026-09-05-groups-wire.md"): (
        "THE MATCHED WORD IS IN A DIFFERENT ROW, ABOUT A DIFFERENT SURFACE. "
        "The citing line is census row 162 -- browse recommended groups -- "
        "which cites `2026-09-05-groups-wire.md` for a live payload, and "
        "that row was NOT edited by this wave. The correction vocabulary is "
        "one line below, inside ROW 163, where a 2026-09-21 measurement "
        "records that row's own address clause as false. A markdown table "
        "has no blank lines, so row 163's prose sits inside row 162's "
        "two-line window. Row 162's claims are untouched and unchallenged."
    ),

    # 2026-09-21, the PROXIMITY-FIELD wave. Triaged by reading the line, and
    # it is the TABLE-ROW proximity shape this dict's own docstring names
    # FIRST -- the matched word is in a different capability's row.
    ("jobs.md", "2026-09-21-the-proximity-field.md"): (
        "THE MATCHED WORD IS IN A DIFFERENT ROW, ABOUT A DIFFERENT ADDRESS. "
        "The citing line is census row 40, which names this wave's own "
        "deliverable as its evidence: *'Evidence "
        "`_audit/2026-09-21-the-proximity-field.md`'*. The correction "
        "vocabulary is `stale`, two lines below, inside ROW 42 -- job "
        "collections -- where it appears as *'all four are the staleness "
        "diagnostic'*, describing the STRING CONTENT OF A JSON PAYLOAD and "
        "not a claim that any document got anything wrong. A markdown table "
        "has no blank lines, so row 42's prose sits inside row 40's window. "
        "**THE CITED DOCUMENT IS ROW 40'S OUTPUT, NOT ITS CORRECTOR.** Row 40 "
        "moved GAP -> COVERED-UNFIRED because that wave built the reader; the "
        "document reports the build and withdraws nothing in `jobs.md`. The "
        "one thing that wave did correct -- a line pointer in two blocker "
        "TSVs -- it deliberately did NOT act on, and says so. "
        "**WHAT WOULD MAKE THIS ENTRY WRONG:** row 40 citing that document "
        "while WITHDRAWING a claim of its own, or row 42 being rewritten so "
        "that its `stale` becomes a verdict about a document rather than "
        "about a payload. Either turns this into a real pair needing markers."
    ),

    # 2026-09-21, the THREE-READERS wave. Both triaged by reading the line,
    # and both are the TABLE-ROW / ADJACENT-HEADING proximity shape this
    # dict's own docstring names.
    ("INSTRUMENTS.md", "2026-09-21-the-three-readers.md"): (
        "THE VOCABULARY IS THE NEXT HEADING AND IT IS ABOUT A PLANTED "
        "DEFECT, NOT ABOUT THAT DOCUMENT. The cited line is *'Deliverable: "
        "`_audit/2026-09-21-the-three-readers.md`.'* -- a pointer and "
        "nothing else. The match is `wrong`, two lines below, inside "
        "*'### 49.1 `dom.COUNT_LINES_JS` -- SHOWN FAILING BY READING THE "
        "WRONG NUMBER'*, which is the register naming what the MUTATED "
        "script reads. The register entry and the deliverable are the same "
        "wave's output and neither withdraws anything in the other. "
        "**WHAT WOULD MAKE THIS ENTRY WRONG:** a later register section "
        "asserting that something in that deliverable is false while "
        "leaving the deliverable untouched."
    ),
    ("network.md", "2026-09-21-the-fires-and-the-controls.md"): (
        "THE ARROW IS DECLARED IN THE OTHER DIRECTION AND THIS IS ITS "
        "SHADOW. The fires-and-the-controls deliverable declares "
        "*'CORRECTS: `_audit/_census/network.md` -- rows 33, 54 and 175'*, "
        "and network.md carries the matching CORRECTED BY. What this "
        "candidate pair claims instead is that NETWORK.MD corrects the "
        "DELIVERABLE, which is backwards: the slice withdraws nothing from "
        "that document and asserts nothing about it. The vocabulary match is "
        "inside row 33's own re-priced cell -- *'both claims are corrected "
        "in place rather than left standing'* -- which is the cell "
        "describing the edit the deliverable made to the SOURCE MODULES, "
        "two lines from the citation that names the deliverable. A census "
        "cell that explains why it moved will always sit near the document "
        "that moved it, so this shape recurs by construction rather than by "
        "anybody's mistake; the sibling entry below is the same shape one "
        "wave earlier. "
        "**WHAT WOULD MAKE THIS ENTRY WRONG:** network.md asserting that "
        "something in the fires-and-the-controls deliverable is false while "
        "leaving that deliverable untouched. It does not -- every row the "
        "deliverable discusses is edited in this slice, in the same commit."
    ),
    ("network.md", "2026-09-21-the-three-readers.md"): (
        "THE VOCABULARY BELONGS TO THE DELTA BELOW, WHICH IS OLDER THAN THE "
        "CITATION AND IS NOT CORRECTED BY IT. The cited line is *'name-"
        "freedom argument for each: `_audit/2026-09-21-the-three-readers."
        "md`.'*, closing the THIRD DELTA -- a BUILD that moved rows 33, 54 "
        "and 175 out of GAP. The match is `correction`, two lines below, in "
        "the header of the SECOND DELTA: *'2026-09-20, and it is a "
        "VOCABULARY correction rather than a finding'*, which is that "
        "earlier delta describing ITSELF. The slice stacks its deltas "
        "newest-first with no blank line between a delta's last line and "
        "the next delta's header, so every new delta lands within the "
        "window of the previous one's self-description. "
        "**WHAT WOULD MAKE THIS ENTRY WRONG:** the three-readers document "
        "asserting that a row or a state in this slice is mistaken while "
        "leaving the row untouched. It does not; all three rows it discusses "
        "are edited in the slice itself."
    ),
    # 2026-09-21, the JOBS-DIRECTION wave. All three triaged by reading the line.
    ("2026-09-21-the-jobs-direction.md", "jobs.md"): (
        "THE CORRECTION WAS MADE IN PLACE, WHICH IS THE ONE CASE THE BACK-"
        "POINTER MECHANISM DOES NOT SERVE. The line reads *'Two statements in "
        "`jobs.md` section 2 were false at HEAD and are corrected in place'*, "
        "and that is literally what happened: both cells are STRUCK THROUGH "
        "in that file with the replacement reading and the admitting commit "
        "beside them. "
        "**THE MARKER PAIR EXISTS FOR CORRECTIONS THAT LIVE IN ANOTHER "
        "DOCUMENT**, where a reader arriving at the claim would otherwise "
        "never learn it was withdrawn -- this file's own subject. A reader "
        "arriving at either of these two claims CANNOT MISS the correction, "
        "because it is in the same sentence. A CORRECTED BY marker at the top "
        "of that slice would additionally be wrong in a specific way: it would "
        "announce that the SLICE was corrected, when what moved was two "
        "costing cells in section 2 and **no row, no state and no count**. "
        "**WHAT WOULD MAKE THIS ENTRY WRONG:** if that wave had corrected a "
        "jobs claim from OUTSIDE the file -- asserting in its own audit "
        "document that a row or a state there is mistaken while leaving the "
        "row untouched. It did not; every jobs edit it made is in the slice."
    ),
    # 2026-09-21, the FOURTEEN-FIRED wave. One pair, and it is the arrow
    # pointing the wrong way.
    ("network.md", "2026-09-21-the-fourteen-fired.md"): (
        "THE CITATION IS A ROW NAMING ITS OWN RECEIPT, AND A RECEIPT IS NOT A "
        "THING THE ROW WITHDRAWS. The line is census row 80, whose cell "
        "reports a live firing and then says *'It does not prove the page "
        "offers a control to NARROW to it'* -- the correction vocabulary is "
        "the row stating ITS OWN verdict about the SURFACE, not a claim that "
        "the cited document got anything wrong. Row 80 exists in that shape "
        "BECAUSE of that document; it is its output. "
        "**THE REAL CORRECTION IN THIS PAIR RUNS THE OTHER WAY AND IS "
        "DECLARED.** `2026-09-21-the-fourteen-fired.md` carries `CORRECTS: "
        "_audit/_census/network.md` and that slice carries the matching "
        "`CORRECTED BY:` back-pointer, because the document is what re-priced "
        "rows 80-93 and moved row 83 out of GAP. A second marker pair for the "
        "reverse direction would assert that the SLICE withdrew something in "
        "the DOCUMENT, which nothing here does. "
        "**WHAT WOULD MAKE THIS ENTRY WRONG:** if a `network.md` row ever "
        "asserted that this document's own readings are mistaken -- a later "
        "wave re-reading the surface and contradicting the banked `locations` "
        "measurement, say -- while leaving the document itself unmarked. That "
        "row WOULD be correcting it from outside, and would need its own "
        "marker pair. Today no row disputes a single figure in it."
    ),
    ("INSTRUMENTS.md", "jobs.md"): (
        "THE REGISTER DESCRIBES A MEASUREMENT OF THAT SLICE, IT DOES NOT "
        "WITHDRAW ANYTHING IN IT. Section 47's line reads *'recorded "
        "`jobs.md`'s rows as UNMEASURED, because its per-row tables run "
        "...'* -- the correction vocabulary belongs to what the CEILING "
        "DOCUMENT said about that slice, and the correction of the ceiling "
        "document is declared with its own marker pair in "
        "`2026-09-21-the-jobs-direction.md`. **No row of `jobs.md` is "
        "contradicted and no state moves**: the wave classified direction, "
        "which that file never stated per row, and the two edits it made to "
        "section 2 repair two EXPIRED BOUNDARY PREMISES in place, each "
        "struck through with the admitting commit beside it. "
        "**WHAT WOULD MAKE THIS ENTRY WRONG:** if the register ever asserted "
        "that a STATE or a COUNT in that slice is mistaken, rather than that "
        "a costing cell went stale underneath it."
    ),
    ("INSTRUMENTS.md", "2026-09-20-the-sanctioned-seventh.md"): (
        "THE CITATION IS AN ANALOGY, NOT A CORRECTION. Section 47.3 reads "
        "*'the same shape `_audit/2026-09-20-the-sanctioned-seventh.md` names "
        "as \"Section 4 was never re-read\"'* -- the cited document is being "
        "AGREED WITH and used as the precedent for why a census cell that was "
        "true when written can be false sixteen days later with nothing "
        "pointing a reader at it. **Nothing in it is withdrawn.** A CORRECTED "
        "BY marker there would tell every future reader that this wave "
        "retracted something in that document, and this wave relies on it."
    ),

    # 2026-09-20, the EVIDENCE-THAT-RESOLVES wave. Both triaged by reading the
    # line that produced them.
    ("2026-09-20-the-evidence-that-resolves.md",
     "2026-09-20-the-chain-verification.md"): (
        "THE CITATION IS AN ANALOGY, NOT A CORRECTION. The line reads *'it is "
        "the same shape as the census at `_audit/2026-09-20-the-chain-"
        "verification.md`: a correct measurement of the wrong population'* -- "
        "the cited document is being AGREED WITH and used as the precedent for "
        "why the citing wave checked a relayed claim instead of acting on it. "
        "The correction vocabulary in the window belongs to what that document "
        "ITSELF corrected, which it already declares with its own marker pair. "
        "A CORRECTED BY marker here would tell every future reader that this "
        "wave withdrew something in it, and nothing in it is withdrawn."
    ),
    ("2026-09-20-the-evidence-that-resolves.md", "messaging-and-content.md"): (
        "THE CITING DOCUMENT REPORTS A CORRECTION SOMEBODY ELSE MADE, AND "
        "DECLINES TO MAKE ONE. The line says row `M4` was corrected -- by "
        "`master`, from EXCLUDED-RULED to MEASURED-ABSENT, in that row's own "
        "words -- and that the correction moved M4 into the banked population "
        "for the first time, which is why a re-measurement found it. NOTHING "
        "IN THAT SLICE IS WITHDRAWN BY THE CITING WAVE: no row is edited, no "
        "state is proposed, and the instrument that found M4 is documented as "
        "measuring and never demoting. "
        "**WHAT WOULD MAKE THIS ENTRY WRONG:** if that document ever asserted "
        "M4's state or its cited numbers were mistaken, rather than reporting "
        "that its own first reading of M4 counted an abbreviated path as "
        "unreachable -- which is a correction of the INSTRUMENT, and is "
        "recorded against the instrument."
    ),
    ("2026-09-20-the-evidence-that-resolves.md", "network.md"): (
        "THE CITATION IS A FALSE-POSITIVE REPORT ABOUT AN INSTRUMENT, NOT A "
        "CLAIM ABOUT THE CENSUS. The line names `network.md` lines 171-172 to "
        "record that the shipped `dialect_of` heuristic flags `ABSENT` there, "
        "in a two-column table about page ADDRESSES where the word means the "
        "page is not drawn. NO ROW OF THAT SLICE IS CONTRADICTED and no state "
        "moves: the finding is about the scope of a matcher the citing wave "
        "imported, and the repair was made in the importing file. The citing "
        "wave DOES correct a census claim elsewhere and declares it with a "
        "CORRECTS:/CORRECTED BY: pair, so its threshold for declaring one is "
        "on the record and this pair sits below it deliberately."
    ),

    # 2026-09-20, the UNFIRED-TWENTYSEVEN wave. Three candidates, triaged by
    # reading each line. Two are a cell superseding ITSELF with a live fire;
    # the third is the scan attributing one row's vocabulary to its neighbour.
    ("jobs.md", "2026-09-19-covered-vs-gap-pairs.md"): (
        "THE CELL SUPERSEDES ITSELF, AND THE CITED DOCUMENT CORRECTS NOTHING. "
        "Row `J 27` moved COVERED-UNFIRED -> COVERED-PROVEN because "
        "`verified_job` was finally fired over 11 live postings and came back "
        "true on 5 and false on 6. The cited document banked the row UNFIRED "
        "on a source trace and said so honestly -- *no run has been recorded "
        "asserting a value on a live posting* -- which was ACCURATE WHEN "
        "WRITTEN and is why the row sat UNFIRED at all. This wave supplied "
        "the measurement that cell had been waiting for; it did not find a "
        "fault in it. A CORRECTED BY: pointer would claim the fire report "
        "convicted the earlier document, when what it did was finish it. "
        "The one genuinely critical remark in the new cell -- that the row's "
        "`_audit/_scratch/` TSV is gitignored and unreachable from a clone -- "
        "is about the CENSUS ROW'S OWN CITATION, not about anything the cited "
        "document claims, and the new cell replaces that reference in place"
    ),
    ("profile.md", "2026-09-19-read-tail.md"): (
        "IDENTICAL CASE, THE TWIN SLICE. Row `K10` is the same capability as "
        "`jobs.md J 27` and moved on the same fired reading. The cited "
        "document said *no audit records this field's value coming back from "
        "a live posting*, which was true when written and is now false "
        "because this wave took the reading -- a claim overtaken by a "
        "measurement, not a claim refuted. The two slices agreed before and "
        "agree after"
    ),
    ("messaging-and-content.md", "2026-08-30-linkedin-writes.md"): (
        "THE VOCABULARY BELONGS TO THE NEXT ROW, NOT TO THIS CITATION. The "
        "flagged line is row `M43`, which this wave did NOT touch and whose "
        "citation still stands exactly as written: `linkedin_open_messaging` "
        "was deliberately never called because *the cost lands on somebody "
        "who is not him*. THIS WAVE DECLINED IT FOR THE SAME REASON and "
        "changed nothing about M43. The correction vocabulary inside the "
        "window is the word *superseded* in row `M45` two lines below, where "
        "a live fire of `linkedin_compose_fields` supersedes that row's OWN "
        "2026-09-02 refusal -- again a cell superseding itself. "
        "**THE SCAN IS RIGHT TO OFFER IT AND RIGHT TO BE OVERRULED HERE:** a "
        "two-line window cannot tell which row a word sits in, which is the "
        "known cost of the window and is why this table exists"
    ),
    # 2026-09-20, the sanctioned-seventh reading. Triaged by the integrator who
    # wrote the citing line, deliberately, to say what he was NOT doing.
    ("2026-09-20-the-sanctioned-seventh.md", "profile.md"): (
        "THE CITATION IS A HANDOVER, AND IT SAYS SO IN THE SAME SENTENCE. The "
        "line reads that `_audit/_census/profile.md` 'is under a live wave's "
        "hand as this is written', and the section it closes states outright "
        "that the rows named above are NOT repaired here because they belong "
        "to the census slices. Naming rows for the wave that owns them is the "
        "opposite of correcting them. "
        "**THE SCAN IS RIGHT TO OFFER IT**, because the correction vocabulary "
        "in the window is real and dense -- the surrounding paragraphs are "
        "about a reason that went false, and rows `B2`, `M1`, `B3`, `B5` and "
        "`G3` in that very file carry it. A later wave may well correct them, "
        "and when it does the pair becomes a genuine CORRECTS:/CORRECTED BY: "
        "declaration against profile.md rather than this entry. "
        "**WHAT WOULD MAKE THIS ENTRY WRONG:** if this document ever edits a "
        "profile.md row, or asserts that a profile.md claim is withdrawn "
        "rather than merely stale. It does neither today; it measures the "
        "code and hands the rows on, and the census file is untouched by it."
    ),

    # 2026-09-20, the FIRST FIRING wave. Triaged by reading the line, which is
    # a census row I had written myself minutes earlier.
    ("jobs.md", "2026-09-20-the-first-firing.md"): (
        "THE CITATION IS EVIDENCE FOR A BANKING, NOT A CORRECTION OF ANYTHING. "
        "The line is row `J 125`, moved GAP -> COVERED-PROVEN because "
        "/jobs/collections/top-applicant was opened for the first time and "
        "linkedin_premium_job_collection shipped in the same commit; it cites "
        "the audit as the place its numbers were taken. Nothing above it is "
        "withdrawn and no earlier claim about J 125 is contradicted -- the row "
        "had no prior reading at all, which is why it sat GAP. "
        "**THE SCAN IS RIGHT TO OFFER IT AND RIGHT TO BE OVERRULED HERE:** the "
        "correction vocabulary inside its window belongs to row `J 127` two "
        "lines below, which IS a real correction and is declared with a "
        "CORRECTS:/CORRECTED BY: marker pair against this same document. Two "
        "adjacent rows, one correcting and one banking, citing one audit -- "
        "the lexical window cannot separate them and a reader can."
    ),

    # 2026-09-20, the premium-four INTEGRATION. Triaged by reading the line,
    # which the integrator had written himself ninety seconds earlier.
    ("2026-09-20-the-premium-integration.md", "2026-09-20-newsletter-built.md"): (
        "THE CITED DOCUMENT IS THE VICTIM, NOT THE SUBJECT. The passage records "
        "a defect in the INTEGRATION'S OWN WORK: it renamed "
        "test_the_admitted_analytics_pages_are_exactly_three so the name would "
        "match the number, and that rename would have rotted a citation -- "
        "because 2026-09-20-newsletter-built.md quotes the function BY NAME at "
        "line 493. The correction vocabulary ('wrong', 'broken') governs the "
        "RENAME, which was reverted, and never the cited document, which is "
        "correct and unchanged and is named only to say whose citation was at "
        "risk. A CORRECTED BY marker would tell every future reader that the "
        "newsletter audit had said something false, which nothing here claims. "
        "THE GUARD FIRED ON THE INTEGRATOR AND IT WAS RIGHT TO: a document that "
        "names another while discussing what was wrong is exactly the shape "
        "this table exists to make somebody read."
    ),

    # 2026-09-20, premium-four wave. THE THIRD OF THREE PAIRS THIS ONE WAVE
    # TRIPPED, AND THE PATTERN IN THEM IS WORTH MORE THAN ANY OF THEM.
    #
    # All three are prose that DISCUSSES correction -- a disclaimer, a filing
    # pointer, and this one, a note about deliberately NOT renaming something
    # so a citation cannot rot. A scanner that keys on correction vocabulary
    # near a citation cannot tell writing ABOUT corrections from writing THAT
    # corrects, and a wave whose audit reasons carefully about what it is and
    # is not correcting will trip it repeatedly. That is the scan being
    # sensitive in the right direction: each one took a minute to read and
    # dismiss, and the failure it prevents -- a false CORRECTED BY marker on
    # somebody else's correct work -- is not cheap to undo.
    ("2026-09-20-the-premium-four.md", "2026-09-20-newsletter-built.md"): (
        "THE LINE EXPLAINS WHY A TEST FUNCTION'S NAME WAS *NOT* CHANGED. It "
        "reads: 'Its NAME still says \"three\" and is KEPT: "
        "_audit/2026-09-20-newsletter-built.md cites this function by name, "
        "and this repository's own finding is that a citation rots into a "
        "PLAUSIBLE WRONG ANSWER rather than a dangling one.' The cited "
        "document is named as a CONSUMER of that name -- the reason to leave "
        "it alone -- not as a document saying anything wrong. Nothing in "
        "newsletter-built.md is being corrected; its own sentence about that "
        "test ('unmoved at 4 patterns') describes the tree as it stood when "
        "it was written and was true then. The count moved later, by this "
        "wave's own admission, which is a fact about the boundary and not an "
        "error in that audit."
    ),

    # 2026-09-20, premium-four wave. A DOCUMENT POINTING AT THE REGISTER ENTRY
    # THAT HOLDS ITS OWN FINDING.
    ("2026-09-20-the-premium-four.md", "INSTRUMENTS.md"): (
        "THE LINE IS A FILING POINTER, NOT A VERDICT ON THE REGISTER. It reads "
        "'The defect is against the SCRIPT and is filed at INSTRUMENTS.md "
        "32.2', and 32.2 is a section THIS SAME WAVE wrote in the same commit "
        "series -- written as 29.2 and renumbered TWICE on the way in, because "
        "live-capture took 29, names-that-do-not-exist took 30, and reason-kinds "
        "landed 31 while this integration was running. "
        "A wave citing the register entry that carries its own finding "
        "is an attribution -- the direction a reader needs in order to find the "
        "detail -- and a CORRECTED BY marker would assert that INSTRUMENTS.md "
        "had said something wrong, which nothing here claims. The correction "
        "vocabulary the scan matched ('defect') belongs to the SUBJECT of the "
        "sentence, a probe script in another wave's file, not to its object. "
        "THIS PAIR WAS CAUGHT AFTER THE GATE HAD ALREADY READ THE INDEX and "
        "therefore after the commit that introduced it, which is its own "
        "lesson: an amendment made after staging is an unchecked change."
    ),

    # 2026-09-20, premium-four wave. Triaged by READING THE LINE, which is what
    # this table asks for -- and the line is a DISCLAIMER of the very thing the
    # scan suspects.
    ("2026-09-20-the-premium-four.md", "2026-09-20-the-live-capture.md"): (
        "THE SENTENCE THAT TRIPS THE SCAN IS THE ONE REFUSING TO CORRECT. It "
        "reads 'THE WAVE THAT OWNS THAT PROBE GOT THIS RIGHT IN PROSE AND THIS "
        "IS NOT A CORRECTION OF ITS CONCLUSION', and the paragraph goes on to "
        "say the cited document states plainly that the create route is drawn "
        "and refused and that the listing is 'not drawn; reached by "
        "admission'. What the premium-four wave found is a defect in the "
        "TABLE the cited wave's INSTRUMENT prints -- depth-3 truncation "
        "displaying a refused create route as an admitted read -- not in the "
        "cited document's reasoning, which is correct. A finding about a "
        "script's output that explicitly exonerates the prose citing it is an "
        "attribution, not a correction, and inserting a CORRECTED BY marker "
        "into the live-capture audit would tell every future reader that its "
        "conclusion was wrong when this wave's own text says it was right. "
        "The defect itself is recorded at INSTRUMENTS.md section 32.2, filed "
        "against the SCRIPT, and deliberately not edited by this wave because "
        "it belongs to another wave's file."
    ),

    # TWO FROM THE REGISTER, 2026-09-20, surfaced only after a merge put section
    # 31 and its cited documents in one tree. Both are the register citing a
    # document as its SOURCE while correction vocabulary in the same sentence
    # describes something else entirely -- which is the scan working: the words
    # are there, and the relation is not.
    ("INSTRUMENTS.md", "2026-09-20-the-contingent-writeoffs.md"): (
        "IT CITES THE DOCUMENT AS THE MEASUREMENT BEHIND A DESIGN RULE. The "
        "passage argues that register keys must be ROW IDS and never line "
        "numbers, and cites that document's s4.1 as the evidence: all six of "
        "the census's line-number locators measured DRIFTING 48 to 51 lines, "
        "one landing on a different row that read COVERED-PROVEN. The drift is "
        "what the cited document FOUND, not an error in it. A rule citing the "
        "measurement that justifies it is an attribution. "
    ),
    ("INSTRUMENTS.md", "2026-09-20-the-reason-kinds.md"): (
        "IT POINTS AT WHERE THE NUMBERS LIVE. The sentence reads 'Their "
        "numbers are the tables in <that document>'. The word SUPERSEDED in "
        "the lines above it governs four scratch mutation drivers -- three "
        "superseded by the committed classifier's own reporting, the fourth by "
        "the pytest guard that runs the same mutations with postcondition "
        "assertions. Nothing in the passage supersedes the cited document; it "
        "is named as the place the surviving numbers were published. "
    ),

    # SURFACED BY A MERGE, not by either wave alone. The register entry and the
    # document it cites arrived on two different branches; neither tree held
    # both, so neither wave's green run could see this pair. It was triaged once
    # during integration and LOST when a sibling branch's version of this dict
    # won the same hunk -- which is its own lesson about where merges eat things.
    ("INSTRUMENTS.md", "2026-09-20-control-census.md"): (
        "THE REGISTER CITES THE DOCUMENT THAT PRODUCED ITS FINDING. The entry is "
        "the control-census instrument's registration, and the line names "
        "control-census.md as the source of the per-file breakdown behind its "
        "numbers. What trips the scan is the sentence just after: 'This is not a "
        "claim that the 5 banked rows are WRONG -- a decorative control does not "
        "mean the probe's finding was false.' That sentence exists to PREVENT a "
        "misreading of the cited document, which is the opposite of correcting "
        "it. An instrument naming its own evidence is an attribution. "
    ),

    # 2026-09-20, from the impact-gate wave. A citation of a defect ALREADY
    # REPAIRED at 5d0efb5, reused as the gate's own proving input -- which is
    # the best kind of test case, because it is a failure that really happened.
    ("2026-09-20-the-impact-gate.md", "2026-09-03-linkedin-gap-blockers.md"): (
        "IT NARRATES A DEFECT ALREADY FIXED, AND USES IT AS THE GATE'S TEST "
        "CASE. The passage describes commit 5d0efb5 -- a CORRECTED BY "
        "marker inserted between a table header and its first data row, "
        "which made _table_after() take zero rows so every blocker read as "
        "unknown. The wave staged the REVERSE of that commit as the input "
        "its selector had to catch, and the old selector returned zero "
        "tests while the truth was two failures. The ledger is the file "
        "that was broken and then repaired; it is the wave's fixture, not a "
        "claim being corrected. "
    ),

    # 2026-09-20, from the premium-block wave. The OTHER candidate it produced
    # IS a real correction -- of the jobs census cell that banked J 127
    # MEASURED-ABSENT on a reading whose instrument carries no needle for a
    # balance -- and is declared with a CORRECTS:/CORRECTED BY: pair instead.
    ("2026-09-20-the-premium-block.md", "2026-09-19-blocker-map-ruling-requests.md"): (
        "IT REPORTS A REQUEST ITS OWN AUTHOR RETRACTED. The passage records "
        "that Request 2a was filed and then retracted by the person who "
        "filed it, and that the caution left behind says the blocker does "
        "not cleanly close even with the disputed row removed. The wave "
        "then writes 'Sibling waves own this adjudication. I report it and "
        "leave it.' Citing a document for a retraction its author already "
        "made, and declining to act on somebody else's blocker, is not "
        "correcting it. "
    ),

    # TWO MORE, 2026-09-20. Both citations. The two REAL corrections that same
    # wave made -- of the ledger's stale ranking tables and of a costing that
    # priced a needle which does not exist -- are declared with CORRECTS: /
    # CORRECTED BY: pairs instead, which is what this table leaves room for.
    ("2026-09-20-the-decides.md", "2026-09-05-decide-retire-rulings.md"): (
        "IT QUOTES THE RULING NOTICING THE SAME THING FIRST. The block "
        "quoted is that ruling's own closing section: 'WHAT THIS RULING "
        "DOES NOT REACH: rows 146-149 are a different product and are "
        "already filed under FILE-UPLOAD-UNSANCTIONED.' The wave agrees and "
        "says the earlier ruling correctly declined to act on somebody "
        "else's blocker. A document citing another one for having seen a "
        "problem first is the opposite of correcting it. "
    ),
    # 2026-09-20, from the names-that-do-not-exist wave. Read the line before
    # judging the shape: the correction vocabulary belongs to the SUBJECT being
    # discussed (an unapplied ruling), not to the relation between the two
    # documents.
    ("2026-09-20-names-that-do-not-exist.md", "2026-09-20-the-decides.md"): (
        "IT CITES THE OTHER DOCUMENT AS CORROBORATION, IN THE SAME SENTENCE "
        "THAT CREDITS IT. The passage reports a second class the guard found "
        "-- blockers opened by a committed ruling that never entered the "
        "ledger -- and closes 'which is a different problem with a different "
        "owner. `2026-09-20-the-decides.md:95` already says so about the "
        "first one in its own words.' The named line is that document "
        "stating `AI-INTERVIEW-RESULTS-NO-ADDRESS` exists only in one other "
        "file, which is the reason THIS wave's guard rules it MARKED-ABSENT "
        "rather than a finding. Citing a document for having disclosed "
        "something first, and letting that disclosure decide a verdict in "
        "its favour, is the opposite of correcting it. "
    ),

    # 2026-09-20, the same wave's second pair. The correction vocabulary here
    # belongs to a COLUMN HEADING in a precision table, not to a relation
    # between the two documents.
    ("2026-09-20-names-that-do-not-exist.md", "2026-09-05-leave-group-writespec.md"): (
        "IT IS A ROW IN A PRECISION TABLE, AND THE VERDICT IN IT IS "
        "AGREEMENT. The line reads '`2026-09-05-leave-group-writespec.md:31` "
        "| `linkedin_leave_group` | discuss (spec) | `MARKED-SPEC-DOC` | yes'. "
        "The WriteSpec is one of the labelled sites in this wave's "
        "hand-versus-guard census, and the label says the WriteSpec marked "
        "its own name correctly -- it declares 'This is a SPECIFICATION, not "
        "a build.' and thereby earns the suppressor. The wave cites it as "
        "the corpus receipt for a marker class, which is the opposite of "
        "correcting it. "
    ),

    # 2026-09-20, the same wave's third pair. The correction vocabulary here is
    # the word "wrong" applied to a REPOSITORY, not to a claim.
    ("2026-09-20-names-that-do-not-exist.md", "2026-08-31-jobcore-paths.md"): (
        "IT EXPLAINS WHY TWELVE CITATIONS ARE NOT DEFECTS. The passage "
        "reports that 12 of 134 strict-unresolved path citations come from "
        "that document, and then says why they are fine: it 'is explicitly "
        "comparing against a SIBLING project's suite. Real files, wrong "
        "repo, and no prefix rule can reach them because they carry no "
        "marker.' The wave is ACQUITTING those citations on the strength of "
        "the document's own stated scope. Clearing another document is not "
        "correcting it. "
    ),

    # 2026-09-20. The register pointing at the wave report that produced the
    # entry. The correction vocabulary is the ENTRY'S SUBJECT -- two numbers
    # that wave got wrong and corrected in itself -- not a relation between the
    # two files.
    ("INSTRUMENTS.md", "2026-09-20-names-that-do-not-exist.md"): (
        "IT IS A REGISTER ENTRY CITING ITS OWN SOURCE DOCUMENT. Section 24.6 "
        "declares twelve scratch probes disposable and closes 'Their numbers "
        "are the tables in `_audit/2026-09-20-names-that-do-not-exist.md`.' "
        "Section 24.5 above it is headed 'TWO NUMBERS THIS WAVE GOT WRONG' -- "
        "self-corrections the wave made and published in that same report, "
        "which is what puts correction vocabulary near the citation. A "
        "register naming where an instrument's workings live is a POINTER. "
        "If it were a correction the arrow would run the wrong way: the "
        "report is the source, not the target. "
    ),

    # 2026-09-20, the same wave's fourth pair, and the shape is worth naming:
    # a document correcting ITSELF, inside a block quote, about a third file it
    # had mis-described. The correction vocabulary is real; its target is the
    # citing document's own earlier sentence, not the file it names.
    ("2026-09-20-names-that-do-not-exist.md", "jobs.md"): (
        "IT IS A SELF-RETRACTION THAT CLEARS THE NAMED FILE. The quoted block "
        "opens 'THIS SECTION FIRST SAID' and withdraws this wave's own claim "
        "that nine rows of `_census/jobs.md` rest their evidence on an "
        "unresolvable commit. The census is not wrong: its column is headed "
        "`source` and holds LinkedIn Help Center article ids, which the same "
        "file writes elsewhere as `help/linkedin/answer/a512388`. The wave "
        "had resolved them against git, which is a true answer to a question "
        "nobody asked. A CORRECTS: marker would tell a reader this document "
        "supersedes the census, when what it supersedes is its own paragraph. "
    ),

    # TWO FROM THE CONTINGENT-WRITEOFFS WAVE, surfaced 2026-09-20 when the
    # newsletter wave strengthened this scan. Both are the SAME SHAPE, and it is
    # a shape worth naming: a document REPORTING THAT A THIRD DOCUMENT CORRECTED
    # ITSELF. The correction vocabulary is real, but it describes somebody else's
    # self-correction inside their own session, and the citing wave goes on to
    # ENDORSE the corrected reasoning rather than supersede it. A CORRECTS:
    # marker here would tell a reader that the later file replaces the earlier,
    # which is the opposite of what the passage says.
    ("2026-09-20-the-contingent-writeoffs.md", "2026-09-05-network-tail.md"): (
        "IT NARRATES A SELF-CORRECTION AND THEN AGREES WITH IT. The passage "
        "reads '`_audit/2026-09-05-network-tail.md` s3 corrects its own "
        "`allowlist +1` in the same session, on the right ground', and closes "
        "the paragraph with '**The address reasoning is right.**' The wave's "
        "own finding is a DIFFERENT question it says nobody joined -- whether "
        "the section is drawn at all. Citing a document for a correction it "
        "made to itself, and endorsing the result, is not correcting it. "
    ),
    ("2026-09-20-the-contingent-writeoffs.md", "2026-09-05-lead-rulings-round-two.md"): (
        "IT COUNTS THE DOCUMENT AS EVIDENCE THAT A REASON EXISTS. The passage "
        "is the orphan tally -- 'named SOMEWHERE outside the seven: 34, named "
        "NOWHERE at all: 0' -- and cites this ruling as the clean example of a "
        "blocker whose reason was written down twice and simply not in the "
        "seven documents the sweep read. The correction vocabulary belongs to "
        "the OTHER file named in the same sentence, which corrected its own "
        "cost. Naming a ruling as present is the opposite of correcting it. "
    ),

    ("jobs.md", "2026-09-20-job-search-params-built.md"): (
        "A CENSUS CELL CITING THE WRITE-UP THAT EVIDENCES ITS NEW STATE. "
        "Row 151 moved to COVERED-UNFIRED on 2026-09-20 and the cell names "
        "the document that records what shipped and why it is UNFIRED "
        "rather than PROVEN. The build write-up is the EVIDENCE for the "
        "state change, exactly as four earlier census cells cite the "
        "documents that evidenced theirs. The cell is a row showing its "
        "work. "
    ),

    # TWO MORE, 2026-09-19, from the remaining-partials wave. Both cite the
    # record that SETTLES a question. The third candidate that wave produced IS
    # a real correction -- of a RULING, not of a slice -- and is declared with a
    # CORRECTS:/CORRECTED BY: pair instead of an entry here.
    ("2026-09-19-the-remaining-partials.md", "messaging-and-content.md"): (
        "THE CENSUS IS THE RECORD THAT KILLS A CLAIM, NOT THE CLAIM BEING "
        "KILLED. The sentence reads 'That is dead:' followed by what the "
        "slice's own C48 note records. The census is quoted as the "
        "authority that settles it; nothing in it is asserted wrong. Sixth "
        "instance tonight of proximity matching pairing a corrector with "
        "its evidence. "
    ),
    ("2026-09-19-the-remaining-partials.md", "profile.md"): (
        "A ROW'S SLICE AND SECTION STATED AS A FACT. The passage identifies "
        "Newsletter analytics as a profile.md section L row while testing "
        "whether an over-published neighbour holds a row of the creator-hub "
        "family. profile.md is the record consulted to establish where a "
        "row lives, which is the ordinary use of a census slice and not a "
        "correction of it. "
    ),

    # THREE MORE, 2026-09-19, from the unassigned-21 wave. All three cite the
    # record that SETTLES a dispute rather than a record being corrected. The
    # genuine correction that wave made -- against the row-walk, not against any
    # census slice -- is declared with a CORRECTS:/CORRECTED BY: pair instead,
    # which is what this table exists to leave room for.
    #
    # FOURTH AND FIFTH INSTANCE TONIGHT of the scan pairing a corrector with its
    # EVIDENCE. That is proximity matching working as designed; it is not a
    # defect, and five instances in one evening is the reason to say so here.
    ("2026-09-19-the-unassigned-21.md", "jobs.md"): (
        "A COLUMN OF THE CENSUS REFUTES AN OBJECTION MADE AGAINST A RULING. "
        "The objection was that a section test proves too much because J "
        "78-J 83 all sit in section D; the refutation is measured over "
        "jobs.md's citation column, where J 81 and J 82 share a Help-Center "
        "id occurring exactly twice while the six rows carry four distinct "
        "ids. jobs.md is quoted as the discriminator, not contradicted -- "
        "the ruling it supports is CONFIRMED, not overturned. "
    ),
    ("2026-09-19-the-unassigned-21.md", "profile.md"): (
        "THE SLICE PROVES THE ARITHMETIC WRONG, IN ITS OWN WORDS, WHICH IS "
        "THE PHRASE THE SCAN MATCHED. An arithmetic argument closes for P "
        "D24 against OPEN-TO-HIRING-MODAL's last W slot; the wave then "
        "shows profile.md itself refutes the reading the arithmetic rests "
        "on. What is wrong is the argument the wave had just built and then "
        "abandoned, and profile.md is what killed it. A file quoted to kill "
        "an argument is not a file being corrected. "
    ),

    # THREE MORE, 2026-09-19, from the premium-apply wave. All citations. The
    # first refutes MY OWN BRIEF rather than the document it cites, which is
    # worth keeping: a wave correcting the orchestrator is not a document
    # correcting a document.
    ("2026-09-19-premium-apply-surfaces.md", "2026-09-19-routing-the-unassigned.md"): (
        "THE THING BEING REFUTED IS MY BRIEF, NOT THE CITED DOCUMENT. I "
        "handed the wave seven candidate rows chosen from their titles, "
        "warning that a title is not evidence. The wave checked one of "
        "them, J 150, found the blocker it resembles is COMPLETE at 2 of 2 "
        "with no room per the routing pass, and wrote that the brief's "
        "inclusion of it on its title is refuted. The routing pass is the "
        "source that SUPPLIED the refutation and is not itself corrected. "
    ),
    ("2026-09-19-premium-apply-surfaces.md", "2026-09-19-the-three-ruling-requests-ruled.md"): (
        "IT HONOURS THE RULING AND SAYS SO IN THREE WORDS: Not re- "
        "litigated. The passage notes that a 1R/4W split would close if J "
        "82 were the read, records that the filing was made and retracted, "
        "and then states that Request 4 ruled the ledger's 1R an error and "
        "closed the door -- quoting the ruling's own sentence that the 1R "
        "may no longer be cited as evidence in any filing. A wave declining "
        "to reopen a ruling is the opposite of correcting it. "
    ),
    ("2026-09-19-premium-apply-surfaces.md", "jobs.md"): (
        "THE CENSUS IS THE CORRECT SOURCE, QUOTED TO REFUTE A THIRD "
        "DOCUMENT. The correction vocabulary belongs to a sentence about "
        "cheap-reads.md, which the wave measures as a paraphrase wrong on "
        "two of its three items; jobs.md section H is quoted verbatim as "
        "the record that settles it, and PREMIUM-JOBS-SURFACES is COMPLETE "
        "at 3 of 3 on exactly those rows. This is the THIRD time tonight "
        "the scan has paired a corrector with its EVIDENCE rather than with "
        "what it corrects -- a property of proximity matching, recorded "
        "here rather than filed as a defect. "
    ),

    # SEVEN MORE, 2026-09-19, AFTER THE THREE-WAVE CENSUS ROUND, each read in
    # context before declaring. Six are plain citations. The seventh is a
    # passage using the word "correction" about a THIRD document which turns
    # out to agree with it already -- so the pair the scan produced is not the
    # pair the sentence is about. That is a property of proximity scanning and
    # is recorded in the entry rather than filed as a defect in the scan.
    ("2026-09-19-partial-blockers-closed.md", "2026-09-19-the-three-ruling-requests-ruled.md"): (
        "IT UPHOLDS THE RULING AND SAYS SO. The sentence is AND THE RULING "
        "IT WOULD HAVE OVERTURNED -- conditional, about a case the wave "
        "built and then refuted itself -- and it calls the ruling's test "
        "the blocker's own name restated, not a test invented to fit, which "
        "is agreement. A document reporting why it did NOT overturn "
        "something is the opposite of a correction. "
    ),
    ("2026-09-19-partial-blockers-closed.md", "messaging-and-content.md"): (
        "THE CENSUS IS THE EVIDENCE FOR A CASE THE WAVE THEN REFUTED. The "
        "line opens The case I built and quotes the census grouping to "
        "state that case; section 3.2 then kills it on an address, "
        "concluding that a census family groups by SUBJECT while a blocker "
        "groups by WHAT BLOCKS IT. The census is quoted, not contradicted "
        "-- the wave's own reading of it is what changed. "
    ),
    ("2026-09-19-the-row-walk.md", "2026-09-03-linkedin-gap-blockers.md"): (
        "A RULING REQUEST, NOT A CORRECTION, AND THE DOCUMENT DECLINES TO "
        "ACT. It says it thinks the ruling answers the wrong question and "
        "cites the ledger's own ASSIGNMENT RULE at L166-169 as the right "
        "one -- then files NOTHING, writing that if the ruling flips six "
        "rows resolve at once and two blockers close, which is exactly why "
        "it did not file. Nothing in the ledger is asserted wrong; a "
        "question is asked of whoever rules. "
    ),
    ("2026-09-19-the-row-walk.md", "2026-09-19-the-empty-blockers.md"): (
        "CORROBORATION, EXPLICITLY INDEPENDENT. The line registers a false- "
        "positive class and adds that it re-derived the same thing "
        "independently from the ledger table BEFORE reading that "
        "registration. Two waves reaching one conclusion by separate routes "
        "is the strongest evidence this census produces, and is the "
        "opposite of one document correcting another. "
    ),
    ("2026-09-19-the-row-walk.md", "2026-09-19-the-three-ruling-requests-ruled.md"): (
        "IT REPORTS THE RULING RETIRING ITS OWN DISCRIMINATOR. The quoted "
        "sentence is the ruling's own: that the 1R may no longer be cited "
        "as evidence in any filing, written after a row filed on it was "
        "retracted. The row-walk cites that retirement to explain why no "
        "discriminator remains. Reporting what a ruling did to itself is "
        "citation. "
    ),
    ("2026-09-19-the-row-walk.md", "messaging-and-content.md"): (
        "THE CENSUS SUPPLIES THE FACT AND THE DOCUMENT UNDER DISCUSSION IS "
        "A DIFFERENT ONE. The passage reads M 1's state from messaging-and- "
        "content.md:332 as EVIDENCE. Checked 2026-09-19: the document it "
        "discusses, blocker-table-refresh.md:37, ALREADY records M 1 as "
        "moved to COVERED-CANNOT-DELIVER -- so the two agree and nothing is "
        "corrected. The correction vocabulary sits beside the evidence "
        "citation rather than beside any corrected claim, which is why "
        "proximity scanning paired it this way. "
    ),
    ("2026-09-19-the-row-walk.md", "profile.md"): (
        "THE SLICE FILE IS READ TO REFUTE AN ARGUMENT ABOUT SLICES. The "
        "point made is that the blocker's two filed rows are both "
        "profile.md rows, so wrong slice was never the bar. profile.md is "
        "the record consulted to establish where the existing rows live. A "
        "file read to settle a question is not a file being corrected. "
    ),

    # TWO MORE, ADDED 2026-09-19 AFTER READING BOTH LINES. Each was produced by
    # today's landings, and in each the correction vocabulary belongs to a
    # sentence ABOUT a correction rather than to a correction being made.
    ("2026-09-19-routing-the-unassigned.md", "messaging-and-content.md"): (
        "A ROUTING DOCUMENT READING THE CENSUS AS EVIDENCE, and it says so in "
        "its own words two lines above the match: 'I am not overturning a "
        "ruling. I am reporting that its stated ground moved.' It quotes "
        "messaging-and-content.md L498 to establish which eleven items the "
        "conversation-management row enumerates, then observes that nine are "
        "already filed and the two that are not -- M M35 (layout) and M M49 "
        "(delivery indicators) -- match the blocker's unfilled 1R/1W split. "
        "The census file is the SOURCE being read, not a document being "
        "corrected; nothing in it is asserted wrong."
    ),
    ("2026-09-19-the-my-items-premise-is-sheltered.md", "2026-09-19-content-tail.md"): (
        "THE WORD 'CORRECTED' DESCRIBES WHAT THE CITED DOCUMENT DID, NOT WHAT "
        "THIS ONE DOES TO IT. The line reads 'content-tail.md section 4.1 "
        "corrected upward on the ground that the /my-items/ redirect is "
        "asserted, never measured' -- that is content-tail correcting its own "
        "cost estimate, reported here as the premise this document then goes "
        "and tests offline. Its conclusion agrees with content-tail: nothing "
        "fired, no pattern moved, C36 and C37 stay GAP. A document that "
        "investigates another's premise and confirms it is not correcting it."
    ),
    # FOUR ENTRIES BELOW, ADDED 2026-09-19 AFTER READING EVERY LINE.
    # A census cell citing the document that EVIDENCES a state is not a
    # document correcting another document -- it is a row showing its work.
    #
    # TWO OF THEM ARE ANOTHER WAVE'S ROWS AND I TOOK THEM ANYWAY, which needs
    # saying. The standing rule is that you do not vouch for a claim you did
    # not write -- it is why an ENROLLED row needs its author. This is the
    # other kind: "is this line a correction or a citation" is answerable by
    # READING THE LINE, which the guard's own message demands and which I did.
    # The cost of waiting was a sibling wave blocked from committing at all,
    # because this guard refuses any commit that stages a test file.

    # A census cell citing the document that EVIDENCES a state change is not a
    # document correcting another document -- it is a row showing its work. The
    # correction vocabulary is in the cell's own account of what it used to say.
    ("jobs.md", "2026-09-19-tier1-fires.md"): (
        "the cell records unsave_job moving from NO. NEVER FIRED to FIRED AND "
        "VERIFIED, and cites the fire's write-up as its EVIDENCE. The cited "
        "document corrects nothing in jobs.md -- it did not exist when that "
        "cell was written, and the cell supersedes ITSELF, keeping six earlier "
        "citations because they were accurate when written. A CORRECTED BY: "
        "pointer would claim the fire report found a fault in the census, when "
        "what it did was supply the measurement the cell had been waiting for"
    ),
    # TWO ENTRIES WERE REMOVED FROM HERE ON 2026-09-20, AND PYTHON HAD ALREADY
    # REMOVED THEM. ("jobs.md", "2026-08-30-linkedin-undo.md") and
    # ("profile.md", "2026-08-31-linkedin-finish.md") were each declared TWICE
    # in this dict -- once here and once further down. A duplicate key in a dict
    # literal is not an error: the later value silently wins, so the reasons
    # written here were dead text that no test could reach and no reader could
    # tell was dead. Both survivors are strict supersets -- each also answers
    # for the NEIGHBOURING row that the +-2 window reaches, which is the half
    # the entries here did not address -- so nothing was argued away.
    #
    # Found while resolving a merge, by a check that ITSELF could not fail on
    # its first attempt: it walked for `ast.Assign` and this is an `ast.AnnAssign`,
    # so it reported nothing and looked like a clean result.
    # `test_no_declaration_is_silently_shadowed` below now holds the property.
    ("profile.md", "2026-09-19-tier1-fires.md"): (
        "same shape as the jobs.md entry above and for the same reason: the "
        "cell records update_setting's WRITE moving to FIRED AND VERIFIED -- "
        "off to on to off, each state read back after a fresh navigation -- "
        "and cites the write-up as the evidence for that move. The row's own "
        "reversibility_class had printed STILL-UNKNOWN until that round trip, "
        "so the citation is the row being satisfied rather than corrected"
    ),
    ("2026-09-19-duplicate-register.md", "jobs.md"): (
        "the fault described is the CITING document's own, not the cited "
        "slice's. jobs.md writes XR where the other three slices write "
        "EXCLUDED-RULED -- a legitimate shorthand that slice has used "
        "throughout -- and the register records that MY same-state filter "
        "compared state strings literally and therefore read every agreement "
        "spelled in two dialects as a disagreement. The repair vocabulary is "
        "me describing a bug in my own instrument. A CORRECTED BY: pointer on "
        "jobs.md would credit that slice with an error belonging to a parser "
        "written against it"
    ),
    ("2026-09-19-the-cross-slice-round.md", "jobs.md"): (
        "same reason, in the round write-up: the six-failure table names XR "
        "versus EXCLUDED-RULED as failure 5, and the failure is the reader's. "
        "count_census_states.py documents this same dialect costing IT 23 "
        "invisible rows, so the hazard is a known property of the corpus that "
        "instruments must accommodate -- not a defect in jobs.md, which is "
        "internally consistent. Nothing that slice asserts is contradicted"
    ),
    ("profile.md", "network.md"): (
        "the citation names an AUTHORITY, not a corrected party. Census row "
        "P B10 was flipped GAP -> EXCLUDED-RULED and its note cites "
        "network.md:814 -- ruling R11, 'the settings family is admitted by name "
        "or not at all' -- as the ruling that governs it, together with the "
        "twin N159 that already carried that verdict. network.md is where the "
        "rule is written down and it is asserted CORRECT, not wrong; the row "
        "that changed is the profile one. The repair vocabulary near the "
        "citation is B10 describing what was wrong with ITS OWN prior state "
        "(GAP on the words 'no tool, no reason'). A CORRECTED BY: pointer on "
        "network.md would tell a reader its ruling had been refuted by a row "
        "that exists only because it applied it"
    ),
    ("profile.md", "2026-09-05-decide-retire-rulings.md"): (
        "CROSS-ROW PROXIMITY, measured before the reason was written. The "
        "citation is on line 205, row A23 (name pronunciation audio, retired "
        "MOBILE-APP-ONLY), and A23 carries NO correction vocabulary at all. "
        "The only vocabulary in the two-line window is 'wrong' on line 204 -- "
        "row A22, a different capability (Primary Position in the intro "
        "editor), where it belongs to this wave stating that the BLOCKER'S "
        "PREMISE is wrong because the controls have now been read. Neither "
        "the word nor the row has anything to do with the retire-rulings "
        "document A23 cites. A census table has one row per LINE, so a "
        "line-based window reaches ACROSS rows -- the same shape already "
        "recorded twice in this table"
    ),
    ("messaging-and-content.md", "2026-09-19-the-disclosing-press-ruling.md"): (
        "the cited document is the GRANTING AUTHORITY and the row is applying "
        "it. C 72 cites the disclosing-press ruling to record which of its "
        "four conditions refuses this press and that the refusal is "
        "reachable_by_this_route -- NOT YET rather than NEVER. The four "
        "vocabulary words in that cell all belong to THIS WAVE CORRECTING "
        "ITSELF, twice: the row first said no counter prices a feed press, "
        "and the cell now records that reading as ACCURATE AND IRRELEVANT "
        "because the nav badges could not have moved for the act in question. "
        "A self-correction in place, citing the ruling it obeys. A CORRECTED "
        "BY: pointer in the ruling would tell a reader that the document "
        "granting the permission had been refuted by a row obeying it"
    ),
    ("2026-09-19-cross-slice-rulings.md", "jobs.md"): (
        "a STRUCTURAL GAP is reported, not a claim refuted. Amendment C "
        "measures that jobs.md carries no R/W column at all -- 151 rows, 0 "
        "with a value, against 199/138/208 in the other three slices -- and "
        "explains that the author's own earlier '74% unknown' was that hole "
        "rather than a parser bug. Nothing jobs.md ASSERTS is contradicted; "
        "the finding is about a column it does not have. A CORRECTED BY: "
        "pointer would tell a reader the slice's content had been refuted, "
        "when what was found is that a field was never recorded"
    ),
    ("2026-09-19-cross-slice-rulings.md", "profile.md"): (
        "profile.md is cited on the same line as the COMPARISON that makes "
        "the jobs.md gap legible -- it records R/W for 199 of 202 rows. Being "
        "named as the well-formed case is not being corrected. The repair "
        "vocabulary near the citation belongs to the jobs.md clause"
    ),
    ("2026-09-19-profile-modals-measured.md", "profile.md"): (
        "the correction is of MY OWN DOCUMENT and profile.md is the thing I "
        "misread, not the thing that was wrong. The banner retracts this "
        "document's claim that blocker 20's rows were profile.md I2-I12: "
        "those rows were EXCLUDED-RULED at the frozen commit and so were "
        "never in the GAP set the ledger divided. profile.md recorded that "
        "correctly the whole time; I identified rows on a count-and-R/W match "
        "without checking frozen-set membership. A CORRECTED BY: pointer on "
        "profile.md would credit it with an error that was mine"
    ),
    ("2026-09-19-scope-jobs-rw-column.md", "jobs.md"): (
        "a COSTING of a structural change, explicitly not an edit and not a "
        "refutation. The document prices adding the R/W column jobs.md lacks "
        "-- 66 rows needing judgement, 179 lines in the diff, no "
        "position-sensitive guard found -- and states in its own last section "
        "that no cell was added and no row touched. Nothing jobs.md says is "
        "asserted wrong"
    ),
    ("messaging-and-content.md", "2026-09-05-article-publish.md"): (
        "the citation is the RULING'S OWN AUTHORITY, not a document being "
        "corrected. Rows M23, C66 and C86 were retired 2026-09-19 on the "
        "mention/tag ACTION-CLASS ruling, and each note cites the document "
        "that reached that ruling in order to say WHOSE ruling is applied. "
        "The phrase that trips the vocabulary is 'only half applied' -- and "
        "that is a statement about the CENSUS, not about the cited document, "
        "which said the remainder was owed in its own words: 'whoever holds "
        "the map should apply it ROW BY ROW rather than take my count'. "
        "Completing an instruction a document gives is the opposite of "
        "correcting it. Note also that the same document IS corrected "
        "elsewhere and that pair is declared properly -- its Amendment E "
        "retracts its own section 1 -- so this entry is not a blanket "
        "exemption for the file, only for the retirement rows quoting its "
        "ruling"
    ),
    ("jobs.md", "2026-08-31-linkedin-perform.md"): (
        "the cited document was RIGHT WHEN WRITTEN and is not corrected by "
        "this row -- MEASURED, not argued. J 127 quoted it for 'the boundary "
        "entry and reader are NOT built'. readonly.is_read_url on that "
        "address returns True today, but the allowlist entry landed in "
        "f80526e on 2026-09-01, the day AFTER that document is dated. So the "
        "document reported the tree it saw and nothing in it is wrong. What "
        "expired is THIS ROW's inheritance of a dated reading, and the row "
        "now says so in those terms. A CORRECTED BY: pointer in the perform "
        "document would tell a reader it had been refuted, when what actually "
        "happened is that a condition it correctly reported changed a day "
        "later -- the relayed-measurements-go-stale law with a census row as "
        "the receiver"
    ),
    ("profile.md", "2026-09-19-settings-tail-addresses.md"): (
        "the citation is CORROBORATION and the cited document is not asserted "
        "wrong. Census row P B10 was flipped GAP -> EXCLUDED-RULED under "
        "network.md's ruling R11, and its note cites the settings-tail audit "
        "for the independent half of the evidence: that document enumerated "
        "the 20 addresses the settings index draws and found this toggle is "
        "not among them, which is what places it behind a denylisted "
        "categories/ page. That audit's own conclusion on this row was that "
        "the charge against it is NOT an allowlist addition but 'either a "
        "denylist narrowing or a modal with no address' -- and R11 is exactly "
        "the denylist ruling. So the flip carries that finding one step "
        "further rather than refuting any part of it. The repair vocabulary "
        "near the citation is the row describing what was WRONG WITH ITS OWN "
        "PRIOR STATE (GAP on the words 'no tool, no reason'), not with the "
        "document it cites. A CORRECTED BY: pointer would tell a reader the "
        "settings-tail measurement had been overturned by a row that rests on it"
    ),
    ("network.md", "2026-09-19-the-disclosing-press-ruling.md"): (
        "the cited document is the GRANTING AUTHORITY and the row is applying "
        "it, not overturning it. N 133 and N 134 cite the disclosing-press "
        "ruling to record that they are now blocked on the MECHANISM rather "
        "than on a ruling. MEASURED which line carries the vocabulary, "
        "because assuming it would have produced a wrong reason twice today: "
        "the words are on lines 436 and 437, the SAME rows that carry the "
        "citation, and they belong to a sentence about an ANALYTICS WAVE "
        "correcting ITSELF -- its section 1 reported the page carries no such "
        "controls and its section 11 measured that false. That self-correction "
        "predates the ruling by a fortnight and has nothing to do with it. A "
        "CORRECTED BY: pointer in the ruling would tell a reader that the "
        "document granting the permission had itself been refuted by a row "
        "obeying it"
    ),
    ("messaging-and-content.md", "2026-09-05-groups-surface-measured.md"): (
        "the cited document is the MEASURING SOURCE and the row AGREES with "
        "it. C61 (join a group) was re-costed from MEASURE to DECIDE on that "
        "wave's finding that no join control is drawn on any suggestion row, "
        "and cites it for exactly that. The correction vocabulary beside the "
        "citation belongs to this row re-costing ITSELF -- the ledger's "
        "queue column is what is called wrong, and the ledger is a THIRD "
        "document the scan cannot see from this pair. Nothing in the groups "
        "measurement is contradicted; it is the evidence"
    ),
    ("network.md", "2026-09-03-linkedin-gap-blockers.md"): (
        "the cited document ALREADY MADE this correction and the row is "
        "agreeing with it, not overturning it. N 136 moved to "
        "MEASURED-ABSENT citing the ledger's own section 6, which had "
        "already corrected the census: the live page carries a Company "
        "FILTER and no top-locations breakdown. A CORRECTED BY: pointer in "
        "the ledger would tell a reader that the document which got this "
        "right first had been refuted by a row quoting it"
    ),
    ("messaging-and-content.md", "2026-09-05-decide-retire-rulings.md"): (
        "CROSS-ROW PROXIMITY, and the two halves are in DIFFERENT ROWS with "
        "nothing to do with each other. MEASURED: the citation is on line "
        "448, row C59 (LinkedIn Live), and C59 carries NO correction "
        "vocabulary at all. The only vocabulary within the two-line window "
        "is the word 'stale' on line 449 -- row C60, a different capability, "
        "where it describes C60's OWN cell having been stale about the "
        "/groups/ boundary. **A census table has one row per LINE, so a "
        "line-based window reaches ACROSS rows**: one row's vocabulary "
        "manufactures a candidate on its neighbour's citation. This is the "
        "complement of the table-row proximity shape already recorded for a "
        "single 2.4k-character row; the window runs unbounded ALONG a row "
        "and two rows DEEP through the table"
    ),
    ("network.md", "2026-09-05-search-appearances-load-a.md"): (
        "CROSS-ROW PROXIMITY, same shape as the "
        "('messaging-and-content.md', '2026-09-05-decide-retire-rulings.md') "
        "entry above and measured the same way. The citation is on line 435, "
        "row N 132 (switch between search appearances and who-viewed), which "
        "carries NO correction vocabulary. The words 'correction' and "
        "'false' sit on lines 436 and 437 -- rows N 133 and N 134, different "
        "capabilities on a different page, where they describe an analytics "
        "wave correcting ITSELF about which controls render. Neither word is "
        "about the search-appearances document and neither is in the row "
        "that cites it"
    ),
    ("messaging-and-content.md", "network.md"): (
        "TABLE-ROW PROXIMITY and a DECLINE TO RULE, and both halves were "
        "measured rather than inferred. The row is C52, and a markdown table "
        "row is ONE LINE, so every phrase in a 2.4k-character cell sits at "
        "line-distance zero from every other phrase in it. The scan finds "
        "exactly ONE vocabulary word in that row -- 'corrected', at character "
        "2145 -- against the network.md citation at character 1885: 260 "
        "characters apart with no newline between them. "
        "THAT WORD IS THE ROW'S OWN PRE-EXISTING MARKER, "
        "'**ROW CORRECTED 2026-09-03.**', which records that this cell once "
        "read 'Follow a hashtag / topic' sourced to a help article that "
        "returns HTTP 404. It was written sixteen days before the network.md "
        "sentence, it corrects THIS ROW and no other document, and it names "
        "no slice at all. The two are adjacent only because a table row "
        "cannot contain a blank line. "
        "The network.md mention is the OPPOSITE of a correction and says so "
        "in its own words: '**This does NOT rule on network.md rows 59-61**'. "
        "Those rows record that LinkedIn may have retired the member "
        "hashtag-follow surface, and they were DELIBERATELY kept mapped "
        "because removing capabilities on an inference is the same undercount "
        "that pass exists to fix. The 2026-09-19 reading behind C52 is of the "
        "FEED -- zero rendered hashtag anchors and zero /feed/hashtag/ hrefs "
        "across four loads -- and a feed that surfaces no hashtag anchors is "
        "consistent BOTH with the follow surface having been retired AND with "
        "its existing somewhere the feed does not link to. So the evidence is "
        "genuinely non-dispositive for rows 59-61, which is why the row "
        "declines to rule on them instead of quietly retiring them. A "
        "CORRECTED BY: pointer in network.md would tell a reader those rows "
        "had been refuted by a measurement whose own sentence refuses to "
        "refute them"
    ),
    ("messaging-and-content.md", "2026-09-19-settings-tail-addresses.md"): (
        "the row CORRECTS ITSELF IN PLACE and cites the 09-19 addresses "
        "document as its REASON -- the same shape as the "
        "('messaging-and-content.md', '2026-09-19-content-tail.md') entry "
        "above. C52 was moved to MEASURED-ABSENT by 09d56d4 on a live read of "
        "the FEED; that was the wrong surface for this row and the cell now "
        "withdraws the state IN the cell, dated, citing the sibling wave that "
        "measured the real address (/mypreferences/d/unfollowed, refused at "
        "the forbidden-substring gate by '/unfollow'). So the row NAMES ITS "
        "OWN CORRECTOR and the reachability this file exists to guarantee is "
        "already satisfied without a marker pair. The cited document is not "
        "wrong about anything -- it is the corrector, and it explicitly "
        "declined to adopt my state change and flagged it as not its claim, "
        "which is why the correction had to come from this side. A CORRECTED "
        "BY: pointer in it would tell a reader that the document supplying "
        "the measurement had itself been refuted"
    ),
    ("messaging-and-content.md", "2026-09-05-settings-tail.md"): (
        "the cited document was RIGHT and this row now agrees with it. "
        "settings-tail.md:224 lists 'FEED-PREFERENCES | M C52' fully "
        "qualified, with no bare-id ambiguity to resolve; the corrected C52 "
        "cell cites it as CORROBORATION that the row is FEED-PREFERENCES "
        "rather than HASHTAG-EXISTENCE. The correction vocabulary in the cell "
        "is this wave withdrawing ITS OWN state, not a claim about "
        "settings-tail.md, which asserted the correct assignment before this "
        "wave existed. A CORRECTED BY: pointer there would tell a reader that "
        "the one source that had it right all along had been refuted"
    ),
    ("messaging-and-content.md", "2026-09-06-corpus-sweep-blocker-evidence.md"): (
        "ANSWERING AN OPEN QUESTION THE CITED DOCUMENT ITSELF POSED, which is "
        "not correcting it -- the 'open question that declines to rule' shape "
        "the preamble above names, arriving from the other end. That "
        "document's section 3 finding C sets out a conflict over M C52 and "
        "expressly leaves it unresolved, in its own words: 'One of them is "
        "wrong, or the ledger's bare C 52 was never M C52 at all.' The "
        "corrected C52 cell settles that conflict with a measured address and "
        "says which. A document that frames a dichotomy and invites a "
        "resolution is not refuted by being handed one; finding C is doing "
        "exactly what it was written to do. The correction vocabulary beside "
        "the citation belongs to this row withdrawing its own MEASURED-ABSENT "
        "state, not to any claim in the sweep document. A CORRECTED BY: "
        "pointer there would tell a reader the question had been wrong to ask"
    ),
    ("2026-09-19-content-tail.md", "2026-09-03-linkedin-gap-blockers.md"): (
        "the cited document is the REFUTING SOURCE, not the refuted one, and "
        "the thing being corrected is a THIRD file the scan cannot see. "
        "Section 10 reports that `_audit/_census/blocker-map.tsv` files row "
        "M C2 as UNASSIGNED with the note 'no committed source names this row "
        "against any blocker' -- and the blockers document refutes that at "
        "L716, inside Amendment A3, by naming the row verbatim. So the "
        "correction vocabulary near the citation is the ledger being quoted "
        "as EVIDENCE that a TSV is wrong. A CORRECTED BY: pointer in the "
        "blockers document would tell a reader that the document supplying "
        "the refutation had itself been refuted, which is the same inversion "
        "the two profile.md entries below record from their own directions. "
        "The TSV is not markdown and is outside this corpus by construction, "
        "so the pair the scan CAN see is the only one available and it is the "
        "wrong two documents"
    ),
    ("messaging-and-content.md", "2026-09-19-content-tail.md"): (
        "the row CORRECTS ITSELF IN PLACE and cites this wave's document as "
        "its REASON -- the same shape as the "
        "('profile.md', '2026-09-05-search-results-consent.md') entry below. "
        "C36 read that saved posts are 'one allowlist entry away'; the 09-19 "
        "annotation says that rests on an unmeasured premise and dates the "
        "correction in the cell, so the row NAMES ITS OWN CORRECTOR and the "
        "reachability this file exists to guarantee is already satisfied "
        "without a marker pair. The citing document is not wrong about "
        "anything here and needs no CORRECTED BY: pointer; it is the "
        "corrector. Ten sibling rows in the same slice carry the same "
        "dated-in-place shape from the same wave, and C36 is the one whose "
        "vocabulary trips the scan"
    ),
    ("2026-09-19-settings-tail-addresses.md", "2026-09-05-settings-tail.md"): (
        "the cited claim is CONDITIONAL and survives intact. The 09-05 wave "
        "wrote that FEED-PREFERENCES is substring-blocked and so cannot be "
        "reached by an allowlist edit -- expressly hedged, in its own words, "
        "as true 'even if that is its address'. It never asserted an address. "
        "The 09-19 wave read the real one off LinkedIn's settings index "
        "(/mypreferences/d/unfollowed, refused by '/unfollow' rather than the "
        "illustrative /feed/follows/ refused by '/follow') and reached the "
        "SAME verdict by the same gate. So nothing in the 09-05 document is "
        "asserted wrong: a conditional whose consequent is confirmed is not "
        "refuted by learning its antecedent. The repair vocabulary near the "
        "citation is the 09-19 wave describing the REASONING ROUTE -- that a "
        "guessed address happening to reach the right verdict still leaves "
        "the row unmeasured -- which is a remark about method, not a claim "
        "that the conclusion is false. A CORRECTED BY: pointer would tell a "
        "reader the 09-05 analysis had been refuted by a document whose own "
        "heading says it sharpens that analysis rather than overturning it"
    ),
    ("2026-09-05-article-publish.md", "INSTRUMENTS.md"): (
        "a handover note about WHO COMMITS the register, not a claim about "
        "what it contains. The wave found another wave's 49 uncommitted "
        "lines inside its own contiguous hunk, backed its 69 out, left "
        "theirs byte-identical, and moved its own entry into its audit doc "
        "for the lead to lift. The repair vocabulary is 'its number will be "
        "wrong' -- said of the section number its OWN proposed entry would "
        "carry, because a neighbour was mid-write in the same file. Nothing "
        "in INSTRUMENTS.md is asserted wrong, and a CORRECTED BY: pointer "
        "would tell a reader the register had been refuted by a document "
        "that only declined to edit it"
    ),
    ("2026-09-05-census-hygiene.md", "network.md"): (
        "a RECONCILIATION table and an open-question list, not a correction. "
        "The census-hygiene wave restored visibility to 37 rows that no "
        "counter could see and cited each slice to say how its row total now "
        "reconciles against the ledger's 705. The repair vocabulary near the "
        "citation is the wave describing what it did to the ROWS, and the "
        "network citation flags an open question it deliberately did NOT "
        "settle -- five recommendation rows now read EXCLUDED-RULED because "
        "their section heading says so, while the paragraph beneath calls "
        "them unmeasured. Nothing in that slice is asserted wrong: the state "
        "column was ADDED where none existed, carrying the heading's own "
        "value. A CORRECTED BY: pointer would tell a reader the slice had "
        "been refuted by a document that only made it countable"
    ),
    ("2026-09-05-census-hygiene.md", "profile.md"): (
        "same reconciliation table, same wave. The profile citation records "
        "that the slice reads one row over its ledger figure while messaging "
        "reads one under -- stated as UNEXPLAINED and explicitly not chased, "
        "with the warning that the two cancel in the total and that is the "
        "arithmetic which hides a pair of errors. An open discrepancy the "
        "author declines to resolve is the opposite of a correction, and "
        "aiming a back-pointer at the slice would publish a refutation "
        "nobody made. The one profile row this wave did touch, G1, had its "
        "verdict left byte-identical and only its qualifier moved out of the "
        "state cell into the note beside it"
    ),
    ("profile.md", "2026-09-05-search-appearances-load-a.md"): (
        "points at the document that CARRIES the correction, not at one being "
        "corrected -- and the correction is the citing wave's own. Row G7 "
        "cites the LOAD A record as the place where an overclaim about what "
        "five member links point at is WITHDRAWN; section 3 of that document "
        "is the withdrawal. A CORRECTED BY: pointer aimed at it would tell a "
        "reader that the document making a self-correction had been refuted "
        "by the row that cites it. Same inversion as the sibling entry below, "
        "arriving from the opposite direction: there the target supplied a "
        "reason, here it supplies a retraction"
    ),
    ("profile.md", "2026-09-05-search-results-consent.md"): (
        "the row CORRECTS ITSELF and cites the consent brief as its REASON. "
        "G7's blocker read 'no tool, no reason'; the 2026-09-05 rewrite says "
        "that is now half false, because the consent brief established what "
        "the reason IS -- this page is the reciprocal instrument for a search, "
        "its LOAD A. The correction vocabulary ('IS NOW HALF FALSE') is about "
        "the census cell it replaces, which is why the fix is written IN PLACE "
        "in the cell rather than as a separate corrector document. The consent "
        "brief is not wrong about anything here and needs no CORRECTED BY: "
        "pointer -- aiming one at it would tell a reader that the document "
        "which SUPPLIED the reason had been refuted by the row that took it, "
        "inverting the relation exactly as the network.md/build-linkedin.md "
        "entry below describes. What the row DOES leave standing is that G7 "
        "is still a GAP: no tool, and nobody has opened the page"
    ),
    ("INSTRUMENTS.md", "2026-08-22-parity-linkedin.md"): (
        "the register DESCRIBES this check and quotes the instance it was "
        "built for, so it cites the corrected document while explaining that "
        "its line 18 was deliberately left byte-identical. It corrects "
        "nothing; the corrector is 2026-08-23-build-linkedin.md and the "
        "parity audit already carries its CORRECTED BY: pointer to that file. "
        "A back-pointer aimed here would name the documentation of a "
        "correction as its author"
    ),
    # THESE TWO WERE ADDED BY THIS FILE GOING RED ON ITS AUTHOR, an hour after
    # it was written, when census row N 118 was retired to MEASURED-ABSENT and
    # the retirement quoted both documents in the chain. That is the check
    # working rather than a collision: a genuine correction written into
    # `_audit/` is SUPPOSED to stop the suite until somebody triages it.
    ("network.md", "2026-08-22-parity-linkedin.md"): (
        "the row RECORDS a correction rather than making one. N 118 cites the "
        "parity audit's cost claim in order to say it was refuted, and names "
        "the document that refuted it -- so the corrector here is "
        "2026-08-23-build-linkedin.md, not network.md, and the parity audit "
        "already carries its CORRECTED BY: back-pointer to exactly that file. "
        "A second back-pointer aimed at this census row would name a reader of "
        "the correction as its author"
    ),
    ("network.md", "2026-08-23-build-linkedin.md"): (
        "points at the CORRECTOR, not at a corrected document. N 118 cites "
        "2026-08-23-build-linkedin.md as the file that got this right; "
        "requiring build-linkedin.md to carry a CORRECTED BY: pointer back to "
        "this row would invert the relation the whole check exists to fix"
    ),
    ("2026-09-03-hygiene-boundary-and-record.md", "2026-08-31-linkedin-perform.md"): (
        "reports the staleness incident rather than correcting it: perform.md "
        "now carries the correction IN PLACE, as a dated block at its own line "
        "3436 ('CORRECTION, 2026-09-03: THE TWO SECTIONS BELOW ARE WRONG ABOUT "
        "A SHIPPED TOOL') and inline beside the 'STILL TRUE, verified "
        "2026-09-02' line this document quotes. The corrected document already "
        "names its own correction, which is what this file asks for"
    ),
    (
        "2026-09-03-hygiene-boundary-and-record.md",
        "2026-09-03-typeahead-name-matching-is-dead.md",
    ): (
        "cites the typeahead finding APPROVINGLY, as the place a trap was "
        "recorded. The 'wrong' two lines down is about a git hash orphaned "
        "onto a backup branch still resolving -- 'the reference is already "
        "wrong' -- and says nothing about the cited document"
    ),
    ("2026-09-03-linkedin-capability-census.md", "2026-08-31-linkedin-perform.md"): (
        "reports perform.md as a stale system of record about a repaired tool. "
        "The line it cites, perform.md:3436, IS the dated in-place correction "
        "block, so the pointer a reader needs is already inside the target"
    ),
    ("2026-09-03-linkedin-gap-blockers.md", "2026-08-22-parity-linkedin.md"): (
        "BLOCK-QUOTES the parity claim inside section B1's three-document "
        "narrative, and names 2026-08-23-build-linkedin.md as its corrector in "
        "the very next paragraph. A later document quoting a correction is not "
        "a second corrector -- this is the class the lead's tight scan flagged"
    ),
    ("2026-09-03-linkedin-gap-blockers.md", "2026-08-23-build-linkedin.md"): (
        "the word CORRECTION on the citing line describes the CITED document "
        "as the corrector -- 'THE CORRECTION, TAKEN THE NEXT DAY, IN WRITING' "
        "-- not as something being corrected. The arrow points the other way"
    ),
    ("2026-09-03-linkedin-gap-blockers.md", "network.md"): (
        "an OPEN QUESTION that explicitly declines to rule: 'One of the two "
        "slices is wrong and I cannot tell which from the text'. A conflict "
        "nobody has resolved has no corrector, so there is no back-pointer to "
        "write and nothing to point it at"
    ),
    ("2026-09-03-linkedin-gap-blockers.md", "profile.md"): (
        "the same unresolved line as the network.md pair above -- profile.md "
        "is the OTHER half of the collision, and the sentence says which of "
        "the two is wrong cannot be told from the text"
    ),
    ("_slice-parity-census.md", "2026-08-22-linkedin-preflight.md"): (
        "the 'stale or still binding' judgment is about the linkedin-jobs "
        "SKILL.md Scope clause, not about the cited preflight audit -- which "
        "is cited as the evidence that the server was live on 2026-08-22"
    ),
    ("mcp-inventory.md", "2026-08-30-description-readiness.md"): (
        "'seven commits stale' is a QUOTED finding taken FROM the cited "
        "document, about a running process lagging its checkout. The citation "
        "supplies the quote; it is not its target"
    ),
    ("mcp-inventory.md", "2026-08-30-linkedin-undo.md"): (
        "the WRONG verdicts in this table are passed on the team lead's grep "
        "hypothesis -- the section heading reads 'Where the team lead's grep "
        "hypothesis was wrong' -- and linkedin-undo is cited as the EVIDENCE "
        "for the verdict. A corrected hypothesis is not a corrected document"
    ),
    ("mcp-inventory.md", "2026-08-30-linkedin-writes.md"): (
        "TABLE-ROW PROXIMITY: the 'wrong' two rows up is about verification "
        "reporting on a different tool. This row reads writes.md:273's "
        "'PERFORMED' header as capability language and grounds that on the "
        "same section's own next sentence, which is a reading, not a fix"
    ),
    ("mcp-inventory.md", "2026-08-31-linkedin-lift.md"): (
        "TABLE-ROW PROXIMITY: the words 'correction header' sit on the NEXT "
        "row, belong to a different tool, and name the successor brief"
    ),
    ("mcp-inventory.md", "_slice-invitation-needle.md"): (
        "TABLE-ROW PROXIMITY: the same 'correction header' on the PREVIOUS "
        "row, again a different tool and again naming the successor brief. "
        "This row quotes the needle slice for a STILL REFUSES verdict"
    ),
    ("mcp-inventory.md", "2026-08-31-linkedin-perform.md"): (
        "the vocabulary hit is the section heading two lines BELOW -- 'Where "
        "the team lead's grep hypothesis was wrong' -- and perform.md is cited "
        "above it as the supporting quote for a reversibility claim"
    ),
    ("mcp-inventory.md", "_slice-apply-census.md"): (
        "'the half that is wrong' two lines up is about a claim concerning "
        "resume upload; the apply census is cited as the count-of-zero "
        "EVIDENCE for the reading being argued, not as the thing corrected"
    ),
    ("network.md", "2026-08-23-linkedin-auth-slice.md"): (
        "THE VOCABULARY HIT IS A NEGATION -- 'and no later file supersedes "
        "them' -- which asserts the cited audits STILL STAND. A statement that "
        "nothing has corrected a document is the opposite of a correction"
    ),
    ("network.md", "2026-08-23-measure-linkedin.md"): (
        "the same negating sentence as the auth-slice pair: this file is the "
        "second of the three audits the row says no later file supersedes"
    ),
    ("network.md", "2026-08-31-linkedin-finish.md"): (
        "TABLE-ROW PROXIMITY: the 'supersedes' is two rows below, on the "
        "notifications row, and concerns that row's citations. This row cites "
        "finish.md:273 as a PASS receipt for followed_companies"
    ),
    ("network.md", "profile.md"): (
        "an OPEN QUESTION -- whether rows 67-78 are double-counted against "
        "profile.md. The 'wrong' two lines up belongs to a DIFFERENT numbered "
        "question, about section 3's tool table"
    ),
    ("profile.md", "2026-08-31-linkedin-perform.md"): (
        "reports that perform.md's pre-ship refusal was 'true when written, "
        "false since'. The target already carries the dated in-place "
        "correction block at its line 3436, so a reader who starts at that "
        "claim is not stranded, which is the harm this file is written against"
    ),
    ("jobs.md", "2026-09-05-decide-retire-rulings.md"): (
        "THE ARROW POINTS THE OTHER WAY: the census row is APPLYING the "
        "ruling, not correcting it. Row J 17 retires on DEVICE-GEOLOCATION and "
        "restates the ruling's own warning -- that the row's original reason "
        "('needs browser geolocation permission') is false, because this "
        "server drives Chrome over CDP and CDP can override geolocation. The "
        "thing corrected is jobs.md's OWN earlier cell text, replaced in the "
        "same commit that added the citation, so there is no second document "
        "left holding a stale claim for a back-pointer to reach. A CORRECTED "
        "BY: pointer aimed at the rulings document would tell a reader the "
        "ruling had been refuted by the row that implements it"
    ),
    # THE CENSUS-WAVE PAIR, triaged 2026-09-19. Both were produced by the scan
    # on 2026-09-06 and sat red through a thirteen-day gap; neither document
    # carries a marker of any kind, and the corpus-sweep never cites the
    # blocker map at all, so there was no reverse declaration to find.
    ("2026-09-05-blocker-map.md", "2026-09-06-corpus-sweep-blocker-evidence.md"): (
        "A RATCHET ADVANCE, NOT A REFUTATION, and the citing document says so "
        "in the same breath: 'SUPERSEDED, AND ONLY DOWNWARD ... Every number "
        "below was correct when measured and is stated with its pass; the "
        "ratchet exists precisely so this direction needs no ceremony.' The "
        "whole-corpus sweep took UNASSIGNED from 284 to 278 by reaching six "
        "rows this document's filter had not, which moves the count the one "
        "way the ratchet permits. Nothing in the blocker map is asserted "
        "wrong, so the arrow inverts twice over: the citation runs from the "
        "SUPERSEDED document to the one that superseded it, and a CORRECTED "
        "BY: pointer aimed at the sweep would tell a reader the later, wider "
        "measurement had been refuted by the narrower one it replaced. The "
        "reader-reachability this file exists to protect is already better "
        "served than a marker would serve it: the banner is the document's "
        "line 3, above every number it qualifies, and it names the figure to "
        "quote instead"
    ),
    ("2026-09-06-corpus-sweep-blocker-evidence.md", "2026-09-03-linkedin-gap-blockers.md"): (
        "AN UNRESOLVED CONFLICT THE AUTHOR DECLINES TO FILE, which is the "
        "opposite of a correction -- the same ground as the two "
        "census-hygiene entries above. Finding B quotes the ledger at "
        "1236-1242 to show that an amendment proposes renaming the blocker "
        "carrying rows J 116-J 120, and then refuses to act on it, because "
        "the passage settles on a THIRD name that is not one of the 97 and "
        "was never ruled: 'a proposal, not a ruling ... Recorded as-is rather "
        "than filed under either side.' The sweep asserts nothing about the "
        "ledger's correctness; it records that the ledger disagrees with "
        "itself and leaves the adjudication to whoever owns it. A CORRECTED "
        "BY: pointer aimed at the ledger would publish a ruling nobody made, "
        "on exactly the question the citing document went out of its way not "
        "to answer"
    ),
    # ----------------------------------------------------------------- 2026-09-19
    # SEVEN TRIAGED AT THE GATE-TO-ZERO PASS. One pair from the same sweep WAS
    # a correction and is declared with markers instead -- groups-admission
    # against groups-surface, a bucket table summing to 22 under a heading
    # saying 21. One in eight, which is the ratio this file's own header
    # documents and the reason the vocabulary alone cannot be the check.
    ("2026-09-19-the-three-ruling-requests-ruled.md", "2026-09-19-blocker-map-ruling-requests.md"): (
        "the line is a PROVENANCE note and not a claim about the cited "
        "document. It records WHICH STATE of the ruling requests was ruled "
        "against -- `5e144bb`, 'corrected at `4fb12a3` and `d6d1479`' -- and "
        "those two commits are corrections the cited document's OWN AUTHOR "
        "made to it. Naming the commits at which a document was fixed is how "
        "a reader knows which version was read; it is the opposite of a claim "
        "that the document is wrong. This document RULES ON the requests "
        "filed there, and a ruling on a request is not a correction of it"
    ),
    # THE THREE BELOW ARE ONE SHAPE, AND IT IS THE SHAPE THIS GUARD CANNOT SEE.
    ("2026-09-19-unfired-but-built.md", "2026-09-19-search-admission-preconditions.md"): (
        "the citation sits inside a TABLE OF TEST FAILURES that wave observed "
        "and attributed elsewhere -- its columns are 'failure' and 'whose', "
        "and this row's whose-cell reads 'not written here'. The correction "
        "vocabulary is not a verb about the cited document: it is the word "
        "'correction' inside a TEST'S OWN NAME, "
        "`test_a_correction_is_findable_from_the_claim`, quoted verbatim in "
        "the failure column. **THE GUARD CANNOT DISTINGUISH 'X CORRECTS Y' "
        "FROM 'X REPORTS THAT A TEST WHOSE NAME CONTAINS correction FIRED ON "
        "Y'**, and reporting a red is not correcting the document the red "
        "names"
    ),
    ("2026-09-19-unfired-but-built.md", "2026-09-19-the-three-ruling-requests-ruled.md"): (
        "same table, next row, and the same reading: the cell names the four "
        "documents that row's failure was counted in and says 'none of them "
        "this wave's prose'. It is an attribution of somebody else's red, "
        "written so the next wave does not spend the pass hunting for it. The "
        "vocabulary is again the test name in the failure column and not a "
        "verb this document applies to the cited one"
    ),
    ("2026-09-19-unfired-but-built.md", "network.md"): (
        "third citation in the same failure row, listing `network.md:436` as "
        "one of the four places that red was counted. A census slice named as "
        "the SITE of another wave's untriaged pair is being located, not "
        "corrected -- and this pass has now read that very line and triaged "
        "it, three entries below"
    ),
    # AND TWO WHERE THE VOCABULARY IS A SUBSTRING OF AN UNRELATED WORD.
    ("jobs.md", "2026-09-19-anchor-reader.md"): (
        "'stale' is matched as a SUBSTRING OF 'staleness'. The phrase in row "
        "42's cell is 'all four are the staleness diagnostic' -- the name of "
        "a field in the `linkedin_job_collections` payload, describing the "
        "only four strings that tool returns. Nothing in the window says a "
        "document is stale. The citation itself is an evidence pointer, "
        "'See `_audit/...`', which is how every census cell names where its "
        "reading is written up"
    ),
    ("jobs.md", "2026-09-19-read-tail.md"): (
        "the same cell, the same word, the same reason: row 42 cites both "
        "write-ups as evidence pointers, and the single 'staleness "
        "diagnostic' in that 4.7k-character cell puts BOTH citations inside "
        "the window. Two candidates from one substring is the cost of a "
        "deliberately loose vocabulary over census rows that hold a whole "
        "investigation on one line, and it is paid here rather than by "
        "narrowing the scan"
    ),
    ("network.md", "2026-09-19-the-first-sanctioned-press.md"): (
        "the citation is the evidence pointer closing row 133's cell, 'Full "
        "evidence: `_audit/2026-09-19-the-first-sanctioned-press.md`'. TWO "
        "UNRELATED THINGS put vocabulary in the window and neither is about "
        "the cited document. The parenthetical '(a self-correction: that "
        "wave's s1 had reported the page carries no such controls and s11 "
        "measured that FALSE)' describes a correction INSIDE A THIRD "
        "document, `_audit/_scratch/_progress-analytics-creator.md`, a "
        "working note no clone carries. And the next row opens 'NOTE THE "
        "NEIGHBOUR THIS CORRECTS:', which corrects a neighbouring CENSUS ROW "
        "-- `N 136` -- and not a document at all"
    ),
    # THESE TWO WERE ADDED BY THE BANKING PASS THAT MOVED jobs 44 AND profile
    # N2 TO COVERED-PROVEN on the first writes this server ever fired. Both are
    # TABLE-ROW PROXIMITY, and in both the matched word sits in a DIFFERENT
    # TOOL'S ROW from the citation -- which is why each reason below names the
    # line the word is on and the line the citation is on, separately.
    ("jobs.md", "2026-08-30-linkedin-undo.md"): (
        "the matched word is in the NEXT ROW and belongs to a different tool. "
        "The flagged line is the `save_job` row, whose citation to the undo "
        "audit ('YES, and it landed', :433 and :1645) is CONFIRMED by the "
        "2026-09-19 fires and contradicted by nothing. The 'SUPERSEDED' one "
        "line below is in the `unsave_job` row, which cites the same audit at "
        ":1775 -- so the pair would be produced by either line and the reason "
        "has to answer for both. IT IS STILL NOT A CORRECTION: the undo audit "
        "said `unsave_job` had never been fired, which was TRUE when written "
        "and remains a true statement about the state on 2026-08-30. An EVENT "
        "OVERTAKING A TRUE STATEMENT IS NOT AN ERROR IN THE DOCUMENT THAT MADE "
        "IT, and a CORRECTED BY: pointer would tell a reader the undo audit "
        "got something wrong. What changed is the world, on 2026-09-19. The "
        "census row itself carries the supersession in place and names the "
        "document that supersedes it, and its own words keep the six undo "
        "citations 'because they were accurate when written' -- which is the "
        "findability this file asks for, aimed at the claim that actually moved"
    ),
    ("profile.md", "2026-08-31-linkedin-finish.md"): (
        "same shape and cleaner, because the two lines share no citation at "
        "all. The flagged line is the `linkedin_surface_census` row, citing "
        "finish.md:275-279 for control counts -- read and checked: that is a "
        "boundary table giving `settings_dark_mode` 2, `profile_edit_intro` 4, "
        "`profile` 4, `settings` 3, none of which anything today touches. The "
        "'superseded' one line ABOVE is in the `linkedin_update_setting` row, "
        "and that row CITES ONLY 2026-09-19-tier1-fires.md -- finish.md is not "
        "named on it. What it supersedes is that cell's OWN PRIOR TEXT, a "
        "standing 'WRITE NEVER FIRED' replaced when the write fired and was "
        "verified both ways. A cell superseding its own earlier wording is the "
        "in-place correction this file prefers; aiming a CORRECTED BY: pointer "
        "at finish.md would refute a control-count table over a dark-mode "
        "write it never made a claim about"
    ),

    # TWO FROM WAVE `absent-blockers`, ADDED 2026-09-19 AFTER READING BOTH
    # LINES THE SCAN PRODUCED. In each the correction vocabulary belongs to
    # something OTHER than the cited document: in the first it is inside a
    # block quotation of that document's OWN ruling, and in the second the
    # thing called wrong is this wave's own handed input.
    ("2026-09-19-the-four-absent-blockers.md",
     "2026-09-19-the-three-ruling-requests-ruled.md"): (
        "THE CORRECTION VOCABULARY IS INSIDE A BLOCK QUOTATION OF THE CITED "
        "DOCUMENT'S OWN RULING, and the thing it calls an ERROR is the 2026-09-03 "
        "LEDGER, not the document being cited. Section 2.2 explains why "
        "PREMIUM-APPLY-SURFACES cannot be filled, and quotes Request 4 verbatim "
        "-- 'RULED: THE CENSUS IS RIGHT. THE LEDGER'S 1R IS THE ERROR ... That "
        "1R may no longer be cited as evidence in any filing.' The ruling is "
        "being RELIED ON as the authority that closes one of the two routes to "
        "5-of-6; it is not contradicted anywhere in the citing document, which "
        "goes on to reproduce its 14-of-15 measurement and reach the same "
        "answer. A CORRECTED BY: pointer here would tell a reader that a "
        "ruling had been overturned when it was upheld and acted on."
    ),
    ("2026-09-19-the-four-absent-blockers.md", "mcp-inventory.md"): (
        "THE THING CALLED WRONG IS THIS WAVE'S OWN HANDED INPUT, AND THE CITED "
        "FILE IS THE REMEDY RATHER THAN THE SUBJECT. The provenance section "
        "records that a delegated agent was given frozen copies of FOUR census "
        "slices when the census has FIVE, said so instead of sweeping 80% of "
        "the file set, and extracted mcp-inventory.md itself to close the gap. "
        "No claim in mcp-inventory.md is asserted wrong, or even evaluated -- "
        "it is named only as the slice that was missing from a brief. The "
        "sentence corrects a brief, and briefs are not documents this "
        "discipline can point at."
    ),
    # FOUR FROM THE FOUR-DEFECTS WAVE, 2026-09-19. A FIFTH pair the same scan
    # produced is NOT here: four-defects-fixed.md really does correct
    # the-four-absent-blockers.md section 5 item 4, and is declared with a
    # CORRECTS:/CORRECTED BY: pair instead. This test found it, which is the
    # design working.
    ("2026-09-19-four-defects-fixed.md", "2026-09-19-the-empty-blockers.md"): (
        "THE LINE IS A FINDING THAT THE DOCUMENT IS SOUND. It reads that "
        "the-empty-blockers.md QUOTES EVERY CELL IT USES, VERBATIM, which is "
        "the evidence for ruling that nothing in the gitignored file it names "
        "is load-bearing. The four-defects wave DID edit that document, but "
        "only to mark an unreadable path as provenance -- a pointer repair, "
        "not a claim asserted wrong. Nothing it concludes is contradicted; the "
        "sentence is the opposite, a reason to trust it."
    ),
    ("2026-09-19-four-defects-fixed.md", "2026-09-19-blocker-map-ruling-requests.md"): (
        "SAME POINTER REPAIR, SAME REASON. The line records that this document "
        "deferred to a gitignored file for an enumeration, and that the "
        "enumeration is recomputable from committed code. What was wrong was "
        "the ADDRESS, not the claim: the remaining blockers do fail on those "
        "three axes and the document's own next paragraph already restates the "
        "closing arithmetic. A CORRECTED BY: pointer would tell a reader a "
        "finding had been overturned when only a citation was re-aimed."
    ),
    ("2026-09-19-four-defects-fixed.md", "jobs.md"): (
        "HISTORY ABOUT THE COUNTER, NOT A CLAIM ABOUT THE SLICE. The line says "
        "23 verdicts were invisible because jobs.md used its own short "
        "spelling XR -- already recorded in count_census_states.py's own "
        "receipt, and already resolved by teaching the counter rather than "
        "rewriting the rows. The slice was never wrong; the vocabulary was "
        "short. The line names jobs.md as the place a dialect was first seen."
    ),
    ("2026-09-19-four-defects-fixed.md", "mcp-inventory.md"): (
        "THE THING CALLED WRONG IS THE WAVE'S OWN DISCARDED DRAFT. The line "
        "reports that the FIRST dialect detector written by this wave flagged "
        "101 cells at HEAD, including every R/W/REV column and the whole of "
        "mcp-inventory.md, and was narrowed for that reason. mcp-inventory.md "
        "is the corpus the bad detector fired on, not a document whose claims "
        "are evaluated -- the report's ruling about it is that its "
        "PROVEN-LIVE / TESTED-ONLY vocabulary is a DIFFERENT LANGUAGE and "
        "correctly outside the count."
    ),
    # 2026-09-19, added by the wave that stopped two documents deferring to a
    # gitignored file. Read in context before declaring, as this list requires.
    ("2026-09-19-blocker-map-ruling-requests.md", "2026-09-19-the-empty-blockers.md"): (
        "THE WORD STALE IS ABOUT A THIRD DOCUMENT, AND THE CITED FILE IS THE "
        "WITNESS RATHER THAN THE SUBJECT. The sentence says the SCRATCH "
        "SNAPSHOT it had been deferring to -- _progress-unlocatable-recovery.md "
        "section 47, a 12:21 reading -- was already stale when cited, and names "
        "the-empty-blockers.md because that document's own section 3 REPORTS "
        "BEING MISLED BY IT and getting three blockers wrong nineteen minutes "
        "later. Citing a document's self-retraction as evidence about a THIRD "
        "file is the opposite of correcting that document; nothing it claims is "
        "asserted wrong, and a CORRECTED BY: pointer would tell a reader its "
        "retraction had itself been overturned. Same proximity-scanning "
        "property already recorded on the row-walk / messaging pair above: the "
        "correction vocabulary sits beside the EVIDENCE citation, not beside "
        "any corrected claim."
    ),
    # 2026-09-20, added by the newsletter build wave, for its own three pairs
    # and no neighbour's. Each line was READ before it was listed, which is
    # what this dict's entries claim.
    ("2026-09-20-newsletter-built.md", "2026-09-05-the-newsletter-create-route.md"): (
        "THE CITED DOCUMENT IS THE MECHANISM'S PRECEDENT, NOT ITS SUBJECT. "
        "The line names the-newsletter-create-route.md as the place this "
        "corpus last chose a BACK-POINTER over a rewrite -- it corrected "
        "register 9.1 by leaving 9.1's text standing and attaching the "
        "correction beneath it -- and says that readonly.py's author-side "
        "paragraph is being amended the same way. Nothing that document "
        "claims is asserted wrong; it is cited as the house convention being "
        "followed. A CORRECTED BY: pointer would tell a reader its own "
        "correction had been overturned, which is the opposite of what the "
        "sentence says."
    ),
    ("INSTRUMENTS.md", "2026-09-20-newsletter-built.md"): (
        "A POINTER TO WHERE THE NUMBERS LIVE, IN A DISPOSABLE-TOOLS "
        "DECLARATION. Register 23.6 declares three scratch scripts disposable "
        "and says their RESULTS survive in the wave report and in the "
        "committed probe's output. The correction vocabulary near it belongs "
        "to the word SUPERSEDED, which is about the scratch scripts being "
        "replaced by the committed probe -- the wave's own discarded drafts, "
        "the same shape as the four-defects / mcp-inventory entry above. "
        "The report is the destination of a result, not a document being "
        "corrected."
    ),
    ("_slice-newsletter-inventory.md", "profile.md"): (
        "THE SLICE IS AN INVENTORY AND profile.md IS ONE OF THE FILES IT "
        "INVENTORIES. The line reports that a test's own prose describes "
        "newsletter analytics as a profile.md census-slice row, quoted while "
        "enumerating what each newsletter-touching test asserts. A read-only "
        "inventory makes no claim about whether that row is right, and it "
        "evaluates nothing in profile.md -- the citation names the corpus "
        "being listed, which is the EVIDENCE-citation shape this dict already "
        "records twice."
    ),

    # 2026-09-20, from the live-capture wave. THREE PAIRS, ALL THE SAME SHAPE
    # THIS DICT ALREADY RECORDS SEVERAL TIMES: a census row withdrawing or
    # advancing ITS OWN state in place and citing the wave that measured it.
    # In each the cited document is the CORRECTOR, never the corrected.
    ("jobs.md", "2026-09-20-the-live-capture.md"): (
        "ROWS 136-138 WITHDRAW THEIR OWN STANDING REASON IN PLACE AND NAME "
        "THE MEASUREMENT THAT REFUTED IT. The reason being withdrawn is "
        "theirs: that answering needs a completed audio session and so only "
        "the operator can discharge it. A live page load refuted that -- the "
        "member-side product is offered, its address is same-origin and "
        "carries no member segment, the one drawn route is a create route, "
        "and no results route is drawn on any of six captured surfaces. The "
        "rows STAY GAP; only their blocker changes. The cited document is "
        "where that measurement lives, so it is the refuting source. A "
        "CORRECTED BY: pointer in it would tell a reader that the document "
        "supplying the measurement had itself been refuted"
    ),
    # 2026-09-20, the five-under-banked wave. THE DECLARED CORRECTION, SEEN
    # FROM THE CORRECTED END. The wave's CORRECTS: marker names jobs.md and
    # jobs.md carries the matching CORRECTED BY: above section A's table, so
    # the pair IS declared -- in the (corrector, target) direction the marker
    # channel records. This candidate is the other direction: five corrected
    # CELLS end with "Reading: `_audit/2026-09-20-the-five-under-banked.md`",
    # which is the corrected document naming its corrector inside the row, so
    # a reader who lands on the claim finds the correction without having to
    # notice the marker. That is the outcome this file exists to require, and
    # the dict header already records the shape ("a report about a document
    # that ALREADY CARRIES ITS CORRECTION IN PLACE ... cannot also be a
    # violation of it"). jobs.md corrects nothing in the wave document.
    ("jobs.md", "2026-09-20-the-five-under-banked.md"): (
        "THE DECLARED CORRECTION READ BACKWARDS. jobs.md is the CORRECTED "
        "document, not the corrector: rows 9, 11, 12, 13 and 14 carry a dated "
        "correction to their own drift-floor sentence and name the wave "
        "document as where the reading lives. The correction itself is "
        "declared with a CORRECTS:/CORRECTED BY: pair in the "
        "(five-under-banked.md, jobs.md) direction. A CORRECTED BY: pointer "
        "in the wave document would tell a reader that the measurement which "
        "corrected these cells had itself been refuted by the cells it "
        "corrected"
    ),
    # 2026-09-20, the five-under-banked wave, and it is TABLE-ROW PROXIMITY --
    # the shape this dict's own header names first. READ THE LINE: the pair is
    # produced by jobs.md row 10 (Filter: Company), which cites
    # 2026-09-05-company-about-card.md for its own UNFIRED reason and is
    # untouched by this wave. The correction vocabulary sits in rows 9 and 11,
    # the lines either side of it, where this wave appended a dated correction
    # about the DRIFT FLOOR of a different probe entirely
    # (_probe_job_search_result_sets.py). A markdown table has no blank lines,
    # so two unrelated rows are always within WINDOW of each other. Row 10
    # makes no claim about the cited document; it quotes it approvingly, as the
    # source that says the L1 live verification was not taken. A CORRECTED BY:
    # pointer in company-about-card.md would tell a reader that the document
    # holding row 10's reason had been refuted, which nothing here claims.
    ("jobs.md", "2026-09-05-company-about-card.md"): (
        "TABLE-ROW PROXIMITY. The candidate is row 10 (Filter: Company), which "
        "cites this document as the source for its own UNFIRED state -- the L1 "
        "live verification was not taken -- and is not edited by the wave that "
        "produced the vocabulary. The words 'CORRECTED', 'wrong' and 'refuted' "
        "are in rows 9 and 11, the adjacent lines, and they govern the DRIFT "
        "FLOOR quoted from scripts/_probe_job_search_result_sets.py, which this "
        "document says nothing about. Row 10 endorses the cited document rather "
        "than correcting it, and the real correction this wave made IS declared, "
        "with a CORRECTS:/CORRECTED BY: pair against jobs.md itself"
    ),
    ("network.md", "2026-09-20-the-live-capture.md"): (
        "ROW 135 IS PROMOTED, NOT CORRECTED. Its prior cell said "
        "COVERED-UNFIRED and gave the reason: surfaced, with no recorded run "
        "asserting a value live. That was TRUE when written and is not "
        "withdrawn -- a run was simply taken, and the row advanced to "
        "COVERED-PROVEN on it. The correction vocabulary in the cell belongs "
        "to the neighbouring scope defect the same call confirmed, which is a "
        "statement about dom.py's reader and not about the cited document. A "
        "CORRECTED BY: pointer in it would tell a reader that the run which "
        "promoted this row had been refuted"
    ),
    ("network.md", "2026-09-20-the-premium-block.md"): (
        "THE CITED DOCUMENT WAS RIGHT AND THIS ROW NOW CONFIRMS IT. Its "
        "section 5 reported, from the tree alone, that the profile-views "
        "insights reader obeys a main scope its own comment says it only "
        "reports, that no committed fixture of that page has a main element, "
        "and that the live branch is therefore untested -- and it called the "
        "consequence ambiguity because offline analysis could go no further. "
        "The live call in this wave turned that hypothesis into a "
        "contradiction: 12 viewer rows parsed by the outer reader, 0 seen by "
        "the scoped one, on the same load. CORROBORATION, arriving from the "
        "other end. A CORRECTED BY: pointer there would tell a reader that "
        "the source which diagnosed the defect first had been refuted"
    ),

    # 2026-09-20, from the split-ruling wave. Both entries below are the
    # INVERSE of a correction and they are the first of that shape in this
    # dict, which is why each says so: the cited document is named because it
    # was RIGHT, and right FIRST. The vocabulary that catches them is the word
    # "correction" describing what THIS wave did to a third document.
    ("2026-09-20-the-split-ruling.md", "2026-09-19-the-remaining-partials.md"): (
        "AN ATTRIBUTION, NOT A CORRECTION -- IT CREDITS THE CITED DOCUMENT "
        "WITH THE FIND. The line reads 'the finding is <this document>'s, the "
        "confirmation is the handover's, and this wave's contribution is the "
        "ruling and the correction, not the find.' The word CORRECTION in it "
        "names what the split-ruling wave did to the 2026-09-03 ledger, which "
        "is declared separately with a real CORRECTS:/CORRECTED BY: pair. "
        "Section 5.4 of the cited document convicted the same published cell "
        "a day earlier and on a stronger argument, and this wave adopts that "
        "argument wholesale. A CORRECTED BY: pointer here would tell a reader "
        "the document that got it right had been overturned."
    ),
    ("2026-09-20-the-split-ruling.md", "2026-09-19-partial-blockers-closed.md"): (
        "A CITATION-COVERAGE MEASUREMENT ABOUT A THIRD DOCUMENT. The line "
        "reports that the newsletter-build wave's report cites neither this "
        "document nor its sibling anywhere in its text -- a grep result with "
        "a count, offered as evidence that the wave re-discovered a ruling "
        "rather than inheriting it. The claim being evaluated is the HANDOVER "
        "REPORT's coverage; nothing in the cited document is asserted wrong, "
        "and the correction vocabulary two lines up belongs to the sentence "
        "triaged immediately above. Naming a document as ABSENT from a third "
        "party's citations is not correcting it."
    ),
    # 2026-09-20, from the sanitiser-scope wave. It is the SUCCESSOR document to
    # the one it cites: that audit's section 4c escalated the page-text bypass
    # and explicitly declined to rule on it, and this wave was chartered to rule.
    ("2026-09-20-the-sanitiser-scope.md", "2026-09-20-the-loop-binding-hole.md"): (
        "IT EXTENDS AN ESCALATION AND REPORTS SOMEBODY ELSE'S LANDED "
        "CORRECTION. Two passages trip the scan and neither asserts that "
        "document is wrong. (1) The cited section 4c demonstrated the "
        "sanitiser-scope bypass with ONE claimant, `_redact`, in the nested "
        "call spelling; this wave measured all three guarded names in both "
        "spellings and both binding forms. That is a WIDENING of a finding, "
        "not a repair of a false one -- 4c never claimed the other two names "
        "were unaffected, and in fact says the stop 'matches BY NAME across "
        "every module', which is the property this wave then measured. (2) "
        "This wave independently re-measured that document's `global` / "
        "`nonlocal` STILL BLIND row, found it false, and then found the "
        "repair ALREADY SHIPPED on master at 42f55b2 by the document's own "
        "author -- whose version carries a 38-row census where this wave had "
        "four cases. The edits written here were REVERTED in favour of it "
        "and the target file is untouched by this wave. Reporting a "
        "correction another wave has already made, and crediting it as the "
        "better one, is not making a correction. "
    ),
    # 2026-09-20, same wave, second pair. The scan is right to look: the line
    # sits two lines under a paragraph counting a mistake this wave made twice.
    ("2026-09-20-the-sanitiser-scope.md", "INSTRUMENTS.md"): (
        "IT IS A HARVEST POINTER, AND THE CORRECTION VOCABULARY NEXT TO IT "
        "IS ABOUT THE WAVE'S OWN MISTAKE. The line records where this wave's "
        "instruments were registered -- section 31 of the register, four "
        "subsections named -- which is the standing requirement that a tool "
        "built in a round is filed rather than left in its round's document. "
        "What trips the scan is the paragraph immediately above it, in which "
        "the wave counts a blind-regex rename that over-reached into prose "
        "TWICE in one hour and says both instances were repaired. That is "
        "this wave correcting ITSELF in its own ledger, and the register is "
        "named only as the place the resulting instruments went. A document "
        "saying where it filed its tools is an attribution. "
    ),

    # 2026-09-20, the REOPENER-TRIGGERS wave. Four pairs, all triaged by
    # reading the lines -- three are census rows this wave wrote, and the
    # fourth is a neighbour caught by the +-2 window.
    ("messaging-and-content.md", "2026-09-20-the-first-firing.md"): (
        "THE CITED DOCUMENT ASKED FOR THIS EDIT AND IS NOT CORRECTED BY IT. "
        "The line is row `M M4`, moved EXCLUDED-RULED -> MEASURED-ABSENT. It "
        "quotes `the-first-firing.md` s4d, which NAMED the two-state-words "
        "defect, declined to fix it because two rows had been committed four "
        "hours earlier, and wrote *the owner of the state vocabulary can rule "
        "it in one line*. Carrying out an act a document explicitly deferred "
        "to somebody else is FULFILLING it, not contradicting it: nothing in "
        "s4d is withdrawn, and its evidence -- three instruments looking, a "
        "raw-versus-rendered sweep over 25 captures -- is relied on rather "
        "than overturned. **THE ROW ITSELF IS CORRECTED, and that correction "
        "IS declared**: this file carries a CORRECTED BY: marker naming "
        "`2026-09-20-the-reopener-triggers.md`, which carries the matching "
        "CORRECTS:. So the pair the scan offers here is the wrong pair -- the "
        "corrector is this wave's document, not the one being quoted. "
    ),
    ("network.md", "2026-09-20-the-first-firing.md"): (
        "THE TWIN OF THE PAIR ABOVE, and the same reading. The line is row "
        "`N 157`, moved EXCLUDED-RULED -> MEASURED-ABSENT in the same pass "
        "and for the same reason, quoting the same s4d sentence. `N 157`, "
        "`M M4` and `J 127` assert one fact about one object -- the InMail "
        "balance is not rendered -- and `J 127` already read MEASURED-ABSENT, "
        "so this removes a three-way disagreement rather than creating one. "
        "The real correction is declared by marker pair with "
        "`2026-09-20-the-reopener-triggers.md`, as above. "
    ),
    ("network.md", "2026-09-20-the-reopener-triggers.md"): (
        "THE CITATION POINTS AT WHERE A DEFECT IS DESCRIBED, AND THE ROW IS "
        "AN INSTANCE OF IT RATHER THAN A CORRECTION OF IT. The line is row "
        "`N 118`, whose STATE DID NOT MOVE -- it was MEASURED-ABSENT before "
        "this wave and is MEASURED-ABSENT after. What was added is a REOPENER "
        "clause naming a trigger that WAS ALREADY BUILT: "
        "`dom.read_profile_detail_entries` has re-taken that reading on every "
        "call since 2026-09-04. The row cites the wave document as the place "
        "the class of defect is written up. Nothing about the cited document "
        "is withdrawn -- it is the document that prompted the clause. "
        "**A row naming the audit that added a sentence to it is an "
        "attribution**, which is the same reading as the "
        "sanitiser-scope/INSTRUMENTS pair above. "
    ),
    ("messaging-and-content.md", "2026-09-19-profile-modals-measured.md"): (
        "COLLATERAL OF THE +-2 WINDOW, AND THE LINE IT FLAGS WAS NOT TOUCHED "
        "BY ANY WAVE TODAY. The line is row `M M5`, which cites "
        "`profile-modals-measured.md` amendment C as the place its R9/R4 "
        "adjudication was made -- a provenance pointer, and the row has read "
        "that way since 2026-09-19. What made it a candidate is the "
        "NEIGHBOURING row: `M M4` sits one line above and now opens "
        "**STATE CORRECTED**, so the vocabulary that trips the scan belongs "
        "to a different row entirely. **THE WINDOW IS DOING EXACTLY WHAT ITS "
        "OWN COMMENT SAYS IT WILL** -- reaching two lines and paying for the "
        "reach in triage entries rather than in silence -- and in a MARKDOWN "
        "TABLE every row is one line, so +-2 means the two adjacent "
        "capabilities. That is a real cost of the heuristic on this corpus, "
        "recorded here rather than argued away: it is the price of not "
        "missing a correction, and it is cheap. "
    ),
    ("profile.md", "2026-09-20-the-sanctioned-seventh.md"): (
        "THE CITATION IS A POINTER AT THE FULL READING, AND THE ARROW POINTS "
        "THE OTHER WAY. The line is row `B2`, whose REASON was repaired "
        "2026-09-20 -- it had called the `set_input_files` ban "
        "*package-wide*, which stopped being true on 2026-09-04 when a single "
        "call site was sanctioned. `B2` cites `the-sanctioned-seventh.md` as "
        "the place that sanction is measured and argued in full. **The cited "
        "document is not corrected by this citation; it is the CORRECTOR's "
        "evidence.** The correction vocabulary beside it is this row "
        "describing its OWN repair. "
        "**THE REAL CORRECTION IS DECLARED, and it is a different pair:** "
        "`profile.md` carries a CORRECTED BY: marker naming "
        "`2026-09-20-the-reopener-triggers.md`, which carries the matching "
        "CORRECTS:. The sanctioned-seventh document deliberately edited no "
        "census row -- its own NOT_A_CORRECTION entry above says so and names "
        "that as its failure condition -- so the wave that DID edit the row "
        "owns the declaration. "
        "**AND THE STATE DID NOT MOVE:** `B2` was EXCLUDED-RULED and remains "
        "so. Upload is absent from `writes.PERFORMABLE` and "
        "`writes.writes_enabled()` is False, so nothing became reachable. "
        "Right answer, wrong reason -- which is worth a correction precisely "
        "because a later reader cannot tell it from wrong answer, wrong "
        "reason. "
    ),
    # -- 2026-09-20, the MESSAGING-GAP wave. Six pairs, every reason written
    # -- after reading the line that produced it. Five of the six are one
    # -- census ROW citing the sources its own argument rests on: a markdown
    # -- table has no blank lines, the row is a single 2,000-character line,
    # -- and every citation in it therefore sits within the window of every
    # -- correction word in it. The sixth is a back-pointer.
    ("INSTRUMENTS.md", "messaging-and-content.md"): (
        "IT IS A REGISTER ENTRY DESCRIBING A CORRECTION THAT WAS MADE IN "
        "PLACE, WHICH IS THE OUTCOME THIS FILE REQUIRES RATHER THAN A "
        "VIOLATION OF IT. Section 39.6 records that the census section 4 was "
        "stale in all four of its factual claims and that a guard now "
        "re-derives them -- and the census itself carries the correction "
        "block, dated, with a CORRECTED BY: marker naming its corrector. The "
        "register is naming the defect its instrument was built for, which is "
        "what every other entry in it does. The document that CORRECTS the "
        "census is the wave report, and that pair IS declared. "
    ),
    ("messaging-and-content.md", "2026-09-05-lead-rulings-round-two.md"): (
        "THE ROW QUOTES THIS DOCUMENT AS ITS AUTHORITY AND CONTRADICTS "
        "NOTHING IN IT. The line is row C43, moved GAP -> EXCLUDED-RULED on "
        "the FEED-CONTENT-READ-RULING, and it quotes that document's section "
        "5 verbatim in support -- 'counts and relations only, never text or "
        "names'. The correction vocabulary in the row is about the CENSUS: "
        "this row was left GAP while its own twin was banked, so what is "
        "being corrected is the row, by itself, in place. The cited ruling is "
        "fifteen days old, unchanged, and is the reason the row moved. "
    ),
    ("messaging-and-content.md", "2026-09-05-settings-rest.md"): (
        "SAME LINE, SAME ROLE: THE CITATION IS THE BUILD RECEIPT FOR THE "
        "RULING THE ROW RESTS ON. Row C43 cites this document's section 1 to "
        "show the ruling was not merely made but BUILT -- as feed.py, with "
        "the guarantee in the signature in both directions. Nothing in that "
        "document is withdrawn, narrowed or contradicted by the row; it is "
        "the evidence that the rule the row is retired under is live code "
        "rather than an audit sentence. "
    ),
    ("messaging-and-content.md", "2026-09-19-cross-slice-rulings.md"): (
        "THE ROW CITES THIS DOCUMENT FOR THE NAME OF THE PATTERN IT IS AN "
        "INSTANCE OF. Row C43 calls itself a propagation failure and points "
        "at that document's section 2, which defines the signature -- a GAP "
        "row that states the ruling's own premise and files GAP anyway. "
        "Citing a taxonomy in order to be classified by it is the opposite of "
        "correcting it, and that document's own count is not touched. "
    ),
    ("messaging-and-content.md", "2026-09-20-the-decides.md"): (
        "THE CENSUS QUOTES THIS DOCUMENT IN ORDER TO OBEY IT, AND THE "
        "CORRECTION VOCABULARY BELONGS TO A DIFFERENT CLAIM. The line sits in "
        "the section 4 correction block, where the census records that its "
        "own claim about set_input_files was false. The quotation from the "
        "decides document is the RULING THAT KEEPS TEN ROWS AT GAP -- 'the "
        "blocker RETIRES as a blocker ... Its 15 rows stay GAP, correctly' -- "
        "cited so that the corrected census cannot be read as licence to move "
        "them. What is corrected is the census; what is quoted is the rule "
        "that bounds the correction. "
    ),
    ("messaging-and-content.md", "2026-09-20-the-messaging-gap.md"): (
        "THIS IS THE BACK-POINTER ITSELF, SEEN FROM THE WRONG END. The "
        "correction runs from the wave report TO the census, and that pair is "
        "declared: the report carries CORRECTS: and the census carries "
        "CORRECTED BY:. What the scan produces here is the census's ROW C43 "
        "naming the wave report as the place its reading is written up -- the "
        "'See ...' pointer every banked row in this corpus carries. Reading "
        "it as the census correcting the report inverts the direction of the "
        "declared pair. "
    ),

    # SEVEN, 2026-09-21, from the read-triage wave. Every one was triaged by
    # reading the line that produced it, and every one is a shape this table
    # already holds: a corrector paired with its EVIDENCE, and a back-pointer
    # seen from the wrong end. The corrections that wave DID make -- nine cells
    # in network.md and one in profile.md -- are declared with CORRECTS: /
    # CORRECTED BY: pairs instead, which is what this table leaves room for.
    ("2026-09-21-the-read-triage.md", "2026-09-20-company-page-built.md"): (
        "THE CITED DOCUMENT IS AGREED WITH, AND THE CENSUS IS WHAT IS "
        "CORRECTED. The line reads that that wave 'found the same thing five "
        "days ago and filed it SHIPPED, pre-existing -- and the census row "
        "was left carrying the refuted blocker'. The word 'refuted' belongs "
        "to the census cell, not to the cited wave: its finding is quoted as "
        "the authority the correction rests on. A CORRECTED BY marker there "
        "would tell every future reader that the build wave withdrew "
        "something, and nothing in it is withdrawn -- what the triage adds is "
        "that its finding never reached the row. "
    ),
    ("network.md", "2026-09-19-search-admission-preconditions.md"): (
        "THE CITATION IS A PRICE, NOT A CORRECTION. Row 79's corrected cell "
        "cites that document's section B.4 for a measurement it still holds: "
        "8 of 11 ordinary search keywords trip the forbidden-substring list. "
        "The correction vocabulary in the window ('EXPIRED', 'FALSE') "
        "belongs to the BLOCKER TEXT the same cell strikes through, three "
        "sentences earlier -- a markdown table row has no blank lines, so a "
        "whole corrected cell is one line and everything it cites lands "
        "inside the window. Nothing in the cited document is withdrawn. "
    ),
    ("network.md", "2026-09-19-the-read-rows.md"): (
        "A DECISION RE-FILED UNCHANGED IS THE OPPOSITE OF A CORRECTION. Row "
        "99's corrected cell quotes that document calling an unmade ruling "
        "'the single highest-yield decision left in this row set' and records "
        "that it is still unanswered. The triage endorses it and re-files it; "
        "a CORRECTED BY marker would claim the read-rows wave got it wrong, "
        "when the finding is that nobody answered it. The vocabulary in the "
        "window is the cell's own verdict on its STRUCK-THROUGH blocker text. "
    ),
    ("network.md", "2026-09-20-company-page-built.md"): (
        "SAME PAIR AS THE FIRST ENTRY ABOVE, SEEN FROM THE CENSUS SIDE. Row "
        "53's corrected cell cites that wave as the source of the finding the "
        "correction applies -- 'found the same thing and filed it SHIPPED, "
        "pre-existing'. The cited document is the evidence for the "
        "correction, never its target. "
    ),
    ("network.md", "2026-09-21-the-read-triage.md"): (
        "THIS IS THE BACK-POINTER ITSELF, SEEN FROM THE WRONG END -- the same "
        "shape as the messaging-gap entry above. The correction runs from the "
        "triage TO this census, and that pair is declared: the triage carries "
        "CORRECTS: and this slice carries CORRECTED BY:. What the scan "
        "produces here is a corrected ROW naming the document its reasoning "
        "is written up in, the 'See ...' pointer every such row in this "
        "corpus carries. Reading it as the census correcting the triage "
        "inverts the direction of the declared pair. "
    ),
    ("profile.md", "2026-09-05-profile-rest.md"): (
        "THE CITED DOCUMENT IS THE MEASUREMENT THAT REFUTES THE CELL, NOT A "
        "DOCUMENT BEING REFUTED. Row K8's corrected cell says its own old "
        "reason -- 'no tool, no reason' -- is false BECAUSE that document "
        "measured the capability live at allowlist +0, and quotes its "
        "conclusion verbatim. The word 'FALSE' in the window is the cell's "
        "verdict on ITSELF. Seventh instance in this corpus of proximity "
        "matching pairing a corrector with its evidence. "
    ),
    ("profile.md", "2026-09-21-the-read-triage.md"): (
        "THE BACK-POINTER FROM THE WRONG END AGAIN, on the profile slice. The "
        "declared pair runs triage -> profile.md, with CORRECTS: on one side "
        "and CORRECTED BY: on the other; row K8's 'See ...' pointer is the "
        "row naming where its reasoning lives. "
    ),
    ("2026-09-21-the-read-triage.md", "2026-09-19-search-shaper.md"): (
        "THE CITED DOCUMENT IS A DATA POINT IN A RANKING, NOT A CLAIM BEING "
        "WITHDRAWN. The line reports that it and the citing document BOTH "
        "SCORE 5.000 for SEARCH-RESULTS-SURFACE in the blocker-reason "
        "locator, so it fell out of the top 3 on an arbitrary tie-break "
        "rather than on merit. The correction vocabulary in the window -- "
        "'worse', 'wrong' -- is the citing document's verdict on THE OBVIOUS "
        "READING OF ITS OWN TEST FAILURE ('the locator got worse ... is "
        "wrong'), not on anything the shaper document says. Nothing in it is "
        "asserted mistaken; it is named because its rank moved. "
    ),

    # 2026-09-21, the WHAT-WAS-RULED wave. THREE pairs, and the first and
    # third are one recurring shape rather than three mistakes: **a report
    # that BUILDS OR REGENERATES a derived file will always cite that file
    # beside staleness vocabulary**, because saying why a derived file had to
    # be rebuilt is what such a report is for. "Stale", "regenerated" and
    # "drifted" are the correction vocabulary AND the vocabulary of
    # derivation, and the scan cannot tell them apart from proximity. Expect
    # this shape from every future wave that touches INDEX.md or RULINGS.md.
    ("2026-09-21-what-was-ruled.md", "RULINGS.md"): (
        "THE CITING DOCUMENT CREATED THE CITED ONE; IT WITHDRAWS NOTHING. "
        "`_audit/RULINGS.md` is this wave's own generated output and the "
        "report is its build note. The correction vocabulary in the window "
        "is *'goes false with nobody touching it'*, which is the report "
        "stating why ITS OWN section-1 counts are pinned as a dated reading "
        "-- the corpus grew by two documents when this wave landed, one of "
        "them the cited file. Nothing in `RULINGS.md` is asserted mistaken; "
        "it did not exist to be mistaken about. "
        "**WHAT WOULD MAKE THIS ENTRY WRONG:** the report later asserting "
        "that a registered claim in `RULINGS.md` is false while leaving the "
        "register unregenerated."
    ),
    ("2026-09-21-what-was-ruled.md", "INDEX.md"): (
        "A DERIVED FILE WAS REGENERATED, NOT CORRECTED. The line reads "
        "*'the committed `INDEX.md` was stale by construction. Regenerated "
        "with --write'* -- 'stale' here is a statement about DERIVATION, not "
        "about a claim. This wave added two documents to `_audit/`, which "
        "makes every derived index stale automatically and is the index's "
        "own drift check working exactly as designed. **Nothing `INDEX.md` "
        "says is asserted wrong**; it is regenerated, every line of it, from "
        "the corpus. It would be incoherent for a report to CORRECT a file "
        "whose entire content is computed. "
        "**WHAT WOULD MAKE THIS ENTRY WRONG:** the report asserting that the "
        "index GENERATOR produces a wrong line, which would be a correction "
        "of `scripts/build_audit_index.py` and would belong there."
    ),
    ("2026-09-21-what-was-ruled.md", "profile.md"): (
        "THE CLAIM IS ABOUT A SCAN'S BEHAVIOUR ON A ROW, NOT ABOUT THE ROW. "
        "The line reads *'The single false positive is "
        "`_audit/_census/profile.md` row `P A25`'* -- where 'false positive' "
        "is the verdict on THIS WAVE'S OWN `RULED:` scan, which matched "
        "inside the state name `EXCLUDED-RULED` in that row's reason cell. "
        "**The row is correct and is not being corrected**; the parser was "
        "the thing at fault and it was fixed. No state, reason or citation "
        "in `profile.md` is touched by this wave, and the wave edited no "
        "census file at all. "
        "**WHAT WOULD MAKE THIS ENTRY WRONG:** the report asserting that "
        "`P A25`'s own state or reason is mistaken."
    ),

}


def _documents() -> list[pathlib.Path]:
    """Every ``.md`` document in ``_audit/`` THAT GIT TRACKS.

    **IT USED TO BE ``AUDIT.rglob("*.md")``, AND THAT MADE THE SCAN'S DOMAIN
    THE WORKING COPY RATHER THAN THE REPOSITORY.** The two are not the same
    corpus, and the gap between them is not small: ``_audit/_scratch/`` is
    ignored unconditionally by ``.gitignore``, so it holds ZERO tracked files
    and, on 2026-09-05, 37 ``.md`` files on disk. A ``rglob`` sees all 37. A
    clone sees none.

    So this test PASSED in the working tree and FAILED in a clone AT THE SAME
    SHA -- six ``NOT_A_CORRECTION`` entries naming ``_scratch/`` documents read
    as live locally and as stale everywhere else. **A CHECK WHOSE VERDICT
    DEPENDS ON WHICH TREE IT RUNS IN IS NOT CHECKING THE REPOSITORY**, and the
    half of that divergence that mattered was the half nobody could see: the
    author who added those entries had them pass.

    Tracked-only is also the answer on the merits, not merely the one that
    converges. This file exists so a reader who starts at a claim can reach its
    correction. A reader has the repository; they do not have anybody's
    scratch directory. A correction parked in an ignored working note was never
    part of the durable record, so it cannot discharge -- nor create -- an
    obligation that record carries.

    **THIS IS DELIBERATELY NARROWER THAN ``committable_files()`` IN
    ``test_no_committed_credential.py``, WHICH SWEEPS TRACKED PLUS
    UNTRACKED-NOT-IGNORED.** That file guards against PUBLISHING a credential,
    so it must see what is about to be committed or its first true answer
    arrives one commit late. This file makes no claim about the future: it
    asserts that the record AT THIS SHA is internally navigable. Including
    untracked drafts would reintroduce exactly the divergence above, one
    unfinished audit note at a time.

    A non-zero git exit FAILS. It is not skipped and not defaulted to a disk
    walk -- a check that goes quiet when its instrument is missing is the shape
    this whole suite is written against.
    """
    proc = subprocess.run(
        ["git", "ls-files", "--", "_audit"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, "git ls-files failed: %s" % proc.stderr
    return sorted(
        ROOT / line
        for line in proc.stdout.splitlines()
        if line.strip().endswith(".md")
    )


def _resolver() -> dict[str, pathlib.Path]:
    """The three spellings the corpus uses, mapped to files that exist.

    Basenames are unique across ``_audit/`` (asserted below), so the bare-name
    form is unambiguous. Anything not in this map resolves to nothing.
    """
    index: dict[str, pathlib.Path] = {}
    for doc in _documents():
        index[doc.relative_to(ROOT).as_posix()] = doc
        index[doc.relative_to(AUDIT).as_posix()] = doc
        index[doc.name] = doc
    return index


def _is_marker(line):
    """``CORRECTS`` / ``CORRECTED BY`` if this line is a declaration, else None.

    MARKER LINES ARE THE DECLARATION CHANNEL AND ARE HELD OUT OF THE PROSE SCAN
    ENTIRELY -- as citation sources and as vocabulary sources both. Without
    that, the back-pointer would feed itself: ``**CORRECTED BY:**`` contains the
    word "corrected" one character from a citation, so the corrected document
    would scan as a corrector OF ITS OWN CORRECTOR, and writing the fix this
    file demands would manufacture a fresh violation pointing the wrong way.
    """
    found = MARKER.search(line)
    return found.group(1) if found else None


def _citations(line: str, index: dict[str, pathlib.Path]) -> list[pathlib.Path]:
    out = []
    for hit in CITATION.finditer(line):
        target = index.get(hit.group(1))
        if target is not None:
            out.append(target)
    return out


#: The document a marker names, which is always the FIRST backticked span on
#: the line: ``**CORRECTS:** `_audit/x.md` -- the reason``.
_CITED = re.compile(r"`[^`]+`")


def _reason_on(line: str) -> str:
    """Whatever a marker line says after the document it names.

    **IT USED TO READ AFTER THE LAST BACKTICK, AND THAT IS NOT WHAT THIS
    DOCSTRING SAYS.** The sentence above was always the intent; ``rindex``
    was the implementation. Any reason that mentions a backticked symbol --
    which is most of the good ones -- was therefore cut at its LAST symbol
    instead of its first citation, and what came back was a tail.

    MEASURED 2026-09-20 over the tracked corpus: **65 of 136 markers**
    returned a strict suffix of their own reason. Thirteen were cut below 60
    characters. The shortest surviving fragment was 23 characters and read,
    entire, ``was re-opened to GAP on``.

    **AND THE GUARD WAS GREEN ON ALL 65.** Its only check is that the
    fragment is at least 20 characters, and a fragment can be: the one above
    clears the bar by three. A length floor tests that something is there,
    never that it is the thing. I satisfied that same floor by hand earlier
    the same day, by rewriting a marker to end in prose rather than a
    backticked symbol -- routing around this defect without noticing it,
    which is how it survived being edited three times in one session.
    """
    cited = _CITED.search(line)
    if cited is None:
        return ""
    return line[cited.end():].strip().lstrip("-*: ").strip()


def _declarations():
    """Every marker in the corpus.

    Returns ``(corrects, corrected_by, malformed)`` -- the first two mapping
    ``(source_name, target_name) -> (line_number, line)``, the third listing
    marker lines that do not name exactly one resolving document with a reason.
    """
    index = _resolver()
    corrects: dict[tuple[str, str], tuple[int, str]] = {}
    corrected_by: dict[tuple[str, str], tuple[int, str]] = {}
    malformed: list[tuple[str, int, str, str]] = []

    for doc in _documents():
        lines = doc.read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, 1):
            kind = _is_marker(line)
            if kind is None:
                continue
            named = _citations(line, index)
            if len(named) != 1:
                malformed.append(
                    (
                        doc.name,
                        number,
                        line.strip(),
                        "names %d documents that resolve; a marker must name "
                        "exactly one" % len(named),
                    )
                )
                continue
            if len(_reason_on(line)) < 20:
                malformed.append(
                    (
                        doc.name,
                        number,
                        line.strip(),
                        "carries no reason after the citation; a marker must "
                        "say in one line what the correction was",
                    )
                )
                continue
            where = corrects if kind == "CORRECTS" else corrected_by
            where[(doc.name, named[0].name)] = (number, line.strip())
    return corrects, corrected_by, malformed


def _candidates() -> dict[tuple[str, str], tuple[int, str]]:
    """Every (corrector, target) pair the LOOSE lexical scan produces.

    A document citing ITSELF is never a candidate, and a citation resolving to
    nothing is ignored. Marker lines are held out -- see :func:`_is_marker`.
    """
    index = _resolver()
    found: dict[tuple[str, str], tuple[int, str]] = {}
    for doc in _documents():
        lines = doc.read_text(encoding="utf-8").splitlines()
        prose = ["" if _is_marker(line) else line.lower() for line in lines]
        for number, line in enumerate(lines, 1):
            if _is_marker(line):
                continue
            for target in _citations(line, index):
                if target == doc or (doc.name, target.name) in found:
                    continue
                low = max(0, number - 1 - WINDOW)
                high = min(len(lines), number + WINDOW)
                near = "\n".join(prose[low:high])
                if any(word in near for word in CORRECTION_VOCABULARY):
                    found[(doc.name, target.name)] = (number, line.strip())
    return found


def test_there_is_a_corpus_and_the_scan_reaches_it():
    """A sweep over nothing passes forever, and this file's whole subject is a
    check that looks like coverage and is not.

    Pinned here rather than trusted: the corpus is large, basenames are unique
    (so a bare-name citation cannot resolve to the wrong document), citations do
    resolve, and the LOOSE scan does produce candidates. If the citation regex
    broke, every entry on ``NOT_A_CORRECTION`` would go stale at once and the
    triage test would say so -- but a positive guard is cheaper to read than an
    inference drawn from 26 failures.
    """
    docs = _documents()
    assert len(docs) > 50, len(docs)

    names = [doc.name for doc in docs]
    assert len(names) == len(set(names)), sorted(
        name for name in names if names.count(name) > 1
    )

    index = _resolver()
    assert index.get("_audit/2026-08-22-parity-linkedin.md") is not None
    assert index.get("2026-08-22-parity-linkedin.md") is not None
    assert index.get("_census/network.md") is not None

    assert len(_candidates()) > 20, sorted(_candidates())


def test_every_declared_correction_carries_a_back_pointer():
    """(A) -- THE ASSERTION THIS FILE WAS BUILT FOR.

    A ``CORRECTS:`` marker without the matching ``CORRECTED BY:`` in the named
    document is the defect itself, in its purest form: the correction exists,
    it is machine-readable, and the reader who starts at the claim still cannot
    find it.
    """
    corrects, corrected_by, _ = _declarations()
    missing = []
    for (corrector, target), (number, line) in sorted(corrects.items()):
        if (target, corrector) not in corrected_by:
            missing.append(
                "  %s:%d declares CORRECTS: %s -- and %s carries no "
                "'CORRECTED BY: %s' back-pointer.\n      line: %s"
                % (corrector, number, target, target, corrector, line)
            )
    assert not missing, (
        "%d declared correction(s) that the corrected document cannot lead a "
        "reader to:\n%s" % (len(missing), "\n".join(missing))
    )


def test_every_back_pointer_is_declared_by_the_document_it_names():
    """The other direction, so half an edit cannot read as a joined pair.

    A ``CORRECTED BY:`` naming a document that does not declare the correction
    is an ORPHAN: it survives the corrector being rewritten, retracted or
    deleted, and it then points a reader at a file that no longer says what the
    back-pointer promises. The one-way arrow again, pointing the other way.
    """
    corrects, corrected_by, _ = _declarations()
    orphans = []
    for (target, corrector), (number, line) in sorted(corrected_by.items()):
        if (corrector, target) not in corrects:
            orphans.append(
                "  %s:%d points at %s as its corrector -- and %s declares no "
                "'CORRECTS: %s'.\n      line: %s"
                % (target, number, corrector, corrector, target, line)
            )
    assert not orphans, (
        "%d back-pointer(s) with nothing declaring them:\n%s"
        % (len(orphans), "\n".join(orphans))
    )


def test_every_marker_names_one_document_and_carries_a_reason():
    """A declaration nobody can follow is worse than no declaration.

    It looks like the joined pair this file requires, and satisfies a reader
    who does not click through.
    """
    _, _, malformed = _declarations()
    assert not malformed, "\n".join(
        "  %s:%d %s\n      line: %s" % (name, number, why, line)
        for name, number, line, why in malformed
    )


def test_every_candidate_pair_is_declared_or_triaged():
    """(B) -- THE HALF THAT KEEPS WORKING AFTER TODAY.

    Fixing one back-pointer is worth one commit. Making the next correction
    impossible to write without somebody either declaring it or saying in
    writing why it is not one is worth the file.

    This does NOT claim every pair below is a correction. It claims each one was
    LOOKED AT.
    """
    corrects, _, _ = _declarations()
    untriaged = []
    for (corrector, target), (number, line) in sorted(_candidates().items()):
        if (corrector, target) in corrects or (corrector, target) in NOT_A_CORRECTION:
            continue
        untriaged.append(
            "  %s:%d cites %s with correction vocabulary within %d line(s), and "
            "the pair is neither declared with a CORRECTS:/CORRECTED BY: marker "
            "pair nor listed on NOT_A_CORRECTION.\n      line: %s"
            % (corrector, number, target, WINDOW, line)
        )
    assert not untriaged, (
        "%d candidate correction(s) nobody has triaged. Each is either a real "
        "correction -- declare it with a CORRECTS: marker and write the "
        "CORRECTED BY: back-pointer into the target -- or it is not, in which "
        "case add it to NOT_A_CORRECTION with the reason, AFTER READING THE "
        "LINE:\n%s" % (len(untriaged), "\n".join(untriaged))
    )


def test_no_triage_entry_is_stale_or_unreasoned():
    """AN ENTRY IS A CLAIM THAT IS ITSELF CHECKED, not a waiver.

    THREE RULES, and the first is the one that separates an allowlist from a
    silencer: an entry for a pair the scan NO LONGER PRODUCES fails as loudly as
    a missing entry. Prose gets rewritten; when the sentence that produced a
    candidate goes away, the exception must go with it, or the list slowly
    becomes a place where pairs are parked and stop being looked at.

    The second: an entry may not cover a pair that IS declared -- that would be
    claiming a correction is not one while its own markers say it is.

    The third: the reason must be long enough to carry an argument, because the
    entry's only job is to be read by the next person.
    """
    candidates = _candidates()
    corrects, _, _ = _declarations()

    stale = [pair for pair in NOT_A_CORRECTION if pair not in candidates]
    assert not stale, (
        "%d NOT_A_CORRECTION entr(ies) for pairs the scan no longer produces. "
        "The prose that made them candidates is gone, so the exception is stale "
        "and must be deleted -- a stale exception is how an allowlist becomes a "
        "silencer:\n%s"
        % (len(stale), "\n".join("  %s -> %s" % pair for pair in sorted(stale)))
    )

    both = [pair for pair in NOT_A_CORRECTION if pair in corrects]
    assert not both, (
        "%s is declared with a CORRECTS: marker AND listed as not a correction. "
        "One of the two is wrong." % sorted(both)
    )

    for pair, reason in sorted(NOT_A_CORRECTION.items()):
        assert len(reason.strip()) > 40, (pair, reason)


def test_an_unresolvable_citation_is_ignored_and_a_self_citation_never_counts():
    """THE CONTROL FOR THE SCAN'S TWO IGNORE RULES, both load-bearing.

    The corpus really does carry citation-shaped strings that name nothing here:
    a glob (``_audit/*.md``), a bare ``.md``, and paths into a SIBLING
    repository's audit directory. Failing on those would make this file's first
    run a list of dangling links -- a different, real defect, and not this one.

    And a document that cites ITSELF while discussing a correction -- which
    every one of the five documents reporting an IN-PLACE correction does --
    would otherwise scan as its own corrector.
    """
    index = _resolver()
    assert _citations("see `_audit/*.md` for the set", index) == []
    assert _citations("the suffix is `.md`", index) == []
    assert (
        _citations("`mcp-servers/_audit/2026-08-21-linkedin-parse-fix.md:5`", index)
        == []
    )

    real = _citations("corrected in `_audit/2026-08-22-parity-linkedin.md`", index)
    assert [path.name for path in real] == ["2026-08-22-parity-linkedin.md"]
    ranged = _citations("`_audit/2026-08-23-build-linkedin.md:229-231`", index)
    assert [path.name for path in ranged] == ["2026-08-23-build-linkedin.md"]

    assert not any(corrector == target for corrector, target in _candidates())


def test_a_marker_line_does_not_feed_the_prose_scan():
    """THE MISTAKE THIS FILE WAS ALMOST BUILT ON, and it would have been
    self-inflicted.

    ``**CORRECTED BY:** `x.md` -- ...`` carries the word "corrected" one
    character from a citation. If marker lines were scanned as prose, writing
    the back-pointer this file DEMANDS would immediately create a new candidate
    pair in the REVERSE direction -- the corrected document scanning as a
    corrector of its own corrector -- and the fix would fail the test that asked
    for it.
    """
    assert _is_marker("**CORRECTS:** `x.md` -- the claim") == "CORRECTS"
    assert _is_marker("   **CORRECTED BY:** `x.md` -- what changed") == "CORRECTED BY"
    assert _is_marker("CORRECTS: `x.md` -- unbolded still counts") == "CORRECTS"
    assert _is_marker("this paragraph corrects `x.md`, in prose") is None
    assert _is_marker("| a table row | that is WRONG |") is None
    # PROSE ABOUT THE MECHANISM IS NOT THE MECHANISM. These two shapes were
    # both read as real markers until 2026-09-04, when writing the register
    # entry that DESCRIBES this check turned the check red on its own author.
    # A marker is a line; a mention is a phrase.
    assert _is_marker("a corrector writes a `CORRECTS:` marker; see below") is None
    assert _is_marker("the target must carry `CORRECTED BY:`. Zero false") is None

    text = "**CORRECTED BY:** `_audit/2026-08-23-build-linkedin.md` -- measured"
    assert _citations(text, _resolver()), "the citation itself must still parse"
    assert "corrected" in text.lower(), "the trigger word really is on that line"
    # ...and the reverse pair it would otherwise have produced does not exist.
    assert (
        "2026-08-22-parity-linkedin.md",
        "2026-08-23-build-linkedin.md",
    ) not in _candidates()


def test_the_entry_and_marker_rules_can_still_fail():
    """THE RULES ABOVE THAT FIRE ON BROKEN INPUT HAVE NOTHING REAL TO FIRE ON,
    by design -- the corpus is meant to stay well-formed.

    Every fresh instrument built in this repository had a bug on its first
    attempt, so each rule is shown REJECTING, on input built here:

    * a marker naming a document that does not exist
    * a marker naming more than one
    * a marker with no reason after the citation
    * a triage entry whose reason is too short to weigh
    * a triage entry for a pair the scan does not produce -- the STALE case,
      which is how an allowlist becomes a silencer
    """
    index = _resolver()

    # Rule: a marker must name exactly one document that resolves.
    assert _citations("**CORRECTS:** `_audit/never-written.md` -- x", index) == []
    assert len(_citations("**CORRECTS:** `network.md` `profile.md` -- two", index)) == 2
    assert len(_citations("**CORRECTS:** `network.md` -- one", index)) == 1

    # Rule: a marker must carry a reason after the citation.
    assert len(_reason_on("**CORRECTS:** `network.md`")) < 20
    assert (
        len(_reason_on("**CORRECTS:** `network.md` -- the endorsement cost was mis-specified"))
        >= 20
    )

    # Rule: a reason must be long enough to carry an argument.
    assert len("table proximity".strip()) <= 40

    # Rule: the stale case, pointed at a pair that really is absent from the
    # scan, so it is shown rejecting a real-looking key rather than nonsense.
    fabricated = ("2026-08-22-parity-linkedin.md", "INSTRUMENTS.md")
    assert fabricated not in _candidates()
    assert fabricated not in NOT_A_CORRECTION


def _module_level_dicts(source: str):
    """Every module-level ``NAME = {...}`` and ``NAME: T = {...}`` in a source.

    BOTH FORMS, DELIBERATELY. The first version of this walked for `ast.Assign`
    alone and found NOTHING, because every declaration table in this file is
    ANNOTATED -- `NOT_A_CORRECTION: dict[tuple[str, str], str] = {`, which the
    parser reports as `ast.AnnAssign`. It printed an empty result and read
    exactly like a clean bill of health. That is this repository's most common
    defect wearing its most convincing costume, and it happened in the check
    written to catch the defect.
    """
    out = []
    for node in ast.parse(source).body:
        if isinstance(node, ast.AnnAssign):
            name = getattr(node.target, "id", None)
        elif isinstance(node, ast.Assign):
            name = next((getattr(t, "id", None) for t in node.targets), None)
        else:
            continue
        if name and isinstance(node.value, ast.Dict):
            out.append((name, node.value))
    return out


def _shadowed(dict_node) -> list:
    """Keys declared more than once. A dict literal keeps only the LAST."""
    keys = []
    for key in dict_node.keys:
        try:
            keys.append(ast.literal_eval(key))
        except ValueError:  # pragma: no cover - a computed key
            continue
    return sorted(k for k, n in collections.Counter(keys).items() if n > 1)


def test_no_declaration_is_silently_shadowed():
    """A key declared twice in a declaration table is DEAD TEXT, not a duplicate.

    Python does not raise on a repeated key in a dict literal -- the later value
    wins and the earlier one becomes unreachable. In this file that means a
    triage entry whose ARGUMENT no longer applies to anything, which is worse
    than a missing entry: a reader finds it, believes it is load-bearing, and
    may delete the wrong half.

    MEASURED, NOT HYPOTHETICAL. On 2026-09-20 this table carried TWO shadowed
    pairs -- ("jobs.md", "2026-08-30-linkedin-undo.md") and
    ("profile.md", "2026-08-31-linkedin-finish.md") -- 140 entries at 138
    distinct keys. They had survived every green run of this suite, because
    nothing had ever asked.
    """
    source = pathlib.Path(__file__).read_text(encoding="utf-8")
    tables = _module_level_dicts(source)
    assert tables, (
        "parsed no module-level dict from this file, so this check is vacuous. "
        "The likely cause is the AnnAssign/Assign split described in "
        "_module_level_dicts -- verify before widening anything."
    )
    offenders = {name: dup for name, node in tables if (dup := _shadowed(node))}
    assert not offenders, (
        "declaration keys silently shadowed (the LATER value wins and the "
        "earlier reason is unreachable): %s" % offenders
    )


def test_control_the_shadow_check_convicts_a_planted_duplicate():
    """SHOWN FAILING on a planted duplicate, in both assignment forms.

    Without the AnnAssign half this control would pass while the real table
    went unexamined -- which is exactly how the first draft behaved.
    """
    plain = "X = {\n    ('a', 'b'): 'first',\n    ('a', 'b'): 'second',\n}\n"
    annotated = "Y: dict = {\n    ('c', 'd'): 'first',\n    ('c', 'd'): 'second',\n}\n"

    for source, expected_name, expected_key in (
        (plain, "X", ("a", "b")),
        (annotated, "Y", ("c", "d")),
    ):
        tables = _module_level_dicts(source)
        assert [n for n, _ in tables] == [expected_name], (
            "the parser did not see a %s-form declaration at all" % expected_name
        )
        assert _shadowed(tables[0][1]) == [expected_key], (
            "the shadow detector did not convict a planted duplicate in %s"
            % expected_name
        )

    clean = "Z: dict = {\n    ('a', 'b'): 'only',\n}\n"
    assert _shadowed(_module_level_dicts(clean)[0][1]) == [], (
        "the detector convicts a table with no duplicate, so it proves nothing"
    )


def test_a_reason_is_not_cut_at_its_last_backtick():
    """No marker's reason may be a strict suffix of the text after its citation.

    THE PROPERTY, not the implementation: whatever `_reason_on` returns must be
    everything the line says after the document it names -- not a tail of it.
    Stated this way the test still fails if somebody reintroduces `rindex`, or
    invents a third rule that happens to truncate.

    It is a FLOOR-FREE check on purpose. The length floor beside it (20
    characters) is what let 65 truncated reasons pass for weeks: a floor tests
    that something is there, never that it is the thing.
    """
    offenders = []
    for doc in _documents():
        for number, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
            if _is_marker(line) is None:
                continue
            cited = _CITED.search(line)
            if cited is None:
                continue
            full = line[cited.end():].strip().lstrip("-*: ").strip()
            got = _reason_on(line)
            if got != full:
                offenders.append((doc.name, number, len(got), len(full)))
    assert not offenders, (
        "%d marker reason(s) are truncated -- the reader is shown a fragment "
        "of the argument, not the argument. (file, line, shown, actual): %s"
        % (len(offenders), offenders[:8])
    )


def test_control_the_truncation_check_convicts_the_rule_it_replaced():
    """SHOWN FAILING against the exact rule that shipped, on a real shape.

    The specimen is the shape that produced the 65: a reason that mentions a
    backticked symbol partway through. Under the old last-backtick rule the
    reader saw everything after `PERFORMABLE` and nothing before it.
    """
    line = (
        "**CORRECTS:** `_audit/x.md` -- the row was excluded citing a "
        "package-wide ban, and upload is absent from `PERFORMABLE` so nothing "
        "became reachable."
    )
    old = line[line.rindex("`") + 1:].strip().lstrip("-*: ").strip()
    new = _reason_on(line)

    assert old != new, "the old and new rules agree here, so this proves nothing"
    assert new.startswith("the row was excluded"), new
    assert old.startswith("so nothing became reachable"), old
    assert len(old) < len(new), (len(old), len(new))
    # And the old fragment CLEARS the 20-character floor, which is the whole
    # reason the floor never caught this.
    assert len(old) >= 20, len(old)

    # A marker with no citation at all must come back empty rather than raise;
    # the old rule raised ValueError on a line with no backtick.
    assert _reason_on("**CORRECTS:** nothing cited here") == ""
