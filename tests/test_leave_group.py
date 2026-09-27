"""``leave_group`` -- census rows ``M C63`` and ``N 64`` -- built to ready-to-fire,
unfired, and the controls that keep a built write from being a fired one.

WHAT THIS ACTION IS. Leaving one LinkedIn group he belongs to, named by its
NUMERIC id, on the ``/groups/`` root -- a constant address, so the id never
enters a navigation. Two presses through ``perform``'s one click site: the
row's disclosure, then ``Leave this group``, appended only by a gate that
re-reads the menu. Built under ``OUTWARD-CLASSES-BUILT-BEHIND-GRANTS``.

WHAT IS MEASURED AND WHAT IS NOT, so no test here claims more. The STRUCTURE of
the page is a measurement -- his own ``/groups/`` capture of 2026-09-20, held
outside the tree and read as shapes and counts only -- and
``tests/fixtures/synthetic/groups_leave_menu.html`` carries that structure
with invented groups. What pressing ``Leave this group`` does is NOT measured;
every behaviour of that press below is a fixture CHOICE the test names.

NOTHING HERE REACHES LINKEDIN. Every page is the synthetic fixture, served into
a local headless Chromium. A grant minted here is minted against a frozen world
by the real preview, and its clicks land on that world.

AND NO GROUP NAME LEAVES. The fixture's names are parsed out of it, never typed
here, and every refusal, block and receipt below is asserted to carry none.

WHY SEVERAL WORLDS SHARE ONE TEST. A browser launch and close is the whole
price of a test here -- measured 2026-09-24 on this laptop under other lanes'
load: 2.6-8.0 s to set up and 7.0-19.1 s to tear down, against 0.04-2.3 s for
the test body. So the scenarios of one check run in a loop over one browser,
each assertion carrying the scenario's label, rather than paying that price
per parameter.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from linkedin_server import group_leave, readonly, server, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_apply_modal_fixture import over  # noqa: F401 -- fixture
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

_FIXTURE = Path(__file__).parent / "fixtures" / "synthetic" / "groups_leave_menu.html"

#: The synthetic Groups root, read once. IMPORTED BY
#: ``tests/test_preview_state_and_click_state.py``, which serves committed
#: markup only and names this module as its source.
GROUPS_LEAVE_MARKUP = _FIXTURE.read_text(encoding="ascii")

_MARKER = "<!--FIXTURE_CONFIG-->"
_ACTION = "leave_group"
_SPEC = spec_for_action(_ACTION)
_URL = _SPEC.url_template

#: The ids, PARSED out of the fixture rather than typed, so a regenerated
#: fixture cannot leave a stale expectation passing.
MEMBER_IDS: list[str] = re.findall(r'<li class="grp-row" data-row="([0-9]+)">', GROUPS_LEAVE_MARKUP)
SUGGESTION_IDS: list[str] = re.findall(
    r'<li class="grp-suggestion"><a href="https://www\.linkedin\.com/groups/([0-9]+)/">',
    GROUPS_LEAVE_MARKUP,
)
#: The one id the tests aim at: the first membership row, which is also the
#: row carrying two spellings of its anchor.
GROUPS_LEAVE_ID = MEMBER_IDS[0]

#: EVERY synthetic group name the page draws: in the disclosures' labels
#: (members) and in the suggestion rows. Parsed, never typed; the rule under
#: test is that none of them appears in anything this action returns or raises.
GROUP_NAMES: list[str] = re.findall(
    r'aria-label="More options for ([^"]+)"', GROUPS_LEAVE_MARKUP
) + re.findall(r'<li class="grp-suggestion"><a [^>]*><span>([^<]+)</span>', GROUPS_LEAVE_MARKUP)


def world(**config) -> str:
    """The fixture with its behaviour chosen. Always an explicit config, so a
    page reused across loads can never inherit the previous document's."""
    assert GROUPS_LEAVE_MARKUP.count(_MARKER) == 1
    script = f"<script>window.__fixtureConfig = {json.dumps(config)};</script>"
    return GROUPS_LEAVE_MARKUP.replace(_MARKER, script)


