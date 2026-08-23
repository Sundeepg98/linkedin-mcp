"""Importing a script must not DO anything.

WHY THIS FILE EXISTS, and it was found by stepping on it.
``scripts/_build_follow_fixtures.py`` ended in a bare ``main()`` at module
scope, and ``main()`` WRITES ``tests/fixtures/``. So importing that module --
to read one substitution table, to exercise one helper, to let a guard walk its
syntax tree -- silently rebuilt four committed fixtures as a side effect. It
fired exactly once, during this wave's own extraction pass, and regenerated
them byte-identically. That was luck, not design: the inputs happened not to
have moved. ``scripts/_build_job_fixtures.py`` had the same ending.

THE HAZARD IS A CLASS, NOT TWO FILES. Every capture and sanitisation script in
this repo is a "run it once by hand" tool that nobody imports on purpose --
right up to the moment something does. A test, a guard, an AST walk, a
``python -c`` in a shell one-liner: any of them turns a module-scope statement
into an action nobody asked for, in a tree somebody else may be working in.
Guarding the two known ones is a fix; this is the rule.

WHAT IS CHECKED, and the honest limit of it. This is a STATIC check on the
module's own top level, deliberately, because the dynamic version would have to
EXECUTE the thing it is trying to prove safe -- and a test that rebuilds four
committed fixtures in order to discover that importing rebuilds four committed
fixtures is not a test, it is the bug with a nicer name. So:

* a bare module-level call to a plain NAME -- ``main()`` -- is refused. Calls
  on an ATTRIBUTE are not (``sys.path.insert(...)`` is how a script reaches its
  own package and writes nothing);
* any module-level statement containing a WRITE-SHAPED call is refused,
  assignment or not, so ``x = OUT.write_text(...)`` cannot slip past by wearing
  a left-hand side;
* everything under ``if __name__ == "__main__":`` is exempt BY CONSTRUCTION --
  that block is precisely the guard being asked for, and it does not run on
  import.

The limit: a module-level call to a locally-defined helper that writes through
a name this file does not recognise would pass. That is a real gap and it is
named rather than papered over. It is also narrower than the shape that
actually occurred twice.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"

#: Calls that put bytes on disk, remove them, or move them. Matched on the
#: ATTRIBUTE name, so ``p.write_text(...)``, ``shutil.rmtree(...)`` and
#: ``os.makedirs(...)`` are all caught without knowing what ``p`` is.
_WRITE_NAMES = frozenset(
    {
        "write_text",
        "write_bytes",
        "mkdir",
        "makedirs",
        "touch",
        "unlink",
        "remove",
        "rmdir",
        "rmtree",
        "rename",
        "replace",
        "symlink_to",
        "hardlink_to",
        "copy",
        "copy2",
        "copyfile",
        "copytree",
        "move",
        "chmod",
    }
)


def _writes_in(node: ast.AST) -> list[str]:
    """Write-shaped calls anywhere inside one statement."""
    found: list[str] = []
    for inner in ast.walk(node):
        if not isinstance(inner, ast.Call):
            continue
        func = inner.func
        if isinstance(func, ast.Attribute) and func.attr in _WRITE_NAMES:
            found.append(func.attr)
        elif isinstance(func, ast.Name) and func.id in _WRITE_NAMES:
            found.append(func.id)
        elif isinstance(func, ast.Name) and func.id == "open":
            mode = ""
            for arg in list(inner.args[1:2]) + [
                kw.value for kw in inner.keywords if kw.arg == "mode"
            ]:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    mode = arg.value
            if any(character in mode for character in "wax+"):
                found.append(f"open(mode={mode!r})")
    return found


def module_level_effects(source: str) -> list[tuple[int, str]]:
    """Everything a module does merely by being imported.

    Only the module's OWN top level is walked. Function and class bodies are
    skipped -- defining a function that writes is not writing -- and the
    ``if __name__ == "__main__":`` block is skipped because it does not run on
    import, which is the entire point of writing it.
    """
    offences: list[tuple[int, str]] = []
    for node in ast.parse(source).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(node, ast.If) and _is_main_guard(node.test):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Name):
                offences.append(
                    (node.lineno, f"calls {func.id}() at import time")
                )
        for written in _writes_in(node):
            offences.append((node.lineno, f"{written} at import time"))
    return offences


def _is_main_guard(test: ast.AST) -> bool:
    """``__name__ == "__main__"``, written either way round."""
    if not isinstance(test, ast.Compare) or len(test.comparators) != 1:
        return False
    if not isinstance(test.ops[0], ast.Eq):
        return False
    sides = (test.left, test.comparators[0])
    names = {s.id for s in sides if isinstance(s, ast.Name)}
    values = {
        s.value for s in sides if isinstance(s, ast.Constant)
    }
    return "__name__" in names and "__main__" in values


def script_paths() -> list[str]:
    return sorted(
        str(p.relative_to(REPO)).replace("\\", "/") for p in SCRIPTS.glob("*.py")
    )


# ---------------------------------------------------------------------------
# 1. The rule
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rel", script_paths(), ids=lambda r: r)
def test_importing_a_script_does_nothing(rel):
    """No script may act merely because something imported it."""
    source = (REPO / rel).read_text(encoding="utf-8", errors="replace")
    offences = module_level_effects(source)
    assert offences == [], f"{rel}: {offences}"


def test_there_are_scripts_to_check():
    """The parametrised sweep passes vacuously on an empty glob."""
    assert len(script_paths()) >= 5


# ---------------------------------------------------------------------------
# 2. Shown failing, on synthetic source and on this repo's own history
# ---------------------------------------------------------------------------


def test_a_bare_main_at_module_scope_is_refused():
    """The exact shape that rebuilt four committed fixtures on import."""
    offences = module_level_effects("def main():\n    pass\n\n\nmain()\n")
    assert offences and "calls main() at import time" in offences[0][1]


def test_a_write_wearing_a_left_hand_side_is_refused():
    """An assignment is not a hiding place."""
    offences = module_level_effects(
        "from pathlib import Path\n"
        "OUT = Path('tests/fixtures')\n"
        "n = (OUT / 'x.html').write_text('hi')\n"
    )
    assert any("write_text" in reason for _, reason in offences), offences


def test_an_opened_file_in_write_mode_is_refused():
    offences = module_level_effects("f = open('x.html', 'w')\n")
    assert any("open(" in reason for _, reason in offences), offences


def test_the_guarded_form_is_accepted():
    """THE CONTROL. Without it every assertion above passes on a checker that
    refuses everything, and the guard this whole file asks for would itself be
    unacceptable."""
    guarded = (
        "from pathlib import Path\n"
        "\n"
        "\n"
        "def main():\n"
        "    Path('x').write_text('hi')\n"
        "\n"
        "\n"
        'if __name__ == "__main__":\n'
        "    main()\n"
    )
    assert module_level_effects(guarded) == []


def test_reading_and_path_setup_at_import_are_accepted():
    """A script may prepare itself. ``sys.path.insert`` reaches its own
    package and ``json.loads`` on a read is how the sanitisers load their key
    -- neither puts a byte on disk, and refusing them would push authors
    toward lazy globals nobody checks."""
    benign = (
        "import sys\n"
        "from pathlib import Path\n"
        "\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n"
        "KEY = Path('_audit/_key.json')\n"
        "DATA = KEY.read_text(encoding='utf-8') if KEY.exists() else ''\n"
    )
    assert module_level_effects(benign) == []


#: The tail of each build script AS IT STOOD AT ``oldsha22``, verbatim, ending
#: in the bare ``main()`` that wrote ``tests/fixtures/`` on import.
#:
#: FROZEN HERE RATHER THAN FETCHED, and that is a correction. The first version
#: of this test ran ``git show oldsha22:<path>`` and passed on this machine
#: because a full clone has the object. CI checks out SHALLOW, so the object
#: does not exist there and the test failed on all three cells with
#: ``fatal: invalid object name`` -- 2 failed, 1211 passed. A test that proves
#: something about history may not DEPEND on the history being present; a
#: shallow clone is the normal case, not the exception. So the evidence travels
#: with the test.
#:
#: Provenance was verified against the real object when this was frozen, and is
#: re-verifiable in any full clone with:
#:     git show oldsha22:scripts/_build_follow_fixtures.py | tail -5
#: A tail is a FRAGMENT, and a fragment starting mid-indentation is not a
#: module: the first frozen version began with ``    if not check(...)`` and
#: ``ast.parse`` raised IndentationError. Caught in a shallow clone before it
#: reached CI, which is the only reason this is a note and not a third red run.
#: So each entry is the file's MODULE-LEVEL SHAPE with function bodies elided.
#: The load-bearing line -- ``main()`` at column 0, as the file's final
#: statement -- is verbatim; the elision is marked.
_HISTORICAL_TAILS = {
    "scripts/_build_follow_fixtures.py": (
        "def main() -> None:\n"
        "    ...  # body elided; it ends: if not check(out_paths): SystemExit(1)\n"
        "\n"
        "\n"
        "main()\n"
    ),
    "scripts/_build_job_fixtures.py": (
        "def main() -> None:\n"
        "    ...  # body elided; it wrote three fixtures then printed a report\n"
        "\n"
        "\n"
        "main()\n"
    ),
}


@pytest.mark.parametrize("rel", sorted(_HISTORICAL_TAILS))
def test_the_frozen_evidence_is_a_parseable_module(rel):
    """Because the first frozen version was not, and only a shallow clone said so.

    Evidence that cannot be parsed proves nothing about a parser, and the two
    tests below would then fail for a reason that has nothing to do with the
    rule they exist to exercise.
    """
    ast.parse(_HISTORICAL_TAILS[rel])


@pytest.mark.parametrize("rel", sorted(_HISTORICAL_TAILS))
def test_it_fires_on_this_repos_own_history(rel):
    """THE STRONGEST FORM: run the rule at the shape that actually shipped.

    Both scripts ended in a bare ``main()`` at ``oldsha22``, and both wrote
    ``tests/fixtures/`` from it. A checker proven only against source written
    to be caught proves less than one proven against the thing that happened.
    """
    offences = module_level_effects(_HISTORICAL_TAILS[rel])
    assert any("calls main()" in reason for _, reason in offences), (rel, offences)


@pytest.mark.parametrize("rel", sorted(_HISTORICAL_TAILS))
def test_and_the_same_file_is_clean_today(rel):
    """So the pair above records a FIX rather than a tolerated finding."""
    assert module_level_effects((REPO / rel).read_text(encoding="utf-8")) == []
