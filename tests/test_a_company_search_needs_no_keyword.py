"""An employer stands in for the keyword -- census ``J 107``, "see all jobs".

THE ROW. ``J 107`` is the company Page's Jobs tab: every open posting at one
employer. Lane D applied D6 to it on 2026-09-24 and measured why the package's
own route did not deliver it (``_audit/2026-09-24-lane-d-d6-pdf.md`` section
1): ``linkedin_search_jobs(company_id=...)`` put the id in the ``f_C`` facet,
but the guard at the top of the tool refused any call without a keyword, so
the route could only ever return the postings at that employer that MATCHED A
WORD the caller had to invent -- a subset of a size nobody could know. The
keyword-less address, ``/jobs/search/?f_C=<id>``, was already admitted.

WHAT CHANGED, AND ALL THAT CHANGED. The guard now admits a keyword-less call
exactly when a company id is given, and a keyword-less call's url carries no
``keywords`` key at all. Every other call builds the url it always built.

WHAT THESE TESTS HOLD, and each has the control that makes it readable:

* the employer-only call makes ONE navigation, to exactly ``f_C=<id>`` and
  nothing else, and the shipped boundary admits that address;
* the guard still refuses a call with neither a keyword nor an employer, with
  ZERO navigations -- the control, without which "admits the employer call"
  cannot be told from "admits everything";
* an employer id that is not a Page id is refused by the company verdict
  before any load, so a keyword-less call cannot become a slug search;
* a keyworded call still builds keywords first.

THE LIVE ANSWER, 2026-09-28 (the live lane's session 3; ``J 107``
COVERED-PROVEN): LinkedIn DOES apply a default location to a keyword-less
employer search -- the no-location and "Worldwide" searches of one employer
shared 0 of their 7 postings. So the tool's docstring tells a caller who wants
every posting at an employer to pass location "Worldwide", and the last
section here pins that sentence, with a control on the words it replaced.

The company id is a synthetic number, the one lane D measured the boundary
with; the card is ``tests/test_tools.py``'s shared synthetic card.
"""
from __future__ import annotations

from urllib.parse import parse_qsl, urlsplit

import pytest

from linkedin_server import readonly
from linkedin_server.server import linkedin_search_jobs

from tests.conftest import FakePage
from tests.test_tools import SEARCH_CARD, drive  # noqa: F401 - drive by injection

#: A synthetic Page id -- the number lane D measured the boundary with.
EMPLOYER = "12345"


def _pairs(url: str) -> list[tuple[str, str]]:
    return parse_qsl(urlsplit(url).query, keep_blank_values=True)


async def test_an_employer_alone_is_a_search_and_its_url_is_only_the_facet(drive):
    page = FakePage(evaluate_result=[dict(SEARCH_CARD)])
    navigations = drive(page)

    result = await linkedin_search_jobs(keywords="", company_id=EMPLOYER)

    assert "error" not in result, result
    assert len(navigations) == 1, navigations
    assert _pairs(navigations[0]) == [("f_C", EMPLOYER)], navigations[0]
    assert urlsplit(navigations[0]).path == "/jobs/search/", navigations[0]
    assert readonly.is_read_url(navigations[0]), (
        "the keyword-less employer address must be one the shipped boundary "
        f"admits: {navigations[0]}"
    )
    assert result["results"], result
    assert result["query"]["keywords"] == "", result["query"]


async def test_blank_keywords_with_an_employer_build_the_same_address(drive):
    page = FakePage(evaluate_result=[dict(SEARCH_CARD)])
    navigations = drive(page)

    result = await linkedin_search_jobs(keywords="   ", company_id=f" {EMPLOYER} ")

    assert "error" not in result, result
    assert [_pairs(url) for url in navigations] == [[("f_C", EMPLOYER)]], navigations


async def test_neither_a_keyword_nor_an_employer_is_still_refused_before_any_load(drive):
    """THE CONTROL. Without it, the test above cannot tell "the employer call
    is admitted" from "the guard admits everything"."""
    page = FakePage(evaluate_result=[dict(SEARCH_CARD)])
    navigations = drive(page)

    for company in ("", "   "):
        result = await linkedin_search_jobs(keywords="", company_id=company)
        assert result.get("error") == "bad_argument", (company, result)
        assert "keywords is required" in result["message"], result
    assert navigations == [], navigations


async def test_an_employer_that_is_not_a_page_id_is_refused_before_any_load(drive):
    """A keyword-less call cannot become a search for a company's NAME: the
    company verdict still refuses a slug, and says so without quoting it."""
    page = FakePage(evaluate_result=[dict(SEARCH_CARD)])
    navigations = drive(page)

    result = await linkedin_search_jobs(keywords="", company_id="umbrella-systems")

    assert result.get("error") == "bad_argument", result
    assert "umbrella-systems" not in result["message"], result["message"]
    assert navigations == [], navigations


#: Values ``str.isdigit()`` accepts and no Page id is: a superscript two, a
#: circled one, fullwidth digits, and zeros. Built from code points so this
#: file stays ASCII.
NOT_A_PAGE_ID = (chr(0xB2), chr(0x2460), chr(0xFF11) + chr(0xFF12), "0", "000")


