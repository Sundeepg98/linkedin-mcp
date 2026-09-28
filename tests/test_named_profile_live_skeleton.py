"""The named-person reader over the LIVE-TRUE fixture (the orchestrator's
addendum of 2026-09-28 08:43).

WHAT HAPPENED LIVE. The live lane's session 2 ran ``linkedin_message_from_profile``
on a first-degree profile the operator named. The preview loaded the profile
once through the named-person door and REFUSED -- ``writes._direction`` raised
because the reading came back ``unknown`` -- and nothing was pressed or sent.
The refusal was the design working; the reader was not live-true. It had been
built over an invented page (``tests/fixtures/synthetic/named_profile.html``)
whose Message control is LABELLED ``Message <name>``, and the live topcard draws
it as a composer link named by its own text, "Message", with no label -- twice,
one of the two hidden.

WHAT THIS FILE HOLDS.

1. The fixture is the capture's STRUCTURE: a fixed point of its committed
   builder, ``scripts/_build_named_profile_skeleton.py``, carrying the
   structure digest the builder printed from the live lane's skeleton.
2. The OLD reader fails on it, as the live page failed it: the label it
   matched is not drawn, so the old gate's conditions read zero.
3. The REBUILT reader passes on it -- the one visible Message control inside
   the owner's topcard, and it the owner's -- whichever of the two action rows
   is the hidden one, and refuses when both are shown.
4. The read he names works on it: the name and headline come back as a people
   record, and the member's GROUPS stay absent -- the capture draws no
   Interests section and no group link, which is why ``N 178`` stays GAP.

WHICH FIXTURE IS LIVE-TRUE: this one. The synthetic page stays the secondary
case, for what the live one cannot show (a Connect control, a degree other than
first, a stranger with the same name, the conversation a Message press opens).
"""
from __future__ import annotations

import contextlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from linkedin_server import dom, named_profile, people_data, server
from tests.test_writes import browser_page  # noqa: F401 -- a fixture

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "synthetic" / "named_profile_live.html"
BUILDER = REPO / "scripts" / "_build_named_profile_skeleton.py"
LIVE = FIXTURE.read_text(encoding="ascii")
HIDDEN = ' style="display:none"'

SEGMENT = "casey-example-3f9a"
LINK = "https://www.linkedin.com/in/" + SEGMENT + "/"
OWNER = "Casey Example"
HEADLINE = "Invented headline for a synthetic person"

#: THE STRUCTURE THE CAPTURE HAS: tags and nesting below <body>, an svg counted
#: and not entered, as the builder printed it when run over the live lane's
#: skeleton on 2026-09-28 (lane L5; recorded in
#: _audit/2026-09-24-lane-l5-messaging.md). Whoever holds the skeleton can
#: re-derive it; a structural hand edit of the fixture changes it.
STRUCTURE_DIGEST = "iefnpejnhfajibng"


def _rebuild(source: Path, out: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BUILDER), "--skeleton", str(source), "--out", str(out)],
        capture_output=True, text=True, cwd=REPO,
    )


def _printed(stdout: str, label: str) -> str:
    lines = [line for line in stdout.splitlines() if line.startswith(label)]
    assert len(lines) == 1, stdout
    return lines[0][len(label):].strip()


