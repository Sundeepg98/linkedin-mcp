"""The group reader answers in integers, and its bound agrees with the door.

``linkedin_server/group_page.py`` is the reader the ``/groups/<id>/`` allowlist
entry says nobody had written. Three properties are worth a test here and the
rest is prose:

1. **THE BUILDER AND THE BOUNDARY AGREE.** A shaper that accepts an identifier
   the allowlist refuses builds an address its own door rejects, and the
   refusal interpolates the url -- which is how a third party's slug reached a
   traceback once already. The coupling is asserted in BOTH directions and is
   SHOWN FAILING against a bound moved by one.
2. **NOTHING THE PAGE CHOSE CAN LEAVE.** The reader is driven by the planted
   page that answers every key with a person-shaped name, and the verdict
   function is driven with the same plant in every field. Neither may carry it
   out, in a value or in an exception -- an exception is not a return value.
3. **THE LIFTED CLASS NAMES EXIST.** This module reads three entries out of
   ``anchors.ROUTE_CLASSES`` by name. A rename there turns every lifted count
   into a silent zero, which is the quiet direction, so it is made loud here.
"""

from __future__ import annotations

import inspect
import json

import pytest

from linkedin_server import anchors, coerce, group_page, groups, readonly
from tests.plantedpage import PLANT, PlantedPage, carries_the_plant

#: A synthetic slug that is person-SHAPED, because the input this refusal
#: exists for is a group named after somebody. A fixture whose hazard is
#: spelled ``xxx`` does not exercise the hazard.
EPONYMOUS_SLUG = "12345-exampleone-markersurname-network"

#: FOUR ARABIC-INDIC DIGITS, NAMED BY CODE POINT RATHER THAN TYPED, so every
#: source file in this package stays pure ASCII -- ``shape.ABOUT_BULLET`` gives
#: the reason: the operator's console is cp1252 and this repository has already
#: shipped one file that broke on being copied through it.
#:
#: ``"".isdigit()`` IS TRUE OF THIS RUN. That is the whole point of the row it
#: feeds: a charset wide enough to hold it is wide enough to hold a name, which
#: is why ``group_page`` names the ten ASCII digits explicitly.
ARABIC_INDIC_DIGITS = "".join(chr(code) for code in (0x0661, 0x0662, 0x0663, 0x0664))

#: U+00AD SOFT HYPHEN -- an INVISIBLE character inside an otherwise ASCII digit
#: run. It renders as nothing and would pass a human reading of the candidate.
SOFT_HYPHEN = chr(0x00AD)

#: The synthetic group id this suite already uses everywhere else -- 21 other
#: occurrences across tests/ -- so no new digit run enters the tree.
IDENTIFIER = "12345678"


# ---------------------------------------------------------------------------
# 1. The builder and the boundary agree
# ---------------------------------------------------------------------------


def test_the_address_this_module_builds_is_one_the_shipped_gate_admits():
    """The whole point of the row: an ADMITTED address with a reader on it."""
    built = group_page.group_page_url(IDENTIFIER)
    assert built["built"] is True
    assert readonly.is_read_url(built["url"]) is True


def test_the_bound_is_the_boundarys_own_and_the_two_are_shown_disagreeing():
    """SHOWN FAILING. A cap one digit past the allowlist's builds a refusal.

    The groups coupling test caught exactly this on its first run: the entry
    shipped as ``[0-9]+`` and opened a 21-digit address the shaper then
    refused. The same divergence in the other direction is the one this
    module could introduce, so it is driven here rather than described.
    """
    assert group_page.MAX_IDENTIFIER_DIGITS == groups._MAX_IDENTIFIER_DIGITS

    at_the_bound = "1" * group_page.MAX_IDENTIFIER_DIGITS
    built = group_page.group_page_url(at_the_bound)
    assert built["built"] is True
    assert readonly.is_read_url(built["url"]) is True

    # One past it: the builder refuses, and the demonstration is that if it
    # did NOT refuse, the address it would have built is one the door shuts.
    past = "1" * (group_page.MAX_IDENTIFIER_DIGITS + 1)
    assert group_page.group_page_url(past)["built"] is False
    would_have_built = f"https://www.linkedin.com/groups/{past}/"
    assert readonly.is_read_url(would_have_built) is False, (
        "the allowlist now admits a 21-digit group address, so this module's "
        "bound is no longer the boundary's and the two have drifted apart"
    )


