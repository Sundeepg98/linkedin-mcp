"""Classify a capture's accessible names with the SHIPPED classifier. Offline.

WHY THIS EXISTS. ``scripts/_probe_messaging_menu_enumeration.py`` ships the
label classifier INTO a live page and brings back integer indices, so no
accessible name ever crosses the CDP boundary. That is the right shape for a
LIVE run and it costs a page load on a real account every time you want to ask
a question about a surface.

**This asks the same questions of a capture already on disk.** No browser, no
network, no session, no cost to anybody. The captures it reads are gitignored
-- they carry full PII -- so this script is the evidence chain: a figure
produced here can be re-derived by anyone holding any capture of the surface,
where a figure quoted in prose off a gitignored file can be checked by nobody.

IT IMPORTS ``linkedin_server.menus`` RATHER THAN MATCHING LABELS ITSELF. Four
waves in this repository reimplemented a shipped instrument on one day and
three of the copies had a bug. ``menus.classify`` already carries the
single-word rule that the ``Star Anise`` defect bought -- a one-word term must
match the WHOLE label, because a given name adds tokens -- and re-deriving that
here would be re-buying it.

WHAT MAY LEAVE. ``menus.tally`` is the one publishing function and it takes no
label as a parameter, asserted on ``inspect.signature`` in ``tests/test_menus.py``.
Its output alphabet is closed: 28 words, every one a literal defined in that
module. This script prints its output and the parse denominator, and nothing
else. **No accessible name is printed, ever**, which matters more here than on
most surfaces: on ``/messaging/`` a label IS a person's name by LinkedIn's own
design.

THE ZERO CARRIES ITS DENOMINATOR. ``matched`` beside ``items`` is the whole
point -- ``matched: 5`` out of fifty says seven-and-forty were not understood,
where a bare list of five terms reads identically whether the rest were refused
or never offered. A vocabulary zero is a fact about the vocabulary.

USAGE:

    ./venv/Scripts/python.exe scripts/_probe_labels_in_capture.py \
        --capture <path to a saved LinkedIn page>

    ./venv/Scripts/python.exe scripts/_probe_labels_in_capture.py --self-test

SHOWN FAILING: ``--self-test`` runs a planted corpus in which one label is a
two-token capitalised run (the shape of a person's name), one is a term the
vocabulary holds and one is a term it holds only as a single word inside a
longer label. It asserts each lands where it should and fails loudly otherwise.
"""

from __future__ import annotations

import argparse
import html.parser
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from linkedin_server import menus  # noqa: E402


class _LabelCollector(html.parser.HTMLParser):
    """Every ``aria-label`` in the document, in document order."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.labels: list[str] = []
        self.file_inputs = 0
        self.buttons = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]) -> None:
        pairs = dict(attrs)
        if tag == "button":
            self.buttons += 1
        if tag == "input" and pairs.get("type") == "file":
            self.file_inputs += 1
        value = pairs.get("aria-label")
        if value:
            self.labels.append(value)


def collect(text: str) -> _LabelCollector:
    collector = _LabelCollector()
    try:
        collector.feed(text)
    except Exception:  # noqa: BLE001
        pass
    return collector


def self_test() -> int:
    """SHOW THE CLASSIFIER DOING EACH OF ITS THREE THINGS."""
    planted = [
        # A term the vocabulary holds as a multi-word phrase: matched.
        ("Mark as unread", "mark_read_state"),
        # THE TWO PHRASES THIS PROBE'S FIRST RUN ADDED, both measured on a
        # capture rather than imagined. Before 2026-09-20 both were UNMATCHED
        # and the first of them was drawn eleven times on the inbox.
        ("Star conversation", "star"),
        ("Attach an image for your draft conversation", "attach"),
        # THE HISTORICAL DEFECT, kept as the control that the widening did not
        # loosen the rule it was bought with. ``star`` is a ONE-WORD term and
        # a one-word term must match the WHOLE label, so a given name that
        # merely starts with the word must not match. This classified as
        # ``star`` once, and that is why the rule exists.
        ("Star Anise", None),
        # The shape of a person's name. Must never match anything.
        ("Select conversation with Two Words", None),
    ]
    failures = 0
    for label, expected in planted:
        verdict = menus.classify(label)
        got = verdict.get("term") if verdict.get("matched") else None
        ok = got == expected
        print(
            "  %-34s expected %-18s got %-18s %s"
            % (
                "<label %d chars>" % len(label),
                expected or "(unmatched)",
                got or "(unmatched)",
                "ok" if ok else "FAIL",
            )
        )
        if not ok:
            failures += 1

    reading = menus.tally(menus.classify(lbl) for lbl, _ in planted)
    if reading["items"] != 5 or reading["matched"] != 3:
        print("  tally control FAILED: %r" % reading)
        failures += 1
    else:
        print("  tally control                      items 5, matched 3        ok")

    print()
    if failures:
        print("SELF-TEST FAILED: %d of 6" % failures)
        return 1
    print("SELF-TEST PASSED: 6 of 6")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--capture", help="path to a saved LinkedIn page")
    parser.add_argument("--self-test", action="store_true")
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
    collector = collect(text)

    if not collector.labels:
        print(
            "REFUSING TO REPORT: 0 accessible names parsed out of %d "
            "characters. That is a parse failure or a document with no "
            "labelled nodes, not a surface with no controls." % len(text)
        )
        return 3

    reading = menus.tally(menus.classify(label) for label in collector.labels)

    print("capture              %s" % path.name)
    print("characters           %d" % len(text))
    print("aria-labels parsed   %d" % reading["items"])
    print("matched              %d" % reading["matched"])
    print("buttons              %d" % collector.buttons)
    print("input[type=file]     %d" % collector.file_inputs)
    print("terms")
    for term, count in sorted(reading["terms"].items()):
        print("  %-22s %d" % (term, count))
    print("refused")
    for reason, count in sorted(reading["refused"].items()):
        print("  %-22s %d" % (reason, count))
    if reading.get("unmatched_shapes"):
        print("unmatched shapes (no text, no names)")
        for shape, count in sorted(reading["unmatched_shapes"].items()):
            print("  %-42s %d" % (shape, count))
    print()
    print(
        "A VOCABULARY ZERO IS A FACT ABOUT THE VOCABULARY. matched beside "
        "items is the denominator; the unmatched shapes are the only thing "
        "said about the rest."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
