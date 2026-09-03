"""THE PROBE MAY TYPE AND IT MAY PRESS ONE ROW. IT MAY NOT SEND.

``scripts/_probe_typeahead_commit.py`` is the first mutating probe in this
repository. The five before it read; this one fills a combobox and clicks a
suggestion, on his live signed-in account, because the question it exists to
answer -- does pressing a typeahead suggestion commit a recipient? -- has no
answer that can be reached by reading.

That makes its boundary a real one rather than a formality, and a boundary
described only in a docstring is section 90's defect: prose claiming a
capability, or in this case an INcapability, that nothing enforces. So the
probe's own module docstring says "this file contains no send click --
asserted below by ``test_the_probe_presses_no_send_control`` rather than
promised here", and this file is what makes that sentence true.

WHAT IS CHECKED, AND WHY EACH ONE IS STRUCTURAL RATHER THAN TEXTUAL
-------------------------------------------------------------------
Every check reads the probe's SYNTAX TREE. A grep for ``compose_send_selector``
would go red on the docstring that promises not to use it, which is the exact
inversion this repository has already paid for once -- a check that fires on a
file for saying it does not do the thing.

    the mutating calls          exactly one fill and one click, counted as
                                CALL SITES, so a second of either has to come
                                and argue with this file
    what the fill is aimed at   the selector ``_live_control`` returned, never
                                ``dom.compose_body_selector()``
    what the click is aimed at  the typeahead gate's own selector, never a
                                send control
    ``perform`` is never called it is the function that continues past the
                                point this probe stops at
    the needle has no default   a default would be a real person's name in a
                                tracked file
    the needle is never printed a terminal, a CI log and an agent transcript
                                are all publication channels

AND EVERY ONE OF THEM IS SHOWN FAILING, against a mutated copy of the source
in which the property is broken. A check that cannot fail certifies nothing,
and a boundary check that cannot fail is worse than none: it manufactures
confidence about the one file in this repo that types on a live account.

NOTHING HERE RUNS THE PROBE. This file reads it. Running it launches a browser
and types into his composer, which is precisely what
``tests/test_scripts_are_import_safe.py`` exists to keep an import from doing.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PROBE = Path(__file__).resolve().parent.parent / "scripts" / "_probe_typeahead_commit.py"


def _tree(source: str | None = None) -> ast.AST:
    return ast.parse(PROBE.read_text(encoding="utf-8") if source is None else source)


def _source() -> str:
    return PROBE.read_text(encoding="utf-8")


def _mutating_calls(tree: ast.AST) -> list[tuple[str, ast.Call]]:
    """Every Playwright call that could change the page, by KIND.

    The kinds are ``readonly._MUTATION_CALL_PATTERNS``' own names, matched on
    the attribute rather than by regex over the text -- so a call split across
    lines, or one wearing a comment, is seen exactly as the interpreter sees
    it.
    """
    kinds = {
        "click",
        "dblclick",
        "fill",
        "type",
        "press",
        "check",
        "uncheck",
        "select_option",
        "set_input_files",
        "drag_to",
        "tap",
        "dispatch_event",
        "submit",
    }
    found: list[tuple[str, ast.Call]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in kinds:
                found.append((node.func.attr, node))
    return found


def _aim_of(call: ast.Call) -> str:
    """A readable description of a mutating call's FIRST argument."""
    return ast.unparse(call.args[0]) if call.args else "<no argument>"


def _called_names(tree: ast.AST) -> set[str]:
    """Every dotted name called anywhere, as text -- ``writes.perform`` etc."""
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            out.add(ast.unparse(node.func))
    return out


def _printed_needle_uses(tree: ast.AST) -> tuple[int, int]:
    """How often ``print`` is handed the needle, and how often wrapped in len().

    Returns ``(references, wrapped)``. The property is that they are EQUAL:
    every mention of the identifier inside a print is inside a ``len(...)``.

    COUNTED ON IDENTIFIERS, NOT ON TEXT, and the first version of this check
    got that wrong -- it searched the unparsed argument for the substring
    "needle" and fired on the line ``"the needle is in the combobox"``, which
    prints no name at all. A word in a sentence and a variable in an
    expression are different things, and only the tree can tell them apart.
    That is the same defect, in miniature, that this file's own preamble
    describes: a check that fires on a file for TALKING about the thing.
    """
    references = 0
    wrapped = 0
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
            continue
        if node.func.id != "print":
            continue
        for arg in node.args:
            for inner in ast.walk(arg):
                if isinstance(inner, ast.Name) and inner.id == "needle":
                    references += 1
                if (
                    isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Name)
                    and inner.func.id == "len"
                    and len(inner.args) == 1
                    and isinstance(inner.args[0], ast.Name)
                    and inner.args[0].id == "needle"
                ):
                    wrapped += 1
    return references, wrapped


