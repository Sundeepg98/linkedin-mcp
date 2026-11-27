"""Build session 12's skeletons WITH THEIR MEASURED WORDS into committed fixtures: the AI job search (two loads), the resume card's open menu, the tracker's open Date posted pill, an organisation's Products tab and three Learning pages.

Kept as the PROVENANCE of the ``tests/fixtures/live12/*_words.html`` fixtures
lane jobs7 builds its readers and its census moves over, 2026-11-27
(``_audit/2026-11-27-jobs7.md``).

THE INPUT is the gitignored KEYED skeleton the live lane wrote in session 12
(``<session dir>/<capture>.skeleton.html``, every text and attribute value a
keyed shape ``{L<letters>D<digits>n<length>:<8-hex hash>}``), that session's
key (``<session dir>/shape.key``) and, for the two job searches, the session's
own reading of the load (``<session dir>/<capture>.json``). All are read, none
is written anywhere, and nothing here prints a hash, the key or a value it
read. The committed copy ``tests/fixtures/live12/<capture>.html`` is
``tracked_copy`` of the same skeleton; this script recomputes that copy and
REFUSES unless it is identical to the committed one, so the input is shown to
be the capture the repository already holds.

WHAT IT CHANGES, in two classes, each declared per fixture in :data:`SPEC`:

1. **LINKEDIN'S OWN WORDS** -- a closed list per fixture: a pill's label, a
   chip, a posted line, a results total, a pager's test id, the SDUI screen's
   name. A keyed shape is replaced by a word ONLY where ``value_shape(word,
   key)`` equals it, as a whole text or a whole attribute value: a MEASURED
   word, never an assumed one. A word that matches nowhere REFUSES the build
   (``scripts/_build_live11_word_skeletons.py``'s rule, its ``build`` reused).
   Every list was measured first by lane jobs7's scratch probe, which hashed
   each candidate against the skeleton and printed only counts, with a random
   key as its negative control (0 hits in 3180 candidates on both searches).

2. **TWO CODE-VOCABULARY KEYS WHOSE VALUES CARRY DATA** (the job searches
   only). A result card is keyed ``job-card-component-ref-<posting id>`` and
   the alert switch ``JobSearchAlertToggleRef_<query words>_<8 digits>_<1
   digit>``. Their values hold a posting id and his query, so no candidate can
   be hashed for them; the key's GRAMMAR is what is measured instead, by the
   SHAPE the skeleton keeps (letters, digits, length):

   * a card key is a ``componentkey`` of 19 letters, at least 6 digits and
     length 23 + digits -- ``job-card-component-ref-`` and a digit run, and
     nothing else -- appearing EXACTLY TWICE, the second copy inside the first
     (each AI card holds one inner keyed copy, search-fix26's measurement on
     session 11's raw page). The number of such outer cards must EQUAL the
     session's own reading of the load (``evidence.ai_cards``, taken live on
     the raw page by the shipped ``job_search_route.render_evidence``, whose
     card test is the real key's regex). Two channels, or the build refuses.
     Each card's two copies take ONE synthetic posting id.
   * the alert key is the ``componentkey`` on the page's one
     ``input[role=switch]``'s nearest keyed ancestors, with exactly 9 digits
     (8 + 1, the grammar's two runs), appearing EXACTLY TWICE, nested. It is
     written as :data:`ALERT_KEY_SYNTHETIC`, the spelling session 11's fixture
     carries.

Every other value is reduced exactly as ``tracked_copy`` reduces it. Third
parties' text -- a job's title, an employer, a place, a course, a product --
stays ``x``; a test that needs one plants a synthetic string into the slot
LinkedIn drew.

    python scripts/_build_jobs7_word_skeletons.py --session-dir <dir> [--only NAME] [--check]

``--check`` writes nothing and exits non-zero if a committed fixture differs
from what this would write. Prints counts and a sha256 digest per fixture,
never a value it read.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import _build_live11_word_skeletons as w11  # noqa: E402  build (words, then tracked_copy)
import _probe_live_lane_session_2 as s2  # noqa: E402  value_shape, tracked_copy

FIXTURES = REPO / "tests" / "fixtures" / "live12"

#: The alert key as session 11's fixture spells it
#: (``scripts/_build_ai_job_search_skeleton.py``): the prefix LinkedIn writes,
#: neutral query words, and the grammar's two digit runs.
ALERT_KEY_SYNTHETIC = "JobSearchAlertToggleRef_synthetic_role_00000000_0"

#: The card key's prefix, LinkedIn's own (search-fix26, session 11's raw page:
#: 50 keyed, 25 outermost, every one this prefix and ten digits).
CARD_KEY_PREFIX = "job-card-component-ref-"

_KEYED = re.compile(r"\{L(\d{1,7})D(\d{1,7})n(\d{1,7}):([0-9a-f]{8})\}")
_KEYED_WHOLE = re.compile(r"^\{L(\d{1,7})D(\d{1,7})n(\d{1,7}):([0-9a-f]{8})\}$")
_COMPONENTKEY = re.compile(r'componentkey="(\{L\d{1,7}D\d{1,7}n\d{1,7}:[0-9a-f]{8}\})"')

_UNITS = ("second", "minute", "hour", "day", "week", "month", "year")


def _posted(*pairs: tuple[int, str]) -> tuple[str, ...]:
    """Each ``N unit ago`` age, and its ``Posted`` line, for the given pairs."""
    out: list[str] = []
    for n, unit in pairs:
        assert unit in _UNITS
        word = unit if n == 1 else unit + "s"
        out += [f"{n} {word} ago", f"Posted {n} {word} ago"]
    return tuple(out)


#: Pager test ids, LinkedIn's code vocabulary.
def _pager(indicators: int, nxt: str) -> tuple[str, ...]:
    return tuple(
        [f"pagination-indicator-{i}" for i in range(indicators)]
        + ["pagination-controls-list", f"pagination-controls-next-button-{nxt}",
           "pagination-controls-prev-button-hidden"]
    )


#: The AI search's furniture both loads drew (measured on each).
_AI_COMMON: tuple[str, ...] = (
    "com.linkedin.sdui.flagshipnav.jobs.SemanticJobDetails",
    "true",
    "Easy Apply",
    "Filter by Easy Apply",
    "Get job alerts for this search",
    "Actively reviewing applicants",
)

#: fixture stem -> (capture stem, closed words, the first synthetic posting id
#: for its cards or None, alert key?). Every word was measured by hashing it
#: with session 12's key against the keyed skeleton (lane jobs7's record,
#: section 2).
SPEC: dict[str, tuple[str, tuple[str, ...], Optional[int], bool]] = {
    # J 1, J 20, J 31, J 40: load 3, the classic address REDIRECTED to the AI
    # route (C-SRCH-1). 25 cards, 99+ results, three pages, Next visible.
    "c_srch_1_words": (
        "c_srch_1",
        _AI_COMMON
        + ("99+ results",)
        + _pager(3, "visible")
        + _posted((1, "day"), (1, "week"), (1, "month"), (2, "week"), (2, "month"),
                  (3, "day"), (3, "week"), (4, "month"), (5, "day"), (6, "day"))
        + ("3 school alumni work here", "1 school alumni works here"),
        4000000201,
        True,
    ),
    # The same, load 4, asked for at the AI route's own address (C-SRCH-0b):
    # 18 cards, 18 results, one page, Next hidden; a reposted card; a
    # connection's proximity line.
    "c_srch_0b_words": (
        "c_srch_0b",
        _AI_COMMON
        + ("Be an early applicant", "18 results")
        + _pager(1, "hidden")
        + _posted((1, "day"), (1, "week"), (1, "month"), (2, "week"), (3, "day"),
                  (3, "week"), (5, "month"), (6, "month"), (11, "hour"), (23, "hour"))
        + ("Reposted 3 days ago", "1 school alumni works here", "1 connection works here"),
        4000000301,
        True,
    ),
    # J 71, J 72, P M1, P M3, P M4: load 9, his application settings page with
    # the first resume card's options menu OPEN (C-RJ26-3). The page's ten
    # words session 11 measured, all drawn again, and the menu's `Download`;
    # its `Delete` is a furniture word the tracked copy already keeps.
    "c_rj26_3_resume_menu-open_words": (
        "c_rj26_3_resume_menu-open",
        (
            "Resumes and application data",
            "Save resumes and application data",
            "Allow LinkedIn to save your resumes and answers to application "
            "questions. You may change your answers with each application.",
            "Learn more about saved application data",
            "Allow LinkedIn to save your resumes and answers",
            "Share resume data with hirers",
            "Hirers can view skills and experiences from the resumes you choose "
            "to share when they search and view profiles and evaluate applicants "
            "through LinkedIn" + chr(0x2019) + "s hiring tools.",
            "Allow recruiters to view your resumes",
            "Upload resume",
            "DOC, DOCX, PDF (5MB)",
            "Download",
        ),
        None,
        False,
    ),
    # J 111: load 21, an organisation's Products tab (C-RJ26-2). The Page
    # navigation's three tab words that are not furniture, the products
    # button's label, the region's link word, and LinkedIn's PATH WORD
    # `products` -- each address segment is its own keyed shape, so the word
    # is written where it matched (the tab's own address, each product's page,
    # the category search) and every slug beside it stays x; every product's
    # own words stay x.
    "c_rj26_2_products_words": (
        "c_rj26_2_products",
        ("Products", "Life", "Insights", "Show all products", "Learn more", "products"),
        None,
        False,
    ),
    # J 114, J 169, J 174: load 20, an organisation's Premium Insights tab
    # with the job-openings card's Functions dropdown OPEN (C-RJ26-1). The
    # module headings, the three screen-reader tables' summaries and header
    # words, the tab word, and the words of LinkedIn's own function list the
    # page drew (the headcount table's `Education` the capture kept plain).
    # Every figure, every growth cell and every member card's words stay x.
    "c_rj26_1_functions-open_words": (
        "c_rj26_1_functions-open",
        (
            "Hiring trends", "Total job openings", "Total employee count",
            "Employee distribution and headcount growth by function",
            "Headcount growth by function", "Notable company alumni", "Headcount growth",
            "Functions", "Insights",
            "Function", "Number of employees", "Percentage of total headcount",
            "3 month growth", "6 month growth", "1 year growth",
            "6m growth", "1y growth", "2y growth",
            "Engineering", "Information Technology", "Sales", "Program and Project Management",
            "Operations", "Product Management", "Business Development", "Arts and Design",
            "Marketing", "Finance", "Support", "Research", "Administrative", "Human Resources",
        ),
        None,
        False,
    ),
}


def header(stem: str, capture: str, words: tuple[str, ...], first_id: Optional[int]) -> str:
    listed = "\n".join("    " + html.escape(w, quote=False).encode("ascii", "xmlcharrefreplace").decode("ascii")
                       for w in words)
    keys = (
        "  and two keys written by their GRAMMAR's shape (each card's posting id\n"
        f"  synthetic, {first_id} upward; the alert key's query words neutral),\n"
        "  refused unless the card count equals the session's own live reading.\n"
        if first_id is not None else ""
    )
    return (
        "<!doctype html>\n<!--\n"
        "  LANE JOBS7, 2026-11-27: built by\n"
        "  scripts/_build_jobs7_word_skeletons.py from the live lane's SESSION-12\n"
        f"  keyed skeleton of {capture}, the same skeleton\n"
        f"  tests/fixtures/live12/{capture}.html is the tracked copy of. Identical to\n"
        "  that copy except where one of these LinkedIn words was written, each only\n"
        "  where its keyed shape matched; every other text is x, as in that copy:\n"
        f"{listed}\n"
        f"{keys}"
        "-->\n"
    )


# ---------------------------------------------------------------------------
# The two grammar-shaped keys
# ---------------------------------------------------------------------------


class _Node:
    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag: str, attrs: dict, parent: Optional["_Node"]):
        self.tag, self.attrs, self.parent = tag, attrs, parent
        self.children: list[_Node] = []


_VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input",
                   "link", "meta", "param", "source", "track", "wbr"})


def _tree(markup: str) -> _Node:
    from html.parser import HTMLParser

    class _T(HTMLParser):
        def __init__(self) -> None:
            super().__init__(convert_charrefs=True)
            self.root = _Node("#root", {}, None)
            self.cur = self.root

        def handle_starttag(self, tag, attrs):
            node = _Node(tag, dict(attrs), self.cur)
            self.cur.children.append(node)
            if tag not in _VOID:
                self.cur = node

        def handle_startendtag(self, tag, attrs):
            self.cur.children.append(_Node(tag, dict(attrs), self.cur))

        def handle_endtag(self, tag):
            walker = self.cur
            while walker is not None and walker.tag != tag:
                walker = walker.parent
            if walker is not None and walker.parent is not None:
                self.cur = walker.parent

    parser = _T()
    parser.feed(markup)
    parser.close()
    return parser.root


def _walk(node: _Node):
    stack = [node]
    while stack:
        cur = stack.pop()
        yield cur
        stack.extend(reversed(cur.children))


def _shape(value: Any) -> Optional[tuple[int, int, int]]:
    match = _KEYED_WHOLE.match(value or "")
    return tuple(int(x) for x in match.groups()[:3]) if match else None  # type: ignore[return-value]


def _is_card_grammar(shape: Optional[tuple[int, int, int]]) -> bool:
    """19 letters, at least 6 digits, length 23 + digits: the prefix and a run."""
    return bool(shape) and shape[0] == 19 and shape[1] >= 6 and shape[2] == 23 + shape[1]


def _nested_pairs(nodes: list[_Node]) -> tuple[list[_Node], str]:
    """The OUTER node of each value appearing exactly twice, one inside the other."""
    by_value: dict[str, list[_Node]] = {}
    for node in nodes:
        by_value.setdefault(node.attrs["componentkey"], []).append(node)
    outers: list[_Node] = []
    for value, group in by_value.items():
        if len(group) != 2:
            return [], f"a key of this grammar appears {len(group)} time(s), where a nested pair is required"
        first, second = group
        up = second.parent
        while up is not None and up is not first:
            up = up.parent
        if up is not first:
            return [], "a key of this grammar appears twice, but not one copy inside the other"
        outers.append(first)
    return outers, ""


def card_keys(skeleton: str, expected: int, first_id: int) -> tuple[dict[str, str], str]:
    """``({keyed value: synthetic card key}, why)``. Refuses on any disagreement."""
    root = _tree(skeleton)
    keyed = [n for n in _walk(root) if _is_card_grammar(_shape(n.attrs.get("componentkey")))]
    outers, why = _nested_pairs(keyed)
    if why:
        return {}, why
    if len(outers) != expected:
        return {}, (f"{len(outers)} outer card(s) by the key's grammar, and the session's own "
                    f"reading counted {expected}: the two channels disagree")
    mapping = {}
    for index, node in enumerate(outers, start=1):
        mapping[node.attrs["componentkey"]] = f"{CARD_KEY_PREFIX}{first_id + index - 1}"
    return mapping, ""


def alert_key(skeleton: str) -> tuple[dict[str, str], str]:
    """``({keyed value: ALERT_KEY_SYNTHETIC}, why)``, from the one switch's keyed ancestors."""
    root = _tree(skeleton)
    switches = [n for n in _walk(root) if n.tag == "input" and n.attrs.get("role") == "switch"]
    if len(switches) != 1:
        return {}, f"{len(switches)} input switch(es) on the page, where exactly one is required"
    ancestors: list[_Node] = []
    up = switches[0].parent
    while up is not None and len(ancestors) < 2:
        shape = _shape(up.attrs.get("componentkey"))
        if shape is not None:
            ancestors.append(up)
        up = up.parent
    if len(ancestors) != 2:
        return {}, "the switch has fewer than two keyed ancestors"
    inner, outer = ancestors
    if inner.attrs["componentkey"] != outer.attrs["componentkey"]:
        return {}, "the switch's two nearest keyed ancestors carry different keys"
    shape = _shape(outer.attrs["componentkey"])
    assert shape is not None
    if shape[1] != 9 or shape[0] < 24 or shape[2] < shape[0] + 12:
        return {}, "the switch's keyed ancestor is not of the alert key's grammar"
    total = sum(1 for n in _walk(root) if n.attrs.get("componentkey") == outer.attrs["componentkey"])
    if total != 2:
        return {}, f"the alert key appears {total} time(s), where its nested pair is required"
    return {outer.attrs["componentkey"]: ALERT_KEY_SYNTHETIC}, ""


