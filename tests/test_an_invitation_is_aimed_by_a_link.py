"""``linkedin_send_invitation`` is aimed by the person's profile LINK, never a name.

THE ORDER (orchestrator, 2026-09-27 23:36, lane L5, item 1;
PEOPLE-DATA-MITIGATIONS, mitigation 6): people search now returns names, so a
name read off a page can reach a write unless the write refuses names. This
action was aimed by one -- ``member``, his word for the person, compared in the
page against the invitation controls' labels (``INVITE_NEEDLE_JS``). Now:

* the target is the person's profile link (or member id), parsed by the
  named-profile parser, which refuses a bare word before anything loads;
* the control pressed is the one whose CARD -- the nearest element holding any
  ``/in/`` link -- links to that profile and to nobody else and holds exactly
  one invitation control: ``dom.rail_invite_control_selector``, XPath the
  browser evaluates, so the comparison runs in the page and a COUNT comes back;
* exactly one such card is the only aimable answer, and the press is that same
  selector, pressed STRICTLY.

MEASURED FIRST, offline, over every capture on disk (counts and shapes only):
the 32 invitation controls on his own profile's rail each sit in a card with
exactly one member segment and one control, the link's text naming the person;
none carries a member id. And the selector itself, run over the 16 captures
holding such controls: 44 of 44 matched exactly one element, the one whose
label is that card's control; upper-cased, 44 of 44 still matched; a segment
no card carries matched none on all 16.

EVERY PAGE HERE IS SYNTHETIC MARKUP IN A REAL HEADLESS CHROMIUM, and every
button records its own press in ``window.__pressed``, so "was it pressed" is
read off the page rather than off the receipt.

NOTHING HERE REACHES LINKEDIN.
"""
from __future__ import annotations

import json

import pytest

from linkedin_server import dom, server, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_writes import FixtureNavigator, browser_page, writes_on  # noqa: F401

SPEC = spec_for_action("send_invitation")

#: The people these pages draw. INVENTED: every slug carries ``example``, a
#: declared synthetic slug token, and the names are the route fixture's.
CASEY = ("Casey Example", "https://www.linkedin.com/in/casey-example-3f9a/")
MORGAN = ("Morgan Example", "https://www.linkedin.com/in/morgan-example-77aa/")
RILEY = ("Riley Example", "/in/riley-example-5b2c/?miniProfileUrn=synthetic")
CASEY_SEGMENT = "casey-example-3f9a"
MEMBER_ID = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000002"

_RECORDER = "<script>window.__pressed = [];</script>"


def _button(name: str, key: str) -> str:
    return (
        '<button type="button" aria-label="Invite %s to connect" '
        "onclick=\"window.__pressed.push('%s')\">Connect</button>" % (name, key)
    )


def _card(person, key: str, extra: str = "") -> str:
    name, href = person
    return '<div class="rail-card"><a href="%s">%s</a>%s%s</div>' % (
        href, name, _button(name, key), extra
    )


def _page(*cards: str) -> str:
    return "<html><body>" + _RECORDER + "<main>" + "".join(cards) + "</main></body></html>"


RAIL = _page(_card(MORGAN, "morgan"), _card(CASEY, "casey"), _card(RILEY, "riley"))


async def _reading(page, html, segment):
    await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
    return await dom.read_invitation_rail(page, segment)


async def _pressed(page):
    return await page.evaluate("window.__pressed")


# ---------------------------------------------------------------------------
# 1. The aim
# ---------------------------------------------------------------------------


async def test_the_card_linking_to_the_profile_is_the_one_aimed_at(browser_page):
    reading = await _reading(browser_page, RAIL, CASEY_SEGMENT)
    assert reading == {"controls": 3, "matches": 1, "error": None}, reading
    aim, why = writes.aim_invitation_by_link(reading, CASEY_SEGMENT)
    assert aim == writes.INVITE_AIMED, why
    await browser_page.click(
        dom.rail_invite_control_selector(CASEY_SEGMENT), timeout=5_000, strict=True
    )
    assert await _pressed(browser_page) == ["casey"]


async def test_a_relative_link_with_a_query_is_the_same_profile(browser_page):
    """The card's link is read as ONE path segment after ``/in/``, stopped at
    ``/``, ``?`` or ``#`` -- a relative href with a tracking query names the
    same person as the canonical link."""
    reading = await _reading(browser_page, RAIL, "riley-example-5b2c")
    assert reading["matches"] == 1, reading


