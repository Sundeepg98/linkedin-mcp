"""A key written twice keeps the second value and BOTH comments.

`CENSUS_SETTLED_CONTROLS` carries one entry per surface, each with a comment
naming the readings behind its number. Found 2026-09-05: `post_composer`
appears TWICE, eight lines apart, with two DIFFERENT comments --

    "31, 31, 31 -- three readings across two days..."
    "31 twice, 2026-08-31, identical on every count."

-- and Python silently keeps the second. Two authors each recorded a baseline
for the same surface, neither aware of the other.

**THE VALUES AGREE, SO NOTHING IS WRONG TODAY, AND THAT IS EXACTLY WHY THIS
NEEDS AN INSTRUMENT RATHER THAN A FIX.** A duplicate whose values match is
invisible: no test fails, no answer changes, and the file reads as though both
comments are live. Edit the first one's number -- re-measure that surface, bump
it, write down why -- and nothing happens at all. The reading is applied, the
comment is published, and the dict keeps the other value. That is a silent
no-op wearing the shape of a measurement, and this repository has now written
up three of those.

WHY AST AND NOT `len(dict)`. By the time the module is imported the duplicate
is GONE -- Python collapsed it at parse time and the dict has one key. A
runtime check cannot see this class at all, which is the same reason the
enumeration guards elsewhere read source rather than state.

SCOPE. This checks the dicts a stale comment would mislead a reader ABOUT: the
census tables that carry per-surface evidence in their comments. It is not a
general lint, and it deliberately does not scan every dict in the package --
a guard that fires everywhere gets a blanket exemption written for it, which is
how a check stops being one.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
SERVER = REPO / "linkedin_server" / "server.py"

#: The tables whose comments carry evidence, so a shadowed entry hides a
#: measurement rather than merely a value.
GUARDED = (
    "CENSUS_SETTLED_CONTROLS",
    "CENSUS_SURFACES",
    "CENSUS_SURFACE_COST",
    "CENSUS_ITEM_RULES",
    "CENSUS_SDUI_NEEDLES",
)


def _dict_literals(source: str) -> dict[str, list[str]]:
    """Every guarded assignment's literal string keys, IN SOURCE ORDER.

    Returns name -> list of keys as written, duplicates preserved. That is the
    whole point: the parsed dict cannot answer this question because it has
    already thrown the duplicate away.
    """
    tree = ast.parse(source)
    out: dict[str, list[str]] = {}
    for node in tree.body:
        target = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target = node.target.id
        elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            target = node.targets[0].id
        if target not in GUARDED or not isinstance(node.value, ast.Dict):
            continue
        keys: list[str] = []
        for key in node.value.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                keys.append(key.value)
        out[target] = keys
    return out


def test_the_guarded_tables_were_all_found():
    """A scan that matched nothing would pass every test below.

    The refusal-must-name-what-it-saw rule: this asserts the tables EXIST
    before anything asserts they are clean, so a rename upstream turns this
    red instead of turning the file into a no-op.
    """
    found = _dict_literals(SERVER.read_text(encoding="utf-8"))
    missing = [name for name in GUARDED if name not in found]
    assert not missing, (
        f"these guarded tables were not found in server.py as dict literals: "
        f"{missing}. Either they were renamed or they stopped being literals, "
        "and until this is fixed the duplicate check below scans nothing."
    )
    for name, keys in found.items():
        assert keys, f"{name} parsed as a dict with no string keys"


@pytest.mark.parametrize("table", GUARDED)
def test_no_surface_is_named_twice(table):
    """One key, one entry, one comment that is actually live."""
    keys = _dict_literals(SERVER.read_text(encoding="utf-8")).get(table, [])
    seen: dict[str, int] = {}
    for key in keys:
        seen[key] = seen.get(key, 0) + 1
    duplicated = sorted(k for k, n in seen.items() if n > 1)
    assert not duplicated, (
        f"{table} names {duplicated} more than once. Python keeps the LAST "
        "value and discards the earlier one along with nothing else -- the "
        "earlier COMMENT stays in the file and reads as live. If the values "
        "agree, nothing is broken today and editing the shadowed one is a "
        "silent no-op. Merge the entries, keeping both sets of readings in "
        "one comment."
    )


def test_the_check_would_catch_a_duplicate_it_was_not_shown():
    """SHOWN FAILING on synthetic source, in both directions.

    The parametrized test above passes when the file is clean, and a check
    that has only ever been seen passing certifies nothing. This drives the
    same function over source that certainly contains the defect -- and over
    source that certainly does not, so a checker that flagged everything would
    fail here too.
    """
    dirty = (
        "CENSUS_SETTLED_CONTROLS = {\n"
        '    "a": 1,\n'
        "    # a comment claiming one set of readings\n"
        '    "b": 2,\n'
        "    # a comment claiming a different set, for the same surface\n"
        '    "a": 3,\n'
        "}\n"
    )
    keys = _dict_literals(dirty)["CENSUS_SETTLED_CONTROLS"]
    assert keys == ["a", "b", "a"], keys
    assert len(keys) != len(set(keys)), (
        "the extractor collapsed the duplicate, which means it is reading the "
        "parsed dict rather than the source and cannot see this class at all"
    )

    clean = 'CENSUS_SETTLED_CONTROLS = {\n    "a": 1,\n    "b": 2,\n}\n'
    keys = _dict_literals(clean)["CENSUS_SETTLED_CONTROLS"]
    assert len(keys) == len(set(keys)), keys


def test_search_appearances_carries_the_baseline_it_earned():
    """The entry added 2026-09-05, pinned so a silent removal is visible.

    Three readings by two instruments agreed on this number. The value is
    pinned here rather than only in the dict because the settle report's
    `unknown` verdict is indistinguishable from a passing check to anyone
    reading a tool answer, so losing this entry would quietly restore that
    ambiguity.
    """
    from linkedin_server import server

    assert server.CENSUS_SETTLED_CONTROLS["search_appearances"] == 51
