"""scripts/start_chrome.ps1's restore guard, RUN: Windows PowerShell on synthetic profiles.

WHY THIS FILE EXISTS. ``tests/test_start_chrome_restore_guard.py`` reads the guard's CODE, because the
script starts a real Chrome and so, it says, CI cannot run it. The GUARD needs no Chrome, though. Its
one Chrome-facing call is ``Get-ChromeOnProfile``. The live lane ran it behaviourally on synthetic
profiles (``guard_checks_s14b.py``, G1-G15), on the operator's machine only. Lane ci-checks28 moved
those 15 cases here, so that CI's Windows cell runs them.

HOW. The guard is cut out of the TRACKED script by its own markers, from ``# --- 3c.`` up to
``$arguments = @(``. It is run alone in Windows PowerShell, with ``Get-ChromeOnProfile`` replaced by a
stub, on synthetic profiles under pytest's temp dir:

- no Chrome is looked for, started or stopped, and no port is read;
- the cut keeps the script's own text, and only the profile and the stub are the test's;
- every case is the live check's own, under its own name, with its own expectation.

WHERE IT RUNS. Under Windows PowerShell 5.1 (``powershell``), the shell the live sitting starts
Chrome with. The guard's paths are Windows paths, and the ubuntu cells have no Windows PowerShell. So
those cells SKIP these tests by name, declared in ``scripts/ci_expected_skips.json``. On Windows
nothing skips: a missing ``powershell`` there FAILS, because that would be an arrangement that stopped
working.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "start_chrome.ps1"

pytestmark = pytest.mark.skipif(
    sys.platform != "win32",
    reason="the restore guard runs in Windows PowerShell on Windows paths; this cell has neither "
           "(declared in scripts/ci_expected_skips.json)")

#: An mtime no write by the guard could leave in place.
MTIME = 1700000000


def guard_text(script: Path) -> str:
    text = script.read_text(encoding="utf-8")
    a = text.index("# --- 3c.")
    b = text.index("$arguments = @(", a)
    return text[a:b]


def prefs(**extra) -> str:
    base = {"profile": {"exit_type": "Crashed", "name": "Synth\u00e9tique"}, "browser": {"x": 1}}
    base.update(extra)
    return json.dumps(base, ensure_ascii=False, separators=(",", ":"))


def compact(value) -> str:
    return json.dumps(value, separators=(",", ":"))


NORMAL = compact({"profile": {"exit_type": "Normal"}})
PROTECTION = {"protection": {"macs": {"session": {"restore_on_startup": "SYNTHETIC0MAC"}}}}

#: The live check's 15 cases: name -> (Preferences, Chrome on the profile, -RefuseSessionRestore,
#: Secure Preferences or None).
CASES = {
    "g1": (prefs(), False, True, None),
    "g2": (prefs(copy={"exit_type": "Crashed"}), False, True, None),
    "g3": (prefs(profile={"exit_type": "Normal", "name": "Synth\u00e9tique"}), False, True, None),
    "g4": (prefs(profile={"exit_type": "Normal"}, session={"restore_on_startup": 1}), False, True, None),
    "g5": (prefs(profile={"exit_type": "Normal"},
                 session={"restore_on_startup": 4, "startup_urls": ["https://www.linkedin.com/feed/"]}),
           False, True, None),
    "g6": (compact({"profile": {"name": "x"}}), False, True, None),
    "g7": (prefs(), True, True, None),
    "g8": (compact({"profile": {"exit_type": "Normal", "exited_cleanly": False, "name": "x"}, "y": [1, 2]}),
           False, True, None),
    "g9": ('{"profile":{"exit_type":"Crashed"},"broken":', False, False, None),
    "g10": (compact({"profile": {"exit_type": "Normal"}, "other": {"exit_type": "Crashed"}}), False, True, None),
    "g11": ('{"profile":{"exit_type":"Crashed"},"broken":', False, True, None),
    "g12": (NORMAL, False, True, compact(dict(PROTECTION, session={"restore_on_startup": 1}))),
    "g13": (NORMAL, False, True, compact(dict(PROTECTION, session={
        "restore_on_startup": 4, "startup_urls": ["https://www.linkedin.com/feed/"]}))),
    "g14": (NORMAL, False, True, '{"protection":{"macs":'),
    "g15": (prefs(), False, True, compact(dict(PROTECTION, session={
        "restore_on_startup": 5, "startup_urls": ["https://example.invalid/"]}))),
}


def run_case(root: Path, name: str, script: Path) -> dict:
    body, chrome_open, refuse, secure = CASES[name]
    prof = root / name
    (prof / "Default").mkdir(parents=True)
    pf = prof / "Default" / "Preferences"
    pf.write_bytes(body.encode("utf-8"))
    before = pf.read_bytes()
    os.utime(pf, (MTIME, MTIME))
    sf = prof / "Default" / "Secure Preferences"
    if secure is not None:
        sf.write_bytes(secure.encode("utf-8"))
    secure_before = sf.read_bytes() if sf.exists() else None
    ps = root / (name + ".ps1")
    stub = ("function Get-ChromeOnProfile { param([string] $Dir) "
            + ("@([pscustomobject]@{ ProcessId = 1 })" if chrome_open else "@()") + " }\n")
    ps.write_text("$ErrorActionPreference = 'Stop'\n$ProfileDir = '" + str(prof) + "'\n"
                  + ("$RefuseSessionRestore = $true\n" if refuse else "$RefuseSessionRestore = $false\n")
                  + stub + guard_text(script) + "\n'GUARD-DONE'\n", encoding="utf-8")
    done = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps)],
                          capture_output=True, text=True, timeout=120)
    return {"exit": done.returncode, "done": "GUARD-DONE" in (done.stdout or ""), "before": before,
            "after": pf.read_bytes(), "mtime_kept": int(pf.stat().st_mtime) == MTIME,
            "tmp_left": any(prof.glob("Default/*.tmp")),
            "secure_kept": (sf.read_bytes() if sf.exists() else None) == secure_before,
            "stderr": (done.stderr or "")[-300:]}


@pytest.fixture(scope="module")
def ran(tmp_path_factory) -> dict:
    """All 15 cases, run once, in parallel: each is its own PowerShell process and its own profile."""
    assert shutil.which("powershell"), "Windows PowerShell is missing on a Windows cell"
    root = tmp_path_factory.mktemp("restore-guard")
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {name: pool.submit(run_case, root, name, SCRIPT) for name in CASES}
        return {name: future.result() for name, future in futures.items()}


#: G1's and G15's want: the one Crashed literal made Normal, every other byte as it was.
WANT_NORMAL = prefs().replace('"exit_type":"Crashed"', '"exit_type":"Normal"').encode("utf-8")


def test_g1_one_crashed_becomes_normal_every_other_byte_identical_no_bom_no_temp_left(ran) -> None:
    g = ran["g1"]
    assert g["done"], g["stderr"]
    assert g["after"] == WANT_NORMAL and not g["after"].startswith(b"\xef\xbb\xbf") and not g["tmp_left"]


def test_g2_the_literal_twice_is_left_as_it_is(ran) -> None:
    """Round 4's NIT-5: only the one exact value is the guard's."""
    g = ran["g2"]
    assert g["done"] and g["after"] == g["before"], g["stderr"]


def test_g3_normal_is_untouched_bytes_and_mtime(ran) -> None:
    g = ran["g3"]
    assert g["done"] and g["after"] == g["before"] and g["mtime_kept"], g["stderr"]


def test_g4_continue_where_you_left_off_is_refused_under_the_switch(ran) -> None:
    """Round 4's NIT-5: exit 5, and nothing after the guard runs."""
    g = ran["g4"]
    assert g["exit"] == 5 and not g["done"], (g["exit"], g["stderr"])


