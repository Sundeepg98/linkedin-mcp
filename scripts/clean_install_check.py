"""Prove this server survives a CLEAN install. Run it before you trust a green suite.

WHY
---
A local venv is a cache of a resolve that happened in the past. It cannot tell
you what a resolve TODAY would produce, and that gap is not theoretical:

    On 2026-08-20 the sibling naukri server declared `mcp[cli]>=1.25.0` with no
    upper bound. `mcp 2.0.0` shipped, relocating `mcp/server/fastmcp` to
    `mcp/server/mcpserver`. Every LOCAL naukri run stayed green -- that venv
    held an mcp installed before 2.0.0 existed. A clean resolve picked 2.0.0 and
    all 55 test modules died at collection: "5 deselected, 55 errors", zero
    tests run. The local venv hid a completely broken clean install for a day.

This script is the check that would have caught it, and the only kind that can:
it throws the cached resolve away and starts from the declared requirements.
tests/test_requirements_pins.py answers the neighbouring question -- whether the
two DECLARATIONS agree with each other -- and deliberately never installs
anything. Neither check substitutes for the other.

THE TWO THINGS IT CATCHES THAT ARE SPECIFIC TO THIS SERVER
----------------------------------------------------------
1. DECLARED VERSUS INSTALLED (step 5). requirements.txt says `fastmcp>=2.0,<4`;
   step 5 asks the fresh venv what it actually got and checks the answer against
   every declared bound. This is the half the pins test structurally cannot do,
   because the pins test refuses to look at an installed version at all -- and
   it is the half that notices when a bound is satisfied on paper by a resolve
   nobody expected.

2. PLAYWRIGHT'S BROWSER BINARIES ARE NOT A PIP ARTIFACT. `pip install
   playwright` installs the driver; the Chromium build arrives through a
   separate `playwright install chromium`. Because this server imports
   playwright LAZILY (measured 2026-08-21: no playwright module is loaded by
   `import linkedin_own_server.server`), a venv missing either one still imports
   perfectly and still passes this script's import probe. Step 4 therefore
   imports the playwright driver EXPLICITLY, and step 8 says out loud that the
   browser binaries were never fetched here, so nobody reads a PASS as "a tool
   call would work on this machine". It would not.

WHAT IT DOES
------------
  1. materialise a throwaway checkout -- `git clone` (COMMITTED state only) when
     this repo has its own .git, otherwise a filesystem copy, LOUDLY announced
     because a copy carries uncommitted working-tree state a clone would not
  2. build a brand new venv
  3. run the documented install recipe: `pip install -r requirements.txt`
  4. import the server, and the playwright driver, and report versions
  5. reconcile every DECLARED bound against what the venv actually installed
  6. print the full resolve, so a future reader can see what "today" meant
  7. run the suite
  8. summarise, including what this check does NOT cover

USAGE
-----
    python scripts/clean_install_check.py [--workdir DIR] [--keep]

`--workdir` defaults to a temp directory beside the repo (a throwaway venv with
playwright is ~200 MB; do not put it on a full C:). The workspace is deleted on
success unless `--keep` is passed. The live tree is never modified.

Exit code 0 means a clean install works. Non-zero means it does not, which is a
live bug even if every local run is green -- ESPECIALLY if every local run is
green.
"""

import argparse
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REPO_NAME = REPO.name

# The documented recipe, as pip argument lists. Keep this in step with whatever
# the README ends up saying: if the two disagree, one of them is lying to a new
# developer.
INSTALL = [
    ["install", "-r", "requirements.txt"],
]

# Never copied into the throwaway checkout. `_state` leads the list for a reason
# that is not disk space: it holds the persistent Chrome profile with the
# operator's live LinkedIn session cookies, and there is no reason for a
# throwaway workspace to hold a second copy of a working login.
COPY_EXCLUDES = shutil.ignore_patterns(
    "_state", ".git", "venv", ".venv", "__pycache__", ".pytest_cache",
    "*.egg-info", "build", "dist", "chrome-profile", "browser_profile",
)

IMPORT_PROBE = (
    "import linkedin_own_server, linkedin_own_server.server; "
    "import importlib.metadata as md; "
    "print('linkedin_own_server', linkedin_own_server.__version__, "
    "'on fastmcp', md.version('fastmcp')); "
    # Imported explicitly because the server does NOT import it at module level.
    # Without this line a venv with no playwright at all would sail through the
    # probe and only fail on the first tool call.
    "import playwright.async_api; "
    "print('playwright driver', md.version('playwright'), 'imports OK')"
)


def run(cmd, cwd, timeout=2400):
    """Run one command, echo it and its output verbatim, return (rc, output)."""
    print("\n$ %s\n  (cwd=%s)" % (subprocess.list2cmdline(cmd), cwd), flush=True)
    started = time.time()
    proc = subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    print(out, flush=True)
    print("[exit %d in %.1fs]" % (proc.returncode, time.time() - started), flush=True)
    return proc.returncode, out


