"""An organisation Page's LIFE tab, read over REAL captured markup.

Census row ``J 109`` (*Company Page Life tab*). Lane build-jobs2, 2026-11-26,
over the live lane's session-11 capture of the tab (load 22), tracked as
``tests/fixtures/live11/company_life.html`` and, with four of LinkedIn's
words measured by keyed shape, as ``company_life_words.html``
(``scripts/_build_jobs2_word_skeletons.py``). Every reading runs
``company_tabs.read_life_tab`` through ``tests/skeleton_page.py``, which
answers Playwright's locators from the parsed document with no browser.

Every member's name and words, and every Page's, are ``x`` in the fixtures,
as in the capture's tracked copy; each test PLANTS synthetic values into the
parsed document, at the place the capture drew the real one -- the two
trending items' author blocks, permalinks and words, and the three
spotlights' titles and bodies.

Every name-shaped string in this file is synthetic.
"""
from __future__ import annotations

import asyncio
from typing import Any, Callable, Iterator, Optional

import pytest

from linkedin_server import company_tabs as ct
from linkedin_server import people_data
from linkedin_server.errors import ExtractionFailedError
from tests.live11_words import chromium_page, plain, words  # noqa: F401 -- a fixture
from tests.plantedpage import PlantedPage
from tests.skeleton_page import Element, SkeletonPage, Text, parse

LIFE_URL = "https://www.linkedin.com/company/example-org/life/"

#: A marker no fixture draws: where it is planted, it may come back only
#: inside a record's declared field, or not at all.
MARKER = "Exampleperson Markersurname"

#: The two trending items' synthetic authors, slugs and post ids, in document
#: order -- declared people (``tests/test_fixtures_hold_only_synthetic_people.py``).
AUTHORS = ("Kai Example", "Juno Fixture")
SLUGS = ("kai-example-1a2b", "juno-example-3c4d")
POST_IDS = ("7400000000000000001", "7400000000000000002")
#: The see-more control's text, as the reader cuts it from the words' end.
MORE = chr(0x2026) + "more"


# ---------------------------------------------------------------------------
# The parsed document, and the plants
# ---------------------------------------------------------------------------


def elements(node: Element) -> Iterator[Element]:
    yield node
    for child in node.children:
        if isinstance(child, Element):
            yield from elements(child)


def texts(node: Element) -> Iterator[Text]:
    for child in node.children:
        if isinstance(child, Text):
            yield child
        else:
            yield from texts(child)


def where(root: Element, test: Callable[[Element], bool]) -> list[Element]:
    return [node for node in elements(root) if test(node)]


def view(name: str) -> Callable[[Element], bool]:
    return lambda node: node.attrs.get("data-view-name") == name


def shaped(node: Element) -> list[Text]:
    """The text nodes under ``node`` that the capture reduced to ``x``."""
    return [text for text in texts(node) if text.data.strip() == "x"]


def set_text(node: Element, value: str) -> None:
    """The ONE reduced text under ``node``, set to ``value``."""
    found = shaped(node)
    assert len(found) == 1, "the plant expects exactly one reduced text here, found %d" % len(found)
    found[0].data = "\n" + value + "\n"


def trending_items(root: Element) -> list[Element]:
    module = where(root, view("org-member-life-trending-employee-content"))
    assert len(module) == 1
    articles = where(module[0], lambda n: n.attrs.get("role") == "article")
    leaves = [a for a in articles if len(where(a, lambda n: n.attrs.get("role") == "article")) == 1]
    assert len(articles) == 3 and len(leaves) == 2, "the capture draws one wrapper and two items"
    return leaves


def _member_links(node: Element) -> list[Element]:
    return where(node, lambda n: n.tag == "a" and "/in/" in n.attrs.get("href", ""))


def _permalink(item: Element) -> Element:
    found = where(item, lambda n: n.tag == "a" and "/feed/update/" in n.attrs.get("href", ""))
    assert len(found) == 1
    return found[0]


