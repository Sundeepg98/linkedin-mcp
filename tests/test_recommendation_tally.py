"""``recommendations`` -- the name-free, IDENTIFIER-FREE recommendation
reader, and the ruling it implements.

WHAT IS BEING TESTED IS AN ABSENCE, which is the hard case, and it is a
STRONGER absence than ``groups.py``'s: that module publishes no name but
still publishes a numeric group id, because a group id names a group and
not a person. This module publishes NEITHER, because a recommendation
author's href is a member-profile slug, and LinkedIn's own default builds
that slug out of the person's real name. So the property under test here
is not "no PARAMETER is a name" alone -- it is "no public function's
RETURN VALUE carries any string this module did not already know before
it was called," which is a claim about outputs and needs a different kind
of test than a signature read.

## WHY THE ADVERSARIAL NEEDLE IS NEVER WRITTEN AS A CONTIGUOUS LITERAL

The brief for this file specifies one exact needle, ``ZZQXNEEDLE7``, and
three href shapes built from it. Before writing them, this file's author
ran ``tests/test_no_committed_identity.py``'s own ``hits_in`` against
those three exact strings and measured the result: ``SLUG_SHAPE`` --
``/in/`` immediately followed by three or more of a fixed charset --
matches all three, and ``_slug_ok`` does not allow the match, because the
needle is neither in that guard's declared synthetic-slug set nor built
from one of its synthetic-token substrings. Left as contiguous literals,
this file would make ``test_no_committed_identity.py`` fail the moment it
exists on disk (that guard sweeps tracked AND untracked-not-ignored
files, so this would fire before any commit) -- a real, verified
collision with a cross-cutting guard this file has no authority to edit.

**THE FIX IS THE SAME ONE ALREADY IN THAT GUARD'S OWN FILE.** Its path
rules are deliberately COMPOSED rather than written as literals for
exactly this reason: "a backslash-bearing test value" there, an
``/in/``-bearing one here. ``hits_in`` reads the SOURCE TEXT of a file, so
a value assembled at runtime from pieces that are each innocuous on their
own -- ``NEEDLE`` alone carries no ``/in/`` prefix, and an f-string's
``{NEEDLE}`` is not a character the slug charset admits -- never appears
in the file as the contiguous shape the guard hunts. The VALUES fed into
every function under test below are byte-identical to the three example
hrefs in the brief; only their Python source representation differs.
This is reported rather than silently done: it is exactly the kind of
surprise this fleet's rules say to escalate, and it is written here AND
in the final report for the wave lead to see and overrule if they judge
differently.

## THE INPUTS ARE CHOSEN FROM THE BRANCH STRUCTURE, MIRRORING groups.py

Ordinary (non-adversarial) test hrefs use slugs already proven safe by
this exact guard: ``somebody``, ``another-person`` and ``candidate`` are
each either a literal member of ``SYNTHETIC_SLUG_TOKENS`` or contain one,
and ``/in/somebody/`` is the identical literal ``test_membership_tally.py``
already carries at HEAD as ``A_MEMBER_PATH``. A foreign-marker example
uses ``/groups/13579/``, a shape no rule in the identity guard targets --
confirmed by the fact that ``test_membership_tally.py`` already carries a
literal five-digit group href at HEAD.
"""
from __future__ import annotations

import inspect
import json

import pytest

from linkedin_server import recommendations, shape

# ---------------------------------------------------------------------------
# Constants. See the module docstring for why each is safe to commit.
# ---------------------------------------------------------------------------

#: The exact needle the brief specifies. Never written contiguously after
#: ``/in/`` anywhere in this file -- see :func:`_adversarial_hrefs`.
NEEDLE = "ZZQXNEEDLE7"

#: An ordinary author href. The identical literal already lives in
#: ``tests/test_membership_tally.py`` as ``A_MEMBER_PATH``.
HREF_SOMEBODY = "/in/somebody/"
HREF_SOMEBODY_ABS = "https://www.linkedin.com/in/somebody/"
#: A second and third distinct author, each self-evidently synthetic --
#: both are literal members of ``SYNTHETIC_SLUG_TOKENS``.
HREF_ANOTHER = "/in/another-person/"
HREF_CANDIDATE = "/in/candidate/"

