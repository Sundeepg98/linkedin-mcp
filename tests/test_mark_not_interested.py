"""``mark_not_interested`` -- census row ``N 154`` (``N 153`` rides it) -- built to ready-to-fire, unfired.

WHAT THE ACT IS. On the permalink of ONE feed item whose urn he names, the
item's own control menu is opened -- the trigger LinkedIn draws with its fixed
"Open control menu" prefix -- and its ``Not interested`` item pressed, only if
the gate finds it in the menu that pressed trigger owns. Behind the grant,
under HIS-OWN-CURATION-NOT-OUTWARD. The verification is IN PLACE: the undo
LinkedIn draws is drawn once.

THE PAGES ARE REAL. The closed world is live session 11's tracked copy of a
member's post's permalink (load 29, ``tests/fixtures/live11/
permalink_member_post.html``); the open one is the same load with its menu
open, LinkedIn's menu words put back by keyed shape
(``tests/fixtures/synthetic/live11_permalink_menu_words.html``). TWO THINGS
ARE PLANTED, each an asserted edit, because the capture reduces them to ``x``:
the trigger's label -- LinkedIn's measured prefix and a SYNTHETIC name, where
the live label names the author -- and, for a press-answering world, a script
that opens the menu as LinkedIn's does (``showPopover`` on the capture's own
popover) and draws what the press leaves, which is a fixture CHOICE named per
world: an ``Undo``, nothing, or the menu left open.

NOTHING HERE REACHES LINKEDIN: a local headless Chromium, every request the
page starts refused by its own route.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pytest

from linkedin_server import feed_curation as fc
from linkedin_server import readonly, server, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

REPO = Path(__file__).resolve().parents[1]
CLOSED_COPY = (REPO / "tests/fixtures/live11/permalink_member_post.html").read_text(encoding="ascii")
OPEN_WORDS = (REPO / "tests/fixtures/synthetic/live11_permalink_menu_words.html").read_text(encoding="ascii")

ACTION = fc.ACTION
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


def _plant(markup: str, old: str, new: str, count: int = 1) -> str:
    assert markup.count(old) == count, (old[:60], markup.count(old))
    return markup.replace(old, new)


#: THE CLOSED CAPTURE, its one trigger labelled: the preview's world.
CLOSED = _plant(CLOSED_COPY, _TRIGGER_CLOSED + ">", _TRIGGER_CLOSED.replace(
    'aria-label="x"', f'aria-label="{LABEL}"') + ">")

#: THE OPEN CAPTURE, labelled, as captured -- the menu open, its popover open.
_OPEN_TAG = _TRIGGER_CLOSED + ' aria-expanded="true" data-floating-ui-inert="">'
OPEN = _plant(OPEN_WORDS, _OPEN_TAG, _OPEN_TAG.replace('aria-label="x"', f'aria-label="{LABEL}"'))

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
  if ((item.textContent || '').replace(/\\s+/g, ' ').trim() !== 'Not interested') {
    window.__otherPresses += 1; return;
  }
  window.__itemPresses += 1;
  var leave = '%(leave)s';
  if (leave === 'open') return;
  if (pop) pop.hidePopover();
  document.querySelector('main button[aria-label^="Open control menu"]').removeAttribute('aria-expanded');
  if (leave === 'undo') {
    var d = document.createElement('div');
    d.innerHTML = '<p>x</p><button type="button">Undo</button>';
    document.querySelector('main').appendChild(d);
  }
  if (leave === 'undo_elsewhere') {
    var t = document.createElement('div');
    t.innerHTML = '<p>x</p><button type="button">Undo</button>';
    document.body.appendChild(t);
  }
}, true);
</script>"""

#: AN UNDO ALREADY DRAWN BEFORE ANY PRESS -- an earlier action's, or another
#: item's. PLANTED, a fixture CHOICE: no capture holds one, and it is the shape
#: the hidden item's own undo is DERIVED to take, which makes it the hardest
#: case for a reading in place (FEED-CURATION-RECEIPT-NEEDS-A-CHANGE).
_STALE_UNDO = '<div><p>x</p><button type="button">Undo</button></div>'


