"""Build tests/fixtures/synthetic/followers_list_people.html from the session-2 skeleton.

WHAT IS CARRIED, UNCHANGED: every byte of tests/fixtures/live2/followers.html
-- the live lane's session-2 capture of his own follower list, already reduced
to a skeleton (every text one ``x``, ids kept as their hash, LinkedIn's own
words kept) -- except the three things below, in each of the ten rows.

WHAT IS INVENTED, per row, in document order:

* the row's two member links (the picture link and the name link) point at a
  DECLARED synthetic slug -- ``https://www.linkedin.com/in/<slug>?miniProfileUrn=x``,
  the skeleton's own query kept;
* the name link's text is the DECLARED synthetic person that slug belongs to;
* the row's subtitle (``div.t-14.t-black.t-normal``) is an invented headline.

THE PEOPLE are the repository's declared synthetic people with their declared
slugs: the eight of ``scripts/_build_people_search_skeleton.SYNTHETIC_PEOPLE``,
then two more declared in ``tests/test_fixtures_hold_only_synthetic_people.
SYNTHETIC_PEOPLE`` whose slugs ``tests/test_no_committed_identity`` admits.
The headlines are that builder's three invented ones, in turn. Nobody here is
anybody. Every button's ``aria-label`` stays the skeleton's ``x``: its live
template was never measured, so none is invented.

IT PRINTS COUNTS ONLY. Strict ASCII in, strict ASCII out. Deterministic: the
same skeleton always builds the same fixture (tests/test_followers_list_people.py
rebuilds it in memory and compares).

    venv/Scripts/python scripts/_build_followers_people_fixture.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKELETON = REPO / "tests" / "fixtures" / "live2" / "followers.html"
OUT = REPO / "tests" / "fixtures" / "synthetic" / "followers_list_people.html"

#: Declared synthetic people and their declared slugs, in the order rows get them.
PEOPLE = (
    ("Farhan Qureshi", "farhan-qureshi-2b8e77c4"),
    ("Anita Krishnan", "anita-krishnan-9d2f4a11"),
    ("Daniel Okonkwo", "daniel-okonkwo-77bd9f02"),
    ("Lakshmi Menon", "lakshmi-menon-51ac0e39"),
    ("Sunita Rao", "sunita-rao-3ef1a6d8"),
    ("Arun Balakrishnan", "arun-balakrishnan-4c19d833"),
    ("Rohan Desai", "rohan-desai-71f2e004"),
    ("Priya Sharma", "priya-sharma-8a41b207"),
    ("Meera Iyer", "meera-iyer"),
    ("Casey Example", "casey-example-3f9a"),
)

#: Invented headlines, taken in turn (the people-search builder's three).
HEADLINES = (
    "Principal Engineer at Umbrella Systems | Distributed Systems",
    "Engineering Manager at Umbrella Systems",
    "Staff Software Engineer | Payments | Example Labs",
)

ROW_MARK = 'data-view-name="search-entity-result-universal-template"'
MEMBER_HREF = 'href="https://www.linkedin.com/in/x?miniProfileUrn=x"'
NAME_TEXT = re.compile(r'(data-test-app-aware-link="">\s*)x(\s*</a>)')
SUBTITLE_TEXT = re.compile(r'(<div class="[^"]*\bt-14 t-black t-normal">\s*)x(\s*</div>)')
COMMENT = (
    "\n<!-- EVERY PERSON HERE IS SYNTHETIC: names and slugs from the declared tables,\n"
    "     headlines invented. The STRUCTURE is the live lane's session-2 capture of\n"
    "     his follower list (tests/fixtures/live2/followers.html), kept by\n"
    "     scripts/_build_followers_people_fixture.py, which says what was kept and\n"
    "     what was replaced. -->\n"
)


def build(skeleton: str) -> str:
    """The fixture, from the skeleton's text. Raises unless every row takes
    exactly two member links, one name and one headline."""
    head, *rows = skeleton.split(ROW_MARK)
    if len(rows) != len(PEOPLE):
        raise ValueError(f"the skeleton draws {len(rows)} rows, the table holds {len(PEOPLE)}")
    built = []
    for index, row in enumerate(rows):
        name, slug = PEOPLE[index]
        headline = HEADLINES[index % len(HEADLINES)]
        href = f'href="https://www.linkedin.com/in/{slug}?miniProfileUrn=x"'
        if row.count(MEMBER_HREF) < 2:
            raise ValueError(f"row {index} draws fewer than two member links")
        row = row.replace(MEMBER_HREF, href, 2)
        row, named = NAME_TEXT.subn(rf"\g<1>{name}\g<2>", row, count=1)
        row, headed = SUBTITLE_TEXT.subn(rf"\g<1>{headline}\g<2>", row, count=1)
        if (named, headed) != (1, 1):
            raise ValueError(f"row {index}: name {named}, headline {headed}")
        built.append(row)
    out = ROW_MARK.join([head, *built])
    body = out.index("<body")
    close = out.index(">", body) + 1
    return out[:close] + COMMENT + out[close:]


def main() -> int:
    text = SKELETON.read_text(encoding="ascii")
    out = build(text)
    out.encode("ascii")
    OUT.write_text(out, encoding="ascii", newline="\n")
    print(f"rows: {len(PEOPLE)}; member links replaced: {2 * len(PEOPLE)}; "
          f"names: {len(PEOPLE)}; headlines: {len(PEOPLE)}; bytes: {len(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
