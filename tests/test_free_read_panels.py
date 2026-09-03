"""The free reads that were already on a page this server opens anyway.

Three readers were added to ``dom.py`` for panels that render on surfaces
``linkedin_job_detail`` and ``linkedin_my_profile`` already load, and that were
being thrown away. This file is their evidence, and it is deliberately split
across the two ways such a reader can be wrong.

PART 1 drives ``dom.read_job_insight_panels`` against the two committed job
captures on a LOCAL headless Chromium. A fake page cannot answer these
questions: the reader climbs a heading's ancestors to find the block it owns,
so what it returns is a property of the PARSED DOM rather than of any string,
and only a browser parses.

PART 2 drives ``linkedin_my_profile`` on the scripted fake, because the three
counts it has DECLARED and returned null for are a question about which page
the tool loads and what it does with the answer -- no DOM required, and a
browser would only make the navigation log harder to read.

WHAT IS BEING PROTECTED, said plainly. Every panel here is free: it costs zero
extra page loads and zero clicks, which is exactly why nobody notices when one
silently stops arriving. A reader that returns None for a panel LinkedIn drew
and a page that genuinely has no panel look identical in a result, so the
control tests below build both states on purpose and assert they come back
DIFFERENT. A check that cannot fail certifies nothing.

Nothing here reaches the network or a LinkedIn account. Local headless
Chromium over committed captures, and a fake page, and nothing else.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from linkedin_server import dom
from linkedin_server import server as server_module
from linkedin_server.server import linkedin_my_profile

# The scripted fake and its constants come from the module that already owns
# them. Cross-module test imports are this suite's own convention -- several
# other files do it -- and a second copy of ``ScriptedPage`` here would give
# the suite two fakes that could drift apart while both looked right.
from tests.test_tools import (  # noqa: F401 - drive is used by injection
    PROFILE_FIELDS,
    PROFILE_ME_URL,
    PROFILE_RESOLVED_URL,
    ScriptedPage,
    drive,
)

FIXTURES = Path(__file__).parent / "fixtures"

#: The two job captures, and the posting id one of them is addressed by. The
#: id is an INVENTED value from a sanitised capture, and is the same one
#: ``tests/test_job_detail_wiring.py`` drives.
HYDRATED = "job_detail_hydrated"
HYDRATED_JOB_ID = "4600000042"
FOLLOWING = "job_detail_following_hydrated"


@pytest.fixture
async def chromium_page():
    """One local headless Chromium for the module. Nothing leaves the machine."""
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            yield await browser.new_page()
        finally:
            await browser.close()


async def _panels(page, fixture: str) -> dict:
    """Load a committed capture into the real page and read its panels."""
    html = (FIXTURES / f"{fixture}.html").read_text(encoding="utf-8")
    await page.set_content(html, wait_until="domcontentloaded")
    return await dom.read_job_insight_panels(page)


async def _panels_of_markup(page, markup: str) -> dict:
    """The same read, over markup this file builds rather than a capture."""
    await page.set_content(markup, wait_until="domcontentloaded")
    return await dom.read_job_insight_panels(page)


# ---------------------------------------------------------------------------
# PART 1a. The applicant panel, on the capture that carries view names
# ---------------------------------------------------------------------------


async def test_the_applicant_panel_comes_back_with_its_heading(chromium_page):
    panels = await _panels(chromium_page, HYDRATED)

    assert panels["applicant_insights"] is not None, panels["observed"]
    assert (
        panels["applicant_insights"]["heading"]
        == "See how you compare to other applicants"
    )


async def test_the_applicant_counts_are_paired_number_then_label(chromium_page):
    """The pairing is LinkedIn's own order, and it was checked before it was
    asserted.

    ``dom.pair_metrics`` documents LinkedIn as drawing the NUMBER first and its
    label after it. That claim was re-measured against this capture rather than
    taken on trust: ``Applicants for this job`` holds the five lines
    heading / 7691 / "Applicants" / 200 / "Applicants in the past day", and the
    two pairs below are what the reader makes of them. They are asserted as the
    WHOLE list, not merely as members of it, because a pairing that silently
    grew a third entry would be a pairing that had shifted.
    """
    panels = await _panels(chromium_page, HYDRATED)
    metrics = panels["applicant_insights"]["metrics"]

    assert {"value": "7691", "label": "Applicants"} in metrics
    assert {"value": "200", "label": "Applicants in the past day"} in metrics
    assert metrics == [
        {"value": "7691", "label": "Applicants"},
        {"value": "200", "label": "Applicants in the past day"},
    ]


async def test_the_seniority_mix_is_three_lines_and_every_one_is_a_share(
    chromium_page,
):
    """Three bands, each carrying its own percentage.

    The percentage is the assertion that matters. A seniority list of three
    plausible sentences with the numbers dropped would still be three lines,
    and would be worthless -- the mix IS the number.
    """
    panels = await _panels(chromium_page, HYDRATED)
    seniority = panels["applicant_insights"]["seniority"]

    assert len(seniority) == 3, seniority
    assert all("%" in line for line in seniority), seniority


async def test_the_education_rows_reach_the_field_through_the_positional_read(
    chromium_page,
):
    """A MISMATCH, PINNED RATHER THAN PAPERED OVER. Expected four; got zero.

    This test was commissioned as ``education has 4 entries``. It does not, on
    either committed capture, and the reason is not that LinkedIn drew nothing
    -- it is that the reader cannot see what LinkedIn drew:

    * the capture carries a ``<tbody>`` holding four ``<tr>`` rows of education
      shares, and NO ``<table>`` anywhere in the file;
    * an HTML parser drops ``<tbody>`` and ``<tr>`` outside a table, so the
      panel's ``<h3>`` is reparented into a ``<div>`` that already holds the
      applicant-counts block and the seniority block -- three headings in one
      parent;
    * ``dom.READ_PROFILE_JS`` climbs only while an ancestor holds exactly ONE
      heading, so it breaks at the first hop and the section's ``lines`` are
      the heading and nothing else;
    * ``dom.lines_below`` then strips that heading, leaving ``[]``.

    The rows themselves are not lost -- ``main``'s rendered text carries all
    four, in order, directly under the heading. Only the section walk misses
    them.

    So this asserted BOTH halves -- the panel WAS seen, its rows did NOT
    arrive -- and said the moment ``dom.py`` learned to read them it would
    fail, which is the intended way for a pin on a gap to end.

    ## IT ENDED THAT WAY, THE SAME HOUR

    ``dom.lines_after_heading`` reads the rows positionally out of ``main``'s
    text when the structural walk returns nothing, and ``dom.share_rows``
    joins the split ``12%`` / ``have a ...`` pairs back together. The
    structural read is still tried FIRST and still wins wherever it works:
    seniority comes back through it on both captures and is untouched. The
    weaker anchor is used exactly where the stronger one was measured to
    fail.

    **AND THE FIRST FIX WAS WRONG BY ONE ROW.** Bounded only by the next
    HEADING, it returned FIVE education rows where the page draws four -- the
    fifth being ``Insights about the company``, which is a ``<strong>`` and
    so invisible to a heading boundary. The run is now bounded by its own
    SHAPE instead: every row of a share breakdown starts with a share, and
    the first line that does not ends the run. That is why this test asserts
    the exact length AND the exact first row rather than just truthiness --
    a bleed of one line from the next panel passes any assertion that only
    asks whether the list is non-empty.
    """
    panels = await _panels(chromium_page, HYDRATED)

    assert "Applicant education level" in panels["observed"]["headings"]
    education = panels["applicant_insights"]["education"]
    assert len(education) == 4, education
    assert education[0].startswith("12% have a Bachelor")
    assert education[-1] == "30% have other degrees"
    # THE BLEED THIS EXISTS TO CATCH, named so a future reader knows the
    # length assertion above is load-bearing rather than incidental.
    assert "Insights about the company" not in education
    # The structural read still wins where it works, and this is the control
    # for that claim: seniority never went through the fallback.
    assert len(panels["applicant_insights"]["seniority"]) == 3


async def test_the_company_panel_is_reported_by_shape_and_is_present(
    chromium_page,
):
    panels = await _panels(chromium_page, HYDRATED)

    assert panels["company_insights"] is not None, panels["observed"]
    assert panels["company_insights"]["heading"] == dom.JOB_COMPANY_PANEL_SHAPE


async def test_the_company_panel_carries_its_rows_and_not_its_plumbing(
    chromium_page,
):
    """The panel's CONTENT, which shipped empty until the fallback reached it.

    Its heading was found and its ``lines`` were ``[]`` on both captures, for
    the same reason the education rows were: the structural walk cannot reach
    a block whose heading shares a parent with two others. It carries the one
    thing on a posting that is genuinely about the EMPLOYER rather than the
    role -- headcount, two-year growth, median tenure -- so an empty list here
    was a silently wrong answer rather than a missing nicety.

    THREE BOUNDARIES ARE ASSERTED, because each was wrong once:

    * ``Powered by Bing`` is a byline LinkedIn draws INSIDE the panel and the
      section walk reports it as a heading. Stopping there returned an empty
      panel, so it is IGNORED rather than stopped at -- and the first row
      after it is asserted here, which is what proves the skip works.
    * ``Show Premium Insights`` sits at the panel's END and is not a heading,
      so the read ran one line past it. It is asserted absent.
    * the screen-reader chart plumbing is dropped, and the one line of that
      block worth keeping is asserted PRESENT -- a filter that took the whole
      block would have been indistinguishable from one that took too much.
    """
    panels = await _panels(chromium_page, HYDRATED)
    lines = panels["company_insights"]["lines"]

    assert lines, panels["observed"]["headings"]
    assert lines[0] == "The latest hiring trend"
    assert "288" in lines and "Total employees" in lines
    assert any(line.startswith("Median employee tenure") for line in lines)

    assert "Powered by Bing" not in lines
    assert "Show Premium Insights" not in lines
    assert "Chart" not in lines
    assert "End of interactive chart." not in lines
    assert not any(line.startswith("The chart has ") for line in lines)
    assert "Chart with 25 data points." in lines


#: THE LIVE PROFILE-VIEWS PAGE, REPRODUCED IN ITS ONE LOAD-BEARING RESPECT.
#:
#: Measured through the shipped tool on 2026-09-03: the live analytics page
#: carried NO ``data-view-name`` attribute ANYWHERE. ``observed.view_names``
#: came back ``[]`` and ``view_name_counts`` came back ``{}`` on a page with
#: nine viewer rows on it. The committed capture is from 2026-08-23 and is
#: full of them, so every assertion taken from that capture exercises the
#: PRECISE anchor and none of them exercises the page LinkedIn serves today.
#:
#: A fixture cannot be re-captured here -- that needs the live account and the
#: profile lock -- so the shape is reproduced instead: the same metric
#: paragraphs, the same filter captions as ``<label>`` elements, the same
#: chart sentence, and not one ``data-view-name``. What it is faithful ABOUT
#: is the only thing this test turns on.
LIVE_SHAPED_VIEWS_PAGE = (
    "<!doctype html><html><body><main>"
    "<div><p>31</p><p>Profile viewers</p></div>"
    "<div><p>20%</p><p>vs. prior 7 days</p></div>"
    "<div><label>Past 90 days</label></div>"
    "<div><label>Interesting viewers</label></div>"
    "<div><label>Company</label></div>"
    "<div><div>Line chart with 13 data points.</div></div>"
    "</main></body></html>"
)


async def test_the_views_reader_still_works_when_no_view_name_is_drawn(
    chromium_page,
):
    """THE ANCHOR THIS READER WAS BUILT ON IS NOT ON THE LIVE PAGE.

    Both the chart and the filters were originally found through
    ``data-view-name``, because the committed capture hangs one off every
    control. A live call on 2026-09-03 returned ``trend: null`` and
    ``filters: []`` while the controls were plainly on screen, and
    ``observed`` said why in the same breath: ``view_names: []``,
    ``view_name_counts: {}``, ``main_chars: 2092``. **That is the observed
    block earning its place** -- two nulls with no explanation would have read
    as "LinkedIn drew no chart", which is false.

    So each has a second route, and this is what exercises it, because no
    committed capture can: the capture has the attribute and the live page
    does not, so an assertion taken from the capture proves only that the
    route nobody hits still works.

    THE SECOND ROUTES STAY INSIDE THE READER'S PRIVACY RULE, which is the part
    worth checking rather than assuming. Filters fall back to ``<label>``
    elements -- a form control's own caption, never an ``aria-label``, because
    this page's aria-labels name other members. The chart falls back to the
    line of ``main``'s text carrying its own description, which IS the value
    the field returns, so finding it directly loses nothing. Both fallbacks
    are capped.
    """
    panels = await _panels_of_markup(chromium_page, LIVE_SHAPED_VIEWS_PAGE)
    del panels  # this markup is a views page; the job reader is not its reader

    views = await dom.read_profile_views_insights(chromium_page)

    # The premise: this page is shaped like the live one, not like the capture.
    assert views["observed"]["view_names"] == []
    assert views["observed"]["view_name_counts"] == {}

    assert views["headline"] == {"value": "31", "label": "Profile viewers"}
    assert views["delta"] == {"value": "20%", "label": "vs. prior 7 days"}
    assert views["filters"] == ["Past 90 days", "Interesting viewers", "Company"]
    assert views["trend"]["present"] is True
    assert views["trend"]["description"] == "Line chart with 13 data points."


async def test_the_committed_analytics_capture_cannot_exercise_this_reader(
    chromium_page,
):
    """THE ANALYTICS FIXTURE HAS NO ``<main>``, so the reader reads nothing
    from it -- and that is a fact about the corpus rather than a bug.

    This test was written as the opposite: assert the view-name route on the
    capture, since that capture hangs a ``data-view-name`` off every control.
    It fails, and the measurement is worth more than the assertion was::

        has_main        False
        doc_view_names     45      <- all of them, and all outside main
        body_chars       1433
        main_chars          0

    Forty-five view names in the document and none reachable, because
    ``read_profile_views_insights`` scopes to ``main`` and this freeze has no
    ``main`` element anywhere.

    **THE READER IS NOT WIDENED TO ``body`` TO MAKE THIS PASS.** The live page
    HAS a main -- measured, 2,092 characters, and the headline and delta come
    back through it -- so scoping is correct for the surface this runs on.
    Widening it would mean reading the whole document on a page that IS a list
    of other members, to satisfy a fixture. That is the wrong direction to
    trade, and it is the trade this file exists to refuse.

    WHAT IT COSTS, said plainly so nobody re-derives it: the analytics capture
    cannot test this reader at all. The behaviour is covered by
    ``test_the_views_reader_still_works_when_no_view_name_is_drawn``, whose
    markup reproduces the LIVE page's shape, and by the live call recorded in
    the wave notes. Re-capturing the fixture WITH its main element would give
    the view-name route a home; that needs the live account and the profile
    lock, and is left as the one uncovered path.

    Meanwhile this asserts the two-different-zeros property on a real file:
    ``main_present`` False is not the same answer as an empty main, and the
    reader says which.
    """
    html = (FIXTURES / "profile_views_analytics_hydrated.html").read_text(
        encoding="utf-8"
    )
    await chromium_page.set_content(html, wait_until="domcontentloaded")
    views = await dom.read_profile_views_insights(chromium_page)

    assert views["observed"]["main_present"] is False
    assert views["observed"]["main_chars"] == 0
    assert views["headline"] is None
    assert views["trend"] is None
    assert views["filters"] == []

    # The document is not empty -- the panels ARE in this file, just not under
    # a main. Asserted so the zero above cannot be read as "the capture is
    # blank", which is the misreading this whole file is built against.
    outside = await chromium_page.evaluate(
        "() => document.querySelectorAll('[data-view-name]').length"
    )
    assert outside > 40, outside

    # NO top-companies AND NO top-locations. Asserted on the reader's own
    # return shape, which carries no such key in any state.
    assert "top_companies" not in views
    assert "top_locations" not in views


async def test_a_promoted_posting_says_so(chromium_page):
    panels = await _panels(chromium_page, HYDRATED)

    assert panels["promoted"] is True


async def test_the_two_collapsed_panels_are_named_rather_than_silently_absent(
    chromium_page,
):
    """Naming what this server will not open is worth more than a null.

    Both panels sit behind a control, and pressing one is a click rather than a
    read. Reported by name, a caller learns the panel exists and that this
    server declined to open it; omitted, the same result would read as
    "LinkedIn does not show you this", which is false.
    """
    panels = await _panels(chromium_page, HYDRATED)

    assert panels["more_behind_a_control"] == [
        "Show match details",
        "Show Premium Insights",
    ]


# ---------------------------------------------------------------------------
# PART 1b. The capture with NO data-view-name anywhere
#
# THIS IS THE IMPORTANT ONE. ``job_detail_following_hydrated.html`` carries no
# ``data-view-name`` attribute at all -- measured, and asserted below rather
# than described -- while ``job_detail_hydrated.html`` carries ten. A reader
# anchored on the view name would read one capture and return nothing for the
# other, and would look completely healthy while doing it, because the healthy
# capture is the one every other test uses. The panel wording differs too
# ("others who clicked apply" against "other applicants"), so a reader anchored
# on the word "Applicant" misses this posting entirely.
# ---------------------------------------------------------------------------


async def test_the_second_spelling_of_the_applicant_heading_is_read_too(
    chromium_page,
):
    panels = await _panels(chromium_page, FOLLOWING)

    assert panels["applicant_insights"] is not None, panels["observed"]
    assert (
        panels["applicant_insights"]["heading"]
        == "See how you compare to others who clicked apply"
    )


async def test_this_capture_carries_no_view_name_at_all(chromium_page):
    """The proof that the reader is not anchored on the view name.

    Without this assertion every test in this section is ambiguous: they would
    pass just as well on a reader that keyed off ``data-view-name`` and got
    lucky. The empty list is what makes the section mean what it claims.
    """
    panels = await _panels(chromium_page, FOLLOWING)

    assert panels["observed"]["view_names"] == []


async def test_the_verified_badge_and_the_off_linkedin_notice_are_read(
    chromium_page,
):
    """Three facts a caller can act on, none of them on any card.

    The badge is the one to notice: the capability census recorded that this
    repository prints no rendered badge wording anywhere, and the wording was
    sitting in this committed fixture the whole time.
    """
    panels = await _panels(chromium_page, FOLLOWING)

    assert panels["verified_job"] is True
    assert panels["responses_managed_off_linkedin"] is True
    assert panels["promoted"] is True


# ---------------------------------------------------------------------------
# PART 1c. THE CONTROL. Two different zeros.
# ---------------------------------------------------------------------------


async def test_an_empty_main_returns_empty_panels_and_says_main_was_there(
    chromium_page,
):
    """Zero panels, and a ``main`` that rendered with nothing in it.

    Every assertion in this file above it would pass on a reader that returned
    a fully populated dict for any input. This is the half of the pair that
    makes them mean something.
    """
    panels = await _panels_of_markup(chromium_page, "<main></main>")

    assert panels["applicant_insights"] is None
    assert panels["company_insights"] is None
    assert panels["promoted"] is False
    assert panels["responses_managed_off_linkedin"] is False
    assert panels["verified_job"] is False
    assert panels["more_behind_a_control"] == []
    assert panels["observed"]["headings"] == []
    assert panels["observed"]["heading_count"] == 0
    assert panels["observed"]["view_names"] == []
    assert panels["observed"]["main_present"] is True
    assert panels["observed"]["main_chars"] == 0


async def test_a_page_with_no_main_is_a_different_zero_from_an_empty_one(
    chromium_page,
):
    """The second zero, and the whole reason ``observed`` exists.

    "No panel, and main was empty" and "no panel, and there was no main" are
    different findings -- one is a page that drew and holds nothing, the other
    is a page this reader was pointed at wrongly or that never rendered. A bare
    null cannot tell them apart, and telling them apart is what stops the next
    person diagnosing the wrong thing.
    """
    panels = await _panels_of_markup(chromium_page, "<div>no main here</div>")

    assert panels["applicant_insights"] is None
    assert panels["observed"]["main_present"] is False
    assert panels["observed"]["main_chars"] == 0

    empty_main = await _panels_of_markup(chromium_page, "<main></main>")
    assert (
        empty_main["observed"]["main_present"]
        is not panels["observed"]["main_present"]
    )


# ---------------------------------------------------------------------------
# PART 1d. THE REDACTION. The employer's name never leaves the reader.
# ---------------------------------------------------------------------------


def _employer_in(html: str) -> str:
    """The employer name this capture carries, taken from the capture itself.

    Derived rather than typed, so this file never has to hold the name it is
    asserting the absence of. It is the SANITISED name the tracked fixture
    carries -- an invented one -- and the real strings live in a file this test
    does not open and nothing here may reproduce.
    """
    marker = dom.JOB_COMPANY_PANEL_PREFIX
    start = html.index(marker) + len(marker)
    tail = html[start:]
    return tail[: tail.index("<")].strip()


def _strings_in(node):
    """Every string anywhere in a nested result, keys included."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _strings_in(key)
            yield from _strings_in(value)
    elif isinstance(node, (list, tuple)):
        for item in node:
            yield from _strings_in(item)
    elif isinstance(node, str):
        yield node


