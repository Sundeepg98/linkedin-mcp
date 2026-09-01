"""The one reader that publishes VALUES, and everything that buys it the right.

``linkedin_profile_editor_fields`` publishes what the editor's controls are
CALLED and refuses to say what they hold -- a control whose accessible name is
its own content comes back as ``<content>`` rather than as the content. This
file is about the tool that lifts exactly that refusal, on the same container,
behind the same gate.

WHY THE WIDER TOOL EXISTS AT ALL. ``linkedin_update_profile_field`` overwrites
a field and cannot say what it overwrote. The operator's ruling on 2026-09-01
is that the previous value is the FEATURE and not the blocker: CODE CAN MAKE
AN ACTION CORRECT; IT CANNOT MAKE AN IRREVERSIBLE OUTWARD-FACING ACTION
UNDOABLE. Only the old value can, and only if somebody has it.

WHAT THIS FILE IS ORGANISED AROUND. Every check below is shown FAILING under a
named mutation of the code it guards, recorded in
``_audit/2026-08-31-linkedin-perform.md`` with the assertion text each one
produced. This is the widest disclosure anything in this package makes, and
certifying it with checks nobody demonstrated failing would be the worst thing
in this repo to take on trust.

The requirements this file answers, in the order they appear:

* R1  a value IS returned, and the SAME document through the label reader
      yields none -- the two tools are shown differing on one document.
* R2  the self-ownership gate is not merely as strict, it is the SAME CODE.
* R3  every refusal carries no ``fields`` key at all.
* R4  a file input's value never crosses into this process.
* R5  a password input's value never crosses either.
* R6  a checkbox's and a radio's ``value`` attribute never cross -- their
      state is a different question and lives in the other tool.
* R7  a contenteditable's content arrives in the VALUE slot, with the name
      still withheld as ``<content>``.
* R8  values are NOT substituted, because a substituted value is not a string
      he could put back.
* R9  names in the same record ARE substituted, exactly as the label tool
      substitutes them.
* R10 a value longer than the ceiling is reported truncated, with its REAL
      length.
* R11 the ten per-control fields are pinned by name and by count.
* R12 ``index`` is a position in the container and pairs with the label tool.
* R13 the member segment appears nowhere in the answer.
* R14 the injected script only reads, and the scan is shown catching a
      mutation planted in this very script.
* R15 the THIRD copy of the name chain agrees with the other two.

Every value planted below is INVENTED. Nothing here is the operator's, and
nothing he has ever typed may be written into this file: values reach the
TOOL RESULT and nothing else -- never a constant, never a fixture, never the
audit. ``test_no_committed_identity`` would flag one and would be right.

Nothing here reaches LinkedIn or an account. It launches a LOCAL headless
Chromium over invented markup, because containment and value resolution are
both browser behaviour -- ``closest()``, ``.labels``, ``selectedIndex`` and
``innerText`` cannot be stood in for by a fake page.
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import server as server_module
from linkedin_server import dom, readonly, shape
from linkedin_server.server import (
    linkedin_profile_editor_fields,
    linkedin_profile_editor_values,
    SELF_PROFILE_URL,
)
from tests.test_editor_fields import (
    EDITOR_VIEWPORT,
    LANDED_EDITOR,
    LANDED_EDITOR_OTHER,
    LANDED_PROFILE,
    LANDED_PROFILE_NO_ASSERTION,
    PROFILE_HTML,
)
from tests.test_surface_census import MEMBER_SLUG

#: Invented strings, planted in places a value can live. None is a label, none
#: is substituted by anything, and none belongs to anybody -- so one of them
#: appearing in an answer says exactly which route produced it.
TEXT_VALUE = "PLANTED-TEXT-VALUE-NOT-A-LABEL"
AREA_VALUE = "PLANTED-TEXTAREA-VALUE-NOT-A-LABEL"
EDITABLE_VALUE = "PLANTED-EDITABLE-CONTENT-NOT-A-LABEL"
OPTION_TOKEN = "PLANTED-OPTION-TOKEN"
OPTION_TEXT = "Planted Option Text"

#: The values that must NEVER cross.
#:
#: THE FILE ONE IS NOT A PATH, and that is worth stating rather than hiding.
#: The first draft wrote a drive-rooted Windows path here so the placeholder
#: would be "shaped like the thing it stands in for", and
#: ``test_no_committed_identity`` failed it as a drive-root hit -- correctly:
#: a path shape in a committed file is a path shape whoever wrote it.
#:
#: IT WOULD ALSO HAVE PROVED NOTHING EXTRA. A browser does not accept a value
#: on a file input from markup, so no fixture can put a path in ``.value``;
#: what this document can carry is an ATTRIBUTE, which is what it carries.
#: The guard is proved instead by the mutation: dropping ``file`` from the
#: withheld types fails with ``assert '' is None`` -- the empty string the
#: browser holds arriving as a NATIVE read where a withholding was expected.
#: That is the route closing, measured on the route that actually exists.
FILE_PLACEHOLDER = "PLANTED-FILE-ATTRIBUTE-NOT-A-PATH"
PASSWORD_VALUE = "PLANTED-SECRET-NOT-A-PROFILE-FIELD"
CHECKBOX_TOKEN = "PLANTED-CHECKBOX-SUBMISSION-TOKEN"
RADIO_TOKEN = "PLANTED-RADIO-SUBMISSION-TOKEN"

#: A value carrying a urn. ``shape.census_substitute`` would turn this into
#: ``<urn>``, and R8 is the assertion that it does not -- a headline may
#: legally contain one and a mangled restore is worse than no restore.
#:
#: THE ID IS ONE ALREADY ON ``test_no_committed_identity``'s SYNTHETIC_IDS
#: rather than a fresh invention, and that is the cheaper of the two correct
#: moves. The other -- inventing one and registering it -- widens a privacy
#: allowlist to buy nothing, and a longer allowlist is a worse allowlist. The
#: first draft invented one and the guard failed it, correctly: it cannot
#: tell an invented urn from a real one and must not try.
URN_IN_A_VALUE = "I wrote urn:li:activity:7400000000000000003 about it"

#: A LABEL carrying a urn, which IS substituted. R9's fixture, and the pair
#: with R8 is the point: one string shape, two opposite answers, decided by
#: which slot it arrived in.
URN_IN_A_LABEL = "Notes on urn:li:activity:7400000000000000003"

#: Longer than :data:`dom.EDITOR_VALUE_MAX_CHARS`. Built from the constant
#: rather than from a literal so the fixture cannot drift away from the
#: ceiling it exists to cross.
LONG_VALUE = "L" * (dom.EDITOR_VALUE_MAX_CHARS + 400)

#: THE EDITOR IS THE SECOND DIALOG, for the reason the label reader's fixture
#: puts it second: a document whose editor is the FIRST dialog cannot fail a
#: test of "the container is found by its anchor rather than by an index".
VALUES_HTML = (
    "<!doctype html><html><body>"
    # Loose controls in no dialog, and one of them carries a value. R1's
    # containment half: a value outside the container is not returned either.
    '<input id="loose" type="text" value="PLANTED-OUTSIDE-THE-CONTAINER">'
    # DIALOG ONE: the ad-report form, drawn first and holding a commit control
    # under a different name so it is not a second anchor.
    "<dialog open>"
    "<button>Submit</button>"
    '<label for="ad-reason">Report this ad</label>'
    '<input id="ad-reason" type="text" value="PLANTED-IN-THE-WRONG-DIALOG">'
    "</dialog>"
    # DIALOG TWO: the editor.
    "<dialog open>"
    '<label for="v-text">First name</label>'
    f'<input id="v-text" type="text" value="{TEXT_VALUE}">'
    # TWO COMPETING NAME ROUTES ON ONE CONTROL, and the fixture is useless
    # without it: with every control naming itself through exactly one route,
    # REORDERING the name chain resolves every name identically and
    # test_the_three_name_chains_agree cannot fail. Measured: the mutation
    # "label routes first" PASSED against the first draft of this document.
    '<label for="v-both">Label route loses</label>'
    '<input id="v-both" type="text" aria-label="Aria route wins" '
    'value="PLANTED-TWO-ROUTES">'
    '<label for="v-area">About</label>'
    f'<textarea id="v-area">{AREA_VALUE}</textarea>'
    '<label for="v-select">Month</label>'
    f'<select id="v-select">'
    f'<option value="OTHER-TOKEN">Not the selected one</option>'
    f'<option value="{OPTION_TOKEN}" selected>{OPTION_TEXT}</option>'
    "</select>"
    # The headline shape, MEASURED on the live editor 2026-08-31: a textbox
    # with no aria-label, no label-for and no title, so its accessible name
    # resolves through the element's own text.
    f'<div role="textbox" contenteditable="true">{EDITABLE_VALUE}</div>'
    # The three whose values must never cross.
    '<label for="v-file">Attach</label>'
    f'<input id="v-file" type="file" data-planted="{FILE_PLACEHOLDER}">'
    '<label for="v-pass">Password</label>'
    f'<input id="v-pass" type="password" value="{PASSWORD_VALUE}">'
    '<label for="v-check">Show this</label>'
    f'<input id="v-check" type="checkbox" value="{CHECKBOX_TOKEN}" checked>'
    '<label for="v-radio">Pick this</label>'
    f'<input id="v-radio" type="radio" value="{RADIO_TOKEN}" checked>'
    # The urn pair: one in a value, one in a label.
    '<label for="v-urnval">Recent activity</label>'
    f'<input id="v-urnval" type="text" value="{URN_IN_A_VALUE}">'
    f'<label for="v-urnlabel">{URN_IN_A_LABEL}</label>'
    '<input id="v-urnlabel" type="text" value="PLANTED-BESIDE-A-URN-LABEL">'
    # The one that crosses the ceiling.
    '<label for="v-long">Long</label>'
    f'<input id="v-long" type="text" value="{LONG_VALUE}">'
    # An empty text input. An empty string is a REAL answer, distinct from a
    # control with no value route at all.
    '<label for="v-empty">Empty</label>'
    '<input id="v-empty" type="text" value="">'
    "<button>Save</button>"
    "</dialog>"
    "</body></html>"
)

#: TWO anchors, derived by renaming the ad dialog's commit control -- the only
#: difference between the two documents is the one thing the refusal is about.
TWO_SAVE_HTML = VALUES_HTML.replace("<button>Submit</button>", "<button>Save</button>")

#: NO anchor, derived from the other end.
NO_SAVE_HTML = VALUES_HTML.replace("<button>Save</button>", "<button>Keep</button>")

#: One anchor, in no dialog at all.
SAVE_OUTSIDE_HTML = (
    "<!doctype html><html><body>"
    "<button>Save</button>"
    "<dialog open>"
    '<label for="x-field">First name</label>'
    f'<input id="x-field" type="text" value="{TEXT_VALUE}">'
    "</dialog>"
    "</body></html>"
)


@pytest.fixture
async def run_values(monkeypatch):
    """Drive the real tool over frozen markup. One browser, a context per read.

    ``window.innerWidth`` is asserted on EVERY measurement rather than once at
    setup. Containment does not depend on layout but ``innerText`` does -- a
    contenteditable's VALUE is its rendered text -- so a reading taken at an
    unrecorded width is a reading whose conditions were not recorded.

    THE TOOL IS DRIVEN, NOT THE READER, for the reason the label file drives
    its tool: every requirement here is about what a CALLER receives, and the
    ownership half lives above the reader.
    """
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        async def _run(
            html: str,
            *,
            profile_landed: str = LANDED_PROFILE,
            editor_landed: str = LANDED_EDITOR,
            tool=linkedin_profile_editor_values,
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
                        f"{EDITOR_VIEWPORT['width']}px. Every value read below "
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
                return await tool(), navigations
            finally:
                await context.close()

        try:
            yield _run
        finally:
            await browser.close()


def by_label(result: dict[str, Any], label: str) -> dict[str, Any]:
    """The one record whose published name is ``label``, or a loud failure."""
    found = [field for field in result["fields"] if field["name"] == label]
    assert len(found) == 1, (label, [f["name"] for f in result["fields"]])
    return found[0]


# ---------------------------------------------------------------------------
# R1. A value IS returned -- and the label tool, on the same document, has none
# ---------------------------------------------------------------------------


async def test_a_value_is_returned(run_values):
    """THE CAPABILITY, stated as the thing a caller receives.

    Four routes, because "a value" is not one mechanism: a native input, a
    textarea, a select's chosen option and a contenteditable's content are
    four different reads and a test covering one would certify a quarter of
    this tool.
    """
    result, navigations = await run_values(VALUES_HTML)
    assert "refused" not in result, result
    assert navigations == [SELF_PROFILE_URL, server_module.SELF_PROFILE_EDIT_INTRO_URL]

    assert by_label(result, "First name")["value"] == TEXT_VALUE
    assert by_label(result, "About")["value"] == AREA_VALUE
    assert by_label(result, "Month")["value"] == OPTION_TEXT
    assert by_label(result, "<content>")["value"] == EDITABLE_VALUE


async def test_the_label_tool_returns_none_of_those_values(run_values):
    """THE CONTROL FOR R1, and it is the pair that makes this tool a decision
    rather than a leak.

    The SAME document is read by BOTH tools and the label tool's answer is
    swept for every planted value. If it carried them, this tool would not be
    a widening -- it would be a second way to reach something already
    published, and the ruling behind it would be about nothing.
    """
    values, _ = await run_values(VALUES_HTML)
    labels, _ = await run_values(VALUES_HTML, tool=linkedin_profile_editor_fields)

    rendered = json.dumps(labels)
    for planted in (TEXT_VALUE, AREA_VALUE, EDITABLE_VALUE, OPTION_TEXT):
        assert planted not in rendered, planted

    # ... and the same four are all present in this tool's answer, so the
    # sweep above is measuring a difference rather than an empty result.
    mine = json.dumps(values)
    for planted in (TEXT_VALUE, AREA_VALUE, EDITABLE_VALUE, OPTION_TEXT):
        assert planted in mine, planted


# ---------------------------------------------------------------------------
# R2. The gate is not "as strict as". It is THE SAME CODE.
# ---------------------------------------------------------------------------


#: A newline, spelled this way ON PURPOSE. The markers below are built from
#: it rather than written as escapes, because a newline escape written
#: immediately before the tool decorator leaves an at-sign with a letter on
#: its left and a dotted word on its right, which is exactly what
#: ``test_no_committed_identity``'s EMAIL_SHAPE looks for -- a valid-looking
#: address that is not one.
#:
#: THE RIGHT RESPONSE IS NOT TO DECLARE A PLANT. Declaring one would make
#: this the file where address-shaped strings are allowed, in exchange for a
#: string that is not an address. The guard is right to be crude; the source
#: is what changes.
#:
#: AND THIS COMMENT IS WORDED AROUND THE SHAPE for the same reason, because
#: the first draft of it QUOTED the sequence it was explaining and failed the
#: guard a second time -- the same way the value script's comment about the
#: mutation-token list tripped that list.
NEWLINE = chr(10)


def _tool_body(source: str, name: str) -> str:
    """The source of one tool, from its ``def`` to the next top-level ``def``."""
    start = source.index("async def %s(" % name)
    rest = source[start + 1 :]
    ends = [
        rest.index(marker)
        for marker in (
            NEWLINE + "def ",
            NEWLINE + "async def ",
            NEWLINE + "@mcp.tool()",
        )
        if marker in rest
    ]
    return rest[: min(ends)]


def test_neither_editor_tool_reimplements_the_ownership_gate():
    """THE STRUCTURAL FORM OF "the same bar", read off the source.

    Both tools could have kept their own copy of the ownership dance and both
    copies could have been correct on the day they were written. That is
    exactly the arrangement in which the WIDER tool later ends up with the
    WEAKER check -- somebody strengthens one and does not know there are two.

    So it is one function, and this asserts that neither tool contains the
    primitives it is built from. ``_self_assertion_on`` and
    ``_member_segment_of`` are used elsewhere in ``server.py`` by other tools,
    which is why the check is scoped to these two BODIES rather than to the
    module.
    """
    source = Path(server_module.__file__).read_text(encoding="utf-8")
    for name in ("linkedin_profile_editor_fields", "linkedin_profile_editor_values"):
        body = _tool_body(source, name)
        assert body.count("_establish_self_owned_editor(") == 1, name
        for primitive in (
            "_self_assertion_on",
            "_member_segment_of",
            "_ownership_block(",
            "SELF_PROFILE_URL",
        ):
            assert primitive not in body, (name, primitive)


async def test_the_two_tools_refuse_the_same_way_on_the_same_page(run_values):
    """THE BEHAVIOURAL HALF, because the structural check above would pass on
    two tools that called one helper and then ignored what it said.

    Both are driven over the SAME two failures a hostile landing produces, and
    their refusal codes and page counts are compared to each other rather than
    to a literal -- a literal would have to be maintained in two places, which
    is the disease.
    """
    for landings in (
        {"profile_landed": LANDED_PROFILE_NO_ASSERTION},
        {"editor_landed": LANDED_EDITOR_OTHER},
    ):
        values, values_nav = await run_values(VALUES_HTML, **landings)
        labels, labels_nav = await run_values(
            VALUES_HTML, tool=linkedin_profile_editor_fields, **landings
        )
        assert values.get("refused") == labels.get("refused"), (values, labels)
        assert values.get("refused") is not None, values
        assert values["pages_loaded"] == labels["pages_loaded"]
        assert values_nav == labels_nav
        assert "fields" not in values


# ---------------------------------------------------------------------------
# R3. A refusal carries no field data at all
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "html, expected",
    [
        (TWO_SAVE_HTML, "ambiguous_anchor"),
        (NO_SAVE_HTML, "no_anchor"),
        (SAVE_OUTSIDE_HTML, "anchor_outside_a_container"),
    ],
)
async def test_the_anchor_refusals_carry_no_fields(run_values, html, expected):
    """NOT AN EMPTY LIST: no ``fields`` key.

    A caller must not be able to read "this reader would not aim" as "the
    editor holds nothing", and on THIS tool that misreading has teeth -- it
    would say a field he is about to overwrite had no previous value.
    """
    result, _ = await run_values(html)
    assert result.get("refused") == expected, result
    assert "fields" not in result, result
    assert result["self_ownership"]["established"] is True


async def test_the_ownership_refusal_carries_no_fields(run_values):
    """The other refusal class, and the one that costs a page load fewer."""
    result, navigations = await run_values(
        VALUES_HTML, profile_landed=LANDED_PROFILE_NO_ASSERTION
    )
    assert result.get("refused") == "no_self_assertion", result
    assert "fields" not in result, result
    assert result["pages_loaded"] == 1
    assert navigations == [SELF_PROFILE_URL]


# ---------------------------------------------------------------------------
# R4-R6. The three values that never cross into this process
# ---------------------------------------------------------------------------


async def test_a_file_inputs_value_never_crosses(run_values):
    """A FILE INPUT'S VALUE IS A PATH ON HIS DISK -- a directory layout and
    often a real filename, which is not a profile field and which no restore
    needs. It is refused by TYPE, in the page, so the string never exists
    here at all.

    WHAT THE FIXTURE CAN AND CANNOT SHOW, said plainly: a browser will not
    accept a value on a file input from markup, so this document cannot plant
    a path in the value property and no test can watch a real one be
    withheld. What is asserted is that the control is refused BY TYPE rather
    than read -- and the mutation dropping the file branch fails with
    ``assert '' is None``, which is the withholding being replaced by a native
    read. On a live page that native read is his path."""
    result, _ = await run_values(VALUES_HTML)
    record = by_label(result, "Attach")
    assert record["value"] is None
    assert record["value_source"] == "withheld_by_type"
    assert record["value_chars"] is None
    assert "PLANTED" not in json.dumps(record), record


async def test_a_password_inputs_value_never_crosses(run_values):
    """No editor field is a password, WHICH IS THE REASON IT IS REFUSED
    STRUCTURALLY rather than by nobody having met one. A surface that grows a
    password field must not start publishing it, and "we never saw one" is
    not a guard."""
    result, _ = await run_values(VALUES_HTML)
    record = by_label(result, "Password")
    assert record["value"] is None
    assert record["value_source"] == "withheld_by_type"
    rendered = json.dumps(result)
    assert PASSWORD_VALUE not in rendered


async def test_a_checkbox_value_is_not_its_state(run_values):
    """THE CONFUSION THIS CLOSES. A checkbox's ``value`` attribute is the
    token it submits when checked -- it is not "on" or "off", and it does not
    change when the box does. Publishing it in the value slot would answer a
    different question in the place a caller reads the answer to this one,
    which is how somebody restores the wrong thing.

    The STATE is ``checked``, and it is the label tool's field. Asserted here
    on the same document so the two answers are visibly different rather than
    merely described as different."""
    result, _ = await run_values(VALUES_HTML)
    for label, token in (("Show this", CHECKBOX_TOKEN), ("Pick this", RADIO_TOKEN)):
        record = by_label(result, label)
        assert record["value"] is None, record
        assert record["value_source"] == "state_not_value", record
        assert token not in json.dumps(result)

    labels, _ = await run_values(VALUES_HTML, tool=linkedin_profile_editor_fields)
    state = [f for f in labels["fields"] if f["name"] == "Show this"]
    assert len(state) == 1 and state[0]["checked"] is True, state


async def test_the_withheld_values_are_really_in_the_document():
    """THE CONTROL for R4 to R6. Three absences prove nothing unless the
    strings were there to begin with -- a fixture that never carried them
    would make all three sweeps vacuous."""
    for planted in (FILE_PLACEHOLDER, PASSWORD_VALUE, CHECKBOX_TOKEN, RADIO_TOKEN):
        assert planted in VALUES_HTML, planted


async def test_a_value_outside_the_container_is_not_returned(run_values):
    """CONTAINMENT, on the value slot. The document carries values in a loose
    input and in the wrong dialog, and neither is in the answer."""
    result, _ = await run_values(VALUES_HTML)
    rendered = json.dumps(result)
    assert "PLANTED-OUTSIDE-THE-CONTAINER" not in rendered
    assert "PLANTED-IN-THE-WRONG-DIALOG" not in rendered
    assert "PLANTED-OUTSIDE-THE-CONTAINER" in VALUES_HTML
    assert "PLANTED-IN-THE-WRONG-DIALOG" in VALUES_HTML


# ---------------------------------------------------------------------------
# R7. The contenteditable, which is the field this tool exists for
# ---------------------------------------------------------------------------


async def test_the_editable_content_arrives_as_a_value_and_not_as_a_name(run_values):
    """THE FIELD THAT MADE THE LABEL TOOL BREAK ITS OWN PROMISE, read the
    right way round.

    LinkedIn draws the headline as a ``div[role=textbox]`` with no aria-label,
    no label-for and no title, so its accessible NAME resolves to its own
    content. The label tool refuses that as ``<content>``. This tool KEEPS the
    refusal in the name slot and publishes the content ONCE, in the value slot
    -- so the answer never says "the control called <his headline> holds <his
    headline>", which would be the same string published twice under two
    different promises."""
    result, _ = await run_values(VALUES_HTML)
    record = by_label(result, "<content>")
    assert record["name_source"] == "content"
    assert record["value"] == EDITABLE_VALUE
    assert record["value_source"] == "content"
    # Published exactly once: the name slot holds the marker, not the string.
    assert json.dumps(result).count(EDITABLE_VALUE) == 1


# ---------------------------------------------------------------------------
# R8 / R9. One string shape, two opposite answers, decided by the slot
# ---------------------------------------------------------------------------


async def test_a_value_that_looks_like_a_urn_is_not_substituted(run_values):
    """THE ONE PLACE THIS PACKAGE DELIBERATELY DOES NOT SHAPE WHAT IT
    PUBLISHES, and the reason is that the alternative fails SILENTLY.

    A headline may legally contain a urn, a member path, a company path, a
    possessive or a long digit run. Substituting any of them produces a string
    that LOOKS like his value and is not, and he would paste it back believing
    it was -- so the tool would have caused exactly the loss it exists to
    prevent."""
    result, _ = await run_values(VALUES_HTML)
    record = by_label(result, "Recent activity")
    assert record["value"] == URN_IN_A_VALUE
    # And the substitution really would have changed it, so this is a
    # measurement rather than a string that happens to survive.
    assert shape.census_substitute(URN_IN_A_VALUE) != URN_IN_A_VALUE


async def test_a_name_that_looks_like_a_urn_IS_substituted(run_values):
    """THE PAIR WITH R8. The same urn, in a LABEL, comes back substituted --
    a urn in a label identifies somebody whichever container it was read in,
    and that argument does not weaken because a value sits beside it."""
    result, _ = await run_values(VALUES_HTML)
    expected = shape.census_substitute(URN_IN_A_LABEL)
    assert expected != URN_IN_A_LABEL
    record = by_label(result, expected)
    assert record["value"] == "PLANTED-BESIDE-A-URN-LABEL"


# ---------------------------------------------------------------------------
# R10. Truncation is reported, never disguised
# ---------------------------------------------------------------------------


async def test_a_long_value_is_cut_and_says_so(run_values):
    """A TRUNCATED VALUE IS A BROKEN RESTORE, NOT A SHORTER ONE.

    The ceiling sits above the longest profile field LinkedIn has, so this is
    the case nobody should meet -- which is exactly why it is asserted. The
    honest failure is to say the string was cut and report its real length;
    the dishonest one is a prefix that looks complete."""
    result, _ = await run_values(VALUES_HTML)
    record = by_label(result, "Long")
    assert record["value_truncated"] is True
    assert record["value_chars"] == len(LONG_VALUE)
    assert len(record["value"]) == dom.EDITOR_VALUE_MAX_CHARS
    assert record["value_chars"] > len(record["value"])


async def test_an_ordinary_value_is_not_flagged_truncated(run_values):
    """The other side of the flag, so a mutation setting it always-true fails
    here rather than passing everything above."""
    result, _ = await run_values(VALUES_HTML)
    record = by_label(result, "First name")
    assert record["value_truncated"] is False
    assert record["value_chars"] == len(TEXT_VALUE)


async def test_an_empty_value_is_not_an_absent_one(run_values):
    """ABSENT IS NOT ZERO, on the field where confusing the two would mean
    restoring an empty string over real content.

    An empty text input HELD an empty string: ``value`` is ``""`` and
    ``value_chars`` is ``0``. A control with no value route at all -- a button
    -- has ``value`` ``None`` and ``value_chars`` ``None``. Both are in this
    one answer, so the distinction is shown rather than described."""
    result, _ = await run_values(VALUES_HTML)
    empty = by_label(result, "Empty")
    assert empty["value"] == ""
    assert empty["value_chars"] == 0
    assert empty["value_source"] == "native"

    anchor = by_label(result, "Save")
    assert anchor["value"] is None
    assert anchor["value_chars"] is None
    assert anchor["value_source"] == "none"


# ---------------------------------------------------------------------------
# R11 / R12. The record shape, and the key that pairs it with the other tool
# ---------------------------------------------------------------------------


async def test_the_ten_fields_are_present_on_every_returned_control(run_values):
    """THE ENUMERATION, PINNED against what a caller actually receives.

    The block above ``EDITOR_VALUES_JS`` lists ten field names, and this
    module's sibling has already lost a field once by describing a dict
    instead of listing it. So the ten are named here and their COUNT is
    asserted, which is what makes the comment's "ten" checkable rather than a
    number a reader has to trust."""
    result, _ = await run_values(VALUES_HTML)
    expected = {
        "name",
        "name_source",
        "tag",
        "type",
        "role",
        "index",
        "value",
        "value_source",
        "value_chars",
        "value_truncated",
    }
    assert len(expected) == 10
    for field in result["fields"]:
        assert set(field) == expected, sorted(field)


async def test_index_is_the_position_inside_the_container(run_values):
    """THE PAIRING KEY, held to actually pairing.

    Both tools enumerate the same container with the same control selector, so
    position lines a value up with the label tool's record for the same
    control. That is asserted here by reading BOTH tools over one document and
    checking the two name lists are identical position for position -- which
    is the only thing that makes ``index`` mean anything.

    ACROSS TWO CALLS THIS IS PAIRING ACROSS TWO RENDERS. Nothing here can
    detect a control that moved between them; the tool says so and this test
    cannot make it false."""
    values, _ = await run_values(VALUES_HTML)
    labels, _ = await run_values(VALUES_HTML, tool=linkedin_profile_editor_fields)

    assert [f["index"] for f in values["fields"]] == list(
        range(len(values["fields"]))
    )
    assert [f["name"] for f in values["fields"]] == [
        f["name"] for f in labels["fields"]
    ]
    assert values["container"] == labels["container"]


async def test_the_member_segment_is_nowhere_in_the_answer(run_values):
    """His slug is COMPARED AND DISCARDED, the same as in the label tool. It
    is not in this answer, which is why the ownership block reports
    ``same_member`` rather than the value."""
    result, _ = await run_values(VALUES_HTML)
    rendered = json.dumps(result)
    assert MEMBER_SLUG not in rendered, rendered
    for part in rendered.split("/"):
        assert part != MEMBER_SLUG
    assert result["self_ownership"]["same_member"] is True


# ---------------------------------------------------------------------------
# R14 / R15. The structural guards
# ---------------------------------------------------------------------------


def test_the_injected_script_only_reads():
    """The same scan ``test_readonly.py`` runs, asserted here too because this
    is the widest-publishing script in the package -- if any script deserves a
    second reader, it is the one that returns a man's profile verbatim."""
    assert readonly.scan_js_for_mutations(dom.EDITOR_VALUES_JS) == []


