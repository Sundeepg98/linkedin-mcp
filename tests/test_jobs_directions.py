"""The jobs-directions side table must be CHECKED, and the check must be able to FAIL.

``scripts/check_jobs_directions.py`` keeps ``_audit/_census/jobs-directions.tsv``
true: one line per still-GAP ``jobs.md`` row, its direction, and -- for every
row with a read half -- the same class/address/boundary columns
``scripts/check_read_addresses.py`` keeps true for bucket 3. It exits 1 on any
disagreement with the population, the row's own capability cell, section 2's
range table, the source column, or the live read boundary.

**GREEN ON ITS OWN IS AMBIGUOUS.** It passes when the table is right AND when
the checker has been broken into something that finds nothing, or the
boundary mutated into admit-everything. So every planted defect below goes
into a COPY of the real table -- never the committed file -- and each must
turn the check red AND name the row it planted. Two plants are INTERNALLY
CONSISTENT lies -- a row whose class, verdict and refusal all agree with each
other and are all wrong -- and only the live boundary, imported unchanged
from ``check_read_addresses``, can convict those.

**THIS FILE GOES RED WHEN THE CENSUS OR ``jobs.md`` SECTION 2 MOVES A ROW, BY
DESIGN.** Bank a still-GAP jobs row, re-rule one, or edit a range's direction
cell, and a test here fails naming the row. The remedy is to update the
table, never to relax the check.

The read-row columns (class, address, basis, source_kind, is_read_url,
refusal, gate, also_driven) are the bucket-3 vocabulary, unchanged, so this
file only re-proves what is NEW here: the population is still-GAP jobs rows
(not bucket 3), the direction columns (dir, dir_phrase, dir_basis), the WRITE
lane, and the two pure functions ``census_completion.py`` calls
(``census_figures``, ``report_lines``).
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import check_jobs_directions as cjd  # noqa: E402

# NO MODULE-LEVEL CONSTANT BEYOND ``ROOT``, deliberately -- see
# tests/test_read_addresses.py's own note: the impact gate couples every test
# file that NAMES an upper-case constant this file defines, as a whole word.


def _lines() -> list[str]:
    return cjd.TABLE.read_text(encoding="ascii").splitlines()


def _data_indexes(lines: list[str]) -> list[int]:
    header = "\t".join(cjd.COLUMNS)
    return [i for i, ln in enumerate(lines)
            if ln and not ln.startswith("#") and ln != header]


def _row(line: str) -> dict[str, str]:
    return dict(zip(cjd.COLUMNS, line.split("\t")))


def _line(row: dict[str, str]) -> str:
    return "\t".join(row[c] for c in cjd.COLUMNS)


def _find(lines: list[str], predicate) -> int:
    """The index of the FIRST data line satisfying ``predicate``.

    Found at runtime rather than named, so a control does not rot into a
    false alarm the day the row it named is banked. It ASSERTS it found one,
    so a table with no such row fails loudly instead of passing vacuously.
    """
    for i in _data_indexes(lines):
        if predicate(_row(lines[i])):
            return i
    raise AssertionError("the real table has no row this control can plant on")


def _plant(tmp_path: pathlib.Path, lines: list[str]) -> pathlib.Path:
    assert lines != _lines(), "the plant changed nothing: the control is broken"
    copy = tmp_path / "jobs-directions.tsv"
    copy.write_text("\n".join(lines) + "\n", encoding="ascii")
    return copy


def _check(capsys, table: pathlib.Path | None = None) -> tuple[int, str]:
    argv = [] if table is None else ["--table", str(table)]
    code = cjd.main(argv)
    return code, capsys.readouterr().out


# ----------------------------------------------------------------- green


def test_green_on_the_real_table(capsys) -> None:
    code, out = _check(capsys)
    assert code == 0, out
    verdicts = [ln.split(":")[0] for ln in out.splitlines()
                if ln.startswith(("GREEN:", "RED:"))]
    # BY LINE, NOT BY SUBSTRING: the gate alphabet's BUILT-UNFIRED carries the
    # letters of RED.
    assert verdicts == ["GREEN"], out


def test_the_real_table_covers_the_population_exactly() -> None:
    """The population is census_completion's own walk, one line per row."""
    rows, problems = cjd.load()
    assert not problems
    population = cjd.population()
    assert population, "the jobs-direction population came back empty"
    assert sorted(cjd.key(r) for r in rows) == sorted(population)


def test_every_read_rows_verdict_is_both_words() -> None:
    """A table of only Trues or only Falses would agree with a broken gate."""
    rows, _ = cjd.load()
    verdicts = {r["is_read_url"] for r in rows if r["is_read_url"] != "-"}
    assert verdicts == {"True", "False"}


