"""Does LinkedIn still DRAW an endorsement count, and a followers line?

TWO QUESTIONS, BOTH ABOUT LINES THIS REPOSITORY BELIEVES IN WITHOUT HAVING
MEASURED. Each has a committed artefact resting on it, and neither artefact
knows which of several worlds it is in.

## Q1 -- the endorsement count, on `/in/me/details/skills/`

`tests/fixtures/profile_skills.html` carries ZERO occurrences of the substring
"endorse". That is a fact about the FIXTURE and it is silent about LinkedIn,
because at least three worlds produce it:

    LINKEDIN DRAWS IT and the fixture is stale or was captured sanitised
    LINKEDIN DRAWS IT ONLY WHEN THE COUNT IS NON-ZERO and his is zero
    LINKEDIN NO LONGER DRAWS IT at all

A card count cannot separate them and neither can the shipped reader:
`dom.read_profile_detail_entries` keeps line 0 of each card as the skill name
and DISCARDS every line after it. The discarded remainder is exactly where an
endorsement count would live, so the reader that would notice it is the one
reader guaranteed not to. This probe therefore runs the raw
`dom.harvest_linked_cards` beside it and looks at every line.

**AND IT SAYS WHAT IT LOOKED AT WHEN IT FINDS NOTHING.** A zero from a page
that never drew is not a zero from a page that drew and had no such line, so
`dom.read_main_text` is read and its character count reported. That is the
same discipline `read_profile_detail_entries.observed` already keeps, for the
same reason: a zero that cannot say what it looked at has cost this repository
two wrong diagnoses.

The three worlds are STILL not fully separable by one run on one account --
"drawn only when non-zero" and "never drawn" look identical on an account with
no endorsements -- and this probe says so in its own reading rather than
picking whichever answer is convenient.

## Q2 -- the followers line, on `/in/me/`

`shape._COUNT_LINE` matches `^[\\d,]+\\+?\\s+(connections?|followers?)$` and
`shape.parse_profile_topcard` uses it ONLY to EXCLUDE such lines from the
headline and the location. Nothing reads them. The committed topcard fixtures
carry "268 connections" and NO followers line, while `linkedin_server/writes.py`
asserts in tracked prose that his profile reports 275 followers. WHICH PAGE
THAT NUMBER CAME FROM IS UNESTABLISHED. So this counts the `_COUNT_LINE`
matches on the live topcard and reports what kind each one is.

## Bounds

**BOTH ADDRESSES ARE MODULE-LEVEL CONSTANTS.** Nothing is built from a landed
url, a slug, or anything the page said.
`tests/test_navigation_is_never_derived.py` scans this file like any other, on
both of its sinks -- the navigation and the print.

**IT IS A READ.** Two allowlisted GETs, three seconds apart. Nothing pressed,
nothing typed, nothing scrolled. A page that draws its skills only after a
scroll therefore reads as a page with no cards, and the reading below says so
rather than calling it an answer.

**IT REDACTS, AND THE RULE IS NARROWER THAN IT LOOKS.** No skill name, no
company, no school, no person, no member path, no urn, no url. Line 0 of a
skill card IS the skill name and is reported as a LENGTH. Every other line off
the page goes through `_shaped`, which blanks capitalised runs.

THE ONE EXEMPTION IS A COUNT LINE. A line matching `shape._COUNT_LINE` in full
is printed verbatim -- the regex is anchored `^...$` and admits only
`<digits>[+] connections|followers`, so it cannot carry a name, and
`linkedin_server/writes.py` already commits his own follower count verbatim
into tracked source. An endorsement line gets the same narrow exemption on the
same terms, and only against `^[\\d,]+\\+?\\s+endorsements?$`. Nothing else.

Run:  venv/Scripts/python.exe scripts/_probe_endorse_and_follow_lines.py
Writes: _audit/_scratch/_probe-endorse-follow.txt (untracked local scratch),
and the same text to stdout.
"""
from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom  # noqa: E402
from linkedin_server import shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402

#: THE TWO ADDRESSES, BOTH MODULE-LEVEL STRING CONSTANTS. Neither is built
#: from anything the page said. Both are already on
#: ``readonly._ALLOWED_URL_PATTERNS``.
SELF_PROFILE_URL = f"{BASE_URL}/in/me/"
SELF_SKILLS_URL = f"{BASE_URL}/in/me/details/skills/"

#: Where the findings land. UNTRACKED LOCAL SCRATCH, created by ``main`` and
#: never at import time -- ``tests/test_scripts_are_import_safe.py`` refuses a
#: ``mkdir`` on a module-level statement, which is the rule and not an
#: obstacle.
OUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "_audit"
    / "_scratch"
    / "_probe-endorse-follow.txt"
)

