"""Read an organisation Page's OWN PROSE off its Page root -- the Home view's
Overview card -- and COUNT the feed items the view drew. Census row ``J 110``.

THE RULING THIS READS UNDER. ``J 110``'s cell recorded that a Page's prose was
MEASURED AND NOT PUBLISHED (``shape.company_about_card``'s standing decision),
because a person's name can sit inside it and nothing here can clear it. The
orchestrator reopened it on 2026-10-10 as THIRD-PARTY-TEXT-AT-RUNTIME,
applying the operator's NAMES-AT-RUNTIME: an organisation Page's prose is
returned at runtime under PEOPLE-DATA-MITIGATIONS --

* returned as UNTRUSTED third-party text: it leaves only inside a
  ``people_data.OrganisationProse`` record, whose envelope carries the
  package's untrusted-text marker;
* SANITISED by ``people_data.sanitise`` (NFC; controls, zero-width,
  bidirectional and other invisible characters removed; whitespace collapsed);
* BOUNDED at ``people_data.PROSE_CAP`` characters, with ``truncated`` saying
  when the page held more -- and the page hands at most
  :data:`MAX_CHARS_CARRIED` characters across the boundary in the first place;
* NEVER STORED: nothing here writes, caches or logs it, and an exception is
  reduced to its TYPE before it can carry a library's message that quotes the
  page (ERROR-MESSAGE-RULED-AT-THE-RAISE).

FEED-CONTENT-READ-RULING's counts-only rule still governs what is stored, and
a FEED ITEM'S OWN WORDS ARE NOT READ HERE AT ALL: they are census row
``M C43``'s, under the same ruling, and this module COUNTS the items only.

WHAT WAS MEASURED, AND ON WHICH CAPTURE (lane B4, 2026-10-10)
-------------------------------------------------------------
Three RAW captures of a Page root (``/company/<x>/``, as the census capture
inventory records them), taken 2026-09-20 and 2026-09-23, each drew the HOME
view: the tab nav's ``aria-current="true"`` anchor is the Home tab
(``/company/<x>/home/``), and inside ``main`` each draws exactly ONE ``h2``
reading ``Overview``, whose card -- the nearest ancestor carrying
``componentkey``, two hops up on all three -- holds exactly ONE
``[data-testid="expandable-text-box"]`` whose only element children are
``br``. That box is the Page's description. The Home view's posts sit under an
``h2`` reading ``Page posts``, five ``role="listitem"`` entries in its card on
all three. ``tests/fixtures/live1/company_root_home_view.html`` is the
2026-09-23 one, reduced to structure with declared synthetic prose.

THE SAME ADMITTED ROOT ADDRESS DREW THE POSTS VIEW ON 2026-10-10. The live
lane's session-9 load of a Page root (a skeleton, keyed) marks the POSTS tab
current, draws no ``Overview`` heading, and is a feed of thirteen items, each
under an ``h2`` reading ``Feed post``. ``tests/fixtures/live9/
company_root_posts_view.html`` is that skeleton reduced the same way. So a Page
root is NOT always its Home view, and this reader says which view it read
(:data:`VIEW_SEGMENTS`) before it says anything about prose: a Posts view
reads ``not_drawn`` for the Overview, which is a fact about the VIEW and never
an empty description.

THE PAGE MAY VETO, NEVER SUPPLY. Nothing read here becomes an address, a
target or an argument. The one string that crosses back is the description,
and it crosses into a record.

IT FIRES NOTHING. No function here presses, types or takes a confirm token.
"""

from __future__ import annotations

from typing import Any

from linkedin_server import coerce, people_data

#: The heading LinkedIn draws over the Home view's description card, MEASURED
#: on the three September Home-view captures (one each, in ``main``).
OVERVIEW_HEADINGS: tuple[str, ...] = ("Overview",)

#: The heading over the Home view's posts, MEASURED (one each, five list
#: items in its card on each).
POSTS_SECTION_HEADINGS: tuple[str, ...] = ("Page posts",)

