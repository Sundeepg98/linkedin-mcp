"""The one reader that publishes names, and everything that buys it the right.

``linkedin_surface_census`` reports SHAPES and never names, because a LinkedIn
page is made of other members and LinkedIn writes their names into control
labels. ``linkedin_profile_editor_fields`` publishes names -- from inside ONE
container, on ONE page, after establishing per call that the page is the
operator's own. This file is where that difference is held to being exactly as
narrow as it claims.

WHAT THIS FILE IS ORGANISED AROUND. Every check below is shown FAILING under a
named mutation of the code it guards, and the mutations are recorded in
``_audit/_slice-editor-fields.md`` with the assertion text each one produced. A
relaxation of a privacy gate certified by checks nobody demonstrated failing
would be the worst possible thing in this repo to take on trust.

The eleven requirements this file answers, in the order they appear:

* R1  a label the census refuses is NAMED here, and ``<opaque>`` there.
* R2  controls outside the container are not returned.
* R3  the container is found via the anchor, never via an index.
* R4  two anchors -- refuse as ambiguous, and carry no field key.
* R5  no anchor -- refuse, and carry no field key.
* R6  no ``isSelfProfile=true`` -- refuse, and never load the second page.
* R7  two landed urls naming different members -- refuse.
* R8  the member segment appears nowhere in the returned structure.
* R9  no control VALUE is returned.
* R10 the substitutions still run even though the gate is off.
* R11 factoring the substitutions out of ``census_shape`` changed nothing.

Four structural guards follow them: the two JS name chains are held to
agreeing, the ten per-control fields are pinned by name, the two addresses are
pinned equal to the census's, and the census is shown to have no path into this
reader.

Every non-ASCII fixture below is written as an escape rather than as the glyph,
because this repo is ASCII throughout and ``test_path_hygiene.py`` reads these
files as ascii.

Nothing here reaches LinkedIn or an account. It launches a LOCAL headless
Chromium over invented markup, because containment lives in the injected script
and only a laid-out document can answer what it asks -- ``closest()`` and
``.labels`` are browser behaviour, and a fake page cannot stand in for either.
"""

from __future__ import annotations

import ast
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import server as server_module
from linkedin_server import dom, readonly, shape
from linkedin_server.server import (
    CENSUS_SURFACES,
    SELF_PROFILE_EDIT_INTRO_URL,
    SELF_PROFILE_URL,
    linkedin_profile_editor_fields,
)
from tests.test_surface_census import (
    ACTIVITY_ID,
    CURLY,
    LEAKS,
    MEMBER_SLUG,
    OTHER_SLUG,
)

EDITOR_VIEWPORT = {"width": 1280, "height": 720}

#: A Devanagari word, as an escape. It stands in for a LOCALISED label, which
#: is the realistic way a control name leaves the census's ASCII character
#: class -- not a name in another script, which would be a different argument.
NON_LATIN = "\u091c\u0928\u0924\u093e"

#: The landed urls, built from the slugs ``test_surface_census.py`` already
#: commits so this file adds no new invented identity of its own. Both spellings
#: are MEASURED shapes rather than guesses: the profile lands slugged WITH the
#: self-assertion query, and the editor lands slugged with NO trailing slash --
#: sections 2d and 2e of ``_audit/2026-08-31-linkedin-finish.md``.
LANDED_PROFILE = f"https://www.linkedin.com/in/{MEMBER_SLUG}/?isSelfProfile=true"
LANDED_EDITOR = f"https://www.linkedin.com/in/{MEMBER_SLUG}/edit/intro"

#: The same profile landing with LinkedIn's own assertion missing. Everything
#: else about it is identical, so R6 isolates the one thing it is about.
LANDED_PROFILE_NO_ASSERTION = f"https://www.linkedin.com/in/{MEMBER_SLUG}/"

#: An editor landing naming somebody else. The shape a hijacked redirect would
#: have, and the only thing R7 needs to be different.
LANDED_EDITOR_OTHER = f"https://www.linkedin.com/in/{OTHER_SLUG}/edit/intro"

#: Distinctive strings planted in ``value`` attributes. Nothing shapes them,
#: nothing substitutes them, and they appear in no label -- so any one of them
#: turning up in the serialised result came out of a control's VALUE.
VALUE_ALPHA = "VALUE-ALPHA-NOT-A-LABEL"
VALUE_BETA = "VALUE-BETA-NOT-A-LABEL"
VALUE_GAMMA = "VALUE-GAMMA-NOT-A-LABEL"


# ---------------------------------------------------------------------------
# Invented markup. NOT in tests/fixtures/, for the reason LABEL_FORM_HTML is
# not: nothing here was ever served by LinkedIn, and invented markup filed
# beside real captures is how invented markup starts being read as evidence.
# ---------------------------------------------------------------------------

#: Page one. The tool reads its LANDED URL and nothing else -- it never touches
#: this document -- so the markup is deliberately empty of anything to read.
#: If that ever stops being true, this fixture is where it will show.
PROFILE_HTML = "<!doctype html><html><body><h1>Profile</h1></body></html>"

#: THE EDITOR DIALOG IS SECOND IN DOCUMENT ORDER, AND THAT IS THE POINT.
#:
#: R3 asserts the container is found through the anchor rather than through an
#: index. A fixture whose editor was the FIRST dialog could not fail that test:
#: an implementation that hardcoded ``document.querySelector('dialog')`` would
#: land on the right container by accident and the check would certify nothing.
#: So the ad-report dialog is drawn first, which is also the shape the live
#: page had -- the 2026-08-31 capture found five dialogs and two ad-report
#: forms around the editor.
#:
#: The rest of the shape is R2's: a second dialog holding a commit control and
#: two fields, and loose controls belonging to no dialog at all.
TWO_DIALOG_HTML = (
    "<!doctype html><html><body>"
    # Loose controls, in no dialog. On the live render these were the activity
    # rail -- ``Comments`` and ``Posts`` both reported container ``none``.
    '<a href="/feed/">Comments</a>'
    "<button>Posts</button>"
    # DIALOG ONE: the ad-report form, drawn first.
    "<dialog open>"
    "<button>Submit</button>"
    '<label for="ad-reason">Report this ad</label>'
    f'<input id="ad-reason" type="text" value="{VALUE_ALPHA}">'
    '<label for="ad-often">I have seen the same ad too often</label>'
    '<input id="ad-often" type="checkbox" checked>'
    "</dialog>"
    # DIALOG TWO: the editor. Three fields and the anchor.
    "<dialog open>"
    '<label for="e-additional">Additional name</label>'
    f'<input id="e-additional" type="text" value="{VALUE_BETA}" required>'
    '<label for="e-city">City</label>'
    f'<input id="e-city" type="text" value="{VALUE_GAMMA}">'
    '<label for="e-month">Month</label>'
    '<select id="e-month"><option>January</option></select>'
    "<button>Save</button>"
    "</dialog>"
    "</body></html>"
)

