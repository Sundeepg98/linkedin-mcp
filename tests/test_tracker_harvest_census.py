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


# ---------------------------------------------------------------------------
# 5. The screen-reader budget, and the premise under it
# ---------------------------------------------------------------------------

#: The CLIP pattern: the element IS rendered, just clipped to nothing. Its text
#: therefore appears in innerText, and a subtraction that removes one copy is
#: correct.
CLIP = (
    "position:absolute;clip:rect(0 0 0 0);clip-path:inset(50%);"
    "height:1px;width:1px;overflow:hidden"
)

SR_TITLE = "Senior Full-stack Engineer - Remote"
SR_COMPANY = "Sprinto"
SR_HREF = "https://www.linkedin.com/jobs/view/4423880462/"


def row_with_screen_reader(style: str) -> str:
    """DERIVED: a saved-shaped row whose title is duplicated for a reader."""
    shell = derive(markup("jobs_tracker_empty"), ">No jobs here</h2>", "></h2>")
    shell = derive(shell, "Saved &#183; 0", "Saved &#183; 1", count=-1)
    frag = (
        f'<div><div><a href="{SR_HREF}">'
        f'<span class="visually-hidden" style="{style}">{SR_TITLE}</span>'
        f"<span>{SR_TITLE}</span><span>{SR_COMPANY}</span></a></div></div>"
    )
    return derive(shell, "</main>", frag + "</main>")


async def _budget(page):
    records = await dom.harvest_linked_cards(
        page, href_pattern=dom.JOB_HREF, max_items=75
    )
    census = await dom.harvest_census(
        page, href_pattern=dom.JOB_HREF, max_items=75
    )
    return records, census


async def test_a_clipped_duplicate_is_still_charged_to_the_card():
    """THE CONTROL, and the behaviour that must NOT change.

    The clip pattern leaves the element rendered, so ``innerText`` really does
    carry a second copy and removing one is correct. This is the case the
    subtraction was built for, and every surface that depends on it -- search
    results with a verified-employer line, notifications -- depends on it
    still working.

    SHOWN FAILING by skipping every hidden element regardless of rendering::

        AssertionError: assert [] == ['Senior Full-stack Engineer - Remote']
        -- a rendered duplicate stopped being subtracted, so it will now be
        read as content
    """

    async def work(page):
        return await _budget(page)

    records, census = await _with_html(row_with_screen_reader(CLIP), work)
    assert records, records
    assert records[0]["hidden"] == [SR_TITLE], records[0]
    assert census["hidden_not_rendered"] == 0, census


async def test_a_display_none_duplicate_is_not_charged_to_the_card():
    """THE FIX. A duplicate innerText never returned may not be subtracted.

    ``strip_screen_reader_copies`` subtracts BY COUNT, one occurrence per
    hidden element. Its docstring's premise -- "innerText includes
    visually-hidden text" -- is true of the clip pattern and FALSE of
    ``display:none``. But the sweep read each hidden element with
    ``innerText``, which on a NON-RENDERED element falls back to
    ``textContent``, so the budget was charged for a copy that was never in
    the card. The subtraction then paid for it out of the VISIBLE copy.

    Measured 2026-08-30: the title vanished, and with it the only line
    ``parse_job_card`` could have read.

    SHOWN FAILING by removing the ``isRendered`` guard::

        AssertionError: assert ['Senior Full-stack Engineer - Remote'] == []
        -- a duplicate that innerText never carried was charged to the card
    """

    async def work(page):
        return await _budget(page)

    records, census = await _with_html(
        row_with_screen_reader("display:none"), work
    )
    assert records, records
    assert records[0]["hidden"] == [], records[0]
    # TWO, NOT ONE, and the number is honest rather than deduped: the walk
    # reads a card's hidden set TWICE -- once for the row and once for the
    # anchor, which fill `hidden` and `link_hidden` -- so one offending
    # element is skipped on both passes. The field counts SKIPPED READS. It
    # exists to answer "does this page carry non-rendered duplicates at all",
    # and for that a count that is high by a constant factor is fine; what
    # would not be fine is calling it a count of elements.
    assert census["hidden_not_rendered"] == 2, census


