"""The people seam, adopted -- and mitigation 2 held on every name lane L5 returns.

RULING ``PEOPLE-DATA-MITIGATIONS``, item 2: every third party's string a tool
returns is SANITISED (Unicode-normalised; control, zero-width and
bidirectional characters removed; whitespace collapsed; length-capped) and
MARKED as untrusted third-party text. Lane G built the one sanitiser and
record, ``linkedin_server/people_data.py``; lane L5 routed its four
name-bearing outputs through ``linkedin_server/people_seam.py`` so the
adoption would be a body swap.

THE SWAP HAPPENED AT LANE L5'S MERGE OF MASTER 52b55b6 (2026-09-27), and this
file changed with it:

* ``people_seam.person`` now builds a ``people_data.Person`` and returns its
  envelope. It is the ONE builder every write PREVIEW that names a person goes
  through: the named acts' ``whom_this_resolves_to``, ``linkedin_send_reply``'s
  ``who_this_would_reach``, and -- since the merge, when the orchestrator's
  order found it building a record of its own -- ``linkedin_send_invitation``'s
  ``who_this_would_reach``. Section 2 shows each preview's record IS the seam's
  output.
* Lane G wired the two READERS -- ``linkedin_list_conversations`` and
  ``linkedin_open_messaging`` -- to ``people_data`` directly, so the seam's
  ``name`` half lost its callers and went. They are still two of the four
  outputs section 3 holds to mitigation 2.
* THE TWELVE MITIGATION-2 TESTS -- three properties, four outputs -- were
  ``xfail(strict=True)`` on lane L5's branch, waiting for this merge. They
  pass now and the marker is gone, so a regression is a plain failure. Each
  plants a name carrying a zero-width space and a right-to-left override and
  (where the reader does not already cut it) more text than the cap, and holds
  one property of what the output RETURNS: nothing invisible survives, the cap
  holds, the untrusted marker rides on the record itself. The reply's output
  was a plain SENTENCE until lane G made it a record; the marker is asserted
  on the record, not anywhere in the block.

NOTHING HERE REACHES LINKEDIN.
"""
from __future__ import annotations

import unicodedata

import pytest

from linkedin_server import people_data, people_seam, shape, threads
from linkedin_server.people_data import UNTRUSTED_KEY, UNTRUSTED_NOTE
from linkedin_server.writes import preview, spec_for_action
from tests import test_send_reply as reply
from tests.test_messaging_threads import COMPOSE_LIST, THREAD, _derive
from tests.test_named_profile_route import LINK, PROFILE, _Navigator
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures
from tests.test_writes_nine import MEMBER, _preview_the_refusal

NAME_CAP = people_data.CAPS["name"]
HEADLINE_CAP = people_data.CAPS["headline"]

ZERO_WIDTH = chr(0x200B)
RIGHT_TO_LEFT_OVERRIDE = chr(0x202E)
#: A planted name: a zero-width space, a direction override, and (for the
#: readers that do not already cut) a tail that runs past the cap.
PLANTED = "Kai" + ZERO_WIDTH + " Ex" + RIGHT_TO_LEFT_OVERRIDE + "ample"
LONG_TAIL = " Longname" * 16
PLANTED_HEADLINE = "Planted headline " + "padding " * 28


def _invisible(text: str) -> list[str]:
    return [c for c in text if unicodedata.category(c) in ("Cc", "Cf")]


def _is_a_person_record(value) -> bool:
    return isinstance(people_data.as_record(value), people_data.Person)


def _marked(record) -> bool:
    """THE MARKER ON THE RECORD ITSELF, with its exact note -- a marker found
    anywhere else in a block would not say which words it is about."""
    return isinstance(record, dict) and record.get(UNTRUSTED_KEY) == UNTRUSTED_NOTE


# ---------------------------------------------------------------------------
# 1. The seam itself
# ---------------------------------------------------------------------------


def test_the_seam_returns_lane_gs_record_exactly():
    """The swap, pinned: exactly ``people_data.PERSON_SHAPE``, sanitised,
    carrying the marker's exact note -- and re-validated as a record."""
    record = people_seam.person(
        name="  Casey   Example ", headline="A headline", href=LINK, degree="1st"
    )
    assert record == {
        "name": "Casey Example",
        "headline": "A headline",
        "link": LINK,
        "degree": "1st",
        UNTRUSTED_KEY: UNTRUSTED_NOTE,
    }
    assert frozenset(record) == people_data.PERSON_SHAPE
    assert _is_a_person_record(record)
    assert people_seam.person(name="   ") is None
    assert people_seam.person(name="Casey Example", degree="4th")["degree"] is None


