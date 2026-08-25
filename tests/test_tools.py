"""Driving the tools end to end, with no browser and no LinkedIn.

``tests/test_shape.py`` proves the parsers turn card text into rows. This file
proves the TOOLS do: that a page of harvested records comes back as a shaped
envelope, and -- the part that matters more -- that the three ways a read can
go wrong are reported as three DIFFERENT things. A bounce to the signed-out
wall is ``not_authenticated``. A page that rendered nothing readable is
``extraction_failed``. A limit that trimmed the list says so in ``capped``.

An empty list that is really a failure is the specific lie this suite exists
to make impossible, so several tests below assert on the NAVIGATION LOG as
well as on the answer: a tool can return a perfectly plausible envelope
without ever having asked LinkedIn anything, and only the log tells them
apart.

Nothing here launches Chromium. The ``drive`` fixture replaces both halves of
the browser a tool touches -- ``BROWSER.session``, which hands it a page, and
``BROWSER.goto``, which turns a target url into a FINAL url. That final url is
the whole auth story: LinkedIn answers a signed-out request with a redirect,
so a fake that ignored redirects could not express the failure being tested.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, Optional

import pytest

from linkedin_server import browser as browser_module
from linkedin_server.config import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    NOTIFICATIONS_DEFAULT_LIMIT,
    NOTIFICATIONS_MAX_LIMIT,
    SEARCH_DEFAULT_LIMIT,
    SEARCH_MAX_LIMIT,
)
from linkedin_server.server import (
    linkedin_my_applications,
    linkedin_my_profile,
    linkedin_notifications,
    linkedin_followed_companies,
    linkedin_saved_jobs,
    linkedin_search_jobs,
    linkedin_who_viewed_me,
)
from tests.conftest import FakePage


# ---------------------------------------------------------------------------
# The urls each tool is expected to open, written out so that a test asserts
# on a literal rather than on the same f-string the server built.
# ---------------------------------------------------------------------------

ANALYTICS_VIEWS_URL = "https://www.linkedin.com/analytics/profile-views/"
CLASSIC_VIEWS_URL = "https://www.linkedin.com/me/profile-views/"
#: /my-items/saved-jobs/ now redirects here and drops its query string, and the
#: tracker's tabs are client-side radios with no urls of their own -- ?stage=
#: is the only address a given list has.
APPLIED_URL = "https://www.linkedin.com/jobs-tracker/?stage=applied"
SAVED_URL = "https://www.linkedin.com/jobs-tracker/?stage=saved"

#: The tracker's tab strip, as ``page.inner_text("main")`` returns it. The
#: counts are what let an empty list be told apart from a failed read, so a
#: test about emptiness sets this and a test about rows mostly need not.
TRACKER_TABS = "\n".join(
    [
        "Job tracker",
        "Saved " + chr(0xB7) + " 3",
        "In Progress " + chr(0xB7) + " 1",
        "Applied " + chr(0xB7) + " 2",
        "Interview " + chr(0xB7) + " 0",
        "Archived",
        "Date posted",
    ]
)
TRACKER_ALL_EMPTY = "\n".join(
    [
        "Job tracker",
        "Saved " + chr(0xB7) + " 0",
        "In Progress " + chr(0xB7) + " 1",
        "Applied " + chr(0xB7) + " 0",
        "Interview " + chr(0xB7) + " 0",
        "Archived",
        "Date posted",
        "No jobs here",
    ]
)
NOTIFICATIONS_URL = "https://www.linkedin.com/notifications/"
PROFILE_ME_URL = "https://www.linkedin.com/in/me/"
PROFILE_RESOLVED_URL = "https://www.linkedin.com/in/alex-r/"
SKILLS_URL = "https://www.linkedin.com/in/alex-r/details/skills/"
AUTHWALL_URL = "https://www.linkedin.com/login?session_redirect=%2Ffeed"


# ---------------------------------------------------------------------------
# Fakes that conftest does not have to carry
# ---------------------------------------------------------------------------


class ScriptedPage(FakePage):
    """A FakePage with a per-call ``evaluate`` queue and per-url redirects.

    Two tools load two pages in one call -- ``linkedin_who_viewed_me`` when it
    falls back, and ``linkedin_my_profile`` when it fetches skills -- so the
    single ``evaluate_result`` in conftest cannot express them: the whole point
    of the fallback is that the two page loads answer DIFFERENTLY.

    ``redirect_map`` is here for the same reason. ``/in/me/`` really does
    redirect to the signed-in member's slug, and the server needs that slug to
    build the skills url, so a fake that returned the requested url unchanged
    would leave the second page load untestable.
    """

    def __init__(
        self,
        *,
        evaluate_queue: Optional[list] = None,
        redirect_map: Optional[dict] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self._queue = list(evaluate_queue or [])
        self.redirect_map = dict(redirect_map or {})
        #: True once the queue ran dry, which means the tool evaluated more
        #: times than the test expected. Recorded rather than raised: the
        #: harvesters wrap every exception out of evaluate() into
        #: ExtractionFailedError, so a raise here would come back disguised as
        #: a server failure and blame the wrong file.
        self.evaluate_overrun = False

    async def goto(self, url: str, **kwargs: Any) -> None:
        self.gotos.append(url)
        self.url = self.redirect_map.get(url, self.redirect_to or url)

    async def evaluate(self, script: str, arg: Any = None) -> Any:
        self.evaluations.append((script, arg))
        if not self._queue:
            self.evaluate_overrun = True
            return []
        item = self._queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


@pytest.fixture
def drive(monkeypatch):
    """Point BROWSER at a FakePage instead of at Chromium.

    Returns a callable: hand it the page, get back the list that will hold
    every url the tool navigates to, in order.
    """
    navigations: list[str] = []

    def install(page: FakePage) -> list[str]:
        @asynccontextmanager
        async def fake_session():
            yield page

        async def fake_goto(target_page, url, **kwargs):
            navigations.append(url)
            await target_page.goto(url)
            return target_page.url

        monkeypatch.setattr(browser_module.BROWSER, "session", fake_session)
        monkeypatch.setattr(browser_module.BROWSER, "goto", fake_goto)
        return navigations

    return install


async def _call(tool, **kwargs):
    """Call a tool, supplying the one argument search cannot do without."""
    if tool is linkedin_search_jobs:
        kwargs.setdefault("keywords", "node.js engineer")
    return await tool(**kwargs)


# ---------------------------------------------------------------------------
# Card fixtures.
#
# Every text below is shaped like real LinkedIn innerText, duplicated lines
# included: LinkedIn renders most labels twice, once visually and once in a
# screen-reader span, and a fixture without the echo would be testing a page
# that does not exist.
# ---------------------------------------------------------------------------

PERSON_CARD = {
    "href": "/in/priya-raman-123/?miniProfileUrn=urn%3Ali%3Afsd_profile%3AACoAAA",
    "text": (
        "Priya Raman\n"
        "Priya Raman\n"
        "Engineering Manager at Razorpay | Hiring backend engineers\n"
        "Riverton, Fairhaven, United States\n"
        "2 days ago"
    ),
}

ANONYMOUS_PERSON_CARD = {
    "href": "/in/ACoAAB7hidden/",
    "text": (
        "LinkedIn Member\n"
        "LinkedIn Member\n"
        "Someone at a staffing and recruiting company\n"
        "1 week ago"
    ),
}

APPLIED_CARD = {
    "href": "/jobs/view/senior-backend-engineer-at-razorpay-4123456789?refId=xY",
    "text": (
        "Senior Backend Engineer\n"
        "Senior Backend Engineer\n"
        "Razorpay\n"
        "Riverton, Fairhaven, United States (Hybrid)\n"
        "Applied 3 days ago"
    ),
}

SAVED_CARD = {
    "href": "/jobs/view/staff-software-engineer-at-zeta-4098765432?refId=Qp",
    "text": (
        "Staff Software Engineer\n"
        "Staff Software Engineer\n"
        "Zeta\n"
        "Riverton, Fairhaven, United States (Remote)\n"
        "Easy Apply\n"
        "2 weeks ago"
    ),
}

SEARCH_CARD = {
    "href": "/jobs/view/senior-node-js-developer-at-postman-4111222333",
    "text": (
        "Senior Node.js Developer\n"
        "Senior Node.js Developer\n"
        "Postman\n"
        "Riverton, Fairhaven, United States (Remote)\n"
        "Promoted\n"
        "Easy Apply"
    ),
}

NOTIFICATION_CARD = {
    "href": "/jobs/view/senior-backend-engineer-at-razorpay-4123456789/?refId=nT",
    "text": (
        "Razorpay\n"
        "Razorpay\n"
        "Your application was viewed by Razorpay\n"
        "2 hours ago"
    ),
    "selector": "article.nt-card",
}

#: A notification whose body carries its own timestamp INLINE. Dropping that
#: whole line to avoid repeating the time would throw the notification away,
#: which is the distinction shape.is_timestamp_line exists to draw.
NOTIFICATION_CARD_INLINE_TIME = {
    "href": "",
    "text": (
        "Your application to Zeta was viewed today\n"
        "Your application to Zeta was viewed today\n"
        "5 hours ago"
    ),
    "selector": "article.nt-card",
}

#: A card holding nothing but interface chrome. Harvested, unparseable, and so
#: countable -- it has to show up as a dropped row, not as a blank result row.
CHROME_ONLY_CARD = {
    "href": "/jobs/view/ghost-role-at-nowhere-4000111222",
    "text": "Easy Apply\nPromoted\nSave",
}


def saved_job_card(n: int) -> dict:
    """One more saved-job card, distinct from its neighbours."""
    job_id = 4100000000 + n
    title = f"Backend Engineer {n}"
    return {
        "href": f"/jobs/view/backend-engineer-{n}-at-acme-{job_id}?refId=r{n}",
        "text": "\n".join(
            [
                title,
                title,
                "Acme Corp",
                "Riverton, Fairhaven, United States (Remote)",
                "2 weeks ago",
            ]
        ),
    }


#: The profile page as ``READ_PROFILE_JS`` now returns it: a list of sections,
#: each a heading plus its own lines. There is no ``name`` field to read any
#: more, because the page carries no h1 and no section ids -- see that script's
#: note. The topcard lines are in the order LinkedIn draws them, PRONOUNS AND
#: ALL, because the pronoun line sits exactly where a headline would and is the
#: reason the headline is chosen by what a line is rather than where it sits.
PROFILE_FIELDS = {
    "url": PROFILE_RESOLVED_URL,
    "title": "Alex R | LinkedIn",
    "has_main": True,
    "sections": [
        {
            "heading": "Alex R",
            "lines": [
                "Alex R",
                "He/Him",
                "Senior Node.js Engineer | TypeScript | AWS",
                "Riverton, Fairhaven, United States",
                chr(0xB7),
                "Contact info",
                "Indian Institute of Information Technology",
                "268 connections",
                "Open to",
                "Add section",
            ],
            "images": 1,
        },
        {
            "heading": "Analytics",
            "lines": ["Analytics", "Private to you", "27 profile views"],
            "images": 0,
        },
        {
            "heading": "About",
            "lines": [
                "About",
                "I build backend services in Node.js and TypeScript.",
            ],
            "images": 0,
        },
        {"heading": "Featured", "lines": ["Featured", "Link"], "images": 0},
    ],
}

#: The skills page, as the LINK-anchored harvest now returns it. Each entry is
#: keyed on the inline edit affordance LinkedIn hangs off every skill, which is
#: the only per-skill key the page has. The old selector, ``main ul li``, found
#: the three filter pills and this tool reported them as his skills.
SKILL_CARDS = [
    {
        "href": "/in/alex-r/details/skills/edit/forms/11/",
        "text": "Node.js\nNode.js\n15 endorsements",
    },
    {
        "href": "/in/alex-r/details/skills/edit/forms/12/",
        "text": "TypeScript\nTypeScript\nEndorsed by 3 colleagues",
    },
    {
        "href": "/in/alex-r/details/skills/edit/forms/13/",
        "text": "PostgreSQL\nPostgreSQL",
    },
    # The same skill again: the skills page repeats entries across its
    # sections, and a repeat must not become a second row.
    {
        "href": "/in/alex-r/details/skills/edit/forms/14/",
        "text": "Node.js\nNode.js\n15 endorsements",
    },
    # A structural entry holding no text at all.
    {"href": "/in/alex-r/details/skills/edit/forms/15/", "text": "   \n  "},
    {"href": "/in/alex-r/details/skills/edit/forms/16/", "text": "AWS\nAWS"},
    {"href": "/in/alex-r/details/skills/edit/forms/17/", "text": "Docker\nDocker"},
    {"href": "/in/alex-r/details/skills/edit/forms/18/", "text": "Redis\nRedis"},
]


# ---------------------------------------------------------------------------
# 1. Happy path, per list tool
# ---------------------------------------------------------------------------


async def test_profile_views_carry_name_headline_and_when_it_happened(drive):
    page = FakePage(evaluate_result=[PERSON_CARD])
    navigations = drive(page)

    result = await linkedin_who_viewed_me(limit=25)

    assert result["results"] == [
        {
            "name": "Priya Raman",
            "headline": "Engineering Manager at Razorpay | Hiring backend engineers",
            "viewed": "2 days ago",
            "anonymous": False,
            "profile": "https://www.linkedin.com/in/priya-raman-123",
        }
    ]
    assert navigations == [ANALYTICS_VIEWS_URL]
    assert result["source_url"] == ANALYTICS_VIEWS_URL


async def test_an_anonymous_viewer_is_flagged_and_given_no_link(drive):
    """LinkedIn shows private-mode viewers as anonymous rows. So does this."""
    page = FakePage(evaluate_result=[PERSON_CARD, ANONYMOUS_PERSON_CARD])
    drive(page)

    result = await linkedin_who_viewed_me()

    hidden = result["results"][1]
    assert hidden["anonymous"] is True
    assert hidden["name"] == "LinkedIn Member"
    assert hidden["viewed"] == "1 week ago"
    assert "profile" not in hidden, "an anonymous viewer must not get a link"
    assert result["results"][0]["anonymous"] is False


async def test_applied_jobs_carry_the_status_linkedin_displays(drive):
    page = FakePage(evaluate_result=[APPLIED_CARD])
    navigations = drive(page)

    result = await linkedin_my_applications(limit=25)

    assert result["results"] == [
        {
            "title": "Senior Backend Engineer",
            "company": "Razorpay",
            "location": "Riverton, Fairhaven, United States (Hybrid)",
            "status": "applied",
            "when": "3 days ago",
            "job_id": "4123456789",
            "url": "https://www.linkedin.com/jobs/view/4123456789",
        }
    ]
    assert navigations == [APPLIED_URL]


async def test_saved_jobs_have_no_status_and_keep_title_company_location(drive):
    page = FakePage(evaluate_result=[SAVED_CARD])
    navigations = drive(page)

    result = await linkedin_saved_jobs(limit=25)

    row = result["results"][0]
    assert row["title"] == "Staff Software Engineer"
    assert row["company"] == "Zeta"
    assert row["location"] == "Riverton, Fairhaven, United States (Remote)"
    assert row["when"] == "2 weeks ago"
    assert row["job_id"] == "4098765432"
    assert "status" not in row, "a saved job was never applied to"
    assert navigations == [SAVED_URL]


# ---------------------------------------------------------------------------
# 1b. The tracker's two kinds of zero
# ---------------------------------------------------------------------------
#
# Both lists were genuinely EMPTY when this surface was first read live
# (Saved 0, Applied 0), so "rows came back" cannot be the success signal here.
# What can be checked is that the two zeros are told apart, and these are the
# tests that check it.


async def test_a_corroborated_empty_list_is_a_result_not_an_error(drive):
    """Nothing saved, and LinkedIn's own tab agrees. That is an answer."""
    page = FakePage(evaluate_result=[])
    page.inner_text_result = TRACKER_ALL_EMPTY
    navigations = drive(page)

    result = await linkedin_saved_jobs(limit=25)

    assert "error" not in result, result
    assert result["results"] == []
    assert result["count"] == 0
    assert result["empty"] is True
    assert result["linkedin_count"] == 0
    assert result["empty_state"] == "No jobs here"
    assert result["tab"] == "Saved"
    assert result["tab_counts"]["in_progress"] == 1
    assert "not a failed read" in result["note"]
    assert navigations == [SAVED_URL]
    assert page.inner_text_calls == ["main"], "the tab strip has to be read"