def plant_item(item: Element, index: int, *, name: Optional[str] = None,
               slug: Optional[str] = None, word_lines: Optional[list[str]] = None) -> None:
    """One trending item, its author, profile, permalink and words synthetic."""
    name = AUTHORS[index] if name is None else name
    slug = SLUGS[index] if slug is None else slug
    link = _permalink(item)
    outside = [a for a in _member_links(item) if a not in _member_links(link)]
    assert len(outside) == 2, "the capture draws the avatar link and the name block"
    for anchor in outside:
        anchor.attrs["href"] = "https://www.linkedin.com/in/%s?miniProfileUrn=urn%%3Ali%%3Afsd_profile%%3AExample" % slug
    block = [a for a in outside if where(a, lambda n: n.tag == "span" and n.attrs.get("aria-hidden") == "true")]
    assert len(block) == 1
    # MEASURED: the name block holds three aria-hidden spans, and ONE of them
    # inside a span carrying dir -- the name, where the capture drew it.
    named = [s for d in where(block[0], lambda n: n.tag == "span" and "dir" in n.attrs)
             for s in where(d, lambda n: n.tag == "span" and n.attrs.get("aria-hidden") == "true")]
    assert len(where(block[0], lambda n: n.tag == "span" and n.attrs.get("aria-hidden") == "true")) == 3
    assert len(named) == 1
    set_text(named[0], name)
    link.attrs["href"] = "/feed/update/urn:li:activity:%s/" % POST_IDS[index]
    buttons = where(link, lambda n: n.tag == "button")
    for button in buttons:
        set_text(button, MORE)
    lines = word_lines if word_lines is not None else None
    reduced = [t for t in shaped(link) if not any(t in list(texts(b)) for b in buttons)]
    for number, text in enumerate(reduced):
        text.data = "\n" + (lines[number] if lines and number < len(lines)
                            else "Example post words %d.%d" % (index + 1, number + 1)) + "\n"


def spotlights(root: Element) -> list[Element]:
    found = where(root, view("org-member-life-company-spotlight"))
    assert len(found) == 3
    return found


def plant_spotlight(row: Element, index: int) -> None:
    """MEASURED: a spotlight holds TWO paragraphs -- one inside its video
    player's dialog, one beside its title -- so the body planted is the one
    under the title's own parent, where the reader looks."""
    assert len(where(row, lambda n: n.tag == "p")) == 2
    (title,) = where(row, lambda n: n.tag == "h4")
    (body,) = where(title.parent, lambda n: n.tag == "p")
    set_text(title, "Example spotlight %d" % (index + 1))
    set_text(body, "Example spotlight words %d." % (index + 1))


def life(plant_people: bool = True, markup: Optional[str] = None) -> Element:
    root = parse(markup if markup is not None else words("company_life"))
    if plant_people:
        for index, item in enumerate(trending_items(root)):
            plant_item(item, index)
        for index, row in enumerate(spotlights(root)):
            plant_spotlight(row, index)
    return root


def run(root: Element) -> tuple[dict[str, Any], SkeletonPage]:
    page = SkeletonPage(PlantedPage(), root, url=LIFE_URL)
    return asyncio.run(ct.read_life_tab(page)), page


def outside_records(value: Any) -> list[str]:
    """Strings that sit outside any people_data record."""
    found: list[str] = []

    def walk(item: Any) -> None:
        record = people_data.as_record(item) if isinstance(item, dict) else None
        if record is not None:
            return
        if isinstance(item, str):
            found.append(item)
        elif isinstance(item, dict):
            for key, inner in item.items():
                found.append(str(key))
                walk(inner)
        elif isinstance(item, (list, tuple)):
            for inner in item:
                walk(inner)

    walk(value)
    return found


# ---------------------------------------------------------------------------
# The reading
# ---------------------------------------------------------------------------


def test_the_life_tab_counts_its_modules_by_linkedins_own_names():
    result, page = run(life())
    assert page.unmodelled == [] and page.planted_answers == []
    assert result["tab"] == "life" and result["view"] == "life"
    assert result["modules"] == {
        "hero_media": 1,
        "featured_members": 1,
        "trending_employee_content": 1,
        "interest_pipeline": 1,
        "company_spotlight": 3,
        "company_photos": 1,
    }
    assert result["interest_offered"] is True
    assert result["photos"] == {"heading_matched": True, "drawn": 2}
    assert result["reads_failed"] == 0


