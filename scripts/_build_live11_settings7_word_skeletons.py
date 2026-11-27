"""Build session 11's Account preferences category capture WITH ITS MEASURED WORDS into a committed fixture, for lane settings7.

Kept as the PROVENANCE of ``tests/fixtures/live11/sessions_surface_words.html``,
the evidence for lane settings7's admission of his contact-syncing page
(CONTACTS-PAGE-FROM-THE-SETTINGS-NAV, the orchestrator, 2026-11-27 13:25):
the settings nav's one contacts entry, ``Sync contacts`` under ``Syncing
options``, drawn as a link to ``/mynetwork/settings/manage-syncing``.

THE CAPTURE. Session 11's load 8 asked for the settings index, ``/mypreferences/d/``,
and was redirected to his Account preferences category page; the tracked copy
is ``tests/fixtures/live11/sessions_surface.html`` (cell 10's capture, the
sessions surface). Its keyed skeleton and session 11's key are preserved,
gitignored, in the main checkout's ``_state/preserved/live11-2026-11-25/``.

THE SAME METHOD AS ``scripts/_build_live11_word_skeletons.py`` (lane
readers-jobs26), whose ``build`` this imports rather than restates: a word is
written ONLY where ``value_shape(word, key)`` equals a keyed shape, as a whole
text, a whole attribute value or one address segment; a declared word that
matches nowhere REFUSES the build; the recomputed tracked copy must be
byte-identical to the committed one, or this refuses. Nothing here prints a
hash, the key or a value it read.

MEASURED 2026-11-27 by hashing candidate words with session 11's key against
the keyed skeleton (lane settings7's probe, matched candidates and counts
only). Every word below matched at least once. NEVER WRITTEN: any value his
profile-information entries draw, and the Microsoft entry's second line (it
carries a digit); nothing here tests one, so each stays ``x``.

    python scripts/_build_live11_settings7_word_skeletons.py --session-dir <dir> [--check]
"""
from __future__ import annotations

import argparse
import hashlib
import html
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import _build_live11_word_skeletons as words_builder  # noqa: E402  build()
import _probe_live_lane_session_2 as s2  # noqa: E402  tracked_copy

FIXTURES = REPO / "tests" / "fixtures" / "live11"

#: fixture stem -> (the committed capture stem, its keyed skeleton's file, its
#: closed word list). LinkedIn's own interface strings and path words only.
SPEC: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "sessions_surface_words": (
        "sessions_surface",
        "sessions_surface.skeleton.html",
        (
            # the category nav
            "categories", "account", "sign-in-and-security", "profile-visibility",
            "privacy", "ads", "m", "Settings",
            # its sections, headings and setting links
            "Profile information", "demographic-info-copy",
            "Display", "dark-mode",
            "General preferences", "language", "language-for-translation",
            "autoplay-videos", "enable-sounds-desktop", "show-profile-photos",
            "preferred-view", "unfollowed",
            "Syncing options", "Sync contacts", "manage-syncing",
            "premium-manage-account",
            "Partners & services", "Microsoft", "connected-microsoft-accounts",
            "Account management", "hibernate-account", "close-accounts",
        ),
    ),
}


def header(stem: str, capture: str, words: tuple[str, ...]) -> str:
    listed = "\n".join(
        "    " + html.escape(w, quote=False).encode("ascii", "xmlcharrefreplace").decode("ascii")
        for w in words
    )
    return (
        "<!doctype html>\n<!--\n"
        "  LANE SETTINGS7, 2026-11-27: built by\n"
        "  scripts/_build_live11_settings7_word_skeletons.py from the live lane's\n"
        f"  SESSION-11 keyed skeleton of {capture}, the same skeleton\n"
        f"  tests/fixtures/live11/{capture}.html is the tracked copy of. Identical to\n"
        "  that copy except where one of these LinkedIn words was written, each only\n"
        "  where its keyed shape matched; every other text is x, as in that copy:\n"
        f"{listed}\n"
        "-->\n"
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--session-dir", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    key = bytes.fromhex((args.session_dir / "shape.key").read_text(encoding="utf-8").strip())
    drift = 0
    for stem, (capture, skeleton_name, words) in sorted(SPEC.items()):
        skeleton = (args.session_dir / skeleton_name).read_text(encoding="utf-8")
        base = s2.tracked_copy(skeleton)
        committed = FIXTURES / (capture + ".html")
        if committed.read_text(encoding="ascii") != base:
            raise SystemExit(f"{capture}: this skeleton's tracked copy is not the committed one")
        copy, counts = words_builder.build(skeleton, key, words)
        text = header(stem, capture, words) + copy[len("<!doctype html>\n"):]
        if not all(ord(ch) < 128 for ch in text):
            raise SystemExit(f"{stem}: the fixture would not be ASCII; refusing")
        out = FIXTURES / (stem + ".html")
        if args.check:
            same = out.exists() and out.read_text(encoding="ascii") == text
            drift += 0 if same else 1
            print("%-40s %s" % (stem, "matches" if same else "DIFFERS"))
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
