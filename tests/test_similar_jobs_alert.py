"""``set_similar_jobs_alert`` and its inverse ``unset_similar_jobs_alert`` -- census row ``J 161``.

WHAT THE PAIR IS. The posting's own "Set alert for similar jobs" switch, turned
on and turned off: a job alert is his own saved query, sent to nobody
(``HIS-OWN-CURATION-NOT-OUTWARD``), so the pair is built behind the grant,
off by default, each the other's inverse in one change.

WHAT IS MEASURED AND WHAT IS NOT, so no test claims more. The OFF shape is
MEASURED on live session 8's posting, ``tests/fixtures/live8/posting.html``:
one block headed "Set alert for similar jobs", one ``input[role=switch]`` in it
labelled ``dom.JOB_ALERT_HEADING_PREFIX`` + the title, the word ``Off`` beside
it. The ON shape is NOT measured: every world below that needs it is DERIVED
from the fixture by asserted edits (the word ``On``, the ``checked``
attribute). The August capture's older shape (a ``div[role=switch]``) is
asserted to read ``unknown``.

NOTHING HERE REACHES LINKEDIN. Every page is the tracked capture or a
derivation of one, served into a local headless Chromium whose page aborts
every request the skeleton's stylesheet and image addresses would start.
"""
from __future__ import annotations

import json

import pytest

from linkedin_server import dom, job_alert_switch, server, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_writes import (  # noqa: F401 -- two of these are fixtures
    JOB,
    FixtureNavigator,
    browser_page,
    markup,
    writes_on,
)

SET = "set_similar_jobs_alert"
UNSET = "unset_similar_jobs_alert"
SET_SPEC = spec_for_action(SET)
UNSET_SPEC = spec_for_action(UNSET)
URL = SET_SPEC.url_template.format(target=JOB)

#: The tracked capture every derived world starts from (session 8, MEASURED).
BASE = markup("live8/posting")
#: The August capture, the OLDER shape of the same control (MEASURED).
AUGUST = markup("job_detail_hydrated")

_LABEL = 'aria-label="Set alert for similar jobs as Example Job Title" type="checkbox">'
#: The switch's whole label: never read into Python, so never in a block,
#: a refusal or a receipt.
LABEL_TEXT = "Set alert for similar jobs as Example Job Title"
_WORD_OFF = "\nOff\n</span>"


@pytest.fixture(autouse=True)
def _a_short_description_wait(monkeypatch):
    """MEASURED 2026-10-10: session 8's posting carries NO ``data-sdui-component``
    attribute at all (0 in the raw capture), so ``dom.JOB_DESCRIPTION_SLOT``
    never attaches on this markup and the posting reader's readiness wait runs
    its whole bound before reading the page, which it then reads in full. The
    bound is shortened here so each posting read does not spend ten seconds;
    what the reader reads is unchanged."""
    monkeypatch.setattr(dom, "JOB_DESCRIPTION_TIMEOUT_MS", 300)


def _derive(old: str, new: str, *, source: str = BASE, count: int = 1) -> str:
    """An ASSERTED edit: a replace whose anchor drifted is a silent no-op."""
    derived = source.replace(old, new, count)
    assert derived != source, f"the derivation anchored on {old!r} changed nothing"
    return derived


#: DERIVED -- the switch on: the word On, the input checked.
ON_WORLD = _derive(_WORD_OFF, "\nOn\n</span>", source=_derive(_LABEL, _LABEL[:-1] + " checked>"))
#: DERIVED -- the word says On, the property says off: they disagree.
DISAGREE_WORLD = _derive(_WORD_OFF, "\nOn\n</span>")
#: DERIVED -- two switches in the block.
_INPUT = BASE[BASE.index('<input role="switch"'): BASE.index(_LABEL) + len(_LABEL)]
TWO_WORLD = _derive(_INPUT, _INPUT + _INPUT)
#: DERIVED -- the switch's label does not carry LinkedIn's prefix.
NO_PREFIX_WORLD = _derive(_LABEL, 'aria-label="Example label" type="checkbox">')
#: DERIVED -- no block headed "Set alert for similar jobs".
NO_BLOCK_WORLD = _derive("\nSet alert for similar jobs\n</h2>", "\nExample heading\n</h2>")


@pytest.fixture
async def page(browser_page):
    """The shared local Chromium page, refusing every request it would start."""

    async def _refuse(route):
        await route.abort()

    await browser_page.route("**/*", _refuse)
    return browser_page


async def _read(page, html: str):
    await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
    return await job_alert_switch.read_state(page)


# ---------------------------------------------------------------------------
# 1. The capture draws what the reader reads
# ---------------------------------------------------------------------------


