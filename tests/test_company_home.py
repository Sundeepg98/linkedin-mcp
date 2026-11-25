"""``linkedin_company_page_home`` -- census row ``J 110`` -- an organisation
Page's own prose, read off the Page root's Home view under the orchestrator's
THIRD-PARTY-TEXT-AT-RUNTIME (2026-10-10): untrusted, sanitised, bounded, never
stored; and the feed items the view drew, as COUNTS.

WHAT IS MEASURED AND WHAT IS NOT. Both fixtures here are REAL captures reduced
to structure by ``scripts/_build_company_home_skeleton.py``:

* ``live1/company_root_home_view.html`` -- a Page root captured 2026-09-23
  that drew its HOME view: the Overview card, its one description box, the
  Page posts section. The description is the builder's declared synthetic
  prose; nobody wrote it.
* ``live9/company_root_posts_view.html`` -- the live lane's session-9 load of
  a Page root, 2026-10-10, through the same admitted root address, which drew
  the POSTS view: no Overview card, thirteen feed items.

Every world that plants something is DERIVED from the Home fixture by an
asserted edit and says so. NOTHING HERE REACHES LINKEDIN: pages are served
into ONE local headless Chromium by ``set_content``, launched once for the
module (a launch per test cost this file 141 s against the two-minute local
cap, measured 2026-10-10), and every reading is taken in that one launch.
"""
from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import sys
from pathlib import Path

import pytest

from linkedin_server import company_home, company_page, dom, people_data, readonly, server
from linkedin_server.config import logger as package_logger

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import _build_company_home_skeleton as builder  # noqa: E402

HOME_FIXTURE = REPO / "tests" / "fixtures" / "live1" / "company_root_home_view.html"
POSTS_FIXTURE = REPO / "tests" / "fixtures" / "live9" / "company_root_posts_view.html"
# LINE ENDINGS NORMALISED: this box checks out with core.autocrlf, which turns
# the builder's "\n" into "\r\n" in a working copy, and the fixed point is a
# claim about the committed text.
HOME = HOME_FIXTURE.read_text(encoding="ascii").replace("\r\n", "\n")
POSTS = POSTS_FIXTURE.read_text(encoding="ascii").replace("\r\n", "\n")
FIXTURES = {"home": HOME, "posts": POSTS}

#: The structure digests the builder printed when it wrote each fixture.
DIGESTS = {"home": "9a2be2f1d3f527c4", "posts": "d5f97e25d747d693"}

#: The synthetic description, as the reader must return it: the builder's two
#: sentences, the line breaks between them collapsed to one space by the
#: sanitiser.
SYNTHETIC_DESCRIPTION = " ".join(builder.SYNTHETIC_PROSE)

ORGANISATION = "1035"
LANDED = "https://www.linkedin.com/company/example-org/"
PROSE_MARKER = "Proseplantmarker"


def _derive(old: str, new: str, source: str = HOME) -> str:
    """An ASSERTED edit: a replace whose anchor drifted is a silent no-op."""
    derived = source.replace(old, new, 1)
    assert derived != source, f"the derivation anchored on {old!r} changed nothing"
    return derived


def _plant_description(markup: str) -> str:
    """The Home fixture with its description box's FIRST run replaced."""
    return _derive(builder.SYNTHETIC_PROSE[0], markup)


LONG_PLANT = "Plantword " * 600  # 6,000 characters
#: Exactly the cap once sanitised: run one, one space, run two.
EXACT_PLANT = "y" * (people_data.PROSE_CAP - len(builder.SYNTHETIC_PROSE[1]) - 1)
SANITISE_PLANT = (
    "Alpha&#x200b;Beta &#x202e;Gamma&#x202c; Delta&#x7;Epsilon\t\tZeta"
    "<script>window.leaked = 'Scriptmarker'</script>"
    "<b>Boldword</b><img alt=\"Imgmarker\">"
    "<button>Buttonmarker</button><span aria-hidden=\"true\">Hiddenmarker</span>"
    "&lt;i&gt;literal&lt;/i&gt;"
)

WORLDS = {
    "home": HOME,
    "posts": POSTS,
    "long": _plant_description(LONG_PLANT),
    "exact": _plant_description(EXACT_PLANT),
    "sanitise": _plant_description(SANITISE_PLANT),
    "two_headings": _derive("<h2>Overview</h2>", "<h2>Overview</h2><h2>Overview</h2>"),
    "tool": _plant_description(PROSE_MARKER + " sentence."),
}


