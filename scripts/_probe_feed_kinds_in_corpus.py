"""Does the feed reader's ASSERTED branch structure survive real LinkedIn markup?

WHY THIS EXISTS RATHER THAN A LIVE READ. ``linkedin_server/feed.py`` shipped
with an explicit MEASURED VERSUS ASSERTED section admitting that nothing in it
had been run against real markup. Two claims in it were guesses:

  1. that a feed author control points at one of the six entity kinds
     ``shape._CENSUS_ENTITY_HREFS`` knows about;
  2. that paths carrying TWO entity segments occur -- the claim the whole
     ambiguity branch exists for, and the branch a mutation showed silently
     attributes a company's people directory TO A PERSON when removed.

A live read cannot cheaply settle either. ``page.evaluate`` and every
attribute reader are TAINT SOURCES in ``tests/test_page_text_is_never_printed``,
whose sanitiser set is DELIBERATELY EMPTY -- so anything derived from a live
page that reaches a ``print`` is refused by a shipped guard, correctly. The
sanctioned route is a reader in ``linkedin_server/`` whose return the probe
prints, and adding one contradicts ``feed.py``'s own "this module ships no DOM
reader" and moves pinned inventory counts.

THE TRACKED CORPUS IS REAL LINKEDIN MARKUP AND COSTS NOTHING. These files were
captured off his signed-in session by earlier waves. Reading them is a file
read, not a page read: no TEXT_CALL appears in this file, no browser is
attached, no page is opened, no badge is touched and no boundary is consulted
because no navigation happens.

WHAT IT CANNOT SETTLE, said before the numbers rather than after. The corpus
holds NO CAPTURE OF THE FEED ITSELF -- checked, not assumed, and the file list
is printed so the reader can see that for themselves. So this measures the
module against LinkedIn's href conventions ACROSS THE SURFACES THIS REPOSITORY
HAS CAPTURED, which is a strictly weaker claim than measuring it against the
feed. A zero here is evidence about this corpus and about nothing else; where
that matters the output says so on the line.

WHAT IT PRINTS: integers, and words drawn from ``feed.AUTHOR_KINDS`` and
``feed.REFUSALS``. NO HREF, NO PATH, NO SLUG AND NO PAGE TEXT reaches this
transcript -- the corpus is full of real identifiers and the entire point of
the module under test is that it does not publish them. The one thing printed
per file is its own repo-relative NAME, which this repository wrote.

RUN (no browser needed, and none is attached):
    ./venv/Scripts/python.exe scripts/_probe_feed_kinds_in_corpus.py
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from linkedin_server import feed  # noqa: E402

#: Every anchor destination in a captured document. Deliberately crude: this
#: probe is testing the MODULE against whatever LinkedIn actually writes, so
#: narrowing to a feed-row selector would be inventing the very structure the
#: module declines to assume.
_HREF = re.compile(r"""href=["']([^"']+)["']""")

#: The two corpus roots this repository holds, both tracked.
_CORPUS = ("tests/fixtures", "_audit")


def _documents() -> list[pathlib.Path]:
    found: list[pathlib.Path] = []
    for folder in _CORPUS:
        found.extend(sorted((ROOT / folder).glob("*.html")))
    return found


def main() -> int:
    print("=" * 72)
    print("FEED READER vs THE TRACKED CORPUS -- counts and kind words only")
    print("=" * 72)

    documents = _documents()
    print("\n0. the corpus, and what it does NOT contain")
    print("   documents read           : %d" % len(documents))
    feedish = [path for path in documents if "feed" in path.name.lower()]
    print("   named for the feed       : %d" % len(feedish))
    print("   -> so this is a claim about LinkedIn's href conventions across")
    print("      the surfaces captured here, NOT about the feed page.")

    everything: list[str] = []
    per_document: list[tuple[str, int, int]] = []
    for path in documents:
        destinations = _HREF.findall(path.read_text(encoding="utf-8", errors="replace"))
        tally = feed.feed_tally(destinations)
        per_document.append((path.name, tally["rows"], tally["identified"]))
        everything.extend(destinations)

    print("\n1. THE CONTROL -- can this instrument resolve anything at all?")
    print("   A sweep that resolves zero rows and a sweep over markup with no")
    print("   entity links are indistinguishable from the outside, and every")
    print("   number below is a claim about which happened.")
    overall = feed.feed_tally(everything)
    print("   anchors handed in        : %d" % overall["rows"])
    print("   resolved to an author    : %d" % overall["identified"])
    print("   distinct authors         : %d" % overall["distinct_authors"])
    print("   instrument resolved > 0  : %s" % (overall["identified"] > 0))

    print("\n2. BY KIND -- every word here is from feed.AUTHOR_KINDS")
    if not overall["by_kind"]:
        print("   (none resolved)")
    for kind in sorted(overall["by_kind"]):
        print("   %-12s : %d" % (kind, overall["by_kind"][kind]))
    unseen = sorted(set(feed.AUTHOR_KINDS) - set(overall["by_kind"]))
    print("   kinds NOT seen in corpus : %s" % (unseen or "none"))

    print("\n3. REFUSALS -- every word here is from feed.REFUSALS")
    for reason in sorted(overall["refused"]):
        print("   %-33s : %d" % (reason, overall["refused"][reason]))
    for reason in feed.REFUSALS:
        if reason not in overall["refused"]:
            print("   %-33s : 0" % reason)

    print("\n4. THE CLAIM THIS PROBE WAS WRITTEN FOR")
    ambiguous = overall["refused"].get("ambiguous_multiple_entity_kinds", 0)
    print("   two-entity paths found   : %d" % ambiguous)
    if ambiguous:
        print("   -> ASSERTED claim CONFIRMED against real markup. The")
        print("      ambiguity branch refuses a real shape, not an imagined")
        print("      one, and removing it attributes these to a person.")
    else:
        print("   -> NOT CONFIRMED BY THIS CORPUS, and that is not a")
        print("      refutation: no feed capture exists here, and the shape")
        print("      was asserted for the feed. The branch stays, because a")
        print("      branch removed on a corpus that could not contain its")
        print("      input is removed on no evidence at all.")

    print("\n5. CONCENTRATION, over the whole corpus")
    concentration = feed.authorship_concentration(everything)
    print("   largest single author    : %d rows" % concentration["largest_author_rows"])
    print("   concentrated             : %s" % concentration["concentrated"])

    print("\n6. PER DOCUMENT -- name, anchors, resolved")
    for name, rows, identified in per_document:
        print("   %-44s %5d %5d" % (name, rows, identified))

    print("\nNo href, path, slug or page text was printed. No page was opened.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