def row_title_only(style: str) -> str:
    """DERIVED: a row whose ONLY visible line is its title, duplicated hidden.

    THE SHAPE THAT REPRODUCES THE LIVE SIGNATURE, and the reason it is a
    separate builder from ``row_with_screen_reader`` is measured rather than
    tidy. A row carrying title AND company loses only the title to the bad
    subtraction, so the parser still finds a line and returns a CORRUPTED row
    (``title: 'Sprinto'``). Only when the eaten line is the row's whole content
    does the parser have nothing left, return None, and produce the live
    ``records=1, dropped=1``.

    The second anchor to the same job is what makes ``rowOf``'s second stop
    fire, so the walk does not climb into page chrome -- chrome lines would
    keep ``lines`` non-empty and mask the drop.
    """
    shell = derive(markup("jobs_tracker_empty"), ">No jobs here</h2>", "></h2>")
    shell = derive(shell, "Saved &#183; 0", "Saved &#183; 1", count=-1)
    frag = (
        f'<div><div><a href="{SR_HREF}">'
        f'<span class="visually-hidden" style="{style}">{SR_TITLE}</span>'
        f"<span>{SR_TITLE}</span></a>"
        f'<a href="{SR_HREF}"></a></div></div>'
    )
    return derive(shell, "</main>", frag + "</main>")


async def test_the_visible_title_survives_a_display_none_duplicate():
    """The consequence, end to end, through the real parser.

    This is the assertion that actually matters: the row parses, and its title
    is the title rather than nothing.

    IT REPRODUCES THE LIVE SIGNATURE, which is why the fixture is a title-only
    row. Measured against the pre-fix walk restored in memory:

        pre-fix   records=1  parsed=0  dropped=1   <- the live numbers
        fixed     records=1  parsed=1  dropped=0

    SHOWN FAILING by removing the ``isRendered`` guard::

        AssertionError: assert 0 == 1
        -- the row was dropped, which is the live signature: records=1,
        dropped=1

    An earlier draft of this test used a title-AND-company row and claimed the
    same failure. It does not produce it: that row loses only its title and
    comes back CORRUPTED (``title: 'Sprinto'``) rather than dropped. The
    docstring was corrected after a mutation run measured it.
    """

    async def work(page):
        records, _census = await _budget(page)
        rows, dropped = dom.parse_all(records, shape.parse_job_card)
        return records, rows, dropped

    records, rows, dropped = await _with_html(row_title_only("display:none"), work)
    assert len(records) == 1, records
    assert len(rows) == 1, (rows, dropped)
    assert dropped == 0, dropped
    assert rows[0]["title"] == SR_TITLE, rows[0]


async def test_a_row_with_other_lines_is_corrupted_rather_than_dropped():
    """The SAME defect, one line richer, and it fails differently.

    Worth pinning because the two look like different bugs and are one. When
    the eaten line is not the row's whole content, the parser finds what is
    left and returns a row that is confidently WRONG rather than absent --
    which is the more dangerous of the two outcomes and the harder to notice.

    SHOWN FAILING by removing the ``isRendered`` guard::

        AssertionError: assert 'Sprinto' == 'Senior Full-stack Engineer -
        Remote' -- the company line was promoted to title after the real
        title was subtracted away
    """

    async def work(page):
        records, _census = await _budget(page)
        rows, dropped = dom.parse_all(records, shape.parse_job_card)
        return rows, dropped

    rows, dropped = await _with_html(
        row_with_screen_reader("display:none"), work
    )
    assert dropped == 0, dropped
    assert len(rows) == 1, rows
    assert rows[0]["title"].startswith(SR_TITLE), rows[0]


