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
import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import dom, errors, readonly, shape
from linkedin_server import server as server_module
from linkedin_server.server import (
    CENSUS_ITEM_RULES,
    CENSUS_RESOLVED_SURFACES,
    CENSUS_SETTLED_CONTROLS,
    CENSUS_SURFACES,
    census_settle_report,
    census_surface_keys,
    linkedin_surface_census,
)
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
    """The merge key is a NAMED SET OF FIELDS, not the name -- and not the
    whole record either, which is what this docstring claimed until
    2026-08-31 and what let two added fields be dropped in silence.

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


def test_the_surface_table_is_a_closed_set_of_eight_plus_one_resolved():
    """EIGHT DIRECT KEYS AND ONE RESOLVED, and the count is in the name so a
    tenth arriving quietly is impossible: the set equality is what a new key
    has to get past, and the name is what a reader compares against the ruling
    block above the table in server.py.

    FIVE UNTIL 2026-08-31. Four surfaces were ruled in that day, each named
    individually by the operator and never as a family, and one of them --
    ``feed_item`` -- is NOT in this table at all: its url carries a urn that
    only a live read can supply, so it lives in ``CENSUS_RESOLVED_SURFACES``
    and is asserted separately below. The split exists because a table entry
    that is not the url actually loaded makes every other guard on this table
    weaker; the first draft used a placeholder and
    ``test_every_surface_is_a_permitted_read_url`` caught it.
    """
    assert set(CENSUS_SURFACES) == {
        "feed",
        "profile",
        "profile_edit_intro",
        "settings",
        "settings_dark_mode",
        "post_composer",
        "article_composer",
        "messaging_compose",
        "premium",
    }
    assert CENSUS_RESOLVED_SURFACES == {"feed_item", "feed_item_commented"}
    # EVERY RESOLVED SURFACE NAMES ITS SELECTION RULE. A resolved key with no
    # rule would fall through to a KeyError at call time, on a path that has
    # already loaded a page.
    assert set(CENSUS_ITEM_RULES) == CENSUS_RESOLVED_SURFACES
    # THE TWO SETS ARE DISJOINT AND THEIR UNION IS WHAT A CALLER IS OFFERED.
    # Without this a key could be in both and the refusal branch would never
    # be reached for it.
    assert not (set(CENSUS_SURFACES) & CENSUS_RESOLVED_SURFACES)
    assert census_surface_keys() == sorted(
        set(CENSUS_SURFACES) | CENSUS_RESOLVED_SURFACES
    )
    assert len(census_surface_keys()) == 11
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
    assert surface not in CENSUS_RESOLVED_SURFACES


@pytest.mark.parametrize(
    "url",
    [
        "https://www.linkedin.com/mynetwork/",
        "https://www.linkedin.com/notifications/",
        "https://www.linkedin.com/messaging/",
        "https://www.linkedin.com/messaging/thread/2-abc/",
    ],
)
def test_no_key_points_at_a_surface_refused_on_a_side_effect_ruling(url):
    """THE URL HALF OF THE SAME GATE, and it had to be rewritten rather than
    kept.

    It used to read ``not any(surface in url for url in ...)`` -- a SUBSTRING
    test over the table's values, with ``surface`` being the bare word
    ``"messaging"``. That stopped working the day ``/messaging/compose/`` was
    admitted by name, and the shape of the failure is worth recording: the
    check was not wrong about the composer, it simply could not tell
    ``/messaging/compose/`` (ruled in, one url, badge read zero first) from
    ``/messaging/`` (never ruled in, redirects into somebody's conversation).
    A substring cannot make that distinction and should not have been asked
    to.

    So the addresses are named in full and asserted absent as ADDRESSES. The
    composer's neighbours are here for exactly the reason the composer is not.
    """
    assert url not in set(CENSUS_SURFACES.values())


def test_notifications_is_deliberately_not_a_surface():
    """It is the obvious third page and it is refused on a MEASURED cost:
    loading it clears the operator's unread badge, which a census would spend
    for nothing. The refusal is worth a test because the next person to look
    will reach for it."""
    assert "notifications" not in CENSUS_SURFACES
    assert "notifications" not in CENSUS_RESOLVED_SURFACES
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

    # AND THE RESOLVED SURFACE, whose url does not exist until a live read has
    # produced a urn. It cannot be in the table -- a table entry that is not
    # the url actually loaded makes the loop above answer a question about a
    # string nobody uses, which is exactly what the first draft did -- so it
    # is checked here against a SYNTHETIC urn of the shape the reader will
    # only ever emit.
    #
    # THE SHAPE IS THE READER'S OWN, not a second spelling written here:
    # dom.ACTIVITY_ITEMS_JS refuses to publish a key that does not match
    # ``urn:li:<type>:<digits>``, so a urn this url could be built from is
    # necessarily one this pattern admits.
    assert CENSUS_RESOLVED_SURFACES == {"feed_item", "feed_item_commented"}
    synthetic = server_module.ITEM_PERMALINK_URL.format(
        urn="urn:li:activity:" + ACTIVITY_ID
    )
    assert readonly.is_read_url(synthetic), synthetic
    # And the shapes it must NOT be buildable into, so "the permalink opens"
    # is not read as "that family opens".
    for refused in (
        server_module.ITEM_PERMALINK_URL.format(urn="urn:li:activity:1/edit"),
        server_module.ITEM_PERMALINK_URL.format(urn="not-a-urn"),
        server_module.ITEM_PERMALINK_URL.format(urn=""),
    ):
        assert not readonly.is_read_url(refused), refused


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
        "article_composer",
        "feed",
        "feed_item",
        "feed_item_commented",
        "messaging_compose",
        "post_composer",
        "premium",
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
    # THE ROW'S WHOLE KEY SET, and the reason it is asserted as an equality
    # rather than a subset: this is the promise a caller reads, and a field
    # that reaches the merge key but not this assertion would be a column
    # nobody was told about. ``checked`` and ``checked_source`` arrived
    # 2026-08-31 and this test is where their arrival at the TOOL is pinned --
    # it went red on the edit that added them, which is how it was confirmed
    # that the merge key is what carries a field the last step out.
    for row in result["control_shapes"]:
        assert set(row) == {
            "shape",
            "count",
            "tag",
            "input_type",
            "role",
            "name_source",
            "has_href",
            "href_shape",
            "aria_expanded",
            "disabled",
            "checked",
            "checked_source",
            "containers",
        }
    # AND THE SAME SET, DERIVED. The literal above is what a caller is
    # promised; this says the promise is exactly the merge key plus the two
    # fields that are not part of it. Written as a second assertion rather
    # than replacing the first, because a pin that derives itself from the
    # code it is pinning cannot catch a field arriving -- it is the literal
    # that goes red, and it did, on the edit that added ``input_type``.
    for row in result["control_shapes"]:
        assert set(row) == set(shape.CENSUS_KEY_FIELDS) | {"count", "containers"}


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
    """THE SAFETY CLAIM, AND ITS ONE EXCEPTION, both asserted.

    The docstring said "IT LOADS EXACTLY ONE PAGE AND CLICKS NOTHING" and that
    stopped being uniformly true on 2026-08-31, when ``feed_item`` arrived --
    a surface whose url is a permalink this server has to READ before it can
    build. Two loads, not one.

    So this asserts the claim AND the exception by name. Deleting the
    assertion would have been the wrong repair and quietly widening the claim
    to "one or two pages" would have been worse: what makes a sentence like
    this worth anything is that a reader can act on it, and "one page, except
    on the surface that loads two, which says so in pages_loaded" is
    actionable where a range is not.
    """
    doc = _doc()
    assert "exactly one page" in doc
    assert "clicks nothing" in doc
    # THE EXCEPTION, NAMED. A claim with an unstated exception is the shape
    # this package keeps finding in its own docstrings.
    assert "feed_item" in doc
    assert "exactly two" in doc
    assert "pages_loaded" in doc


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


# ---------------------------------------------------------------------------
# 8c. WHICH CONTAINER a control sits in
# ---------------------------------------------------------------------------
#
# THE GAP, and it is a gap in what the census can SAY rather than in what it
# reads. ``linkedin_surface_census("profile_edit_intro")`` was run four times
# against the intro editor and the two most recent agree exactly: 256
# controls, ``forms: 2``, ``dialogs: 5``. The editor is a DIALOG drawn inside
# a full profile render, and the same page draws an ad-report dialog and an
# activity rail -- so the flat list carries ``Save`` (button, enabled),
# ``Submit`` (button, disabled, count 2), ``Additional name``, ``City``,
# ``Comments`` and ``Posts`` with nothing in it saying which of the five
# dialogs or two forms any of them belongs to.
#
# TWO SEPARATE READERS then guessed at that FROM ADJACENCY IN THE FLAT LIST:
# ``Comments``/``Posts`` sitting near profile fields read as profile fields,
# and ``Save`` near them read as the editor's commit control. Adjacency in
# this list is ``querySelectorAll`` order, which is document order, and
# document order is not containment -- on that page the control after a
# profile field can be a rail filter. Neither reading was measured, and one of
# them decides whether a capability is reachable.
#
# WHAT THE DESCRIPTOR IS ALLOWED TO BE: A SHAPE, NEVER A NAME. Containers are
# a NEW source of page text into this census -- a dialog is named by an
# ``aria-label``, a section by its heading, and either can be a member -- so
# the descriptor is built from STRUCTURE ONLY: the container's tag or role,
# plus a per-document index in document order. No heading, no label, no id, no
# class. The privacy test below is the certification, and it drives a person's
# name in through all four of those routes at once.
#
# WHY EVERY READING BELOW IS TAKEN OFF THE RAW SCRIPT rather than through
# ``read_surface_census`` like sections 8 and 8f are. WHEN THIS SECTION WAS
# WRITTEN the reader's dict literal named eight keys and dropped the ninth the
# script had just started emitting, so the raw script was the only place the
# descriptor existed at all. THAT GAP IS CLOSED: the literal names ten keys
# now and ``test_the_container_descriptor_reaches_the_caller`` at the end of
# this section pins the descriptor arriving at a caller. The readings below
# stay raw because they are assertions about the SCRIPT's walk, and taking
# them through the shaper would make each one an assertion about two things.

#: EIGHT controls in six containers, in document order. INVENTED, and kept out
#: of ``tests/fixtures/`` for the reason :data:`LABEL_FORM_HTML` is: invented
#: markup filed beside real captures starts being read as evidence. No slug,
#: no urn, no address, no id shape.
CONTAINER_HTML = (
    "<!doctype html><html><body>"
    # 0 -- outside every container. The residue that makes "none" an answer a
    # reader can act on rather than a hole.
    "<button>Submit</button>"
    # container #0, a form. Rows 1 and 2 share it, which is the property a
    # reader needs in order to GROUP by the descriptor.
    "<form>"
    "<button>Submit</button>"
    "<button>Cancel</button>"
    "</form>"
    # container #1, a dialog by ROLE, holding the same accessible name as the
    # two above. The intro editor's question in miniature: three controls
    # reading "Submit", three different answers.
    '<div role="dialog"><button>Submit</button></div>'
    # containers #2 and #3, NESTED: a form inside a dialog. "open" is
    # load-bearing -- a closed dialog does not render, so innerText would be
    # empty and both controls would come back nameless for a reason that has
    # nothing to do with containment.
    "<dialog open><button>Outer</button>"
    "<form><button>Inner</button></form>"
    "</dialog>"
    # container #4, carrying a PERSON'S NAME four ways at once -- heading, id,
    # class and aria-label. The descriptor may carry none of them.
    '<section role="dialog" id="jane-doe-intro" class="jane-doe-intro-panel"'
    ' aria-label="Jane Doe">'
    "<h2>Jane Doe</h2><button>Message</button></section>"
    # container #5, a form by ROLE. The arm of the selector that no entry in
    # the counts block can see -- see the population test below.
    '<section role="form"><button>Refresh</button></section>'
    "</body></html>"
)

ROW_NO_CONTAINER = 0
ROW_FORM_SUBMIT = 1
ROW_FORM_CANCEL = 2
ROW_DIALOG_SUBMIT = 3
ROW_NESTED_OUTER = 4
ROW_NESTED_INNER = 5
ROW_NAMED_CONTAINER = 6
ROW_ROLE_FORM = 7

#: Every descriptor the fixture produces. Pinned as a SET rather than as a
#: count so a walk that returned the right number of wrong answers is visible.
CONTAINER_DESCRIPTORS = {
    "none",
    "form#0",
    "dialog#1",
    "dialog#2",
    "form#3",
    "dialog#4",
    "form#5",
}

#: The name planted in container #4, in the spellings the markup uses.
#: Committed because it is INVENTED -- a personal name has no shape, as the
#: header of ``test_no_committed_identity.py`` says at length, and this one is
#: already the literal content of the fixture above.
PLANTED_NAME_TOKENS = ("Jane", "Doe", "jane-doe")


async def _container_rows(census_over) -> list[dict[str, Any]]:
    """The RAW census of :data:`CONTAINER_HTML`. See the section header for
    why raw: the shaped reader enumerates its keys and drops this field."""

    async def work(page):
        return await page.evaluate(dom.CENSUS_JS, _census_cfg())

    raw = await census_over(CONTAINER_HTML, work)
    rows = raw["controls"]
    assert len(rows) == 8, (
        f"the fixture yielded {len(rows)} controls, not 8 -- every ROW_ index "
        "in this section is now pointing at the wrong control."
    )
    return rows


async def test_the_same_name_in_two_containers_is_two_different_answers(
    census_over,
):
    """THE WHOLE SLICE, in one assertion.

    Three controls whose accessible name is the same string sit in three
    different places, and a flat list cannot tell them apart. This is the
    ``Submit``/``Save`` question the intro-editor census could not answer and
    that two readers then guessed at from adjacency.
    """
    rows = await _container_rows(census_over)
    reading = [
        rows[index]["name"]
        for index in (ROW_NO_CONTAINER, ROW_FORM_SUBMIT, ROW_DIALOG_SUBMIT)
    ]
    assert reading == ["Submit", "Submit", "Submit"], (
        "the premise moved: these three controls no longer share one "
        "accessible name, so distinguishing them proves nothing."
    )
    assert rows[ROW_NO_CONTAINER]["container"] == "none"
    assert rows[ROW_FORM_SUBMIT]["container"] == "form#0"
    assert rows[ROW_DIALOG_SUBMIT]["container"] == "dialog#1"


async def test_two_controls_in_one_container_share_a_descriptor(census_over):
    """The other half of the same property, and the one that makes the field
    usable: a reader GROUPS by this string. If it were unique per control it
    would be an id, which is a different and much more dangerous field."""
    rows = await _container_rows(census_over)
    assert rows[ROW_FORM_SUBMIT]["container"] == "form#0"
    assert rows[ROW_FORM_CANCEL]["container"] == "form#0"


async def test_the_nearest_container_wins_when_containers_nest(census_over):
    """A form inside a dialog is the LinkedIn shape exactly -- the intro
    editor is a form drawn inside a dialog -- so which of the two the
    descriptor names decides whether the field answers anything. NEAREST, and
    the outermost walk is shown failing this in the mutation check below."""
    rows = await _container_rows(census_over)
    assert rows[ROW_NESTED_OUTER]["container"] == "dialog#2"
    assert rows[ROW_NESTED_INNER]["container"] == "form#3"


async def test_a_control_in_no_container_says_none_rather_than_nothing(
    census_over,
):
    """``none`` is a string and it is always present. A missing key and a null
    are two ways of saying "not measured", and this census exists to refuse
    exactly that conflation -- ``name_source: "none"`` was read as "carries no
    name" when it meant "cannot read one", and that cost the label routes."""
    rows = await _container_rows(census_over)
    assert all("container" in row for row in rows)
    assert rows[ROW_NO_CONTAINER]["container"] == "none"
    assert isinstance(rows[ROW_NO_CONTAINER]["container"], str)


async def test_the_container_descriptor_carries_no_text_from_the_container(
    census_over,
):
    """THE PRIVACY CERTIFICATION for a new source of page text.

    Container #4 carries a person's name in its heading, its id, its class and
    its aria-label -- four routes, each of them the obvious way to describe a
    container to a reader, and all four refused. What comes out is a tag and
    an index.
    """
    rows = await _container_rows(census_over)
    descriptor = rows[ROW_NAMED_CONTAINER]["container"]
    assert descriptor == "dialog#4"
    for token in PLANTED_NAME_TOKENS:
        assert token.lower() not in descriptor.lower()


def test_that_privacy_check_is_reading_markup_that_carries_the_name():
    """THE CONTROL for the test above, which markup with no name in it would
    also pass. The name has to be there, in all four places, or the assertion
    certifies nothing."""
    assert 'id="jane-doe-intro"' in CONTAINER_HTML
    assert 'class="jane-doe-intro-panel"' in CONTAINER_HTML
    assert 'aria-label="Jane Doe"' in CONTAINER_HTML
    assert "<h2>Jane Doe</h2>" in CONTAINER_HTML


async def test_the_role_arm_of_the_container_selector_fires(census_over):
    """``role="form"`` is a container and no entry in the counts block can see
    it. Asserted so the arm is not carried untested, and so the population
    mismatch below reads as measured rather than as a defect."""
    rows = await _container_rows(census_over)
    assert rows[ROW_ROLE_FORM]["container"] == "form#5"


async def test_the_descriptor_population_is_not_the_counts_block(census_over):
    """THE LIMIT, pinned rather than described.

    A reader who adds ``counts.forms`` to ``counts.dialogs`` and expects that
    many distinct descriptors will be wrong. The counts are two fixed
    selectors -- ``form`` and ``[role="dialog"], dialog`` -- and the
    descriptor's population is their union PLUS ``[role="form"]``, which
    neither counts. On this fixture: two form TAGS, three ``form#``
    containers.
    """

    async def work(page):
        return await page.evaluate(dom.CENSUS_JS, _census_cfg())

    raw = await census_over(CONTAINER_HTML, work)
    descriptors = {row["container"] for row in raw["controls"]}
    assert descriptors == CONTAINER_DESCRIPTORS
    assert raw["counts"]["forms"] == 2
    assert raw["counts"]["dialogs"] == 3
    assert len({d for d in descriptors if d.startswith("form#")}) == 3
    assert len({d for d in descriptors if d.startswith("dialog#")}) == 3


# ---------------------------------------------------------------------------
# 8d. What ELSE moved under the container walk, and what the walk is worth
# ---------------------------------------------------------------------------
#
# The risk this edit carries is the same one section 8b measured for the label
# routes, and it is not that the walk fails: it is that adding a field to every
# control row quietly disturbs one of the fields already there -- eight of
# them when this was measured, ten as of the ``checked`` edit -- at which point
# every census in ``_audit/`` describes an instrument that no longer exists and
# nothing in the diff says so.
#
# So it is measured, not argued. Two scripts -- the real one, and one with the
# container call site deleted -- are run over all 19 committed fixtures and
# every pre-existing field of every control is compared. ZERO move. The
# comparator is shown catching movement on the same files in the control test,
# so "zero" is a reading rather than a comparison that could not fail.

#: The container call site, exactly as ``CENSUS_JS`` spells it and INCLUDING
#: the comma before it, so the derived object literal is still valid JS.
CONTAINER_CALL = ",\n      container: containerOf(el)"

#: The nearest-ancestor lookup, and the OUTERMOST lookup that replaces it in
#: the mutation check. Both name ``containerNodes``, which is in scope there
#: and holds every container in document order -- so the first container that
#: contains an element is the outermost one containing it.
CONTAINER_NEAREST = "el.closest(containerSelector)"
CONTAINER_OUTERMOST = "(containerNodes.filter((n) => n.contains(el))[0] || null)"


def _census_without_containers() -> str:
    derived = dom.CENSUS_JS.replace(CONTAINER_CALL, "", 1)
    assert derived != dom.CENSUS_JS, (
        "CONTAINER_CALL no longer appears in CENSUS_JS, so this derivation is "
        "the real script wearing another name and every comparison below "
        "certifies nothing. Repoint the anchor at the container call site."
    )
    return derived


def _census_walking_to_the_outermost_container() -> str:
    derived = dom.CENSUS_JS.replace(CONTAINER_NEAREST, CONTAINER_OUTERMOST, 1)
    assert derived != dom.CENSUS_JS, (
        "CONTAINER_NEAREST no longer appears in CENSUS_JS, so the nearest "
        "rule cannot be broken by this derivation and the nesting test below "
        "is no longer shown failing under the wrong walk."
    )
    return derived


async def _pre_existing_field_movement(
    census_over, html: str, other_js: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Controls where a field the OTHER script also emits differs.

    Reports the differing FIELD NAMES and never their values. A diff quoting
    an accessible name would put one into a CI log, which is the thing this
    file exists to prevent, and the field names alone answer the question.
    """
    cfg = _census_cfg()

    async def work(page):
        return (
            await page.evaluate(dom.CENSUS_JS, cfg),
            await page.evaluate(other_js, cfg),
        )

    live, other = await census_over(html, work)
    after, before = live["controls"], other["controls"]
    assert len(after) == len(before)
    moved = [
        {
            "index": index,
            "tag": new["tag"],
            "fields": sorted(
                key
                for key in old
                if key not in new or new[key] != old[key]
            ),
        }
        for index, (new, old) in enumerate(zip(after, before))
        if any(key not in new or new[key] != old[key] for key in old)
    ]
    assert live["counts"] == other["counts"]
    return moved, live


async def _container_sweep(
    census_over,
) -> tuple[dict[str, list[dict[str, Any]]], int, dict[str, list[tuple]]]:
    """Run the comparison over every committed fixture.

    Returns the movers, the number of controls read -- so a shrinking sweep is
    visible -- and every CONTAINED control in the repo, file by file, as
    ``(descriptor, tag, name_source)``. Never a name: the triple says where a
    control sits and what kind of thing it is, which is the whole question,
    and a sweep that printed accessible names would put them in a CI log.
    """
    fixtures = sorted(FIXTURE_DIR.glob("*.html"))
    assert len(fixtures) >= 19, "the fixture directory shrank; this proof did too"
    derived = _census_without_containers()
    found: dict[str, list[dict[str, Any]]] = {}
    total = 0
    contained: dict[str, list[tuple]] = {}

    for path in fixtures:
        html = _fixture_text(path)
        moved, live = await _pre_existing_field_movement(
            census_over, html, derived
        )
        rows = live["controls"]
        total += len(rows)
        inside = [
            (row["container"], row["tag"], row["name_source"])
            for row in rows
            if row["container"] != "none"
        ]
        if inside:
            contained[path.name] = inside
        if moved:
            found[path.name] = moved
    return found, total, contained


#: EVERY control in the fixture directory that sits inside a container, file
#: by file, measured 2026-08-31. THREE, out of 537 -- and all three are in the
#: Easy Apply capture, which is the finding rather than a shortfall: it is the
#: only committed fixture that captured a MODAL, and a modal is the shape this
#: field exists to describe. The other 18 are page fragments with neither a
#: dialog nor a form in them, so the corpus can certify the FORMAT of the
#: descriptor across the repo and can certify its VALUES only here.
#:
#: Read the three together, because they are the intro editor's question
#: answered on a real capture: ONE dialog holding TWO SEPARATE FORMS. A flat
#: list says the modal has a Submit and two inputs; this says the Submit
#: belongs to the modal itself and the two inputs belong to two different
#: forms inside it.
FIXTURE_CONTAINMENT = {
    "apply_modal_derived.html": [
        ("form#1", "input", "label-for"),
        ("form#2", "input", "label-for"),
        ("dialog#0", "button", "aria-label"),
    ]
}


async def test_no_committed_fixture_moves_a_pre_existing_field(census_over):
    """THE INVARIANT THAT DECIDES WHETHER OLD CAPTURES ARE STILL TRUE.

    Every field a census already published -- name, name_source, tag, role,
    href, aria_expanded, disabled, has_href -- reads identically with the
    container walk and without it, on every control of every committed
    fixture. The counts block is compared too, inside the comparator. Nothing
    already written down is contradicted by this edit; a field was added.
    """
    found, total, _descriptors = await _container_sweep(census_over)
    assert found == {}
    assert total == FIXTURE_CONTROLS, (
        f"the sweep read {total} controls, not {FIXTURE_CONTROLS}. A fixture "
        "changed, so this proof was taken over a directory that no longer "
        "exists -- re-measure it rather than moving this number."
    )


async def test_that_sweep_can_detect_a_moved_field(census_over):
    """THE CONTROL, and it is run over a COMMITTED fixture rather than over
    invented markup, so it certifies the comparator on the same input the
    sweep gives a clean bill of health.

    ``jobs_tracker_empty.html`` is where section 8b measured twelve inputs
    moving under the label routes. The same comparator, the same file: the
    container derivation reports nothing and the label derivation reports all
    twelve. A comparator that reported nothing in both cases would be the way
    the test above passes while seeing nothing at all.
    """
    html = _fixture_text(FIXTURE_DIR / "jobs_tracker_empty.html")
    quiet, _live = await _pre_existing_field_movement(
        census_over, html, _census_without_containers()
    )
    assert quiet == []
    loud, _live = await _pre_existing_field_movement(
        census_over, html, _census_without_label_routes()
    )
    assert len(loud) == 12
    assert all("name_source" in row["fields"] for row in loud)


#: Every descriptor shape the walk may emit. A container's own text can only
#: get out through this string, so a value that does not match this pattern is
#: the leak -- which is why the check is a WHITELIST of two forms rather than a
#: search for names, and why it is applied to the whole fixture directory.
CONTAINER_DESCRIPTOR_SHAPE = re.compile(r"^(?:none|(?:form|dialog)#[0-9]+)$")


async def test_every_descriptor_in_every_committed_fixture_is_a_shape(
    census_over,
):
    """THE PRIVACY RULE, applied across the repo rather than to one fixture.

    A container's own text can only get out through this string, so the check
    is a WHITELIST of two forms -- ``none``, or a tag-or-role and an integer --
    rather than a search for names, which is the same argument the shaper
    makes and for the same reason.

    WHAT THIS DOES AND DOES NOT COVER, because the numbers are lopsided and a
    reader should not take more from it than is there. All 537 controls are
    checked, and 534 of them are in no container at all, so for those the
    check only confirms the string is ``none``. THREE controls, all in the
    Easy Apply capture, are the only real-capture evidence that a descriptor
    built off LinkedIn's own ids, classes and headings carries none of them --
    and that is why the invented markup in section 8c exists: it is the
    fixture where the name is planted deliberately, four ways at once.
    """
    _found, total, contained = await _container_sweep(census_over)
    descriptors = {row[0] for rows in contained.values() for row in rows}
    bad = sorted(d for d in descriptors if not CONTAINER_DESCRIPTOR_SHAPE.match(d))
    assert bad == []
    # And not vacuously. The walk is shown FIRING on real captures rather than
    # returning "none" everywhere and passing the pattern for free -- pinned as
    # a COUNT and a place, because "some fixture has a container" would go on
    # passing if the walk stopped firing on the modal and started firing on a
    # page fragment.
    assert contained == FIXTURE_CONTAINMENT
    inside = sum(len(rows) for rows in contained.values())
    assert (inside, total - inside) == (3, 534)


async def test_deleting_the_container_walk_takes_the_readings_with_it(
    census_over,
):
    """MUTATION CHECK, first half. With the call site gone the field is gone
    entirely -- so every assertion in section 8c rests on the walk and not on
    something the browser would have returned anyway."""
    derived = _census_without_containers()

    async def work(page):
        return await page.evaluate(derived, _census_cfg())

    raw = await census_over(CONTAINER_HTML, work)
    assert len(raw["controls"]) == 8
    assert all("container" not in row for row in raw["controls"])


async def test_walking_to_the_outermost_container_breaks_the_nesting(
    census_over,
):
    """MUTATION CHECK, second half, and the one that matters most.

    A walk that returned the OUTERMOST container instead of the nearest would
    pass every other test in section 8c -- the same-name test, the shared
    descriptor, the ``none``, the privacy check, the format check -- because
    only one control in the fixture is nested. Here it is shown giving the
    nested control the wrong answer: ``dialog#2``, the page furniture, where
    the real walk says ``form#3``, the editor.
    """
    derived = _census_walking_to_the_outermost_container()

    async def work(page):
        return await page.evaluate(derived, _census_cfg())

    raw = await census_over(CONTAINER_HTML, work)
    rows = raw["controls"]
    assert rows[ROW_NESTED_INNER]["container"] == "dialog#2"
    assert rows[ROW_NESTED_OUTER]["container"] == "dialog#2"
    # The value the real walk reports for the same control, quoted so the two
    # readings are side by side rather than a file apart.
    assert (await _container_rows(census_over))[ROW_NESTED_INNER][
        "container"
    ] == "form#3"


async def test_the_container_descriptor_reaches_the_caller(census_over):
    """THIS TEST REPLACED A PIN ON THE GAP, and the gap is worth keeping in
    view because of how it hid.

    The descriptor used to stop at ``CENSUS_JS``'s own return value. Two sites
    dropped it, both enumerating: ``dom.read_surface_census`` WAS shaping each
    control by building a dict literal with eight named keys, and
    ``shape.census_aggregate`` WAS merging on an explicit eight-field tuple.
    The aggregate's docstring said "the merge key is the WHOLE record", which
    was FALSE and was the sentence that made the drop invisible. Both are
    fixed, and both literals have since taken a further two fields --
    ``checked`` and ``checked_source`` -- through the same deliberate edit.

    THE CHOICE THE OLD PIN EXISTED TO FORCE, made and recorded here. Merging
    is what makes the field worth anything: ``Submit`` in one dialog and
    ``Submit`` in another would collapse to a single row of count 2 and
    destroy the fact the field was added to establish. The two ways out were
    to put the descriptor IN the merge key, or to have the merged row carry
    the SET of containers.

    THE SET WON, on a measurement rather than a preference:
    :func:`shape.census_redact_rare` fires at exactly ``count == 1``, so
    splitting a readable shape seen once per container into two rows of count
    1 turns it into two ``<redacted>`` rows. Keying on the container would
    have destroyed readable output in order to report itself.
    """
    rows, _ = shape.census_aggregate(
        [
            {"shape": "Submit", "tag": "button", "container": "form#0"},
            {"shape": "Submit", "tag": "button", "container": "dialog#1"},
            {"shape": "Submit", "tag": "button", "container": "dialog#1"},
        ]
    )
    assert len(rows) == 1, rows
    row = rows[0]
    # ONE row, because the container is not in the key -- and the count still
    # means what it always meant.
    assert row["shape"] == "Submit"
    assert row["count"] == 3
    # And the row says WHERE, counted, most-populated first.
    assert row["containers"] == {"dialog#1": 2, "form#0": 1}


async def test_a_control_with_no_container_is_counted_as_none_not_dropped(
    census_over,
):
    """``none`` is a place. A row whose controls were loose on the page must
    say so rather than carry an empty map, which would read as "not measured"
    -- the same absent-is-not-zero rule this instrument keeps everywhere."""
    rows, _ = shape.census_aggregate(
        [
            {"shape": "Save", "tag": "button", "container": "none"},
            {"shape": "Save", "tag": "button", "container": "form#0"},
        ]
    )
    assert rows[0]["containers"] == {"form#0": 1, "none": 1}


async def test_a_record_with_no_container_field_at_all_still_aggregates(
    census_over,
):
    """SHOWN FAILING by removing the ``or "none"`` default, which raises
    rather than counting::

        TypeError: unhashable type / None used as a dict key

    A record from an older script -- or any caller building one by hand --
    carries no ``container`` at all, and the aggregate may not crash on it.
    It is counted as ``none``, which is the honest answer: no container was
    reported, so none is what is known."""
    rows, _ = shape.census_aggregate([{"shape": "Edit", "tag": "button"}])
    assert rows[0]["containers"] == {"none": 1}


# ---------------------------------------------------------------------------
# 8e. The same proof at the level the captures were written from
# ---------------------------------------------------------------------------
#
# Section 8d diffs what the SCRIPT returns. Nothing in ``_audit/`` was written
# from that: a capture is what ``read_surface_census`` returned, which is the
# script's output with every name and href replaced by a shape. Those two
# fields are computed by the reader and the script-level sweep cannot see
# them, so the equality is asserted again one level up, over the same 19
# fixtures, with the reader itself pointed at the pre-edit script.


async def _reader_readings(census_over, monkeypatch, html: str, other_js: str):
    """``read_surface_census`` run twice over one page: once as it stands, once
    with the module's script swapped for ``other_js``. Returns both whole
    return values, which is what a capture in ``_audit/`` is made of."""

    async def work(page):
        after = await dom.read_surface_census(page)
        monkeypatch.setattr(dom, "CENSUS_JS", other_js)
        try:
            before = await dom.read_surface_census(page)
        finally:
            monkeypatch.undo()
        return after, before

    return await census_over(html, work)


async def test_the_shaped_reader_returns_what_it_returned_before(
    census_over, monkeypatch
):
    """THE SAME INVARIANT ONE LEVEL UP, and this is the level captures were
    written from.

    The sweep above diffs the SCRIPT's output. A census in ``_audit/`` was
    written from the READER's output -- shaped names, shaped hrefs, the counts
    block -- so that is what has to be shown unchanged. ``read_surface_census``
    is pointed at the pre-edit script and its return value is compared over
    every committed fixture, including ``shape`` and ``href_shape``, which the
    script-level sweep never sees.

    ONE FIELD IS NOW EXPECTED TO DIFFER, and the assertion is written so that
    it is the ONLY one. ``container`` reaches the reader as of 2026-08-31, so
    a bare equality would have to be either deleted or weakened; instead the
    comparison strips exactly that key and asserts equality on everything
    else, THEN asserts separately that the stripped key is present after and
    absent before. Deleting the field from both sides and calling it equal
    would prove nothing about the field, and weakening it to "mostly equal"
    would stop catching the thing this test exists for -- that no capture
    already written into ``_audit/`` is contradicted.
    """
    derived = _census_without_containers()
    fixtures = sorted(FIXTURE_DIR.glob("*.html"))
    assert len(fixtures) >= 19, "the fixture directory shrank; this proof did too"
    total = 0
    for path in fixtures:
        after, before = await _reader_readings(
            census_over, monkeypatch, _fixture_text(path), derived
        )
        # BOTH sides are stripped, because both sides HAVE the key. The
        # pre-edit script emits no container at all, and the reader's
        # ``or "none"`` default turns that absence into the string "none"
        # rather than a None -- so the difference between the two readings is
        # never PRESENCE, it is CONTENT, and stripping one side only would
        # compare a missing key against "none" and fail for the wrong reason.
        # Measured, after getting it wrong twice: before reads "none" on every
        # row of every fixture.
        assert _without_container(after) == _without_container(before), path.name
        assert all(
            row["container"] == "none" for row in before["controls"]
        ), path.name
        total += after["controls_read"]
    assert total == FIXTURE_CONTROLS


def _without_container(reading: dict) -> dict:
    """The reading with the container descriptor lifted off every control."""
    out = dict(reading)
    out["controls"] = [
        {k: v for k, v in row.items() if k != "container"}
        for row in reading["controls"]
    ]
    return out


async def test_the_container_sweep_can_tell_the_two_readings_apart(
    census_over, monkeypatch
):
    """THE CONTROL for the test above, and it is the one that stops the
    stripping from making the comparison vacuous.

    Both sides have ``container`` stripped before they are compared, so an
    edit that changed NOTHING BUT the container would pass silently. This
    asserts the two readings really do differ on the field that was stripped
    -- at least one control on this fixture reports a real container after the
    edit, where before reports "none" everywhere.
    """
    after, before = await _reader_readings(
        census_over,
        monkeypatch,
        CONTAINER_HTML,
        _census_without_containers(),
    )
    assert any(row["container"] != "none" for row in after["controls"])
    assert all(row["container"] == "none" for row in before["controls"])


async def test_that_reader_comparison_can_detect_a_changed_row(
    census_over, monkeypatch
):
    """THE CONTROL for the test above. The identical comparison, with the
    label routes deleted instead of the container walk, has to come back
    UNEQUAL on twelve rows -- otherwise the equality above is an equality
    between two things that were never going to differ."""
    after, before = await _reader_readings(
        census_over,
        monkeypatch,
        _fixture_text(FIXTURE_DIR / "jobs_tracker_empty.html"),
        _census_without_label_routes(),
    )
    assert after != before
    moved = [
        index
        for index, (new, old) in enumerate(
            zip(after["controls"], before["controls"])
        )
        if new != old
    ]
    assert len(moved) == 12


# ---------------------------------------------------------------------------
# 8f. WHETHER A CONTROL IS CHECKED
# ---------------------------------------------------------------------------
#
# THE GAP, and it was named exactly rather than noticed vaguely. The census of
# ``/mypreferences/d/dark-mode`` was taken twice on 2026-08-31 and both
# readings were identical: ``forms 0, buttons 1, links 16``, and three
# controls reading ``Always off``, ``Always on`` and ``Device settings`` --
# tag ``input``, ``name_source aria-labelledby``, all three. So the three
# DESTINATIONS were measured and WHICH ONE THE ACCOUNT IS ON was not. The
# census reported ``disabled`` and had no field for ``checked``, and the
# preview gate for that capability refuses to render without a measured
# current state -- correctly, because a gate that cannot say which way it
# moves a control is not a gate. One missing reading, one blocked capability.
#
# NATIVE BEFORE ARIA, and the ordering is the decision in this section rather
# than a detail of it. It is DELIBERATELY THE OPPOSITE of ``nameOf``, which
# tries ``aria-label`` first: for a native radio or checkbox ``el.checked`` is
# the state the browser holds and the state a click would move, while an
# ``aria-checked`` written on the same element is redundant markup that can go
# stale against it; for a control with no native state ARIA is the only truth
# there is. On well-formed markup the two never compete. Where they do
# compete -- row 8 below, a checked radio also carrying
# ``aria-checked="false"`` -- the native property is the one that describes
# what a click would do, and the ARIA-first ordering is derived and shown
# giving that row the wrong answer.
#
# THE TYPE GATE IS THE POINT. ``HTMLInputElement.checked`` is defined for
# EVERY input type and reads ``false`` on a text box, so an ungated read would
# report a control that cannot be checked at all as one that is checkable and
# off. That is measured across this repo rather than argued: the real script
# finds 29 non-null readings in the 19 committed fixtures and the ungated
# derivation finds 37, and the 8 extra are all ``input`` controls that are not
# checkable. It is also the SAME conflation this instrument was caught in
# earlier the same day, when ``name_source: "none"`` was reading as "this
# control carries no name" where it meant "this instrument cannot read one".
# So ``null`` means NOT A CHECKABLE CONTROL and ``false`` means CHECKABLE AND
# OFF, and no test below lets those two share an answer.
#
# WHAT THE CENSUS CANNOT SEE, pinned here because it is a limit of the
# SELECTOR rather than of this field and a reader costing the dark-mode
# capability needs it. ``CENSUS_CONTROL_SELECTOR`` has no ``[role="checkbox"]``
# and no ``[role="radio"]`` arm, so a ``div`` built as either is not censused
# at all and no ``checked`` reading exists for it. Measured, not assumed --
# the fixture below ends with such a div and the row count excludes it. The
# ARIA route is still reachable and is exercised twice below, because it fires
# on any element the selector DOES admit: a ``button`` or a
# ``div[role="button"]`` carrying ``aria-checked``.
#
# EVERY READING IN THIS SECTION IS TAKEN THROUGH ``read_surface_census``,
# unlike section 8c's, and the difference is the point: the two fields were
# added to the reader's dict literal and to the aggregate's merge key in the
# same edit as the script, so what these tests assert on is what a caller
# actually receives.

#: TEN censused controls, in document order, each a different route to a
#: checked state -- plus an eleventh element that is deliberately NOT censused.
#:
#: INVENTED, and deliberately not written into ``tests/fixtures/`` for the
#: reason :data:`LABEL_FORM_HTML` is not: invented markup filed beside real
#: captures is how invented markup starts being read as evidence. It carries
#: no slug, no urn, no address and no id shape -- ``test_no_committed_identity``
#: reads this file. The three radio labels echo the strings measured live on
#: the dark-mode page so the fixture's purpose is legible; nothing else here
#: was ever served by LinkedIn, and the markup around them is not a capture of
#: that page.
CHECKED_FORM_HTML = (
    "<!doctype html><html><body><form>"
    # 0, 1, 2 -- A RADIO GROUP OF THREE with exactly one checked: the dark-mode
    # shape, which is the whole reason this field exists. Each carries a
    # ``<label for>`` as well, so the group is named as well as stated and a
    # row that lost its name would not be mistaken for one that lost its state.
    '<label for="c-theme-off">Always off</label>'
    '<input id="c-theme-off" type="radio" name="c-theme">'
    '<label for="c-theme-on">Always on</label>'
    '<input id="c-theme-on" type="radio" name="c-theme" checked>'
    '<label for="c-theme-device">Device settings</label>'
    '<input id="c-theme-device" type="radio" name="c-theme">'
    # 3 -- a checkbox, ON.
    '<label for="c-digest">Weekly digest</label>'
    '<input id="c-digest" type="checkbox" checked>'
    # 4 -- a checkbox, OFF. Paired with the one above so "false" is shown
    # being a reading rather than the default of a field nobody set.
    '<label for="c-mentions">Mention alerts</label>'
    '<input id="c-mentions" type="checkbox">'
    # 5 -- THE TYPE GATE. A text input, which HAS an ``el.checked`` property
    # reading false. It must come back ``None``.
    '<label for="c-headline">Headline</label>'
    '<input id="c-headline" type="text">'
    # 6 -- THE ARIA ROUTE, on an element with no native checked state at all.
    # A ``button[role=switch]`` rather than the ``div[role=checkbox]`` the
    # shape suggests, because the census selector does not admit that div --
    # see the limit test below, which pins it.
    '<button role="switch" aria-checked="true">Weekly summary</button>'
    # 7 -- the third ARIA value. A tri-state "select all" is the canonical
    # carrier of ``mixed`` and it is the value most likely to be flattened by
    # a well-meaning ``bool()`` somewhere downstream.
    '<button role="checkbox" aria-checked="mixed">Select all</button>'
    # 8 -- THE CONFLICT, and the only row where the ordering can be observed:
    # a natively checked radio that also carries ``aria-checked="false"``.
    # Native wins, so this reads true.
    '<label for="c-conflict">Conflict row</label>'
    '<input id="c-conflict" type="radio" checked aria-checked="false">'
    # 9 -- a control with no checked state of either kind. The residue that
    # makes ``None`` an answer about the control rather than about the reader.
    "<button>Refresh</button>"
    # 10 -- AN INPUT WITH NO type ATTRIBUTE, added 2026-08-31 with
    # ``input_type``. It is the one row where reading the ATTRIBUTE and
    # reading the PROPERTY give different answers: ``getAttribute('type')``
    # returns nothing and ``el.type`` returns ``"text"``, which is the type
    # the browser actually applied and therefore the one a selector has to
    # match. Placed LAST among the censused controls so it cannot move any
    # ROW_ index above it.
    '<label for="c-untyped">Untyped box</label><input id="c-untyped">'
    # NOT CENSUSED, and it is here to be counted as absent. A div built as a
    # checkbox matches no arm of CENSUS_CONTROL_SELECTOR, so it yields no row
    # at all -- it is LAST in document order so that it cannot move any ROW_
    # index if the selector ever grows an arm that admits it.
    '<div role="checkbox" aria-checked="true">Div checkbox</div>'
    "</form></body></html>"
)

ROW_RADIO_OFF = 0
ROW_RADIO_ON = 1
ROW_RADIO_DEVICE = 2
ROW_CHECKBOX_ON = 3
ROW_CHECKBOX_OFF = 4
ROW_TEXT_INPUT = 5
ROW_ARIA_TRUE = 6
ROW_ARIA_MIXED = 7
ROW_NATIVE_BEATS_ARIA = 8
ROW_NOT_CHECKABLE = 9
#: Added 2026-08-31 with ``input_type``: an ``<input>`` carrying no ``type``
#: attribute at all.
ROW_UNTYPED_INPUT = 10

#: The three radios of the group, so the "exactly one is on" assertion reads
#: as a group rather than as three separate rows.
ROW_THEME_GROUP = (ROW_RADIO_OFF, ROW_RADIO_ON, ROW_RADIO_DEVICE)

#: Every value ``checked_source`` may take. THREE, and this is the
#: enumeration itself rather than a claim about one -- the sweep at the end of
#: this section checks the whole fixture directory against it.
CHECKED_SOURCES = {"native", "aria-checked", "none"}


async def _checked_form_rows(census_over) -> list[dict[str, Any]]:
    """The SHAPED census of :data:`CHECKED_FORM_HTML`, read the production way.

    Through ``read_surface_census`` rather than a bare ``evaluate``: these two
    fields reach a caller, so the rows asserted on below are the rows a caller
    receives.
    """

    async def work(page):
        return await dom.read_surface_census(page)

    census = await census_over(CHECKED_FORM_HTML, work)
    rows = census["controls"]
    assert len(rows) == 11, (
        f"the fixture yielded {len(rows)} controls, not 11 -- every ROW_ index "
        "in this section is now pointing at the wrong control."
    )
    return rows


async def test_exactly_one_radio_of_a_three_state_group_reads_checked(
    census_over,
):
    """THE BLOCKED CAPABILITY, in one assertion.

    Three same-shaped radios, one of them on. Before this field the census
    could say the dark-mode page carried three destinations and could not say
    which one the account was set to, and the preview gate for that capability
    refuses to render without a measured current state.
    """
    rows = await _checked_form_rows(census_over)
    group = [rows[index] for index in ROW_THEME_GROUP]
    assert [row["checked"] for row in group] == [False, True, False]
    assert [row["shape"] for row in group] == [
        "Always off",
        "Always on",
        "Device settings",
    ]
    # And the state is a reading rather than a default: the two that are off
    # say ``False``, not ``None``.
    assert all(row["checked"] is not None for row in group)


async def test_a_checkbox_reports_both_of_its_states(census_over):
    """The other native carrier. Both directions, so ``False`` is shown being
    read off a checkbox rather than being what the field says when it has
    nothing to report."""
    rows = await _checked_form_rows(census_over)
    assert rows[ROW_CHECKBOX_ON]["checked"] is True
    assert rows[ROW_CHECKBOX_OFF]["checked"] is False


async def test_a_text_input_is_not_checkable_and_says_so_rather_than_false(
    census_over,
):
    """THE TYPE GATE, and the most load-bearing assertion in this section.

    ``HTMLInputElement.checked`` exists on a text input and reads ``false``.
    Reporting that would say "this control is checkable and it is off" about a
    control that cannot be checked at all -- the same conflation that made
    ``name_source: "none"`` mean two different things until it was split. So
    ``None`` and ``False`` are asserted as DIFFERENT answers here, with ``is``
    rather than ``==``, because it is ``bool(None)`` that collapses them.
    """
    rows = await _checked_form_rows(census_over)
    text = rows[ROW_TEXT_INPUT]
    assert text["tag"] == "input"
    assert text["shape"] == "Headline", (
        "the premise moved: this row is no longer the text input, so what it "
        "reports about the type gate proves nothing."
    )
    assert text["checked"] is None
    assert text["checked"] is not False
    assert text["checked_source"] == "none"
    # The row that IS a checkable input and off, quoted beside it so the two
    # answers are visibly different rather than a file apart.
    assert rows[ROW_CHECKBOX_OFF]["checked"] is False


async def test_the_source_says_where_each_reading_came_from(census_over):
    """``checked_source`` exists for the reason ``name_source`` does: a caller
    can cost a capability off "this is a native radio" and cannot cost one off
    "something said it was off". Three values, reported distinctly, on one
    page."""
    rows = await _checked_form_rows(census_over)
    assert rows[ROW_RADIO_ON]["checked_source"] == "native"
    assert rows[ROW_ARIA_TRUE]["checked_source"] == "aria-checked"
    assert rows[ROW_NOT_CHECKABLE]["checked_source"] == "none"
    assert {row["checked_source"] for row in rows} == CHECKED_SOURCES


async def test_a_native_state_beats_an_aria_attribute_that_disagrees(
    census_over,
):
    """THE ORDERING, on the only row where it can be observed.

    A radio that is natively checked and also carries ``aria-checked="false"``
    is a page contradicting itself. The native property wins because it is the
    one that describes what a click would do; the ARIA-first ordering is
    derived below and shown reading this row ``False``.
    """
    rows = await _checked_form_rows(census_over)
    row = rows[ROW_NATIVE_BEATS_ARIA]
    assert row["checked"] is True
    assert row["checked_source"] == "native"


def test_that_conflict_row_really_does_carry_both_states():
    """THE CONTROL for the test above, which markup carrying only the native
    state would also pass. Both halves of the contradiction have to be in the
    fixture or the ordering is not being exercised at all."""
    assert 'type="radio" checked aria-checked="false"' in CHECKED_FORM_HTML


async def test_a_mixed_control_survives_as_the_string_and_is_not_coerced(
    census_over,
):
    """``mixed`` is a third state and it reaches the caller as a string.

    ``bool()`` anywhere on this path would turn it into ``True``, which is a
    tri-state control reported as fully on. Asserted on the shaped row, which
    is where such a coercion would most naturally be written.
    """
    rows = await _checked_form_rows(census_over)
    row = rows[ROW_ARIA_MIXED]
    assert row["checked"] == "mixed"
    assert isinstance(row["checked"], str)
    assert row["checked"] is not True
    assert row["checked_source"] == "aria-checked"


async def test_a_control_with_no_checked_state_reports_none(census_over):
    """The residue. A plain button is not a checkable control and the field
    says so with the same ``None`` the text input gets -- because they are the
    same answer: this is not a thing that can be checked."""
    rows = await _checked_form_rows(census_over)
    assert rows[ROW_NOT_CHECKABLE]["checked"] is None
    assert rows[ROW_NOT_CHECKABLE]["checked_source"] == "none"


async def test_a_div_built_as_a_checkbox_is_not_censused_at_all(census_over):
    """A MEASURED LIMIT OF THE SELECTOR, not of this field, and it is pinned
    because a reader costing the dark-mode capability will otherwise assume
    the census sees every checkable thing on a page.

    ``CENSUS_CONTROL_SELECTOR`` admits ``input`` and a list of roles that does
    NOT include ``checkbox`` or ``radio``. So a ``div[role="checkbox"]`` --
    the shape a framework emits when it builds its own controls -- produces no
    row, and therefore no ``checked`` reading either. The fixture ends with
    one and the census returns ten rows, not eleven. Widening the selector is
    a separate change with its own blast radius on every count already
    written down.
    """
    assert 'role="checkbox" aria-checked="true">Div checkbox' in (
        CHECKED_FORM_HTML
    ), "the fixture no longer carries the div, so this limit is untested"
    assert '[role="checkbox"]' not in dom.CENSUS_CONTROL_SELECTOR
    assert '[role="radio"]' not in dom.CENSUS_CONTROL_SELECTOR
    rows = await _checked_form_rows(census_over)
    assert len(rows) == 11
    assert "Div checkbox" not in json.dumps(rows)


# ---------------------------------------------------------------------------
# ``input_type``: the eleventh key, and what needs it
# ---------------------------------------------------------------------------
#
# WHY A CENSUS THAT COUNTS CONTROLS CARRIES A FIELD ABOUT DRIVING ONE.
# ``writes._live_control`` builds ``update_setting``'s click selector from the
# ROLE the control actually has, and an ``<input>``'s role is decided by its
# TYPE: radio and checkbox are two different roles wearing one tag. Without
# this field the selector would have to assume one of them, and a selector
# built on an assumed shape is the thing this package refuses on a write.
#
# The three dark-mode controls come back ``checked_source: "native"``, which
# proves only that they are checkbox-OR-radio, because that is the whole of
# what ``checkedOf``'s type gate distinguishes.


async def test_a_radio_and_a_checkbox_of_one_name_do_not_merge(census_over):
    """THE MERGE-KEY REQUIREMENT, shown as the thing it protects.

    Two controls named the same, both ``<input>``, both ``checked: false``,
    differing ONLY in type. Without ``input_type`` in the key every other
    field agrees and they collapse to one row of count 2 -- a page carrying
    two different kinds of control reported as carrying one kind twice, which
    is the exact failure ``tag`` and ``role`` are already in the key to
    prevent, one level finer.
    """
    rows, _hrefs = shape.census_aggregate(
        [
            _control(
                shape="Weekly digest",
                tag="input",
                role=None,
                input_type="radio",
                checked=False,
                checked_source="native",
            ),
            _control(
                shape="Weekly digest",
                tag="input",
                role=None,
                input_type="checkbox",
                checked=False,
                checked_source="native",
            ),
        ]
    )
    assert len(rows) == 2, rows
    assert {row["input_type"] for row in rows} == {"radio", "checkbox"}
    assert [row["count"] for row in rows] == [1, 1]


def test_the_published_row_is_built_from_the_key_by_name_not_by_index():
    """THE MISLABEL GUARD, and it pins a defect CLASS rather than an instance.

    The row used to be assembled by SUBSCRIPTING the merge key -- ``"role":
    key[2]`` and so on -- so inserting a field anywhere but the end renamed
    every column after it. Silently: every value is still a string or a None,
    so the row stays well-formed while ``role`` reports what ``name_source``
    measured. That is worse than the silent DROP ``container`` suffered on the
    day it was added, because the output still looks complete.

    Asserted on a record whose fields are all DIFFERENT AND RECOGNISABLE, so a
    one-place shift cannot land on an equal value and pass.
    """
    rows, _hrefs = shape.census_aggregate(
        [
            {
                "shape": "Always on",
                "tag": "input",
                "input_type": "radio",
                "role": "presentation",
                "name_source": "aria-labelledby",
                "has_href": False,
                "href_shape": None,
                "aria_expanded": "false",
                "disabled": True,
                "checked": True,
                "checked_source": "native",
            }
        ]
    )
    assert len(rows) == 1
    row = rows[0]
    assert row["shape"] == "Always on"
    assert row["tag"] == "input"
    assert row["input_type"] == "radio"
    assert row["role"] == "presentation"
    assert row["name_source"] == "aria-labelledby"
    assert row["has_href"] is False
    assert row["href_shape"] is None
    assert row["aria_expanded"] == "false"
    assert row["disabled"] is True
    assert row["checked"] is True
    assert row["checked_source"] == "native"
    # AND THE NAMES ARE THE KEY'S OWN, so a field can never be in one and not
    # the other.
    assert set(row) - {"count", "containers"} == set(shape.CENSUS_KEY_FIELDS)


async def test_input_type_is_the_type_the_browser_applied_not_the_attribute(
    census_over,
):
    """THE PROPERTY, NEVER THE ATTRIBUTE, and the untyped box is why.

    ``<input id="c-untyped">`` carries no ``type`` attribute, so
    ``getAttribute('type')`` returns nothing -- and the browser applies
    ``text``, which is what an ARIA role and a selector both follow. Reading
    the attribute would report this control as having no type at all, which is
    the same absent-is-not-zero conflation ``checked`` and ``name_source``
    have each already cost this module once.
    """
    rows = await _checked_form_rows(census_over)
    assert rows[ROW_UNTYPED_INPUT]["shape"] == "Untyped box"
    assert rows[ROW_UNTYPED_INPUT]["input_type"] == "text"


async def test_input_type_is_none_for_everything_that_is_not_an_input(
    census_over,
):
    """``None`` MEANS NOT AN INPUT, and it is a third value rather than the
    empty string.

    A ``<button>`` and an ``<input type="button">`` are different elements
    with different roles. Reporting the second's type as ``""`` -- or the
    first's -- would put them in one row, and ``""`` is a value a real input
    type can never take.
    """
    rows = await _checked_form_rows(census_over)
    assert rows[ROW_NOT_CHECKABLE]["tag"] == "button"
    assert rows[ROW_NOT_CHECKABLE]["input_type"] is None
    for index in ROW_THEME_GROUP:
        assert rows[index]["input_type"] == "radio", rows[index]
    assert rows[ROW_CHECKBOX_ON]["input_type"] == "checkbox"
    assert rows[ROW_TEXT_INPUT]["input_type"] == "text"
    # THE ARIA ROUTE'S CARRIERS ARE BUTTONS, so they are not inputs either --
    # which is the row where "checkable" and "is an input" come apart, and the
    # reason the two fields are separate rather than one.
    assert rows[ROW_ARIA_TRUE]["input_type"] is None
    assert rows[ROW_ARIA_TRUE]["checked"] is True


async def test_the_reader_passes_checked_through_untouched(census_over):
    """WHAT THE READER DOES TO THIS FIELD: nothing.

    Every other string on a control row is shaped and every boolean is
    coerced. ``checked`` is neither, and the way to show it is to read the raw
    script and the shaped reader over one page and assert the values are
    IDENTICAL row for row -- including the ``None`` that a ``bool()`` would
    turn into ``False`` and the ``"mixed"`` it would turn into ``True``.
    """

    async def work(page):
        return (
            await page.evaluate(dom.CENSUS_JS, _census_cfg()),
            await dom.read_surface_census(page),
        )

    raw, shaped = await census_over(CHECKED_FORM_HTML, work)
    before = [row["checked"] for row in raw["controls"]]
    after = [row["checked"] for row in shaped["controls"]]
    assert before == after
    # Not vacuously: the page carries all four values, so an identity that
    # held only for booleans would not pass this.
    assert before == [
        False,
        True,
        False,
        True,
        False,
        None,
        True,
        "mixed",
        True,
        None,
        # ROW_UNTYPED_INPUT: an ``<input>`` with no type attribute is a TEXT
        # box, so it is not checkable and reads ``None`` -- the type gate
        # working on the control that has no type written down.
        None,
    ]
    # ``checked_source`` is the one of the two that IS defaulted, and the
    # default only fires on a record that never carried the key -- so on a
    # live reading it passes through as well.
    assert [row["checked_source"] for row in raw["controls"]] == [
        row["checked_source"] for row in shaped["controls"]
    ]


async def test_a_reader_record_with_no_checked_field_still_reads():
    """The absent-is-a-value discipline, at the reader. A control dict from an
    older script carries neither key: ``checked`` stays ``None``, which is the
    honest answer -- nothing was measured, so nothing checkable is claimed --
    and ``checked_source`` reads the string ``"none"`` rather than ``None``."""
    shaped = await dom.read_surface_census(
        FakePage(url=FEED_URL, evaluate_result=_payload([{"tag": "button"}]))
    )
    row = shaped["controls"][0]
    assert row["checked"] is None
    assert row["checked_source"] == "none"


# ---------------------------------------------------------------------------
# 8g. The three derivations, and what each one gets wrong
# ---------------------------------------------------------------------------
#
# Every claim in 8f rests on one of three decisions -- that the field is read
# at all, that the native read is gated on the input TYPE, and that native is
# tried before ARIA. Each is derived here and shown producing a different and
# WRONG reading, so none of the assertions above is a test that could not have
# failed.

#: The two record fields, exactly as ``CENSUS_JS`` spells them and INCLUDING
#: the comma before them, so the derived object literal is still valid JS.
#: The helper stays defined and its result assigned-and-unused, which is the
#: minimal neutralisation: the derived script differs from the real one in the
#: keys on the record and in nothing else.
CHECKED_CALL = (
    ",\n      checked: state.checked,\n      checked_source: state.source"
)

#: The type gate, and the ungated read that replaces it. Same return, same
#: source string, one condition fewer -- so what the derived script changes is
#: WHICH inputs get a native reading and nothing else.
CHECKED_TYPE_GATE = (
    "      const type = String(el.type || '').toLowerCase();\n"
    "      if (type === 'radio' || type === 'checkbox') {\n"
    "        return { checked: el.checked === true, source: 'native' };\n"
    "      }\n"
)
CHECKED_UNGATED = (
    "        return { checked: el.checked === true, source: 'native' };\n"
)

#: The native branch's gate, and the ARIA-FIRST spelling of it. Standing the
#: native branch down wherever an ``aria-checked`` exists is what an ARIA-first
#: chain does, and it is one line rather than a re-ordered copy of the helper
#: -- so the derivation cannot drift away from the real script without the
#: assertion below catching it.
CHECKED_NATIVE_GATE = "if (tag === 'input') {"
CHECKED_ARIA_FIRST_GATE = (
    "if (tag === 'input' && !attrOf(el, 'aria-checked').trim()) {"
)


def _census_without_checked() -> str:
    derived = dom.CENSUS_JS.replace(CHECKED_CALL, "", 1)
    assert derived != dom.CENSUS_JS, (
        "CHECKED_CALL no longer appears in CENSUS_JS, so this derivation is "
        "the real script wearing another name and every comparison below "
        "certifies nothing. Repoint the anchor at the checked call site."
    )
    return derived


def _census_without_the_type_gate() -> str:
    derived = dom.CENSUS_JS.replace(CHECKED_TYPE_GATE, CHECKED_UNGATED, 1)
    assert derived != dom.CENSUS_JS, (
        "CHECKED_TYPE_GATE no longer appears in CENSUS_JS, so the gate cannot "
        "be removed by this derivation and the test below is no longer "
        "showing an ungated read getting a text input wrong."
    )
    return derived


def _census_reading_aria_first() -> str:
    derived = dom.CENSUS_JS.replace(
        CHECKED_NATIVE_GATE, CHECKED_ARIA_FIRST_GATE, 1
    )
    assert derived != dom.CENSUS_JS, (
        "CHECKED_NATIVE_GATE no longer appears in CENSUS_JS, so the ordering "
        "cannot be inverted by this derivation and native-before-aria is no "
        "longer shown mattering."
    )
    return derived


async def test_deleting_the_checked_call_site_takes_the_readings_with_it(
    census_over,
):
    """MUTATION CHECK, first of three. With the call site gone both keys are
    gone entirely, so every assertion in 8f rests on the field and not on
    something the browser would have returned anyway."""
    derived = _census_without_checked()

    async def work(page):
        return await page.evaluate(derived, _census_cfg())

    raw = await census_over(CHECKED_FORM_HTML, work)
    assert len(raw["controls"]) == 11
    assert all("checked" not in row for row in raw["controls"])
    assert all("checked_source" not in row for row in raw["controls"])


async def test_an_ungated_native_read_reports_a_text_input_as_unchecked(
    census_over,
):
    """MUTATION CHECK, second of three, AND THE EVIDENCE THE GATE EARNS ITS
    PLACE.

    ``el.checked`` on a text input is ``false``, so the ungated derivation
    reports the ``Headline`` field as a checkable control that is off. The
    real script reports ``None``. The two readings are quoted side by side
    because the difference between them is the whole argument for the gate,
    and it is a difference a reader costing a capability would act on.
    """
    derived = _census_without_the_type_gate()

    async def work(page):
        return await page.evaluate(derived, _census_cfg())

    raw = await census_over(CHECKED_FORM_HTML, work)
    ungated = raw["controls"][ROW_TEXT_INPUT]
    assert ungated["checked"] is False
    assert ungated["checked_source"] == "native"
    live = (await _checked_form_rows(census_over))[ROW_TEXT_INPUT]
    assert live["checked"] is None


async def test_reading_aria_first_gets_the_conflict_row_wrong(census_over):
    """MUTATION CHECK, third of three, and the one that matters most.

    An ARIA-first ordering passes every other test in 8f -- the radio group,
    the checkboxes, the type gate, ``mixed``, the sources -- because only one
    control in the fixture carries both states. Here it is shown reading that
    control ``False`` off a stale attribute where the real script reads
    ``True`` off the property a click would move.
    """
    derived = _census_reading_aria_first()

    async def work(page):
        return await page.evaluate(derived, _census_cfg())

    raw = await census_over(CHECKED_FORM_HTML, work)
    row = raw["controls"][ROW_NATIVE_BEATS_ARIA]
    assert row["checked"] is False
    assert row["checked_source"] == "aria-checked"
    live = (await _checked_form_rows(census_over))[ROW_NATIVE_BEATS_ARIA]
    assert live["checked"] is True
    assert live["checked_source"] == "native"


# ---------------------------------------------------------------------------
# 8h. The merge key, and why this field is in it where ``container`` is not
# ---------------------------------------------------------------------------
#
# ``census_aggregate`` merges control records into counted rows on an
# ENUMERATED key, so a field that is not named in it is dropped in silence --
# which is exactly what happened to ``container`` on the day that was added.
# The choice for ``checked`` went the other way from ``container`` and the
# axis is the reason: a container is a PLACE and a checked flag is a STATE.
# ``disabled`` and ``aria_expanded`` are states and were already in the key,
# so state was never the axis the key collapsed; two controls with the same
# name in different states are two different controls, and merging them
# destroys the only thing this field was added to report.
#
# The hazard that kept ``container`` out was measured for this field too and
# did not appear: keying on the container would have split a readable shape
# seen once per container into two rows of count 1, and ``census_redact_rare``
# fires at exactly ``count == 1``, so the field would have turned readable
# output into ``<redacted>`` in order to report itself. The sweep in 8i checks
# every committed fixture for exactly that and finds none.

#: THREE RADIOS THAT DIFFER ONLY IN THEIR STATE -- same tag, same role, same
#: label text, so the same shape and the same eight pre-existing key fields.
#: Without the state in the key they are one row of count 3, which is the page
#: reported as "three identical radios" when what it carries is a choice with
#: one option taken. INVENTED, same rule as the fixture above.
CHECKED_MERGE_HTML = (
    "<!doctype html><html><body><form>"
    '<label for="c-pick-a">Theme choice</label>'
    '<input id="c-pick-a" type="radio" name="c-pick" checked>'
    '<label for="c-pick-b">Theme choice</label>'
    '<input id="c-pick-b" type="radio" name="c-pick">'
    '<label for="c-pick-c">Theme choice</label>'
    '<input id="c-pick-c" type="radio" name="c-pick">'
    "</form></body></html>"
)


def _without_checked(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The same records with both new keys lifted off.

    ``census_aggregate`` reads them with ``.get``, so records that lack them
    key on ``None``/``"none"`` for every row -- which makes those two slots
    CONSTANT and the aggregation identical to the eight-field key that ran
    before this edit. That is what makes it a usable stand-in for "before".
    """
    return [
        {k: v for k, v in row.items() if k not in ("checked", "checked_source")}
        for row in rows
    ]


async def _merge_fixture_rows(census_over) -> list[dict[str, Any]]:
    async def work(page):
        return await dom.read_surface_census(page)

    census = await census_over(CHECKED_MERGE_HTML, work)
    rows = census["controls"]
    assert len(rows) == 3, f"the fixture yielded {len(rows)} controls, not 3"
    assert {row["shape"] for row in rows} == {"Theme choice"}, (
        "the premise moved: the three radios no longer share one shape, so "
        "keeping them apart proves nothing about the state field."
    )
    return rows


async def test_three_same_shaped_radios_do_not_merge_into_one_row(census_over):
    """THE TEST THAT JUSTIFIES THE KEY CHANGE.

    Three controls identical in every field the key held before -- shape, tag,
    role, ``name_source``, ``has_href``, ``href_shape``, ``aria_expanded``,
    ``disabled`` -- and different in exactly one: which of them is on. They
    come back as two rows, and the counts say one is on and two are off. That
    is the dark-mode page's answer, and without the state in the key it is a
    single row of count 3.
    """
    rows = await _merge_fixture_rows(census_over)
    merged, _hrefs = shape.census_aggregate(rows)
    assert len(merged) == 2, merged
    by_state = {row["checked"]: row for row in merged}
    assert set(by_state) == {True, False}
    assert by_state[True]["count"] == 1
    assert by_state[False]["count"] == 2
    assert {row["shape"] for row in merged} == {"Theme choice"}
    assert {row["checked_source"] for row in merged} == {"native"}


async def test_without_the_state_in_the_key_they_are_one_row_of_three(
    census_over,
):
    """THE CONTROL for the test above, and the "before" it is measured
    against. The same three records with the two fields lifted off key on a
    constant, which is what the eight-field tuple did to them, and they
    collapse into the single row this edit exists to prevent."""
    rows = await _merge_fixture_rows(census_over)
    merged, _hrefs = shape.census_aggregate(_without_checked(rows))
    assert len(merged) == 1, merged
    assert merged[0]["count"] == 3
    assert merged[0]["shape"] == "Theme choice"
    assert merged[0]["checked"] is None
    assert merged[0]["checked_source"] == "none"


async def test_the_split_does_not_cost_the_row_its_name(census_over):
    """THE HAZARD THAT KEPT ``container`` OUT OF THE KEY, checked on the
    fixture that splits.

    ``census_redact_rare`` fires at exactly ``count == 1``, so a split that
    drops a readable shape to a count of one can blank it. Here the shape that
    ends up at count 1 is still readable afterwards -- because the cap looks
    for a run of capitalised words and a sentence-case label is not one. This
    is the property the 19-fixture sweep below asserts across the repo; it is
    asserted on the splitting fixture too, because the sweep would also pass
    if nothing in the repo split at all.
    """
    rows = await _merge_fixture_rows(census_over)
    merged, _hrefs = shape.census_aggregate(rows)
    singleton = [row for row in merged if row["count"] == 1]
    assert len(singleton) == 1
    assert singleton[0]["shape"] == "Theme choice"
    assert singleton[0]["shape"] != shape.CENSUS_REDACTED


def test_the_merge_key_carries_both_fields_onto_the_row():
    """Both fields come back ON the row, which is what makes the key
    inspectable from the output rather than only from the source. Asserted on
    hand-built records so it does not depend on a browser."""
    rows, _hrefs = shape.census_aggregate(
        [
            _control(shape="Follow", checked=True, checked_source="native"),
            _control(shape="Follow", checked=False, checked_source="native"),
            _control(shape="Follow", checked=False, checked_source="native"),
        ]
    )
    assert len(rows) == 2
    assert {(row["checked"], row["count"]) for row in rows} == {
        (True, 1),
        (False, 2),
    }
    assert all(row["checked_source"] == "native" for row in rows)


def test_two_readings_of_the_same_state_from_different_sources_stay_apart():
    """``checked_source`` is in the key as well as ``checked``, and this is
    what that buys: a ``True`` read off a native radio and a ``True`` read off
    an ``aria-checked`` attribute are different-quality answers, and merging
    them would publish the weaker one under the stronger one's count."""
    rows, _hrefs = shape.census_aggregate(
        [
            _control(shape="Toggle", checked=True, checked_source="native"),
            _control(
                shape="Toggle", checked=True, checked_source="aria-checked"
            ),
        ]
    )
    assert len(rows) == 2
    assert {row["checked_source"] for row in rows} == {
        "native",
        "aria-checked",
    }


def test_a_record_with_no_checked_field_at_all_still_aggregates():
    """A record from an older script -- or any caller building one by hand --
    carries neither key. It is counted as ``None``/``"none"``, which is the
    honest answer: nothing was measured, so nothing is claimed."""
    rows, _hrefs = shape.census_aggregate([{"shape": "Edit", "tag": "button"}])
    assert rows[0]["checked"] is None
    assert rows[0]["checked_source"] == "none"
    assert rows[0]["count"] == 1


# ---------------------------------------------------------------------------
# 8i. What the field does to the whole repo, measured
# ---------------------------------------------------------------------------
#
# The risk is the one sections 8b and 8d measured for the two edits before
# this: not that the field fails to fire, but that it disturbs a reading
# already written into ``_audit/``, at which point those captures describe an
# instrument that no longer exists and nothing in the diff says so. This edit
# carries a SECOND risk the other two did not, because it touches the merge
# key -- a split can drop a row to ``count == 1``, where
# ``census_redact_rare`` blanks capitalised runs, so the field could destroy
# readable output in order to report itself. Both are measured over all 19
# committed fixtures, 537 controls, on 2026-08-31.
#
# WHAT THE SWEEP FOUND:
#
#   * ZERO pre-existing fields move. Same names, same sources, same counts.
#   * 29 of the 537 controls carry a non-null ``checked``, all of them
#     ``native``, all of them on ``input`` controls, in five files: one
#     unchecked input in each of three job-detail captures, twelve in the
#     empty job tracker and fourteen in the tracker row.
#   * TWO fixtures gain a row when the key changes, and both gain exactly
#     one. In each, a single ``<opaque>`` row of count 8 -- the tracker's
#     filter checkboxes, indistinguishable before -- splits by state: 6 off
#     and 2 on in the empty tracker, 4 and 4 in the row capture. That split
#     IS the capability, on a real committed capture rather than on invented
#     markup.
#   * NOT ONE readable shape becomes ``<redacted>`` in any fixture. That is
#     the hazard that kept ``container`` out of the key, and it does not
#     appear for this field.

#: The two readings the fixtures carry, named so the map below reads as two
#: kinds of control rather than as twenty-nine rows.
CHECKBOX_ON = ("input", True, "native")
CHECKBOX_OFF = ("input", False, "native")

#: EVERY control in the fixture directory that carries a checked state, file
#: by file and in document order, measured 2026-08-31. Pinned as the sequence
#: rather than as a tally, so the field cannot stop firing in one place and
#: start in another while a count stays flat.
FIXTURE_CHECKED = {
    "job_detail.html": [CHECKBOX_OFF],
    "job_detail_following_hydrated.html": [CHECKBOX_OFF],
    "job_detail_hydrated.html": [CHECKBOX_OFF],
    "jobs_tracker_empty.html": (
        [CHECKBOX_ON] + [CHECKBOX_OFF] * 5 + [CHECKBOX_ON] + [CHECKBOX_OFF] * 5
    ),
    "jobs_tracker_row.html": (
        [CHECKBOX_ON] * 2
        + [CHECKBOX_OFF] * 4
        + [CHECKBOX_ON] * 2
        + [CHECKBOX_OFF] * 6
    ),
}

#: Controls carrying a non-null ``checked`` across the whole directory, and
#: the denominator it is 29 OUT OF. Both pinned: a sweep whose size nobody
#: recorded can shrink, and a count with no denominator cannot be read.
FIXTURE_CHECKED_TOTAL = 29

#: What the ungated derivation reads instead, over the same 537 controls. The
#: EIGHT-control gap is the type gate's whole value, expressed as a number
#: rather than as an argument: eight ``input`` controls in this repo are not
#: checkable and would be reported as checkable-and-off without it.
FIXTURE_CHECKED_UNGATED_TOTAL = 37

#: EVERY aggregate row the new key splits, file by file. The key is
#: ``(shape, count before)`` and the value is the counts by state after.
#: Pinned rather than summarised because the split is the capability: before,
#: one row said the tracker carried eight identical filter checkboxes; after,
#: two rows say how many of them are on.
FIXTURE_KEY_SPLIT = {
    "jobs_tracker_empty.html": {(shape.CENSUS_OPAQUE, 8): {False: 6, True: 2}},
    "jobs_tracker_row.html": {(shape.CENSUS_OPAQUE, 8): {True: 4, False: 4}},
}


def _readable(rows: list[dict[str, Any]]) -> set:
    """The shapes in an aggregate that actually say something."""
    return {
        row["shape"]
        for row in rows
        if row["shape"] not in ("", shape.CENSUS_REDACTED)
    }


def _key_identity(row: dict[str, Any]) -> tuple:
    """A row's key WITHOUT the two new fields, so a row from each side of the
    edit can be matched against the other."""
    return (
        row["shape"],
        row["tag"],
        row["role"],
        row["name_source"],
        row["has_href"],
        row["href_shape"],
        row["aria_expanded"],
        row["disabled"],
    )


def _key_split(rows: list[dict[str, Any]]) -> tuple[dict, set]:
    """Aggregate one page's records twice -- with the new key and without it --
    and report what changed.

    Returns the split rows, keyed ``(shape, count before)``, and the set of
    readable shapes that the split LOST to redaction. The second value is the
    hazard check and it is empty everywhere in this repo.
    """
    after, _after_hrefs = shape.census_aggregate(rows)
    before, _before_hrefs = shape.census_aggregate(_without_checked(rows))
    grouped: dict[tuple, list[dict[str, Any]]] = {}
    for row in after:
        grouped.setdefault(_key_identity(row), []).append(row)
    split = {}
    for row in before:
        mates = grouped.get(_key_identity(row), [])
        if len(mates) == 1 and mates[0]["count"] == row["count"]:
            continue
        split[(row["shape"], row["count"])] = {
            mate["checked"]: mate["count"] for mate in mates
        }
    return split, _readable(before) - _readable(after)


async def _checked_sweep(census_over) -> dict[str, Any]:
    """Run every measurement in this section over every committed fixture.

    Returns the pre-existing field movers, the number of controls read -- so a
    shrinking sweep is visible -- the checked readings file by file, the key
    splits, and any readable shape lost to redaction. Never a name: a sweep
    that printed accessible names would put them in a CI log, which is what
    this whole file exists to prevent.
    """
    fixtures = sorted(FIXTURE_DIR.glob("*.html"))
    assert len(fixtures) >= 19, "the fixture directory shrank; this proof did too"
    derived = _census_without_checked()
    moved_files: dict[str, list[dict[str, Any]]] = {}
    readings: dict[str, list[tuple]] = {}
    splits: dict[str, dict] = {}
    lost: dict[str, set] = {}
    sources: set = set()
    total = 0

    async def shaped(page):
        return await dom.read_surface_census(page)

    for path in fixtures:
        html = _fixture_text(path)
        moved, live = await _pre_existing_field_movement(
            census_over, html, derived
        )
        if moved:
            moved_files[path.name] = moved
        total += len(live["controls"])
        rows = await census_over(html, shaped)
        found = [
            (row["tag"], row["checked"], row["checked_source"])
            for row in rows["controls"]
            if row["checked"] is not None
        ]
        sources.update(row["checked_source"] for row in rows["controls"])
        if found:
            readings[path.name] = found
        split, blanked = _key_split(rows["controls"])
        if split:
            splits[path.name] = split
        if blanked:
            lost[path.name] = blanked
    return {
        "moved": moved_files,
        "total": total,
        "readings": readings,
        "splits": splits,
        "lost": lost,
        "sources": sources,
    }


async def test_no_committed_fixture_moves_a_pre_existing_field_under_checked(
    census_over,
):
    """THE INVARIANT THAT DECIDES WHETHER OLD CAPTURES ARE STILL TRUE.

    Every field a census already published reads identically with the checked
    read and without it, on every control of every committed fixture, and the
    counts block is compared too inside the comparator. Nothing already
    written down is contradicted by this edit; two fields were added.
    """
    swept = await _checked_sweep(census_over)
    assert swept["moved"] == {}
    assert swept["total"] == FIXTURE_CONTROLS, (
        f"the sweep read {swept['total']} controls, not {FIXTURE_CONTROLS}. A "
        "fixture changed, so every number pinned in this section was measured "
        "against a directory that no longer exists -- re-measure them rather "
        "than moving this one."
    )


async def test_what_the_checked_field_reads_across_the_repo_is_pinned(
    census_over,
):
    """The receipt: what carries a state, where, and how much of the repo was
    read to find out. Pinned per file and in document order rather than
    totalled, so the field cannot stop firing on the tracker and start firing
    somewhere new while a count stays flat."""
    swept = await _checked_sweep(census_over)
    assert swept["readings"] == FIXTURE_CHECKED
    assert (
        sum(len(rows) for rows in swept["readings"].values())
        == FIXTURE_CHECKED_TOTAL
    )
    assert swept["total"] == FIXTURE_CONTROLS
    # And every source in the repo is one of the three this section
    # enumerates, which is the completeness claim made checkable rather than
    # asserted in prose.
    assert swept["sources"] <= CHECKED_SOURCES


async def test_the_key_split_is_pinned_and_costs_no_readable_shape(
    census_over,
):
    """THE SECOND HALF OF THE SWEEP, and the one the key change had to earn.

    Two fixtures gain exactly one row, and in both the row that splits is the
    tracker's block of eight indistinguishable filter checkboxes coming apart
    by state. NOT ONE readable shape is lost to ``<redacted>`` anywhere in the
    directory -- which is the hazard that kept ``container`` out of the key,
    checked for this field and absent.
    """
    swept = await _checked_sweep(census_over)
    assert swept["lost"] == {}
    assert swept["splits"] == FIXTURE_KEY_SPLIT


async def test_that_checked_sweep_can_detect_movement(census_over):
    """THE CONTROL. A sweep that could not have failed proves nothing, and
    this one makes three claims that each need a way of going red.

    It is run over a COMMITTED fixture rather than invented markup, on the
    same file the sweep gives a clean bill of health. ``jobs_tracker_empty``
    is where section 8b measured twelve inputs moving under the label routes
    and where this section measures twelve checked readings.
    """
    html = _fixture_text(FIXTURE_DIR / "jobs_tracker_empty.html")
    # 1. The comparator can see a moved field: silent for the checked
    #    derivation, twelve rows for the label derivation.
    quiet, _live = await _pre_existing_field_movement(
        census_over, html, _census_without_checked()
    )
    assert quiet == []
    loud, _live = await _pre_existing_field_movement(
        census_over, html, _census_without_label_routes()
    )
    assert len(loud) == 12

    # 2. The count of 29 is a measurement of the TYPE GATE and not of nothing.
    #    The ungated derivation reads a native state off eight more controls
    #    across the directory, every one of them an input that cannot be
    #    checked.
    async def ungated(page):
        raw = await page.evaluate(
            _census_without_the_type_gate(), _census_cfg()
        )
        return sum(1 for row in raw["controls"] if row["checked"] is not None)

    total = 0
    for path in sorted(FIXTURE_DIR.glob("*.html")):
        total += await census_over(_fixture_text(path), ungated)
    assert total == FIXTURE_CHECKED_UNGATED_TOTAL
    assert total - FIXTURE_CHECKED_TOTAL == 8

    # 3. The split detector can see a split. The merge fixture in 8h splits
    #    one row into two; a detector that returned {} everywhere would give
    #    the sweep above the same clean answer it gives now.
    async def shaped(page):
        return await dom.read_surface_census(page)

    rows = await census_over(CHECKED_MERGE_HTML, shaped)
    split, blanked = _key_split(rows["controls"])
    assert split == {("Theme choice", 3): {True: 1, False: 2}}
    assert blanked == set()


# ---------------------------------------------------------------------------
# THE SETTLE PRECONDITION, MOVED INTO THE INSTRUMENT
# ---------------------------------------------------------------------------
#
# The rule -- check the control count against what the surface is known to
# produce before interpreting anything -- was written down on 2026-08-31 after
# profile_edit_intro was read TWICE at 67 controls and twice at 256, and the
# small pair was a page that had not finished navigating.
#
# IT HAPPENED AGAIN THE SAME DAY, ON A DIFFERENT SURFACE, TO SOMEBODY WHO HAD
# JUST WRITTEN THAT PARAGRAPH: /in/me/ read twice at 67 controls with no
# redirect, where four earlier readings gave 232 and 233. The only reason it
# was caught is that somebody happened to remember 233.


#: Every SETTLED reading this server has taken, and every HALF-RENDER. Each
#: number was measured; none is a tolerance somebody chose.
#:
#: SPLIT BY VERDICT RATHER THAN CARRYING ONE, and the reason is a guard in
#: ``tests/test_no_committed_identity.py`` that fires on a table whose rows
#: pair a string PRESENT in a committed fixture with one that is ABSENT --
#: the shape a de-anonymisation table has. A single table of
#: ``(surface, count, verdict)`` has exactly that shape by accident:
#: ``"profile"`` is in the fixtures and ``"consistent"`` is not.
#:
#: The shape is REMOVED rather than declared an exception, which is this
#: repository's standing preference -- a declared exception is a hole in that
#: guard for the whole file, and it should be earned rather than spent on a
#: table that had another way to be written. Split like this each row carries
#: ONE string, so the guard has no pair to consider at all.
SETTLED_READINGS = (
    ("profile", 233),
    ("profile", 232),
    ("profile_edit_intro", 256),
    ("profile_edit_intro", 255),
    ("settings_dark_mode", 20),
    ("post_composer", 31),
    ("feed", 297),
    ("feed", 277),
)

#: THE TWO HALF-RENDERS ACTUALLY OBSERVED, both at 67 controls, on two
#: different surfaces, on the same day.
HALF_RENDERS = (
    ("profile", 67),
    ("profile_edit_intro", 67),
)


@pytest.mark.parametrize(
    "surface,read,verdict",
    [(s, n, "consistent") for s, n in SETTLED_READINGS]
    + [(s, n, "looks_half_rendered") for s, n in HALF_RENDERS],
)
def test_the_settle_report_calls_every_observed_reading_correctly(
    surface, read, verdict
):
    """EVERY READING THIS SERVER HAS ACTUALLY TAKEN, against the report.

    Both halves matter and the second is the one that makes the first worth
    anything: the settled readings must come back ``consistent``, or the check
    would be an alarm that fires on everything and gets ignored.
    """
    assert census_settle_report(surface, read)["verdict"] == verdict


async def test_the_richest_item_is_chosen_without_indexing_a_moving_list(
    monkeypatch,
):
    """THE BUG THIS RESOLVER SHIPPED WITH, and it failed on first live use.

    ``feed_item_commented`` picks the item carrying the most permalink
    anchors. The first version broke ties with ``items.index(urn)`` INSIDE the
    sort key -- which ``list.sort`` evaluates WHILE it is mutating the very
    list being indexed, so a urn already moved by the partial sort was no
    longer where ``index`` looked and the call raised ``ValueError: '<urn>' is
    not in list``.

    It failed LOUDLY on its first call, before the census had navigated
    anywhere, which is the good version of that bug. This pins both halves:
    the selection is correct, and ties keep DOCUMENT ORDER -- a census whose
    subject moved between readings could not be compared with itself.
    """
    rail = {
        "authorship_facts": {"authors_found": 1, "unanimous": True},
        "items": ["urn:a", "urn:b", "urn:c", "urn:d"],
        # Two items tie at the top; the earlier one must win.
        "anchors_per_item": {"urn:a": 2, "urn:b": 4, "urn:c": 4, "urn:d": 2},
        "counts": {},
        "item_root_source": {},
    }

    async def _rail(page, **kwargs):
        return dict(rail)

    monkeypatch.setattr(dom, "read_own_activity_items", _rail)
    monkeypatch.setattr(
        server_module, "_self_assertion_on", lambda landed: True
    )

    class _Nav:
        async def goto(self, page, url):
            return url

    monkeypatch.setattr(server_module, "BROWSER", _Nav())

    aimed, url = await server_module._resolve_own_item_permalink(
        object(), "most_anchors"
    )
    assert url is not None, aimed
    assert url.endswith("urn:b/"), url
    assert aimed["anchors_on_the_chosen_item"] == 4
    assert "MOST" in aimed["chosen_by"]

    # AND THE DEFAULT RULE IS UNTOUCHED: document order, first item.
    aimed, url = await server_module._resolve_own_item_permalink(
        object(), "first"
    )
    assert url.endswith("urn:a/"), url
    assert "first item in document order" in aimed["chosen_by"]


def test_an_unmeasured_surface_reports_unknown_rather_than_passing():
    """THE ABSENCE OF A CHECK IS NOT A CHECK PASSING, and the three verdicts
    keep that distinction.

    A surface nobody has measured twice cannot say what a settled render looks
    like. Reporting ``consistent`` there would be the loudest possible version
    of this module's standing error: an unmeasured thing wearing a measured
    answer.
    """
    # THIS LIST SHRANK ON 2026-09-01 AND THAT IS THE MECHANISM WORKING, not a
    # weakening. A surface earns a settled entry by being read more than once
    # and AGREEING WITH ITSELF, and two did:
    #
    #   messaging_compose  77 and 77, two independent readings hours apart and
    #                      across a server restart
    #   post_composer      31, 31, 31, the third carrying the instrument's own
    #                      "consistent" verdict
    #
    # WHAT DID NOT EARN ONE IS THE INTERESTING HALF, and ``premium`` is the
    # case worth reading: it HAS been read twice -- 73 and 80 -- and the two
    # readings DISAGREE. Two readings are not a baseline; two AGREEING
    # readings are. So it stays here, and a finding drawn from it has to
    # survive both numbers.
    #
    # ``article_composer``, ``feed_item`` and ``feed_item_commented`` are read
    # once each at most.
    for surface in (
        "article_composer",
        "feed_item",
        "feed_item_commented",
        "premium",
    ):
        assert surface not in CENSUS_SETTLED_CONTROLS, surface
        report = census_settle_report(surface, 5)
        assert report["verdict"] == "unknown"
        assert report["expected_controls"] is None
        assert "ABSENCE of a check" in report["why"]


def test_the_floor_separates_the_two_things_it_has_to_separate():
    """THE NUMBER, CHECKED AGAINST THE DATA IT WAS CHOSEN FROM.

    Both observed half-renders came in around a QUARTER of the settled count
    -- 67 of 233 and 67 of 255 -- while honest variation between settled
    readings is a few per cent: 232 vs 233, 255 vs 256, 277 vs 287 vs 297.
    There is an order of magnitude between them.

    This asserts the gap rather than the constant, so a future tolerance
    change has to keep both properties rather than merely stay a number.
    """
    for surface, expected in CENSUS_SETTLED_CONTROLS.items():
        # A reading a tenth under the known count is NORMAL variation.
        assert (
            census_settle_report(surface, int(expected * 0.9))["verdict"]
            == "consistent"
        ), surface
        # A reading at a quarter of it is what both observed failures were.
        assert (
            census_settle_report(surface, int(expected * 0.25))["verdict"]
            == "looks_half_rendered"
        ), surface


def test_the_report_says_repeating_it_will_not_help():
    """THE SENTENCE THAT MAKES THIS ACTIONABLE, and it is the counter-intuitive
    half.

    The instinct on a suspect reading is to take another one. Both observed
    instances were TWO AGREEING READINGS -- repetition catches variance and
    cannot catch a stable wrong state -- so a report that flagged the reading
    without saying that would send a reader to do the one thing that does not
    work.
    """
    why = census_settle_report("profile", 67)["why"]
    assert "REPEATING IT DOES NOT HELP" in why
    assert "233" in why and "67" in why
    # And it repeats the absent-is-not-zero rule, which matters more on a
    # half-rendered page than anywhere: most of it is missing.
    assert "UNKNOWN and not zero" in why


async def test_every_census_answer_carries_the_settle_block(drive):
    """ON EVERY ANSWER, not only on a bad one.

    A field that appears only when something is wrong is a field a reader
    learns to skip -- and ``unknown`` is itself worth seeing, since it means
    this instrument cannot tell.
    """
    page = _raw_page(RAW_CONTROLS)
    drive(page)
    result = await linkedin_surface_census("feed")
    assert "settle" in result, result
    assert set(result["settle"]) == {
        "verdict",
        "expected_controls",
        "controls_read",
        "why",
    }
    assert result["settle"]["controls_read"] == result["controls_read"]


def test_a_surface_earns_its_entry_by_being_measured_more_than_once():
    """THE TABLE'S OWN RULE, asserted so an entry cannot be added on one
    reading.

    Every key here must be a surface the census can actually reach. The
    converse is deliberately NOT asserted -- a surface with no entry is the
    normal state for one nobody has read twice, and that is what ``unknown``
    is for.
    """
    reachable = set(CENSUS_SURFACES) | set(CENSUS_RESOLVED_SURFACES)
    unknown = sorted(set(CENSUS_SETTLED_CONTROLS) - reachable)
    assert not unknown, (
        f"{unknown} have settled counts and are not surfaces this instrument "
        "measures, so nothing can ever be compared against them."
    )
    for surface, expected in CENSUS_SETTLED_CONTROLS.items():
        assert expected > 0, surface
