"""Which browser the live runner may attach to, and which one its teardown may close.

WHY THIS FILE EXISTS. Session 14b's runner and its Chrome teardown live in gitignored state, and
their red-first checks (``tabs_checks_s14b.py``, ``teardown_checks_s14b.py``) ran only on the
operator's machine. The DECISIONS those checks test are pure, and lane ci-checks28 tracked them in
``scripts/live_runner_rules.py``, whose docstring says which parts are verbatim and which are
re-cut. These tests are the live checks' own cases, ported case for case under the same names
(T1-T9, N2-N6, G1-G8), on synthetic readings. No port, process or browser is touched.

WHAT STAYS LOCAL, named so that nobody mistakes this file for it:

- the port's HTTP reads (``/json/list``, ``/json/version``);
- the OS's process and listener reads;
- the files the runner writes;
- the meter's wiring of the gate into load 1 (that a refusal reaches neither the navigation nor a
  ledger);
- every real graceful close and kill, timed on real processes.

The lane's record (``_audit/2026-11-28-live-runner-checks-on-ci.md``) names each of these with the
check that still covers it.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import live_runner_rules as rules  # noqa: E402

#: A fake DevTools port, as the live tabs checks used: never the live lane's port.
PORT = 9338
PID, OTHER = 4242, 4343
#: The dedicated profile, synthetic. A drive path whose first segment names a place.
PROFILE = r"C:\workspace\dedicated-profile"
#: An address the runner did not open, on LinkedIn. Its slug is a synthetic token.
SECRET = "https://www.linkedin.com/in/someone-example/edit/"
LAUNCH_1 = "ws://127.0.0.1:" + str(PORT) + "/devtools/browser/SYNTHETIC-LAUNCH-1"
LAUNCH_2 = "ws://127.0.0.1:" + str(PORT) + "/devtools/browser/SYNTHETIC-LAUNCH-2"


def cmd(port: int = PORT, profile: str = PROFILE, *, quoted: bool = True) -> str:
    """A browser command line as Windows reports it."""
    user = ('--user-data-dir="' + profile + '"') if quoted else ("--user-data-dir=" + profile)
    return '"chrome.exe" --remote-debugging-port=' + str(port) + " " + user + " about:blank"


def page(url: str) -> dict:
    return {"type": "page", "url": url, "title": "synthetic", "id": "SYNTHETIC"}


def reading(targets: list, *, browser: str | None = "a" * 16, dedicated: bool = True,
            listeners: int = 1) -> dict:
    return rules.tabs_reading(targets, browser, dedicated, listeners, "12:00:00")


# ---------------------------------------------------------------------------------------------
# The teardown's judge: the PID, then the port's listeners (teardown_checks_s14b.py T3-T9)
# ---------------------------------------------------------------------------------------------


def preclose(read, owners, profile: str = PROFILE) -> tuple:
    """The precheck, where a raise is itself the defect round 5's NIT-6 names: a report, never a
    traceback. So it fails here BY NAME, never as an error from inside the test."""
    try:
        return rules.teardown_preclose(PID, PORT, profile, read, owners)
    except Exception as exc:  # noqa: BLE001 - the type is the finding
        pytest.fail("the teardown's precheck raised " + type(exc).__name__ + " instead of a report")


def refused(code, out: dict, path: str) -> None:
    """Exit 2 FIRST: a defect that lets the close go ahead fails on that, not on a missing key."""
    assert code == 2, "the close would go ahead: " + repr(out)
    assert out.get("path") == path, out


def test_the_dedicated_browser_named_rightly_may_be_closed() -> None:
    """The control (T1's and T4b's precondition): chrome.exe, this port, exactly this profile, and
    the port's one listener is the PID. The close may go ahead."""
    code, out = preclose(("chrome.exe", cmd()), {PID})
    assert code is None, out
    assert out.get("judged") == "the dedicated browser"
    assert out.get("port_listeners") == 1 and out.get("port_owner_is_the_pid") is True, out
    assert "path" not in out, "the path is the close's to write, not the precheck's"


def test_t3_a_pid_that_is_not_chrome_is_refused() -> None:
    code, out = preclose(("python.exe", cmd()), {PID})
    refused(code, out, "refused")
    assert out.get("judged") == "not chrome.exe"


def test_t4_chrome_on_the_right_port_with_another_profile_is_refused() -> None:
    code, out = preclose(("chrome.exe", cmd(profile=r"C:\workspace\everyday-profile")), {PID})
    refused(code, out, "refused")
    assert out.get("judged") == "not this profile"