async def test_the_employer_name_is_nowhere_in_the_return_and_the_shape_is(
    chromium_page,
):
    """LinkedIn writes the employer into the panel's own heading.

    The heading reads "Exclusive Job Seeker Insights about <employer>", and it
    reaches a result TWICE -- once as the panel's heading and once in the
    heading tally -- so a reader that shaped only one of them would publish the
    name through the other. The walk below is recursive and covers keys as well
    as values, because a reader that ever keyed a dict by a heading would leak
    through a route a value-only walk cannot see.

    The positive half is not optional. Asserting only the absence would pass on
    a reader that returned nothing at all, which is the same failure this
    file's controls exist to catch one level up.
    """
    html = (FIXTURES / f"{HYDRATED}.html").read_text(encoding="utf-8")
    employer = _employer_in(html)
    assert employer, "the capture no longer carries the company panel heading"

    panels = await _panels(chromium_page, HYDRATED)

    offenders = [text for text in _strings_in(panels) if employer in text]
    assert offenders == [], offenders

    assert panels["company_insights"]["heading"] == dom.JOB_COMPANY_PANEL_SHAPE
    assert dom.JOB_COMPANY_PANEL_SHAPE in panels["observed"]["headings"]


# ---------------------------------------------------------------------------
# PART 1e. THE WIRING. The tool, not the reader.
# ---------------------------------------------------------------------------


