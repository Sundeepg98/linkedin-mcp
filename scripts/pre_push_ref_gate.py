"""Refuse to push any ref but ``master`` -- and a swept ``ci/`` ref -- because
publishing is the one thing this repository cannot take back.

WHY THIS EXISTS, and it is a measured hazard rather than a precaution.

This checkout carries 59 local branches. Ten of them are NOT ancestors of
master, and one class of them is kept deliberately: ``integrate-1821`` is the
only ref under which 22 cited SHAs resolve, and
``_audit/2026-09-20-the-six-unremapped.md`` rules it *"KEEP, do not delete, do
not push"*. Those branches carry blobs that ``scripts/purge_denied_term.py``
removed from the history that master publishes.

**Until this file existed, that protection was a sentence in an audit file.**
``git push --all`` and ``git push --mirror`` would have published every one of
them, and the repository is PUBLIC. A force-push does not undo that: retained
objects stay resolvable by SHA, and the only remedy measured to work was
delete-and-recreate, which cost this account a sibling repo's entire pull
request history once.

WHAT IT REFUSES, AND WHAT THAT IS WORTH. It refuses on the REMOTE ref, which
is the thing that becomes public -- ``git push origin HEAD:refs/heads/x`` is
caught where a check on the local ref would not be. It refuses deletes too,
naming them as deletes: removing a published ref is deliberate work and should
not ride in on a wildcard.

THE ONE EXCEPTION, ADDED 2026-10-10: ``refs/heads/ci/<name>``, so a lane can
run the free CI matrix on its own branch instead of a full suite on the one
shared box (``scripts/lane_ci.py`` is the caller; ``.github/workflows/ci.yml``
gives a ``ci/`` push a small matrix). A ``ci/`` ref is admitted ONLY when every
clause below holds, and each clause is the answer to one way the hazard above
could ride in:

1. ``origin/master`` (resolved once, to a sha) is an ANCESTOR of the pushed
   commit. Everything below that sha is already public, so the only objects
   the push can add are the commits in ``<master>..<sha>`` -- the lane's own.
   ``integrate-1821`` and its kind are not descendants of master, and that is
   exactly the clause they fail.
2. The SHIPPED identity blob sweep (``sweep_blobs_for_identity.py``, through
   its own ``load_wordlist``) reads PASS over ``<master>..<sha>`` -- every
   blob of every commit in the range, so a value added in one commit and
   removed in the next is still caught. Exit 2 (it could not speak: no
   wordlist, an empty range, nothing swept) refuses exactly as a hit does;
   **2 never means clean**, and neither does a wordlist that failed to load.
3. The push goes to the remote named ``origin``, because clause 1 is measured
   against origin's master and says nothing about what another remote serves.
4. The ``ci/`` ref is the ONLY ref in the push. ``--all`` and ``--mirror``
   offer every branch at once; a ``ci/`` line riding among others is refused
   with them, so neither can carry one out.
5. The name is plain: ``ci/`` then path components of ``[A-Za-z0-9._-]`` that
   do not start with a dot.

A DELETE of a ``ci/`` ref, alone in its push, is allowed: it publishes nothing,
and it is how ``lane_ci.py clean`` tidies up. Every other delete is still
refused and named.

WHAT IT IS NOT. Still not a purity check on master's own pushes: the master
path runs no sweep and loads no wordlist, so it works on a machine with no key
(and a CI runner has none). The sweeps for that are
``sweep_tracked_for_identity.py`` (the working tree) and
``sweep_blobs_for_identity.py`` (a commit range). For ``ci/`` the sweep is part
of the decision because no human reads a lane's range before it goes out.

MEASURED 2026-09-21, so the threat model is stated rather than assumed:
``origin`` already serves 13 refs besides master, of which ``ci-offload`` is an
ORPHAN commit with no parent, holding 498 blobs master does not have. It was
swept and reads PASS on all 218 spellings. So the accident has already
happened once, harmlessly, before anything stopped it. (``ci-offload`` is not
under ``ci/`` and stays refused, update and delete alike.)

AN EMPTY STDIN IS NOT A PASS. Git always feeds this hook at least one line for
a push that would transfer anything. Reading none means the hook was invoked in
a way this script does not understand, and saying "allowed" to that is how a
gate becomes decoration. It says so and allows, loudly, rather than pretending
it checked.

THE OVERRIDE IS DELIBERATE AND NAMED. Set ``LINKEDIN_MCP_ALLOW_ANY_REF=1`` for
one command when a non-master push is genuinely wanted. Accidents do not set
environment variables; that is the entire security model here and it is stated
rather than implied. The ``ci/`` exception does not need it and does not widen
it.

Install with ``scripts/install_git_hooks.py``. NOTE THE HOOK RUNS THE MAIN
CHECKOUT'S COPY of this file (it resolves ``git rev-parse --git-common-dir``),
so a change here governs pushes from every worktree only once it is in the
main checkout. Run by hand:

    git push --dry-run --all 2>/dev/null   # then read what this would have said
"""

