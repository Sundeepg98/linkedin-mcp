"""Every address the settings index draws, pinned by GATE -- not just boolean.

MEASURED FACT, taken directly against the shipped predicate rather than
argued from reading the source. On 2026-09-19 the settings index
``https://www.linkedin.com/mypreferences/d/`` -- already on this server's
read allowlist -- was loaded and every settings-family href the page draws
was enumerated: 33 anchors, 20 distinct ``/mypreferences/...`` paths. Each of
those 20, plus the index itself (21 addresses total), was run through the
shipped predicate ``linkedin_server.readonly.is_read_url`` and the GATE that
refused it was recorded by asking the module's own structures, in the
module's own order.

WHY THE GATE MATTERS AND NOT JUST THE BOOLEAN. This repo has twice caught two
urls returning the same ``False`` for different reasons being read as one
fact. A refusal by FORBIDDEN SUBSTRING cannot be lifted by adding an
allowlist pattern -- that gate runs BEFORE the allowlist loop inside
``assert_read_url`` and stops the check before any pattern is even
consulted. A refusal by ALLOWLIST MISS is admitted the moment somebody adds a
pattern whose shape happens to match it. Those two refusals want OPPOSITE
remedies, so pinning only the boolean would let either kind of maintenance
edit silently reclassify an address without a single assertion here
noticing which kind of edit it was.

This file opens nothing and edits nothing in readonly.py: every verdict below
was measured against the module exactly as shipped, and the two tests that
widen the allowlist do so with pytest's monkeypatch fixture, which is
guaranteed to restore the original tuple when each test ends -- so no test in
this file, or any test that runs after it in the same process, can inherit a
widened boundary.

THE GATE CLASSIFIER (``_gate_for`` below) is adapted from a working reference
implementation at ``_audit/_scratch/_settings_gate_classify.py`` (function
``gate_for``), copied in rather than imported because that script is
untracked scratch. It is rewritten here to mirror ``assert_read_url``'s own
exemption lookup exactly -- the exact-url dict is tried first, and the
pattern-exemption table is consulted only when the dict names nothing, never
both combined for one url -- rather than the reference script's shortcut of
checking both unconditionally. For every url this file exercises the two
formulations agree (measured, not assumed: none of the 21 addresses below
appears in ``_FORBIDDEN_SUBSTRING_EXEMPTIONS`` or matches either pattern in
``_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS``), but this version is written to
be correct even for a url where they would not.
"""

from __future__ import annotations

import re

from linkedin_server import readonly

BASE = "https://www.linkedin.com"

# ---------------------------------------------------------------------------
# 1. The 21 addresses, their pinned verdicts, and the gate that produces each
#    -- measured 2026-09-19 off the settings index's own drawn hrefs.
# ---------------------------------------------------------------------------