def answering(leave: str, *, stale: Optional[str] = None) -> str:
    """The OPEN capture made closed -- the trigger's aria-expanded removed,
    the popover left as the capture draws it, shut until shown -- with the
    press-answering script. DERIVED: what the item's press leaves is the
    test's choice (``undo``, in the page's main where the item is;
    ``undo_elsewhere``, outside it, as a toast would be; ``nothing``;
    ``open``). ``stale`` plants an undo before any press: ``"main"`` beside
    the item, ``"page"`` outside the page's main."""
    closed = _plant(OPEN, f'aria-label="{LABEL}" aria-expanded="true"', f'aria-label="{LABEL}"')
    if stale == "main":
        closed = _plant(closed, "</main>", _STALE_UNDO + "</main>")
    elif stale == "page":
        closed = _plant(closed, "</body>", _STALE_UNDO + "</body>")
    else:
        assert stale is None, stale
    return closed.replace("</body>", _SCRIPT % {"leave": leave} + "</body>", 1)


class Navigator:
    def __init__(self, *worlds: str):
        self.worlds = list(worlds)
        self.gotos: list[str] = []
        self.pressed: list[dict[str, int]] = []

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
    return browser_page


@pytest.fixture(autouse=True)
def _no_grants_survive_a_test():
    yield
    writes.discard_all()


@pytest.fixture
def fast_menu(monkeypatch):
    monkeypatch.setattr(fc, "MENU_POLL_MS", 5)


# ---------------------------------------------------------------------------
# 0. Pure: the selectors, the verdicts
# ---------------------------------------------------------------------------


def test_the_selectors_name_the_prefix_and_the_owned_portal_never_a_name():
    assert fc.TRIGGER == 'main button[aria-label^="Open control menu"]'
    assert "data-menu-portal-anchor" in fc.ITEM_IN_OWNED_MENU
    assert "@aria-owns" in fc.ITEM_IN_OWNED_MENU and "@id" in fc.ITEM_IN_OWNED_MENU
    assert "Not interested" in fc.ITEM_IN_OWNED_MENU
    assert "Example" not in fc.TRIGGER + fc.ITEM_IN_OWNED_MENU


def test_the_verdicts_say_what_they_saw_in_counts():
    one = {"triggers": 1, "triggers_visible": 1}
    assert fc.item_verdict(one)[1] == fc.SHOWN
    assert fc.item_verdict({"triggers": 2, "triggers_visible": 2})[1] == fc.UNKNOWN
    assert fc.item_verdict({})[1] == fc.UNKNOWN
    assert fc.item_verdict(dict(one, triggers_expanded=1))[1] == fc.UNKNOWN
    assert fc.item_verdict({"error": "TimeoutError"})[1] == fc.UNKNOWN
    owned = {"triggers_expanded": 1, "items_visible": 1, "items_in_owned_menu": 1}
    assert fc.menu_verdict(owned)["proceed"] is True
    assert fc.menu_verdict(dict(owned, items_in_owned_menu=0))["refused_condition"] == "item_outside_the_owned_menu"
    assert fc.menu_verdict(dict(owned, items_visible=2))["refused_condition"] == "item_not_unique"
    assert fc.menu_verdict(dict(owned, triggers_expanded=0))["refused_condition"] == "menu_not_open"
    # IN PLACE, AS A CHANGE: an Undo with no count taken before the press is
    # no proof. It read hidden until 2026-11-27 -- the defect lane msg7 found
    # beside save_post's (FEED-CURATION-RECEIPT-NEEDS-A-CHANGE). The menu still
    # open with its item is not done; anything else is unknown -- never
    # "not done".
    assert fc.verification_verdict({"undo_controls": 1, "undo_in_main": 1})[1] == fc.UNKNOWN
    assert fc.verification_verdict(
        {"undo_controls": 1, "undo_in_main": 1}, before={"undo_in_main": 0}
    )[1] == fc.HIDDEN
    assert fc.verification_verdict(owned)[1] == fc.SHOWN
    assert fc.verification_verdict({"triggers": 1})[1] == fc.UNKNOWN


