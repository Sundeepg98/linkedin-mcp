"""The feed reader's two guarantees, asserted on the SIGNATURES and on
real payloads -- because a property asserted only in a docstring is the
defect this repository has named more than once.

    IN  -- no public callable accepts free text.
    OUT -- no public callable returns a string derived from its input.

The IN half is the one the wave lead's ruling turned on. ``groups.py``
and ``recommendations.py`` guarantee only the OUT half, which is enough
for a surface whose input is a list of hrefs. It is not enough for the
feed, where the obvious next commit is a ``text=`` parameter added in
good faith to count something. A leak needs a route in before it needs a
route out.

Every test below is driven from SYNTHETIC hrefs. Nothing here can be
satisfied by a browser behaving a particular way, and no test in this
file opens a page.
"""
from __future__ import annotations

import inspect

import pytest

from linkedin_server import feed

#: A SYNTHETIC SLUG that resembles no real identifier: no digit run, no
#: name, no urn. It exists to be looked for in output, so it must be a
#: string that could not plausibly arrive from anywhere else in this
#: repository -- if it appears in a return value, it got there from the
#: href this test handed in and from nowhere else.
NEEDLE = "zqx-needle-alpha"

#: Every public callable in the module, resolved once so a function added
#: later is swept automatically rather than needing to be listed here.
PUBLIC_CALLABLES = sorted(
    name
    for name, value in vars(feed).items()
    if not name.startswith("_") and inspect.isfunction(value)
)


def _strings(value):
    """Every string anywhere inside a returned structure, recursively.

    A guarantee about return values is worthless if it only inspects the
    top level: this module returns nested dicts and lists, and a slug
    leaking into ``saw`` or into a ``by_kind`` key would sit two levels
    down.
    """
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _strings(key)
            yield from _strings(item)
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            yield from _strings(item)


# ---------------------------------------------------------------- IN half


def test_the_module_declares_at_least_one_public_callable():
    """The sweeps below are vacuous if the module exposes nothing.

    A check that cannot fail certifies nothing, and a signature sweep
    over an empty list passes loudly. This is the control for the two
    tests that follow it.
    """
    assert len(PUBLIC_CALLABLES) >= 4, PUBLIC_CALLABLES


@pytest.mark.parametrize("name", PUBLIC_CALLABLES)
def test_no_public_callable_accepts_a_parameter_outside_the_closed_set(name):
    """THE SIGNATURE IS THE GUARD, INPUT SIDE.

    This is the ruling implemented mechanically. A parameter named
    ``text``, ``body``, ``author_name``, ``headline`` or ``reason`` turns
    this red at the moment it is written -- before it has carried
    anything anywhere.

    The failure message names the offending parameter, because a refusal
    that reports only what it did NOT match is half a measurement.
    """
    signature = inspect.signature(getattr(feed, name))
    offending = [
        parameter
        for parameter in signature.parameters
        if parameter not in feed._PERMITTED_PARAMETER_NAMES
    ]
    assert not offending, (
        "feed." + name + " accepts " + repr(offending) + ", which is outside "
        "_PERMITTED_PARAMETER_NAMES. If this parameter is meant to carry post "
        "text or an author name, the ruling refuses it: names are not "
        "detectable by shape, so the defence is the signature. If it is a "
        "genuinely new href-shaped input, widen the closed set DELIBERATELY "
        "and say why."
    )


def test_the_permitted_parameter_set_excludes_the_text_vocabulary():
    """The closed set is only a guard if the dangerous names are outside it.

    Without this, somebody clearing the test above could add ``text`` to
    ``_PERMITTED_PARAMETER_NAMES`` and turn it green -- adding a name to
    a list to clear a test, which is exactly the move that admitted a
    sanitiser on the strength of its name elsewhere in this repository.
    """
    for forbidden in (
        "text",
        "body",
        "name",
        "author",
        "author_name",
        "headline",
        "title",
        "reason",
        "label",
        "post",
    ):
        assert forbidden not in feed._PERMITTED_PARAMETER_NAMES, forbidden


# --------------------------------------------------------------- OUT half


