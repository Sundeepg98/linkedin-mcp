"""What do the four FREE member-space reads actually return, in counts and shapes?

FOUR ADDRESSES THIS PACKAGE CAN REACH FOR NOTHING, AND NOT ONE OF THEM HAS
BEEN MEASURED. ``scripts/_probe_self_details_url.py`` settled one question on
one of them -- ``/in/me/details/skills/`` is served, and 20 skill cards came
back through the shipped harvest -- and every neighbouring surface was left
as an assumption:

    /in/me/details/experience/    is it served, and what harvests it?
    /in/me/details/education/     the same question, a different section
    /analytics/profile-views/     what does the census see on the free view?
    /jobs/view/<id>               and on a posting

THE HARVEST PATTERN IS THE POINT ON TWO OF THEM. ``dom.SKILL_HREF`` works on
the skills page because LinkedIn hangs a per-skill EDIT affordance off the
owner's own list, and that id is the only per-entry key the page offers. The
same argument PREDICTS an experience form id and an education form id, and a
prediction is not a measurement: the entries could equally be keyed on a
company link, a school link, or on nothing at all. So this runs every
candidate ONCE PER PATTERN and prints the pattern beside the count it
returned. The winner is identified by measurement rather than by the argument
that suggested it -- the same discipline the skills question got, and the
reason that one did not have to be re-litigated.

``dom.SKILL_HREF`` RUNS ON BOTH AS THE CONTROL. It is the pattern already
proven on the skills page, and a NON-ZERO count for it on the experience or
education document would mean these form ids are not section-specific -- at
which point a high count for a candidate proves much less than it looks like
it does. A control that cannot fire is not a control, so it is run and
reported whatever it returns.

A REFUSAL MUST SAY WHAT IT DID SEE, and that is the shape of the whole run.
A zero card count on its own has already cost this package two wrong
diagnoses: it is returned both by a page that drew nothing and by a page that
drew everything under a key this probe did not ask for. So EVERY surface
reports its ``dom.read_main_text`` character count and a heading tally
WHATEVER the harvests return. "Zero cards, but main carried 4812 characters
under 7 headings" and "zero cards, and main was empty" are different
findings, and a probe that cannot tell them apart is not worth the session.

## Bounds

**IT NAVIGATES MODULE-LEVEL CONSTANTS AND NOTHING ELSE.** Five addresses,
five constants, none built from anything a page said.
``tests/test_navigation_is_never_derived.py`` scans this file like any other,
and this is the rule the exemplar it copies exists to demonstrate.

**COUNTS, SHAPES AND FURNITURE HEADINGS. NOTHING ELSE.** No url, no landed
value, no member path, no person's name, no company name. The relation
between the address asked for and the one that came back is ``_shape_of``,
copied from ``_probe_self_details_url.py`` -- it exists because the first run
of that probe printed the operator's slug. Section headings are LinkedIn's
own furniture words and are printed only when they pass ``_safe_heading``;
anything carrying an unrecognised run of capitalised words is withheld as a
character count, because a run of capitalised words is what a person's name
and a company's name both look like.

**NO OUTPUT PATH.** None, and no constant that could become one.

**IT IS A READ.** Allowlisted GETs of his own surfaces. Nothing is pressed,
typed, scrolled or submitted, and each surface is wrapped in its own
try/except so one failure does not cost the other four.

**JOB_ID IS A PLACEHOLDER AND SURFACE 5 SKIPS ITSELF UNTIL IT IS FILLED IN.**

Run:  python scripts/_probe_free_reads_shapes.py
Writes NOTHING.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402

#: THE FIVE ADDRESSES, EVERY ONE A MODULE-LEVEL CONSTANT. Not one is built
#: from anything the page said, which is the single rule the exemplar this
#: file copies exists to demonstrate.
SELF_PROFILE_URL = f"{BASE_URL}/in/me/"
SELF_EXPERIENCE_URL = f"{BASE_URL}/in/me/details/experience/"
SELF_EDUCATION_URL = f"{BASE_URL}/in/me/details/education/"
PROFILE_VIEWS_URL = f"{BASE_URL}/analytics/profile-views/"

#: THE LEAD FILLS THIS IN BEFORE RUNNING. "0" is not a job id and is not meant
#: to be one: surface 5 SKIPS ITSELF while this is the placeholder, so the
#: file is runnable as committed and measures four surfaces rather than
#: erroring on the fifth. The guard is ``_job_id_is_usable`` -- all digits,
#: at least six of them -- which is also exactly what
#: readonly._ALLOWED_URL_PATTERNS admits (^.../jobs/view/\d{6,}/?$), so an id
#: that passes the guard is one the read boundary will accept.
#: FILLED IN 2026-09-03 from linkedin_saved_jobs -- the one row in the
#: operator's Saved tab. A POSTING id, not a person.
JOB_ID = "4423880462"
JOB_POSTING_URL = f"{BASE_URL}/jobs/view/{JOB_ID}"

#: CANDIDATE KEYS FOR AN EXPERIENCE ENTRY, run one at a time so the winner is
#: named by its count rather than by the argument that proposed it. Every one
#: is a guess until this runs, which is why there are three.
EXPERIENCE_HREF_CANDIDATES = (
    r"/details/experience/edit/forms/(\d+)",
    r"/company/([A-Za-z0-9\-_%]+)",
    r"/search/results/all/\?keywords=([^&\"]+)",
)

#: The same for an education entry.
EDUCATION_HREF_CANDIDATES = (
    r"/details/education/edit/forms/(\d+)",
    r"/school/([A-Za-z0-9\-_%]+)",
    r"/company/([A-Za-z0-9\-_%]+)",
)

#: BLOCK-CARD SELECTORS, DEFINED HERE RATHER THAN BORROWED.
#:
#: ``dom.NOTIFICATION_SELECTORS`` would have worked mechanically -- its tail
#: is generic -- and it is deliberately not used: its NAME asserts a surface
#: that is none of these four, and a count taken through a misnamed constant
#: is a number nobody can interpret six weeks later. These are structural and
#: say so. ``harvest_block_cards`` returns the FIRST selector that yields any
#: card, so the winning selector is reported beside the count.
GENERIC_BLOCK_SELECTORS = ("main section", "main article", "main ul li", "main li")

#: The six integer tallies ``dom.read_surface_census`` returns under
#: ``counts``. Named here so this probe prints what that function actually
#: returns rather than what a reader assumes it returns.
CENSUS_COUNT_KEYS = (
    "forms",
    "buttons",
    "links",
    "contenteditable",
    "file_inputs",
    "dialogs",
)

#: RUNS OF CAPITALISED WORDS THAT ARE FURNITURE RATHER THAN IDENTITIES.
#:
#: A heading is printed only when every run of two or more consecutive
#: capitalised words in it appears here. The reason is that a capitalised run
#: is exactly what a person's name and a company's name look like, and a
#: heading tally that printed one would leak the thing this file is arranged
#: not to leak.
#:
#: MOST LINKEDIN FURNITURE NEVER TRIPS THE FILTER AT ALL, because LinkedIn
#: writes its headings in sentence case: "Top companies", "Top locations",
#: "How you match", "Skills match", "Why am I seeing this job" and "Promoted"
#: contain no run of two capitalised words and need no entry here. This list
#: is only for the product names that do.
#:
#: SEEDED, AND DELIBERATELY SHORT. Every entry is a LinkedIn PRODUCT or
#: CONTROL name, never an entity name, and a run that is missing costs one
#: heading printed as "<withheld: N chars>" -- which is the safe direction.
#: Add an entry only from a withheld count somebody actually looked at.
FURNITURE_RUNS = frozenset(
    {
        "Easy Apply",
        "LinkedIn News",
        "LinkedIn Premium",
        "Premium Career",
        "Sales Navigator",
    }
)

#: Punctuation stripped off a token before its first character is examined.
HEADING_TRIM = " \t\r\n.,:;!?()[]{}'\"/-"


def _path_of(url: str) -> str:
    """The path of a url and nothing else -- no host, no query."""
    return urlsplit(str(url or "")).path.rstrip("/")


def _shape_of(url: str, requested: str) -> str:
    """WHAT HAPPENED TO AN ADDRESS, never the address it became.

    COPIED FROM ``scripts/_probe_self_details_url.py``, which is where the
    argument for it lives: the first run of that probe printed the operator's
    slug out of a file whose docstring promised it never printed a url,
    because ``/in/me/...`` REDIRECTS to ``/in/<vanity>/...`` and a member path
    IS an identity.

    A LOCAL COPY UNDER THE SAME NAME, and that is not laziness. The name sits
    on ``tests/test_navigation_is_never_derived.py::_SANITISERS``, which is a
    claim about a CONTRACT -- a function that takes a tainted value and
    provably returns one which cannot reconstruct it. Defining it here keeps
    that claim checkable in this file; importing it would put the contract one
    indirection away from the rule that pins it.

    So this returns the RELATION between what was asked for and what came
    back -- served, redirected within the member space, or redirected away --
    and the relation is what the question actually needs.
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


