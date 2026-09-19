"""THE REVERT PATH FOR THE SEARCH-RESULTS ADMISSION, WRITTEN BEFORE IT LANDS.

**THIS FILE'S JOB IS TO GO RED.** It is committed green, today, while nothing
is admitted -- and the wave that lands the `SEARCH-RESULTS-SURFACE` pattern
will turn it red on its first run. That is not a defect in this file and it is
not a defect in that wave. It is the point.

Condition 4 of the ruling at `09f9961` section 6: *"A REVERT PATH EXISTS BEFORE
THE ADMISSION, NOT AFTER. The pattern's removal is one line; the test that
shows the address refused must be written and shown failing BEFORE the pattern
is added, so the rollback is proven rather than assumed."*

**WHAT THE ADMITTING WAVE MUST DO WITH THIS FILE, stated here so it is not a
judgement call at 2am.** **REWRITE IT AND INVERT IT**, in the same commit that
adds the pattern: the entries in `_SEARCH_RESULTS_URLS` that the pattern now
admits flip to asserting they ARE admitted, and everything the pattern must
still refuse stays asserting refusal. Do NOT silence it, do NOT narrow its url
list to whatever still refuses, and do NOT mark it xfail.

**THIS SAID "DELETE IT" UNTIL 2026-09-19 13:05, AND THE LEAD RULED THE OTHER
WAY.** The argument that changed it: a deleted test leaves no record that the
transition happened, an inverted one keeps asserting something true, and its
diff is the clearest possible statement of what flipped. `a603a61`
(`tests/test_search_admission_blast_radius.py`) said so first and was adopted;
this file is brought into line rather than left contradicting it, because two
guards giving opposite instructions is worse than either instruction.

Until that rewrite happens this file is the executable statement that the
boundary refuses the surface -- which is what makes the one-line removal of
the pattern a PROVEN rollback rather than an assumed one.

**AND IT ALSO SAYS WHY THE REVERT IS ONE LINE.**
`test_the_refusal_is_the_allowlist_and_not_the_denylist` measures which of the
two gates does the refusing. It is the allowlist, on every spelling: no entry
in `readonly._FORBIDDEN_URL_SUBSTRINGS` names any of these addresses. So
removing the pattern restores the refusal completely, with no denylist surgery
to undo -- and if that ever stops being true, this test says so before the
rollback is attempted rather than during it.

NO URL BELOW NAMES A PERSON. They are LinkedIn's own product addresses with a
one-character placeholder keyword.
"""

from __future__ import annotations

import re

from linkedin_server import readonly

# ---------------------------------------------------------------------------
# 1. The addresses the 20 rows need
# ---------------------------------------------------------------------------

#: `SEARCH-RESULTS-SURFACE` carries 21 census rows, 20 of them reads, and not
#: one has an admitted address. These are the spellings those rows need,
#: recorded in `_audit/2026-09-05-search-results-consent.md` section 4 and
#: `_audit/2026-09-05-search-results-measured.md` section 1.
_SEARCH_RESULTS_URLS: tuple[str, ...] = (
    "https://www.linkedin.com/search/results/people/",
    "https://www.linkedin.com/search/results/people/?keywords=x",
    (
        "https://www.linkedin.com/search/results/people/?keywords=x"
        "&network=%5B%22F%22%5D&geoUrn=%5B%22000%22%5D"
    ),
    "https://www.linkedin.com/search/results/all/?keywords=x",
    "https://www.linkedin.com/search/results/companies/?keywords=x",
    "https://www.linkedin.com/search/results/groups/?keywords=x",
    "https://www.linkedin.com/search/results/events/?keywords=x",
    "https://www.linkedin.com/search/results/content/?keywords=%23hiring",
)

#: The candidate the pre-admission wave measured. Carried here ONLY so the
#: monkeypatched test below can show the refusal above is one pattern away
#: from lifting. It is NOT installed on disk by this file or any other.
_CANDIDATE_NARROW = (
    r"^https://www\.linkedin\.com/search/results/people/?(\?[^#]*)?$"
)

#: The shape condition 2 forbids, carried for the same reason: to show, rather
#: than to argue, what a family wildcard reaches that the narrow one does not.
_CANDIDATE_FAMILY_WILDCARD = r"^https://www\.linkedin\.com/search/.*$"

#: A string whose NORMALISED form is an account-ending address. A browser
#: resolves `..` before it issues a request; `assert_read_url` matches the
#: string it was handed. So a family wildcard admits this and the address it
#: really reaches is named by no forbidden substring at all.
_TRAVERSAL_ONTO_ACCOUNT_ENDING = (
    "https://www.linkedin.com/search/results/people/../../"
    "mypreferences/d/close-account"
)

#: A known-admitted read. The control that proves the detector below can say
#: "admitted" and is not hardwired to say "refused".
_KNOWN_ADMITTED_URL = "https://www.linkedin.com/in/me/"


def _refused(url: str) -> bool:
    """True if the shipped predicate refuses ``url`` as a read.

    One detector, proven honest once, rather than every assertion in this file
    trusting itself to call `is_read_url` correctly. Wraps the shipped
    predicate and reimplements no url matching.
    """
    return readonly.is_read_url(url) is False


# ---------------------------------------------------------------------------
# 2. THE REVERT ASSERTION -- green today, red the moment the pattern lands
# ---------------------------------------------------------------------------