#: The accessible heading LinkedIn draws over every feed item, MEASURED: one
#: on the 2026-09-23 Home view, thirteen on the 2026-10-10 Posts view.
FEED_ITEM_HEADING = "Feed post"

#: The text box's hook, MEASURED on every capture: the description on the
#: Home view, each item's words on the Posts view.
TEXT_BOX_TESTID = "expandable-text-box"

#: How far above its heading a card may sit. Measured at 2; the room is for a
#: wrapper LinkedIn adds, and the bound keeps a heading from claiming the page.
CARD_HOPS = 4

#: THE CLOSED VIEW ALPHABET: the second path segment of the Page tab the page
#: marks current. A reading is a POSITION here, computed inside the page by
#: equality, so no string of the page's crosses back for it.
VIEW_SEGMENTS: tuple[str, ...] = (
    "home", "about", "posts", "jobs", "people", "insights", "life",
    "products", "services", "events", "videos",
)

#: What a view position outside :data:`VIEW_SEGMENTS` means. ``-1``: no Page
#: tab was marked current; ``-2``: the marked tabs disagree; ``-3``: one tab
#: was marked and its segment is in no list here.
VIEW_REFUSALS: dict[int, str] = {
    -1: "no_current_tab",
    -2: "tabs_disagree",
    -3: "unrecognised_tab",
}

#: THE CLOSED STATE ALPHABET FOR THE OVERVIEW. Position 0 asserts nothing
#: about the organisation, so a refused reading lands where it is harmless.
OVERVIEW_STATES: tuple[str, ...] = (
    "reader_blind",
    "not_drawn",
    "several_headings",
    "no_card",
    "no_text_box",
    "several_text_boxes",
    "empty_after_sanitising",
    "read",
)

#: The most characters the page hands across the boundary: twice the record's
#: cap, so the record can tell a cut text from one that merely ended there.
MAX_CHARS_CARRIED = 2 * people_data.PROSE_CAP

#: Subtrees of the text box whose text is NOT the description: non-content,
#: and the expander control, whose label is LinkedIn's and not the Page's.
SKIPPED_TAGS: tuple[str, ...] = (
    "SCRIPT", "STYLE", "TEMPLATE", "NOSCRIPT", "BUTTON", "SVG", "IFRAME", "OBJECT",
)

