"""Build session 11's composer skeletons WITH THEIR MEASURED WORDS into committed fixtures, for lane build-msg2.

Kept as the PROVENANCE of the ``tests/fixtures/live11/*_words.html`` fixtures
lane build-msg2 builds the group post (census ``M C64``) and the scheduled
list read (``M C14``) over, 2026-11-26.

THE SAME METHOD AS ``scripts/_build_live11_word_skeletons.py`` (lane
readers-jobs26), whose ``build`` this imports rather than restates: the input
is the gitignored KEYED skeleton the live lane wrote in session 11 (every text
and attribute value a keyed shape) and that session's key; both are read,
neither is written anywhere, and nothing here prints a hash, the key or a
value it read. A word is written ONLY where ``value_shape(word, key)`` equals
a keyed shape, as a whole text or a whole attribute value; a declared word
that matches nowhere REFUSES the build. The committed copy
``tests/fixtures/live11/<capture>.html`` is ``tracked_copy`` of the same
skeleton, and this REFUSES unless the recomputed copy is identical to it, so
the input is shown to be the capture the repository already holds.

ONE DIFFERENCE, and the reason this is a file of its own: the live lane named
these skeletons by their capture keys (``sharebox_schedule-open``,
``group_composer-open``), not by the tracked copies' stems, so each entry
names its skeleton file.

MEASURED 2026-11-26 by hashing these candidate words with session 11's key
against each keyed skeleton (a probe printing matched candidate words and
counts only): the words below each matched at least once; LinkedIn's
furniture (``Back``, ``Next``, ``Cancel``, ``Dismiss``, ``More``) is kept
verbatim by the skeletons already.

    python scripts/_build_msg2_word_skeletons.py --session-dir <dir> [--only NAME] [--check]
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
#: closed word list). LinkedIn's own interface words only.
SPEC: dict[str, tuple[str, str, tuple[str, ...]]] = {
    # The feed's own composer, /preload/sharebox/ (load 25): its editor's name
    # and placeholder, the controls beside it, Schedule post and Post.
    "sharebox_words": (
        "sharebox",
        "sharebox.skeleton.html",
        (
            "Text editor for creating content",
            "What do you want to talk about?",
            "Add media",
            "Celebrate an occasion",
            "Schedule post",
            "Post",
        ),
    ),
    # Schedule post pressed (load 25): the schedule dialog's heading, its two
    # inputs' names and the control that opens the scheduled list.
    "sharebox_schedule_open_words": (
        "sharebox_schedule_open",
        "sharebox_schedule-open.skeleton.html",
        ("Schedule post", "View all scheduled posts", "Date", "Time"),
    ),
    # View all scheduled posts pressed (load 25): the list dialog's heading,
    # its empty state's headline and the one button under it.
    "sharebox_scheduled_list_open_words": (
        "sharebox_scheduled_list_open",
        "sharebox_scheduled_list-open.skeleton.html",
        ("Scheduled posts", "No scheduled posts yet", "Schedule"),
    ),
    # His member group's page (load 36), the share box closed: its trigger's
    # word and the three detours beside it.
    "group_member_words": (
        "group_member",
        "group_member_c_b5_3_4.skeleton.html",
        ("Start a public post", "Add a photo", "Add a video", "Video", "Photo", "Poll"),
    ),
    # The same page with the share box pressed open (load 36): the composer's
    # editor name, the controls beside it and Post.
    "group_composer_open_words": (
        "group_composer_open",
        "group_composer-open.skeleton.html",
        (
            "Start a public post",
            "Text editor for creating content",
            "Add media",
            "Celebrate an occasion",
            "Post",
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
        "  LANE BUILD-MSG2, 2026-11-26: built by\n"
        "  scripts/_build_msg2_word_skeletons.py from the live lane's SESSION-11\n"
        f"  keyed skeleton of {capture}, the same skeleton\n"
        f"  tests/fixtures/live11/{capture}.html is the tracked copy of. Identical to\n"
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
    for stem, (capture, skeleton_name, words) in sorted(SPEC.items()):
        if args.only and stem != args.only:
            continue
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
