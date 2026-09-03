"""A CLICK THAT LANDED IS NOT A RECIPIENT THAT IS COMMITTED.

``send_message`` now presses a typeahead suggestion between its two fills.
That press is the missing step -- measured 2026-09-03, a bare fill commits
nobody -- and it introduces the one failure mode this whole flow was designed
to refuse: **a gate reading its own homework.**

The dangerous version of this feature is easy to write and hard to see. The
typeahead gate finds exactly one suggestion carrying his needle, presses it,
and concludes that the message is addressed. Every sentence of that is about
what THIS SERVER DID. None of it is about what LINKEDIN DREW. If pressing a
suggestion does not commit a recipient -- and nobody knows whether it does,
because no reading of a live LinkedIn typeahead has ever been taken -- then a
gate satisfied by its own click would type his message into a composer
addressed to nobody, or to whoever LinkedIn drew first.

So the shipped flow keeps the two claims apart:

    _typeahead_gate     exactly one suggestion carries his needle, and it was
                        pressed.                    A CLAIM ABOUT THE CLICK.
    _recipient_gate     exactly one recipient is COMMITTED and its accessible
                        name carries his needle.    A CLAIM ABOUT THE PAGE.

and only the second one lets his words be typed.

WHAT THIS FILE ADDS THAT ``tests/test_typeahead_gate.py`` DOES NOT
------------------------------------------------------------------
That file tests the gate. This file tests the WIRING, in three registers,
because the invariant lives in how ``perform`` is assembled rather than in any
one function:

1. **BEHAVIOURALLY, THROUGH THE REAL ``perform``**, over two hand-written
   composers that differ in exactly one respect -- whether clicking a
   suggestion commits anybody. The INERT one is the important half: the click
   succeeds, no chip appears, and the run must still refuse with the body
   never typed and the send never pressed.

2. **STRUCTURALLY, OFF THE SYNTAX TREE.** The body fill must be appended
   inside the branch guarded by the RECIPIENT gate and nowhere else, and
   ``_recipient_gate`` must be called with nothing the typeahead step
   produced. Derived from the AST rather than from string counts: a
   ``source.count("dom.compose_body_selector()") == 1`` check goes red the day
   somebody mentions the function in a comment, which is a failure mode this
   repository has already paid for once.

3. **AS A SHOWN-FAILING CONTROL.** Every structural check above is run again
   against a MUTATED copy of ``perform``'s source in which the invariant is
   broken, and asserted to go red. A check that cannot fail certifies nothing.

AND IT PINS THE RECEIPT, WHICH IS WHERE THE DEFECT ACTUALLY LANDED
------------------------------------------------------------------
The first wiring of this feature handed ``typed_text_residue`` ``perform``'s
raw click counter. On the inert run -- press a suggestion, then refuse -- that
made the receipt say ``submit_was_pressed: True`` and
``left_in_the_composer: False``: nothing had been submitted and his composer
held somebody's name. Both false, on the action where a false receipt costs
the most. ``test_the_receipt_does_not_call_a_typeahead_press_a_submit``
reproduces exactly that wiring and asserts it produces exactly those two lies,
so the fix cannot be quietly undone by a future edit that "simplifies" the
subtraction away.

NOTHING HERE REACHES LINKEDIN. Every reading is taken over hand-written markup
in a local headless Chromium. The two fixtures are DOUBLES, not captures, and
what they can and cannot prove is stated on each one.
"""

from __future__ import annotations

import ast
import json

from linkedin_server import writes
from linkedin_server.writes import TARGET_JOIN, spec_for_action

# ONE OWNER PER FIXTURE, which is this suite's standing convention. The empty
# composer and the four invented names live in the module that committed them
# and are imported rather than copied, so a change to ``dom``'s constants
# fails one file instead of silently diverging two.
from tests.test_send_message_gate import (  # noqa: F401
    COMPOSER_MARKUP,
    CHIP_RAIL_EMPTY,
    MESSAGE_BODY,
    MODE_LABEL_SECOND_NAME,
    NAMED_RECIPIENT,
    OPERATOR_STANDIN,
    SOMEBODY_ELSE,
)
from tests.test_writes import FixtureNavigator, writes_on  # noqa: F401

