"""Build the classic job search's ALERT TOGGLE into a committed fixture: the live lane's session-2 skeleton of one job search, with the toggle's one measured word kept.

Kept as the PROVENANCE of ``tests/fixtures/live2/j107_search_alert.html``, the
fixture ``linkedin_server.search_alert_switch`` (census row ``J 31``) is built
over, 2026-11-25 (lane build-jmn26).

THE INPUT is the gitignored KEYED skeleton the live lane wrote on 2026-09-28
(``_state/live2/j107.skeleton.html``, every text and attribute value a keyed
shape ``{L<letters>D<digits>n<length>:<8-hex hash>}``) and that session's key
(``_state/live2/shape.key``). Both are read, neither is written anywhere, and
nothing here prints a hash or the key. The committed copy
``tests/fixtures/live2/j107.html`` is ``tracked_copy`` of the same skeleton;
this script recomputes that copy and REFUSES unless it is identical to the
committed one, so the input is shown to be the capture the repository
already holds.

WHAT IT CHANGES, and only inside the toggle: the ONE
``div.jobs-search-create-alert__artdeco-toggle`` must hold exactly one
``span.artdeco-toggle__text`` with one line of text, and that text is written
as :data:`WORD` ONLY after ``value_shape(WORD, key)`` equals the keyed shape at
that place -- a MEASURED word, never an assumed one. The toggle's hidden label
(27 letters in 33 characters, matched by no candidate tried) stays ``x``, as
every other text does. Everything else is the committed copy's.

    python scripts/_build_search_alert_skeleton.py --skeleton <keyed skeleton> --key <shape.key> [--out <path>]

Prints counts and a sha256 digest of what it wrote, never a value it read.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import _probe_live_lane_session_2 as s2  # noqa: E402  value_shape, tracked_copy

DEFAULT_OUT = REPO / "tests" / "fixtures" / "live2" / "j107_search_alert.html"
BASE_COPY = REPO / "tests" / "fixtures" / "live2" / "j107.html"

#: The toggle's class, LinkedIn's own, and its visible word, MEASURED
#: 2026-11-25 by hashing the candidate with session 2's key against the keyed
#: skeleton (this lane's record, section 0).
TOGGLE_CLASS = "jobs-search-create-alert__artdeco-toggle"
TEXT_CLASS = "artdeco-toggle__text"
WORD = "Set alert"

HEADER = (
    "<!doctype html>\n<!--\n"
    "  LANE BUILD-JMN26 (census row J 31), 2026-11-25: built by\n"
    "  scripts/_build_search_alert_skeleton.py from the live lane's SESSION-2\n"
    "  keyed skeleton of one classic job search, the same skeleton\n"
    "  tests/fixtures/live2/j107.html is the tracked copy of. Identical to that\n"
    "  copy except for ONE text: the alert toggle's visible word, LinkedIn's\n"
    "  own, written only after its keyed shape matched. Every other text is x,\n"
    "  as in that copy.\n"
    "-->\n"
)

_VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input",
                   "link", "meta", "param", "source", "track", "wbr"})


class _Node:
    def __init__(self, tag: str, attrs: dict, line: int, parent: Optional["_Node"]) -> None:
        self.tag, self.attrs, self.line, self.parent = tag, attrs, line, parent
        self.children: list = []


class _Text:
    def __init__(self, text: str, line: int, parent: "_Node") -> None:
        self.text, self.line, self.parent = text, line, parent


class _Tree(HTMLParser):
    """The skeleton writes one token per line, so a token's line IS its place."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("#root", {}, 0, None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, dict(attrs), self.getpos()[0], self.cur)
        self.cur.children.append(node)
        if tag not in _VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(_Node(tag, dict(attrs), self.getpos()[0], self.cur))

    def handle_endtag(self, tag):
        walker = self.cur
        while walker is not None and walker.tag != tag:
            walker = walker.parent
        if walker is not None and walker.parent is not None:
            self.cur = walker.parent

    def handle_data(self, data):
        if data.strip():
            lead = data[: len(data) - len(data.lstrip())].count("\n")
            self.cur.children.append(_Text(data.strip(), self.getpos()[0] + lead, self.cur))


def _walk(node):
    yield node
    for child in getattr(node, "children", []):
        yield from _walk(child)


def _classes(node: _Node) -> list[str]:
    return str(node.attrs.get("class") or "").split()


def build(skeleton: str, key: bytes) -> tuple[str, dict[str, int]]:
    lines = skeleton.split("\n")
    tree = _Tree()
    tree.feed(skeleton)
    tree.close()

    toggles = [n for n in _walk(tree.root)
               if isinstance(n, _Node) and TOGGLE_CLASS in _classes(n)]
    if len(toggles) != 1:
        raise SystemExit(f"{len(toggles)} alert toggles in the skeleton, where one is required")
    spans = [n for n in _walk(toggles[0])
             if isinstance(n, _Node) and n.tag == "span" and TEXT_CLASS in _classes(n)]
    if len(spans) != 1:
        raise SystemExit(f"the toggle holds {len(spans)} text spans, where one is required")
    texts = [n for n in _walk(spans[0]) if isinstance(n, _Text)]
    if len(texts) != 1:
        raise SystemExit("the toggle's text span does not hold exactly one line of text")
    text = texts[0]
    if text.text != WORD and s2.value_shape(WORD, key) != text.text:
        raise SystemExit("the toggle's text did not match its measured word; refusing to write it")
    current = lines[text.line - 1]
    if current.count(text.text) != 1:
        raise SystemExit("the toggle's text line did not hold exactly one value to replace")
    lines[text.line - 1] = current.replace(text.text, WORD)

    copy = s2.tracked_copy("\n".join(lines))
    if not copy.startswith("<!doctype html>\n"):
        raise SystemExit("the skeleton does not open with its doctype line")
    counts = {"toggles": len(toggles), "text spans": len(spans), "words kept": 1}
    return HEADER + copy[len("<!doctype html>\n"):], counts


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--skeleton", required=True, type=Path)
    parser.add_argument("--key", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    skeleton = args.skeleton.read_text(encoding="utf-8")
    key = bytes.fromhex(args.key.read_text(encoding="utf-8").strip())

    base = s2.tracked_copy(skeleton)
    if BASE_COPY.read_text(encoding="ascii") != base:
        raise SystemExit("this skeleton's tracked copy is not tests/fixtures/live2/j107.html")

    text, counts = build(skeleton, key)
    assert all(ord(ch) < 128 for ch in text)
    args.out.write_text(text, encoding="ascii", newline="\n")
    print("base copy identical to the committed capture: True")
    for name in sorted(counts):
        print("%-12s %d" % (name, counts[name]))
    body = text.split("\n")[len(HEADER.split("\n")) - 1:]
    print("lines differing from the base copy: %d" % sum(
        1 for a, b in zip(base.split("\n")[1:], body) if a != b))
    print("sha256 %s" % hashlib.sha256(text.encode("ascii")).hexdigest()[:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
