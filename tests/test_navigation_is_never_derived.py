"""A url that came from a navigation is never handed back to one.

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


def _is_tainted_expr(node: ast.AST, tainted: set[str]) -> bool:
    """Does this expression read anything the browser produced?

    WALKS THE WHOLE SUBTREE, so an f-string, a concatenation or a ``.format``
    that merely CONTAINS a tainted name is tainted too. A rule that only
    matched a bare ``Name`` would be defeated by ``landed + "/"``, which is the
    same url with a slash on it.
    """
    for child in ast.walk(node):
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
    return False


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
    tainted: set[str] = set()
    # PASS 1 -- what is tainted. Repeated to a fixed point, because an
    # assignment can taint a name that an EARLIER line already copied, and one
    # pass in document order would miss it.
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

    found: list[tuple[int, str]] = []
    for call in _goto_calls(tree):
        arg = _url_arg(call)
        if arg is None:
            continue
        if _is_tainted_expr(arg, tainted):
            found.append((call.lineno, ast.unparse(arg)))
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
#: **THIS RULE FOUND A THIRD ONE ON ITS FIRST RUN, AND IT IS NOT IN A PROBE.**
#: Both probes were fixed before this test existed; ``server.py`` was not,
#: because nobody had looked. ``linkedin_my_profile(include_skills=True)``
#: derives the operator's slug FROM A LANDED URL and then navigates to a url
#: built out of it::
#:
#:     slug = shape.profile_slug_from(final_url)      # server.py:1695
#:     skills_url = f"{BASE_URL}/in/{slug}/details/skills/"
#:     skills_final = await BROWSER.goto(page, skills_url)
#:
#: It is SAFE TODAY and it is the same class. The allowlist admits
#: ``/in/<member>/details/``, so the navigation succeeds and no refusal fires;
#: the exposure is that the aim comes from the page rather than from this
#: repository, which is the property the ruling is about.
#:
#: WHY IT IS DECLARED AND NOT FIXED HERE. The fix is almost certainly to
#: navigate ``/in/me/details/skills/`` -- ``me`` matches the same allowlist
#: pattern, and "LinkedIn's own self-reference serves the signed-in member and
#: nobody else" is the argument that already carried the probes. But whether
#: LinkedIn SERVES that address is a live measurement nobody has taken, and
#: changing a shipped read tool on an unverified guess is how a working
#: capability breaks quietly.
#:
#: THE SET IS ASSERTED, NOT A COUNT AND NOT A SKIP. A new derived navigation
#: fails naming itself; FIXING this one also fails, because the declared entry
#: stops matching and has to be deleted. The documentation of the defect cannot
#: survive the fix -- section 88's shape, applied to an inventory.
KNOWN_DERIVED_NAVIGATIONS: dict[str, list[str]] = {
    "server.py": ["skills_url"],
}


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


def test_the_checker_reads_both_goto_arities():
    """``BROWSER.goto(page, url)`` and ``page.goto(url)`` both carry a url.

    Pinned because the argument POSITION differs between them, and a checker
    that only understood one would be silently blind to half the call sites
    while reporting a clean scan.
    """
    assert violations(_HEAD + "    await page.goto(page.url)\n")
    assert violations(_HEAD + "    await BROWSER.goto(page, page.url)\n")
    assert violations(_HEAD + "    await BROWSER.goto(page, url=page.url)\n")
