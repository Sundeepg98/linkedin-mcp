"""The Premium job-collection reader, run over real markup in a real page.

WHY THIS LOADS A BROWSER INSTEAD OF FAKING THE LOCATOR. The whole risk on this
surface is the AIM and the SCOPE, and a fake ``page`` returning canned counts
exercises the Python half while asserting nothing about either. This package
has already shipped one aim that resolved ZERO against a live DOM, and a live
load of ``/analytics/profile-views/`` parsed 12 rows document-wide and 0 inside
``main`` -- a reader looking in the wrong box, on this exact page family. A
reader whose selector is never executed is precisely the instrument this file
exists to refuse.

**AND THE THING THIS FILE IS TESTING HAS NEVER BEEN OPENED.**
``/jobs/collections/top-applicant`` and ``/jobs/collections/top-choice`` have
no capture. The fixture's structure is measured off their two captured
siblings. So these tests establish that the reader is correct ABOUT THE SHAPE
IT WAS BUILT FOR -- they do not and cannot establish that the target draws that
shape. The row stays GAP until the reader is fired live; see
``_audit/2026-09-20-the-premium-four.md``.

THE TWO TIERS ARE THE POINT OF HALF THIS FILE. LinkedIn draws one
``li[data-occludable-job-id]`` per posting placed in the list window and fills
only the few near the viewport: 24 slots and 7 cards on one captured sibling,
25 and 7 on the other. A reader counting cards reports 7 where the collection
holds 24, so ``slots`` and ``hydrated`` are asserted separately and asserted to
DIFFER -- an assertion that would pass vacuously on a fully-hydrated document,
which is why the fixture is not one.

Nothing here navigates to LinkedIn. ``set_content`` loads local markup into a
throwaway chromium context -- never the signed-in profile at
``_state/chrome-profile``, which a live wave may hold and which two processes
on one user-data-dir would corrupt.
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path

import pytest

from linkedin_server import job_collections

FIXTURE = Path(__file__).parent / "fixtures" / "synthetic" / "job_collection.html"

#: What the fixture draws. **MEASURED OFF THE FILE BY AN INDEPENDENT PARSE
#: BELOW, NEVER TRANSCRIBED** -- the discipline the newsletter and connections
#: fixtures already keep, because a number typed into a test is a number that
#: can disagree with the file it claims to describe.
EXPECTED_SLOTS_IN_MAIN = 10       # 9 well-formed + 1 whose id is not a digit run
EXPECTED_SLOTS_OUTSIDE = 1        # THE DECOY -- hydrated, so it decoys both tiers
EXPECTED_HYDRATED_IN_MAIN = 3
EXPECTED_HYDRATED_OUTSIDE = 1
EXPECTED_IDS = 9
EXPECTED_IDS_REFUSED = 1

#: The ONLY words the fixture is allowed to draw, and this file authors both.
#: Global nav chrome, not page content -- present so the document is shaped
#: like a page rather than like a list in a vacuum.
FIXTURE_VOCABULARY = frozenset({"home", "jobs"})


async def _open(html: str, factory):
    """Load markup into a real headless page and run ``factory`` over it."""
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1280, "height": 900})
            await page.set_content(
                html, wait_until="domcontentloaded", timeout=60_000
            )
            return await factory(page)
        finally:
            await browser.close()


async def _read(html: str | None = None, expect: int | None = 0):
    if html is None:
        html = FIXTURE.read_text(encoding="utf-8")

    async def factory(page):
        return await job_collections.read_job_collection(page, expect=expect)

    return await _open(html, factory)


def _markup() -> str:
    """The fixture with COMMENTS STRIPPED.

    Stripped first, and it is a red a sibling test caught on its own first run
    rather than a precaution: this fixture's header PROSE names the ``<main>``
    wrapper and the decoy it describes, so a bare ``find`` locates the word in
    the explanation and reports the decoy on the wrong side of the tag. A
    locator that can match documentation is not locating markup.
    """
    return re.sub(r"<!--.*?-->", "", FIXTURE.read_text(encoding="utf-8"), flags=re.S)


# ---------------------------------------------------------------------------
# 1. The fixture describes itself, so the numbers above are not transcriptions
# ---------------------------------------------------------------------------


def test_the_fixture_puts_exactly_one_slot_outside_main_and_it_is_hydrated():
    """THE DECOY IS LOAD-BEARING, so the file is asserted to still carry it.

    If somebody tidies the decoy away, every scoping assertion below keeps
    passing while testing nothing -- this repository's own definition of a
    check that certifies nothing. It must decoy BOTH tiers, so it is asserted
    to carry a slot id AND a card id.
    """
    markup = _markup()
    opens_main = markup.find("<main>")
    assert opens_main > 0, "the fixture lost its <main> wrapper"

    for attribute, outside, inside in (
        ("data-occludable-job-id", EXPECTED_SLOTS_OUTSIDE, EXPECTED_SLOTS_IN_MAIN),
        ("data-job-id", EXPECTED_HYDRATED_OUTSIDE, EXPECTED_HYDRATED_IN_MAIN),
    ):
        needle = re.escape(attribute + '="')
        before = len(re.findall(needle, markup[:opens_main]))
        after = len(re.findall(needle, markup[opens_main:]))
        assert before == outside, (attribute, before, outside)
        assert after == inside, (attribute, after, inside)


def test_the_fixture_is_two_tiered_and_most_slots_draw_no_card():
    """THE WHOLE REASON THE READER COUNTS TIER 1.

    If a future edit hydrated every slot, the tier distinction would have no
    reaching input and a reader that confused the two would pass every other
    test in this file. Measured on the captures: 7 of 24 and 7 of 25.
    """
    inner = _markup().split("<main>", 1)[-1].split("</main>", 1)[0]
    slots = len(re.findall(r'data-occludable-job-id="', inner))
    cards = len(re.findall(r'(?<!occludable-)data-job-id="', inner))
    assert slots == EXPECTED_SLOTS_IN_MAIN
    assert cards == EXPECTED_HYDRATED_IN_MAIN
    assert cards < slots, "every slot is hydrated, so the tiers cannot diverge"


def test_the_fixture_carries_exactly_one_slot_id_that_is_not_a_digit_run():
    """The shape gate needs a reaching input or its branch is untested."""
    ids = re.findall(r'data-occludable-job-id="([^"]*)"', _markup())
    bad = [value for value in ids if not job_collections.JOB_ID_SHAPE.match(value)]
    assert len(bad) == EXPECTED_IDS_REFUSED, bad


def test_every_hydrated_card_id_equals_its_slot_id():
    """Cross-tier equality, measured 7 of 7 on both captures with zero
    mismatches. If the two ever disagreed, reading ids off the slot tier would
    be substituting one identifier for another rather than reaching more of
    the same one -- which is a different and much larger claim."""
    for slot_id, body in re.findall(
        r'<li data-occludable-job-id="([^"]*)"(.*?)</li>', _markup(), flags=re.S
    ):
        for card_id in re.findall(r'(?<!occludable-)data-job-id="([^"]*)"', body):
            assert card_id == slot_id, (slot_id, card_id)


def test_the_fixture_draws_nothing_but_two_words_this_file_authors():
    """There is nothing to redact here because nothing of LinkedIn's is present.

    Asserted as an ALLOWLIST rather than as "no text": the first version of
    this test demanded the document be textless, which the two nav labels duly
    failed. **A refusal that reports only what it did not match is half a
    measurement** -- so this reports the vocabulary it DID find and fails on
    anything outside it. A future edit pasting a real job title lands here.
    """
    body = _markup().split("<body>", 1)[-1]
    words = set(re.findall(r"[A-Za-z]+", re.sub(r"<[^>]+>", " ", body)))
    unexpected = {word for word in words if word.lower() not in FIXTURE_VOCABULARY}
    assert unexpected == set(), sorted(unexpected)


def test_the_list_region_itself_carries_no_text_at_all():
    """THE STRICTER HALF, where it actually matters. ``main`` holds the list,
    and a job title or company name could only arrive inside one."""
    inner = _markup().split("<main>", 1)[-1].split("</main>", 1)[0]
    stripped = re.sub(r"<[^>]+>", "", inner)
    assert stripped.strip() == "", repr(stripped[:200])


# ---------------------------------------------------------------------------
# 2. The two tiers, and the scope pairs that are the whole point of them
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_the_reader_counts_slots_inside_main_and_the_decoy_outside():
    """ONE OUTSIDE, TEN INSIDE. A document-wide counter reports 11 and 0."""
    out = await _read()
    assert out["error"] is None
    assert out["refusal"] is None
    assert out["slots"] == EXPECTED_SLOTS_IN_MAIN
    assert out["slots_outside_main"] == EXPECTED_SLOTS_OUTSIDE
    assert out["list_container_seen"] is True


@pytest.mark.asyncio
async def test_slots_is_the_answer_and_hydrated_is_published_beside_it():
    """THE 3.4x UNDERCOUNT THIS PAIR EXISTS TO PREVENT.

    A reader publishing ``hydrated`` as the posting count reports 7 where the
    captured siblings hold 24 and 25. The two never share a field, and this
    asserts they are actually DIFFERENT on the fixture -- an assertion that
    would pass vacuously on a fully-hydrated document.
    """
    out = await _read()
    assert out["hydrated"] == EXPECTED_HYDRATED_IN_MAIN
    assert out["hydrated_outside_main"] == EXPECTED_HYDRATED_OUTSIDE
    assert out["hydrated"] < out["slots"], (out["hydrated"], out["slots"])


@pytest.mark.asyncio
async def test_a_window_of_pure_placeholders_is_a_populated_list_not_a_miss():
    """THE CASE A CARD-TIER READER CALLS EMPTY AND A SLOT-TIER READER COUNTS.

    LinkedIn hydrates only what is near the viewport, so a list read before any
    card renders draws slots and zero cards. That is a fully populated list,
    and a reader blind to tier 1 would report it as nothing at all.
    """
    html = (
        "<html><body><main><ul>"
        + "".join('<li data-occludable-job-id="100000000%d"></li>' % n
                  for n in range(1, 6))
        + "</ul></main></body></html>"
    )
    out = await _read(html)
    assert out["slots"] == 5
    assert out["hydrated"] == 0
    assert out["containers"] == 0
    assert out["list_container_seen"] is True
    assert out["refusal"] is None
    assert len(out["job_ids"]) == 5


@pytest.mark.asyncio
async def test_the_naive_document_wide_selector_is_shown_getting_it_wrong(monkeypatch):
    """THE MUTATION, PLANTED AND SHOWN FIRING, not described in a comment.

    A check that has only ever been seen passing certifies nothing. So the
    obvious wrong implementation -- count the whole document -- is installed
    here and MEASURED: it reports ELEVEN slots in main and ZERO outside,
    against the shipped reader's ten and one.

    **THIS ASSERTION IS THE ONLY REASON THE DECOY EXISTS**, because on the two
    real captures every candidate selector agrees exactly across the two
    scopes: 24 == 24, 25 == 25, 7 == 7 and 7 == 7. A scoping claim proved
    against those captures alone would be proving nothing.
    """
    monkeypatch.setattr(
        job_collections, "SLOT_SELECTOR", job_collections.SLOT_SELECTOR_ANYWHERE
    )
    monkeypatch.setattr(
        job_collections, "CARD_SELECTOR", job_collections.CARD_SELECTOR_ANYWHERE
    )
    naive = await _read()
    assert naive["slots"] == EXPECTED_SLOTS_IN_MAIN + EXPECTED_SLOTS_OUTSIDE
    assert naive["slots_outside_main"] == 0
    assert naive["hydrated"] == EXPECTED_HYDRATED_IN_MAIN + EXPECTED_HYDRATED_OUTSIDE
    assert naive["hydrated_outside_main"] == 0
    # AND IT CORRUPTS THE PAYLOAD, not only the count: the decoy's posting id
    # is now published as though it were one of his.
    assert len(naive["job_ids"]) == EXPECTED_IDS + 1


@pytest.mark.asyncio
async def test_the_container_selector_is_counted_in_both_scopes_too():
    """Three selectors, six numbers. A future deploy dropping an attribute
    makes them diverge instead of returning a silent zero."""
    out = await _read()
    assert out["containers"] == EXPECTED_HYDRATED_IN_MAIN
    assert out["containers_outside_main"] == EXPECTED_HYDRATED_OUTSIDE


# ---------------------------------------------------------------------------
# 3. The one page-derived value, and its gate
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_only_digit_runs_are_published_and_the_rest_are_counted():
    out = await _read()
    assert len(out["job_ids"]) == EXPECTED_IDS
    assert out["ids_refused"] == EXPECTED_IDS_REFUSED
    assert all(value.isdigit() for value in out["job_ids"]), out["job_ids"]


@pytest.mark.asyncio
async def test_the_ids_come_from_the_slot_tier_so_unhydrated_postings_are_reached():
    """NINE IDS FROM THREE CARDS. A card-tier reader returns three.

    This is the capability difference stated as a number: the slot tier yields
    an id for every posting, the card tier only for those LinkedIn happened to
    have drawn.
    """
    out = await _read()
    assert len(out["job_ids"]) == EXPECTED_IDS
    assert out["hydrated"] == EXPECTED_HYDRATED_IN_MAIN
    assert len(out["job_ids"]) > out["hydrated"]


@pytest.mark.asyncio
async def test_no_non_numeric_string_from_the_document_reaches_the_caller():
    """Asserted over the WHOLE returned structure rather than over one field,
    because a leak would arrive somewhere nobody was watching."""
    blob = repr(await _read())
    assert "see-job-details" not in blob
    assert "job-card-container" not in blob
    assert "scaffold" not in blob
    assert "occludable" not in blob


@pytest.mark.asyncio
async def test_a_slot_whose_id_is_a_title_produces_a_refusal_not_a_title():
    """THE GATE'S REASON, planted as its own document.

    The failure this prevents is a page that puts a job title where the id
    goes. The reader must then hand its caller a COUNT, never the title.
    """
    html = (
        '<html><body><main><ul><li data-occludable-job-id='
        '"Senior Engineer at Some Company"></li></ul></main></body></html>'
    )
    out = await _read(html)
    assert out["job_ids"] == []
    assert out["ids_refused"] == 1
    assert "Senior" not in repr(out)
    assert "Company" not in repr(out)


# ---------------------------------------------------------------------------
# 4. A ZERO AND A PARSE MISS NEVER SHARE A FIELD
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_a_page_with_no_list_at_all_reports_zero_beside_a_dead_control():
    """ZERO WITHOUT THE CONTROL IS UNINTERPRETABLE, which is how this surface
    family produced a confident wrong answer once already.

    No slot, no card, no container: the zero is a fact about THE READER and
    the refusal says so by name.
    """
    html = "<html><body><main><div>some other page entirely</div></main></body></html>"
    out = await _read(html)
    assert out["slots"] == 0
    assert out["hydrated"] == 0
    assert out["list_container_seen"] is False
    assert out["refusal"] == "no_card_container_drawn"


@pytest.mark.asyncio
async def test_an_empty_collection_that_draws_its_list_is_a_fact_about_him():
    """The OTHER zero. The list is drawn, so whatever it holds is his -- and
    the refusal stays None, because this is not a refusal."""
    html = (
        '<html><body><main><ul><li data-occludable-job-id="1000000001">'
        "</li></ul></main><aside></aside></body></html>"
    )
    out = await _read(html)
    assert out["list_container_seen"] is True
    assert out["refusal"] is None
    assert out["slots"] == 1


@pytest.mark.asyncio
async def test_an_empty_state_message_is_counted_and_never_returned():
    """What the page SAID when it drew nothing, as a number.

    A page that says "nothing here" and a page that says nothing at all are
    different findings -- the role-play listing served, rendered 17 characters
    in ``main`` and drew NO empty-state message, and that silence was the
    finding.
    """
    html = (
        "<html><body><main><p>No results found. Try again later.</p>"
        "</main></body></html>"
    )
    out = await _read(html)
    assert out["slots"] == 0
    assert out["list_container_seen"] is False
    assert out["empty_state_needles"] >= 2
    assert "No results" not in repr(out)


@pytest.mark.asyncio
async def test_a_silent_empty_page_is_distinguishable_from_a_talking_one():
    """THE DISCRIMINATION, which is what makes the needle count worth a field.

    Both pages draw zero postings. One says why and one does not, and the
    reader returns different numbers for them.
    """
    talking = await _read(
        "<html><body><main><p>Nothing here yet</p></main></body></html>"
    )
    silent = await _read("<html><body><main></main></body></html>")
    assert talking["slots"] == silent["slots"] == 0
    assert talking["empty_state_needles"] > silent["empty_state_needles"]
    assert silent["empty_state_needles"] == 0


# ---------------------------------------------------------------------------
# 5. A partial reading is worse than none
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_a_detached_frame_resets_every_field_rather_than_keeping_some():
    """Counts taken before an exception would otherwise sit beside an error
    saying nothing was measured, and nothing downstream could tell."""

    class Exploding:
        def locator(self, _selector):
            raise RuntimeError("frame was detached")

    out = await job_collections.read_job_collection(Exploding(), expect=0)
    assert out["error"] == "RuntimeError: frame was detached"
    assert out["slots"] == 0
    assert out["slots_outside_main"] == 0
    assert out["hydrated"] == 0
    assert out["hydrated_outside_main"] == 0
    assert out["containers"] == 0
    assert out["containers_outside_main"] == 0
    assert out["job_ids"] == []
    assert out["ids_refused"] == 0
    assert out["empty_state_needles"] == 0
    assert out["list_container_seen"] is False
    assert out["refusal"] is None


@pytest.mark.asyncio
async def test_an_exception_after_the_counts_still_clears_them():
    """SHOWN, not assumed: the reset must survive a failure that happens LATE.

    The detached-frame case fails on the FIRST locator call, so it would pass
    even if the reset were only the initialisation at the top of the function.
    This one fails on the ``main`` locator, reached after six successful counts
    and after the whole id loop -- so populated fields have to be cleared, not
    zeroed ones left alone.
    """

    async def factory(page):
        real = page.locator

        def locator(selector):
            if selector == "main":
                raise RuntimeError("navigated away mid-read")
            return real(selector)

        page.locator = locator
        return await job_collections.read_job_collection(page, expect=0)

    out = await _open(FIXTURE.read_text(encoding="utf-8"), factory)
    assert out["error"].startswith("RuntimeError")
    assert out["slots"] == 0
    assert out["hydrated"] == 0
    assert out["containers"] == 0
    assert out["job_ids"] == []
    assert out["ids_refused"] == 0


# ---------------------------------------------------------------------------
# 6. The alphabet, the signatures, and the refusal to clamp
# ---------------------------------------------------------------------------


def test_the_collection_vocabulary_is_pinned_in_order():
    """Reordering renames every reading ever taken, so the order is pinned.

    ``recommended`` was APPENDED on 2026-09-23 (census ``J 39``): indices 0 and
    1 still name what they always named, which is the only way a third entry
    could join without renaming a reading already taken.
    """
    assert job_collections.COLLECTIONS == (
        "top-applicant", "top-choice", "recommended")


def test_collection_url_refuses_out_of_range_rather_than_clamping():
    """A clamp would file a reading under the wrong collection -- a wrong
    answer wearing a measurement's clothes."""
    assert job_collections.collection_url(0).endswith("/top-applicant/")
    assert job_collections.collection_url(1).endswith("/top-choice/")
    assert job_collections.collection_url(2).endswith("/recommended/")
    with pytest.raises(IndexError):
        job_collections.collection_url(3)
    with pytest.raises(IndexError):
        job_collections.collection_url(-1)
    with pytest.raises(TypeError):
        job_collections.collection_url(True)


