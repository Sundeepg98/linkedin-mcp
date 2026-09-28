"""The read he names -- ruling NAMED-PROFILE-READ-BEHIND-A-GRANT.

THE RULING (the operator, 2026-09-28 08:01, verbatim: "Yes, I'm giving you
permission."; ``_audit/2026-09-28-rulings-named-profile-read.md``): a read of
a member's profile he names in the call -- by link or member id, never a name
read off a page -- behind the single-use grant; its preview states that
LinkedIn may show the member the view; the declared fields leave as people
records; never for a measurement. The mitigations the question put to him,
each held below by a test that can fail:

1. ONLY A LINK OR MEMBER ID HE NAMES -- a name, a bare word or a sub-page is
   refused before a browser is touched, and before a grant exists.
2. A SINGLE-USE CONFIRMATION FOR EACH VIEW, STATING THE POSSIBLE TRACE -- the
   preview loads NOTHING and says the member may be shown the view; the token
   works once, for one profile, within the writes' two minutes.
3. ONE PAGE PER CALL, DECLARED FIELDS ONLY AS PEOPLE RECORDS -- the confirmed
   call makes exactly one navigation, through the second door, and returns
   the person as a record; the groups and the degree are ABSENT, because no
   capture shows them.
4. NOTHING STORED -- no grant outlives its use, and nothing the page drew is
   left in the module.

And the two conditions of the ruling that are about WHO may use it: the
second door's read caller is ONE function, reached from ONE tool, and no
script -- a probe, a census, an instrument -- names the read at all.

THE SECTIONS:

1. The register: the ruling entry the order specified, and the id it amends.
2. The target: a name is refused before anything.
3. The preview: nothing loaded, the trace stated, a token.
4. The token: once, one profile, two minutes.
5. The confirmed read: one load, the record, the absent fields.
6. The doors and the callers: never for a measurement.
7. Controls: each property above, planted false, is caught.

NOTHING HERE REACHES LINKEDIN. The page is
``tests/fixtures/synthetic/named_profile.html``, served into a local headless
Chromium by a navigator double that records every ask.
"""
from __future__ import annotations

import ast
import contextlib
import json
import pathlib

import pytest

from linkedin_server import named_profile, people_data, readonly, server, writes
from linkedin_server.errors import WriteAttemptError
from tests.test_messaging_threads import _derive
from tests.test_named_profile_route import (
    HEADLINE,
    LINK,
    MEMBER_ID,
    OWNER,
    PROFILE,
    SEGMENT,
    STRANGERS,
    THEIR_WORDS,
)
from tests.test_writes import browser_page  # noqa: F401 -- a fixture

REPO = pathlib.Path(__file__).resolve().parent.parent
MEMBER_LINK = "https://www.linkedin.com/in/" + MEMBER_ID + "/"

#: DERIVED -- the profile draws an Interests card with a Groups tab and two
#: group links, as a DERIVED guess at LinkedIn's markup. No capture shows a
#: member's groups (NEEDS-CAPTURE C-P7), so the read must not read them: the
#: groups stay ABSENT whatever the page draws, and only the hint counts links.
WITH_GROUPS = _derive(
    PROFILE,
    '<section class="about">',
    '<section class="interests"><h2>Interests</h2>'
    '<div role="tablist"><button role="tab" aria-selected="true">Groups</button></div>'
    '<ul><li><a href="/groups/1234501/">Example Group One</a></li>'
    '<li><a href="/groups/1234502/">Example Group Two</a></li></ul></section>'
    '<section class="about">',
)
#: DERIVED -- a page that is not one person's profile: its topcard removed.
NO_TOPCARD = _derive(
    PROFILE,
    'id="com.linkedin.sdui.profile.card.refACoAASYNTHETICSYNTHETICSYNTHETIC0000002Topcard"',
    'id="com.linkedin.sdui.profile.card.somethingElse"',
)
GROUP_TITLES = ("Example Group One", "Example Group Two")


@pytest.fixture(autouse=True)
def _no_read_grant_survives_a_test():
    named_profile.discard_read_grants()
    yield
    named_profile.discard_read_grants()


