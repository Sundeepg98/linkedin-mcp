"""A notification link should hand the caller a key some tool will take.

RELEVANCE SHAPING, which is a different pass from the size audit. The size
question is "is this response too big". This one is "can a caller DECIDE from
it, without a follow-up call, and is anything here they did not need".

The two failures are not symmetric. Noise costs context; **a missing field
costs a whole round trip**, which is worse. So these keys ADD tokens per row
on purpose.

WHAT WAS WRONG. A notification carried ``link`` -- an absolute url -- and
nothing on this server accepts a url. A caller who wanted to act on a
notification had to parse the href themselves or spend a call finding the key.
Meanwhile two keys that tools here DO accept were sitting in that href unread:
the keywords of a job alert, which go straight to ``linkedin_search_jobs``,
and a numeric company id, which goes to ``linkedin_unfollow_company``.

MEASURED AGAINST THE TRACKED FIXTURE rather than guessed. Its notification
links are job alerts, feed posts, member profiles and one company page --
and NOT job postings, which is the obvious guess and is wrong. There is no
``/jobs/view/<id>`` link among them, so there is no job_id to extract, and a
reader that went looking would find nothing and report nothing -- which looks
exactly like a notification that has no job attached.
"""
from __future__ import annotations

import pytest

from linkedin_server import shape

BASE = "https://www.linkedin.com"


@pytest.mark.parametrize(
    "link,expected",
    [
        (
            f"{BASE}/jobs/search-results/?keywords=Senior+Software+Engineer&distance=25",
            {"search_keywords": "Senior Software Engineer"},
        ),
        (
            f"{BASE}/jobs/search-results?keywords=Senior%20Software%20Engineer%20II",
            {"search_keywords": "Senior Software Engineer II"},
        ),
        (f"{BASE}/company/5417062", {"company_id": "5417062"}),
    ],
    ids=["alert plus-encoded", "alert percent-encoded", "company page"],
)
def test_a_link_yields_the_key_a_tool_will_take(link, expected):
    assert shape.notification_handles(link) == expected


@pytest.mark.parametrize(
    "link",
    [
        f"{BASE}/feed/?highlightedUpdateUrn=urn%3Ali%3Aactivity%3A7400000000000000001",
        f"{BASE}/video/event/urn:li:ugcPost:7400000000000000003",
        f"{BASE}/in/dana%2Dwhitfield%2D4b12",
        "",
    ],
    ids=["feed post", "video event", "member profile", "empty"],
)
def test_a_link_with_no_usable_key_says_nothing(link):
    """Silence is the honest answer.

    A feed post and a member profile carry no key this server can use today --
    member lookup is not built -- and inventing a field so every row has one
    would be noise with a confident shape.
    """
    assert shape.notification_handles(link) == {}


def test_no_job_id_is_invented_from_a_notification():
    """The obvious guess, pinned as wrong.

    Notification links are alerts and profiles, not postings. If a future
    edit adds job_id extraction here it must come with a fixture that
    actually contains a /jobs/view/ link, or it is a field that will read
    null forever and mean nothing.
    """
    for link in (
        f"{BASE}/jobs/search-results/?keywords=Backend+Engineer",
        f"{BASE}/company/5417062",
    ):
        assert "job_id" not in shape.notification_handles(link)


def test_the_keys_are_the_ones_tools_actually_accept():
    """The whole point is that these are not decorative.

    ``search_keywords`` is the argument ``linkedin_search_jobs`` takes, and
    ``company_id`` is what ``linkedin_unfollow_company`` takes -- by NUMERIC
    id, never a name, which is why the pattern requires digits. A key that no
    tool accepts would be the same defect being fixed here, wearing a
    different field name.
    """
    import inspect

    from linkedin_server.server import linkedin_search_jobs, linkedin_unfollow_company

    assert "keywords" in inspect.signature(linkedin_search_jobs).parameters
    assert "company_id" in inspect.signature(linkedin_unfollow_company).parameters

    # And a company SLUG is not a company id, so it must not match.
    assert shape.notification_handles(f"{BASE}/company/some-company-name") == {}


