"""Build two earlier sessions' skeletons WITH THEIR MEASURED WORDS into committed fixtures: the jobs home's recent-searches card (session 2) and the recommendations feedback pair (session 8).

Kept as the PROVENANCE of ``tests/fixtures/live2/j18_words.html`` and
``tests/fixtures/live8/recommended_words.html``, the fixtures lane build-jobs2
builds census rows ``J 19`` and ``J 163`` over, 2026-11-26.

THE INPUT is the gitignored KEYED skeleton the live lane wrote in each session
(``<session dir>/<capture>.skeleton.html``, every text and attribute value a
keyed shape ``{L<letters>D<digits>n<length>:<8-hex hash>}``) and that
session's key (``<session dir>/shape.key``), each session's directory given on
the command line by its label. Both are read, neither is
written anywhere, and nothing here prints a hash, the key or a value it read.
The committed copy (``tests/fixtures/live2/j18.html``,
``tests/fixtures/live8/recommended.html``) is ``tracked_copy`` of the same
skeleton; this script recomputes that copy and REFUSES unless it is identical
to the committed one, so the input is shown to be the capture the repository
already holds.

WHAT IT CHANGES. For each fixture, a CLOSED list of LinkedIn's own interface
words (:data:`SPEC`) -- a heading, a sentence, a button's text -- never a
member's or an employer's. A keyed shape is replaced by a word ONLY where
``value_shape(word, key)`` equals it, as a whole text or a whole attribute
value: a MEASURED word, never an assumed one. A word that matches nowhere
REFUSES the build. Every other value is reduced exactly as ``tracked_copy``
reduces it. The machinery is ``scripts/_build_live11_word_skeletons.py``'s,
imported, with each fixture's own session.

    python scripts/_build_jobs2_word_skeletons.py --session live2=<dir> --session live8=<dir>
        --session live11=<dir> [--only NAME] [--check]

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

import _build_live11_word_skeletons as w11  # noqa: E402  build
import _probe_live_lane_session_2 as s2  # noqa: E402  tracked_copy

FIXTURES = REPO / "tests" / "fixtures"

#: LinkedIn's curly apostrophe, built with chr() so this file stays ASCII.
RSQUO = chr(0x2019)

#: fixture -> (session directory, skeleton stem, committed copy, closed word
#: list). Every word was measured by hashing it with its session's key against
#: the keyed skeleton (lane build-jobs2's record, sections 4 and 5).
SPEC: dict[str, tuple[str, str, str, tuple[str, ...]]] = {
    # J 19: the jobs home (session 2). The recent-searches card's heading --
    # also its list's accessible name -- and the one button beside it.
    "live2/j18_words": (
        "live2",
        "j18",
        "live2/j18",
        ("Recent job searches", "Clear"),
    ),
    # J 163: his recommended jobs (session 8). The feedback block's heading,
    # its sentence, and its two buttons' texts.
    "live8/recommended_words": (
        "live8",
        "lk_recommended",
        "live8/recommended",
        (
            "Are these results helpful?",
            "Your feedback helps us improve job recommendations.",
            "Are you finding what you" + RSQUO + "re looking for? No",
            "Are you finding what you" + RSQUO + "re looking for? Yes",
        ),
    ),
    # J 37: the jobs home's alert manager (session 11, load 17), open on load
    # outside main. Its heading; every alert's words stay x.
    "live11/jobs_alerts_manager_words": (
        "live11",
        "jobs_alerts_manager",
        "live11/jobs_alerts_manager",
        ("Manage job alerts",),
    ),
}


def header(stem: str, session: str, copy: str, words: tuple[str, ...]) -> str:
    listed = "\n".join("    " + html.escape(w, quote=False).encode("ascii", "xmlcharrefreplace").decode("ascii")
                       for w in words)
    return (
        "<!doctype html>\n<!--\n"
        "  LANE BUILD-JOBS2, 2026-11-26: built by\n"
        "  scripts/_build_jobs2_word_skeletons.py from the live lane's\n"
        f"  {session.upper()} keyed skeleton, the same skeleton\n"
        f"  tests/fixtures/{copy}.html is the tracked copy of. Identical to\n"
        "  that copy except where one of these LinkedIn words was written, each only\n"
        "  where its keyed shape matched; every other text is x, as in that copy:\n"
        f"{listed}\n"
        "-->\n"
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--session", action="append", default=[],
                        help="label=directory, once per session the SPEC names")
    parser.add_argument("--only", default="")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    sessions = dict(item.split("=", 1) for item in args.session)
    drift = 0
    for stem, (session, skeleton_stem, copy, words) in sorted(SPEC.items()):
        if args.only and stem != args.only:
            continue
        if session not in sessions:
            raise SystemExit(f"{stem}: no --session given for {session}")
        session_dir = Path(sessions[session])
        key = bytes.fromhex((session_dir / "shape.key").read_text(encoding="utf-8").strip())
        skeleton = (session_dir / (skeleton_stem + ".skeleton.html")).read_text(encoding="utf-8")
        base = s2.tracked_copy(skeleton)
        committed = FIXTURES / (copy + ".html")
        if committed.read_text(encoding="ascii") != base:
            raise SystemExit(f"{copy}: this skeleton's tracked copy is not the committed one")
        built, counts = w11.build(skeleton, key, words)
        text = header(stem, session, copy, words) + built[len("<!doctype html>\n"):]
        assert all(ord(ch) < 128 for ch in text)
        out = FIXTURES / (stem + ".html")
        if args.check:
            same = out.exists() and out.read_text(encoding="ascii") == text
            drift += 0 if same else 1
            print("%-28s %s" % (stem, "matches" if same else "DIFFERS"))
            continue
        out.write_text(text, encoding="ascii", newline="\n")
        changed = sum(1 for a, b in zip(base.split("\n")[1:], built.split("\n")[1:]) if a != b)
        print("%s: base copy identical to the committed capture: True" % stem)
        print("  words declared %d, places written %d, lines differing %d"
              % (len(words), sum(counts.values()), changed))
        print("  sha256 %s" % hashlib.sha256(text.encode("ascii")).hexdigest()[:16])
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
