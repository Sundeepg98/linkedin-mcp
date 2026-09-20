"""Coercions that CANNOT CARRY THEIR INPUT OUT, for values a page chose.

## THE DEFECT, STATED ONCE

``int()`` writes the value it refused verbatim into its own exception::

    ValueError: invalid literal for int() with base 10: '<a label from the page>'

That exception escapes the reader, ``server._error`` catches it, and
``config.scrub`` substitutes THIS SERVER'S OWN PATHS and nothing else -- a
person's name has no shape to scrub, so it reaches the caller intact.

    AN INTEGER-ONLY RETURN VALUE DOES NOT MAKE A FUNCTION INTEGER-ONLY,
    BECAUSE AN EXCEPTION IS NOT A RETURN VALUE.

Every reader in this package whose contract is "counts and integers" was
therefore telling the truth about its ``return`` and nothing about its raise.
Measured 2026-09-20 by driving the real readers with a page that answers in
strings: **14 of 115 readers carried a planted name out through a ValueError.**

## WHY THIS MODULE EXISTS RATHER THAN A FOURTEENTH LOCAL FIX

``search_results.py`` was repaired on 2026-09-20 with a private ``_as_int``;
``anchors.py`` and ``collections_page.py`` were filed and left. That is the
shape this repository keeps repeating -- a class repaired one site at a time,
each fix correct and none of them closing anything. A single importable helper
is what lets ``tests/test_readers_emit_no_page_string.py`` hold the property
for readers nobody has written yet.

## THE TWO CONTRACT HALVES, AND LOSING EITHER LOSES THE PROPERTY

:func:`as_int` **never raises and never quotes its input.** The only things it
can return are an integer it was handed and ``None``, so there is no path by
which a string reaches a caller through it -- not as a value, not as a message,
not as an exception argument. A version that raised a *scrubbed* message would
still be wrong: scrubbing is a list of known shapes, and the whole finding is
that a name has none.

``bool`` is refused deliberately. ``True`` is an ``int`` in Python, so a
permissive check would report a count of ``True`` results, which is a reading
nobody took.

## THE SUBSTITUTION IS COUNTED OR LOGGED, NEVER SILENT

A reader that cannot say why it is empty is the green this repository distrusts
most, so a refused value is always announced:

* :func:`counts_only` returns HOW MANY entries it substituted, for callers that
  publish a refusal count (``search_results`` does);
* :func:`as_count` logs the refusal for callers whose output schema is already
  fixed and cannot grow a field without changing a tool's contract.

**THE LOG LINE NAMES THE TYPE AND NEVER THE VALUE.** Logging the value would
reintroduce the exact defect one layer over -- a log record is another way out
of the process, and ``leakwalk.assert_no_leak`` takes a ``caplog`` for exactly
that reason.

## POSITION IS A MEANING, SO A REFUSED ENTRY IS SUBSTITUTED AND NEVER DROPPED

:func:`counts_only` keeps the list the same length. Several callers align their
lists positionally against a closed alphabet -- ``anchors.ROUTE_CLASSES``,
``search_results.RESULT_KINDS`` -- where index 0 is the hazard class
(``member_profile``, ``person_result``). Dropping one entry renames every kind
behind it, which is precisely the silent rename ``term_for`` refuses to commit
by never clamping. Arriving one function earlier does not make it acceptable.
"""

from __future__ import annotations

from typing import Any, Iterable, Optional

from linkedin_server.config import logger


def as_int(value: Any) -> Optional[int]:
    """An integer, or ``None``. IT NEVER RAISES AND NEVER QUOTES ITS INPUT.

    Both halves are the contract; see the module docstring for why each one is
    load-bearing. The only things this can return are an integer it was handed
    and ``None``, so it can carry nothing out.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def as_count(value: Any, default: int = 0) -> int:
    """An integer for a caller whose output schema cannot grow a field.

    The mechanical replacement for ``int(<something> or 0)`` at a site where
    ``<something>`` came off a page. Same answer as the shipped code on every
    input that shipped code handled, and a LOGGED SUBSTITUTION instead of a
    raised string on the input it did not.

    The log names ``type(value).__name__`` and never ``value``. A log record is
    another way out of the process, so the redaction rule that applies to a
    return value applies here unchanged.
    """
    number = as_int(value)
    if number is None:
        if value is not None:
            logger.warning(
                "a page value that should have been a number was a %s; "
                "substituted %d (the value is not logged, by design)",
                type(value).__name__,
                default,
            )
        return default
    return number


def counts_only(
    values: Any, default: int = 0
) -> tuple[list[int], int]:
    """Position-preserving integers, and how many entries were not integers.

    A NON-INTEGER IS SUBSTITUTED, NEVER DROPPED -- see the module docstring for
    what dropping one costs. The substitution is COUNTED, so a page answering
    with something other than a number becomes a VISIBLE INTEGER rather than a
    silent shift or a raised string.

    A non-sequence is reported as one refusal rather than as an empty reading,
    because "the page sent something that is not a list" and "the page sent an
    empty list" are different answers.
    """
    if isinstance(values, (str, bytes)) or not isinstance(values, Iterable):
        return [], 0 if values is None else 1
    out: list[int] = []
    refused = 0
    for value in values:
        number = as_int(value)
        if number is None:
            refused += 1
            number = default
        out.append(number)
    return out, refused


def scalars_only(
    raw: Any, names: tuple[tuple[str, str], ...]
) -> tuple[dict[str, int], int]:
    """``{output name: integer}``, and how many values were not integers.

    ABSENT IS NOT THE SAME AS WRONG, and they are counted differently. A key
    the page never set reads 0 and is NOT counted -- that is the shipped
    ``or 0`` behaviour and it means "I was not told". A key set to something
    that is not an integer IS counted, because that is the page answering with
    a string, and a string from this page is a name until shown otherwise.
    """
    source = raw if isinstance(raw, dict) else {}
    out: dict[str, int] = {}
    refused = 0
    for output_name, key in names:
        value = source.get(key)
        number = as_int(value)
        if number is None:
            if value is not None:
                refused += 1
            number = 0
        out[output_name] = number
    return out, refused