def test_a_slug_is_refused_as_an_identifier_and_is_never_echoed():
    """A group named after a person gets that person's name in its slug."""
    out = group_page.group_page_url(EPONYMOUS_SLUG)
    assert out["built"] is False
    assert out["refused"] == "identifier_is_not_numeric"
    assert EPONYMOUS_SLUG not in json.dumps(out)
    # A refusal that names only the absence is half a measurement.
    assert "letters" in out["saw"]


@pytest.mark.parametrize(
    "candidate",
    [
        "",
        None,
        "  ",
        "12 34",
        "12345678/members",
        "urn:li:group:12345678",
        ARABIC_INDIC_DIGITS,
        "1234" + SOFT_HYPHEN + "5678",
    ],
)
def test_every_non_ascii_digit_spelling_is_refused(candidate):
    """``str.isdigit()`` is true of several other scripts; this is not that.

    The Arabic-Indic run above IS a run of decimal digits to Python, and a
    charset wide enough to hold it is wide enough to hold a name. The soft
    hyphen is the other half: an invisible character inside a digit run.
    """
    out = group_page.group_page_url(candidate)
    assert out["built"] is False
    assert "url" not in out


def test_the_builder_never_raises_on_anything_at_all():
    """A refusal is a return value here, so no candidate leaves in a traceback."""
    for candidate in [None, "", 0, 12345678, [], {}, object()]:
        out = group_page.group_page_url(candidate)  # type: ignore[arg-type]
        assert out.get("built") in (True, False)


# ---------------------------------------------------------------------------
# 2. The landing is compared, never published
# ---------------------------------------------------------------------------


def test_the_invitation_token_in_a_direct_link_is_dropped_before_reading():
    """``/groups/<id>/?invitedBy=<token>`` IS the direct-link half of N 175."""
    token = "AQEExampletokenNeverPublished0123456789"
    landed = f"https://www.linkedin.com/groups/{IDENTIFIER}/?invitedBy={token}"
    assert group_page.landed_on_the_same_group(landed, IDENTIFIER) is True


def test_a_landing_on_a_member_profile_is_refused_rather_than_matched():
    """The conservative direction: a row pointing at a person cannot count."""
    landed = (
        f"https://www.linkedin.com/groups/{IDENTIFIER}/in/"
        "exampleone-markersurname"
    )
    assert group_page.landed_on_the_same_group(landed, IDENTIFIER) is None


def test_a_landing_elsewhere_answers_none_rather_than_false():
    """``None`` is "could not be answered"; ``False`` is "answered, and no"."""
    assert (
        group_page.landed_on_the_same_group(
            "https://www.linkedin.com/feed/", IDENTIFIER
        )
        is None
    )
    assert (
        group_page.landed_on_the_same_group(
            "https://www.linkedin.com/groups/99999999/", IDENTIFIER
        )
        is False
    )


# ---------------------------------------------------------------------------
# 3. The verdict is honest about what it cannot see
# ---------------------------------------------------------------------------


def test_a_feed_that_drew_is_the_only_reading_that_claims_a_reach():
    assert (
        group_page.reachability(
            {"anchors_seen": 60, "feed_update_anchors": 8, "member_profile_anchors": 19}
        )["reached"]
        is True
    )


def test_a_rendered_page_with_no_feed_permalink_stays_ambiguous():
    """A gate, an empty group and a restyle all produce this reading.

    THE FLATTERING BRANCH IS THE ONE THIS REFUSES. Reporting ``reached: False``
    here would assert a membership gate on the evidence that nothing rendered,
    and reporting ``True`` would assert the opposite on the same evidence.
    """
    out = group_page.reachability(
        {"anchors_seen": 60, "feed_update_anchors": 0, "member_profile_anchors": 4}
    )
    assert out["state"] == "ambiguous"
    assert out["reached"] is None


