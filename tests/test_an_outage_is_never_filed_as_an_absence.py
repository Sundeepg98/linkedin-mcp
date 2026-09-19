"""A PROBE MUST CRASH ON AN OUTAGE. IT MUST NEVER RETURN A ZERO.

**THE FAILURE MODE, MEASURED TODAY.** The automation Chrome died at roughly
09:48 and was restarted at 10:04. Any live read taken in that window got an
attach failure whose text blames Chrome -- the one thing that was not wrong.
**A zero from a failed attach and a zero from an empty surface are the same
number and completely different findings**, and a probe that catches the
failure and reports the number has filed an outage as an absence.

At 09:50:03, inside that window, a probe died with ``ECONNREFUSED`` and
recorded NOTHING. That is the correct behaviour and it was structural rather
than lucky: the only ``try`` in that file is a ``try/finally`` for tab closure,
with no ``except`` anywhere. **A probe with no exception handler cannot file an
outage as an absence.**

## WHAT THIS FILE CHECKS, AND WHY IT IS NOT "NO except ANYWHERE"

A blanket ban would be wrong and would be routed around within a day. Probes
legitimately catch: reporting *"reader failed: TimeoutError"* for ONE selector,
on a page that demonstrably rendered, is a measurement and not a suppression --
and several probes here do exactly that, returning ``None`` with a docstring
saying **None is NOT zero and is never printed as one.**

**THE DISTINCTION THAT MATTERS IS WHAT THE HANDLER PRODUCES.** A handler that
returns ``None``, re-raises, or records a typed failure leaves the outage
visible. A handler that returns ``0``, ``[]``, ``{}``, ``""`` or ``False``
**manufactures a reading that is indistinguishable from real data** -- and the
reader downstream has no way to tell. That is the one shape this file refuses.

So the rule is: **an exception handler in a probe may not return a falsy
datum.** Crash, or return None, or report the type -- never a number somebody
will put in a table.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"

#: Returning one of these from an ``except`` handler is the defect: each reads
#: downstream as a real, empty measurement.
_FALSY_DATA = (0, 0.0, "", False)


def _returns_falsy_datum(node: ast.AST) -> bool:
    """Does this ``except`` handler return something that reads as data?"""
    for inner in ast.walk(node):
        if not isinstance(inner, ast.Return) or inner.value is None:
            continue
        value = inner.value
        if isinstance(value, ast.Constant):
            if value.value is None:
                continue  # None is the sanctioned "unreadable" answer.
            if value.value in _FALSY_DATA or value.value is False:
                return True
        # An empty container literal is the same defect wearing a collection.
        if isinstance(value, (ast.List, ast.Tuple, ast.Set)) and not value.elts:
            return True
        if isinstance(value, ast.Dict) and not value.keys:
            return True
    return False


#: A falsy return is NOT a datum in these two roles, and the distinction was
#: forced by the guard's first run rather than anticipated.
#:
#: * ``main`` returns an EXIT CODE. ``return 0`` there means "allow", not
#:   "zero of the thing you asked about". ``pre_commit_identity_gate.main``
#:   does exactly this, deliberately, printing a warning and naming the test
#:   that still applies.
#: * A function annotated ``-> bool`` returns a VERDICT. ``return False`` from
#:   a control runner means "the controls did not pass", which is the safe
#:   direction and the opposite of a manufactured reading.
#:
#: **THIS IS THE DETECTOR'S REAL PRECISION LIMIT, WRITTEN DOWN RATHER THAN
#: REDISCOVERED**: a bare AST walk cannot tell an exit code from a count. The
#: ROLE can, and the role is legible from the name and the annotation.
_VERDICT_RETURNING_NAMES = frozenset({"main"})


def _is_verdict_role(function: ast.AST) -> bool:
    if isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if function.name in _VERDICT_RETURNING_NAMES:
            return True
        annotation = function.returns
        if isinstance(annotation, ast.Name) and annotation.id in {"bool", "int"}:
            return True
    return False


#: KNOWN AND UNFIXED, recorded so that FIXING it turns a test red rather than
#: passing in silence -- the idiom this repository already uses for a defect
#: somebody measured but does not own.
#:
#: **NOT AN EXEMPTION.** An exemption says "this is fine"; this says "this is a
#: defect, here is who owns it, and the guard will notice when it goes."
KNOWN_UNFIXED: dict[tuple[str, int], str] = {
    ("_probe_apply_flow.py", 313): (
        "await page.inner_text('main') wrapped in a bare `except Exception: "
        "return {}`, with no logging. An empty mapping flows on as 'the page "
        "drew no tracker tabs', which is indistinguishable from a failed read "
        "-- EXACTLY the outage-as-absence shape this file exists for. It is "
        "also the only one of the three first-run hits that is a real defect. "
        "Not fixed here: it is another wave's file and the remedy (return "
        "None, or let it crash) changes that probe's contract."
    ),
}


def _offenders() -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    for path in sorted(SCRIPTS.glob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        for function in ast.walk(tree):
            if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if _is_verdict_role(function):
                continue
            for node in ast.walk(function):
                if isinstance(node, ast.ExceptHandler) and _returns_falsy_datum(node):
                    out.append((path.name, node.lineno))
    return out


def test_no_probe_returns_a_falsy_datum_from_an_exception_handler():
    """THE GUARD.

    If this fires, the fix is not to widen it. Return ``None`` and let the
    caller distinguish, or let the exception propagate -- an outage that
    crashes costs one re-run, and an outage recorded as a zero costs a row
    somebody retires on it.
    """
    offenders = [site for site in _offenders() if site not in KNOWN_UNFIXED]
    assert not offenders, (
        "these exception handlers return a value that reads as real data:\n"
        + "\n".join(f"    {name}:{line}" for name, line in offenders)
        + "\n\nA zero from a failed read and a zero from an empty surface are "
        "the same number and different findings. Return None, report the "
        "exception TYPE, or let it crash -- but do not hand a caller an empty "
        "measurement it cannot tell from a real one."
    )


def test_the_known_defect_is_still_there_so_fixing_it_is_visible():
    """A KNOWN DEFECT, RECORDED SO THAT FIXING IT TURNS A TEST RED.

    This is the inverse of an exemption and the repository's own idiom for a
    defect somebody measured but does not own. If the handler is repaired --
    or the line moves -- this goes red and whoever did it removes the entry,
    which is how the record stops outliving the defect.
    """
    live = set(_offenders())
    vanished = sorted(site for site in KNOWN_UNFIXED if site not in live)
    assert not vanished, (
        f"these recorded defects are no longer detected: {vanished}. If one "
        "was FIXED, delete its KNOWN_UNFIXED entry -- the record of a defect "
        "may not outlive the defect. If the line merely MOVED, update it."
    )


def test_the_detector_fires_on_the_shapes_it_exists_for():
    """SHOWN FAILING on every falsy datum, against fixture sources.

    Parsed rather than executed -- nothing here touches a probe file, so a
    failure midway cannot leave one edited.
    """
    bad = [
        "try:\n    x = f()\nexcept Exception:\n    return 0\n",
        "try:\n    x = f()\nexcept Exception:\n    return []\n",
        "try:\n    x = f()\nexcept Exception:\n    return {}\n",
        "try:\n    x = f()\nexcept Exception:\n    return ''\n",
        "try:\n    x = f()\nexcept Exception:\n    return False\n",
        "try:\n    x = f()\nexcept Exception:\n    return ()\n",
    ]
    for source in bad:
        tree = ast.parse("def g():\n " + source.replace("\n", "\n "))
        handlers = [n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler)]
        assert handlers, source
        assert any(_returns_falsy_datum(h) for h in handlers), (
            f"the detector missed a falsy return: {source!r}"
        )


def test_the_detector_does_not_fire_on_the_sanctioned_shapes():
    """THE FALSE-POSITIVE CONTROL, and it is the half that keeps this usable.

    Every one of these is a handler this repository already ships and should
    keep shipping. A guard that flagged them would be widened into uselessness
    by the first wave that met it.
    """
    good = [
        # None is the sanctioned "unreadable" answer -- not a zero.
        "try:\n    x = f()\nexcept Exception:\n    return None\n",
        # Re-raising.
        "try:\n    x = f()\nexcept Exception:\n    raise\n",
        # Reporting the TYPE and carrying on -- the shipped pattern.
        "try:\n    x = f()\nexcept Exception as e:\n    print(type(e).__name__)\n",
        # A non-empty structure that NAMES the failure.
        "try:\n    x = f()\nexcept Exception as e:\n"
        "    return {'error': type(e).__name__}\n",
        # A try/finally with no handler at all -- the strongest form.
        "try:\n    x = f()\nfinally:\n    close()\n",
    ]
    for source in good:
        tree = ast.parse("def g():\n " + source.replace("\n", "\n "))
        handlers = [n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler)]
        assert not any(_returns_falsy_datum(h) for h in handlers), (
            f"the detector fired on a sanctioned handler: {source!r}"
        )


def test_the_scan_reaches_the_probe_directory():
    """A guard that scans nothing passes forever."""
    files = sorted(SCRIPTS.glob("*.py"))
    assert len(files) >= 50, f"only {len(files)} probe scripts found"
    parsed = 0
    for path in files:
        try:
            ast.parse(path.read_text(encoding="utf-8"))
            parsed += 1
        except (SyntaxError, OSError, UnicodeDecodeError):
            pass
    assert parsed >= 50, f"only {parsed} of {len(files)} probe scripts parsed"


@pytest.mark.parametrize("falsy", _FALSY_DATA)
def test_every_declared_falsy_datum_is_actually_detected(falsy):
    """The table and the detector cannot drift apart.

    Without this, adding a value to ``_FALSY_DATA`` that the walker never
    checks would look like coverage and provide none.
    """
    source = f"def g():\n    try:\n        x = f()\n    except Exception:\n        return {falsy!r}\n"
    tree = ast.parse(source)
    handlers = [n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler)]
    assert any(_returns_falsy_datum(h) for h in handlers), falsy
