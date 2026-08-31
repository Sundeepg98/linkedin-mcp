"""The surface census, and the privacy property it exists to hold.

``linkedin_surface_census`` reads the CONTROLS on a page so that capabilities
this server refuses can be costed from a measurement instead of a guess. The
surface it most needs to read is the feed, and the feed is made of OTHER
MEMBERS -- so the tool's whole design problem is reporting what a page carries
without reporting who is on it.

WHAT THIS FILE IS ORGANISED AROUND. The shaper is not tested by feeding it
strings it already handles. Every rule below is shown REFUSING something: a
name in a possessive, a name as a whole accessible name, a name repeated so
the singleton cap cannot see it, a name in a script the character class does
not cover. A shaper demonstrated only on clean input certifies nothing, and
two of the rules here exist because an earlier version of this file showed the
shaper LEAKING and the code had to move.

Both of those leaks were real and are pinned as regressions rather than
described:

* ``test_the_curly_apostrophe_does_not_defeat_the_possessive_rule`` -- LinkedIn
  serves U+2019. With that glyph left in place the possessive rule fired
  correctly and the CHARACTER GATE then refused the whole result, so every
  reaction control on the feed collapsed to ``<opaque>`` and the census
  reported nothing about the surface it exists to measure.
* ``test_a_member_who_appears_twice_is_still_refused`` -- the singleton cap
  rests on "furniture repeats and a person does not", and that premise is
  false for a member linked twice on one page. The href rule is what closes
  it, and it closes it on the STRUCTURE of the control rather than on the
  string.

Every non-ASCII fixture below is written as an escape rather than as the
glyph, because this repo is ASCII throughout and ``test_path_hygiene.py``
reads these files as ascii.

Nothing here reaches LinkedIn or an account. ONE section launches a browser
and it is section 8: a LOCAL headless Chromium over invented markup, because
name resolution lives in the injected script and only a laid-out document can
answer what it asks. Its header says why a fake page cannot stand in, and the
line it replaced -- "nothing here launches Chromium" -- was true for as long
as the census had never been asked to name a form field.
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import dom, errors, readonly, shape
from linkedin_server.server import CENSUS_SURFACES, linkedin_surface_census
from tests.conftest import FakePage

FEED_URL = "https://www.linkedin.com/feed/"
PROFILE_URL = "https://www.linkedin.com/in/me/"
#: The settings INDEX. The trailing slash is load-bearing: the tests below
#: append to this string to build the category pages that must stay refused.
SETTINGS_URL = "https://www.linkedin.com/mypreferences/d/"

#: The intro editor on HIS OWN profile, added 2026-08-31 on the operator's
#: ruling. The ``/in/me/`` spelling is the whole of the permission: it
#: redirects to whoever is signed in, so it can only ever reach him, and this
#: server has MEASURED on ``linkedin_who_viewed_me`` that loading a third
#: party's profile leaves them a durable record.
PROFILE_EDIT_INTRO_URL = "https://www.linkedin.com/in/me/edit/intro/"

#: ONE NAMED SETTINGS PAGE, added the same day and by the same ruling: one
#: page at a time, never the family and never a wildcard. Deliberately NOT
#: ``/mypreferences/d/settings/language`` or ``.../autoplay-videos``, each of
#: which would have needed the forbidden substring ``"/settings/"`` narrowed.
DARK_MODE_URL = "https://www.linkedin.com/mypreferences/d/dark-mode"

#: Invented, and drawn from the families ``test_no_committed_identity.py``
#: already sanctions, so this file's own fixtures cannot read as real data.
MEMBER_SLUG = "alex-r-12ab34"
OTHER_SLUG = "priya-sharma-12ab34"
ACTIVITY_ID = "7400000000000000001"

#: The curly apostrophe LinkedIn actually serves, as an escape.
CURLY = "\u2019"


# ---------------------------------------------------------------------------
# 1. The shaper, shown REFUSING
# ---------------------------------------------------------------------------

#: ``(label, raw, the substring that must not survive)``. The third column is
#: the point: asserting an exact output would pass just as well against a
#: shaper that mangled the string for some unrelated reason, and what is being
#: certified here is that the IDENTITY is gone.
LEAKS = [
    (
        "possessive in an aria-label",
        "React Like to Jane Doe's post",
        "Jane Doe",
    ),
    (
        "possessive with the curly apostrophe LinkedIn actually serves",
        "React Like to Jane Doe" + CURLY + "s post",
        "Jane Doe",
    ),
    (
        "a member path",
        "/in/" + MEMBER_SLUG + "/",
        MEMBER_SLUG,
    ),
    (
        "a member path inside a longer name",
        "View /in/" + OTHER_SLUG + "/ now",
        OTHER_SLUG,
    ),
    (
        "a company path",
        "/company/example-corp/jobs/",
        "example-corp",
    ),
    (
        "an entity urn",
        "urn:li:activity:" + ACTIVITY_ID,
        ACTIVITY_ID,
    ),
    (
        "a long numeric id in a path",
        "/feed/update/" + ACTIVITY_ID + "/",
        ACTIVITY_ID,
    ),
    (
        "a lowercase possessive",
        "the recruiter's note",
        "recruiter's",
    ),
]


@pytest.mark.parametrize("label,raw,identity", LEAKS, ids=[row[0] for row in LEAKS])
def test_the_shaper_refuses_every_form_of_identity(label, raw, identity):
    """Each rule, shown removing the thing it exists to remove."""
    shaped = shape.census_shape(raw)
    assert identity not in shaped, f"{label}: {identity!r} survived as {shaped!r}"


def test_the_leak_table_would_notice_a_shaper_that_stopped_working():
    """THE CONTROL. Without it the table above is a list of strings that a
    do-nothing shaper could also pass -- it could not, but nothing here would
    say so, and a check that cannot fail certifies nothing.

    ``str`` is the identity function on these inputs, which is precisely a
    shaper that has been switched off: every planted identity survives it.
    """
    survived = [
        identity for _label, raw, identity in LEAKS if identity in str(raw)
    ]
    assert len(survived) == len(LEAKS), survived


def test_the_shaped_forms_are_what_the_instrument_promises():
    """The exact outputs, since the tool's docstring quotes them at a caller."""
    assert (
        shape.census_shape("React Like to Jane Doe's post")
        == "React Like to <member>'s post"
    )
    assert shape.census_shape("/in/" + MEMBER_SLUG + "/") == "/in/<member>/"
    assert shape.census_shape("/company/example-corp/") == "/company/<company>/"
    assert shape.census_shape("urn:li:activity:" + ACTIVITY_ID) == "<urn>"
    assert (
        shape.census_shape("/feed/update/" + ACTIVITY_ID + "/")
        == "/feed/update/<id>/"
    )


def test_the_curly_apostrophe_does_not_defeat_the_possessive_rule():
    """REGRESSION, and the failure was not the one it looks like.

    The possessive rule always fired on U+2019. What broke was the step after
    it: the captured apostrophe stayed in the output, the character gate does
    not admit U+2019, and the entire shape was therefore replaced with
    ``<opaque>``. The name was never leaked -- the MEASUREMENT was, every
    reaction control on the feed collapsing into one meaningless bucket.
    """
    curly = shape.census_shape("React Like to Jane Doe" + CURLY + "s post")
    straight = shape.census_shape("React Like to Jane Doe's post")
    assert curly == straight == "React Like to <member>'s post"
    assert curly != shape.CENSUS_OPAQUE


