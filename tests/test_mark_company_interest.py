"""``mark_company_interest`` -- census row ``P I14`` -- built to ready-to-fire,
and the three controls that keep a built write from being a fired one.

WHAT THIS ACTION IS. Pressing "I'm interested" in the About-the-company card
of one job posting, which tells THAT EMPLOYER'S RECRUITERS he is interested in
working there. The act is FOR other people, so its live proof is aimed by the
operator (``OPERATOR-NAMES-THE-TARGET``); nothing here, and nothing in the
lane that built it, chooses a real posting.

WHAT IS MEASURED AND WHAT IS NOT, so no test claims more. The OFF control is
MEASURED: a plain button named by its own text, ``I<U+2019>m interested``, in
the card, on three tracked posting captures (``tests/fixtures/job_detail*.html``)
-- section 1 reads all three. The ON label is NOT measured: every world below
that needs it is DERIVED from ``job_detail_hydrated.html`` by one asserted
edit, and the gate is required to refuse it rather than to read it.

NOTHING HERE REACHES LINKEDIN. Every page is a tracked capture or a
derivation of one, served into a local headless Chromium.
"""
from __future__ import annotations

import json
import re

import pytest

from linkedin_server import company_interest, dom, server, shape, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_apply_modal_fixture import over  # noqa: F401 -- fixture
from tests.test_writes import (  # noqa: F401 -- two of these are fixtures
    JOB,
    FixtureNavigator,
    browser_page,
    markup,
    writes_on,
)

_ACTION = "mark_company_interest"
_SPEC = spec_for_action(_ACTION)
_URL = _SPEC.url_template.format(target=JOB)

#: The tracked capture every derived world starts from.
_BASE = markup("job_detail_hydrated")

#: The OFF label as the capture writes it (an HTML entity for U+2019).
_OFF_MARKUP = "I&#8217;m interested</span>"

#: The employer's name, parsed out of the capture's own company label rather
#: than typed, so a regenerated fixture cannot leave a stale expectation. The
#: label ends with a full stop LinkedIn adds for screen readers, which is not
#: part of the name.
_EMPLOYER = re.search(r'aria-label="Company, ([^"]+?)\.?"', _BASE).group(1)


def _derive(old: str, new: str, *, source: str = _BASE, count: int = 1) -> str:
    """An ASSERTED edit: a replace whose anchor drifted is a silent no-op."""
    derived = source.replace(old, new, count)
    assert derived != source, f"the derivation anchored on {old!r} changed nothing"
    return derived


#: DERIVED -- the control relabelled to a name NOBODY HAS MEASURED, which is
#: the shape an already-signalled interest would take.
_ON_WORLD = _derive(_OFF_MARKUP, "Interested</span>")
#: DERIVED -- a second OFF control in the same card.
_BUTTON = re.search(
    r'<button [^>]*data-view-name="org-member-company-interest-pipeline-interested-cta">'
    r".*?</button>",
    _BASE,
    re.S,
).group(0)
_TWO_OFF_WORLD = _derive(_BUTTON, _BUTTON + _BUTTON)
#: DERIVED -- the card opens by naming ANOTHER company.
_OTHER_CARD_WORLD = _derive(
    f">{_EMPLOYER}</span></p></div></div><div", ">Otherway Example Nine</span></p></div></div><div"
)
#: DERIVED -- the card draws no interest control at all.
_NO_CONTROL_WORLD = _derive(_BUTTON, "")


def _no_page_string(text: str) -> None:
    """Nothing the PAGE chose may appear in a ``why`` or an exception."""
    for needle in ("Otherway", "Interested</span>"):
        assert needle not in text, f"{needle!r} leaked into: {text}"


async def _verdict(over, world: str):
    async def read(page):
        posting = await dom.read_job_posting(page)
        return await company_interest.read_state(
            page, company=posting["detail"].get("company")
        )

    return await over(world, read)


# ---------------------------------------------------------------------------
# 1. The captures draw what the reader reads
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture", ["job_detail", "job_detail_hydrated", "job_detail_following_hydrated"]
)
async def test_all_three_tracked_captures_read_not_signalled(over, fixture):
    facts, state, why = await _verdict(over, markup(fixture))
    assert state == company_interest.NOT_SIGNALLED == _SPEC.from_state, why
    assert facts["off_controls_in_card"] == 1
    assert facts["off_controls_on_page"] == 1