def test_t6_a_profile_whose_path_only_starts_with_this_one_is_refused() -> None:
    """Round 4's NIT-4b: the WHOLE --user-data-dir value, never a substring."""
    code, out = preclose(("chrome.exe", cmd(profile=PROFILE + "x")), {PID})
    refused(code, out, "refused")
    assert out.get("judged") == "not this profile"


def test_a_port_that_only_starts_with_this_one_is_not_this_port() -> None:
    """The same rule for the port: ``--remote-debugging-port=93380`` is not port 9338."""
    code, out = preclose(("chrome.exe", cmd(port=PORT * 10)), {PID})
    refused(code, out, "refused")
    assert out.get("judged") == "not this debugging port"


def test_t5_another_browser_on_the_port_closes_nothing() -> None:
    """Round 4's NIT-4a: Browser.close goes to the PORT, so its one listener must BE the judged PID."""
    code, out = preclose(("chrome.exe", cmd()), {OTHER})
    refused(code, out, "refused_port_held_by_another")
    assert out.get("port_listeners") == 1 and out.get("port_owner_is_the_pid") is False, out


def test_t7_two_listeners_close_nothing_even_for_the_ports_own_browser() -> None:
    """Measured 2026-11-28: a second Chromium whose 127.0.0.1 bind failed listened on ::1 with the
    same port number. An ambiguous port closes nothing."""
    code, out = preclose(("chrome.exe", cmd()), {PID, OTHER})
    refused(code, out, "refused_port_held_by_another")
    assert out.get("port_listeners") == 2, out


def test_t8_no_listener_at_all_closes_nothing_and_kills_nothing() -> None:
    """The orchestrator's 14b rulings, NIT-4: no listener is a report, never the kill fallback."""
    code, out = preclose(("chrome.exe", cmd()), set())
    refused(code, out, "refused_no_listener_on_the_port")
    assert out.get("port_listeners") == 0, out


def test_t9_a_listener_read_that_failed_is_a_report_never_a_traceback() -> None:
    """Round 5's NIT-6: the teardown's listener read timed out, and the precheck refuses by name."""
    code, out = preclose(("chrome.exe", cmd()), None)
    refused(code, out, "refused_listener_read_failed")
    assert "port_listeners" not in out


def judge(read, port: int = PORT, profile: str = PROFILE) -> tuple:
    try:
        return rules.judge_command_line(read, port, profile)
    except Exception as exc:  # noqa: BLE001 - the type is the finding
        pytest.fail("the judge raised " + type(exc).__name__ + " on a read instead of naming why")


@pytest.mark.parametrize("read, why", [
    (None, "the process could not be read"),
    (("", ""), "no such process"),
    (("CHROME.EXE", cmd()), "the dedicated browser"),
    (("chrome.exe", cmd().replace("--remote-debugging-port", "--remote-debugging-pipe")), "not this debugging port"),
    (("chrome.exe", '"chrome.exe" --remote-debugging-port=9338 about:blank'), "not this profile"),
], ids=["no-read", "gone", "upper-case-image", "no-port-switch", "no-profile-switch"])
def test_the_judge_names_why_for_each_read(read, why) -> None:
    assert judge(read) == (why == "the dedicated browser", why)


@pytest.mark.parametrize("spelled", [
    PROFILE,
    PROFILE + "\\",
    PROFILE.upper(),
    PROFILE.replace("\\", "/"),
    PROFILE.replace("\\", "/") + "/",
], ids=["as-is", "trailing-separator", "upper-case", "forward-slashes", "forward-slashes-trailing"])
def test_the_profile_matches_whole_through_case_and_separators(spelled) -> None:
    """Normalised and case-folded, as Windows reads a path, on every CI cell alike."""
    assert rules.judge_command_line(("chrome.exe", cmd(profile=spelled)), PORT, PROFILE)[0] is True
    assert rules.judge_command_line(("chrome.exe", cmd(profile=spelled, quoted=False)), PORT, PROFILE)[0] is True


def test_the_user_data_dir_is_read_whole_quoted_or_bare() -> None:
    assert rules.user_data_dir_of('x --user-data-dir="C:\\workspace\\a b" --y') == "C:\\workspace\\a b"
    assert rules.user_data_dir_of("x --user-data-dir=C:\\workspace\\ab --y") == "C:\\workspace\\ab"
    assert rules.user_data_dir_of("x --no-profile --y") == ""


# ---------------------------------------------------------------------------------------------
# The tabs check at the first attach (tabs_checks_s14b.py T1-T6)
# ---------------------------------------------------------------------------------------------