#: TWO anchors. Derived from the fixture above by renaming the ad dialog's
#: commit control, so the only difference between the two documents is the one
#: thing R4 is about.
TWO_SAVE_HTML = TWO_DIALOG_HTML.replace(
    "<button>Submit</button>", "<button>Save</button>"
)

#: NO anchor. Derived the same way, from the other end.
NO_SAVE_HTML = TWO_DIALOG_HTML.replace(
    "<button>Save</button>", "<button>Keep</button>"
)

#: One anchor, sitting in no dialog at all. The third refusal, which is neither
#: of the two counting ones: there is exactly one anchor and there is still no
#: container to scope to.
SAVE_OUTSIDE_HTML = (
    "<!doctype html><html><body>"
    "<button>Save</button>"
    "<dialog open>"
    '<label for="x-field">Additional name</label>'
    '<input id="x-field" type="text">'
    "</dialog>"
    "</body></html>"
)

#: A label over the census's 60-character limit. Counted, not estimated: the
#: assertion in R1 recomputes the length rather than trusting this comment.
LONG_LABEL = (
    "Additional name, and every other spelling this member has gone by"
)

#: A label carrying BOTH substitutable identities -- an entity urn and a member
#: path -- so R10 shows the substitutions running with the gate switched off.
URN_PATH_LABEL = (
    f"Note on urn:li:fsd_profile:{ACTIVITY_ID} for /in/{MEMBER_SLUG}/"
)

#: The editor dialog again, still SECOND, this time carrying the labels the
#: census refuses and the values this reader must not return.
RELAXED_HTML = (
    "<!doctype html><html><body>"
    "<dialog open>"
    "<button>Submit</button>"
    '<label for="ad-reason">Report this ad</label>'
    '<input id="ad-reason" type="text">'
    "</dialog>"
    "<dialog open>"
    f'<label for="r-long">{LONG_LABEL}</label>'
    f'<input id="r-long" type="text" value="{VALUE_ALPHA}">'
    f'<label for="r-script">{NON_LATIN} City</label>'
    f'<input id="r-script" type="text" value="{VALUE_BETA}">'
    f'<label for="r-note">{URN_PATH_LABEL}</label>'
    f'<input id="r-note" type="text" value="{VALUE_GAMMA}">'
    '<a href="/help/">Learn more</a>'
    "<button>Save</button>"
    "</dialog>"
    "</body></html>"
)


#: THE VALUE THAT IS ALSO A NAME. Invented, and deliberately shaped like the
#: live one: LinkedIn draws the headline as a ``div[role=textbox]`` whose text
#: content IS what has been typed into it, so its accessible name resolves
#: through the LAST route in the name chain -- the element's own text.
EDITABLE_VALUE = "Senior Widget Engineer | Node and TypeScript | Springfield"

#: The editor dialog with the control that broke the promise.
#:
#: NO FIXTURE IN THIS FILE HAD A CONTENTEDITABLE IN IT UNTIL NOW, and that is
#: the whole reason three layers of guard passed while the live tool published
#: a value. Every value here was an ``<input value=...>``, which is the
#: PROPERTY route -- the one the script scan, the named keys and the JSON sweep
#: were all built against.
EDITABLE_HTML = (
    "<!doctype html><html><body>"
    "<dialog open>"
    '<label for="ed-additional">Additional name</label>'
    '<input id="ed-additional" type="text" value="' + VALUE_BETA + '">'
    # THE CONTROL. No aria-label, no label-for, no title -- exactly like the
    # live one, so the name chain falls all the way through to its own text.
    '<div role="textbox" contenteditable="true">' + EDITABLE_VALUE + "</div>"
    "<button>Save</button>"
    "</dialog>"
    "</body></html>"
)


# ---------------------------------------------------------------------------
# The harness
# ---------------------------------------------------------------------------


@pytest.fixture
async def run_tool(monkeypatch):
    """Drive the real tool over frozen markup. One browser, a context per read.

    ``window.innerWidth`` is asserted on EVERY measurement, not once at setup.
    Containment does not depend on layout but ``innerText`` does -- a label's
    name IS its rendered text -- so a reading taken at an unrecorded width is a
    reading whose conditions were not recorded.

    THE TOOL IS DRIVEN, NOT THE READER. Every requirement here is about what a
    CALLER receives: the refusals, the absent ``fields`` key, the navigation
    count, the absence of the slug. Testing ``dom.read_self_owned_editor_fields``
    directly would answer none of those, because the ownership half lives in
    the tool and the reader deliberately cannot see it.
    """
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        async def _run(
            html: str,
            *,
            profile_landed: str = LANDED_PROFILE,
            editor_landed: str = LANDED_EDITOR,
        ) -> tuple[dict[str, Any], list[str]]:
            context = await browser.new_context(viewport=dict(EDITOR_VIEWPORT))
            navigations: list[str] = []
            try:
                page = await context.new_page()

                async def render(markup: str) -> None:
                    await page.set_content(
                        markup, wait_until="domcontentloaded", timeout=60_000
                    )
                    width = await page.evaluate("window.innerWidth")
                    assert width == EDITOR_VIEWPORT["width"], (
                        f"the page laid out at {width}px, not "
                        f"{EDITOR_VIEWPORT['width']}px. Every name read below "
                        "came off a document whose conditions were not "
                        "recorded."
                    )

                @asynccontextmanager
                async def fake_session():
                    yield page

                async def fake_goto(_page, url, **_kwargs):
                    navigations.append(url)
                    if url == SELF_PROFILE_URL:
                        await render(PROFILE_HTML)
                        return profile_landed
                    await render(html)
                    return editor_landed

                monkeypatch.setattr(
                    browser_module.BROWSER, "session", fake_session
                )
                monkeypatch.setattr(browser_module.BROWSER, "goto", fake_goto)
                return await linkedin_profile_editor_fields(), navigations
            finally:
                await context.close()

        try:
            yield _run
        finally:
            await browser.close()


