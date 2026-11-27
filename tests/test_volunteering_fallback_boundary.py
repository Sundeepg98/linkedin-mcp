"""His volunteering page by its one drawn spelling, the id from his arguments only.

THE RULING (the orchestrator, 2026-11-27 13:10, VOLUNTEERING-FALLBACK-BOUNDARY,
answering Q-VOLUNTEERING-ID-FROM-HIS-ARGUMENTS). VOLUNTEERING-BARE-SPELLING-
FIRST took the bare spelling first, "and if it does not land, profileId from
tool arguments at runtime (his own id, never stored)". The bare spelling
landed on his profile root (the live lane's session 12, load 22), so the
fallback gets its boundary line now:

* ``profileId`` comes ONLY from the caller's arguments at runtime, validated by
  shape, and is NEVER stored, logged, committed or kept in a raw; a missing or
  ill-shaped id REFUSES;
* the page NEVER supplies it: a link (or the Open-to menu's item) on his root
  may be pressed only when its target EXACTLY equals the address formed from
  the admitted pattern plus his argument -- the landed member, proven his,
  read as ``me``; any other id or parameter vetoes
  (SELF-ROOT-LINK-PRESS-BY-EXACT-MATCH, as amended at 13:10).

THE CONTROLS the ruling names, each a test below: a page-drawn id differing
from his argument vetoes; no argument refuses; an id shaped wrong refuses; the
formed address never reaches a log line, an exception or a verdict.

RED BEFORE THE BOUNDARY: the formed address was refused by allowlist silence,
and ``linkedin_server.volunteering_route`` did not exist.

Every id here is one of ``tests/test_no_committed_identity.py``'s declared
SYNTHETIC_MEMBER_TOKENS; every member segment is a placeholder.
"""
from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

import pytest

from linkedin_server import named_profile, readonly
from linkedin_server.errors import WriteAttemptError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import blast_radius  # noqa: E402

B = "https://www.linkedin.com"
BARE = f"{B}/in/me/opportunities/volunteering/education/"
#: His id, as his argument would carry it (a declared synthetic token).
HIS_ID = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000002"
#: Another id a page could draw (a declared synthetic token).
OTHER_ID = "ACoAASYNTHETICSYNTHETICSYNTHETIC0000003"
#: The landed member segment of his proven root (a placeholder).
MEMBER = "placeholder-member"
FORMED = f"{BARE}?profileId={HIS_ID}"

ALLOWLIST_SENTENCE = "not on the read-only allowlist"


def _route():
    from linkedin_server import volunteering_route

    return volunteering_route


def _refusal(url: str) -> str:
    try:
        readonly.assert_read_url(url)
    except WriteAttemptError as exc:
        return str(exc)
    return ""


def _card(member: str = MEMBER, query: str = f"profileId={HIS_ID}", fragment: str = "") -> str:
    """His root's card link to the page, as LinkedIn draws it: his member path,
    the page's own id in the query."""
    out = f"{B}/in/{member}/opportunities/volunteering/education/"
    if query:
        out += "?" + query
    if fragment:
        out += "#" + fragment
    return out


# ---------------------------------------------------------------------------
# 1. The boundary line
# ---------------------------------------------------------------------------


def test_the_formed_address_is_admitted_and_only_its_shape():
    """RED BEFORE THE BOUNDARY: refused by allowlist silence. Now the drawn
    spelling is admitted with an id of the member-id shape, and with nothing
    else: one anchored line, no other parameter, no fragment, his own
    ``/in/me/`` spelling only."""
    assert readonly.is_read_url(FORMED), _refusal(FORMED)
    for sibling, why in (
        (f"{BARE}?profileId=placeholder-id", "an id not shaped like a member id"),
        (f"{BARE}?profileId=", "an empty id"),
        (f"{BARE}?profileid={HIS_ID}", "the parameter's name in another case"),
        (f"{BARE}?profileId={HIS_ID}&x=1", "an extra parameter"),
        (f"{BARE}?x=1&profileId={HIS_ID}", "an extra parameter first"),
        (f"{BARE}?profileId={HIS_ID}&profileId={OTHER_ID}", "the id twice"),
        (f"{BARE}?profileId={HIS_ID}'", "a quote after the id"),
        (f"{BARE}?profileId={HIS_ID}%27", "an encoded quote after the id"),
        (f"{B}/in/{MEMBER}/opportunities/volunteering/education/?profileId={HIS_ID}",
         "a member path, not his /in/me/ spelling"),
        (f"{B}/in/me/opportunities/volunteering/education/next/?profileId={HIS_ID}",
         "a step inside the flow"),
        (f"{B}/in/me/opportunities/services/education/?profileId={HIS_ID}",
         "the services page with an id"),
        (f"http://www.linkedin.com/in/me/opportunities/volunteering/education/?profileId={HIS_ID}",
         "another scheme"),
    ):
        assert not readonly.is_read_url(sibling), why
        assert ALLOWLIST_SENTENCE in _refusal(sibling), (why, _refusal(sibling))