def test_every_address_this_module_can_build_is_on_the_read_allowlist():
    """THE SHAPER AND THE BOUNDARY AGREE, address for address.

    Imported predicate, never a re-implementation: this repository has twice
    reached a wrong answer by reading pattern text instead of running the
    check. A divergence here means either the entry opens something this
    module would refuse, or this module builds something the entry refuses --
    and the groups coupling test caught exactly that on its first run.
    """
    from linkedin_server import readonly

    for index in range(len(job_collections.COLLECTIONS)):
        url = job_collections.collection_url(index)
        assert readonly.is_read_url(url) is True, url
        assert readonly.is_read_url(url.rstrip("/")) is True, url


def test_no_label_or_href_is_a_parameter_of_any_function_here():
    """A property stated only in prose is the defect this repository has
    recorded more than once, so it is asserted on the signatures."""
    for name in ("collection_url", "term_for"):
        params = list(inspect.signature(getattr(job_collections, name)).parameters)
        assert params == ["index"], (name, params)
    reader = inspect.signature(job_collections.read_job_collection).parameters
    assert list(reader) == ["page", "expect"], list(reader)


@pytest.mark.asyncio
async def test_the_published_alphabet_is_closed_over_adversarial_input():
    """Every non-numeric string the reader emits must be a literal of the
    module. A new literal added without a thought fails here."""
    allowed = job_collections.emitted_alphabet()
    for html in (
        FIXTURE.read_text(encoding="utf-8"),
        "<html><body><main><p>Nothing here</p></main></body></html>",
        '<html><body><main><ul><li data-occludable-job-id="a title">'
        "</li></ul></main></body></html>",
    ):
        out = await _read(html)
        for key in ("collection", "refusal"):
            value = out[key]
            if value is not None:
                assert value in allowed, (key, value)


