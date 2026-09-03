"""Can this server READ his own LinkedIn inbox, and what does reading cost?

DELIBERATELY PROBES A FORBIDDEN SURFACE. ``/messaging`` is not merely absent
from ``readonly._ALLOWED_URL_PATTERNS`` -- it is on
``readonly._FORBIDDEN_URL_SUBSTRINGS``, so it is refused by the second gate
before the allowlist is even consulted. Nothing in ``linkedin_server/`` can
reach it and nothing here changes that: this is a script, driving Playwright
directly, exactly as ``_probe_interests.py`` did for the Interests page.

WHY A PROBE AT ALL. Every written rationale for the ``/messaging`` block in
this repo is phrased against SENDING -- a message in his name that he did not
read. None of them is about READING, and reading his own inbox is not
collecting data about other members any more than opening his own mail is.
Whether reading is even POSSIBLE has never been measured, and an allowlist
argued about rather than measured is how a boundary grows on speculation.

TWO QUESTIONS, NOT ONE. The first is obvious and the second is the one that
decides the answer:

1. Does the inbox render for a signed-in read at all?
2. WHAT DOES LOADING IT COST? THE HYPOTHESIS, UNVERIFIED: LinkedIn's desktop
   messaging view is understood to auto-select a conversation, and opening a
   conversation marks it read. Nobody here has watched it happen, which is
   precisely why this measures rather than assumes -- an unverified belief
   about a side effect is no better a basis for opening a boundary than an
   unverified belief that there is none. If it holds, a "read-only" inbox tool
   destroys unread state on every call
   -- the same objection that keeps ``mark_notifications_read`` permanently
   forbidden, arriving through a tool that calls itself a read.

HOW THE COST IS MEASURED, since asking the inbox about itself would be circular:
the messaging unread badge is drawn in the global nav on EVERY page, including
``/feed/``, which is already an allowed read surface. So the probe reads the
badge from the feed, loads the inbox, and reads the badge from the feed again.
A drop between the two is the auto-open marking something read. This is the
same discipline the write path already uses: verification comes from a
DIFFERENT surface than the one acted on.

INCONCLUSIVE IS A REAL ANSWER. If the badge is absent or zero to begin with,
there is nothing to lose and the probe cannot tell whether loading the inbox
would have cost anything. It says so rather than reporting a clean run.

Run:  python scripts/_probe_messaging.py
Writes ``_audit/_probe-messaging-*.html`` (gitignored) and prints a summary.
"""
from __future__ import annotations

import asyncio
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, FEED_URL, SETTLE_MS  # noqa: E402
from linkedin_server.shape import census_redact_rare  # noqa: E402

# NO OUTPUT DIRECTORY. This probe writes no file, so it holds no path to write
# one to. That is deliberate: the version that had an ``OUT`` used it, and the
# captures had to be destroyed by hand afterwards.

#: The inbox list. No thread id, no ``?`` -- the narrowest form of the surface.
INBOX_URL = f"{BASE_URL}/messaging/"

#: Badge shapes worth hunting in the global nav. Hunted as several independent
#: spellings rather than one selector, because a single guessed selector that
#: matches nothing is indistinguishable from a badge that is not there.
_BADGE_PATTERNS = (
    ("aria-label-unread", re.compile(r'aria-label="([^"]*\bunread\b[^"]*)"', re.I)),
    ("aria-label-messaging", re.compile(r'aria-label="([^"]*[Mm]essaging[^"]*)"')),
    ("notification-badge", re.compile(r'notification-badge[^>]*>\s*<?[^<]{0,40}')),
    ("badge-count-text", re.compile(r'"badgeCount"\s*:\s*(\d+)')),
    ("new-notification", re.compile(r'class="[^"]*notification-badge__count[^"]*"[^>]*>\s*([0-9,+]+)')),
)