#: gate is one of:
#:   "allowlist match"            -- admitted by _ALLOWED_URL_PATTERNS
#:   "FORBIDDEN SUBSTRING '<str>'" -- refused before the allowlist is even
#:                                    consulted; SURVIVES an allowlist widening
#:   "NO PATTERN MATCHES"         -- refused only because nothing on the
#:                                    allowlist admits it; FALLS to a widening
_MEASURED_VERDICTS: tuple[tuple[str, bool, str], ...] = (
    ("/mypreferences/d/", True, "allowlist match"),
    ("/mypreferences/d/dark-mode", True, "allowlist match"),
    (
        "/mypreferences/d/categories/account",
        False,
        "FORBIDDEN SUBSTRING '/mypreferences/d/categories/'",
    ),
    (
        "/mypreferences/d/categories/ads",
        False,
        "FORBIDDEN SUBSTRING '/mypreferences/d/categories/'",
    ),
    (
        "/mypreferences/d/categories/notifications",
        False,
        "FORBIDDEN SUBSTRING '/mypreferences/d/categories/'",
    ),
    (
        "/mypreferences/d/categories/privacy",
        False,
        "FORBIDDEN SUBSTRING '/mypreferences/d/categories/'",
    ),
    (
        "/mypreferences/d/categories/profile-visibility",
        False,
        "FORBIDDEN SUBSTRING '/mypreferences/d/categories/'",
    ),
    (
        "/mypreferences/d/categories/sign-in-and-security",
        False,
        "FORBIDDEN SUBSTRING '/mypreferences/d/categories/'",
    ),
    (
        "/mypreferences/d/close-accounts",
        False,
        "FORBIDDEN SUBSTRING '/close-accounts'",
    ),
    (
        "/mypreferences/d/connected-microsoft-accounts",
        False,
        "FORBIDDEN SUBSTRING '/connect'",
    ),
    ("/mypreferences/d/demographic-info-copy", False, "NO PATTERN MATCHES"),
    (
        "/mypreferences/d/hibernate-account",
        False,
        "FORBIDDEN SUBSTRING '/hibernate-account'",
    ),
    ("/mypreferences/d/language-for-translation", False, "NO PATTERN MATCHES"),
    ("/mypreferences/d/premium-manage-account", False, "NO PATTERN MATCHES"),
    (
        "/mypreferences/d/settings/autoplay-videos",
        False,
        "FORBIDDEN SUBSTRING '/settings/'",
    ),
    (
        "/mypreferences/d/settings/enable-sounds-desktop",
        False,
        "FORBIDDEN SUBSTRING '/settings/'",
    ),
    (
        "/mypreferences/d/settings/language",
        False,
        "FORBIDDEN SUBSTRING '/settings/'",
    ),
    (
        "/mypreferences/d/settings/preferred-view",
        False,
        "FORBIDDEN SUBSTRING '/settings/'",
    ),
    (
        "/mypreferences/d/settings/show-profile-photos",
        False,
        "FORBIDDEN SUBSTRING '/settings/'",
    ),
    ("/mypreferences/d/unfollowed", False, "FORBIDDEN SUBSTRING '/unfollow'"),
    ("/mypreferences/d/verifications", False, "FORBIDDEN SUBSTRING 'verification'"),
)

#: THE ONE-LINE EDIT a future wave would most plausibly make to discharge
#: several "allowlist +1" ledger rows at once: admit any single lowercase /
#: digit / hyphen segment directly under /mypreferences/d/. Tests 3 and 5
#: both apply this same pattern via monkeypatch, which restores
#: readonly._ALLOWED_URL_PATTERNS at the end of each test regardless of
#: outcome.
_FAMILY_PATTERN = re.compile(r"^https://www\.linkedin\.com/mypreferences/d/[a-z0-9-]+/?$")


# ---------------------------------------------------------------------------
# 2. The gate classifier -- names WHICH gate produced a refusal, not just
#    that one occurred.
# ---------------------------------------------------------------------------


def _exempted_substrings(url: str, lowered: str) -> frozenset[str]:
    """Mirrors assert_read_url's own exemption lookup, in its own order: the
    exact-url dict is tried first, and the pattern table is consulted only
    when the dict names nothing for this url -- never both combined.
    """
    exact = readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS.get(lowered)
    if exact is not None:
        return frozenset({exact})
    for pattern, substrings in readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS:
        if pattern.match(url):
            return substrings
    return frozenset()


def _gate_for(url: str) -> str:
    """Name the gate that decides ``url``, asking readonly's own structures
    in readonly's own order: the forbidden-substring loop runs BEFORE the
    allowlist loop inside assert_read_url, so this function checks the
    substrings first rather than reaching for the allowlist because it is
    the more familiar gate.
    """
    lowered = url.lower()
    exempted = _exempted_substrings(url, lowered)
    for bad in readonly._FORBIDDEN_URL_SUBSTRINGS:
        if bad in lowered and bad not in exempted:
            return "FORBIDDEN SUBSTRING %r" % bad
    for pattern in readonly._ALLOWED_URL_PATTERNS:
        if pattern.match(url):
            return "allowlist match"
    return "NO PATTERN MATCHES"


# ---------------------------------------------------------------------------
# 3. Every drawn address has its verdict pinned
# ---------------------------------------------------------------------------


