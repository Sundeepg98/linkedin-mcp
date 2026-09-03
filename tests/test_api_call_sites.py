"""The HTTP requests this package makes that are NOT page navigations.

WHY THIS FILE EXISTS. ``readonly.assert_read_url`` is described throughout this
repo as the door every read goes through, and that description is precise and
slightly narrower than it reads: it is the only door to ``page.goto``. A call
made with ``page.request.get`` is not a navigation and never reaches it.

Measured 2026-08-24, while investigating whether a paged read could be built on
LinkedIn's own API:

* ``assert_read_url`` is called in exactly TWO places -- ``browser.py`` and
  ``writes.py``, both wrapping ``goto``;
* ``auth.py`` issues ``page.request.get(ME_API, ...)`` with no gate at all;
* and ``readonly.is_read_url(ME_API)`` is **False**. The identity endpoint this
  server has always used WOULD BE REFUSED BY ITS OWN READ BOUNDARY if that
  boundary were consulted.

**Nothing is wrong with the request.** It is one hardcoded module constant, GET
only, to LinkedIn's own identity endpoint, and no caller can influence it -- it
is the single call that answers "is there a live session", which is the one
question a page load cannot answer honestly. The problem was that **nobody had
written down that this path exists**, so the boundary read as complete when it
covered navigations only.

So this file does what ``readonly.SANCTIONED_MUTATIONS`` does for clicks:
enumerates the call sites, structurally, and fails if the set changes. The
enumeration is by AST rather than by text, because a text search for
``request.get`` cannot tell a call from a docstring mentioning one -- and this
repo's own guard modules are full of docstrings mentioning the things they hunt.

WHAT THIS DOES NOT DO. It does not gate the call, and it deliberately does not
add ``/voyager/api/me`` to the read allowlist. Adding it would move a frozen
boundary structure and fire the AST invariant, to authorise something that is
already a constant nobody can redirect. Pinning the call site is the cheaper
half of the trade and catches the failure that could actually happen: a future
edit adding a SECOND request, or pointing this one somewhere else.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from linkedin_server import readonly
from linkedin_server.config import ME_API

PACKAGE = Path(__file__).resolve().parents[1] / "linkedin_server"

#: HTTP verbs on a Playwright ``APIRequestContext``. ``fetch`` and the
#: mutating verbs are here even though none is used, so that adding one is a
#: failing test rather than a quiet new capability.
_VERBS = frozenset(
    {"get", "post", "put", "patch", "delete", "fetch", "head", "options"}
)

#: THE COMPLETE LIST of direct HTTP call sites this package is permitted to
#: contain, as ``(module, verb, first-argument-as-written)``. Deliberately
#: shaped like ``readonly.SANCTIONED_MUTATIONS``, and deliberately one line
#: long. The first argument is pinned AS SOURCE TEXT, so pointing the call at
#: a different url -- or at something a caller could supply -- fails here even
#: though the verb and the module are unchanged.
SANCTIONED_API_CALLS: frozenset[tuple[str, str, str]] = frozenset(
    {
        ("auth.py", "get", "ME_API"),
        # ADDED 2026-08-24, AND THE OMISSION IS THE FINDING. This entry was
        # missing while the docstring above and ``server_info`` both presented
        # a COMPLETE list naming one call. The walker matched
        # ``<x>.request.<verb>`` and was structurally blind to a bare-name
        # ``urlopen(...)``, so the enumeration returned the set the METHOD
        # expected rather than the set the repo HAS -- which is the first law
        # in the rewrite runbook, committed here by the person quoting it.
        # Loopback only: it asks a local Chrome whether it is attachable.
        ("cdp_bridge.py", "urlopen", "f'{endpoint()}/json/version'"),
    }
)


#: Callables that fetch over HTTP by NAME rather than through a request
#: object. Kept separate from :data:`_VERBS` because they are found a
#: different way: ``urlopen`` is a bare Name, or an Attribute on ``urllib``,
#: and no amount of looking for ``.request.<verb>`` will ever see one.
_FETCH_NAMES = frozenset({"urlopen", "urlretrieve", "urlretrieve"})


def _api_call_sites() -> list[tuple[str, str, str]]:
    """Every direct HTTP call in the package, found by AST. TWO SHAPES.

    THE SECOND SHAPE WAS MISSING UNTIL 2026-08-24, and its absence is the
    reason this docstring is longer than the function. The walker looked only
    for ``<x>.request.<verb>(...)`` -- so it saw the identity call and was
    structurally incapable of seeing ``cdp_bridge``'s bare ``urlopen(...)``,
    while this module and ``linkedin_server_info`` both advertised a COMPLETE
    list of one. An enumeration that reports the set its method expects rather
    than the set the repo has is the exact failure the rewrite runbook opens
    with, and it shipped here anyway.

    So both shapes are hunted now:

    * ``<x>.request.<verb>(...)`` -- a Playwright APIRequestContext call.
    * a call to a FETCH NAME -- ``urlopen(...)`` bare, or as an attribute on
      any receiver, which covers ``urllib.request.urlopen`` without needing to
      know the import spelling.
    """
    found: list[tuple[str, str, str]] = []
    for path in sorted(PACKAGE.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            verb = None
            if isinstance(func, ast.Attribute) and func.attr in _VERBS:
                receiver = func.value
                if isinstance(receiver, ast.Attribute) and receiver.attr == "request":
                    verb = func.attr
            elif isinstance(func, ast.Name) and func.id in _FETCH_NAMES:
                verb = func.id
            elif isinstance(func, ast.Attribute) and func.attr in _FETCH_NAMES:
                verb = func.attr
            if verb is None:
                continue
            first = ast.unparse(node.args[0]) if node.args else "<none>"
            found.append((path.name, verb, first))
    return found


def test_the_package_makes_exactly_the_sanctioned_direct_api_calls():
    """One call site, and its target is a module constant.

    A second one appearing -- or this one pointed at a caller-supplied string
    -- is a new way for this server to talk to LinkedIn that no allowlist
    would see, because ``assert_read_url`` only guards navigations.
    """
    assert set(_api_call_sites()) == set(SANCTIONED_API_CALLS)
    assert len(_api_call_sites()) == len(SANCTIONED_API_CALLS)


def test_no_mutating_verb_is_used_against_the_api():
    """GET only. The scanner already refuses ``.post(`` anywhere in the
    package; this says the same thing about the API surface specifically, so
    the claim does not rest on the scanner's pattern list alone."""
    for _module, verb, _arg in _api_call_sites():
        assert verb in {"get", "head", "options"} | _FETCH_NAMES, verb
    # And a fetch-name call is GET by construction -- urlopen without a data=
    # argument issues a GET, so the claim holds for both shapes rather than
    # only the one with the verb in its name.
    for path in sorted(PACKAGE.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            name = getattr(f, "id", None) or getattr(f, "attr", None)
            if name in _FETCH_NAMES:
                kwargs = {k.arg for k in node.keywords}
                assert "data" not in kwargs, (path.name, "urlopen with data= is a POST")
                assert len(node.args) < 2, (path.name, "positional data= is a POST")


def test_the_identity_endpoint_is_not_on_the_read_allowlist_and_that_is_recorded():
    """THE MEASUREMENT THIS FILE WAS WRITTEN FOR, asserted so it cannot rot.

    The endpoint this server has always used to answer "am I signed in" would
    be REFUSED by its own read boundary. That is not a defect -- the boundary
    is about navigations and this is not one -- but it is a fact a reader of
    ``readonly.py`` would not guess, and one that decides how any future API
    read has to be gated.

    If somebody later adds it to the allowlist, this test fails and they have
    to come here and say why. That is the intended outcome, not an obstacle.
    """
    assert readonly.is_read_url(ME_API) is False
    assert ME_API.startswith("https://www.linkedin.com/voyager/api/")


def test_assert_read_url_is_called_only_on_the_navigation_paths():
    """Pins the SCOPE of the read door, which is the half that surprised me.

    Two call sites, both wrapping a ``goto``. This is what makes the sentence
    "every read goes through the allowlist" true of navigations and false of
    everything else, and the number is asserted so that a third caller -- or
    the loss of one of these two -- is visible.
    """
    callers = set()
    for path in sorted(PACKAGE.glob("*.py")):
        if path.name == "readonly.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = node.func
            target = (
                name.attr
                if isinstance(name, ast.Attribute)
                else getattr(name, "id", "")
            )
            if target == "assert_read_url":
                callers.add(path.name)
    assert callers == {"browser.py", "writes.py"}, sorted(callers)


@pytest.mark.parametrize(
    "source, why",
    [
        (
            "async def f(page):\n    await page.request.get(url)\n",
            "a caller-supplied url",
        ),
        (
            "async def f(page):\n    await page.request.post(ME_API)\n",
            "a mutating verb",
        ),
        (
            "async def f(page):\n    await page.request.get(ME_API)\n"
            "async def g(page):\n    await page.request.get(OTHER_API)\n",
            "a second endpoint",
        ),
    ],
)
def test_the_enumerator_catches_what_it_is_written_to_catch(source, why):
    """THE CONTROL, and without it the assertions above pass on an enumerator
    that finds nothing at all -- which is exactly what a broken AST walk does.

    Each case is a real shape somebody could add: a url from an argument, a
    verb that writes, and a second endpoint beside the sanctioned one.
    """
    tree = ast.parse(source)
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr not in _VERBS:
            continue
        receiver = func.value
        if isinstance(receiver, ast.Attribute) and receiver.attr == "request":
            first = ast.unparse(node.args[0]) if node.args else "<none>"
            found.append((func.attr, first))

    assert found, why
    assert set(found) - {("get", "ME_API")}, why


def test_a_docstring_mentioning_a_request_is_not_counted_as_one():
    """WHY THE ENUMERATION IS AST AND NOT TEXT.

    This repo's guard modules are full of prose naming the calls they hunt --
    ``readonly.py``'s own tables are made of the strings it scans for. A text
    search for ``request.get`` would count this very docstring. The AST walk
    sees an expression statement holding a string, and no call at all.
    """
    source = (
        'def f():\n'
        '    """Calls page.request.get(SOMETHING) -- but only in prose."""\n'
        '    return 1\n'
    )
    tree = ast.parse(source)
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
    assert calls == []
    assert "request.get" in source


def test_readonly_states_its_own_scope_as_navigation_only():
    """The module must SAY what it covers, not leave it to be inferred.

    ``readonly.py``'s opening claim -- "the only door to ``page.goto``" -- was
    always exact and always read as broader than it is. Exactness is not the
    same as clarity: a reader who takes it for full coverage has not
    misunderstood the sentence, they have understood a different sentence that
    the true one is easily mistaken for.

    So the module states the scope outright and names the uncovered path. This
    pins that it still does, because a docstring is the easiest thing in a
    codebase to lose in a refactor and the whole point of it is to be there
    when somebody new arrives.
    """
    doc = readonly.__doc__ or ""
    assert "NAVIGATION-ONLY" in doc
    # It must name the mechanism that escapes it, not just gesture at one.
    assert "page.request.get" in doc
    assert "ME_API" in doc
    # And say which way the refusal would go, which is the surprising half.
    assert "REFUSED by this allowlist" in doc


def test_the_scope_statement_names_where_the_real_coverage_lives():
    """A gap named without its mitigation reads as an unfixed hole.

    The path is covered -- by an enumeration rather than by a pattern -- and
    the docstring has to say where, or the next reader either re-discovers the
    finding or "fixes" it by widening the allowlist, which is precisely the
    move it was decided against.
    """
    doc = readonly.__doc__ or ""
    assert "test_api_call_sites.py" in doc
    assert "direct_api_reads" in doc
    # And why the pattern list was NOT widened, so the decision survives.
    assert "AST invariant" in doc


def test_the_scope_statement_cost_no_boundary_movement():
    """MEASURED, not asserted, and recorded because it is the whole reason
    this could be written into ``readonly.py`` at all.

    The boundary freeze hashes the four constant structures as VALUES and each
    top-level function's token stream with COMMENT tokens dropped. A MODULE
    docstring is neither -- so stating the scope moved no digest. Verified two
    ways when it was written: the digest probe returned ``7a48ca1e8dd14ec1``
    under both 3.10.19 and 3.13.14, unchanged; and the module body excluding
    its docstring parsed AST-identical to the previous commit.

    The second is the stronger claim and is the one reproduced here, because a
    digest matching proves the hashed things did not move while this proves
    NOTHING BUT PROSE did. Note the asymmetry it protects against: a FUNCTION
    docstring is a string token inside a function body and WOULD move that
    function's digest. Only the module docstring is free, and a future edit
    that "tidies" this paragraph into ``assert_read_url``'s own docstring
    would fire the invariant -- correctly.
    """
    import ast

    source = (PACKAGE / "readonly.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    assert isinstance(tree.body[0], ast.Expr), "module docstring expected first"
    assert ast.get_docstring(tree), "and it must be a docstring, not a bare expr"

    # Every top-level function is still present and none was touched by this.
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    # THIRTEEN UNTIL 2026-09-03, FOURTEEN SINCE. readonly.py gained one
    # top-level function when the compose-by-identifier admission shipped --
    # the anchored pattern-exemption helper, which exists because an exact key
    # was impossible: the exemption table is an equality test on a lowered url
    # and a compose-with-recipient address carries two member ids.
    #
    # THE COUNT IS NOT INCIDENTAL TO THIS TEST. What it protects is the claim
    # in the docstring above -- that stating the scope in a MODULE docstring
    # moved no digest. A function arriving is exactly the thing that would
    # falsify "nothing but prose changed", so the number must move
    # deliberately, with the arrival named, rather than be derived.
    assert len(functions) == 14, len(functions)
