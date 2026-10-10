"""The read he names hands back two HANDLES -- lane NP, 2026-10-10.

``linkedin_read_named_profile`` returns, beside the person, the PROFILE OWNER'S
member token (for ``linkedin_people_search_shape(connections_of=...)``: census
``N 30``, ``N 85``, ``N 172``, ``N 31``) and the item keys of the posts its first
render draws in the Activity section, each with whose post it is (for
``linkedin_react_to_item``: ``M C32``). The caller passes them back as
arguments; nothing in the package consumes them.

THE FIXTURE is ``tests/fixtures/synthetic/named_profile_activity.html``, built by
``scripts/_build_named_profile_activity_skeleton.py`` from the live lane's
SESSION-7 skeleton of one first-degree profile the operator named (2026-10-10),
peopled with declared synthetic values only. Every variant below is DERIVED from
it by a DOM edit in the test, and says what it plants.

ONE BROWSER PER TEST FUNCTION, AND FEW FUNCTIONS: a browser launch measured 5 to
8 seconds on the shared box on 2026-10-10, against about one second for a read,
so the plants of one property run in a loop on one page rather than one
parametrised browser each -- the local gate stays under its two minutes.

THE SECTIONS:

1. The two fields on the shipped fixture; both absent where the read stops.
2. The token is absent whenever the chain does not close -- each step planted.
3. Whose item: owner, another member, unknown -- each rule planted.
4. Bounds and shapes: ten items, anchored keys, one Activity section.
5. What the handles are FOR, and that nothing in the package consumes them.
6. Controls: each check, weakened in the script, lets its plant through.

NOTHING HERE REACHES LINKEDIN: one local headless Chromium, ``set_content``.
"""
from __future__ import annotations

import ast
import pathlib
import re

from linkedin_server import dom, named_handles, named_profile, people_search, server, writes
from tests.test_writes import browser_page  # noqa: F401 -- a fixture

REPO = pathlib.Path(__file__).resolve().parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "synthetic" / "named_profile_activity.html"
ACTIVITY = FIXTURE.read_text(encoding="ascii")

SEGMENT = "casey-example-3f9a"
LINK = "https://www.linkedin.com/in/" + SEGMENT + "/"
OWNER = "Casey Example"
OWNER_MEMBER = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000002"
ANOTHER_MEMBER = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000003"
ITEM_ONE = "urn:li:activity:7400000000000000001"
ITEM_TWO = "urn:li:activity:7400000000000000002"
THE_TWO = [{"item": ITEM_ONE, "author": "owner"}, {"item": ITEM_TWO, "author": "owner"}]


async def _read(page, world: str = ACTIVITY, plant: str = "", arg=None) -> dict:
    """The confirmed read's answer off ``world``, after an optional DOM plant."""
    await page.set_content(world, wait_until="domcontentloaded", timeout=60_000)
    if plant:
        await page.evaluate(plant, arg)
    return await named_profile.read_the_confirmed_profile(page, segment=SEGMENT, landed=LINK)


async def _handles(page, plant: str = "", arg=None) -> dict:
    await page.set_content(ACTIVITY, wait_until="domcontentloaded", timeout=60_000)
    if plant:
        await page.evaluate(plant, arg)
    return await dom.read_named_profile_handles(page)


# ---------------------------------------------------------------------------
# 1. The two fields on the shipped fixture
# ---------------------------------------------------------------------------