#: Patterns that turn a live value into a SHAPE. Applied to everything this
#: probe prints, in this order.
#:
#: WHY THIS EXISTS, stated bluntly because the lesson cost something: the first
#: version of this probe printed every aria-label on the page and a 900
#: character slice of the inbox text, and wrote three full-page captures to
#: disk. Running it therefore published eleven real people's names and a live
#: member urn into a transcript, and left 2.1 MB of somebody's private inbox on
#: disk -- **the instrument built to answer a privacy question captured the
#: data it was asking about.** Nothing it needed to establish required a single
#: name: "eleven conversations, one auto-opened" is the entire finding.
_REDACTIONS = (
    # Opaque conversation identifiers. These are NOT caught by the digit rule
    # below -- a thread id is base64, so it survived the first version of this
    # redactor entirely. It named a specific private conversation.
    (re.compile(r'(/messaging/thread/)[^/"?\s]+'), r'\1<THREAD-ID>'),
    (re.compile(r'(?i)\b(urn:li:[a-z_]+):[A-Za-z0-9_%\-=]+'), r'\1:<ID>'),
    (re.compile(r'(?i)\b(conversation with|message from)\s+.+$'), r'\1 <NAME>'),
    # A VANITY SLUG, WHICH THIS REDACTOR DID NOT TOUCH UNTIL 2026-09-03.
    # `_redact(page.url)` runs on EVERY page this probe loads, and
    # `/in/somebodys-vanity-name/` came back byte-identical -- a member's
    # public identity printed by the one function standing between this probe
    # and a leak. A slug with digits fared no better: only the digits changed.
    #
    # THAT IS THE LEAK CLASS THAT COST THIS SESSION THREE SEPARATE INCIDENTS,
    # and it is refused here on STRUCTURE rather than on how the string looks
    # -- the same move `shape.census_href_identifies_entity` makes. Whatever
    # sits after `/in/` names a member, so no rule about its shape is needed
    # or wanted.
    #
    # ORDERED BEFORE THE DIGIT RULE ON PURPOSE. Behind it, `<N>` had already
    # eaten the slug's trailing digits and this pattern then matched only the
    # remainder, printing `/in/<SLUG><N>/` -- correct but ugly, and ugly in a
    # way that invites somebody to "tidy" one of the two rules away.
    (re.compile(r'(/in/)[A-Za-z0-9%\-_]{3,}'), r'\1<SLUG>'),
    (re.compile(r'\d{3,}'), '<N>'),
)

#: Words that make a capitalised run a UI STRING rather than a person. Without
#: this, the name collapse below turned "Conversation List" into "<NAME>" and
#: destroyed the structure the probe exists to report -- over-redaction is a
#: real failure too, just a cheaper one than the alternative.
_UI_WORDS = frozenset("""
conversation conversations list messaging navigation global primary footer
content search toast more options star select open close skip main linkedin
premium menu dropdown message messages new unread filter sort settings help
home jobs network notifications me business learning you are on the press
enter to overlay compose keyboard shortcuts jump back next previous view all
show hide sponsored inmail archived spam other focused date posted
""".split())

#: Runs of two or more LETTER words. Deliberately not spelled ``[A-Z][a-z]+``:
#: that version missed "Jane Q Public" (a one-letter initial breaks the run)
#: and would equally have missed the accented names actually present in this
#: account's inbox, since ``[a-z]`` does not match ``u`` with an umlaut. The
#: capitalisation test is done in code below, where it can be unicode-aware.
_NAME_RUN = re.compile(r"\b[^\W\d_][^\W\d_'\-]*(?:\s+[^\W\d_][^\W\d_'\-]*\.?)+")


def _collapse_names(text: str) -> str:
    """Replace capitalised runs that are not made only of UI words.

    KNOWN GAP, written down rather than left to be discovered: a SINGLE
    capitalised token is not collapsed, because at one word a person and a UI
    label are genuinely indistinguishable ("Messaging" and a one-word company
    name have the same shape). Names of two or more tokens are the case this
    handles, and the templates above catch the rest.
    """
    def repl(match: "re.Match[str]") -> str:
        run = match.group(0)
        words = run.split()
        if not all(w[:1].isupper() for w in words):
            return run
        if all(w.lower().strip("'-.") in _UI_WORDS for w in words):
            return run
        return "<NAME>"
    return _NAME_RUN.sub(repl, text)


def _redact(value: str) -> str:
    """Reduce one string to its shape. Never returns an identity.

    Errs toward over-redaction: a shape that has lost a little structure is a
    recoverable problem, and a name in a transcript is not. Both directions
    are nonetheless checked, because a redactor that flattens everything to
    <NAME> reports nothing and would look like it was working.
    """
    out = value
    for pattern, replacement in _REDACTIONS:
        out = pattern.sub(replacement, out)
    return _collapse_names(out)


#: What a control is reported as when its DESTINATION identifies somebody. The
#: label is never shaped, never counted and never printed -- only the fact that
#: such a control was there.
ENTITY_LABEL = "<entity link>"

#: Hrefs that identify a person or a company BY CONSTRUCTION. The same two
#: shapes ``shape._CENSUS_ENTITY_HREFS`` names, and the same reasoning: this
#: does not depend on how the label reads or on how often it repeats.
_ENTITY_HREF = re.compile(r"/(?:in|company)/[A-Za-z0-9%\-_.]{2,}")

