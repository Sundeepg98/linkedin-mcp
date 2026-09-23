"""Turn a captured JOBS HOME into a sanitised fixture of its recent-searches list.

Kept as the PROVENANCE of ``tests/fixtures/synthetic/jobs_home_recent_searches.html``:
the exact record of what was carried over from the live capture and what was
invented, which is what a privacy review needs and cannot get from the output.

WHAT IS CARRIED OVER, AND IT IS STRUCTURE ONLY. For each entry of the
``Recent job searches`` list, in the captured order: the list item's class
(LinkedIn collapses some entries behind its show-more control, and that state
is carried), the two spans' classes, WHICH query keys the entry's href carries
and in what order, and the SHAPE of the subtitle -- which of its dot-joined
tokens are LinkedIn's own badges (``Alert On``, ``In your network``, a
workplace word) and where the place sits among them.

WHAT IS INVENTED, AND IT IS EVERY STRING A PERSON, AN EMPLOYER OR A PLACE COULD
LIVE IN. His queries become ``Placeholder ... Engineer`` by position, every
place becomes ``Placeholder City`` plus a position letter, and every query
VALUE except the history tag and the network flag is replaced: the keyword by
the invented query, ``geoId`` by the placeholder the tracked notifications
fixture already uses, ``distance`` by 25, a salary band and a time range by
fixed placeholders. So a real query, place, radius or pay expectation cannot
reach the committed file by construction, and no sanitisation key is needed.

WHAT IS ADDED, AND SAID TO BE ADDED. Three decoys the reader must NOT count,
each marked in the fixture's own comment: a history entry OUTSIDE ``main``, a
search-route anchor INSIDE ``main`` without the history tag, and a second list
under the SAME element id (the capture draws its top-applicant list that way).

The raw capture is gitignored and never committed. Re-run only after
re-capturing the landing of ``/jobs/alerts/``:

    python scripts/_build_jobs_home_fixture.py --capture <path to the capture>

It prints counts only -- never a query, a place or an id.
"""
from __future__ import annotations

import argparse
import html as htmllib
import pathlib
import re
import sys
from urllib.parse import parse_qs, urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_CAPTURE = ROOT / "_state" / "cap-ct-jobsalerts.html"
DEFAULT_OUT = ROOT / "tests" / "fixtures" / "synthetic" / "jobs_home_recent_searches.html"

LIST_LABEL = "Recent job searches"
HISTORY_ORIGIN = "SEMANTIC_SEARCH_HISTORY"
DOT = chr(0xB7)

#: LinkedIn's own subtitle badges, carried VERBATIM because they are product
#: chrome, not content. Anything else in a subtitle is the place, and is
#: replaced.
BADGES = {"alert on": "Alert On", "in your network": "In your network",
          "remote": "Remote", "hybrid": "Hybrid", "on-site": "On-site"}

#: The invented queries, by position. Six were measured; the table is longer so
#: a re-capture with more entries still builds.
QUERIES = ("Placeholder Platform Engineer", "Placeholder Data Engineer",
           "Placeholder Frontend Engineer", "Placeholder Backend Engineer",
           "Placeholder Mobile Developer", "Placeholder Cloud Developer",
           "Placeholder Test Engineer", "Placeholder Site Engineer")

#: Replacement VALUES by query key. The history tag and the network flag are
#: kept verbatim: they are LinkedIn's own vocabulary and the reader reads them.
VALUES = {"distance": "25", "geoId": "100000000", "f_SAL": "f_SA_id_000",
          "f_TPR": "r86400", "f_WT": "2", "f_E": "4", "f_JT": "F",
          "f_AL": "true", "f_EA": "true", "f_FCE": "true", "f_C": "12345",
          "f_JIYN": "true", "origin": HISTORY_ORIGIN}

_STRIP = re.compile(r"<(script|style|svg|noscript|code)\b.*?</\1>", re.S | re.I)


def _text(fragment: str) -> str:
    plain = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", htmllib.unescape(plain)).strip()


def _cls(attrs: str) -> str:
    found = re.search(r'class="([^"]*)"', attrs)
    return re.sub(r"\s+", " ", found.group(1)).strip() if found else ""


def measure(html: str) -> list[dict]:
    """The list's entries, as STRUCTURE: classes, key order, subtitle shape."""
    body = _STRIP.sub("", html)
    main = re.search(r"<main\b.*?</main>", body, re.S)
    if not main:
        raise SystemExit("the capture has no <main>")
    main_html = main.group(0)
    opened = re.search(r'<ul\b[^>]*aria-label="' + re.escape(LIST_LABEL)
                       + r'"[^>]*>', main_html)
    if not opened:
        raise SystemExit("no recent-searches list in <main>; not the jobs home")
    closed = main_html.find("</ul>", opened.end())
    region = main_html[opened.end():closed]
    entries = []
    for li in re.finditer(r"<li\b([^>]*)>(.*?)</li>", region, re.S):
        anchor = re.search(r'<a\b[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
                           li.group(2), re.S)
        if not anchor:
            continue
        href = htmllib.unescape(anchor.group(1))
        parts = urlsplit(href)
        query = parse_qs(parts.query, keep_blank_values=True)
        if query.get("origin") != [HISTORY_ORIGIN]:
            raise SystemExit("an entry of the list lacks the history tag; the "
                             "reader's discriminator would not hold here")
        keys = [k for k, _v in (p.split("=", 1) for p in parts.query.split("&")
                                if "=" in p)]
        spans = re.findall(r"<span\b([^>]*)>(.*?)</span>", anchor.group(2), re.S)
        if len(spans) != 2:
            raise SystemExit(f"an entry draws {len(spans)} spans, not 2")
        tokens = [t.strip() for t in _text(spans[1][1]).split(DOT) if t.strip()]
        shape = [BADGES.get(t.lower(), None) for t in tokens]
        entries.append({
            "li_class": _cls(li.group(1)),
            "title_class": _cls(spans[0][0]),
            "subtitle_class": _cls(spans[1][0]),
            "path": parts.path,
            "keys": keys,
            "shape": shape,          # a badge literal, or None for the place
        })
    return entries


