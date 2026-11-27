#!/usr/bin/env python3
"""What the runner a CI shard runs on HAS: workers, CPUs, free memory.

WHY THIS FILE EXISTS. Master run 46030101439's windows shard 1 stalled in its
parallel phase (lane masterfix7's record, section 4): two 60 s ``set_content``
bounds ran out, the process-spawning files ran 2.5 to 10 times slower than on
the re-run, and the re-run of the same commit passed. Whether the runner had
fewer CPUs than usual, started fewer workers, or was short of memory could
not be read, because the job recorded none of it -- the measurement
``_audit/2026-09-21-the-windows-shard.md`` asked for in its 7.1. This records
the three facts in ONE step, before the run:

* ``xdist_workers`` -- how many workers ``-n auto`` starts in this job. Asked
  of xdist's OWN resolution (its ``pytest_xdist_auto_num_workers`` hook, in
  this interpreter and this environment), never re-derived beside it: the
  rule moves with the install (with psutil present xdist counts PHYSICAL
  cores, without it the CPUs this process may use) and with
  ``PYTEST_XDIST_AUTO_NUM_WORKERS``. ``xdist_rule`` says which branch applied.
  No conftest here implements the hook, so xdist's is the one the run calls.
* ``cpu_count`` and ``cpus_usable`` -- the machine's logical CPUs, and the ones
  this process may run on (affinity), where the platform says.
* ``memory_total_bytes`` and ``memory_available_bytes`` -- ``/proc/meminfo``'s
  MemTotal and MemAvailable on Linux, ``GlobalMemoryStatusEx`` on Windows.

The facts go to the job log as one ``runner:`` line, and to a JSON file that
``scripts/ci_shard_totals.py record --runner`` carries into the shard's report,
so the totals job can show every shard's runner side by side.

STDLIB ONLY, ubuntu and windows both, and a fact it cannot read is recorded as
``None`` with the reason under ``unknown`` -- never as a zero, and never as a
failure that would stop the shard's tests from running. ``tests/
test_ci_runner_facts.py`` runs it on whatever machine runs the suite, which on
CI is both platforms.

USAGE
    python scripts/ci_runner_facts.py --out runner-facts.json
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from pathlib import Path

GIB = 1024 ** 3


def meminfo_bytes(text: str) -> tuple[int, int] | None:
    """(MemTotal, MemAvailable) in bytes from ``/proc/meminfo``'s text, or None.

    The kernel writes both in kibibytes ("kB"). A text missing either number
    is unknown, not zero: a zero would read as a runner with no free memory.
    """
    found: dict[str, int] = {}
    for line in text.splitlines():
        name, _, rest = line.partition(":")
        parts = rest.split()
        if name in ("MemTotal", "MemAvailable") and parts and parts[0].isdigit():
            found[name] = int(parts[0]) * 1024
    if set(found) != {"MemTotal", "MemAvailable"}:
        return None
    return found["MemTotal"], found["MemAvailable"]


def _windows_memory() -> tuple[int, int]:
    """(total, available) physical memory from ``GlobalMemoryStatusEx``."""
    import ctypes  # noqa: PLC0415 -- Windows only

    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(MemoryStatusEx)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx returned 0")
    return int(status.ullTotalPhys), int(status.ullAvailPhys)


def memory(unknown: dict[str, str]) -> tuple[int | None, int | None, str]:
    """(total, available, source) in bytes; Nones and a reason when unread."""
    if sys.platform == "win32":
        try:
            total, available = _windows_memory()
            return total, available, "GlobalMemoryStatusEx"
        except (OSError, AttributeError, ValueError) as exc:
            unknown["memory"] = f"GlobalMemoryStatusEx failed: {type(exc).__name__}"
            return None, None, "GlobalMemoryStatusEx"
    path = Path("/proc/meminfo")
    try:
        read = meminfo_bytes(path.read_text(encoding="ascii", errors="replace"))
    except OSError as exc:
        unknown["memory"] = f"{path} unreadable: {type(exc).__name__}"
        return None, None, str(path)
    if read is None:
        unknown["memory"] = f"{path} holds no MemTotal and MemAvailable pair"
        return None, None, str(path)
    return read[0], read[1], f"{path} MemAvailable"


def cpus_usable(unknown: dict[str, str]) -> int | None:
    """The CPUs this process may run on, where the platform can say."""
    counter = getattr(os, "process_cpu_count", None)  # Python 3.13+
    if counter is not None:
        count = counter()
        if count:
            return int(count)
    affinity = getattr(os, "sched_getaffinity", None)  # Linux
    if affinity is not None:
        return len(affinity(0))
    unknown["cpus_usable"] = "no os.process_cpu_count or os.sched_getaffinity here"
    return None


def xdist_workers(unknown: dict[str, str]) -> tuple[int | None, str]:
    """(what ``-n auto`` starts here, which of xdist's rules decided it).

    Asks xdist's own hook implementation, so the number is the one the run
    will use. The rule is read from the same inputs the hook reads, in the
    hook's order, for the log; it does not decide the number.
    """
    try:
        from xdist.plugin import pytest_xdist_auto_num_workers  # noqa: PLC0415
    except ImportError as exc:
        unknown["xdist_workers"] = f"xdist does not import: {exc}"
        return None, "xdist absent"

    class _Option:
        numprocesses = "auto"

    class _Config:
        option = _Option()

    override = os.environ.get("PYTEST_XDIST_AUTO_NUM_WORKERS", "")
    if override.strip().lstrip("-").isdigit():
        rule = "PYTEST_XDIST_AUTO_NUM_WORKERS is set"
    else:
        try:
            import psutil  # noqa: F401, PLC0415
        except ImportError:
            rule = ("no psutil: the CPUs this process may use"
                    if hasattr(os, "sched_getaffinity")
                    else "no psutil: os.cpu_count()")
        else:
            rule = "psutil present: physical cores"
    try:
        return int(pytest_xdist_auto_num_workers(_Config())), rule
    except Exception as exc:  # noqa: BLE001 -- recorded, never raised
        unknown["xdist_workers"] = f"xdist's resolution raised {type(exc).__name__}"
        return None, rule


def gather() -> dict:
    unknown: dict[str, str] = {}
    workers, rule = xdist_workers(unknown)
    total, available, source = memory(unknown)
    return {
        "cpu_count": os.cpu_count(),
        "cpus_usable": cpus_usable(unknown),
        "xdist_workers": workers,
        "xdist_rule": rule,
        "memory_total_bytes": total,
        "memory_available_bytes": available,
        "memory_source": source,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "unknown": unknown,
    }


def _amount(value) -> str:
    return "unknown" if value is None else f"{value / GIB:.1f}"


def summary(facts: dict | None) -> str:
    """The one line a log shows; ``ci_shard_totals.py`` prints the same one."""
    if not facts:
        return "runner facts: not recorded"
    workers = facts.get("xdist_workers")
    cpus = facts.get("cpu_count")
    usable = facts.get("cpus_usable")
    return (
        f"runner: {cpus if cpus is not None else 'unknown'} CPUs "
        f"({usable if usable is not None else 'unknown'} usable); "
        f"-n auto starts {workers if workers is not None else 'unknown'} workers "
        f"({facts.get('xdist_rule')}); memory "
        f"{_amount(facts.get('memory_available_bytes'))} GiB available of "
        f"{_amount(facts.get('memory_total_bytes'))}"
        + (f"; UNKNOWN: {facts['unknown']}" if facts.get("unknown") else "")
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True, help="where to write the facts")
    args = parser.parse_args(argv[1:])
    facts = gather()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(facts, indent=2), encoding="utf-8")
    print(summary(facts), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
