"""Run the tests a change can actually break, and say out loud what it did not run.

THE PROPERTY THIS FIXES, which is not slowness.

A full-suite gate is **O(suite)**. Every feature added makes every commit
slower, forever, and the curve only bends the wrong way. Measured on this box
2026-09-20: 6094 tests in 168 files, and merely COLLECTING them -- before one
of them runs -- costs 36.2s cold and 7.0s warm; CI is 1042s wall with the
windows shards at 409-460s. An impact-scoped gate is **O(change)**: what it
runs is a function of the diff and not of the tree, so it stays flat as the
suite grows.

The exponent is visible in this very change. Adding ONE script and ONE test
file took the suite from 6076 tests to 6094 -- eighteen, of which nine are
mine and nine are parametrised meta-tests that sweep ``scripts/*.py`` and
grew because a file appeared. Under a full-suite gate every commit from now
on pays for those nine, forever, including the commits that cannot touch
them.

That is the whole argument. Not "the gate is slow", but "the gate has the
wrong exponent."

THE DEFECT THAT MADE THE OBVIOUS VERSION UNSAFE, and it is why this file is
longer than a one-line pytest invocation.

``scripts/pre_commit_boundary_gate.py`` already computes an impact set. Its
rule is NAME-BASED over python: file B is coupled to staged file A when B
names a module-level constant A defines. Scoping a gate to that rule alone
produces a gate that waves through the exact class of defect this repository
hit on the morning of 2026-09-20:

    staged   _audit/2026-09-03-linkedin-gap-blockers.md   (a CORRECTED BY
             marker inserted between a table header and its first data row)
    impact   ZERO test files -- ``staged_paths()`` keeps only ``*.py``, so a
             ``.md`` never reaches the coupling rule at all
    truth    tests/test_blocker_map_is_derived.py, 2 failed / 5 passed in
             1.16s. The parser read 9 blockers where the ledger has 97.

Measured, not argued: on 2026-09-20 that exact revert was staged in a
worktree and ``pre_commit_boundary_gate.py`` exited **0 with no output at
all**, while the coupled test was red in 3.07s wall.

The reason is structural and it generalises past this one file. **A document
that is also a DATA SOURCE is read by a path, and a path is not a name.**
``scripts/build_blocker_map.py`` opens that ledger as
``ROOT / "_audit" / "2026-09-03-linkedin-gap-blockers.md"`` -- composed from
segments, so even a literal grep for the repo-relative path finds nothing.
And the test never mentions the ledger at all; it imports the script.

So the coupling is TWO HOPS over TWO DIFFERENT KINDS OF EDGE:

    data file  --named by-->     scripts/build_blocker_map.py
               --imported by-->  tests/test_blocker_map_is_derived.py

and the two arrows cannot be found by the same instrument. That is the
central design decision in this file:

  * **A PYTHON DEPENDENCY IS FOUND BY PARSING IMPORTS.** Precise, and it has
    to be: ``linkedin_server/shape.py`` has the module stem ``shape``, and a
    text scan for the word "shape" across 168 test files matches prose in
    docstrings and would couple most of the suite to a one-line edit. An
    import is a structure; read it as one.
  * **A DATA DEPENDENCY IS FOUND BY SCANNING FOR THE PATH.** It has to be:
    the path is assembled from segments at runtime, so there is no import to
    parse and no constant to match. The token that survives assembly is the
    BASENAME, so that is what is matched, bounded so ``jobs.md`` does not
    match ``subjobs.md``.
  * **A SHARED CONSTANT IS FOUND BY THE SHIPPED RULE**, imported from the
    boundary gate rather than copied.

Using one instrument for all three is how the census case got missed. The
boundary gate's own docstring already says its constant rule is deliberately
NOT an import graph, for the symmetric reason. Three couplings, three
readers.

AND A THIRD CATEGORY THAT IS NOT A COUPLING AT ALL: THE CORPUS-WIDE FLOOR.

A sibling wave shipped red to CI twice on 2026-09-20, both times for one
cause, and its own diagnosis is the requirement: *"a local selection that ran
the files I touched and their neighbours and missed guards whose names
connect to nothing I was working on."* The two it missed were
``test_page_text_is_never_printed.py`` and ``test_no_committed_identity.py``.

**NO WIDENING OF THE RULES ABOVE COULD HAVE CAUGHT THOSE.** They sweep the
whole tracked file set for a property, so they are coupled to EVERYTHING and
therefore to nothing in particular; they name no module and import nothing
from the diff. The relationship is real and maximal and the ANALYSIS has no
handle on it. So the plan is:

    selected     coupled to the diff -- name, import, constant, data path
    + floor      every corpus-wide sweep, run UNCONDITIONALLY
    = plan

The floor is DERIVED (:func:`always_run_files`), not listed, and a control
pins the two proven members so the derivation is checked rather than
believed. It costs 13 files / 1797 tests / 25.6s, and that is the price of
not shipping a real name into served history.

``selected`` and the floor are kept in separate fields for a reason that took
one careful moment to see: the floor is never empty, so if the plan were a
single merged list the "empty impact set" alarm below could never fire
again -- satisfied forever by a guarantee that says nothing at all about
whether the analyser worked.

WHAT IT REFUSES TO SAY.

**A gate that prints PASS after running 12 of 6094 tests has told a dangerous
half-truth.** So this one may not print a bare pass. Every scoped run ends
with what it did NOT run and the fraction that represents, in its own output,
on success as loudly as on failure. Where it cannot derive a number it says
so rather than estimating: the suite-size denominator is cached in
``impact_gate_suite_size.json`` with the commit it was taken at, and a
missing cache downgrades the report to file counts, which are exact and free.

**AN EMPTY IMPACT SET IS A LOUD EVENT, NEVER A SILENT PASS.** This repository
has produced three checks in two days that could not fail -- a control that
could not fire on linux, a guard disarmed in every worktree, a floor guard
that could not run on its own floor. A selector that returns an empty set is
the same disease wearing a different hat, because an empty selection is
indistinguishable from a broken selector from the outside. So it FALLS BACK
TO THE FULL SUITE and says why.

THE ESCAPE HATCH IS PART OF THE DESIGN, not an apology for it. Three
conditions send this to the full suite, and each prints its reason:

    empty          the selector found nothing (see above)
    too wide       the impact set is a large fraction of the suite, where
                   running everything costs about the same and answers more
    unclassified   a staged path changes behaviour this analyser has no model
                   of -- conftest.py, pytest.ini, pyproject.toml,
                   requirements.txt -- so scoping would be a guess

Silently narrowing is the one thing it may never do.

**WHAT THIS DOES NOT REPLACE: CI. KEEP THE MATRIX.**

``.github/workflows/ci.yml`` runs this suite across THREE PLATFORMS. This box
is windows-only, and windows-vs-linux defects are precisely what CI has been
catching -- path separators, encodings, line endings, and guards whose
behaviour differs by filesystem. A green impact gate is a fast LOCAL signal
that a change did not break what it can reach on ONE platform. It is not a
certification, and **nobody should read a 5-second pass here as a reason to
shrink the matrix.** The certifier is CI; this is the thing that tells you
before you push.

USAGE::

    python scripts/impact_gate.py                 # the staged index
    python scripts/impact_gate.py --against HEAD~1
    python scripts/impact_gate.py --paths a/b.md  # explicit, for controls
    python scripts/impact_gate.py --plan-only     # print the set, run nothing
    python scripts/impact_gate.py --recount       # refresh the denominator

Exit 0 = the plan was green, or infrastructure prevented a verdict and said
so. Exit 1 = a test this change can reach is RED.
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import re
import subprocess
import sys
import time
import tokenize
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
# THE SHIPPED INSTRUMENT, IMPORTED RATHER THAN REWRITTEN. The boundary gate
# already solved worktree root resolution -- the CONTENT root and the TOOLING
# root are different questions with different answers, and both were found the
# hard way on 2026-09-19. A second copy here would be a second copy to keep
# correct.
import pre_commit_boundary_gate as boundary  # noqa: E402

REPO: Path = boundary.REPO
PYTHON: Path = boundary.PYTHON

TESTS_DIR = REPO / "tests"
SCRIPTS_DIR = REPO / "scripts"
PACKAGE_DIR = REPO / "linkedin_server"

#: A staged path matching any of these changes behaviour the analyser has no
#: model of, so scoping would be a guess. ``tests/conftest.py`` is the sharp
#: one: its fixtures are AUTOUSE, so it is loaded by every test in the suite
#: and named by almost none of them -- exactly the coupling a name-based
#: analyser cannot see. The rest configure the runner itself.
_GLOBAL_TRIGGERS = (
    "tests/conftest.py",
    "pytest.ini",
    "pyproject.toml",
    "setup.cfg",
    "tox.ini",
    "requirements.txt",
    "requirements-dev.txt",
)

#: Above this fraction of the suite's TEST FILES, scoping stops paying: the
#: plan costs about what everything costs, and everything answers more. The
#: denominator is FILES rather than tests because files are exact and free to
#: count, while counting tests means the 36.2s collection this gate exists to
#: avoid.
_FULL_SUITE_AT_FRACTION = 0.45

#: Plans at or above this many files run under xdist. Taken from the boundary
#: gate's MEASURED threshold rather than re-guessed: xdist pays a fixed
#: per-worker startup that loses on small plans (31.74s at ``-n 8`` against
#: 26.10s serial on one 29-test file, 2026-09-19).
_PARALLEL_FILE_THRESHOLD = 5

#: Where the suite-size denominator is cached, with the commit it was taken at
#: so a reader can tell whether it still means anything.
_SUITE_SIZE_CACHE = Path(__file__).resolve().parent / "impact_gate_suite_size.json"


# --------------------------------------------------------------------------
# Tokens: what a path looks like when another file refers to it.
# --------------------------------------------------------------------------

def _rel(path: str) -> str:
    """Repo-relative, forward slashes, no leading ``./``."""
    out = path.replace("\\", "/")
    while out.startswith("./"):
        out = out[2:]
    return out


def code_text(path: Path) -> str | None:
    """Source with COMMENTS AND DOCSTRINGS REMOVED.

    **THIS IS THE DIFFERENCE BETWEEN A DEPENDENCY AND A CITATION, and it was
    measured.** Scanning raw source for the census ledger's name selected 93
    of 170 test files, because ``linkedin_server/readonly.py:2045`` mentions
    it in a ``#`` comment and ``linkedin_server/server.py:185`` quotes it in a
    module docstring. Neither module opens that file; both are prose. Follow a
    prose mention and the walk reaches every test that imports the package,
    which is most of them.

    In this repository that distinction is unusually load-bearing: the house
    style puts long argued docstrings on nearly every file, so raw text is
    mostly ESSAY, and an essay names everything it reasons about. A path that
    survives this strip is one the CODE holds.

    **ON A PARSE FAILURE IT RETURNS THE RAW SOURCE**, which over-couples. A
    parse error must widen the plan, never narrow it -- the whole point of
    this module is that silently checking less is the defect.

    **ON A READ FAILURE IT RETURNS None, NOT ``""``**, and that distinction
    was not mine: ``tests/test_an_outage_is_never_filed_as_an_absence.py``
    refused this file's first version at ``impact_gate.py:225`` for returning
    an empty string out of an ``except OSError``. It was right, and it was
    right about THIS module in particular. An empty string means "this file
    mentions nothing", a file that cannot be read means "unknown" -- and the
    two are the same value to every caller, so an I/O error would have
    silently REMOVED a candidate from the plan. That is the exact failure
    this gate exists to prevent, reproduced inside the gate. None forces the
    caller to decide, and the caller widens.
    """
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return src
    # An expression statement whose whole value is a string literal is a
    # string that is evaluated and thrown away -- which is precisely what a
    # docstring is, including the ``#:``-style attribute docstrings used
    # throughout this repo.
    prose: set[tuple[int, int]] = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)):
            prose.add((node.value.lineno, node.value.col_offset))
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError, ValueError):
        return src
    kept: list[str] = []
    for tok in tokens:
        if tok.type == tokenize.COMMENT:
            continue
        if tok.type == tokenize.STRING and tok.start in prose:
            continue
        kept.append(tok.string)
    # One token per line, so nothing is glued into a match that the source
    # does not actually contain.
    return "\n".join(kept)


#: Ways a file can read a WHOLE DIRECTORY. The ancestor-directory rule below
#: fires only for a file that shows one of these, because holding a directory
#: and WALKING it are different claims -- see :func:`data_tokens`.
#:
#: ``walk`` is NOT in this list and the omission is deliberate and measured:
#: a bare ``\bwalk\b`` matched ``ast.walk`` in
#: ``tests/test_a_covered_row_names_the_artifact_that_covers_it.py``, which
#: traverses a syntax tree and no directory at all. It is spelled ``os.walk``
#: here so that the two cannot be confused. A verb list assembled by
#: association rather than by checking what it matches is how a selector
#: quietly becomes a rubber stamp in the generous direction.
_SWEEP_VERBS = re.compile(
    r"\b(?:rglob|glob|iterdir|scandir|listdir)\b|os\.walk|ls-files|ls_files"
)


def data_tokens(rel_path: str) -> tuple[list[re.Pattern[str]], list[re.Pattern[str]]]:
    """``(file_patterns, directory_patterns)`` matching a CODE reference.

    The two are returned separately because they carry different burdens of
    proof, and the caller applies the second only to a file that demonstrably
    sweeps. See below.

    THE BASENAME IS THE LOAD-BEARING ONE, and that is not laziness. A path
    read at runtime is usually composed -- ``ROOT / "_audit" / "<name>"`` --
    so the repo-relative string appears nowhere in the source. The last
    segment is the only token that survives that composition.

    Bounded on both sides so it stays a reference rather than a coincidence:
    ``jobs.md`` matches ``_census/jobs.md`` and ``"jobs.md"`` but not
    ``subjobs.md``. The left guard deliberately ALLOWS ``/`` and ``"``,
    because a reference is normally preceded by exactly those.

    **THE ANCESTOR DIRECTORIES ARE HERE FOR THE SWEEP READERS**, which are
    otherwise invisible to every rule in this file.
    ``tests/test_a_correction_is_findable_from_the_claim.py`` holds
    ``AUDIT = ROOT / "_audit"`` and walks the tree underneath it, so it reads
    every document in there and NAMES NOT ONE OF THEM. A rule matching only a
    file's own name misses it completely, and it is a real reader: it is the
    test that enforces the corrections vocabulary those documents carry.

    **BUT HOLDING A DIRECTORY IS NOT READING IT, and conflating the two cost
    real precision.** Measured: with the directory token applied to anything
    that merely mentions the folder, an edit to one audit document dragged in
    ``tests/test_no_committed_identity.py`` -- because ``tests/repo_paths.py``
    contains ``Path("_audit") / "_sanitisation_key.json"``. That names the
    folder in order to reach ONE named file inside it, and no edit to a
    different document in that folder can touch it. Same shape as
    ``SERVER = REPO / "linkedin_server" / "server.py"``.

    So the directory patterns come back separately and the caller fires them
    only at a file that also shows a SWEEP VERB. The narrowing is sound
    because it touches only this one token class: a file that names the actual
    changed file, or its full path, still couples through the patterns above
    regardless of whether it sweeps.
    """
    rel_path = _rel(rel_path)
    parts = rel_path.split("/")
    base = parts[-1]
    files = [
        re.compile(re.escape(rel_path)),
        re.compile(re.escape(rel_path.replace("/", "\\"))),
    ]
    if base and base != rel_path:
        files.append(
            re.compile(r"(?<![A-Za-z0-9_.-])" + re.escape(base) + r"(?![A-Za-z0-9])")
        )
    # Each ancestor directory, as a QUOTED segment. Quoted, because after the
    # prose strip a bare identifier is a variable and a quoted one is a path
    # segment, and only the second is evidence that this file addresses that
    # directory at all.
    dirs: list[re.Pattern[str]] = []
    for depth in range(1, len(parts)):
        segment = parts[depth - 1]
        if not segment:
            continue
        dirs.append(re.compile(r"[\"']" + re.escape(segment) + r"[\"']"))
        if depth > 1:
            joined = "/".join(parts[:depth])
            dirs.append(re.compile(r"[\"']" + re.escape(joined) + r"[\"']"))
    return files, dirs


def import_names(rel_path: str) -> set[str]:
    """The dotted names under which a staged ``.py`` file can be imported.

    ``scripts/`` gets a BARE name as well as a dotted one because test files
    reach it by ``sys.path.insert(0, str(ROOT / "scripts"))`` and then a plain
    ``import build_blocker_map``. That is precisely the hop the census case
    needs, and a dotted-only index would miss it.
    """
    rel_path = _rel(rel_path)
    if not rel_path.endswith(".py"):
        return set()
    parts = rel_path[:-3].split("/")
    names = {".".join(parts)}
    if parts[0] in ("scripts", "tests"):
        # Both are put on sys.path by files in this repo, so the bare module
        # name is a real import target.
        names.add(parts[-1])
    if parts[-1] == "__init__":
        names.add(".".join(parts[:-1]))
    return {n for n in names if n}


# --------------------------------------------------------------------------
# The import index, built by parsing rather than grepping.
# --------------------------------------------------------------------------

def _imports_of(path: Path) -> set[str] | None:
    """Every dotted module name a file imports, off the AST. None if unknown.

    ``from linkedin_server import readonly`` yields BOTH ``linkedin_server``
    and ``linkedin_server.readonly``, because the alias in a ``from X import
    Y`` may be a submodule and the syntax alone cannot say which. Recording
    both over-couples slightly and under-couples never, which is the correct
    direction of error for a gate.

    **UNREADABLE OR UNPARSEABLE RETURNS None, NOT AN EMPTY SET.** An empty set
    says "this file imports nothing", which is an answer; failing to read the
    file is the ABSENCE of an answer, and collapsing the two would let an I/O
    error quietly drop a candidate out of the plan. The caller widens on None.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, ValueError):
        return None
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import; not used across these roots
                continue
            if node.module:
                names.add(node.module)
                names.add(node.module.split(".")[0])
                for alias in node.names:
                    names.add(f"{node.module}.{alias.name}")
    return names