class _Navigator:
    def __init__(self, world: str):
        self.world = world
        self.gotos: list[str] = []

    async def goto(self, page, url, **_ignored):
        self.gotos.append(url)
        await page.set_content(self.world, wait_until="domcontentloaded", timeout=60_000)
        return LANDED


class _Browser:
    def __init__(self, page, navigator):
        self.page = page
        self.navigator = navigator

    @contextlib.asynccontextmanager
    async def session(self):
        yield self.page

    async def goto(self, page, url, **kwargs):
        return await self.navigator.goto(page, url, **kwargs)


class _Heard(logging.Handler):
    """Every record emitted while attached, as text, at every level."""

    def __init__(self):
        super().__init__(logging.DEBUG)
        self.lines: list[str] = []

    def emit(self, record):
        self.lines.append(
            record.getMessage() + " " + str(record.args) + " " + str(record.exc_info)
        )


@contextlib.contextmanager
def _listening():
    heard = _Heard()
    loggers = [logging.getLogger(), logging.getLogger("linkedin")]
    levels = [one.level for one in loggers]
    for one in loggers:
        one.addHandler(heard)
        one.setLevel(logging.DEBUG)
    try:
        yield heard
    finally:
        for one, level in zip(loggers, levels):
            one.removeHandler(heard)
            one.setLevel(level)


async def _take_every_reading() -> dict:
    playwright = pytest.importorskip("playwright.async_api")
    out: dict = {}
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            for name, world in WORLDS.items():
                if name == "tool":
                    continue
                await page.set_content(world, wait_until="domcontentloaded", timeout=60_000)
                out[name] = await dom.read_company_home(page)
            navigator = _Navigator(WORLDS["tool"])
            original = server.BROWSER
            server.BROWSER = _Browser(page, navigator)
            try:
                with _listening() as heard:
                    out["tool"] = await server.linkedin_company_page_home(ORGANISATION)
            finally:
                server.BROWSER = original
            out["tool_gotos"] = list(navigator.gotos)
            out["tool_heard"] = "\n".join(heard.lines)
        finally:
            await browser.close()
    return out


@pytest.fixture(scope="module")
def readings():
    return asyncio.run(_take_every_reading())


# ---------------------------------------------------------------------------
# 1. The fixtures are what the builder makes of the captures
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("kind", ["home", "posts"])
def test_each_fixture_is_the_builders_fixed_point(kind):
    text = FIXTURES[kind]
    again, _counts = builder.build(text, kind=kind)
    assert again == text
    assert builder.structure_digest(text) == DIGESTS[kind]


def test_the_fixtures_hold_no_text_but_kept_words_x_and_the_synthetic_prose():
    allowed = set(builder.KEPT_WORDS) | {"x"} | set(builder.SYNTHETIC_PROSE)
    for text in (HOME, POSTS):
        tree = builder.Tree()
        tree.feed(text)
        tree.close()
        seen = {run for node in builder.walk(tree.root) for run in builder.texts_of(node)}
        assert seen <= allowed, len(seen - allowed)


# ---------------------------------------------------------------------------
# 2. The Home view: the prose, as an untrusted record
# ---------------------------------------------------------------------------


def test_the_home_view_returns_the_overview_prose_marked_untrusted(readings):
    out = readings["home"]
    assert out["view"] == "home"
    assert out["error"] is None
    overview = out["overview"]
    assert overview["state"] == "read", overview["why"]
    assert overview["prose"] == {
        "text": SYNTHETIC_DESCRIPTION,
        "truncated": False,
        "read_from": "overview_card",
        people_data.UNTRUSTED_KEY: people_data.UNTRUSTED_NOTE,
    }
    assert type(people_data.as_record(overview["prose"])) is people_data.OrganisationProse


def test_the_home_view_reports_its_feed_items_as_counts_only(readings):
    out = readings["home"]
    assert out["feed_items"] == {
        "page_posts_sections": 1,
        "page_posts_items": 5,
        "feed_item_headings": 1,
    }
    for value in out["feed_items"].values():
        assert type(value) is int


# ---------------------------------------------------------------------------
# 3. The Posts view the root drew on 2026-10-10: said, never read as empty
# ---------------------------------------------------------------------------