async def _job_detail(monkeypatch, page, fixture: str, job_id: str) -> dict:
    """Call the real tool with a frozen capture behind it.

    The same session-and-navigation patch ``tests/test_job_detail_wiring.py``
    uses, for the same reason: the tool's own body runs unmodified, including
    the lines this test exists to cover.
    """
    html = (FIXTURES / f"{fixture}.html").read_text(encoding="utf-8")

    class Session:
        async def __aenter__(self):
            await page.set_content(html, wait_until="domcontentloaded")
            return page

        async def __aexit__(self, *exc):
            return False

    async def fake_goto(_page, url, **kwargs):
        # The content is already loaded; report the url the tool asked for, so
        # the auth-wall check sees a job posting rather than a blank page.
        return url

    monkeypatch.setattr(server_module.BROWSER, "session", lambda: Session())
    monkeypatch.setattr(server_module.BROWSER, "goto", fake_goto)
    return await server_module.linkedin_job_detail(job_id)


async def test_the_tool_actually_returns_the_panels_it_computes(
    monkeypatch, chromium_page
):
    """A field computed correctly and never plumbed is invisible to every unit
    test of the computation.

    Everything above this drives ``dom.read_job_insight_panels`` directly, and
    every one of those tests passes whether or not anybody CALLS it. Delete the
    two lines in ``server.py`` that put the reading into the result and this is
    the only test in the file that notices -- which is exactly the shape of gap
    ``tests/test_job_detail_wiring.py`` was written for, on the same tool, one
    field earlier.

    ``pages_loaded`` is pinned beside it because the whole claim these panels
    are sold on is that they are free. A future reading that reached for a
    second surface would move that number and nothing else would complain.
    """
    out = await _job_detail(
        monkeypatch, chromium_page, HYDRATED, HYDRATED_JOB_ID
    )

    assert "error" not in out, out
    assert "insights_error" not in out, out.get("insights_error")
    assert out["insights"]["applicant_insights"] is not None
    assert out["pages_loaded"] == 1