async def test_session_8s_posting_reads_off_and_the_toggle_takes_a_trial_press(page):
    facts, state, why = await _read(page, BASE)
    assert state == job_alert_switch.ALERT_OFF == SET_SPEC.from_state, why
    assert facts["blocks"] == facts["prefixed_in_block"] == facts["prefixed_on_page"] == 1
    assert facts["state_word"] == "Off" and facts["checked"] is False
    trial = await job_alert_switch.trial_press(page)
    assert trial == {"toggles": 1, "actionable": True, "error": None}


async def test_the_august_shape_reads_unknown_never_a_state(page):
    _facts, state, why = await _read(page, AUGUST)
    assert state == job_alert_switch.UNKNOWN
    assert "August shape" in why


async def test_the_derived_on_world_reads_on(page):
    _facts, state, why = await _read(page, ON_WORLD)
    assert state == job_alert_switch.ALERT_ON == UNSET_SPEC.from_state, why
    assert "DERIVED" in why


@pytest.mark.parametrize(
    "world, fragment",
    [
        (DISAGREE_WORLD, "they disagree"),
        (TWO_WORLD, "exactly one of each"),
        (NO_PREFIX_WORLD, "exactly one of each"),
        (NO_BLOCK_WORLD, "0 blocks"),
    ],
    ids=["word-and-property-disagree", "two-switches", "label-without-prefix", "no-block"],
)
async def test_every_derived_world_is_refused_and_says_why_without_the_title(page, world, fragment):
    _facts, state, why = await _read(page, world)
    assert state == job_alert_switch.UNKNOWN
    assert fragment in why
    assert "Example Job Title" not in why


def test_the_label_prefix_is_the_one_dom_already_names():
    assert dom.JOB_ALERT_HEADING_PREFIX == "Set alert for similar jobs as "
    assert dom.JOB_ALERT_HEADING_PREFIX in job_alert_switch.SWITCH
    assert job_alert_switch.TOGGLE == job_alert_switch.SWITCH + "/parent::*"


def test_a_reader_failure_is_reported_by_type_only():
    _f, state, why = job_alert_switch.switch_verdict({"error": "TimeoutError"})
    assert state == job_alert_switch.UNKNOWN and "TimeoutError" in why


# ---------------------------------------------------------------------------
# 2. The preview: one load, the posting named by its id, a token minted
# ---------------------------------------------------------------------------


async def test_set_previews_from_off_and_mints(writes_on, page):
    nav = FixtureNavigator({URL: BASE})
    block = await preview(SET_SPEC, target=JOB, navigator=nav, page=page)
    assert nav.gotos == [URL]
    assert block["where"]["job_id"] == JOB
    assert block["read"]["same_page_as_the_action"] is True
    assert block["read"]["page_loads"] == 1
    assert block["direction"]["currently"] == "alert_off"
    assert block["direction"]["after"] == "alert_on"
    # An unmeasured verdict may not wear a measured class (the gate refuses it):
    # the inverse is BUILT, and whether it restores the On shape is unmeasured.
    assert block["reversibility_class"] == "STILL-UNKNOWN"
    assert isinstance(block["to_confirm"], str) and block["to_confirm"]
    # The preview names the posting (PREVIEW-NAMES-THE-RESOLVED-TARGET); the
    # switch's own label, which carries the title again, is never read out.
    assert LABEL_TEXT not in json.dumps(block)


async def test_set_from_on_is_refused_with_its_own_note_and_mints_nothing(writes_on, page):
    nav = FixtureNavigator({URL: ON_WORLD})
    with pytest.raises(WriteAttemptError) as excinfo:
        await preview(SET_SPEC, target=JOB, navigator=nav, page=page)
    assert LABEL_TEXT not in str(excinfo.value)
    assert not writes._GRANTS, "a refused preview minted a grant"


async def test_unset_previews_from_on_and_is_refused_from_off(writes_on, page):
    nav = FixtureNavigator({URL: ON_WORLD})
    block = await preview(UNSET_SPEC, target=JOB, navigator=nav, page=page)
    assert block["direction"]["currently"] == "alert_on"
    assert block["direction"]["after"] == "alert_off"
    writes.discard_all()
    nav = FixtureNavigator({URL: BASE})
    with pytest.raises(WriteAttemptError):
        await preview(UNSET_SPEC, target=JOB, navigator=nav, page=page)
    assert not writes._GRANTS


@pytest.mark.parametrize(
    "world",
    [DISAGREE_WORLD, TWO_WORLD, NO_PREFIX_WORLD, NO_BLOCK_WORLD, AUGUST],
    ids=["word-and-property-disagree", "two-switches", "label-without-prefix", "no-block",
         "the-august-shape"],
)
async def test_the_preview_refuses_every_unknown_world(writes_on, page, world):
    nav = FixtureNavigator({URL: world})
    with pytest.raises(WriteAttemptError):
        await preview(SET_SPEC, target=JOB, navigator=nav, page=page)
    assert not writes._GRANTS