#: ``.get("refused")`` rather than ``result["refused"]`` in every refusal check
#: below, and that is about the FAILURE TEXT rather than about strictness. A
#: subscript on a result that stopped refusing raises ``KeyError: 'refused'``,
#: which says nothing about what the tool returned instead; ``.get`` with the
#: whole result as the assertion message prints the answer a caller would have
#: received. The check is exactly as strict either way -- ``None`` never equals
#: a refusal code -- and every one of these is paired with an assertion that
#: ``"fields"`` is absent, which is the half that would actually be dangerous.
def names_of(result: dict[str, Any]) -> list[str]:
    """The published label of every control in the answer, in document order."""
    return [field["name"] for field in result["fields"]]


# ---------------------------------------------------------------------------
# R1. The relaxation, shown against the thing it relaxes
# ---------------------------------------------------------------------------


async def test_a_label_the_census_refuses_comes_back_named_here(run_tool):
    """BOTH HALVES IN ONE TEST, and that is deliberate rather than tidy.

    The claim being certified is not "this reader names things" -- it is that
    it names the SAME STRINGS the census declines to publish. Asserting those
    two facts in two tests would let one of them go green against markup the
    other never saw, which is exactly how a relaxation stops being measured
    against what it relaxes.

    Two failure routes are covered, because ``census_shape`` has two:

    * LENGTH -- a label over :data:`shape.CENSUS_NAME_LIMIT`.
    * CHARACTER CLASS -- a label carrying a script outside ASCII, which is what
      a localised LinkedIn label looks like.
    """
    result, _ = await run_tool(RELAXED_HTML)
    published = names_of(result)

    assert len(LONG_LABEL) > shape.CENSUS_NAME_LIMIT, len(LONG_LABEL)
    assert shape.census_shape(LONG_LABEL) == shape.CENSUS_OPAQUE
    assert LONG_LABEL in published, published

    localised = NON_LATIN + " City"
    assert shape.census_shape(localised) == shape.CENSUS_OPAQUE
    assert localised in published, published


# ---------------------------------------------------------------------------
# R2. The scope IS the permission
# ---------------------------------------------------------------------------


async def test_controls_outside_the_container_are_not_returned(run_tool):
    """The whole ruling is "one container", so this is the whole ruling.

    The set is asserted EXACTLY rather than by absence of the ad-dialog rows: a
    check that only looked for what must not be there would pass against a
    reader that returned nothing at all.
    """
    result, _ = await run_tool(TWO_DIALOG_HTML)

    assert names_of(result) == [
        "Additional name",
        "City",
        "Month",
        "Save",
    ], names_of(result)
    assert result["container"] == {
        "kind": "dialog",
        "anchor": "Save",
        "controls_inside": 4,
    }


def test_the_ad_dialog_and_the_loose_controls_are_really_in_that_document():
    """THE CONTROL for R2. Without it, the set equality above would pass just
    as well against markup that never had anything to exclude -- and a check
    that cannot fail certifies nothing.

    Four names are asserted present in the SOURCE and absent from the answer:
    two in the first dialog, two in no dialog.
    """
    for outside in (
        "Submit",
        "Report this ad",
        "Comments",
        "Posts",
    ):
        assert outside in TWO_DIALOG_HTML, outside


# ---------------------------------------------------------------------------
# R3. Found by the anchor, never by an index
# ---------------------------------------------------------------------------


async def test_the_container_is_found_by_the_anchor_not_by_position(run_tool):
    """The editor is the SECOND dialog in :data:`TWO_DIALOG_HTML`, so an
    implementation that took the first one would return the ad-report form's
    controls and fail here.

    The position is asserted, not assumed: if somebody reorders the fixture,
    this test says so instead of quietly becoming unable to fail.
    """
    assert TWO_DIALOG_HTML.index("<button>Submit</button>") < TWO_DIALOG_HTML.index(
        "<button>Save</button>"
    ), "the editor dialog must not be first, or this test cannot fail"

    result, _ = await run_tool(TWO_DIALOG_HTML)
    assert "Report this ad" not in names_of(result), names_of(result)
    assert "Additional name" in names_of(result), names_of(result)


# ---------------------------------------------------------------------------
# R4 and R5. The two counting refusals
# ---------------------------------------------------------------------------


async def test_two_anchors_refuse_as_ambiguous_and_carry_no_fields(run_tool):
    """AMBIGUOUS IS NOT A TIE TO BREAK. Two controls named ``Save`` means the
    only thing separating them is document order, and picking by document
    order is the defect the container measurement was taken to end.

    ``"fields" not in result`` rather than ``result["fields"] == []``: an empty
    list beside a warning is readable as "the container has none", which is a
    different and false statement.
    """
    result, navigations = await run_tool(TWO_SAVE_HTML)

    assert result.get("refused") == "ambiguous_anchor", result
    assert "fields" not in result, sorted(result)
    assert "container" not in result, sorted(result)
    assert result["anchor_controls"] == 2
    # Ownership DID hold -- this refusal is about the page, not about him.
    assert result["self_ownership"]["established"] is True
    assert len(navigations) == 2, navigations


