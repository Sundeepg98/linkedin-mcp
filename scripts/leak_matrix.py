"""Run every leak test against every credential-echo transform, print the grid.

One cell per (test, transform). A cell is only acceptable RED: the build under
test is deliberately leaking the operator's session cookie, so a green cell is
a leak the suite would have shipped.

    venv/Scripts/python scripts/leak_matrix.py

Prints a table and exits non-zero if any cell is green. Takes a few minutes:
each transform is a full pytest session over the six guarded tests.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from credential_echo_control import TRANSFORMS  # noqa: E402

#: The six assertions that exist to keep the credential inside the process.
GUARDED = (
    "tests/test_auth.py::test_no_cookie_value_ever_reaches_a_tool_result",
    "tests/test_auth.py::test_no_cookie_value_leaks_from_the_login_result",
    "tests/test_auth.py::test_session_info_never_returns_a_cookie_value",
    "tests/test_auth_lifecycle.py::test_the_offline_result_carries_no_cookie_value",
    "tests/test_auth_lifecycle.py::test_the_live_result_carries_no_cookie_value",
    "tests/test_auth_lifecycle.py::test_a_logout_result_carries_no_cookie_value",
)

PY = str(REPO / "venv" / "Scripts" / "python.exe")
if not Path(PY).is_file():  # posix / CI
    PY = sys.executable


def run(transform: str) -> dict[str, str]:
    env = dict(os.environ)
    env["LINKEDIN_LEAK_TRANSFORM"] = transform
    env["PYTHONPATH"] = str(REPO / "scripts")
    proc = subprocess.run(
        [PY, "-m", "pytest", "-p", "credential_echo_control", "-q", "--no-header",
         "-rA", "--tb=no", *GUARDED],
        cwd=str(REPO), env=env, capture_output=True, text=True,
    )
    verdicts: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        for name in GUARDED:
            short = name.split("::")[-1]
            if line.startswith("PASSED ") and line.rstrip().endswith(short):
                verdicts[short] = "GREEN"
            elif line.startswith("FAILED ") and short in line:
                verdicts[short] = "red"
    return verdicts


def main() -> int:
    shorts = [n.split("::")[-1] for n in GUARDED]
    width = max(len(t) for t in TRANSFORMS) + 2
    print("\ncell = verdict of that leak test under that leaking build")
    print("red = the leak was caught.  GREEN = the leak shipped.\n")
    header = "transform".ljust(width) + "".join(f"{i + 1:>4}" for i in range(len(shorts)))
    print(header)
    print("-" * len(header))

    green_cells = 0
    for transform in TRANSFORMS:
        verdicts = run(transform)
        row = transform.ljust(width)
        for short in shorts:
            v = verdicts.get(short, "??")
            green_cells += v != "red"
            row += f"{('.' if v == 'red' else v[0].upper() if v != '??' else '?'):>4}"
        print(row)

    print("\n  . = red (leak caught)   G = GREEN (leak shipped)   ? = not run\n")
    for i, short in enumerate(shorts, 1):
        print(f"  {i}. {short}")
    print(f"\ngreen cells: {green_cells} of {len(TRANSFORMS) * len(shorts)}")
    return 1 if green_cells else 0


if __name__ == "__main__":
    raise SystemExit(main())
