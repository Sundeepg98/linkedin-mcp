"""Who can reach ONE module-level function? An AST caller census, not a grep.

WHY THIS EXISTS. READ-CARDS-DELETION (2026-11-26) ruled that
``server._read_cards`` is deleted "if an AST caller census shows no caller", and
named the two channels a grep is weakest on: a call through an ATTRIBUTE and a
call through ``getattr``. A grep for the name also convicts a same-named
function in another module (``search_vertical_results._read_cards`` is one),
and passes a caller that spells the module through an alias. This reads every
file's syntax tree and BINDS each reference before it counts it.

WHAT COUNTS AS A CALLER (each a reference that can reach the target):

  DIRECT      a Load of the bare name in the defining module (a call, or the
              function passed as a value), or of a name imported from it
  ATTRIBUTE   ``<alias>.<name>``, where ``<alias>`` is bound to the defining
              module by any import spelling, or the full dotted chain
  GETATTR     ``getattr`` / ``hasattr`` / ``setattr`` / ``delattr`` on such an
              alias with the literal name
  IMPORT      ``from <module> import <name>`` (relative spellings resolved)
  UNRESOLVED  ``<receiver>.<name>`` whose receiver the census cannot bind to
              any module: COUNTED as a possible caller, never dropped

WHAT IS LISTED BUT NOT COUNTED:

  OTHER       ``<alias>.<name>`` where ``<alias>`` is bound to a DIFFERENT
              module: a same-named function, not this one
  STRING      a string constant containing the name -- a monkeypatch dotted
              path, ``vars(m)["name"]``, a table of function names, prose. A
              string cannot be bound statically, so each is printed with its
              line for a reader to classify; the record says how each was.

WHAT IT CANNOT SEE: a name assembled at runtime (``"_read_" + "cards"``) and
a module reached through a value it cannot bind (``m = load(); m.<name>``,
which lands in UNRESOLVED, counted). Files: ``git ls-files '*.py'`` under the
repo root (the tracked tree), plus every ``.py`` under each ``--extra`` root
(a gitignored runner that imports the package, for one).

Usage:
    python scripts/caller_census.py linkedin_server.server _read_cards \
        [--repo .] [--extra <dir> ...]

Exit 0 when nothing COUNTED was found (the verdict line reads NO CALLER), 1
otherwise. Its controls are tests/test_caller_census.py.
"""
from __future__ import annotations

import argparse
import ast
import os
import subprocess
import sys
from typing import Iterable, NamedTuple

ATTR_FUNCS = frozenset({"getattr", "hasattr", "setattr", "delattr"})
#: The kinds that can reach the target. A PARSE-FAILED file is counted too:
#: a file the census could not read is not a file it cleared.
COUNTED = ("DIRECT", "ATTRIBUTE", "GETATTR", "IMPORT", "UNRESOLVED", "PARSE-FAILED")
ORDER = ("DEF",) + COUNTED + ("OTHER", "STRING")


class Hit(NamedTuple):
    kind: str
    rel: str
    line: int
    what: str


def _absolute(node: ast.ImportFrom, rel: str) -> str | None:
    """The dotted module an ImportFrom names; a relative one is resolved
    against the importing file's own package (``rel`` is its repo path)."""
    if node.level == 0:
        return node.module
    parts = rel.replace("\\", "/").split("/")[:-1]
    if node.level > 1:
        parts = parts[: len(parts) - (node.level - 1)]
    base = ".".join(parts)
    if not base:
        return node.module
    return base + ("." + node.module if node.module else "")


def _module_bindings(tree: ast.AST, rel: str) -> tuple[dict[str, str], set[str]]:
    """local name -> the module it is bound to, and the dotted chains that
    spell a module because ``import a.b.c`` was written."""
    names: dict[str, str] = {}
    chains: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.asname:
                    names[a.asname] = a.name
                else:
                    chains.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            mod = _absolute(node, rel)
            if not mod:
                continue
            for a in node.names:
                # ``from a.b import c`` may bind a MODULE c; whether it does is
                # not knowable without the tree, so the dotted guess is kept
                # and only ever compared against a module name.
                names[a.asname or a.name] = mod + "." + a.name
    return names, chains


def _dotted(node: ast.AST) -> str | None:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def _receiver_module(recv: str | None, names: dict[str, str],
                     chains: set[str]) -> str | None:
    if recv is None:
        return None
    if any(recv == c or recv.startswith(c + ".") for c in chains):
        return recv                       # ``import a`` makes ``a.b.c`` a spelling
    head, _, rest = recv.partition(".")
    if head in names:
        return names[head] + ("." + rest if rest else "")
    return None


