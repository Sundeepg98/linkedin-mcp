"""``shape.membership_row`` -- the gate a groups reader needs and cannot inherit.

WHY THIS FILE EXISTS BEFORE ANY GROUPS READER DOES. The boundary widened on
2026-09-05 to admit ``/groups/`` and ``/events/``, and the first thing anyone
will want to build on it is a reader that walks the rows and returns his
memberships. Such a reader inherits NEITHER of the census's two protections:

* ``census_shape`` is a LENGTH AND CHARSET gate. It is not the redactor.
* ``census_redact_rare`` IS the redactor and it needs a COUNT, so it lives
  inside ``census_aggregate`` where a tally exists. A per-record path has no
  tally and therefore no access to it.

That gap shipped in this package once already, on the Interests entity kinds,
and was caught by a probe rather than by a test. So the gate is written and
proven first, and the harvest that will use it comes second.

EVERY VALUE IN THIS FILE IS SYNTHETIC. The group ids are sequential digits,
the slugs are invented words, and the one urn carries the literal token
``SYNTHETIC``. No real member token prefix appears anywhere here.
"""
from __future__ import annotations

import pytest

from linkedin_server import shape

GROUP_ABS = "https://www.linkedin.com/groups/12345678/"
GROUP_REL = "/groups/12345678/"

#: THE TWO SYNTHETIC MEMBER-SLUG LITERALS IN THIS FILE, WRITTEN ONCE EACH AND
#: DECLARED IN ``tests/test_no_committed_identity.py``'s ``DECLARED_PLANTS``.
#:
#: They are SHAPE-VALID on purpose. Assembling them at runtime would hide them
#: from that sweep, and a sweep blinded to this file's deliberate values is
#: blinded to a real one pasted in later -- which is the failure that whole
#: file exists to catch. So each spelling appears exactly once as a literal,
#: the count is pinned, and a third one goes red.
#:
#: The slug is invented and matches no member. ``a-made-up-slug`` is not a
#: name.
A_MEMBER_PROFILE = "https://www.linkedin.com/in/a-made-up-slug/"

#: A GROUP URL THAT ALSO CARRIES A MEMBER PATH -- the row that decides whether
#: the foreign-marker check runs FIRST, and the input a red proof measured the
#: earlier version of this file insensitive to. A member roster's own url IS a
#: group url, so "it starts with /groups/" is exactly the reasoning that would
#: publish one.
A_GROUP_URL_CARRYING_A_MEMBER = (
    "https://www.linkedin.com/groups/12345678/members/?p=/in/a-made-up-slug/"
)


# ---------------------------------------------------------------------------
# THE CONTROL HALF. A gate that refuses everything is not a gate, it is an off
# switch, and it would pass every leak test in this file.
# ---------------------------------------------------------------------------

MUST_PUBLISH_VERBATIM = [
    # A plain group name, in both href spellings LinkedIn writes on one page.
    (GROUP_ABS, "Node.js Developers"),
    (GROUP_REL, "Node.js Developers"),
    # Punctuation a charset gate might have objected to.
    (GROUP_REL, "Node.js Developers - India"),
    # A FOUR-DIGIT YEAR. ``_CENSUS_LONG_DIGITS`` needs six, deliberately, so
    # that a year or a count survives a shape -- asserted here rather than
    # trusted, because this is the commonest legitimate group name that looks
    # like an identifier.
    (GROUP_REL, "Alumni 2019"),
    # A CURLY APOSTROPHE NOT FOLLOWED BY 's'. LinkedIn serves U+2019 and the
    # possessive rule matches a capitalised run before an apostrophe-s. This
    # is the near miss, and it must NOT be shaped.
    (GROUP_REL, "Developers’ Guild"),
]


@pytest.mark.parametrize("href,name", MUST_PUBLISH_VERBATIM)
def test_a_plain_group_row_publishes_its_name_unchanged(href: str, name: str):
    row = shape.membership_row(href, name)
    assert row["published"] is True, row
    assert row["name_shaped"] is False, row
    # The curly apostrophe is normalised to the straight one and nothing else
    # about the string moves.
    assert row["name"] == name.replace("’", "'"), row
    # EQUALITY, because the published href is a LITERAL rather than a shape of
    # the input -- LinkedIn writes both the relative and the absolute form on
    # one page and both publish the same string. The spellings that prove it,
    # including the one carrying a query token, are below.
    assert row["href_shape"] == "/groups/<group>/", row


