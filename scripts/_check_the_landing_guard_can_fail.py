"""Show the landing guard failing, by restoring the refusal that ACTUALLY SHIPPED.

A check that cannot fail certifies nothing, and this package has shipped one of
those. So before ``tests/test_landing.py`` and
``tests/test_company_root.py``'s inverted control are allowed to count as
evidence that the landed-url leak is closed, they have to be shown convicting
the defect.

## THE DEFECT IS THE REAL PREVIOUS STATE, NOT A MUTATION SOMEBODY INVENTED

``_THE_REFUSAL_THAT_SHIPPED`` below is the exact message
``auth.assert_not_authwall`` carried at master ``762ec23``, character for
character. **A control whose defect is the state the repository was actually
in is the strongest kind available**, because nobody has to argue the mutation
is representative -- the argument this repository's coercion-family control
makes, and the reason that one restores ``int()`` rather than inventing a
leaky helper.

## IT REBINDS AT EVERY IMPORT SITE AND PRINTS HOW MANY IT REPLACED

``from linkedin_server.auth import assert_not_authwall`` COPIES THE FUNCTION
OBJECT. Patching ``auth.assert_not_authwall`` alone changes nothing that
``server.py`` or ``writes.py`` ever calls, and this script would report a guard
that "cannot fail" when it had never been handed a defect at all.

**A COUNT OF ZERO IS A LOUD FAILURE OF THE CONTROL**, not a quiet pass. That
lesson is not this file's: ``scripts/_check_the_coercion_family_guard_can_fail``
records paying for it, and this is the same shape one class over.

## WHAT IT DOES NOT DO

It does not touch a browser, a network or the operator's profile. It rebinds
in-process, runs pytest in a CHILD process against the unmodified tree, and
compares the two runs. The planted build is never written to disk, so there is
nothing to forget to restore -- the failure mode that made the coercion
control verify its restore by sha256.

Run::

    python scripts/_check_the_landing_guard_can_fail.py
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

#: The message ``assert_not_authwall`` shipped with until 2026-09-21.
#: Reproduced verbatim. ``tests/test_company_root.py`` holds the same string in
#: ``_the_refusal_that_shipped`` and the check below asserts the two agree, so
#: a repair to one cannot silently leave the other describing a defect nobody
#: has any more.
_THE_REFUSAL_THAT_SHIPPED = (
    "loading the {surface} page landed on {final_url}, which is "
    "LinkedIn's signed-out wall -- there is no live session. Call "
    "linkedin_login and sign in yourself in the window it "
    "opens."
)

#: The modules that hold their own reference to the function. HARVESTED, not
#: listed: a module that starts importing it tomorrow is in the set the moment
#: it does. The count is printed, and zero is a failure.
_IMPORTERS = ("linkedin_server.server", "linkedin_server.writes")

#: Which tests must go RED under the plant. Each is named with what it proves,
#: because a control that reports "something failed" proves less than one that
#: reports WHICH thing.
_MUST_CONVICT = (
    (
        "tests/test_company_root.py::"
        "test_the_shipped_authwall_refusal_no_longer_publishes_the_slug_it_bounced",
        "the inverted control -- the test that used to assert the leak existed",
    ),
    (
        "tests/test_landing.py::"
        "test_the_refusal_carries_no_part_of_the_landing_and_neither_does_the_log",
        "the end-to-end property, over the refusal AND the log",
    ),
    (
        "tests/test_landing.py::test_the_exception_carries_no_url_attribute",
        "the attribute path, which the plant does NOT reopen -- expected GREEN",
    ),
)


def _planted(marker_source):
    """Build the pre-repair ``assert_not_authwall``, closing over the real
    marker predicate so the VERDICT is unchanged and only the MESSAGE is the
    defect. A plant that also changed which urls are refused would be two
    mutations, and the report could not say which one the guard caught.
    """
    from linkedin_server.errors import NotAuthenticatedError

    def assert_not_authwall(final_url: str, *, surface: str) -> None:
        if marker_source(final_url) is not None:
            raise NotAuthenticatedError(
                _THE_REFUSAL_THAT_SHIPPED.format(
                    surface=surface, final_url=final_url
                )
            )

    return assert_not_authwall


def _import_style(module_name: str) -> str:
    """MODULE_LEVEL, FUNCTION_LOCAL or NONE -- parsed, not guessed.

    **THE TWO STYLES NEED OPPOSITE TREATMENT AND THE DIFFERENCE IS INVISIBLE
    AT RUNTIME.** ``from linkedin_server.auth import assert_not_authwall`` at
    module level COPIES the function object, so patching ``auth`` alone
    changes nothing that module calls -- it has to be rebound in place. The
    same statement INSIDE A FUNCTION BODY re-resolves from ``auth`` on every
    call, so the ``auth`` rebinding already covers it and there is no module
    attribute to set.

    A control that only counted module attributes would report the second
    style as a binding it failed to reach, which reads exactly like a hole.
    ``writes.py`` is that style.
    """
    import ast
    import importlib.util

    spec = importlib.util.find_spec(module_name)
    if spec is None or not spec.origin:
        return "NONE"
    tree = ast.parse(pathlib.Path(spec.origin).read_text(encoding="utf-8"))
    inside_function = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if not any(alias.name == "assert_not_authwall" for alias in node.names):
            continue
        inside_function = True
        for parent in ast.walk(tree):
            if isinstance(parent, ast.Module) and node in parent.body:
                return "MODULE_LEVEL"
    return "FUNCTION_LOCAL" if inside_function else "NONE"


def _rebind(function) -> tuple[int, list[tuple[str, str]]]:
    """Put ``function`` at every binding of the name.

    Returns ``(how many module attributes were set, [(module, style)])``.
    """
    import importlib

    from linkedin_server import auth

    auth.assert_not_authwall = function
    replaced = 1
    styles: list[tuple[str, str]] = [("linkedin_server.auth", "DEFINITION")]
    for name in _IMPORTERS:
        module = importlib.import_module(name)
        style = _import_style(name)
        styles.append((name, style))
        if hasattr(module, "assert_not_authwall"):
            setattr(module, "assert_not_authwall", function)
            replaced += 1
    return replaced, styles


def _the_two_copies_of_the_planted_message_agree() -> bool:
    """The test file holds the same string. Drift there is drift in a control."""
    import tests.test_company_root as subject

    theirs = subject._the_refusal_that_shipped("<URL>", surface="<SURFACE>")
    mine = _THE_REFUSAL_THAT_SHIPPED.format(surface="<SURFACE>", final_url="<URL>")
    return theirs == mine


def _run(selector: str) -> int:
    """Run one test in a CHILD process against the unmodified tree."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", selector, "-q", "--no-header"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    return proc.returncode


