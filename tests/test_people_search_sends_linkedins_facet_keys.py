"""The facet keys ``people_search`` sends are the keys LinkedIn writes, read
off a skeleton of LinkedIn's own links.

WHY (lane ci8, 2026-11-28; the wave-7 verifier's F2 on lane net7). Three keys
the people search sends -- ``schoolFilter`` (census ``N 88``), ``industry``
(``N 89``) and ``activelyHiring`` (``N 82``) -- were spelled from LinkedIn's
own links on the raw captures of 2026-09-20. Those are gitignored, because
they hold real people, and no tracked fixture carried the keys. So no
committed test and no CI run could check the spellings again: a key renamed
in the code would still be checked only against the code.

``tests/fixtures/synthetic/net7_people_search_facet_links.html`` is a
SKELETON of every such link (``scripts/_build_net7_facet_link_skeleton.py``):
LinkedIn's scheme, host, path and query keys in LinkedIn's order, every value
synthetic in the captured shape. This file reads the keys off it and holds
the code to them:

* each key is on LinkedIn's own links, as many times as the captures wrote it;
* :func:`people_search.compose` sends that exact spelling, with the value in
  the form on record: ``activelyHiring`` as LinkedIn's JSON string ``"true"``
  exactly (MEASURED), ``schoolFilter`` and ``industry`` as a JSON list holding
  LinkedIn's bare value (the list form is DERIVED, as the module says);
* :func:`people_search.landing_verdict` reads LinkedIn's own link as the
  address the code asked for.

SHOWN FAILING by renaming each key in ``people_search``; the record of lane
ci8, section 13, has the counts.
"""

from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

import pytest

from linkedin_server import people_search

FIXTURE = (Path(__file__).resolve().parent / "fixtures" / "synthetic"
           / "net7_people_search_facet_links.html")
BUILDER = "scripts/_build_net7_facet_link_skeleton.py"

#: (tool argument, the key LinkedIn writes, how many of the skeleton's links
#: carry it): 1 on a job collection, 6 on the two profile-views captures and
#: search appearances, 2 on the premium hub and a role-play page.
EXPECTED = [
    ("school_ids", "schoolFilter", 1),
    ("industry_ids", "industry", 6),
    ("actively_hiring", "activelyHiring", 2),
]


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.capture = None
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag, attrs):  # noqa: ANN001
        attrs = dict(attrs)
        if tag == "section":
            self.capture = attrs.get("data-capture")
        if tag == "a" and attrs.get("href"):
            self.links.append((self.capture, attrs["href"]))


def _text() -> str:
    """The skeleton as committed: strict ASCII, line ends read as LF."""
    return FIXTURE.read_bytes().decode("ascii").replace("\r\n", "\n")


def _links() -> list[tuple[str, str]]:
    parser = _Links()
    parser.feed(_text())
    return parser.links


def _carrying(key: str) -> list[tuple[str, str]]:
    return [(capture, href) for capture, href in _links()
            if key in dict(parse_qsl(urlsplit(href).query))]


def _composed(argument: str, value: str) -> str:
    kwargs = {argument: True} if argument == "actively_hiring" else {argument: value}
    built = people_search.compose(**kwargs)
    assert built.get("built") is True, built
    return built["url"]


def test_the_skeleton_opens_with_its_provenance_and_is_strict_ascii():
    text = _text()
    assert text.startswith("<!doctype html>\n<!--\n  LANE CI8, 2026-11-28: a SKELETON"), text[:80]
    assert BUILDER in text


def test_every_link_is_linkedins_people_search_and_nothing_else():
    links = _links()
    assert len(links) == sum(count for _a, _k, count in EXPECTED), links
    for capture, href in links:
        parts = urlsplit(href)
        assert (parts.scheme, parts.netloc, parts.path) == (
            "https", "www.linkedin.com", "/search/results/people/"), (capture, href)


@pytest.mark.parametrize(("argument", "key", "count"), EXPECTED, ids=[k for _a, k, _c in EXPECTED])
def test_the_key_is_on_linkedins_own_links(argument, key, count):
    assert len(_carrying(key)) == count, [c for c, _h in _carrying(key)]


@pytest.mark.parametrize(("argument", "key", "count"), EXPECTED, ids=[k for _a, k, _c in EXPECTED])
def test_the_code_sends_the_key_linkedin_writes(argument, key, count):
    _capture, href = _carrying(key)[0]
    written = dict(parse_qsl(urlsplit(href).query))[key]
    sent = dict(parse_qsl(urlsplit(_composed(argument, written)).query))
    assert key in sent, (
        f"LinkedIn writes {key!r} on its own people-search links, and "
        f"compose({argument}=...) sends {sorted(sent)}")
    if argument == "actively_hiring":
        assert sent[key] == written == '"true"', (sent[key], written)
    else:
        assert json.loads(sent[key]) == [written], (sent[key], written)


@pytest.mark.parametrize(("argument", "key", "count"), EXPECTED, ids=[k for _a, k, _c in EXPECTED])
def test_linkedins_own_link_lands_as_the_address_the_code_asked_for(argument, key, count):
    for capture, href in _carrying(key):
        written = dict(parse_qsl(urlsplit(href).query))[key]
        verdict = people_search.landing_verdict(href, _composed(argument, written))
        assert verdict["on_people_search"] is True, (capture, verdict)
        want = "verbatim" if argument == "actively_hiring" else "same_values"
        assert verdict["query_kept"].get(argument) == want, (capture, verdict)
