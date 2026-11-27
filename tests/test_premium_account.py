"""His Manage Premium account page, read over its REAL capture (census P N22).

``premium_account.read_premium_account`` runs over session 12's capture of
``/mypreferences/d/premium-manage-account/`` (load 33, served exact), as
``tests/fixtures/live12/premium_manage_account_words.html`` -- the committed
skeleton with LinkedIn's words written where their keyed shapes matched
(``scripts/_build_live12_settings_word_skeletons.py``) -- through
``tests/skeleton_page.py``, with no browser. His purchase id and the card's two
description lines are ``x`` in the fixture, as in the tracked copy; where a
test needs text there it plants a SYNTHETIC string.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import premium_account as pa
from linkedin_server.errors import ExtractionFailedError
from linkedin_server.server import linkedin_my_premium_account
from tests.live11_words import plant
from tests.plantedpage import PlantedPage
from tests.skeleton_page import SkeletonPage, parse

URL = pa.PREMIUM_ACCOUNT_URL
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "live12" / "premium_manage_account_words.html"

#: A marker no fixture draws: it must never leave, in any field.
MARKER = "Placeholder Markerplan"

_PLAN = "data-test-premium-subscription-overview-settings-card__header=\"\">\nPremium Career\n</h2>"
_LINE = '<p class="sans-14 t-black">\nx\n</p>'
_SWITCH = ">\nSwitch plans\n</a>"
_CARD_LIST = 'data-test-premium-subscription-overview-settings-card=""'
_HEADING = 'data-test-header-title="">\nManage Premium account\n</h1>'


def markup() -> str:
    return FIXTURE.read_text(encoding="ascii")


def run(text: str) -> tuple[dict[str, Any], SkeletonPage]:
    page = SkeletonPage(PlantedPage(), parse(text), url=URL)
    return asyncio.run(pa.read_premium_account(page)), page


def strings_in(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from strings_in(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from strings_in(item)


def test_the_capture_reads_one_premium_career_subscription_and_its_three_controls():
    result, page = run(markup())
    assert page.unmodelled == [] and page.planted_answers == []
    assert result["refused"] is None
    assert result["page_heading_drawn"] is True
    assert result["subscriptions"] == [{
        "plan": "premium_career",
        "actions": ["switch_plans", "manage_subscription", "cancel_subscription"],
        "description_lines": 2,
        "description_lines_with_digits": 0,
    }]
    assert result["subscriptions_seen"] == 1
    assert result["unknown_plans"] == 0 and result["unknown_actions"] == 0
    assert result["readable"] is True


def test_no_text_of_the_card_leaves_and_a_dated_line_is_only_counted():
    """A line with a date in it is counted as carrying a digit; the line, the
    date and the marker never leave."""
    dated = _LINE.replace("\nx\n", "\n" + MARKER + " renews on Jan 1, 2031\n")
    text = plant(markup(), _LINE + "\n" + _LINE, dated + "\n" + _LINE)
    result, page = run(text)
    assert page.unmodelled == []
    assert result["subscriptions"][0]["description_lines_with_digits"] == 1
    for value in strings_in(result):
        assert "Markerplan" not in value and "2031" not in value and "renews" not in value


def test_a_plan_this_server_has_not_measured_is_counted_and_never_named():
    result, _ = run(plant(markup(), _PLAN, _PLAN.replace("Premium Career", MARKER)))
    assert result["subscriptions"][0]["plan"] == "other"
    assert result["unknown_plans"] == 1
    assert all("Markerplan" not in value for value in strings_in(result))


def test_a_control_under_another_word_is_counted_and_never_named():
    result, _ = run(plant(markup(), _SWITCH, _SWITCH.replace("Switch plans", MARKER)))
    assert result["subscriptions"][0]["actions"] == ["manage_subscription", "cancel_subscription"]
    assert result["unknown_actions"] == 1
    assert all("Markerplan" not in value for value in strings_in(result))


def test_no_address_the_card_draws_is_returned():
    result, _ = run(markup())
    for value in strings_in(result):
        assert "linkedin.com" not in value and "purchases" not in value and "cancellation" not in value


def test_no_subscription_card_is_a_failure_not_an_empty_list():
    with pytest.raises(ExtractionFailedError):
        run(plant(markup(), _CARD_LIST, 'data-test-placeholder-card=""'))


def test_a_page_without_its_heading_is_not_read():
    with pytest.raises(ExtractionFailedError):
        run(plant(markup(), _HEADING, _HEADING.replace("Manage Premium account", "Placeholder")))


def test_a_page_with_two_main_regions_refuses():
    text = markup().replace("</main>", "</main>\n<main>\n</main>", 1)
    result, _ = run(text)
    assert result["refused"] == "main_unreadable" and result["subscriptions"] == []


@pytest.mark.parametrize("landed, ok", [
    ("https://www.linkedin.com/mypreferences/d/premium-manage-account/", True),
    ("https://www.linkedin.com/mypreferences/d/premium-manage-account", True),
    ("https://www.linkedin.com/premium/my-premium/", False),
    ("https://www.linkedin.com/mypreferences/d/categories/account/", False),
    ("http://www.linkedin.com/mypreferences/d/premium-manage-account/", False),
    ("https://example.com/mypreferences/d/premium-manage-account/", False),
    (None, False),
])
def test_the_landing_may_veto(landed, ok):
    assert pa.landed_on_the_page(landed) is ok


# ---------------------------------------------------------------------------
# The tool: one load of the admitted address, the landing checked first
# ---------------------------------------------------------------------------


def _drive(monkeypatch, text: str, landing: str = URL) -> list[str]:
    navigations: list[str] = []
    page = SkeletonPage(PlantedPage(), parse(text), url=landing)

    @asynccontextmanager
    async def fake_session():
        yield page

    async def fake_goto(target_page, url, **kwargs):
        navigations.append(url)
        return landing

    monkeypatch.setattr(browser_module.BROWSER, "session", fake_session)
    monkeypatch.setattr(browser_module.BROWSER, "goto", fake_goto)
    return navigations


async def test_the_tool_loads_the_one_admitted_address_and_reads_it(monkeypatch):
    navigations = _drive(monkeypatch, markup())
    result = await linkedin_my_premium_account()
    assert navigations == [URL]
    assert result["subscriptions"][0]["plan"] == "premium_career"
    assert result["refused"] is None


async def test_a_landing_elsewhere_is_not_read(monkeypatch):
    _drive(monkeypatch, markup(), landing="https://www.linkedin.com/premium/my-premium/")
    result = await linkedin_my_premium_account()
    assert result["refused"] == "landed_elsewhere"
    assert result["subscriptions"] == []