def candidate_files() -> list[str]:
    """Every python file that can participate in a coupling, repo-relative."""
    out: list[str] = []
    for directory, prefix in (
        (TESTS_DIR, "tests/"),
        (SCRIPTS_DIR, "scripts/"),
        (PACKAGE_DIR, "linkedin_server/"),
    ):
        if directory.is_dir():
            out.extend(prefix + p.name for p in sorted(directory.glob("*.py")))
    return out


class Corpus:
    """The python files, read once and analysed only where it matters.

    THE LATENCY ARGUMENT APPLIES TO THE ANALYSER TOO, and it nearly did not.
    Stripping prose from all ~400 python files costs a tokenize and an AST
    parse each: 5.2s measured, against roughly 3s for the tests the census
    case actually needs to run. **An analyser that costs more than the suite
    it scopes has moved the latency rather than removed it** -- the same
    O(suite) shape this module exists to escape, wearing the costume of the
    fix.

    So the expensive readings are LAZY and guarded by a cheap, SOUND reject: a
    match in stripped source is necessarily a match in raw source, and a file
    that imports ``X`` necessarily contains the substring ``X``. Raw text
    rules out almost everything for the price of a read; only the survivors
    are parsed. Soundness is what makes it a filter rather than a narrowing --
    it can only produce FALSE candidates for the oracle to reject, never hide
    a true one.
    """

    def __init__(self) -> None:
        self.files = candidate_files()
        self._raw: dict[str, str | None] = {}
        self._code: dict[str, str | None] = {}
        self._imports: dict[str, set[str] | None] = {}
        #: The corpus-wide floor, memoised -- it takes no input from the diff,
        #: so deriving it twice in one run is pure cost.
        self.floor: list[tuple[str, str]] | None = None

    def raw(self, rel: str) -> str | None:
        """Raw source, or None if it could not be read. NEVER ``""``."""
        if rel not in self._raw:
            try:
                self._raw[rel] = (REPO / rel).read_text(
                    encoding="utf-8", errors="replace")
            except OSError:
                self._raw[rel] = None
        return self._raw[rel]

    def code(self, rel: str) -> str | None:
        if rel not in self._code:
            self._code[rel] = code_text(REPO / rel)
        return self._code[rel]

    def imports(self, rel: str) -> set[str] | None:
        if rel not in self._imports:
            self._imports[rel] = _imports_of(REPO / rel)
        return self._imports[rel]


