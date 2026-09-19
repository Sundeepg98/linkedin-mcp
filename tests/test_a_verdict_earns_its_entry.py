"""A VERDICT FUNCTION IS A DIFFERENT CLAIM, AND THIS IS ITS PROOF.

Built 2026-09-19 from the brief at
``_audit/2026-09-19-the-sanitiser-list-holds-two-kinds.md``, which was filed
rather than built because it was written against a closing deadline.

``tests/test_a_sanitiser_earns_its_entry.py`` certifies SHAPERS::

    input -> a SHAPED OUTPUT derived from it
    SAFE IFF no input survives AND IT DISCRIMINATES

This file certifies the other kind::

    input -> ONE OF A CLOSED, ENUMERATED SET
    SAFE IFF no input survives AND THE ALPHABET IS CLOSED

**AND THE SHAPER TEST IS NOT MERELY WRONG FOR THIS KIND -- IT IS INVERTED.**
The more a verdict varies with its input, the more it tells you about that
input. For a verdict function, many inputs mapping to ONE value is the
property you want, and ``MUST_DISCRIMINATE`` scores that property as a defect.
A verdict function that discriminated per-input would be leaking, and the
shaper table would pass it. **So there is no discrimination requirement here,
deliberately** -- see :func:`test_this_file_has_no_discrimination_requirement`,
which asserts the absence rather than leaving it to be noticed.

## The needle half is STRONGER here, not weaker

A shaper may DERIVE -- it is allowed to compute something from its input, and
the shaper table checks that the input's identity does not survive that
computation. A verdict may not derive at all. Every ``return`` must be a
CONSTANT proven off the AST: no f-string, no concatenation, no ``%``, no
``.format``, no name. A constant cannot carry an input, so the needle question
is answered by structure rather than by sampling.

That is the whole reason this proof is worth having: the shaper table can only
report on the inputs somebody thought to put in it. This one closes over every
input there will ever be.

## WHAT AN ENTRY COSTS, and it is the same discipline as the other list

``(filename, function name) -> (arity, alphabet)``. **A claim made by the
function's author and by nobody else.** The shaper file's rule has now caught
the same event four times (``_shape_of`` -> ``_redact`` -> ``_relation`` ->
``_why_refused``) and is not relaxed for this list.

**THIS TABLE SHIPS EMPTY OF REAL ROWS, AND THAT IS THE HONEST STATE.** The
three functions this file was built for are not this wave's to enrol:

    _why_refused      scripts/_probe_landed_address_sweep.py      owner 1f244e1
    _landing_class    scripts/_probe_creator_content_analytics.py
    is_read_url       linkedin_server/readonly.py

All three were MEASURED against this file's own proof functions at build time
and the measurement is recorded in
``_audit/2026-09-19-verdict-certifier.md``. A measurement is not an enrolment.
Enrolment ASSERTS a contract is safe; this wave did not write any of the three
and vouching for a function it did not write is the ``_redact`` mistake the
sibling file exists to stop.

**An empty table would make every parametrized test here vacuous**, which is
the exact hazard this package has a standing rule about. So the arms are
exercised by CONTROLS over fixtures authored in this file -- each proof
function is shown REJECTING before any of them is trusted to accept. See the
``test_the_proof_would_catch_*`` tests below; none of them passes if its proof
function is replaced by ``return []``.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tests.test_navigation_is_never_derived import _SANITISERS  # noqa: E402

ONE_ARG = "one_arg"
TWO_ARG = "two_arg"

#: **A DELIBERATE WIDENING OF THE BRIEF'S RULE 1, ARGUED RATHER THAN QUIET.**
#:
#: The brief says "every ``return`` in the function is a STRING constant".
#: Taken literally that makes the brief's own clearest instance --
#: ``is_read_url``, which returns ``True``/``False`` -- permanently
#: unrepresentable, and a certifier that cannot admit the case that motivated
#: it is self-refuting.
#:
#: **WIDENING FROM "STRING CONSTANT" TO "CONSTANT OF A DECLARED TYPE" IS NOT A
#: LOOSENING.** The property being proved is that NO INPUT SURVIVES, and it is
#: carried entirely by the node being ``ast.Constant``: an ``ast.Constant``
#: admits no interpolation, no concatenation, no name and no call, whatever
#: its value's type. A two-member boolean alphabet is a STRICTLY TIGHTER
#: closed set than any string alphabet, not a looser one.
#:
#: The types are enumerated rather than left open because ``ast.Constant``
#: also covers things whose closure is not obvious by inspection, and an
#: entry declares which one it means.
ALLOWED_VERDICT_TYPES = (str, bool, type(None))

#: **THE ENROLMENT.** ``(filename, function name) -> (arity, alphabet)``.
#:
#: The alphabet is the DECLARED closed set. It is compared against the set
#: measured off the AST, so the entry goes RED if the function gains or loses
#: a member -- which is the whole point of enumerating it rather than counting
#: it. A count would survive a rename of one verdict into another.
VERDICTS: dict[tuple[str, str], tuple[str, frozenset]] = {
    # EMPTY OF REAL ROWS ON PURPOSE -- see this module's docstring. The three
    # known candidates are measured in the audit file and left for their
    # owners to claim. Do not add a row here for a function you did not write.
}

#: Where a claimant may live. ``is_read_url`` is in the package rather than in
#: ``scripts/``, so a loader hard-coded to ``scripts/`` would have made the
#: brief's third instance unrepresentable for a second reason.
SEARCH_DIRS = ("scripts", "linkedin_server")

_MODULES: dict[str, object] = {}


def _path_of(filename: str) -> pathlib.Path:
    for directory in SEARCH_DIRS:
        candidate = REPO / directory / filename
        if candidate.exists():
            return candidate
    raise AssertionError(
        "%s is enrolled and is in none of %s" % (filename, list(SEARCH_DIRS))
    )


def _module(filename: str):
    if filename not in _MODULES:
        path = _path_of(filename)
        spec = importlib.util.spec_from_file_location(path.stem, path)
        assert spec and spec.loader, filename
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _MODULES[filename] = module
    return _MODULES[filename]


def _function_node(tree: ast.AST, function_name: str):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == function_name:
                return node
    return None


def _returns_of(node) -> list[ast.Return]:
    """Every ``return`` OWNED BY THIS FUNCTION, nested ones excluded.

    ``ast.walk`` from a function descends into functions defined INSIDE it, and
    a closure's returns are not this function's alphabet. Getting that wrong
    would fail an honest verdict function because of a helper it happens to
    define, which is the kind of false red that gets a certifier disabled.
    """
    nested = {
        id(inner)
        for child in ast.walk(node)
        if child is not node
        and isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda))
        for inner in ast.walk(child)
    }
    return [
        child
        for child in ast.walk(node)
        if isinstance(child, ast.Return) and id(child) not in nested
    ]


def non_constant_returns(source: str, function_name: str) -> list[str]:
    """**PROOF 1.** The returns that are NOT a bare constant, as source text.

    A FUNCTION rather than an inline expression, so the controls below can
    hand it code it must reject. A predicate only ever run on code that passes
    has never been shown to reject anything.

    A bare ``return`` with no value counts as an offender: ``None`` by
    omission is a verdict nobody wrote down, and the alphabet would silently
    gain a member that reads as an accident.
    """
    tree = ast.parse(source)
    node = _function_node(tree, function_name)
    assert node is not None, "no function named %s in this source" % function_name
    offenders: list[str] = []
    for ret in _returns_of(node):
        if ret.value is None:
            offenders.append("bare `return` (an undeclared None)")
        elif not isinstance(ret.value, ast.Constant):
            offenders.append(ast.dump(ret.value)[:160])
        elif not isinstance(ret.value.value, ALLOWED_VERDICT_TYPES):
            offenders.append(
                "constant of type %s" % type(ret.value.value).__name__
            )
    return offenders


def _always_exits(statements) -> bool:
    """Does this statement list always leave via ``return`` or ``raise``?

    Conservative and deliberately small: it models the last statement being a
    return, a raise, or an if/else whose every branch always exits. Anything
    else is reported as "may fall through", which can be a FALSE positive on a
    shape this does not model -- and the repair for that is one explicit
    ``return`` at the end, which costs a line and makes the alphabet legible.
    A conservative check that asks for a line is the right trade here; the
    other direction would silently under-declare an alphabet.
    """
    if not statements:
        return False
    last = statements[-1]
    if isinstance(last, (ast.Return, ast.Raise)):
        return True
    if isinstance(last, ast.If) and last.orelse:
        return _always_exits(last.body) and _always_exits(last.orelse)
    return False


def falls_off_the_end(source: str, function_name: str) -> bool:
    """**PROOF 1b.** Can this function return an IMPLICIT ``None``?

    THE GAP THIS CLOSES, and it is invisible to the other two proofs. A
    function whose last branch simply falls through returns ``None`` at
    runtime while the AST shows only the returns that were written::

        def v(u):
            if u:
                return "yes"
            # falls through -- returns None, and nothing above sees it

    :func:`measured_alphabet` reports ``{"yes"}``, the entry declares
    ``{"yes"}``, and the two agree -- **so the alphabet claim is false and
    every check passes.**

    **THIS IS A COMPLETENESS DEFECT, NOT A LEAK**, and the distinction is
    worth keeping straight: an implicit ``None`` cannot carry an input, so the
    needle half still holds. What breaks is the entry's promise to enumerate
    what the function can return, which is what a downstream print is trusted
    against.
    """
    tree = ast.parse(source)
    node = _function_node(tree, function_name)
    assert node is not None, "no function named %s in this source" % function_name
    return not _always_exits(node.body)


def measured_alphabet(source: str, function_name: str) -> frozenset:
    """**PROOF 2.** The set of constant values returned, off the AST.

    Only meaningful once :func:`non_constant_returns` is empty; it ignores
    non-constant returns rather than guessing at them, so the two proofs are
    ordered and the ordering is asserted by the tests below.
    """
    tree = ast.parse(source)
    node = _function_node(tree, function_name)
    assert node is not None, "no function named %s in this source" % function_name
    return frozenset(
        ret.value.value
        for ret in _returns_of(node)
        if ret.value is not None
        and isinstance(ret.value, ast.Constant)
        and isinstance(ret.value.value, ALLOWED_VERDICT_TYPES)
    )


def members_spoken(function, arity: str, corpus) -> frozenset:
    """**PROOF 3.** Which alphabet members the function is SHOWN returning.

    Without this the other two proofs are satisfied in full by ``return "x"``:
    one constant, one closed alphabet, nothing ever measured. This is the
    control that proves the function can speak, and the requirement is TWO
    DIFFERENT members -- one would be satisfied by the constant function.
    """
    spoken = set()
    for value in corpus:
        spoken.add(function(value) if arity == ONE_ARG else function(value, value))
    return frozenset(spoken)


#: Inputs the corpus offers a verdict function so it can be shown speaking.
#: Every value is this repository's own invention or a shape-valid synthetic;
#: none is read off a page. A verdict function is entitled to be handed
#: anything, so the corpus is deliberately ragged.
CORPUS = [
    "",
    "https://www.linkedin.com/feed/",
    "https://www.linkedin.com/login",
    "https://www.linkedin.com/in/some-real-slug-99/details/skills/",
    "https://www.linkedin.com/analytics/creator/content/",
    "not a url at all",
]


@pytest.mark.parametrize("claimant", sorted(VERDICTS), ids=lambda c: "%s::%s" % c)
def test_every_verdict_return_is_a_constant(claimant):
    """THE NEEDLE HALF, and it is answered by structure rather than sampling."""
    filename, function_name = claimant
    offenders = non_constant_returns(
        _path_of(filename).read_text(encoding="utf-8"), function_name
    )
    assert not offenders, (
        "%s::%s has %d return(s) that are not a bare constant: %s. A verdict "
        "function may not DERIVE -- that is what separates it from a shaper. "
        "An interpolated return re-opens the alphabet and can carry its input."
        % (filename, function_name, len(offenders), offenders)
    )


@pytest.mark.parametrize("claimant", sorted(VERDICTS), ids=lambda c: "%s::%s" % c)
def test_no_verdict_can_fall_off_its_own_end(claimant):
    """THE COMPLETENESS HALF. An implicit ``None`` is a member nobody declared."""
    filename, function_name = claimant
    assert not falls_off_the_end(
        _path_of(filename).read_text(encoding="utf-8"), function_name
    ), (
        "%s::%s can reach the end of its body without returning, so it can "
        "return an implicit None that its declared alphabet does not list. "
        "End it with an explicit return -- that is one line, and it makes the "
        "alphabet the entry claims the alphabet the function has."
        % (filename, function_name)
    )


@pytest.mark.parametrize("claimant", sorted(VERDICTS), ids=lambda c: "%s::%s" % c)
def test_every_verdict_alphabet_is_the_declared_one(claimant):
    """RED IF THE FUNCTION GAINS OR LOSES A MEMBER.

    The alphabet is ENUMERATED in the entry rather than counted, so renaming
    one verdict into another is caught too.
    """
    filename, function_name = claimant
    _arity, declared = VERDICTS[claimant]
    measured = measured_alphabet(
        _path_of(filename).read_text(encoding="utf-8"), function_name
    )
    assert measured == declared, (
        "%s::%s no longer returns the alphabet its entry declares. "
        "gained=%s lost=%s. The entry is the claim; edit the entry "
        "deliberately or restore the function."
        % (filename, function_name,
           sorted(measured - declared, key=repr),
           sorted(declared - measured, key=repr))
    )


@pytest.mark.parametrize("claimant", sorted(VERDICTS), ids=lambda c: "%s::%s" % c)
def test_every_verdict_is_shown_returning_two_different_members(claimant):
    """THE CONTROL PROVING IT CAN SPEAK. Without it ``return "x"`` passes."""
    filename, function_name = claimant
    arity, _declared = VERDICTS[claimant]
    function = getattr(_module(filename), function_name)
    spoken = members_spoken(function, arity, CORPUS)
    assert len(spoken) >= 2, (
        "%s::%s returned %s for every input in the corpus, so nothing here "
        "has measured that it reports anything. One constant satisfies both "
        "AST proofs completely."
        % (filename, function_name, sorted(spoken, key=repr))
    )


def test_no_name_is_on_both_lists():
    """ONE NAME, ONE TRUST DECISION.

    The taint guard matches ``func.id in _SANITISERS`` -- by NAME, corpus-wide.
    A name appearing on both lists would mean two different contracts claiming
    one spelling, and the guard cannot tell which one it is looking at. That is
    the three-namesake recurrence with the lists as the new disguise.
    """
    overlap = {name for _f, name in VERDICTS} & set(_SANITISERS)
    assert not overlap, (
        "these names are claimed as both a shaper and a verdict: %s. The guard "
        "trusts a spelling, so one spelling may carry only one contract."
        % sorted(overlap)
    )


def test_this_file_has_no_discrimination_requirement():
    """**THE ABSENCE IS ASSERTED, NOT LEFT TO BE NOTICED.**

    Applying the shaper table's ``MUST_DISCRIMINATE`` to a verdict function is
    not merely wrong -- SATISFYING IT WOULD MAKE THE FUNCTION LEAK, because the
    more a verdict varies with its input the more it reveals about that input.
    A future tidier reading the two files side by side will see one arm the
    sibling has and this one does not, and the obvious repair is to add it.
    This test is the note that says the gap is the design.
    """
    source = pathlib.Path(__file__).read_text(encoding="utf-8")
    # THE NEEDLE IS BUILT RATHER THAN WRITTEN, and the first run is why: spelt
    # literally, the assertion's own text is the match and this test failed on
    # the file it was checking. A self-scanning check has to not be its own
    # evidence.
    needle = "MUST_" + "DISCRIMINATE = ["
    assert needle not in source, (
        "a discrimination table has been added to the VERDICT certifier. For a "
        "verdict function, many inputs mapping to one value is the PROPERTY, "
        "not the defect. Read the brief before restoring this."
    )


# ---------------------------------------------------------------------------
# THE CONTROLS. An instrument enters only if it has been shown FAILING, and
# with an empty enrolment table these are the ONLY things running -- so they
# carry the whole claim that the three proofs above can reject anything.
# ---------------------------------------------------------------------------

#: Fixtures written to be caught, one per way a verdict can stop being closed.
#: Kept as SOURCE TEXT rather than as real functions because the proof runs on
#: the AST: a fixture that only existed at runtime would exercise none of it.
LEAKY_FIXTURES = [
    (
        "an f-string return",
        'def v(u):\n    return f"landed on {u}"\n',
    ),
    (
        "a percent interpolation",
        'def v(u):\n    return "FORBIDDEN SUBSTRING %r" % u\n',
    ),
    (
        "a .format call",
        'def v(u):\n    return "class {}".format(u)\n',
    ),
    (
        "a concatenation",
        'def v(u):\n    return "class " + u\n',
    ),
    (
        "the input returned by name",
        "def v(u):\n    return u\n",
    ),
    (
        "a bare return, an undeclared None",
        'def v(u):\n    if u:\n        return "yes"\n    return\n',
    ),
]


@pytest.mark.parametrize(
    "why, source", LEAKY_FIXTURES, ids=[w for w, _s in LEAKY_FIXTURES]
)
def test_the_proof_would_catch_a_derived_return(why, source):
    """CONTROL 1. Each way a return can carry its input, shown rejected."""
    offenders = non_constant_returns(source, "v")
    assert offenders, (
        "non_constant_returns accepted %s, so it is not proving that a verdict "
        "cannot derive. Every green above it is vacuous." % why
    )


def test_the_proof_accepts_a_genuinely_closed_verdict():
    """CONTROL 2. THE OTHER DIRECTION, or the proof could be ``return ['no']``.

    A check that rejects everything is as useless as one that rejects nothing,
    and it fails in the direction that looks like diligence.
    """
    source = (
        "def v(u):\n"
        '    if "/login" in u:\n        return "AUTH-WALL"\n'
        '    return "ELSEWHERE"\n'
    )
    assert non_constant_returns(source, "v") == []
    assert measured_alphabet(source, "v") == frozenset({"AUTH-WALL", "ELSEWHERE"})


def test_the_proof_accepts_a_boolean_alphabet():
    """CONTROL 3. The brief's third instance, in miniature.

    ``is_read_url`` returns ``True``/``False``. If this fails, the widening
    argued at :data:`ALLOWED_VERDICT_TYPES` has been reverted and the clearest
    of the three motivating sites is unrepresentable again.
    """
    source = (
        "def v(u):\n"
        "    if u:\n        return False\n"
        "    return True\n"
    )
    assert non_constant_returns(source, "v") == []
    assert measured_alphabet(source, "v") == frozenset({True, False})


def test_the_alphabet_proof_would_catch_a_gained_member():
    """CONTROL 4. The declared set going stale, which is the silent failure.

    A function that gains a verdict has widened what a downstream print may
    publish, and nothing else in this package would notice.
    """
    before = 'def v(u):\n    return "a"\n'
    after = 'def v(u):\n    if u:\n        return "b"\n    return "a"\n'
    declared = measured_alphabet(before, "v")
    assert measured_alphabet(after, "v") != declared, (
        "measured_alphabet reported the same set before and after a member was "
        "added, so the RED-on-change claim is false."
    )


def test_the_speaking_control_would_catch_a_constant_verdict():
    """CONTROL 5. ``return "x"`` satisfies both AST proofs completely.

    This is the arm the brief names explicitly: without it, the tightest
    possible closed alphabet is a function that has never been shown measuring
    anything at all.
    """
    def mute(_u):
        return "x"

    def speaking(u):
        return "AUTH-WALL" if "/login" in u else "ELSEWHERE"

    assert len(members_spoken(mute, ONE_ARG, CORPUS)) == 1, (
        "the speaking control thinks a constant function speaks, so it would "
        "certify a verdict that never measures its input."
    )
    assert len(members_spoken(speaking, ONE_ARG, CORPUS)) >= 2, (
        "the speaking control cannot see a function that DOES speak, so it "
        "rejects everything and certifies nothing."
    )


def test_the_fallthrough_proof_would_catch_an_undeclared_none():
    """**CONTROL 8. The gap the other two proofs cannot see.**

    The fixture below satisfies proof 1 (its one written return is a constant)
    AND proof 2 (its measured alphabet matches a declaration of ``{"yes"}``)
    while returning ``None`` at runtime. Both directions are asserted, so this
    control also fails if :func:`falls_off_the_end` simply says yes to
    everything.
    """
    leaky = 'def v(u):\n    if u:\n        return "yes"\n'
    closed = 'def v(u):\n    if u:\n        return "yes"\n    return "no"\n'
    both_branches = (
        "def v(u):\n"
        '    if u:\n        return "yes"\n'
        '    else:\n        return "no"\n'
    )

    # The fixture passes BOTH other proofs -- which is the whole point.
    assert non_constant_returns(leaky, "v") == []
    assert measured_alphabet(leaky, "v") == frozenset({"yes"})

    assert falls_off_the_end(leaky, "v"), (
        "a function that can reach the end of its body without returning was "
        "reported as closed. Its entry would declare an alphabet it does not "
        "have, and neither of the other proofs can see it."
    )
    assert not falls_off_the_end(closed, "v"), (
        "falls_off_the_end flagged a function ending in an explicit return, "
        "so it rejects everything and certifies nothing."
    )
    assert not falls_off_the_end(both_branches, "v"), (
        "falls_off_the_end flagged an if/else whose every branch returns. "
        "That is a false red, and a false red is how a check gets deleted."
    )


def test_the_shaper_table_rewards_the_hazard_on_a_verdict_function():
    """**CONTROL 7. THE INVERSION, MEASURED RATHER THAN ARGUED.**

    This is the brief's central claim and it shipped as prose. Prose is what
    a future tidier overrules. So it is run here against the SIBLING'S REAL
    TABLE -- imported, never copied, because a copy would drift and the
    measurement would quietly stop being about the table it names.

    Two functions, both verdict-shaped, through ``MUST_DISCRIMINATE``:

    * ``honest`` returns one closed verdict for every address in the pair.
      That is the PROPERTY a verdict function is supposed to have.
    * ``leaky`` returns a different string per input, carrying the input
      into its output. That is a LEAK.

    **The shaper table FAILS the honest one and PASSES the leaky one.** Not
    "is a poor fit for" -- scores them backwards. That is why widening the
    shaper table was never a loosening, and why nobody may just add an arm.
    """
    from tests.test_a_sanitiser_earns_its_entry import (  # noqa: E402
        MUST_DISCRIMINATE,
    )

    def honest(url, _requested=None):
        return "AUTH-WALL" if "/login" in url else "ELSEWHERE"

    def leaky(url, _requested=None):
        return "landed on " + url

    honest_separated = [
        why for left, right, why in MUST_DISCRIMINATE
        if honest(left) != honest(right)
    ]
    leaky_separated = [
        why for left, right, why in MUST_DISCRIMINATE
        if leaky(left) != leaky(right)
    ]

    assert not honest_separated, (
        "the shaper's discrimination table SEPARATED an honest closed verdict "
        "(%s), so this control is no longer demonstrating the inversion -- "
        "either the table changed or the fixture stopped being verdict-shaped."
        % honest_separated
    )
    assert leaky_separated, (
        "the shaper's discrimination table did NOT separate a function that "
        "concatenates its input into its output. If that is true the "
        "inversion argument is unsupported and this file's premise needs "
        "re-measuring before anything else here is trusted."
    )
    # AND THE NEEDLE HALF IS WHAT CATCHES THE LEAKY ONE, which is the other
    # half of the argument: the shaper table is not blind, it is MIS-AIMED.
    # Its discrimination arm rewards the leak; its needle arm still refuses
    # it. A verdict function needs the refusing half and not the rewarding
    # one, and the two are welded together in the sibling.
    assert non_constant_returns(
        'def leaky(u):\n    return "landed on " + u\n', "leaky"
    ), "proof 1 failed to reject the leaky fixture this control depends on"


def test_the_enrolment_table_is_empty_by_design():
    """**THE PIN.** Three skips above are a state, not an oversight.

    With :data:`VERDICTS` empty the three parametrized arms SKIP on an empty
    parameter set, and a reader scanning output sees three skips that look
    like something went wrong. This test is what makes the emptiness legible,
    and it makes the first enrolment a DELIBERATE act rather than a quiet one:
    adding a row turns this red and the adder must come here and say so.

    That is the same handshake as the sibling's ``_SANITISERS`` pin, and for
    the same reason argued there -- **a pin updated before its evidence is a
    different act from one updated after, and the diff looks identical.**

    The three measured candidates, none of them this wave's to claim:

        _landing_class   CERTIFIABLE   5-member alphabet, all constants
        is_read_url      CERTIFIABLE   2-member boolean alphabet
        _why_refused     REFUSED       one return interpolates a runtime token
    """
    assert VERDICTS == {}, (
        "VERDICTS has gained its first row(s): %s. That is the intended "
        "direction -- update this pin, and say in the entry's comment WHO "
        "authored the function, since an entry is a claim only its author "
        "may make." % sorted(VERDICTS)
    )


def test_nested_returns_are_not_counted_as_this_functions_alphabet():
    """CONTROL 6. The false-red arm, and it is the one that gets a check disabled.

    A verdict function that defines a helper must not be failed because of the
    helper's returns. Measured rather than assumed: the naive ``ast.walk``
    version of :func:`_returns_of` fails this.
    """
    source = (
        "def v(u):\n"
        "    def helper(x):\n        return x\n"
        '    return "CLOSED"\n'
    )
    assert non_constant_returns(source, "v") == [], (
        "a nested helper's `return x` was counted as the outer function's, "
        "which fails an honest verdict function for a reason it cannot fix."
    )
    assert measured_alphabet(source, "v") == frozenset({"CLOSED"})