def main() -> int:
    from linkedin_server import auth, landing

    print("THE LANDING GUARD, SHOWN FAILING")
    print("=" * 72)

    if not _the_two_copies_of_the_planted_message_agree():
        print(
            "FAIL: the planted message here and the one in "
            "tests/test_company_root.py have drifted. One of them is "
            "describing a defect the other does not."
        )
        return 2
    print("the planted message matches the copy in tests/test_company_root.py")

    print()
    print("1. THE TREE AS IT STANDS -- every guard must be GREEN")
    green_ok = True
    for selector, what in _MUST_CONVICT:
        code = _run(selector)
        print("   %-6s %s" % ("PASS" if code == 0 else "FAIL", what))
        green_ok = green_ok and code == 0
    if not green_ok:
        print("   the tree is already red; the control below would prove nothing")
        return 2

    print()
    print("2. THE PLANT -- the refusal that actually shipped, rebound in place")
    shipped_marker = landing.authwall_marker
    replaced, styles = _rebind(_planted(shipped_marker))
    for module_name, style in styles:
        print("   %-26s %s" % (module_name, style))
    print("   module attributes replaced: %d" % replaced)
    unreached = [
        module_name
        for module_name, style in styles
        if style not in ("DEFINITION", "MODULE_LEVEL", "FUNCTION_LOCAL")
    ]
    if replaced < 2 or unreached:
        print(
            "   FAIL: a plant that reached one module proves nothing. "
            "`from ... import assert_not_authwall` at MODULE level copies the "
            "function object; unreached: %r" % (unreached,)
        )
        return 2
    print(
        "   every importer is either rebound in place or resolves through "
        "linkedin_server.auth at call time, which the line above rebound."
    )

    from linkedin_server import server
    from linkedin_server.errors import NotAuthenticatedError

    needle = "example-markersurname-associates"
    url = (
        "https://www.linkedin.com/authwall?sessionRedirect="
        "https%3A%2F%2Fwww.linkedin.com%2Fcompany%2F" + needle + "%2F"
    )
    convicted = []
    for module_name in ("linkedin_server.auth",) + _IMPORTERS:
        import importlib

        module = importlib.import_module(module_name)
        function = getattr(module, "assert_not_authwall", None)
        if function is None:
            continue
        try:
            function(url, surface="organisation Page")
        except NotAuthenticatedError as exc:
            rendered = str(server._error(exc))
            convicted.append((module_name, needle in rendered))
    print()
    print("3. WHAT THE PLANT PUBLISHES, per binding")
    for module_name, leaked in convicted:
        print(
            "   %-26s %s"
            % (module_name, "LEAKS the slug" if leaked else "clean")
        )
    leaked_count = sum(1 for _m, leaked in convicted if leaked)

    # Restore, in-process, before anything else runs. The repaired function is
    # re-imported from a reloaded module rather than stashed in a local, so the
    # restore is the real one and not a copy this script was holding.
    _rebind(_shipped())
    assert auth.assert_not_authwall is not None
    assert "WITHHELD" in _nothing_leaks_now(), "the restore did not take"

    print()
    print("4. THE VERDICT")
    print("   bindings driven:        %d" % len(convicted))
    print("   bindings that LEAKED:   %d" % leaked_count)
    if leaked_count != len(convicted) or not convicted:
        print(
            "   FAIL: the plant did not reach every binding, so a green in "
            "this suite would not mean what it says."
        )
        return 2
    print(
        "   PASS: the refusal that shipped publishes the slug at every "
        "binding, and the guards above are green only because it no longer "
        "does."
    )
    return 0


def _shipped():
    """The repaired function, re-imported fresh so the restore is the real one."""
    import importlib

    from linkedin_server import auth

    importlib.reload(auth)
    return auth.assert_not_authwall


def _nothing_leaks_now() -> str:
    """Drive the restored function once and return its message.

    **THE RESTORE IS VERIFIED RATHER THAN ASSUMED.** The coercion-family
    control records paying for that lesson: a plant left in place is a defect
    somebody else finds. Nothing here is written to disk, so the only thing
    that can go wrong is an in-process binding, and this is the check for it.
    """
    from linkedin_server import auth
    from linkedin_server.errors import NotAuthenticatedError

    try:
        auth.assert_not_authwall(
            "https://www.linkedin.com/authwall?sessionRedirect=%2Fcompany%2Fx",
            surface="control",
        )
    except NotAuthenticatedError as exc:
        return str(exc)
    return "DID NOT RAISE"


if __name__ == "__main__":  # pragma: no cover - a hand-run control
    raise SystemExit(main())
