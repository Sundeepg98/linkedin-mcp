"""The people he follows (census ``N 38``) and the members he unfollowed (``N 39``), read on live session 11's captures.

THE PAGES ARE REAL: the live lane's session-11 tracked copies
``tests/fixtures/live11/following.html`` (load 16) and ``unfollowed.html``
(load 9), every name and headline the skeleton's ``x``. Both readers aim by
words the tracked copies keep -- LinkedIn's ``Following`` and ``Follow`` are
on the harness's closed list -- and, on the unfollowed page, by LinkedIn's own
test-hook attributes. Every test reads one of those pages or one of them with
one thing planted:

* the followers tab current -> the following reader refuses;
* a card with a second button -> that card is not read;
* the unfollowed card's hook removed -> the read refuses;
* a row's word ``Following`` -> that member reads as followed again;
* every row's button removed -> no row, and it raises;
* a name in every name slot -> back inside the records only;
* a name in every label -> the answer is identical.

NOTHING HERE REACHES LINKEDIN: a local headless Chromium over ``set_content``,
every request refused first.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import following_list, people_data, unfollowed_list
from linkedin_server.errors import ExtractionFailedError
from tests.plantedpage import PLANT, carries_the_plant_outside_records
from tests.test_writes import browser_page  # noqa: F401 -- fixture

REPO = Path(__file__).resolve().parents[1]
FOLLOWING = REPO / "tests" / "fixtures" / "live11" / "following.html"
UNFOLLOWED = REPO / "tests" / "fixtures" / "live11" / "unfollowed.html"


def _record(name: str = "x", headline: Any = "x", link: Any = "https://www.linkedin.com/in/x/") -> dict[str, Any]:
    return {"name": name, "headline": headline, "link": link, "degree": None,
            people_data.UNTRUSTED_KEY: people_data.UNTRUSTED_NOTE}


async def _refused(route: Any) -> None:
    await route.abort()


async def _read(page: Any, html: str, reader: Any) -> dict[str, Any]:
    await page.route("**/*", _refused)
    await page.set_content(html, wait_until="domcontentloaded")
    return await reader(page)


def _text(path: Path) -> str:
    return path.read_text(encoding="ascii")


# ---------------------------------------------------------------------------
# The people he follows (N 38)
# ---------------------------------------------------------------------------


async def test_the_following_list_reads_its_twenty_cards(browser_page):
    out = await _read(browser_page, _text(FOLLOWING), following_list.read_following_list)
    assert (out["side"], out["refused"]) == ("following", None)
    assert out["tab_links_seen"] == 2
    assert (out["cards_seen"], out["cards_read"]) == (20, 20)
    assert out["following"] == [_record()] * 20
    assert out["card_gaps"] == {gap: 0 for gap in following_list.CARD_GAPS}
    assert out["readable"] is True


async def test_the_followers_tab_current_refuses(browser_page):
    html = _text(FOLLOWING)
    html = html.replace(
        'aria-current="true" href="https://www.linkedin.com/mynetwork/network-manager/people-follow/following"',
        'href="https://www.linkedin.com/mynetwork/network-manager/people-follow/following"', 1,
    )
    assert 'aria-current="true"' not in html.split("<main", 1)[1].split("</nav>", 1)[0]
    html = html.replace(
        'href="https://www.linkedin.com/mynetwork/network-manager/people-follow/followers"',
        'aria-current="true" href="https://www.linkedin.com/mynetwork/network-manager/people-follow/followers"', 1,
    )
    out = await _read(browser_page, html, following_list.read_following_list)
    assert (out["side"], out["refused"]) == ("followers", "not_the_following_side")
    assert out["following"] == []


async def test_a_card_with_a_second_button_is_not_read(browser_page):
    html = _text(FOLLOWING)
    first = html.index(">\nFollowing\n<", html.index("<main"))
    first = html.index(">\nFollowing\n<", first + 1)  # past the tab, to the first card
    cut = html.index("</button>", first) + len("</button>")
    html = html[:cut] + '<button type="button"><span>x</span></button>' + html[cut:]
    out = await _read(browser_page, html, following_list.read_following_list)
    assert out["card_gaps"]["not_one_button"] == 1
    assert len(out["following"]) == 19


async def test_a_followed_members_name_comes_back_only_inside_a_record(browser_page):
    html = re.sub(r'(<p class="[^"]*">\n)x(\n</p>)', lambda m: m.group(1) + PLANT + m.group(2),
                  _text(FOLLOWING))
    out = await _read(browser_page, html, following_list.read_following_list)
    assert {member["name"] for member in out["following"]} == {PLANT}
    outside, records = carries_the_plant_outside_records(out)
    assert outside == [] and records > 0


async def test_a_name_in_every_label_of_the_following_list_is_never_read(browser_page):
    plain = await _read(browser_page, _text(FOLLOWING), following_list.read_following_list)
    planted = await _read(
        browser_page, _text(FOLLOWING).replace('aria-label="x"', f'aria-label="{PLANT}"'),
        following_list.read_following_list,
    )
    assert planted == plain


# ---------------------------------------------------------------------------
# The members he unfollowed (N 39)
# ---------------------------------------------------------------------------


async def test_the_unfollowed_page_reads_its_44_members_with_no_link(browser_page):
    out = await _read(browser_page, _text(UNFOLLOWED), unfollowed_list.read_unfollowed_list)
    assert out["refused"] is None and out["cards_seen"] == 1
    assert (out["rows_seen"], out["rows_read"]) == (44, 44)
    assert out["unfollowed"] == [
        {"member": _record(headline=None, link=None), "he_follows": False}
    ] * 44
    assert out["row_gaps"] == {gap: 0 for gap in unfollowed_list.ROW_GAPS}
    assert out["readable"] is True


async def test_a_row_reading_following_is_a_member_he_follows_again(browser_page):
    html = _text(UNFOLLOWED)
    button = html.index("data-test-unfollowed-member__follow-btn")
    word = html.index("\nFollow\n", button)
    html = html[:word] + "\nFollowing\n" + html[word + len("\nFollow\n"):]
    out = await _read(browser_page, html, unfollowed_list.read_unfollowed_list)
    assert [row["he_follows"] for row in out["unfollowed"]][:2] == [True, False]


async def test_no_unfollowed_card_refuses(browser_page):
    html = _text(UNFOLLOWED).replace("data-test-unfollowed-card=", "data-test-other-card=")
    out = await _read(browser_page, html, unfollowed_list.read_unfollowed_list)
    assert (out["refused"], out["cards_seen"]) == ("card_unreadable", 0)
    assert out["unfollowed"] == []


async def test_a_card_with_no_follow_button_raises_and_quotes_nothing(browser_page):
    html = _text(UNFOLLOWED).replace(
        "data-test-unfollowed-member__follow-btn=", "data-test-other-btn="
    )
    with pytest.raises(ExtractionFailedError) as raised:
        await _read(browser_page, html, unfollowed_list.read_unfollowed_list)
    assert PLANT not in str(raised.value)


async def test_an_unfollowed_members_name_comes_back_only_inside_a_record(browser_page):
    html = re.sub(
        r'(data-test-profile-card-name="">\n)x(\n</div>)',
        lambda m: m.group(1) + PLANT + m.group(2),
        _text(UNFOLLOWED),
    )
    out = await _read(browser_page, html, unfollowed_list.read_unfollowed_list)
    assert {row["member"]["name"] for row in out["unfollowed"]} == {PLANT}
    outside, records = carries_the_plant_outside_records(out)
    assert outside == [] and records > 0


async def test_a_name_in_every_label_of_the_unfollowed_page_is_never_read(browser_page):
    plain = await _read(browser_page, _text(UNFOLLOWED), unfollowed_list.read_unfollowed_list)
    planted = await _read(
        browser_page,
        _text(UNFOLLOWED).replace('aria-label="x"', f'aria-label="{PLANT}"').replace(
            'alt="x"', f'alt="{PLANT}"'),
        unfollowed_list.read_unfollowed_list,
    )
    assert planted == plain


# ---------------------------------------------------------------------------
# The landings, and the modules' reach
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("landed", "following", "unfollowed"),
    [
        ("https://www.linkedin.com/mynetwork/network-manager/people-follow/following/", True, False),
        ("https://www.linkedin.com/mynetwork/network-manager/people-follow/following", True, False),
        ("https://www.linkedin.com/mynetwork/network-manager/people-follow/followers/", False, False),
        ("https://www.linkedin.com/mypreferences/d/unfollowed", False, True),
        ("https://www.linkedin.com/mypreferences/d/unfollowed/?x=1", False, True),
        ("https://www.linkedin.com/mypreferences/d/", False, False),
        (None, False, False),
    ],
)
def test_each_reader_knows_its_own_landing(landed, following, unfollowed):
    assert following_list.landed_on_the_list(landed) is following
    assert unfollowed_list.landed_on_the_page(landed) is unfollowed


@pytest.mark.parametrize("module", ["following_list.py", "unfollowed_list.py"])
def test_the_modules_press_nothing_and_store_nothing(module):
    source = (REPO / "linkedin_server" / module).read_text(encoding="utf-8")
    for call in (".click(", ".fill(", ".press(", ".check(", ".tap(", "open(", "logging", ".goto("):
        assert call not in source, call