def test_a_page_that_drew_nothing_is_a_fact_about_the_reader():
    out = group_page.reachability({"anchors_seen": 0, "feed_update_anchors": 0})
    assert out["state"] == "reader_blind"
    assert out["reached"] is None
    assert "READER" in out["why"]


def test_a_redirect_off_the_group_refuses_the_reading_it_took():
    """A reading taken after a redirect is a reading of some other page."""
    out = group_page.reachability(
        {"anchors_seen": 60, "feed_update_anchors": 8}, False
    )
    assert out["state"] == "off_group"
    assert out["reached"] is False


def test_the_verdict_alphabet_is_closed_over_adversarial_readings():
    """Every ``state`` a caller can get is a literal this module declares."""
    seen = set()
    for reading in [
        None,
        {},
        {"anchors_seen": PLANT},
        {"anchors_seen": 1, "feed_update_anchors": PLANT},
        {"anchors_seen": -5, "feed_update_anchors": -5},
        {"anchors_seen": [1, 2], "feed_update_anchors": {"a": 1}},
    ]:
        for same in (None, True, False):
            seen.add(group_page.reachability(reading, same)["state"])
    assert seen <= group_page.emitted_alphabet()


def test_term_for_refuses_out_of_range_rather_than_clamping():
    """Index 0 is ``reader_blind``; a clamp could rename blindness into a reach."""
    assert group_page.term_for(0) == "reader_blind"
    assert group_page.term_for(-1) == "index_out_of_range"
    assert group_page.term_for(len(group_page.REACH_STATES)) == "index_out_of_range"


# ---------------------------------------------------------------------------
# 4. Nothing the page chose can leave
# ---------------------------------------------------------------------------


def test_the_verdict_function_carries_no_plant_out_in_a_value_or_a_raise():
    """The property the whole module rests on, driven rather than asserted."""
    for reading in [
        {"anchors_seen": PLANT, "feed_update_anchors": PLANT},
        {"anchors_seen": {"x": PLANT}, "member_profile_anchors": [PLANT]},
    ]:
        try:
            out = group_page.reachability(reading)
        except Exception as exc:  # noqa: BLE001 -- a raise is a failure here
            pytest.fail(f"reachability raised {type(exc).__name__}: {exc}")
        assert carries_the_plant(out) == []


def test_the_control_a_bare_int_would_have_carried_the_plant_out():
    """SHOWN FAILING, on the coercion that actually shipped elsewhere.

    ``int()`` writes the value it refused verbatim into its own ValueError,
    and that exception is not a return value. This is the hazard the test
    above is clean against, demonstrated on the same input so the green above
    is a measurement rather than a coincidence.
    """
    with pytest.raises(ValueError) as caught:
        int(PLANT)
    assert PLANT in str(caught.value)
    # And the shipped coercion on the identical input carries nothing.
    assert coerce.as_int(PLANT) is None
    assert coerce.as_count(PLANT) == 0


async def test_the_reader_driven_by_a_page_that_answers_in_names_is_clean():
    """Every field it returns is an integer or a list of integers."""
    out = await group_page.read_group_page(PlantedPage())
    assert carries_the_plant(out) == []
    assert isinstance(out["anchors_seen"], int)
    assert isinstance(out["feed_update_anchors"], int)
    assert all(isinstance(value, int) for value in out["counts"])
    # The page answered every slot with a string, so the refusal count is the
    # FINDING and it must be visible rather than swallowed.
    assert out["values_refused"] > 0


async def test_the_reader_never_raises_on_a_page_that_answers_in_names():
    """An exception is not a return value, so the raise path is driven too."""
    await group_page.read_group_page(PlantedPage(), html=PLANT)


async def test_the_positional_list_travels_with_its_own_alphabet():
    """A positional list published without its key is a reading nobody can
    interpret, which is one step from a reading somebody interprets WRONGLY.

    Every entry is a literal ``anchors.py`` declares, so this publishes
    shipped-in vocabulary and nothing the page chose -- asserted here against
    the module's own emitted alphabet rather than described.
    """
    out = await group_page.read_group_page(PlantedPage())
    alphabet = out["counts_are_positions_in"]
    assert alphabet == list(anchors.ROUTE_CLASSES)
    assert set(alphabet) <= anchors.emitted_alphabet()
    assert carries_the_plant(out) == []
    # The list and its key are the same length, or the key is not a key.
    assert len(out["counts"]) in (0, len(alphabet)), (
        len(out["counts"]), len(alphabet)
    )


