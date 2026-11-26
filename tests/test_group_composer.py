"""A post in ONE group he names -- census row ``M C64``.

WHAT IS BUILT (lane build-msg2, 2026-11-26), behind the single-use grant on
EVERY-OUTWARD-CLASS-BUILT-BEHIND-GRANTS: ``linkedin_publish_group_post`` --
the group page's closed share box, its trigger ``Start a public post``
pressed, his words typed only into ONE empty group composer, and ``Post``
pressed only when the editor holds exactly those words with Post turned on.
Receipt-only: what Post leaves in a group has never been drawn.

WHAT IS MEASURED AND WHAT IS NOT. Every world's MARKUP is live session 11's
own (load 36): the closed group page and the open composer, with LinkedIn's
words put back by keyed shape (``tests/group_composer_worlds.py``). What
typing does to Post is the disabled-while-empty shape the capture measures;
what Post does is NOT measured, and every world that varies it names it.

NOTHING HERE REACHES LINKEDIN. Every page is set into a local headless
Chromium by the navigator below, every request refused.
"""
from __future__ import annotations

from typing import Any, Optional

import pytest

from linkedin_server import group_composer as gc
from linkedin_server import server, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, perform, preview, spec_for_action
from tests import group_composer_worlds as w
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

#: Invented digits and invented words.
GROUP = "1234567"
GROUP_URL = f"https://www.linkedin.com/groups/{GROUP}/"
TEXT = "A synthetic post written for this test world."
ACTION = "publish_group_post"


class _Navigator:
    """Serves frozen worlds for the group's address, in order (the last one
    repeats), and RECORDS every ask with the page's own press counters."""

    def __init__(self, worlds: list[str], *, landed: Optional[str] = None):
        self.worlds = list(worlds)
        self.gotos: list[str] = []
        self.pressed: list[Any] = []
        self.landed = landed

    async def goto(self, page, url: str) -> str:
        self.gotos.append(url)
        if url != GROUP_URL:
            raise AssertionError(f"the gate asked for {url!r}, which this test did not freeze")
        self.pressed.append(await page.evaluate("() => window.__presses || null"))
        html = self.worlds.pop(0) if len(self.worlds) > 1 else self.worlds[0]
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return self.landed if self.landed is not None else url


@pytest.fixture(autouse=True)
def _no_grants_survive_a_test():
    yield
    writes.discard_all()


@pytest.fixture(autouse=True)
def _fast_polls(monkeypatch):
    """The polls' INTERVAL pushed down for documents that change only on a
    timer the test sets; the COUNT -- the property -- is kept."""
    monkeypatch.setattr(gc, "POLL_MS", 20)


@pytest.fixture
async def page(browser_page):
    """The shared local browser's page, with EVERY request refused."""

    async def _refuse(route) -> None:
        await route.abort()

    await browser_page.route("**/*", _refuse)
    yield browser_page


async def _witness(page) -> dict[str, Any]:
    return await page.evaluate("() => window.__presses")


async def _granted(page, nav: _Navigator):
    spec = spec_for_action(ACTION)
    block = await preview(spec, target={"group": GROUP, "text": TEXT}, navigator=nav, page=page)
    target = writes._target_for(spec, {"group": GROUP, "text": TEXT})
    return consume(block["to_confirm"], action=ACTION, target=target), block


# ---------------------------------------------------------------------------
# 1. The captures, read by the module's own readers
# ---------------------------------------------------------------------------


async def test_the_captures_read_as_measured_and_the_feed_composer_is_told_apart(page):
    await page.set_content(w.CLOSED_PAGE, wait_until="domcontentloaded")
    assert gc.box_state(await gc.read_box(page))[0] == gc.BOX_CLOSED

    await page.set_content(w.OPEN_PAGE, wait_until="domcontentloaded")
    opened = gc.opened_gate(await gc.read_composer(page))
    assert opened["proceed"] is True, opened

    # SHOWN FAILING ON REAL MARKUP: the FEED's own composer (load 25) draws
    # Schedule post, and the group composer's gate refuses it.
    await page.set_content(w.FEED_COMPOSER_PAGE, wait_until="domcontentloaded")
    feed = gc.opened_gate(await gc.read_composer(page))
    assert feed["proceed"] is False and feed["refused_condition"] == "4_feed_composer"


