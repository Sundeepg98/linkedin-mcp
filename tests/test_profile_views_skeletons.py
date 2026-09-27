"""THE PROFILE-VIEWS SKELETONS: fixed points of their committed builder,
carrying the structure it printed from each capture, and carrying nobody.

``scripts/_build_profile_views_skeleton.py`` wrote the four files below from
raw captures of ``/analytics/profile-views/`` taken in live-lane session 1
(``_audit/2026-09-23-live-lane-session-1.md``). The captures are never
committed: they list other members. The skeletons keep the page's elements,
tags and nesting, a closed set of attributes, LinkedIn's own interface words
from the builder's declared allowlist, and plain numbers; every other text is
REDUCED TO SHAPE (letters to X or x, digits and punctuation kept).

    profile_views_closed.html     Entry 3's load, every filter pill closed
    profile_views_pill_open.html  the same load, "Interesting viewers" open
    profile_views_verify.html     Entry 7's fresh plain load after the switch
    profile_views_revealed.html   Entry 7's switch run at its end, "Show more
                                  analytics" pressed, Highlights and Details
                                  drawn

What is held here, and why each is separate:

1. A FIXED POINT: the builder run over a skeleton reproduces it byte for byte.
   That pins the TEXT -- which words were kept and which were shaped -- and a
   builder changed without re-running it. It does NOT pin the structure: an
   element deleted by hand leaves a file that is still a fixed point.
2. THE STRUCTURE DIGEST the builder printed from each CAPTURE, pinned. That
   pins the tags and their nesting; a structural hand edit changes it.
3. NOBODY: every text node and every aria-label is an allowlisted interface
   phrase, a number, or a shape; every href is a member shape or a route.
4. THE STATES: each file is the state it is named for, by counts only --
   which is what makes it usable as the before or after of a press.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

import pytest

REPO = Path(__file__).resolve().parent.parent
BUILDER = REPO / "scripts" / "_build_profile_views_skeleton.py"
SYNTHETIC = REPO / "tests" / "fixtures" / "synthetic"

#: Each skeleton, and the STRUCTURE DIGEST the builder printed when it ran over
#: the raw capture of that state on 2026-09-28 (lane G, slice S). Whoever holds
#: a capture can re-derive it; a structural hand edit of a skeleton changes it.
SKELETONS = {
    "profile_views_closed.html": "locnhnioigchomef",
    "profile_views_pill_open.html": "dklngmfjfhjbnlnf",
    "profile_views_verify.html": "bnobgmligemmjlck",
    "profile_views_revealed.html": "nkooebifhbbjjkkm",
}

#: An invented, undeclared name for the controls below -- the plant the
#: synthetic-people guard uses for its own.
PLANTED_NAME = "Zzqx Plantperson"


def _builder():
    spec = importlib.util.spec_from_file_location("_profile_views_builder", BUILDER)
    assert spec is not None and spec.loader is not None, BUILDER
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B = _builder()


def _rebuild(source: Path, out: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BUILDER), "--capture", str(source), "--out", str(out)],
        capture_output=True, text=True, cwd=REPO,
    )


def _printed_digest(stdout: str) -> str:
    lines = [line for line in stdout.splitlines() if line.startswith("structure digest ")]
    assert len(lines) == 1, stdout
    return lines[0].split()[-1]


def _lf(data: bytes) -> bytes:
    """Line endings only: a Windows checkout with autocrlf hands the skeleton
    over with CRLF, and the builder writes LF."""
    return data.replace(b"\r\n", b"\n")


def _body(text: str):
    tree = B.Tree()
    tree.feed(text)
    tree.close()
    return next(node for node in B.walk(tree.root) if node.tag == "body")


def _attr(node, name):
    for key, value in node.attrs:
        if key == name:
            return value if value is not None else ""
    return None


def _text_of(node) -> str:
    parts = []
    if node.tag not in B.FOREIGN and node.tag not in B.VOID:
        for item in B.kept_children(node):
            if isinstance(item, str):
                parts.append(item)
            else:
                parts.append(_text_of(item))
    return " ".join(" ".join(parts).split())


def _inside(node, ancestor) -> bool:
    walker = node.parent
    while walker is not None:
        if walker is ancestor:
            return True
        walker = walker.parent
    return False


# ---------------------------------------------------------------------------
# 1-2. Fixed point and structure
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", sorted(SKELETONS))
def test_each_skeleton_is_a_fixed_point_of_its_committed_builder(name, tmp_path):
    out = tmp_path / "rebuilt.html"
    run = _rebuild(SYNTHETIC / name, out)
    assert run.returncode == 0, run.stderr
    assert _lf(out.read_bytes()) == _lf((SYNTHETIC / name).read_bytes())


@pytest.mark.parametrize("name", sorted(SKELETONS))
def test_each_skeleton_carries_the_structure_its_capture_had(name, tmp_path):
    run = _rebuild(SYNTHETIC / name, tmp_path / "rebuilt.html")
    assert run.returncode == 0, run.stderr
    assert _printed_digest(run.stdout) == SKELETONS[name]


def test_THIS_CONTROL_CAN_FAIL_a_structural_hand_edit_changes_the_digest(tmp_path):
    """The edit the fixed point lets through: one <hr> in main deleted, with
    the builder's own line break before it."""
    text = (SYNTHETIC / "profile_views_closed.html").read_text(encoding="ascii").replace("\r\n", "\n")
    found = re.compile(r"\n?<hr(?: [^>]*)?>").search(text, text.index("<main"))
    assert found is not None
    edited = tmp_path / "edited.html"
    edited.write_bytes((text[: found.start()] + text[found.end():]).encode("ascii"))
    out = tmp_path / "rebuilt.html"
    run = _rebuild(edited, out)
    assert run.returncode == 0, run.stderr
    assert _printed_digest(run.stdout) != SKELETONS["profile_views_closed.html"]
    # ...and it IS still a fixed point: the digest is what caught it.
    assert out.read_bytes() == edited.read_bytes()