#: The worlds the aim must refuse, as ``(label, world, target)``, shared by the
#: verdict test and the preview test so the two cannot drift apart. Each is
#: DERIVED by a fixture flag, named in the label.
REFUSED_AIMS: list[tuple[str, str, str]] = [
    ("id-not-on-the-page", world(), "4242"),
    ("id-on-a-suggestion-row", world(), SUGGESTION_IDS[0]),
    ("two-rows-carry-the-id", world(duplicateRowOf=GROUPS_LEAVE_ID), GROUPS_LEAVE_ID),
    ("no-row-scoped-disclosure-unhydrated", world(stripDisclosures=True), GROUPS_LEAVE_ID),
    ("a-prefix-of-a-member-id", world(), GROUPS_LEAVE_ID[:-1]),
]


def _no_name(text: str, label: str = "") -> None:
    """Nothing the page NAMED may appear: not a member's name, not a suggestion's."""
    for name in GROUP_NAMES:
        assert name not in text, f"[{label}] a group name leaked into: {text[:400]}"


class _Navigator:
    """Serves frozen worlds for the ONE address this action loads, in order,
    and RECORDS every ask. The last world repeats once the list runs out."""

    def __init__(self, *worlds: str, landed: str = ""):
        assert worlds
        self.worlds = list(worlds)
        self.gotos: list[str] = []
        self.landed = landed

    async def goto(self, page, url: str) -> str:
        self.gotos.append(url)
        if url != _URL:
            raise AssertionError(f"the gate asked for {url!r}, which this test did not freeze")
        html = self.worlds.pop(0) if len(self.worlds) > 1 else self.worlds[0]
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return self.landed or url


@pytest.fixture(autouse=True)
def _no_grants_survive_a_test():
    yield
    writes.discard_all()


@pytest.fixture
def fast_menu(monkeypatch):
    """The menu poll's INTERVAL pushed down for a document that cannot change;
    the COUNT -- the property -- is kept."""
    monkeypatch.setattr(group_leave, "MENU_POLL_MS", 5)


async def _read(over, html: str, identifier: str = GROUPS_LEAVE_ID) -> dict:
    return await over(html, lambda page: group_leave.read_rows(page, identifier))


async def _granted(page, target: str = GROUPS_LEAVE_ID, html: str = ""):
    """A real preview over a frozen world, then the real token door."""
    block = await preview(_SPEC, target=target, navigator=_Navigator(html or world()), page=page)
    return consume(block["to_confirm"], action=_ACTION, target=target), block


# ---------------------------------------------------------------------------
# 1. The fixture draws what the capture drew
# ---------------------------------------------------------------------------


def test_the_fixture_parses_into_members_suggestions_and_names():
    assert MEMBER_IDS == ["10001", "10002", "10003"]
    assert len(SUGGESTION_IDS) == 3 and not set(SUGGESTION_IDS) & set(MEMBER_IDS)
    assert len(GROUP_NAMES) == 6 and len(set(GROUP_NAMES)) == 6
    # Every synthetic id is under six digits: tests/test_no_committed_identity.py.
    assert all(len(identifier) < 6 for identifier in MEMBER_IDS + SUGGESTION_IDS)


