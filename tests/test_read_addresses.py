"""The bucket-3 address table must be CHECKED, and the check must be able to FAIL.

`scripts/check_read_addresses.py` keeps `_audit/_census/read-addresses.tsv`
true: it re-drives every recorded address through the shipped
`readonly.is_read_url` and exits 1 on any disagreement, on any bucket-3 row
with no line, and on any line whose row has left the bucket. A check that
runs only when somebody remembers to run it has already stopped working, so it
runs here -- the house pattern of `tests/test_gap_rows_on_refused_addresses.py`.

**GREEN ON ITS OWN IS AMBIGUOUS.** It passes when the table is right AND when
the checker has been broken into something that finds nothing, or the boundary
mutated into admit-everything. So every planted defect below goes into a COPY
of the real table -- never the committed file -- and each must turn the check
red AND name the row it planted. The plants that matter most are the two that
are INTERNALLY CONSISTENT: a row whose class, verdict, refusal and gate all
agree with each other and are all wrong. Only the live boundary can convict
those, which is the property this instrument exists to have.

**THIS FILE GOES RED WHEN THE CENSUS MOVES A BUCKET-3 ROW, BY DESIGN.** Bank
a read row, re-rule it, or correct a direction cell, and
`test_green_on_the_real_table` fails naming the row. The remedy is to update
the table -- remove the line of a row that left, measure the address of a row
that entered -- never to relax the check. That is the tripwire that
`scripts/triage_read_gap_rows.py` also carries, and that sat red at HEAD with
nothing running it.

**AND SINCE 2026-09-23, THE RULINGS ARE ASKED TOO.** The boundary says what
the code may open; a ruling says what may be done. `M M49` was classed blocked
on nothing on a messaging thread while `DO-NOT-OPEN-MESSAGING` stood, and every
check here passed, because the row agreed with itself and with the boundary.
The operator lifted that ruling at 18:15 the same day, so the last block below
cannot plant on a real held page: each test installs its own hold on a page it
chooses and requires the row named, plus the converse -- the `STANDING-RULING`
gate may not be spent on a page its ruling does not hold -- and a note still
citing a lifted ruling.
"""
from __future__ import annotations

import pathlib
import sys
import urllib.parse

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import check_read_addresses as cra  # noqa: E402
import ruling_holds as rh  # noqa: E402

# NO MODULE-LEVEL CONSTANT BEYOND THE CONVENTIONAL ``ROOT``, deliberately. The
# impact gate couples every test file that NAMES an upper-case constant this
# file defines, as a whole word -- and a first draft's ``REAL`` matched the
# word REAL in the prose of dozens of docstrings, dragging 98 of 215 files
# into a one-file change and widening the gate to the full suite.


def _lines() -> list[str]:
    return cra.TABLE.read_text(encoding="ascii").splitlines()


def _data_indexes(lines: list[str]) -> list[int]:
    header = "\t".join(cra.COLUMNS)
    return [i for i, ln in enumerate(lines)
            if ln and not ln.startswith("#") and ln != header]


def _row(line: str) -> dict[str, str]:
    return dict(zip(cra.COLUMNS, line.split("\t")))


def _line(row: dict[str, str]) -> str:
    return "\t".join(row[c] for c in cra.COLUMNS)


def _find(lines: list[str], predicate) -> int:
    """The index of the FIRST data line satisfying ``predicate``.

    Found at runtime rather than named, so a control does not rot into a false
    alarm the day the row it named is banked. It ASSERTS it found one, so a
    table with no such row fails loudly instead of passing vacuously.
    """
    for i in _data_indexes(lines):
        if predicate(_row(lines[i])):
            return i
    raise AssertionError("the real table has no row this control can plant on")


def _plant(tmp_path: pathlib.Path, lines: list[str]) -> pathlib.Path:
    assert lines != _lines(), "the plant changed nothing: the control is broken"
    copy = tmp_path / "read-addresses.tsv"
    copy.write_text("\n".join(lines) + "\n", encoding="ascii")
    return copy


def _check(capsys, table: pathlib.Path | None = None) -> tuple[int, str]:
    argv = [] if table is None else ["--table", str(table)]
    code = cra.main(argv)
    return code, capsys.readouterr().out