def test_THIS_CONTROL_CAN_FAIL_a_text_hand_edit_breaks_the_fixed_point(tmp_path):
    """A kept interface word edited to one the allowlist does not hold is
    shaped by the builder, so the file stops being a fixed point."""
    text = (SYNTHETIC / "profile_views_closed.html").read_text(encoding="ascii").replace("\r\n", "\n")
    assert ">Reset<" in text
    edited = tmp_path / "edited.html"
    edited.write_bytes(text.replace(">Reset<", ">Resat<", 1).encode("ascii"))
    out = tmp_path / "rebuilt.html"
    assert _rebuild(edited, out).returncode == 0
    assert out.read_bytes() != edited.read_bytes()


def test_the_builder_refuses_a_page_with_no_main_and_quotes_nothing(tmp_path):
    page = tmp_path / "no-main.html"
    page.write_text("<!DOCTYPE html><html><body><div><p>%s</p></div></body></html>\n" % PLANTED_NAME,
                    encoding="ascii")
    out = tmp_path / "out.html"
    run = _rebuild(page, out)
    assert run.returncode != 0
    assert not out.exists()
    assert "no <main>" in run.stderr
    assert PLANTED_NAME not in run.stdout + run.stderr


# ---------------------------------------------------------------------------
# 3. Nobody
# ---------------------------------------------------------------------------


def _shape_only(text: str) -> bool:
    for character in text:
        if character in "Xx" or character.isdigit() or character.isspace():
            continue
        if character.isascii() and not character.isalnum():
            continue
        if not character.isascii() and unicodedata.category(character)[0] == "P":
            continue
        return False
    return True


def _unexplained_texts(text: str) -> list[str]:
    """Kind labels (never values) of each text node or aria-label that is not
    an allowlisted phrase, a number, or a shape."""
    bad = []
    for element in B.kept_elements(_body(text)):
        label = _attr(element, "aria-label")
        values = [("aria-label", label)] if label else []
        if element.tag not in B.FOREIGN and element.tag not in B.VOID:
            values += [("text", item) for item in B.kept_children(element)
                       if isinstance(item, str) and not B.is_formatting(item)]
        for kind, value in values:
            value = B.collapse(value)
            if not (B.allowlisted(value) or B.is_numeric(value) or _shape_only(value)):
                bad.append(kind)
    return bad


@pytest.mark.parametrize("name", sorted(SKELETONS))
def test_every_text_and_label_is_interface_text_a_number_or_a_shape(name):
    assert _unexplained_texts((SYNTHETIC / name).read_text(encoding="ascii")) == []