def test_each_trending_item_returns_as_a_post_record_its_author_a_person():
    result, _ = run(life())
    trending = result["trending"]
    assert trending["heading_matched"] is True
    assert trending["articles_seen"] == 3
    assert trending["skipped"] == {
        "not_visible": 0, "holds_other_items": 1, "not_one_permalink": 0,
        "not_one_author_block": 0, "more_than_one_profile": 0,
        "no_member_author": 0, "changed_while_read": 0, "no_words": 0,
    }
    # The first item draws a see-more control, the second none.
    assert trending["more_controls_drawn"] == 1
    posts = trending["posts"]
    assert [p["author"]["name"] for p in posts] == list(AUTHORS)
    assert [p["author"]["link"] for p in posts] == [
        "https://www.linkedin.com/in/%s/" % slug for slug in SLUGS]
    assert [p["link"] for p in posts] == [
        "https://www.linkedin.com/feed/update/urn:li:activity:%s/" % pid for pid in POST_IDS]
    for index, post in enumerate(posts):
        assert people_data.as_record(post) is not None
        assert post["author"]["headline"] is None and post["author"]["degree"] is None
        assert post["text"].startswith("Example post words %d.1" % (index + 1))
        assert MORE not in post["text"], "the see-more control's own text is cut from the words"
        assert post[people_data.UNTRUSTED_KEY] == people_data.UNTRUSTED_NOTE


def test_each_spotlight_returns_its_title_and_words_as_the_pages_prose():
    result, _ = run(life())
    spot = result["spotlights"]
    assert spot["heading_matched"] is True and spot["withheld"] == 0 and spot["beyond_bound"] == 0
    assert [s["title"]["text"] for s in spot["spotlights"]] == [
        "Example spotlight 1", "Example spotlight 2", "Example spotlight 3"]
    assert [s["body"]["text"] for s in spot["spotlights"]] == [
        "Example spotlight words 1.", "Example spotlight words 2.", "Example spotlight words 3."]
    assert {s["title"]["read_from"] for s in spot["spotlights"]} == {"life_spotlight_title"}
    assert {s["body"]["read_from"] for s in spot["spotlights"]} == {"life_spotlight_body"}


def test_a_member_mentioned_in_the_words_is_never_taken_for_the_author():
    root = life()
    item = trending_items(root)[0]
    hashtag = where(_permalink(item), lambda n: n.tag == "a" and "/search/results/" in n.attrs.get("href", ""))
    hashtag[0].attrs["href"] = "https://www.linkedin.com/in/lea-example-5e6f/"
    result, _ = run(root)
    assert result["trending"]["posts"][0]["author"]["link"] == "https://www.linkedin.com/in/kai-example-1a2b/"


def test_a_second_profile_outside_the_words_skips_the_item_never_chooses():
    root = life()
    item = trending_items(root)[0]
    outside = [a for a in _member_links(item) if a not in _member_links(_permalink(item))]
    avatar = [a for a in outside if not where(a, lambda n: n.tag == "span" and n.attrs.get("aria-hidden") == "true")]
    avatar[0].attrs["href"] = "https://www.linkedin.com/in/lea-example-5e6f/"
    result, _ = run(root)
    assert [p["author"]["name"] for p in result["trending"]["posts"]] == ["Juno Fixture"]
    assert result["trending"]["skipped"]["more_than_one_profile"] == 1


def _name_block(item: Element) -> Element:
    outside = [a for a in _member_links(item) if a not in _member_links(_permalink(item))]
    (block,) = [a for a in outside if where(a, lambda n: n.tag == "span" and "dir" in n.attrs)]
    return block


