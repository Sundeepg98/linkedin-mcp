"""A group's member list -- census ``N 165`` and ``N 177`` -- and a group's link, ``N 197``.

Lane B5, 2026-10-10.

THE READER, ``group_roster.read_group_members``, and its tool,
``linkedin_group_members``, run here OVER THE LIVE LANE'S TRACKED SKELETON of
one group's member list (``tests/fixtures/live2/group_members.html``, session 2,
2026-09-28) -- the markup LinkedIn served, every member's text reduced to
``x``. No new fixture is committed: each scenario loads that skeleton into a
local headless Chromium with EVERY request aborted, then a fill script writes
SYNTHETIC people into the places a person sits (the declared ``someone-
example`` slugs, invented names and headlines) and PLANTS a needle in every
place the reader must never read -- the screen-reader copy of the degree, the
Message button's label, the presence text, the photo's alt, a badge icon's
label, the group's own title and the heading above the list. Nothing is
loaded from LinkedIn; nothing is written anywhere.

ONE BROWSER FOR THE WHOLE FILE. Every scenario below runs in one headless
launch, once, and the tests assert on the cached readings: a launch per test
cost 254 s for this file on 2026-10-10, over the box's two-minute local cap.

SECTIONS. 1, the reader over the skeleton. 2, what is never read. 3, the six
PEOPLE-DATA-MITIGATIONS, each with a control that shows its check can fail.
4, the landing and the tool end to end. 5, ``group_link`` (N 197). 6, the
roster composer's first importer.
"""
from __future__ import annotations

import ast
import asyncio
import functools
import inspect
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import (
    browser as browser_module,
    group_page,
    group_roster,
    member_rosters,
    people_data,
    readonly,
    writes,
)
from linkedin_server import server as server_module
from tests.test_member_rosters import GROUP_ID
from tests.test_people_search_names import (
    ALLOWED_PAGE_CALLS,
    containers_written_at_module_level,
    page_calls_outside_the_allowlist,
    write_tools_reaching_through_helpers,
)

REPO = Path(__file__).resolve().parent.parent
SKELETON = REPO / "tests" / "fixtures" / "live2" / "group_members.html"
GROUP_HOME = REPO / "tests" / "fixtures" / "live2" / "group_home.html"
READER_SOURCE = REPO / "linkedin_server" / "group_roster.py"
SERVER_SOURCE = REPO / "linkedin_server" / "server.py"

#: The capture's own numbers, measured off the skeleton (lane B5, 2026-10-10)
#: and asserted below rather than assumed.
CAPTURED_ROWS = 20
ROWS_WITHOUT_A_DEGREE = (3, 6, 11, 16)

#: Needles, one per place the reader must never read. Invented strings with
#: no person's shape.
NEEDLES = {
    "a11y": "Zzqneedle Screenreader",
    "label": "Zzqneedle Buttonlabel",
    "presence": "Zzqneedle Presence",
    "alt": "Zzqneedle Photoalt",
    "icon": "Zzqneedle Badgeicon",
    "group": "Zzqneedle Grouptitle",
    "heading": "Zzqneedle Heading",
}

DEGREE_CYCLE = ("1st", "2nd", "3rd+")

#: LinkedIn's separator before the degree, built from its code point so this
#: file stays ASCII (a tool that wrote an escape here once decoded it).
MIDDLE_DOT = chr(0x00B7)

#: A name laced with a zero-width space and a right-to-left override.
LACED = "Example" + chr(0x200B) + " Member" + chr(0x202E) + " Laced"


def synthetic_row(index: int) -> dict[str, str]:
    """The invented person written into row ``index``."""
    return {
        "slug": f"someone-example-{index + 101}",
        "name": f"Example Member {index:02d}",
        "headline": f"Synthetic headline {index:02d} | Example Labs",
        "degree": MIDDLE_DOT + " " + DEGREE_CYCLE[index % 3],
        "bare_degree": DEGREE_CYCLE[index % 3],
    }


ROWS = tuple(synthetic_row(i) for i in range(CAPTURED_ROWS))

