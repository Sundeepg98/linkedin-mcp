"""RE-DERIVE the item-address figures from a capture of the creator analytics page.

WHY THIS IS A SCRIPT AND NOT A SENTENCE IN AN AUDIT DOCUMENT. The figures in
``linkedin_server/item_addresses.py`` were measured against a raw capture, and
a raw capture is never committed -- it carries full PII, live tracking tokens
and real member ids. A figure whose only witness is a gitignored file is a
figure nobody can check. **This script is the evidence chain**: hand it any
capture of ``/analytics/creator/content/`` and it prints the same numbers.

IT OPENS NOTHING. No browser, no network, no session. It reads one file off
disk that somebody else already captured, which is the whole point -- the
measurement it re-derives cost a page load that had already been spent.

WHAT IT MAY PRINT, AND THIS IS TIGHTER THAN THE PROBE THAT TOOK THE CAPTURE.
``scripts/_probe_creator_content_analytics.py`` refused to emit **any href**,
on the correct ground that LinkedIn urls carry member and entity identifiers.
That refusal is why the addresses on this page were captured and never read:
the instrument's own disclosure rule hid them. The answer is not to loosen the
rule but to classify INSIDE and publish a closed alphabet:

* counts, always
* the urn TYPE words (``share``, ``activity``, ...) -- letters only, no digits,
  no member token, no slug
* NEVER a urn, NEVER an href, NEVER a path segment

:func:`main` calls ``item_addresses.tally`` with ``include_identifiers``
hard-wired to False. There is no flag to turn that on, deliberately.

THE ZERO CARRIES ITS DENOMINATOR. A zero with no denominator cannot be told
apart from a file that never parsed, so this refuses to report a reading when
it found no anchors at all, and says which of the two it was.

USAGE (the capture path is yours; captures live outside the repo):

    ./venv/Scripts/python.exe scripts/_probe_item_addresses_in_capture.py \
        --capture <path to a saved /analytics/creator/content/ page>

SHOWN FAILING: ``--self-test`` runs the classifier over a planted corpus in
which one href is a profile slug, one carries both markers and one is not urn
shaped, and asserts the tally refuses each for its own reason. It fails loudly
if any of them is recognised, which is the control that makes a clean reading
on a real capture mean something.
"""

from __future__ import annotations

import argparse
import html.parser
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from linkedin_server import item_addresses  # noqa: E402


class _HrefCollector(html.parser.HTMLParser):
    """Every ``href`` attribute in the document, in document order.

    An HTML parser rather than a pattern: a pattern over 100 KB of minified
    LinkedIn markup is a second thing to be wrong about, and the standard
    library already has the parser.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]) -> None:
        for name, value in attrs:
            if name == "href" and value:
                self.hrefs.append(value)


def hrefs_in(text: str) -> list[str]:
    """Parse ``text`` as HTML and return its hrefs. Never raises."""
    collector = _HrefCollector()
    try:
        collector.feed(text)
    except Exception:  # noqa: BLE001
        # A truncated capture still yields what it parsed before the break,
        # and that is more useful than an exception -- but the caller sees
        # the count, so a short read is visible as a small denominator.
        pass
    return collector.hrefs


def urn_types(hrefs: list[str]) -> dict[str, int]:
    """How many recognised addresses carried each urn TYPE word.

    The type is the letters between the second and third colon -- ``share``,
    ``activity``. It carries no digits and identifies no post, which is why it
    is the one part of a urn this script is allowed to print.
    """
    counts: dict[str, int] = {}
    for href in hrefs:
        verdict = item_addresses.classify(href)
        if not verdict["recognised"]:
            continue
        rest = verdict["urn"][len("urn:li:"):]
        word = rest.partition(":")[0]
        counts[word] = counts.get(word, 0) + 1
    return dict(sorted(counts.items()))


def self_test() -> int:
    """SHOW THE CLASSIFIER REFUSING. Returns a process exit code."""
    planted = [
        # A section root, NOT a /in/<slug> address. A slug -- even an invented
        # one -- is a shape this repository's identity guard refuses in a
        # tracked file, and it refused an earlier draft of this line. The
        # branch under test is "no item marker", which a section root
        # exercises exactly as well.
        ("https://www.linkedin.com/jobs/", "no_item_marker"),
        ("https://www.linkedin.com/feed/update/not-a-urn/", "not_urn_shaped"),
        (
            "https://www.linkedin.com/analytics/post-summary/"
            "urn:li:activity:11/?src=/feed/update/",
            "both_markers",
        ),
        ("", "no_href"),
    ]
    failures = 0
    for href, expected in planted:
        verdict = item_addresses.classify(href)
        ok = (not verdict["recognised"]) and verdict["refused"] == expected
        print(
            "  %-14s expected %-16s got %-16s %s"
            % (
                "planted",
                expected,
                verdict.get("refused", "RECOGNISED"),
                "ok" if ok else "FAIL",
            )
        )
        if not ok:
            failures += 1

    # And the positive control: a clean address MUST be recognised, or the
    # four refusals above prove only that this classifier refuses everything.
    good = item_addresses.classify(
        "https://www.linkedin.com/feed/update/urn:li:share:11/"
    )
    ok = good["recognised"] and good["kind"] == "permalink"
    print("  %-14s expected recognised permalink       %s"
          % ("control", "ok" if ok else "FAIL"))
    if not ok:
        failures += 1

    print()
    if failures:
        print("SELF-TEST FAILED: %d of 5" % failures)
        return 1
    print("SELF-TEST PASSED: 5 of 5 (4 refusals, 1 recognition)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--capture",
        help="path to a saved /analytics/creator/content/ page",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the planted-defect control and exit",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    if not args.capture:
        parser.error("--capture is required unless --self-test is given")

    path = pathlib.Path(args.capture)
    if not path.is_file():
        print("REFUSING: no such capture: %s" % path.name)
        return 2

    text = path.read_text(encoding="utf-8", errors="replace")
    hrefs = hrefs_in(text)

    if not hrefs:
        print(
            "REFUSING TO REPORT: 0 anchors parsed out of %d characters. "
            "That is a parse failure or an empty document, not a page with "
            "no item addresses on it." % len(text)
        )
        return 3

    # include_identifiers is hard-wired False. There is no flag.
    reading = item_addresses.tally(hrefs, include_identifiers=False)

    print("capture              %s" % path.name)
    print("characters           %d" % len(text))
    print("anchors parsed       %d" % reading["hrefs_seen"])
    print("recognised           %d" % reading["recognised"])
    for kind in item_addresses.ADDRESS_KINDS:
        print(
            "  %-18s %d hrefs, %d distinct urns"
            % (kind, reading["by_kind"][kind], reading["distinct_by_kind"][kind])
        )
    print("distinct urns        %d   (NOT a post count -- see the module)"
          % reading["distinct_urns"])
    print("urn types            %s" % (urn_types(hrefs) or "{}"))
    print("refusals")
    for reason in item_addresses.REFUSALS:
        print("  %-18s %d" % (reason, reading["refused"][reason]))
    print()
    print(
        "NOTHING ABOVE IDENTIFIES A POST. distinct_urns is a count; the urn "
        "types are letters. The identifiers stayed in this process."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