@pytest.mark.parametrize("fixture", ["job_detail_following", "job_detail_shell"])
async def test_a_skeleton_or_a_shell_is_unknown_not_a_state(over, fixture):
    _facts, state, why = await _verdict(over, markup(fixture))
    assert state == company_interest.UNKNOWN
    assert why


def test_the_label_is_built_from_the_code_point_and_matches_the_card_reader():
    assert company_interest.OFF_LABEL == "I" + chr(0x2019) + "m interested"
    assert shape._ABOUT_INTEREST_CONTROL.match(company_interest.OFF_LABEL)
    assert company_interest.CARD == dom.ABOUT_COMPANY_CONTAINER
    assert company_interest.OFF_CONTROL_IN_CARD.startswith("css=" + dom.ABOUT_COMPANY_CONTAINER)


async def test_the_section_is_bounded_so_a_missing_control_counts_zero(over):
    """SHOWN FAILING FIRST: the unbounded version climbed from the Help link to
    the nearest ancestor holding ANY button, so with the interest control
    removed it counted the card's Follow control and 'more' toggle as the
    section's (2), which the verification would have read as a control that
    MOVED. Bounded to the section's own keyed block, it counts zero."""
    measured = await over(_BASE, company_interest.read_interest_control)
    removed = await over(_NO_CONTROL_WORLD, company_interest.read_interest_control)
    assert measured["section_buttons"] == 1 and measured["off_in_card"] == 1
    assert removed["section_buttons"] == 0 and removed["off_in_card"] == 0
    assert removed["section"] >= 1, "the Help link, the section's marker, is still drawn"


async def test_the_click_selector_resolves_to_the_one_control_in_the_card(over):
    async def aim(page):
        target = page.locator(company_interest.OFF_CONTROL_IN_CARD)
        return await target.count(), await target.get_attribute("data-view-name")

    assert await over(_BASE, aim) == (1, "org-member-company-interest-pipeline-interested-cta")


# ---------------------------------------------------------------------------
# 2. The verdict: one state besides unknown, and no page string in any why
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "world, fragment",
    [
        (_ON_WORLD, "ALREADY-SIGNALLED"),
        (_TWO_OFF_WORLD, "pressing by position"),
        (_OTHER_CARD_WORLD, "'unnamed'"),
        (_NO_CONTROL_WORLD, "no interest control at all"),
    ],
    ids=["already-signalled-shape", "two-off-controls", "another-companys-card", "no-control"],
)
async def test_every_derived_world_is_refused_and_says_why_without_quoting_the_page(
    over, world, fragment
):
    _facts, state, why = await _verdict(over, world)
    assert state == company_interest.UNKNOWN
    assert fragment in why
    _no_page_string(why)


def test_a_reader_failure_is_reported_by_type_only():
    _f, state, why = company_interest.interest_verdict(
        {"state": "read"}, {"error": "TimeoutError"}, company="x"
    )
    assert state == company_interest.UNKNOWN and "TimeoutError" in why


def test_counts_that_are_words_are_coerced_not_raised():
    _f, state, why = company_interest.interest_verdict(
        {"state": "read"},
        {"off_in_card": "Exampleperson Markersurname", "section_buttons": 0},
        company="x",
    )
    assert state == company_interest.UNKNOWN and "Markersurname" not in why


@pytest.mark.parametrize(
    "reading, card, expected",
    [
        ({"off_in_card": 1, "section_buttons": 1}, {"state": "read"}, "not_signalled"),
        ({"off_in_card": 0, "section_buttons": 1}, {"state": "read"}, "interest_signalled"),
        ({"off_in_card": 0, "section_buttons": 0}, {"state": "read"}, "unknown"),
        ({"off_in_card": 0, "section_buttons": 1}, {"state": "unnamed"}, "unknown"),
        ({"error": "TimeoutError"}, {"state": "read"}, "unknown"),
    ],
    ids=["off-still-drawn", "control-moved", "nothing-drawn", "card-unattributed", "read-failed"],
)
def test_the_verification_verdict(reading, card, expected):
    state, _why = company_interest.verification_verdict(reading, card)
    assert state == expected


