"""The result's ``verification`` field, for an action that declares it has none.

THE DEFECT THIS FILE REPRODUCES, found 2026-09-02. ``writes.perform`` returns
one dict literal, and that literal sets the key ``"verification"`` TWICE --
once near the top, from ``spec.unverifiable.as_block()``, and once again near
the bottom, from the expected/observed comparison block. Python evaluates both
and the LATER key wins. So the first is computed, allocated, and thrown away
before the caller ever sees the dict.

WHY THAT IS NOT A COSMETIC DUPLICATION. Two actions in this package declare
``unverifiable`` on their spec -- ``publish_post`` and ``send_invitation`` --
and for those two the three-part disclosure is the ONLY thing the result has to
say about the outcome. The comment sitting directly above the discarded key
says it is "REPEATED ON PURPOSE", and names the reason: he reads the preview to
decide and the result to find out what happened, and the sentence he needs
AFTER acting is the third one -- what to go and look at. That sentence is
exactly what the duplicate key deletes. The result reports ``performed:
"unknown"`` and hands him no instruction at all.

AND WHAT SURVIVES IN ITS PLACE IS WORSE THAN NOTHING. The winning block builds
its ``surface`` field from an if/elif chain over ``spec.action``. There is no
arm for ``publish_post``, so it falls through to the final ``else``, which
reads:

    "a DIFFERENT surface from the one clicked. A control that redraws itself
    is the weakest possible witness to its own effect, so the confirmation
    comes from LinkedIn's own saved list with its own per-tab count."

Every clause of that is false here. Nothing was read. There is no different
surface -- the whole point of the ``Unverifiable`` declaration on this spec is
that the activity rail renders intermittently and cannot answer. And the saved
list is a job-tracker tab that has no bearing on whether a post published. So
the one action in this package that most explicitly declares its outcome
unconfirmable ships a result claiming an independent surface confirmed it.

That is the precise failure ``Unverifiable``'s own docstring exists to forbid:
"A CHECK THAT CANNOT PASS MAY NEVER SHIP AS THOUGH IT MIGHT." It was written
about ``apply_job``'s old ``to_state`` comparison. The duplicate key
reintroduces the same shape one layer further out -- not in the check, but in
the block that reports it.

WHY NOTHING CAUGHT IT. ``tests/test_unverifiable_outcomes.py`` asserts the
INVARIANT -- that an action has exactly one of {a branch in ``_verify_after``,
an ``Unverifiable`` on its spec} -- and ``publish_post`` satisfies it: the spec
carries the declaration and ``_verify_after`` returns early on it. That is a
statement about the SPEC and about ``_verify_after``. It says nothing about
whether ``perform``'s return value carries the declaration out to the caller,
and a duplicate key inside a dict literal is invisible to it. Meanwhile
``tests/test_writes_nine.py`` drives ``perform`` end to end for exactly one
action, ``update_setting``, which is verifiable and therefore takes the OTHER
branch -- the surviving one. There has never been an end-to-end ``perform``
test for ``publish_post`` or ``send_invitation``, which is to say: there has
never been a test that would run the discarded branch.

WHAT THIS FILE DOES. It drives the real chain -- preview, consume, perform --
for ``publish_post`` over a local headless page, and asserts on what the caller
actually receives. Both tests are RED against the tree as committed on
2026-09-02. They are the reproduction, not the fix; ``linkedin_server/writes.py``
is not touched here.

NOTHING HERE REACHES LINKEDIN OR AN ACCOUNT. The navigator is the fixture
server from ``tests/test_writes.py`` and the composer below is invented markup
served by ``set_content``. Every label in that markup is read from the constant
``linkedin_server.dom`` already measured, so a renamed label fails this file
rather than quietly producing a fixture the readers no longer match.
"""

from __future__ import annotations

import json

from linkedin_server import dom, writes
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_writes import (  # noqa: F401 -- two of these are fixtures
    FixtureNavigator,
    browser_page,
    writes_on,
)
from tests.test_writes_nine import FEED_MARKUP, TARGETS

#: The text this write would type, taken from the corpus the rest of the write
#: suite already addresses ``publish_post`` with rather than typed a second
#: time. It is the GRANT's target, so it is also the exact string ``perform``
#: fills into the composer -- see ``tests/test_typed_bytes.py``, which pins
#: that identity.
POST_TEXT = TARGETS["publish_post"]

#: THE SHAREBOX, and it is the surface ``perform`` navigates to -- distinct
#: from the feed, which is what the PREVIEW reads. The two are different pages
#: in this chain and the navigator has to serve both or the run stops halfway.
#:
#: Read off the spec rather than typed, for the same reason every label below
#: is read off ``dom``: a moved address should fail here loudly instead of
#: leaving a navigator serving a page nobody asks for.
SHAREBOX_URL = str(spec_for_action("publish_post").url_template)