def is_test_target(rel: str) -> bool:
    """Is this a file pytest would actually run?

    ``tests/conftest.py``, ``tests/leakwalk.py`` and ``tests/repo_paths.py``
    live in ``tests/`` and are NOT targets -- they are helpers other tests
    import. Handing one to pytest collects nothing, so a plan that contains
    one is a plan that silently checks less than its own file count claims.
    They stay in the graph as things to expand THROUGH, which is what they
    are.
    """
    return rel.startswith("tests/") and rel.rsplit("/", 1)[-1].startswith("test_")


def test_files_on_disk() -> list[str]:
    """``tests/test_*.py``. The exact, free denominator."""
    if not TESTS_DIR.is_dir():
        return []
    return ["tests/" + p.name for p in sorted(TESTS_DIR.glob("test_*.py"))]


# --------------------------------------------------------------------------
# The impact set.
# --------------------------------------------------------------------------

#: A test is CORPUS-WIDE when its file enumeration takes no input from the
#: diff: it walks the tracked set, or the repository root, or two or more
#: top-level source folders. Such a test is coupled to EVERYTHING and
#: therefore to nothing in particular, so no name-based or import-based
#: analysis will ever select it -- and these are exactly the guards whose
#: silence is most expensive, because one of them is the identity gate's test
#: half.
_TOPLEVEL_FOLDERS = ("scripts", "linkedin_server", "tests", "_audit")
_TRACKED_SET = re.compile(r"ls-files|ls_files")
_ROOT_WALK = re.compile(r"(?:REPO|_ROOT|ROOT)\s*\.\s*rglob")