class _Navigator:
    """Serves one frozen world, LANDS where the test says, records every ask."""

    def __init__(self, world: str = PROFILE, *, landed: str | None = None):
        self.world = world
        self.landed = landed
        self.gotos: list[str] = []
        self.named: list[bool] = []

    async def goto(self, page, url: str, *, named_profile: bool = False) -> str:
        self.gotos.append(url)
        self.named.append(named_profile)
        await page.set_content(self.world, wait_until="domcontentloaded", timeout=60_000)
        return self.landed if self.landed is not None else url


class _Browser:
    """``server.BROWSER`` for a tool test: a session yields the test's page,
    and ``goto`` is the navigator double's. Counts sessions opened."""

    def __init__(self, page, navigator: _Navigator):
        self.page = page
        self.navigator = navigator
        self.sessions = 0

    @contextlib.asynccontextmanager
    async def session(self):
        self.sessions += 1
        yield self.page

    async def goto(self, page, url, *, named_profile: bool = False, **_ignored):
        return await self.navigator.goto(page, url, named_profile=named_profile)


class _NoBrowser:
    """A browser that fails the test the moment anything asks for a session."""

    sessions = 0

    def session(self):
        raise AssertionError("the tool opened a browser")

    async def goto(self, *_args, **_kwargs):
        raise AssertionError("the tool navigated")


def _clean(value, *, allow_owner: bool = False) -> None:
    """Nothing the page drew about anybody else -- and, unless allowed, not
    the owner either -- anywhere in ``value``."""
    text = json.dumps(value)
    needles = STRANGERS + THEIR_WORDS + GROUP_TITLES + (
        () if allow_owner else (OWNER, HEADLINE)
    )
    for needle in needles:
        assert needle not in text, f"{needle!r} leaked into: {text[:400]}"


async def _preview(monkeypatch, given: str = LINK) -> dict:
    monkeypatch.setattr(server, "BROWSER", _NoBrowser())
    return await server.linkedin_read_named_profile(given)


# ---------------------------------------------------------------------------
# 1. The register: the entry the order specified, and the id it amends
# ---------------------------------------------------------------------------


def _entry():
    from scripts import build_rulings_index as bri

    found = [r for r in bri.REGISTER if r.id == "NAMED-PROFILE-READ-BEHIND-A-GRANT"]
    assert len(found) == 1, found
    return found[0]


def test_the_ruling_is_registered_with_the_fields_the_order_gave():
    entry = _entry()
    assert entry.claim == (
        "A read of a member's profile he names in the call -- by link or "
        "member id, never a name read off a page -- is built behind the "
        "single-use grant, its preview stating that LinkedIn may show the "
        "member the view; declared fields leave as people records; never for "
        "a measurement."
    )
    assert entry.binds == "read boundary -- a third-party profile he names"
    assert entry.document == "_audit/2026-09-28-rulings-named-profile-read.md"
    assert entry.anchor == 'RULED: (operator, 2026-09-28 08:01, verbatim) "Yes, I\'m giving you permission."'
    assert entry.note == (
        "The operator's ruling, verbatim in its document; mitigations as the "
        "question put them."
    )
    text = (REPO / entry.document).read_text(encoding="utf-8")
    assert text.count(entry.anchor) == 1, "the anchor must name ONE line of his words"


def test_the_amended_id_is_the_family_that_carries_his_2026_09_04_removal():
    """``AMENDS NO-THIRD-PARTY-PROFILE-LOAD``: the rulings register holds no
    entry for his 2026-09-04 call, and the exclusion register does -- a family
    the OPERATOR made (``op=YES``), anchored on the removal's own comment."""
    from scripts import check_exclusion_basis as ceb

    entry = _entry()
    assert entry.status == "AMENDS NO-THIRD-PARTY-PROFILE-LOAD"
    family = ceb.FAMILIES["NO-THIRD-PARTY-PROFILE-LOAD"]
    assert family.op == "YES" and family.made_by == "OPERATOR", family
    anchors = " ".join(anchor for _path, anchor in family.sources)
    assert "THE THIRD-PARTY PROFILE PATTERN WAS REMOVED 2026-09-04" in anchors


