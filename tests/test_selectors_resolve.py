"""Every selector this package builds must RESOLVE in a real browser.

THE DEFECT THIS FILE EXISTS FOR, found 2026-09-02 while building something
else. Three of ``dom.py``'s selector builders emitted

    role=radio[name="Always on"][exact=true]

and ``exact`` is not an attribute Playwright's role engine has. Handed to any
page it raises ``Unknown attribute "exact"``. So three of the ten performable
capabilities could not act:

* ``update_setting`` -- ``named_role_selector`` builds its ONLY click.
* ``publish_post`` -- ``post_submit_selector`` builds the submit after the
  fill, so the text landed in his composer and nothing was posted.
* ``comment_on_item`` -- ``comment_submit_selector``, same shape.

**NOTHING CAUGHT IT BECAUSE EVERY TEST COMPARED THE STRING.** Three
assertions in ``test_writes_nine.py`` checked the literal, and the fake page
in that file records ``page.clicks`` as whatever string it is handed, so it
accepts a selector no browser would. **A selector test that never resolves the
selector is a check that cannot fail on the one thing the selector is for.**

Nothing had ever fired, which is exactly why it survived to be found by
somebody building a fourth thing.

## What this file does that the string assertions cannot

Builds every selector and RESOLVES it against a local headless page that
carries a matching control. A builder whose output is malformed raises; one
whose output is well-formed and wrong matches nothing. Both are failures here
and neither is visible to a string comparison.

**THE LIST IS DERIVED BY AST, not hand-maintained.** Every ``*_selector``
function in ``dom.py`` must be exercised below or carry a reason on
:data:`NOT_RESOLVED_HERE` -- and an entry there is CHECKED rather than waived,
the same discipline ``test_reader_reachability.py`` keeps. A hand-written list
of selectors to test is the same defect one level up.

Nothing here reaches LinkedIn or an account. The markup is invented and every
label in it comes from a constant this package already measured, so a renamed
label fails here too rather than silently making the fixture stop matching.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from linkedin_server import dom, shape

DOM = pathlib.Path(dom.__file__)

VIEWPORT = {"width": 1280, "height": 720}

SAVE_LABEL = "Save the job"
FOLLOW_LABEL = sorted(shape.FOLLOW_LABELS)[0]
COMPANY_ID = "5300011"

#: Selector builders NOT resolved here, each with the reason. AN ENTRY IS A
#: CLAIM THAT IS ITSELF CHECKED: the test below asserts the name really is a
#: builder in ``dom.py``, so a stale entry fails as loudly as a missing one.
NOT_RESOLVED_HERE: dict[str, str] = {
    # The one selector in this package that is not a Playwright selector at
    # all -- it is an xpath, and the reason it is an xpath is that it has to
    # walk UP from a company link to the row that contains it. It IS resolved,
    # against the real tracker captures, in tests/test_writes.py; building a
    # synthetic document faithful enough to exercise it here would be
    # reproducing those captures badly.
    "unfollow_control_selector": (
        "an xpath resolved against the committed followed-companies captures "
        "in tests/test_writes.py, where the row structure it climbs is real "
        "rather than invented"
    ),
    # THE ONLY BUILDER HERE WHOSE MATCH IS AN ACCESSIBLE NAME OF A PERSON.
    # Every control on this file's PAGE is furniture with a fixed label, so a
    # suggestion row is the one thing it cannot honestly draw: the selector's
    # subject is a name supplied at call time, and a fixture inventing one
    # would resolve a string this builder will never be handed.
    #
    # It IS resolved -- in tests/test_typeahead_gate.py, in a real browser,
    # against a listbox of two suggestions, including the case that matters:
    # his row drawn SECOND, so a builder aiming by position would press a
    # stranger. That file also pins the measurement that forced the regex
    # spelling, which this fixture could not have exposed.
    "typeahead_option_selector": (
        "resolved in tests/test_typeahead_gate.py against a real listbox, "
        "because its match is the ACCESSIBLE NAME of a suggestion and this "
        "file's page has no suggestions to name"
    ),
}

#: One document carrying a control for every builder below. Every label is
#: read from the constant the builder uses, so a renamed constant fails this
#: file instead of quietly producing a fixture that no longer matches.
PAGE = (
    "<!doctype html><html><body><main>"
    # named_role_selector -- the dark-mode radio group's shape.
    '<input type="radio" aria-label="Always on">'
    # ... and a NEAR MISS, so exactness is tested rather than assumed.
    '<input type="radio" aria-label="Always on, recommended">'
    f'<button aria-label="{SAVE_LABEL}">save</button>'
    f'<button aria-label="{FOLLOW_LABEL}">follow</button>'
    f'<div role="textbox" aria-label="{dom.POST_EDITOR_LABEL}"></div>'
    f"<button>{dom.POST_SUBMIT_NAME}</button>"
    f'<div role="textbox" aria-label="{dom.COMMENT_EDITOR_LABEL}"></div>'
    f"<button>{dom.COMMENT_CONTROL_NAME}</button>"
    f'<button aria-label="{dom.REACTION_OFF_LABEL}">react</button>'
    '<button aria-label="Someone to connect">invite</button>'
    # THE COMPOSER'S THREE, added 2026-09-02 with send_message. The recipient
    # is drawn as a LABEL-FOR pair rather than with an aria-label, because
    # that is how the live surface names it -- measured, "an input with
    # role=combobox named through label-for" -- and an aria-label here would
    # make this fixture prove the selector against a naming route the real
    # page does not use.
    f'<label for="msg-recipients">{dom.MESSAGE_RECIPIENT_LABEL}</label>'
    '<input id="msg-recipients" role="combobox">'
    # The body carries NO LABEL, which is the point: it is addressed by role
    # alone. Note this page now draws THREE div[role=textbox] -- the post
    # editor, the comment editor and this -- so compose_body_selector matches
    # three here. That is correct and is why this test asserts >= 1: the
    # body's exactly-one property is a fact about the COMPOSER, enforced by
    # dom.read_compose_modes refusing textbox_count_not_one, not a fact about
    # the selector.
    '<div role="textbox"></div>'
    f"<button>{dom.MESSAGE_SEND_NAME}</button>"
    '<a href="/jobs/view/1/">a job row</a>'
    "</main></body></html>"
)


def build_all() -> dict[str, str]:
    """Every selector, built exactly as the capability that uses it builds it."""
    return {
        "named_role_selector": dom.named_role_selector("radio", "Always on"),
        "save_control_selector": dom.save_control_selector(SAVE_LABEL),
        "follow_control_selector": dom.follow_control_selector(FOLLOW_LABEL),
        "post_editor_selector": dom.post_editor_selector(),
        "post_submit_selector": dom.post_submit_selector(),
        "comment_editor_selector": dom.comment_editor_selector(),
        "comment_submit_selector": dom.comment_submit_selector(
            dom.COMMENT_CONTROL_NAME
        ),
        "reaction_control_selector": dom.reaction_control_selector(),
        "invite_control_selector": dom.invite_control_selector(0),
        "tracker_list_selector": dom.tracker_list_selector(),
        "compose_recipient_selector": dom.compose_recipient_selector(),
        "compose_body_selector": dom.compose_body_selector(),
        "compose_send_selector": dom.compose_send_selector(),
    }


def _selector_builders() -> list[str]:
    """Every ``*_selector`` function defined in ``dom.py``, by AST."""
    tree = ast.parse(DOM.read_text(encoding="utf-8"))
    return sorted(
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.endswith("_selector")
    )


def test_every_builder_in_dom_is_covered_or_declared():
    """A NEW BUILDER CANNOT ARRIVE UNTESTED, which is the half of this file
    that keeps working after today.

    Fixing three selectors is worth one commit. Making the fourth one
    impossible to add without resolving it is worth the file.
    """
    builders = _selector_builders()
    assert len(builders) > 5, builders
    covered = set(build_all()) | set(NOT_RESOLVED_HERE)
    missing = [name for name in builders if name not in covered]
    assert not missing, (
        "%s is a selector builder in dom.py that no test resolves and no "
        "entry explains. A selector nobody hands to a browser is a string." % missing
    )
    for name, reason in NOT_RESOLVED_HERE.items():
        assert name in builders, "%s is declared and is not a builder" % name
        assert len(reason.strip()) > 40, (name, reason)


@pytest.mark.parametrize("name", sorted(build_all()))
async def test_the_selector_resolves_against_a_real_page(name):
    """THE CHECK THE STRING COMPARISONS COULD NOT MAKE.

    A malformed selector RAISES; a well-formed one pointed at nothing returns
    zero. The three that shipped broken did the first, on every page, for
    three capabilities that had never been fired.
    """
    playwright = pytest.importorskip("playwright.async_api")
    selector = build_all()[name]
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(viewport=dict(VIEWPORT))
        try:
            page = await context.new_page()
            await page.set_content(
                PAGE, wait_until="domcontentloaded", timeout=60_000
            )
            count = await page.locator(selector).count()
        finally:
            await context.close()
            await browser.close()

    assert count >= 1, (
        "%s built %r and it matched nothing on a page drawn to carry its "
        "control." % (name, selector)
    )


async def test_the_role_selectors_match_by_name_and_by_case():
    """WHAT THE SUFFIX ACTUALLY BUYS, asserted after MEASURING it rather than
    after believing the comment beside it.

    The first draft of this test asserted that the fix preserved protection
    against a SUBSTRING match, because that is what the code comment claimed
    the broken ``[exact=true]`` was for. **A mutation dropping the suffix
    entirely PASSED it.** Measured against this Playwright: the role engine
    matches a name WHOLE, never as a substring, with or without a suffix --
    so the clause was defending against something the engine does not do, and
    a test asserting it could not fail.

    What ``s`` does buy is CASE SENSITIVITY: ``[name="always on"]`` matches 0
    and ``[name="always on"i]`` matches 1. That is the property pinned here,
    and the mutation that breaks it is ``s`` -> ``i``.

    **AND THIS ASSERTION IS THE GUARD, NOT THE SUFFIX. DO NOT DELETE IT ON
    THE GROUNDS THAT THE ``s`` COVERS IT.** Case-sensitive is also this
    Playwright version's DEFAULT, which is why a mutation dropping the suffix
    entirely still passes -- so the suffix is documentation, and what actually
    protects this package from a future Playwright flipping that default is
    the line below pinning ``[name="always on"]`` to 0. Remove it and the
    suffix goes on LOOKING correct while silently doing nothing, which is the
    state the ``[exact=true]`` clause was in for a day and a half.

    The whole-name behaviour is asserted too -- it is real and load-bearing on
    a radio group, where ``Always on`` and ``Always on, recommended`` are
    different destinations -- but it is asserted as a fact about the ENGINE
    rather than as something this builder's spelling achieves.
    """
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(viewport=dict(VIEWPORT))
        try:
            page = await context.new_page()
            await page.set_content(
                PAGE, wait_until="domcontentloaded", timeout=60_000
            )
            assert '"Always on"' in PAGE and '"Always on, recommended"' in PAGE
            exact = await page.locator(
                dom.named_role_selector("radio", "Always on")
            ).count()
            longer = await page.locator(
                dom.named_role_selector("radio", "Always on, recommended")
            ).count()
            # THE CASE-SENSITIVITY HALF, which is what the suffix pins. Built
            # through the same builder, so a suffix change reaches it.
            wrong_case = await page.locator(
                dom.named_role_selector("radio", "always on")
            ).count()
            # And the whole-name half, asserted as a fact about the ENGINE.
            fragment = await page.locator(
                dom.named_role_selector("radio", "Always")
            ).count()
        finally:
            await context.close()
            await browser.close()

    assert exact == 1, (
        "the short name matched %d controls on a page drawing two radios "
        "whose names differ only by a suffix" % exact
    )
    assert longer == 1, longer
    assert wrong_case == 0, (
        "a lowercase spelling of the name matched %d control(s). The builder "
        "has stopped matching case-sensitively -- check the suffix." % wrong_case
    )
    assert fragment == 0, (
        "a prefix of the name matched %d control(s), so the engine is "
        "substring-matching. Every selector this package builds assumes it "
        "does not." % fragment
    )


def test_no_builder_emits_the_attribute_that_does_not_exist():
    """THE CHEAP GUARD BESIDE THE EXPENSIVE ONE, and it is not redundant.

    The parametrised test above needs a browser and is skipped without one.
    This one runs anywhere and catches the exact regression that shipped: the
    string ``exact=`` inside a ``role=`` selector. It cannot replace the
    resolution test -- a differently-malformed selector passes here -- which
    is why both exist and why this one says so.
    """
    for name, selector in build_all().items():
        if not selector.startswith("role="):
            continue
        assert "exact=" not in selector, (
            "%s emits %r. Playwright's role engine has no 'exact' attribute; "
            "exact matching is the 's' suffix on the name value." % (name, selector)
        )
