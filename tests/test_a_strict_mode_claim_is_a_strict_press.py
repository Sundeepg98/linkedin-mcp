"""A comment that says "strict mode" holds a press must sit over a strict press.

THE DEFECT THIS ENCODES (the orchestrator's call (b) at lane L5's merge of
master 52b55b6, 2026-09-27). Eight sentences in the package said Playwright's
strict mode held a click to one element -- of ``mark_company_interest``,
``follow_company_page``, ``follow_company``, ``update_profile_field`` and
``withdraw_from_group`` -- while ``perform`` pressed all five with
``page.click(selector)`` and no ``strict=``. A page-level click is NOT strict
unless asked: it takes the first of several matches. So the property the
sentences described did not exist, and nothing could notice, because a comment
is not executed.

The code was moved to match, where each action's fixtures MEASURED exactly one
match at the moment of every press: ``writes.STRICT_PRESS_ACTIONS``. This file
holds the two together from both ends:

1. THE SET AND THE CALL. The set is pinned by name; ``perform``'s one click
   passes ``strict=press_strictly``, computed from that set; its one fill
   stays strict only for the named-person acts, the only fill measured.
2. THE CLAIMS. Every sentence of the claim shape ("strict mode holds" /
   "strict mode refuses") in the package is in a pinned table naming the
   action it is about, and that action must be in the set. A NEW claim
   arrives here as an unlisted sentence; an action leaving the set turns its
   sentence red. Shown failing both ways.
3. THE BEHAVIOUR, once, through the real call: a second OFF control drawn in
   the card WHILE the press waits stops the ``mark_company_interest`` press
   with the library's strict error, and the same world pressed without the
   set's membership is pressed -- so it is the strictness that stops it.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from linkedin_server import company_interest, writes
from linkedin_server.writes import consume, preview
from tests.test_mark_company_interest import _ACTION, _BASE, _SPEC, _URL, _derive
from tests.test_writes import (  # noqa: F401 -- two of these are fixtures
    JOB,
    FixtureNavigator,
    browser_page,
    writes_on,
)

PACKAGE = Path(writes.__file__).resolve().parent
WRITES = Path(writes.__file__)

#: THE SET, BY NAME. Seven since lane L5's merge of master 52b55b6; its
#: comment in writes.py gives each member's measurement.
PINNED_STRICT_PRESS_ACTIONS = frozenset(
    {
        "connect_from_profile",
        "message_from_profile",
        "mark_company_interest",
        "follow_company_page",
        "update_profile_field",
        "withdraw_from_group",
        "follow_company",
    }
)

#: EVERY CLAIM-SHAPED SENTENCE IN THE PACKAGE, by file and a phrase unique to
#: it, with the action it is about. Counted, not recalled: see
#: ``test_every_claim_in_the_package_is_in_the_table``.
CLAIMS: dict[tuple[str, str], str] = {
    ("company_interest.py", "strict mode holds the click to one element"): "mark_company_interest",
    ("dom.py", "strict mode refuses a click whose selector matches more"): "follow_company_page",
    ("profile_editor.py", "strict mode holds the click to exactly one element"): "update_profile_field",
    ("group_leave.py", "strict mode refuses the click if that stops being true -- TRUE"): "withdraw_from_group",
    ("writes.py", "strict mode holds it to the one OFF control in the card"): "mark_company_interest",
    ("writes.py", "strict mode refuses the click if that stops being true (since"): "withdraw_from_group",
    ("writes.py", "strict mode refuses the click if that stops being true between"): "follow_company_page",
    ("writes.py", "strict mode refuses a click whose selector matches more -- so"): "follow_company",
}

_CLAIM = re.compile(r"strict mode (?:holds|refuses)", re.IGNORECASE)


def _prose(source: str) -> str:
    """The file with comment markers dropped and whitespace collapsed, so a
    sentence broken across comment lines reads as one."""
    lines = []
    for line in source.splitlines():
        stripped = line.strip()
        while stripped.startswith("#"):
            stripped = stripped[1:].lstrip(":").strip()
        lines.append(stripped)
    return " ".join(" ".join(lines).split())


def _claims_by_file(sources: dict[str, str]) -> dict[str, int]:
    return {
        name: len(_CLAIM.findall(_prose(text)))
        for name, text in sources.items()
        if _CLAIM.search(_prose(text))
    }


def _package_sources() -> dict[str, str]:
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(PACKAGE.glob("*.py"))}


# ---------------------------------------------------------------------------
# 1. The set and the call
# ---------------------------------------------------------------------------


def test_the_strict_press_set_is_pinned_by_name():
    assert writes.STRICT_PRESS_ACTIONS == PINNED_STRICT_PRESS_ACTIONS
    assert writes.NAMED_PROFILE_ACTIONS < writes.STRICT_PRESS_ACTIONS
    assert writes.STRICT_PRESS_ACTIONS <= writes.PERFORMABLE


def _perform_assignments() -> dict[str, str]:
    tree = ast.parse(WRITES.read_text(encoding="utf-8"))
    perform = next(
        node
        for node in tree.body
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "perform"
    )
    out = {}
    for node in ast.walk(perform):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in ("press_strictly", "fill_strictly"):
                out[target.id] = ast.unparse(node.value)
    return out


def _strict_keyword_of(method: str) -> list[str]:
    tree = ast.parse(WRITES.read_text(encoding="utf-8"))
    found = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == method
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "page"
        ):
            for keyword in node.keywords:
                if keyword.arg == "strict":
                    found.append(ast.unparse(keyword.value))
    return found


def test_the_one_click_is_strict_by_the_set_and_the_fill_only_for_named_acts():
    assignments = _perform_assignments()
    assert assignments == {
        "press_strictly": "spec.action in STRICT_PRESS_ACTIONS",
        "fill_strictly": "spec.action in NAMED_PROFILE_ACTIONS",
    }, assignments
    assert _strict_keyword_of("click") == ["press_strictly"]
    assert _strict_keyword_of("fill") == ["fill_strictly"]


# ---------------------------------------------------------------------------
# 2. The claims
# ---------------------------------------------------------------------------


def test_every_claim_in_the_table_is_in_its_file_once_and_its_action_presses_strictly():
    sources = _package_sources()
    for (name, phrase), action in CLAIMS.items():
        prose = _prose(sources[name])
        assert prose.count(phrase) == 1, (name, phrase, prose.count(phrase))
        assert action in writes.STRICT_PRESS_ACTIONS, (
            f"{name} says strict mode holds {action}'s press, and {action} is "
            "not pressed strictly (writes.STRICT_PRESS_ACTIONS)"
        )


def test_every_claim_in_the_package_is_in_the_table():
    """COUNTED OFF THE SOURCE: a claim-shaped sentence the table does not list
    is a new claim nobody tied to a press."""
    expected: dict[str, int] = {}
    for name, _phrase in CLAIMS:
        expected[name] = expected.get(name, 0) + 1
    assert _claims_by_file(_package_sources()) == expected


def test_the_claim_rules_are_shown_failing():
    """A planted claim is counted, and an action removed from the set turns
    its sentence red -- neither rule can pass by looking at nothing."""
    sources = _package_sources()
    planted = dict(sources)
    planted["press.py"] = planted["press.py"] + (
        "\n# Playwright's strict mode holds this press to one element.\n"
    )
    counted = _claims_by_file(planted)
    assert counted.get("press.py") == 1, counted
    shrunk = writes.STRICT_PRESS_ACTIONS - {"withdraw_from_group"}
    red = [
        (name, phrase)
        for (name, phrase), action in CLAIMS.items()
        if action not in shrunk
    ]
    assert red == [
        ("group_leave.py", "strict mode refuses the click if that stops being true -- TRUE"),
        ("writes.py", "strict mode refuses the click if that stops being true (since"),
    ], red


# ---------------------------------------------------------------------------
# 3. The behaviour, once, through the real call
# ---------------------------------------------------------------------------

#: A layer that holds every press for 1.2 s, then lifts and runs the redraw --
#: a page re-rendered while a press waits, which is when Playwright resolves
#: the press's selector again (the technique of
#: ``tests/test_named_profile_route.py``).
_HOLD = (
    '<div id="press-hold" style="position:fixed;left:0;top:0;width:100%;'
    'height:100%;z-index:99999;background:transparent"></div>'
)
_OFF_BUTTON = 'button[data-view-name="org-member-company-interest-pipeline-interested-cta"]'
#: The OFF control replaced by a fresh copy (so the element the press resolved
#: is detached) and a SECOND copy drawn beside it, inside the same card. The
#: capture has no ``</body>``: its markup ends at ``</main>``, so the layer and
#: the script go in before it.
_TWIN_DRAWN_MID_PRESS = _derive(
    "</main>",
    _HOLD
    + "<script>setTimeout(function () {"
    "  var hold = document.getElementById('press-hold');"
    "  if (hold) { hold.parentNode.removeChild(hold); }"
    f"  var off = document.querySelector('{_OFF_BUTTON}');"
    "  if (off) {"
    "    var fresh = off.cloneNode(true);"
    "    off.replaceWith(fresh);"
    "    fresh.parentNode.appendChild(fresh.cloneNode(true));"
    "  }"
    "}, 1200);</script></main>",
)


async def _press_over(browser_page, world: str) -> dict:
    nav = FixtureNavigator({_URL: _BASE})
    block = await preview(_SPEC, target=JOB, navigator=nav, page=browser_page)
    grant = consume(block["to_confirm"], action=_ACTION, target=JOB)
    act = FixtureNavigator({_URL: [world, _BASE]})
    return await writes.perform(act, browser_page, grant)


async def test_a_second_control_drawn_mid_press_stops_the_strict_press(writes_on, browser_page):
    receipt = await _press_over(browser_page, _TWIN_DRAWN_MID_PRESS)
    assert receipt["clicked"]["selector"] == company_interest.OFF_CONTROL_IN_CARD
    assert receipt["clicked"]["clicks_made"] == 0, receipt["clicked"]
    # THE TYPE ONLY: a strict violation's message quotes every matched
    # element's outer HTML, and none of it may reach the receipt.
    assert receipt["clicked"]["error"] == "Error", receipt["clicked"]["error"]
    assert receipt["performed"] is not True


async def test_the_same_world_is_pressed_when_the_press_is_not_strict(
    writes_on, browser_page, monkeypatch
):
    """THE CONTROL: without the set's membership the same re-render is pressed
    -- the first of the two matches -- so the strictness is what stops it."""
    monkeypatch.setattr(
        writes, "STRICT_PRESS_ACTIONS", writes.STRICT_PRESS_ACTIONS - {_ACTION}
    )
    receipt = await _press_over(browser_page, _TWIN_DRAWN_MID_PRESS)
    assert receipt["clicked"]["clicks_made"] == 1, receipt["clicked"]
    assert receipt["clicked"]["error"] is None, receipt["clicked"]["error"]