# ---------------------------------------------------------------------------
# THROUGH THE CALLER. Everything above this line calls the extractor DIRECTLY.
# ---------------------------------------------------------------------------
#
# That is what made this defect survive: six test functions and eight
# parametrised cases, all green, none of them routed through
# ``shape.parse_notification`` -- the only thing in this repository that calls
# ``notification_handles`` at all. The extractor was correct and unreachable at
# the same instant, and no test here could tell those apart, because the input
# every one of them supplied was a url the caller never actually passes.
#
# The mechanism, measured 2026-09-05: ``parse_notification`` handed the
# extractor ``absolute_url(href)``, and ``absolute_url`` deletes the query
# string. ``search_keywords`` lives ONLY in the query string. So it was
# extracted and discarded on every notification this server has ever shaped,
# while ``company_id`` -- which lives in the PATH -- kept working. One of two
# keys firing is why the surface never looked broken.
#
# The reason it costs real signal: the keyword is what a job alert FIRED ON,
# which is the field that separates a relevant alert from noise, and it is the
# argument ``linkedin_search_jobs`` takes.

#: A job alert exactly as the tracked notifications fixture draws one: the
#: keyword first, then LinkedIn's own filter and origin parameters.
ALERT_HREF = (
    "/jobs/search-results/?keywords=Senior+Software+Engineer"
    "&f_TPR=a1787213463-&origin=SEMANTIC_SEARCH_JOB_ALERT"
)

#: The same alert with a content urn in its query. 2 of the 7 query strings on
#: the tracked fixture carry one of these, which is what ``absolute_url`` is
#: really protecting against -- it is an identity control, not tidiness. The
#: urn is the one already used above for the feed-post case, so this widens
#: nothing: it is a value this file has already established is invented.
ALERT_HREF_WITH_URN = (
    ALERT_HREF + "&highlightedUpdateUrn=urn%3Ali%3Aactivity%3A7400000000000000001"
)


def _alert_row(href: str) -> dict:
    """One notification card, shaped the way the harvest hands them over."""
    return {
        "text": "Your job alert for Senior Software Engineer: 12 new jobs",
        "time": "2h",
        "href": href,
        "unread": True,
    }


def test_a_job_alerts_keyword_reaches_the_caller_that_publishes_it():
    """THE DEFECT, pinned end to end rather than at the extractor.

    Reverting ``parse_notification`` to pass ``link`` instead of ``href``
    turns this red and leaves every test above it green.
    """
    row = shape.parse_notification(_alert_row(ALERT_HREF))
    assert row["search_keywords"] == "Senior Software Engineer"


def test_the_published_link_still_has_its_query_deleted():
    """THE PROTECTION, pinned so it cannot be traded away for the fix above.

    The cheap way to make the previous test pass is to stop stripping the
    query. That would publish the tracking parameters and, on a feed
    notification, a content urn. This is the test that refuses that fix.
    """
    row = shape.parse_notification(_alert_row(ALERT_HREF))
    assert row["link"] == f"{BASE}/jobs/search-results/"
    assert "?" not in row["link"]


def test_only_the_keyword_ever_escapes_the_query_string():
    """Nothing else in the query may appear anywhere in the emitted row.

    Derived from the href rather than typed as literals, so the check cannot
    drift away from the input it is about, and so no new opaque value has to
    be invented to write it.
    """
    row = shape.parse_notification(_alert_row(ALERT_HREF_WITH_URN))
    emitted = " ".join(str(value) for value in row.values())
    query = ALERT_HREF_WITH_URN.split("?", 1)[1]
    leaked = [
        part.split("=", 1)[0]
        for part in query.split("&")
        if "=" in part
        and not part.startswith("keywords=")
        and part.split("=", 1)[1]
        and part.split("=", 1)[1] in emitted
    ]
    assert leaked == []
    # And the control: the keyword DID come through, so an empty ``leaked``
    # means "nothing else escaped" rather than "the row came back blank".
    assert row["search_keywords"] == "Senior Software Engineer"


def test_a_company_id_is_read_from_the_path_and_never_from_the_query():
    """The hole the fix would otherwise have opened, closed and pinned.

    Now that this function is handed unstripped urls, a ``/company/<digits>``
    inside a redirect or tracking parameter would start being reported as the
    company a notification is about. It is read from the path only.
    """
    in_the_query = (
        f"{BASE}/jobs/search-results/?keywords=Backend+Engineer"
        "&redirectUrl=/company/5417062"
    )
    assert shape.notification_handles(in_the_query) == {
        "search_keywords": "Backend Engineer"
    }
    # The control, and it is the whole reading: the SAME digits in the PATH
    # are still read, so the test above measures where the id was found and
    # not whether the extractor works at all.
    assert shape.notification_handles(f"{BASE}/company/5417062") == {
        "company_id": "5417062"
    }