#: Writes the synthetic people into the skeleton's rows and plants every
#: needle. Returns, per row, whether the row draws a degree span -- the
#: capture's own fact, read back so the expectation is not assumed.
FILL = """([rows, needles]) => {
  const items = document.querySelectorAll(
    'ul.groups-members-list__results-list > li.groups-members-list__typeahead-result');
  const drawn = [];
  items.forEach((li, i) => {
    const spec = rows[i];
    li.querySelector('a.ui-entity-action-row__link').setAttribute('href', '/in/' + spec.slug + '/');
    li.querySelector('.artdeco-entity-lockup__title').textContent = spec.name;
    li.querySelector('.artdeco-entity-lockup__subtitle').textContent = spec.headline;
    const degree = li.querySelector('.artdeco-entity-lockup__degree');
    if (degree) { degree.textContent = spec.degree; }
    const a11y = li.querySelector('.a11y-text');
    if (a11y) { a11y.textContent = needles.a11y + ' ' + spec.bare_degree; }
    li.querySelectorAll('button').forEach((b) => b.setAttribute('aria-label', 'Message ' + needles.label));
    li.querySelectorAll('.presence-entity .visually-hidden').forEach((s) => { s.textContent = needles.presence; });
    li.querySelectorAll('img').forEach((img) => img.setAttribute('alt', needles.alt));
    li.querySelectorAll('svg[aria-label]').forEach((svg) => svg.setAttribute('aria-label', needles.icon));
    drawn.push(Boolean(degree));
  });
  const groupLink = document.querySelector('a.groups-members-list__groups-entity-link');
  if (groupLink) {
    groupLink.setAttribute('href', '/groups/12345678/');
    groupLink.setAttribute('aria-label', needles.group);
    groupLink.querySelectorAll('span').forEach((s) => { s.textContent = needles.group; });
  }
  document.querySelectorAll('h1').forEach((h) => { h.textContent = needles.heading; });
  return drawn;
}"""

#: The first row's name element, set to the argument.
SET_FIRST_NAME = (
    "(value) => { document.querySelector('.artdeco-entity-lockup__title')"
    ".textContent = value; }"
)

NESTED_NAME = (
    "() => { const t = document.querySelector('.artdeco-entity-lockup__title');"
    " const s = document.createElement('span'); s.textContent = 'Zzqneedle Nested';"
    " t.appendChild(s); }"
)
TWO_LINKS = (
    "() => { const li = document.querySelector('li.groups-members-list__typeahead-result');"
    " const a = document.createElement('a'); a.setAttribute('href', '/in/someone-example-999/');"
    " a.textContent = 'other'; li.appendChild(a); }"
)
FORTY_ROWS = (
    "() => { const list = document.querySelector('ul.groups-members-list__results-list');"
    " const first = list.querySelector('li');"
    " for (let i = 0; i < 20; i++) { const c = first.cloneNode(true);"
    " c.querySelector('a.ui-entity-action-row__link').setAttribute('href',"
    " '/in/someone-example-' + (500 + i) + '/'); list.appendChild(c); } }"
)
HIDE_FIRST_ROW = (
    "() => { document.querySelector('li.groups-members-list__typeahead-result')"
    ".style.display = 'none'; }"
)
COUNT_PRESSES = (
    "() => { window.__presses = 0; document.querySelectorAll("
    "'button.scaffold-finite-scroll__load-button').forEach((b) => "
    "b.addEventListener('click', () => { window.__presses += 1; })); }"
)

#: Reader scenarios: (mutate script, its argument, a module patch, extra read).
READER_SCENARIOS: dict[str, dict[str, Any]] = {
    "clean": {},
    "badge_headline": {"patch": ("HEADLINE", ".artdeco-entity-lockup__badge")},
    "nested": {"mutate": NESTED_NAME},
    "two_links": {"mutate": TWO_LINKS},
    "laced": {"mutate": SET_FIRST_NAME, "arg": LACED, "raw_title": True},
    "forty": {"mutate": FORTY_ROWS},
    "hidden": {"mutate": HIDE_FIRST_ROW},
    "anonymised": {"mutate": SET_FIRST_NAME, "arg": people_data.ANONYMISED_NAME},
    "presses": {"mutate": COUNT_PRESSES, "presses": True},
}

ELSEWHERE = f"https://www.linkedin.com/groups/{GROUP_ID}/?zzqlanding=1"
AUTHWALL = "https://www.linkedin.com/authwall?sessionRedirect=zzqbounced"
OTHER_GROUP = "https://www.linkedin.com/groups/87654321/"