def test_the_posts_view_is_named_and_no_prose_is_invented(readings):
    out = readings["posts"]
    assert out["view"] == "posts"
    assert out["tabs_marked_current"] == 3
    assert out["overview"]["state"] == "not_drawn"
    assert out["overview"]["prose"] is None
    assert "posts view" in out["overview"]["why"]
    assert out["feed_items"] == {
        "page_posts_sections": 0,
        "page_posts_items": 0,
        "feed_item_headings": 13,
    }


# ---------------------------------------------------------------------------
# 4. The mitigations, each driven
# ---------------------------------------------------------------------------


def test_a_long_plant_is_cut_at_the_cap_and_says_so(readings):
    out = readings["long"]
    prose = out["overview"]["prose"]
    assert out["overview"]["state"] == "read"
    assert len(prose["text"]) <= people_data.PROSE_CAP
    assert len(prose["text"]) >= people_data.PROSE_CAP - len("Plantword ")
    assert prose["truncated"] is True


def test_a_text_at_the_cap_is_not_flagged_as_cut(readings):
    prose = readings["exact"]["overview"]["prose"]
    assert len(prose["text"]) == people_data.PROSE_CAP
    assert prose["truncated"] is False


def test_markup_and_control_characters_in_a_plant_are_sanitised(readings):
    out = readings["sanitise"]
    text = out["overview"]["prose"]["text"]
    for invisible in ("\u200b", "\u202e", "\u202c", "\x07", "\t", "\n"):
        assert invisible not in text
    assert "AlphaBeta Gamma DeltaEpsilon Zeta" in text
    assert "Boldword" in text  # an element's TEXT is prose; its tag is not
    for skipped in ("Scriptmarker", "Buttonmarker", "Hiddenmarker", "Imgmarker", "<b>", "<img"):
        assert skipped not in text
    # Markup the page drew AS TEXT stays inert text inside the record.
    assert "<i>literal</i>" in text
    assert out["overview"]["subtrees_skipped"] == 3


def test_two_overview_headings_are_refused_rather_than_one_chosen(readings):
    out = readings["two_headings"]
    assert out["overview"]["state"] == "several_headings"
    assert out["overview"]["prose"] is None


# ---------------------------------------------------------------------------
# 5. Never logged, never in an exception
# ---------------------------------------------------------------------------


def test_the_tool_returns_the_prose_and_logs_none_of_it(readings):
    result = readings["tool"]
    assert result["ok"] is True, result
    assert result["pages_loaded"] == 1
    assert result["redirected"] is True
    assert readings["tool_gotos"] == [company_page.company_page_url(ORGANISATION)["url"]]
    assert PROSE_MARKER in result["overview"]["prose"]["text"]
    assert PROSE_MARKER not in readings["tool_heard"]


class _RaisingPage:
    """A page whose read fails with a library message that QUOTES the prose."""

    async def evaluate(self, *args, **kwargs):
        raise RuntimeError("evaluate failed near: " + PROSE_MARKER + " sentence.")


def _records_text(caplog) -> str:
    return "\n".join(
        record.getMessage() + " " + str(record.args) + " " + str(record.exc_info)
        for record in caplog.records
    )


#: Emitted on the package logger when each capture below is set, and required
#: back out of it: the per-test proof that "no record carries the prose" is
#: read off a channel this package can reach.
_CHANNEL_CONTROL = "caplog control: the package logger is heard at DEBUG"


def set_root_and_package_to_debug(caplog) -> None:
    """``caplog`` at DEBUG on the ROOT logger AND on the package's own logger.

    THE ROOT CALL ALONE NEVER HEARD A DEBUG RECORD FROM THIS PACKAGE, so the two
    absences below passed on a build that logged the prose at DEBUG. Found by
    ``tests/test_a_debug_capture_lowers_the_package_logger.py`` on integration
    2's ci/ run (J 110's branch predates that guard). ``config.py`` gives the
    ``linkedin`` logger a level of its own (INFO unless ``LINKEDIN_LOG_LEVEL``
    says otherwise) and ``propagate = False``, and a logger with a level of its
    own does not inherit the root's; the root call stays for any module that
    logs through ``getLogger(__name__)``. The same helper, for the same reason,
    as ``tests/test_a_preview_names_the_resolved_target.py``'s.
    """
    caplog.set_level(logging.DEBUG)
    caplog.set_level(logging.DEBUG, logger=package_logger.name)
    package_logger.debug(_CHANNEL_CONTROL)
    assert _CHANNEL_CONTROL in caplog.text, (
        "caplog cannot hear the package logger at DEBUG: 'no record carries "
        "the prose' would pass on a line that printed it"
    )