from __future__ import annotations

import contextlib
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

ALLOWED_REMOTE_REFS = frozenset({"refs/heads/master"})

OVERRIDE_ENV = "LINKEDIN_MCP_ALLOW_ANY_REF"

ZERO = "0" * 40

#: The lane refs, and the only remote and base they are measured against.
CI_PREFIX = "refs/heads/ci/"
CI_REMOTE = "origin"
CI_BASE = "refs/remotes/origin/master"
_CI_NAME = re.compile(r"[A-Za-z0-9_-][A-Za-z0-9._-]*(?:/[A-Za-z0-9_-][A-Za-z0-9._-]*)*")

#: (sha) -> problems; empty means every content clause held.
CiCheck = Callable[[str], list[str]]


def is_ci_ref(remote_ref: str) -> bool:
    return remote_ref.startswith(CI_PREFIX)


def ci_name_ok(remote_ref: str) -> bool:
    name = remote_ref[len(CI_PREFIX):]
    return bool(_CI_NAME.fullmatch(name)) and ".." not in name \
        and not name.endswith(".lock")


def verdicts(lines: list[str], *, remote: str = CI_REMOTE,
             ci_check: CiCheck | None = None) -> list[tuple[str, str, str]]:
    """(verdict, remote_ref, why) for each pre-push stdin line.

    Git's format is ``<local ref> <local sha> <remote ref> <remote sha>``. A
    line this cannot parse is REFUSED rather than skipped -- an unparsed line
    is an unknown push, and the whole point of the file is to not guess.

    ``ci_check`` answers the content clauses for a ``ci/`` update; with none
    given, a ``ci/`` update is refused, so a caller that forgot to wire it
    gets the old gate's answer, never a silent allow.
    """
    rows = [raw.strip() for raw in lines if raw.strip()]
    out: list[tuple[str, str, str]] = []
    for line in rows:
        parts = line.split()
        if len(parts) != 4:
            out.append(("REFUSE", line, "unparsed line -- not 4 fields"))
            continue
        local_ref, local_sha, remote_ref, _remote_sha = parts
        if remote_ref in ALLOWED_REMOTE_REFS:
            out.append(("ALLOW", remote_ref, f"from {local_ref}"))
        elif is_ci_ref(remote_ref):
            out.append(_ci_verdict(local_ref, local_sha, remote_ref,
                                   remote=remote, alone=len(rows) == 1,
                                   ci_check=ci_check))
        elif local_sha == ZERO:
            out.append(("REFUSE", remote_ref, "this is a DELETE of a published ref"))
        else:
            out.append(("REFUSE", remote_ref, f"not master (from {local_ref})"))
    return out