def test_a_hidden_reading_must_be_a_change_this_press_made():
    """FEED-CURATION-RECEIPT-NEEDS-A-CHANGE (the orchestrator, 2026-11-27, on
    lane msg7's finding beside save_post's receipt). The verdict read ANY
    visible Undo as hidden and read nothing before the press, so an Undo
    already on the page -- an earlier action's, or another item's -- made an
    unlanded mark read hidden, which is ``performed: true``."""
    gate = {"triggers": 1, "triggers_visible": 1, "triggers_expanded": 1,
            "items_visible": 1, "items_in_owned_menu": 1}
    stale = dict(gate, undo_controls=1, undo_in_main=1)
    closed = {"triggers": 1, "triggers_visible": 1}
    # A STALE UNDO BESIDE THE ITEM AND NO CHANGE: unverified, never hidden.
    _facts, state, why = fc.verification_verdict(dict(closed, undo_controls=1, undo_in_main=1), before=stale)
    assert state == fc.UNKNOWN, why
    assert why.startswith(fc.UNVERIFIED + ":"), why
    # ... and beside the menu still open with its item: the press did not land.
    _facts, state, why = fc.verification_verdict(dict(gate, undo_controls=1, undo_in_main=1), before=stale)
    assert state == fc.SHOWN, why
    assert why.startswith(fc.NOT_LANDED + ":"), why
    # A REAL CHANGE: one more undo beside the item than the gate counted --
    # with the item's trigger still drawn, or the item replaced by its card.
    _facts, state, why = fc.verification_verdict(dict(closed, undo_controls=1, undo_in_main=1), before=gate)
    assert state == fc.HIDDEN, why
    assert why.startswith(fc.HIDDEN_BY_THE_PRESS + ":"), why
    assert fc.verification_verdict(dict(closed, undo_controls=2, undo_in_main=2), before=stale)[1] == fc.HIDDEN
    assert fc.verification_verdict({"undo_controls": 1, "undo_in_main": 1}, before=gate)[1] == fc.HIDDEN
    # A NEW UNDO ELSEWHERE ON THE PAGE IS NOT BESIDE THE ITEM: unverified.
    _facts, state, why = fc.verification_verdict(dict(closed, undo_controls=1, undo_in_main=0), before=gate)
    assert state == fc.UNKNOWN, why
    assert why.startswith(fc.UNVERIFIED + ":"), why
    # THE ITEM'S TRIGGER GONE AND NO NEW UNDO: a navigation or an error page
    # removes it too, so that alone is never hidden.
    assert fc.verification_verdict({"triggers": 0}, before=gate)[1] == fc.UNKNOWN
    # NO READING BEFORE THE PRESS: nothing can be shown to be a change.
    assert fc.verification_verdict(dict(closed, undo_controls=1, undo_in_main=1))[1] == fc.UNKNOWN
    # A NEW UNDO WHILE THE MENU STILL DRAWS ITS ITEM UNPRESSED: contradictory.
    assert fc.verification_verdict(dict(gate, undo_controls=1, undo_in_main=1), before=gate)[1] == fc.UNKNOWN
    # NOTHING PRESSED PAST THE TRIGGER: nothing marked by this call.
    _facts, state, why = fc.verification_verdict({}, before=None, pressed=False)
    assert state == fc.SHOWN, why
    assert why.startswith(fc.NOT_PRESSED + ":"), why
    assert fc.verification_verdict({"error": "TimeoutError"}, before=stale)[1] == fc.UNKNOWN
    assert set(fc.OUTCOMES) == {fc.HIDDEN_BY_THE_PRESS, fc.NOT_LANDED, fc.NOT_PRESSED, fc.UNVERIFIED}


# ---------------------------------------------------------------------------
# 1. The captures draw what the readers read
# ---------------------------------------------------------------------------


async def test_the_readers_over_the_captures(page):
    async def read(html: str, show: bool = False):
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        if show:
            await page.evaluate("() => document.querySelector('[data-floating-ui-portal] [popover]').showPopover()")
        return await fc.read_item(page)

    # THE CLOSED CAPTURE, labelled: one trigger, closed -- shown.
    facts, state, why = fc.item_verdict(await read(CLOSED))
    assert state == fc.SHOWN, why
    assert (facts["triggers"], facts["triggers_expanded"], facts["items_visible"]) == (1, 0, 0)
    # THE RED: the tracked copy as captured -- its trigger's label reduced to
    # x -- draws no trigger by LinkedIn's prefix, and is refused.
    assert fc.item_verdict(await read(CLOSED_COPY))[1] == fc.UNKNOWN
    # THE OPEN CAPTURE, its popover shown as LinkedIn shows it: the item is in
    # the menu the pressed trigger owns, by the portal id its anchor names.
    reading = await read(OPEN, show=True)
    assert (reading["triggers_expanded"], reading["items_visible"], reading["items_in_owned_menu"]) == (1, 1, 1)
    assert fc.menu_verdict(reading)["proceed"] is True
    # THE PORTAL NOT OWNED: the anchor names another id -- refused.
    stranger = _plant(OPEN, 'aria-owns="k2c1ddb96"', 'aria-owns="kffffffff"')
    reading = await read(stranger, show=True)
    assert reading["items_visible"] == 1 and reading["items_in_owned_menu"] == 0
    assert fc.menu_verdict(reading)["refused_condition"] == "item_outside_the_owned_menu"
    # THE MENU'S WORDS REDUCED (the tracked copy's own menu): no item at all.
    copy_open = (REPO / "tests/fixtures/live11/permalink_member_post_menu_open.html").read_text(encoding="ascii")
    copy_open = _plant(copy_open, _OPEN_TAG, _OPEN_TAG.replace('aria-label="x"', f'aria-label="{LABEL}"'))
    reading = await read(copy_open, show=True)
    assert reading["items_visible"] == 0
    assert fc.menu_verdict(reading)["refused_condition"] == "item_not_unique"