def test_every_settings_address_the_index_draws_has_its_verdict_pinned():
    for path, expected_is_read, _gate in _MEASURED_VERDICTS:
        url = BASE + path
        actual = readonly.is_read_url(url)
        assert actual is expected_is_read, (
            f"{url!r}: is_read_url returned {actual!r}, expected "
            f"{expected_is_read!r} -- this address's admitted/refused status "
            "changed since the 2026-09-19 measurement this file pins. If "
            "the change was a deliberate boundary edit, re-measure this "
            "address's gate with _gate_for and update its row in "
            "_MEASURED_VERDICTS to match; if nobody meant to change it, the "
            "boundary moved by accident and that is the thing to chase "
            "before touching this test."
        )


# ---------------------------------------------------------------------------
# 4. Every refusal names the gate it actually comes from
# ---------------------------------------------------------------------------


def test_each_refusal_names_the_gate_it_comes_from():
    for path, expected_is_read, expected_gate in _MEASURED_VERDICTS:
        if expected_is_read:
            continue
        url = BASE + path
        actual_gate = _gate_for(url)
        assert actual_gate == expected_gate, (
            f"{url!r}: refused by {actual_gate!r}, expected {expected_gate!r} "
            "-- these two refusals are NOT interchangeable. A FORBIDDEN "
            "SUBSTRING refusal survives an allowlist widening (see test 5 "
            "below); an ALLOWLIST MISS ('NO PATTERN MATCHES') is admitted "
            "the moment a pattern is added that matches its shape (see test "
            "3 below). Re-measure with _gate_for before updating the pinned "
            "gate -- do not just flip the string to make this pass."
        )


# ---------------------------------------------------------------------------
# 5. Control: the classifier can report ADMISSION, not only refusal
# ---------------------------------------------------------------------------


def test_the_classifier_can_report_admission_not_only_refusal():
    """Without this, test_each_refusal_names_the_gate_it_comes_from could be
    vacuous in a way nothing else here would catch: it only calls _gate_for
    on refused rows. If _gate_for were hardwired to always return a refusal
    string, that test would still pass. This proves the two already-admitted
    addresses in this family -- the index itself and dark-mode -- are seen
    as admitted by BOTH readonly.is_read_url and this file's own _gate_for,
    under the shipped, unmodified boundary.
    """
    for path in ("/mypreferences/d/", "/mypreferences/d/dark-mode"):
        url = BASE + path
        assert readonly.is_read_url(url) is True, (
            f"{url!r} should be an admitted read under the shipped, "
            "unmodified allowlist -- if this fails, the boundary changed "
            "and every other assertion in this file needs re-measuring "
            "before it can be trusted"
        )
        gate = _gate_for(url)
        assert gate == "allowlist match", (
            f"{url!r}: _gate_for reported {gate!r}, expected "
            "'allowlist match' -- is_read_url still says this url is "
            "admitted, so if this assertion fails, _gate_for has diverged "
            "from assert_read_url's real control flow and its output on "
            "every refused row above is no longer trustworthy either"
        )


# ---------------------------------------------------------------------------
# 6. THE LOAD-BEARING TEST -- the measured blast radius of one plausible edit
# ---------------------------------------------------------------------------