#: THE COMPOSER, BUILT TO THE MEASURED SHAPE AND NOT A LINE MORE.
#:
#: ``_live_control`` and ``_publish_submit_gate`` between them require four
#: things of this page, and all four are measured facts about the live
#: sharebox rather than conveniences:
#:
#:   1. exactly ONE editor matching ``dom.post_editor_selector()`` -- a
#:      contenteditable wearing role=textbox and the measured aria-label;
#:   2. exactly ONE control matching ``dom.post_submit_selector()`` -- a
#:      button whose accessible name is exactly ``dom.POST_SUBMIT_NAME``;
#:   3. that control DISABLED while the composer is empty, which is what
#:      ``_live_control`` requires before it will type anything (an enabled
#:      one means content is already in the box and it refuses rather than
#:      filling over a draft it cannot read back);
#:   4. that same control ENABLED after the fill, which is the observable
#:      disabled-to-enabled transition ``_publish_submit_gate`` requires
#:      before it will append the submit to the click plan.
#:
#: THE SCRIPT IS WHAT MAKES 3 AND 4 ONE PAGE RATHER THAN TWO. Every other fake
#: surface in this suite is static, because every other gate reads a state
#: LinkedIn had already drawn. This gate reads a TRANSITION -- it is the whole
#: of why typing is safe on this surface and unsafe on the comment surface one
#: page over -- and a static fixture cannot carry one. Serving a second,
#: enabled capture after the fill would be the alternative, and it would be
#: strictly weaker: it would assert that the gate proceeds when handed an
#: enabled control, which is not the claim. The claim is that THE FILL
#: produces the enabling.
#:
#: The script is three lines and branches on the editor's own text content, so
#: a fill that landed nothing leaves the control disabled and the gate refuses
#: -- which is the behaviour under test, not a hole in it.
SHAREBOX_MARKUP = (
    "<html><body>"
    '<div contenteditable="true" role="textbox" aria-label="'
    + dom.POST_EDITOR_LABEL
    + '"></div>'
    '<button disabled id="post-submit">' + dom.POST_SUBMIT_NAME + "</button>"
    "<script>"
    "var editor = document.querySelector('[contenteditable]');"
    "var submit = document.getElementById('post-submit');"
    "editor.addEventListener('input', function () {"
    "  submit.disabled = (editor.textContent.trim().length === 0);"
    "});"
    "</script>"
    "</body></html>"
)


def _publish_pages() -> dict[str, str]:
    """The two surfaces one publish touches, and no others.

    The FEED is what ``preview`` reads -- ``publish_post``'s ``state_from`` is
    ``feed_composer``, and the reader there counts controls named 'Start a
    post'. The SHAREBOX is where ``perform`` navigates to type. Serving only
    these two means a gate that wandered anywhere else raises out of
    ``FixtureNavigator`` naming the url, rather than quietly reading whatever
    happened to be loaded.

    ``FEED_MARKUP`` is imported rather than rebuilt: it is the minimum page the
    feed reader returns a settled state on, and a second copy of it here would
    be a second thing to keep in step with ``dom``'s constants.
    """
    return {
        writes.FEED_URL: FEED_MARKUP,
        SHAREBOX_URL: SHAREBOX_MARKUP,
    }


async def _published(page) -> dict:
    """One publish, all the way through the real gate chain. Returns the result.

    THE LONG WAY ROUND, DELIBERATELY, exactly as ``_setting_grant`` in
    ``tests/test_writes_nine.py`` does it: ``perform`` requires a grant that
    ``consume`` has already burned, so a grant handed straight to it would be
    refused and the test would never reach the block it is about. Every gate
    in between is the shipped one -- the direction is read off the feed, the
    token is minted only from that reading, ``consume`` burns it, ``perform``
    re-reads the composer before typing, and the publish gate re-reads it
    again after.
    """
    spec = spec_for_action("publish_post")
    nav = FixtureNavigator(_publish_pages())
    block = await preview(spec, target=POST_TEXT, navigator=nav, page=page)
    grant = consume(
        block["to_confirm"], action="publish_post", target=POST_TEXT
    )
    return await writes.perform(nav, page, grant)