#: Tool scenarios: (tool name, skeleton, landing, arguments).
TOOL_SCENARIOS: dict[str, tuple[str, Path, str, dict[str, str]]] = {
    "members_ok": ("linkedin_group_members", SKELETON, "", {"group_id": GROUP_ID}),
    "members_elsewhere": ("linkedin_group_members", SKELETON, ELSEWHERE, {"group_id": GROUP_ID}),
    "members_authwall": ("linkedin_group_members", SKELETON, AUTHWALL, {"group_id": GROUP_ID}),
    "members_slug": ("linkedin_group_members", SKELETON, "", {"group_id": "zzq-slug-group"}),
    "page_same": ("linkedin_group_page", GROUP_HOME, "", {"group_id": GROUP_ID}),
    "page_feed": ("linkedin_group_page", GROUP_HOME, "https://www.linkedin.com/feed/",
                  {"group_id": GROUP_ID}),
    "page_other": ("linkedin_group_page", GROUP_HOME, OTHER_GROUP, {"group_id": GROUP_ID}),
}


async def _load(context: Any, skeleton: Path, fill: bool) -> tuple[Any, list[bool]]:
    page = await context.new_page()
    await page.set_content(skeleton.read_text(encoding="utf-8"))
    drawn: list[bool] = []
    if fill:
        drawn = await page.evaluate(FILL, [list(ROWS), NEEDLES])
    return page, drawn


async def _reader_scenario(context: Any, spec: dict[str, Any]) -> dict[str, Any]:
    page, drawn = await _load(context, SKELETON, True)
    try:
        if spec.get("mutate"):
            if "arg" in spec:
                await page.evaluate(spec["mutate"], spec["arg"])
            else:
                await page.evaluate(spec["mutate"])
        out: dict[str, Any] = {"drawn": drawn}
        if spec.get("raw_title"):
            out["raw_title"] = await page.evaluate(
                "() => document.querySelector('.artdeco-entity-lockup__title').textContent")
        before = page.url
        patch = spec.get("patch")
        original = getattr(group_roster, patch[0]) if patch else None
        if patch:
            setattr(group_roster, patch[0], patch[1])
        try:
            out["result"] = await group_roster.read_group_members(page)
        finally:
            if patch:
                setattr(group_roster, patch[0], original)
        if spec.get("presses"):
            out["presses"] = await page.evaluate("() => window.__presses")
            out["stayed"] = before == page.url
        return out
    finally:
        await page.close()


async def _tool_scenario(context: Any, spec: tuple) -> dict[str, Any]:
    name, skeleton, land_on, arguments = spec
    page, _drawn = await _load(context, skeleton, skeleton == SKELETON)
    gotos: list[str] = []

    @asynccontextmanager
    async def fake_session(*args: Any, **more: Any):
        yield page

    async def fake_goto(target: Any, url: str, **more: Any) -> str:
        gotos.append(url)
        return land_on or url

    original = browser_module.BROWSER.session, browser_module.BROWSER.goto
    browser_module.BROWSER.session = fake_session
    browser_module.BROWSER.goto = fake_goto
    try:
        envelope = await getattr(server_module, name)(**arguments)
    finally:
        browser_module.BROWSER.session, browser_module.BROWSER.goto = original
        await page.close()
    envelope["_gotos"] = list(gotos)
    return envelope


async def _run_all() -> dict[str, Any]:
    playwright = pytest.importorskip("playwright.async_api")
    out: dict[str, Any] = {}
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            context = await browser.new_context()
            await context.route("**/*", lambda route: route.abort())
            for name, spec in READER_SCENARIOS.items():
                out[name] = await _reader_scenario(context, spec)
            for name, spec in TOOL_SCENARIOS.items():
                out[name] = await _tool_scenario(context, spec)
        finally:
            await browser.close()
    return out


@functools.lru_cache(maxsize=1)
def readings() -> dict[str, Any]:
    """Every scenario, run once in one browser."""
    return asyncio.run(_run_all())


def result_of(name: str) -> dict[str, Any]:
    return readings()[name]["result"]


def walk_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from walk_strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from walk_strings(item)


def needles_in(value: Any) -> list[str]:
    return sorted(
        kind for kind, needle in NEEDLES.items()
        for text in walk_strings(value) if needle in text
    )


def expected_people(drawn: list[bool]) -> list[dict[str, Any]]:
    return [
        people_data.Person(
            name=spec["name"],
            headline=spec["headline"],
            link=f"https://www.linkedin.com/in/{spec['slug']}/",
            degree=spec["bare_degree"] if drawn[i] else None,
        ).envelope()
        for i, spec in enumerate(ROWS)
    ]