def _job_id_is_usable() -> bool:
    """Is JOB_ID a real posting id, or is it still the placeholder?

    ALL DIGITS AND AT LEAST SIX, spelled out rather than ``str.isdigit``,
    which also accepts superscripts and other unicode digit forms that no job
    id has ever worn. The bound matches the read allowlist, so an id this
    accepts is one the read boundary will accept too.
    """
    return len(JOB_ID) >= 6 and all(character in "0123456789" for character in JOB_ID)


def _capitalised_runs(heading: str) -> list[str]:
    """Every maximal run of two or more consecutive capitalised words.

    ONE capitalised word is not a run and is not withheld: "Promoted" is a
    heading, and "Why am I seeing this job" carries a capital I that no rule
    should choke on. TWO in a row is the shape of a name, which is the thing
    being kept out of the output.

    ``str.isupper`` rather than a set of A-Z, so a capitalised non-ASCII
    initial counts as capitalised. Erring that way costs a withheld heading;
    erring the other way costs an identity.
    """
    runs: list[str] = []
    current: list[str] = []
    for token in str(heading or "").split():
        word = token.strip(HEADING_TRIM)
        if word and word[:1].isupper():
            current.append(word)
            continue
        if len(current) >= 2:
            runs.append(" ".join(current))
        current = []
    if len(current) >= 2:
        runs.append(" ".join(current))
    return runs