# ----------------------------------------------------------------- green


def test_green_on_the_real_table(capsys) -> None:
    code, out = _check(capsys)
    assert code == 0, out
    verdicts = [ln.split(":")[0] for ln in out.splitlines()
                if ln.startswith(("GREEN:", "RED:"))]
    # BY LINE, NOT BY SUBSTRING: the gate alphabet's BUILT-UNFIRED carries the
    # letters of RED, and the first draft of this assertion failed on it.
    assert verdicts == ["GREEN"], out


def test_the_real_table_covers_bucket_three_exactly() -> None:
    """The population is census_completion's own walk, one line per row."""
    rows, problems = cra.load()
    assert not problems
    population = cra.population()
    assert population, "the bucket-3 population came back empty"
    assert sorted(cra.key(r) for r in rows) == sorted(population)


def test_every_verdict_in_the_table_is_both_words() -> None:
    """A table of only Trues or only Falses would agree with a broken gate."""
    rows, _ = cra.load()
    verdicts = {r["is_read_url"] for r in rows if r["class"] in cra.WITH_ADDRESS}
    assert verdicts == {"True", "False"}


# ------------------------------------------------ the two consistent lies


def test_a_consistent_wrong_verdict_on_an_admitted_row_turns_it_red(
        tmp_path, capsys) -> None:
    """ADMITTED rewritten as a self-consistent REFUSED. Only the boundary knows."""
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "ADMITTED")
    row = _row(lines[i])
    row.update({"class": "REFUSED", "is_read_url": "False",
                "refusal": "NO-PATTERN", "gate": "n/a"})
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: recorded is_read_url=False, the live " \
           f"boundary says True" in out


def test_a_consistent_wrong_verdict_on_a_refused_row_turns_it_red(
        tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "REFUSED")
    row = _row(lines[i])
    row.update({"class": "ADMITTED", "is_read_url": "True", "refusal": "-",
                "gate": "READER"})
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: recorded is_read_url=True, the live " \
           f"boundary says False" in out


# ------------------------------------------------------ coverage, both ways


def test_a_missing_row_turns_it_red(tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: True)
    gone = _row(lines[i])
    del lines[i]
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{gone['slice']} {gone['row']}: a bucket-3 row today" in out
    assert "NO line in the table" in out


def test_a_row_that_left_the_bucket_turns_it_red(tmp_path, capsys) -> None:
    """A line for a WRITE row: its verdict would point at nothing."""
    lines = _lines()
    stale = _row(lines[_find(lines, lambda r: True)])
    stale.update({"slice": "N", "row": "1"})  # a W row, read by hand in
    lines.append(_line(stale))                 # reader_closable_blockers.KNOWN
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert "N 1: has a line but is NOT a bucket-3 row today" in out


def test_a_duplicated_row_turns_it_red(tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: True)
    lines.insert(i, lines[i])
    dup = _row(lines[i])
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{dup['slice']} {dup['row']}: 2 lines, want exactly one" in out


def test_a_moved_direction_turns_it_red(tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: r["dir"] == "R")
    row = _row(lines[i])
    row["dir"] = "R+W"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: dir 'R+W' but the census cell now " \
           f"reads 'R'" in out


# ------------------------------------------------- the other recorded cells


def test_a_wrong_refusal_kind_turns_it_red(tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: r["refusal"].startswith("FORBIDDEN["))
    row = _row(lines[i])
    row["refusal"] = "NO-PATTERN"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: recorded refusal 'NO-PATTERN', the " \
           f"live boundary raises 'FORBIDDEN[" in out


def test_a_wrong_also_driven_verdict_turns_it_red(tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: "=>True" in r["also_driven"])
    row = _row(lines[i])
    row["also_driven"] = row["also_driven"].replace("=>True", "=>False", 1)
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: also_driven " in out
    assert "recorded False, the live boundary says True" in out


def test_a_class_contradicting_its_own_verdict_turns_it_red(
        tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "ADMITTED")
    row = _row(lines[i])
    row["is_read_url"] = "False"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: class ADMITTED contradicts its own " \
           f"recorded verdict" in out


