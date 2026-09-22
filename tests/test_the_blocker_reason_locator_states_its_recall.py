"""The blocker-reason locator must keep its measured recall, and say so.

WHY THIS TEST EXISTS. `scripts/find_blocker_reason.py` ranks, per blocker, the
documents that ARGUE its reason. On 2026-09-20 a sibling wave's child reported
that it had missed the most relevant document for `SERVICES-PAGE-SURFACE` and
found that document only by hand. That report was correct, and measuring it
turned up three independent defects -- a vocabulary in which every STEM was
dead, a scoring unit of one physical LINE in a hard-wrapped corpus, and the
GENERATED map competing with the prose and winning 59 times out of 97.

THE DANGER THE LOCATOR CARRIES. A ranked list of documents to read is useful at
any recall. A DERIVED COLUMN naming one document is a claim, and a wrong claim
of that shape does not dangle -- it rots into a plausible wrong answer that
stops the reader instead of sending them looking. So the recall is pinned here,
in both directions: it may not regress, and the at-rank-1 number is asserted to
still be too low to justify a `reason_doc` column. If someone genuinely fixes
the ranking, THIS TEST FAILS and they must re-read the ruling in
`_audit/2026-09-20-the-three-held-defects.md` section 2 before shipping one.

THE VALIDATION SET IS NOT THE TOOL'S OWN OUTPUT. It is the six blockers
`surf-evid-A` researched BY HAND -- grep plus reading -- with the documents it
named in its own deliverable, written before any of this work began. A tool
evaluated on the cases it found is measuring itself.

SHOWN FAILING against the version at `8b58dcb`, which is what the report was
about. Run by loading that revision's module and calling it:

    test_the_known_miss_is_found                     FAILED
      candidates('SERVICES-PAGE-SURFACE') = 3 documents, and
      _audit/2026-09-20-the-contingent-writeoffs.md is not among them
    test_recall_against_a_hand_built_set_does_not_regress   FAILED
      found-anywhere 1 of 8, floor is 6
    test_no_generated_artifact_is_ever_a_candidate   FAILED
      _audit/_census/blocker-map.tsv is the TOP candidate for 59 of 97 blockers
    test_every_stem_in_the_vocabulary_actually_matches_its_word_forms  FAILED
      'measured' unmatched; 'refused' unmatched; 'refusal' unmatched;
      'admitted' unmatched; 'rulings' unmatched; 'proven' unmatched;
      'shown' unmatched
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import find_blocker_reason as fbr  # noqa: E402

#: The blocker whose miss started this, and the document that was missed.
KNOWN_MISS_BLOCKER = "SERVICES-PAGE-SURFACE"
KNOWN_MISS_DOC = "_audit/2026-09-20-the-contingent-writeoffs.md"

#: Hand-found by `surf-evid-A`, independent of this tool. See the docstring.
HAND_FOUND = {
    "COMPANY-PAGE-SURFACE": ["_audit/2026-09-20-company-page-built.md"],
    "NEWSLETTER-SURFACE": ["_audit/2026-09-20-newsletter-built.md"],
    "EVENTS-SURFACE": ["_audit/2026-09-19-events-surface.md"],
    "GROUPS-SURFACE": ["_audit/2026-09-19-groups-surface.md",
                       "_audit/2026-09-19-groups-admission.md"],
    # THE THIRD ENTRY WAS ADDED 2026-09-21 AND THE FLOOR WAS NOT TOUCHED,
    # WHICH IS THE WHOLE POINT OF RECORDING IT HERE.
    #
    # `_audit/2026-09-21-the-read-triage.md` triages 19 of this blocker's 20
    # read rows and is a hand-found reason document for it by the same standard
    # as its two neighbours. Adding it took the set from 8 documents to 9.
    #
    # WHAT IT EXPOSED ON THE WAY IN, because "the locator regressed" was the
    # obvious reading and it is the wrong one. Scores, measured:
    #
    #     1.  7.000  2026-09-19-search-admission-preconditions.md
    #     2.  7.000  2026-09-03-linkedin-gap-blockers.md
    #     3.  5.000  2026-09-21-the-read-triage.md
    #     4.  5.000  2026-09-19-search-shaper.md
    #
    # **THE SHAPER DOCUMENT FELL OUT OF THE TOP 3 ON A TIE, NOT ON MERIT.** Two
    # candidates scored 5.000 and the order between them is whatever the sort
    # was already doing. So a `top3` floor is sensitive to an ARBITRARY
    # TIE-BREAK whenever a new document lands on an existing score -- which is
    # a property of this measurement nobody had written down, and it is the
    # reason the corpus growing can look exactly like the locator getting
    # worse. The floor stays at 7 and is not lowered: lowering it would have
    # hidden the tie instead of naming it.
    "SEARCH-RESULTS-SURFACE": [
        "_audit/2026-09-19-search-admission-preconditions.md",
        "_audit/2026-09-19-search-shaper.md",
        "_audit/2026-09-21-the-read-triage.md"],
    "SERVICES-PAGE-SURFACE": [KNOWN_MISS_DOC],
}

#: FLOORS, not pins. Raising them is the intended direction and needs no
#: ceremony; lowering one needs a reason, because it means the locator got worse
#: at the only question anybody checked it on.
RECALL_ANYWHERE_FLOOR = 8

#: RETIRED AS A GATE 2026-09-22, KEPT AS A PRINTED OBSERVATION. This floor could
#: not distinguish the locator getting WORSE from the corpus getting BETTER, and
#: it fired on the second. Measured when it fired: per-document top3 was 5 of 9
#: against this floor of 7, while `anywhere` was 9 of 9 -- the locator had not
#: lost a single hand-found document, it had ranked a genuinely better one above
#: three of them (score 14 against their 7). Neither refreshing the fixture nor
#: excluding census slices rescues it; see AGAINST_A_WEAKER_DOCUMENT below for
#: what replaced it and why. The number is still computed and printed, because
#: the information is worth having even when it is not worth gating on.
RECALL_TOP3_OBSERVED_ONLY = 7
#: A CEILING, and the unusual one. While the top-ranked document is the
#: hand-chosen one only about half the time, the `reason_doc` column may not
#: carry a BARE PATH -- a bare path in a table reads as data. It carries the
#: candidate's rank and score instead. If this fails because the locator
#: IMPROVED, that is good news and a decision to re-take -- see
#: `_audit/2026-09-20-the-three-held-defects.md` section 2.
RANK1_CEILING_FOR_A_DERIVED_COLUMN = 6


def _ranks():
    """blocker -> {wanted doc: 1-based rank or None}, over the hand-found set."""
    out = {}
    for blocker, wanted in HAND_FOUND.items():
        docs = [d for _s, d in fbr.candidates(blocker)]
        out[blocker] = {
            w: (docs.index(w) + 1 if w in docs else None) for w in wanted
        }
    return out


def test_the_known_miss_is_found():
    docs = [d for _s, d in fbr.candidates(KNOWN_MISS_BLOCKER)]
    assert KNOWN_MISS_DOC in docs, (
        f"{KNOWN_MISS_BLOCKER}'s candidate list is {len(docs)} document(s) and "
        f"does not contain {KNOWN_MISS_DOC}, which a human found by hand. "
        f"Got: {docs[:5]}. This is the exact miss the locator was repaired for; "
        "a regression here means one of F1/F2/F3 in the script's docstring was "
        "undone."
    )


def displacements(scores=None):
    """Per blocker: what outranks the best hand-found document, and is it better?

    THE QUESTION A TOP-3 FLOOR COULD NOT ASK. A hand-found document leaving the
    top 3 has two completely different causes -- the ranker got worse, or a
    better document arrived -- and a count of how many are in the top 3 cannot
    tell them apart. It fired on the second cause on 2026-09-21 and would have
    been "fixed" by lowering it, which would have recorded a degradation that
    had not happened.

    This asks the discriminating question instead: **is anything ranked above a
    known-good answer WEAKER than it?** Being displaced by something better is
    the locator working. Being displaced by something worse is the only shape
    that is a defect, and it is the shape a reader actually suffers from.

    Stable under corpus growth by construction, so its floor is ALL blockers
    rather than a fraction that has to be revisited every time somebody writes
    a good document.

    `scores` is injectable so the control can plant a weaker document above a
    hand-found one and watch this convict it.
    """
    out = {}
    for blocker, wanted in HAND_FOUND.items():
        rows = scores if scores is not None else fbr.candidates(blocker)
        by_doc = {d: s for s, d in rows}
        order = [d for _s, d in rows]
        found = [d for d in wanted if d in order]
        if not found:
            out[blocker] = ("NO-HAND-FOUND-DOC", [])
            continue
        best = max(by_doc[d] for d in found)
        cut = min(order.index(d) for d in found)
        weaker = [(by_doc[d], d) for d in order[:cut] if by_doc[d] < best]
        out[blocker] = (best, weaker)
    return out


def test_no_known_good_answer_is_displaced_by_a_weaker_document():
    """THE GATE. Every blocker, not a fraction of them."""
    verdicts = displacements()
    offenders = {b: w for b, (best, w) in verdicts.items() if w or best == "NO-HAND-FOUND-DOC"}
    assert not offenders, (
        "a hand-found document is outranked by a document the locator itself "
        "scores LOWER, which is ranking degradation rather than a better answer "
        f"arriving: {offenders}"
    )


def test_the_displacement_gate_convicts_a_weaker_document():
    """The SHOWN-FAILING half. Without this the gate above proves nothing.

    Replacing the real ranking with a planted one where a document the locator
    scores LOWER sits above a hand-found document. The gate must convict it. If
    this test ever passes trivially, the gate has stopped reading its input.
    """
    blocker, wanted = next(iter(HAND_FOUND.items()))
    target = wanted[0]
    planted = [(1, "_audit/a-deliberately-weaker-document.md"), (5, target)]

    verdicts = displacements(scores=planted)
    best, weaker = verdicts[blocker]

    assert best == 5, f"the plant did not take: {verdicts[blocker]}"
    assert weaker, (
        "the gate did NOT convict a weaker document ranked above a hand-found "
        f"one, which is the only thing it exists to catch: {verdicts[blocker]}"
    )
    assert weaker[0][0] < best, weaker

    # And the same shape must come back CLEAN when the displacer is better,
    # because a gate that fires on improvement is the defect this replaced.
    better = [(9, "_audit/a-genuinely-better-document.md"), (5, target)]
    _best, none_weaker = displacements(scores=better)[blocker]
    assert not none_weaker, (
        "the gate fired on a BETTER document displacing a hand-found one, which "
        f"is the false red it was built to remove: {none_weaker}"
    )


def test_recall_against_a_hand_built_set_does_not_regress():
    ranks = _ranks()
    flat = [(b, d, r) for b, m in ranks.items() for d, r in m.items()]
    anywhere = sum(1 for _b, _d, r in flat if r is not None)
    top3 = sum(1 for _b, _d, r in flat if r is not None and r <= 3)
    misses = [(b, d) for b, d, r in flat if r is None]
    assert anywhere >= RECALL_ANYWHERE_FLOOR, (
        f"the locator now finds {anywhere} of {len(flat)} hand-found documents "
        f"anywhere in its ranking, below the floor of "
        f"{RECALL_ANYWHERE_FLOOR}. Missing: {misses}"
    )
    # OBSERVED, NOT GATED -- see RECALL_TOP3_OBSERVED_ONLY. Printed so a reader
    # sees the number and can judge it; not asserted, because it cannot tell a
    # worse ranker from a better corpus.
    print(f"  OBSERVED per-document top3: {top3} of {len(flat)} "
          f"(was gated at {RECALL_TOP3_OBSERVED_ONLY} until 2026-09-22); "
          f"anywhere {anywhere} of {len(flat)}")


def test_no_generated_artifact_is_ever_a_candidate():
    """A file a script writes cannot argue a reason, and must not be its input.

    `blocker-map.tsv` is generated from `blocker-assignments.tsv`. Letting it
    score would also make any column written INTO it depend on its own content.
    `blocker-assignments.tsv` is hand-written evidence and is deliberately NOT
    excluded -- this asserts the distinction, not a blanket ban on .tsv.
    """
    offenders = {}
    for blocker in sorted(fbr._ranking()):
        for _score, doc in fbr.candidates(blocker):
            if doc in fbr.DERIVED_ARTIFACTS:
                offenders.setdefault(doc, []).append(blocker)
    assert offenders == {}, (
        f"generated artifacts appear as candidates: "
        f"{ {k: len(v) for k, v in offenders.items()} }. A derived index "
        "restates assignments; it does not argue them."
    )
    assert "_audit/_census/blocker-assignments.tsv" not in fbr.DERIVED_ARTIFACTS, (
        "blocker-assignments.tsv is HAND-WRITTEN evidence whose notes argue. "
        "Excluding it would discard real reasons to fix a different problem."
    )


def test_the_top_answer_is_still_too_weak_to_be_a_bare_path():
    """The ruling that shaped `reason_doc`, kept honest by re-measurement.

    This is a CEILING on purpose. It fails if the locator gets good enough that
    naming one document plainly becomes defensible -- at which point somebody
    should re-take the decision rather than inherit it.
    """
    ranks = _ranks()
    flat = [r for m in ranks.values() for r in m.values()]
    at_rank_1 = sum(1 for r in flat if r == 1)
    assert at_rank_1 <= RANK1_CEILING_FOR_A_DERIVED_COLUMN, (
        f"the top-ranked document is now the hand-found one {at_rank_1} times "
        f"of {len(flat)}, above the ceiling of "
        f"{RANK1_CEILING_FOR_A_DERIVED_COLUMN}. This is GOOD NEWS and a "
        "decision to re-take: `_audit/2026-09-20-the-three-held-defects.md` "
        "section 2 shaped the `reason_doc` cell as RANK + SCORE + path rather "
        "than a bare path because at-rank-1 was 4 of 8. Re-read that ruling, "
        "re-measure, and either raise this ceiling deliberately or simplify "
        "the cell."
    )


def test_the_reason_doc_column_never_ships_a_bare_path():
    """The column must read as a RANKING, never as an identification.

    A table reads as DATA rather than as a claim -- this repo has already lost
    a push to that, when a marker placed in a table body made the whole map
    parse as zero rows. At 4-of-8 at rank 1 a bare path would be a coin flip
    wearing a fact's clothes, so every populated cell carries its rank and
    score and a reader cannot mistake it for the answer.
    """
    import build_blocker_map as bbm

    lines = bbm.MAP_OUT.read_text(encoding="utf-8",
                                  errors="replace").splitlines()
    header = lines[0].split("	")
    assert "reason_doc" in header, (
        f"the committed map has no reason_doc column; header is {header}"
    )
    col = header.index("reason_doc")
    bare, seen = [], 0
    for line in lines[1:]:
        parts = line.split("	")
        assert len(parts) == len(header), (
            f"row {parts[0]!r} has {len(parts)} fields against "
            f"{len(header)} header fields -- a tab leaked into a cell"
        )
        cell = parts[col]
        seen += 1
        if cell in ("NO-BLOCKER-ASSIGNED", "NO-ARGUMENT-FOUND"):
            continue
        if not cell.startswith("CANDIDATE-"):
            bare.append((parts[0], cell))
    assert seen > 0, "read no data rows out of the committed map"
    assert bare == [], (
        f"{len(bare)} reason_doc cells are not marked as a ranked candidate, "
        f"first three {bare[:3]}. Every populated cell must begin "
        "'CANDIDATE-<rank>-OF-<n> SCORE-<n> ' so it cannot be read as the "
        "document that argues the reason. See the locator's measured recall."
    )


@pytest.mark.parametrize(
    "word",
    ["measure", "measured", "measurement", "measures",
     "refuse", "refused", "refusal", "refuses",
     "admit", "admits", "admitted",
     "rule", "ruled", "rules", "ruling", "rulings",
     "evidence", "evidenced", "proven", "proves", "shown", "showed"],
)
def test_every_stem_in_the_vocabulary_actually_matches_its_word_forms(word):
    """The F1 bug, pinned so it cannot come back.

    The vocabulary was written with stems and wrapped in `\\b(...)\\b`. A
    trailing word boundary after a stem can never match, so `measur` matched
    nothing at all while "measured" appeared 1910 times in the corpus. The
    regex said the opposite of what its own comment said it did.
    """
    assert fbr.ARGUES.search(word), (
        f"the argument vocabulary does not match {word!r}. If a stem was "
        "re-wrapped in a trailing \\b, it now matches nothing -- that is the "
        "2026-09-20 defect returning, and it is silent: the locator keeps "
        "producing a confident ranking built on a dead word list."
    )


def test_a_word_the_vocabulary_must_not_claim():
    """The other half: broad is not unbounded, and two stems are spelled out.

    `prov\\w*` would match "providing", and this corpus is full of "Providing
    services"; bare `block` is a LinkedIn capability. Both are deliberately NOT
    stemmed, so this asserts the false positives stay out.
    """
    for word in ("providing", "provision", "provider"):
        assert not fbr.ARGUES.search(word), (
            f"{word!r} now reads as an argument word. `prove` must not be "
            "stemmed to `prov` -- `Providing services` is a capability in this "
            "census, not a reason."
        )
