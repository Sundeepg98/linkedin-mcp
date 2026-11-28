"""A skip declared BY CELL holds on every cell: a cell that must skip a test skips it by name, and a
cell that must run it ran it.

WHY THIS FILE EXISTS. ``scripts/ci_expected_skips.json`` declared skips by NAME, and the totals job
tolerated a declared name on every cell. The 15 tests of the start script's restore guard
(``tests/test_start_chrome_guard_behaviour.py``) skip on ubuntu and RUN on windows-latest, the only
cell that can run them. Declared by name alone, a windows cell that skipped them, or never collected
them, PASSED: a tolerance cannot see a lost source, and nothing would have run the guard anywhere.
The orchestrator ruled on lane ci-checks28's question (c) on 2026-11-28:

- the windows cell must RUN all 15, and a skip there is a failure;
- each ubuntu cell must skip them by name.

``scripts/ci_shard_totals.py`` does this as failure mode 7, from the file's ``by_cell`` rules.

SHOWN FAILING FIRST, with the control the ruling asked for: a windows cell that skips one of them.
``test_without_the_rule_a_windows_skip_passes_unnoticed`` keeps the blindness on the record. It is
the same reports, judged by name alone, and nothing is found.
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import ci_shard_totals as totals  # noqa: E402

CELLS = [
    {"os": "ubuntu-latest", "python-version": "3.10"},
    {"os": "ubuntu-latest", "python-version": "3.13"},
    {"os": "windows-latest", "python-version": "3.13"},
]
LABELS = [totals.cell_label(cell) for cell in CELLS]
A, B = "tests.test_x::test_a_guard_case", "tests.test_x::test_b_guard_case"
WHY = ("synthetic: two guard cases that cannot run on ubuntu and must run on windows, declared by name and "
       "held to each cell by this rule")
DECLARED = {A: WHY, B: WHY}
RULE = {"why": WHY, "skipped_on_os": ["ubuntu-latest"], "executed_on_os": ["windows-latest"], "tests": [A, B]}
OTHERS = 8


def cell_report(label: str, outcomes: dict[str, str], index: int = 0, of: int = 1) -> dict:
    """One shard of one cell, its counts derived from its ruled outcomes plus OTHERS passing tests."""
    skipped = sorted(name for name, outcome in outcomes.items() if outcome == "skipped")
    ran = OTHERS + len(outcomes)
    return {"cell": label, "index": index, "of": of, "collected_total": ran, "shard_expected": ran,
            "ran": ran, "skipped": len(skipped), "skipped_tests": skipped, "xfailed": 0, "failures": 0,
            "errors": 0, "ruled_outcomes": dict(outcomes)}


def reports(windows: dict | None = None, ubuntu: dict | None = None) -> list[dict]:
    """Every cell, one shard each. As ruled, ubuntu skips A and B by name and windows runs both;
    ``windows`` and ``ubuntu`` override an outcome, and None takes the test out of the cell."""
    out = []
    for label in LABELS:
        on_windows = totals.os_of(label) == "windows-latest"
        outcomes = {A: "passed", B: "passed"} if on_windows else {A: "skipped", B: "skipped"}
        for name, outcome in ((windows if on_windows else ubuntu) or {}).items():
            if outcome is None:
                outcomes.pop(name, None)
            else:
                outcomes[name] = outcome
        out.append(cell_report(label, outcomes))
    return out


def judged(rows: list[dict], rules=None, labels=LABELS, of: int = 1) -> list[str]:
    """The totals check over ``rows``. A raise is itself a finding -- the totals job would die
    without naming the problem -- so it fails here BY NAME, never as an error inside the test."""
    try:
        return totals.problems_in(rows, labels, of, DECLARED, [RULE] if rules is None else rules)
    except Exception as exc:  # noqa: BLE001 - the type is the finding
        pytest.fail("the totals check raised " + type(exc).__name__ + " instead of naming a problem")


# ---------------------------------------------------------------------------------------------
# The control, and the blindness the rule closes
# ---------------------------------------------------------------------------------------------


def test_the_control_each_cell_held_to_its_half_passes() -> None:
    """THE CONTROL FOR THE CONTROLS: every cell did what the rule says, and nothing is found."""
    assert judged(reports()) == []


def test_without_the_rule_a_windows_skip_passes_unnoticed() -> None:
    """THE BLINDNESS, KEPT ON THE RECORD. The same reports as the next test, judged by name alone:
    the windows cell skipped A, A is declared, the arithmetic closes, and nothing is found."""
    assert totals.problems_in(reports(windows={A: "skipped"}), LABELS, 1, DECLARED) == []
    assert totals.problems_in(reports(windows={B: None}), LABELS, 1, DECLARED) == []
    assert totals.problems_in(reports(ubuntu={A: "passed"}), LABELS, 1, DECLARED) == []


# ---------------------------------------------------------------------------------------------
# Each way a cell can break its half
# ---------------------------------------------------------------------------------------------


def test_a_windows_skip_of_a_test_that_must_run_there_fails() -> None:
    """THE RULING'S CONTROL: the windows cell skips one of them."""
    problems = judged(reports(windows={A: "skipped"}))
    assert len(problems) == 1, problems
    assert "windows-latest py3.13" in problems[0] and A in problems[0], problems
    assert "must RUN on windows-latest" in problems[0] and "reported it skipped" in problems[0], problems


