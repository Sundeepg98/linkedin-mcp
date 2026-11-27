"""An organisation Page's Products tab, read over session 12's REAL captured markup (census row J 111; lane jobs7, 2026-11-27).

Session 12's load 21 (``C-RJ26-2``) landed on the Products tab of an
organisation whose Page navigation draws one
(``tests/fixtures/live12/c_rj26_2_products.html``). By keyed shape the page
draws, in ``main``:

* the navigation's ``Products`` tab, marked current, beside ``Life`` and
  ``Insights``;
* TWO product cards, each with a name link carrying an ``aria-label`` to the
  product's own ``/products/<slug>/`` page, its ``h2`` the product's name;
* one category link per card, to ``/search/results/products/?productCategory=``,
  its paragraph the category;
* a face pile under each card (the members who use it), never read;
* a ``Show all products`` button, never pressed.

The words fixture ``tests/fixtures/live12/c_rj26_2_products_words.html`` is
that skeleton with those words written where their keyed shapes matched;
every product's own words are ``x``, and each test PLANTS synthetic ones at
the places the capture drew the real ones. Every product name here is
synthetic.

RED FIRST: before this commit there was no products tab and no reader.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import company_tabs as ct
from linkedin_server import people_data
from linkedin_server.errors import ExtractionFailedError
from tests.plantedpage import PlantedPage
from tests.skeleton_page import SkeletonPage, parse

ROOT = Path(__file__).resolve().parent.parent
LOAD_21 = ROOT / "tests" / "fixtures" / "live12" / "c_rj26_2_products_words.html"
URL = "https://www.linkedin.com/company/example-org/products/"

PRODUCTS = [("Exampleproduct Alpha", "Synthetic Category One"),
            ("Exampleproduct Beta", "Synthetic Category Two")]
NAME_H2 = '<h2 class="t-20 t-bold truncate org-product-card__entity-lockup-title">'
CATEGORY_P = '<p class="text-body-small t-black--light truncate">'
X_LINE = "\nx\n"


def _put(markup: str, at: int, value: str) -> str:
    return markup[:at] + "\n" + value + "\n" + markup[at + len(X_LINE):]


def plant(markup: str, products=PRODUCTS) -> str:
    """Each card's name and category, in the order the capture drew them."""
    out = markup
    pos = 0
    for name, category in products:
        at = out.index(X_LINE, out.index(NAME_H2, pos))
        out = _put(out, at, name)
        at = out.index(X_LINE, out.index(CATEGORY_P, at))
        out = _put(out, at, category)
        pos = at
    return out


def run(markup: str) -> dict[str, Any]:
    page = SkeletonPage(PlantedPage(), parse(markup), url=URL)
    result = asyncio.run(ct.read_products_tab(page))
    assert page.unmodelled == [] and page.planted_answers == []
    return result


def test_each_drawn_product_is_its_name_and_category_as_records():
    result = run(plant(LOAD_21.read_text(encoding="utf-8")))
    assert result["view"] == "products" and result["products_tab_drawn"] is True
    assert [p["name"]["text"] for p in result["products"]] == [n for n, _c in PRODUCTS]
    assert [p["category"]["text"] for p in result["products"]] == [c for _n, c in PRODUCTS]
    for product in result["products"]:
        assert people_data.as_record(product["name"]) is not None
        assert people_data.as_record(product["category"]) is not None
        assert product["name"]["read_from"] == "product_name"
        assert product["category"]["read_from"] == "product_category"
    assert result["products_withheld"] == 0 and result["show_all_offered"] is True


def test_no_product_string_leaves_outside_a_record():
    result = run(plant(LOAD_21.read_text(encoding="utf-8")))
    outside = repr({k: v for k, v in result.items() if k != "products"})
    for name, category in PRODUCTS:
        assert name not in outside and category not in outside


def test_a_drawn_products_tab_with_no_product_is_a_failed_read():
    """The tab marked current, its name links stripped of the label the
    reader keys a NAME link on: no product is read, and that is a failure."""
    markup = LOAD_21.read_text(encoding="utf-8").replace(
        ' aria-label="x">\n' + NAME_H2, ">\n" + NAME_H2)
    assert NAME_H2 in markup
    with pytest.raises(ExtractionFailedError):
        run(markup)


def test_a_page_whose_navigation_draws_no_products_tab_answers_none():
    """THE ZERO RULE, as a control over the same capture with its Products tab
    taken out of the navigation and no tab marked current."""
    markup = LOAD_21.read_text(encoding="utf-8").replace('aria-current="page"', "")
    # The Page's own tab navigation, inside main -- not the global bar above it.
    nav_start = markup.index("<nav", markup.index("<main"))
    nav_end = markup.index("</nav>", nav_start)
    nav = markup[nav_start:nav_end].replace("\nProducts\n", "\nAbout\n")
    assert nav != markup[nav_start:nav_end]
    result = run(markup[:nav_start] + nav + markup[nav_end:])
    assert result["products"] is None and result["products_tab_drawn"] is False


def test_the_products_tab_is_composed_from_its_one_admitted_address():
    assert ct.tab_url("5417062", "products")["url"] == (
        "https://www.linkedin.com/company/5417062/products/")
    assert ct.landed_on_tab("https://www.linkedin.com/company/example-org/products/", "products")