def _lf(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


# ---------------------------------------------------------------------------
# 1. The fixture is the capture's structure
# ---------------------------------------------------------------------------


def test_the_fixture_is_a_fixed_point_of_its_committed_builder(tmp_path):
    """NORMAL FORM: run over its own output, the builder reproduces it byte for
    byte -- every value it writes is one it keeps. That pins the text and the
    builder; the structure is pinned by the digest below."""
    out = tmp_path / "rebuilt.html"
    run = _rebuild(FIXTURE, out)
    assert run.returncode == 0, run.stderr
    assert _lf(out.read_bytes()) == _lf(FIXTURE.read_bytes())
    assert _printed(run.stdout, "reduced text") == "0"
    assert _printed(run.stdout, "unclassified text") == "0"
    assert _printed(run.stdout, "unclassified labels") == "0"
    assert _printed(run.stdout, "action rows") == "2, the second hidden"


def test_the_words_the_builder_keeps_are_the_words_the_live_lane_kept():
    """The builder keeps LinkedIn's own words verbatim, and only the ones the
    live lane's skeleton kept: every one is on that builder's closed list."""
    sys.path.insert(0, str(REPO / "scripts"))
    import _build_named_profile_skeleton as builder
    import _probe_live_lane_session_2 as live

    assert builder.KEPT_WORDS <= live.FURNITURE, builder.KEPT_WORDS - live.FURNITURE
    assert builder.KEPT_LABELS <= live.FURNITURE, builder.KEPT_LABELS - live.FURNITURE


def test_the_fixture_carries_the_structure_the_builder_printed_from_the_capture(tmp_path):
    run = _rebuild(FIXTURE, tmp_path / "rebuilt.html")
    assert run.returncode == 0, run.stderr
    assert _printed(run.stdout, "structure digest") == STRUCTURE_DIGEST


def test_THIS_CONTROL_CAN_FAIL_a_structural_hand_edit_changes_the_digest(tmp_path):
    """Every svg deleted: the text survives, the structure does not."""
    edited = tmp_path / "edited.html"
    stripped = re.sub(r"<svg[^>]*></svg>", "", LIVE)
    assert stripped != LIVE
    edited.write_text(stripped, encoding="ascii")
    run = _rebuild(edited, tmp_path / "rebuilt.html")
    assert run.returncode == 0, run.stderr
    assert _printed(run.stdout, "structure digest") != STRUCTURE_DIGEST


def test_THIS_CONTROL_CAN_FAIL_a_hand_edit_breaks_the_fixed_point(tmp_path):
    edited = tmp_path / "edited.html"
    edited.write_text(LIVE.replace(HEADLINE, HEADLINE + " edited"), encoding="ascii")
    out = tmp_path / "rebuilt.html"
    run = _rebuild(edited, out)
    assert run.returncode == 0, run.stderr
    assert _lf(out.read_bytes()) != _lf(edited.read_bytes())


def test_THIS_CONTROL_CAN_FAIL_a_hand_edit_in_a_kept_attribute_breaks_the_fixed_point(tmp_path):
    """FOUND BY THE COLD CHECK OF 2026-09-28: a canary written into ``role``,
    ``dir`` and ``aria-current`` survived the builder and WAS a fixed point of
    it -- a kept attribute was kept whatever it held. Each kept attribute now
    holds a closed vocabulary, and a value outside it is dropped and counted."""
    from tests.test_fixtures_hold_only_synthetic_people import PLANTED

    edited = tmp_path / "edited.html"
    planted = LIVE.replace('role="button"', 'role="' + PLANTED + '"', 1)
    planted = planted.replace('<main ', '<main dir="' + PLANTED + '" aria-current="' + PLANTED + '" ', 1)
    assert planted.count(PLANTED) == 3
    edited.write_text(planted, encoding="ascii")
    out = tmp_path / "rebuilt.html"
    run = _rebuild(edited, out)
    assert run.returncode == 0, run.stderr
    assert PLANTED not in out.read_text(encoding="ascii")
    assert _printed(run.stdout, "unclassified attributes") == "3"
    assert _lf(out.read_bytes()) != _lf(edited.read_bytes())


def test_THIS_CONTROL_CAN_FAIL_a_capture_that_draws_interests_keeps_them(tmp_path):
    """THE N 178 CHECK BELOW CAN FAIL: a capture drawing an Interests section
    with a Groups tab and a group link keeps all three through the builder
    (the cold check found "Interests" written as "Example text", which made
    that check unfailable)."""
    edited = tmp_path / "edited.html"
    planted = LIVE.replace(
        "</body>",
        '<section><h3>Interests</h3><div role="tablist"><button type="button" role="tab">'
        'Groups</button></div><a href="https://www.linkedin.com/groups/1234501/">x</a>'
        "</section></body>",
        1,
    )
    edited.write_text(planted, encoding="ascii")
    out = tmp_path / "rebuilt.html"
    run = _rebuild(edited, out)
    assert run.returncode == 0, run.stderr
    rebuilt = out.read_text(encoding="ascii")
    assert "Interests" in rebuilt and ">Groups<" in rebuilt and "/groups/" in rebuilt


def test_the_fixture_says_it_is_the_live_true_one_and_the_synthetic_says_secondary():
    assert "THIS IS THE LIVE-TRUE FIXTURE" in LIVE
    synthetic = (FIXTURE.parent / "named_profile.html").read_text(encoding="utf-8")
    assert "THE SECONDARY CASE SINCE 2026-09-28" in synthetic
    assert "named_profile_live.html" in synthetic


# ---------------------------------------------------------------------------
# 2. The old reader fails on it; 3. the rebuilt reader does not
# ---------------------------------------------------------------------------


async def _reading(page, world: str = LIVE) -> dict:
    await page.set_content(world, wait_until="domcontentloaded", timeout=60_000)
    return await dom.read_named_profile(page)


def _old_message_state(reading: dict) -> str:
    """THE OLD GATE'S FIRST THREE CONDITIONS, frozen as master c94c39e shipped
    them (``named_profile.message_state`` before 2026-09-28): exactly one
    control on the page LABELLED ``Message <owner>``, that one inside the
    topcard, and exactly one labelled Message control in the topcard. The
    fields they read are still returned, with the same meaning."""
    if not named_profile.identity_confirmed(reading):
        return named_profile.UNKNOWN
    if reading["message_matches"] != 1 or reading["message_in_topcard"] != 1:
        return named_profile.UNKNOWN
    if reading["message_controls_in_topcard"] != 1:
        return named_profile.UNKNOWN
    return named_profile.MESSAGE_FROM


async def test_the_old_reader_refuses_the_live_page_as_it_did_live(browser_page):
    """MEASURED BEFORE THE REBUILD, on this fixture, by the reader master
    c94c39e shipped: identity confirmed, degree 1st -- and message_state
    ``unknown``, "0 Message control(s) are named for this person". The live
    page's topcard draws its Message control with no label, and every
    labelled Message control on the page is another person's."""
    reading = await _reading(browser_page)
    assert named_profile.identity_confirmed(reading)
    assert reading["degree"] == "1st"
    assert reading["message_matches"] == 0
    assert reading["message_in_topcard"] == 0
    assert reading["message_controls_in_topcard"] == 0
    assert reading["message_controls"] >= 1, "the rails' labelled controls are drawn"
    assert _old_message_state(reading) == named_profile.UNKNOWN


async def test_the_rebuilt_reader_finds_the_one_visible_message_and_it_is_theirs(browser_page):
    reading = await _reading(browser_page)
    assert reading["topcards"] == 1 and reading["heading_matches_title"] is True
    assert reading["message_kind_in_topcard"] == 2, "drawn twice"
    assert reading["message_visible_in_topcard"] == 1, "one of the two hidden"
    assert reading["message_owner_visible_in_topcard"] == 1
    assert reading["message_foreign_in_topcard"] == 0
    assert (reading["message_tag"], reading["message_href"]) == ("a", "compose")
    assert reading["more_in_topcard"] == 2 and reading["more_visible_in_topcard"] == 1
    state, _why = named_profile.message_state(reading)
    assert state == named_profile.MESSAGE_FROM
    assert await browser_page.locator(dom.topcard_message_control_selector()).count() == 1


async def test_whichever_row_is_hidden_the_press_reaches_exactly_one(browser_page):
    """WHICH ROW LINKEDIN HIDES IS NOT IN THE CAPTURE, so both are driven: the
    second hidden (as built) and the first hidden instead."""
    await browser_page.set_content(LIVE.replace(HIDDEN, ""), wait_until="domcontentloaded")
    await browser_page.evaluate(
        """() => {
          const card = document.querySelector('[id$="Topcard"]');
          let row = card.querySelector('a[href*="/messaging/compose/"]');
          while (row && !Array.from(row.querySelectorAll('button')).some(
              b => (b.getAttribute('aria-label') || b.textContent).trim() === 'More')) {
            row = row.parentElement;
          }
          row.style.display = 'none';
        }"""
    )
    reading = await dom.read_named_profile(browser_page)
    assert reading["message_visible_in_topcard"] == 1
    assert named_profile.message_state(reading)[0] == named_profile.MESSAGE_FROM
    assert await browser_page.locator(dom.topcard_message_control_selector()).count() == 1


async def test_both_rows_shown_is_refused_before_anything_is_pressed(browser_page):
    reading = await _reading(browser_page, LIVE.replace(HIDDEN, ""))
    assert reading["message_visible_in_topcard"] == 2
    state, why = named_profile.message_state(reading)
    assert state == named_profile.UNKNOWN and "2 VISIBLE Message" in why
    assert await browser_page.locator(dom.topcard_message_control_selector()).count() == 2


async def test_THIS_CONTROL_CAN_FAIL_a_hidden_control_counted_would_read_two(browser_page):
    """Without the visibility test the topcard reads two Message controls --
    the live lane's broken More handle, one level down."""
    reading = await _reading(browser_page)
    assert reading["message_kind_in_topcard"] == 2
    assert reading["message_kind_in_topcard"] != reading["message_visible_in_topcard"]


async def test_a_first_degree_live_profile_draws_no_topcard_connect(browser_page):
    reading = await _reading(browser_page)
    assert reading["invite_visible_in_topcard"] == 0
    assert reading["invite_controls"] >= 1, "the rails' Connect controls are drawn"
    assert named_profile.connect_state(reading)[0] == named_profile.UNKNOWN


# ---------------------------------------------------------------------------
# 4. The read he names, on the live-true page
# ---------------------------------------------------------------------------


class _Navigator:
    def __init__(self, world: str):
        self.world = world
        self.gotos: list[str] = []

    async def goto(self, page, url, *, named_profile: bool = False, **_ignored):
        self.gotos.append(url)
        await page.set_content(self.world, wait_until="domcontentloaded", timeout=60_000)
        return url


class _Browser:
    def __init__(self, page, navigator):
        self.page = page
        self.navigator = navigator

    @contextlib.asynccontextmanager
    async def session(self):
        yield self.page

    async def goto(self, page, url, *, named_profile: bool = False, **_ignored):
        return await self.navigator.goto(page, url, named_profile=named_profile)


@pytest.fixture(autouse=True)
def _no_read_grant_survives_a_test():
    named_profile.discard_read_grants()
    yield
    named_profile.discard_read_grants()


async def test_the_read_returns_the_person_and_no_groups_from_the_live_page(
    monkeypatch, browser_page
):
    monkeypatch.setattr(server, "BROWSER", _Browser(browser_page, _Navigator(LIVE)))
    block = await server.linkedin_read_named_profile(LINK)
    result = await server.linkedin_read_named_profile(LINK, block["confirm_token"])
    assert result["identity_confirmed"] is True
    assert result["person"] == {
        "name": OWNER, "headline": HEADLINE, "link": LINK, "degree": None,
        people_data.UNTRUSTED_KEY: people_data.UNTRUSTED_NOTE,
    }, json.dumps(result)[:400]
    assert result["groups"] is None
    assert result["capture_hints"]["group_links_drawn"] == 0


def test_the_capture_holds_no_groups_section_so_n178_stays_gap():
    """THE CENSUS'S REASON, AS A FACT ABOUT THE FIXTURE: the live page, loaded
    once without a scroll, draws no Interests section and no link under
    /groups/ -- so no reader of a member's groups can be built over it, and
    ``N 178`` waits on the capture spec C-P7."""
    assert "Interests" not in LIVE
    assert "/groups/" not in LIVE