async def test_an_uncorroborated_empty_list_is_still_an_error(drive):
    """LinkedIn says two. Nothing parsed. Reporting [] would be the lie."""
    page = FakePage(evaluate_result=[])
    page.inner_text_result = TRACKER_TABS
    drive(page)

    result = await linkedin_my_applications(limit=25)

    assert result["error"] == "extraction_failed", result
    assert "Applied tab says 2" in result["message"]
    assert "results" not in result
    assert "count" not in result


async def test_followed_companies_reports_a_failed_read_as_a_failure(drive):
    """THE SAME RULE ON A SECOND SURFACE, and the half the first cut got wrong.

    The first version of this tool raised when LinkedIn's heading said a
    positive number and no row parsed -- and returned a cheerful empty list
    when the page drew NOTHING AT ALL, no rows and no heading either. That is
    the more likely failure of the two, because a page that never rendered has
    no count left to contradict. An empty list there is indistinguishable from
    him following nobody, which is the exact confusion `_read_tracker` exists
    to prevent one surface over.
    """
    page = FakePage(evaluate_result=[])
    page.inner_text_result = ""
    drive(page)

    result = await linkedin_followed_companies()

    assert result["error"] == "extraction_failed", result
    assert "NOR its own" in result["message"]
    assert "pages" not in result


