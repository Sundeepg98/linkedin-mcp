"""IS A COMPANY SLUG A NAME? Ask the corpus rather than the intuition.

The ``/company/`` admission turns on one question: a group id is numeric so its
address names nobody, a search results page is a list of people so it needs a
shaper -- which of those is an organisation address?

**The answer is BOTH, and this is the instrument that says so.** It walks every
HTML document this repository has committed and reports, for each ``/company/``
path segment it finds, whether that segment is a bounded run of the ten ASCII
digits or a SLUG.

It prints the distinct segments. That is safe HERE and is not a licence
anywhere else: these are the TRACKED, SANITISED fixtures, whose every name is
already a committed literal that ``tests/test_no_committed_identity.py`` has
passed. A probe pointed at a live page or at an untracked capture MUST NOT
print a segment -- ``identifier_kind`` and ``describe_shape`` exist for that.

Opens no browser. Navigates nothing. Reads no page.

Run:  ./venv/Scripts/python.exe scripts/_probe_company_path_segments.py
"""
from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

#: Everything up to the next delimiter. Deliberately WIDER than the admitted
#: character class: a probe that only matches what the pattern admits cannot
#: discover the spellings the pattern refuses, which is half of what a
#: denominator is for.
SEGMENT = re.compile(r"/company/([^/\"'?&\\ >]{1,120})")

#: The ten, as a set, for the reason ``company_page`` names them: the same run
#: written in another script's digits is ``str.isdigit()`` True.
ASCII_DIGITS = frozenset("0123456789")

#: The class the shipped allowlist entry admits, as a set.
SLUG_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "%-_"
)


def main() -> int:
    documents = sorted((ROOT / "tests" / "fixtures").glob("**/*.html"))
    per_document: dict[str, collections.Counter] = {}
    every = collections.Counter()
    characters = 0

    for document in documents:
        text = document.read_text(encoding="utf-8", errors="replace")
        characters += len(text)
        found = collections.Counter(SEGMENT.findall(text))
        per_document[document.name] = found
        every.update(found)

    numeric = sorted(s for s in every if set(s) <= ASCII_DIGITS and s)
    slugs = sorted(s for s in every if not (set(s) <= ASCII_DIGITS and s))

    print("documents           %d" % len(documents))
    print("characters          %d" % characters)
    print("total /company/     %d" % sum(every.values()))
    print("distinct segments   %d" % len(every))
    print("  NUMERIC           %d   -- the address names nobody" % len(numeric))
    print("  SLUG              %d   -- the address CAN name somebody"
          % len(slugs))
    print("")
    print("PER DOCUMENT (documents with no hit are omitted)")
    for name, found in per_document.items():
        if found:
            print("  %-42s hits %3d  distinct %2d"
                  % (name, sum(found.values()), len(found)))
    print("")
    print("THE SLUGS, WHICH ARE THE WHOLE ARGUMENT")
    for slug in slugs:
        print("  len=%-3d in_admitted_class=%-5s  %s"
              % (len(slug), set(slug) <= SLUG_CHARS, slug))
    print("")
    print("THE NUMERIC SEGMENTS, for the denominator")
    for value in numeric:
        print("  len=%-3d %s" % (len(value), value))
    print("")
    print("THE DENOMINATOR IS THE POINT. This is what THIS CORPUS holds. A")
    print("spelling nobody ever captured is invisible here, and its absence")
    print("is a fact about the corpus and not about LinkedIn.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
