"""``J 31``'s AI ARM: the job-alert switch on LinkedIn's AI job search, set and unset (lane jobs7).

WHY AN AI ARM. Live session 12's load 3 asked for the classic job search and
was redirected to the AI search, with no classic list and no classic alert
toggle (``C-SRCH-1``, the decision load). The classic pair could not act any
more: its address redirected and its toggle was never drawn. So the pair's
address is the AI search's own (``search_alert_switch.URL_TEMPLATE``) and its
reader reads the AI page's switch; the classic arm stays, read wherever
LinkedIn serves the classic page.

THE MARKUP IS SESSION 12'S OWN, both AI loads: ``tests/fixtures/live12/
c_srch_1_words.html`` and ``c_srch_0b_words.html`` (``scripts/_build_jobs7_
word_skeletons.py``), each drawing ONE ``input[role=switch]`` inside the
component keyed ``JobSearchAlertToggleRef_...`` (the key written by its
grammar), captioned ``Get job alerts for this search`` (by keyed shape), with
no ``checked`` attribute and no ``aria-checked``. The ON shape is DERIVED by
an asserted edit (the ``checked`` attribute added); no capture holds it on.

NOTHING HERE REACHES LINKEDIN: every page is a capture served into a local
headless Chromium whose page aborts every request it would start.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from linkedin_server import readonly, search_alert_switch, server, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_writes import (  # noqa: F401 -- two of these are fixtures
    FixtureNavigator,
    browser_page,
    markup,
    writes_on,
)

SET = "set_search_job_alert"
UNSET = "unset_search_job_alert"
SET_SPEC = spec_for_action(SET)
UNSET_SPEC = spec_for_action(UNSET)

KEYWORDS = "Example role"
QUERY, _ = search_alert_switch.query_for(KEYWORDS)
URL = SET_SPEC.url_template.format(target=QUERY)

#: Session 12's two AI loads, MEASURED (their words and keys by keyed shape).
AI_BASE = markup("live12/c_srch_1_words")
AI_SECOND = markup("live12/c_srch_0b_words")
#: Session 2's classic capture, the arm kept for a classic landing.
CLASSIC_BASE = markup("live2/j107_search_alert")

_AI_INPUT = '<input role="switch" type="checkbox"'


def _derive(old: str, new: str, *, source: str = AI_BASE, count: int = 1) -> str:
    """An ASSERTED edit: a replace whose anchor drifted is a silent no-op."""
    assert source.count(old) >= count, f"the derivation's anchor {old!r} is drawn {source.count(old)} time(s)"
    derived = source.replace(old, new, count)
    assert derived != source
    return derived


#: DERIVED -- the switch on: the input checked, still no aria-checked.
ON_WORLD = _derive(_AI_INPUT, _AI_INPUT + ' checked=""')
#: DERIVED -- the caption gone.
NO_CAPTION_WORLD = _derive("\nGet job alerts for this search\n", "\nx\n")
#: DERIVED -- a second switch inside the keyed toggle.
_INPUT_LINE = AI_BASE[AI_BASE.index(_AI_INPUT): AI_BASE.index(">", AI_BASE.index(_AI_INPUT)) + 1]
TWO_WORLD = _derive(_INPUT_LINE, _INPUT_LINE + _INPUT_LINE)
#: DERIVED -- the switch draws an aria-checked, which no capture has drawn.
ARIA_WORLD = _derive(_AI_INPUT, '<input role="switch" aria-checked="false" type="checkbox"')
#: DERIVED -- the toggle's key without LinkedIn's prefix.
NO_KEY_WORLD = _derive('componentkey="JobSearchAlertToggleRef_', 'componentkey="k0_', count=2)
#: DERIVED -- a classic toggle drawn beside the AI one, right inside <body>.
_BODY_OPEN_END = AI_BASE.index(">", AI_BASE.index("<body")) + 1
BOTH_WORLD = (
    AI_BASE[:_BODY_OPEN_END]
    + '\n<div class="jobs-search-create-alert__artdeco-toggle">'
      '<span class="artdeco-toggle__text">Set alert</span></div>'
    + AI_BASE[_BODY_OPEN_END:]
)


@pytest.fixture
async def page(browser_page):
    """The shared local Chromium page, refusing every request it would start."""

    async def _refuse(route):
        await route.abort()

    await browser_page.route("**/*", _refuse)
    return browser_page


async def _read(page, html: str):
    await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
    return await search_alert_switch.read_state(page)


# ---------------------------------------------------------------------------
# 0. The address: the AI search's own, keywords alone, a place refused
# ---------------------------------------------------------------------------


def test_the_grant_address_is_the_ai_searchs_own_and_admitted():
    """RED BEFORE LANE JOBS7: the template was the classic ``/jobs/search/``."""
    assert QUERY == "keywords=Example+role"
    assert URL == "https://www.linkedin.com/jobs/search-results/?keywords=Example+role"
    assert SET_SPEC.url_pattern.fullmatch(URL) and UNSET_SPEC.url_pattern.fullmatch(URL)
    assert readonly.is_read_url(URL) is True


def test_a_place_is_refused_before_any_load_and_not_repeated():
    """RED BEFORE LANE JOBS7: a place was composed into the address."""
    query, why = search_alert_switch.query_for(KEYWORDS, "Example City")
    assert query is None and "C-SRCH-2" in why and "Example City" not in why
    target, why = search_alert_switch.canonical("keywords=Example+role&location=Example+City")
    assert target is None and "C-SRCH-2" in why


async def test_the_tool_refuses_a_place_and_loads_nothing():
    refused = await server.linkedin_set_search_job_alert(KEYWORDS, "Example City")
    assert refused["error"] == "bad_argument" and refused["performed"] is False
    assert "Nothing was loaded" in refused["message"] and "Example City" not in refused["message"]


@pytest.mark.parametrize(
    "landed, on_search",
    [("https://www.linkedin.com/jobs/search-results/?keywords=Example+role", True),
     ("https://www.linkedin.com/jobs/search-results/?keywords=Example+role&origin=JOB_SEARCH_PAGE_JOB_FILTER", True),
     ("https://www.linkedin.com/jobs/search/?keywords=Example+role", True),
     ("https://www.linkedin.com/jobs/search-results/?keywords=Another+role", False),
     ("https://www.linkedin.com/jobs/search-results/", False),
     ("https://www.linkedin.com/jobs/collections/recommended/?keywords=Example+role", False),
     ("https://example.com/jobs/search-results/?keywords=Example+role", False)],
)
def test_the_landing_may_be_either_route_and_must_be_the_same_search(landed, on_search):
    assert search_alert_switch.landed_on_search(landed, QUERY) is on_search


# ---------------------------------------------------------------------------
# 1. The reader on session 12's AI page
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("html", [AI_BASE, AI_SECOND], ids=["load-3", "load-4"])
async def test_session_12s_ai_switch_reads_off_on_its_own_arm(page, html):
    """RED BEFORE LANE JOBS7: the classic reader found no toggle here (unknown)."""
    facts, state, why = await _read(page, html)
    assert state == search_alert_switch.ALERT_OFF, why
    assert facts["arm"] == search_alert_switch.AI_ARM
    assert (facts["ai_toggles"], facts["ai_switches"], facts["switches_on_page"]) == (2, 1, 1)
    assert (facts["captions"], facts["captions_near_switch"]) == (1, 1)
    assert facts["aria_checked"] is None and facts["checked"] is False
    assert search_alert_switch.switch_for(facts) == search_alert_switch.AI_SWITCH


async def test_the_derived_on_world_reads_on(page):
    facts, state, why = await _read(page, ON_WORLD)
    assert state == search_alert_switch.ALERT_ON and "DERIVED" in why
    assert facts["checked"] is True


@pytest.mark.parametrize(
    "world, fragment",
    [(NO_CAPTION_WORLD, "not captioned"),
     (TWO_WORLD, "input switch"),
     (ARIA_WORLD, "aria-checked"),
     (NO_KEY_WORLD, "alert toggles"),
     (BOTH_WORLD, "both the classic")],
    ids=["no-caption", "two-switches", "an-aria-checked", "no-key-prefix", "both-arms"],
)
async def test_every_derived_ai_world_is_refused_and_says_why(page, world, fragment):
    _facts, state, why = await _read(page, world)
    assert state == search_alert_switch.UNKNOWN
    assert fragment in why, why


async def test_the_classic_capture_still_reads_off_on_its_own_arm(page):
    facts, state, _why = await _read(page, CLASSIC_BASE)
    assert state == search_alert_switch.ALERT_OFF
    assert facts["arm"] == search_alert_switch.CLASSIC_ARM
    assert search_alert_switch.switch_for(facts) == search_alert_switch.SWITCH


async def test_the_press_target_is_one_element_on_the_ai_page(page):
    await page.set_content(AI_BASE, wait_until="domcontentloaded", timeout=60_000)
    assert await page.locator(search_alert_switch.AI_SWITCH).count() == 1
    assert await page.locator(search_alert_switch.AI_TOGGLE).count() == 2


# ---------------------------------------------------------------------------
# 2. Preview, press and fresh render on the AI page -- both ways
# ---------------------------------------------------------------------------


async def test_set_previews_from_off_on_the_ai_page_and_mints(writes_on, page):
    nav = FixtureNavigator({URL: AI_BASE})
    block = await preview(SET_SPEC, target=QUERY, navigator=nav, page=page)
    assert nav.gotos == [URL]
    assert block["where"]["search"] == {"keywords": KEYWORDS, "location": ""}
    assert block["direction"]["currently"] == "alert_off"
    assert block["direction"]["after"] == "alert_on"
    assert isinstance(block["to_confirm"], str) and block["to_confirm"]


async def test_set_from_on_is_refused_on_the_ai_page(writes_on, page):
    nav = FixtureNavigator({URL: ON_WORLD})
    with pytest.raises(WriteAttemptError):
        await preview(SET_SPEC, target=QUERY, navigator=nav, page=page)
    assert not writes._GRANTS


async def _run(page, spec, before: str, after: str) -> dict:
    nav = FixtureNavigator({URL: before})
    block = await preview(spec, target=QUERY, navigator=nav, page=page)
    grant = consume(block["to_confirm"], action=spec.action, target=QUERY)
    act = FixtureNavigator({URL: [before, after]})
    receipt = await writes.perform(act, page, grant)
    assert act.gotos == [URL, URL], "the press and the fresh render, nothing else"
    return receipt


async def test_set_on_the_ai_page_presses_the_ai_switch_and_is_performed(writes_on, page):
    """RED BEFORE LANE JOBS7: the press aimed the classic toggle's switch."""
    receipt = await _run(page, SET_SPEC, AI_BASE, ON_WORLD)
    assert receipt["clicked"]["selector"] == search_alert_switch.AI_SWITCH
    assert receipt["clicked"]["state_before"] == "alert_off"
    assert receipt["verification"]["observed_state"] == "alert_on"
    assert receipt["performed"] is True and receipt["verified"] is True