# ---------------------------------------------------------------------------
# 1. What it may do to the page, and how many times
# ---------------------------------------------------------------------------


def test_the_probe_makes_exactly_one_fill_and_one_click():
    """TWO MUTATING CALL SITES, counted the way the boundary counts them.

    This is the probe's whole licence stated as a number. A third would be a
    capability nobody argued for, and counting CALL SITES rather than
    executions is the same rule ``readonly.SANCTIONED_MUTATIONS`` uses: what a
    reviewer reads is the number of places, not the number of times.
    """
    kinds = sorted(kind for kind, _ in _mutating_calls(_tree()))
    assert kinds == ["click", "fill"], kinds


def test_the_probe_presses_no_send_control():
    """**THE SENTENCE THE PROBE'S OWN DOCSTRING POINTS AT.**

    Its one click is aimed at the typeahead gate's selector -- the row it
    resolved by name inside the page -- and at nothing else. A send control is
    reached through ``dom.compose_send_selector()`` or by the name
    ``dom.MESSAGE_SEND_NAME``, and neither may be the target of anything here.
    """
    clicks = [call for kind, call in _mutating_calls(_tree()) if kind == "click"]
    assert len(clicks) == 1, clicks
    aim = _aim_of(clicks[0])
    assert aim == "gate['selector']", aim

    # AND NOTHING IN THIS FILE EVEN RESOLVES A SEND CONTROL. Checked on the
    # tree rather than by grep, so the docstring that promises this stays
    # invisible to the check that enforces it.
    called = _called_names(_tree())
    assert "dom.compose_send_selector" not in called, called
    assert not any(
        isinstance(node, ast.Attribute) and node.attr == "MESSAGE_SEND_NAME"
        for node in ast.walk(_tree())
    )


def test_the_probe_types_the_needle_and_never_the_body():
    """Its one fill is aimed at the recipient combobox, never at the body.

    ``_live_control`` returns the recipient selector for this action, and that
    returned value is what the fill uses. The body is addressed through
    ``dom.compose_body_selector()``, which must not appear as a call at all --
    typing a message is the act this probe exists to stop short of.
    """
    fills = [call for kind, call in _mutating_calls(_tree()) if kind == "fill"]
    assert len(fills) == 1, fills
    assert _aim_of(fills[0]) == "selector", _aim_of(fills[0])
    assert ast.unparse(fills[0].args[1]) == "needle"

    assert "dom.compose_body_selector" not in _called_names(_tree())


def test_the_probe_never_calls_perform():
    """``perform`` CONTINUES past the point this probe stops at.

    On a proceeding recipient gate it types his message and presses Send.
    Reaching this measurement through ``perform`` would be reaching it through
    the one function that cannot be asked to stop, which is the whole reason
    the probe re-drives the gates itself.
    """
    called = _called_names(_tree())
    assert "writes.perform" not in called, called
    assert not any(name.endswith(".perform") for name in called), called


# ---------------------------------------------------------------------------
# 2. What it may know, and what it may say
# ---------------------------------------------------------------------------


