"""The named-person route -- ruling THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET.

WHAT THIS ROUTE IS. A third party's profile, ``/in/<segment>/``, loaded ONLY
inside an outward act whose target the operator names in that call, by link
or member id -- never by name, never from page content, never for a
measurement. Two acts ride it: ``connect_from_profile`` (census ``N 1``'s
route and ``N 4``) and ``message_from_profile`` (``M M1``; for anyone who is
not a first-degree connection it presses, records and stops -- ``M M6``'s
capture). Lane L5's follow-up, 2026-09-27.

WHAT IS MEASURED AND WHAT IS NOT. No third party's profile has ever been
captured, so the page every test below drives is
``tests/fixtures/synthetic/named_profile.html``, which says, element by
element, what it borrows from a measured surface and what it derives. Every
world built from it by an asserted edit says which it is.

THE SECTIONS:

1. The doors: the second door admits one shape, the read door still refuses
   it, and exactly one function in the package can ask for the second.
2. The target: a link or a member id, canonical as the link; never a name.
3. The reader: integers and closed tokens, the owner's controls matched in
   the page and addressed by position.
4. The preview: WHOM THE ACT RESOLVED TO, printed in the block and kept
   nowhere; a landing elsewhere vetoes and mints nothing.
5. Connect, end to end, on a fresh render.
6. Message, end to end, in place with a before-count -- and every refusal
   before a word is typed.
7. The three controls, and the tools.

NOTHING HERE REACHES LINKEDIN. Every page is the fixture, served into a local
headless Chromium; its own script stands in for LinkedIn's redraw.
"""
from __future__ import annotations

import ast
import json
import pathlib

import pytest

from linkedin_server import dom, named_profile, people_seam, readonly, server, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_messaging_threads import _derive
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

REPO = pathlib.Path(__file__).resolve().parent.parent
PROFILE = (REPO / "tests" / "fixtures" / "synthetic" / "named_profile.html").read_text(
    encoding="utf-8"
)

CONNECT = spec_for_action("connect_from_profile")
MESSAGE = spec_for_action("message_from_profile")

#: The synthetic person the fixture draws. The segment carries ``example``,
#: one of ``tests/test_no_committed_identity.SYNTHETIC_SLUG_TOKENS``; the
#: member id is one of its ``SYNTHETIC_MEMBER_TOKENS``.
SEGMENT = "casey-example-3f9a"
LINK = "https://www.linkedin.com/in/casey-example-3f9a/"
MEMBER_ID = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000002"
OWNER = "Casey Example"
HEADLINE = "Invented headline for a synthetic person"
#: Other people the page draws, and words nobody here wrote. None of them may
#: reach a block, a grant, a receipt or an error.
STRANGERS = ("Morgan Example", "Riley Example")
THEIR_WORDS = ("Good to hear from you last month.", "Invented about text")
TEXT = "Thursday works for me, speak then."
TARGET = {"profile": LINK, "text": TEXT}

_BODY = '<body data-message-opens="conversation" data-connect="nothing">'


def _body(**attributes: str) -> str:
    """The fixture with its behaviour attributes set -- an asserted edit."""
    replacement = _BODY
    for key, value in attributes.items():
        name = "data-" + key.replace("_", "-")
        if name in replacement:
            start = replacement.index(name + '="') + len(name) + 2
            end = replacement.index('"', start)
            replacement = replacement[:start] + value + replacement[end:]
        else:
            replacement = replacement[:-1] + f' {name}="{value}">'
    return _derive(PROFILE, _BODY, replacement)


_CONNECT_BUTTON = (
    '<button type="button" aria-label="Invite Casey Example to connect" '
    'id="topcard-connect">Connect</button>'
)
_MESSAGE_LINK_HREF = (
    'href="/messaging/compose/?recipient=ACoAASYNTHETICSYNTHETICSYNTHETIC0000002'
    '&amp;screenContext=NON_SELF_PROFILE_VIEW"'
)

