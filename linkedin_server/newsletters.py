"""The newsletters he subscribes to, read off a page that has now been opened.

WHY THIS EXISTS AND WHY IT DID NOT EXIST YESTERDAY. Its predecessor wave
shipped the shape layer (:func:`shape.subscription_row`) and the address
(``readonly._ALLOWED_URL_PATTERNS``) and DELIBERATELY SHIPPED NO READER, on the
argument that an aim written against a page nobody has opened fails CLOSED and
answers *he subscribes to nothing* -- the exact reading this surface was opened
to produce. That argument was correct and it does not survive a capture. Every
selector, offset and count below is a measurement taken off the live page on
2026-09-05 at 16:19 IST and kept at ``_audit/_probe-newsletters-hyd.html``
(gitignored: that capture is made of other people's publications).

WHY IT IS A MODULE AND NOT A BLOCK IN ``dom.py``, STATED PLAINLY RATHER THAN
DRESSED UP. ``dom.py`` held 317 uncommitted lines from another wave at the
moment this was written, and ``git commit --only`` does not protect a
neighbour's LINES inside a path you name -- measured in this tree three times
this week. A file with one writer can be committed in seconds; a shared 460 KB
module cannot. The package already carries focused modules of this size
(``uploads.py``, ``paths.py``, ``preflight.py``), so this is not a new shape --
but the reason it was taken NOW is the tree, and a later reader deserves the
real one.

## WHAT MAY BE SAID ABOUT THIS SURFACE IS NARROWER THAN ANYWHERE ELSE

**THE BOUNDARY DECIDES WHAT MAY BE OPENED; THE SHAPER DECIDES WHAT MAY BE
SAID.** This module opens nothing -- it reads a document it is handed -- and it
says as little as the question allows. A newsletter is authored BY A PERSON and
both its title and its slug routinely carry that person's name, measured on
2026-09-04 by ``scripts/_probe_interests_entity_shaping.py``. So every row
leaves through :func:`shape.subscription_row`, which redacts the title
unconditionally and publishes a constant href shape. The raw strings exist only
inside :func:`read_newsletter_subscriptions`.

## THE COUNT IS THE PAYLOAD HERE, AND IT IS NOT THE NUMBER OF ANCHORS

MEASURED: ten anchors, five newsletters. LinkedIn draws every row twice -- once
around an illustration carrying no text at all, once around the title. The one
question this surface was opened to settle is *how many*, and a reader
publishing the anchor count answers **ten** to it while looking entirely
correct.
"""
from __future__ import annotations

import re
from typing import Any, Optional

from linkedin_server import shape

#: THE ADDRESS. Admitted to the read allowlist on 2026-09-05 and MEASURED to
#: SERVE on 2026-09-05 -- relation ``SERVED, exact``. That measurement is the
#: whole difference between this address and ``/in/me/details/interests/``,
#: which is admitted, was admitted for this same precondition, and redirects.
#: An admitted address is not a served one, and only a load can tell them
#: apart.
SUBSCRIPTIONS_URL = (
    "https://www.linkedin.com/mynetwork/network-manager/newsletters/"
)

#: THE WIDEST POSSIBLE AIM, ON PURPOSE: every anchor whose href mentions the
#: product. Not a class, not a position, not an ordinal.
#:
#: The classes on this page are hashed build artefacts -- the row container is
#: ``div._5bf80336 _63abe882 _46f248c1 ...`` -- so a reader aimed at one has a
#: shelf life measured in LinkedIn deploys. The href is the stable half, which
#: is the same reasoning ``dom.read_invitation_badge`` aims on and the same
#: reasoning ``shape.subscription_row`` refuses on: **a subscription row is
#: identified by where it points, never by where it sits.**
ANCHOR_SELECTOR = 'a[href*="/newsletters/"]'

#: THE CONTROL THAT SEPARATES "HE SUBSCRIBES TO NOTHING" FROM "THIS AIM IS
#: WRONG". Without it a zero out of this module is uninterpretable, and an
#: uninterpretable zero on this surface is not a neutral outcome -- it is
#: precisely the wrong answer, delivered confidently.
#:
#: MEASURED: exactly one ``h2`` whose text is this word, at document position
#: 169, immediately above all ten row anchors, with the next heading 44
#: elements later and belonging to an advertisement. The word is FURNITURE --
#: one plain product noun, no entity, nobody's name -- so matching on it costs
#: no disclosure.
#:
#: The receipt for needing this at all: an aim for the invitation badge
#: required a trailing slash the badged control does not carry, resolved ZERO,
#: and a bare zero would have read as *he has no pending invitations* while the
#: badge was reading ONE.
HEADING_WORD = "newsletters"

#: Where the heading control looks. Plain Playwright, no injection.
HEADING_SELECTOR = "h1, h2, h3"

