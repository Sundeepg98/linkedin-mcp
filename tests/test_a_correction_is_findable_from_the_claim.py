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
