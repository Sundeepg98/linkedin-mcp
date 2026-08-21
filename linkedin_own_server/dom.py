"""Reading the rendered page.

LinkedIn's class names are generated and its GraphQL query ids rotate with
every deploy, so both make brittle anchors. What does not rotate is the shape
of a link: a person is behind ``/in/<slug>``, a job is behind
``/jobs/view/<id>``. Every list surface here is harvested by finding those
links and taking the text of the card around them.

Three small scripts are injected, and only three. Each is a module-level
constant so it can be read in one place and scanned by
``tests/test_readonly.py`` against :data:`readonly.JS_MUTATION_TOKENS` -- the
scripts query the DOM and read text, and nothing else. The Python side of
each call carries a ``# readonly-ok`` waiver, which is what keeps a future
``evaluate`` from slipping in unreviewed.

The harvesters return ``{"href": ..., "text": ...}`` records. Turning those
into typed rows is ``shape.py``'s job, and it is pure, so the parsing can be
tested without a browser.
"""

from __future__ import annotations

from typing import Any, Optional

from linkedin_own_server.config import logger
from linkedin_own_server.errors import ExtractionFailedError

# ---------------------------------------------------------------------------
# Injected scripts (read-only: query, read text, return)
# ---------------------------------------------------------------------------

#: Harvest cards anchored on a link whose href matches a pattern.
#:
#: The walk up from the link is the whole game. LinkedIn's newer surfaces are
#: nested anonymous DIVs with hash-generated class names -- no ``li``, no
#: ``article``, and ``data-view-name`` is attached by the client AFTER
#: hydration, so it is there or not depending on how far the page got before
#: we read it. When none of those three stops fires, an unbounded walk runs
#: to ``maxHops`` and lands on a container holding the whole list AND the page
#: heading, at which point every row reports the heading as its name. That is
#: measured, not hypothetical: on /analytics/profile-views/ it produced four
#: viewers all called "Who's viewed your profile".
#:
#: So the stop that matters is structural and needs no attribute: a row is the
#: LARGEST ancestor that still speaks for exactly ONE match. One hop further
#: swallows a sibling row. Nothing about that depends on class names, tag
#: names, or how much of the page has hydrated.
#:
#: That rule has a blind spot, and the job tracker fell straight into it: it
#: counts DEDUPED KEYS, so a card carrying two anchors to the SAME job is still
#: "one match" and the walk sails past it. On a tracker page holding a single
#: job the walk therefore ran to ``maxHops`` and every field came back as page
#: furniture -- title "Job tracker", company "Saved <dot> 0". Measured on the
#: real page, not imagined.
#:
#: The second stop closes it: once the row we have ACCEPTED already has text, a
#: candidate holding more matching ANCHORS than one is a container, not a row.
#: The "already has text" clause is what keeps it safe on profile views, where
#: LinkedIn wraps the photo in its own link to the same person: the walk starts
#: on that empty anchor, and a bare link-count stop would freeze there and drop
#: the viewer entirely. Both fixtures pin that.
HARVEST_LINKED_CARDS_JS = """
(cfg) => {
  const re = new RegExp(cfg.hrefPattern);
  const keyOf = (href) => {
    const m = (href || '').match(re);
    return m ? (m[1] || href) : null;
  };
  const keysWithin = (node) => {
    const keys = new Set();
    if (!node.querySelectorAll) return keys;
    for (const link of node.querySelectorAll('a[href]')) {
      const key = keyOf(link.getAttribute('href') || '');
      if (key) keys.add(key);
    }
    return keys;
  };
  const linkWithin = (node) => {
    if (!node.querySelectorAll) return '';
    for (const link of node.querySelectorAll('a[href]')) {
      const href = link.getAttribute('href') || '';
      if (keyOf(href)) return href;
    }
    return '';
  };
  const linksWithin = (node) => {
    if (!node.querySelectorAll) return 0;
    let count = 0;
    for (const link of node.querySelectorAll('a[href]')) {
      if (keyOf(link.getAttribute('href') || '')) count += 1;
    }
    return count;
  };
  const hasText = (node) => !!(node && node.innerText && node.innerText.trim());
  const rowOf = (anchor) => {
    let node = anchor;
    let row = anchor;
    let hops = 0;
    while (node && hops < cfg.maxHops) {
      if (keysWithin(node).size > 1) break;
      // A container, not a row: it repeats the link we came in on, and we
      // already hold something readable. Before we hold text, a second link
      // to the same target is the row's own photo link and must be climbed
      // through rather than stopped at.
      if (hasText(row) && linksWithin(node) > 1) break;
      row = node;
      const tag = node.tagName;
      if (tag === 'LI' || tag === 'ARTICLE') break;
      if (node.dataset && node.dataset.viewName) break;
      node = node.parentElement;
      hops += 1;
    }
    return row;
  };
  const record = (href, node) => {
    const text = (node.innerText || '').trim();
    if (!text) return null;
    return { href: href, text: text.slice(0, cfg.maxChars) };
  };

  const found = [];
  const seen = new Set();
  for (const anchor of document.querySelectorAll('a[href]')) {
    const href = anchor.getAttribute('href') || '';
    const key = keyOf(href);
    if (!key || seen.has(key)) continue;
    seen.add(key);
    found.push({ href: href, row: rowOf(anchor) });
  }

  if (cfg.siblingRows && found.length) {
    // The list is the NEAREST COMMON ANCESTOR of the rows, not the parent of
    // any one of them. Where the walk stopped varies with hydration -- the
    // same page puts the rows at different depths from one load to the next
    // -- so "the rows share a parent" is true on one render and false on the
    // other, and keying on it silently returns nothing extra half the time.
    const rowNodes = found.map((item) => item.row);
    let list = rowNodes[0];
    while (list && !rowNodes.every((node) => list.contains(node))) {
      list = list.parentElement;
    }
    // The list has to be a STRICT ancestor of every row, or its "children"
    // are one row's internals rather than the rows.
    while (list && rowNodes.some((node) => node === list)) {
      list = list.parentElement;
    }
    if (list) {
      const rows = [];
      let orderly = true;
      for (const child of list.children) {
        const keys = keysWithin(child);
        if (child.tagName === 'A') {
          const own = keyOf(child.getAttribute('href') || '');
          if (own) keys.add(own);
        }
        if (keys.size > 1) { orderly = false; break; }
        const item = record(linkWithin(child), child);
        if (item) rows.push(item);
        if (rows.length >= cfg.maxItems) break;
      }
      if (orderly && rows.length >= found.length) return rows;
    }
  }

  const out = [];
  for (const item of found) {
    const rec = record(item.href, item.row);
    if (rec) out.push(rec);
    if (out.length >= cfg.maxItems) break;
  }
  return out;
}
"""

