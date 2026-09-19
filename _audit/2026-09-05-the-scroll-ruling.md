# The scroll ruling: NOT sanctioned, and the reason is that it is not needed

A wave measured the job-search result window, found it fixed at seven, and
handed up a boundary question rather than taking it. This is the answer.

## What was measured, and by whom

`job-search-params`, 2026-09-05, 17 live loads:

    LinkedIn reported          2915 postings for the query
    every load returned        exactly 7   (17 of 17)
    max_items asked            200
    parser refusals            0
    growth after 6s            0 on all 17

So the seven is not the cap, not the parser, and not a timing artifact. It is
the window.

**And the docstring told the caller to page with `start=25`.** At a window of
seven that silently skips eighteen of every twenty-five postings. The offset is
by ONES:

    start=0 / 7 / 14  ->  21 distinct postings, zero overlap, zero drift

Validated through the tool itself rather than only the probe.

## The question that was handed up

Widening the window in a single load requires scrolling the results list,
because LinkedIn lazy-loads beyond the first screen. `scroll` is not in
`SANCTIONED_MUTATIONS`, so it is a boundary change and therefore a ruling.

## The ruling: NO, and revisit only on evidence

**Scroll is not sanctioned, because the capability it was proposed to buy is
already reachable without it.** Correct paging returns the same postings that
scrolling would; the wave measured that directly. What scroll buys is *fewer
page loads for the same jobs* -- an efficiency gain, not a capability gain.

**The boundary is the thing protecting his account, and an efficiency gain is
the weakest reason to move it.** Every entry in `SANCTIONED_MUTATIONS` has to
be argued for and lived with; spending one on a saving that correct paging
already delivers is a bad trade in exactly the direction that matters.

This is deliberately NOT the argument that scroll is dangerous. It is not
obviously more dangerous than `click`, which is sanctioned, and inventing a
per-capability bar stricter than the one shipped capabilities already meet is a
mistake this project has recorded. **The objection is sufficiency, not safety.**

## What would REOPEN it

A ruling nobody can reopen is a wall, not a decision. Any one of these reopens
this:

1. **Paging is measured to break down** -- overlap between offsets, drift
   across a sequence, or a ceiling on `start` that caps total reachable
   postings below what the query reports.
2. **The page-load cost becomes the binding constraint** -- if 3 loads for 21
   postings is measured to trip a rate limit or an automation signal that 1
   load for 21 would not, the trade inverts and scroll becomes the SAFER
   option.
3. **A surface exists that has no `start` equivalent at all.** Then scroll is
   not an efficiency but the only route, and this ruling does not cover it.

## The condition attached if it is ever sanctioned

`linkedin_server_info` publishes `rate_discipline.auto_paging: false` and
`max_page_loads_per_call: 2`. **Scrolling a lazy-loading list is auto-paging
under another name.** If scroll is ever admitted, that published claim must be
RE-DERIVED rather than left standing as a stale literal -- this repo's standing
rule is that a surface may not print a claim it cannot derive, and a disclosure
that has quietly become false is more dangerous than a boast, because nobody
re-reads a sentence that flatters nothing.

## What was fixed instead, needing no ruling at all

The docstring now states the real window, and the tool reports the shortfall at
the call site (`count: 7, page_had: 7, capped: False`, plus a note). **A caller
wanting more postings makes three calls at `start=0/7/14` and gets three times
the jobs from the same code.** That was available all along and was hidden by
one wrong number in a docstring.
