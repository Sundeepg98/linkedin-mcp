"""Write three committed fixtures from live session 11's KEYED skeletons: the tracked copy, with LinkedIn's own fixed words put back where the keyed shape proves them.

Kept as the PROVENANCE of the three fixtures lane readers-net26 built its readers over:

    tests/fixtures/synthetic/live11_invitations_words.html       his received invitations
    tests/fixtures/synthetic/live11_invitations_sent_words.html  the invitations he sent
    tests/fixtures/synthetic/live11_ads_words.html               his Advertising data page

WHY A TRACKED COPY IS NOT ENOUGH. The live lane commits each capture as a
TRACKED copy (``_probe_live_lane_session_2.tracked_copy``): every keyed text and
attribute value one ``x``, LinkedIn's words kept only where they are on the
harness's closed ``FURNITURE`` list. ``Accept``, ``Ignore``, ``Withdraw``,
``Sent 2 weeks ago`` and the address words ``invitation-manager``, ``sent`` and
``ads-connections`` are not on it, so the tracked copies of these three pages
draw each of them as ``x`` -- and a reader aimed by LinkedIn's own words, which
is what NO-INDEX-PINNED-JUDGEMENTS asks for, cannot be shown working on them.

WHAT THIS SCRIPT DOES, AND THE ONLY THING IT DOES. It reads the session's KEYED
skeleton (``<name>.skeleton.html``) and its key (``shape.key``) -- both in the
live lane's gitignored state, on the box that took the capture -- and replaces a
keyed shape by a word ONLY when the shape EQUALS that word's keyed shape under
the session's key (``FIXED-UI-LABEL-MATCH``: a fixed product label is not
third-party text; ``scripts/verify_fixed_labels.py`` is the same method). The
words are this file's literals, :data:`WORDS`, each one of LinkedIn's interface
strings or path words; THERE IS NO ARGUMENT THAT TAKES A WORD. Everything else
is reduced by the harness's own :func:`tracked_copy`, imported and not
rewritten -- so where no word was proven the fixture IS the tracked copy.
``tests/test_live11_word_fixtures.py`` holds each fixture to its tracked copy
token by token: they differ only where the fixture holds one of these words and
the copy an ``x``.

WHAT IT CANNOT PUT BACK: a decorated label (an exact check neither matches nor
excludes it), and any word not in :data:`WORDS`. A person's name, a headline, a
newsletter's title: never, because nothing here tests one.

IT PRINTS COUNTS ONLY -- per page, how many tokens each word took -- never a
hash, the key, or any other value. Strict ASCII out.

    python scripts/_build_live11_word_fixtures.py --state <the live lane's _state/live11 directory>
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import _probe_live_lane_session_2 as harness  # noqa: E402 -- the session's own shapes

OUT = REPO / "tests" / "fixtures" / "synthetic"


def _sent_ago() -> tuple[str, ...]:
    """LinkedIn's relative time on a sent invitation, as a closed family."""
    words = ["Sent today", "Sent yesterday", "Sent 1 day ago", "Sent 1 week ago",
             "Sent 1 month ago", "Sent 1 year ago"]
    words += ["Sent %d days ago" % n for n in range(2, 32)]
    words += ["Sent %d weeks ago" % n for n in range(2, 6)]
    words += ["Sent %d months ago" % n for n in range(2, 13)]
    words += ["Sent %d years ago" % n for n in range(2, 6)]
    return tuple(words)


#: THE WORDS, per page: LinkedIn's own interface strings and address words,
#: each read on that page's keyed skeleton by keyed shape before it was listed
#: here (lane readers-net26's record, section 2). A word listed for a page and
#: drawn nowhere on it restores nothing and is printed with 0.
WORDS: dict[str, tuple[str, ...]] = {
    "invitations": (
        "Manage invitations", "Received", "Ignore", "Accept", "wants to connect",
        "invited you to subscribe to", "invitation-manager", "received", "sent",
    ),
    "invitations_sent": (
        "Manage invitations", "Received", "Withdraw", "invitation-manager", "received", "sent",
        "CONNECTION",
    ) + _sent_ago(),
    "ads": (
        "m", "categories", "account", "sign-in-and-security", "profile-visibility", "privacy",
        "ads", "interest-categories", "ads-connections", "ads-companies-followed",
        "ads-based-on-groups", "ads-education", "ads-job-information", "ads-employer",
        "ads-personalization", "ads-location", "ads-inferred-location", "ads-by-age",
        "ads-by-gender", "ads-beyond-linkedin", "ads-interactions-with-business",
        "ads-related-actions", "share-data-with-select-partners", "Profile data",
        "Activity and inferred data",
    ),
}

#: Where each fixture is written.
OUTPUTS: dict[str, Path] = {
    "invitations": OUT / "live11_invitations_words.html",
    "invitations_sent": OUT / "live11_invitations_sent_words.html",
    "ads": OUT / "live11_ads_words.html",
}


def restore(skeleton: str, key: bytes, words: tuple[str, ...]) -> tuple[str, dict[str, int]]:
    """``(fixture, {word: tokens restored})``. PURE.

    A keyed shape becomes a word only when it IS that word's shape under
    ``key``; the rest of the document is then reduced by the harness's own
    :func:`tracked_copy`. Every restored word is HTML-escaped, so it is text in
    a text node and a value inside an attribute.
    """
    table = {harness.value_shape(word, key): word for word in words}
    counts = {word: 0 for word in words}

    def ids(match: "re.Match[str]") -> str:
        # AN ID IS NEVER A WORD: every id-reference attribute takes the
        # tracked copy's own ``k`` + hash form FIRST, so nothing below can
        # restore a word into one.
        tokens = []
        for token in match.group(2).split():
            keyed = harness._KEYED_SHAPE.fullmatch(token)
            tokens.append("k" + keyed.group(4) if keyed else token)
        return match.group(1) + '="' + " ".join(tokens) + '"'

    def put_back(match: "re.Match[str]") -> str:
        word = table.get(match.group(0))
        if word is None:
            return match.group(0)
        counts[word] += 1
        return html.escape(word, quote=True)

    restored = harness._KEYED_SHAPE.sub(put_back, harness._ID_REF_WRITTEN.sub(ids, skeleton))
    return harness.tracked_copy(restored), counts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--state", required=True, type=Path,
                        help="the live lane's session-11 state directory (keyed skeletons and shape.key)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        key = bytes.fromhex((args.state / "shape.key").read_text(encoding="utf-8").strip())
    except (OSError, ValueError) as exc:
        print("refused: %s (the session key is unreadable)" % type(exc).__name__)
        return 2
    for name, words in WORDS.items():
        source = args.state / (name + ".skeleton.html")
        try:
            skeleton = source.read_text(encoding="utf-8")
        except OSError as exc:
            print("refused: %s (%s.skeleton.html is unreadable)" % (type(exc).__name__, name))
            return 2
        fixture, counts = restore(skeleton, key, words)
        fixture.encode("ascii")
        OUTPUTS[name].write_text(fixture, encoding="ascii", newline="\n")
        print("== %s: %d bytes" % (OUTPUTS[name].name, len(fixture)))
        for word in words:
            if counts[word] or not word.startswith("Sent "):
                print("   %-40s %d" % (word, counts[word]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