#: Harvest block-shaped cards (notifications) that have no reliable link.
#:
#: Alongside the card's text this returns three things the text alone cannot
#: give, and each one fixes a measured defect:
#:
#: * ``hidden`` -- the strings the page itself marked screen-reader-only.
#:   ``innerText`` includes them, so every notification body arrived with
#:   "Unread notification." or "Status is reachable" welded to the front. They
#:   are returned as a LIST rather than subtracted here, because some of them
#:   are a second copy of the VISIBLE body and deleting those by phrase would
#:   empty the notification. ``shape.parse_notification`` removes one
#:   occurrence per hidden element, which is exact and needs no phrase list.
#: * ``time`` -- the card's own timestamp element. The page writes "2h", with
#:   no "ago", so no amount of scanning the body finds it; ``when`` was null on
#:   all 22 rows.
#: * ``unread`` -- whether LinkedIn was still calling this one unread at the
#:   moment we looked, which is the one fact loading the page destroys.
HARVEST_BLOCK_CARDS_JS = """
(cfg) => {
  const textOf = (node) => (node && node.innerText ? node.innerText.trim() : '');
  for (const selector of cfg.selectors) {
    let nodes;
    try { nodes = document.querySelectorAll(selector); } catch (e) { continue; }
    if (!nodes || nodes.length === 0) continue;
    const out = [];
    for (const node of nodes) {
      const text = textOf(node);
      if (!text) continue;
      const link = node.querySelector('a[href]');
      const hidden = [];
      if (cfg.hiddenSelector) {
        let marked;
        try { marked = node.querySelectorAll(cfg.hiddenSelector); } catch (e) { marked = []; }
        for (const el of marked) {
          const value = textOf(el);
          if (value) hidden.push(value.slice(0, cfg.maxChars));
        }
      }
      let when = '';
      if (cfg.timeSelector) {
        let stamp;
        try { stamp = node.querySelector(cfg.timeSelector); } catch (e) { stamp = null; }
        when = textOf(stamp).slice(0, 40);
      }
      let unread = null;
      if (cfg.unreadClass && node.classList) {
        unread = node.classList.contains(cfg.unreadClass);
      }
      out.push({
        href: link ? (link.getAttribute('href') || '') : '',
        text: text.slice(0, cfg.maxChars),
        hidden: hidden,
        time: when,
        unread: unread,
        selector: selector
      });
      if (out.length >= cfg.maxItems) break;
    }
    if (out.length) return out;
  }
  return [];
}
"""