async def test_the_draft_row_still_parses_and_for_the_same_reason():
    """THE CONSTRAINT: fixing Saved must not change what Draft relies on.

    ``jobs_tracker_row.html`` is the DRAFT tab, and it is the one tracker
    surface that works live. Its fields are asserted EXACTLY -- not merely
    "it still returns something" -- because a fix that left it parsing by
    coincidence would pass a weaker check.

    WHAT THIS TEST DOES AND DOES NOT GUARD, corrected after a mutation run.
    An earlier docstring claimed its screen-reader elements are "RENDERED in
    this fixture", so that the over-broad mutation -- skip EVERY hidden
    element -- would change it. That is false: ``jobs_tracker_row.html``
    contains ZERO elements matching ``dom.CARD_HIDDEN_SELECTOR``, so
    ``hiddenWithin`` walks an empty list and the guard line never executes on
    it. This test CANNOT fail at that mutation and no longer claims to.

    What it does hold is worth keeping on its own: the draft row's fields,
    exactly, so any change to the walk or the parser that reshapes the one
    tracker surface working live fails here.

    THE OVER-BROAD MUTATION IS CAUGHT ELSEWHERE, and loudly -- measured, it
    takes ``tests/test_job_search_fixture.py`` to 19 failures, because search
    results DO carry rendered screen-reader lines and depend on their being
    subtracted. That is the guard; this is not.

    SHOWN FAILING by any change that reshapes the draft row -- for example
    dropping the middle-dot split in ``parse_job_card``::

        AssertionError: assert [{'title': ..., 'company': 'Ashgrove Systems
        <dot> Fairhaven (Remote)', 'location': None, ...}] == [...]
    """

    async def work(page):
        records = await dom.harvest_linked_cards(
            page, href_pattern=dom.JOB_HREF, max_items=75
        )
        return dom.parse_all(records, shape.parse_job_card)

    rows, dropped = await _with_html(markup("jobs_tracker_row"), work)
    assert dropped == 0, dropped
    assert rows == [
        {
            "title": "Platform Integration Engineer",
            "company": "Ashgrove Systems",
            "location": "Fairhaven (Remote)",
            "status": "no longer accepting applications",
            "job_id": "4011223344",
            "url": "https://www.linkedin.com/jobs/view/4011223344",
        }
    ], rows


# ---------------------------------------------------------------------------
# 6. The refusal must not name two culprits at once
# ---------------------------------------------------------------------------


async def test_the_shape_sentence_does_not_blame_the_walk_that_returned_rows():
    """A REFUSAL MAY NOT NAME TWO COMPONENTS IN ONE BREATH.

    Measured on a live refusal 2026-08-30, four sentences apart:

        "THE CARD WALK RETURNED 1 RECORD(S) AND THE ROW PARSER REJECTED ALL 1
         ... that is the PARSER"
        "The text exists and is readable, so a walk that returned nothing
         stopped short of it -- that is a defect in the walk."

    The second reasons from a premise the first has already refuted, and both
    reached the same caller. An instrument that names two culprits at once can
    be quoted either way, which is worse than naming none.

    SHOWN FAILING by deleting the ``records == 0`` guard on that branch --
    ``elif records == 0:`` -> ``elif True:``::

        AssertionError: 'defect in the walk' in '...' -- the refusal blames
        the walk in the same breath as clearing it

    NOT reproducible by removing the ``records`` ARGUMENT from the call, and
    that was this docstring's first claim. Measured: the parameter defaults to
    ``None``, ``None == 0`` is False, so the call falls through to the same
    safe branch and the output is byte-identical. The argument makes the guard
    POSSIBLE; the guard is what does the work, and a docstring naming the
    wrong one sends the next reader to the wrong line.
    """
    ladder = [
        [
            {"tag": "A", "children": 1, "keys": 0, "text_chars": 75,
             "content_chars": 75},
            {"tag": "DIV", "children": 1, "keys": 1, "text_chars": 231,
             "content_chars": 396},
        ]
    ]
    note = shape.tracker_read_note(
        {}, {"attached": True, "waited_ms": 5}, {},
        records=1, dropped=1, row_shape=ladder,
    )
    # The walk returned something, so it did not stop short.
    assert "defect in the walk" not in note, note
    assert "stopped short" not in note, note
    # And the parser sentence must still be there, alone.
    assert "REJECTED ALL 1" in note, note
    assert "that is the PARSER" in note, note
    # The shape numbers are still reported -- suppressed blame, not evidence.
    assert "renders 231" in note, note


async def test_the_shape_sentence_DOES_blame_the_walk_when_it_returned_nothing():
    """The control. Suppressing the sentence always would be the other error.

    SHOWN FAILING by dropping the ``records == 0`` branch entirely::

        AssertionError: 'defect in the walk' not in '...'
    """
    ladder = [
        [
            {"tag": "A", "children": 1, "keys": 0, "text_chars": 75,
             "content_chars": 75},
        ]
    ]
    note = shape.tracker_read_note(
        {}, {"attached": True, "waited_ms": 5}, {},
        records=0, row_shape=ladder,
    )
    assert "defect in the walk" in note, note


