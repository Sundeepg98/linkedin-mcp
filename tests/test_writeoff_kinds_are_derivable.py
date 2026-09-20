"""Guard: every written-off census row carries a derivable KIND, PER FILE.

WHAT THIS TESTS. `scripts/classify_writeoff_reasons.py` sorts all 309 written-off census
rows by the kind of fact their reason rests on -- US-RULING, US-BOUNDARY, WORLD-FACT,
ACCOUNT-FACT, PROCESS-FACT -- so that the CONTINGENT ones, the write-offs that depend on
something outside this codebase and go stale silently, can be listed and re-checked.

The tests below are the SHOWN-FAILING set `_audit/INSTRUMENTS.md` requires. Each one drives
the classifier over a MUTATED SANDBOX COPY of the census; no committed file is ever
written. Three properties they exist to defend, each learned the hard way in this repo:

**1. THE ASSERTION IS PER FILE, NEVER OVER THE UNION.** `test_per_file_...` empties
`network.md` of all 101 write-offs and leaves the other three slices intact. A union
assertion over 309 rows is still satisfied in that state by the other three slices -- so a
slice that stopped being read would look exactly like a slice with nothing to say. It must
go red, and it does.

**2. A MUTATION THAT CHANGED BYTES IS NOT A MUTATION THAT ACHIEVED ITS INTENT.** Every
mutation here asserts its POSTCONDITION, not merely that the text differs. The first
version of this harness rewrote state cells with one regex and left 12 of network.md's 101
write-offs standing -- because the corpus also writes `EXCLUDED-RULED (R11)` and
`**COVERED-CANNOT-DELIVER**`. The control then passed CORRECTLY, and it was one step from
being recorded as a control that cannot fail. `gapify` now goes through the shipped
vocabulary, and `test_per_file_...` asserts the slice actually reached zero first.

**3. A NEEDLE THAT NEVER FIRES AND A FACT THAT IS NEVER TRUE LOOK IDENTICAL IN A COUNT.**
Ten of the classifier's signals fire zero times on the real corpus, including the whole
PROCESS-FACT class. `test_no_signal_is_a_dead_needle` feeds every zero-firing pattern a
synthetic positive, so a reported zero is a measurement rather than a broken regex.

WHAT IS DELIBERATELY NOT TESTED HERE. The exact per-kind counts are not pinned. They move
whenever the census is edited, which is constantly and by design, and a test that fails on
every legitimate census edit gets suppressed rather than read. What is pinned is that every
write-off row in every slice resolves to SOME kind, that the hand adjudications stay
pinned to evidence that still exists, and that the controls can fail.
"""
from __future__ import annotations

import pathlib
import shutil
import sys
import tempfile

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import count_census_states as ccs            # noqa: E402
import classify_writeoff_reasons as cw       # noqa: E402

WRITEOFF_STATES = ("EXCLUDED-RULED", "XR", "MEASURED-ABSENT",
                   "COVERED-CANNOT-DELIVER", "CANNOT-DELIVER")


@pytest.fixture
def real_census():
    """Restore the module-level corpus pointer whatever a test does to it."""
    original = ccs.CENSUS
    yield original
    ccs.CENSUS = original


def sandbox_census() -> pathlib.Path:
    d = pathlib.Path(tempfile.mkdtemp(prefix="kindsguard_"))
    shutil.copytree(ccs.CENSUS, d / "_census")
    return d / "_census"


def gapify(text: str) -> str:
    """Rewrite every recognised non-GAP state token in every table row to GAP.

    Goes through `ccs.STATES`, the shipped vocabulary, rather than a hand-written
    alternation -- see property 2 in the module docstring.
    """
    out = []
    for line in text.splitlines(keepends=True):
        if line.startswith("|"):
            cells = ccs.cells(line)
            new = []
            for i, cell in enumerate(cells):
                bare = cell.replace("`", "").replace("*", "").strip()
                head = bare.split(" ")[0]
                if i > 0 and head in ccs.STATES and head != "GAP":
                    cell = cell.replace(head, "GAP")
                new.append(cell)
            line = "| " + " | ".join(new) + " |" + chr(10)
        out.append(line)
    return "".join(out)


def build_at(census_dir: pathlib.Path):
    ccs.CENSUS = census_dir
    return cw.build(None)


def check_at(census_dir: pathlib.Path) -> tuple[int, str]:
    """(exit code, stdout) of `--check`.

    `build()` returns only the `problems` list; the PER-FILE and EMPTY-CORPUS controls
    live in `main()`. Asserting against `build()` and calling the per-file control green
    was a real defect in the first harness.
    """
    import contextlib
    import io

    ccs.CENSUS = census_dir
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cw.main(["--check"])
    return rc, buf.getvalue()


