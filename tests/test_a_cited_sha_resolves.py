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


#: **THE PIN IS EMPTY, 2026-09-20, BECAUSE THE DEFECT IS GONE AND NOT BECAUSE
#: THE DETECTOR STOPPED SEEING IT.** All 26 (token, document) rows previously
#: pinned here -- 22 distinct SHAs across 29 citation sites in 19 documents --
#: were REPAIRED by the `evidence-that-resolves` wave. The evidence is in
#: `_audit/2026-09-20-the-evidence-that-resolves.md` and the receipt that made
#: the edits is `scripts/_repair_branch_only_citations.py`.
#:
#: WHAT THEY WERE. Commits made on a `worktree-agent-*` branch by a wave that
#: then reported its work by SHA. The branch never merged, so the SHA never
#: reached `master`, so the citation was unresolvable from the moment it was
#: written.
#:
#: WHAT THE REPAIR FOUND, and it is the reason every one could be repaired
#: rather than annotated: **all 22 commits have an exact twin on `master`** --
#: byte-identical subject, byte-identical author identity and date, and an
#: identical `git patch-id --stable`, each subject occurring exactly once on
#: `master`. The branches never merged but the WORK was re-applied. Each
#: document now carries a `## Dead hashes, recovered` table naming that twin,
#: and the dead hash is kept in place because it is the key a reader arrives
#: with.
#:
#: **AN EMPTY PIN HERE IS STRONGER THAN A FULL ONE, and that is worth stating
#: because it looks like the opposite.** With nothing pinned, ANY regression in
#: the suppressors -- a broken mapping-table parser, a lost declaration, a
#: dropped cross-repo entry -- puts a citation straight back into `bad`, and
#: `appeared` is then non-empty and this test goes RED naming it. A pin of 26
#: absorbed exactly those regressions silently for the 26. The one direction an
#: empty pin cannot cover is the detector going blind, and that is held by
#: `test_the_detector_finds_a_planted_citation`,
#: `test_every_suppressor_fires_on_the_real_corpus` and
#: `test_a_mapping_row_that_cannot_be_checked_is_a_finding`.
PINNED: set[tuple[str, str, int]] = set()

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


def test_a_sentence_initial_committed_is_a_slot():
    """A capitalised, sentence-initial "Committed `...`" must be a candidate.

    The `committed` slot's keyword was case-sensitive, so a citation that
    opens a sentence -- as lane L3's record wrote `Committed `d111560`` --
    never matched the pattern at all, and the citation was never checked.
    """
    blob = "Committed `deadbee` on a settled tree.\n"
    sites = guard.candidates({"_audit/_planted.md": blob})
    assert [s.token for s in sites] == ["deadbee"], sites
    assert sites[0].verdict == "CANDIDATE", sites
    assert [s.token for s in guard.findings(REPO, sites)] == ["deadbee"]


def test_the_case_fold_reaches_the_keyword_and_never_the_hex():
    """The fix's case fold must cover only the keyword, never the hex class.

    Uppercase hex is not this corpus's citation shape (`HEX` is
    `[0-9a-f]{7,40}`, lowercase only), so widening the keyword match must not
    also widen what counts as a hex digit -- a capitalised token must still
    be rejected, and the plain lowercase form must keep working.
    """
    upper = "Committed `DEADBEE` on a settled tree.\n"
    assert guard.candidates({"_audit/_planted.md": upper}) == []

    lower = "committed `deadbee` on a settled tree.\n"
    sites = guard.candidates({"_audit/_planted.md": lower})
    assert [s.token for s in sites] == ["deadbee"], sites


#: ONE CAPITALISED PLANT PER KEYWORD SLOT. The ``committed`` defect was never
#: that slot's alone: every keyword here was lowercase-only, and folding them
#: was MEASURED before it was done -- over the tracked corpus it adds 35
#: (token, site) pairs this guard had never checked, 33 of which resolve and
#: two of which are already suppressed at the same site (``56e03b0`` in a
#: document declaring its SHAs dead, ``c4d2be2`` already MARKED-MAPPED through
#: the lowercase ``at``), so ZERO new findings. Each slot is asserted through
#: its OWN pattern, because ``candidates`` hands a site to whichever slot
#: matches first and several of these plants would also match ``at``.
_CAPITALISED_PLANTS = {
    "at-backtick": "At `deadbee` the tree was settled.",
    "at-bare": "At deadbee the tree was settled.",
    "commit": "Commit `deadbee` carried it.",
    "committed": "Committed `deadbee` on a settled tree.",
    "landed-on": "Landed on `deadbee` after review.",
    "landed-after": "`deadbee` Landed first.",
    "applied": "Applied as `deadbee` to the tree.",
    "introduced-at": "Introduced at `deadbee` by the wave.",
    "baseline": "Baseline `deadbee` held.",
    "pinned-commit": "Pinned commit `deadbee` held.",
}

