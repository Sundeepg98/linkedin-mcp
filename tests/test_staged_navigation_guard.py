"""The fast half of the navigation guard, SHOWN FAILING before anything trusts it.

``scripts/staged_navigation_guard.py`` lets ``scripts/impact_gate.py`` stop
running two rules over 170 files on every commit and run them over the handful
the commit writes. That substitution is worth exactly as much as the evidence
that the fast half fires, so every assertion here that matters is a RED one.

THE PLANTS ARE THE TWIN'S OWN EXEMPLARS, copied verbatim from the synthetic
bodies ``tests/test_navigation_is_never_derived.py`` already feeds its
detector, and each is asserted against the SLOW half first. Inventing a plant
risks measuring the plant; reusing the twin's risks nothing, and if the twin
ever stops flagging one the precondition test says so instead of the fast half
quietly going green.

THE EQUALITY IS TWO-SIDED AND BOTH SIDES ARE PLANTED HERE. The rule fails when
a site is ADDED **and** when a site is FIXED and its declaration left behind.
A fast half that only checked the first would silently permit a "known hole"
note outliving its hole, which this repository has a standing receipt for.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SIBLING = REPO / "scripts" / "staged_navigation_guard.py"

_HEAD = "async def main(page):\n"

#: Verbatim from the twin's own red exemplars.
DERIVED_NAVIGATION = (
    "    landed = await BROWSER.goto(page, SELF_PROFILE_URL)\n"
    "    await BROWSER.goto(page, landed)\n"
)
#: Verbatim from the twin's own green exemplars.
AUTHORED_NAVIGATION = (
    "    landed = await BROWSER.goto(page, SELF_PROFILE_URL)\n"
    "    await BROWSER.goto(page, SELF_PROFILE_URL)\n"
)
TAINTED_OUTPUT = (
    "    landed = await BROWSER.goto(page, SELF_PROFILE_URL)\n"
    "    print(landed)\n"
)


def _property():
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location(
        "_navigation_property_control",
        REPO / "tests" / "test_navigation_is_never_derived.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["_navigation_property_control"] = module
    spec.loader.exec_module(module)
    return module


def _repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q"], cwd=str(tmp_path), check=True,
                   capture_output=True)
    for key, value in (("user.email", "nobody@example.invalid"),
                       ("user.name", "nobody")):
        subprocess.run(["git", "config", key, value], cwd=str(tmp_path),
                       check=True, capture_output=True)
    (tmp_path / "linkedin_server").mkdir()
    (tmp_path / "scripts").mkdir()
    return tmp_path


def _run(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SIBLING), "--repo", str(repo)],
        capture_output=True, text=True, errors="replace",
    )


def _stage(repo: Path, rel: str, body: str) -> None:
    (repo / rel).write_text(_HEAD + body, encoding="utf-8")
    subprocess.run(["git", "add", rel], cwd=str(repo), check=True,
                   capture_output=True)


# ---------------------------------------------------------------------------
# Preconditions: the SLOW half sees the plants. Assert this before anything
# concludes something from the fast half's verdict.
# ---------------------------------------------------------------------------

def test_the_slow_half_flags_the_derived_navigation():
    assert _property().violations(_HEAD + DERIVED_NAVIGATION), (
        "the twin no longer flags its own red exemplar; this control is "
        "measuring the plant rather than the guard"
    )


def test_the_slow_half_flags_the_tainted_output():
    assert _property().output_violations(_HEAD + TAINTED_OUTPUT), (
        "the twin no longer flags its own tainted-output shape"
    )


def test_the_slow_half_stays_green_on_the_authored_navigation():
    """THE OTHER DIRECTION. A detector that flags everything is not one."""
    assert not _property().violations(_HEAD + AUTHORED_NAVIGATION)


# ---------------------------------------------------------------------------
# It fires, in both scanned folders and on both rules.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("folder", ["linkedin_server", "scripts"])
def test_it_refuses_a_staged_derived_navigation(tmp_path, folder):
    repo = _repo(tmp_path)
    _stage(repo, f"{folder}/probe_x.py", DERIVED_NAVIGATION)
    proc = _run(repo)
    assert proc.returncode == 1, (
        f"a staged {folder}/ file navigating a url the browser chose did not "
        f"produce a refusal (exit {proc.returncode}). stderr: "
        f"{proc.stderr[-500:]}"
    )
    assert "derived-navigation" in proc.stderr


def test_it_refuses_a_staged_tainted_output(tmp_path):
    repo = _repo(tmp_path)
    _stage(repo, "linkedin_server/probe_y.py", TAINTED_OUTPUT)
    proc = _run(repo)
    assert proc.returncode == 1, proc.stderr[-500:]
    assert "tainted-output" in proc.stderr


def test_it_stays_green_on_an_authored_navigation(tmp_path):
    """The green direction, so a refusal above means something."""
    repo = _repo(tmp_path)
    _stage(repo, "linkedin_server/probe_z.py", AUTHORED_NAVIGATION)
    proc = _run(repo)
    assert proc.returncode == 0, proc.stderr[-500:]
    assert "1 file(s) examined" in proc.stderr


# ---------------------------------------------------------------------------
# The scope of the twin, matched exactly. More is as wrong as less.
# ---------------------------------------------------------------------------

def test_a_nested_file_is_out_of_scope_because_the_twin_does_not_glob_it(tmp_path):
    """THE TWIN'S GLOB DOES NOT RECURSE.

    ``(REPO / folder).glob("*.py")`` is one level. A fast half that refused a
    nested file would produce refusals its slow half never produces, and a
    disagreement in that direction trains people to bypass the gate just as
    surely as a missed defect trains them to trust it.
    """
    repo = _repo(tmp_path)
    (repo / "linkedin_server" / "sub").mkdir()
    _stage(repo, "linkedin_server/sub/probe.py", DERIVED_NAVIGATION)
    proc = _run(repo)
    assert proc.returncode == 0, (
        "a nested file was refused; the twin does not scan it. stderr: "
        + proc.stderr[-500:]
    )
    assert "examined 0 files" in proc.stderr


def test_a_file_outside_the_scanned_folders_is_out_of_scope(tmp_path):
    repo = _repo(tmp_path)
    (repo / "tests").mkdir()
    _stage(repo, "tests/probe.py", DERIVED_NAVIGATION)
    proc = _run(repo)
    assert proc.returncode == 0, proc.stderr[-500:]


def test_it_declines_when_the_twin_scans_a_different_set():
    """THE DRIFT GUARD, READ BACK OUT OF THE SCRIPT.

    The scanned folders are written down in two places on purpose -- the twin's
    ``SCANNED`` and this script's ``FOLDERS`` -- and the script compares them at
    run time rather than trusting them to stay equal.
    """
    source = SIBLING.read_text(encoding="utf-8")
    assert 'getattr(prop, "SCANNED", ())' in source, (
        "the script no longer checks the twin's scanned set, so the day the "
        "twin widens, the fast half would keep answering about the old set"
    )
    assert tuple(_property().SCANNED) == ("scripts", "linkedin_server"), (
        "the twin's SCANNED changed; scripts/staged_navigation_guard.py's "
        "FOLDERS must change in the same commit"
    )


# ---------------------------------------------------------------------------
# It declines rather than guessing, and it is loud when it read nothing.
# ---------------------------------------------------------------------------

def test_editing_the_property_forces_the_slow_path(tmp_path):
    """Both detectors and both declaration tables live in that one file."""
    repo = _repo(tmp_path)
    (repo / "tests").mkdir()
    (repo / "tests" / "test_navigation_is_never_derived.py").write_text(
        "# edited\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True,
                   capture_output=True)
    proc = _run(repo)
    assert proc.returncode == 2, (
        f"editing the property produced exit {proc.returncode}; anything but "
        "2 means the gate would deselect the whole-tree sweeps on the one "
        "commit that can invalidate them"
    )


def test_an_empty_change_set_says_so_rather_than_passing_quietly(tmp_path):
    repo = _repo(tmp_path)
    proc = _run(repo)
    assert proc.returncode == 0
    assert "examined 0 files" in proc.stderr


def test_it_reads_the_staged_bytes_and_not_the_working_tree(tmp_path):
    """The index carries the violation; the working copy is innocent."""
    repo = _repo(tmp_path)
    _stage(repo, "linkedin_server/probe_w.py", DERIVED_NAVIGATION)
    (repo / "linkedin_server" / "probe_w.py").write_text(
        _HEAD + AUTHORED_NAVIGATION, encoding="utf-8")
    proc = _run(repo)
    assert proc.returncode == 1, (
        "the staged blob navigates a derived url and the working copy does "
        "not; exiting 0 means this script reads the wrong bytes. stderr: "
        + proc.stderr[-500:]
    )
