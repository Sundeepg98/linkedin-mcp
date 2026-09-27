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


#: EVERY ENCODED ASCII OCTET IS REFUSED. The cold re-check of 2026-09-27
#: found the segment's percent-encoded unit admitted ANY octet, which let back
#: in, through the encoding, everything the literal rules refuse -- and an
#: ASCII letter or digit is written as itself, so no encoded ASCII octet is
#: ever needed.
ENCODED_ASCII = (
    "casey%20example",            # a space: a two-word NAME
    "someone%2Fexample",          # a slash
    "someone%00example",          # a NUL
    "someone%0Aexample",          # a newline
    "someone%2Finvite-example",   # a forbidden substring, spelled encoded
    "%41someone-example",         # an encoded letter, never needed
)
#: ENCODED NON-ASCII THAT IS NOT A LETTER passes the shape and is refused on
#: the DECODED form: a no-break space, a zero-width space, a direction
#: override, and a UTF-8 sequence cut short.
ENCODED_NOT_A_LETTER = (
    "casey%C2%A0example",
    "casey%E2%80%8Bexample",
    "someone%E2%80%AEexample",
    "someone-example%C3",
)
#: What the encoded unit exists for: a vanity name with a non-ASCII letter,
#: as LinkedIn serves it -- percent-encoded UTF-8.
ENCODED_LETTER = "jos%C3%A9-example"


@pytest.mark.parametrize("segment", ENCODED_ASCII + ENCODED_NOT_A_LETTER)
def test_no_encoding_lets_back_in_what_the_segment_refuses(segment):
    link = "https://www.linkedin.com/in/" + segment + "/"
    assert readonly.valid_named_profile_segment(segment) is False
    with pytest.raises(WriteAttemptError):
        readonly.named_profile_url(segment)
    with pytest.raises(WriteAttemptError):
        readonly.assert_named_profile_url(link)
    for spec, target in ((CONNECT, link), (MESSAGE, {"profile": link, "text": TEXT})):
        with pytest.raises(WriteAttemptError):
            writes._target_for(spec, target)


@pytest.mark.parametrize("segment", ENCODED_ASCII)
def test_the_write_specs_own_address_pattern_refuses_an_encoded_ascii_octet(segment):
    """THE SECOND COPY OF THE SHAPE. Each spec's ``url_pattern`` is what
    ``assert_write_url`` holds a rebuilt address to, and it carried the same
    any-octet unit; it is a regex alone, so it refuses the ASCII octets and
    leaves the decoded check to the door."""
    link = "https://www.linkedin.com/in/" + segment + "/"
    for spec in (CONNECT, MESSAGE):
        assert spec.url_pattern.fullmatch(link) is None, (spec.action, segment)


def test_a_vanity_name_with_a_non_ascii_letter_is_still_admitted():
    link = "https://www.linkedin.com/in/" + ENCODED_LETTER + "/"
    assert readonly.valid_named_profile_segment(ENCODED_LETTER) is True
    assert readonly.named_profile_url(ENCODED_LETTER) == link
    assert readonly.assert_named_profile_url(link) == link
    canonical = writes._target_for(CONNECT, link)
    assert canonical == link and writes.url_target_of(CONNECT, canonical) == ENCODED_LETTER
    for spec in (CONNECT, MESSAGE):
        assert spec.url_pattern.fullmatch(link)


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


@pytest.mark.parametrize("given", ["casey", "casey-example-3f9a", "Casey"])
def test_a_bare_word_is_refused_as_a_possible_name_and_says_so(given):
    """A one-word name and a vanity segment are the same shape, so a bare word
    is refused BY ITS OWN RULE, with the reason -- not by the host check a
    bare word happens to fail one line later, whose message would send him
    looking for the wrong mistake."""
    with pytest.raises(WriteAttemptError, match="bare word"):
        named_profile.profile_segment(given)


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
    assert reading["invite_topcard_index"] == 0
    assert reading["message_controls"] == 2 and reading["message_matches"] == 1
    assert reading["message_index"] == 0 and reading["message_in_topcard"] == 1
    assert reading["message_topcard_index"] == 0
    assert reading["message_tag"] == "a" and reading["message_href"] == "compose"
    assert reading["more_actions"] == 1
    assert reading["dialogs"] == 0 and reading["composer_editors"] == 0
    # Nothing is open yet, so no conversation can be anybody's.
    assert reading["bubbles_with_editor"] == 0 and reading["bubble_titles"] == 0
    assert reading["bubble_title_names_owner"] is False
    assert reading["named_controls"] == []
    assert reading["dialog_controls"] == [] and reading["dialog_note_fields"] == 0
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


