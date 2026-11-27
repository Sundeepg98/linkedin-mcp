"""``save_post`` -- census row ``M C36`` (``M C37`` rides it) -- built to ready-to-fire, unfired.

WHAT THE ACT IS. On the permalink of ONE feed item whose urn he names, the
item's own control menu is opened -- the trigger LinkedIn draws with its fixed
"Open control menu" prefix, ``feed_curation``'s -- and its ``Save`` item pressed,
only if the gate finds exactly one visible ``Save`` in the menu that pressed
trigger owns. Behind the grant, on SAVE-POST-UNDER-OWN-CURATION (the
orchestrator, 2026-11-27), under HIS-OWN-CURATION-NOT-OUTWARD. The
verification is IN PLACE.

THE PAGES ARE REAL. The closed world is live session 11's tracked copy of a
member's post's permalink (load 29); the open one is the same load with its
menu open, LinkedIn's menu words put back by keyed shape
(``tests/fixtures/synthetic/live11_permalink_menu_words.html``). The readers
are also shown on live session 12's two permalink menus, a member's post and a
Page's (``tests/fixtures/live12/permalink_*_menu-open.html``). PLANTED, each an
asserted edit: the trigger's label (LinkedIn's measured prefix and a SYNTHETIC
name, where the live label names the author); for a press-answering world, a
script that opens the menu as LinkedIn's does and draws what the press leaves
-- a fixture CHOICE named per world, because no capture holds it; and, for the
already-saved world, the menu's ``Save`` word replaced by the DERIVED ``Unsave``.

NOTHING HERE REACHES LINKEDIN: a local headless Chromium, every request the
page starts refused by its own route.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from linkedin_server import feed_curation as fc
from linkedin_server import feed_save as fs
from linkedin_server import readonly, server, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

REPO = Path(__file__).resolve().parents[1]
CLOSED_COPY = (REPO / "tests/fixtures/live11/permalink_member_post.html").read_text(encoding="ascii")
OPEN_WORDS = (REPO / "tests/fixtures/synthetic/live11_permalink_menu_words.html").read_text(encoding="ascii")
S12_MENUS = {
    "member": (REPO / "tests/fixtures/live12/permalink_member_post_menu-open.html").read_text(encoding="ascii"),
    "page": (REPO / "tests/fixtures/live12/permalink_page_post_menu-open.html").read_text(encoding="ascii"),
}

ACTION = fs.ACTION
SPEC = spec_for_action(ACTION)
#: A synthetic urn, from the identity guard's declared synthetic ids.
URN = "urn:li:activity:7400000000000000001"
URL = SPEC.url_template.format(target=URN)

#: A synthetic author, after LinkedIn's measured fixed prefix.
LABEL = fc.TRIGGER_PREFIX + " for post by Example Member"
_TRIGGER_CLOSED = (
    '<button class="ekfj5d ekfj5c ekft0 ekfa26 ekffvv ekfjpf ekfjqy ekfj5h ekfj5f '
    'ekfj5e ekfazu ekfh8u ekfh94 ekfjgk ekfjia ekfji6 ekffyi ekfgeu ekfh89" '
    'type="button" componentkey="x" aria-label="x"'
)
_OPEN_TAG = _TRIGGER_CLOSED + ' aria-expanded="true" data-floating-ui-inert="">'
_SAVE_WORD = ">\nSave\n<"


def _plant(markup: str, old: str, new: str, count: int = 1) -> str:
    assert markup.count(old) == count, (old[:60], markup.count(old))
    return markup.replace(old, new)


def _labelled_open(markup: str) -> str:
    return _plant(markup, _OPEN_TAG, _OPEN_TAG.replace('aria-label="x"', f'aria-label="{LABEL}"'))


#: THE CLOSED CAPTURE, its one trigger labelled: the preview's world.
CLOSED = _plant(CLOSED_COPY, _TRIGGER_CLOSED + ">", _TRIGGER_CLOSED.replace(
    'aria-label="x"', f'aria-label="{LABEL}"') + ">")

#: THE OPEN CAPTURE, labelled, as captured -- the menu open, its popover open.
OPEN = _labelled_open(OPEN_WORDS)

_SCRIPT = """<script>
window.__triggerPresses = 0; window.__itemPresses = 0; window.__otherPresses = 0;
document.addEventListener('click', function (e) {
  var trigger = e.target.closest('main button[aria-label^="Open control menu"]');
  var pop = document.querySelector('[data-floating-ui-portal] [popover]');
  if (trigger) {
    window.__triggerPresses += 1;
    trigger.setAttribute('aria-expanded', 'true');
    if (pop && !pop.matches(':popover-open')) pop.showPopover();
    return;
  }
  var item = e.target.closest('[role=menuitem]');
  if (!item) return;
  e.preventDefault();
  if ((item.textContent || '').replace(/\\s+/g, ' ').trim() !== 'Save') {
    window.__otherPresses += 1; return;
  }
  window.__itemPresses += 1;
  var leave = '%(leave)s';
  if (leave === 'open') return;
  if (pop) pop.hidePopover();
  document.querySelector('main button[aria-label^="Open control menu"]').removeAttribute('aria-expanded');
  if (leave === 'saved') {
    var d = document.createElement('div');
    d.setAttribute('role', 'status');
    d.innerHTML = '<p>Saved</p>';
    document.querySelector('main').appendChild(d);
  }
}, true);
</script>"""


def answering(leave: str, *, already_saved: bool = False) -> str:
    """The OPEN capture made closed -- the trigger's aria-expanded removed --
    with the press-answering script. DERIVED: what the item's press leaves is
    the test's choice (``saved``, ``nothing``, ``open``); an item already saved
    is DERIVED to draw ``Unsave`` in ``Save``'s place."""
    closed = _plant(OPEN, f'aria-label="{LABEL}" aria-expanded="true"', f'aria-label="{LABEL}"')
    if already_saved:
        closed = _plant(closed, _SAVE_WORD, ">\nUnsave\n<")
    return closed.replace("</body>", _SCRIPT % {"leave": leave} + "</body>", 1)