def test_a_settings_family_pattern_admits_exactly_these_and_no_more(monkeypatch):
    """PASSES TODAY, and that is the point: it measures exactly which of the
    19 currently-refused addresses a single, plausible allowlist edit would
    silently admit -- the edit a future wave would most naturally reach for
    to discharge several "allowlist +1" ledger rows at once with one line,
    rather than one deliberate entry per address the way every other pattern
    on _ALLOWED_URL_PATTERNS was added.

    THE SET BELOW WAS MEASURED, NOT INFERRED FROM THE PATTERN'S SHAPE: run by
    applying exactly this monkeypatch and calling readonly.is_read_url on
    all 21 addresses, both before and after, and diffing the two admitted
    sets. See the verification run recorded in
    _audit/_scratch/_settings-guard-slice.md.
    """
    already_admitted = {path for path, is_read, _gate in _MEASURED_VERDICTS if is_read}

    widened = readonly._ALLOWED_URL_PATTERNS + (_FAMILY_PATTERN,)
    monkeypatch.setattr(readonly, "_ALLOWED_URL_PATTERNS", widened)

    now_admitted = {
        path for path, _is_read, _gate in _MEASURED_VERDICTS if readonly.is_read_url(BASE + path)
    }
    newly_admitted = now_admitted - already_admitted

    # THE MEASURED BLAST RADIUS -- three addresses nobody has ever ruled on,
    # each refused today only by allowlist miss (NO PATTERN MATCHES in
    # _MEASURED_VERDICTS above), that this one-line edit would silently open:
    expected_blast_radius = {
        "/mypreferences/d/demographic-info-copy",
        "/mypreferences/d/language-for-translation",
        "/mypreferences/d/premium-manage-account",
    }
    assert newly_admitted == expected_blast_radius, (
        f"the family pattern newly admitted {sorted(newly_admitted)!r}, "
        f"expected exactly {sorted(expected_blast_radius)!r} -- this is the "
        "measured blast radius of the one-line edit this test exists to "
        "document. If the set changed, some address that used to be refused "
        "only by allowlist miss either gained an earlier forbidden-"
        "substring refusal (shrinking this set) or lost one (growing it) -- "
        "re-run the measurement described in this test's docstring before "
        "updating expected_blast_radius; do not just paste in whatever this "
        "run produced."
    )


# ---------------------------------------------------------------------------
# 7. The contrast that matters -- a name-based refusal survives; a
#    shape-based one does not
# ---------------------------------------------------------------------------


def test_the_denylisted_addresses_survive_the_widened_allowlist(monkeypatch):
    """Under the exact same widened allowlist as test 6 above, every address
    refused by a NAMED forbidden substring must stay refused: close-accounts,
    hibernate-account, unfollowed, verifications, connected-microsoft-
    accounts (via '/connect'), and every categories/ and settings/ path.

    THIS IS THE CONTRAST THE WHOLE FILE EXISTS TO MAKE VISIBLE: a name-based
    refusal survives a widened allowlist because the forbidden-substring gate
    runs BEFORE the allowlist is ever consulted; a shape-based refusal (test
    6) does not, because it has no gate standing in front of the allowlist at
    all. Same edit, two different outcomes, and the difference is which gate
    produced the original refusal -- which is exactly why test 4 above pins
    the gate and not only the boolean.
    """
    still_named_refused = [
        path
        for path, is_read, gate in _MEASURED_VERDICTS
        if not is_read and gate != "NO PATTERN MATCHES"
    ]
    # Sanity on the fixture itself: this must be the 16 FORBIDDEN SUBSTRING
    # rows (19 refused rows total, minus the 3 NO-PATTERN-MATCHES rows that
    # test 6 shows falling). A file that silently lost a row here would make
    # the loop below assert nothing about it.
    assert len(still_named_refused) == 16, (
        f"expected 16 forbidden-substring-refused addresses in "
        f"_MEASURED_VERDICTS, found {len(still_named_refused)}: "
        f"{sorted(still_named_refused)!r} -- a row's gate classification "
        "changed; fix _MEASURED_VERDICTS rather than this count"
    )

    widened = readonly._ALLOWED_URL_PATTERNS + (_FAMILY_PATTERN,)
    monkeypatch.setattr(readonly, "_ALLOWED_URL_PATTERNS", widened)

    for path in still_named_refused:
        url = BASE + path
        assert not readonly.is_read_url(url), (
            f"{url!r} was refused by a named forbidden substring under the "
            "shipped boundary, but is now ADMITTED under the widened "
            "allowlist used here -- a name-based refusal is supposed to "
            "survive an allowlist widening; if it no longer does, the "
            "forbidden-substring gate is not running before the allowlist "
            "loop any more inside assert_read_url, which is a far bigger "
            "change than this test's premise accounts for and needs "
            "investigating in readonly.py itself, not silencing here"
        )