#: DERIVED -- the conversation's Send DISPATCHES: the fixture draws the words
#: as the new last message and empties the box, as LinkedIn redraws.
DISPATCHING = _body(dispatches="yes")
#: DERIVED -- a second-degree person: the topcard's degree line reads 2nd.
SECOND_DEGREE = _derive(DISPATCHING, "<p>&#183; 1st</p>", "<p>&#183; 2nd</p>")
#: DERIVED -- a fresh render after a Connect press LinkedIn turned into a
#: pending invitation. What a pressed Connect becomes is NEEDS-CAPTURE C-P2.
AFTER_PENDING = _derive(
    PROFILE,
    _CONNECT_BUTTON,
    '<button type="button" aria-label="Pending, click to withdraw invitation '
    'sent to Casey Example" id="topcard-connect">Pending</button>',
)
#: DERIVED -- a profile that draws no Connect for its owner (already
#: connected, or Connect behind the More menu).
NO_CONNECT = _derive(PROFILE, _CONNECT_BUTTON, "")
#: DERIVED -- two controls both named for inviting the owner.
TWO_CONNECTS = _derive(PROFILE, _CONNECT_BUTTON, _CONNECT_BUTTON + _CONNECT_BUTTON)
#: DERIVED -- a Message control that is a link to a THREAD, not the composer:
#: the destination measured on 2 of the 18 Message controls captured.
MESSAGE_TO_A_THREAD = _derive(
    PROFILE, _MESSAGE_LINK_HREF, 'href="/messaging/thread/2-SYNTHETICEXAMPLETHREAD/"'
)
#: DERIVED -- a conversation composer already open before anything is pressed.
COMPOSER_ALREADY_OPEN = _derive(
    PROFILE,
    '<div class="msg-overlay-container" id="msg-overlay"></div>',
    '<div class="msg-overlay-container" id="msg-overlay">'
    '<div class="msg-overlay-conversation-bubble"><form class="msg-form">'
    '<div class="msg-form__contenteditable" contenteditable="true" role="textbox"></div>'
    '<button type="submit" class="msg-form__send-button" disabled>Send</button>'
    "</form></div></div>",
)
#: DERIVED -- a stranger's Message BUTTON and Invite button drawn BEFORE the
#: owner's controls in document order. The owner's Message control is then
#: position 1 of a list mixing an <a> and a <button>, which is what proves
#: the position the page computes is the position the click resolves.
STRANGER_FIRST = _derive(
    DISPATCHING,
    '<main class="scaffold-layout__main">',
    '<nav class="stranger-strip">'
    '<button type="button" aria-label="Message Morgan Example">Message</button>'
    '<button type="button" aria-label="Invite Morgan Example to connect">Connect</button>'
    '</nav><main class="scaffold-layout__main">',
)
#: DERIVED -- the link reaches a consistent profile of SOMEBODY ELSE (a
#: recycled vanity, a typo in the link): title, topcard and controls all name
#: another synthetic person. Nothing on the page is wrong; only the link is.
SOMEBODY_ELSE = PROFILE.replace("Casey Example", "Jordan Example")
assert SOMEBODY_ELSE.count("Jordan Example") >= 5, "the derivation drifted"
#: DERIVED -- the owner's topcard draws neither control, and a DIFFERENT
#: person WITH THE SAME NAME is carded in the aside with both. Exactly one
#: control on the page matches the owner's name, and it is a stranger's.
SAME_NAME_ELSEWHERE = _derive(
    _derive(
        _derive(PROFILE, _CONNECT_BUTTON, ""),
        '<a aria-label="Message Casey Example" ' + _MESSAGE_LINK_HREF + ' id="topcard-message">Message</a>',
        "",
    ),
    "<li><span>Morgan Example</span>",
    '<li><span>Casey Example</span> <button type="button" aria-label="Invite Casey '
    'Example to connect">Connect</button> <a aria-label="Message Casey Example" '
    'href="/messaging/compose/?recipient=ACoAASYNTHETICSYNTHETICSYNTHETIC0000004">'
    "Message</a></li><li><span>Morgan Example</span>",
)


class _Navigator:
    """Serves frozen worlds, LANDS where the test says, and RECORDS the asks.

    Each visit takes the next world, the last repeating. It records whether
    the caller asked for the NAMED-PROFILE door, which is what section 1 pins.
    """

    def __init__(self, *worlds: str, landed: str = LINK):
        self.worlds = list(worlds)
        self.landed = landed
        self.gotos: list[str] = []
        self.named: list[bool] = []

    async def goto(self, page, url: str, *, named_profile: bool = False) -> str:
        self.gotos.append(url)
        self.named.append(named_profile)
        if url != LINK:
            raise AssertionError(f"the act asked for {url!r}, which this test did not freeze")
        html = self.worlds[min(len(self.gotos) - 1, len(self.worlds) - 1)]
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return self.landed


def _clean(value, *, allow_owner: bool = False) -> None:
    """Nothing the page supplied about anybody, in a block, a grant or a
    receipt. The owner's name is allowed ONLY in the preview's
    ``whom_this_resolves_to`` -- asserted separately where it is."""
    text = json.dumps(value)
    needles = STRANGERS + THEIR_WORDS + (() if allow_owner else (OWNER, HEADLINE))
    for needle in needles:
        assert needle not in text, f"{needle!r} leaked into: {text[:400]}"


async def _pressed(page) -> str:
    return str(await page.evaluate("() => document.body.getAttribute('data-pressed') || ''"))


# ---------------------------------------------------------------------------
# 1. The doors
# ---------------------------------------------------------------------------


def test_the_second_door_admits_one_named_profile_and_nothing_else():
    assert readonly.named_profile_url(SEGMENT) == LINK
    assert readonly.assert_named_profile_url(LINK) == LINK
    assert readonly.assert_named_profile_url(readonly.named_profile_url(MEMBER_ID))
    for bad in (
        LINK[:-1],                                  # no trailing slash
        LINK + "?trk=example",                      # a query
        LINK + "#top",                              # a fragment
        LINK + "details/experience/",               # a sub-page
        "http://www.linkedin.com/in/casey-example-3f9a/",
        "https://linkedin.com/in/casey-example-3f9a/",
        "https://www.linkedin.com.example.org/in/casey-example-3f9a/",
        "https://www.linkedin.com/in/me/",          # his own, and too short
        "https://www.linkedin.com/in/ab/",
        "https://www.linkedin.com/in/-leading-hyphen-example/",
        "https://www.linkedin.com/in/someone example/",
        "https://www.linkedin.com/company/example-co/",
        "",
    ):
        with pytest.raises(WriteAttemptError):
            readonly.assert_named_profile_url(bad)


@pytest.mark.parametrize("segment", ["invite-someone-example", "someone-settings-example"])
def test_the_second_door_takes_no_exemption_from_the_forbidden_list(segment):
    """A segment that happens to carry a forbidden substring is refused, not
    excused: the only cost is the one profile it names."""
    url = readonly.named_profile_url(segment)
    with pytest.raises(WriteAttemptError, match="takes no exemption"):
        readonly.assert_named_profile_url(url)


def test_the_read_door_still_refuses_every_named_profile():
    for url in (LINK, readonly.named_profile_url(MEMBER_ID)):
        assert readonly.is_read_url(url) is False
        with pytest.raises(WriteAttemptError):
            readonly.assert_read_url(url)
    # And his own profile is still the read door's, not this one's.
    assert readonly.is_read_url("https://www.linkedin.com/in/me/") is True


class _Page:
    def __init__(self):
        self.visited: list[str] = []

    async def goto(self, url, **_kwargs):
        self.visited.append(url)