# ---------------------------------------------------------------------------
# 2. The target: a name is refused before anything
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "given",
    [
        OWNER,                                   # a name, with a space
        "casey",                                 # a bare word
        "Casey-Example",                         # still a bare word
        "https://www.linkedin.com/in/me/",       # his own profile
        LINK + "details/interests/",             # a sub-page -- the groups tab
        "https://www.example.org/in/casey-example-3f9a/",
        "casey" + chr(0x200B) + "example",
        "",
    ],
)
async def test_a_name_or_anything_not_a_profile_is_refused_before_a_browser_or_a_grant(
    monkeypatch, given
):
    monkeypatch.setattr(server, "BROWSER", _NoBrowser())
    for token in ("", "a-token"):
        result = await server.linkedin_read_named_profile(given, token)
        assert result.get("error"), result
        assert "confirm_token" not in result
    assert named_profile._READ_GRANTS == {}, "a refused target minted a grant"


# ---------------------------------------------------------------------------
# 3. The preview: nothing loaded, the trace stated, a token
# ---------------------------------------------------------------------------


async def test_the_preview_loads_nothing_and_states_the_view(monkeypatch):
    block = await _preview(monkeypatch)
    assert block["loaded"] is False and block["pages_loaded"] == 0
    assert block["profile_this_loads"] == LINK
    assert block["given_as"] == "a profile link"
    assert "LinkedIn may show this member that you viewed their profile" in (
        block["they_may_see_this_view"]
    )
    assert block["whom_this_resolves_to"] is None, "a name the preview could not have read"
    assert "NOT READ" in block["whom_this_resolves_to_why"]
    assert "ABSENT" in block["on_confirm"]["groups"]
    assert block["expires_in_seconds"] == int(writes.GRANT_TTL_SECONDS)
    assert set(named_profile._READ_GRANTS) == {block["confirm_token"]}
    assert "member_id_landing" not in block
    _clean(block)


async def test_a_member_id_preview_says_a_redirect_returns_nothing(monkeypatch):
    for given in (MEMBER_ID, "urn:li:fsd_profile:" + MEMBER_ID):
        block = await _preview(monkeypatch, given)
        assert block["profile_this_loads"] == MEMBER_LINK
        assert block["given_as"] == "a member id"
        assert "returns NOTHING" in block["member_id_landing"]
        assert "C-P6" in block["member_id_landing"]


def test_the_read_grant_lives_as_long_as_a_write_grant():
    assert named_profile.READ_GRANT_TTL_SECONDS == writes.GRANT_TTL_SECONDS


def test_the_read_is_no_write():
    """A READ: in no write table, not named like a write, and no write door
    accepts its action."""
    assert "linkedin_read_named_profile" not in writes.SANCTIONED_WRITES
    assert named_profile.READ_ACTION not in {s.action for s in writes.SANCTIONED_WRITES.values()}
    assert not readonly.name_implies_write("linkedin_read_named_profile")
    assert "linkedin_read_named_profile" in people_data.PEOPLE_TOOLS


# ---------------------------------------------------------------------------
# 4. The token: once, one profile, two minutes
# ---------------------------------------------------------------------------


async def test_a_token_reads_once_and_a_replay_loads_nothing(monkeypatch, browser_page):
    block = await _preview(monkeypatch)
    nav = _Navigator()
    browser = _Browser(browser_page, nav)
    monkeypatch.setattr(server, "BROWSER", browser)
    first = await server.linkedin_read_named_profile(LINK, block["confirm_token"])
    assert first["loaded"] is True and nav.gotos == [LINK]
    second = await server.linkedin_read_named_profile(LINK, block["confirm_token"])
    assert second.get("error") and "already-used" in second["message"], second
    assert nav.gotos == [LINK], "a replayed token navigated"


