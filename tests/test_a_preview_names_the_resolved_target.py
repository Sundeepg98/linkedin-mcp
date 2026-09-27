"""PREVIEW-NAMES-THE-RESOLVED-TARGET, encoded: a preview names whom the tool
resolved inside a people record; nothing a write retains carries that name.

THE RULING (orchestrator, 2026-09-27, applying NAMES-AT-RUNTIME;
``_audit/2026-09-27-rulings-previews-and-receipts.md``): "A PREVIEW NAMES WHOM
THE TOOL RESOLVED, AND A PREVIEW IS NOT A RECEIPT." The preview shows the
member the tool resolved -- the name and headline read off the page,
sanitised, marked as another member's words, and carried inside a people
record -- returned at runtime and never written. A receipt, anything that
persists after a write fires, carries only the target the caller supplied.

THE TWO PREVIEWS THAT NAME A THIRD PARTY, each driven through the real gate
over fixture pages in a real headless Chromium:

* ``send_invitation`` -- the label of the ONE invitation control his word
  selected, ``Invite <name> to connect``; the record holds the name.
* ``send_reply`` -- the title of the ONE conversation he named by id.

WHAT "PERSISTS" MEANS IN THIS PACKAGE, measured rather than assumed: a write
writes NOTHING to disk -- a grant is "held in memory only and never written
to disk" (``writes.WriteGrant``). What outlives a call is the grant store
(``writes._GRANTS``, with each grant's target, retained preview and
observation), the observation store (``writes._OBSERVED``), and the log
records a call emits, which the host process may write wherever it keeps a
server's stderr. Each is checked here, after the preview and, for the reply,
after the write fires -- and each check is shown convicting a planted
regression, so none can pass by looking at nothing.

THE RECORD OF THE RIGHT KIND (orchestrator, 2026-09-27 19:52): the headline
is read where the page draws one, and where it does not the record says
ABSENT (``people_data.ABSENT``, null) -- a different state from an empty
string. A conversation with one other member names a person, with the line
its header draws under the title (measured present on the one captured
header; that it is the headline is derived); a GROUP conversation, or one
whose row the page does not draw, comes back as the conversation's title
record. The invitation's reading is one control's label, which draws no
headline: ABSENT, and section 1 says so. Until that evening both previews
carried a person record with an empty headline, whoever they named.
"""

from __future__ import annotations

import json
import logging

import pytest

from linkedin_server import dom, people_data, threads, writes
from linkedin_server.config import logger as package_logger
from linkedin_server.writes import consume
from tests.test_send_reply import (
    AFTER,
    DISPATCHING,
    TARGET,
    THREAD,
    _ACTION,
    _nav,
    _preview,
)
from tests.test_messaging_threads import _derive
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures
from tests.test_writes_nine import (
    MEMBER,
    MEMBER_LINK,
    _grantable_invitation,
    _preview_the_refusal,
)

#: What the reply fixture's conversation header draws: the title, and the line
#: under it.
_TITLE = "Kai Example"
_HEADLINE = "Invented headline"
_HEADLINE_LINE = (
    '<dd class="msg-entity-lockup__entity-info t-12 t-black--light t-normal">'
    + _HEADLINE + "</dd>"
)
#: The open conversation's row link, as the fixture draws it: active.
_ACTIVE_LINK = 'msg-conversations-container__convo-item-link--active">'
#: The list reader's group marker, as the composer capture draws it.
_GROUP_FACEPILE = (
    '<div class="msg-facepile-grid msg-facepile-grid--4"><img class="msg-facepile-grid__img '
    'msg-facepile-grid__img--multiple-participants" alt=""></div>'
)


def _is_a_person_record(value) -> bool:
    return isinstance(people_data.as_record(value), people_data.Person)


def _is_a_title_record(value) -> bool:
    return isinstance(people_data.as_record(value), (people_data.Group, people_data.Event))


def retained_state() -> str:
    """Everything the write path keeps after a call returns, as one text: the
    grant store (targets, retained previews, observations) and the observation
    store. repr, so a field the check does not know about is still read."""
    return repr(list(writes._GRANTS.values())) + repr(list(writes._OBSERVED.values()))


def carried(name: str, *, receipts=(), records=()) -> list[str]:
    """Where a page-read name persists: the retained state, a receipt, or a
    log record. Never the name -- the place."""
    places = []
    if name in retained_state():
        places.append("retained write state")
    for receipt in receipts:
        if name in json.dumps(receipt, default=repr):
            places.append("a receipt")
    for record in records:
        if name in record.getMessage():
            places.append("a log record")
    return places


#: Emitted on the package logger when each capture below is set, and required
#: back out of it: the per-test proof that "a log record" above is read off a
#: channel this package can reach.
_CHANNEL_CONTROL = "caplog control: the package logger is heard at DEBUG"


