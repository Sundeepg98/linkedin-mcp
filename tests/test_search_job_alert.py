"""``set_search_job_alert`` and its inverse ``unset_search_job_alert`` -- census row ``J 31``.

WHAT THE PAIR IS. The "Set alert" switch at the head of one job search's
results, turned on and turned off: a job alert is his own saved search, sent
to nobody (``HIS-OWN-CURATION-NOT-OUTWARD``), so the pair is built behind the
grant, off by default, each the other's inverse in one change.

WHAT IS MEASURED AND WHAT IS NOT, so no test claims more. The OFF shape is
MEASURED on live session 2's classic job search,
``tests/fixtures/live2/j107_search_alert.html`` (the tracked copy ``j107.html``
with the toggle's word written by keyed shape): one toggle wearing LinkedIn's
class ``jobs-search-create-alert__artdeco-toggle``, its word "Set alert", one
``input[role=switch]`` in it drawing aria-checked off. The ON shape is NOT
measured: every world below that needs it is DERIVED from the fixture by
asserted edits (aria-checked on, the ``checked`` attribute). The tracked copy
itself, its word reduced to ``x``, is asserted to read ``unknown``.

NOTHING HERE REACHES LINKEDIN. Every page is the tracked capture or a
derivation of one, served into a local headless Chromium whose page aborts
every request the skeleton's stylesheet and image addresses would start.
"""
from __future__ import annotations

import json

import pytest

from linkedin_server import search_alert_switch, server, writes
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

#: A search with a location, and one without: declared shapes, not his data.
KEYWORDS = "Example role"
LOCATION = "Example City"
QUERY, _ = search_alert_switch.query_for(KEYWORDS, LOCATION)
URL = SET_SPEC.url_template.format(target=QUERY)

#: The tracked capture every derived world starts from (session 2, MEASURED).
BASE = markup("live2/j107_search_alert")
#: The plain tracked copy of the same capture: its toggle word reduced to x.
REDUCED = markup("live2/j107")

_SWITCH = '<input role="switch" aria-checked="false"'


def _derive(old: str, new: str, *, source: str = BASE, count: int = 1) -> str:
    """An ASSERTED edit: a replace whose anchor drifted is a silent no-op."""
    derived = source.replace(old, new, count)
    assert derived != source, f"the derivation anchored on {old!r} changed nothing"
    return derived


#: DERIVED -- the switch on: aria-checked on, the input checked.
ON_WORLD = _derive(_SWITCH, '<input role="switch" aria-checked="true" checked=""')
#: DERIVED -- aria-checked says on, the property says off: they disagree.
DISAGREE_WORLD = _derive(_SWITCH, '<input role="switch" aria-checked="true"')
#: DERIVED -- a second switch inside the toggle.
_INPUT = BASE[BASE.index(_SWITCH): BASE.index(">", BASE.index(_SWITCH)) + 1]
TWO_WORLD = _derive(_INPUT, _INPUT + _INPUT)
#: DERIVED -- the toggle without LinkedIn's class for it.
NO_TOGGLE_WORLD = _derive(f"{search_alert_switch.TOGGLE_CLASS} ", "example-toggle ")
#: DERIVED -- the toggle's word is not the measured one.
OTHER_WORD_WORLD = _derive("\nSet alert\n</span>", "\nExample word\n</span>")


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
# 0. The address: composed from his two arguments, one spelling, vetoed by the page
# ---------------------------------------------------------------------------


def test_the_query_is_his_two_values_in_one_spelling():
    assert QUERY == "keywords=Example+role&location=Example+City"
    assert search_alert_switch.query_for(KEYWORDS, "") == ("keywords=Example+role", "")
    assert search_alert_switch.query_for("  Example role  ", " Example City ")[0] == QUERY
    assert search_alert_switch.canonical(QUERY) == (QUERY, "")
    assert URL == "https://www.linkedin.com/jobs/search/?keywords=Example+role&location=Example+City"
    assert SET_SPEC.url_pattern.match(URL) and UNSET_SPEC.url_pattern.match(URL)


@pytest.mark.parametrize(
    "keywords, location",
    [("", ""), ("   ", "Example City"), ("x" * 201, ""), ("Example\nrole", ""),
     ("Example role", "y" * 101), (None, "")],
    ids=["empty", "blank", "too-long", "control-character", "location-too-long", "not-text"],
)
def test_a_search_that_cannot_be_composed_is_refused_and_not_repeated(keywords, location):
    query, why = search_alert_switch.query_for(keywords, location)
    assert query is None and why
    if isinstance(keywords, str) and keywords.strip():
        assert keywords not in why