async def test_followed_companies_reports_a_corroborated_zero_as_an_answer(drive):
    """THE CONTROL. Without it the refusal above passes on a tool that has
    simply lost the ability to return an empty list at all -- and following
    nobody is a real state, not an error."""
    page = FakePage(evaluate_result=[])
    page.inner_text_result = "Manage Pages 0 Pages"
    drive(page)

    result = await linkedin_followed_companies(company="Ashgrove Systems")

    assert "error" not in result, result
    assert result["pages"] == []
    assert result["rendered"] == 0
    assert result["total_followed"] == 0
    # A zero LinkedIn itself STATES is a complete list, so a question about any
    # Page can now be answered "no" rather than "unknown". This is the only
    # shape of empty result in which that is true, which is why the two tests
    # around it are worth having separately.
    assert result["complete"] is True
    assert result["follow_state"]["state"] == "not_following"
    assert "why_incomplete" not in result


async def test_followed_companies_says_unknown_not_no_off_a_partial_list(drive):
    """The partial-list hazard, at the TOOL boundary rather than the parser's.

    LinkedIn renders twenty rows under a heading saying 58. Asking about a Page
    that is not among the twenty must come back `unknown`: he may well follow
    them, on a row this read was never shown.
    """
    page = FakePage(evaluate_result=[])
    page.inner_text_result = "Manage Pages 58 Pages"
    drive(page)

    # No rows parse off a FakePage, so this exercises the strictest case: a
    # heading that says 58 with nothing under it is a FAILED read, not a "no".
    result = await linkedin_followed_companies(company="Ashgrove Systems")

    assert result["error"] == "extraction_failed", result
    assert "58 Pages" in result["message"] or "58" in result["message"]


