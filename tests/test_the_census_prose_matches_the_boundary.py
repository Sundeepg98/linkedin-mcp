"""The census's claims about the read boundary are checked against the boundary.

## THE DEFECT THIS FILE EXISTS FOR, measured 2026-09-20

`_audit/_census/messaging-and-content.md` section 4 is titled *THE READ
BOUNDARY IS THE STRUCTURAL CAUSE OF MOST OF THE 88*. It is the section that
explains why most of that slice is a GAP, and every factual claim it made about
the code was stale:

    the read allowlist is 22 url patterns        -> 41 today
    nothing in it reaches Groups / Events /
      newsletters / creator analytics           -> all four reachable today
    set_input_files has not been sanctioned     -> entry 7 of 7, since 2026-09-04
    no document has ever discussed it           -> 8 documents under _audit/

**Ten GAP rows carried the third of those as their stated reason.** The section
was written 2026-09-03 and never re-run, while the same file took eighteen
further commits on 2026-09-19 that edited other sections. Nothing went red,
because prose is asserted by nothing.

## WHY THIS IS NOT "JUST UPDATE THE NUMBER"

A corrected number rots exactly as fast as the one it replaced. `readonly.py`
says so about itself: *"a count in prose beside a list it cannot read goes
stale in silence, and knowing that does not stop you writing one."* So this
file makes the DOCUMENT the subject: it reads the claims out of the census and
compares them with the shipped boundary, and it is the census that fails when
the two disagree.

## WHAT IS ASSERTED, AND WHAT IS DELIBERATELY NOT

**Asserted:** the numeric and boolean claims of the correction block -- the
pattern count, which surfaces `is_read_url` admits and refuses, and which
mutation kinds are sanctioned.

**Not asserted:** that the section's ARGUMENT is right. Whether a read boundary
is the structural cause of anything is a judgement, and no test decides one.

## THE CONTROLS, because a check over prose is the easiest kind to make vacuous

1. **Readability.** The claims must be FOUND. If section 4 is renamed, its
   table reformatted or the block deleted, this file fails loudly rather than
   passing over zero claims -- the `PASS: 0 hits across 0 blobs` shape.
2. **The boundary is not mute.** `is_read_url` is shown REFUSING (`/psettings/`,
   an off-site url) and ACCEPTING (`/feed/`) in the same run, so a table of
   False verdicts cannot be produced by a dead instrument.
3. **Shown failing.** :func:`test_the_claim_reader_can_fail` runs the same
   comparison against a mutated copy of the claim and requires a mismatch.

## THE REACHABLE SURFACES ARE READ FROM THEIR ROW, NOT FROM A WINDOW (lane ci8, 2026-11-27)

The check that the census names every surface this file calls reachable used
to read the first 6000 characters of section 4 and look for each surface's
first word anywhere in them. The count row above it grows by a clause with
every admission, and on 2026-11-27 it pushed the reachable row past the
window twice: the guard went red on a census that was right, and integration
7 had to shorten the count cell's clauses to make it fit. The window also
matched words wherever they fell, so "post" and "saved" were found in the
COUNT row, not in the row that makes the claim.

So the guard now reads the ROW: section 4's table row whose first cell opens
"nothing in it reaches", split by the census's own cell reader
(`scripts/count_census_states.py`, which honours an escaped pipe). Every
surface this file calls reachable must be named in that row's MEASURED cell,
by its name or by its address. Its controls:

* :func:`test_a_cell_grown_past_the_old_window_cannot_hide_the_row` grows
  the count cell past the window and shows the old reading missing surfaces
  while the row reading misses none;
* :func:`test_the_row_reader_can_fail` takes "saved posts" out of the
  measured cell and requires the row reading to name exactly that surface.
"""

from __future__ import annotations

import pathlib
import re
import sys

import pytest

from linkedin_server import readonly

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import count_census_states  # noqa: E402 -- the census's own cell reader

_CENSUS = (
    pathlib.Path(__file__).resolve().parent.parent
    / "_audit"
    / "_census"
    / "messaging-and-content.md"
)

#: The correction block's row for the pattern count reads, in part:
#:
#:     | the read allowlist is **22** url patterns | **41**. Twenty of ...
#:
#: so the claim is the first bolded integer in the RIGHT-hand cell. Anchored on
#: the left cell's wording so a different row cannot be read by accident.
_COUNT_CLAIM = re.compile(
    r"\|\s*the read allowlist is \*\*(\d+)\*\* url patterns\s*\|\s*\*\*(\d+)\*\*"
)

