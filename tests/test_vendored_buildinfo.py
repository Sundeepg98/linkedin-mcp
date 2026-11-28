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

IT READS THE CANONICAL SOURCE AT THE PIN, NEVER AT MASTER (2026-11-28). Each
copy's vendor header names the jobcore commit it was copied from, and every
comparison here is against that commit's blob (``git show <pin>:src/jobcore/
<module>.py`` in the sibling checkout). Until this date the identity and the
control compared against jobcore's working tree, which on CI is a fresh clone
of jobcore MASTER -- so an upstream merge that touched a vendored module turned
EVERY branch of this repo red on its next run, a lane's included, for a change
that lane never made. That happened: jobcore 50da018 reached master at
13:06:38Z, and the next lane run on ci/census-calls28 failed this file twice
(the identity at the master comparison and the control's precondition) for a
commit that lane had never seen. A branch now answers
only for what it claims, which is a question about the branch. Whether its
claim is still CURRENT -- the copy against jobcore master -- is a separate
question, asked by ``scripts/check_vendored_current.py`` in its own workflow
(``.github/workflows/vendored-current.yml``) on master pushes and on a daily
schedule, and never on a ci/ ref.

A PIN THAT DOES NOT RESOLVE FAILS, LOUDLY. It used to skip. A header names a
commit as a claim; a claim that cannot be checked against a checkout that IS
present is not a pass, and a skip let it pass quietly.

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


def pinned_blob(jobcore_root, commit, module):
    """jobcore's ``src/jobcore/<module>.py`` as it was AT ``commit``.

    Read with ``git show`` from the jobcore checkout, so neither its working
    tree nor its master can answer for the commit a header names. A commit
    that does not resolve there FAILS the calling test: see the module
    docstring for why that is no longer a skip.
    """
    blob = subprocess.run(
        ["git", "-C", str(jobcore_root), "show", f"{commit}:src/jobcore/{module}.py"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if blob.returncode != 0:
        pytest.fail(
            f"the vendored {module}.py is pinned to jobcore {commit}, which does "
            f"not resolve in the jobcore checkout beside this repo: "
            f"{blob.stderr.strip()[:200]!r}. A pin is a claim; give the checkout "
            f"full history, or correct the header.",
            pytrace=False,
        )
    return blob.stdout


def pinned_canonical(canonical, module):
    """The canonical module at the commit THIS copy's own header names."""
    header, _ = split_header((PACKAGE_DIR / f"{module}.py").read_text(encoding="utf-8"))
    commit = pinned_commit(header)
    if not commit:
        pytest.fail(f"linkedin_server/{module}.py names no jobcore commit in its vendor header")
    return pinned_blob(canonical.parents[1], commit, module)


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
    """One differing byte is a failure. Fix upstream, then re-vendor.

    Canonical means jobcore AT THE PIN this copy's header names -- never the
    jobcore checkout's working tree, which on CI is master.
    """
    _, body = split_header((PACKAGE_DIR / f"{module}.py").read_text(encoding="utf-8"))
    expected = pinned_canonical(canonical, module)

    assert normalise(body) == normalise(expected), (
        f"linkedin_server/{module}.py has drifted from jobcore's canonical "
        f"{module}.py at the commit its header pins. Fix the bug UPSTREAM in "
        f"jobcore, then re-vendor and update the commit line in the vendor header."
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
    # makes the pin a claim rather than a decoration -- and a pin that does
    # not resolve FAILS inside pinned_blob, where it used to skip.
    expected = pinned_blob(canonical.parents[1], commit, module)
    assert normalise(body) == normalise(expected), (
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
    real = (PACKAGE_DIR / f"{module}.py").read_text(encoding="utf-8")
    expected = pinned_canonical(canonical, module)

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


def _git(repo, *args):
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert proc.returncode == 0, f"git {' '.join(args)}: {proc.stderr}"
    return proc.stdout.strip()


def _jobcore_whose_master_moved(tmp_path):
    """A jobcore checkout whose master moved on after the commit a copy pins.

    Two commits of ``src/jobcore/buildinfo.py``: the PINNED one, then a later
    one that master and the working tree now hold -- what lane CI's fresh clone
    looks like the moment an upstream change lands.
    """
    root = tmp_path / "jobcore"
    (root / "src" / "jobcore").mkdir(parents=True)
    _git(root, "init", "-q")
    who = ("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
           "-c", "commit.gpgsign=false")
    (root / "src" / "jobcore" / "buildinfo.py").write_text("PINNED = 1\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, *who, "commit", "-q", "-m", "the commit a copy pins")
    pinned = _git(root, "rev-parse", "--short", "HEAD")
    (root / "src" / "jobcore" / "buildinfo.py").write_text("MOVED = 2\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, *who, "commit", "-q", "-m", "master moves on upstream")
    return root, pinned


def test_the_comparison_reads_the_pin_and_never_the_working_tree(tmp_path):
    """THE REDESIGN, pinned. Master moving upstream must not move what is compared.

    Against the pre-2026-11-28 comparison, which read the checkout's working
    tree, this returns the MOVED body and fails.
    """
    root, pinned = _jobcore_whose_master_moved(tmp_path)
    assert (root / "src" / "jobcore" / "buildinfo.py").read_text(encoding="utf-8") == "MOVED = 2\n"
    assert normalise(pinned_blob(root, pinned, "buildinfo")) == "PINNED = 1\n"


def test_a_pin_that_does_not_resolve_fails_loudly(tmp_path):
    """A header pin with no commit behind it is a FAILURE, never a skip.

    The pre-2026-11-28 header test skipped here. Caught both ways below, so a
    regression to a skip is red rather than one more quiet "s" in the summary.
    """
    root, _ = _jobcore_whose_master_moved(tmp_path)
    try:
        pinned_blob(root, "0000000", "buildinfo")
    except pytest.fail.Exception as raised:
        assert "does not resolve" in str(raised), raised
    except pytest.skip.Exception:
        pytest.fail("an unresolvable pin was SKIPPED, which is the defect this test exists for")
    else:
        pytest.fail("an unresolvable pin returned a body")


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