# ---------------------------------------------------------------------------
# 2. The preview, the controls
# ---------------------------------------------------------------------------


async def test_the_preview_mints_on_the_permalink_and_refuses_every_other_world(writes_on, page):
    nav = Navigator(CLOSED)
    block = await preview(SPEC, target=URN, navigator=nav, page=page)
    assert nav.gotos == [URL]
    assert block["direction"]["currently"] == fc.SHOWN
    assert block["direction"]["after"] == fc.HIDDEN
    assert block["reversibility_class"] == "STILL-UNKNOWN"
    assert block["where"]["url"] == URL
    assert "Example Member" not in json.dumps(block)
    writes.discard_all()
    for label, html in (("the-reduced-copy", CLOSED_COPY),
                        ("two-triggers", _plant(CLOSED, f'aria-label="{LABEL}">', f'aria-label="{LABEL}"></button><button type="button" aria-label="{LABEL}">'))):
        with pytest.raises(WriteAttemptError) as raised:
            await preview(SPEC, target=URN, navigator=Navigator(html), page=page)
        assert not writes._GRANTS, label
        assert "Example Member" not in str(raised.value), label
    # A DESCRIPTION IS NO ADDRESS. ``item_urn`` is an opaque kind, so the urn's
    # shape is enforced where the string is USED (``writes._opaque_target``):
    # the read door refuses the composed address before any load, and the
    # write door's anchored pattern refuses it after.
    words = "a feed post I liked"
    nav = Navigator(CLOSED)
    with pytest.raises(WriteAttemptError):
        await preview(SPEC, target=words, navigator=nav, page=page)
    assert nav.gotos == [] and not writes._GRANTS
    assert not SPEC.url_pattern.match(SPEC.url_template.format(target=words))


async def test_the_controls_writes_off_another_item_and_a_second_use(monkeypatch, page, fast_menu):
    monkeypatch.delenv(writes.WRITES_FLAG, raising=False)
    off = await server.linkedin_mark_not_interested(URN)
    assert off["error"] == "writes_disabled" and off["performed"] is False
    monkeypatch.setenv(writes.WRITES_FLAG, "1")
    block = await preview(SPEC, target=URN, navigator=Navigator(CLOSED), page=page)
    with pytest.raises(WriteAttemptError, match="minted for target"):
        consume(block["to_confirm"], action=ACTION, target="urn:li:activity:7400000000000000002")
    block = await preview(SPEC, target=URN, navigator=Navigator(CLOSED), page=page)
    grant = consume(block["to_confirm"], action=ACTION, target=URN)
    await writes.perform(Navigator(answering("undo")), page, grant)
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


async def test_two_presses_and_an_undo_is_hidden(writes_on, page, fast_menu):
    receipt, _act = await _run(page, answering("undo"))
    assert receipt["clicked"]["clicks_made"] == 2
    assert receipt["clicked"]["selector"] == fc.TRIGGER
    assert receipt["clicked"]["error"] is None
    assert await _witness(page) == {"trigger": 1, "item": 1, "other": 0}
    gate = receipt["curation_gate"]
    assert gate["proceeded"] is True
    assert gate["after_the_item_press"]["undo_controls"] == 1
    assert receipt["verification"]["observed_state"] == fc.HIDDEN
    assert receipt["performed"] is True
    assert "Example Member" not in json.dumps(receipt)


async def test_a_press_that_leaves_nothing_is_unknown_never_not_done(writes_on, page, fast_menu):
    receipt, _act = await _run(page, answering("nothing"))
    assert await _witness(page) == {"trigger": 1, "item": 1, "other": 0}
    assert receipt["verification"]["observed_state"] == fc.UNKNOWN
    assert receipt["performed"] == writes.UNKNOWN


async def test_the_menu_left_open_with_its_item_is_not_done(writes_on, page, fast_menu):
    receipt, _act = await _run(page, answering("open"))
    assert receipt["verification"]["observed_state"] == fc.SHOWN
    assert receipt["performed"] is False