def test_a_refusal_contradicting_its_class_turns_it_red(
        tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "REFUSED")
    row = _row(lines[i])
    row["refusal"] = "-"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: class REFUSED contradicts its own " \
           f"recorded refusal '-'" in out


def test_a_missing_table_is_a_named_problem_not_a_traceback(
        tmp_path, capsys) -> None:
    code, out = _check(capsys, tmp_path / "read-addresses.tsv")
    assert code == 1, out
    assert "the address table does not exist" in out


def test_an_off_alphabet_gate_turns_it_red(tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "ADMITTED")
    row = _row(lines[i])
    row["gate"] = "PROBABLY-FINE"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: gate 'PROBABLY-FINE' is off" in out


def test_an_unexplained_row_without_an_address_turns_it_red(
        tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: r["class"] not in cra.WITH_ADDRESS)
    row = _row(lines[i])
    row["note"] = "unknown"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: {row['class']} must say in its note" \
           in out


# ------------------------------------------------- the source column resolves


@pytest.mark.parametrize("plant, expect", [
    (lambda s: "scripts/no_such_file.py", "does not exist"),
    (lambda s: "linkedin_server/dom.py::NO_SUCH_SYMBOL_ANYWHERE",
     "source symbol NO_SUCH_SYMBOL_ANYWHERE is no longer spelled"),
    (lambda s: "_audit/_census/network.md row 9999",
     "source row 9999 is no longer a row"),
    (lambda s: "somewhere, as prose", "does not open on a repository path"),
], ids=["missing-file", "missing-symbol", "missing-census-row", "not-a-path"])
def test_a_source_that_no_longer_resolves_turns_it_red(
        tmp_path, capsys, plant, expect) -> None:
    """A citation rots into a plausible wrong answer, so it is re-resolved."""
    lines = _lines()
    i = _find(lines, lambda r: True)
    row = _row(lines[i])
    row["source"] = plant(row["source"])
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: " in out and expect in out


def test_the_source_check_reaches_every_kind_it_claims() -> None:
    """Green on the real table is only a reading if all three branches ran."""
    rows, _ = cra.load()
    assert not cra.source_problems(rows)
    symbols = sum(1 for r in rows if (m := cra._SOURCE_PATH.match(r["source"]))
                  and m.group(2))
    census_rows = sum(1 for r in rows if r["source"].startswith("_audit/_census/")
                      and cra._SOURCE_ROW.search(r["source"]))
    assert symbols and census_rows


# ---------------------------------------------- the boundary, seen working


def test_the_refusal_reader_tells_all_three_kinds_apart() -> None:
    """Read off the SHIPPED gate's sentences, never off a re-derivation."""
    base = cra.HOST
    assert cra.refusal_of(base + "feed/") == "-"
    assert cra.refusal_of(base + "analytics/") == "NO-PATTERN"
    # THE FOLLOWING LIST, not the follower list: the lane-L1 REVIEW: commit
    # admits the follower list past `/follow`, and this control needs an
    # address that is still refused by a substring with no pattern behind it.
    assert cra.refusal_of(
        base + "mynetwork/network-manager/people-follow/following/"
    ) == "FORBIDDEN[/follow]+NO-PATTERN"
    # The people-search pattern admits a query SHAPE, so a keyword that trips
    # a forbidden substring is refused by the substring ALONE.
    assert cra.refusal_of(
        base + "search/results/people/?keywords=settings"
    ) == "FORBIDDEN[settings]+PATTERN-WOULD-ADMIT"


def test_a_reworded_refusal_is_reported_not_matched() -> None:
    assert cra.kind_of_refusal("navigation blocked: something new") == \
        "UNREADABLE"


def test_a_boundary_that_admits_everything_is_caught(monkeypatch) -> None:
    from linkedin_server import readonly

    monkeypatch.setattr(readonly, "is_read_url", lambda url: True)
    problems = cra.control_problems()
    assert problems and "a third party's profile" in problems[0]


# ------------------------------------------------------ census_completion