@pytest.mark.asyncio
async def test_an_out_of_range_expectation_refuses_rather_than_reading():
    """``expect`` is an index and a bad one is a caller bug, so it refuses
    BEFORE touching the page rather than filing a reading under nothing.

    The page raises if touched, so this asserts the ORDER of the two checks
    and not merely the returned value.
    """

    class NeverTouched:
        def locator(self, _selector):  # pragma: no cover -- must not run
            raise AssertionError("the page was read despite a bad index")

    out = await job_collections.read_job_collection(NeverTouched(), expect=99)
    assert out["refusal"] == "index_out_of_range"
    assert out["collection"] is None
    assert out["error"] is None


# ---------------------------------------------------------------------------
# 7. The control fixture must fire, and must discriminate
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_the_control_fixture_produces_its_known_reading():
    """THE POSITIVE CONTROL. A zero from this reader on a live surface is two
    findings -- the collection is empty, or the shape is not what the two
    captured siblings drew -- and nothing in the reading separates them. This
    is what a run that CAN see looks like.
    """
    out = await _read(job_collections.control_fixture(), expect=1)
    assert out["collection"] == "top-choice"
    assert out["slots"] == 4          # 2 hydrated + 1 placeholder + 1 bad id
    assert out["slots_outside_main"] == 1
    assert out["hydrated"] == 2
    assert out["hydrated_outside_main"] == 1
    assert out["job_ids"] == ["1000000001", "1000000002", "1000000003"]
    assert out["ids_refused"] == 1
    assert out["list_container_seen"] is True
    assert out["refusal"] is None