class Navigator:
    def __init__(self, *worlds: str):
        self.worlds = list(worlds)
        self.gotos: list[str] = []

    async def goto(self, page, url: str, **_kwargs) -> str:
        self.gotos.append(url)
        if url != URL:
            raise AssertionError(f"the gate asked for {url!r}, which this test did not freeze")
        html = self.worlds.pop(0) if len(self.worlds) > 1 else self.worlds[0]
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return url


async def _witness(page) -> dict[str, int]:
    return await page.evaluate(
        "() => ({trigger: window.__triggerPresses || 0, item: window.__itemPresses || 0,"
        " other: window.__otherPresses || 0})"
    )


@pytest.fixture
async def page(browser_page):
    async def _refuse(route):
        await route.abort("aborted")

    await browser_page.route("**/*", _refuse)
    # A TALL VIEWPORT, because the tracked copy carries none of LinkedIn's CSS.
    # Unstyled, each of the menu's seven items renders about 188 px tall, and
    # the popover -- top layer, centered, never scrollable -- puts its FIRST
    # item, ``Save``, above a 720 px viewport (measured: its box at y = -354),
    # where no click can reach it. ``Not interested``, fifth, lands on screen,
    # which is why mark_not_interested's tests never met this. The live menu
    # is styled and compact; this changes the harness, not what is pressed.
    await browser_page.set_viewport_size({"width": 1280, "height": 2400})
    return browser_page


@pytest.fixture(autouse=True)
def _no_grants_survive_a_test():
    yield
    writes.discard_all()


@pytest.fixture
def fast_menu(monkeypatch):
    monkeypatch.setattr(fs, "MENU_POLL_MS", 5)


# ---------------------------------------------------------------------------
# 0. Pure: the selectors, the verdicts
# ---------------------------------------------------------------------------


def test_the_selectors_are_feed_curations_trigger_and_owned_portal_never_a_name():
    assert fs.TRIGGER == fc.TRIGGER == 'main button[aria-label^="Open control menu"]'
    assert fs.URL_TEMPLATE == fc.URL_TEMPLATE
    assert "data-menu-portal-anchor" in fs.ITEM_IN_OWNED_MENU
    assert "@aria-owns" in fs.ITEM_IN_OWNED_MENU and "@id" in fs.ITEM_IN_OWNED_MENU
    assert "normalize-space(.)='Save'" in fs.ITEM_IN_OWNED_MENU
    assert "Example" not in fs.TRIGGER + fs.ITEM_IN_OWNED_MENU


def test_the_verdicts_say_what_they_saw_in_counts():
    one = {"triggers": 1, "triggers_visible": 1}
    assert fs.item_verdict(one)[1] == fs.SHOWN
    assert fs.item_verdict({"triggers": 2, "triggers_visible": 2})[1] == fs.UNKNOWN
    assert fs.item_verdict(dict(one, triggers_expanded=1))[1] == fs.UNKNOWN
    assert fs.item_verdict({})[1] == fs.UNKNOWN
    owned = {"triggers_expanded": 1, "items_visible": 1, "items_in_owned_menu": 1}
    assert fs.menu_verdict(owned)["proceed"] is True
    # An item already saved draws no Save: it refuses as not unique, by count.
    assert fs.menu_verdict(dict(owned, items_visible=0, items_in_owned_menu=0))["refused_condition"] == "item_not_unique"
    assert fs.menu_verdict(dict(owned, items_in_owned_menu=0))["refused_condition"] == "item_outside_the_owned_menu"
    assert fs.menu_verdict(dict(owned, triggers_expanded=0))["refused_condition"] == "menu_not_open"
    assert fs.menu_verdict({"error": "TimeoutError"})["refused_condition"] == "unreadable"
    # IN PLACE: a live region carrying "saved" is saved; the menu still open
    # with its item is not done; anything else is unknown -- never "not saved".
    assert fs.verification_verdict({"saved_regions": 1})[1] == fs.SAVED
    assert fs.verification_verdict(owned)[1] == fs.SHOWN
    assert fs.verification_verdict({"triggers": 1})[1] == fs.UNKNOWN