def test_a_name_in_another_script_is_refused_by_the_character_gate():
    """The gate is POSITIVE, so a name it has never seen is refused by default.

    This is the rule that makes the design safe against names nobody wrote a
    case for: it does not recognise these scripts, so it does not emit them.
    """
    assert shape.census_shape("\u091c\u0928\u0924\u093e Sharma") == shape.CENSUS_OPAQUE
    assert shape.census_shape("\u5f20\u4f1f") == shape.CENSUS_OPAQUE


def test_a_long_accessible_name_is_refused_rather_than_truncated():
    """A sentence on a feed card is somebody's words, so it is not emitted at
    all. Truncating would publish the first sixty characters of it."""
    long_name = "A" + " word" * 40
    assert len(long_name) > shape.CENSUS_NAME_LIMIT
    assert shape.census_shape(long_name) == shape.CENSUS_OPAQUE


def test_empty_input_shapes_to_empty_rather_than_to_a_placeholder():
    """Absent is absent. A placeholder here would later read like a control
    that carried a name nobody could shape."""
    assert shape.census_shape(None) == ""
    assert shape.census_shape("") == ""
    assert shape.census_shape("   ") == ""


# ---------------------------------------------------------------------------
# 2. The cap, and what it is for
# ---------------------------------------------------------------------------


def test_the_shaper_alone_would_pass_a_bare_name_through():
    """SHOWN FAILING, and this is the test that justifies the cap existing.

    ``census_shape`` is a substitution pass. A name carrying no path, no id and
    no possessive has nothing in it to substitute, so it comes out untouched --
    "Jane Doe" is inside the character class and under the length limit. The
    shaper is not the thing that stops it, and a reader who assumed otherwise
    would delete the cap as redundant.
    """
    assert shape.census_shape("Jane Doe") == "Jane Doe"
    assert shape.census_shape("Reply to Jane Doe") == "Reply to Jane Doe"


def test_the_cap_removes_the_name_the_shaper_could_not():
    """The other half: at ``count == 1`` those two shapes lose the name."""
    assert shape.census_redact_rare("Jane Doe", 1) == "<redacted>"
    assert shape.census_redact_rare("Reply to Jane Doe", 1) == "Reply to <redacted>"


def test_the_cap_leaves_a_repeated_shape_alone():
    """Which is the whole reason the cap can afford to be aggressive.

    The signal a capability measurement is built on is the REPEATED control --
    twelve identical reaction buttons is the fact worth having. Those keep
    their shape; only the singletons are blanked.
    """
    repeated = "React Like to <member>'s post"
    assert shape.census_redact_rare(repeated, 12) == repeated


def test_the_cap_fires_at_two_words_not_three():
    """The documented departure from the brief, pinned so it cannot drift back.

    Three capitalised words was the specification and it does not hold: both
    of the shapes below are two words, and both are names.
    """
    assert shape.census_redact_rare("Jane Elizabeth Doe", 1) == "<redacted>"
    assert shape.census_redact_rare("Jane Doe", 1) == "<redacted>"
    # One capitalised word AT THE START of a shape is the control's verb, not
    # a name, and survives. See the two tests below for the case where one
    # capitalised word arrives mid-string, which does not.
    assert shape.census_redact_rare("Follow", 1) == "Follow"
    assert shape.census_redact_rare("Start a post", 1) == "Start a post"


#: The labels that leaked, as ``(shape, the identity that must not survive)``.
#:
#: MEASURED ON THIS IMPLEMENTATION on 2026-08-30, not imagined. The first is
#: the exact template ``dom.FOLLOWED_PAGE_BUTTON`` anchors on -- LinkedIn
#: writes ``Click to stop following <Page>`` -- and it leaked whenever the
#: Page name was a SINGLE capitalised word.
ONE_WORD_LEAKS = [
    ("Click to stop following Acme", "Acme"),
    ("Connect with Prince", "Prince"),
    ("Message from Madonna today", "Madonna"),
]


@pytest.mark.parametrize(
    "raw,identity", ONE_WORD_LEAKS, ids=[row[1] for row in ONE_WORD_LEAKS]
)
def test_the_cap_removes_a_one_word_name_the_run_rule_cannot_see(raw, identity):
    """REGRESSION, and the rule moved from two words to one because of it.

    A run of two capitalised words was the rule, and it has a blind spot that
    is not obvious from reading it: a name is only caught when it sits BESIDE
    another capital. ``Follow Acme`` was always caught. ``Click to stop
    following Acme`` was not -- its only other capital is ``Click``, four
    lowercase words away, so no run of two exists anywhere in the string and
    the label shipped with the Page name on it.

    That template is not hypothetical. It is the one
    ``dom.FOLLOWED_PAGE_BUTTON`` selects on, so it is the label this package
    is most certain to meet.
    """
    shaped = shape.census_redact_rare(shape.census_shape(raw), 1)
    assert identity not in shaped, f"{identity!r} survived as {shaped!r}"
    assert shape.CENSUS_REDACTED in shaped


def test_that_one_word_rule_would_notice_a_cap_that_stopped_firing():
    """THE CONTROL. Without it the table above passes against a cap that has
    been switched off, because ``census_shape`` alone leaves all three strings
    untouched -- none carries a path, an id or a possessive to substitute.

    So the assertion is the INVERSE of the one being certified: at any count
    other than one the cap does not fire, and every planted name survives.
    """
    survived = [
        identity
        for raw, identity in ONE_WORD_LEAKS
        if identity in shape.census_redact_rare(shape.census_shape(raw), 2)
    ]
    assert len(survived) == len(ONE_WORD_LEAKS), survived


def test_a_one_word_shape_with_no_href_is_a_KNOWN_residual():
    """PINNED AS KNOWN rather than fixed, so it is not rediscovered as a bug.

    A shape that is EXACTLY one capitalised word still survives. It has to:
    ``Follow`` is that shape, and it is the single most useful row a follow
    census can return. Nothing about the STRING separates ``Follow`` from
    ``Gridwell``.

    What separates them in practice is structure, and that is where the cover
    comes from -- a control naming an entity almost always LINKS to it, and
    :func:`shape.census_href_identifies_entity` blanks those on the href
    whatever the name looks like. The uncovered case is a bare one-word button
    with no href at all. This test asserts the current behaviour so that a
    future reader meets a decision instead of a hole.
    """
    assert shape.census_redact_rare("Gridwell", 1) == "Gridwell"
    # And the structural rule that covers the usual form of it.
    assert shape.census_href_identifies_entity("/company/<company>/")


# ---------------------------------------------------------------------------
# 3. Aggregation: the count is where privacy is actually won
# ---------------------------------------------------------------------------


def _control(**kwargs: Any) -> dict[str, Any]:
    base = {
        "shape": "",
        "tag": "button",
        "role": "button",
        "name_source": "aria-label",
        "has_href": False,
        "href_shape": None,
        "aria_expanded": None,
        "disabled": False,
    }
    base.update(kwargs)
    return base


def test_two_different_people_collapse_into_one_shape():
    """THE PRIVACY PROPERTY, stated as an outcome rather than as a rule.

    Two reaction buttons naming two different members are ONE row with a count
    of two. Neither name is in the output, and the row that replaces them is a
    fact about the page rather than about either person.
    """
    records = [
        _control(shape=shape.census_shape("React Like to Jane Doe's post")),
        _control(shape=shape.census_shape("React Like to Bob Roe's post")),
    ]
    shapes, _hrefs = shape.census_aggregate(records)
    assert len(shapes) == 1
    assert shapes[0]["shape"] == "React Like to <member>'s post"
    assert shapes[0]["count"] == 2
    blob = json.dumps(shapes)
    assert "Jane" not in blob and "Bob" not in blob