# ---------------------------------------------------------------------------
# 7. WHICH filter ate the row -- the parse trace
# ---------------------------------------------------------------------------

#: Records chosen to reach each of ``parse_job_card``'s outcomes, including
#: both of its two separate ``return None`` lines. Synthetic, and none of them
#: names a real person or employer.
TRACE_RECORDS = {
    "ordinary row": {"text": "Senior Engineer\n\nSprinto", "hidden": []},
    "every line a status": {
        "text": "No longer accepting applications",
        "hidden": [],
    },
    "subtraction takes the only line": {
        "text": "Senior Engineer",
        "hidden": ["Senior Engineer"],
    },
    "empty": {"text": "", "hidden": []},
    # REPOINTED after a mutation run: this record used to read "Date posted",
    # which ``shape.is_chrome`` does NOT match -- measured -- so the record
    # meant to exercise the chrome path came back ``parsed`` and nothing in
    # this file covered ``no_lines`` reached via the chrome filter. Both
    # strings below are in ``shape._CHROME``.
    "chrome only": {"text": "Promoted\n\nDismiss", "hidden": []},
    # THE LIVE SHAPE the anchored-title exemption was written for: one line
    # carrying the title with a timestamp welded into it. In the corpus so the
    # trace and the parser are held to agreeing about it -- they did NOT when
    # the exemption was added to only one of them.
    "live welded row": {
        "text": "Senior Engineer - Remote Acme India Saved 3 days ago",
        "link_text": "Senior Engineer - Remote Acme India Saved 3 days ago",
        "hidden": [],
    },
}


async def test_the_trace_agrees_with_the_parser_it_describes():
    """THE ANTI-DRIFT GUARD, and the reason the trace is allowed to exist.

    ``parse_job_card_trace`` re-runs the same helpers in the same order as
    ``parse_job_card`` rather than being spliced into it, which buys a
    diagnostic that costs nothing on the healthy path and risks saying
    something the parser would not. So the agreement is asserted, over every
    record the tracked fixtures actually produce PLUS the synthetic ones that
    reach the edges -- a trace that disagreed with its subject would be worse
    than no trace at all.

    SHOWN FAILING by making the trace report ``parsed`` for a record the
    parser rejects -- delete its ``elif not remaining:`` branch::

        AssertionError: ('every line a status', 'parsed', 'rejected')

    WHAT THIS TEST DOES NOT CATCH ON ITS OWN, corrected after a mutation run
    measured it. Swapping the two refusal VALUES is invisible to the agreement
    assertion, because ``verdict == "parsed"`` collapses both of them to the
    same boolean. That swap is caught by the two sibling tests below, which
    pin a specific verdict on a specific record -- so the coverage exists, and
    this docstring used to claim credit for it wrongly.

    The second assertion block closes the gap here as well: it checks the
    verdict against the trace's OWN counts, which distinguishes the two
    refusals without re-implementing the parser.

    AND REORDERING THE FILTERS IS NOT CATCHABLE HERE AT ALL -- that is a
    property rather than a hole. The three predicates are pure and
    ``remaining`` requires all three to be false, so the set of lines reaching
    it is order-invariant and no reordering can move ``verdict``. It moves
    LABELS, which is what the label assertions in the siblings hold.
    """
    checks: list[tuple] = []

    async def work(page):
        return await dom.harvest_linked_cards(
            page, href_pattern=dom.JOB_HREF, max_items=75
        )

    # Every record the real fixtures produce, through the real walk.
    for which in ("jobs_tracker_row", "jobs_tracker_empty", "jobs_search"):
        try:
            html = markup(which)
        except FileNotFoundError:  # pragma: no cover - fixture set may differ
            continue
        for record in await _with_html(html, work):
            checks.append(("fixture:" + which, record))

    for name, record in TRACE_RECORDS.items():
        checks.append((name, record))

    assert len(checks) >= 4, checks

    seen: set = set()
    for name, record in checks:
        trace = shape.parse_job_card_trace(record)
        parsed = shape.parse_job_card(record) is not None
        assert (trace["verdict"] == "parsed") == parsed, (
            name,
            trace["verdict"],
            "parsed" if parsed else "rejected",
        )
        assert trace["verdict"] in shape.PARSE_VERDICTS, trace
        seen.add(trace["verdict"])

        # THE VERDICT AGAINST THE TRACE'S OWN COUNTS. This is what separates
        # the two refusals, which the boolean above cannot: swapping the two
        # verdict strings passes the agreement check and fails here.
        # Derived from the numbers the trace already reports, so it is not a
        # second implementation of the parser.
        if trace["verdict"] == "no_lines":
            assert trace["lines_after_chrome"] == 0, (name, trace)
        elif trace["verdict"] == "no_remaining":
            assert trace["lines_after_chrome"] > 0, (name, trace)
            assert trace["remaining_after_status"] == 0, (name, trace)
        else:
            assert trace["remaining_after_status"] > 0, (name, trace)

    # AND ALL THREE VERDICTS MUST ACTUALLY OCCUR. Without this the block above
    # is satisfied by a corpus that only ever parses -- which is what this
    # file's was until the "chrome only" record was repointed at a string
    # shape.is_chrome actually matches.
    assert seen == set(shape.PARSE_VERDICTS), sorted(seen)