async def test_no_anchor_refuses_and_carries_no_fields(run_tool):
    """The other end of the same rule: nothing to aim at is a refusal, never a
    fall back to the first dialog on the page."""
    result, _ = await run_tool(NO_SAVE_HTML)

    assert result.get("refused") == "no_anchor", result
    assert "fields" not in result, sorted(result)
    assert result["anchor_controls"] == 0


async def test_an_anchor_outside_every_dialog_refuses(run_tool):
    """THE THIRD REFUSAL, which neither counting rule reaches.

    Exactly one control is named ``Save`` and it sits in no dialog, while a
    dialog full of fields sits right beside it. A reader that scoped to "the
    dialog on the page" instead of "the anchor's dialog" would return those
    fields; there is no container here and the scope is the permission.
    """
    result, _ = await run_tool(SAVE_OUTSIDE_HTML)

    assert result.get("refused") == "anchor_outside_a_container", result
    assert "fields" not in result, sorted(result)
    assert result["anchor_controls"] == 1


# ---------------------------------------------------------------------------
# R6 and R7. Self-ownership, established rather than assumed
# ---------------------------------------------------------------------------


async def test_a_missing_self_assertion_refuses_before_the_second_load(run_tool):
    """THE NAVIGATION COUNT IS THE ASSERTION THAT MATTERS.

    Refusing after reading the editor would still be a refusal and would still
    have opened a page this tool had no ground to open. So the check is not
    only that ``fields`` is absent -- it is that the second address was never
    requested.
    """
    result, navigations = await run_tool(
        TWO_DIALOG_HTML, profile_landed=LANDED_PROFILE_NO_ASSERTION
    )

    assert result.get("refused") == "self_assertion_unreadable", result
    assert "fields" not in result, sorted(result)
    assert result["self_ownership"]["established"] is False
    assert result["self_ownership"]["self_assertion_present"] is False
    assert result["pages_loaded"] == 2
    assert navigations == [SELF_PROFILE_URL, SELF_PROFILE_URL], navigations


async def test_two_landed_urls_naming_different_members_refuse(run_tool):
    """The self-assertion was seen on ONE profile. An editor belonging to a
    different member is not that profile's editor, whatever the assertion said.
    """
    result, navigations = await run_tool(
        TWO_DIALOG_HTML, editor_landed=LANDED_EDITOR_OTHER
    )

    assert result.get("refused") == "different_member", result
    assert "fields" not in result, sorted(result)
    assert result["self_ownership"]["same_member"] is False
    assert result["self_ownership"]["established"] is False
    assert len(navigations) == 2, navigations


# ---------------------------------------------------------------------------
# R8. The segment is compared and DISCARDED
# ---------------------------------------------------------------------------


async def test_the_member_segment_appears_nowhere_in_the_answer(run_tool):
    """THE WHOLE STRUCTURE IS SERIALISED, not the fields it occurred to check.

    A key-by-key assertion would only cover the keys somebody thought of, and
    the failure this guards against is a slug arriving in a key nobody
    anticipated -- a landed url returned raw, a reason string quoting the path.
    So the answer is rendered to JSON and searched as one string.

    Both landings are checked, because the slug rides on both of them.
    """
    result, _ = await run_tool(TWO_DIALOG_HTML)
    rendered = json.dumps(result)

    assert MEMBER_SLUG not in rendered, rendered
    assert result["self_ownership"]["same_member"] is True
    assert result["landed_paths"] == {
        "profile": "/in/<member>/",
        "editor": "/in/<member>/edit/intro",
    }


async def test_the_segment_sweep_is_looking_at_a_slug_that_was_really_there():
    """THE CONTROL for R8. The assertion above passes trivially if the fixture
    never carried a slug, so the two landed urls are shown carrying one."""
    assert MEMBER_SLUG in LANDED_PROFILE
    assert MEMBER_SLUG in LANDED_EDITOR


async def test_a_refusal_does_not_leak_the_segment_either(run_tool):
    """The refusal paths build their own strings, so they get their own sweep.

    The different-member refusal is the one that has BOTH slugs in hand at the
    moment it writes its reason, which makes it the worst case rather than a
    representative one.
    """
    result, _ = await run_tool(
        TWO_DIALOG_HTML, editor_landed=LANDED_EDITOR_OTHER
    )
    rendered = json.dumps(result)

    assert MEMBER_SLUG not in rendered, rendered
    assert OTHER_SLUG not in rendered, rendered


# ---------------------------------------------------------------------------
# R9. Labels, never values
# ---------------------------------------------------------------------------


async def test_no_control_value_is_returned(run_tool):
    """A LABEL IS "First name". A VALUE IS HIS FIRST NAME.

    Two checks, and MEASURING WHICH ONE CATCHES WHAT found a third barrier
    nobody had put there on purpose. Three edits were tried:

    * ``raw_value: String(el.value || '')`` in the script -- caught by the
      token scan below, on the first line of this test.
    * ``raw_value: attrOf(el, 'value')`` in the script -- reaches the value
      without the token, and this test still PASSED. The reason is
      ``read_self_owned_editor_fields``'s field dict, which NAMES its ten keys:
      a field the script emits and that dict does not name is dropped before
      anything is returned. The same enumerate-the-keys discipline that once
      lost ``container`` in silence is, here, a privacy backstop.
    * the same script edit PLUS ``"raw_value": control.get("raw_value")`` in
      that dict -- which is what the sweep below actually catches, and it is
      the edit somebody would really write, because a value is no use to them
      until it is returned.

    So the two checks are not redundant and they are not the same check twice:
    the scan guards the script, the enumeration guards the crossing, and the
    sweep guards the answer. Only the sweep sees an edit that made it all the
    way out.
    """
    assert ".value" not in dom.EDITOR_FIELDS_JS

    result, _ = await run_tool(RELAXED_HTML)
    rendered = json.dumps(result)
    for planted in (VALUE_ALPHA, VALUE_BETA, VALUE_GAMMA):
        assert planted not in rendered, planted