#: Surfaces the correction block says are REACHABLE today, with the address it
#: says reaches them. Kept here rather than parsed out of the prose because a
#: url inside a markdown table cell is the kind of thing a reformat breaks,
#: and a guard that silently stops checking is worse than none. The prose and
#: this list are compared by :func:`test_the_reachable_surfaces_are_named_in_the_census`.
_CLAIMED_REACHABLE = {
    "groups": "https://www.linkedin.com/groups/",
    "events": "https://www.linkedin.com/events/",
    "newsletters": "https://www.linkedin.com/mynetwork/network-manager/newsletters/",
    "creator analytics": "https://www.linkedin.com/analytics/creator/content/",
    # MOVED FROM THE REFUSED TABLE BELOW 2026-09-23, with the census cell it
    # checks: lane L1 admitted ONE post's analytics by its activity urn, on
    # its own anchored line. The guard did its job -- it went red at the edit
    # and the census moved with the boundary, not the assertion.
    "post analytics": (
        "https://www.linkedin.com/analytics/post-summary/urn:li:activity:10001/"
    ),
    # MOVED FROM THE REFUSED TABLE BELOW 2026-11-27, with the census row it
    # checks: lane msg7 admitted his saved posts list on its own anchored
    # line (ADMIT-NOW-LANDING-IN-SESSION-14). The guard went red at the edit,
    # and the census moved with the boundary, not the assertion.
    "saved posts": "https://www.linkedin.com/my-items/saved-posts/",
}

#: Surfaces the correction block says still REFUSE. Five of the eleven the
#: original sentence named (seven until 2026-09-23, when post analytics moved
#: up; six until 2026-11-27, when saved posts moved up).
_CLAIMED_REFUSED = {
    "linkedin live": "https://www.linkedin.com/video/live/",
    "hashtags": "https://www.linkedin.com/feed/hashtag/",
    "article drafts": "https://www.linkedin.com/article/drafts/",
    "scheduled posts": "https://www.linkedin.com/scheduled-posts/",
    "media upload": "https://www.linkedin.com/mypreferences/d/media-upload/",
}

#: Mutation kinds the correction block asserts are sanctioned.
_CLAIMED_SANCTIONED_KINDS = ("set_input_files", "fill")


def _text() -> str:
    return _CENSUS.read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# Control 1 -- the claims are found at all


def test_the_correction_block_is_readable() -> None:
    body = _text()
    assert "## 4. THE READ BOUNDARY IS THE STRUCTURAL CAUSE" in body, (
        "section 4 is not where this guard expects it. If it moved, this "
        "guard has to move with it; a claim-checker that cannot find its "
        "claims passes over everything."
    )
    assert _COUNT_CLAIM.search(body), (
        "the allowlist-count claim row is not parseable any more. Reformat "
        "the table and this guard stops checking, which is exactly the "
        "failure it exists to prevent."
    )


# --------------------------------------------------------------------------
# Control 2 -- the boundary is not mute


def test_the_boundary_instrument_is_alive() -> None:
    """It must be shown REFUSING and ACCEPTING in the same run.

    Without this, every False below could come from a broken `is_read_url`
    and the table would look like a careful measurement.
    """
    assert readonly.is_read_url("https://www.linkedin.com/feed/") is True
    assert readonly.is_read_url("https://www.linkedin.com/psettings/") is False
    assert readonly.is_read_url("https://example.com/") is False


# --------------------------------------------------------------------------
# The claims


def test_the_allowlist_count_in_the_census_matches_the_shipped_boundary() -> None:
    found = _COUNT_CLAIM.search(_text())
    stated_then, stated_now = (int(found.group(1)), int(found.group(2)))
    actual = len(readonly._ALLOWED_URL_PATTERNS)
    assert stated_now == actual, (
        "the census says the read allowlist holds %d patterns; it holds %d. "
        "The original claim of %d was already stale for seventeen days before "
        "anyone measured it -- update the census, not this assertion."
        % (stated_now, actual, stated_then)
    )


@pytest.mark.parametrize(("surface", "url"), sorted(_CLAIMED_REACHABLE.items()))
def test_a_surface_the_census_calls_reachable_is_reachable(surface, url) -> None:
    assert readonly.is_read_url(url) is True, (
        "the census says %s is reachable at %s and the boundary refuses it. "
        "Either a pattern was removed or the census is wrong; both need a "
        "decision, not a quiet edit." % (surface, url)
    )


