"""The About-the-company card: four company-Page reads that open no company Page.

WHY THIS FILE EXISTS AND WHAT IT IS DEFENDING.

The surface census scores ``COMPANY-PAGE-SURFACE`` at 18 rows, 13 of them
reads, and files all 18 behind putting ``/company/`` on the read allowlist.
Four of the thirteen do not need it. LinkedIn draws a Page's follower count,
its industry, its self-declared size band and its LinkedIn headcount on the
JOB POSTING's own About-the-company card -- on ``/jobs/view/<id>``, an address
already on ``readonly._ALLOWED_URL_PATTERNS`` and already loaded by
``linkedin_job_detail``.

That matters beyond the four rows. A company Page is a THIRD PARTY'S surface,
and nothing in this repository has measured what opening one costs. The
instrument that proved the member-profile emission is
``linkedin_who_viewed_me`` -- a per-member viewer list this account holds. The
organisation-side equivalent is a Page ADMIN analytics surface, and the
tracked Manage Pages capture carries 58 Pages and ZERO admin markers, so that
instrument is not reachable from here. An unmeasured cost is not a zero cost.
Reading these four off a render he already performed does not answer that
question; it declines to ask it, which is the honest description.

THE THREE MEASUREMENTS THIS FILE PINS, each taken before the code was written:

1. ``dom.harvest_linked_cards`` CANNOT reach these fields, and not because of
   its depth. Run over the tracked fixtures at six depths (1, 2, 3, 4, 6, 8 --
   ``_audit/_scratch/_probe_company_about_hops.py``) the card anchored on the
   ``/company/.../life/`` link is 16 characters at every one of them. The
   cause is the walk's own stop rule, ``keysWithin(node).size > 1``: the About
   section holds two distinct ``/company/`` targets, so the climb halts at the
   anchor. Raising the hop count cannot help, because the walk is not stopping
   for want of budget. That is why a dedicated reader exists.

2. THE CONTAINER ARRIVES BEFORE ITS CONTENTS. ``job_detail_following.html``
   carries the ``componentkey`` container with a shimmer bar and NO TEXT, and
   no SDUI attribute. A reader anchored on the container alone would report an
   employer with no follower count and no industry -- as a fact about the
   employer. It is a fact about hydration, and ``unhydrated`` is a state of
   its own for exactly that reason.

3. THE META ROW IS A ROW. LinkedIn draws
   ``<industry> BULLET <size band> BULLET <N on LinkedIn>``, and the industry
   is the only one of the three with no pattern of its own. Matched by
   position alone it is whatever sits in that slot, so the row's shape is
   asserted first and the industry read at an offset from an anchor that CAN
   refuse.

Everything here runs offline. The browser sections drive a local headless
Chromium over committed, sanitised fixtures -- no LinkedIn session, no
persistent profile, no lock, and no third party's page.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from linkedin_server import dom, shape

FIXTURE_DIR = Path(__file__).parent / "fixtures"

#: The renders this card has been SEEN on, and what each one is here to prove.
FILLED = ["job_detail.html", "job_detail_hydrated.html"]
#: The same page for an employer he already follows -- the sanitised follower
#: count is what makes it a different test rather than a third copy.
FOLLOWED = "job_detail_following_hydrated.html"
#: Container present, no text. The measurement behind the ``unhydrated`` state.
SKELETON = "job_detail_following.html"
#: No container at all. The measurement behind ``absent``.
SHELL = "job_detail_shell.html"

BULLET = shape.ABOUT_BULLET
#: Named rather than typed, so this file stays pure ASCII on a cp1252 console.
APOSTROPHE = shape.APOSTROPHE
#: LinkedIn's control label, with the typographic apostrophe it really draws.
INTEREST_LABEL = "I" + APOSTROPHE + "m interested"
EMPLOYER = "Ashgrove Systems"

#: One card, spelled out, so every gate below has something to be aimed at.
#: It is the shape ``dom.read_company_about_card`` returned from
#: ``job_detail_hydrated.html``, with the description shortened.
CARD = [
    "About the company",
    EMPLOYER,
    "5,288,656 followers",
    "Follow",
    "Staffing and Recruiting",
    BULLET,
    "51-200 employees",
    BULLET,
    "304 on LinkedIn",
    "Ashgrove Systems connects skilled professionals with opportunities.",
    "Key areas of focus",
    "Interested in working with us in the future?",
    INTEREST_LABEL,
    "Show more",
]

#: A word that appears ONLY inside the description. The withholding test is
#: aimed at this string, and the detector that looks for it is proved able to
#: find something before it is trusted to find nothing.
DESCRIPTION_ONLY_WORD = "skilled"


def observed(lines, container=True):
    """A ``dom.read_company_about_card`` return, built by hand."""
    return {"container": container, "sdui": True, "lines": list(lines), "error": None}


def fields_carrying(result, needle):
    """Every (field, value) of a verdict whose string form carries ``needle``.

    FACTORED OUT OF THE ASSERTION THAT CONSUMES IT, deliberately. A search
    written inside an ``assert`` has no handle, so it can never be aimed at a
    sample that is known to contain the thing -- and a search that cannot be
    shown finding is worth nothing when it finds nothing.
    ``test_the_withholding_detector_can_find_something`` is that aiming.
    """
    hits = []
    for key, value in (result or {}).items():
        if needle.casefold() in str(value).casefold():
            hits.append((key, value))
    return hits


# ---------------------------------------------------------------------------
# 1. The five states, and the two in the middle are the point
# ---------------------------------------------------------------------------


def test_a_whole_card_reads_all_four_fields():
    out = shape.company_about_card(observed(CARD), company=EMPLOYER)
    assert out["state"] == "read"
    assert out["followers"] == 5288656
    assert out["industry"] == "Staffing and Recruiting"
    assert out["size_band"] == "51-200"
    assert out["on_linkedin"] == 304
    assert out["follow_state"] == "Follow"


def test_no_container_is_absent():
    out = shape.company_about_card(observed([], container=False), company=EMPLOYER)
    assert out["state"] == "absent"
    assert out["followers"] is None


def test_a_container_holding_no_text_is_unhydrated_and_not_absent():
    """THE DISTINCTION THIS STATE EXISTS FOR, asserted rather than described.

    Both states carry ``followers is None``. If they carried the same
    ``state`` as well, a caller could not tell "LinkedIn drew no card" from
    "the card had not been filled in yet", and the second reads as the first
    -- which is the claim that this employer has no followers.
    """
    empty = shape.company_about_card(observed([]), company=EMPLOYER)
    missing = shape.company_about_card(observed([], container=False), company=EMPLOYER)
    assert empty["state"] == "unhydrated"
    assert missing["state"] == "absent"
    assert empty["state"] != missing["state"]
    assert "hydration" in empty["why"]


def test_a_card_that_does_not_open_by_naming_this_employer_reports_nothing():
    out = shape.company_about_card(observed(CARD), company="Somewhere Else Ltd")
    assert out["state"] == "unnamed"
    for field in ("followers", "industry", "size_band", "on_linkedin", "follow_state"):
        assert out[field] is None, field


def test_the_unnamed_refusal_drops_its_booleans_too():
    """A refusal that keeps some of its findings is a half-applied refusal.

    ``description_truncated`` and ``interest_control`` are computed BEFORE the
    name is checked, so they survive the refusal unless it clears them. Saying
    "the interest control is drawn" about a card this function has just
    declined to attribute is a claim about a page it disowned.
    """
    out = shape.company_about_card(observed(CARD), company="Somewhere Else Ltd")
    assert out["interest_control"] is False
    assert out["description_truncated"] is False
    # ... and the same card, correctly named, DOES report both -- so the
    # assertion above is about the refusal and not about the card being empty.
    named = shape.company_about_card(observed(CARD), company=EMPLOYER)
    assert named["interest_control"] is True
    assert named["description_truncated"] is True


def test_an_unnamed_posting_cannot_attribute_a_card():
    out = shape.company_about_card(observed(CARD), company=None)
    assert out["state"] == "unnamed"
    assert out["followers"] is None


# ---------------------------------------------------------------------------
# 2. The meta row is matched as a ROW, and the check can refuse
# ---------------------------------------------------------------------------


def test_a_missing_bullet_costs_the_industry_and_not_the_size_band():
    """THE ROW-SHAPE GATE, SHOWN REFUSING.

    The industry has no pattern of its own -- it is a label. It is read at a
    fixed offset from the size band ONLY IF both bullets and the headcount
    line are where LinkedIn's row says they are. Remove one bullet and the
    offset would land on the follow state, so the industry must go null. The
    size band, which has its own pattern, is unaffected: a gate that fails
    should cost what it guards and nothing else.
    """
    broken = [line for line in CARD if line != BULLET]
    out = shape.company_about_card(observed(broken), company=EMPLOYER)
    assert out["state"] == "partial"
    assert out["industry"] is None
    assert out["size_band"] == "51-200"
    assert "industry" in out["why"]


def test_the_industry_slot_is_not_published_when_it_holds_an_unexpected_shape():
    """Refusing an unknown string costs an industry; publishing one costs
    whatever was in that slot. The taxonomy label is a SELECTION, but nothing
    here can prove LinkedIn's list is closed, so the shape is the gate."""
    odd = list(CARD)
    odd[4] = "<script>alert(1)</script>"
    out = shape.company_about_card(observed(odd), company=EMPLOYER)
    assert out["industry"] is None
    assert out["state"] == "partial"