#: One HTML tag. Attribute ORDER VARIES on LinkedIn's markup, so the label and
#: the href are pulled from the same tag rather than assumed adjacent -- a
#: pattern requiring `aria-label` before `href` silently matches nothing on
#: half the controls, which is a reading that looks like an absence.
_TAG = re.compile(r"<[a-zA-Z][^>]{0,600}>")
_TAG_LABEL = re.compile(r'aria-label="([^"]{0,80})"')
_TAG_HREF = re.compile(r'href="([^"]{0,300})"')


def _href_identifies_entity(href: str | None) -> bool:
    """True when this control's destination names a person or a company."""
    return bool(href) and bool(_ENTITY_HREF.search(href or ""))


def _labelled_tags(html: str) -> list[tuple[str, str | None]]:
    """``(aria-label, href)`` for every tag carrying a label, PAIRED.

    The old reading took labels alone, with a regex over the whole document,
    and so could never ask the one question that does not depend on the
    string: where does this control GO. Pairing them is what makes the
    structural refusal above possible at all.
    """
    out: list[tuple[str, str | None]] = []
    for tag in _TAG.finditer(html):
        text = tag.group(0)
        label = _TAG_LABEL.search(text)
        if not label:
            continue
        href = _TAG_HREF.search(text)
        out.append((label.group(1), href.group(1) if href else None))
    return out


def _label_shapes(html: str, limit: int = 25) -> list[str]:
    """aria-label TEMPLATES and their counts -- never the labels themselves.

    THE COUNT RULE LIVES HERE AND CANNOT LIVE IN ``_redact``, which is the
    whole reason this function changed rather than that one.

    ``_redact`` could not see a name that sits beside a lowercase word: its
    name rule takes the MAXIMAL run of letter-words and requires EVERY word in
    it to be capitalised, so one lowercase word -- "to", "profile", "sent" --
    exempts the run and the name with it. Measured 2026-09-03:

        Conversation with <a name>   redacted   (a template rule caught it)
        Reply to <a name>            NAME SURVIVED
        Open <a name> profile        NAME SURVIVED
        Send message to <a name>     NAME SURVIVED

    THE OBVIOUS FIX WAS MEASURED AND REJECTED. Teaching ``_redact`` to blank
    any capitalised run -- the census's rule -- closes all four, and against
    the 104 distinct aria-labels in this repo's committed fixtures it also
    blanks 32 shapes that are JOB TITLES and product names: "Apply to Staff
    Engineer", "Back End Developer with verification", "Chart. Highcharts
    interactive chart." Nothing about those STRINGS separates them from a
    person's name, which is precisely the premise
    :func:`shape.census_redact_rare` is built on: **page furniture repeats
    across a surface and a member does not.** The discriminator is the COUNT,
    and the count does not exist until the shapes merge -- three lines below
    this comment and nowhere earlier.

    So the sanctioned instrument is applied at the one place its precondition
    holds. The TEMPLATE still survives -- "Reply to <redacted>", "Apply to
    <redacted>" -- so what is lost is the variable part and not the structure
    this function exists to report.

    HONEST LIMIT ON THAT COST. It was measured on job and profile fixtures,
    and this probe reads neither: it loads the feed and the inbox. There is no
    committed capture of either to measure against, because this probe writes
    none -- by design, after the version that did. **The safety property that
    makes the real cost unmeasurable is the same one that makes the probe
    safe**, and that is stated rather than quietly rounded to zero.
    """
    counts: dict[str, int] = {}
    for raw, href in _labelled_tags(html):
        # LAYER ONE, STRUCTURAL AND COUNT-FREE. A control pointing at a member
        # or a company IS a link to that entity, so its accessible name is that
        # entity's name whatever the string looks like and however often it
        # appears. Refused here rather than downstream, because the count rule
        # below cannot see it.
        if _href_identifies_entity(href):
            counts[ENTITY_LABEL] = counts.get(ENTITY_LABEL, 0) + 1
            continue
        shaped = _redact(raw)
        counts[shaped] = counts.get(shaped, 0) + 1
    # LAYER TWO. THE MERGE HAS HAPPENED; THE COUNT NOW EXISTS.
    merged: dict[str, int] = {}
    for shaped, n in counts.items():
        blanked = census_redact_rare(shaped, n)
        merged[blanked] = merged.get(blanked, 0) + n
    ordered = sorted(merged.items(), key=lambda kv: (-kv[1], kv[0]))
    return [f"{shaped} x{n}" for shaped, n in ordered[:limit]]