def test_no_public_callable_returns_any_substring_of_its_input():
    """THE SIGNATURE IS THE GUARD, OUTPUT SIDE.

    Every public callable is invoked with hrefs carrying :data:`NEEDLE`,
    and every string anywhere in every returned structure is checked.
    """
    href = "https://www.linkedin.com/in/" + NEEDLE + "/"
    calls = {
        "author_kind": (href,),
        "feed_tally": ([href, href],),
        "authorship_concentration": ([href],),
        "overlap": ([href], [href]),
    }
    assert set(calls) == set(PUBLIC_CALLABLES), (
        "a public callable was added or removed and this sweep was not "
        "updated: " + repr(sorted(set(PUBLIC_CALLABLES) ^ set(calls)))
    )

    for name, args in calls.items():
        returned = getattr(feed, name)(*args)
        leaked = [text for text in _strings(returned) if NEEDLE in text]
        assert not leaked, "feed." + name + " published " + repr(leaked)


def test_every_kind_of_entity_href_is_refused_publication_not_just_members():
    """The guarantee is UNIFORM across all six kinds, not member-only.

    ``groups.py`` publishes an opaque group id and argues correctly that
    no run of digits is a person's name. This module deliberately does
    not take that argument for any kind -- a personal-brand Page is named
    after its owner -- so the sweep runs over every segment the module
    recognises rather than over ``/in/`` alone.
    """
    for segment in feed._ENTITY_SEGMENTS:
        href = "https://www.linkedin.com/" + segment + "/" + NEEDLE + "/"
        returned = feed.author_kind(href)
        assert returned["identified"] is True, (segment, returned)
        leaked = [text for text in _strings(returned) if NEEDLE in text]
        assert not leaked, (segment, leaked)


def test_every_published_kind_word_is_in_the_closed_vocabulary():
    """A kind word that is not in AUTHOR_KINDS is an open vocabulary.

    The point of the closed set is that a caller can enumerate what this
    module can ever say. That is only true if the module cannot say
    anything else.
    """
    for segment in feed._ENTITY_SEGMENTS:
        href = "https://www.linkedin.com/" + segment + "/" + NEEDLE + "/"
        assert feed.author_kind(href)["kind"] in feed.AUTHOR_KINDS


# ------------------------------------------------------- branch structure


def test_an_empty_href_refuses_before_anything_is_parsed():
    refused = feed.author_kind("")
    assert refused["identified"] is False
    assert refused["refused"] == "no_href"
    assert refused["saw"] == []


def test_a_path_with_no_entity_segment_refuses_and_says_it_saw_nothing():
    refused = feed.author_kind("https://www.linkedin.com/jobs/")
    assert refused["refused"] == "not_an_entity_href"
    assert refused["saw"] == []


def test_an_entity_root_with_no_identifier_after_it_refuses():
    refused = feed.author_kind("https://www.linkedin.com/in/")
    assert refused["refused"] == "entity_root_carries_no_identifier"
    assert refused["saw"] == ["member"]


def test_the_query_and_fragment_are_dropped_before_any_marker_is_sought():
    """A tracking parameter carrying a segment name must not classify a row.

    Feed hrefs carry tracking parameters routinely, and some of them
    carry the very segment names this module matches on. The path alone
    decides.
    """
    refused = feed.author_kind("https://www.linkedin.com/jobs/?redirect=/in/x")
    assert refused["refused"] == "not_an_entity_href", refused

    resolved = feed.author_kind(
        "https://www.linkedin.com/in/" + NEEDLE + "/?trk=feed#anchor"
    )
    assert resolved["identified"] is True
    assert resolved["kind"] == "member"


# -------------------------------------- the ambiguity branch, and its control