def test_the_line_is_one_and_its_id_is_the_member_id_shape():
    """ONE LINE, and its id class is the package's member-id shape, so the two
    cannot drift: removing the line refuses the formed address again (the
    proven rollback), and the id class is ``named_profile.MEMBER_ID``'s."""
    lines = [p for p in readonly._ALLOWED_URL_PATTERNS if p.match(FORMED)]
    assert len(lines) == 1, [p.pattern for p in lines]
    member_class = named_profile.MEMBER_ID.pattern.strip("^$")
    assert member_class in lines[0].pattern, (member_class, lines[0].pattern)


def test_without_the_line_the_formed_address_is_refused(monkeypatch):
    kept = tuple(p for p in readonly._ALLOWED_URL_PATTERNS if not p.match(FORMED))
    assert len(kept) == len(readonly._ALLOWED_URL_PATTERNS) - 1
    monkeypatch.setattr(readonly, "_ALLOWED_URL_PATTERNS", kept)
    assert not readonly.is_read_url(FORMED)
    assert ALLOWLIST_SENTENCE in _refusal(FORMED)


def test_the_line_newly_admits_exactly_the_id_shaped_spelling():
    """THE BLAST RADIUS, on concrete urls before and after: over the shipped
    corpus plus every address in this file, the line admits nothing but the
    formed spellings."""
    line = next(p for p in readonly._ALLOWED_URL_PATTERNS if p.match(FORMED))
    corpus = sorted(set(blast_radius.corpus()) | {
        FORMED,
        f"{BARE}?profileId={OTHER_ID}",
        f"{BARE}?profileId=placeholder-id",
        f"{BARE}?profileId={HIS_ID}&x=1",
        BARE,
        _card(),
    })
    without = tuple(p for p in readonly._ALLOWED_URL_PATTERNS if p is not line)
    newly = [u for u in corpus
             if any(p.match(u) for p in readonly._ALLOWED_URL_PATTERNS)
             and not any(p.match(u) for p in without)]
    assert sorted(newly) == sorted([FORMED, f"{BARE}?profileId={OTHER_ID}"]), newly
    assert readonly.is_read_url(BARE), "the bare line is untouched"


# ---------------------------------------------------------------------------
# 2. The address, formed from his argument and from nothing else
# ---------------------------------------------------------------------------


def test_the_address_is_formed_from_his_argument():
    route = _route()
    assert route.volunteering_address(HIS_ID) == FORMED
    assert readonly.is_read_url(route.volunteering_address(HIS_ID))


@pytest.mark.parametrize(
    "given",
    [None, "", "   ", "placeholder-id", HIS_ID + "'", HIS_ID[:-30], " " + HIS_ID,
     HIS_ID + "\n", 12345, ["x"], b"ACoAASYNTHETICSYNTHETICSYNTHETIC0000002"],
    ids=["none", "empty", "blank", "not-an-id", "a-quote", "too-short", "a-space",
         "a-newline", "an-int", "a-list", "bytes"],
)
def test_a_missing_or_ill_shaped_id_refuses_and_never_quotes_it(given):
    route = _route()
    with pytest.raises(route.ProfileIdRefused) as raised:
        route.volunteering_address(given)
    message = str(raised.value)
    assert "SYNTHETIC" not in message and "placeholder" not in message, message
    assert "ACoAA" not in message


# ---------------------------------------------------------------------------
# 3. The press match: the page may veto, never supply
# ---------------------------------------------------------------------------


def test_his_card_link_matches_only_on_his_own_id():
    """THE MATCH (SELF-ROOT-LINK-PRESS-BY-EXACT-MATCH, as amended): the card
    link, his landed member read as ``me``, is EXACTLY the address formed from
    his argument. A page-drawn id differing from his argument VETOES."""
    route = _route()
    assert route.match_verdict(_card(), HIS_ID, MEMBER) == "match"
    assert route.link_matches(_card(), HIS_ID, MEMBER) is True
    assert route.match_verdict(_card(query=f"profileId={OTHER_ID}"), HIS_ID, MEMBER) == "id_differs"
    assert route.link_matches(_card(query=f"profileId={OTHER_ID}"), HIS_ID, MEMBER) is False


