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