def _safe_heading(heading: str) -> str:
    """A heading, or a character count where a heading would have been.

    THE WITHHOLDING IS THE DEFAULT AND THE ALLOWLIST IS THE EXCEPTION, which
    is the only arrangement that fails safely: an unrecognised capitalised run
    costs one heading rendered as a count, where the opposite arrangement
    costs an identity the first time LinkedIn puts a name in an h3.
    """
    text = str(heading or "").strip()
    if any(run not in FURNITURE_RUNS for run in _capitalised_runs(text)):
        return "<withheld: %d chars>" % len(text)
    return text


def _report_failure(exc: BaseException) -> None:
    """The exception's TYPE and the LENGTH of its text. Never the text.

    ``dom``'s readers raise ``ExtractionFailedError(..., url=_url_of(page))``,
    and the read boundary's own refusal interpolates the url it is refusing --
    the exact mechanism that put the operator's vanity slug into a traceback
    out of a probe that never chose to print a url. A promise about what a
    file CHOOSES to print does not hold for an exception escaping through it,
    so the text is never rendered at all.
    """
    print(
        "      FAILED: %s (%d chars of detail, withheld)"
        % (type(exc).__name__, len(str(exc)))
    )


async def _report_furniture(page) -> None:
    """Main text size and the heading tally. RUNS ON EVERY SURFACE.

    THIS IS WHAT MAKES A ZERO READABLE. Every harvest below can return an
    empty list, and an empty list comes back both from a page that drew
    nothing and from a page that drew everything under a key nobody asked
    for. The character count and the heading tally separate those two, so
    they are printed whatever the harvests do.

    WHY A FUNCTION NAMED FOR THE PROFILE RUNS ON THE ANALYTICS VIEW AND ON A
    JOB POSTING. ``dom.read_profile_fields`` is not profile-shaped in any way:
    its script walks ``main``'s h1/h2/h3 elements and returns each heading
    with the lines under it. Nothing in it knows or cares which surface it is
    standing on, and a heading tally is exactly what it produces. The name
    records where it was first needed, not what it is limited to.

    ITS RETURN ALSO CARRIES ``url`` AND ``title`` -- ``document.location.href``
    and ``document.title`` -- AND NEITHER IS TOUCHED HERE. Not printed, not
    passed on, not bound to a local. The taint instrument cannot help with
    this one: it keys on an ATTRIBUTE named ``url``, and ``fields["url"]`` is
    a subscript it would walk straight past. Not reading the key is the whole
    of the protection.
    """
    print("      main text: %d chars" % len(await dom.read_main_text(page)))
    fields = await dom.read_profile_fields(page)
    sections = list(fields.get("sections") or [])
    print(
        "      read_profile_fields: has_main=%s  sections=%d"
        % (bool(fields.get("has_main")), len(sections))
    )
    for section in sections:
        # ``images`` is ALREADY an integer in the return -- the script counts
        # ``img`` elements and reports the number -- so it is printed as the
        # count it is rather than measured a second time.
        print(
            "        [lines %3d, images %2d]  %s"
            % (
                len(list(section.get("lines") or [])),
                int(section.get("images") or 0),
                _safe_heading(section.get("heading")),
            )
        )


