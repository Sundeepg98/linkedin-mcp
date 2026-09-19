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
    ("jobs.md", "messaging-and-content.md"): (
        "the cited slice is the CORROBORATING SOURCE and this row agrees with "
        "it. J 127 and M4 are the same capability -- the InMail credit "
        "balance -- in two slices, and M4 already records the measurement "
        "that settles both: the admitted page carries no balance. J 127 cites "
        "M4 to adopt that finding, not to overturn it. The correction "
        "vocabulary in the cell belongs to this row correcting ITSELF (it was "
        "GAP on an expired premise) and to a note REPORTING, deliberately "
        "without changing, that M4 carries the same measurement under a "
        "different state name. Both rows are out of GAP so no count moves; "
        "flagging a duplicate is not refuting it"
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
        "above. C52 was moved to MEASURED-ABSENT by a402c35 on a live read of "
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


def _reason_on(line: str) -> str:
    """Whatever a marker line says after the document it names."""
    return line[line.rindex("`") + 1 :].strip().lstrip("-*: ").strip()


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
