"""His Advertising data settings page (census ``P P15``), read on live session 11's capture.

THE PAGE IS REAL: ``tests/fixtures/synthetic/live11_ads_words.html`` is the
live lane's session-11 tracked copy (``tests/fixtures/live11/ads.html``, load
10) with LinkedIn's own address words put back where the keyed shape proves
them (``scripts/_build_live11_word_fixtures.py``). The tracked copy writes
every setting's address word as ``x``; ``On`` it keeps, being on the harness's
closed list.

THE PLANTS: the tracked copy itself (no setting is named: it raises); a
seventeenth setting link under a word nobody measured (counted, never named);
an ``Off`` line (read as off).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from linkedin_server import advertising_data as ad
from linkedin_server.errors import ExtractionFailedError
from tests.test_writes import browser_page  # noqa: F401 -- fixture

REPO = Path(__file__).resolve().parents[1]
WORDS = REPO / "tests" / "fixtures" / "synthetic" / "live11_ads_words.html"
COPY = REPO / "tests" / "fixtures" / "live11" / "ads.html"


async def _refused(route: Any) -> None:
    await route.abort()


async def _read(page: Any, html: str) -> dict[str, Any]:
    await page.route("**/*", _refused)
    await page.set_content(html, wait_until="domcontentloaded")
    return await ad.read_advertising_data(page)


def _text(path: Path) -> str:
    return path.read_text(encoding="ascii")


#: What the page drew, in its own order: (setting, state).
DRAWN = [
    ("ads-connections", "on"), ("ads-companies-followed", "on"), ("ads-based-on-groups", "on"),
    ("ads-education", "other"), ("ads-job-information", "other"), ("ads-employer", "other"),
    ("ads-personalization", "on"), ("ads-location", "on"), ("ads-inferred-location", "on"),
    ("interest-categories", "none"), ("ads-by-age", "on"), ("ads-by-gender", "on"),
    ("ads-beyond-linkedin", "on"), ("ads-interactions-with-business", "on"),
    ("ads-related-actions", "on"), ("share-data-with-select-partners", "on"),
]


async def test_the_page_reads_its_sixteen_settings_and_their_states(browser_page):
    out = await _read(browser_page, _text(WORDS))
    assert out["refused"] is None
    assert out["setting_links_seen"] == 16 and out["unknown_settings"] == 0
    assert [(s["setting"], s["state"]) for s in out["settings"]] == DRAWN
    assert [s["section"] for s in out["settings"]] == (
        ["profile_data"] * 8 + ["activity_and_inferred_data"] * 4 + ["off_linkedin_data"] * 4
    )
    assert out["states"] == {"on": 12, "off": 0, "other": 3, "none": 1}
    assert out["form_controls_in_main"] == 0
    assert out["readable"] is True


async def test_the_tracked_copy_names_no_setting_and_raises(browser_page):
    """THE RED: without LinkedIn's address words no link names a setting."""
    with pytest.raises(ExtractionFailedError):
        await _read(browser_page, _text(COPY))


async def test_a_setting_under_an_unmeasured_word_is_counted_and_never_named(browser_page):
    html = _text(WORDS)
    cut = html.index("</main>")
    planted = ('<a href="https://www.linkedin.com/mypreferences/m/settings/ads-somethingunmeasured/">'
               "<p>x</p><p><span>On</span></p></a>")
    out = await _read(browser_page, html[:cut] + planted + html[cut:])
    assert out["setting_links_seen"] == 17 and out["unknown_settings"] == 1
    assert "ads-somethingunmeasured" not in repr(out)
    assert len(out["settings"]) == 16


async def test_an_off_line_reads_off(browser_page):
    html = _text(WORDS)
    first_on = html.index(">\nOn\n<", html.index("ads-connections"))
    html = html[:first_on] + ">\nOff\n<" + html[first_on + len(">\nOn\n<"):]
    out = await _read(browser_page, html)
    assert out["settings"][0] == {"setting": "ads-connections", "section": "profile_data", "state": "off"}
    assert out["states"]["off"] == 1 and out["states"]["on"] == 11


@pytest.mark.parametrize(
    ("href", "setting"),
    [
        ("https://www.linkedin.com/mypreferences/m/settings/ads-connections/", "ads-connections"),
        ("/mypreferences/d/settings/ads-by-age", "ads-by-age"),
        ("https://www.linkedin.com/mypreferences/m/interest-categories/", "interest-categories"),
        ("https://www.linkedin.com/mypreferences/m/settings/ads-unknown/", None),
        ("https://www.linkedin.com/mypreferences/d/categories/ads/", None),
        ("https://www.linkedin.com/mypreferences/d/unfollowed/", None),
        ("https://example.com/mypreferences/m/settings/ads-connections/", None),
        (None, None),
    ],
)
def test_a_setting_is_named_only_by_a_measured_word(href, setting):
    assert ad.setting_of(href) == setting


def test_every_setting_has_one_measured_section():
    assert set(ad.SECTION_OF.values()) == set(ad.SECTIONS)
    assert len(ad.SETTINGS) == 16 == len(set(ad.SETTINGS))


def test_the_landing_is_the_page_itself():
    assert ad.landed_on_the_page("https://www.linkedin.com/mypreferences/d/categories/ads/")
    assert ad.landed_on_the_page("https://www.linkedin.com/mypreferences/d/categories/ads")
    assert not ad.landed_on_the_page("https://www.linkedin.com/mypreferences/d/categories/privacy/")
    assert ad.landed_elsewhere()["refused"] == "landed_elsewhere"


def test_the_module_presses_nothing():
    source = (REPO / "linkedin_server" / "advertising_data.py").read_text(encoding="utf-8")
    for call in (".click(", ".fill(", ".press(", ".check(", ".tap(", "open(", "logging", ".goto("):
        assert call not in source, call
