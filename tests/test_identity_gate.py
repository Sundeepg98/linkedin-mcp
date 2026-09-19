"""``scripts/identity_gate.py``, shown blocking and shown passing.

THE PROPERTY WORTH TESTING IS NOT THE SHAPES. Those belong to
``tests/test_no_committed_identity.py`` and are tested there; the gate imports
them rather than restating them, and :func:`test_the_gate_owns_no_shape_of_its
_own` pins that. What this module tests is the thing the gate adds:

    **it reads the INDEX, which is neither the working tree nor the last
    commit, and which is the only thing a commit actually writes.**

That distinction is not academic. The four exposures of 2026-09-04 were found
by an agent reporting them as "untracked or working-copy only, so nothing is in
history" -- and all of them were in history, two committed within the hour. The
tree and the index disagree constantly in a repository with several writers,
and every instrument here before this one read the tree.

WHY THE PLANTS ARE LITERALS AND ARE DECLARED rather than assembled at runtime:
assembling them would hide them from the shape guard that sweeps this file,
and a scanner blinded to this file's deliberate values is blinded to a REAL
value pasted into it later. That reasoning is not new here -- it is the note
DECLARED_PLANTS already carries for two other modules.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
GATE_PATH = REPO / "scripts" / "identity_gate.py"

#: An ordinary path -- NOT one of the three the exact-value sweep exempts, and
#: not one DECLARED_PLANTS names. A control planted at an exempt path passes
#: and proves nothing, which is a mistake this repository has already made.
ORDINARY = "linkedin_server/some_ordinary_module.py"


def _gate():
    spec = importlib.util.spec_from_file_location("_identity_gate", GATE_PATH)
    assert spec is not None and spec.loader is not None, GATE_PATH
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gate = _gate()


@pytest.mark.parametrize(
    "shape, planted",
    [
        ("member token", "ACoAAQq1Ww2Ee3Rr4Tt5Yy6Uu7Ii8Oo9Pp0Aa1Ss"),
        ("urn id", "urn:li:ugcPost:7522222222222222222"),
        ("opaque urn", "urn:li:digitalmediaAsset:D5622AQKp7Lm3Nb8Vc"),
        # A grouped mobile, and deliberately not the one SYNTHETIC_PHONES
        # allows: a control built from an allowlisted value cannot fail.
        ("phone", "reachable on 98123 45678 most evenings"),
    ],
)
def test_the_gate_blocks_each_shape(shape, planted):
    """CAN-IT-FAIL, one class at a time, at an ordinary path."""
    found = gate.shape_findings(ORDINARY, planted)
    assert shape in {name for name, _ in found}, (shape, found)


def test_the_gate_passes_an_ordinary_blob():
    """THE CONTROL FOR THE CONTROLS. Without it, a gate that blocks everything
    would satisfy every test above and be useless in exactly the way that gets
    a gate uninstalled on its first day."""
    clean = "def add(a, b):\n    return a + b\n"
    assert gate.shape_findings(ORDINARY, clean) == []


def test_the_gate_honours_a_declared_plant():
    """A file allowed N of a shape must not be blocked for its Nth.

    Otherwise the gate contradicts the suite: the guard would be green and the
    commit refused, and whoever hit that would remove the gate rather than the
    value. Driven on a real DECLARED_PLANTS entry so a change to that table
    reaches this test.
    """
    from tests.test_no_committed_identity import DECLARED_PLANTS

    rel, name = "tests/test_writes_nine.py", "urn id"
    assert DECLARED_PLANTS.get((rel, name)) == 1, DECLARED_PLANTS.get((rel, name))
    blob = 'ITEM = "urn:li:ugcPost:7533333333333333333"\n'
    assert [n for n, _ in gate.shape_findings(rel, blob) if n == name] == []
    # ...and a SECOND one in the same file is still blocked, which is what
    # pinning by count buys over skipping the file.
    assert [n for n, _ in gate.shape_findings(rel, blob + blob) if n == name] == [name]


def test_the_gate_reads_the_index_and_not_the_working_tree(monkeypatch):
    """THE WHOLE REASON THIS SCRIPT EXISTS, asserted rather than described.

    ``git add`` a file and then edit the value back out and the working tree is
    clean while the commit still carries it. Every instrument in this repo
    before the gate read the tree, so every one of them would call that safe.
    """
    staged = 'TARGET = "urn:li:ugcPost:7544444444444444444"\n'

    def fake_git(*args):
        class R:
            returncode = 0
            stderr = ""
            stdout = ""
        r = R()
        if args[:2] == ("diff", "--cached"):
            r.stdout = ORDINARY + "\n"
        elif args[0] == "show":
            assert args[1] == f":{ORDINARY}", args
            r.stdout = staged
        return r

    monkeypatch.setattr(gate, "_git", fake_git)
    assert gate.staged_paths() == [ORDINARY]
    body = gate.staged_blob(ORDINARY)
    assert body == staged
    assert [n for n, _ in gate.shape_findings(ORDINARY, body)] == ["urn id"]


def test_the_gate_never_prints_the_identifier():
    """A pre-commit hook prints to a terminal, a scrollback and often a log."""
    value = "ACoAAQq1Ww2Ee3Rr4Tt5Yy6Uu7Ii8Oo9Pp0Aa1Ss"
    rendered = gate.redact(f'MEMBER = "{value}"')
    assert value not in rendered
    assert set(rendered) <= set("x=\"' ")


def test_the_gate_owns_no_shape_of_its_own():
    """One source of truth, or the gate and the guard drift apart.

    The drift would present as this passing while the suite is red -- which is
    the exact state the gate was written to end, so a second copy of the rules
    would reproduce the defect inside the fix.
    """
    source = GATE_PATH.read_text(encoding="ascii")
    assert "from tests.test_no_committed_identity import" in source
    assert "hits_in" in source and "DECLARED_PLANTS" in source
    assert "ACoAA" not in source, "the gate restated a shape instead of importing it"
    assert "urn:li" not in source, "the gate restated a shape instead of importing it"


def test_the_gate_is_not_installed_silently():
    """Installing a pre-commit hook gates EVERY writer in a shared tree.

    This repository runs many agents against one working copy, and the standing
    ruling is that commits are wanted. So the gate ships as a script plus an
    install line in its own docstring, and the install is the lead's call. This
    test pins the script's existence, not the hook's -- if it ever asserted the
    hook, a fresh clone would fail for lacking a file git does not carry.
    """
    assert GATE_PATH.exists(), GATE_PATH
    source = GATE_PATH.read_text(encoding="ascii")
    assert ".git/hooks/pre-commit" in source, "the install line is the handover"