def test_a_test_the_windows_cell_never_collected_fails() -> None:
    """A test that vanished from the cell's collection: its shard's numbers close without it."""
    problems = judged(reports(windows={B: None}))
    assert len(problems) == 1 and B in problems[0], problems
    assert "never collected or reported it" in problems[0], problems


def test_an_ubuntu_cell_that_ran_a_test_it_must_skip_fails_on_each_ubuntu_cell() -> None:
    """The other half: a cell declared to SKIP a test by name must skip it. Both ubuntu cells ran A."""
    problems = judged(reports(ubuntu={A: "passed"}))
    assert len(problems) == 2, problems
    assert all(A in p and "declared to SKIP on ubuntu-latest" in p and "reported it passed" in p
               for p in problems), problems
    assert {label for label in LABELS if any(label in p for p in problems)} == set(LABELS[:2])


def test_an_ubuntu_cell_that_never_collected_a_test_it_must_skip_fails() -> None:
    problems = judged(reports(ubuntu={B: None}))
    assert len(problems) == 2 and all(B in p and "never collected" in p for p in problems), problems


@pytest.mark.parametrize("outcome, ran", [
    ("passed", True), ("failed", True), ("xfailed", True), ("error", False), ("skipped", False),
], ids=["passed", "failed", "xfailed", "error", "skipped"])
def test_a_run_is_a_passed_failed_or_xfailed_test_never_an_error(outcome, ran) -> None:
    """A failure RAN (its shard is red for it, by its own count). An error never ran its body."""
    problems = judged(reports(windows={A: outcome}))
    assert (problems == []) is ran, problems


def test_a_cell_the_rule_does_not_name_is_unconstrained_and_fails() -> None:
    """A cell added to the matrix cannot arrive unconstrained."""
    labels = LABELS + ["macos-latest py3.13"]
    rows = reports() + [cell_report("macos-latest py3.13", {A: "passed", B: "passed"})]
    problems = judged(rows, labels=labels)
    assert len(problems) == 1 and "says nothing about macos-latest" in problems[0], problems


def test_a_report_without_ruled_outcomes_cannot_be_checked() -> None:
    rows = reports()
    rows[2].pop("ruled_outcomes")
    problems = judged(rows)
    assert any("carries no ruled outcomes" in p for p in problems), problems
    assert any("never collected or reported it" in p for p in problems), problems


def test_a_run_in_which_no_cell_reported_the_rules_tests_holds_nobody_to_it() -> None:
    """Another suite's run, such as the synthetic ones this repository's tests feed ``verify``: the
    rule does not apply, and ``verify`` names it as not checked (below). Tests that vanish from
    EVERY cell are this file's to catch, by collecting them on every cell."""
    rows = reports(windows={A: None, B: None}, ubuntu={A: None, B: None})
    assert judged(rows) == []