async def test_a_token_minted_for_one_profile_loads_no_other(monkeypatch, browser_page):
    block = await _preview(monkeypatch)
    nav = _Navigator()
    monkeypatch.setattr(server, "BROWSER", _Browser(browser_page, nav))
    for other in (MEMBER_ID, "https://www.linkedin.com/in/jordan-example-7c1d/"):
        result = await server.linkedin_read_named_profile(other, block["confirm_token"])
        assert result.get("error") and "different profile" in result["message"], result
    assert nav.gotos == []
    assert "jordan-example" not in json.dumps(result), "the refusal quoted a link"


async def test_an_expired_token_loads_nothing(monkeypatch, browser_page):
    block = await _preview(monkeypatch)
    grant = named_profile._READ_GRANTS[block["confirm_token"]]
    grant.minted_at -= named_profile.READ_GRANT_TTL_SECONDS + 1
    nav = _Navigator()
    monkeypatch.setattr(server, "BROWSER", _Browser(browser_page, nav))
    result = await server.linkedin_read_named_profile(LINK, block["confirm_token"])
    assert result.get("error") and "expired" in result["message"], result
    assert nav.gotos == [] and named_profile._READ_GRANTS == {}


async def test_an_unminted_token_loads_nothing(monkeypatch, browser_page):
    nav = _Navigator()
    monkeypatch.setattr(server, "BROWSER", _Browser(browser_page, nav))
    result = await server.linkedin_read_named_profile(LINK, "made-up-token")
    assert result.get("error"), result
    assert nav.gotos == []


async def test_a_grant_loads_once_even_if_handed_back(browser_page):
    """Single-use at the LOAD as well as at the token: a grant object that was
    consumed and loaded cannot reach the door again, however it is handed in."""
    grant = named_profile.mint_read_grant(SEGMENT)
    nav = _Navigator()
    await named_profile.load_the_confirmed_profile(
        nav, browser_page, token=grant.token, segment=SEGMENT
    )
    named_profile._READ_GRANTS[grant.token] = grant   # a registry tampered with
    with pytest.raises(WriteAttemptError):
        await named_profile.load_the_confirmed_profile(
            nav, browser_page, token=grant.token, segment=SEGMENT
        )
    assert nav.gotos == [LINK]


@pytest.mark.parametrize("case", ["unminted", "replayed", "expired", "another profile"])
async def test_a_token_that_would_be_refused_opens_no_browser(monkeypatch, browser_page, case):
    """FOUND BY THE COLD CHECK OF 2026-09-28: each refusal was reached inside a
    browser session the tool had already opened. It is refused before one."""
    nav = _Navigator()
    browser = _Browser(browser_page, nav)
    token = "made-up-token"
    if case != "unminted":
        block = await _preview(monkeypatch)
        token = block["confirm_token"]
    monkeypatch.setattr(server, "BROWSER", browser)
    given = LINK
    if case == "replayed":
        await server.linkedin_read_named_profile(LINK, token)
    elif case == "expired":
        named_profile._READ_GRANTS[token].minted_at -= named_profile.READ_GRANT_TTL_SECONDS + 1
    elif case == "another profile":
        given = MEMBER_ID
    before = browser.sessions
    result = await server.linkedin_read_named_profile(given, token)
    assert result.get("error"), result
    assert browser.sessions == before, "a refused token opened a browser session"


def test_expired_grants_are_swept_on_the_next_mint():
    stale = named_profile.mint_read_grant(SEGMENT)
    stale.minted_at -= named_profile.READ_GRANT_TTL_SECONDS + 1
    fresh = named_profile.mint_read_grant(SEGMENT)
    assert set(named_profile._READ_GRANTS) == {fresh.token}


# ---------------------------------------------------------------------------
# 5. The confirmed read: one load, the record, the absent fields
# ---------------------------------------------------------------------------


async def _confirmed(monkeypatch, page, world: str = PROFILE, *, given: str = LINK,
                     landed: str | None = None):
    block = await _preview(monkeypatch, given)
    nav = _Navigator(world, landed=landed)
    browser = _Browser(page, nav)
    monkeypatch.setattr(server, "BROWSER", browser)
    result = await server.linkedin_read_named_profile(given, block["confirm_token"])
    return result, nav, browser