def always_run_files(corpus: "Corpus") -> list[tuple[str, str]]:
    """``(path, why)`` for every corpus-wide sweep. DERIVED, never listed.

    **THIS CATEGORY EXISTS BECAUSE A SIBLING WAVE SHIPPED RED TWICE IN ONE
    DAY WITHOUT IT.** Its own diagnosis, 2026-09-20: *"a local selection that
    ran the files I touched and their neighbours and missed guards whose
    names connect to nothing I was working on --
    ``test_page_text_is_never_printed.py``, ``test_no_committed_identity.py``."*

    That is not a coupling bug and widening the coupling rules cannot fix it.
    ``test_no_committed_identity.py`` sweeps every tracked file INCLUDING
    ``.md`` and ``.tsv``, so a census edit can trip it -- while the file names
    no census document and imports no module, which is precisely why an
    impact analysis cannot see it. The relationship is real and maximal; it
    is the ANALYSIS that has no handle on it.

    So these run unconditionally, and the cost is the argument for it: 13
    files, 1797 tests, 25.6s (measured 2026-09-20, ``-n auto``). Omitting
    them to save that is how a fast gate ships a real name into published
    history, and a name in served history is the least reversible thing this
    repository can do.

    DERIVED RATHER THAN LISTED, for the reason the boundary gate already
    gives about its own coupling: a hand-written pair is correct for the
    instance that produced it and blind to the next one. The two proven
    members are pinned by a control in
    ``tests/test_impact_gate_selects_data_dependencies.py``, which FAILS if
    this detector ever stops finding them -- so the derivation is checked
    rather than believed.
    """
    if corpus.floor is not None:
        return corpus.floor
    out: list[tuple[str, str]] = []
    for rel in test_files_on_disk():
        # SOUND PREFILTER, same trick as everywhere else in this module: each
        # condition below implies its own weakened form over RAW source, so a
        # file failing all three weakened forms cannot satisfy any strict one,
        # and the expensive prose strip is skipped for it.
        raw = corpus.raw(rel)
        if raw is not None:
            folders_raw = sum(
                1 for f in _TOPLEVEL_FOLDERS
                if re.search(r"[\"']" + f + r"[\"']", raw)
            )
            if not (_TRACKED_SET.search(raw)
                    or _ROOT_WALK.search(raw)
                    or (_SWEEP_VERBS.search(raw) and folders_raw >= 2)):
                continue
        code = corpus.code(rel)
        if code is None:
            # Unreadable: cannot rule it out, so it joins the floor. Widening
            # on an unknown, as everywhere else in this module.
            out.append((rel, "UNREADABLE, treated as corpus-wide"))
            continue
        why: list[str] = []
        if _TRACKED_SET.search(code):
            why.append("enumerates the tracked file set")
        if _ROOT_WALK.search(code):
            why.append("walks the repository root")
        if _SWEEP_VERBS.search(code):
            folders = [f for f in _TOPLEVEL_FOLDERS
                       if re.search(r"[\"']" + f + r"[\"']", code)]
            if len(folders) >= 2:
                why.append("sweeps " + " + ".join(folders))
        if why:
            out.append((rel, "; ".join(why)))
    corpus.floor = out
    return out


@dataclass(frozen=True)
class Pairing:
    """One corpus-wide SWEEP and the script that answers it on the change.

    The unit is a SWEEP, not a file, and that distinction is the whole design.
    ``tests/test_no_committed_identity.py`` is 18.0s and MIXED: 546
    parametrised per-file shape cases, a control that shells the exact-value
    sweep over the whole tree, a genuinely SET-SHAPED cross-file pairing test,
    and forty small controls. Substituting the FILE would move the set-shaped
    half and every control to CI as collateral. Substituting the two SWEEPS
    leaves the file in the plan with ``--deselect`` and moves nothing else.
    """

    #: The pytest node id whose whole-tree enumeration the script replaces.
    #: Deselecting the bare name of a parametrised test removes the whole
    #: group, which is what makes this cheap to express.
    node: str
    #: The incremental script. Contract: 0 clean, 1 refused, anything else
    #: CANNOT ANSWER -- and see ``fails_open_token``.
    script: str
    #: A literal this script prints when it has DECLINED to check rather than
    #: checked and found nothing. ``pre_commit_identity_gate.py`` exits 0 and
    #: says ALLOWING when its gitignored wordlist is absent, which is a
    #: documented deliberate fail-open, and a fail-open is not an answer. A
    #: sibling that says this word gets its sweep restored to the plan.
    fails_open_token: str | None = None


#: **THE PAIRING REGISTER: corpus-wide sweep -> the script that checks THE SAME
#: PROPERTY on the change set instead of on the tree.**
#:
#: A corpus-wide guard is expensive because its denominator is the corpus. Some
#: of them do not need that denominator to be useful LOCALLY, because the
#: property is PER-FILE: "no committable file carries X" is preserved by
#: checking only the files this commit writes, PROVIDED it already held on the
#: tree they are landing on.
#:
#: **THAT PROVISO IS A BASE CASE AND IT IS NOT OPTIONAL.** A paired sweep is an
#: INDUCTION STEP. Its base case is the WHOLE-TREE form, which is not deleted
#: and does not move: it stays in ``tests/`` and runs on every push, on three
#: platforms, in ``.github/workflows/ci.yml``. Local gets the fast signal; CI
#: remains the certifier. Nothing local guarantees the previous tree was clean
#: -- a ``--no-verify`` commit, a guard disarmed in a worktree, a merge from a
#: branch that never ran it -- so a reader who deletes a swept guard because
#: its paired script is green has removed the base case from an induction and
#: will not find out until it matters.
#:
#:     base case        the whole-tree sweep, in CI, on every push
#:     induction step   the script below, locally, on every commit
#:
#: A pair is admitted only when BOTH halves exist and the fast half has been
#: SHOWN FAILING on content the slow half catches -- see
#: ``tests/test_staged_identity_shapes.py``, which plants three shapes at
#: runtime in a throwaway repository and asserts both halves see each one. A
#: fast check that has never been seen red certifies nothing, and a register
#: of such checks manufactures confidence at scale.
#:
#: WHAT IS NOT IN HERE IS ALSO A RESULT. A sweep whose property is about the
#: SET -- a uniqueness, a total, a pairing between two files, an inventory that
#: must match exactly -- cannot be answered from staged content, because
#: staging file A can break an invariant about (A, B) where B was never
#: staged. Those stay whole-tree and stay in the floor. They are named in
#: ``_audit/2026-09-20-the-flat-gate.md`` with the reason, rather than worked
#: around.
_INCREMENTAL_SIBLINGS: dict[str, tuple[Pairing, ...]] = {
    # BOTH parametrised families come off ONE script: each is a per-file rule
    # over the same 170-file glob, and the script answers both in one pass. Two
    # entries rather than one because the unit of substitution is a SWEEP -- the
    # file's other 31 cases, including its own shown-failing controls, keep
    # running here.
    "tests/test_navigation_is_never_derived.py": (
        Pairing(
            node="tests/test_navigation_is_never_derived.py"
                 "::test_no_navigation_is_aimed_at_a_url_the_browser_chose",
            script="scripts/staged_navigation_guard.py",
        ),
        Pairing(
            node="tests/test_navigation_is_never_derived.py"
                 "::test_no_navigation_derived_value_reaches_an_output_sink",
            script="scripts/staged_navigation_guard.py",
        ),
    ),
    "tests/test_no_committed_identity.py": (
        # The SHAPE sweep: one assertion parametrised over 545 committable
        # files. 17,996 ms for the file whole; 446 ms for the change set.
        Pairing(
            node="tests/test_no_committed_identity.py"
                 "::test_no_tracked_file_carries_a_real_identifier",
            script="scripts/staged_identity_shapes.py",
        ),
        # The EXACT-VALUE sweep, hiding inside a control that shells
        # scripts/sweep_tracked_for_identity.py over the whole tree: 7,820 ms
        # of the file's time in one test. **ITS INCREMENTAL HALF ALREADY
        # EXISTED** -- scripts/pre_commit_identity_gate.py, 208 ms, shipped as
        # a git hook and never joined up to the gate. This line is the join.
        Pairing(
            node="tests/test_no_committed_identity.py"
                 "::test_the_exact_value_sweep_actually_runs",
            script="scripts/pre_commit_identity_gate.py",
            fails_open_token="ALLOWING",
        ),
    ),
}