async def test_an_empty_list_with_no_readable_tab_strip_is_an_error(drive):
    """No count to corroborate with, so the zero cannot be believed."""
    page = FakePage(evaluate_result=[])
    page.inner_text_result = ""
    drive(page)

    result = await linkedin_saved_jobs(limit=25)

    assert result["error"] == "extraction_failed", result
    assert "count could not be read" in result["message"]


async def test_rows_are_reported_alongside_linkedins_own_count(drive):
    page = FakePage(evaluate_result=[SAVED_CARD])
    page.inner_text_result = TRACKER_TABS
    drive(page)

    result = await linkedin_saved_jobs(limit=25)

    assert result["empty"] is False
    assert result["count"] == 1
    assert result["linkedin_count"] == 3
    assert result["tab_counts"] == {
        "saved": 3,
        "in_progress": 1,
        "applied": 2,
        "interview": 0,
    }
    # One page load, no scrolling: the shortfall is explained, not hidden.
    assert "does not scroll" in result["note"]


async def test_a_full_read_is_not_annotated_with_a_shortfall(drive):
    """The shortfall note, shown NOT firing. A note that always fires is noise."""
    page = FakePage(evaluate_result=[saved_job_card(n) for n in range(3)])
    page.inner_text_result = TRACKER_TABS
    drive(page)

    result = await linkedin_saved_jobs(limit=25)

    assert result["count"] == 3
    assert result["linkedin_count"] == 3
    assert "note" not in result


async def test_more_rows_than_linkedin_counts_is_flagged_as_a_disagreement(drive):
    """The mirror of the empty case, and the same symptom.

    The reconciliation was one-sided at first: it raised on too FEW rows and
    said nothing about too many. But a walk that overshoots its row does not
    return nothing -- it returns page furniture wearing a job's shape, which is
    exactly how this surface broke. Five rows where LinkedIn counts two is that
    symptom.
    """
    page = FakePage(evaluate_result=[saved_job_card(n) for n in range(5)])
    page.inner_text_result = TRACKER_TABS.replace(
        "Saved " + chr(0xB7) + " 3", "Saved " + chr(0xB7) + " 2"
    )
    drive(page)

    result = await linkedin_saved_jobs(limit=25)

    assert result["count"] == 5
    assert result["linkedin_count"] == 2
    assert "DISAGREEMENT" in result["note"]
    assert "with suspicion" in result["note"]


async def test_a_search_result_is_shaped_like_the_other_job_rows(drive):
    page = FakePage(evaluate_result=[SEARCH_CARD])
    navigations = drive(page)

    result = await linkedin_search_jobs(keywords="node.js engineer", limit=25)

    assert result["results"] == [
        {
            "title": "Senior Node.js Developer",
            "company": "Postman",
            "location": "Riverton, Fairhaven, United States (Remote)",
            "job_id": "4111222333",
            "url": "https://www.linkedin.com/jobs/view/4111222333",
        }
    ]
    assert navigations == [
        "https://www.linkedin.com/jobs/search/?keywords=node.js+engineer"
    ]