#: Slots with no keyword to fold -- pure punctuation around the hex.
_KEYWORDLESS_SLOTS = frozenset({"range-lhs", "range-rhs", "show-path"})


@pytest.mark.parametrize("slot_name", sorted(_CAPITALISED_PLANTS))
def test_every_keyword_slot_reads_a_capitalised_keyword(slot_name):
    """RED PROOF per slot: a sentence-initial keyword is still the slot."""
    pattern = {slot.name: slot.pattern for slot in guard.SLOTS}[slot_name]
    line = _CAPITALISED_PLANTS[slot_name]
    match = pattern.search(line)
    assert match is not None and match.group(1) == "deadbee", (
        f"slot {slot_name!r} does not read its own keyword capitalised: {line!r}"
    )
    assert pattern.search(line.replace("deadbee", "DEADBEE")) is None, (
        f"slot {slot_name!r} folded the HEX class as well as the keyword"
    )


def test_every_slot_is_either_folded_or_keywordless():
    """A keyword slot added tomorrow without a capitalised plant fails here."""
    names = {slot.name for slot in guard.SLOTS}
    assert names == set(_CAPITALISED_PLANTS) | _KEYWORDLESS_SLOTS, (
        f"unaccounted slots: {sorted(names - set(_CAPITALISED_PLANTS) - _KEYWORDLESS_SLOTS)}; "
        f"stale plants: {sorted((set(_CAPITALISED_PLANTS) | _KEYWORDLESS_SLOTS) - names)}"
    )


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


# --------------------------------------------------------------------------
# THE MAPPING ROW MUST PAY FOR ITSELF
#
# `MARKED-MAPPED` is the strongest suppressor here: one table row silences a
# dead hash at every site in its document. Until 2026-09-20 it fired on the
# mere PRESENCE of the hash in column 0, so a row naming a garbage live hash --
# or none -- switched the guard off just as effectively as a correct one.
# **A repair nobody can check is this guard's own defect wearing its uniform.**
# --------------------------------------------------------------------------

_GOOD_TABLE = (
    "# A document\n\n"
    "Measured at `{dead}` on a settled tree.\n\n"
    "## Dead hashes, recovered\n\n"
    "| dead hash | subject (the durable reference) | live hash | confidence |\n"
    "|---|---|---|---|\n"
    "| `{dead}` | {subject} | `{live}` | CONFIRMED |\n"
)


def _live_and_subject():
    short = _on_master()
    subject = _git("log", "-1", "--format=%s", short).stdout.rstrip("\n")
    return short, subject


def test_a_correct_mapping_row_suppresses_and_checks_out():
    """The positive control. Without it the red proof below proves nothing:
    an instrument that convicts everything convicts a correct row too."""
    live, subject = _live_and_subject()
    blob = _GOOD_TABLE.format(dead="deadbee", live=live, subject=subject)
    sites = guard.candidates({"_audit/_planted.md": blob})
    assert [s.verdict for s in sites if s.token == "deadbee"] == ["MARKED-MAPPED"], sites
    claims = guard.remap_claims({"_audit/_planted.md": blob})
    assert len(claims) == 1, claims
    assert guard.broken_remaps(REPO, claims) == []