def write_keys(skeleton: str, mapping: dict[str, str]) -> tuple[str, int]:
    """Each mapped keyed ``componentkey`` value written as its key; the count."""
    count = 0

    def swap(match: "re.Match[str]") -> str:
        nonlocal count
        value = mapping.get(match.group(1))
        if value is None:
            return match.group(0)
        count += 1
        return 'componentkey="' + html.escape(value, quote=True) + '"'

    return _COMPONENTKEY.sub(swap, skeleton), count


def build(skeleton: str, key: bytes, words: tuple[str, ...], *, first_id: Optional[int], alert: bool,
          expected_cards: Optional[int]) -> tuple[str, dict[str, int]]:
    """The skeleton with its words, and its two grammar keys when declared, then reduced."""
    keyed_counts: dict[str, int] = {}
    if first_id is not None or alert:
        mapping: dict[str, str] = {}
        if first_id is not None:
            if expected_cards is None:
                raise SystemExit("card keys are declared and the session's reading gives no card count")
            got, why = card_keys(skeleton, expected_cards, first_id)
            if why:
                raise SystemExit(f"card keys refused: {why}")
            mapping.update(got)
            keyed_counts["card keys"] = len(got)
        if alert:
            got, why = alert_key(skeleton)
            if why:
                raise SystemExit(f"alert key refused: {why}")
            mapping.update(got)
            keyed_counts["alert keys"] = len(got)
        skeleton, written = write_keys(skeleton, mapping)
        keyed_counts["key attributes written"] = written
    copy, counts = w11.build(skeleton, key, words)
    counts.update(keyed_counts)
    return copy, counts


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--session-dir", required=True, type=Path)
    parser.add_argument("--only", default="")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    key = bytes.fromhex((args.session_dir / "shape.key").read_text(encoding="utf-8").strip())
    drift = 0
    for stem, (capture, words, first_id, alert) in sorted(SPEC.items()):
        if args.only and stem != args.only:
            continue
        skeleton = (args.session_dir / (capture + ".skeleton.html")).read_text(encoding="utf-8")
        base = s2.tracked_copy(skeleton)
        committed = FIXTURES / (capture + ".html")
        if committed.read_text(encoding="ascii") != base:
            raise SystemExit(f"{capture}: this skeleton's tracked copy is not the committed one")
        expected = None
        if first_id is not None:
            reading = json.loads((args.session_dir / (capture + ".json")).read_text(encoding="utf-8"))
            expected = int(reading["evidence"]["ai_cards"])
        copy, counts = build(skeleton, key, words, first_id=first_id, alert=alert, expected_cards=expected)
        text = header(stem, capture, words, first_id) + copy[len("<!doctype html>\n"):]
        assert all(ord(ch) < 128 for ch in text)
        out = FIXTURES / (stem + ".html")
        if args.check:
            same = out.exists() and out.read_text(encoding="ascii") == text
            drift += 0 if same else 1
            print("%-36s %s" % (stem, "matches" if same else "DIFFERS"))
            continue
        out.write_text(text, encoding="ascii", newline="\n")
        changed = sum(1 for a, b in zip(base.split("\n")[1:], copy.split("\n")[1:]) if a != b)
        word_places = sum(v for k, v in counts.items() if k in words)
        print("%s: base copy identical to the committed capture: True" % stem)
        print("  words declared %d, places written %d, lines differing %d"
              % (len(words), word_places, changed))
        for name in ("card keys", "alert keys", "key attributes written"):
            if name in counts:
                print("  %s %d" % (name, counts[name]))
        print("  sha256 %s" % hashlib.sha256(text.encode("ascii")).hexdigest()[:16])
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
