"""Recruiter insights -- census ``N 195``, read off a capture's skeleton.

THE ROW. "See recruiter insights (Premium): how many recruiters viewed your
profile, their trend, and each recruiter viewer's company and industry."
/analytics/recruiter-views/ was captured live on 2026-09-23 by the live lane;
``recruiter_views.read_recruiter_views`` reads it and
``linkedin_recruiter_insights`` returns it.

THE PEOPLE IN IT. The page names no member: each recruiter viewer is drawn as
an employer line, an industry and a time, linked to the employer's insights
page. WHO-WHICH-COUNTS-ARE-NOT-DELIVERY does not hold the row (lane Y2,
2026-09-24), and each viewer is returned the way ``linkedin_who_viewed_me``
returns a viewer drawn as "Recruiter at Acme": a people record, anonymous, no
link. Section 3 holds the six mitigations of PEOPLE-DATA-MITIGATIONS, each
with a control that shows the check can fail.

THE FIXTURE is ``tests/fixtures/synthetic/recruiter_views.html``, built by
``scripts/_build_capture_skeleton.py --plan recruiter``: the capture's
structure (the digest below is the builder's, printed from the capture), every
employer, industry, count, point and time invented.
"""
from __future__ import annotations

import asyncio
import ast
import sys
from pathlib import Path

import pytest

from linkedin_server import people_data, recruiter_views
from linkedin_server.errors import ExtractionFailedError
from linkedin_server import server as server_module
from tests import xhtml_page
from tests.test_people_search_names import (
    containers_written_at_module_level,
    page_calls_outside_the_allowlist,
    write_tools_reaching_through_helpers,
    _WriteSpy,
)

REPO = Path(__file__).resolve().parent.parent
FIXTURE = xhtml_page.SYNTHETIC / "recruiter_views.html"
READER_SOURCE = REPO / "linkedin_server" / "recruiter_views.py"
SERVER_SOURCE = REPO / "linkedin_server" / "server.py"

#: Printed by the builder from the CAPTURE's kept subtree on 2026-09-28.
STRUCTURE_DIGEST = "meedofnacenhhgaj"

VIEWERS = (
    ("Recruiter at Northgate Analytics", "Staffing and Recruiting", "2 weeks ago"),
    ("Recruiter at Umbrella Systems", "Software Development", "5 days ago"),
)

#: A name laced with a zero-width space and a direction override, planted on
#: the first viewer's employer line.
_LACED_NAME = "Recruiter at Zzq\u200bLaced\u202eEmployer"
_LACE = (
    "() => { const span = document.querySelector('a[tabindex] p span');"
    " span.textContent = 'Recruiter at Zzq\\u200bLaced\\u202eEmployer'; }"
)


def _builder():
    sys.path.insert(0, str(REPO / "scripts"))
    import _build_capture_skeleton as builder  # noqa: PLC0415
    return builder


def _read(mutate: str = "") -> dict:
    return xhtml_page.read(FIXTURE, recruiter_views.read_recruiter_views, mutate=mutate)


def _tool(mutate: str = "") -> dict:
    return xhtml_page.drive_tool(FIXTURE, server_module.linkedin_recruiter_insights,
                                 mutate=mutate)


# ---------------------------------------------------------------------------
# 0. The fixture is the capture's structure, and synthetic
# ---------------------------------------------------------------------------


def test_the_fixture_carries_the_structure_the_builder_printed_from_the_capture():
    builder = _builder()
    tree = builder.Tree()
    tree.feed(FIXTURE.read_text(encoding="ascii"))
    assert builder.structure_digest(builder.RECRUITER.select(tree.root), True) == STRUCTURE_DIGEST


def test_THIS_CONTROL_CAN_FAIL_the_digest_moves_when_an_attribute_does():
    """The attributes the reader selects on are in the digest: a chart region
    that is no longer a region fails it."""
    builder = _builder()
    tree = builder.Tree()
    tree.feed(FIXTURE.read_text(encoding="ascii").replace('role="region"', 'role="img"', 1))
    assert builder.structure_digest(builder.RECRUITER.select(tree.root), True) != STRUCTURE_DIGEST