def test_the_industry_is_read_from_the_row_and_not_from_the_first_label():
    """Aimed at the offset, not at the happy path.

    A reader that took "the first line that looks like a label" would return
    the heading. The anchor is the size band, and the industry is two lines
    above it.
    """
    out = shape.company_about_card(observed(CARD), company=EMPLOYER)
    assert out["industry"] == "Staffing and Recruiting"
    assert out["industry"] != "About the company"
    assert out["industry"] != EMPLOYER


def test_the_declared_band_and_the_linkedin_headcount_are_different_facts():
    """They disagree on the real capture and NEITHER is wrong.

    ``51-200`` is what the organisation declared. ``304`` is how many member
    profiles LinkedIn attributes to it. A reader that folded them into one
    "size" would publish a contradiction as a fact, so they are two fields and
    this test says so out loud.
    """
    out = shape.company_about_card(observed(CARD), company=EMPLOYER)
    assert out["size_band"] == "51-200"
    assert out["on_linkedin"] == 304
    assert str(out["on_linkedin"]) not in out["size_band"]


def test_a_sanitised_follower_count_is_null_and_never_zero():
    """The tracked ``following`` fixture spells its follower count ``NNN,NNN``.

    A parser that stripped non-digits would return 0 -- a number, wrong, and
    indistinguishable from a real zero. It returns None with a why instead,
    and the state says the answer is partial.
    """
    sanitised = list(CARD)
    sanitised[2] = "NNN,NNN followers"
    out = shape.company_about_card(observed(sanitised), company=EMPLOYER)
    assert out["followers"] is None
    assert out["state"] == "partial"
    assert "followers" in out["why"]


