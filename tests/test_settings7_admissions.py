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
* (commit D adds ``/mypreferences/m/download-my-data/``, census ``P P3``.)

READ-ONLY, ZERO PRESSES: clearing his search history and requesting his
archive are each a write with its own row and spec; the press gate refuses
every control on either page.

THE CONDITIONS, EACH A TEST BELOW, are lane admit26's harness as lane
admit5-26 applied it (``tests/test_admit5_26_admissions.py``), unchanged:

1. ONE exact, anchored pattern per address, carrying no wildcard.
2. A control is shown failing: every sibling spelling is still refused, on the
   gate its entry names, and the refusal's own sentence is checked.
3. No forbidden substring is crossed, so no exemption exists for either
   address, and the forbidden tuple is unchanged.
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

from linkedin_server import readonly
from linkedin_server.errors import WriteAttemptError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import blast_radius  # noqa: E402

B = "https://www.linkedin.com"

ALLOWLIST_SENTENCE = "not on the read-only allowlist"

#: The forbidden tuple's size when this lane began. An admission here never
#: shortens it.
FORBIDDEN_TUPLE_SIZE = 33

#: Where the spellings were measured.
PRIVACY_WORDS = ROOT / "tests" / "fixtures" / "live12" / "privacy_words.html"


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
    text = PRIVACY_WORDS.read_text(encoding="ascii")
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
def test_no_substring_is_crossed_and_no_exemption_exists(adm):
    # MEASURED against the shipped tuple.
    assert _trips(adm.address) == frozenset(), (adm.key, _trips(adm.address))
    assert _exemptions_for(adm.address) == [], adm.key


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
    after = {url: readonly.is_read_url(url) for url in corpus}
    try:
        readonly._ALLOWED_URL_PATTERNS = tuple(
            p for p in allow if not p.match(adm.address)
        )
        before = {url: readonly.is_read_url(url) for url in corpus}
    finally:
        readonly._ALLOWED_URL_PATTERNS = allow
    gained = sorted(u for u in corpus if after[u] and not before[u])
    lost = sorted(u for u in corpus if before[u] and not after[u])
    assert gained == sorted(own), (adm.key, gained)
    assert lost == [], (adm.key, lost)


def test_the_forbidden_tuple_is_unchanged():
    assert len(readonly._FORBIDDEN_URL_SUBSTRINGS) == FORBIDDEN_TUPLE_SIZE


def test_the_table_holds_no_duplicate_address():
    addresses = [a.address for a in ADMISSIONS]
    assert len(addresses) == len(set(addresses)), addresses
