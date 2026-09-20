"""Controls and the pin for `scripts/check_cited_shas_resolve.py`.

WHAT THIS MODULE PINS. 22 distinct SHAs, across 26 (token, document) rows and
29 citation sites, that sit in a commit slot in a tracked `_audit/` document
and that **no clone of this repository can resolve**. They are pinned rather
than repaired: they live in nineteen documents belonging to other waves, and
the wave that built this detector is the wrong party to rewrite them.

THE RATCHET RUNS BOTH WAYS.

    a NEW unresolvable citation appears -> RED, naming it
    a PINNED one is repaired            -> RED, saying so, and asking for the
                                           pin to be narrowed in the same commit

The second direction is the one worth having. A pin that only ever grows is a
suppression list; a pin that reds when a defect DISAPPEARS forces somebody to
say whether it was fixed or whether the detector stopped seeing it. Those two
look identical from the outside and only one of them is good news.

THE CONTROL THAT MATTERS MOST is `test_ancestry_not_existence_is_the_predicate`.
This guard exists because `git cat-file` answers the WRONG QUESTION here, and
answers it in the direction that looks like a pass: this repository keeps a
`pre-purge-restore` tag and 80+ `worktree-agent-*` branches, so a commit no
clone can reach still answers "commit" locally. If that control ever goes
green-by-accident -- because the local branch it uses got deleted -- the guard
silently becomes the broken thing it replaced, so the control asserts the
branch exists FIRST and fails loudly rather than skipping.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import check_cited_shas_resolve as guard  # noqa: E402


#: (token, document, occurrences) -- measured at 800b617, 2026-09-20.
#: Named with the evidence in `_audit/2026-09-20-the-sixty-dangling.md`.
#:
#: WHAT THEY HAVE IN COMMON, and it is not the August history rewrite that
#: produced the previous batch: all but one are commits made on a
#: `worktree-agent-*` branch by a wave that then reported its work by SHA. The
#: branch never merged, so the SHA never reached `master`, so the citation was
#: unresolvable from the moment it was written. This is a LIVE generator, not
#: an inherited mess.
PINNED: set[tuple[str, str, int]] = {
    ("f6ddfe3", "_audit/2026-09-03-typeahead-name-matching-is-dead.md", 1),
    ("ae1894b", "_audit/2026-09-19-blocker-conflicts.md", 1),
    ("c4d2be2", "_audit/2026-09-19-blocker-conflicts.md", 3),
    ("1349fe6", "_audit/2026-09-19-blocker-map-ruling-requests.md", 1),
    ("a604394", "_audit/2026-09-19-blocker-map-ruling-requests.md", 1),
    ("7bca683", "_audit/2026-09-19-blocker-table-refresh.md", 1),
    ("c1991ac", "_audit/2026-09-19-events-surface.md", 1),
    ("744a1f4", "_audit/2026-09-19-groups-admission.md", 1),
    ("7668b40", "_audit/2026-09-19-groups-admission.md", 1),
    ("a5a988a", "_audit/2026-09-19-groups-admission.md", 1),
    ("1349fe6", "_audit/2026-09-19-premium-apply-surfaces.md", 1),
    ("12c20e1", "_audit/2026-09-19-routing-the-unassigned.md", 1),
    ("569dc5e", "_audit/2026-09-19-search-admission-preconditions.md", 1),
    ("d588034", "_audit/2026-09-19-search-admission-preconditions.md", 1),
    ("c48ec60", "_audit/2026-09-19-the-first-sanctioned-press.md", 1),
    ("66e2038", "_audit/2026-09-19-the-gate-at-zero.md", 1),
    ("806360a", "_audit/2026-09-19-the-gate-at-zero.md", 1),
    ("eed87a5", "_audit/2026-09-19-the-gate-at-zero.md", 1),
    ("59192ac", "_audit/2026-09-19-the-last-five-reds.md", 1),
    ("889f488", "_audit/2026-09-19-the-last-two-reds.md", 2),
    ("c1991ac", "_audit/2026-09-19-the-three-ruling-requests-ruled.md", 1),
    ("12c20e1", "_audit/2026-09-19-the-unassigned-21.md", 1),
    ("5c5ebf9dda43", "_audit/2026-09-19-tier1-fires.md", 1),
    ("70d7c0f62e97", "_audit/2026-09-19-tier2-fires.md", 1),
    ("12c20e1", "_audit/2026-09-19-two-waves-agreed-on-nine-rows.md", 1),
    ("ded0048", "_audit/2026-09-19-unblocking-the-stranded-commits.md", 1),
}

#: Every verdict the classifier can hand down other than the finding itself.
#: Kept explicit so that ADDING a suppressor without a corpus example fails
#: `test_every_suppressor_fires_on_the_real_corpus` rather than passing unseen.
SUPPRESSORS = (
    "MARKED-MAPPED",
    "MARKED-DEAD-DOC",
    "MARKED-CROSS-REPO",
    "MARKED-DISCLOSED",
)


@pytest.fixture(scope="module")
def measured():
    return guard.run(REPO)


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(REPO), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


# --------------------------------------------------------------------------
# CONTROLS
# --------------------------------------------------------------------------

def test_ancestry_not_existence_is_the_predicate():
    """A commit that exists locally but is off `master` must NOT resolve.

    This is the entire reason this guard exists rather than a `cat-file` one:
    `cat-file -e` says yes to any object in the store, and a clone says no to
    everything off `master`.

    THE FIXTURE IS MANUFACTURED, AND IT USED TO BE FOUND. This control pinned
    `integrate-1821` -- a branch that exists on the box this was written on,
    resolves in no clone, and is under a standing ruling never to be pushed
    (`_audit/2026-09-20-the-six-unremapped.md`: "KEEP, do not delete, do not
    push, do not modify"). So the control was green locally and went red on
    all three CI platforms the instant it was published. That is this guard's
    own subject arriving inside its own control: a test that assumes its repo
    holds a ref nobody else has is the same error as a wave citing a SHA on a
    branch that never merged.

    `commit-tree` builds the fixture from `master`'s own tree instead. It
    writes one dangling commit object, depends on no ref, and satisfies both
    preconditions in any clone -- the object exists, and it is an ancestor of
    nothing.
    """
    tip = _git(
        "-c", "user.name=control",
        "-c", "user.email=control@example.invalid",
        "commit-tree", "master^{tree}",
        "-m", "off-master fixture for the ancestry control",
    ).stdout.strip()
    assert re.fullmatch(r"[0-9a-f]{40}", tip), (
        "could not manufacture the control's fixture with commit-tree, so this "
        "control cannot distinguish a working guard from a broken one. Do not "
        "skip -- without it the guard can pass on existence instead of ancestry."
    )
    assert _git("cat-file", "-e", tip + "^{commit}").returncode == 0, (
        "control precondition: the object must EXIST locally, or this proves nothing"
    )
    assert _git("merge-base", "--is-ancestor", tip, "master").returncode != 0, (
        "control precondition: it must NOT be an ancestor of master"
    )
    assert guard.resolves(REPO, tip) is False, (
        "THE GUARD IS USING EXISTENCE, NOT ANCESTRY. It will pass green on every "
        "citation a clone cannot resolve, which is the defect it was built for."
    )


def _on_master() -> str:
    """A short SHA that a clone CAN resolve.

    Deliberately `master` and not `HEAD`. This suite is normally run from a
    `worktree-agent-*` branch, and such a branch's own HEAD is exactly the
    thing this guard convicts -- it is not an ancestor of `master` until the
    branch merges. Written as `HEAD` first, and every positive control went red
    the moment the wave made its own commit: **the guard caught its own test
    suite committing the defect the guard exists to find.**
    """
    short = _git("rev-parse", "--short=7", "master").stdout.strip()
    assert re.fullmatch(r"[0-9a-f]{7,}", short), (
        f"cannot resolve `master` to a short sha (got {short!r}); the positive "
        "controls below cannot run and must not be skipped"
    )
    return short


def test_a_known_good_abbreviation_resolves():
    """The mirror control: an instrument that resolves NOTHING reports
    everything missing and looks exactly like a finding."""
    assert guard.resolves(REPO, _on_master()) is True


def test_a_nonsense_token_does_not_resolve():
    assert guard.resolves(REPO, "0000000") is False


def test_the_detector_finds_a_planted_citation(tmp_path):
    """RED PROOF. A guard that has never been shown failing certifies nothing."""
    blob = "Measured at `deadbee` on a settled tree.\n"
    sites = guard.candidates({"_audit/_planted.md": blob})
    assert [s.token for s in sites] == ["deadbee"], sites
    assert sites[0].verdict == "CANDIDATE"
    assert [s.token for s in guard.findings(REPO, sites)] == ["deadbee"]


def test_a_resolvable_citation_is_not_convicted():
    sha = _on_master()
    blob = f"Measured at `{sha}` on a settled tree.\n"
    sites = guard.candidates({"_audit/_planted.md": blob})
    assert [s.token for s in sites] == [sha]
    assert guard.findings(REPO, sites) == []


def test_a_token_outside_any_slot_is_never_a_candidate():
    """KIND BEFORE RESOLUTION. `a540461` is a real commit and `a1341821` is a
    help-article id; neither may enter on shape alone."""
    blob = (
        "The census `source` column reads a1341821 and a540461 beside each other.\n"
        "Run id 32661307599 succeeded on all three cells.\n"
    )
    assert guard.candidates({"_audit/_planted.md": blob}) == []


def test_an_all_digit_sha_is_not_filtered_out():
    """`5480246`, `5581950` and `9580360` are all-digit and are real commits.

    Every "not all digits" pre-filter in use elsewhere drops them silently, so
    this control asserts the shape rule was not quietly re-introduced.
    """
    blob = "The pin was applied at `5480246` upstream.\n"
    sites = guard.candidates({"_audit/_planted.md": blob})
    assert [s.token for s in sites] == ["5480246"]


def test_the_digest_bound_hides_no_resolving_citation(measured):
    """The ONE shape rule must not be load-bearing in the wrong direction.

    It excludes exactly 16 characters. Assert that no 16-character hex token
    anywhere in the corpus resolves as a commit -- if one ever does, the bound
    is deleting signal and must be re-measured rather than kept.
    """
    seen: set[str] = set()
    rx = re.compile(r"(?<![0-9a-zA-Z_./-])([0-9a-f]{16})(?![0-9a-zA-Z_])")
    for blob in guard.load_corpus(REPO).values():
        seen.update(rx.findall(blob))
    assert seen, "found no 16-char tokens at all -- the bound's premise is unmeasured"
    resolving = sorted(t for t in seen if guard.resolves(REPO, t))
    assert resolving == [], (
        f"these 16-character tokens DO resolve as commits: {resolving}. "
        "DIGEST_LENGTHS is discarding real citations; re-measure the length "
        "table in the module docstring before touching anything else."
    )


def test_every_suppressor_fires_on_the_real_corpus(measured):
    """A suppressor with no corpus example is a hole nobody can see.

    Each of the four must claim at least one real site, or it is either dead
    code or wrong -- and a dead suppressor is indistinguishable from a working
    one until the day it is needed.
    """
    sites, _ = measured
    verdicts = {s.verdict for s in sites}
    missing = [s for s in SUPPRESSORS if s not in verdicts]
    assert not missing, (
        f"these suppressors matched NOTHING in the corpus: {missing}. "
        f"Verdicts actually seen: {sorted(verdicts)}."
    )


#: WHY THESE ARE TESTED ONE SOURCE AT A TIME, and it is a finding rather than
#: a style choice. The first version of this control stripped ONE mark and
#: asserted the citation was convicted again. It failed on both cases -- not
#: because the suppressors are broken, but because they OVERLAP: the two
#: repaired documents each carry a top-of-file "EVERY SHORT SHA IN THIS FILE IS
#: DEAD" declaration AND a "## Dead hashes, recovered" mapping table, so
#: removing either one leaves the other still covering the token.
#:
#: **A UNION ASSERTION OVER A REDUNDANT CORPUS CANNOT DETECT A LOST SOURCE.**
#: If the mapping-table parser silently broke tomorrow, a "is it still
#: suppressed?" test would stay green on the declaration alone, and the parser
#: would be dead code nobody noticed. So each source is asserted to produce ITS
#: OWN verdict, and the full strip is a separate case.
_MARK_SOURCES = [
    ("_audit/2026-08-24-perform-save-unsave.md", "5a69147", "MARKED-MAPPED",
     lambda b: b.replace("## Dead hashes, recovered", "## Notes")),
    ("_audit/2026-08-24-out-of-scope-wave.md", "5bc0181", "MARKED-MAPPED",
     lambda b: b.replace("## Dead hashes, recovered", "## Notes")),
]


def test_the_dead_doc_declaration_suppresses_and_can_be_defeated():
    """The declaration suppressor, controlled on a PLANTED document -- and why.

    It has NO exclusive example in the corpus today. Both documents that carry
    a top-of-file "EVERY SHORT SHA IN THIS FILE IS DEAD" note ALSO carry a
    mapping table, and the table is checked first, so the declaration's only
    real-corpus firings are on two hashes that resolve anyway. Controlling it
    against the corpus would therefore assert nothing.

    It is kept rather than deleted because declaring a document's SHAs dead
    WITHOUT a mapping table is a legitimate repair -- it is what you do when no
    honest twin exists -- and a guard that convicts that repair is a guard that
    gets switched off. So it is controlled here, on a document written for the
    purpose, and its thinness in the corpus is stated rather than hidden.
    """
    cited = "Measured at `deadbee` on a settled tree.\n"
    declared = "> **EVERY SHORT SHA IN THIS FILE IS DEAD.** Added 2026-09-20.\n\n" + cited

    plain = guard.candidates({"_audit/_planted.md": cited})
    assert [s.verdict for s in plain] == ["CANDIDATE"]

    marked = guard.candidates({"_audit/_planted.md": declared})
    assert [s.verdict for s in marked] == ["MARKED-DEAD-DOC"], marked

    defeated = guard.candidates(
        {"_audit/_planted.md": declared.replace("IS DEAD", "is fine")}
    )
    assert [s.verdict for s in defeated] == ["CANDIDATE"], defeated


def test_quoting_the_declaration_does_not_declare():
    """A document DISCUSSING the declaration must not be cleared by it.

    FOUND IN THIS GUARD, BY THIS GUARD, AFTER IT WAS COMMITTED. The audit
    document reporting this wave quotes "EVERY SHORT SHA IN THIS FILE IS DEAD"
    twice -- once in prose, once in a table of suppressors -- and the first
    version of the pattern read both AS declarations, silently clearing every
    citation in the reporting document. `MARKED-DEAD-DOC` went 2 -> 9 and the
    guard got QUIETER, which is the worst direction for a defect to move.

    Third instance of one shape in this repository: a correction-marker guard
    reading a sentence about markers as a marker; the register quoting a
    planted citation into a live commit slot; and this. The fix is positional
    for the same reason the correction guard's was anchoring -- a declaration
    is something a reader meets BEFORE the citations it covers.
    """
    filler = "\n".join(f"Filler line {i}." for i in range(_FAR_BELOW_PREAMBLE))
    quoting = (
        "# A report about dead-SHA declarations\n\n"
        + filler
        + "\n\nThe two repaired documents each say "
        '*"EVERY SHORT SHA IN THIS FILE IS DEAD"* at the top.\n'
        # Far enough below the quote that the DISCLOSURE window cannot reach
        # it either -- this control is about the DECLARATION suppressor alone,
        # and a fixture that trips a second one proves nothing about the first.
        + "\n".join(f"More prose {i}." for i in range(10))
        + "\nMeasured at `deadbee` on a settled tree.\n"
    )
    sites = guard.candidates({"_audit/_planted.md": quoting})
    assert [s.token for s in sites] == ["deadbee"], sites
    assert sites[0].verdict == "CANDIDATE", (
        "a document QUOTING the declaration was treated as making one; the "
        f"suppressor is matching a phrase rather than a position (got "
        f"{sites[0].verdict})"
    )


#: Comfortably past `_DECLARATION_WINDOW`, so the quote in the control above
#: lands in the body rather than the preamble where a real declaration sits.
_FAR_BELOW_PREAMBLE = 60


@pytest.mark.parametrize("doc, token, verdict, mutate", _MARK_SOURCES)
def test_each_mark_source_produces_its_own_verdict(doc, token, verdict, mutate):
    """MUTATION FINDS WHAT READING DOES NOT, asserted PER SOURCE.

    Break one mark and THAT verdict must stop being handed down -- whatever
    else may still cover the token. A suppressor that cannot be turned off is
    not suppressing anything; it is a constant wearing a suppressor's name.
    """
    blob = (REPO / doc).read_text(encoding="utf-8", errors="replace")
    before = [s for s in guard.candidates({doc: blob}) if s.token == token]
    assert before, f"fixture drift: {token} is no longer cited in {doc}"
    assert any(s.verdict == verdict for s in before), (
        f"{token} in {doc} is not {verdict} to begin with "
        f"(it is {sorted({s.verdict for s in before})}); this control cannot "
        "show that suppressor doing anything"
    )
    after = [s for s in guard.candidates({doc: mutate(blob)}) if s.token == token]
    assert all(s.verdict != verdict for s in after), (
        f"removing the mark did not stop {verdict} being handed down for "
        f"{token}: that source is not what was producing it, so something "
        "else is silently doing the work"
    )


def test_stripping_every_mark_reconvicts():
    """The other half: with ALL cover removed the citation must come back.

    Per-source assertions prove each suppressor is live; only this one proves
    that together they are the whole of what clears the token, and that nothing
    else is quietly excusing it.
    """
    doc = "_audit/2026-08-24-perform-save-unsave.md"
    blob = (REPO / doc).read_text(encoding="utf-8", errors="replace")
    stripped = (
        blob.replace("## Dead hashes, recovered", "## Notes")
        .replace("EVERY SHORT SHA IN THIS FILE IS DEAD", "some shas here")
    )
    after = [s for s in guard.candidates({doc: stripped}) if s.token == "5a69147"]
    assert after, "fixture drift: 5a69147 is no longer cited in that document"
    assert any(s.verdict == "CANDIDATE" for s in after), (
        "with every mark removed the citation is STILL suppressed -- some "
        f"unaccounted rule is clearing it: {sorted({s.verdict for s in after})}"
    )


def test_an_empty_corpus_fails_rather_than_passes():
    """AN ASSERTION SATISFIED BY AN EMPTY RESULT CANNOT FAIL.

    The guard's worst failure mode is selecting nothing -- a broken slot regex
    reports a spotless corpus. `main` must treat that as a hard failure.
    """
    assert guard.candidates({}) == []
    assert guard.findings(REPO, []) == []


def test_the_guard_stays_cheap_enough_to_gate():
    import time
    t0 = time.perf_counter()
    guard.run(REPO)
    elapsed = time.perf_counter() - t0
    assert elapsed < 120, f"guard took {elapsed:.1f}s; too slow to gate on"


# --------------------------------------------------------------------------
# THE PIN
# --------------------------------------------------------------------------

def test_no_new_unresolvable_citation_appears(measured):
    import collections
    _, bad = measured
    seen = {
        (tok, doc, n)
        for (tok, doc), n in collections.Counter((s.token, s.doc) for s in bad).items()
    }
    appeared = sorted(seen - PINNED)
    repaired = sorted(PINNED - seen)

    assert not appeared, (
        f"NEW unresolvable SHA citation(s): {appeared}. A short SHA in an audit "
        "document is a promise a reader can check, and these cannot be checked "
        "from any clone. Record the commit SUBJECT -- it survives a rewrite and "
        "a branch deletion -- or say in the document that the SHA resolves only "
        "on a branch. Do NOT delete the hash: it is the key a reader arrives with."
    )
    assert not repaired, (
        f"these pinned defects are gone: {repaired}. If they were REPAIRED, that "
        "is good and PINNED above must be narrowed in the SAME commit, with the "
        "repair recorded. If instead the DETECTOR stopped seeing them, the pin "
        "just hid a regression -- check `test_the_detector_finds_a_planted_citation` "
        "and `test_every_suppressor_fires_on_the_real_corpus` before editing PINNED."
    )