# THE FEED, because the PREVIEW reads the messaging badge off it rather
# than opening messaging -- which is ``send_message``'s ``from_state``
# being ``composer_unmeasured`` on purpose: looking would redirect into a
# stranger's conversation and spend their thread. Imported from the module
# that owns it, so there is one feed double in this suite.
from tests.test_writes_nine import FEED_MARKUP  # noqa: F401
from tests.test_apply_modal_fixture import VIEWPORT, over  # noqa: F401

COMPOSE_URL = spec_for_action("send_message").url_template
TARGET = NAMED_RECIPIENT + TARGET_JOIN + MESSAGE_BODY


# ---------------------------------------------------------------------------
# The two composers, and they differ in ONE respect
# ---------------------------------------------------------------------------
#
# THE LISTBOX IS DRAWN TO MATCH A GUESS, and the guess is named rather than
# hidden. ``dom.TYPEAHEAD_OPTION_SELECTORS`` has never matched anything on a
# real LinkedIn page -- nobody has typed into that combobox through this
# server -- so these rows are shaped to the ARIA contract the first candidate
# assumes. A fixture built from the same guess as the code under test cannot
# validate the guess, and this file does not claim to.
#
# THE ROW'S ACCESSIBLE NAME IS THE WHOLE ROW, name and degree run together,
# because that is what the 2026-09-03 selector measurement found on a live-
# shaped listbox and it is the reason ``typeahead_option_selector`` had to
# become a REGEX. A row whose name were exactly the needle would let the
# quoted whole-string spelling pass here and fail in production.


def _option(name: str, degree: str) -> str:
    return (
        '<div role="option"><span>'
        + name
        + "</span><span>"
        + degree
        + "</span></div>"
    )


LISTBOX = (
    '<div role="listbox">'
    + _option(NAMED_RECIPIENT, "1st")
    + _option(SOMEBODY_ELSE, "2nd")
    + "</div>"
)


def _with_listbox(markup: str, extra: str = "") -> str:
    """Put a typeahead under the composer. DERIVED, and it proves it changed.

    The same assertion ``_with_chips`` makes in the module that owns the base
    fixture, and for the same reason: a derivation anchored on a literal that
    stopped matching becomes a silent no-op, and the test built on it goes on
    passing while testing the base fixture under another name.
    """
    out = markup.replace(CHIP_RAIL_EMPTY, CHIP_RAIL_EMPTY + LISTBOX + extra, 1)
    assert out != markup, (
        "the chip-rail anchor changed nothing, so this variant is the empty "
        "composer wearing another name. Repoint it, and do not delete this."
    )
    return out


#: **THE INERT COMPOSER, AND IT IS THE LOAD-BEARING ONE.** Clicking a
#: suggestion here does exactly nothing, because the markup is static -- which
#: is precisely the state nobody can rule out on the live surface. The click
#: lands, Playwright reports success, and no recipient is committed.
#:
#: This is what "the click is not its own evidence" MEANS, drawn as a page.
COMPOSER_TYPEAHEAD_INERT = _with_listbox(COMPOSER_MARKUP)


#: THE COMMITTING COMPOSER, and it carries a script for the reason
#: ``SHAREBOX_MARKUP`` carries one: this gate reads a TRANSITION, and a static
#: page cannot hold one. Serving a second, already-committed capture instead
#: would assert that the recipient gate proceeds when handed a chip, which is
#: not the claim -- the claim is that THE CLICK produces the chip.
#:
#: IT IS A DOUBLE, NOT A CAPTURE. No LinkedIn markup is involved and the three
#: behaviours it models are the three this flow depends on:
#:
#:   1. clicking an option removes the listbox and appends a chip whose
#:      ``aria-label`` starts with ``Remove`` -- candidate #1 of
#:      ``dom.RECIPIENT_CHIP_SELECTORS``, and a GUESS, exactly as ``_chip``
#:      says where it is defined;
#:   2. typing into the body enables ``Send``, which is the disabled-to-enabled
#:      transition ``_send_gate`` requires;
#:   3. nothing else moves, so a run that got here by any other route fails.
#:
#: WHAT IT PROVES: that the pipeline is ALIVE. Without it every assertion in
#: this file would be satisfied by a ``perform`` that refused unconditionally,
#: which is the shape a section full of refusals cannot distinguish.
COMPOSER_TYPEAHEAD_COMMITS = _with_listbox(
    COMPOSER_MARKUP,
    "<script>"
    "var railOf = function () { return document.getElementById('chip-rail'); };"
    "var bodyOf = function () {"
    "  return document.querySelector('div[role=\\\"textbox\\\"]');"
    "};"
    "var sendOf = function () {"
    "  var all = Array.prototype.slice.call(document.querySelectorAll('button'));"
    "  for (var i = 0; i < all.length; i += 1) {"
    "    if (!all[i].hasAttribute('aria-label')) { return all[i]; }"
    "  }"
    "  return null;"
    "};"
    "document.addEventListener('click', function (event) {"
    "  var node = event.target;"
    "  while (node && node.getAttribute && node.getAttribute('role') !== 'option') {"
    "    node = node.parentNode;"
    "  }"
    "  if (!node || !node.getAttribute) { return; }"
    "  var box = document.querySelector('[role=\\\"listbox\\\"]');"
    "  var chip = document.createElement('button');"
    "  chip.setAttribute('aria-label', 'Remove ' + node.textContent);"
    "  chip.textContent = 'Remove';"
    "  railOf().appendChild(chip);"
    "  if (box) { box.parentNode.removeChild(box); }"
    "}, true);"
    "document.addEventListener('input', function () {"
    "  var body = bodyOf();"
    "  var send = sendOf();"
    "  if (body && send) { send.disabled = (body.textContent.trim().length === 0); }"
    "}, true);"
    "</script>",
)


