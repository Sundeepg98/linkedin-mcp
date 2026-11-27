"""Lane msg7 admissions (wave 7): two addresses session 12 drew or answered, red-first.

Record: ``_audit/2026-11-27-msg7.md``, sections 3 and 5. Each admission below
implements one ruling the orchestrator has already made -- this lane decides
none of them -- and each line is the spelling the ruling names:

* ADMIT-NOW-LANDING-IN-SESSION-14 (the orchestrator, 2026-11-27 12:35 IST,
  registration owed at integration 7): "Admit /my-items/saved-posts/ and the
  hashtag address now, anchored and red first. Each admission goes in ONE
  commit with its census lines." Each address then gets one read-only
  landing-and-capture load in session 14, and "If a landing check fails, the
  next integration reverts that admission." Both are refused today by
  allowlist SILENCE alone, so READ-PAST-AN-ACT-SUBSTRING's second clause: one
  exact anchored pattern, a control shown failing.

THE CONDITIONS, EACH A TEST BELOW, are lane admit26's harness
(``tests/test_admit26_admissions.py``), applied unchanged, as lane admit5-26
applied it:

1. ONE exact, anchored pattern per address, carrying no wildcard.
2. A control is shown failing: every sibling spelling is still refused, on the
   gate its entry names, and the refusal's own sentence is checked.
3. No forbidden substring is crossed, so no exemption exists and the forbidden
   tuple is unchanged.
4. The blast radius, measured on concrete urls before and after (never a
   grep): each admission newly admits exactly its own spellings and refuses
   nothing new.

Nothing here opens a page. Every variable segment is a placeholder.
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

#: The allowlist's own refusal sentence, as the shipped gate writes it
#: (tests/test_refusal_names_both_gates.py pins it).
ALLOWLIST_SENTENCE = "not on the read-only allowlist"

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
    siblings: tuple
    spellings: tuple = ()
    twin: bool = True


def _slash_twin(url: str) -> str:
    return url[:-1] if url.endswith("/") else url + "/"


def _own(adm) -> set:
    own = {adm.address, *adm.spellings}
    if adm.twin:
        own.add(_slash_twin(adm.address))
    return own


ADMISSIONS = (
    Admission(
        key="my-items-saved-posts",
        ruling="ADMIT-NOW-LANDING-IN-SESSION-14",
        rows=("M C36", "M C37"),
        address=f"{B}/my-items/saved-posts/",
        siblings=(
            Sibling(f"{B}/my-items/", None, "the family root"),
            Sibling(f"{B}/my-items/saved-jobs/", None,
                    "his saved jobs, which readonly.py records as redirecting to "
                    "the job tracker: refused before and after"),
            Sibling(f"{B}/my-items/saved-posts/?x=1", None, "a QUERY"),
            Sibling(f"{B}/my-items/saved-posts/x/", None, "a SUB-PATH"),
            Sibling(f"{B}/my-items/saved-posts/unsave/", None,
                    "an act's spelling under it: a sub-path"),
            Sibling(f"{B}/my-items/saved-postsx/", None, "a longer word"),
            Sibling(f"{B}/my-items/saved-post/", None, "the singular"),
            Sibling(f"{B}/my-items/Saved-Posts/", None,
                    "another case: the line is matched as written"),
            Sibling(f"{B}/my-items/posts/", None,
                    "another tail the runner's closed list named"),
            Sibling(f"{B}/my-items/saved-articles/", None, "a sibling list nothing draws"),
            Sibling(f"{B}/my-items/saved-posts/#x", None, "a FRAGMENT"),
            Sibling(f"{B}/my-items/saved-posts/x/../../../in/someone-else/", None,
                    "a TRAVERSAL onto a third party"),
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


@pytest.mark.parametrize("adm", ADMISSIONS, ids=KEYS)
def test_it_trips_no_forbidden_substring_and_carries_no_exemption(adm):
    # MEASURED against the shipped tuple: allowlist silence was the only gate.
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
    """The proven rollback: the one line removed, the address refuses again."""
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
