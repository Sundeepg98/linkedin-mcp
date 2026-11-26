"""Build session 11's skeletons WITH THEIR MEASURED WORDS into committed fixtures: each one the live lane's keyed skeleton, LinkedIn's own interface words written where their keyed shapes matched, and nothing else.

Kept as the PROVENANCE of the ``tests/fixtures/live11/*_words.html`` fixtures
lane readers-jobs26 builds its readers over, 2026-11-26.

THE INPUT is the gitignored KEYED skeleton the live lane wrote in session 11
(``<session dir>/<capture>.skeleton.html``, every text and attribute value a
keyed shape ``{L<letters>D<digits>n<length>:<8-hex hash>}``) and that
session's key (``<session dir>/shape.key``). Both are read, neither is written
anywhere, and nothing here prints a hash, the key or a value it read. The
committed copy ``tests/fixtures/live11/<capture>.html`` is ``tracked_copy`` of
the same skeleton; this script recomputes that copy and REFUSES unless it is
identical to the committed one, so the input is shown to be the capture the
repository already holds.

WHAT IT CHANGES. For each fixture, a CLOSED list of words (:data:`SPEC`):
LinkedIn's own interface words -- a heading, a tab's label, a switch's
accessible name -- never a member's, an employer's or a Page's own text. A
keyed shape is replaced by a word ONLY where ``value_shape(word, key)`` equals
it, as a whole text or a whole attribute value: a MEASURED word, never an
assumed one. A word that matches nowhere REFUSES the build (a declared word
must have been drawn), so a wrong key or a moved page cannot pass silently.
Every other value is reduced exactly as ``tracked_copy`` reduces it.

Where a reader needs a third party's text to be present -- an event's title,
a Page's prose -- the fixture carries the reduction (``x``) and the TEST
plants a synthetic string into the markup LinkedIn drew; nothing synthetic is
written here.

    python scripts/_build_live11_word_skeletons.py --session-dir <dir> [--only NAME] [--check]

``--check`` writes nothing and exits non-zero if a committed fixture differs
from what this would write. Prints counts and a sha256 digest per fixture,
never a value it read.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import _probe_live_lane_session_2 as s2  # noqa: E402  value_shape, tracked_copy

FIXTURES = REPO / "tests" / "fixtures" / "live11"

#: The middle dot LinkedIn separates a tracker tab from its count with. Built
#: with chr() so this file stays ASCII.
DOT = chr(0xB7)

#: fixture stem -> (the capture it is built from, its closed word list).
#: Every word was measured by hashing it with session 11's key against the
#: keyed skeleton (lane readers-jobs26's record, the section of each surface).
SPEC: dict[str, tuple[str, tuple[str, ...]]] = {
    # J 52: the job tracker's clicked_apply stage (load 12).
    "tracker_clicked_apply_words": (
        "tracker_clicked_apply",
        (
            "Job tracker",
            "0 selected",
            "Saved " + DOT + " 0",
            "Clicked apply " + DOT + " 0",
            "Applied " + DOT + " 0",
            "Interview " + DOT + " 0",
            "Date posted",
            "No matches",
        ),
    ),
}

_KEYED = re.compile(r"\{L(\d{1,7})D(\d{1,7})n(\d{1,7}):([0-9a-f]{8})\}")


def header(stem: str, capture: str, words: tuple[str, ...]) -> str:
    listed = "\n".join("    " + html.escape(w, quote=False).encode("ascii", "xmlcharrefreplace").decode("ascii")
                       for w in words)
    return (
        "<!doctype html>\n<!--\n"
        "  LANE READERS-JOBS26, 2026-11-26: built by\n"
        "  scripts/_build_live11_word_skeletons.py from the live lane's SESSION-11\n"
        f"  keyed skeleton of {capture}, the same skeleton\n"
        f"  tests/fixtures/live11/{capture}.html is the tracked copy of. Identical to\n"
        "  that copy except where one of these LinkedIn words was written, each only\n"
        "  where its keyed shape matched; every other text is x, as in that copy:\n"
        f"{listed}\n"
        "-->\n"
    )


def build(skeleton: str, key: bytes, words: tuple[str, ...]) -> tuple[str, dict[str, int]]:
    """The skeleton with each word written where its shape matched, reduced."""
    by_shape: dict[str, str] = {}
    for word in words:
        shape = s2.value_shape(" ".join(word.split()), key)
        if shape in by_shape and by_shape[shape] != word:
            raise SystemExit("two declared words share one keyed shape; refusing")
        by_shape[shape] = word
    counts = {word: 0 for word in words}

    def swap(match: "re.Match[str]") -> str:
        word = by_shape.get(match.group(0))
        if word is None:
            return match.group(0)
        counts[word] += 1
        return html.escape(word, quote=True)

    written = _KEYED.sub(swap, skeleton)
    missing = [w for w, n in counts.items() if n == 0]
    if missing:
        raise SystemExit(f"{len(missing)} declared word(s) matched no keyed shape; refusing")
    copy = s2.tracked_copy(written)
    if not copy.startswith("<!doctype html>\n"):
        raise SystemExit("the skeleton does not open with its doctype line")
    return copy, counts


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--session-dir", required=True, type=Path)
    parser.add_argument("--only", default="")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    key = bytes.fromhex((args.session_dir / "shape.key").read_text(encoding="utf-8").strip())
    drift = 0
    for stem, (capture, words) in sorted(SPEC.items()):
        if args.only and stem != args.only:
            continue
        skeleton = (args.session_dir / (capture + ".skeleton.html")).read_text(encoding="utf-8")
        base = s2.tracked_copy(skeleton)
        committed = FIXTURES / (capture + ".html")
        if committed.read_text(encoding="ascii") != base:
            raise SystemExit(f"{capture}: this skeleton's tracked copy is not the committed one")
        copy, counts = build(skeleton, key, words)
        text = header(stem, capture, words) + copy[len("<!doctype html>\n"):]
        assert all(ord(ch) < 128 for ch in text)
        out = FIXTURES / (stem + ".html")
        if args.check:
            same = out.exists() and out.read_text(encoding="ascii") == text
            drift += 0 if same else 1
            print("%-36s %s" % (stem, "matches" if same else "DIFFERS"))
            continue
        out.write_text(text, encoding="ascii", newline="\n")
        changed = sum(1 for a, b in zip(base.split("\n")[1:], copy.split("\n")[1:]) if a != b)
        print("%s: base copy identical to the committed capture: True" % stem)
        print("  words declared %d, places written %d, lines differing %d"
              % (len(words), sum(counts.values()), changed))
        print("  sha256 %s" % hashlib.sha256(text.encode("ascii")).hexdigest()[:16])
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
