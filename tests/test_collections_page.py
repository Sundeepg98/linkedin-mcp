"""``collections_page`` publishes its own literals and cannot publish a label.

The properties asserted here are the ones the module's docstring claims, because
a property stated only in prose is the defect this repository has recorded more
than once. Three of them are STRUCTURAL -- a signature, an order and a closed
alphabet -- and a structural property is the only kind a future edit cannot
quietly forget.

SHOWN FAILING before admission, against COPIES of the module's own constants so
no contended file was edited. Recorded in ``_audit/2026-09-19-read-tail.md``.
"""

from __future__ import annotations

import inspect

import pytest

from linkedin_server import collections_page


#: Parameter names whose VALUE would be a page string. None may appear on any
#: function here except the reader's documented control path.
_LABEL_SHAPED = frozenset(
    {"label", "labels", "name", "names", "text", "heading", "headings", "title"}
)


def test_the_module_is_readable_at_all() -> None:
    """The control. A guard over an empty module refuses nothing."""
    assert len(collections_page.GROUPINGS) == 5
    assert callable(collections_page.tally)
    assert callable(collections_page.term_for)
    assert callable(collections_page.read_collections)


def test_no_label_is_a_parameter_of_any_publishing_function() -> None:
    """The structural property, asserted on ``inspect.signature``.

    ``groups.py``'s rule, copied with its reason: a reader that is never handed
    a name cannot leak one, whatever LinkedIn calls a grouping tomorrow. A
    filter has to keep up; an absent parameter does not.
    """
    for name in ("tally", "term_for", "emitted_alphabet", "control_fixture"):
        signature = inspect.signature(getattr(collections_page, name))
        offenders = _LABEL_SHAPED & set(signature.parameters)
        assert not offenders, (
            f"collections_page.{name} takes {sorted(offenders)}, which is a "
            "page string by any other name. Everything a caller publishes must "
            "take INDICES."
        )


def test_the_readers_only_string_parameter_is_the_documented_control_path() -> None:
    """``read_collections(page, html="")`` -- and ``html`` is not a reading.

    Asserted rather than trusted, because it is the one string parameter in
    the module and the whole safety argument depends on it being a CONTROL
    input and not a page's text arriving by another route.
    """
    signature = inspect.signature(collections_page.read_collections)
    assert list(signature.parameters) == ["page", "html"], (
        "read_collections' signature changed. Its second parameter is the "
        "detached-container CONTROL path; a third string parameter would need "
        "its own argument about what may cross the boundary."
    )
    assert not (_LABEL_SHAPED & set(signature.parameters))
    assert "control" in (collections_page.read_collections.__doc__ or "").lower()


def test_the_vocabulary_order_is_the_contract() -> None:
    """The page returns a POSITION in this tuple, so reordering renames readings.

    This is not a style pin. An index taken today and mapped tomorrow against a
    reordered tuple silently reports one grouping as another, and a census built
    on it would be wrong in a way nobody could see.
    """
    assert collections_page.GROUPINGS == (
        "domains",
        "industries",
        "company benefits",
        "editorial",
        "corporate commitments",
    )


def test_out_of_range_is_REFUSED_and_never_clamped() -> None:
    """A clamp would rename a grouping. It refuses with a literal instead."""
    assert collections_page.term_for(-1) == collections_page.UNMATCHED
    assert collections_page.term_for(0) == "domains"
    assert collections_page.term_for(4) == "corporate commitments"
    for out_of_range in (5, 99, -7):
        assert collections_page.term_for(out_of_range) == "index_out_of_range", (
            f"term_for({out_of_range}) must refuse. A clamp to the nearest "
            "valid index would silently rename one grouping to another."
        )


def test_the_output_alphabet_is_closed_over_adversarial_input() -> None:
    """Every string ``tally`` can emit is a literal of this module.

    Run over indices no page would produce, because the claim is about what
    the function CAN emit rather than what it usually does.
    """
    adversarial = [-99, -1, 0, 1, 2, 3, 4, 5, 500]
    result = collections_page.tally(adversarial, [1] * len(adversarial))
    emitted = set(result["by_term"]) | set(result["cards_by_term"])
    allowed = collections_page.emitted_alphabet()
    assert emitted <= allowed, (
        f"tally emitted {sorted(emitted - allowed)}, which is not in the "
        "module's own alphabet. Every publishable string must be a literal "
        "defined here -- that is the safety property."
    )


def test_a_zero_card_count_is_not_an_absent_one() -> None:
    """Collapsing them is how a reader reports 'nothing' when it means 'I could
    not see'. ``cards`` shorter than ``indices`` counts as UNKNOWN, not zero.
    """
    short = collections_page.tally([0, 1, 2], [7])
    assert short["sections_with_unknown_cards"] == 2
    assert short["cards_by_term"] == {"domains": 7}
    full = collections_page.tally([0, 1], [7, 0])
    assert full["sections_with_unknown_cards"] == 0
    assert full["cards_by_term"] == {"domains": 7, "industries": 0}