async def test_the_read_returns_the_owners_token_and_the_activity_items(browser_page):
    out = await _read(browser_page)
    assert out["identity_confirmed"] is True
    assert out["member_token"] == OWNER_MEMBER, out["member_token_why"]
    assert out["activity_items"] == THE_TWO, out["activity_items_why"]
    chain = out["member_token_chain"]
    assert chain["message_control_is_the_owners_and_names_the_topcard_member"] is True
    assert chain["topcard_composer_links"] == chain["naming_the_topcard_member"] == 2
    # THREE CONNECTIONS LINKS AND FIVE PERMALINKS ON THE CAPTURE; HTML's parser,
    # loading the fixture, splits an anchor that nests another (the session-2
    # builder's note), so the DOM holds more anchors than the capture drew --
    # each split copy carrying the same address. Every one names the owner.
    assert chain["topcard_connections_links"] == chain["naming_the_topcard_member_too"] >= 3
    assert out["activity_counts"]["permalink_anchors"] >= 5
    assert out["member_token_use"] and out["activity_items_use"]

    handles = await _handles(browser_page)
    assert handles["member"] == OWNER_MEMBER and handles["member_why"] == "chain_closed"
    assert handles["activity_sections"] == 1
    assert handles["items"] == THE_TWO
    assert handles["unrecognised"] == handles["unpaired"] == handles["dropped"] == 0

    # WHERE THE READ STOPS, NEITHER FIELD: a landing elsewhere, and a page whose
    # title names somebody its topcard does not.
    await browser_page.set_content(ACTIVITY, wait_until="domcontentloaded", timeout=60_000)
    elsewhere = await named_profile.read_the_confirmed_profile(
        browser_page, segment=SEGMENT, landed="https://www.linkedin.com/in/someone-example-9/"
    )
    assert elsewhere["member_token"] is None and elsewhere["activity_items"] is None
    world = ACTIVITY.replace("<title>Casey Example | LinkedIn</title>",
                             "<title>Someone Example | LinkedIn</title>")
    assert world != ACTIVITY
    nobody = await _read(browser_page, world)
    assert nobody["identity_confirmed"] is False
    assert nobody["member_token"] is None and nobody["activity_items"] is None

    # NO ACTIVITY SECTION IS ABSENT, NOT EMPTY -- and the token does not hang on it.
    no_section = await _read(browser_page, plant=(
        "() => { for (const h of document.querySelectorAll('section h2'))"
        " if (h.textContent.trim() === 'Activity') h.textContent = 'Example'; }"
    ))
    assert no_section["activity_items"] is None
    assert no_section["member_token"] == OWNER_MEMBER


# ---------------------------------------------------------------------------
# 2. The token: absent whenever the chain does not close
# ---------------------------------------------------------------------------

#: The topcard element, as the reader finds it.
_CARD = "document.querySelector('[id$=\"Topcard\"]')"
_SWAP = ".split('ACoAASYNTHETICSYNTHETICSYNTHETIC0000002').join(other)"

#: PLANT: the topcard's LAST composer link (the hidden row's) names another member.
STRANGER_COMPOSER = (
    "(other) => { const links = " + _CARD + ".querySelectorAll('a[href*=\"/messaging/compose\"]');"
    " const a = links[links.length - 1];"
    " a.setAttribute('href', a.getAttribute('href')" + _SWAP + "); }"
)
#: PLANT: one of the topcard's connections links names another member.
STRANGER_CONNECTIONS = (
    "(other) => { const a = " + _CARD + ".querySelector('a[href*=\"connectionOf\"]');"
    " a.setAttribute('href', a.getAttribute('href')" + _SWAP + "); }"
)
#: PLANT: the topcard's id carries no member.
NO_MEMBER_ID = "() => { " + _CARD + ".id = 'com.linkedin.sdui.profile.card.somethingTopcard'; }"
#: PLANT: the topcard draws no composer link -- each becomes a conversation link.
NO_COMPOSER = (
    "() => { for (const a of " + _CARD + ".querySelectorAll('a[href*=\"/messaging/compose\"]'))"
    " a.setAttribute('href', '/messaging/thread/example/'); }"
)
#: PLANT: the VISIBLE row's composer link names another member.
STRANGER_VISIBLE_COMPOSER = (
    "(other) => { const a = " + _CARD + ".querySelector('a[href*=\"/messaging/compose\"]');"
    " a.setAttribute('href', a.getAttribute('href')" + _SWAP + "); }"
)

