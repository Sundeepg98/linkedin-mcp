"""A value the browser chose never reaches a navigation, and never reaches a print.

TWO SINKS, ONE TAINT ENGINE. The filename names the first, which is the one
this file was built for; the second was added on 2026-09-03 after the same
defect leaked the operator's slug three times in a morning. They share
``_tainted_names`` deliberately -- two implementations of "did this come from
the browser" would drift, and the quieter one would go wrong unnoticed.

    SINK 1   BROWSER.goto        a url the page chose, navigated to
    SINK 2   print and logging   a url the page chose, published

**A LEAK NEEDS A TAINTED VALUE AND A WAY OUT.** This file guarded one way out
for a day. Three leaks went through the other one -- an allowlist refusal
interpolating the url it refused, a disk ruling that pasted its own diagnostic,
and a probe printing a landed path out of a file whose docstring promised it
never printed a url. Each was caught by a DIFFERENT accident: a raised
exception, a tracked-file scan, a human reading output. **None by an
instrument.** That is not three mistakes, it is one missing check that had
already fired three times.

---



THE DEFECT THIS EXISTS FOR, measured on 2026-09-03. Both payload probes did::

    landed = await BROWSER.goto(page, SELF_PROFILE_URL)
    ...
    await BROWSER.goto(page, landed)

``/in/me/`` resolves to a member path that LinkedIn intermittently decorates
with ``?isSelfProfile=true``. The read allowlist admits the member path and
NOT the query, so ``readonly.assert_read_url`` refused -- and its refusal
interpolates the url it is refusing. **The operator's vanity slug went into a
traceback**, out of a script whose own docstring promises it never prints a
url. That promise held for what the script CHOOSES to print and not for an
exception escaping through it.

## The ruling, and why it is this test rather than a redaction

The url STAYS in the refusal. A navigation refusal that will not name what it
refused makes every future boundary bug harder to find, and the boundary is
the thing most worth being able to debug. **The defect is at the CALL SITE** --
handing a landed identity url to the function whose job is to print urls -- and
the fix was to remove the mechanism rather than guard it: nothing derived from
a navigation is passed to ``goto``, so there is no identity url for an error to
interpolate.

**A RULING THAT IS ONLY PROSE IS SECTION 90'S DEFECT** -- prose asserting a
relationship in the code that nothing checks. This is the enforceable form.

## What is tainted, and why the rule is about DERIVATION rather than about names

A url is TAINTED if it came from the browser: the return of a ``goto``, a
``.url`` attribute off a page, a request or a response, or any local bound to
one of those. Taint propagates through assignment, so renaming ``landed``
defeats nothing.

**Untainted is not "any name" -- it is a value this repository authored.** A
module-level constant, a literal, or a template built from them. That is the
whole point: the process must be able to say what it is about to navigate to
WITHOUT having asked the page, because a page that can choose the next url can
choose a stranger's.

## It is shown failing in BOTH directions, on synthetic source

A checker that flags everything would pass a red-only demonstration while
making the sanctioned form unwritable, so the green cases are asserted as
carefully as the red ones -- including the exact shape both probes now use.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
SCANNED = ("scripts", "linkedin_server")

#: Attributes whose value came from the browser rather than from this
#: repository. ``url`` covers ``page.url``, ``response.url`` and
#: ``request.url`` without needing to know which object it was read off --
#: naming the objects would be a list to keep in step, and the attribute is
#: the thing that carries the taint whatever holds it.
_TAINTED_ATTRS = frozenset({"url"})

#: Calls whose RETURN is a url the browser chose.
_TAINTED_CALLS = frozenset({"goto"})


#: THE SECOND SINK. ``print`` and the logging verbs.
#:
#: A LEAK NEEDS A TAINTED VALUE AND A WAY OUT, and until now this rule guarded
#: only one way out. Three slug leaks in one day went through the other one.
_SINK_NAMES = frozenset({"print"})
_SINK_ATTRS = frozenset(
    {"debug", "info", "warning", "warn", "error", "exception", "critical", "log"}
)

#: FUNCTIONS WHOSE RESULT CARRIES NONE OF THEIR INPUT.
#:
#: **WITHOUT THIS THE RULE WOULD FORBID ITS OWN FIX.** ``_shape_of`` takes a
#: landed url and returns the RELATION between it and the address that was
#: asked for -- served, redirected within the member space, or redirected
#: elsewhere. That is the repair for the third leak, and a rule that flagged it
#: would push the next author back to printing the path.
#:
#: AN ENTRY HERE IS A CLAIM ABOUT A FUNCTION'S CONTRACT, so it is deliberately
#: hard to add: the function must take a tainted value and provably return a
#: value that cannot reconstruct it. ``_member_path`` is NOT here and must not
#: be -- it returns a path, and a member path IS an identity. That distinction
#: is the whole of the third leak.
_SANITISERS = frozenset({"_shape_of", "_redact"})

#: CALLS WHOSE RESULT IS A NUMBER, whatever went in.
_COUNTING_CALLS = frozenset({"len"})


def _is_sanitiser_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Name):
        return func.id in _SANITISERS
    if isinstance(func, ast.Attribute):
        return func.attr in _SANITISERS
    return False


def _is_tainted_expr(node: ast.AST, tainted: set[str]) -> bool:
    """Does this expression read anything the browser produced?

    WALKS THE WHOLE SUBTREE, so an f-string, a concatenation or a ``.format``
    that merely CONTAINS a tainted name is tainted too. A rule that only
    matched a bare ``Name`` would be defeated by ``landed + "/"``, which is the
    same url with a slash on it.

    AND IT STOPS AT A SANITISER, which is what makes the output rule usable
    rather than merely strict. ``_shape_of(landed, ASKED)`` reads a tainted
    value and returns a relation; descending into it would flag the very repair
    the third leak was fixed with.
    """
    stack: list[ast.AST] = [node]
    while stack:
        child = stack.pop()
        if _is_sanitiser_call(child):
            # ITS RESULT CARRIES NOTHING, so its arguments are not this rule's
            # business. The claim lives in _SANITISERS and is argued there.
            continue
        if isinstance(child, ast.Compare):
            # A COMPARISON YIELDS A BOOLEAN, whatever it compared. Without this
            # the rule flags `"/login" in landed` -- an auth-wall check every
            # probe here makes and the one thing they must keep doing. It also
            # stops the fixed point tainting `walled = "/login" in landed`,
            # which is a bool wearing a tainted name.
            continue
        if (
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Name)
            and child.func.id in _COUNTING_CALLS
        ):
            # `len(payload)` is an integer. Counting a thing is the discipline
            # this package uses INSTEAD of printing it, so a rule that flagged
            # it would forbid the safe form.
            continue
        if isinstance(child, ast.Name) and child.id in tainted:
            return True
        if isinstance(child, ast.Attribute) and child.attr in _TAINTED_ATTRS:
            return True
        if (
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and child.func.attr in _TAINTED_CALLS
        ):
            return True
        stack.extend(ast.iter_child_nodes(child))
    return False


def _tainted_names(tree: ast.AST) -> set[str]:
    """Every name in a module bound, however indirectly, to a navigation.

    ONE DEFINITION, SHARED BY BOTH SINKS. The navigation rule and the output
    rule ask the same question -- did this come from the browser -- and two
    implementations of it would drift, with the quieter one going wrong
    unnoticed.

    COLLECTED PER MODULE AND TO A FIXED POINT. Per module because both probes
    read ``landed`` from an enclosing scope inside a closure, so a
    function-scoped analysis would be blind to the exact shape this was written
    for. To a fixed point because an assignment can taint a name that an
    EARLIER line already copied, and one pass in document order would miss it.
    """
    tainted: set[str] = set()
    for _ in range(4):
        before = set(tainted)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            value = node.value
            if value is None or not _is_tainted_expr(value, tainted):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                for name in ast.walk(target):
                    if isinstance(name, ast.Name):
                        tainted.add(name.id)
        if tainted == before:
            break
    return tainted


def _sink_calls(tree: ast.AST):
    """Every ``print(...)`` and logging call in a module."""
    for child in ast.walk(tree):
        if not isinstance(child, ast.Call):
            continue
        func = child.func
        if isinstance(func, ast.Name) and func.id in _SINK_NAMES:
            yield child, func.id
        elif isinstance(func, ast.Attribute) and func.attr in _SINK_ATTRS:
            yield child, func.attr


def _goto_calls(node: ast.AST):
    """Every ``*.goto(...)`` call in a subtree."""
    for child in ast.walk(node):
        if (
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and child.func.attr == "goto"
        ):
            yield child


def _url_arg(call: ast.Call):
    """The url argument of a ``goto`` call, positional or keyword.

    ``BROWSER.goto(page, url)`` puts it second; ``page.goto(url)`` puts it
    first. Taking "the last positional that is not the page" would be guessing,
    so both arities are handled explicitly and anything else returns None
    rather than a wrong node.
    """
    for keyword in call.keywords:
        if keyword.arg == "url":
            return keyword.value
    if len(call.args) >= 2:
        return call.args[1]
    if len(call.args) == 1:
        return call.args[0]
    return None


def violations(source: str, label: str = "<source>") -> list[tuple[int, str]]:
    """Every ``goto`` in this source whose url is derived from a navigation.

    TAINT IS COLLECTED PER MODULE AND IN DOCUMENT ORDER, not per function.
    A closure that reads a ``landed`` from its enclosing scope is the exact
    shape both probes had -- ``_remember`` compared against a name bound
    outside it -- so a function-scoped analysis would have been blind to the
    thing it was written for.
    """
    tree = ast.parse(source, filename=label)
    tainted = _tainted_names(tree)
    found: list[tuple[int, str]] = []
    for call in _goto_calls(tree):
        arg = _url_arg(call)
        if arg is None:
            continue
        if _is_tainted_expr(arg, tainted):
            found.append((call.lineno, ast.unparse(arg)))
    return sorted(found)


def output_violations(source: str, label: str = "<source>") -> list[tuple[int, str]]:
    """Every ``print`` or logging call handed something a navigation produced.

    THE SINK THAT HAD NO GUARD, AND IT HAD ALREADY FIRED THREE TIMES. On
    2026-09-03 the operator's vanity slug reached a transcript three separate
    ways: an allowlist refusal interpolating the url it refused, a disk ruling
    that pasted its own diagnostic, and a probe printing a landed path out of a
    file whose docstring promised it never printed a url. Each was caught by a
    DIFFERENT accident -- a raised exception, a tracked-file scan, a human
    reading output -- and none by an instrument.

    **A LEAK NEEDS A TAINTED VALUE AND A WAY OUT.** The taint half was already
    computed for the navigation rule; this adds the second way out, and the
    same engine answers both. One taint definition, two sinks, so the two
    cannot drift apart.

    WHAT THIS DOES NOT COVER, SAID PLAINLY RATHER THAN IMPLIED. Taint here
    means NAVIGATION-DERIVED -- a ``goto`` return, a ``.url``, anything bound to
    one. **A response BODY is not tainted by this rule**, so printing
    ``await response.text()`` would pass, and that is the richest identity in
    this package. It is left out deliberately: tainting it would flag
    ``len(payload)`` and every count taken off it, and a rule whose true
    positives arrive buried in false ones gets declared into uselessness. The
    body is guarded by design instead -- the probes hold no output path and
    emit counts -- and naming the gap is the honest alternative to implying it
    is covered.
    """
    tree = ast.parse(source, filename=label)
    tainted = _tainted_names(tree)
    found: list[tuple[int, str]] = []
    for call, sink in _sink_calls(tree):
        for argument in list(call.args) + [k.value for k in call.keywords]:
            if _is_tainted_expr(argument, tainted):
                found.append((call.lineno, "%s(%s)" % (sink, ast.unparse(argument))))
                break
    return sorted(found)


def _python_files() -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for folder in SCANNED:
        out.extend(sorted((REPO / folder).glob("*.py")))
    return out


# ---------------------------------------------------------------------------
# The rule, on this repository
# ---------------------------------------------------------------------------


#: THE SITES THAT ARE STILL DERIVED, DECLARED RATHER THAN WAIVED.
#:
#: **EMPTY, AND IT WAS NOT EMPTY WHEN THIS FILE WAS WRITTEN.** The rule found a
#: third site on its first run, in shipped code rather than in a probe:
#: ``linkedin_my_profile(include_skills=True)`` parsed the operator's slug OUT
#: OF A LANDED URL and navigated to an address built from it. Safe -- the
#: allowlist admits ``/in/<member>/details/skills/`` -- and the same class,
#: because the aim came from the page rather than from this package.
#:
#: IT WAS DECLARED HERE FIRST, DELIBERATELY, and the holding position was the
#: right one: the fix was a GUESS until ``scripts/_probe_self_details_url.py``
#: ran live on 2026-09-03 and measured that ``/in/me/details/skills/`` is
#: served, returning 20 skill cards through the same harvest with the same
#: arguments. Then it was fixed, and the entry deleted.
#:
#: **THE DELETION IS THE MECHANISM WORKING.** The set is asserted rather than a
#: count or a skip, so fixing a declared site FAILS this file until its entry
#: goes -- the documentation of a defect cannot outlive the defect. That is
#: section 88's shape applied to an inventory, and it has now been exercised
#: once in each direction: the entry was forced in by a finding and forced out
#: by a fix.
#:
#: Leave it empty. A new derived navigation fails naming itself, and an entry
#: added here has to carry the same argument this one did.
KNOWN_DERIVED_NAVIGATIONS: dict[str, list[str]] = {}


@pytest.mark.parametrize(
    "path", _python_files(), ids=lambda p: p.name
)
def test_no_navigation_is_aimed_at_a_url_the_browser_chose(path):
    """THE RULE. Every ``goto`` argument is a value this repository authored."""
    found = violations(path.read_text(encoding="utf-8"), path.name)
    declared = KNOWN_DERIVED_NAVIGATIONS.get(path.name, [])
    assert [expr for _line, expr in found] == declared, (
        "%s: derived-navigation sites are %s and the declared set is %s. "
        "A url that came from the page is a url the page chose, and handing "
        "one to the read boundary is what put the operator's profile slug in "
        "a traceback. If you ADDED one, navigate a module-level constant "
        "instead. If you FIXED one, delete its entry from "
        "KNOWN_DERIVED_NAVIGATIONS -- this failing is the point."
        % (path.name, found, declared)
    )


def test_every_declared_site_still_exists():
    """A DECLARATION FOR A SITE THAT IS GONE IS A COMMENT PRETENDING TO BE A
    CHECK.

    ``read_settings_surface`` is this repository's standing proof of what a
    stale "known hole" note becomes: dead for ten days with its own comment
    observing it was uncalled. An entry above must name a file that exists and
    a site that is really still there.
    """
    for name in KNOWN_DERIVED_NAVIGATIONS:
        matches = [p for p in _python_files() if p.name == name]
        assert matches, "%s is declared and is not a scanned file" % name
        found = violations(matches[0].read_text(encoding="utf-8"), name)
        assert found, (
            "%s is declared as having a derived navigation and has none. "
            "Delete the entry." % name
        )


def test_there_are_files_to_scan_and_gotos_among_them():
    """THE SWEEP PASSES VACUOUSLY ON AN EMPTY GLOB, so both halves are pinned.

    A rule asserted over zero files, or over files containing zero
    navigations, is a green test that checks nothing -- and this repository
    has already shipped one of those.
    """
    files = _python_files()
    assert len(files) > 10, files
    total = sum(
        len(list(_goto_calls(ast.parse(p.read_text(encoding="utf-8")))))
        for p in files
    )
    assert total >= 3, total


# ---------------------------------------------------------------------------
# Shown failing, and shown NOT failing, on synthetic source
# ---------------------------------------------------------------------------

_HEAD = "async def main(page):\n"


@pytest.mark.parametrize(
    "body, why",
    [
        (
            "    landed = await BROWSER.goto(page, SELF_PROFILE_URL)\n"
            "    await BROWSER.goto(page, landed)\n",
            "the exact shape both probes shipped with",
        ),
        (
            "    landed = await BROWSER.goto(page, SELF_PROFILE_URL)\n"
            "    here = landed\n"
            "    await BROWSER.goto(page, here)\n",
            "taint survives a rename",
        ),
        (
            "    landed = await BROWSER.goto(page, SELF_PROFILE_URL)\n"
            '    await BROWSER.goto(page, landed + "/")\n',
            "taint survives being concatenated",
        ),
        (
            "    landed = await BROWSER.goto(page, SELF_PROFILE_URL)\n"
            '    await BROWSER.goto(page, f"{landed}?x=1")\n',
            "taint survives an f-string",
        ),
        (
            "    await BROWSER.goto(page, page.url)\n",
            "the address bar, read directly",
        ),
        (
            "    for response in seen:\n"
            "        await BROWSER.goto(page, response.url)\n",
            "a response's url, which is the browser's answer and not a plan",
        ),
        (
            "    await BROWSER.goto(page, await BROWSER.goto(page, X))\n",
            "a goto return passed straight back in",
        ),
    ],
)
def test_it_goes_red_on_a_derived_navigation(body, why):
    found = violations(_HEAD + body)
    assert found, why


@pytest.mark.parametrize(
    "body, why",
    [
        (
            "    landed = await BROWSER.goto(page, SELF_PROFILE_URL)\n"
            "    await BROWSER.goto(page, SELF_PROFILE_URL)\n",
            "THE SANCTIONED FORM, and the one both probes now use: pass 1 keeps "
            "its landed url for the auth-wall check and pass 2 navigates the "
            "constant again",
        ),
        (
            '    await BROWSER.goto(page, BASE_URL + "/in/me/")\n',
            "a template built from a module constant",
        ),
        (
            '    await BROWSER.goto(page, f"{BASE_URL}/jobs/view/{job_id}/")\n',
            "a job id is a caller's argument, not a url the browser chose",
        ),
        (
            "    landed = await BROWSER.goto(page, SELF_PROFILE_URL)\n"
            '    if "/login" in landed:\n'
            "        return\n",
            "READING a landed url is fine -- the rule is about navigating to "
            "one, and the auth-wall check must stay possible",
        ),
    ],
)
def test_it_stays_green_on_a_url_this_repository_authored(body, why):
    """THE OTHER DIRECTION, and it is the half that keeps the rule usable.

    A checker that flagged every ``goto`` would pass every red case above
    while making the sanctioned form unwritable -- a guard that forbids the
    fix is worse than no guard, because the next author deletes it.
    """
    assert violations(_HEAD + body) == [], why


#: OUTPUT SITES THAT HAND A NAVIGATION-DERIVED VALUE TO A PRINT.
#:
#: **EIGHT, ALL FOUND BY THIS RULE'S FIRST RUN, NONE PREVIOUSLY KNOWN.** Every
#: one is a hand-run diagnostic probe printing the url it landed on, and every
#: one is the shape of the third slug leak: a value the browser chose, handed
#: to an output sink, in a file that never claimed to be careful about it.
#:
#: WHY THEY ARE DECLARED AND NOT FIXED. The tempting argument is that these
#: probes land on RESOURCE paths -- /feed/following/, a job url, a preferences
#: page -- so their urls carry no identity. **That is the exact argument that
#: produced the third leak.** "Paths are safe" was never the rule; "these paths
#: are safe" was, and not one of these eight has been checked. Fixing them on
#: the assumption would be repeating this morning's mistake across more files.
#:
#: So they are declared, which states the truth: a rule now sees them, nobody
#: has measured what they emit, and the declaration makes that visible instead
#: of latent. Fixing one -- print a RELATION, or route it through a proven
#: redactor as ``_probe_messaging`` already does -- forces its entry out.
KNOWN_TAINTED_OUTPUT: dict[str, list[str]] = {
    "_capture_toggle_states.py": [
        "print(f'    final url : {page.url}')",
    ],
    "_probe_apply_flow.py": [
        "print(f'    landed  {page.url}')",
    ],
    "_probe_apply_route_screen.py": [
        "print(f'  {job_id}  EXPIRED (redirected to {landed[:70]})')",
    ],
    "_probe_follow_on_posting.py": [
        "print(f'    final url: {page.url}   pre {len(pre)}  hyd {len(hyd)}')",
    ],
    "_probe_following.py": [
        "print(f'    final url: {page.url}')",
    ],
    "_probe_in_progress.py": [
        "print(f'    landed {page.url}')",
    ],
    "_probe_interests.py": [
        "print(f'    final url: {page.url}')",
    ],
    "_probe_manage_pages_both.py": [
        "print(f'    final url: {page.url}')",
    ],
}


@pytest.mark.parametrize("path", _python_files(), ids=lambda p: p.name)
def test_no_navigation_derived_value_reaches_an_output_sink(path):
    """THE SECOND SINK, AND THE ONE THAT HAD NO GUARD AT ALL.

    Three slug leaks in one day, each found by a different accident and none by
    an instrument. A leak needs a tainted value AND a way out; the taint half
    was already computed for the navigation rule, and this is the other way
    out. The same engine answers both, so the two cannot drift.
    """
    found = output_violations(path.read_text(encoding="utf-8"), path.name)
    declared = KNOWN_TAINTED_OUTPUT.get(path.name, [])
    assert [what for _line, what in found] == declared, (
        "%s: tainted output sites are %s and the declared set is %s. A value "
        "the browser chose, handed to a print, is how the operator's slug "
        "reached a transcript three times. If you ADDED one, emit a RELATION "
        "or a count instead. If you FIXED one, delete its entry -- this "
        "failing is the point." % (path.name, found, declared)
    )


def test_every_declared_output_site_still_exists():
    """A declaration for a site that is gone is a comment pretending to check."""
    for name in KNOWN_TAINTED_OUTPUT:
        matches = [p for p in _python_files() if p.name == name]
        assert matches, "%s is declared and is not a scanned file" % name
        found = output_violations(matches[0].read_text(encoding="utf-8"), name)
        assert found, "%s is declared and has no tainted output. Delete it." % name


@pytest.mark.parametrize(
    "body, why",
    [
        ("    print(page.url)\n", "the address bar, printed bare"),
        (
            "    landed = await BROWSER.goto(page, X)\n    print(landed)\n",
            "a goto return, printed",
        ),
        (
            "    landed = await BROWSER.goto(page, X)\n"
            '    print(f"landed at {landed}")\n',
            "and inside an f-string",
        ),
        (
            "    landed = await BROWSER.goto(page, X)\n    logger.info(landed)\n",
            "a logging call is a sink too",
        ),
        (
            "    landed = await BROWSER.goto(page, X)\n    print(landed[:70])\n",
            "a SLICE of a url is still a url",
        ),
        (
            "    landed = await BROWSER.goto(page, X)\n"
            "    print(_member_path(landed))\n",
            "A MEMBER PATH IS AN IDENTITY. _member_path is deliberately not a "
            "sanitiser, and this is the third leak's exact shape",
        ),
    ],
)
def test_output_goes_red_on_a_navigation_derived_value(body, why):
    assert output_violations(_HEAD + body), why


@pytest.mark.parametrize(
    "body, why",
    [
        (
            "    landed = await BROWSER.goto(page, X)\n"
            "    print(_shape_of(landed, X))\n",
            "THE REPAIR MUST STAY WRITABLE -- a relation between the address "
            "asked for and the one returned carries neither",
        ),
        (
            "    landed = await BROWSER.goto(page, X)\n"
            '    print("/login" in landed)\n',
            "an auth-wall check yields a BOOLEAN, and every probe here makes one",
        ),
        (
            "    landed = await BROWSER.goto(page, X)\n"
            '    walled = "/login" in landed\n'
            "    print(walled)\n",
            "and the boolean does not become tainted by being named",
        ),
        (
            "    print(len(payload))\n",
            "a COUNT is the discipline this package uses instead of printing",
        ),
        (
            "    print(needle)\n",
            "THE OPERATOR'S OWN NEEDLE. He supplied it, it was in this process "
            "before any page loaded, and a rule that forbade echoing it would "
            "forbid telling him what he asked for",
        ),
        ("    print(response.status)\n", "a status code is not a url"),
    ],
)
def test_output_stays_green_on_a_value_that_carries_nothing(body, why):
    """THE OTHER DIRECTION, and it is what keeps the rule from being deleted.

    A checker that flagged every print would pass all six red cases above while
    making the repair, the auth-wall check and the counts unwritable. A guard
    that forbids the fix does not survive its first inconvenient morning.
    """
    assert output_violations(_HEAD + body) == [], why


def test_a_sanitiser_entry_is_a_claim_about_a_contract():
    """PINNED, because the set is the one place this rule can be defeated.

    Adding a name to ``_SANITISERS`` silences every site that calls it. Two
    entries today, each earned: ``_shape_of`` returns a relation, and
    ``_redact`` has its own both-directions test file. ``_member_path`` is NOT
    there and must not be -- it returns a path, and a member path is an
    identity. That single distinction is the whole of the third leak.
    """
    assert _SANITISERS == frozenset({"_shape_of", "_redact"}), _SANITISERS
    assert "_member_path" not in _SANITISERS
    assert "_path_of" not in _SANITISERS


def test_the_checker_reads_both_goto_arities():
    """``BROWSER.goto(page, url)`` and ``page.goto(url)`` both carry a url.

    Pinned because the argument POSITION differs between them, and a checker
    that only understood one would be silently blind to half the call sites
    while reporting a clean scan.
    """
    assert violations(_HEAD + "    await page.goto(page.url)\n")
    assert violations(_HEAD + "    await BROWSER.goto(page, page.url)\n")
    assert violations(_HEAD + "    await BROWSER.goto(page, url=page.url)\n")
