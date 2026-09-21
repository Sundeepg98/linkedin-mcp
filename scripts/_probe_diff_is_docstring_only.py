#!/usr/bin/env python3
"""Is the difference between two revisions of a module EXECUTABLE, or is it prose?

WHY THIS EXISTS. On 2026-09-21 a red CI shard had to be attributed to one of two
commits, and the candidate commit's only source change was 47 lines in
``linkedin_server/server.py``. A textual diff cannot answer "did the code
change": in this repository a docstring rewrite is routinely larger than a
behaviour change, and the two look identical to ``git diff --stat``. Reading the
hunks by eye is how a reviewer concludes "looks like comments" and is wrong once.

So the question is asked of the AST instead. Both revisions are parsed, every
docstring is DELETED from both trees, and what is left is compared. A docstring
here means the leading string expression of a Module, ClassDef, FunctionDef or
AsyncFunctionDef -- the only string constants Python treats specially. Comments
never reach the AST at all, so they need no handling.

WHAT IT ANSWERS AND WHAT IT DOES NOT. A verdict of IDENTICAL means: no statement,
expression, signature, decorator, default or constant differs. It does NOT mean
the two files behave identically in every respect -- a change to a docstring is
observable through ``help()``, ``__doc__`` and any test that asserts on prose,
and this repository has such tests. It means the change cannot alter control
flow or a value, which is the question a failure investigation is asking.

USAGE
    python scripts/_probe_diff_is_docstring_only.py OLD.py NEW.py [--name-a A --name-b B]
    python scripts/_probe_diff_is_docstring_only.py --self-test

Exit status is 0 when the two are identical as code and 1 when they are not, so
this composes into a shell pipeline. ``--self-test`` exits 0 when the probe
demonstrates that it CAN return both verdicts.

Pair it with git to compare two commits without a checkout:
    git show A:path/to/mod.py > /tmp/a.py
    git show B:path/to/mod.py > /tmp/b.py
    python scripts/_probe_diff_is_docstring_only.py /tmp/a.py /tmp/b.py
"""

from __future__ import annotations

import argparse
import ast
import sys

DOC_HOLDERS = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def strip_docstrings(tree: ast.AST) -> ast.AST:
    """Delete every docstring in place, leaving a ``pass`` if a body empties.

    The ``or [ast.Pass()]`` matters and is not defensive noise: a function whose
    entire body is a docstring becomes syntactically invalid with the docstring
    removed, and ``ast.dump`` of an empty body would compare equal to another
    empty body regardless of what the two docstrings said. Substituting ``pass``
    keeps every such function distinguishable from a genuinely empty one.
    """
    for node in ast.walk(tree):
        if not isinstance(node, DOC_HOLDERS):
            continue
        body = node.body
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            node.body = body[1:] or [ast.Pass()]
    return tree


