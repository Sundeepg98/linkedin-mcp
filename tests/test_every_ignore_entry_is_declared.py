"""Every ``.gitignore`` entry that shields the sweep must argue for itself.

WHY THIS FILE EXISTS. The identity and credential guards sweep
``committable_files()`` -- tracked PLUS untracked-not-ignored. ``.gitignore`` is
therefore not only a convenience about what git carries: **it is the one lever
that removes a file from the guard's subject.** Three times on 2026-09-19 a
sweep failure was repaired by adding a line to ``.gitignore``, and each time the
repair was correct -- but the argument for why it was correct lived in a commit
message, where the next person adding a line will not read it.

``4e80b79`` wrote the rule out while repairing the third one:

    the same argument for why ignoring is the repair rather than declaring:
    the ids are DERIVED from the test files, and those are swept directly.
    This artifact is a second copy of text the guard already reads at its
    source, so nothing stops being checked.

That sentence is the class-level fix. This file promotes it from prose to a
test, so the next ``.pw-browsers/`` cannot enter by convenience: a new pattern
fails the suite until somebody classifies it, and the ``DERIVED`` class cannot
be claimed without naming the source that is swept instead.

WHAT THIS IS NOT. It is NOT a narrowing of the sweep -- it adds no exclusion and
removes no file from any scan. It constrains only the *justification* attached
to an exclusion that already exists. The sweep's subject is unchanged at every
point in this file, which is the property
:func:`test_this_file_removes_nothing_from_the_sweep` pins.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
GITIGNORE = REPO / ".gitignore"


# ===========================================================================
# The classes
# ===========================================================================

#: The five admissible reasons an entry may shield a path from the sweep.
#: Each one is a claim about COVERAGE, not about tidiness, because the only
#: question that matters is whether ignoring the path stops something being
#: checked.
CLASSES = {
    "SECRET": (
        "Content that must never be committed at all. The ignore IS the "
        "protection: sweeping it is not the goal, its absence from every "
        "commit is. Coverage is not lost because the file is not supposed to "
        "reach a commit for the sweep to inspect."
    ),
    "DERIVED": (
        "A second copy of text the guard already sweeps at its source. "
        "Coverage is not lost because the original is read directly. "
        "REQUIRES a named source, and the source must itself be swept."
    ),
    "FOREIGN": (
        "Installed, downloaded or compiled third-party content. Nothing "
        "under it was authored here, so there is no identifier of ours for "
        "the guard to find."
    ),
    "LOCAL_STATE": (
        "Machine-local runtime, cache or scratch output. It exists only on "
        "one box and is never part of any commit."
    ),
    "UNIGNORE": (
        "A '!' negation. It WIDENS the swept set rather than shielding "
        "anything, so it needs no coverage argument."
    ),
}

#: Every pattern in ``.gitignore``, with the class that justifies it and, for
#: ``DERIVED`` only, the source glob that is swept in its place.
#:
#: ADDING A LINE TO ``.gitignore`` MEANS ADDING A LINE HERE. That is the whole
#: point: the cost of shielding a path from the identity guard is one sentence
#: of argument, paid at the moment the shield goes up rather than reconstructed
#: from a commit message months later.
DECLARED: dict[str, tuple[str, str | None]] = {
    # Live session cookies -- a signed-in login to his real account.
    "_state/": ("SECRET", None),
    "chrome-profile/": ("SECRET", None),
    "browser_profile/": ("SECRET", None),
    # Interpreters, installed packages and compiled output.
    "venv/": ("FOREIGN", None),
    ".venv/": ("FOREIGN", None),
    "__pycache__/": ("FOREIGN", None),
    "uv.lock": ("FOREIGN", None),
    "*.py[cod]": ("FOREIGN", None),
    "*.egg-info/": ("FOREIGN", None),
    "build/": ("FOREIGN", None),
    "dist/": ("FOREIGN", None),
    # Local run output.
    ".pytest_cache/": ("LOCAL_STATE", None),
    ".coverage": ("LOCAL_STATE", None),
    "htmlcov/": ("LOCAL_STATE", None),
    "*.log": ("LOCAL_STATE", None),
    # CI's own working files. THE 4e80b79 CASE: pytest node ids are a second
    # copy of text that lives in tests/, and tests/ is swept directly.
    "junit*.xml": ("DERIVED", "tests"),
    "collected*.txt": ("DERIVED", "tests"),
    "collected.txt": ("DERIVED", "tests"),
    "shard-collected.txt": ("DERIVED", "tests"),
    "shard-files.txt": ("DERIVED", "tests"),
    "shard-plan.json": ("DERIVED", "tests"),
    "junit.xml": ("DERIVED", "tests"),
    "reports/": ("DERIVED", "tests"),
    # Secrets by file shape.
    ".env": ("SECRET", None),
    ".env.*": ("SECRET", None),
    "!.env.example": ("UNIGNORE", None),
    # Raw captures from the live signed-in session: full PII, live tokens.
    "_audit/_probe-*.html": ("SECRET", None),
    "_audit/*_raw.html": ("SECRET", None),
    "_audit/_fixture_sanitisation_check.txt": ("SECRET", None),
    "*_probe-*.html": ("SECRET", None),
    "*_capture*.html": ("SECRET", None),
    # The de-anonymisation key for every committed fixture.
    "_audit/_sanitisation_key.json": ("SECRET", None),
    "_sanitisation_key*": ("SECRET", None),
    # Session archives and storage-state exports.
    "*.har": ("SECRET", None),
    "*.har.gz": ("SECRET", None),
    "storage_state*.json": ("SECRET", None),
    "*storage-state*.json": ("SECRET", None),
    "auth_state*.json": ("SECRET", None),
    # Chrome profile artefacts wherever they land -- a cookie jar with extra
    # steps, per .gitignore's own note on this block.
    "**/Cookies": ("SECRET", None),
    "**/Cookies-journal": ("SECRET", None),
    "**/Local State": ("SECRET", None),
    "**/Login Data*": ("SECRET", None),
    "**/Web Data*": ("SECRET", None),
    "**/DevToolsActivePort": ("SECRET", None),
    "*.pma": ("SECRET", None),
    "*.sqlite": ("SECRET", None),
    "*.sqlite3": ("SECRET", None),
    "*.db-journal": ("SECRET", None),
    # Designated quarantine for working notes.
    "_audit/_scratch/": ("LOCAL_STATE", None),
    # Playwright's downloaded browsers. THE .pw-browsers CASE: nothing under
    # it is ours, and a Linux executable named `chrome` has no suffix, so the
    # extension-keyed binary filter could not reach it either.
    ".pw-browsers/": ("FOREIGN", None),
}


# ===========================================================================
# The parser -- a pure function, so the controls can feed it synthetic text
# ===========================================================================


def ignore_patterns(text: str) -> list[tuple[int, str]]:
    """Every real pattern line in ``text``, as ``(line number, pattern)``.

    Pure on purpose. The controls at the bottom of this file feed it a
    SYNTHETIC ``.gitignore`` to prove the checks below can actually fail; a
    version that read the real file internally could not be controlled at all.
    """
    out: list[tuple[int, str]] = []
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append((number, line))
    return out


def undeclared(text: str, declared: dict[str, tuple[str, str | None]]) -> list[tuple[int, str]]:
    """Patterns present in ``text`` that nobody has classified."""
    return [(n, p) for n, p in ignore_patterns(text) if p not in declared]


def stale(text: str, declared: dict[str, tuple[str, str | None]]) -> list[str]:
    """Declarations whose pattern is no longer in ``text``."""
    live = {p for _, p in ignore_patterns(text)}
    return sorted(p for p in declared if p not in live)


def _gitignore_text() -> str:
    return GITIGNORE.read_text(encoding="utf-8", errors="replace")


# ===========================================================================
# 1. The admission rule
# ===========================================================================


def test_every_ignore_pattern_is_declared():
    """A new ``.gitignore`` line fails the suite until somebody argues for it.

    THIS IS THE POINT OF THE FILE. Three times in one day a sweep failure was
    repaired by ignoring a path. Every one of those repairs was right, and not
    one of them was forced to say why in a place the next author would read.
    """
    missing = undeclared(_gitignore_text(), DECLARED)
    assert not missing, (
        "These .gitignore patterns shield paths from the identity and "
        "credential sweeps and are not declared in DECLARED:\n  "
        + "\n  ".join(f"line {n}: {p}" for n, p in missing)
        + "\n\nAdd each one to DECLARED with the class that justifies it. The "
        "question is never whether the path is untidy -- it is whether "
        "ignoring it stops something being checked. If the answer is DERIVED, "
        "name the source that is swept in its place."
    )


def test_no_declaration_outlives_its_pattern():
    """The table cannot rot into a list of rules about nothing."""
    dead = stale(_gitignore_text(), DECLARED)
    assert not dead, (
        "These patterns are declared here but no longer in .gitignore: "
        f"{dead}. Remove the declaration, so the table keeps describing the "
        "file it claims to describe."
    )


def test_every_declaration_uses_a_real_class():
    wrong = {p: c for p, (c, _) in DECLARED.items() if c not in CLASSES}
    assert not wrong, (
        f"Unknown justification class(es): {wrong}. Admissible: "
        f"{sorted(CLASSES)}."
    )


# ===========================================================================
# 2. The DERIVED rule -- 4e80b79's sentence, made mechanical
# ===========================================================================


def test_derived_entries_name_a_source():
    """``DERIVED`` is the one class that can be claimed falsely for free.

    Every other class is a statement about the ignored file itself. DERIVED is
    a statement about a RELATION -- that the same text is read somewhere else
    -- and a relation with no named other end is just an assertion.
    """
    unsourced = [p for p, (c, s) in DECLARED.items() if c == "DERIVED" and not s]
    assert not unsourced, (
        f"DERIVED claimed without naming a swept source: {unsourced}. "
        "Name the path whose text this artifact copies."
    )

    misplaced = [p for p, (c, s) in DECLARED.items() if c != "DERIVED" and s]
    assert not misplaced, (
        f"A source is only meaningful for DERIVED: {misplaced}."
    )


def test_every_derived_source_is_actually_swept():
    """"Nothing stops being checked" is a claim, so check it.

    A DERIVED declaration says the guard still reads this text at its source.
    If that source is not itself in the swept set, the claim is false and the
    ignore entry really did remove coverage.
    """
    swept = _committable()
    assert swept, "the swept set came back empty; this test would pass vacuously"

    for pattern, (klass, source) in sorted(DECLARED.items()):
        if klass != "DERIVED":
            continue
        covered = [rel for rel in swept if rel == source or rel.startswith(f"{source}/")]
        assert covered, (
            f"{pattern!r} is declared DERIVED from {source!r}, but no swept "
            f"file lives under {source!r}. Either the source is wrong or "
            "ignoring this pattern really does remove coverage."
        )


def _committable() -> list[str]:
    """Tracked plus untracked-not-ignored, as the guards define their subject."""
    out: list[str] = []
    for args in (["ls-files"], ["ls-files", "--others", "--exclude-standard"]):
        proc = subprocess.run(
            ["git", *args], cwd=str(REPO), capture_output=True, text=True
        )
        assert proc.returncode == 0, f"git {' '.join(args)} failed: {proc.stderr}"
        out.extend(line for line in proc.stdout.splitlines() if line.strip())
    return sorted(set(out))


# ===========================================================================
# 3. The controls -- every check above, shown FAILING
# ===========================================================================
#
# An instrument enters this repo's register only if it has been shown failing.
# A checker over a file that already satisfies it is green on day one and would
# be green with its body deleted, so each control below feeds the pure parser a
# SYNTHETIC .gitignore and asserts the check fires.


SYNTHETIC = "\n".join(
    [
        "# a comment, which is not a pattern",
        "",
        "   ",
        "_state/",
        "tests/fixtures/something-a-tool-dropped/",  # the undeclared newcomer
    ]
)


def test_control_the_parser_ignores_comments_and_blanks():
    got = ignore_patterns(SYNTHETIC)
    assert [p for _, p in got] == [
        "_state/",
        "tests/fixtures/something-a-tool-dropped/",
    ], got
    assert got[0][0] == 4, f"line numbers are off: {got}"


def test_control_an_undeclared_newcomer_is_caught():
    """THE .pw-browsers REPRODUCTION, in miniature.

    A tool drops a directory into the tree; somebody makes the sweep failure go
    away by ignoring it. Without this check that is a one-line, silent removal
    of a path from the guard's subject.
    """
    missing = undeclared(SYNTHETIC, DECLARED)
    assert missing == [(5, "tests/fixtures/something-a-tool-dropped/")], missing


def test_control_a_stale_declaration_is_caught():
    dead = stale(SYNTHETIC, DECLARED)
    assert "venv/" in dead and ".pw-browsers/" in dead, dead
    assert "_state/" not in dead, dead


def test_control_a_sourceless_derived_claim_is_caught():
    bad = {"reports/": ("DERIVED", None)}
    unsourced = [p for p, (c, s) in bad.items() if c == "DERIVED" and not s]
    assert unsourced == ["reports/"]


def test_control_a_derived_claim_with_a_dead_source_is_caught():
    """The claim 'the source is swept' must be able to come back false."""
    swept = _committable()
    source = "this-directory-does-not-exist"
    covered = [r for r in swept if r == source or r.startswith(f"{source}/")]
    assert covered == [], (
        "a path that does not exist was reported as swept; the DERIVED source "
        "check cannot fail and therefore certifies nothing"
    )


def test_control_an_unknown_class_is_caught():
    bad = {"reports/": ("TIDINESS", None)}
    wrong = {p: c for p, (c, _) in bad.items() if c not in CLASSES}
    assert wrong == {"reports/": "TIDINESS"}


# ===========================================================================
# 4. Anti-vacuity, and the promise that this file narrows nothing
# ===========================================================================


def test_the_table_actually_describes_this_repo():
    """Guards against the table and the file both being empty."""
    live = ignore_patterns(_gitignore_text())
    assert len(live) >= 40, f"only {len(live)} patterns parsed; the parser broke"
    assert len(DECLARED) >= 40, f"only {len(DECLARED)} declarations"


def test_this_file_removes_nothing_from_the_sweep():
    """The property that makes this addition safe, pinned rather than asserted.

    Everything else in this repo's guard history is a fight about what the
    sweep may stop looking at. This file introduces no exclusion at all: it
    reads ``.gitignore`` and a table, and writes nothing. The swept set with
    this file present is the swept set without it, plus this file itself.
    """
    swept = _committable()
    assert "tests/test_every_ignore_entry_is_declared.py" in swept, (
        "this test file is not in the swept set, which would mean the guard "
        "does not read the file that governs the guard"
    )
    # No pattern declared here may be one this file invented: every key must
    # come from .gitignore, which is the direction that keeps the table
    # descriptive rather than prescriptive.
    assert not stale(_gitignore_text(), DECLARED)


@pytest.mark.parametrize("klass", sorted(CLASSES))
def test_every_class_states_what_it_claims_about_coverage(klass):
    """A class whose meaning is unwritten is a rubber stamp with a name."""
    meaning = CLASSES[klass]
    assert len(meaning) > 60, f"{klass} has no real definition"
