"""His Premium networking matches (census ``N 199``), read on live session 12's capture.

THE PAGE IS REAL: the live lane's session-12 capture of ``/premium/matches/``
(load 26, served exact), its tracked copy
``tests/fixtures/live12/premium_matches.html`` with LinkedIn's two words on each
card's job line put back by keyed shape --
``tests/fixtures/synthetic/live12_premium_matches_words.html``
(``scripts/_build_live12_net7_word_skeletons.py``). Every name, headline, title
and organisation is the skeleton's ``x``; a test that needs a member plants a
SYNTHETIC one into the markup LinkedIn drew, by an asserted edit:

* the capture as drawn -> two cards seen, both links the skeleton's one ``x``
  slug, so one person and one ``already_returned``;
* two synthetic members planted -> two records, each beside its job's id;
* the TRACKED COPY, LinkedIn's words reduced to ``x`` -> no card, it raises:
  the reader is aimed by those words and nothing else finds a card;
* ``Hiring for`` taken off one card -> that card is not seen;
* a second member link in one card -> that card is not read;
* a name in every name slot -> back inside the records only;
* a name in every label and in the Message link -> the answer is identical.

NOTHING HERE REACHES LINKEDIN: a local headless Chromium over ``set_content``,
every request refused first.
"""
from __future__ import annotations

import asyncio
import contextlib
import re
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import people_data, premium_matches, readonly
from linkedin_server.errors import ExtractionFailedError
from tests.plantedpage import PLANT, carries_the_plant_outside_records
from tests.test_writes import browser_page  # noqa: F401 -- fixture

REPO = Path(__file__).resolve().parents[1]
WORDS = REPO / "tests" / "fixtures" / "synthetic" / "live12_premium_matches_words.html"
TRACKED = REPO / "tests" / "fixtures" / "live12" / "premium_matches.html"

MEMBER_X = 'href="https://www.linkedin.com/in/x/"'
JOB_X = 'href="https://www.linkedin.com/jobs/view/x/"'
SPAN_X = "<span>\nx\n</span>"

#: Synthetic members: slugs and names naming nobody.
ONE = ("example-member-one", "Exampleone Syntheticperson", "Example headline one", "4000000001")
TWO = ("example-member-two", "Exampletwo Syntheticperson", "Example headline two", "4000000002")


async def _refused(route: Any) -> None:
    await route.abort()


async def _read(page: Any, html: str) -> dict[str, Any]:
    await page.route("**/*", _refused)
    await page.set_content(html, wait_until="domcontentloaded")
    return await premium_matches.read_matches(page)


def _text(path: Path = WORDS) -> str:
    return path.read_text(encoding="ascii")


def _plant_card(html: str, slug: str, name: str, headline: str, job_id: str,
                degree: str = "· 2nd") -> str:
    """Plant one synthetic member into the FIRST card not yet planted -- its
    link, its three lines and its job's id -- each edit asserted to land
    exactly once. Called twice, it plants both of the capture's cards."""
    starts = [m.start() for m in re.finditer(re.escape(MEMBER_X), html)]
    assert starts, "no unplanted member link is left on the page"
    start = starts[0]
    end = html.index("</a>", start)
    region = html[start:end]
    assert region.count(SPAN_X) == 2, "a member link draws a name and a headline line"
    degree_line = re.compile(r'(<p class="[^"]*">\n)x(\n</p>)')
    assert len(degree_line.findall(region)) == 1, "a member link draws one degree line"
    region = region.replace(MEMBER_X, f'href="https://www.linkedin.com/in/{slug}/"', 1)
    region = region.replace(SPAN_X, f"<span>\n{name}\n</span>", 1)
    region = degree_line.sub(lambda m: m.group(1) + degree + m.group(2), region, count=1)
    region = region.replace(SPAN_X, f"<span>\n{headline}\n</span>", 1)
    html = html[:start] + region + html[end:]
    # THE CARD'S JOB LINK follows its member link: the first one after it.
    target = html.index(JOB_X, start)
    return html[:target] + f'href="https://www.linkedin.com/jobs/view/{job_id}/"' + html[target + len(JOB_X):]


def _both(html: str | None = None) -> str:
    html = _plant_card(_text() if html is None else html, *ONE)
    return _plant_card(html, *TWO)


def _record(slug: str, name: str, headline: str, degree: str = "2nd") -> dict[str, Any]:
    return {"name": name, "headline": headline, "link": f"https://www.linkedin.com/in/{slug}/",
            "degree": degree, people_data.UNTRUSTED_KEY: people_data.UNTRUSTED_NOTE}


# ---------------------------------------------------------------------------
# The capture as drawn, and as planted
# ---------------------------------------------------------------------------


