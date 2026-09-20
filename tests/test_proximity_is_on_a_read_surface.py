"""The per-job network-proximity field is ON a surface this server reads.

WHY THIS FILE EXISTS. The capability census writes six job rows off against a
blocker named ``SERVED-BY-GMAIL-SKILL``, and row ``J 40`` -- *read per-job
network proximity ("2 connections", "1 company alum")* -- carries the reason
cell **"Not on any surface this server reads"**, quoting an external skill's
line that no scraper or job-board API can produce the field.

That reason is a claim about THIS repo's surfaces, and this repo's own
committed captures refute it. The field is rendered on both hydrated job
surfaces and is simply not extracted. "Present and discarded" and "not on any
surface" are different verdicts with different prices: the first is a parser on
an address already admitted, the second is somebody else's job.

So this file pins the evidence, not the conclusion. It asserts only what the
bytes on disk say, and it is built to be able to say NO:

  POSITIVE  the two HYDRATED job captures each carry the proximity field.
  CONTROL   their UN-HYDRATED twins -- the same two pages before client-side
            render -- carry ZERO. Same needle, same pages, opposite answer, so
            a pass means the needle discriminates rather than matching prose.
  CONTROL   a non-job capture carries ZERO, so the needle is not matching
            LinkedIn chrome that happens to be on every page.

Nothing here reaches the network, a LinkedIn account, or a browser. It reads
four committed files and applies one regex.

Shown failing before admission: with the proximity line deleted from a COPY of
``jobs_search_hydrated.html`` the positive assertion fails, and with the needle
widened to a bare ``alum`` the un-hydrated control fails. Receipts are in
``_audit/2026-09-20-the-contingent-writeoffs.md``.
"""
from __future__ import annotations

import os
import re

import pytest

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")

#: The per-job proximity field, in every form LinkedIn has been observed to
#: draw it. Deliberately anchored on a COUNT or on the "<kind> alumni from"
#: heading -- a bare ``alum`` would also match an alumni FILTER label and a
#: school page, which is the way this check would quietly stop discriminating.
PROXIMITY = re.compile(
    r"\b\d+\s+(?:company|school)\s+alum(?:ni)?\b"
    r"|\b(?:Company|School)\s+alum(?:ni)?\s+from\b"
    r"|\b\d+\s+connections?\s+work",
    re.I,
)

#: Hydrated job surfaces -- pages ``linkedin_search_jobs`` and
#: ``linkedin_job_detail`` load on an ordinary call, at addresses already on
#: the navigation allowlist.
DRAWS_IT = ("jobs_search_hydrated.html", "job_detail_following_hydrated.html")

#: The un-hydrated twins of those same two pages, plus one unrelated surface.
#: These are the controls: if the needle matched here the positive result above
#: would be worth nothing.
DRAWS_IT_NOT = (
    "jobs_search.html",
    "job_detail_following.html",
    "profile_topcard_hydrated.html",
)


def _read(name: str) -> str:
    path = os.path.join(FIXTURES, name)
    assert os.path.exists(path), "missing committed fixture: %s" % name
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def proximity_hits(html: str) -> list:
    """Every proximity string in a page. A pure function, so the control runs
    below can drive it over mutated text without touching a committed file."""
    return [m.group(0).strip() for m in PROXIMITY.finditer(html)]


@pytest.mark.parametrize("name", DRAWS_IT)
def test_a_read_surface_draws_the_proximity_field(name):
    """The field the census calls unreachable is in a committed capture."""
    hits = proximity_hits(_read(name))
    assert hits, (
        "%s carries no proximity field. Either the capture was replaced or "
        "LinkedIn stopped drawing it -- both are findings, neither is a reason "
        "to widen the needle until this passes." % name
    )


@pytest.mark.parametrize("name", DRAWS_IT_NOT)
def test_the_needle_reads_zero_where_the_field_is_not_drawn(name):
    """The control. Same needle, pages that do not draw the field, zero hits.

    Two of these three are the UN-hydrated twins of the two captures above, so
    this is the tightest control available: identical page, identical needle,
    and the only difference is whether the client-side render ran.
    """
    hits = proximity_hits(_read(name))
    assert hits == [], (
        "%s matched %r. The needle has stopped discriminating, so the positive "
        "result above no longer means anything." % (name, hits)
    )


def _prose_lines(path):
    """Line numbers of PROSE in a module: comment lines, and docstring bodies.

    Written after the first version of this check called ``shape.py:699`` a
    reader. That line sits inside a function docstring, and a filter that only
    skipped lines beginning with ``#`` could not see the difference between a
    sentence about the field and a line of code naming it. A check that cannot
    tell prose from code cannot certify what this file claims.
    """
    import ast
    import tokenize

    prose = set()
    with open(path, "rb") as fh:
        for tok in tokenize.tokenize(fh.readline):
            if tok.type == tokenize.COMMENT:
                prose.update(range(tok.start[0], tok.end[0] + 1))

    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=path)
    holders = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    for node in ast.walk(tree):
        if not isinstance(node, holders):
            continue
        body = getattr(node, "body", None)
        if not body:
            continue
        first = body[0]
        if (isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)):
            prose.update(range(first.lineno, (first.end_lineno or first.lineno) + 1))
    return prose


def test_the_field_is_read_by_nothing_in_the_package():
    """The other half of the finding, and the reason the row is a BUILD.

    The field is drawn and thrown away. ``linkedin_server`` names an alumni
    line only in PROSE -- one ``#:`` comment in ``dom.py`` and one docstring
    sentence in ``shape.py``, both about field-shift hazards rather than about
    reading it -- and no line of CODE names it, whether as an identifier or as
    a string needle.

    This asserts that prose-only state. The day somebody wires a reader this
    test goes red and is deleted along with the census row: that is the
    intended end of this file, not a regression.
    """
    import glob

    pkg = os.path.join(os.path.dirname(FIXTURES), "..", "linkedin_server")
    modules = sorted(glob.glob(os.path.join(pkg, "*.py")))
    assert modules, "no modules found -- the package path is wrong, so a pass here means nothing"

    in_code, in_prose = [], []
    for path in modules:
        prose = _prose_lines(path)
        with open(path, encoding="utf-8", errors="replace") as fh:
            for n, line in enumerate(fh, 1):
                if not re.search(r"alum", line, re.I):
                    continue
                where = "%s:%d" % (os.path.basename(path), n)
                (in_prose if n in prose else in_code).append(where)

    assert in_prose, (
        "the two prose mentions this check is calibrated against are gone, so "
        "it is no longer looking at the package it was written for"
    )
    assert in_code == [], (
        "CODE now names the alumni field at %r. If that is a reader, census "
        "row J 40 is no longer a GAP and this file has done its job -- move "
        "the row and delete this test." % in_code
    )
