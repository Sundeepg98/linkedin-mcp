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