async def test_the_browser_swaps_the_door_only_when_asked(monkeypatch):
    from linkedin_server import browser as browser_module

    nav = browser_module.LinkedInBrowser()

    async def _no_wait(*_args, **_kwargs):
        return 0.0

    monkeypatch.setattr(nav, "wait_for_rate_slot", _no_wait)
    page = _Page()
    with pytest.raises(WriteAttemptError):
        await nav.goto(page, LINK)
    assert page.visited == [], "the read door let a named profile through"
    with pytest.raises(WriteAttemptError):
        await nav.goto(page, "https://www.linkedin.com/feed/", named_profile=True)
    assert page.visited == [], "the named door let a read address through"


def _package_sources():
    for folder in ("linkedin_server", "scripts"):
        for path in sorted((REPO / folder).rglob("*.py")):
            yield path, ast.parse(path.read_text(encoding="utf-8"))


def test_exactly_one_function_in_the_package_asks_for_the_named_door():
    """THE PIN. ``named_profile=`` is passed to a ``goto`` in ONE place,
    ``writes._load_named_profile`` -- so the second door is reachable from the
    two named-person specs and from nothing else, and no read can reach it."""
    callers = []
    for path, tree in _package_sources():
        for function in ast.walk(tree):
            if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for node in ast.walk(function):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "goto"
                    and any(kw.arg == "named_profile" for kw in node.keywords)
                ):
                    callers.append((path.name, function.name))
    assert sorted(set(callers)) == [("writes.py", "_load_named_profile")]


def test_the_second_door_is_referenced_only_by_the_browser_and_the_loader():
    users = set()
    for path, tree in _package_sources():
        for node in ast.walk(tree):
            if isinstance(node, (ast.Name, ast.Attribute)):
                name = node.id if isinstance(node, ast.Name) else node.attr
                if name == "assert_named_profile_url":
                    users.add(path.name)
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "assert_named_profile_url":
                        users.add(path.name)
    assert users == {"browser.py", "writes.py"}


async def test_the_loader_refuses_every_spec_that_is_not_a_named_person_act():
    nav = _Navigator(PROFILE)
    for action in ("send_reply", "send_invitation", "save_job"):
        with pytest.raises(WriteAttemptError, match="not a named-person act"):
            await writes._load_named_profile(nav, object(), spec_for_action(action), LINK)
    assert nav.gotos == []


# ---------------------------------------------------------------------------
# 2. The target: a link or a member id, canonical as the link; never a name
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "given",
    [
        LINK,
        LINK[:-1],
        "https://www.linkedin.com/in/casey-example-3f9a/?trk=people-card",
        "https://www.linkedin.com/in/casey-example-3f9a#about",
        "www.linkedin.com/in/casey-example-3f9a/",
        "linkedin.com/in/casey-example-3f9a",
        "https://in.linkedin.com/in/casey-example-3f9a/",
        "  " + LINK + "  ",
    ],
)
def test_a_profile_link_in_any_spelling_is_canonical_as_the_link(given):
    canonical = writes._target_for(CONNECT, given)
    assert canonical == LINK
    assert writes._target_for(CONNECT, canonical) == canonical, "not idempotent"
    assert writes.url_target_of(CONNECT, canonical) == SEGMENT


@pytest.mark.parametrize("given", [MEMBER_ID, "urn:li:fsd_profile:" + MEMBER_ID])
def test_a_member_id_is_accepted_and_composes_its_own_address(given):
    canonical = writes._target_for(CONNECT, given)
    assert canonical == "https://www.linkedin.com/in/" + MEMBER_ID + "/"
    assert writes.url_target_of(CONNECT, canonical) == MEMBER_ID


@pytest.mark.parametrize(
    "given",
    [
        OWNER,                                   # a name, with a space
        "casey",                                 # a bare word: a name or a segment?
        "Casey-Example",                         # still a bare word
        "https://www.linkedin.com/in/me/",       # his own profile
        LINK + "details/experience/",            # a sub-page
        "https://www.example.org/in/casey-example-3f9a/",
        "https://www.linkedin.com/company/example-co/",
        "casey\u200bexample",                    # an invisible character
        "",
        None,
    ],
)
def test_a_name_or_anything_that_is_not_a_profile_is_refused(given):
    with pytest.raises(WriteAttemptError):
        writes._target_for(CONNECT, given)
    with pytest.raises(WriteAttemptError):
        writes._target_for(MESSAGE, {"profile": given, "text": TEXT})


def test_the_message_target_is_the_profile_and_the_words_and_only_the_profile_reaches_a_url():
    canonical = writes._target_for(MESSAGE, TARGET)
    assert canonical == LINK + writes.TARGET_JOIN + TEXT
    assert writes._target_for(MESSAGE, canonical) == canonical, "not idempotent"
    assert writes.url_target_of(MESSAGE, canonical) == SEGMENT
    assert writes._text_component_of(MESSAGE, canonical) == TEXT
    for spec, target in ((CONNECT, LINK), (MESSAGE, canonical)):
        grant = writes.WriteGrant(action=spec.action, target=target, token="t", minted_at=0.0)
        rebuilt = spec.url_template.format(target=writes.url_target_of(spec, target))
        assert writes.assert_write_url(rebuilt, grant) == LINK
    with pytest.raises(WriteAttemptError):
        writes._target_for(MESSAGE, {"profile": LINK, "text": "two\nlines"})
    with pytest.raises(WriteAttemptError):
        writes._target_for(MESSAGE, {"profile": LINK, "text": ""})