# ---------------------------------------------------------------------------
# 1. The reader over the tracked skeleton
# ---------------------------------------------------------------------------


def test_every_row_the_capture_drew_comes_back_as_a_person_record():
    clean = readings()["clean"]
    assert clean["result"]["people"] == expected_people(clean["drawn"])
    assert clean["result"]["people_denominators"] == {
        "member_lists_seen": 1,
        "rows_seen": CAPTURED_ROWS,
        "rows_attempted": CAPTURED_ROWS,
        "people_returned": CAPTURED_ROWS,
        "degree_drawn": CAPTURED_ROWS - len(ROWS_WITHOUT_A_DEGREE),
        "skipped": {reason: 0 for reason in group_roster.SKIP_REASONS},
        "headline_unread": 0,
        "more_members_control_drawn": 1,
        "failed": {},
    }


def test_the_rows_without_a_degree_are_the_captures_own_and_come_back_none():
    """Four of the capture's twenty rows draw an empty badge. Their degree is
    None -- not a guess, not the screen-reader copy."""
    clean = readings()["clean"]
    assert [i for i, has in enumerate(clean["drawn"]) if not has] == list(ROWS_WITHOUT_A_DEGREE)
    for i in ROWS_WITHOUT_A_DEGREE:
        assert clean["result"]["people"][i]["degree"] is None


def test_n177_the_people_he_knows_are_the_members_drawn_first_degree():
    """N 177 reads the declared degree field: a member drawn 1st is one of his
    connections. The reader returns every member and their degree; the
    people he knows are exactly the 1st-degree ones, and no other row."""
    clean = readings()["clean"]
    known = [p["name"] for p in clean["result"]["people"] if p["degree"] == "1st"]
    assert known == [
        spec["name"] for i, spec in enumerate(ROWS)
        if clean["drawn"][i] and spec["bare_degree"] == "1st"
    ]
    assert known, "the capture drew no 1st-degree row to check against"


def test_the_load_more_control_is_counted_and_never_pressed():
    """ONE PAGE: the capture's finite-scroll control says more members exist.
    A listener counts presses on it; the read presses nothing and the page
    does not move."""
    presses = readings()["presses"]
    assert presses["result"]["people_denominators"]["more_members_control_drawn"] == 1
    assert presses["presses"] == 0 and presses["stayed"] is True


# ---------------------------------------------------------------------------
# 2. What is never read
# ---------------------------------------------------------------------------


def test_no_needle_crosses_from_any_place_the_reader_must_not_read():
    assert needles_in(result_of("clean")) == []


def test_THIS_CONTROL_CAN_FAIL_a_reader_aimed_at_the_badge_carries_the_screen_reader_copy():
    """The needle check is not vacuous: aim the headline at the badge, which
    holds the screen-reader copy beside the visible degree, and the needle
    crosses."""
    assert "a11y" in needles_in(result_of("badge_headline"))


def test_a_name_element_holding_a_child_with_text_is_skipped_not_split():
    result = result_of("nested")
    assert result["people_denominators"]["skipped"]["name_has_nested_text"] == 1
    assert len(result["people"]) == CAPTURED_ROWS - 1
    assert not any("Zzqneedle Nested" in text for text in walk_strings(result))


def test_a_row_holding_two_member_links_is_skipped_not_guessed():
    result = result_of("two_links")
    assert result["people_denominators"]["skipped"]["more_than_one_member_link"] == 1
    assert len(result["people"]) == CAPTURED_ROWS - 1


# ---------------------------------------------------------------------------
# 3. The six PEOPLE-DATA-MITIGATIONS
# ---------------------------------------------------------------------------


def test_mitigation_1_declared_fields_only():
    result = result_of("clean")
    assert set(result) == {"people", "people_denominators"}
    for envelope in result["people"]:
        assert frozenset(envelope) == people_data.PERSON_SHAPE
        assert type(people_data.as_record(envelope)) is people_data.Person


def test_mitigation_2_sanitised_and_marked():
    laced = readings()["laced"]
    assert laced["result"]["people"][0]["name"] == "Example Member Laced"
    assert all(
        p[people_data.UNTRUSTED_KEY] == people_data.UNTRUSTED_NOTE
        for p in laced["result"]["people"]
    )


