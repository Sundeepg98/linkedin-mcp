"""``known_side_effects`` makes ENUMERATION claims, and nothing checked them.

THE FIELD. ``linkedin_server_info``'s ``known_side_effects`` is the list a
caller reads to decide which tool is safe to call. Its messaging entry does not
merely describe a cost; it makes a CLOSED claim about who can incur it:

    "Only linkedin_open_messaging and linkedin_new_messages can incur this"

**THE NEIGHBOURING BULLET IN THE SAME LIST WAS FALSE FOR TWO DAYS.** It read
"no tool here loads /mynetwork/ at all" while ``linkedin_connections`` had
loaded an address under it since 2026-09-03. It was corrected at ``2f27a83``
on 2026-09-05 at 21:33 -- by the wave that added the SECOND violation, which
is to say it was found because somebody tripped over it, not because anything
was watching.

**SO THE FIX FOR ONE BULLET LEFT THE CLASS OPEN, AND THIS FILE IS THE CLASS.**
An enumeration claim in prose, about code, with no instrument behind it, in the
one field whose whole purpose is to let a caller weigh a cost. Measured
2026-09-05 22:24 by AST over ``server.py``, the messaging bullet is wrong in
BOTH directions at once -- see the two tests below.

WHY BOTH DIRECTIONS. An enumeration claim has two halves and they fail
differently:

    the named set is too SMALL   a caller pays a cost the field said nobody
                                 could charge them.  (the /mynetwork/ failure)
    the named set is too LARGE   a caller avoids a tool that is in fact free.
                                 (the messaging failure, measured here)

The second is the quieter one and it has a real cost: ``linkedin_new_messages``
exists PRECISELY to answer the messaging question without paying for it -- its
own docstring says "This never sends a message, never opens a conversation,
and never loads the messaging surface at all", and it returns
``opened_a_conversation: False``. Naming it beside the expensive tool tells a
caller the cheap route is expensive, so the field steers away from the one tool
built to protect the counter it is warning about.

WHAT THESE TESTS ASSERT, AND IT IS TODAY'S DEFECT RATHER THAN THE FIX. The
sentence lives in ``linkedin_server/server.py``, which was DIRTY with another
wave's uncommitted lines when this was written, and whose ``known_side_effects``
block has a measured owner (``2f27a83``). This repository's standing rule is
that you hand a peer the measurement, not the fix, and you do not sweep a
neighbour's lines. So:

**GREEN HERE MEANS THE DEFECT IS STILL PRESENT AND RECORDED. It is NOT a
certificate that the field is correct.** Repairing the sentence turns these
tests RED, which is the point -- a known defect must not be able to be fixed in
silence, and the record of a defect may not outlive the defect.

THE CONTROL IS NOT DECORATION. Both defect tests are claims of the form "this
tool does NOT navigate to messaging", and the guaranteed failure mode of the
reader underneath them is that it finds NO navigation anywhere -- at which
point both pass for the wrong reason and this file certifies nothing.
:func:`test_the_reader_finds_a_true_positive` is the detector factored out of
the assertions: the same reader, on the same file, must find the tool that
demonstrably DOES navigate to messaging.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SERVER = REPO / "linkedin_server" / "server.py"

#: The address family this bullet is about. A value is in it when the url it
#: resolves to sits under LinkedIn's messaging namespace -- the root AND the
#: composer, deliberately, because the ambiguity between "the root" and "the
#: whole surface" is exactly what let the /mynetwork/ bullet be read as true.
_FAMILY = "/messaging"


def _server_tree() -> ast.Module:
    return ast.parse(SERVER.read_text(encoding="utf-8"))


def _url_constants() -> dict[str, str]:
    """Module-level ``*_URL`` string constants, resolved from config by AST.

    Read rather than imported: importing ``server`` pulls a browser, an MCP
    registration and every reader in the package into a test whose question is
    about four string literals.
    """
    out: dict[str, str] = {}
    config = ast.parse((REPO / "linkedin_server" / "config.py").read_text(encoding="utf-8"))
    base = ""
    for node in config.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        # BASE_URL is a plain literal; the rest are f-strings built off it.
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            out[target.id] = node.value.value
            if target.id == "BASE_URL":
                base = node.value.value
        elif isinstance(node.value, ast.JoinedStr):
            parts = []
            for piece in node.value.values:
                if isinstance(piece, ast.Constant):
                    parts.append(str(piece.value))
                elif isinstance(piece, ast.FormattedValue) and isinstance(
                    piece.value, ast.Name
                ):
                    parts.append(out.get(piece.value.id, base))
            out[target.id] = "".join(parts)
    return out


def _census_surfaces() -> dict[str, str]:
    """``server.CENSUS_SURFACES``, resolved by AST the same way."""
    urls = _url_constants()
    base = urls.get("BASE_URL", "")
    out: dict[str, str] = {}
    for node in ast.walk(_server_tree()):
        if not (isinstance(node, ast.AnnAssign) or isinstance(node, ast.Assign)):
            continue
        targets = [node.target] if isinstance(node, ast.AnnAssign) else node.targets
        names = [t.id for t in targets if isinstance(t, ast.Name)]
        if "CENSUS_SURFACES" not in names or not isinstance(node.value, ast.Dict):
            continue
        for key, value in zip(node.value.keys, node.value.values):
            if not (isinstance(key, ast.Constant) and isinstance(key.value, str)):
                continue
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                out[key.value] = value.value
            elif isinstance(value, ast.Name):
                out[key.value] = urls.get(value.id, "")
            elif isinstance(value, ast.JoinedStr):
                parts = []
                for piece in value.values:
                    if isinstance(piece, ast.Constant):
                        parts.append(str(piece.value))
                    elif isinstance(piece, ast.FormattedValue) and isinstance(
                        piece.value, ast.Name
                    ):
                        parts.append(urls.get(piece.value.id, base))
                out[key.value] = "".join(parts)
    return out


def _navigation_targets_by_tool() -> dict[str, set[str]]:
    """For every ``linkedin_*`` function, the set of urls it navigates to.

    A navigation is ``<anything>.goto(page, <target>)``. The target is resolved
    through the config constants and through ``CENSUS_SURFACES``; anything that
    resolves to nothing is kept as its unparsed source so a reader can see that
    it was seen and not silently dropped -- a refusal must name what it SAW.
    """
    urls = _url_constants()
    surfaces = _census_surfaces()
    out: dict[str, set[str]] = {}

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self._enter(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self._enter(node)

        def _enter(self, node) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def visit_Call(self, node: ast.Call) -> None:
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "goto"
                and len(node.args) >= 2
                and self.stack
            ):
                out.setdefault(self.stack[-1], set()).add(
                    self._resolve(node.args[1])
                )
            self.generic_visit(node)

        @staticmethod
        def _resolve(node: ast.expr) -> str:
            if isinstance(node, ast.Name):
                return urls.get(node.id, node.id)
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                return node.value
            if (
                isinstance(node, ast.Subscript)
                and isinstance(node.value, ast.Name)
                and node.value.id == "CENSUS_SURFACES"
                and isinstance(node.slice, ast.Constant)
            ):
                return surfaces.get(str(node.slice.value), ast.unparse(node))
            return ast.unparse(node)

    Visitor().visit(_server_tree())
    return out


def _messaging_sentence() -> str:
    """The one ``known_side_effects`` entry this file is about."""
    for node in ast.walk(_server_tree()):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if not (
                isinstance(key, ast.Constant) and key.value == "known_side_effects"
            ):
                continue
            if not isinstance(value, ast.List):
                continue
            for element in value.elts:
                try:
                    text = ast.literal_eval(element)
                except Exception:  # noqa: BLE001 - a non-literal is not our entry
                    continue
                if isinstance(text, str) and "clears the messaging badge" in text:
                    return text
    raise AssertionError(
        "the messaging side-effect sentence is gone from known_side_effects. "
        "That is a finding, not a fixture problem: this file exists because "
        "that sentence makes an unchecked enumeration claim."
    )


def _asserted_tools() -> set[str]:
    """The tools the sentence CLAIMS are the only ones that can incur it.

    Taken from the ``Only ... can incur this`` clause and NOT from every
    ``linkedin_*`` token in the sentence, because the sentence also names
    ``linkedin_send_message`` in order to say it does NOT open messaging.
    Reading the whole sentence would count a denial as a claim -- which is the
    same class of error as the defect being measured.
    """
    text = _messaging_sentence()
    match = re.search(r"Only (.+?) can incur this", text, re.S)
    assert match, (
        "the sentence no longer carries an 'Only ... can incur this' clause. "
        "Re-read it before trusting anything else in this file."
    )
    return set(re.findall(r"linkedin_[a-z_]+", match.group(1)))


def _tools_that_navigate_to_messaging() -> set[str]:
    return {
        tool: None
        for tool, targets in _navigation_targets_by_tool().items()
        if tool.startswith("linkedin_")
        and any(_FAMILY in target for target in targets)
    }.keys() | set()


# ---------------------------------------------------------------------------
# THE CONTROL. Run it first: it is what makes the two zeros below mean
# anything at all.
# ---------------------------------------------------------------------------


def test_the_reader_finds_a_true_positive() -> None:
    """The reader must find the tool that demonstrably DOES load messaging.

    Both assertions in this file are of the form "this tool does not navigate
    to messaging". A reader that finds no navigation ANYWHERE satisfies both
    and certifies nothing -- the guaranteed failure mode of a guessed AST
    walk. This is the detector factored out of the assertion.
    """
    navigating = _tools_that_navigate_to_messaging()
    assert navigating, (
        "the navigation reader found NO tool loading a messaging address. "
        "That is a dead reader, not a finding about the server -- every "
        "other assertion in this file is void until it fires."
    )
    assert "linkedin_open_messaging" in navigating, (
        "linkedin_open_messaging is the tool this whole bullet is about and "
        "the reader cannot see its navigation. Fix the reader before reading "
        "anything else here."
    )
    assert _asserted_tools(), (
        "the 'Only ... can incur this' clause parsed to an EMPTY tool set, so "
        "the set comparisons below would trivially hold. Dead extractor."
    )


# ---------------------------------------------------------------------------
# THE DEFECT, IN BOTH DIRECTIONS. Green means present-and-recorded.
# ---------------------------------------------------------------------------


def test_the_sentence_names_a_tool_that_cannot_incur_the_cost() -> None:
    """TOO LARGE: a named tool navigates only to the feed.

    ``linkedin_new_messages`` is named in the ``Only ... can incur this``
    clause. Its only navigation is ``FEED_URL``, and it returns
    ``opened_a_conversation: False`` -- it reads the badge off a page the
    server already loads and stops. It cannot open a conversation and cannot
    clear the messaging badge, so a caller reading this field is steered away
    from the one tool built to answer the messaging question for free.

    WHEN THIS GOES RED: the sentence was repaired. Delete this test and keep
    the direction below, or replace both with the positive invariant.
    """
    asserted = _asserted_tools()
    navigating = _tools_that_navigate_to_messaging()

    assert "linkedin_new_messages" in asserted, (
        "the sentence no longer names linkedin_new_messages -- if it was "
        "removed, this defect is fixed and this test should go."
    )
    named_but_cannot = asserted - navigating
    assert named_but_cannot == {"linkedin_new_messages"}, (
        "the set of tools NAMED as able to incur the messaging cost but "
        "navigating nowhere near messaging has changed. measured 2026-09-05: "
        "exactly {'linkedin_new_messages'}. now: %r" % (sorted(named_but_cannot),)
    )


def test_a_tool_loads_a_messaging_address_and_the_sentence_does_not_name_it() -> None:
    """TOO SMALL: the same failure as the /mynetwork/ bullet, unfixed here.

    ``linkedin_compose_fields`` navigates to
    ``CENSUS_SURFACES['messaging_compose']``, which is
    ``<base>/messaging/compose/`` -- a messaging address. The sentence does not
    name it.

    **THIS IS NOT A CLAIM THAT IT COSTS WHAT THE ROOT COSTS.** The composer was
    measured on 2026-09-01 with the badge at 0 either side and no redirect, and
    ``dom`` records that. The defect is the SCOPE of the word "messaging" in a
    closed claim: read as the root the sentence is defensible, read as the
    surface it is false -- and that exact ambiguity is what let the /mynetwork/
    bullet stand wrong for two days, its own correction says so.

    **I FIRST WROTE THIS EXPECTING TWO TOOLS AND THE READER REFUTED ME.** See
    the test below: the second candidate navigates to a caller-chosen key, and
    that is a different and larger finding than the one I was asserting.

    WHEN THIS GOES RED: somebody scoped the claim. Read the new wording.
    """
    asserted = _asserted_tools()
    navigating = _tools_that_navigate_to_messaging()

    unnamed = navigating - asserted
    assert unnamed == {"linkedin_compose_fields"}, (
        "the set of tools that navigate to a STATICALLY RESOLVABLE messaging "
        "address WITHOUT being named in the sentence has changed. measured "
        "2026-09-05: exactly {'linkedin_compose_fields'}. now: %r"
        % (sorted(unnamed),)
    )


def test_a_closed_claim_cannot_be_checked_while_a_parameterised_navigator_exists() -> None:
    """THE THIRD SHAPE, and it is why the field's FORM is wrong, not its text.

    ``linkedin_surface_census`` navigates to ``CENSUS_SURFACES[key]`` where
    ``key`` is a CALLER'S ARGUMENT, and ``messaging_compose`` is one of the
    keys it accepts. So it can load a messaging address, and **no static
    reader can attribute that to it** -- the destination does not exist until
    a caller picks one.

    That is not a bug in the reader above; it is the reason a sentence of the
    form *"only tools X and Y can incur this"* is UNVERIFIABLE in this package
    as it currently stands. A closed enumeration cannot be checked against an
    open navigator. Either the claim is scoped to statically-addressed tools
    and says so, or the parameterised tool is named as able to reach the
    family, or the field stops making closed claims.

    **This is the finding the two tests above cannot state**, and it is worth
    more than either of them: the /mynetwork/ correction repaired one
    sentence's TEXT, and the field's FORM is what keeps producing these.
    """
    tree = _server_tree()
    surfaces = _census_surfaces()
    assert "messaging_compose" in surfaces

    parameterised: set[str] = set()

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self._enter(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self._enter(node)

        def _enter(self, node) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def visit_Call(self, node: ast.Call) -> None:
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "goto"
                and len(node.args) >= 2
                and self.stack
                and self.stack[-1].startswith("linkedin_")
            ):
                target = node.args[1]
                # A subscript of CENSUS_SURFACES whose key is NOT a literal.
                if (
                    isinstance(target, ast.Subscript)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "CENSUS_SURFACES"
                    and not isinstance(target.slice, ast.Constant)
                ):
                    parameterised.add(self.stack[-1])
            self.generic_visit(node)

    Visitor().visit(tree)

    assert parameterised == {"linkedin_surface_census"}, (
        "the set of tools navigating to a CALLER-CHOSEN census surface has "
        "changed. measured 2026-09-05: exactly {'linkedin_surface_census'}. "
        "now: %r -- every closed claim in known_side_effects is unverifiable "
        "against each of these." % (sorted(parameterised),)
    )
    assert not (parameterised & _asserted_tools()), (
        "a parameterised navigator is now named in the closed clause. That "
        "may be the right repair; read the wording before deleting this."
    )


def test_the_composer_address_really_is_under_the_messaging_family() -> None:
    """The premise the test above rests on, asserted rather than assumed."""
    surfaces = _census_surfaces()
    assert "messaging_compose" in surfaces, (
        "CENSUS_SURFACES no longer carries messaging_compose; the resolver "
        "above is reading a dict that has moved."
    )
    assert _FAMILY in surfaces["messaging_compose"], (
        "messaging_compose no longer resolves under %r, so the classification "
        "in this file is measuring something else." % (_FAMILY,)
    )


# ---------------------------------------------------------------------------
# THE SECOND SITE. The same closed claim lives in README.md, and a README is
# the class this repository's correction machinery cannot bind.
# ---------------------------------------------------------------------------

README = REPO / "README.md"


def _readme_asserted_tools() -> set[str]:
    """The same ``Only ... can incur this`` clause, out of the README."""
    text = README.read_text(encoding="utf-8")
    match = re.search(r"Only (.{0,400}?) can incur\s+this", text, re.S)
    assert match, (
        "README.md no longer carries an 'Only ... can incur this' clause. If "
        "it was rewritten, read the new wording -- this file asserts that the "
        "README and server.py say the SAME thing, and it cannot check a "
        "sentence that is gone."
    )
    return set(re.findall(r"linkedin_[a-z_]+", match.group(1)))


def test_the_readme_repeats_the_claim_and_the_two_copies_must_not_diverge() -> None:
    """TWO COPIES OF ONE CLOSED CLAIM, and this is the divergence detector.

    ``README.md`` restates the messaging cost bullet including its ``Only ...
    can incur this`` clause, with the same two tool names. So the defect
    measured in this file exists TWICE, and **a repair applied to one copy
    leaves the other standing and wrong.**

    A README is worse than the field it copies: an audit document is a dated
    record and rots fairly harmlessly, but a README is a STANDING INSTRUCTION
    read as current truth by whoever opens the repository next, and it carries
    no ``CORRECTED BY:`` mechanism at all. This repository has already measured
    a false premise propagating through a workflow comment rather than through
    an audit doc, for exactly this reason.

    **WHAT THIS TEST IS FOR IS THE DIVERGENCE, NOT THE AGREEMENT.** Today the
    two copies agree -- both wrong, identically. It fires the moment they stop
    agreeing, which is precisely what a one-sided fix looks like.
    """
    assert _readme_asserted_tools() == _asserted_tools(), (
        "README.md and server.py's known_side_effects now name DIFFERENT tool "
        "sets in their 'Only ... can incur this' clauses.\n"
        "  README:    %r\n"
        "  server.py: %r\n"
        "If you are repairing this claim, repair BOTH copies. If you are "
        "deliberately splitting them, say so and delete this test."
        % (sorted(_readme_asserted_tools()), sorted(_asserted_tools()))
    )


def test_the_readme_contradicts_itself_four_lines_later() -> None:
    """THE CORRECTION WAS ALREADY IN THE DOCUMENT, and nobody joined them.

    The README's messaging bullet says only two named tools can incur the
    messaging cost. **The very next bullet says "the message composer is on the
    surface point 3 describes"** -- which is `linkedin_compose_fields`'
    destination, and point 3 does not name it.

    So the README states the premise and its own counterexample within a few
    lines of each other, and the closed claim survived anyway. That is this
    repository's most-repeated shape: two accurate statements, no reader
    joining them, and the join is where the finding lives.

    **This is not a second defect. It is evidence about how cheap the fix
    was** -- nobody needed a browser, an AST walk or a live load to catch it;
    they needed to read two adjacent bullets as one claim.
    """
    text = README.read_text(encoding="utf-8")
    assert re.search(r"message composer is on the surface", text), (
        "the README no longer says the message composer sits on the messaging "
        "surface. If that bullet was rewritten, re-read both bullets together "
        "before trusting either."
    )
    assert "linkedin_compose_fields" not in _readme_asserted_tools(), (
        "the README's closed clause now names linkedin_compose_fields, so the "
        "contradiction is resolved. Delete this test and say so."
    )


@pytest.mark.parametrize("tool", ["linkedin_new_messages", "linkedin_open_messaging"])
def test_both_named_tools_exist_at_all(tool: str) -> None:
    """A sentence naming a tool that does not exist is a third failure mode.

    Cheap, and it closes the case where a rename makes every set comparison
    above vacuously true.
    """
    names = {
        node.name
        for node in ast.walk(_server_tree())
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert tool in names, (
        "known_side_effects names %r and server.py defines no such function." % tool
    )
