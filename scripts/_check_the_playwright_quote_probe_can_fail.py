"""Can ``_probe_what_playwright_quotes.py`` CONVICT? Four ways, all shown red.

A probe that has only ever been seen green certifies nothing. This drives the
probe's verdict engine over its own committed baseline with four deliberate
corruptions, and it is itself a failure if any of them comes back PASS.

    A  a DECLARATION is flipped        -> the engine must convict the flip
    B  a strict message is REPLACED     -> a real echo reported as silence
                                           must convict
    C  the navigation rows' server log  -> "the landing is not quoted" with no
       is EMPTIED                          evidence the landing was visited is
                                           VACUOUS and must convict
    D  a raising case is made to        -> a case declared to raise that did
       NOT RAISE                           not must convict

Then the untouched baseline is replayed and must come back clean, because a
check that convicts everything is as useless as one that convicts nothing.

No browser is launched. The engine is pure and the baseline is on disk.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE = HERE / "_probe_what_playwright_quotes.py"
BASELINE = HERE / "_probe_what_playwright_quotes.json"


def _load_probe():
    spec = importlib.util.spec_from_file_location("_pwq_probe", PROBE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _fails(judged):
    return [r for r in judged if r["verdict"] != "PASS"]


def main() -> int:
    if not BASELINE.exists():
        print("MISSING BASELINE: run the probe with --json first: " + BASELINE.name)
        return 2
    probe = _load_probe()
    rows = json.loads(BASELINE.read_text(encoding="ascii"))
    decls = probe.declarations()

    problems: list[str] = []

    def expect_red(label, judged, must_mention, case_id):
        fails = _fails(judged)
        hit = [r for r in fails if r["id"] == case_id]
        print("-" * 68)
        print("CONTROL " + label)
        if not hit:
            print("  NOT CONVICTED -- this control is broken")
            problems.append(label + ": expected " + case_id + " to fail")
            return
        row = hit[0]
        print("  %s  declared=%s observed=%s" % (
            row["id"], row.get("expect"), row["observed"]))
        print("  why: " + row["why"])
        if must_mention and must_mention not in row["why"]:
            print("  WRONG REASON -- expected the reason to mention: " + must_mention)
            problems.append(label + ": wrong reason")

    # ---- A: flip one declaration ------------------------------------------
    flipped = dict(decls)
    flipped["strict.text_content"] = dict(
        flipped["strict.text_content"], expect=probe.SILENT)
    expect_red("A  declaration flipped to SILENT",
               probe.verdict(rows, flipped), "observed ECHO",
               "strict.text_content")

    # ---- B: blank out a message that really does echo ----------------------
    gutted = copy.deepcopy(rows)
    for row in gutted:
        if row["id"] == "strict.inner_text":
            row["message"] = "Locator.inner_text: something went wrong"
            row["hits"] = {"page_chosen": [], "ours": []}
            row["observed"] = probe.SILENT
    expect_red("B  a real echo replaced by a sentinel-free message",
               probe.verdict(gutted, decls), "declared ECHO",
               "strict.inner_text")

    # ---- C: empty the navigation rows' server log --------------------------
    vacuous = copy.deepcopy(rows)
    for row in vacuous:
        if row["id"] in probe.LANDING_REQUIRED:
            row["server_saw"] = []
    expect_red("C  navigation rows with no proof the landing was visited",
               probe.verdict(vacuous, decls), "VACUOUS",
               "nav.redirect_then_reset")

    # ---- D: a case declared to raise that did not --------------------------
    quiet = copy.deepcopy(rows)
    for row in quiet:
        if row["id"] == "strict.get_attribute":
            row["raised"] = False
            row["exc_type"] = None
            row["message"] = None
            row["hits"] = {"page_chosen": [], "ours": []}
            row["observed"] = probe.SILENT
    expect_red("D  a case declared to raise that did not raise",
               probe.verdict(quiet, decls), "declared to raise",
               "strict.get_attribute")

    # ---- the untouched baseline must be clean ------------------------------
    print("-" * 68)
    clean = _fails(probe.verdict(rows, decls))
    print("CONTROL E  the untouched baseline")
    if clean:
        for row in clean:
            print("  UNEXPECTED FAIL: %s -- %s" % (row["id"], row["why"]))
        problems.append("E: the untouched baseline is not clean")
    else:
        print("  %d rows, 0 failures" % len(rows))

    print("=" * 68)
    if problems:
        for line in problems:
            print("BROKEN CONTROL: " + line)
        return 1
    print("all five controls behaved: four convictions and one clean replay")
    return 0


if __name__ == "__main__":
    sys.exit(main())