async def _report_blocks(page) -> None:
    """How many BLOCK-shaped cards a surface offers, and under which selector.

    ``dom.CARD_HIDDEN_SELECTOR`` is passed so the screen-reader strings a card
    carries are COUNTED rather than silently absent -- the count only, never
    the strings.
    """
    records = await dom.harvest_block_cards(
        page,
        selectors=list(GENERIC_BLOCK_SELECTORS),
        max_items=200,
        hidden_selector=dom.CARD_HIDDEN_SELECTOR,
    )
    winners = sorted({str(record.get("selector") or "") for record in records})
    with_hidden = sum(1 for record in records if list(record.get("hidden") or []))
    print(
        "      harvest_block_cards: %3d cards  (selector: %s)  carrying hidden: %d"
        % (len(records), ", ".join(winners) or "none matched", with_hidden)
    )


async def _report_pattern(page, pattern: str, note: str = "") -> None:
    """One ``harvest_linked_cards`` run, its pattern printed beside its count.

    ONE RUN PER PATTERN IS THE MEASUREMENT. A single run under a guessed
    pattern answers "did this guess work", which is not the question. The set
    of counts across the candidates is what identifies the key the page
    actually uses.
    """
    records = await dom.harvest_linked_cards(
        page, href_pattern=pattern, max_items=200, max_chars=300
    )
    print("      %-48s -> %3d cards%s" % (pattern, len(records), note))


