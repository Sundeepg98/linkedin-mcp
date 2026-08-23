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
    """Every path git tracks, as repo-relative posix strings."""
    proc = subprocess.run(
        ["git", "ls-files"], cwd=str(REPO), capture_output=True, text=True
    )
    assert proc.returncode == 0, f"git ls-files failed: {proc.stderr}"
    return [line for line in proc.stdout.splitlines() if line.strip()]


def scan(text: str) -> list[str]:
    """Return one complaint per credential-shaped token in ``text``."""
    return [
        f"{label}-shaped token {match.group(0)[:24]}..."
        for label, pattern in SHAPES
        for match in pattern.finditer(text)
    ]


TRACKED = tracked_files()


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


@pytest.mark.parametrize("relative", TRACKED, ids=lambda p: p)
def test_no_tracked_file_carries_a_session_credential(relative):
    if relative == _PLANT_HOME:
        pytest.skip("the module that defines the plant")
    path = REPO / relative
    if not path.is_file():
        pytest.skip("not present in the working tree")
    text = path.read_text(encoding="utf-8", errors="replace")
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