def test_the_published_href_carries_no_group_id():
    """The name is the payload. The id is not, and never leaves."""
    row = shape.membership_row(GROUP_ABS, "Node.js Developers")
    assert "12345678" not in row["href_shape"], row
    assert "12345678" not in row["name"], row


#: HREFS THAT MUST ALL PUBLISH THE SAME LITERAL. The last of them is the one
#: that decided the design: a BARE MEMBER TOKEN IN A QUERY survives
#: ``census_substitute`` -- ``/in/`` is the only member shape it knows -- so a
#: function that published ``census_substitute(href)`` would emit that token.
#: The token below is invented and matches no real member.
SAME_ROW_MANY_SPELLINGS = [
    GROUP_REL,
    GROUP_ABS,
    "https://www.linkedin.com/groups/12345678",
    "/groups/12345678/?highlightedUpdateType=x",
    "https://www.linkedin.com/groups/12345678/?invitedBy=QQrrSSttUUvvWW",
]


@pytest.mark.parametrize("href", SAME_ROW_MANY_SPELLINGS)
def test_the_published_href_is_a_LITERAL_and_never_a_shape_of_the_input(
    href: str,
):
    """An arbitrary string that never crosses can never carry an identifier.

    This is the closed-vocabulary conclusion ``linkedin_connections`` reached
    after two filters that each looked right and each left a token standing.
    The input href DECIDES; it is never what is emitted.

    The last spelling is the proof rather than an extra case. Publishing the
    shaped input would emit ``?invitedBy=QQrrSSttUUvvWW`` verbatim, because
    the substitutions have no rule for a bare token outside an ``/in/``
    segment -- a gap this repository has already measured and deliberately
    chose not to close by widening the shared predicate.
    """
    row = shape.membership_row(href, "Node.js Developers")
    assert row["published"] is True, row
    assert row["href_shape"] == "/groups/<group>/", row
    assert "12345678" not in row["href_shape"], row
    assert "QQrrSSttUUvvWW" not in repr(row), row


def test_every_spelling_publishes_a_byte_identical_href_shape():
    """One surface, one string. A consumer comparing rows sees one class."""
    shapes = {
        shape.membership_row(href, "Node.js Developers")["href_shape"]
        for href in SAME_ROW_MANY_SPELLINGS
    }
    assert shapes == {"/groups/<group>/"}, shapes


def test_publishing_the_shaped_input_WOULD_have_leaked_the_query_token():
    """SHOWN FAILING for the design decision itself, not just the code.

    The mutation is not planted in the function -- it is the function's own
    first implementation, rebuilt here from the shared predicate, so the
    argument in the docstring is a measurement rather than a claim.
    """
    leaky = shape.census_substitute(
        "https://www.linkedin.com/groups/12345678/?invitedBy=QQrrSSttUUvvWW"
    )
    assert "QQrrSSttUUvvWW" in leaky, leaky
    assert "<group>" in leaky, leaky
    safe = shape.membership_row(
        "https://www.linkedin.com/groups/12345678/?invitedBy=QQrrSSttUUvvWW",
        "Node.js Developers",
    )
    assert "QQrrSSttUUvvWW" not in repr(safe), safe


# ---------------------------------------------------------------------------
# THE REFUSAL HALF, and each refusal must NAME WHAT IT SAW. A refusal that
# reports only what it did not match is half a measurement -- three rounds
# were lost to that in this project before the rule was written down.
# ---------------------------------------------------------------------------

MUST_REFUSE = [
    # Four foreign entity kinds, one per marker in _CENSUS_ENTITY_HREFS.
    (
        A_MEMBER_PROFILE,
        "href_identifies_another_kind_of_entity",
        ["/in/<member>"],
    ),
    (
        "https://www.linkedin.com/company/a-made-up-company/",
        "href_identifies_another_kind_of_entity",
        ["/company/<company>"],
    ),
    (
        "https://www.linkedin.com/newsletters/a-made-up-letter/",
        "href_identifies_another_kind_of_entity",
        ["/newsletters/<newsletter>"],
    ),
    (
        "https://www.linkedin.com/school/a-made-up-school/",
        "href_identifies_another_kind_of_entity",
        ["/school/<school>"],
    ),
    # A GROUP URL THAT ALSO CARRIES A MEMBER PATH. This is the row that
    # decides whether the foreign check runs first, and it must: a member
    # roster's own url is a group url, and "it starts with /groups/" is
    # exactly the reasoning that would publish one.
    (
        A_GROUP_URL_CARRYING_A_MEMBER,
        "href_identifies_another_kind_of_entity",
        ["/in/<member>"],
    ),
    # Not an entity at all.
    ("https://www.linkedin.com/feed/", "not_a_group_href", []),
    ("", "no_href", []),
    (None, "no_href", []),
]