CHAIN_PLANTS = (
    (STRANGER_COMPOSER, "a_composer_link_names_another_member"),
    (STRANGER_CONNECTIONS, "a_connections_link_names_another_member"),
    (NO_MEMBER_ID, "topcard_id_names_no_member"),
    (NO_COMPOSER, "no_composer_link_in_topcard"),
)


async def test_the_token_is_absent_when_any_step_of_the_chain_fails(browser_page):
    for plant, why in CHAIN_PLANTS:
        handles = await _handles(browser_page, plant, ANOTHER_MEMBER)
        assert handles["member"] is None and handles["member_why"] == why, why
        out = await _read(browser_page, plant=plant, arg=ANOTHER_MEMBER)
        assert out["member_token"] is None, (why, out["member_token_why"])
        assert ANOTHER_MEMBER not in str(out), "an id of anyone else left the read"
        assert out["activity_items"] == THE_TWO, "the items do not hang on the token"
    # M M1's OWN CHAIN -- the engine's reading of the one VISIBLE Message
    # control -- fails before the page's chain is asked.
    out = await _read(browser_page, plant=STRANGER_VISIBLE_COMPOSER, arg=ANOTHER_MEMBER)
    assert out["member_token"] is None
    assert out["member_token_chain"][
        "message_control_is_the_owners_and_names_the_topcard_member"] is False
    assert ANOTHER_MEMBER not in str(out)


# ---------------------------------------------------------------------------
# 3. Whose item
# ---------------------------------------------------------------------------

_ITEM = "document.querySelectorAll('[role=\"listitem\"]')"
_OVERFLOW = "'button[aria-label^=\"Open control menu for post by \"]'"


def _second_item(statement: str) -> str:
    return "() => { const root = " + _ITEM + "[1]; " + statement + " }"


ACTOR_IS_ANOTHER = _second_item(
    "const a = root.querySelector('a[href*=\"/in/\"]');"
    " a.setAttribute('href', 'https://www.linkedin.com/in/someone-example-9/');"
)
AUTHOR_IS_ANOTHER = _second_item(
    "for (const b of root.querySelectorAll(" + _OVERFLOW + "))"
    " b.setAttribute('aria-label', 'Open control menu for post by Someone Example');"
)
TWO_OVERFLOWS = _second_item(
    "const b = root.querySelector(" + _OVERFLOW + ");"
    " root.insertAdjacentHTML('beforeend', b.outerHTML);"
)
NO_OVERFLOW = _second_item(
    "for (const b of root.querySelectorAll(" + _OVERFLOW + "))"
    " b.setAttribute('aria-label', 'Example label');"
)
NO_ACTOR = _second_item(
    "const first = root.querySelector('a[href*=\"/feed/update/\"]');"
    " for (const a of root.querySelectorAll('a[href*=\"/in/\"]')) {"
    "   if (first.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_PRECEDING)"
    "     a.setAttribute('href', '/jobs/'); }"
)
MENTION_BEFORE = _second_item(
    "const first = root.querySelector('a[href*=\"/feed/update/\"]');"
    " first.insertAdjacentHTML('beforebegin', '<a href=\"/in/someone-example-8/\">X</a>');"
)
SHORTENED_NAME = _second_item(
    "for (const b of root.querySelectorAll(" + _OVERFLOW + "))"
    " b.setAttribute('aria-label', 'Open control menu for post by Casey E');"
)

ITEM_PLANTS = (
    (ACTOR_IS_ANOTHER, "another_member"),
    (AUTHOR_IS_ANOTHER, "another_member"),
    (MENTION_BEFORE, "another_member"),
    (TWO_OVERFLOWS, "unknown"),
    (NO_OVERFLOW, "unknown"),
    (NO_ACTOR, "unknown"),
    # LinkedIn is measured to shorten his own name in the overflow label; the
    # prefix rule linkedin_my_activity_items applies is applied here.
    (SHORTENED_NAME, "owner"),
)


