"""The de-anonymisation key must be uncommittable under EVERY name it wears.

WHAT HAPPENED. ``.gitignore`` named ``_audit/_sanitisation_key.json`` as an
EXACT PATH. On 2026-09-03 a working backup of that file was made, called
``_sanitisation_key.json.bak-preneedle-20260903``, and it was FULLY
COMMITTABLE -- the one file in this repository that reverses every scrubbed
fixture, sitting untracked and un-ignored, one ``git add -A`` from a public
commit. It was moved out of the tree by hand.

WHY AN EXACT PATH WAS THE WRONG SHAPE, and it is the same shape of error as a
navigation gate anchored to one spelling: the thing being protected is not a
PATH, it is a FILE, and files acquire suffixes. ``.bak``, ``.orig``, ``.save``,
a date stamp, an editor's swap copy, a second copy under ``scripts/`` beside
the sweep that reads it -- every one of those was committable while the rule
read as though the key were covered.

MEASURED BEFORE THE FIX, with ``git check-ignore`` -- git's own answer, not a
reading of the file:

    IGNORED      _audit/_sanitisation_key.json
    COMMITTABLE  _audit/_sanitisation_key.json.bak-preneedle-20260903
    COMMITTABLE  _audit/_sanitisation_key.json.bak
    COMMITTABLE  _audit/_sanitisation_key.backup.json
    COMMITTABLE  _audit/_sanitisation_key-copy.json
    COMMITTABLE  _audit/_sanitisation_key.json.orig
    COMMITTABLE  scripts/_sanitisation_key.json

Six of seven, and the last one is the one the handover did not predict: the
rule was anchored to ``_audit/`` as well as to the name, so a COPY AT ANOTHER
PATH was never covered either.

THE INSTRUMENT IS ``git check-ignore``, deliberately, and not a substring
search of ``.gitignore``. A test that greps the file can only confirm that a
line somebody wrote is still there; it cannot answer the question that
matters, which is whether git would let the file through. The exact-path rule
would have passed a grep every day it was insufficient.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def _is_ignored(relative_path: str) -> bool:
    """Ask git, about a path that need not exist.

    ``git check-ignore`` resolves patterns without touching the filesystem, so
    this asserts the RULE rather than requiring a real key on the machine --
    which matters, because the machines that most need this guard are the ones
    that do not have the key.
    """
    proc = subprocess.run(
        ["git", "check-ignore", "-q", "--no-index", relative_path],
        cwd=str(REPO),
        capture_output=True,
    )
    # 0 = ignored, 1 = not ignored, anything else = git could not answer.
    assert proc.returncode in (0, 1), (
        f"git check-ignore failed on {relative_path!r}: "
        f"rc={proc.returncode} {proc.stderr!r}"
    )
    return proc.returncode == 0


#: Names the key has worn or could plausibly wear.
#:
#: THE FIRST IS THE REAL ONE. ``...bak-preneedle-20260903`` is not invented for
#: this test -- it is the file that actually existed, untracked and
#: un-ignored, on 2026-09-03. The rest are the ordinary ways a file acquires a
#: second name: a shell backup, an editor's original, a dated copy, a
#: hand-made duplicate, and the same file sitting next to the script that
#: reads it.
KEY_SPELLINGS = (
    "_audit/_sanitisation_key.json.bak-preneedle-20260903",
    "_audit/_sanitisation_key.json",
    "_audit/_sanitisation_key.json.bak",
    "_audit/_sanitisation_key.json.orig",
    "_audit/_sanitisation_key.json.save",
    "_audit/_sanitisation_key.json.20260903",
    "_audit/_sanitisation_key.backup.json",
    "_audit/_sanitisation_key-copy.json",
    "_audit/_sanitisation_key (copy).json",
    "scripts/_sanitisation_key.json",
    "_sanitisation_key.json",
)


@pytest.mark.parametrize("spelling", KEY_SPELLINGS)
def test_every_spelling_of_the_key_is_ignored(spelling):
    """One file, every name it can wear, and git's own verdict on each."""
    assert _is_ignored(spelling), (
        f"{spelling!r} is COMMITTABLE. It is the de-anonymisation key for "
        "every fixture in tests/fixtures/, under a name the ignore rule does "
        "not cover -- which is exactly how the 2026-09-03 backup came to be "
        "one `git add -A` from a public commit."
    )


def test_a_neighbour_that_is_not_the_key_is_still_committable():
    """THE CONTROL, and without it the test above certifies nothing.

    A rule broad enough to ignore every spelling of the key is also broad
    enough to ignore things nobody meant to hide, and the failure mode of an
    over-broad ignore is silent: a file that should be tracked simply never
    appears in ``git status``. So the boundary is asserted from BOTH sides --
    these are real neighbours in the same directories, and each must remain
    visible to git.

    ``scripts/sweep_tracked_for_identity.py`` is the sharpest of them: it is
    the script that READS the key, it lives beside where a stray copy would
    land, and ``test_no_committed_identity.py`` asserts it is tracked. An
    ignore rule that swallowed it would turn the identity sweep off without a
    single test going red there.
    """
    must_stay_visible = (
        "scripts/sweep_tracked_for_identity.py",
        "_audit/2026-08-31-linkedin-perform.md",
        "tests/fixtures/jobs_tracker_row.html",
        "_audit/_sanitisation_notes.md",
    )
    swallowed = [name for name in must_stay_visible if _is_ignored(name)]
    assert swallowed == [], (
        f"the ignore rule is too broad and swallowed {swallowed}. An "
        "over-broad ignore hides a file from `git status` silently, which is "
        "a worse failure than the one it was widened to fix."
    )


def test_the_exact_path_rule_was_kept_alongside_the_glob():
    """The narrow rule STAYS, and the redundancy is deliberate.

    The glob is a strict superset, so removing the exact line would change no
    behaviour -- and ``test_no_committed_identity.py`` asserts that exact
    string is present in ``.gitignore``, so dropping it would break a guard
    somewhere else for no gain. A redundant ignore costs nothing; a removed
    one is a change somebody has to notice.
    """
    ignored = (REPO / ".gitignore").read_text(encoding="utf-8")
    assert "_audit/_sanitisation_key.json" in ignored
    assert "_sanitisation_key*" in ignored
