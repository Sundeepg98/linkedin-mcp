"""Write the two tracked skeletons of lane L1's session-1 pages: his articles list (M C48) and one of his posts' analytics (M C38).

Lane B3 (child reads), 2026-10-10. Writes, and writes nothing else:

    tests/fixtures/live1/articles.html       from the raw capture of
                                             /in/me/recent-activity/articles/
    tests/fixtures/live1/post_summary.html   from the raw capture of
                                             /analytics/post-summary/urn:li:activity:<id>/

WHAT THE CAPTURES ARE. The live lane's session 1 (2026-09-23 22:48) saved both
pages RAW under a gitignored ``_state/`` (``l1-articles.html``,
``l1-post_summary.html``); they show other people and are never committed. The
paths are ARGUMENTS, defaulting to ``_state/`` under this repository, so no
absolute workspace path is written here.

WHAT THIS WRITES. The shipped reduction, IMPORTED AND NOT REWRITTEN:
``_probe_live_lane_session_2.skeleton_of(page_html, key)`` and then
``tracked_copy(skeleton)``. Every text node and attribute value becomes a
keyed shape, and the tracked copy turns every keyed shape into ONE ``x`` (an
id reference keeps ``k`` and its 8-hex hash, which names a control, never a
person). The key is ``os.urandom(32)``, fresh on every run and never written
anywhere: the copy keeps no hash a key could be tested against.

ONE SUBSTITUTION IS MADE BETWEEN THE TWO, and it is the closed tuple
:data:`KEPT_WORDS`. The shared reduction keeps LinkedIn's own words only when
they are in its ``FURNITURE`` set, and the two readers built over these
skeletons key on words that set does not hold, so the copy would turn each into
``x`` and no reader could be tested on it. Each kept word is a FIXED PRODUCT
STRING LinkedIn writes on every account's page -- a heading, a tab label, a
category name -- and never a value that names a person, an employer, a school,
a place or a job title of a real person. It is restored ONLY where a WHOLE text
node, or the WHOLE value of a label attribute, equals it, matched by its keyed
shape under this run's key (letters, digits, length AND the keyed hash), so a
value that merely contains the word stays ``x``. The shared script is not
edited; ``FURNITURE`` is not touched.

THE DEMOGRAPHIC VALUES STAY ``x``. On the per-post page each of the five
demographic rows draws a category word (kept), a VALUE -- a job title, a
location, a company, an industry, a seniority or a company size of the people
who viewed his post -- and a percentage. The values are other people's data,
however aggregated, and the percentages are his post's audience numbers: both
reduce to ``x`` like every other text. A reader's positive path is tested on a
copy with SYNTHETIC values planted, never on these.

It prints sizes and counts, never a value, and REFUSES to write if any keyed
shape survives the reduction or the copy is not strict ASCII.

    python scripts/_build_live1_l1_fixtures.py [--articles <raw>] [--post-summary <raw>]
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _probe_live_lane_session_2 import (  # noqa: E402
    LABEL_ATTRIBUTES,
    _KEYED_SHAPE,
    skeleton_of,
    tracked_copy,
    value_shape,
)

REPO = HERE.parent
OUT_DIR = REPO / "tests" / "fixtures" / "live1"

#: The raw captures' default places: the gitignored ``_state/`` of this
#: repository. Both are arguments; neither is ever committed.
DEFAULT_ARTICLES = REPO / "_state" / "l1-articles.html"
DEFAULT_POST_SUMMARY = REPO / "_state" / "l1-post_summary.html"

#: LinkedIn's fixed product strings these two skeletons keep, CLOSED. Each is
#: a word LinkedIn writes on every account's page, and each is one a reader in
#: ``linkedin_server`` keys on:
KEPT_WORDS: tuple[str, ...] = (
    # The articles page's one section heading (its h2), measured on the
    # session-1 capture: ``own_articles`` keys the activity section on it.
    "All activity",
    # The per-post page's demographics card title, drawn once:
    # ``post_viewer_demographics`` keys the card on it.
    "Top demographics",
    # The demographics card's FIRST tab, the one drawn ``aria-current`` on the
    # capture: the reader reports the selected tab by this word.
    "All",
    # The six demographic CATEGORY words, drawn as the card's other six tabs
    # and as each row's category: the reader's closed vocabulary. Category
    # names, never a category's value.
    "Job title",
    "Location",
    "Seniority",
    "Company",
    "Industry",
    "Company size",
)

#: A label attribute holding exactly one keyed shape, as ``skeleton_of``
#: writes it: after a space, in double quotes.
_LABEL_WRITTEN = re.compile(
    r'(?<= )(' + "|".join(sorted(LABEL_ATTRIBUTES, key=len, reverse=True)) + r')="([^"]*)"'
)


def keep_words(skeleton: str, key: bytes) -> tuple[str, dict[str, int]]:
    """Restore each :data:`KEPT_WORDS` entry where a WHOLE text node or a
    WHOLE label value is its keyed shape under ``key``. Returns the text and a
    count per word. PURE."""
    by_shape = {value_shape(word, key): word for word in KEPT_WORDS}
    if len(by_shape) != len(KEPT_WORDS):
        raise SystemExit("REFUSING: two kept words share a keyed shape under this key.")
    counts = {word: 0 for word in KEPT_WORDS}

    def label(match: "re.Match[str]") -> str:
        word = by_shape.get(match.group(2))
        if word is None:
            return match.group(0)
        counts[word] += 1
        return match.group(1) + '="' + word + '"'

    lines = []
    for line in skeleton.split("\n"):
        word = by_shape.get(line)
        if word is not None:
            counts[word] += 1
            lines.append(word)
        else:
            lines.append(_LABEL_WRITTEN.sub(label, line))
    return "\n".join(lines), counts


def build(raw_html: str, key: bytes) -> tuple[str, dict[str, int]]:
    """One raw page -> its tracked copy, and how many times each word was kept."""
    skeleton, counts = keep_words(skeleton_of(raw_html, key), key)
    copy = tracked_copy(skeleton)
    leftover = len(_KEYED_SHAPE.findall(copy))
    if leftover:
        raise SystemExit(f"REFUSING: {leftover} keyed shape(s) survived the reduction.")
    if not copy.isascii():
        raise SystemExit("REFUSING: the copy is not strict ASCII.")
    return copy, counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--articles", type=Path, default=DEFAULT_ARTICLES)
    parser.add_argument("--post-summary", type=Path, default=DEFAULT_POST_SUMMARY)
    args = parser.parse_args(argv)
    key = os.urandom(32)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, raw_path in (("articles", args.articles), ("post_summary", args.post_summary)):
        raw = raw_path.read_text(encoding="utf-8")
        copy, counts = build(raw, key)
        out = OUT_DIR / (name + ".html")
        out.write_text(copy, encoding="ascii", newline="\n")
        kept = ", ".join(f"{word!r} x{n}" for word, n in counts.items() if n)
        print(f"wrote tests/fixtures/live1/{name}.html: {len(copy)} bytes from {len(raw)} "
              f"characters; 0 keyed shapes left; kept {sum(counts.values())}: {kept or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
