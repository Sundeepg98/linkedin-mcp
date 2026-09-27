"""The controls of ``tests/record_typed.py``, the reading the former "no name
parameter" tests apply since 2026-09-27.

Eight tests in seven files ask it, each over its own module and vocabulary:
``test_membership_tally``, ``test_the_groups_tool_keeps_its_properties``,
``test_search_results``, ``test_anchors``, ``test_company_root``,
``test_group_page``, ``test_recommendation_tally`` and ``test_feed_tally``. On
the real tree every one of those modules takes no identity-named parameter at
all, so their green says nothing about the rule's two halves. These plants do:
an identity-named parameter is refused as a bare string, unannotated, as
``Any``, as a list of strings and as an annotation that cannot be resolved, and
admitted only as a people record -- alone, in a container, or optional.
"""

from __future__ import annotations

from typing import Any, Iterable, List, Optional, Sequence

import pytest

from linkedin_server import people_data
from tests.record_typed import (
    RECORD_TYPES,
    identity_parameters_outside_a_record,
    is_record_annotation,
)

IDENTITY = {"name", "names", "person", "people", "viewer", "title", "member"}


def bare(name: str, member: Any, person, title: List[str]) -> None:
    """Every identity-named parameter here is refused."""


def recorded(
    viewer: people_data.Person,
    people: list[people_data.Person],
    names: Optional[people_data.Person],
    title: Sequence[people_data.Group],
    member: tuple[people_data.Person, ...],
    count: int,
) -> None:
    """Every identity-named parameter here is a record, and ``count`` is not
    named like an identity at all."""


def unresolvable(person: "NoSuchRecord") -> None:  # noqa: F821 - on purpose
    """A forward reference to nothing: resolution fails, so it fails closed."""


def test_a_bare_identity_parameter_is_refused_in_every_spelling():
    assert identity_parameters_outside_a_record(bare, IDENTITY) == [
        "name", "member", "person", "title",
    ]


def test_a_record_typed_identity_parameter_is_admitted():
    assert identity_parameters_outside_a_record(recorded, IDENTITY) == []


def test_an_annotation_that_cannot_be_resolved_fails_closed():
    assert identity_parameters_outside_a_record(unresolvable, IDENTITY) == ["person"]


def test_a_predicate_vocabulary_matches_as_the_old_substring_tests_did():
    """``test_membership_tally`` matched ``"name" in parameter``; the
    predicate form keeps that, so ``author_name`` is still caught."""

    def planted(author_name: str, first_name: people_data.Person) -> None:
        pass

    assert identity_parameters_outside_a_record(planted, lambda p: "name" in p) == [
        "author_name"
    ]


@pytest.mark.parametrize(
    "annotation, expected",
    [
        (people_data.Person, True),
        (people_data.Group, True),
        (people_data.Event, True),
        (list[people_data.Person], True),
        (Iterable[people_data.Event], True),
        (Optional[people_data.Group], True),
        (str, False),
        (Any, False),
        (list[str], False),
        (Optional[str], False),
        (dict, False),
        (None, False),
    ],
    ids=lambda value: getattr(value, "__name__", str(value)),
)
def test_is_record_annotation_on_each_shape(annotation, expected):
    assert is_record_annotation(annotation) is expected


def test_a_class_that_only_compares_equal_to_a_record_is_not_one():
    """Found by lane G's cold verification (2026-09-27): containment compared
    with ``==``, so a ``str`` subclass whose metaclass says it equals anything
    was admitted as a record. Contrived, and closed by comparing identity."""

    class _EqualToEverything(type):
        def __eq__(cls, other: object) -> bool:
            return True

        __hash__ = type.__hash__

    class LooksLikeARecord(str, metaclass=_EqualToEverything):
        pass

    assert LooksLikeARecord in RECORD_TYPES  # the trap, still set
    assert is_record_annotation(LooksLikeARecord) is False


def test_the_record_types_are_the_people_data_ones():
    assert set(RECORD_TYPES) == {people_data.Person, people_data.Group, people_data.Event}