# ---------------------------------------------------------------------------
# 3. The description is counted and never published
# ---------------------------------------------------------------------------


def test_the_withholding_detector_can_find_something():
    """THE CONTROL FOR THE TEST BELOW, and it must run first.

    ``fields_carrying`` is asked to find a string that IS in the verdict --
    the employer's name, which the ``why`` quotes. A detector that cannot be
    shown finding anything certifies nothing when it finds nothing.
    """
    out = shape.company_about_card(observed(CARD), company=EMPLOYER)
    assert fields_carrying(out, EMPLOYER), out["why"]


def test_no_field_carries_the_description_text():
    out = shape.company_about_card(observed(CARD), company=EMPLOYER)
    assert fields_carrying(out, DESCRIPTION_ONLY_WORD) == []


def test_the_description_is_measured_even_though_it_is_withheld():
    """Withholding the prose is not the same as pretending it is not there.

    A company that wrote three paragraphs and one that wrote none are
    different employers, and the counts say which without saying what.
    """
    out = shape.company_about_card(observed(CARD), company=EMPLOYER)
    assert out["description_lines"] > 0
    assert out["description_chars"] > 0
    assert out["description_words"] > 0


def test_a_card_with_no_description_counts_zero():
    """The counts must be able to say "nothing", or they say nothing."""
    bare = CARD[:9]
    out = shape.company_about_card(observed(bare), company=EMPLOYER)
    assert out["state"] == "read"
    assert out["description_lines"] == 0
    assert out["description_words"] == 0


