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

THE FULL RECORDING RUNS ON CI, ADDED 2026-11-28 (lane ci8). Run whole, the
recipe is a full-suite run, and the full suite does not run on the shared
box, so the map went two months stale (recorded 2026-09-22). Now a
workflow_dispatch of ``.github/workflows/ci.yml`` with ``record_read_map``
runs every shard of ONE cell under this recorder, and its merge job runs::

    python scripts/build_read_map.py --merge <recordings> --out <map> \\
        --run-id <run id> --head <short sha>

``merge_shards`` and ``prune``, the same two functions a local run uses, over
every shard's recordings, with each shard's own pytest exit code and seconds
(``RUN_FILE``) held to the local rule: exit 0 or 1 is a run, anything else is
not, and no map is written from one. The map is uploaded as the run's
``MAP_ARTIFACT``, stamped with the run id and the head it recorded, and::

    python scripts/build_read_map.py --fetch <run id> --sha <head sha>

installs it only if the run is that sha's recording and the map's stamp is
that run's (``scripts/lane_ci.py read-map <sha>`` dispatches, waits and
fetches in one step).
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

#: In a git WORKTREE, ``.git`` at the root is a FILE naming the real git
#: directory, so the ``.git/`` prefix above never matches it and ``prune``'s
#: is-a-file test keeps it. Lane ci8's scoped re-record of 2026-11-28 recorded
#: it as a read. A diff can never name it, so it is never a read target.
_IGNORED_NAMES = frozenset({".git"})

#: One shard's own account of its run, written beside its recordings by the
#: CI step that ran it: ``{"shard": k, "exit": n, "seconds": s}``.
RUN_FILE = "pytest-run.json"

#: The run name ci.yml gives a read-map recording. A recording and the full
#: matrix are both workflow_dispatch runs of ci.yml on a sha; this is how the
#: two are told apart, by the fetch here and by ``scripts/lane_ci.py``.
RECORDING_RUN_NAME = "read-map recording"

#: The recording's merge job, and the artifact it uploads.
MERGE_JOB_NAME = "the read map, merged and pruned"
MAP_ARTIFACT = "impact-gate-read-map"


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
    if out in _IGNORED_NAMES or any(out.startswith(prefix) for prefix in _IGNORED_PREFIXES):
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
    """Union every worker's recording. Returns ``(edges, unattributed)``.

    It walks DOWN the directory: a CI download lays each shard job's
    recordings in a directory of its own, and a flat glob found none of them.
    """
    edges: dict[str, set[str]] = {}
    unattributed: set[str] = set()
    for shard in sorted(shard_dir.rglob("shard-*.json")):
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
                      if not p.endswith(".py") and p not in _IGNORED_NAMES
                      and (repo / p).is_file())
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
    payload = payload_for(
        edges, unattributed,
        head=_git(repo, "rev-parse", "--short", "HEAD") or "unknown",
        seconds=round(elapsed, 1),
        scope="full-suite" if not targets else "partial: " + " ".join(targets),
        pytest_exit=proc.returncode,
    )
    MAP_PATH.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"build_read_map: wrote {MAP_PATH.name} -- {len(edges)} test files, "
          f"{sum(len(v) for v in edges.values())} edges, "
          f"{len(unattributed)} unattributed reads.")
    return 0


def payload_for(edges: dict[str, list[str]], unattributed: list[str], *, head: str,
                seconds, scope: str, pytest_exit, run_id: str | None = None) -> dict:
    """The map, stamped. ONE shape for a local run and a CI merge alike; a CI
    recording also carries the run id it came from."""
    payload = {
        "taken_at": time.strftime("%Y-%m-%d"),
        "head": head,
        "seconds": seconds,
        "scope": scope,
        "pytest_exit": pytest_exit,
        "test_files": len(edges),
        "edges": edges,
        "unattributed": unattributed,
    }
    if run_id is not None:
        payload["run_id"] = str(run_id)
    return payload


def merge_recordings(record_dir: Path, out: Path, *, run_id: str, head: str,
                     repo: Path) -> int:
    """The CI merge: every shard's recordings, merged and pruned by the recipe.

    Refuses, writing nothing, when no shard reported its run, when any shard's
    pytest could not run (an exit other than 0 or 1, the local rule), or when
    the recordings hold no edge at all.
    """
    runs = []
    for path in sorted(record_dir.rglob(RUN_FILE)):
        try:
            runs.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            print(f"build_read_map: {path} is not a run record", file=sys.stderr)
            return 1
    if not runs:
        print(f"build_read_map: no shard under {record_dir} reported its run "
              f"({RUN_FILE}), so NO MAP WAS WRITTEN.", file=sys.stderr)
        return 1
    bad = [r for r in runs if r.get("exit") not in (0, 1)]
    if bad:
        print(f"build_read_map: pytest could not run in shard(s) "
              f"{sorted(r.get('shard') for r in bad)} (exits "
              f"{sorted(r.get('exit') for r in bad)}), so NO MAP WAS WRITTEN.",
              file=sys.stderr)
        return 1
    edges, unattributed = merge_shards(record_dir)
    edges = prune(edges, repo)
    if not edges:
        print("build_read_map: the recordings hold ZERO edges. That is a broken "
              "instrument, not a repository with no file reads; NOT writing a map.",
              file=sys.stderr)
        return 1
    payload = payload_for(
        edges, unattributed, head=head,
        seconds=round(sum(float(r.get("seconds") or 0) for r in runs), 1),
        scope=(f"full-suite (GitHub Actions, one cell in {len(runs)} shards, "
               f"recorded by run {run_id})"),
        pytest_exit=max(r["exit"] for r in runs),
        run_id=run_id,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"build_read_map: merged {len(runs)} shard(s) into {out.name} -- "
          f"{len(edges)} test files, {sum(len(v) for v in edges.values())} edges, "
          f"{len(unattributed)} unattributed reads; run {run_id} at {head}.")
    return 0