def scan(source: str, rel: str, target: str, name: str) -> list[Hit]:
    """Every reference to ``target.name`` in one file's source."""
    try:
        tree = ast.parse(source, rel)
    except (SyntaxError, ValueError) as exc:
        return [Hit("PARSE-FAILED", rel, 0, type(exc).__name__)]
    hits: list[Hit] = []
    names, chains = _module_bindings(tree, rel)
    own = rel.replace("\\", "/") == target.replace(".", "/") + ".py"
    imported_as: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and _absolute(node, rel) == target:
            for a in node.names:
                if a.name == name:
                    imported_as.add(a.asname or a.name)
                    hits.append(Hit("IMPORT", rel, node.lineno, "from %s import %s%s" % (
                        target, name, " as " + a.asname if a.asname else "")))
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if (own and node.id == name) or node.id in imported_as:
                hits.append(Hit("DIRECT", rel, node.lineno, node.id))
        elif isinstance(node, ast.Attribute) and node.attr == name:
            recv = _dotted(node.value)
            mod = _receiver_module(recv, names, chains)
            if mod == target:
                hits.append(Hit("ATTRIBUTE", rel, node.lineno, "%s.%s" % (recv, name)))
            elif mod is not None:
                hits.append(Hit("OTHER", rel, node.lineno, "%s.%s (bound to %s)" % (
                    recv, name, mod)))
            else:
                hits.append(Hit("UNRESOLVED", rel, node.lineno, "%s.%s" % (
                    recv or "<expression>", name)))
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id in ATTR_FUNCS and len(node.args) >= 2
              and isinstance(node.args[1], ast.Constant) and node.args[1].value == name):
            recv = _dotted(node.args[0])
            mod = _receiver_module(recv, names, chains)
            kind = "GETATTR" if mod == target else ("OTHER" if mod else "UNRESOLVED")
            hits.append(Hit(kind, rel, node.lineno, "%s(%s, %r)" % (node.func.id, recv, name)))
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and name in node.value:
            text = " ".join(node.value.split())
            hits.append(Hit("STRING", rel, node.lineno,
                            text if len(text) <= 80 else text[:77] + "..."))
    if own:
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
                hits.append(Hit("DEF", rel, node.lineno, "the definition"))
    return hits


def tracked_files(repo: str) -> list[str]:
    out = subprocess.run(["git", "-C", repo, "ls-files", "-z", "*.py"],
                         capture_output=True, text=True, check=True).stdout
    return [p for p in out.split("\0") if p]


def files_under(root: str) -> list[str]:
    found = []
    for d, dirs, fs in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in ("__pycache__", ".git", "venv", ".venv"))
        found.extend(os.path.relpath(os.path.join(d, f), root) for f in sorted(fs)
                     if f.endswith(".py"))
    return found


def census(target: str, name: str, *, repo: str = ".", extra: Iterable[str] = (),
           tracked: bool = True) -> tuple[list[Hit], int]:
    """(hits, files read). ``tracked=False`` walks ``repo`` instead of asking git."""
    hits: list[Hit] = []
    roots = [(repo, tracked_files(repo) if tracked else files_under(repo), "")]
    roots += [(r, files_under(r), "extra:") for r in extra]
    n = 0
    for root, rels, tag in roots:
        for rel in rels:
            n += 1
            try:
                with open(os.path.join(root, rel), encoding="utf-8") as fh:
                    source = fh.read()
            except (OSError, UnicodeDecodeError) as exc:
                hits.append(Hit("PARSE-FAILED", tag + rel, 0, type(exc).__name__))
                continue
            hits.extend(h._replace(rel=tag + h.rel) for h in
                        scan(source, rel.replace("\\", "/"), target, name))
    return hits, n


def counted(hits: Iterable[Hit]) -> list[Hit]:
    return [h for h in hits if h.kind in COUNTED]


def render(hits: list[Hit], n: int, target: str, name: str) -> str:
    lines = ["caller census of %s.%s: %d file(s) read" % (target, name, n)]
    for h in sorted(hits, key=lambda h: (ORDER.index(h.kind), h.rel, h.line)):
        lines.append("%-12s %s:%d  %s" % (h.kind, h.rel, h.line, h.what))
    tally = {k: sum(1 for h in hits if h.kind == k) for k in ORDER}
    lines.append("counts: " + ", ".join("%s %d" % kv for kv in tally.items()))
    c = len(counted(hits))
    lines.append("VERDICT: " + ("NO CALLER" if c == 0 else "%d POSSIBLE CALLER(S)" % c))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("target", help="the defining module, dotted (linkedin_server.server)")
    ap.add_argument("name", help="the function's name")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--extra", action="append", default=[],
                    help="another root whose every .py is read (repeatable)")
    args = ap.parse_args(argv)
    hits, n = census(args.target, args.name, repo=args.repo, extra=args.extra)
    print(render(hits, n, args.target, args.name))
    return 0 if not counted(hits) else 1


if __name__ == "__main__":
    sys.exit(main())