def test_the_collapse_marker_is_reported_so_the_count_is_not_read_as_a_length():
    with_more = shape.company_about_card(observed(CARD), company=EMPLOYER)
    without = shape.company_about_card(
        observed([x for x in CARD if x != "Show more"]), company=EMPLOYER
    )
    assert with_more["description_truncated"] is True
    assert without["description_truncated"] is False


def test_the_show_more_control_is_not_counted_as_description():
    """It is LinkedIn's chrome, not the company's prose."""
    out = shape.company_about_card(observed(CARD), company=EMPLOYER)
    assert fields_carrying(out, "Show more") == []


# ---------------------------------------------------------------------------
# 4. A write that has a surface and was not fired
# ---------------------------------------------------------------------------


def test_the_interest_control_is_reported_and_not_pressed():
    """``J 86`` / ``P I14`` -- "privately signal interest in a company".

    The census files it as a write with no surface. It HAS a surface, and it
    is on a page this server already loads. Reporting that is not firing it:
    this package offers no tool that presses it, and the flag exists because
    "no surface" and "a surface nobody has fired" are different rows.
    """
    out = shape.company_about_card(observed(CARD), company=EMPLOYER)
    assert out["interest_control"] is True
    without = shape.company_about_card(
        observed([x for x in CARD if not x.startswith(INTEREST_LABEL[:2])]), company=EMPLOYER
    )
    assert without["interest_control"] is False


def test_the_interest_control_is_matched_on_the_typographic_apostrophe():
    """LinkedIn draws U+2019, not U+0027. A literal would silently miss it."""
    straight = [x.replace(APOSTROPHE, chr(39)) for x in CARD]
    out = shape.company_about_card(observed(straight), company=EMPLOYER)
    assert out["interest_control"] is True


def test_the_interest_copy_is_not_mistaken_for_the_control():
    """LinkedIn's explanatory sentence sits directly above the button and
    contains the word "interested". Only the control itself counts."""
    copy_only = [x for x in CARD if not x.startswith(INTEREST_LABEL[:2])]
    out = shape.company_about_card(observed(copy_only), company=EMPLOYER)
    assert any("Interested in working with us" in x for x in copy_only)
    assert out["interest_control"] is False


# ---------------------------------------------------------------------------
# 5. The reader, over the frozen markup
# ---------------------------------------------------------------------------


async def _read(name: str):
    """Run the REAL reader over one committed fixture in a local Chromium."""
    playwright = pytest.importorskip("playwright.async_api")
    html = (FIXTURE_DIR / name).read_text(encoding="utf-8")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return await dom.read_company_about_card(page)
        finally:
            await browser.close()


@pytest.mark.parametrize("name", FILLED)
async def test_the_reader_finds_the_whole_card_on_a_filled_render(name):
    out = await _read(name)
    assert out["container"] is True
    assert out["sdui"] is True
    verdict = shape.company_about_card(out, company=EMPLOYER)
    assert verdict["state"] == "read", verdict["why"]
    assert verdict["followers"] == 5288656
    assert verdict["size_band"] == "51-200"
    assert verdict["on_linkedin"] == 304


