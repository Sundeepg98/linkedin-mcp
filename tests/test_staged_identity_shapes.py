"""The fast half of the identity guard, SHOWN FAILING before anything trusts it.

WHY THIS FILE IS THE PRICE OF ADMISSION.

``scripts/staged_identity_shapes.py`` exists so that
``scripts/impact_gate.py`` can stop sweeping 545 files on every commit to ask
a question about the two or three the commit writes. That substitution is only
safe if the fast half actually catches what the slow half catches, and **an
incremental guard is trivially green on an empty stage** -- read nothing, find
nothing, exit 0. A check that cannot fail certifies nothing, and a register of
such checks manufactures confidence at scale. So every assertion below that
matters is a RED one: a planted shape, a planted disagreement, a planted
decline.

WHAT IS PLANTED AND WHERE. Every identifier shape used here is ASSEMBLED AT
RUNTIME from fragments that are individually harmless, and written into a
THROWAWAY GIT REPOSITORY under ``tmp_path``. Nothing below is a literal
identifier in a tracked file, which matters because the guard this file is
about would flag one, correctly.

THE FOUR THINGS THAT COULD GO WRONG, and the control for each:

  * **it does not see the shape at all** -- three planted shapes, each first
    confirmed visible to the SLOW half (``hits_in``) so a green fast half
    cannot be excused by "the property does not fire on that either";
  * **it reads the WORKING TREE instead of the INDEX** -- the exact mistake
    this repository already recorded, where a clean tree said nothing about
    what a commit carried. Planted directly: the index is dirty, the worktree
    is clean, and a reader of the wrong one goes green;
  * **it silently answers when it cannot** -- the property module in the
    change set must produce exit 2, never 0. That is the set-shaped residue of
    an otherwise per-file property: editing ``DECLARED_PLANTS`` changes what
    the question MEANS for files this run never reads;
  * **it prints the value** -- the whole point is keeping identifiers out of
    terminals, transcripts and CI logs, and a refusal is exactly where a
    careless implementation leaks one.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SIBLING = REPO / "scripts" / "staged_identity_shapes.py"

#: Shapes built from fragments. Each fragment on its own matches nothing: the
#: member-token rule needs ten characters after the prefix, the slug rule needs
#: three after ``/in/``, and the urn rule needs six digits.
PLANTS = {
    "member token": "ACoAA" + "B" * 14,
    "linkedin slug": "https://www.linkedin.com" + "/in/" + "qwertyuiopas",
    "urn id": "urn:li:activity" + ":" + "7" * 12,
}


def _property():
    """The SLOW half, imported the same way the script imports it."""
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location(
        "_identity_property_control", REPO / "tests" / "test_no_committed_identity.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["_identity_property_control"] = module
    spec.loader.exec_module(module)
    return module


def _repo(tmp_path: Path) -> Path:
    """A throwaway git repository. Nothing here touches the real one."""
    subprocess.run(["git", "init", "-q"], cwd=str(tmp_path), check=True,
                   capture_output=True)
    for key, value in (("user.email", "nobody@example.invalid"),
                       ("user.name", "nobody")):
        subprocess.run(["git", "config", key, value], cwd=str(tmp_path),
                       check=True, capture_output=True)
    return tmp_path


def _run(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SIBLING), "--repo", str(repo)],
        capture_output=True, text=True, errors="replace",
    )


# ---------------------------------------------------------------------------
# 1. It fires. Three shapes, each shown visible to the slow half first.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("shape", sorted(PLANTS))
def test_the_slow_half_sees_the_plant(shape):
    """THE PRECONDITION FOR EVERY TEST BELOW IT.

    If the property does not fire on a plant, the fast half going green proves
    nothing about the fast half. Assert the slow half first, always.
    """
    found = _property().hits_in("landed on " + PLANTS[shape] + "\n")
    assert any(name == shape for name, _value in found), (
        f"the whole-tree property did not flag a planted {shape}; this "
        f"control is measuring the plant, not the guard. Got {found}."
    )


@pytest.mark.parametrize("shape", sorted(PLANTS))
def test_the_fast_half_refuses_the_same_plant(tmp_path, shape):
    """The substitution's whole warrant, one shape at a time."""
    repo = _repo(tmp_path)
    (repo / "notes.md").write_text("landed on " + PLANTS[shape] + "\n",
                                   encoding="utf-8")
    subprocess.run(["git", "add", "notes.md"], cwd=str(repo), check=True,
                   capture_output=True)
    proc = _run(repo)
    assert proc.returncode == 1, (
        f"a staged file carrying a {shape} did not produce a refusal "
        f"(exit {proc.returncode}). stderr: {proc.stderr[-400:]}"
    )
    assert shape in proc.stderr, (
        f"the refusal did not name the class it found. stderr: {proc.stderr[-400:]}"
    )