# ---------------------------------------------------------------------------
# PART 2. ``linkedin_my_profile``'s three counts.
#
# All three were DECLARED in the result and hardcoded null since the tool
# shipped -- not a limitation of the render, but a tool that runs and cannot
# deliver three of its own stated outputs. These tests are about which page a
# call loads, so they run on the scripted fake and assert the NAVIGATION LOG as
# well as the answer: a count can be right and still have been guessed, and
# only the log tells the two apart.
# ---------------------------------------------------------------------------

#: An experience details page, as the link-anchored harvest returns it. Three
#: cards, which is the number the live probe recorded in
#: ``dom.PROFILE_DETAIL_ENTRY_HREF``'s note. Every company below is invented,
#: and the doubled first line is LinkedIn's own habit of rendering each label
#: twice, once visually and once for a screen reader.
EXPERIENCE_CARDS = [
    {
        "href": "/in/alex-r/details/experience/edit/forms/301/",
        "text": (
            "Senior Node.js Engineer\n"
            "Senior Node.js Engineer\n"
            "Aurora Labs - Full-time\n"
            "2 yrs 3 mos"
        ),
    },
    {
        "href": "/in/alex-r/details/experience/edit/forms/302/",
        "text": (
            "Backend Engineer\n"
            "Backend Engineer\n"
            "Beacon Systems - Full-time\n"
            "1 yr 8 mos"
        ),
    },
    {
        "href": "/in/alex-r/details/experience/edit/forms/303/",
        "text": (
            "Software Engineer\n"
            "Software Engineer\n"
            "Corvid Interactive - Full-time\n"
            "11 mos"
        ),
    },
]