def test_t1_one_blank_tab_at_the_first_attach_passes() -> None:
    got = reading([page("about:blank"), {"type": "service_worker", "url": "chrome://x"}])
    assert (got["pages"], got["on_linkedin"], got["blank_or_new_tab"]) == (1, 0, 1)
    assert rules.tabs_stop(got, PORT) is None


def test_t2_two_tabs_are_a_stop_before_load_1() -> None:
    got = reading([page("about:blank"), page("chrome://newtab/")])
    assert rules.tabs_stop(got, PORT) == "STOP before load 1: not exactly one tab open"


def test_t3_a_linkedin_tab_the_runner_did_not_open_is_a_stop() -> None:
    got = reading([page(SECRET)])
    assert got["on_linkedin"] == 1
    assert rules.tabs_stop(got, PORT) == "STOP before load 1: a LinkedIn tab the runner did not open"


def test_two_tabs_one_on_linkedin_name_both_reasons() -> None:
    got = reading([page("about:blank"), page(SECRET)])
    assert rules.tabs_stop(got, PORT) == (
        "STOP before load 1: not exactly one tab open and a LinkedIn tab the runner did not open")


def test_t4_a_port_that_does_not_answer_is_a_stop_never_no_tabs() -> None:
    """The kept reading says it did not answer, and carries no stale counts."""
    got = rules.unanswered_reading("12:00:00")
    assert got == {"answered": False, "at": "12:00:00"}
    said = rules.tabs_stop(got, PORT, error="URLError")
    assert said == "STOP before load 1: the DevTools port 9338 did not answer (URLError)"


def test_t5_nothing_kept_or_said_names_an_address_or_a_browser_endpoint() -> None:
    """COUNTS only: the browser is a digest, and no target's address survives into the reading."""
    launch = rules.browser_digest({"Browser": "Synthetic/1", "webSocketDebuggerUrl": LAUNCH_1})
    readings = [reading([page(SECRET)], browser=launch), reading([page("about:blank")], browser=launch),
                reading([page("about:blank"), page(SECRET)], browser=launch), rules.unanswered_reading("12:00:00")]
    for got in readings:
        text = json.dumps(got) + str(rules.tabs_stop(got, PORT))
        assert SECRET not in text and "someone-example" not in text, text
        assert "devtools/browser" not in text and "ws://" not in text, text
    assert re.fullmatch(r"[0-9a-f]{16}", launch)


def test_t6_a_port_that_names_no_browser_endpoint_is_a_stop() -> None:
    """r3c: checked FIRST -- before the listener and before the tab counts."""
    got = reading([page("about:blank"), page(SECRET)], browser=None, dedicated=False)
    assert rules.tabs_stop(got, PORT) == "STOP before load 1: the DevTools port 9338 names no browser endpoint"


def test_one_launch_is_one_digest_and_another_launch_is_another() -> None:
    v1 = {"webSocketDebuggerUrl": LAUNCH_1}
    assert rules.browser_digest(v1) == rules.browser_digest(dict(v1))
    assert rules.browser_digest(v1) != rules.browser_digest({"webSocketDebuggerUrl": LAUNCH_2})
    for none in (None, {}, {"webSocketDebuggerUrl": ""}, ["not", "a", "dict"], "text"):
        assert rules.browser_digest(none) is None, none


# ---------------------------------------------------------------------------------------------
# The listener is the dedicated profile's browser (tabs_checks_s14b.py N2-N6, round 5's NIT-7)
# ---------------------------------------------------------------------------------------------

OS_DEFAULT = {"owners": {PID}, "name": "chrome.exe", "profile": PROFILE}

N_CASES = [
    ("N2", "chrome.exe on this port with ANOTHER profile", {"profile": r"C:\workspace\everyday-profile"},
     (False, "not this profile", 1)),
    ("N3", "two listening processes on the port", {"owners": {PID, OTHER}},
     (False, "2 listening processes on the port", 2)),
    ("N4", "a listener that is not chrome.exe", {"name": "python.exe"}, (False, "not chrome.exe", 1)),
    ("N5", "a listener read that fails", {"owners": None}, (False, "the listener read failed", -1)),
    ("N6", "a profile whose path only STARTS with the dedicated one", {"profile": PROFILE + "-other"},
     (False, "not this profile", 1)),
]


def listener(**changed) -> tuple[bool, str, int]:
    osa = dict(OS_DEFAULT, **changed)

    def read_of(pid: int):
        assert pid in (osa["owners"] or ()), "the judge read a PID that is not the port's listener"
        return osa["name"], cmd(profile=osa["profile"])

    return rules.dedicated_listener(osa["owners"], read_of, PORT, PROFILE)


