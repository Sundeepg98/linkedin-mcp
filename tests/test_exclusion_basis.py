"""The exclusion-basis table must be CHECKED, and the check must be able to FAIL.

`scripts/check_exclusion_basis.py` keeps `_audit/_census/exclusion-basis.tsv`
true: one line per census row outside the denominator (EXCLUDED-RULED and
MEASURED-ABSENT), each naming who ruled the row out and where that ruling is.
It exits 1 when an EXCLUDED-RULED row has NO TRACEABLE BASIS, when a row rests on
a ruling the operator has WITHDRAWN, and on any structural defect.

**THE CHECKER IS RED AT HEAD BY DESIGN, AND THIS FILE IS GREEN.** Whether a row
with no basis returns to GAP is the operator's decision, so nothing here asserts
the verdict is empty. What is asserted is that the verdict is CONSISTENT -- the
checker names exactly the rows the table classes as untraced or lifted -- and
that every other kind of defect is caught.

**GREEN ON ITS OWN IS AMBIGUOUS.** A checker broken into one that finds nothing
passes too. So each failure mode is planted twice: into a world built entirely
here (no census, no repo files -- a control fixture must be built, not found),
and, for the modes the real corpus can exhibit, into a COPY of the real table.
Every plant must turn the check red AND name the row it planted.

**THIS FILE GOES RED WHEN THE CENSUS MOVES A ROW INTO OR OUT OF AN OUT-OF-SCOPE
STATE, BY DESIGN.** A row that entered EXCLUDED-RULED has no traced basis until
somebody traces it; a row that left one leaves a line pointing at nothing.
`test_the_real_table_is_structurally_sound` names the row. The remedy is a line
in the table, never a relaxed check -- the tripwire `tests/test_read_addresses.py`
carries for bucket 3.
"""
from __future__ import annotations

import pathlib
import shutil
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_exclusion_basis as ceb  # noqa: E402

ER, MA = ceb.ER, ceb.MA


# ---------------------------------------------------------------------------
# A world built here, so every failure mode has a known-good baseline
# ---------------------------------------------------------------------------

def _row(slice_, rid, state, cls, basis, source):
    return {"slice": slice_, "row": rid, "state": state, "class": cls,
            "basis": basis, "source": source, "_line": "0"}


@pytest.fixture
def world(tmp_path):
    """(families, population, resolved text, rows, root), all green."""
    (tmp_path / "rulings.md").write_text(
        "The operator ruled that settings open one at a time.\n\n"
        "A wave filed these rows by name: R2b and R7c.\n",
        encoding="ascii")
    audit = tmp_path / ceb.LIFT_SOURCE[0]
    audit.parent.mkdir(parents=True)
    audit.write_text("> " + ceb.LIFT_SOURCE[1] + "\n", encoding="ascii")
    fams = {
        "FAM-OP": ceb.Family(
            "FAM-OP", "an operator family", "OPERATOR", "YES",
            (("rulings.md", "The operator ruled that settings"),),
            (r"\bTOKEN-OP\b",)),
        "FAM-AG": ceb.Family(
            "FAM-AG", "an agent family", "CODE", "NO",
            (("rulings.md", "The operator ruled that settings"),),
            (r"\bTOKEN-AG\b",),
            (("rulings.md", "A wave filed these rows by name"),)),
    }
    src = "rulings.md#The operator ruled that settings"
    lift = f"{ceb.LIFT_SOURCE[0]}#{ceb.LIFT_SOURCE[1]}"
    rows = [
        _row("N", "1", ER, "B", "family=FAM-OP; op=YES; scope=YES; note=x", src),
        _row("N", "2", ER, "B", "family=FAM-AG; op=NO; scope=EXTENDED; note=x", src),
        _row("N", "3", ER, "A", "ruling=FAM-OP; op=YES; note=x", src),
        _row("N", "4", MA, "M+", "measurement=a reading; evidence=RECORDED; note=x", src),
        _row("P", "R2b", ER, "B", "family=FAM-AG; op=NO; scope=YES; note=by roll-up", src),
        _row("N", "5", ER, "B", "family=FAM-AG; op=NO; scope=YES; via=2; note=x", src),
    ]
    pop = {("N", "1"): ER, ("N", "2"): ER, ("N", "3"): ER, ("N", "4"): MA,
           ("P", "R2b"): ER, ("N", "5"): ER}
    hay = {("N", "1"): "cites TOKEN-OP", ("N", "2"): "cites TOKEN-AG",
           ("N", "3"): "TOKEN-OP names it", ("N", "4"): "a reading",
           ("P", "R2b"): "same ruling", ("N", "5"): "same entry as 2"}
    ceb._FILE_CACHE.clear()
    return fams, pop, hay, rows, tmp_path, lift


def _verdict(world_):
    fams, pop, hay, rows, root, _lift = world_
    structural, untraced, lifted = ceb.row_problems(rows, hay, fams, root)
    return (ceb.coverage_problems(rows, pop) + ceb.family_problems(fams, root)
            + structural), untraced, lifted


def test_the_built_world_is_green(world):
    problems, untraced, lifted = _verdict(world)
    assert problems == [] and untraced == [] and lifted == []