def test_THIS_CONTROL_CAN_FAIL_the_lace_really_reached_the_page():
    """Without this, mitigation 2 could pass on a page the lace never
    reached: the raw title held the invisible characters."""
    raw = readings()["laced"]["raw_title"]
    assert raw == LACED and chr(0x200B) in raw and chr(0x202E) in raw


def test_mitigation_3_the_reader_keeps_no_state_and_writes_nothing():
    source = READER_SOURCE.read_text(encoding="utf-8")
    assert containers_written_at_module_level(source) == []
    tree = ast.parse(source)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert not names & {"open", "print", "logger", "logging", "LOG"}
    assert not attributes & {"write_text", "write_bytes", "write", "info", "debug",
                             "warning", "error", "exception"}


def test_mitigation_3_a_failure_is_counted_by_its_type_and_never_quoted():
    class Raising:
        def locator(self, selector: str) -> Any:
            raise RuntimeError(NEEDLES["label"])

    result = asyncio.run(group_roster.read_group_members(Raising()))
    assert result["people"] == []
    assert result["people_denominators"]["failed"] == {"RuntimeError": 1}
    assert needles_in(result) == []


def test_mitigation_4_one_page_and_a_bounded_number_of_rows():
    """Forty rows drawn, each a distinct member: twenty-five are read."""
    counts = result_of("forty")["people_denominators"]
    assert counts["rows_seen"] == 40
    assert counts["rows_attempted"] == group_roster.MAX_ROWS_READ == 25
    assert counts["people_returned"] == 25


def _calls_outside(source: str) -> list[str]:
    """The people search's own allowlist of finds and reads, plus ``count``,
    which returns an integer."""
    allowed = ALLOWED_PAGE_CALLS | {"count"}
    return [
        call for call in page_calls_outside_the_allowlist(source)
        if call.split(" at line ")[0] not in allowed
    ]