def test_THIS_CONTROL_CAN_FAIL_the_digest_counts_the_chart_points():
    builder = _builder()
    text = FIXTURE.read_text(encoding="ascii")
    first = text.index("<path ")
    tree = builder.Tree()
    tree.feed(text[:first] + text[text.index("/>", first) + 2:])
    assert builder.structure_digest(builder.RECRUITER.select(tree.root), True) != STRUCTURE_DIGEST


# ---------------------------------------------------------------------------
# 1. The counts, the range and the trend
# ---------------------------------------------------------------------------


def test_the_counts_and_the_range_are_integers_under_declared_keys():
    result = _read()
    assert result["counts"] == {"profile_views": 41, "recruiter_views": 3}
    assert result["time_range_days"] == 90


def test_a_thousands_comma_in_a_count_is_read_as_a_number():
    mutate = ("() => { for (const p of document.querySelectorAll('p'))"
              " if (p.textContent === '41') p.textContent = '1,041'; }")
    assert _read(mutate)["counts"]["profile_views"] == 1041


def test_each_trend_is_its_thirteen_points_dated_by_this_package():
    trends = _read()["trends"]
    assert sorted(trends) == ["profile_views", "recruiter_views"]
    for key, series in (("profile_views", (3, 5, 2, 6, 4, 7, 3, 2, 5, 8, 4, 3, 6)),
                        ("recruiter_views", (0, 1, 0, 0, 2, 0, 1, 0, 0, 1, 0, 0, 1))):
        assert trends[key]["data_points"] == 13
        assert [p["views"] for p in trends[key]["points"]] == list(series)
        assert trends[key]["points"][0]["date"] == "2026-06-01"
        assert trends[key]["points"][-1]["date"] == "2026-08-24"


def test_no_label_the_page_drew_comes_back():
    result = _read()
    for label in ("Profile views", "Recruiter views", "Past 90 days", "Line chart",
                  "Views over time", "View insights", "Recruiter insights", "Premium"):
        assert not xhtml_page.anywhere(label, result), label


def test_a_point_label_of_another_shape_is_not_a_point():
    mutate = ("() => { const p = document.querySelector('path[aria-label]');"
              " p.setAttribute('aria-label', 'x, Zzqpointplant, 4. Views over time.'); }")
    result = _read(mutate)
    assert len(result["trends"]["profile_views"]["points"]) == 12
    assert not xhtml_page.anywhere("Zzqpointplant", result)


@pytest.mark.parametrize("drawn", ["Past 2 weeks", "90"])
def test_a_filter_label_of_another_shape_is_not_the_range(drawn):
    """ONLY "Past <n> days" IS A RANGE. A filter drawn in weeks, or as a bare
    number, is not guessed into days: the range reads null, and the reading
    still returns. Found by a planted mutation that survived every other test
    (a range pattern that also took a bare number)."""
    mutate = ("() => { document.querySelector('label').firstChild.textContent = '"
              + drawn + "'; }")
    result = _read(mutate)
    assert result["time_range_days"] is None, result["time_range_days"]
    assert result["counts"] == {"profile_views": 41, "recruiter_views": 3}


# ---------------------------------------------------------------------------
# 2. The viewers
# ---------------------------------------------------------------------------


def test_each_recruiter_viewer_is_a_record_as_linkedin_drew_it():
    viewers = _read()["viewers"]
    assert [(v["person"]["name"], v["person"]["headline"], v["viewed"]) for v in viewers] == [
        *VIEWERS
    ]
    for row in viewers:
        assert row["anonymous"] is True
        assert row["person"]["link"] is None and row["person"]["degree"] is None


def test_the_view_insights_twin_is_not_a_second_viewer():
    denominators = _read()["denominators"]
    assert denominators["insight_links_seen"] == 4
    assert denominators["viewer_rows_seen"] == 2
    assert denominators["viewers_returned"] == 2
    assert denominators["charts_seen"] == 2 and denominators["charts_read"] == 2