def test_a_member_who_appears_twice_is_still_refused():
    """REGRESSION, and the hole the count rule cannot see by construction.

    The cap fires only at ``count == 1``. A member linked twice on one page --
    posting twice, or linked from a card header and again from a comment --
    merges to a count of two, so the cap never runs and the name ships. The
    href rule closes it: a control pointing at ``/in/<member>/`` is a link to
    a member however many of them there are.
    """
    link = _control(
        shape=shape.census_shape("Jane Doe"),
        tag="a",
        role=None,
        name_source="text",
        has_href=True,
        href_shape=shape.census_shape("/in/" + MEMBER_SLUG + "/"),
    )
    shapes, hrefs = shape.census_aggregate([link, dict(link)])
    assert len(shapes) == 1
    assert shapes[0]["count"] == 2
    assert shapes[0]["shape"] == "<redacted>"
    assert "Jane" not in json.dumps(shapes)
    assert hrefs == {"/in/<member>/": 2}


def test_a_company_link_is_refused_on_the_same_structural_rule():
    company = _control(
        shape=shape.census_shape("Example Corp"),
        tag="a",
        has_href=True,
        href_shape=shape.census_shape("/company/example-corp/"),
    )
    shapes, _hrefs = shape.census_aggregate([company, dict(company)])
    assert shapes[0]["shape"] == "<redacted>"


def test_the_structural_rule_is_keyed_on_the_href_and_can_be_asked_directly():
    assert shape.census_href_identifies_entity("/in/<member>/") is True
    assert shape.census_href_identifies_entity("/company/<company>/") is True
    assert shape.census_href_identifies_entity("/jobs/view/<id>/") is False
    assert shape.census_href_identifies_entity(None) is False


def test_controls_differing_only_in_state_stay_separate_rows():
    """The merge key is the whole record, not the name.

    Two controls reading "Follow" are the same shape only if they are also the
    same tag, role and disabled state. Merging on the name alone would report
    one shape where the page carries two different controls, which is a
    measurement error rather than a privacy one -- but it is the same key that
    delivers both properties.
    """
    records = [
        _control(shape="Follow", disabled=False),
        _control(shape="Follow", disabled=True),
    ]
    shapes, _hrefs = shape.census_aggregate(records)
    assert len(shapes) == 2
    assert {row["disabled"] for row in shapes} == {True, False}


def test_control_shapes_come_back_sorted_by_count_descending():
    records = (
        [_control(shape="Follow")] * 3
        + [_control(shape="Save")] * 7
        + [_control(shape="Apply")]
    )
    shapes, _hrefs = shape.census_aggregate(records)
    counts = [row["count"] for row in shapes]
    assert counts == sorted(counts, reverse=True)
    assert shapes[0]["shape"] == "Save"


def test_href_shapes_are_counted_across_every_control():
    records = [
        _control(has_href=True, href_shape="/in/<member>/", shape="<redacted>"),
        _control(has_href=True, href_shape="/in/<member>/", shape="<redacted>"),
        _control(has_href=True, href_shape="/jobs/view/<id>/", shape="Job"),
    ]
    _shapes, hrefs = shape.census_aggregate(records)
    assert hrefs == {"/in/<member>/": 2, "/jobs/view/<id>/": 1}


# ---------------------------------------------------------------------------
# 4. The DOM reader: raw names die inside it
# ---------------------------------------------------------------------------


def _payload(controls: list[dict[str, Any]], **counts: int) -> dict[str, Any]:
    return {
        "url": FEED_URL,
        "title": "Feed | LinkedIn",
        "truncated": False,
        "counts": {
            "forms": counts.get("forms", 1),
            "buttons": counts.get("buttons", 2),
            "links": counts.get("links", 3),
            "contenteditable": counts.get("contenteditable", 1),
            "file_inputs": counts.get("file_inputs", 0),
            "dialogs": counts.get("dialogs", 0),
        },
        "controls": controls,
    }


def _raw_page(controls: list[dict[str, Any]], **counts: int) -> FakePage:
    return FakePage(url=FEED_URL, evaluate_result=_payload(controls, **counts))


#: What the injected script really hands back: raw accessible names, raw hrefs.
RAW_CONTROLS = [
    {
        "tag": "button",
        "role": "button",
        "name": "React Like to Jane Doe" + CURLY + "s post",
        "name_source": "aria-label",
        "has_href": False,
        "href": "",
        "aria_expanded": "false",
        "disabled": False,
    },
    {
        "tag": "a",
        "role": None,
        "name": "Jane Doe",
        "name_source": "text",
        "has_href": True,
        "href": "https://www.linkedin.com/in/" + MEMBER_SLUG + "/",
        "aria_expanded": None,
        "disabled": False,
    },
    {
        "tag": "a",
        "role": None,
        "name": "Priya Sharma",
        "name_source": "text",
        "has_href": True,
        "href": "/in/" + OTHER_SLUG + "/",
        "aria_expanded": None,
        "disabled": False,
    },
]

#: Every identity planted in :data:`RAW_CONTROLS`.
PLANTED = ("Jane Doe", "Jane", "Priya Sharma", "Priya", MEMBER_SLUG, OTHER_SLUG)


async def test_no_raw_name_survives_the_dom_reader():
    """THE STRUCTURAL CLAIM, tested at the boundary that makes it structural.

    The shaping happens inside ``read_surface_census``, the only caller of the
    injected script, so a raw accessible name has nowhere to go. This drives
    that function with a payload full of names and asserts that none of them
    is anywhere in what it returns -- not in a field, not in a key, not in a
    nested value.
    """
    page = _raw_page(RAW_CONTROLS)
    census = await dom.read_surface_census(page)
    blob = json.dumps(census)
    for identity in PLANTED:
        assert identity not in blob, f"{identity!r} survived the reader: {blob}"


def test_that_leak_detector_would_fire_on_an_unshaped_reader():
    """THE CONTROL for the test above, which would otherwise pass against a
    reader that returned nothing at all.

    The same detector is run over the RAW payload. It must find every planted
    identity there -- if it does not, the assertion above is vacuous.
    """
    blob = json.dumps(RAW_CONTROLS)
    missing = [identity for identity in PLANTED if identity not in blob]
    assert missing == [], missing


async def test_a_bare_name_with_no_href_is_the_reader_s_residue():
    """THE LIMIT OF THE READER, stated rather than left for someone to find.

    ``read_surface_census`` can refuse a name two ways: substitute it (the
    possessive, the paths) or recognise the control as an entity link. A
    control carrying a bare name and NO href gives it neither handle, so the
    name survives this function and is removed one layer later, by the
    singleton cap in ``census_aggregate`` -- which needs a count the reader
    does not have.

    The tool is what a caller sees and the tool is clean; this pins where the
    boundary actually is, so the next reader does not mistake the reader's
    guarantee for the whole of it.
    """
    orphan = {
        "tag": "button",
        "role": "button",
        "name": "Jane Doe",
        "name_source": "text",
        "has_href": False,
        "href": "",
        "aria_expanded": None,
        "disabled": False,
    }
    census = await dom.read_surface_census(_raw_page([orphan]))
    assert census["controls"][0]["shape"] == "Jane Doe"
    # And the counting pass is what removes it.
    shapes, _hrefs = shape.census_aggregate(census["controls"])
    assert shapes[0]["shape"] == "<redacted>"