async def test_a_notification_keeps_a_body_that_contains_its_own_timestamp(drive):
    page = FakePage(evaluate_result=[NOTIFICATION_CARD, NOTIFICATION_CARD_INLINE_TIME])
    navigations = drive(page)

    result = await linkedin_notifications(limit=20)

    assert result["results"][0] == {
        "text": "Razorpay Your application was viewed by Razorpay",
        "when": "2 hours ago",
        "link": (
            "https://www.linkedin.com/jobs/view/"
            "senior-backend-engineer-at-razorpay-4123456789/"
        ),
    }
    inline = result["results"][1]
    # The line that IS the timestamp is dropped; the line that merely contains
    # one is kept whole. find_time_ago returns the first relative time it sees
    # scanning top down, which here is the inline "today".
    assert inline["text"] == "Your application to Zeta was viewed today"
    assert inline["when"] == "today"
    assert "link" not in inline, "a notification with no anchor gets no link"
    assert navigations == [NOTIFICATIONS_URL]


async def test_the_envelope_reports_every_honesty_field(drive):
    """count, page_had, capped, limit, pages_loaded, source_url, results."""
    page = FakePage(evaluate_result=[SAVED_CARD])
    drive(page)

    result = await linkedin_saved_jobs(limit=25)

    assert result["count"] == 1
    assert result["page_had"] == 1
    assert result["capped"] is False
    assert result["limit"] == 25
    assert result["pages_loaded"] == 1
    assert result["source_url"] == SAVED_URL
    assert len(result["results"]) == 1
    assert "unparsed_rows" not in result, "nothing was dropped, so say nothing"
    assert "error" not in result


async def test_cards_that_could_not_be_parsed_are_counted_not_hidden(drive):
    page = FakePage(evaluate_result=[SAVED_CARD, CHROME_ONLY_CARD, saved_job_card(7)])
    drive(page)

    result = await linkedin_saved_jobs(limit=25)

    assert result["count"] == 2
    assert result["unparsed_rows"] == 1
    # page_had counts the CARDS the page held (3), not just the ones that
    # parsed (2). Counting only the parsed ones would let a full page report
    # capped: false and read as "you have reached the end of the list".
    assert result["page_had"] == 3


# ---------------------------------------------------------------------------
# 2. The cap is reported, never silent
# ---------------------------------------------------------------------------


async def test_a_cap_is_always_reported_never_silent(drive):
    """Five results must never be mistakable for "five results exist"."""
    page = FakePage(evaluate_result=[saved_job_card(n) for n in range(40)])
    drive(page)

    result = await linkedin_saved_jobs(limit=5)

    assert result["count"] == 5
    assert result["page_had"] == 40
    assert result["capped"] is True
    assert result["limit"] == 5
    assert len(result["results"]) == 5


async def test_a_list_that_fits_under_the_limit_is_not_reported_as_capped(drive):
    """capped, shown NOT firing. A flag that is always true says nothing."""
    page = FakePage(evaluate_result=[saved_job_card(n) for n in range(4)])
    drive(page)

    result = await linkedin_saved_jobs(limit=5)

    assert result["count"] == 4
    assert result["page_had"] == 4
    assert result["capped"] is False


async def test_a_page_holding_exactly_the_limit_is_not_capped(drive):
    page = FakePage(evaluate_result=[saved_job_card(n) for n in range(5)])
    drive(page)

    result = await linkedin_saved_jobs(limit=5)

    assert result["count"] == 5
    assert result["capped"] is False


async def test_the_notification_cap_is_reported_too(drive):
    page = FakePage(evaluate_result=[NOTIFICATION_CARD] * 30)
    drive(page)

    result = await linkedin_notifications(limit=4)

    assert result["count"] == 4
    assert result["page_had"] == 30
    assert result["capped"] is True


# ---------------------------------------------------------------------------
# 3. An auth-wall bounce is a refusal, not an empty list
# ---------------------------------------------------------------------------

AUTHWALL_TOOLS = {
    "who_viewed_me": linkedin_who_viewed_me,
    "my_applications": linkedin_my_applications,
    "saved_jobs": linkedin_saved_jobs,
    "search_jobs": linkedin_search_jobs,
    "notifications": linkedin_notifications,
    "my_profile": linkedin_my_profile,
}


@pytest.mark.parametrize("name", sorted(AUTHWALL_TOOLS))
async def test_an_auth_wall_bounce_is_not_authenticated_not_an_empty_list(drive, name):
    page = FakePage(evaluate_result=[])
    page.redirect_to = AUTHWALL_URL
    navigations = drive(page)

    result = await _call(AUTHWALL_TOOLS[name])

    assert result["error"] == "not_authenticated", result
    # THE NAME IN THAT REFUSAL CHANGED ON 2026-08-25, from
    # ``linkedin_login_browser`` to ``linkedin_login``. The old spelling is
    # still a registered tool -- a deprecated alias that forwards, covered in
    # ``test_server_surface.py`` -- so this is not a dead name; it is the wrong
    # one to print. A refusal is the moment a caller is most likely to copy a
    # tool name straight out of the message, which is why the six read tools
    # above are all held to naming the canonical one.
    #
    # Asserted in both directions because ``linkedin_login`` is a substring of
    # ``linkedin_login_browser``: the positive check alone cannot fail on the
    # pre-rename message and would certify nothing.
    assert "linkedin_login" in result["message"]
    assert "linkedin_login_browser" not in result["message"]
    assert AUTHWALL_URL in result["message"]
    assert "results" not in result, "a refusal must not look like a result set"
    assert len(navigations) == 1, "the bounce must stop the call, not retry it"


