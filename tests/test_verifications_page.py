"""His Verifications settings page, read over its REAL capture (census P K1).

``verifications_page.read_verifications`` runs over session 12's capture of
``/mypreferences/d/verifications`` (load 15, served exact), as
``tests/fixtures/live12/verifications_words.html`` -- the committed skeleton
with LinkedIn's words written where their keyed shapes matched
(``scripts/_build_live12_settings_word_skeletons.py``) -- through
``tests/skeleton_page.py``, with no browser. The verification's three detail
lines are ``x`` in the fixture, as in the capture's tracked copy; where a test
needs text there it plants a SYNTHETIC marker.

Every name-shaped string in this file is synthetic.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import verifications_page as vp
from linkedin_server.errors import ExtractionFailedError
from linkedin_server.server import linkedin_my_verifications
from tests.live11_words import plant
from tests.plantedpage import PlantedPage
from tests.skeleton_page import SkeletonPage, parse

URL = vp.VERIFICATIONS_URL
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "live12" / "verifications_words.html"

#: A marker no fixture draws: it must never leave, in any field.
MARKER = "Exampleperson Markersurname"

_KIND = '<h3 class="text-body-small-bold t-black">\nWorkplace\n</h3>'
_DETAIL = '<p class="text-body-small t-black">\nx\n</p>'
_STATE = '<span class=" _toggle-text_12ycew" aria-hidden="true" id="k1c3e3fd3">\nOn\n</span>'
_SWITCH = '<input class="_switchCheckbox_12ycew" aria-label="x" role="switch" type="checkbox">'
_DELETE_WORD = "<span class=\"_text_ddl063 _text_ps32ck\">\nDelete\n</span>"
_CONTAINER = 'data-test-verifications-evidences-container=""'
_CONSENT = 'data-test-verifications-evidences-work-email-consent-toggle=""'
_HEADING = 'data-test-header-title="">\nVerifications\n</h1>'


def markup() -> str:
    return FIXTURE.read_text(encoding="ascii")


def run(text: str) -> tuple[dict[str, Any], SkeletonPage]:
    page = SkeletonPage(PlantedPage(), parse(text), url=URL)
    return asyncio.run(vp.read_verifications(page)), page


def strings_in(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from strings_in(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from strings_in(item)


def test_the_capture_reads_one_workplace_verification_with_its_switch_on_and_delete_drawn():
    result, page = run(markup())
    assert page.unmodelled == [] and page.planted_answers == []
    assert result["refused"] is None
    assert result["page_heading_drawn"] is True
    assert result["verifications"] == [{
        "kind": "workplace",
        "detail_lines": 3,
        "work_email_consent": "on",
        "delete_drawn": True,
    }]
    assert result["entries_seen"] == 1
    assert result["unknown_kinds"] == 0 and result["entries_withheld"] == 0
    assert result["readable"] is True


def test_no_text_of_the_page_leaves_even_where_a_marker_is_planted():
    """The detail lines are his (an employer may be among them), the switch's
    name and the helper lines are LinkedIn's long copy: none is returned."""
    text = plant(markup(), _DETAIL, _DETAIL.replace("\nx\n", "\n" + MARKER + "\n"), count=3)
    text = plant(text, _SWITCH, _SWITCH.replace('aria-label="x"', 'aria-label="%s"' % MARKER))
    result, page = run(text)
    assert page.unmodelled == []
    assert result["verifications"][0]["detail_lines"] == 3
    for value in strings_in(result):
        assert MARKER not in value and "Exampleperson" not in value


def test_a_kind_this_server_has_not_measured_is_counted_and_never_named():
    result, _ = run(plant(markup(), _KIND, _KIND.replace("Workplace", "Placeholder kind")))
    assert result["verifications"][0]["kind"] == "other"
    assert result["unknown_kinds"] == 1
    assert all("Placeholder" not in value for value in strings_in(result))


def test_off_reads_off():
    result, _ = run(plant(markup(), _STATE, _STATE.replace("\nOn\n", "\nOff\n")))
    assert result["verifications"][0]["work_email_consent"] == "off"


def test_a_state_word_that_is_neither_reads_unknown():
    result, _ = run(plant(markup(), _STATE, _STATE.replace("\nOn\n", "\nPending\n")))
    assert result["verifications"][0]["work_email_consent"] == "unknown"


def test_a_second_switch_in_the_section_reads_unknown_never_the_first():
    result, page = run(plant(markup(), _SWITCH, _SWITCH + "\n" + _SWITCH))
    assert page.unmodelled == []
    assert result["verifications"][0]["work_email_consent"] == "unknown"


def test_an_entry_with_no_consent_section_reads_none():
    result, _ = run(plant(markup(), _CONSENT, 'data-test-placeholder-section=""'))
    assert result["verifications"][0]["work_email_consent"] is None


