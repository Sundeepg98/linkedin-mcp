"""Run the free CI matrix on a lane's branch instead of the suite on this box.

WHY THIS EXISTS. Every lane used to run its suite locally, on one shared
8-core machine, because the pre-push gate published nothing but master: a lane
took 30-60 minutes and serialised behind its neighbours. Since 2026-10-10 the
gate (``scripts/pre_push_ref_gate.py``) admits a lone ``refs/heads/ci/<name>``
that descends from ``origin/master`` and whose new commits sweep clean, and
``.github/workflows/ci.yml`` runs a push there on ONE ubuntu cell in FOUR
shards. This file is the two commands a lane types:

    <main checkout>/venv/Scripts/python.exe scripts/lane_ci.py push
    <main checkout>/venv/Scripts/python.exe scripts/lane_ci.py wait <sha>

and, when the lane is done with the ref,

    <main checkout>/venv/Scripts/python.exe scripts/lane_ci.py clean <branch>

Run from the lane's worktree root (a worktree has no venv; the main
checkout's interpreter is the one to use).

WHAT ``push`` DOES, in order, and why each step is where it is:

1. refuses a dirty tree -- tracked changes OR untracked files. CI tests the
   COMMIT, and a green run over a commit the lane has since edited, or that
   is missing a file the lane forgot to add, is a receipt for something else.
   An untracked ``_TEAM_LEAD_*.md`` ruling refuses too: read it first.
2. refuses a detached HEAD: the ci/ ref is named after the branch.
3. refuses unless the MAIN checkout's gate knows ci/ refs -- the pre-push
   hook runs that copy, not this worktree's, so until this file's lane is
   merged into the main checkout every ci/ push would be refused anyway.
4. runs the GATE'S OWN ancestry clause (``git_ci_check(sha, sweep=False)``)
   so a branch that does not descend from ``origin/master`` is refused before
   any network call. It does NOT run the identity sweep: the hook runs the
   gate's whole check, sweep included, on this very push, and running it here
   as well paid the sweep twice (2026-10-10: 72-217s each, before the sweep
   read its blobs through one process). A planted value is therefore refused
   by the hook, from inside the push, with nothing published.
5. pushes the CHECKED sha (not ``HEAD`` again) to ``ci/<branch>``, forced --
   the ref belongs to one lane and its old commits were already published --
   with ``--no-follow-tags`` so no tag can ride along and be refused.
6. prints the sha as its LAST line, alone, so ``tail -1`` captures it.

WHAT ``wait`` DOES. Finds the run BY HEAD SHA (``gh run list --commit``),
never "the latest run" -- right after a push the latest run is the previous
one. Keeps only a ``push`` run whose head branch is a ``ci/`` ref. Polls every
20 s, bounded at 25 minutes. Reads the verdict from
``gh run view --json status,conclusion,jobs``, never from ``gh run watch``'s
exit code, which is 0 on a 403. On a failure it prints the failing job names,
then EVERY failing test as a node id (``tests/f.py::test_x``), then the first
failing lines from ``--log-failed`` as detail, truncated. The id rides a
``FAILED tests/...::test`` line under ``-rf`` or, under the ``-q -rs`` CI
actually runs, the sub-banner opening each FAILURES block, paired with that
block's own ``tests/...:NNN`` reference. The ids are read separately from the
detail and are not subject to its cap; past ``ID_LIMIT`` the count of the
rest is printed. When the log names no test it says so rather than let the
exit banner pass for one.

WHAT ``wait <sha> --full`` DOES, ADDED 2026-11-27 (lane ci8; ruled 22:55:
before master is fast-forwarded, a branch's ci/ ref gets the FULL matrix --
three cells x six shards, which ``ci.yml`` gives a workflow_dispatch on any
ref). In order:

1. refuses unless ``origin``'s ``ci/<branch>`` holds exactly ``<sha>``
   (``git ls-remote``): a dispatch runs the REF's head, and a full matrix of
   another commit is no certificate for this one.
2. waits for the PUSH run of ``<sha>`` on ``ci/<branch>`` to FINISH. The
   dispatch shares its concurrency group (``ci.yml``: one group per branch
   ref, cancel-in-progress), so whichever started first would be cancelled.
   A red push run ends it there: nothing is dispatched, because the full
   matrix cannot certify a sha whose lane run failed.
3. reads the workflow_dispatch runs of ``<sha>`` on ``ci/<branch>`` BEFORE
   dispatching. One still running is RESUMED, never sent again (a second
   dispatch would cancel it); one already finished is READ, not repeated --
   it is the full matrix's verdict on this sha (re-run its failed jobs with
   ``gh run rerun <id> --failed`` and ``--full`` waits on that attempt). Only
   when there is none, or the last was cancelled, does it dispatch:
   ``gh workflow run ci.yml --ref ci/<branch>``.
4. finds the new run BY HEAD SHA AND EVENT and ref, excluding every run id
   that existed before the dispatch -- never "the latest run", which right
   after a dispatch is somebody else's -- and waits on it, bounded at
   ``FULL_BOUND_SECONDS``.
5. reports the run's verdict and EVERY CELL: each cell's shards and their
   conclusions, the plan and totals jobs, and on a red run the failing tests
   as ``wait`` prints them. A green run of one cell is the fast lane's shape,
   and is reported as NOT THE FULL MATRIX rather than as its certificate.

Re-running ``--full`` after a shell cut it short is therefore safe: it finds
the dispatch it already sent and waits on that.

EXIT CODES: 0 success; 1 a refusal or a red run; 2 nothing could be
established (no run appeared, the bound ran out, gh kept failing). 2 never
means green.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import pre_push_ref_gate as gate  # noqa: E402
# The read-map recording's run name, merge job and fetch are the recipe's own.
import build_read_map as recipe  # noqa: E402

RECORDING_RUN_NAME = recipe.RECORDING_RUN_NAME

POLL_SECONDS = 20
BOUND_SECONDS = 25 * 60
#: The full matrix's bound, from the dispatch to its verdict. Measured: master
#: run 46042146411 (three cells x six shards, 2026-11-27) took 10m44s; the
#: windows shards set it, and a degraded windows runner has run 2x slower.
FULL_BOUND_SECONDS = 45 * 60
#: The read-map recording's bound: one cell in six shards, every read
#: recorded, so slower than a shard of the full matrix.
RECORDING_BOUND_SECONDS = 60 * 60
#: The workflow ``--full`` dispatches, by its file name.
WORKFLOW_FILE = "ci.yml"
FAILED_JOB_STATES = frozenset(
    {"failure", "cancelled", "timed_out", "action_required", "startup_failure"})
#: A shard job's name as ``ci.yml`` renders it: ``pytest (<os>, py<version>,
#: shard <n>)``. Held to the workflow's own template by
#: ``tests/test_lane_ci.py::test_the_cell_reader_parses_the_job_name_ci_yml_writes``.
_SHARD_JOB = re.compile(
    r"^pytest \((?P<os>[^,()]+), py(?P<py>[^,()]+), shard (?P<shard>\d+)\)$")
# The pre-fix pattern was ``(FAILED|ERROR) \S|##\[error\]|REFUS``. Those
# classes carry a failing id when the suite runs under ``-rf`` (a
# ``FAILED tests/...::test`` line) or always carry the exit banner. But CI
# runs the suite with ``-q -rs`` -- skip summary only, NOT ``-rf`` -- so a
# real red log carries the failing test id on THREE OTHER line classes
# instead, none of them matched by the old pattern:
#   * the ``______ test_name ______`` sub-banner that opens each FAILURES
#     block,
#   * the ``E       ...`` lines of that block -- the message,
#   * the ``tests/file.py:NNN: ...`` reference lines -- the test's own frame
#     and any frame deeper in the suite.
# A real red log on 2026-10-26 (lane run, shard 0) had the id on all three
# and on none of the old classes, which is why ``wait`` printed only the
# banner. ``_FALLING_LINE`` below is the union of the old and the new, so a
# run logged either way still surfaces the id.
#
# THE SUB-BANNER'S FILL IS ANY WIDTH, measured 2026-11-25 (pytest -q -rs at
# COLUMNS=80, CI's fallback): a name too long for the line is padded with ONE
# underscore a side, and this suite has test names past 80 characters. The
# first version wanted four, and such a test vanished from the report. AND
# THE TITLE IS NOT ITSELF FILL: pytest draws ``_ _ _ ... _`` between the
# frames of a long traceback, which any-width fill alone would take for a
# banner (it did, on the real log of a four-failure run, after the fixture
# transcribed from that log had passed without the separator in it).
_FALLING_LINE = re.compile(
    r"(FAILED|ERROR) \S|##\[error\]|REFUS"
    r"|^_+ [^_\s].*? _+$"  # the ____ test_name ____ sub-banner, any fill width
    r"|^E\s"              # an "E" (excerpt) line of a FAILURES block
    r"|^tests/[\w./-]+\.py:\d+")   # a "tests/file.py:NNN: ..." reference line

# THE IDS ARE READ ON THEIR OWN. The lines above are the DETAIL view, capped
# at 20 because every E line and every frame comes with it; on the first
# live red run it read (four failing tests, 2026-10-26) the cap ran out one
# block early and ``wait`` named three. These read only what identifies a
# failing test, and ``_report`` prints all of them ahead of the detail.
#: A FAILURES block's opening sub-banner; group 1 is the name pytest printed
#: there -- ``test_x``, ``Class.test_x``, ``test_x[param]``, or a sentence
#: such as ``ERROR at setup of test_x``.
_SUBBANNER = re.compile(r"^_+ ([^_\s].*?) _+$")
#: An ``-rf`` short-summary line; group 1 is the node id (or, for an error
#: collecting a file, the file).
_ID_LINE = re.compile(r"^(?:FAILED|ERROR) (tests/\S+?\.py(?:::.+?)?)(?: - |$)")
#: A traceback reference into the suite; group 1 is the test file.
_TEST_REF = re.compile(r"^(tests/[\w./-]+\.py):\d+")
#: How many failing test ids ``wait`` prints before it says how many more
#: there are. The most a lane run here has had is four; a run past fifty is
#: broken wholesale, and the count says so instead of a silent cut.
ID_LIMIT = 50


# ---------------------------------------------------------------------------
# Pure logic -- tested without a network or a remote
# ---------------------------------------------------------------------------


def ci_ref_for(branch: str) -> str:
    """``refs/heads/ci/<branch>``, or ValueError naming why not."""
    branch = branch.strip()
    if not branch or branch == "HEAD":
        raise ValueError("no branch: HEAD is detached, and the ci/ ref is "
                         "named after the branch")
    ref = gate.CI_PREFIX + branch
    if not gate.ci_name_ok(ref):
        raise ValueError(f"{branch!r} does not make a plain ci/ name -- the "
                         "gate would refuse it")
    return ref


def slug_from_url(url: str) -> str:
    """``owner/repo`` from a GitHub remote url, https or ssh."""
    m = re.search(r"github\.com[:/]+([^/\s]+)/([^/\s]+?)(?:\.git)?/?$", url.strip())
    if not m:
        raise ValueError(f"not a GitHub remote url: {url!r}")
    return f"{m.group(1)}/{m.group(2)}"


def choose_run(runs: list[dict], sha: str, branch: str | None = None) -> dict | None:
    """The run a lane is waiting on: a ``push`` run of exactly this sha on a
    ``ci/`` ref -- ``ci/<branch>`` when there is one, else the newest such run.

    A master run of the SAME sha (after the merge) and a pull_request run are
    never it: they ran a different matrix and answer a different question.
    """
    mine = [r for r in runs
            if r.get("headSha") == sha and r.get("event") == "push"
            and (r.get("headBranch") or "").startswith("ci/")]
    if branch:
        exact = [r for r in mine if r.get("headBranch") == f"ci/{branch}"]
        mine = exact or mine
    if not mine:
        return None
    return max(mine, key=lambda r: (r.get("createdAt") or "", r.get("databaseId") or 0))


def verdict(view: dict) -> str:
    """pending / success / cancelled / failure:<conclusion>.

    CANCELLED IS NOT A FAILURE. The workflow supersedes a branch run when the
    same ref is pushed again, and a run cancelled that way says nothing about
    the code -- reporting it as red would send a lane hunting a bug that does
    not exist.
    """
    if view.get("status") != "completed":
        return "pending"
    conclusion = view.get("conclusion") or "none"
    if conclusion == "success":
        return "success"
    if conclusion == "cancelled":
        return "cancelled"
    return f"failure:{conclusion}"


def failing_jobs(view: dict) -> list[str]:
    return [j.get("name", "?") for j in view.get("jobs") or []
            if j.get("conclusion") in FAILED_JOB_STATES]


def _strip_gh_prefix(raw: str) -> str:
    """One ``--log-failed`` line as pytest wrote it.

    gh's ``--log-failed`` prefixes each line with ``<job>\\t<step>\\t
    <timestamp> ``; that prefix is cut. The first annotation line of a step
    also carries a byte-order mark on its timestamp, and a stray one is
    stripped too -- spelled ``chr(0xFEFF)`` because a literal one in this
    file is invisible to whoever edits it next.
    """
    text = raw.split("\t")[-1]
    text = re.sub(r"^\S+Z\s", "", text).strip()
    return text.lstrip(chr(0xFEFF))


def first_failing_lines(log: str, limit: int = 20, width: int = 220) -> list[str]:
    """The DETAIL view of a red ``--log-failed`` dump: its first failing
    lines, deduplicated, capped at ``limit``.

    A line is kept when it belongs to a failure: the old classes (a
    ``FAILED``/``ERROR`` id line, the ``##[error]`` process banner, a ``REFUS``
    refusal) and the three that carry the failure under ``-q -rs`` (the
    sub-banner, the ``E`` lines, the ``tests/...:NNN`` references) -- see the
    module-level patterns. Because every ``E`` line and frame is kept, a run
    with several failures can fill the cap before its last block: the ids are
    therefore read separately, by :func:`failing_test_ids`, and never capped
    by this.
    """
    out: list[str] = []
    seen: set[str] = set()
    for raw in log.splitlines():
        text = _strip_gh_prefix(raw)
        if not _FALLING_LINE.search(text) or text in seen:
            continue
        seen.add(text)
        out.append(text if len(text) <= width else text[:width - 3] + "...")
        if len(out) >= limit:
            break
    return out


def _node_id(name: str, path: str | None) -> str:
    """A sub-banner's name as a node id a reader can run.

    ``Class.test_x[p]`` under ``tests/f.py`` is ``tests/f.py::Class::test_x[p]``
    (only the part before ``[`` is split: a parameter may hold dots). A name
    with whitespace before any ``[`` is a sentence -- ``ERROR at setup of
    test_x`` -- and is kept as written, because pairing it with a path would
    invent a node id that does not exist.
    """
    head, bracket, rest = name.partition("[")
    if path is None or re.search(r"\s", head):
        return name
    return f"{path}::{head.replace('.', '::')}{bracket}{rest}"


def failing_test_ids(log: str) -> list[str]:
    """Every distinct failing test a ``--log-failed`` dump names, in order.

    Two sources, because a local ``-rf`` run and CI's ``-q -rs`` log a failure
    differently: the ``FAILED``/``ERROR`` short-summary lines, and the
    sub-banner opening each FAILURES block. A sub-banner carries only the
    name, so it is paired with the first ``tests/`` reference INSIDE ITS OWN
    BLOCK -- the test's own frame -- and a block that ends without one keeps
    the bare name. The same test failing in several cells is one id.

    NOT CAPPED. That is the point of a second function: the detail view is
    capped, and on a four-failure run it ran out one block early.
    """
    ids: list[str] = []
    seen: set[str] = set()

    def add(node: str) -> None:
        if node not in seen:
            seen.add(node)
            ids.append(node)

    pending: str | None = None
    for raw in log.splitlines():
        text = _strip_gh_prefix(raw)
        banner = _SUBBANNER.match(text)
        if banner:
            if pending is not None:
                add(_node_id(pending, None))
            pending = banner.group(1)
            continue
        if pending is not None:
            ref = _TEST_REF.match(text)
            if ref:
                add(_node_id(pending, ref.group(1)))
                pending = None
                continue
            if text.startswith("=") and text.endswith("="):
                add(_node_id(pending, None))   # the section ended first
                pending = None
        summary = _ID_LINE.match(text)
        if summary:
            add(summary.group(1))
    if pending is not None:
        add(_node_id(pending, None))
    return ids


def elapsed(view: dict) -> str:
    """Wall clock of the run from its own timestamps, or ``unknown``."""
    from datetime import datetime
    start, end = view.get("startedAt") or view.get("createdAt"), view.get("updatedAt")
    try:
        a = datetime.fromisoformat(start.replace("Z", "+00:00"))
        b = datetime.fromisoformat(end.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return "unknown"
    seconds = int((b - a).total_seconds())
    return f"{seconds // 60}m{seconds % 60:02d}s"


def _newest(runs: list[dict]) -> dict | None:
    if not runs:
        return None
    return max(runs, key=lambda r: (r.get("createdAt") or "", r.get("databaseId") or 0))


def _dispatched(runs: list[dict], sha: str, branch: str) -> list[dict]:
    return [r for r in runs
            if r.get("headSha") == sha and r.get("event") == "workflow_dispatch"
            and r.get("headBranch") == f"ci/{branch}"]


def dispatch_runs(runs: list[dict], sha: str, branch: str) -> list[dict]:
    """The FULL-MATRIX dispatch runs of exactly this sha on ``ci/<branch>``.

    A read-map recording is a workflow_dispatch run of the same workflow on the
    same sha, and it certifies nothing: it is told apart by its run name and
    is never one of these (2026-11-28).
    """
    return [r for r in _dispatched(runs, sha, branch)
            if r.get("displayTitle") != RECORDING_RUN_NAME]


def recording_runs(runs: list[dict], sha: str, branch: str) -> list[dict]:
    """The read-map recordings of exactly this sha on ``ci/<branch>``."""
    return [r for r in _dispatched(runs, sha, branch)
            if r.get("displayTitle") == RECORDING_RUN_NAME]


def choose_push_run(runs: list[dict], sha: str, branch: str) -> dict | None:
    """The push run of this sha on ``ci/<branch>`` itself, the one the dispatch
    would share a concurrency group with. A push of the same sha to another
    ci/ ref is in another group, so it is never this run."""
    return _newest([r for r in runs
                    if r.get("headSha") == sha and r.get("event") == "push"
                    and r.get("headBranch") == f"ci/{branch}"])


def choose_dispatch_run(runs: list[dict], sha: str, branch: str,
                        before: set) -> dict | None:
    """The dispatch run this ``--full`` sent: of this sha, event and ref, and
    not one of ``before``, the run ids that existed before the dispatch."""
    return _newest([r for r in dispatch_runs(runs, sha, branch)
                    if r.get("databaseId") not in before])


def cells_of(view: dict) -> dict[str, dict[int, str]]:
    """``{cell: {shard index: conclusion}}`` from a run's shard jobs.

    The cell is spelled as ``ci_shard_totals.cell_label`` spells it
    ("ubuntu-latest py3.13"). Jobs that are not shards (the plan, the totals)
    are not cells and are reported apart.
    """
    cells: dict[str, dict[int, str]] = {}
    for job in view.get("jobs") or []:
        match = _SHARD_JOB.match(job.get("name") or "")
        if match:
            label = f"{match['os'].strip()} py{match['py'].strip()}"
            cells.setdefault(label, {})[int(match["shard"])] = (
                job.get("conclusion") or job.get("status") or "unknown")
    return cells


def matrix_problems(cells: dict[str, dict[int, str]]) -> list[str]:
    """Why these cells are not a full-matrix run, or ``[]`` when they are.

    The shape is read from what RAN, never from a second copy of the plan:
    more than one cell (one cell is the fast lane's shape), and every cell
    holding the same shards, 0 to n-1. The totals job, which reads the plan's
    own outputs, already refuses a run whose shards do not add up.
    """
    problems: list[str] = []
    if len(cells) < 2:
        problems.append(f"{len(cells)} cell(s) ran; the full matrix runs more "
                        "than one, and one cell is the fast lane's shape")
    counts = {label: len(shards) for label, shards in cells.items()}
    for label, shards in sorted(cells.items()):
        if sorted(shards) != list(range(len(shards))):
            problems.append(f"{label}: shards {sorted(shards)} are not "
                            f"0..{len(shards) - 1}")
    if len(set(counts.values())) > 1:
        problems.append(f"the cells ran different numbers of shards: {counts}")
    return problems


def cell_lines(cells: dict[str, dict[int, str]]) -> list[str]:
    """One line per cell: how many shards succeeded, and every one that did not."""
    lines = []
    for label, shards in sorted(cells.items()):
        good = sum(1 for c in shards.values() if c == "success")
        line = f"  {label}: {good} of {len(shards)} shards success"
        bad = [f"shard {i} {shards[i]}" for i in sorted(shards) if shards[i] != "success"]
        if bad:
            line += "; " + ", ".join(bad)
        lines.append(line)
    return lines


# ---------------------------------------------------------------------------
# The repository and the network
# ---------------------------------------------------------------------------


def _run(*argv: str) -> tuple[int, str, str]:
    out = subprocess.run(list(argv), capture_output=True, text=True,
                         errors="replace")
    return out.returncode, out.stdout.strip(), out.stderr.strip()


def _git(*args: str) -> tuple[int, str, str]:
    return _run("git", *args)


def _gh(*args: str) -> tuple[int, str, str]:
    return _run("gh", *args)


def main_checkout_gate() -> Path | None:
    rc, common, _err = _git("rev-parse", "--path-format=absolute", "--git-common-dir")
    if rc != 0 or not common:
        return None
    return Path(common).parent / "scripts" / "pre_push_ref_gate.py"


def hook_gate_knows_ci(path: Path | None) -> bool:
    """The hook runs the MAIN checkout's gate; does that copy admit ci/?"""
    if path is None or not path.is_file():
        return False
    return 'CI_PREFIX = "refs/heads/ci/"' in path.read_text(encoding="utf-8",
                                                           errors="replace")


def push_problems() -> tuple[list[str], str, str]:
    """Everything ``push`` checks before it pushes: (problems, sha, ci_ref)."""
    rc, status, err = _git("status", "--porcelain")
    if rc != 0:
        return [f"git status failed: {err}"], "", ""
    if status:
        shown = status.splitlines()
        lines = [f"the tree is dirty ({len(shown)} path(s)); commit or remove "
                 "them first -- CI tests the commit, not the tree:"]
        lines += [f"    {line}" for line in shown[:10]]
        return lines, "", ""
    rc, branch, _err = _git("symbolic-ref", "--quiet", "--short", "HEAD")
    try:
        ref = ci_ref_for(branch if rc == 0 else "")
    except ValueError as exc:
        return [str(exc)], "", ""
    if not hook_gate_knows_ci(main_checkout_gate()):
        return ["the pre-push hook runs the MAIN checkout's "
                "scripts/pre_push_ref_gate.py, and that copy does not admit "
                "ci/ refs yet -- the push would be refused. It needs the "
                "2026-10-10 gate merged into the main checkout."], "", ref
    rc, sha, err = _git("rev-parse", "--verify", "HEAD^{commit}")
    if rc != 0:
        return [f"HEAD does not resolve: {err}"], "", ref
    # ANCESTRY ONLY. The hook runs the gate's whole check, sweep included, on
    # this very push; sweeping here too paid the sweep twice per push.
    return gate.git_ci_check(sha, sweep=False), sha, ref


def git_push(sha: str, ref: str) -> int:
    done = subprocess.run(["git", "push", "--no-follow-tags", gate.CI_REMOTE,
                           f"+{sha}:{ref}"])
    return done.returncode


def cmd_push(pusher=git_push) -> int:
    problems, sha, ref = push_problems()
    if problems:
        print("lane_ci push: REFUSED, nothing was pushed", file=sys.stderr)
        for line in problems:
            print(f"  {line}", file=sys.stderr)
        return 1
    print(f"lane_ci push: {sha[:12]} -> {gate.CI_REMOTE} {ref}", file=sys.stderr)
    rc = pusher(sha, ref)
    if rc != 0:
        print(f"lane_ci push: git push exited {rc}; nothing to wait on",
              file=sys.stderr)
        return 1
    print(sha)
    return 0


_RUN_FIELDS = "databaseId,headSha,headBranch,event,status,conclusion,createdAt,displayTitle"
_VIEW_FIELDS = "status,conclusion,jobs,createdAt,startedAt,updatedAt"


def _list_runs(slug: str, sha: str, event: str, what: str) -> list[dict] | None:
    """The runs of ``sha`` for ``event``, asked BY SHA; None when gh failed."""
    rc, out, err = _gh("run", "list", "-R", slug, "--commit", sha, "--event", event,
                       "--limit", "50", "--json", _RUN_FIELDS)
    if rc != 0:
        print(f"lane_ci {what}: gh run list failed ({err[:200]})", file=sys.stderr)
        return None
    return json.loads(out or "[]")


def _await_run(slug: str, sha: str, event: str, choose, *, what: str, poll: int,
               bound: int, sleep, clock) -> tuple[str | None, dict | None, str | None]:
    """Poll until ``choose`` names a run of ``sha`` and that run completes.

    Returns ``(run_id, view, state)``. ``view`` is None when the bound ran out
    first, which is NO VERDICT, and is said so.
    """
    deadline = clock() + bound
    run_id = None
    while True:
        if run_id is None:
            runs = _list_runs(slug, sha, event, what)
            run = choose(runs) if runs is not None else None
            if run is not None:
                run_id = str(run["databaseId"])
                print(f"lane_ci {what}: run {run_id} on {run['headBranch']} "
                      f"for {sha[:12]}", file=sys.stderr)
        if run_id is not None:
            rc, out, err = _gh("run", "view", run_id, "-R", slug, "--json", _VIEW_FIELDS)
            if rc == 0:
                view = json.loads(out)
                state = verdict(view)
                if state != "pending":
                    return run_id, view, state
                jobs = view.get("jobs") or []
                done = sum(1 for j in jobs if j.get("status") == "completed")
                print(f"lane_ci {what}: run {run_id} {view.get('status')}, "
                      f"{done}/{len(jobs)} jobs done", file=sys.stderr)
            else:
                print(f"lane_ci {what}: gh run view failed ({err[:200]})",
                      file=sys.stderr)
        if clock() >= deadline:
            print(f"lane_ci {what}: NO VERDICT within {bound // 60} minutes "
                  f"(run {run_id or 'never appeared'}). This is not a pass.",
                  file=sys.stderr)
            return run_id, None, None
        sleep(poll)


def cmd_wait(sha: str, *, poll: int = POLL_SECONDS, bound: int = BOUND_SECONDS,
             sleep=time.sleep, clock=time.monotonic) -> int:
    rc, url, err = _git("remote", "get-url", gate.CI_REMOTE)
    if rc != 0:
        print(f"lane_ci wait: no {gate.CI_REMOTE} remote ({err})", file=sys.stderr)
        return 2
    slug = slug_from_url(url)
    rc_branch, branch, _err = _git("symbolic-ref", "--quiet", "--short", "HEAD")
    mine = branch if rc_branch == 0 else None
    run_id, view, state = _await_run(
        slug, sha, "push", lambda runs: choose_run(runs, sha, mine), what="wait",
        poll=poll, bound=bound, sleep=sleep, clock=clock)
    if view is None:
        return 2
    return _report(slug, run_id, view, state)


def _ref_head(ref: str) -> str:
    """The sha ``origin``'s ``ref`` holds, or ``""``."""
    rc, out, _err = _git("ls-remote", gate.CI_REMOTE, ref)
    return out.split()[0] if rc == 0 and out.split() else ""


def cmd_read_map(sha: str, *, poll: int = POLL_SECONDS,
                 bound: int = RECORDING_BOUND_SECONDS, sleep=time.sleep,
                 clock=time.monotonic, fetcher=None) -> int:
    """``read-map <sha>``: record the impact gate's read map on CI, install it.

    The read-map recording is a dispatch of ci.yml with ``record_read_map``:
    one cell, sharded, every shard under ``build_read_map.py``'s recorder, the
    merged map uploaded by its last job. This dispatches it on ``ci/<branch>``
    (refused unless the ref holds ``sha``), finds the run BY SHA, EVENT AND
    RUN NAME -- never a full-matrix dispatch of the same sha -- waits, and on
    a merge job that succeeded installs the map through the recipe's own
    fetch, by run id and sha. As with ``--full``, a recording
    already running is waited on, and one finished is read, not repeated. The
    recording has a concurrency group of its own, so no push run is waited on.
    """
    fetcher = fetcher or recipe.fetch
    rc, url, err = _git("remote", "get-url", gate.CI_REMOTE)
    if rc != 0:
        print(f"lane_ci read-map: no {gate.CI_REMOTE} remote ({err})", file=sys.stderr)
        return 2
    slug = slug_from_url(url)
    rc, branch, _err = _git("symbolic-ref", "--quiet", "--short", "HEAD")
    try:
        ref = ci_ref_for(branch if rc == 0 else "")
    except ValueError as exc:
        print(f"lane_ci read-map: REFUSED -- {exc}", file=sys.stderr)
        return 1
    short_ref = ref[len("refs/heads/"):]
    held = _ref_head(ref)
    if held != sha:
        print(f"lane_ci read-map: REFUSED -- {gate.CI_REMOTE} {short_ref} holds "
              f"{held[:12] or 'nothing'}, not {sha[:12]}. A dispatch runs the "
              "ref's head; push this sha first (lane_ci.py push).", file=sys.stderr)
        return 1

    listed = _list_runs(slug, sha, "workflow_dispatch", "read-map")
    if listed is None:
        return 2
    existing = recording_runs(listed, sha, branch)
    last = _newest(existing)
    if last is not None and (last.get("status") != "completed"
                             or last.get("conclusion") != "cancelled"):
        known = last.get("databaseId")
        print(f"lane_ci read-map: recording run {known} of {sha[:12]} is "
              f"{last.get('status')}; reading it, not dispatching again",
              file=sys.stderr)

        def choose(runs):
            return next((r for r in recording_runs(runs, sha, branch)
                         if r.get("databaseId") == known), None)
    else:
        before = {r.get("databaseId") for r in existing}
        rc, _out, err = _gh("workflow", "run", WORKFLOW_FILE, "-R", slug, "--ref",
                            short_ref, "-f", "record_read_map=true")
        if rc != 0:
            print(f"lane_ci read-map: the dispatch failed ({err[:200]}); nothing "
                  "was started", file=sys.stderr)
            return 2
        print(f"lane_ci read-map: dispatched the read-map recording on {short_ref} "
              f"for {sha[:12]}", file=sys.stderr)

        def choose(runs):
            return _newest([r for r in recording_runs(runs, sha, branch)
                            if r.get("databaseId") not in before])

    run_id, view, state = _await_run(
        slug, sha, "workflow_dispatch", choose, what="read-map", poll=poll,
        bound=bound, sleep=sleep, clock=clock)
    if view is None:
        return 2
    jobs = view.get("jobs") or []
    merged = [j.get("conclusion") for j in jobs if j.get("name") == recipe.MERGE_JOB_NAME]
    print(f"run {run_id}: {state}  jobs={len(jobs)}  wall={elapsed(view)}  "
          f"(read-map recording)")
    for line in cell_lines(cells_of(view)):
        print(line)
    print(f"  {recipe.MERGE_JOB_NAME}: {merged[0] if merged else 'absent'}")
    if merged != ["success"]:
        print("  NO MAP: the merge job did not succeed, so nothing was recorded "
              "whole; nothing is installed.")
        return 1
    return fetcher(run_id, sha, slug=slug)


def cmd_full(sha: str, *, poll: int = POLL_SECONDS, bound: int = BOUND_SECONDS,
             full_bound: int = FULL_BOUND_SECONDS, sleep=time.sleep,
             clock=time.monotonic) -> int:
    """``wait <sha> --full``: the module docstring's five steps, in order."""
    rc, url, err = _git("remote", "get-url", gate.CI_REMOTE)
    if rc != 0:
        print(f"lane_ci full: no {gate.CI_REMOTE} remote ({err})", file=sys.stderr)
        return 2
    slug = slug_from_url(url)
    rc, branch, _err = _git("symbolic-ref", "--quiet", "--short", "HEAD")
    try:
        ref = ci_ref_for(branch if rc == 0 else "")
    except ValueError as exc:
        print(f"lane_ci full: REFUSED -- {exc}", file=sys.stderr)
        return 1
    short_ref = ref[len("refs/heads/"):]

    # 1. The ref holds this sha, or the dispatch would test another commit.
    held = _ref_head(ref)
    if held != sha:
        print(f"lane_ci full: REFUSED -- {gate.CI_REMOTE} {short_ref} holds "
              f"{held[:12] or 'nothing'}, not {sha[:12]}. A dispatch runs the "
              "ref's head, so the full matrix would test that commit under this "
              "sha's name; push this sha first (lane_ci.py push).",
              file=sys.stderr)
        return 1

    # 2. The push run finishes first: it shares the dispatch's concurrency
    # group, and cancel-in-progress cancels whichever started first.
    push_id, push_view, push_state = _await_run(
        slug, sha, "push", lambda runs: choose_push_run(runs, sha, branch),
        what="full", poll=poll, bound=bound, sleep=sleep, clock=clock)
    if push_view is None:
        return 2
    print(f"lane_ci full: the push run {push_id} on {short_ref} finished: "
          f"{push_state}", file=sys.stderr)
    if push_state.startswith("failure"):
        _report(slug, push_id, push_view, push_state)
        print("lane_ci full: the full matrix is not dispatched on a sha whose "
              f"lane run is red. Re-run its failed jobs (gh run rerun {push_id} "
              "--failed) or fix and push; then --full again.", file=sys.stderr)
        return 1

    # 3. A dispatch of this sha already running is resumed, one finished is
    # read; only none, or a cancelled one, sends another.
    listed = _list_runs(slug, sha, "workflow_dispatch", "full")
    if listed is None:
        return 2
    existing = dispatch_runs(listed, sha, branch)
    last = _newest(existing)
    if last is not None and (last.get("status") != "completed"
                             or last.get("conclusion") != "cancelled"):
        known = last.get("databaseId")
        if last.get("status") != "completed":
            print(f"lane_ci full: run {known} was already dispatched for "
                  f"{sha[:12]} and is still running; waiting on it, not "
                  "dispatching again", file=sys.stderr)
        else:
            print(f"lane_ci full: the full matrix already ran on this sha (run "
                  f"{known}, {last.get('conclusion')}); reading it, not repeating "
                  "it", file=sys.stderr)

        def choose(runs):
            return next((r for r in dispatch_runs(runs, sha, branch)
                         if r.get("databaseId") == known), None)
    else:
        before = {r.get("databaseId") for r in existing}
        rc, _out, err = _gh("workflow", "run", WORKFLOW_FILE, "-R", slug,
                            "--ref", short_ref)
        if rc != 0:
            print(f"lane_ci full: the dispatch failed ({err[:200]}); nothing was "
                  "started", file=sys.stderr)
            return 2
        print(f"lane_ci full: dispatched {WORKFLOW_FILE} on {short_ref} for "
              f"{sha[:12]}", file=sys.stderr)

        def choose(runs):
            return choose_dispatch_run(runs, sha, branch, before)

    # 4. The dispatch run, BY SHA AND EVENT, then 5. its verdict and cells.
    run_id, view, state = _await_run(
        slug, sha, "workflow_dispatch", choose, what="full", poll=poll,
        bound=full_bound, sleep=sleep, clock=clock)
    if view is None:
        return 2
    return _report_full(slug, run_id, view, state)


def _report(slug: str, run_id: str, view: dict, state: str) -> int:
    jobs = view.get("jobs") or []
    print(f"run {run_id}: {state}  jobs={len(jobs)}  wall={elapsed(view)}")
    if state == "success":
        return 0
    if state == "cancelled":
        print("  cancelled -- most often superseded by a newer push to the same "
              "ci/ ref. No verdict on this sha; wait on the newer one.")
        return 2
    for name in failing_jobs(view):
        print(f"  failed job: {name}")
    rc, log, _err = _gh("run", "view", run_id, "-R", slug, "--log-failed")
    text = log if rc == 0 else ""
    ids = failing_test_ids(text)
    if ids:
        print(f"  failing tests ({len(ids)}):")
        for node in ids[:ID_LIMIT]:
            print(f"    {node}")
        if len(ids) > ID_LIMIT:
            print(f"    ... and {len(ids) - ID_LIMIT} more -- gh run view "
                  f"{run_id} --log-failed")
    lines = first_failing_lines(text)
    if lines:
        print("  first failing lines:")
        for line in lines:
            print(f"    {line}")
        if not ids:
            print("    (no failing test id found in the failed log -- the lines "
                  "above name no test; pull it yourself: gh run view "
                  f"{run_id} --log-failed)")
    elif rc != 0:
        print("    (could not fetch the failed log; no failing lines found -- "
              "pull it yourself: gh run view "
              f"{run_id} --log-failed)")
    else:
        print("    (no failing lines found in the failed log -- the run was red "
              "but nothing named the failing test)")
    return 1


def _report_full(slug: str, run_id: str, view: dict, state: str) -> int:
    """``_report``'s verdict, then every cell, then the shape check."""
    rc = _report(slug, run_id, view, state)
    cells = cells_of(view)
    for line in cell_lines(cells):
        print(line)
    for job in view.get("jobs") or []:
        if not _SHARD_JOB.match(job.get("name") or ""):
            print(f"  {job.get('name')}: {job.get('conclusion') or job.get('status')}")
    problems = matrix_problems(cells)
    if problems:
        print("  NOT THE FULL MATRIX: " + "; ".join(problems))
        return 1 if rc == 0 else rc
    shards = len(next(iter(cells.values())))
    print(f"  full matrix: {len(cells)} cells x {shards} shards = "
          f"{len(cells) * shards} shard jobs")
    return rc


def cmd_clean(branch: str, pusher=None) -> int:
    try:
        ref = ci_ref_for(branch)
    except ValueError as exc:
        print(f"lane_ci clean: REFUSED -- {exc}", file=sys.stderr)
        return 1
    argv = ["git", "push", "--no-follow-tags", gate.CI_REMOTE, f":{ref}"]
    rc = (pusher or (lambda a: subprocess.run(a).returncode))(argv)
    print(f"lane_ci clean: delete {ref} -> exit {rc}", file=sys.stderr)
    return 0 if rc == 0 else 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="lane_ci.py", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("push", help="push HEAD to ci/<branch> after the gate's checks")
    w = sub.add_parser("wait", help="wait on the CI run for a sha")
    w.add_argument("sha")
    w.add_argument("--full", action="store_true",
                   help="then dispatch the FULL matrix on ci/<branch> and wait on "
                        "that run, read by sha (resumes one already dispatched)")
    r = sub.add_parser("read-map", help="record the impact gate's read map on CI "
                                        "for a sha, and install it")
    r.add_argument("sha")
    c = sub.add_parser("clean", help="delete ci/<branch>")
    c.add_argument("branch")
    args = parser.parse_args(argv[1:])
    if args.command == "push":
        return cmd_push()
    if args.command == "wait":
        return cmd_full(args.sha) if args.full else cmd_wait(args.sha)
    if args.command == "read-map":
        return cmd_read_map(args.sha)
    return cmd_clean(args.branch)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