async def test_the_fixture_draws_the_measured_shape_and_no_closed_item_is_pressable(over):
    """Disclosures on every row and outside them; row-scoped ones only on the
    memberships; the menus in the DOM, closed, and not one item pressable.

    AND ARIA-HIDDEN ALONE KEEPS A CLOSED ITEM UNPRESSABLE. With the closed menus
    DRAWN (still ``aria-hidden="true"``) a VISIBILITY-ONLY rule counts all three
    items -- SHOWN FAILING -- while the role-engine rule counts none. The
    capture holds every closed menu in the DOM, so this is the rule standing
    between a closed row's item and a press."""

    async def counts(page):
        count = lambda selector: page.locator(selector).count()  # noqa: E731
        return {
            "disclosures": await count(group_leave.DISCLOSURES),
            "row_scoped": await count(group_leave.ROW_SCOPED_DISCLOSURES),
            "numeric_anchors": await count(f"xpath=//a[{group_leave.NUMERIC_GROUP_ANCHOR}]"),
            "leave_in_dom": await count(group_leave.LEAVE_ITEMS_IN_DOM),
            "leave_pressable": await count(group_leave.LEAVE_ITEM_PRESSABLE),
            "visibility_only": await count(group_leave.LEAVE_ITEMS_IN_DOM + " >> visible=true"),
            "dialogs": await count(group_leave.VISIBLE_DIALOGS),
            "menus": await count("xpath=//*[@role='menu' or @role='menuitem']"),
            "main": await count("main"),
        }

    assert await over(world(), counts) == {
        "disclosures": 7, "row_scoped": 3, "numeric_anchors": 7, "leave_in_dom": 3,
        "leave_pressable": 0, "visibility_only": 0, "dialogs": 0, "menus": 0, "main": 1,
    }
    drawn = await over(world(closedMenusDisplayed=True), counts)
    assert drawn["leave_pressable"] == 0
    assert drawn["visibility_only"] == 3, "the visibility-only rule was supposed to count the closed items"


# ---------------------------------------------------------------------------
# 2. The verdict: exact ids, counts only, and no name in any why
# ---------------------------------------------------------------------------


async def test_the_verdict_reads_a_membership_and_refuses_every_other_aim(over):
    facts, state, why = group_leave.membership_verdict(await _read(over, world()), GROUPS_LEAVE_ID)
    assert state == group_leave.MEMBER == _SPEC.from_state
    assert facts["row_scoped_disclosures"] == 3
    assert facts["row_scoped_disclosures_for_this_id"] == 1
    assert facts["group_name_read"] is False
    _no_name(json.dumps(facts) + why, "member")

    expected = {
        "id-not-on-the-page": (group_leave.NOT_MEMBER, "not one of the memberships"),
        "id-on-a-suggestion-row": (group_leave.NOT_MEMBER, "suggestion row"),
        "two-rows-carry-the-id": (group_leave.UNKNOWN, "exactly one is required"),
        "no-row-scoped-disclosure-unhydrated": (group_leave.UNKNOWN, "NO row-scoped"),
        "a-prefix-of-a-member-id": (group_leave.NOT_MEMBER, "not one of the memberships"),
    }
    assert set(expected) == {label for label, _w, _t in REFUSED_AIMS}
    for label, html, target in REFUSED_AIMS:
        facts, got, why = group_leave.membership_verdict(await _read(over, html, target), target)
        want, fragment = expected[label]
        assert got == want and got != _SPEC.from_state, (label, got, why)
        assert fragment in why, (label, why)
        _no_name(json.dumps(facts) + why, label)


async def test_the_exact_id_rule_is_shown_failing_as_a_prefix_match(over, monkeypatch):
    """SHOWN FAILING. An id that is a PREFIX of a membership id reads
    ``not_member`` -- the segment is compared with ``=``. Replace that with a
    prefix match and the same page, left with one row, calls the prefix a
    membership: the row the grant would press is somebody else's id."""
    one_row = world(absentRows=MEMBER_IDS[1:])
    prefix = GROUPS_LEAVE_ID[:-1]
    _f, state, _w = group_leave.membership_verdict(await _read(over, one_row, prefix), prefix)
    assert state == group_leave.NOT_MEMBER

    seg = group_leave._SEGMENT
    numeric = group_leave.NUMERIC_GROUP_ANCHOR

    def prefix_match(identifier):  # the mutation: '=' becomes starts-with
        return (
            f"[.//a[({numeric}) and starts-with({seg}, '{identifier}')]]"
            f"[not(.//a[({numeric}) and not(starts-with({seg}, '{identifier}'))])]"
        )

    monkeypatch.setattr(group_leave, "_carries_only", prefix_match)
    _f, state, _w = group_leave.membership_verdict(await _read(over, one_row, prefix), prefix)
    assert state == group_leave.MEMBER, "without the exact rule a prefix reads as a membership"