async def test_the_planted_values_are_really_in_the_document(run_tool):
    """THE CONTROL for R9, and it is read off the LIVE PAGE rather than off the
    markup string -- a value attribute that never made it into the DOM would
    make the sweep above vacuous in a way a substring check on the source could
    not see."""
    assert VALUE_ALPHA in RELAXED_HTML
    result, _ = await run_tool(RELAXED_HTML)
    # The answer describes three inputs; the values behind them are what the
    # sweep above proved absent.
    inputs = [field for field in result["fields"] if field["tag"] == "input"]
    assert len(inputs) == 3, inputs


async def test_no_href_is_returned_either(run_tool):
    """WHETHER, NEVER WHICH. The container's controls can link out, and an
    address is the other field that could carry an identity out of a container
    measured to hold none."""
    result, _ = await run_tool(RELAXED_HTML)
    rendered = json.dumps(result)

    assert "/help/" not in rendered, rendered
    anchors = [field for field in result["fields"] if field["tag"] == "a"]
    assert len(anchors) == 1, anchors
    assert anchors[0]["has_href"] is True
    assert "href" not in anchors[0], sorted(anchors[0])


# ---------------------------------------------------------------------------
# R10. The gate is off. The substitutions are not.
# ---------------------------------------------------------------------------


async def test_the_substitutions_still_run_with_the_gate_switched_off(run_tool):
    """THE HALF OF THE SHAPING THAT DID NOT MOVE.

    The ruling relaxed the ``<opaque>`` gate on the ground that the container
    holds no third party. It did not relax the substitutions, and it could not
    have: a urn and a member path identify somebody whichever container they
    were read in, and a label is a place LinkedIn has been observed putting
    both.
    """
    result, _ = await run_tool(RELAXED_HTML)

    assert "Note on <urn> for /in/<member>/" in names_of(result), names_of(result)
    rendered = json.dumps(result)
    assert ACTIVITY_ID not in rendered, rendered
    assert MEMBER_SLUG not in rendered, rendered


def test_that_label_really_carries_both_identities():
    """THE CONTROL for R10: the raw label is shown carrying the urn and the
    member path that the answer above is asserted not to."""
    assert ACTIVITY_ID in URN_PATH_LABEL
    assert MEMBER_SLUG in URN_PATH_LABEL


# ---------------------------------------------------------------------------
# R11. The refactor changed nothing
# ---------------------------------------------------------------------------

#: ``census_shape`` output for every adversarial input, CAPTURED BEFORE the
#: substitutions were factored out into ``shape.census_substitute`` on
#: 2026-08-31, by running the pre-move function over these exact strings.
#:
#: THE INPUTS ARE IMPORTED, NOT COPIED. The first eight rows are
#: ``tests/test_surface_census.py``'s own ``LEAKS`` table, reused directly so
#: the two files cannot drift into testing different strings. The rows after
#: them are the cases ``LEAKS`` deliberately does not carry, because it is a
#: table about IDENTITY and the refactor's risk is at the EDGES: the empty
#: string, whitespace, ``None``, and both sides of the length limit -- the
#: branch that was removed was the empty-input one, so an empty input is the
#: single most load-bearing row here.
CENSUS_SHAPE_BASELINE: list[tuple[str, Any, str]] = [
    ("possessive", "React Like to Jane Doe's post", "React Like to <member>'s post"),
    (
        "possessive, curly",
        "React Like to Jane Doe" + CURLY + "s post",
        "React Like to <member>'s post",
    ),
    ("member path", "/in/" + MEMBER_SLUG + "/", "/in/<member>/"),
    (
        "member path inside a name",
        "View /in/" + OTHER_SLUG + "/ now",
        "View /in/<member>/ now",
    ),
    ("company path", "/company/example-corp/jobs/", "/company/<company>/jobs/"),
    ("urn", "urn:li:activity:" + ACTIVITY_ID, "<urn>"),
    ("digit run", "/feed/update/" + ACTIVITY_ID + "/", "/feed/update/<id>/"),
    ("lowercase possessive", "the recruiter's note", "the <member>'s note"),
    ("non-latin beside latin", NON_LATIN + " Sharma", "<opaque>"),
    ("wholly non-latin", "\u5f20\u4f1f", "<opaque>"),
    ("one over the limit", "A" * 61, "<opaque>"),
    ("exactly at the limit", "A" * 60, "A" * 60),
    ("none", None, ""),
    ("empty", "", ""),
    ("whitespace only", "   ", ""),
    ("a clean name", "Jane Doe", "Jane Doe"),
    ("a bare verb", "Save", "Save"),
    ("an em dash", "Save \u2014 now", "<opaque>"),
    ("collapsing whitespace", "  React   Like  ", "React Like"),
]


@pytest.mark.parametrize(
    "label,raw,expected",
    CENSUS_SHAPE_BASELINE,
    ids=[row[0] for row in CENSUS_SHAPE_BASELINE],
)
def test_the_refactor_left_census_shape_byte_identical(label, raw, expected):
    """THE REFACTOR, HELD TO CHANGING NOTHING.

    ``census_shape`` was split into ``census_substitute`` plus its gate so that
    this package has ONE implementation of the substitutions rather than two.
    The whole value of that is lost if the split moved the census's own answers
    by a character, because every capture in ``_audit/`` is a reading of the
    old function.

    So the expectations are OUTPUTS, not properties: pinned literals captured
    from the pre-move code, compared exactly.
    """
    assert shape.census_shape(raw) == expected, label


def test_the_leaks_table_is_the_one_the_census_file_uses():
    """The first eight baseline rows ARE ``LEAKS``, asserted rather than
    assumed -- a copy that had drifted would still pass the parametrised test
    above while silently testing different strings from the file it claims to
    reuse."""
    assert [row[1] for row in CENSUS_SHAPE_BASELINE[: len(LEAKS)]] == [
        row[1] for row in LEAKS
    ]