# ---------------------------------------------------------------------------
# 5. The couplings, made loud
# ---------------------------------------------------------------------------


def test_every_route_class_this_module_lifts_exists_in_the_shipped_alphabet():
    """A rename in ``anchors.py`` turns a lifted count into a silent zero."""
    for name in group_page.route_classes_this_reader_depends_on():
        assert name in anchors.ROUTE_CLASSES, (
            f"{name} is no longer an anchors.ROUTE_CLASSES entry, so "
            "group_page reads zero for it forever and says nothing about it"
        )


def test_no_function_here_takes_a_name_an_address_or_a_page_except_the_reader():
    """THE SIGNATURE IS HALF THE SAFETY PROPERTY.

    Asserted the way ``groups.py``, ``search_results.py`` and
    ``company_page.py`` assert it: the counting and verdict functions are never
    handed a needle, and exactly one function touches a page.
    """
    async_functions = []
    for name, function in vars(group_page).items():
        if not inspect.isfunction(function):
            continue
        if inspect.iscoroutinefunction(function):
            async_functions.append(name)
    assert async_functions == ["read_group_page"], async_functions

    banned = {"name", "url", "href", "slug", "query", "keywords", "text", "label"}
    for name, function in vars(group_page).items():
        if not inspect.isfunction(function):
            continue
        parameters = set(inspect.signature(function).parameters)
        assert not (parameters & banned), (name, parameters)


def test_the_module_fires_nothing():
    """No confirm token, no press. A shaper that could fire would have
    imported the joining ruling by accident."""
    for name, function in vars(group_page).items():
        if not inspect.isfunction(function):
            continue
        parameters = set(inspect.signature(function).parameters)
        assert not (parameters & {"confirm_token", "token", "grant"}), name


def test_the_published_href_is_a_literal_and_not_a_shape_of_the_input():
    """A "shape" derived from the value is a channel; a constant is not."""
    assert group_page.PUBLISHED_HREF == groups.PUBLISHED_HREF
    assert IDENTIFIER not in group_page.PUBLISHED_HREF


def test_the_member_roster_stays_refused_with_this_reader_shipped():
    """N 165 is out of scope BY NAME and nothing here reopens it."""
    assert (
        readonly.is_read_url(
            f"https://www.linkedin.com/groups/{IDENTIFIER}/members/"
        )
        is False
    )


def test_control_a_renamed_route_class_turns_the_lifted_count_into_a_zero(
    monkeypatch,
):
    """SHOWN FAILING. The quiet direction, driven rather than described.

    The assertion above checks that the three names this module lifts are in
    ``anchors.ROUTE_CLASSES``. What that assertion is FOR is the silence on
    the other side of a rename: ``by_class.get("feed_update", 0)`` answers
    ZERO with no error, and a reader that reports zero feed permalinks on a
    group whose feed drew says ``ambiguous`` about a group it reached.

    Monkeypatched rather than edited -- several agents write this tree.
    """
    renamed = tuple(
        "feed_update_v2" if name == "feed_update" else name
        for name in anchors.ROUTE_CLASSES
    )
    assert "feed_update" not in renamed

    # The shipped membership assertion would now fail:
    assert "feed_update" not in set(renamed)

    # And the consequence it exists to prevent is real: a tally built over the
    # renamed alphabet answers zero for the class this module reads by name.
    monkeypatch.setattr(anchors, "ROUTE_CLASSES", renamed)
    counts = [0] * len(renamed)
    counts[renamed.index("feed_update_v2")] = 7
    by_class = anchors.tally(counts)["by_class"]
    assert by_class.get("feed_update", 0) == 0, (
        "the rename did not silence the lifted count, so the membership "
        "assertion above is not standing for anything"
    )
    assert by_class.get("feed_update_v2") == 7