def test_g5_a_linkedin_startup_page_is_refused_under_the_switch(ran) -> None:
    g = ran["g5"]
    assert g["exit"] == 5 and not g["done"], (g["exit"], g["stderr"])


def test_g6_no_exit_type_at_all_is_untouched(ran) -> None:
    g = ran["g6"]
    assert g["done"] and g["after"] == g["before"], g["stderr"]


def test_g7_with_a_chrome_on_the_profile_a_crashed_profile_is_left_as_it_is(ran) -> None:
    g = ran["g7"]
    assert g["done"] and g["after"] == g["before"], g["stderr"]


def test_g8_exited_cleanly_false_becomes_true_and_no_other_byte_moves(ran) -> None:
    """The orchestrator's 14b rulings, NIT-5: JSON-aware, the two keys only."""
    g = ran["g8"]
    assert g["done"], g["stderr"]
    assert g["after"] == g["before"].replace(b'"exited_cleanly":false', b'"exited_cleanly":true')


def test_g9_a_preferences_that_does_not_parse_is_left_as_it_is_without_the_switch(ran) -> None:
    g = ran["g9"]
    assert g["done"] and g["after"] == g["before"], g["stderr"]


def test_g10_crashed_under_another_key_is_left_as_it_is(ran) -> None:
    """NIT-5: ``other.exit_type`` is not ``profile.exit_type``."""
    g = ran["g10"]
    assert g["done"] and g["after"] == g["before"], g["stderr"]


def test_g11_a_preferences_that_does_not_parse_is_refused_under_the_switch_untouched(ran) -> None:
    """What it would reopen cannot be ruled out."""
    g = ran["g11"]
    assert g["exit"] == 5 and not g["done"] and g["after"] == g["before"], (g["exit"], g["stderr"])


def test_g12_continue_where_you_left_off_held_in_secure_preferences_is_refused(ran) -> None:
    """Round 5's NIT-5 clause: on Windows Chrome keeps a tracked pref's value in Secure
    Preferences. Neither file is written."""
    g = ran["g12"]
    assert g["exit"] == 5 and not g["done"], (g["exit"], g["stderr"])
    assert g["after"] == g["before"] and g["secure_kept"]


def test_g13_a_linkedin_startup_page_held_in_secure_preferences_is_refused(ran) -> None:
    g = ran["g13"]
    assert g["exit"] == 5 and not g["done"] and g["secure_kept"], (g["exit"], g["stderr"])


def test_g14_a_secure_preferences_that_does_not_parse_is_refused_under_the_switch(ran) -> None:
    g = ran["g14"]
    assert g["exit"] == 5 and not g["done"], (g["exit"], g["stderr"])
    assert g["after"] == g["before"] and g["secure_kept"]


def test_g15_control_a_harmless_startup_setting_in_secure_preferences_starts(ran) -> None:
    """Preferences' Crashed still becomes Normal, and Secure Preferences is never written."""
    g = ran["g15"]
    assert g["done"] and g["after"] == WANT_NORMAL and g["secure_kept"], g["stderr"]
