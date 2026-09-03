"""The forbidden list is a CLASS gate, not a list of addresses somebody hit.

WHAT THIS FILE EXISTS TO STOP HAPPENING A THIRD TIME.

``readonly._FORBIDDEN_URL_SUBSTRINGS`` documents itself as "a second,
independent gate" and as "belt and braces: a future pattern edited too loosely
still cannot reach these". Twice now that claim has been measured and found
false for a whole surface at once, and BOTH TIMES THE FIX WAS PER-ADDRESS:

* 2026-08-30 -- ``"/settings/"`` had been on the list since the beginning and
  matched NOTHING LinkedIn serves. Fixed by adding
  ``/mypreferences/d/categories/`` and ``/psettings/``.
* 2026-08-31 -- the two account-ending pages were assumed covered by
  ``categories/`` and were not. Fixed by adding ``/close-accounts`` and
  ``/hibernate-account``.

On 2026-09-03 the same question was asked MECHANICALLY instead of
incidentally: which addresses are refused by the anchored allowlist ALONE, with
no forbidden substring behind them? Ten came back, and reading them together
names the defect the two per-address fixes had both missed:

    THE FORBIDDEN LIST WAS ANCHORED TO PATH SPELLINGS ON THE DESKTOP TREE.

A surface reachable at a second SPELLING (``/public-profile/settings``, with no
trailing slash, which ``"/settings/"`` does not match), under a LEGACY
NAMESPACE (``/uas/``, the sibling of the ``/psettings/`` already on the list),
or on a PARALLEL TREE (``/mwlite/``, LinkedIn's entire mobile-web mirror) had
no second gate at all -- and every future page LinkedIn adds to any of them
would have arrived the same way.

NOTHING HERE WAS EVER REACHABLE. All ten are refused today and were refused
before this file existed; the anchored allowlist held every one. This is a
defence-in-depth asymmetry, not an open door, and saying so plainly is more
important than the fix.

WHAT MAKES THE FIX A CLASS FIX RATHER THAN TEN MORE LITERALS is not the
wording of its entries -- it is
:func:`test_each_new_entry_also_closes_an_address_nobody_listed`, which puts
an address through the real guard FOR EVERY NEW ENTRY that is not one of the
ten. An entry that closed only its own member would fail there.

AND ONE PART OF THE CLASS IS DELIBERATELY NOT CLOSED, for a reason that was
measured rather than argued. See
:func:`test_the_subtree_prefix_is_absent_and_the_blocker_is_shown`.
"""

from __future__ import annotations

import pytest

from linkedin_server import readonly, writes
from linkedin_server.errors import WriteAttemptError


def _refusing_substring(url: str) -> str:
    """Return the substring the REAL guard reported, or fail loudly.

    The message is the instrument, exactly as it is in
    ``test_readonly.py::test_the_two_account_ending_pages_are_refused_twice``:
    it is the only thing that tells the forbidden gate apart from the
    allowlist, and this whole file is about which gate refused.
    """
    with pytest.raises(WriteAttemptError) as caught:
        readonly.assert_read_url(url)
    message = str(caught.value)
    assert "not on the read-only allowlist" not in message, (
        f"{url} is refused by the ALLOWLIST ONLY. That is the defect this "
        "file exists to close: one layer where the documented promise is two."
    )
    assert "not a read surface" in message, message
    for bad in readonly._FORBIDDEN_URL_SUBSTRINGS:
        if repr(bad) in message:
            return bad
    raise AssertionError(f"no forbidden substring named in: {message}")


#: The ten, and the entry expected to catch each.
#:
#: RE-DERIVED, NOT INHERITED. ``_audit/_scratch/_probe_class_defect.py`` put
#: every one through the live guard and read back which layer refused it:
#: zero forbidden hits, zero allowlist hits, on all ten. The three controls in
#: that probe -- ``/close-accounts``, ``/hibernate-account`` and
#: ``/mypreferences/d/categories/privacy`` -- each came back with a forbidden
#: hit AS WELL, which is what makes the ten a finding rather than a listing.
#:
#: The expected entry is named per url so this cannot pass on some unrelated
#: substring happening to match. Where two new entries both cover an address
#: the first in tuple order is named, and
#: :func:`test_the_mobile_tree_is_covered_twice` asserts the second
#: independently rather than leaving it to ordering.
CLASS_MEMBERS = (
    ("https://www.linkedin.com/mypreferences/d/change-password", "password"),
    (
        "https://www.linkedin.com/mypreferences/d/two-factor-authentication",
        "two-factor",
    ),
    ("https://www.linkedin.com/mypreferences/d/verifications", "verification"),
    ("https://www.linkedin.com/mypreferences/d/member-cookies", "cookies"),
    (
        "https://www.linkedin.com/mypreferences/d/job-application-accounts",
        "job-application",
    ),
    (
        "https://www.linkedin.com/mypreferences/d/profile-visibility-for-partners",
        "visibility",
    ),
    ("https://www.linkedin.com/public-profile/settings", "settings"),
    ("https://www.linkedin.com/uas/login", "/uas/"),
    ("https://www.linkedin.com/badges/profile/create", "/create"),
    ("https://www.linkedin.com/mwlite/settings", "settings"),
)