@pytest.mark.parametrize(
    "href,word",
    [
        (_card(member="someone-else"), "not_his_member"),
        (_card(query=""), "query"),
        (_card(query=f"profileId={HIS_ID}&x=1"), "query"),
        (_card(query=f"x=1&profileId={HIS_ID}"), "query"),
        (_card(query=f"profileId={HIS_ID}&profileId={HIS_ID}"), "query"),
        (_card(query=f"profileid={HIS_ID}"), "query"),
        (_card(fragment="top"), "fragment"),
        (_card().replace("https://", "http://"), "address"),
        (_card().replace("www.linkedin.com", "linkedin.com"), "address"),
        (_card().replace("/education/", "/education/next/"), "path"),
        (_card().replace("volunteering", "services"), "path"),
        (f"/in/{MEMBER}/opportunities/volunteering/education/?profileId={HIS_ID}", "address"),
        ("", "address"),
        (None, "address"),
    ],
    ids=["another-member", "no-query", "extra-after", "extra-before", "id-twice",
         "name-case", "fragment", "http", "host", "sub-path", "services", "relative",
         "empty", "none"],
)
def test_every_other_target_vetoes(href, word):
    route = _route()
    assert route.match_verdict(href, HIS_ID, MEMBER) == word
    assert route.link_matches(href, HIS_ID, MEMBER) is False


def test_no_argument_or_an_ill_shaped_one_refuses_the_match():
    """NO ARGUMENT REFUSES, AND SO DOES A WRONG SHAPE -- even against a link
    whose own id is well formed: the page never stands in for his argument."""
    route = _route()
    for given in (None, "", "placeholder-id", HIS_ID + "'"):
        assert route.match_verdict(_card(), given, MEMBER) == "refused"
        assert route.link_matches(_card(), given, MEMBER) is False


def test_a_member_segment_is_folded_in_ascii_only():
    """A page cannot draw a look-alike of his segment: the Kelvin sign folds to
    ``k`` under ``str.lower`` and must not here; plain ASCII case still folds,
    as vanity segments do."""
    route = _route()
    landed = "placeholder-k"
    assert route.match_verdict(_card(member="placeholder-K"), HIS_ID, landed) == "match"
    assert route.match_verdict(_card(member="placeholder-\u212a"), HIS_ID, landed) == "not_his_member"


def test_the_landed_member_must_be_a_member_segment():
    """The member the href is read against is the landing's, proven his; a
    landing that is not a member segment (the self alias, nothing, a shape
    outside the closed alphabet) matches nothing."""
    route = _route()
    for landed in ("me", "", None, "x'y", "a/b"):
        assert route.match_verdict(_card(member=str(landed or "x")), HIS_ID, landed) == "not_his_member"


# ---------------------------------------------------------------------------
# 4. The formed address never reaches a log line, an exception or a verdict
# ---------------------------------------------------------------------------


def test_the_id_and_the_formed_address_reach_no_log_and_no_verdict(caplog):
    route = _route()
    caplog.set_level(logging.DEBUG)
    outputs = [
        route.match_verdict(_card(), HIS_ID, MEMBER),
        route.match_verdict(_card(query=f"profileId={OTHER_ID}"), HIS_ID, MEMBER),
        route.match_verdict(_card(fragment="top"), HIS_ID, MEMBER),
        route.link_matches(_card(), HIS_ID, MEMBER),
        route.match_verdict(_card(), "placeholder-id", MEMBER),
    ]
    for bad in (None, "placeholder-id"):
        with pytest.raises(route.ProfileIdRefused):
            route.volunteering_address(bad)
    route.volunteering_address(HIS_ID)
    for value in outputs:
        assert value in route.MATCH_WORDS or isinstance(value, bool), value
    logged = " ".join(record.getMessage() for record in caplog.records)
    for needle in ("SYNTHETIC", "ACoAA", "profileId=", MEMBER, "volunteering"):
        assert needle not in logged, (needle, logged)


def test_the_route_module_writes_and_logs_nothing():
    """STRUCTURAL: the module holds no logger call, no print, no file write
    and no store -- so the formed address has nowhere to go but back to its
    caller."""
    source = Path(_route().__file__).read_text(encoding="utf-8")
    code = "\n".join(line for line in source.splitlines() if not line.lstrip().startswith("#"))
    for banned in ("logger.", "logging.", "print(", "open(", ".write(", "write_text",
                   "json.dump", "BROWSER", "goto("):
        assert banned not in code, banned