def test_the_control_fixture_would_match_every_grouping_and_one_decoy() -> None:
    """The positive control's INPUT, asserted offline.

    The fixture is run through the real in-page matcher during a live read --
    measured 2026-09-19: **5 matched, 1 unmatched**. This asserts the fixture
    itself still contains what that demonstration depends on, so the control
    cannot rot into one that matches nothing and passes silently.
    """
    fixture = collections_page.control_fixture()
    for term in collections_page.GROUPINGS:
        assert term.title() in fixture, (
            f"the control fixture no longer contains {term!r}. A positive "
            "control that cannot fire is worse than none."
        )
    assert "Saved searches" in fixture, (
        "the fixture's DECOY heading is gone. Without it the control proves "
        "the matcher matches, but not that it discriminates."
    )


def test_the_control_has_an_expectation_and_it_predicts_the_decoy() -> None:
    """The fixture is held to a WRITTEN prediction, not only to its own input.

    **THIS MODULE SHIPPED WITHOUT ONE UNTIL 2026-09-21.** Its three siblings --
    ``anchors``, ``search_results`` (twice) and ``company_root`` -- each wrote
    down what their fixture must produce. This one did not, and the test above
    is why the gap was invisible: it asserts the fixture still CONTAINS the
    right strings, which is a claim about the input. Nothing said what the
    output had to be, so once the fixture was finally driven through a real
    engine there was nothing for the result to disagree with.

    ``UNMATCHED`` IS THE ENTRY THAT MATTERS. Five matches is also the shape a
    matcher that salutes every heading makes; the decoy is what separates them,
    so it is PREDICTED here rather than merely present in the fixture.
    """
    expectation = collections_page.CONTROL_EXPECTATION

    for term in collections_page.GROUPINGS:
        assert expectation.get(term) == 1, (
            f"{term!r} is missing from the expectation, so the control makes "
            "no prediction about it."
        )
    assert expectation.get(collections_page.UNMATCHED) == 1, (
        "the expectation does not predict the DECOY. Without that entry a "
        "matcher that matched everything it was shown would satisfy it."
    )
    assert set(expectation) == set(collections_page.GROUPINGS) | {
        collections_page.UNMATCHED
    }, (
        "the expectation names something the fixture cannot produce, or has "
        "stopped naming something it can."
    )


def test_THIS_CONTROL_CAN_FAIL_a_saluting_matcher_satisfies_a_decoyless_table() -> None:
    """The partner red, and it convicts the expectation rather than the code.

    A matcher that returns the FIRST grouping for every heading it is shown is
    broken in the way this surface's zero-reading scar was about. Scored
    against the shipped expectation it fails. Scored against the same table
    with the decoy entry removed -- the version this module shipped with, in
    effect, by shipping no table at all -- it is indistinguishable from a
    working one on the count that would have been checked.
    """
    # Six headings, and a saluting matcher calls all six the first grouping.
    first = collections_page.GROUPINGS[0]
    saluted = collections_page.tally([0] * 6)["by_term"]

    assert saluted.get(collections_page.UNMATCHED, 0) == 0, (
        "a saluting matcher leaves nothing unmatched -- that is the tell"
    )
    assert saluted.get(first) == 6

    decoyless = {
        term: count
        for term, count in collections_page.CONTROL_EXPECTATION.items()
        if term != collections_page.UNMATCHED
    }
    assert saluted != collections_page.CONTROL_EXPECTATION
    assert (
        saluted.get(collections_page.UNMATCHED, 0)
        != collections_page.CONTROL_EXPECTATION[collections_page.UNMATCHED]
    ), "the decoy entry is what the saluting matcher fails on"
    assert collections_page.UNMATCHED not in decoyless


@pytest.mark.parametrize(
    "mutation,expected",
    [
        (("industries", "domains", "company benefits", "editorial",
          "corporate commitments"), "domains"),
        (("editorial", "industries", "company benefits", "domains",
          "corporate commitments"), "domains"),
    ],
)
def test_this_guard_can_fail_a_reordering_renames_a_reading(
    mutation: tuple, expected: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """SHOWN FAILING: index 0 means a different grouping under a reorder.

    The mutation is applied with ``monkeypatch`` to a COPY of the constant, so
    no file is edited and the demonstration costs no staging window. It asserts
    the SPECIFIC harm rather than that something changed: the same index now
    resolves to a different term, which is exactly the silent rename the order
    pin exists to prevent.
    """
    assert collections_page.term_for(0) == expected
    monkeypatch.setattr(collections_page, "GROUPINGS", mutation)
    assert collections_page.term_for(0) != expected, (
        "a reordered vocabulary did NOT change what index 0 resolves to, "
        "which would mean the order pin is guarding nothing"
    )