def summary_line(output):
    """pytest's own summary line, quoted rather than re-counted.

    Its ABSENCE is the loudest possible result: it means pytest never got as far
    as running anything, which is exactly what a collection-time import failure
    looks like.
    """
    pattern = re.compile(
        r"\b\d+\s+(passed|failed|error|errors|deselected|skipped)\b|no tests ran"
    )
    for line in reversed(output.splitlines()):
        if pattern.search(line):
            return line.rstrip()
    return "<no pytest summary line was printed -- pytest never ran a test>"


def is_own_git_repo(path):
    """True only if `path` is the ROOT of a git work tree.

    Measured 2026-08-21: linkedin-own is NOT one. Its files live under a
    `mcp-servers/` path that the parent job-hunting repo gitignores wholesale
    ("Standalone projects (each has/will have own git repo)"), so a clone of the
    parent would not contain this server either. The sibling instahyre server
    DOES have its own .git, which is the shape this repo is expected to grow
    into -- so the clone path below is not dead code, it is the path this check
    takes the day someone runs `git init` here.
    """
    return (path / ".git").exists()


def materialise(checkout, workspace):
    """Put a throwaway copy of this repo at `checkout`. Returns a mode string."""
    if is_own_git_repo(REPO):
        rc, _ = run(
            ["git", "clone", "--no-hardlinks", "--quiet", str(REPO), str(checkout)],
            cwd=workspace,
        )
        if rc or not checkout.is_dir():
            return None
        run(["git", "log", "--oneline", "-1"], cwd=checkout)
        return "git clone (COMMITTED state only)"

    print(
        "\n!! %s has no .git of its own, so there is no committed state to clone."
        "\n!! Falling back to a FILESYSTEM COPY of the working tree."
        "\n!! Read the result accordingly: this checks the files as they sit on"
        "\n!! disk right now, INCLUDING uncommitted edits. A clone would have"
        "\n!! checked what a fresh cloner gets, which is the stronger question."
        "\n!! Run `git init` here and this check gets stronger for free." % REPO,
        flush=True,
    )
    shutil.copytree(REPO, checkout, ignore=COPY_EXCLUDES)
    return "filesystem copy (UNCOMMITTED working tree)"


# --- declared versus installed -----------------------------------------------
#
# Parsed here with ten lines of stdlib rather than by importing
# tests/test_requirements_pins.py or `packaging`. Two reasons, both practical:
# this script runs in the PARENT interpreter, where neither pytest nor packaging
# is guaranteed to exist, and it reads the requirements file of the THROWAWAY
# CHECKOUT, not of the tree it was launched from. The comparison below handles
# only the operators this project actually uses and reports anything else as
# UNKNOWN rather than passing it -- a check that silently approves what it
# cannot parse is worse than no check.

def requirement_lines(path):
    """The non-comment, non-blank requirement lines of a pip file."""
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line and not line.startswith("-"):
            lines.append(line)
    return lines


def split_requirement(line):
    """`fastmcp>=2.0,<4` -> ("fastmcp", [(">=", "2.0"), ("<", "4")])."""
    head = re.match(r"^\s*([A-Za-z][A-Za-z0-9_.\-]*)(\[[^\]]*\])?", line)
    name = head.group(1).lower()
    tail = line[head.end():].split(";", 1)[0]
    clauses = []
    for part in tail.split(","):
        part = part.strip()
        if not part:
            continue
        op = re.match(r"^(>=|<=|==|!=|~=|>|<)\s*(.+)$", part)
        clauses.append((op.group(1), op.group(2).strip()) if op else ("?", part))
    return name, clauses


def version_tuple(text):
    """A comparable tuple of the leading numeric components of a version.

    `1.58.0` -> (1, 58, 0). Non-numeric suffixes are truncated, so `1.4.0b1`
    compares equal to `1.4.0`. That is a real limitation and it is stated rather
    than hidden: this is a bounds smoke check, not a PEP 440 implementation.
    """
    parts = []
    for chunk in str(text).split("."):
        digits = re.match(r"\d+", chunk)
        if not digits:
            break
        parts.append(int(digits.group(0)))
    return tuple(parts)


def satisfies(installed, op, wanted):
    """Does `installed` satisfy one clause? None means "cannot tell"."""
    got, want = version_tuple(installed), version_tuple(wanted)
    width = max(len(got), len(want))
    got = got + (0,) * (width - len(got))
    want = want + (0,) * (width - len(want))
    if op == ">=":
        return got >= want
    if op == ">":
        return got > want
    if op == "<=":
        return got <= want
    if op == "<":
        return got < want
    if op == "==":
        return got == want
    if op == "!=":
        return got != want
    return None