@pytest.mark.parametrize("label, mutate, needle", [
    ("live hash does not resolve",
     lambda b, live, subj: b.replace("`" + live + "`", "`0000000`"),
     "does not resolve"),
    ("no live hash at all, and silent about it",
     lambda b, live, subj: b.replace("| `" + live + "` | CONFIRMED |", "| -- | CONFIRMED |"),
     "names no live hash"),
    ("subject cell names a different commit",
     lambda b, live, subj: b.replace(subj, "chore: a subject this commit does not have"),
     "does not match the live commit"),
    ("the row maps the hash to itself",
     lambda b, live, subj: b.replace("`deadbee`", "`" + live + "`"),
     "maps the hash to itself"),
])
def test_a_mapping_row_that_cannot_be_checked_is_a_finding(label, mutate, needle):
    """RED PROOF, four ways. A check that has never been shown failing
    certifies nothing, and this one suppresses 44 occurrences in the live
    corpus -- it is the most load-bearing check in the file."""
    live, subject = _live_and_subject()
    blob = mutate(_GOOD_TABLE.format(dead="deadbee", live=live, subject=subject),
                  live, subject)
    claims = guard.remap_claims({"_audit/_planted.md": blob})
    assert claims, f"{label}: the mutation destroyed the row itself, so nothing was tested"
    bad = guard.broken_remaps(REPO, claims)
    assert bad, f"{label}: the check passed a row it cannot verify"
    assert needle in bad[0][1], (label, bad[0][1])


def test_a_declared_no_twin_row_is_not_convicted_and_the_exemption_can_be_defeated():
    """THE EXEMPTION, controlled -- and it exists because the check convicted
    the corpus's own correct repair on its first run.

    `94600de` and `db99276` in `2026-08-24-perform-save-unsave.md` read
    `| ... | **UNMAPPED** -- see below | -- | UNMAPPED |` and the document
    spends two paragraphs on why no honest twin exists. Recording the gap IS
    the repair. A guard that convicts it is a guard that gets switched off.
    """
    row = ("# A document\n\nMeasured at `deadbee` on a settled tree.\n\n"
           "## Dead hashes, recovered\n\n"
           "| dead hash | subject | live hash | confidence |\n|---|---|---|---|\n"
           "| `deadbee` | **UNMAPPED** -- see below | -- | UNMAPPED |\n")
    claims = guard.remap_claims({"_audit/_planted.md": row})
    assert len(claims) == 1 and claims[0].declares_no_twin
    assert guard.broken_remaps(REPO, claims) == []

    # Defeat it: the SAME row with an ordinary confidence cell is a finding.
    silent = row.replace("| -- | UNMAPPED |", "| -- | CONFIRMED |")
    claims = guard.remap_claims({"_audit/_planted.md": silent})
    assert not claims[0].declares_no_twin
    assert guard.broken_remaps(REPO, claims), (
        "a row with no live hash and no declaration was accepted; the "
        "exemption is matching something other than the declaration"
    )


def test_the_whole_corpus_mapping_table_checks_out(measured):
    """The live reading. 51 rows across 21 documents at the time of writing."""
    blobs = guard.load_corpus(REPO)
    claims = guard.remap_claims(blobs)
    assert claims, "no mapping rows found at all -- the table parser is broken"
    bad = guard.broken_remaps(REPO, claims)
    assert bad == [], "\n".join(f"{c}: {why}" for c, why in bad)


# --------------------------------------------------------------------------
# THE IN-LINE MARKER MUST BE SELF-VERIFYING
# --------------------------------------------------------------------------

#: The 2026-09-20 repair writes, at the citation itself:
#:
#:     at `c4d2be2` (branch-only; on `master` at `5073827`)
#:
#: The live hash is deliberately placed in the ``at `X` `` slot this guard
#: already reads, so a marker naming a hash that does not resolve is convicted
#: by the EXISTING matcher and no new one was needed.
#:
#: THAT ONLY WORKS IF THE TWO STAY ON ONE LINE, and the first pass of the
#: repair did not. `candidates()` scans line by line; six markers wrapped
#: between `at` and the backtick, so six live hashes sat in no slot and were
#: verified by nothing, and a seventh marker pushed itself between `806360a`
#: and the `landed` that gave that token its only slot -- so the DEAD hash
#: vanished from the guard entirely, which reads the same from outside as a
#: hash somebody deleted. Both were caught by measuring the repair rather than
#: by reading it, and this test is what makes the next one impossible.
_MARKER = "`master` at `"


def _marker_live_tokens(blob: str):
    """Every marker occurrence whose live slot holds something HASH-SHAPED.

    The hex requirement is not decoration. Documents that EXPLAIN the marker
    write it with a placeholder -- ``on `master` at `<live>` `` -- and a
    placeholder is not a claim about any commit, so demanding it sit in a
    commit slot convicts a document for describing the mechanism correctly.
    That is 37.8's shape one more time, arriving through the control rather
    than through the guard.

    The filter is safe in the only direction that matters because
    `test_every_inline_remap_marker_is_self_verifying` also asserts a COUNT
    FLOOR: if this predicate ever started eating real markers, the count would
    drop below 21 and the test would go red rather than quietly checking less.
    """
    for lineno, line in enumerate(blob.splitlines(), 1):
        start = 0
        while True:
            i = line.find(_MARKER, start)
            if i < 0:
                break
            rest = line[i + len(_MARKER):]
            end = rest.find("`")
            if end > 0:
                token = rest[:end]
                if re.fullmatch(r"[0-9a-f]{7,40}", token):
                    yield lineno, line, token
            start = i + len(_MARKER)