async def test_the_trace_names_the_status_classifier_when_that_is_what_ate_it():
    """``if not remaining`` -- a title classified as a status or a time-ago.

    One of ``parse_job_card``'s two refusals, and the one that means a
    CLASSIFIER is wrong rather than the text being absent.

    SHOWN FAILING by returning a single generic sentence for both refusals::

        AssertionError: 'if not remaining' not in "... IT RETURNED None AT
        'if not lines' ..."
    """
    trace = shape.parse_job_card_trace(TRACE_RECORDS["every line a status"])
    assert trace["verdict"] == "no_remaining", trace
    assert trace["lines_after_chrome"] == 1, trace
    assert trace["remaining_after_status"] == 0, trace
    assert trace["labels"] == ["status"], trace

    note = shape.parse_trace_note([trace])
    assert "if not remaining" in note, note
    assert "CLASSIFIER problem" in note, note
    assert "if not lines" not in note, note


async def test_the_trace_names_the_subtraction_when_that_is_what_ate_it():
    """``if not lines`` -- and the counts say whether it was chrome or the
    screen-reader budget.

    SHOWN FAILING by reporting the RAW line count in the post-subtraction
    slot -- ``"lines_after_screen_reader": len(raw)``::

        AssertionError: assert 1 == 0 -- the count after the subtraction was
        not the count after the subtraction, so which step took the line is
        unknowable from the trace

    NOT reproducible by reporting ``len(after_repeats)`` there, and that was
    this docstring's first claim. Measured across all 13 records this file
    drives, ``drop_consecutive_repeats`` removes nothing, so the two counts
    are equal everywhere and the substitution has no observable effect. A
    mutation that changes no output is not a test of anything.
    """
    trace = shape.parse_job_card_trace(
        TRACE_RECORDS["subtraction takes the only line"]
    )
    assert trace["verdict"] == "no_lines", trace
    # THE PAIR IS THE POINT: one line went in, none survived the subtraction,
    # so the budget took it and the chrome filter never saw it.
    assert trace["lines_raw"] == 1, trace
    assert trace["lines_after_screen_reader"] == 0, trace
    assert trace["hidden_count"] == 1, trace

    note = shape.parse_trace_note([trace])
    assert "if not lines" in note, note
    assert "if not remaining" not in note, note


async def test_the_trace_reports_no_line_text():
    """LABELS AND COUNTS ONLY. A tracker row names a company and a job.

    Every label is drawn from a CLOSED vocabulary, so the trace cannot leak a
    line by deriving a label from it.

    SHOWN FAILING by putting the line itself in the label list::

        AssertionError: 'Ashgrove' leaked out of the parse trace
    """

    async def work(page):
        return await dom.harvest_linked_cards(
            page, href_pattern=dom.JOB_HREF, max_items=75
        )

    records = await _with_html(markup("jobs_tracker_row"), work)
    assert records, records
    trace = shape.parse_job_card_trace(records[0])
    rendered = str(trace) + shape.parse_trace_note([trace])
    for secret in ("Ashgrove", "Platform Integration", "Fairhaven"):
        assert secret not in rendered, f"{secret!r} leaked out of the parse trace"
    for label in trace["labels"]:
        assert label in shape.PARSE_LINE_LABELS, label


