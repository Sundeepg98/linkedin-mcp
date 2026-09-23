"""The completeness probe must find what the census lacks, and ONLY that.

`scripts/completeness_harvest.py` harvests what LinkedIn drew on captured pages
and diffs the route shapes against every address the census records. Its whole
value is one discrimination, so both halves are planted here and both are
asserted:

  * a route the census has NEVER written must come out a CANDIDATE, and
  * a route a census capability row DOES carry must NOT.

**GREEN ON ITS OWN IS AMBIGUOUS.** A probe whose census parse silently returned
nothing would report every route as a candidate -- and the first assertion
would still pass. A probe that matched everything would pass the second. Only
the pair, run against the REAL census, discriminates. The shown-failing runs are
recorded in `_audit/2026-09-23-completeness-probe.md`: the census index emptied
turns the recorded route NEW and this file red, naming it.

Two further plants close the two ways this instrument can lie about itself:
its OWN output sits in the census directory and must never be read back as
census (a second run would otherwise find every candidate "recorded"), and a
route written into a census ROW must stop being a candidate (so the diff is
reading the census and not a constant).

No capture is needed: the planted page is written to a temporary directory, so
this runs in CI, where `_state/` does not exist.
"""
from __future__ import annotations

import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import completeness_harvest as ch  # noqa: E402

# NO MODULE-LEVEL UPPER-CASE CONSTANT BEYOND ``ROOT``: the impact gate couples
# every test file that names one, as a whole word (see tests/test_read_addresses.py).

planted_route = "/zzz-planted-surface/report"
recorded_route = "/analytics/profile-views"


def _verdicts(result: dict) -> dict[str, str]:
    return {p.text(): result["verdicts"][p].klass for p in result["patterns"]}


def _census_copy(tmp_path: pathlib.Path) -> pathlib.Path:
    dest = tmp_path / "census"
    shutil.copytree(ch.CENSUS, dest)
    return dest


def test_a_planted_route_is_a_candidate_and_a_recorded_one_is_not():
    result = ch._planted_result()
    klass = _verdicts(result)
    candidates = {p.text() for p in result["candidates"]}

    assert klass.get(planted_route) == "NEW", (
        "a route no census file has ever written came out %r, not NEW"
        % klass.get(planted_route))
    assert planted_route in candidates

    assert klass.get(recorded_route) == "ROW", (
        "%s is carried by census capability rows and came out %r -- the census "
        "parse or the matcher has stopped seeing it" % (recorded_route, klass.get(recorded_route)))
    assert recorded_route not in candidates
    rows = next(result["verdicts"][p].rows for p in result["patterns"]
                if p.text() == recorded_route)
    assert any(r.startswith("P ") for r in rows), (
        "the profile slice carries this address in a row and was not credited: %r" % rows)


def test_a_route_written_into_a_census_row_stops_being_a_candidate(tmp_path):
    census = _census_copy(tmp_path)
    profile = census / "profile.md"
    profile.write_text(
        profile.read_text(encoding="utf-8")
        + "\n| Z99 | planted capability | R | GAP | `%s/` |\n" % planted_route,
        encoding="utf-8")
    klass = _verdicts(ch._planted_result(census))
    assert klass.get(planted_route) == "ROW", (
        "a route written into a census row still came out %r" % klass.get(planted_route))


def test_its_own_output_is_never_read_back_as_census(tmp_path):
    census = _census_copy(tmp_path)
    for name in sorted(ch.OWN_FILES):
        (census / name).write_text(
            "kind\tpattern\naddress\t%s\n" % planted_route, encoding="ascii")
    klass = _verdicts(ch._planted_result(census))
    assert klass.get(planted_route) == "NEW", (
        "the probe read its own candidates file as census and called a planted "
        "route %r -- a second run would report zero candidates" % klass.get(planted_route))


def test_no_name_no_query_value_and_no_bundled_route_leaves():
    result = ch._planted_result()
    emitted = " ".join(p.text() for p in result["patterns"])
    emitted += " " + " ".join(k for s in result["patterns"].values() for k in s.keys)
    emitted += " " + " ".join(result["templates"])
    for needle in ("placeholder-member", "secret", "abc", "zzz-bundled-only",
                   "Placeholder", "Person", "Another"):
        assert needle not in emitted, "%r left the reducer" % needle
    assert "Follow <X>" in result["templates"]


def test_the_committed_candidates_table_is_ascii_and_name_free():
    table = ch.OUT_TSV
    if not table.exists():
        return
    from tests.test_no_committed_identity import hits_in

    text = table.read_text(encoding="ascii")
    assert not hits_in(text), "the committed candidates table matches an identity shape"
    for line in text.splitlines():
        if not line or line.startswith("#") or line.startswith("kind\t"):
            continue
        cells = line.split("\t")
        assert len(cells) == len(ch.TSV_COLUMNS), "malformed line: %r" % cells[1]
        pattern = cells[1]
        assert not re.search(r"\d{4,}", pattern), "an id-length digit run: %r" % pattern
        # EVERY COMMITTED CANDIDATE CARRIES A HAND READING. A regeneration that
        # surfaced a new candidate nobody has looked at must not be committed
        # as if it had been read: annotate it in completeness-annotations.tsv.
        assert cells[ch.TSV_COLUMNS.index("appears_to_be")] != "-", (
            "a committed candidate nobody has read: %r" % pattern)
        if cells[0] == "address":
            segs = [s for s in pattern.split("/") if s]
            for i, seg in enumerate(segs[1:], 1):
                if segs[i - 1].lower() in ("in", "company", "school", "groups"):
                    assert seg.startswith("<"), "a literal after /%s/: %r" % (
                        segs[i - 1], pattern)