#: DERIVED -- the title names one person and the topcard's heading another.
TITLE_AND_TOPCARD_DISAGREE = _derive(
    PROFILE, "<title>Casey Example | LinkedIn</title>", "<title>Jordan Example | LinkedIn</title>"
)


async def test_a_topcard_that_names_somebody_other_than_the_title_confirms_nobody(browser_page):
    reading = await _read(browser_page, TITLE_AND_TOPCARD_DISAGREE)
    assert reading["topcards"] == 1 and reading["topcard_headings"] == 1
    assert reading["heading_matches_title"] is False
    assert named_profile.identity_confirmed(reading) is False
    state, why, index = named_profile.connect_state(reading)
    assert state == named_profile.UNKNOWN and index is None
    assert "NEEDS-CAPTURE C-P1" in why


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


#: DERIVED -- somebody else's Connect and Message drawn INSIDE the owner's
#: topcard, before the owner's own (a mutual connection's chip, say). Inside
#: the topcard the owner's controls are then position 1 of lists that mix
#: nothing else, which is what proves the position the page counts inside the
#: topcard is the position the scoped press resolves.
STRANGER_IN_THE_TOPCARD = _derive(
    STRANGER_FIRST,
    '<div class="topcard-actions">',
    '<div class="topcard-actions">'
    '<button type="button" aria-label="Invite Riley Example to connect">Connect</button>'
    '<a aria-label="Message Riley Example" '
    'href="/messaging/compose/?recipient=ACoAASYNTHETICSYNTHETICSYNTHETIC0000003">Message</a>',
)


@pytest.mark.parametrize(
    "world, inside", [(STRANGER_FIRST, 0), (STRANGER_IN_THE_TOPCARD, 1)],
    ids=["strangers-before-the-topcard", "a-stranger-inside-the-topcard"],
)
async def test_positions_are_counted_inside_the_topcard_the_press_is_scoped_to(
    browser_page, world, inside
):
    """The page-wide position of the owner's controls is 1 in both worlds; the
    position INSIDE THE TOPCARD is what the press is aimed by, and pressing by
    it reaches the owner's controls and no other."""
    reading = await _read(browser_page, world)
    assert reading["message_matches"] == 1 and reading["message_index"] == 1 + inside
    assert reading["invite_matches"] == 1 and reading["invite_index"] == 1 + inside
    assert reading["message_topcard_index"] == inside
    assert reading["invite_topcard_index"] == inside
    await browser_page.click(
        dom.topcard_message_control_selector(reading["message_topcard_index"]), timeout=5_000
    )
    await browser_page.click(
        dom.topcard_invite_control_selector(reading["invite_topcard_index"]), timeout=5_000
    )
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
    for builder in (dom.topcard_invite_control_selector, dom.topcard_message_control_selector):
        built = builder(2)
        assert built.endswith(" >> nth=2")
        alternatives = built[: -len(" >> nth=2")].split(",")
        assert all(
            part.strip().startswith(dom.NAMED_PROFILE_TOPCARD + " ") for part in alternatives
        ), built
        for bad in (-1, True, "0", None, 1.0):
            with pytest.raises(ValueError):
                builder(bad)
    # THE PAGE-WIDE MESSAGE BUILDER IS GONE: nothing pressed Message but this
    # route, and a builder kept beside the scoped one is one edit from use.
    assert not hasattr(dom, "message_control_selector")


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
    why = receipt["verification"]["why"]
    assert "A DIALOG OPENED" in why and "C-P3" in why
    # C-P3'S FIRST READING RIDES THE RECEIPT: what the dialog drew, as closed
    # tokens and a count read in the page, before the reload discarded it.
    assert "['add_a_note', 'send_without_a_note']" in why
    assert "0 note field(s)" in why
    assert "Add a note to your invitation" not in json.dumps(receipt)


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