async def test_the_reader_returns_the_counts_untouched():
    page = _raw_page(RAW_CONTROLS, forms=2, file_inputs=1, dialogs=3)
    census = await dom.read_surface_census(page)
    assert census["counts"] == {
        "forms": 2,
        "buttons": 2,
        "links": 3,
        "contenteditable": 1,
        "file_inputs": 1,
        "dialogs": 3,
    }
    assert census["controls_read"] == 3


async def test_the_reader_reports_a_failed_evaluate_as_a_failed_read():
    page = FakePage(url=FEED_URL, evaluate_result=RuntimeError("detached frame"))
    with pytest.raises(Exception) as caught:
        await dom.read_surface_census(page)
    assert "could not read the page" in str(caught.value)


# ---------------------------------------------------------------------------
# 5. The injected script reads and nothing else
# ---------------------------------------------------------------------------


def test_the_census_script_carries_no_mutating_token():
    """The same scan ``test_readonly.py`` runs, asserted here too because this
    is the one script in the package that goes looking at BUTTONS."""
    assert readonly.scan_js_for_mutations(dom.CENSUS_JS) == []


def test_that_scan_can_fail_on_this_script():
    """The control: the scanner is shown catching a mutation planted in the
    census script itself, so the assertion above is not vacuous."""
    planted = dom.CENSUS_JS.replace(
        "const controls = [];",
        "const controls = []; document.querySelector('button').click();",
    )
    assert ".click(" in readonly.scan_js_for_mutations(planted)


def test_the_script_never_scrolls():
    """Absent means UNKNOWN in this tool's output, and that promise is only
    honest while the script genuinely does not scroll."""
    for token in ("scrollIntoView", "window.scrollTo", "scrollBy", "scrollTop"):
        assert token not in dom.CENSUS_JS


# ---------------------------------------------------------------------------
# 6. The tool: a closed set of keys, one page, no navigation on refusal
# ---------------------------------------------------------------------------


@pytest.fixture
def drive(monkeypatch):
    """Point BROWSER at a FakePage, and record every navigation."""
    navigations: list[str] = []

    def install(page: FakePage) -> list[str]:
        @asynccontextmanager
        async def fake_session():
            yield page

        async def fake_goto(target_page, url, **kwargs):
            navigations.append(url)
            await target_page.goto(url)
            return target_page.url

        monkeypatch.setattr(browser_module.BROWSER, "session", fake_session)
        monkeypatch.setattr(browser_module.BROWSER, "goto", fake_goto)
        return navigations

    return install


def test_the_surface_table_is_a_closed_set_of_five():
    """FIVE SINCE 2026-08-31, and the count is in the name so a sixth arriving
    quietly is impossible: the set equality is what a new key has to get past,
    and the name is what a reader compares against the ruling block above the
    table in server.py."""
    assert set(CENSUS_SURFACES) == {
        "feed",
        "profile",
        "profile_edit_intro",
        "settings",
        "settings_dark_mode",
    }
    assert CENSUS_SURFACES["feed"] == FEED_URL
    assert CENSUS_SURFACES["profile"] == PROFILE_URL
    assert CENSUS_SURFACES["settings"] == SETTINGS_URL
    assert CENSUS_SURFACES["profile_edit_intro"] == PROFILE_EDIT_INTRO_URL
    assert CENSUS_SURFACES["settings_dark_mode"] == DARK_MODE_URL


def test_the_two_surfaces_ruled_on_2026_08_31_reach_one_page_each():
    """THE NARROWNESS OF THE RULING, asserted rather than described.

    The operator ruled two things: the profile editors are his to open, and
    ONE NAMED settings page at a time -- never the family, never a wildcard.
    A census key is the place that ruling is easiest to widen by accident,
    because a key is just a string beside a url.

    So both keys are pinned to their exact url, and the addresses each key
    would grow into are asserted refused by the read boundary. The
    account-ending pair is the reason this matters at all:
    ``/mypreferences/d/close-accounts`` and
    ``/mypreferences/d/hibernate-account`` are one wildcard away from a key
    like ``settings_dark_mode``.
    """
    assert readonly.is_read_url(PROFILE_EDIT_INTRO_URL) is True
    assert readonly.is_read_url(DARK_MODE_URL) is True

    for refused in (
        # The rest of his own editor family.
        "https://www.linkedin.com/in/me/edit/",
        "https://www.linkedin.com/in/me/edit/topcard/",
        # Another member's, which no pattern here may ever address.
        "https://www.linkedin.com/in/" + MEMBER_SLUG + "/edit/intro/",
        # The rest of the settings family, including the two that end an
        # account and the two named pages deliberately NOT admitted.
        "https://www.linkedin.com/mypreferences/d/close-accounts",
        "https://www.linkedin.com/mypreferences/d/hibernate-account",
        "https://www.linkedin.com/mypreferences/d/settings/language",
        "https://www.linkedin.com/mypreferences/d/settings/autoplay-videos",
        SETTINGS_URL + "categories/account",
    ):
        assert readonly.is_read_url(refused) is False, refused


@pytest.mark.parametrize(
    "surface",
    ["mynetwork", "network", "messaging", "messages", "inbox", "invitations"],
)
def test_the_three_surfaces_refused_on_a_side_effect_ruling_are_absent(surface):
    """THE GATE, as something that can fail rather than as a paragraph.

    Each of these was considered on 2026-08-30 and refused because LOADING the
    page costs something: /mynetwork/ carries the pending-invitation badge, and
    /messaging/ does not stay on a list at all -- LinkedIn redirects it into
    one specific conversation, measured twice, so a census there opens a
    stranger's thread. Notifications is the older member of the same set and
    has its own test above.

    A refusal that lives only in a comment is one refactor from being an
    oversight, so it is asserted on the KEY and on every url in the table.
    """
    assert surface not in CENSUS_SURFACES
    assert not any(surface in url for url in CENSUS_SURFACES.values())


def test_notifications_is_deliberately_not_a_surface():
    """It is the obvious third page and it is refused on a MEASURED cost:
    loading it clears the operator's unread badge, which a census would spend
    for nothing. The refusal is worth a test because the next person to look
    will reach for it."""
    assert "notifications" not in CENSUS_SURFACES
    assert not any("notifications" in url for url in CENSUS_SURFACES.values())


def test_every_surface_is_a_permitted_read_url():
    """Every key resolves to a url the read boundary admits.

    THE SENTENCE THIS DOCSTRING USED TO CARRY IS NO LONGER TRUE, and saying so
    is the point of rewriting it rather than deleting it. It read: "the tool
    adds no url that readonly.py did not already allow, which is why building
    it needed no edit to the navigation allowlist." That held for two surfaces
    and stopped holding on 2026-08-30, when ``settings`` was added and the
    navigation allowlist was deliberately widened by exactly one anchored
    pattern to admit it. The widening is recorded where it happened -- on the
    pattern in ``readonly.py`` and in the re-freeze note in
    ``test_readonly_boundary_invariant.py`` -- and a stale claim of "no edit
    was needed" sitting here would have been the one place a reader could have
    checked and been told the wrong thing.
    """
    for key, url in CENSUS_SURFACES.items():
        assert readonly.is_read_url(url), f"{key}: {url}"