#: The education page. ONE card, which is what the same probe recorded.
EDUCATION_CARDS = [
    {
        "href": "/in/alex-r/details/education/edit/forms/401/",
        "text": (
            "Indian Institute of Information Technology\n"
            "Indian Institute of Information Technology\n"
            "Bachelor of Technology - BTech, Computer Science\n"
            "2016 - 2020"
        ),
    },
]

#: Read off the server's own table rather than typed out again here. The point
#: of that table is that the process can say what it is about to navigate to
#: without asking anything outside the package, and a test that retyped the
#: address would be asserting against its own copy of the answer.
EXPERIENCE_URL = server_module.PROFILE_DETAIL_URLS["experience"]
EDUCATION_URL = server_module.PROFILE_DETAIL_URLS["education"]
SKILLS_URL = server_module.PROFILE_DETAIL_URLS["skills"]


def _scripted(queue):
    """The profile fake, with ``/in/me/`` redirecting the way LinkedIn does."""
    return ScriptedPage(
        evaluate_queue=list(queue),
        redirect_map={PROFILE_ME_URL: PROFILE_RESOLVED_URL},
    )


async def test_details_experience_loads_that_page_and_fills_that_count(drive):
    """The count is READ, and the result says where it was read.

    ``experience_entries`` was null by construction until the details page was
    wired in, and a null there is indistinguishable from "LinkedIn holds
    none". So this asserts the number AND its stated source AND the exact two
    addresses the call opened -- because a plausible number that nobody
    fetched is the failure this suite is arranged to make impossible.
    """
    page = _scripted([PROFILE_FIELDS, EXPERIENCE_CARDS])
    navigations = drive(page)

    result = await linkedin_my_profile(details="experience")

    assert result["pages_loaded"] == 2
    assert navigations == [PROFILE_ME_URL, EXPERIENCE_URL]
    assert navigations[1] == "https://www.linkedin.com/in/me/details/experience/"

    completeness = result["completeness"]
    assert completeness["experience_entries"] == len(EXPERIENCE_CARDS)
    assert "/details/experience/" in completeness["experience_entries_source"]
    assert page.evaluate_overrun is False