def test_the_control_fixture_carries_its_decoy_outside_main():
    """The control is only a control while its decoy survives, and the decoy
    is only a both-tier decoy while it stays hydrated."""
    html = job_collections.control_fixture()
    opens_main = html.find("<main>")
    assert opens_main > 0
    head = html[:opens_main]
    assert 'data-occludable-job-id="1000000099"' in head
    assert 'data-job-id="1000000099"' in head


# ---------------------------------------------------------------------------
# 8. The recommended collection: index 2, read over a skeleton of its capture
# ---------------------------------------------------------------------------
#
# NO MODULE-LEVEL CONSTANT IS ADDED FOR THIS SECTION, deliberately: the impact
# gate couples every file that NAMES an upper-case constant defined here, and a
# word like SKELETON is exactly the kind a docstring elsewhere might carry.


def _skeleton_path() -> Path:
    return Path(__file__).parent / "fixtures" / "synthetic" / "jobs_recommended_skeleton.html"


def _skeleton_markup() -> str:
    """The skeleton with its provenance COMMENT stripped, for the same reason
    ``_markup`` strips the synthetic fixture's: prose about a tag is not one."""
    text = _skeleton_path().read_text(encoding="ascii")
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def test_the_recommended_skeleton_describes_itself():
    """THE NUMBERS BELOW ARE MEASURED OFF THE FILE, NEVER TRANSCRIBED.

    ``scripts/_build_job_list_skeleton.py`` built it from the live capture of
    ``/jobs/collections/recommended/`` and measured 24 slots, 7 of them
    hydrated, every card id equal to its slot id and no slot outside main --
    the same figures ``job_collections``' own docstring table records for that
    page. An independent parse here re-derives them from the committed bytes.
    """
    markup = _skeleton_markup()
    slots = re.findall(r'data-occludable-job-id="([^"]*)"', markup)
    cards = re.findall(r'data-job-id="([^"]*)"', markup)
    assert len(slots) == 24
    assert len(cards) == 7
    assert cards == slots[:7], "the captured order put every card first"
    assert all(re.fullmatch(r"[0-9]{10}", s) for s in slots)
    assert len(set(slots)) == 24
    inner = markup.split("<main>", 1)[-1].split("</main>", 1)[0]
    assert re.sub(r"<[^>]+>", "", inner).strip() == "", "the skeleton drew text"