#: Q1's needle, applied to every line of every card AND to the whole of
#: ``main``. Deliberately the stem rather than a word: "endorse", "endorsed",
#: "endorsement", "endorsements", "Endorsed by" all match it, so a finding
#: cannot be missed because LinkedIn chose a different inflection.
ENDORSE = re.compile(r"(?i)endors")

#: THE NARROW EXEMPTION FOR AN ENDORSEMENT COUNT, deliberately the same SHAPE
#: as ``shape._COUNT_LINE`` and anchored the same way. A line matching this
#: carries digits and one lowercase word and can hold no identity, so it is
#: printed verbatim. Anything else claiming to be an endorsement line is
#: shaped like every other line.
ENDORSE_COUNT_LINE = re.compile(r"^[\d,]+\+?\s+endorsements?$", re.I)

#: A run of capitalised tokens is a name until proven otherwise. Matched as a
#: RUN of two or more, and separately as a single token that is not the start
#: of the line -- a company, a school and a person all wear that shape and no
#: property of the string separates them from a job title, so all of them are
#: blanked. Digits and lowercase words survive, which is the whole reporting
#: vocabulary this probe needs.
#:
#: THE ACCENTED RANGE IS WRITTEN AS ESCAPE SEQUENCES so this file stays ASCII
#: while the compiled pattern still sees the real characters -- the same device
#: ``tests/test_probe_redaction.py`` uses for its non-ASCII case, and for the
#: same reason: a name spelled with accents is still a name.
_CAP_TOKEN = "[A-Z\\u00c0-\\u024f][\\w'\\u00c0-\\u024f.&-]*"
_CAP_RUN = re.compile("%s(?:\\s+%s)+" % (_CAP_TOKEN, _CAP_TOKEN))
_CAP_ONE = re.compile("(?<=\\S\\s)%s" % _CAP_TOKEN)
_CAP_ONE_ANCHORED = re.compile("^%s$" % _CAP_TOKEN)


def _path_of(url: str) -> str:
    """The path of a url and nothing else -- no host, no query."""
    return urlsplit(str(url or "")).path.rstrip("/")


def _shape_of(url: str, requested: str) -> str:
    """WHAT HAPPENED TO AN ADDRESS, never the address it became.

    Lifted deliberately from ``scripts/_probe_self_details_url.py``, which
    grew it after its FIRST run printed the operator's slug: ``/in/me/``
    redirects to ``/in/<vanity>/``, so printing the landed path publishes the
    identity. A member path IS an identity, and "paths are safe" was never the
    rule -- "these paths are safe" was.

    So this returns the RELATION between what was asked for and what came
    back, which is what both questions actually need: whether the document
    measured is the document asked for.

    The name is load-bearing. ``_SANITISERS`` in
    ``tests/test_navigation_is_never_derived.py`` lists it, which is how the
    output rule knows a print of this result carries none of its input.
    """
    landed = _path_of(url)
    asked = _path_of(requested)
    if landed == asked:
        return "SERVED AT THE REQUESTED ADDRESS (no redirect)"
    if landed.startswith("/in/") and landed.endswith(asked.split("/in/me", 1)[-1]):
        return (
            "REDIRECTED to the same resource under a member path "
            "(slug withheld -- it is an identity)"
        )
    return "REDIRECTED ELSEWHERE (%d path segments)" % len(
        [part for part in landed.split("/") if part]
    )


def _shaped(line: str) -> str:
    """A line off the page with every capitalised run replaced by ``<NAME>``.

    THE RULE IS DELIBERATELY OVER-BROAD AND THAT IS THE POINT. No property of
    a string separates a job title from a person's name, or a skill from a
    company, so this does not try: two or more consecutive capitalised tokens
    go, and so does any single capitalised token that is not the first token
    of the line. What survives is digits, punctuation and lowercase words --
    which is exactly the vocabulary needed to say "3 endorsements",
    "268 connections", or "<NAME> - <NAME>".

    A sentence-initial capital survives so that a shaped line still reads as a
    line rather than as a row of placeholders; it can carry at most one token,
    and every line reported through here is additionally length-capped.

    **EXCEPT WHEN IT IS THE WHOLE LINE**, which the smoke test caught: a card
    line reading only ``Microsoft`` is one capitalised token at a sentence
    start, so both rules above let it through -- and a one-word line has no
    sentence for it to start. A lone capitalised token IS an entity here, so it
    is blanked, and nothing is lost by it: the ``/endors/i`` tally counts the
    RAW line before any of this runs, so a lone "Endorsements" heading is still
    counted even when its text is blanked. The needle itself is spared anyway,
    because seeing its shape is the entire point of Q1 and an inflection of
    "endorse" is not an identity.
    """
    text = " ".join(str(line or "").split())
    if not text:
        return ""
    if " " not in text and _CAP_ONE_ANCHORED.match(text) and not ENDORSE.search(text):
        return "<NAME>"
    text = _CAP_RUN.sub("<NAME>", text)
    text = _CAP_ONE.sub("<NAME>", text)
    return text[:80]