@pytest.mark.parametrize("href,refused,saw", MUST_REFUSE)
def test_a_row_that_is_not_his_membership_is_dropped_and_says_why(
    href, refused, saw
):
    row = shape.membership_row(href, "Any Name At All")
    assert row["published"] is False, row
    assert row["refused"] == refused, row
    assert row["saw"] == saw, row
    assert row["why"], row


#: THE INPUT THIS TEST USES IS THE POINT OF IT, and it was CHANGED after a red
#: proof measured the first version insensitive.
#:
#: The original input was a plain ``/in/`` href. Under the mutation that
#: deletes the foreign-marker branch, that row STILL refuses -- it falls
#: through to the group-marker check, which still turns it away -- so the test
#: passed against a guard with its first branch removed. It was asserting the
#: refusal SHAPE and nothing about the branch it appeared to be protecting.
#:
#: This input carries BOTH markers, so the foreign branch is the ONLY thing
#: refusing it. Delete that branch and this row publishes a person's name.
#: Measured: with the branch removed, this input publishes.
_FOREIGN_ONLY_REFUSES_THIS = A_GROUP_URL_CARRYING_A_MEMBER


@pytest.mark.parametrize(
    "href",
    [
        _FOREIGN_ONLY_REFUSES_THIS,
        A_MEMBER_PROFILE,
    ],
)
def test_a_refusal_returns_no_fragment_of_what_it_refused(href: str):
    """SUBTRACTION, NOT REDACTION, and the difference is the whole design.

    A blanked row still reports that somebody was there, and a redaction that
    erases its own marker is worse than no redaction: it buys the reader's
    trust and ships the name anyway. So a refused row carries the MARKERS it
    matched -- this module's own vocabulary, which names nobody -- and no
    field of the input.

    TWO INPUTS, because they prove different things and only one of them was
    here first. The first is refused by the FOREIGN-MARKER branch alone; the
    second by the group-marker check. Together they say the no-fragment
    property holds on both refusal paths rather than on whichever one the
    author happened to pick.
    """
    row = shape.membership_row(href, "Wilhelmina Farnsworth")
    blob = repr(row)
    assert row["published"] is False, row
    assert "Wilhelmina" not in blob, row
    assert "Farnsworth" not in blob, row
    assert "a-made-up-slug" not in blob, row
    assert "name" not in row, row


# ---------------------------------------------------------------------------
# THE NAME HALF. The href says the row is his; the name still has to be a
# group's name rather than a person's.
# ---------------------------------------------------------------------------

MUST_SHAPE_THE_NAME = [
    # A POSSESSIVE. LinkedIn's commonest way of putting a person into a label.
    ("Jane Elizabeth Doe’s Node Circle", "<member>'s Node Circle"),
    # A URN, which identifies somebody whichever container it was read in.
    ("Members of urn:li:fsd_profile:SYNTHETIC", "Members of <urn>"),
    # SIX OR MORE DIGITS, the threshold "Alumni 2019" above sits under.
    ("Cohort 1234567", "Cohort <id>"),
]


@pytest.mark.parametrize("name,expected", MUST_SHAPE_THE_NAME)
def test_a_name_carrying_an_identifier_is_shaped_and_the_caller_is_told(
    name: str, expected: str
):
    row = shape.membership_row(GROUP_REL, name)
    assert row["published"] is True, row
    assert row["name_shaped"] is True, row
    assert row["name"] == expected, row
    assert row["why"], row


def test_the_shaped_name_keeps_no_part_of_the_person():
    row = shape.membership_row(GROUP_REL, "Jane Elizabeth Doe’s Node Circle")
    for fragment in ("Jane", "Elizabeth", "Doe"):
        assert fragment not in row["name"], row


# ---------------------------------------------------------------------------
# SHOWN FAILING. Three mutations, each rebuilding a design somebody would
# plausibly write, each asserted to leak. A guard that has not been shown
# failing certifies nothing, and a register of such guards manufactures
# confidence at scale.
# ---------------------------------------------------------------------------


