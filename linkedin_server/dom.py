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

The harvesters return ``{"href": ..., "text": ...}`` records, plus a handful
of OBSERVATIONS about where that text came from -- which strings the page
marked screen-reader-only, what the matched link itself says, the accessible
name of the entity's logo. They are observations rather than fields on
purpose: deciding which one is the company and which is the location is
``shape.py``'s job, and it is pure, so the parsing can be tested without a
browser.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from linkedin_server import shape
from linkedin_server.config import logger
from linkedin_server.errors import ExtractionFailedError

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
#:
#: Alongside the row's text this returns four OBSERVATIONS about where the
#: text came from. They exist because reading a job card as "line 1, line 2,
#: line 3" makes every field hostage to whatever LinkedIn inserts above it,
#: and LinkedIn inserts plenty: a verified employer adds a screen-reader line
#: reading "<title> with verification", which landed in ``company`` and pushed
#: the real company down into ``location`` on 5 of 14 rows measured live on
#: 2026-08-22. "Promoted", "Viewed", "Actively reviewing applicants", a salary
#: chip and an alumni line were on the same page and are each capable of the
#: same shift. So each field is anchored on the thing that IDENTIFIES it:
#:
#: * ``link_text`` / ``link_hidden`` -- the matched link's own text, and the
#:   screen-reader copies inside it. The link is what MAKES this row a job
#:   row, so its text is the title; subtracting its hidden copies is what
#:   removes the decoration without knowing the phrase.
#: * ``logo_name`` -- the accessible name LinkedIn gives the employer's logo,
#:   "<Company> logo". An image is not a line, so no inserted line moves it.
#: * ``meta_line`` -- the first entry of the metadata list inside the entity
#:   LOCKUP, where the lockup is found without a class name: the smallest
#:   ancestor of the link that also holds that logo. The insight line, the
#:   footer chips and the dismiss button all sit OUTSIDE it.
#:
#: All four are absent when the surface does not offer them -- the job tracker
#: has no logo and no metadata list -- and ``shape.parse_job_card`` falls back
#: to reading lines in order, which is what it has always done.
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
  const anchorWithin = (node) => {
    if (!node || !node.querySelectorAll) return null;
    for (const link of node.querySelectorAll('a[href]')) {
      if (keyOf(link.getAttribute('href') || '')) return link;
    }
    return null;
  };
  const linkWithin = (node) => {
    const link = anchorWithin(node);
    return link ? (link.getAttribute('href') || '') : '';
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
  const textOf = (node) => (node && node.innerText ? node.innerText.trim() : '');
  const hiddenWithin = (node) => {
    const out = [];
    if (!node || !node.querySelectorAll || !cfg.hiddenSelector) return out;
    let marked;
    try { marked = node.querySelectorAll(cfg.hiddenSelector); } catch (e) { marked = []; }
    for (const el of marked) {
      const value = textOf(el);
      if (value) out.push(value.slice(0, cfg.maxChars));
      if (out.length >= cfg.maxHidden) break;
    }
    return out;
  };
  const LOGO = / logo$/i;
  const logoNameIn = (node) => {
    if (!node || !node.querySelectorAll) return '';
    for (const img of node.querySelectorAll('img[alt]')) {
      const alt = (img.getAttribute('alt') || '').trim();
      if (LOGO.test(alt)) return alt.slice(0, alt.length - 5).trim();
    }
    return '';
  };
  // The entity lockup: the smallest ancestor of the link that also holds the
  // employer's logo. Named by nothing -- no class, no id, no tag -- so it
  // survives the generated class names LinkedIn ships.
  const lockupOf = (anchor, row) => {
    let node = anchor;
    let hops = 0;
    while (node && hops <= cfg.maxHops) {
      if (logoNameIn(node)) return node;
      if (node === row) return null;
      node = node.parentElement;
      hops += 1;
    }
    return null;
  };
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
  const record = (href, node, anchor) => {
    const text = (node.innerText || '').trim();
    if (!text) return null;
    const out = {
      href: href,
      text: text.slice(0, cfg.maxChars),
      hidden: hiddenWithin(node)
    };
    // Not a safety clause -- every helper below tolerates a null anchor. It
    // keeps empty keys out of the payload for a sibling row that carries no
    // link at all, which is what profile views are full of.
    if (anchor) {
      out.link_text = textOf(anchor).slice(0, cfg.maxChars);
      out.link_hidden = hiddenWithin(anchor);
      const lockup = lockupOf(anchor, node);
      if (lockup) {
        out.logo_name = logoNameIn(lockup).slice(0, cfg.maxChars);
        const list = lockup.querySelector('ul, ol');
        if (list && list.children.length) {
          out.meta_line = textOf(list.children[0]).slice(0, cfg.maxChars);
        }
      }
    }
    return out;
  };

  const found = [];
  const seen = new Set();
  for (const anchor of document.querySelectorAll('a[href]')) {
    const href = anchor.getAttribute('href') || '';
    const key = keyOf(href);
    if (!key || seen.has(key)) continue;
    seen.add(key);
    found.push({ href: href, row: rowOf(anchor), anchor: anchor });
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
        const item = record(linkWithin(child), child, anchorWithin(child));
        if (item) rows.push(item);
        if (rows.length >= cfg.maxItems) break;
      }
      if (orderly && rows.length >= found.length) return rows;
    }
  }

  const out = [];
  for (const item of found) {
    const rec = record(item.href, item.row, item.anchor);
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
    max_hidden: int = 12,
) -> list[dict[str, Any]]:
    """Return one record per card anchored on a matching link.

    Every record carries ``href`` and ``text``. A record whose card offered
    them also carries ``hidden``, ``link_text``, ``link_hidden``, ``logo_name``
    and ``meta_line`` -- the anchors described on
    :data:`HARVEST_LINKED_CARDS_JS`. They are OBSERVATIONS, not fields: which
    of them is the company and which is the location is decided in
    ``shape.py``, where it can be tested without a browser.

    Args:
        sibling_rows: also return the rows that carry NO link, by reading
            every child of the list the linked rows sit in. Off by default,
            because on most surfaces a row without a link is chrome. On
            profile views it is a person: LinkedIn draws privacy-limited
            viewers ("Someone at Acme", "Recruiter at Acme") with no link at
            all, so a harvest anchored only on links cannot see one of them
            and silently reports a shorter list than the page shows. Six of
            ten viewers were invisible this way when it was measured.
        max_hidden: cap on the screen-reader strings returned per card, so a
            page that marks half of itself hidden cannot inflate a result.
    """
    cfg = {
        "hrefPattern": href_pattern,
        "maxItems": int(max_items),
        "maxChars": int(max_chars),
        "maxHops": int(max_hops),
        "siblingRows": bool(sibling_rows),
        "hiddenSelector": CARD_HIDDEN_SELECTOR,
        "maxHidden": int(max_hidden),
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


#: The employer block on a job posting. LinkedIn labels it itself --
#: ``aria-label="Company, Ashgrove Systems."`` -- and that label is the
#: strongest anchor the page offers: it is the page DECLARING which element
#: is the employer, rather than this module inferring it from position or
#: from a generated class name. Measured on the 2026-08-22 capture: it occurs
#: exactly ONCE in both the pre-hydration and the hydrated render, and not at
#: all in the unrendered shell, which is exactly the discrimination wanted.
#:
#: The posting carries several other ``/company/`` links -- the insights
#: panel, the About-the-company card -- so "the first company link on the
#: page" is NOT the same thing and would drift with LinkedIn's layout.
COMPANY_BLOCK = '[aria-label^="Company,"]'

#: ``Company, Ashgrove Systems.`` -> ``Ashgrove Systems``.
_COMPANY_LABEL = re.compile(r"^\s*Company\s*,\s*(.+?)\s*\.?\s*$", re.I)

#: The employer's slug, taken out of whatever company url the block carries
#: (``/life/``, ``/insights/?insightType=...``). The base page is rebuilt from
#: the slug rather than the href being returned as found, so a tracking query
#: never travels out in a tool result.
_COMPANY_SLUG = re.compile(r"/company/([A-Za-z0-9\-_%]+)")


async def read_job_identity(page: Any) -> dict[str, Any]:
    """Return the employer and the document title of a job posting.

    Both are plain Playwright reads -- an attribute, a title, no script is
    injected and nothing is evaluated. Every field is ``None`` when the page
    did not render it, and a missing employer is the signal the caller uses to
    tell an unrendered page from a real posting: LinkedIn sets the document
    title server-side, so the title arrives even on a shell that carries no
    posting at all, and a reader that trusted it alone would report a job that
    was never on the page.
    """
    out: dict[str, Any] = {
        "company": None,
        "company_url": None,
        "document_title": None,
    }

    try:
        out["document_title"] = str(await page.title() or "").strip() or None
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("document title unreadable: %s: %s", type(exc).__name__, exc)

    try:
        block = page.locator(COMPANY_BLOCK).first
        label = await block.get_attribute("aria-label")
    except Exception as exc:
        logger.debug("company block unreadable: %s: %s", type(exc).__name__, exc)
        return out

    match = _COMPANY_LABEL.match(str(label or ""))
    if match:
        out["company"] = match.group(1).strip() or None

    try:
        href = await block.locator('a[href*="/company/"]').first.get_attribute("href")
    except Exception as exc:
        logger.debug("company url unreadable: %s: %s", type(exc).__name__, exc)
        return out

    slug = _COMPANY_SLUG.search(str(href or ""))
    if slug:
        out["company_url"] = f"https://www.linkedin.com/company/{slug.group(1)}/"
    return out


# ---------------------------------------------------------------------------
# Save state
# ---------------------------------------------------------------------------

#: The accessible names the job-SAVE control has been SEEN wearing. One of
#: them, and the singular is the point -- see ``shape.SAVE_LABELS`` for why
#: the ON state cannot be photographed on this account.
#:
#: MEASURED across all four frozen postings at BOTH hydration states:
#:
#:   not saved -> ``<button type="button" ... aria-label="Save the job">``
#:
#: Anchored on the accessible name, and the alternatives are ruled out by
#: measurement rather than by preference. ``data-view-name="job-save-button"``
#: is on the 2026-08-22 hydrated capture and GONE from the 2026-08-23 one --
#: same surface, same account, one day, the whole instrumenting layer removed.
#: The class list is a build hash and is byte-identical to the follow button's
#: neighbours. ``componentkey`` is a per-posting uuid. The accessible name is
#: the only handle that survived the day it was tested on.
SAVE_LABELS_SEEN: tuple[str, ...] = ("Save the job",)

#: Matches the save control in any state this reader recognises -- which today
#: is one state, so a posting that IS saved matches nothing here and
#: ``read_save_control`` reports count 0. That reading is deliberately
#: ambiguous rather than falsely negative: see ``shape.save_state``.
SAVE_CONTROL = ", ".join(
    f'button[aria-label="{label}"]' for label in SAVE_LABELS_SEEN
)


def save_control_selector(label: str) -> str:
    """A selector for the save control wearing exactly ``label``.

    GUARDED, because this is the one string in this package that a click is
    built from. The label may only be one this reader has actually seen
    LinkedIn render, so the selector cannot be assembled out of a value that
    arrived from somewhere else -- the same discipline ``writes.assert_write_url``
    applies to a url, applied to the other half of the click.
    """
    if label not in SAVE_LABELS_SEEN:
        raise ExtractionFailedError(
            f"refusing to build a save-control selector for {label!r}: this "
            f"reader has only ever seen {list(SAVE_LABELS_SEEN)}. A selector "
            "assembled from an unmeasured label is a guess pointed at a "
            "button."
        )
    return f'button[aria-label="{label}"]'


async def read_save_control(page: Any) -> dict[str, Any]:
    """Return the save control's accessible name, and how sure we are.

    Same three outcomes as :func:`read_follow_control`, and the same reason for
    keeping them three: ``count`` 0 means the control did not render IN A STATE
    THIS READER KNOWS, which on a posting that is already saved is exactly what
    would happen. Absence is not a state.
    """
    out: dict[str, Any] = {"label": None, "count": 0}
    try:
        controls = page.locator(SAVE_CONTROL)
        out["count"] = int(await controls.count())
    except Exception as exc:
        logger.debug("save control unreadable: %s: %s", type(exc).__name__, exc)
        return out
    if out["count"] != 1:
        return out
    try:
        label = await controls.first.get_attribute("aria-label")
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("save label unreadable: %s: %s", type(exc).__name__, exc)
        return out
    out["label"] = str(label or "").strip() or None
    return out


async def read_any_save_control_label(page: Any) -> Optional[str]:
    """The accessible name of whatever save-shaped control the page now draws.

    UNANCHORED ON PURPOSE, and used for exactly one thing: after a supervised
    save, reading back what the control changed INTO. :data:`SAVE_CONTROL`
    cannot do that job -- it only matches labels already known, so it would
    report the very absence the click was supposed to cause.

    It is a MEASUREMENT INSTRUMENT, never a decision input. Nothing branches on
    what this returns; ``writes.perform`` prints it so the ON-state label can be
    written into ``shape.SAVE_LABELS`` by a human who saw it. Locating "the
    save control" without knowing its name means locating it by POSITION, which
    is precisely what this package refuses to decide on -- so the value comes
    back for a person to read and for nothing else.
    """
    try:
        controls = page.locator("main button[aria-label]")
        total = int(await controls.count())
    except Exception as exc:
        logger.debug("post-click sweep failed: %s: %s", type(exc).__name__, exc)
        return None
    for index in range(min(total, 60)):
        try:
            label = await controls.nth(index).get_attribute("aria-label")
        except Exception:  # pragma: no cover - defensive
            continue
        text = str(label or "").strip()
        if text and "sav" in text.casefold():
            return text
    return None


# ---------------------------------------------------------------------------
# Apply route
# ---------------------------------------------------------------------------

#: The accessible names the APPLY control has been SEEN wearing, MEASURED
#: 2026-08-24 across thirteen job captures. Two, and they are two ROUTES rather
#: than two states of one thing -- see ``shape.APPLY_LABELS``.
#:
#: BOTH ARE ANCHORS, NOT BUTTONS. Every apply control in every capture is an
#: ``<a href=...>``; there are zero apply ``<button>`` elements anywhere. So
#: activating one is a NAVIGATION, and the destination is readable BEFORE
#: anything is activated. That is the single most useful property this surface
#: has: the route can be identified, and the third-party site named, without
#: touching the control at all.
APPLY_LABELS_SEEN: tuple[str, ...] = (
    "LinkedIn Apply to this job",
    "Apply on company website",
)

#: Matches the apply control in either route this reader recognises. An
#: already-applied posting is NOT known to match -- that state has never been
#: observed, because the applied list on this account is empty -- so count 0
#: here is genuinely ambiguous and ``shape.apply_route`` says so.
#:
#: THE LINKEDIN-HOSTED ARM IS A PREFIX MATCH, and it had to become one: the
#: exact-equality version of this selector carried the SAME defect that was
#: found in ``shape.APPLY_LABELS`` on 2026-08-24, one layer down. LinkedIn
#: serves that control as "LinkedIn Apply to this job" while the page is
#: hydrating and as "LinkedIn Apply to <TITLE> at <COMPANY>" once it settles,
#: so an ``[aria-label="..."]`` selector finds ZERO controls on a fully
#: rendered posting -- and count 0 reads as "no apply control here", which is
#: indistinguishable from a posting that genuinely has none.
#:
#: Fixing the classifier without fixing the selector would have left the bug
#: exactly where it was: the classifier would simply never have been handed
#: anything to classify. ``^=`` is CSS prefix matching, and it is deliberately
#: NOT used for the off-site arm, whose label has never been observed varying.
APPLY_CONTROL = ", ".join(
    (
        f'a[aria-label^="{shape.LINKEDIN_APPLY_PREFIX}"]'
        if label.startswith(shape.LINKEDIN_APPLY_PREFIX)
        else f'a[aria-label="{label}"]'
    )
    for label in APPLY_LABELS_SEEN
)


#: The LINKEDIN-ROUTE apply control alone, and deliberately NOT
#: :data:`APPLY_CONTROL`, which matches both routes because it exists to FIND
#: whichever control a posting draws. This one exists to be CLICKED, and the
#: whole off-site refusal rests on never driving the other one -- so the
#: selector that a click is built from must be incapable of matching it,
#: rather than merely unlikely to.
#:
#: A prefix, for the same reason ``APPLY_CONTROL`` uses one: LinkedIn writes
#: the posting's own title and employer into this label, so there is no exact
#: string to match. See ``shape.LINKEDIN_APPLY_PREFIX``.
LINKEDIN_APPLY_CONTROL = f'a[aria-label^="{shape.LINKEDIN_APPLY_PREFIX}"]'


async def read_apply_control(page: Any) -> dict[str, Any]:
    """Return the apply control's name, destination and target attribute.

    Reads THREE fields rather than one, because ``shape.apply_route`` refuses
    to classify on any single one of them: the accessible name has already been
    changed once by LinkedIn on this control, and the outbound href is a
    generic wrapper that also carries links which have nothing to do with
    applying. Same three-outcome discipline as :func:`read_follow_control`;
    count 0 and count above 1 are both reported rather than resolved.
    """
    out: dict[str, Any] = {
        "label": None,
        "href": None,
        "link_target": None,
        "count": 0,
    }
    try:
        controls = page.locator(APPLY_CONTROL)
        out["count"] = int(await controls.count())
    except Exception as exc:
        logger.debug("apply control unreadable: %s: %s", type(exc).__name__, exc)
        return out
    if out["count"] != 1:
        return out
    control = controls.first
    for field, attribute in (
        ("label", "aria-label"),
        ("href", "href"),
        ("link_target", "target"),
    ):
        try:
            value = await control.get_attribute(attribute)
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("apply %s unreadable: %s", attribute, exc)
            continue
        out[field] = str(value or "").strip() or None
    return out


# ---------------------------------------------------------------------------
# Follow state
# ---------------------------------------------------------------------------

#: The two accessible names the company-follow control on a JOB POSTING wears,
#: MEASURED on 2026-08-23 against his live account rather than guessed:
#:
#:   not following -> ``<button ... aria-label="Follow">``
#:   following     -> ``<button ... aria-label="Following">``
#:
#: Both bare -- no company name, unlike every other follow control LinkedIn
#: draws (``Follow EXL`` on a profile rail, ``Click to stop following X`` on
#: Manage Pages, ``Following, click to unfollow X`` in Interests). Four
#: conventions for one concept, which is why the ON state had to be captured
#: on THIS control rather than inferred from a sibling.
#:
#: THE CLASS ATTRIBUTE IS NOT A SIGNAL ON THIS SURFACE AND THIS IS MEASURED,
#: not assumed: on ``/jobs/view/`` the two buttons carry BYTE-IDENTICAL class
#: lists and ``aria-pressed`` appears nowhere on the page, so the accessible
#: name is the whole of the difference and that is the entire case for
#: anchoring on it.
#:
#: THE SURFACE QUALIFIER IS LOAD-BEARING AND IT WAS MISSING UNTIL 2026-08-24,
#: when a census found a capture IN THIS REPO refuting the universal form of
#: the sentence. ``/jobs/search/`` renders a different, older control --
#: ``class="follow is-following ..." aria-pressed="true"`` -- so on THAT
#: surface the class and ``aria-pressed`` do both carry the state. The reader
#: below is unaffected, because it is only ever pointed at a posting page and
#: measured count 1 on both. The correction is recorded rather than quietly
#: applied: a comment claiming something universal that one of this repo's own
#: files disproves is the same defect class as a gate printing an unmeasured
#: reversibility claim, one layer down.
FOLLOW_CONTROL = 'button[aria-label="Follow"], button[aria-label="Following"]'


async def read_follow_control(page: Any) -> dict[str, Any]:
    """Return the company-follow control's accessible name, and how sure we are.

    Three outcomes, and keeping them three rather than two is the point:

    * ``label`` set, ``count`` 1 -- the state is known.
    * ``count`` 0 -- the control did not render. On a job posting that means
      the page has not hydrated yet, NOT that he is not following: measured
      2026-08-23, the same posting showed no follow control at all before it
      settled and ``Following`` after. A reader that treated absence as "not
      following" would hand a confirm gate the wrong direction, silently.
    * ``count`` above 1 -- ambiguous. More than one follow control means the
      page is drawing something besides the posting's own employer, and
      picking the first would be picking by position.
    """
    out: dict[str, Any] = {"label": None, "count": 0}
    try:
        controls = page.locator(FOLLOW_CONTROL)
        out["count"] = int(await controls.count())
    except Exception as exc:
        logger.debug("follow control unreadable: %s: %s", type(exc).__name__, exc)
        return out
    if out["count"] != 1:
        return out
    try:
        label = await controls.first.get_attribute("aria-label")
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("follow label unreadable: %s: %s", type(exc).__name__, exc)
        return out
    out["label"] = str(label or "").strip() or None
    return out


#: One row of LinkedIn's "Manage Pages" list. Anchored on the accessible name
#: of its button, which states the inverse action outright -- ``Click to stop
#: following Ashgrove Systems``.
FOLLOWED_PAGE_BUTTON = 'button[aria-label^="Click to stop following "]'

#: The scope a followed-Page row's OWN company link lives in, as pure XPath
#: rather than an injected script.
#:
#: WHY NO ``page.evaluate`` HERE, when the three harvesters above all use one.
#: Every injected script in this package has to be declared in
#: ``test_readonly.py``'s ``INJECTED_SCRIPTS`` and put through the JS mutation
#: scanner, and ``test_readonly.py`` is under a standing zero-line-diff
#: constraint. A locator chain needs no declaration because it injects nothing,
#: so the read-only boundary is not asked to grow a new entry to accommodate a
#: read. That is the cheaper side of the trade and it was taken deliberately.
#:
#: WHY "NEAREST" AND NOT "LARGEST", WHICH IS WHAT THIS USED TO SAY. The rule
#: was THE ROW RULE stated literally -- the LARGEST ancestor containing
#: exactly ONE of these buttons, which on the reverse ``ancestor::`` axis is
#: ``[last()]``. That rule is UNBOUNDED ABOVE whenever a single row has
#: rendered, because then the whole document contains exactly one button and
#: the document is an ancestor. Measured 2026-08-23 in headless Chromium, on
#: one genuine row inside ``main`` plus one unrelated ``/company/`` link in
#: the nav: the hop resolved to ``html``, the link search under it then took
#: the first company link in DOCUMENT order, and the harvest returned a
#: single record wearing one company's NAME beside another company's ID --
#: ``{'name': 'Really Followed Co', 'id': 'unrelated-nav-corp'}``. Downstream
#: that is a confident ``following`` for a Page he does not follow AND a
#: confident ``not_following`` for the one he does. Neither came back
#: ``unknown``, which is the one wrong answer this reader is allowed.
#:
#: THE REPLACEMENT, and why it cannot degenerate the same way. The button
#: count only GROWS as you climb, so the ancestors containing exactly one of
#: them are a contiguous run starting at the button; ``[last()]`` took the top
#: of that run and the top is the document. This takes the LOWEST member of
#: the run that carries a company link at all, so the search stops at the
#: first enclosing scope that can answer and can never widen past it. Three
#: conditions, each closing one way of being wrong:
#:
#: * ``[1]`` on the reverse axis -- NEAREST, so no climb out of the row.
#: * a scope must not BE a document landmark, so a row whose own link has not
#:   drawn yields no id rather than the page's first unrelated one.
#: * exactly one button, so a scope straddling two rows yields no id rather
#:   than the neighbouring row's.
#:
#: Nothing here counts children, indexes a list or names a class, so the
#: property the original was written for survives intact: a restyled or
#: reordered row still reads, and a build-hash class change cannot break it.
#: The row predicate itself, WITHOUT the ``xpath=`` prefix, so it can be spliced
#: into a longer expression. Defined once and consumed twice -- by the reader
#: below and by :func:`unfollow_control_selector` -- because the READ and the
#: WRITE agreeing about what a row is cannot be left to two copies of a string.
#:
#: THIS SHARING IS A REPAIR, NOT A TIDY-UP. The write path shipped its own copy
#: on 2026-08-24 with a comment claiming it was "reused verbatim", and it was
#: not: it had dropped the ``[.//a[contains(@href,'/company/')]]`` condition.
#: Measured consequence on the real capture -- ALL TWENTY rows resolved to a
#: bare wrapping ``<div>`` holding zero company links, so the selector matched
#: NOTHING and every unfollow would have refused. Caught by a slice that
#: instrumented the scope resolution instead of trusting the comment. A comment
#: asserting that two strings are the same is worth exactly nothing; being the
#: same string is worth what the comment claimed.
_ROW_SCOPE = (
    "ancestor::*["
    "not(self::html or self::body or self::main or self::nav"
    " or self::header or self::footer or @role='main' or @role='navigation'"
    " or @role='banner' or @role='contentinfo')"
    "][.//a[contains(@href,'/company/')]]"
    "[count(.//button[starts-with(@aria-label,'Click to stop following ')])=1]"
    "[1]"
)

_FOLLOWED_PAGE_ID_SCOPE = "xpath=" + _ROW_SCOPE

#: The Page link inside that scope. Kept separate so a row that has none still
#: yields its NAME, which is the field the follow question is actually asked
#: in; the id is corroboration, not the answer. Which is also why NO ID is a
#: perfectly good outcome here and a NEIGHBOUR'S id is not: one loses the
#: corroboration, the other corroborates the wrong thing.
_FOLLOWED_PAGE_LINK = 'a[href*="/company/"]'


async def harvest_followed_pages(page: Any) -> list[dict[str, Any]]:
    """Every followed-Page row LinkedIn has rendered, in document order.

    Plain Playwright locators throughout: an attribute read per row and a
    BOUNDED XPath hop to the scope holding that row's own Page link. No script
    is injected and nothing is evaluated.

    The name comes off the button's own accessible name, so it is anchored to
    the row by construction and cannot be another row's. The id is the field
    that has to be hopped for, and the hop is the part that used to be able to
    leave the row -- see ``_FOLLOWED_PAGE_ID_SCOPE``.
    """
    try:
        buttons = page.locator(FOLLOWED_PAGE_BUTTON)
        count = int(await buttons.count())
    except Exception as exc:
        logger.debug("followed pages unreadable: %s: %s", type(exc).__name__, exc)
        return []

    rows: list[dict[str, Any]] = []
    for index in range(count):
        button = buttons.nth(index)
        try:
            label = await button.get_attribute("aria-label")
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("row %d label unreadable: %s", index, exc)
            continue
        href = None
        try:
            link = button.locator(_FOLLOWED_PAGE_ID_SCOPE).locator(
                _FOLLOWED_PAGE_LINK
            )
            if await link.count():
                href = await link.first.get_attribute("href")
        except Exception as exc:
            # A row with no readable link is still a row. Losing the id costs
            # corroboration; dropping the row would lose the follow itself.
            logger.debug("row %d link unreadable: %s", index, exc)
        rows.append({"label": str(label or ""), "href": href})
    return rows


def unfollow_control_selector(company_id: str) -> str:
    """A selector for the unfollow button of ONE company, keyed by its id.

    GUARDED, like :func:`save_control_selector`, and for the same reason: this
    is a string a click is built from. ``company_id`` must be digits, so
    nothing a caller supplies can escape the quoting or widen the predicate.

    WHY THE ID AND NOT THE NAME, even though the name is right there in the
    accessible name this anchors on. The label states the inverse action --
    ``Click to stop following <Page>`` -- which is what makes it the strongest
    anchor in this package. It is also the WEAKEST KEY: display names collide,
    change, and are chosen by somebody else. So the button is found by its
    label and the ROW is found by its company id, and both must agree.

    WHY THE ROW MUST CARRY A ``/company/`` LINK AT ALL, which is the part that
    is a safety property rather than a nicety. A census on 2026-08-24 measured
    LinkedIn rendering the IDENTICAL label template -- ``Click to stop
    following <name>`` -- over PEOPLE on ``/feed/following/``: twenty rows,
    ``urn:li:member:`` urns, and no company link anywhere in them. A selector
    anchored on the label alone matched all twenty. This server cannot reach
    that surface (it is not on the read allowlist), so nothing was ever at
    risk; the requirement is here because the day the selector meets a page
    nobody predicted is the day the requirement has to already be in it.
    Requiring the company link discriminates 80 company rows from 20 member
    rows with no exceptions in either direction.
    """
    identifier = str(company_id or "").strip()
    if not identifier.isdigit() or len(identifier) < 4:
        raise ExtractionFailedError(
            f"refusing to build an unfollow selector for {company_id!r}: a "
            "followed Page is addressed by its numeric LinkedIn company id. A "
            "selector assembled from anything else is a guess pointed at "
            "whichever row happens to match."
        )
    return (
        "xpath=//button[starts-with(@aria-label,'Click to stop following ')]["
        + _ROW_SCOPE
        + f"/descendant::a[contains(@href,'/company/{identifier}/')]]"
    )


async def read_unfollow_control(page: Any, company_id: str) -> dict[str, Any]:
    """The unfollow button belonging to ONE company row, and how sure we are.

    Same three outcomes as every other control reader here, and the middle one
    is not theoretical on this surface: LinkedIn renders twenty rows of a
    larger list, so count 0 means "that company's row is not on the page",
    which is emphatically NOT "he does not follow them". The caller reconciles
    that against LinkedIn's own stated total -- see
    ``shape.followed_page_state`` -- and this reader does not pretend to.
    """
    out: dict[str, Any] = {"label": None, "count": 0}
    selector = unfollow_control_selector(company_id)
    try:
        controls = page.locator(selector)
        out["count"] = int(await controls.count())
    except Exception as exc:
        logger.debug("unfollow control unreadable: %s: %s", type(exc).__name__, exc)
        return out
    if out["count"] != 1:
        return out
    try:
        label = await controls.first.get_attribute("aria-label")
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("unfollow label unreadable: %s: %s", type(exc).__name__, exc)
        return out
    out["label"] = str(label or "").strip() or None
    return out


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

#: Where LinkedIn parks text meant only for a screen reader, across surfaces.
#: A job card's verification decoration lives in the first of these; the header
#: toggles use the second. The selector is passed to ``querySelectorAll`` in a
#: try/catch, so an entry a browser cannot parse costs nothing.
#:
#: These strings are CSS classes, which this package otherwise refuses to lean
#: on because LinkedIn generates them. These are the exception and the reason
#: is that they are not layout classes: they are the page DECLARING which of
#: its own text is a duplicate, and there is no other way to be told. Losing
#: them costs the decoration removal and nothing else -- the parse falls back
#: to reading lines in order.
CARD_HIDDEN_SELECTOR = ".visually-hidden, .a11y-text, .sr-only, .screen-reader-text"

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


# ---------------------------------------------------------------------------
# The apply modal
# ---------------------------------------------------------------------------

#: LinkedIn's own test hook on the control that SUBMITS an application.
#: Measured 2026-08-24 on a live posting: exactly one occurrence, on
#: ``<button aria-label="Submit application" ... type="button">``.
#:
#: PREFERRED OVER THE ACCESSIBLE NAME, which is the opposite of the choice
#: made for every other control in this package, so the reason matters: an
#: apply cannot be withdrawn by this server, and the accessible name is the
#: field LinkedIn has already been measured changing WITHIN a single page load
#: (see ``shape.LINKEDIN_APPLY_PREFIX``). A hook LinkedIn maintains for its own
#: tests is the more stable of the two, and the name is checked as well rather
#: than instead -- both must agree before anything is pressed.
#:
#: Note it still says ``easy-apply``, the retired product name, while the
#: aria-label says "LinkedIn Apply". A parser keyed on the visible product name
#: and one keyed on this hook disagree about what this surface is called.
APPLY_SUBMIT_HOOK = "data-live-test-easy-apply-submit-button"
APPLY_SUBMIT_SELECTOR = f"button[{APPLY_SUBMIT_HOOK}]"

#: The modal root. Measured: exactly 1 ``role="dialog"`` on the rendered flow,
#: and 0 ``aria-modal`` -- so this is the only usable root and aria-modal must
#: NOT be required.
APPLY_MODAL_SELECTOR = "[role=dialog]"

#: Words that mean "this control advances the flow rather than ending it".
#: Their PRESENCE is what makes a posting unsafe to drive: the one flow
#: measured had zero of them and a single Submit, and a posting that renders a
#: Next is a shape nobody here has ever seen finish.
APPLY_ADVANCE_WORDS = ("next", "continue", "review")

#: How many buttons inside the dialog the advance scan will walk. A TRIPWIRE,
#: NOT A BUDGET, and the difference is the whole point of this constant: when
#: a modal draws more than this, the scan does NOT run and does NOT truncate --
#: it reports itself INCOMPLETE and the gate refuses. Silently walking the
#: first N and reporting "no advance controls" is how a multi-step flow reads
#: as single-screen, which is precisely the failure this number used to cause
#: at 40 against a modal recorded with 43 buttons.
#:
#: 200 because an apply dialog carrying more controls than that is not a shape
#: this reader has ever seen, and the right response to an unrecognised shape
#: here is to stop rather than to sample it.
APPLY_ADVANCE_SCAN_LIMIT = 200


async def read_apply_modal(page: Any) -> dict[str, Any]:
    """Read the apply modal WITHOUT touching it.

    Returns what the caller needs to decide whether this flow is the one that
    was measured, and refuses to summarise: every field is reported so a
    surprise shows up as a surprise rather than as a False.

    THE ADVANCE COUNT IS THE SAFETY FIELD. One posting was measured, and it was
    a single screen carrying one enabled Submit and no Next. Another posting
    may well be a multi-step flow. Rather than assume it is not, this reports
    the advance controls it can see, and the caller refuses when there are any
    -- so a shape nobody has measured stops the action instead of being driven
    on a guess.
    """
    out: dict[str, Any] = {
        "modal_present": False,
        "submit_present": False,
        "submit_enabled": False,
        "submit_name": None,
        "advance_names": [],
        # DEFAULTS THAT REFUSE. Every early return below leaves these as they
        # are, and an unscanned modal must never read as one with no advance
        # controls -- so "complete" starts false and is earned, not assumed.
        "buttons_total": 0,
        "advance_scan_complete": False,
        "why": "",
    }
    try:
        out["modal_present"] = int(await page.locator(APPLY_MODAL_SELECTOR).count()) > 0
    except Exception:
        out["modal_present"] = False

    try:
        submit = page.locator(APPLY_SUBMIT_SELECTOR)
        count = int(await submit.count())
    except Exception as exc:
        out["why"] = f"the submit control could not be read ({type(exc).__name__})"
        return out

    if count != 1:
        out["why"] = (
            f"expected exactly one {APPLY_SUBMIT_HOOK} control and found "
            f"{count}. One is the measured shape; anything else is a flow "
            "this reader has never seen."
        )
        return out

    out["submit_present"] = True
    for key, coro in (
        ("submit_name", submit.get_attribute("aria-label")),
        ("_disabled", submit.get_attribute("disabled")),
        ("_aria_disabled", submit.get_attribute("aria-disabled")),
    ):
        try:
            out[key] = await coro
        except Exception:
            out[key] = None
    try:
        visible = bool(await submit.is_visible())
    except Exception:
        visible = False
    out["submit_enabled"] = (
        visible
        and out.pop("_disabled", None) is None
        and out.pop("_aria_disabled", None) != "true"
    )
    out.pop("_disabled", None)
    out.pop("_aria_disabled", None)

    # Advance controls anywhere in the modal.
    #
    # AN EMPTY LIST AND AN UNFINISHED SCAN ARE NOT THE SAME VALUE, and until
    # 2026-08-26 they were. This loop walked ``min(total, 40)`` and reported
    # whatever it found; a Next past the fortieth button came back as
    # ``advance_names: []``, which the gate reads as a single-screen flow and
    # proceeds to submit on. The one modal ever observed was recorded at 43
    # buttons. The margin was three.
    #
    # THREE WAYS THIS SCAN CAN COME UP SHORT, and all three now say so instead
    # of returning a tidy empty list:
    #   * more controls than the tripwire  -- not scanned at all, see below;
    #   * one control that would not read  -- a button this reader could not
    #     read is a button it cannot RULE OUT;
    #   * the locator itself raising       -- previously ``pass``, which
    #     turned a failed scan into "no advance controls found".
    names: list[str] = []
    total = 0
    complete = False
    try:
        buttons = page.locator(f"{APPLY_MODAL_SELECTOR} button")
        total = int(await buttons.count())
        if total > APPLY_ADVANCE_SCAN_LIMIT:
            # DELIBERATELY NOT SCANNED. The gate refuses an incomplete scan, so
            # walking hundreds of controls would spend the round trips to reach
            # the answer it already has. Reporting the count is what matters.
            complete = False
        else:
            complete = True
            for i in range(total):
                node = buttons.nth(i)
                try:
                    if not await node.is_visible():
                        continue
                    label = (await node.get_attribute("aria-label")) or ""
                    text = (await node.inner_text()) or ""
                except Exception:
                    complete = False
                    continue
                name = " ".join(f"{label} {text}".split()).lower()
                if not name:
                    continue
                if any(w in name for w in APPLY_ADVANCE_WORDS):
                    names.append(name[:60])
    except Exception:
        complete = False
    out["advance_names"] = sorted(set(names))
    out["buttons_total"] = total
    out["advance_scan_complete"] = complete
    return out


# ---------------------------------------------------------------------------
# Messaging filters
# ---------------------------------------------------------------------------

#: The ONLY controls this server may activate on the messaging surface, by
#: accessible name. A closed set, matched exactly, refusing everything else --
#: the same shape as ``config.PERMITTED_LAUNCH_FLAGS`` allowing exactly two
#: Chromium flags and refusing a third.
#:
#: WHY A CLICK IS PERMITTED HERE AT ALL, since this is a READ path.
#:
#: The measurement first: all six pills are ``<button>`` with no href, so the
#: filter surface is not reachable by navigation. Reading their destinations
#: rather than guessing a ``?filter=`` parameter is what established that.
#:
#: Then the argument, which the operator made and which is right. A filter
#: pill SENDS NOTHING and CHANGES NOTHING on LinkedIn's servers -- it alters
#: which rows are displayed. Counted by EFFECT rather than by verb, which is
#: how this family classifies everything else, a view filter is a read.
#:
#: And the part that settles it: ``linkedin_open_messaging`` ALREADY opens
#: somebody's conversation and may fire a read receipt, and ships with that
#: stated as an accepted cost. Refusing the lesser act while performing the
#: greater one is backwards. The previous refusal was a convention wearing the
#: costume of a limit -- the server's own verdict said InMails were
#: unreachable "without interacting with the page, which it does not do", and
#: that clause was a decision, not a wall.
MESSAGING_FILTERS: tuple[str, ...] = (
    "focused",
    "other",
    "unread",
    "jobs",
    "connections",
    "inmail",
    "starred",
)


def filter_name_matches(accessible_name: str, wanted: str) -> bool:
    """THE ONE RULE BOTH PATHS USE. Substring, case-insensitive.

    THIS EXISTS BECAUSE THE TWO PATHS DISAGREED ON HIS LIVE PAGE, inside a
    single response: the enumerator reported an ``inmail`` pill and the
    activator reported "expected exactly one and found 0". Same page, same
    call, opposite answers.

    The cause was not a broken matcher. It was TWO MATCHERS ASKING DIFFERENT
    QUESTIONS. The enumerator asked "does the accessible name CONTAIN inmail";
    the activator rebuilt a selector demanding the name be EXACTLY "InMail",
    from a guess about how LinkedIn capitalises it. Any real label -- "InMail
    messages", "InMail 1 new", "Filter by InMail" -- satisfies the first and
    fails the second.

    The activator was the wrong one. It reconstructed a selector from an
    assumption instead of using what the page actually carries, which is the
    same mistake as guessing an apply url rather than reading the anchor.

    So there is now ONE predicate and both call it. A disagreement of this
    shape is not possible while that holds, and a test asserts it.
    """
    return str(wanted or "").strip().lower() in str(accessible_name or "").lower()


def assert_permitted_filter(name: str) -> str:
    """The closed-set check, unchanged, and still done BEFORE anything else.

    The narrowing was never the bug. The permission granted is to activate one
    of seven named pills, not to press things on a page, and that is enforced
    here before any locator exists.
    """
    wanted = str(name or "").strip().lower()
    if wanted not in MESSAGING_FILTERS:
        raise ValueError(
            f"{name!r} is not a messaging filter this server may activate. "
            f"The permitted set is {list(MESSAGING_FILTERS)} and it is closed: "
            "a control outside it is refused rather than clicked, because the "
            "permission granted here is to filter a view, not to press things "
            "on a page."
        )
    return wanted


async def activate_messaging_filter(page: Any, name: str) -> dict[str, Any]:
    """Activate one filter pill. THE ONLY CLICK ON ANY READ PATH.

    Located by ACCESSIBLE NAME with substring matching -- the same rule the
    enumerator uses -- rather than by a selector rebuilt from a guess about
    LinkedIn's exact capitalisation. See :func:`filter_name_matches`.

    Returns what happened, including the url before and after, because the
    caller has to be able to tell a FILTER from a NAVIGATION. If activating a
    pill turns out to move the page, that is a finding rather than a detail:
    it would mean the control does more than filter, and the read
    classification that permits this click would no longer hold.
    """
    wanted = assert_permitted_filter(name)
    before = page.url
    try:
        pills = page.get_by_role("button", name=wanted, exact=False)
        count = int(await pills.count())
    except Exception as exc:  # noqa: BLE001 - reported, never fatal
        return {"activated": False, "why": f"pill unreadable ({type(exc).__name__})"}
    if count != 1:
        return {
            "activated": False,
            "found": count,
            "why": (
                f"expected exactly one {name!r} pill and found {count}. One is "
                "the measured shape; anything else is a page this reader has "
                "not seen, and it is not clicked on speculation."
            ),
        }

    # THE ACCESSIBLE NAME, which is what the locator matched on. Reading
    # aria-label alone reported empty for every successful activation on his
    # live page -- his pills carry visible TEXT and no aria-label -- and an
    # empty label beside activated:true reads like a contradiction when it is
    # only a field looking in the wrong place.
    label = ""
    try:
        label = str(await pills.first.get_attribute("aria-label") or "").strip()
        if not label:
            label = str(await pills.first.inner_text() or "").strip()
    except Exception:  # pragma: no cover - a report, not a gate
        label = ""

    await pills.first.click(timeout=FILTER_CLICK_TIMEOUT_MS)
    try:
        await page.wait_for_timeout(FILTER_SETTLE_MS)
    except Exception:  # pragma: no cover - a settle, not a gate
        pass
    return {
        "activated": True,
        "filter": wanted,
        "pill_label": label,
        "url_before": before,
        "url_after": page.url,
        "navigated": page.url != before,
    }


#: How long to wait for a pill to be actionable, and for the list to redraw
#: after it. Short: this is a client-side filter, not a page load.
FILTER_CLICK_TIMEOUT_MS = 10_000
FILTER_SETTLE_MS = 2_000


# ---------------------------------------------------------------------------
# The surface census (measurement instrument, not a job-search reader)
# ---------------------------------------------------------------------------

#: Enumerate the CONTROLS on a rendered page, with no interpretation.
#:
#: THE FOURTH SCRIPT, and it is the only one here that is not in service of a
#: job-search feature. It exists so that the capabilities this server has never
#: measured -- and therefore refuses -- can be costed by READING what a page
#: actually carries, rather than by guessing a selector and finding out at the
#: moment it fires. ``tests/test_readonly.py`` scans it like the other three.
#:
#: It reads and returns. There is no click, no focus, no attribute write, no
#: request, and no scroll: the tokens that would do any of those are refused by
#: :data:`readonly.JS_MUTATION_TOKENS`, and this script is scanned against that
#: list by name.
#:
#: WHAT IT RETURNS IS RAW AND IS NOT SAFE TO PUBLISH. Accessible names on a
#: feed contain other members' names, so every name and every href leaving this
#: script goes through ``shape.census_shape`` in the wrapper below, BEFORE it
#: reaches any caller. This script is the only place raw names exist and its
#: only caller shapes them.
#:
#: THE NAME IS RESOLVED IN THE ORDER A SCREEN READER WOULD, which is the whole
#: reason to read the accessible name rather than the text: LinkedIn labels its
#: reaction buttons with ``aria-label`` and leaves their text as an icon, so a
#: text-only census reports a page of nameless buttons.
CENSUS_JS = """
(cfg) => {
  const textOf = (node) => (node && node.innerText ? node.innerText.trim() : '');
  const attrOf = (el, name) => {
    if (!el || !el.getAttribute) return '';
    const found = el.getAttribute(name);
    return found === null ? '' : String(found).slice(0, cfg.maxChars);
  };
  const countOf = (selector) => {
    try { return document.querySelectorAll(selector).length; } catch (e) { return 0; }
  };
  const labelledBy = (el) => {
    const ids = attrOf(el, 'aria-labelledby');
    if (!ids) return '';
    const parts = [];
    for (const id of ids.split(/\\s+/)) {
      if (!id) continue;
      let target = null;
      try { target = document.getElementById(id); } catch (e) { target = null; }
      if (target) parts.push(textOf(target));
    }
    return parts.join(' ').trim();
  };
  const nameOf = (el) => {
    const aria = attrOf(el, 'aria-label');
    if (aria) return { name: aria, source: 'aria-label' };
    const referenced = labelledBy(el);
    if (referenced) return { name: referenced, source: 'aria-labelledby' };
    const title = attrOf(el, 'title');
    if (title) return { name: title, source: 'title' };
    const body = textOf(el);
    if (body) return { name: body, source: 'text' };
    return { name: '', source: 'none' };
  };

  const controls = [];
  let nodes;
  try { nodes = document.querySelectorAll(cfg.controlSelector); } catch (e) { nodes = []; }
  for (const el of nodes) {
    const named = nameOf(el);
    const href = attrOf(el, 'href');
    const expanded = attrOf(el, 'aria-expanded');
    const ariaDisabled = attrOf(el, 'aria-disabled');
    controls.push({
      tag: (el.tagName || '').toLowerCase(),
      role: attrOf(el, 'role') || null,
      name: named.name,
      name_source: named.source,
      has_href: !!href,
      href: href,
      aria_expanded: expanded ? expanded : null,
      disabled: el.disabled === true || ariaDisabled === 'true'
    });
    if (controls.length >= cfg.maxControls) break;
  }

  return {
    url: document.location.href,
    title: document.title || '',
    truncated: controls.length >= cfg.maxControls,
    counts: {
      forms: countOf('form'),
      buttons: countOf('button, [role="button"]'),
      links: countOf('a[href]'),
      contenteditable: countOf('[contenteditable]:not([contenteditable="false"])'),
      file_inputs: countOf('input[type="file"]'),
      dialogs: countOf('[role="dialog"], dialog')
    },
    controls: controls
  };
}
"""

#: What counts as a control worth censusing. Roles as well as tags, because
#: LinkedIn builds plenty of its buttons out of divs.
CENSUS_CONTROL_SELECTOR = (
    'button, a[href], input, textarea, select, '
    '[role="button"], [role="link"], [role="textbox"], [role="combobox"], '
    '[contenteditable]:not([contenteditable="false"])'
)

#: Ceiling on controls returned from one page. A feed carries hundreds and the
#: census is a distribution, not a list, so the tail costs nothing to lose --
#: but it is REPORTED as truncated rather than silently cut.
CENSUS_MAX_CONTROLS = 400


async def read_surface_census(
    page: Any,
    *,
    max_controls: int = CENSUS_MAX_CONTROLS,
    max_chars: int = 300,
) -> dict[str, Any]:
    """Return the control census of the rendered page, ALREADY SHAPED.

    The shaping is done here, in the only caller of :data:`CENSUS_JS`, so that
    a raw accessible name has nowhere to go: this function returns records
    whose ``shape`` and ``href_shape`` have been through
    ``shape.census_shape``, and the raw strings are discarded inside it.

    That placement is the privacy property. Shaping in the tool instead would
    leave a function on this module returning other members' names to anyone
    who called it later, which is precisely the shape of defect that gets
    found a release after it is introduced.
    """
    cfg = {
        "controlSelector": CENSUS_CONTROL_SELECTOR,
        "maxControls": int(max_controls),
        "maxChars": int(max_chars),
    }
    try:
        data = await page.evaluate(CENSUS_JS, cfg)  # readonly-ok
    except Exception as exc:
        raise ExtractionFailedError(
            f"could not read the page: {type(exc).__name__}: {exc}",
            url=_url_of(page),
        ) from exc

    data = dict(data or {})
    shaped: list[dict[str, Any]] = []
    for control in list(data.get("controls") or []):
        href_shape = shape.census_shape(control.get("href")) or None
        # A control that POINTS AT a member or a company is a link to a named
        # entity, so its accessible name is that entity's name whatever the
        # string looks like. Refused here, at the earliest point the two
        # fields exist together, rather than left for the aggregation pass --
        # the aggregation pass still checks it, and neither is redundant: this
        # one keeps a raw name out of THIS function's return value, which is
        # what lets its docstring claim what it claims.
        name_shape = shape.census_shape(control.get("name"))
        if shape.census_href_identifies_entity(href_shape):
            name_shape = shape.CENSUS_REDACTED
        shaped.append(
            {
                "shape": name_shape,
                "tag": str(control.get("tag") or ""),
                "role": control.get("role"),
                "name_source": control.get("name_source"),
                "has_href": bool(control.get("has_href")),
                "href_shape": href_shape,
                "aria_expanded": control.get("aria_expanded"),
                "disabled": bool(control.get("disabled")),
            }
        )

    counts = {
        key: int((data.get("counts") or {}).get(key) or 0)
        for key in (
            "forms",
            "buttons",
            "links",
            "contenteditable",
            "file_inputs",
            "dialogs",
        )
    }
    return {
        "counts": counts,
        "controls": shaped,
        "controls_read": len(shaped),
        "truncated": bool(data.get("truncated")),
    }