async def _report_census(page) -> None:
    """The control census, as a row count, a shape tally and six integers.

    THE FIRST RUN OF THIS PROBE PUBLISHED THIRTEEN REAL NAMES, and this
    docstring used to be the reason why. It said every row's name "has
    already been through ``shape.census_shape``, which is where the raw
    string is discarded", concluded the shapes were printable, and tallied
    them here. HALF TRUE IS THE DANGEROUS KIND. ``census_shape`` opaques a
    long or non-ASCII string and ``census_href_identifies_entity`` blanks a
    control that LINKS to a member -- but the rule that catches a member's
    name in a control that does NOT link to them is
    ``shape.census_redact_rare``, and it CANNOT run in the reader: it fires
    only at ``count == 1`` and the count does not exist until the rows are
    merged. ``dom.py:1480`` says so out loud -- "deliberately NOT applied".

    So the redaction lives at PUBLISH time, in ``shape.census_aggregate``,
    which merges the rows, blanks the singletons and merges AGAIN on the
    redacted key. ``linkedin_surface_census`` calls it. This probe hand-rolled
    its own tally and therefore skipped it, and out came "Follow <a real
    person>", "Send a message to <a real person>", "Open control menu for post
    by <a real person>" -- thirteen rows, none of which any rule was broken to
    produce. **A HAND-ROLLED TALLY IS A RE-IMPLEMENTED PRIVACY BOUNDARY.**

    It now calls ``shape.census_aggregate`` -- the same function the shipped
    tool calls -- and prints ``shape`` and ``count`` off the rows that come
    back. Nothing else on a row is printable and nothing else is printed.

    ``truncated`` matters and is not decoration: the ceiling is
    ``dom.CENSUS_MAX_CONTROLS`` (400), and a surface that reaches it has a
    tail this run did not see.
    """
    census = await dom.read_surface_census(page)
    controls = list(census.get("controls") or [])
    counts = dict(census.get("counts") or {})
    print(
        "      read_surface_census: rows=%d  controls_read=%s  truncated=%s"
        % (len(controls), census.get("controls_read"), bool(census.get("truncated")))
    )
    print(
        "      counts: %s"
        % "  ".join(
            "%s=%d" % (key, int(counts.get(key) or 0)) for key in CENSUS_COUNT_KEYS
        )
    )
    control_shapes, _hrefs = shape.census_aggregate(controls)
    tally: dict[str, int] = {}
    for row in control_shapes:
        name = str(row.get("shape") or "")
        tally[name] = tally.get(name, 0) + int(row.get("count") or 0)
    for name, seen in sorted(tally.items(), key=lambda item: (-item[1], item[0])):
        print("        %4d  %s" % (seen, name))


