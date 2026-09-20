"""THE REVERT PATH FOR THE SEARCH-RESULTS ADMISSION. **THE PATTERN HAS LANDED.**

**INVERTED 2026-09-20, WHICH IS THIS FILE DOING ITS JOB.** It was committed
green while nothing was admitted, went red the moment the pattern landed, and
is rewritten here in that same commit -- entries the pattern now admits assert
ADMISSION, everything it must still refuse goes on asserting refusal. Not
deleted, not narrowed, not silenced, not xfailed. **The diff against the
previous revision is the clearest available statement of exactly what flipped,
and that is why the lead ruled invert over delete on 2026-09-19 13:05.**

WHAT LANDED, so this file records it rather than pointing elsewhere: the S1
candidate `^https://www\\.linkedin\\.com/search/results/people/?(\\?[^#]*)?$`,
the PEOPLE vertical only, with its shaper (`linkedin_server/search_results.py`)
and its tool (`linkedin_people_search_shape`) in the same commit, which is
condition 1. The other five verticals below were NOT admitted and are now the
durable half of this file.

**WHY ONLY PEOPLE, WHEN FOUR MORE ADDRESSES SIT BELOW.** 16 of the blocker's
20 reads are the people vertical. The three-vertical alternation would have
served 19 and admitted two more third-party-dense pages; it was refused
because this is the precedent-setting admission on the platform's densest
third-party surface and the ruling's own reopening clause gives widening a
named route -- *"a later wave showing the narrow pattern is TOO NARROW to
serve the 20 rows, which is a request to widen it and gets its own blast
radius"*. Groups, events and content should take that route.

Condition 4 of the ruling at `09f9961` section 6: *"A REVERT PATH EXISTS BEFORE
THE ADMISSION, NOT AFTER. The pattern's removal is one line; the test that
shows the address refused must be written and shown failing BEFORE the pattern
is added, so the rollback is proven rather than assumed."*

**THE INSTRUCTION THIS FILE CARRIED, now discharged.** It said: rewrite and
invert, in the same commit that adds the pattern; do not silence, narrow or
xfail. It said "DELETE IT" until 2026-09-19 13:05 and the lead ruled the other
way, on the argument that a deleted test leaves no record that the transition
happened while an inverted one keeps asserting something true. `a603a61`
(`tests/test_search_admission_blast_radius.py`) said so first and was adopted.
**Both guards were brought into line, and both were followed here.**

**A STALE INSTRUCTION SURVIVED ELSEWHERE AND IS NOW DECLARED CORRECTED.**
`_audit/2026-09-19-search-admission-preconditions.md` section C and section
D.3 told the admitting wave to DELETE this file -- that document was written
at 12:46, before the 13:05 ruling, and nobody went back to it.

The 2026-09-20 wave first recorded that only here, reasoning that another
wave's audit doc should not be edited. **`test_a_correction_is_findable_from
_the_claim` went red on exactly that**, and it was right: a correction the
corrected document cannot name is unreachable from the claim, so a reader who
starts at the stale instruction never learns it was superseded. The pair is
declared -- `CORRECTS:` in `_audit/2026-09-20-the-search-admission.md` and
`CORRECTED BY:` at the head of that document's section C.

The one-line removal of the pattern is still what reverts the surface, and
section 4 below now proves that in the live direction rather than the
hypothetical one.

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

import pathlib
import re

from linkedin_server import readonly

# ---------------------------------------------------------------------------
# 1. The addresses the 20 rows need
# ---------------------------------------------------------------------------

#: `SEARCH-RESULTS-SURFACE` carries 21 census rows, 20 of them reads. These
#: are the spellings those rows need, recorded in
#: `_audit/2026-09-05-search-results-consent.md` section 4 and
#: `_audit/2026-09-05-search-results-measured.md` section 1.
#:
#: **THE SPLIT BELOW IS THE ADMISSION.** It is kept as two named tuples rather
#: than one list plus a filter, because which side an address is on is a
#: RULING and not a computation -- deriving it from the live allowlist would
#: make this file agree with whatever the boundary currently says, which is
#: the one thing a guard may never do.
_ADMITTED_NOW: tuple[str, ...] = (
    "https://www.linkedin.com/search/results/people/",
    "https://www.linkedin.com/search/results/people/?keywords=x",
    (
        "https://www.linkedin.com/search/results/people/?keywords=x"
        "&network=%5B%22F%22%5D&geoUrn=%5B%22000%22%5D"
    ),
)

#: **THE DURABLE HALF.** Five verticals the admission did NOT buy. Each is its
#: own third-party-dense surface and each needs its own blast radius, so a
#: green run here is the statement that the admission stayed the size it was
#: ruled at.
_STILL_REFUSED: tuple[str, ...] = (
    "https://www.linkedin.com/search/results/all/?keywords=x",
    "https://www.linkedin.com/search/results/companies/?keywords=x",
    "https://www.linkedin.com/search/results/groups/?keywords=x",
    "https://www.linkedin.com/search/results/events/?keywords=x",
    "https://www.linkedin.com/search/results/content/?keywords=%23hiring",
)

#: Every spelling the rows named, on both sides of the line. Used where a
#: claim is about the SURFACE rather than about one side of it.
_SEARCH_RESULTS_URLS: tuple[str, ...] = _ADMITTED_NOW + _STILL_REFUSED

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


def test_the_people_vertical_is_now_admitted():
    """THE INVERTED HALF. These three asserted refusal until 2026-09-20.

    They are the address the 16 people rows need, and they are admitted
    together with the shaper and the tool -- condition 1 of the ruling, which
    says an admission that defers the shaper has VIOLATED it rather than
    partially satisfied it.
    """
    for url in _ADMITTED_NOW:
        assert not _refused(url), (
            f"the people-search address is refused again: {url!r}. Either the "
            "admission was reverted -- in which case this file is inverted "
            "BACK, in that same commit, and the shaper's tool goes with it -- "
            "or the pattern was edited and no longer matches LinkedIn's "
            "spelling."
        )


def test_the_other_five_verticals_are_still_refused():
    """THE DURABLE HALF, and it is what makes the admission narrow rather than
    a family.

    Every one of these is a search-results page too, and every one stays shut.
    If one of them opens without its own blast radius and its own ruling, the
    admission grew by accident -- which is exactly what condition 2 forbids.
    """
    for url in _STILL_REFUSED:
        assert _refused(url), (
            f"a vertical nobody admitted became readable: {url!r}. The "
            "2026-09-20 admission was the PEOPLE vertical only. Widening is "
            "allowed by the ruling's reopening clause and it costs a fresh "
            "blast radius -- it is not something a pattern edit does quietly."
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

    # AND THE TWO SIDES REALLY ARE DECIDED BY THE ALLOWLIST, each in its own
    # direction. Asserting only the refusals would let the admitted three be
    # admitted by something nobody looked at.
    for url in _STILL_REFUSED:
        assert not any(p.match(url) for p in readonly._ALLOWED_URL_PATTERNS), (
            f"{url!r} matches an allowlist pattern, which contradicts "
            "test_the_other_five_verticals_are_still_refused and means the "
            "two are reading different state"
        )
    for url in _ADMITTED_NOW:
        matching = [p for p in readonly._ALLOWED_URL_PATTERNS if p.match(url)]
        assert len(matching) == 1, (
            f"{url!r} is admitted by {len(matching)} patterns, not one. The "
            "revert is 'remove one line' only while exactly one line admits "
            "it; two would make the rollback silently incomplete."
        )


# ---------------------------------------------------------------------------
# 4. THE LOAD-BEARING TEST -- the refusal is exactly one pattern away
# ---------------------------------------------------------------------------


def test_removing_the_one_shipped_pattern_reverts_the_whole_surface(monkeypatch):
    """THE ROLLBACK, NOW RUN IN THE LIVE DIRECTION.

    Before the admission this test installed a candidate and showed it
    admitted; the rollback it proved was the hypothetical half. **It now takes
    the SHIPPED pattern out of the live tuple and shows every admitted address
    refusing again** -- which is the direction an actual revert would travel,
    and the one that was previously impossible to run.

    `monkeypatch` restores the tuple when the test ends, so nothing after this
    inherits a narrowed boundary.
    """
    original = readonly._ALLOWED_URL_PATTERNS
    for url in _ADMITTED_NOW:
        assert not _refused(url), "precondition: the surface is admitted"

    survivors = tuple(
        pattern for pattern in original
        if not any(pattern.match(url) for url in _ADMITTED_NOW)
    )
    assert len(survivors) == len(original) - 1, (
        f"removing what admits the people search took "
        f"{len(original) - len(survivors)} patterns out, not one. The revert "
        "is only 'delete one line' while exactly one line does the admitting."
    )

    monkeypatch.setattr(readonly, "_ALLOWED_URL_PATTERNS", survivors)
    for url in _ADMITTED_NOW:
        assert _refused(url), (
            f"removing the one admitting pattern did NOT restore the refusal "
            f"of {url!r} -- something else now admits it and the rollback "
            "this file exists to prove does not work."
        )

    monkeypatch.setattr(readonly, "_ALLOWED_URL_PATTERNS", original)
    for url in _ADMITTED_NOW:
        assert not _refused(url), "restoring the tuple did not restore the read"


def test_the_pattern_admits_the_spellings_LINKEDIN_ITSELF_EMITS():
    """THE ONLY REAL-LINKEDIN EVIDENCE AVAILABLE FOR THIS SURFACE OFFLINE.

    No capture of a `/search/` PAGE exists in this repository. But LinkedIn
    links TO the people search from pages that WERE captured -- the
    profile-views analytics page draws "search for who viewed you"
    call-to-action links, and a job detail page carries a canned search -- so
    those fixtures contain search URLs **that LinkedIn wrote**, not ones this
    repository guessed.

    Measured 2026-09-20: seven distinct spellings across three captures, and
    the shipped pattern admits all seven. They carry `keywords`, `origin`,
    `currentCompany` and `pastCompany` parameters in varying order and with
    one of them lacking `keywords` entirely.

    **WHAT THIS DOES AND DOES NOT ESTABLISH.** It establishes that the
    admitted ADDRESS SHAPE is the one the platform really uses, which no
    amount of reasoning about the regex could. It establishes NOTHING about
    whether the shaper reads the resulting page correctly -- that needs a
    capture of the page itself and a browser slot.

    The hrefs are read from the fixtures at run time and never written down
    here: they carry real query values, and a test that embedded them would
    put into a tracked file exactly what this surface's whole discipline
    exists to keep out.
    """
    hrefs: set[str] = set()
    for name in (
        "profile_views_analytics.html",
        "profile_views_analytics_hydrated.html",
        "job_detail_following_hydrated.html",
    ):
        path = pathlib.Path(__file__).resolve().parent / "fixtures" / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        hrefs |= set(re.findall(r'href="([^"]*search/results/people/[^"]*)"', text))

    assert hrefs, (
        "no LinkedIn-authored people-search href was found in any capture. "
        "Either the fixtures moved or this test is now vacuous -- and a "
        "vacuous version of THIS test would silently stop being the only "
        "real-platform evidence the admission has."
    )

    refused = []
    for href in hrefs:
        url = href if href.startswith("http") else "https://www.linkedin.com" + href
        # A captured href is HTML-escaped; a browser sends the unescaped form.
        # BOTH must be admitted or the pattern is right about a spelling
        # nothing actually uses.
        for spelling in (url, url.replace("&amp;", "&")):
            if _refused(spelling):
                refused.append(re.sub(r"=[^&]*", "=<value>", spelling))

    assert not refused, (
        "the admission refuses a people-search address LinkedIn itself "
        "emits, so the pattern is narrower than the platform: "
        + "; ".join(sorted(set(refused)))
    )


def test_the_narrow_candidate_on_record_is_the_one_that_shipped(monkeypatch):
    """THE MEASURED CANDIDATE AND THE SHIPPED LINE ARE THE SAME STRING.

    `_CANDIDATE_NARROW` is what the pre-admission wave ran its blast radius
    on. If the line that actually landed had drifted from it by one character,
    every number in
    `_audit/2026-09-19-search-admission-preconditions.md` would describe
    something other than the boundary this repository ships -- a measurement
    correctly taken of the wrong artifact, which is this repo's most expensive
    recurring defect.
    """
    shipped = [
        pattern.pattern for pattern in readonly._ALLOWED_URL_PATTERNS
        if pattern.match(_ADMITTED_NOW[0])
    ]
    assert shipped == [_CANDIDATE_NARROW], (
        "the pattern on disk is not the candidate that was measured:\n"
        f"  measured: {_CANDIDATE_NARROW!r}\n"
        f"  shipped : {shipped!r}"
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
