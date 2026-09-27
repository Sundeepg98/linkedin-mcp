"""``focused`` and ``other`` are not values ``linkedin_open_messaging`` accepts.

THE ORDER (orchestrator, 2026-09-27 23:36, lane L5, item 2): the tool still
accepted ``message_filter="focused"`` and ``"other"`` although lane G's bar
scoping refuses both -- on the measured page they are the FOLDER dropdown's
choices, beside the filter bar, not pills (lane G's record, R.2). Two accepted
values that could never be activated, and asking for one cost the tool's two
page loads -- the composer's list, then ``/messaging/``, which opens a
conversation of LinkedIn's choosing -- before the activator said no.

WHAT THIS FILE HOLDS:

1. ``dom.MESSAGING_FILTERS`` is the five pills, and neither folder choice.
2. The tool's REGISTERED schema offers exactly those five and the empty
   default, as an enum a client reads before it calls -- read off
   ``mcp.list_tools()``, the surface a client sees, and held equal to
   ``dom.MESSAGING_FILTERS`` so the two cannot drift apart.
3. A direct call with either folder choice is refused BEFORE ANY PAGE IS
   LOADED: the browser session is never entered.
4. The activator itself refuses both before any locator exists.

NOTHING HERE REACHES LINKEDIN.
"""
from __future__ import annotations

import asyncio

import pytest

from linkedin_server import dom, server

FOLDER_CHOICES = ("focused", "other")
PILLS = ("unread", "jobs", "connections", "inmail", "starred")


def _schema_values() -> list[str]:
    async def read():
        tools = {tool.name: tool for tool in await server.mcp.list_tools()}
        return tools["linkedin_open_messaging"].parameters["properties"]["message_filter"]

    prop = asyncio.run(read())
    assert "enum" in prop, "message_filter is not an enum in the registered schema: %r" % prop
    return list(prop["enum"])


def test_the_permitted_set_is_the_five_pills_and_no_folder_choice():
    assert dom.MESSAGING_FILTERS == PILLS
    for choice in FOLDER_CHOICES:
        assert choice not in dom.MESSAGING_FILTERS, choice


def test_the_schema_offers_the_five_pills_and_the_default_and_nothing_else():
    values = _schema_values()
    assert values == [""] + list(PILLS), values
    # HELD EQUAL TO THE CLOSED SET, so the schema a client reads and the check
    # the activator makes are one list, not two that can drift.
    assert [v for v in values if v] == list(dom.MESSAGING_FILTERS)
    for choice in FOLDER_CHOICES:
        assert choice not in values, choice


def test_the_description_no_longer_offers_the_folder_choices():
    async def read():
        tools = {tool.name: tool for tool in await server.mcp.list_tools()}
        return tools["linkedin_open_messaging"]

    tool = asyncio.run(read())
    prop = tool.parameters["properties"]["message_filter"]
    description = " ".join(str(prop.get("description") or "").split()).lower()
    assert "focused" not in description and "other," not in description, description


class _NoSession:
    """A browser whose session must never be entered."""

    def __init__(self):
        self.entered = 0

    def session(self):
        outer = self

        class _S:
            async def __aenter__(self):
                outer.entered += 1
                raise AssertionError("a page was opened for a value that is not a filter")

            async def __aexit__(self, *exc):
                return False

        return _S()

    async def goto(self, page, url):  # pragma: no cover - never reached
        raise AssertionError("navigated for a value that is not a filter")


@pytest.mark.parametrize("choice", FOLDER_CHOICES)
async def test_a_folder_choice_is_refused_before_any_page_loads(monkeypatch, choice):
    fake = _NoSession()
    monkeypatch.setattr(server, "BROWSER", fake)
    result = await server.linkedin_open_messaging(message_filter=choice)
    assert fake.entered == 0, "the browser session was entered"
    assert "error" in result or "message" in result, result
    assert "is not a messaging filter" in str(result), result


async def test_a_pill_is_still_accepted_past_the_value_check(monkeypatch):
    """THE CONTROL: a pill passes the early check and reaches the browser -- so
    the refusal above is about the value, not a tool that refuses everything."""
    fake = _NoSession()
    monkeypatch.setattr(server, "BROWSER", fake)
    result = await server.linkedin_open_messaging(message_filter="inmail")
    assert fake.entered == 1, result


class _RecordingPage:
    """A page whose every locator request is recorded."""

    url = "https://www.linkedin.com/messaging/"

    def __init__(self):
        self.asked = []

    def locator(self, selector):
        self.asked.append(selector)
        raise AssertionError("a locator was built for a value that is not a filter")


@pytest.mark.parametrize("choice", FOLDER_CHOICES)
async def test_the_activator_refuses_a_folder_choice_before_any_locator(choice):
    page = _RecordingPage()
    with pytest.raises(ValueError, match="is not a messaging filter"):
        await dom.activate_messaging_filter(page, choice)
    assert page.asked == []
