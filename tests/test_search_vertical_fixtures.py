"""The groups and events search fixtures ARE the live captures' structure, and synthetic.

Census rows ``N 161`` (search for groups) and ``N 179`` (search for events):
the live lane captured one results page of each (sessions 2 and 3,
2026-09-28) and committed each as a TRACKED copy -- every keyed text one x,
ids kept as their hash -- ``tests/fixtures/live2/n161.html`` and
``tests/fixtures/live3/n179.html``. Those copies are the live-true sources.
The readers in ``linkedin_server/search_vertical_results.py`` are built over
the pages ``scripts/_build_search_vertical_fixtures.py`` made from the same
captures' gitignored skeletons, which carry what the readers need told apart
-- which result each link names -- with every value declared synthetic.

WHAT THIS FILE HOLDS, the named-profile skeleton's approach
(``tests/test_named_profile_live_skeleton.py``) applied to two pages:

1. Each fixture is a FIXED POINT of its committed builder: run over its own
   output, the builder reproduces it byte for byte, so a hand edit of a text,
   a label or a kept attribute does not survive.
2. Each fixture carries the STRUCTURE DIGEST the builder printed from the live
   lane's skeleton (tags and nesting below ``<body>``) -- and the TRACKED
   COPY's body has that digest too, so anybody can re-derive the tie from
   tracked files.
3. The words kept verbatim are the live lane's words, on its closed list.
4. What the readers rest on, measured on the fixtures: the result links, the
   synthetic ids, the link-in-a-link of an event card, and every title reduced
   to shape.

Each guard is shown failing (``THIS_CONTROL_CAN_FAIL``).
"""
from __future__ import annotations

import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from tests.test_fixtures_hold_only_synthetic_people import PLANTED, is_reduced_to_shape

REPO = Path(__file__).resolve().parent.parent
BUILDER = REPO / "scripts" / "_build_search_vertical_fixtures.py"
SYNTHETIC = REPO / "tests" / "fixtures" / "synthetic"
XHTML = "{http://www.w3.org/1999/xhtml}"

#: Per vertical: the fixture, the live lane's tracked copy of the same
#: capture, and THE STRUCTURE DIGEST the builder printed when run over the
#: live lane's keyed skeleton on 2026-10-10 (lane B2's child; the skeletons
#: are gitignored, under the live lane's _state/live2 and _state/live3).
#: Whoever holds a skeleton can re-derive it; a structural hand edit of a
#: fixture or a tracked copy changes it.
PAGES = {
    "groups": {
        "fixture": SYNTHETIC / "search_groups_live.html",
        "source": REPO / "tests" / "fixtures" / "live2" / "n161.html",
        "digest": "caaocajhampndjac",
    },
    "events": {
        "fixture": SYNTHETIC / "search_events_live.html",
        "source": REPO / "tests" / "fixtures" / "live3" / "n179.html",
        "digest": "kmcbjofakiepohli",
    },
}
VERTICALS = sorted(PAGES)

#: What the captures draw, measured on the skeletons by shape (and on the
#: tracked copies by count): nine groups, each linked once, ids of 5, 7 and 8
#: digits; thirteen events, each linked twice, ids of 19 digits.
GROUP_ID_LENGTHS = (5, 5, 7, 7, 7, 5, 5, 7, 8)
EVENTS = 13
EVENT_ID_LENGTH = 19


def _rebuild(vertical: str, source: Path, out: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BUILDER), "--vertical", vertical, "--skeleton", str(source),
         "--out", str(out)],
        capture_output=True, text=True, cwd=REPO,
    )


def _printed(stdout: str, label: str) -> str:
    lines = [line for line in stdout.splitlines() if line.startswith(label)]
    assert len(lines) == 1, stdout
    return lines[0][len(label):].strip()