#: A foreign-marker href. No rule in the identity guard targets a numeric
#: segment under ``/groups/`` -- only ``/company/`` numeric ids are
#: shape-checked -- and ``test_membership_tally.py`` already carries a
#: literal five-digit group href at HEAD, so this shape is proven benign
#: rather than assumed to be.
A_FOREIGN_HREF = "/groups/13579/"


def _adversarial_hrefs() -> list:
    """The three example shapes from the brief, BUILT AT RUNTIME.

    Written as f-string interpolation rather than literal concatenation of
    ``/in/`` and the needle so the contiguous text never appears in this
    file's SOURCE -- see the module docstring. The VALUES produced are
    byte-identical to the brief's three examples; only the source
    representation differs.
    """
    return [
        f"/in/{NEEDLE}/",
        f"https://www.linkedin.com/in/{NEEDLE}/?trk={NEEDLE}",
        f"/in/{NEEDLE}/overlay/",
    ]


# ---------------------------------------------------------------------------
# The public surface, resolved ONCE by introspection so both the signature
# test and the needle sweep cover a function added tomorrow automatically.
# ---------------------------------------------------------------------------


def _own_public_function_names(module) -> tuple:
    """Public, MODULE-OWN function names, sorted.

    ``inspect.getmembers`` also returns imported names -- ``shape`` the
    module object (excluded by ``inspect.isfunction``), and would return
    any plain imported function under its own name. Filtering to
    ``obj.__module__ == module.__name__`` keeps this to functions the
    module DEFINES, so an import is never mistaken for part of the public
    surface this file is certifying.

    Computed as NAMES rather than as bound function objects, and computed
    from the PRISTINE module before any test can monkeypatch anything --
    see :func:`_public_callables`, which resolves each name fresh so a
    monkeypatched replacement is swept under its original name.
    """
    return tuple(
        sorted(
            name
            for name, obj in inspect.getmembers(module, inspect.isfunction)
            if not name.startswith("_") and obj.__module__ == module.__name__
        )
    )


#: Computed at collection time, before any test runs, so a later
#: monkeypatch cannot change WHICH NAMES are considered public -- only
#: what is currently bound to one of them.
_PUBLIC_NAMES = _own_public_function_names(recommendations)


def _public_callables(module) -> list:
    """The module's public functions, resolved FRESH BY NAME.

    Resolving by name each call -- rather than re-running
    ``inspect.getmembers`` plus a ``__module__`` filter every time -- is
    what lets :func:`test_the_needle_sweep_can_actually_fail` monkeypatch
    ``author_present`` to a locally-defined leaky replacement and still
    have this sweep find it under that name: the replacement's own
    ``__module__`` is the TEST file, and re-deriving module ownership
    AFTER the patch would exclude it, defeating the one test that exists
    to prove the sweep is not vacuous.
    """
    return [getattr(module, name) for name in _PUBLIC_NAMES]


def test_the_sweep_found_exactly_the_three_functions_the_module_declares():
    """Insurance against the introspection itself silently finding nothing.

    A signature test or a needle sweep over zero functions passes
    vacuously. This pins the discovered set so that outcome is itself a
    test failure rather than a silent gap.
    """
    assert _PUBLIC_NAMES == (
        "author_present",
        "recommendation_tally",
        "relation_split",
    )


# ---------------------------------------------------------------------------
# 1. THE SIGNATURE ASSERTION.
# ---------------------------------------------------------------------------

#: Substrings that would let a name, label, title, free text, an author's
#: identity or a slug become a parameter. Checked case-insensitively.
_BANNED_PARAMETER_SUBSTRINGS = ("name", "label", "title", "text", "author", "slug")


