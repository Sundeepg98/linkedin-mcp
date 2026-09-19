"""No file in this repository may carry a LinkedIn session credential.

WHY THIS FILE EXISTS
--------------------
This repo has already pushed session material once. A fixture went in carrying
three real ``urn:li:activity`` ids and two per-impression tracking tokens, and
it walked past a guard that was a list of five literal strings --
``("li_at", "JSESSIONID", "csrfToken", "urn:li:member", "Bearer ")``. Every one
of those is a NAME. A credential is a VALUE. A guard made of names cannot see a
value, so the check was incapable of the finding from the day it was written.

``tests/test_sdui_surfaces_fixture.py`` fixed half of that afterwards by
hunting opaque LinkedIn ids as SHAPES rather than as remembered strings. This
file closes the other half, and widens it from the fixtures to the whole
repository:

* it enumerates every file GIT TRACKS, not a list anybody maintains, so a new
  fixture, a new script or a pasted debug dump is covered the moment it is
  added -- the same reasoning that turned the fixture list into a glob;
* it hunts the SHAPE of the two credentials that actually matter here, the
  365-day ``li_at`` and the ``JSESSIONID`` csrf token;
* it exempts the deliberate plant by EXACT PATH, never by shape, because a
  loose exemption is how a real credential hides behind a guard.

The scan is also driven at input it must reject, below, so an empty result
means the sweep ran rather than that it found nothing to look at.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tests.leakwalk import (
    JSESSIONID_SHAPE,
    LI_AT_SHAPE,
    PLANTED_JSESSIONID,
    PLANTED_LI_AT,
)

REPO = Path(__file__).resolve().parent.parent

#: The one file allowed to contain a credential-shaped string: the module that
#: DEFINES the plant. Written as an exact repo-relative path. Adding a second
#: entry here should feel like the deliberate act it is.
_PLANT_HOME = "tests/leakwalk.py"

SHAPES = (("li_at", LI_AT_SHAPE), ("JSESSIONID", JSESSIONID_SHAPE))


def tracked_files() -> list[str]:
    """Every path git TRACKS, as repo-relative posix strings.

    Kept narrow and kept in use: where the question really is "is this file in
    the repository", this is the answer. It is NOT what the sweeps below use
    -- see :func:`committable_files` for why.
    """
    proc = subprocess.run(
        ["git", "ls-files"], cwd=str(REPO), capture_output=True, text=True
    )
    assert proc.returncode == 0, f"git ls-files failed: {proc.stderr}"
    return [line for line in proc.stdout.splitlines() if line.strip()]


def untracked_files() -> list[str]:
    """Every path git does NOT track and does NOT ignore.

    ``--exclude-standard`` applies .gitignore, the global excludes and
    .git/info/exclude, so build output, ``_state/`` and caches stay out. What
    is left is exactly the set of files a ``git add`` would pick up.
    """
    proc = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"git ls-files --others failed: {proc.stderr}"
    return [line for line in proc.stdout.splitlines() if line.strip()]


def committable_files() -> list[str]:
    """Everything a commit could carry: TRACKED plus UNTRACKED-NOT-IGNORED.

    THIS EXISTS BECAUSE THE SWEEPS WERE SWEEPING THE WRONG SET, and the way
    that was found is the argument for it.

    On 2026-09-01 a file was added carrying a REAL LinkedIn activity id -- one
    of the operator's own posts -- in a repository that is public under his
    real name. The identity guard would have caught it instantly, and did not,
    because it swept ``git ls-files``: the file was UNTRACKED through every
    run. The suite was green and CORRECT; the file was invisible to the
    question. It became visible in the same commit that put the id in history.

    **THE CHECK A NEW FILE MOST NEEDS RAN ONLY AFTER THE FILE WAS PUBLISHED.**
    A guard against committing something must see what is ABOUT TO BE
    committed, not only what already was -- otherwise its first true answer
    always arrives one commit late, which is precisely too late for anything
    it is protecting.

    WHAT THIS COSTS: a stray untracked file in somebody's working tree is now
    swept, and a plant in one fails the suite. That is the intended behaviour
    rather than a side effect -- a file sitting in the tree is a file one
    ``git add -A`` away from being published, and this repo's own history has
    that exact mistake in it.
    """
    return sorted(set(tracked_files()) | set(untracked_files()))


def scan(text: str) -> list[str]:
    """Return one complaint per credential-shaped token in ``text``."""
    return [
        f"{label}-shaped token {match.group(0)[:24]}..."
        for label, pattern in SHAPES
        for match in pattern.finditer(text)
    ]


#: WIDENED 2026-09-01 from ``tracked_files()``. The name changed with it,
#: because "TRACKED" would now be a false description of the set and this
#: package does not keep names that lie. See :func:`committable_files`.
COMMITTABLE = committable_files()

#: The old name, kept ONLY so that the widening is visible rather than
#: silent: it is the same object, so nothing reads a narrower set by accident.
TRACKED = COMMITTABLE

#: What actually gets swept. The plant's home is removed HERE, at list-build
#: time, rather than skipped inside the test: this workflow treats any skip as
#: a failure on purpose (``scripts/ci_full_run_check.py``), because a suite
#: that is allowed to skip is a suite that can quietly stop checking.
SCANNED = [relative for relative in TRACKED if relative != _PLANT_HOME]


def test_exactly_one_file_is_exempt_and_every_other_one_is_on_disk():
    """No file may leave the sweep quietly.

    Two ways that could happen and both are closed here: an exemption growing
    past the single deliberate one, and a tracked path that is not in the
    working tree, which would drop out of the walk with nothing said.
    """
    assert set(TRACKED) - set(SCANNED) == {_PLANT_HOME}
    missing = [relative for relative in SCANNED if not (REPO / relative).is_file()]
    assert missing == [], missing


def test_an_untracked_file_reaches_the_sweep_before_it_is_ever_committed():
    """THE REGRESSION TEST FOR THE HOLE, at the level of the SET.

    A probe is written into the repo, confirmed to be untracked, and required
    to appear in ``committable_files()`` and NOT in ``tracked_files()``. That
    is the whole of what changed on 2026-09-01, so narrowing the sweep back
    fails here.

    IT DOES NOT WRITE A PLANT, and that is a deliberate risk trade rather than
    a weaker test. An end-to-end version -- untracked file, real plant, both
    guards red -- WAS run before this landed and both guards caught it, and
    both went blind when the untracked half of the sweep was removed. But as a
    PERMANENT test it would leave a credential-shaped string in the working
    tree if pytest were killed mid-run, and this repo's own history is a file
    reaching a commit because somebody did not notice it sitting there. The
    property is composed instead, from two checks that each fail on their own:
    this one owns "the set includes untracked files", and
    ``test_the_sweep_catches_a_credential_planted_in_a_file`` owns "the scan
    catches a plant".
    """
    probe = REPO / "tests" / "fixtures" / "_sweep_membership_probe.txt"
    assert not probe.exists(), "a previous run left this behind: %s" % probe
    try:
        probe.write_text("membership probe, no plant" + chr(10), encoding="utf-8")
        relative = "tests/fixtures/_sweep_membership_probe.txt"

        status = subprocess.run(
            ["git", "status", "--porcelain", "--", relative],
            cwd=str(REPO),
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert status.startswith("??"), (
            "the probe is not untracked (%r), so this test is not measuring "
            "what it claims to" % status
        )

        assert relative not in tracked_files(), relative
        assert relative in untracked_files(), relative
        assert relative in committable_files(), (
            "an untracked file is NOT in the committable sweep, which is the "
            "hole that let a real activity id reach a commit on a public repo"
        )
    finally:
        if probe.exists():
            probe.unlink()
    assert not probe.exists()


def test_there_are_files_to_scan():
    """A sweep over nothing passes forever. This is what stops that.

    The named files are the ones this check most exists for: the committed
    page captures, which are where session material got in last time.
    """
    assert len(TRACKED) > 50, len(TRACKED)
    for name in (
        "tests/fixtures/profile_topcard.html",
        "tests/fixtures/job_detail_hydrated.html",
        "linkedin_server/auth.py",
    ):
        assert name in TRACKED, name


@pytest.mark.parametrize("relative", SCANNED, ids=lambda p: p)
def test_no_tracked_file_carries_a_session_credential(relative):
    text = (REPO / relative).read_text(encoding="utf-8", errors="replace")
    assert not scan(text), (relative, scan(text))


def test_the_sweep_catches_a_credential_planted_in_a_file():
    """The control. Without it every assertion above could be a dead regex."""
    assert scan(f'<div data-token="{PLANTED_LI_AT}"></div>')
    assert scan(f"Cookie: JSESSIONID={PLANTED_JSESSIONID}")
    assert scan("AQEDAQ" + "aB3-_xY9" * 6)


def test_the_sweep_is_quiet_on_the_kind_of_file_it_walks_over():
    """The other direction. A sweep that fired on ordinary markup or code
    would be turned off within a day, which is the real failure mode."""
    assert scan("<div class='_17f16833 _86848d5e _573181de' role='list'>") == []
    assert scan("https://www.linkedin.com/jobs/view/4600000042") == []
    assert scan("def assert_read_url(url: str) -> str:  # the allowlist door") == []


def test_the_plant_home_really_does_hold_the_plant():
    """The exemption is only safe while it is pointed at the right file.

    If the plant moves and this exemption does not, the exemption becomes a
    blind spot over a file that no longer needs one -- so it is checked rather
    than assumed.
    """
    assert _PLANT_HOME in TRACKED
    assert scan((REPO / _PLANT_HOME).read_text(encoding="utf-8"))
