"""His "Sharing profile edits" setting page is admitted for READING, and nothing else is.

The live lane, 2026-09-27: the orchestrator's application of
ONE-NAMED-SETTINGS-PAGE-AT-A-TIME, step 1 of the capture spec in section (f)
of ``_audit/2026-09-23-live-lane-session-1.md``. The page holds the
account-level setting condition 1 of SELF-PROFILE-EDITS-NOT-OUTWARD now rests
on where the edit dialog draws no notify control
(SELF-PROFILE-EDIT-NOTIFY-CONDITION-AMENDED). The argument is on the line in
``linkedin_server/readonly.py``.

THE TWO GATES ARE BOTH NEEDED AND THIS FILE SHOWS IT, the shape lane L1's
follower-list carve-out set (``tests/test_l1_follower_list_carve_out.py``):
remove the exemption and the address refuses on ``/settings/`` (with the
sentence saying a pattern WOULD admit it); remove the allowlist line and it
refuses on the allowlist's own sentence. Either half alone admits nothing.

THE CONTROLS THE ORDER NAMED: a sibling settings page
(``/mypreferences/d/settings/show-profile-photos``) stays refused, and so does
this address with anything beneath it.

READ ONLY: ``writes.assert_write_url`` does not consult the exemption tables,
so no write reaches this address through this admission -- asserted below on
the write door itself.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from linkedin_server import readonly
from linkedin_server.errors import WriteAttemptError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import blast_radius  # noqa: E402

B = "https://www.linkedin.com"
SETTING = f"{B}/mypreferences/d/settings/notify-network-for-updates"
CARRIER = "notify-network-for-updates"

#: (url, the substring that must refuse it -- None where the allowlist is the
#: whole refusal -- and why)
NEIGHBOURS = (
    (f"{B}/mypreferences/d/settings/show-profile-photos", "/settings/",
     "A SIBLING settings page -- the order's named control"),
    (f"{B}/mypreferences/d/settings/language", "/settings/",
     "a sibling the dark-mode entry declined by name"),
    (f"{B}/mypreferences/d/settings/autoplay-videos", "/settings/",
     "the other sibling the dark-mode entry declined by name"),
    (SETTING + "/anything", "/settings/",
     "this address with a SUB-PATH -- the order's named control"),
    (SETTING + "/", None, None),  # placeholder, replaced below: ADMITTED
    (SETTING + "?x=1", "/settings/",
     "this address with a QUERY -- the anchor is load-bearing"),
    (SETTING + "/../show-profile-photos", "/settings/",
     "a TRAVERSAL onto a sibling"),
    (SETTING + "/../../../close-accounts", "/settings/",
     "a TRAVERSAL onto the account-ending address"),
    (f"{B}/mypreferences/d/settings/NOTIFY-network-for-updates", "/settings/",
     "the same path in another CASE -- the exemption is case-sensitive"),
    (f"{B}/mypreferences/d/notify-network-for-updates", None,
     "THE OTHER CANDIDATE -- not admitted until this one is seen to redirect"),
    (f"{B}/mypreferences/d/categories/profile-visibility",
     "/mypreferences/d/categories/", "the CATEGORY page that lists the setting"),
    (f"{B}/psettings/activity-broadcast", "/psettings/",
     "the OLD address, a family refused outright"),
    (f"{B}/mypreferences/d/settings/", "/settings/", "the settings family root"),
)
NEIGHBOURS = tuple(n for n in NEIGHBOURS if n[2] is not None)


def _refusal(url: str) -> str:
    with pytest.raises(WriteAttemptError) as caught:
        readonly.assert_read_url(url)
    return str(caught.value)


def _allow_lines():
    return [p for p in readonly._ALLOWED_URL_PATTERNS if CARRIER in p.pattern]


def _exempt_entries():
    return [
        (p, s) for p, s in readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS
        if p.match(SETTING)
    ]


def test_the_setting_page_is_admitted_through_the_shipped_gate():
    assert readonly.is_read_url(SETTING)
    assert readonly.is_read_url(SETTING + "/")


def test_exactly_one_line_and_one_exemption_carry_it():
    assert len(_allow_lines()) == 1, [p.pattern for p in _allow_lines()]
    entries = _exempt_entries()
    assert len(entries) == 1, entries
    assert entries[0][1] == frozenset({"/settings/", "settings"}), entries[0][1]


def test_the_exemption_excuses_exactly_the_two_it_trips_and_only_here():
    """MEASURED, not assumed: the address trips exactly these two substrings
    of the forbidden tuple, and the exemption names those two and no more."""
    tripped = {s for s in readonly._FORBIDDEN_URL_SUBSTRINGS if s in SETTING.lower()}
    assert tripped == {"/settings/", "settings"}, tripped
    assert readonly._pattern_exempted_substrings(SETTING) == frozenset(tripped)
    for url, _bad, why in NEIGHBOURS:
        assert readonly._pattern_exempted_substrings(url) == frozenset(), why


@pytest.mark.parametrize("url,bad,why", NEIGHBOURS)
def test_every_neighbour_is_still_refused_on_its_own_gate(url, bad, why):
    assert not readonly.is_read_url(url), why
    message = _refusal(url)
    if bad is None:
        assert "is not on the read-only allowlist" in message, (why, message)
        return
    assert "contains %r" % bad in message, (why, message)
    assert "not a read surface" in message, (why, message)


def test_the_forbidden_tuple_is_unchanged_and_still_names_both_words():
    assert "/settings/" in readonly._FORBIDDEN_URL_SUBSTRINGS
    assert "settings" in readonly._FORBIDDEN_URL_SUBSTRINGS
    assert len(readonly._FORBIDDEN_URL_SUBSTRINGS) == 33


def test_without_the_exemption_the_substring_refuses_and_says_a_pattern_would_admit(
    monkeypatch,
):
    """THE FIRST GATE ALONE: the allowlist line cannot admit it by itself."""
    kept = tuple(
        (p, s) for p, s in readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS
        if not p.match(SETTING)
    )
    assert len(kept) == len(readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS) - 1
    monkeypatch.setattr(readonly, "_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS", kept)
    assert not readonly.is_read_url(SETTING)
    message = _refusal(SETTING)
    assert "contains '/settings/'" in message, message
    assert "A READ PATTERN DOES ADMIT THIS ADDRESS" in message, message


def test_without_the_allowlist_line_the_allowlist_refuses_it(monkeypatch):
    """THE SECOND GATE ALONE: the exemption cannot admit it by itself -- and
    this is also the proven rollback of the allowlist half."""
    kept = tuple(p for p in readonly._ALLOWED_URL_PATTERNS if CARRIER not in p.pattern)
    assert len(kept) == len(readonly._ALLOWED_URL_PATTERNS) - 1
    monkeypatch.setattr(readonly, "_ALLOWED_URL_PATTERNS", kept)
    assert not readonly.is_read_url(SETTING)
    assert "is not on the read-only allowlist" in _refusal(SETTING)


def test_the_pair_newly_admits_exactly_its_own_two_spellings():
    """THE BLAST RADIUS of the PAIR, over the shipped corpus plus this file's
    spellings, measured the way ``blast_radius`` measures -- ``is_read_url``
    before and after, on concrete urls, never a grep."""
    corpus = sorted(
        set(blast_radius.corpus())
        | {SETTING, SETTING + "/"}
        | {url for url, _bad, _why in NEIGHBOURS}
    )
    allow = readonly._ALLOWED_URL_PATTERNS
    exempt = readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS
    after = {url: readonly.is_read_url(url) for url in corpus}
    try:
        readonly._ALLOWED_URL_PATTERNS = tuple(
            p for p in allow if CARRIER not in p.pattern
        )
        readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS = tuple(
            (p, s) for p, s in exempt if not p.match(SETTING)
        )
        before = {url: readonly.is_read_url(url) for url in corpus}
    finally:
        readonly._ALLOWED_URL_PATTERNS = allow
        readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS = exempt
    gained = sorted(u for u in corpus if after[u] and not before[u])
    lost = sorted(u for u in corpus if before[u] and not after[u])
    assert gained == sorted({SETTING, SETTING + "/"}), gained
    assert lost == [], lost


def test_the_line_names_nobody_and_nothing_else():
    """No class, no wildcard, no group, no query, no member segment."""
    source = _allow_lines()[0].pattern
    for token in ("[", ".*", ".+", r"\w", r"\d", "+", "(", "/in/"):
        assert token not in source, (token, source)
    assert source.endswith("notify-network-for-updates/?$"), source


def test_it_is_no_write_surface():
    """READ ONLY, on the write door's own terms. ``assert_write_url`` rebuilds
    the url from a grant's spec and walks the forbidden tuple honouring only
    that spec's ``exempt_substring`` -- it consults neither exemption table.
    So no write reaches this address unless a spec names it or exempts one of
    the two words it trips, and none does."""
    from linkedin_server import writes

    specs = list(writes.SANCTIONED_WRITES.values())
    assert specs, "the write registry is empty -- this check would pass on nothing"
    naming = [
        spec.action for spec in specs
        if CARRIER in str(spec.url_template or "")
        or (spec.url_pattern is not None and spec.url_pattern.match(SETTING))
    ]
    assert naming == [], naming
    exempting = [
        spec.action for spec in specs
        if spec.exempt_substring in ("/settings/", "settings")
    ]
    assert exempting == [], exempting