# ---------------------------------------------------------------------------
# 3. The preview: one page load, the employer named, a token minted
# ---------------------------------------------------------------------------


async def test_the_preview_reads_the_page_it_acts_on(writes_on, browser_page):
    nav = FixtureNavigator({_URL: _BASE})
    block = await preview(_SPEC, target=JOB, navigator=nav, page=browser_page)
    assert nav.gotos == [_URL]
    assert block["where"]["job_id"] == JOB
    assert block["where"]["company"] == _EMPLOYER
    assert block["read"]["same_page_as_the_action"] is True
    assert block["read"]["page_loads"] == 1
    assert block["direction"]["currently"] == "not_signalled"
    assert block["direction"]["after"] == "interest_signalled"
    assert block["reversibility_class"] == "STILL-UNKNOWN"
    assert block["verification"]["outcome_is_verifiable"] == "YES"
    assert "max 50" in block["spends"]
    assert isinstance(block["to_confirm"], str) and block["to_confirm"]


@pytest.mark.parametrize(
    "world", [_ON_WORLD, _TWO_OFF_WORLD, _OTHER_CARD_WORLD, _NO_CONTROL_WORLD],
    ids=["already-signalled-shape", "two-off-controls", "another-companys-card", "no-control"],
)
async def test_the_preview_refuses_every_derived_world_and_mints_nothing(
    writes_on, browser_page, world
):
    nav = FixtureNavigator({_URL: world})
    with pytest.raises(WriteAttemptError) as excinfo:
        await preview(_SPEC, target=JOB, navigator=nav, page=browser_page)
    _no_page_string(str(excinfo.value))
    assert not writes._GRANTS, "a refused preview minted a grant"


# ---------------------------------------------------------------------------
# 4. THE THREE CONTROLS -- no grant, another target, a second use
# ---------------------------------------------------------------------------


async def test_control_1_it_refuses_without_a_grant(monkeypatch, browser_page):
    monkeypatch.delenv(writes.WRITES_FLAG, raising=False)
    nav = FixtureNavigator({_URL: _BASE})
    with pytest.raises(WriteAttemptError, match="disabled"):
        await preview(_SPEC, target=JOB, navigator=nav, page=browser_page)
    with pytest.raises(WriteAttemptError, match="disabled"):
        consume("anything", action=_ACTION, target=JOB)
    off = await server._write_tool(_ACTION, JOB, "")
    assert off["error"] == "writes_disabled" and off["performed"] is False

    monkeypatch.setenv(writes.WRITES_FLAG, "1")
    for bogus in ("", None, True, "not-a-real-token"):
        with pytest.raises(WriteAttemptError):
            consume(bogus, action=_ACTION, target=JOB)
    unredeemed = writes.WriteGrant(action=_ACTION, target=JOB, token="t", minted_at=0.0)
    with pytest.raises(WriteAttemptError, match="not been redeemed"):
        await writes.perform(nav, browser_page, unredeemed)
    with pytest.raises(WriteAttemptError, match="WriteGrant"):
        await writes.perform(nav, browser_page, {"action": _ACTION})
    assert nav.gotos == [], "a refused write navigated"
    writes.discard_all()


async def test_control_2_it_refuses_a_grant_for_a_different_target(writes_on, browser_page):
    nav = FixtureNavigator({_URL: _BASE})
    block = await preview(_SPEC, target=JOB, navigator=nav, page=browser_page)
    with pytest.raises(WriteAttemptError, match="minted for target"):
        consume(block["to_confirm"], action=_ACTION, target="4600000043")
    # ... and for a different VERB on the same posting: follow_company and
    # save_job act on this very address, so these are the pairings worth
    # refusing.
    nav = FixtureNavigator({_URL: _BASE})
    block = await preview(_SPEC, target=JOB, navigator=nav, page=browser_page)
    for other in ("follow_company", "save_job"):
        with pytest.raises(WriteAttemptError, match="minted for 'mark_company_interest'"):
            consume(block["to_confirm"], action=other, target=JOB)


