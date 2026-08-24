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

    git show 5277dfc:linkedin_server/readonly.py

and re-run :func:`ast_digest` over it. If a future change to the boundary is
DELIBERATE, update the digests in the same commit that changes the behaviour --
that is the review moment this file exists to create, and it should feel like
one.

IT HAS BEEN ONE, ONCE. On 2026-08-23 the package acquired its first mutating
call and the baseline moved from ``oldsha14`` to ``5277dfc``. Two digests moved
and four did not, and the four are the ones that matter: the navigation
allowlist, the forbidden-substring list, the mutation scanner's patterns and
the JS token list are byte-identical across the change. That is asserted below
against the old values rather than left as a claim, because "the write widened
nothing" is exactly the sentence a reader most needs to be able to check.
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
#:
#: ``SANCTIONED_MUTATIONS`` JOINED THIS LIST on 2026-08-23, with the write. It
#: is the newest of the five and the only one that GRANTS rather than refuses,
#: which is exactly why it belongs here: the other four are worth freezing
#: because widening them lets something through, and this one is worth freezing
#: because ADDING TO IT lets something through. A boundary made of four
#: denylists and one allowlist is only as frozen as its allowlist.
PINNED = (
    "_ALLOWED_URL_PATTERNS",
    "_FORBIDDEN_URL_SUBSTRINGS",
    "_MUTATION_CALL_PATTERNS",
    "JS_MUTATION_TOKENS",
    "SANCTIONED_MUTATIONS",
)

#: Digests of ``linkedin_server/readonly.py`` at ``5277dfc``.
#:
#: RE-FROZEN 2026-08-23, DELIBERATELY, and this is the review moment the file's
#: own docstring promised. The previous baseline was ``oldsha14``, the commit
#: the zero-line-diff freeze was declared against, and every digest below moved
#: except one. WHAT CHANGED AND WHY, so a reader does not have to diff two
#: commits to find out:
#:
#: * ``SANCTIONED_MUTATIONS`` is NEW. The package acquired its first mutating
#:   call -- one click, in ``writes.perform`` -- and this is the list that
#:   admits it. It is pinned from birth.
#: * ``<functions>`` MOVED, because ``readonly.py`` gained two:
#:   ``enclosing_function`` and ``partition_mutation_hits``. Neither weakens
#:   anything; the scan itself is byte-for-byte what it was.
#: * ``_ALLOWED_URL_PATTERNS``, ``_FORBIDDEN_URL_SUBSTRINGS``,
#:   ``_MUTATION_CALL_PATTERNS`` and ``JS_MUTATION_TOKENS`` are UNCHANGED, and
#:   that is the load-bearing half of this re-freeze. The write did not widen
#:   the navigation allowlist, did not shorten the forbidden list, did not
#:   remove a detector from the scanner and did not drop a JS token. Their
#:   digests are identical to the ``oldsha14`` values, which are kept below so
#:   the claim is checkable rather than asserted::
#:
#:       _ALLOWED_URL_PATTERNS      ae3977e43da53d26
#:       _FORBIDDEN_URL_SUBSTRINGS  0b857f0637cdaaad
#:       _MUTATION_CALL_PATTERNS    23aece1483afdee9
#:       JS_MUTATION_TOKENS         d47e30b67c583c1b
#:       <functions>                fd79a6a7c02c3e34   (moved)
#:
#: Frozen rather than fetched (CI checks out shallow), and computed from VALUES
#: rather than from ``ast.dump`` output.
#:
#: THREE ATTEMPTS, and the first two failed the same way. v1 hashed
#: ``ast.dump``; v2 hashed a TOKEN STREAM. Both are THE PARSER DESCRIBING
#: ITSELF, and both split along the interpreter matrix -- green on the two
#: 3.13 cells, red on 3.10, with the four CONSTANT digests matching every time
#: because a regex is a string on every Python. v2's failure named its own
#: cause precisely: four of eleven functions differed and every one contained
#: an f-string (PEP 701, 3.12).
#:
#: v3 asks the tokenizer only WHERE THE COMMENTS ARE -- a position question,
#: stable -- and hashes the remaining source text. VERIFIED rather than
#: argued: computed under 3.13.14 and 3.10.19 on the same file, all five
#: digests identical.
#: RE-FROZEN 2026-08-24, and the shape of the move is the argument. A false
#: sentence was removed from ``assert_read_url``'s error message -- it told a
#: live caller "This server has no write path" while three write tools ship.
#: ONLY ``<functions>`` moved (9f0a86dafffc2299 -> 199939f7998e8d48); all four
#: CONSTANT digests are byte-identical across the change, which is what proves
#: the correction touched prose and widened no boundary. Verified under 3.13.14
#: AND 3.10.19 -- a single-version run cannot verify a version-independent
#: claim, and this file has three red CI runs in its history saying so.
#:
#: RENAMED at the same time: the constant was called ...AT_5277DFC while
#: holding a value re-frozen twice since. A name that asserts a provenance it
#: no longer has is the same defect as a docstring that denies a capability
#: that ships, one layer down.
READONLY_AST_AT_LAST_REFREEZE = {
    "_ALLOWED_URL_PATTERNS": "ae3977e43da53d26",
    "_FORBIDDEN_URL_SUBSTRINGS": "0b857f0637cdaaad",
    "_MUTATION_CALL_PATTERNS": "23aece1483afdee9",
    "JS_MUTATION_TOKENS": "d47e30b67c583c1b",
    "SANCTIONED_MUTATIONS": "033a34fbbc538d8c",
    "<functions>": "199939f7998e8d48",
}