def _href(index: int, entry: dict) -> str:
    pairs = []
    for key in entry["keys"]:
        if key == "keywords":
            pairs.append("keywords=" + QUERIES[index].replace(" ", "+"))
        else:
            pairs.append(f"{key}={VALUES.get(key, 'placeholder')}")
    return "https://www.linkedin.com" + entry["path"] + "?" + "&amp;".join(pairs)


def fixture(entries: list[dict]) -> str:
    items = []
    for index, entry in enumerate(entries):
        place = f"Placeholder City {chr(ord('A') + index)}"
        tokens = [badge if badge else place for badge in entry["shape"]]
        subtitle = f" &#183; ".join(tokens)
        items.append(
            f'<li class="{entry["li_class"]}"><div class="display-flex">'
            f'<a class="display-flex flex-column" href="{_href(index, entry)}">'
            f'<span class="{entry["title_class"]}">{QUERIES[index]}</span>'
            f'<span class="{entry["subtitle_class"]}">{subtitle}</span>'
            f"</a></div></li>")
    alerts = sum(1 for e in entries if "Alert On" in e["shape"])
    header = (
        "<!--\n"
        "  The jobs home's RECENT SEARCHES list, sanitised. Built by\n"
        "  scripts/_build_jobs_home_fixture.py from the gitignored live capture of\n"
        "  the /jobs/alerts/ landing; that capture is never committed.\n"
        f"  CARRIED OVER: {len(entries)} entries in order, each entry's list-item\n"
        "  and span classes, its href's query KEYS in order, and its subtitle's\n"
        f"  badge shape ({alerts} carry the alert badge).\n"
        "  INVENTED: every query, every place, every query value except the\n"
        "  history tag and the network flag.\n"
        "  ADDED, NOT CAPTURED: three decoys, each marked below.\n"
        "-->\n"
    )
    decoy_outside = (
        "<!-- DECOY 1, added: a history entry OUTSIDE main. -->\n"
        '<nav><a href="https://www.linkedin.com/jobs/search-results/?keywords='
        'Decoy+Outside+Main&amp;origin=SEMANTIC_SEARCH_HISTORY">'
        "<span>Decoy Outside Main</span><span>Placeholder City Z</span></a></nav>\n")
    decoy_untagged = (
        "<!-- DECOY 2, added: a search-route anchor in main WITHOUT the history"
        " tag. -->\n"
        '<a href="https://www.linkedin.com/jobs/search-results/?keywords='
        'Decoy+Untagged&amp;origin=JOBS_HOME_SEARCH_BUTTON">'
        "<span>Decoy Untagged</span><span>Placeholder City Y</span></a>\n")
    decoy_list = (
        "<!-- DECOY 3, added: a second list under the SAME element id, as the"
        " capture draws its top-applicant list. -->\n"
        '<section><h2>Placeholder second list</h2><ul aria-label="Placeholder'
        ' second list" id="jobs-home-vertical-list__entity-list">'
        '<li><a href="/jobs/collections/top-applicant/?currentJobId=1000000201">'
        "<span>Decoy Posting</span><span>Placeholder City X</span></a></li>"
        "</ul></section>\n")
    return (
        header
        + "<html><head><title>Jobs | LinkedIn</title></head><body>\n"
        + decoy_outside
        + "<main>\n<section><h2>Recent job searches</h2>"
        + '<button aria-label="Clear your search history">Clear</button>\n'
        + f'<ul aria-label="{LIST_LABEL}" id="jobs-home-vertical-list__entity-list">\n'
        + "\n".join(items)
        + "\n</ul>\n</section>\n"
        + decoy_untagged
        + decoy_list
        + "</main></body></html>\n"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--capture", type=pathlib.Path, default=DEFAULT_CAPTURE)
    ap.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    if not args.capture.is_file():
        raise SystemExit(f"no capture at {args.capture.name}; pass --capture")
    entries = measure(args.capture.read_text(encoding="utf-8", errors="replace"))
    if len(entries) > len(QUERIES):
        raise SystemExit(f"{len(entries)} entries and {len(QUERIES)} invented "
                         "queries; extend QUERIES before building")
    out = fixture(entries)
    out.encode("ascii")
    args.out.write_text(out, encoding="ascii", newline="\n")
    alerts = sum(1 for e in entries if "Alert On" in e["shape"])
    print(f"entries {len(entries)}  alert badges {alerts}  -> {args.out.name} "
          f"({len(out)} bytes)")
    return 0


if __name__ == "__main__":
    # Guarded: main() WRITES a committed fixture.
    sys.exit(main())