def installed_versions(py, cwd):
    """{name: version} as the fresh venv reports it, from `pip list --format=freeze`."""
    rc, out = run([str(py), "-m", "pip", "list", "--format=freeze"], cwd=cwd)
    found = {}
    if rc:
        return found
    for line in out.splitlines():
        if "==" in line:
            name, _, version = line.partition("==")
            found[name.strip().lower().replace("_", "-")] = version.strip()
    return found


def reconcile(checkout, installed):
    """Check every declared bound against what got installed. Returns problems."""
    problems = []
    for line in requirement_lines(checkout / "requirements.txt"):
        name, clauses = split_requirement(line)
        version = installed.get(name.replace("_", "-"))
        if version is None:
            problems.append("%s is declared but NOT INSTALLED" % name)
            print("  %-14s DECLARED %-18s -> NOT INSTALLED" % (name, line))
            continue
        for op, wanted in clauses:
            verdict = satisfies(version, op, wanted)
            if verdict is None:
                problems.append("%s: cannot evaluate %r%s" % (name, op, wanted))
                mark = "UNKNOWN OPERATOR"
            elif verdict:
                mark = "ok"
            else:
                problems.append("%s %s violates %s%s" % (name, version, op, wanted))
                mark = "VIOLATED"
            print("  %-14s installed %-10s vs %s%-8s  %s"
                  % (name, version, op, wanted, mark))
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--workdir", default=None, help="where to build the throwaway venv")
    parser.add_argument("--keep", action="store_true", help="do not delete the workspace")
    args = parser.parse_args()

    workspace = Path(args.workdir) if args.workdir else REPO.parent / ("_cleaninstall_" + REPO_NAME)
    checkout = workspace / REPO_NAME
    venv = workspace / "venv"
    py = venv / "Scripts" / "python.exe"
    if not sys.platform.startswith("win"):
        py = venv / "bin" / "python"

    print("=" * 78)
    print("CLEAN-INSTALL CHECK: %s   %s" % (REPO_NAME, time.strftime("%Y-%m-%d %H:%M:%S")))
    print("workspace: %s  (throwaway; the live tree at %s is never touched)" % (workspace, REPO))
    print("=" * 78)

    if workspace.exists():
        shutil.rmtree(workspace, ignore_errors=True)
    workspace.mkdir(parents=True, exist_ok=True)

    failures = []

    print("\n--- STEP 1: materialise a throwaway checkout ---")
    mode = materialise(checkout, workspace)
    if mode is None or not checkout.is_dir():
        print("\nCLEAN INSTALL: FAIL (could not materialise a checkout)")
        return 1

    print("\n--- STEP 2: brand new venv ---")
    rc, _ = run([sys.executable, "-m", "venv", str(venv)], cwd=workspace)
    if rc:
        print("\nCLEAN INSTALL: FAIL (venv creation)")
        return 1
    run([str(py), "-m", "pip", "install", "--upgrade", "--quiet", "pip"], cwd=checkout)

    print("\n--- STEP 3: the documented install recipe ---")
    for pip_args in INSTALL:
        rc, _ = run([str(py), "-m", "pip"] + pip_args, cwd=checkout)
        if rc:
            failures.append("pip " + " ".join(pip_args))

    print("\n--- STEP 4: import the server, and the playwright driver ---")
    rc, _ = run([str(py), "-c", IMPORT_PROBE], cwd=checkout)
    if rc:
        failures.append("import probe")

    print("\n--- STEP 5: every DECLARED bound against what was INSTALLED ---")
    installed = installed_versions(py, checkout)
    if not installed:
        failures.append("could not read the installed set")
    else:
        problems = reconcile(checkout, installed)
        failures.extend(problems)

    print("\n--- STEP 6: what a resolve TODAY actually picked (full) ---")
    for name in sorted(installed):
        print("  %s==%s" % (name, installed[name]))

    print("\n--- STEP 7: the suite ---")
    rc, out = run([str(py), "-m", "pytest"], cwd=checkout)
    if rc:
        failures.append("pytest (exit %d)" % rc)

    print("\n" + "=" * 78)
    print("checkout mode: %s" % mode)
    print("pytest summary line (verbatim): %s" % summary_line(out))
    print("failed steps: %s" % ("; ".join(failures) if failures else "none"))
    print("CLEAN INSTALL: %s" % ("FAIL" if failures else "PASS"))
    print("NOT COVERED by this PASS: `playwright install chromium` was never run"
          " here, so no browser binary exists in that venv and no tool call"
          " could actually reach LinkedIn from it.")
    print("=" * 78)

    if not failures and not args.keep:
        shutil.rmtree(workspace, ignore_errors=True)
        print("workspace removed (pass --keep to inspect it)")
    else:
        print("workspace kept at %s" % workspace)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