def test_that_scan_can_fail_on_this_script():
    """THE CONTROL: the scanner is shown catching a mutation planted in this
    very script, so the assertion above is not vacuous."""
    planted = dom.EDITOR_VALUES_JS.replace(
        "const anchors = [];",
        "const anchors = []; document.querySelector('button').click();",
    )
    assert ".click(" in readonly.scan_js_for_mutations(planted)


def test_the_script_never_scrolls():
    """Absent means UNKNOWN in this tool's output too, and that promise is
    only honest while the script genuinely does not scroll. It matters more
    here than in the label reader: a field this did not see is a field it
    cannot restore."""
    for token in ("scrollIntoView", "window.scrollTo", "scrollBy", "scrollTop"):
        assert token not in dom.EDITOR_VALUES_JS


def test_the_label_readers_no_value_assertion_is_still_unconditional():
    """WHY THERE ARE TWO SCRIPTS AND NOT ONE FLAG, asserted rather than
    argued in a comment.

    ``EDITOR_FIELDS_JS`` could have grown a ``cfg.readValues`` branch and
    saved a copy of the name chain. It would also have turned the label
    reader's unconditional "contains no value read" guard into a claim about
    a branch, on the narrowest and most-scrutinised reader in this package.
    That guard is re-asserted from here so that anyone merging the two
    scripts fails in the file that would have benefited from the merge."""
    assert ".value" not in dom.EDITOR_FIELDS_JS
    assert "readValues" not in dom.EDITOR_FIELDS_JS