#: The in-page reader. It returns integers, one view POSITION, and the text of
#: ONE text box -- the description -- sliced to ``max_chars``. A ``br`` is a
#: line break; a skipped subtree (above), anything ``aria-hidden="true"`` and
#: anything ``hidden`` is stepped over and COUNTED.
HOME_JS = r"""
(args) => {
  const out = {
    main: 0, elements: 0, current_tabs: 0, view: -1, headings: 0, cards: 0,
    boxes: 0, text: null, chars: 0, runs: 0, skipped: 0, posts_sections: 0,
    posts_items: 0, feed_item_headings: 0,
  };
  const norm = (s) => String(s == null ? '' : s).replace(/\s+/g, ' ').trim();
  const main = document.querySelector('main');
  if (!main) return out;
  out.main = 1;
  out.elements = main.getElementsByTagName('*').length;

  const seen = new Set();
  for (const anchor of document.querySelectorAll('a[aria-current="true"]')) {
    let path = '';
    try {
      path = new URL(anchor.getAttribute('href') || '', 'https://www.linkedin.com').pathname;
    } catch (e) {
      continue;
    }
    const segments = path.split('/').filter(Boolean);
    if (segments.length < 3 || segments[0] !== 'company') continue;
    out.current_tabs += 1;
    seen.add(args.views.indexOf(segments[2]));
  }
  if (out.current_tabs > 0) {
    if (seen.size > 1) out.view = -2;
    else {
      const only = Array.from(seen)[0];
      out.view = only >= 0 ? only : -3;
    }
  }

  const nearestCard = (element) => {
    let node = element.parentElement;
    for (let hop = 1; node && hop <= args.hops; hop += 1) {
      if (node.hasAttribute('componentkey')) return node;
      node = node.parentElement;
    }
    return null;
  };
  const headed = (words) => Array.from(main.querySelectorAll('h2')).filter(
    (h) => words.includes(norm(h.textContent)));

  const headings = headed(args.overview);
  out.headings = headings.length;
  if (headings.length === 1) {
    const card = nearestCard(headings[0]);
    if (card) {
      out.cards = 1;
      const boxes = card.querySelectorAll('[data-testid="' + args.testid + '"]');
      out.boxes = boxes.length;
      if (boxes.length === 1) {
        const parts = [];
        const visit = (node) => {
          for (const child of Array.from(node.childNodes)) {
            if (child.nodeType === 3) {
              parts.push(child.data);
              out.runs += 1;
            } else if (child.nodeType === 1) {
              const tag = String(child.tagName || '').toUpperCase();
              if (tag === 'BR') {
                parts.push('\n');
              } else if (args.skipped.includes(tag)
                  || child.getAttribute('aria-hidden') === 'true'
                  || child.hasAttribute('hidden')) {
                out.skipped += 1;
              } else {
                visit(child);
              }
            }
          }
        };
        visit(boxes[0]);
        const whole = parts.join('');
        out.chars = whole.length;
        out.text = whole.slice(0, args.max_chars);
      }
    }
  }

  const sections = headed(args.posts_headings);
  out.posts_sections = sections.length;
  for (const heading of sections) {
    const card = nearestCard(heading);
    if (card) out.posts_items += card.querySelectorAll('[role="listitem"]').length;
  }
  out.feed_item_headings = headed([args.feed_heading]).length;
  return out;
}
"""

#: The integer fields the page returns, by name.
_COUNT_FIELDS: tuple[str, ...] = (
    "main", "elements", "current_tabs", "headings", "cards", "boxes", "chars",
    "runs", "skipped", "posts_sections", "posts_items", "feed_item_headings",
)


def _arguments() -> dict[str, Any]:
    """What is shipped INTO the page: strings this package authored."""
    return {
        "overview": list(OVERVIEW_HEADINGS),
        "posts_headings": list(POSTS_SECTION_HEADINGS),
        "feed_heading": FEED_ITEM_HEADING,
        "testid": TEXT_BOX_TESTID,
        "views": list(VIEW_SEGMENTS),
        "hops": CARD_HOPS,
        "max_chars": MAX_CHARS_CARRIED,
        "skipped": list(SKIPPED_TAGS),
    }


def view_for(position: Any) -> str:
    """One view position -> one literal. Out of range REFUSES, never clamps."""
    number = coerce.as_int(position)
    if number is None:
        return "position_out_of_range"
    if 0 <= number < len(VIEW_SEGMENTS):
        return VIEW_SEGMENTS[number]
    return VIEW_REFUSALS.get(number, "position_out_of_range")


def emitted_alphabet() -> frozenset[str]:
    """Every token this module can publish in a ``view`` or ``state`` field."""
    return (
        frozenset(VIEW_SEGMENTS)
        | frozenset(VIEW_REFUSALS.values())
        | frozenset(OVERVIEW_STATES)
        | {"position_out_of_range"}
    )


def _unread_home(error: Any = None) -> dict[str, Any]:
    """The answer for a page this reader could not read: every field reset."""
    return _home_answer({}, error=error)


async def read_company_home(page: Any) -> dict[str, Any]:
    """The view the Page root drew, its Overview prose as ONE untrusted
    record, and the feed items it drew as COUNTS. THE ONLY FUNCTION HERE THAT
    TOUCHES A PAGE.

    **AN EXCEPTION IS REDUCED TO ITS TYPE.** A library's message can quote the
    page, and the prose is exactly what it would quote; every field is reset
    and ``error`` names the type (ERROR-MESSAGE-RULED-AT-THE-RAISE).
    """
    try:
        raw = await page.evaluate(HOME_JS, _arguments())
    except Exception as exc:  # noqa: BLE001 -- the type is kept, never the message
        return _unread_home(error=type(exc).__name__)
    return _home_answer(raw if isinstance(raw, dict) else {})