async def test_case_is_folded_on_both_sides(browser_page):
    """Vanity segments are case-insensitive on LinkedIn, so the fold is
    ASCII on both sides: his segment upper-cased, and a card whose SEGMENT is
    upper-cased, each still match -- and each is the half the other misses.
    The ``/in/`` marker itself is matched as LinkedIn writes it, lower case."""
    assert (await _reading(browser_page, RAIL, CASEY_SEGMENT.upper()))["matches"] == 1
    shouted_link = CASEY[1].replace(CASEY_SEGMENT, CASEY_SEGMENT.upper())
    assert shouted_link != CASEY[1]
    shouted = _page(_card((CASEY[0], shouted_link), "casey"))
    assert (await _reading(browser_page, shouted, CASEY_SEGMENT))["matches"] == 1


async def test_a_profile_no_card_carries_matches_nothing_and_says_where_to_go(browser_page):
    segment = "jordan-example-1d2e"
    reading = await _reading(browser_page, RAIL, segment)
    assert reading["controls"] == 3 and reading["matches"] == 0, reading
    aim, why = writes.aim_invitation_by_link(reading, segment)
    assert aim == writes.INVITE_NO_MATCH
    assert "linkedin_connect_from_profile" in why
    assert segment not in why, "a refusal repeated the link it was given"


async def test_a_member_id_matches_no_rail_card_and_says_why(browser_page):
    """THE RAIL CARRIES VANITY LINKS (measured, 32 of 32), so an id is a
    shape this accepts and a card it never finds -- and the refusal says so
    rather than reading as "that person is not on your rail"."""
    reading = await _reading(browser_page, RAIL, MEMBER_ID)
    assert reading["matches"] == 0, reading
    aim, why = writes.aim_invitation_by_link(reading, MEMBER_ID)
    assert aim == writes.INVITE_NO_MATCH
    assert "MEMBER ID" in why and "32 of 32" in why
    assert MEMBER_ID not in why


async def test_two_cards_carrying_the_link_are_ambiguous(browser_page):
    twice = _page(_card(CASEY, "casey-1"), _card(CASEY, "casey-2"))
    reading = await _reading(browser_page, twice, CASEY_SEGMENT)
    assert reading["matches"] == 2, reading
    aim, why = writes.aim_invitation_by_link(reading, CASEY_SEGMENT)
    assert aim == writes.INVITE_AMBIGUOUS and "position" in why


async def test_a_card_holding_two_peoples_links_is_not_aimed_at(browser_page):
    """A card is ONE person's: a link to anybody else in it, and the control
    in it is nobody's to aim at by this link."""
    mixed = _page(
        '<div class="rail-card"><a href="%s">%s</a><a href="%s">%s</a>%s</div>'
        % (CASEY[1], CASEY[0], MORGAN[1], MORGAN[0], _button(CASEY[0], "casey"))
    )
    assert (await _reading(browser_page, mixed, CASEY_SEGMENT))["matches"] == 0


async def test_a_card_holding_two_invitation_controls_is_not_aimed_at(browser_page):
    doubled = _page(_card(CASEY, "casey", extra=_button(MORGAN[0], "morgan")))
    assert (await _reading(browser_page, doubled, CASEY_SEGMENT))["matches"] == 0


async def test_a_control_in_no_card_is_counted_and_never_aimed_at(browser_page):
    """A button with no profile link anywhere above it has no card at all --
    and the nearest element holding a link is then the whole page, which
    holds another person's link too."""
    loose = _page(_card(MORGAN, "morgan")).replace(
        "</main>", _button(CASEY[0], "loose") + "</main>"
    )
    reading = await _reading(browser_page, loose, CASEY_SEGMENT)
    assert reading["controls"] == 2 and reading["matches"] == 0, reading


# ---------------------------------------------------------------------------
# 2. What crosses into this process
# ---------------------------------------------------------------------------


class _Spy:
    """A real page whose ``evaluate`` calls are counted."""

    def __init__(self, page):
        self._page = page
        self.evaluated = 0

    def __getattr__(self, name):
        return getattr(self._page, name)

    async def evaluate(self, *args, **kwargs):  # pragma: no cover - must not run
        self.evaluated += 1
        return await self._page.evaluate(*args, **kwargs)