@pytest.mark.parametrize("company", NOT_A_PAGE_ID, ids=["sup2", "circled1", "fullwidth", "0", "000"])
async def test_a_digit_that_is_no_page_id_is_refused_before_any_load(drive, company):
    """The company verdict decides whether the id is a Page id, and a
    keyword-less call rests on it: a digit that is not ASCII, or an id of
    zeros, is refused rather than searched (the cold review)."""
    page = FakePage(evaluate_result=[dict(SEARCH_CARD)])
    navigations = drive(page)

    result = await linkedin_search_jobs(keywords="", company_id=company)

    assert result.get("error") == "bad_argument", (company, result)
    assert company not in result["message"]
    assert navigations == [], navigations


async def test_a_none_keyword_from_a_python_caller_is_the_employer_search_too(drive):
    """keywords stays REQUIRED -- the tool-envelope guard drives each tool with
    its required arguments, and a default would stop it driving this one --
    but a None from a Python caller reaches the employer search and is echoed
    as empty rather than raising after the load (the cold review)."""
    page = FakePage(evaluate_result=[dict(SEARCH_CARD)])
    navigations = drive(page)

    absent = await linkedin_search_jobs(keywords=None, company_id=EMPLOYER)

    assert "error" not in absent, absent
    assert [_pairs(url) for url in navigations] == [[("f_C", EMPLOYER)]]
    assert absent["query"]["keywords"] == ""


@pytest.mark.parametrize("company", ["", EMPLOYER])
async def test_a_keyworded_search_builds_keywords_first_as_it_always_did(drive, company):
    page = FakePage(evaluate_result=[dict(SEARCH_CARD)])
    navigations = drive(page)

    result = await linkedin_search_jobs(keywords="node.js engineer", company_id=company)

    assert "error" not in result, result
    pairs = _pairs(navigations[0])
    assert pairs[0] == ("keywords", "node.js engineer"), pairs
    assert (("f_C", EMPLOYER) in pairs) is bool(company), pairs


# ---------------------------------------------------------------------------
# THE DOCSTRING SAYS WHAT THE LIVE FIRE MEASURED
# ---------------------------------------------------------------------------

#: The instruction, as the docstring words it.
WORLDWIDE = 'For every posting at an employer, pass location "Worldwide".'

#: The measurement it rests on, in the docstring's words.
MEASURED = (
    'LinkedIn applies a DEFAULT LOCATION to a keyword-less employer search',
    '"Worldwide" searches of one employer shared 0 of their 7 postings',
)

#: What the docstring said before the fire, word for word: the default was
#: UNVERIFIED. A docstring still carrying it would tell a caller the question
#: is open when it has been answered the other way.
BEFORE_THE_FIRE = (
    "whether LinkedIn's default location narrows a keyword-less employer "
    "search is UNVERIFIED"
)


def _flat(text: str) -> str:
    """Whitespace-normalised, so the pin survives a reflow."""
    return " ".join(text.split())


def _docstring() -> str:
    return _flat(linkedin_search_jobs.__doc__ or "")


def test_the_docstring_tells_a_caller_to_pass_worldwide_for_every_posting():
    doc = _docstring()
    assert WORLDWIDE in doc
    for words in MEASURED:
        assert words in doc, words
    assert BEFORE_THE_FIRE not in doc


def test_THIS_CONTROL_CAN_FAIL_the_words_before_the_fire_are_convicted():
    """The paragraph as it stood before the fire: it lacks the instruction and
    carries the open question, and the pin above would reject it."""
    before = _flat(
        "ALL OF ONE EMPLOYER'S POSTINGS: pass company_id and an EMPTY keywords "
        "(\"\" -- the argument is still required, so pass it rather than leave "
        "it out). That is the company Page's \"see all jobs\" as a search, with "
        "no keyword narrowing it; with neither, the call is refused. BUILT, NOT "
        "YET FIRED LIVE (census J 107, 2026-09-28): whether LinkedIn's default "
        "location narrows a keyword-less employer search is UNVERIFIED -- the "
        "Page lists the employer's postings wherever they are -- so pass "
        "`location` when the answer must not depend on that default."
    )
    assert WORLDWIDE not in before
    assert BEFORE_THE_FIRE in before


async def test_the_worldwide_call_the_docstring_prescribes_is_one_the_tool_builds(drive):
    """The instruction is a call the tool accepts: an employer, no keyword and
    location "Worldwide" -- one navigation, the facet and the place, no
    keyword key."""
    page = FakePage(evaluate_result=[dict(SEARCH_CARD)])
    navigations = drive(page)

    result = await linkedin_search_jobs(keywords="", company_id=EMPLOYER, location="Worldwide")

    assert "error" not in result, result
    assert len(navigations) == 1, navigations
    pairs = _pairs(navigations[0])
    assert ("f_C", EMPLOYER) in pairs and ("location", "Worldwide") in pairs, pairs
    assert "keywords" not in dict(pairs), pairs