# ---------------------------------------------------------------------------
# 3. THE THREE CONTROLS -- writes off, another target or verb, a second use
# ---------------------------------------------------------------------------


async def test_control_1_it_refuses_with_writes_off(monkeypatch, page):
    monkeypatch.delenv(writes.WRITES_FLAG, raising=False)
    nav = FixtureNavigator({URL: BASE})
    with pytest.raises(WriteAttemptError, match="disabled"):
        await preview(SET_SPEC, target=JOB, navigator=nav, page=page)
    off = await server._write_tool(SET, JOB, "")
    assert off["error"] == "writes_disabled" and off["performed"] is False
    assert nav.gotos == []


async def test_control_2_a_grant_binds_its_posting_and_its_verb(writes_on, page):
    nav = FixtureNavigator({URL: BASE})
    block = await preview(SET_SPEC, target=JOB, navigator=nav, page=page)
    with pytest.raises(WriteAttemptError, match="minted for target"):
        consume(block["to_confirm"], action=SET, target="4600000043")
    nav = FixtureNavigator({URL: BASE})
    block = await preview(SET_SPEC, target=JOB, navigator=nav, page=page)
    for other in (UNSET, "save_job", "follow_company"):
        with pytest.raises(WriteAttemptError, match="minted for 'set_similar_jobs_alert'"):
            consume(block["to_confirm"], action=other, target=JOB)


async def test_control_3_a_grant_is_used_once(writes_on, page):
    nav = FixtureNavigator({URL: BASE})
    block = await preview(SET_SPEC, target=JOB, navigator=nav, page=page)
    grant = consume(block["to_confirm"], action=SET, target=JOB)
    first = FixtureNavigator({URL: [BASE, ON_WORLD]})
    receipt = await writes.perform(first, page, grant)
    assert receipt["clicked"]["clicks_made"] == 1
    second = FixtureNavigator({URL: BASE})
    with pytest.raises(WriteAttemptError, match="already been used once"):
        await writes.perform(second, page, grant)
    assert second.gotos == []


# ---------------------------------------------------------------------------
# 4. End to end: press the toggle, confirm on a fresh render -- both ways
# ---------------------------------------------------------------------------


async def _run(page, spec, before: str, after: str) -> dict:
    nav = FixtureNavigator({URL: before})
    block = await preview(spec, target=JOB, navigator=nav, page=page)
    grant = consume(block["to_confirm"], action=spec.action, target=JOB)
    act = FixtureNavigator({URL: [before, after]})
    receipt = await writes.perform(act, page, grant)
    assert act.gotos == [URL, URL], "the press and the fresh render, nothing else"
    return receipt


async def test_set_whose_fresh_render_reads_on_is_performed(writes_on, page):
    receipt = await _run(page, SET_SPEC, BASE, ON_WORLD)
    assert receipt["clicked"]["selector"] == job_alert_switch.TOGGLE
    assert receipt["clicked"]["error"] is None
    assert receipt["clicked"]["state_before"] == "alert_off"
    assert receipt["verification"]["observed_state"] == "alert_on"
    assert receipt["performed"] is True and receipt["verified"] is True
    assert LABEL_TEXT not in json.dumps(receipt)


async def test_set_whose_fresh_render_still_reads_off_is_not_performed(writes_on, page):
    receipt = await _run(page, SET_SPEC, BASE, BASE)
    assert receipt["verification"]["observed_state"] == "alert_off"
    assert receipt["performed"] is False


async def test_the_inverse_unset_whose_fresh_render_reads_off_is_performed(writes_on, page):
    receipt = await _run(page, UNSET_SPEC, ON_WORLD, BASE)
    assert receipt["clicked"]["state_before"] == "alert_on"
    assert receipt["verification"]["observed_state"] == "alert_off"
    assert receipt["performed"] is True


async def test_a_fresh_render_without_the_switch_is_unknown(writes_on, page):
    receipt = await _run(page, SET_SPEC, BASE, NO_BLOCK_WORLD)
    assert receipt["verification"]["observed_state"] == "unknown"
    assert receipt["performed"] == writes.UNKNOWN


def test_the_tables_name_both_actions():
    for action, spec in ((SET, SET_SPEC), (UNSET, UNSET_SPEC)):
        assert action in writes.PERFORMABLE
        assert action in writes.STRICT_PRESS_ACTIONS
        assert action in writes._TOGGLE_ACTIONS
        assert "switch" in writes._WHERE_TO_LOOK[action]
        assert "RE-RENDERED" in writes._VERIFIED_FROM[action]
        assert writes.anchor_label_for(spec) == dom.JOB_ALERT_HEADING_PREFIX
        assert writes.grant_is_possible(spec)
        assert callable(getattr(server, "linkedin_" + action, None))
    assert SET_SPEC.from_state == UNSET_SPEC.to_state
    assert SET_SPEC.to_state == UNSET_SPEC.from_state