_SIBLING_CLEAN, _SIBLING_REFUSED = 0, 1


def pairings_for(floor: list[str]) -> list[Pairing]:
    """Every registered pairing whose sweep is in this run's floor.

    A pairing whose SCRIPT is missing from disk is skipped, so the sweep stays
    in the plan. A register entry that silently dropped a guard because
    somebody renamed a file would be this repository's own "check that cannot
    fail", with the check missing altogether.
    """
    out: list[Pairing] = []
    for rel in floor:
        for pair in _INCREMENTAL_SIBLINGS.get(rel, ()):
            if (REPO / pair.script).exists():
                out.append(pair)
            else:
                print(f"impact-gate: {pair.script} is registered as the fast "
                      f"half of {pair.node} and is NOT ON DISK. Keeping the "
                      "whole-tree sweep.", file=sys.stderr)
    return out


def run_siblings(
    pairings: list[Pairing],
) -> tuple[list[tuple[Pairing, str]], list[Pairing], list[Pairing], float]:
    """``(refusals, answered, fell_back, seconds)``.

    ``fell_back`` are the pairings whose script could not answer -- a bad exit
    code, or a documented fail-open. Their sweeps go back in the pytest plan,
    which is the entire reason a third outcome exists. Every other gate in this
    repository fails OPEN because there is nowhere better to fail to; a paired
    sweep HAS somewhere better, so it fails to the SLOW PATH.
    """
    refusals: list[tuple[Pairing, str]] = []
    answered: list[Pairing] = []
    fell_back: list[Pairing] = []
    started = time.monotonic()
    # ONE RUN PER SCRIPT, NOT PER SWEEP. A script can answer several sweeps --
    # the navigation one answers two -- and running it twice would pay its
    # interpreter twice to compute the same verdict, which is the cost this
    # whole mechanism exists to remove.
    verdicts: dict[str, tuple[int, str]] = {}
    for pair in pairings:
        if pair.script not in verdicts:
            proc = subprocess.run(
                [str(PYTHON), str(REPO / pair.script)],
                cwd=REPO, capture_output=True, text=True,
                encoding="utf-8", errors="replace",
            )
            verdicts[pair.script] = (
                proc.returncode, (proc.stderr or "") + (proc.stdout or ""))
        code, output = verdicts[pair.script]
        if code == _SIBLING_REFUSED:
            refusals.append((pair, output))
        elif code != _SIBLING_CLEAN:
            fell_back.append(pair)
            print(f"impact-gate: {pair.script} could not answer (exit "
                  f"{code}); RESTORING its whole-tree sweep.",
                  file=sys.stderr)
            for line in output.strip().splitlines()[:4]:
                print("      " + line, file=sys.stderr)
        elif pair.fails_open_token and pair.fails_open_token in output:
            # EXIT 0 IS NOT ALWAYS AN ANSWER. This one declined.
            fell_back.append(pair)
            print(f"impact-gate: {pair.script} exited 0 but FAILED OPEN "
                  f"(said {pair.fails_open_token!r}), which is a decline, not "
                  "a clean answer; RESTORING its whole-tree sweep.",
                  file=sys.stderr)
        else:
            answered.append(pair)
    return refusals, answered, fell_back, time.monotonic() - started


@dataclass
class Impact:
    """What a change can reach, and the trail that says how it got there.

    ``selected`` and ``always_run`` are kept APART on purpose. Merging them
    would make the union non-empty on every invocation, and the loud-empty
    law -- an empty selection must never read as a pass -- would be silently
    satisfied by the floor for the rest of this gate's life. The floor is a
    guarantee about the corpus; it is not evidence that the analyser worked.
    """

    #: Coupled to the diff by name, import, constant or data path.
    selected: list[str] = field(default_factory=list)
    #: The corpus-wide floor, which takes no input from the diff at all.
    always_run: list[str] = field(default_factory=list)
    #: ``(from, to, why)`` -- the provenance, so the report can EXPLAIN itself
    #: rather than assert a set. A selector nobody can audit is a selector
    #: nobody should trust.
    edges: list[tuple[str, str, str]] = field(default_factory=list)
    #: Staged paths that force the full suite, each with its reason.
    triggers: list[tuple[str, str]] = field(default_factory=list)

    @property
    def test_files(self) -> list[str]:
        """Everything that will actually be handed to pytest."""
        return sorted(set(self.selected) | set(self.always_run))

    def explain(self, target: str) -> list[str]:
        return [f"{a} -> {b} ({why})" for a, b, why in self.edges if b == target]