def test_a_query_on_a_viewer_link_does_not_drop_the_row():
    """The link is matched on its path: a tracking query LinkedIn adds does
    not turn a viewer into nobody (the cold review)."""
    mutate = ("() => { for (const a of document.querySelectorAll('a[href]'))"
              " if (a.getAttribute('href').indexOf('/company/') !== -1)"
              " a.setAttribute('href', a.getAttribute('href') + '?trk=example#top'); }")
    result = _read(mutate)
    assert [v["person"]["name"] for v in result["viewers"]] == [v[0] for v in VIEWERS]


def test_the_spelled_out_time_is_a_viewer_row_too():
    """Both of LinkedIn's notations: "Viewed 2w ago" and "Viewed 2 weeks ago"."""
    mutate = ("() => { for (const p of document.querySelectorAll('p'))"
              " if (p.textContent === 'Viewed 2w ago') p.textContent = 'Viewed 2 weeks ago'; }")
    viewers = _read(mutate)["viewers"]
    assert [v["viewed"] for v in viewers] == ["2 weeks ago", "5 days ago"]


def test_a_time_in_digits_that_are_not_ascii_never_leaves():
    """A digit is a digit to the time parser whatever its script; what leaves
    is this package's spelling in ASCII digits, or nothing."""
    drawn = "Viewed " + chr(0x665) + "d ago"
    mutate = ("() => { for (const p of document.querySelectorAll('p'))"
              " if (p.textContent === 'Viewed 5d ago') p.textContent = '" + drawn + "'; }")
    viewers = _read(mutate)["viewers"]
    assert viewers[1]["viewed"] is None
    assert viewers[0]["viewed"] == "2 weeks ago"


def test_a_chart_whose_card_names_no_metric_is_seen_not_absent():
    mutate = ("() => { for (const p of document.querySelectorAll('p'))"
              " if (p.textContent === 'Recruiter views') p.textContent = 'Example metric'; }")
    result = _read(mutate)
    assert sorted(result["trends"]) == ["profile_views"]
    assert result["denominators"]["charts_seen"] == 2
    assert result["denominators"]["charts_read"] == 1


def test_a_signed_out_load_is_an_error_not_an_empty_reading():
    envelope = xhtml_page.drive_tool(FIXTURE, server_module.linkedin_recruiter_insights,
                                     land_on="https://www.linkedin.com/login")
    assert envelope.get("error") == "not_authenticated", envelope
    assert "viewers" not in envelope and "counts" not in envelope


def test_the_employer_page_link_is_not_returned():
    result = _read()
    assert not xhtml_page.anywhere("/company/", result)
    assert not xhtml_page.anywhere("5417062", result)


def test_the_tool_returns_the_reading_off_one_load():
    envelope = _tool()
    assert envelope["ok"] is True and envelope["pages_loaded"] == 1
    assert envelope["_gotos"] == [recruiter_views.RECRUITER_VIEWS_URL]
    assert envelope["counts"] == {"profile_views": 41, "recruiter_views": 3}
    assert len(envelope["viewers"]) == 2


# ---------------------------------------------------------------------------
# 3. The six mitigations, each with a control that can fail
# ---------------------------------------------------------------------------


def test_mitigation_1_declared_fields_only():
    for row in _read()["viewers"]:
        assert set(row) == {"person", "viewed", "anonymous"}
        assert set(row["person"]) == people_data.PERSON_SHAPE


def test_mitigation_2_sanitised_and_marked_untrusted():
    row = _read(_LACE)["viewers"][0]
    assert row["person"]["name"] == people_data.sanitise(_LACED_NAME, cap=120)
    assert "\u200b" not in row["person"]["name"] and "\u202e" not in row["person"]["name"]
    assert row["person"][people_data.UNTRUSTED_KEY] == people_data.UNTRUSTED_NOTE


def test_THIS_CONTROL_CAN_FAIL_the_laced_name_reaches_the_page():
    async def raw(page):
        return await page.evaluate("() => document.querySelector('a[tabindex] p span').textContent")
    assert "\u200b" in xhtml_page.read(FIXTURE, raw, mutate=_LACE)


def test_mitigation_3_never_stored_no_state_and_no_file(monkeypatch):
    assert containers_written_at_module_level(READER_SOURCE.read_text(encoding="utf-8")) == []
    spy = _WriteSpy(monkeypatch)

    async def action(page):
        spy.armed = True
        try:
            return await recruiter_views.read_recruiter_views(page)
        finally:
            spy.armed = False

    assert len(asyncio.run(xhtml_page.with_page(FIXTURE, action))["viewers"]) == 2
    assert spy.opened == []


