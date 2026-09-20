"""A COVERED census row goes RED when the artifact that covers it leaves.

THE SIBLING OF ``test_a_retired_row_rests_on_a_live_assertion.py``, and the
other half of the same law. That file binds an EXCLUDED-RULED row to the rule
that excluded it. This one binds a COVERED row to the CODE that covers it.

## THE DISEASE THIS TREATS, measured twice in one morning

Two rows in this census read GAP while the code that provides them was already
shipped and tested:

* ``J 10`` -- ``linkedin_server/jobfilter.py`` says in its OWN FIRST PARAGRAPH
  that both halves of its blocker are built *"and the row is still GAP, because
  nothing joined them"*.
* ``K10`` -- read ``no tool, no reason`` while ``dom.py`` had been setting
  ``verified_job`` and ``server.py`` passing it to a tool.

Banking them fixes the count once. **It does not stop the reverse defect**, which
is a row left claiming coverage after somebody deletes the reader. A census that
can drift in one direction can drift in the other, and only the first direction
has ever been looked for here.

## WHY THE ``K10`` CASE NEEDED AN ASSERTION AND NOT A NOTE

``dom.read_job_insight_panels`` returns a dict containing ``verified_job``.
``server.py`` assigns **the whole dict** to ``linkedin_job_detail``'s
``insights``. So the field reaches a caller -- and

    grep -n "verified_job" linkedin_server/server.py

**RETURNS NOTHING**, because a field that travels inside a dict is invisible to
a search for its name. That grep was run during the wave that banked the row and
read, for a minute, as a refutation.

**A PASSTHROUGH IS EXACTLY THE COUPLING A HUMAN CHECK CANNOT SEE**, which makes
it the one most worth asserting: the two ends can be separated by an edit at
either end and nothing in between would notice.

## WHAT IS DELIBERATELY NOT ASSERTED

* **Not that the row's state is CORRECT.** No test can judge that.
* **Not that the capability WORKS.** These rows are COVERED-UNFIRED precisely
  because nothing has seen them return a payload live, and this file does not
  pretend otherwise -- it asserts the artifact exists, never that it ran.
* **Not that every COVERED row is listed here.** The table holds rows whose
  coverage this repository has written down against a named artifact.

SHOWN FAILING before admission, each against a COPY or a monkeypatch so no
contended file was edited. Recorded in ``_audit/2026-09-19-read-tail.md``.
"""

from __future__ import annotations

import ast
import pathlib
import re

import pytest

_ROOT = pathlib.Path(__file__).resolve().parent.parent
_PKG = _ROOT / "linkedin_server"
_CENSUS = _ROOT / "_audit" / "_census"

#: A census row in any slice: ``| 10 | ...`` or ``| K10 | ...``.
_ROW = re.compile(r"^\|\s*([A-Za-z]{0,2}\s?\d+[a-z]?)\s*\|[^|]*\|(?:[^|]*\|)?\s*\*{0,2}([A-Z-]+)\*{0,2}\s*\|")

#: (slice file, row id) -> (required state, why in one line).
COVERED_ROWS: dict[tuple[str, str], tuple[str, str]] = {
    ("jobs.md", "10"): (
        "COVERED-UNFIRED",
        "the company filter: a resolver, a tool parameter and the f_C key",
    ),
    ("profile.md", "K10"): (
        "COVERED-UNFIRED",
        "the job-posting verification badge, as a boolean inside insights",
    ),
    ("jobs.md", "151"): (
        "COVERED-UNFIRED",
        "multi-location search: a plan, a merge, and one url per place",
    ),
}


def _states(slice_name: str) -> dict[str, str]:
    """Every row id in one census slice and the state cell it carries."""
    out: dict[str, str] = {}
    path = _CENSUS / slice_name
    for line in path.read_text(encoding="utf-8").splitlines():
        found = _ROW.match(line)
        if found is not None:
            out.setdefault(found.group(1).replace(" ", ""), found.group(2))
    return out


def _source(name: str) -> str:
    return (_PKG / name).read_text(encoding="utf-8")


def test_both_census_slices_are_readable_at_all() -> None:
    """The control. A guard that reads an empty corpus refuses nothing."""
    jobs, profile = _states("jobs.md"), _states("profile.md")
    assert len(jobs) >= 100, f"only {len(jobs)} rows parsed out of jobs.md"
    assert len(profile) >= 100, f"only {len(profile)} rows parsed out of profile.md"
    assert "10" in jobs and "K10" in profile, "the two banked rows are not being read"


@pytest.mark.parametrize("key", sorted(COVERED_ROWS))
def test_the_row_still_claims_the_coverage_it_was_banked_with(key: tuple[str, str]) -> None:
    """A banked row silently reverting to GAP fails here, naming the row."""
    slice_name, row = key
    required, why = COVERED_ROWS[key]
    states = _states(slice_name)
    assert row in states, (
        f"census row {row} has left {slice_name}. It was banked as {required} "
        f"because {why}. Re-numbering is fine; vanishing is not."
    )
    assert states[row] == required, (
        f"census row {row} in {slice_name} reads {states[row]!r}, not "
        f"{required!r}. It was banked because {why}. If the coverage claim has "
        "been withdrawn, remove it from COVERED_ROWS here with the reason -- a "
        "row and a table that disagree is how a count starts lying."
    )