# ------------------------------------------------ the two consistent lies


def test_a_consistent_wrong_verdict_on_an_admitted_row_turns_it_red(
        tmp_path, capsys) -> None:
    """ADMITTED rewritten as a self-consistent REFUSED. Only the boundary knows."""
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "ADMITTED")
    row = _row(lines[i])
    tag = f"{row['slice']} {row['row']}"
    row.update({"class": "REFUSED", "is_read_url": "False",
                "refusal": "NO-PATTERN", "gate": "n/a"})
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert (f"{tag}: recorded is_read_url=False, the live boundary says "
            f"True") in out


def test_a_consistent_wrong_verdict_on_a_refused_row_turns_it_red(
        tmp_path, capsys) -> None:
    """REFUSED rewritten as a self-consistent ADMITTED. Only the boundary knows."""
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "REFUSED")
    row = _row(lines[i])
    tag = f"{row['slice']} {row['row']}"
    row.update({"class": "ADMITTED", "is_read_url": "True", "refusal": "-",
                "gate": "READER"})
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert (f"{tag}: recorded is_read_url=True, the live boundary says "
            f"False") in out


# ------------------------------------------------------ coverage, both ways


def test_a_missing_still_gap_row_turns_it_red(tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: True)
    gone = _row(lines[i])
    del lines[i]
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{gone['slice']} {gone['row']}: a still-GAP jobs row today" in out
    assert "NO line in the table" in out


def test_a_line_for_a_row_that_left_gap_turns_it_red(tmp_path, capsys) -> None:
    """A jobs row id that is no longer GAP today: its line points at nothing."""
    import census_completion as cc

    left = next((letter, rid) for letter, rid, state, _d in cc.walk()
                if letter == "J" and state != "GAP")
    lines = _lines()
    i = _find(lines, lambda r: True)
    row = _row(lines[i])
    row["row"] = left[1]
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"J {left[1]}: has a line but is NOT a still-GAP jobs row today" in out


def test_a_duplicated_line_turns_it_red(tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: True)
    lines.insert(i, lines[i])
    dup = _row(lines[i])
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{dup['slice']} {dup['row']}: 2 lines, want exactly one" in out


# ------------------------------------------------------- direction columns


def test_a_dir_phrase_no_longer_in_the_capability_cell_turns_it_red(
        tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: r["dir"] != "R+W")
    row = _row(lines[i])
    tag = f"{row['slice']} {row['row']}"
    row["dir_phrase"] = "zzznocapabilitymatch"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert (f"{tag}: dir_phrase 'zzznocapabilitymatch' is no longer written "
            f"in the row's capability cell") in out


def test_a_verb_row_the_range_now_disagrees_with_turns_it_red(
        tmp_path, capsys) -> None:
    """A VERB-OVER-RANGE row already records a range disagreement; relabel it
    VERB and the checker must read that same disagreement as a defect.

    Changing ``dir`` instead would also trip the WRITE/class and phrase
    checks, so ``dir_basis`` is the one field this plant touches -- the row
    already disagrees with section 2, the plant only mis-labels why.
    """
    lines = _lines()
    i = _find(lines, lambda r: r["dir_basis"] == "VERB-OVER-RANGE")
    row = _row(lines[i])
    tag = f"{row['slice']} {row['row']}"
    row["dir_basis"] = "VERB"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{tag}: dir_basis VERB, but section 2's range now files it" in out


def test_a_stale_verb_over_range_disagreement_turns_it_red(
        tmp_path, capsys) -> None:
    """A VERB row whose section-2 range already agrees with it, relabelled
    VERB-OVER-RANGE: the recorded disagreement no longer exists.
    """
    import _check_jobs_range_directions as jrd

    resolved, _unresolved = jrd.jobs_directions()
    lines = _lines()
    i = _find(lines, lambda r: r["dir_basis"] == "VERB"
              and resolved.get(f"J {r['row']}") == r["dir"])
    row = _row(lines[i])
    tag = f"{row['slice']} {row['row']}"
    row["dir_basis"] = "VERB-OVER-RANGE"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{tag}: dir_basis VERB-OVER-RANGE, but section 2 now AGREES" in out
    assert "the recorded disagreement is stale" in out


def test_a_write_row_reclassed_off_write_turns_it_red(tmp_path, capsys) -> None:
    """A W row given a non-WRITE class: WRITE is exactly the no-read-half rows."""
    lines = _lines()
    i = _find(lines, lambda r: r["dir"] == "W")
    row = _row(lines[i])
    tag = f"{row['slice']} {row['row']}"
    row["class"] = "REFUSED"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert (f"{tag}: class 'REFUSED' with dir W: a row is WRITE exactly "
            f"when it has no read half") in out


