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
exit code, which is 0 on a 403. On a failure it prints the failing job names
and the first failing test lines from ``--log-failed``, truncated.

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
_FAIL_LINE = re.compile(r"(FAILED|ERROR) \S|##\[error\]|REFUS")


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


def first_failing_lines(log: str, limit: int = 20, width: int = 220) -> list[str]:
    """The first failing-test lines of a ``--log-failed`` dump, deduplicated.

    gh prefixes each line with ``<job>\\t<step>\\t<timestamp> ``; that prefix
    is cut so the line reads as pytest wrote it.
    """
    out: list[str] = []
    seen: set[str] = set()
    for raw in log.splitlines():
        text = raw.split("\t")[-1]
        text = re.sub(r"^\S+Z\s", "", text).strip()
        if not _FAIL_LINE.search(text) or text in seen:
            continue
        seen.add(text)
        out.append(text if len(text) <= width else text[:width - 3] + "...")
        if len(out) >= limit:
            break
    return out


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
    for line in first_failing_lines(log if rc == 0 else ""):
        print(f"    {line}")
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