def test_the_settings_key_reaches_the_index_and_not_the_toggles():
    """SHOWN FAILING on the widening this pattern exists to keep narrow.

    The value of a settings census is the INDEX -- which sections exist, and
    whether a section is url-addressed or opens as a modal. The COST would be
    the category pages, which is where the switches are. So the permission is
    anchored to the index and the pages below it are refused twice: they miss
    the anchored pattern, and they carry a forbidden substring.

    Both halves are asserted, because either one alone would pass against a
    boundary that had lost the other.
    """
    assert readonly.is_read_url(SETTINGS_URL)
    for below in (
        SETTINGS_URL + "categories/account",
        SETTINGS_URL + "categories/privacy",
        SETTINGS_URL + "?tab=account",
        "https://www.linkedin.com/psettings/",
    ):
        assert not readonly.is_read_url(below), below

    # And the SECOND gate specifically, since the anchored pattern alone would
    # already refuse these -- what is being certified here is that the
    # substring list now covers the settings family, which it did not before
    # 2026-08-30. Measured then: "/settings/" matched neither
    # /mypreferences/d/ nor /psettings/, so the "belt and braces" this list
    # documents itself as was not engaged for this surface at all.
    for below in (
        SETTINGS_URL + "categories/account",
        "https://www.linkedin.com/psettings/",
    ):
        with pytest.raises(errors.WriteAttemptError) as caught:
            readonly.assert_read_url(below)
        assert "contains" in str(caught.value), str(caught.value)


@pytest.mark.parametrize(
    "bad",
    [
        "notifications",
        "messaging",
        "https://www.linkedin.com/feed/",
        "/feed/",
        "FEED/../messaging",
        "",
        None,
    ],
)
async def test_an_unknown_surface_is_refused_without_navigating(drive, bad):
    """A URL NEVER COMES FROM THE ARGUMENT, and the refusal RETURNS.

    The url spellings in this list matter most: a caller passing a real url --
    even the very url the "feed" key resolves to -- is refused, because the
    argument is a KEY and is never a target. And nothing navigates: a refusal
    that reached ``BROWSER.goto`` first would have already loaded a page.
    """
    page = _raw_page(RAW_CONTROLS)
    navigations = drive(page)
    result = await linkedin_surface_census(bad)
    assert result["error"] == "unknown_surface"
    # Spelled out rather than derived from CENSUS_SURFACES: comparing the
    # answer against the same dict that produced it could not fail.
    assert result["valid_surfaces"] == [
        "feed",
        "profile",
        "profile_edit_intro",
        "settings",
        "settings_dark_mode",
    ]
    assert navigations == []
    assert page.evaluations == []


async def test_the_key_is_matched_case_and_space_insensitively(drive):
    page = _raw_page(RAW_CONTROLS)
    navigations = drive(page)
    result = await linkedin_surface_census("  FEED ")
    assert result["surface"] == "feed"
    assert navigations == [FEED_URL]


async def test_a_census_loads_exactly_one_page_and_reads_it_once(drive):
    page = _raw_page(RAW_CONTROLS)
    navigations = drive(page)
    result = await linkedin_surface_census("feed")
    assert navigations == [FEED_URL]
    assert result["pages_loaded"] == 1
    assert len(page.evaluations) == 1
    assert page.evaluations[0][0] is dom.CENSUS_JS


async def test_the_profile_surface_opens_the_same_url_my_profile_does(drive):
    page = FakePage(url=PROFILE_URL, evaluate_result=_payload([]))
    navigations = drive(page)
    await linkedin_surface_census("profile")
    assert navigations == [PROFILE_URL]


async def test_the_tool_result_carries_no_member_name(drive):
    """End to end, with the same detector the reader test uses."""
    page = _raw_page(RAW_CONTROLS)
    drive(page)
    result = await linkedin_surface_census("feed")
    blob = json.dumps(result)
    for identity in PLANTED:
        assert identity not in blob, f"{identity!r} reached a tool result"


async def test_the_result_has_the_shape_a_caller_is_promised(drive):
    page = _raw_page(RAW_CONTROLS)
    drive(page)
    result = await linkedin_surface_census("feed")
    assert result["surface"] == "feed"
    assert result["source_url"] == FEED_URL
    assert set(result["counts"]) == {
        "forms",
        "buttons",
        "links",
        "contenteditable",
        "file_inputs",
        "dialogs",
    }
    assert isinstance(result["control_shapes"], list)
    assert isinstance(result["href_shapes"], dict)
    for row in result["control_shapes"]:
        assert set(row) == {
            "shape",
            "count",
            "tag",
            "role",
            "name_source",
            "has_href",
            "href_shape",
            "aria_expanded",
            "disabled",
        }


async def test_an_auth_wall_is_reported_as_a_failed_read_not_an_empty_census(drive):
    """An empty census and a signed-out bounce must never look alike."""
    page = _raw_page(RAW_CONTROLS)
    page.redirect_to = "https://www.linkedin.com/login?session_redirect=%2Ffeed"
    drive(page)
    result = await linkedin_surface_census("feed")
    assert result["error"] == "not_authenticated"
    assert "control_shapes" not in result


async def test_truncation_is_reported_rather_than_silently_cutting(drive):
    payload = _payload(RAW_CONTROLS)
    payload["truncated"] = True
    page = FakePage(url=FEED_URL, evaluate_result=payload)
    drive(page)
    result = await linkedin_surface_census("feed")
    assert result["truncated"] is True
    assert str(dom.CENSUS_MAX_CONTROLS) in result["truncated_note"]


# ---------------------------------------------------------------------------
# 7. The docstring is where the honesty lives, so it is asserted
# ---------------------------------------------------------------------------


def _doc() -> str:
    """The docstring as one lowercased line.

    Whitespace is COLLAPSED because a docstring is wrapped for a reader, not
    for a matcher: "It is not a\n    job-search tool" is the same promise as
    the unwrapped form, and an assertion that fails on the line break is
    testing the reflow rather than the claim.
    """
    return " ".join((linkedin_surface_census.__doc__ or "").lower().split())


def test_the_docstring_says_it_is_an_instrument_and_not_a_feature():
    doc = _doc()
    assert "instrument" in doc
    assert "not a job-search tool" in doc


def test_the_docstring_says_it_loads_one_page_and_clicks_nothing():
    doc = _doc()
    assert "exactly one page" in doc
    assert "clicks nothing" in doc


def test_the_docstring_refuses_to_let_presence_read_as_permission():
    """The sentence that stops this tool being quoted as a green light."""
    assert "is not evidence that activating it is safe" in _doc()


def test_the_docstring_says_absent_means_unknown_never_zero():
    """The exact phrasing ``linkedin_my_profile`` already uses, matched so the
    two surfaces do not teach a caller two different things."""
    doc = _doc()
    assert "unknown, never zero" in doc
    assert "scroll" in doc


def test_the_docstring_says_the_census_reports_shapes():
    doc = _doc()
    assert "shapes, never names" in doc
    assert "count of 1" in doc


def test_the_docstring_explains_why_notifications_is_absent():
    doc = _doc()
    assert "notifications" in doc
    assert "badge" in doc


def test_the_docstring_makes_no_write_claim():
    """The same check ``test_server_surface.py`` runs across the surface,
    asserted here as well because this docstring NAMES several write
    capabilities while denying that it performs them -- which is exactly the
    sentence the negation window exists to permit, and exactly the one that
    would go wrong quietly."""
    assert readonly.docstring_write_claims(linkedin_surface_census.__doc__ or "") == []