def _ci_verdict(local_ref: str, local_sha: str, remote_ref: str, *,
                remote: str, alone: bool,
                ci_check: CiCheck | None) -> tuple[str, str, str]:
    if not ci_name_ok(remote_ref):
        return ("REFUSE", remote_ref,
                "not a plain ci/<name> (path components of [A-Za-z0-9._-], "
                "none starting with a dot, no '..')")
    if not alone:
        return ("REFUSE", remote_ref,
                "a ci/ ref is admitted only ALONE in its push -- --all, "
                "--mirror and multi-ref pushes stay refused")
    if remote != CI_REMOTE:
        return ("REFUSE", remote_ref,
                f"a ci/ ref is measured against {CI_REMOTE}/master, and this "
                f"push goes to {remote!r}")
    if local_sha == ZERO:
        return ("ALLOW", remote_ref, "a DELETE of a ci/ ref -- publishes nothing")
    if ci_check is None:
        return ("REFUSE", remote_ref, "no ci/ content check was wired")
    problems = ci_check(local_sha)
    if problems:
        return ("REFUSE", remote_ref, "; ".join(problems))
    return ("ALLOW", remote_ref,
            f"from {local_ref}: descends from {CI_REMOTE}/master and its new "
            "commits swept clean")


# ---------------------------------------------------------------------------
# The content clauses, asked of the PUSHING repository
# ---------------------------------------------------------------------------


def _git(*args: str) -> tuple[int, str, str]:
    """Run git in the pushing repository: the hook's cwd and git's own env."""
    out = subprocess.run(["git", *args], capture_output=True, text=True,
                         errors="replace")
    return out.returncode, out.stdout.strip(), out.stderr.strip()


@contextlib.contextmanager
def _pinned_git_dir(git_dir: str):
    """Aim the shipped sweep at the pushing repository for one call.

    The sweep runs git with ``cwd`` set to the checkout the SCRIPT lives in,
    and the hook runs the MAIN checkout's copy. Objects are shared across
    worktrees, so that resolves today -- but "it happens to share an object
    store" is not a reason, so the repository whose push this is gets named
    explicitly for the duration of the sweep and restored after.
    """
    before = os.environ.get("GIT_DIR")
    os.environ["GIT_DIR"] = git_dir
    try:
        yield
    finally:
        if before is None:
            os.environ.pop("GIT_DIR", None)
        else:
            os.environ["GIT_DIR"] = before