async def test_the_authwall_check_does_not_fire_on_an_ordinary_page(drive):
    """The auth check, shown NOT firing -- otherwise it could be a constant."""
    page = FakePage(evaluate_result=[SAVED_CARD])
    drive(page)

    result = await linkedin_saved_jobs()

    assert "error" not in result


# ---------------------------------------------------------------------------
# 4. An empty page is a failure, except where it legitimately is not
# ---------------------------------------------------------------------------

EMPTY_IS_AN_ERROR = {
    "who_viewed_me": (linkedin_who_viewed_me, CLASSIC_VIEWS_URL),
    "my_applications": (linkedin_my_applications, APPLIED_URL),
    "saved_jobs": (linkedin_saved_jobs, SAVED_URL),
    "notifications": (linkedin_notifications, NOTIFICATIONS_URL),
}


@pytest.mark.parametrize("name", sorted(EMPTY_IS_AN_ERROR))
async def test_an_empty_page_is_extraction_failed_not_a_fake_empty_success(drive, name):
    """The lie this server was built to refuse to tell.

    An empty list because the page did not render is indistinguishable from an
    empty list because the operator has none, so the first is never allowed to
    be reported as the second.
    """
    tool, expected_url = EMPTY_IS_AN_ERROR[name]
    page = FakePage(evaluate_result=[])
    drive(page)

    result = await _call(tool)

    assert result["error"] == "extraction_failed", result
    assert result["url"] == expected_url, "the operator must be able to look himself"
    assert "results" not in result
    assert "count" not in result


async def test_the_notification_failure_names_the_selector_list_to_update(drive):
    """Notifications is the surface with the least dependable markup."""
    page = FakePage(evaluate_result=[])
    drive(page)

    result = await linkedin_notifications()

    assert result["error"] == "extraction_failed"
    assert "NOTIFICATION_SELECTORS" in result["hint"]


async def test_an_empty_search_page_is_a_legitimate_result_not_an_error(drive):
    """Search is the one surface where nothing found is a real answer.

    A filter combination that matches nothing, or an offset past the end of the
    results, is not a broken page -- so search lets the empty harvest through
    and explains it, where every other tool raises.
    """
    page = FakePage(evaluate_result=[])
    drive(page)

    result = await linkedin_search_jobs(keywords="cobol architect", start=500)

    assert "error" not in result, result
    assert result["results"] == []
    assert result["count"] == 0
    assert result["page_had"] == 0
    assert result["capped"] is False
    assert "held no job cards" in result["note"]


# ---------------------------------------------------------------------------
# 5. who_viewed_me falls back exactly once
# ---------------------------------------------------------------------------

#: Records the harvester really returns and the parser really rejects: cards
#: whose every line is interface chrome. This exercises "no parseable ROWS",
#: which is a strictly harder case than "no records at all".
UNPARSEABLE_VIEWER_CARDS = [
    {"href": "/in/somebody/", "text": "Follow\nFollow"},
    {"href": "/in/another-person/", "text": "Message\nConnect"},
]


async def test_who_viewed_me_falls_back_to_the_classic_page_once(drive):
    page = ScriptedPage(evaluate_queue=[UNPARSEABLE_VIEWER_CARDS, [PERSON_CARD]])
    navigations = drive(page)

    result = await linkedin_who_viewed_me(limit=25)

    assert result["pages_loaded"] == 2
    assert navigations == [ANALYTICS_VIEWS_URL, CLASSIC_VIEWS_URL]
    assert result["source_url"] == CLASSIC_VIEWS_URL
    assert result["results"][0]["name"] == "Priya Raman"
    assert page.evaluate_overrun is False


async def test_who_viewed_me_loads_one_page_when_the_first_one_answers(drive):
    """The fallback must be a fallback, not a second page load on every call."""
    page = ScriptedPage(evaluate_queue=[[PERSON_CARD], [PERSON_CARD]])
    navigations = drive(page)

    result = await linkedin_who_viewed_me(limit=25)

    assert result["pages_loaded"] == 1
    assert navigations == [ANALYTICS_VIEWS_URL]
    assert len(page.evaluations) == 1


async def test_both_profile_view_pages_failing_is_reported_as_a_failure(drive):
    page = ScriptedPage(evaluate_queue=[[], []])
    navigations = drive(page)

    result = await linkedin_who_viewed_me()

    assert result["error"] == "extraction_failed"
    assert result["url"] == CLASSIC_VIEWS_URL
    assert len(navigations) == 2, "two urls tried, and no more than two"


# ---------------------------------------------------------------------------
# 6. Search argument validation, and the url it builds
# ---------------------------------------------------------------------------

BAD_SEARCH_ARGS = {
    "empty_keywords": {"keywords": ""},
    "whitespace_keywords": {"keywords": "   "},
    "unknown_remote": {"keywords": "node.js", "remote": "anywhere"},
    "unknown_date_posted": {"keywords": "node.js", "date_posted": "past_year"},
    "unknown_experience": {"keywords": "node.js", "experience_level": "principal"},
    "unknown_sort_by": {"keywords": "node.js", "sort_by": "salary"},
}


@pytest.mark.parametrize("name", sorted(BAD_SEARCH_ARGS))
async def test_a_bad_search_argument_is_refused_before_any_page_load(drive, name):
    page = FakePage(evaluate_result=[SEARCH_CARD])
    navigations = drive(page)

    result = await linkedin_search_jobs(**BAD_SEARCH_ARGS[name])

    assert result["error"] == "bad_argument", result
    assert result["message"]
    assert navigations == [], "a rejected argument must not cost a page load"
    assert page.evaluations == []


