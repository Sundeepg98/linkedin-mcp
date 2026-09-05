"""``groups`` -- the name-free membership reader, and the ruling it implements.

WHAT IS BEING TESTED IS AN ABSENCE, which is the hard case. The safety claim of
``linkedin_server/groups.py`` is that **no name is a parameter of any function
in it**, so the first test here reads the signatures rather than the behaviour.
A property asserted only in a docstring is the defect this repository has named
repeatedly; this file is the enforceable form of that sentence.

## THE INPUTS ARE CHOSEN FROM THE BRANCH STRUCTURE, NOT FROM A MODEL OF THE RISK

Measured in this project on 2026-09-05 and written into the freeze ruling: a
planted mutation that deletes a guard's branch may fail to kill the test named
for that branch, because the test's input FALLS THROUGH to a later check and
still refuses. The refusal shape is asserted and the branch is not.

    When a mutation survives, do not enlarge the mutation. Ask which input
    would make that branch the only thing standing.

So each refusal below is exercised with an input where the branch under test is
the ONLY thing refusing, and the survival-critical one -- the numeric rule -- is
given a slug carrying a person's name, which every other branch in the function
lets through.

## NO REAL IDENTIFIER IS TYPED INTO THIS FILE

Group ids on his own page were measured at 5, 6, 7 and 8 digits. Six or more is
exactly the shape ``census_substitute`` treats as an identifier and
``test_no_committed_identity`` refuses in a tracked file, so **every long run
here is BUILT AT RUNTIME rather than typed** -- and the one literal id is five
digits, which is a length his own page actually carries, so it is a realistic
shape rather than a value ducking under a threshold.

That is not hiding from the guard. The property under test is a LENGTH
property, and typing an eight-digit literal to test it would create in a
tracked file the precise shape the guard exists to refuse.
"""
from __future__ import annotations

import inspect

import pytest

from linkedin_server import groups, shape

#: A five-digit id. His own page carries one at this length, measured, so this
#: is a real shape and not a value chosen to be short.
SHORT_ID = "12345"

#: A relative href, which is what BOTH these pages actually write. Measured:
#: an absolute matcher found 5 of 10 group links and 0 of 54 event links on the
#: same two captures, and the control refused the tally as void rather than
#: printing a plausible half-answer.
GROUP_REL = f"/groups/{SHORT_ID}/"
GROUP_ABS = f"https://www.linkedin.com/groups/{SHORT_ID}/"

#: A GROUP NAMED AFTER A PERSON, as a slug. This is the input the whole module
#: exists for: it is a group href, it points at no other kind of entity, it has
#: no query, and its segment is a person's name. Every branch except the
#: numeric one lets it through.
A_SLUG_MADE_OF_A_NAME = "/groups/jane-elizabeth-doe/"

#: A MEMBER PATH, DELIBERATELY SHORT, AND THE SHORTNESS IS THE FIX RATHER THAN
#: A DECLARATION.
#:
#: This constant first held ``/in/`` followed by a sixteen-character
#: hyphenated run -- twenty characters in all, and the exact shape
#: ``test_no_committed_identity``'s slug rule is built to refuse. It went red
#: on the file's first staging: *1 unallowed linkedin slug hit(s), 0
#: declared.*
#:
#: **AND THE FIRST VERSION OF THIS VERY COMMENT PUT THE STRING BACK.** The
#: rename removed it from the code and the note explaining the rename quoted
#: it verbatim, so the file stayed red at exactly the same count with the
#: defect now living in the explanation. The guard could not tell the
#: difference and was right not to. **A note about a removed value must
#: describe its SHAPE, never reproduce it** -- which is the same rule the rest
#: of this repository keeps for identifiers and which a comment feels exempt
#: from because it is "only prose". The measurement caught it; reading the
#: rule beforehand did not, and that ordering is now the third instance of it
#: recorded on this project.
#:
#: **THE FIX IS A RENAME, NOT A DECLARATION**, and the order of preference is
#: not a style choice: every declaration permanently widens what that guard
#: tolerates for that file, forever, and a rename widens nothing. The branch
#: under test is "does a path carrying a member segment get refused" -- what
#: the slug SAYS is irrelevant to it, so nothing is lost by making it short.
#:
#: The pair was run rather than reasoned about: red with the long form, green
#: with this one, and red again when the long form is put back -- which is
#: what proves the guard actually counts this class and that the fix is not
#: vacuous. A wave nearly shipped a declaration today that exempted nothing
#: while looking like it did.
A_MEMBER_PATH = "/in/somebody/"