#: Read the operator's own profile page as a list of SECTIONS.
#:
#: The old version of this script asked for ``main h1`` and for elements with
#: ids ``about`` / ``experience`` / ``education`` / ``skills``. LinkedIn has
#: since rebuilt the profile on server-driven UI: measured 2026-08-22, the page
#: contains ZERO ``h1`` and none of those ids. Every field came back null and
#: the tool errored on its own owner's profile.
#:
#: What survives is the same shape the row walk leans on, one level up: a
#: SECTION is the largest ancestor of its heading that still holds exactly ONE
#: heading. Nothing in that depends on a class name, an id, or a tag beyond
#: h1/h2/h3, and it produces byte-identical topcard lines on the pre-hydration
#: and hydrated renders -- which is the property the two frozen fixtures pin.
#:
#: The climb is bounded by ``main`` rather than by a hop count: a page with a
#: single heading would otherwise walk out to ``documentElement`` and return
#: the entire document as one "section".
#:
#: This returns raw LINES and does no interpretation. Deciding which line is a
#: headline and which is a location is ``shape.py``'s job, where it can be
#: tested without a browser.
READ_PROFILE_JS = """
(cfg) => {
  const textOf = (node) => (node && node.innerText ? node.innerText.trim() : '');
  const linesOf = (node) =>
    textOf(node).split('\\n').map((s) => s.trim()).filter(Boolean);
  const main = document.querySelector('main');
  const headingsIn = (node) =>
    node.querySelectorAll ? node.querySelectorAll('h1,h2,h3').length : 0;
  const sections = [];
  if (main) {
    for (const heading of main.querySelectorAll('h1,h2,h3')) {
      let node = heading;
      let block = heading;
      let hops = 0;
      while (node && node !== main && hops < cfg.maxHops) {
        if (headingsIn(node) > 1) break;
        block = node;
        node = node.parentElement;
        hops += 1;
      }
      sections.push({
        heading: textOf(heading).slice(0, 120),
        lines: linesOf(block).slice(0, cfg.maxLines),
        images: block.querySelectorAll ? block.querySelectorAll('img').length : 0
      });
      if (sections.length >= cfg.maxSections) break;
    }
  }
  return {
    url: document.location.href,
    title: document.title || '',
    has_main: !!main,
    sections: sections
  };
}
"""


# ---------------------------------------------------------------------------
# Harvesters
# ---------------------------------------------------------------------------


async def harvest_linked_cards(
    page: Any,
    *,
    href_pattern: str,
    max_items: int,
    max_chars: int = 1200,
    max_hops: int = 8,
    sibling_rows: bool = False,
) -> list[dict[str, Any]]:
    """Return ``{href, text}`` for each card anchored on a matching link.

    Args:
        sibling_rows: also return the rows that carry NO link, by reading
            every child of the list the linked rows sit in. Off by default,
            because on most surfaces a row without a link is chrome. On
            profile views it is a person: LinkedIn draws privacy-limited
            viewers ("Someone at Acme", "Recruiter at Acme") with no link at
            all, so a harvest anchored only on links cannot see one of them
            and silently reports a shorter list than the page shows. Six of
            ten viewers were invisible this way when it was measured.
    """
    cfg = {
        "hrefPattern": href_pattern,
        "maxItems": int(max_items),
        "maxChars": int(max_chars),
        "maxHops": int(max_hops),
        "siblingRows": bool(sibling_rows),
    }
    try:
        records = await page.evaluate(HARVEST_LINKED_CARDS_JS, cfg)  # readonly-ok
    except Exception as exc:
        raise ExtractionFailedError(
            f"could not read the page: {type(exc).__name__}: {exc}",
            url=_url_of(page),
        ) from exc
    return list(records or [])


async def harvest_block_cards(
    page: Any,
    *,
    selectors: list[str],
    max_items: int,
    max_chars: int = 800,
    hidden_selector: str = "",
    time_selector: str = "",
    unread_class: str = "",
) -> list[dict[str, Any]]:
    """Return ``{href, text, hidden, time, unread, selector}`` per card.

    Args:
        hidden_selector: elements inside a card whose text the page marks
            screen-reader-only. Returned verbatim so the shaper can subtract
            exactly one occurrence of each -- see the script's own note for
            why subtracting by phrase would be wrong.
        time_selector: the element carrying the card's timestamp, for surfaces
            that write the time somewhere the body text never reaches.
        unread_class: a class the card wears while it is unread.
    """
    cfg = {
        "selectors": list(selectors),
        "maxItems": int(max_items),
        "maxChars": int(max_chars),
        "hiddenSelector": str(hidden_selector or ""),
        "timeSelector": str(time_selector or ""),
        "unreadClass": str(unread_class or ""),
    }
    try:
        records = await page.evaluate(HARVEST_BLOCK_CARDS_JS, cfg)  # readonly-ok
    except Exception as exc:
        raise ExtractionFailedError(
            f"could not read the page: {type(exc).__name__}: {exc}",
            url=_url_of(page),
        ) from exc
    return list(records or [])