@pytest.mark.parametrize("url,expected", CLASS_MEMBERS)
def test_each_class_member_is_refused_by_the_forbidden_gate(url, expected):
    """The ten now have TWO layers, and the message says which one spoke."""
    assert _refusing_substring(url) == expected
    assert expected in readonly._FORBIDDEN_URL_SUBSTRINGS


#: One address per new entry that is NOT one of the ten -- the proof that each
#: entry is a CLASS and not a rephrased literal.
#:
#: Every one is a real LinkedIn address shape rather than a hostile string: the
#: mobile mirror of a page the desktop tree already refuses, the legacy auth
#: namespace's own members, the spelling LinkedIn uses for two-step
#: verification, and a creation surface. An entry that closed only its own
#: member of the ten would fail here, which is the whole point.
#:
#: NONE OF THEM IS ON THE MOBILE TREE, and the first draft of this list had
#: three that were. ``/mwlite/`` sits ahead of the word entries in the tuple,
#: so it answers first for anything under it and those three cases proved
#: ``/mwlite/`` three times over instead of proving the word. That is defence
#: in depth working exactly as intended and it makes the mobile tree the wrong
#: instrument for this particular question, so each word is demonstrated on an
#: address only that word reaches.
CLASS_ALSO_CLOSES = (
    ("https://www.linkedin.com/settings", "settings"),
    ("https://www.linkedin.com/uas/oauth2/authorization", "/uas/"),
    ("https://www.linkedin.com/mwlite/feed", "/mwlite/"),
    ("https://www.linkedin.com/groups/12345/create", "/create"),
    (
        "https://www.linkedin.com/checkpoint/rp/request-password-reset",
        "password",
    ),
    (
        "https://www.linkedin.com/checkpoint/challenge/two-factor-authentication",
        "two-factor",
    ),
    (
        "https://www.linkedin.com/mypreferences/d/two-step-verification",
        "verification",
    ),
    ("https://www.linkedin.com/mypreferences/d/manage-cookies", "cookies"),
    (
        "https://www.linkedin.com/my-items/saved-job-applications",
        "job-application",
    ),
    (
        "https://www.linkedin.com/mypreferences/d/profile-visibility",
        "visibility",
    ),
)


@pytest.mark.parametrize("url,expected", CLASS_ALSO_CLOSES)
def test_each_new_entry_also_closes_an_address_nobody_listed(url, expected):
    """THE CLASS PROPERTY, and it is the only thing separating this change
    from the two per-address fixes it is correcting.

    None of these urls is one of the ten. Each is refused by the entry added
    for a DIFFERENT address, which is what "a class was closed" means and what
    "ten more literals" would have failed.
    """
    assert _refusing_substring(url) == expected


def test_the_mobile_tree_is_covered_twice():
    """``/mwlite/settings`` is closed by BOTH new entries that reach it.

    Named separately because the parametrised case above can only report
    whichever comes first in the tuple, and a reader would otherwise have to
    trust ordering for the claim that the tree entry covers it too.
    """
    url = "https://www.linkedin.com/mwlite/settings"
    lowered = url.lower()
    covering = [
        bad for bad in readonly._FORBIDDEN_URL_SUBSTRINGS if bad in lowered
    ]
    assert "settings" in covering, covering
    assert "/mwlite/" in covering, covering


#: The two spellings of one surface, for two surfaces.
#:
#: THE DEFECT IN MINIATURE. ``"/settings/"`` -- slashes on both sides -- has
#: been on the forbidden list since the beginning, and it catches the
#: trailing-slash spelling of both of these while missing the slashless one.
#: The gate was a spelling filter, and a ruling one spelling cannot express is
#: not a ruling.
SPELLING_PAIRS = (
    "https://www.linkedin.com/public-profile/settings",
    "https://www.linkedin.com/public-profile/settings/",
    "https://www.linkedin.com/mwlite/settings",
    "https://www.linkedin.com/mwlite/settings/",
)


@pytest.mark.parametrize("url", SPELLING_PAIRS)
def test_both_spellings_of_a_settings_surface_are_refused_by_the_gate(url):
    """BOTH spellings, one gate. Before this change the slashless half of each
    pair reached the allowlist and nothing else."""
    assert _refusing_substring(url) in ("settings", "/settings/", "/mwlite/")


def test_the_old_settings_entry_was_kept_rather_than_replaced():
    """``"/settings/"`` STAYS, and the redundancy is deliberate.

    The bare word is a strict superset of it, so replacing would have cost
    nothing behaviourally -- and it would have been a DELETION from a denylist
    that has only ever grown, needing an entry in
    ``FORBIDDEN_SUBSTRINGS_DELIBERATELY_REMOVED`` and the review that goes
    with one. A redundant refusal is free; a removed one is a boundary change.
    The module already made this exact call once, in the 2026-08-30 note that
    keeps ``"/settings/"`` after measuring that it matched nothing.
    """
    assert "/settings/" in readonly._FORBIDDEN_URL_SUBSTRINGS
    assert "settings" in readonly._FORBIDDEN_URL_SUBSTRINGS