def top_level_defs(tree: ast.AST) -> dict[str, str]:
    """Each top-level def/class, dumped, so a difference can be NAMED.

    A bare "DIFFERENT" sends a reader back to the diff they were trying to
    avoid reading. Naming the function is the whole value of doing this
    structurally rather than textually.
    """
    out: dict[str, str] = {}
    for node in getattr(tree, "body", []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[node.name] = ast.dump(node)
    return out


def parse_stripped(text: str) -> ast.AST:
    return strip_docstrings(ast.parse(text))


def compare(left_text: str, right_text: str) -> tuple[bool, dict]:
    left, right = parse_stripped(left_text), parse_stripped(right_text)
    ldefs, rdefs = top_level_defs(left), top_level_defs(right)
    detail = {
        "only_left": sorted(set(ldefs) - set(rdefs)),
        "only_right": sorted(set(rdefs) - set(ldefs)),
        "changed": sorted(n for n in set(ldefs) & set(rdefs) if ldefs[n] != rdefs[n]),
        "present_both": sorted(set(ldefs) & set(rdefs)),
        "n_left": len(ldefs),
        "n_right": len(rdefs),
    }
    return ast.dump(left) == ast.dump(right), detail


def read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def report(same: bool, detail: dict, name_a: str, name_b: str, focus: str | None) -> None:
    print(
        "WHOLE-MODULE AST, docstrings stripped: %s"
        % ("IDENTICAL" if same else "DIFFERENT")
    )
    print("top-level defs: %s=%d  %s=%d" % (name_a, detail["n_left"], name_b, detail["n_right"]))
    print("defs only in %s: %s" % (name_a, detail["only_left"] or "none"))
    print("defs only in %s: %s" % (name_b, detail["only_right"] or "none"))
    print("defs whose CODE changed: %s" % (detail["changed"] or "none"))
    if focus:
        # ABSENT IS NOT UNCHANGED, and collapsing the two is how a typo in
        # --focus reads as reassurance. A name nobody defined on either side
        # would otherwise print the same word as a name that was compared.
        if focus in detail["changed"]:
            state = "CHANGED"
        elif focus in detail["present_both"]:
            state = "UNCHANGED"
        elif focus in detail["only_left"]:
            state = "PRESENT ONLY IN %s" % name_a
        elif focus in detail["only_right"]:
            state = "PRESENT ONLY IN %s" % name_b
        else:
            state = "NOT A TOP-LEVEL DEF IN EITHER REVISION -- nothing was compared"
        print("%s: %s" % (focus, state))


# ---------------------------------------------------------------------------
# THE CONTROL. A comparator that answers IDENTICAL certifies nothing until it
# has been shown answering DIFFERENT, on a change small enough that a textual
# diff of the same pair would be one line.
# ---------------------------------------------------------------------------

_BASE = '''
"""Module prose."""


def keep(value):
    """Old prose about keep."""
    if isinstance(value, KeyError):
        return 1
    return 2


class Holder:
    """Old prose about Holder."""

    def method(self):
        """Old prose about method."""
        return 3
'''

_PROSE_ONLY = _BASE.replace("Old prose", "Completely rewritten and much longer prose")

_ONE_TOKEN = _BASE.replace("isinstance(value, KeyError)", "isinstance(value, ValueError)")


def self_test() -> int:
    ok = True

    same, detail = compare(_BASE, _PROSE_ONLY)
    print("CONTROL 1 -- every docstring rewritten, no code touched")
    report(same, detail, "base", "prose_only", None)
    if not same:
        print("  UNEXPECTED: prose-only rewrite reported as a code change")
        ok = False
    print()

    same, detail = compare(_BASE, _ONE_TOKEN)
    print("CONTROL 2 -- one exception type changed, docstrings untouched")
    report(same, detail, "base", "one_token", "keep")
    if same or detail["changed"] != ["keep"]:
        print("  UNEXPECTED: a real one-token code change was not caught, or was misattributed")
        ok = False
    print()

    same, detail = compare(_BASE, _BASE)
    print("CONTROL 3 -- a revision against itself")
    report(same, detail, "base", "base", None)
    if not same:
        print("  UNEXPECTED: a file differs from itself")
        ok = False
    print()

    # CONTROL 4 exists because of a defect this probe SHIPPED WITH. --focus
    # first printed "unchanged-or-absent" for any name not in the changed list,
    # so a misspelled --focus produced the same reassuring word as a genuine
    # comparison. A focus line has to be able to say it compared nothing.
    same, detail = compare(_BASE, _ONE_TOKEN)
    print("CONTROL 4 -- --focus on a name that exists in neither revision")
    report(same, detail, "base", "one_token", "no_such_function")
    print("CONTROL 4b -- --focus on a name that exists and did not change")
    report(same, detail, "base", "one_token", "Holder")
    print()

    print("SELF-TEST: %s" % ("PASS -- the probe returns both verdicts" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("old", nargs="?", help="the earlier revision")
    parser.add_argument("new", nargs="?", help="the later revision")
    parser.add_argument("--name-a", default="OLD")
    parser.add_argument("--name-b", default="NEW")
    parser.add_argument(
        "--focus", help="a top-level def to report on by name, whatever the verdict"
    )
    parser.add_argument(
        "--self-test", action="store_true", help="show the probe returning both verdicts"
    )
    args = parser.parse_args(argv[1:])

    if args.self_test:
        return self_test()
    if not (args.old and args.new):
        parser.error("two paths are required unless --self-test is given")

    same, detail = compare(read(args.old), read(args.new))
    report(same, detail, args.name_a, args.name_b, args.focus)
    return 0 if same else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