@pytest.mark.parametrize(
    "target",
    ["location=Example+City&keywords=Example+role", "keywords=Example+role&f_WT=2",
     "keywords=Example%20role", "keywords=Example+role&location=", "keywords=a&keywords=b",
     "https://www.linkedin.com/jobs/search/?keywords=Example+role"],
    ids=["reordered", "a-filter", "another-spelling", "an-empty-location", "a-repeated-key",
         "a-whole-url"],
)
def test_a_target_not_in_the_one_spelling_is_refused(target):
    assert search_alert_switch.canonical(target)[0] is None
    with pytest.raises(WriteAttemptError, match="addressed by one job search"):
        writes._target_for(SET_SPEC, target)


@pytest.mark.parametrize(
    "landed, on_search",
    [(URL, True),
     (URL + "&geoId=100000000&refresh=true", True),
     ("https://www.linkedin.com/jobs/search?keywords=Example+role&location=Example+City", True),
     ("https://www.linkedin.com/jobs/search-results/?keywords=Example+role", False),
     ("https://www.linkedin.com/jobs/search/?keywords=Another+role&location=Example+City", False),
     ("https://www.linkedin.com/jobs/search/?keywords=Example+role", False),
     ("https://www.linkedin.com/jobs/search/?keywords=Example+role&keywords=Another&location=Example+City", False),
     ("https://example.com/jobs/search/?keywords=Example+role&location=Example+City", False)],
    ids=["the-same", "linkedin-added-params", "no-trailing-slash", "the-ai-search",
         "other-keywords", "the-location-dropped", "keywords-twice", "another-host"],
)
def test_the_page_may_veto_the_search_and_never_supply_one(landed, on_search):
    assert search_alert_switch.landed_on_search(landed, QUERY) is on_search


# ---------------------------------------------------------------------------
# 1. The capture draws what the reader reads
# ---------------------------------------------------------------------------


async def test_session_2s_search_reads_off(page):
    facts, state, why = await _read(page, BASE)
    assert state == search_alert_switch.ALERT_OFF == SET_SPEC.from_state, why
    assert facts["toggles"] == facts["switches_in_toggle"] == facts["switches_on_page"] == 1
    assert facts["word"] == "Set alert"
    assert facts["aria_checked"] == "false" and facts["checked"] is False


async def test_the_tracked_copy_with_its_word_reduced_reads_unknown(page):
    facts, state, why = await _read(page, REDUCED)
    assert state == search_alert_switch.UNKNOWN
    assert facts["word"] == "other"
    assert "measured word" in why


async def test_the_derived_on_world_reads_on(page):
    _facts, state, why = await _read(page, ON_WORLD)
    assert state == search_alert_switch.ALERT_ON == UNSET_SPEC.from_state, why
    assert "DERIVED" in why


@pytest.mark.parametrize(
    "world, fragment",
    [
        (DISAGREE_WORLD, "they disagree"),
        (TWO_WORLD, "2 input switch(es)"),
        (NO_TOGGLE_WORLD, "0 alert toggles"),
        (OTHER_WORD_WORLD, "measured word"),
    ],
    ids=["aria-and-property-disagree", "two-switches", "no-toggle-class", "another-word"],
)
async def test_every_derived_world_is_refused_and_says_why(page, world, fragment):
    _facts, state, why = await _read(page, world)
    assert state == search_alert_switch.UNKNOWN
    assert fragment in why


def test_a_reader_failure_is_reported_by_type_only():
    _f, state, why = search_alert_switch.switch_verdict({"error": "TimeoutError"})
    assert state == search_alert_switch.UNKNOWN and "TimeoutError" in why


def test_the_selectors_are_built_from_linkedins_class_alone():
    assert search_alert_switch.TOGGLE == "div.jobs-search-create-alert__artdeco-toggle"
    assert search_alert_switch.SWITCH.startswith(search_alert_switch.TOGGLE + " ")
    assert search_alert_switch.TOGGLE_WORD.startswith(search_alert_switch.TOGGLE + " > ")


# ---------------------------------------------------------------------------
# 2. The preview: one load, the search named by his two values, a token minted
# ---------------------------------------------------------------------------