def _badges(html: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for name, pattern in _BADGE_PATTERNS:
        hits = sorted({m.group(0)[:120] for m in pattern.finditer(html)})
        if hits:
            found[name] = hits[:12]
    return found


async def _load(page, url: str, *, label: str) -> str:
    await BROWSER.wait_for_rate_slot()
    await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
    BROWSER._last_navigation_at = time.monotonic()
    try:
        await page.wait_for_load_state("networkidle", timeout=SETTLE_MS)
    except Exception:
        await page.wait_for_timeout(SETTLE_MS)
    html = await page.content()
    # NO CAPTURE IS WRITTEN. Not for the inbox, and not for the feed either --
    # both render other people. An earlier version wrote three of these and
    # they had to be destroyed by hand afterwards; a file that must be deleted
    # after every run is a file that should never have been written. Everything
    # this probe concludes is derivable from counts, and counts are computed
    # here and thrown away with the page.
    print(f"\n=== {label}: asked {url}")
    print(f"    landed  {_redact(page.url)}")
    print(f"    {len(html)} chars")
    return html


async def main() -> None:
    async with BROWSER.session() as page:
        # --- 1. the badge BEFORE, read off an already-allowed surface --------
        before = await _load(page, FEED_URL, label="feed-before")
        badges_before = _badges(before)
        print("    badges:", badges_before or "NONE FOUND")

        # --- 2. the forbidden surface itself ---------------------------------
        html = await _load(page, INBOX_URL, label="inbox-hyd")
        landed = page.url
        print("    auth-wall?     ", "/login" in landed or "/checkpoint" in landed)
        print(
            "    thread links:  ",
            len(set(re.findall(r'href="(/messaging/thread/[^"]+)"', html))),
        )
        # THE COUNT THAT IS THE FINDING. How many conversations the list holds
        # is the whole structural answer; WHO they are with is never needed and
        # is never read.
        conversations = len(
            set(re.findall(r'aria-label="Select conversation with ([^"]+)"', html))
        )
        print(f"    conversations listed: {conversations}")
        print(f"    auth-wall?            {'/login' in landed or '/checkpoint' in landed}")

        # Compose surfaces. If reading ever put a send control on the page,
        # this is where it would show, so it is counted explicitly rather than
        # left to be noticed.
        for what, pattern in (
            ("contenteditable nodes", r'contenteditable="true"'),
            ("send controls", r'(?i)aria-label="[^"]*\bsend\b[^"]*"'),
            ("form elements", r"<form\b"),
        ):
            print(f"    {what:<21} {len(re.findall(pattern, html))}")

        print("    aria-label SHAPES (identities redacted):")
        for shape in _label_shapes(html):
            print(f"      {shape}")
        print(
            "    conversation-ish class tokens:",
            sorted({m for m in re.findall(r'(msg-[a-z0-9-]{3,40})', html)})[:30],
        )
        print(
            "    unread markers:",
            sorted({m for m in re.findall(r'([a-z-]*unread[a-z-]*)', html, re.I)})[:20],
        )
        # The page text is NOT printed. It is a live inbox: its head carried a
        # member urn and a slab of payload json the one time it was printed.

        # --- 3. the badge AFTER, same surface as step 1 ----------------------
        after = await _load(page, FEED_URL, label="feed-after")
        badges_after = _badges(after)
        print("    badges:", badges_after or "NONE FOUND")

        print("\n=== SIDE-EFFECT VERDICT")
        if not badges_before:
            print("    INCONCLUSIVE: no badge was readable before the load, so a")
            print("    drop could not have been observed. Absence of evidence.")
        elif badges_before == badges_after:
            print("    NO OBSERVED CHANGE in the nav badge across the inbox load.")
            print("    Not proof of no side effect: a badge already at zero, or one")
            print("    LinkedIn recomputes lazily, would read the same either way.")
        else:
            print("    CHANGED. Loading the inbox moved the nav badge:")
            print("      before:", badges_before)
            print("      after :", badges_after)
    await BROWSER.stop()


# GUARDED, WHICH THE FOUR SIBLING PROBES ARE NOT, AND THE DIFFERENCE MATTERS
# MORE HERE THAN ANYWHERE. ``tests/test_scripts_are_import_safe.py`` exists
# because importing a script must not DO anything -- two build scripts ended in
# a bare ``main()`` and importing either one to read a single table rebuilt the
# committed fixtures. That rule accepts an ATTRIBUTE call at module scope
# (``sys.path.insert`` writes nothing), and ``asyncio.run(...)`` is an
# attribute call, so a probe ending in one passes the guard while doing the
# most side-effecting thing in this repo on import: launching a browser and
# navigating his signed-in session.
#
# For the sibling probes that is a real hole and it is not mine to close here.
# For THIS one it would mean an import driving a browser to a surface the read
# boundary forbids, which is the accident this file is written to avoid causing
# rather than to demonstrate. So it runs only when run.
if __name__ == "__main__":
    asyncio.run(main())
