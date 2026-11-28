"""Build session 12's three LinkedIn Learning skeletons WITH THEIR MEASURED WORDS into committed fixtures.

Kept as the PROVENANCE of ``tests/fixtures/live12/learning_words.html``,
``learning_library_words.html`` and ``learning_journey_words.html``, the
fixtures lane build28 builds its Learning readers over, 2026-11-28
(``_audit/2026-11-28-build28.md`` section 2).

THE INPUT is the gitignored KEYED skeleton the live lane wrote in session 12
(``<session dir>/<capture>.skeleton.html``, every text and attribute value a
keyed shape ``{L<letters>D<digits>n<length>:<8-hex hash>}``) and that
session's key (``<session dir>/shape.key``). Both are read, neither is
written anywhere, and nothing here prints a hash, the key or a value it read.
The committed copy ``tests/fixtures/live12/<capture>.html`` is ``tracked_copy``
of the same skeleton; this script recomputes that copy and REFUSES unless it
is identical to the committed one, so the input is shown to be the capture the
repository already holds.

WHAT IT CHANGES: LINKEDIN'S OWN WORDS, a closed list per fixture -- a course's
type label, a badge, a thumbnail's duration, a control's word, a section's
label, an address's path words. A keyed shape is replaced by a word ONLY where
``value_shape(word, key)`` equals it, as a whole text, a whole attribute value
or a whole address segment: a MEASURED word, never an assumed one. A word that
matches nowhere REFUSES the build (``scripts/_build_live11_word_skeletons.py``'s
rule, its ``build`` reused). Every list was measured first by lane build28's
scratch probe, which hashed each candidate against the skeleton and printed
only counts and places, with a random key as its negative control (0 hits on
all three captures).

Every other value is reduced exactly as ``tracked_copy`` reduces it. Third
parties' text -- a course's title, an instructor's name -- and his own -- his
career goal, his role -- stays ``x``; a test that needs one plants a synthetic
string into the slot LinkedIn drew.

    python scripts/_build_build28_word_skeletons.py --session-dir <dir> [--only NAME] [--check]

``--check`` writes nothing and exits non-zero if a committed fixture differs
from what this would write. Prints counts and a sha256 digest per fixture,
never a value it read.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import _build_live11_word_skeletons as w11  # noqa: E402  build (words, then tracked_copy)
import _probe_live_lane_session_2 as s2  # noqa: E402  tracked_copy

FIXTURES = REPO / "tests" / "fixtures" / "live12"

#: The Learning app's chrome both pages draw, measured on each: its own name
#: and the path word every one of its addresses opens with.
_CHROME: tuple[str, ...] = ("LinkedIn Learning", "learning")

#: fixture stem -> (capture stem, closed words). Every word was measured by
#: hashing it with session 12's key against the keyed skeleton (lane
#: build28's record, section 2.1).
SPEC: dict[str, tuple[str, tuple[str, ...]]] = {
    # J 152: load 23, the Learning HOME. Fifteen carousel cards, each a
    # `Course` type label and a thumbnail duration; three thumbnail badges and
    # the hero's badge, `Popular`. Each duration below matched exactly once,
    # in a card's thumbnail label.
    "learning_words": (
        "learning",
        _CHROME
        + ("Course", "Popular")
        + ("1h 9m", "1h 18m", "1h 28m", "1h 52m", "1h 53m", "2h 46m", "3h", "4h 4m",
           "27m", "40m", "45m", "47m", "50m", "55m", "59m"),
    ),
    # J 154: load 25, his library's IN-PROGRESS tab (the address asked for
    # was redirected one level deeper). The tab links' path words, the one
    # course's type label, duration, update line and controls, the authors'
    # lead word, the brand's name, and the header's two section words.
    "learning_library_words": (
        "learning_library",
        _CHROME
        + ("my-library", "in-progress", "saved", "collections", "completed")
        + ("Course", "1h 17m", "Updated Apr 2022", "Unsave", "Remove", "By:", "LinkedIn",
           "Weekly goal", "Learning history"),
    ),
    # J 156: load 24, "My Career Journey". The section labelled `Career goal`,
    # its heading `Goal` and its button `Edit goal`; the learning plan's
    # section label; the app nav's name for the page and its address word.
    "learning_journey_words": (
        "learning_journey",
        _CHROME
        + ("career-journey",)
        + ("Career goal", "Goal", "Edit goal", "Learning Plan", "My Career Journey"),
    ),
}


def header(stem: str, capture: str, words: tuple[str, ...]) -> str:
    listed = "\n".join("    " + html.escape(w, quote=False).encode("ascii", "xmlcharrefreplace").decode("ascii")
                       for w in words)
    return (
        "<!doctype html>\n<!--\n"
        "  LANE BUILD28, 2026-11-28: built by\n"
        "  scripts/_build_build28_word_skeletons.py from the live lane's SESSION-12\n"
        f"  keyed skeleton of {capture}, the same skeleton\n"
        f"  tests/fixtures/live12/{capture}.html is the tracked copy of. Identical to\n"
        "  that copy except where one of these LinkedIn words was written, each only\n"
        "  where its keyed shape matched; every other text is x, as in that copy:\n"
        f"{listed}\n"
        "-->\n"
    )


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
        copy, counts = w11.build(skeleton, key, words)
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
