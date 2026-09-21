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
* **Not that the capability WORKS.** This file asserts the artifact EXISTS,
  never that it ran. **AMENDED 2026-09-20 AND THE AMENDMENT IS THE POINT:**
  this paragraph used to say the pinned rows are COVERED-UNFIRED *"precisely
  because nothing has seen them return a payload live"*. All three have since
  been fired live and now read COVERED-PROVEN. The sentence was true when it
  was written and became false without anything editing it -- so it is
  corrected here rather than left to describe a world that moved. What this
  file checks is unchanged: it reads the state cell and compares it to a pin,
  and the EVIDENCE for the promotion lives in the census row and in
  ``_audit/2026-09-20-the-unfired-twentyseven.md``, not here.
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
    # ALL THREE MOVED UNFIRED -> PROVEN ON 2026-09-20, and the pin is updated
    # DELIBERATELY rather than relaxed. This guard caught the upgrade on the
    # same run that banked it, which is the guard working in the direction
    # nobody designed it for: it was written to catch a banked row silently
    # reverting to GAP, and it also catches a row being promoted without
    # anybody saying so. A pin that only notices downgrades would have let an
    # unannounced upgrade through, and those are the ones that inflate a count.
    ("jobs.md", "10"): (
        "COVERED-PROVEN",
        "the company filter, FIRED 2026-09-20: an id resolved off a real "
        "posting, fed back to the search tool, filtered vs unfiltered "
        "overlapping in only 1 of 7 against a drift floor of 2",
    ),
    ("profile.md", "K10"): (
        "COVERED-PROVEN",
        "the job-posting verification badge, FIRED 2026-09-20 over 11 live "
        "postings: true on 5 and false on 6, so the reader discriminates "
        "rather than defaulting",
    ),
    ("jobs.md", "151"): (
        "COVERED-PROVEN",
        "multi-location search, FIRED 2026-09-20: 2 searches, 12 rows, 12 "
        "distinct ids, all carrying found_in, attributed to 2 places",
    ),
    # THE FIRST NETWORK ROWS ON THIS TABLE, 2026-09-21, and the first three
    # pinned at UNFIRED rather than PROVEN. That is the state they belong in
    # and pinning it is the point: the wave that built them was forbidden the
    # browser, so nothing has seen either tool return a payload live. This
    # guard was written to catch a banked row reverting to GAP and it also
    # catches an unannounced PROMOTION -- which is the direction that inflates
    # a count, and the one these three are most likely to drift in the moment
    # somebody fires them without writing it down.
    ("network.md", "33"): (
        "COVERED-UNFIRED",
        "connections at an organization: linkedin_company_page_counts opens "
        "the Page root by numeric id and returns a COUNT from integers read "
        "inside the document",
    ),
    ("network.md", "54"): (
        "COVERED-UNFIRED",
        "connections subscribed to a Page: the same reader and the same page "
        "load as row 33, a second phrase in one closed table",
    ),
    ("network.md", "175"): (
        "COVERED-UNFIRED",
        "the direct link to a group: linkedin_group_page builds "
        "/groups/<digits>/ and answers feed_drawn, reader_blind or ambiguous "
        "from anchor counts alone",
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
    """The control. A guard that reads an empty corpus refuses nothing.

    EXTENDED 2026-09-21 TO network.md, because the table above now pins rows
    in it. A pin over a slice this control does not read would pass on a walk
    that had been broken into finding nothing, which is the exact ambiguity
    this function exists to remove.
    """
    jobs, profile = _states("jobs.md"), _states("profile.md")
    network = _states("network.md")
    assert len(jobs) >= 100, f"only {len(jobs)} rows parsed out of jobs.md"
    assert len(profile) >= 100, f"only {len(profile)} rows parsed out of profile.md"
    assert len(network) >= 100, f"only {len(network)} rows parsed out of network.md"
    assert "10" in jobs and "K10" in profile, "the two banked rows are not being read"
    assert {"33", "54", "175"} <= set(network), (
        "the three network rows banked 2026-09-21 are not being parsed out of "
        "network.md, so their pins above are asserting nothing"
    )


def _defined_names(source: str) -> set[str]:
    """Function names DEFINED in a source, as AST definitions.

    Matched as definitions rather than as substrings for the reason the
    multi-location chain below earned on its first mutation run: an old name
    that is a PREFIX of its replacement survives a substring check while every
    call site points at nothing.
    """
    return {
        node.name
        for node in ast.walk(ast.parse(source))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


#: ``module -> the names census rows 33, 54 and 175 rest on``. Kept as data so
#: the chain test and the control below drive the SAME predicate over the same
#: list -- a control that checks a hand-copied subset proves the copy.
_THREE_READER_CHAIN: dict[str, tuple[str, ...]] = {
    "company_root.py": (
        "read_company_root",
        "connection_counts",
        "phrases_shipped",
        "control_fixture",
    ),
    "group_page.py": (
        "read_group_page",
        "reachability",
        "group_page_url",
        "landed_on_the_same_group",
    ),
    "dom.py": ("read_count_lines",),
    "server.py": ("linkedin_company_page_counts", "linkedin_group_page"),
}


def test_the_two_readers_behind_the_three_network_rows_are_still_whole() -> None:
    """``N 33``, ``N 54`` and ``N 175``: shaper -> reader -> tool.

    THE ROWS ARE COVERED ONLY IF EVERY LINK HOLDS. Each of the two chains ends
    at a registered tool, and the failure this asserts against is the one the
    file's docstring names in the other direction: a row left claiming
    coverage after somebody deletes the reader. Both of these modules are new,
    which makes them the likeliest in the package to be moved or folded into a
    neighbour by a later tidy-up.
    """
    for module, names in _THREE_READER_CHAIN.items():
        defined = _defined_names(_source(module))
        for name in names:
            assert name in defined, (
                f"{module} no longer defines {name}. Census rows 33, 54 and "
                "175 in network.md claim COVERED-UNFIRED against these two "
                "readers, and a chain with a link missing is a row claiming a "
                "capability nobody provides."
            )
    # THE SCRIPT IS PART OF THE CHAIN AND IT IS NOT A DEF, so it is asserted
    # separately rather than being left out because it did not fit the loop.
    assert "COUNT_LINES_JS" in _source("dom.py"), (
        "dom.COUNT_LINES_JS is gone; rows 33 and 54 rest on a reader whose "
        "in-page half no longer exists"
    )


def test_control_the_chain_check_convicts_a_renamed_reader() -> None:
    """SHOWN FAILING, against a MUTATED COPY so no tracked file is edited.

    A rename is the likeliest way one of these links breaks, and it is the
    shape a substring check cannot see when the old name is a prefix of the
    new one. This drives the SAME predicate the test above drives, over a copy
    of each module with one name extended.
    """
    for module, names in _THREE_READER_CHAIN.items():
        source = _source(module)
        target = names[0]
        mutated = source.replace(f"def {target}(", f"def {target}_renamed(")
        assert mutated != source, (module, target)
        assert target not in _defined_names(mutated), (
            f"the chain check cannot see {target} disappearing from {module}, "
            "so its green above certifies nothing"
        )


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
