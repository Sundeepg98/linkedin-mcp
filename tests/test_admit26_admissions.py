"""Lane admit26 admissions: pages of his own account the read boundary refused.

Record: ``_audit/2026-11-25-admit26.md``. Every admission below rests on a
registered ruling, named on its entry, and on a spelling LinkedIn DRAWS -- the
record names the capture or the committed table that measured each one:

* PROFILE-EDITOR-ADDRESSES-ALLOWED (the operator, 2026-08-31: "/in/<member>/edit/
  and the profile editors are allowed. His own profile, no third party") with
  READ-PAST-AN-ACT-SUBSTRING ("/edit/" is a fence against EDITING; loading an
  editor edits nothing);
* READ-PAST-AN-ACT-SUBSTRING's second clause, for a page refused by allowlist
  silence alone "when a row needs it and no ruling holds it";
* ONE-NAMED-SETTINGS-PAGE-AT-A-TIME as NAMED-SETTINGS-PAGES-RATIFIED reads it,
  for a settings page: one page, by its exact address, in its own commit.

THE CONDITIONS, EACH A TEST BELOW, FOR EVERY ADMISSION IN ONE TABLE -- the same
four lane A's harness (``tests/test_lane_a_admissions.py``) holds its own to:

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
(``someone-else``, invented digits).
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
    # HIS OWN PROFILE EDITORS, past "/edit/" (PROFILE-EDITOR-ADDRESSES-ALLOWED
    # with READ-PAST-AN-ACT-SUBSTRING). Each is the spelling LinkedIn draws on
    # his own profile, in the /in/me/ form.
    Admission(
        key="editor-position",
        rows=("P D5", "P D6", "P D8", "P D9"),
        address=(f"{B}/in/me/edit/forms/position/new/"
                 "?profileFormEntryPoint=identityModuleMirror"),
        excused=frozenset({"/edit/"}),
        twin=False,
        siblings=(
            Sibling(f"{B}/in/me/edit/forms/position/new/", "/edit/",
                    "the bare form: never drawn, so never admitted"),
            Sibling(f"{B}/in/me/edit/forms/position/new/"
                    "?profileFormEntryPoint=other", "/edit/",
                    "an entry point nothing draws"),
            Sibling(f"{B}/in/me/edit/forms/position/new/"
                    "?profileFormEntryPoint=identityModuleMirror&x=1", "/edit/",
                    "a second key"),
            Sibling(f"{B}/in/me/edit/forms/position/1234567890/", "/edit/",
                    "an existing position's editor, by id"),
            Sibling(f"{B}/in/someone-else/edit/forms/position/new/"
                    "?profileFormEntryPoint=identityModuleMirror", "/edit/",
                    "ANOTHER MEMBER'S editor: the me form is the permission"),
            Sibling(f"{B}/in/me/edit/forms/education/new/", "/edit/",
                    "a section form no capture has drawn"),
        ),
    ),
    Admission(
        key="editor-summary",
        rows=("P D2",),
        address=f"{B}/in/me/edit/forms/summary/new/",
        excused=frozenset({"/edit/"}),
        siblings=(
            Sibling(f"{B}/in/me/edit/forms/summary/new/?x=1", "/edit/",
                    "a QUERY"),
            Sibling(f"{B}/in/me/edit/forms/summary/", "/edit/",
                    "the form's parent"),
            Sibling(f"{B}/in/someone-else/edit/forms/summary/new/", "/edit/",
                    "another member's About editor"),
            Sibling(f"{B}/in/me/edit/forms/summary/new/x/../../", "/edit/",
                    "a TRAVERSAL"),
            Sibling(f"{B}/in/me/edit/topcard/", "/edit/",
                    "an editor nothing here names"),
        ),
    ),
    Admission(
        key="editor-contact-info",
        rows=("P A26", "P A27", "P A28", "P A29"),
        address=f"{B}/in/me/edit/forms/contact-info/new/",
        excused=frozenset({"/edit/"}),
        siblings=(
            Sibling(f"{B}/in/me/edit/contact-info/", "/edit/",
                    "the spelling the ledger INFERRED: LinkedIn draws the "
                    "forms/ one"),
            Sibling(f"{B}/in/me/edit/forms/contact-info/new/?x=1", "/edit/",
                    "a QUERY"),
            Sibling(f"{B}/in/someone-else/edit/forms/contact-info/new/",
                    "/edit/", "another member's contact editor"),
            Sibling(f"{B}/in/me/edit/forms/contact-info/", "/edit/",
                    "the form's parent"),
        ),
    ),
    Admission(
        key="editor-secondary-language",
        rows=("P D27",),
        address=f"{B}/in/me/edit/secondary-language/",
        excused=frozenset({"/edit/"}),
        siblings=(
            Sibling(f"{B}/in/me/edit/secondary-language/?locale=x", "/edit/",
                    "a QUERY"),
            Sibling(f"{B}/in/me/edit/secondary-language/x/", "/edit/",
                    "a SUB-PATH"),
            Sibling(f"{B}/in/someone-else/edit/secondary-language/", "/edit/",
                    "another member's language editor"),
            Sibling(f"{B}/in/me/edit/", "/edit/", "the editor root"),
        ),
    ),
    Admission(
        key="editor-skill",
        rows=("P E2", "P E3"),
        address=f"{B}/in/me/details/skills/edit/forms/2/",
        excused=frozenset({"/edit/"}),
        siblings=(
            Sibling(f"{B}/in/me/details/skills/edit/forms/abc/", "/edit/",
                    "a word segment"),
            Sibling(f"{B}/in/me/details/skills/edit/forms/٢/", "/edit/",
                    "an Arabic-Indic digit, which a \\d class would admit"),
            Sibling(f"{B}/in/me/details/skills/edit/forms/2/?x=1", "/edit/",
                    "a QUERY"),
            Sibling(f"{B}/in/me/details/skills/edit/forms/2/x/", "/edit/",
                    "a SUB-PATH"),
            Sibling(f"{B}/in/someone-else/details/skills/edit/forms/2/",
                    "/edit/", "another member's skill editor"),
            Sibling(f"{B}/in/me/details/skills/edit/forms/", "/edit/",
                    "no segment"),
            Sibling(f"{B}/in/me/details/experience/edit/forms/2/", "/edit/",
                    "a sibling section's editor"),
        ),
        spellings=(f"{B}/in/me/details/skills/edit/forms/1234567890/",),
    ),
    # ------------------------------------------------------------------
    # ALLOWLIST SILENCE (READ-PAST-AN-ACT-SUBSTRING's second clause): no
    # substring crossed, so `excused` is empty and the exemption table must
    # hold nothing for any of these.
    Admission(
        key="open-to-services",
        rows=("P H1",),
        address=f"{B}/in/me/opportunities/services/education/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/in/me/opportunities/services/education/?x=1", None,
                    "a QUERY"),
            Sibling(f"{B}/in/me/opportunities/services/education/next/", None,
                    "a SUB-PATH: a step inside the flow"),
            Sibling(f"{B}/in/me/opportunities/services/", None,
                    "the family below it"),
            Sibling(f"{B}/in/me/opportunities/", None, "the Open-to root"),
            Sibling(f"{B}/in/someone-else/opportunities/services/education/",
                    None, "another member's page"),
            # The volunteering page's BARE spelling stood here until
            # 2026-11-26, when lane admit5-26 admitted it on
            # VOLUNTEERING-BARE-SPELLING-FIRST
            # (tests/test_admit5_26_admissions.py). The spelling LinkedIn
            # draws, his own profile id in its query, did not travel with it.
            Sibling(f"{B}/in/me/opportunities/volunteering/education/"
                    "?profileId=placeholder-id", None,
                    "the volunteering page as drawn, his own profile id in its "
                    "query, so not admitted here"),
            Sibling(f"{B}/in/me/opportunities/job-opportunities/edit/",
                    "/edit/", "the Open To Work editor's inferred address: "
                    "the editor has no address at all"),
            Sibling(f"{B}/in/me/opportunities/hiring/education/", None,
                    "the #Hiring item, a broadcast by nature"),
        ),
    ),
    Admission(
        key="my-network",
        rows=("N 22", "N 32", "N 62", "N 97", "N 98"),
        address=f"{B}/mynetwork/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/mynetwork/?x=1", None,
                    "a QUERY -- where a filter naming a person would arrive"),
            Sibling(f"{B}/mynetwork/discovery-see-all/", None,
                    "the full suggestion lists: drawn, not admitted here"),
            Sibling(f"{B}/mynetwork/discover-hub/", None,
                    "the Discover-more hub: drawn, not admitted here"),
            Sibling(f"{B}/mynetwork/import-contacts/", None,
                    "the address-book import page (CONTACT-IMPORT-STAYS-MANUAL)"),
            Sibling(f"{B}/mynetwork/network-manager/", None,
                    "the network manager's root"),
            Sibling(f"{B}/mynetwork/invite-connect/invitations/", "/invite",
                    "the invitation surface the forbidden substrings exist for"),
            Sibling(f"{B}/mynetwork/settings/manage-syncing/", "/settings/",
                    "a syncing settings page"),
            Sibling(f"{B}/mynetworkx/", None, "a longer word"),
            Sibling(f"{B}/mynetwork/x/../../in/someone-else/", None,
                    "a TRAVERSAL onto a third party"),
        ),
    ),
    # ------------------------------------------------------------------
    # NAMED SETTINGS PAGES (ONE-NAMED-SETTINGS-PAGE-AT-A-TIME as
    # NAMED-SETTINGS-PAGES-RATIFIED reads it: one page by its exact address,
    # in its own commit).
    Admission(
        key="privacy-category",
        rows=("J 87", "N 96", "N 143", "P O22", "P P3"),
        address=f"{B}/mypreferences/d/categories/privacy",
        excused=frozenset({"/mypreferences/d/categories/"}),
        siblings=(
            Sibling(f"{B}/mypreferences/d/categories/",
                    "/mypreferences/d/categories/", "the category root"),
            Sibling(f"{B}/mypreferences/d/categories/account",
                    "/mypreferences/d/categories/", "the account category"),
            Sibling(f"{B}/mypreferences/d/categories/sign-in-and-security",
                    "/mypreferences/d/categories/",
                    "the security category -- a surface the ruling excludes"),
            Sibling(f"{B}/mypreferences/d/categories/profile-visibility",
                    "/mypreferences/d/categories/", "the visibility category"),
            Sibling(f"{B}/mypreferences/d/categories/notifications",
                    "/mypreferences/d/categories/", "the notifications category"),
            Sibling(f"{B}/mypreferences/d/categories/privacy?x=1",
                    "/mypreferences/d/categories/", "a QUERY"),
            Sibling(f"{B}/mypreferences/d/categories/privacy/search-history",
                    "/mypreferences/d/categories/", "a SUB-PATH: each page the "
                    "category lists is admitted by its own name or not at all"),
            Sibling(f"{B}/mypreferences/d/categories/privacyx",
                    "/mypreferences/d/categories/", "a longer leaf"),
            Sibling(f"{B}/mypreferences/d/demographic-info-copy", None,
                    "a page the category links that records a sensitive "
                    "attribute -- the allowlist alone refuses it"),
        ),
    ),
    Admission(
        key="premium-manage-account",
        rows=("P N22",),
        address=f"{B}/mypreferences/d/premium-manage-account/",
        excused=frozenset(),
        siblings=(
            Sibling(f"{B}/mypreferences/d/premium-manage-account/?x=1", None,
                    "a QUERY"),
            Sibling(f"{B}/mypreferences/d/premium-manage-account/cancel/", None,
                    "a SUB-PATH naming a purchase act (PURCHASES-STAY-MANUAL)"),
            Sibling(f"{B}/mypreferences/d/premium-manage-accountx", None,
                    "a longer word"),
            Sibling(f"{B}/manage/purchases-payments/purchases/", None,
                    "his purchase history: drawn, not admitted here"),
            Sibling(f"{B}/premium/products/", None, "a purchase page"),
            Sibling(f"{B}/mypreferences/d/language-for-translation", None,
                    "another settings page nothing here names"),
            Sibling(f"{B}/mypreferences/d/demographic-info-copy", None,
                    "a settings page recording a sensitive attribute"),
        ),
    ),
    Admission(
        key="job-preferences",
        rows=("P I12", "P I13"),
        address=f"{B}/jobs/preferences?viewType=SEEKING_PREFERENCES",
        excused=frozenset(),
        twin=False,
        siblings=(
            Sibling(f"{B}/jobs/preferences/", None,
                    "the bare page: never drawn, so never admitted"),
            Sibling(f"{B}/jobs/preferences", None, "no query at all"),
            Sibling(f"{B}/jobs/preferences?viewType=OTHER", None,
                    "a view nothing draws"),
            Sibling(f"{B}/jobs/preferences?viewType=seeking_preferences", None,
                    "another case"),
            Sibling(f"{B}/jobs/preferences?viewType=SEEKING_PREFERENCES&x=1",
                    None, "a second key"),
            Sibling(f"{B}/jobs/preferences/?viewType=SEEKING_PREFERENCES", None,
                    "a slash LinkedIn does not draw before the query"),
            Sibling(f"{B}/jobs/preferences/edit/", "/edit/",
                    "an editor under it"),
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