async def test_details_education_loads_that_page_and_fills_that_count(drive):
    """The same seam on the second section, and it is not a copy for symmetry.

    ``dom.PROFILE_DETAIL_ENTRY_HREF`` carries a DIFFERENT per-entry pattern for
    each section, measured one at a time rather than predicted from the skills
    one. A wiring that pointed both sections at the same address, or that
    filled the wrong completeness key, would still pass the experience test
    above.
    """
    page = _scripted([PROFILE_FIELDS, EDUCATION_CARDS])
    navigations = drive(page)

    result = await linkedin_my_profile(details="education")

    assert result["pages_loaded"] == 2
    assert navigations == [PROFILE_ME_URL, EDUCATION_URL]
    assert navigations[1] == "https://www.linkedin.com/in/me/details/education/"

    completeness = result["completeness"]
    assert completeness["education_entries"] == len(EDUCATION_CARDS)
    assert "/details/education/" in completeness["education_entries_source"]
    assert completeness["experience_entries"] is None
    assert page.evaluate_overrun is False


async def test_an_unknown_section_is_refused_before_anything_is_loaded(drive):
    """THE ASSERTION THAT MATTERS HERE IS THE EMPTY NAVIGATION LOG.

    The section name becomes part of an address, so an unrecognised one must
    never reach a navigation. Refusing it AFTER the profile page had loaded
    would return the same error dict and would still look correct -- while
    having spent a page load, and a browser round trip, finding out it was
    never going to answer. Only the log tells the two apart, so only the log is
    trusted here.
    """
    page = _scripted([PROFILE_FIELDS])
    navigations = drive(page)

    result = await linkedin_my_profile(details="nonsense")

    assert result["error"] == "bad_argument", result
    assert navigations == []
    assert page.gotos == []
    assert page.evaluations == []