async def test_the_confirmed_read_loads_once_through_the_named_door(monkeypatch, browser_page):
    result, nav, browser = await _confirmed(monkeypatch, browser_page)
    assert nav.gotos == [LINK] and nav.named == [True], "one load, through the second door"
    assert browser.sessions == 1
    assert result["pages_loaded"] == 1 and result["profile_loaded"] == LINK
    assert result["landed_on_the_named_profile"] is True
    assert result["identity_confirmed"] is True


async def test_the_person_comes_back_as_a_people_record(monkeypatch, browser_page):
    result, _nav, _browser = await _confirmed(monkeypatch, browser_page)
    person = result["person"]
    assert person == {
        "name": OWNER,
        "headline": HEADLINE,
        "link": LINK,
        "degree": None,
        people_data.UNTRUSTED_KEY: people_data.UNTRUSTED_NOTE,
    }, person
    assert isinstance(people_data.as_record(person), people_data.Person)
    _clean({k: v for k, v in result.items() if k != "person"})


async def test_the_groups_stay_absent_whatever_the_page_draws(monkeypatch, browser_page):
    """BUILT ONLY OVER CAPTURED MARKUP: the page below draws two group links,
    a DERIVED guess at LinkedIn's Interests card, and the read still returns no
    group -- only the hint for the capture, a count."""
    result, _nav, _browser = await _confirmed(monkeypatch, browser_page, WITH_GROUPS)
    assert result["groups"] is None and "ABSENT" in result["groups_why"]
    assert result["capture_hints"]["group_links_drawn"] == 2
    _clean({k: v for k, v in result.items() if k != "person"})


async def test_a_member_id_redirected_elsewhere_reads_nothing(monkeypatch, browser_page):
    result, nav, _browser = await _confirmed(
        monkeypatch, browser_page, given=MEMBER_ID, landed=LINK
    )
    assert nav.gotos == [MEMBER_LINK], "the address composed from HIS argument"
    assert result["landed_on_the_named_profile"] is False
    assert result["person"] is None and result["identity_confirmed"] is False
    assert result["what_the_page_showed"] == {} and result["capture_hints"] == {}
    assert SEGMENT not in json.dumps(result), "the landing was published"
    _clean(result)


async def test_a_page_that_names_no_one_person_returns_no_record(monkeypatch, browser_page):
    result, _nav, _browser = await _confirmed(monkeypatch, browser_page, NO_TOPCARD)
    assert result["identity_confirmed"] is False and result["person"] is None
    assert result["what_the_page_showed"]["topcards"] == 0
    _clean(result)


async def test_nothing_is_kept_after_the_read(monkeypatch, browser_page):
    """NOTHING STORED: no grant is left, and nothing the page drew is held in
    the module that read it."""
    result, _nav, _browser = await _confirmed(monkeypatch, browser_page)
    assert result["person"]["name"] == OWNER
    assert named_profile._READ_GRANTS == {}
    held = repr({k: v for k, v in vars(named_profile).items() if not k.startswith("__")})
    for needle in (OWNER, HEADLINE) + STRANGERS + THEIR_WORDS:
        assert needle not in held, f"{needle!r} is held by the module"


# ---------------------------------------------------------------------------
# 6. The doors and the callers: never for a measurement
# ---------------------------------------------------------------------------


def _sources(folder: str):
    for path in sorted((REPO / folder).rglob("*.py")):
        yield path, ast.parse(path.read_text(encoding="utf-8"))


def _names_in(tree) -> set[str]:
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            out.add(node.id)
        elif isinstance(node, ast.Attribute):
            out.add(node.attr)
        elif isinstance(node, ast.ImportFrom):
            out.update(alias.name for alias in node.names)
    return out


#: Every name by which the read could be reached.
_THE_READ = frozenset({
    "linkedin_read_named_profile", "read_preview", "mint_read_grant",
    "consume_read_grant", "load_the_confirmed_profile", "read_the_confirmed_profile",
})


def _scripts_naming_the_read(root: pathlib.Path) -> list[tuple[str, str]]:
    return sorted(
        (path.name, name)
        for path in sorted((root / "scripts").rglob("*.py"))
        for name in _names_in(ast.parse(path.read_text(encoding="utf-8"))) & _THE_READ
    )


