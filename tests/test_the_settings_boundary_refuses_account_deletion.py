"""The settings boundary must refuse account deletion by NAME, not by accident.

MEASURED FACT, taken directly against the shipped predicate rather than
argued from reading the source: LinkedIn's account-deletion address is
refused today ONLY because no entry in readonly._ALLOWED_URL_PATTERNS happens
to match it -- not because any entry in readonly._FORBIDDEN_URL_SUBSTRINGS
names it. That is a property of the allowlist's current SHAPE, not a decision
anyone made about account deletion specifically. And the shape is one edit
away from changing: a single family-shaped settings pattern -- the kind a
future wave would naturally write to collapse several "allowlist +1"
gap-ledger rows into one entry, spelled out exactly in
test_a_settings_family_pattern_would_admit_account_deletion below -- would
ALSO admit account deletion, because that address lives under the exact same
path prefix as every other settings page this server is allowed to read.

This file turns that accident into an assertion a suite can see fail. It does
NOT edit readonly.py: every url below is refused by the module exactly as
shipped, and the one test that widens the allowlist (the load-bearing one)
does so with pytest's monkeypatch fixture, which is guaranteed to restore the
original tuple when the test ends -- so no test in this file, or any test
that runs after it in the same process, can inherit a widened boundary.
"""

from __future__ import annotations

import re

from linkedin_server import readonly

# ---------------------------------------------------------------------------
# 1. The spellings
# ---------------------------------------------------------------------------

#: Every address hunted here reaches the same LinkedIn action: permanently
#: closing and deleting the account. None of these strings names a person --
#: they are LinkedIn's own product addresses.
_ACCOUNT_DELETION_URLS: tuple[str, ...] = (
    "https://www.linkedin.com/mypreferences/d/close-account",
    "https://www.linkedin.com/mypreferences/d/close-account/",
    "https://www.linkedin.com/psettings/close-account",
    "https://www.linkedin.com/mypreferences/d/close-account?trk=x",
    # A FURTHER PLAUSIBLE SPELLING, justified rather than guessed. readonly.py's
    # own comment on _FORBIDDEN_URL_SUBSTRINGS records: "measured off a live
    # census 2026-08-31, their real addresses are /mypreferences/d/close-accounts
    # and /mypreferences/d/hibernate-account" -- plural "accounts" -- and that
    # exact string sits on the forbidden-substrings tuple today as
    # "/close-accounts". Included so this file also asserts against the ONE
    # spelling the shipped module already refuses BY NAME, in contrast with the
    # four above, which it refuses only because nothing on the allowlist admits
    # them. See index [4] in test_a_settings_family_pattern_would_admit_account_
    # deletion below, where that contrast is the whole point.
    "https://www.linkedin.com/mypreferences/d/close-accounts",
)

#: The one already-admitted settings page below the index. Used as the control
#: that proves this file is not asserting a blanket settings refusal, which
#: would be trivially satisfiable.
_ADMITTED_SETTINGS_URL = "https://www.linkedin.com/mypreferences/d/dark-mode"

#: A known-admitted, non-settings url. Used only to prove the detector below
#: can report "admitted" and is not hardwired to always say "refused".
_KNOWN_ADMITTED_URL = "https://www.linkedin.com/in/me/"


def _refused(url: str) -> bool:
    """True if the shipped predicate refuses ``url`` as a read.

    Factored out so this file has ONE detector to prove honest --
    test_the_detector_can_report_admission below -- rather than trusting every
    assertion in this file to call readonly.is_read_url correctly on its own.
    Wraps is_read_url and nothing else: no reimplementation of url matching.
    """
    return readonly.is_read_url(url) is False


# ---------------------------------------------------------------------------
# 2. Every spelling of account deletion is refused, today, as shipped
# ---------------------------------------------------------------------------


def test_every_account_deletion_spelling_is_refused():
    for url in _ACCOUNT_DELETION_URLS:
        assert _refused(url), f"account-deletion address admitted as a read: {url!r}"


# ---------------------------------------------------------------------------
# 3. THE LOAD-BEARING TEST -- the refusal above is an accident of shape
# ---------------------------------------------------------------------------


def test_a_settings_family_pattern_would_admit_account_deletion(monkeypatch):
    """PASSES TODAY, and that is the point: it proves the refusal above is an
    accident of the allowlist's shape rather than a decision anyone made,
    because one plausible settings-family pattern is all it takes to admit
    account deletion as a permitted read.
    """
    family_pattern = re.compile(
        r"^https://www\.linkedin\.com/mypreferences/d/[a-z0-9-]+/?$"
    )
    widened = readonly._ALLOWED_URL_PATTERNS + (family_pattern,)
    monkeypatch.setattr(readonly, "_ALLOWED_URL_PATTERNS", widened)

    target = _ACCOUNT_DELETION_URLS[0]
    assert not _refused(target), (
        f"expected the family pattern to admit {target!r} -- that admission "
        "IS the hazard this test exists to document. If this assertion now "
        "fails, the hazard may have been closed some other way and this "
        "test's premise needs re-checking before the test is deleted, not "
        "silenced."
    )

    # THE DENYLIST STILL PROTECTS THE ONE SPELLING IT NAMES, even under this
    # same widened allowlist. "/close-accounts" (plural) is on
    # _FORBIDDEN_URL_SUBSTRINGS today, and that gate runs BEFORE the pattern
    # loop in assert_read_url -- so the one spelling readonly.py's own
    # settings-audit comment measured as LinkedIn's real address stays
    # refused here, while the singular spelling that nothing on the denylist
    # names is the one that falls. That contrast is the whole argument for
    # this test existing: a name-based refusal survives a widened allowlist;
    # a shape-based one does not.
    plural = _ACCOUNT_DELETION_URLS[4]
    assert _refused(plural), (
        f"the denylisted plural spelling {plural!r} should stay refused even "
        "under the widened allowlist used above -- if it is now admitted, "
        "the denylist gate no longer runs before the pattern loop, which is "
        "a bigger change than this test's premise accounts for"
    )


# ---------------------------------------------------------------------------
# 4. The control: this file is not asserting a blanket settings refusal
# ---------------------------------------------------------------------------


def test_the_one_admitted_settings_page_still_reads():
    assert not _refused(_ADMITTED_SETTINGS_URL), (
        f"{_ADMITTED_SETTINGS_URL!r} should still be an admitted read under "
        "the shipped, unmodified allowlist -- if this fails, either the "
        "boundary changed or a prior test in this file leaked a mutated "
        "_ALLOWED_URL_PATTERNS past its own monkeypatch teardown"
    )


# ---------------------------------------------------------------------------
# 5. The detector itself can report admission, not only refusal
# ---------------------------------------------------------------------------


def test_the_detector_can_report_admission():
    """Without this, every refusal assertion above could be passing because
    _refused always reports "refused" regardless of its argument.
    """
    assert not _refused(_KNOWN_ADMITTED_URL), (
        f"{_KNOWN_ADMITTED_URL!r} is a known-admitted read, but _refused "
        "reported it as refused -- the detector cannot currently tell "
        "admission from refusal, which means every refusal assertion above "
        "is unproven"
    )
