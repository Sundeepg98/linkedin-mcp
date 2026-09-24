"""Every app-scope completeness candidate carries ONE verdict, and the census bears it out.

Lane Y2 (2026-09-24) gave each of the 121 app-scope candidates the completeness
probe raised a verdict -- ADMIT (a new GAP census row carries it), RECORDED (an
existing row carried the capability in words and gained the address or control
as evidence) or OUT (not a user capability). The verdicts live in the
annotations file's ``verdict`` columns; ``completeness_harvest.verdict_problems``
checks them against the committed table and the census, with no capture, so it
runs in CI. ``--check`` adds the half that needs the captures: the committed
table is exactly what ``--write`` would write over the adjudicated corpus.

**GREEN ON ITS OWN IS AMBIGUOUS**, so each way the layer can lie is planted into
a COPY and asserted red, naming the line:

  * an app-scope candidate with no verdict -- a regeneration that surfaced a
    route nobody adjudicated;
  * an ADMIT or RECORDED route that is still a candidate -- the census row the
    verdict names does not carry it, so the verdict says more than the tree;
  * a verdict naming a row no slice file writes;
  * a committed table edited by hand -- ``--check``'s fixed point.

And the corpus cutoff is shown keeping only what was captured before it, with
the rest printed as set aside rather than silently dropped.
"""
from __future__ import annotations

import os
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import completeness_harvest as ch  # noqa: E402

# NO MODULE-LEVEL UPPER-CASE CONSTANT BEYOND ``ROOT``: the impact gate couples
# every test file that names one, as a whole word (see tests/test_read_addresses.py).