async def main() -> None:
    print("=== WHAT DO THE FREE MEMBER-SPACE READS RETURN?")
    print("    five module-level addresses, one session, nothing pressed")
    print("    counts, shapes and furniture headings -- never a url or a name\n")

    await BROWSER.start()
    async with BROWSER.session() as page:
        # ------------------------------------------------------------------
        # SURFACE 1 -- the auth wall, and nothing else is asked of it.
        # ------------------------------------------------------------------
        landed_profile = await BROWSER.goto(page, SELF_PROFILE_URL)
        if "/login" in landed_profile or "/checkpoint" in landed_profile:
            print("    AUTH WALL. Not signed in, so nothing was measured.")
            await BROWSER.stop()
            return
        print(
            "    signed in. profile: %s" % _shape_of(landed_profile, SELF_PROFILE_URL)
        )

        # ------------------------------------------------------------------
        # SURFACE 2 -- the experience document
        # ------------------------------------------------------------------
        print("\n=== SURFACE 2: /in/me/details/experience/")
        try:
            landed_experience = await BROWSER.goto(page, SELF_EXPERIENCE_URL)
            print(
                "      relation: %s"
                % _shape_of(landed_experience, SELF_EXPERIENCE_URL)
            )
            if "/login" in landed_experience or "/checkpoint" in landed_experience:
                print("      AUTH WALL on this address. Nothing else measured here.")
            else:
                await _report_furniture(page)
                await _report_blocks(page)
                for candidate in EXPERIENCE_HREF_CANDIDATES:
                    await _report_pattern(page, candidate)
                await _report_pattern(page, dom.SKILL_HREF, "   <- CONTROL")
        except Exception as exc:  # noqa: BLE001 - one surface may not cost four
            _report_failure(exc)

        # ------------------------------------------------------------------
        # SURFACE 3 -- the education document
        # ------------------------------------------------------------------
        print("\n=== SURFACE 3: /in/me/details/education/")
        try:
            landed_education = await BROWSER.goto(page, SELF_EDUCATION_URL)
            print(
                "      relation: %s" % _shape_of(landed_education, SELF_EDUCATION_URL)
            )
            if "/login" in landed_education or "/checkpoint" in landed_education:
                print("      AUTH WALL on this address. Nothing else measured here.")
            else:
                await _report_furniture(page)
                await _report_blocks(page)
                for candidate in EDUCATION_HREF_CANDIDATES:
                    await _report_pattern(page, candidate)
                await _report_pattern(page, dom.SKILL_HREF, "   <- CONTROL")
        except Exception as exc:  # noqa: BLE001
            _report_failure(exc)

        print("\n    THE CONTROL LINE ON BOTH SURFACES IS dom.SKILL_HREF, the")
        print("    pattern already proven on the skills page. A NON-ZERO count")
        print("    there means these form ids are NOT section-specific, and every")
        print("    candidate count above it means correspondingly less.")

        # ------------------------------------------------------------------
        # SURFACE 4 -- who viewed the profile
        # ------------------------------------------------------------------
        print("\n=== SURFACE 4: /analytics/profile-views/")
        try:
            landed_views = await BROWSER.goto(page, PROFILE_VIEWS_URL)
            print("      relation: %s" % _shape_of(landed_views, PROFILE_VIEWS_URL))
            if "/login" in landed_views or "/checkpoint" in landed_views:
                print("      AUTH WALL on this address. Nothing else measured here.")
            else:
                await _report_furniture(page)
                await _report_blocks(page)
                await _report_pattern(page, dom.PERSON_HREF)
                await _report_pattern(page, dom.SKILL_HREF, "   <- CONTROL")
                await _report_census(page)
        except Exception as exc:  # noqa: BLE001
            _report_failure(exc)

        # ------------------------------------------------------------------
        # SURFACE 5 -- one job posting. It skips itself until JOB_ID is real.
        # ------------------------------------------------------------------
        print("\n=== SURFACE 5: /jobs/view/<JOB_ID>")
        if not _job_id_is_usable():
            print("      SKIPPED. JOB_ID is still the placeholder, so there is no")
            print("      posting to read. Fill JOB_ID in at the top of this file --")
            print("      all digits, at least six -- and run again.")
        else:
            try:
                landed_posting = await BROWSER.goto(page, JOB_POSTING_URL)
                print(
                    "      relation: %s" % _shape_of(landed_posting, JOB_POSTING_URL)
                )
                if "/login" in landed_posting or "/checkpoint" in landed_posting:
                    print("      AUTH WALL on this address. Nothing else measured.")
                else:
                    # ``read_profile_fields`` runs here too, and its NAME is the
                    # only thing about it that says "profile": it walks main's
                    # headings and returns them with their lines, which is exactly
                    # the tally a posting wants ("How you match", "Skills match",
                    # "Why am I seeing this job"). Its url and title keys are not
                    # read -- see the note on ``_report_furniture``.
                    await _report_furniture(page)
                    await _report_blocks(page)
                    await _report_pattern(page, dom.PERSON_HREF)
                    await _report_pattern(page, dom.SKILL_HREF, "   <- CONTROL")
                    await _report_census(page)
            except Exception as exc:  # noqa: BLE001
                _report_failure(exc)

        print("\n=== READING")
        print("    A CANDIDATE PATTERN WINS BY ITS COUNT, not by the argument that")
        print("    proposed it -- and only while the CONTROL line reads zero.")
        print("    ZERO EVERYWHERE IS NOT 'NOT SERVED': read it against the main")
        print("    text size and the heading tally on the same surface. Text with")
        print("    no cards is a key this probe did not ask for; no text at all is")
        print("    a page that did not draw, and this probe does not scroll.")

    await BROWSER.stop()


# GUARDED: importing a script must not DO anything.
# ``tests/test_scripts_are_import_safe.py`` asserts that for every script here.
if __name__ == "__main__":
    asyncio.run(main())