@pytest.mark.asyncio
async def test_index_two_reads_the_recommended_skeleton_as_measured():
    """THE ROW'S CAPABILITY, OFFLINE: posting ids off the recommended list.

    Census ``J 39`` -- read job recommendations -- asks for the postings
    LinkedIn recommends, and ``linkedin_job_collections`` deliberately returns
    only their COUNT. Index 2 returns the ids, each a digit run
    ``linkedin_job_detail`` accepts. ``slots`` is the answer and ``hydrated``
    sits beside it: 24 against 7, the 3.4x gap this module exists to report.
    """
    html = _skeleton_path().read_text(encoding="ascii")
    out = await _read(html, expect=2)
    assert out["collection"] == "recommended"
    assert out["error"] is None and out["refusal"] is None
    assert out["slots"] == 24 and out["slots_outside_main"] == 0
    assert out["hydrated"] == 7 and out["containers"] == 7
    assert out["list_container_seen"] is True
    assert out["ids_refused"] == 0
    assert out["job_ids"] == re.findall(
        r'data-occludable-job-id="([^"]*)"', _skeleton_markup())


def test_the_recommended_index_aims_at_the_page_the_counts_tool_opens():
    """ONE PAGE, TWO READERS, AND THEY CANNOT DRIFT APART.

    ``linkedin_job_collections`` COUNTS ``collections_page.COLLECTIONS_URL`` and
    was fired live on it; index 2 returns that page's posting ids. If either
    constant moved alone, the ids would describe a different page from the one
    whose counts have been proven.
    """
    from linkedin_server import collections_page

    assert job_collections.collection_url(2) == collections_page.COLLECTIONS_URL
