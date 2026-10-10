"""Lane A admissions: read pages of his own account past a substring written to
stop an ACT, and pages refused by allowlist silence alone.

Ruling READ-PAST-AN-ACT-SUBSTRING (orchestrator, 2026-09-28), registered in
``_audit/2026-09-28-rulings-build-classes.md`` section 5. Record:
``_audit/2026-09-28-lane-a-admissions.md``.

THE RULING'S CONDITIONS, EACH A TEST BELOW, FOR EVERY ADMISSION IN ONE TABLE:

1. ONE exact, anchored pattern per address -- exactly one allowlist line
   matches the address, and it carries no wildcard.
2. A control is shown failing: the substring (or the allowlist) still refuses
   every other spelling and every sibling path. Each sibling names the gate
   that must refuse it, and the refusal's own sentence is checked.
3. Where a forbidden substring is crossed, the exemption excuses EXACTLY the
   substrings the address trips, for exactly that anchored address; the
   forbidden tuple is unchanged. EITHER GATE ALONE ADMITS NOTHING: drop the
   exemption and the substring refuses (saying a pattern would admit it); drop
   the line and the allowlist refuses.
4. The blast radius, measured the way ``scripts/blast_radius.py`` measures --
   ``is_read_url`` before and after on concrete urls, never a grep: each
   admission newly admits exactly its own spellings and refuses nothing new.

Nothing here opens a page. Every variable segment is a placeholder
(``placeholder-org``, ``someone-else``, invented digits).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import NamedTuple, Optional

import pytest

from linkedin_server import readonly
from linkedin_server.errors import WriteAttemptError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import blast_radius  # noqa: E402

B = "https://www.linkedin.com"

#: The allowlist's own refusal sentence and the forbidden branch's, as the
#: shipped gate writes them (tests/test_refusal_names_both_gates.py pins both).
ALLOWLIST_SENTENCE = "not on the read-only allowlist"
PATTERN_WOULD_ADMIT = "A READ PATTERN DOES ADMIT THIS ADDRESS"

#: The forbidden tuple's size when lane A landed. An admission here never
#: shortens it; the floor in tests/test_readonly_boundary_invariant.py is the
#: standing guard, this is the lane's own statement.
FORBIDDEN_TUPLE_SIZE = 33


class Sibling(NamedTuple):
    url: str
    #: The forbidden substring that must refuse it, or None when the
    #: allowlist alone must refuse it.
    gate: Optional[str]
    why: str


class Admission(NamedTuple):
    key: str
    rows: tuple
    address: str
    #: The forbidden substrings the address trips and the exemption excuses;
    #: empty for an allowlist-silence admission.
    excused: frozenset
    siblings: tuple
    #: Spellings the pair must newly admit besides ``address`` (normally the
    #: other slash form).
    spellings: tuple = ()


def _slash_twin(url: str) -> str:
    return url[:-1] if url.endswith("/") else url + "/"


ADMISSIONS = (
    Admission(
        key="invitations-received",
        rows=("N 13", "N 14", "N 19"),
        address=f"{B}/mynetwork/invitation-manager/",
        excused=frozenset({"invitation"}),
        siblings=(
            Sibling(f"{B}/mynetwork/invitation-manager/?filterCriteria=x",
                    "invitation", "a QUERY -- the anchor is load-bearing"),
            Sibling(f"{B}/mynetwork/invitation-manager/received/",
                    "invitation", "an unrecorded leaf: its own line if served"),
            Sibling(f"{B}/mynetwork/invitation-manager/accept/",
                    "invitation", "a SUB-PATH naming an act"),
            Sibling(f"{B}/mynetwork/invitation-manager/../../in/someone-else/",
                    "invitation", "a TRAVERSAL onto a third party"),
            Sibling(f"{B}/mynetwork/invite-connect/invitations/",
                    "/invite", "the other invitation surface"),
            Sibling(f"{B}/groups/12345678/invite/", "/invite",
                    "inviting somebody to a group"),
            Sibling(f"{B}/mynetwork/", None,
                    "the hub, refused on its badge cost (R1) and by nothing "
                    "else -- the allowlist alone"),
        ),
    ),
    Admission(
        key="invitations-sent",
        rows=("N 9", "N 11"),
        address=f"{B}/mynetwork/invitation-manager/sent/",
        excused=frozenset({"invitation"}),
        siblings=(
            Sibling(f"{B}/mynetwork/invitation-manager/sent/?invitationType=x",
                    "invitation", "a QUERY -- the Page tab's spelling is "
                    "unrecorded"),
            Sibling(f"{B}/mynetwork/invitation-manager/sent/withdraw/",
                    "invitation", "a SUB-PATH naming the write (N 10)"),
            Sibling(f"{B}/mynetwork/invitation-manager/sent/x/../../",
                    "invitation", "a TRAVERSAL"),
        ),
    ),
    Admission(
        key="people-followed",
        rows=("N 38",),
        address=f"{B}/mynetwork/network-manager/people-follow/following/",
        excused=frozenset({"/follow"}),
        siblings=(
            Sibling(f"{B}/mynetwork/network-manager/people-follow/following/?x=1",
                    "/follow", "a QUERY"),
            Sibling(f"{B}/mynetwork/network-manager/people-follow/following/"
                    "unfollow/", "/follow", "a SUB-PATH naming the write"),
            Sibling(f"{B}/in/me/follow/", "/follow", "following a member"),
            Sibling(f"{B}/company/placeholder-org/follow/", "/follow",
                    "following a Page"),
            Sibling(f"{B}/company/placeholder-org/unfollow/", "/unfollow",
                    "unfollowing a Page"),
            Sibling(f"{B}/feed/follows/", "/follow",
                    "a read the exemption does not reach"),
            Sibling(f"{B}/company/placeholder-org/admin/following/", "/follow",
                    "his Page's following list (N A3), not admitted here"),
            Sibling(f"{B}/mynetwork/network-manager/people-follow/", None,
                    "the family root, refused by the allowlist alone"),
        ),
    ),
    Admission(
        key="job-application-settings",
        rows=("P M2", "P M4", "P M5", "P M6", "P M12", "J 71", "J 72", "J 73"),
        address=f"{B}/jobs/application-settings/",
        excused=frozenset({"/jobs/application", "settings"}),
        siblings=(
            Sibling(f"{B}/jobs/application-settings/?resume=1",
                    "/jobs/application", "a QUERY"),
            Sibling(f"{B}/jobs/application-settings/resume/delete",
                    "/jobs/application", "a SUB-PATH naming a write"),
            Sibling(f"{B}/jobs/application/1234567890/", "/jobs/application",
                    "an application itself"),
            Sibling(f"{B}/jobs/applications/", "/jobs/application",
                    "a sibling the exemption does not reach"),
            Sibling(f"{B}/jobs/easy-apply/", "easy-apply", "applying"),
            Sibling(f"{B}/mypreferences/d/job-application-accounts",
                    "job-application", "the stored applicant accounts, NOT "
                    "admitted (a credential-adjacent surface; the record, 2.6)"),
            Sibling(f"{B}/mypreferences/d/settings/language", "/settings/",
                    "a settings page the dark-mode entry declined by name"),
            Sibling(f"{B}/public-profile/settings", "settings",
                    "the second spelling the 2026-09-03 block closed"),
        ),
    ),
    Admission(
        key="unfollowed",
        rows=("N 39",),
        address=f"{B}/mypreferences/d/unfollowed",
        excused=frozenset({"/unfollow"}),
        siblings=(
            Sibling(f"{B}/mypreferences/d/unfollowed?member=1", "/unfollow",
                    "a QUERY -- where a person would arrive"),
            Sibling(f"{B}/mypreferences/d/unfollowed/refollow", "/unfollow",
                    "a SUB-PATH naming the write"),
            Sibling(f"{B}/company/placeholder-org/unfollow/", "/unfollow",
                    "unfollowing a Page"),
            Sibling(f"{B}/mypreferences/d/categories/privacy",
                    "/mypreferences/d/categories/", "a category page"),
            Sibling(f"{B}/mypreferences/d/settings/show-profile-photos",
                    "/settings/", "a sibling settings page"),
            Sibling(f"{B}/mypreferences/d/demographic-info-copy", None,
                    "a settings page recording a sensitive attribute -- the "
                    "allowlist alone refuses it, and nothing here reaches it"),
        ),
    ),
    Admission(
        key="ads-settings",
        rows=("P P15",),
        address=f"{B}/mypreferences/d/categories/ads",
        excused=frozenset({"/mypreferences/d/categories/"}),
        siblings=(
            Sibling(f"{B}/mypreferences/d/categories/",
                    "/mypreferences/d/categories/", "the category root"),
            Sibling(f"{B}/mypreferences/d/categories/account",
                    "/mypreferences/d/categories/", "the account category"),
            Sibling(f"{B}/mypreferences/d/categories/sign-in-and-security",
                    "/mypreferences/d/categories/",
                    "the security category -- a surface the ruling excludes"),
            Sibling(f"{B}/mypreferences/d/categories/privacy",
                    "/mypreferences/d/categories/", "the privacy category"),
            Sibling(f"{B}/mypreferences/d/categories/ads?x=1",
                    "/mypreferences/d/categories/", "a QUERY"),
            Sibling(f"{B}/mypreferences/d/categories/ads/off",
                    "/mypreferences/d/categories/", "a SUB-PATH"),
            Sibling(f"{B}/mypreferences/d/categories/adsx",
                    "/mypreferences/d/categories/", "a longer leaf"),
        ),
    ),
)

KEYS = [a.key for a in ADMISSIONS]


def _refusal(url: str) -> str:
    with pytest.raises(WriteAttemptError) as caught:
        readonly.assert_read_url(url)
    return str(caught.value)


def _lines_for(url: str):
    return [p for p in readonly._ALLOWED_URL_PATTERNS if p.match(url)]


def _exemptions_for(url: str):
    return [
        (p, s) for p, s in readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS
        if p.match(url)
    ]


def _trips(url: str) -> frozenset:
    lowered = url.lower()
    return frozenset(s for s in readonly._FORBIDDEN_URL_SUBSTRINGS if s in lowered)


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_the_address_is_admitted_through_the_shipped_gate(adm):
    for url in (adm.address, _slash_twin(adm.address), *adm.spellings):
        assert readonly.is_read_url(url), (adm.key, url)


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_exactly_one_anchored_line_carries_it_and_it_has_no_wildcard(adm):
    lines = _lines_for(adm.address)
    assert len(lines) == 1, (adm.key, [p.pattern for p in lines])
    source = lines[0].pattern
    assert source.startswith("^https://www\\.linkedin\\.com/"), source
    assert source.endswith("$"), source
    for token in (".*", ".+", r"\w", r"\S", "[^"):
        assert token not in source, (adm.key, token, source)
    if "/in/" in source:
        assert "/in/me/" in source, (adm.key, source)


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_the_exemption_excuses_exactly_what_the_address_trips(adm):
    # MEASURED against the shipped tuple, not copied from the table above:
    # the table's claim is checked against the gate's own substrings.
    assert _trips(adm.address) == adm.excused, (adm.key, _trips(adm.address))
    entries = _exemptions_for(adm.address)
    if not adm.excused:
        assert entries == [], (adm.key, entries)
        return
    assert len(entries) == 1, (adm.key, entries)
    assert entries[0][1] == adm.excused, (adm.key, entries[0][1])
    for bad in adm.excused:
        assert bad in readonly._FORBIDDEN_URL_SUBSTRINGS, bad


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_every_sibling_is_still_refused_on_the_gate_that_names_it(adm):
    for sib in adm.siblings:
        assert not readonly.is_read_url(sib.url), (adm.key, sib.why)
        message = _refusal(sib.url)
        if sib.gate is None:
            assert ALLOWLIST_SENTENCE in message, (adm.key, sib.why, message)
        else:
            assert "contains %r" % sib.gate in message, (adm.key, sib.why, message)
        # The exemption reaches no sibling.
        assert readonly._pattern_exempted_substrings(sib.url) == frozenset(), (
            adm.key, sib.why)


@pytest.mark.parametrize(
    "adm", [a for a in ADMISSIONS if a.excused], ids=[a.key for a in ADMISSIONS if a.excused]
)
def test_without_the_exemption_the_substring_refuses_and_says_a_pattern_would_admit(
    adm, monkeypatch
):
    """THE FIRST GATE ALONE: the allowlist line cannot admit it by itself."""
    kept = tuple(
        (p, s) for p, s in readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS
        if not p.match(adm.address)
    )
    assert len(kept) == len(readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS) - 1
    monkeypatch.setattr(readonly, "_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS", kept)
    assert not readonly.is_read_url(adm.address)
    message = _refusal(adm.address)
    assert PATTERN_WOULD_ADMIT in message, (adm.key, message)


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_without_the_line_the_address_is_refused(adm, monkeypatch):
    """THE SECOND GATE ALONE, and the proven rollback of the allowlist half."""
    kept = tuple(
        p for p in readonly._ALLOWED_URL_PATTERNS if not p.match(adm.address)
    )
    assert len(kept) == len(readonly._ALLOWED_URL_PATTERNS) - 1
    monkeypatch.setattr(readonly, "_ALLOWED_URL_PATTERNS", kept)
    assert not readonly.is_read_url(adm.address)
    assert ALLOWLIST_SENTENCE in _refusal(adm.address), adm.key


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_each_admission_newly_admits_exactly_its_own_spellings(adm):
    """THE BLAST RADIUS of each pair, over the shipped corpus plus every
    address in this file -- before and after, on concrete urls."""
    own = {adm.address, _slash_twin(adm.address), *adm.spellings}
    corpus = sorted(
        set(blast_radius.corpus())
        | own
        | {s.url for a in ADMISSIONS for s in a.siblings}
        | {a.address for a in ADMISSIONS}
    )
    allow = readonly._ALLOWED_URL_PATTERNS
    exempt = readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS
    after = {url: readonly.is_read_url(url) for url in corpus}
    try:
        readonly._ALLOWED_URL_PATTERNS = tuple(
            p for p in allow if not p.match(adm.address)
        )
        readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS = tuple(
            (p, s) for p, s in exempt if not p.match(adm.address)
        )
        before = {url: readonly.is_read_url(url) for url in corpus}
    finally:
        readonly._ALLOWED_URL_PATTERNS = allow
        readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS = exempt
    gained = sorted(u for u in corpus if after[u] and not before[u])
    lost = sorted(u for u in corpus if before[u] and not after[u])
    assert gained == sorted(own), (adm.key, gained)
    assert lost == [], (adm.key, lost)


def test_the_forbidden_tuple_is_unchanged_and_every_crossed_substring_is_in_it():
    assert len(readonly._FORBIDDEN_URL_SUBSTRINGS) == FORBIDDEN_TUPLE_SIZE
    for adm in ADMISSIONS:
        for bad in adm.excused:
            assert bad in readonly._FORBIDDEN_URL_SUBSTRINGS, (adm.key, bad)


def test_the_table_holds_no_duplicate_address():
    addresses = [a.address for a in ADMISSIONS]
    assert len(addresses) == len(set(addresses)), addresses
