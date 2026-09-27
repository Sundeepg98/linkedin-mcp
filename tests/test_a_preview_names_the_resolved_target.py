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

LIMITS: the headline half of "name and headline" is empty on both surfaces --
neither the invitation rail's control nor the conversation header draws one
in the measured markup. A group conversation's title comes back in a person
record, as the messaging overview's does.
"""

from __future__ import annotations

import json
import logging

import pytest

from linkedin_server import dom, people_data, threads, writes
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
from tests.test_writes_nine import MEMBER, _grantable_invitation, _preview_the_refusal

#: What the reply fixture's conversation header draws.
_TITLE = "Kai Example"


def _is_a_person_record(value) -> bool:
    return isinstance(people_data.as_record(value), people_data.Person)


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


async def test_the_reply_preview_names_the_conversation_in_a_record(writes_on, browser_page):
    block, _nav_used = await _preview(browser_page)
    named = block.get("who_this_would_reach")
    assert _is_a_person_record(named), named
    assert named["name"] == _TITLE
    check = block.get("who_this_would_reach_check", "")
    assert "CHECK IT" in check and _TITLE not in check, check


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
    caplog.set_level(logging.DEBUG)
    _grantable_invitation(monkeypatch)
    block, _nav_used = await _preview_the_refusal(browser_page, "send_invitation")
    assert block.get("to_confirm"), "no grant was minted, so nothing could keep the name"
    label = "Invite " + MEMBER + dom.INVITE_CONTROL_SUFFIX
    assert carried(label, records=caplog.records) == []
    # His own word is the target the caller supplied, and it is kept: that is
    # the receipt half of the ruling, not a leak.
    grant = writes._GRANTS[block["to_confirm"]]
    assert grant.target == MEMBER


async def test_nothing_a_sent_reply_keeps_carries_the_title(writes_on, browser_page, caplog):
    """Preview, redeem and FIRE: after the send, the retained state, the
    receipt and every log record carry no title -- and the grant's target is
    the thread id and the words he supplied."""
    caplog.set_level(logging.DEBUG)
    block, _nav_used = await _preview(browser_page)
    assert _TITLE in json.dumps(block["who_this_would_reach"]), "the preview did not name it"
    grant = consume(block["to_confirm"], action=_ACTION, target=TARGET)
    receipt = await writes.perform(_nav(DISPATCHING, AFTER), browser_page, grant)
    assert receipt["performed"] is True, receipt
    assert carried(_TITLE, receipts=[receipt], records=caplog.records) == []
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