async def test_a_failed_read_carries_no_prose_out_in_a_value_or_a_raise(caplog):
    set_root_and_package_to_debug(caplog)
    out = await dom.read_company_home(_RaisingPage())
    assert out["error"] == "RuntimeError"
    assert out["overview"]["state"] == "reader_blind"
    assert out["overview"]["prose"] is None
    assert PROSE_MARKER not in json.dumps(out)
    assert PROSE_MARKER not in _records_text(caplog)


async def test_the_tool_answers_a_failed_read_without_the_prose(monkeypatch, caplog):
    set_root_and_package_to_debug(caplog)

    class _Raising(_Browser):
        @contextlib.asynccontextmanager
        async def session(self):
            yield _RaisingPage()

        async def goto(self, page, url, **kwargs):
            return LANDED

    monkeypatch.setattr(server, "BROWSER", _Raising(None, None))
    result = await server.linkedin_company_page_home(ORGANISATION)
    assert result["ok"] is True
    assert result["error"] == "RuntimeError"
    assert PROSE_MARKER not in json.dumps(result)
    assert PROSE_MARKER not in _records_text(caplog)


async def test_control_the_raising_page_really_quotes_the_prose():
    """THE TWO ASSERTIONS ABOVE CAN FAIL: the text they hunt is really in the
    exception a careless reader would have let through."""
    with pytest.raises(RuntimeError) as caught:
        await _RaisingPage().evaluate()
    assert PROSE_MARKER in str(caught.value)


# ---------------------------------------------------------------------------
# 6. The address: numeric id from the argument only; the Posts tab refused
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "organisation", ["example-org", "12a4", "", " ", "1" * 21],
    ids=["slug", "mixed", "empty", "blank", "too-long"],
)
async def test_a_non_numeric_id_is_refused_before_any_load(monkeypatch, organisation):
    class _Refusing:
        sessions = 0

        @contextlib.asynccontextmanager
        async def session(self):
            _Refusing.sessions += 1
            raise AssertionError("a session was opened for a refused id")
            yield  # pragma: no cover

        async def goto(self, *args, **kwargs):  # pragma: no cover
            raise AssertionError("a navigation was attempted for a refused id")

    monkeypatch.setattr(server, "BROWSER", _Refusing())
    result = await server.linkedin_company_page_home(organisation)
    assert result["ok"] is False
    assert result["built"] is False
    assert _Refusing.sessions == 0
    if organisation.strip():
        assert organisation.strip() not in json.dumps(result)


def test_the_root_is_admitted_and_the_posts_and_home_tabs_stay_refused():
    root = company_page.company_page_url(ORGANISATION)["url"]
    assert readonly.is_read_url(root) is True
    # ``about/`` WAS THE THIRD NEIGHBOUR UNTIL INTEGRATION 2 (2026-11-24): lane
    # A admitted ``/company/<x>/about/`` on its own anchored line (census
    # ``J 106``, the allowlist-silence clause of READ-PAST-AN-ACT-SUBSTRING), so
    # it is no longer a refused neighbour. ``jobs/`` takes its place: no ruling
    # reaches it, and readonly.py records that ``J 107`` does not need it.
    for tab in ("posts/", "home/", "jobs/"):
        assert readonly.is_read_url(root + tab) is False, tab
    assert readonly.is_read_url("https://www.linkedin.com/company/placeholder-org/posts/") is False


def test_the_view_alphabet_is_closed_and_refuses_out_of_range():
    assert company_home.view_for(2) == "posts"
    assert company_home.view_for(0) == "home"
    assert company_home.view_for(-1) == "no_current_tab"
    assert company_home.view_for(-2) == "tabs_disagree"
    assert company_home.view_for(len(company_home.VIEW_SEGMENTS)) == "position_out_of_range"
    assert company_home.view_for("posts") == "position_out_of_range"
    assert company_home.view_for(True) == "position_out_of_range"