@pytest.mark.parametrize("headline", [None, "", "   ", ZERO_WIDTH + RIGHT_TO_LEFT_OVERRIDE])
def test_a_headline_with_nothing_to_show_is_absent_never_empty(headline):
    """PREVIEW-NAMES-THE-RESOLVED-TARGET as the orchestrator applied it to the
    previews: a headline the page does not draw -- or that sanitises to
    nothing -- is ``None``, never ``""``. And the record still validates."""
    record = people_seam.person(name="Casey Example", headline=headline)
    assert record["headline"] is None, record
    assert _is_a_person_record(record)


def test_the_seam_holds_mitigation_2_on_its_own_input():
    record = people_seam.person(name=PLANTED + LONG_TAIL, headline=PLANTED_HEADLINE)
    assert _invisible(record["name"]) == [] and _invisible(record["headline"]) == []
    assert len(record["name"]) <= NAME_CAP and len(record["headline"]) <= HEADLINE_CAP
    assert _marked(record)


# ---------------------------------------------------------------------------
# 2. ROUTING: each preview's record IS the seam's output
# ---------------------------------------------------------------------------


def _marker(prefix: str):
    def _mark(**fields):
        return {"marked_by": prefix, "name": fields.get("name")}

    return _mark


async def test_the_named_acts_identity_comes_out_of_the_seam(writes_on, browser_page, monkeypatch):
    monkeypatch.setattr(people_seam, "person", _marker("SEAM"))
    block = await preview(
        spec_for_action("connect_from_profile"),
        target=LINK,
        navigator=_Navigator(PROFILE),
        page=browser_page,
    )
    assert block["whom_this_resolves_to"] == {"marked_by": "SEAM", "name": "Casey Example"}


async def _reply_block(page, world: str = THREAD) -> dict:
    return await preview(
        spec_for_action("send_reply"), target=reply.TARGET, navigator=reply._nav(world), page=page
    )


async def test_the_reply_recipient_comes_out_of_the_seam(writes_on, browser_page, monkeypatch):
    """Before the seam, a send_reply preview made ZERO seam calls and printed
    the conversation's title unmarked (the cold re-check of 2026-09-27)."""
    calls = []

    def _mark(**fields):
        calls.append(fields)
        return {"marked_by": "SEAM", "name": fields.get("name")}

    monkeypatch.setattr(people_seam, "person", _mark)
    block = await _reply_block(browser_page)
    assert calls == [{"name": "Kai Example"}], calls
    assert block["who_this_would_reach"] == {"marked_by": "SEAM", "name": "Kai Example"}


async def test_the_invitation_recipient_comes_out_of_the_seam(writes_on, browser_page, monkeypatch):
    """THE ORCHESTRATOR'S ORDER OF 2026-09-27: ``linkedin_send_invitation``'s
    recipient label bypassed the seam -- lane G's foundation built its record
    in ``writes._name_the_invitation_recipient`` -- so one preview answered to
    a rule the other three did not share. Routed at lane L5's merge."""
    monkeypatch.setattr(people_seam, "person", _marker("SEAM"))
    block, _nav = await _preview_the_refusal(browser_page, "send_invitation")
    assert block["who_this_would_reach"] == {"marked_by": "SEAM", "name": MEMBER}


async def test_the_invitation_recipient_is_the_seams_record_unpatched(writes_on, browser_page):
    """And unpatched, it is exactly the record the seam builds for that name
    -- no field the seam would not set, the headline ABSENT."""
    block, _nav = await _preview_the_refusal(browser_page, "send_invitation")
    assert block["who_this_would_reach"] == people_seam.person(name=MEMBER)
    assert block["who_this_would_reach"]["headline"] is None


# ---------------------------------------------------------------------------
# 3. MITIGATION 2, per output -- twelve tests, three properties by four
# ---------------------------------------------------------------------------

#: The conversation list with row 1's participant planted.
PLANTED_LIST = _derive(
    COMPOSE_LIST,
    "<div><span>Kai Example</span></div></h3>",
    "<div><span>Kai&#8203; Ex&#8238;ample" + LONG_TAIL + "</span></div></h3>",
)


async def _list_result(page) -> dict:
    await page.set_content(PLANTED_LIST, wait_until="domcontentloaded", timeout=60_000)
    reading = await threads.read_conversation_list(page, include_names=True)
    return threads.list_result(reading, threads.COMPOSE_URL, include_names=True)


def _planted_row_record(result: dict) -> dict:
    """The planted row's ``with`` -- the people record lane G returns."""
    records = [
        row.get("with")
        for row in result["rows"]
        if "Kai" in str((row.get("with") or {}).get("name") or (row.get("with") or {}).get("title"))
    ]
    assert len(records) == 1, records
    return records[0]


def _text_of(record: dict) -> str:
    return str(record.get("name") if "name" in record else record.get("title"))


async def test_the_list_plant_reaches_the_row(browser_page):
    """THE CONTROL for the three below: the planted row is read, and its
    letters come back -- so a failure there is a missing property of the
    name, never a plant that did not arrive."""
    text = _text_of(_planted_row_record(await _list_result(browser_page)))
    assert "Kai" in text and "ample" in text and "Longname" in text


