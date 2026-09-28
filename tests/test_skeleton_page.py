"""What ``tests/skeleton_page.py`` answers, and that it answers as Playwright would.

The double exists so the reader-leak guard can drive readers over committed
page skeletons and stand in for their clicks. Every semantic it claims is a
test here, over small inline pages (synthetic, no person) and over two
tracked fixtures -- ``tests/fixtures/synthetic/own_post_menu.html`` and
``tests/fixtures/profile_views_analytics.html`` -- read for COUNTS ONLY: no
test here prints what a fixture draws.

THE SELECTOR LIST IS HARVESTED, NOT ONLY WRITTEN. :data:`READER_SELECTORS` is
every selector the readers this double serves build, and
:func:`test_the_served_readers_build_exactly_the_listed_selectors` reads
those readers' source and fails the day one of them builds a selector the list
does not hold -- which is the day the double's grammar may no longer cover it.

EVERY TEST HERE WAS SHOWN FAILING (2026-09-28): 67 deliberate mutations --
63 of the double, 4 of this file's own tables -- were run against this file,
and each of its 252 test cases went red under at least one of them. A first
table of 23 had reddened only 49 of them; the other 44 mutations exist
because of that count. The table is in lane G's record of slice M.
"""

from __future__ import annotations

import ast
import asyncio
import builtins
import importlib
import importlib.util
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Optional

import pytest

from tests import plantedpage
from tests import skeleton_page as sp
from tests.plantedpage import PLANT, NavigationAttempted, PageAnswer, PlantedPage
from tests.skeleton_page import (
    DOCUMENT_TAG,
    GRAMMAR_REFUSAL,
    REFUSAL_REASONS,
    Element,
    SelectorOutsideGrammar,
    SkeletonLocator,
    SkeletonPage,
    Text,
    parse,
    parse_selector,
    select,
    text_of,
)

TESTS_DIR = Path(plantedpage.__file__).resolve().parent
FIXTURES = TESTS_DIR / "fixtures"
REPO = TESTS_DIR.parent

URL = "https://www.linkedin.com/analytics/profile-views/"

HEADINGS = "h1, h2, h3, h4, h5, h6, [role=heading]"
OPTIONS = '[role="checkbox"][aria-label], [role="radio"][aria-label]'


def run(awaitable: Any) -> Any:
    return asyncio.run(awaitable)


def _page(html: str, **kwargs: Any) -> tuple[SkeletonPage, PlantedPage]:
    planted = PlantedPage()
    return SkeletonPage(planted, parse(html), url=URL, **kwargs), planted


def _chain(page: SkeletonPage, chain: tuple[str, ...]) -> SkeletonLocator:
    locator = page.locator(chain[0])
    for selector in chain[1:]:
        locator = locator.locator(selector)
    return locator


def _ids(locator: SkeletonLocator) -> list[Optional[str]]:
    async def go() -> list[Optional[str]]:
        return [handle.element().attrs.get("id") for handle in await locator.element_handles()]

    return run(go())


def _elements(node: Element) -> list[Element]:
    return [n for n in sp.walk(node) if isinstance(n, Element) and n.tag != DOCUMENT_TAG]


# ===========================================================================
# THE SELECTOR LIST: every selector the served readers build, and who
# ===========================================================================

#: Every selector the readers this double serves build, with the reader. The
#: brief's readers, plus two things they reach that build locators:
#: ``press.disclose`` (the filter-pill opener's press) and the two nav-badge
#: readers the counter closure calls.
READER_SELECTORS: dict[str, str] = {
    "main": (
        "view_switch._pill_positions and apply_and_restore; reveal.reveal "
        "(CANDIDATE_SCOPE); press.disclose (PRESS_SCOPES 'main'); "
        "profile_views_more.read_profile_views_more_insights; "
        "server._open_profile_views_filter_menus"
    ),
    "[aria-expanded]": (
        "under main: view_switch._pill_positions and apply_and_restore; "
        "server._open_profile_views_filter_menus; press.disclose (a "
        "SANCTIONED_SHAPES key, the shape that opener passes)"
    ),
    "[aria-haspopup]": "under a scope: press.disclose (the other SANCTIONED_SHAPES key; no served caller passes it)",
    OPTIONS: "view_switch.OPTION_SELECTOR: _option_positions, _wait_for_option (.first.wait_for), apply_and_restore",
    "button": "page-wide: view_switch._apply_positions and apply_and_restore; under main: reveal.reveal",
    "main *": "reveal.reveal (CANDIDATE_SCOPE + ' *'), before and after its click",
    '[aria-expanded="true"]': "press._read_witness (WITNESS_SELECTORS), from press.disclose and reveal.reveal",
    '[role="dialog"]': "press._read_witness (WITNESS_SELECTORS)",
    '[role="menu"]': "press._read_witness (WITNESS_SELECTORS)",
    '[role="menuitem"]': "press._read_witness (WITNESS_SELECTORS)",
    '[role="listbox"]': "press._read_witness (WITNESS_SELECTORS)",
    HEADINGS: "under main: profile_views_more.read_profile_views_more_insights",
    "xpath=..": "on a heading, up to four times: profile_views_more._section_lines",
    "label": "on a pill: server._open_profile_views_filter_menus (_pill_indices)",
    'a[href*="/mynetwork"]': "dom.read_invitation_badge, from server._profile_views_press_counters",
    'a[href*="/mynetwork"][aria-label*="new notification"]': (
        "dom.invitation_badge_selector() in dom.read_invitation_badge, from "
        "server._profile_views_press_counters"
    ),
    'a[href*="/notifications"]': "notify_cost.read_notifications_badge, from server._profile_views_press_counters",
    'a[href*="/notifications"][aria-label*="new notification" i]': (
        "notify_cost.notifications_badge_selector() in "
        "notify_cost.read_notifications_badge, from server._profile_views_press_counters"
    ),
}

#: The readers whose ``.locator(...)`` calls are harvested, by module.
SERVED_READERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("view_switch", ("_pill_positions", "_option_positions", "_apply_positions",
                     "_wait_for_option", "apply_and_restore")),
    ("reveal", ("reveal",)),
    ("press", ("_read_witness", "disclose", "_take_reading")),
    ("profile_views_more", ("read_profile_views_more_insights", "_section_lines")),
    ("server", ("_open_profile_views_filter_menus", "_profile_views_press_counters",
                "_profile_views_switch", "_profile_views_more_analytics")),
    ("dom", ("read_invitation_badge", "read_profile_views_insights", "read_count_lines",
             "harvest_linked_cards")),
    ("notify_cost", ("read_notifications_badge",)),
)


def _run_time_selectors() -> dict[tuple[str, str, str], tuple[str, ...]]:
    """The selectors a served reader takes from a VARIABLE, and where its
    values come from -- each a closed table of the package."""
    from linkedin_server import press

    return {
        ("press", "disclose", "scope_selector"): tuple(
            entry["selector"] for _key, entry in press.PRESS_SCOPES
        ),
        ("press", "disclose", "shape"): tuple(press.SANCTIONED_SHAPES),
        ("press", "_read_witness", "selector"): tuple(
            selector for _name, selector in press.WITNESS_SELECTORS
        ),
    }