async def test_control_3_it_refuses_a_second_use_of_the_same_grant(writes_on, browser_page):
    nav = FixtureNavigator({_URL: _BASE})
    block = await preview(_SPEC, target=JOB, navigator=nav, page=browser_page)
    grant = consume(block["to_confirm"], action=_ACTION, target=JOB)
    with pytest.raises(WriteAttemptError, match="unknown or already-discarded"):
        consume(block["to_confirm"], action=_ACTION, target=JOB)
    first = FixtureNavigator({_URL: [_BASE, _ON_WORLD]})
    receipt = await writes.perform(first, browser_page, grant)
    assert receipt["clicked"]["clicks_made"] == 1
    second = FixtureNavigator({_URL: _BASE})
    with pytest.raises(WriteAttemptError, match="already been used once"):
        await writes.perform(second, browser_page, grant)
    assert second.gotos == [], "the second use navigated before it refused"


# ---------------------------------------------------------------------------
# 5. End to end: press in the card, confirm on a fresh render
# ---------------------------------------------------------------------------


async def _run(browser_page, after_world: str) -> dict:
    nav = FixtureNavigator({_URL: _BASE})
    block = await preview(_SPEC, target=JOB, navigator=nav, page=browser_page)
    grant = consume(block["to_confirm"], action=_ACTION, target=JOB)
    act = FixtureNavigator({_URL: [_BASE, after_world]})
    receipt = await writes.perform(act, browser_page, grant)
    assert act.gotos == [_URL, _URL], "the press and the fresh render, nothing else"
    return receipt


async def test_a_signal_whose_control_moved_is_performed(writes_on, browser_page):
    """THE POSITIVE CASE, on a DERIVED after-world: the OFF label gone and the
    section still drawing a control."""
    receipt = await _run(browser_page, _ON_WORLD)
    assert receipt["clicked"]["selector"] == company_interest.OFF_CONTROL_IN_CARD
    assert receipt["clicked"]["error"] is None
    assert receipt["clicked"]["state_before"] == "not_signalled"
    assert receipt["verification"]["observed_state"] == "interest_signalled"
    assert receipt["verification"]["read_from"] == _URL
    assert receipt["performed"] is True and receipt["verified"] is True


async def test_the_off_label_still_drawn_on_the_fresh_render_is_not_performed(
    writes_on, browser_page
):
    """THE STRONG NEGATIVE: a press that opened a step nobody took, or that
    LinkedIn ignored, re-renders with the OFF label still there."""
    receipt = await _run(browser_page, _BASE)
    assert receipt["clicked"]["clicks_made"] == 1
    assert receipt["verification"]["observed_state"] == "not_signalled"
    assert receipt["performed"] is False
    assert "dialog(s) open" in receipt["verification"]["why"]


async def test_a_section_that_vanished_after_the_press_is_unknown_not_moved(
    writes_on, browser_page
):
    """A card that re-renders WITHOUT the interest control is not evidence the
    signal landed: the verification must answer unknown, never 'signalled'."""
    receipt = await _run(browser_page, _NO_CONTROL_WORLD)
    assert receipt["verification"]["observed_state"] == "unknown"
    assert receipt["performed"] == writes.UNKNOWN


async def test_a_fresh_render_of_another_companys_card_is_unknown(writes_on, browser_page):
    receipt = await _run(browser_page, _OTHER_CARD_WORLD)
    assert receipt["verification"]["observed_state"] == "unknown"
    assert receipt["performed"] == writes.UNKNOWN
    _no_page_string(json.dumps(receipt["verification"]))


def test_the_receipt_and_the_surface_tables_name_this_action():
    assert writes._WHERE_TO_LOOK[_ACTION] == "the About-the-company card on that posting"
    assert "RE-RENDERED" in writes._VERIFIED_FROM[_ACTION]
    assert _ACTION not in writes._TOGGLE_ACTIONS
    assert writes.anchor_label_for(_SPEC) == company_interest.OFF_LABEL
    assert writes.grant_is_possible(_SPEC)
    assert _ACTION in writes.PERFORMABLE
    assert writes.SANCTIONED_WRITES["linkedin_mark_company_interest"].action == _ACTION
    assert callable(getattr(server, "linkedin_mark_company_interest", None))