@pytest.mark.parametrize("shape", sorted(PLANTS))
def test_a_refusal_never_prints_the_identifier(tmp_path, shape):
    """A refusal reaches terminals, transcripts and CI logs. It reports the
    SHAPE and a masked span, never the value."""
    repo = _repo(tmp_path)
    (repo / "notes.md").write_text("landed on " + PLANTS[shape] + "\n",
                                   encoding="utf-8")
    subprocess.run(["git", "add", "notes.md"], cwd=str(repo), check=True,
                   capture_output=True)
    proc = _run(repo)
    assert proc.returncode == 1
    assert PLANTS[shape] not in proc.stderr
    assert PLANTS[shape] not in proc.stdout


# ---------------------------------------------------------------------------
# 2. It reads the INDEX. This repo has already paid for the other answer.
# ---------------------------------------------------------------------------

def test_it_reads_the_staged_bytes_and_not_the_working_tree(tmp_path):
    """**THE DANGEROUS DIRECTION, PLANTED.**

    The index carries the shape and the working tree does not. A check that
    read the tree would go green while the blob about to be written carries an
    identifier -- which is precisely the failure
    ``scripts/pre_commit_identity_gate.py`` was written for: *a clean tree says
    nothing about what a commit contains.*
    """
    repo = _repo(tmp_path)
    victim = repo / "notes.md"
    victim.write_text("landed on " + PLANTS["member token"] + "\n",
                      encoding="utf-8")
    subprocess.run(["git", "add", "notes.md"], cwd=str(repo), check=True,
                   capture_output=True)
    # Now make the WORKING TREE innocent. The index still holds the shape.
    victim.write_text("nothing to see here\n", encoding="utf-8")

    proc = _run(repo)
    assert proc.returncode == 1, (
        "the staged blob carries an identifier and the working copy does not; "
        "exiting 0 here means this script reads the wrong bytes. stderr: "
        + proc.stderr[-400:]
    )


def test_an_untracked_file_is_in_the_change_set(tmp_path):
    """UNTRACKED FILES HAVE NO BASE CASE IN CI AND CANNOT GET ONE.

    CI clones a commit, so it never sees an untracked file and never will.
    ``committable_files()`` was widened on 2026-09-01 because one carrying a
    real activity id sat through a green suite. If this script dropped them,
    that widening would be checked by nothing at all.
    """
    repo = _repo(tmp_path)
    (repo / "stray.md").write_text("landed on " + PLANTS["urn id"] + "\n",
                                   encoding="utf-8")
    proc = _run(repo)
    assert proc.returncode == 1, (
        "an untracked file carrying an identifier was not examined. stderr: "
        + proc.stderr[-400:]
    )


# ---------------------------------------------------------------------------
# 3. It declines rather than guessing.
# ---------------------------------------------------------------------------

