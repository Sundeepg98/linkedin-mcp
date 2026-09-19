"""A job-collections reader that matches IN THE PAGE and returns INTEGERS.

``JOB-COLLECTIONS-SURFACE`` (census ``J 42``) had its address admitted by
``tests/test_school_and_collections_boundary.py`` **with nothing behind it** --
Amendment A10's shape -- and nobody had opened it until 2026-09-19.

## WHY THE OBVIOUS INSTRUMENT CANNOT SERVE, measured before this was written

``dom.read_surface_census`` is a CENSUS: it counts and it SHAPES. It carries
``has_href`` and ``href_shape`` and **never hands out a raw href by
construction**. Asking it for ``href`` returns a value indistinguishable from
absence -- measured on this very surface, ``(no href)`` on **147 of 147**
controls of a page made entirely of links. Shaping is exactly what makes it
unusable as a parser, and that is the shaper doing its job rather than a defect.

So a reader was needed, and the question was what it may look at.

## THE RULE THIS MODULE KEEPS: NO PAGE STRING CROSSES THE BOUNDARY

Stricter than ``groups.py``, which takes hrefs somebody else read, and stricter
than ``menus.py``, whose ``classify`` is a pure Python function that IS handed a
label and refuses to return any part of it.

**Here the vocabulary is shipped INTO the page and only an INTEGER INDEX comes
back.** The comparison happens in the document; what crosses the CDP boundary is
a position in a tuple defined in this file. A label is therefore not redacted,
not shaped, and **not present in this process at all** -- which is a different
and stronger claim than either sibling makes, and the only one that needs no
argument about what a shaper can and cannot recognise.

**THE OUTPUT ALPHABET IS CLOSED AND THAT IS THE SAFETY PROPERTY.** Every term
this module can emit is a literal in :data:`GROUPINGS`. An index outside its
range is refused rather than clamped, because a clamp would silently rename one
grouping to another and a census built on it would be wrong in a way nobody
could see.

## THE VOCABULARY IS LINKEDIN'S, NOT MINE

:data:`GROUPINGS` is the five groupings the census row names, sourced there to
LinkedIn's own help article ``a1652837``. **It is not invented and not read off
the page** -- inventing a vocabulary from what a page happens to draw is how a
closed set stops being closed. A grouping LinkedIn adds tomorrow comes back
``unmatched`` with a COUNT, never with its name, and the fix is a deliberate
edit here.

## NO LABEL IS A PARAMETER OF ANY FUNCTION IN THIS MODULE

Copied from ``groups.py`` and ``menus.py``, including the reason. The only
function that touches the page is :func:`read_collections`, and what it returns
is indices and integers. :func:`tally` -- the function a caller publishes --
takes a list of INDICES and cannot be handed a label even by mistake.
``tests/test_collections_page.py`` asserts the signatures, because a property
stated only in prose is the defect this repository has recorded more than once.

## WHAT THIS MODULE DOES NOT CLAIM

* **Not that the groupings it finds are all of them.** The page's control count
  moved 75 -> 93 across five minutes on 2026-09-19, so any count off this
  surface is a reading with a timestamp and :func:`tally` reports what it was
  handed rather than what exists.
* **Not that an unmatched heading is not a grouping.** It reports a count of
  unmatched headings precisely so that a vocabulary going stale is VISIBLE as a
  number instead of arriving as a silent zero.
"""

from __future__ import annotations

from typing import Any, Iterable, Optional, Sequence

#: LinkedIn's five job-collection groupings, as the census row names them,
#: sourced there to help article ``a1652837``. THE ORDER IS THE CONTRACT: the
#: page returns a position in this tuple, so reordering it silently renames
#: every reading ever taken. ``tests/test_collections_page.py`` pins it.
GROUPINGS: tuple[str, ...] = (
    "domains",
    "industries",
    "company benefits",
    "editorial",
    "corporate commitments",
)

#: What a caller sees when the page drew a heading the vocabulary does not know.
#: A TERM, not a label -- an unmatched heading is counted and never named.
UNMATCHED = "unmatched"

#: Refusals, each a literal. A reader that cannot say why it is empty is the
#: green this repository distrusts most.
REFUSALS: tuple[str, ...] = (
    "no_headings_drawn",
    "index_out_of_range",
)

