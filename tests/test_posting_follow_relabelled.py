"""The posting's follow control after LinkedIn RELABELLED it -- census N 46 and J 103.

THE MEASUREMENT THIS ANSWERS. ``_audit/2026-09-19-the-follow-control-live.md``:
on five hydrated live postings the company-follow control inside the
About-the-company card carried ``aria-label="Follow <the employer's name>"``,
and ``dom.FOLLOW_CONTROL`` -- the exact-value union of ``Follow`` and
``Following`` -- matched ZERO controls on all five. The reader then reported
"no follow control rendered ... the page had not hydrated yet", which was
false: the card had drawn its follower line and its button. So
``linkedin_follow_company`` refused on every live posting while its census rows
read COVERED-UNFIRED, whose definition is a tool that would NOT refuse at the
gate.

THE ANCHOR, carried over from the organisation Page root (``N 47``): a prefix
alone is not an identity. The posting's own control is the ONE button in the
About-the-company card whose name opens ``Follow `` -- the space is the
discriminator, so a ``Following ...`` control never matches -- AND whose name,
after that prefix, is the employer name the card itself draws in its own
``/company/`` link. Both are read on the page; nothing is typed here, and the
reader never returns the employer-bearing label: a bound control is reported
by the canonical state word ``Follow``, which is all a caller acts on.

WHAT IS STILL NOT MEASURED, AND WHICH WAY IT FAILS. The relabelled ON label has
never been seen (every measured posting was an employer he did not follow).
A card drawing a ``Following `` control is therefore UNKNOWN -- never
``following`` -- and the refusal says so instead of blaming hydration.

EVERY WORLD BELOW IS ONE ASSERTED EDIT of ``tests/fixtures/job_detail.html``, a
committed, sanitised capture whose card draws the invented employer
"Ashgrove Systems" and a bare ``Follow`` control. Nothing here reaches LinkedIn.
"""
from __future__ import annotations

import pathlib

import pytest

from linkedin_server import dom, shape, writes
from linkedin_server.writes import spec_for_action

from tests.test_apply_modal_fixture import VIEWPORT, over  # noqa: F401
from tests.test_writes import _bare_grant

ROOT = pathlib.Path(__file__).resolve().parents[1]

# NO MODULE-LEVEL UPPER-CASE CONSTANT BEYOND ``ROOT``, on the impact gate's
# rule: a test naming an upper-case constant another file defines is coupled
# to it.

_legacy = (ROOT / "tests" / "fixtures" / "job_detail.html").read_text(
    encoding="ascii")
_employer = "Ashgrove Systems"
_stranger = "Otherway Example"
_job = "4600000042"
_bare = 'aria-label="Follow"'


def _one_edit(html: str, old: str, new: str) -> str:
    assert html.count(old) == 1, f"{old!r} occurs {html.count(old)} times"
    return html.replace(old, new)


def _relabelled() -> str:
    return _one_edit(_legacy, _bare, f'aria-label="Follow {_employer}"')


def _relabelled_on() -> str:
    return _one_edit(_legacy, _bare, f'aria-label="Following {_employer}"')


def _unbound() -> str:
    return _one_edit(_legacy, _bare, f'aria-label="Follow {_stranger}"')


def _two_in_card() -> str:
    """A second, bound, prefixed control inside the same card."""
    tag = f'aria-label="Follow {_employer}">'
    return _one_edit(_relabelled(), tag,
                     f'{tag}</button><button type="button" {tag}')


def _outside_the_card() -> str:
    """The card's control is gone; a bound-looking one sits outside the card."""
    html = _one_edit(_legacy, _bare, 'aria-label="Share"')
    # The capture is a fragment that ends at ``</main>``; the stray control
    # goes just before it, inside the page and outside the card.
    return _one_edit(html, "</main>",
                     f'<button type="button" aria-label="Follow {_employer}">'
                     "Follow</button></main>")