def impact_set(
    paths: list[str],
    *,
    data_coupling: bool = True,
    import_coupling: bool = True,
    constant_coupling: bool = True,
    always_run: bool = True,
    max_hops: int = 4,
) -> Impact:
    """Test files a change to ``paths`` can break.

    The three keyword switches exist so a CONTROL can turn one rule OFF and
    watch the selector stop finding what it must find. A check that cannot be
    shown failing certifies nothing, and a selector whose rules cannot be
    disarmed individually cannot be shown failing at all. See
    ``tests/test_impact_gate_selects_data_dependencies.py``, which asserts
    both arms.
    """
    impact = Impact()
    paths = [_rel(p) for p in paths]

    for rel in paths:
        if rel in _GLOBAL_TRIGGERS:
            impact.triggers.append(
                (rel, "changes runner-wide behaviour no name can express")
            )

    corpus = Corpus()
    candidates = corpus.files

    found: set[str] = set()
    frontier: list[str] = []
    seen: set[str] = set(paths)

    def reached(source: str, rel: str, why: str, nxt: list[str]) -> None:
        impact.edges.append((source, rel, why))
        if is_test_target(rel):
            found.add(rel)
        elif rel not in seen:
            seen.add(rel)
            nxt.append(rel)

    def importers_of(source: str, nxt: list[str]) -> None:
        names = import_names(source)
        if not names:
            return
        # CHEAP REJECT FIRST. A file that imports ``X`` must contain the
        # literal ``X`` somewhere in its raw source, so a substring test over
        # text already in memory rules out almost every candidate before any
        # of them is parsed. The AST is the ORACLE, not the filter.
        needles = names | {n.rsplit(".", 1)[-1] for n in names}
        for rel in candidates:
            if rel == source or rel in found:
                continue
            raw = corpus.raw(rel)
            if raw is None:
                reached(source, rel, "UNREADABLE, coupled defensively", nxt)
                continue
            if not any(needle in raw for needle in needles):
                continue
            imported = corpus.imports(rel)
            if imported is None:
                reached(source, rel, "UNPARSEABLE, coupled defensively", nxt)
            elif names & imported:
                reached(source, rel, "imports it", nxt)

    # --- HOP 0: from what was actually changed. --------------------------
    # BOTH kinds of edge fire here, and the text edge fires ONLY here. See
    # the comment on the loop below for why that asymmetry is the whole
    # difference between a selector and a rubber stamp in the other
    # direction.
    for source in paths:
        if data_coupling:
            file_pats, dir_pats = data_tokens(source)
            for rel in candidates:
                if rel == source or rel in found:
                    continue
                # CHEAP REJECT FIRST, then the expensive, correct answer.
                # Stripping prose costs a tokenize plus an AST parse, and over
                # the whole corpus that is 5.2s -- more than the tests it
                # saves, which would make the analyser the new latency. But a
                # match in the STRIPPED text is always also a match in the raw
                # text, so the raw scan is a sound filter and the strip runs
                # only on the handful that survive it.
                raw = corpus.raw(rel)
                if raw is None:
                    # UNKNOWN IS NOT ABSENT. A file that cannot be read might
                    # name this path; dropping it here would narrow the plan
                    # on an I/O error, which is the failure this whole module
                    # is about.
                    reached(source, rel, "UNREADABLE, coupled defensively",
                            frontier)
                    continue
                if not any(pat.search(raw) for pat in file_pats + dir_pats):
                    continue
                code = corpus.code(rel)
                if code is None:
                    reached(source, rel, "UNREADABLE, coupled defensively",
                            frontier)
                elif any(pat.search(code) for pat in file_pats):
                    reached(source, rel, "names the path", frontier)
                elif (_SWEEP_VERBS.search(code)
                        and any(pat.search(code) for pat in dir_pats)):
                    reached(source, rel, "sweeps the directory", frontier)
        if import_coupling and source.endswith(".py"):
            importers_of(source, frontier)

    # --- HOPS 1..N: IMPORTS ONLY. ----------------------------------------
    # **THE TEXT EDGE IS DELIBERATELY NOT TRANSITIVE, and this was MEASURED
    # rather than reasoned.** The first version followed text matches at every
    # hop. On the census ledger it selected 158 of 170 test files in 14.7s --
    # a "selector" that returns 93% of the suite is not selecting, it is
    # laundering a full run through a narrowing story, which is worse than an
    # honest full run because it claims to have reasoned.
    #
    # The mechanism: a probe script MENTIONS the ledger in a docstring, so it
    # joins the frontier; its own basename then matches prose in dozens of
    # unrelated files, and two hops later everything names everything. Prose
    # mentions are not dependencies.
    #
    # The asymmetry is principled, not a tuning knob. "Who READS this data
    # file" is answerable only by looking for the path, because the path is
    # composed at runtime and there is nothing else to look for. "Who DEPENDS
    # on this module" is answerable exactly, by reading its importers. Once
    # the walk is in python-land the precise instrument exists, so using the
    # blunt one there buys nothing and costs the whole property.
    if import_coupling:
        for _ in range(max_hops):
            if not frontier:
                break
            nxt: list[str] = []
            for source in frontier:
                importers_of(source, nxt)
            frontier = nxt

    # --- THE STAGED TESTS THEMSELVES, and the shipped constant rule --------
    staged_tests = [p for p in paths if p.startswith("tests/") and p.endswith(".py")]
    for rel in staged_tests:
        if is_test_target(rel) and (REPO / rel).exists():
            found.add(rel)
            impact.edges.append((rel, rel, "staged"))

    if constant_coupling and staged_tests:
        # THE SHIPPED RULE, CALLED NOT COPIED. It catches a class neither rule
        # above can see: a structure defined in one test file and pinned by a
        # LITERAL COPY in another, with no import between them.
        for rel in boundary.coupled_test_files(staged_tests):
            if rel not in found:
                found.add(rel)
                impact.edges.append(
                    (staged_tests[0], rel, "pins a shared module-level constant")
                )

    # --- THE PACKAGE INVARIANT ---------------------------------------------
    # Carried over from the boundary gate because its receipt still holds:
    # when a file is ADDED to linkedin_server/, the package-level invariants
    # are the tests most likely to be broken by it, and tests/test_readonly.py
    # auto-includes new modules by GLOB -- so nothing names the new file and
    # neither an import rule nor a text rule can reach it.
    if any(p.startswith("linkedin_server/") and p.endswith(".py") for p in paths):
        if (REPO / "tests/test_readonly.py").exists():
            found.add("tests/test_readonly.py")
            impact.edges.append(
                ("linkedin_server/", "tests/test_readonly.py",
                 "package-level invariant, auto-globs new modules")
            )

    impact.selected = sorted(f for f in found if (REPO / f).exists())

    # THE FLOOR, added LAST and kept in its own field. It is not a selection
    # and must never be counted as one.
    if always_run:
        for rel, why in always_run_files(corpus):
            if (REPO / rel).exists():
                impact.always_run.append(rel)
                impact.edges.append(("<corpus-wide>", rel, why))
    return impact


# --------------------------------------------------------------------------
# Staged paths, and the denominator.
# --------------------------------------------------------------------------

def changed_paths(
    against: str | None = None,
) -> tuple[list[str], list[str]] | None:
    """``(present, deleted)`` repo-relative paths for this change.

    Reads the INDEX by default, for the boundary gate's reason: the thing
    being judged is what this commit would write, and in a tree with several
    concurrent writers the working tree is a different object.

    **DELETIONS ARE RETURNED, NOT DROPPED.** A vanished file is the one case
    where the name-based rules are at their most useful and any content-based
    rule is useless: nothing can be read out of a file that is gone, but
    everything that NAMES it is about to break. So a deletion contributes its
    tokens and is simply never expanded.

    **AND IT RETURNS None WHEN GIT COULD NOT ANSWER**, rather than an empty
    pair. "Nothing is staged" and "I could not find out what is staged" are
    different findings that an empty list renders identical, and the second
    one silently becomes a pass. Same law as :func:`code_text`; the caller
    reports the outage instead of reading it as an all-clear.
    """
    argv = ["git", "diff", "--cached", "--name-status"]
    if against:
        argv = ["git", "diff", "--name-status", against]
    try:
        proc = subprocess.run(argv, cwd=REPO, capture_output=True, text=True,
                              encoding="utf-8")
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    present: list[str] = []
    deleted: list[str] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        path = parts[-1]
        (deleted if status.startswith("D") else present).append(_rel(path))
    return present, deleted