async def test_the_reader_runs_no_script_and_returns_only_numbers(browser_page):
    """THE NEEDLE'S RULING, KEPT: no label crosses to AIM. The reader is two
    locator counts; it runs no script, and every value it returns is a count,
    ``None`` or an exception's type."""
    await browser_page.set_content(RAIL, wait_until="domcontentloaded", timeout=60_000)
    spy = _Spy(browser_page)
    reading = await dom.read_invitation_rail(spy, CASEY_SEGMENT)
    assert spy.evaluated == 0
    for key, value in reading.items():
        assert isinstance(value, (int, type(None))), (key, value)
    blob = json.dumps(reading)
    for name, _href in (CASEY, MORGAN, RILEY):
        assert name not in blob and name.split()[0] not in blob, blob


@pytest.mark.parametrize(
    "bad",
    ["", "casey'example", 'casey"example', "casey]example", "casey example", "a/b", "../x"],
    ids=["empty", "quote", "double-quote", "bracket", "space", "slash", "traversal"],
)
def test_the_selector_builder_refuses_anything_that_is_not_a_segment(bad):
    with pytest.raises(ValueError):
        dom.rail_invite_control_selector(bad)


def test_his_link_is_compared_and_never_navigated_to():
    """THE ACT LANDS ON HIS OWN PROFILE, where the rail is drawn. The person's
    link is compared in the page and never reaches a url: loading a third
    party's profile emits a view, and only the named-profile door may do that
    (ruling THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET). Held the way the needle
    was held in ``tests/test_opaque_targets.py`` until it left: as its own
    assertion, not inferred from the template's text today."""
    assert SPEC.url_template == writes.PROFILE_URL
    assert "{target}" not in SPEC.url_template
    assert SPEC.action not in writes.NAMED_PROFILE_ACTIONS
    built = SPEC.url_template.format(target=writes.url_target_of(SPEC, CASEY[1]))
    assert built == writes.PROFILE_URL and CASEY_SEGMENT not in built


def test_a_bare_word_is_refused_as_the_target():
    """A NAME IS NEVER THE TARGET: a one-word name and a vanity segment look
    the same, so a bare word is refused -- and the refusal repeats nothing."""
    with pytest.raises(WriteAttemptError) as caught:
        writes._target_for(SPEC, "Casey")
    assert "Casey" not in str(caught.value)
    assert writes._target_for(SPEC, CASEY[1]) == CASEY[1]
    assert SPEC.target_kind == "rail_profile"


async def test_the_tool_refuses_a_name_before_any_page_loads(writes_on, monkeypatch):
    class _NoSession:
        entered = 0

        def session(self):
            outer = self

            class _S:
                async def __aenter__(self):
                    outer.entered += 1
                    raise AssertionError("a page was opened for a name")

                async def __aexit__(self, *exc):
                    return False

            return _S()

    fake = _NoSession()
    monkeypatch.setattr(server, "BROWSER", fake)
    result = await server.linkedin_send_invitation(profile="Casey")
    assert fake.entered == 0, result
    assert "bare word" in json.dumps(result), result


# ---------------------------------------------------------------------------
# 3. End to end: the preview names whom it resolved; the press is strict
# ---------------------------------------------------------------------------

#: A transparent layer that holds every press for 1.2 s, then lifts and runs
#: the redraw -- a page re-rendered while a press waits, which is when
#: Playwright resolves the press's selector again (the technique of
#: ``tests/test_a_strict_mode_claim_is_a_strict_press.py``). MEASURED HERE
#: FIRST, the hard way: a redraw that only ADDS a card leaves the element the
#: press resolved connected, Playwright keeps pressing that handle, and
#: strictness never gets a second look -- so the redraw must detach it.
_HOLD = (
    '<div id="press-hold" style="position:fixed;left:0;top:0;width:100%;'
    'height:100%;z-index:99999;background:transparent"></div>'
)


def _redrawn_mid_press(html: str, redraw: str) -> str:
    derived = html.replace(
        "</main>",
        "</main>" + _HOLD + "<script>setTimeout(function () {"
        "  var hold = document.getElementById('press-hold');"
        "  if (hold) { hold.parentNode.removeChild(hold); }" + redraw + "}, 1200);</script>",
    )
    assert derived != html
    return derived