def test_a_reader_failure_is_reported_by_type_and_a_forged_type_is_not_echoed():
    _f, state, why = group_leave.membership_verdict({"error": "TimeoutError"}, GROUPS_LEAVE_ID)
    assert state == group_leave.UNKNOWN and "TimeoutError" in why
    _f, state, why = group_leave.membership_verdict({"error": GROUP_NAMES[0]}, GROUPS_LEAVE_ID)
    assert state == group_leave.UNKNOWN
    _no_name(why)


def test_a_name_given_as_the_id_is_refused_and_not_repeated():
    for candidate in (GROUP_NAMES[0], "", "12a", "1" * 21, None, True):
        digits, why = group_leave.checked_group_id(candidate)
        assert digits is None, candidate
        _no_name(why)
        _f, state, why = group_leave.membership_verdict({"disclosures_for_target": 1}, candidate)
        assert state == group_leave.UNKNOWN
        _no_name(why)
    with pytest.raises(WriteAttemptError) as excinfo:
        writes._target_for(_SPEC, GROUP_NAMES[0])
    _no_name(str(excinfo.value))
    with pytest.raises(ValueError) as excinfo:
        group_leave.disclosure_selector("10001') or ('1'='1")
    assert "10001" not in str(excinfo.value)


def test_string_counts_are_substituted_not_raised_on():
    reading = {"disclosures": GROUP_NAMES[0], "row_scoped_disclosures": "3",
               "disclosures_for_target": [1]}
    facts, state, why = group_leave.membership_verdict(reading, GROUPS_LEAVE_ID)
    assert state == group_leave.UNKNOWN
    _no_name(json.dumps(facts) + why)


# ---------------------------------------------------------------------------
# 3. The preview: one page load, the id and counts, no name, no grant on refusal
# ---------------------------------------------------------------------------


async def test_the_preview_reads_the_page_it_acts_on_and_prints_no_name(writes_on, browser_page):
    nav = _Navigator(world())
    block = await preview(_SPEC, target=GROUPS_LEAVE_ID, navigator=nav, page=browser_page)
    assert nav.gotos == [_URL]
    assert block["where"]["group_id"] == GROUPS_LEAVE_ID
    assert block["where"]["url"] == _URL
    assert block["read"]["same_page_as_the_action"] is True
    assert block["read"]["page_loads"] == 1
    assert block["direction"]["currently"] == "member"
    assert block["direction"]["after"] == "not_member"
    assert block["irreversible"] is True
    assert block["reversibility_class"] == "STILL-UNKNOWN"
    assert block["verification"]["outcome_is_verifiable"] == "YES"
    assert isinstance(block["to_confirm"], str) and block["to_confirm"]
    _no_name(json.dumps(block))


async def test_the_preview_refuses_every_aim_a_name_and_a_landing_and_mints_nothing(
    writes_on, browser_page
):
    for label, html, target in REFUSED_AIMS:
        nav = _Navigator(html)
        with pytest.raises(WriteAttemptError) as excinfo:
            await preview(_SPEC, target=target, navigator=nav, page=browser_page)
        assert nav.gotos == [_URL], label
        _no_name(str(excinfo.value), label)
        assert not writes._GRANTS, f"[{label}] a refused preview minted a grant"

    # A NAME AS THE TARGET is refused before any page loads, and not repeated.
    nav = _Navigator(world())
    with pytest.raises(WriteAttemptError) as excinfo:
        await preview(_SPEC, target=GROUP_NAMES[0], navigator=nav, page=browser_page)
    assert nav.gotos == [], "a name reached a navigation"
    _no_name(str(excinfo.value), "name-as-target")

    # A LANDING ELSEWHERE reads unknown, and the landing is withheld.
    nav = _Navigator(world(), landed="https://www.linkedin.com/groups/10001/")
    with pytest.raises(WriteAttemptError) as excinfo:
        await preview(_SPEC, target=GROUPS_LEAVE_ID, navigator=nav, page=browser_page)
    assert "WITHHELD" in str(excinfo.value)
    assert "/groups/10001" not in str(excinfo.value)
    assert not writes._GRANTS