async def test_list_conversations_strips_invisible_characters(browser_page):
    assert _invisible(_text_of(_planted_row_record(await _list_result(browser_page)))) == []


async def test_list_conversations_caps_a_name(browser_page):
    assert len(_text_of(_planted_row_record(await _list_result(browser_page)))) <= NAME_CAP


async def test_list_conversations_marks_names_untrusted(browser_page):
    assert _marked(_planted_row_record(await _list_result(browser_page)))


def _overview_record() -> dict:
    html = (
        '<div aria-label="Select conversation with ' + PLANTED + LONG_TAIL + '"></div>'
        '<div aria-label="Select conversation with Ivo Placeholder"></div>'
    )
    out = shape.messaging_overview(html, "https://www.linkedin.com/messaging/", include_names=True)
    return out["rows"][0]["with"]


def test_the_overview_plant_reaches_the_row():
    """THE CONTROL for the three below (see the list's)."""
    name = _overview_record()["name"]
    assert "Kai" in name and "ample" in name and "Longname" in name


def test_open_messaging_strips_invisible_characters():
    assert _invisible(_overview_record()["name"]) == []


def test_open_messaging_caps_a_name():
    assert len(_overview_record()["name"]) <= NAME_CAP


def test_open_messaging_marks_names_untrusted():
    assert _marked(_overview_record())


#: The named profile with its owner planted: the title, the topcard's
#: heading and the owner's Connect carry the planted name (so the page still
#: names one person consistently), and the headline runs past the cap. The
#: topcard parser already cuts a NAME at 120, so for this output the cap is
#: tested on the headline.
_ENTITY_NAME = "Kai&#8203; Ex&#8238;ample"
PLANTED_PROFILE = _derive(
    _derive(
        _derive(
            _derive(
                PROFILE,
                "<title>Casey Example | LinkedIn</title>",
                "<title>" + _ENTITY_NAME + " | LinkedIn</title>",
            ),
            "<h2>Casey Example</h2>",
            "<h2>" + _ENTITY_NAME + "</h2>",
        ),
        'aria-label="Invite Casey Example to connect" id="topcard-connect"',
        'aria-label="Invite ' + _ENTITY_NAME + ' to connect" id="topcard-connect"',
    ),
    "<p>Invented headline for a synthetic person</p>",
    "<p>" + PLANTED_HEADLINE + "</p>",
)


async def _whom(page) -> dict:
    block = await preview(
        spec_for_action("connect_from_profile"),
        target=LINK,
        navigator=_Navigator(PLANTED_PROFILE),
        page=page,
    )
    whom = block["whom_this_resolves_to"]
    assert whom is not None, block.get("whom_this_resolves_to_why")
    return whom


async def test_the_named_profile_plant_reaches_the_block(writes_on, browser_page):
    """THE CONTROL for the three below (see the list's)."""
    whom = await _whom(browser_page)
    assert "Kai" in whom["name"] and "ample" in whom["name"]
    assert whom["headline"].startswith("Planted headline")


async def test_the_named_act_strips_invisible_characters(writes_on, browser_page):
    assert _invisible((await _whom(browser_page))["name"]) == []


async def test_the_named_act_caps_a_headline(writes_on, browser_page):
    assert len((await _whom(browser_page))["headline"]) <= HEADLINE_CAP


async def test_the_named_act_marks_the_identity_untrusted(writes_on, browser_page):
    assert _marked(await _whom(browser_page))


#: The reply's conversation with its title planted.
PLANTED_THREAD = _derive(
    THREAD,
    '<span class="msg-entity-lockup__entity-title">Kai Example</span>',
    '<span class="msg-entity-lockup__entity-title">Kai&#8203; Ex&#8238;ample'
    + LONG_TAIL
    + "</span>",
)


async def _reached(page) -> dict:
    block = await _reply_block(page, PLANTED_THREAD)
    record = block.get("who_this_would_reach")
    assert isinstance(record, dict), block.get("who_this_would_reach_check")
    return record


async def test_the_reply_plant_reaches_the_record(writes_on, browser_page):
    """THE CONTROL for the three below (see the list's)."""
    name = (await _reached(browser_page))["name"]
    assert "Kai" in name and "ample" in name and "Longname" in name


async def test_send_reply_strips_invisible_characters(writes_on, browser_page):
    assert _invisible((await _reached(browser_page))["name"]) == []


async def test_send_reply_caps_a_name(writes_on, browser_page):
    assert len((await _reached(browser_page))["name"]) <= NAME_CAP


async def test_send_reply_marks_the_name_untrusted(writes_on, browser_page):
    """THE MARKER ON WHAT WAS A PLAIN-STRING OUTPUT: this preview printed the
    title inside a sentence until lane G made it a record."""
    assert _marked(await _reached(browser_page))
