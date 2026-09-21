"""OBSERVE which test file reads which data file. Do not infer it.

WHAT THIS ANSWERS, AND WHY A SECOND INSTRUMENT EXISTS AT ALL.

``scripts/impact_gate.py`` already couples a data file to its readers by
SCANNING SOURCE FOR THE PATH: the basename survives ``ROOT / "_audit" /
"<name>"`` composition, so a bounded match on the last segment finds the code
that holds it. That rule is real and it works -- measured on this tree, an
edit to ``_audit/_census/jobs.md`` selects sixteen test files, and the test
whose parser the census ledger broke on 2026-09-20 is among them.

**BUT A STATIC RULE CANNOT SEE A PATH THAT NEVER APPEARS AS TEXT.** Three
shapes in this repository produce exactly that:

    a directory read   a file walks ``_audit/`` and reads every document in
                       it, naming none of them
    a composed stem    a name assembled from a variable, a loop, or a
                       captured group
    a child process    a test that shells a script; the read happens in a
                       process the scan never looks inside

Each is a TRUE reader that the analyser has no text to match on. This module
answers the same question by MEASUREMENT instead: it runs the suite with every
file-opening call instrumented, records which test file's stack was live when
each read happened, and writes the result to
``scripts/impact_gate_read_map.json``.

WHAT THE MAP IS FOR, AND THE ONE LAW GOVERNING ITS USE.

**IT MAY ONLY ADD EDGES. IT MAY NEVER REMOVE ONE.** The map is a recording of
one run at one commit, so a test added since it was taken is simply absent from
it -- and treating absence as "nothing reads this" is precisely the defect the
impact gate exists to refuse. So the gate takes the UNION of the static rules
and the map, never the map alone, and prints how stale the map is beside the
verdict. A reader who deletes the static rules because the map is more precise
has replaced a sound filter with a cache.

HOW ATTRIBUTION WORKS, AND WHERE IT IS BLIND.

Every read is attributed by walking the live stack for the outermost frame
belonging to a ``tests/test_*.py`` file. That is what makes indirection
transparent: when ``tests/repo_paths.py`` composes the path and opens it, the
test file that asked for it is still on the stack above.

Two blind spots, named rather than papered over:

* **IMPORT CACHING.** A module-level read in a shared helper is attributed to
  whichever test file imported it FIRST; the second importer never triggers the
  read. The static import rule covers that hop, which is why the union matters.
* **GRANDCHILD PROCESSES.** A child process's own reads are invisible. What is
  recorded instead is the ARGV: any repo-relative path handed to a subprocess
  is logged as a read, so a test that shells ``scripts/sweep_x.py`` records an
  edge to that script and the static import rules take it from there.

USAGE::

    python scripts/build_read_map.py            # run the suite, write the map
    python scripts/build_read_map.py --quick tests/test_x.py tests/test_y.py

Exit 0 when a map was written. Exit 1 when it was not -- and a map that was
not written is never silently treated as an empty one.
"""

from __future__ import annotations

import argparse
import builtins
import io
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_FALLBACK = _SCRIPT_DIR.parent

#: Where the observed map lives, beside the suite-size denominator it is a
#: sibling of -- both are cached MEASUREMENTS stamped with the commit they were
#: taken at, and both are downgraded to "unknown" rather than guessed when
#: absent.
MAP_PATH = _SCRIPT_DIR / "impact_gate_read_map.json"

#: One shard's raw recording, keyed by pid so xdist workers cannot overwrite
#: each other. The env var is how the plugin half finds the directory; it is
#: absent in an ordinary suite run, and the plugin then does nothing at all.
SHARD_ENV = "IMPACT_GATE_READ_MAP_DIR"

#: Directories whose contents are never interesting as READ TARGETS: they are
#: the interpreter, the cache and the virtualenv, and recording them would bury
#: the repository's own files under tens of thousands of rows.
_IGNORED_PREFIXES = (
    "venv/", ".venv/", "__pycache__/", ".git/", ".pytest_cache/",
)