async def read_profile_fields(
    page: Any,
    *,
    max_sections: int = 40,
    max_lines: int = 60,
    max_hops: int = 20,
) -> dict[str, Any]:
    """Return the profile page's sections, each as a heading plus its lines."""
    cfg = {
        "maxSections": int(max_sections),
        "maxLines": int(max_lines),
        "maxHops": int(max_hops),
    }
    try:
        data = await page.evaluate(READ_PROFILE_JS, cfg)  # readonly-ok
    except Exception as exc:
        raise ExtractionFailedError(
            f"could not read the profile page: {type(exc).__name__}: {exc}",
            url=_url_of(page),
        ) from exc
    return dict(data or {})


async def read_main_text(page: Any) -> str:
    """Return the rendered text of ``main``, or an empty string if there is none.

    A plain Playwright text read -- no script is injected and nothing is
    evaluated. It exists because two facts the job tracker will not put in any
    card are printed in its own furniture: the per-tab COUNTS, and the empty
    state. Without them an empty list and a broken parse look identical, which
    is the failure this whole module is arranged to prevent.
    """
    try:
        return str(await page.inner_text("main") or "")
    except Exception as exc:
        logger.debug("main text unreadable: %s: %s", type(exc).__name__, exc)
        return ""


def _url_of(page: Any) -> str:
    try:
        return str(page.url)
    except Exception:  # pragma: no cover
        return ""


# ---------------------------------------------------------------------------
# Href patterns used by the tools
# ---------------------------------------------------------------------------

#: A person card. The capture group is the public identifier, used to dedupe.
PERSON_HREF = r"/in/([A-Za-z0-9\-_%]{2,})"
#: A job card. The capture group is the numeric job id.
JOB_HREF = r"/jobs/view/(?:[^/?#]*-)?(\d{6,})"

#: One entry on the skills page. LinkedIn hangs an inline edit affordance off
#: every skill on the owner's own profile, and its id is the only per-skill key
#: the page offers -- the names sit in generated-class divs with no list
#: semantics, and ``main ul li`` finds the three filter pills ("All", "Industry
#: Knowledge", "Tools & Technologies"), which is what this tool used to return
#: as the operator's skills.
#:
#: It is used ONLY as a DOM key. Nothing navigates to it, and nothing could:
#: ``readonly._FORBIDDEN_URL_SUBSTRINGS`` blocks ``/edit/`` outright, so a url
#: built from one of these hrefs is refused before the allowlist is even
#: consulted.
SKILL_HREF = r"/details/skills/edit/forms/(\d+)"

#: Notification cards mark their screen-reader-only text with this class, carry
#: their timestamp in this element, and wear this class while unread.
NOTIFICATION_HIDDEN_SELECTOR = ".visually-hidden"
NOTIFICATION_TIME_SELECTOR = "p.nt-card__time-ago"
NOTIFICATION_UNREAD_CLASS = "nt-card--unread"

#: Notification cards, in order of preference. LinkedIn's notification list
#: has no dependable per-item link, so this is the one surface anchored on
#: structure instead. It is also the surface most likely to need updating,
#: which is why a miss raises rather than returning an empty list.
NOTIFICATION_SELECTORS = [
    "article.nt-card",
    "div.nt-card-list article",
    "main article",
    'main [data-view-name*="notification"]',
    "main ul li",
]


def require_rows(
    rows: list[dict[str, Any]],
    *,
    url: str,
    surface: str,
    hint: str = "",
) -> list[dict[str, Any]]:
    """Raise instead of returning nothing.

    An empty list from a page that failed to render is indistinguishable from
    an empty list because the operator genuinely has none, and the two must
    never be confusable. Callers that can legitimately be empty pass through
    :func:`allow_empty` instead.
    """
    if rows:
        return rows
    raise ExtractionFailedError(
        f"nothing readable found on the {surface} page. Either the page did "
        "not finish rendering, the session is not signed in, or LinkedIn "
        "changed this surface. Open the url yourself to see which.",
        url=url,
        hint=hint,
    )


def allow_empty(rows: list[dict[str, Any]], *, surface: str) -> list[dict[str, Any]]:
    """Pass an empty harvest through, logging it."""
    if not rows:
        logger.info("%s: page rendered but held no rows", surface)
    return rows


def parse_all(
    records: list[dict[str, Any]],
    parser,
) -> tuple[list[dict[str, Any]], int]:
    """Run ``parser`` over records, returning ``(rows, dropped_count)``."""
    rows: list[dict[str, Any]] = []
    dropped = 0
    for record in records:
        try:
            parsed: Optional[dict[str, Any]] = parser(record)
        except Exception as exc:  # a bad row must not lose the good ones
            logger.debug("row parse failed: %s: %s", type(exc).__name__, exc)
            parsed = None
        if parsed:
            rows.append(parsed)
        else:
            dropped += 1
    return rows, dropped
