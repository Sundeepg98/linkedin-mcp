"""Skeleton the people-search LINKS LinkedIn wrote with schoolFilter, industry or activelyHiring.

Kept as the PROVENANCE of ``tests/fixtures/synthetic/net7_people_search_facet_links.html``.

WHY IT EXISTS (lane ci8, 2026-11-28). ``linkedin_server.people_search`` sends
three facet keys whose spellings rest on LinkedIn's own links: ``schoolFilter``
(census ``N 88``), ``industry`` (``N 89``) and ``activelyHiring`` (``N 82``).
Lane net7 read them off the raw captures of 2026-09-20, which are gitignored
because they hold real people, and lane S's committed table records them by
name. No tracked fixture carried them, so no committed test and no CI run could
check the spellings again (the wave-7 verifier's F2). This builder keeps the
SHAPE of every such link, so a test can.

WHAT IS KEPT, per capture: every ``<a href>`` whose path is LinkedIn's
people-search results page and whose query carries one of the three keys. Of
each link: its scheme, host and path, and its query's KEYS, in their order.

WHAT IS REPLACED, EVERY TIME, value by value, in the same shape:

    a run of digits                -> 9s, as many: an 8-digit school id, a
                                      3-digit industry id, a geo id
    a company id (currentCompany)  -> 902611, an id the identity guard declares
                                      invented (its SYNTHETIC_IDS): the guard
                                      holds every company id in a tracked file
                                      to that list, and a fresh number could be
                                      a real company's, so the id's LENGTH is
                                      the declared id's, not the capture's
    a JSON list or string          -> the same JSON, each digit run 9s, then
                                      percent-encoded if the capture encoded it
    activelyHiring's "true"        -> kept: it is LinkedIn's switch, not data
    an origin, [A-Z_]{3,40}        -> kept: LinkedIn's own enum
    keywords, and any other value  -> "example"

WHAT IS DROPPED: everything else on the page, so no person, name, slug,
member id, employer or page text survives -- the link's own text too, which is
written as "link". Each capture's links sit under a ``data-capture`` attribute
naming the capture by its file stem, which names a surface and never a person.

THE CAPTURES ARE NEVER COPIED. They are read in place, read-only, from the
directory given, and the only file written is the fixture:

    python scripts/_build_net7_facet_link_skeleton.py --captures <the main checkout's _state>

IT PRINTS COUNTS ONLY: links and keys per capture, never a value or an href.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "synthetic" / "net7_people_search_facet_links.html"

#: The three keys this skeleton exists for.
KEYS = ("schoolFilter", "industry", "activelyHiring")
PEOPLE_SEARCH_PATH = "/search/results/people/"
#: LinkedIn's origin enums, the only free-standing words kept.
ENUM = re.compile(r"[A-Z_]{3,40}")
KEPT_VERBATIM = {("activelyHiring", '"true"')}
#: tests/test_no_committed_identity.py's SYNTHETIC_IDS declares it invented.
DECLARED_COMPANY_ID = "902611"
COMPANY_KEYS = frozenset({"currentCompany", "companyId"})

PROVENANCE = """\
<!doctype html>
<!--
  LANE CI8, 2026-11-28: a SKELETON of the people-search links LinkedIn wrote
  with schoolFilter, industry or activelyHiring on the raw captures of
  2026-09-20, built by scripts/_build_net7_facet_link_skeleton.py. Every link's
  scheme, host, path and query keys are LinkedIn's, in LinkedIn's order; every
  value is synthetic in the captured shape (each digit 9, JSON kept as JSON,
  percent-encoded where the capture encoded it; a company id is the identity
  guard's declared 902611), except activelyHiring's "true" and the origin
  enums, which are LinkedIn's constants. No person,
  name, slug, member id, employer or page text: the raws are gitignored and
  are never committed. tests/test_people_search_sends_linkedins_facet_keys.py
  reads it.
-->
"""


class _Hrefs(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):  # noqa: ANN001
        if tag != "a":
            return
        for name, value in attrs:
            if name == "href" and value:
                self.hrefs.append(value)


def _nines(text: str) -> str:
    return re.sub(r"\d", "9", text)


def synthetic(key: str, value: str) -> str:
    """The value LinkedIn wrote for ``key``, in its shape, holding nothing of it."""
    decoded = unquote(value)
    if (key, decoded) in KEPT_VERBATIM:
        return value
    if key == "origin" and ENUM.fullmatch(decoded):
        return value
    if key in COMPANY_KEYS and decoded.isdigit():
        return DECLARED_COMPANY_ID
    if decoded.isdigit():
        return _nines(decoded)
    try:
        parsed = json.loads(decoded)
    except ValueError:
        parsed = None
    if isinstance(parsed, (list, str)) and key != "keywords":
        rebuilt = _nines(json.dumps(parsed, separators=(",", ":")))
        return quote(rebuilt, safe="") if "%" in value else rebuilt
    return "example"


def skeleton_links(text: str) -> list[str]:
    """Every people-search href of ``text`` that carries one of the KEYS, as a
    skeleton href; nothing else."""
    parser = _Hrefs()
    parser.feed(text)
    out = []
    for href in parser.hrefs:
        parts = urlsplit(href)
        if parts.path != PEOPLE_SEARCH_PATH:
            continue
        pairs = [pair.split("=", 1) + [""] for pair in parts.query.split("&") if pair]
        if not any(pair[0] in KEYS for pair in pairs):
            continue
        query = "&".join(f"{key}={synthetic(key, value)}" for key, value, *_ in pairs)
        out.append(f"{parts.scheme}://{parts.netloc}{parts.path}?{query}")
    return out


def build(captures: Path) -> tuple[str, list[tuple[str, int, list[str]]]]:
    sections = []
    counts = []
    for path in sorted(captures.glob("cap-*.html")):
        links = skeleton_links(path.read_text(encoding="utf-8", errors="replace"))
        if not links:
            continue
        stem = path.stem[len("cap-"):]
        counts.append((stem, len(links), sorted({k for link in links for k in KEYS
                                                 if f"?{k}=" in link or f"&{k}=" in link})))
        anchors = "\n".join(f'  <a href="{link.replace("&", "&amp;")}">link</a>' for link in links)
        sections.append(f'<section data-capture="{stem}">\n{anchors}\n</section>')
    body = "<html><body><main>\n" + "\n".join(sections) + "\n</main></body></html>\n"
    return PROVENANCE + body, counts


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--captures", required=True,
                        help="the directory holding the raw cap-*.html captures, read in place")
    parser.add_argument("--out", default=str(FIXTURE), help="the fixture to write")
    args = parser.parse_args(argv[1:])
    captures = Path(args.captures)
    if not captures.is_dir():
        print("no capture directory at the path given", file=sys.stderr)
        return 1
    text, counts = build(captures)
    if not counts:
        print("no capture held a people-search link with any of the three keys; "
              "nothing written", file=sys.stderr)
        return 1
    if not text.isascii():
        print("the skeleton is not ASCII; nothing written", file=sys.stderr)
        return 1
    Path(args.out).write_text(text, encoding="ascii", newline="\n")
    for stem, links, keys in counts:
        print(f"{stem}: {links} link(s), keys {keys}")
    print(f"wrote the skeleton: {sum(c[1] for c in counts)} link(s) from {len(counts)} capture(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
