"""ONE detail page of a profile he names -- ruling NAMED-PROFILE-DETAIL-PAGES (lane NP, 2026-10-10).

THE RULING (orchestrator, 2026-10-10, applying the operator's 08:01 YES to
reading profiles he names; ``_audit/2026-10-10-rulings-named-profile-detail-pages.md``):
"the read of a profile he names includes that SAME profile's own detail pages
(/in/<the same slug>/details/<section>/), one load per call, behind the same
single-use grant and the same preview warning."

THE SECTIONS:

1. The register: the ruling's entry.
2. The door: exactly that shape, for the named segment only -- and the controls,
   each refused, and each shown to be refused BY the check it names.
3. The browser: the third check is asked only when the caller names a segment,
   and never together with the profile door.
4. The read: the preview loads nothing and binds its token to that one page;
   one load; a landing elsewhere reads nothing; counts only.
5. Who reaches it: one function asks for the third check, and one tool.

NOTHING HERE REACHES LINKEDIN.
"""
from __future__ import annotations

import ast
import contextlib
import pathlib

import pytest

from linkedin_server import named_details, named_profile, readonly, server
from linkedin_server.errors import WriteAttemptError
from tests.test_writes import browser_page  # noqa: F401 -- a fixture

REPO = pathlib.Path(__file__).resolve().parent.parent
SEGMENT = "casey-example-3f9a"
OTHER = "someone-example-1"
LINK = "https://www.linkedin.com/in/" + SEGMENT + "/"
INTERESTS = "https://www.linkedin.com/in/" + SEGMENT + "/details/interests/"
PAGE = "<html><head><title>Example</title></head><body><h1>Example</h1>" \
       "<ul><li><a href=\"/groups/1234501/\">Example Group</a></li></ul></body></html>"


@pytest.fixture(autouse=True)
def _no_read_grant_survives_a_test():
    named_profile.discard_read_grants()
    yield
    named_profile.discard_read_grants()


# ---------------------------------------------------------------------------
# 1. The register
# ---------------------------------------------------------------------------


def test_the_ruling_is_registered_with_its_document():
    from scripts import build_rulings_index as bri

    found = [r for r in bri.REGISTER if r.id == "NAMED-PROFILE-DETAIL-PAGES"]
    assert len(found) == 1, found
    entry = found[0]
    assert entry.document == "_audit/2026-10-10-rulings-named-profile-detail-pages.md"
    text = (REPO / entry.document).read_text(encoding="utf-8")
    assert entry.anchor in text
    assert "/in/<the same slug>/details/<section>/" in text


# ---------------------------------------------------------------------------
# 2. The door
# ---------------------------------------------------------------------------


def test_the_door_admits_a_detail_page_of_the_named_profile():
    for section in readonly.NAMED_PROFILE_DETAIL_SECTIONS:
        url = readonly.named_profile_details_url(SEGMENT, section)
        assert url == LINK + "details/" + section + "/"
        assert readonly.assert_named_profile_details_url(url, SEGMENT) == url


REFUSED = (
    # ANOTHER MEMBER'S detail page, asked under the named segment.
    ("https://www.linkedin.com/in/" + OTHER + "/details/interests/", SEGMENT),
    # The same page in another ASCII case: the door compares the segment it was
    # handed exactly, as it composed it.
    ("https://www.linkedin.com/in/Casey-Example-3f9a/details/interests/", SEGMENT),
    # Non-details paths under the named profile.
    (LINK, SEGMENT),
    (LINK + "recent-activity/all/", SEGMENT),
    (LINK + "overlay/contact-info/", SEGMENT),
    (LINK + "edit/intro/", SEGMENT),
    # A section off the vocabulary.
    (LINK + "details/recommendations/", SEGMENT),
    (LINK + "details/connections/", SEGMENT),
    # A query, a fragment, a deeper path, no trailing slash, another host.
    (INTERESTS + "?detailScreenTabIndex=1", SEGMENT),
    (INTERESTS + "#groups", SEGMENT),
    (INTERESTS + "groups/", SEGMENT),
    (INTERESTS[:-1], SEGMENT),
    ("https://linkedin.com/in/" + SEGMENT + "/details/interests/", SEGMENT),
    # Whitespace, and a segment carrying a word the boundary refuses anywhere.
    (INTERESTS + " ", SEGMENT),
    ("https://www.linkedin.com/in/settings-example-1/details/interests/", "settings-example-1"),
    # No segment named at all.
    (INTERESTS, ""),
)