# ---------------------------------------------------------------------------
# 4. THE GRANT CONTROLS -- no grant, another target or verb, a second use
# ---------------------------------------------------------------------------


async def test_control_1_it_refuses_without_a_grant(monkeypatch, browser_page):
    """Without a grant nothing moves, at every door, and nothing is navigated."""
    # (a) writes off -- the process-wide door refuses before anything else.
    monkeypatch.delenv(writes.WRITES_FLAG, raising=False)
    nav = _Navigator(world())
    with pytest.raises(WriteAttemptError, match="disabled"):
        await preview(_SPEC, target=GROUPS_LEAVE_ID, navigator=nav, page=browser_page)
    with pytest.raises(WriteAttemptError, match="disabled"):
        consume("anything", action=_ACTION, target=GROUPS_LEAVE_ID)
    off = await server.linkedin_leave_group(group_id=GROUPS_LEAVE_ID)
    assert off["error"] == "writes_disabled" and off["performed"] is False
    off = await server.linkedin_leave_group(group_id=GROUPS_LEAVE_ID, confirm_token="forged")
    assert off["error"] == "writes_disabled" and off["performed"] is False

    # (b) writes on, and still no grant: no token, None, True, a forged token,
    # an unredeemed grant, and something that is not a grant at all.
    monkeypatch.setenv(writes.WRITES_FLAG, "1")
    for bogus in ("", None, True, "not-a-real-token"):
        with pytest.raises(WriteAttemptError):
            consume(bogus, action=_ACTION, target=GROUPS_LEAVE_ID)
    unredeemed = writes.WriteGrant(action=_ACTION, target=GROUPS_LEAVE_ID, token="t", minted_at=0.0)
    with pytest.raises(WriteAttemptError, match="not been redeemed"):
        await writes.perform(nav, browser_page, unredeemed)
    with pytest.raises(WriteAttemptError, match="WriteGrant"):
        await writes.perform(nav, browser_page, {"action": _ACTION})
    assert nav.gotos == [], "a refused write navigated"


async def test_control_2_it_refuses_a_grant_for_another_group_or_another_verb(writes_on, browser_page):
    block = await preview(_SPEC, target=GROUPS_LEAVE_ID, navigator=_Navigator(world()), page=browser_page)
    with pytest.raises(WriteAttemptError, match="minted for target"):
        consume(block["to_confirm"], action=_ACTION, target=MEMBER_IDS[1])
    # ... and for a different VERB on the same digits: a company id of the
    # same shape is the pairing most worth refusing.
    block = await preview(_SPEC, target=GROUPS_LEAVE_ID, navigator=_Navigator(world()), page=browser_page)
    with pytest.raises(WriteAttemptError, match="minted for 'leave_group'"):
        consume(block["to_confirm"], action="unfollow_company", target=GROUPS_LEAVE_ID)


async def test_control_3_it_refuses_a_second_use_of_the_same_grant(writes_on, browser_page, fast_menu):
    """Single use at BOTH doors: the token cannot be redeemed twice, and the
    redeemed grant cannot be performed twice."""
    grant, block = await _granted(browser_page)
    with pytest.raises(WriteAttemptError, match="unknown or already-discarded"):
        consume(block["to_confirm"], action=_ACTION, target=GROUPS_LEAVE_ID)

    first = _Navigator(world(), world(absentRows=[GROUPS_LEAVE_ID]))
    receipt = await writes.perform(first, browser_page, grant)
    assert receipt["clicked"]["clicks_made"] == 2
    second = _Navigator(world())
    with pytest.raises(WriteAttemptError, match="already been used once"):
        await writes.perform(second, browser_page, grant)
    assert second.gotos == [], "the second use navigated before it refused"