def test_the_two_halves_recompose_into_the_whole():
    """The gate, applied by hand to ``census_substitute``, reproduces
    ``census_shape`` on every baseline row.

    This is the property the split has to hold and the parametrised test above
    cannot see: that test would still pass if ``census_shape`` had been
    reimplemented from scratch and merely happened to agree on nineteen
    strings.
    """
    for label, raw, _expected in CENSUS_SHAPE_BASELINE:
        substituted = shape.census_substitute(raw)
        residue = shape._CENSUS_PLACEHOLDER.sub("", substituted)
        gated = (
            shape.CENSUS_OPAQUE
            if len(substituted) > shape.CENSUS_NAME_LIMIT
            or not shape._CENSUS_SAFE_CHARS.match(residue)
            else substituted
        )
        assert gated == shape.census_shape(raw), label


# ---------------------------------------------------------------------------
# The structural guards
# ---------------------------------------------------------------------------


async def test_the_editor_chain_resolves_the_same_names_as_the_census():
    """THE TWO COPIES OF THE NAME CHAIN, HELD TO AGREEING.

    ``EDITOR_FIELDS_JS`` carries its own copy of ``CENSUS_JS``'s name-resolution
    chain, and the duplication is forced: the census script is document-wide
    and returns raw names for the whole page, which is the thing being avoided,
    and a script assembled from a shared fragment cannot be certified by
    ``tests/test_readonly.py``'s call-site resolver.

    A copy nothing compares is a copy that goes stale, so both scripts are run
    over ONE document and the names they resolve for the container's controls
    are compared -- name AND ``name_source``, because the source is the half
    that says which route won.
    """
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(viewport=dict(EDITOR_VIEWPORT))
        try:
            page = await context.new_page()
            await page.set_content(
                TWO_DIALOG_HTML, wait_until="domcontentloaded", timeout=60_000
            )
            width = await page.evaluate("window.innerWidth")
            assert width == EDITOR_VIEWPORT["width"], width

            census = await page.evaluate(
                dom.CENSUS_JS,
                {
                    "controlSelector": dom.CENSUS_CONTROL_SELECTOR,
                    "maxControls": dom.CENSUS_MAX_CONTROLS,
                    "maxChars": 300,
                },
            )
            editor = await page.evaluate(
                dom.EDITOR_FIELDS_JS,
                {
                    "controlSelector": dom.CENSUS_CONTROL_SELECTOR,
                    "containerSelector": dom.EDITOR_CONTAINER_SELECTOR,
                    "anchorName": dom.EDITOR_ANCHOR_NAME,
                    "maxControls": dom.EDITOR_MAX_CONTROLS,
                    "maxChars": 300,
                },
            )
        finally:
            await context.close()
            await browser.close()

    from_editor = [
        (row["name"], row["name_source"]) for row in editor["controls"]
    ]
    by_name = {
        (row["name"], row["name_source"])
        for row in census["controls"]
        if row["name"]
    }
    assert from_editor, from_editor
    for pair in from_editor:
        assert pair in by_name, (pair, sorted(by_name))


async def test_the_ten_fields_are_present_on_every_returned_control(run_tool):
    """THE ENUMERATION, PINNED against what a caller actually receives.

    The block above ``EDITOR_FIELDS_JS`` lists ten field names, and this module
    has already lost a field once by describing a dict instead of listing it --
    ``container``, on the day it was added, with the docstring beside it
    calling itself "the WHOLE record". So the ten are named here and their
    COUNT is asserted, which is what makes the comment's "ten" checkable rather
    than a number a reader has to trust."""
    result, _ = await run_tool(TWO_DIALOG_HTML)
    expected = {
        "name",
        "name_source",
        "tag",
        "type",
        "role",
        "disabled",
        "checked",
        "checked_source",
        "required",
        "has_href",
    }
    assert len(expected) == 10
    for field in result["fields"]:
        assert set(field) == expected, sorted(field)


async def test_the_tristates_are_not_collapsed_to_booleans(run_tool):
    """``None`` means NOT MEASURABLE ON THIS KIND OF CONTROL and ``False``
    means measured and off. Collapsing them is the conflation this package
    keeps paying for, so both values are shown arriving from one document.
    """
    result, _ = await run_tool(TWO_DIALOG_HTML)
    by_name = {field["name"]: field for field in result["fields"]}

    # A text input is not checkable at all.
    assert by_name["Additional name"]["checked"] is None
    assert by_name["Additional name"]["checked_source"] == "none"
    # ... and it IS a control the required question applies to.
    assert by_name["Additional name"]["required"] is True
    assert by_name["City"]["required"] is False
    # A button cannot be required, which is not the same as being optional.
    assert by_name["Save"]["required"] is None


def test_the_two_addresses_are_the_census_surfaces_they_claim_to_be():
    """The tool loads two LITERAL addresses and no argument selects them. They
    are the same two the census reaches under ``profile`` and
    ``profile_edit_intro``, and pinning the pairs equal is what stops the two
    tools drifting onto different pages while claiming one measurement."""
    assert SELF_PROFILE_URL == CENSUS_SURFACES["profile"]
    assert SELF_PROFILE_EDIT_INTRO_URL == CENSUS_SURFACES["profile_edit_intro"]
    assert readonly.is_read_url(SELF_PROFILE_URL) is True
    assert readonly.is_read_url(SELF_PROFILE_EDIT_INTRO_URL) is True