def test_the_subtree_prefix_is_absent_and_the_blocker_is_shown(monkeypatch):
    """THE PART OF THE CLASS THAT IS NOT CLOSED, and why -- shown, not argued.

    Six of the ten live under ``/mypreferences/d/``. The natural close is that
    prefix, and it CANNOT BE TAKEN, for a reason measured rather than
    supposed: the six share with the two ADMITTED urls under that prefix --
    the settings index and ``/mypreferences/d/dark-mode`` -- only the prefix
    itself, so no substring separates them; and while
    ``readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS`` could hold the two admitted
    urls for the READ door, ``writes.assert_write_url`` does not consult that
    table at all. It iterates the forbidden tuple directly and honours only
    ``spec.exempt_substring``, which is ``None`` on the settings write.

    So adding the prefix closes six read addresses and BREAKS THE ONLY
    SETTINGS WRITE THIS SERVER SHIPS. That is demonstrated below rather than
    asserted, because a blocker nobody can re-run is a claim.

    THE REPAIR IS ONE LINE -- ``exempt_substring="/mypreferences/d/"`` on the
    ``update_setting`` spec -- and it is in ``writes.py``, which the agent who
    wrote this file did not own. Recorded here so the prefix entry is a
    decision somebody takes deliberately rather than a gap somebody rediscovers
    mechanically for a third time.

    WHAT COVERS THOSE SIX MEANWHILE is the word-shaped half of this change,
    and it is not merely a fallback: ``password`` refuses the password page at
    EVERY address, on the desktop tree, the mobile tree, the legacy namespace
    and whatever LinkedIn ships next. The prefix would refuse it at one.
    """
    assert "/mypreferences/d/" not in readonly._FORBIDDEN_URL_SUBSTRINGS

    spec = writes.spec_for_action("update_setting")
    assert spec.exempt_substring is None
    assert "/mypreferences/d/" in spec.url_template.lower()

    grant = writes.WriteGrant(
        action="update_setting",
        target="dark_mode=dark",
        token="not-a-real-token",
        minted_at=0.0,
    )
    # The write door admits its own target today.
    assert writes.assert_write_url(spec.url_template, grant) == spec.url_template

    monkeypatch.setattr(
        readonly,
        "_FORBIDDEN_URL_SUBSTRINGS",
        readonly._FORBIDDEN_URL_SUBSTRINGS + ("/mypreferences/d/",),
    )
    with pytest.raises(WriteAttemptError) as caught:
        writes.assert_write_url(spec.url_template, grant)
    message = str(caught.value)
    assert "/mypreferences/d/" in message, message
    assert "does not exempt" in message, message


def _shipped_corpus() -> list[str]:
    """Every url this package builds, gathered from the tables that decide it.

    The census surface table and the write specs, rather than a list retyped
    here, so a surface added later joins this check without anybody
    remembering to add it.

    ``{target}`` IS SUBSTITUTED WITH A JOB ID and that is deliberately WRONG
    for two of the specs -- ``comment_on_item`` and ``react_to_item`` take an
    activity urn, so those two come out as urls the anchored allowlist does
    not match. That costs nothing here because the check below FILTERS ON THE
    ALLOWLIST rather than trusting this corpus, and a mis-substituted url is
    simply not in scope. Filtering is not laziness: see the test.
    """
    from linkedin_server import server

    corpus = list(server.CENSUS_SURFACES.values())
    corpus += [str(url) for url in server.READABLE_SETTINGS.values()]
    for spec in writes.SANCTIONED_WRITES.values():
        if spec.url_template:
            corpus.append(spec.url_template.format(target="4600000042"))
    return sorted(set(corpus))


def test_the_widening_took_nothing_the_allowlist_grants():
    """A TIGHTENING WITH NO CASUALTIES IS A FACT WORTH STATING RATHER THAN
    ASSUMING -- the phrasing, and the discipline, are the 2026-09-03 allowlist
    re-freeze's own.

    Ten refusals were added to a gate every navigation passes through, and the
    claim that none of them cost a surface this server needs is checkable.

    THE INSTRUMENT IS THE RELATION BETWEEN THE TWO GATES, not a snapshot of
    what opens. For every url this package builds that the ANCHORED ALLOWLIST
    ADMITS, ``assert_read_url`` must still admit it -- which can only fail if a
    forbidden substring stole it, because nothing here touches the allowlist.
    A snapshot would have had to be re-baselined by the same edit it was
    checking; this cannot be.
    """
    granted = [
        url
        for url in _shipped_corpus()
        if any(pattern.match(url) for pattern in readonly._ALLOWED_URL_PATTERNS)
    ]
    # Not vacuous: the filter must leave a real corpus behind.
    assert len(granted) >= 10, granted
    stolen = [url for url in granted if not readonly.is_read_url(url)]
    assert stolen == [], (
        f"the class close cost these surfaces: {stolen}. Each is a url this "
        "package builds AND the allowlist admits, so a forbidden substring "
        "took it."
    )
