"""Build session 12's four settings-page skeletons WITH THEIR MEASURED WORDS into committed fixtures, for lane settings7.

Kept as the PROVENANCE of the ``tests/fixtures/live12/*_words.html`` fixtures
lane settings7 reads its census cells over, 2026-11-27: his Data privacy
category page (census cell 28), his Verifications page (cell 46), the page his
job-seeker preferences address served (cell 73) and his Manage Premium account
page (cell 85).

THE SAME METHOD AS ``scripts/_build_live11_word_skeletons.py`` (lane
readers-jobs26), whose ``build`` this imports rather than restates: the input
is the gitignored KEYED skeleton the live lane wrote in session 12 (every text
and attribute value a keyed shape) and that session's key; both are read,
neither is written anywhere, and nothing here prints a hash, the key or a
value it read. A word is written ONLY where ``value_shape(word, key)`` equals
a keyed shape, as a whole text, a whole attribute value or one address
segment; a declared word that matches nowhere REFUSES the build. The committed
copy ``tests/fixtures/live12/<capture>.html`` is ``tracked_copy`` of the same
skeleton, and this REFUSES unless the recomputed copy is identical to it, so
the input is shown to be the capture the repository already holds.

MEASURED 2026-11-27 by hashing candidate words with session 12's key against
each keyed skeleton (lane settings7's probe, printing matched candidates and
counts only; the record, section 2). Every word below matched at least once.
NEVER WRITTEN: a member's name, his employer, the verification's three detail
lines, his purchase id, any date or amount -- nothing here tests one, so each
stays ``x`` exactly as in the tracked copy.

    python scripts/_build_live12_settings_word_skeletons.py --session-dir <dir> [--only NAME] [--check]
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

FIXTURES = REPO / "tests" / "fixtures" / "live12"

#: The settings category words every settings page's own links carry.
_CATEGORY_WORDS: tuple[str, ...] = ("categories", "account")

#: fixture stem -> (the committed capture stem, its keyed skeleton's file, its
#: closed word list). LinkedIn's own interface strings and path words only.
SPEC: dict[str, tuple[str, str, tuple[str, ...]]] = {
    # Cell 28, load 10: his Data privacy category page. The category nav's
    # path words, the five section headings, the setting links' path words and
    # every label measured. Three labels were not measured (the record,
    # section 3.1) and stay x.
    "privacy_words": (
        "privacy",
        "privacy.skeleton.html",
        _CATEGORY_WORDS + (
            "sign-in-and-security",
            "profile-visibility",
            "privacy",
            "ads",
            "m",
            "Settings",
            "How LinkedIn uses your data",
            "manage-data-and-activity",
            "download-my-data",
            "Download your data",
            "search-history",
            "Clear search history",
            "demographic-info",
            "Personal demographic info",
            "data-for-ai-improvement",
            "Who can reach you",
            "receive-invitations",
            "Invitations to connect",
            "Invitations from your network",
            "who-can-message-me",
            "research-invitations",
            "Research invitations",
            "recruiter-calls",
            "Recruiter calls",
            "Messaging experience",
            "focused-inbox",
            "Focused Inbox",
            "read-receipts",
            "suggest-replies",
            "Messaging suggestions",
            "Message nudges",
            "Job seeking preferences",
            "application-settings",
            "job-seeker",
            "Share your profile when you click Apply for a job",
            "Signal your interest to recruiters at companies you've created job alerts for",
            "Stored job applicant accounts",
            "Other applications",
            "Permitted services",
            "Microsoft Word",
        ),
    ),
    # Cell 46, load 15: his Verifications page. The Back link's path words,
    # the entry's kind, the help link's word and the email-settings link's
    # path word. The entry's three detail lines are NEVER written.
    "verifications_words": (
        "verifications",
        "verifications.skeleton.html",
        _CATEGORY_WORDS + (
            "Workplace",
            "Learn more",
            "manage-email-addresses",
        ),
    ),
    # Cell 73, load 18: what the job-seeker preferences address served. Its
    # title, the jobs rail's anchors and the job modules' heading; every job
    # card and the member it drew stay x.
    "job_prefs_words": (
        "job_prefs",
        "job_prefs.skeleton.html",
        (
            "Jobs | LinkedIn",
            "preferences",
            "SEEKING_PREFERENCES",
            "Preferences",
            "My Career Insights",
            "Post a free job",
            "search-results",
            "Jobs based on your preferences",
        ),
    ),
    # Cell 85, load 33: his Manage Premium account page. Its heading, the
    # plan's name and the three actions' words and path words; his purchase
    # id and the two description lines stay x.
    "premium_manage_account_words": (
        "premium_manage_account",
        "premium_manage_account.skeleton.html",
        _CATEGORY_WORDS + (
            "Manage Premium account",
            "Premium Career",
            "premium",
            "Switch plans",
            "manage",
            "purchases-payments",
            "purchases",
            "Manage subscription",
            "http:",
            "cancellation",
            "Cancel subscription",
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
        "  scripts/_build_live12_settings_word_skeletons.py from the live lane's\n"
        f"  SESSION-12 keyed skeleton of {capture}, the same skeleton\n"
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