def test_a_write_row_given_an_address_turns_it_red(tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "WRITE")
    row = _row(lines[i])
    tag = f"{row['slice']} {row['row']}"
    row["address"] = "https://www.linkedin.com/jobs/view/1234567890/"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert (f"{tag}: a WRITE row carries no address, so address must be "
            f"'-'") in out


def test_an_rw_row_with_one_phrase_part_turns_it_red(tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: r["dir"] == "R+W")
    row = _row(lines[i])
    tag = f"{row['slice']} {row['row']}"
    row["dir_phrase"] = row["dir_phrase"].split(" + ")[0].strip()
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{tag}: an R+W row names its read word AND its write word" in out


def test_an_r_row_given_dir_basis_resolved_turns_it_red(
        tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: r["dir"] == "R")
    row = _row(lines[i])
    tag = f"{row['slice']} {row['row']}"
    row["dir_basis"] = "RESOLVED"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{tag}: dir_basis RESOLVED is for an R+W row" in out


# ------------------------------------------------- the source column resolves


def test_a_missing_source_token_turns_it_red(tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: "::" in r["source"] and " row " not in r["source"])
    row = _row(lines[i])
    tag = f"{row['slice']} {row['row']}"
    path, _old_token = row["source"].split("::", 1)
    row["source"] = f"{path}::zznosuchtoken"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{tag}: source token zznosuchtoken is no longer spelled in" in out


def test_a_missing_source_file_turns_it_red(tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: True)
    row = _row(lines[i])
    tag = f"{row['slice']} {row['row']}"
    row["source"] = "scripts/zz_no_such_file_at_all.py"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert (f"{tag}: source file scripts/zz_no_such_file_at_all.py does not "
            f"exist") in out


def test_a_stale_census_row_citation_turns_it_red(tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines,
              lambda r: r["source"].startswith("_audit/_census/jobs.md row"))
    row = _row(lines[i])
    tag = f"{row['slice']} {row['row']}"
    row["source"] = "_audit/_census/jobs.md row 999"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{tag}: source row 999 is no longer a row of" in out


def test_a_prose_source_turns_it_red(tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: True)
    row = _row(lines[i])
    tag = f"{row['slice']} {row['row']}"
    row["source"] = "somewhere, as prose"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{tag}: source 'somewhere, as prose' is not '<path>" in out


# ------------------------------------------------------ boundary columns


def test_a_wrong_refusal_kind_turns_it_red(tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "REFUSED"
              and r["refusal"] == "NO-PATTERN")
    row = _row(lines[i])
    tag = f"{row['slice']} {row['row']}"
    row["refusal"] = "FORBIDDEN[/x]+NO-PATTERN"
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert (f"{tag}: recorded refusal 'FORBIDDEN[/x]+NO-PATTERN', the live "
            f"boundary raises 'NO-PATTERN'") in out


def test_a_wrong_also_driven_verdict_turns_it_red(tmp_path, capsys) -> None:
    lines = _lines()
    i = _find(lines, lambda r: r["dir"] in ("R", "R+W")
              and "=>True" in r["also_driven"])
    row = _row(lines[i])
    tag = f"{row['slice']} {row['row']}"
    row["also_driven"] = row["also_driven"].replace("=>True", "=>False", 1)
    lines[i] = _line(row)
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert f"{tag}: also_driven " in out
    assert "recorded False, the live boundary says True" in out


# ---------------------------------------------------- robustness and control


def test_a_missing_table_is_a_named_problem_not_a_traceback(
        tmp_path, capsys) -> None:
    code, out = _check(capsys, tmp_path / "jobs-directions.tsv")
    assert code == 1, out
    assert "does not exist" in out


def test_a_boundary_that_admits_everything_is_caught(monkeypatch, capsys) -> None:
    from linkedin_server import readonly

    monkeypatch.setattr(readonly, "is_read_url", lambda url: True)
    code, out = _check(capsys)
    assert code == 1, out
    assert "CONTROL:" in out


# ------------------------------------------------- the census_completion hook


def test_census_figures_on_the_real_table() -> None:
    """The pure split ``census_completion.report`` would print for jobs."""
    import census_completion as cc

    walk_rows = list(cc.walk())
    figures, problems = cjd.census_figures(walk_rows)
    assert not problems and figures is not None
    assert (figures["jobs_dir_r"] + figures["jobs_dir_w"]
            + figures["jobs_dir_rw"]) == figures["jobs_gap"]
    assert (figures["jobs_admitted"] + figures["jobs_refused"]
            + figures["jobs_no_address"] + figures["jobs_needs_session"]
            + figures["jobs_undetermined"]) == (
                figures["jobs_dir_r"] + figures["jobs_dir_rw"])