def test_THIS_CONTROL_CAN_FAIL_a_name_planted_in_a_skeleton_is_caught():
    text = (SYNTHETIC / "profile_views_closed.html").read_text(encoding="ascii")
    planted = text.replace("</main>", "<p>%s</p></main>" % PLANTED_NAME, 1)
    labelled = text.replace("<main", '<main aria-label="Send a message to %s"' % PLANTED_NAME, 1)
    assert _unexplained_texts(planted) == ["text"]
    assert _unexplained_texts(labelled) == ["aria-label"]


_MEMBER_SHAPE = re.compile(r"https://www\.linkedin\.com/in/[x0_%-]+/")


def _unexplained_hrefs(text: str) -> int:
    bad = 0
    for element in B.kept_elements(_body(text)):
        href = _attr(element, "href")
        if href is None or _MEMBER_SHAPE.fullmatch(href):
            continue
        parts = urlsplit(href)
        host_ok = (not parts.netloc or parts.netloc in B.LINKEDIN_HOSTS
                   or "https://" + parts.netloc == B.PLACEHOLDER_HOST)
        segments = [s for s in parts.path.split("/") if s]
        if not (host_ok and not parts.query and not parts.fragment
                and all(s in B.ROUTE_WORDS or s == B.PLACEHOLDER_SEGMENT for s in segments)):
            bad += 1
    return bad


@pytest.mark.parametrize("name", sorted(SKELETONS))
def test_every_href_is_a_member_shape_or_a_route(name):
    assert _unexplained_hrefs((SYNTHETIC / name).read_text(encoding="ascii")) == 0


#: A raw member address for the control below: the synthetic-people guard's
#: plant, whose slug carries tokens the identity guard already sanctions, so
#: this file adds no identifier for that guard to find.
PLANT_MEMBER = "/in/someone-placeholder-0001/"


def test_THIS_CONTROL_CAN_FAIL_a_raw_member_link_is_caught():
    text = (SYNTHETIC / "profile_views_closed.html").read_text(encoding="ascii")
    planted = text.replace("</main>", '<a href="%s">x</a></main>' % PLANT_MEMBER, 1)
    assert _unexplained_hrefs(planted) == 1


# ---------------------------------------------------------------------------
# 4. The states, by counts
# ---------------------------------------------------------------------------


def _state(name: str) -> dict:
    body = _body((SYNTHETIC / name).read_text(encoding="ascii"))
    every = list(B.kept_elements(body))
    main = next(node for node in every if node.tag == "main")
    buttons = [node for node in every if node.tag == "button"]
    options = [node for node in every
               if _attr(node, "role") in ("checkbox", "radio") and _attr(node, "aria-label") is not None]
    headings = [B.match_key(_text_of(node)) for node in every if _inside(node, main)
                and (node.tag in ("h1", "h2", "h3", "h4", "h5", "h6") or _attr(node, "role") == "heading")]
    return {
        "expanded_true_in_main": sum(1 for node in every if _inside(node, main)
                                     and _attr(node, "aria-expanded") == "true"),
        "options": len(options),
        "options_checked": sorted(_attr(node, "aria-checked") for node in options),
        "show_more_analytics": sum(1 for b in buttons if B.match_key(_text_of(b)) == "show more analytics"),
        "show_results": sum(1 for b in buttons if B.match_key(_text_of(b)) == "show results"),
        "highlights": headings.count("highlights"),
        "details": headings.count("details"),
    }


CLOSED = {"expanded_true_in_main": 0, "options": 0, "options_checked": [],
          "show_more_analytics": 1, "show_results": 0, "highlights": 0, "details": 0}


@pytest.mark.parametrize(
    "name, expected",
    [
        ("profile_views_closed.html", CLOSED),
        ("profile_views_verify.html", CLOSED),
        ("profile_views_pill_open.html",
         {**CLOSED, "expanded_true_in_main": 1, "options": 2,
          "options_checked": ["false", "false"], "show_results": 1}),
        ("profile_views_revealed.html",
         {**CLOSED, "show_more_analytics": 0, "highlights": 1, "details": 1}),
    ],
)
def test_each_skeleton_is_the_state_it_is_named_for(name, expected):
    assert _state(name) == expected
