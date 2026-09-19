"""``anchors`` classifies by route SHAPE and can publish nothing else.

Every property asserted here is one the module's docstring claims. Four are
STRUCTURAL -- a signature, an order, a closed alphabet, and the form of the
in-page comparison -- and a structural property is the only kind a future edit
cannot quietly forget.

SHOWN FAILING before admission, against copies and monkeypatches so no
contended file was edited. Recorded in ``_audit/2026-09-19-anchor-reader.md``.
"""

from __future__ import annotations

import inspect

import pytest

from linkedin_server import anchors


#: Parameter names whose VALUE would be an address or an identity.
_ADDRESS_SHAPED = frozenset(
    {"href", "hrefs", "url", "urls", "link", "links", "slug", "slugs",
     "name", "names", "id", "ids", "urn", "urns", "path", "paths"}
)


def test_the_module_is_readable_at_all() -> None:
    """The control. A guard over an empty module refuses nothing."""
    assert len(anchors.ROUTE_CLASSES) >= 10
    assert len(anchors.ROUTE_TABLE) >= 8
    for name in ("read_anchors", "tally", "term_for", "control_fixture"):
        assert callable(getattr(anchors, name))


def test_no_address_is_a_parameter_of_any_publishing_function() -> None:
    """``groups.py``'s rule, copied with its reason.

    A reader never handed an address cannot leak one, whatever LinkedIn routes
    tomorrow. A filter has to keep up; an absent parameter does not.
    """
    for name in ("tally", "term_for", "emitted_alphabet", "control_fixture"):
        signature = inspect.signature(getattr(anchors, name))
        offenders = _ADDRESS_SHAPED & set(signature.parameters)
        assert not offenders, (
            f"anchors.{name} takes {sorted(offenders)}, which is an address by "
            "another name. Everything a caller publishes must take INTEGERS."
        )


def test_the_readers_only_string_parameter_is_the_documented_control_path() -> None:
    signature = inspect.signature(anchors.read_anchors)
    assert list(signature.parameters) == ["page", "html"], (
        "read_anchors' signature changed. Its second parameter is the "
        "detached-container CONTROL path; another string parameter would need "
        "its own argument about what may cross the boundary."
    )
    assert not (_ADDRESS_SHAPED & set(signature.parameters))


def test_the_class_order_is_the_contract_and_member_profile_is_index_zero() -> None:
    """The page returns a POSITION, so reordering renames every reading.

    ``member_profile`` sitting at index 0 is load-bearing for the next test:
    a classifier that failed open, or a ``term_for`` that clamped a negative
    index, would land on the one class whose entity segment is a NAME.
    """
    assert anchors.ROUTE_CLASSES[0] == "member_profile"
    assert anchors.ROUTE_CLASSES[:4] == (
        "member_profile", "company_page", "school_page", "job_posting",
    )


def test_out_of_range_is_REFUSED_and_never_clamped() -> None:
    """A clamp at the low end renames anything into ``member_profile``."""
    assert anchors.term_for(0) == "member_profile"
    for out_of_range in (-1, -7, len(anchors.ROUTE_CLASSES), 999):
        assert anchors.term_for(out_of_range) == "index_out_of_range", (
            f"term_for({out_of_range}) must refuse. A clamp would rename an "
            "unclassifiable anchor into a real class -- and at the low end "
            "that class is member_profile, the one that carries a name."
        )


def test_the_output_alphabet_is_closed_over_adversarial_input() -> None:
    counts = list(range(len(anchors.ROUTE_CLASSES) + 6))
    result = anchors.tally(counts)
    emitted = set(result["by_class"])
    allowed = anchors.emitted_alphabet()
    assert emitted <= allowed, (
        f"tally emitted {sorted(emitted - allowed)}, which is not in the "
        "module's own alphabet."
    )


def test_a_short_count_list_is_reported_not_padded() -> None:
    """A missing class and a zero-count class are different answers."""
    short = anchors.tally([1, 2])
    assert short["classes_not_reported"] == len(anchors.ROUTE_CLASSES) - 2
    assert short["by_class"] == {"member_profile": 1, "company_page": 2}
    over = anchors.tally([0] * (len(anchors.ROUTE_CLASSES) + 3))
    assert over["positions_beyond_the_alphabet"] == 3


# ---------------------------------------------------------------------------
# THE SEGMENT RULE. ``menus.py`` shipped a matcher where classify("Star Anise")
# returned ``star``, because containment was applied at every phrase length and
# THE HAZARD HAD BEEN TREATED AS A PROPERTY OF ONE WORD rather than of every
# single-word term. The same hole exists here one level over.
#
# THE PREDICTED HARM WAS WRONG AND THE MEASURED ONE IS WORSE. The expectation
# was that containment moves a name-bearing anchor OUT of member_profile.
# Measured in a page: member_profile went 1 -> 4, because ``in`` is a substring
# of linkedin, messaging and institute. Over-reporting the hazard class is not
# the safe direction -- see the last test in this file.
# ---------------------------------------------------------------------------


