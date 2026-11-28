"""``scripts/resolve_instruments_order.py`` edits only the INSTRUMENTS.md it is
named, or the one under the git root it is run from, and never the main
checkout's without ``--main-checkout``.

WHY (lane hygiene28, 2026-11-28). Until this lane the tool lived only in the
main checkout's gitignored ``_state/orchestrator-tools/`` and found its file
from its OWN location, ``Path(__file__).resolve().parents[2]``. So whatever
directory an integrator ran it from, it edited the MAIN checkout's
``_audit/INSTRUMENTS.md``, and it took no arguments. The merge notes recorded
that hazard twice (integration 6, 2026-11-27), and every integrator brief had
to repeat the warning by hand.

THE HARNESS IS A REAL REPOSITORY. One temp repository per module: a main
checkout with one commit, and a linked worktree NESTED INSIDE it at
``.claude/worktrees/lane``. That is the layout on the operator's box, where
every worktree's path starts with the main checkout's, so a path prefix cannot
tell a worktree's file from the main checkout's. The tool under test (this
repository's file) is copied into the temp tree in both places it is run from:
the main checkout's ``_state/orchestrator-tools/``, where ``merge_wave.py``
calls it, and the worktree's ``scripts/``. Where the tool is stored must not
change which file it edits. Before each test both INSTRUMENTS.md files are
rewritten from scratch, holding the same conflict.

SHOWN FAILING against the tool as it was: the record of lane hygiene28,
section 2, has the counts.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

TOOL = Path(__file__).resolve().parent.parent / "scripts" / "resolve_instruments_order.py"
INSTRUMENTS = Path("_audit") / "INSTRUMENTS.md"

#: Git variables that move repository discovery away from the directory git is
#: run in. The harness scrubs them so a test never inherits a caller's repo;
#: one test sets GIT_DIR on purpose.
_REDIRECTING = ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                "GIT_OBJECT_DIRECTORY", "GIT_CEILING_DIRECTORIES",
                "GIT_DISCOVERY_ACROSS_FILESYSTEM")

BASE = "# Instruments\n\n## 1. THE FIRST SECTION\n\nbody one\n"
OURS = "## 3. THE THIRD SECTION, OURS\n\nours body\n"
THEIRS = "## 2. THE SECOND SECTION, THEIRS\n\ntheirs body\n"


def conflict(ours: str = OURS, theirs: str = THEIRS) -> str:
    """BASE, then one conflict hunk where both sides APPENDED sections."""
    return BASE + "\n<<<<<<< HEAD\n" + ours + "=======\n" + theirs + ">>>>>>> lane\n"


#: The hunk resolved in section-number order: THEIRS (2) before OURS (3),
#: separated by one blank line.
RESOLVED = BASE + "\n" + THEIRS.rstrip("\n") + "\n\n" + OURS


def _env(**extra: str) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k.upper() not in _REDIRECTING}
    env.update(extra)
    return env


def _git(cwd: Path, *args: str) -> str:
    done = subprocess.run(["git", *args], cwd=str(cwd), env=_env(), check=True,
                          capture_output=True, text=True, errors="replace")
    return done.stdout


def _write(path: Path, text: str) -> None:
    """Exactly these bytes: no newline translation on any platform."""
    path.write_bytes(text.encode("utf-8"))


def _read(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


@pytest.fixture(scope="module")
def built(tmp_path_factory) -> SimpleNamespace:
    root = tmp_path_factory.mktemp("resolver")
    main = root / "main"
    main.mkdir()
    _git(main, "init", "-q")
    _git(main, "config", "user.email", "nobody@example.invalid")
    _git(main, "config", "user.name", "nobody")
    _git(main, "config", "core.autocrlf", "false")
    (main / "_audit").mkdir()
    _write(main / INSTRUMENTS, BASE)
    _write(main / ".gitignore", "_state/\n.claude/\n")
    _git(main, "add", "-A")
    _git(main, "commit", "-q", "-m", "base")
    wt = main / ".claude" / "worktrees" / "lane"
    _git(main, "worktree", "add", "-q", "-b", "lane", str(wt))
    tools = {
        "main-orchestrator-tools": main / "_state" / "orchestrator-tools" / TOOL.name,
        "worktree-scripts": wt / "scripts" / TOOL.name,
    }
    for path in tools.values():
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(TOOL, path)
    other = root / "other"
    other.mkdir()
    _git(other, "init", "-q")
    loose = root / "loose"
    loose.mkdir()
    return SimpleNamespace(root=root, main=main, wt=wt, tools=tools, other=other,
                           loose=loose)


@pytest.fixture
def tree(built) -> SimpleNamespace:
    """Both INSTRUMENTS.md files rewritten from scratch, holding the conflict."""
    for checkout in (built.main, built.wt):
        path = checkout / INSTRUMENTS
        if path.exists():
            path.unlink()
        _write(path, conflict())
    return built


def _run(cwd: Path, tool: Path, *args: str, env: dict[str, str] | None = None):
    return subprocess.run([sys.executable, str(tool), *args], cwd=str(cwd),
                          env=env if env is not None else _env(),
                          capture_output=True, text=True, errors="replace",
                          timeout=120)


def _named(output: str) -> Path:
    """The file the tool says it edits: its one ``target: `` line."""
    lines = [line for line in output.splitlines() if line.startswith("target: ")]
    assert len(lines) == 1, output
    return Path(lines[0][len("target: "):])


# ---------------------------------------------------------------------------
# 1. Which file: the tree it runs in, never the tree it is stored in


@pytest.mark.parametrize("stored", ["main-orchestrator-tools", "worktree-scripts"])
def test_run_from_a_worktree_it_edits_that_worktrees_file_and_names_it(tree, stored):
    done = _run(tree.wt, tree.tools[stored])
    assert done.returncode == 0, done.stdout + done.stderr
    assert _read(tree.wt / INSTRUMENTS) == RESOLVED
    assert _read(tree.main / INSTRUMENTS) == conflict(), (
        "run from a worktree, the tool edited the MAIN checkout's file")
    assert os.path.samefile(_named(done.stdout), tree.wt / INSTRUMENTS), done.stdout


def test_an_explicit_file_is_the_only_file_it_edits(tree):
    loose = tree.loose / "INSTRUMENTS.md"
    _write(loose, conflict())
    done = _run(tree.wt, tree.tools["worktree-scripts"], "--file", str(loose))
    assert done.returncode == 0, done.stdout + done.stderr
    assert _read(loose) == RESOLVED
    assert _read(tree.wt / INSTRUMENTS) == conflict()
    assert _read(tree.main / INSTRUMENTS) == conflict()
    assert os.path.samefile(_named(done.stdout), loose), done.stdout


def test_with_no_file_and_no_git_root_it_refuses(tree):
    done = _run(tree.loose, tree.tools["main-orchestrator-tools"])
    assert done.returncode == 2, done.stdout + done.stderr
    assert "--file" in done.stderr, done.stderr
    assert _read(tree.main / INSTRUMENTS) == conflict()


def test_a_missing_file_is_refused(tree):
    done = _run(tree.wt, tree.tools["worktree-scripts"], "--file",
                str(tree.loose / "absent.md"))
    assert done.returncode == 2, done.stdout + done.stderr
    assert _read(tree.wt / INSTRUMENTS) == conflict()
    assert _read(tree.main / INSTRUMENTS) == conflict()


# ---------------------------------------------------------------------------
# 2. The main checkout's file: refused unless --main-checkout


@pytest.mark.parametrize("stored", ["main-orchestrator-tools", "worktree-scripts"])
def test_run_from_the_main_checkout_it_refuses_without_the_flag(tree, stored):
    done = _run(tree.main, tree.tools[stored])
    assert done.returncode == 2, done.stdout + done.stderr
    assert "--main-checkout" in done.stderr, done.stderr
    assert _read(tree.main / INSTRUMENTS) == conflict()
    assert _read(tree.wt / INSTRUMENTS) == conflict()


def test_naming_the_main_checkouts_file_from_a_worktree_is_refused(tree):
    done = _run(tree.wt, tree.tools["worktree-scripts"], "--file",
                str(tree.main / INSTRUMENTS))
    assert done.returncode == 2, done.stdout + done.stderr
    assert _read(tree.main / INSTRUMENTS) == conflict()
    assert _read(tree.wt / INSTRUMENTS) == conflict()


def test_the_flag_permits_the_main_checkouts_file(tree):
    """Control: the refusals above are the flag's, not a tool that cannot
    resolve. This is merge_wave.py's call: run in the main checkout."""
    done = _run(tree.main, tree.tools["main-orchestrator-tools"], "--main-checkout")
    assert done.returncode == 0, done.stdout + done.stderr
    assert _read(tree.main / INSTRUMENTS) == RESOLVED
    assert _read(tree.wt / INSTRUMENTS) == conflict()
    assert os.path.samefile(_named(done.stdout), tree.main / INSTRUMENTS), done.stdout