#: The paragraphs inside one row anchor. The FIRST is the title.
#:
#: WHY THE FIRST PARAGRAPH IS THE TITLE, MEASURED RATHER THAN ASSUMED. Each
#: text-bearing anchor holds exactly two paragraphs, the first 11 to 26
#: characters over the five rows and the second 27 to 107. That alone proves
#: nothing -- a long title and a short blurb are perfectly possible. What
#: proves it is an INDEPENDENT WITNESS that names nobody: a newsletter's slug
#: is derived from its title, and the first paragraph's normalised text is a
#: PREFIX OF THE SLUG in five rows of five, while the second's is in none.
#:
#: That comparison is not discarded once the measurement is taken. It ships as
#: a per-row boolean, so a page that ever reorders the two paragraphs makes
#: this reader SAY SO instead of publishing a description as a title.
PARAGRAPH_SELECTOR = "p"

# ===========================================================================
# THIS MODULE INJECTS NO SCRIPT, AND THAT WAS A CORRECTION RATHER THAN A
# CHOICE.
#
# It first read the rows through one ``page.evaluate`` of a module-level
# ``ROWS_JS``, carrying a ``# readonly-ok`` waiver. ``tests/test_readonly.py``
# refused it, in two places and correctly:
#
#     test_only_dom_module_waives_evaluate          assert set(waived_in) <= {"dom.py"}
#     test_the_scripts_executed_are_exactly_the_ones_declared    extra: ROWS_JS
#
# **THE WAIVER IS SCOPED TO ONE MODULE, NOT RATIONED ACROSS THE PACKAGE.** The
# ``# readonly-ok`` comment silences the executed-script check; it does not
# make a module eligible to hold one. So the choice was never "declare it or
# not" -- it was "belong in ``dom.py``, or do not inject."
#
# AND THE ANSWER WAS ALREADY WRITTEN IN THAT GUARD'S OWN COMMENT, about a
# waiver proposed on 2026-08-30 and declined:
#
#     "A THIRD WAS PROPOSED AND NOT SPENT: main's textContent length is read
#      through locator.text_content(), Playwright's own API, because A WAIVER
#      THAT A PLAIN CALL REPLACES IS A WAIVER NOBODY SHOULD BE ASKED TO
#      REVIEW."
#
# Every line of that script is replaceable by a plain call -- ``count()``,
# ``nth()``, ``get_attribute()``, ``inner_text()`` -- so it was exactly the
# waiver that comment refuses. Declaring it would have asked reviewers to
# widen a security boundary to save this module a loop.
#
# WHAT IT COSTS, STATED SO THE TRADE IS VISIBLE: about forty round trips on
# this page instead of one, since each anchor needs a count, an href and a
# paragraph read. On a five-row list that is not a cost worth a boundary
# change. **If this surface ever grows to hundreds of rows the right answer is
# to move the reader into ``dom.py``, where the waiver lives -- not to inject
# from here.**
# ===========================================================================

#: Everything but letters and digits. A slug is lower-case and hyphenated and a
#: title is neither, so the comparison has to be made on what survives both.
_NORMALISE = re.compile(r"[^a-z0-9]+")


def title_matches_slug(href: Optional[str], title: Optional[str]) -> Optional[bool]:
    """Is this title the string the address was built from?

    RETURNS A BOOLEAN OR ``None`` AND NEVER A FRAGMENT OF EITHER INPUT. The
    two inputs are the most dangerous strings on the page; the answer is one
    bit.

    ``None`` MEANS THE QUESTION COULD NOT BE PUT -- an empty title, or an href
    with no final segment. That is a different answer from ``False`` and the
    two are kept apart deliberately: collapsing "absent" into "false" deletes
    the vocabulary needed to test for the bug, which is a defect class this
    package has already paid for once.

    **IT IS A CONTROL, NOT A CONVENIENCE.** This module picks the first
    paragraph as the title on the strength of one measurement. This function is
    the assertion that the measurement is still true on the page in front of
    it, computed against a string LinkedIn built independently of the markup
    order. A reader whose aiming rule cannot fail is not aimed -- it is
    guessing, and reporting the guess as data.

    **THE RULE IS A STRICT PREFIX, AND WHAT THAT ASSUMES IS STATED RATHER THAN
    GUARDED AGAINST.** It assumes the slug is the whole normalised title plus a
    tail, which is what five rows of five showed on 2026-09-05 -- with titles
    of 11 to 26 characters, where truncation could not have shown even if it
    happens. If LinkedIn truncates the slug of a LONG title, this returns
    ``False`` for a title that is perfectly correct: a false alarm, on a
    surface where a false alarm costs a caution and a false all-clear costs a
    name. Widening the rule to "either is a prefix of the other" would absorb
    that case and would also make it much harder for this control to fail at
    all, which is the property it exists for. So the narrow rule stands until
    somebody MEASURES a truncated slug, and this paragraph is the record that
    nobody has.
    """
    slug = str(href or "").split("?")[0].rstrip("/").rsplit("/", 1)[-1]
    slug_norm = _NORMALISE.sub("", slug.lower())
    title_norm = _NORMALISE.sub("", str(title or "").lower())
    if not slug_norm or not title_norm:
        return None
    return slug_norm.startswith(title_norm)