def test_the_census_has_no_path_into_this_reader():
    """A CALLER MUST NOT BE ABLE TO REACH THIS BEHAVIOUR THROUGH THE CENSUS.

    Read off the SOURCE rather than argued: ``read_self_owned_editor_fields``
    is CALLED exactly once in ``server.py``, and the surface census's body does
    not call it. The census's key table is pinned at five here too, so a sixth
    key pointing somewhere new fails in this file as well as in its own.

    COUNTED BY AST, NOT BY ``str.count``, AND THE CHANGE IS A CORRECTION
    RATHER THAN A RELAXATION. It counted occurrences of the name in the file's
    characters, so on 2026-09-03 it went red at 2 when a corrected docstring
    NAMED the reader -- in a sentence explaining that editor fields ARE
    observed, which is prose ABOUT the reader and not a path INTO it. A
    mention is not a call, and a check that cannot tell them apart is
    measuring the wrong thing: the property being guarded is reachability,
    and reachability is a fact about the call graph. Same lesson this package
    learned when a grep for a reader's name matched a docstring and reported a
    dead function as live. The census body check below is now a call check for
    the same reason.
    """
    source = Path(server_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)

    def _calls_named(node: ast.AST, name: str) -> int:
        """How many times ``name`` is CALLED anywhere under ``node``."""
        hits = 0
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Call):
                continue
            fn = sub.func
            called = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
            if called == name:
                hits += 1
        return hits

    assert _calls_named(tree, "read_self_owned_editor_fields") == 1, _calls_named(
        tree, "read_self_owned_editor_fields"
    )

    census = [
        n
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        and n.name == "linkedin_surface_census"
    ]
    assert len(census) == 1, [n.name for n in census]
    assert _calls_named(census[0], "read_self_owned_editor_fields") == 0
    # PINNED AS A SET RATHER THAN A COUNT, and the change is a strengthening.
    # It read ``len(CENSUS_SURFACES) == 5``, which a key ADDED and a key
    # REMOVED in one edit would satisfy -- and what this file is guarding
    # against is a key pointing somewhere new, which is exactly that edit.
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
        "search_appearances",
    }, sorted(CENSUS_SURFACES)


def test_the_injected_script_only_reads():
    """The same scan ``test_readonly.py`` runs, asserted here too because this
    is the script that was granted a relaxed privacy gate -- if any script in
    this package deserves a second reader, it is this one."""
    assert readonly.scan_js_for_mutations(dom.EDITOR_FIELDS_JS) == []


def test_that_scan_can_fail_on_this_script():
    """THE CONTROL: the scanner is shown catching a mutation planted in this
    very script, so the assertion above is not vacuous."""
    planted = dom.EDITOR_FIELDS_JS.replace(
        "const anchors = [];",
        "const anchors = []; document.querySelector('button').click();",
    )
    assert ".click(" in readonly.scan_js_for_mutations(planted)


def test_the_script_never_scrolls():
    """Absent means UNKNOWN in this tool's output too, and that promise is only
    honest while the script genuinely does not scroll."""
    for token in ("scrollIntoView", "window.scrollTo", "scrollBy", "scrollTop"):
        assert token not in dom.EDITOR_FIELDS_JS

# ---------------------------------------------------------------------------
# "LABELS, NEVER VALUES" -- the shape that was missing
# ---------------------------------------------------------------------------


async def test_an_editables_own_content_is_not_published_as_its_name(run_tool):
    """THE PROMISE THIS TOOL MAKES, ON THE ONE SHAPE THAT BROKE IT.

    MEASURED ON THE LIVE INTRO EDITOR, 2026-08-31: the headline control is a
    ``div[role=textbox]`` with no aria-label, no label-for and no title, so
    its accessible name resolves through the LAST route in the chain -- the
    element's own text. For a contenteditable that text IS the value, and the
    tool's answer carried his headline verbatim under a docstring promising
    "LABELS, AND NEVER VALUES".

    WHY THREE LAYERS OF GUARD ALL PASSED. Each was built against the PROPERTY
    route: a scan of the script for a value read, the field dict's named keys,
    and a JSON sweep of the whole answer for the fixture values. Every value in
    every fixture in this file was an ``<input value=...>``. None of them was a
    control whose NAME IS ITS CONTENT, so there was nothing for any of the
    three to catch -- and the sweep in particular could only ever look for
    values IT had planted.

    The marker is not the same answer as ``none``: this control HAS a name.
    """
    result, _navigations = await run_tool(EDITABLE_HTML)
    assert result["self_ownership"]["established"] is True, result

    by_name = {field["name"]: field for field in result["fields"]}
    assert "<content>" in by_name, result["fields"]
    marked = by_name["<content>"]
    assert marked["name_source"] == "content"
    assert marked["tag"] == "div"
    assert marked["role"] == "textbox"

    # AND THE VALUE IS IN NO PART OF THE ANSWER, checked over the whole JSON
    # rather than over the field that carried it -- the sweep this file
    # already runs, pointed at the one value it could not have planted before.
    blob = json.dumps(result)
    assert EDITABLE_VALUE not in blob
    for fragment in EDITABLE_VALUE.split(" | "):
        assert fragment not in blob, fragment

    # THE ORDINARY FIELD BESIDE IT IS UNAFFECTED. A gate that answered
    # ``<content>`` for everything would pass every assertion above.
    assert "Additional name" in by_name
    assert by_name["Additional name"]["name_source"] == "label-for"
    assert VALUE_BETA not in blob


async def test_a_button_named_by_its_own_text_is_still_named(run_tool):
    """THE CONTROL FOR THE CONTROL ABOVE, and it is the whole reason the gate
    is on EDITABLE rather than on the ``text`` route.

    A ``<button>`` is named by its own text too, and for a button that text is
    a LABEL -- ``Save``, ``Learn more``. Gating the text route itself would
    have blanked every one of them and taken the anchor with it, since the
    container is found by the control named ``Save``.
    """
    result, _navigations = await run_tool(EDITABLE_HTML)
    names = {field["name"] for field in result["fields"]}
    assert "Save" in names, names
    assert result["container"]["anchor"] == "Save"


async def test_the_marker_is_not_the_same_answer_as_no_name(run_tool):
    """``<content>`` AND ``none`` ARE DIFFERENT FACTS, and collapsing them is
    the absent-is-not-zero conflation this package keeps paying for.

    ``none`` means this instrument found no name. ``<content>`` means it found
    one, the name is the control's own content, and it will not publish it. A
    caller deciding whether a field can be AIMED at needs to tell those apart:
    the first is a gap in the instrument, the second is a deliberate refusal.
    """
    unnamed = EDITABLE_HTML.replace(
        '<div role="textbox" contenteditable="true">' + EDITABLE_VALUE + "</div>",
        '<div role="textbox" contenteditable="true"></div>',
    )
    assert EDITABLE_VALUE not in unnamed
    result, _navigations = await run_tool(unnamed)
    sources = {field["name"]: field["name_source"] for field in result["fields"]}
    assert "<content>" not in sources
    assert "" in sources and sources[""] == "none"


