"""Whether linkedin_search_jobs's docstring tells the truth about its own
result window, and whether the five filter-parameter spellings its
neighbouring tables promise are still the ones LinkedIn was shown to honor.

THE NUMBERS BELOW WERE MEASURED LIVE ON 2026-09-05 and are not re-measured
here. The source is two probe scripts:

* ``scripts/_probe_job_search_result_sets.py`` -- filter parameters compared
  on the RESULT-SET channel, not just the pill-and-count channel.
* ``scripts/_probe_job_search_paging_stride.py`` -- the paging stride itself.

What they found, taken as given rather than re-derived here:

* ``linkedin_search_jobs`` returned exactly 7 postings per call on a
  1036x703 viewport, on every one of 13 loads tried: two professions, two
  cities, five filters, and a repeated baseline that came back identical.
* LinkedIn's own result count for one of those queries was 2915 -- so 7 is
  a page fragment, nowhere close to a full result set.
* ``start`` offsets by ONES, not by pages: three loads at start=0, 7 and 14
  returned 21 distinct postings with zero overlap, against a zero-drift
  floor the same probe measured on a repeated load at a fixed offset.

At the time this file was written, ``linkedin_search_jobs``'s docstring
still told a caller to page with ``start=25, start=50`` -- a stride more
than three times the measured window, which silently drops eighteen of
every twenty-five postings a caller asked for and reports nothing that
would let anyone notice. That text is being replaced elsewhere, in the same
commit this file lands in. THIS FILE DOES NOT REPLACE IT -- it holds the
replacement to the two numbers above, so a future edit that reintroduces
the old stride, or drops the measured window, fails here instead of
shipping quietly a second time.

The last test re-affirms the five job-search parameter spellings
``server._BOOLEAN_FILTERS`` and ``server._JOB_TYPE``'s ``full_time``/
``contract`` rows. THEIR CHANNELS DIFFER BY DATE AND THAT DISTINCTION
MATTERS: all five were verified live on 2026-09-04 on the pill
(accessible-name/aria-state) and parameter-survival (kept vs stripped from
the landed url) channels -- but NOT yet on the result-set channel, which
``server._JOB_TYPE``'s own docstring records as "unavailable" that day,
because the job-card harvest returned 7 postings on every load including
baseline and so could not distinguish a working filter from a blind
reader. ``scripts/_probe_job_search_result_sets.py`` is what closed that
gap, comparing the actual returned postings, on 2026-09-05. This test pins
the spellings both dates' evidence rests on -- a drift guard beside this
window's finding, not a second measurement of it.
"""
from __future__ import annotations

import re

from linkedin_server import server as server_module
from linkedin_server.server import linkedin_search_jobs

# The fake page, the drive fixture and the search-card fixture come from the
# module that already owns them. Cross-module test imports are this suite's
# own convention -- tests/test_free_read_panels.py does the same and says why
# in its own header -- and a second copy of SEARCH_CARD or drive here would
# give the suite two fixtures free to drift apart while both looked right.
from tests.conftest import FakePage
from tests.test_tools import (  # noqa: F401 - drive is used by injection
    SEARCH_CARD,
    drive,
)

#: Three copies of SEARCH_CARD that differ only in the numeric job id inside
#: their href, so a walk that returns all three cannot be mistaken for a walk
#: that returned the same card three times over. Ten digits, comfortably past
#: dom.JOB_HREF's ``\d{6,}`` floor; consecutive only for readability, nothing
#: below depends on that.
_THREE_DISTINCT_SEARCH_CARDS = [
    {**SEARCH_CARD, "href": SEARCH_CARD["href"].replace("4111222333", job_id)}
    for job_id in ("4111222333", "4111222334", "4111222335")
]


# ---------------------------------------------------------------------------
# 1-2. The docstring itself. No browser, no `drive` -- these read a string.
#
# Each check below is a small function shared with a permanent CONTROL test
# beside it, rather than logic re-typed twice: a check that cannot fail
# certifies nothing, and tests/test_a_sanitiser_earns_its_entry.py already
# shipped one that could not, once. Sharing the function means the control
# and the real test can never quietly drift apart from each other.
# ---------------------------------------------------------------------------


def _prescriptive_paging_sentences(doc: str) -> list[str]:
    """Every sentence in ``doc`` that uses start=25 as live advice.

    "Live advice" means the sentence does NOT also carry a correction
    marker -- "not", "used to", "no longer", "instead of" -- so a sentence
    that CITES the old stride while rejecting it ("NOT start=25", "used to
    prescribe start=25") is not counted, and a bare instruction to page
    with it is.
    """
    sentences = re.split(r"(?<=[.!?])\s+", doc.replace("\n", " "))
    return [
        s
        for s in sentences
        if "start=25" in s
        and not re.search(r"\bnot\b|used to|no longer|instead of", s, re.I)
    ]


def _start_paragraphs(doc: str) -> list[str]:
    """Every blank-line-delimited paragraph of ``doc`` that mentions start."""
    return [p for p in doc.split("\n\n") if "start" in p]