#: The in-page matcher. **THE VOCABULARY IS AN ARGUMENT, NEVER A CONSTANT
#: HERE** -- the page is handed the terms this module defines and hands back a
#: position, so this function is the whole of the boundary crossing and its
#: return type is the safety property. Word-bounded rather than a bare
#: ``includes``: ``writes._recipient_gate`` once used a bare ``indexOf`` and
#: could have committed a stranger to an irreversible message, and a bare
#: ``editorial`` would match a heading about an editorial team.
_MATCH_IN_PAGE = """
(args) => {
  const vocabulary = args.vocabulary || [];
  const html = args.html || "";
  const norm = (s) => (s || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
  const wordBounded = (hay, needle) => {
    if (!hay || !needle) return false;
    const h = " " + hay + " ";
    const n = " " + needle + " ";
    return h.indexOf(n) !== -1;
  };
  // THE CONTROL PATH, and it is the reason this takes an object rather than a
  // bare vocabulary. When ``html`` is supplied the SAME matching code runs
  // against a DETACHED container, so a positive control can be run on any page
  // without navigating anywhere. A matcher that returns zero everywhere is
  // indistinguishable from a broken one, and this repository has been bitten
  // by exactly that -- so the demonstration that it CAN match ships with it
  // rather than living in a side script that can drift.
  let root = document;
  if (html) {
    root = document.createElement("div");
    root.innerHTML = html;
  }
  // HEADINGS AND TAB-LIKE CONTROLS BOTH. Measured 2026-09-19: the live page
  // draws 18 headings and matched NONE of the five groupings, while carrying
  // 47 buttons -- and LinkedIn renders a collection strip as pressable pills,
  // not as headings. Scanning headings alone could not tell "he has no
  // collections" from "the labels are not headings".
  const headings = Array.from(
    root.querySelectorAll(
      "h1, h2, h3, [role='heading'], [role='tab'], button, a[role='button']"
    )
  );
  const out = [];
  for (const node of headings) {
    const text = norm(node.textContent);
    if (!text) continue;
    let index = -1;
    for (let i = 0; i < vocabulary.length; i += 1) {
      if (wordBounded(text, vocabulary[i])) { index = i; break; }
    }
    // A SECTION'S CARD COUNT, taken from the heading's own container so it is
    // a count of what sits UNDER that heading rather than of the whole page.
    let scope = node.closest("section, li, div[data-view-name]") || node.parentElement;
    let cards = 0;
    if (scope) {
      cards = scope.querySelectorAll("a[href*='/jobs/view/'], li").length;
    }
    out.push({ index: index, cards: cards });
  }
  // INTEGERS ONLY. No element text is in this return value, by construction:
  // every field above is a number.
  return { headings: headings.length, matches: out };
}
"""


async def read_collections(page: Any, html: str = "") -> dict[str, Any]:
    """Run the matcher in the page. Returns indices and integers, never text.

    THE ONLY FUNCTION HERE THAT TOUCHES A PAGE, and the vocabulary it ships is
    :data:`GROUPINGS`. What comes back is positions in that tuple.

    ``html`` IS THE CONTROL PATH AND IT IS NOT A READING OF ANYTHING. When it
    is supplied the same in-page matcher runs against a DETACHED container
    built from that string, so :func:`control_fixture` can prove the matcher
    CAN match without navigating. It is a parameter of the READER, never of
    :func:`tally`, so nothing a caller publishes can be handed a page string
    through it.
    """
    raw = await page.evaluate(
        _MATCH_IN_PAGE, {"vocabulary": list(GROUPINGS), "html": html or ""}
    )
    matches = list((raw or {}).get("matches") or [])
    return {
        "headings_seen": int((raw or {}).get("headings") or 0),
        "indices": [int(m.get("index", -1)) for m in matches],
        "cards": [int(m.get("cards", 0)) for m in matches],
    }


def term_for(index: int) -> str:
    """One index -> one literal of this module. Out of range REFUSES.

    Never clamped. A clamp would silently rename one grouping to another, and
    a census built on that would be wrong in a way nobody could see.
    """
    if index == -1:
        return UNMATCHED
    if 0 <= index < len(GROUPINGS):
        return GROUPINGS[index]
    return "index_out_of_range"


def tally(indices: Iterable[int], cards: Optional[Sequence[int]] = None) -> dict[str, Any]:
    """COUNTS BY TERM. Its parameter is INDICES -- a label cannot reach it.

    ``cards`` is optional and positional-by-index against ``indices``; when it
    is short, the missing entries are counted as unknown rather than as zero,
    because a zero and an absence are different answers and collapsing them is
    how a surface reports "he has nothing" when it means "I could not see".
    """
    counts: dict[str, int] = {}
    per_term_cards: dict[str, int] = {}
    unknown_cards = 0
    card_list = list(cards or [])
    for position, index in enumerate(indices):
        term = term_for(int(index))
        counts[term] = counts.get(term, 0) + 1
        if position < len(card_list):
            per_term_cards[term] = per_term_cards.get(term, 0) + int(card_list[position])
        else:
            unknown_cards += 1
    return {
        "by_term": dict(sorted(counts.items())),
        "cards_by_term": dict(sorted(per_term_cards.items())),
        "sections_with_unknown_cards": unknown_cards,
        "matched_groupings": sum(
            value for key, value in counts.items()
            if key in GROUPINGS
        ),
        "unmatched_headings": counts.get(UNMATCHED, 0),
    }


def emitted_alphabet() -> frozenset[str]:
    """Every string this module can publish. Asserted in the tests.

    The point of naming it as a function rather than describing it in prose:
    the test compares this against what ``tally`` actually emits over
    adversarial input, so a new literal added below without a thought fails
    there rather than reaching a caller.
    """
    return frozenset(GROUPINGS) | {UNMATCHED} | set(REFUSALS)


def control_fixture() -> str:
    """A synthetic DOM that MUST match all five groupings. The positive control.

    **THIS EXISTS BECAUSE THE LIVE READ RETURNED ZERO.** Zero matches on a real
    page is two different findings -- the groupings are not drawn, or the
    matcher cannot see them -- and nothing in the reading separates them. A
    control that must fire does.

    It is SYNTHETIC and carries no page text: every string in it is a literal
    from :data:`GROUPINGS` plus markup. Running it costs no page load, because
    :func:`read_collections` matches it in a detached container.
    """
    rows = "".join(
        f"<section><h2>{term.title()}</h2><ul><li></li><li></li></ul></section>"
        for term in GROUPINGS
    )
    # A heading the vocabulary must NOT match, so the control also proves the
    # matcher discriminates rather than matching everything it is shown.
    return rows + "<section><h2>Saved searches</h2><ul><li></li></ul></section>"