def test_a_path_carrying_two_entity_segments_is_refused_as_ambiguous():
    """THE BRANCH THIS MODULE HAS AND ITS TWO SIBLINGS DO NOT.

    THE INPUT IS CHOSEN FROM THE BRANCH STRUCTURE, NOT FROM A MODEL OF
    THE RISK. Nothing else about this href is wrong: both segments are
    well-formed, both carry an identifier after them, the path is
    non-empty and there is no query string. Every OTHER refusal branch
    in ``_entity_key`` passes this input cleanly. The ambiguity check is
    the only thing standing between it and a confident kind word -- a
    word that reads as a measurement and would mean nothing but the order
    the checks ran in.

    MEASURED UNDER THE MUTATION, and it corrected the guess this
    docstring first carried. With the check neutralised
    (``if len(present) > 1`` -> ``if False``) this input does not resolve
    to ``"company"`` as its author predicted. It resolves to::

        {'identified': True, 'kind': 'member', 'href_shape': '<a feed author>'}

    because ``_ENTITY_SEGMENTS`` inherits ``shape._CENSUS_ENTITY_HREFS``'
    order, in which ``in`` precedes ``company``. **That is worse than the
    error I guessed at**: a company Page's people directory is attributed
    to a PERSON, on a surface whose whole ruling is about not naming
    people. The branch is load-bearing in the direction nobody would have
    checked for.

    THE ASSERTION IS ON THE REFUSAL REASON. Asserting merely that
    ``identified`` is False would survive being satisfied by the wrong
    branch, and asserting ``kind != "company"`` would have PASSED under
    the mutation -- which is the concrete reason a mutation is run
    instead of an input being reasoned about.
    """
    refused = feed.author_kind(
        "https://www.linkedin.com/company/" + NEEDLE + "/people/in/" + NEEDLE + "-two/"
    )
    assert refused["identified"] is False, refused
    assert refused["refused"] == "ambiguous_multiple_entity_kinds", refused
    assert sorted(refused["saw"]) == ["company", "member"], refused


def test_the_ambiguity_refusal_names_both_kinds_it_saw():
    """A refusal reporting only what it did NOT match is half a measurement.

    Three rounds were lost in this repository to exactly that shape, and
    the remedy was to print what WAS seen. ``saw`` is drawn from the
    closed kind vocabulary, so reporting it discloses nothing.
    """
    refused = feed.author_kind(
        "https://www.linkedin.com/groups/" + NEEDLE + "/events/" + NEEDLE + "/"
    )
    assert refused["refused"] == "ambiguous_multiple_entity_kinds"
    assert set(refused["saw"]) <= set(feed.AUTHOR_KINDS)
    assert len(refused["saw"]) == 2, refused


# --------------------------------------------------------------- the tallies


def test_rows_and_identified_are_reported_separately():
    """A bare identified count reads the same whether rows were refused.

    Handed four rows of which two resolve, a caller must be able to see
    that two were refused rather than that two were all that was offered.
    """
    tally = feed.feed_tally(
        [
            "https://www.linkedin.com/in/" + NEEDLE + "/",
            "https://www.linkedin.com/jobs/",
            "https://www.linkedin.com/company/" + NEEDLE + "/",
            "",
        ]
    )
    assert tally["rows"] == 4
    assert tally["identified"] == 2
    assert tally["refused"] == {"not_an_entity_href": 1, "no_href": 1}


def test_the_distinct_count_separates_a_repeated_author_from_several():
    """The feed is the surface where identified and distinct diverge hardest.

    The same author four times in one scroll is the ordinary case here,
    not the exotic one, and the distinct count is what the precondition
    wants.
    """
    href = "https://www.linkedin.com/in/" + NEEDLE + "/"
    tally = feed.feed_tally([href, href, href, href])
    assert tally["identified"] == 4
    assert tally["distinct_authors"] == 1


def test_the_key_carries_the_kind_so_two_kinds_sharing_a_spelling_stay_distinct():
    """A key of the segment alone would merge these and under-report.

    ``/company/<x>`` and ``/in/<x>`` are different entities that can
    share a segment spelling.
    """
    tally = feed.feed_tally(
        [
            "https://www.linkedin.com/in/" + NEEDLE + "/",
            "https://www.linkedin.com/company/" + NEEDLE + "/",
        ]
    )
    assert tally["distinct_authors"] == 2, tally


def test_by_kind_counts_every_kind_it_saw_and_omits_the_ones_it_did_not():
    tally = feed.feed_tally(
        [
            "https://www.linkedin.com/in/" + NEEDLE + "/",
            "https://www.linkedin.com/in/" + NEEDLE + "-two/",
            "https://www.linkedin.com/company/" + NEEDLE + "/",
        ]
    )
    assert tally["by_kind"] == {"member": 2, "company": 1}
    assert set(tally["by_kind"]) <= set(feed.AUTHOR_KINDS)


def test_an_empty_feed_tallies_to_zeroes_rather_than_raising():
    tally = feed.feed_tally([])
    assert tally["rows"] == 0
    assert tally["identified"] == 0
    assert tally["distinct_authors"] == 0
    assert tally["by_kind"] == {}
    assert tally["refused"] == {}


# ------------------------------------------------------------ concentration