def _constant_selector(node: ast.AST, module_name: str) -> Optional[str]:
    """A selector argument the source fixes: a literal, an UPPER_CASE module
    constant, a sum of those, or a no-argument call of a module function."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name) and node.id.isupper():
        value = getattr(importlib.import_module(f"linkedin_server.{module_name}"), node.id, None)
        return value if isinstance(value, str) else None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _constant_selector(node.left, module_name)
        right = _constant_selector(node.right, module_name)
        return left + right if left is not None and right is not None else None
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and not node.args
        and not node.keywords
    ):
        function = getattr(importlib.import_module(f"linkedin_server.{module_name}"), node.func.id, None)
        value = function() if callable(function) else None
        return value if isinstance(value, str) else None
    return None


def _harvest_served_selectors() -> tuple[set[str], list[str]]:
    import linkedin_server

    package = Path(linkedin_server.__file__).resolve().parent
    run_time = _run_time_selectors()
    found: set[str] = set()
    problems: list[str] = []
    for module_name, functions in SERVED_READERS:
        tree = ast.parse((package / f"{module_name}.py").read_text(encoding="utf-8"))
        top = {
            node.name: node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        for function in functions:
            if function not in top:
                problems.append(f"{module_name}.{function}: no such function")
                continue
            for node in ast.walk(top[function]):
                if not (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "locator"
                ):
                    continue
                if node.keywords or len(node.args) != 1:
                    problems.append(f"{module_name}.{function}: a locator call with filters or no selector")
                    continue
                argument = node.args[0]
                value = _constant_selector(argument, module_name)
                if value is not None:
                    found.add(value)
                elif isinstance(argument, ast.Name) and (module_name, function, argument.id) in run_time:
                    found.update(run_time[(module_name, function, argument.id)])
                else:
                    problems.append(f"{module_name}.{function}: a selector this list cannot resolve")
    return found, problems


def test_the_served_readers_build_exactly_the_listed_selectors() -> None:
    found, problems = _harvest_served_selectors()
    assert problems == []
    assert sorted(found - set(READER_SELECTORS)) == [], "a served reader builds a selector the list lacks"
    assert sorted(set(READER_SELECTORS) - found) == [], "the list holds a selector no served reader builds"


@pytest.mark.parametrize("selector", sorted(READER_SELECTORS))
def test_every_listed_selector_is_inside_the_grammar(selector: str) -> None:
    parse_selector(selector)


#: Each listed selector, applied as its reader applies it (the chain), over
#: an inline page built to tell right from wrong, with the ids it must find.
SELECTOR_CASES: tuple[tuple[tuple[str, ...], str, list[str]], ...] = (
    (("main",),
     '<div id="d"><main id="m1"></main></div><main id="m2"><main id="m3"></main></main>',
     ["m1", "m2", "m3"]),
    (("main", "[aria-expanded]"),
     '<nav><button id="nav" aria-expanded="false"></button></nav>'
     '<main><button id="p1" aria-expanded="false"></button>'
     '<div id="p2" role="button" aria-expanded="true"><label>x</label></div>'
     '<button id="plain"></button></main>',
     ["p1", "p2"]),
    (("main", "[aria-haspopup]"),
     '<button id="out" aria-haspopup="menu"></button>'
     '<main><button id="a" aria-haspopup="menu"></button><button id="b"></button></main>',
     ["a"]),
    ((OPTIONS,),
     '<div id="c1" role="checkbox" aria-label="verified"></div>'
     '<div id="r1" role="radio" aria-label="past 7 days"></div>'
     '<div id="c2" role="checkbox"></div>'
     '<div id="s1" role="switch" aria-label="verified"></div>'
     '<div id="c3" role="checkbox" aria-label=""></div>',
     ["c1", "r1", "c3"]),
    (("button",),
     '<nav><button id="b1"></button></nav><main><button id="b2"></button></main><div id="x"></div>',
     ["b1", "b2"]),
    (("main", "button"),
     '<nav><button id="b1"></button></nav><main><div><button id="b2"></button></div></main>',
     ["b2"]),
    (("main *",),
     '<div id="out1"></div><main id="m"><div id="a"><span id="b">t</span></div><p id="c"></p></main>'
     '<div id="out2"></div>',
     ["a", "b", "c"]),
    (('[aria-expanded="true"]',),
     '<button id="t" aria-expanded="true"></button><button id="f" aria-expanded="false"></button>'
     '<button id="u" aria-expanded="TRUE"></button><button id="n" aria-expanded></button>',
     ["t"]),
    (('[role="dialog"]',),
     '<div id="d" role="dialog"></div><dialog id="native"></dialog><div id="a" role="alertdialog"></div>',
     ["d"]),
    (('[role="menu"]',),
     '<ul id="m" role="menu"><li id="i" role="menuitem"></li></ul><div id="b" role="menubar"></div>',
     ["m"]),
    (('[role="menuitem"]',),
     '<ul role="menu"><li id="i1" role="menuitem"></li><li id="c" role="menuitemcheckbox"></li>'
     '<li id="i2" role="menuitem"></li></ul>',
     ["i1", "i2"]),
    (('[role="listbox"]',),
     '<div id="l" role="listbox"><div role="option"></div></div><div id="c" role="combobox"></div>',
     ["l"]),
    (("main", HEADINGS),
     '<h1 id="out"></h1><main><h2 id="a"></h2><div id="b" role="heading"></div>'
     '<h1 id="c"></h1><h6 id="d"></h6><p id="e"></p><h7 id="f"></h7></main>',
     ["a", "b", "c", "d"]),
    (("main", HEADINGS, "xpath=.."),
     '<main id="m"><h2 id="top"></h2><section id="s"><div id="w"><h2 id="h"></h2></div></section></main>',
     ["m", "w"]),
    (("main", "[aria-expanded]", "label"),
     '<label id="out"></label><main><div id="p1" role="button" aria-expanded="false">'
     '<span><label id="l1"></label></span></div><div id="p2" aria-expanded="false"></div>'
     '<label id="loose"></label></main>',
     ["l1"]),
    (('a[href*="/mynetwork"]',),
     '<a id="mn" href="https://www.linkedin.com/mynetwork" aria-label="My Network, 1 new notification">.</a>'
     '<a id="sub" href="https://www.linkedin.com/mynetwork/network-manager/newsletters/">.</a>'
     '<a id="nt" href="https://www.linkedin.com/notifications/">.</a>',
     ["mn", "sub"]),
    (('a[href*="/mynetwork"][aria-label*="new notification"]',),
     '<a id="mn" href="https://www.linkedin.com/mynetwork" aria-label="My Network, 1 new notification">.</a>'
     '<a id="sub" href="https://www.linkedin.com/mynetwork/network-manager/newsletters/">.</a>'
     '<a id="cap" href="/mynetwork" aria-label="My Network, 2 New Notifications">.</a>'
     '<button id="btn" href="/mynetwork" aria-label="1 new notification">.</button>',
     ["mn"]),
    (('a[href*="/notifications"]',),
     '<a id="nt" href="https://www.linkedin.com/notifications/" aria-label="Notifications">.</a>'
     '<a id="rel" href="/notifications/">.</a><a id="mn" href="/mynetwork">.</a>',
     ["nt", "rel"]),
    (('a[href*="/notifications"][aria-label*="new notification" i]',),
     '<a id="cap" href="https://www.linkedin.com/notifications/" aria-label="Notifications, 3 New Notifications">.</a>'
     '<a id="low" href="/notifications/" aria-label="Notifications, 1 new notification">.</a>'
     '<a id="none" href="/notifications/" aria-label="Notifications">.</a>'
     '<a id="mn" href="/mynetwork" aria-label="1 new notification">.</a>',
     ["cap", "low"]),
)


def test_every_listed_selector_has_a_case() -> None:
    assert sorted({chain[-1] for chain, _html, _ids in SELECTOR_CASES}) == sorted(READER_SELECTORS)


@pytest.mark.parametrize(
    "chain, html, expected", SELECTOR_CASES, ids=[" > ".join(case[0]) for case in SELECTOR_CASES]
)
def test_each_listed_selector_finds_what_it_means(chain: tuple[str, ...], html: str, expected: list[str]) -> None:
    page, _planted = _page(html)
    assert _ids(_chain(page, chain)) == expected


# ===========================================================================
# PARSE
# ===========================================================================


def test_void_elements_hold_no_children() -> None:
    root = parse("<p>a<br>b<img src=x>c<input>d<hr>e</p>")
    (paragraph,) = root.children
    assert [child.tag if isinstance(child, Element) else "#text" for child in paragraph.children] == [
        "#text", "br", "#text", "img", "#text", "input", "#text", "hr", "#text",
    ]


def test_an_end_tag_closes_what_it_encloses_and_a_stray_one_is_ignored() -> None:
    root = parse("<div id=a><span id=b>t<p id=c>u</div><em id=d>v</em></b></i>")
    a, d = [child for child in root.children if isinstance(child, Element)]
    assert (a.attrs["id"], d.attrs["id"]) == ("a", "d")
    (b,) = [child for child in a.children if isinstance(child, Element)]
    (c,) = [child for child in b.children if isinstance(child, Element)]
    assert (b.attrs["id"], c.attrs["id"], c.parent is b, d.parent is root) == ("b", "c", True, True)
    (x,) = parse("<div id=x><span id=y>t</i>u</span>v</div>").children
    (y,) = [child for child in x.children if isinstance(child, Element)]
    assert (text_of(y), text_of(x)) == ("tu", "tuv")


def test_a_self_closed_tag_holds_nothing() -> None:
    root = parse('<div id="a"/><span id="b"></span>')
    assert [child.attrs["id"] for child in root.children] == ["a", "b"]
    assert root.children[0].children == []


def test_the_tree_is_the_people_search_builders_tree() -> None:
    """Built as ``scripts/_build_people_search_skeleton.py``'s ``Tree`` builds
    it -- on markup that exercises every tolerance -- compared by tag and
    nesting (that Tree also drops blank text, which is compared apart)."""
    spec = importlib.util.spec_from_file_location(
        "_skeleton_builder_under_test", REPO / "scripts" / "_build_people_search_skeleton.py"
    )
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    markup = (
        "<html><body><main><div><span>a<p>b</div><ul><li>one<li>two</ul>"
        "<a href=x>link<a href=y>inner</a></a><br><img><div/>tail</b>"
        "<section><h2>t</h2>loose</main><p>after</p></body></html>"
    )

    def shape_of_ours(node: Any, depth: int = 0, out: Optional[list[str]] = None) -> list[str]:
        out = [] if out is None else out
        if isinstance(node, Text):
            if node.data.strip():
                out.append(f"{depth}:#text")
            return out
        out.append(f"{depth}:{node.tag}")
        for child in node.children:
            shape_of_ours(child, depth + 1, out)
        return out

    def shape_of_theirs(node: Any, depth: int = 0, out: Optional[list[str]] = None) -> list[str]:
        out = [] if out is None else out
        out.append(f"{depth}:{'#document' if node.tag == '#root' else node.tag}")
        for child in node.children:
            shape_of_theirs(child, depth + 1, out)
        return out

    tree = builder.Tree()
    tree.feed(markup)
    tree.close()
    assert shape_of_ours(parse(markup)) == shape_of_theirs(tree.root)


def test_comments_scripts_and_styles_are_dropped() -> None:
    root = parse(
        "<main><!-- a comment --><script>var x = '<b>no</b>';</script>"
        "<style>b { color: red }</style><b>kept</b><script src=y /></main>"
    )
    assert [element.tag for element in _elements(root)] == ["main", "b"]
    assert text_of(root) == "kept"


def test_attribute_names_are_lower_cased_the_first_duplicate_wins_and_a_bare_one_is_empty() -> None:
    (element,) = parse('<INPUT Type="checkbox" TYPE="radio" Checked data-X=1>').children
    assert element.tag == "input"
    assert element.attrs == {"type": "checkbox", "checked": "", "data-x": "1"}


def test_entities_are_decoded_in_text_and_attributes() -> None:
    (element,) = parse('<a href="/x?a=1&amp;b=2" aria-label="A &amp; B">1 &lt; 2 &#8226; x</a>').children
    assert element.attrs["href"] == "/x?a=1&b=2"
    assert element.attrs["aria-label"] == "A & B"
    assert text_of(element) == "1 < 2 " + chr(0x2022) + " x"


def test_blank_text_is_kept_and_a_run_of_text_is_one_node() -> None:
    (div,) = parse("<div><span>a</span> <span>b</span>x&amp;y</div>").children
    kinds = [type(child).__name__ for child in div.children]
    assert kinds == ["Element", "Text", "Element", "Text"]
    assert div.children[1].data == " " and div.children[3].data == "x&y"


def test_a_comment_or_a_dropped_element_parts_two_text_nodes_as_in_a_browser() -> None:
    """``html.parser`` hands one run of text over in pieces (``a < b`` comes
    as three calls), and those pieces are ONE text node in a browser; but a
    comment -- or a script, dropped here -- stands BETWEEN two text nodes, and
    ``answer_text`` is called once per text node, so the two stay two. (The
    analytics capture carries 37 comments.)"""
    (div,) = parse("<div>a < b<!-- c -->d<script>x</script>e<!---->f</div>").children
    assert [child.data for child in div.children] == ["a < b", "d", "e", "f"]
    seen: list[str] = []
    page, _planted = _page("<p>Xxxxx<!---->Xxxx</p>", answer_text=lambda text: seen.append(text) or text)
    assert run(page.locator("p").inner_text()) == "XxxxxXxxx"
    assert seen == ["Xxxxx", "Xxxx"]


def test_the_document_root_is_never_an_answer() -> None:
    page, _planted = _page("<main></main>")
    root = page.document
    assert (root.tag, root.parent) == (DOCUMENT_TAG, None)
    assert run(page.locator("*").count()) == 1
    assert run(page.locator("xpath=..").count()) == 0
    assert run(page.locator("main").locator("xpath=..").count()) == 0


def test_reprs_carry_no_text_and_no_value() -> None:
    (element,) = parse('<a aria-label="Secret Person">Secret Person</a>').children
    assert "Secret" not in repr(element) and "Secret" not in repr(element.children[0])


# ===========================================================================
# GRAMMAR
# ===========================================================================

#: Selectors outside the grammar, each with the reason it must be refused for.
OUTSIDE: tuple[tuple[str, str], ...] = (
    ("main > button", "a combinator other than the descendant one"),
    ("main>button", "a combinator other than the descendant one"),
    ("h2 + p", "a combinator other than the descendant one"),
    ("h2 ~ p", "a combinator other than the descendant one"),
    ("main >> button", "a combinator other than the descendant one"),
    ("button:visible", "a pseudo-class or pseudo-element"),
    (":is(main, nav)", "a pseudo-class or pseudo-element"),
    ("button::before", "a pseudo-class or pseudo-element"),
    (".visually-hidden", "a class or id selector"),
    ("#post-root", "a class or id selector"),
    ("div.card", "a class or id selector"),
    ("svg|a", "a namespace"),
    ("[xlink|href]", "a namespace"),
    ('[href$=".pdf"]', "an attribute operator outside =, *= and ^="),
    ('[class~="x"]', "an attribute operator outside =, *= and ^="),
    ('[lang|="en"]', "an attribute operator outside =, *= and ^="),
    ('[aria-label="x" s]', "an attribute flag other than i"),
    ('[aria-label="a\\"b"]', "an escape inside a string or identifier"),
    ('[aria-label="open]', "an unterminated string"),
    ('[role="button"', "an unterminated attribute selector"),
    ("[role=", "an unterminated attribute selector"),
    ("[role=1x]", "an attribute value that is neither quoted nor an identifier"),
    ("[1x]", "an attribute name that is not an identifier"),
    ("[]", "an attribute name that is not an identifier"),
    ("[role=a b]", "an unexpected character"),
    ("[role]div", "a type selector after an attribute or another type"),
    ("main*", "a type selector after an attribute or another type"),
    ("*div", "a type selector after an attribute or another type"),
    (",main", "an empty compound"),
    ("main,", "an empty compound"),
    ("main,,nav", "an empty compound"),
    ("", "an empty selector"),
    ("   ", "an empty selector"),
    ("css=", "an empty selector"),
    ("text=Show more", "a selector engine other than css= and xpath="),
    ('role=button[name="Save"]', "a selector engine other than css= and xpath="),
    ("internal:has-text=x", "a selector engine other than css= and xpath="),
    ("nth=0", "a selector engine other than css= and xpath="),
    ("xpath=//main", "an xpath other than .."),
    ("xpath=../..", "an xpath other than .."),
    ("//main", "an implicit xpath or text selector"),
    ("..", "an implicit xpath or text selector"),
    ('"Show more"', "an implicit xpath or text selector"),
    ("main @", "an unexpected character"),
)


@pytest.mark.parametrize("selector, reason", OUTSIDE, ids=[case[0] or "<empty>" for case in OUTSIDE])
def test_a_selector_outside_the_grammar_is_refused_for_its_reason(selector: str, reason: str) -> None:
    with pytest.raises(ValueError) as caught:
        parse_selector(selector)
    assert isinstance(caught.value, SelectorOutsideGrammar)
    assert str(caught.value) == GRAMMAR_REFUSAL == "selector outside the skeleton grammar"
    assert caught.value.reason == reason
    assert reason in REFUSAL_REASONS


def test_a_non_string_selector_is_refused() -> None:
    with pytest.raises(SelectorOutsideGrammar) as caught:
        parse_selector(None)
    assert caught.value.reason == "the selector is not a string"


#: A marker no refusal's own words contain, placed where each construct
#: would carry a reader's (or a page's) text.
MARKER = "Zqxwv"

MARKED_OUTSIDE: tuple[str, ...] = (
    f"main > {MARKER}", f"{MARKER}:hover", f".{MARKER}", f"#{MARKER}",
    f'[href$="{MARKER}"]', f'[aria-label="{MARKER}" s]', f'[aria-label="{MARKER}',
    f'[aria-label="{MARKER}"', f"text={MARKER}", f"xpath=//{MARKER}", f'"{MARKER}"',
    f"[role={MARKER} b]", f"{MARKER} @", f"[role={MARKER}]div", f"{MARKER}|a",
)


def test_a_refusal_quotes_no_part_of_the_selector() -> None:
    page, _planted = _page("<main></main>")
    for selector in MARKED_OUTSIDE:
        with pytest.raises(SelectorOutsideGrammar) as caught:
            page.locator(selector)
        said = " ".join((str(caught.value), caught.value.reason, repr(caught.value)))
        assert MARKER not in said
    assert len(page.unmodelled) == len(MARKED_OUTSIDE)
    assert MARKER not in " ".join(page.unmodelled)


def test_the_css_prefix_names_the_same_selector() -> None:
    page, _planted = _page('<main><div id="a" role="menu"></div><p id="b"></p></main>')
    assert _ids(page.locator("css=main *")) == _ids(page.locator("main *")) == ["a", "b"]
    assert _ids(page.locator('css=[role="menu"], p')) == ["a", "b"]


def test_the_attribute_operators() -> None:
    page, _planted = _page(
        '<a id="e" data-v="">.</a><a id="p" data-v="prefix-middle-suffix">.</a>'
        '<a id="q" data-v="middle">.</a><a id="n">.</a>'
    )
    assert _ids(page.locator("[data-v]")) == ["e", "p", "q"]
    assert _ids(page.locator('[data-v=""]')) == ["e"]
    assert _ids(page.locator('[data-v="middle"]')) == ["q"]
    assert _ids(page.locator("[data-v=middle]")) == ["q"]
    assert _ids(page.locator("[data-v='middle']")) == ["q"]
    assert _ids(page.locator('[ data-v = "middle" ]')) == ["q"]
    assert _ids(page.locator('[data-v*="middle"]')) == ["p", "q"]
    assert _ids(page.locator('[data-v^="prefix"]')) == ["p"]
    assert _ids(page.locator('[data-v^="middle"]')) == ["q"]


def test_an_empty_substring_or_prefix_matches_nothing() -> None:
    page, _planted = _page('<a id="e" data-v="">.</a><a id="p" data-v="x">.</a>')
    assert _ids(page.locator('[data-v*=""]')) == []
    assert _ids(page.locator('[data-v^=""]')) == []


@pytest.mark.parametrize("operator", ["=", "*=", "^="])
def test_the_i_flag_matches_across_case_and_nothing_else_does(operator: str) -> None:
    value = {"=": "new notification", "*=": "new notif", "^=": "new"}[operator]
    page, _planted = _page(
        '<a id="low" aria-label="new notification">.</a><a id="cap" aria-label="New Notification">.</a>'
        '<a id="up" aria-label="NEW NOTIFICATION">.</a><a id="other" aria-label="old notification">.</a>'
    )
    sensitive = _ids(page.locator(f'a[aria-label{operator}"{value}"]'))
    folded = _ids(page.locator(f'a[aria-label{operator}"{value}" i]'))
    folded_upper_flag = _ids(page.locator(f'a[aria-label{operator}"{value.upper()}"I]'))
    assert sensitive == ["low"]
    assert folded == folded_upper_flag == ["low", "cap", "up"]


def test_tag_and_attribute_names_ignore_case_and_values_do_not() -> None:
    page, _planted = _page('<button id="b" aria-label="Save">.</button><button id="c" aria-label="save">.</button>')
    assert _ids(page.locator('BUTTON[ARIA-LABEL="Save"]')) == ["b"]


# ===========================================================================
# MATCHING: order, scope, chains, nth, the parent
# ===========================================================================


def test_matching_is_in_document_order_and_deduplicated() -> None:
    page, _planted = _page(
        '<h2 id="a"></h2><h1 id="b" role="heading"></h1><div id="c" role="heading"></div><h1 id="d"></h1>'
    )
    assert _ids(page.locator("h1, h2, [role=heading]")) == ["a", "b", "c", "d"]
    assert _ids(page.locator("[role=heading], h1")) == ["b", "c", "d"]


def test_a_chained_locator_is_the_descendants_of_each_match_once_in_document_order() -> None:
    page, _planted = _page(
        '<div id="o"><span id="s1"></span><div id="i"><span id="s2"></span></div><span id="s3"></span></div>'
        '<div id="p"><span id="s4"></span></div><span id="s5"></span>'
    )
    assert _ids(page.locator("div")) == ["o", "i", "p"]
    assert _ids(page.locator("div").locator("span")) == ["s1", "s2", "s3", "s4"]


def test_the_descendant_combinator_reaches_any_depth() -> None:
    page, _planted = _page(
        '<main><div><div><div><span id="deep"></span></div></div></div><span id="child"></span></main>'
        '<span id="out"></span>'
    )
    assert _ids(page.locator("main span")) == ["deep", "child"]
    assert _ids(page.locator("main div span")) == ["deep"]


def test_the_scope_never_matches_itself_and_nothing_above_it_counts() -> None:
    page, _planted = _page(
        '<section id="above"><div id="scope"><span id="direct"></span>'
        '<div id="inner"><span id="nested"></span></div></div></section>'
    )
    scope = page.locator('[id="scope"]')
    assert _ids(scope.locator("div")) == ["inner"]
    assert _ids(scope.locator("div span")) == ["nested"]
    assert _ids(scope.locator("section span")) == []
    assert _ids(page.locator("section span")) == ["direct", "nested"]


def test_nth_first_last_and_past_the_end() -> None:
    page, _planted = _page("".join(f'<b id="{name}"></b>' for name in "abcd"))
    bold = page.locator("b")
    assert [_ids(bold.nth(index)) for index in range(5)] == [["a"], ["b"], ["c"], ["d"], []]
    assert _ids(bold.first) == ["a"] and _ids(bold.last) == ["d"]
    assert _ids(bold.nth(-2)) == ["c"]
    assert _ids(bold.nth(-5)) == []
    assert run(bold.nth(9).count()) == 0
    assert _ids(page.locator("i").last) == []


def test_main_star_is_every_element_under_main() -> None:
    page, _planted = _page('<main id="m"><div id="a">text<br id="b"><span id="c"></span></div></main><i id="x"></i>')
    assert run(page.locator("main *").count()) == 3


def test_the_parent_climbs_one_level_at_a_time_and_stops_below_the_document() -> None:
    page, _planted = _page('<main id="m"><section id="s"><div id="w"><h2 id="h"></h2></div></section></main>')
    heading = page.locator("h2")
    assert _ids(heading.locator("xpath=..")) == ["w"]
    assert _ids(heading.locator("xpath=..").locator("xpath=..")) == ["s"]
    climbed = heading
    for _level in range(4):
        climbed = climbed.locator("xpath=..")
    assert _ids(climbed) == []


def test_the_parent_of_several_is_in_the_order_of_the_children_as_in_playwright() -> None:
    """Playwright unions a chained part's results root by root and does NOT
    re-sort (``InjectedScript.querySelectorAll``): the parents of [deep child,
    shallow child] come back [deep parent, shallow parent] -- not document
    order. Mirrored, and pinned so nobody "fixes" it into a divergence."""
    page, _planted = _page('<div id="outer"><div id="inner"><b id="deep"></b></div><b id="shallow"></b></div>')
    assert _ids(page.locator("b")) == ["deep", "shallow"]
    assert _ids(page.locator("b").locator("xpath=..")) == ["inner", "outer"]


def test_select_answers_as_a_locator_does_and_counts_no_read() -> None:
    page, planted = _page('<main><div id="a"><span id="b"></span></div></main>')
    assert [element.attrs["id"] for element in select(page.document, "main *")] == ["a", "b"]
    (div,) = select(page.document, "div")
    assert select(div, "div") == [] and [e.attrs["id"] for e in select(div, "span")] == ["b"]
    assert planted.reads == 0


# ===========================================================================
# READS: strictness, no match, and what each answers
# ===========================================================================

SINGLE_ELEMENT_READS: tuple[tuple[str, Callable[[SkeletonLocator], Any]], ...] = (
    ("get_attribute", lambda loc: loc.get_attribute("id")),
    ("inner_text", lambda loc: loc.inner_text()),
    ("text_content", lambda loc: loc.text_content()),
    ("is_enabled", lambda loc: loc.is_enabled()),
    ("is_checked", lambda loc: loc.is_checked()),
    ("click", lambda loc: loc.click()),
    ("wait_for", lambda loc: loc.wait_for(state="attached")),
)


@pytest.mark.parametrize("method, read", SINGLE_ELEMENT_READS, ids=[case[0] for case in SINGLE_ELEMENT_READS])
def test_a_single_element_read_on_no_match_raises_the_timeout_at_once(method: str, read: Callable) -> None:
    page, _planted = _page("<p>Secretword here</p>")
    with pytest.raises(sp.TimeoutError) as caught:
        run(read(page.locator("button")))
    assert "Secretword" not in str(caught.value)


def test_element_on_no_match_raises_the_timeout() -> None:
    page, _planted = _page("<p></p>")
    with pytest.raises(sp.TimeoutError):
        page.locator("button").element()


@pytest.mark.parametrize(
    "method, read",
    SINGLE_ELEMENT_READS + (("is_visible", lambda loc: loc.is_visible()),),
    ids=[case[0] for case in SINGLE_ELEMENT_READS] + ["is_visible"],
)
def test_a_single_element_read_on_several_raises_a_strict_error_naming_the_count(method: str, read: Callable) -> None:
    page, _planted = _page("<b>Secretword one</b><b>Secretword two</b><b>three</b>")
    with pytest.raises(sp.Error) as caught:
        run(read(page.locator("b")))
    assert not isinstance(caught.value, sp.TimeoutError)
    message = str(caught.value)
    assert "strict mode violation" in message and "3 elements" in message and method in message
    assert "Secretword" not in message


def test_element_on_several_raises_a_strict_error() -> None:
    page, _planted = _page("<b></b><b></b>")
    with pytest.raises(sp.Error, match="2 elements"):
        page.locator("b").element()


def test_is_visible_on_no_match_is_false_at_once() -> None:
    page, _planted = _page("<p></p>")
    assert run(page.locator("button").is_visible()) is False


def test_count_and_element_handles_are_never_strict() -> None:
    page, _planted = _page("<b></b><b></b><b></b>")
    assert run(page.locator("b").count()) == 3
    assert len(run(page.locator("b").element_handles())) == 3
    assert run(page.locator("i").element_handles()) == []


def test_the_timeout_is_playwrights_shape_and_not_the_builtin() -> None:
    """Playwright's TimeoutError derives from its own Error, an Exception --
    not the builtin; and on this interpreter the guard's drive-timeout clause
    catches ``asyncio.TimeoutError``, which IS the builtin."""
    assert issubclass(sp.TimeoutError, sp.Error) and issubclass(sp.Error, Exception)
    assert not issubclass(sp.TimeoutError, builtins.TimeoutError)
    page, _planted = _page("<p></p>")
    try:
        run(page.locator("button").inner_text())
    except asyncio.TimeoutError:  # the guard's clause for a drive that timed out
        pytest.fail("a read on no match would be misfiled as a drive timeout")
    except sp.TimeoutError:
        pass


def test_inner_text_breaks_lines_at_blocks_and_br_and_collapses_the_rest() -> None:
    page, _planted = _page(
        "<section id=s><h2>Highlights</h2>\n   <div>  first\n\n value </div>"
        "<p>a <b>bold</b>   <i>word</i></p><span>one</span><span>two</span> <span>three</span>"
        "<ul><li>x</li><li>y<br>z</li></ul>tail<hr>after<div></div><div>  </div>"
        "<em>nb" + chr(0xA0) + "sp</em></section>"
    )
    assert run(page.locator("section").inner_text()).split("\n") == [
        "Highlights", "first value", "a bold word", "onetwo three", "x", "y", "z", "tail",
        "after", "nb" + chr(0xA0) + "sp",
    ]


def test_inner_text_skips_what_is_not_rendered() -> None:
    page, _planted = _page(
        '<div id="d">shown<span hidden>gone</span><input type="HIDDEN" value="v">'
        '<div hidden><p>also gone</p></div>kept</div>'
    )
    assert run(page.locator('[id="d"]').inner_text()) == "shownkept"


def test_a_hidden_element_answers_its_text_content_as_the_standard_says() -> None:
    page, _planted = _page('<div id="d" hidden><p>one</p><p>two</p></div>')
    assert run(page.locator('[id="d"]').inner_text()) == "onetwo"


def test_text_content_concatenates_every_text_node_with_no_breaks() -> None:
    page, _planted = _page("<div><h2>Head</h2>\n<p>one<br>two</p><span hidden>hid</span></div>")
    assert run(page.locator("div").text_content()) == "Head\nonetwohid"


def test_answer_text_reaches_every_text_node_and_the_aria_label_and_nothing_else() -> None:
    seen: list[str] = []

    def answer(text: str) -> str:
        seen.append(text)
        return text.replace("Xxxx", PLANT).replace("xxxx", PLANT)

    # The href is a member slug in the shape the skeleton builder writes it
    # (lower case, which the identity sweep reads as a shape): a double that
    # answered the href too would turn it into the plant.
    page, _planted = _page(
        '<a id="a" href="/in/xxxx/" role="Xxxx" aria-label="View Xxxx profile" title="Xxxx">'
        "<span>Xxxx</span> <span>Xxxx</span></a>",
        answer_text=answer,
    )
    link = page.locator("a")
    assert run(link.inner_text()) == f"{PLANT} {PLANT}"
    assert run(link.text_content()) == f"{PLANT} {PLANT}"
    assert run(link.get_attribute("aria-label")) == f"View {PLANT} profile"
    assert run(link.get_attribute("ARIA-LABEL")) == f"View {PLANT} profile"
    assert run(link.get_attribute("href")) == "/in/xxxx/"
    assert run(link.get_attribute("role")) == "Xxxx"
    assert run(link.get_attribute("title")) == "Xxxx"
    assert text_of(link.element()) == "Xxxx Xxxx"
    assert seen.count(" ") == 2  # the blank text node went through answer_text too


def test_text_of_is_the_raw_descendant_text() -> None:
    page, _planted = _page("<div><h2>Head</h2><p>one<br>two</p></div>", answer_text=lambda text: PLANT)
    assert text_of(page.locator("div").element()) == "Headonetwo"
    assert text_of(page.document.children[0].children[0].children[0]) == "Head"


def test_get_attribute_absent_bare_and_present() -> None:
    page, _planted = _page('<input id="i" checked type="checkbox">')
    field = page.locator("input")
    assert run(field.get_attribute("aria-label")) is None
    assert run(field.get_attribute("checked")) == ""
    assert run(field.get_attribute("TYPE")) == "checkbox"


def test_is_visible_by_the_hidden_attribute_and_the_hidden_input() -> None:
    page, _planted = _page(
        '<div id="v"></div><div id="h" hidden></div><section hidden><p id="under"></p></section>'
        '<input id="hi" type="hidden"><input id="HI" type="HIDDEN"><input id="t" type="text">'
        '<div aria-hidden="true" id="aria"></div>'
    )
    verdicts = {
        name: run(page.locator(f'[id="{name}"]').is_visible())
        for name in ("v", "h", "under", "hi", "HI", "t", "aria")
    }
    assert verdicts == {"v": True, "h": False, "under": False, "hi": False, "HI": False, "t": True, "aria": True}


def test_is_enabled_by_disabled_a_disabled_fieldset_and_aria_disabled() -> None:
    page, _planted = _page(
        '<button id="on"></button><button id="off" disabled></button>'
        '<fieldset disabled><div><input id="in-set"></div></fieldset>'
        '<div disabled><button id="under-div"></button></div>'
        '<div id="aria" role="button" aria-disabled="true"></div>'
        '<div id="aria-no" role="button" aria-disabled="false"></div>'
    )
    verdicts = {
        name: run(page.locator(f'[id="{name}"]').is_enabled())
        for name in ("on", "off", "in-set", "under-div", "aria", "aria-no")
    }
    assert verdicts == {
        "on": True, "off": False, "in-set": False, "under-div": True, "aria": False, "aria-no": True,
    }


def test_is_checked_by_checked_or_aria_checked_true() -> None:
    page, _planted = _page(
        '<input id="c" type="checkbox" checked><input id="u" type="checkbox">'
        '<div id="t" role="checkbox" aria-checked="true"></div>'
        '<div id="f" role="checkbox" aria-checked="false"></div>'
    )
    verdicts = {name: run(page.locator(f'[id="{name}"]').is_checked()) for name in "cutf"}
    assert verdicts == {"c": True, "u": False, "t": True, "f": False}


def test_wait_for_answers_each_state_at_once_and_strictly() -> None:
    page, _planted = _page('<div id="v"></div><div id="h" hidden></div><b></b><b></b>')
    visible, hidden, absent, several = (
        page.locator('[id="v"]'), page.locator('[id="h"]'), page.locator("i"), page.locator("b"),
    )
    run(visible.wait_for())
    run(visible.wait_for(state="visible"))
    run(visible.wait_for(state=None))
    run(hidden.wait_for(state="attached"))
    run(hidden.wait_for(state="hidden"))
    run(absent.wait_for(state="detached"))
    run(absent.wait_for(state="hidden"))
    for locator, state in ((hidden, "visible"), (absent, "visible"), (absent, "attached"),
                           (visible, "hidden"), (visible, "detached")):
        with pytest.raises(sp.TimeoutError):
            run(locator.wait_for(state=state))
    with pytest.raises(sp.Error, match="2 elements"):
        run(several.wait_for(state="attached"))
    with pytest.raises(sp.Error, match="expected one of"):
        run(visible.wait_for(state="stable"))
    run(several.first.wait_for(state="visible", timeout=5000))


def test_element_handles_are_pinned_each_to_its_element_in_order() -> None:
    page, _planted = _page(
        '<ul><li id="a"><b id="ab">1</b></li><li id="b"><b id="bb">2</b></li></ul>'
    )
    handles = run(page.locator("li").element_handles())
    assert [handle.element().attrs["id"] for handle in handles] == ["a", "b"]
    assert [run(handle.inner_text()) for handle in handles] == ["1", "2"]
    assert [_ids(handle.locator("b")) for handle in handles] == [["ab"], ["bb"]]


# ===========================================================================
# LAZINESS AND THE CLICK STAND-IN
# ===========================================================================

BEFORE_THE_CLICK = (
    '<main><div id="pill" role="button" aria-expanded="false"><label>Pill</label></div></main>'
)
AFTER_THE_CLICK = (
    '<main><div id="pill" role="button" aria-expanded="true"><label>Pill</label></div>'
    '<div role="dialog"><div id="o1" role="checkbox" aria-label="verified" aria-checked="false"></div>'
    '<div id="o2" role="checkbox" aria-label="other" aria-checked="false"></div></div></main>'
)


def test_a_locator_is_lazy_and_reads_the_document_it_finds_at_each_action() -> None:
    page, _planted = _page('<main><b id="a1" data-k="first"></b></main>')
    bold = page.locator("main").locator("b")
    last = bold.last
    assert run(bold.count()) == 1 and run(last.get_attribute("data-k")) == "first"
    page.document = parse('<main><b id="b1" data-k="one"></b><b id="b2" data-k="two"></b></main>')
    assert run(bold.count()) == 2
    assert run(last.get_attribute("data-k")) == "two"
    assert run(bold.nth(0).get_attribute("id")) == "b1"


def test_the_click_stand_in_sees_what_was_pressed_and_moves_the_page() -> None:
    calls: list[tuple[str, str, bool]] = []

    def on_click(locator: SkeletonLocator, page: SkeletonPage) -> None:
        pressed = locator.element()
        calls.append((pressed.attrs["id"], text_of(pressed), page is skeleton))
        page.document = parse(AFTER_THE_CLICK)

    skeleton, planted = _page(BEFORE_THE_CLICK, on_click=on_click)
    pills = skeleton.locator("main").locator("[aria-expanded]")
    options = skeleton.locator(OPTIONS)
    assert run(options.count()) == 0 and run(pills.get_attribute("aria-expanded")) == "false"
    reads = planted.reads
    run(pills.nth(0).click(timeout=5000))
    assert calls == [("pill", "Pill", True)]
    assert run(pills.get_attribute("aria-expanded")) == "true"
    assert _ids(options) == ["o1", "o2"]
    assert run(options.nth(0).get_attribute("aria-label")) == "verified"
    assert planted.reads == reads  # a click is not a read


def test_a_click_with_no_stand_in_is_the_planted_pages_own_refusal() -> None:
    page, _planted = _page("<button>Go</button>")

    async def a_reader_that_catches_everything() -> str:
        try:
            await page.locator("button").click()
        except Exception:  # noqa: BLE001 -- what a reader does
            return "swallowed"
        return "clicked"

    with pytest.raises(NavigationAttempted, match="locator.click"):
        run(a_reader_that_catches_everything())


def test_a_click_resolves_strictly_before_it_refuses_or_stands_in() -> None:
    calls: list[str] = []
    page, _planted = _page("<b></b><b></b>", on_click=lambda locator, page: calls.append("x"))
    with pytest.raises(sp.TimeoutError):
        run(page.locator("button").click())
    with pytest.raises(sp.Error, match="2 elements"):
        run(page.locator("b").click())
    assert calls == []
    bare, _planted = _page("<b></b><b></b>")
    with pytest.raises(sp.TimeoutError):
        run(bare.locator("button").click())


def test_a_stand_in_may_refuse_a_transition_no_capture_shows() -> None:
    def on_click(locator: SkeletonLocator, page: SkeletonPage) -> None:
        raise NavigationAttempted("no capture shows what this opens")

    page, _planted = _page("<button>Go</button>", on_click=on_click)
    with pytest.raises(NavigationAttempted, match="no capture"):
        run(page.locator("button").click())


def test_an_async_stand_in_is_awaited() -> None:
    async def on_click(locator: SkeletonLocator, page: SkeletonPage) -> None:
        page.document = parse('<p id="after"></p>')

    page, _planted = _page("<button>Go</button>", on_click=on_click)
    run(page.locator("button").click())
    assert _ids(page.locator("p")) == ["after"]


def test_a_pinned_element_the_new_document_left_behind() -> None:
    page, _planted = _page('<div id="d"><p>one</p><p>two</p></div>', on_click=lambda locator, page: None)
    (handle,) = run(page.locator("div").element_handles())
    page.document = parse("<p></p>")
    assert run(handle.is_visible()) is False
    assert run(handle.inner_text()) == "onetwo"  # not rendered: its text content
    with pytest.raises(sp.Error, match="not attached"):
        run(handle.click())


# ===========================================================================
# READS COUNTED, AND EVERYTHING ELSE THE PLANTED PAGE'S OWN
# ===========================================================================


def test_page_locator_counts_one_read_and_nothing_chained_does() -> None:
    page, planted = _page('<main><div id="p" aria-expanded="false"><label>x</label></div></main>')
    pills = page.locator("main")
    assert planted.reads == 1
    chained = pills.locator("[aria-expanded]").nth(0).locator("label").first.last
    run(chained.count())
    run(chained.inner_text())
    run(chained.is_visible())
    run(pills.locator("[aria-expanded]").get_attribute("aria-expanded"))
    run(pills.element_handles())
    run(page.wait_for_timeout(2500))
    run(page.wait_for_load_state("domcontentloaded"))
    assert planted.reads == 1
    page.locator("main *")
    assert planted.reads == 2


def test_evaluate_counts_one_read_and_answers_from_a_registered_stand_in() -> None:
    seen: list[tuple[Any, Any]] = []

    def insights(page: SkeletonPage, arg: Any) -> dict[str, Any]:
        seen.append((page, arg))
        return {"metrics": [{"value": str(len(select(page.document, "p")))}]}

    async def later(page: SkeletonPage, arg: Any) -> str:
        return "awaited"

    page, planted = _page("<p></p><p></p>", scripts={"SCRIPT_A": insights, "SCRIPT_B": later})
    assert run(page.evaluate("SCRIPT_A", {"k": 1})) == {"metrics": [{"value": "2"}]}
    assert seen == [(page, {"k": 1})]
    assert run(page.evaluate("SCRIPT_B")) == "awaited"
    assert planted.reads == 2
    assert page.planted_answers == []


def test_an_unregistered_script_gets_the_planted_answer_and_is_recorded() -> None:
    page, planted = _page("<p></p>")
    answer = run(page.evaluate("() => document.title"))
    assert isinstance(answer, PageAnswer) and answer.get("anything") == PLANT
    assert planted.reads == 1
    assert page.planted_answers == ["page.evaluate"]


def test_everything_else_is_the_planted_pages_own() -> None:
    page, planted = _page("<p></p>")
    with pytest.raises(NavigationAttempted, match="keyboard.press"):
        run(page.keyboard.press("Escape"))
    with pytest.raises(NavigationAttempted, match="page.goto"):
        run(page.goto("https://www.linkedin.com/feed/"))
    with pytest.raises(NavigationAttempted, match="page.click"):
        run(page.click("p"))
    assert page.is_closed() is False
    assert planted.reads == 0
    located = page.get_by_role("button")
    assert run(located.inner_text()) == PLANT
    assert planted.reads == 1
    assert page.planted_answers == ["page.get_by_role"]
    assert page.url == URL and page.reads == 1


def test_a_refused_selector_counts_no_read_and_is_recorded_though_a_reader_swallows_it() -> None:
    page, planted = _page("<main><p></p></main>")

    async def a_reader() -> Any:
        try:
            return await page.locator("main > p").count()
        except Exception as exc:  # noqa: BLE001 -- what a reader does
            return {"error": type(exc).__name__}

    assert run(a_reader()) == {"error": "SelectorOutsideGrammar"}
    assert planted.reads == 0
    with pytest.raises(SelectorOutsideGrammar):
        page.locator("main").locator("p:first-child")
    assert planted.reads == 1
    assert page.unmodelled == [
        "selector: a combinator other than the descendant one",
        "selector: a pseudo-class or pseudo-element",
    ]


def test_a_locator_filter_is_refused_and_recorded() -> None:
    page, planted = _page("<main><p>x</p></main>")
    with pytest.raises(SelectorOutsideGrammar) as caught:
        page.locator("p", has_text="x")
    assert str(caught.value) == GRAMMAR_REFUSAL
    main = page.locator("main")
    with pytest.raises(SelectorOutsideGrammar):
        main.locator("p", has=main)
    assert planted.reads == 1
    assert page.unmodelled == [
        "selector: a locator filter argument (has, has_text, has_not, has_not_text)"
    ] * 2


def test_an_unmodelled_locator_method_is_recorded_and_the_planted_refusals_stay_loud() -> None:
    page, _planted = _page("<input>")
    field = page.locator("input")
    with pytest.raises(AttributeError):
        field.bounding_box  # noqa: B018 -- the access is the subject
    with pytest.raises(AttributeError):
        field.and_(field)
    assert page.unmodelled == ["locator.bounding_box", "locator.and_"]
    with pytest.raises(NavigationAttempted, match="locator.fill"):
        run(field.fill("words"))
    with pytest.raises(NavigationAttempted, match="locator.select_option"):
        run(field.select_option("x"))


# ===========================================================================
# THE TRACKED FIXTURES, BY COUNT ONLY
# ===========================================================================

TRACKED = ("synthetic/own_post_menu.html", "profile_views_analytics.html")

_FLAT_VOID = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
     "param", "source", "track", "wbr"}
)


class _FlatCount(HTMLParser):
    """AN INDEPENDENT COUNT over a fixture's markup: its own stack of open
    start tags, and each selector's MEANING written as a predicate -- neither
    the double's tree nor its selector engine. A predicate answers the key of
    what it matched (an element's number, or its parent's for ``xpath=..``),
    and the count is how many distinct keys it answered."""

    def __init__(self, predicate: Callable[[int, str, dict[str, str], list[tuple[int, str, dict[str, str]]]], Optional[int]]) -> None:
        super().__init__(convert_charrefs=True)
        self._predicate = predicate
        self._open: list[tuple[int, str, dict[str, str]]] = []
        self._dropping: Optional[str] = None
        self._number = 0
        self.keys: set[int] = set()

    def _element(self, tag: str, attrs: list[tuple[str, Optional[str]]], opens: bool) -> None:
        if self._dropping is not None:
            return
        if tag in ("script", "style"):
            if opens:
                self._dropping = tag
            return
        attributes: dict[str, str] = {}
        for name, value in attrs:
            attributes.setdefault(name, value or "")
        self._number += 1
        key = self._predicate(self._number, tag, attributes, self._open)
        if key is not None:
            self.keys.add(key)
        if opens and tag not in _FLAT_VOID:
            self._open.append((self._number, tag, attributes))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        self._element(tag, attrs, opens=True)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        self._element(tag, attrs, opens=False)

    def handle_endtag(self, tag: str) -> None:
        if self._dropping is not None:
            if tag == self._dropping:
                self._dropping = None
            return
        for index in range(len(self._open) - 1, -1, -1):
            if self._open[index][1] == tag:
                del self._open[index:]
                return


def _under_main(stack: list[tuple[int, str, dict[str, str]]]) -> bool:
    return any(tag == "main" for _number, tag, _attrs in stack)


def _is_heading(tag: str, attrs: dict[str, str]) -> bool:
    return tag in ("h1", "h2", "h3", "h4", "h5", "h6") or attrs.get("role") == "heading"


def _in_a_pill_in_main(stack: list[tuple[int, str, dict[str, str]]]) -> bool:
    for index, (_number, tag, _attrs) in enumerate(stack):
        if tag == "main":
            return any("aria-expanded" in attrs for _n, _t, attrs in stack[index + 1:])
    return False


def _parent_key(stack: list[tuple[int, str, dict[str, str]]]) -> Optional[int]:
    return stack[-1][0] if stack else None


#: Each listed selector's chain, and what it MEANS, as a predicate.
FLAT_MEANINGS: tuple[tuple[tuple[str, ...], Callable[..., Optional[int]]], ...] = (
    (("main",), lambda n, t, a, s: n if t == "main" else None),
    (("main", "[aria-expanded]"), lambda n, t, a, s: n if _under_main(s) and "aria-expanded" in a else None),
    (("main", "[aria-haspopup]"), lambda n, t, a, s: n if _under_main(s) and "aria-haspopup" in a else None),
    ((OPTIONS,), lambda n, t, a, s: n if a.get("role") in ("checkbox", "radio") and "aria-label" in a else None),
    (("button",), lambda n, t, a, s: n if t == "button" else None),
    (("main", "button"), lambda n, t, a, s: n if _under_main(s) and t == "button" else None),
    (("main *",), lambda n, t, a, s: n if _under_main(s) else None),
    (('[aria-expanded="true"]',), lambda n, t, a, s: n if a.get("aria-expanded") == "true" else None),
    (('[role="dialog"]',), lambda n, t, a, s: n if a.get("role") == "dialog" else None),
    (('[role="menu"]',), lambda n, t, a, s: n if a.get("role") == "menu" else None),
    (('[role="menuitem"]',), lambda n, t, a, s: n if a.get("role") == "menuitem" else None),
    (('[role="listbox"]',), lambda n, t, a, s: n if a.get("role") == "listbox" else None),
    (("main", HEADINGS), lambda n, t, a, s: n if _under_main(s) and _is_heading(t, a) else None),
    (("main", HEADINGS, "xpath=.."), lambda n, t, a, s: _parent_key(s) if _under_main(s) and _is_heading(t, a) else None),
    (("main", "[aria-expanded]", "label"), lambda n, t, a, s: n if t == "label" and _in_a_pill_in_main(s) else None),
    (('a[href*="/mynetwork"]',), lambda n, t, a, s: n if t == "a" and "/mynetwork" in a.get("href", "") else None),
    (('a[href*="/mynetwork"][aria-label*="new notification"]',),
     lambda n, t, a, s: n if t == "a" and "/mynetwork" in a.get("href", "")
     and "new notification" in a.get("aria-label", "") else None),
    (('a[href*="/notifications"]',), lambda n, t, a, s: n if t == "a" and "/notifications" in a.get("href", "") else None),
    (('a[href*="/notifications"][aria-label*="new notification" i]',),
     lambda n, t, a, s: n if t == "a" and "/notifications" in a.get("href", "")
     and "new notification" in a.get("aria-label", "").lower() else None),
)


def test_every_listed_selector_has_a_flat_meaning() -> None:
    assert sorted({chain[-1] for chain, _meaning in FLAT_MEANINGS}) == sorted(READER_SELECTORS)


@pytest.mark.parametrize("fixture", TRACKED)
@pytest.mark.parametrize(
    "chain, meaning", FLAT_MEANINGS, ids=[" > ".join(case[0]) for case in FLAT_MEANINGS]
)
def test_on_a_tracked_fixture_each_chain_counts_what_a_flat_reading_counts(
    fixture: str, chain: tuple[str, ...], meaning: Callable[..., Optional[int]]
) -> None:
    markup = (FIXTURES / fixture).read_text(encoding="utf-8")
    flat = _FlatCount(meaning)
    flat.feed(markup)
    flat.close()
    page, _planted = _page(markup)
    counted = run(_chain(page, chain).count())
    assert counted == len(flat.keys)


def _has_ancestor(stack: list[tuple[int, str, dict[str, str]]], test: Callable[[str, dict[str, str]], bool]) -> bool:
    return any(test(tag, attrs) for _number, tag, attrs in stack)


def _section_then_link(stack: list[tuple[int, str, dict[str, str]]]) -> bool:
    seen_section = False
    for _number, tag, _attrs in stack:
        if tag == "section":
            seen_section = True
        elif tag == "a" and seen_section:
            return True
    return False


#: Selectors in the grammar that the tracked captures DO draw. The readers'
#: own selectors find almost nothing there -- neither profile-views capture
#: draws a ``main`` -- so without these the fixture comparison would be a
#: column of zeros, which no broken engine could fail.
FIXTURE_SHAPES: tuple[tuple[tuple[str, ...], Callable[..., Optional[int]]], ...] = (
    (("*",), lambda n, t, a, s: n),
    (("div",), lambda n, t, a, s: n if t == "div" else None),
    (("span",), lambda n, t, a, s: n if t == "span" else None),
    (("p",), lambda n, t, a, s: n if t == "p" else None),
    (("a",), lambda n, t, a, s: n if t == "a" else None),
    (("figure",), lambda n, t, a, s: n if t == "figure" else None),
    (("input",), lambda n, t, a, s: n if t == "input" else None),
    (("label",), lambda n, t, a, s: n if t == "label" else None),
    (("section",), lambda n, t, a, s: n if t == "section" else None),
    (('[role="presentation"]',), lambda n, t, a, s: n if a.get("role") == "presentation" else None),
    (('hr[role="presentation"]',), lambda n, t, a, s: n if t == "hr" and a.get("role") == "presentation" else None),
    (("[role=button]",), lambda n, t, a, s: n if a.get("role") == "button" else None),
    (("[aria-label]",), lambda n, t, a, s: n if "aria-label" in a else None),
    (("a[href]",), lambda n, t, a, s: n if t == "a" and "href" in a else None),
    (('a[href*="/in/"]',), lambda n, t, a, s: n if t == "a" and "/in/" in a.get("href", "") else None),
    (('a[href^="https://www.linkedin.com/"]',),
     lambda n, t, a, s: n if t == "a" and a.get("href", "").startswith("https://www.linkedin.com/") else None),
    (('[role="tablist"] [role="tab"]',),
     lambda n, t, a, s: n if a.get("role") == "tab" and _has_ancestor(s, lambda tag, at: at.get("role") == "tablist") else None),
    (("section *",), lambda n, t, a, s: n if _has_ancestor(s, lambda tag, at: tag == "section") else None),
    (("p span",), lambda n, t, a, s: n if t == "span" and _has_ancestor(s, lambda tag, at: tag == "p") else None),
    (("div div div",), lambda n, t, a, s: n if t == "div" and sum(tag == "div" for _n, tag, _a in s) >= 2 else None),
    (("section a span",), lambda n, t, a, s: n if t == "span" and _section_then_link(s) else None),
    (('[role="region"] *',),
     lambda n, t, a, s: n if _has_ancestor(s, lambda tag, at: at.get("role") == "region") else None),
    (("div", "p"), lambda n, t, a, s: n if t == "p" and _has_ancestor(s, lambda tag, at: tag == "div") else None),
    (("a", "span"), lambda n, t, a, s: n if t == "span" and _has_ancestor(s, lambda tag, at: tag == "a") else None),
    (("figure", "xpath=.."), lambda n, t, a, s: _parent_key(s) if t == "figure" else None),
)


@pytest.mark.parametrize("fixture", TRACKED)
@pytest.mark.parametrize(
    "chain, meaning", FIXTURE_SHAPES, ids=[" > ".join(case[0]) for case in FIXTURE_SHAPES]
)
def test_on_a_tracked_fixture_the_engine_counts_what_a_flat_reading_counts(
    fixture: str, chain: tuple[str, ...], meaning: Callable[..., Optional[int]]
) -> None:
    markup = (FIXTURES / fixture).read_text(encoding="utf-8")
    flat = _FlatCount(meaning)
    flat.feed(markup)
    flat.close()
    page, _planted = _page(markup)
    assert run(_chain(page, chain).count()) == len(flat.keys)


def test_the_fixture_comparison_is_not_a_column_of_zeros() -> None:
    markup = (FIXTURES / "profile_views_analytics.html").read_text(encoding="utf-8")
    page, _planted = _page(markup)
    nonzero = [chain for chain, _meaning in FIXTURE_SHAPES if run(_chain(page, chain).count())]
    assert len(nonzero) == len(FIXTURE_SHAPES)


class _TextInside(HTMLParser):
    """The characters of text under one tag, counted flat (scripts, styles
    and comments excluded, as the double drops them)."""

    def __init__(self, tag: str) -> None:
        super().__init__(convert_charrefs=True)
        self._tag = tag
        self._depth = 0
        self._dropping: Optional[str] = None
        self.characters = 0

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag in ("script", "style"):
            self._dropping = tag
        elif tag == self._tag:
            self._depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == self._dropping:
            self._dropping = None
        elif tag == self._tag and self._depth:
            self._depth -= 1

    def handle_data(self, data: str) -> None:
        if self._depth and self._dropping is None:
            self.characters += len(data)


def test_on_the_analytics_capture_text_content_is_every_character_under_the_element() -> None:
    markup = (FIXTURES / "profile_views_analytics.html").read_text(encoding="utf-8")
    flat = _TextInside("section")
    flat.feed(markup)
    flat.close()
    page, _planted = _page(markup, answer_text=lambda text: "#" * len(text))
    assert flat.characters > 0
    assert len(run(page.locator("section").text_content())) == flat.characters


def test_what_the_tracked_fixtures_draw_that_drives_rest_on() -> None:
    """Counts the lead's drives cite (``tests/shipped_drives.py``), re-read
    through the double: the analytics capture draws no ``main``; the
    own-post fixture's static markup holds exactly one disclosure in ``main``
    -- its script appends the trigger, and a skeleton drops scripts."""
    analytics, _p1 = _page((FIXTURES / "profile_views_analytics.html").read_text(encoding="utf-8"))
    menu, _p2 = _page((FIXTURES / "synthetic/own_post_menu.html").read_text(encoding="utf-8"))
    assert run(analytics.locator("main").count()) == 0
    assert run(analytics.locator("button").count()) > 0
    assert run(analytics.locator('hr[role="presentation"]').count()) > 0
    assert run(menu.locator("main").locator("[aria-expanded]").count()) == 1
    assert run(menu.locator("main *").count()) == 2
    assert _elements(menu.document) and all(element.tag != "script" for element in _elements(menu.document))


# ===========================================================================
# THE READERS IT SERVES, DRIVEN
# ===========================================================================

#: A member's text as a skeleton draws it: a run of words made of x/X only.
SHAPED = re.compile(r"\b[xX]+(?:\s+[xX]+)*\b")


def plant_the_shapes(text: str) -> str:
    return SHAPED.sub(PLANT, text)


REVEALED_PAGE = (
    "<html><body><main>"
    "<div><h1>Xxxx xxxxx</h1></div>"
    "<section><div><h2>Highlights</h2></div>"
    "<div><p>Xxxxxxxxx, Xxxxx</p><p>Top location</p></div>"
    "<div><p>Xxxxxxxx Xxxxxxxx</p><p>Top industry</p></div>"
    "<div><p>Xxxxx Xxxxxxx</p><p>Top company</p></div></section>"
    "<section><div><h2>Details</h2></div><div><p>Companies</p><ul>"
    "<li>Xxxxx Xxxxxxx (13.3%)</li><li>Xxxxxx (6.7%)</li><li>Xxxx Xx (6.7%)</li>"
    "</ul></div></section>"
    "</main></body></html>"
)


def test_the_revealed_insights_reader_reads_a_skeleton_and_carries_the_plant_where_it_was_shaped() -> None:
    from linkedin_server import profile_views_more

    page, planted = _page(REVEALED_PAGE, answer_text=plant_the_shapes)
    out = run(profile_views_more.read_profile_views_more_insights(page))
    assert out["sections_found"] == ["highlights", "details"]
    assert out["unparsed_lines"] == 0
    assert set(out["highlights"]) == {"top_location", "top_industry", "top_company"}
    assert out["highlights"]["top_industry"] == PLANT
    assert out["highlights"]["top_location"] == f"{PLANT}, {PLANT}"
    assert out["details"]["heading"] == "companies"
    assert [entry["name"] for entry in out["details"]["entries"]] == [PLANT] * 3
    assert [entry["percent"] for entry in out["details"]["entries"]] == [13.3, 6.7, 6.7]
    assert planted.reads == 1
    assert page.unmodelled == [] and page.planted_answers == []


CLOSED_PAGE = (
    "<html><body><main><section><p>27</p><p>Profile viewers</p>"
    '<button type="button">All filters</button><button type="button">Reset</button>'
    '<button type="button">Show more analytics</button>'
    '<button type="button" aria-expanded="false">Show more analytics</button>'
    "</section></main></body></html>"
)


def test_the_reveal_reaches_its_click_and_a_stand_in_carries_it_to_the_revealed_page() -> None:
    from linkedin_server import reveal

    key = reveal.DECIDED_REVEALS[0][0]

    async def counters() -> dict[str, int]:
        return {"headline_viewers": 27}

    bare, _planted = _page(CLOSED_PAGE)
    with pytest.raises(NavigationAttempted, match="locator.click"):
        run(reveal.reveal(bare, key=key, read_counters=counters))
    assert bare.unmodelled == []

    pressed: list[str] = []

    def on_click(locator: SkeletonLocator, page: SkeletonPage) -> None:
        pressed.append(text_of(locator.element()))
        page.document = parse(REVEALED_PAGE)

    page, planted = _page(CLOSED_PAGE, on_click=on_click)
    out = run(reveal.reveal(page, key=key, read_counters=counters))
    assert pressed == ["Show more analytics"]
    assert (out["pressed"], out["permitted"], out["url_unchanged"]) == (True, True, True)
    closed_count = len(select(parse(CLOSED_PAGE), "main *"))
    revealed_count = len(select(parse(REVEALED_PAGE), "main *"))
    assert out["main_elements"] == {"before": closed_count, "after": revealed_count}
    assert planted.reads > 0 and page.unmodelled == []
