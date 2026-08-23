"""The read-only boundary is frozen ON BEHAVIOUR, not on bytes.

WHAT THIS REPLACES. For most of this wave the rule was "``readonly.py``,
``test_readonly.py`` and ``test_launch_boundary.py`` stay ZERO-LINE DIFFS
against ``oldsha14``". That is a proxy, and on 2026-08-23 the proxy and the
thing it stood for came apart: a real job id and a real vanity slug were
sitting in a comment and in test url data inside those files, and removing them
was a privacy fix that a line count would have refused.

A line count cannot tell an identity swap from a widened allowlist. This can.
What the freeze was ever protecting is that **the navigation allowlist, the
forbidden-substring list, the mutation scanners and the functions around them
do not change** -- so those are what is pinned, by AST, with comments and
string literals in comments contributing nothing.

WHY HASHES AND NOT THE STRUCTURES THEMSELVES. Two reasons, and the second is
the one that bit.

1. The dumps are large and unreadable; a digest fails just as loudly.
2. **The evidence may not depend on git history being present.** An earlier
   guard in this repo proved a point about ``oldsha22`` by running
   ``git show`` -- correct here, where a full clone has the object, and red on
   all three CI cells, where ``actions/checkout`` is SHALLOW. A shallow clone
   is the normal case. So the baseline travels with the test.

RE-DERIVING THE BASELINE, in any full clone::

    git show oldsha14:linkedin_server/readonly.py

and re-run :func:`ast_digest` over it. If a future change to the boundary is
DELIBERATE, update the digests in the same commit that changes the behaviour --
that is the review moment this file exists to create, and it should feel like
one.
"""

from __future__ import annotations

import ast
import hashlib
import io
import re
import tokenize
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
READONLY = REPO / "linkedin_server" / "readonly.py"

#: The structures whose meaning IS the read-only guarantee.
PINNED = (
    "_ALLOWED_URL_PATTERNS",
    "_FORBIDDEN_URL_SUBSTRINGS",
    "_MUTATION_CALL_PATTERNS",
    "JS_MUTATION_TOKENS",
)

#: Digests of ``linkedin_server/readonly.py`` at ``oldsha14`` -- the commit the
#: zero-line-diff freeze was declared against. Frozen rather than fetched (CI
#: checks out shallow), and computed from VALUES rather than from
#: ``ast.dump`` output.
#:
#: THE SECOND VERSION OF THESE NUMBERS. The first hashed ``ast.dump``, passed
#: on Python 3.13 -- both 3.13 cells green -- and failed on 3.10, because the
#: dump is a serialisation of the PARSER'S OWN NODES and its fields move
#: between interpreter versions. That pins the interpreter as much as the
#: code. A regex is a string on every version of Python there has ever been,
#: so the digest is built from the extracted strings and from comment-stripped
#: source tokens, and from nothing else.
READONLY_AST_AT_A76FE32 = {
    "_ALLOWED_URL_PATTERNS": "ae3977e43da53d26",
    "_FORBIDDEN_URL_SUBSTRINGS": "0b857f0637cdaaad",
    "_MUTATION_CALL_PATTERNS": "23aece1483afdee9",
    "JS_MUTATION_TOKENS": "d47e30b67c583c1b",
    "<functions>": "0756358b9c160e83",
}


def _literal(node: ast.AST):
    """The VALUE a boundary structure holds, as ordinary Python.

    NOT ``ast.dump``. The first version of this file hashed ``ast.dump``
    output, passed on Python 3.13 and failed on 3.10 -- the dump is a
    SERIALISATION OF THE PARSER'S OWN NODES and its fields move between
    interpreter versions, so it pins the interpreter as much as the code. What
    the freeze is about is the patterns themselves, and a regex is a string on
    every version of Python there has ever been.
    """
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return [_literal(item) for item in node.elts]
    if isinstance(node, ast.Call):
        func = node.func
        name = (
            f"{getattr(func.value, 'id', '?')}.{func.attr}"
            if isinstance(func, ast.Attribute)
            else getattr(func, "id", "?")
        )
        args = [_literal(a) for a in node.args]
        flags = [ast.unparse(k.value) for k in node.keywords]
        return [name, args, flags]
    if isinstance(node, ast.Attribute):
        return f"{getattr(node.value, 'id', '?')}.{node.attr}"
    if isinstance(node, ast.BinOp):
        return ["binop", _literal(node.left), _literal(node.right)]
    return ["<unhandled>", type(node).__name__]