def test_census_figures_withholds_on_a_missing_row(tmp_path) -> None:
    """A table that drifts from the population yields NO figures -- WITHHELD,
    never zeroed, and the problem names the row.
    """
    import census_completion as cc

    walk_rows = list(cc.walk())
    lines = _lines()
    i = _find(lines, lambda r: True)
    gone = _row(lines[i])
    del lines[i]
    figures, problems = cjd.census_figures(walk_rows,
                                           path=_plant(tmp_path, lines))
    assert figures is None
    assert problems
    assert any(f"{gone['slice']} {gone['row']}" in p for p in problems)


def test_report_lines_renders_both_forms(tmp_path) -> None:
    """Both the figures form and the None+problems form render, and only the
    withheld form says WITHHELD.
    """
    import census_completion as cc

    walk_rows = list(cc.walk())
    figures, _no_problems = cjd.census_figures(walk_rows)
    ok_lines = cjd.report_lines(figures, [])
    assert ok_lines and all(isinstance(x, str) for x in ok_lines)
    assert not any("WITHHELD" in x for x in ok_lines)

    lines = _lines()
    i = _find(lines, lambda r: True)
    del lines[i]
    none_figures, problems = cjd.census_figures(walk_rows,
                                                path=_plant(tmp_path, lines))
    withheld_lines = cjd.report_lines(none_figures, problems)
    assert withheld_lines and all(isinstance(x, str) for x in withheld_lines)
    assert "WITHHELD" in "\n".join(withheld_lines)


# ------------------------------------------- the ruling-holds edge, 2026-09-23
#
# The bucket-3 table gained `check_read_addresses.ruling_problems` on master:
# no row blocked on nothing on a page a RULING holds. This table applies the
# same function to its read rows. Since the register of 2026-09-23 no hold
# binds a page, so on the real table the edge has nothing to fire on; these
# tests install a hold themselves, the way `tests/test_read_addresses.py`
# does, and show it firing on a jobs row.


def _jobs_page(row: dict[str, str]) -> str:
    import urllib.parse

    return urllib.parse.urlsplit(row["address"]).path


def _admitted_unheld_jobs_row(row: dict[str, str]) -> bool:
    import ruling_holds as rh

    return (row["class"] == "ADMITTED" and _jobs_page(row).endswith("/")
            and rh.surface_hold(_jobs_page(row)) is None)


def test_the_real_table_passes_the_ruling_edge() -> None:
    import check_read_addresses as cra

    rows, _ = cjd.load()
    assert cra.ruling_problems([r for r in rows if r["dir"] != "W"]) == []


def test_blocked_on_nothing_on_a_held_jobs_page_turns_it_red(
        tmp_path, capsys, monkeypatch) -> None:
    """A jobs row made READER on a page a planted ruling holds: red, and named."""
    import ruling_holds as rh

    lines = _lines()
    i = _find(lines, _admitted_unheld_jobs_row)
    row = _row(lines[i])
    row["gate"] = "READER"
    lines[i] = _line(row)
    monkeypatch.setitem(rh.ROW_HOLDS, "PLANTED-RULING", rh.Hold(
        status="STANDING", binds="surface", surface=_jobs_page(row)))
    code, out = _check(capsys, _plant(tmp_path, lines))
    assert code == 1, out
    assert (f"{row['slice']} {row['row']}: classed blocked on nothing (gate "
            f"READER), but its page {_jobs_page(row)} sits on "
            f"{_jobs_page(row)}, which PLANTED-RULING holds (STANDING)") in out


def test_census_figures_withholds_when_the_ruling_edge_fails(
        tmp_path, monkeypatch) -> None:
    """The pure hook census_completion calls applies the edge too: WITHHELD."""
    import census_completion as cc
    import ruling_holds as rh

    lines = _lines()
    i = _find(lines, _admitted_unheld_jobs_row)
    row = _row(lines[i])
    row["gate"] = "READER"
    lines[i] = _line(row)
    monkeypatch.setitem(rh.ROW_HOLDS, "PLANTED-RULING", rh.Hold(
        status="STANDING", binds="surface", surface=_jobs_page(row)))
    figures, problems = cjd.census_figures(list(cc.walk()),
                                           path=_plant(tmp_path, lines))
    assert figures is None
    assert any(p.startswith(f"{row['slice']} {row['row']}: classed blocked on "
                            f"nothing") for p in problems), problems
