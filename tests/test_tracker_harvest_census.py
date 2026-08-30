"""What the card walk threw away, and where a tracker row's text actually is.

WHAT WAS WRONG. On 2026-08-30 ``linkedin_saved_jobs`` refused eight times out
of eight, across two server restarts and two hours, with byte-identical
numbers: LinkedIn's Saved tab reading 1, a ``<main>`` carrying 256 characters,
8 links, 4 of them job-row links -- and zero rows. The refusal could say the
loss was "the card walk or the row parser" and could not choose between them.

That is one integer's worth of ignorance and the caller already held it.
``_read_tracker`` computes ``rows, dropped = parse_all(records, ...)`` and threw
``len(records)`` away. Zero records means the WALK lost them; N records with N
dropped means the PARSER did. They fail in different files.

A HYPOTHESIS DIED HERE AND IT IS WORTH RECORDING. Part 2 of the audit proposed
that the rows were drawn but not painted, and that ``record()`` -- which
returns null for an empty ``innerText`` -- was discarding them. Measured
offline, that is FALSE: per the HTML spec, ``innerText`` on an element that is
not being rendered returns its ``textContent``, so a ``display:none`` row
harvests perfectly. ``test_a_hidden_row_still_harvests`` pins it, because it is
the reason the obvious fix would have been the wrong one.

WHAT THIS MODULE ADDS is three instruments, not a repair:

* ``dom.harvest_census`` -- the same walk under a flag, reporting how many
  keyed anchors it considered and how many it discarded for empty text. Not a
  second implementation: a separate counter is free to disagree with the thing
  it counts.
* ``dom.read_tracker_row_shape`` -- the climb from each row anchor, in tag
  names and character counts and nothing else, saying at which level text
  appears and whether it is rendered.
* the two numbers the refusal was already holding.

Every reading below is taken by the REAL reader over a REAL parsed DOM in a
local headless Chromium. Nothing here reaches the network or an account. Pages
are DERIVED from the two tracker captures by explicit, asserted edits, and are
models of a state -- never evidence about LinkedIn.

EVERY TEST HERE WAS SHOWN FAILING at the mutation named in its docstring.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from linkedin_server import dom, shape

FIXTURE_DIR = Path(__file__).parent / "fixtures"

#: The live signature this module exists to model, measured 8 times on
#: 2026-08-30 through two processes. Kept as data so a test that stops matching
#: it is visible rather than quietly drifting.
LIVE = {"main_chars": 256, "anchors_total": 8, "rows_matching": 4, "records": 0}


def markup(which: str) -> str:
    return (FIXTURE_DIR / f"{which}.html").read_text(encoding="ascii")


def derive(src: str, old: str, new: str, *, count: int = 1) -> str:
    out = src.replace(old, new, count)
    assert out != src, (
        f"the derivation anchored on {old!r} changed nothing, so this variant "
        "is the base fixture wearing another name. Repoint the anchor, and do "
        "NOT delete this assertion."
    )
    return out


def wrapped_rows(style: str) -> str:
    """DERIVED: the row capture with its whole body inside a styled element."""
    out = derive(markup("jobs_tracker_row"), "<main>", f'<main><div style="{style}">')
    return derive(out, "</main>", "</div></main>")


def hidden_rows() -> str:
    return wrapped_rows("display:none")


def bare_anchors() -> str:
    """DERIVED: the live signature -- job-row links wrapping NO text.

    Built on the SHELL (tab strip says 1, no empty state) so the only thing
    separating it from a legitimately unreadable page is the rows themselves.
    """
    shell = derive(markup("jobs_tracker_empty"), ">No jobs here</h2>", "></h2>")
    shell = derive(shell, "Saved &#183; 0", "Saved &#183; 1", count=-1)
    links = "".join(
        f'<a href="https://www.linkedin.com/jobs/view/40112233{n:02d}/"></a>'
        for n in range(2)
    )
    return derive(shell, "</main>", f"<div><div>{links}</div></div></main>")


async def _with_html(html: str, work):
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        chromium = await pw.chromium.launch(headless=True)
        try:
            page = await chromium.new_page()
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return await work(page)
        finally:
            await chromium.close()


async def _harvest(page):
    records = await dom.harvest_linked_cards(
        page, href_pattern=dom.JOB_HREF, max_items=75
    )
    rows, dropped = dom.parse_all(records, shape.parse_job_card)
    return records, rows, dropped


# ---------------------------------------------------------------------------
# 1. The hypothesis that died
# ---------------------------------------------------------------------------


async def test_a_hidden_row_still_harvests():
    """A row in the DOM and not painted is NOT what breaks the harvest.

    THIS TEST EXISTS TO STOP A FIX THAT WOULD HAVE BEEN WRONG. The audit's
    Part 2 reasoned that ``record()``'s empty-innerText guard was discarding
    unpainted rows, and the obvious repair -- fall back to ``textContent`` --
    would have changed behaviour every other surface depends on, to cure a
    disease this page does not have.

    Per the HTML spec, ``innerText`` on an element that is NOT being rendered
    returns the same value as ``textContent``. So the walk reads a hidden row
    exactly as it reads a shown one.

    SHOWN FAILING by hiding the rows with ``visibility: hidden`` instead of
    ``display: none``, which keeps the element rendered and therefore really
    does empty its innerText::

        AssertionError: assert 0 == 1
        -- the harvest lost a row that was merely invisible
    """

    async def work(page):
        return await _harvest(page)

    records, rows, dropped = await _with_html(hidden_rows(), work)
    assert len(records) == 1, (records, rows, dropped)
    assert len(rows) == 1, (records, rows, dropped)


async def test_a_visibility_hidden_row_is_what_ACTUALLY_breaks_the_harvest():
    """The other kind of hidden, and the two are opposite here.

    THE MOST USEFUL FACT THIS MODULE ESTABLISHES, and it is the difference
    between the two CSS ways of hiding something:

        display: none       the element is NOT rendered, so innerText falls
                            back to textContent and the walk reads it fine.
        visibility: hidden  the element IS rendered -- it still has a box --
                            and the rendered-text collection skips it, so
                            innerText is EMPTY and record() drops the row.

    Measured, not reasoned, over the same capture under each wrapper:

        no wrapper           records=1  dropped_empty=0
        display:none         records=1  dropped_empty=0
        visibility:hidden    records=0  dropped_empty=1

    WHY IT MATTERS TO THE LIVE DEFECT. The Saved tab produces exactly the
    right-hand signature -- job-row anchors present, zero records -- and this
    is one of the two states that produce it. The other is a row carrying no
    text at all. ``dom.read_tracker_row_shape`` is what separates them: within
    the row, 0 rendered against 0 present is an empty row, and 0 rendered
    against N present is this.

    SHOWN FAILING by wrapping in ``display:none`` instead, which is the whole
    point of the pair::

        AssertionError: assert 1 == 0
        -- display:none does not break the harvest, so this proves nothing
    """

    async def work(page):
        records, rows, dropped = await _harvest(page)
        census = await dom.harvest_census(
            page, href_pattern=dom.JOB_HREF, max_items=75
        )
        return records, rows, census

    records, rows, census = await _with_html(
        wrapped_rows("visibility:hidden"), work
    )
    assert len(records) == 0, records
    assert len(rows) == 0, rows
    assert census["anchors_keyed"] == 1, census
    assert census["dropped_empty_text"] == 1, census


# ---------------------------------------------------------------------------
# 2. The census -- which of the two stages lost the rows
# ---------------------------------------------------------------------------


async def test_the_census_names_the_walk_when_the_walk_is_what_dropped_them():
    """Anchors considered, and every one discarded for carrying no text.

    This is the live signature modelled: keyed anchors present, zero records.
    Before the census, that state and "the page offered no anchor at all" were
    the same empty list.

    SHOWN FAILING by having the census count anchors it kept rather than
    anchors it considered::

        AssertionError: assert 0 == 2
        -- a walk that discarded everything reported considering nothing
    """

    async def work(page):
        records, _rows, _dropped = await _harvest(page)
        census = await dom.harvest_census(
            page, href_pattern=dom.JOB_HREF, max_items=75
        )
        return records, census

    records, census = await _with_html(bare_anchors(), work)
    assert len(records) == 0, records
    assert census["anchors_keyed"] == 2, census
    assert census["dropped_empty_text"] == 2, census


async def test_the_census_agrees_with_the_walk_it_describes():
    """It runs the SAME script, so it cannot report a different world.

    A separate counting routine would be free to disagree with the walk it
    counts, which is how a diagnostic starts lying. Driven over the capture
    that works, the census's kept rows must be the harvest's rows.

    SHOWN FAILING by pointing the census at a different href pattern::

        AssertionError: assert 0 == 1
    """

    async def work(page):
        records, _rows, _dropped = await _harvest(page)
        census = await dom.harvest_census(
            page, href_pattern=dom.JOB_HREF, max_items=75
        )
        return records, census

    records, census = await _with_html(markup("jobs_tracker_row"), work)
    assert len(census["rows"]) == len(records) == 1, (census, records)
    assert census["dropped_empty_text"] == 0, census


async def test_a_census_that_could_not_run_reports_unknown_not_zero():
    """An instrument failure must not look like a page that offered nothing.

    SHOWN FAILING by initialising the counters to 0::

        AssertionError: assert 0 is None
        -- a census that never ran claimed the page had no anchors
    """

    class Unreadable:
        async def evaluate(self, script, arg=None):
            raise RuntimeError("browser is gone")

    census = await dom.harvest_census(
        Unreadable(), href_pattern=dom.JOB_HREF, max_items=75
    )
    assert census["anchors_keyed"] is None, census
    assert census["dropped_empty_text"] is None, census
    assert census["rows"] == [], census


# ---------------------------------------------------------------------------
# 3. The row's shape -- where the text is, in integers
# ---------------------------------------------------------------------------


async def test_the_row_shape_finds_no_text_inside_a_bare_anchor():
    """The climb, bounded at the row, over a link wrapping nothing.

    SHOWN FAILING by taking the verdict over the WHOLE climb instead of
    stopping at the container -- which is what the first draft did, and it
    reported the page's own chrome as the row's text::

        AssertionError: assert 310 == 0
        -- <main>'s tab strip was counted as the row's content
    """

    async def work(page):
        return await dom.read_tracker_row_shape(page)

    shapes = await _with_html(bare_anchors(), work)
    assert shapes, shapes
    within = [lvl for lvl in shapes[0] if int(lvl["keys"]) <= 1]
    assert within, shapes[0]
    assert max(lvl["content_chars"] for lvl in within) == 0, within
    # And the level ABOVE the row does carry chrome, which is exactly why the
    # bound is necessary rather than tidy.
    assert max(lvl["content_chars"] for lvl in shapes[0]) > 0, shapes[0]


async def test_the_row_shape_finds_the_text_on_a_row_that_has_some():
    """The control. Without it every assertion above passes on a reader that
    always returns zero.

    SHOWN FAILING by reporting ``content_chars`` as 0 unconditionally::

        AssertionError: assert 0 > 0
    """

    async def work(page):
        return await dom.read_tracker_row_shape(page)

    shapes = await _with_html(markup("jobs_tracker_row"), work)
    assert shapes, shapes
    within = [lvl for lvl in shapes[0] if int(lvl["keys"]) <= 1]
    assert max(lvl["content_chars"] for lvl in within) > 0, within


async def test_the_row_shape_reports_no_text_of_its_own():
    """TAG NAMES AND INTEGERS ONLY. A tracker row names a company and a job.

    The save sweep took this ruling for the same reason; this is a second path
    by which a row's contents could reach a reader, so the guard has to hold
    on it too.

    SHOWN FAILING by adding the node's text to each level::

        AssertionError: 'Ashgrove Systems' leaked out of the row shape
    """

    async def work(page):
        return await dom.read_tracker_row_shape(page)

    shapes = await _with_html(markup("jobs_tracker_row"), work)
    rendered = str(shapes)
    for secret in ("Ashgrove", "Platform Integration", "Fairhaven", "Luxoft"):
        assert secret not in rendered, f"{secret!r} leaked out of the row shape"
    # Nor may it reach the sentence built from it.
    note = shape.tracker_read_note(
        {}, {"attached": True, "waited_ms": 1}, {}, row_shape=shapes
    )
    for secret in ("Ashgrove", "Platform Integration", "Fairhaven"):
        assert secret not in note, f"{secret!r} leaked into the refusal note"


# ---------------------------------------------------------------------------
# 4. The sentences, over the state that produced them
# ---------------------------------------------------------------------------


async def test_the_note_names_the_walk_and_the_empty_row():
    """The whole refusal, over the modelled live signature.

    SHOWN FAILING by dropping ``records`` from the note's arguments, which is
    the state this wave found the refusal in::

        AssertionError: 'THE CARD WALK RETURNED NOTHING' not in '... that is
        the card walk or the row parser ...'
        -- the refusal still cannot choose between the two
    """

    async def work(page):
        evidence = await dom.read_tracker_evidence(page)
        records, _rows, dropped = await _harvest(page)
        census = await dom.harvest_census(
            page, href_pattern=dom.JOB_HREF, max_items=75
        )
        shapes = await dom.read_tracker_row_shape(page)
        wait = await dom.wait_for_tracker_list(page)
        return shape.tracker_read_note(
            evidence,
            wait,
            {"branch": "networkidle_timed_out", "settled_ms": 7011},
            records=len(records),
            dropped=dropped,
            census=census,
            row_shape=shapes,
        )

    note = await _with_html(bare_anchors(), work)
    assert "THE CARD WALK RETURNED NOTHING" in note, note
    assert "discarded ALL 2 for carrying no text" in note, note
    assert "NO LEVEL WITHIN THE ROW" in note, note
    assert "addressable link around nothing" in note, note
    # And it must NOT send the reader to the walk, which is the wrong file.
    assert "the repair is NOT in the walk" in note, note


async def test_the_note_says_parser_when_the_parser_is_what_dropped_them():
    """The other branch, and it must not borrow the first one's sentence.

    SHOWN FAILING by using the same wording for both::

        AssertionError: 'THE CARD WALK RETURNED NOTHING' in '...' -- a parser
        failure was reported as a walk failure
    """
    note = shape.tracker_read_note(
        {}, {"attached": True, "waited_ms": 5}, {}, records=4, dropped=4
    )
    assert "REJECTED ALL 4" in note, note
    assert "that is the PARSER" in note, note
    assert "THE CARD WALK RETURNED NOTHING" not in note, note


async def test_the_note_is_silent_about_a_harvest_it_was_not_told_about():
    """No arguments, no claim. The note must not invent a count.

    SHOWN FAILING by defaulting ``records`` to 0, which would make every
    caller that forgot to pass it report a walk failure::

        AssertionError: 'THE CARD WALK RETURNED NOTHING' in '...'
    """
    note = shape.tracker_read_note({}, {"attached": True, "waited_ms": 5}, {})
    assert "CARD WALK" not in note, note
    assert "WALK CENSUS" not in note, note
