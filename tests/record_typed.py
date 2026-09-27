"""A NAME ENTERS A SHAPER ONLY AS A PEOPLE RECORD -- the one reading every
former "no name parameter" test applies.

THE DOCTRINE THOSE TESTS HELD. The name-free readers and shapers -- ``groups``,
``anchors``, ``search_results``, ``company_root``, ``group_page``,
``recommendations``, ``feed`` -- were each held by a STRUCTURAL test that no
function in the module takes a parameter named like a name, an address or a
needle: "a reader never handed a name cannot leak one."

WHY IT MOVED. NAMES-AT-RUNTIME (the operator, 2026-09-24) amended the
name-free doctrine for what a read RETURNS, and PEOPLE-DATA-MITIGATIONS says
how a person, a group or an event now crosses: as a
``linkedin_server.people_data`` record -- sanitised, capped, marked. The
orchestrator's order for those tests: "rewritten around the record type, not
deleted. Keep them structural."

SO EACH OF THEM ASKS ONE QUESTION MORE PRECISELY, off the same signature: a
parameter NAMED like a person or an identity is refused UNLESS its ANNOTATION
says it is a people record -- ``Person``, ``Group`` or ``Event``, or a list,
tuple, set, sequence or iterable of them, or an optional one. Everything else
those tests refused stays refused outright, because no record type carries it:
a NEEDLE (a query, keywords, a search term) and PAGE TEXT (a label, a body).

THE LIMITS, plainly:

* It reads ANNOTATIONS, not values. A parameter annotated as a record and
  handed a string at runtime passes here; the record classes refuse an
  unsanitised value at construction, which is the other half.
* An annotation that cannot be resolved -- a forward reference to a name the
  module does not bind -- counts as NOT a record, so it fails closed.
* The vocabulary of what is "named like an identity" is each test's own,
  unchanged by the rewrite; a synonym outside it passes, as it did before.
"""

from __future__ import annotations

import collections.abc
import inspect
import types
import typing
from typing import Any, Callable, Iterable, Union

from linkedin_server import people_data

#: The record classes, from the module that defines them.
RECORD_TYPES: tuple[type, ...] = tuple(people_data.RECORD_TYPES)

#: Containers a record may arrive in, as ``typing.get_origin`` spells them.
_CONTAINERS = (
    list,
    tuple,
    set,
    frozenset,
    collections.abc.Sequence,
    collections.abc.Iterable,
    collections.abc.Collection,
)

_UNIONS: tuple[Any, ...] = (Union, getattr(types, "UnionType", Union))


def is_record_annotation(annotation: Any) -> bool:
    """Is ``annotation`` a people record, a container of them, or an optional one?"""
    if isinstance(annotation, type) and annotation in RECORD_TYPES:
        return True
    origin = typing.get_origin(annotation)
    members = [a for a in typing.get_args(annotation) if a is not Ellipsis]
    if origin in _UNIONS:
        members = [a for a in members if a is not type(None)]
    elif origin not in _CONTAINERS:
        return False
    return bool(members) and all(is_record_annotation(a) for a in members)


def _hints(function: Callable[..., Any]) -> dict[str, Any]:
    """Resolved annotations, or none at all when resolution fails -- which
    makes every identity-named parameter count as not a record."""
    try:
        return typing.get_type_hints(function)
    except Exception:  # noqa: BLE001 - failing closed is the point
        return {}


def identity_parameters_outside_a_record(
    function: Callable[..., Any], identity: Union[Iterable[str], Callable[[str], bool]]
) -> list[str]:
    """The parameters of ``function`` NAMED like an identity whose annotation
    is not a people record. ``identity`` is a set of exact names or a
    predicate on a name (a test that matched a substring keeps doing so)."""
    matches = identity if callable(identity) else frozenset(identity).__contains__
    hints = _hints(function)
    return [
        name
        for name in inspect.signature(function).parameters
        if matches(name) and not is_record_annotation(hints.get(name))
    ]