def _long_digits(count: int) -> str:
    """A digit run BUILT, not typed. See the module docstring."""
    return "9" * count


# ---------------------------------------------------------------------------
# 1. The safety property is the SIGNATURE, so it is read rather than argued.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "function",
    [groups.group_identifier, groups.membership_tally, groups.disjoint],
)
def test_no_public_function_takes_a_name(function):
    """A reader never handed a name cannot leak one.

    THIS IS THE WHOLE RULING IN ONE ASSERTION. ``shape.membership_row`` takes
    ``(href, name)`` and decides whether the name may be published; that
    decision is where a group named after a person escapes, and no filter
    closes it because a plain human name has no shape. This module's answer is
    to remove the parameter, and the difference between "we filter it" and "we
    are never given it" is exactly the difference a test can see.

    A future edit adding a ``name`` parameter here turns this red, which is the
    point: the fix would look reasonable in a diff and would silently
    reintroduce the class.
    """
    parameters = list(inspect.signature(function).parameters)
    assert not any("name" in parameter for parameter in parameters), parameters


def test_the_module_publishes_no_free_text_key():
    """Nothing in either payload is a string LinkedIn wrote.

    Every value out of this module is a count, a boolean, a run of digits this
    module validated, a refusal reason from its own vocabulary, or the one href
    LITERAL. Asserted over a real payload rather than by reading the source,
    because a key added later would pass a source reading that nobody re-ran.
    """
    payload = groups.membership_tally([GROUP_REL, GROUP_ABS, A_MEMBER_PATH])
    for key, value in payload.items():
        if key == "identifiers":
            assert all(item.isdigit() for item in value), value
        elif key == "href_shape":
            assert value == groups.PUBLISHED_HREF
        elif key == "refused":
            assert all(
                reason.replace("_", "").isalpha() for reason in value
            ), value
        else:
            assert isinstance(value, int), (key, value)


# ---------------------------------------------------------------------------
# 2. Each refusal, on an input where that branch is the only thing standing.
# ---------------------------------------------------------------------------


def test_a_slug_made_of_a_persons_name_is_refused_by_the_numeric_rule_alone():
    """THE SURVIVAL-CRITICAL TEST, and its input is chosen to make it so.

    Delete the ``isdigit`` branch in ``group_identifier`` and this input
    publishes ``jane-elizabeth-doe`` as an identifier -- a person's name, in a
    field named for the thing that is supposed to be safe. Nothing else in the
    function refuses it: it carries a group segment, it points at no other
    entity kind, it has no query, and it is not the root.

    Verified sensitive by neutralising that branch, not by reasoning about it.
    """
    verdict = groups.group_identifier(A_SLUG_MADE_OF_A_NAME)
    assert verdict["identified"] is False
    assert verdict["refused"] == "identifier_is_not_numeric"
    assert "jane" not in repr(verdict).lower()


def test_a_person_href_is_refused_and_says_which_marker_it_saw():
    """THIS TEST DOES NOT PROVE THE FOREIGN BRANCH, and it says so.

    Delete the foreign branch and this input STILL refuses -- it falls through
    to ``not_a_group_href``, because a member path has no group segment
    either. So this asserts the refusal SHAPE and the ``saw`` contract, and the
    branch itself is proven by the test below, on an input where it is the only
    thing standing. Both are kept: the freeze ruling's own repair was to add
    the sharper input and KEEP the old one as a second case.
    """
    verdict = groups.group_identifier(A_MEMBER_PATH)
    assert verdict["identified"] is False
    assert verdict["refused"] == "href_identifies_another_kind_of_entity"
    assert verdict["saw"], "a refusal that names only the absence is half a measurement"


def test_a_group_path_that_also_carries_a_member_segment_is_refused_as_foreign():
    """THE INPUT WHERE THE FOREIGN BRANCH IS THE ONLY THING REFUSING.

    ``/groups/<digits>/in/<member>/`` has a group segment, has digits directly
    after it, has no query and is not the root. Every other check in the
    function passes it. With the foreign branch neutralised it is IDENTIFIED,
    and a row pointing at a person is counted as one of his memberships.

    Verified by planting that mutation, not by reasoning about it.
    """
    verdict = groups.group_identifier(f"/groups/{SHORT_ID}/in/somebody/")
    assert verdict["identified"] is False
    assert verdict["refused"] == "href_identifies_another_kind_of_entity"
    assert "/in/<member>" in verdict["saw"]