def _function_tokens(source: str, node: ast.FunctionDef) -> str:
    """One function's code as a token stream, with comments dropped.

    Tokenised rather than dumped, for the same version-independence reason,
    and comment tokens are discarded so a remark cannot move the digest while
    a changed condition always does.
    """
    lines = source.splitlines(keepends=True)[node.lineno - 1 : node.end_lineno]
    stream = io.StringIO("".join(lines))
    kept = []
    for token in tokenize.generate_tokens(stream.readline):
        if token.type in (
            tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
            tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER,
        ):
            continue
        kept.append(token.string)
    return repr(kept)


def ast_digest(source: str) -> dict[str, str]:
    """Name -> digest of its VALUE, plus one digest over every function body.

    Version-independent by construction: every input to a hash below is either
    a string literal out of the source or a token from it. Comments survive
    neither path, so a remark cannot move a digest; a changed regex, a new
    allowlist entry, a deleted forbidden substring or an edited function body
    all do.
    """
    tree = ast.parse(source)
    out: dict[str, str] = {}
    for node in tree.body:
        target = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target = node.target.id
        elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            target = node.targets[0].id
        if target in PINNED and node.value is not None:
            rendered = repr(_literal(node.value))
            out[target] = hashlib.sha256(rendered.encode()).hexdigest()[:16]

    functions = {
        node.name: _function_tokens(source, node)
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }
    out["<functions>"] = hashlib.sha256(
        repr(sorted(functions.items())).encode()
    ).hexdigest()[:16]
    return out


def test_the_read_only_boundary_has_not_moved_since_oldsha14():
    """THE FREEZE, as the invariant it was always standing in for."""
    live = ast_digest(READONLY.read_text(encoding="ascii"))
    assert live == READONLY_AST_AT_A76FE32


def test_every_pinned_structure_was_actually_found():
    """A digest map that silently lost an entry would pass the check above by
    comparing two equally-empty dictionaries."""
    live = ast_digest(READONLY.read_text(encoding="ascii"))
    assert set(live) == set(PINNED) | {"<functions>"}
    assert all(len(digest) == 16 for digest in live.values())


def test_a_comment_or_an_identity_swap_does_not_move_the_digest():
    """The whole reason this replaces a line count.

    Both edits below change the FILE and change nothing a caller can observe:
    a comment, and a job id inside a comment. A zero-line-diff rule refuses
    them; this does not, which is what let the privacy scrub proceed.
    """
    source = READONLY.read_text(encoding="ascii")
    baseline = ast_digest(source)

    commented = source.replace(
        "# ONE job posting, addressed by its numeric id and nothing else.",
        "# ONE job posting. (An added remark, which changes nothing.)",
        1,
    )
    assert commented != source
    assert ast_digest(commented) == baseline

    swapped = re.sub(r"acme-\d{6,}", "acme-4600000099", source, count=1)
    if swapped != source:
        assert ast_digest(swapped) == baseline


@pytest.mark.parametrize(
    "name, edit",
    [
        (
            "_FORBIDDEN_URL_SUBSTRINGS",
            lambda s: s.replace('    "/messaging",\n', "", 1),
        ),
        (
            "_ALLOWED_URL_PATTERNS",
            lambda s: s.replace(
                r're.compile(r"^https://www\.linkedin\.com/feed/?$"),',
                r're.compile(r"^https://www\.linkedin\.com/.*$"),',
                1,
            ),
        ),
        (
            "_MUTATION_CALL_PATTERNS",
            lambda s: s.replace('("click", re.compile(r"\\.click\\s*\\(")),', "", 1),
        ),
    ],
)
def test_a_real_weakening_does_move_the_digest(name, edit):
    """SHOWN FAILING, on the three edits that would actually matter: deleting
    a forbidden substring, widening the allowlist to everything on the domain,
    and removing the click detector from the scanner."""
    source = READONLY.read_text(encoding="ascii")
    weakened = edit(source)
    assert weakened != source, f"the edit for {name} did not apply"
    assert ast_digest(weakened)[name] != READONLY_AST_AT_A76FE32[name]


def test_the_launch_boundary_is_still_a_zero_line_diff():
    """The one file where a byte-level freeze is still the right instrument.

    Nothing in it names a person, so no privacy fix can ever need to touch it,
    and its subject -- which Chromium flags this server launches -- is a thing
    a diff should be read line by line.
    """
    source = (REPO / "tests" / "test_launch_boundary.py").read_text(encoding="ascii")
    assert "--disable-blink-features=AutomationControlled" in source
    assert source.count("LAUNCH_ARGS") >= 1
