"""Five bounded waits read their own duration so that it never falls short of
the bound the driver enforced.

WHY. Lane ci8 found the tracker wait's "999 < 1000" flake (lane CI run
45970717983; ``tests/test_tracker_readiness.py`` section 2b). Two faults met in
it. Playwright's driver ends a wait on Node's whole-millisecond clock, so in
real time a wait can end anywhere in its bound's last millisecond, and the
reading truncated with ``int(...)``. And ``time.monotonic()`` is
GetTickCount64, a 15.625 ms clock, on Windows before Python 3.13, while
``time.perf_counter()`` is QueryPerformanceCounter on every version. The
tracker wait was fixed first. These are the five siblings whose readings are
SET BESIDE THEIR BOUND, each now read on ``perf_counter`` and rounded up:

* ``dom.wait_for_save_control``: the refusal prints "Nms of a Mms wait";
* ``dom.wait_for_job_description``: the note prints "(Nms, the full bound)";
* ``attachments.wait_for_attachment_drawn``: the time spent is subtracted
  from the bound, to give the second wait only what is left of it;
* ``named_profile.wait_for_send_enabled`` and
  ``threads.wait_for_reply_send_enabled``: their tests assert that a wait
  which never turned on spent its bound.

Two siblings are LEFT, because nothing sets their reading beside their bound:
``named_profile.wait_for_opened_composer`` (recorded as ``composer_waited_ms``;
its one test reads it against the page's 600 ms draw delay) and
``named_profile.wait_for_sent_words`` (its one test asserts a non-negative int).

HOW. Each wait runs against a page whose ``wait_for`` advances a VIRTUAL
clock, the one the module reads, by a scripted amount, and then returns or
raises Playwright's own ``TimeoutError``. No browser, no sleep. Every case
here failed before the fix and passes after it.
"""

from __future__ import annotations

import pytest

from linkedin_server import attachments, dom, named_profile, threads

#: The tick of GetTickCount64, Python's monotonic clock on Windows before 3.13.
TICK = 0.015625


class _VirtualClock:
    """Stands in for a module's ``time``. ``now`` is the true instant, in
    seconds; ``monotonic()`` can read it floored to whole ticks, the way
    GetTickCount64 does, and ``perf_counter()`` always reads it fine."""

    def __init__(self, start: float, tick: float = 0.0):
        self.now = start
        self._tick = tick
        self.reads = 0

    def perf_counter(self) -> float:
        self.reads += 1
        return self.now

    def monotonic(self) -> float:
        self.reads += 1
        return (self.now // self._tick) * self._tick if self._tick else self.now

    def __getattr__(self, name):
        import time

        return getattr(time, name)


class _Page:
    """Every locator chain the five waits build, ending in a ``wait_for``
    that takes the next scripted step: advance the clock by ``seconds``, then
    return, or raise the driver's TimeoutError. Every timeout handed to it is
    kept, so a test can read the budget a wait was given."""

    def __init__(self, clock: _VirtualClock, steps):
        self._clock = clock
        self._steps = list(steps)
        self.timeouts: list[float] = []

    def locator(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def get_by_text(self, *args, **kwargs):
        return self

    @property
    def first(self):
        return self

    async def wait_for(self, **kwargs):
        from playwright.async_api import TimeoutError as DriverTimeout

        self.timeouts.append(kwargs.get("timeout"))
        seconds, times_out = self._steps.pop(0)
        self._clock.now += seconds
        if times_out:
            raise DriverTimeout("Timeout %sms exceeded." % kwargs.get("timeout"))


async def _save_control(page, bound, monkeypatch):
    return await dom.wait_for_save_control(page, bound)


async def _job_description(page, bound, monkeypatch):
    monkeypatch.setattr(dom, "JOB_DESCRIPTION_TIMEOUT_MS", bound)
    return await dom.wait_for_job_description(page)


async def _attachment_drawn(page, bound, monkeypatch):
    return await attachments.wait_for_attachment_drawn(page, "cv.pdf", timeout_ms=bound)


async def _send_enabled(page, bound, monkeypatch):
    return await named_profile.wait_for_send_enabled(page, timeout_ms=bound)


async def _reply_send_enabled(page, bound, monkeypatch):
    return await threads.wait_for_reply_send_enabled(page, timeout_ms=bound)


#: (name, the module whose ``time`` the wait reads, how to run it)
WAITS = [
    ("save_control", dom, _save_control),
    ("job_description", dom, _job_description),
    ("attachment_drawn", attachments, _attachment_drawn),
    ("send_enabled", named_profile, _send_enabled),
    ("reply_send_enabled", threads, _reply_send_enabled),
]


@pytest.mark.parametrize(("name", "module", "run"), WAITS, ids=[w[0] for w in WAITS])
async def test_a_wait_the_driver_ended_in_its_last_millisecond_reads_its_bound(
    name, module, run, monkeypatch
):
    """The driver ends the wait 0.4 ms before the bound, in real time, the
    shape lane CI measured. SHOWN FAILING before the fix: each read 999."""
    clock = _VirtualClock(500.0)
    monkeypatch.setattr(module, "time", clock)
    page = _Page(clock, [(0.9996, True)])
    verdict = await run(page, 1_000, monkeypatch)
    assert clock.reads >= 2, (name, clock.reads)
    assert verdict["failure"] == "TimeoutError", verdict
    assert verdict["waited_ms"] >= 1_000, verdict


@pytest.mark.parametrize(("name", "module", "run"), WAITS, ids=[w[0] for w in WAITS])
async def test_a_wait_is_read_on_the_fine_clock_not_the_tick_clock(
    name, module, run, monkeypatch
):
    """The wait lasts 300.8 ms from just after a tick, which the tick clock
    reads as 19 ticks, 296.875 ms. SHOWN FAILING before the fix: each read
    296."""
    start = 1_000 * TICK + 0.0001
    clock = _VirtualClock(start, tick=TICK)
    monkeypatch.setattr(module, "time", clock)
    page = _Page(clock, [(0.3008, True)])
    verdict = await run(page, 300, monkeypatch)
    assert verdict["failure"] == "TimeoutError", verdict
    assert verdict["waited_ms"] >= 300, verdict


async def test_the_attachment_waits_second_step_gets_only_what_is_left(monkeypatch):
    """The attachment wait gives Send's wait what is left of ONE bound. The
    name drew after 500.4 ms of a 1000 ms bound, so 499.6 ms are left. SHOWN
    FAILING before the fix: the truncated reading left 500 ms, and the two
    waits together were allowed 1000.4 ms of a 1000 ms bound."""
    clock = _VirtualClock(500.0)
    monkeypatch.setattr(attachments, "time", clock)
    page = _Page(clock, [(0.5004, False), (0.4, False)])
    verdict = await attachments.wait_for_attachment_drawn(page, "cv.pdf", timeout_ms=1_000)
    assert verdict["drawn"] is True, verdict
    first, second = page.timeouts
    assert first == 1_000, page.timeouts
    assert 500.4 + second <= 1_000, page.timeouts
