"""Whether he already follows the employer, and the ways that goes wrong.

WHY THIS IS ASKED AT ALL. The follow question is never reported for its own
sake. It feeds a confirm gate, and a gate handed the wrong direction offers to
follow a company he already follows, or offers to unfollow one he does not --
silently, and with a plausible-looking answer, which is the worst kind. So the
reader is permitted to be wrong in exactly ONE way: by declining to answer.
Every assertion in this module is arranged around that asymmetry. A fact that
did not render must read as "could not tell", never as "no".

THREE READS, and one fixture pair each, because each read has its own way of
looking answered when it is not.

* THE FOLLOW CONTROL ON A POSTING. ``job_detail.html`` and
  ``job_detail_hydrated.html`` are a posting at a company he does NOT follow;
  ``job_detail_following.html`` and ``job_detail_following_hydrated.html`` are
  the same shape at one he DOES. The pre-settle half of the second pair is the
  reason that pair exists: the control has not rendered at all, and an absent
  control is not a direction.

* MANAGE PAGES. ``manage_pages_following.html`` renders TEN rows and
  ``manage_pages_following_hydrated.html`` renders TWENTY, both under a
  heading that says the account follows fifty-eight Pages. So the list is a
  third of itself at best, and nothing here is allowed to turn "absent from
  the rows I was shown" into "you do not follow them".

* OPEN TO WORK, on his own topcard. ``profile_topcard.html`` and
  ``profile_topcard_hydrated.html`` both carry ``Open to work`` and its
  AUDIENCE. The audience is the half that matters to someone job-hunting while
  employed: one setting is invisible to a current employer and the other draws a
  green frame on the photo for everybody including a current employer, so a gate
  that repeats LinkedIn's four words back at him has told him nothing.

THE ANCHORING RULE, and this is the surface that PROVES it rather than
restating it. The two states of the posting control carry byte-identical class
lists, and ``aria-pressed`` appears nowhere on either page: the accessible
name is the whole of the difference between "follows them" and "does not".
That is asserted below, not written down as a comment, because a comment
cannot notice LinkedIn changing its mind.

WHAT IS AND IS NOT PINNED. The company names, the Page ids and the locations
in these fixtures are invented, so none of them is typed into an assertion
here -- where a name is needed it is taken out of the parse at runtime. The
counts are the fixtures' real shape and ARE pinned: ten rows, twenty rows,
fifty-eight follows.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from linkedin_server import dom, shape

FIXTURE_DIR = Path(__file__).parent / "fixtures"

FIXTURES = {
    # A posting at a company he does NOT follow. The control says "Follow".
    "job_off": FIXTURE_DIR / "job_detail.html",
    "job_off_hydrated": FIXTURE_DIR / "job_detail_hydrated.html",
    # A posting at a company he DOES follow. The first has not settled and
    # draws no control at all, which is the trap.
    "job_on": FIXTURE_DIR / "job_detail_following.html",
    "job_on_hydrated": FIXTURE_DIR / "job_detail_following_hydrated.html",
    # Manage Pages, the same list before and after it settles.
    "pages": FIXTURE_DIR / "manage_pages_following.html",
    "pages_hydrated": FIXTURE_DIR / "manage_pages_following_hydrated.html",
    # His own profile topcard, both renders.
    "profile": FIXTURE_DIR / "profile_topcard.html",
    "profile_hydrated": FIXTURE_DIR / "profile_topcard_hydrated.html",
}

#: How many rows each render of Manage Pages actually drew, and what LinkedIn
#: itself says the total is. These three numbers ARE the hazard: ten of
#: fifty-eight, or twenty of fifty-eight, is why absence proves nothing.
ROWS_RENDERED = {"pages": 10, "pages_hydrated": 20}
TOTAL_FOLLOWED = 58

BOTH_PAGE_RENDERS = list(ROWS_RENDERED)
BOTH_PROFILES = ["profile", "profile_hydrated"]
BOTH_POSTINGS_SETTLED = ["job_off_hydrated", "job_on_hydrated"]

#: chr(0xB7) is the middle dot LinkedIn separates "Open to work" from its
#: audience with. Spelled this way so this file stays pure ASCII, as shape.py
#: and test_job_detail_fixture.py do.
DOT = chr(0xB7)

#: A Page invented FOR THIS MODULE, not taken from any fixture, so it is
#: absent from the rendered list by construction.
ABSENT_PAGE = "Nowhere Industries Ltd"


# ---------------------------------------------------------------------------
# The browser harness
# ---------------------------------------------------------------------------


async def _with_html(html: str, work):
    """Run ``work(page)`` over frozen markup in a LOCAL headless Chromium."""
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return await work(page)
        finally:
            await browser.close()


def markup(which: str) -> str:
    return FIXTURES[which].read_text(encoding="ascii")


async def _follow_control(which: str) -> dict:
    async def work(page):
        return await dom.read_follow_control(page)

    return await _with_html(markup(which), work)


async def _follow_state(which: str) -> tuple[dict, dict]:
    """The control as read, and the verdict the tool builds from it."""
    control = await _follow_control(which)
    verdict = shape.follow_state(
        control.get("label"), count=int(control.get("count") or 0)
    )
    return control, verdict


async def _follow_button_class(which: str):
    async def work(page):
        return await page.locator(dom.FOLLOW_CONTROL).first.get_attribute("class")

    return await _with_html(markup(which), work)


async def _followed_pages(which: str) -> dict:
    """The Manage-Pages read, exactly as the tool assembles it."""

    async def work(page):
        return shape.parse_followed_pages(
            await dom.harvest_followed_pages(page),
            await dom.read_main_text(page),
        )

    return await _with_html(markup(which), work)


async def _open_to_work(which: str) -> dict:
    """Open To Work, through the same three calls the profile tool makes."""

    async def work(page):
        fields = await dom.read_profile_fields(page)
        topcard = shape.pick_topcard(
            fields.get("sections") or [], fields.get("title")
        )
        return shape.parse_open_to_work((topcard or {}).get("lines") or [])

    return await _with_html(markup(which), work)


# ---------------------------------------------------------------------------
# 0. The fixtures themselves
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("which", list(FIXTURES))
def test_the_fixture_exists_and_is_pure_ascii(which):
    """Everything below reads these with ``encoding="ascii"``.

    Without this the failure for a fixture that picked up a real middle dot or
    a curly quote is a UnicodeDecodeError inside a browser harness, which
    names neither the file nor the reason.
    """
    path = FIXTURES[which]
    assert path.exists(), f"missing fixture: {path}"
    raw = path.read_bytes()
    assert raw, f"empty fixture: {path}"
    raw.decode("ascii")


# ---------------------------------------------------------------------------
# 1. The follow control on a posting, both directions, both renders
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "which, label, state",
    [
        ("job_off", "Follow", "not_following"),
        ("job_off_hydrated", "Follow", "not_following"),
        ("job_on_hydrated", "Following", "following"),
    ],
)
@pytest.mark.asyncio
async def test_a_settled_posting_states_its_follow_direction(which, label, state):
    """Both directions, read off the real control rather than off a sibling.

    The ON state had to be captured on THIS control: LinkedIn draws four
    different conventions for one concept ("Follow EXL" on a profile rail,
    "Click to stop following X" on Manage Pages, "Following, click to unfollow
    X" in Interests), so the bare "Following" here could not be inferred from
    any of them. Absent this test, the ON direction is an assumption.
    """
    control, verdict = await _follow_state(which)
    assert control["count"] == 1
    assert control["label"] == label
    assert verdict["state"] == state
    assert repr(label) in verdict["why"]


@pytest.mark.asyncio
async def test_a_posting_that_has_not_settled_refuses_to_say_not_following():
    """THE LOAD-BEARING ONE.

    The control has not rendered. Reading that absence as "he does not follow
    them" would hand the confirm gate the wrong direction on a company he DOES
    follow -- which is what this fixture pair is: the same posting, at an
    employer he follows, caught before it hydrated. The answer must be the
    refusal, and the refusal has to explain that it is about the RENDER rather
    than about the following, or a caller cannot tell it from a real "no".

    Its control is the second half of the pair, asserted here so that
    "unknown" cannot be coming from a reader that only ever says unknown.
    """
    control, verdict = await _follow_state("job_on")
    assert control["count"] == 0
    assert control["label"] is None
    assert verdict["state"] == "unknown"

    why = verdict["why"].casefold()
    assert "hydrat" in why, verdict["why"]
    assert "not evidence" in why, verdict["why"]
    assert "unfollow" in why, verdict["why"]

    _, settled = await _follow_state("job_on_hydrated")
    assert settled["state"] == "following"


def test_the_refusal_is_spelled_unknown():
    """Three callers have to agree that "could not tell" is a real answer.

    Pinned against the literal word rather than against the constant, since a
    test that compares the constant to itself would survive it being renamed
    to something a caller silently treats as falsy.
    """
    assert shape.FOLLOW_UNKNOWN == "unknown"


@pytest.mark.asyncio
async def test_the_two_states_differ_only_in_their_accessible_name():
    """The evidence for the anchoring rule, asserted instead of described.

    If the class list distinguished the two states, a reader could anchor on
    it, and the whole case for reading the accessible name would be a
    preference. It does not: the two buttons carry the same classes to the
    byte, and neither page carries ``aria-pressed`` anywhere. That is a fact
    about LinkedIn's markup, so it is checked rather than believed.
    """
    off = await _follow_button_class("job_off_hydrated")
    on = await _follow_button_class("job_on_hydrated")
    # Two missing attributes would also compare equal, which would make the
    # comparison below unable to fail. So the attribute has to be there first.
    assert off, "the follow control carries no class attribute at all"
    assert off == on

    for which in BOTH_POSTINGS_SETTLED:
        assert "aria-pressed" not in markup(which)


def test_an_unrecognised_label_is_refused_rather_than_guessed():
    """LinkedIn in French, or LinkedIn having renamed its own button.

    Either way the direction is not derivable, and picking one would be a coin
    toss reported as a reading. The two labels that HAVE been measured are
    asserted alongside it, so this cannot pass on a function that refuses
    everything.
    """
    verdict = shape.follow_state("Suivre", count=1)
    assert verdict["state"] == "unknown"
    assert "Suivre" in verdict["why"]

    assert shape.follow_state("Follow", count=1)["state"] == "not_following"
    assert shape.follow_state("Following", count=1)["state"] == "following"


def test_more_than_one_control_is_ambiguous_and_names_the_count():
    """Several follow controls means one of them belongs to something else.

    Taking the first would be taking it by position, which is the failure the
    whole reader is arranged against. The count goes into the reason because
    "the page had not rendered" and "there were three of them" want different
    responses from whoever reads it.
    """
    verdict = shape.follow_state("Follow", count=3)
    assert verdict["state"] == "unknown"
    assert "3" in verdict["why"]


# ---------------------------------------------------------------------------
# 2. Manage Pages, and the partial-list hazard
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("which", BOTH_PAGE_RENDERS)
@pytest.mark.asyncio
async def test_every_rendered_row_is_harvested(which):
    """Ten before the list settles, twenty after, off the same surface.

    The row is found by the accessible name of its button and its id by an
    XPath hop to the enclosing row -- nothing counts children or names a
    class. A count short of these means the hop or the anchor stopped
    matching, which is exactly the kind of drift that otherwise shows up as a
    quietly shorter list.
    """
    parsed = await _followed_pages(which)
    assert parsed["rendered"] == ROWS_RENDERED[which]
    assert len(parsed["pages"]) == ROWS_RENDERED[which]


@pytest.mark.parametrize("which", BOTH_PAGE_RENDERS)
@pytest.mark.asyncio
async def test_the_read_reports_linkedins_total_and_admits_it_is_short(which):
    """LinkedIn's own number is the only thing that makes the gap visible.

    Without it the list is just a list, and twenty rows look like twenty
    follows. With it the read can say it covers twenty of fifty-eight, which
    is what every refusal below is built on.
    """
    parsed = await _followed_pages(which)
    assert parsed["total_followed"] == TOTAL_FOLLOWED
    assert parsed["complete"] is False
    assert parsed["rendered"] < parsed["total_followed"]
    assert parsed["why_incomplete"]


@pytest.mark.parametrize("which", BOTH_PAGE_RENDERS)
@pytest.mark.asyncio
async def test_a_page_that_did_render_is_answered_following(which):
    """The positive direction, so the refusals are not the only answer given.

    The name is lifted out of the parse rather than typed in, because the
    fixtures' company names are invented and may be reinvented.
    """
    parsed = await _followed_pages(which)
    name = parsed["pages"][0]["name"]
    verdict = shape.followed_page_state(name, parsed)
    assert verdict["state"] == "following"
    assert verdict["matched"]["name"] == name
    assert repr(name) in verdict["why"]


@pytest.mark.parametrize("which", BOTH_PAGE_RENDERS)
@pytest.mark.asyncio
async def test_a_page_absent_from_a_partial_list_is_unknown_not_unfollowed(which):
    """THE MOST IMPORTANT TEST IN THIS FILE.

    Thirty-eight of his follows were never rendered. A reader that answered
    "not following" from this list would be answering it about them, and would
    be answering it to a confirm gate -- which would then offer to follow a
    company he already follows. The refusal has to name the incompleteness
    too: "absent" is only a defensible non-answer if the caller can see WHY it
    is not an answer.
    """
    parsed = await _followed_pages(which)
    names = {str(page["name"]).casefold() for page in parsed["pages"]}
    assert ABSENT_PAGE.casefold() not in names, (
        "this test needs a name the list does not contain; the fixture now "
        "contains it"
    )

    verdict = shape.followed_page_state(ABSENT_PAGE, parsed)
    assert verdict["state"] == "unknown"
    assert verdict["matched"] is None

    why = verdict["why"]
    assert "does not cover the whole list" in why.casefold(), why
    assert "not evidence" in why.casefold(), why
    assert str(parsed["total_followed"]) in why, why
    assert str(parsed["rendered"]) in why, why


def test_the_same_question_is_answered_no_once_the_list_is_complete():
    """The control for the test above, and it is not optional.

    Without it, that "unknown" passes just as happily on a function that can
    only ever say unknown -- which fails the other way round: he would never
    be told he does NOT follow somebody, and the gate would be as stuck as if
    it had been lied to. So the same query goes to a list that covers
    everything, and comes back not_following.

    The list is built here rather than taken from a fixture: no capture of
    this surface is complete, which is the point of the surface.
    """
    complete = {
        "pages": [{"name": "Aldergate Works", "id": "1"}],
        "rendered": 1,
        "total_followed": 1,
        "complete": True,
        "why_incomplete": None,
    }
    verdict = shape.followed_page_state(ABSENT_PAGE, complete)
    assert verdict["state"] == "not_following"
    assert verdict["matched"] is None
    assert "covers completely" in verdict["why"].casefold(), verdict["why"]

    # And the lookup still works on this hand-built list, so the answer above
    # is a real absence rather than a match that never ran.
    present = shape.followed_page_state("Aldergate Works", complete)
    assert present["state"] == "following"


@pytest.mark.parametrize("which", BOTH_PAGE_RENDERS)
@pytest.mark.asyncio
async def test_every_row_yields_a_name_and_some_row_yields_an_id(which):
    """The name is the answer; the id is the corroboration.

    A row keeps its name even when its link cannot be read, so a broken XPath
    hop does not shorten the list -- it silently empties the ids instead, and
    the ``any`` below is the only place that shows up.
    """
    parsed = await _followed_pages(which)
    assert parsed["pages"]
    for page in parsed["pages"]:
        name = page["name"]
        assert name, f"a row parsed with no name: {page}"
        assert name.strip() == name, f"a row kept its whitespace: {page}"
        assert (
            "Click to stop following" not in name
        ), f"the button label leaked into the name: {page}"
    assert any(page["id"] for page in parsed["pages"]), (
        "no row produced an id, so the XPath hop to the enclosing row found "
        "no company link on any of them"
    )


# ---------------------------------------------------------------------------
# 3. Open To Work, where the audience is the fact
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("which", BOTH_PROFILES)
@pytest.mark.asyncio
async def test_open_to_work_and_its_audience_survive_both_renders(which):
    """Hydration timing must not change which of the two settings he is told.

    "On" alone is not the fact. The two audiences differ by whether his
    employer can see it, so an audience that survives one render and not the
    other is a gate that is right half the time.
    """
    got = await _open_to_work(which)
    assert got["on"] is True
    assert got["audience"] == "Recruiters only"


@pytest.mark.asyncio
async def test_the_audience_is_reported_as_who_can_see_it():
    """A gate for someone job-hunting while employed has to say who can see it.

    Repeating LinkedIn's own four words back at him is not that. So the
    recruiters-only setting is reported as NOT public, the all-members setting
    is reported as public AND as visible to a current employer, and the two readings
    are not the same string.
    """
    got = await _open_to_work("profile_hydrated")
    quiet = got["who_can_see_it"]
    assert "public" not in quiet.casefold(), quiet
    assert "employer" in quiet.casefold(), quiet

    loud = shape.OPEN_TO_WORK_AUDIENCES["all linkedin members"]
    assert "PUBLIC" in loud, loud
    assert "employer" in loud.casefold(), loud
    assert quiet != loud


@pytest.mark.parametrize("lines", [[], ["something else"]])
def test_a_card_that_did_not_draw_reports_none_and_never_false(lines):
    """``None`` and ``False`` are different claims and only one is available.

    ``False`` would be a statement that he is not sharing his job hunt. A page
    whose topcard did not render is not entitled to make it -- and the two are
    indistinguishable to any caller written as ``if not on:``, which is
    exactly why the distinction is asserted by identity here.
    """
    got = shape.parse_open_to_work(lines)
    assert got["on"] is None
    assert got["audience"] is None
    assert "not the same as it being off" in got["who_can_see_it"].casefold()


def test_the_readers_whole_vocabulary_for_on_is_true_or_none():
    """The control for the test above: ``on`` is never the third value.

    Asserted as a set over a read that succeeds and two that do not, so a
    reader that started answering ``False`` for an unread card fails here even
    if somebody loosened the identity checks above.
    """
    seen = {
        shape.parse_open_to_work(lines)["on"]
        for lines in ([], ["something else"], [f"Open to work {DOT} Recruiters only"])
    }
    assert seen == {None, True}


def test_an_unrecognised_audience_says_so_instead_of_guessing():
    """LinkedIn adding a third audience must not be read as one of the two.

    The state is still reported as on, because the line was there and it said
    so. What is refused is the consequence -- who can see it -- since that is
    the half a decision would be made on.
    """
    got = shape.parse_open_to_work([f"Open to work {DOT} My network only"])
    assert got["on"] is True
    assert got["audience"] == "My network only"
    assert "UNRECOGNISED" in got["who_can_see_it"]

    # The control: a measured audience still gets its real reading.
    known = shape.parse_open_to_work([f"Open to work {DOT} Recruiters only"])
    assert "UNRECOGNISED" not in known["who_can_see_it"]