def _set(rows, rid, **changes):
    for r in rows:
        if r["row"] == rid:
            r.update(changes)
            return
    raise AssertionError(rid)


@pytest.mark.parametrize("rid, change, needle", [
    ("1", {"class": "C", "basis": "why=NONE; cites=-; note=nothing"}, "NO TRACEABLE BASIS"),
    ("1", {"basis": "family=NOPE; op=YES; scope=YES; note=x"}, "unknown family"),
    ("2", {"basis": "family=FAM-AG; op=YES; scope=YES; note=x"}, "records op=NO"),
    ("2", {"basis": "family=FAM-AG; op=NO; scope=MAYBE; note=x"}, "scope 'MAYBE'"),
    ("1", {"basis": "family=FAM-AG; op=NO; scope=YES; note=x"}, "the table asserts a link"),
    ("3", {"basis": "ruling=FAM-AG; op=NO; note=x"}, "not an operator ruling"),
    ("1", {"source": "rulings.md#a sentence that was never written"}, "no longer contains"),
    ("1", {"source": "missing.md#anything"}, "does not exist"),
    ("1", {"source": "EXT:elsewhere.md#x"}, "no source this repository can resolve"),
    ("1", {"source": "/abs/rulings.md#x"}, "not a repo-relative path"),
    ("4", {"basis": "measurement=a reading; evidence=UNRECORDED; note=x"}, "contradicts evidence"),
    ("4", {"class": "B"}, "is not allowed for MEASURED-ABSENT"),
    ("5", {"basis": "family=FAM-AG; op=NO; scope=YES; via=9; note=x"}, "does not name 9"),
    ("2", {"basis": "family=FAM-AG; op=NO; scope=YES; lifted=READ-ONLY-NO-WRITES; note=x"},
     "carries lifted="),
])
def test_each_planted_defect_is_red_and_named(world, rid, change, needle):
    fams, pop, hay, rows, root, _lift = world
    _set(rows, rid, **change)
    problems, untraced, lifted = _verdict(world)
    hits = [p for p in problems + untraced + lifted if needle in p]
    assert hits, f"planted {change} on {rid}; nothing said {needle!r}: {problems + untraced}"
    assert all(f" {rid}:" in h for h in hits), hits


def test_a_roll_up_links_only_the_rows_it_names(world, tmp_path):
    (tmp_path / "rulings.md").write_text(
        "The operator ruled that settings open one at a time.\n\n"
        "A wave filed these rows by name: R7c only.\n", encoding="ascii")
    ceb._FILE_CACHE.clear()
    problems, _u, _l = _verdict(world)
    assert any("P R2b:" in p and "asserts a link" in p for p in problems), problems


@pytest.mark.parametrize("mutate, needle", [
    (lambda rows, pop: rows.pop(0), "has NO LINE"),
    (lambda rows, pop: pop.pop(("N", "2")), "is not out of scope in the census"),
    (lambda rows, pop: rows.append(dict(rows[0])), "2 lines for one row"),
    (lambda rows, pop: pop.__setitem__(("N", "1"), MA), "census says MEASURED-ABSENT"),
])
def test_coverage_drift_is_red_and_named(world, mutate, needle):
    fams, pop, hay, rows, root, _lift = world
    mutate(rows, pop)
    problems = ceb.coverage_problems(rows, pop)
    assert any(needle in p for p in problems), problems


def test_a_lifted_row_is_its_own_verdict(world):
    fams, pop, hay, rows, root, lift = world
    src = "rulings.md#The operator ruled that settings"
    _set(rows, "2", **{"class": "B-lifted", "source": f"{src} ; {lift}",
                       "basis": "family=FAM-AG; op=NO; scope=YES; "
                                "lifted=APPLY-CONNECT-INMAIL-CUT; remaining=FAM-OP; note=x"})
    problems, untraced, lifted = _verdict(world)
    assert problems == [] and untraced == []
    assert lifted == ["N 2: EXCLUDED-RULED on a LIFTED ruling "
                      "(APPLY-CONNECT-INMAIL-CUT); still held by FAM-OP"]


@pytest.mark.parametrize("basis, source_has_lift, needle", [
    ("family=FAM-AG; op=NO; scope=YES; lifted=SOMETHING-ELSE; note=x", True, "each part must be one of"),
    ("family=FAM-AG; op=NO; scope=YES; lifted=READ-ONLY-NO-WRITES; note=x", False, "must cite the tracked record"),
    ("family=FAM-AG; op=NO; scope=YES; lifted=READ-ONLY-NO-WRITES; remaining=NOPE; note=x", True,
     "is not a registered family"),
])
def test_a_malformed_lifted_row_is_red_and_named(world, basis, source_has_lift, needle):
    fams, pop, hay, rows, root, lift = world
    src = "rulings.md#The operator ruled that settings"
    _set(rows, "2", **{"class": "B-lifted", "basis": basis,
                       "source": f"{src} ; {lift}" if source_has_lift else src})
    problems, _u, _l = _verdict(world)
    assert any(needle in p and "N 2:" in p for p in problems), problems


