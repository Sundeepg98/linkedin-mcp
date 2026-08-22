"""The vendored copies of jobcore's modules must not drift.

``linkedin_server/buildinfo.py`` and ``linkedin_server/paths.py`` are VERBATIM
copies of jobcore's canonical modules. This server does not depend on jobcore
and must not start: adding the dependency for a debug field and a path renderer
would turn ``pip install -r requirements.txt`` into "also clone a sibling repo".
jobcore declares zero runtime dependencies precisely so a copy is possible.

The cost of a copy is drift, and drift in these two modules is not cosmetic.
``buildinfo`` exists to answer "what code is this process running" -- a copy
that quietly diverges answers that question about a module nobody else has.
So this file is the thing that makes vendoring honest: it re-reads the canonical
source and fails on a single differing byte.

WHY THIS FILE SKIPS RATHER THAN FAILS when jobcore is absent: linkedin is a
standalone repository with its own remote, and a clone of it alone must stay
green. The sibling checkout is a convenience of the operator's workspace, not a
requirement of this package -- which is the entire argument for vendoring.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

#: The line the vendor header ends with. Everything after it is canonical.
SENTINEL = "# --- END VENDOR HEADER; everything below is verbatim from jobcore ---"

VENDORED = ("buildinfo", "paths")

PACKAGE_DIR = Path(__file__).resolve().parent.parent / "linkedin_server"


def canonical_dir():
    """Walk UP to the shared ``mcp-servers`` directory. Never a hardcoded path.

    A hardcoded absolute path would be one more copy of this machine's layout
    living in the repository, which is the defect the sibling
    ``test_path_hygiene.py`` exists to remove from tool results.
    """
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "jobcore" / "src" / "jobcore"
        if candidate.is_dir():
            return candidate
    return None


def split_header(text):
    """Return ``(header, body)``. The body is what must match canonical."""
    assert SENTINEL in text, "the vendor header sentinel is missing"
    header, _, body = text.partition(SENTINEL)
    return header, body.lstrip("\r\n")


def normalise(text):
    """Line endings only.

    ``core.autocrlf`` is true on this machine, so a freshly CLONED repository
    checks out CRLF while a file a tool just wrote is LF. Comparing raw bytes
    across two repositories would then fail whenever one is cloned and the other
    is not -- red for a reason nobody in either repo can fix, which is exactly
    the failure mode ``pytest.ini`` already scopes the warning filter to avoid.
    Every other byte is compared exactly.
    """
    return text.replace("\r\n", "\n")


def pinned_commit(header):
    for line in header.splitlines():
        if "Vendored from jobcore commit:" in line:
            return line.split(":", 1)[1].strip()
    return None


@pytest.fixture(scope="module")
def canonical():
    directory = canonical_dir()
    if directory is None:
        pytest.skip(
            "the jobcore checkout is not present next to this one; a clone of "
            "linkedin alone is expected to be green, which is the point of "
            "vendoring rather than depending"
        )
    return directory


@pytest.mark.parametrize("module", VENDORED)
def test_the_vendored_body_is_identical_to_canonical(canonical, module):
    """One differing byte is a failure. Fix upstream, then re-vendor."""
    source = canonical / f"{module}.py"
    if not source.is_file():
        pytest.skip(f"canonical {module}.py is not present at {source.name}")

    _, body = split_header((PACKAGE_DIR / f"{module}.py").read_text(encoding="utf-8"))
    expected = source.read_text(encoding="utf-8")

    assert normalise(body) == normalise(expected), (
        f"linkedin_server/{module}.py has drifted from jobcore's canonical "
        f"{module}.py. Fix the bug UPSTREAM in jobcore, then re-vendor and "
        f"update the commit line in the vendor header."
    )


@pytest.mark.parametrize("module", VENDORED)
def test_the_header_pins_the_commit_it_was_copied_from(canonical, module):
    """A copy that does not say what it is a copy of cannot be checked."""
    header, body = split_header(
        (PACKAGE_DIR / f"{module}.py").read_text(encoding="utf-8")
    )

    commit = pinned_commit(header)
    assert commit, "the vendor header must name the jobcore commit"
    assert len(commit) >= 7 and all(c in "0123456789abcdef" for c in commit), commit

    # The header must also say WHERE, and that this is not a file to edit.
    assert "jobcore" in header and "VENDORED COPY" in header
    assert "DO NOT EDIT" in header

    # And the body must match the canonical file AT THAT COMMIT, not merely
    # whatever jobcore's working tree happens to hold right now. This is what
    # makes the pin a claim rather than a decoration.
    blob = subprocess.run(
        ["git", "-C", str(canonical.parents[1]), "show",
         f"{commit}:src/jobcore/{module}.py"],
        capture_output=True,
        text=True,
    )
    if blob.returncode != 0:
        pytest.skip(f"jobcore has no commit {commit} available to compare against")
    assert normalise(body) == normalise(blob.stdout), (
        f"linkedin_server/{module}.py does not match jobcore {commit}, which is "
        f"the commit its own header claims it was copied from."
    )


@pytest.mark.parametrize("module", VENDORED)
def test_the_comparison_can_fail(canonical, module):
    """CONTROL. Without this the two tests above could be vacuously green.

    A drift check that cannot detect drift is worse than no check: it
    manufactures confidence at scale. So an altered copy is built here and shown
    NOT comparing equal, using the same splitter and the same comparison the
    real assertions use.
    """
    source = canonical / f"{module}.py"
    if not source.is_file():
        pytest.skip(f"canonical {module}.py is not present at {source.name}")

    real = (PACKAGE_DIR / f"{module}.py").read_text(encoding="utf-8")
    expected = source.read_text(encoding="utf-8")

    # Sanity: the unaltered copy passes, so a failure below is the alteration.
    _, body = split_header(real)
    assert normalise(body) == normalise(expected)

    # One line changed, the header untouched: exactly what a "small fix applied
    # to the copy instead of upstream" looks like.
    tampered = real.replace("GIT_TIMEOUT_SECONDS = 5.0", "GIT_TIMEOUT_SECONDS = 9.0")
    tampered = tampered.replace("DISPLAY_TAIL_PARTS = 3", "DISPLAY_TAIL_PARTS = 4")
    assert tampered != real, "the control edited nothing; it would prove nothing"

    _, tampered_body = split_header(tampered)
    assert normalise(tampered_body) != normalise(expected)

    # A whitespace-only change must also be caught -- the comparison normalises
    # line endings and NOTHING else.
    spaced = real.replace(SENTINEL + "\n", SENTINEL + "\n\n ")
    _, spaced_body = split_header(spaced)
    assert normalise(spaced_body) != normalise(expected)


def test_the_vendored_modules_are_pure_ascii():
    """House rule, and the reason the em dashes were removed upstream.

    This package logs through a ``StreamHandler`` that encodes cp1252 on a
    Windows console, where a non-ASCII byte raises ``UnicodeEncodeError``.
    """
    for module in VENDORED:
        raw = (PACKAGE_DIR / f"{module}.py").read_bytes()
        offenders = [(i, b) for i, b in enumerate(raw) if b > 127]
        assert offenders == [], f"{module}.py: {offenders[:5]}"


def test_the_vendored_modules_import_and_expose_what_the_server_uses():
    """Vendoring that does not import is a copy of a file, not of a module."""
    from linkedin_server import buildinfo, paths

    assert callable(buildinfo.stamp)
    assert callable(buildinfo.resolve)
    assert callable(buildinfo.build_block)
    assert callable(paths.display_path)
    assert callable(paths.relativise_known)

    # build_block is NOT in jobcore's __all__, so a star-import would silently
    # not carry it. Pinned here because that is a trap, not an opinion.
    assert "build_block" not in buildinfo.__all__
