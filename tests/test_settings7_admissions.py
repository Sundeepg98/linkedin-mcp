"""Lane settings7 admissions: two named settings pages his Data privacy category draws, red-first.

Record: ``_audit/2026-11-27-settings7.md``, section 5. Each page is admitted BY
NAME, in its own commit, under ONE-NAMED-SETTINGS-PAGE-AT-A-TIME as
NAMED-SETTINGS-PAGES-RATIFIED reads it ("one named settings page per commit is
within the ruling"), with HIS-OWN-SETTINGS-NOT-OUTWARD; neither trips a
forbidden substring, so each is READ-PAST-AN-ACT-SUBSTRING's second clause (a
page the allowlist refuses by its silence is admitted the same way). The
orchestrator confirmed both admissions on 2026-11-27 (12:55).

THE SPELLINGS ARE MEASURED, NOT GUESSED. Session 12's capture of his Data
privacy category page (load 10; ``tests/fixtures/live12/privacy_words.html``)
draws each as a setting link whose path words matched by keyed shape:

* ``/mypreferences/m/search-history/``, labelled ``Clear search history``
  (census ``N 96``, "Clear your search history"), under the page's ``How
  LinkedIn uses your data`` heading;
* ``/mypreferences/m/download-my-data/``, labelled ``Download your data``
  (census ``P P3``, "Get a copy of his data"), under the same heading.

And a third, on the orchestrator's order CONTACTS-PAGE-FROM-THE-SETTINGS-NAV
(2026-11-27 13:25): his contact-syncing page, drawn on session 11's capture of
his Account preferences category page (load 8;
``tests/fixtures/live11/sessions_surface_words.html``) as ``Sync contacts``
under ``Syncing options``, a link to ``/mynetwork/settings/manage-syncing``
(census ``N 32`` and ``N 110``, whose next steps lane net7 re-aims). It trips
``/settings/`` and ``settings``, the 2026-09-03 second gate over the
toggle-bearing settings family -- an act's ground -- so its line is paired
with ONE exemption excusing exactly those two for that anchored address alone
(READ-PAST-AN-ACT-SUBSTRING, the "Sharing profile edits" precedent).

READ-ONLY, ZERO PRESSES: clearing his search history and requesting his
archive are each a write with its own row and spec; the press gate refuses
every control on either page.

THE CONDITIONS, EACH A TEST BELOW, are lane admit26's harness as lane
admit5-26 applied it (``tests/test_admit5_26_admissions.py``), unchanged:

1. ONE exact, anchored pattern per address, carrying no wildcard.
2. A control is shown failing: every sibling spelling is still refused, on the
   gate its entry names, and the refusal's own sentence is checked.
3. Where a forbidden substring is crossed, the exemption excuses EXACTLY the
   substrings the address trips, for exactly that anchored address, and the
   forbidden tuple is unchanged; otherwise no exemption exists. EITHER GATE
   ALONE ADMITS NOTHING.
4. The blast radius, measured on concrete urls before and after (never a
   grep): each admission newly admits exactly its own spellings and refuses
   nothing new.

Nothing here opens a page.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import NamedTuple, Optional

import pytest

from linkedin_server import press, readonly, writes
from linkedin_server.errors import WriteAttemptError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import blast_radius  # noqa: E402

B = "https://www.linkedin.com"

ALLOWLIST_SENTENCE = "not on the read-only allowlist"
PATTERN_WOULD_ADMIT = "A READ PATTERN DOES ADMIT THIS ADDRESS"

#: The forbidden tuple's size when this lane began. An admission here never
#: shortens it.
FORBIDDEN_TUPLE_SIZE = 33

#: Where the spellings were measured.
PRIVACY_WORDS = ROOT / "tests" / "fixtures" / "live12" / "privacy_words.html"
ACCOUNT_WORDS = ROOT / "tests" / "fixtures" / "live11" / "sessions_surface_words.html"


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
    label: str
    siblings: tuple
    #: The forbidden substrings the address trips and its paired exemption
    #: excuses; empty for an allowlist-silence admission.
    excused: frozenset = frozenset()
    #: The words fixture the spelling was measured on.
    measured_on: Path = PRIVACY_WORDS


def _slash_twin(url: str) -> str:
    return url[:-1] if url.endswith("/") else url + "/"


def _own(adm) -> set:
    return {adm.address, _slash_twin(adm.address)}


ADMISSIONS = (
    Admission(
        key="search-history",
        rows=("N 96",),
        address=f"{B}/mypreferences/m/search-history/",
        label="Clear search history",
        siblings=(
            Sibling(f"{B}/mypreferences/d/search-history", None,
                    "the desktop-tree spelling, which nothing draws"),
            Sibling(f"{B}/mypreferences/m/search-history/clear/", None, "a sub-path"),
            Sibling(f"{B}/mypreferences/m/search-history/?trk=x", None, "a query"),
            Sibling(f"{B}/mypreferences/m/Search-History/", None, "another case"),
            Sibling(f"{B}/mypreferences/m/search-histories/", None, "a longer leaf"),
            Sibling(f"{B}/mypreferences/m/settings/search-history/", "/settings/",
                    "the settings-tree spelling"),
            Sibling(f"{B}/jobs/search-history/", None,
                    "the jobs search history, J 18's priced address, still refused"),
            Sibling(f"{B}/psettings/search-history", "/psettings/", "the legacy namespace"),
            Sibling(f"{B}/mypreferences/m/manage-data-and-activity/", None,
                    "its neighbour on the same heading, not admitted here"),
        ),
    ),
    Admission(
        key="download-my-data",
        rows=("P P3",),
        address=f"{B}/mypreferences/m/download-my-data/",
        label="Download your data",
        siblings=(
            Sibling(f"{B}/mypreferences/d/download-my-data", None,
                    "the desktop-tree spelling, which nothing draws"),
            Sibling(f"{B}/mypreferences/m/download-my-data/request/", None, "a sub-path"),
            Sibling(f"{B}/mypreferences/m/download-my-data/?tier=fast", None, "a query"),
            Sibling(f"{B}/mypreferences/m/Download-My-Data/", None, "another case"),
            Sibling(f"{B}/mypreferences/m/download-my-data-now/", None, "a longer leaf"),
            Sibling(f"{B}/mypreferences/m/demographic-info/", None,
                    "its neighbour on the same heading, sensitive self-identification, refused"),
            Sibling(f"{B}/psettings/member-data", "/psettings/", "the legacy namespace"),
        ),
    ),
    Admission(
        key="manage-syncing",
        rows=("N 32", "N 110"),
        address=f"{B}/mynetwork/settings/manage-syncing",
        label="Sync contacts",
        excused=frozenset({"/settings/", "settings"}),
        measured_on=ACCOUNT_WORDS,
        siblings=(
            Sibling(f"{B}/mynetwork/settings/", "/settings/", "the settings root under /mynetwork/"),
            Sibling(f"{B}/mynetwork/settings/manage-syncing/contacts/", "/settings/", "a sub-path"),
            Sibling(f"{B}/mynetwork/settings/manage-syncing?trk=x", "/settings/", "a query"),
            Sibling(f"{B}/mynetwork/settings/Manage-Syncing", "/settings/", "another case"),
            Sibling(f"{B}/mynetwork/settings/manage-syncing-all", "/settings/", "a longer leaf"),
            Sibling(f"{B}/mynetwork/settings/manage-calendar", "/settings/",
                    "a sibling settings page, never drawn"),
            Sibling(f"{B}/mypreferences/d/settings/manage-syncing", "/settings/",
                    "the settings tree under /mypreferences/"),
            Sibling(f"{B}/mynetwork/import-contacts/", None,
                    "the address-book import page (CONTACT-IMPORT-STAYS-MANUAL)"),
            Sibling(f"{B}/mynetwork/import-contacts/saved-contacts/", None,
                    "the imported-contacts manager, which no capture has drawn"),
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
def test_the_spelling_is_the_one_the_privacy_capture_draws_with_its_label(adm):
    """MEASURED: the address and its label are the words the capture drew."""
    text = adm.measured_on.read_text(encoding="ascii")
    assert text.count('href="%s"' % adm.address) == 1, adm.key
    link = text.split('href="%s"' % adm.address, 1)[1].split("</a>", 1)[0]
    assert "\n%s\n" % adm.label in link, adm.key


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
def test_every_sibling_is_still_refused_on_the_gate_that_names_it(adm):
    for sib in adm.siblings:
        assert not readonly.is_read_url(sib.url), (adm.key, sib.why)
        message = _refusal(sib.url)
        if sib.gate is None:
            assert ALLOWLIST_SENTENCE in message, (adm.key, sib.why, message)
        else:
            assert "contains %r" % sib.gate in message, (adm.key, sib.why, message)
        assert readonly._pattern_exempted_substrings(sib.url) == frozenset(), (
            adm.key, sib.why)


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_without_the_line_the_address_is_refused(adm, monkeypatch):
    """The proven rollback: the line alone admits it."""
    kept = tuple(
        p for p in readonly._ALLOWED_URL_PATTERNS if not p.match(adm.address)
    )
    assert len(kept) == len(readonly._ALLOWED_URL_PATTERNS) - 1
    monkeypatch.setattr(readonly, "_ALLOWED_URL_PATTERNS", kept)
    assert not readonly.is_read_url(adm.address)
    assert ALLOWLIST_SENTENCE in _refusal(adm.address), adm.key


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_each_admission_newly_admits_exactly_its_own_spellings(adm):
    """THE BLAST RADIUS of each line, over the shipped corpus plus every
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


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_the_press_gate_refuses_every_control_on_the_page(adm):
    """READ-PAST-AN-ACT-SUBSTRING'S THIRD CONDITION, "the press gate still
    refusing every control", MEASURED OFFLINE the way lane msg7 measured
    ``/feed/hashtag/`` (the orchestrator's addendum to
    CONTACTS-PAGE-FROM-THE-SETTINGS-NAV, 2026-11-27). No entry of
    ``press.SENSITIVITY_BASES`` reaches the page, so ``sensitivity_basis`` is
    None and ``_basis_refusal`` refuses every press there before the click;
    and no sanctioned write spec's pattern or template names it."""
    for url in sorted(_own(adm)):
        assert press.sensitivity_basis(url) is None, (adm.key, url)
        # The gate's own refusal path, for every shape it sanctions: refused
        # before any page contact, never priced (the order of 14:12).
        for shape in press.SANCTIONED_SHAPES:
            verdict = press.check_basis(url, shape)
            assert verdict.get("refused") == "no_sensitivity_basis", (adm.key, url, shape, verdict)
        path = url.split("linkedin.com", 1)[1].rstrip("/")
        for name, spec in writes.SANCTIONED_WRITES.items():
            pattern = getattr(spec, "url_pattern", None)
            assert not (pattern is not None and pattern.match(url)), (adm.key, name, url)
            assert path not in (getattr(spec, "url_template", None) or ""), (adm.key, name, url)


def test_the_press_gate_check_can_fail(monkeypatch):
    """THE CHECK CAN FAIL: the feed is a priced surface, and a basis planted
    for a prefix the contact-syncing page carries reaches it by containment --
    the inheritance that held the hashtag page back."""
    assert press.sensitivity_basis(f"{B}/feed/") is not None
    planted = (("/mynetwork/", {"kind": "sensitive", "counters": ("off_state",),
                                "why": "planted by this test"}),) + tuple(press.SENSITIVITY_BASES)
    monkeypatch.setattr(press, "SENSITIVITY_BASES", planted)
    assert press.sensitivity_basis(f"{B}/mynetwork/settings/manage-syncing") is not None


def test_the_forbidden_tuple_is_unchanged_and_every_crossed_substring_is_in_it():
    assert len(readonly._FORBIDDEN_URL_SUBSTRINGS) == FORBIDDEN_TUPLE_SIZE
    for adm in ADMISSIONS:
        for bad in adm.excused:
            assert bad in readonly._FORBIDDEN_URL_SUBSTRINGS, (adm.key, bad)


def test_the_table_holds_no_duplicate_address():
    addresses = [a.address for a in ADMISSIONS]
    assert len(addresses) == len(set(addresses)), addresses