def set_root_and_package_to_debug(caplog) -> None:
    """``caplog`` at DEBUG on the ROOT logger AND on the package's own logger.

    THE ROOT CALL ALONE NEVER HEARD A DEBUG RECORD FROM THIS PACKAGE.
    ``config.py`` gives the ``linkedin`` logger a level of its own (INFO unless
    ``LINKEDIN_LOG_LEVEL`` says otherwise) and ``propagate = False``. The
    handler does reach it -- pytest attaches caplog's handler to every
    non-propagating logger, and ``tests/conftest.py`` attaches it by name --
    but ``caplog.set_level(logging.DEBUG)`` lowers only the root, and a logger
    with a level of its own does not inherit the root's. Every
    ``logger.debug(...)`` in the package was dropped before capture, so
    ``carried(..., records=caplog.records)`` passed on a DEBUG line that
    printed the name: measured 2026-09-28 with a planted record (lane G,
    item 4). The root call stays for ``threads.py``, which logs through
    ``getLogger(__name__)`` -- its records reach the root, never ``linkedin``.
    """
    caplog.set_level(logging.DEBUG)
    caplog.set_level(logging.DEBUG, logger=package_logger.name)
    package_logger.debug(_CHANNEL_CONTROL)
    assert _CHANNEL_CONTROL in caplog.text, (
        "caplog cannot hear the package logger at DEBUG: 'no log record "
        "carries the name' would pass on a line that printed it"
    )


# ---------------------------------------------------------------------------
# 1. The preview names whom it resolved, inside a people record
# ---------------------------------------------------------------------------


async def test_the_invitation_preview_names_the_person_in_a_record(writes_on, browser_page):
    block, _nav_used = await _preview_the_refusal(browser_page, "send_invitation")
    named = block.get("who_this_would_reach")
    assert _is_a_person_record(named), named
    assert named["name"] == MEMBER, "the record holds the NAME, not the control's label"
    assert named[people_data.UNTRUSTED_KEY] == people_data.UNTRUSTED_NOTE
    # The instruction to CHECK it travels beside the record, as prose that
    # carries no page text.
    check = block.get("who_this_would_reach_check", "")
    assert "CHECK IT" in check and MEMBER not in check, check


async def test_the_invitation_record_says_its_headline_is_absent(writes_on, browser_page):
    """WHAT IS READ HERE IS ONE CONTROL'S LABEL, and it draws a name and no
    headline: the record says ABSENT -- null, not the empty string it carried
    until 2026-09-27. The rail's card around the control has never been
    captured, so no reader here knows where a headline would be, and none is
    guessed at."""
    block, _nav_used = await _preview_the_refusal(browser_page, "send_invitation")
    named = block["who_this_would_reach"]
    assert named["headline"] is people_data.ABSENT, named
    assert named["headline"] != "", "ABSENT is not the empty string"


async def test_the_reply_preview_names_the_person_with_the_headline_drawn(
    writes_on, browser_page
):
    """ONE OTHER MEMBER: the row is drawn active with no group marker, so the
    record is a person -- the title, and the line the header draws under it."""
    block, _nav_used = await _preview(browser_page)
    named = block.get("who_this_would_reach")
    assert _is_a_person_record(named), named
    assert named["name"] == _TITLE
    assert named["headline"] == _HEADLINE, named
    check = block.get("who_this_would_reach_check", "")
    assert "CHECK IT" in check and _TITLE not in check and _HEADLINE not in check, check


async def test_a_header_with_no_line_under_the_title_says_absent(writes_on, browser_page):
    world = _derive(THREAD, _HEADLINE_LINE, "")
    block, _nav_used = await _preview(browser_page, world)
    named = block["who_this_would_reach"]
    assert _is_a_person_record(named), named
    assert named["headline"] is people_data.ABSENT, named


async def test_an_empty_line_under_the_title_is_empty_not_absent(writes_on, browser_page):
    """THE OTHER SIDE OF THE DISTINCTION: a line drawn with nothing in it is
    the empty string -- drawn, and empty -- never ABSENT."""
    world = _derive(THREAD, _HEADLINE_LINE, _HEADLINE_LINE.replace(_HEADLINE, ""))
    block, _nav_used = await _preview(browser_page, world)
    assert block["who_this_would_reach"]["headline"] == "", block["who_this_would_reach"]