def _rel(path: str, repo: Path) -> str | None:
    """Repo-relative, forward slashes -- or None when it is outside the repo.

    None rather than the absolute path: an absolute path on this box is an
    identifier (it carries the account name), and it is also useless to a gate
    that reasons in repo-relative terms. Returning the raw string "just in
    case" is how a workspace path reaches a tracked file.
    """
    try:
        resolved = Path(path).resolve()
    except (OSError, ValueError):
        return None
    try:
        out = resolved.relative_to(repo).as_posix()
    except ValueError:
        return None
    # **EXISTENCE IS THE FILTER, and without it the argv door manufactures
    # edges.** ``Path("git").resolve()`` is ``<repo>/git`` -- repo-relative,
    # plausible, and not a file. The first smoke run recorded ``git`` and
    # ``show`` as read targets from a ``git show`` argv. A recorded edge to a
    # path that does not exist is noise that would widen every plan touching
    # a file with that name.
    if not resolved.exists():
        return None
    if any(out.startswith(prefix) for prefix in _IGNORED_PREFIXES):
        return None
    if "/__pycache__/" in out:
        return None
    return out


# --------------------------------------------------------------------------
# The plugin half. Imported by pytest as ``-p build_read_map``; inert unless
# the shard directory is in the environment.
# --------------------------------------------------------------------------

class _Recorder:
    """Accumulates ``test file -> {paths read}`` for one process."""

    def __init__(self, repo: Path) -> None:
        self.repo = repo
        self.edges: dict[str, set[str]] = {}
        self.unattributed: set[str] = set()

    def attribute(self) -> str | None:
        """The outermost ``tests/test_*.py`` frame on the live stack.

        OUTERMOST, not innermost, and that is the whole point: the innermost
        frame during a helper-mediated read is the helper, which is not a
        pytest target and would lose the edge. The frame that ASKED is the one
        the gate can run.
        """
        frame = sys._getframe(1)
        found: str | None = None
        while frame is not None:
            name = frame.f_code.co_filename
            if name.endswith(".py") and "tests" in name:
                rel = _rel(name, self.repo)
                if (rel and rel.startswith("tests/")
                        and rel.rsplit("/", 1)[-1].startswith("test_")):
                    found = rel
            frame = frame.f_back
        return found

    def record(self, target: str) -> None:
        rel = _rel(target, self.repo)
        if rel is None:
            return
        owner = self.attribute()
        if owner is None:
            self.unattributed.add(rel)
            return
        self.edges.setdefault(owner, set()).add(rel)

    def payload(self) -> dict:
        return {
            "edges": {k: sorted(v) for k, v in sorted(self.edges.items())},
            "unattributed": sorted(self.unattributed),
        }


_RECORDER: _Recorder | None = None


def _install(recorder: _Recorder) -> None:
    """Wrap the two doors every read in this repository goes through.

    **BOTH ``builtins.open`` AND ``io.open`` MUST BE REBOUND, and the first
    smoke run is the receipt for why.** The two names point at the same
    function object, which makes it very easy to believe that patching one
    patches the other. They are separate entries in separate module
    dictionaries: ``pathlib`` holds ``import io`` and calls ``io.open``, so
    ``Path.read_text`` walked straight past a ``builtins``-only wrapper. The
    run recorded four census documents -- every one of them from a ``git
    show`` ARGV -- and not a single one of the reads those same tests perform
    through ``Path``. An instrument that records a third of the reads and says
    nothing is the shape of defect this whole wave is about.

    ``subprocess`` is the second door and it is not optional: several guards
    in this suite do their work by shelling a script, and a child's reads are
    invisible from here. What is recorded for those is the argv.
    """
    real_open = builtins.open

    def traced_open(file, mode="r", *args, **kwargs):  # noqa: ANN001
        if isinstance(file, (str, bytes, os.PathLike)) and "w" not in str(mode) \
                and "a" not in str(mode) and "x" not in str(mode):
            try:
                recorder.record(os.fspath(file))
            except (TypeError, ValueError):
                pass
        return real_open(file, mode, *args, **kwargs)

    builtins.open = traced_open
    io.open = traced_open

    real_run = subprocess.run
    real_popen = subprocess.Popen.__init__

    def _record_argv(argv) -> None:  # noqa: ANN001
        if isinstance(argv, (str, bytes)):
            items = [argv]
        else:
            try:
                items = list(argv)
            except TypeError:
                return
        for item in items:
            if not isinstance(item, (str, os.PathLike)):
                continue
            try:
                text = os.fspath(item)
            except (TypeError, ValueError):
                continue
            recorder.record(text)
            # ``git show <rev>:<path>`` READS A TRACKED FILE and is how
            # several guards in this suite reach a previous version of one.
            # The revision is composed at runtime, so the whole argument is
            # not a path on disk -- but the half after the colon is, and it
            # is the file the test depends on.
            if isinstance(text, str) and ":" in text:
                tail = text.split(":", 1)[1]
                if tail and not tail.startswith(("\\", "/")):
                    recorder.record(tail)

    def traced_run(*args, **kwargs):  # noqa: ANN002
        if args:
            _record_argv(args[0])
        return real_run(*args, **kwargs)

    def traced_popen(self, args=None, *rest, **kwargs):  # noqa: ANN001
        if args is not None:
            _record_argv(args)
        return real_popen(self, args, *rest, **kwargs)

    subprocess.run = traced_run
    subprocess.Popen.__init__ = traced_popen