def test_mitigation_3_the_module_logs_nothing():
    source = READER_SOURCE.read_text(encoding="utf-8")
    assert "logging" not in source and "print(" not in source


def test_mitigation_4_one_page_per_call_and_nothing_but_finding_and_reading():
    assert len(_tool()["_gotos"]) == 1
    assert page_calls_outside_the_allowlist(READER_SOURCE.read_text(encoding="utf-8")) == []


def test_THIS_CONTROL_CAN_FAIL_a_scroll_in_the_reader_is_refused():
    anchor = "    lines = _lines(await anchor.inner_text())" + chr(10)
    source = READER_SOURCE.read_text(encoding="utf-8")
    assert source.count(anchor) == 1
    planted = source.replace(
        anchor, "    await anchor.scroll_into_view_if_needed()" + chr(10) + anchor)
    assert page_calls_outside_the_allowlist(planted) != []


def test_mitigation_5_visible_only_a_hidden_viewer_is_counted_and_not_read():
    hide = ("() => { const a = document.querySelectorAll('a[tabindex][href*=\"/company/\"]')[1];"
            " a.style.display = 'none'; }")
    result = _read(hide)
    assert [v["person"]["name"] for v in result["viewers"]] == [VIEWERS[0][0]]
    assert result["denominators"]["viewers_hidden"] == 1


def test_mitigation_5_a_viewer_inside_an_aria_hidden_container_is_not_read():
    hide = ("() => { const a = document.querySelectorAll('a[tabindex][href*=\"/company/\"]')[1];"
            " a.parentElement.setAttribute('aria-hidden', 'true'); }")
    result = _read(hide)
    assert len(result["viewers"]) == 1 and result["denominators"]["viewers_hidden"] == 1


def test_mitigation_6_never_a_target_no_link_and_no_write_reaches_the_reader():
    assert all(v["person"]["link"] is None for v in _read()["viewers"])
    assert write_tools_reaching_through_helpers(
        SERVER_SOURCE.read_text(encoding="utf-8"), "recruiter_views") == []


def test_the_tool_is_a_declared_people_tool():
    assert "linkedin_recruiter_insights" in people_data.PEOPLE_TOOLS


def test_a_failing_page_raises_by_type_alone():
    class Failing:
        async def query_selector_all(self, *args, **kwargs):
            raise ValueError("Zzqfailureplant Markersurname")

    with pytest.raises(ExtractionFailedError) as caught:
        asyncio.run(recruiter_views.read_recruiter_views(Failing()))
    assert "Zzqfailureplant" not in str(caught.value)
    assert caught.value.__cause__ is None and caught.value.__suppress_context__


def test_a_link_or_region_that_cannot_be_read_is_counted_by_type_and_the_rest_are_read():
    """One failing element is counted by its exception's TYPE, never its
    message, and every other element is still read."""
    class FailingElement:
        async def get_attribute(self, *args, **kwargs):
            raise ValueError("Zzqfailureplant Markersurname")

        async def query_selector_all(self, *args, **kwargs):
            raise ValueError("Zzqfailureplant Markersurname")

    class OneFailingEach:
        def __init__(self, page):
            self._page = page

        async def query_selector_all(self, selector, *args, **kwargs):
            found = await self._page.query_selector_all(selector, *args, **kwargs)
            if selector in (recruiter_views.CHART_REGIONS, recruiter_views.COMPANY_LINKS):
                return [FailingElement(), *found]
            return found

    async def action(page):
        return await recruiter_views.read_recruiter_views(OneFailingEach(page))

    result = xhtml_page.read(FIXTURE, action)
    assert [v["person"]["name"] for v in result["viewers"]] == [v[0] for v in VIEWERS]
    assert sorted(result["trends"]) == ["profile_views", "recruiter_views"]
    assert result["denominators"]["charts_failed"] == {"ValueError": 1}
    assert result["denominators"]["links_failed"] == {"ValueError": 1}
    assert not xhtml_page.anywhere("Zzqfailureplant", result)