def test_the_company_filter_chain_is_still_whole() -> None:
    """``J 10``'s coverage: resolver -> verdict -> tool parameter -> query key.

    Asserted as a CHAIN rather than as four independent names, because the row
    is covered only if every link holds. Any one of them removed leaves a
    census row claiming a capability nobody provides.
    """
    shape_src, server_src, filter_src = (
        _source("shape.py"), _source("server.py"), _source("jobfilter.py")
    )
    assert "def company_id_from_insight_cards" in shape_src, (
        "shape.company_id_from_insight_cards is gone; census row J 10 claims "
        "COVERED and the resolver behind it no longer exists"
    )
    assert "company_id_from_insight_cards" in server_src, (
        "server.py no longer consumes the resolver; J 10's chain is broken at "
        "the verdict step"
    )
    assert "company_id" in server_src, "the tool parameter J 10 rests on is gone"
    assert 'COMPANY_FILTER_KEY = "f_C"' in filter_src, (
        "jobfilter.COMPANY_FILTER_KEY is no longer f_C; J 10 claims a company "
        "filter and the query key it is built from has changed"
    )


def test_the_multi_location_chain_is_still_whole() -> None:
    """``J 151``'s coverage, and the link that is NOT a name anyone would grep.

    The chain is plan -> merge -> tool -> url. Three of the four links are
    ordinary names. The fourth is the one worth asserting: the capability is
    only safe because EVERY location reaches a url through ONE function that
    takes ONE place, so the two spellings measured wrong on 2026-09-05 -- a
    comma-joined pair, and ``location`` appended twice -- are unreachable by
    construction rather than by care. A fan-out that grew a second url builder
    would break nothing a name check can see, and would break exactly that.

    ``tests/test_job_search_multiple_locations.py`` asserts the BEHAVIOUR
    against a driven page. This asserts the row's claim against the tree, which
    is the direction that survives somebody deleting the behaviour test.
    """
    server_src, filter_src = _source("server.py"), _source("jobfilter.py")

    # NAMES MATCHED AS AST DEFINITIONS, NOT AS SUBSTRINGS, and that is a
    # correction this guard earned on its first mutation run rather than a
    # style preference. Written as ``"def merge_location_reads" in filter_src``
    # it survived the function being RENAMED to
    # ``merge_location_reads_renamed`` -- the old name is a PREFIX of the new
    # one, so the substring was still there while ``server.py``'s call site
    # pointed at nothing. A rename is the likeliest way this link breaks and it
    # was the one shape the check could not see.
    defined = {
        node.name
        for node in ast.walk(ast.parse(filter_src))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "locations_plan" in defined, (
        "jobfilter.locations_plan is gone; census row J 151 claims COVERED "
        "and the verdict that decides which places a call visits no longer "
        "exists"
    )
    assert "merge_location_reads" in defined, (
        "jobfilter.merge_location_reads is gone; J 151's chain is broken at "
        "the merge step and a fan-out would return only its last place"
    )
    assert "locations_plan(" in server_src, (
        "server.py no longer consults the plan; J 151's chain is broken "
        "between the tool and the verdict"
    )
    assert "locations: str" in server_src, (
        "the tool parameter J 151 rests on is gone"
    )

    # THE URL FUNNEL. One builder, and the location it appends is the argument
    # it was given -- not a list, not a join.
    tree = ast.parse(server_src)
    builders = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_search_url"
    ]
    assert len(builders) == 1, (
        "expected exactly one _search_url; found %d. Every location must "
        "reach a url through ONE function taking ONE place, or the spellings "
        "measured wrong on 2026-09-05 become reachable again" % len(builders)
    )
    body = ast.unparse(builders[0])
    assert body.count("'location'") + body.count('"location"') == 1, (
        "the url builder names the location key more than once, which is the "
        "shape LinkedIn was measured to strip down to the last city: %s" % body
    )


def test_the_verified_badge_passthrough_is_still_whole() -> None:
    """``K10``'s coverage, and the one a grep provably cannot check.

    ``verified_job`` is set inside ``dom.read_job_insight_panels``'s returned
    dict and reaches a caller only because ``server.py`` assigns THAT WHOLE
    DICT to ``insights``. Searching ``server.py`` for the field name returns
    nothing. Both ends are asserted here, and the join between them.
    """
    dom_src, server_src = _source("dom.py"), _source("server.py")

    assert '"verified_job"' in dom_src, (
        "dom.py no longer produces verified_job; census row K10 claims "
        "COVERED on a field that is gone"
    )

    # The FAR END: the function must still be the thing assigned to insights.
    tree = ast.parse(server_src)
    joined = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        target = ast.unparse(node.targets[0]) if node.targets else ""
        # ``ast.unparse`` renders string subscripts with SINGLE quotes, so a
        # check written as ``["insights"]`` never matches and the guard fails
        # for a reason that has nothing to do with the code under test. That
        # was this file's own first-run bug, and it is the reason the
        # shown-failing demo below plants a real mutation rather than trusting
        # a green.
        if not (target.endswith("['insights']") or target.endswith('["insights"]')):
            continue
        if "read_job_insight_panels" in ast.unparse(node.value):
            joined = True
    assert joined, (
        "server.py no longer assigns dom.read_job_insight_panels to an "
        "\"insights\" key. THAT ASSIGNMENT IS THE ONLY THING CARRYING "
        "verified_job to a caller -- the field name appears nowhere in "
        "server.py, so nothing else in this repository would notice it had "
        "stopped. Census row K10 claims COVERED on exactly this join."
    )