# ---------------------------------------------------------------------------
# 1. The captures draw what the readers read
# ---------------------------------------------------------------------------


async def test_the_readers_over_the_captures(page):
    async def read(html: str, show: bool = False):
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        if show:
            await page.evaluate(
                "() => document.querySelector('[data-floating-ui-portal] [popover]').showPopover()"
            )
        return await fs.read_item(page)

    # THE CLOSED CAPTURE, labelled: one trigger, closed -- shown.
    facts, state, why = fs.item_verdict(await read(CLOSED))
    assert state == fs.SHOWN, why
    assert (facts["triggers"], facts["triggers_expanded"], facts["items_visible"]) == (1, 0, 0)
    # THE RED: the tracked copy as captured, its trigger's label reduced to x.
    assert fs.item_verdict(await read(CLOSED_COPY))[1] == fs.UNKNOWN
    # THE OPEN CAPTURE (session 11): Save is in the menu the trigger owns.
    reading = await read(OPEN, show=True)
    assert (reading["triggers_expanded"], reading["items_visible"], reading["items_in_owned_menu"]) == (1, 1, 1)
    assert fs.menu_verdict(reading)["proceed"] is True
    # SESSION 12's two permalink menus, a member's post and a Page's: the same.
    for kind, markup in S12_MENUS.items():
        reading = await read(_labelled_open(markup), show=True)
        assert (reading["triggers_expanded"], reading["items_visible"],
                reading["items_in_owned_menu"]) == (1, 1, 1), kind
        assert fs.menu_verdict(reading)["proceed"] is True, kind
    # THE PORTAL NOT OWNED: the anchor names another id -- refused.
    stranger = _plant(OPEN, 'aria-owns="k2c1ddb96"', 'aria-owns="kffffffff"')
    reading = await read(stranger, show=True)
    assert reading["items_visible"] == 1 and reading["items_in_owned_menu"] == 0
    assert fs.menu_verdict(reading)["refused_condition"] == "item_outside_the_owned_menu"
    # AN ITEM ALREADY SAVED (DERIVED: Unsave in Save's place): nothing to press.
    reading = await read(_plant(OPEN, _SAVE_WORD, ">\nUnsave\n<"), show=True)
    assert reading["items_visible"] == 0
    assert fs.menu_verdict(reading)["refused_condition"] == "item_not_unique"


# ---------------------------------------------------------------------------
# 2. The preview, the controls
# ---------------------------------------------------------------------------


async def test_the_preview_mints_on_the_permalink_and_refuses_every_other_world(writes_on, page):
    nav = Navigator(CLOSED)
    block = await preview(SPEC, target=URN, navigator=nav, page=page)
    assert nav.gotos == [URL]
    assert block["direction"]["currently"] == fs.SHOWN
    assert block["direction"]["after"] == fs.SAVED
    assert block["reversibility_class"] == "STILL-UNKNOWN"
    assert block["where"]["url"] == URL
    assert "Example Member" not in json.dumps(block)
    writes.discard_all()
    two = _plant(CLOSED, f'aria-label="{LABEL}">',
                 f'aria-label="{LABEL}"></button><button type="button" aria-label="{LABEL}">')
    for label, html in (("the-reduced-copy", CLOSED_COPY), ("two-triggers", two)):
        with pytest.raises(WriteAttemptError) as raised:
            await preview(SPEC, target=URN, navigator=Navigator(html), page=page)
        assert not writes._GRANTS, label
        assert "Example Member" not in str(raised.value), label
    # A DESCRIPTION IS NO ADDRESS: refused before any load.
    words = "a feed post I liked"
    nav = Navigator(CLOSED)
    with pytest.raises(WriteAttemptError):
        await preview(SPEC, target=words, navigator=nav, page=page)
    assert nav.gotos == [] and not writes._GRANTS
    assert not SPEC.url_pattern.match(SPEC.url_template.format(target=words))