def test_concentration_answers_whether_one_author_dominated_as_an_integer():
    """The function that pays for the module's cost.

    A caller cannot ask WHICH author dominated. This is the question
    worth asking, and the answer is a number.
    """
    one = "https://www.linkedin.com/in/" + NEEDLE + "/"
    two = "https://www.linkedin.com/in/" + NEEDLE + "-two/"
    result = feed.authorship_concentration([one, one, one, two])
    assert result["identified"] == 4
    assert result["distinct_authors"] == 2
    assert result["largest_author_rows"] == 3
    assert result["concentrated"] is True
    assert not [text for text in _strings(result) if NEEDLE in text]


def test_an_evenly_split_two_author_feed_is_not_reported_as_concentrated():
    """A STRICT majority, so a 2-2 split is not dominance.

    A boolean derived from a threshold is only as honest as its rule, and
    this pins the rule so a later change to it is visible in a diff.
    """
    one = "https://www.linkedin.com/in/" + NEEDLE + "/"
    two = "https://www.linkedin.com/in/" + NEEDLE + "-two/"
    result = feed.authorship_concentration([one, one, two, two])
    assert result["largest_author_rows"] == 2
    assert result["concentrated"] is False


def test_an_empty_feed_is_not_a_concentrated_one():
    """A vacuous True here would read as a finding.

    With nothing identified there is no largest author, and ``max`` over
    an empty collection would raise. Both are handled deliberately.
    """
    result = feed.authorship_concentration(["https://www.linkedin.com/jobs/"])
    assert result["identified"] == 0
    assert result["largest_author_rows"] == 0
    assert result["concentrated"] is False


# ----------------------------------------------------------------- overlap


def test_overlap_publishes_the_intersection_size_and_never_its_members():
    one = "https://www.linkedin.com/in/" + NEEDLE + "/"
    two = "https://www.linkedin.com/in/" + NEEDLE + "-two/"
    three = "https://www.linkedin.com/in/" + NEEDLE + "-three/"
    result = feed.overlap([one, two], [two, three])
    assert result["first_distinct"] == 2
    assert result["second_distinct"] == 2
    assert result["common"] == 1
    assert result["disjoint"] is False
    assert not [text for text in _strings(result) if NEEDLE in text]


def test_two_empty_sets_are_disjoint_and_the_counts_say_why():
    """``disjoint`` True for two empty sets is correct and easy to misread.

    A caller distinguishing "shares nobody" from "had nobody to share"
    reads the two distinct counts, which is why both are returned.
    """
    result = feed.overlap([], [])
    assert result["disjoint"] is True
    assert result["first_distinct"] == 0
    assert result["second_distinct"] == 0


# ------------------------------------------------------ derived vocabularies


def test_the_kind_vocabulary_is_derived_from_shape_rather_than_retyped():
    """A seventh entity kind in shape.py must not become a silent hole.

    This pins the CURRENT six by count and by membership, so adding a
    marker to ``shape._CENSUS_ENTITY_HREFS`` without teaching this module
    its kind word turns the second assertion red rather than passing in
    silence.
    """
    from linkedin_server import shape

    markers = {marker.split("/")[1] for marker in shape._CENSUS_ENTITY_HREFS}
    assert len(feed.AUTHOR_KINDS) == 6, feed.AUTHOR_KINDS
    assert markers == set(feed._KIND_FOR_SEGMENT), (
        "shape._CENSUS_ENTITY_HREFS and feed._KIND_FOR_SEGMENT disagree: "
        + repr(markers ^ set(feed._KIND_FOR_SEGMENT))
        + ". A new entity kind needs a kind word here, or this module "
        "resolves its hrefs to not_an_entity_href and under-counts silently."
    )


def test_the_published_literal_is_not_shaped_like_a_url():
    """A reader must not mistake it for a redacted real value.

    ``groups.py`` publishes a marker-shaped literal because its surface
    has a safe identifier to gesture at. This one has none, so the
    literal deliberately does not resemble an href.
    """
    assert "/" not in feed.PUBLISHED_HREF
    assert feed.PUBLISHED_HREF.startswith("<")


def test_every_refusal_reason_the_module_can_emit_is_in_the_closed_set():
    for status, reason in feed._REFUSAL_FOR_STATUS.items():
        assert reason in feed.REFUSALS, (status, reason)
    assert len(set(feed._REFUSAL_FOR_STATUS.values())) == len(feed.REFUSALS)
