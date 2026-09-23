"""The profile-views insights reader's FILTERS are the filter pills, not a dialog.

MEASURED 2026-09-23 (`_audit/2026-09-23-readers-four-rows.md` section 2.1), on
a raw capture of `/analytics/profile-views/`, structure only: the page carries
five `<label>` elements. Three sit inside the three filter pills; TWO sit in a
form inside a CLOSED DIALOG in the right rail, and both are short enough to
pass the reader's 40-character cap. The page carries no `data-view-name` at
all, so `PROFILE_VIEWS_INSIGHTS_JS` takes its `<label>` fallback -- and
published all five as "filters", two of them a feedback form's options. Found
independently by the sibling lane L2 on the earlier capture.

The fix skips a label by WHERE it sits (inside `dialog` / `[role="dialog"]`),
never by what it says. These tests run the REAL injected script over synthetic
markup with the capture's shape, in a local headless Chromium that reaches
nothing outside this machine. Every string in the markup is synthetic UI text.
"""
from __future__ import annotations

import pytest

from linkedin_server import dom

PILLS = ("Past 90 days", "Interesting viewers", "Company")


def _page(dialog_open_tag: str, dialog_close_tag: str) -> str:
    pills = "".join(
        f'<div role="button" aria-expanded="false"><div>'
        f'<label for="f{i}">{caption}</label></div></div>'
        for i, caption in enumerate(PILLS)
    )
    return (
        "<html><body>"
        '<header><nav><button aria-expanded="false">Me</button></nav></header>'
        "<main>"
        "<p>27</p><p>Profile viewers</p>"
        f"{pills}"
        "<aside>"
        f"{dialog_open_tag}<form>"
        '<label for="r1">Not relevant to my work</label>'
        '<label for="r2">Shown to me too often</label>'
        f"</form>{dialog_close_tag}"
        "</aside>"
        "</main></body></html>"
    )


async def _insights(html: str) -> dict:
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return await dom.read_profile_views_insights(page)
        finally:
            await browser.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "opening, closing",
    [
        ("<dialog>", "</dialog>"),
        ('<div role="dialog" aria-hidden="true">', "</div>"),
    ],
    ids=["dialog-element", "role-dialog"],
)
async def test_a_label_inside_a_dialog_is_not_a_filter(opening, closing):
    insights = await _insights(_page(opening, closing))
    assert insights["filters"] == list(PILLS), insights["filters"]


@pytest.mark.asyncio
async def test_the_control_the_same_labels_outside_a_dialog_are_still_read():
    """THE CONTROL. Without it a reader that dropped EVERY label outside the
    pills would pass the test above: the same two form labels, NOT in a
    dialog, must still be read -- the rule is about the dialog and nothing
    else."""
    insights = await _insights(_page("<section>", "</section>"))
    assert insights["filters"][: len(PILLS)] == list(PILLS), insights["filters"]
    assert len(insights["filters"]) == len(PILLS) + 2, insights["filters"]