@pytest.mark.parametrize("url, named", REFUSED)
def test_every_other_address_is_refused_and_not_quoted(url, named):
    with pytest.raises(WriteAttemptError) as caught:
        readonly.assert_named_profile_details_url(url, named)
    assert SEGMENT not in str(caught.value) and OTHER not in str(caught.value)


def test_control_the_shape_alone_admits_another_member_so_the_segment_check_is_what_refuses():
    """The anchored shape matches ANOTHER member's detail page: the comparison
    with the named segment is the check that refuses it, not the regex."""
    stranger = "https://www.linkedin.com/in/" + OTHER + "/details/interests/"
    assert readonly._NAMED_PROFILE_DETAILS_URL.fullmatch(stranger)
    assert readonly.assert_named_profile_details_url(stranger, OTHER) == stranger
    with pytest.raises(WriteAttemptError):
        readonly.assert_named_profile_details_url(stranger, SEGMENT)


def test_control_the_shape_alone_admits_a_section_off_the_vocabulary():
    off = LINK + "details/recommendations/"
    assert readonly._NAMED_PROFILE_DETAILS_URL.fullmatch(off)
    with pytest.raises(WriteAttemptError):
        readonly.assert_named_profile_details_url(off, SEGMENT)
    with pytest.raises(WriteAttemptError):
        readonly.named_profile_details_url(SEGMENT, "recommendations")


def test_the_other_two_doors_still_refuse_a_detail_page():
    assert not readonly.is_read_url(INTERESTS)
    with pytest.raises(WriteAttemptError):
        readonly.assert_read_url(INTERESTS)
    with pytest.raises(WriteAttemptError):
        readonly.assert_named_profile_url(INTERESTS)


# ---------------------------------------------------------------------------
# 3. The browser
# ---------------------------------------------------------------------------


class _Page:
    def __init__(self):
        self.visited: list[str] = []

    async def goto(self, url, **_kwargs):
        self.visited.append(url)


async def test_the_browser_asks_the_third_check_only_for_the_named_segment(monkeypatch):
    from linkedin_server import browser as browser_module

    nav = browser_module.LinkedInBrowser()

    async def _no_wait(*_args, **_kwargs):
        return 0.0

    monkeypatch.setattr(nav, "wait_for_rate_slot", _no_wait)
    page = _Page()
    for url, kwargs in (
        (INTERESTS, {}),
        (INTERESTS, {"named_profile": True}),
        (INTERESTS, {"named_profile_details_of": OTHER}),
        (INTERESTS, {"named_profile_details_of": SEGMENT, "named_profile": True}),
        (LINK, {"named_profile_details_of": SEGMENT}),
    ):
        with pytest.raises(WriteAttemptError):
            await nav.goto(page, url, **kwargs)
    assert page.visited == [], "a door let a detail page through"


# ---------------------------------------------------------------------------
# 4. The read
# ---------------------------------------------------------------------------


class _Navigator:
    """Serves one frozen page, LANDS where the test says, records every ask."""

    def __init__(self, *, landed=None):
        self.landed = landed
        self.asks: list[tuple[str, dict]] = []

    async def goto(self, page, url, **kwargs):
        self.asks.append((url, kwargs))
        await page.set_content(PAGE, wait_until="domcontentloaded", timeout=60_000)
        return self.landed if self.landed is not None else url


class _Browser:
    def __init__(self, page, navigator):
        self.page = page
        self.navigator = navigator
        self.sessions = 0

    @contextlib.asynccontextmanager
    async def session(self):
        self.sessions += 1
        yield self.page

    async def goto(self, page, url, **kwargs):
        return await self.navigator.goto(page, url, **kwargs)


class _NoBrowser:
    sessions = 0

    def session(self):
        raise AssertionError("the tool opened a browser")

    async def goto(self, *_args, **_kwargs):
        raise AssertionError("the tool navigated")


async def test_the_preview_loads_nothing_and_binds_its_token_to_that_page(monkeypatch):
    monkeypatch.setattr(server, "BROWSER", _NoBrowser())
    block = await server.linkedin_read_named_profile(LINK, section="interests")
    assert block["loaded"] is False and block["pages_loaded"] == 0
    assert block["page_this_loads"] == INTERESTS
    assert "may show this member that you viewed" in block["they_may_see_this_view"]
    assert block["confirm_token"]
    # A SECTION OFF THE VOCABULARY is refused before a grant or a browser.
    refused = await server.linkedin_read_named_profile(LINK, section="recommendations")
    assert refused.get("error") and "confirm_token" not in refused