async def test_whose_item_it_is_follows_its_author_and_its_actors(browser_page):
    for plant, kind in ITEM_PLANTS:
        handles = await _handles(browser_page, plant)
        assert handles["items"] == [
            {"item": ITEM_ONE, "author": "owner"},
            {"item": ITEM_TWO, "author": kind},
        ], kind
    # MEASURED on the session-7 skeleton: the first item's text links other
    # members AFTER its first permalink -- mentions, not actors -- and the item
    # is still the owner's.
    handles = await _handles(browser_page)
    mentions = await browser_page.evaluate(
        "() => Array.from(document.querySelectorAll('[role=\"listitem\"]')[0]"
        ".querySelectorAll('a[href*=\"/in/someone-example-\"]')).length"
    )
    assert mentions >= 1
    assert handles["items"][0] == {"item": ITEM_ONE, "author": "owner"}


# ---------------------------------------------------------------------------
# 4. Bounds and shapes
# ---------------------------------------------------------------------------

#: PLANT: twelve more items, each a copy of the first with its own key. The key
#: is assembled in the page from pieces, so no whole urn stands in this file
#: (tests/test_no_committed_identity.py sweeps for the shape).
TWELVE_MORE = (
    "() => { const root = document.querySelectorAll('[role=\"listitem\"]')[0];"
    " const head = ['urn', 'li', 'activity'].join(':') + ':';"
    " for (let i = 0; i < 12; i += 1) {"
    "   const copy = root.cloneNode(true);"
    "   for (const a of copy.querySelectorAll('a[href*=\"/feed/update/\"]'))"
    "     a.setAttribute('href', '/feed/update/' + head + '7400000000000' + String(100000 + i) + '/');"
    "   root.parentNode.insertAdjacentElement('beforeend', copy); } }"
)
#: PLANT: the second item's permalinks carry a key of another shape.
ODD_KEY = (
    "() => { for (const a of document.querySelectorAll('[role=\"listitem\"]')[1]"
    ".querySelectorAll('a[href*=\"/feed/update/\"]'))"
    " a.setAttribute('href', '/feed/update/urn:li:activity:example/'); }"
)


async def test_at_most_ten_items_and_only_anchored_keys_come_back(browser_page):
    out = await _read(browser_page, plant=TWELVE_MORE)
    assert len(out["activity_items"]) == 10
    assert out["activity_counts"]["truncated"] is True
    assert "more than the ten returned" in out["activity_items_why"]
    handles = await _handles(browser_page, ODD_KEY)
    assert handles["unrecognised"] >= 1
    assert [item["item"] for item in handles["items"]] == [ITEM_ONE]


def test_the_token_shape_is_the_one_people_search_takes():
    assert dom.NAMED_MEMBER_TOKEN.pattern == people_search._MEMBER_TOKEN.pattern


def test_the_closed_vocabularies_are_the_ones_the_script_writes():
    for why in dom.NAMED_MEMBER_WHY:
        assert "'" + why + "'" in dom.NAMED_HANDLES_JS, why
    for kind in dom.NAMED_ITEM_AUTHOR_KINDS:
        assert "'" + kind + "'" in dom.NAMED_HANDLES_JS, kind
    assert set(named_handles.MEMBER_WHY_SENTENCES) == set(dom.NAMED_MEMBER_WHY)


# ---------------------------------------------------------------------------
# 5. What the handles are for -- and that nothing consumes them
# ---------------------------------------------------------------------------


async def test_the_handles_are_the_arguments_the_two_tools_take(browser_page):
    out = await _read(browser_page)
    built = people_search.compose(connections_of=out["member_token"], network="F")
    assert built["built"] is True and built["applied"]["connections_of"] == 1
    spec = writes.SANCTIONED_WRITES["linkedin_react_to_item"]
    for entry in out["activity_items"]:
        assert spec.url_pattern.fullmatch(spec.url_template.format(target=entry["item"]))


