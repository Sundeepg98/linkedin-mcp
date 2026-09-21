"""Show the census's DICT-LITERAL walk failing, three ways, then passing.

A CHECK THAT CANNOT FAIL CERTIFIES NOTHING, and this one guards a change whose
whole subject is a walk that could not see a construct. So nothing here is
admitted on a green run: each arm is driven RED on a mutation and green on its
removal, in one process, and both are printed.

## THE THREE ARMS, AND WHY EACH ONE EXISTS

**ARM 1 -- THE WALK SEES BOTH OF ``server._error``'S RENDERINGS.** Until
2026-09-21 it saw neither, and the exclusion was not one condition but three,
each sufficient alone (see the comment above ``_Walker.visit_Return``). The
subject is a SYNTHETIC module carrying both renderings transcribed onto a
needle no page ever chose, PLUS three negatives the walk saw before the change.
The negatives are the half that matters: a walk that had simply stopped
returning anything would look identical to one that had gained the construct,
and the negatives are what tell those apart.

**ARM 2 -- THE CONSTANT PRE-SKIP IS BEHAVIOUR-PRESERVING.** ``_offer_dict``
skips a key whose value is an ``ast.Constant`` before calling
``_record_field``. The claim is that ``_record_field`` could not have recorded
such a key anyway. That is an argument until it is run, so this arm runs the
walk with the skip and without it and requires byte-identical rows.

**ARM 3 -- ``_segment`` IS ``ast.get_source_segment``.** The census stopped
calling the stdlib function directly because it re-splits its whole ``source``
argument per call, which was measured at 12 of 16 profiled seconds on one
module. A REIMPLEMENTATION OF A STDLIB FUNCTION IS A LIABILITY UNLESS IT IS
PROVEN EQUAL, so this arm compares the two over every located node of the
modules it names -- and prints the ones it did NOT read -- plus a SYNTHETIC
subject carrying multi-byte characters. That last part is the half that
matters: a byte-offset slice is exactly what a multi-byte character breaks,
and this repository is strict-ASCII, so no real module can supply the case.

## AND ONE THING THAT IS NOT A CHECK

``--narrow`` prints the counterfactual: the current walk beside the same walk
with its two dict entry points removed, over the real package. That is what
the exclusion used to hide, and keeping it here rather than in a throwaway
harness is what makes the before/after in
``_audit/2026-09-21-the-dict-literal-exclusion.md`` re-derivable at any later
revision instead of only at the one it was taken on. **It is also a regression
detector**: the delta IS the cost of the exclusion, so a delta collapsing
toward zero means somebody has re-narrowed the walk.

    python scripts/_check_the_dict_literal_walk_can_fail.py
    python scripts/_check_the_dict_literal_walk_can_fail.py --narrow

Exit: 0 every arm behaved in both directions, 1 an arm failed to fire, 2 it
could not run at all.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any, Callable, Optional

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import _census_message_interpolations as C  # noqa: E402

#: ARM 3's real-module subject. NOT the whole package, and the omission is
#: printed rather than left to be discovered: the STDLIB side of the
#: comparison is the very function whose cost this change removed, so it
#: re-splits the file per node and sweeping all 46 modules costs minutes for
#: no extra shape. These are swept IN FULL, every located node.
SEGMENT_MODULES: tuple[str, ...] = (
    "errors.py", "coerce.py", "creator_analytics.py", "intro_fields.py",
    "chart_labels.py", "paths.py", "transport.py", "profile_lock.py",
)

#: The shapes a small ASCII module cannot supply, built here so they are
#: covered anyway. A segment extractor that slices by BYTE offset is exactly
#: what a multi-byte character breaks, and this package is strict-ASCII, so
#: no real module can exercise that path -- the literal below is assembled
#: from ``chr`` calls to keep THIS file ASCII while the parsed text is not.
SEGMENT_EDGE_SOURCE = (
    "ACCENTED = '"
    + chr(0x00E9) + chr(0x00FC) + chr(0x4E2D) + chr(0x1F600)
    + "'\n"
    "\n"
    "def spans_several_lines(a, b):\n"
    "    return outer(\n"
    "        inner(a,\n"
    "              b),\n"
    "        '" + chr(0x00E9) + " tail',\n"
    "    )\n"
    "\n"
    "def starts_mid_line(x):\n"
    "    y = 1; z = f'{x!r} " + chr(0x4E2D) + " {y}'\n"
    "    return z\n"
    "\n"
    "def nested(x):\n"
    "    return f\"outer {f'inner {x}'} done\"\n"
)

#: ARM 1's subject. ``server._error``'s two renderings, transcribed onto an
#: obviously synthetic needle, plus three shapes the pre-2026-09-21 walk
#: already saw.
CONTROL_SOURCE = '''
def rendering_one(exc):
    """The ANNASSIGN form. Dropped by _record_field's target-shape gate."""
    out: dict = {"error": "kind", "message": scrub(f"SYNTHETIC-NEEDLE {exc}")}
    return out