async def test_the_ladder_reports_keyed_links_as_well_as_keys():
    """``rowOf``'s second stop tests LINKS, so a ladder without them is blind.

    The stop is ``hasText(row) && linksWithin(node) > 1`` -- the raw count of
    keyed anchors, not the deduped one. Printing only distinct keys made the
    live ladder unable to say where that stop should have fired, on a page
    carrying four job-row anchors under one job id.

    SHOWN FAILING by dropping ``links`` from the printed ladder, which is the
    state it shipped in::

        AssertionError: '2L' not in "... DIV(1c,1k) 75/75 ..."
    """
    ladder = [
        [
            {"tag": "A", "children": 1, "keys": 0, "links": 0,
             "text_chars": 75, "content_chars": 75},
            {"tag": "DIV", "children": 2, "keys": 1, "links": 2,
             "text_chars": 75, "content_chars": 75},
        ]
    ]
    note = shape.tracker_read_note(
        {}, {"attached": True, "waited_ms": 5}, {}, records=1, row_shape=ladder
    )
    assert "2L" in note, note
    assert "keyed Links" in note, note


# ---------------------------------------------------------------------------
# 8. The classifier that ate the title
# ---------------------------------------------------------------------------

#: THE LIVE SHAPE, modelled from the trace the Saved tab returned on
#: 2026-08-30: ONE line, carrying the anchored title with a relative timestamp
#: welded into it. Invented text of the right shape -- it names no real
#: employer -- and the two fields are equal because on that row the whole card
#: sat inside a single anchor.
WELDED = "Senior Full-stack Engineer - Remote Sprinto India (Remote) Saved 3 days ago"
WELDED_RECORD = {"text": WELDED, "link_text": WELDED, "hidden": []}


async def test_a_title_with_an_inline_timestamp_is_not_discarded():
    """THE FIX. ``has_time_ago`` asks whether a line CONTAINS a timestamp, and
    ``parse_job_card`` discarded the WHOLE line on a yes.

    That pairing is a defect this module had already documented for another
    surface -- ``is_timestamp_line``'s docstring says a notification body
    carrying its time inline must not be thrown away to avoid repeating the
    time. The job-card parser never learned it.

    Measured live: the Saved row arrived as one 75-character line carrying the
    anchored title and a relative timestamp. The line was discarded whole,
    ``remaining`` emptied, and the row dropped -- records=1, dropped=1.

    SHOWN FAILING by removing the ``and line != anchor`` exemption::

        AssertionError: assert None is not None
        -- the row is dropped, which is the live signature
    """
    parsed = shape.parse_job_card(WELDED_RECORD)
    assert parsed is not None, "the row was dropped"
    assert parsed["title"] == WELDED, parsed
    # THE TIMESTAMP IS STILL REPORTED. find_time_ago runs over every line
    # before the discard loop, so sparing the line does not lose the time.
    assert parsed["when"] == "3 days ago", parsed


async def test_the_timestamp_is_still_lifted_when_it_is_NOT_the_title():
    """The exemption is one line wide. Everything else is discarded as before.

    A card whose timestamp sits on its own line must still lose that line --
    otherwise "3 days ago" becomes a content field.

    SHOWN FAILING by sparing every line instead of the anchored one::

        AssertionError: assert '3 days ago' != 'Senior Engineer'
        -- a bare timestamp line survived and could be read as a field
    """
    record = {
        "text": "Senior Engineer\n\n3 days ago\n\nSprinto",
        "link_text": "Senior Engineer",
        "hidden": [],
    }
    parsed = shape.parse_job_card(record)
    assert parsed is not None, record
    assert parsed["title"] == "Senior Engineer", parsed
    assert parsed["when"] == "3 days ago", parsed
    # The bare timestamp line is gone, so it cannot have become the company.
    assert parsed.get("company") != "3 days ago", parsed