def _home_answer(source: dict[str, Any], *, error: Any = None) -> dict[str, Any]:
    """Shape one in-page reading. Integers through ``coerce``; the one string
    through ``people_data``; everything else is this module's own words."""
    counts = {
        name: max(0, coerce.as_count(source.get(name))) for name in _COUNT_FIELDS
    }
    view = view_for(source.get("view")) if counts["main"] else "no_current_tab"
    record = None
    text = source.get("text")
    reached_the_box = (
        counts["main"] and counts["headings"] == 1 and counts["cards"] == 1
        and counts["boxes"] == 1
    )
    if reached_the_box and isinstance(text, str):
        record = people_data.OrganisationProse.from_page(
            text=text,
            read_from=people_data.PROSE_SOURCES[0],
            cut_before=counts["chars"] > len(text),
        )
    state = _overview_state(counts, record, error)
    return {
        "view": view,
        "tabs_marked_current": counts["current_tabs"],
        "overview": {
            "state": state,
            "prose": None if record is None else record.envelope(),
            "headings": counts["headings"],
            "text_boxes": counts["boxes"],
            "subtrees_skipped": counts["skipped"],
            "why": _overview_why(state, view, counts),
        },
        # COUNTS ONLY. A feed item's own words are census row M C43's.
        "feed_items": {
            "page_posts_sections": counts["posts_sections"],
            "page_posts_items": counts["posts_items"],
            "feed_item_headings": counts["feed_item_headings"],
        },
        "elements_walked": counts["elements"],
        "error": error if isinstance(error, str) else None,
    }


def _overview_state(counts: dict[str, int], record: Any, error: Any) -> str:
    if error is not None or not counts["main"] or counts["elements"] <= 0:
        return "reader_blind"
    if counts["headings"] == 0:
        return "not_drawn"
    if counts["headings"] > 1:
        return "several_headings"
    if counts["cards"] == 0:
        return "no_card"
    if counts["boxes"] == 0:
        return "no_text_box"
    if counts["boxes"] > 1:
        return "several_text_boxes"
    if record is None:
        return "empty_after_sanitising"
    return "read"


def _overview_why(state: str, view: str, counts: dict[str, int]) -> str:
    """This module's own words, with integers interpolated. Never page text."""
    if state == "reader_blind":
        return (
            "no main column was walked, so this is a fact about the READER and "
            "not about the organisation: a page that had not hydrated, a "
            "signed-out load and a restyle all land here."
        )
    if state == "not_drawn":
        if view != "home":
            return (
                "the Page root drew its %s view, not its Home view, and the "
                "Overview card is a Home-view card. This is NOT an empty "
                "description: the root address served a different view." % view
            )
        return (
            "the Home view walked %d element(s) and drew no Overview heading. "
            "This is NOT an empty description: the card was not drawn, or "
            "LinkedIn now words its heading differently." % counts["elements"]
        )
    if state == "several_headings":
        return (
            "%d Overview headings were drawn; picking one would be choosing by "
            "position, so none is read." % counts["headings"]
        )
    if state == "no_card":
        return (
            "the Overview heading has no card within %d levels above it, so "
            "nothing is attributed to it." % CARD_HOPS
        )
    if state == "no_text_box":
        return "the Overview card drew no description box."
    if state == "several_text_boxes":
        return (
            "the Overview card drew %d description boxes; none is read rather "
            "than one chosen." % counts["boxes"]
        )
    if state == "empty_after_sanitising":
        return "the description box held nothing once sanitised."
    return (
        "one Overview card with one description box: its text is returned in "
        "an untrusted-text record, sanitised and bounded, and never stored."
    )