def test_the_tool_name_does_not_imply_a_write():
    assert readonly.name_implies_write("linkedin_surface_census") is False


# ---------------------------------------------------------------------------
# The settings redirect: the second gate is a gate on what is ASKED FOR
# ---------------------------------------------------------------------------
#
# MEASURED LIVE 2026-08-30. ``linkedin_surface_census(surface="settings")`` was
# run against the operator's account and came back
#
#     "source_url": "https://www.linkedin.com/mypreferences/d/categories/account"
#
# having been asked for ``https://www.linkedin.com/mypreferences/d/``. LinkedIn
# REDIRECTS the settings index onto a category page -- and the category family
# is precisely what was added to ``_FORBIDDEN_URL_SUBSTRINGS`` that same
# morning, as the "second, independent gate" behind the newly widened
# allowlist.
#
# SO THE CENSUS LANDED ON A URL ITS OWN DENYLIST REFUSES. Nothing was breached:
# the page it read is the settings index's own account section, which is what
# the ruling intended to permit, and the census clicks nothing. What is false
# is a sentence somebody could reasonably infer from readonly.py -- that the
# forbidden list keeps this server OFF those addresses. It keeps this server
# from ASKING for them. ``assert_read_url`` gates the requested url and the
# landed url is never re-checked, which readonly.py already states in the
# messaging comment and which is now measured a second time on a second family.
#
# WHY THIS IS PINNED RATHER THAN FIXED. Re-checking the landed url would break
# two working tools deliberately: ``linkedin_open_messaging`` is DESIGNED to
# land on a thread url, and this census is designed to land wherever the
# settings index sends it. Both are documented, both were ruled on. A guard
# added here would refuse them, and quietly widening the allowlist to admit the
# category page instead would undo the ruling that put it on the denylist. The
# honest artefact is this test.


def test_the_settings_index_is_permitted_and_its_landing_page_is_not():
    """The requested url passes the read door; the url LinkedIn serves does not.

    Both halves are asserted because either alone is a different, weaker
    claim. That the index is allowed is what makes the census possible; that
    the destination is forbidden is what makes the redirect a finding.
    """
    requested = CENSUS_SURFACES["settings"]
    assert requested == "https://www.linkedin.com/mypreferences/d/"
    assert readonly.is_read_url(requested) is True

    # The url the live run actually landed on, 2026-08-30.
    landed = "https://www.linkedin.com/mypreferences/d/categories/account"
    assert readonly.is_read_url(landed) is False
    # And it is the DENYLIST that refuses it, not merely the allowlist -- which
    # is the whole point of the entry added that morning. Checked by finding
    # the substring rather than by trusting the refusal's wording.
    assert any(
        bad in landed.lower() for bad in readonly._FORBIDDEN_URL_SUBSTRINGS
    )


def test_the_read_door_is_documented_as_gating_the_request_and_not_the_landing():
    """The property that makes the redirect reachable, asserted on the guard.

    ``assert_read_url`` takes a url and returns it. There is no landed-url
    parameter and no post-navigation hook, so a redirect cannot be caught by
    it -- and that is a fact about the signature rather than about any caller.
    Pinned so that somebody adding such a check has to come here and read why
    two shipped tools would break.
    """
    import inspect

    signature = inspect.signature(readonly.assert_read_url)
    assert list(signature.parameters) == ["url"]
    # The other measured redirect in this package, kept beside it so the two
    # are read as one class rather than as two curiosities.
    assert readonly.is_read_url("https://www.linkedin.com/messaging/") is True
    assert (
        readonly.is_read_url(
            "https://www.linkedin.com/messaging/thread/2-abcdef123456/"
        )
        is True
    )
# ---------------------------------------------------------------------------
# 8. Name resolution over a REAL DOM: the two label routes
# ---------------------------------------------------------------------------
#
# WHY THIS SECTION LAUNCHES A BROWSER when nothing else in this file does.
# Everything above tests Python -- the shaper, the cap, the reader's contract,
# the tool's wiring -- and every one of those can be driven from a FakePage
# because the thing under test is Python. NAME RESOLUTION IS NOT PYTHON. It
# lives in the injected script and it asks questions only a laid-out document
# can answer (``el.labels``, ``closest('label')``). A FakePage handing back a
# payload somebody typed would certify the payload, which is precisely how the
# gap below survived five surfaces without anyone noticing.
#
# THE GAP, MEASURED LIVE 2026-08-31. ``linkedin_surface_census(
# "profile_edit_intro")`` was run twice against ``/in/me/edit/intro/`` and both
# runs came back identical: 67 controls, ``forms: 1``, and three ``input``
# controls at ``name_source: "none"`` with an empty shape. The sibling capture
# on ``settings_dark_mode`` resolved its three inputs through
# ``aria-labelledby``, so the instrument was not simply broken.
#
# It was BLIND, and blind in a way that read as a finding: every surface
# censused before that day was made of buttons and anchors, which LinkedIn
# labels with ``aria-label``. The profile editor is the first surface made of
# FORM FIELDS, and a form field is named by a ``<label>`` -- the one route the
# chain never tried. ``name_source: "none"`` was being read as "this control
# carries no name" when what it meant was "this instrument cannot read one",
# which is the conflation this package exists to refuse.
#
# The harness is the one in ``test_apply_modal_fixture.py``, copied rather than
# imported for the same reason that file copied ``test_apply_fixture.py``: one
# browser per test, one ISOLATED CONTEXT per reading, and ``window.innerWidth``
# asserted on every measurement rather than once at setup, so no answer below
# was taken at a width nobody recorded.

CENSUS_VIEWPORT = {"width": 1280, "height": 720}

#: SIX form controls, in document order, each a different route to a name.
#:
#: INVENTED, and deliberately not written into ``tests/fixtures/``: nothing
#: here was ever served by LinkedIn, and invented markup filed beside real
#: captures is how invented markup starts being read as evidence. It carries
#: no slug, no urn, no address and no id shape -- ``test_no_committed_identity``
#: reads this file.
LABEL_FORM_HTML = (
    "<!doctype html><html><body><form>"
    # 0 -- a SIBLING label pointing at the input by id. The ordinary profile
    # editor shape, and the route the chain did not have.
    '<label for="c-headline">Headline</label>'
    '<input id="c-headline" type="text">'
    # 1 -- an ANCESTOR label wrapping the input. No id anywhere, so the route
    # above cannot reach it and the wrapper is the only name it has.
    '<label>Current company<input type="text"></label>'
    # 2 -- BOTH, and aria-label has to win. That is the ARIA order, and it is
    # also the compatibility constraint: every surface already measured was
    # named through aria-label, so a label route that outranked it would
    # silently rename controls in captures already in the audit record.
    '<label for="c-pronouns">Pronouns</label>'
    '<input id="c-pronouns" type="text" aria-label="Pronouns, choose one">'
    # 3 -- title AND a label, and title has to win. This is NARROWER than the
    # accessible-name spec, which puts a native label ahead of title; the
    # narrow order is chosen so that no control that already resolved through
    # title on a measured surface can change its name under this edit. Pinned
    # here so the deviation is reviewable instead of discovered.
    '<label for="c-industry">Industry</label>'
    '<input id="c-industry" type="text" title="Industry, start typing">'
    # 4 -- a label carrying a PERSON'S NAME, with the curly apostrophe
    # LinkedIn actually serves. Labels are a NEW source of page text into the
    # census and the shaping was written when there were three sources, so the
    # fourth is shown going through it.
    '<label for="c-note">Reply to Jane Doe' + CURLY + 's message</label>'
    '<input id="c-note" type="text">'
    # 5 -- named by nothing at all. The residue: a fall-through that invented
    # a name for this one would be worse than the blind spot it replaced.
    '<input id="c-bare" type="text">'
    "</form></body></html>"
)