def test_the_tables_name_both_actions():
    for spec in (CONNECT, MESSAGE):
        assert spec.action in writes.PERFORMABLE
        assert spec.action in writes.NAMED_PROFILE_ACTIONS
        assert spec.irreversible is True
        assert spec.unverifiable is None, "both acts read back what they did"
        assert writes.grant_is_possible(spec)
        assert spec.action not in writes._TOGGLE_ACTIONS
        assert spec.action not in writes.UPLOAD_ACTIONS
        assert spec.action in writes._WRITE_SURFACE_FOR_ACTION
        assert spec.action in writes._WHERE_TO_LOOK
        assert spec.action in writes._VERIFIED_FROM
        assert "delete_or_withdraw_anything" in spec.reversible_by
    assert writes.anchor_label_for(CONNECT) == dom.INVITE_CONTROL_SUFFIX
    assert writes.anchor_label_for(MESSAGE) == dom.MESSAGE_CONTROL_PREFIX
    assert MESSAGE.action in writes.TYPING_ACTIONS
    assert MESSAGE.action in writes.OPEN_THEN_TYPE_ACTIONS
    assert CONNECT.action not in writes.TYPING_ACTIONS
    assert MESSAGE.action not in writes.ADDRESSED_TYPING_ACTIONS
    assert MESSAGE.action not in writes.REPLY_ACTIONS


# ---------------------------------------------------------------------------
# 3. The reader: integers and closed tokens
# ---------------------------------------------------------------------------


async def _read(page, html: str) -> dict:
    await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
    return await dom.read_named_profile(page)


async def test_the_reader_identifies_the_owner_and_finds_their_two_controls(browser_page):
    reading = await _read(browser_page, PROFILE)
    assert reading["error"] is None
    assert reading["title_shape"] == "profile" and reading["topcards"] == 1
    assert reading["heading_matches_title"] is True
    assert reading["degree"] == "1st" and reading["degree_tokens"] == 1
    # Two Connect controls and two Message controls on the page, ONE of each
    # named for the owner -- the aside's belong to somebody else.
    assert reading["invite_controls"] == 2 and reading["invite_matches"] == 1
    assert reading["invite_index"] == 0 and reading["invite_in_topcard"] == 1
    assert reading["message_controls"] == 2 and reading["message_matches"] == 1
    assert reading["message_index"] == 0 and reading["message_in_topcard"] == 1
    assert reading["message_tag"] == "a" and reading["message_href"] == "compose"
    assert reading["more_actions"] == 1
    assert reading["dialogs"] == 0 and reading["composer_editors"] == 0
    assert reading["named_controls"] == []
    assert named_profile.identity_confirmed(reading) is True


async def test_the_reader_returns_nothing_that_names_anybody(browser_page):
    reading = await _read(browser_page, STRANGER_FIRST)
    text = json.dumps(reading)
    for needle in (OWNER, MEMBER_ID, "/messaging/") + STRANGERS:
        assert needle not in text, f"{needle!r} crossed out of the page"
    for key, value in reading.items():
        assert value is None or isinstance(value, (bool, int, list)) or value in (
            "profile", "none", "a", "button", "other", "compose", "thread",
            "1st", "2nd", "3rd+",
        ), f"{key}={value!r} is not an integer or a closed token"


async def test_a_notification_count_in_the_title_does_not_hide_the_owner(browser_page):
    counted = _derive(PROFILE, "<title>Casey Example", "<title>(3) Casey Example")
    reading = await _read(browser_page, counted)
    assert reading["heading_matches_title"] is True and reading["invite_matches"] == 1


async def test_a_same_name_stranger_elsewhere_on_the_page_is_never_the_target(browser_page):
    """THE WRONG-PERSON CASE A NAME COMPARISON INVITES. The owner's topcard
    draws neither control; a different person with the same name, carded in
    the aside, draws both. Exactly one control on the page matches the
    owner's name -- and it is a stranger's, so both acts refuse."""
    reading = await _read(browser_page, SAME_NAME_ELSEWHERE)
    assert reading["invite_matches"] == 1 and reading["invite_in_topcard"] == 0
    assert reading["message_matches"] == 1 and reading["message_in_topcard"] == 0
    for state_of in (named_profile.connect_state, named_profile.message_state):
        state, why, index = state_of(reading)
        assert state == named_profile.UNKNOWN and index is None
        assert "NOT inside their topcard" in why


async def test_positions_are_computed_over_the_same_list_the_click_resolves(browser_page):
    reading = await _read(browser_page, STRANGER_FIRST)
    assert reading["message_matches"] == 1 and reading["message_index"] == 1
    assert reading["invite_matches"] == 1 and reading["invite_index"] == 1
    await browser_page.click(dom.message_control_selector(reading["message_index"]))
    await browser_page.click(dom.invite_control_selector(reading["invite_index"]))
    assert await _pressed(browser_page) == (
        "[Message Casey Example][Invite Casey Example to connect]"
    )


@pytest.mark.parametrize(
    "world, fragment",
    [
        (NO_CONNECT, "draws no Connect control"),
        (TWO_CONNECTS, "is a refusal rather than a choice"),
    ],
    ids=["none", "two"],
)
async def test_connect_is_aimable_only_at_exactly_one_control(browser_page, world, fragment):
    state, why, index = named_profile.connect_state(await _read(browser_page, world))
    assert state == named_profile.UNKNOWN and index is None
    assert fragment in why


@pytest.mark.parametrize(
    "world, fragment",
    [
        (MESSAGE_TO_A_THREAD, "PAGE-MAY-VETO-NEVER-SUPPLY"),
        (COMPOSER_ALREADY_OPEN, "already open"),
    ],
    ids=["a-link-to-a-thread", "a-composer-already-open"],
)
async def test_message_is_refused_before_anything_is_pressed(browser_page, world, fragment):
    state, why, index = named_profile.message_state(await _read(browser_page, world))
    assert state == named_profile.UNKNOWN and index is None
    assert fragment in why