# 2026-11-27, the cold verification of lane settings7 (its F3): two or more
# consent sections, and a section count that could not be read, both came back
# None -- the word for "no consent section". Each is its own closed word now.
_DELETE_SECTION = (
    '<div class="verifications-evidences__delete-evidence" '
    'data-test-verifications-delete-evidence="">'
)


def test_two_consent_sections_read_as_several_never_as_none():
    second = '<div data-test-verifications-evidences-work-email-consent-toggle="">\n</div>\n'
    result, page = run(plant(markup(), _DELETE_SECTION, second + _DELETE_SECTION))
    assert page.unmodelled == []
    assert result["verifications"][0]["work_email_consent"] == "several_sections"


class _UnreadableSections:
    """A container whose consent-section count raises, as a detached page would."""

    def locator(self, selector: str) -> "_UnreadableSections":
        return self

    async def count(self) -> int:
        raise RuntimeError("placeholder failure")


def test_a_consent_count_that_cannot_be_read_says_unread_never_none():
    failed = [0]
    assert asyncio.run(vp._consent(_UnreadableSections(), failed)) == "unread"
    assert failed == [1]


def test_each_consent_reading_is_a_closed_word_and_none_means_no_section():
    assert vp.CONSENT_READINGS == ("on", "off", "unknown", "several_sections", "unread")
    assert None not in vp.CONSENT_READINGS


def test_delete_is_drawn_only_when_its_own_word_is():
    result, _ = run(plant(markup(), _DELETE_WORD, _DELETE_WORD.replace("Delete", "Remove")))
    assert result["verifications"][0]["delete_drawn"] is False


def test_a_container_holding_two_entries_is_withheld_and_the_zero_raises():
    """Pairing a switch and a Delete to the right verification is measured only
    for ONE entry per container; two make the pairing a guess."""
    content = '<div class="verifications-evidences__content" data-test-verifications-evidences="">'
    text = plant(markup(), content, content + "\n" + _KIND + "\n</div>\n" + content)
    with pytest.raises(ExtractionFailedError) as caught:
        run(text)
    assert "1 entry" in str(caught.value) and "withheld" in str(caught.value)


def test_no_entry_drawn_is_a_failure_not_an_empty_list():
    with pytest.raises(ExtractionFailedError):
        run(plant(markup(), _CONTAINER, 'data-test-placeholder-container=""'))


def test_a_page_without_its_heading_is_not_read():
    with pytest.raises(ExtractionFailedError):
        run(plant(markup(), _HEADING, _HEADING.replace("Verifications", "Placeholder")))


def test_a_page_with_two_main_regions_refuses():
    text = markup().replace("</main>", "</main>\n<main>\n</main>", 1)
    result, _ = run(text)
    assert result["refused"] == "main_unreadable" and result["verifications"] == []


@pytest.mark.parametrize("landed, ok", [
    ("https://www.linkedin.com/mypreferences/d/verifications", True),
    ("https://www.linkedin.com/mypreferences/d/verifications/", True),
    ("https://www.linkedin.com/mypreferences/d/two-step-verification", False),
    ("https://www.linkedin.com/mypreferences/d/", False),
    ("http://www.linkedin.com/mypreferences/d/verifications", False),
    ("https://example.com/mypreferences/d/verifications", False),
    (None, False),
])
def test_the_landing_may_veto(landed, ok):
    assert vp.landed_on_the_page(landed) is ok


# ---------------------------------------------------------------------------
# The tool: one load of the admitted address, the landing checked first
# ---------------------------------------------------------------------------


def _drive(monkeypatch, text: str, landing: str = URL) -> list[str]:
    navigations: list[str] = []
    page = SkeletonPage(PlantedPage(), parse(text), url=landing)

    @asynccontextmanager
    async def fake_session():
        yield page

    async def fake_goto(target_page, url, **kwargs):
        navigations.append(url)
        return landing

    monkeypatch.setattr(browser_module.BROWSER, "session", fake_session)
    monkeypatch.setattr(browser_module.BROWSER, "goto", fake_goto)
    return navigations


async def test_the_tool_loads_the_one_admitted_address_and_reads_it(monkeypatch):
    navigations = _drive(monkeypatch, markup())
    result = await linkedin_my_verifications()
    assert navigations == [URL]
    assert result["verifications"][0]["kind"] == "workplace"
    assert result["refused"] is None


async def test_a_landing_elsewhere_is_not_read(monkeypatch):
    _drive(monkeypatch, markup(), landing="https://www.linkedin.com/feed/")
    result = await linkedin_my_verifications()
    assert result["refused"] == "landed_elsewhere"
    assert result["verifications"] == []