def test_the_name_is_found_by_structure_never_by_position():
    """The name block's other two aria-hidden spans -- the supplementary line
    and the headline -- are never read: a value planted in each leaves
    nowhere. And with the name's ``dir`` span gone, the block holds no name
    span, so the item is skipped rather than named off the first span."""
    root = life()
    block = _name_block(trending_items(root)[0])
    others = [s for s in where(block, lambda n: n.tag == "span" and n.attrs.get("aria-hidden") == "true")
              if not any(s in where(d, lambda n: True)
                         for d in where(block, lambda n: n.tag == "span" and "dir" in n.attrs))]
    assert len(others) == 2
    for span in others:
        set_text(span, "Examplepage Headlineword")
    result, _ = run(root)
    assert result["trending"]["posts"][0]["author"]["name"] == "Kai Example"
    assert "Examplepage Headlineword" not in repr(result)

    root = life()
    block = _name_block(trending_items(root)[0])
    for span in where(block, lambda n: n.tag == "span" and "dir" in n.attrs):
        del span.attrs["dir"]
    result, _ = run(root)
    assert [p["author"]["name"] for p in result["trending"]["posts"]] == ["Juno Fixture"]
    assert result["trending"]["skipped"]["not_one_author_block"] == 1


def test_an_item_with_no_words_is_counted_and_never_returned():
    root = life()
    item = trending_items(root)[1]
    for text in texts(_permalink(item)):
        text.data = " "
    result, _ = run(root)
    assert [p["author"]["name"] for p in result["trending"]["posts"]] == ["Kai Example"]
    assert result["trending"]["skipped"]["no_words"] == 1


def test_with_its_words_reduced_no_section_is_read_by_heading():
    result, _ = run(parse(plain("company_life")))
    assert result["modules"]["trending_employee_content"] == 1
    assert result["trending"]["heading_matched"] is False and result["trending"]["posts"] is None
    assert result["spotlights"] is None
    assert result["photos"] == {"heading_matched": False, "drawn": 2}
    assert result["interest_offered"] is False


def test_a_carousel_that_drew_no_item_yet_is_unread_never_empty():
    root = life()
    module = where(root, view("org-member-life-trending-employee-content"))[0]
    for node in where(module, lambda n: n.attrs.get("role") == "article"):
        node.attrs["role"] = "none"
    result, _ = run(root)
    assert result["trending"]["articles_seen"] == 0
    assert result["trending"]["posts"] is None


def test_a_page_with_no_life_module_is_a_failed_read_never_an_empty_tab():
    markup = '<!doctype html><html><body><main><nav><a aria-current="page" href="/company/x/life/">x</a></nav><p>x</p></main></body></html>'
    with pytest.raises(ExtractionFailedError):
        run(parse(markup))


def test_a_planted_name_leaves_only_inside_records():
    root = life()
    for text in texts(root):
        if text.data.strip() == "x":
            text.data = MARKER
    result, page = run(root)
    assert page.unmodelled == []
    assert result["trending"]["posts"] and result["spotlights"]["spotlights"]
    assert not [s for s in outside_records(result) if MARKER in s or "Example" in s]


# ---------------------------------------------------------------------------
# The address, and the landing's veto
# ---------------------------------------------------------------------------


def test_the_life_tab_is_composed_from_the_numeric_id_and_a_constant():
    assert ct.tab_url("5417062", "life") == {
        "built": True, "url": "https://www.linkedin.com/company/5417062/life/",
        "identifier": "5417062", "tab": "life",
    }


def test_the_read_boundary_admits_the_composed_address():
    from linkedin_server import readonly

    assert readonly.is_read_url(ct.tab_url("5417062", "life")["url"])


@pytest.mark.parametrize("landed,ok", [
    ("https://www.linkedin.com/company/example-org/life/", True),
    ("https://www.linkedin.com/company/5417062/life", True),
    ("https://www.linkedin.com/company/example-org/", False),
    ("https://www.linkedin.com/company/example-org/life/7000000000/", False),
    ("https://www.linkedin.com/company/unavailable/life/", False),
])
def test_the_landing_may_veto_the_life_tab(landed, ok):
    assert ct.landed_on_tab(landed, "life") is ok


def test_the_tool_reads_the_life_tab_with_its_own_reader():
    import ast
    from pathlib import Path

    source = (Path(ct.__file__).resolve().parent / "server.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    tool = [n for n in ast.walk(tree)
            if isinstance(n, ast.AsyncFunctionDef) and n.name == "linkedin_company_page_tab"]
    assert len(tool) == 1
    calls = {ast.unparse(c.func) for c in ast.walk(tool[0]) if isinstance(c, ast.Call)}
    assert "company_tabs.read_life_tab" in calls