def test_no_script_can_reach_the_read():
    """NEVER FOR A MEASUREMENT, as a fact about the tree: no file under
    ``scripts/`` -- where every probe, census and instrument lives -- names
    the read by any of its names."""
    assert _scripts_naming_the_read(REPO) == []


def test_one_tool_reaches_the_reads_load_and_nothing_else_in_the_package_does():
    callers = set()
    for path, tree in _sources("linkedin_server"):
        for function in ast.walk(tree):
            if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if "load_the_confirmed_profile" in _names_in(function) and (
                function.name != "load_the_confirmed_profile"
            ):
                callers.add((path.name, function.name))
    assert callers == {("server.py", "linkedin_read_named_profile")}, callers


def test_the_read_door_still_refuses_the_address_the_read_loads():
    for url in (LINK, MEMBER_LINK):
        assert readonly.assert_named_profile_url(url) == url
        assert not readonly.is_read_url(url)
        with pytest.raises(WriteAttemptError):
            readonly.assert_read_url(url)


def test_the_permanent_refusal_is_narrowed_to_this_read_and_keeps_its_ground():
    entry = writes.PERMANENTLY_FORBIDDEN["load_a_third_partys_profile_to_measure_a_control"]
    assert "NAMED-PROFILE-READ-BEHIND-A-GRANT" in entry
    assert "linkedin_read_named_profile" in entry
    assert "exactly ONE read" in entry
    assert "A load for a measurement" in entry and "stays forbidden" in entry
    assert "linkedin_who_viewed_me returns rows" in entry, "the measured ground was dropped"


# ---------------------------------------------------------------------------
# 7. Controls: each property, planted false, is caught
# ---------------------------------------------------------------------------


async def test_control_a_preview_that_loads_is_caught(monkeypatch):
    """The preview test drives the tool with a browser that fails on any
    session. A preview that opened one comes back an error, and the test's
    first read of its block fails."""
    original = named_profile.read_preview

    def loading_preview(segment):
        with server.BROWSER.session():
            pass
        return original(segment)

    monkeypatch.setattr(named_profile, "read_preview", loading_preview)
    with pytest.raises((AssertionError, KeyError)):
        await test_the_preview_loads_nothing_and_states_the_view(monkeypatch)


async def test_control_a_reusable_token_is_caught(monkeypatch, browser_page):
    """With a registry that FORGETS each use -- a fresh, unused grant put back
    under the same token -- the replay test's second call loads again, and
    that test's assertions refuse it. (The first version of this control reset
    the used grant in place; the token check the cold check of 2026-09-28
    added reads its ``loaded`` flag and refused the replay anyway, so that
    control stopped failing. It plants the wider defect now.)"""
    original = named_profile.consume_read_grant

    def lax(token, segment):
        grant = original(token, segment)
        named_profile._READ_GRANTS[grant.token] = named_profile.ReadGrant(
            target=grant.target, token=grant.token, minted_at=grant.minted_at
        )
        return grant

    monkeypatch.setattr(named_profile, "consume_read_grant", lax)
    with pytest.raises(AssertionError):
        await test_a_token_reads_once_and_a_replay_loads_nothing(monkeypatch, browser_page)


async def test_control_a_read_of_the_groups_is_caught(monkeypatch, browser_page):
    """A read that returned the page's group titles would put them in the
    result, and the groups test's clean check refuses them."""
    original = named_profile.read_the_confirmed_profile

    async def reads_groups(page, *, segment, landed):
        out = await original(page, segment=segment, landed=landed)
        out["groups"] = [await link.inner_text() for link in await page.locator(
            named_profile.GROUP_LINK_SELECTOR).all()]
        return out

    monkeypatch.setattr(named_profile, "read_the_confirmed_profile", reads_groups)
    with pytest.raises(AssertionError):
        await test_the_groups_stay_absent_whatever_the_page_draws(monkeypatch, browser_page)