def test_the_selector_builders_take_a_position_and_nothing_else():
    assert dom.message_control_selector(2).endswith(" >> nth=2")
    for bad in (-1, True, "0", None, 1.0):
        with pytest.raises(ValueError):
            dom.message_control_selector(bad)


# ---------------------------------------------------------------------------
# 4. The preview: whom it resolved to, printed and kept nowhere
# ---------------------------------------------------------------------------


async def test_the_connect_preview_names_whom_it_resolved_to_and_keeps_it_nowhere(
    writes_on, browser_page
):
    nav = _Navigator(PROFILE)
    block = await preview(CONNECT, target=LINK, navigator=nav, page=browser_page)
    assert nav.gotos == [LINK] and nav.named == [True]
    assert block["to_confirm"]
    assert block["direction"]["currently"] == named_profile.CONNECT_FROM
    assert block["where"]["target"] == LINK and block["where"]["url"] == LINK
    whom = block["whom_this_resolves_to"]
    assert whom["name"] == OWNER and whom["headline"] == HEADLINE
    assert whom["link"] == LINK and whom["degree"] == "1st"
    assert whom[people_seam.PENDING_KEY] == people_seam.PENDING_NOTE
    assert "CHECK IT" in block["whom_this_resolves_to_why"]
    grant = writes._GRANTS[block["to_confirm"]]
    assert "whom_this_resolves_to" not in grant.preview, "the identity reached the grant"
    _clean(grant.preview)
    _clean(grant.observation.facts)
    assert grant.target == LINK
    _clean({key: value for key, value in block.items() if not key.startswith("whom")})


async def test_the_message_preview_prints_his_words_and_whom_they_would_reach(
    writes_on, browser_page
):
    block = await preview(MESSAGE, target=TARGET, navigator=_Navigator(PROFILE), page=browser_page)
    assert block["where"]["profile"] == LINK and block["where"]["text"] == TEXT
    assert block["direction"]["currently"] == named_profile.MESSAGE_FROM
    assert "reads '1st'" in block["direction"]["why"]
    assert block["whom_this_resolves_to"]["name"] == OWNER
    grant = writes._GRANTS[block["to_confirm"]]
    _clean(grant.preview)


async def test_a_second_degree_preview_says_it_will_stop_before_typing(writes_on, browser_page):
    block = await preview(
        MESSAGE, target=TARGET, navigator=_Navigator(SECOND_DEGREE), page=browser_page
    )
    assert "STOP BEFORE TYPING" in block["direction"]["why"]
    assert block["whom_this_resolves_to"]["degree"] == "2nd"


async def test_a_landing_that_is_not_the_named_profile_vetoes_and_mints_nothing(
    writes_on, browser_page
):
    """A member id LinkedIn sends to a vanity address, a removed profile, a
    wall: the page may VETO, never supply. Whatever the page there says, it is
    not read, and the landing is withheld rather than quoted."""
    elsewhere = "https://www.linkedin.com/in/morgan-example-77aa/"
    with pytest.raises(WriteAttemptError) as excinfo:
        await preview(
            CONNECT, target=LINK, navigator=_Navigator(PROFILE, landed=elsewhere), page=browser_page
        )
    message = str(excinfo.value)
    assert "did not land on the profile you named" in message and "WITHHELD" in message
    assert "morgan-example-77aa" not in message
    assert writes._GRANTS == {}, "a token exists for a profile nobody named"


async def test_a_landing_folded_for_case_and_encoding_is_still_the_named_profile(
    writes_on, browser_page
):
    upper = "https://www.linkedin.com/in/Casey-Example-3F9A/"
    block = await preview(
        CONNECT, target=LINK, navigator=_Navigator(PROFILE, landed=upper), page=browser_page
    )
    assert block["to_confirm"]


async def test_a_link_to_somebody_else_is_caught_by_the_name_the_block_prints(
    writes_on, browser_page
):
    """THE ONE FAILURE NO GATE HERE CAN CATCH, AND WHERE IT IS CAUGHT. The
    link reaches a consistent profile of another person. The target is a link,
    never a name, so there is nothing to compare the page against -- which is
    exactly why the block prints WHOM IT RESOLVED TO, and says to check it."""
    block = await preview(
        CONNECT, target=LINK, navigator=_Navigator(SOMEBODY_ELSE), page=browser_page
    )
    assert block["whom_this_resolves_to"]["name"] == "Jordan Example"
    assert "CHECK IT" in block["whom_this_resolves_to_why"]
    assert "WRONG" in block["whom_this_resolves_to_why"]


async def test_a_preview_where_only_a_stranger_matches_mints_nothing(writes_on, browser_page):
    with pytest.raises(WriteAttemptError, match="NOT inside their topcard"):
        await preview(
            CONNECT, target=LINK, navigator=_Navigator(SAME_NAME_ELSEWHERE), page=browser_page
        )
    assert writes._GRANTS == {}


#: DERIVED -- the owner's heading drawn as two block spans (so its text reads
#: across a line break), and a PROMOTED card with its own heading drawn above
#: the topcard inside main. The page still names its owner consistently --
#: the in-page comparison collapses whitespace -- but the topcard is no longer
#: the first section, and the section reader can no longer find it by name.
SPLIT_HEADING_AND_A_CARD_ABOVE = _derive(
    _derive(
        PROFILE,
        "<h2>Casey Example</h2>",
        '<h2><span style="display:block">Casey</span>'
        '<span style="display:block">Example</span></h2>',
    ),
    '<section aria-label="Primary content">',
    '<section class="promoted"><h2>Promoted</h2><p>An invented promoted card.</p>'
    '</section><section aria-label="Primary content">',
)