#: The exact paragraph ``linkedin_search_jobs``'s docstring carried before
#: the 2026-09-05 fix -- transcribed from
#: ``scripts/_probe_job_search_paging_stride.py``'s own quotation of it, not
#: retyped from memory. A KNOWN-BAD input, kept here so the two checks above
#: can be shown catching it PERMANENTLY rather than only once, during
#: authoring, against a docstring that will not sit still in a shared tree.
_OLD_PAGING_PARAGRAPH = (
    "One page load per call, no scrolling and no auto-paging -- LinkedIn "
    "puts roughly 25 results on a page, so ask for the next page "
    "deliberately with start=25, start=50 and so on. capped in the result "
    "tells you the limit trimmed the rows, and page_had tells you how many "
    "the page actually held."
)


async def test_the_docstring_does_not_prescribe_a_stride_of_twenty_five():
    """The measured window is 7; a stride of 25 skips 18 of every 25 rows.

    NOT A BARE SUBSTRING CHECK, AND THAT IS A FINDING WORTH RECORDING HERE
    RATHER THAN SILENTLY PICKING ONE. The corrected docstring this test
    reads was written to name the mistake it replaces -- it says outright
    "SO PAGE WITH start=7, NOT start=25" and "This docstring used to
    prescribe start=25, start=50" -- so the literal substring "start=25" is
    PRESENT in the fixed text, on purpose, twice. A test asserting
    ``"start=25" not in doc`` would therefore fail forever against the
    correct docstring, which is a worse defect than the one it exists to
    catch: a tripwire that cannot tell a citation from an instruction is
    not a tripwire, it is noise that trains people to stop reading red.

    So this checks the thing the test's own name says: not whether the
    substring appears, but whether any SENTENCE containing it is doing so
    as live paging advice rather than as a correction -- see
    ``_prescriptive_paging_sentences``. Both sentences in the corrected
    docstring carry a marker; ``_OLD_PAGING_PARAGRAPH``'s does not. See
    ``test_the_stride_check_would_catch_the_old_advice`` for that kept live
    as a control rather than only observed once.
    """
    doc = linkedin_search_jobs.__doc__ or ""
    prescriptive = _prescriptive_paging_sentences(doc)
    assert not prescriptive, (
        "found start=25 used as live paging advice rather than as a "
        "corrected-from citation: %r -- "
        "scripts/_probe_job_search_paging_stride.py measured the window at "
        "7 postings per call, so a stride of 25 silently skips 18 of every "
        "25 postings between one call and the next and says nothing about "
        "it" % prescriptive
    )


def test_the_stride_check_would_catch_the_old_advice():
    """THE CONTROL for the test above. Without it, that test's green proves
    nothing on its own.

    Runs ``_prescriptive_paging_sentences`` -- the identical function, not a
    re-typed copy of its logic -- over ``_OLD_PAGING_PARAGRAPH``, the
    literal paragraph this docstring carried before 2026-09-05, and confirms
    it is caught.
    """
    caught = _prescriptive_paging_sentences(_OLD_PAGING_PARAGRAPH)
    assert caught, (
        "the prescriptive-sentence predicate let the pre-fix paging advice "
        "through unflagged: %r" % _OLD_PAGING_PARAGRAPH
    )


async def test_the_docstring_states_the_measured_window():
    """The replacement advice has to name the number it stands on.

    Loose enough to survive a rewording of the sentence -- no exact phrase
    is pinned -- but tight enough to fail if the paragraph disappears
    entirely: the measured window (7) has to appear in the SAME paragraph
    that talks about ``start`` (``_start_paragraphs``), and the docstring
    has to say the number was measured rather than assumed, which is the
    entire difference between this text and the one it replaces. See
    ``test_the_window_check_would_catch_the_old_paragraph`` for the second
    half proved against a known-bad input, kept live.
    """
    doc = linkedin_search_jobs.__doc__ or ""
    assert "measured" in doc.lower(), (
        "the docstring must say the window was MEASURED, not guessed -- "
        "that is the whole difference between this text and the one it "
        "replaces"
    )
    paragraphs = _start_paragraphs(doc)
    assert paragraphs, "no paragraph in the docstring even mentions start"
    assert any("7" in p for p in paragraphs), (
        "the paragraph(s) mentioning start do not name 7, the measured "
        "per-call window: %r" % paragraphs
    )


def test_the_window_check_would_catch_the_old_paragraph():
    """THE CONTROL for the test above, same reasoning as the one beside it.

    ``_OLD_PAGING_PARAGRAPH`` mentions start and never names 7 -- exactly
    the shape the real test's second assertion refuses. This runs that same
    assertion over the known-bad input instead of the live docstring.
    """
    paragraphs = _start_paragraphs(_OLD_PAGING_PARAGRAPH)
    assert paragraphs, (
        "the paragraph filter did not even recognise the known-bad "
        "paragraph as mentioning start, so this control input is not what "
        "this test thinks it is: %r" % _OLD_PAGING_PARAGRAPH
    )
    assert not any("7" in p for p in paragraphs), (
        "expected the OLD paragraph to be missing 7 and it was not, so "
        "this control input is not what this test thinks it is: %r"
        % paragraphs
    )