def test_the_guard_modules_15_tests_are_collected_on_this_cell() -> None:
    """THE OTHER HALF OF THE LOST SOURCE. The rule holds a run only when some cell reports its
    tests, so tests that vanish from every cell at once -- a conftest that ignores the module, a
    rename -- would leave every cell unchecked. This runs on every cell, ubuntu and windows alike,
    and collects the module there: all 15 must be collected on each, whether they then run or
    skip."""
    done = _run("-m", "pytest", "--collect-only", "-q", "-p", "no:randomly", GUARD)
    ids = sorted(line.strip().replace("tests/test_start_chrome_guard_behaviour.py::",
                                      "tests.test_start_chrome_guard_behaviour::")
                 for line in done.stdout.splitlines() if "::" in line)
    assert ids == guard_ids() and len(ids) == 15, done.stdout + done.stderr


def test_a_test_reported_by_two_shards_of_one_cell_fails() -> None:
    rows = [r for r in reports() if r["cell"] != LABELS[2]]
    rows += [cell_report(LABELS[2], {A: "passed", B: "passed"}, 0, 2),
             cell_report(LABELS[2], {A: "passed"}, 1, 2)]
    problems = judged(rows, of=2)
    assert any(A in p and "reported by 2 shards" in p for p in problems), problems


# ---------------------------------------------------------------------------------------------
# The outcomes ``record`` reads from a junit report
# ---------------------------------------------------------------------------------------------

JUNIT = """<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite name="pytest" errors="1" failures="1" skipped="2" tests="6">
<testcase classname="tests.test_x" name="test_a_guard_case" time="0.1"/>
<testcase classname="tests.test_x" name="test_b_guard_case" time="0.0"><skipped type="pytest.skip" message="no">s</skipped></testcase>
<testcase classname="tests.test_x" name="test_c_guard_case" time="0.0"><skipped type="pytest.xfail" message="x">x</skipped></testcase>
<testcase classname="tests.test_x" name="test_d_guard_case" time="0.0"><failure message="f">f</failure></testcase>
<testcase classname="tests.test_x" name="test_e_guard_case" time="0.0"><error message="e">e</error></testcase>
<testcase classname="tests.test_y" name="test_unruled" time="0.0"><failure message="f">f</failure></testcase>
</testsuite></testsuites>
"""


def test_record_reads_each_ruled_tests_outcome_and_nothing_else(tmp_path) -> None:
    junit = tmp_path / "junit.xml"
    junit.write_text(JUNIT, encoding="utf-8")
    ruled = {"tests.test_x::test_" + k + "_guard_case" for k in "abcde"}
    assert totals.junit_outcomes(str(junit), ruled) == {
        "tests.test_x::test_a_guard_case": "passed", "tests.test_x::test_b_guard_case": "skipped",
        "tests.test_x::test_c_guard_case": "xfailed", "tests.test_x::test_d_guard_case": "failed",
        "tests.test_x::test_e_guard_case": "error",
    }


# ---------------------------------------------------------------------------------------------
# The real declaration, and the two halves of the real script end to end
# ---------------------------------------------------------------------------------------------

GUARD = REPO / "tests" / "test_start_chrome_guard_behaviour.py"


def guard_ids() -> list[str]:
    tree = ast.parse(GUARD.read_text(encoding="utf-8"))
    return sorted("tests.test_start_chrome_guard_behaviour::" + node.name for node in tree.body
                  if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"))


def workflow_systems() -> set[str]:
    text = (REPO / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    return set(re.findall(r'"os":\s*"([a-z0-9.-]+)"', text))


def test_the_guards_rule_names_exactly_its_15_tests_and_each_is_declared() -> None:
    rules = totals.cell_rules()
    guard = [rule for rule in rules if any(n.startswith("tests.test_start_chrome_guard_behaviour::")
                                           for n in rule["tests"])]
    assert len(guard) == 1, rules
    assert sorted(guard[0]["tests"]) == guard_ids() and len(guard_ids()) == 15
    assert guard[0]["skipped_on_os"] == ["ubuntu-latest"] and guard[0]["executed_on_os"] == ["windows-latest"]


def test_every_rule_narrows_a_declared_skip_and_covers_every_system_the_workflow_runs() -> None:
    declared, systems = totals.expected_skips(), workflow_systems()
    assert systems == {"ubuntu-latest", "windows-latest"}, systems
    for rule in totals.cell_rules():
        assert len(rule["why"]) > 80, rule["why"]
        assert set(rule["tests"]) <= set(declared), sorted(set(rule["tests"]) - set(declared))
        skip_on, run_on = set(rule["skipped_on_os"]), set(rule["executed_on_os"])
        assert not skip_on & run_on and skip_on | run_on == systems, rule


def _run(*argv) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *[str(a) for a in argv]], capture_output=True, text=True, cwd=REPO)