def suite_size() -> dict | None:
    """The cached test-count denominator, or None. NEVER a guess.

    Cached because deriving it costs a 36.2s collection, which is most of the
    latency this gate exists to remove. Stamped with the commit it was taken
    at so the report can say how old the number is instead of implying it is
    current.
    """
    try:
        return json.loads(_SUITE_SIZE_CACHE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def recount_suite() -> dict:
    """Re-derive the denominator by collecting the suite. Slow on purpose."""
    started = time.monotonic()
    proc = subprocess.run(
        [str(PYTHON), "-m", "pytest", "tests/", "-q", "-p", "no:randomly",
         "--collect-only"],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8",
    )
    match = re.search(r"(\d+) tests? collected", proc.stdout)
    if not match:
        raise SystemExit("impact-gate: could not read a collected count from "
                         "pytest; NOT writing a number I cannot derive.")
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                          capture_output=True, text=True, encoding="utf-8")
    payload = {
        "tests": int(match.group(1)),
        "files": len(test_files_on_disk()),
        "taken_at": time.strftime("%Y-%m-%d"),
        "head": head.stdout.strip() or "unknown",
        "collect_seconds": round(time.monotonic() - started, 1),
    }
    _SUITE_SIZE_CACHE.write_text(json.dumps(payload, indent=2) + "\n",
                                 encoding="utf-8")
    return payload


# --------------------------------------------------------------------------
# Running, and reporting honestly.
# --------------------------------------------------------------------------

def run_plan(
    plan: list[str], full: bool, deselect: list[str] | None = None,
) -> tuple[int, str, float]:
    """Run the plan. Returns ``(returncode, stdout, seconds)``.

    ``deselect`` holds node ids whose whole-tree sweep a paired script has
    already answered on the change set -- see :data:`_INCREMENTAL_SIBLINGS`.
    Deselecting a NODE rather than dropping the FILE is deliberate: these files
    are mixed, and every control and every set-shaped assertion beside the
    sweep keeps running locally. It is also empty whenever ``full`` is set, so
    a widened run stays exhaustive.
    """
    targets = ["tests/"] if full else [str(REPO / name) for name in plan]
    skips: list[str] = []
    for node in (deselect or ()):
        skips += ["--deselect", node]
    parallel: list[str] = []
    if full or len(plan) >= _PARALLEL_FILE_THRESHOLD:
        # ``--dist loadfile`` KEEPS EACH FILE ON ONE WORKER. These files carry
        # module-level state and frozen captures; splitting one across workers
        # is an isolation change, and an isolation change that alters a verdict
        # is reporting on the isolation rather than on the code.
        parallel = ["-n", "auto", "--dist", "loadfile"]
    started = time.monotonic()
    proc = subprocess.run(
        [str(PYTHON), "-m", "pytest", *targets, "-q", "-p", "no:randomly",
         "--tb=line", *skips, *parallel],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8",
    )
    if parallel and proc.returncode not in (0, 1):
        # A MISSING PLUGIN MUST NOT BECOME A REFUSAL, and it must not become a
        # silent one either.
        print("impact-gate: parallel run failed to start "
              f"(exit {proc.returncode}); RETRYING SERIALLY.", file=sys.stderr)
        started = time.monotonic()
        proc = subprocess.run(
            [str(PYTHON), "-m", "pytest", *targets, "-q", "-p", "no:randomly",
             "--tb=line", *skips],
            cwd=REPO, capture_output=True, text=True, encoding="utf-8",
        )
    return proc.returncode, proc.stdout, time.monotonic() - started


_COUNT_RE = re.compile(r"(\d+) (passed|failed|xfailed|xpassed|skipped|error)")


def tests_run(stdout: str) -> int | None:
    """How many tests the run actually executed, off pytest's own summary.

    Returns None when the summary cannot be read, and the caller then prints
    that it does not know rather than an estimate. **The surface may not print
    a claim it cannot derive.**
    """
    tail = stdout.strip().splitlines()
    for line in reversed(tail[-6:]):
        hits = _COUNT_RE.findall(line)
        if hits:
            return sum(int(n) for n, _ in hits)
    return None