def rendering_two(exc):
    """The RETURN form. Never offered to a recorder at all."""
    return {"error": "unexpected", "message": scrub(f"SYNTHETIC-NEEDLE {exc}")}


def negative_subscript(exc, out):
    """SEEN BEFORE THE CHANGE. If this is missing, this script is broken."""
    out["message"] = f"SYNTHETIC-NEEDLE {exc}"


def negative_raise(exc):
    """SEEN BEFORE THE CHANGE."""
    raise ValueError(f"SYNTHETIC-NEEDLE {exc}")


def negative_log(exc):
    """SEEN BEFORE THE CHANGE."""
    logger.warning("SYNTHETIC-NEEDLE %s", exc)
'''

#: ARM 2's subject. Every ``ast.Constant`` shape a dict value can take, beside
#: two built values that MUST still be recorded, so a skip that swallowed
#: everything could not pass.
CONSTANT_SOURCE = '''
def constants_only(value):
    return {
        "message": "a plain string",
        "reason": 7,
        "detail": None,
        "why": True,
        "note": 1.5,
        "error": b"bytes",
    }


def built_values(exc, value):
    return {
        "message": f"SYNTHETIC-NEEDLE {exc}",
        "why": "a" + str(value),
    }
'''


def _functions(rows: list[dict[str, Any]]) -> set[str]:
    return {row["function"] for row in rows}


def _walk(sources: dict[str, str]) -> list[dict[str, Any]]:
    return C.census_sources(sources, frozenset())


def _run(label: str, arm: Callable[[], Optional[str]]) -> bool:
    """Print an arm's verdict. ``None`` from ``arm`` means it held."""
    problem = arm()
    print("  %-12s %s" % ("HELD" if problem is None else "FAILED", label))
    if problem is not None:
        print("        %s" % problem)
    return problem is None


# ---------------------------------------------------------------------------
# ARM 1 -- the walk sees both renderings
# ---------------------------------------------------------------------------

RENDERINGS = {"rendering_one", "rendering_two"}
NEGATIVES = {"negative_subscript", "negative_raise", "negative_log"}


def arm_one() -> Optional[str]:
    seen = _functions(_walk({"_control.py": CONTROL_SOURCE}))
    missing_negatives = sorted(NEGATIVES - seen)
    if missing_negatives:
        return (
            "THIS SCRIPT IS BROKEN, not the walk: shapes the walk saw before "
            "the change are missing: %s" % ", ".join(missing_negatives)
        )
    missing = sorted(RENDERINGS - seen)
    if missing:
        return "the walk cannot see %s" % ", ".join(missing)
    return None


def mutate_one() -> None:
    """Restore the pre-2026-09-21 walk by removing the two entry points."""
    del C._Walker.visit_Return
    del C._Walker.visit_Dict


def unmutate_one(saved: dict[str, Any]) -> None:
    C._Walker.visit_Return = saved["visit_Return"]
    C._Walker.visit_Dict = saved["visit_Dict"]


# ---------------------------------------------------------------------------
# ARM 2 -- the constant pre-skip records nothing extra
# ---------------------------------------------------------------------------

def _offer_without_skip(self: Any, node: ast.Dict) -> None:
    """``_offer_dict`` with the ``ast.Constant`` shortcut removed."""
    if id(node) in self._dicts_opened:
        return
    self._dicts_opened.add(id(node))
    for key, value in zip(node.keys, node.values):
        if key is None:
            continue
        if not (isinstance(key, ast.Constant) and isinstance(key.value, str)):
            continue
        self._record_field(key, [C._dict_literal_target(key.value)], value)


def arm_two() -> Optional[str]:
    sources = {"_constants.py": CONSTANT_SOURCE}
    with_skip = _walk(sources)
    if not with_skip:
        return (
            "THIS SCRIPT IS BROKEN: the subject recorded nothing at all, so "
            "an equality between two empty lists would prove nothing"
        )
    shipped = C._Walker._offer_dict
    C._Walker._offer_dict = _offer_without_skip
    try:
        without_skip = _walk(sources)
    finally:
        C._Walker._offer_dict = shipped
    if with_skip != without_skip:
        return (
            "the pre-skip is NOT behaviour-preserving: %d row(s) with it, "
            "%d without" % (len(with_skip), len(without_skip))
        )
    return None


def mutate_two() -> None:
    """Make the skip drop a value it must keep."""
    def greedy(self: Any, node: ast.Dict) -> None:
        if id(node) in self._dicts_opened:
            return
        self._dicts_opened.add(id(node))
        for key, value in zip(node.keys, node.values):
            if key is None:
                continue
            if not (isinstance(key, ast.Constant) and isinstance(key.value, str)):
                continue
            if isinstance(value, (ast.Constant, ast.JoinedStr)):
                continue  # THE MUTATION: JoinedStr must not be skipped
            self._record_field(key, [C._dict_literal_target(key.value)], value)

    C._Walker._offer_dict = greedy


# ---------------------------------------------------------------------------
# ARM 3 -- _segment equals ast.get_source_segment
# ---------------------------------------------------------------------------

def arm_three() -> Optional[str]:
    subjects = {name: (C.PACKAGE / name).read_text(encoding="utf-8")
                for name in SEGMENT_MODULES}
    subjects["<multi-byte edge cases>"] = SEGMENT_EDGE_SOURCE

    compared = 0
    multibyte = 0
    for name, text in subjects.items():
        tree = ast.parse(text, filename=name)
        for node in ast.walk(tree):
            if not hasattr(node, "lineno"):
                continue
            compared += 1
            mine = C._segment(text, node)
            theirs = ast.get_source_segment(text, node)
            if mine != theirs:
                return (
                    "%s: disagreement at line %s on %s"
                    % (name, getattr(node, "lineno", "?"), type(node).__name__)
                )
            if mine is not None and not mine.isascii():
                multibyte += 1
    if compared < 1000:
        return (
            "THIS SCRIPT IS BROKEN: only %d node(s) compared, which is too "
            "few for an agreement to mean anything" % compared
        )
    if multibyte < 4:
        return (
            "THIS SCRIPT IS BROKEN: only %d multi-byte segment(s) compared. "
            "A byte-offset slice is exactly what a multi-byte character "
            "breaks, so an agreement reached without one proves the easy "
            "half" % multibyte
        )
    modules = len(list(C.PACKAGE.glob("*.py")))
    uncovered = sorted(
        p.name for p in C.PACKAGE.glob("*.py") if p.name not in SEGMENT_MODULES
    )
    print("        compared %d located nodes (%d carrying multi-byte text) "
          "over %d of %d package modules IN FULL, plus a synthetic edge-case "
          "module." % (compared, multibyte, len(SEGMENT_MODULES), modules))
    print("        DID NOT RUN over %d module(s): %s"
          % (len(uncovered), ", ".join(uncovered)))
    return None


def mutate_three() -> None:
    """An off-by-one on the start column -- the classic slice error."""
    shipped = C._segment

    def skewed(text: str, node: ast.AST) -> Optional[str]:
        out = shipped(text, node)
        return out[1:] if out else out

    C._segment = skewed  # type: ignore[assignment]


def unmutate_three(saved: Any) -> None:
    C._segment = saved


# ---------------------------------------------------------------------------

def _totals(rows: list[dict[str, Any]]) -> tuple[int, int, int]:
    subs = sum(len(r["fields"]) for r in rows)
    short = sum(1 for r in rows if any(f["shortlist"] for f in r["fields"]))
    return len(rows), subs, short


def narrow() -> int:
    """What the exclusion used to hide, measured against the current walk."""
    sources = {p.name: p.read_text(encoding="utf-8")
               for p in sorted(C.PACKAGE.glob("*.py"))}
    errors = C._package_error_names(C.PACKAGE)

    wide = C.census_sources(sources, errors)
    saved = {"visit_Return": C._Walker.visit_Return,
             "visit_Dict": C._Walker.visit_Dict}
    mutate_one()
    try:
        narrowed = C.census_sources(sources, errors)
    finally:
        unmutate_one(saved)

    print("subject digest %s over %d modules"
          % (C.source_digest(sources)["combined"], len(sources)))
    print("")
    print("%-34s %6s %10s %12s" % ("", "sites", "sub-exprs", "shortlisted"))
    print("%-34s %6d %10d %12d" % ("WITH the dict entry points", *_totals(wide)))
    print("%-34s %6d %10d %12d"
          % ("WITHOUT them (pre-2026-09-21)", *_totals(narrowed)))
    a, b, c = _totals(wide)
    d, e, f = _totals(narrowed)
    print("%-34s %+6d %+10d %+12d" % ("THE EXCLUSION'S COST", a - d, b - e, c - f))
    print("")

    seen = {(r["module"], r["line"], r["function"], r["kind"], r["target"])
            for r in narrowed}
    hidden = [r for r in wide
              if (r["module"], r["line"], r["function"], r["kind"],
                  r["target"]) not in seen]
    shortlisted = [r for r in hidden if any(f["shortlist"] for f in r["fields"])]
    print("SITES THE EXCLUSION HID THAT REACH THE ADDRESS SHORTLIST: %d"
          % len(shortlisted))
    for row in shortlisted:
        hits = [f["expr"] for f in row["fields"] if f["shortlist"]]
        print("   %-12s %-24s %-28s %s"
              % (row["module"], row["function"], row["target"], hits))
    if a == d:
        print("")
        print("WARNING: zero delta. Either this package has stopped using "
              "dict literals, which is implausible, or the walk has been "
              "re-narrowed.")
        return 1
    return 0


def main() -> int:
    if "--narrow" in sys.argv[1:]:
        return narrow()
    saved_entries = {
        "visit_Return": C._Walker.visit_Return,
        "visit_Dict": C._Walker.visit_Dict,
    }
    saved_offer = C._Walker._offer_dict
    saved_segment = C._segment

    print("BEFORE THE MUTATIONS -- every arm must HOLD")
    green = [
        _run("arm 1: the walk sees both renderings", arm_one),
        _run("arm 2: the constant pre-skip is inert", arm_two),
        _run("arm 3: _segment == ast.get_source_segment", arm_three),
    ]
    print("")

    print("MUTATION 1 -- the two dict entry points are removed (the walk as "
          "it stood before 2026-09-21)")
    mutate_one()
    try:
        red_one = not _run("arm 1", arm_one)
    finally:
        unmutate_one(saved_entries)
    print("")

    print("MUTATION 2 -- the pre-skip is widened to swallow an f-string")
    mutate_two()
    try:
        red_two = not _run("arm 2", arm_two)
    finally:
        C._Walker._offer_dict = saved_offer
    print("")

    print("MUTATION 3 -- _segment loses its first character")
    mutate_three()
    try:
        red_three = not _run("arm 3", arm_three)
    finally:
        unmutate_three(saved_segment)
    print("")

    if not all(green):
        print("FAIL: an arm did not hold on the unmutated tree.")
        return 1
    reds = {"arm 1": red_one, "arm 2": red_two, "arm 3": red_three}
    silent = sorted(name for name, fired in reds.items() if not fired)
    if silent:
        print("FAIL: %s stayed green under its mutation, so it certifies "
              "nothing." % ", ".join(silent))
        return 1
    print("OK: all three arms held on the tree and all three fired on their "
          "mutation.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 -- a control that cannot run says so
        print("COULD NOT RUN: %s: %s" % (type(exc).__name__, exc))
        raise SystemExit(2)