async def test_the_search_url_carries_the_linkedin_filter_parameters(drive):
    page = FakePage(evaluate_result=[SEARCH_CARD])
    navigations = drive(page)

    result = await linkedin_search_jobs(
        keywords="senior node.js engineer",
        location="Riverton",
        remote="remote",
        date_posted="past_24h",
        experience_level="mid_senior",
        sort_by="date",
        start=25,
    )

    assert "error" not in result, result
    url = navigations[0]
    assert url.startswith("https://www.linkedin.com/jobs/search/?")
    assert "keywords=senior+node.js+engineer" in url
    assert "location=Riverton" in url
    assert "f_WT=2" in url, "remote"
    assert "f_TPR=r86400" in url, "past 24 hours"
    assert "f_E=4" in url, "mid-senior"
    assert "sortBy=DD" in url, "sort by date"
    assert "start=25" in url


async def test_several_experience_levels_become_one_comma_joined_parameter(drive):
    page = FakePage(evaluate_result=[SEARCH_CARD])
    navigations = drive(page)

    result = await linkedin_search_jobs(
        keywords="engineering manager",
        experience_level="mid_senior, director",
    )

    assert "error" not in result, result
    assert "f_E=4%2C5" in navigations[0]
    assert result["query"]["experience_level"] == ["mid_senior", "director"]


async def test_an_unfiltered_search_adds_no_filter_parameters(drive):
    """"any" has to mean no parameter, or every search is silently filtered."""
    page = FakePage(evaluate_result=[SEARCH_CARD])
    navigations = drive(page)

    await linkedin_search_jobs(keywords="node.js engineer")

    url = navigations[0]
    assert url == "https://www.linkedin.com/jobs/search/?keywords=node.js+engineer"
    for absent in ("f_WT", "f_TPR", "f_E", "sortBy", "start", "location"):
        assert absent not in url


async def test_the_search_echoes_back_the_query_it_actually_ran(drive):
    page = FakePage(evaluate_result=[SEARCH_CARD])
    drive(page)

    result = await linkedin_search_jobs(
        keywords="  node.js engineer  ", location="  Riverton  ", start=50
    )

    assert result["query"] == {
        "keywords": "node.js engineer",
        "location": "Riverton",
        "remote": "any",
        "date_posted": "any",
        "experience_level": None,
        "sort_by": "relevance",
        "start": 50,
    }


# ---------------------------------------------------------------------------
# 7. The profile reader
# ---------------------------------------------------------------------------


async def test_the_profile_loads_one_page_when_skills_are_not_asked_for(drive):
    page = ScriptedPage(
        evaluate_queue=[PROFILE_FIELDS],
        redirect_map={PROFILE_ME_URL: PROFILE_RESOLVED_URL},
    )
    navigations = drive(page)

    result = await linkedin_my_profile(include_skills=False)

    assert result["pages_loaded"] == 1
    assert navigations == [PROFILE_ME_URL]
    assert len(page.evaluations) == 1
    assert "skills" not in result
    assert result["name"] == "Alex R"
    assert result["headline"] == "Senior Node.js Engineer | TypeScript | AWS"
    assert result["location"] == "Riverton, Fairhaven, United States"
    assert result["public_identifier"] == "alex-r"
    assert result["profile_url"] == PROFILE_RESOLVED_URL


async def test_the_profile_loads_the_skills_page_second_when_asked(drive):
    page = ScriptedPage(
        evaluate_queue=[PROFILE_FIELDS, SKILL_CARDS],
        redirect_map={PROFILE_ME_URL: PROFILE_RESOLVED_URL},
    )
    navigations = drive(page)

    result = await linkedin_my_profile(include_skills=True)

    assert result["pages_loaded"] == 2
    assert navigations == [PROFILE_ME_URL, SKILLS_URL]
    assert result["skills"] == [
        "Node.js",
        "TypeScript",
        "PostgreSQL",
        "AWS",
        "Docker",
        "Redis",
    ]
    assert result["skills_count"] == 6
    assert page.evaluate_overrun is False


async def test_the_completeness_block_is_labelled_derived_and_invents_no_score(drive):
    """LinkedIn's profile-strength meter is not exposed, so none is reported."""
    page = ScriptedPage(
        evaluate_queue=[PROFILE_FIELDS],
        redirect_map={PROFILE_ME_URL: PROFILE_RESOLVED_URL},
    )
    drive(page)

    result = await linkedin_my_profile(include_skills=False)
    completeness = result["completeness"]

    derived_by = completeness["derived_by"]
    assert "this server" in derived_by
    assert "profile-strength meter" in derived_by

    assert completeness["has_photo"] is True
    assert completeness["has_about"] is True
    # Only LinkedIn's own profile SECTIONS. "Analytics" rendered too, but it is
    # page furniture and is reported under headings_seen, not as a section.
    assert completeness["sections_present"] == ["About", "Featured"]
    assert "Analytics" in completeness["headings_seen"]
    # The sections LinkedIn defers until the page is scrolled. They are null,
    # never zero, and the result says out loud that null means unknown.
    assert completeness["sections_not_rendered"] == [
        "Experience",
        "Education",
        "Skills",
    ]
    assert completeness["experience_entries"] is None
    assert completeness["education_entries"] is None
    assert completeness["skills_listed"] is None
    assert "UNKNOWN, not zero" in completeness["not_rendered_means"]

    invented = ("score", "strength", "percent", "rating", "grade", "out_of")
    offenders = [
        key
        for key in list(completeness) + list(result)
        if any(word in key.lower() for word in invented)
    ]
    assert offenders == [], offenders