@pytest.mark.parametrize(("surface", "url"), sorted(_CLAIMED_REFUSED.items()))
def test_a_surface_the_census_calls_refused_is_refused(surface, url) -> None:
    assert readonly.is_read_url(url) is False, (
        "the census says %s still refuses, and the boundary now admits %s. "
        "An admission is a decision; if one was made, the census's structural "
        "argument has moved with it." % (surface, url)
    )


@pytest.mark.parametrize("kind", _CLAIMED_SANCTIONED_KINDS)
def test_a_mutation_kind_the_census_calls_sanctioned_is_sanctioned(kind) -> None:
    kinds = {verb for _path, _fn, verb in readonly.SANCTIONED_MUTATIONS}
    assert kind in kinds, (
        "the census's correction block asserts %r is a sanctioned mutation "
        "kind and it is not in readonly.SANCTIONED_MUTATIONS. If the sanction "
        "was withdrawn, ten GAP rows' stated reason changes back." % kind
    )


def test_the_census_does_not_still_claim_the_sanction_is_missing() -> None:
    """The ORIGINAL sentence may stay; the correction must sit beside it.

    This repository preserves superseded text rather than deleting it, so the
    words `set_input_files` ... `has not been` are expected to remain. What
    must also be present is the correction, or a reader starting from the
    claim reaches the wrong answer -- the defect
    `a-correction-cannot-be-found-from-the-claim` names.
    """
    body = _text()
    assert "SANCTIONED_MUTATIONS" in body, (
        "section 4 states the sanction is missing and nothing in this file "
        "names the list that now holds it"
    )
    assert "CORRECTED 2026-09-20" in body


#: Section 4's heading, and the opening words of the left cell of the row that
#: corrects the original "nothing in it reaches ..." sentence. The row is
#: found by those words, so a reformat that loses them fails loudly instead
#: of leaving this guard reading nothing.
_SECTION_4 = "## 4. THE READ BOUNDARY"
_REACHABLE_ROW_OPENS = "nothing in it reaches"


def _section_4(text: str) -> str | None:
    """Section 4's text, from its heading to the next ``## `` heading."""
    if _SECTION_4 not in text:
        return None
    body = text.split(_SECTION_4, 1)[1]
    end = re.search(r"^## ", body, flags=re.M)
    return body[: end.start()] if end else body


def _reachable_row(text: str) -> tuple[list[str] | None, str]:
    """(the row's cells, or None, and what was found where it was looked for).

    The rows of section 4's correction table sit in a blockquote, so each
    opens ``> |``; the quote marker is cut and the census's own cell reader
    splits the rest. Exactly one row may open with the claim's words, and it
    must have two cells: what the section said, and what was measured.
    """
    section = _section_4(text)
    if section is None:
        return None, f"no {_SECTION_4!r} heading in the census"
    rows = []
    for line in section.splitlines():
        body = line.strip()
        if body.startswith(">"):
            body = body[1:].strip()
        if not body.startswith("|"):
            continue
        cells = count_census_states.cells(body)
        if cells and cells[0].lower().startswith(_REACHABLE_ROW_OPENS):
            rows.append(cells)
    if len(rows) != 1:
        return None, (
            f"{len(rows)} rows of section 4 open with "
            f"{_REACHABLE_ROW_OPENS!r}; the guard reads exactly one"
        )
    if len(rows[0]) != 2:
        return None, f"the row has {len(rows[0])} cells, not 2: {rows[0]!r}"
    return rows[0], "found"


def _address_of(url: str) -> str:
    """A claimed url as the census writes an address: its path, every run of
    digits written ``<id>`` (the census names one post as
    ``/analytics/post-summary/urn:li:activity:<id>/``)."""
    path = re.sub(r"^https://www\.linkedin\.com", "", url)
    return re.sub(r"\d+", "<id>", path)


def _named_in(cell: str, surface: str, url: str) -> bool:
    """Is the surface named in the cell, by its name or by its address?"""
    lowered = cell.lower()
    by_name = re.search(r"\b%s\b" % re.escape(surface), lowered)
    return bool(by_name) or _address_of(url) in lowered


def _unnamed_in_the_row(text: str) -> tuple[list[str] | None, str]:
    """(every reachable surface the row's MEASURED cell does not name, or
    None when the row cannot be read, and the reading's own account)."""
    cells, found = _reachable_row(text)
    if cells is None:
        return None, found
    measured = cells[1]
    return [
        surface
        for surface, url in sorted(_CLAIMED_REACHABLE.items())
        if not _named_in(measured, surface, url)
    ], found