def test_the_capture_draws_two_cards_by_linkedins_words() -> None:
    """The premise: two job links whose line opens ``Hiring for``, two member
    links, and the two words only in the words fixture."""
    words = _text()
    assert words.count(MEMBER_X) == 2 and words.count(JOB_X) == 2
    assert words.count(">\nHiring for\n<") == 2 and words.count(">\nat\n<") == 2
    tracked = _text(TRACKED)
    assert "Hiring for" not in tracked


async def test_the_capture_as_drawn_reads_one_person_and_counts_the_other(browser_page):
    out = await _read(browser_page, _text())
    assert out["refused"] is None
    assert (out["cards_seen"], out["cards_attempted"]) == (2, 2)
    # Both member links are the skeleton's one ``x`` slug: one person, once.
    assert out["matches"] == [{"person": _record("x", "x", "x", None), "hiring_for_job_id": None}]
    assert out["skipped"]["already_returned"] == 1
    assert out["readable"] is True


async def test_each_match_comes_back_as_a_person_beside_its_job(browser_page):
    out = await _read(browser_page, _both())
    assert out["matches"] == [
        {"person": _record(*ONE[:3]), "hiring_for_job_id": ONE[3]},
        {"person": _record(*TWO[:3]), "hiring_for_job_id": TWO[3]},
    ]
    assert out["skipped"] == {reason: 0 for reason in premium_matches.SKIP_REASONS}
    assert out["failed"] == {} and out["headline_unread"] == 0


async def test_the_tracked_copy_without_linkedins_words_finds_no_card(browser_page):
    """THE RED FOR A WORD-AIMED READER: the same page with ``Hiring for``
    reduced to ``x`` draws no card this reader can find, and it raises."""
    with pytest.raises(ExtractionFailedError):
        await _read(browser_page, _text(TRACKED))


async def test_a_card_whose_line_does_not_open_hiring_for_is_not_seen(browser_page):
    html = _both().replace(">\nHiring for\n<", ">\nx\n<", 1)
    out = await _read(browser_page, html)
    assert out["cards_seen"] == 1
    assert [m["hiring_for_job_id"] for m in out["matches"]] == [TWO[3]]


async def test_no_card_raises(browser_page):
    html = _both().replace(">\nHiring for\n<", ">\nx\n<")
    with pytest.raises(ExtractionFailedError):
        await _read(browser_page, html)


async def test_a_card_with_a_second_member_link_is_not_read(browser_page):
    html = _both()
    # A SECOND MEMBER LINK BESIDE THE FIRST, inside the first card's own block:
    # the first member link's end, then another member's link.
    first_member = html.index("https://www.linkedin.com/in/" + ONE[0] + "/")
    cut = html.index("</a>", first_member) + len("</a>")
    html = html[:cut] + '<a href="https://www.linkedin.com/in/example-member-three/">x</a>' + html[cut:]
    out = await _read(browser_page, html)
    assert out["skipped"]["not_one_member_link"] == 1
    assert [m["hiring_for_job_id"] for m in out["matches"]] == [TWO[3]]


# ---------------------------------------------------------------------------
# What never crosses
# ---------------------------------------------------------------------------


async def test_a_members_name_comes_back_only_inside_a_record(browser_page):
    html = _plant_card(_text(), ONE[0], PLANT, ONE[2], ONE[3])
    html = _plant_card(html, TWO[0], PLANT, TWO[2], TWO[3])
    out = await _read(browser_page, html)
    assert {m["person"]["name"] for m in out["matches"]} == {PLANT}
    outside, records = carries_the_plant_outside_records(out)
    assert outside == [] and records > 0


async def test_a_name_in_every_label_and_the_message_link_is_never_read(browser_page):
    plain = await _read(browser_page, _both())
    planted_html = (
        _both()
        .replace('alt="x"', f'alt="{PLANT}"')
        .replace('aria-label="x"', f'aria-label="{PLANT}"')
        .replace("recipient=x", "recipient=" + PLANT.replace(" ", "-"))
    )
    assert planted_html != _both()
    planted = await _read(browser_page, planted_html)
    assert planted == plain


async def test_the_title_and_organisation_never_cross(browser_page):
    html = re.sub(r"(<strong[^>]*>\n)x(\n</strong>)", lambda m: m.group(1) + PLANT + m.group(2), _both())
    assert html.count(PLANT) == 4
    out = await _read(browser_page, html)
    outside, _records = carries_the_plant_outside_records(out)
    assert outside == []
    assert PLANT not in str(out)