async def test_the_narrow_repair_was_chosen_over_the_wide_one():
    """``is_timestamp_line`` would fix this row and break one that works.

    Recorded as an executable statement rather than a paragraph, because the
    wide repair is the obvious one and the next reader will reach for it.

    Measured across all 25 records the fixtures produce: swapping the
    predicate promotes a location-and-time line from discarded to content on
    ``job_detail_following_hydrated``. Sparing the anchored title changes
    NOTHING -- zero of 25.

    SHOWN FAILING by making ``is_timestamp_line`` agree with ``has_time_ago``
    on this line, which is what the wide repair assumes::

        AssertionError: assert True is False
    """
    welded_location = (
        "Riverton, Fairhaven, United States - 1 week ago - 33 people clicked apply"
    )
    # has_time_ago says yes -- it CONTAINS a timestamp -- and that is why the
    # line is discarded today.
    assert shape.has_time_ago(welded_location) is True
    # is_timestamp_line says no -- it is not ONLY a timestamp -- which is why
    # swapping the predicate would keep it and change that card.
    assert shape.is_timestamp_line(welded_location) is False


async def test_the_trace_mirrors_the_anchored_title_exemption():
    """The trace and the parser must agree on the record the fix was FOR.

    When the parser gained the exemption this function had not, and the two
    disagreed immediately -- the trace said ``no_remaining`` while the parser
    returned a row. That is the drift the agreement test exists to catch, and
    it caught it.

    SHOWN FAILING by removing ``and line != anchor`` from the trace only::

        AssertionError: ('live welded row', 'no_remaining', 'parsed')
    """
    trace = shape.parse_job_card_trace(WELDED_RECORD)
    assert trace["verdict"] == "parsed", trace
    assert trace["labels"] == ["content"], trace
    assert trace["has_anchored_title"] is True, trace


# ---------------------------------------------------------------------------
# 9. The one-line card, pulled apart on the boundaries it actually has
# ---------------------------------------------------------------------------

DOT = shape.MIDDLE_DOT

#: THE TWO LIVE SHAPES, measured 2026-08-30 -- Saved and Draft. Both arrive as
#: ONE line with everything welded. The employer names are invented; the SHAPE
#: is what was measured, and it is the shape under test.
SAVED_LINE = f"Senior Full-stack Engineer - Remote Acme {DOT} India (Remote)Reposted 4d ago"
DRAFT_LINE = (
    f"ServiceNow Application Developer Northwind {DOT} "
    "India (Remote)No longer accepting applications"
)


def welded_record(line: str) -> dict:
    """A tracker-shaped record: one line, inside one anchor, no lockup."""
    return {
        "text": line,
        "link_text": line,
        "hidden": [],
        "href": "https://www.linkedin.com/jobs/view/4423880462/",
    }


async def test_the_saved_row_splits_into_title_and_location():
    """The live Saved shape, end to end.

    Before this, the WHOLE line landed in ``title`` with company and location
    null -- measured on the live tab after the Part 6 fix made the row parse
    at all.

    SHOWN FAILING by narrowing the trigger to cards with a lockup, which is
    the guard that keeps this off every other surface::

        AssertionError: assert 'Senior Full-stack Engineer - Remote Acme
        <dot> India (Remote)Reposted 4d ago' == 'Senior Full-stack Engineer -
        Remote Acme'
    """
    row = shape.parse_job_card(welded_record(SAVED_LINE))
    assert row is not None
    assert row["title"] == "Senior Full-stack Engineer - Remote Acme", row
    assert row["location"] == "India (Remote)", row
    # AND THE TIMESTAMP IS UNTOUCHED. find_time_ago ran over the original
    # lines, so ``when`` comes from where it always came from -- not from the
    # split. That is the thing most easily broken by this change.
    assert row["when"] == "4 days ago", row


async def test_the_draft_row_splits_and_recovers_its_status():
    """The live Draft shape. Same defect, and it also hid the status.

    ``_JOB_STATUS_LINE`` is anchored at ``^``, so a status welded onto the end
    of a line never matched and never reached the ``status`` field.

    SHOWN FAILING by dropping the status branch from
    ``split_welded_card_line``::

        AssertionError: 'status' not in {'title': ..., 'location': 'India
        (Remote)No longer accepting applications', ...}
    """
    row = shape.parse_job_card(welded_record(DRAFT_LINE))
    assert row is not None
    assert row["title"] == "ServiceNow Application Developer Northwind", row
    assert row["location"] == "India (Remote)", row
    assert row["status"] == "no longer accepting applications", row