async def test_an_unowned_menu_is_never_pressed(writes_on, page, fast_menu):
    world = _plant(answering("undo"), 'aria-owns="k2c1ddb96"', 'aria-owns="kffffffff"')
    receipt, _act = await _run(page, world)
    assert receipt["clicked"]["clicks_made"] == 1, "the trigger and nothing more"
    assert await _witness(page) == {"trigger": 1, "item": 0, "other": 0}
    assert receipt["curation_gate"]["refused_condition"] == "item_outside_the_owned_menu"
    assert receipt["performed"] != True  # noqa: E712 -- never claimed done


# ---------------------------------------------------------------------------
# 3b. FEED-CURATION-RECEIPT-NEEDS-A-CHANGE: hidden is a change this press made
# ---------------------------------------------------------------------------


async def test_an_undo_drawn_before_the_press_is_no_confirmation(writes_on, page, fast_menu):
    """THE RED THE ORDER NAMES: a page already drawing an undo beside the item,
    and a press that changes nothing, read item_hidden -- performed: true --
    at the lane's certified head. The gate's reading, taken just before the
    'Not interested' press, is the baseline the verdict now compares with."""
    receipt, _act = await _run(page, answering("nothing", stale="main"))
    assert await _witness(page) == {"trigger": 1, "item": 1, "other": 0}
    assert receipt["verification"]["observed_state"] == fc.UNKNOWN
    assert receipt["performed"] == writes.UNKNOWN
    assert receipt["verification"]["why"].startswith(fc.UNVERIFIED + ":")
    gate = receipt["curation_gate"]
    assert gate["observed"]["undo_in_main"] == 1, "the stale undo, counted before the press"
    assert gate["after_the_item_press"]["undo_in_main"] == 1


async def test_an_undo_outside_the_main_before_the_press_is_no_confirmation(writes_on, page, fast_menu):
    receipt, _act = await _run(page, answering("nothing", stale="page"))
    assert receipt["verification"]["observed_state"] == fc.UNKNOWN
    assert receipt["performed"] == writes.UNKNOWN


async def test_the_menu_left_open_beside_a_stale_undo_is_not_landed(writes_on, page, fast_menu):
    receipt, _act = await _run(page, answering("open", stale="main"))
    assert receipt["verification"]["observed_state"] == fc.SHOWN
    assert receipt["performed"] is False
    assert receipt["verification"]["why"].startswith(fc.NOT_LANDED + ":")


async def test_a_new_undo_outside_the_main_is_not_beside_the_item(writes_on, page, fast_menu):
    receipt, _act = await _run(page, answering("undo_elsewhere"))
    assert await _witness(page) == {"trigger": 1, "item": 1, "other": 0}
    assert receipt["verification"]["observed_state"] == fc.UNKNOWN
    assert receipt["performed"] == writes.UNKNOWN
    assert receipt["verification"]["why"].startswith(fc.UNVERIFIED + ":")


async def test_control_a_refused_gate_beside_a_stale_undo_is_not_pressed(writes_on, page, fast_menu):
    """CONTROL: a refused gate reads not_pressed. Beside a stale undo it read
    item_hidden -- performed: true, with nothing pressed past the trigger."""
    world = _plant(answering("undo", stale="main"), 'aria-owns="k2c1ddb96"', 'aria-owns="kffffffff"')
    receipt, _act = await _run(page, world)
    assert receipt["clicked"]["clicks_made"] == 1, "the trigger and nothing more"
    assert await _witness(page) == {"trigger": 1, "item": 0, "other": 0}
    assert receipt["performed"] is False
    assert receipt["verification"]["why"].startswith(fc.NOT_PRESSED + ":")


async def test_control_a_new_undo_beside_a_stale_one_is_hidden(writes_on, page, fast_menu):
    """CONTROL: a real change reads hidden, beside a stale undo too."""
    receipt, _act = await _run(page, answering("undo", stale="main"))
    assert await _witness(page) == {"trigger": 1, "item": 1, "other": 0}
    assert receipt["verification"]["observed_state"] == fc.HIDDEN
    assert receipt["performed"] is True


# ---------------------------------------------------------------------------
# 4. The tables and the tool
# ---------------------------------------------------------------------------


def test_the_tables_name_the_act():
    assert ACTION in writes.PERFORMABLE
    assert ACTION in writes.STRICT_PRESS_ACTIONS
    assert ACTION not in writes._TOGGLE_ACTIONS
    assert "IN PLACE" in writes._VERIFIED_FROM[ACTION]
    assert writes.anchor_label_for(SPEC) == fc.NOT_INTERESTED
    assert SPEC.target_kind == "item_urn" and SPEC.url_pattern.match(URL)
    assert readonly.name_implies_write(SPEC.tool_name)
    assert callable(getattr(server, SPEC.tool_name, None))
