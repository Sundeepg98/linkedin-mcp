"""Install the pre-commit hook: ONE file, TWO checks, and never a silent clobber.

``.git/hooks/pre-commit`` IS A SINGLE FILE. A second hook does not coexist with
the first -- it replaces it -- and the failure mode is silent: the check that
was there stops running and nobody is told. So this repository has one hook
entry point that calls both gates, and this script is the only sanctioned way
to write it.

TWO THINGS IT REFUSES TO DO, and both are the same lesson.

**It will not overwrite a hook it does not recognise.** If the installed hook
is neither absent, nor the known identity-only form, nor already current, this
script REPORTS and exits non-zero rather than replacing it. Somebody wrote that
file for a reason and a tool that silently discards it is the exact defect the
single-file constraint creates.

**The first gate is not run with ``exec``.** The identity-only hook used
``exec``, which REPLACES THE SHELL -- so anything appended after that line
would never run, and an installer that naively appended a second command would
produce a hook that looks like two checks and is one. That is the shadowing
failure in its most convincing disguise: the file reads correctly.

WHAT IT WRITES::

    #!/bin/sh
    ./venv/Scripts/python.exe scripts/pre_commit_identity_gate.py || exit 1
    ./venv/Scripts/python.exe scripts/pre_commit_boundary_gate.py || exit 1

IDEMPOTENT. Running it twice is a no-op and says so.

PER-CHECKOUT AND UNTRACKED. ``.git/hooks/`` is not version controlled, so this
protects this working copy and nothing else -- not a clone, not CI, not a
teammate's tree. Both gates say the same thing in their own docstrings. The
repo-wide guarantee is the tests; hooks only make forgetting harder here.

    ./venv/Scripts/python.exe scripts/install_git_hooks.py          # install
    ./venv/Scripts/python.exe scripts/install_git_hooks.py --check  # report only
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HOOK = REPO / ".git" / "hooks" / "pre-commit"

LEGACY_PYTHON = "./venv/Scripts/python.exe"
#: ONLY THE IDENTITY GATE RUNS IN THE HOOK. The boundary gate moved to CI
#: on 2026-09-19, which is what its own docstring asked for: "THIS IS AN
#: INTERIM. The right owner of this check is CI ... this box is windows
#: py3.13 only -- two of three cells have never been exercised here."
#:
#: THE TRADE IS STATED RATHER THAN ASSUMED. The hook cost 142-240s on any
#: commit touching tests/, because one staged test file drags in eighteen
#: coupled ones; the identity gate costs 0.203s. That 240s was also a
#: CONCURRENCY tax -- one .git/index lock means every wave queues behind
#: every other wave's hook. On 2026-09-19 it serialised four waves, left
#: three finished pieces of work stranded in the index, killed one commit
#: process at five minutes still holding the lock, and swept one wave's
#: audit file into a neighbour's commit during the window it held open.
#:
#: THE SPLIT IS BY WHAT EACH GATE GUARDS. The identity gate guards a PUSH
#: and CANNOT run on a runner -- its wordlist is gitignored and absent from
#: every clone -- so it stays local. The boundary gate guards a BUILD and
#: runs better on three platforms than on one, so it goes. What is given up:
#: a test regression now surfaces in ~7 minutes rather than before the
#: commit exists. That is a real cost and it is the one being chosen.
GATES = (
    "scripts/pre_commit_identity_gate.py",
)

#: BOTH ROOTS COME FROM GIT, AND THEY ARE DELIBERATELY TWO ANSWERS. The
#: interpreter and the gate scripts come from the checkout that owns venv/
#: (--git-common-dir resolves there from inside any linked worktree); each gate
#: then works out for itself which TREE is being committed. Hard-coding one root
#: for both is what broke this hook twice on 2026-09-19 -- first it could not
#: find the interpreter from a worktree at all, then it found it and certified
#: the main checkout's files against the worktree's index.
WANTED = (
    "#!/bin/sh\n"
    "# RESOLVE THE INTERPRETER AGAINST THE MAIN CHECKOUT, NOT THE CWD.\n"
    "#\n"
    "# This read './venv/Scripts/python.exe' until 2026-09-19. Linked worktrees\n"
    "# SHARE this hooks directory but have no venv of their own, so every worktree\n"
    "# agent hit \"interpreter not found\" -- and three reported, independently and\n"
    "# in the same hour, that the tempting fix at that moment is --no-verify.\n"
    "# A gate that cannot run is indistinguishable from a gate that passed, and\n"
    "# the one it disarms first is the identity gate.\n"
    "#\n"
    "# git rev-parse --git-common-dir resolves to the MAIN repository's .git from\n"
    "# inside any linked worktree, so its parent owns the venv. Each gate then\n"
    "# resolves the TREE BEING COMMITTED for itself -- two roots, two questions.\n"
    "COMMON=$(git rev-parse --git-common-dir 2>/dev/null) || exit 0\n"
    'ROOT=$(cd "$(dirname "$COMMON")" && pwd)\n'
    'PY="$ROOT/venv/Scripts/python.exe"\n'
    "\n"
    "# NOT FOUND IS A LOUD ALLOW, NEVER A SILENT ONE. A missing interpreter is\n"
    "# infrastructure rather than a red guard, and refusing on it is how a hook\n"
    "# earns a bypass habit -- but passing in silence is how it stops being a gate.\n"
    'if [ ! -x "$PY" ]; then\n'
    '  echo "pre-commit: interpreter not found at $PY -- GATES DID NOT RUN. Allowing." >&2\n'
    "  exit 0\n"
    "fi\n"
    "\n"
) + "".join(f'"$PY" "$ROOT/{gate}" || exit 1\n' for gate in GATES)

#: The relative-path body this script emitted until 2026-09-19. Known BY CONTENT
#: so --check reports it as upgradeable rather than "unrecognised", which would
#: refuse to touch it and leave every fresh clone with a hook that cannot run.
LEGACY_RELATIVE = "#!/bin/sh\n" + "".join(
    f"{LEGACY_PYTHON} {gate} || exit 1\n" for gate in GATES
)

#: The hook this repository installed before the boundary gate existed. Known
#: BY CONTENT so an upgrade is safe; anything else is somebody's own work.
KNOWN_IDENTITY_ONLY = (
    f"#!/bin/sh\nexec {LEGACY_PYTHON} {GATES[0]}\n"
)


def classify(text: str) -> str:
    if text == WANTED:
        return "current"
    if text.strip() == LEGACY_RELATIVE.strip():
        return "legacy-relative"
    if text.strip() == KNOWN_IDENTITY_ONLY.strip():
        return "identity-only"
    return "unrecognised"


def install_pre_commit() -> int:
    check_only = "--check" in sys.argv

    if not HOOK.parent.exists():
        print(f"REFUSED: {HOOK.parent} does not exist. Is this a git checkout?")
        return 2

    if HOOK.exists():
        state = classify(HOOK.read_text(encoding="utf-8"))
    else:
        state = "absent"

    print(f"pre-commit hook: {state}")
    print(f"  path   : {HOOK}")
    print(f"  gates  : {', '.join(GATES)}")

    if state == "current":
        print("  nothing to do.")
        return 0

    if state == "unrecognised":
        print()
        print("REFUSED: the installed hook is neither the known identity-only")
        print("form nor the current one, so somebody wrote it deliberately.")
        print("A single-file hook means installing over it would DISCARD it")
        print("silently. Merge the two gate lines in by hand:")
        print()
        for gate in GATES:
            print(f"    {LEGACY_PYTHON} {gate} || exit 1")
        return 3

    if check_only:
        print()
        print(f"  --check: would upgrade from {state!r} to 'current'.")
        return 1

    HOOK.write_text(WANTED, encoding="utf-8")
    try:
        HOOK.chmod(0o755)
    except OSError:
        # Windows checkouts often cannot, and git for Windows does not need it.
        pass
    # VERIFY BY READING IT BACK, never from the absence of an exception.
    written = classify(HOOK.read_text(encoding="utf-8"))
    print()
    print(f"  installed. re-read says: {written}")
    if written != "current":
        print("  REFUSED-AFTER-THE-FACT: the file on disk is not what was written.")
        return 4
    print("  NOTE: .git/hooks is per-checkout and untracked. This protects this")
    print("  working copy only. Bypass when you mean it: git commit --no-verify")
    return 0


# ---------------------------------------------------------------------------
# THE SECOND HOOK. A DIFFERENT FILE, A DIFFERENT EVENT, AND ONE GATE IN IT.
# ---------------------------------------------------------------------------
#: ``exec`` IS CORRECT HERE AND WRONG IN THE PRE-COMMIT HOOK, which is worth
#: saying out loud because this file's own docstring warns against it. That
#: warning is about APPENDING a second command after an exec line -- the shell
#: is replaced, so the second gate never runs and the file still reads as if it
#: does. This hook runs exactly one gate and must hand it git's stdin unchanged
#: (the ref lines ARE the input), so exec is the honest spelling. If a second
#: pre-push gate is ever added, exec has to go first.
PUSH_HOOK = REPO / ".git" / "hooks" / "pre-push"
PUSH_GATE = "scripts/pre_push_ref_gate.py"

PUSH_WANTED = (
    "#!/bin/sh\n"
    "# Resolve the interpreter against the MAIN checkout, not the cwd -- linked\n"
    "# worktrees share this hooks directory and have no venv of their own. Same\n"
    "# reasoning, and the same 2026-09-19 scar, as the pre-commit hook above.\n"
    "COMMON=$(git rev-parse --git-common-dir 2>/dev/null) || exit 0\n"
    'ROOT=$(cd "$(dirname "$COMMON")" && pwd)\n'
    'PY="$ROOT/venv/Scripts/python.exe"\n'
    "\n"
    "# NOT FOUND IS A LOUD ALLOW. Refusing every push because of infrastructure\n"
    "# is how a gate earns a --no-verify habit; passing in silence is how it\n"
    "# stops being a gate. Say which happened.\n"
    'if [ ! -x "$PY" ]; then\n'
    '  echo "pre-push: interpreter not found at $PY -- REF GATE DID NOT RUN. Allowing." >&2\n'
    "  exit 0\n"
    "fi\n"
    "\n"
    f'exec "$PY" "$ROOT/{PUSH_GATE}" "$@"\n'
)


def classify_push(text: str) -> str:
    return "current" if text == PUSH_WANTED else "unrecognised"


def install_pre_push() -> int:
    check_only = "--check" in sys.argv
    state = "absent" if not PUSH_HOOK.exists() else classify_push(
        PUSH_HOOK.read_text(encoding="utf-8"))

    print()
    print(f"pre-push hook: {state}")
    print(f"  path   : {PUSH_HOOK}")
    print(f"  gate   : {PUSH_GATE}")

    if state == "current":
        print("  nothing to do.")
        return 0

    if state == "unrecognised":
        print()
        print("REFUSED: a pre-push hook is already installed and this script")
        print("did not write it. Somebody wrote that file deliberately and a")
        print("single-file hook means installing over it would DISCARD it.")
        return 3

    if check_only:
        print()
        print("  --check: would install the ref gate.")
        return 1

    PUSH_HOOK.write_text(PUSH_WANTED, encoding="utf-8")
    try:
        PUSH_HOOK.chmod(0o755)
    except OSError:
        pass
    written = classify_push(PUSH_HOOK.read_text(encoding="utf-8"))
    print()
    print(f"  installed. re-read says: {written}")
    if written != "current":
        print("  REFUSED-AFTER-THE-FACT: the file on disk is not what was written.")
        return 4
    print("  It refuses any REMOTE ref but refs/heads/master, deletes included.")
    print("  Override for one command: LINKEDIN_MCP_ALLOW_ANY_REF=1 git push ...")
    return 0


def main() -> int:
    # BOTH RUN, AND THE WORSE CODE WINS. Returning early on the first hook's
    # result would mean a healthy pre-commit hook silently skips installing the
    # pre-push one -- the same shadowing this file exists to prevent, one level
    # up.
    commit_rc = install_pre_commit()
    push_rc = install_pre_push()
    return max(commit_rc, push_rc)


if __name__ == "__main__":
    sys.exit(main())