#: His card's control replaced by a fresh copy (so the element the press
#: resolved is detached), and a SECOND card linking to the same profile drawn
#: FIRST on the rail while the press waits -- so a press that is not strict
#: lands on whoever was drawn first, which is not his card.
_TWIN = (
    "  var mine = document.querySelector("
    "'button[aria-label=\"Invite " + CASEY[0] + " to connect\"]');"
    "  if (mine) { mine.replaceWith(mine.cloneNode(true)); }"
    "  var main = document.querySelector('main');"
    "  var twin = document.createElement('div');"
    "  twin.className = 'rail-card';"
    "  twin.innerHTML = '<a href=\"" + CASEY[1] + "\">x</a>"
    "<button type=\"button\" aria-label=\"Invite x to connect\" "
    "onclick=\"window.__pressed.push(\\'twin\\')\">Connect</button>';"
    "  main.insertBefore(twin, main.firstChild);"
)


async def _grant(page, html=RAIL):
    block = await preview(
        SPEC, target=CASEY[1], navigator=FixtureNavigator({writes.PROFILE_URL: html}), page=page
    )
    return block, consume(block["to_confirm"], action=SPEC.action, target=CASEY[1])


async def test_the_preview_names_the_person_on_the_one_card_his_link_selected(
    writes_on, browser_page
):
    block, grant = await _grant(browser_page)
    whom = block["who_this_would_reach"]
    assert whom["name"] == CASEY[0] and whom["link"] == CASEY[1], whom
    assert whom["headline"] is None
    assert "CHECK IT" in block["who_this_would_reach_check"]
    # THE GRANT HOLDS HIS LINK, and nothing the page drew.
    assert grant.target == CASEY[1]
    kept = json.dumps(grant.preview, default=repr) + json.dumps(
        grant.observation.facts, default=repr
    )
    for name, _href in (CASEY, MORGAN, RILEY):
        assert name not in kept, kept


async def test_the_press_lands_on_his_card_and_the_receipt_names_only_his_link(
    writes_on, browser_page
):
    _block, grant = await _grant(browser_page)
    receipt = await writes.perform(
        FixtureNavigator({writes.PROFILE_URL: RAIL}), browser_page, grant
    )
    assert receipt["clicked"]["clicks_made"] == 1, receipt["clicked"]
    assert receipt["clicked"]["error"] is None, receipt["clicked"]
    assert await _pressed(browser_page) == ["casey"]
    blob = json.dumps(receipt, default=repr)
    for name, _href in (CASEY, MORGAN, RILEY):
        assert name not in blob, "a name the page drew reached the receipt"
    assert CASEY[1] in blob, "the receipt does not name the target he supplied"


async def test_a_second_card_drawn_mid_press_stops_the_strict_press(writes_on, browser_page):
    _block, grant = await _grant(browser_page)
    world = _redrawn_mid_press(RAIL, _TWIN)
    receipt = await writes.perform(
        FixtureNavigator({writes.PROFILE_URL: world}), browser_page, grant
    )
    assert receipt["clicked"]["clicks_made"] == 0, receipt["clicked"]
    assert receipt["clicked"]["error"] == "Error", receipt["clicked"]
    assert await _pressed(browser_page) == []


async def test_the_same_world_is_pressed_when_the_press_is_not_strict(
    writes_on, browser_page, monkeypatch
):
    """THE CONTROL: without the strict set's membership the re-render is
    pressed -- the first of two matches, the card drawn FIRST, which is not
    his -- so it is strictness that stops it, and what it stops is real."""
    monkeypatch.setattr(
        writes, "STRICT_PRESS_ACTIONS", writes.STRICT_PRESS_ACTIONS - {SPEC.action}
    )
    _block, grant = await _grant(browser_page)
    world = _redrawn_mid_press(RAIL, _TWIN)
    receipt = await writes.perform(
        FixtureNavigator({writes.PROFILE_URL: world}), browser_page, grant
    )
    assert receipt["clicked"]["clicks_made"] == 1, receipt["clicked"]
    assert await _pressed(browser_page) == ["twin"]
