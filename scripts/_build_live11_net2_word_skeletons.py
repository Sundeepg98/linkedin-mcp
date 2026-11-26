"""Write lane build-net2's word fixtures from live session 11's KEYED skeletons: the tracked copy, with LinkedIn's own fixed words put back where the keyed shape proves them.

Kept as the PROVENANCE of the fixtures lane build-net2 builds over,
2026-11-26:

    tests/fixtures/synthetic/live11_permalink_menu_words.html
        a member's post's permalink with the item's own control menu OPEN
        (session 11, load 29; tracked copy
        ``tests/fixtures/live11/permalink_member_post_menu_open.html``) --
        ``N 154``'s hide
    tests/fixtures/synthetic/live11_search_box_words.html
        the feed with its global search box's typeahead OPEN (session 11,
        load 28; tracked copy ``tests/fixtures/live11/feed_search_box_open.html``)
        -- ``N 95``'s recent searches; its one ADDRESS word, ``search-results``,
        sits inside a link, where the builder writes it like any other shape

THE METHOD IS ``scripts/_build_live11_word_skeletons.py``'s, IMPORTED, NOT
REWRITTEN: its :func:`build` replaces a keyed shape by a word ONLY where the
shape EQUALS that word's keyed shape under the session's key
(``FIXED-UI-LABEL-MATCH``), REFUSES a declared word that matches nowhere, and
reduces everything else exactly as the harness's ``tracked_copy`` does. What
this file adds is the one thing that builder cannot express: the keyed
skeleton's file name (``..._menu-open``) differs from its committed tracked
copy's (``..._menu_open``), so each entry names both. It refuses unless the
skeleton's tracked copy IS the committed one, so the input is shown to be the
capture the repository already holds.

THE WORDS ARE CLOSED: :data:`SPEC`, each one of LinkedIn's fixed words -- a
menu item, a heading, an address word -- read on the keyed skeleton by keyed
shape before it was listed (counts only; lane build-net2's record, sections 3
and 4). ``Save`` is already on the harness's ``FURNITURE`` list and survives
in the tracked copy. A person's name, the post's words, a search's keywords,
the trigger's label (it names the author) -- never: nothing here tests one.
No argument takes a word.

    python scripts/_build_live11_net2_word_skeletons.py --session-dir <dir> [--check]

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

LIVE11 = REPO / "tests" / "fixtures" / "live11"
OUT = REPO / "tests" / "fixtures" / "synthetic"

#: fixture stem -> (keyed skeleton name, committed tracked copy name, words).
SPEC: dict[str, tuple[str, str, tuple[str, ...]]] = {
    # N 154: the permalink of a member's post, its own control menu open (load
    # 29). Four of the menu's seven items, LinkedIn's fixed words; the other
    # two keyed items (23 and 15 letters) were matched by no candidate and stay x.
    "live11_permalink_menu_words": (
        "permalink_member_post_menu-open",
        "permalink_member_post_menu_open",
        ("Copy link to post", "Embed this post", "Not interested", "Report post"),
    ),
    # N 95: the feed with the global search box's typeahead open (load 28).
    # The recent jobs search's own address word -- the path segment
    # ``search-results``, which the tracked copy reduces to x -- and the
    # listbox's three fixed words: its heading, its clear-all option and the
    # suggestions' heading.
    "live11_search_box_words": (
        "feed_search_box-open",
        "feed_search_box_open",
        ("search-results", "Recent", "Clear all", "Try searching for"),
    ),
}


def header(stem: str, capture: str, words: tuple[str, ...]) -> str:
    listed = "\n".join("    " + html.escape(w, quote=False) for w in words)
    return (
        "<!doctype html>\n<!--\n"
        "  LANE BUILD-NET2, 2026-11-26: built by\n"
        "  scripts/_build_live11_net2_word_skeletons.py from the live lane's SESSION-11\n"
        f"  keyed skeleton of the page tests/fixtures/live11/{capture}.html is the\n"
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
    committed = (LIVE11 / (capture + ".html")).read_text(encoding="ascii")
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
            print("    %-24s %d" % (word, n))
        print("  sha256 %s" % hashlib.sha256(text.encode("ascii")).hexdigest()[:16])
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