def _gh_cli(*args: str) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(["gh", *args], capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
    except OSError as exc:
        return 127, "", str(exc)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def fetch(run_id: str, sha: str, *, slug: str | None = None, gh=None,
          map_path: Path = MAP_PATH) -> int:
    """Install the map recorded by run ``run_id``, which must be ``sha``'s.

    BY RUN ID AND HEAD SHA, never "the latest run": the run is read by its id,
    and refused unless it is a completed read-map recording of exactly that
    sha whose merge job succeeded; the map is then refused unless its own
    stamp names that run and a head ``sha`` begins with. Exit 0 installed, 1
    refused, 2 gh could not answer.
    """
    gh = gh or _gh_cli
    if slug is None:
        import lane_ci  # noqa: PLC0415 -- only the fetch needs the remote

        rc, url, err = lane_ci._git("remote", "get-url", "origin")
        if rc != 0:
            print(f"build_read_map: no origin remote ({err})", file=sys.stderr)
            return 2
        slug = lane_ci.slug_from_url(url)
    rc, out, err = gh("run", "view", str(run_id), "-R", slug, "--json",
                      "databaseId,headSha,event,status,conclusion,displayTitle,jobs")
    if rc != 0:
        print(f"build_read_map: gh run view {run_id} failed ({err[:200]})", file=sys.stderr)
        return 2
    view = json.loads(out)
    merge_job = [j for j in view.get("jobs") or [] if j.get("name") == MERGE_JOB_NAME]
    problems = []
    if view.get("headSha") != sha:
        problems.append(f"run {run_id} recorded {str(view.get('headSha'))[:12]}, not {sha[:12]}")
    if view.get("event") != "workflow_dispatch" or view.get("displayTitle") != RECORDING_RUN_NAME:
        problems.append(f"run {run_id} is not a read-map recording "
                        f"({view.get('event')}, {view.get('displayTitle')!r})")
    if view.get("status") != "completed":
        problems.append(f"run {run_id} is {view.get('status')}, not completed")
    if [j.get("conclusion") for j in merge_job] != ["success"]:
        problems.append(f"its job {MERGE_JOB_NAME!r} did not succeed "
                        f"({[j.get('conclusion') for j in merge_job]})")
    if problems:
        print("build_read_map: REFUSED, nothing installed: " + "; ".join(problems),
              file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as scratch:
        rc, _out, err = gh("run", "download", str(run_id), "-R", slug, "-n", MAP_ARTIFACT,
                           "-D", scratch)
        if rc != 0:
            print(f"build_read_map: gh run download {run_id} failed ({err[:200]})",
                  file=sys.stderr)
            return 2
        downloaded = Path(scratch) / MAP_PATH.name
        try:
            payload = json.loads(downloaded.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"build_read_map: the artifact holds no readable map ({exc})",
                  file=sys.stderr)
            return 1
    head = str(payload.get("head") or "")
    stamp_problems = []
    if str(payload.get("run_id")) != str(run_id):
        stamp_problems.append(f"the map names run {payload.get('run_id')}, not {run_id}")
    if not head or not sha.startswith(head):
        stamp_problems.append(f"the map names head {head!r}, not a prefix of {sha[:12]}")
    if not str(payload.get("scope", "")).startswith("full-suite"):
        stamp_problems.append(f"the map's scope is {payload.get('scope')!r}")
    if not isinstance(payload.get("edges"), dict) or not payload["edges"]:
        stamp_problems.append("the map holds no edges")
    if stamp_problems:
        print("build_read_map: REFUSED, nothing installed: " + "; ".join(stamp_problems),
              file=sys.stderr)
        return 1
    map_path.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"build_read_map: installed run {run_id}'s map at {head} -- "
          f"{len(payload['edges'])} test files.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("targets", nargs="*", default=[],
                        help="pytest targets; default is the whole suite")
    parser.add_argument("--shard-dir", default=None,
                        help="where worker recordings land (default: a temp dir)")
    parser.add_argument("--serial", action="store_true",
                        help="do not use xdist")
    parser.add_argument("--merge", default=None, metavar="DIR",
                        help="merge and prune a CI recording's shards; write --out")
    parser.add_argument("--out", default=None, help="where --merge writes the map")
    parser.add_argument("--run-id", default=None, help="the recording run, for its stamp")
    parser.add_argument("--head", default=None, help="the head it recorded, for its stamp")
    parser.add_argument("--repo-root", default=None,
                        help="the checkout prune reads against (default: git's top level)")
    parser.add_argument("--fetch", default=None, metavar="RUN_ID",
                        help="install the map recorded by this CI run")
    parser.add_argument("--sha", default=None, help="the head sha --fetch must find")
    args = parser.parse_args(argv)

    repo = Path(args.repo_root or _git(Path.cwd(), "rev-parse", "--show-toplevel")
                or str(_REPO_FALLBACK)).resolve()
    if args.repo_root is None and not (repo / "tests").is_dir():
        repo = _REPO_FALLBACK
    if args.fetch is not None:
        if not args.sha:
            parser.error("--fetch needs --sha, the head the run must have recorded")
        return fetch(args.fetch, args.sha)
    if args.merge is not None:
        if not (args.out and args.run_id and args.head):
            parser.error("--merge needs --out, --run-id and --head")
        return merge_recordings(Path(args.merge), Path(args.out), run_id=args.run_id,
                                head=args.head, repo=repo)
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