async def test_the_three_name_chains_agree():
    """THREE COPIES OF THE NAME CHAIN, HELD TO AGREEING.

    ``CENSUS_JS`` resolves names document-wide, ``EDITOR_FIELDS_JS`` resolves
    them inside one container, and now ``EDITOR_VALUES_JS`` resolves them
    again beside the values. The duplication is forced -- a script assembled
    from a shared fragment cannot be certified by ``test_readonly.py``'s
    call-site resolver -- and a copy nothing compares is a copy that goes
    stale.

    So all three run over ONE document and the names they resolve for the
    container's controls are compared: name AND ``name_source``, because the
    source is the half that says which route won. The pairing with the label
    reader is asserted EXACTLY, since those two see the same container; the
    census is document-wide, so its names are checked for containment."""
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(viewport=dict(EDITOR_VIEWPORT))
        try:
            page = await context.new_page()
            await page.set_content(
                VALUES_HTML, wait_until="domcontentloaded", timeout=60_000
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
            shared = {
                "controlSelector": dom.CENSUS_CONTROL_SELECTOR,
                "containerSelector": dom.EDITOR_CONTAINER_SELECTOR,
                "anchorName": dom.EDITOR_ANCHOR_NAME,
                "maxControls": dom.EDITOR_MAX_CONTROLS,
                "maxChars": 300,
            }
            fields = await page.evaluate(dom.EDITOR_FIELDS_JS, shared)
            values = await page.evaluate(
                dom.EDITOR_VALUES_JS,
                {**shared, "maxValueChars": dom.EDITOR_VALUE_MAX_CHARS},
            )
        finally:
            await context.close()
            await browser.close()

    from_fields = [(row["name"], row["name_source"]) for row in fields["controls"]]
    from_values = [(row["name"], row["name_source"]) for row in values["controls"]]
    assert from_fields, from_fields
    # THE FIXTURE'S PRECONDITION, asserted rather than assumed: at least one
    # control names itself through a route that BEAT another available route.
    # Without that this comparison passes under any reordering of the chain,
    # which is the state the first draft of this file was in.
    assert ("Aria route wins", "aria-label") in from_values, from_values
    assert "Label route loses" not in [pair[0] for pair in from_values]
    assert from_values == from_fields

    by_name = {
        (row["name"], row["name_source"])
        for row in census["controls"]
        if row["name"]
    }
    for pair in from_values:
        # The census gives the editable its CONTENT where both editor scripts
        # give the marker; that difference is the whole point of the marker,
        # so the one pair it produces is not looked for in the census set.
        if pair[1] == "content":
            continue
        assert pair in by_name, (pair, sorted(by_name))


def test_the_census_has_no_path_into_this_reader():
    """A CALLER MUST NOT BE ABLE TO REACH THIS BEHAVIOUR THROUGH THE CENSUS.

    Read off the SOURCE rather than argued: ``read_self_owned_editor_values``
    is named exactly once in ``server.py``, and the surface census's body does
    not name it."""
    source = Path(server_module.__file__).read_text(encoding="utf-8")
    assert source.count("read_self_owned_editor_values") == 1
    body = _tool_body(source, "linkedin_surface_census")
    assert "read_self_owned_editor_values" not in body
