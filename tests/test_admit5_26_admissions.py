"""Lane admit5-26 admissions: five ruled pages of his own account, red-first.

Record: ``_audit/2026-11-26-admit5-26.md``. Every admission below implements
a ruling the orchestrator has already made -- this lane decides none of them --
and each line is the spelling the ruling names or LinkedIn draws:

* RECOMMENDATIONS-DETAIL-PAGE-ADMITTED (2026-11-25): "ADMIT the named
  /in/me/details/recommendations/ line (interests-page precedent); the
  capture records the landing." Refused by allowlist silence alone, so
  READ-PAST-AN-ACT-SUBSTRING's second clause.
* VERIFICATIONS-PAGE-ADMITTED (2026-11-25): "ADMIT that exact address
  read-only, zero presses, a per-address exemption for "verification";
  two-step-verification stays refused."
* VOLUNTEERING-BARE-SPELLING-FIRST (2026-11-25): "the bare spelling first, the
  capture recording the landing; if it does not land, profileId from tool
  arguments at runtime (his own id, never stored)."
* NAME-BEARING-ADDRESS-REDACTION-SCOPE (2026-11-25): "Newsletter page admitted
  now on its drawn slug shape." The slug is name-bearing, so the line is a
  SHAPE and every slug in this file is synthetic.
* SELF-PROFILE-QUERY-VARIANT-ADMITTED (the orchestrator, 2026-11-26 10:10
  IST): his own profile address carrying exactly ``isSelfProfile=true`` is a
  read address in its own right; the same query on another member's profile,
  and any extra parameter or value, stays refused.

THE CONDITIONS, EACH A TEST BELOW, are lane admit26's harness
(``tests/test_admit26_admissions.py``) applied unchanged, which are lane A's:

1. ONE exact, anchored pattern per address, carrying no wildcard, and on his
   own profile only the ``/in/me/`` spelling.
2. A control is shown failing: every sibling spelling is still refused, on the
   gate its entry names, and the refusal's own sentence is checked.
3. Where a forbidden substring is crossed, the exemption excuses EXACTLY the
   substrings the address trips, for exactly that anchored address, and the
   forbidden tuple is unchanged. EITHER GATE ALONE ADMITS NOTHING.
4. The blast radius, measured on concrete urls before and after (never a
   grep): each admission newly admits exactly its own spellings and refuses
   nothing new.

Nothing here opens a page. Every variable segment is a placeholder
(``someone-else``, ``placeholder-...``, invented digits).
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

#: The forbidden tuple's size when this lane began. An admission here never
#: shortens it.
FORBIDDEN_TUPLE_SIZE = 33


class Sibling(NamedTuple):
    url: str
    #: The forbidden substring that must refuse it, or None when the
    #: allowlist alone must refuse it.
    gate: Optional[str]
    why: str


class Admission(NamedTuple):
    key: str
    ruling: str
    rows: tuple
    address: str
    #: The forbidden substrings the address trips and the exemption excuses;
    #: empty for an allowlist-silence admission.
    excused: frozenset
    siblings: tuple
    #: Spellings the pair must newly admit besides ``address`` and, when
    #: ``twin``, its other slash form.
    spellings: tuple = ()
    #: False for an address that ends in a query value: it has no slash twin.
    twin: bool = True


def _slash_twin(url: str) -> str:
    return url[:-1] if url.endswith("/") else url + "/"


def _own(adm) -> set:
    own = {adm.address, *adm.spellings}
    if adm.twin:
        own.add(_slash_twin(adm.address))
    return own


ADMISSIONS = (
    # ------------------------------------------------------------------
    # HIS RECOMMENDATIONS DETAIL PAGE, the named /in/me/ spelling, on the
    # interests-page precedent: a NAMED detail page admitted by its own line,
    # never a fourth word in the measured alternation, the capture recording
    # where it lands.
    Admission(
        key="recommendations-detail-page",
        ruling="RECOMMENDATIONS-DETAIL-PAGE-ADMITTED",
        rows=("N 121", "N 122", "N 123", "N 125", "N 126", "N 127", "N 128",
              "P F1", "P F5", "P F6", "P F7", "P F8", "P F9"),
        address=f"{B}/in/me/details/recommendations/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/in/someone-else/details/recommendations/", None,
                    "ANOTHER MEMBER'S recommendations: the me form is the "
                    "permission"),
            Sibling(f"{B}/in/me/details/recommendations/?detailScreenTabIndex=1",
                    None, "a QUERY: a tab spelling no capture has drawn"),
            Sibling(f"{B}/in/me/details/recommendations/x/", None, "a SUB-PATH"),
            Sibling(f"{B}/in/me/details/recommendation/", None,
                    "the singular, a spelling nothing names"),
            Sibling(f"{B}/in/me/details/recommendationsx/", None, "a longer word"),
            Sibling(f"{B}/in/me/details/recommendations/edit/", "/edit/",
                    "an editor under it"),
            Sibling(f"{B}/in/me/recommendations/", None,
                    "the same word outside details/"),
            Sibling(f"{B}/in/me/details/", None, "the details root"),
            Sibling(f"{B}/in/me/details/connections/", "/connect",
                    "a details section nothing has admitted, refused first on "
                    "the substring"),
            Sibling(f"{B}/in/me/details/recommendations/x/../../../../someone-else/",
                    None, "a TRAVERSAL onto a third party"),
        ),
    ),
    # ------------------------------------------------------------------
    # HIS VERIFICATIONS SETTINGS PAGE, by name, in its own commit, past
    # "verification" for this one address: the ruling names the exemption
    # and its own control, two-step verification, which stays refused.
    Admission(
        key="verifications-page",
        ruling="VERIFICATIONS-PAGE-ADMITTED",
        rows=("P K1", "P K7"),
        address=f"{B}/mypreferences/d/verifications",
        excused=frozenset({"verification"}),
        siblings=(
            Sibling(f"{B}/mypreferences/d/two-step-verification", "verification",
                    "TWO-STEP VERIFICATION STAYS REFUSED: the ruling's own "
                    "control"),
            Sibling(f"{B}/mypreferences/d/two-step-verification/", "verification",
                    "the same, slashed"),
            Sibling(f"{B}/mypreferences/d/verifications?x=1", "verification",
                    "a QUERY"),
            Sibling(f"{B}/mypreferences/d/verifications/x", "verification",
                    "a SUB-PATH: each page it lists is admitted by its own name "
                    "or not at all"),
            Sibling(f"{B}/mypreferences/d/verificationsx", "verification",
                    "a longer leaf"),
            Sibling(f"{B}/mypreferences/d/verification", "verification",
                    "the singular"),
            Sibling(f"{B}/mypreferences/d/Verifications", "verification",
                    "another case: the exemption is matched as written"),
            Sibling(f"{B}/trust/verification/", "verification",
                    "the Premium hub's verification link (P K1's cell), "
                    "another page"),
            Sibling(f"{B}/mypreferences/d/two-factor-authentication",
                    "two-factor", "the second factor, refused on its own word"),
            Sibling(f"{B}/mypreferences/d/categories/sign-in-and-security",
                    "/mypreferences/d/categories/",
                    "the security category -- a surface the ruling's class "
                    "excludes"),
            Sibling(f"{B}/mypreferences/d/verifications/../change-password",
                    "password", "a TRAVERSAL onto the password page"),
            Sibling(f"{B}/psettings/verifications", "/psettings/",
                    "the legacy settings tree"),
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
    for url in sorted(_own(adm)):
        assert readonly.is_read_url(url), (adm.key, url)


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_exactly_one_anchored_line_carries_it_and_it_has_no_wildcard(adm):
    lines = _lines_for(adm.address)
    assert len(lines) == 1, (adm.key, [p.pattern for p in lines])
    source = lines[0].pattern
    assert source.startswith("^https://www\\.linkedin\\.com/"), source
    assert source.endswith("$"), source
    for token in (".*", ".+", r"\w", r"\S", r"\d", "[^"):
        assert token not in source, (adm.key, token, source)
    if "/in/" in source:
        assert "/in/me/" in source, (adm.key, source)


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_the_exemption_excuses_exactly_what_the_address_trips(adm):
    # MEASURED against the shipped tuple, not copied from the table above.
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
    "adm", [a for a in ADMISSIONS if a.excused],
    ids=[a.key for a in ADMISSIONS if a.excused],
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
    assert PATTERN_WOULD_ADMIT in _refusal(adm.address), adm.key


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
    own = _own(adm)
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