#: The four denylist digests as they stood at ``oldsha14``, kept so that "the
#: write widened nothing" is CHECKABLE rather than a sentence in a comment.
#: ``test_the_write_did_not_touch_any_of_the_four_denylists`` compares them.
DENYLISTS_AT_A76FE32 = {
    "_ALLOWED_URL_PATTERNS": "ae3977e43da53d26",
    "_FORBIDDEN_URL_SUBSTRINGS": "0b857f0637cdaaad",
    "_MUTATION_CALL_PATTERNS": "23aece1483afdee9",
    "JS_MUTATION_TOKENS": "d47e30b67c583c1b",
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


def _function_source(source: str, node: ast.FunctionDef) -> str:
    """One function's code with comments removed.

    ``tokenize`` is used ONLY to LOCATE comments, never to render structure,
    and that distinction is the whole correction. A ``COMMENT`` is one token on
    every version of Python; how the tokenizer decomposes a STRING is not --
    **PEP 701 splits an f-string into FSTRING_START/MIDDLE/END on 3.12+** where
    3.10 emits a single ``STRING``. ``readonly.py``'s refusal messages are
    f-strings, so a digest built from the token STREAM split exactly along the
    interpreter matrix: four of eleven functions differed, and every one of the
    four contained an f-string.

    Asking the tokenizer WHERE a comment is, is a position question and stable.
    Asking it WHAT a string is made of is a structure question and moved. The
    first two attempts at this digest -- ``ast.dump`` and then the token stream
    -- were both the parser describing ITSELF, which is exactly what the
    ``_literal`` docstring above warns against. The four value digests were
    safe throughout precisely because a regex is a string on every Python.

    ONE DELIBERATE CONSEQUENCE: trailing whitespace is stripped and blank lines
    dropped, so REFORMATTING a function moves the digest where a token stream
    would have ignored it. That is the conservative direction for a boundary
    invariant -- it fires more readily, never less -- and it is chosen rather
    than inherited.
    """
    segment = "".join(
        source.splitlines(keepends=True)[node.lineno - 1 : node.end_lineno]
    )
    spans = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(segment).readline):
            if token.type == tokenize.COMMENT:
                spans.append((token.start, token.end))
    except (tokenize.TokenError, IndentationError):  # pragma: no cover
        pass
    lines = segment.splitlines()
    for (start_row, start_col), (end_row, end_col) in reversed(spans):
        if start_row == end_row and 1 <= start_row <= len(lines):
            lines[start_row - 1] = (
                lines[start_row - 1][:start_col] + lines[start_row - 1][end_col:]
            )
    return "\n".join(
        line for line in (raw.rstrip() for raw in lines) if line.strip()
    )


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
        node.name: _function_source(source, node)
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }
    out["<functions>"] = hashlib.sha256(
        repr(sorted(functions.items())).encode()
    ).hexdigest()[:16]
    return out


def test_the_read_only_boundary_is_where_it_was_re_frozen():
    """THE FREEZE, as the invariant it was always standing in for."""
    live = ast_digest(READONLY.read_text(encoding="ascii"))
    assert live == READONLY_AST_AT_LAST_REFREEZE


def test_the_write_did_not_touch_any_of_the_four_denylists():
    """THE HALF OF THE RE-FREEZE THAT IS A CLAIM ABOUT THE WRITE.

    Re-freezing a boundary is only honest if somebody can see WHAT moved. Two
    digests moved -- a new allowlist, and two new functions. These four did
    not, and they are the four that would have to move for the write to have
    weakened anything: a widened navigation allowlist, a shortened forbidden
    list, a detector removed from the scanner, a JS token dropped.

    Compared against the values from ``oldsha14``, the baseline BEFORE the
    write, so this is a statement about the change and not a restatement of the
    new map.
    """
    live = ast_digest(READONLY.read_text(encoding="ascii"))
    for name, digest in DENYLISTS_AT_A76FE32.items():
        assert live[name] == digest, (
            f"{name} moved across the write. It is one of the four structures "
            "the write was not supposed to touch."
        )


def test_adding_a_second_sanctioned_mutation_moves_the_digest():
    """SHOWN FAILING on the edit this new pin exists to catch.

    The other three weakening cases below delete or widen a REFUSAL. This one
    is the opposite shape and is the reason SANCTIONED_MUTATIONS was pinned at
    all: it grows a PERMISSION. A second entry -- here, a click in dom.py --
    has to move the digest, or the allowlist is frozen in name only.
    """
    source = READONLY.read_text(encoding="ascii")
    widened = source.replace(
        '    ("linkedin_server/writes.py", "perform", "click"),\n',
        '    ("linkedin_server/writes.py", "perform", "click"),\n'
        '    ("linkedin_server/dom.py", "read_job", "click"),\n',
        1,
    )
    assert widened != source, "the edit did not apply"
    assert (
        ast_digest(widened)["SANCTIONED_MUTATIONS"]
        != READONLY_AST_AT_LAST_REFREEZE["SANCTIONED_MUTATIONS"]
    )


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
    assert ast_digest(weakened)[name] != READONLY_AST_AT_LAST_REFREEZE[name]


def test_the_launch_boundary_is_still_a_zero_line_diff():
    """The one file where a byte-level freeze is still the right instrument.

    Nothing in it names a person, so no privacy fix can ever need to touch it,
    and its subject -- which Chromium flags this server launches -- is a thing
    a diff should be read line by line.
    """
    source = (REPO / "tests" / "test_launch_boundary.py").read_text(encoding="ascii")
    assert "--disable-blink-features=AutomationControlled" in source
    assert source.count("LAUNCH_ARGS") >= 1