#: A transparent layer over the whole page. Every press is intercepted while
#: it is there, and the press RETRIES until it can land.
_PRESS_HOLD = (
    '<div id="press-hold" style="position:fixed;left:0;top:0;width:100%;'
    'height:100%;z-index:99999;background:transparent"></div>'
)
#: DERIVED -- A RE-RENDER DURING THE PRESS, the world the cold re-check of
#: 2026-09-27 built. The layer holds the press back for 1.2 s; then it lifts,
#: the owner's Connect is replaced by an identical fresh node -- the element
#: the press resolved is detached, so the selector is resolved again -- and a
#: STRANGER's 'Invite ... to connect' is drawn at the very top of the page,
#: before the topcard. The page-wide press landed on the stranger.
RERENDERED_DURING_THE_PRESS = _derive(
    PROFILE,
    "</body>",
    _PRESS_HOLD
    + "<script>setTimeout(function () {"
    "  var hold = document.getElementById('press-hold');"
    "  if (hold) { hold.parentNode.removeChild(hold); }"
    "  var owners = document.getElementById('topcard-connect');"
    "  if (owners) { owners.replaceWith(owners.cloneNode(true)); }"
    "  var stranger = document.createElement('button');"
    "  stranger.type = 'button';"
    "  stranger.setAttribute('aria-label', 'Invite Morgan Example to connect');"
    "  stranger.textContent = 'Connect';"
    "  document.body.insertBefore(stranger, document.body.firstChild);"
    "}, 1200);</script></body>",
)


class _KeepsWhatWasPressed(_Navigator):
    """Records what the act pressed before the verification's fresh render
    replaces the page it pressed on."""

    async def goto(self, page, url, *, named_profile=False):
        if self.gotos:
            self.pressed = await _pressed(page)
        return await super().goto(page, url, named_profile=named_profile)


async def test_a_re_render_during_the_press_cannot_hand_it_to_a_stranger(writes_on, browser_page):
    """THE PRESS IS SCOPED TO THE OWNER'S TOPCARD, so a selector resolved
    again mid-press can reach only a control of the owner's own topcard --
    here, the fresh copy of the owner's Connect -- and never the stranger's
    control drawn earlier in the page."""
    grant = await _connect_grant(browser_page)
    act = _KeepsWhatWasPressed(RERENDERED_DURING_THE_PRESS, PROFILE)
    receipt = await writes.perform(act, browser_page, grant)
    assert act.pressed == "[Invite Casey Example to connect]", act.pressed
    assert receipt["clicked"]["clicks_made"] == 1 and receipt["clicked"]["error"] is None
    _clean(receipt)


@pytest.mark.parametrize("which", ["connect", "message"])
async def test_a_press_that_fails_is_reported_by_its_type_and_names_nobody(
    writes_on, browser_page, monkeypatch, which
):
    """THE RECEIPT OF A PRESS THAT FAILED, found by the cold re-check of
    2026-09-27: the browser library's timeout text carries a CALL LOG quoting
    the element it resolved -- the owner's name in both controls' labels, and
    the member id in the Message link -- and ``clicked.error`` printed it
    whole. It now carries the exception's TYPE (``describe_click_error``)."""
    spec, target = (CONNECT, LINK) if which == "connect" else (MESSAGE, TARGET)
    block = await preview(spec, target=target, navigator=_Navigator(PROFILE), page=browser_page)
    grant = consume(block["to_confirm"], action=spec.action, target=target)
    monkeypatch.setattr(writes, "CLICK_TIMEOUT_MS", 800)
    held = _derive(PROFILE, "</body>", _PRESS_HOLD + "</body>")
    receipt = await writes.perform(_Navigator(held, PROFILE), browser_page, grant)
    assert receipt["clicked"]["error"] == "TimeoutError", receipt["clicked"]["error"]
    assert receipt["clicked"]["clicks_made"] == 0
    assert MEMBER_ID not in json.dumps(receipt)
    _clean(receipt)


def test_this_packages_own_refusal_is_still_reported_whole():
    """The other half of ``describe_click_error``: a ``WriteAttemptError`` is
    raised by this package with a reason it composed, so it crosses whole."""
    ours = WriteAttemptError("refusing to press: a reason this package wrote")
    assert writes.describe_click_error(ours) == (
        "WriteAttemptError: refusing to press: a reason this package wrote"
    )
    assert writes.describe_click_error(TimeoutError("call log: <button ...>")) == "TimeoutError"


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
    # WHOSE CONVERSATION, checked before the fill and again before Send.
    assert opened["observed"]["conversation_titles"] == 1
    assert opened["observed"]["conversation_names_the_owner"] is True
    assert opened["observed"]["composer_appeared"] is True
    assert receipt["send_gate"]["proceeded"] is True
    assert receipt["send_gate"]["observed"]["conversation_names_the_owner"] is True
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
    # C-P5's first reading, as hints: this synthetic composer says nothing
    # about InMail or credits.
    assert opened["observed"]["inmail_words"] is False
    assert opened["observed"]["credit_words"] is False