# ---------------------------------------------------------------- the real tree


def test_baseline_is_clean_and_every_row_carries_a_kind(real_census):
    rows, wo, dialects, stated, rulings, problems, adj = build_at(real_census)
    assert wo, "an empty corpus is a loud event, never a silent pass"
    assert not problems, f"unresolved pointers or stale adjudications: {problems[:3]}"
    assert not dialects, f"dialect state cells: {dialects[:3]}"
    for letter, name in ccs.SLICES.items():
        sub = [r for r in wo if r.letter == letter]
        assert sub, f"{name} contributed zero write-off rows"
        unkinded = [r.key for r in sub if not r.kind]
        assert not unkinded, f"{name}: rows with no kind: {unkinded[:5]}"


def test_every_ruling_section_is_adjudicated(real_census):
    """72 rows inherit from 11 rulings, so an unadjudicated ruling silently unclassifies
    a whole block. A keyword sweep over a 2,735-character ruling body was measured to
    produce a three-kind verdict carrying no information, which is why these are hand
    judgements pinned to quotes."""
    _, _, _, _, rulings, problems, adj = build_at(real_census)
    adjudicated = {a.key for a in adj if a.key.startswith("RULING ")}
    for code in rulings:
        assert f"RULING {code}" in adjudicated, f"{code} has no adjudication"
    assert not [p for p in problems if "ADJUDICATION" in p]


def test_no_signal_is_a_dead_needle(real_census):
    """Every signal that fires zero times on the corpus must still match a synthetic
    positive. Otherwise a reported zero measures the regex, not the census."""
    _, wo, _, _, _, _, _ = build_at(real_census)
    synthetic = {
        "not-built": "the reader was deliberately not built",
        "structurally": "structurally unable to complete",
        "name-freedom": "the name-freedom ruling forbids it",
        "cannot-verify-send": 'send_message cannot report "sent" today',
        "never-actioned": "NEVER ACTIONED on this account",
        "unverifiable-account": "IS UNVERIFIABLE ON THIS ACCOUNT",
        "his-locale": "blocked by his locale",
        "geography": "a US-only overlay in the United States",
        "served-by-skill": "served by the skill",
        "separate-product": "opens as a separate LinkedIn Learning product",
        "live-process": "measured off the live server, which is 58 commits stale",
        "retired-by-linkedin": "LinkedIn retired the product",
        "not-on-allowlist": "the address is not on the allowlist",
        "http-404": "the article is 404",
        "operator-must-act": "the operator names one",
        "mutation-verb": "on the mutation-verb denylist",
        "writespec": "needs a WriteSpec",
        "sibling-slice": "owned by the messaging slice",
    }
    dead = []
    for label, kind, pat in cw.SIGNALS:
        if any(pat.search(r.reason) for r in wo):
            continue
        probe = synthetic.get(label)
        if probe is None:
            dead.append(f"{label} fires zero times and has no synthetic positive")
        elif not pat.search(probe):
            dead.append(f"{label} did not match its own positive {probe!r}")
    assert not dead, "DEAD NEEDLES: " + "; ".join(dead)


def test_process_fact_zero_is_a_real_zero(real_census):
    """No census reason rests on a refusal read off a RUNNING server. That matters -- a
    running server holds the allowlist it booted with, and this repo has measured a live
    one answering while the tree had moved on. The zero is asserted together with the
    needle's liveness so it cannot quietly become a dead-regex zero."""
    _, wo, _, _, _, _, _ = build_at(real_census)
    pat = next(p for label, _k, p in cw.SIGNALS if label == "live-process")
    assert pat.search("measured off the live server, which is 58 commits stale")
    assert not [r.key for r in wo if "PROCESS-FACT" in r.kind]


# ---------------------------------------------------------------- shown failing


def test_per_file_control_fails_when_one_slice_loses_every_writeoff(real_census):
    """THE UNION/PER-FILE PROOF. Empty network.md alone; the other three slices still
    hold 208 write-off rows, so a union assertion would pass."""
    census = sandbox_census()
    target = census / "network.md"
    before = target.read_text(encoding="utf-8", errors="replace")
    target.write_text(gapify(before), encoding="utf-8")

    _, wo, _, _, _, _, _ = build_at(census)
    per = {L: sum(1 for r in wo if r.letter == L) for L in ccs.SLICES}
    # POSTCONDITION FIRST: if the mutation did not reach zero, the run proves nothing.
    assert per["N"] == 0, f"mutation did not achieve its intent: {per}"
    assert per["J"] and per["P"] and per["M"], "other slices must be untouched"
    assert sum(per.values()) > 100, "a union assertion would still be satisfied here"

    rc, out = check_at(census)
    assert rc == 1
    assert "network.md contributed ZERO write-off rows" in out


