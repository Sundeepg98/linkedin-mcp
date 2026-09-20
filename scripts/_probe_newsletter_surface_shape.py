"""What does the newsletters manager actually DRAW, control by control?

``NEWSLETTER-SURFACE`` holds twelve census rows and ELEVEN OF THEM ARE STILL
GAP. Nine of the eleven are WRITES, and every write needs a control to aim at.
**A row whose control is drawn on no address this server may open is not a row
waiting for a WriteSpec; it is a row waiting for an ADDRESS, and the two are
costed differently.** This asks which of the two each row is, off the one
newsletter surface this repository has ever opened.

``scripts/_probe_newsletter_subscriptions_live.py`` opened it on 2026-09-05 and
wrote its own four questions down. It answered two of them -- the page SERVES,
and it holds five subscriptions -- and left two open, because a live probe's
job is to spend the page load and a reading of the capture is cheaper than a
second one. **This file answers the other two, and it costs nothing**: it is
OFFLINE over the gitignored capture, so no browser, no network, no page load,
and no counter of anybody's is spent.

## THE FOUR QUESTIONS, AND THE ROWS EACH ONE PRICES

**Q1 -- WHAT ADDRESSES DOES THE PAGE OFFER?** Every href in the document,
reduced to a path SHAPE, with the shipped read gate's verdict beside it. This
decides what the ledger's ``allowlist +2`` actually has to buy: a family, or
two named patterns.

**Q2 -- IS AN ANALYTICS AFFORDANCE DRAWN?** Census ``M C83`` "View newsletter
analytics" and ``P L4`` "Newsletter analytics" are the only two READS left in
this blocker. ``readonly.py``'s newsletter entry names the address it refuses
for them -- ``/newsletters/<slug>/analytics/`` -- and **nobody has measured
that LinkedIn serves it.** An admitted address is not a served one, which is
this surface's own founding lesson: ``/in/me/details/interests/`` was admitted
for this very precondition and redirects. If the page that lists his
newsletters draws no route to analytics and says the word zero times, then an
allowlist entry for that address would be a GUESS, and a guessed address is
what the entry beside it declined to be.

**Q3 -- IS A SUBSCRIBE OR UNSUBSCRIBE CONTROL DRAWN HERE?** This is the live
probe's own unanswered question 4, in its own words: an unsubscribe control
drawn here *"would take census N 56 from two blockers to one"*. Rows ``N 55``,
``N 56`` and ``M C80`` turn on it.

**Q4 -- IS AN AUTHOR-SIDE AFFORDANCE DRAWN, AND WHERE DOES IT SIT?** Five rows
(``M C50``, ``M C51``, ``M C81``, ``M C84``, ``P L3``) are about newsletters he
WRITES, and ``readonly.py`` says in as many words that whether this page lists
those is *"a question for the first live read, not an assumption for this
entry"*. **PRESENCE IS NOT ENOUGH AND THE STRUCTURE IS THE ANSWER.** A create
route in the global nav or the footer says nothing about this account; one
inside the same container as the product heading is that section's own header
action and IS an eligibility signal. So every needle is reported with its
ENCLOSING LANDMARK STACK -- tag names only, which name nobody.

## WHAT LEAVES THIS PROCESS

INTEGERS, PATH SHAPES, TAG STACKS, AND PRODUCT WORDS FROM A CLOSED
VOCABULARY. Never a newsletter title, never a slug, never a member path, never
an accessible name that is not a plain product noun.

**A NEWSLETTER TITLE AND SLUG ARE THE DANGEROUS FIELDS HERE**, measured rather
than feared: a newsletter is authored BY A PERSON and both routinely carry that
person's name (``scripts/_probe_interests_entity_shaping.py``, 2026-09-04).

Path shapes are built by SEGMENT REPLACEMENT against a CLOSED PRODUCT
VOCABULARY, which is stricter than the sibling events probe's rule and
deliberately so: that one replaces the segment after a known keyword, so a
segment somewhere it did not anticipate survives. Here ANY segment that is not
a known product word becomes ``<seg>``, so a surviving segment is impossible
rather than unlikely, and ``shape.census_substitute`` runs FIRST so the
placeholders this repository already authors are preserved as themselves.

## THE CONTROLS, BECAUSE A CHECK THAT CANNOT FAIL CERTIFIES NOTHING

**MUST FIRE, and it is a cross-instrument agreement rather than a self-check:**
the ``/newsletters/`` anchor total must equal 10, the number
``newsletters.read_newsletter_subscriptions`` measured on this same page in
this same session and wrote into its own module docstring. This parses HTML
with a regular expression; that reader walks a live DOM through Playwright.
They are different instruments, so agreement is evidence and DISAGREEMENT
VOIDS EVERY TALLY BELOW IT.

**MUST STAY SILENT:** an attribute no document carries must be found zero
times. A matcher that finds things everywhere is measuring itself.

**THE REDUCER MUST BE SHOWN CHANGING A NAME.** The whole of Q1's safety is the
claim that no free segment survives. That claim is checked against a
person-shaped newsletter slug -- the tracked synthetic one, already admitted by
this repository's identity guard -- and the run VOIDS if the reducer leaves it
alone. A redactor only ever seen passing over furniture has not been seen.

**AND ``--control`` INVERTS THE WORD CENSUS.** Q2's and Q3's findings are
ZEROS, and a zero out of a broken matcher looks identical to a zero out of a
page. ``--control`` runs the same census over a synthetic document that DOES
carry those words and requires every one of them to be named. **Without it a
zero here is not a measurement.**

## THE CAPTURE IS GITIGNORED, AND ITS ABSENCE IS NOT A ZERO

``.gitignore`` matches ``*_probe-*.html``, because a capture of this page is
made of other people's publications and must never be committable. **A LINKED
GIT WORKTREE CARRIES NO GITIGNORED FILES**, so this script run from a worktree
finds nothing and must say so rather than report an empty page. It returns
non-zero and prints nothing that could be read as a tally. ``--capture`` points
it at a checkout that has one.

Usage::

    venv/Scripts/python.exe scripts/_probe_newsletter_surface_shape.py
    venv/Scripts/python.exe scripts/_probe_newsletter_surface_shape.py --control
    venv/Scripts/python.exe scripts/_probe_newsletter_surface_shape.py \\
        --capture <path to a checkout's _audit/_probe-newsletters-hyd.html>
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedin_server import readonly, shape  # noqa: E402

#: The gitignored capture. ``.gitignore`` matches ``*_probe-*.html``.
CAPTURE = ROOT / "_audit" / "_probe-newsletters-hyd.html"

#: THE CROSS-INSTRUMENT CONTROL. ``linkedin_server/newsletters.py`` records
#: "MEASURED: ten anchors, five newsletters" off this same capture's session,
#: counted through Playwright. This file counts with a regex. Agreement is
#: evidence; disagreement voids the run.
READER_MEASURED_ANCHORS = 10

#: THE REDUCER'S MUST-CHANGE NEEDLE, TAKEN FROM THE CORPUS RATHER THAN TYPED.
#:
#: The safety claim under Q1 is that no free segment survives. Checking it
#: needs a PERSON-SHAPED slug, and a person-shaped slug pasted here would be a
#: fourth copy of a literal this tree already carries in three places -- one
#: more string for the pre-image detector to pair, and one more place for an
#: invented person to spread to. So it is READ OUT OF THE TRACKED SYNTHETIC
#: FIXTURE at run time: the control then exercises the exact string this corpus
#: holds, and it follows the fixture if the fixture ever changes.
#:
#: The fixture's own header says why that string is the right needle: it is
#: "the measurement that a plain human name survives every identity
#: substitution", which is precisely the case a path reducer must not miss.
NAME_SHAPED_FIXTURE = (
    ROOT / "tests" / "fixtures" / "synthetic" / "newsletter_subscriptions.html"
)
NAME_SHAPED_HREF = re.compile(
    r'href="(https://www\.linkedin\.com/newsletters/[^"/]+/)"'
)

#: Every href, bounded so a malformed attribute cannot swallow markup.
ANY_HREF = re.compile(r'href="([^"]{1,400})"')

#: The newsletter anchors the reader counts.
NEWSLETTER_HREF = re.compile(r'href="([^"]*/newsletters/[^"]*)"')

#: Accessible names, bounded for the same reason.
LABEL = re.compile(r'aria-label="([^"]{1,200})"')

#: The must-stay-silent control: an attribute no document carries.
IMPOSSIBLE = re.compile(r'aria-nonexistent-attribute="([^"]*)"')

#: STRUCTURE ONLY. A tag name names nobody, so a landmark stack is publishable
#: where the text inside it is not.
LANDMARK = re.compile(r"<(/?)(nav|header|footer|main|section|aside|form)[ >]",
                      re.IGNORECASE)

#: THE CLOSED PRODUCT VOCABULARY. A path segment survives only by being one of
#: these. Every word is a plain LinkedIn product noun or route word: no
#: identifier, no member, no organisation, no title.
PRODUCT_SEGMENTS = frozenset("""
about accessibility ad-choices analytics article audience brand-policy
careers checkpoint comm company content cookie-policy create creator d
dark-mode delete developer edit events feed follow followers following
form frequency groups help home in insights jobs learning legal life login
logout manage marketing-solutions me messaging mobile my-items mynetwork
network-manager new newsletter newsletters notifications oauth people posts
premium press privacy products profile-views psettings pulse
recent-activity recruiter-views sales-solutions school search
search-appearances services settings signup subscribe subscribers talent
talent-solutions unsubscribe user-agreement
""".split())

#: A PLACEHOLDER THIS REPOSITORY AUTHORS. ``shape.census_substitute`` writes
#: these, so they must survive the reducer as themselves rather than be
#: flattened into ``<seg>`` -- otherwise the output loses the one distinction
#: that says WHICH kind of entity a segment held.
PLACEHOLDER_SEGMENT = re.compile(r"^<[a-z]+>$")

#: Q2. Route needles for an analytics affordance. The first is the
#: must-fire half: ``/newsletters/`` is on this page by construction, so a
#: needle sweep reporting zero for it is broken rather than informative.
ANALYTICS_NEEDLES = (
    "/newsletters/",
    "analytics",
    "/analytics/creator/",
    "/analytics/creator/newsletters",
    "metricType",
    "impressions",
)

#: Q3. Route needles for a subscription control.
SUBSCRIPTION_NEEDLES = (
    "/newsletters/",
    "subscribe",
    "unsubscribe",
    "subscription",
    "/comm/",
    "frequency",
)

#: Q4. Route needles for an author-side affordance, each reported with the
#: landmark stack it sits in.
AUTHOR_NEEDLES = (
    "/newsletters/",
    "/article/newsletter/new",
    "/article/new",
    "/newsletters/create",
    "/newsletter/new",
    "manage",
    "/in/",
)

#: THE WORD CENSUS. Whole-word, case-insensitive, over the whole document.
#: Every one is a plain product noun; none can carry an identifier. Split into
#: the two halves the ``--control`` inversion needs: words this page is
#: EXPECTED to carry, and words whose ABSENCE is the finding.
EXPECTED_WORDS = ("newsletter", "newsletters")
FINDING_WORDS = (
    "analytics", "subscribe", "unsubscribe", "subscribed", "subscriber",
    "subscribers", "manage", "create", "edit", "delete", "settings",
    "email", "frequency", "author", "publish", "draft",
)

#: A word no page carries, so the census is shown capable of returning zero
#: for a reason other than being broken.
ABSENT_WORD = "qwxzjvnewsletterqwxzjv"

#: THE CONTROL DOCUMENT. Synthetic, written here, carrying every FINDING_WORD
#: exactly once plus one newsletter anchor. It exists so a zero measured on
#: the real capture can be distinguished from a census that cannot speak.
#: The slug is ``weekly-123456``, the literal ``scripts/_probe_newsletter_
#: routes.py`` already carries and argues for: six digits, the minimum
#: ``shape._CENSUS_LONG_DIGITS`` reduces, so it exercises the digit rule while
#: wearing no real identifier's shape.
CONTROL_HTML = (
    "<html><body><main><section><section>"
    "<h2>Newsletters</h2>"
    '<a href="https://www.linkedin.com/newsletters/weekly-123456/">x</a>'
    "<p>" + " ".join(EXPECTED_WORDS + FINDING_WORDS) + "</p>"
    "</section></section></main></body></html>"
)


def name_shaped_needle() -> str:
    """A person-shaped newsletter path, read out of the tracked fixture.

    Returns ``""`` when the fixture is missing or holds no such href, which
    the callers treat as a VOID rather than as a pass. A control that quietly
    skips is a control that cannot fail.
    """
    if not NAME_SHAPED_FIXTURE.is_file():
        return ""
    match = NAME_SHAPED_HREF.search(
        NAME_SHAPED_FIXTURE.read_text(encoding="utf-8", errors="replace")
    )
    if not match:
        return ""
    return "/" + match.group(1).split("/", 3)[3]


def path_shape(href: str) -> str:
    """The path shape of an href, by SEGMENT REPLACEMENT against a closed set.

    ``shape.census_substitute`` runs FIRST, so the placeholders this repository
    already authors survive as themselves. Then EVERY segment that is not a
    known product word and not such a placeholder becomes ``<seg>`` -- the
    inverse of an allowlist on identifiers, which is what makes a surviving
    identifier impossible rather than unlikely. Query and fragment are dropped
    and reported separately as a count, because a query is exactly where a
    filter naming a person would arrive.
    """
    shaped = shape.census_substitute(href)
    path = shaped.split("?")[0].split("#")[0]
    out = []
    for segment in path.split("/"):
        if segment == "":
            out.append("")
        elif segment.lower() in PRODUCT_SEGMENTS:
            out.append(segment.lower())
        elif PLACEHOLDER_SEGMENT.match(segment):
            out.append(segment)
        else:
            out.append("<seg>")
    return "/".join(out)


def landmarks(html: str) -> list[tuple[int, str]]:
    """Every structural landmark with its offset. Tag names only."""
    out: list[tuple[int, str]] = []
    for match in LANDMARK.finditer(html):
        out.append((match.start(),
                    ("/" if match.group(1) else "") + match.group(2).lower()))
    return out


def enclosing(marks: list[tuple[int, str]], position: int) -> str:
    """The open landmark stack at an offset -- structure, never text."""
    stack: list[str] = []
    for offset, tag in marks:
        if offset > position:
            break
        if tag.startswith("/"):
            if stack and stack[-1] == tag[1:]:
                stack.pop()
        else:
            stack.append(tag)
    return ">".join(stack) or "(root)"


def word_count(html: str, word: str) -> int:
    return len(re.findall(r"\b%s\b" % re.escape(word), html, re.IGNORECASE))


def run_word_census(html: str, label: str) -> dict[str, int]:
    print("\n=== WORD CENSUS (%s)" % label)
    tally: dict[str, int] = {}
    for word in EXPECTED_WORDS + FINDING_WORDS + (ABSENT_WORD,):
        count = word_count(html, word)
        tally[word] = count
        note = ""
        if word in EXPECTED_WORDS:
            note = "   <- must fire"
        elif word == ABSENT_WORD:
            note = "   <- must stay silent"
        print("    %5d  %s%s" % (count, word, note))
    return tally


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="the newsletters manager, "
                                                 "control by control")
    parser.add_argument("--capture", default=str(CAPTURE),
                        help="a checkout's gitignored capture of the page")
    parser.add_argument("--control", action="store_true",
                        help="invert the word census over a synthetic "
                             "document that DOES carry the finding words")
    args = parser.parse_args(argv)

    print("=== THE NEWSLETTERS MANAGER, CONTROL BY CONTROL. Offline.")

    # ------------------------------------------------------------- CONTROL
    if args.control:
        tally = run_word_census(CONTROL_HTML, "SYNTHETIC CONTROL DOCUMENT")
        missed = [w for w in FINDING_WORDS if tally.get(w, 0) == 0]
        needle = name_shaped_needle()
        if not needle:
            print("\n    NEEDLE ABSENT -- the tracked synthetic fixture is")
            print("    missing or holds no newsletter href, so the reducer")
            print("    was NOT exercised. This is a VOID, not a pass.")
            return 1
        shaped = path_shape(needle)
        reduced = shaped != needle
        print("\n    reducer over a person-shaped slug -> %s   %s"
              % (shaped, "CHANGED" if reduced else "UNCHANGED -- BROKEN"))
        ok = not missed and reduced
        if missed:
            print("    NOT NAMED by the census: %s" % ", ".join(missed))
        print("\ncontrol: %s" % ("the census can speak, and the reducer "
                                 "changes a name -- a zero on the real page "
                                 "is therefore a measurement"
                                 if ok else "BROKEN -- fix this before "
                                            "reading any zero below"))
        return 0 if ok else 1

    # ------------------------------------------------------------- CAPTURE
    capture = Path(args.capture)
    if not capture.is_file():
        print("    CAPTURE ABSENT (%s)." % capture.name)
        print("    A linked git worktree carries no gitignored files, and this")
        print("    capture is gitignored. Nothing below this line is a reading,")
        print("    and an absence is not a zero. Pass --capture.")
        return 2
    html = capture.read_text(encoding="utf-8", errors="replace")
    print("    %d chars" % len(html))

    silent = len(IMPOSSIBLE.findall(html))
    print("\n--- CONTROL, must stay silent: %d  %s"
          % (silent, "PASS" if silent == 0 else "FAIL"))
    # AND IT VOIDS, WHICH IT DID NOT IN THE FIRST DRAFT. That draft printed
    # FAIL and then printed every tally below it with exit 0 -- a check that
    # announces its own failure and certifies anyway, which is worse than not
    # having it, because the word FAIL sits four screens above a table that
    # reads as data. Found by planting a matcher that CANNOT stay silent and
    # running it; the sibling events probe has the same shape and the same
    # gap. If this matcher is finding things, it is matching something other
    # than what it was written for, and nothing it neighbours is a reading.
    if silent:
        print("    VOID. A matcher that finds an attribute no document carries")
        print("    is measuring itself, so no tally below it is a reading.")
        return 1

    anchors = [(m.start(), m.group(1)) for m in NEWSLETTER_HREF.finditer(html)]
    agree = len(anchors) == READER_MEASURED_ANCHORS
    print("--- CONTROL, must fire: %d newsletter anchors, the reader measured "
          "%d -- %s" % (len(anchors), READER_MEASURED_ANCHORS,
                        "AGREE" if agree else "DISAGREE"))
    if not agree:
        print("    VOID. This parse does not see what the reader saw, so no")
        print("    tally below it is a reading. Fix the matcher, not the page.")
        return 1

    needle = name_shaped_needle()
    if not needle:
        print("--- CONTROL, the reducer must change a name: NEEDLE ABSENT "
              "-- VOID")
        return 1
    shaped = path_shape(needle)
    if shaped == needle:
        print("--- CONTROL, the reducer must change a name: UNCHANGED -- VOID")
        return 1
    print("--- CONTROL, the reducer must change a name: %s  PASS" % shaped)

    marks = landmarks(html)
    hrefs = [m.group(1) for m in ANY_HREF.finditer(html)]

    # ---------------------------------------------------------------- Q1
    print("\n=== Q1  WHAT ADDRESSES DOES THE PAGE OFFER?")
    print("    hrefs in the document: %d, distinct: %d"
          % (len(hrefs), len(set(hrefs))))
    shapes: dict[str, int] = {}
    gate: dict[str, set[bool]] = {}
    queried = 0
    for href in hrefs:
        if "?" in href or "#" in href:
            queried += 1
        key = path_shape(href)
        shapes[key] = shapes.get(key, 0) + 1
        if href.startswith("http"):
            gate.setdefault(key, set()).add(bool(readonly.is_read_url(href)))
    for key, count in sorted(shapes.items(), key=lambda kv: (-kv[1], kv[0])):
        verdicts = gate.get(key)
        if verdicts is None:
            mark = "relative -- no gate verdict"
        elif verdicts == {True}:
            mark = "ADMITTED"
        elif verdicts == {False}:
            mark = "refused"
        else:
            mark = "MIXED -- spellings disagree"
        print("    %4d  %-46s %s" % (count, key, mark))
    print("    distinct path shapes: %d" % len(shapes))
    print("    hrefs carrying a query or fragment: %d" % queried)

    # ---------------------------------------------------------------- Q2
    print("\n=== Q2  IS AN ANALYTICS AFFORDANCE DRAWN?")
    for needle in ANALYTICS_NEEDLES:
        hits = sum(1 for href in hrefs if needle in href)
        note = "  <- must fire; a zero voids this sweep" \
            if needle == "/newsletters/" else ""
        print("    %5d  href contains %-32s%s" % (hits, needle, note))
    print("    the word 'analytics' anywhere in the document: %d"
          % word_count(html, "analytics"))

    # ---------------------------------------------------------------- Q3
    print("\n=== Q3  IS A SUBSCRIBE OR UNSUBSCRIBE CONTROL DRAWN HERE?")
    for needle in SUBSCRIPTION_NEEDLES:
        hits = sum(1 for href in hrefs if needle in href)
        note = "  <- must fire; a zero voids this sweep" \
            if needle == "/newsletters/" else ""
        print("    %5d  href contains %-32s%s" % (hits, needle, note))
    labels = LABEL.findall(html)
    print("    aria-labels in the document: %d, distinct: %d"
          % (len(labels), len(set(labels))))
    for word in ("subscribe", "unsubscribe", "subscribed", "following"):
        inlabel = sum(1 for lab in labels if word in lab.lower())
        print("    %5d  aria-label contains %s" % (inlabel, word))
    print("    <button> elements: %d" % len(re.findall(r"<button[ >]", html,
                                                       re.IGNORECASE)))
    print("    <form> elements:   %d" % len(re.findall(r"<form[ >]", html,
                                                       re.IGNORECASE)))

    # ---------------------------------------------------------------- Q4
    print("\n=== Q4  IS AN AUTHOR-SIDE AFFORDANCE DRAWN, AND WHERE?")
    print("    Presence is not the answer; the enclosing structure is. A route")
    print("    in global chrome says nothing about this account.")
    # CASE-INSENSITIVE, and it is a correction rather than a preference: the
    # word census below is case-insensitive and a case-SENSITIVE sweep here
    # reported ZERO for a word the census reported ONE for. Two numbers about
    # the same document that disagree because of a flag nobody printed is the
    # shape that gets read as drift.
    for needle in AUTHOR_NEEDLES:
        positions = [m.start()
                     for m in re.finditer(re.escape(needle), html, re.I)]
        stacks: dict[str, int] = {}
        for position in positions:
            key = enclosing(marks, position)
            stacks[key] = stacks.get(key, 0) + 1
        note = "  <- must fire" if needle == "/newsletters/" else ""
        print("    %5d  %-30s%s" % (len(positions), needle, note))
        for key, count in sorted(stacks.items()):
            print("             %4d in  %s" % (count, key))

    run_word_census(html, "THE CAPTURE")
    print("\n    A zero above is a measurement ONLY if --control passes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