def _assert_the_chain_actually_ran(result: dict) -> None:
    """The harness's own self-check, asserted BEFORE the claim under test.

    WHY IT IS HERE. Both tests below fail today, and they must fail for the
    RIGHT reason. Every refusal in this chain -- a composer that did not
    render, a fill that landed nothing, a submit that stayed disabled --
    produces a result whose ``verification`` is equally wrong, so a fixture
    that had quietly stopped working would keep these tests red after the
    defect was fixed. That is the worst outcome available: a red that survives
    its own repair teaches whoever repairs it that the repair did not work.

    So the three facts that prove the chain reached the end are asserted
    first, and all three PASS against the tree as committed. If one of them
    ever fails, the failure is in this file's fixture and says so.
    """
    assert result["publish_gate"] is not None, (
        "no publish gate ran, which means the fill never happened -- "
        "``perform`` only reaches ``_publish_submit_gate`` from inside the "
        "fill loop. The composer fixture is not the shape the gate requires."
    )
    assert result["publish_gate"]["proceeded"] is True, result["publish_gate"]
    assert result["clicked"]["clicks_made"] == 1, result["clicked"]


async def test_a_declared_unverifiable_result_carries_the_declaration(
    writes_on, browser_page
):
    """The three-part disclosure must reach the caller of ``perform``.

    ``publish_post``'s spec carries an ``Unverifiable``, and
    ``Unverifiable.as_block`` exists to be printed in TWO places -- its own
    docstring says so: "Both, deliberately. He reads the preview before
    deciding and the result after acting, and the sentence he needs after
    acting is the one telling him what to go and look at."

    This asserts the second of those two. The block the caller receives must
    be the disclosure: ``outcome_is_verifiable`` of "NO", and the three fields
    that make the declaration actionable -- what would settle it, why this
    server cannot read that, and what HE must do to find out.

    IT FAILS TODAY, and the shape of the failure is the finding: the key is
    present and holds the OTHER block entirely, because the same dict literal
    assigns ``"verification"`` a second time about a hundred lines further
    down and the later assignment wins. The disclosure is built and discarded
    inside the same expression that returns.

    THE THIRD FIELD IS THE ONE THAT MATTERS MOST and it is the one this loses.
    ``performed`` on this action is "unknown" by construction -- there is
    nothing that could make it anything else -- so the result's entire value
    to him is the instruction to open his profile and look at his recent
    activity. Without it he is told an irreversible act may or may not have
    happened and given nowhere to go.
    """
    result = await _published(browser_page)
    _assert_the_chain_actually_ran(result)

    block = result["verification"]
    assert block.get("outcome_is_verifiable") == "NO", (
        "the result's verification block is not the declaration. What came "
        "back instead: " + json.dumps(block, indent=2, sort_keys=True)
    )
    for field in (
        "what_would_confirm_it",
        "why_this_server_cannot",
        "what_you_must_do_to_find_out",
    ):
        assert str(block.get(field) or "").strip(), (
            f"the declaration's {field!r} is missing or empty. A disclosure "
            "with a hole in it is not one -- the field that goes missing is "
            "always the third, because the first two are about the software "
            "and only the third is about him. Block: "
            + json.dumps(block, indent=2, sort_keys=True)
        )


async def test_a_publish_result_does_not_claim_the_saved_list_confirmed_it(
    writes_on, browser_page
):
    """No result for a post may cite the job tracker as its witness.

    THE SURVIVING BLOCK'S ``surface`` FIELD IS CHOSEN BY AN IF/ELIF CHAIN over
    ``spec.action`` -- ``unfollow_company``, then ``update_setting``, then
    ``apply_job``, then a final ``else``. ``publish_post`` matches none of
    them, so it inherits the else, which was written for the save pair and
    says the confirmation "comes from LinkedIn's own saved list with its own
    per-tab count".

    THAT IS A FALSE CLAIM PRINTED ON AN ACTION WHOSE OUTCOME IS DECLARED
    UNCONFIRMABLE, and it is worse than a missing field in the same way a
    wrong error is worse than no error. Nothing navigated. Nothing was read.
    ``_verify_after`` returns before any comparison for exactly this action,
    on purpose -- its docstring calls that ordering "THE SAFETY PROPERTY, not
    a shortcut", because "a comparison that exists is a comparison somebody
    will later read as evidence". The block then reports a comparison anyway,
    and names a surface that could not answer the question even if it had been
    read: the saved list is a jobs tab, and this action published a post.

    ASSERTED OVER THE WHOLE SERIALISED BLOCK rather than over the ``surface``
    key alone. The claim is that this sentence is nowhere in what he reads
    about verification, not that it has moved to a different field of it --
    ``tests/test_writes_nine.py`` makes the same assertion the same way for
    ``update_setting``, which is the action that first caught this else being
    borrowed by something it does not describe.
    """
    result = await _published(browser_page)
    _assert_the_chain_actually_ran(result)

    printed = json.dumps(result["verification"], indent=2, sort_keys=True)
    assert "saved list" not in printed, (
        "a publish result cites the saved-jobs list as the surface that "
        "confirmed it. Nothing read that list, it could not answer this "
        "question, and this action declares it has no confirming surface at "
        "all. What came back: " + printed
    )
