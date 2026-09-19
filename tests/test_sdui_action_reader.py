"""A zero from a reader that has never been shown returning non-zero is not a measurement.

THE RULING THIS SERVES. The operator ruled on 2026-09-01 that **a click
measured to issue no `ServerRequest` is, by effect, a READ** -- extending this
package's own reasoning about the messaging filter pills, which send nothing
and change nothing. `set_open_to_work`'s editor opens as a modal and modals
open by clicking, so that ruling is the only route to it.

Something has to do the measuring. `dom.read_sdui_actions` is it, and this file
is about the one way such an instrument fails: **by returning a clean zero to a
question it could not actually ask.**

That failure has happened four times this week in other forms -- a guard blind
to a doubled backslash, a comparison with no passing case, a corpus of nothing
reading as a pass, a suite green over a file it could not see. Every one was an
instrument answering confidently about something it could not see. A parser
that has stopped parsing reports zero of everything, and **zero of everything
is the exact shape of permission.**

SO THE READER CARRIES ITS OWN FLOOR. `readable` is False unless the payload was
present AND carried recognisable action tokens. A page with script blocks and
no actions is a page this reader cannot speak for, and it says so rather than
reporting a comfortable row of zeroes.

AND THE WINDOW ERRS TOWARD REFUSING, which is asserted here rather than
described: an over-wide window attributes a neighbour's `ServerRequest` to this
control and refuses a click that would have been safe; a too-narrow one misses
this control's own and permits a click that SENDS. Those errors are not
symmetric.

WHAT THESE TESTS CANNOT DO. They cannot exercise the JavaScript -- that needs a
browser and a real flight payload. They test the Python wrapper: its defaults,
its floor, and its refusal to turn an unreadable page into a permissive one.
The live half is a separate act, on the live profile, and it is gated on the
reader being shown to correctly report the control it must REFUSE before any
zero it produces is treated as permission.
"""

import pytest

from linkedin_server import dom


class _Page:
    """A page whose ``evaluate`` returns a canned reading, or raises."""

    def __init__(self, reading=None, raises=None):
        self.reading = reading
        self.raises = raises
        self.calls = []

    async def evaluate(self, script, cfg=None):
        self.calls.append((script, cfg))
        if self.raises is not None:
            raise self.raises
        return self.reading


def _reading(whole=None, scoped=None, **kw):
    """A canned page reading. ``whole`` fills the ``global`` bucket.

    Named ``whole`` because ``global`` is a Python keyword and cannot be a
    keyword argument -- an earlier version passed ``global_=`` and the update
    silently did nothing, so the "ordinary case" test asserted readable=True
    against a reading of all zeroes and failed. Worth the comment: a helper
    that quietly drops its argument makes every test built on it a test of
    the default.
    """
    base = {
        "script_blocks": 17,
        "payload_chars": 1_091_238,
        "needle_hits": 1,
        "global": {k: 0 for k in dom.SDUI_ACTION_TOKENS},
        "scoped": {k: 0 for k in dom.SDUI_ACTION_TOKENS},
    }
    base["global"].update(whole or {})
    base["scoped"].update(scoped or {})
    base.update(kw)
    return base


async def test_a_payload_with_actions_reads_as_readable():
    """The ordinary case, so the floor below cannot pass by refusing everything."""
    page = _Page(_reading({"navigate": 40, "server_request": 24}))
    out = await dom.read_sdui_actions(page, "opento_preview_otw")
    assert out["readable"] is True
    assert out["global"]["server_request"] == 24
    assert out["error"] is None


async def test_a_page_with_no_payload_at_all_is_not_readable():
    """Zero script characters is the sanitised-fixture shape, not a clean page.

    Every tracked profile fixture in this repo carries ZERO script characters,
    deliberately, because the payload is where his identity lives. A reader
    pointed at one must say it cannot speak rather than report no actions.
    """
    page = _Page(_reading(script_blocks=0, payload_chars=0))
    out = await dom.read_sdui_actions(page, "opento_preview_otw")
    assert out["readable"] is False


async def test_a_payload_with_no_recognisable_actions_is_not_readable():
    """THE FLOOR, and the whole point of this file.

    A megabyte of script that yields zero of every action token is far more
    likely a parser that has stopped working than a profile with no server
    actions at all. Reporting that as a row of zeroes would hand a caller the
    exact shape of permission.
    """
    page = _Page(_reading(payload_chars=1_091_238))
    out = await dom.read_sdui_actions(page, "opento_preview_otw")
    assert out["readable"] is False
    assert sum(out["global"].values()) == 0


async def test_an_evaluate_that_raises_reports_the_error_and_is_not_readable():
    """A reader that threw knows nothing, which is not the same as 'no actions'."""
    page = _Page(raises=RuntimeError("detached frame"))
    out = await dom.read_sdui_actions(page, "opento_preview_otw")
    assert out["readable"] is False
    assert "RuntimeError" in out["error"]
    assert out["global"]["server_request"] == 0
    assert out["scoped"]["server_request"] == 0


async def test_a_malformed_reading_cannot_produce_a_confident_zero():
    """Missing keys must not become zeroes that read as measurements.

    A future page-side change that drops the ``global`` bucket would otherwise
    hand back a full set of zeroes with ``readable`` deciding on nothing.
    """
    page = _Page({"payload_chars": 900_000})
    out = await dom.read_sdui_actions(page, "opento_preview_otw")
    assert out["readable"] is False
    assert set(out["global"]) == set(dom.SDUI_ACTION_TOKENS)
    assert set(out["scoped"]) == set(dom.SDUI_ACTION_TOKENS)


async def test_the_needle_and_window_reach_the_page_unchanged():
    """The scoping arguments are what make a count about one control.

    Asserted because a needle silently dropped would turn every scoped count
    into a whole-page count -- which over-counts, so it would fail SAFE, but
    it would also make the instrument useless while looking like it worked.
    """
    page = _Page(_reading())
    await dom.read_sdui_actions(page, "opento_preview_otw", window=1234)
    _script, cfg = page.calls[0]
    assert cfg["needle"] == "opento_preview_otw"
    assert cfg["window"] == 1234
    assert cfg["tokens"] == dict(dom.SDUI_ACTION_TOKENS)


def test_server_request_is_the_token_the_ruling_turns_on():
    """The token set is small and each member earns its place.

    ``server_request`` decides. The other three exist so that a zero on it can
    be told apart from a reading of nothing at all -- which is the distinction
    this whole file is about.
    """
    assert dom.SDUI_ACTION_TOKENS["server_request"] == "ServerRequest"
    assert set(dom.SDUI_ACTION_TOKENS) == {
        "server_request",
        "navigate",
        "set_state",
        "show_menu",
    }


def test_the_window_is_wide_enough_to_err_toward_refusing():
    """The asymmetry, pinned as a number with its reason.

    Too narrow permits a click that sends; too wide refuses one that was safe.
    A future edit shrinking this to a "tighter" value is trading a safe error
    for an unsafe one, and it should have to move this line to do it.
    """
    assert dom.SDUI_WINDOW_CHARS >= 4000, dom.SDUI_WINDOW_CHARS


@pytest.mark.parametrize("needle", ["", None])
async def test_no_needle_means_no_scoped_claim(needle):
    """Without a needle the scoped counts stay zero and mean nothing.

    They must not be mistaken for "this control has no ServerRequest" -- which
    is why the gate consuming this requires ``needle_hits`` to be non-zero
    before it reads a scoped count at all.
    """
    page = _Page(_reading(needle_hits=0))
    out = await dom.read_sdui_actions(page, needle or "")
    assert out["needle_hits"] == 0
