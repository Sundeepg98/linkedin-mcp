"""``follow_company_page`` -- census row ``N 47`` -- built to ready-to-fire, and
the three controls that keep a built write from being a fired one.

WHAT THIS ACTION IS. A follow of one organisation Page, performed on the Page
root itself and addressed by the Page's NUMERIC id -- the same id
``unfollow_company`` keys Manage Pages rows by. It is the first follow in this
design whose undo can be aimed without a resolver.

WHAT IS MEASURED AND WHAT IS NOT, so no test here claims more. The STRUCTURE
of the page is a measurement, taken 2026-09-20 off one Page-root capture held
outside the tree, and ``tests/fixtures/synthetic/company_page_follow.html``
carries that structure with invented content. The label a FOLLOWED Page's
control wears has never been captured; every world below that needs it is
DERIVED from the fixture by an asserted edit and labelled as such, and the
gate is required to refuse it rather than to read it.

NOTHING HERE REACHES LINKEDIN. Every page is the synthetic fixture or a
committed Manage Pages capture, served into a local headless Chromium. A
grant minted here is minted against a frozen world by the real preview, and
its click lands on a static button in that world.

THE THREE CONTROLS THE LANE BRIEF ASKED FOR, in section 5: the write refuses
WITHOUT a grant, refuses a grant for a DIFFERENT target, and refuses a SECOND
use of the same grant -- each at the token door AND at ``perform``.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from linkedin_server import coerce, dom, server, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_apply_modal_fixture import over  # noqa: F401 -- fixture
from tests.test_writes import (  # noqa: F401 -- two of these are fixtures
    FOLLOWED_COMPANY,
    browser_page,
    markup,
    writes_on,
)

_FIXTURE = Path(__file__).parent / "fixtures" / "synthetic" / "company_page_follow.html"

#: The synthetic Page root, read once. IMPORTED BY
#: ``tests/test_preview_state_and_click_state.py``, which serves committed
#: markup only and names this module as its source.
COMPANY_PAGE_FOLLOW_MARKUP = _FIXTURE.read_text(encoding="ascii")

#: The numeric id the fixture's own people-search link names, PARSED out of
#: the fixture rather than typed, so a regenerated fixture cannot leave a
#: stale expectation passing.
COMPANY_PAGE_FOLLOW_ID = dom.company_ids_in_people_search_href(
    re.search(r'href="(https://www\.linkedin\.com/search/results/people/[^"]*)"',
              COMPANY_PAGE_FOLLOW_MARKUP).group(1).replace("&amp;", "&")
)[0][0]

_ACTION = "follow_company_page"
_SPEC = spec_for_action(_ACTION)

#: The Page's own name, parsed out of the one heading that the top card's
#: follow control names -- never typed here.
_SUBJECT = re.search(r'aria-label="Follow ([^"]+)" componentkey="page-a1b2c3d4-top"',
                     COMPANY_PAGE_FOLLOW_MARKUP).group(1)

#: Where LinkedIn's redirect lands in these worlds: an organisation root under
#: a SLUG, which is the canonical shape and the reason the landing is never
#: printed. Invented, and deliberately name-shaped.
_LANDED = "https://www.linkedin.com/company/examplecorp-analytics/"


def _page_url(company_id: str) -> str:
    return _SPEC.url_template.format(target=company_id)


def _derive(old: str, new: str, *, count: int = -1, source: str = COMPANY_PAGE_FOLLOW_MARKUP) -> str:
    """An ASSERTED edit of the fixture. A replace whose anchor drifted is a
    silent no-op, and a refusal test run against the unedited page would pass
    for the wrong reason."""
    derived = source.replace(old, new, count)
    assert derived != source, f"the derivation anchored on {old!r} changed nothing"
    return derived


#: DERIVED -- the Page as it would read if he already followed it, with the
#: control relabelled to a name NOBODY HAS MEASURED. The gate must not read it.
_FOLLOWED_WORLD = _derive(
    f'aria-label="Follow {_SUBJECT}"', f'aria-label="Following {_SUBJECT}"'
)
#: DERIVED -- the Page's own link names another organisation.
_OTHER_ID_WORLD = _derive(f"%22{COMPANY_PAGE_FOLLOW_ID}%22", "%2253000012%22")
#: DERIVED -- the Page draws no people-search link at all.
_NO_LINK_WORLD = _derive("/search/results/people/?currentCompany", "/company/setup/?currentCompany")
#: DERIVED -- one recommended card moved out of the aside into the main column.
_TWO_IN_MAIN_WORLD = _derive(
    '<section class="org-about">',
    '<div class="rec-card"><span>Otherway Example Nine</span><button type="button" '
    'aria-label="Follow Otherway Example Nine">Follow</button></div>'
    '<section class="org-about">',
    count=1,
)
#: DERIVED -- the Page's heading no longer matches what its control names.
_UNBOUND_WORLD = _derive(
    f'<h2 class="org-top-card-summary__title">{_SUBJECT}</h2>',
    '<h2 class="org-top-card-summary__title">A Different Heading</h2>',
)


class _RedirectingNavigator:
    """Serves frozen worlds and RECORDS the asks; lands where LinkedIn would.

    A url maps to ``(html, landed)``. The organisation root lands on a SLUG,
    because LinkedIn canonicalises the numeric address -- which is the whole
    reason the gate reads identity off the page rather than off the url.
    """

    def __init__(self, pages: dict[str, tuple[str, str]]):
        self.pages = dict(pages)
        self.gotos: list[str] = []

    async def goto(self, page, url: str) -> str:
        self.gotos.append(url)
        if url not in self.pages:
            raise AssertionError(f"the gate asked for {url!r}, which this test did not freeze")
        html, landed = self.pages[url]
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return landed


def _navigator(world: str, company_id: str, *, followed: str = "manage_pages_following_hydrated"):
    return _RedirectingNavigator(
        {
            _page_url(company_id): (world, _LANDED),
            writes.FOLLOWED_PAGES_URL: (markup(followed), writes.FOLLOWED_PAGES_URL),
        }
    )


async def _read(over, world: str) -> dict:
    return await over(world, dom.read_company_page_follow)


def _no_page_string(text: str) -> None:
    """The rule under test: nothing the PAGE chose may appear in a ``why`` or
    an exception. Names from the fixture, and the landed slug."""
    for needle in (_SUBJECT, "Otherway", "examplecorp-analytics", "53000012"):
        assert needle not in text, f"{needle!r} leaked into: {text}"


# ---------------------------------------------------------------------------
# 1. The fixture draws what the capture drew
# ---------------------------------------------------------------------------


async def test_the_fixture_draws_the_measured_shape(over):
    """Eight ``Follow ``-prefixed controls: one outside <main>, one in the main
    column, six in the recommended aside. The reason a prefix is no aim."""

    async def counts(page):
        return {
            "anywhere": await page.locator(dom.COMPANY_PAGE_FOLLOW_ANYWHERE).count(),
            "main_column": await page.locator(dom.COMPANY_PAGE_FOLLOW_CONTROL).count(),
            "aside": await page.locator("xpath=//aside//button[starts-with(@aria-label, 'Follow ')]").count(),
            "outside_main": await page.locator(
                "xpath=//button[starts-with(@aria-label, 'Follow ')][not(ancestor::main)]"
            ).count(),
            "h1": await page.locator("h1").count(),
            "identity_links": await page.locator(dom.COMPANY_PAGE_IDENTITY_LINKS).count(),
        }

    assert await over(COMPANY_PAGE_FOLLOW_MARKUP, counts) == {
        "anywhere": 8, "main_column": 1, "aside": 6, "outside_main": 1,
        "h1": 0, "identity_links": 1,
    }


async def test_the_reader_binds_the_one_control_to_the_pages_own_heading(over):
    reading = await _read(over, COMPANY_PAGE_FOLLOW_MARKUP)
    assert reading["error"] is None
    assert reading["follow_controls"] == 1
    assert reading["follow_controls_anywhere"] == 8
    assert reading["bound_controls"] == 1
    assert reading["subject"] == _SUBJECT
    assert reading["identity_ids"] == [COMPANY_PAGE_FOLLOW_ID]
    assert reading["identity_malformed"] == 0


async def test_the_click_selector_is_a_constant_that_resolves_to_the_top_card_control(over):
    """Strict mode is the last guard: the constant selector must match EXACTLY
    one element, and it must be the Page's own control, not the header's."""

    async def aim(page):
        target = page.locator(dom.COMPANY_PAGE_FOLLOW_CONTROL)
        return await target.count(), await target.get_attribute("componentkey")

    assert await over(COMPANY_PAGE_FOLLOW_MARKUP, aim) == (1, "page-a1b2c3d4-top")
    assert dom.COMPANY_PAGE_FOLLOW_CONTROL.startswith("xpath=")
    assert _SUBJECT not in dom.COMPANY_PAGE_FOLLOW_CONTROL


# ---------------------------------------------------------------------------
# 2. The verdict: one state besides unknown, and no page string in any why
# ---------------------------------------------------------------------------


async def test_the_measured_world_reads_not_following(over):
    facts, state, why = writes.company_page_follow_verdict(
        await _read(over, COMPANY_PAGE_FOLLOW_MARKUP), COMPANY_PAGE_FOLLOW_ID
    )
    assert state == "not_following" == _SPEC.from_state
    assert facts["company"] == _SUBJECT
    _no_page_string(why)


@pytest.mark.parametrize(
    "world, fragment",
    [
        (_FOLLOWED_WORLD, "never 'following'"),
        (_OTHER_ID_WORLD, "DIFFERENT organisation id"),
        (_NO_LINK_WORLD, "name 0 distinct"),
        (_TWO_IN_MAIN_WORLD, "picking by position"),
        (_UNBOUND_WORLD, "cannot be shown to be THIS"),
    ],
    ids=["already-followed", "another-organisation", "no-identity-link",
         "two-in-the-main-column", "control-not-bound-to-heading"],
)
async def test_every_derived_world_is_refused_and_says_why_without_quoting_the_page(
    over, world, fragment
):
    facts, state, why = writes.company_page_follow_verdict(
        await _read(over, world), COMPANY_PAGE_FOLLOW_ID
    )
    assert state == writes.UNKNOWN
    assert fragment in why
    _no_page_string(why)


def test_a_reader_failure_is_reported_by_type_and_a_forged_type_is_not_echoed():
    _f, state, why = writes.company_page_follow_verdict({"error": "TimeoutError"}, "53000011")
    assert state == writes.UNKNOWN and "TimeoutError" in why
    _f, state, why = writes.company_page_follow_verdict(
        {"error": "Exampleperson Markersurname"}, "53000011"
    )
    assert state == writes.UNKNOWN and "Markersurname" not in why


def test_the_verdict_ignores_what_is_not_digits_and_never_raises_on_strings():
    reading = {
        "follow_controls": "Exampleperson Markersurname",
        "bound_controls": 1,
        "subject": "x",
        "identity_ids": ["53000011", "not-an-id", 7],
    }
    _f, state, why = writes.company_page_follow_verdict(reading, "53000011")
    # The count that is a string is substituted with zero, not raised on.
    assert state == writes.UNKNOWN
    assert "Markersurname" not in why


def test_the_identity_link_parser_reads_both_spellings_and_counts_the_rest():
    ids = dom.company_ids_in_people_search_href
    assert ids("/search/results/people/?currentCompany=%5B%2253000011%22%5D") == (["53000011"], 0)
    assert ids("/search/results/people/?currentCompany=53000011&pastCompany=53000012") == (["53000011"], 0)
    assert ids("/search/results/people/?currentCompany=%5B%22abc%22%5D") == ([], 1)
    assert ids("/search/results/people/?currentCompany=%5B") == ([], 1)
    # str.isdigit would admit these; the ten ASCII digits do not. The four
    # Arabic-Indic digits are built from code points so this file stays ASCII.
    arabic_indic = "".join(chr(0x0661 + n) for n in range(4))
    assert arabic_indic.isdigit() and not arabic_indic.isascii()
    assert ids("/search/results/people/?currentCompany=" + arabic_indic) == ([], 1)


# ---------------------------------------------------------------------------
# 3. The preview: one page load, the page named, the landing withheld
# ---------------------------------------------------------------------------


async def test_the_preview_reads_the_page_it_acts_on_and_withholds_the_landing(writes_on, browser_page):
    nav = _navigator(COMPANY_PAGE_FOLLOW_MARKUP, COMPANY_PAGE_FOLLOW_ID)
    block = await preview(_SPEC, target=COMPANY_PAGE_FOLLOW_ID, navigator=nav, page=browser_page)
    assert nav.gotos == [_page_url(COMPANY_PAGE_FOLLOW_ID)]
    assert block["where"]["company"] == _SUBJECT
    assert block["where"]["company_id"] == COMPANY_PAGE_FOLLOW_ID
    assert block["where"]["redirected"] is True
    assert block["where"]["read_from_the_pages_own_control"] is True
    assert "list_coverage" not in block["where"]
    assert block["read"]["same_page_as_the_action"] is True
    assert block["read"]["page_loads"] == 1
    assert block["direction"]["currently"] == "not_following"
    assert block["direction"]["after"] == "following"
    assert block["reversibility_class"] == "REVERSIBLE"
    assert block["verification"]["outcome_is_verifiable"] == "YES"
    assert isinstance(block["to_confirm"], str) and block["to_confirm"]
    # THE CANONICAL SLUG IS NOWHERE IN THE BLOCK.
    assert "examplecorp-analytics" not in json.dumps(block)


@pytest.mark.parametrize(
    "world", [_FOLLOWED_WORLD, _OTHER_ID_WORLD, _NO_LINK_WORLD, _TWO_IN_MAIN_WORLD, _UNBOUND_WORLD],
    ids=["already-followed", "another-organisation", "no-identity-link",
         "two-in-the-main-column", "control-not-bound-to-heading"],
)
async def test_the_preview_refuses_every_derived_world_and_the_refusal_quotes_nothing(
    writes_on, browser_page, world
):
    nav = _navigator(world, COMPANY_PAGE_FOLLOW_ID)
    with pytest.raises(WriteAttemptError) as excinfo:
        await preview(_SPEC, target=COMPANY_PAGE_FOLLOW_ID, navigator=nav, page=browser_page)
    _no_page_string(str(excinfo.value))
    assert not writes._GRANTS, "a refused preview minted a grant"


# ---------------------------------------------------------------------------
# 4. The landing check: the shape of an organisation root, nothing more
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "landed",
    ["https://www.linkedin.com/company/examplecorp-analytics/",
     "https://www.linkedin.com/company/examplecorp-analytics",
     "https://www.linkedin.com/company/53000011/"],
)
def test_the_landing_check_accepts_an_organisation_root(landed):
    grant = writes.WriteGrant(action=_ACTION, target="53000011", token="t", minted_at=0.0)
    writes._assert_landed_on_target(_SPEC, grant, landed)


@pytest.mark.parametrize(
    "landed",
    ["https://www.linkedin.com/company/examplecorp-analytics/people/",
     "https://www.linkedin.com/feed/",
     "http://www.linkedin.com/company/examplecorp-analytics/",
     "https://example.invalid/company/examplecorp-analytics/",
     "https://www.linkedin.com/authwall?sessionRedirect=examplecorp-analytics"],
)
def test_the_landing_check_refuses_anything_else_and_withholds_it(landed):
    grant = writes.WriteGrant(action=_ACTION, target="53000011", token="t", minted_at=0.0)
    with pytest.raises(WriteAttemptError) as excinfo:
        writes._assert_landed_on_target(_SPEC, grant, landed)
    assert "WITHHELD" in str(excinfo.value)
    _no_page_string(str(excinfo.value))


# ---------------------------------------------------------------------------
# 5. THE THREE CONTROLS -- no grant, another target, a second use
# ---------------------------------------------------------------------------


async def test_control_1_it_refuses_without_a_grant(monkeypatch, browser_page):
    """Without a grant nothing moves, at every door, and nothing is navigated."""
    # (a) writes off -- the process-wide door refuses before anything else.
    monkeypatch.delenv(writes.WRITES_FLAG, raising=False)
    nav = _navigator(COMPANY_PAGE_FOLLOW_MARKUP, COMPANY_PAGE_FOLLOW_ID)
    with pytest.raises(WriteAttemptError, match="disabled"):
        await preview(_SPEC, target=COMPANY_PAGE_FOLLOW_ID, navigator=nav, page=browser_page)
    with pytest.raises(WriteAttemptError, match="disabled"):
        consume("anything", action=_ACTION, target=COMPANY_PAGE_FOLLOW_ID)
    off = await server._write_tool(_ACTION, COMPANY_PAGE_FOLLOW_ID, "")
    assert off["error"] == "writes_disabled" and off["performed"] is False

    # (b) writes on, and still no grant: no token, a forged token, an
    # unredeemed grant, and something that is not a grant at all.
    monkeypatch.setenv(writes.WRITES_FLAG, "1")
    for bogus in ("", None, True, "not-a-real-token"):
        with pytest.raises(WriteAttemptError):
            consume(bogus, action=_ACTION, target=COMPANY_PAGE_FOLLOW_ID)
    unredeemed = writes.WriteGrant(
        action=_ACTION, target=COMPANY_PAGE_FOLLOW_ID, token="t", minted_at=0.0
    )
    with pytest.raises(WriteAttemptError, match="not been redeemed"):
        await writes.perform(nav, browser_page, unredeemed)
    with pytest.raises(WriteAttemptError, match="WriteGrant"):
        await writes.perform(nav, browser_page, {"action": _ACTION})
    assert nav.gotos == [], "a refused write navigated"


async def test_control_2_it_refuses_a_grant_for_a_different_target(writes_on, browser_page):
    nav = _navigator(COMPANY_PAGE_FOLLOW_MARKUP, COMPANY_PAGE_FOLLOW_ID)
    block = await preview(_SPEC, target=COMPANY_PAGE_FOLLOW_ID, navigator=nav, page=browser_page)
    token = block["to_confirm"]
    with pytest.raises(WriteAttemptError, match="minted for target"):
        consume(token, action=_ACTION, target="53000012")
    # ... and for a different VERB on the same target: the unfollow is keyed
    # by the same numeric id, so this is the pairing most worth refusing.
    nav = _navigator(COMPANY_PAGE_FOLLOW_MARKUP, COMPANY_PAGE_FOLLOW_ID)
    block = await preview(_SPEC, target=COMPANY_PAGE_FOLLOW_ID, navigator=nav, page=browser_page)
    with pytest.raises(WriteAttemptError, match="minted for 'follow_company_page'"):
        consume(block["to_confirm"], action="unfollow_company", target=COMPANY_PAGE_FOLLOW_ID)


async def test_control_3_it_refuses_a_second_use_of_the_same_grant(writes_on, browser_page):
    """Single use at BOTH doors: the token cannot be redeemed twice, and the
    redeemed grant cannot be performed twice."""
    nav = _navigator(COMPANY_PAGE_FOLLOW_MARKUP, COMPANY_PAGE_FOLLOW_ID)
    block = await preview(_SPEC, target=COMPANY_PAGE_FOLLOW_ID, navigator=nav, page=browser_page)
    grant = consume(block["to_confirm"], action=_ACTION, target=COMPANY_PAGE_FOLLOW_ID)
    with pytest.raises(WriteAttemptError, match="unknown or already-discarded"):
        consume(block["to_confirm"], action=_ACTION, target=COMPANY_PAGE_FOLLOW_ID)

    first = _navigator(COMPANY_PAGE_FOLLOW_MARKUP, COMPANY_PAGE_FOLLOW_ID)
    receipt = await writes.perform(first, browser_page, grant)
    assert receipt["clicked"]["clicks_made"] == 1
    second = _navigator(COMPANY_PAGE_FOLLOW_MARKUP, COMPANY_PAGE_FOLLOW_ID)
    with pytest.raises(WriteAttemptError, match="already been used once"):
        await writes.perform(second, browser_page, grant)
    assert second.gotos == [], "the second use navigated before it refused"


async def test_the_second_use_guard_is_shown_failing_without_its_flag(writes_on, browser_page):
    """SHOWN FAILING. Clear the flag ``perform`` set on the first use -- the
    state every redeemed grant was in before 2026-09-23 -- and the SAME grant
    object walks straight back to the page and clicks again. So the flag is
    the whole of the second-use refusal, and nothing else stood there."""
    nav = _navigator(COMPANY_PAGE_FOLLOW_MARKUP, COMPANY_PAGE_FOLLOW_ID)
    block = await preview(_SPEC, target=COMPANY_PAGE_FOLLOW_ID, navigator=nav, page=browser_page)
    grant = consume(block["to_confirm"], action=_ACTION, target=COMPANY_PAGE_FOLLOW_ID)
    await writes.perform(_navigator(COMPANY_PAGE_FOLLOW_MARKUP, COMPANY_PAGE_FOLLOW_ID), browser_page, grant)
    assert grant.performed is True

    grant.performed = False  # the mutation: the guard's input, removed
    replay = _navigator(COMPANY_PAGE_FOLLOW_MARKUP, COMPANY_PAGE_FOLLOW_ID)
    receipt = await writes.perform(replay, browser_page, grant)
    assert replay.gotos[0] == _page_url(COMPANY_PAGE_FOLLOW_ID)
    assert receipt["clicked"]["clicks_made"] == 1, "without the flag the replay clicks"


# ---------------------------------------------------------------------------
# 6. End to end: click on the Page, confirm on a DIFFERENT surface
# ---------------------------------------------------------------------------


async def test_a_follow_runs_end_to_end_and_is_verified_off_manage_pages(writes_on, browser_page):
    """THE POSITIVE CASE. The Page is re-keyed to the id the committed Manage
    Pages capture draws a row for -- DERIVED, one asserted edit -- so the
    verification can find it."""
    world = _derive(f"%22{COMPANY_PAGE_FOLLOW_ID}%22", f"%22{FOLLOWED_COMPANY}%22")
    nav = _navigator(world, FOLLOWED_COMPANY)
    block = await preview(_SPEC, target=FOLLOWED_COMPANY, navigator=nav, page=browser_page)
    grant = consume(block["to_confirm"], action=_ACTION, target=FOLLOWED_COMPANY)
    act = _navigator(world, FOLLOWED_COMPANY)
    receipt = await writes.perform(act, browser_page, grant)
    assert act.gotos == [_page_url(FOLLOWED_COMPANY), writes.FOLLOWED_PAGES_URL]
    assert receipt["clicked"]["selector"] == dom.COMPANY_PAGE_FOLLOW_CONTROL
    assert receipt["clicked"]["error"] is None
    assert receipt["clicked"]["state_before"] == "not_following"
    assert receipt["clicked"]["on"] == _page_url(FOLLOWED_COMPANY)
    assert receipt["verification"]["observed_state"] == "following"
    assert receipt["performed"] is True and receipt["verified"] is True
    assert "examplecorp-analytics" not in json.dumps(receipt)


async def test_a_follow_whose_row_is_not_drawn_reports_unknown_not_failure(writes_on, browser_page):
    """Manage Pages renders a fraction of itself; an absent row is not evidence."""
    nav = _navigator(COMPANY_PAGE_FOLLOW_MARKUP, COMPANY_PAGE_FOLLOW_ID)
    block = await preview(_SPEC, target=COMPANY_PAGE_FOLLOW_ID, navigator=nav, page=browser_page)
    grant = consume(block["to_confirm"], action=_ACTION, target=COMPANY_PAGE_FOLLOW_ID)
    receipt = await writes.perform(
        _navigator(COMPANY_PAGE_FOLLOW_MARKUP, COMPANY_PAGE_FOLLOW_ID), browser_page, grant
    )
    assert receipt["clicked"]["clicks_made"] == 1
    assert receipt["performed"] == writes.UNKNOWN
    assert receipt["verification"]["observed_state"] == writes.UNKNOWN


def test_the_receipt_and_the_surface_tables_name_this_action():
    assert writes._WHERE_TO_LOOK[_ACTION] == "your followed companies"
    assert "DIFFERENT surface" in writes._VERIFIED_FROM[_ACTION]
    assert writes._WRITE_SURFACE_FOR_ACTION[_ACTION] == "organisation Page"
    assert _ACTION in writes._TOGGLE_ACTIONS
    assert writes.anchor_label_for(_SPEC) == dom.COMPANY_PAGE_FOLLOW_PREFIX
    assert writes.grant_is_possible(_SPEC)


# ---------------------------------------------------------------------------
# 7. The two repairs made in the functions this build touched
# ---------------------------------------------------------------------------


async def test_the_unfollow_arm_no_longer_quotes_the_label_into_a_refusal(monkeypatch):
    """``perform`` raises with ``_live_control``'s ``why``; the unfollow arm
    used to put the control's full accessible name -- a Page's name -- in it."""

    async def planted(_page, _company_id):
        return {"count": 1, "label": "Exampleperson Markersurname"}

    monkeypatch.setattr(dom, "read_unfollow_control", planted)
    spec = spec_for_action("unfollow_company")
    grant = writes.WriteGrant(action="unfollow_company", target="902611", token="t", minted_at=0.0)
    state, why, selector = await writes._live_control(object(), spec, grant, writes.UNFOLLOW_ANCHOR_PREFIX)
    assert state == writes.UNKNOWN and selector == ""
    assert "Markersurname" not in why


async def test_a_string_count_no_longer_carries_itself_out_of_live_control(monkeypatch):
    """The coercion repair, SHOWN FAILING: with ``coerce.as_count`` put back to
    the ``int(x or 0)`` it replaced, the same reading raises a ValueError that
    quotes the page's string."""

    async def planted(_page):
        return {"controls": "Exampleperson Markersurname", "off_state": 0}

    monkeypatch.setattr(dom, "read_reaction_surface", planted)
    spec = spec_for_action("react_to_item")
    grant = writes.WriteGrant(action="react_to_item", target="x", token="t", minted_at=0.0)
    state, why, _sel = await writes._live_control(object(), spec, grant, dom.REACTION_OFF_LABEL)
    assert state == writes.UNKNOWN and "Markersurname" not in why

    monkeypatch.setattr(coerce, "as_count", lambda value, default=0: int(value or default))
    with pytest.raises(ValueError) as excinfo:
        await writes._live_control(object(), spec, grant, dom.REACTION_OFF_LABEL)
    assert "Markersurname" in str(excinfo.value)


# ---------------------------------------------------------------------------
# 8. The census row this build banked, and the chain it rests on
# ---------------------------------------------------------------------------


def test_n47_claims_the_coverage_it_was_banked_with_and_the_chain_is_whole():
    """``N 47`` reads COVERED-UNFIRED -- built, never fired -- and every link it
    rests on still exists: the reader, the verdict, the spec, the tool. A row
    left claiming coverage after one of these moves is the reverse of the GAP
    drift this census usually finds, and it is caught here, by name."""
    census = (Path(__file__).resolve().parents[1] / "_audit" / "_census" / "network.md")
    rows = [line for line in census.read_text(encoding="utf-8").splitlines()
            if line.startswith("| 47 |")]
    assert len(rows) == 1, rows
    assert "| **COVERED-UNFIRED** |" in rows[0]
    assert "linkedin_follow_company_page" in rows[0]
    assert callable(dom.read_company_page_follow)
    assert callable(writes.company_page_follow_verdict)
    assert _ACTION in writes.PERFORMABLE
    assert writes.SANCTIONED_WRITES["linkedin_follow_company_page"].action == _ACTION
    assert callable(getattr(server, "linkedin_follow_company_page", None))
