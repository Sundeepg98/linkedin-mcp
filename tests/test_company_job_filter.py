"""The company job filter, and the assertion the whole module exists for.

The load-bearing test here is not that a good id produces a good parameter --
that one would pass against almost any implementation. It is
``test_a_refused_value_does_not_survive_into_the_refusal``: the most probable
wrong input for ``f_C`` is a company SLUG, and a slug is a third-party
organisation's name. An implementation that follows this package's usual
"name what you saw" rule publishes that name on every such call.

Each assertion below was shown failing against a planted mutation before being
admitted; ``_audit/2026-09-05-cheap-reads.md`` records which mutation killed
which test.
"""

from __future__ import annotations

import pytest

from linkedin_server import jobfilter


# A shape, not an instance. This is not any real company: it is two invented
# words chosen so that every character class the refusal could leak is present
# -- letters, a hyphen, and digits -- and so that a substring search for it
# cannot collide with ordinary English in the refusal text.
A_SLUG_SHAPED_VALUE = "zzqqx-widgetworks7"


def test_a_numeric_id_resolves_to_the_f_c_pair() -> None:
    verdict = jobfilter.company_filter_param("5417062")
    assert verdict["state"] == "resolved"
    assert verdict["param"] == ("f_C", "5417062")


def test_an_empty_value_is_absent_and_not_an_error() -> None:
    """The filter is optional, and 'no filter' must not read as a failure.

    Collapsing ABSENT into REFUSED would delete the vocabulary needed to tell
    "the caller did not ask for a company filter" from "the caller asked for
    one and got it wrong" -- two states a caller handles differently.
    """

    for nothing in ("", "   ", None):
        verdict = jobfilter.company_filter_param(nothing)  # type: ignore[arg-type]
        assert verdict["state"] == "absent", nothing
        assert verdict["param"] is None, nothing


def test_a_slug_is_refused() -> None:
    verdict = jobfilter.company_filter_param(A_SLUG_SHAPED_VALUE)
    assert verdict["state"] == "refused"
    assert verdict["param"] is None


def test_a_refused_value_does_not_survive_into_the_refusal() -> None:
    """THE ASSERTION THIS MODULE EXISTS FOR.

    The input is chosen so that the refused branch is the ONLY thing standing
    between the value and the output -- the lesson from a mutation that survived
    earlier today because the test's input fell through to a later check and
    refused anyway. Here, if the refusal quotes its input at all, this fails.

    It checks the WHOLE verdict rather than only ``why``, because a value
    leaking through some other key would be the same leak wearing a different
    field name.
    """

    verdict = jobfilter.company_filter_param(A_SLUG_SHAPED_VALUE)
    rendered = repr(verdict)

    assert A_SLUG_SHAPED_VALUE not in rendered
    # And not by lowercasing or partial quoting either. "zzqqx" is the
    # distinctive stem; if any part of the supplied name reaches the output the
    # redaction is not a redaction.
    assert "zzqqx" not in rendered.lower()
    assert "widgetworks" not in rendered.lower()


def test_the_refusal_still_says_what_it_saw() -> None:
    """Not quoting the value is not licence to say nothing about it.

    A refusal that reports only what it did NOT match is half a measurement --
    the scar that cost this package three rounds. The shape must be there.
    """

    why = jobfilter.company_filter_param(A_SLUG_SHAPED_VALUE)["why"]
    assert str(len(A_SLUG_SHAPED_VALUE)) in why
    assert "letters" in why
    assert "hyphen" in why


def test_describe_shape_is_reachable_on_its_own() -> None:
    """The detector is factored OUT of the assertion that consumes it.

    Logic inside an ``assert`` has no handle and can never be aimed at a
    known-bad sample. This is the handle.
    """

    described = jobfilter.describe_shape("abc-123")
    assert "7 characters" in described
    assert "digits" in described and "letters" in described
    assert "abc" not in described


@pytest.mark.parametrize("value", ["54170 62", "5417062x", "-5417062", "5.417062"])
def test_values_that_are_only_nearly_digits_are_refused(value: str) -> None:
    """``str.isdigit`` is the guard; these are the inputs that probe its edges.

    A whitespace-bearing or sign-bearing value would otherwise be url-encoded
    into ``f_C`` and produce a search filtered by nothing, which fails as an
    empty result set rather than as an error.
    """

    assert jobfilter.company_filter_param(value)["state"] == "refused"


def test_an_absurdly_long_run_of_digits_is_refused() -> None:
    assert jobfilter.company_filter_param("1" * 40)["state"] == "refused"