#: DERIVED -- the conversation that opens for a non-connection names an
#: InMail and a credit, as LinkedIn's help says an InMail composer does. The
#: wording is invented; C-P5 is what captures the real one.
SECOND_DEGREE_INMAIL = _derive(
    SECOND_DEGREE,
    "    bubble.appendChild(header);",
    "    bubble.appendChild(header);\n"
    "    var notice = document.createElement('p');\n"
    "    notice.textContent = 'InMail -- uses 1 of your InMail credits';\n"
    "    bubble.appendChild(notice);",
)


async def test_a_composer_that_names_a_credit_is_recorded_and_still_typed_nothing(
    writes_on, browser_page
):
    grant = await _message_grant(browser_page, SECOND_DEGREE_INMAIL)
    receipt = await writes.perform(_Navigator(SECOND_DEGREE_INMAIL), browser_page, grant)
    observed = receipt["opened_conversation_gate"]["observed"]
    assert observed["inmail_words"] is True and observed["credit_words"] is True
    assert receipt["opened_conversation_gate"]["refused_condition"] == (
        "3_not_a_first_degree_connection"
    )
    assert receipt["typed_text"]["text_was_entered"] is False
    assert "uses 1 of your" not in json.dumps(receipt)


@pytest.mark.parametrize(
    "world, condition",
    [
        (_body(message_opens="nothing", dispatches="yes"), "5_not_one_conversation"),
        (_body(message_opens="draft", dispatches="yes"), "8_not_empty"),
        (_body(message_opens="new-message", dispatches="yes"), "7_recipient_box"),
        (_body(message_opens="navigates", dispatches="yes"), "1_navigated_away"),
        # WHOSE CONVERSATION (the cold re-check, 2026-09-27): the press opens
        # one empty conversation, measured-shaped in every other respect,
        # headed by somebody else -- and a GROUP that includes the named
        # person, whose title contains their name and is not it.
        (
            _body(conversation_with="Morgan Example", dispatches="yes"),
            "6_not_their_conversation",
        ),
        (
            _body(conversation_with="Casey Example, Morgan Example", dispatches="yes"),
            "6_not_their_conversation",
        ),
    ],
    ids=[
        "opens-nothing", "opens-a-draft", "opens-a-new-message", "navigates",
        "opens-somebody-elses", "opens-a-group-that-includes-them",
    ],
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


async def test_a_conversation_headed_by_somebody_else_is_read_and_refused_in_the_page(
    writes_on, browser_page
):
    """WHAT THE REFUSAL SAW, as a count and two booleans computed in the page:
    one title, not the owner's name, not containing it -- and the composer
    left exactly as it opened."""
    grant = await _message_grant(browser_page)
    world = _body(conversation_with="Morgan Example", dispatches="yes")
    receipt = await writes.perform(_Navigator(world), browser_page, grant)
    observed = receipt["opened_conversation_gate"]["observed"]
    assert observed["editors"] == 1 and observed["bubbles_with_editor"] == 1
    assert observed["conversation_titles"] == 1
    assert observed["conversation_names_the_owner"] is False
    assert observed["title_contains_the_owner"] is False
    editor = browser_page.locator(named_profile.COMPOSER_EDITOR_SELECTOR)
    assert await editor.inner_text() == ""


#: DERIVED -- THE PRESS OPENS NOTHING, and a conversation with somebody else
#: is drawn DURING the press (on its first mouse movement): the shape of an
#: overlay conversation LinkedIn restores by itself. Counts alone read it as
#: "none before the press, one after" -- the cold re-check of 2026-09-27 built
#: this world, and his words went into it and read SENT.
RESTORED_DURING_THE_PRESS = _derive(
    _body(message_opens="nothing", dispatches="yes"),
    "</body>",
    "<script>document.addEventListener('mousemove', function () {"
    "  var bubble = document.createElement('div');"
    "  bubble.className = 'msg-overlay-conversation-bubble';"
    "  bubble.innerHTML ="
    "    '<header class=\"msg-overlay-bubble-header\">' +"
    "    '<h2 class=\"msg-overlay-bubble-header__title\">Morgan Example</h2></header>' +"
    "    '<ul class=\"msg-s-message-list-content\"></ul>' +"
    "    '<form class=\"msg-form\"><div class=\"msg-form__contenteditable t-14\" '"
    "    + 'contenteditable=\"true\" role=\"textbox\"></div>' +"
    "    '<button type=\"submit\" class=\"msg-form__send-button artdeco-button\" disabled>'"
    "    + 'Send</button></form>';"
    "  document.getElementById('msg-overlay').appendChild(bubble);"
    "}, {once: true});</script></body>",
)


async def test_a_conversation_the_press_did_not_open_never_takes_his_words(
    writes_on, browser_page
):
    grant = await _message_grant(browser_page)
    receipt = await writes.perform(_Navigator(RESTORED_DURING_THE_PRESS), browser_page, grant)
    opened = receipt["opened_conversation_gate"]
    assert opened["observed"]["bubbles_with_editor"] == 1, "the restored bubble was not drawn"
    assert opened["proceeded"] is False
    assert opened["refused_condition"] == "6_not_their_conversation"
    assert receipt["typed_text"]["text_was_entered"] is False
    assert receipt["performed"] is False
    editor = browser_page.locator(named_profile.COMPOSER_EDITOR_SELECTOR)
    assert await editor.inner_text() == ""
    _clean(receipt)


#: DERIVED -- the conversation changes hands WHILE HE TYPES: the fill's own
#: input event re-titles it. The opened gate passed; only a re-check between
#: the fill and Send can see it.
CHANGES_HANDS_AS_HE_TYPES = _derive(
    DISPATCHING,
    "send.disabled = (editor.textContent.trim().length === 0);\n    });",
    "send.disabled = (editor.textContent.trim().length === 0); "
    "title.textContent = 'Morgan Example';\n    });",
)


async def test_send_is_not_pressed_when_the_conversation_changes_hands_after_the_fill(
    writes_on, browser_page
):
    grant = await _message_grant(browser_page)
    receipt = await writes.perform(_Navigator(CHANGES_HANDS_AS_HE_TYPES), browser_page, grant)
    assert receipt["opened_conversation_gate"]["proceeded"] is True
    gate = receipt["send_gate"]
    assert gate["proceeded"] is False
    assert gate["refused_condition"] == "6_not_their_conversation"
    assert gate["observed"]["words_exact"] is True
    assert gate["observed"]["conversation_names_the_owner"] is False
    assert receipt["clicked"]["clicks_made"] == 1 and receipt["clicked"]["opener_clicks"] == 1
    assert receipt["typed_text"]["text_was_entered"] is True
    assert receipt["typed_text"]["submit_was_pressed"] is False
    assert receipt["performed"] is not True
    _clean(receipt)


#: DERIVED -- the conversation is drawn 600 ms after the press rather than at
#: once. How long LinkedIn's overlay takes has never been measured (C-P4).
DRAWN_A_MOMENT_LATER = _derive(
    DISPATCHING,
    "    if (label === 'Message ' + owner) { openConversation(); }",
    "    if (label === 'Message ' + owner) { setTimeout(openConversation, 600); }",
)


async def test_a_conversation_drawn_a_moment_after_the_press_is_still_found(
    writes_on, browser_page
):
    """THE BOUNDED WAIT, and it decides nothing: without it the gate read the
    page the instant the press returned and refused a composer drawn a moment
    later. The receipt records how long it took -- C-P4's timing, measured by
    the first supervised act."""
    grant = await _message_grant(browser_page)
    receipt = await writes.perform(_Navigator(DRAWN_A_MOMENT_LATER), browser_page, grant)
    opened = receipt["opened_conversation_gate"]
    assert opened["proceeded"] is True, opened["why"]
    assert opened["observed"]["composer_appeared"] is True
    assert opened["observed"]["composer_waited_ms"] >= 300
    assert receipt["performed"] is True


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
    # THE ONE CLICK WAS THE MESSAGE PRESS, AND IT IS NOT A SUBMIT: the words
    # were typed and Send was never pressed, so they are still on his screen.
    assert receipt["clicked"]["opener_clicks"] == 1
    assert receipt["typed_text"]["text_was_entered"] is True
    assert receipt["typed_text"]["submit_was_pressed"] is False
    assert receipt["typed_text"]["left_in_the_composer"] is True
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