async def test_the_skeleton_render_is_unhydrated_on_the_real_markup():
    """MEASUREMENT 2, on the page it was taken from.

    The container is there, the SDUI attribute is not, and there is no text.
    This is the case a container-only reader would have published as "this
    employer has no followers".
    """
    out = await _read(SKELETON)
    assert out["container"] is True
    assert out["sdui"] is False
    assert out["lines"] == []
    verdict = shape.company_about_card(out, company="Vantrex Systems")
    assert verdict["state"] == "unhydrated"


async def test_the_shell_render_has_no_card_at_all():
    out = await _read(SHELL)
    assert out["container"] is False
    verdict = shape.company_about_card(out, company=EMPLOYER)
    assert verdict["state"] == "absent"


async def test_the_followed_employers_card_reads_its_follow_state():
    out = await _read(FOLLOWED)
    verdict = shape.company_about_card(out, company="Vantrex Systems")
    assert verdict["follow_state"] == "Following"
    assert verdict["industry"] == "Technology, Information and Internet"
    assert verdict["size_band"] == "10001+"
    # The follower count on this capture is SANITISED, so it must come back
    # null with the state saying so -- not zero, and not a wrong number.
    assert verdict["followers"] is None
    assert verdict["state"] == "partial"


async def test_the_generic_card_harvest_cannot_reach_these_fields():
    """MEASUREMENT 1, ASSERTED RATHER THAN NARRATED.

    This is the test that justifies a dedicated reader existing at all. If a
    future change to ``HARVEST_LINKED_CARDS_JS`` ever makes the generic walk
    able to see the meta row, this goes red and somebody gets to delete a
    function instead of maintaining two.

    Eight hops is ``harvest_linked_cards``'s own default and the most generous
    setting the probe measured. Even there the ``/company/`` cards carry none
    of the three meta fields, because the walk stops on
    ``keysWithin(node).size > 1`` long before it reaches them.
    """
    playwright = pytest.importorskip("playwright.async_api")
    html = (FIXTURE_DIR / "job_detail_hydrated.html").read_text(encoding="utf-8")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            records = await dom.harvest_linked_cards(
                page, href_pattern="/company/", max_items=12, max_hops=8
            )
        finally:
            await browser.close()

    assert records, "the /company/ anchors are on the page; only the fields are not"

    # THE FIRST FORM OF THIS ASSERTION WAS WRONG AND THE FIXTURE SAID SO.
    # It read `"employees" not in text` and went red on the Premium insights
    # card, which is a DIFFERENT /company/ anchor and legitimately says
    # "Total employees: 288". The word was never the claim. The claim is that
    # the generic walk cannot deliver the ABOUT CARD'S META ROW -- the
    # declared size band together with the LinkedIn headcount -- so it is
    # asserted through the same two patterns the shaper matches with, and
    # then through the shaper itself.
    #
    # WORTH KNOWING WHILE YOU ARE HERE: that red exposed a THIRD employee
    # number on the same posting. The About card declares the band 51-200 and
    # counts 304 on LinkedIn; the Premium panel says 288 total. Three numbers,
    # three sources, no contradiction -- which is the whole argument for
    # size_band and on_linkedin being separate fields rather than one "size".
    for record in records:
        text = str(record.get("text") or "")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        has_band = any(shape._ABOUT_SIZE_BAND.match(line) for line in lines)
        has_head = any(shape._ABOUT_ON_LINKEDIN.match(line) for line in lines)
        assert not (has_band and has_head), record

        verdict = shape.company_about_card(
            {"container": True, "sdui": True, "lines": lines, "error": None},
            company=EMPLOYER,
        )
        assert verdict["state"] != "read", (record.get("href"), verdict)
