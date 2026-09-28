"""Build the intro editor whose controls answer a press LATE: the world the
editor path's bounded wait after its press is tested in (the live lane's
session 5, 2026-09-28).

THE MEASUREMENT THIS FIXTURE PLANTS. Live, P B9's restore pressed the Premium
badge switch once and the in-dialog read taken straight after the press still
showed the old state, so the write -- rightly -- did not press Save, and his
badge was left hidden; the same press about two minutes later flipped the
switch in the read (``_audit/2026-09-23-live-lane-session-1.md``, "Live
session 5"). The select path reads its field the same way, straight after
``select_option``.

WHAT IS CARRIED OVER, AND FROM WHERE.
* The switch row comes from ``tests/fixtures/synthetic/intro_editor_switches.html``,
  built by ``scripts/_build_intro_editor_switches_fixture.py`` from session
  1's capture: one dialog, the settings row with its two switches, one Save.
  Every text, id and key in it is already invented.
* TODAY'S CAPTURE, ``tests/fixtures/live4/editor.html`` (the tracked copy of
  his editor, every text of his one ``x``), gives the two selects' SHAPES, and
  this builder refuses unless it draws them: one dialog holding Save, a
  select of 5 options and a select of 2, each opening on exactly one option
  whose value is empty (the unset option), and exactly two switch inputs.
  Nothing else is read from it and nothing is carried over from it: the
  options' texts here are invented.

WHAT IS INVENTED: the lateness. :func:`make_late_press` appends one script: a
switch press flips its switch ``switch_ms`` after the press (never, when
negative), and a select's change is undone at once and applied again
``select_ms`` later (never, when negative) -- the shape of a controlled
component whose state lands a moment after the DOM event. The committed file
also carries the minimal press handler the switch row needs to be pressed at
all, since the source fixture carries none.

    python scripts/_build_intro_editor_late_press_fixture.py            # write it
    python scripts/_build_intro_editor_late_press_fixture.py --check    # exit 1 if stale

It prints counts only.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests" / "fixtures" / "synthetic" / "intro_editor_switches.html"
TODAY = ROOT / "tests" / "fixtures" / "live4" / "editor.html"
OUT = ROOT / "tests" / "fixtures" / "synthetic" / "intro_editor_late_press.html"

#: ``profile_editor.PREMIUM_BADGE_TITLE``, restated so this builder imports
#: nothing from the package; a test holds the two equal.
BADGE_TITLE = "Profile Premium Badge"

#: How late the committed fixture answers. A test sets its own.
#: Long enough that a read straight after the press lands before it even on a
#: loaded box (800 ms did not, once, under a concurrent suite).
DEFAULT_SWITCH_MS = 2500
DEFAULT_SELECT_MS = 2500

#: The two selects today's capture draws, by option count, each opening on
#: its one unset option. Their labels are LinkedIn's field names; their
#: option texts are invented.
SELECTS = (
    ("Pronouns", "intro-pronouns", ("Please select", "Option A", "Option B", "Option C", "Custom")),
    ("Education", "intro-education", ("Please select", "Placeholder school")),
)

#: The minimal press handler: pressing a switch wrapper flips it.
BASE_SCRIPT = (
    "<script>"
    "window.__flip = function (w) {"
    " var on = w.getAttribute('aria-checked') !== 'true';"
    " w.setAttribute('aria-checked', on ? 'true' : 'false');"
    " w.querySelector('input[type=\"checkbox\"]').checked = on; };"
    "window.__press = function (event, w) { event.preventDefault(); window.__flip(w); };"
    "</script>"
)


def late_press_script(switch_ms: int, select_ms: int) -> str:
    """The lateness, as one script. PURE. ``None`` leaves that behaviour as it
    was; a negative delay means the change never lands."""
    sw = "null" if switch_ms is None else str(int(switch_ms))
    se = "null" if select_ms is None else str(int(select_ms))
    return (
        "<script>(function () {"
        " var sw = " + sw + ", se = " + se + ";"
        " if (sw !== null && window.__flip) {"
        "  var flip = window.__flip;"
        "  window.__flip = function (w) { if (sw >= 0) { setTimeout(function () { flip(w); }, sw); } };"
        " }"
        " if (se !== null) {"
        "  var remember = function () { document.querySelectorAll('select').forEach(function (s) {"
        "   if (typeof s.__was !== 'number') { s.__was = s.selectedIndex; } }); };"
        "  remember();"
        "  new MutationObserver(remember).observe(document.documentElement, {childList: true, subtree: true});"
        "  document.addEventListener('change', function (e) {"
        "   var s = e.target;"
        "   if (!s || s.tagName !== 'SELECT' || s.__applying) { return; }"
        "   var want = s.selectedIndex; var was = s.__was;"
        "   if (typeof was !== 'number' || want === was) { return; }"
        "   s.selectedIndex = was;"
        "   if (se >= 0) { setTimeout(function () {"
        "    s.__applying = true; s.selectedIndex = want; s.__was = want; s.__applying = false; }, se); }"
        "  }, true);"
        " }"
        "})();</script>"
    )


def make_late_press(html: str, switch_ms: int = DEFAULT_SWITCH_MS,
                    select_ms: int = DEFAULT_SELECT_MS) -> str:
    """The page with the lateness appended before its body closes. PURE."""
    if html.count("</body>") != 1:
        raise ValueError("the page must close its body exactly once")
    return html.replace("</body>", late_press_script(switch_ms, select_ms) + "</body>", 1)


def _selects_html() -> str:
    parts = []
    for label, dom_id, options in SELECTS:
        opts = "".join(
            '<option value="' + ("" if i == 0 else "v" + str(i)) + '">' + text + "</option>"
            for i, text in enumerate(options)
        )
        parts.append('<label for="' + dom_id + '">' + label + "</label>"
                     '<select id="' + dom_id + '">' + opts + "</select>\n")
    return "".join(parts)


def today_shapes(html: str) -> dict:
    """What today's capture draws that this fixture relies on. Counts only."""
    selects = re.findall(r"<select[^>]*>(.*?)</select>", html, re.S)
    shapes = []
    for body in selects:
        values = re.findall(r"<option[^>]*?value=\"([^\"]*)\"", body)
        options = len(re.findall(r"<option\b", body))
        shapes.append((options, sum(1 for v in values if v == ""), bool(values) and values[0] == ""))
    return {
        "save_dialogs": len(re.findall(r"<dialog\b[^>]*>(?:(?!</dialog>).)*>Save</button>", html, re.S)),
        "selects": sorted(shapes),
        "switch_inputs": len(re.findall(r"<input[^>]*role=\"switch\"", html)),
    }


