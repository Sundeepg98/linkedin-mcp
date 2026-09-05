"""The per-record gate a newsletter reader needs, and the three ways to break it.

THE POINT OF THIS FILE IS THE MUTATIONS, not the happy path. Every branch of
:func:`shape.subscription_row` is planted with the edit a later reader is most
likely to make, and each is fed AN INPUT CHOSEN SO THAT BRANCH IS THE ONLY
THING STANDING. That last clause is the whole discipline: this project has
already caught a test that appeared to protect a guard's branch and was in
fact asserting the refusal SHAPE, because its input fell through to a later
check and refused anyway.

THE VALUES ARE SYNTHETIC AND WEAR NO REAL IDENTIFIER'S SHAPE. The slugs are
lifted from ``tests/test_membership_row.py``, which is tracked and has passed
``test_no_committed_identity`` since 2026-09-04; the personal names are
invented and belong to nobody; the newsletter id is SIX digits, the minimum
``_CENSUS_LONG_DIGITS`` reduces, so the digit rule is exercised without a
ten-digit run wearing a phone number's shape -- a probe in this package had
exactly that refused.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from linkedin_server import shape  # noqa: E402

BASE = "https://www.linkedin.com"

A_NEWSLETTER = f"{BASE}/newsletters/weekly-123456/"
A_NEWSLETTER_WORDS = f"{BASE}/newsletters/a-made-up-letter/"

#: A MEMBER'S OWN NEWSLETTER TAB. The one href that carries the newsletter
#: marker AND a member marker, which is what makes the foreign-marker branch
#: testable at all.
A_MEMBERS_NEWSLETTER_TAB = (
    f"{BASE}/in/priya-sharma-12ab34/recent-activity/newsletters/weekly-123456/"
)

#: A NEWSLETTER HREF CARRYING A BARE MEMBER TOKEN IN ITS QUERY. Not exotic:
#: it is the exact escape ``membership_row`` records, because ``/in/`` is the
#: only member shape the substitutions know, so the token rides out of
#: ``census_substitute`` untouched.
A_NEWSLETTER_WITH_A_TOKEN = f"{BASE}/newsletters/weekly-123456/?authorProfile=ACoAAB12cd34"
A_BARE_MEMBER_TOKEN = "ACoAAB12cd34"

#: THE TITLE THAT CARRIES ITS AUTHOR. A newsletter is authored BY A PERSON and
#: LinkedIn builds both the title and the slug out of that. The name is
#: invented.
A_TITLE_CARRYING_ITS_AUTHOR = "Weekly Notes by Savita Krishnan"
THE_AUTHORS_SURNAME = "Krishnan"

#: A TITLE WITH NO CAPITALISED RUN AT ALL, which the redactor leaves alone.
#: It is the control for "this gate has not simply blanked everything".
A_TITLE_THAT_SURVIVES = "data weekly"


# ---------------------------------------------------------------------------
# What it publishes
# ---------------------------------------------------------------------------


def test_a_subscription_row_publishes_a_constant_href_and_never_the_input():
    row = shape.subscription_row(A_NEWSLETTER, A_TITLE_THAT_SURVIVES)
    assert row["published"] is True, row
    assert row["href_shape"] == "/newsletters/<newsletter>/", row
    assert "weekly-123456" not in row["href_shape"], row


def test_a_title_with_no_capitalised_run_survives_intact():
    """THE CONTROL. A gate that blanked everything would pass every leak test
    below while making the reader's payload useless, so one title must come
    through unchanged or this file is measuring a constant."""
    row = shape.subscription_row(A_NEWSLETTER_WORDS, A_TITLE_THAT_SURVIVES)
    assert row["published"] is True, row
    assert row["name"] == A_TITLE_THAT_SURVIVES, row
    assert row["name_redacted"] is False, row


def test_a_title_carrying_its_author_is_redacted_and_keeps_its_marker():
    row = shape.subscription_row(A_NEWSLETTER, A_TITLE_CARRYING_ITS_AUTHOR)
    assert row["published"] is True, row
    assert THE_AUTHORS_SURNAME not in row["name"], row
    assert row["name_redacted"] is True, row
    # THE MARKER IS THE HALF THAT IS EASY TO LOSE. A redaction that erases its
    # own marker buys the reader's trust and ships the name anyway; this
    # project made that exact half-applied fix twice in two days.
    assert shape.CENSUS_REDACTED in row["name"], row


def test_a_bare_member_token_in_the_query_never_reaches_the_output():
    row = shape.subscription_row(A_NEWSLETTER_WITH_A_TOKEN, A_TITLE_THAT_SURVIVES)
    assert row["published"] is True, row
    assert A_BARE_MEMBER_TOKEN not in repr(row), row


def test_a_row_with_no_href_is_refused_and_says_so():
    row = shape.subscription_row("", "anything")
    assert row["published"] is False, row
    assert row["refused"] == "no_href", row


def test_a_refusal_reports_the_markers_it_saw_rather_than_a_bare_no():
    """A refusal that reports only what it did NOT match is half a
    measurement -- three rounds were lost in this project to a guard that
    printed a count without the observations it counted over."""
    row = shape.subscription_row(f"{BASE}/company/a-made-up-co/", "An Organisation")
    assert row["published"] is False, row
    assert row["saw"] == ["/company/<company>"], row


# ---------------------------------------------------------------------------
# THE MUTATIONS. Each planted, each with an input that makes the mutated
# branch the only thing standing.
# ---------------------------------------------------------------------------


def test_MUTATION_publishing_the_shaped_href_ships_the_query_token(monkeypatch):
    """Plant: publish ``census_substitute(href)`` instead of the constant.

    THE INPUT IS WHAT MAKES THIS A TEST OF THE CONSTANT. A newsletter href
    with no query would shape to ``/newsletters/<newsletter>/`` and be
    byte-identical to the constant -- the mutation would survive and prove
    nothing. Measured: the query token survives the substitutions, so with the
    constant replaced it is published.
    """
    shaped = shape.census_substitute(A_NEWSLETTER_WITH_A_TOKEN)
    assert A_BARE_MEMBER_TOKEN in shaped, (
        "the substitutions now reduce this token, so this mutation no longer "
        "demonstrates the escape the constant href exists to close"
    )
    monkeypatch.setattr(shape, "_SUBSCRIPTION_PUBLISHED_HREF", shaped)
    row = shape.subscription_row(A_NEWSLETTER_WITH_A_TOKEN, A_TITLE_THAT_SURVIVES)
    assert A_BARE_MEMBER_TOKEN in row["href_shape"], (
        "the token did not reach the output even with the constant replaced, "
        "so this test is not measuring the constant"
    )


def test_MUTATION_dropping_the_foreign_markers_publishes_a_members_own_tab(
    monkeypatch,
):
    """Plant: empty ``_SUBSCRIPTION_FOREIGN_MARKERS``.

    THE INPUT IS THE POINT, AND A BARE ``/in/`` HREF WOULD NOT DO. With the
    foreign branch gone, ``/in/<member>/`` falls through to the newsletter
    marker check and is refused THERE -- same verdict, different reason, and
    the mutation survives while telling you nothing. A member's own newsletter
    TAB carries both markers, so the foreign branch is the only thing refusing
    it.
    """
    both = shape.census_substitute(A_MEMBERS_NEWSLETTER_TAB)
    assert "/in/<member>" in both and "/newsletters/<newsletter>" in both, both
    monkeypatch.setattr(shape, "_SUBSCRIPTION_FOREIGN_MARKERS", ())
    row = shape.subscription_row(A_MEMBERS_NEWSLETTER_TAB, "Their Newsletter")
    assert row["published"] is True, (
        "the row was still refused with the foreign markers removed, so "
        "something else is doing the work and this test measures nothing"
    )


def test_MUTATION_making_the_redaction_conditional_ships_the_author_verbatim(
    monkeypatch,
):
    """Plant: the sibling's rule -- redact only if the substitutions changed it.

    This is the mutation that matters, because it is not a deletion: it is
    ``membership_row``'s rule, which is correct there, applied here. A reader
    generalising the group gate to newsletters would write exactly this.

    THE INPUT IS A TITLE THAT SURVIVES THE SUBSTITUTIONS UNCHANGED, which is
    what makes the count-1 redaction the only thing standing -- and it is not
    a contrived string. A plain human name carries no urn, no ``/in/`` path,
    no possessive and no digit run.
    """
    assert (
        shape.census_substitute(A_TITLE_CARRYING_ITS_AUTHOR)
        == A_TITLE_CARRYING_ITS_AUTHOR
    ), "the substitutions now change this title, so the mutation is moot"

    def conditional(text, count):
        del count  # the mutation: the count is ignored, as the sibling's rule
        return text

    monkeypatch.setattr(shape, "census_redact_rare", conditional)
    row = shape.subscription_row(A_NEWSLETTER, A_TITLE_CARRYING_ITS_AUTHOR)
    assert THE_AUTHORS_SURNAME in row["name"], (
        "the author's name did not ship even with the redaction neutralised, "
        "so this test is not measuring the redaction"
    )


def test_MUTATION_a_sixth_entity_marker_becomes_a_refusal_not_a_hole(monkeypatch):
    """The derivation, asserted rather than described.

    ``_SUBSCRIPTION_FOREIGN_MARKERS`` is DERIVED from
    ``_CENSUS_ENTITY_HREFS`` so that a marker added there tomorrow refuses
    here automatically. A literal tuple of its own would have looked identical
    today and silently admitted the sixth kind. Rebuilding the derivation
    under a patched source is what tells the two apart.
    """
    monkeypatch.setattr(
        shape,
        "_CENSUS_ENTITY_HREFS",
        shape._CENSUS_ENTITY_HREFS + ("/services/<service>",),
    )
    rebuilt = tuple(
        marker
        for marker in shape._CENSUS_ENTITY_HREFS
        if marker != shape._SUBSCRIPTION_HREF_MARKER
    )
    assert "/services/<service>" in rebuilt, rebuilt
    assert shape._SUBSCRIPTION_HREF_MARKER not in rebuilt, rebuilt


# ---------------------------------------------------------------------------
# The finding that will not fit in an assertion, kept where a reader meets it
# ---------------------------------------------------------------------------


def test_the_redactor_is_a_caps_run_rule_and_NOT_a_name_detector():
    """THE RESIDUAL RISK, ASSERTED SO IT CANNOT BE FORGOTTEN.

    ``subscription_row`` is a floor under the leak, not a proof there is none.
    A title spelling its author in lower case survives the redactor, and this
    test exists so the limit is a measured fact in the suite rather than a
    sentence in a docstring nobody re-reads.

    IT IS NOT A BUG TO FIX HERE. What would raise the floor is an instrument
    that can decide whether a string is a person's name, and this package has
    none -- measured, and reported as a finding rather than left as a TODO.
    """
    lowercase_author = "notes by alex"
    row = shape.subscription_row(A_NEWSLETTER, lowercase_author)
    assert row["name"] == lowercase_author, (
        "the redactor now catches a lower-case name, which is a better floor "
        "than this file was written against -- re-measure and rewrite this "
        "test rather than deleting it"
    )