async def test_the_company_is_reported_ABSENT_rather_than_guessed():
    """There is no delimiter between the title and the company, so there is no
    company.

    THE HEAD IS NOT SPLIT FURTHER, deliberately. On this surface the card
    carries no employer logo -- measured, ``jobs_tracker_row.html``'s only
    ``<img>`` has an empty ``alt`` -- so ``logo_name`` is null and the lockup
    cannot name the company either. Every rule for finding that boundary in
    the string would be a guess, and a wrong value in a real field does not
    announce itself the way a missing one does.

    SHOWN FAILING by splitting the head on its last space, which is the
    obvious guess::

        AssertionError: assert 'Acme' is None -- a company was invented out
        of the title
    """
    for line in (SAVED_LINE, DRAFT_LINE):
        row = shape.parse_job_card(welded_record(line))
        assert row["company"] is None, row


async def test_a_line_it_cannot_account_for_is_left_alone():
    """No middle dot, or two of them, and the split refuses entirely.

    SHOWN FAILING by falling back to splitting on the first dot found::

        AssertionError: assert {'head': 'a', ...} is None
    """
    assert shape.split_welded_card_line("no separator at all") is None
    assert shape.split_welded_card_line(f"a {DOT} b {DOT} c") is None
    assert shape.split_welded_card_line("") is None
    assert shape.split_welded_card_line(f"{DOT} only a location") is None


async def test_an_ambiguous_status_word_is_not_lifted_from_the_end():
    """"Applied Scientist" is a job title. The end-anchored vocabulary is a
    DELIBERATE SUBSET of the status one.

    ``_JOB_STATUS_LINE`` is anchored at ``^`` because, in its own words, a
    substring match "would eat it as the status and shift every other field up
    by one". Recognising a status at the END is a weaker form of the same
    hazard, so the single ambiguous words -- applied, viewed, interview -- are
    not in the welded vocabulary.

    THE AMBIGUOUS WORD MUST BE AT THE END, and the first version of this test
    put it mid-line -- where an end-anchored pattern can never reach it, so the
    guard could not fail at the mutation it names. Corrected after a mutation
    run measured it. This is a line whose LOCATION ends in a title-ish word.

    SHOWN FAILING by reusing ``_JOB_STATUS_LINE``'s full word list at the end
    of the line. Measured, the damage is worse than the status field: the
    lifted tail drags the location with it::

        AssertionError: {'head': 'Acme', 'location': 'Berlin Data Engineer,',
        'status': 'applied', ...}
        assert 'applied' is None
    """
    line = f"Acme {DOT} Berlin Data Engineer, Applied"
    out = shape.split_welded_card_line(line)
    assert out is not None, line
    assert out["status"] is None, out
    # The whole tail stays where it was; nothing was lifted off the end.
    assert out["location"] == "Berlin Data Engineer, Applied", out


async def test_the_trigger_does_not_fire_where_the_card_has_anchors():
    """A card with a lockup keeps its anchors. An anchor beats a split.

    This is the guard that kept the change off every other surface -- measured,
    the welded path fires on ZERO of the 25 records the fixtures produce.

    SHOWN FAILING by removing the ``logo_name``/``meta_line`` condition from
    the trigger::

        AssertionError: assert None == 'Northwind' -- a card that named its
        employer through the lockup had that answer discarded
    """
    record = welded_record(f"Senior Engineer Northwind {DOT} Berlin")
    record["logo_name"] = "Northwind"
    row = shape.parse_job_card(record)
    assert row["company"] == "Northwind", row


# A CORPUS-WIDE GUARD WAS WRITTEN HERE AND DELETED, and the deletion is
# recorded rather than silent. It walked every fixture record and asserted
# that a card naming its employer through the lockup still reports that
# company. It survived FOUR separate mutations: relaxing the single-line
# clause, deleting the lockup clauses, removing the whole trigger, and even
# removing the lockup as the company source altogether.
#
# The reason is structural. Of the 25 records the fixtures produce, the two
# whose lines split at all are not the ones carrying a lockup, so no trigger
# change can make the welded path swallow a lockup card in this corpus. The
# test therefore could not fail for the reason it was written, and this
# repo's rule is that a check which cannot fail certifies nothing.
#
# What it was meant to cover IS covered:
# test_the_trigger_does_not_fire_where_the_card_has_anchors drives the same
# property on a record built to reach it, and goes red at every one of those
# four mutations. The breadth was the illusion; the synthetic record is the
# guard.