def test_without_the_foreign_marker_check_a_person_row_publishes(monkeypatch):
    """MUTATION 1: gate on "is it a group href" and forget "and nothing else".

    This is the natural first implementation -- check for the marker you want
    and return. It publishes a member roster row, because a roster's url IS a
    group url.
    """
    monkeypatch.setattr(shape, "_MEMBERSHIP_FOREIGN_MARKERS", ())
    leaked = shape.membership_row(
        A_GROUP_URL_CARRYING_A_MEMBER,
        "Wilhelmina Farnsworth",
    )
    assert leaked["published"] is True, (
        "the mutation did not reach -- with the foreign markers emptied this "
        "row must publish, or this test is not measuring the check it names"
    )
    assert leaked["name"] == "Wilhelmina Farnsworth", leaked


def test_census_href_identifies_entity_is_the_WRONG_gate_and_here_is_why():
    """MUTATION 2: reuse the census predicate, which is the tempting reuse.

    ``census_href_identifies_entity`` returns True for a group href -- the
    marker was added to that tuple on 2026-09-04 for exactly that reason -- so
    a reader gated on it refuses EVERY membership row and returns an empty
    list that looks like "he belongs to no groups".

    **That is the failure this project is most practised at misreading**: a
    zero from an instrument that cannot see the thing. The assertion is here
    so that anyone who reaches for the shared predicate finds out from a test
    rather than from an empty answer.
    """
    assert shape.census_href_identifies_entity("/groups/<group>/") is True
    assert shape.membership_row(GROUP_REL, "Node.js Developers")["published"]


def test_publishing_the_name_without_the_substitution_check_ships_a_person(
    monkeypatch,
):
    """MUTATION 3: trust the href and publish the name.

    Once the href has proven the row is a group, publishing its name looks
    safe. It is not: LinkedIn writes people into group labels, and the row
    below is the shape it does it in.
    """
    original = shape.census_substitute
    monkeypatch.setattr(shape, "census_substitute", lambda text: original(text))
    # The real mutation is in the comparison, so it is rebuilt rather than
    # patched: this is what the function would return without the name check.
    row = shape.membership_row(GROUP_REL, "Jane Elizabeth Doe’s Node Circle")
    unchecked = original("Jane Elizabeth Doe’s Node Circle")
    assert row["name"] != "Jane Elizabeth Doe's Node Circle", row
    assert unchecked == "<member>'s Node Circle", unchecked


# ---------------------------------------------------------------------------
# THE EVENT MARKER, added 2026-09-05 in the same wave that opened /events/.
#
# These live here rather than in tests/test_surface_census.py because the
# reason they exist is this wave's: the boundary admitted /events/, and the
# next thing anybody does with an admitted address is census it.
# ---------------------------------------------------------------------------

AN_EVENT_HREF = "https://www.linkedin.com/events/7300000000000000000/"

#: An event card's accessible name is routinely its ORGANISER. This one is
#: invented and belongs to nobody.
AN_ORGANISER_BEARING_NAME = "Hiring Meetup by Wilhelmina Farnsworth"


def test_an_event_href_is_recognised_as_naming_an_entity():
    """The gap this wave found, asserted so it cannot come back.

    ``fa1a1ba`` added group, newsletter and school markers on 2026-09-04
    because the profile Interests tab enumerates five entity kinds and a probe
    put a name behind each. **Events are not on that tab**, so that probe had
    no event row and could not have found this. It was found the other way
    round -- by opening the address.
    """
    shaped = shape.census_shape(AN_EVENT_HREF)
    assert shaped == "https://www.linkedin.com/events/<event>/", shaped
    assert shape.census_href_identifies_entity(shaped) is True, shaped


def test_the_event_placeholder_is_declared_or_the_shape_reads_opaque():
    """THE HALF-APPLIED FIX, which is worse than the leak, and was made twice.

    ``_CENSUS_SAFE_CHARS`` admits no angle brackets, so a substitution added
    WITHOUT its placeholder turns every shape into ``<opaque>`` -- which reads
    as a redaction, carries no marker, and therefore makes
    ``census_href_identifies_entity`` return False and ship the name beside it.

    That was recorded on ``_CENSUS_PLACEHOLDER`` on 2026-09-04 and the same
    mistake was made again on 2026-09-05, caught in the same minute by running
    the pair rather than reading the note. This asserts the outcome the note
    could not enforce.
    """
    assert shape.census_shape(AN_EVENT_HREF) != shape.CENSUS_OPAQUE
    assert shape._CENSUS_PLACEHOLDER.search("<event>"), (
        "the event placeholder is not declared, so its shape will fail the "
        "charset gate and read <opaque> -- a redaction with no marker, which "
        "is worse than publishing the href"
    )