# ---------------------------------------------------------------------------
# The same reading in a real engine
# ---------------------------------------------------------------------------


def _replace_in_order(markup: str, old: str, news: list[str]) -> str:
    """Each occurrence of ``old``, in document order, replaced by the next of
    ``news`` -- and the markup must draw exactly that many."""
    head, sep, body = markup.partition("\n-->\n")
    assert body.count(old) == len(news), (body.count(old), len(news))
    for new in news:
        body = body.replace(old, new, 1)
    return head + sep + body


def real_engine_markup() -> str:
    """The words fixture with the two items' authors and permalinks planted
    as markup, for a browser: the parsed-tree plants above have no
    serialiser."""
    markup = words("company_life")
    member = 'href="https://www.linkedin.com/in/x?miniProfileUrn=x"'
    markup = _replace_in_order(markup, member, [
        'href="https://www.linkedin.com/in/%s?miniProfileUrn=x"' % slug
        for slug in (SLUGS[0], SLUGS[0], SLUGS[1], SLUGS[1])])
    name = '<span dir="ltr">\n<span aria-hidden="true">\nx\n</span>'
    markup = _replace_in_order(markup, name, [
        name.replace("\nx\n", "\n%s\n" % author) for author in AUTHORS])
    for anchor, post in (('id="k26f6e803"', POST_IDS[0]), ('id="k09155234"', POST_IDS[1])):
        old = 'href="/feed/update/urn:li:activity:x/" ' + anchor
        markup = _replace_in_order(markup, old, [
            'href="/feed/update/urn:li:activity:%s/" %s' % (post, anchor)])
    return markup


def test_the_double_keeps_the_permalink_whole_as_the_live_page_drew_it():
    """MEASURED, the reason the skeleton double is this capture's engine: the
    live page built its DOM by script, and its serialised skeleton draws each
    item's permalink anchor HOLDING the hashtag anchors (three and one). The
    double keeps that tree as serialised: one permalink per item."""
    root = parse(real_engine_markup())
    for item, inner in zip(trending_items(root), (3, 1)):
        permalinks = where(item, lambda n: n.tag == "a" and "/feed/update/" in n.attrs.get("href", ""))
        assert len(permalinks) == 1
        assert len(where(permalinks[0], lambda n: n.tag == "a" and "/search/results/" in n.attrs.get("href", ""))) == inner


async def test_a_browser_reparse_splits_the_permalink_and_every_item_is_skipped_loudly(chromium_page):
    """A BROWSER RE-PARSING THE SKELETON DOES NOT REBUILD THE LIVE DOM. The
    HTML parser never nests an anchor in an anchor: ``set_content`` closes the
    permalink at its first hashtag and reconstructs it after each one, so a
    local headless Chromium (every request refused) draws THREE copies of each
    item's permalink and no hashtag inside any. That is the parser's repair,
    not the page. What it shows is the reader's failure mode on a DOM it does
    not know: every item is counted ``not_one_permalink`` and none is read --
    never words pieced together from the copies, never a silent zero."""
    await chromium_page.set_content(real_engine_markup(), wait_until="domcontentloaded")
    result = await ct.read_life_tab(chromium_page)
    assert result["view"] == "life" and result["reads_failed"] == 0
    assert result["modules"] == {
        "hero_media": 1, "featured_members": 1, "trending_employee_content": 1,
        "interest_pipeline": 1, "company_spotlight": 3, "company_photos": 1,
    }
    trending = result["trending"]
    assert trending["posts"] == [], "items were drawn, so the list is read -- and empty"
    assert trending["skipped"]["not_one_permalink"] == 2
    assert trending["skipped"]["holds_other_items"] == 1
    # The rest of the tab does not rest on a nested anchor, and reads the same.
    assert result["spotlights"]["heading_matched"] is True
    assert len(result["spotlights"]["spotlights"]) == 3
    assert result["photos"] == {"heading_matched": True, "drawn": 2}
    assert result["interest_offered"] is True
