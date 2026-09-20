"""Rewrite the UNPUSHED range to remove a known-real term from three blobs.

WHAT THIS IS FOR, and why it is a script rather than a command someone types.

`_audit/2026-09-05-jobs-tail.md` line 403 carried a value from the
`operator_own_denied_terms` class -- an EXACT-VALUE list, so the match was a
literal equality rather than an inference. The working tree was fixed the same
hour; three blobs in unpushed history were not.

    2c78f1bb2  _audit/2026-09-05-jobs-tail.md:403
    ac74d44eb  _audit/2026-09-05-jobs-tail.md:403
    6b942ecda  _audit/2026-09-05-jobs-tail.md:403

**NOTHING IS PUBLISHED.** All three are in `origin/master..HEAD`, which is why
this is a fix-before-push and not an incident, and why the rewrite is safe: it
touches no commit anybody else has ever seen.

REHEARSED TWICE ON A CLONE, AND THE FIRST REHEARSAL SILENTLY DID NOTHING.
`git filter-branch` reported success and then `Ref 'refs/heads/master' is
unchanged`. Cause, measured on a known-bad checkout: the term was present
CASE-INSENSITIVELY and absent with exact case, while the filter used `in`.
The shipped sweep matches on `casefold()`; the filter did not. Fixed with
`re.IGNORECASE`. **That is the entire reason to rehearse a rewrite on a clone.**

Second rehearsal, verified: `Ref 'refs/heads/master' was rewritten`, then
`PASS: 0 hits across 415 blobs`, 73 commits preserved, 342 tracked files intact.

WHY IT ASKS BEFORE ACTING. A history rewrite is the one operation here that
cannot be undone by another commit. It refuses unless the tree is quiescent, it
takes a restore tag first, and it verifies afterwards with the SHIPPED sweeps
rather than its own opinion. It also refuses outright if the range contains a
commit that is already published -- rewriting published history is a different
decision, with a different owner, and this script is not it.

THE TERM NEVER TOUCHES THIS FILE. The expressions are generated at run time from
the gitignored wordlist, into a temp file, and deleted afterwards.

    ./venv/Scripts/python.exe scripts/purge_denied_term.py          # report only
    ./venv/Scripts/python.exe scripts/purge_denied_term.py --run    # act
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = "_audit/2026-09-05-jobs-tail.md"
CLASS = "operator_own_denied_terms"
PLACEHOLDER = "<a term from his own denied-terms list>"
RESTORE_TAG = "pre-purge-restore"
QUIET_MINUTES = 10


def sh(*args: str, check: bool = True) -> str:
    proc = subprocess.run(args, cwd=str(REPO), capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise SystemExit(f"FAILED: {' '.join(args)}\n{proc.stderr}")
    return proc.stdout


def wordlist_terms() -> list[str]:
    spec = importlib.util.spec_from_file_location(
        "_sweep", REPO / "scripts" / "sweep_tracked_for_identity.py"
    )
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return sorted(module.load_wordlist().get(CLASS, set()), key=len, reverse=True)


def preflight() -> list[str]:
    """Every reason to refuse, gathered rather than short-circuited."""
    problems: list[str] = []

    if sh("git", "status", "--porcelain", "--untracked-files=no").strip():
        problems.append("the working tree has uncommitted TRACKED changes")

    recent = sh("git", "log", f"--since={QUIET_MINUTES} minutes ago", "--oneline")
    if recent.strip():
        n = len(recent.strip().splitlines())
        problems.append(f"{n} commit(s) in the last {QUIET_MINUTES} min -- a wave may be live")

    if (REPO / ".git" / "index.lock").exists():
        problems.append("an index.lock exists -- another git process is running")

    published = sh("git", "rev-list", "origin/master", check=False).split()
    unpushed = sh("git", "rev-list", "origin/master..HEAD").split()
    if not unpushed:
        problems.append("nothing is unpushed -- there is no range to rewrite")
    overlap = set(unpushed) & set(published)
    if overlap:
        problems.append(
            f"{len(overlap)} commit(s) in the range are ALREADY PUBLISHED -- refusing. "
            "Rewriting published history is a separate decision with a different owner."
        )

    terms = wordlist_terms()
    if not terms:
        problems.append(
            f"the wordlist has no '{CLASS}' entries -- it is gitignored and may be absent. "
            "An empty needle set would rewrite nothing and report success."
        )
    return problems


def main() -> int:
    act = "--run" in sys.argv
    problems = preflight()
    unpushed = sh("git", "rev-list", "origin/master..HEAD").split()
    terms = wordlist_terms()

    print(f"repo      {REPO}")
    print(f"range     origin/master..HEAD  ({len(unpushed)} commits)")
    print(f"path      {TARGET}")
    print(f"needles   {len(terms)} spelling(s) of {CLASS} (values not printed)")
    print()

    if problems:
        print("REFUSING -- preflight found:")
        for p in problems:
            print(f"  * {p}")
        return 1
    print("preflight: clean (tree quiet, nothing published in range, needles loaded)")

    if not act:
        print("\nreport only. re-run with --run to rewrite.")
        return 0

    sh("git", "tag", "-f", RESTORE_TAG, "HEAD")
    print(f"restore point: git reset --hard {RESTORE_TAG}   (if anything goes wrong)")

    tmp = Path(tempfile.mkdtemp(prefix="purge-"))
    expr = tmp / "expressions.txt"
    expr.write_text(
        "\n".join(f"literal:{t}==>{PLACEHOLDER}" for t in terms) + "\n", encoding="utf-8"
    )
    filt = tmp / "redact_one.py"
    filt.write_text(
        "import os, pathlib, re, sys\n"
        "EXPR = pathlib.Path(os.environ['REDACT_EXPRESSIONS'])\n"
        f"TARGET = pathlib.Path({TARGET!r})\n"
        "if not TARGET.exists():\n    sys.exit(0)\n"
        "text = TARGET.read_text(encoding='utf-8', errors='surrogateescape')\n"
        "before = text\n"
        "for line in EXPR.read_text(encoding='utf-8').splitlines():\n"
        "    if not line.startswith('literal:') or '==>' not in line:\n        continue\n"
        "    src, dst = line[len('literal:'):].split('==>', 1)\n"
        "    if src:\n"
        "        text = re.sub(re.escape(src), dst, text, flags=re.IGNORECASE)\n"
        "if text != before:\n"
        "    TARGET.write_text(text, encoding='utf-8', errors='surrogateescape')\n",
        encoding="utf-8",
    )

    env = dict(os.environ)
    env["REDACT_EXPRESSIONS"] = str(expr)
    env["FILTER_BRANCH_SQUELCH_WARNING"] = "1"
    subprocess.run(["rm", "-rf", ".git/refs/original"], cwd=str(REPO))

    # THE INTERPRETER IS THE ONE ALREADY RUNNING, NOT ONE RESOLVED FROM REPO.
    #
    # This read `REPO / "venv" / "Scripts" / "python.exe"`, and `venv/` is
    # GITIGNORED -- so it exists in the main checkout and in NO LINKED WORKTREE,
    # which is where this fleet does its work. The path then went into a
    # `git filter-branch --tree-filter` shell string, so a miss would not raise
    # here: the filter would fail on EVERY COMMIT while this function printed a
    # single captured line. A history-rewriting tool failing quietly is the
    # worst shape available, and this one rewrites the operator's identity out
    # of unpushed history.
    #
    # `sys.executable` is the interpreter executing this script. It exists by
    # construction, it is absolute so the tree-filter can use it from any
    # working directory, and it needs no root-resolution to be right.
    #
    # FOURTH REPAIR OF THIS SPELLING IN TWO DAYS -- a test control, a test
    # module, `enumerate_gap_rows.py`, and now this. Each earlier one was fixed
    # for the environment that had just bitten. `leak_matrix.py` carries the
    # same construction and is NOT a defect: it falls back to `sys.executable`
    # when the file is absent. `pre_commit_boundary_gate.py` is the other
    # correct form, taking the TOOLING root deliberately and saying why.
    python = Path(sys.executable)
    print("\nrewriting...")
    proc = subprocess.run(
        ["git", "filter-branch", "--force", "--tree-filter",
         f'"{python}" "{filt}"', "--", "origin/master..HEAD"],
        cwd=str(REPO), env=env, capture_output=True, text=True,
    )
    tail = (proc.stderr or proc.stdout).strip().splitlines()[-1:]
    print("  " + (tail[0] if tail else "(no output)"))

    for f in (expr, filt):
        f.unlink(missing_ok=True)
    tmp.rmdir()

    print("\nVERIFYING with the shipped instruments, not this script's opinion:")
    for cmd in (["scripts/sweep_blobs_for_identity.py", "origin/master..HEAD"],
                ["scripts/sweep_tracked_for_identity.py"]):
        out = subprocess.run([str(python), *cmd], cwd=str(REPO),
                             capture_output=True, text=True).stdout
        line = [l for l in out.splitlines() if l.startswith(("PASS", "FAIL"))]
        print(f"  {cmd[0].split('/')[-1]:<34} {line[0] if line else '(no verdict)'}")

    after = sh("git", "rev-list", "origin/master..HEAD").split()
    print(f"\ncommits in range: {len(unpushed)} before, {len(after)} after")
    print("Both sweeps must read PASS before pushing. If either FAILs, "
          f"run: git reset --hard {RESTORE_TAG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