def test_the_dedicated_browser_alone_on_the_port_is_the_dedicated_listener() -> None:
    assert listener() == (True, "the dedicated browser", 1)


@pytest.mark.parametrize("key, what, change, want", N_CASES, ids=[c[0] for c in N_CASES])
def test_n_a_listener_that_is_not_the_dedicated_browser_stops_before_load_1(key, what, change, want) -> None:
    ok, why, count = listener(**change)
    assert (ok, why, count) == want, what
    got = reading([page("about:blank")], browser="b" * 16, dedicated=ok, listeners=count)
    assert rules.tabs_stop(got, PORT, why) == (
        "STOP before load 1: the DevTools port's listener is not the dedicated profile's browser (" + why + ")")
    assert got["dedicated"] is False
    # and the gate on load 1 refuses the reading, even after the flag and on this launch
    assert rules.tabs_gate(got, 200.0, 100.0, "b" * 16) == "this session's tabs_check did not pass"


# ---------------------------------------------------------------------------------------------
# The gate on load 1 (tabs_checks_s14b.py G1-G8, r3c, the orchestrator's 14b rulings NIT-3)
# ---------------------------------------------------------------------------------------------

NOW = "c" * 16
PASSED = {"answered": True, "pages": 1, "on_linkedin": 0, "blank_or_new_tab": 1, "browser": NOW,
          "dedicated": True, "listeners": 1, "at": "12:00:00"}


def test_g5_control_a_passing_reading_after_the_flag_on_this_launch_lets_load_1_through() -> None:
    assert rules.tabs_gate(dict(PASSED), 200.0, 100.0, NOW) is None
    assert rules.tabs_gate(dict(PASSED), 100.0, 100.0, NOW) is None, "taken in the flag's own second"


def test_g1_with_no_tabs_check_in_the_session_load_1_is_refused() -> None:
    for none in (None, [], "text"):
        assert rules.tabs_gate(none, 200.0, 100.0, NOW) == "no tabs_check in this session (run tabs_check after flag_on)"


@pytest.mark.parametrize("change", [
    {"pages": 2}, {"on_linkedin": 1}, {"answered": False}, {"dedicated": False}, {"dedicated": None},
    {"pages": None}, {"on_linkedin": None},
], ids=["two-pages", "on-linkedin", "unanswered", "not-dedicated", "dedicated-unknown", "pages-unknown",
        "on-linkedin-unknown"])
def test_g2_a_tabs_check_that_did_not_pass_refuses_load_1(change) -> None:
    assert rules.tabs_gate(dict(PASSED, **change), 200.0, 100.0, NOW) == "this session's tabs_check did not pass"


def test_g3_a_passing_tabs_check_older_than_the_flag_refuses_load_1() -> None:
    assert rules.tabs_gate(dict(PASSED), 95.0, 100.0, NOW) == (
        "the tabs_check is older than this session's flag (run it again after flag_on)")


def test_g4_a_passing_tabs_check_taken_on_another_launch_refuses_load_1() -> None:
    assert rules.tabs_gate(dict(PASSED), 200.0, 100.0, "d" * 16) == (
        "the tabs_check was taken on another launch of the browser (run it again)")


def test_g6_a_passing_tabs_check_with_no_flag_standing_refuses_load_1() -> None:
    assert rules.tabs_gate(dict(PASSED), 200.0, None, NOW) == (
        "the tabs_check is older than this session's flag (run it again after flag_on)")


def test_g8_a_passing_tabs_check_with_the_port_down_at_load_1_refuses_it() -> None:
    assert rules.tabs_gate(dict(PASSED), 200.0, 100.0, None) == "the DevTools port names no browser endpoint now"


def test_a_reading_whose_time_cannot_be_read_refuses_load_1() -> None:
    assert rules.tabs_gate(dict(PASSED), None, 100.0, NOW) == "the tabs_check's time cannot be read"


def test_the_gate_accepts_exactly_what_the_tabs_check_passes() -> None:
    """A reading the tabs check passes is one the gate lets through, and every reading it stops is
    one the gate refuses: the two halves of NIT-3 cannot drift apart."""
    cases = [
        ([page("about:blank")], True), ([page("chrome://newtab/")], True),
        ([page("about:blank"), page("chrome://newtab/")], False), ([page(SECRET)], False), ([], False),
    ]
    for targets, passes in cases:
        for dedicated in (True, False):
            got = reading(targets, browser=NOW, dedicated=dedicated)
            stopped = rules.tabs_stop(got, PORT, "synthetic") is not None
            refused = rules.tabs_gate(got, 200.0, 100.0, NOW) is not None
            assert stopped is refused is (not (passes and dedicated)), (targets, dedicated)