async def test_the_second_use_guard_is_shown_failing_without_its_flag(writes_on, browser_page, fast_menu):
    """SHOWN FAILING. Clear the flag ``perform`` set on the first use and the
    SAME grant object walks straight back to the page and presses twice more.
    The flag is the whole of the second-use refusal."""
    grant, _block = await _granted(browser_page)
    await writes.perform(_Navigator(world(), world(absentRows=[GROUPS_LEAVE_ID])), browser_page, grant)
    assert grant.performed is True

    grant.performed = False  # the mutation: the guard's input, removed
    replay = _Navigator(world(), world(absentRows=[GROUPS_LEAVE_ID]))
    receipt = await writes.perform(replay, browser_page, grant)
    assert replay.gotos[0] == _URL
    assert receipt["clicked"]["clicks_made"] == 2, "without the flag the replay presses again"


# ---------------------------------------------------------------------------
# 5. THE MENU GATE -- the second press is appended only on a fresh read
# ---------------------------------------------------------------------------


async def test_the_menu_gate_refuses_and_presses_nothing_further(writes_on, browser_page, fast_menu):
    scenarios = [
        ("the-item-never-becomes-visible", {"menuNeverOpens": True}, "leave_item_not_visible"),
        ("two-items-in-the-row", {"duplicateLeaveItem": True}, "leave_item_not_unique"),
        ("every-row-opens", {"opensAllMenus": True}, "leave_item_not_unique"),
        ("the-menu-opens-outside-the-row", {"menuPortal": True}, "leave_item_outside_the_target_row"),
    ]
    for label, config, condition in scenarios:
        grant, _block = await _granted(browser_page, html=world(**config))
        act = _Navigator(world(**config), world())
        receipt = await writes.perform(act, browser_page, grant)
        assert act.gotos == [_URL, _URL], label
        assert receipt["clicked"]["clicks_made"] == 1, f"[{label}] the item was pressed past a refusing gate"
        assert receipt["clicked"]["error"] is None, label
        gate = receipt["menu_gate"]
        assert gate["proceeded"] is False, label
        assert gate["refused_condition"] == condition, (label, gate)
        assert "NOTHING further was pressed" in gate["why"], label
        assert gate["after_the_item_press"] is None, label
        # The fresh render still draws the row: NOT left, and said as False.
        assert receipt["verification"]["observed_state"] == "member", label
        assert receipt["performed"] is False and receipt["verified"] is False, label
        _no_name(json.dumps(receipt), label)


async def test_the_in_row_condition_is_shown_failing_on_a_portal_menu(writes_on, browser_page, fast_menu, monkeypatch):
    """SHOWN FAILING. A menu drawn OUTSIDE the row cannot be shown to be that
    row's, and the gate refuses it (the test above). Drop the in-row condition
    -- let the gate press the one pressable item on the page -- and the same
    world gets its item pressed."""
    config = {"menuPortal": True}
    monkeypatch.setattr(
        group_leave, "leave_item_in_row_selector",
        lambda identifier: group_leave.LEAVE_ITEM_PRESSABLE,
    )
    grant, _block = await _granted(browser_page, html=world(**config))
    receipt = await writes.perform(_Navigator(world(**config), world()), browser_page, grant)
    assert receipt["menu_gate"]["proceeded"] is True
    assert receipt["clicked"]["clicks_made"] == 2, "without the in-row condition the portal item is pressed"


def test_the_menu_gate_reads_counts_only():
    verdict = group_leave.menu_verdict(
        {"pressable_on_the_page": 1, "pressable_in_the_target_row": 1, "target_rows": 1},
        GROUPS_LEAVE_ID,
    )
    assert verdict["proceed"] is True
    assert verdict["selector"] == group_leave.leave_item_in_row_selector(GROUPS_LEAVE_ID)
    refused = group_leave.menu_verdict({"error": GROUP_NAMES[0]}, GROUPS_LEAVE_ID)
    assert refused["proceed"] is False and refused["selector"] == ""
    _no_name(json.dumps(refused))


# ---------------------------------------------------------------------------
# 6. THE DIALOG BRANCH -- a further step opens and is not taken
# ---------------------------------------------------------------------------