async def read_newsletter_subscriptions(page: Any) -> dict[str, Any]:
    """The newsletters he subscribes to, ALREADY GATED.

    THE SHAPING HAPPENS HERE, which is ``dom.read_surface_census``'s standing
    placement rule rather than a stylistic choice: it is what lets this
    function's return value be described without a caveat. Shaping in the tool
    instead would leave a function in this package returning other people's
    publications to whoever called it next.

    RETURNS, and the census half carries as much weight as the rows::

        {
          "rows": [...],            # one shape.subscription_row per DISTINCT href
          "heading_seen": int,      # THE CONTROL -- see HEADING_WORD
          "anchors": int,           # every anchor matching the product
          "anchors_without_text": int,
          "distinct": int,          # THE SUBSCRIPTION COUNT
          "published": int,
          "titles_matching_slug": int,
          "titles_unmatched": int,
          "error": str | None,
        }

    **``distinct`` IS THE ANSWER, NOT ``anchors``.** Measured 2026-09-05: ten
    anchors, five newsletters. The illustration anchors are COUNTED and dropped
    rather than filtered in silence, because a page that stopped drawing them
    would otherwise move the headline number with nothing saying why.

    **A ZERO IS ONLY INTERPRETABLE BESIDE ``heading_seen``.** Zero rows with the
    heading present is a fact about HIS ACCOUNT. Zero rows with the heading
    absent is a fact about THIS INSTRUMENT -- a wrong aim, or a page that had
    not hydrated -- and a caller that reports the first when it measured the
    second has answered the whole blocker backwards. The two never share a
    field.

    NO NAVIGATION AND NO PRESS. It reads the document it is handed. The caller
    owns reaching :data:`SUBSCRIPTIONS_URL`, and owns the invitation-badge
    obligation that address inherits from ``/mynetwork/``: read
    ``dom.read_invitation_badge`` before and after, and refuse when it cannot
    be read. That obligation is not discharged by this function and it must not
    look as though it were.
    """
    out: dict[str, Any] = {
        "rows": [],
        "heading_seen": 0,
        "anchors": 0,
        "anchors_without_text": 0,
        "distinct": 0,
        "published": 0,
        "titles_matching_slug": 0,
        "titles_unmatched": 0,
        "error": None,
    }
    try:
        # THE CONTROL FIRST, so a run that finds no rows already knows which
        # kind of zero it has.
        headings = page.locator(HEADING_SELECTOR)
        for index in range(int(await headings.count())):
            text = str(await headings.nth(index).inner_text() or "").strip()
            if text.lower() == HEADING_WORD:
                out["heading_seen"] += 1

        anchors = page.locator(ANCHOR_SELECTOR)
        out["anchors"] = int(await anchors.count())
        records: list[tuple[str, int, str]] = []
        for index in range(out["anchors"]):
            item = anchors.nth(index)
            href = str(await item.get_attribute("href") or "")
            paragraphs = item.locator(PARAGRAPH_SELECTOR)
            count = int(await paragraphs.count())
            title = (
                str(await paragraphs.first.inner_text() or "").strip()
                if count
                else ""
            )
            records.append((href, count, title))
    except Exception as exc:  # pragma: no cover - defensive
        # THE CLASS AND THE MESSAGE, BOTH. A handler that keeps the class and
        # drops the message is one of this project's own scars: the diagnostic
        # named its own cause and was thrown away. Neither carries a title --
        # a selector goes in, and nothing is interpolated back.
        #
        # THE WHOLE READ IS INSIDE ONE TRY, and that is deliberate now that it
        # is forty round trips rather than one evaluate: a frame detaching
        # halfway would otherwise leave a PARTIAL row list that looks like a
        # complete short one. A half-read subscription list reporting three of
        # five is worse than an error, because nothing downstream can tell.
        out["error"] = "%s: %s" % (type(exc).__name__, exc)
        out["rows"] = []
        out["heading_seen"] = 0
        out["anchors"] = 0
        return out

    seen: set[str] = set()
    for href, paragraph_count, title in records:
        if not paragraph_count:
            # THE ILLUSTRATION ANCHOR: same href, no text of any kind. This is
            # the branch that makes ten into five.
            out["anchors_without_text"] += 1
            continue
        key = href.split("?")[0].rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        matched = title_matches_slug(href, title)
        if matched is True:
            out["titles_matching_slug"] += 1
        else:
            out["titles_unmatched"] += 1
        row = dict(shape.subscription_row(href, title))
        # THE CONTROL TRAVELS WITH THE ROW, so a caller holding one row can
        # tell whether the rule that picked its title is still holding, without
        # re-deriving the measurement this module was built on.
        row["title_matches_slug"] = matched
        out["rows"].append(row)
        if row.get("published"):
            out["published"] += 1
    out["distinct"] = len(seen)
    return out
