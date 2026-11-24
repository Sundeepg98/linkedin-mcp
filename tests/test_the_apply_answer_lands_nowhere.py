"""The test navigator's answer to a pressed apply anchor must LAND NOWHERE.

On LinkedIn, the posting's apply anchor is intercepted by LinkedIn's own script,
which opens the apply flow in place. On a frozen capture there is no script, so
pressing it starts a navigation, and ``tests.test_writes.FixtureNavigator``
answers that navigation so nothing leaves the box. The answer must leave the
page ON THE CAPTURE, and leave the page's later reads alive, on every
playwright this suite may resolve -- ``requirements.txt`` leaves playwright
unpinned (``playwright>=1.40``), so CI takes whatever is newest on the day.

MEASURED, the fixes lane, 2026-11-24 (``_audit/2026-10-26-fixes.md``,
section 3). The full-matrix run of master f339459 on 2026-10-26 resolved
playwright 1.64.1, where every earlier run had 1.63.0, and four tests went red
on every platform. The navigator answered ``204 No Content``. Under 1.64.1 a
press whose navigation is answered 204 never resolves -- the click raised
TimeoutError at its full bound -- and the stuck navigation then held the
page's next waits to THEIR full bounds: ``wait_for_job_description`` reported
the description "NEVER ARRIVED" over a capture that carries it, and the
confirm gate refused. Answered ``abort("aborted")``, the press resolved in
under 100 ms and the page stayed on the capture under 1.63.0, 1.64.1 and
1.65.2 alike; ``abort("failed")`` was measured too and replaces the page with
Chromium's error page, so it is not an answer that lands nowhere.

SHOWN FAILING under playwright 1.64.1 with the 204 answer restored: the press
raised TimeoutError at this test's 5 s bound. It passes under 1.63.0 with
either answer, which is why the suite on this box never saw the red.
"""

from __future__ import annotations

import time

from linkedin_server import dom, shape
from tests.test_writes import (  # noqa: F401 -- browser_page is a fixture
    JOB,
    FixtureNavigator,
    browser_page,
    markup,
)

#: The selector ``perform`` presses for a LinkedIn apply, built from the same
#: shipped prefix -- the one the red run's log shows it asked ``page.click``
#: for.
_APPLY_PRESS = f'a[aria-label^="{shape.LINKEDIN_APPLY_PREFIX}"]'


async def test_a_pressed_apply_anchor_lands_nowhere_and_the_page_stays_readable(browser_page):
    posting = f"https://www.linkedin.com/jobs/view/{JOB}/"
    nav = FixtureNavigator({posting: markup("job_detail")})
    await nav.goto(browser_page, posting)
    url_before = browser_page.url

    started = time.monotonic()
    await browser_page.click(_APPLY_PRESS, timeout=5_000, strict=True)
    pressed_ms = int((time.monotonic() - started) * 1000)

    # THE NAVIGATION WAS STARTED AND ANSWERED HERE, and nothing committed.
    assert len(nav.answered) == 1, nav.answered
    assert nav.answered[0].startswith(f"https://www.linkedin.com/jobs/view/{JOB}/apply/")
    assert browser_page.url == url_before, "the answer committed a navigation"
    assert pressed_ms < 4_000, f"the press took {pressed_ms} ms"

    # AND THE PAGE'S LATER READS ARE ALIVE: the capture still carries the
    # description, and the wait finds it at once rather than at its bound.
    verdict = await dom.wait_for_job_description(browser_page)
    assert verdict["attached"] is True, verdict
    assert verdict["waited_ms"] < 2_000, verdict