async def test_a_profile_page_with_no_readable_name_is_a_failure(drive):
    """Not a dict of Nones. A shape full of nulls reads like data."""
    page = ScriptedPage(
        evaluate_queue=[{"url": PROFILE_RESOLVED_URL, "sections": []}],
        redirect_map={PROFILE_ME_URL: PROFILE_RESOLVED_URL},
    )
    drive(page)

    result = await linkedin_my_profile(include_skills=True)

    assert result["error"] == "extraction_failed", result
    assert result["url"] == PROFILE_RESOLVED_URL
    assert "name" not in result
    assert "completeness" not in result


async def test_a_profile_whose_slug_cannot_be_resolved_says_so(drive):
    """/in/me/ that never redirects leaves no slug to build a skills url from."""
    page = ScriptedPage(evaluate_queue=[PROFILE_FIELDS])
    navigations = drive(page)

    result = await linkedin_my_profile(include_skills=True)

    assert result["public_identifier"] is None
    assert result["pages_loaded"] == 1
    assert navigations == [PROFILE_ME_URL]
    assert "skills" not in result
    assert "could not resolve" in result["skills_note"]


# ---------------------------------------------------------------------------
# 8. The notification side effect is disclosed in the RESULT
# ---------------------------------------------------------------------------


async def test_the_notification_side_effect_is_disclosed_in_the_result(drive):
    """A docstring is read once. The result is read every call."""
    page = FakePage(evaluate_result=[NOTIFICATION_CARD])
    drive(page)

    result = await linkedin_notifications()

    assert "badge" in result["side_effect"]
    assert "cleared" in result["side_effect"]


@pytest.mark.parametrize(
    "name", ["who_viewed_me", "my_applications", "saved_jobs", "search_jobs"]
)
async def test_no_other_tool_claims_a_side_effect_it_does_not_have(drive, name):
    records = {
        "who_viewed_me": [PERSON_CARD],
        "my_applications": [APPLIED_CARD],
        "saved_jobs": [SAVED_CARD],
        "search_jobs": [SEARCH_CARD],
    }[name]
    page = FakePage(evaluate_result=records)
    drive(page)

    result = await _call(AUTHWALL_TOOLS[name])

    assert "side_effect" not in result


# ---------------------------------------------------------------------------
# 9. Limits are clamped, not trusted
# ---------------------------------------------------------------------------

#: (tool, default, maximum) taken from config, never guessed at the call site.
LIMIT_TOOLS = {
    "who_viewed_me": (linkedin_who_viewed_me, DEFAULT_LIMIT, MAX_LIMIT),
    "my_applications": (linkedin_my_applications, DEFAULT_LIMIT, MAX_LIMIT),
    "saved_jobs": (linkedin_saved_jobs, DEFAULT_LIMIT, MAX_LIMIT),
    "search_jobs": (linkedin_search_jobs, SEARCH_DEFAULT_LIMIT, SEARCH_MAX_LIMIT),
    "notifications": (
        linkedin_notifications,
        NOTIFICATIONS_DEFAULT_LIMIT,
        NOTIFICATIONS_MAX_LIMIT,
    ),
}

ONE_ROW = {
    "who_viewed_me": [PERSON_CARD],
    "my_applications": [APPLIED_CARD],
    "saved_jobs": [SAVED_CARD],
    "search_jobs": [SEARCH_CARD],
    "notifications": [NOTIFICATION_CARD],
}


@pytest.mark.parametrize("asked", [99999, 10**9, 101])
@pytest.mark.parametrize("name", sorted(LIMIT_TOOLS))
async def test_an_oversized_limit_is_clamped_to_the_tools_own_maximum(
    drive, name, asked
):
    tool, _default, maximum = LIMIT_TOOLS[name]
    page = FakePage(evaluate_result=list(ONE_ROW[name]))
    drive(page)

    result = await _call(tool, limit=asked)

    assert result["limit"] == maximum, result


@pytest.mark.parametrize("asked", [0, -1, -9999])
@pytest.mark.parametrize("name", sorted(LIMIT_TOOLS))
async def test_a_zero_or_negative_limit_is_clamped_to_at_least_one(drive, name, asked):
    tool, _default, _maximum = LIMIT_TOOLS[name]
    page = FakePage(evaluate_result=list(ONE_ROW[name]))
    drive(page)

    result = await _call(tool, limit=asked)

    assert result["limit"] == 1, result
    assert result["count"] <= 1


@pytest.mark.parametrize("asked", ["twelve", None, [], {"n": 5}])
@pytest.mark.parametrize("name", sorted(LIMIT_TOOLS))
async def test_a_limit_that_is_not_a_number_falls_back_to_the_default(
    drive, name, asked
):
    tool, default, _maximum = LIMIT_TOOLS[name]
    page = FakePage(evaluate_result=list(ONE_ROW[name]))
    drive(page)

    result = await _call(tool, limit=asked)

    assert result["limit"] == default, result


@pytest.mark.parametrize("name", sorted(LIMIT_TOOLS))
async def test_a_numeric_string_limit_is_honoured_rather_than_discarded(drive, name):
    tool, _default, _maximum = LIMIT_TOOLS[name]
    page = FakePage(evaluate_result=list(ONE_ROW[name]))
    drive(page)

    result = await _call(tool, limit="3")

    assert result["limit"] == 3, result


def test_the_documented_limits_are_the_configured_limits():
    """The docstrings quote these numbers at the caller. They have to be true."""
    assert (DEFAULT_LIMIT, MAX_LIMIT) == (25, 100)
    assert (SEARCH_DEFAULT_LIMIT, SEARCH_MAX_LIMIT) == (25, 50)
    assert (NOTIFICATIONS_DEFAULT_LIMIT, NOTIFICATIONS_MAX_LIMIT) == (20, 50)