def test_a_hardlink_to_the_main_checkouts_file_is_refused(tree):
    """A worktree path can still BE the main checkout's file: a path check
    alone would let the write through the link."""
    linked = tree.wt / INSTRUMENTS
    linked.unlink()
    try:
        os.link(tree.main / INSTRUMENTS, linked)
    except OSError as exc:  # pragma: no cover - a filesystem without hardlinks
        pytest.skip(f"no hardlinks here: {exc}")
    done = _run(tree.wt, tree.tools["worktree-scripts"])
    assert done.returncode == 2, done.stdout + done.stderr
    assert _read(tree.main / INSTRUMENTS) == conflict()


def _link_directory(link: Path, target: Path) -> None:
    """A directory link: a symlink, or on Windows without the privilege for
    one, a junction (which needs none)."""
    try:
        os.symlink(target, link, target_is_directory=True)
        return
    except OSError as exc:
        if os.name != "nt":  # pragma: no cover
            pytest.skip(f"no directory symlinks here: {exc}")
    import _winapi  # Windows only

    try:
        _winapi.CreateJunction(str(target), str(link))
    except OSError as exc:  # pragma: no cover
        pytest.skip(f"no junctions here: {exc}")


def _remove_directory_link(link: Path) -> None:
    """The link only, never what it points at: on Windows a junction and a
    directory symlink both go with rmdir; on POSIX a symlink is unlinked."""
    if os.name == "nt":
        os.rmdir(link)
    else:
        link.unlink()