async def test_set_previews_from_off_and_mints(writes_on, page):
    nav = FixtureNavigator({URL: BASE})
    block = await preview(SET_SPEC, target=QUERY, navigator=nav, page=page)
    assert nav.gotos == [URL]
    assert block["where"]["search"] == {"keywords": KEYWORDS, "location": LOCATION}
    assert block["where"]["target"] == QUERY
    assert block["read"]["same_page_as_the_action"] is True
    assert block["read"]["page_loads"] == 1
    assert block["direction"]["currently"] == "alert_off"
    assert block["direction"]["after"] == "alert_on"
    # An unmeasured verdict may not wear a measured class (the gate refuses it):
    # the inverse is BUILT, and whether it restores the On shape is unmeasured.
    assert block["reversibility_class"] == "STILL-UNKNOWN"
    assert isinstance(block["to_confirm"], str) and block["to_confirm"]


async def test_set_from_on_is_refused_and_mints_nothing(writes_on, page):
    nav = FixtureNavigator({URL: ON_WORLD})
    with pytest.raises(WriteAttemptError):
        await preview(SET_SPEC, target=QUERY, navigator=nav, page=page)
    assert not writes._GRANTS, "a refused preview minted a grant"


async def test_unset_previews_from_on_and_is_refused_from_off(writes_on, page):
    nav = FixtureNavigator({URL: ON_WORLD})
    block = await preview(UNSET_SPEC, target=QUERY, navigator=nav, page=page)
    assert block["direction"]["currently"] == "alert_on"
    assert block["direction"]["after"] == "alert_off"
    writes.discard_all()
    nav = FixtureNavigator({URL: BASE})
    with pytest.raises(WriteAttemptError):
        await preview(UNSET_SPEC, target=QUERY, navigator=nav, page=page)
    assert not writes._GRANTS


@pytest.mark.parametrize(
    "world",
    [DISAGREE_WORLD, TWO_WORLD, NO_TOGGLE_WORLD, OTHER_WORD_WORLD, REDUCED],
    ids=["aria-and-property-disagree", "two-switches", "no-toggle-class", "another-word",
         "the-reduced-copy"],
)
async def test_the_preview_refuses_every_unknown_world(writes_on, page, world):
    nav = FixtureNavigator({URL: world})
    with pytest.raises(WriteAttemptError):
        await preview(SET_SPEC, target=QUERY, navigator=nav, page=page)
    assert not writes._GRANTS


async def test_the_preview_refuses_a_landing_on_another_search(writes_on, page):
    class Elsewhere(FixtureNavigator):
        async def goto(self, page, url, **kwargs):
            await super().goto(page, url, **kwargs)
            return "https://www.linkedin.com/jobs/search-results/?keywords=Example+role"

    nav = Elsewhere({URL: BASE})
    with pytest.raises(WriteAttemptError) as excinfo:
        await preview(SET_SPEC, target=QUERY, navigator=nav, page=page)
    assert "search-results" not in str(excinfo.value), "the landing was quoted"
    assert not writes._GRANTS


# ---------------------------------------------------------------------------
# 3. THE THREE CONTROLS -- writes off, another target or verb, a second use
# ---------------------------------------------------------------------------


async def test_control_1_it_refuses_with_writes_off(monkeypatch, page):
    monkeypatch.delenv(writes.WRITES_FLAG, raising=False)
    nav = FixtureNavigator({URL: BASE})
    with pytest.raises(WriteAttemptError, match="disabled"):
        await preview(SET_SPEC, target=QUERY, navigator=nav, page=page)
    off = await server._write_tool(SET, QUERY, "")
    assert off["error"] == "writes_disabled" and off["performed"] is False
    tool_off = await server.linkedin_set_search_job_alert(KEYWORDS, LOCATION)
    assert tool_off["error"] == "writes_disabled" and tool_off["performed"] is False
    assert nav.gotos == []


async def test_control_1b_a_search_the_tool_cannot_compose_loads_nothing():
    refused = await server.linkedin_set_search_job_alert("   ")
    assert refused["error"] == "bad_argument" and refused["performed"] is False
    assert "Nothing was loaded" in refused["message"]


async def test_control_2_a_grant_binds_its_search_and_its_verb(writes_on, page):
    nav = FixtureNavigator({URL: BASE})
    block = await preview(SET_SPEC, target=QUERY, navigator=nav, page=page)
    other, _ = search_alert_switch.query_for("Another role", LOCATION)
    with pytest.raises(WriteAttemptError, match="minted for target"):
        consume(block["to_confirm"], action=SET, target=other)
    nav = FixtureNavigator({URL: BASE})
    block = await preview(SET_SPEC, target=QUERY, navigator=nav, page=page)
    for verb in (UNSET, "set_similar_jobs_alert", "save_job"):
        with pytest.raises(WriteAttemptError, match="minted for 'set_search_job_alert'"):
            consume(block["to_confirm"], action=verb, target=QUERY)