async def test_one_confirmed_load_through_the_third_check(monkeypatch, browser_page):
    navigator = _Navigator()
    fake = _Browser(browser_page, navigator)
    monkeypatch.setattr(server, "BROWSER", fake)
    block = await server.linkedin_read_named_profile(LINK, section="interests")
    out = await server.linkedin_read_named_profile(LINK, block["confirm_token"], section="interests")
    assert navigator.asks == [(INTERESTS, {"named_profile_details_of": SEGMENT})]
    assert out["landed_on_the_details_page"] is True
    assert out["entries"] is None and "NEEDS-CAPTURE C-NP1" in out["entries_why"]
    assert out["what_the_page_showed"]["group_links"] == 1
    assert "Example Group" not in str(out), "a page string left the details read"
    # ONCE: the same token loads nothing a second time.
    again = await server.linkedin_read_named_profile(LINK, block["confirm_token"], section="interests")
    assert again.get("error") and len(navigator.asks) == 1


async def test_a_token_for_the_profile_loads_no_detail_page_and_back(monkeypatch, browser_page):
    navigator = _Navigator()
    monkeypatch.setattr(server, "BROWSER", _Browser(browser_page, navigator))
    profile_block = await server.linkedin_read_named_profile(LINK)
    crossed = await server.linkedin_read_named_profile(
        LINK, profile_block["confirm_token"], section="interests")
    assert crossed.get("error") and "different" in crossed["message"]
    details_block = await server.linkedin_read_named_profile(LINK, section="skills")
    crossed_back = await server.linkedin_read_named_profile(LINK, details_block["confirm_token"])
    assert crossed_back.get("error")
    other_section = await server.linkedin_read_named_profile(
        LINK, details_block["confirm_token"], section="interests")
    assert other_section.get("error")
    assert navigator.asks == []


async def test_a_landing_elsewhere_reads_nothing(monkeypatch, browser_page):
    navigator = _Navigator(landed=LINK)
    monkeypatch.setattr(server, "BROWSER", _Browser(browser_page, navigator))
    block = await server.linkedin_read_named_profile(LINK, section="interests")
    out = await server.linkedin_read_named_profile(LINK, block["confirm_token"], section="interests")
    assert out["landed_on_the_details_page"] is False
    assert out["what_the_page_showed"] == {} and out["entries"] is None
    assert "landed_why" in out


@pytest.mark.parametrize(
    "landed, same",
    [
        (INTERESTS, True),
        (INTERESTS + "?detailScreenTabIndex=0", True),
        ("https://www.linkedin.com/in/CASEY-EXAMPLE-3F9A/details/interests/", True),
        (LINK, False),
        ("https://www.linkedin.com/in/" + OTHER + "/details/interests/", False),
        (LINK + "details/skills/", False),
        ("http://www.linkedin.com/in/" + SEGMENT + "/details/interests/", False),
        ("", False),
    ],
)
def test_the_landing_is_compared_never_adopted(landed, same):
    assert named_details.landed_on_details(landed, SEGMENT, "interests") is same


# ---------------------------------------------------------------------------
# 5. Who reaches it
# ---------------------------------------------------------------------------


def _package_trees():
    for folder in ("linkedin_server", "scripts"):
        for path in sorted((REPO / folder).rglob("*.py")):
            yield path, ast.parse(path.read_text(encoding="utf-8"))


def test_exactly_one_function_asks_for_the_third_check():
    callers = []
    for path, tree in _package_trees():
        for function in ast.walk(tree):
            if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for node in ast.walk(function):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "goto"
                    and any(kw.arg == "named_profile_details_of" for kw in node.keywords)
                ):
                    callers.append((path.name, function.name))
    assert sorted(set(callers)) == [("named_details.py", "load_the_confirmed_details")]


def test_the_third_check_is_referenced_only_by_the_browser_and_the_details_read():
    users = set()
    for path, tree in _package_trees():
        for node in ast.walk(tree):
            if isinstance(node, (ast.Name, ast.Attribute)):
                name = node.id if isinstance(node, ast.Name) else node.attr
                if name == "assert_named_profile_details_url":
                    users.add(path.name)
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "assert_named_profile_details_url":
                        users.add(path.name)
    assert users == {"browser.py", "named_details.py"}


def test_one_tool_reaches_the_details_load():
    callers = set()
    for path, tree in _package_trees():
        for function in ast.walk(tree):
            if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for node in ast.walk(function):
                if (
                    isinstance(node, ast.Attribute)
                    and node.attr == "load_the_confirmed_details"
                ):
                    callers.add((path.name, function.name))
    assert callers == {("server.py", "linkedin_read_named_profile")}, callers
