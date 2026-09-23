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
"""

from __future__ import annotations

import pathlib
import re

import pytest

from linkedin_server import readonly

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
}

#: Surfaces the correction block says still REFUSE. Six of the eleven the
#: original sentence named (seven until 2026-09-23; post analytics moved up).
_CLAIMED_REFUSED = {
    "linkedin live": "https://www.linkedin.com/video/live/",
    "saved posts": "https://www.linkedin.com/my-items/saved-posts/",
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


def test_the_reachable_surfaces_are_named_in_the_census() -> None:
    """The prose and this guard's list must name the same surfaces.

    Otherwise this file could go on passing while the census's table said
    something else entirely.
    """
    block = _text().split("## 4. THE READ BOUNDARY")[1][:6000].lower()
    for surface in _CLAIMED_REACHABLE:
        assert surface.split()[0] in block, surface


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
