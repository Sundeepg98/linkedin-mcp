"""``M C43`` is retired on the FEED-CONTENT-READ-RULING, and may not outlive it.

## THE LAW THIS DISCHARGES

``tests/test_a_retired_row_rests_on_a_live_assertion.py`` states it and this
file is the second instance of it:

    A RULING NOT ATTACHED TO THE ROW IT DECIDES GETS RE-DERIVED.

That file binds six rows to ``FORBIDDEN_PARAMETER_NAMES``. **It cannot hold
this row**: its own docstring says every entry names a parameter in that set,
and ``C43`` rests on a different shipped assertion entirely. A seventh entry
would have broken the invariant that makes that file readable, so this is a
separate file rather than a widened one.

## THE ROW, AND THE RULING

``M C43  Read a post's text``. Retired 2026-09-20 on a ruling made
2026-09-05 and built the same week -- not a new decision by the wave that
moved the row.

The ruling, ``_audit/2026-09-05-lead-rulings-round-two.md`` section 5:

    Reading the feed means reading other people's posts. Ruled: counts and
    relations only, never text or names, built structurally as in 3.

and, in the same section, the reason a filter could not discharge it:

    ``census_substitute`` returns a person's name UNCHANGED ... **No
    shape-based guard will catch a name.** That is why the remedy has to be
    structural rather than a filter.

It was built as ``linkedin_server/feed.py``
(``_audit/2026-09-05-settings-rest.md`` section 1), with the guarantee in the
SIGNATURE rather than in a filter, in both directions.

## WHY THIS ROW AND NOT ANOTHER

``C43`` asks for A POST'S TEXT. That is the exact payload the ruling names and
forbids -- not an adjacent one, not a neighbouring surface. Its TWIN under the
same blocker, ``C74`` *Read your feed*, already left GAP on the same
reasoning; ``C43`` was the half nobody wrote back, which is the propagation
signature ``_audit/2026-09-19-cross-slice-rulings.md`` section 2 names.

**THE REOPENER IS NAMED AND IS NOT A CONSOLATION.** The operator ruling that
a post's text may cross the boundary, shaped, re-opens this row -- the same
mechanism by which dark mode became the one writable setting.

## WHAT IS DELIBERATELY NOT ASSERTED

That the retirement is CORRECT. No test can assert a judgement. What is
asserted is that the retirement and its stated reason cannot be separated: an
editor who puts ``text`` into ``feed._PERMITTED_PARAMETER_NAMES``, or deletes
the OUT-half assertion, has changed the ruling, and this is where they find
out a census row was resting on it.

SHOWN FAILING before admission, three ways, each against a COPY of the census
so no contended file was edited: the state flipped to ``GAP`` (red, naming the
row), the row id deleted (red, naming it missing rather than passing over an
absent row), and ``text`` added to the permitted set (red, naming the
assertion). Recorded in ``_audit/2026-09-20-the-messaging-gap.md``.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from linkedin_server import feed

_CENSUS = (
    pathlib.Path(__file__).resolve().parent.parent
    / "_audit"
    / "_census"
    / "messaging-and-content.md"
)

_ROW = re.compile(r"^\|\s*([CM]\d+)\s*\|[^|]*\|[^|]*\|\s*\*{0,2}([A-Z-]+)\*{0,2}\s*\|")

#: The row, the state its retirement requires, and the one-line why.
ROW_ID = "C43"
REQUIRED_STATE = "EXCLUDED-RULED"

#: Parameter names that would carry a post's TEXT or an author's NAME into a
#: feed reader. The ruling forbids exactly these, and ``feed.py``'s own
#: ``tests/test_feed_tally.py::test_the_permitted_parameter_set_excludes_the_text_vocabulary``
#: asserts the same thing from the module's side. Repeated here because this
#: file must fail for ITS OWN reason -- a row re-opening -- and not only as a
#: casualty of somebody else's test going red.
TEXT_CARRYING_NAMES = frozenset(
    {
        "text", "body", "post_text", "content", "prose", "caption",
        "author", "author_name", "name", "label", "title",
    }
)


def _states() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in _CENSUS.read_text(encoding="utf-8").splitlines():
        found = _ROW.match(line)
        if found is not None:
            out.setdefault(found.group(1), found.group(2))
    return out


def test_the_census_is_readable_at_all() -> None:
    """THE CONTROL. A guard that reads an empty corpus refuses nothing.

    Without this, renaming the slice or reformatting its table would make
    every assertion below pass over zero rows and read as coverage.
    """
    states = _states()
    assert len(states) >= 80, (
        "only %d rows parsed out of %s" % (len(states), _CENSUS.name)
    )
    assert "C1" in states, "the first content row is missing; the reader is not reading"


def test_the_permitted_set_is_readable_at_all() -> None:
    """The second control: the imported set must be non-empty and real."""
    assert feed._PERMITTED_PARAMETER_NAMES
    assert "href" in feed._PERMITTED_PARAMETER_NAMES


def test_the_row_is_present_and_retired() -> None:
    """A row that VANISHED must fail here, not be passed over silently."""
    states = _states()
    assert ROW_ID in states, (
        "%s is not in %s any more. If it was renumbered, this binding has to "
        "move with it; a retirement whose row cannot be found is a retirement "
        "nobody can check." % (ROW_ID, _CENSUS.name)
    )
    assert states[ROW_ID] == REQUIRED_STATE, (
        "%s carries state %r but is retired on the FEED-CONTENT-READ-RULING. "
        "If the row is being re-opened, remove this binding in the same "
        "commit and say which ruling changed."
        % (ROW_ID, states[ROW_ID])
    )


@pytest.mark.parametrize("forbidden", sorted(TEXT_CARRYING_NAMES))
def test_the_ruling_it_rests_on_is_still_shipped(forbidden: str) -> None:
    """The IN half of the ruling, in the signature, as it was built.

    ``feed.py``'s permitted parameter set is the structural form of *never
    text or names*. A name from :data:`TEXT_CARRYING_NAMES` appearing there
    means the ruling has moved, and ``C43`` has to be re-argued rather than
    left retired.
    """
    assert forbidden not in feed._PERMITTED_PARAMETER_NAMES, (
        "%r is now a permitted parameter of a public feed callable. That is a "
        "change to the FEED-CONTENT-READ-RULING, and census row %s is retired "
        "on it." % (forbidden, ROW_ID)
    )


def test_the_out_half_of_the_ruling_is_still_asserted() -> None:
    """The OUT half lives in ``feed.py``'s own suite; this checks it exists.

    Binding to another file's test by NAME is deliberately weak -- it proves
    the assertion is present, not that it passes -- so it is paired with the
    IN half above, which is checked directly against the shipped constant.
    Together they cover both directions of the guarantee the ruling was built
    as.
    """
    suite = (
        pathlib.Path(__file__).resolve().parent / "test_feed_tally.py"
    ).read_text(encoding="utf-8")
    assert "def test_no_public_callable_returns_any_substring_of_its_input" in suite, (
        "the OUT half of the FEED-CONTENT-READ-RULING is no longer asserted "
        "in test_feed_tally.py; census row %s is retired on it" % ROW_ID
    )


def test_the_published_href_is_a_literal_and_not_a_redacted_real_value() -> None:
    """The ruling's shape, not only its scope.

    ``feed.PUBLISHED_HREF`` is the one string the module emits in place of an
    href, and it is deliberately NOT url-shaped so a reader cannot mistake it
    for a redacted real value. If that becomes a url shape, the module has
    started publishing something that looks like content.
    """
    assert "/" not in feed.PUBLISHED_HREF.strip("<>")
    assert "linkedin" not in feed.PUBLISHED_HREF.lower()