def test_mitigation_4_the_reader_only_finds_and_reads():
    assert _calls_outside(READER_SOURCE.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize("plant", [
    "async def read(page, row):\n    await row.click()\n",
    "async def read(page):\n    await page.mouse.wheel(0, 2000)\n",
    "async def read(page, row):\n    await row.scroll_into_view_if_needed()\n",
], ids=["click", "wheel", "scroll"])
def test_THIS_CONTROL_CAN_FAIL_a_press_or_a_scroll_is_refused(plant):
    assert _calls_outside(plant) != []


def test_mitigation_5_a_row_the_page_hides_is_not_read():
    result = result_of("hidden")
    assert result["people_denominators"]["skipped"]["not_visible"] == 1
    assert ROWS[0]["name"] not in [p["name"] for p in result["people"]]


def test_mitigation_5_an_anonymised_member_stays_anonymised():
    assert result_of("anonymised")["people"][0]["name"] == people_data.ANONYMISED_NAME


def _imports_of(path: Path) -> set[str]:
    """The orphan rule's own import reader (parsed, never grepped)."""
    from tests.test_every_orphan_module_is_ruled import _imported_submodules

    return _imported_submodules(path)


def test_mitigation_6_no_write_reaches_the_reader():
    assert write_tools_reaching_through_helpers(
        SERVER_SOURCE.read_text(encoding="utf-8"), "group_roster") == []
    assert "linkedin_group_members" not in writes.SANCTIONED_WRITES
    importers = sorted(
        path.name for path in (REPO / "linkedin_server").glob("*.py")
        if path.name != "group_roster.py" and "group_roster" in _imports_of(path)
    )
    assert importers == ["server.py"]


def test_THIS_CONTROL_CAN_FAIL_a_write_tool_behind_a_helper_is_found():
    planted = (
        "async def _first(page):\n"
        "    return (await group_roster.read_group_members(page))['people'][0]\n"
        "async def linkedin_planted(page):\n"
        "    target = await _first(page)\n"
        "    return await _write_tool(target)\n"
    )
    assert write_tools_reaching_through_helpers(planted, "group_roster") == [
        "linkedin_planted"
    ]


def test_the_tool_is_a_declared_people_tool():
    assert "linkedin_group_members" in people_data.PEOPLE_TOOLS


# ---------------------------------------------------------------------------
# 4. The landing, and the tool end to end
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("landed, verdict", [
    (f"https://www.linkedin.com/groups/{GROUP_ID}/members/", True),
    (f"https://www.linkedin.com/groups/{GROUP_ID}/members", True),
    (f"https://www.linkedin.com/groups/{GROUP_ID}/members/?trk=x", True),
    (f"https://www.linkedin.com/groups/{GROUP_ID}/", False),
    ("https://www.linkedin.com/groups/87654321/members/", False),
    (f"https://www.linkedin.com/groups/{GROUP_ID}/members/extra/", False),
    (f"https://evil.example/groups/{GROUP_ID}/members/", False),
    ("https://www.linkedin.com/feed/", None),
    ("", None),
    (None, None),
])
def test_the_landing_must_be_this_groups_member_list(landed, verdict):
    assert group_roster.landed_on_the_members_page(landed, GROUP_ID) is verdict


def test_the_tool_reads_one_page_of_the_list_it_composed():
    envelope = readings()["members_ok"]
    assert envelope["ok"] is True and envelope["pages_loaded"] == 1
    assert envelope["_gotos"] == [member_rosters.compose("group_members", GROUP_ID)["url"]]
    assert readonly.is_read_url(envelope["_gotos"][0])
    assert envelope["landed_on_the_members_page"] is True
    assert envelope["people_denominators"]["people_returned"] == CAPTURED_ROWS
    assert needles_in(envelope) == []


def test_a_landing_elsewhere_reads_nothing_and_does_not_publish_the_landing():
    envelope = readings()["members_elsewhere"]
    assert envelope["landed_on_the_members_page"] is False
    assert envelope["people"] == [] and envelope["people_denominators"] is None
    assert not any("zzqlanding" in text for text in walk_strings(envelope))


def test_a_signed_out_landing_is_an_error_and_names_no_landing():
    envelope = readings()["members_authwall"]
    assert envelope.get("ok") is not True
    assert "people" not in envelope
    assert not any("zzqbounced" in text for text in walk_strings(envelope))


def test_a_slug_is_refused_before_any_navigation_and_is_never_echoed():
    envelope = readings()["members_slug"]
    assert envelope["ok"] is False and envelope["_gotos"] == []
    assert not any("zzq-slug-group" in text for text in walk_strings(envelope))


def test_the_tool_takes_no_paging_argument():
    assert list(inspect.signature(server_module.linkedin_group_members).parameters) == [
        "group_id"
    ]


# ---------------------------------------------------------------------------
# 5. N 197 -- the group's own link, from linkedin_group_page
# ---------------------------------------------------------------------------


def test_group_link_is_the_composed_address_only_on_the_same_group():
    link = group_page.group_link(GROUP_ID, True)
    assert link == f"https://www.linkedin.com/groups/{GROUP_ID}/"
    assert link == people_data.canonical_group_link(link)
    assert readonly.is_read_url(link)
    assert group_page.group_link(GROUP_ID, False) is None
    assert group_page.group_link(GROUP_ID, None) is None
    assert group_page.group_link("a-group-slug", True) is None


def test_the_group_page_tool_returns_the_link_when_it_landed_on_that_group():
    envelope = readings()["page_same"]
    assert envelope["ok"] is True and envelope["landed_on_the_same_group"] is True
    assert envelope["group_link"] == f"https://www.linkedin.com/groups/{GROUP_ID}/"
    assert envelope["_gotos"] == [envelope["group_link"]]


@pytest.mark.parametrize("scenario", ["page_feed", "page_other"])
def test_the_group_page_tool_withholds_the_link_on_any_other_landing(scenario):
    envelope = readings()[scenario]
    assert envelope["group_link"] is None
    assert not any("87654321" in text for text in walk_strings(envelope))


# ---------------------------------------------------------------------------
# 6. The roster composer's first importer
# ---------------------------------------------------------------------------


def test_the_one_roster_the_package_composes_is_the_group_members_list():
    """member_rosters composes four rosters; this lane wires ONE. The other
    three (event attendees, company and school People tabs) have no capture
    and no reader, and nothing in the package composes them."""
    source = SERVER_SOURCE.read_text(encoding="utf-8")
    assert "member_rosters.compose(group_roster.ROSTER" in source
    assert group_roster.ROSTER == "group_members"
    assert group_roster.ROSTER in member_rosters.ROSTERS
    for other in ("event_attendees", "company_people", "school_people"):
        assert other not in source


def test_this_file_stays_ascii():
    data = Path(__file__).read_bytes()
    assert [i for i, byte in enumerate(data) if byte > 127] == []