def test_empty_corpus_is_loud(real_census):
    census = sandbox_census()
    for name in ccs.SLICES.values():
        p = census / name
        p.write_text(gapify(p.read_text(encoding="utf-8", errors="replace")),
                     encoding="utf-8")
    _, wo, _, _, _, _, _ = build_at(census)
    assert len(wo) == 0, "mutation did not achieve its intent"
    rc, out = check_at(census)
    assert rc == 1
    assert "loud event" in out


def test_a_pinned_adjudication_fails_when_its_evidence_moves(real_census):
    """The anti-staleness mechanism. Reword R2's pinned quote and the hand judgement must
    go red rather than keep applying to text that no longer says what it said."""
    census = sandbox_census()
    target = census / "network.md"
    before = target.read_text(encoding="utf-8", errors="replace")
    after = before.replace(
        "catching a read that has nothing to do with inviting",
        "catching a read that has NOTHING WHATSOEVER to do with inviting")
    assert after != before, "mutation did not land"
    target.write_text(after, encoding="utf-8")

    _, _, _, _, _, problems, _ = build_at(census)
    assert any("RULING R2" in p and "NO LONGER PRESENT" in p for p in problems), problems


def test_an_adjudication_on_a_row_that_left_writeoff_is_reported_moot(real_census):
    census = sandbox_census()
    target = census / "jobs.md"
    before = target.read_text(encoding="utf-8", errors="replace")
    after = before.replace(
        "| 134 | Practice by reading and typing responses instead | a8336402 "
        "| EXCLUDED-RULED |",
        "| 134 | Practice by reading and typing responses instead | a8336402 | GAP |")
    assert after != before, "mutation did not land"
    target.write_text(after, encoding="utf-8")

    _, _, _, _, _, problems, _ = build_at(census)
    assert any("J 134" in p for p in problems), problems


def test_a_deleted_ruling_section_is_reported(real_census):
    import re as _re
    census = sandbox_census()
    target = census / "network.md"
    before = target.read_text(encoding="utf-8", errors="replace")
    m = _re.search(r"\n### R5 --.*?(?=\n### )", before, _re.S)
    assert m, "R5 section not found"
    after = before[:m.start()] + "\n" + before[m.end():]
    target.write_text(after, encoding="utf-8")

    _, _, _, _, _, problems, _ = build_at(census)
    assert any("R5" in p for p in problems), problems


def test_a_cosmetic_edit_changes_nothing(real_census):
    """CALIBRATION. A harness where every mutation goes red is not discriminating."""
    rows, wo, _, _, _, _, _ = build_at(real_census)
    baseline = {r.key: r.kind for r in wo}

    census = sandbox_census()
    target = census / "jobs.md"
    before = target.read_text(encoding="utf-8", errors="replace")
    after = before.replace(
        "| 134 | Practice by reading and typing responses instead |",
        "| 134 | Practice by reading and typing responses instead  |")
    assert after != before, "mutation did not land"
    target.write_text(after, encoding="utf-8")

    _, wo2, _, _, _, problems, _ = build_at(census)
    assert not problems
    assert {r.key: r.kind for r in wo2} == baseline


def test_backreference_chains_repoint_silently_when_a_row_is_inserted(real_census):
    """NOT A BUG IN THE CLASSIFIER -- A MEASUREMENT OF THE CENSUS.

    46 reason cells are the word `same`, resolving BY POSITION to the row above. Planting
    one row re-points every dependent beneath it, changing their classification, with no
    error and no warning. This test pins that the fragility is real, so that if the census
    ever gains a stable backreference (an explicit row id instead of `same`) this test
    fails and somebody deletes it deliberately.
    """
    census = sandbox_census()
    target = census / "profile.md"
    before = target.read_text(encoding="utf-8", errors="replace")
    lines = before.splitlines(keepends=True)
    out = []
    for line in lines:
        out.append(line)
        if line.startswith("| D14 |"):
            out.append("| D14b | A PLANTED ROW | W | EXCLUDED-RULED | "
                       "a completely different argument about the mobile app only |"
                       + chr(10))
    after = "".join(out)
    assert after != before, "mutation did not land"
    target.write_text(after, encoding="utf-8")

    _, wo, _, _, _, problems, _ = build_at(census)
    by = {r.key: r for r in wo}
    repointed = [k for k in ("P D15", "P D16", "P D17")
                 if k in by and by[k].backref_donor == "P D14b"]
    assert len(repointed) == 3, (
        f"expected all three dependents to re-point to the planted row, got {repointed}")
    assert not problems, "and it happens with no complaint at all, which is the finding"