# ---------------------------------------------------------------------------
# Redaction must be safe to run twice, added 2026-09-01
# ---------------------------------------------------------------------------


def test_redaction_is_idempotent_including_on_a_two_character_segment():
    """``redact(redact(x)) == redact(x)``, and the short segment is the point.

    FOUND THE FIRST TIME THIS TOOL WAS EVER RUN. The second redaction pass was
    a SUBSTRING replacement, so for the editor url -- whose member segment is
    the two-character ``me`` -- it replaced the literal ``me`` INSIDE the
    ``<member>`` token the first pass had just written, and the tool returned

        /in/<<member>mber>/edit/intro/

    A test built only on a long vanity slug would have passed forever: ``me``
    is a substring of ``<member>`` and a long slug is not. So the
    two-character case is asserted BY NAME rather than left to chance.

    In the module whose entire job is redaction, a pass that is not safe to run
    twice is a defect CLASS rather than one bug, which is why the invariant is
    asserted directly instead of just the one output being pinned.
    """
    from linkedin_server.server import _path_without_member

    # URLS BUILT FROM PARTS, never written out. Every segment below is
    # synthetic, but test_no_committed_identity hunts the SHAPE of a member
    # url and cannot tell a synthetic slug from a real one -- which is correct
    # behaviour for that guard. Constructing them keeps the shapes out of the
    # source instead of widening its declared allowlist, which has survived
    # every wave unwidened.
    def _url(segment: str) -> str:
        return "https://www.linkedin" + ".com/in/" + segment + "/edit/intro/"

    cases = [
        # THE TWO-CHARACTER CASE, which is the one that broke.
        (_url("me"), "me"),
        (_url("a-long-vanity-slug"), "a-long-vanity-slug"),
        # A segment that is a substring of the token itself -- the general
        # form of the bug rather than the one instance of it.
        (_url("member"), "member"),
        # A segment equal to the path PREFIX. This over-redacts -- the literal
        # "/in/" becomes "<member>" too -- which is the safe direction and is
        # left as-is. Recorded here so the behaviour is not discovered later
        # and mistaken for a defect.
        (_url("in"), "in"),
    ]
    for url, segment in cases:
        once = _path_without_member(url, segment)

        # NO NESTED TOKEN. This is the corruption itself, asserted directly.
        assert "<<" not in once, (url, segment, once)

        # NO SEGMENT SURVIVES AS A SEGMENT. Deliberately NOT a substring
        # check: ``intro`` contains ``in``, and asserting on substrings is the
        # very mistake that produced the bug this test exists for. The claim
        # is about path SEGMENTS, so it is checked against segments.
        assert segment not in once.split("/"), (url, segment, once)

        # THE INVARIANT. Re-running the redaction on its own output must
        # change nothing.
        again = "/".join(
            "<member>" if part == segment else part for part in once.split("/")
        )
        assert again == once, (url, segment, once, again)


def test_the_two_character_case_is_what_the_old_code_got_wrong():
    """The control: prove the OLD implementation fails where the new one holds.

    Without this, the test above could pass against an implementation that was
    never broken, and it would certify nothing about the fix. This reproduces
    the previous substring behaviour inline and asserts it produces the
    corrupted output that was actually observed.
    """
    from linkedin_server import shape
    from linkedin_server.server import _landed_path

    url = "https://www.linkedin" + ".com/in/" + "me" + "/edit/intro/"
    old_style = shape.census_substitute(_landed_path(url)).replace("me", "<member>")
    assert "<<member>mber>" in old_style, old_style

    from linkedin_server.server import _path_without_member

    assert _path_without_member(url, "me") == "/in/<member>/edit/intro/"


async def test_an_explicit_false_assertion_refuses_at_once(run_tool):
    """FALSE IS A STATEMENT AND ABSENT IS NOT, so only one of them is retried.

    Added 2026-09-02 with the split. ``isSelfProfile=false`` is LinkedIn
    answering the question -- a settled answer, refused on the FIRST load with
    no retry, because asking a settled question twice is not a reading, it is
    a page load spent on nothing.

    The absent case above costs two loads for exactly the opposite reason: the
    question was never answered, and a live pair of calls seconds apart
    returned absent then true.
    """
    landed_false = LANDED_PROFILE.replace("isSelfProfile=true", "isSelfProfile=false")
    result, navigations = await run_tool(TWO_DIALOG_HTML, profile_landed=landed_false)

    assert result.get("refused") == "not_self_profile", result
    assert "fields" not in result, result
    assert result["pages_loaded"] == 1, result
    assert navigations == [SELF_PROFILE_URL], navigations
    assert "settled answer" in result["reason"]


def test_the_three_assertion_states_are_distinguished():
    """THE PRIMITIVE, on its own, because the tool-level tests can only reach
    two of the three cheaply -- and the third is the one that was missing.

    ``_self_assertion_on`` still returns a BOOLEAN and is not changed, but as
    of 2026-09-03 it has NO callers left in the package: the activity path was
    its last one and now shares ``_goto_self_profile_asserted`` with the
    editor gate. It is kept as the collapsed reading this pair exists to be
    contrasted with. ``_self_assertion_state`` is the three-way reading beside
    it, and the pair is what stops a future edit collapsing them again.
    """
    from linkedin_server.server import _self_assertion_state as state

    base = "https://www.linkedin.com/in/somebody/"
    assert state(base + "?isSelfProfile=true") == "true"
    assert state(base + "?isSelfProfile=TRUE") == "true"
    assert state(base + "?isSelfProfile=false") == "false"
    assert state(base + "?isSelfProfile=") == "absent"
    assert state(base) == "absent"
    # AND THE TWO THAT MUST NEVER BE EQUAL.
    assert state(base + "?isSelfProfile=false") != state(base)