# ---------------------------------------------------------------------------
# Drivers
# ---------------------------------------------------------------------------


async def _run(page, html: str) -> dict:
    """One ``send_message`` through the REAL ``perform``. Returns the receipt.

    THE LONG WAY ROUND, exactly as ``tests/test_result_verification_block.py``
    drives a publish: ``perform`` refuses any grant ``consume`` has not burned,
    so a fabricated one would be testing a path no caller can take. The
    preview reads nothing off this page -- ``send_message``'s ``from_state`` is
    ``composer_unmeasured`` BY DESIGN, because the preview's gate must not open
    messaging; what it DOES read is the messaging badge on the feed. So the
    navigator serves exactly those two urls and a wandering read fails inside
    it, naming the address it wanted.
    """
    nav = FixtureNavigator({writes.FEED_URL: FEED_MARKUP, COMPOSE_URL: html})
    block = await writes.preview(
        spec_for_action("send_message"), target=TARGET, navigator=nav, page=page
    )
    grant = writes.consume(
        block["to_confirm"], action="send_message", target=TARGET
    )
    return await writes.perform(nav, page, grant)


# ---------------------------------------------------------------------------
# 1. Behaviour: the inert composer must refuse, and it is the important half
# ---------------------------------------------------------------------------


async def test_a_click_that_commits_nobody_still_refuses(writes_on, over):
    """THE INVARIANT, AS A RUN. The click lands; the recipient gate says no.

    Everything about this run looks like success up to the moment it is asked
    the right question. The typeahead drew a listbox, exactly one row carried
    his needle, the row was pressed and Playwright reported no error. And no
    recipient was committed, so his message was never typed.
    """
    block = await over(COMPOSER_TYPEAHEAD_INERT, lambda page: _run(page, COMPOSER_TYPEAHEAD_INERT))

    assert block["typeahead_gate"] is not None
    assert block["typeahead_gate"]["proceeded"] is True, block["typeahead_gate"]
    assert block["clicked"]["error"] is None, block["clicked"]["error"]
    assert block["clicked"]["clicks_made"] == 1, block["clicked"]

    # AND THE ANSWER THAT MATTERS. One recipient was expected by nobody; zero
    # were found; the run stopped.
    assert block["recipient_gate"] is not None
    assert block["recipient_gate"]["proceeded"] is False
    assert (
        block["recipient_gate"]["refused_condition"] == "1_no_recipient_committed"
    ), block["recipient_gate"]

    # HIS WORDS WERE NEVER TYPED. One fill happened -- the recipient -- and the
    # send gate was never reached, so no send control was pressed.
    assert block["send_gate"] is None, block["send_gate"]
    assert block["typed_text"]["submit_was_pressed"] is False
    assert block["typed_text"]["left_in_the_composer"] is True