# ---------------------------------------------------------------------------
# 3. A behaviour test: does a short page say it was short.
# ---------------------------------------------------------------------------


async def test_a_page_smaller_than_the_limit_says_so(drive):
    """A page that held 3 rows and was asked for 25 should say it held fewer.

    ``capped`` already says whether the limit trimmed a BIGGER page down to
    size. Nothing today says the opposite -- that the page held FEWER rows
    than the caller asked for -- and that is exactly the shape a caller most
    needs flagged: this module's own docstring records the window measured
    at 7 against a limit that defaults to 25, so "the page had fewer rows
    than you asked for" is not a corner case here, it is closer to the
    common case. 3-of-25 and 3-of-3 carry identical `count`, `capped` and
    `results` shapes today; only a note can tell them apart.

    RED AT THE TIME OF WRITING (2026-09-05); the note is being added in the
    same commit as the docstring fix this file otherwise checks for, and
    this test is not the thing that adds it -- it only pins the behaviour
    once it exists. Observed on this tree before that landed:
    ``AssertionError: the page held 3 of the 25 rows asked for and nothing
    said so ... assert 'note' in {'count': 3, 'page_had': 3, 'capped':
    False, 'limit': 25, ...}``.
    """
    page = FakePage(evaluate_result=_THREE_DISTINCT_SEARCH_CARDS)
    drive(page)

    result = await linkedin_search_jobs(keywords="node.js engineer", limit=25)

    # The shape has to be right before the missing note means anything: three
    # distinct postings, none of them trimmed by the limit.
    assert result["count"] == 3, result
    assert result["page_had"] == 3, result
    assert result["capped"] is False, result
    assert len({row["job_id"] for row in result["results"]}) == 3, result[
        "results"
    ]

    assert "note" in result, (
        "the page held 3 of the 25 rows asked for and nothing said so -- "
        f"{result}"
    )
    note = result["note"].lower()
    assert "3" in result["note"] and "25" in result["note"], result["note"]
    assert "fewer" in note or "held" in note, result["note"]


# ---------------------------------------------------------------------------
# 4. The five spellings verified live on 2026-09-04, pinned at the value
#    level rather than only at the structural level test_tools.py already
#    checks.
# ---------------------------------------------------------------------------


async def test_the_boolean_filters_table_is_still_the_five_that_were_verified():
    """The five 2026-09-04 filter spellings, pinned so a rename fails loudly.

    ``tests/test_tools.py``'s ``BOOLEAN_FILTER_CASES`` plus the value-level
    control recorded in ``server._JOB_TYPE``'s own docstring measured these
    five parameter spellings against live LinkedIn: ``f_AL``, ``f_EA``,
    ``f_JIYN``, ``f_FCE`` and ``f_JT`` with its ``F``/``C`` values. Each one
    was shown, on 2026-09-04, to move a real control -- a checked pill for
    the four booleans, a "Reset selected Job type" affordance for f_JT --
    and to survive in the landed url, against a negative control
    (``f_ZZQQX``) that moved nothing and was stripped. Whether these five
    actually changed which POSTINGS came back, rather than only what the
    page drew, was still open that day (see this file's own module
    docstring); ``scripts/_probe_job_search_result_sets.py`` closed it on
    2026-09-05. Both dates together are what make "these five are read" a
    finding rather than a guess.

    Changing one of these five spellings does not raise where anyone would
    see it: ``linkedin_search_jobs`` binds them into a dict keyed by
    argument name, so a table that stopped matching the signature returns
    ``{"error": "unexpected", "message": "KeyError: ..."}`` with no page
    load at all -- quieter than a crash, and easy to misread as a transient
    fault rather than as every filtered search since silently returning the
    wrong jobs, or none of the intended narrowing. This pins the table at
    the VALUE level; ``test_the_boolean_table_and_the_signature_cannot_
    drift_apart`` in test_tools.py already pins it at the structural one.

    RED WHEN FORCED (proved during authoring by asserting this same
    comparison against a LOCAL copy of the table with one value corrupted --
    ``server_module._BOOLEAN_FILTERS`` itself was never written to, on disk
    or in memory):
    ``AssertionError: {'easy_apply': 'f_WRONG'} == {'easy_apply': 'f_AL',
    'under_ten_applicants': 'f_EA', 'in_your_network': 'f_JIYN',
    'fair_chance_employer': 'f_FCE'}``.
    """
    assert dict(server_module._BOOLEAN_FILTERS) == {
        "easy_apply": "f_AL",
        "under_ten_applicants": "f_EA",
        "in_your_network": "f_JIYN",
        "fair_chance_employer": "f_FCE",
    }, server_module._BOOLEAN_FILTERS
    assert server_module._JOB_TYPE["full_time"] == "F", server_module._JOB_TYPE
    assert server_module._JOB_TYPE["contract"] == "C", server_module._JOB_TYPE