def test_the_count_rule_CANNOT_catch_an_organisers_name_and_that_is_the_point():
    """SHOWN FAILING for the marker's REASON, not just its presence.

    ``census_redact_rare`` fires only at ``count == 1``. An organiser who
    appears twice on a page -- two events, or a card and a header -- merges to
    ``count == 2`` and the name ships. So the count rule is not a second line
    of defence here; the href marker is the only one.
    """
    shaped = shape.census_shape(AN_ORGANISER_BEARING_NAME)
    assert shape.census_redact_rare(shaped, 2) == shaped, (
        "the count rule fired at count 2, so this test is no longer "
        "demonstrating the escape the href marker exists to close"
    )
    assert "Wilhelmina" in shaped, shaped
    # And the href marker IS what catches it.
    assert shape.census_href_identifies_entity(
        shape.census_shape(AN_EVENT_HREF)
    ) is True


def test_removing_the_event_marker_makes_the_guard_silent(monkeypatch):
    """The mutation, planted: drop the marker and the guard stops speaking."""
    monkeypatch.setattr(
        shape,
        "_CENSUS_ENTITY_HREFS",
        tuple(m for m in shape._CENSUS_ENTITY_HREFS if m != "/events/<event>"),
    )
    shaped = shape.census_shape(AN_EVENT_HREF)
    assert shape.census_href_identifies_entity(shaped) is False, (
        "the guard still fires with the event marker removed, so it is not "
        "the marker doing the work and this test measures nothing"
    )


def test_the_other_four_entity_kinds_still_redact_and_two_controls_survive():
    """A blanket redactor would pass every leak test above.

    So the pair is run: five kinds that must be recognised, and two ordinary
    LinkedIn addresses that must NOT be -- because a guard that fires on
    everything has stopped discriminating and the census would publish nothing.
    """
    must_redact = [
        AN_EVENT_HREF,
        "https://www.linkedin.com/groups/12345678/",
        A_MEMBER_PROFILE,
        "https://www.linkedin.com/company/a-made-up-co/",
        "https://www.linkedin.com/newsletters/weekly-123456/",
        "https://www.linkedin.com/school/a-made-up-school/",
    ]
    must_survive = [
        "https://www.linkedin.com/feed/",
        "https://www.linkedin.com/jobs/search/",
    ]
    for href in must_redact:
        assert shape.census_href_identifies_entity(
            shape.census_shape(href)
        ) is True, href
    for href in must_survive:
        assert shape.census_href_identifies_entity(
            shape.census_shape(href)
        ) is False, href


def test_the_foreign_markers_are_derived_from_the_shared_tuple():
    """A sixth entity kind must become a REFUSAL here, never a hole.

    The foreign set is computed from ``_CENSUS_ENTITY_HREFS`` rather than
    written out, so a marker added there tomorrow is refused here without
    anybody remembering to come and add it. That is asserted rather than
    described, because a derivation somebody later "simplifies" into a literal
    is exactly how this stops being true.
    """
    assert shape._MEMBERSHIP_HREF_MARKER in shape._CENSUS_ENTITY_HREFS
    assert set(shape._MEMBERSHIP_FOREIGN_MARKERS) == (
        set(shape._CENSUS_ENTITY_HREFS) - {shape._MEMBERSHIP_HREF_MARKER}
    )
    # 4 -> 5 ON 2026-09-05, AND THE MOVE IS THE PROPERTY WORKING RATHER THAN A
    # MAINTENANCE CHORE. The event marker was added to the shared tuple hours
    # after this test was written, by the same wave, and the derivation turned
    # it into a REFUSAL in `membership_row` with no edit to that function --
    # which is exactly what the assertion above says it must do. The pinned
    # count then went red so a human had to look, which is what the assertion
    # below is for. Both halves did their job in the same session.
    #
    # An event href refusing here is CORRECT: a membership row is about a
    # group, and an event is a different entity with a different consent
    # question -- see the `/events/` allowlist entry, which records that its
    # census rows are thinner than the groups half's.
    assert len(shape._MEMBERSHIP_FOREIGN_MARKERS) == 5, (
        shape._MEMBERSHIP_FOREIGN_MARKERS
    )