async def test_the_receipt_does_not_call_a_typeahead_press_a_submit(
    writes_on, over
):
    """THE CONTROL FOR THE RECEIPT DEFECT, and it reproduces the old wiring.

    ``perform`` used to hand ``typed_text_residue`` its raw click counter. On
    the run above that is 1 -- the suggestion -- and the block would have
    reported the message dispatched and the composer clear. Both false.

    This asserts the CORRECT answer off the real receipt AND recomputes the
    block the old way to show what it would have said, so the subtraction
    cannot be removed as a simplification.
    """
    block = await over(COMPOSER_TYPEAHEAD_INERT, lambda page: _run(page, COMPOSER_TYPEAHEAD_INERT))
    clicked = block["clicked"]

    assert clicked["clicks_made"] == 1
    assert clicked["typeahead_clicks"] == 1
    assert block["typed_text"]["submit_was_pressed"] is False
    assert block["typed_text"]["left_in_the_composer"] is True
    assert "still sitting in the composer" in block["typed_text"]["what_to_do"]

    # THE OLD WIRING, RECONSTRUCTED. Feed the raw count and watch it lie.
    old = writes.typed_text_residue(
        spec_for_action("send_message"),
        fills_made=1,
        submit_clicks=clicked["clicks_made"],
        click_error=clicked["error"],
    )
    assert old["submit_was_pressed"] is True
    assert old["left_in_the_composer"] is False
    assert "the submit WAS pressed" in old["what_to_do"]


# ---------------------------------------------------------------------------
# 2. Behaviour: and the pipeline is alive, or the section above proves nothing
# ---------------------------------------------------------------------------


async def test_a_click_that_does_commit_reaches_the_body_and_the_send(
    writes_on, over
):
    """THE POSITIVE CASE, and it goes here for the reason it always does.

    A file full of refusals passes perfectly against a ``perform`` that refuses
    unconditionally. This is the test that fails if the flow stops working.
    """
    block = await over(
        COMPOSER_TYPEAHEAD_COMMITS,
        lambda page: _run(page, COMPOSER_TYPEAHEAD_COMMITS),
    )

    assert block["typeahead_gate"]["proceeded"] is True, block["typeahead_gate"]
    assert block["recipient_gate"]["proceeded"] is True, block["recipient_gate"]
    assert block["send_gate"] is not None
    assert block["send_gate"]["proceeded"] is True, block["send_gate"]

    # TWO CLICKS AND ONE OF THEM WAS THE SUGGESTION. The receipt reports both
    # numbers rather than one that has to be interpreted.
    assert block["clicked"]["clicks_made"] == 2, block["clicked"]
    assert block["clicked"]["typeahead_clicks"] == 1, block["clicked"]
    assert block["typed_text"]["submit_was_pressed"] is True
    assert block["typed_text"]["left_in_the_composer"] is False


#: THE NAMES THAT ARE ONLY EVER ON THE PAGE, never in his request. Every one
#: of them is drawn by these fixtures and none is anything this server was
#: asked for, so a component word of any of them appearing anywhere in a
#: receipt is a name that was READ and then published.
#:
#: HIS OWN NEEDLE IS DELIBERATELY NOT ON THIS LIST, and that distinction is the
#: whole content of the test below. The receipt echoes the grant's canonical
#: target back to him -- it has to, that is the string the token was bound
#: across -- so ``NAMED_RECIPIENT`` appears in it by design. What must never
#: happen is the needle turning up in a block DERIVED FROM READING THE PAGE,
#: because that would mean a gate had resolved a label and kept it.
READ_ONLY_NAMES = (SOMEBODY_ELSE, OPERATOR_STANDIN, MODE_LABEL_SECOND_NAME)

#: The receipt blocks whose content comes from reading LinkedIn rather than
#: from his request. Nothing he typed should be reachable through them either.
READING_BLOCKS = ("typeahead_gate", "recipient_gate", "send_gate", "clicked")


async def test_no_name_this_server_merely_READ_reaches_the_receipt(
    writes_on, over
):
    """A NAME HE SUPPLIED MAY COME BACK. A NAME LINKEDIN DREW MAY NOT.

    Both fixtures draw four people: the one he named, the one LinkedIn drew
    beside him in the dropdown, and the two in the dispatch-radio labels. The
    comparisons all run inside the page and only integers come back, so not one
    component word of the three he did NOT name may appear anywhere in a
    rendered receipt.

    Per WORD rather than per name, because a partial leak is still a leak: a
    receipt carrying one distinctive token has published a person.
    """
    for html in (COMPOSER_TYPEAHEAD_INERT, COMPOSER_TYPEAHEAD_COMMITS):
        block = await over(html, lambda page: _run(page, html))
        rendered = json.dumps(block, default=str).lower()
        for name in READ_ONLY_NAMES:
            for word in name.split():
                assert word.lower() not in rendered, (name, word)