def test_a_family_whose_own_source_rots_is_red(world, tmp_path):
    fams, pop, hay, rows, root, _lift = world
    (tmp_path / "rulings.md").write_text("rewritten entirely\n", encoding="ascii")
    ceb._FILE_CACHE.clear()
    problems = ceb.family_problems(fams, root)
    assert any(p.startswith("family FAM-OP:") and "no longer contains" in p for p in problems)


@pytest.mark.parametrize("content, needle", [
    (None, "does not exist"),
    ("slice\trow\n", "header must be exactly"),
    ("\t".join(ceb.COLUMNS) + "\nN\t1\tEXCLUDED-RULED\tB\tnote=caf\u00e9\tx\n", "not ASCII"),
    ("\t".join(ceb.COLUMNS) + "\nN\t1\tEXCLUDED-RULED\n", "3 fields"),
])
def test_an_unreadable_table_is_a_named_problem(tmp_path, content, needle):
    path = tmp_path / "t.tsv"
    if content is not None:
        path.write_bytes(content.encode("utf-8"))
    _rows, problems = ceb.load(path)
    assert any(needle in p for p in problems), problems


# ---------------------------------------------------------------------------
# The real table, against the real census through the shipped parse
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real():
    rows, load_problems = ceb.load()
    pop, hay, pop_problems = ceb.population()
    return rows, load_problems, pop, hay, pop_problems


def test_the_real_table_is_structurally_sound(real):
    rows, load_problems, pop, hay, pop_problems = real
    ceb._FILE_CACHE.clear()
    assert load_problems == [] and pop_problems == []
    assert ceb.coverage_problems(rows, pop) == []
    assert ceb.family_problems(ceb.FAMILIES, ceb.ROOT) == []
    structural, untraced, lifted = ceb.row_problems(rows, hay, ceb.FAMILIES, ceb.ROOT)
    assert structural == []
    # THE VERDICT IS CONSISTENT WITH THE TABLE -- never asserted empty.
    c_rows = {f"{r['slice']} {r['row']}" for r in rows if r["state"] == ER and r["class"] == "C"}
    l_rows = {f"{r['slice']} {r['row']}" for r in rows
              if r["state"] == ER and r["class"].endswith("-lifted")}
    assert {u.split(":")[0] for u in untraced} == c_rows
    assert {li.split(":")[0] for li in lifted} == l_rows


def test_every_family_in_the_registry_is_used_or_says_why(real):
    rows = real[0]
    used = set()
    for r in rows:
        b = ceb.parse_basis(r["basis"])
        used.update(x for x in (b.get("family") or b.get("ruling") or "").split("+") if x)
    unused = sorted(set(ceb.FAMILIES) - used)
    # An unused family is a registered ruling nothing is filed under: a
    # vocabulary entry that can no longer fail. None is expected today.
    assert unused == [], unused


@pytest.mark.parametrize("row, field, old, new, needle", [
    ("P D5", "basis", "family=EDIT-FAMILY; op=CONTRARY",
     "family=R9-OUTREACH-AUTOMATION; op=YES", "cites R9-OUTREACH-AUTOMATION"),
    ("P D5", "basis", "op=CONTRARY", "op=YES", "records op=CONTRARY"),
    ("N 119", "source", '"endorse_or_recommend": (', '"endorse_or_admire": (', "no longer contains"),
])
def test_a_plant_in_a_copy_of_the_real_table_is_red_and_named(real, tmp_path, row, field, old, new, needle):
    rows = [dict(r) for r in real[0]]
    _pop, hay = real[2], real[3]
    target = next(r for r in rows if f"{r['slice']} {r['row']}" == row)
    assert old in target[field], (row, field)
    target[field] = target[field].replace(old, new, 1)
    ceb._FILE_CACHE.clear()
    structural, _u, _l = ceb.row_problems(rows, hay, ceb.FAMILIES, ceb.ROOT)
    hits = [p for p in structural if needle in p]
    assert hits and all(p.startswith(f"{row}:") for p in hits), structural


def test_main_on_a_copy_missing_a_line_is_red_and_names_it(tmp_path, capsys):
    copy = tmp_path / "exclusion-basis.tsv"
    lines = ceb.TABLE.read_text(encoding="ascii").splitlines(keepends=True)
    kept = [ln for ln in lines if not ln.startswith("N\t23\t")]
    assert len(kept) == len(lines) - 1
    copy.write_text("".join(kept), encoding="ascii")
    assert ceb.main(["--table", str(copy)]) == 1
    out = capsys.readouterr().out
    assert "N 23: is EXCLUDED-RULED in the census and has NO LINE" in out


def test_main_is_red_exactly_while_the_table_holds_an_open_question(real, capsys):
    rows = real[0]
    open_q = [r for r in rows if r["state"] == ER
              and (r["class"] == "C" or r["class"].endswith("-lifted"))]
    rc = ceb.main([])
    out = capsys.readouterr().out
    assert rc == (1 if open_q else 0), out[-2000:]
    for r in open_q:
        assert f"{r['slice']} {r['row']}: EXCLUDED-RULED" in out