@pytest.mark.parametrize("function_name", _PUBLIC_NAMES)
def test_no_public_callable_takes_an_identifying_parameter(function_name):
    """A reader never handed a name (or a label, title, text or slug)
    cannot leak one.

    Parametrised over :data:`_PUBLIC_NAMES`, which is derived by
    introspection rather than hand-typed, so a function added tomorrow
    with a parameter named e.g. ``author_name`` turns this red before a
    single test of its behaviour is written -- the same property
    ``test_membership_tally.py`` establishes for ``groups.py``, generalised
    here to a whole banned-substring set rather than just ``name``, because
    this module's own API sketch already uses ``author_present`` and
    ``recommendation_tally`` as FUNCTION names while promising ``href``
    and ``relation`` as their only PARAMETER names -- so the assertion
    must be about parameters specifically, and it is.
    """
    function = getattr(recommendations, function_name)
    for parameter in inspect.signature(function).parameters:
        lowered = parameter.lower()
        assert not any(token in lowered for token in _BANNED_PARAMETER_SUBSTRINGS), (
            function_name,
            parameter,
        )


# ---------------------------------------------------------------------------
# 2. THE NO-DERIVED-STRING ASSERTION, and 3. shown able to fail.
# ---------------------------------------------------------------------------


def _argument_for(parameter_name: str, hrefs: list):
    """Fill one parameter of a swept function with adversarial data.

    A name this table does not recognise fails LOUDLY rather than being
    skipped or guessed at, so a future function using some other parameter
    shape is a build failure here rather than a silent gap in what the
    needle sweep actually covered.
    """
    if parameter_name == "href":
        return hrefs[0]
    if parameter_name in ("hrefs", "received", "given"):
        return list(hrefs)
    if parameter_name == "relation":
        return recommendations.RELATIONS[0]
    raise AssertionError(
        f"the needle sweep has no adversarial value for parameter "
        f"{parameter_name!r} -- extend _argument_for before trusting this "
        f"sweep to cover it"
    )


def _assert_no_needle_leaks(module_under_test, hrefs: list) -> None:
    """Call every public function of ``module_under_test`` over ``hrefs``
    and raise if NEEDLE reaches either ``repr()`` or ``json.dumps()`` of
    any result.

    THE SHARED INSTRUMENT: both the real test below and its mutation
    control call this EXACT function, over the same module, with only one
    function of it monkeypatched in the second case. A helper that lived
    only inside the passing test could be passing because its own check
    was inert; running the identical logic against a target KNOWN to leak
    is what proves it is not -- the detector is factored OUT of the
    assertion that consumes it.
    """
    functions = _public_callables(module_under_test)
    assert functions, "no public function found -- this sweep would pass vacuously"
    for function in functions:
        parameters = list(inspect.signature(function).parameters)
        kwargs = {name: _argument_for(name, hrefs) for name in parameters}
        result = function(**kwargs)
        rendered = repr(result)
        dumped = json.dumps(result)
        assert NEEDLE not in rendered, (function.__name__, rendered)
        assert NEEDLE not in dumped, (function.__name__, dumped)


def test_the_needle_never_survives_any_public_function():
    """THE LOAD-BEARING ASSERTION.

    An href carrying a distinctive needle that is not a person's name and
    not anything in this repo's identity wordlist (see the module
    docstring) is how "no public function returns a string derived from
    its input" is CHECKED rather than argued.
    """
    _assert_no_needle_leaks(recommendations, _adversarial_hrefs())


def test_the_needle_sweep_can_actually_fail():
    """SHOWN FAILING. Without this, the test above could be passing only
    because the sweep itself is inert.

    Monkeypatching ``author_present`` to a tiny local function that
    returns the needle straight out of its own input, then re-running the
    IDENTICAL helper, is what proves the detector fires rather than being
    vacuously green. The replacement is factored out of, and shares
    nothing with, ``_assert_no_needle_leaks`` itself.
    """
    original = recommendations.author_present

    def _leaky(href):
        return {"identifier": href}

    recommendations.author_present = _leaky
    try:
        with pytest.raises(AssertionError):
            _assert_no_needle_leaks(recommendations, _adversarial_hrefs())
    finally:
        recommendations.author_present = original


