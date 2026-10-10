"""Turn the live lane's session-8 capture of ONE job posting into the tracked fixture ``tests/fixtures/live8/posting.html``.

PROVENANCE of ``tests/fixtures/live8/posting.html`` (lane B4, 2026-10-10), the
fixture census rows ``J 161`` (the similar-jobs alert switch) and ``J 124``
(the posting's company insights) are built on. Lane K's ledger
(``_audit/_census/next-step.tsv``) names this path for the session-8 posting.

THE INPUT is the RAW capture the live lane kept at load 17 of live session 8
(2026-10-10 14:16, key ``lk_posting``, surface ``jobs``): gitignored, in the
live lane's own ``_state/live8/``. It holds a real employer, real people and
real figures, and it is NEVER committed. Nothing here prints any of its text:
the script prints COUNTS only.

THE METHOD is the session-2 pipeline, UNCHANGED and imported, not copied:
``_probe_live_lane_session_2.skeleton_of`` (tags, classes, roles and closed
ARIA states kept; every other text and attribute value a keyed shape; a text
or label EQUAL to a ``FURNITURE`` word kept) and then ``tracked_copy`` (every
keyed shape becomes one ``x``; an id reference keeps ``k`` and its 8-hex hash so
a label still finds its control). Four additions, made HERE only:

1. ``EXTRA_KEEP`` -- LinkedIn's own interface words on this surface that
   ``FURNITURE`` does not hold. EACH IS MEASURED: the script counts each in the
   capture's text and labels and refuses to build if any counts zero.
2. ``SYNTHETIC_LABELS`` -- two values that carry the employer's name or the
   posting's title inside LinkedIn's own words are rewritten BEFORE shaping:
   the company panel's heading (``dom.JOB_COMPANY_PANEL_PREFIX`` + the
   employer) and the alert switch's label (``dom.JOB_ALERT_HEADING_PREFIX`` +
   the title). The prefix is LinkedIn's and is kept; the rest becomes a
   declared synthetic value.
3. ``AFTER_ANCHOR`` -- the AI-written prose of the company insights (a focus
   area's title and summary under "Company focus areas", the summary under
   "Hiring & headcount") is replaced, text node by text node after its anchor,
   by declared synthetic sentences, so the fixture still draws TEXT where the
   page drew text and a reader can be shown returning it.
4. NUMBERS -- every bare number or percentage becomes a synthetic one of the
   same format (each digit replaced, in order, by 1..9 cycling), so no figure
   of the real employer survives, while "9,999"-shaped and "99%"-shaped values
   keep their shape for a reader.
5. HEADINGS -- a heading's own keyed text becomes ``SYNTHETIC_HEADING``
   rather than ``x``, so headings stay distinct from body lines as they are
   live (see the constant for the measurement that forced it).

THE KEY is a FIXED public one. ``tracked_copy`` drops every text hash; the only
hashes left are id references, which name controls and never people, and a
fixed key makes the build a fixed point (run twice, byte-identical).

    python scripts/_build_live8_posting_skeleton.py --capture <raw lk_posting.html> [--out <path>]
"""
from __future__ import annotations

import argparse
import hashlib
import html as html_escape
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import _probe_live_lane_session_2 as s2  # noqa: E402

DEFAULT_OUT = REPO / "tests" / "fixtures" / "live8" / "posting.html"

#: A fixed public key: see the module docstring.
FIXTURE_KEY = hashlib.sha256(b"lane-b4-live8-posting-fixture").digest()

#: U+2019, built so this file stays ASCII.
RSQUO = chr(0x2019)

#: LinkedIn's own words on this posting that FURNITURE does not hold. Each is
#: counted in the capture by :func:`measure` and the build refuses on a zero.
EXTRA_KEEP: tuple[str, ...] = (
    "Set alert for similar jobs",
    "Insights about the company",
    "Powered by Bing",
    "Company focus areas",
    "Hiring & headcount",
    "Total employees",
    "Company-wide",
    "2 year growth",
    "Median employee tenure:",
    "Show Premium Insights",
    "About the company",
    "Chart",
    "End of interactive chart.",
    "People you can reach out to",
    "Easy Apply",
    "Insights about this job" + RSQUO + "s applicants",
)

#: The declared synthetic values. ``Example Org`` and ``Example Job Title``
#: carry the token ``Example``, the fixtures' convention for invented text.
SYNTHETIC_EMPLOYER = "Example Org"
SYNTHETIC_TITLE = "Example Job Title"
COMPANY_PANEL_PREFIX = "Exclusive Job Seeker Insights about "
ALERT_LABEL_PREFIX = "Set alert for similar jobs as "
SYNTHETIC_LABELS: dict[str, str] = {
    COMPANY_PANEL_PREFIX: COMPANY_PANEL_PREFIX + SYNTHETIC_EMPLOYER,
    ALERT_LABEL_PREFIX: ALERT_LABEL_PREFIX + SYNTHETIC_TITLE,
}

#: The prose after an anchor, replaced in order, one text node each.
AFTER_ANCHOR: dict[str, tuple[str, ...]] = {
    "Company focus areas": (
        "Example focus area",
        "Example focus area summary: an invented sentence standing where the "
        "page drew the organisation's focus, written for this fixture.",
    ),
    "Hiring & headcount": (
        "Example hiring summary: an invented sentence standing where the page "
        "drew its account of hiring and headcount, written for this fixture.",
    ),
}