def check_today(html: str) -> None:
    shapes = today_shapes(html)
    wanted = [(len(o), 1, True) for _, _, o in SELECTS]
    have = [s for s in shapes["selects"] if s in wanted]
    if sorted(have) != sorted(wanted):
        raise ValueError("today's capture does not draw the two selects this world is shaped on "
                         "(a 5-option and a 2-option select, each opening on one unset option)")
    if shapes["switch_inputs"] != 2:
        raise ValueError("today's capture draws " + str(shapes["switch_inputs"]) + " switch inputs, not 2")


def build() -> str:
    """The fixture's text, or ValueError if today's capture disagrees."""
    check_today(TODAY.read_text(encoding="ascii"))
    source = SOURCE.read_text(encoding="ascii")
    doctype = "<!doctype html>\n"
    if not source.startswith(doctype):
        raise ValueError("the switch fixture no longer opens on its doctype")
    body = source[len(doctype):]
    # THE BADGE'S TITLE ON ITS BLOCK, as the badge world places it: the one
    # LinkedIn UI string the P B9 ruling admits for aiming, compared in the page.
    if body.count("Placeholder setting B") != 1:
        raise ValueError("the switch fixture no longer draws its second block's placeholder title")
    body = body.replace("Placeholder setting B", BADGE_TITLE, 1)
    body = body.replace('<div role="switch"', '<div role="switch" onclick="__press(event, this)"')
    if body.count('<button type="button">Save</button>') != 1:
        raise ValueError("the switch fixture no longer draws its one Save control")
    body = body.replace('<button type="button">Save</button>',
                        _selects_html() + '<button type="button">Save</button>', 1)
    body = body.replace("<body>", "<body>" + BASE_SCRIPT, 1)
    provenance = (
        "<!-- LATE PRESS: built by scripts/_build_intro_editor_late_press_fixture.py\n"
        "     from intro_editor_switches.html, its two selects shaped as today's\n"
        "     capture draws them. A switch press lands DEFAULT_SWITCH_MS late and a\n"
        "     select change DEFAULT_SELECT_MS late. -->\n"
    )
    return doctype + provenance + make_late_press(body)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the committed fixture is stale")
    args = ap.parse_args(argv)
    try:
        text = build()
    except ValueError as exc:
        print("REFUSED:", exc)
        return 2
    shapes = today_shapes(TODAY.read_text(encoding="ascii"))
    print("today's capture: selects " + str(shapes["selects"]) + ", switch inputs "
          + str(shapes["switch_inputs"]))
    if args.check:
        same = OUT.exists() and OUT.read_text(encoding="ascii") == text
        print("the committed fixture is " + ("current" if same else "STALE"))
        return 0 if same else 1
    OUT.write_text(text, encoding="ascii", newline="\n")
    print("wrote " + OUT.name + ": " + str(len(text)) + " characters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
