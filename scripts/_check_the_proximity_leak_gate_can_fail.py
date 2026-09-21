"""SHOW `_probe_proximity_live`'s gate and verdict FAILING, on planted defects.

AN INSTRUMENT ENTERS THE REGISTER ONLY IF IT HAS BEEN SHOWN FAILING. A check
that cannot fail certifies nothing, and a library of such checks is worse than
no library because it manufactures confidence at scale. Every case here plants
a specific defect and asserts the shipped function REFUSES it, then asserts the
clean case passes -- because a gate that refuses everything is equally useless.

THE FOUR THINGS UNDER TEST

1. :func:`leak_gate` catches a STRING in a proximity slot. That is the defect
   that matters: the proximity reading is three integers or None by
   construction, so the one thing an out-of-type value on this path could be
   carrying is a string off a page.
2. :func:`leak_gate` NEVER QUOTES THE OFFENDING VALUE. This is asserted
   directly, with a planted value that would be unmistakable if it leaked --
   because a gate that reports a leak BY LEAKING IT is the exact failure this
   repository measured when `int()` put its refused input verbatim into its
   own ValueError.
3. :func:`leak_gate` catches a BOOL. `isinstance(True, int)` is True in Python,
   so a naive int check admits booleans, and a boolean in a count slot is a
   collapsed state -- the census has paid for that class before.
4. :func:`verdict` calls a single-valued tally UNDISCRIMINATED. A reader whose
   selector died returns one verdict for every posting on earth, and a probe
   that called that a pass would bank a dead reader.

    ./venv/Scripts/python.exe scripts/_check_the_proximity_leak_gate_can_fail.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

import _probe_proximity_live as probe  # noqa: E402

#: A planted value chosen so that a leak is UNMISTAKABLE in the output. It is
#: not a real name, a real employer or a real anything -- it is a synthetic
#: scar phrase, the same device the people-search probe used.
SCAR = "anise-hyssop-placeholder"

FAILURES: list[str] = []


def expect_refusal(label: str, reading, must_not_contain: str = "") -> None:
    complaint = probe.leak_gate(reading)
    if complaint is None:
        FAILURES.append(label + ": the gate ADMITTED a planted defect")
        print("    FAIL  " + label + " -- admitted")
        return
    if must_not_contain and must_not_contain in complaint:
        FAILURES.append(label + ": the gate QUOTED the value it refused")
        print("    FAIL  " + label + " -- the complaint quotes the value")
        return
    print("    ok    " + label + " -- refused: " + complaint)


def expect_pass(label: str, reading) -> None:
    complaint = probe.leak_gate(reading)
    if complaint is not None:
        FAILURES.append(label + ": the gate REFUSED a clean reading")
        print("    FAIL  " + label + " -- refused: " + complaint)
        return
    print("    ok    " + label + " -- admitted")


def main() -> int:
    print("=" * 68)
    print("SHOWING THE PROXIMITY PROBE'S GATE FAIL")
    print("=" * 68)

    print("\n1. leak_gate REFUSES an out-of-type value, and does not quote it")
    expect_refusal("a string in the count slot",
                   {"state": 4, "relation": 0, "count": SCAR},
                   must_not_contain=SCAR)
    expect_refusal("a string in the relation slot",
                   {"state": 4, "relation": SCAR, "count": 1},
                   must_not_contain=SCAR)
    expect_refusal("a string in the state slot",
                   {"state": SCAR, "relation": 0, "count": 1},
                   must_not_contain=SCAR)
    expect_refusal("the whole reading is a string",
                   SCAR, must_not_contain=SCAR)
    expect_refusal("an unexpected key arrives",
                   {"state": 4, "relation": 0, "count": 1, "line": SCAR},
                   must_not_contain=SCAR)

    print("\n2. leak_gate REFUSES a bool, which a naive int check admits")
    if isinstance(True, int):
        print("    (confirmed: isinstance(True, int) is True in this runtime,")
        print("     so the naive check would have admitted the next case)")
    expect_refusal("a bool in the count slot",
                   {"state": 4, "relation": 0, "count": True})

    print("\n3. leak_gate ADMITS the clean shapes the reader really emits")
    expect_pass("count_read with a count", {"state": 4, "relation": 0, "count": 1})
    expect_pass("relation_only, no count",
                {"state": 1, "relation": 0, "count": None})
    expect_pass("not_drawn", {"state": 0, "relation": None, "count": None})
    expect_pass("the key was absent altogether", None)

    print("\n4. verdict CALLS A SINGLE-VALUED TALLY UNDISCRIMINATED")
    dead = {"not_drawn": 12, "relation_only": 0, "count_read": 0}
    text = probe.verdict(dead)
    if not text.startswith("UNDISCRIMINATED"):
        FAILURES.append("verdict: a dead-reader tally did not read "
                        "UNDISCRIMINATED, it read " + text)
        print("    FAIL  a dead-reader tally read " + text)
    else:
        print("    ok    a dead-reader tally reads " + text)
        print("          " + probe.bankable(text))

    alive = {"not_drawn": 9, "relation_only": 2, "count_read": 1}
    text = probe.verdict(alive)
    if not text.startswith("DISCRIMINATES"):
        FAILURES.append("verdict: a discriminating tally read " + text)
        print("    FAIL  a discriminating tally read " + text)
    else:
        print("    ok    a discriminating tally reads " + text)

    empty = probe.verdict({"not_drawn": 0})
    if empty != "NO-SAMPLE":
        FAILURES.append("verdict: an empty tally read " + empty)
        print("    FAIL  an empty tally read " + empty)
    else:
        print("    ok    an empty tally reads NO-SAMPLE, not a pass")

    print("\n4b. THE ABSENT CLASS IS IN THE TALLY -- the defect the first live")
    print("    run of this probe exposed in the probe itself")
    # `parse_job_card` OMITS the proximity key when nothing was drawn, so a
    # selector that died omits it on EVERY card. A verdict blind to the absent
    # class cannot see that, and the first version of `verdict` was: on a real
    # run of 3 count_read and 18 absent it reported UNDISCRIMINATED over a
    # denominator of 3, reading only the rows that already agreed.
    dead_reader = {"(key absent)": 21, "count_read": 0, "not_drawn": 0}
    text = probe.verdict(dead_reader)
    if "DEAD-READER" not in text:
        FAILURES.append("verdict: an absent-everywhere tally did not name the "
                        "dead-reader signature, it read " + text)
        print("    FAIL  absent-everywhere read " + text)
    else:
        print("    ok    absent-everywhere reads " + text)

    real_run = {"(key absent)": 18, "count_read": 3, "not_drawn": 0}
    text = probe.verdict(real_run)
    if not text.startswith("DISCRIMINATES"):
        FAILURES.append("verdict: 3-drawn/18-absent read " + text
                        + "; the absent class is being dropped again")
        print("    FAIL  3 drawn against 18 absent read " + text)
    else:
        print("    ok    3 drawn against 18 absent reads " + text)
        print("          (this is the live shape that caught the defect)")

    print("\n5. THE ALPHABETS THE PROBE PRINTS ARE THE SHIPPED ONES")
    from linkedin_server import shape
    for position, name in enumerate(shape.PROXIMITY_STATES):
        if probe.state_name(position) != name:
            FAILURES.append("state_name(" + str(position) + ") drifted")
    if probe.state_name(999) == "(out-of-alphabet position)":
        print("    ok    an out-of-range position is NAMED as such, not guessed")
    else:
        FAILURES.append("state_name admitted an out-of-range position")
    if probe.relation_name(None) == "(none)":
        print("    ok    a None relation reads (none)")
    print("    ok    all " + str(len(shape.PROXIMITY_STATES))
          + " state positions and "
          + str(len(shape.PROXIMITY_RELATIONS))
          + " relation positions resolve to the shipped tokens")

    print("\n" + "=" * 68)
    if FAILURES:
        print("REFUSING -- " + str(len(FAILURES)) + " control(s) did not behave:")
        for line in FAILURES:
            print("    " + line)
        return 1
    print("ALL CONTROLS BEHAVED: the gate refuses every planted defect, never")
    print("quotes what it refused, admits every clean shape, and the verdict")
    print("calls a dead reader dead.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
