"""Write lane net7's word fixtures from live session 12's KEYED skeletons: the tracked copy, with LinkedIn's own fixed words put back where the keyed shape proves them.

Kept as the PROVENANCE of the fixtures lane net7 builds over, 2026-11-27:

    tests/fixtures/synthetic/live12_people_panel_words.html
        the people search with a keyword, All filters' panel OPEN (session 12,
        load 6; tracked copy ``tests/fixtures/live12/search_people_all_filters-open.html``)
        -- the sections ``N 82``, ``N 86``, ``N 88``, ``N 89`` rest on, and the
        panel's whole form that ``N 90`` to ``N 93`` are re-aimed by
    tests/fixtures/synthetic/live12_first_degree_panel_words.html
        his first degree's search, the same panel OPEN (load 32; tracked copy
        ``tests/fixtures/live12/search_first_all_filters-open.html``) -- ``N 26b``
    tests/fixtures/synthetic/live12_premium_matches_words.html
        his Premium networking matches (load 26; tracked copy
        ``tests/fixtures/live12/premium_matches.html``) -- ``N 199``
    tests/fixtures/synthetic/live12_invitation_pills_words.html
        his received invitations (load 28; tracked copy
        ``tests/fixtures/live12/invitation_manager.html``) -- the three filter
        pills ``N 14`` is re-aimed by

THE METHOD IS ``scripts/_build_live11_word_skeletons.py``'s, IMPORTED, NOT
REWRITTEN: its :func:`build` replaces a keyed shape by a word ONLY where the
shape EQUALS that word's keyed shape under the session's key
(``FIXED-UI-LABEL-MATCH``), REFUSES a declared word that matches nowhere, and
reduces everything else exactly as the harness's ``tracked_copy`` does. This
file refuses unless the keyed skeleton's tracked copy IS the committed one, so
the input is shown to be the capture the repository already holds.

THE WORDS ARE CLOSED: :data:`SPEC`, each one of LinkedIn's fixed words -- a
filter section's heading, an option's label, a button's words, a pill's
label with its count, a path word, an ``origin`` value -- read on the keyed
skeleton by keyed shape before it was listed (counts only; lane net7's
record, section 2). A person's name, a headline, a job title, an
organisation's name, a place -- never: nothing here tests one. No argument
takes a word.

    python scripts/_build_live12_net7_word_skeletons.py --session-dir <dir> [--check]

Prints counts and a sha256 digest prefix per fixture, never a value it read.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import _build_live11_word_skeletons as base  # noqa: E402  build(): the keyed-shape writer
import _probe_live_lane_session_2 as s2  # noqa: E402  tracked_copy

LIVE12 = REPO / "tests" / "fixtures" / "live12"
OUT = REPO / "tests" / "fixtures" / "synthetic"

#: The panel's section headings and option words both people searches draw.
_PANEL_COMMON: tuple[str, ...] = (
    "Actively hiring", "Connections", "1st", "2nd", "3rd+", "Locations",
    "Add a location", "Current companies", "Add a company", "Connections of",
    "Add a connection", "Followers of", "Add a creator", "Past companies",
    "Schools", "Add a school", "Industries", "Add an industry", "English", "Others",
    "Open to volunteering", "Service categories", "Add a service category",
    "FACETED_SEARCH",
)

#: fixture stem -> (keyed skeleton name, committed tracked copy name, words).
SPEC: dict[str, tuple[str, str, tuple[str, ...]]] = {
    # Load 6: the keyword search's panel. Its language section draws five
    # options; its Show results link carries ``origin`` FACETED_SEARCH.
    "live12_people_panel_words": (
        "search_people_all_filters-open",
        "search_people_all_filters-open",
        _PANEL_COMMON + ("French", "Portuguese", "Spanish"),
    ),
    # Load 32: his first degree's panel, ``1st`` drawn checked. Three
    # language options.
    "live12_first_degree_panel_words": (
        "search_first_all_filters-open",
        "search_first_all_filters-open",
        _PANEL_COMMON + ("German",),
    ),
    # Load 26: the two match cards' job line, ``Hiring for`` <title> ``at``
    # <organisation>; the two words between and before the strong parts.
    "live12_premium_matches_words": (
        "premium_matches",
        "premium_matches",
        ("Hiring for", "at"),
    ),
    # Load 28: the received tab -- the three pills' labels, each a word and
    # its count as drawn, the tab strip's address words and the invitations'
    # fixed words (readers-net26's on session 11, measured again here).
    "live12_invitation_pills_words": (
        "invitation_manager",
        "invitation_manager",
        ("Focused 3", "Verified 1", "Mutual Connections 1", "Manage invitations",
         "Ignore", "Accept", "wants to connect", "invited you to subscribe to",
         "invitation-manager", "received"),
    ),
}


def header(stem: str, capture: str, words: tuple[str, ...]) -> str:
    listed = "\n".join("    " + html.escape(w, quote=False) for w in words)
    return (
        "<!doctype html>\n<!--\n"
        "  LANE NET7, 2026-11-27: built by\n"
        "  scripts/_build_live12_net7_word_skeletons.py from the live lane's SESSION-12\n"
        f"  keyed skeleton of the page tests/fixtures/live12/{capture}.html is the\n"
        "  tracked copy of. Identical to that copy except where one of these LinkedIn\n"
        "  words was written, each only where its keyed shape matched; every other\n"
        "  text is x, as in that copy:\n"
        f"{listed}\n"
        "-->\n"
    )


def render(session_dir: Path, stem: str) -> tuple[str, dict[str, int], int]:
    """``(fixture text, words written per word, lines differing from the copy)``."""
    skeleton_name, capture, words = SPEC[stem]
    key = bytes.fromhex((session_dir / "shape.key").read_text(encoding="utf-8").strip())
    skeleton = (session_dir / (skeleton_name + ".skeleton.html")).read_text(encoding="utf-8")
    copy_base = s2.tracked_copy(skeleton)
    committed = (LIVE12 / (capture + ".html")).read_text(encoding="ascii")
    if committed != copy_base:
        raise SystemExit(f"{capture}: this skeleton's tracked copy is not the committed one")
    copy, counts = base.build(skeleton, key, words)
    text = header(stem, capture, words) + copy[len("<!doctype html>\n"):]
    assert all(ord(ch) < 128 for ch in text)
    changed = sum(1 for a, b in zip(copy_base.split("\n")[1:], copy.split("\n")[1:]) if a != b)
    return text, counts, changed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--session-dir", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    drift = 0
    for stem in sorted(SPEC):
        text, counts, changed = render(args.session_dir, stem)
        out = OUT / (stem + ".html")
        if args.check:
            same = out.exists() and out.read_text(encoding="ascii") == text
            drift += 0 if same else 1
            print("%-36s %s" % (stem, "matches" if same else "DIFFERS"))
            continue
        out.write_text(text, encoding="ascii", newline="\n")
        print("%s: base copy identical to the committed capture: True" % stem)
        print("  words declared %d, places written %d, lines differing %d"
              % (len(counts), sum(counts.values()), changed))
        for word, n in counts.items():
            print("    %-28s %d" % (word, n))
        print("  sha256 %s" % hashlib.sha256(text.encode("ascii")).hexdigest()[:16])
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
