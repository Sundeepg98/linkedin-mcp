"""The write-class table must be CHECKED, and the check must be able to FAIL.

``scripts/check_write_classes.py`` keeps ``_audit/_census/write-classes.tsv``
true: every write-direction still-GAP row has exactly one line, every class is
DERIVED from the line's act through a closed vocabulary, every line cites its
own census row, every R1 / R2 line cites the passage that defines its class,
every R2 line -- outward, cut until the ruling relayed at 18:15 on
2026-09-23 -- carries four build-ready columns that no other line may carry,
and every citation still resolves. A check that runs only when somebody
remembers to run it has already stopped working, so it runs here.

**GREEN ON ITS OWN IS AMBIGUOUS.** It passes when the table is right AND when
the checker has been broken into something that finds nothing. So every
planted defect below goes into a COPY of the real table -- never the committed
file -- and each must turn the check red AND name the row it planted. The
plant that matters most is the CONSISTENT one: a line whose act and class
agree with each other and are both wrong is invisible to the vocabulary check,
and is caught only because R1 must cite the passage that defines R1.

**THIS FILE GOES RED WHEN THE CENSUS MOVES A WRITE-DIRECTION GAP ROW, BY
DESIGN.** Bank a write row, re-rule it or correct its direction cell, and
``test_green_on_the_real_table`` fails naming the row. The remedy is to update
the table -- remove the line of a row that left, class the row that entered --
never to relax the check.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import check_write_classes as cwc  # noqa: E402

# NO MODULE-LEVEL UPPER-CASE CONSTANT BEYOND ``ROOT``, on the impact gate's
# rule: a test file that NAMES an upper-case constant another staged file
# defines is coupled to it, and a generic name couples half the suite.


def _lines() -> list[str]:
    return cwc.WRITE_CLASS_TABLE.read_text(encoding="ascii").splitlines()


def _data_indexes(lines: list[str]) -> list[int]:
    header = "\t".join(cwc.WRITE_CLASS_COLUMNS)
    return [i for i, ln in enumerate(lines)
            if ln and not ln.startswith("#") and ln != header]


def _row(line: str) -> dict[str, str]:
    return dict(zip(cwc.WRITE_CLASS_COLUMNS, line.split("\t")))


def _line(row: dict[str, str]) -> str:
    return "\t".join(row[c] for c in cwc.WRITE_CLASS_COLUMNS)


def _find(lines: list[str], predicate) -> int:
    """The FIRST data line satisfying ``predicate``, found at runtime so a
    control does not rot the day the row it named is banked. It ASSERTS it
    found one, so a table with no such row fails loudly."""
    for i in _data_indexes(lines):
        if predicate(_row(lines[i])):
            return i
    raise AssertionError("the real table has no row this control can plant on")


def _plant(tmp_path: pathlib.Path, lines: list[str], *, raw: bytes = b"") -> pathlib.Path:
    copy = tmp_path / "write-classes.tsv"
    if raw:
        copy.write_bytes(raw)
        return copy
    assert lines != _lines(), "the plant changed nothing: the control is broken"
    copy.write_text("\n".join(lines) + "\n", encoding="ascii")
    return copy


def _problems(table: pathlib.Path, performable=None) -> list[str]:
    _rows, problems = cwc.check(table, performable=performable)
    return problems


def _red_naming(problems: list[str], key: str, needle: str) -> None:
    hits = [p for p in problems if p.startswith(key + ":") and needle in p]
    assert hits, (f"the plant on {key} was not convicted with {needle!r}; "
                  f"the check said: {problems}")


# ---------------------------------------------------------------------------
# GREEN, and the population it is green over
# ---------------------------------------------------------------------------


def test_green_on_the_real_table():
    rows, problems = cwc.check()
    assert problems == [], problems
    assert len(rows) >= 100


def test_the_table_is_the_population_plus_what_was_built():
    rows, _ = cwc.load()
    index = cwc.census_index()
    pop = cwc.population(index)
    keys = {r["key"] for r in rows}
    built = {r["key"] for r in rows if r["disposition"].startswith("built:")}
    assert keys == pop | built
    assert not (pop & built), "a built row is still write-direction GAP"


def test_the_walk_is_not_vacuous():
    index = cwc.census_index()
    pop = cwc.population(index)
    assert cwc.control_problems(index) == []
    for key in cwc.WRITE_CLASS_KNOWN_IN:
        assert key in pop
    for key in cwc.WRITE_CLASS_KNOWN_OUT:
        assert key in index and key not in pop


def test_the_split_is_the_one_the_lane_report_quotes():
    """Pinned so a moved line is a visible decision. The arithmetic: 151 rows
    at b0d3ab8 = 11 R1 + 23 R2 + 117 R3; the R1 disposition is re-counted from
    the table every run, so a build moves it without moving this.

    325 SINCE LANE R'S MERGE, 2026-09-24 (`_audit/2026-09-23-exclusion-returns.md`,
    Integration 2026-09-24): lane R returned 173 write-direction rows to GAP,
    and rulings batch 3 made `N 183` a write row; each of the 174 was classed by
    its act -- 5 R1 (`N 34`, `N 36`, `N 50`, `N 62`, `P I2`, all queued), 12 R2
    (the sends and connects ruling (b) permits), 157 R3.
    151 + 174 = 325 = 16 R1 + 35 R2 + 274 R3.

    339 AFTER LANE Y2'S COMPLETENESS ADMISSION, measured on the tree that
    merged it with lane R (`_audit/2026-09-24-lane-y2-admission.md`,
    Integration 2026-09-24): fourteen admitted write rows, one R2 (`M C94`,
    sending a post to one person) and thirteen R3 (`P S2`, `S4`, `S6`-`S10`;
    `M M52`, `C97`, `C100`; `N 196`, `198`, `200`). R1 is untouched: no
    admitted row's act is one of the first round's own verbs.
    325 + 14 = 339 = 16 R1 + 36 R2 + 287 R3."""
    rows, _ = cwc.load()
    split = cwc.split(rows)
    assert (split["R1"], split["R2"], split["R3"]) == (16, 36, 287)
    assert split["R1:built"] + split["R1:queued"] == split["R1"]


# ---------------------------------------------------------------------------
# SHOWN FAILING -- one plant per defect class, each into a COPY
# ---------------------------------------------------------------------------


def test_a_range_id_citation_is_parsed_and_must_still_name_a_row(tmp_path):
    """``profile.md row O6-O20`` is a census row with a RANGE id. The self-row
    form admits it, and the admission is not a hole: a range that names no row
    is convicted by the same resolver as any other id, not waved through and
    not misread as an unparseable citation."""
    lines = _lines()
    i = _find(lines, lambda r: r["key"].startswith("P "))
    row = _row(lines[i])
    row["sources"] = row["sources"] + " ; _audit/_census/profile.md row O6-O99"
    lines[i] = _line(row)
    problems = _problems(_plant(tmp_path, lines))
    _red_naming(problems, row["key"], "row O6-O99 is no longer a row of")
    assert not [p for p in problems if "O6-O99" in p and "is neither a path" in p]


def test_red_on_a_missing_row(tmp_path):
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "R3")
    key = _row(lines[i])["key"]
    del lines[i]
    _red_naming(_problems(_plant(tmp_path, lines)), key, "NO line")


def test_red_on_a_duplicate(tmp_path):
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "R2")
    lines.insert(i + 1, lines[i])
    _red_naming(_problems(_plant(tmp_path, lines)), _row(lines[i])["key"],
                "lines, want exactly one")


def test_red_on_a_row_that_is_not_a_write_gap_row(tmp_path):
    """``N 1`` is a COVERED-UNFIRED write -- not in the population."""
    lines = _lines()
    i = _find(lines, lambda r: r["key"].startswith("N "))
    row = _row(lines[i])
    row["key"] = "N 1"
    lines.append(_line(row))
    _red_naming(_problems(_plant(tmp_path, lines)), "N 1",
                "not a write-direction GAP row today")


def test_red_on_a_class_that_disagrees_with_its_act(tmp_path):
    lines = _lines()
    i = _find(lines, lambda r: r["act"] == "subscribe")
    row = _row(lines[i])
    row["class"] = "R1"
    row["disposition"] = "queued:ANY-BLOCKER"
    lines[i] = _line(row)
    _red_naming(_problems(_plant(tmp_path, lines)), row["key"],
                "is class R3")


def test_red_on_a_consistent_widening_that_cites_no_authority(tmp_path):
    """THE PLANT THAT MATTERS. Act and class are rewritten TOGETHER, so the
    vocabulary check is satisfied -- ``subscribe`` becomes ``follow`` and R3
    becomes R1. Only the demand that R1 cite the passage defining R1 can
    convict it."""
    lines = _lines()
    i = _find(lines, lambda r: r["act"] == "subscribe")
    row = _row(lines[i])
    row["act"], row["class"] = "follow", "R1"
    row["disposition"] = "queued:ANY-BLOCKER"
    lines[i] = _line(row)
    _red_naming(_problems(_plant(tmp_path, lines)), row["key"],
                "must cite the passage that defines it")


def test_red_on_an_act_off_the_vocabulary(tmp_path):
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "R3")
    row = _row(lines[i])
    row["act"] = "tidy-up"
    lines[i] = _line(row)
    _red_naming(_problems(_plant(tmp_path, lines)), row["key"],
                "off the closed vocabulary")


def test_red_on_a_drifted_capability(tmp_path):
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "R1")
    row = _row(lines[i])
    row["capability"] = row["capability"] + " and something else"
    lines[i] = _line(row)
    _red_naming(_problems(_plant(tmp_path, lines)), row["key"],
                "capability text no longer matches")


def test_red_on_a_missing_self_citation(tmp_path):
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "R2")
    row = _row(lines[i])
    row["sources"] = " ; ".join(c for c in cwc.citations(row)
                                if not c.startswith("_audit/_census/")
                                or "::" in c)
    lines[i] = _line(row)
    _red_naming(_problems(_plant(tmp_path, lines)), row["key"],
                "does not cite its own census row")


def test_red_on_a_phrase_that_no_longer_resolves(tmp_path):
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "R1")
    row = _row(lines[i])
    row["sources"] += (" ; linkedin_server/writes.py::a sentence this module "
                       "has never contained")
    lines[i] = _line(row)
    _red_naming(_problems(_plant(tmp_path, lines)), row["key"],
                "phrase does not resolve")


def test_red_on_an_unregistered_ruling(tmp_path):
    lines = _lines()
    i = _find(lines, lambda r: "RULING:" in r["sources"])
    row = _row(lines[i])
    row["sources"] += " ; RULING:NO-SUCH-RULING-EXISTS"
    lines[i] = _line(row)
    _red_naming(_problems(_plant(tmp_path, lines)), row["key"],
                "is not registered")


def test_red_on_a_superseded_ruling(tmp_path):
    """A superseded ruling keeps its register row, so its id RESOLVES -- the
    unregistered-id rule cannot see it. The id is read off the register at
    runtime, so this control does not rot the day one ruling is re-ruled."""
    superseded = sorted(cwc.superseded_rulings())
    assert superseded, "the register holds no SUPERSEDED ruling to plant"
    lines = _lines()
    i = _find(lines, lambda r: "RULING:" in r["sources"])
    row = _row(lines[i])
    row["sources"] += f" ; RULING:{superseded[0]}"
    lines[i] = _line(row)
    _red_naming(_problems(_plant(tmp_path, lines)), row["key"],
                "is SUPERSEDED")


def test_red_on_a_build_naming_an_action_that_cannot_perform(tmp_path):
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "R1")
    row = _row(lines[i])
    row["disposition"] = "built:a_write_nobody_built"
    lines[i] = _line(row)
    problems = _problems(_plant(tmp_path, lines),
                         performable=frozenset({"save_job"}))
    _red_naming(problems, row["key"], "is not in writes.PERFORMABLE")
    _red_naming(problems, row["key"], "a build that did not move its row")


def test_red_on_a_classify_only_class_carrying_a_build(tmp_path):
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "R2")
    row = _row(lines[i])
    row["disposition"] = "queued:SOMETHING"
    lines[i] = _line(row)
    _red_naming(_problems(_plant(tmp_path, lines)), row["key"],
                "is classify-only in this lane")


def test_red_on_an_r2_line_without_build_ready_detail(tmp_path):
    """The relayed 18:15 ruling asks for BUILD-READY detail on every R2 line.
    A line that drops one of the four columns back to '-' must go red."""
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "R2")
    row = _row(lines[i])
    row["r2_live_proof"] = "-"
    lines[i] = _line(row)
    _red_naming(_problems(_plant(tmp_path, lines)), row["key"],
                "R2 needs build-ready r2_live_proof")


def test_red_on_build_ready_detail_on_a_row_nobody_cleared(tmp_path):
    """The other half: detail must not quietly attach to an R3 row, where it
    would read as a build plan for an act nobody has ruled on."""
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "R3")
    row = _row(lines[i])
    row["r2_action"] = "Press the control and send the thing"
    lines[i] = _line(row)
    _red_naming(_problems(_plant(tmp_path, lines)), row["key"],
                "r2_action is for R2 lines only")


def test_red_on_an_r2_target_outside_the_four_kinds(tmp_path):
    lines = _lines()
    i = _find(lines, lambda r: r["class"] == "R2")
    row = _row(lines[i])
    row["r2_target"] = "company -- an organisation Page"
    lines[i] = _line(row)
    _red_naming(_problems(_plant(tmp_path, lines)), row["key"],
                "r2_target must open with one of")


def test_red_on_non_ascii(tmp_path):
    # The em dash is built from its code point so this file stays ASCII.
    raw = "\n".join(_lines()).encode("ascii") + (chr(0x2014) + "\n").encode("utf-8")
    problems = _problems(_plant(tmp_path, [], raw=raw))
    assert any("not ASCII" in p for p in problems), problems


def test_red_on_a_missing_table(tmp_path):
    problems = _problems(tmp_path / "absent.tsv")
    assert any("does not exist" in p for p in problems), problems


@pytest.mark.parametrize("cls", ["R1", "R2"])
def test_every_defining_passage_resolves_on_its_own(cls):
    """The two passages the classes rest on, resolved directly -- so a reworded
    source is caught by name even before any row cites it."""
    row = {"key": "X 0", "sources": cwc.WRITE_CLASS_DEFINING[cls]}
    assert cwc.source_problems([row]) == []
