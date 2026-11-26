"""The server's own spacing between page loads is the ruled pace: 20 seconds.

``LIVE-BUDGET-40-LOADS`` (``_audit/RULINGS.md``) puts LinkedIn page loads at
least 20 seconds apart. The live lane has always set
``LINKEDIN_MIN_INTERVAL_S=20`` in its own environment, but the server's
DEFAULT was 3 s, so whatever drove this server without that variable spaced
its loads 3 s apart -- inside one tool call above all, where nothing else
looks. A red team of the apply pipeline measured exactly that on 2026-11-26
(its attack N-01): the pipeline's hook spaces call STARTS, and only
``config.MIN_NAVIGATION_INTERVAL_S`` spaces every navigation. So the default
is the ruled pace now, and this file holds it:

* THE DEFAULT, read in a FRESH interpreter with the variable unset, through
  the module whose rate slot spends it (``linkedin_server.browser``). In this
  process the value was fixed at import by whatever environment ran the
  suite, so only a new interpreter can say what the default is. Shown failing
  on a planted 3.0 default, through the same read.
* THE OVERRIDE still sets one process's pace, as it always has.
* ONE CALL'S BURST -- attack N-01's shape, three loads back to back -- lands
  the interval apart, on the fake rate clock (``tests/conftest.py``), so the
  40 s are asserted and never slept.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from linkedin_server import browser as browser_module
from linkedin_server.browser import LinkedInBrowser
from tests.conftest import FakePage, FakeRateClock

REPO = Path(__file__).resolve().parents[1]

#: The ruled pace, in seconds between two page loads (LIVE-BUDGET-40-LOADS).
RULED_PACE_S = 20.0

#: The shipped default, exactly as config.py spells it. The control plants a
#: 3.0 in its place and refuses to run if it cannot find this spelling, so a
#: rewrite of the line cannot leave the control planting nothing.
_SHIPPED_DEFAULT = 'os.environ.get("LINKEDIN_MIN_INTERVAL_S", "20.0")'
_PLANTED_DEFAULT = 'os.environ.get("LINKEDIN_MIN_INTERVAL_S", "3.0")'

#: Run in a fresh interpreter: optionally swap in a planted config module,
#: then import the browser and print the interval its rate slot reads.
#: ``import linkedin_server`` comes first because the package imports its
#: config eagerly (for SERVER_NAME); the plant replaces that module in
#: ``sys.modules`` BEFORE the browser binds from it.
_READ_THE_SLOT = r"""
import importlib.util
import sys

planted = sys.argv[1]
if planted:
    import linkedin_server
    spec = importlib.util.spec_from_file_location("linkedin_server.config", planted)
    module = importlib.util.module_from_spec(spec)
    sys.modules["linkedin_server.config"] = module
    spec.loader.exec_module(module)
from linkedin_server import browser
print(repr(browser.MIN_NAVIGATION_INTERVAL_S))
"""


def _the_slot_in_a_fresh_process(
    *, override: Optional[str] = None, planted_config: Optional[Path] = None
) -> float:
    """The interval ``linkedin_server.browser`` binds in a new interpreter."""
    env = {k: v for k, v in os.environ.items() if k != "LINKEDIN_MIN_INTERVAL_S"}
    if override is not None:
        env["LINKEDIN_MIN_INTERVAL_S"] = override
    done = subprocess.run(
        [sys.executable, "-c", _READ_THE_SLOT, str(planted_config or "")],
        cwd=str(REPO),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert done.returncode == 0, done.stderr[-1500:]
    return float(done.stdout.strip().splitlines()[-1])


def _meets_the_ruled_pace(interval: float) -> bool:
    return interval >= RULED_PACE_S


def test_the_default_spacing_is_the_ruled_twenty_seconds() -> None:
    """RED AT 7760a5f: with the variable unset, the slot read 3.0 there."""
    interval = _the_slot_in_a_fresh_process()
    assert _meets_the_ruled_pace(interval), (
        f"with LINKEDIN_MIN_INTERVAL_S unset the rate slot spaces page loads "
        f"{interval} s apart; LIVE-BUDGET-40-LOADS rules at least {RULED_PACE_S} s"
    )


def test_the_pace_check_fails_on_a_planted_three_second_default(tmp_path) -> None:
    """THE CONTROL: the same read, through a config defaulting to 3.0, is refused."""
    source = (REPO / "linkedin_server" / "config.py").read_text(encoding="utf-8")
    assert source.count(_SHIPPED_DEFAULT) == 1, (
        "config.py no longer spells the default this way; re-aim the plant"
    )
    planted = tmp_path / "config.py"
    planted.write_text(
        source.replace(_SHIPPED_DEFAULT, _PLANTED_DEFAULT), encoding="utf-8"
    )
    interval = _the_slot_in_a_fresh_process(planted_config=planted)
    assert interval == 3.0, "the plant never reached the rate slot"
    assert not _meets_the_ruled_pace(interval)


def test_the_override_still_sets_one_processes_pace() -> None:
    """``LINKEDIN_MIN_INTERVAL_S`` is still read, so one process can set its own."""
    assert _the_slot_in_a_fresh_process(override="45") == 45.0


class _ClockedPage(FakePage):
    """A fake page that notes the rate clock's reading at every load."""

    def __init__(self, clock: FakeRateClock) -> None:
        super().__init__()
        self.clock = clock
        self.loaded_at: list[float] = []

    async def goto(self, url: str, **kwargs) -> None:
        self.loaded_at.append(self.clock.now)
        await super().goto(url, **kwargs)


async def test_one_calls_three_loads_land_the_ruled_pace_apart(
    monkeypatch, rate_clock
) -> None:
    """ATTACK N-01's SHAPE: three loads inside one call, back to back.

    Nothing between them waits -- no hook sees inside a call -- so the rate
    slot is the only spacing they get. At the ruled pace each load after the
    first owes the whole 20 s, and the loads land exactly that far apart.
    """
    monkeypatch.setattr(browser_module, "MIN_NAVIGATION_INTERVAL_S", RULED_PACE_S)
    browser = LinkedInBrowser()
    page = _ClockedPage(rate_clock)
    for url in (
        "https://www.linkedin.com/feed/",
        "https://www.linkedin.com/notifications/",
        "https://www.linkedin.com/mynetwork/",
    ):
        await browser.goto(page, url)

    assert rate_clock.sleeps == [RULED_PACE_S, RULED_PACE_S]
    gaps = [later - earlier for earlier, later in zip(page.loaded_at, page.loaded_at[1:])]
    assert gaps == [RULED_PACE_S, RULED_PACE_S], gaps