def _sweep(rev_range: str) -> tuple[int, str]:
    """The SHIPPED blob sweep's exit code over ``rev_range``, never a copy."""
    here = str(Path(__file__).resolve().parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    try:
        import sweep_blobs_for_identity as sweep  # noqa: PLC0415
    except SystemExit as exc:  # its import chain can exit on a broken tree
        return 2, f"the identity sweep could not be imported ({exc})"
    except Exception as exc:  # noqa: BLE001 -- any import failure refuses
        return 2, f"the identity sweep could not be imported ({type(exc).__name__})"
    rc_dir, git_dir, err = _git("rev-parse", "--absolute-git-dir")
    if rc_dir != 0 or not git_dir:
        return 2, f"cannot name the pushing repository's git dir ({err})"
    with _pinned_git_dir(git_dir), contextlib.redirect_stdout(sys.stderr):
        try:
            rc = sweep.main(["sweep_blobs_for_identity.py", rev_range])
        except SystemExit as exc:  # load_wordlist() exits when the key is absent
            code = exc.code if isinstance(exc.code, int) else 2
            return (code or 2), ("the identity wordlist did not load, so the "
                                 "sweep never ran")
    return rc, ""


def git_ci_check(sha: str, *, sweep: bool = True) -> list[str]:
    """Clauses 1 and 2 for one pushed commit; an empty list means both held.

    ``sweep=False`` answers clause 1 alone. ``scripts/lane_ci.py push`` asks
    for that and nothing else: the hook asks again with the sweep, and one
    sweep per push is the whole cost the helper exists to save. The hook path
    (``main``) never passes it, so the gate itself always sweeps.
    """
    rc, kind, _err = _git("cat-file", "-t", sha)
    if rc != 0 or kind != "commit":
        return [f"{sha[:12]} is not a commit here ({kind or 'unknown'})"]
    rc, base, _err = _git("rev-parse", "--verify", "--quiet", f"{CI_BASE}^{{commit}}")
    if rc != 0 or not base:
        return [f"{CI_BASE} does not resolve here, so there is nothing to "
                "measure ancestry against"]
    if base == sha:
        return [f"nothing above origin/master {base[:12]} to test -- a ci/ run "
                "of master's own commit says nothing master's run did not"]
    rc, _out, err = _git("merge-base", "--is-ancestor", base, sha)
    if rc == 1:
        return [f"origin/master {base[:12]} is NOT an ancestor of {sha[:12]}: "
                "this push would publish history master does not "
                "(merge origin/master into the branch first)"]
    if rc != 0:
        return [f"git merge-base --is-ancestor failed (exit {rc}): {err}"]
    if not sweep:
        return []
    rev_range = f"{base}..{sha}"
    rc, why = _sweep(rev_range)
    if rc == 0:
        return []
    if rc == 1:
        return [f"the identity sweep found hits in {base[:12]}..{sha[:12]} "
                "(file:line above, values redacted)"]
    return [f"the identity sweep could not speak over {base[:12]}..{sha[:12]} "
            f"(exit {rc}{': ' + why if why else ''}) -- 2 never means clean"]


def main(argv: list[str]) -> int:
    remote = argv[1] if len(argv) > 1 else "(unnamed)"
    lines = sys.stdin.read().splitlines()

    if not lines:
        print(f"pre-push: read NO ref lines for remote {remote}. "
              "THIS IS NOT A CHECK -- nothing was examined. Allowing, because "
              "refusing a push this script does not understand would be worse "
              "than saying so.", file=sys.stderr)
        return 0

    results = verdicts(lines, remote=remote, ci_check=git_ci_check)
    refused = [r for r in results if r[0] == "REFUSE"]

    # SAY WHAT WAS SEEN, ALWAYS -- on the allow path too. A gate that prints
    # only when it fires cannot be distinguished from one that never ran.
    allowed = len(results) - len(refused)
    if not refused:
        print(f"pre-push: {allowed} ref(s) to {remote}, all master or "
              "admitted ci/. Allowed.", file=sys.stderr)
        for _v, ref, why in results:
            print(f"    {ref}  ({why})", file=sys.stderr)
        return 0

    if os.environ.get(OVERRIDE_ENV) == "1":
        print(f"pre-push: {len(refused)} non-master ref(s) ALLOWED by "
              f"{OVERRIDE_ENV}=1:", file=sys.stderr)
        for _v, ref, why in refused:
            print(f"    {ref}  ({why})", file=sys.stderr)
        return 0

    print("", file=sys.stderr)
    print(f"PUSH REFUSED: {len(refused)} of {len(results)} ref(s) are not "
          f"{'/'.join(sorted(ALLOWED_REMOTE_REFS))} or an admitted ci/ ref.",
          file=sys.stderr)
    print("", file=sys.stderr)
    for _v, ref, why in refused:
        print(f"    {ref}", file=sys.stderr)
        print(f"        {why}", file=sys.stderr)
    print("", file=sys.stderr)
    print("This repository is PUBLIC, and branches outside master carry blobs "
          "that were", file=sys.stderr)
    print("purged from the history master publishes. Publishing is not "
          "reversible: retained", file=sys.stderr)
    print("objects stay resolvable by SHA after a force-push, and only "
          "delete-and-recreate", file=sys.stderr)
    print("was measured to remove them.", file=sys.stderr)
    print("", file=sys.stderr)
    print("A lane that wants CI pushes its branch with scripts/lane_ci.py push, "
          "which", file=sys.stderr)
    print("checks ancestry first, names the ci/ ref for you, and leaves the "
          "sweep to this hook.", file=sys.stderr)
    print("", file=sys.stderr)
    print("If you meant it, sweep the range first and then say so for one "
          "command:", file=sys.stderr)
    print("    venv/Scripts/python.exe scripts/sweep_blobs_for_identity.py "
          "'master..<ref>'", file=sys.stderr)
    print(f"    {OVERRIDE_ENV}=1 git push ...", file=sys.stderr)
    print("", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