@pytest.mark.parametrize("placed", ["inside-the-worktree", "outside-any-repository"])
def test_a_link_into_the_main_checkout_is_refused(tree, placed):
    """A path that leads, through a directory link, to ANOTHER file of the
    main checkout, so the identity check against the main INSTRUMENTS.md
    cannot catch it.

    Inside the worktree, git places it whichever way it is asked, because git
    runs from the directory's physical path. OUTSIDE any repository there is
    no ``.git`` above the link at all, so a tool that did not resolve the link
    first would call the file "in no checkout" and write through it."""
    other = tree.main / "_audit" / "OTHER.md"
    _write(other, conflict())
    home = tree.wt if placed == "inside-the-worktree" else tree.loose
    link = home / "linked-audit"
    _link_directory(link, tree.main / "_audit")
    try:
        done = _run(tree.wt, tree.tools["worktree-scripts"], "--file",
                    str(link / "OTHER.md"))
        assert done.returncode == 2, done.stdout + done.stderr
        assert _read(other) == conflict()
    finally:
        _remove_directory_link(link)
        other.unlink()
    assert (tree.main / INSTRUMENTS).exists(), "removing the link removed its target"


def test_a_file_git_cannot_place_is_refused(tree):
    """A ``.git`` above the file that git cannot read: the tool cannot tell
    whether this is the main checkout, so it fails closed."""
    broken = tree.loose / "broken"
    broken.mkdir(exist_ok=True)
    _write(broken / ".git", "gitdir: ./no-such-directory\n")
    target = broken / "INSTRUMENTS.md"
    _write(target, conflict())
    done = _run(tree.wt, tree.tools["worktree-scripts"], "--file", str(target))
    assert done.returncode == 2, done.stdout + done.stderr
    assert "--main-checkout" in done.stderr, done.stderr
    assert _read(target) == conflict()


def test_a_redirecting_git_environment_cannot_hide_the_main_checkout(tree):
    """GIT_DIR names another repository, the way a hook's environment names
    its own. Git asked with it would place the main checkout's file in that
    repository; the tool asks git with it removed."""
    done = _run(tree.wt, tree.tools["worktree-scripts"], "--file",
                str(tree.main / INSTRUMENTS),
                env=_env(GIT_DIR=str(tree.other / ".git")))
    assert done.returncode == 2, done.stdout + done.stderr
    assert _read(tree.main / INSTRUMENTS) == conflict()


# ---------------------------------------------------------------------------
# 3. What it did before, kept


@pytest.mark.parametrize("hunks", [0, 2])
def test_not_exactly_one_hunk_is_refused_and_nothing_is_written(tree, hunks):
    text = BASE if hunks == 0 else conflict() + "\n" + conflict()[len(BASE):]
    _write(tree.wt / INSTRUMENTS, text)
    done = _run(tree.wt, tree.tools["worktree-scripts"])
    assert done.returncode == 1, done.stdout + done.stderr
    assert "hunk" in done.stderr, done.stderr
    assert _read(tree.wt / INSTRUMENTS) == text
    assert _read(tree.main / INSTRUMENTS) == conflict()


def test_a_block_with_no_numbered_heading_is_refused_and_nothing_is_written(tree):
    text = conflict(theirs="a paragraph and no heading\n")
    _write(tree.wt / INSTRUMENTS, text)
    done = _run(tree.wt, tree.tools["worktree-scripts"])
    assert done.returncode == 1, done.stdout + done.stderr
    assert _read(tree.wt / INSTRUMENTS) == text
    assert _read(tree.main / INSTRUMENTS) == conflict()


def test_a_crlf_checkout_is_resolved(tree):
    """core.autocrlf=true writes every line CRLF into a Windows checkout."""
    _write(tree.wt / INSTRUMENTS, conflict().replace("\n", "\r\n"))
    done = _run(tree.wt, tree.tools["worktree-scripts"])
    assert done.returncode == 0, done.stdout + done.stderr
    assert _read(tree.wt / INSTRUMENTS) == RESOLVED
    assert _read(tree.main / INSTRUMENTS) == conflict()