ROW_LABEL_FOR = 0
ROW_LABEL_ANCESTOR = 1
ROW_ARIA_BEATS_LABEL = 2
ROW_TITLE_BEATS_LABEL = 3
ROW_LABEL_CARRYING_A_NAME = 4
ROW_NAMED_BY_NOTHING = 5


@pytest.fixture
async def census_over():
    """Run ``work(page)`` over frozen markup. One browser, a context per read.

    ``window.innerWidth`` is asserted on EVERY measurement. Name resolution
    does not depend on layout, but ``innerText`` does -- an ancestor label's
    name IS its rendered text -- so a reading taken at an unknown width is a
    reading whose conditions were not recorded.
    """
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        async def _run(html: str, work):
            context = await browser.new_context(viewport=dict(CENSUS_VIEWPORT))
            try:
                page = await context.new_page()
                await page.set_content(
                    html, wait_until="domcontentloaded", timeout=60_000
                )
                width = await page.evaluate("window.innerWidth")
                assert width == CENSUS_VIEWPORT["width"], (
                    f"the page laid out at {width}px, not "
                    f"{CENSUS_VIEWPORT['width']}px. Every name read below came "
                    "off a document whose conditions were not recorded."
                )
                return await work(page)
            finally:
                await context.close()

        try:
            yield _run
        finally:
            await browser.close()


def _census_cfg() -> dict[str, Any]:
    """The config ``read_surface_census`` passes, built from ``dom``'s own
    constants so a change there drags these readings with it."""
    return {
        "controlSelector": dom.CENSUS_CONTROL_SELECTOR,
        "maxControls": dom.CENSUS_MAX_CONTROLS,
        "maxChars": 300,
    }


async def _label_form_rows(census_over) -> list[dict[str, Any]]:
    """The SHAPED census of :data:`LABEL_FORM_HTML`, read the production way.

    Deliberately through ``read_surface_census`` and not through a bare
    ``evaluate``: the rows below are what a caller would actually receive,
    shaping included, so nothing here can pass on a raw name a caller never
    sees.
    """

    async def work(page):
        return await dom.read_surface_census(page)

    census = await census_over(LABEL_FORM_HTML, work)
    rows = census["controls"]
    assert len(rows) == 6, (
        f"the fixture yielded {len(rows)} controls, not 6 -- every ROW_ index "
        "below is now pointing at the wrong control."
    )
    # The shape the live capture had, so the fixture is answering the same
    # question the profile editor asked.
    assert census["counts"]["forms"] == 1
    assert census["counts"]["contenteditable"] == 0
    return rows


async def test_a_sibling_label_for_names_the_input_it_points_at(census_over):
    """THE BLIND SPOT, red before the fall-through existed.

    An ``<input id=x>`` with a ``<label for="x">`` beside it is the single
    most ordinary named form control on the web, and this census reported it
    as nameless.
    """
    row = (await _label_form_rows(census_over))[ROW_LABEL_FOR]
    assert row["name_source"] == "label-for"
    assert row["shape"] == "Headline"


async def test_a_label_wrapping_an_input_names_it(census_over):
    """The second standard route, and the one no id can reach: the control is
    named by the element it sits inside."""
    row = (await _label_form_rows(census_over))[ROW_LABEL_ANCESTOR]
    assert row["name_source"] == "label-ancestor"
    assert row["shape"] == "Current company"


async def test_the_two_label_routes_are_reported_separately(census_over):
    """They are not collapsed into one ``label`` source, and that is the whole
    value of ``name_source``: it says WHERE the string came from, so a reader
    costing a capability can tell a labelled field from a wrapped one without
    going back to the page."""
    rows = await _label_form_rows(census_over)
    assert (
        rows[ROW_LABEL_FOR]["name_source"]
        != rows[ROW_LABEL_ANCESTOR]["name_source"]
    )
    sources = {row["name_source"] for row in rows}
    assert {"label-for", "label-ancestor"} <= sources


async def test_aria_label_still_beats_a_label_element(census_over):
    """PRECEDENCE, and it is a compatibility contract rather than a taste.

    Every control on every surface measured before 2026-08-31 was named
    through ``aria-label``. A label route that outranked it would rename
    controls in captures already written into the audit record, which would
    make those captures wrong without anything in the diff saying so.
    """
    row = (await _label_form_rows(census_over))[ROW_ARIA_BEATS_LABEL]
    assert row["name_source"] == "aria-label"
    assert row["shape"] == "Pronouns, choose one"


async def test_title_still_beats_a_label_element(census_over):
    """The same argument one step down the chain, and the deviation from the
    accessible-name spec is deliberate: the spec ranks a native label ABOVE
    title, and adopting that order here would move any already-measured
    control that resolved through title. The narrow order moves nothing."""
    row = (await _label_form_rows(census_over))[ROW_TITLE_BEATS_LABEL]
    assert row["name_source"] == "title"
    assert row["shape"] == "Industry, start typing"


async def test_a_name_in_a_label_is_shaped_like_a_name_in_an_aria_label(
    census_over,
):
    """THE PRIVACY RULE, applied to the new source of text.

    Shapes, never names. A label is a fourth way for page text to enter the
    census and the shaping was written when there were three, so this drives
    a person's name in through the new route and asserts it comes out shaped
    -- through the same ``census_shape`` call, in the same place, with no
    branch of its own.
    """
    row = (await _label_form_rows(census_over))[ROW_LABEL_CARRYING_A_NAME]
    assert row["name_source"] == "label-for"
    assert row["shape"] == "Reply to <member>'s message"
    assert "Jane Doe" not in json.dumps(row)


async def test_that_redaction_check_would_notice_a_reader_that_stopped_shaping(
    census_over,
):
    """THE CONTROL for the test above, which a script returning nothing at all
    would also pass. The RAW script is run over the same markup and has to be
    caught carrying the name, so the assertion above is not vacuous."""

    async def work(page):
        return await page.evaluate(dom.CENSUS_JS, _census_cfg())

    raw = await census_over(LABEL_FORM_HTML, work)
    name = raw["controls"][ROW_LABEL_CARRYING_A_NAME]["name"]
    assert "Jane Doe" in name
    assert shape.census_shape(name) == "Reply to <member>'s message"


async def test_an_input_named_by_nothing_is_still_reported_as_nothing(
    census_over,
):
    """The fall-through does not invent. A control with no label, no aria and
    no title stays ``none`` with an empty shape -- which is what
    ``name_source: "none"`` is now allowed to mean."""
    row = (await _label_form_rows(census_over))[ROW_NAMED_BY_NOTHING]
    assert row["name_source"] == "none"
    assert row["shape"] == ""