def _unnamed_in_the_old_window(text: str) -> list[str]:
    """THE READING THIS GUARD USED UNTIL 2026-11-27, carried verbatim as a
    control: each surface's first word, anywhere in section 4's first 6000
    characters. Only the controls below call it."""
    block = text.split("## 4. THE READ BOUNDARY")[1][:6000].lower()
    return [s for s in _CLAIMED_REACHABLE if s.split()[0] not in block]


def test_the_reachable_surfaces_are_named_in_the_census() -> None:
    """The prose and this guard's list must name the same surfaces.

    Otherwise this file could go on passing while the census's table said
    something else entirely. Read from the reachable-surfaces ROW, its
    measured cell, so the row's place in the section and the length of the
    cells above it do not matter.
    """
    unnamed, found = _unnamed_in_the_row(_text())
    assert unnamed is not None, (
        "the reachable-surfaces row of section 4 cannot be read (%s). If the "
        "table moved or was reworded, this guard has to move with it; a "
        "claim-checker that cannot find its claims passes over everything."
        % found
    )
    assert unnamed == [], (
        "the census's reachable-surfaces row does not name %s, which this "
        "guard calls reachable. Either the census or this guard is wrong, and "
        "the boundary decides which." % unnamed
    )


def _grown(text: str, chars: int) -> str:
    """The census with the COUNT row's measured cell grown by ``chars`` of
    clause, the way every admission grows it."""
    lines = text.split("\n")
    at = [i for i, line in enumerate(lines) if _COUNT_CLAIM.search(line)]
    assert len(at) == 1, at
    row = lines[at[0]].rstrip("\r")
    assert row.endswith("|"), row[-40:]
    clause = " and a further admitted line, named by its ruling" * (chars // 50 + 1)
    lines[at[0]] = row[:-1].rstrip() + clause + " |"
    return "\n".join(lines)


def test_a_cell_grown_past_the_old_window_cannot_hide_the_row() -> None:
    """RED FIRST, KEPT AS A CONTROL. Grow the count cell by 6000 characters:
    the old window reading loses surfaces, the row reading loses none.

    The first half is what makes the input discriminating: a grown census the
    OLD reading still passed would show nothing about the new one.
    """
    grown = _grown(_text(), 6000)
    assert _COUNT_CLAIM.search(grown), "growing the cell broke the count claim"
    assert _section_4(grown) is not None, "the census has no section 4 to read"
    lost = _unnamed_in_the_old_window(grown)
    assert lost, "the grown cell did not push any surface out of the old window"
    unnamed, found = _unnamed_in_the_row(grown)
    assert unnamed == [], (unnamed, found)


def test_the_row_reader_can_fail() -> None:
    """SHOWN FAILING: take "saved posts" out of the measured cell, by name and
    by address, and the row reading must name exactly that surface."""
    text = _text()
    cells, found = _reachable_row(text)
    assert cells is not None, found
    measured = cells[1]
    stripped = measured.replace("saved posts", "a list").replace(
        "/my-items/saved-posts/", "/a-list/"
    )
    assert stripped != measured, "the mutation changed nothing in the cell"
    mutated = text.replace(measured, stripped, 1)
    assert mutated != text, "the cell as read is not the cell as written"
    unnamed, _found = _unnamed_in_the_row(mutated)
    assert unnamed == ["saved posts"], unnamed


# --------------------------------------------------------------------------
# Control 3 -- shown failing


def test_the_claim_reader_can_fail() -> None:
    """SHOWN FAILING. Mutate the claim and the comparison must not survive it."""
    body = _text()
    found = _COUNT_CLAIM.search(body)
    assert found is not None
    actual = len(readonly._ALLOWED_URL_PATTERNS)
    mutated = body.replace(found.group(0), found.group(0).replace(
        "**%d**" % actual, "**%d**" % (actual + 1), 1
    ), 1)
    again = _COUNT_CLAIM.search(mutated)
    assert again is not None, "the mutation broke the pattern, not the claim"
    assert int(again.group(2)) != actual, (
        "a census claiming one more pattern than the boundary holds was read "
        "as agreeing with it; this comparison cannot fail and certifies "
        "nothing"
    )


def test_the_reachability_check_can_fail() -> None:
    """SHOWN FAILING, the other half: an address nobody admits must refuse."""
    assert readonly.is_read_url(
        "https://www.linkedin.com/an-address-no-pattern-admits/"
    ) is False