def _line_report(line: str) -> str:
    """One page line, in the safest form that still answers a question.

    THREE TIERS, NARROWEST FIRST. A count line and an endorsement count line
    are printed verbatim under the exemption argued in the module docstring --
    both regexes are anchored end to end and admit only digits plus one
    lowercase word. EVERYTHING ELSE IS SHAPED, and its length is given beside
    it so a blanked line is still distinguishable from a short one.
    """
    text = " ".join(str(line or "").split())
    if shape._COUNT_LINE.match(text) or ENDORSE_COUNT_LINE.match(text):
        return "VERBATIM(count-line): %s" % ascii(text)
    return "shaped: %s  [len %d]" % (ascii(_shaped(text)), len(text))


async def _read_topcard(page, out: list[str]) -> None:
    """Q2. Count the ``_COUNT_LINE`` matches on the live topcard."""
    fields = await dom.read_profile_fields(page)
    sections = [s for s in (fields.get("sections") or []) if s]
    topcard = shape.pick_topcard(sections, fields.get("title"))
    lines = [str(one) for one in ((topcard or {}).get("lines") or [])]

    out.append("    topcard sections on the page : %d" % len(sections))
    out.append("    topcard lines               : %d" % len(lines))

    matches = [one for one in lines if shape._COUNT_LINE.match(" ".join(one.split()))]
    out.append("    lines matching _COUNT_LINE  : %d" % len(matches))
    if not matches:
        out.append("      (none -- the topcard drew no connections or followers line)")
    for index, one in enumerate(matches):
        text = " ".join(one.split())
        kind = "followers" if "follow" in text.lower() else "connections"
        out.append("      [%d] %s -> %s" % (index, kind.upper(), _line_report(text)))

    followers = [one for one in matches if "follow" in one.lower()]
    connections = [one for one in matches if "follow" not in one.lower()]
    out.append("    of those, FOLLOWERS lines   : %d" % len(followers))
    out.append("    of those, CONNECTIONS lines : %d" % len(connections))


async def _read_skills(page, out: list[str]) -> None:
    """Q1. Every line on every skill card, plus what ``main`` said."""
    entries = await dom.read_profile_detail_entries(page, section="skills")
    observed = entries.get("observed") or {}
    out.append("    read_profile_detail_entries(section='skills')")
    out.append("      count            : %s" % entries.get("count"))
    out.append("      names readable   : %d" % len(entries.get("entries") or []))
    out.append("      observed.main_chars : %s" % observed.get("main_chars"))
    if entries.get("why"):
        out.append("      why              : %s" % _shaped(str(entries["why"])))

    # THE RAW HARVEST, because the reader above keeps line 0 and DISCARDS the
    # rest -- and the discarded rest is the entire question.
    records = await dom.harvest_linked_cards(
        page,
        href_pattern=dom.SKILL_HREF,
        max_items=200,
        max_chars=300,
    )
    out.append("")
    out.append("    raw harvest_linked_cards(SKILL_HREF)")
    out.append("      cards            : %d" % len(records))

    endorse_hits = 0
    multi_line_cards = 0
    for index, record in enumerate(records):
        lines = shape.content_lines(str(record.get("text") or ""))
        if len(lines) > 1:
            multi_line_cards += 1
        # LINE 0 IS THE SKILL NAME. Its LENGTH, and nothing else.
        head = "      card %02d: %d line(s); line0 is the skill name [len %d]" % (
            index,
            len(lines),
            len(lines[0]) if lines else 0,
        )
        out.append(head)
        for offset, one in enumerate(lines[1:], start=1):
            if ENDORSE.search(one):
                endorse_hits += 1
            out.append("         line%d %s" % (offset, _line_report(one)))
        if len(lines) <= 1:
            out.append("         (no line after line 0)")

    body = await dom.read_main_text(page)
    main_hits = len(ENDORSE.findall(body))
    out.append("")
    out.append("    cards carrying more than one line : %d" % multi_line_cards)
    out.append("    card lines matching /endors/i     : %d" % endorse_hits)
    out.append("    main() character count            : %d" % len(body))
    out.append("    /endors/i occurrences in main     : %d" % main_hits)
    if main_hits:
        # WHAT IT LOOKED LIKE, SHAPED. A hit in main that no card carried is
        # the interesting case -- it would mean the count is drawn somewhere
        # this harvest does not reach.
        for one in shape.content_lines(body):
            if ENDORSE.search(one):
                out.append("      main line %s" % _line_report(one))