async def test_a_name_the_reader_cannot_tie_to_the_title_names_nobody(writes_on, browser_page):
    """WHOM IT RESOLVED TO MUST BE THE PAGE'S OWN OWNER, OR NOBODY. The section
    reader falls back to the FIRST section when no heading equals the title,
    and here the first section is a promoted card: without the cross-check
    against the title, the block would name 'Promoted' as the person."""
    block = await preview(
        CONNECT, target=LINK, navigator=_Navigator(SPLIT_HEADING_AND_A_CARD_ABOVE), page=browser_page
    )
    assert block["to_confirm"], "the page names one person; only the naming is refused"
    assert block["whom_this_resolves_to"] is None
    assert "Promoted" not in json.dumps(block)


async def test_an_identity_the_reader_cannot_confirm_is_named_as_unknown_not_guessed(
    writes_on, browser_page, monkeypatch
):
    """If the re-read cannot name the owner, the block says so and names
    nobody -- it does not fall back on a guess."""
    real = dom.read_profile_fields

    async def _no_sections(page, **kwargs):
        fields = await real(page, **kwargs)
        return {**fields, "sections": []}

    monkeypatch.setattr(dom, "read_profile_fields", _no_sections)
    block = await preview(CONNECT, target=LINK, navigator=_Navigator(PROFILE), page=browser_page)
    assert block["whom_this_resolves_to"] is None
    assert "cannot tell you whom" in block["whom_this_resolves_to_why"]


# ---------------------------------------------------------------------------
# 5. Connect, end to end
# ---------------------------------------------------------------------------


async def _connect_grant(page):
    block = await preview(CONNECT, target=LINK, navigator=_Navigator(PROFILE), page=page)
    return consume(block["to_confirm"], action=CONNECT.action, target=LINK)


async def test_a_connect_the_fresh_render_still_draws_was_not_sent(writes_on, browser_page):
    grant = await _connect_grant(browser_page)
    act = _Navigator(PROFILE, PROFILE)
    receipt = await writes.perform(act, browser_page, grant)
    assert act.gotos == [LINK, LINK], "one load to act, one FRESH render to verify"
    assert act.named == [True, True]
    assert receipt["clicked"]["clicks_made"] == 1 and receipt["clicked"]["error"] is None
    assert receipt["verification"]["observed_state"] == named_profile.CONNECT_STILL_DRAWN
    assert receipt["performed"] is False
    assert "NO INVITATION WAS SENT" in receipt["verification"]["why"]
    _clean(receipt)


async def test_a_connect_that_changed_the_control_is_unknown_and_says_what_it_became(
    writes_on, browser_page
):
    """What a sent invitation leaves on a profile is NEEDS-CAPTURE C-P2, so a
    gone control is reported as closed tokens and never called sent."""
    grant = await _connect_grant(browser_page)
    act = _Navigator(_body(connect="pending"), AFTER_PENDING)
    receipt = await writes.perform(act, browser_page, grant)
    assert await _pressed(browser_page) == "", "the fresh render replaced the pressed page"
    assert receipt["clicked"]["clicks_made"] == 1
    assert receipt["performed"] == writes.UNKNOWN
    why = receipt["verification"]["why"]
    assert "['pending']" in why and "C-P2" in why and "DO NOT RETRY" in why
    _clean(receipt)


async def test_a_connect_that_opened_a_dialog_presses_nothing_in_it(writes_on, browser_page):
    grant = await _connect_grant(browser_page)
    act = _Navigator(_body(connect="dialog"), PROFILE)
    receipt = await writes.perform(act, browser_page, grant)
    assert receipt["clicked"]["clicks_made"] == 1
    assert receipt["performed"] is False
    assert "A DIALOG OPENED" in receipt["verification"]["why"]
    assert "C-P3" in receipt["verification"]["why"]


async def test_the_press_reaches_the_owners_control_and_no_other(writes_on, browser_page):
    block = await preview(CONNECT, target=LINK, navigator=_Navigator(STRANGER_FIRST), page=browser_page)
    grant = consume(block["to_confirm"], action=CONNECT.action, target=LINK)

    class _KeepThePressedPage(_Navigator):
        async def goto(self, page, url, *, named_profile=False):
            if self.gotos:
                self.pressed = await _pressed(page)
            return await super().goto(page, url, named_profile=named_profile)

    act = _KeepThePressedPage(STRANGER_FIRST, STRANGER_FIRST)
    await writes.perform(act, browser_page, grant)
    assert act.pressed == "[Invite Casey Example to connect]"


async def test_the_act_refuses_before_any_press_when_the_landing_moved(writes_on, browser_page):
    grant = await _connect_grant(browser_page)
    act = _Navigator(PROFILE, landed="https://www.linkedin.com/in/morgan-example-77aa/")
    with pytest.raises(WriteAttemptError, match="refusing to act") as excinfo:
        await writes.perform(act, browser_page, grant)
    assert "WITHHELD" in str(excinfo.value)
    assert "morgan-example-77aa" not in str(excinfo.value)
    assert await _pressed(browser_page) == ""


async def test_the_act_refuses_when_connect_is_gone_since_the_preview(writes_on, browser_page):
    grant = await _connect_grant(browser_page)
    with pytest.raises(WriteAttemptError, match="refusing to click"):
        await writes.perform(_Navigator(NO_CONNECT), browser_page, grant)
    assert await _pressed(browser_page) == ""


# ---------------------------------------------------------------------------
# 6. Message, end to end
# ---------------------------------------------------------------------------


async def _message_grant(page, world: str = PROFILE, target=None):
    target = TARGET if target is None else target
    block = await preview(MESSAGE, target=target, navigator=_Navigator(world), page=page)
    return consume(block["to_confirm"], action=MESSAGE.action, target=target)


