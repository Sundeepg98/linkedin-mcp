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

Nothing here launches Chromium or reaches LinkedIn.
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
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


def test_the_surface_table_is_a_closed_set_of_three():
    assert set(CENSUS_SURFACES) == {"feed", "profile", "settings"}
    assert CENSUS_SURFACES["feed"] == FEED_URL
    assert CENSUS_SURFACES["profile"] == PROFILE_URL
    assert CENSUS_SURFACES["settings"] == SETTINGS_URL


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
    assert result["valid_surfaces"] == ["feed", "profile", "settings"]
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