def test_the_foreign_segments_are_derived_from_the_markers_and_not_retyped():
    """A retyped list is a list that drifts.

    The segments are the markers' own second path component, so a marker added
    to ``shape._CENSUS_ENTITY_HREFS`` reaches this module without an edit. This
    asserts the derivation rather than the values, because asserting the values
    is what a copy would also pass.
    """
    assert groups.FOREIGN_SEGMENTS == tuple(
        marker.split("/")[1] for marker in groups.FOREIGN_MARKERS
    )
    assert len(groups.FOREIGN_SEGMENTS) == len(groups.FOREIGN_MARKERS)
    assert groups._PATH_KEY not in groups.FOREIGN_SEGMENTS


def test_the_groups_root_is_refused_and_named_as_the_root():
    """The nav's own link to the surface, and it is not a membership.

    MEASURED, NOT IMAGINED: a live walk over his Groups page found ELEVEN
    hrefs whose path contains the group segment and TEN group entities. The
    eleventh is this. A reader that counted it would report six memberships
    where there are five, and the error would look like a data change rather
    than a bug.
    """
    verdict = groups.group_identifier("/groups/")
    assert verdict["identified"] is False
    assert verdict["refused"] == "group_root_carries_no_identifier"


def test_an_empty_href_is_refused_rather_than_counted():
    for empty in (None, "", "   "):
        assert groups.group_identifier(empty)["refused"] == "no_href"


def test_a_non_group_href_is_refused_with_what_it_saw():
    verdict = groups.group_identifier("/jobs/collections/recommended/")
    assert verdict["identified"] is False
    assert verdict["refused"] == "not_a_group_href"


# ---------------------------------------------------------------------------
# 3. The query is dropped rather than shaped, which is the measured escape.
# ---------------------------------------------------------------------------


def test_a_member_token_in_the_query_reaches_nothing():
    """``membership_row`` measured this escape; this is the closed form of it.

    ``/groups/<id>/?invitedBy=<token>`` survives the census substitutions with
    the token INTACT, because ``/in/`` is the only member shape they know. Here
    the query is discarded before any check runs, so the token cannot appear in
    the output -- asserted over the WHOLE payload rather than over one field,
    because a leak into a field nobody thought to check is the failure mode.
    """
    token = "AB" + _long_digits(16)
    verdict = groups.group_identifier(f"{GROUP_REL}?invitedBy={token}")
    assert verdict["identified"] is True
    assert verdict["identifier"] == SHORT_ID
    assert token not in repr(verdict)
    assert "invitedBy" not in repr(verdict)


def test_a_fragment_is_dropped_the_same_way():
    verdict = groups.group_identifier(f"{GROUP_REL}#member-{_long_digits(12)}")
    assert verdict["identified"] is True
    assert verdict["identifier"] == SHORT_ID


def test_a_long_real_length_identifier_is_accepted():
    """Eight digits is the commonest length on his own page, and it is BUILT.

    The rule must not be a threshold that happens to admit the short fixture
    above and refuse the real thing.
    """
    for length in (5, 6, 7, 8):
        built = _long_digits(length)
        verdict = groups.group_identifier(f"/groups/{built}/")
        assert verdict["identified"] is True, length
        assert verdict["identifier"] == built


def test_a_run_of_non_ascii_digits_is_refused():
    """``str.isdigit()`` IS TRUE OF SEVERAL SCRIPTS AND THIS RULE IS NOT.

    Found on a fresh-eyes re-read before the freeze rather than by a test, so
    the test is written after the fix and says so. Measured: a five-character
    run in Arabic-Indic digits, one in Extended Arabic-Indic digits and a pair
    of superscripts are ALL ``isdigit() == True``, and ``int()`` cannot even
    parse the superscripts.

    **THE POINT IS NOT THAT LINKEDIN WILL SERVE ONE.** It is that this module's
    whole design rests on one sentence -- *a charset wide enough to hold a slug
    is wide enough to hold a name* -- and ``isdigit()`` admits a charset
    materially wider than the ten characters the docstring promised. That is a
    check being correct for the inputs it was imagined against, which is the
    defect this repository has now been caught by three times.

    THE CHARACTERS ARE BUILT BY CODEPOINT, NOT TYPED. A tracked file in this
    repository stays ASCII, and a literal here would also be unreadable to the
    next person, who would have to guess whether it was deliberate.
    """
    for start, length in ((0x0663, 5), (0x06F1, 8), (0x00B2, 2)):
        run = "".join(chr(start) for _ in range(length))
        assert run.isdigit(), "the premise of this test is that isdigit passes"
        verdict = groups.group_identifier(f"/groups/{run}/")
        assert verdict["identified"] is False, run.encode("unicode_escape")
        assert verdict["refused"] == "identifier_is_not_numeric"