async def test_a_message_that_lands_reports_sent_in_place_with_a_before_count(
    writes_on, browser_page
):
    grant = await _message_grant(browser_page)
    act = _Navigator(DISPATCHING)
    receipt = await writes.perform(act, browser_page, grant)
    assert act.gotos == [LINK], "one load; the conversation is read where it opened"
    assert await _pressed(browser_page) == "[Message Casey Example]"
    opened = receipt["opened_conversation_gate"]
    assert opened["proceeded"] is True and opened["refused_condition"] is None
    assert opened["observed"]["events_with_text"] == 0
    assert receipt["send_gate"]["proceeded"] is True
    assert receipt["clicked"]["clicks_made"] == 2
    assert receipt["clicked"]["opener_clicks"] == 1
    assert receipt["typed_text"]["submit_was_pressed"] is True
    assert receipt["verification"]["observed_state"] == named_profile.MESSAGE_SENT
    assert receipt["performed"] is True and receipt["verified"] is True
    assert "from 0 to 1" in receipt["verification"]["why"]
    _clean(receipt)


async def test_a_message_that_never_left_the_box_reports_not_sent(writes_on, browser_page):
    grant = await _message_grant(browser_page)
    receipt = await writes.perform(_Navigator(PROFILE), browser_page, grant)
    assert receipt["clicked"]["clicks_made"] == 2
    assert receipt["verification"]["observed_state"] == named_profile.MESSAGE_NOT_SENT
    assert receipt["performed"] is False
    assert "NOTHING WAS DISPATCHED" in receipt["verification"]["why"]


async def test_a_second_degree_message_presses_records_and_types_nothing(writes_on, browser_page):
    """M M6's capture: Message is pressed, what opened is recorded as counts,
    and NOTHING is typed -- a message there may spend an InMail credit."""
    grant = await _message_grant(browser_page, SECOND_DEGREE)
    receipt = await writes.perform(_Navigator(SECOND_DEGREE), browser_page, grant)
    opened = receipt["opened_conversation_gate"]
    assert opened["proceeded"] is False
    assert opened["refused_condition"] == "3_not_a_first_degree_connection"
    assert opened["observed"]["degree"] == "2nd" and opened["observed"]["editors"] == 1
    assert receipt["clicked"]["clicks_made"] == 1 and receipt["clicked"]["opener_clicks"] == 1
    assert receipt["typed_text"]["text_was_entered"] is False
    assert receipt["performed"] is False
    assert "NOTHING WAS TYPED" in receipt["verification"]["why"]
    editor = browser_page.locator(named_profile.COMPOSER_EDITOR_SELECTOR)
    assert await editor.inner_text() == ""


@pytest.mark.parametrize(
    "world, condition",
    [
        (_body(message_opens="nothing", dispatches="yes"), "5_not_one_conversation"),
        (_body(message_opens="draft", dispatches="yes"), "7_not_empty"),
        (_body(message_opens="new-message", dispatches="yes"), "6_recipient_box"),
        (_body(message_opens="navigates", dispatches="yes"), "1_navigated_away"),
    ],
    ids=["opens-nothing", "opens-a-draft", "opens-a-new-message", "navigates"],
)
async def test_nothing_is_typed_unless_the_press_opened_one_empty_conversation(
    writes_on, browser_page, world, condition
):
    """Every shape a press could open that is not the measured empty form
    stops the act BEFORE A WORD IS TYPED, and names which condition it was.
    What a profile's Message press opens is NEEDS-CAPTURE C-P4."""
    grant = await _message_grant(browser_page)
    receipt = await writes.perform(_Navigator(world), browser_page, grant)
    opened = receipt["opened_conversation_gate"]
    assert opened["proceeded"] is False and opened["refused_condition"] == condition
    assert receipt["clicked"]["clicks_made"] == 1
    assert receipt["typed_text"]["text_was_entered"] is False
    assert receipt["performed"] is False
    _clean(receipt)


#: DERIVED -- a composer that changes the words as they are typed. Send does
#: turn on; what is in the box is not what he confirmed.
CHANGES_THE_WORDS = _derive(
    DISPATCHING,
    "send.disabled = (editor.textContent.trim().length === 0);\n    });",
    "if (editor.textContent.slice(-1) !== '!') "
    "{ editor.textContent = editor.textContent + '!'; } "
    "send.disabled = (editor.textContent.trim().length === 0);\n    });",
)


async def test_send_is_not_pressed_when_the_box_holds_other_words_than_his(
    writes_on, browser_page
):
    grant = await _message_grant(browser_page)
    receipt = await writes.perform(_Navigator(CHANGES_THE_WORDS), browser_page, grant)
    gate = receipt["send_gate"]
    assert gate["proceeded"] is False and gate["refused_condition"] == "5_words_not_exact"
    assert gate["observed"]["held_characters"] == gate["observed"]["grant_characters"] + 1
    assert receipt["clicked"]["clicks_made"] == 1
    assert receipt["performed"] is not True


#: DERIVED -- the conversation already ends with HIS exact words (sent once
#: before), so the before-count is one and the delta must still be exactly one.
ALREADY_SAID_ONCE = _derive(
    DISPATCHING,
    "'<p class=\"msg-s-event-listitem__body t-14\">Good to hear from you last month.</p></div></li>' +",
    "'<p class=\"msg-s-event-listitem__body t-14\">Good to hear from you last month.</p></div></li>' +"
    " '<li class=\"msg-s-message-list__event clearfix\">"
    "<div class=\"msg-s-event-listitem msg-s-event-listitem--last-in-group\">"
    f"<p class=\"msg-s-event-listitem__body t-14\">{TEXT}</p></div></li>' +",
)


async def test_an_identical_earlier_message_is_counted_and_the_delta_is_still_one(
    writes_on, browser_page
):
    grant = await _message_grant(browser_page)
    receipt = await writes.perform(_Navigator(ALREADY_SAID_ONCE), browser_page, grant)
    assert receipt["opened_conversation_gate"]["observed"]["events_with_text"] == 1
    assert receipt["performed"] is True
    assert "from 1 to 2" in receipt["verification"]["why"]