# ---------------------------------------------------------------------------
# The pure parts
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("landed, expected", [
    ("https://www.linkedin.com/premium/matches/", True),
    ("https://www.linkedin.com/premium/matches", True),
    ("https://www.linkedin.com/premium/matches/?trk=x", True),
    ("https://www.linkedin.com/premium/", False),
    ("https://www.linkedin.com/premium/matches/more/", False),
    ("http://www.linkedin.com/premium/matches/", False),
    ("", False),
    (None, False),
])
def test_the_landing_is_the_matches_page_itself(landed, expected) -> None:
    assert premium_matches.landed_on_the_matches(landed) is expected


@pytest.mark.parametrize("href, expected", [
    ("https://www.linkedin.com/jobs/view/4000000001/", "4000000001"),
    ("/jobs/view/12/", "12"),
    ("https://www.linkedin.com/jobs/view/x/", None),
    ("https://www.linkedin.com/jobs/view/12/more/", None),
    ("", None),
    (None, None),
])
def test_a_job_id_is_the_digits_of_its_link(href, expected) -> None:
    assert premium_matches.job_id_of(href) == expected


def test_the_address_is_admitted_and_the_module_never_navigates() -> None:
    assert readonly.is_read_url(premium_matches.MATCHES_URL) is True
    source = (REPO / "linkedin_server" / "premium_matches.py").read_text(encoding="utf-8")
    for call in ("goto(", ".click(", ".press(", ".fill(", ".type(", ".scroll", "mouse.wheel", ".hover("):
        assert call not in source, call


# ---------------------------------------------------------------------------
# The tool
# ---------------------------------------------------------------------------


class _ServingBrowser:
    """One session over the given page; goto serves ``html`` and lands at ``landing``."""

    def __init__(self, page: Any, html: str, landing: str) -> None:
        self.page, self.html, self.landing = page, html, landing
        self.gotos: list[str] = []

    def session(self):
        @contextlib.asynccontextmanager
        async def _session():
            yield self.page

        return _session()

    async def goto(self, page: Any, url: str) -> str:
        readonly.assert_read_url(url)
        self.gotos.append(url)
        await page.route("**/*", _refused)
        await page.set_content(self.html, wait_until="domcontentloaded")
        return self.landing


async def test_the_tool_loads_the_one_address_and_returns_the_matches(browser_page, monkeypatch):
    from linkedin_server import server

    browser = _ServingBrowser(browser_page, _both(), premium_matches.MATCHES_URL)
    monkeypatch.setattr(server, "BROWSER", browser)
    out = await server.linkedin_premium_matches()
    assert browser.gotos == [premium_matches.MATCHES_URL]
    assert [m["hiring_for_job_id"] for m in out["matches"]] == [ONE[3], TWO[3]]


async def test_the_tool_refuses_a_landing_elsewhere(browser_page, monkeypatch):
    from linkedin_server import server

    browser = _ServingBrowser(browser_page, _both(), "https://www.linkedin.com/premium/")
    monkeypatch.setattr(server, "BROWSER", browser)
    out = await server.linkedin_premium_matches()
    assert out["refused"] == "landed_elsewhere" and out["matches"] == []


# ---------------------------------------------------------------------------
# The census: N 199 moved on its own cell's bar, and off every GAP table
# ---------------------------------------------------------------------------


def test_n199_is_covered_unfired_on_this_reader_and_off_every_gap_table() -> None:
    import sys as _sys

    network = REPO / "_audit" / "_census" / "network.md"
    row = next(line for line in network.read_text(encoding="utf-8").splitlines()
               if line.split("|")[1:2] == [" 199 "])
    cells = row.split("|")
    assert cells[4].strip() == "COVERED-UNFIRED"
    paragraph = cells[5][cells[5].index("**LANE NET7, 2026-11-27"):]
    for words in ("NOT FIRED -- COVERED-UNFIRED", "`linkedin_premium_matches()`",
                  "tests/fixtures/synthetic/live12_premium_matches_words.html",
                  "tests/test_premium_matches.py", "NAMES-AT-RUNTIME",
                  "WHO-WHICH-COUNTS-ARE-NOT-DELIVERY", "_audit/2026-11-27-net7.md"):
        assert words in paragraph, words
    census = REPO / "_audit" / "_census"
    assert not any(line.startswith("N 199\t") for line in
                   (census / "next-step.tsv").read_text(encoding="utf-8").splitlines())
    assert not any(line.startswith("N\t199\t") for line in
                   (census / "read-addresses.tsv").read_text(encoding="utf-8").splitlines())
    assert "admit-premium-matches" not in (census / "capture-queue.tsv").read_text(encoding="utf-8")
    _sys.path.insert(0, str(REPO / "scripts"))
    import census_completion as cc  # noqa: PLC0415
    import triage_read_gap_rows as triage  # noqa: PLC0415

    assert "N 199" not in triage.TRIAGE
    assert "N 199" in cc.PINNED_B1_ROWS[cc.NO_RULING]