_NUMBER = re.compile(r"^[+-]?[0-9][0-9,.]*%?$")


def synthetic_number(text: str) -> str:
    """The same format, every digit replaced in order by 1..9 cycling. PURE."""
    out, n = [], 0
    for ch in text:
        if ch.isdigit():
            out.append(str(n % 9 + 1))
            n += 1
        else:
            out.append(ch)
    return "".join(out)


def _rewrite_labels(raw: str) -> tuple[str, dict[str, int]]:
    """Rewrite the two name-carrying values before shaping; count each."""
    counts: dict[str, int] = {}
    out = raw
    for prefix, synthetic in SYNTHETIC_LABELS.items():
        # In an attribute value: up to the closing quote.
        pattern_attr = re.compile(r'="' + re.escape(prefix) + r'[^"<>]*"')
        out, n_attr = pattern_attr.subn('="' + synthetic + '"', out)
        # As an element's text: up to the next tag.
        pattern_text = re.compile(r">(\s*)" + re.escape(prefix) + r"[^<]*<")
        out, n_text = pattern_text.subn(">" + r"\1" + synthetic + "<", out)
        counts[prefix.strip()] = n_attr + n_text
    return out, counts


#: What a heading's own member- or employer-written text becomes. ``tracked_copy``
#: turns every keyed text into ONE ``x``, which makes every such heading EQUAL
#: every such body line -- and a reader bounded by "the next heading" then stops
#: at the first ``x`` line, which no live page does (measured 2026-10-10: on the
#: raw capture the company panel's positional read runs to its tenure line; on
#: an all-``x`` copy it stopped five lines in). One declared synthetic heading
#: text keeps headings distinct from body lines, as they are live.
SYNTHETIC_HEADING = "Example heading"
_HEADINGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})


class PostingSkeleton(s2._Skeleton):
    """The session-2 skeleton parser, with the numbers, the anchored prose and
    distinct headings."""

    def __init__(self, key: bytes) -> None:
        super().__init__(key)
        self.queue: list[str] = []
        self.in_heading = 0
        self.counts = {"numbers": 0, "anchored prose": 0, "headings made synthetic": 0}

    def handle_starttag(self, tag, attrs) -> None:
        super().handle_starttag(tag, attrs)
        if tag in _HEADINGS and not self.dropping:
            self.in_heading += 1

    def handle_endtag(self, tag) -> None:
        super().handle_endtag(tag)
        if tag in _HEADINGS and not self.dropping:
            self.in_heading = max(0, self.in_heading - 1)

    def handle_data(self, data: str) -> None:
        if self.dropping:
            return
        text = " ".join(data.split())
        if not text:
            return
        if self.in_heading and not self.queue and text not in s2.FURNITURE and not _NUMBER.match(text):
            self.counts["headings made synthetic"] += 1
            self.out.append(html_escape.escape(SYNTHETIC_HEADING, quote=False))
            return
        if self.queue:
            shown = self.queue.pop(0)
            self.counts["anchored prose"] += 1
            self.out.append(html_escape.escape(shown, quote=False))
            return
        if text in AFTER_ANCHOR:
            self.queue = list(AFTER_ANCHOR[text])
        if _NUMBER.match(text):
            self.counts["numbers"] += 1
            self.out.append(html_escape.escape(synthetic_number(text), quote=False))
            return
        super().handle_data(data)


def measure(raw: str) -> dict[str, int]:
    """Each EXTRA_KEEP word's count in the capture's text nodes and labels."""
    text = re.sub(r"<(script|style)\b.*?</\1>", "", raw, flags=re.S | re.I)
    nodes = [" ".join(html_escape.unescape(t).split()) for t in re.split(r"<[^>]+>", text)]
    labels = [" ".join(html_escape.unescape(v).split())
              for v in re.findall(r'(?:aria-label|title|alt)="([^"]*)"', raw)]
    return {word: nodes.count(word) + labels.count(word) for word in EXTRA_KEEP}


def build(raw: str) -> tuple[str, dict[str, object]]:
    """The tracked fixture's text, and the counts printed beside it. PURE."""
    measured = measure(raw)
    missing = sorted(word for word, n in measured.items() if not n)
    if missing:
        raise SystemExit(f"refused: {len(missing)} EXTRA_KEEP word(s) not drawn in the capture")
    rewritten, label_counts = _rewrite_labels(raw)
    furniture = s2.FURNITURE
    s2.FURNITURE = frozenset(furniture | set(EXTRA_KEEP) | set(SYNTHETIC_LABELS.values()))
    try:
        parser = PostingSkeleton(FIXTURE_KEY)
        parser.feed(rewritten)
        parser.close()
    finally:
        s2.FURNITURE = furniture
    skeleton = "<!doctype html>\n" + "\n".join(parser.out)
    tracked = s2.tracked_copy(skeleton)
    counts: dict[str, object] = {
        "extra words kept": sum(measured.values()),
        "extra words (distinct)": len(measured),
        "name-carrying labels rewritten": label_counts,
        **parser.counts,
        "bytes": len(tracked),
        "sha256": hashlib.sha256(tracked.encode("ascii")).hexdigest()[:16],
    }
    return tracked, counts


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--capture", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    tracked, counts = build(args.capture.read_text(encoding="utf-8"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(tracked, encoding="ascii", newline="\n")
    for name, value in counts.items():
        print(f"{name}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