async def test_the_controls_writes_off_another_item_and_a_second_use(monkeypatch, page, fast_menu):
    monkeypatch.delenv(writes.WRITES_FLAG, raising=False)
    off = await server.linkedin_save_post(URN)
    assert off["error"] == "writes_disabled" and off["performed"] is False
    monkeypatch.setenv(writes.WRITES_FLAG, "1")
    block = await preview(SPEC, target=URN, navigator=Navigator(CLOSED), page=page)
    with pytest.raises(WriteAttemptError, match="minted for target"):
        consume(block["to_confirm"], action=ACTION, target="urn:li:activity:7400000000000000002")
    block = await preview(SPEC, target=URN, navigator=Navigator(CLOSED), page=page)
    grant = consume(block["to_confirm"], action=ACTION, target=URN)
    await writes.perform(Navigator(answering("saved")), page, grant)
    with pytest.raises(WriteAttemptError, match="already been used once"):
        await writes.perform(Navigator(CLOSED), page, grant)


# ---------------------------------------------------------------------------
# 3. End to end: two presses, an in-place reading decides
# ---------------------------------------------------------------------------


async def _run(page, world: str) -> tuple[dict, Navigator]:
    block = await preview(SPEC, target=URN, navigator=Navigator(CLOSED), page=page)
    grant = consume(block["to_confirm"], action=ACTION, target=URN)
    act = Navigator(world)
    receipt = await writes.perform(act, page, grant)
    assert act.gotos == [URL], "one load for the press; the verification is in place"
    return receipt, act


async def test_two_presses_and_a_saved_confirmation_is_saved(writes_on, page, fast_menu):
    receipt, _act = await _run(page, answering("saved"))
    assert receipt["clicked"]["clicks_made"] == 2
    assert receipt["clicked"]["selector"] == fs.TRIGGER
    assert receipt["clicked"]["error"] is None
    assert await _witness(page) == {"trigger": 1, "item": 1, "other": 0}
    gate = receipt["curation_gate"]
    assert gate["proceeded"] is True
    assert gate["after_the_item_press"]["saved_regions"] == 1
    assert receipt["verification"]["observed_state"] == fs.SAVED
    assert receipt["performed"] is True
    assert "Example Member" not in json.dumps(receipt)


async def test_a_press_that_leaves_nothing_is_unknown_never_not_saved(writes_on, page, fast_menu):
    receipt, _act = await _run(page, answering("nothing"))
    assert await _witness(page) == {"trigger": 1, "item": 1, "other": 0}
    assert receipt["verification"]["observed_state"] == fs.UNKNOWN
    assert receipt["performed"] == writes.UNKNOWN


async def test_the_menu_left_open_with_its_item_is_not_done(writes_on, page, fast_menu):
    receipt, _act = await _run(page, answering("open"))
    assert receipt["verification"]["observed_state"] == fs.SHOWN
    assert receipt["performed"] is False


async def test_an_unowned_menu_is_never_pressed(writes_on, page, fast_menu):
    world = _plant(answering("saved"), 'aria-owns="k2c1ddb96"', 'aria-owns="kffffffff"')
    receipt, _act = await _run(page, world)
    assert receipt["clicked"]["clicks_made"] == 1, "the trigger and nothing more"
    assert await _witness(page) == {"trigger": 1, "item": 0, "other": 0}
    assert receipt["curation_gate"]["refused_condition"] == "item_outside_the_owned_menu"
    assert receipt["performed"] != True  # noqa: E712 -- never claimed done


async def test_an_item_already_saved_is_pressed_no_further(writes_on, page, fast_menu):
    receipt, _act = await _run(page, answering("saved", already_saved=True))
    assert receipt["clicked"]["clicks_made"] == 1, "the trigger and nothing more"
    assert await _witness(page) == {"trigger": 1, "item": 0, "other": 0}
    assert receipt["curation_gate"]["refused_condition"] == "item_not_unique"
    assert receipt["performed"] != True  # noqa: E712 -- never claimed done


# ---------------------------------------------------------------------------
# 4. The tables and the tool
# ---------------------------------------------------------------------------


def test_the_tables_name_the_act():
    assert ACTION in writes.PERFORMABLE
    assert ACTION in writes.STRICT_PRESS_ACTIONS
    assert ACTION not in writes._TOGGLE_ACTIONS
    assert "IN PLACE" in writes._VERIFIED_FROM[ACTION]
    assert writes.anchor_label_for(SPEC) == fs.SAVE
    assert SPEC.target_kind == "item_urn" and SPEC.url_pattern.match(URL)
    assert SPEC.state_from == "feed_item_save_menu"
    assert readonly.name_implies_write(SPEC.tool_name)
    assert callable(getattr(server, SPEC.tool_name, None))
