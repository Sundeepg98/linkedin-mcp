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

POLL_SECONDS = 20
BOUND_SECONDS = 25 * 60
FAILED_JOB_STATES = frozenset(
    {"failure", "cancelled", "timed_out", "action_required", "startup_failure"})
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


def cmd_wait(sha: str, *, poll: int = POLL_SECONDS, bound: int = BOUND_SECONDS,
             sleep=time.sleep, clock=time.monotonic) -> int:
    rc, url, err = _git("remote", "get-url", gate.CI_REMOTE)
    if rc != 0:
        print(f"lane_ci wait: no {gate.CI_REMOTE} remote ({err})", file=sys.stderr)
        return 2
    slug = slug_from_url(url)
    rc_branch, branch, _err = _git("symbolic-ref", "--quiet", "--short", "HEAD")
    deadline = clock() + bound
    run_id = None
    while True:
        if run_id is None:
            rc, out, err = _gh("run", "list", "-R", slug, "--commit", sha,
                               "--event", "push", "--limit", "50", "--json",
                               "databaseId,headSha,headBranch,event,status,"
                               "conclusion,createdAt")
            if rc == 0:
                run = choose_run(json.loads(out or "[]"), sha,
                                 branch if rc_branch == 0 else None)
                if run is not None:
                    run_id = str(run["databaseId"])
                    print(f"lane_ci wait: run {run_id} on {run['headBranch']} "
                          f"for {sha[:12]}", file=sys.stderr)
            else:
                print(f"lane_ci wait: gh run list failed ({err[:200]})",
                      file=sys.stderr)
        if run_id is not None:
            rc, out, err = _gh("run", "view", run_id, "-R", slug, "--json",
                               "status,conclusion,jobs,createdAt,startedAt,updatedAt")
            if rc == 0:
                view = json.loads(out)
                state = verdict(view)
                jobs = view.get("jobs") or []
                done = sum(1 for j in jobs if j.get("status") == "completed")
                if state != "pending":
                    return _report(slug, run_id, view, state)
                print(f"lane_ci wait: run {run_id} {view.get('status')}, "
                      f"{done}/{len(jobs)} jobs done", file=sys.stderr)
            else:
                print(f"lane_ci wait: gh run view failed ({err[:200]})",
                      file=sys.stderr)
        if clock() >= deadline:
            print(f"lane_ci wait: NO VERDICT within {bound // 60} minutes "
                  f"(run {run_id or 'never appeared'}). This is not a pass.",
                  file=sys.stderr)
            return 2
        sleep(poll)


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
    c = sub.add_parser("clean", help="delete ci/<branch>")
    c.add_argument("branch")
    args = parser.parse_args(argv[1:])
    if args.command == "push":
        return cmd_push()
    if args.command == "wait":
        return cmd_wait(args.sha)
    return cmd_clean(args.branch)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