def test_the_needle_has_no_default_and_the_probe_refuses_without_one():
    """NO DEFAULT, ENFORCED BY THE FUNCTION rather than by anybody remembering.

    A default would be a real person's name in a tracked file, and
    ``tests/test_no_committed_identity.py`` says out loud that its shape checks
    cannot detect one. So the guard has to be behavioural, and this is it.
    """
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location("_probe_typeahead_commit", PROBE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    saved_argv = list(sys.argv)
    try:
        sys.argv = ["_probe_typeahead_commit.py"]
        with pytest.raises(SystemExit) as raised:
            module._needle()
    finally:
        sys.argv = saved_argv
    assert "no needle was given" in str(raised.value)


def test_the_probe_never_prints_the_needle():
    """It reports the needle's LENGTH and its counts. Never the name.

    A terminal scrollback, a CI log and an agent transcript are publication
    channels, and this repository's rule is that a third party's name does not
    enter one in order to explain a measurement. So every occurrence of the
    IDENTIFIER inside a ``print`` must be wrapped in ``len(...)`` -- counted
    on the tree, so the word appearing in a sentence is not mistaken for the
    variable appearing in an expression.
    """
    references, wrapped = _printed_needle_uses(_tree())
    assert references > 0, (
        "no print mentions the needle at all, so this check is asserting "
        "nothing. The probe is supposed to print its LENGTH."
    )
    assert references == wrapped, (references, wrapped)


def test_the_probe_writes_no_file():
    """It captures nothing. A composer holding a committed recipient holds a
    third party, and a capture of one is a file somebody has to remember to
    destroy -- which the messaging probe already learned the hard way."""
    writers = {
        "write_text",
        "write_bytes",
        "open",
        "mkdir",
        "makedirs",
        "screenshot",
        "content",
    }
    offenders = [
        ast.unparse(node.func)
        for node in ast.walk(_tree())
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in writers
    ]
    assert offenders == [], offenders


def test_it_runs_only_when_run():
    """The browser is launched under ``if __name__ == '__main__'`` and nowhere
    else.

    ``tests/test_scripts_are_import_safe.py`` accepts an ATTRIBUTE call at
    module scope, and ``asyncio.run(...)`` is one -- so a probe ending in a
    bare ``asyncio.run(main())`` passes that guard while doing the most
    side-effecting thing in this repo on import. For a reading probe that is a
    hole. For this one an import would type into his composer.
    """
    tree = _tree()
    guarded = [
        node
        for node in tree.body
        if isinstance(node, ast.If) and "__name__" in ast.unparse(node.test)
    ]
    assert len(guarded) == 1, "no __main__ guard"
    top_level = "\n".join(
        ast.unparse(node) for node in tree.body if node not in guarded
    )
    assert "asyncio.run" not in top_level
    assert "asyncio.run" in ast.unparse(guarded[0])


# ---------------------------------------------------------------------------
# 3. The controls. Every check above, shown going red
# ---------------------------------------------------------------------------
#
# THE MUTATIONS ARE APPLIED TO A COPY OF THE TEXT, never to the file. Each is
# the smallest edit that breaks the property while leaving something that still
# parses.


def _mutate(old: str, new: str) -> ast.AST:
    source = _source()
    assert source.count(old) == 1, (
        f"the mutation anchor {old!r} appears {source.count(old)} times. "
        "Repoint it -- a mutation that does not apply is a control that tests "
        "nothing."
    )
    return _tree(source.replace(old, new, 1))


def test_the_send_check_goes_red_on_a_planted_send_click():
    """Plant the click this probe is forbidden to make, and watch it caught."""
    tree = _mutate(
        "await page.click(gate[\"selector\"], timeout=writes.CLICK_TIMEOUT_MS)",
        "await page.click(gate[\"selector\"], timeout=writes.CLICK_TIMEOUT_MS)\n"
        "        await page.click(dom.compose_send_selector())",
    )
    clicks = [call for kind, call in _mutating_calls(tree) if kind == "click"]
    assert len(clicks) == 2
    assert "dom.compose_send_selector" in _called_names(tree)


def test_the_body_check_goes_red_on_a_planted_body_fill():
    """Plant the fill that would put his words on the page."""
    tree = _mutate(
        "await page.fill(selector, needle, timeout=writes.CLICK_TIMEOUT_MS)",
        "await page.fill(selector, needle, timeout=writes.CLICK_TIMEOUT_MS)\n"
        "        await page.fill(dom.compose_body_selector(), UNSENT_BODY)",
    )
    assert "dom.compose_body_selector" in _called_names(tree)
    kinds = sorted(kind for kind, _ in _mutating_calls(tree))
    assert kinds == ["click", "fill", "fill"], kinds


def test_the_perform_check_goes_red_on_a_planted_perform_call():
    """Route the measurement through the function that cannot be asked to
    stop, and the check must see it."""
    tree = _mutate(
        "        gate = await writes._typeahead_gate(page, grant)",
        "        gate = await writes.perform(None, page, grant)",
    )
    assert "writes.perform" in _called_names(tree)


def test_the_print_check_goes_red_on_a_planted_leak():
    """Print the name instead of its length, and the check must see it.

    This is the likeliest accidental leak in the whole file -- a debugging
    line added during a live run and never removed -- so it gets its own
    control rather than riding on the others.
    """
    tree = _mutate(
        'print(f"  needle length            {len(needle)} chars (never printed)")',
        'print(f"  needle {needle}")',
    )
    references, wrapped = _printed_needle_uses(tree)
    assert references > wrapped, (references, wrapped)


def test_the_main_guard_check_goes_red_on_an_unguarded_run():
    """Move the launch to module scope -- which the import-safety guard
    ACCEPTS, because it is an attribute call -- and this must still catch it."""
    source = _source()
    marker = 'if __name__ == "__main__":'
    assert source.count(marker) == 1
    unguarded = source[: source.index(marker)] + "asyncio.run(main())\n"
    tree = _tree(unguarded)
    guarded = [
        node
        for node in tree.body
        if isinstance(node, ast.If) and "__name__" in ast.unparse(node.test)
    ]
    assert guarded == []
    assert "asyncio.run" in "\n".join(ast.unparse(node) for node in tree.body)
