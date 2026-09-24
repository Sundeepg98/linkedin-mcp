"""Turn a captured INTRO EDITOR into a sanitised fixture of its two unnamed switches.

Kept as the PROVENANCE of ``tests/fixtures/synthetic/intro_editor_switches.html``:
the exact record of what was carried over from the live capture and what was
invented, which is what a privacy review needs and cannot get from the output.

THE CAPTURE. The live lane's session 1 captured the intro editor
(``_audit/2026-09-23-live-lane-session-1.md``, Entry 5) and identified its two
switches offline, by the text of their section, as 'Open Profile' and 'Profile
Premium Badge'. ``linkedin_server.profile_editor`` ties a switch it sees to
that identification by STRUCTURE; this fixture carries that structure and
nothing else.

WHAT IS CARRIED OVER, AND IT IS STRUCTURE ONLY. The settings row that holds
the switches, inside the one element above it the page names -- the dialog's
scrolling column, carried as ``data-testid="lazy-column"`` because the
recognition anchors on it -- element for element in the captured order: every tag, the ARIA
attributes the recognition reads by PRESENCE (``role``, ``aria-checked``), the
switch inputs' ``type`` and ``checked`` state, each input's ``label[for]``
pairing, and the one accessible name the capture gives each wrapper -- a
LinkedIn UI string, carried verbatim the way the job fixtures carry theirs.

WHAT IS INVENTED, AND IT IS EVERYTHING ELSE. Every text node (the row's title,
each block's title and description, the state word), every id (the capture's
are of the shape React generates), every ``componentkey`` (the capture's have
random-UUID, version-4 shape) and every class (dropped: the recognition reads none). The
rest of the dialog is not carried at all -- its fields hold his values -- and
is replaced by one invented named field and the ``Save`` control the dialog is
anchored by. So no value of his can reach the committed file by construction,
and no sanitisation key is needed.

WHICH BLOCK IS WHICH. The capture's first block is the one its section text
calls 'Open Profile', the second 'Profile Premium Badge' -- the order
``profile_editor.INTRO_SWITCH_IDENTITIES`` records. The fixture's own titles
are placeholders, so a test can move them without moving the structure.

The raw capture is gitignored and never committed. Re-run only after
re-capturing the intro editor:

    python scripts/_build_intro_editor_switches_fixture.py --capture <path>
    python scripts/_build_intro_editor_switches_fixture.py --check <file>...

It prints counts only -- never a text, an id or a key. ``--check`` runs the
same structural signature against any file and exits non-zero when it does not
find exactly one settings row with exactly two switch blocks, so re-running it
on a new capture says whether the recorded structure still holds.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "tests" / "fixtures" / "synthetic" / "intro_editor_switches.html"

SAVE = "Save"
WRAPPER_NAME = "Tap to toggle setting"
#: The test id the capture draws on the row's parent -- the anchor
#: ``profile_editor.INTRO_SWITCH_COLUMN`` names. Carried only when it is exactly
#: this, which the signature requires.
COLUMN_TESTID = "lazy-column"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
#: The attributes carried over from the capture, by name. Everything else is
#: dropped; ids and ``for`` are carried as a PAIRING, with invented values.
CARRIED = ("role", "aria-checked", "type", "checked", "tabindex")
INTERACTIVE = {"input", "button", "select", "textarea"}


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.children: list[Node] = []
        self.text: list[str] = []

    def kids(self):
        return [c for c in self.children if isinstance(c, Node)]


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", [], None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, data):
        if data.strip():
            self.cur.text.append(data.strip())


def walk(n):
    yield n
    for c in n.kids():
        yield from walk(c)


def text_of(n) -> str:
    return " ".join([*n.text, *(text_of(c) for c in n.kids())]).strip()


def _dialog(root):
    """The one dialog holding exactly one button whose text is ``Save``."""
    dialogs = [n for n in walk(root) if n.tag == "dialog" or n.attrs.get("role") == "dialog"]
    holders = [
        d for d in dialogs
        if sum(1 for b in walk(d) if b.tag == "button" and text_of(b) == SAVE) == 1
    ]
    return holders[0] if len(holders) == 1 else None


def _unnamed(root, sw) -> bool:
    """No naming attribute, no label around it, the label right before it
    EMPTY, and no label naming it from anywhere in the document -- the
    attribute half and the accessible-name half the recogniser asks."""
    if any(a in sw.attrs for a in ("aria-label", "aria-labelledby", "title")):
        return False
    n = sw.parent
    while n is not None:
        if n.tag == "label":
            return False
        n = n.parent
    siblings = sw.parent.kids() if sw.parent is not None else []
    at = next((i for i, k in enumerate(siblings) if k is sw), 0)
    before = siblings[at - 1] if at > 0 else None
    if before is None or before.tag != "label" or before.kids() or text_of(before):
        return False
    sid = sw.attrs.get("id")
    if sid:
        for lab in walk(root):
            if lab.tag == "label" and lab.attrs.get("for") == sid and text_of(lab):
                return False
    return True


def _block_of(root, sw):
    """The same signature ``profile_editor.INTRO_SWITCH_BLOCKS`` applies."""
    if sw.attrs.get("role") != "switch" or not _unnamed(root, sw):
        return None, None
    wrap = sw.parent
    while wrap is not None and wrap.attrs.get("role") != "switch":
        wrap = wrap.parent
    if wrap is None or wrap.tag != "div" or "aria-checked" not in wrap.attrs:
        return None, None
    if sum(1 for n in walk(wrap) if n.tag == "input" and n.attrs.get("type") == "checkbox") != 1:
        return None, None
    part = wrap.parent
    block = part.parent if part is not None else None
    if block is None or block.tag != "div":
        return None, None
    kids = block.kids()
    if len(kids) != 2 or kids[1] is not part or kids[0].tag != "div" or part.tag != "div":
        return None, None
    if sum(1 for n in walk(block) if n.tag == "input" and n.attrs.get("type") == "checkbox") != 1:
        return None, None
    textpart = kids[0]
    if any(n.tag in INTERACTIVE or "role" in n.attrs for n in list(walk(textpart))[1:]):
        return None, None
    if not any(n.tag == "p" for n in walk(textpart)):
        return None, None
    return block, wrap


def find_row(root):
    """(row, [(block, wrapper, input) in row order]) or (None, reason)."""
    dialog = _dialog(root)
    if dialog is None:
        return None, "no single dialog anchored by one Save button"
    inputs = [n for n in walk(dialog) if n.tag == "input" and n.attrs.get("type") == "checkbox"]
    found = [(sw,) + _block_of(root, sw) for sw in inputs]
    rows = {}
    for sw, block, wrap in found:
        if block is not None:
            rows.setdefault(id(block.parent), (block.parent, []))[1].append((block, wrap, sw))
    good = []
    for row, members in rows.values():
        kids = row.kids()
        column = row.parent
        if column is None or column.attrs.get("data-testid") != COLUMN_TESTID:
            continue
        if len(kids) == 3 and kids[0].tag == "p" and {id(k) for k in kids[1:]} == {id(b) for b, _, _ in members}:
            good.append((row, sorted(members, key=lambda m: kids.index(m[0]))))
    if len(good) != 1:
        return None, f"{len(good)} settings rows under the {COLUMN_TESTID} column match the signature, where exactly one is required"
    return good[0], None


def _serialise(node, ids, depth=0) -> str:
    """Tags and CARRIED attributes only; every text invented by position."""
    attrs = []
    for name in CARRIED:
        if name in node.attrs:
            value = node.attrs[name]
            attrs.append(name if value is None else f'{name}="{value}"')
    if node.attrs.get("role") == "switch" and node.tag == "div":
        attrs.append(f'aria-label="{WRAPPER_NAME}"' if node.attrs.get("aria-label") == WRAPPER_NAME else 'aria-label="Placeholder wrapper"')
    if node.tag == "input" and node.attrs.get("id"):
        attrs.append(f'id="{ids[node.attrs["id"]]}"')
    if node.tag == "label" and node.attrs.get("for") in ids:
        attrs.append(f'for="{ids[node.attrs["for"]]}"')
    open_tag = "<" + node.tag + ("" if not attrs else " " + " ".join(attrs)) + ">"
    if node.tag in VOID:
        return open_tag
    inner = []
    if node.text and node.tag != "label":
        inner.append(node.__dict__.get("_invented", "Placeholder"))
    inner.extend(_serialise(c, ids, depth + 1) for c in node.kids())
    return open_tag + "".join(inner) + f"</{node.tag}>"


def build(capture: pathlib.Path) -> tuple[str, dict]:
    tree = Tree()
    tree.feed(capture.read_text(encoding="utf-8", errors="replace"))
    found, reason = find_row(tree.root)
    if found is None:
        raise SystemExit(f"REFUSED: {reason}")
    row, members = found
    # INVENTED TEXT, by position: the row title, each block's title and
    # description, the state word inside each wrapper.
    row.kids()[0]._invented = "Placeholder section"
    for letter, (block, wrap, sw) in zip("AB", members):
        paragraphs = [n for n in walk(block.kids()[0]) if n.tag == "p"]
        for k, p in enumerate(paragraphs):
            p._invented = f"Placeholder setting {letter}" if k == 0 else f"Placeholder description {letter}"
        for n in walk(wrap):
            if n.text:
                n._invented = "Placeholder state"
    ids = {sw.attrs["id"]: f"intro-switch-{k + 1}" for k, (_, _, sw) in enumerate(members) if sw.attrs.get("id")}
    row_html = f'<div data-testid="{COLUMN_TESTID}">' + _serialise(row, ids) + "</div>"
    counts = {
        "blocks": len(members),
        "checked": sum(1 for _, _, sw in members if "checked" in sw.attrs),
        "wrapper_name_carried": sum(1 for _, w, _ in members if w.attrs.get("aria-label") == WRAPPER_NAME),
    }
    html = (
        "<!doctype html>\n"
        "<!-- SYNTHETIC: built by scripts/_build_intro_editor_switches_fixture.py from one\n"
        "     capture of the intro editor. The settings row is the capture's STRUCTURE;\n"
        "     every text, id and key is invented, and the rest of the dialog is not\n"
        "     carried (see the builder's docstring). -->\n"
        "<html><body><main><h1>Profile</h1></main>\n"
        '<dialog open aria-labelledby="intro-dialog-header">\n'
        '<h2 id="intro-dialog-header">Edit intro</h2>\n'
        '<label for="intro-city">City</label>'
        '<input id="intro-city" type="text" value="Placeholdertown">\n'
        f"{row_html}\n"
        '<button type="button">Save</button>\n'
        "</dialog></body></html>\n"
    )
    return html, counts


def check(path: pathlib.Path) -> int:
    tree = Tree()
    tree.feed(path.read_text(encoding="utf-8", errors="replace"))
    found, reason = find_row(tree.root)
    if found is None:
        print(f"{path.name}: NO -- {reason}")
        return 1
    _, members = found
    print(f"{path.name}: one settings row, {len(members)} switch blocks")
    return 0 if len(members) == 2 else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--capture", type=pathlib.Path, help="the raw intro-editor capture")
    ap.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    ap.add_argument("--check", type=pathlib.Path, nargs="*", default=None)
    args = ap.parse_args(argv)
    if args.check is not None:
        return max([check(p) for p in args.check] or [1])
    if args.capture is None:
        ap.error("--capture is required to build")
    html, counts = build(args.capture)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="ascii", newline="\n")
    print(f"wrote {args.out.name}: {counts}")
    return check(args.out)


if __name__ == "__main__":
    raise SystemExit(main())