async def test_the_inverse_unset_on_the_ai_page_is_performed(writes_on, page):
    receipt = await _run(page, UNSET_SPEC, ON_WORLD, AI_BASE)
    assert receipt["clicked"]["selector"] == search_alert_switch.AI_SWITCH
    assert receipt["clicked"]["state_before"] == "alert_on"
    assert receipt["verification"]["observed_state"] == "alert_off"
    assert receipt["performed"] is True


async def test_a_set_whose_fresh_render_still_reads_off_is_not_performed(writes_on, page):
    receipt = await _run(page, SET_SPEC, AI_BASE, AI_BASE)
    assert receipt["verification"]["observed_state"] == "alert_off"
    assert receipt["performed"] is False


def test_the_anchor_is_the_ai_switchs_caption():
    for spec in (SET_SPEC, UNSET_SPEC):
        assert writes.anchor_label_for(spec) == search_alert_switch.CAPTION


def test_a_reading_carries_no_page_text():
    reading = {"arm": "ai_toggle", "toggles": 0, "switches_in_toggle": 0, "switches_on_page": 1,
               "word": None, "ai_toggles": 2, "ai_switches": 1, "captions": 1,
               "captions_near_switch": 1, "aria_checked": None, "checked": False}
    facts, state, _why = search_alert_switch.switch_verdict(reading)
    assert state == search_alert_switch.ALERT_OFF
    assert all(value is None or isinstance(value, (bool, int)) or value in (
        search_alert_switch.AI_ARM, search_alert_switch.CLASSIC_ARM, search_alert_switch.WORD,
        "other", "true", "false") for value in facts.values())