def _both_conventions() -> str:
    """The bare control kept, and a bound prefixed one beside it in the card."""
    tag = f"{_bare}>"
    return _one_edit(_legacy, tag,
                     f'{tag}</button><button type="button" '
                     f'aria-label="Follow {_employer}">')


async def _state(over, html: str) -> tuple[str, str]:  # noqa: F811
    async def work(page):
        return await writes._read_follow_state(page)

    return await over(html, work)


async def _live(over, html: str):  # noqa: F811
    spec = spec_for_action("follow_company")
    grant = _bare_grant(action="follow_company", target=_job)
    anchor = writes.anchor_label_for(spec, _job) or ""

    async def work(page):
        state, why, selector, *_rest = await writes._live_control(
            page, spec, grant, anchor)
        matched = labels = None
        if selector:
            located = page.locator(selector)
            matched = await located.count()
            labels = [await located.nth(i).get_attribute("aria-label")
                      for i in range(matched)]
        return state, why, selector, matched, labels

    return await over(html, work)


# ---------------------------------------------------------------------------
# 1. the worlds are what they claim to be
# ---------------------------------------------------------------------------


def test_the_legacy_capture_is_the_shape_every_world_is_derived_from():
    assert _legacy.count(_bare) == 1
    assert _legacy.count("JobDetails_AboutTheCompany") >= 1
    assert _legacy.count(f"<span>{_employer}</span>") >= 1


# ---------------------------------------------------------------------------
# 2. SHOWN FAILING before the repair: the relabelled OFF control
# ---------------------------------------------------------------------------


async def test_a_relabelled_posting_reads_not_following(over):  # noqa: F811
    state, why = await _state(over, _relabelled())
    assert state == "not_following", (
        f"the relabelled OFF control read {state!r}: {why}")
    assert _employer not in why


async def test_the_click_lands_on_the_cards_own_control_and_nothing_else(over):  # noqa: F811
    state, why, selector, matched, labels = await _live(over, _relabelled())
    assert state == "not_following", why
    assert selector, "no selector was built for a control the gate accepted"
    assert matched == 1, f"the click selector matches {matched} elements"
    assert labels == [f"Follow {_employer}"]
    assert _employer not in why


async def test_the_on_label_is_unknown_and_not_blamed_on_hydration(over):  # noqa: F811
    state, why = await _state(over, _relabelled_on())
    assert state == "unknown"
    assert "hydrat" not in why.lower(), (
        "a card that drew a Following control was reported as a page that "
        f"had not hydrated: {why}")
    assert _employer not in why


# ---------------------------------------------------------------------------
# 3. the worlds the anchor must refuse, each quoting nothing the page chose
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("world", [
    _unbound, _two_in_card, _outside_the_card, _both_conventions,
], ids=lambda f: f.__name__.lstrip("_"))
async def test_a_control_that_cannot_be_shown_to_be_the_employers_is_refused(
        over, world):  # noqa: F811
    state, why = await _state(over, world())
    assert state == "unknown", f"{world.__name__} read {state!r}: {why}"
    assert _employer not in why and _stranger not in why, why
    live_state, _why, selector, _m, _l = await _live(over, world())
    assert live_state == "unknown" and not selector


# ---------------------------------------------------------------------------
# 4. the measured legacy convention is untouched
# ---------------------------------------------------------------------------


async def test_the_bare_convention_still_reads_as_it_was_measured(over):  # noqa: F811
    state, _why = await _state(over, _legacy)
    assert state == "not_following"
    live_state, _why, selector, matched, labels = await _live(over, _legacy)
    assert live_state == "not_following" and matched == 1
    assert labels == ["Follow"]


def test_the_reader_never_returns_the_employer_bearing_label():
    """A bound relabelled control is reported by the canonical state word; the
    verdict that consumes it is a pure function of that reading."""
    reading = {"label": "Follow", "count": 1, "form": "prefixed",
               "in_card": 1, "in_card_following": 0, "anywhere": 1,
               "bound": 1, "error": None}
    verdict = shape.posting_follow_state(reading)
    assert verdict["state"] == "not_following"
    assert set(verdict) == {"state", "why"}