def report_scope(plan: list[str], ran: int | None, seconds: float) -> None:
    """Say what was NOT checked. Printed on PASS as loudly as on FAIL.

    THE REASON THIS FUNCTION EXISTS. A gate that prints "PASS" after running
    12 of 6094 tests has told a dangerous half-truth: the word means
    "everything I check is green" to the writer and "this change is fine" to
    the reader, and the gap between those is where a scoped gate does its
    damage. So the scope is not a footnote, it is part of the verdict.
    """
    all_files = test_files_on_disk()
    n_files, n_plan = len(all_files), len(plan)
    print("", file=sys.stderr)
    if n_files:
        pct = 100.0 * (n_files - n_plan) / n_files
        print(f"  NOT CHECKED: {n_files - n_plan} of {n_files} test files "
              f"({pct:.1f}% of the suite by file).", file=sys.stderr)
        print("  The corpus-wide guards DID run, so the identity, credential "
              "and page-text", file=sys.stderr)
        print("  sweeps cover the whole tree. Everything else above is "
              "unexamined.", file=sys.stderr)
    size = suite_size()
    if size and isinstance(size.get("tests"), int) and ran is not None:
        total = size["tests"]
        skipped = max(total - ran, 0)
        print(f"  That is roughly {skipped} of {total} tests unrun "
              f"({100.0 * skipped / total:.1f}%), against a suite count taken "
              f"{size.get('taken_at', '?')} at {size.get('head', '?')}.",
              file=sys.stderr)
    elif ran is None:
        print("  Tests executed: UNKNOWN -- pytest's summary could not be "
              "read, so no fraction is claimed here.", file=sys.stderr)
    else:
        print(f"  Tests executed: {ran}. The suite-wide denominator is NOT "
              "cached, so no percentage is claimed. Run --recount for it.",
              file=sys.stderr)
    print(f"  Wall clock: {seconds:.1f}s.", file=sys.stderr)
    print("  THIS IS A LOCAL, WINDOWS-ONLY SIGNAL. CI runs three platforms "
          "and is the", file=sys.stderr)
    print("  certifier; a green gate here is not a reason to shrink that "
          "matrix.", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--paths", nargs="*", default=None,
                        help="explicit repo-relative paths instead of the index")
    parser.add_argument("--against", default=None,
                        help="diff against this ref instead of the index")
    parser.add_argument("--plan-only", action="store_true",
                        help="print the impact set and its provenance; run nothing")
    parser.add_argument("--recount", action="store_true",
                        help="re-derive the suite-size denominator (slow)")
    args = parser.parse_args(argv)

    if args.recount:
        payload = recount_suite()
        print(f"impact-gate: suite is {payload['tests']} tests in "
              f"{payload['files']} files, collected in "
              f"{payload['collect_seconds']}s at {payload['head']}.")
        return 0

    if args.paths is not None:
        present, deleted = list(args.paths), []
    else:
        answer = changed_paths(args.against)
        if answer is None:
            # AN OUTAGE, NOT AN ALL-CLEAR. Fail open, as every gate in this
            # repo does, but never silently: a gate that goes quiet when its
            # own input is unavailable is a gate that has stopped running
            # while still appearing installed.
            print("impact-gate: git could not report what changed, so the "
                  "impact set is UNKNOWN -- not empty. ALLOWING, but nothing "
                  "here has been checked.", file=sys.stderr)
            return 0
        present, deleted = answer
    changed = present + deleted

    if not changed:
        print("impact-gate: nothing staged; nothing to check.", file=sys.stderr)
        return 0

    if not PYTHON.exists() and not args.plan_only:
        print(f"impact-gate: {PYTHON.name} not found; ALLOWING. The guards "
              "still apply -- run them yourself.", file=sys.stderr)
        return 0

    impact = impact_set(changed)
    plan = impact.test_files
    all_files = test_files_on_disk()

    # --- THE ESCAPE HATCH. Three ways to widen, each one spoken aloud. -----
    full = False
    why_full = ""
    if impact.triggers:
        full = True
        names = ", ".join(f"{p} ({why})" for p, why in impact.triggers)
        why_full = ("a staged path this analyser has NO MODEL OF: " + names +
                    ". Scoping would be a guess, so it does not scope.")
    elif not impact.selected:
        # **ON `selected`, NOT ON `plan`.** The corpus-wide floor is never
        # empty, so testing the union here would have made this branch
        # unreachable forever -- the loud-empty law quietly satisfied by a
        # guarantee that says nothing about whether the analyser worked. That
        # is the same "check that cannot fail" this gate was built to avoid,
        # and adding the floor is exactly the change that would have
        # introduced it.
        full = True
        why_full = (
            f"the selector returned an EMPTY impact set for {len(changed)} "
            "changed path(s). An empty selection is indistinguishable from a "
            "broken selector from the outside, so this is never a pass. (The "
            f"{len(impact.always_run)} corpus-wide guards would have run "
            "either way; they are a floor, not a finding.)"
        )
    elif all_files and len(plan) / len(all_files) >= _FULL_SUITE_AT_FRACTION:
        full = True
        why_full = (
            f"the impact set is {len(plan)} of {len(all_files)} test files "
            f"({100.0 * len(plan) / len(all_files):.0f}%), at or above the "
            f"{_FULL_SUITE_AT_FRACTION:.0%} line where running everything "
            "costs about the same and answers more."
        )

    # --- PAIRED GUARDS. The floor's own O(suite) term, answered on the change.
    #
    # DELIBERATELY NOT DONE WHEN WIDENING: a full-suite run already contains
    # every whole-tree form, so substituting there would buy nothing and would
    # remove the certifier from the one run that was asked to be exhaustive.
    candidates = [] if full else pairings_for(impact.always_run)
    answered: list[Pairing] = []
    sibling_seconds = 0.0
    sibling_refusals: list[tuple[Pairing, str]] = []
    if candidates and not args.plan_only:
        sibling_refusals, answered, _fell_back, sibling_seconds = run_siblings(
            candidates)
    elif candidates:
        # --plan-only does not RUN anything, so it reports what WOULD be
        # substituted rather than what was. Saying "answered" about a script
        # that never ran is the kind of claim this gate exists to refuse.
        answered = []
    deselect = [pair.node for pair in answered]

    print(f"impact-gate: {len(changed)} changed path(s) -> "
          f"{len(impact.selected)} SELECTED + {len(impact.always_run)} "
          f"corpus-wide = {len(plan)} test file(s).",
          file=sys.stderr)
    for name in impact.selected[:40]:
        print(f"    {name}", file=sys.stderr)
        for step in impact.explain(name)[:3]:
            print(f"        via {step}", file=sys.stderr)
    if len(impact.selected) > 40:
        print(f"    ... and {len(impact.selected) - 40} more selected",
              file=sys.stderr)
    if impact.always_run:
        print(f"  + {len(impact.always_run)} CORPUS-WIDE guard(s), run "
              "unconditionally -- they sweep the tracked set and take no "
              "input from the diff,", file=sys.stderr)
        print("    so no impact analysis can ever select them. Omitting "
              "them is how a fast gate ships a real name.", file=sys.stderr)
    if candidates and args.plan_only:
        print(f"  {len(candidates)} corpus-wide SWEEP(s) inside them have a "
              "registered incremental half and WOULD be deselected:",
              file=sys.stderr)
        for pair in candidates:
            print(f"      {pair.node}", file=sys.stderr)
            print(f"        -> {pair.script}", file=sys.stderr)
    if answered:
        print(f"  {len(answered)} corpus-wide SWEEP(s) inside them answered "
              f"on the CHANGE rather than the tree, in "
              f"{sibling_seconds * 1000:.0f} ms:", file=sys.stderr)
        for pair in answered:
            print(f"      {pair.node}", file=sys.stderr)
            print(f"        -> {pair.script} (same property, staged content)",
                  file=sys.stderr)
        print("    Their FILES stay in the plan; only the sweeps are "
              "deselected, so every control and every set-shaped assertion "
              "beside them still runs here.", file=sys.stderr)
        print("    THIS IS AN INDUCTION STEP. Its base case is the whole-tree "
              "form, which still runs on every push in CI, on three "
              "platforms.", file=sys.stderr)
        print("    Delete the sweep and this stops being a fast check and "
              "becomes a fast guess.", file=sys.stderr)
    if full:
        print("", file=sys.stderr)
        print(f"  WIDENING TO THE FULL SUITE, because {why_full}",
              file=sys.stderr)

    if args.plan_only:
        return 0

    if sibling_refusals:
        # A PAIRED GUARD IS RED. Reported BEFORE pytest runs, because the
        # committer does not need to wait out a test plan to be told the thing
        # that already decided the answer.
        print("", file=sys.stderr)
        print("REFUSED: a corpus-wide guard is RED on this change, answered "
              "by its incremental half.", file=sys.stderr)
        for pair, output in sibling_refusals:
            print(f"    {pair.script}  (the fast half of {pair.node})",
                  file=sys.stderr)
            for line in output.strip().splitlines():
                print("      " + line, file=sys.stderr)
        print("", file=sys.stderr)
        print("  The whole-tree form is " + ", ".join(
            pair.node for pair, _o in sibling_refusals) +
            " -- run it if you want the full picture.", file=sys.stderr)
        print("  Bypass, if you truly mean to: git commit --no-verify",
              file=sys.stderr)
        return 1

    code, stdout, seconds = run_plan(plan, full, deselect)
    ran = tests_run(stdout)

    if code not in (0, 1):
        # EXIT CODES ABOVE 1 ARE PYTEST FAILING TO RUN -- a collection error,
        # a missing plugin, an internal error. That is infrastructure, not a
        # red guard, and refusing on it is how a gate earns a bypass habit.
        print(f"impact-gate: pytest could not run (exit {code}); ALLOWING. "
              "Output follows.", file=sys.stderr)
        print(stdout[-2000:], file=sys.stderr)
        return 0

    if code == 1:
        print("", file=sys.stderr)
        print("REFUSED: a test this change can reach is RED.", file=sys.stderr)
        for line in stdout.splitlines():
            if line.startswith("FAILED") or " failed" in line:
                print("    " + line, file=sys.stderr)
        print("", file=sys.stderr)
        print("  changed:", file=sys.stderr)
        for name in changed[:20]:
            print("    " + name, file=sys.stderr)
        if not full:
            report_scope(plan, ran, seconds)
        print("  Bypass, if you truly mean to: git commit --no-verify",
              file=sys.stderr)
        return 1

    if full:
        print("", file=sys.stderr)
        print(f"  PASS over the FULL SUITE ({ran if ran is not None else '?'} "
              f"tests) in {seconds:.1f}s.", file=sys.stderr)
        print("  Still windows-only. CI runs three platforms and remains the "
              "certifier.", file=sys.stderr)
        return 0

    print("", file=sys.stderr)
    print(f"  PASS over the {len(plan)} file(s) above"
          f"{'' if ran is None else f' ({ran} tests)'}"
          " -- AND OVER NOTHING ELSE.", file=sys.stderr)
    report_scope(plan, ran, seconds)
    return 0


if __name__ == "__main__":
    sys.exit(main())