#: DERIVED -- his words already the last message, and a Send that EMPTIES
#: the box and draws nothing new (a send whose redraw never came, or one that
#: never left). The last message is his exact words, so only the delta can
#: say this is not a send.
EMPTIED_AND_DREW_NOTHING = _derive(
    ALREADY_SAID_ONCE,
    "      list.insertBefore(li, list.lastElementChild);\n",
    "",
)


async def test_an_identical_earlier_message_cannot_stand_in_for_this_one(writes_on, browser_page):
    grant = await _message_grant(browser_page)
    receipt = await writes.perform(_Navigator(EMPTIED_AND_DREW_NOTHING), browser_page, grant)
    assert receipt["opened_conversation_gate"]["observed"]["events_with_text"] == 1
    assert receipt["clicked"]["clicks_made"] == 2
    assert receipt["performed"] == writes.UNKNOWN
    assert "1 before, 1 after" in receipt["verification"]["why"]


#: DERIVED -- the redraw draws his words WEARING the --other modifier: the
#: other side sent the same words, which a count and a text match cannot tell.
FROM_THE_OTHER_SIDE = _derive(
    DISPATCHING,
    "item.className = 'msg-s-event-listitem msg-s-event-listitem--last-in-group';",
    "item.className = 'msg-s-event-listitem msg-s-event-listitem--last-in-group "
    "msg-s-event-listitem--other';",
)


async def test_the_same_words_from_the_other_side_are_not_his_send(writes_on, browser_page):
    grant = await _message_grant(browser_page)
    receipt = await writes.perform(_Navigator(FROM_THE_OTHER_SIDE), browser_page, grant)
    assert receipt["performed"] == writes.UNKNOWN
    assert "last message from: other" in receipt["verification"]["why"]
    assert "Do NOT retry" in receipt["verification"]["why"]


async def test_the_message_press_reaches_the_owners_control_among_strangers(
    writes_on, browser_page
):
    grant = await _message_grant(browser_page, STRANGER_FIRST)
    receipt = await writes.perform(_Navigator(STRANGER_FIRST), browser_page, grant)
    assert await _pressed(browser_page) == "[Message Casey Example]"
    assert receipt["performed"] is True


# ---------------------------------------------------------------------------
# 7. The three controls, and the tools
# ---------------------------------------------------------------------------


async def test_control_1_it_refuses_without_a_grant(monkeypatch, browser_page):
    monkeypatch.delenv(writes.WRITES_FLAG, raising=False)
    nav = _Navigator(PROFILE)
    with pytest.raises(WriteAttemptError, match="disabled"):
        await preview(CONNECT, target=LINK, navigator=nav, page=browser_page)
    with pytest.raises(WriteAttemptError, match="disabled"):
        consume("anything", action=CONNECT.action, target=LINK)
    for tool, args in (
        (server.linkedin_connect_from_profile, (LINK,)),
        (server.linkedin_message_from_profile, (LINK, TEXT)),
    ):
        off = await tool(*args)
        assert off["error"] == "writes_disabled" and off["performed"] is False
    monkeypatch.setenv(writes.WRITES_FLAG, "1")
    unredeemed = writes.WriteGrant(action=CONNECT.action, target=LINK, token="t", minted_at=0.0)
    with pytest.raises(WriteAttemptError, match="not been redeemed"):
        await writes.perform(nav, browser_page, unredeemed)
    assert nav.gotos == [], "a refused write navigated"


async def test_control_2_it_refuses_a_grant_for_another_person_or_other_words(
    writes_on, browser_page
):
    block = await preview(CONNECT, target=LINK, navigator=_Navigator(PROFILE), page=browser_page)
    with pytest.raises(WriteAttemptError, match="minted for target"):
        consume(block["to_confirm"], action=CONNECT.action, target=MEMBER_ID)
    block = await preview(MESSAGE, target=TARGET, navigator=_Navigator(PROFILE), page=browser_page)
    with pytest.raises(WriteAttemptError, match="minted for target"):
        consume(block["to_confirm"], action=MESSAGE.action, target={"profile": LINK, "text": TEXT + "!"})
    block = await preview(CONNECT, target=LINK, navigator=_Navigator(PROFILE), page=browser_page)
    with pytest.raises(WriteAttemptError, match="minted for 'connect_from_profile'"):
        consume(block["to_confirm"], action=MESSAGE.action, target=TARGET)


async def test_control_3_it_refuses_a_second_use_of_the_same_grant(writes_on, browser_page):
    grant = await _message_grant(browser_page)
    await writes.perform(_Navigator(DISPATCHING), browser_page, grant)
    second = _Navigator(DISPATCHING)
    with pytest.raises(WriteAttemptError, match="already been used once"):
        await writes.perform(second, browser_page, grant)
    assert second.gotos == [], "the second use navigated before it refused"


async def test_the_tools_refuse_a_name_before_a_browser_is_opened(writes_on, monkeypatch):
    class _NoBrowser:
        def session(self):
            raise AssertionError("the tool opened a browser for a name")

    monkeypatch.setattr(server, "BROWSER", _NoBrowser())
    for result in (
        await server.linkedin_connect_from_profile(OWNER),
        await server.linkedin_message_from_profile("casey", TEXT),
        await server.linkedin_message_from_profile(LINK, "two\nlines"),
    ):
        assert result.get("error"), result
        assert "opened a browser" not in json.dumps(result)


def test_both_tools_are_registered_as_sanctioned_writes():
    for tool, action in (
        ("linkedin_connect_from_profile", "connect_from_profile"),
        ("linkedin_message_from_profile", "message_from_profile"),
    ):
        assert writes.SANCTIONED_WRITES[tool].action == action
        assert callable(getattr(server, tool, None))
        assert readonly.name_implies_write(tool)
