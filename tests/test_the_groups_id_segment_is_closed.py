"""THE GROUPS DEEP-PATH ADMISSION, AND THE CONTROL THAT FAILS IF IT WIDENS.

``/groups/<id>/`` and ``/groups/discover/`` were admitted 2026-09-19 on the
team lead's ruling. The whole safety argument is ONE SENTENCE -- **a group id
is NUMERIC, so the address names nobody** -- and that sentence is only true
while the id segment stays a closed run of the ten ASCII digits.

**This file is condition 2 of that ruling**, which does not ask for a test that
the pattern works. It asks for *"a control that goes red if the segment class
ever widens to admit letters. Without it the digits-only claim is untested and
one edit from being false."*

## WHY A LIST OF REFUSED URLS IS NOT ENOUGH ON ITS OWN

A guard made of ``is_read_url(...) is False`` assertions passes just as happily
when the predicate has stopped admitting anything at all, and it says nothing
about WHY a url was refused. Two things are therefore asserted beyond the list:

1. **THE BOUNDARY AND THE SHAPER AGREE ON THE SEGMENT CLASS.** ``groups.py``
   decides what may be SAID about a group and refuses a non-numeric segment
   *because a slug is a name*. ``readonly.py`` decides what may be OPENED.
   Those are different modules with different authors, and nothing but this
   test makes them answer the same question the same way.
   ``test_the_two_gates_agree`` drives both over one set of segments -- so a
   widening of EITHER, in either direction, goes red here.

2. **THE CONTROL IS SHOWN FAILING**, in-file and on every run, by installing
   the three patterns somebody would plausibly write instead and measuring
   that the refusals above collapse under them. A check that cannot fail
   certifies nothing, and this repository has already shipped four of those.

## THE NON-ASCII DIGITS ARE NOT A CURIOSITY

The ruling was written as ``/groups/[backslash]d+/?$`` and the entry
deliberately ships ``[0-9]``. Python's ``[backslash]d`` matches any Unicode
decimal digit, so the ruling as literally written admits four further
spellings of an id -- and ``groups.py`` REFUSES all four, because it names the
ten characters rather than calling ``str.isdigit()``. That gap is a boundary
disagreeing with its own shaper, and ``test_the_two_gates_agree`` is what
keeps it closed.

Every non-ASCII digit below is spelled as a unicode escape in the SOURCE, so
this file stays strict ASCII on disk while the VALUE under test is the real
character. ``test_the_digit_spellings_are_really_non_ascii`` asserts that,
because an escape that silently became a literal would make this file quietly
stop testing what it says it tests.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import groups, readonly  # noqa: E402

BASE = "https://www.linkedin.com"

#: A group id shape. Eight ASCII digits, invented, naming nothing.
ID = "12345678"

#: The four non-ASCII digit runs, spelled as escapes. Named rather than
#: inlined so the two collections below cannot drift apart.
ARABIC_INDIC = "\u0661\u0662\u0663"
EXT_ARABIC_INDIC = "\u06f1\u06f2\u06f3"
DEVANAGARI = "\u0967\u0968\u0969"
FULLWIDTH = "\uff11\uff12\uff13"

NON_ASCII_DIGIT_RUNS = {
    "digits-arabic-indic": ARABIC_INDIC,
    "digits-ext-arabic-indic": EXT_ARABIC_INDIC,
    "digits-devanagari": DEVANAGARI,
    "digits-fullwidth": FULLWIDTH,
}

#: What the ruling bought. These are the ONLY addresses either pattern is
#: allowed to newly admit, and the blast radius measured exactly that.
ADMITTED = (
    f"{BASE}/groups/{ID}",
    f"{BASE}/groups/{ID}/",
    f"{BASE}/groups/discover",
    f"{BASE}/groups/discover/",
)

#: THE DURABLE HALF. Every one of these was refused before the admission and
#: must be refused after it. Slugs use SANCTIONED SYNTHETIC TOKENS -- these are
#: invented strings, and no group anybody belongs to is named here.
MUST_STAY_REFUSED = {
    # ---------------------------------------------------------------- slugs
    # THE CLASS CONDITION 2 EXISTS FOR. A slug is a name: a group named after
    # a person carries that person's name here. If any of these goes True the
    # segment class has widened to admit letters and the admission's entire
    # justification is false.
    "slug-plain": f"{BASE}/groups/example-group/",
    "slug-personal": f"{BASE}/groups/somebody-and-friends/",
    "slug-test-token": f"{BASE}/groups/test-group-12345/",
    # DIGITS ARE NOT ENOUGH ON THEIR OWN -- a segment that merely CONTAINS a
    # numeric run is not a numeric segment, and these two are the spellings an
    # unanchored digit class would let through.
    "slug-digits-first": f"{BASE}/groups/{ID}-placeholder/",
    "slug-digits-last": f"{BASE}/groups/placeholder-{ID}/",
    # A urn is the other name-bearing shape an id-looking segment can wear.
    "urn": f"{BASE}/groups/urn:li:group:{ID}/",
    # ------------------------------------------------------- the deep paths
    # THE MEMBER ROSTER, census row N 165, put out of scope BY NAME. It is a
    # list of people who did not choose to be enumerated by him. It carries no
    # forbidden substring, so the ONLY thing refusing it is the anchor on the
    # pattern beside it -- which is exactly why it is pinned here.
    "roster": f"{BASE}/groups/{ID}/members/",
    "requests-queue": f"{BASE}/groups/{ID}/requests/",
    "about": f"{BASE}/groups/{ID}/about/",
    "manage": f"{BASE}/groups/{ID}/manage/",
    # Refused TWICE, and the second gate is not this pattern's doing.
    "invite": f"{BASE}/groups/{ID}/invite/",
    # Group search belongs to SEARCH-RESULTS-SURFACE and is not this
    # admission's to inherit.
    "search-groups": f"{BASE}/search/results/groups/?keywords=x",
    "mynetwork-groups": f"{BASE}/mynetwork/groups/",
    # ----------------------------------------------------------- the query
    # Neither pattern takes one. Nothing builds a query on these addresses, so
    # nothing needs preserving, and a pattern that accepts a query accepts
    # whatever a caller appends to it.
    "query-on-id": f"{BASE}/groups/{ID}/?highlightedUpdateUrn=x",
    "query-on-discover": f"{BASE}/groups/discover/?origin=x",
    # ------------------------------------------------------- the traversals
    # A PATH THAT NORMALISES SOMEWHERE ELSE. Measured on a sibling surface the
    # same day: a pattern anchored at both ends around a wildcard admitted 18
    # addresses, identical to the bare wildcard, and a traversal normalising
    # onto an account-ending address walked straight through it. A closed
    # segment plus the trailing anchor is what makes these unreachable.
    "traversal-close-account": (
        f"{BASE}/groups/{ID}/../../mypreferences/d/close-account"
    ),
    "traversal-hibernate": (
        f"{BASE}/groups/{ID}/../../mypreferences/d/hibernate-account"
    ),
    "traversal-account-mgmt": (
        f"{BASE}/groups/{ID}/../../psettings/account-management"
    ),
    "traversal-public-profile": (
        f"{BASE}/groups/{ID}/../../public-profile/settings"
    ),
    "traversal-legacy-auth": f"{BASE}/groups/{ID}/../../uas/login",
    "traversal-mobile-mirror": f"{BASE}/groups/{ID}/../../mwlite/settings",
    # A THIRD PARTY REACHED FROM THE GROUP FAMILY. Loading a member's profile
    # leaves them a durable record in their own "who viewed your profile"
    # list, which is why no pattern may reach one however it is spelled.
    "traversal-member": f"{BASE}/groups/{ID}/../in/someone-else/",
    "traversal-bare": f"{BASE}/groups/{ID}/..",
    # ------------------------------------------------- the non-ASCII digits
    # THE RULING AS LITERALLY WRITTEN ADMITS THESE FOUR AND THE SHIPPED ENTRY
    # DOES NOT. Not because a person's name can be spelled in Devanagari
    # digits, but because the admission's claim is about a charset of TEN
    # characters, and a pattern matching a materially wider one has made that
    # claim false. ``groups.py`` refuses all four; the boundary must agree.
    "digits-arabic-indic": f"{BASE}/groups/{ARABIC_INDIC}/",
    "digits-ext-arabic-indic": f"{BASE}/groups/{EXT_ARABIC_INDIC}/",
    "digits-devanagari": f"{BASE}/groups/{DEVANAGARI}/",
    "digits-fullwidth": f"{BASE}/groups/{FULLWIDTH}/",
}

#: Segments driven through BOTH gates. The value is what each gate must say.
#: A segment is admissible exactly when it is a bounded run of ASCII digits.
SEGMENTS = {
    ID: True,
    "1": True,
    "0": True,
    "9" * 20: True,
    # Bounded above -- ``groups.py`` caps the identifier at twenty digits, so
    # a longer run is refused there and must be refused here too.
    "9" * 21: False,
    "example-group": False,
    "somebody-and-friends": False,
    "test-group-12345": False,
    f"{ID}-placeholder": False,
    f"placeholder-{ID}": False,
    "": False,
    # ``discover`` IS DELIBERATELY NOT IN THIS SET, and the omission is the
    # interesting part. It is the one segment the two gates are SUPPOSED to
    # disagree about: the boundary opens it by a second, named-page pattern,
    # and the shaper refuses it because it is not an identifier. Leaving it
    # here made this test red for the wrong reason on its first run.
    # ``test_discover_is_opened_as_a_name_not_as_an_identifier`` asserts that
    # asymmetry directly instead, so it is recorded rather than hidden.
    ARABIC_INDIC: False,
    EXT_ARABIC_INDIC: False,
    DEVANAGARI: False,
    FULLWIDTH: False,
}

#: THE PATTERNS SOMEBODY WOULD PLAUSIBLY WRITE INSTEAD, each one wider than
#: what shipped. They are installed only inside the can-it-fail control, and
#: the control asserts the guard above COLLAPSES under each.
WIDER_THAN_SHIPPED = {
    # The ruling's own literal text. Wider by four digit scripts.
    "unicode-digits": r"^https://www\.linkedin\.com/groups/\d+/?$",
    # The obvious "one segment" spelling, and the one condition 1 names: a
    # character class that admits letters is a different ruling.
    "any-segment": r"^https://www\.linkedin\.com/groups/[^/]+/?$",
    # Anchored at both ends and still a family.
    "anchored-wildcard": r"^https://www\.linkedin\.com/groups/.*$",
}


@pytest.mark.parametrize("name", sorted(MUST_STAY_REFUSED))
def test_the_admission_must_never_reach_these(name: str) -> None:
    """THE GUARD. Unchanged by the admission, and red if it ever widens."""
    url = MUST_STAY_REFUSED[name]
    assert readonly.is_read_url(url) is False, (
        f"{name} became READABLE. The groups admission is a closed numeric "
        "segment on an anchored pattern; anything that reaches this address "
        "is a different ruling than the one that was made."
    )


@pytest.mark.parametrize("url", ADMITTED)
def test_the_addresses_the_ruling_bought(url: str) -> None:
    """The admission itself, and the half that keeps the guard honest.

    A file of all-False assertions passes when the predicate has stopped
    admitting anything. These four are the same predicate answering True.
    """
    assert readonly.is_read_url(url) is True


@pytest.mark.parametrize("segment", sorted(SEGMENTS))
def test_the_two_gates_agree(segment: str) -> None:
    """THE COUPLING, AND THE MOST IMPORTANT ASSERTION IN THIS FILE.

    ``readonly.py`` decides what may be OPENED; ``groups.py`` decides what may
    be SAID. Different modules, different authors, and the admission's safety
    argument QUOTES THE SECOND TO JUSTIFY THE FIRST -- a group id is numeric,
    so the address names nobody.

    That borrowed argument is only sound while the two agree about which
    segments are numeric. Nothing else in this repository makes them, and they
    already disagreed once: a Unicode digit class admits four digit scripts
    that ``group_identifier`` refuses as ``identifier_is_not_numeric``.

    So this drives one set of segments through both and asserts they answer
    the same. A widening of EITHER module, in EITHER direction, is red here.
    """
    expected = SEGMENTS[segment]

    opened = readonly.is_read_url(f"{BASE}/groups/{segment}/")
    said = groups.group_identifier(f"/groups/{segment}/")["identified"]

    assert opened is expected, (
        f"the BOUNDARY changed its mind about {segment!r}: expected "
        f"{expected}, got {opened}"
    )
    assert said is expected, (
        f"the SHAPER changed its mind about {segment!r}: expected "
        f"{expected}, got {said}"
    )
    assert opened is said, (
        f"THE TWO GATES DISAGREE about {segment!r}. The admission's whole "
        "justification is that a numeric segment names nobody, and it borrows "
        "'numeric' from groups.py. If the boundary opens what the shaper "
        "refuses to name, that argument no longer covers the address."
    )


@pytest.mark.parametrize("wider", sorted(WIDER_THAN_SHIPPED))
def test_the_control_is_shown_failing_under_a_wider_segment(wider: str) -> None:
    """SHOWN FAILING, on every run, against the three plausible widenings.

    **A CHECK THAT CANNOT FAIL CERTIFIES NOTHING**, and a refusal list is the
    easiest kind to write that way. This installs a wider pattern onto the
    real tuple, measures which of ``MUST_STAY_REFUSED`` go readable, and
    asserts that at least one does -- so the guard above is demonstrated to be
    load bearing rather than assumed to be.

    The tuple is restored in a ``finally``, so a failure mid-measurement
    cannot leave a widened boundary behind in the process.
    """
    original = readonly._ALLOWED_URL_PATTERNS
    try:
        readonly._ALLOWED_URL_PATTERNS = original + (
            re.compile(WIDER_THAN_SHIPPED[wider]),
        )
        breached = sorted(
            name
            for name, url in MUST_STAY_REFUSED.items()
            if readonly.is_read_url(url)
        )
    finally:
        readonly._ALLOWED_URL_PATTERNS = original

    assert breached, (
        f"{wider} breached NOTHING in MUST_STAY_REFUSED. That does not mean "
        "the widening is safe -- it means this guard has stopped covering the "
        "class it was written for, and the next real widening will pass it."
    )

    # AND THE BOUNDARY IS BACK. A control that widens the shipped tuple has to
    # prove it put it back, or it is the most dangerous test in the file.
    assert readonly._ALLOWED_URL_PATTERNS is original
    assert readonly.is_read_url(MUST_STAY_REFUSED["roster"]) is False


def test_discover_is_opened_as_a_name_not_as_an_identifier() -> None:
    """THE ONE PLACE THE TWO GATES ARE MEANT TO DISAGREE, pinned as intended.

    ``test_the_two_gates_agree`` asserts the boundary and the shaper answer
    the same for every group segment. ``discover`` is the exception: it is a
    LITERAL PAGE NAME admitted by its own pattern, not an identifier, and
    ``group_identifier`` refuses it exactly as it refuses any other
    non-numeric segment.

    That asymmetry is correct and it is also the shape of thing that gets
    quietly "fixed" by somebody widening the identifier class to make a red
    test pass. Asserting it here means the next person meets a sentence
    instead of a puzzle.
    """
    assert readonly.is_read_url(f"{BASE}/groups/discover/") is True
    assert (
        groups.group_identifier("/groups/discover/")["identified"] is False
    ), (
        "the shaper now treats 'discover' as a group identifier. It is a page "
        "name; if this passes, the identifier class has widened to admit "
        "letters and the admission's justification is false."
    )
    # AND IT BUYS NOTHING BELOW ITSELF. The named page is a leaf.
    assert readonly.is_read_url(f"{BASE}/groups/discover/anything/") is False


def test_the_letter_admitting_widenings_reach_a_slug() -> None:
    """The control, aimed at the class condition 2 actually names.

    ``test_the_control_is_shown_failing_under_a_wider_segment`` proves each
    widening breaches SOMETHING. That is necessary and it is not the claim:
    the ruling's words are *"goes red if the segment class ever widens to
    admit letters"*, so the two widenings that admit letters are shown
    reaching a SLUG specifically -- the shape that carries a name.

    The Unicode-digit widening is deliberately NOT asserted here. It admits no
    slug, which is exactly why it is the plausible mistake, and it is caught
    by ``test_the_two_gates_agree`` instead.
    """
    slugs = [k for k in MUST_STAY_REFUSED if k.startswith("slug-")]
    original = readonly._ALLOWED_URL_PATTERNS
    for wider in ("any-segment", "anchored-wildcard"):
        try:
            readonly._ALLOWED_URL_PATTERNS = original + (
                re.compile(WIDER_THAN_SHIPPED[wider]),
            )
            reached = [s for s in slugs if readonly.is_read_url(MUST_STAY_REFUSED[s])]
        finally:
            readonly._ALLOWED_URL_PATTERNS = original
        assert reached, (
            f"{wider} admits letters and yet reached no slug in this file. "
            "The slug corpus has stopped representing the class the ruling "
            "was protecting."
        )


def test_the_digit_spellings_are_really_non_ascii() -> None:
    """The file's own claim about itself, asserted rather than trusted.

    The docstring says the non-ASCII digits are spelled as escapes in the
    source so the file stays ASCII while the values stay real. If somebody
    normalises this file and turns the escapes into literals, or turns the
    values into plain ASCII digits, the tests above keep passing while testing
    nothing. Both halves are checked.
    """
    source = Path(__file__).read_bytes()
    assert all(byte < 128 for byte in source), (
        "this file is no longer strict ASCII on disk"
    )
    for name, run in NON_ASCII_DIGIT_RUNS.items():
        assert any(ord(ch) > 127 for ch in run), (
            f"{name} is now plain ASCII -- the widening it exists to catch "
            "would no longer be caught"
        )
        assert run.isdigit(), (
            f"{name} must still satisfy str.isdigit(), since the whole point "
            "is that isdigit() is wider than the ten characters the boundary "
            "promises"
        )


def test_the_roster_is_still_refused_by_exactly_one_gate() -> None:
    """THE COUNT IS THE POINT, and the admission did not change it.

    ``test_readonly.py`` records this for the root entry: the member roster
    carries NO forbidden substring, so the only thing standing between this
    server and a list of people who did not choose to be enumerated by him is
    the anchoring on the pattern beside it.

    **The admission moved that anchor** -- from the bare root to a closed
    numeric segment -- so the sentence is re-measured here against the pattern
    that actually holds the line now, rather than inherited.
    """
    roster = MUST_STAY_REFUSED["roster"]
    substrings = [
        substring
        for substring in readonly._FORBIDDEN_URL_SUBSTRINGS
        if substring in roster.lower()
    ]
    assert substrings == [], (
        "a forbidden substring now refuses the roster. That is not a "
        "regression, but this test's claim -- refused by ONE gate -- has "
        "become false and the comment on the admission must be corrected."
    )
    assert not any(
        pattern.match(roster) for pattern in readonly._ALLOWED_URL_PATTERNS
    )
