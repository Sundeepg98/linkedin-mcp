"""Where a file lives when the checkout you are standing in is a WORKTREE.

THE BUG THIS MODULE EXISTS FOR, stated once. Every script and test in this
repository resolves its paths as ``Path(__file__).resolve().parents[1]``. That
is correct in a clone and WRONG IN A LINKED WORKTREE for one specific class of
file: **the ones that are gitignored.** A worktree is populated by git from the
index, and git does not carry ignored files into it, so an ignored file that
exists in the main checkout simply is not there.

For almost everything that is harmless. For ``_audit/_sanitisation_key.json``
it is not, because that file is the wordlist for the EXACT-VALUE half of the
identity guard -- the only half that can catch a real name, city, employer or
campus, since nothing structural distinguishes those from English. Absent
wordlist means:

    tests/test_no_committed_identity.py::test_the_exact_value_sweep_actually_runs
    SKIPPED -- the shape half ran, the exact-value half did not

and ``scripts/pre_commit_identity_gate.py`` prints ``identity wordlist absent
(it is gitignored); ALLOWING``.

THE DECLARATION IN ``scripts/ci_expected_skips.json`` SAYS THAT SKIP IS
STRUCTURAL because the key "is absent from every clone and this test skips on
every machine but the operator's". That reasoning is right about clones and
does not cover the case that now matters: **a worktree OF the operator's
machine.** The key is fifty metres away on the same disk, and the guard runs
blind anyway. Every agent in this fleet works in a worktree, so in practice the
exact-value sweep had stopped running for everyone except a human sitting in
the main checkout.

THE FIX IS THE ONE THE PRE-COMMIT HOOK ALREADY USES. On 2026-09-19 that hook
was repaired for the identical reason -- it resolved ``./venv/Scripts/python.exe``
against the cwd, and no worktree has a venv -- by asking git where the real
checkout is:

    git rev-parse --git-common-dir

From inside a linked worktree that resolves to the MAIN repository's ``.git``,
so its parent is the checkout that owns the ignored files. From a normal clone
it resolves to ``.git`` right here and the parent is this repo, so behaviour is
UNCHANGED on CI and in every fresh clone. That property is the reason this is
safe, and :func:`main_checkout` is written so it can be asserted rather than
believed.

WHAT THIS DOES NOT DO: it does not widen, narrow or otherwise touch the swept
set. It changes only where one gitignored wordlist is looked for. The direction
of the change is strictly toward MORE checking -- a guard that was skipping now
runs -- which is the only direction a change to this subsystem is allowed to
move without an argument.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

#: The gitignored de-anonymisation key, by its repo-relative path.
KEY_RELATIVE = Path("_audit") / "_sanitisation_key.json"


def main_checkout(start: Path) -> Path:
    """The root of the MAIN checkout, even when ``start`` is a worktree.

    Returns ``start`` unchanged whenever git cannot answer -- no git on PATH,
    not a repository, a timeout. A path helper that raises would convert a
    missing tool into a failing guard, and a guard that fails for
    infrastructure reasons is the one people learn to bypass.
    """
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=str(start),
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return start
    if proc.returncode != 0:
        return start
    common = proc.stdout.strip()
    if not common:
        return start
    path = Path(common)
    if not path.is_absolute():
        path = (start / path).resolve()
    parent = path.parent
    return parent if parent.is_dir() else start


def in_linked_worktree(start: Path) -> bool:
    """True when ``start`` is a linked worktree rather than the main checkout.

    Measured by asking git for both directories and comparing them, which is
    how git itself distinguishes the two: in a linked worktree ``--git-dir`` is
    ``<main>/.git/worktrees/<name>`` while ``--git-common-dir`` is ``<main>/.git``.
    """
    try:
        one = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=str(start), capture_output=True, text=True, timeout=15,
        )
        two = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=str(start), capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    if one.returncode != 0 or two.returncode != 0:
        return False
    return Path(one.stdout.strip()).resolve() != Path(two.stdout.strip()).resolve()


def sanitisation_key_path(repo: Path) -> Path:
    """Where the de-anonymisation wordlist actually is, worktree or not.

    THE LOCAL COPY WINS. A worktree that has its own key -- somebody put one
    there deliberately -- is answered with its own, never silently overridden
    by the main checkout's. Only when there is no local copy does this reach
    across, which is exactly the worktree case.

    When neither exists the LOCAL path comes back, so every error and skip
    message keeps naming the place a reader would look first.
    """
    local = repo / KEY_RELATIVE
    if local.exists():
        return local
    shared = main_checkout(repo) / KEY_RELATIVE
    if shared.exists():
        return shared
    return local


def describe_key_path(repo: Path, key: Path) -> str:
    """A path for a human-readable message, relative when it can be.

    ``Path.relative_to`` RAISES when the key was found in the main checkout and
    ``repo`` is a worktree, which is precisely the case this module was written
    to create -- so the one caller that formats this string would have started
    throwing ValueError the day the fix landed.
    """
    try:
        return key.relative_to(repo).as_posix()
    except ValueError:
        return key.as_posix()