def test_census_completion_prints_the_split_counted_off_the_table(
        capsys) -> None:
    import census_completion as cc

    rows = list(cc.walk())
    split, problems = cc.bucket3_split(rows)
    assert not problems and split is not None
    table, _ = cra.load()
    assert split == cra.split(table)
    assert split["rows"] == sum(split["class:" + c] for c in cra.CLASSES)
    out: list[str] = []
    figures = cc.report(rows, out)
    text = "\n".join(out)
    assert f"the boundary ADMITS the row's page      " \
           f"{split['class:ADMITTED']:4d}" in text
    assert figures["b3_blocked_on_nothing"] == split["blocked_on_nothing"]


def test_census_completion_withholds_the_split_when_the_table_drifts(
        tmp_path, monkeypatch) -> None:
    """A table that no longer covers the bucket yields NO b3 figures at all."""
    import census_completion as cc

    lines = _lines()
    del lines[_find(lines, lambda r: True)]
    monkeypatch.setattr(cra, "TABLE", _plant(tmp_path, lines))
    monkeypatch.setattr(cra.load, "__defaults__", (cra.TABLE,))
    out: list[str] = []
    figures = cc.report(list(cc.walk()), out)
    assert "BUCKET 3 SPLIT WITHHELD" in "\n".join(out)
    assert not any(k.startswith("b3_") for k in figures)


@pytest.mark.parametrize("gate", cra.BLOCKED_ON_NOTHING)
def test_blocked_on_nothing_is_a_subset_of_the_gate_alphabet(gate) -> None:
    assert gate in cra.GATES


# ------------------------------- the edge: a RULING holds the page (2026-09-23)
#
# `M M49` was classed READER -- blocked on nothing -- on a messaging thread
# while `DO-NOT-OPEN-MESSAGING` stood, and run on that table the edge named it
# and nothing else. The operator lifted that ruling at 18:15 the same day, so
# no admitted row sits on a held page today and green on the real table checks
# nothing on its own. Every plant below therefore installs its OWN hold, on a
# page it chooses, into the holds table the edge reads -- never the real table
# or the real holds -- and must name the row.


def _page(row: dict[str, str]) -> str:
    return urllib.parse.urlsplit(row["address"]).path


def _admitted_and_unheld(row: dict[str, str]) -> bool:
    return (row["class"] == "ADMITTED" and _page(row).endswith("/")
            and rh.surface_hold(_page(row)) is None)


def _plant_hold(monkeypatch, surface: str, status: str = "STANDING",
                hold_id: str = "PLANTED-RULING") -> str:
    monkeypatch.setitem(rh.ROW_HOLDS, hold_id, rh.Hold(
        status=status, binds="surface", surface=surface))
    return hold_id


def test_the_real_table_passes_the_edge() -> None:
    """Green on the real table.

    On its own that says little: since the register of 2026-09-23 no hold
    binds a page, so the edge has nothing to fire on here. What it CAN do is
    shown below, each test on a hold it installs itself.
    """
    rows, _ = cra.load()
    assert cra.ruling_problems(rows) == []


def test_the_edge_reads_the_holds_table_it_is_given(monkeypatch) -> None:
    """Not vacuous: install a hold on a real admitted row's page and the real table goes red."""
    rows, _ = cra.load()
    row = next(r for r in rows if _admitted_and_unheld(r)
               and r["gate"] in cra.BLOCKED_ON_NOTHING)
    _plant_hold(monkeypatch, _page(row))
    problems = cra.ruling_problems(rows)
    assert any(p.startswith(f"{row['slice']} {row['row']}: classed blocked on "
                            f"nothing") for p in problems), problems


def test_blocked_on_nothing_on_a_held_page_turns_it_red(
        tmp_path, capsys, monkeypatch) -> None:
    """THE PLANT THIS EDGE EXISTS FOR: `M M49` as it stood before 18:15."""
    lines = _lines()
    i = _find(lines, _admitted_and_unheld)
    row = _row(lines[i])
    row["gate"] = "READER"
    lines[i] = _line(row)
    held = _plant_hold(monkeypatch, _page(row))
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: classed blocked on nothing (gate " \
           f"READER), but its page {_page(row)} sits on {_page(row)}, which " \
           f"{held} holds (STANDING)" in out