def test_the_route_table_holds_single_segments_never_paths() -> None:
    """A table entry carrying a slash would be a path fragment, not a segment,
    and a path fragment is matched by containment however it is compared.
    """
    for token, first, second in anchors.ROUTE_TABLE:
        assert token in anchors.ROUTE_CLASSES, f"{token} is not in the alphabet"
        for segment in (first, second):
            assert "/" not in segment, (
                f"route term {segment!r} for {token} contains a slash. Terms "
                "are SEGMENTS compared for equality at a fixed position."
            )
            assert segment == segment.strip()


def test_the_in_page_comparison_is_segment_equality_and_not_containment() -> None:
    """Asserted on the classifier's SOURCE, because the comparison happens in
    the page and no Python test can call it.

    This is the ``Star Anise`` class of defect, and pinning the FORM is what
    closes the class. A rewrite to ``path.indexOf(first)`` classifies
    ``/company/example-school-group/`` as ``school_page`` -- and, measured rather
    than predicted, sweeps a help article, a messaging thread and a school page
    into ``member_profile``, taking that count from 1 to 4.
    """
    source = anchors._CLASSIFY_IN_PAGE
    assert "segments[0] !== first" in source, (
        "the first-segment comparison is no longer an equality test. A "
        "containment test here matches a route term INSIDE a slug."
    )
    assert "segments[1] !== second" in source, (
        "the second-segment comparison is no longer an equality test."
    )
    for banned in ("path.indexOf(first", "path.includes(", "raw.includes("):
        assert banned not in source, (
            f"{banned!r} is a containment test over the whole path. That is "
            "exactly the shape that made classify('Star Anise') return 'star'."
        )


def test_the_control_fixture_carries_both_adversarial_anchors() -> None:
    """The fixture's INPUT, asserted offline, so the control cannot rot.

    Run through the real in-page classifier during a live read -- measured
    2026-09-19: it reproduced ``CONTROL_EXPECTATION`` exactly, twice.
    """
    fixture = anchors.control_fixture()
    assert '"/in/example-company-ltd/"' in fixture, (
        "the fixture no longer carries a MEMBER slug containing a route term. "
        "That is the adversarial case that matters most: a containment "
        "matcher moves it out of member_profile."
    )
    assert '"/company/example-school-group/"' in fixture, (
        "the fixture no longer carries a COMPANY slug containing the 'school' "
        "route term."
    )
    assert "<a>m</a>" in fixture, "the no-href case is gone"


def test_the_control_has_an_expectation_covering_every_class() -> None:
    """A control whose result nobody predicted cannot fail."""
    assert set(anchors.CONTROL_EXPECTATION) == set(anchors.ROUTE_CLASSES), (
        "CONTROL_EXPECTATION and ROUTE_CLASSES disagree, so the control "
        "exercises fewer classes than the module can emit."
    )
    assert all(value >= 1 for value in anchors.CONTROL_EXPECTATION.values())


def test_this_guard_can_fail_a_reorder_renames_the_hazard_class(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SHOWN FAILING: index 0 stops meaning ``member_profile`` under a reorder.

    Asserts the SPECIFIC harm rather than that something changed -- the page's
    integer 0 would then be mapped to an organisation, and the count of
    name-bearing anchors would silently become a count of something else.
    """
    assert anchors.term_for(0) == "member_profile"
    reordered = ("company_page",) + tuple(
        term for term in anchors.ROUTE_CLASSES if term != "company_page"
    )
    monkeypatch.setattr(anchors, "ROUTE_CLASSES", reordered)
    assert anchors.term_for(0) != "member_profile", (
        "a reordered alphabet did NOT change what index 0 resolves to, which "
        "would mean the order pin is guarding nothing"
    )


def test_a_route_term_really_is_a_substring_of_other_routes() -> None:
    """The segment rule is LOAD-BEARING, and this measures it rather than
    asserting it.

    **MEASURED 2026-09-19, and it refuted the prediction that produced it.**
    Running a containment classifier against the control fixture was expected
    to move a NAME-BEARING anchor OUT of ``member_profile``. It did the
    opposite and worse: ``member_profile`` went **1 -> 4**, because the route
    term ``in`` is a substring of ``linkedin``, ``messaging`` and
    ``institute`` -- so a help article, a messaging thread and a school page
    were all reclassified as member profiles.

    Over-reporting the hazard class is not the safe direction. It makes the
    one count a caller must not publish per-record into a number that is
    wrong by 4x, and it would tell a caller a page is full of people when it
    holds one.

    This test pins the property that makes that possible, so nobody
    re-litigates the segment rule as theoretical.
    """
    terms = {first for _token, first, _second in anchors.ROUTE_TABLE}
    # Path words this repository's own routes are built from.
    route_words = ("linkedin", "messaging", "institute", "collections")
    offenders = {
        term: [word for word in route_words if term in word and term != word]
        for term in terms
    }
    offenders = {term: words for term, words in offenders.items() if words}
    assert offenders, (
        "no route term is a substring of any other route word any more. If "
        "that is genuinely true the segment rule is cheaper than it looks -- "
        "but check the word list first, because it is far more likely this "
        "test's corpus went stale than that LinkedIn renamed its routes."
    )
    assert "in" in offenders, (
        "the 'in' term is no longer measured as a substring of other route "
        "words. It is the one that took member_profile from 1 to 4 under a "
        "containment classifier."
    )
