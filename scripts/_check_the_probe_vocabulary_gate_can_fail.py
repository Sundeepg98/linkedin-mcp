"""Show `_gate` in `_probe_people_search_shape_live.py` CAN refuse.

`_probe_people_search_shape_live.py` fires the shipped people-search shaper
(`search_results.read_results` / `search_results.read_filters`) at a live
LinkedIn search page and prints what came back. Its own docstring states the
claim under test: no string from the document may leave the shaper, because
every row of a people search is a third party. `_gate` is the control that
enforces that claim on the live reading -- it walks the payload the probe is
about to print or write, and refuses (raises `ValueError`, naming only the
FIELD PATH, never the value) if any dict key or string value falls outside
`search_results.emitted_alphabet() | search_results.filter_alphabet()` plus
the probe's own `_OWN_KEYS`.

A GUARD THAT HAS NEVER BEEN SHOWN FAILING CERTIFIES NOTHING -- this
repository's instrument register admits a check only once it has been shown
refusing, and this file is that demonstration for `_gate`. It never touches a
browser, a page or the network; it drives the real function over payloads
built entirely by hand, in-process, so it costs nothing and can run on every
checkout.

FIVE CASES, each answering a different way the gate could be lying to us:

  A. A HEALTHY PAYLOAD PASSES. A payload shaped like a real trial record,
     built only from strings the shipped alphabets actually contain, must
     NOT raise. A gate that refuses everything would pass every other case
     below for the wrong reason, so this is checked first and separately.

  B. A FOREIGN STRING IN A VALUE IS CAUGHT, planted a couple of levels deep
     inside a list inside a dict -- not just at the top level. The raised
     message must NAME THE FIELD PATH (contain the nested key the string was
     found under) and must NEVER contain the planted string itself -- that
     asymmetry, name the address but never the contents, is the entire point
     of `_gate`, and this is the control that shows it holds under a real
     violation rather than merely in its own docstring.

  C. A FOREIGN DICT KEY IS CAUGHT, the same way a foreign value is, and
     distinctly from it (the message says KEY, not STRING).

  D. AN UNEXPECTED TYPE IS CAUGHT -- something that is neither a dict, a
     list/tuple, a string, nor a number/bool/None. Tried twice, once with a
     built-in container (`set`) and once with an arbitrary object, because a
     gate shown to catch one exotic type has not thereby shown it catches the
     class of them.

  E. THE GATE IS NOT VACUOUS. It would be trivial for `allowed` to be empty
     or unrelated to the real vocabulary and have every case above still
     pass by accident -- an empty alphabet refuses every string
     unconditionally, which LOOKS like cases B/C/D succeeding for a reason
     that has nothing to do with the vocabulary being right. So this
     asserts the alphabet `_gate` was actually built from is non-empty and
     contains a real, named term, and then -- the sharper check -- that the
     SAME healthy payload from case A RAISES once the allowed set is
     deliberately emptied. If the alphabet were decorative rather than
     load-bearing, that last assertion would fail.

THE PROBE MODULE IS LOADED BY FILE PATH, under a name that is not
`__main__`, specifically so its `if __name__ == "__main__":` block never
executes here -- this check must never open a browser, attach to CDP, or
touch `LINKEDIN_CDP_ATTACH`. Only `_gate`, `_alphabet` and the imported
`search_results` module -- all bound above that guard -- are used.

`--demonstrate-red` IS THE CONTROL'S OWN SHOWN-FAILING PROOF, RE-RUNNABLE
RATHER THAN WRITTEN IN PROSE. A sentence in a docstring saying "if `_gate`
were disarmed, B1-B3/C1-C2/D1-D2/E3 would fail" can go stale silently -- a
case gets renamed, a message format changes, and nothing ever re-checks that
the sentence still matches the code. So instead this flag swaps in
`_DisarmedProbe`, a stand-in whose `_gate` is a bare no-op -- it takes the
same three arguments and returns `None` without inspecting any of them,
never refusing anything -- and delegates every other attribute (`_alphabet`,
the imported `search_results` module) to the real probe, unchanged. It
re-runs the IDENTICAL case battery against that stand-in and INVERTS the
verdict: this run of the script passes only if every case in
`GATE_DEPENDENT_CASES` (the ones whose assertion depends on `_gate` actually
raising) comes back FAILED, and every other case (the ones that assert facts
about the alphabet or about a healthy payload, and never need `_gate` to
refuse anything) still PASSES. Same convention as
`scripts/_check_cells_honours_escaped_pipe.py`: *"a control that describes
the bug in prose cannot fail when the bug comes back."* Here the "bug" this
re-runs on demand is a `_gate` silently disarmed -- by a bad merge, a
well-meaning refactor, anything -- and this flag is what would still catch
it.

Usage::

    ./venv/Scripts/python.exe scripts/_check_the_probe_vocabulary_gate_can_fail.py
    ./venv/Scripts/python.exe scripts/_check_the_probe_vocabulary_gate_can_fail.py --demonstrate-red

Exit (default): 0 if every case behaved as required, 1 if any did not.
Exit (--demonstrate-red): 0 if every gate-dependent case correctly FAILED
against the disarmed stand-in and no other case broke, 1 otherwise.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROBE_PATH = REPO / "scripts" / "_probe_people_search_shape_live.py"

RESULTS: list[tuple[str, bool, str]] = []


def record(label: str, ok: bool, text: str) -> bool:
    RESULTS.append((label, ok, text))
    print("%-6s %-4s %s" % ("PASS" if ok else "FAIL", label, text))
    return ok


def _load_probe_module():
    """Load `_probe_people_search_shape_live.py` BY FILE PATH.

    Named something other than `__main__`, so its own
    `if __name__ == "__main__":` block does not fire on load -- this check
    must never reach `main()`, never touch `LINKEDIN_CDP_ATTACH`, and never
    open a browser. Everything this script needs (`_gate`, `_alphabet`, the
    imported `search_results` module) is bound at the probe's top level,
    above that guard, so a plain `exec_module` is enough.
    """
    spec = importlib.util.spec_from_file_location(
        "_the_probe_vocabulary_gate_under_test", PROBE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not build an import spec for {PROBE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _DisarmedProbe:
    """Stand-in for the probe module with `_gate` REPLACED BY A NO-OP.

    `--demonstrate-red`'s plant, built exactly the way it was first proven by
    hand: everything except `_gate` -- `_alphabet`, the imported
    `search_results` module, anything else the case battery ever touches --
    delegates to the REAL module through `__getattr__`, unchanged. Only
    `_gate` is disarmed, to the exact shape a silently-broken gate would
    take: called with the same three arguments, it inspects nothing and
    never raises.
    """

    def __init__(self, real_module) -> None:
        self._real = real_module

    def _gate(self, payload: object, allowed: frozenset, where: str = "") -> None:
        """The plant: a gate that inspects nothing and never refuses."""
        return None

    def __getattr__(self, name: str):
        return getattr(self._real, name)


#: The case labels whose PASS verdict can only be true if `_gate` actually
#: raises on bad input. Named explicitly rather than inferred or counted --
#: the alternative, "assume every case is gate-dependent" or "assert N of 11
#: failed", is exactly the brittleness `--demonstrate-red` exists to avoid: a
#: case added later that does NOT exercise `_gate` refusing anything (a
#: hypothetical future case checking some other fact about the alphabet, the
#: way E1/E2 already do) must NOT be required to fail here, and a hardcoded
#: count would not know that -- only a named set can say "these, and only
#: these".
#:
#: A, E1 and E2 are the complement, and are asserted to KEEP PASSING under
#: the plant: a disarmed gate does not stop a healthy payload from passing
#: (A), and E1/E2 assert facts about the alphabet `_alphabet()` returns,
#: which `_DisarmedProbe` never touches.
GATE_DEPENDENT_CASES: frozenset[str] = frozenset(
    {"B1", "B2", "B3", "C1", "C2", "D1", "D2", "E3"}
)


def _healthy_reading(sr) -> dict:
    """One `_read_both` reading, shaped like the real one, built only from
    vocabulary the shipped alphabets actually contain -- pulled BY INDEX out
    of `sr.RESULT_KINDS` / `sr.FILTER_TERMS` / `sr.VALUE_CLASSES` rather than
    typed out here, so this stays valid if the vocabulary itself changes.
    """
    person_kind = sr.RESULT_KINDS[0]
    company_kind = sr.RESULT_KINDS[1]
    connections_of = sr.FILTER_TERMS[0]
    keywords_term = sr.FILTER_TERMS[2]
    person_valued = sr.VALUE_CLASSES[0]
    needle_valued = sr.VALUE_CLASSES[1]
    return {
        "results": {
            "by_kind": {person_kind: 3, company_kind: 0},
            "kinds_not_reported": 0,
            "positions_beyond_the_alphabet": 0,
            "total_classified": 3,
            "person_results": 3,
            "traversals_refused": 0,
            "queries_present": 1,
            "anchors_seen": 3,
            "numeric_entity": 2,
            "non_numeric_entity": 1,
            "values_refused": 0,
        },
        "filters": {
            "by_term": {connections_of: 1, keywords_term: 0},
            "by_value_class": {person_valued: 1, needle_valued: 0},
            "terms_not_reported": 0,
            "positions_beyond_the_vocabulary": 0,
            "filters_offered": 1,
            "person_valued_filters": 1,
            "needle_valued_filters": 0,
            "controls_seen": 2,
            "matched_controls": 2,
            "unmatched_controls": 0,
            "empty_labels": 0,
            "values_refused": 0,
        },
    }


def _healthy_trial(sr) -> dict:
    """A payload shaped like `one_load`'s return value.

    `"people_search"` is the literal `one_load` itself passes as `surface`
    (see the probe's own call site) -- not pulled by index, because it is a
    sentinel rather than a positional vocabulary term.
    """
    reading = _healthy_reading(sr)
    return {
        "trial": 1,
        "surface": "people_search",
        "landed_where_it_was_sent": True,
        "reading": [reading, copy.deepcopy(reading)],
    }


def _attempt(gate, payload: object, allowed: frozenset, where: str) -> tuple[bool, str]:
    """Run `_gate`. Return (raised_value_error, message).

    Only `ValueError` is caught. Anything else propagates -- a different
    exception type is not a pass, it is an unexamined failure mode, and
    hiding it behind a broad `except` would be exactly the defect this
    repository's controls exist to refuse.
    """
    try:
        gate(payload, allowed, where)
    except ValueError as exc:
        return True, str(exc)
    return False, ""


# ---------------------------------------------------------------------------
# THE CASE BATTERY. Each function takes `target` -- either the real probe
# module (default run) or a `_DisarmedProbe` stand-in (`--demonstrate-red`)
# -- and asserts on `target._gate`'s behaviour. Nothing below needs to know
# which one it was handed; that is the point of the stand-in sharing the
# real module's interface.
# ---------------------------------------------------------------------------


def case_a(target, allowed: frozenset, healthy: dict) -> None:
    raised, message = _attempt(target._gate, healthy, allowed, "trial1")
    detail = "" if not raised else f" (it raised: {message})"
    record(
        "A",
        not raised,
        "a healthy trial record built only from shipped vocabulary passes "
        "_gate without raising" + detail,
    )


def case_b(target, allowed: frozenset, healthy: dict) -> None:
    planted = "example048177-not-shipped-vocabulary"
    poisoned = copy.deepcopy(healthy)
    # A list inside a dict, a couple of levels below the payload root.
    poisoned["reading"][0]["filters"]["empty_labels"] = [
        {"unmatched_controls": [planted]}
    ]
    raised, message = _attempt(target._gate, poisoned, allowed, "trial1")
    record(
        "B1",
        raised,
        "a foreign string planted a couple of levels deep, inside a list "
        "inside a dict, is caught (_gate raises ValueError)",
    )
    record(
        "B2",
        raised and "unmatched_controls" in message,
        "the raised message names the FIELD PATH -- it contains the nested "
        "key 'unmatched_controls' the string was found under",
    )
    record(
        "B3",
        raised and planted not in message,
        "the raised message does NOT contain the planted string itself",
    )


def case_c(target, allowed: frozenset, healthy: dict) -> None:
    poisoned = copy.deepcopy(healthy)
    poisoned["reading"][0]["results"]["example_unshipped_key"] = 0
    raised, message = _attempt(target._gate, poisoned, allowed, "trial1")
    record(
        "C1",
        raised,
        "a foreign dict KEY outside the alphabet is caught (_gate raises "
        "ValueError)",
    )
    record(
        "C2",
        raised and "KEY" in message,
        "the raised message identifies it as a KEY violation, distinctly "
        "from a STRING (value) violation",
    )


def case_d(target, allowed: frozenset, healthy: dict) -> None:
    class _NotAShippedType:
        """Neither dict, list/tuple, str, nor int/float/bool/None."""

    poisoned_set = copy.deepcopy(healthy)
    poisoned_set["reading"][0]["results"]["numeric_entity"] = {1, 2, 3}
    raised_set, message_set = _attempt(
        target._gate, poisoned_set, allowed, "trial1"
    )
    record(
        "D1",
        raised_set and "UNEXPECTED TYPE" in message_set,
        "an unexpected TYPE (a built-in set) is caught",
    )

    poisoned_obj = copy.deepcopy(healthy)
    poisoned_obj["reading"][0]["results"]["numeric_entity"] = _NotAShippedType()
    raised_obj, message_obj = _attempt(
        target._gate, poisoned_obj, allowed, "trial1"
    )
    record(
        "D2",
        raised_obj and "UNEXPECTED TYPE" in message_obj,
        "an unexpected TYPE (a bare object) is caught",
    )


def case_e(target, allowed: frozenset, healthy: dict) -> None:
    record("E1", len(allowed) > 0, "the alphabet _gate was built from is non-empty")
    record(
        "E2",
        "connections of" in allowed,
        "the alphabet contains a known real term ('connections of')",
    )
    raised, _ = _attempt(target._gate, healthy, frozenset(), "trial1")
    record(
        "E3",
        raised,
        "the SAME healthy payload from case A RAISES against a "
        "deliberately EMPTY allowed set -- the alphabet is load-bearing, "
        "not decorative",
    )


def _verdict_default() -> int:
    """PASS iff every case behaved as required against the REAL gate."""
    failed = [(label, text) for label, ok, text in RESULTS if not ok]
    if failed:
        print(
            f"FAIL: {len(failed)} of {len(RESULTS)} cases did not behave "
            "as required:"
        )
        for label, text in failed:
            print(f"  {label}: {text}")
        return 1
    print(f"PASS: {len(RESULTS)} of {len(RESULTS)} cases behaved as required.")
    return 0


def _verdict_demonstrate_red() -> int:
    """INVERTED verdict for the run against the disarmed stand-in.

    PASS (0) only if EVERY case in `GATE_DEPENDENT_CASES` came back FAILED --
    proof the control notices its own gate being silently replaced with a
    no-op -- AND no case outside that set broke as a side effect, which would
    mean the plant reached further than `_gate`, or that the classification
    in `GATE_DEPENDENT_CASES` is wrong. Nowhere here is a literal count of
    "how many failed" compared against another literal: only the NAMED set
    is asserted, so a case added to the battery later needs one line added
    to `GATE_DEPENDENT_CASES`, never a number updated here.
    """
    seen = {label for label, _ok, _text in RESULTS}
    missing = sorted(GATE_DEPENDENT_CASES - seen)
    if missing:
        print(
            f"FAIL: the case battery never produced {missing} -- this flag "
            "cannot certify anything against case labels it does not "
            "recognise. GATE_DEPENDENT_CASES is stale."
        )
        return 1

    still_passed = [
        (label, text)
        for label, ok, text in RESULTS
        if label in GATE_DEPENDENT_CASES and ok
    ]
    broke_anyway = [
        (label, text)
        for label, ok, text in RESULTS
        if label not in GATE_DEPENDENT_CASES and not ok
    ]

    if still_passed:
        print(
            "FAIL: the control CANNOT detect a disarmed gate -- the "
            "following gate-dependent case(s) still PASSED against a "
            "_gate that is a bare no-op:"
        )
        for label, text in still_passed:
            print(f"  {label}: {text}")
        print(
            "A control that stays green when the thing it certifies is "
            "silently removed certifies nothing."
        )
        return 1

    if broke_anyway:
        print(
            "FAIL: case(s) NOT listed in GATE_DEPENDENT_CASES broke anyway "
            "under the plant -- either that classification is wrong, or "
            "the plant reaches further than _gate:"
        )
        for label, text in broke_anyway:
            print(f"  {label}: {text}")
        return 1

    correctly_failed = sorted(
        label for label, ok, text in RESULTS if label in GATE_DEPENDENT_CASES
    )
    print(
        f"PASS: all {len(correctly_failed)} gate-dependent case(s) "
        f"correctly FAILED against the disarmed stand-in: "
        f"{', '.join(correctly_failed)}."
    )
    print("The control can detect its own gate being silently replaced.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--demonstrate-red",
        action="store_true",
        help=(
            "run the identical case battery against a stand-in whose _gate "
            "is a no-op, and INVERT the verdict: PASS (exit 0) only if "
            "every gate-dependent case correctly FAILS against it."
        ),
    )
    args = parser.parse_args()

    probe = _load_probe_module()
    target = _DisarmedProbe(probe) if args.demonstrate_red else probe

    print("=" * 70)
    if args.demonstrate_red:
        print("DEMONSTRATE-RED -- the same battery against a _gate that is a")
        print("bare no-op. Every gate-dependent case below MUST fail.")
    else:
        print("RECEIPT: _gate in _probe_people_search_shape_live.py can REFUSE")
    print("=" * 70)

    allowed = target._alphabet()
    healthy = _healthy_trial(target.search_results)

    case_a(target, allowed, healthy)
    case_b(target, allowed, healthy)
    case_c(target, allowed, healthy)
    case_d(target, allowed, healthy)
    case_e(target, allowed, healthy)

    print()
    if args.demonstrate_red:
        return _verdict_demonstrate_red()
    return _verdict_default()


if __name__ == "__main__":
    raise SystemExit(main())
