"""Does anything in this package ever build a ``/in/<not-me>/details/`` url?

THE QUESTION IS A PRECONDITION FOR A RULING, NOT A CHANGE. The self-profile
details pattern takes ``[A-Za-z0-9\\-_%]+`` for its member segment, not ``me``,
so ``/in/<a-third-party>/details/skills/`` is on the read allowlist and always
has been. Sixteen lines below it the intro editor is deliberately restricted to
the ``/in/me/`` form, with a MEASURED reason: ``linkedin_who_viewed_me``
establishes that loading a member's profile leaves them a durable record in
their own viewer list, so "a pattern that can address anybody but him is
refused on that ground alone, whatever the page underneath is for".

**Two rulings three lines apart disagree about the same segment.** Narrowing
the older one strictly REDUCES reach, which is the safe direction -- but it can
break a shipped tool, and "it is probably unused" is not a measurement. This
file asks the question that decides how expensive the narrowing would be:

    if NOTHING builds such a url, the breadth is reach nobody uses and the
    narrowing is nearly free;

    if SOMETHING does, this names it, and the answer is to stop rather than to
    narrow.

## Why this parses instead of grepping

A grep for ``/details/`` answers a different question, and this repository has
already paid for the difference twice: once in a memory about text-shaped reads
of a structure, and once THIS SESSION, when a grep over the very pattern this
file is about returned only the FIRST of its two source lines and appeared to
contradict a correct measurement. The allowlist entry is a two-line implicit
string concatenation; half of it says nothing about the other half.

So every module is parsed, and the three ways a url gets built are asked about
separately:

    1. a plain string CONSTANT that contains ``/details/``
    2. an f-string (``JoinedStr``) that contains ``/details/``
    3. a ``.format()`` call or a ``%`` on a string containing ``/details/``

For each hit the MEMBER SEGMENT is read out of the text: the run between
``/in/`` and the next ``/``. It is classified rather than printed raw:

    no-member-segment  the string carries no ``/in/<segment>`` at all. THE
                    LABEL AVOIDS SPELLING THAT PATH: written the obvious way
                    it is itself slug-shaped, and `test_no_committed_identity`
                    refused this file for it -- a classification label that
                    looks like a member slug is exactly what that guard exists
                    to catch, and it cannot know the difference.
    literal-me      the segment is exactly ``me``
    interpolated    the segment is an f-string field or a format placeholder
                    -- THE CASE THAT MATTERS, because a slug harvested off a
                    page would arrive here
    literal-other   a literal that is not ``me``
    regex           the string is a compiled pattern, not a url -- the
                    allowlist entries themselves land here and must not be
                    counted as callers

## The control

A file is only interesting if the instrument can see anything at all. So the
run reports the TOTAL number of string literals examined and the number
containing ``/in/``, whatever the ``/details/`` count turns out to be. **A zero
beside "0 literals examined" is a broken parse; a zero beside "1,247 literals
examined, 31 mention /in/" is a finding.** A refusal must say what it did see.

## Bounds

**PURE. NO BROWSER, NO NETWORK, NO IMPORT OF THE PACKAGE.** It reads files as
text and parses them. Nothing is executed, so a module with a side effect at
import cannot fire.

**NO IDENTITY.** It prints file paths, line numbers, classifications and
counts. The only string content it prints is a MEMBER SEGMENT that has already
been classified as ``literal-me`` or as a placeholder -- never a slug.

**NO OUTPUT PATH.** It writes nothing.

Run:  python scripts/_probe_details_url_breadth.py
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: WHERE A NAVIGATION COULD COME FROM. `linkedin_server/` is the package;
#: `scripts/` is included because a probe navigates too, and a probe that
#: builds a third-party details url is the same finding as a tool that does.
ROOTS = ("linkedin_server", "scripts")

#: RENAMED FROM `NEEDLE`, and the rename is the guard working rather than a
#: style change. `NEEDLE` is in `PERSON_CONSTANTS` in
#: `tests/test_a_person_name_is_never_a_literal.py` -- a constant with that
#: name is where a person's name goes in this repository, so the guard
#: requires its value to be a declared invented name. This one held a path
#: fragment. The fix is to stop calling it a needle, NOT to put `/details/`
#: into a table of invented PEOPLE.
DETAILS_MARKER = "/details/"
IN_MARKER = "/in/"


def _member_segment(text: str) -> str:
    """The run between ``/in/`` and the next ``/``, or "" if there is none."""
    at = text.find(IN_MARKER)
    if at < 0:
        return ""
    rest = text[at + len(IN_MARKER):]
    cut = rest.find("/")
    return rest if cut < 0 else rest[:cut]


#: THIS FILE'S OWN NAME. A probe that talks ABOUT `/in/<not-me>/details/` is
#: full of strings that match its own needle, and the first run flagged two of
#: its own print statements as risky. THEY ARE NOT EXCLUDED FROM THE SCAN --
#: they are CLASSIFIED, as `self-reference`, and still printed. Excluding a
#: file from an instrument because the instrument is inside it is how a real
#: hit in that file would be hidden later.
SELF = Path(__file__).name


def _classify(segment: str, whole: str) -> str:
    """What KIND of member segment this is. Never returns the segment itself
    unless it is the literal ``me``, which identifies nobody."""
    if not segment:
        return "no-member-segment"
    # A compiled pattern rather than a url. Character classes and anchors are
    # the tell, and these must not be counted as callers: the allowlist
    # entries themselves are exactly this shape.
    if any(marker in whole for marker in ("^https", "[A-Za-z", "\\.", "(?", "$")):
        return "regex"
    if segment == "me":
        return "literal-me"
    if "{" in segment or "%" in segment:
        return "interpolated"
    return "literal-other"


def main() -> None:
    print("=== DOES ANYTHING BUILD A /in/<not-me>/details/ URL?")
    print("    parsed, not grepped -- a two-line implicit concatenation is one")
    print("    string to the parser and two lines to a grep\n")

    files = 0
    literals = 0
    mention_in = 0
    hits: list[tuple[str, int, str, str]] = []
    fstrings: list[tuple[str, int, str]] = []
    formats: list[tuple[str, int]] = []

    for root in ROOTS:
        for path in sorted((REPO / root).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            files += 1
            try:
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError as exc:  # pragma: no cover - a broken file
                print("    UNPARSED %s: %s" % (path.name, exc.__class__.__name__))
                continue
            rel = str(path.relative_to(REPO)).replace("\\", "/")
            for node in ast.walk(tree):
                # 1. plain string constants
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    literals += 1
                    text = node.value
                    if IN_MARKER in text:
                        mention_in += 1
                    if DETAILS_MARKER in text:
                        seg = _member_segment(text)
                        hits.append((rel, node.lineno, _classify(seg, text), seg))
                # 2. f-strings
                elif isinstance(node, ast.JoinedStr):
                    flat = "".join(
                        part.value for part in node.values
                        if isinstance(part, ast.Constant) and isinstance(part.value, str)
                    )
                    if DETAILS_MARKER in flat:
                        # An f-string's member segment may be a FIELD, which
                        # flattens to "" here -- that is exactly the case worth
                        # printing, so it is reported by its own path.
                        seg = _member_segment(flat)
                        kind = "literal-me" if seg == "me" else (
                            "interpolated" if not seg or seg.endswith("/") else "literal-other"
                        )
                        fstrings.append((rel, node.lineno, kind))
                # 3. .format() on something mentioning /details/
                elif isinstance(node, ast.Call):
                    func = node.func
                    if (
                        isinstance(func, ast.Attribute)
                        and func.attr == "format"
                        and isinstance(func.value, ast.Constant)
                        and isinstance(func.value.value, str)
                        and DETAILS_MARKER in func.value.value
                    ):
                        formats.append((rel, node.lineno))

    print("=== CONTROL -- what the instrument saw at all")
    print("    files parsed:                     %d" % files)
    print("    string literals examined:         %d" % literals)
    print("    literals mentioning '/in/':       %d" % mention_in)
    print("    literals mentioning '/details/':  %d" % len(hits))
    print("    f-strings mentioning '/details/': %d" % len(fstrings))
    print("    .format() on a '/details/' string: %d" % len(formats))
    if not literals:
        print("\n    ZERO LITERALS EXAMINED -- the parse is broken and every")
        print("    count below is meaningless. Do not read this as a negative.")
        return

    print("\n=== EVERY '/details/' STRING, CLASSIFIED")
    tally: dict[str, int] = {}
    for rel, line, kind, seg in hits:
        if rel.endswith(SELF):
            kind = "self-reference"
        tally[kind] = tally.get(kind, 0) + 1
        shown = seg if kind in ("literal-me", "interpolated") else "<withheld>"
        print("    %-52s :%-5d %-16s %s" % (rel, line, kind, shown))
    for rel, line, kind in fstrings:
        tally["fstring/" + kind] = tally.get("fstring/" + kind, 0) + 1
        print("    %-52s :%-5d %-16s (f-string)" % (rel, line, kind))
    for rel, line in formats:
        tally["format-call"] = tally.get("format-call", 0) + 1
        print("    %-52s :%-5d %-16s" % (rel, line, "format-call"))

    print("\n=== TALLY")
    for kind, n in sorted(tally.items()):
        print("    %-22s %d" % (kind, n))

    # `self-reference` is deliberately absent from this sum, and the reason is
    # printed rather than hidden: those strings are this file's own prose about
    # the thing it is looking for, and they are listed above under that name so
    # a reader can check the judgement rather than take it.
    risky = sum(
        n for kind, n in tally.items()
        if kind != "self-reference"
        and ("interpolated" in kind or "literal-other" in kind or kind == "format-call")
    )
    print("\n=== READING")
    if risky:
        print("    %d string(s) could carry a member segment that is not `me`." % risky)
        print("    NAME THEM ABOVE AND STOP. The narrowing is not free.")
    else:
        print("    NOTHING in this package builds a /in/<not-me>/details/ url.")
        print("    Every '/details/' string is either the literal `me` form or a")
        print("    compiled allowlist pattern. The breadth in the allowlist is")
        print("    reach NOBODY USES, and narrowing it would break no caller here.")
        print("    THAT IS A STATEMENT ABOUT THIS PACKAGE, NOT ABOUT THE BOUNDARY:")
        print("    the allowlist still admits those urls to anything that asks.")


# GUARDED: importing a script must not DO anything.
if __name__ == "__main__":
    main()