async def test_a_dialog_after_the_leave_press_is_counted_and_never_answered(writes_on, browser_page, fast_menu):
    grant, _block = await _granted(browser_page, html=world(onLeave="dialog"))
    receipt = await writes.perform(_Navigator(world(onLeave="dialog"), world()), browser_page, grant)
    assert receipt["clicked"]["clicks_made"] == 2, "exactly the disclosure and the item; nothing in the dialog"
    after = receipt["menu_gate"]["after_the_item_press"]
    assert after["further_step_opened"] is True
    assert after["dialogs"] + after["alertdialogs"] == 1
    assert after["buttons_in_dialogs"] == 2
    assert "A FURTHER STEP OPENED AND WAS NOT TAKEN" in after["what_this_means"]
    # The fresh render still draws the row, so the leave did not land.
    assert receipt["verification"]["observed_state"] == "member"
    assert receipt["performed"] is False
    _no_name(json.dumps(receipt), "dialog")

    # AND A PRESS THAT DOES NOTHING opens no step and still reports NOT left.
    grant, _block = await _granted(browser_page, html=world(onLeave="nothing"))
    receipt = await writes.perform(_Navigator(world(onLeave="nothing"), world()), browser_page, grant)
    assert receipt["clicked"]["clicks_made"] == 2
    assert receipt["menu_gate"]["after_the_item_press"]["further_step_opened"] is False
    assert receipt["performed"] is False
    _no_name(json.dumps(receipt), "nothing")


# ---------------------------------------------------------------------------
# 7. THE HAPPY PATH -- press, press, and a fresh render that no longer lists it
# ---------------------------------------------------------------------------


async def test_a_leave_runs_end_to_end_and_is_verified_off_a_fresh_render(writes_on, browser_page, fast_menu):
    grant, _block = await _granted(browser_page)
    act = _Navigator(world(), world(absentRows=[GROUPS_LEAVE_ID]))
    receipt = await writes.perform(act, browser_page, grant)
    assert act.gotos == [_URL, _URL]
    assert receipt["clicked"]["selector"] == group_leave.disclosure_selector(GROUPS_LEAVE_ID)
    assert receipt["clicked"]["state_before"] == "member"
    assert receipt["clicked"]["on"] == _URL
    assert receipt["clicked"]["error"] is None
    assert receipt["clicked"]["clicks_made"] == 2
    gate = receipt["menu_gate"]
    assert gate["proceeded"] is True and gate["refused_condition"] is None
    assert gate["after_the_item_press"]["further_step_opened"] is False
    assert receipt["target"] == {"url": _URL, "kind": "group_id", "group_id": GROUPS_LEAVE_ID}
    assert receipt["verification"]["observed_state"] == "not_member"
    assert receipt["performed"] is True and receipt["verified"] is True
    _no_name(json.dumps(receipt), "happy")

    # HIS ONLY GROUP LEFT and a page that had not arrived look the same from
    # here, and the receipt says ``unknown`` rather than choosing.
    grant, _block = await _granted(browser_page)
    receipt = await writes.perform(
        _Navigator(world(), world(absentRows=MEMBER_IDS)), browser_page, grant
    )
    assert receipt["clicked"]["clicks_made"] == 2
    assert receipt["verification"]["observed_state"] == writes.UNKNOWN
    assert receipt["performed"] == writes.UNKNOWN


async def test_a_click_error_carries_its_type_and_never_the_element(writes_on, browser_page, fast_menu, monkeypatch):
    """A Playwright click error can print the element it resolved -- here the
    disclosure, whose label carries the group's name. SHOWN FAILING first: the
    raw error of the same click on the same world DOES carry the name. Then the
    receipt carries only the type."""
    disabled = world().replace(
        f'aria-label="More options for {GROUP_NAMES[0]}"',
        f'disabled aria-label="More options for {GROUP_NAMES[0]}"',
    )
    assert disabled != world()
    await browser_page.set_content(disabled, wait_until="domcontentloaded")
    with pytest.raises(Exception) as excinfo:
        await browser_page.click(group_leave.disclosure_selector(GROUPS_LEAVE_ID), timeout=300)
    assert GROUP_NAMES[0] in str(excinfo.value), "the raw click error was expected to quote the element"

    monkeypatch.setattr(writes, "CLICK_TIMEOUT_MS", 300)
    grant, _block = await _granted(browser_page, html=disabled)
    receipt = await writes.perform(_Navigator(disabled, world()), browser_page, grant)
    assert receipt["clicked"]["clicks_made"] == 0
    assert receipt["clicked"]["error"] == "TimeoutError"
    assert receipt["performed"] is False
    _no_name(json.dumps(receipt))