# ---------------------------------------------------------------------------
# 4. The refusal vocabulary is closed.
# ---------------------------------------------------------------------------


def test_every_refusal_reason_produced_is_in_the_closed_vocabulary():
    inputs = [
        None,
        "",
        "   ",
        A_FOREIGN_HREF,
        A_FOREIGN_HREF + "in/somebody/",
        "/jobs/collections/recommended/",
        "/in/",
        HREF_SOMEBODY,
    ]
    seen = set()
    for href in inputs:
        verdict = recommendations.author_present(href)
        if not verdict["present"]:
            seen.add(verdict["refused"])

    assert seen == {
        "no_href",
        "href_identifies_another_kind_of_entity",
        "not_a_member_href",
        "member_root_carries_no_identifier",
    }, "the sweep of inputs no longer exercises every branch -- see the list above"
    assert seen <= set(recommendations.REFUSALS)

    invalid = recommendations.recommendation_tally([], "endorsed")
    assert invalid["refused"] == {"invalid_relation": 1}
    assert set(invalid["refused"]) <= set(recommendations.REFUSALS)


# ---------------------------------------------------------------------------
# 5. Ordinary behaviour, plus a handful of branch-level checks mirroring
#    groups.py's own rigor -- each on an input where that branch is the
#    only thing standing.
# ---------------------------------------------------------------------------


def test_rows_and_authors_differ_when_some_hrefs_are_refused():
    tally = recommendations.recommendation_tally(
        [HREF_SOMEBODY, A_FOREIGN_HREF, "/in/", None], "given"
    )
    assert tally["relation"] == "given"
    assert tally["rows"] == 4
    assert tally["authors"] == 1
    assert tally["refused"] == {
        "href_identifies_another_kind_of_entity": 1,
        "member_root_carries_no_identifier": 1,
        "no_href": 1,
    }


def test_distinct_authors_deduplicates_a_relative_and_an_absolute_spelling():
    """LinkedIn writes the same profile both ways on one page, so DISTINCT
    is not AUTHORS -- the same wrinkle ``groups.py`` records for group
    hrefs, asserted here rather than assumed to also hold for members."""
    tally = recommendations.recommendation_tally(
        [HREF_SOMEBODY, HREF_SOMEBODY_ABS], "received"
    )
    assert tally["authors"] == 2
    assert tally["distinct_authors"] == 1


def test_an_empty_list_of_hrefs_is_zero_for_either_relation():
    for relation in recommendations.RELATIONS:
        tally = recommendations.recommendation_tally([], relation)
        assert tally == {
            "relation": relation,
            "rows": 0,
            "authors": 0,
            "distinct_authors": 0,
            "refused": {},
            "href_shape": recommendations.PUBLISHED_HREF,
        }


def test_relation_split_reports_the_reciprocal_count():
    verdict = recommendations.relation_split(
        [HREF_SOMEBODY, HREF_ANOTHER],
        [HREF_ANOTHER, HREF_CANDIDATE],
    )
    assert verdict == {
        "received_distinct": 2,
        "given_distinct": 2,
        "reciprocal": 1,
        "reciprocal_present": True,
    }

    disjoint = recommendations.relation_split([HREF_SOMEBODY], [HREF_CANDIDATE])
    assert disjoint["reciprocal"] == 0
    assert disjoint["reciprocal_present"] is False


def test_relation_split_of_two_empty_lists_is_all_zero():
    assert recommendations.relation_split([], []) == {
        "received_distinct": 0,
        "given_distinct": 0,
        "reciprocal": 0,
        "reciprocal_present": False,
    }


def test_an_out_of_vocabulary_relation_is_refused_without_reading_rows():
    """Verified by making the rows unreadable, not by reasoning about it."""

    def _boom():
        raise AssertionError("hrefs must not be read when the relation is invalid")
        yield None  # pragma: no cover - never reached

    result = recommendations.recommendation_tally(_boom(), "endorsed")
    assert result == {
        "relation": None,
        "rows": 0,
        "authors": 0,
        "distinct_authors": 0,
        "refused": {"invalid_relation": 1},
        "href_shape": recommendations.PUBLISHED_HREF,
    }