def test_editing_the_property_forces_the_slow_path(tmp_path):
    """THE SET-SHAPED RESIDUE, COMPUTED FROM THE DIFF RATHER THAN ASSUMED AWAY.

    ``DECLARED_PLANTS`` is a per-file allowance table and ``SHAPES`` is the
    rule set. A commit that edits either has changed what the question MEANS,
    so a staged-set answer stops being evidence about the files it did not
    read. Exit 2, never 0.
    """
    repo = _repo(tmp_path)
    (repo / "tests").mkdir()
    (repo / "tests" / "test_no_committed_identity.py").write_text(
        "# edited\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True,
                   capture_output=True)
    proc = _run(repo)
    assert proc.returncode == 2, (
        f"editing the property produced exit {proc.returncode}; anything but "
        "2 means the gate would deselect the whole-tree sweep on the one "
        "commit that can invalidate it."
    )


def test_the_gate_restores_the_sweep_when_the_script_cannot_answer():
    """The other end of the same wire, asserted on the GATE.

    A third exit code is worth nothing if the caller treats it as a pass. This
    is the pairing register's escape hatch read back out of
    ``scripts/impact_gate.py`` rather than believed.
    """
    gate = (REPO / "scripts" / "impact_gate.py").read_text(encoding="utf-8")
    assert "_SIBLING_CLEAN" in gate and "fails_open_token" in gate, (
        "impact_gate no longer distinguishes a clean answer from a decline"
    )
    assert "RESTORING its whole-tree sweep" in gate, (
        "impact_gate no longer restores the whole-tree sweep when its fast "
        "half declines, so a decline would read as a pass"
    )


# ---------------------------------------------------------------------------
# 4. An empty change set is loud, and a clean one says what it did not read.
# ---------------------------------------------------------------------------

def test_an_empty_change_set_says_so_rather_than_passing_quietly(tmp_path):
    """AN INCREMENTAL GUARD IS TRIVIALLY GREEN ON AN EMPTY STAGE.

    Exit 0 is correct there -- nothing is being committed -- but a bare pass
    is not, because it is indistinguishable from a guard that ran and found
    the tree clean. Same law as the gate's own empty-impact-set alarm.
    """
    repo = _repo(tmp_path)
    proc = _run(repo)
    assert proc.returncode == 0
    assert "examined 0 files" in proc.stderr, (
        "a run that read nothing printed no such thing. stderr: "
        + proc.stderr[-400:]
    )


def test_a_clean_run_names_what_it_did_not_read(tmp_path):
    """The scope disclaimer is part of the verdict, not a footnote.

    A reader who takes this green for "the tree is clean" has been misled by a
    check that only ever looked at one file.
    """
    repo = _repo(tmp_path)
    (repo / "notes.md").write_text("nothing to see here\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True,
                   capture_output=True)
    proc = _run(repo)
    assert proc.returncode == 0, proc.stderr[-400:]
    assert "1 file(s) examined" in proc.stderr
    assert "were NOT read" in proc.stderr
    assert "CI" in proc.stderr, (
        "the clean message does not name the base case, so the next reader "
        "has no way to learn that deleting the sweep breaks the induction"
    )


def test_the_pairing_register_names_a_script_that_exists():
    """A REGISTER ENTRY POINTING AT NOTHING WOULD DROP A GUARD SILENTLY."""
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location(
        "_gate_control", REPO / "scripts" / "impact_gate.py")
    gate = importlib.util.module_from_spec(spec)
    sys.modules["_gate_control"] = gate
    spec.loader.exec_module(gate)
    assert gate._INCREMENTAL_SIBLINGS, "the register is empty"
    for sweep_file, pairings in gate._INCREMENTAL_SIBLINGS.items():
        assert (REPO / sweep_file).exists(), (
            f"{sweep_file} is registered as having a fast half and does not "
            "exist"
        )
        for pair in pairings:
            assert (REPO / pair.script).exists(), (
                f"{pair.script} is registered as the fast half of "
                f"{pair.node} and is not on disk"
            )
            assert pair.node.startswith(sweep_file + "::"), (
                f"{pair.node} is filed under {sweep_file} and does not belong "
                "to it, so deselecting it would remove a sweep nobody checked"
            )