def _lf(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def _text(vertical: str) -> str:
    return PAGES[vertical]["fixture"].read_text(encoding="ascii")


def _digest_of_body(text: str) -> str:
    """The builder's own structure digest over a page's ``<body>`` -- the
    function it prints from (the named-profile builder's), not a second
    reading of it."""
    sys.path.insert(0, str(REPO / "scripts"))
    import _build_named_profile_skeleton as named

    tree = named.Tree()
    tree.feed(text)
    tree.close()
    body = next(node for node in named.walk(tree.root) if node.tag == "body")
    return named.structure_digest(body)


def _root(vertical: str) -> ET.Element:
    """The fixture parsed by an XML parser -- the DOCTYPE line skipped."""
    return ET.fromstring(_text(vertical).split("\n", 1)[1])


def _result_id(href: str, word: str):
    found = re.fullmatch(r"/%s/([0-9]+)/" % word, href or "")
    return found.group(1) if found else None


# ---------------------------------------------------------------------------
# 1. A fixed point of the committed builder
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("vertical", VERTICALS)
def test_each_fixture_is_a_fixed_point_of_its_committed_builder(vertical, tmp_path):
    out = tmp_path / "rebuilt.html"
    run = _rebuild(vertical, PAGES[vertical]["fixture"], out)
    assert run.returncode == 0, run.stderr
    assert _lf(out.read_bytes()) == _lf(PAGES[vertical]["fixture"].read_bytes())
    for label in ("reduced text", "unclassified text", "unclassified labels",
                  "unclassified attributes", "ids mapped"):
        assert _printed(run.stdout, label) == "0", label


@pytest.mark.parametrize("vertical", VERTICALS)
def test_THIS_CONTROL_CAN_FAIL_a_hand_edit_of_a_title_breaks_the_fixed_point(vertical, tmp_path):
    """A title written back as a name does not survive: it is neither a shape,
    a reduced shape nor one of LinkedIn's words, so it comes back the
    placeholder and is counted."""
    text = _text(vertical)
    title = re.search(r'href="/%s/[0-9]+/"[^>]*>(?:<[^>]+>)*?<p>([Xx9 ]+)</p>' % vertical, text)
    if vertical == "events":
        title = re.search(r'<p><a href="/events/[0-9]+/">([Xx9 ]+)</a></p>', text)
    assert title is not None
    edited = tmp_path / "edited.html"
    edited.write_text(text.replace(title.group(1), PLANTED, 1), encoding="ascii")
    out = tmp_path / "rebuilt.html"
    run = _rebuild(vertical, edited, out)
    assert run.returncode == 0, run.stderr
    assert PLANTED not in out.read_text(encoding="ascii")
    assert _printed(run.stdout, "unclassified text") == "1"
    assert _lf(out.read_bytes()) != _lf(edited.read_bytes())


@pytest.mark.parametrize("vertical", VERTICALS)
def test_THIS_CONTROL_CAN_FAIL_a_hand_edit_in_a_kept_attribute_or_an_id_breaks_it(vertical, tmp_path):
    """A canary in ``role`` is dropped and counted; a result id edited by hand
    is put back to the declared run, so neither is a fixed point."""
    text = _text(vertical)
    planted = text.replace('role="list"', 'role="' + PLANTED + '"', 1)
    first = re.search(r'href="/%s/([0-9]+)/"' % vertical, planted)
    planted = planted.replace(first.group(1), "9" * len(first.group(1)))
    edited = tmp_path / "edited.html"
    edited.write_text(planted, encoding="ascii")
    out = tmp_path / "rebuilt.html"
    run = _rebuild(vertical, edited, out)
    assert run.returncode == 0, run.stderr
    rebuilt = out.read_text(encoding="ascii")
    assert PLANTED not in rebuilt
    assert _printed(run.stdout, "unclassified attributes") == "1"
    assert "/%s/%s/" % (vertical, "9" * len(first.group(1))) not in rebuilt
    assert _lf(out.read_bytes()) != _lf(edited.read_bytes())


# ---------------------------------------------------------------------------
# 2. The capture's structure, tied to the tracked copy
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("vertical", VERTICALS)
def test_each_fixture_carries_the_structure_the_builder_printed_from_the_capture(vertical, tmp_path):
    run = _rebuild(vertical, PAGES[vertical]["fixture"], tmp_path / "rebuilt.html")
    assert run.returncode == 0, run.stderr
    assert _printed(run.stdout, "structure digest") == PAGES[vertical]["digest"]


@pytest.mark.parametrize("vertical", VERTICALS)
def test_each_page_is_built_from_the_capture_whose_tracked_copy_is_the_source(vertical):
    """ONE LIVE-TRUE SOURCE: over the tracked copy's body the builder's digest
    is the one it printed from the skeleton, and the fixture's."""
    source = PAGES[vertical]["source"].read_text(encoding="ascii")
    assert _digest_of_body(source) == PAGES[vertical]["digest"]
    assert _digest_of_body(_text(vertical)) == PAGES[vertical]["digest"]


@pytest.mark.parametrize("vertical", VERTICALS)
def test_THIS_CONTROL_CAN_FAIL_a_structural_edit_of_the_source_breaks_the_tie(vertical):
    source = PAGES[vertical]["source"].read_text(encoding="ascii")
    edited = re.sub(r"<hr [^>]*>", "", source, count=1)
    assert edited != source
    assert _digest_of_body(edited) != PAGES[vertical]["digest"]


@pytest.mark.parametrize("vertical", VERTICALS)
def test_THIS_CONTROL_CAN_FAIL_a_structural_edit_of_the_fixture_changes_the_digest(vertical, tmp_path):
    text = _text(vertical)
    stripped = re.sub(r"<svg[^>]*></svg>", "", text)
    assert stripped != text
    edited = tmp_path / "edited.html"
    edited.write_text(stripped, encoding="ascii")
    run = _rebuild(vertical, edited, tmp_path / "rebuilt.html")
    assert run.returncode == 0, run.stderr
    assert _printed(run.stdout, "structure digest") != PAGES[vertical]["digest"]


@pytest.mark.parametrize("vertical", VERTICALS)
def test_each_page_names_its_live_true_source(vertical):
    text = _text(vertical)
    assert "THE LIVE-TRUE SOURCE IS THE LIVE LANE'S TRACKED COPY" in text
    assert PAGES[vertical]["source"].relative_to(REPO).as_posix() in text


# ---------------------------------------------------------------------------
# 3. The words kept are the live lane's
# ---------------------------------------------------------------------------


def test_the_words_the_builder_keeps_are_the_words_the_live_lane_kept():
    sys.path.insert(0, str(REPO / "scripts"))
    import _build_search_vertical_fixtures as builder
    import _probe_live_lane_session_2 as live

    assert builder.KEPT_WORDS <= live.FURNITURE, builder.KEPT_WORDS - live.FURNITURE
    assert builder.KEPT_LABELS <= live.FURNITURE, builder.KEPT_LABELS - live.FURNITURE


def test_the_builder_extends_the_named_profile_builder_rather_than_copying_it():
    """Its parser, walk, shape reduction, escaping, kept vocabularies and
    digest are IMPORTED, so the two cannot drift on what they mean."""
    source = BUILDER.read_text(encoding="ascii")
    assert "import _build_named_profile_skeleton as named" in source
    for helper in ("named.Tree", "named.walk", "named.reduced", "named.escape",
                   "named.structure_digest", "named.KEPT", "named.kept_value"):
        assert helper in source, helper
    for copied in ("def reduced(", "def escape(", "def structure_digest(", "class Tree("):
        assert copied not in source, copied


# ---------------------------------------------------------------------------
# 4. What the readers rest on, measured on the fixtures
# ---------------------------------------------------------------------------


def test_the_groups_fixture_draws_nine_results_each_a_link_wrapping_its_list_item():
    root = _root("groups")
    links = [a for a in root.iter(XHTML + "a") if _result_id(a.get("href"), "groups")]
    assert len(links) == len(GROUP_ID_LENGTHS)
    ids = [_result_id(a.get("href"), "groups") for a in links]
    assert [len(i) for i in ids] == list(GROUP_ID_LENGTHS)
    assert len(set(ids)) == len(ids), "each group is linked once"
    for link in links:
        items = [e for e in link.iter() if e.get("role") == "listitem"]
        assert len(items) == 1
        nested = [a for a in link.iter(XHTML + "a") if a is not link]
        assert nested == []
        titles = list(items[0].iter(XHTML + "p"))
        assert titles and len(list(titles[0])) == 0, "the title paragraph holds text only"
        assert is_reduced_to_shape(titles[0].text or "")


def test_the_events_fixture_draws_thirteen_results_each_a_link_holding_its_title_link():
    root = _root("events")
    cards = []
    for anchor in root.iter(XHTML + "a"):
        href = anchor.get("href")
        if _result_id(href, "events") and any(
            inner is not anchor and inner.get("href") == href for inner in anchor.iter(XHTML + "a")
        ):
            cards.append(anchor)
    assert len(cards) == EVENTS
    ids = [_result_id(card.get("href"), "events") for card in cards]
    assert len(set(ids)) == EVENTS
    assert all(len(i) == EVENT_ID_LENGTH for i in ids)
    for card in cards:
        inner = [a for a in card.iter(XHTML + "a") if a is not card]
        assert len(inner) == 1 and inner[0].get("href") == card.get("href")
        assert len(list(inner[0])) == 0, "the title link holds text only"
        assert is_reduced_to_shape(inner[0].text or "")
    every = [a for a in root.iter(XHTML + "a") if _result_id(a.get("href"), "events")]
    assert len(every) == 2 * EVENTS, "each event is linked twice"


@pytest.mark.parametrize("vertical", VERTICALS)
def test_every_result_id_is_the_declared_synthetic_run_in_order(vertical):
    """"1", then the result's number, zero-padded to the captured length."""
    seen: list[str] = []
    for anchor in _root(vertical).iter(XHTML + "a"):
        found = _result_id(anchor.get("href"), vertical)
        if found and found not in seen:
            seen.append(found)
    assert seen, "no result id read"
    for number, value in enumerate(seen, 1):
        assert value == "1" + str(number).zfill(len(value) - 1), value


@pytest.mark.parametrize("vertical", VERTICALS)
def test_THIS_CONTROL_CAN_FAIL_the_xml_parse_refuses_html_void_syntax(vertical):
    """The fixture is well-formed XHTML; the same page with one void element
    written as HTML writes it is not, so the parse above is a real check."""
    broken = _text(vertical).replace("<hr role=\"presentation\" />", "<hr role=\"presentation\">", 1)
    assert broken != _text(vertical)
    with pytest.raises(ET.ParseError):
        ET.fromstring(broken.split("\n", 1)[1])