def test_a_group_is_named_by_its_digits_and_a_name_is_never_repeated():
    spec = spec_for_action(ACTION)
    canonical = writes._target_for(spec, {"group": GROUP, "text": TEXT})
    assert canonical == GROUP + writes.TARGET_JOIN + TEXT
    assert writes.url_target_of(spec, canonical) == GROUP
    assert spec.url_template.format(target=writes.url_target_of(spec, canonical)) == GROUP_URL
    name = "Synthetic Person Group"
    with pytest.raises(WriteAttemptError) as refused:
        writes._target_for(spec, {"group": name, "text": TEXT})
    assert name not in str(refused.value)


# ---------------------------------------------------------------------------
# 2. The preview: one load, nothing pressed
# ---------------------------------------------------------------------------


async def test_the_preview_reads_the_closed_box_and_presses_nothing(writes_on, page):
    nav = _Navigator([w.world()])
    _grant, block = await _granted(page, nav)
    assert nav.gotos == [GROUP_URL]
    assert block["direction"]["currently"] == gc.BOX_CLOSED
    shown = block["where"]["what_the_page_showed"]
    assert shown["landed_on_the_named_group"] is True
    assert shown["audience"]["says"] == "public"
    # GROUP-POST-AUDIENCE-FROM-ITS-TRIGGER, condition 1 (the orchestrator, round
    # 2): the preview shows the trigger's label VERBATIM, before any grant.
    assert shown["audience"]["trigger_words"] == "Start a public post"
    assert "Start a public post" in str(block)
    assert await _witness(page) == {"trigger": 0, "post": 0, "typed": 0, "other": 0}
    assert block["verification"]["outcome_is_verifiable"] == "NO"
    assert block["irreversible"] is True
    assert TEXT in str(block)


async def test_the_preview_refuses_a_landing_on_another_page(writes_on, page):
    nav = _Navigator([w.world()], landed="https://www.linkedin.com/feed/")
    with pytest.raises(WriteAttemptError, match="did not land on the group you named"):
        await preview(spec_for_action(ACTION), target={"group": GROUP, "text": TEXT},
                      navigator=nav, page=page)


# ---------------------------------------------------------------------------
# 3. The confirmed press
# ---------------------------------------------------------------------------


async def test_his_words_are_typed_into_the_empty_composer_and_post_pressed(writes_on, page):
    nav = _Navigator([w.world(), w.world()])
    grant, _block = await _granted(page, nav)
    receipt = await perform(nav, page, grant)
    presses = await _witness(page)
    assert presses["trigger"] == 1 and presses["post"] == 1 and presses["typed"] >= 1
    assert presses["other"] == 0
    assert receipt["clicked"]["clicks_made"] == 2 and receipt["clicked"]["opener_clicks"] == 1
    assert receipt["group_composer_gate"]["proceeded"] is True
    assert receipt["publish_gate"]["proceeded"] is True
    assert receipt["group_composer_gate"]["after_post"]["modals"] == 0
    assert receipt["verification"]["outcome_is_verifiable"] == "NO"
    assert nav.gotos == [GROUP_URL, GROUP_URL], "a receipt-only act loaded again"


@pytest.mark.parametrize(
    "config,condition",
    [
        ({"openDrawsSchedule": True}, "4_feed_composer"),
        ({"openHoldsText": True}, "2_editor_not_one_blank"),
        ({"triggerDoesNothing": True}, "1_not_one_composer"),
    ],
    ids=["a-feed-composer", "a-composer-holding-a-draft", "a-trigger-that-opens-nothing"],
)
async def test_no_word_is_typed_into_a_composer_that_is_not_the_measured_one(
    writes_on, page, config, condition
):
    """SHOWN FAILING, three ways: the opened gate refuses, nothing is typed and
    Post is never pressed."""
    nav = _Navigator([w.world(), w.world(**config)])
    grant, _block = await _granted(page, nav)
    receipt = await perform(nav, page, grant)
    presses = await _witness(page)
    assert presses["trigger"] == 1 and presses["post"] == 0
    assert presses["typed"] == 0
    assert receipt["group_composer_gate"]["proceeded"] is False
    assert receipt["group_composer_gate"]["refused_condition"] == condition
    assert receipt["publish_gate"] is None