def _importers_of(module: str) -> list[str]:
    found = []
    for path in sorted((REPO / "linkedin_server").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "linkedin_server":
                if any(alias.name == module for alias in node.names):
                    found.append(path.stem)
            elif isinstance(node, ast.Import):
                if any(alias.name == "linkedin_server." + module for alias in node.names):
                    found.append(path.stem)
    return sorted(set(found))


def test_one_module_reaches_the_handles_and_it_is_the_read():
    assert _importers_of("named_handles") == ["named_profile"]


def test_the_handles_module_navigates_nowhere_and_keeps_nothing():
    source = (REPO / "linkedin_server" / "named_handles.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    attrs = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert not ({"goto", "BROWSER", "page"} & (names | attrs))
    module_state = [
        node for node in tree.body
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        and isinstance(getattr(node, "value", None), (ast.List, ast.Set))
    ]
    assert module_state == [], "a module-level container could keep a handle"


def test_the_tool_and_its_preview_declare_both_fields():
    doc = server.linkedin_read_named_profile.__doc__ or ""
    assert "member_token" in doc and "activity_items" in doc
    preview = named_profile.read_preview(SEGMENT)
    assert "member_token" in preview["on_confirm"] and "activity_items" in preview["on_confirm"]
    named_profile.discard_read_grants()


# ---------------------------------------------------------------------------
# 6. Controls: each check, weakened, lets its plant through
# ---------------------------------------------------------------------------

#: (the check in the script, what it is weakened to, the plant it vetoes, and
#: what the weakened script then says).
CONTROLS = (
    ("named.every((m) => m === member)", "true", STRANGER_COMPOSER, "token"),
    ("list[0] === member", "true", STRANGER_CONNECTIONS, "token"),
    ("if (!own.has(seg)) ownActors = false;", "", ACTOR_IS_ANOTHER, "owner"),
    ("const related = shorter >= cfg.minAuthorChars",
     "const related = true || shorter >= cfg.minAuthorChars", AUTHOR_IS_ANOTHER, "owner"),
    # WITHOUT THE STOP AT THE FIRST PERMALINK, the first item's mentions become
    # its actors and the owner's own post reads as a stranger's.
    ("if (path !== null && path.indexOf(marker) === 0) break;", "", "", "first_is_another"),
)


async def test_control_each_check_weakened_lets_its_plant_through(browser_page, monkeypatch):
    shipped = dom.NAMED_HANDLES_JS
    for check, weakened, plant, says in CONTROLS:
        assert check in shipped, check
        monkeypatch.setattr(dom, "NAMED_HANDLES_JS", shipped.replace(check, weakened))
        handles = await _handles(browser_page, plant, ANOTHER_MEMBER if plant else None)
        if says == "token":
            assert handles["member"] == OWNER_MEMBER, check
        elif says == "owner":
            assert handles["items"][1]["author"] == "owner", check
        else:
            assert handles["items"][0]["author"] == "another_member", check
    monkeypatch.setattr(dom, "NAMED_HANDLES_JS", shipped)


def test_the_fixture_holds_only_declared_synthetic_values():
    declared = (OWNER_MEMBER, ANOTHER_MEMBER, OWNER_MEMBER[:-1] + "1", OWNER_MEMBER[:-1] + "4")
    for found in re.findall(r"ACoAA[A-Za-z0-9_-]+", ACTIVITY):
        assert found in declared, found
    for found in re.findall(r"urn:li:activity:([0-9]+)", ACTIVITY):
        assert found.startswith("74000000000000000"), found
    slugs = set(re.findall(r"/in/([A-Za-z0-9%_-]+)/", ACTIVITY))
    assert slugs
    for slug in slugs:
        assert slug == SEGMENT or slug.startswith("someone-example-"), slug