def test_control_a_script_naming_the_read_is_caught(tmp_path):
    """A probe that reached the read by attribute, and one that imported its
    loader, are both found by the scan the real test runs."""
    planted = tmp_path / "scripts"
    planted.mkdir()
    (planted / "_probe_planted.py").write_text(
        "from linkedin_server import server\n"
        "server.linkedin_read_named_profile('x')\n",
        encoding="utf-8",
    )
    (planted / "_probe_imported.py").write_text(
        "from linkedin_server.named_profile import load_the_confirmed_profile\n",
        encoding="utf-8",
    )
    assert _scripts_naming_the_read(tmp_path) == [
        ("_probe_imported.py", "load_the_confirmed_profile"),
        ("_probe_planted.py", "linkedin_read_named_profile"),
    ]


async def test_control_a_landing_the_read_did_not_compose_is_caught(monkeypatch, browser_page):
    """With the landing veto removed, a member id redirected to a vanity would
    be read as the member -- and the redirect test's assertions catch it."""
    monkeypatch.setattr(named_profile, "landed_on_profile", lambda landed, segment: True)
    with pytest.raises(AssertionError):
        await test_a_member_id_redirected_elsewhere_reads_nothing(monkeypatch, browser_page)


# ---------------------------------------------------------------------------
# 8. What the cold check of 2026-09-28 found, each shown red on cee979c first
# ---------------------------------------------------------------------------

#: A profile segment of the right shape carrying a word the navigation
#: boundary refuses in ANY address. Built from declared synthetic tokens.
DOOR_REFUSED = ("someone-settings-example", "someone-invitation-example",
                "someone-verification-example")


@pytest.mark.parametrize("segment", DOOR_REFUSED)
async def test_a_profile_the_door_refuses_gets_no_token_and_is_not_quoted(monkeypatch, segment):
    """The preview asked nothing of the door: it minted a token for an address
    the confirmed call could never load, and that call's error QUOTED the
    address. The preview now asks the door first, and says why without it."""
    result = await _preview(monkeypatch, "https://www.linkedin.com/in/" + segment + "/")
    assert result.get("error"), result
    assert "confirm_token" not in result and named_profile._READ_GRANTS == {}
    assert segment not in json.dumps(result), "the refusal quoted the address"


@pytest.mark.parametrize(
    "landed, named, same",
    [
        ("https://www.linkedin.com/in/Casey-Example-3f9a/", "casey-example-3f9a", True),
        ("https://www.linkedin.com/in/stra%C3%9Fe-example/", "stra%c3%9fe-example", True),
        # casefold() said each of these was the profile named, and none is:
        ("https://www.linkedin.com/in/strasse-example/", "stra%C3%9Fe-example", False),
        ("https://www.linkedin.com/in/%E2%84%AAase-example/", "kase-example", False),
        ("https://www.linkedin.com/in/%EF%AC%81ne-example/", "fine-example", False),
        ("https://www.linkedin.com/in/%C5%BFome-example/", "some-example", False),
        # a member id is case-sensitive
        (MEMBER_LINK, MEMBER_ID, True),
        ("https://www.linkedin.com/in/" + MEMBER_ID.lower() + "/", MEMBER_ID, False),
    ],
)
def test_the_landing_is_the_named_profile_by_ascii_case_only(landed, named, same):
    assert named_profile.landed_on_profile(landed, named) is same


async def test_an_empty_landing_vetoes_the_read(browser_page):
    """An empty landing used to default to the composed address and pass the
    veto: nothing the browser said was taken as having landed on the profile."""

    class _Blank(_Navigator):
        async def goto(self, page, url, *, named_profile: bool = False) -> str:
            await super().goto(page, url, named_profile=named_profile)
            return ""

    grant = named_profile.mint_read_grant(SEGMENT)
    landed = await named_profile.load_the_confirmed_profile(
        _Blank(), browser_page, token=grant.token, segment=SEGMENT
    )
    assert landed == ""
    result = await named_profile.read_the_confirmed_profile(browser_page, segment=SEGMENT, landed=landed)
    assert result["landed_on_the_named_profile"] is False and result["person"] is None
