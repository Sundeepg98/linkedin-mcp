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

PYTHON = "./venv/Scripts/python.exe"
GATES = (
    "scripts/pre_commit_identity_gate.py",
    "scripts/pre_commit_boundary_gate.py",
)

WANTED = "#!/bin/sh\n" + "".join(
    f"{PYTHON} {gate} || exit 1\n" for gate in GATES
)

#: The hook this repository installed before the boundary gate existed. Known
#: BY CONTENT so an upgrade is safe; anything else is somebody's own work.
KNOWN_IDENTITY_ONLY = (
    f"#!/bin/sh\nexec {PYTHON} {GATES[0]}\n"
)


def classify(text: str) -> str:
    if text == WANTED:
        return "current"
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
            print(f"    {PYTHON} {gate} || exit 1")
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
