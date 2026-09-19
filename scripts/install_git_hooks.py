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
GATES = (
    "scripts/pre_commit_identity_gate.py",
    "scripts/pre_commit_boundary_gate.py",
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


def main() -> int:
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


if __name__ == "__main__":
    sys.exit(main())