def test_an_absurdly_long_run_is_refused_rather_than_published():
    verdict = groups.group_identifier(f"/groups/{_long_digits(64)}/")
    assert verdict["identified"] is False
    assert verdict["refused"] == "identifier_is_not_numeric"


# ---------------------------------------------------------------------------
# 4. The tally, and the two counts that are not the same question.
# ---------------------------------------------------------------------------


def test_the_two_spellings_of_one_group_are_one_membership():
    """LinkedIn writes both on one page, so DISTINCT is not GROUPS.

    ``membership_row`` records the same wrinkle from the other side: the
    relative and absolute spellings shaped to two different strings, so a
    consumer comparing them saw two classes where there is one surface.
    """
    tally = groups.membership_tally([GROUP_REL, GROUP_ABS])
    assert tally["groups"] == 2
    assert tally["distinct"] == 1


def test_the_tally_reports_what_it_refused_and_not_only_what_it_kept():
    tally = groups.membership_tally(
        [GROUP_REL, A_MEMBER_PATH, A_SLUG_MADE_OF_A_NAME, "/groups/", None]
    )
    assert tally["rows"] == 5
    assert tally["groups"] == 1
    assert tally["refused"] == {
        "href_identifies_another_kind_of_entity": 1,
        "identifier_is_not_numeric": 1,
        "group_root_carries_no_identifier": 1,
        "no_href": 1,
    }


def test_an_empty_page_is_zero_and_says_so_without_pretending_to_have_read():
    tally = groups.membership_tally([])
    assert tally == {
        "rows": 0,
        "groups": 0,
        "distinct": 0,
        "identifiers": [],
        "refused": {},
        "href_shape": groups.PUBLISHED_HREF,
    }


def test_disjointness_returns_counts_and_no_identifier():
    """The deciding measurement of the precondition, and it names nothing.

    Five memberships against five suggestions with zero in common is what makes
    them two sets rather than one set drawn twice, and an overlap of zero says
    everything an overlap of zero can say.
    """
    mine = [f"/groups/{_long_digits(7)}/", f"/groups/{_long_digits(8)}/"]
    theirs = [f"/groups/{'8' * 7}/", GROUP_REL]
    verdict = groups.disjoint(mine, theirs)
    assert verdict == {
        "first_distinct": 2,
        "second_distinct": 2,
        "in_common": 0,
        "disjoint": True,
    }
    overlapping = groups.disjoint(mine, mine[:1])
    assert overlapping["in_common"] == 1
    assert overlapping["disjoint"] is False
    assert all(isinstance(value, (int, bool)) for value in verdict.values())


# ---------------------------------------------------------------------------
# 5. The markers are shape's, not a copy of them.
# ---------------------------------------------------------------------------


def test_the_foreign_markers_are_shapes_own_and_not_a_copy():
    """A sixth entity kind added tomorrow must refuse here without an edit.

    ``membership_row`` derives its foreign set from ``_CENSUS_ENTITY_HREFS`` so
    that a new marker becomes a refusal automatically rather than a hole. This
    module inherits the same tuple instead of restating it, and this test is
    what makes a future copy-paste a failure rather than a silent divergence.
    """
    assert groups.FOREIGN_MARKERS is shape._MEMBERSHIP_FOREIGN_MARKERS
    assert groups.GROUP_MARKER == shape._MEMBERSHIP_HREF_MARKER
    assert groups.PUBLISHED_HREF == shape._MEMBERSHIP_PUBLISHED_HREF
    assert groups.GROUP_MARKER not in groups.FOREIGN_MARKERS


def test_every_entity_kind_shape_knows_about_is_refused_here():
    """Not a sample of the markers -- ALL of them, driven off the tuple.

    A test that hand-picks two markers passes forever while a third goes
    unchecked. This one cannot: it is parametrised by the source of truth, so
    a marker added to shape and not handled here fails immediately.
    """
    for marker in groups.FOREIGN_MARKERS:
        kind = marker.split("/")[1]
        verdict = groups.group_identifier(f"/{kind}/{SHORT_ID}/")
        assert verdict["identified"] is False, marker
        assert verdict["refused"] in {
            "href_identifies_another_kind_of_entity",
            "not_a_group_href",
        }, (marker, verdict)
