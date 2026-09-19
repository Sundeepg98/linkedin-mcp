"""Does this repository still compile on the OLDEST Python it claims to support?

WHY THIS EXISTS, AND IT IS A MEASURED WHY. On 2026-09-19, run 35441013901 went
red with fourteen failures on ubuntu py3.10 spread over four test files. Ten of
them were ONE defect: ``scripts/_probe_add_section_menu.py`` put an escaped
quote inside an f-string EXPRESSION, which PEP 701 legalised in 3.12 and which
is a SyntaxError before it. The file did not parse on 3.10 at all, so every
guard in this suite that walks the package with ``ast.parse`` -- the navigation
rule, the page-text sink rule, the goto census, the sanitiser-claimant sweep,
the relation-definition check -- raised SyntaxError instead of returning a
verdict.

None of those ten failures was reporting a rule violation. They were reporting
that the guard could not read the file. Five instruments stopped running and
the symptom looked like ten unrelated reds.

**AND THE BOX COULD NOT SEE ANY OF IT.** Local Python is 3.13, where the file
parses fine. ``ast.parse(..., feature_version=(3, 10))`` does NOT help --
measured: it accepts the construct, because ``feature_version`` never reached
the f-string tokenizer PEP 701 replaced. So the only instrument that can catch
this before CI does is one that reads the SOURCE for constructs the baseline
interpreter refuses, rather than one that asks the running interpreter.

WHAT THIS IS NOT. It is not a general 3.10 compatibility checker and does not
pretend to be: it knows two constructs. Both are f-string forms, because that
is where PEP 701 moved the line and it is the only part of the grammar this
repository has actually tripped over. A file it passes may still fail to
compile on 3.10 for a reason nobody here has met yet -- and when that happens,
the repair is to add the rule, with the offending line as its control.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

#: Version below which PEP 701 does not apply. Both rules below are about
#: constructs legal from 3.12 and refused before it, so a repository whose
#: floor is already 3.12 has nothing to check.
PEP_701 = (3, 12)

BACKSLASH = "backslash-in-f-string-expression"
REUSED_QUOTE = "enclosing-quote-reused-in-f-string-expression"

#: Read by both the pyproject reader and the workflow reader so a drifting pin
#: is a failure of this module and not of whichever caller noticed first.
_REQUIRES = re.compile(r'^\s*requires-python\s*=\s*["\']>=\s*(\d+)\.(\d+)', re.M)
_MATRIX_VERSION = re.compile(r'"python-version"\s*:\s*"(\d+)\.(\d+)"')


def minimum_python_from_pyproject(repo: Path) -> tuple[int, int]:
    """The floor this package DECLARES."""
    text = (repo / "pyproject.toml").read_text(encoding="utf-8")
    found = _REQUIRES.search(text)
    if not found:
        raise SystemExit("pyproject.toml has no `requires-python = \">=X.Y\"`")
    return int(found.group(1)), int(found.group(2))


def python_versions_in_ci(repo: Path) -> list[tuple[int, int]]:
    """Every version the matrix actually RUNS, lowest first.

    Declared and run are two different facts, and a lint that reads only one of
    them is pinned to a number nobody tests.
    """
    text = (repo / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    return sorted({(int(a), int(b)) for a, b in _MATRIX_VERSION.findall(text)})


def tracked_python_files(repo: Path) -> list[Path]:
    """Tracked ``.py`` only.

    Untracked is deliberately out of scope: this rule is about what the
    repository ships, and a scratch file in the tree is nobody's build.
    """
    listed = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "*.py"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    return [repo / name for name in listed]


def _quote_of(segment: str) -> str:
    """The quote sequence that TERMINATES this f-string literal.

    Triple quotes matter: inside ``f\"\"\"...\"\"\"`` a lone ``\"`` in the
    expression never terminated anything, so flagging it would be a false
    positive on every version.
    """
    body = segment.lstrip("fFrRbB")
    for quote in ('"""', "'''", '"', "'"):
        if body.startswith(quote):
            return quote
    return ""


def _segment(lines: list[str], node: ast.AST) -> str:
    """``ast.get_source_segment`` with the line split hoisted out of the loop.

    The stdlib function re-splits the WHOLE FILE on every call, and this scan
    calls it once per f-string and once per expression inside it: 31.4s over
    311 files, measured, which is real money on a suite this size. The byte
    encode/decode is not decoration -- ``col_offset`` is a UTF-8 BYTE offset,
    so slicing the str directly would be wrong on any non-ASCII line, and
    silently wrong in the direction that reads as a clean file.

    test_the_fast_segment_agrees_with_the_stdlib pins the equivalence.
    """
    first, last = node.lineno - 1, node.end_lineno - 1

    def cut(line: str, start: int | None = None, end: int | None = None) -> str:
        return line.encode("utf-8")[start:end].decode("utf-8")

    if first == last:
        return cut(lines[first], node.col_offset, node.end_col_offset)
    out = [cut(lines[first], node.col_offset)]
    out.extend(lines[first + 1 : last])
    out.append(cut(lines[last], None, node.end_col_offset))
    return "".join(out)


def violations(source: str, label: str = "<source>") -> list[tuple[int, str, str]]:
    """Every construct in ``source`` that a pre-PEP-701 interpreter refuses.

    Returns ``(line, rule, expression text)``, one per offending expression,
    so a failure names the line and shows the reader the thing itself rather
    than a count.

    Raises ``SyntaxError`` if ``source`` does not parse HERE -- which is a
    different and louder problem, and the caller is expected to report it as
    one rather than fold it in.
    """
    tree = ast.parse(source, filename=label)
    lines = source.splitlines(keepends=True)
    found: list[tuple[int, str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.JoinedStr):
            continue
        quote = _quote_of(_segment(lines, node))
        for part in node.values:
            if not isinstance(part, ast.FormattedValue):
                continue
            expression = _segment(lines, part.value)
            if "\\" in expression:
                found.append((part.value.lineno, BACKSLASH, expression))
            elif quote and quote in expression:
                found.append((part.value.lineno, REUSED_QUOTE, expression))
    return sorted(set(found))


def scan(repo: Path) -> tuple[list[str], list[tuple[str, int, str, str]]]:
    """``(files that do not parse here, violations)`` over the tracked tree."""
    unparseable: list[str] = []
    offences: list[tuple[str, int, str, str]] = []
    for path in tracked_python_files(repo):
        name = path.relative_to(repo).as_posix()
        source = path.read_text(encoding="utf-8")
        try:
            for line, rule, text in violations(source, name):
                offences.append((name, line, rule, text))
        except SyntaxError as error:
            unparseable.append(f"{name}:{error.lineno}: {error.msg}")
    return unparseable, offences


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    floor = minimum_python_from_pyproject(repo)
    unparseable, offences = scan(repo)

    if args.json:
        print(
            json.dumps(
                {
                    "floor": list(floor),
                    "applies": floor < PEP_701,
                    "unparseable": unparseable,
                    "violations": [list(item) for item in offences],
                },
                indent=2,
            )
        )
    else:
        print(f"floor {floor[0]}.{floor[1]}  files {len(tracked_python_files(repo))}")
        for line in unparseable:
            print(f"  DOES NOT PARSE HERE  {line}")
        for name, line, rule, text in offences:
            print(f"  {rule}  {name}:{line}  {text}")
        if not unparseable and not offences:
            print("  clean")

    if floor >= PEP_701:
        return 1 if unparseable else 0
    return 1 if (unparseable or offences) else 0


if __name__ == "__main__":
    sys.exit(main())