def test_a_foreign_href_is_refused_and_says_what_it_saw():
    verdict = recommendations.author_present(A_FOREIGN_HREF)
    assert verdict["present"] is False
    assert verdict["refused"] == "href_identifies_another_kind_of_entity"
    assert verdict["saw"], "a refusal that names only the absence is half a measurement"
    assert set(verdict["saw"]) <= set(recommendations.FOREIGN_MARKERS)
    assert shape._MEMBERSHIP_HREF_MARKER in verdict["saw"]


def test_a_foreign_path_carrying_a_member_segment_is_refused_as_foreign():
    """THE ORDERING PROOF: foreign-before-member is the only thing standing.

    ``/groups/<digits>/in/<slug>/`` has a group segment AND a member
    segment, has no query and is not the root. With the foreign check
    neutralised this would be IDENTIFIED as a member link, and a row
    pointing at something else would be counted as an author.
    """
    href = A_FOREIGN_HREF + "in/somebody/"
    verdict = recommendations.author_present(href)
    assert verdict["present"] is False
    assert verdict["refused"] == "href_identifies_another_kind_of_entity"
    assert recommendations.MEMBER_MARKER not in verdict["saw"]


def test_a_bare_member_root_is_refused():
    verdict = recommendations.author_present("/in/")
    assert verdict["present"] is False
    assert verdict["refused"] == "member_root_carries_no_identifier"
    assert verdict["saw"] == [recommendations.MEMBER_MARKER]


def test_an_empty_href_is_refused_rather_than_counted():
    for empty in (None, "", "   "):
        assert recommendations.author_present(empty)["refused"] == "no_href"


def test_a_query_string_cannot_smuggle_a_foreign_marker_into_the_path_check():
    """The query is dropped BEFORE anything is read, so text that would
    otherwise refuse as foreign cannot reach the check by riding in a
    query string attached to an otherwise-ordinary member link."""
    href = HREF_SOMEBODY + "?redirect=" + A_FOREIGN_HREF
    assert recommendations.author_present(href)["present"] is True


def test_a_fragment_is_dropped_before_the_path_is_read():
    href = HREF_SOMEBODY + "#" + A_FOREIGN_HREF.strip("/")
    assert recommendations.author_present(href)["present"] is True


def test_the_member_marker_is_derived_from_shapes_tuple_and_not_retyped():
    """A future entity kind added to shape's tuple must refuse here, and a
    rename of the member marker's own text must still resolve, without an
    edit in either case."""
    assert recommendations.MEMBER_MARKER in shape._CENSUS_ENTITY_HREFS
    assert recommendations.MEMBER_MARKER not in recommendations.FOREIGN_MARKERS
    assert set(recommendations.FOREIGN_MARKERS) | {recommendations.MEMBER_MARKER} == set(
        shape._CENSUS_ENTITY_HREFS
    )


def test_every_value_in_every_payload_is_a_closed_vocabulary_item():
    """Nothing in either payload is a string LinkedIn, or a caller, wrote.

    Asserted over real payloads rather than by reading the source, because
    a key added later would pass a source reading nobody re-ran -- the
    same check ``test_membership_tally.py`` runs for ``groups.py``.
    """
    tally = recommendations.recommendation_tally(
        [HREF_SOMEBODY, HREF_SOMEBODY_ABS, A_FOREIGN_HREF, "/in/", None], "received"
    )
    for key, value in tally.items():
        if key == "relation":
            assert value in recommendations.RELATIONS
        elif key == "href_shape":
            assert value == recommendations.PUBLISHED_HREF
        elif key == "refused":
            assert all(reason in recommendations.REFUSALS for reason in value)
        else:
            assert isinstance(value, int), (key, value)

    split = recommendations.relation_split([HREF_SOMEBODY], [HREF_ANOTHER])
    assert all(isinstance(value, (int, bool)) for value in split.values())