# ---------------------------------------------------------------------------
# 8. The spec, the tables and the tool
# ---------------------------------------------------------------------------


def test_the_spec_is_the_writespec_with_its_corrections():
    assert _SPEC.tool_name == "linkedin_leave_group"
    assert _SPEC.url_template == group_leave.GROUPS_URL == "https://www.linkedin.com/groups/"
    assert "{target}" not in _SPEC.url_template
    assert _SPEC.url_pattern.match(_SPEC.url_template)
    assert not _SPEC.url_pattern.match(_SPEC.url_template + "10001/")
    assert readonly.assert_read_url(_SPEC.url_template) == _SPEC.url_template
    assert not [bad for bad in readonly._FORBIDDEN_URL_SUBSTRINGS if bad in _SPEC.url_template]
    assert _SPEC.exempt_substring is None
    assert (_SPEC.from_state, _SPEC.to_state) == ("member", "not_member")
    assert _SPEC.target_kind == "group_id" and _SPEC.state_from == "groups_memberships"
    assert _SPEC.irreversible is True
    assert _SPEC.reversibility_measured is False and _SPEC.reversibility_class == "STILL-UNKNOWN"
    assert _SPEC.unverifiable is None
    assert "NOT through this server" in _SPEC.reversible_by
    assert "does not join it" in _SPEC.wrong_state_note
    assert writes._reversibility_disagreement(_SPEC) is None
    grant = writes.WriteGrant(action=_ACTION, target=GROUPS_LEAVE_ID, token="t", minted_at=0.0)
    assert writes.assert_write_url(_URL, grant) == _URL


def test_the_receipt_and_the_surface_tables_name_this_action():
    assert _ACTION in writes.PERFORMABLE and writes.grant_is_possible(_SPEC)
    assert _ACTION in writes.MENU_ITEM_ACTIONS
    assert _ACTION not in writes.TWO_CLICK_ACTIONS
    assert _ACTION not in writes._TOGGLE_ACTIONS
    assert writes.anchor_label_for(_SPEC) == group_leave.LEAVE_LABEL
    assert writes._WHERE_TO_LOOK[_ACTION] == "your LinkedIn Groups page"
    assert "RE-RENDERED" in writes._VERIFIED_FROM[_ACTION]
    assert writes._WRITE_SURFACE_FOR_ACTION[_ACTION] == "groups"
    assert writes.SANCTIONED_WRITES["linkedin_leave_group"].action == _ACTION
    keys = list(writes.SANCTIONED_WRITES)
    assert keys[keys.index("linkedin_mark_company_interest") + 1] == "linkedin_leave_group"


def test_the_tool_is_registered_and_says_what_it_does_not_do():
    tool = getattr(server, "linkedin_leave_group", None)
    assert callable(tool)
    doc = tool.__doc__ or ""
    for phrase in ("NUMERIC ID", "THE PAGE ONLY VETOES", "CONFIRMATION THIS SERVER HAS NEVER SEEN",
                   "NOTHING further is pressed", "THE UNDO IS NOT THROUGH THIS SERVER"):
        assert phrase in doc, phrase


def test_no_selector_in_the_module_names_a_label_that_carries_a_name():
    """The disclosure's label carries the group's name, so no selector may
    mention ``aria-label`` or the words LinkedIn writes before the name."""
    selectors = [
        group_leave.DISCLOSURES, group_leave.ROW_SCOPED_DISCLOSURES,
        group_leave.LEAVE_ITEMS_IN_DOM, group_leave.LEAVE_ITEM_PRESSABLE,
        group_leave.disclosure_selector(GROUPS_LEAVE_ID),
        group_leave.leave_item_in_row_selector(GROUPS_LEAVE_ID),
    ]
    for selector in selectors:
        assert "aria-label" not in selector and "More options" not in selector