async def test_a_group_conversation_comes_back_as_a_title_record(writes_on, browser_page):
    """A GROUP CONVERSATION NAMES NO ONE PERSON: its row carries the group
    marker, so the preview returns the conversation's title record -- the
    record the list returns for a group row -- and not a person."""
    world = _derive(THREAD, _ACTIVE_LINK, _ACTIVE_LINK + _GROUP_FACEPILE)
    block, _nav_used = await _preview(browser_page, world)
    named = block["who_this_would_reach"]
    assert _is_a_title_record(named), named
    assert not _is_a_person_record(named), named
    assert named["title"] == _TITLE, named
    assert named == threads.conversation_with(_TITLE, group=True), named
    assert "GROUP" in block["who_this_would_reach_check"]


async def test_a_conversation_whose_row_is_not_drawn_names_no_person(writes_on, browser_page):
    """Nothing says whether it is one member or several, so it is not dressed
    up as a person: the title record."""
    world = _derive(THREAD, " " + _ACTIVE_LINK, '">')
    block, _nav_used = await _preview(browser_page, world)
    named = block["who_this_would_reach"]
    assert _is_a_title_record(named), named
    assert named["title"] == _TITLE, named


async def test_a_header_drawing_two_lines_under_the_title_names_nobody(writes_on, browser_page):
    world = _derive(THREAD, _HEADLINE_LINE, _HEADLINE_LINE + _HEADLINE_LINE)
    block, _nav_used = await _preview(browser_page, world)
    assert "who_this_would_reach" not in block, block
    assert "cannot tell you who" in block["who_this_would_reach_check"]


async def test_the_reply_preview_sanitises_the_title_it_names(writes_on, browser_page):
    """A title laced with a zero-width space and a direction override comes
    back without either -- the record is built by people_data, not copied."""
    laced = _TITLE.replace(" ", chr(0x200B) + " ") + chr(0x202E)
    header = '<span class="msg-entity-lockup__entity-title">'
    world = _derive(THREAD, header + _TITLE + "<", header + laced + "<")
    block, _nav_used = await _preview(browser_page, world)
    named = block["who_this_would_reach"]
    assert _is_a_person_record(named), named
    assert named["name"] == _TITLE, named


# ---------------------------------------------------------------------------
# 2. Nothing a write keeps carries the name
# ---------------------------------------------------------------------------


async def test_nothing_the_invitation_preview_keeps_carries_the_name(
    writes_on, browser_page, monkeypatch, caplog
):
    """Driven through a spec made grantable, so a grant EXISTS to keep the
    name (``_grantable_invitation``: in production this action mints none,
    and the check would pass on an absence)."""
    set_root_and_package_to_debug(caplog)
    _grantable_invitation(monkeypatch)
    block, _nav_used = await _preview_the_refusal(browser_page, "send_invitation")
    assert block.get("to_confirm"), "no grant was minted, so nothing could keep the name"
    label = "Invite " + MEMBER + dom.INVITE_CONTROL_SUFFIX
    assert carried(label, records=caplog.records) == []
    # His LINK is the target the caller supplied, and it is kept: that is the
    # receipt half of the ruling, not a leak. (It was his own WORD for the
    # person until 2026-09-27, when the invitation stopped being aimed by a
    # name -- lane L5, the orchestrator's order of 23:36.)
    grant = writes._GRANTS[block["to_confirm"]]
    assert grant.target == MEMBER_LINK


async def test_nothing_a_sent_reply_keeps_carries_the_title(writes_on, browser_page, caplog):
    """Preview, redeem and FIRE: after the send, the retained state, the
    receipt and every log record carry no title -- and the grant's target is
    the thread id and the words he supplied."""
    set_root_and_package_to_debug(caplog)
    block, _nav_used = await _preview(browser_page)
    assert _TITLE in json.dumps(block["who_this_would_reach"]), "the preview did not name it"
    grant = consume(block["to_confirm"], action=_ACTION, target=TARGET)
    receipt = await writes.perform(_nav(DISPATCHING, AFTER), browser_page, grant)
    assert receipt["performed"] is True, receipt
    assert carried(_TITLE, receipts=[receipt], records=caplog.records) == []
    assert carried(_HEADLINE, receipts=[receipt], records=caplog.records) == []
    assert _TITLE not in repr(grant), "the fired grant kept the title"
    assert TARGET["thread"] in grant.target and TARGET["text"] in grant.target


async def test_the_retained_state_check_convicts_a_name_that_reached_a_grant(
    writes_on, browser_page
):
    """THE CONTROL: the same check, on a planted regression -- the named block
    assigned to the grant it was built beside. It must convict."""
    block, _nav_used = await _preview(browser_page)
    writes._GRANTS[block["to_confirm"]].preview = dict(block)
    assert carried(_TITLE) == ["retained write state"]


def test_the_receipt_and_log_checks_convict_a_planted_name():
    class _Record:
        def getMessage(self) -> str:
            return "sent to " + _TITLE

    assert carried(_TITLE, receipts=[{"sent_to": _TITLE}], records=[_Record()]) == [
        "a receipt", "a log record",
    ]
