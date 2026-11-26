"""His resumes-and-application-data page, read over its REAL capture (census P M2).

``application_settings.read_application_settings`` runs over session 11's
capture of ``/jobs/application-settings/`` (load 11), as
``tests/fixtures/live11/application_settings_words.html`` -- the committed
skeleton with LinkedIn's words written where their keyed shapes matched --
through ``tests/skeleton_page.py``, with no browser. The four resume cards'
names and dates are ``x`` in the fixture, as in the capture's tracked copy;
the tests plant SYNTHETIC ones where the capture drew his.

Every name-shaped string in this file is synthetic.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any

import pytest

from linkedin_server import application_settings as aps
from linkedin_server import browser as browser_module
from linkedin_server.errors import ExtractionFailedError
from linkedin_server.server import linkedin_application_settings
from tests.live11_words import plain, plant, words
from tests.plantedpage import PlantedPage
from tests.skeleton_page import SkeletonPage, parse

URL = aps.PAGE_URL
STEM = "application_settings"
_NAME = '<h3 class="ui-attachment__filename jobs-resume-card__filedata">\nx\n</h3>'
_DATE = '<p class="ui-attachment__filesize jobs-resume-card__filedata">\nx\n</p>'

#: A marker no fixture draws: it must never leave, in any field.
MARKER = "Exampleperson Markersurname"

#: Four synthetic resumes, in the capture's order: its two date forms.
RESUMES = [
    ("Example resume.pdf", "Last used on 9/2/2025"),
    ("Example resume two.pdf", "Last used on 10/14/2025"),
    ("Example cv.docx", "Uploaded on 8/30/2025"),
    ("Example cv old.doc", "Uploaded on 1/5/2024"),
]


def settings_markup(resumes=RESUMES) -> str:
    markup = words(STEM)
    head, sep, body = markup.partition("\n-->\n")
    assert body.count(_NAME) == len(resumes) and body.count(_DATE) == len(resumes)
    for name, date in resumes:
        body = body.replace(_NAME, _NAME.replace("\nx\n", "\n" + name + "\n"), 1)
        body = body.replace(_DATE, _DATE.replace("\nx\n", "\n" + date + "\n"), 1)
    return head + sep + body


def run(markup: str) -> tuple[dict[str, Any], SkeletonPage]:
    page = SkeletonPage(PlantedPage(), parse(markup), url=URL)
    return asyncio.run(aps.read_application_settings(page)), page


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


def test_the_page_returns_both_switches_and_every_resume_without_its_name():
    result, page = run(settings_markup())
    assert page.unmodelled == [] and page.planted_answers == []
    assert result["page_heading_drawn"] is True
    assert result["switches"] == {
        "save_resumes_and_answers": "on",
        "share_resume_data_with_hirers": "on",
    }
    assert result["resumes"] == [
        {"file_name": "Example resume.pdf", "type": "pdf", "date_shown": "last_used", "date": "2025-09-02"},
        {"file_name": "Example resume two.pdf", "type": "pdf", "date_shown": "last_used", "date": "2025-10-14"},
        {"file_name": "Example cv.docx", "type": "docx", "date_shown": "uploaded", "date": "2025-08-30"},
        {"file_name": "Example cv old.doc", "type": "doc", "date_shown": "uploaded", "date": "2024-01-05"},
    ]
    assert result["resume_count"] == 4 and result["resume_cards_withheld"] == 0
    assert result["file_control"] == {
        "offered": True, "rule": {"types": ["doc", "docx", "pdf"], "max_megabytes": 5},
    }
    assert result["switch_labels_unrecognised"] == 0 and result["reads_failed"] == 0


def test_a_file_name_leaves_only_as_its_resume_entry_and_sanitised():
    """HIS-OWN-TEXT-AT-RUNTIME: the name he uploaded comes back in its own
    entry's ``file_name`` and nowhere else, its invisible characters removed;
    the options button's label, which repeats it, is never read."""
    planted = [(n.replace("Example", "Example" + chr(0x200B)), d) for n, d in RESUMES]
    result, _ = run(settings_markup(planted))
    assert [r["file_name"] for r in result["resumes"]] == [n for n, _d in RESUMES]
    others = [t for key, value in result.items() if key != "resumes" for t in strings_in(value)]
    assert all("Example" not in text for text in others)
    assert all("Show options" not in text for text in strings_in(result))


def test_a_switch_reads_its_own_input_not_the_one_beside_it():
    """Turn the SECOND switch off on its own input: only its key moves."""
    markup = settings_markup()
    second = 'aria-checked="true" class="input artdeco-toggle__button " data-artdeco-toggle-button="x" id="kf67a4379"'
    markup = plant(markup, second, second.replace('aria-checked="true"', 'aria-checked="false"'))
    result, _ = run(markup)
    assert result["switches"] == {
        "save_resumes_and_answers": "on",
        "share_resume_data_with_hirers": "off",
    }


def test_a_label_bound_to_no_input_reads_unknown():
    markup = plant(settings_markup(), '<label for="kb5e0cfaa"', '<label for="knothere0"')
    result, _ = run(markup)
    assert result["switches"]["save_resumes_and_answers"] == "unknown"


def test_with_its_words_reduced_the_capture_is_a_failed_read():
    """THE CONTROL: the committed copy draws the same markup with its words x."""
    with pytest.raises(ExtractionFailedError):
        run(plain(STEM))


def test_cards_whose_dates_do_not_read_are_withheld_and_the_zero_raises():
    broken = [(n, "recently") for n, _d in RESUMES]
    with pytest.raises(ExtractionFailedError) as caught:
        run(settings_markup(broken))
    assert "4 card(s) seen and withheld" in str(caught.value)


def test_an_unknown_suffix_is_other():
    result, _ = run(settings_markup([("Example notes.txt", d) for _n, d in RESUMES]))
    assert {r["type"] for r in result["resumes"]} == {"other"}


@pytest.mark.parametrize("landed,ok", [
    ("https://www.linkedin.com/jobs/application-settings/", True),
    ("https://www.linkedin.com/jobs/application-settings", True),
    ("https://www.linkedin.com/jobs/application-settings/?trk=x", True),
    ("https://www.linkedin.com/jobs/", False),
    ("https://www.linkedin.com/feed/", False),
    ("http://www.linkedin.com/jobs/application-settings/", False),
    (None, False),
])
def test_the_landing_may_veto(landed, ok):
    assert aps.landed_on_the_page(landed) is ok


# ---------------------------------------------------------------------------
# The tool: one load of the admitted address, the landing checked first
# ---------------------------------------------------------------------------


def _drive(monkeypatch, markup: str, landing: str = URL) -> list[str]:
    navigations: list[str] = []
    page = SkeletonPage(PlantedPage(), parse(markup), url=landing)

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
    navigations = _drive(monkeypatch, settings_markup())
    result = await linkedin_application_settings()
    assert navigations == [URL]
    assert result["ok"] is True and result["pages_loaded"] == 1
    assert result["resume_count"] == 4
    assert result["switches"]["share_resume_data_with_hirers"] == "on"


async def test_a_landing_elsewhere_is_not_read(monkeypatch):
    _drive(monkeypatch, settings_markup(), landing="https://www.linkedin.com/jobs/")
    result = await linkedin_application_settings()
    assert result["ok"] is False and result["refused"] == "landed_off_the_page"
    assert "resumes" not in result
