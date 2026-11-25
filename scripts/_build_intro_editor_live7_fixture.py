"""Build the TRACKED copy of his intro editor as the live lane's session 7
drew it (2026-10-10): ``tests/fixtures/live7/editor.html``.

Kept as the PROVENANCE of that fixture: the exact record of what was carried
over from the live lane's skeleton, what was restored, and what was invented
-- which is what a privacy review needs and cannot get from the output.

THE SOURCE. The live lane's session 7 loaded his intro editor once
(``_audit/2026-09-23-live-lane-session-1.md``, "Live session 7") and kept it
as a SKELETON in its gitignored state: every text and every attribute value
outside a closed set reduced to a keyed shape (letters, digits, length, an
8-hex HMAC under that session's own key, which is gitignored too), LinkedIn's
own furniture words kept. Lane K's ledger plans this tracked copy from it
(``_audit/2026-09-28-lane-k-ledger.md``, the PLANNED block: P A14, P A15,
P A22). Both inputs are passed on the command line; no path to them is
written here.

WHAT IS CARRIED OVER. Everything ``tracked_copy`` of
``scripts/_probe_live_lane_session_2.py`` keeps -- tags, classes, roles, ARIA
states, LinkedIn's path words and furniture -- with every remaining keyed shape
one ``x`` and every id reference ``k`` plus its hash, so a label still finds
its control. That is the rule the session-2 and session-4 tracked copies were
made by.

WHAT IS RESTORED, AND ONLY WHERE THE SESSION'S OWN KEY SAYS SO. A word below
replaces a keyed shape only when that shape is EXACTLY the word's shape under
the session's key -- equal letters, digits, length and HMAC -- so nothing is
restored on a guess:

* :data:`LABEL_WORDS`, LinkedIn's labels of the editor's controls, wherever
  their shape stands (a label's text, an ``aria-label``);
* :data:`OPTION_WORDS`, LinkedIn's own option texts, ONLY as the text of an
  ``option`` -- the pronoun words also stand once outside the select, on his
  top card, and are NOT restored there;
* :data:`ARIA_WORDS`, the closed ARIA vocabulary of ``aria-autocomplete``.

WHAT IS INVENTED. The text of any option that is none of LinkedIn's words --
his organization (its value is a ten-digit company id) and his school -- is
replaced by the DECLARED SYNTHETIC text of :data:`INVENTED_OPTIONS`, keyed by
the label of the select it sits in. An option of any other select (one sits
far outside the dialog) stays one ``x``, as every other text of his does.

ONE FORMAT CORRECTION. The skeleton writes every node on its own line, which
inside an ``option`` would put line breaks into the option's text -- text the
shipped value reader returns untrimmed. Each option's text is written inline
(see :func:`restore`, step 4).

    python scripts/_build_intro_editor_live7_fixture.py --skeleton <path> --key <path>
    python scripts/_build_intro_editor_live7_fixture.py --skeleton <path> --key <path> --check

It prints counts only -- never a text, an id or a key. ``--check`` exits 1
when the committed fixture is not what the inputs build. Both inputs exist on
the live lane's box only, so CI holds the fixture to its pinned digest
instead (``tests/test_the_intro_editor_draws_his_organization_select.py``).
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import html as html_escape
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "tests" / "fixtures" / "live7" / "editor.html"

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _probe_live_lane_session_2 import tracked_copy  # noqa: E402

#: LinkedIn's labels of the intro editor's controls, each matched in the
#: session-7 skeleton by its keyed shape (counted 2026-10-10 by the lane B1
#: lead). "Education", "Save" and "On" are furniture and survive anyway.
LABEL_WORDS: tuple[str, ...] = (
    "Organization",
    "Pronouns",
    "Additional name",
    "Country/Region",
    "City",
    "Industry",
    "First name",
    "Last name",
    "Headline",
    "Contact info",
    "Edit intro",
    "Open Profile",
    "Profile Premium Badge",
    "Tap to toggle setting",
    "Link",
)

#: LinkedIn's own option texts: the unset option and the pronoun choices.
OPTION_WORDS: tuple[str, ...] = ("Please select", "She/Her", "He/Him", "They/Them", "Custom")

#: The closed values of ``aria-autocomplete``.
ARIA_WORDS: tuple[str, ...] = ("list", "none", "both", "inline")

#: DECLARED SYNTHETIC option texts, by the label of their select. Never a
#: real organization or school.
INVENTED_OPTIONS: dict[str, str] = {
    "Organization": "Example Organisation",
    "Education": "Example School",
}

PROVENANCE = (
    "<!-- LIVE7 EDITOR: built by scripts/_build_intro_editor_live7_fixture.py\n"
    "     from the live lane's session-7 skeleton of his intro editor\n"
    "     (2026-10-10). Every text of his one x; LinkedIn's labels and option\n"
    "     words restored by their keyed shapes; the organization and school\n"
    "     options invented. -->\n"
)

_SHAPE_TOKEN = re.compile(r"\{L\d{1,7}D\d{1,7}n\d{1,7}:[0-9a-f]{8}\}")


def shape_of(text: str, key: bytes) -> str:
    """The keyed shape the session wrote for ``text``: the same function as
    ``value_shape`` in ``scripts/_probe_live_lane_session_2.py``. PURE."""
    letters = sum(1 for ch in text if ch.isalpha())
    digits = sum(1 for ch in text if ch.isdigit())
    mark = hmac.new(key, text.encode("utf-8"), hashlib.sha256).hexdigest()[:8]
    return "{L" + str(letters) + "D" + str(digits) + "n" + str(len(text)) + ":" + mark + "}"


def restore(skeleton: str, key: bytes) -> tuple[str, dict[str, int]]:
    """The skeleton with LinkedIn's words put back where their shapes stand,
    and the invented options planted. PURE. Returns the text and its counts."""
    counts: dict[str, int] = {}
    label_shapes = {shape_of(w, key): w for w in LABEL_WORDS}
    option_shapes = {shape_of(w, key): w for w in OPTION_WORDS}
    aria_shapes = {shape_of(w, key): w for w in ARIA_WORDS}

    lines = skeleton.split("\n")
    # 1. Labels, wherever their shape stands.
    out: list[str] = []
    for line in lines:
        def put(match: "re.Match[str]") -> str:
            token = match.group(0)
            word = label_shapes.get(token)
            if word is None and 'aria-autocomplete="' + token + '"' in line:
                word = aria_shapes.get(token)
            if word is None:
                return token
            counts[word] = counts.get(word, 0) + 1
            return html_escape.escape(word, quote=True)
        out.append(_SHAPE_TOKEN.sub(put, line))
    lines = out

    # 2. Which select each label names: <label ... for="ID"> ... <word> ... </label>.
    select_label: dict[str, str] = {}
    current_for = None
    for line in lines:
        m = re.match(r'<label\b[^>]*\bfor="([^"]+)"', line)
        if m:
            current_for = m.group(1)
            continue
        if line.startswith("</label>"):
            current_for = None
            continue
        if current_for is not None and not line.startswith("<"):
            select_label.setdefault(current_for, line.strip())

    # 3. Options: LinkedIn's words by shape, else the invented text of the
    # select's label. Only an option's own text line is touched; an option of
    # a select whose label has no invented text stays a shape (so one x).
    in_select = None
    in_option = False
    for i, line in enumerate(lines):
        m = re.match(r'<select\b[^>]*\bid="([^"]+)"', line)
        if m:
            in_select = m.group(1)
            continue
        if line.startswith("</select>"):
            in_select = None
            continue
        if in_select is None:
            continue
        if line.startswith("<option"):
            in_option = True
            continue
        if line.startswith("</option>"):
            in_option = False
            continue
        if in_option and _SHAPE_TOKEN.fullmatch(line.strip()):
            word = option_shapes.get(line.strip())
            if word is not None:
                counts["option:" + word] = counts.get("option:" + word, 0) + 1
                lines[i] = html_escape.escape(word, quote=False)
                continue
            label = select_label.get(in_select, "")
            invented = INVENTED_OPTIONS.get(label)
            if invented is None:
                counts["left as x: option of an unlisted select"] = (
                    counts.get("left as x: option of an unlisted select", 0) + 1
                )
                continue
            counts["invented:" + label] = counts.get("invented:" + label, 0) + 1
            lines[i] = invented

    # 4. AN OPTION'S TEXT IS WRITTEN INLINE. The skeleton writes every node on
    # its own line; inside an option those line breaks become part of the
    # option's textContent, which the shipped value reader returns UNTRIMMED by
    # design (a value is read to be put back). LinkedIn's live options carry no
    # such whitespace -- P A21's live proof read the chosen option equal to its
    # label at the first poll after the press -- so an option's one text line
    # is joined to its tags. Nothing else moves.
    joined: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if (line.startswith("<option") and i + 2 < len(lines)
                and not lines[i + 1].startswith("<") and lines[i + 2].startswith("</option>")):
            joined.append(line + lines[i + 1].strip() + lines[i + 2])
            counts["options written inline"] = counts.get("options written inline", 0) + 1
            i += 3
            continue
        joined.append(line)
        i += 1
    return "\n".join(joined), counts


def build(skeleton: str, key: bytes) -> tuple[str, dict[str, int]]:
    """The fixture's text and the restoration counts. PURE."""
    restored, counts = restore(skeleton, key)
    copy = tracked_copy(restored)
    doctype = "<!doctype html>\n"
    if not copy.startswith(doctype):
        raise ValueError("the skeleton no longer opens on its doctype")
    return doctype + PROVENANCE + copy[len(doctype):], counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--skeleton", required=True, help="the live lane's session-7 skeleton of the editor")
    ap.add_argument("--key", required=True, help="that session's shape key")
    ap.add_argument("--check", action="store_true", help="exit 1 if the committed fixture is stale")
    args = ap.parse_args(argv)
    skeleton = pathlib.Path(args.skeleton).read_text(encoding="utf-8")
    key = bytes.fromhex(pathlib.Path(args.key).read_text(encoding="utf-8").strip())
    try:
        text, counts = build(skeleton, key)
    except ValueError as exc:
        print("REFUSED:", exc)
        return 2
    for name in sorted(counts):
        print("restored " + name + ": " + str(counts[name]))
    if args.check:
        same = OUT.exists() and OUT.read_text(encoding="ascii") == text
        print("the committed fixture is " + ("current" if same else "STALE"))
        return 0 if same else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="ascii", newline="\n")
    print("wrote " + OUT.name + ": " + str(len(text)) + " characters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