async def test_details_wins_over_include_skills_and_the_result_says_so(drive):
    """Both arguments passed, one page-load budget, and no silent choice.

    Only one details page fits in this tool's two-page ceiling. A caller that
    passed both and got no skills with no explanation would conclude the skills
    read had broken, so the tool names what it dropped -- and the skills page
    must not appear in the log, which is the half that proves the note is
    describing something that actually happened.
    """
    page = _scripted([PROFILE_FIELDS, EXPERIENCE_CARDS])
    navigations = drive(page)

    result = await linkedin_my_profile(include_skills=True, details="experience")

    assert "include_skills_ignored" in result, sorted(result)
    assert "skills" in result["include_skills_ignored"]
    assert navigations == [PROFILE_ME_URL, EXPERIENCE_URL]
    assert SKILLS_URL not in navigations
    assert "skills" not in result


async def test_no_details_page_means_all_three_counts_are_named_as_unasked(
    drive,
):
    """THE CONTROL FOR PART 2, and it is the reason a null is now readable.

    Three nulls that cannot say why they are null is the exact misreading this
    tool invited for as long as it shipped: a caller reads null and concludes
    LinkedIn holds nothing. So the single-page call must return all three as
    null AND name all three as not-requested -- the naming is what turns a null
    from a claim about LinkedIn into a claim about this call.
    """
    page = _scripted([PROFILE_FIELDS])
    navigations = drive(page)

    result = await linkedin_my_profile(include_skills=False)

    assert result["pages_loaded"] == 1
    assert navigations == [PROFILE_ME_URL]

    completeness = result["completeness"]
    assert completeness["experience_entries"] is None
    assert completeness["education_entries"] is None
    assert completeness["skills_listed"] is None
    assert completeness["counts_not_requested"] == [
        "experience_entries",
        "education_entries",
        "skills_listed",
    ]
