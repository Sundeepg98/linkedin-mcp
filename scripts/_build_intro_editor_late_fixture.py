"""Build the intro editor whose dialog is drawn LATE: the world the editor
path's bounded wait is tested in (the live lane's session 4, 2026-09-28).

THE MEASUREMENT THIS FIXTURE PLANTS. Live, P B9's test write loaded his intro
editor and its gate read the dialog the moment the address loaded: refused,
``0_editor_not_found`` -- the dialog holding the one Save control was not
found exactly once. Another load of the same address found the dialog already
drawn when the navigation returned. So LinkedIn draws that dialog on its own
schedule after the page loads, and a reader that looks at once can lose the
race (``_audit/2026-09-23-live-lane-session-1.md``, "Live session 4").

WHAT IS CARRIED OVER, AND FROM WHERE.
* The editor's STRUCTURE comes from ``tests/fixtures/synthetic/intro_editor_switches.html``,
  itself built by ``scripts/_build_intro_editor_switches_fixture.py`` from
  session 1's capture: one ``dialog`` holding a labelled field, the settings
  row with the two switches, and the one ``Save`` control. Every text, id and
  key in it is already invented.
* TODAY'S CAPTURE, ``tests/fixtures/live4/editor.html`` (the tracked copy of
  session 4's skeleton of his editor, every text of his one ``x``), is the
  PRECONDITION: this builder refuses unless that page draws exactly one
  ``dialog`` element holding a button whose text is exactly ``Save`` -- the
  element a late draw defers. It reads nothing else from it and carries
  nothing over from it.

WHAT IS INVENTED: the lateness. The dialog is held in a ``template`` and
inserted by the page's own script ``data-late-ms`` milliseconds after the
page loads; a negative value never inserts it. Nothing else changes, so every
reader that finds the dialog finds the same structure it always found.

    python scripts/_build_intro_editor_late_fixture.py            # write it
    python scripts/_build_intro_editor_late_fixture.py --check    # exit 1 if stale

It prints counts only.
"""
from __future__ import annotations

import argparse
import pathlib
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests" / "fixtures" / "synthetic" / "intro_editor_switches.html"
TODAY = ROOT / "tests" / "fixtures" / "live4" / "editor.html"
OUT = ROOT / "tests" / "fixtures" / "synthetic" / "intro_editor_late.html"

#: How late the committed fixture draws its dialog. A test sets its own.
DEFAULT_LATE_MS = 1500
TEMPLATE_ID = "intro-editor-late"
DIALOG_OPEN = "<dialog"
DIALOG_CLOSE = "</dialog>"

#: The page's own script: after ``data-late-ms`` milliseconds, the template's
#: dialog is appended to the body; a negative value never draws it.
INSERT_SCRIPT = (
    "<script>(function () {"
    " var t = document.getElementById('" + TEMPLATE_ID + "');"
    " var ms = Number(t.getAttribute('data-late-ms'));"
    " if (!(ms >= 0)) { return; }"
    " setTimeout(function () { document.body.appendChild(t.content.cloneNode(true)); }, ms);"
    " })();</script>"
)


def make_late(html: str, late_ms: int = DEFAULT_LATE_MS) -> str:
    """The page with its ONE dialog held back and drawn ``late_ms`` after it
    loads (never, when negative). PURE. Refuses a page with no dialog or with
    more than one: which one to defer would be a choice this does not make."""
    if html.count(DIALOG_OPEN) != 1 or html.count(DIALOG_CLOSE) != 1:
        raise ValueError("the page must hold exactly one dialog to draw late")
    start = html.index(DIALOG_OPEN)
    end = html.index(DIALOG_CLOSE) + len(DIALOG_CLOSE)
    if "</body>" not in html[end:]:
        raise ValueError("the dialog must sit inside the body")
    held = ('<template id="' + TEMPLATE_ID + '" data-late-ms="' + str(int(late_ms)) + '">'
            + html[start:end] + "</template>")
    late = html[:start] + held + html[end:]
    return late.replace("</body>", INSERT_SCRIPT + "</body>", 1)


class _Dialogs(HTMLParser):
    """Counts ``dialog`` elements, and those holding a button whose own text
    is exactly ``Save``. Counts only."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.dialogs = 0
        self.with_save = 0
        self._depth = 0
        self._saw_save = False
        self._in_button = False
        self._button_text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "dialog":
            if self._depth == 0:
                self.dialogs += 1
                self._saw_save = False
            self._depth += 1
        elif tag == "button" and self._depth:
            self._in_button = True
            self._button_text = []

    def handle_endtag(self, tag):
        if tag == "button" and self._in_button:
            self._in_button = False
            if " ".join("".join(self._button_text).split()) == "Save":
                self._saw_save = True
        elif tag == "dialog" and self._depth:
            self._depth -= 1
            if self._depth == 0 and self._saw_save:
                self.with_save += 1

    def handle_data(self, data):
        if self._in_button:
            self._button_text.append(data)


def dialog_counts(html: str) -> tuple[int, int]:
    """(dialog elements, dialogs holding a button reading exactly Save)."""
    parser = _Dialogs()
    parser.feed(html)
    parser.close()
    return parser.dialogs, parser.with_save


#: The late fixture's own provenance line, after the doctype; the switch
#: fixture's header below it still says where the structure came from.
PROVENANCE = (
    "<!-- LATE: built by scripts/_build_intro_editor_late_fixture.py from\n"
    "     intro_editor_switches.html. Its one dialog is drawn by the page's own\n"
    "     script data-late-ms after the page loads (never, when negative). -->\n"
)


def build() -> str:
    """The fixture's text, or ValueError if today's capture disagrees."""
    dialogs, with_save = dialog_counts(TODAY.read_text(encoding="ascii"))
    if with_save != 1:
        raise ValueError(
            "today's capture draws " + str(with_save) + " dialog(s) holding a Save control ("
            + str(dialogs) + " dialogs in all); the late world defers exactly one"
        )
    source = SOURCE.read_text(encoding="ascii")
    doctype = "<!doctype html>\n"
    if not source.startswith(doctype):
        raise ValueError("the switch fixture no longer opens on its doctype")
    return doctype + PROVENANCE + make_late(source[len(doctype):])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the committed fixture is stale")
    args = ap.parse_args(argv)
    try:
        text = build()
    except ValueError as exc:
        print("REFUSED:", exc)
        return 2
    dialogs, with_save = dialog_counts(TODAY.read_text(encoding="ascii"))
    print("today's capture: " + str(dialogs) + " dialogs, " + str(with_save) + " holding Save")
    if args.check:
        same = OUT.exists() and OUT.read_text(encoding="ascii") == text
        print("the committed fixture is " + ("current" if same else "STALE"))
        return 0 if same else 1
    OUT.write_text(text, encoding="ascii", newline="\n")
    print("wrote " + OUT.name + ": " + str(len(text)) + " characters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