def _reading(out: list[str]) -> None:
    """What the numbers above can and cannot settle. Written before the run."""
    out.append("")
    out.append("=== HOW TO READ THIS")
    out.append("    Q1. A card line matching /endors/i, or a hit in main, means")
    out.append("        LINKEDIN DRAWS IT and the fixture is stale. Zero on both,")
    out.append("        on a page that DID draw cards and DID carry main text,")
    out.append("        rules out 'the fixture is stale' and leaves two worlds")
    out.append("        this account cannot separate: drawn only when non-zero,")
    out.append("        and no longer drawn at all. Zero cards with zero main")
    out.append("        characters settles NOTHING -- that is a page that never")
    out.append("        drew, and this probe does not scroll.")
    out.append("    Q2. The _COUNT_LINE tally is the answer. Zero followers lines")
    out.append("        on a topcard that DID draw a connections line means the")
    out.append("        topcard is not where a followers count lives, and the 275")
    out.append("        in writes.py came from some other page.")


async def main() -> None:
    out: list[str] = []
    out.append("=== ENDORSEMENT COUNTS AND THE FOLLOWERS LINE")
    out.append("    two questions, two allowlisted reads, nothing pressed")
    out.append("    no skill, no company, no school, no person, no url")
    out.append("    a count line is the ONE exemption and is printed verbatim")
    out.append("")

    try:
        await BROWSER.start()
    except Exception as exc:
        # A HELD PROFILE LOCK IS A RESULT, NOT A FAILURE. Other agents work in
        # this repo. Record it and stop -- no retry loop, and nothing is
        # killed.
        out.append("    BROWSER DID NOT START: %s" % type(exc).__name__)
        out.append("    Nothing was measured. If this is ProfileLockedError,")
        out.append("    another live process holds the profile; that is the")
        out.append("    cross-process lock working, not a defect.")
        _emit(out)
        return

    try:
        async with BROWSER.session() as page:
            # THE AUTH WALL FIRST, off the profile itself -- a skills page read
            # while signed out is a measurement of the login screen.
            landed = await BROWSER.goto(page, SELF_PROFILE_URL)
            if "/login" in landed or "/checkpoint" in landed:
                out.append("    AUTH WALL on /in/me/. Not signed in, so nothing")
                out.append("    was measured. Both questions stay open.")
                _emit(out)
                return

            out.append("=== Q2  THE TOPCARD, at /in/me/")
            out.append("    %s" % _shape_of(landed, SELF_PROFILE_URL))
            await _read_topcard(page, out)

            # THREE SECONDS BETWEEN THE TWO LOADS. Two GETs total.
            await asyncio.sleep(3)

            skills_landed = await BROWSER.goto(page, SELF_SKILLS_URL)
            out.append("")
            out.append("=== Q1  THE SKILLS DOCUMENT, at /in/me/details/skills/")
            out.append("    %s" % _shape_of(skills_landed, SELF_SKILLS_URL))
            if "/login" in skills_landed or "/checkpoint" in skills_landed:
                out.append("    AUTH WALL on the skills address. Q1 unmeasured.")
                _emit(out)
                return
            await _read_skills(page, out)

        _reading(out)
    except Exception as exc:
        # THE MESSAGE IS NOT PRINTED. An exception raised at the read boundary
        # interpolates the url it refused, and that is one of the three ways
        # the operator's slug reached a transcript on 2026-09-03.
        out.append("")
        out.append("    RAISED: %s (message withheld -- it can carry a url)" % (
            type(exc).__name__,
        ))
        out.append("    Whatever is above this line was measured; nothing below.")
    finally:
        await BROWSER.stop()

    _emit(out)


def _emit(out: list[str]) -> None:
    """Print the findings and put the SAME BYTES on disk.

    FOLDED TO ASCII FIRST, and both halves need it for different reasons. The
    file must be ASCII because this repository's rule says so; the print must
    be, because a Windows console on a legacy code page RAISES
    ``UnicodeEncodeError`` on a character it cannot map -- which would kill the
    run at the very moment it had the answer, and after the browser had already
    been driven. Folding once, before either sink, also guarantees the two
    carry identical bytes rather than merely similar ones.
    """
    text = "\n".join(out) + "\n"
    text = text.encode("ascii", "backslashreplace").decode("ascii")
    print(text)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(text, encoding="ascii")
    print("wrote %s" % OUT_PATH.name)


# GUARDED: importing a script must not DO anything.
# ``tests/test_scripts_are_import_safe.py`` asserts that for every script here.
if __name__ == "__main__":
    asyncio.run(main())