async def test_his_own_needle_never_leaks_out_of_a_block_that_READ_the_page(
    writes_on, over
):
    """THE OTHER HALF, and it is the one a whole-receipt search cannot make.

    ``NAMED_RECIPIENT`` is in the receipt legitimately -- the target echo is
    the string his token was minted against and he is entitled to see it. So a
    search of the whole document proves nothing about the gates. This searches
    only the blocks BUILT FROM READING THE PAGE, where his needle appearing
    would mean a gate had pulled a label into this process and printed it.

    It would fail today on any gate that quoted the row it matched, which is
    the single most natural thing to write into a refusal message and the
    reason this assertion exists rather than being assumed from the design.
    """
    for html in (COMPOSER_TYPEAHEAD_INERT, COMPOSER_TYPEAHEAD_COMMITS):
        block = await over(html, lambda page: _run(page, html))
        for key in READING_BLOCKS:
            rendered = json.dumps(block.get(key), default=str).lower()
            for word in NAMED_RECIPIENT.split():
                assert word.lower() not in rendered, (key, word)


# ---------------------------------------------------------------------------
# 3. Structure: the invariant, read off the syntax tree
# ---------------------------------------------------------------------------
#
# AST RATHER THAN STRING COUNTS, and the difference is not stylistic. A check
# spelled ``source.count("dom.compose_body_selector()") == 1`` goes red the day
# somebody writes the name in a comment, and green if the call moves into a
# branch guarded by the wrong gate. The tree answers the question actually
# being asked: WHICH ``if`` is this call underneath.


def _perform_tree() -> ast.AST:
    import inspect
    import textwrap

    return ast.parse(textwrap.dedent(inspect.getsource(writes.perform)))


def _body_fill_guards(tree: ast.AST) -> list[str]:
    """Every gate whose ``["proceed"]`` guards a body-fill append.

    Returns the NAMES of the gate variables tested by each ``if`` that encloses
    a call to ``dom.compose_body_selector()``. The invariant is that this list
    is exactly ``["recipient_gate"]``.
    """
    def _is_body_append(node: ast.AST) -> bool:
        for inner in ast.walk(node):
            if (
                isinstance(inner, ast.Call)
                and isinstance(inner.func, ast.Attribute)
                and inner.func.attr == "compose_body_selector"
            ):
                return True
        return False

    guards: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        if not any(_is_body_append(stmt) for stmt in node.body):
            continue
        for sub in ast.walk(node.test):
            if isinstance(sub, ast.Subscript) and isinstance(sub.value, ast.Name):
                guards.append(sub.value.id)
    return guards


def _recipient_gate_arguments(tree: ast.AST) -> list[list[str]]:
    """What every call to ``_recipient_gate`` is handed, as argument names."""
    calls: list[list[str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Name) and func.id == "_recipient_gate"):
            continue
        calls.append(
            [
                arg.id if isinstance(arg, ast.Name) else type(arg).__name__
                for arg in node.args
            ]
            + [kw.arg or "**" for kw in node.keywords]
        )
    return calls


def test_only_the_recipient_gate_may_queue_his_message():
    """THE INVARIANT ITSELF. One guard, and it is not the typeahead's."""
    assert _body_fill_guards(_perform_tree()) == ["recipient_gate"], (
        "the body fill is appended under a branch guarded by something other "
        "than the recipient gate -- or under more than one. If the typeahead "
        "gate can queue his message, the click has become its own evidence "
        "and the whole ordering argument in this file is gone."
    )


def test_the_recipient_gate_is_handed_nothing_the_click_produced():
    """The gate re-reads the page. It is not TOLD what the click achieved.

    ``_recipient_gate(page, grant)`` and nothing else. A third argument -- the
    typeahead reading, the aim, a "we clicked" boolean -- would make the gate's
    answer depend on the step it exists to be independent of, and that is the
    defect however carefully the extra argument were used.
    """
    calls = _recipient_gate_arguments(_perform_tree())
    assert calls == [["page", "grant"]], calls


def test_the_typeahead_result_never_guards_anything_but_its_own_click():
    """``typeahead_gate`` may decide ONE thing: whether to press a row.

    Asserted over every ``if`` in ``perform`` that tests it, so a second use --
    gating the body, the send, or the verification -- fails here rather than
    being noticed later.
    """
    tree = _perform_tree()
    appended: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        tested = {
            sub.value.id
            for sub in ast.walk(node.test)
            if isinstance(sub, ast.Subscript) and isinstance(sub.value, ast.Name)
        }
        if "typeahead_gate" not in tested:
            continue
        for stmt in node.body:
            for inner in ast.walk(stmt):
                if (
                    isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr == "append"
                    and isinstance(inner.func.value, ast.Name)
                ):
                    appended.append(inner.func.value.id)
    assert appended == ["click_plan"], appended