def test_every_search_results_address_is_refused_today():
    """GREEN TODAY BECAUSE NOTHING IS ADMITTED. RED WHEN THE PATTERN LANDS.

    The admitting wave REWRITES AND INVERTS this file in the commit that adds
    the pattern. See this module's docstring: that diff is the rollback being
    spent deliberately and visibly, which is the whole value of writing it
    first.
    """
    for url in _SEARCH_RESULTS_URLS:
        assert _refused(url), (
            f"search-results address admitted as a read: {url!r}. If the "
            "admission ruled at 09f9961 section 6 has landed, this file has "
            "done its job and should be REWRITTEN AND INVERTED in that same "
            "commit -- the admitted entries flipped to assert admission, the "
            "rest still asserting refusal. Not deleted, not narrowed, not "
            "silenced, not xfailed."
        )


# ---------------------------------------------------------------------------
# 3. WHICH GATE REFUSES -- the reason the revert is one line
# ---------------------------------------------------------------------------


def test_the_refusal_is_the_allowlist_and_not_the_denylist():
    """No forbidden substring names any of these addresses.

    MEASURED, not assumed. If the refusal came from the denylist, removing an
    allowlist pattern would not restore it and the rollback would be two
    edits in two places. It does not: every address above is refused purely
    because no pattern admits it, exactly as account deletion is.
    """
    for url in _SEARCH_RESULTS_URLS:
        lowered = url.lower()
        biting = [s for s in readonly._FORBIDDEN_URL_SUBSTRINGS if s in lowered]
        assert not biting, (
            f"{url!r} is refused partly by the denylist ({biting!r}), so "
            "removing an allowlist pattern would NOT be the whole revert. "
            "The rollback for this surface needs re-costing before it is "
            "attempted."
        )
        assert not any(p.match(url) for p in readonly._ALLOWED_URL_PATTERNS), (
            f"{url!r} matches an allowlist pattern, which contradicts the "
            "test above and means the two are reading different state"
        )


# ---------------------------------------------------------------------------
# 4. THE LOAD-BEARING TEST -- the refusal is exactly one pattern away
# ---------------------------------------------------------------------------


def test_one_narrow_pattern_is_all_that_stands_between(monkeypatch):
    """PASSES TODAY, and that is the point.

    It proves the refusal in section 2 is the absence of one line rather than
    a defended boundary, and it proves the revert direction too: take the
    pattern away and the address refuses again, in the same process.

    `monkeypatch` restores the original tuple when the test ends, so no test
    running after this one inherits a widened boundary.
    """
    target = _SEARCH_RESULTS_URLS[1]
    assert _refused(target), "precondition: the address refuses before we widen"

    original = readonly._ALLOWED_URL_PATTERNS
    monkeypatch.setattr(
        readonly,
        "_ALLOWED_URL_PATTERNS",
        original + (re.compile(_CANDIDATE_NARROW),),
    )
    assert not _refused(target), (
        f"expected the narrow candidate to admit {target!r}. If this fails, "
        "either the candidate no longer matches LinkedIn's spelling or the "
        "denylist has grown an entry that bites it -- and in the second case "
        "the revert is no longer one line. Re-measure before rewriting this."
    )

    monkeypatch.setattr(readonly, "_ALLOWED_URL_PATTERNS", original)
    assert _refused(target), (
        "removing the pattern did NOT restore the refusal -- the rollback "
        "this file exists to prove does not work"
    )


# ---------------------------------------------------------------------------
# 5. WHY CONDITION 2 SAYS "NEVER A /search/ FAMILY WILDCARD"
# ---------------------------------------------------------------------------


def test_a_family_wildcard_admits_a_traversal_the_narrow_one_refuses(
    monkeypatch,
):
    """SHOWN, not argued: the guard failing on what it must still refuse.

    A `/search/` family wildcard admits a string whose normalised form is an
    account-ending address that NO forbidden substring names. The narrow
    candidate refuses the same string, because its path segment is a closed
    spelling rather than an open one.
    """
    assert _refused(_TRAVERSAL_ONTO_ACCOUNT_ENDING), (
        "precondition: the traversal spelling refuses at HEAD"
    )
    lowered = _TRAVERSAL_ONTO_ACCOUNT_ENDING.lower()
    assert not any(s in lowered for s in readonly._FORBIDDEN_URL_SUBSTRINGS), (
        "the traversal spelling is named by a forbidden substring, so it is "
        "not an example of an address defended by nothing -- this test's "
        "premise has changed and the denylist should be re-read"
    )

    original = readonly._ALLOWED_URL_PATTERNS

    monkeypatch.setattr(
        readonly,
        "_ALLOWED_URL_PATTERNS",
        original + (re.compile(_CANDIDATE_FAMILY_WILDCARD),),
    )
    assert not _refused(_TRAVERSAL_ONTO_ACCOUNT_ENDING), (
        "expected the family wildcard to admit the traversal spelling -- "
        "that admission IS the hazard condition 2 exists to forbid. If this "
        "now fails the hazard may have been closed some other way, and this "
        "test's premise needs re-checking before the test is deleted."
    )

    monkeypatch.setattr(
        readonly,
        "_ALLOWED_URL_PATTERNS",
        original + (re.compile(_CANDIDATE_NARROW),),
    )
    assert _refused(_TRAVERSAL_ONTO_ACCOUNT_ENDING), (
        "the NARROW candidate admitted a traversal spelling. It is supposed "
        "to be a closed path segment; if it admits this, the candidate is "
        "wrong and must not be landed."
    )


# ---------------------------------------------------------------------------
# 6. The detector can report admission, not only refusal
# ---------------------------------------------------------------------------


def test_the_detector_can_report_admission():
    """Without this, every refusal above could pass because `_refused`
    always answers "refused" regardless of its argument.
    """
    assert not _refused(_KNOWN_ADMITTED_URL), (
        f"{_KNOWN_ADMITTED_URL!r} is a known-admitted read but `_refused` "
        "called it refused -- the detector cannot tell admission from "
        "refusal, which makes every assertion in this file unproven"
    )