@pytest.mark.parametrize(
    "config,condition",
    [
        ({"postStaysDisabled": True}, "3_post_not_enabled"),
        ({"typingAltered": True}, "2_words_not_exact"),
    ],
    ids=["post-never-turns-on", "the-words-changed-as-they-landed"],
)
async def test_post_is_not_pressed_unless_the_composer_holds_exactly_his_words(
    writes_on, page, config, condition
):
    """SHOWN FAILING, two ways: his words went in, and the Post gate refuses."""
    nav = _Navigator([w.world(), w.world(**config)])
    grant, _block = await _granted(page, nav)
    receipt = await perform(nav, page, grant)
    presses = await _witness(page)
    assert presses["trigger"] == 1 and presses["typed"] >= 1 and presses["post"] == 0
    assert receipt["group_composer_gate"]["proceeded"] is True
    assert receipt["publish_gate"]["proceeded"] is False
    assert receipt["publish_gate"]["refused_condition"] == condition


@pytest.mark.parametrize(
    "config", [{"openAfterMs": 120}, {"enableAfterMs": 120}],
    ids=["a-composer-that-opens-late", "a-post-that-turns-on-late"],
)
async def test_a_composer_or_a_post_that_arrives_late_is_waited_for(writes_on, page, config):
    """A live modal animates in and a live Post turns on after the words land:
    each gate reads after a bounded wait, which decides nothing."""
    nav = _Navigator([w.world(), w.world(**config)])
    grant, _block = await _granted(page, nav)
    receipt = await perform(nav, page, grant)
    presses = await _witness(page)
    assert presses["trigger"] == 1 and presses["post"] == 1
    assert receipt["publish_gate"]["proceeded"] is True


@pytest.mark.parametrize(
    "config,gate,condition",
    [
        ({"openAfterMs": 120}, "group_composer_gate", "1_not_one_composer"),
        ({"enableAfterMs": 120}, "publish_gate", "3_post_not_enabled"),
    ],
    ids=["no-wait-for-the-composer", "no-wait-for-post"],
)
async def test_without_the_wait_the_same_world_is_refused(writes_on, page, monkeypatch, config, gate, condition):
    """SHOWN FAILING: the bound taken to zero polls, the same late worlds are
    refused -- so the waits above are what let a live fire through."""
    monkeypatch.setattr(gc, "POLLS", 0)
    nav = _Navigator([w.world(), w.world(**config)])
    grant, _block = await _granted(page, nav)
    receipt = await perform(nav, page, grant)
    assert receipt[gate]["proceeded"] is False
    assert receipt[gate]["refused_condition"] == condition
    assert (await _witness(page))["post"] == 0


async def test_a_wrong_landing_at_the_act_presses_nothing(writes_on, page):
    nav = _Navigator([w.world()])
    grant, _block = await _granted(page, nav)
    nav.landed = "https://www.linkedin.com/groups/7654321/"
    with pytest.raises(WriteAttemptError, match="landed somewhere that is not that group"):
        await perform(nav, page, grant)
    assert (await _witness(page))["trigger"] == 0


# ---------------------------------------------------------------------------
# 4. The tool
# ---------------------------------------------------------------------------


async def test_the_tool_is_registered_with_the_group_and_the_words():
    tools = {tool.name: tool for tool in await server.mcp.list_tools()}
    tool = tools["linkedin_publish_group_post"]
    assert sorted((tool.parameters or {}).get("properties") or {}) == [
        "confirm_token", "group_id", "text",
    ]
    assert spec_for_action(ACTION).tool_name == "linkedin_publish_group_post"
    assert ACTION in writes.PERFORMABLE and ACTION in writes.TYPING_ACTIONS
    assert ACTION in writes.GROUP_COMPOSER_ACTIONS