# ---------------------------------------------------------------------------
# 4. The controls. Every check above, shown going red on a broken perform
# ---------------------------------------------------------------------------
#
# THE MUTATIONS ARE APPLIED TO A COPY OF THE SOURCE, never to the module. Each
# one is the smallest edit that breaks the invariant while leaving code that
# still parses -- which is the only kind of mutation worth making, since a
# syntax error would fail every check for the wrong reason.


def _mutated(old: str, new: str) -> ast.AST:
    import inspect
    import textwrap

    source = textwrap.dedent(inspect.getsource(writes.perform))
    assert source.count(old) == 1, (
        f"the mutation anchor {old!r} appears {source.count(old)} times in "
        "perform. Repoint it -- a mutation that does not apply is a control "
        "that tests nothing, which is the failure mode this section exists "
        "to be immune to."
    )
    mutated = source.replace(old, new, 1)
    assert mutated != source
    return ast.parse(mutated)


def test_the_guard_check_goes_red_when_the_typeahead_queues_the_body():
    """THE DEFECT THIS FILE IS ABOUT, planted, and caught.

    Move the body-fill append under the typeahead gate's branch and the click
    has become its own evidence. The invariant check must see it.
    """
    tree = _mutated(
        'if typeahead_gate["proceed"]:\n'
        '                        click_plan.append(typeahead_gate["selector"])',
        'if typeahead_gate["proceed"]:\n'
        "                        fill_plan.append(\n"
        "                            (\n"
        "                                dom.compose_body_selector(),\n"
        "                                _text_component_of(spec, grant.target),\n"
        "                            )\n"
        "                        )",
    )
    assert "typeahead_gate" in _body_fill_guards(tree)


def test_the_argument_check_goes_red_when_the_gate_is_told_what_happened():
    """Hand the recipient gate the typeahead's verdict and it stops being
    independent. The signature check must see the third argument."""
    tree = _mutated(
        "recipient_gate = await _recipient_gate(page, grant)",
        "recipient_gate = await _recipient_gate(page, grant, typeahead_gate)",
    )
    assert _recipient_gate_arguments(tree) == [["page", "grant", "typeahead_gate"]]


def test_the_scope_check_goes_red_when_the_typeahead_gates_a_second_thing():
    """Let the typeahead's verdict queue a fill as well as a click and the
    scope check must report both queues rather than one."""
    tree = _mutated(
        'if typeahead_gate["proceed"]:\n'
        '                        click_plan.append(typeahead_gate["selector"])',
        'if typeahead_gate["proceed"]:\n'
        '                        click_plan.append(typeahead_gate["selector"])\n'
        "                        fill_plan.append((\"x\", \"y\"))",
    )
    appended: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        tested = {
            sub.value.id
            for sub in ast.walk(node.test)
            if isinstance(sub, ast.Subscript) and isinstance(sub.value, ast.Name)
        }
        if "typeahead_gate" not in tested:
            continue
        for stmt in node.body:
            for inner in ast.walk(stmt):
                if (
                    isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr == "append"
                    and isinstance(inner.func.value, ast.Name)
                ):
                    appended.append(inner.func.value.id)
    assert appended == ["click_plan", "fill_plan"], appended


def test_the_body_fill_guard_reader_is_not_satisfied_by_a_comment():
    """THE REASON THIS FILE USES AN AST AT ALL, demonstrated.

    A string-counting version of the invariant goes red on a mention. This one
    does not move, because a comment is not a call.
    """
    import inspect
    import textwrap

    source = textwrap.dedent(inspect.getsource(writes.perform))
    before = _body_fill_guards(ast.parse(source))
    with_comment = source.replace(
        "    click_error: Optional[str] = None",
        "    # see dom.compose_body_selector() for the body's address\n"
        "    click_error: Optional[str] = None",
        1,
    )
    assert with_comment != source
    assert source.count("dom.compose_body_selector()") + 1 == with_comment.count(
        "dom.compose_body_selector()"
    ), "the mention did not land, so this demonstrates nothing"
    assert _body_fill_guards(ast.parse(with_comment)) == before
