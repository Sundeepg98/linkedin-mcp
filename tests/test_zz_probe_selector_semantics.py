"""THROWAWAY. Measure which role-selector name spelling matches a substring."""

import pytest

from tests.test_apply_modal_fixture import VIEWPORT, over  # noqa: F401

HTML = (
    "<html><body>"
    '<div role="listbox">'
    '<div role="option"><span>Thornwick M</span><span>1st</span></div>'
    '<div role="option"><span>Priya Raghunathan</span><span>2nd</span></div>'
    "</div></body></html>"
)

SPELLINGS = [
    'role=option[name="Thornwick M"i]',
    'role=option[name="Thornwick M"]',
    'role=option[name="Thornwick M"s]',
    'role=option[name="Thornwick M 1st"]',
    'role=option[name=/Thornwick M/i]',
    '[role="option"]',
]


@pytest.mark.asyncio
async def test_measure(over):  # noqa: F811
    async def work(page):
        out = {}
        for spelling in SPELLINGS:
            try:
                out[spelling] = await page.locator(spelling).count()
            except Exception as exc:
                out[spelling] = f"RAISED {type(exc).__name__}"
        names = await page.locator('[role="option"]').all_text_contents()
        out["_text"] = names
        return out

    result = await over(HTML, work)
    for key, value in result.items():
        print("   ", repr(key), "->", value)
    assert True
