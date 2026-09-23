"""The tracker x posting proximity JOIN, ``linkedin_tracked_job_proximity``.

Census ``J 57`` -- view network connections reachable for a tracked job. Both
halves ship: the tracker read (``_read_tracker``, rows 47-49) and the posting's
proximity (``shape.find_proximity`` inside ``dom.read_job_posting``, row 40,
fired live). What this file tests is the JOIN, and it tests it twice:

* with the two halves FAKED, so every branch of the join -- a bad index, the
  clamp, a posting that fails, a posting that draws nothing -- is reached
  without a browser; and
* ONCE END TO END over the committed captures of BOTH halves in a real headless
  page, so the join is shown reading a real tracker row and a real posting's
  proximity rather than a dict this file wrote.

**EVERY CALL TO THE TOOL INSTALLS A FAKE ``BROWSER`` FIRST**, and the last test
asserts it by AST, the house guard from ``tests/test_connections_reader.py``:
a tool that navigates, called from a test that did not fake the browser,
drives a real Chrome against the real account.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from linkedin_server import server


class _FakeBrowser:
    """``BROWSER``: yields one page per session and records every goto."""

    def __init__(self, page=None, on_goto=None):
        self._page = page if page is not None else object()
        self._on_goto = on_goto
        self.gotos: list[str] = []
        self.last_settle = None

    def session(self):
        page = self._page

        class _Session:
            async def __aenter__(self_inner):
                return page

            async def __aexit__(self_inner, *exc):
                return False

        return _Session()

    async def goto(self, page, url):
        self.gotos.append(url)
        if self._on_goto is not None:
            await self._on_goto(page, url)
        return url


def _tracker(ids, *, empty=False, count=None):
    async def fake(stage, *, tab_label, limit, surface):
        rows = [{"job_id": i, "title": "Placeholder Title"} for i in ids]
        return {"results": rows[:limit], "linkedin_count": count,
                "empty": empty, "tab": tab_label}
    return fake


def _posting(by_id):
    """``dom.read_job_posting`` faked from ``{job_id: detail-or-exception}``."""
    async def fake(page):
        job_id = page.current
        value = by_id[job_id]
        if isinstance(value, Exception):
            raise value
        return {"identity": {}, "detail": value, "main_present": True,
                "main_chars": 100, "description_wait": None}
    return fake


class _Page:
    current = None


def _browser_tracking_ids(page):
    async def on_goto(p, url):
        p.current = url.rstrip("/").rsplit("/", 1)[-1]
    return _FakeBrowser(page, on_goto)


_READ = {"title": "Placeholder Title", "company": "Placeholder Org",
         "description": "Placeholder description."}
_RELATION = {"state": 1, "relation": 0, "count": None}


# ---------------------------------------------------------------------------
# 1. The arguments: an index, and a cost ceiling
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("stage", [True, "0", 3, -1, 1.0, None])
@pytest.mark.asyncio
async def test_a_stage_that_is_not_an_index_refuses_before_any_load(
        monkeypatch, stage):
    browser = _FakeBrowser()
    monkeypatch.setattr(server, "BROWSER", browser)
    monkeypatch.setattr(server, "_read_tracker", _tracker(["1000000001"]))
    out = await server.linkedin_tracked_job_proximity(stage=stage)
    assert out["error"] == "bad_argument"
    assert out["stages"] == ["saved", "applied", "draft"]
    assert browser.gotos == []
    assert repr(stage) not in out["message"], "the refusal quoted its input"


@pytest.mark.asyncio
async def test_the_limit_is_clamped_to_the_declared_ceiling(monkeypatch):
    page = _Page()
    browser = _browser_tracking_ids(page)
    ids = [str(1000000001 + n) for n in range(15)]
    monkeypatch.setattr(server, "BROWSER", browser)
    monkeypatch.setattr(server, "_read_tracker", _tracker(ids))
    monkeypatch.setattr(server.dom, "read_job_posting",
                        _posting({i: dict(_READ) for i in ids}))
    out = await server.linkedin_tracked_job_proximity(stage=0, limit=50)
    assert out["jobs_read"] == 10
    assert out["pages_loaded"] == 11
    assert len(browser.gotos) == 10


# ---------------------------------------------------------------------------
# 2. The join's states
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_drawn_not_drawn_and_unread_are_three_different_answers(
        monkeypatch):
    page = _Page()
    browser = _browser_tracking_ids(page)
    monkeypatch.setattr(server, "BROWSER", browser)
    monkeypatch.setattr(server, "_read_tracker", _tracker(
        ["1000000001", "1000000002", "1000000003", "1000000004"], count=4))
    monkeypatch.setattr(server.dom, "read_job_posting", _posting({
        "1000000001": dict(_READ, proximity=dict(_RELATION)),
        "1000000002": dict(_READ, proximity=None),
        "1000000003": {"title": None, "company": None, "description": None},
        "1000000004": RuntimeError("Placeholder page string"),
    }))
    out = await server.linkedin_tracked_job_proximity(stage=0, limit=5)
    states = [job["state"] for job in out["jobs"]]
    assert states == ["drawn", "not_drawn", "posting_unread", "posting_unread"]
    assert out["jobs"][0]["proximity"] == _RELATION
    assert out["jobs"][3]["error"] == "RuntimeError"
    assert "Placeholder page string" not in repr(out)
    assert out["with_proximity"] == 1
    assert out["pages_loaded"] == 5
    assert out["linkedin_count"] == 4


@pytest.mark.asyncio
async def test_the_join_publishes_ids_and_literals_and_no_page_text(monkeypatch):
    page = _Page()
    monkeypatch.setattr(server, "BROWSER", _browser_tracking_ids(page))
    monkeypatch.setattr(server, "_read_tracker", _tracker(["1000000001"]))
    monkeypatch.setattr(server.dom, "read_job_posting", _posting(
        {"1000000001": dict(_READ, proximity=dict(_RELATION))}))
    out = await server.linkedin_tracked_job_proximity(stage=0)
    assert "Placeholder Title" not in repr(out)
    assert "Placeholder Org" not in repr(out)
    assert out["proximity_states"][1] == "relation_only"
    assert out["proximity_relations"][0] == "company_alum"


@pytest.mark.asyncio
async def test_an_empty_stage_is_one_load_and_says_so(monkeypatch):
    browser = _FakeBrowser()
    monkeypatch.setattr(server, "BROWSER", browser)
    monkeypatch.setattr(server, "_read_tracker",
                        _tracker([], empty=True, count=0))
    out = await server.linkedin_tracked_job_proximity(stage=1)
    assert out["stage"] == "applied"
    assert out["empty"] is True
    assert out["jobs"] == [] and out["pages_loaded"] == 1
    assert browser.gotos == []


@pytest.mark.asyncio
async def test_a_tracker_failure_is_the_error_envelope_not_an_empty_join(
        monkeypatch):
    async def exploding(stage, *, tab_label, limit, surface):
        raise RuntimeError("tracker could not be read")

    browser = _FakeBrowser()
    monkeypatch.setattr(server, "BROWSER", browser)
    monkeypatch.setattr(server, "_read_tracker", exploding)
    out = await server.linkedin_tracked_job_proximity(stage=0)
    assert "error" in out and "jobs" not in out
    assert browser.gotos == []


@pytest.mark.asyncio
async def test_a_non_numeric_or_repeated_id_never_reaches_a_url(monkeypatch):
    page = _Page()
    browser = _browser_tracking_ids(page)
    monkeypatch.setattr(server, "BROWSER", browser)
    monkeypatch.setattr(server, "_read_tracker", _tracker(
        ["1000000001", "1000000001", "not-an-id", "12345"]))
    monkeypatch.setattr(server.dom, "read_job_posting", _posting(
        {"1000000001": dict(_READ, proximity=None)}))
    out = await server.linkedin_tracked_job_proximity(stage=0)
    assert [job["job_id"] for job in out["jobs"]] == ["1000000001"]
    assert browser.gotos == ["https://www.linkedin.com/jobs/view/1000000001"]


# ---------------------------------------------------------------------------
# 3. End to end over the committed captures of BOTH halves
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_the_join_end_to_end_over_the_committed_tracker_and_posting(
        monkeypatch):
    """A real tracker row and a real posting, joined in a real headless page.

    ``jobs_tracker_row.html`` is the tracked capture of a populated draft tab;
    ``job_detail_following_hydrated.html`` is the one committed posting that
    draws proximity -- ``relation_only`` / ``company_alum``, the reading the
    live fire of ``J 40`` reproduced. Whatever id the tracker yields, the
    posting capture is served for it, so this proves the join's plumbing and
    the proximity read, and NOT that this posting belongs to that row.
    """
    playwright = pytest.importorskip("playwright.async_api")
    fixtures = Path(__file__).parent / "fixtures"
    tracker_html = (fixtures / "jobs_tracker_row.html").read_text(
        encoding="utf-8")
    posting_html = (fixtures / "job_detail_following_hydrated.html").read_text(
        encoding="utf-8")

    async def on_goto(page, url):
        html = tracker_html if "/jobs-tracker/" in url else posting_html
        await page.set_content(html, wait_until="domcontentloaded",
                               timeout=60_000)

    async with playwright.async_playwright() as pw:
        chromium = await pw.chromium.launch(headless=True)
        try:
            page = await chromium.new_page()
            browser = _FakeBrowser(page, on_goto)
            monkeypatch.setattr(server, "BROWSER", browser)
            out = await server.linkedin_tracked_job_proximity(stage=2, limit=3)
        finally:
            await chromium.close()

    assert out.get("ok") is True, out
    assert out["stage"] == "draft"
    assert out["tracked_rows"] >= 1
    assert out["jobs_read"] >= 1
    first = out["jobs"][0]
    assert first["job_id"].isdigit()
    assert first["state"] == "drawn", first
    assert first["proximity"]["state"] == out["proximity_states"].index(
        "relation_only")
    assert first["proximity"]["relation"] == out["proximity_relations"].index(
        "company_alum")
    assert first["proximity"]["count"] is None
    assert browser.gotos[0].endswith("/jobs-tracker/?stage=draft")


# ---------------------------------------------------------------------------
# 4. The guard every navigating tool's test file carries
# ---------------------------------------------------------------------------


def test_every_call_to_the_tool_here_installs_the_fake_browser():
    source = Path(__file__).read_text(encoding="utf-8")
    offenders = []
    for func in ast.walk(ast.parse(source)):
        if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        calls = {node.func.attr for node in ast.walk(func)
                 if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Attribute)}
        if "linkedin_tracked_job_proximity" not in calls:
            continue
        body = ast.get_source_segment(source, func) or ""
        if 'monkeypatch.setattr(server, "BROWSER"' not in body:
            offenders.append(func.name)
    assert offenders == []