def test_a_held_page_under_any_other_gate_turns_it_red(
        tmp_path, capsys, monkeypatch) -> None:
    lines = _lines()
    i = _find(lines, _admitted_and_unheld)
    row = _row(lines[i])
    row["gate"] = "PRESS"
    lines[i] = _line(row)
    held = _plant_hold(monkeypatch, _page(row))
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: gate PRESS, but {held} (STANDING) " \
           f"holds its page {_page(row)} before anything past the boundary -- " \
           f"the gate is STANDING-RULING" in out


def test_a_held_page_whose_note_cites_no_hold_turns_it_red(
        tmp_path, capsys, monkeypatch) -> None:
    lines = _lines()
    i = _find(lines, _admitted_and_unheld)
    row = _row(lines[i])
    row["gate"] = "STANDING-RULING"
    lines[i] = _line(row)
    held = _plant_hold(monkeypatch, _page(row))
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: its page sits on {_page(row)}, so " \
           f"its note must cite HELD BY `{held}`" in out


def test_a_standing_ruling_gate_off_its_page_turns_it_red(
        tmp_path, capsys, monkeypatch) -> None:
    """The new gate cannot be spent on a page the ruling it cites does not hold."""
    lines = _lines()
    i = _find(lines, _admitted_and_unheld)
    row = _row(lines[i])
    held = _plant_hold(monkeypatch, "/planted-elsewhere/")
    row["gate"] = "STANDING-RULING"
    row["note"] += f" HELD BY `{held}`"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: gate STANDING-RULING citing " \
           f"{held}, but its page {_page(row)} is not on " \
           f"/planted-elsewhere/" in out


def test_a_standing_ruling_gate_citing_nothing_turns_it_red(
        tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, _admitted_and_unheld)
    row = _row(lines[i])
    row["gate"] = "STANDING-RULING"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: gate STANDING-RULING, and its note " \
           f"cites no STANDING hold with HELD BY" in out


def test_a_pending_question_on_a_page_convicts_a_blocked_on_nothing_row(
        tmp_path, capsys, monkeypatch) -> None:
    """A question not yet answered holds a page exactly as firmly as a ruling.

    Self-sufficient on purpose: it makes its OWN blocked-on-nothing row, so it
    does not depend on which rows are blocked on nothing today.
    """
    lines = _lines()
    i = _find(lines, _admitted_and_unheld)
    row = _row(lines[i])
    row["gate"] = "READER"
    lines[i] = _line(row)
    held = _plant_hold(monkeypatch, _page(row), status="PENDING",
                       hold_id="PLANTED-QUESTION")
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: classed blocked on nothing (gate " \
           f"READER), but its page {_page(row)} sits on {_page(row)}, which " \
           f"{held} holds (PENDING)" in out


def test_a_note_still_citing_a_lifted_ruling_turns_it_red(
        tmp_path, capsys) -> None:
    """A lifted ruling cited as a hold is history published as a hold."""
    lines = _lines()
    i = _find(lines, lambda r: True)
    row = _row(lines[i])
    lifted = next(iter(rh.LIFTED_ROW_HOLDS))
    row["note"] += f" HELD BY `{lifted}`"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{row['slice']} {row['row']}: its note cites HELD BY `{lifted}`, " \
           f"and that ruling is lifted" in out


def test_census_completion_withholds_the_split_when_the_edge_fails(
        tmp_path, monkeypatch) -> None:
    """A blocked-on-nothing figure over a table the rulings refute is not printed."""
    import census_completion as cc

    lines = _lines()
    i = _find(lines, _admitted_and_unheld)
    row = _row(lines[i])
    row["gate"] = "READER"
    lines[i] = _line(row)
    _plant_hold(monkeypatch, _page(row))
    monkeypatch.setattr(cra, "TABLE", _plant(tmp_path, lines))
    monkeypatch.setattr(cra.load, "__defaults__", (cra.TABLE,))
    out: list[str] = []
    figures = cc.report(list(cc.walk()), out)
    text = "\n".join(out)
    assert "BUCKET 3 SPLIT WITHHELD" in text
    assert f"{row['slice']} {row['row']}: classed blocked on nothing" in text
    assert "b3_blocked_on_nothing" not in figures