def pytest_configure(config) -> None:  # noqa: ANN001, ARG001
    """Arm the recorder when the shard directory is set, and not otherwise."""
    global _RECORDER
    shard_dir = os.environ.get(SHARD_ENV)
    if not shard_dir:
        return
    repo = Path(os.environ.get("IMPACT_GATE_READ_MAP_REPO",
                               str(_REPO_FALLBACK))).resolve()
    _RECORDER = _Recorder(repo)
    _install(_RECORDER)


def pytest_unconfigure(config) -> None:  # noqa: ANN001, ARG001
    """Write this process's shard. One file per pid; the runner merges them."""
    shard_dir = os.environ.get(SHARD_ENV)
    if not shard_dir or _RECORDER is None:
        return
    out = Path(shard_dir)
    try:
        out.mkdir(parents=True, exist_ok=True)
        (out / f"shard-{os.getpid()}.json").write_text(
            json.dumps(_RECORDER.payload()), encoding="utf-8")
    except OSError as exc:
        print(f"build_read_map: could not write a shard: {exc}",
              file=sys.stderr)


# --------------------------------------------------------------------------
# The runner half.
# --------------------------------------------------------------------------

def _git(repo: Path, *args: str) -> str | None:
    """git's answer, or None when there was no answer.

    **None RATHER THAN ``""``, and this repository's own guard is the reason.**
    The first version returned an empty string out of ``except OSError``, and
    ``tests/test_an_outage_is_never_filed_as_an_absence.py`` refused it at
    ``build_read_map.py:293`` on the first full run. It was right: the caller
    stamps the map with the commit it was taken at, and an empty string would
    have been written as a blank ``head`` field, indistinguishable from a
    repository that legitimately reports nothing. A map that cannot say which
    commit it describes is a map nobody can age.
    """
    try:
        proc = subprocess.run(["git", *args], cwd=repo, capture_output=True,
                              text=True, encoding="utf-8")
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def merge_shards(shard_dir: Path) -> tuple[dict[str, list[str]], list[str]]:
    """Union every worker's recording. Returns ``(edges, unattributed)``."""
    edges: dict[str, set[str]] = {}
    unattributed: set[str] = set()
    for shard in sorted(shard_dir.glob("shard-*.json")):
        try:
            payload = json.loads(shard.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for owner, paths in payload.get("edges", {}).items():
            edges.setdefault(owner, set()).update(paths)
        unattributed.update(payload.get("unattributed", ()))
    return ({k: sorted(v) for k, v in sorted(edges.items())},
            sorted(unattributed))


def prune(edges: dict[str, list[str]], repo: Path) -> dict[str, list[str]]:
    """Keep only the edges the impact gate cannot already derive precisely.

    **PYTHON TARGETS COME OUT, AND NOTHING ELSE DOES.** A test's dependency on
    a ``.py`` file is answerable exactly, by parsing imports, and
    ``impact_gate.py`` does that; recording it here would duplicate a precise
    rule with a cached one and invite somebody to trust the cache. What is
    left is the class no parser can reach -- documents, fixtures, baselines
    and tables, read through a walk, a composed name or a child process.
    Measured on the first full recording: 8661 raw edges become 2310.

    **THE FLOOR IS NOT PRUNED, DELIBERATELY.** Dropping the corpus-wide
    guards' edges because they run unconditionally would tie this recording to
    a DERIVATION that can change: the day a guard stops being classified as
    corpus-wide, its edges would already be missing here and nothing would
    have noticed. The extra rows cost about 54 KB and buy independence.
    """
    out: dict[str, list[str]] = {}
    for test_file, paths in edges.items():
        # ``is_file()``, not ``exists()``: a walk opens its DIRECTORY, so the
        # first recording carried rows for ``.`` and ``_audit``. Neither can
        # ever be a changed path in a diff, so they are recorded noise -- and
        # noise in a cache is what somebody later mistakes for a finding.
        keep = sorted(p for p in paths
                      if not p.endswith(".py") and (repo / p).is_file())
        if keep:
            out[test_file] = keep
    return out


def build(repo: Path, targets: list[str], shard_dir: Path,
          parallel: bool) -> int:
    """Run the suite under the recorder and write the map. Returns an exit code."""
    python = Path(sys.executable)
    env = dict(os.environ)
    env[SHARD_ENV] = str(shard_dir)
    env["IMPACT_GATE_READ_MAP_REPO"] = str(repo)
    env["PYTHONPATH"] = str(_SCRIPT_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    argv = [str(python), "-m", "pytest", *(targets or ["tests/"]), "-q",
            "-p", "no:randomly", "-p", "build_read_map", "--tb=no"]
    if parallel:
        argv += ["-n", "auto", "--dist", "loadfile"]
    started = time.monotonic()
    proc = subprocess.run(argv, cwd=repo, env=env, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    elapsed = time.monotonic() - started
    tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-12:])
    print(f"build_read_map: pytest exit {proc.returncode} in {elapsed:.1f}s")
    print(tail)
    if proc.returncode not in (0, 1):
        print("build_read_map: pytest could not run, so NO MAP WAS WRITTEN. "
              "An absent map is reported as unknown by the gate, which is the "
              "correct reading; an empty one would have been a lie.",
              file=sys.stderr)
        return 1
    edges, unattributed = merge_shards(shard_dir)
    edges = prune(edges, repo)
    if not edges:
        print("build_read_map: the recorder produced ZERO edges. That is a "
              "broken instrument, not a repository with no file reads; NOT "
              "writing a map.", file=sys.stderr)
        return 1
    payload = {
        "taken_at": time.strftime("%Y-%m-%d"),
        "head": _git(repo, "rev-parse", "--short", "HEAD") or "unknown",
        "seconds": round(elapsed, 1),
        "scope": "full-suite" if not targets else "partial: " + " ".join(targets),
        "pytest_exit": proc.returncode,
        "test_files": len(edges),
        "edges": edges,
        "unattributed": unattributed,
    }
    MAP_PATH.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"build_read_map: wrote {MAP_PATH.name} -- {len(edges)} test files, "
          f"{sum(len(v) for v in edges.values())} edges, "
          f"{len(unattributed)} unattributed reads.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("targets", nargs="*", default=[],
                        help="pytest targets; default is the whole suite")
    parser.add_argument("--shard-dir", default=None,
                        help="where worker recordings land (default: a temp dir)")
    parser.add_argument("--serial", action="store_true",
                        help="do not use xdist")
    args = parser.parse_args(argv)

    repo = Path(_git(Path.cwd(), "rev-parse", "--show-toplevel")
                or str(_REPO_FALLBACK)).resolve()
    if not (repo / "tests").is_dir():
        repo = _REPO_FALLBACK
    # THE SHARDS GO OUTSIDE THE TREE BY DEFAULT. A scratch directory inside
    # the repository would surface in every concurrent writer's ``git status``
    # and would need an ignore entry, which this repo asserts is declared --
    # a build artefact is not worth a tracked rule.
    shard_dir = Path(args.shard_dir) if args.shard_dir else (
        Path(tempfile.gettempdir()) / "impact-gate-read-map-shards")
    if shard_dir.is_dir():
        for stale in shard_dir.glob("shard-*.json"):
            try:
                stale.unlink()
            except OSError:
                pass
    shard_dir.mkdir(parents=True, exist_ok=True)
    return build(repo, args.targets, shard_dir, parallel=not args.serial)


if __name__ == "__main__":
    sys.exit(main())
