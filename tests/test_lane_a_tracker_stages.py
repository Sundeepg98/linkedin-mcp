"""His job tracker's three further stages: interview, archived, clicked_apply.

Lane A, 2026-10-10 -- census ``J 50``, ``J 51``, ``J 52``. Record:
``_audit/2026-09-28-lane-a-admissions.md``, section 4.2.

THE READER IS THE TRACKER'S OWN, AIMED AT REAL CAPTURED MARKUP.
``server._read_tracker`` already reads ``/jobs-tracker/?stage=<token>`` for
three stages; the tracked live skeletons ``tests/fixtures/jobs_tracker_row.html``
and ``jobs_tracker_empty.html`` are captures of that page, and
``tests/test_sdui_surfaces_fixture.py`` already reads off them that the strip
draws "Interview <dot> 0" and an "Archived" tab WITHOUT a count. This file
pins the tool that hands the same reader the three further tokens, each of
which the read boundary admits by its own anchored line (lane A).

What a capture has not shown, and so is not claimed: that the three stages
render the same row component the captured stages do (the tracker's tabs are
one list redrawn per stage, which is why the reader is reused, but no capture
of these three exists), and that ``clicked_apply`` renders a list at all -- its
tab is drawn on neither capture. ``_audit/_census/capture-queue-reads.tsv``,
surface ``tracker-stages``, is the capture that settles both.

Every card below is synthetic and names nobody.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import readonly
from linkedin_server import server as server_module
from linkedin_server.server import linkedin_tracker_stage
from tests.conftest import FakePage

BASE = "https://www.linkedin.com"
DOT = chr(0xB7)

#: A row as the tracker draws it -- synthetic, the shape test_tools' cards use.
STAGE_CARD = {
    "href": "/jobs/view/platform-engineer-at-acme-4155555556?refId=Iv",
    "text": (
        "Platform Engineer\n"
        "Platform Engineer\n"
        "Acme Corp\n"
        "Riverton, Fairhaven, United States (Remote)\n"
        "1 week ago"
    ),
}


def _strip(interview: str = "1", empty_state: str = "") -> str:
    """The tab strip as the captures draw it: Interview WITH a count, Archived
    WITHOUT one, and no clicked_apply tab."""
    lines = [
        "Job tracker",
        "Saved " + DOT + " 3",
        "In Progress " + DOT + " 1",
        "Applied " + DOT + " 2",
        "Interview " + DOT + " " + interview,
        "Archived",
    ]
    if empty_state:
        lines.append(empty_state)
    return "\n".join(lines)


@pytest.fixture
def drive(monkeypatch):
    """Point BROWSER at a FakePage; return the list of urls the tool opens."""
    navigations: list[str] = []

    def install(page: FakePage) -> list[str]:
        @asynccontextmanager
        async def fake_session():
            yield page

        async def fake_goto(target_page, url, **kwargs):
            navigations.append(url)
            await target_page.goto(url)
            return target_page.url

        monkeypatch.setattr(browser_module.BROWSER, "session", fake_session)
        monkeypatch.setattr(browser_module.BROWSER, "goto", fake_goto)
        return navigations

    return install


@pytest.mark.parametrize("stage", ["interview", "archived", "clicked_apply"])
async def test_each_stage_is_read_from_its_own_url(drive, stage):
    page = FakePage(evaluate_result=[STAGE_CARD])
    page.inner_text_result = _strip()
    navigations = drive(page)

    result = await linkedin_tracker_stage(stage, limit=25)

    assert "error" not in result, result
    assert navigations == [f"{BASE}/jobs-tracker/?stage={stage}"]
    assert result["count"] == 1
    assert result["tab"] == server_module.TRACKER_STAGES_LANE_A[stage]
    row = result["results"][0]
    assert row["job_id"] == "4155555556"
    assert row["title"] == "Platform Engineer"


@pytest.mark.parametrize(
    "stage",
    ["saved", "applied", "draft", "withdraw", "INTERVIEW", "interview/",
     "interview&x=1", "", None, 7],
)
async def test_any_other_stage_is_refused_before_a_page_opens(drive, stage):
    navigations = drive(FakePage(evaluate_result=[STAGE_CARD]))

    result = await linkedin_tracker_stage(stage, limit=25)

    assert result["error"] == "bad_argument", result
    assert navigations == []


async def test_a_corroborated_empty_interview_list_is_an_answer(drive):
    """Interview carries a count on the captures, so a zero can be believed."""
    page = FakePage(evaluate_result=[])
    page.inner_text_result = _strip(interview="0", empty_state="No matches")
    drive(page)

    result = await linkedin_tracker_stage("interview", limit=25)

    assert "error" not in result, result
    assert result["results"] == []
    assert result["empty"] is True
    assert result["linkedin_count"] == 0


@pytest.mark.parametrize("stage", ["archived", "clicked_apply"])
async def test_an_empty_list_on_a_tab_without_a_count_is_a_failure(drive, stage):
    """THE CONSERVATIVE DIRECTION, pinned. Archived is drawn without a count and
    clicked_apply not at all, so an empty list there cannot be told from a
    failed read -- and is reported as the failure, never as "you have none"."""
    page = FakePage(evaluate_result=[])
    page.inner_text_result = _strip(empty_state="No matches")
    drive(page)

    result = await linkedin_tracker_stage(stage, limit=25)

    assert result["error"] == "extraction_failed", result
    assert "count could not be read" in result["message"]


@pytest.mark.parametrize("stage", ["interview", "archived", "clicked_apply"])
def test_each_stage_address_is_admitted_by_exactly_its_own_line(stage):
    url = f"{BASE}/jobs-tracker/?stage={stage}"
    assert readonly.is_read_url(url)
    lines = [p for p in readonly._ALLOWED_URL_PATTERNS if p.match(url)]
    assert len(lines) == 1, [p.pattern for p in lines]
    assert lines[0].pattern.endswith("?stage=" + stage + "$"), lines[0].pattern


def test_the_stage_table_is_exactly_the_three_tokens():
    assert set(server_module.TRACKER_STAGES_LANE_A) == {
        "interview", "archived", "clicked_apply"}