def test_every_inline_remap_marker_is_self_verifying():
    found = 0
    for doc, blob in sorted(guard.load_corpus(REPO).items()):
        if "branch-only" not in blob:
            continue
        for lineno, line, token in _marker_live_tokens(blob):
            found += 1
            in_slot = {
                m.group(1)
                for slot in guard.SLOTS
                for m in slot.pattern.finditer(line)
            }
            assert token in in_slot, (
                f"{doc}:{lineno} names `{token}` as the live twin but the token "
                "sits in NO commit slot on that line -- most likely the line "
                "wrapped between `at` and the backtick. Nothing verifies this "
                "marker, so a wrong hash here would never be caught.\n"
                f"  line: {line.strip()[:140]}"
            )
            assert guard.resolves(REPO, token), (
                f"{doc}:{lineno} names `{token}` as a `master` twin and it does "
                "not resolve as an ancestor of master"
            )
    assert found >= 21, (
        f"only {found} in-line remap markers found; the 2026-09-20 repair wrote "
        "21 and a drop means the corpus lost them or this matcher broke"
    )


def test_a_placeholder_marker_is_not_treated_as_a_claim():
    """The hex filter, controlled in both directions.

    A document explaining the marker writes it with a placeholder. That is
    prose about the mechanism and must not be audited as the mechanism -- but
    the filter must not be so loose that a real marker slips through it
    either, so both cases are asserted here together.
    """
    live = _on_master()
    template = "The marker is ``on `master` at `<live>` ``, which puts it in a slot."
    real = f"Applied at `deadbee` (branch-only; on `master` at `{live}`)."
    assert list(_marker_live_tokens(template)) == [], (
        "a placeholder was read as a live-hash claim"
    )
    assert [t for _, _, t in _marker_live_tokens(real)] == [live]


def test_the_marker_matcher_convicts_a_wrapped_marker():
    """MUTATION. The test above must be able to fail, or it is decoration.

    Break one marker the way the repair's own first pass broke six -- wrap the
    line between `at` and the backtick -- and the token must leave the slot.
    """
    live = _on_master()
    good = f"Applied at `deadbee` (branch-only; on `master` at `{live}`)."
    wrapped = f"Applied at `deadbee` (branch-only; on `master` at\n`{live}`)."

    def slotted(text):
        return {
            m.group(1)
            for line in text.splitlines()
            for slot in guard.SLOTS
            for m in slot.pattern.finditer(line)
        }

    assert live in slotted(good), "the intact marker was not in a slot to begin with"
    assert live not in slotted(wrapped), (
        "a marker wrapped between `at` and the backtick was STILL found in a "
        "slot; this control cannot detect the defect it was written for"
    )


def test_a_marker_alone_suppresses_nothing():
    """THE MARKER IS NOT A SUPPRESSOR, and this is the control for the trap
    this repository has now hit four times: prose about a mechanism read as
    the mechanism.

    The marker is a courtesy to a human reading mid-document. The MAPPING
    TABLE is what silences the guard. So a document that carries the marker
    phrase and no table must still be convicted -- which also means a document
    that merely QUOTES a marker (this wave's own audit file does, repeatedly)
    cannot clear anything.
    """
    live = _on_master()
    blob = (
        "# A document\n\n"
        f"Applied at `deadbee` (branch-only; on `master` at `{live}`).\n"
    )
    sites = guard.candidates({"_audit/_planted.md": blob})
    assert {s.token for s in sites} == {"deadbee", live}, sites
    verdicts = {s.token: s.verdict for s in sites}
    assert verdicts["deadbee"] == "CANDIDATE", (
        "the marker phrase suppressed the dead hash on its own; it is being "
        f"read as a mark rather than as prose (got {verdicts['deadbee']})"
    )
    assert [s.token for s in guard.findings(REPO, sites)] == ["deadbee"]


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
