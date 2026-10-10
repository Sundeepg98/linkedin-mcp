"""A followed Page's name leaves the unfollow read only inside a declared record.

THE RULING (the orchestrator, 2026-10-10 14:56 IST, to lane G2): page strings
leave only through a declared record. ``writes._read_followed_state`` read the
name LinkedIn writes into the row's own button -- "Click to stop following
<Page>" -- and returned it verbatim in its facts (``company``), which the
preview prints as the field he checks and the receipt repeats, and quoted it
in its sentence. The reader guard found that success path on 2026-10-10, when
the old clean stopped counting.

NOW the name travels as a ``people_data.Organisation`` record -- sanitised,
bounded, marked as untrusted third-party text, its link the Page's numeric
address (a slug can be a name, so none is kept) -- and the sentence says the
Page is in the list without naming it.

Every page here is a stand-in for the two reads the function makes; nothing
reaches LinkedIn or a browser. The Page's name is the harness plant, which no
real Page carries.
"""
from __future__ import annotations

import asyncio
import json

from linkedin_server import dom, people_data, writes
from tests.plantedpage import PLANT, carries_the_plant_outside_records

#: The row the Manage Pages list draws for the Page he names, as
#: ``dom.harvest_followed_pages`` returns it: its button's accessible name and
#: its company link. Its id and the other Page's are members of the identity
#: sweep's invented ids (``SYNTHETIC_IDS``, the 530000xx series of invented
#: organisations), which its company-id shape passes on sight.
COMPANY_ID = "53000011"
ROW = {"label": "Click to stop following " + PLANT, "href": "/company/" + COMPANY_ID + "/"}


def _read(monkeypatch, rows, target=COMPANY_ID):
    async def harvest(page, *args, **kwargs):
        return list(rows)

    async def main_text(page, *args, **kwargs):
        return ""

    monkeypatch.setattr(dom, "harvest_followed_pages", harvest)
    monkeypatch.setattr(dom, "read_main_text", main_text)
    return asyncio.run(writes._read_followed_state(object(), target))


def test_the_pages_name_comes_back_only_inside_an_organisation_record(monkeypatch):
    facts, state, why = _read(monkeypatch, [ROW])
    assert state == "following", (state, why)
    outside, records = carries_the_plant_outside_records({"facts": facts, "state": state, "why": why})
    assert outside == [], ("the Page's name left outside a record", outside, json.dumps(facts))
    assert records == 1
    record = people_data.as_record(facts["company"])
    assert isinstance(record, people_data.Organisation), facts["company"]
    assert record.link == "https://www.linkedin.com/company/" + COMPANY_ID + "/"
    assert facts["company_id"] == COMPANY_ID


def test_no_match_is_no_record_and_the_sentence_names_only_his_own_target(monkeypatch):
    other = {"label": "Click to stop following Another Example Page", "href": "/company/53000012/"}
    facts, state, why = _read(monkeypatch, [other])
    assert state != "following"
    assert facts["company"] is None
    assert "Another Example Page" not in json.dumps([facts, why])