# ---------------------------------------------------------------------------
# 8b. What ELSE moved, measured over every committed fixture
# ---------------------------------------------------------------------------
#
# The risk this edit carries is not that the label routes fail to fire. It is
# that they fire somewhere they did not before and quietly RENAME a control on
# a surface already captured, at which point the readings in ``_audit/``
# describe an instrument that no longer exists and nothing says so.
#
# So it was measured rather than argued. Both scripts -- the real one, and one
# with the label call site deleted -- were run over all 19 committed fixtures,
# 537 controls, on 2026-08-31. TWENTY-EIGHT controls move, and the shape of the
# movement is the whole finding:
#
#   * 26 ``input`` controls go from ``none`` to ``label-for``. Their published
#     shape was the empty string. These ARE the blind spot -- and they sit in
#     ``apply_modal_derived.html`` and both job-tracker captures, which means
#     the gap was already committed to this repo in captures of the Easy Apply
#     modal and the tracker, not only on the profile editor that found it.
#   * 2 ``select`` controls go from ``text`` to ``label-for``, and both are the
#     same language picker in a page footer. Its ``text`` name was the whole
#     option list -- 36 languages in a dozen scripts -- which the shaper
#     refused as ``<opaque>``. Through the label route it reads
#     ``Select language``, which is what a screen reader says.
#
# NOT ONE control whose published shape was a READABLE NAME changed. That is
# the invariant the first test below asserts and it is the one that decides
# whether captures already taken are still true: every mover was previously
# either nameless or unreadable, so no earlier reading is contradicted. A
# non-answer became an answer.

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"

#: The label call site, exactly as ``CENSUS_JS`` spells it. Deleting it is the
#: minimal neutralisation: the resolver stays defined and unreferenced, so the
#: derived script differs from the real one in one behaviour and nothing else.
LABEL_ROUTE_CALL = (
    "    const labelled = labelRoutes(el);\n"
    "    if (labelled) return labelled;\n"
)

#: The two transitions the sweep found, named so the map below reads as two
#: kinds of movement rather than as twenty-eight rows.
INPUT_NAMED = ("input", "none", "label-for")
SELECT_RENAMED = ("select", "text", "label-for")

#: EVERY control that moves, file by file, measured 2026-08-31. Pinned rather
#: than summarised: a count alone would go on passing if the routes stopped
#: firing on the tracker and started firing somewhere new.
FIXTURE_MOVEMENT = {
    "apply_modal_derived.html": [INPUT_NAMED] * 2,
    "job_detail_following.html": [SELECT_RENAMED],
    "job_detail_shell.html": [SELECT_RENAMED],
    "jobs_tracker_empty.html": [INPUT_NAMED] * 12,
    "jobs_tracker_row.html": [INPUT_NAMED] * 12,
}

#: Controls read across the whole fixture directory, and the denominator of
#: "28 moved". Pinned because a sweep whose size nobody recorded can shrink.
FIXTURE_CONTROLS = 537


def _census_without_label_routes() -> str:
    derived = dom.CENSUS_JS.replace(LABEL_ROUTE_CALL, "", 1)
    assert derived != dom.CENSUS_JS, (
        "LABEL_ROUTE_CALL no longer appears in CENSUS_JS, so this derivation "
        "is the real script wearing another name and the comparison below "
        "certifies nothing. Repoint the anchor at the label call site."
    )
    return derived


def _fixture_text(path: Path) -> str:
    """utf-8, and the difference from the rest of the suite is deliberate.

    ``test_apply_fixture.py`` reads ITS fixture as ascii because that fixture
    is DERIVED and this repo writes derived markup as ASCII bytes. The sweep
    below reads all nineteen, and the profile-views pair are captures carrying
    raw non-ASCII. Reading those as ascii fails on a property of the capture
    rather than of this edit, which is a worse failure than none.
    """
    return path.read_text(encoding="utf-8")


async def _label_route_movement(census_over, html: str) -> list[dict[str, Any]]:
    """Every control the two scripts disagree about, reported SHAPED.

    Each row carries the tag, the two ``name_source`` values and the two
    SHAPED names -- never the raw ones. A failure message quoting a raw
    accessible name would put one into a CI log, which is the thing this whole
    file exists to prevent.
    """
    derived = _census_without_label_routes()
    cfg = _census_cfg()

    async def work(page):
        return (
            await page.evaluate(dom.CENSUS_JS, cfg),
            await page.evaluate(derived, cfg),
        )

    live, without = await census_over(html, work)
    after, before = live["controls"], without["controls"]
    assert len(after) == len(before)
    return [
        {
            "index": index,
            "tag": new["tag"],
            "before": old["name_source"],
            "after": new["name_source"],
            "before_shape": shape.census_shape(old["name"]),
            "after_shape": shape.census_shape(new["name"]),
        }
        for index, (new, old) in enumerate(zip(after, before))
        if new != old
    ]


async def _sweep(census_over) -> tuple[dict[str, list[dict[str, Any]]], int]:
    """Run the comparison over every committed fixture. Returns the movers and
    the number of controls read, so a shrinking sweep is visible."""
    fixtures = sorted(FIXTURE_DIR.glob("*.html"))
    assert len(fixtures) >= 19, "the fixture directory shrank; this proof did too"
    found: dict[str, list[dict[str, Any]]] = {}
    total = 0

    async def count(page):
        return len((await page.evaluate(dom.CENSUS_JS, _census_cfg()))["controls"])

    for path in fixtures:
        html = _fixture_text(path)
        moved = await _label_route_movement(census_over, html)
        total += await census_over(html, count)
        if moved:
            found[path.name] = moved
    return found, total


async def test_no_committed_fixture_loses_a_readable_name_to_the_label_routes(
    census_over,
):
    """THE INVARIANT THAT DECIDES WHETHER OLD CAPTURES ARE STILL TRUE.

    A control that moves is fine if what it moved FROM said nothing -- an
    empty shape, or ``<opaque>``. A control that moves away from a readable
    name is a rename, and a rename means every census already written down
    reported a name this instrument no longer reports. That is a much larger
    change than this one and it would have to be argued on its own; here it
    must simply not happen.
    """
    found, _total = await _sweep(census_over)
    renamed = [
        (name, row["index"], row["before_shape"], row["after_shape"])
        for name, rows in found.items()
        for row in rows
        if row["before_shape"] not in ("", shape.CENSUS_OPAQUE)
    ]
    assert renamed == [], renamed


async def test_the_movement_the_label_routes_cause_is_pinned_file_by_file(
    census_over,
):
    """The receipt for the paragraph above: what moved, where, and how much of
    the repo was read to find out. Pinned per file rather than totalled, so
    the routes cannot stop firing in one place and start in another while a
    count stays flat."""
    found, total = await _sweep(census_over)
    summary = {
        name: [(row["tag"], row["before"], row["after"]) for row in rows]
        for name, rows in found.items()
    }
    assert summary == FIXTURE_MOVEMENT
    assert sum(len(rows) for rows in summary.values()) == 28
    assert total == FIXTURE_CONTROLS, (
        f"the sweep read {total} controls, not {FIXTURE_CONTROLS}. A fixture "
        "changed, so FIXTURE_MOVEMENT above was measured against a directory "
        "that no longer exists -- re-measure it rather than moving this number."
    )


async def test_that_sweep_can_detect_movement(census_over):
    """THE CONTROL. The same comparison over the label fixture has to find the
    three controls the routes were added for -- otherwise the sweep above is a
    sweep that could not have failed."""
    moved = await _label_route_movement(census_over, LABEL_FORM_HTML)
    assert [row["index"] for row in moved] == [
        ROW_LABEL_FOR,
        ROW_LABEL_ANCESTOR,
        ROW_LABEL_CARRYING_A_NAME,
    ]
    assert [row["before"] for row in moved] == ["none", "none", "none"]
    assert [row["after"] for row in moved] == [
        "label-for",
        "label-ancestor",
        "label-for",
    ]