def _copies(tmp_path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    table = tmp_path / "completeness-candidates.tsv"
    notes = tmp_path / "completeness-annotations.tsv"
    shutil.copyfile(ch.OUT_TSV, table)
    shutil.copyfile(ch.ANNOTATIONS, notes)
    return table, notes


def _rewrite_note(notes: pathlib.Path, kind: str, pattern: str, **cells: str) -> None:
    """Set cells of ONE annotation line, found by (kind, pattern); assert it landed."""
    lines = notes.read_text(encoding="ascii").splitlines()
    header = next(l.split("\t") for l in lines if l and not l.startswith("#"))
    hit = 0
    for i, line in enumerate(lines):
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        parts += [""] * (len(header) - len(parts))
        if parts[0] == kind and parts[1] == pattern:
            for name, value in cells.items():
                parts[header.index(name)] = value
            lines[i] = "\t".join(parts)
            hit += 1
    assert hit == 1, "the plant did not land on exactly one line: %r" % pattern
    notes.write_text("\n".join(lines) + "\n", encoding="ascii")


def _an_app_line(table: pathlib.Path) -> dict:
    lines = [l for l in ch._table_lines(table) if l["scope"] == "app"]
    assert lines, "the committed table holds no app-scope line to plant against"
    return lines[0]


def test_the_committed_verdict_layer_holds():
    problems = ch.verdict_problems()
    assert not problems, "the verdict layer does not hold:\n  " + "\n  ".join(problems)


def test_every_app_scope_line_left_in_the_table_is_an_out():
    notes = ch.load_annotations()
    for line in ch._table_lines(ch.OUT_TSV):
        if line["scope"] != "app":
            continue
        verdict = notes.get((line["kind"], line["pattern"]), {}).get("verdict")
        assert verdict == "OUT", (
            "%s %s is still a candidate with verdict %r" % (line["kind"], line["pattern"],
                                                            verdict))


def test_an_app_candidate_with_no_verdict_is_red(tmp_path):
    table, notes = _copies(tmp_path)
    line = _an_app_line(table)
    _rewrite_note(notes, line["kind"], line["pattern"], verdict="-")
    problems = ch.verdict_problems(table, notes)
    assert any(line["pattern"] in p and "no verdict" in p for p in problems), problems


def test_a_recorded_route_that_is_still_a_candidate_is_red(tmp_path):
    table, notes = _copies(tmp_path)
    line = _an_app_line(table)
    _rewrite_note(notes, line["kind"], line["pattern"], verdict="RECORDED",
                  verdict_rows="P N3")
    problems = ch.verdict_problems(table, notes)
    assert any(line["pattern"] in p and "still a candidate" in p for p in problems), problems


def test_a_verdict_naming_a_row_nobody_wrote_is_red(tmp_path):
    table, notes = _copies(tmp_path)
    admitted = [k for k, n in ch.load_annotations(notes).items()
                if n.get("verdict") in ("ADMIT", "RECORDED")]
    assert admitted, "no ADMIT or RECORDED verdict to plant against"
    kind, pattern = admitted[0]
    _rewrite_note(notes, kind, pattern, verdict_rows="J 9999")
    problems = ch.verdict_problems(table, notes)
    assert any(pattern in p and "J 9999" in p for p in problems), problems


def test_the_cutoff_keeps_what_was_captured_before_it_and_prints_the_rest(tmp_path):
    state = tmp_path / "_state"
    state.mkdir()
    early, late = state / "cap-early.html", state / "cap-late.html"
    early.write_text("<a href='/zzz-early/'>e</a>", encoding="utf-8")
    late.write_text("<a href='/zzz-late/'>l</a>", encoding="utf-8")
    os.utime(early, (1_700_000_000, 1_700_000_000))    # 2023-11-14
    os.utime(late, (1_800_000_000, 1_800_000_000))     # 2027-01-15
    everything, _aside = ch.select_corpus(tmp_path, worktrees=False, fixtures=False)
    assert {c.label for c in everything} == {"cap-early", "cap-late"}
    kept, aside = ch.select_corpus(tmp_path, worktrees=False, fixtures=False,
                                   captured_before="2026-01-01T00:00:00")
    assert [c.label for c in kept] == ["cap-early"]
    assert ["cap-late"] in list(aside.values()), aside


def test_check_convicts_a_table_edited_by_hand(tmp_path, capsys):
    result = ch._planted_result()
    notes = tmp_path / "completeness-annotations.tsv"
    rows = ["kind\tpattern\tscope\tslice\trw\tappears_to_be\tverdict\tverdict_rows"
            "\tverdict_basis"]
    for pattern in sorted(p.shape() for p in result["candidates"]):
        rows.append("address\t%s\t\t\t\tplanted\tOUT\t-\tplanted, not a capability"
                    % pattern)
    notes.write_text("\n".join(rows) + "\n", encoding="ascii")
    lines, _n = ch.tsv_lines(result, ch.load_annotations(notes))
    table = tmp_path / "completeness-candidates.tsv"
    table.write_text("\n".join(lines) + "\n", encoding="ascii")

    assert ch.check(result, table, notes) == 0, capsys.readouterr().out

    # THE EDIT TOUCHES ONE CELL AND NOT THE KEY. The first version of this edit
    # replaced a word that also sits in the planted PATTERN, so the key moved and
    # the check reported an ADD and a REMOVE instead of the CHANGE this test is
    # about -- red for the right reason, asserted in the wrong words.
    edited = ["\t".join(l.split("\t")[:-1] + ["edited by hand"])
              if l.startswith("address\t") else l for l in lines]
    assert edited != lines, "the hand edit did not land"
    table.write_text("\n".join(edited) + "\n", encoding="ascii")
    assert ch.check(result, table, notes) == 1
    out = capsys.readouterr().out
    assert "would CHANGE" in out and "NOT what --write would write" in out, out


def test_the_planted_capture_is_what_the_other_tests_think_it_is():
    """The fixed-point test above is only as good as its plant: it must yield a
    candidate, or every table it writes is empty and the edit changes nothing."""
    result = ch._planted_result()
    assert "/zzz-planted-surface/report" in {p.shape() for p in result["candidates"]}