def test_record_writes_the_real_rules_outcomes_into_the_report(tmp_path) -> None:
    first, second = guard_ids()[:2]
    junit = tmp_path / "junit.xml"
    cls, n1 = first.split("::")
    junit.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<testsuites><testsuite name="pytest" errors="0" failures="0" '
        'skipped="1" tests="2">\n<testcase classname="' + cls + '" name="' + n1 + '" time="0.1"/>\n'
        '<testcase classname="' + cls + '" name="' + second.split("::")[1] + '" time="0.0"><skipped '
        'type="pytest.skip" message="s">s</skipped></testcase>\n</testsuite></testsuites>\n', encoding="utf-8")
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"index": 0, "of": 1, "files": [], "tests": 2, "collected_total": 2,
                                "files_total": 1}), encoding="utf-8")
    out = tmp_path / "report.json"
    done = _run(REPO / "scripts" / "ci_shard_totals.py", "record", "--plan", plan, "--junit", junit,
                "--cell", json.dumps(CELLS[2]), "--out", out)
    assert done.returncode == 0, done.stderr
    assert json.loads(out.read_text(encoding="utf-8"))["ruled_outcomes"] == {first: "passed", second: "skipped"}


def write_reports(directory: Path, windows_skip: str | None = None, cells=CELLS) -> None:
    """The real rule's 15 tests on every cell, 5 other tests each, as the ruling says."""
    ids = guard_ids()
    for cell in cells:
        label = totals.cell_label(cell)
        on_windows = cell["os"] == "windows-latest"
        outcomes = {name: ("passed" if on_windows else "skipped") for name in ids}
        if on_windows and windows_skip:
            outcomes[windows_skip] = "skipped"
        report = cell_report(label, outcomes)
        report.update(collected_total=len(ids) + 5, shard_expected=len(ids) + 5, ran=len(ids) + 5)
        (directory / (cell["os"] + "-" + cell["python-version"] + "-0.json")).write_text(
            json.dumps(report), encoding="utf-8")


def test_verify_end_to_end_fails_a_windows_skip_of_one_guard_test(tmp_path) -> None:
    ids = guard_ids()
    write_reports(tmp_path)
    good = _run(REPO / "scripts" / "ci_shard_totals.py", "verify", "--reports", tmp_path, "--of", "1",
                "--cells", json.dumps(CELLS))
    assert good.returncode == 0, good.stdout + good.stderr
    assert "1 by-cell rule(s)" in good.stdout and "NOT CHECKED" not in good.stdout
    write_reports(tmp_path, windows_skip=ids[3])
    bad = _run(REPO / "scripts" / "ci_shard_totals.py", "verify", "--reports", tmp_path, "--of", "1",
               "--cells", json.dumps(CELLS))
    assert bad.returncode == 1, bad.stdout + bad.stderr
    assert ids[3] in bad.stderr and "must RUN on windows-latest" in bad.stderr, bad.stderr


def test_verify_names_a_rule_no_cell_reported_as_not_checked(tmp_path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    for index in (0, 1):
        shard = dict(cell_report(LABELS[1], {}, index, 2), collected_total=2 * OTHERS)
        (reports_dir / ("ubuntu-" + str(index) + ".json")).write_text(json.dumps(shard), encoding="utf-8")
    done = _run(REPO / "scripts" / "ci_shard_totals.py", "verify", "--reports", reports_dir, "--of", "2",
                "--cells", json.dumps([CELLS[1]]))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "NOT CHECKED in this run: a by-cell rule over 15 test(s) -- no cell reported any of them" in done.stdout


def test_the_lane_fast_path_says_by_name_which_half_it_cannot_check(tmp_path) -> None:
    """The lane run has one ubuntu cell, so the rule's windows half is the full matrix's to check."""
    write_reports(tmp_path, cells=[CELLS[1]])
    done = _run(REPO / "scripts" / "ci_shard_totals.py", "verify", "--reports", tmp_path, "--of", "1",
                "--cells", json.dumps([CELLS[1]]))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "NOT CHECKED in this run: the rule that 15 test(s) run on windows-latest" in done.stdout, done.stdout