async def test_control_3_a_grant_is_used_once(writes_on, page):
    nav = FixtureNavigator({URL: BASE})
    block = await preview(SET_SPEC, target=QUERY, navigator=nav, page=page)
    grant = consume(block["to_confirm"], action=SET, target=QUERY)
    first = FixtureNavigator({URL: [BASE, ON_WORLD]})
    receipt = await writes.perform(first, page, grant)
    assert receipt["clicked"]["clicks_made"] == 1
    second = FixtureNavigator({URL: BASE})
    with pytest.raises(WriteAttemptError, match="already been used once"):
        await writes.perform(second, page, grant)
    assert second.gotos == []


# ---------------------------------------------------------------------------
# 4. End to end: press the switch, confirm on a fresh render -- both ways
# ---------------------------------------------------------------------------


async def _run(page, spec, before: str, after: str) -> dict:
    nav = FixtureNavigator({URL: before})
    block = await preview(spec, target=QUERY, navigator=nav, page=page)
    grant = consume(block["to_confirm"], action=spec.action, target=QUERY)
    act = FixtureNavigator({URL: [before, after]})
    receipt = await writes.perform(act, page, grant)
    assert act.gotos == [URL, URL], "the press and the fresh render, nothing else"
    return receipt


async def test_set_whose_fresh_render_reads_on_is_performed(writes_on, page):
    receipt = await _run(page, SET_SPEC, BASE, ON_WORLD)
    assert receipt["clicked"]["selector"] == search_alert_switch.SWITCH
    assert receipt["clicked"]["error"] is None
    assert receipt["clicked"]["state_before"] == "alert_off"
    assert receipt["verification"]["observed_state"] == "alert_on"
    assert receipt["performed"] is True and receipt["verified"] is True


async def test_set_whose_fresh_render_still_reads_off_is_not_performed(writes_on, page):
    receipt = await _run(page, SET_SPEC, BASE, BASE)
    assert receipt["verification"]["observed_state"] == "alert_off"
    assert receipt["performed"] is False


async def test_the_inverse_unset_whose_fresh_render_reads_off_is_performed(writes_on, page):
    receipt = await _run(page, UNSET_SPEC, ON_WORLD, BASE)
    assert receipt["clicked"]["state_before"] == "alert_on"
    assert receipt["verification"]["observed_state"] == "alert_off"
    assert receipt["performed"] is True


async def test_a_fresh_render_without_the_toggle_is_unknown(writes_on, page):
    receipt = await _run(page, SET_SPEC, BASE, NO_TOGGLE_WORLD)
    assert receipt["verification"]["observed_state"] == "unknown"
    assert receipt["performed"] == writes.UNKNOWN


def test_the_tables_name_both_actions():
    for action, spec in ((SET, SET_SPEC), (UNSET, UNSET_SPEC)):
        assert action in writes.PERFORMABLE
        assert action in writes.STRICT_PRESS_ACTIONS
        assert action in writes._TOGGLE_ACTIONS
        assert "switch" in writes._WHERE_TO_LOOK[action]
        assert "RE-RENDERED" in writes._VERIFIED_FROM[action]
        assert writes.anchor_label_for(spec) == search_alert_switch.WORD
        assert writes.grant_is_possible(spec)
        assert spec.target_kind == "job_search"
        assert callable(getattr(server, "linkedin_" + action, None))
    assert SET_SPEC.from_state == UNSET_SPEC.to_state
    assert SET_SPEC.to_state == UNSET_SPEC.from_state
    assert search_alert_switch.ACTIONS == (SET, UNSET)


def test_the_block_names_the_search_and_no_label_text():
    # The toggle's hidden label is never read: no reading carries it.
    reading = {"toggles": 1, "switches_in_toggle": 1, "switches_on_page": 1,
               "word": "Set alert", "aria_checked": "false", "checked": False}
    facts, state, _why = search_alert_switch.switch_verdict(reading)
    assert state == search_alert_switch.ALERT_OFF
    assert set(facts) == {"toggles", "switches_in_toggle", "switches_on_page", "word",
                          "aria_checked", "checked"}
    assert json.dumps(facts)
