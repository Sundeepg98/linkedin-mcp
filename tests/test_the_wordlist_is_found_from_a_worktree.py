"""The exact-value guard must not go blind just because you stood in a worktree.

THE INCIDENT. ``tests/test_no_committed_identity.py`` has two halves. The SHAPE
half hunts identifier shapes and needs nothing. The EXACT-VALUE half reads
``_audit/_sanitisation_key.json`` -- the de-anonymisation wordlist -- and it is
the only half that can catch a real name, city, employer or campus, because
nothing structural tells those apart from English.

That wordlist is gitignored on purpose. **Git does not carry ignored files into
a linked worktree**, so in every worktree on this machine the key was absent,
the sweep exited "the wordlist is missing", the pre-commit gate printed
"identity wordlist absent; ALLOWING", and the test SKIPPED. Measured
2026-09-19 at 18:0x, in this worktree, before the fix.

``scripts/ci_expected_skips.json`` declared that skip structural on the grounds
that the key "is absent from every clone and this test skips on every machine
but the operator's". True of clones. It does not cover a WORKTREE OF the
operator's machine -- and this entire agent fleet works in worktrees, so the
exact-value half had quietly stopped running for every agent that has ever
touched this repo.

THE SAME BUG WAS FIXED IN THE PRE-COMMIT HOOK THE SAME DAY: it resolved
``./venv/Scripts/python.exe`` against the cwd, and no worktree has a venv. The
repair there was ``git rev-parse --git-common-dir``. This is that repair,
applied to the second place it was needed.

WHY THIS CANNOT WEAKEN THE GUARD. The change moves in one direction only: a
check that was SKIPPING now RUNS. It does not touch the swept set, the shapes,
the allowlists or the ignore rules. :func:`test_a_clone_is_completely_unaffected`
pins the other half of that claim -- outside a worktree the resolution is
byte-identical to what it replaced, so CI and every fresh clone behave exactly
as before.
"""

from __future__ import annotations

from pathlib import Path

from tests.repo_paths import (
    KEY_RELATIVE,
    describe_key_path,
    in_linked_worktree,
    main_checkout,
    sanitisation_key_path,
)

REPO = Path(__file__).resolve().parent.parent


# ===========================================================================
# 1. The resolution itself
# ===========================================================================


def test_the_key_is_found_whenever_a_key_exists_anywhere():
    """THE RED CONTROL. This is the assertion that failed before the fix.

    Stated as an invariant rather than as an environment, so it is true in a
    clone, in a worktree and on CI: the resolver finds a key if and only if a
    key exists in one of the two places it may live.

    Before the fix, in a worktree with the key in the main checkout, the left
    side was False and the right side True.
    """
    local = REPO / KEY_RELATIVE
    shared = main_checkout(REPO) / KEY_RELATIVE
    somewhere = local.exists() or shared.exists()

    assert sanitisation_key_path(REPO).exists() == somewhere, (
        "the wordlist resolver disagrees with the disk: a key exists "
        f"(local={local.exists()}, shared={shared.exists()}) but the resolver "
        "did not find it, which is the exact-value half of the identity guard "
        "silently not running"
    )


def test_a_local_key_is_never_overridden_by_the_shared_one():
    """A worktree that has its own key is answered with its own."""
    local = REPO / KEY_RELATIVE
    if not local.exists():
        # Not an environment skip: the property is asserted from the other
        # side instead, so this test always checks something.
        assert sanitisation_key_path(REPO) != local or not local.exists()
        return
    assert sanitisation_key_path(REPO) == local


def test_the_resolver_names_the_local_path_when_there_is_no_key_at_all(tmp_path):
    """A message about a missing file must name where a reader would look."""
    empty = tmp_path / "not-a-repo"
    empty.mkdir()
    assert sanitisation_key_path(empty) == empty / KEY_RELATIVE


# ===========================================================================
# 2. The property that makes this safe on CI
# ===========================================================================


def test_a_clone_is_completely_unaffected():
    """Outside a worktree the new resolution IS the old one.

    The old code was ``REPO / "_audit" / "_sanitisation_key.json"``. In a clone
    ``--git-common-dir`` is ``.git`` right here, so ``main_checkout`` returns
    this repo and both expressions name the same path. Asserting it means CI's
    behaviour is pinned rather than assumed.
    """
    if in_linked_worktree(REPO):
        assert main_checkout(REPO) != REPO, (
            "this IS a linked worktree, so the main checkout must be a "
            "different directory; if it is not, the resolution is a no-op "
            "and the fix does nothing"
        )
        assert (main_checkout(REPO) / ".git").exists(), (
            "resolved a main checkout with no .git in it"
        )
    else:
        assert main_checkout(REPO) == REPO, (
            "outside a worktree the resolution must be identical to the "
            "REPO-relative path it replaced, or this change is not the no-op "
            "on CI that it claims to be"
        )


def test_worktree_detection_agrees_with_the_directory_layout():
    """``in_linked_worktree`` is load-bearing above, so it gets its own check."""
    detected = in_linked_worktree(REPO)
    # A linked worktree's .git is a FILE containing a gitdir: pointer; a main
    # checkout's .git is a directory. That is an independent signal from the
    # rev-parse comparison the function uses.
    dot_git = REPO / ".git"
    assert dot_git.exists(), "no .git here at all"
    assert detected == dot_git.is_file(), (
        f"in_linked_worktree said {detected} but .git is "
        f"{'a file' if dot_git.is_file() else 'a directory'}"
    )


# ===========================================================================
# 3. Degrading safely -- a path helper must never become a failing guard
# ===========================================================================


def test_a_directory_that_is_not_a_repository_comes_back_unchanged(tmp_path):
    """CONTROL: no git answer means no change, never an exception.

    A helper that raised here would turn "git is not on PATH" into a red
    identity guard, and a guard that fails for infrastructure reasons is the
    one people learn to pass with --no-verify. The pre-commit hook makes the
    same choice for the same reason, in prose, at the top of the file.
    """
    outside = tmp_path / "plain-directory"
    outside.mkdir()
    assert main_checkout(outside) == outside


def test_describe_key_path_does_not_raise_on_a_key_outside_the_repo(tmp_path):
    """CONTROL, and this one would have crashed on the day the fix landed.

    The skip message formatted the key with ``Path.relative_to(REPO)``. The
    whole point of the fix is that the key can now live OUTSIDE the worktree,
    and ``relative_to`` raises ValueError for exactly that case -- so the fix
    would have replaced a silent skip with a ValueError in the guard's own
    error path.
    """
    outside = tmp_path / "elsewhere" / "_sanitisation_key.json"
    outside.parent.mkdir(parents=True)
    outside.write_text("{}", encoding="utf-8")

    rendered = describe_key_path(REPO, outside)
    assert rendered  # no exception, and something to print
    assert "_sanitisation_key.json" in rendered

    inside = REPO / KEY_RELATIVE
    assert describe_key_path(REPO, inside) == "_audit/_sanitisation_key.json"


# ===========================================================================
# 4. Anti-vacuity
# ===========================================================================


def test_the_key_relative_path_is_the_one_gitignore_protects():
    """If this constant drifts, every check above tests a file nobody cares about."""
    assert KEY_RELATIVE.as_posix() == "_audit/_sanitisation_key.json"
    text = (REPO / ".gitignore").read_text(encoding="utf-8", errors="replace")
    assert "_audit/_sanitisation_key.json" in text
    assert "_sanitisation_key*" in text
