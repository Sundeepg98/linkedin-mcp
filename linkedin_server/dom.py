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
import time
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

#: The accessible names the job-SAVE control has been SEEN wearing. TWO of
#: them since 2026-08-30, and the pairing is the point -- see
#: ``shape.SAVE_LABELS`` for what each one MEANS and for the four observations
#: the second one rests on.
#:
#: MEASURED. The OFF label across all four frozen postings at BOTH hydration
#: states; the ON label on the live posting the operator saved, read three
#: times through ``linkedin_job_detail`` after the write path reported it once:
#:
#:   not saved -> ``<button type="button" ... aria-label="Save the job">``
#:   saved     -> ``<button type="button" ... aria-label="Unsave the job">``
#:
#: NO FIXTURE CARRIES THE ON LABEL. Every capture in ``tests/fixtures`` was
#: taken while the account had nothing saved, so every offline test that needs
#: a saved posting DERIVES one by relabelling the control. That is stated here
#: because it is the one asymmetry left between the two rows: the OFF label is
#: reproducible from disk, the ON label is reproducible only from the live
#: account. A capture of a saved posting would close it.
#:
#: Anchored on the accessible name, and the alternatives are ruled out by
#: measurement rather than by preference. ``data-view-name="job-save-button"``
#: is on the 2026-08-22 hydrated capture and GONE from the 2026-08-23 one --
#: same surface, same account, one day, the whole instrumenting layer removed.
#: The class list is a build hash and is byte-identical to the follow button's
#: neighbours. ``componentkey`` is a per-posting uuid. The accessible name is
#: the only handle that survived the day it was tested on.
SAVE_LABELS_SEEN: tuple[str, ...] = ("Save the job", "Unsave the job")

#: Matches the save control in any state this reader recognises -- which since
#: 2026-08-30 is BOTH states, so a saved posting now matches and reports its
#: label instead of reporting count 0. Count 0 has correspondingly narrowed in
#: meaning: it no longer covers "the state nobody has photographed", only "the
#: page has not drawn its controls" or "LinkedIn renamed one". Still ambiguous,
#: still refuses, one fewer reading to hold open: see ``shape.save_state``.
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
    THIS READER KNOWS. Absence is not a state.

    WHAT CHANGED ON 2026-08-30. Until the ON label was measured, an
    already-saved posting was the commonest way to reach count 0 -- the
    selector held one name and a saved posting wore the other. It now matches
    both, so a saved posting reports ``"Unsave the job"`` and count 0 means
    what it says: nothing this reader recognises is on the page.
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


#: How many labelled controls the unanchored save sweep will walk before it
#: stops walking. The same number and the same reasoning as
#: :data:`APPLY_ADVANCE_SCAN_LIMIT`: a posting drawing more labelled controls
#: than this is not a shape this reader has seen, and REPORTING the count is
#: worth more than sampling past it.
#:
#: IT REPLACES A SILENT 60. ``read_any_save_control_label`` walked
#: ``min(total, 60)`` and told nobody when it stopped early -- the exact defect
#: this section now exists to fix, sitting inside the one instrument that was
#: supposed to fix it.
SAVE_SCAN_LIMIT = 200

#: What an accessible name must contain before this reader will REPORT it.
#:
#: A WHOLE WORD, AND THE WORD BOUNDARY IS LOAD-BEARING. The substring test this
#: replaces -- ``"sav" in text.casefold()`` -- also matches the member names
#: Savita and Savannah, and a job posting draws a hiring team and a "people
#: also viewed" rail, so the substring rule was a member-name filter that let
#: member names through. ``\b(?:un)?saved?\b`` matches save, saved, unsave and
#: unsaved and matches neither of those names.
_SAVE_WORD = re.compile(r"\b(?:un)?saved?\b", re.IGNORECASE)

#: Both element kinds the save control could be wearing. Every capture this
#: repo holds draws a ``<button>``; the APPLY control sitting beside it is an
#: ``<a>`` in every capture, so a save control that had become an anchor is a
#: shape worth being able to SEE rather than one worth being blind to.
SAVE_SWEEP_SELECTOR = "main button[aria-label], main a[aria-label]"

#: Every ``<button>`` under ``<main>``, labelled or not. THE ONE COUNT THAT
#: SEPARATES "NOT READY" FROM "RENAMED", and it earns that job by measurement
#: rather than by argument.
#:
#: Measured 2026-08-30 across every job capture in this repo:
#:
#:   job_detail_shell               0 buttons   (the un-hydrated shell)
#:   job_detail_following           2
#:   job_detail                     8
#:   job_detail_hydrated            8
#:   job_detail_following_hydrated 12
#:
#: Zero on the shell, never fewer than two on a posting that actually drew.
#: WHY NOT THE APPLY CONTROL, which was the obvious candidate and was tried
#: first: the apply control is an ``<a>`` in every capture, and an anchor
#: survives in a document whose BUTTON layer has not attached -- a derived page
#: with every ``<button>`` stripped still reports one apply control and a
#: believable title and employer. Apply therefore cannot tell the two states
#: apart, and a readiness signal that cannot fail is not one.
MAIN_BUTTONS = "main button"

#: What the captures actually draw, carried as data so the refusal can quote
#: them instead of a reader having to go and look. Measured 2026-08-30 over
#: every job capture in this repo, counting ``<button>`` under ``<main>``.
#:
#: THE SECOND NUMBER IS THE INTERESTING ONE. ``job_detail_following`` draws
#: only two buttons and is plainly a PARTIAL render beside its own hydrated
#: sibling (167 nodes under the primary-content section against 715) -- and it
#: still carries exactly one save control, as do all four rendered captures.
#: So a low button count does not by itself mean the save control is absent,
#: and that is precisely why the readiness verdict must report the count
#: rather than merely pass or fail on it.
SAVE_CAPTURE_BUTTONS_FULL = "8-12"
SAVE_CAPTURE_BUTTONS_MIN = 2

#: The labelled half of :data:`MAIN_BUTTONS`. Reported beside the sweep total
#: so that "labelled controls" can be split into buttons and anchors -- the
#: anchors are what remain when the button layer has not attached.
SAVE_LABELLED_BUTTONS = "main button[aria-label]"

#: How long :func:`wait_for_save_control` will wait for the control to attach.
#:
#: ON TOP OF ``config.SETTLE_MS`` (3500ms), which every navigation already
#: spends -- and which is a FLAT TIMER, not a condition: ``browser.goto`` tries
#: ``networkidle`` first and LinkedIn's long-poll connections mean it "rarely
#: settles", so in practice every read falls through to the flat wait. That
#: timer is the bet this constant exists to stop making. A save is a supervised
#: write behind a token that expires in two minutes, so ten seconds of WAITING
#: FOR A NAMED THING is affordable where another blind 3500ms is not.
SAVE_READY_TIMEOUT_MS = 10_000


async def _sweep_save_shaped(page: Any) -> dict[str, Any]:
    """Every save-WORDED control on the page, plus the scan's own receipts.

    Returns RAW accessible names, in document order, and nothing here is fit to
    publish: :func:`read_save_candidates` is the one that reduces them. The two
    callers want different things from the same walk -- one wants the raw
    string to write into a table, the other wants a shaped string to print in a
    refusal -- so the walk is shared and the OUTPUT is not.
    """
    out: dict[str, Any] = {
        # DEFAULTS THAT REFUSE, the same discipline ``read_apply_modal`` runs
        # on: a page that was never scanned and a page carrying no save
        # control must not reach a reader as the same pair of values.
        "names": [],
        "buttons_total": 0,
        "labelled_buttons": 0,
        # UNREPORTED, NOT ZERO. Zero is a measurement that says the button
        # layer never attached, and it is the whole discriminator -- so it may
        # only ever be set by a count that actually ran. None is what an
        # unread page says, and the note prints the two differently.
        "main_buttons_total": None,
        "scan_complete": False,
    }
    try:
        controls = page.locator(SAVE_SWEEP_SELECTOR)
        total = int(await controls.count())
    except Exception as exc:
        logger.debug("save sweep failed: %s: %s", type(exc).__name__, exc)
        return out

    # The two counts that separate an unattached page from a renamed control.
    # Read BEFORE the walk, and each in its own try, because a sweep that comes
    # back empty is exactly when they matter most -- these must not be lost to
    # the same failure that emptied it.
    try:
        out["labelled_buttons"] = int(await page.locator(SAVE_LABELLED_BUTTONS).count())
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("labelled-button count failed: %s", type(exc).__name__)
    try:
        out["main_buttons_total"] = int(await page.locator(MAIN_BUTTONS).count())
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("main-button count failed: %s", type(exc).__name__)

    out["buttons_total"] = total
    if total > SAVE_SCAN_LIMIT:
        # DELIBERATELY NOT SCANNED, and reported as not scanned. The count is
        # the answer at this point; walking past the limit would spend the
        # round trips to reach one that is already known to be incomplete.
        return out

    names: list[str] = []
    complete = True
    for index in range(total):
        try:
            label = await controls.nth(index).get_attribute("aria-label")
        except Exception:  # pragma: no cover - defensive
            # A control that would not read is a control that cannot be RULED
            # OUT, so this makes the scan incomplete rather than merely
            # shorter. ``continue`` alone was what turned a failed read into
            # "nothing found here".
            complete = False
            continue
        text = str(label or "").strip()
        if text and _SAVE_WORD.search(text):
            names.append(text)
    out["names"] = names
    out["scan_complete"] = complete
    return out


async def read_any_save_control_label(page: Any) -> Optional[str]:
    """The accessible name of whatever save-shaped control the page now draws.

    UNANCHORED ON PURPOSE, and used for exactly one thing: after a supervised
    write, reading back what the control changed INTO. :data:`SAVE_CONTROL`
    cannot be trusted with that job even now that it knows both labels -- the
    whole point of the read-back is to catch a name NOBODY has written down,
    and an anchored selector can only ever confirm the names it already holds.

    IT DID ITS JOB ONCE AND IS STILL HERE. This is what reported
    ``"Unsave the job"`` on the operator's first save, 2026-08-30, which is the
    row ``shape.SAVE_LABELS`` gained that evening. It is kept, not retired,
    because the next rename lands the same way: the anchored reader goes to
    count 0 and says nothing, and this is what says what the page drew.

    It is a MEASUREMENT INSTRUMENT, never a decision input. Nothing branches on
    what this returns; ``writes.perform`` prints it so a new label can be
    written into ``shape.SAVE_LABELS`` by a human who saw it. Locating "the
    save control" without knowing its name means locating it by POSITION, which
    is precisely what this package refuses to decide on -- so the value comes
    back for a person to read and for nothing else.

    RAW, AND THAT IS THE POINT OF IT: the string here is the one a human copies
    into ``shape.SAVE_LABELS``, so reducing it would hand them ``<opaque>`` to
    write down. What protects the value instead is :data:`_SAVE_WORD` -- and
    tightening that from a substring to a whole word closed a leak on THIS
    path, not only on the diagnostic one, because a hiring-team control named
    "Savita ..." satisfied the old rule and would have been printed as the
    label the save control changed into.
    """
    names = (await _sweep_save_shaped(page))["names"]
    return names[0] if names else None


async def read_save_candidates(page: Any) -> dict[str, Any]:
    """What the page ACTUALLY draws, for a refusal that found no known control.

    THE POINT OF THIS FUNCTION IS THAT A REFUSAL SHOULD TEACH SOMETHING, and
    the reason it has to be a SECOND reading is worth stating exactly.
    :func:`read_save_control` asks the page ONE question -- is there a
    ``button[aria-label="Save the job"]`` -- and a page that answers no leaves
    it holding ``{"label": None, "count": 0}``. There is nothing to salvage
    from that reading, because nothing was ever read: the other controls on the
    posting were walked past by a CSS selector, not measured and then
    discarded. So the diagnostic cannot be a matter of printing what the first
    read already had. It has to go and look again, wider.

    A MEASUREMENT INSTRUMENT, NEVER A DECISION INPUT, exactly as
    :func:`read_any_save_control_label` is. Nothing branches on what comes
    back and no selector is built from it: :func:`save_control_selector` still
    refuses every label outside :data:`SAVE_LABELS_SEEN`, so a name cannot
    become a click by having been reported here.

    WHAT IS WITHHELD, AND WHY IT IS WITHHELD RATHER THAN TRUSTED. A job posting
    renders a hiring team and a "people also viewed" rail, so its accessible
    names include real members'. TWO gates run, in this order:

    1. the name must carry a save WORD (:data:`_SAVE_WORD`) -- the filter, and
       a word rather than a substring because "Savita" contains "sav";
    2. whatever survives is reduced by ``shape.census_shape``, the same
       function the whole privacy property of ``linkedin_surface_census`` rests
       on, which returns ``<opaque>`` for anything over 60 characters or
       outside a narrow ASCII class.

    ``shape.census_redact_rare`` is deliberately NOT applied, and that is a
    decision rather than an omission: it blanks a run of two capitalised words
    in any shape seen ONCE, and the save control is drawn once. A genuine ON
    label reading "Saved Job" would come back ``<redacted>`` -- the instrument
    would destroy the exact measurement it was called to take.
    """
    swept = await _sweep_save_shaped(page)
    names = swept["names"]
    return {
        "candidates": sorted({shape.census_shape(name) for name in names}),
        # KEPT SEPARATE FROM len(candidates) BECAUSE THE SET LOSES A CASE.
        # Two controls both labelled "Saved" dedupe to one shape, and "two
        # save controls rendered" is the fact that decides whether the reader
        # is looking at a rename or at a page it cannot scope.
        "matched_total": len(names),
        "buttons_total": swept["buttons_total"],
        "labelled_buttons": swept["labelled_buttons"],
        # Derived rather than counted, because the two selectors are disjoint
        # by construction: a node is a button or an anchor, never both.
        "labelled_links": swept["buttons_total"] - swept["labelled_buttons"],
        "main_buttons_total": swept["main_buttons_total"],
        "scan_complete": swept["scan_complete"],
    }


async def wait_for_save_control(page: Any, timeout_ms: int) -> dict[str, Any]:
    """Wait for the save control to ATTACH. Reports what happened, not a verdict.

    Returns ``{"ready", "waited_ms", "timeout_ms", "failure"}`` and refuses to
    summarise, the same contract :func:`read_apply_modal` keeps: a caller that
    gets a bare ``False`` cannot tell a page that was asked and said no from a
    page that could not be asked at all, and those are different findings. The
    numbers are the ones that ACTUALLY happened rather than the constant that
    was meant to apply, so a refusal cannot quote a duration it did not spend.

    A POSITIVE CONDITION AND NOT A SLEEP, and the difference is the point of
    the function. ``browser.goto`` already spends ``config.SETTLE_MS`` on every
    navigation, but it spends it as a FLAT TIMER -- ``networkidle`` is tried
    first and LinkedIn's long-poll connections mean it rarely settles, so the
    read lands wherever 3500ms happens to put it. That is a bet on a duration.
    This waits for a NAMED ELEMENT and returns the moment it exists, so a page
    that is ready in 200ms costs 200ms and a page that never becomes ready
    costs the ceiling and SAYS SO.

    ONE BOUNDED WAIT, ONE VERDICT. There is no retry loop here, deliberately:
    re-reading until the answer changes is how a racy reader is made to look
    reliable while staying racy, and it would also make the timeout meaningless.

    ``attached`` rather than ``visible``: the question is whether the control
    layer has rendered this control at all. Whether it is scrolled into view is
    a different question, and ``page.click`` waits on actionability itself.

    Never raises. ``ready`` is False on timeout AND on any locator failure,
    because the caller refuses on False and an exception that came back True
    would be a failure that opened the gate. ``failure`` is what separates the
    two for a human reading the refusal.
    """
    out: dict[str, Any] = {
        # THE DEFAULT REFUSES. Nothing below sets ready True except the wait
        # actually returning.
        "ready": False,
        "waited_ms": 0,
        "timeout_ms": int(timeout_ms),
        "failure": None,
    }
    started = time.monotonic()
    try:
        await page.locator(SAVE_CONTROL).first.wait_for(
            state="attached", timeout=timeout_ms
        )
        out["ready"] = True
    except Exception as exc:
        out["failure"] = type(exc).__name__
        logger.debug(
            "save control did not attach in %dms: %s: %s",
            timeout_ms,
            type(exc).__name__,
            exc,
        )
    out["waited_ms"] = int((time.monotonic() - started) * 1000)
    return out


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


def follow_control_selector(label: str) -> str:
    """A selector for the follow control wearing exactly ``label``.

    The twin of :func:`save_control_selector`, and guarded for the same
    reason: this is a string a CLICK is built from, so the label may only be
    one ``shape.FOLLOW_LABELS`` has actually seen LinkedIn render. Added
    2026-08-30, when ``follow_company`` moved into ``writes.PERFORMABLE`` --
    before that there was no follow click and therefore no follow selector,
    and the gap was invisible precisely because nothing called it.

    NOTE WHAT THIS DELIBERATELY DOES NOT DO. It never returns the two-state
    :data:`FOLLOW_CONTROL` union. That constant exists to READ a state and
    matches the control in either one; a click built from it would press
    whichever of the two happened to be on the page, which on a toggle is how
    an action performs its opposite.
    """
    from linkedin_server import shape as _shape

    if label not in _shape.FOLLOW_LABELS:
        raise ExtractionFailedError(
            f"refusing to build a follow-control selector for {label!r}: this "
            f"reader has only ever seen {sorted(_shape.FOLLOW_LABELS)}. A "
            "selector assembled from an unmeasured label is a guess pointed "
            "at a button."
        )
    return f'button[aria-label="{label}"]'


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


# ---------------------------------------------------------------------------
# Job description readiness
# ---------------------------------------------------------------------------

#: The description section, as LinkedIn's SDUI layer marks it FILLED.
#: MEASURED 2026-08-30 over the five job captures in tests/fixtures, and
#: re-counted independently before this shipped:
#:
#:   capture                         this anchor   id="JobDetails_AboutTheJob_<id>"
#:   job_detail_shell                     0                  0
#:   job_detail_following                 0                  1   <-- description ABSENT
#:   job_detail                           1                  1
#:   job_detail_hydrated                  1                  1
#:   job_detail_following_hydrated        1                  1
#:
#: THE OBVIOUS ANCHOR IS THE WRONG ONE, AND WRONG IN THE DANGEROUS DIRECTION.
#: ``id="JobDetails_AboutTheJob_<id>"`` is the SLOT and is drawn before its
#: content; it is PRESENT on ``job_detail_following``, the capture whose
#: description is missing, so a wait anchored on it reports READY in precisely
#: the state this wait exists to detect. The ``data-sdui-component`` attribute
#: marks the slot FILLED. Measured, not preferred -- and the difference is a
#: whole column of the table above.
JOB_DESCRIPTION_SLOT = (
    'main [data-sdui-component='
    '"com.linkedin.sdui.generated.jobseeker.dsl.impl.aboutTheJob"]'
)

#: The ceiling this wait may spend. Generous, and it costs nothing on a page
#: that has drawn -- the sibling wait, ``wait_for_save_control``, was measured
#: at 27 ms on a ready page, because an attached element satisfies the wait at
#: once. What the bound buys is that a page which never draws costs this much
#: ONCE and then SAYS SO, instead of producing a confident refusal about
#: LinkedIn from a read taken before LinkedIn had answered.
JOB_DESCRIPTION_TIMEOUT_MS = 10_000


async def wait_for_job_description(page: Any) -> dict[str, Any]:
    """Wait for the description to ATTACH. Three outcomes, and none is a verdict.

    WHY THIS EXISTS, and it is a defect in this package rather than in
    LinkedIn. ``browser.goto`` settles a navigation with ``networkidle`` and
    falls back to a flat timer, and those two branches are SEVEN SECONDS APART
    -- roughly 1 s if networkidle resolves, roughly 7 s if it does not.
    Measured across 37 recorded ``/jobs/view/<id>`` loads, the fast branch ran
    28 times; across 15 reads whose outcome was recorded the split was total,
    13 of 13 early reads refusing for a missing description and 2 of 2
    late reads drawing the posting in full. The page was fine. The read was
    early.

    A DURATION IS THE WRONG FIX AND IS NOT TAKEN HERE. Raising the settle, or
    flooring it, would tax every surface for one surface's missing readiness
    check -- and nothing measured through the shipped build can distinguish
    "2 s would be enough" from "6 s would be enough", because the settle is
    binary by construction and every candidate number sits inside an unmeasured
    bracket. This waits for the NAMED ELEMENT and returns the moment it exists,
    so a drawn page costs almost nothing and an undrawn one costs the ceiling
    and reports that it did.

    ONE BOUNDED WAIT, ONE VERDICT, NO RETRY LOOP -- the same contract as
    :func:`wait_for_save_control`. Re-reading until the answer changes is how a
    racy reader is made to LOOK reliable while staying racy, and it would make
    the timeout mean nothing.

    THREE-VALUED, AND THE THIRD VALUE IS NOT DECORATION:

    ======================  ==================================================
    ``attached`` is True    the anchor attached. The description is drawn.
    ``attached`` is False   the wait ran its full course and found nothing.
                            THIS IS A FINDING about the page.
    ``attached`` is None    the readiness check ITSELF failed -- a locator
                            error, a closed page. Evidence for NEITHER.
    ======================  ==================================================

    Collapsing None into False would report a broken instrument as a finding
    about LinkedIn, which is the same class of error as a gate printing an
    unmeasured reversibility claim. It is also not hypothetical: that exact
    mutation came back green on first pass in the save wave.

    ``attached`` rather than ``visible``: the question is whether the content
    layer has rendered this section at all, not whether it is scrolled into
    view.

    Never raises. The caller decides what to do with all three.
    """
    out: dict[str, Any] = {
        # THE DEFAULT IS THE INSTRUMENT-FAILED VALUE, not the finding. Nothing
        # below sets True except the wait returning, and nothing sets False
        # except a timeout specifically -- so a path nobody thought about
        # cannot arrive claiming to have measured LinkedIn.
        "attached": None,
        "waited_ms": 0,
        "timeout_ms": int(JOB_DESCRIPTION_TIMEOUT_MS),
        "failure": None,
        "why": "the readiness check did not run",
    }
    started = time.monotonic()
    try:
        await page.locator(JOB_DESCRIPTION_SLOT).first.wait_for(
            state="attached", timeout=JOB_DESCRIPTION_TIMEOUT_MS
        )
        out["attached"] = True
        out["why"] = "the description section attached"
    except Exception as exc:  # noqa: BLE001 - classified below, never re-raised
        # CLASSIFIED BY NAME, which is this package's own idiom rather than a
        # shortcut -- writes.py already tells a genuine expiry from an
        # instrument failure the same way, and it avoids importing playwright
        # into a module that has never needed it. Python's builtin TimeoutError,
        # asyncio's, and playwright's all carry the name and all mean the same
        # thing here: the wait ran its course.
        name = type(exc).__name__
        out["failure"] = name
        if name == "TimeoutError":
            # THE ONLY PATH THAT MAY REPORT A FINDING. A timeout is the page
            # answering "not here" for the whole bounded period; every other
            # exception is this function failing to ask.
            out["attached"] = False
            out["why"] = (
                "the description section did not attach within the bound, so "
                "the page had not drawn it"
            )
        else:
            out["why"] = (
                f"the readiness check itself failed ({name}), so this says "
                "nothing about the page"
            )
            logger.debug("description readiness check failed: %s: %s", name, exc)
    out["waited_ms"] = int((time.monotonic() - started) * 1000)
    return out


async def read_job_posting(page: Any) -> dict[str, Any]:
    """THE reader for a job posting. Both job-detail paths call this one.

    WHY IT EXISTS, and the history is the argument. ``linkedin_job_detail`` and
    ``writes._read_posting_facts`` each held their own copy of the same three
    calls -- ``read_job_identity``, ``read_main_text``, ``shape.parse_job_detail``
    -- in the same order with the same arguments. Two copies of one sequence is
    how "the two readers must be using different strategies" becomes a
    plausible theory about a disagreement they cannot possibly have caused.
    They cannot drift apart now because there is one of them.

    THE RENDER EVIDENCE IS THE OTHER HALF. ``read_main_text`` returns ``""``
    both when ``<main>`` is missing and when it is empty, so a caller could
    never tell "the page drew nothing" from "the page drew something this
    parser could not read". Those want completely different responses -- one is
    a page to re-read, the other is a parser to fix -- so the presence of
    ``<main>`` and the SIZE of its text are reported alongside the parse.

    Character counts, never the text: a job page carries a hiring team and a
    "people also viewed" rail, so the body is not this server's to hand around
    for diagnostics.

    THE READINESS WAIT RUNS FIRST, AND THE ORDER IS THE WHOLE OF ITS VALUE.
    Added 2026-08-30. After the text has been read, waiting for the description
    changes nothing about what was read -- it would spend up to ten seconds to
    produce a field describing a page that had already been parsed. Every read
    below it therefore happens on a page that has either drawn its description
    or spent the bound failing to, and ``description_wait`` says which.
    """
    description_wait = await wait_for_job_description(page)
    identity = await read_job_identity(page)
    main_text = await read_main_text(page)
    try:
        main_present = int(await page.locator("main").count()) > 0
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("main presence unreadable: %s", type(exc).__name__)
        # UNKNOWN, NOT ABSENT. False here would say "the page drew no main",
        # which is the strongest thing this evidence can claim.
        main_present = None
    return {
        "identity": identity,
        "detail": shape.parse_job_detail(
            main_text,
            company=identity.get("company"),
            document_title=identity.get("document_title"),
        ),
        "main_present": main_present,
        "main_chars": len(main_text),
        "description_wait": description_wait,
    }


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


# ---------------------------------------------------------------------------
# The nine surfaces
# ---------------------------------------------------------------------------
#
# READERS FOR THE CAPABILITIES THAT ARE SANCTIONED AND REFUSE. Every constant
# below is a string MEASURED on the operator's live account on 2026-08-30 by
# ``linkedin_surface_census``, and the census that produced it is named beside
# it. None was inferred from a sibling, a screenshot or a plausible
# convention -- which is the whole reason this block exists rather than the
# selectors being written inline where they are used.
#
# WHY THESE READ AND NEVER CLICK. The seven actions they serve are sanctioned
# and NOT performable; what each reader exists to do is let the confirm gate
# refuse with a FRESH measurement instead of a stored sentence. "I looked just
# now and here is what was there" is a different artefact from "somebody
# looked once in August", and the second is what goes stale silently.
#
# WHY NO ``page.evaluate`` ANYWHERE BELOW. The same trade as
# ``FOLLOWED_PAGE_ROW_SCOPE`` above: an injected script has to be declared in
# ``test_readonly.py``'s ``INJECTED_SCRIPTS`` and put through the JS mutation
# scanner, and a locator chain injects nothing. Seven readers that need no new
# entry on the read-only boundary is the cheaper side of that trade.

#: The feed composer's entry control. MEASURED on ``/feed/`` 2026-08-30 as
#: ``shape "Start a post", tag div, role button, name_source text,
#: has_href false``, count 1.
#:
#: A ``div`` with ``role=button`` and NO href, so the composer is not reachable
#: by navigation -- it opens as a MODAL. The same run measured
#: ``contenteditable: 0`` across the whole page, and that is the finding which
#: matters more than the control: THE EDITOR ITSELF HAS NEVER BEEN OBSERVED.
#: What is measured here is the door, not the room behind it.
COMPOSER_CONTROL_NAME = "Start a post"

#: The two URL-ADDRESSABLE publish routes, both MEASURED as real anchors:
#: ``Write article`` -> ``/article/new/`` on ``/feed/``, and ``Create a post``
#: -> ``/preload/sharebox/`` on ``/in/me/``. Recorded because "a post cannot be
#: reached by navigation" would be FALSE if anybody wrote it. It can. Neither
#: address is on the read allowlist and neither editor has ever been loaded,
#: which are different objections and both are stated.
ARTICLE_COMPOSER_HREF = "/article/new/"
SHAREBOX_COMPOSER_HREF = "/preload/sharebox/"

#: The comment affordance, MEASURED in both of its shapes -- and they are not
#: the same control:
#:
#:   ``/feed/``   shape "Comment", tag button, name_source text,
#:                has_href false, count 3 -- an inline composer.
#:   ``/in/me/``  shape "Comment", tag a, name_source text, href_shape
#:                ``https://www.linkedin.com/feed/update/<urn>/``, count 8 --
#:                a LINK to the item's permalink.
#:
#: The second is where the target key lives: a feed item is addressed by its
#: urn, in a url this server's read boundary forbids (``/feed/update``).
COMMENT_CONTROL_NAME = "Comment"

#: The reaction control, and the most informative string measured that day.
#: MEASURED ``aria-label="Reaction button state: no reaction"``: count 3 on
#: ``/feed/`` and count 8 on ``/in/me/``. Eleven controls, every one of them in
#: the OFF state.
#:
#: LINKEDIN WRITES THE TOGGLE STATE INTO THE ACCESSIBLE NAME. That is the same
#: convention as the follow control and the unfollow row, and it means the
#: OFF-to-ON direction has a measured anchor. THE ON-STATE LABEL HAS NEVER
#: BEEN SEEN, because nothing on either surface had been reacted to -- exactly
#: the position ``unsave_job`` WAS in, and it gets the same answer: the missing
#: half is not guessed.
#:
#: AND THE SAVE PAIR IS NOW THE WORKED EXAMPLE OF HOW IT GETS UNSTUCK, which
#: is worth more here than the analogy was. Its ON label was measured on
#: 2026-08-30 by a supervised write, and then RE-measured three times through a
#: read-only route built so the measurement never had to be bought twice. The
#: same shape applies here: one supervised reaction produces the ON label, and
#: a reader that reports the reaction control's name off a page already open
#: makes it re-measurable for nothing. Neither exists yet.
REACTION_STATE_PREFIX = "Reaction button state:"
REACTION_OFF_LABEL = "Reaction button state: no reaction"
REACTION_CONTROL = 'button[aria-label^="Reaction button state:"]'

#: The reaction PICKER, measured beside the toggle: ``aria-label="Open
#: reactions menu"``, ``aria-expanded="false"``, count 3 and 8. Its contents
#: have never been observed, so WHICH reactions exist is unknown.
REACTIONS_MENU_LABEL = "Open reactions menu"

#: The invitation control, and the finding that gives the invitation
#: capability a route costing no badge. MEASURED on ``/in/me/`` 2026-08-30:
#: 9 controls shaped ``"<redacted> to connect"``, tag button, name_source
#: aria-label.
#:
#: THE PREFIX IS REDACTED AND THAT IS NOT A HOLE IN THE MEASUREMENT, it is the
#: measurement working. LinkedIn writes the other person's NAME into this
#: label and the census blanks a name before counting it. So the suffix is the
#: whole of what may be known about this control without collecting a third
#: party's identity, and a suffix is what a selector may be built from.
INVITE_CONTROL_SUFFIX = " to connect"
INVITE_CONTROL = 'button[aria-label$=" to connect"]'

#: The profile editors, MEASURED as ordinary anchors on ``/in/me/``
#: 2026-08-30 -- each a single ``<a href>`` with an aria-label, count 1.
#:
#: THIS IS THE MEASUREMENT THAT REFUTES A SENTENCE THIS SERVER WAS SHIPPING.
#: The live page carries 2 forms where every tracked profile fixture carries
#: 0, and it carries these three anchors where the fixtures carry none. A
#: profile editor IS url-addressed. See ``server._WHY_NOT_PERFORMED``, where
#: the claim is narrowed to the one thing that survived rather than deleted.
PROFILE_EDITOR_HREFS = (
    "/edit/intro/",
    "/edit/forms/summary/new/",
    "/overlay/contact-info/",
)

#: Where a settings VALUE lives. MEASURED 2026-08-30: the settings surface
#: renders 33 links and ZERO forms, and every individual setting is its own
#: address -- ``/mypreferences/d/settings/language``,
#: ``/mypreferences/d/dark-mode``, ``/mypreferences/d/categories/privacy``. So
#: a setting IS url-addressed and its CONTROL has never been observed, because
#: no page below the index has ever been loaded.
SETTINGS_LINK_PREFIX = "/mypreferences/d/"


async def _count_by_role(page, name):
    """How many controls carry EXACTLY the accessible name ``name``.

    ``get_by_role`` rather than a CSS selector because both controls this is
    pointed at are named by their TEXT and not by an aria-label, and CSS
    cannot match text. It injects nothing, so the read-only boundary is not
    asked to grow an entry to accommodate a read.
    """
    try:
        return int(await page.get_by_role("button", name=name, exact=True).count())
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("role count unreadable: %s: %s", type(exc).__name__, exc)
        return 0


async def _count_links_with(page, fragment):
    """How many anchors carry ``fragment`` inside their href."""
    try:
        return int(await page.locator('a[href*="' + fragment + '"]').count())
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("href count unreadable: %s: %s", type(exc).__name__, exc)
        return 0


async def read_composer_surface(page: Any) -> dict[str, Any]:
    """What this page offers for publishing, and what it does not.

    ``editors`` is the field that decides the question. A LinkedIn composer is
    a ``contenteditable`` node; the census measured ZERO of them on the first
    render of both the feed and the profile, so a non-zero count here would be
    a finding and a zero is the expected reading. Either way it is taken
    afresh rather than asserted from a run in August.
    """
    out: dict[str, Any] = {
        "composer_controls": await _count_by_role(page, COMPOSER_CONTROL_NAME),
        "article_routes": await _count_links_with(page, ARTICLE_COMPOSER_HREF),
        "sharebox_routes": await _count_links_with(page, SHAREBOX_COMPOSER_HREF),
        "editors": 0,
    }
    try:
        out["editors"] = int(await page.locator("[contenteditable]").count())
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("editor count unreadable: %s: %s", type(exc).__name__, exc)
    return out


async def read_reaction_surface(page: Any) -> dict[str, Any]:
    """The reaction and comment controls on this page, and the states worn.

    ``labels`` holds the DISTINCT accessible names found, sorted, each put
    through ``shape.census_shape`` on the way out. Not decoration: if LinkedIn
    ever writes a member's name into this label -- which it already does on
    the neighbouring ``Hide post by <name>`` control -- an unshaped read would
    publish it into a confirm block. The measured label carries no name and
    survives shaping unchanged, so nothing is lost while that stays true.
    """
    out: dict[str, Any] = {
        "controls": 0,
        "off_state": 0,
        "menus": 0,
        "comment_controls": await _count_by_role(page, COMMENT_CONTROL_NAME),
        "permalinks": await _count_links_with(page, "/feed/update/"),
        "labels": [],
    }
    try:
        controls = page.locator(REACTION_CONTROL)
        out["controls"] = int(await controls.count())
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("reaction controls unreadable: %s: %s", type(exc).__name__, exc)
        return out
    try:
        out["menus"] = int(
            await page.locator(
                'button[aria-label="' + REACTIONS_MENU_LABEL + '"]'
            ).count()
        )
        out["off_state"] = int(
            await page.locator(
                'button[aria-label="' + REACTION_OFF_LABEL + '"]'
            ).count()
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("reaction menus unreadable: %s: %s", type(exc).__name__, exc)
    seen = set()
    for index in range(min(int(out["controls"]), CENSUS_MAX_CONTROLS)):
        try:
            label = await controls.nth(index).get_attribute("aria-label")
        except Exception:  # noqa: BLE001 - a measurement, not a gate
            continue
        shaped = shape.census_shape(str(label or "").strip())
        if shaped:
            seen.add(shaped)
    out["labels"] = sorted(seen)
    return out


async def read_profile_editor_surface(page: Any) -> dict[str, Any]:
    """Which profile editors this page addresses by url. COUNTS ONLY.

    No href is returned and no accessible name is read. The addresses carry
    his own member slug, the question being asked is "is there an anchor at
    all", and a count answers it without carrying a slug into a tool result.
    """
    out: dict[str, Any] = {"forms": 0, "editors": {}}
    for fragment in PROFILE_EDITOR_HREFS:
        out["editors"][fragment] = await _count_links_with(page, fragment)
    try:
        out["forms"] = int(await page.locator("form").count())
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("form count unreadable: %s: %s", type(exc).__name__, exc)
    return out


async def read_invitation_surface(page: Any) -> dict[str, Any]:
    """How many invitation controls this page draws. A COUNT AND NOTHING ELSE.

    Deliberately narrower than every other reader here, and the narrowness is
    the point. This control's accessible name IS another person's name. A
    reader that returned the label would be collecting third-party identity in
    order to populate a confirm block, which is the cost this whole family of
    rulings refuses to pay. So the label is never read -- not read and then
    shaped, not read and then dropped. The count establishes that the control
    exists on a surface costing no badge, and that is the only question asked.
    """
    out: dict[str, Any] = {"controls": 0}
    try:
        out["controls"] = int(await page.locator(INVITE_CONTROL).count())
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("invite controls unreadable: %s: %s", type(exc).__name__, exc)
    return out


async def read_messaging_badge(page: Any) -> dict[str, Any]:
    """The messaging nav badge, read WITHOUT opening messaging.

    This is the whole of what the send-a-message gate is allowed to look at,
    and the restraint is the design rather than a limitation of it. Loading
    /messaging/ is MEASURED to redirect into one specific conversation of
    LinkedIn's choosing and to reset this very badge -- so a gate that opened
    it in order to describe it would spend, on a stranger and on his own
    unread count, exactly what it is supposed to be warning him about.

    The nav link is present on every signed-in page. Its accessible name
    carries the count LinkedIn would consume: measured 2026-08-30 as
    ``Messaging, 0 new notifications`` on both the feed and the profile. The
    label is shaped on the way out for the usual reason -- it is a nav label
    today and nothing guarantees it stays one.
    """
    out: dict[str, Any] = {"links": 0, "label": None}
    try:
        links = page.locator('a[href*="/messaging/"]')
        out["links"] = int(await links.count())
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("messaging link unreadable: %s: %s", type(exc).__name__, exc)
        return out
    if out["links"] < 1:
        return out
    try:
        label = await links.first.get_attribute("aria-label")
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("messaging label unreadable: %s: %s", type(exc).__name__, exc)
        return out
    out["label"] = shape.census_shape(str(label or "").strip()) or None
    return out


async def read_settings_surface(page: Any) -> dict[str, Any]:
    """How many settings this page addresses by url, and how many it toggles.

    ``controls`` reading zero while ``links`` is large IS the measurement: the
    settings surface hands out ADDRESSES, not switches. Every value lives one
    page further down, and no page below the index has ever been loaded by
    this server.
    """
    out: dict[str, Any] = {"links": 0, "forms": 0, "controls": 0}
    out["links"] = await _count_links_with(page, SETTINGS_LINK_PREFIX)
    try:
        out["forms"] = int(await page.locator("form").count())
        out["controls"] = int(
            await page.locator(
                'input[type="checkbox"], select, [role="switch"]'
            ).count()
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("settings controls unreadable: %s: %s", type(exc).__name__, exc)
    return out


# ---------------------------------------------------------------------------
# Job tracker readiness
# ---------------------------------------------------------------------------

#: A drawn row on the job tracker, as a SELECTOR rather than as the regex the
#: harvest matches. The two are deliberately different instruments over the
#: same fact: ``JOB_HREF`` decides which harvested card is a job, this decides
#: whether any such card has ATTACHED yet, and only the second can be waited
#: on. Measured over the two tracker captures -- zero hits on
#: ``jobs_tracker_empty``, two on ``jobs_tracker_row`` (LinkedIn draws the row
#: twice, once per layout, both anchored at the same job id).
TRACKER_ROW_LINK = 'main a[href*="/jobs/view/"]'

#: The ceiling the wait below may spend, matching its two siblings. It costs
#: almost nothing on a tab that has drawn -- either half of the disjunction
#: satisfies it at once -- and a tab that never resolves costs this much ONCE
#: and then SAYS SO, rather than producing a confident claim about an empty
#: list.
TRACKER_LIST_TIMEOUT_MS = 10_000


def tracker_list_selector() -> str:
    """WHAT "THE LIST RESOLVED" MEANS, assembled from what ``shape`` owns.

    A DISJUNCTION rather than one element, because the tracker has two
    legitimate finished states and a reader that waits only for the first
    hangs for the full bound on every empty tab.

    The disjunction is EXACTLY the condition the refusal tests.
    ``_read_tracker`` raises when it has neither rows NOR a corroborated empty
    state, so this waits for whichever of those two arrives and returns the
    moment one does. Waiting for the same condition the caller is about to
    judge is the whole reason this cannot drift into waiting for something
    irrelevant.

    THE EMPTY HALF IS DERIVED FROM ``shape.TRACKER_EMPTY_MARKERS``, never
    written down a second time -- the same discipline
    ``writes.anchor_label_for`` runs on ``shape.SAVE_LABELS``. A marker added
    there is waited on here automatically, and one renamed there cannot leave a
    stale copy behind.

    WHY THIS ANCHOR CAN FAIL IN THE STATE IT DETECTS, which is the law the
    description anchor was chosen under. The tab strip is NOT part of it, and
    that is measured rather than preferred: on 2026-08-30 the live Saved tab
    reported LinkedIn's own count of 1 -- so the strip HAD drawn -- while no
    row and no empty state had. An anchor on the strip would have reported
    READY in precisely the state this wait exists to detect. The strip's own
    links are ``/jobs-tracker/?stage=...``, which ``TRACKER_ROW_LINK`` does not
    match.

    AND THE EMPTY HALF SURVIVES THE SAME TEST, which matters because a marker
    that LinkedIn always draws -- hidden until needed -- would satisfy this
    wait on an undrawn page and be the same mistake in the other half. It does
    not: the six live Saved-tab failures on 2026-08-30 each reported that no
    empty state had been drawn, read out of the same ``<main>`` text
    :func:`shape.tracker_empty_state` matches on. So the marker is absent in
    exactly the state this wait must fail in.
    """
    parts = [TRACKER_ROW_LINK]
    parts += ['main :text-is("%s")' % marker for marker in shape.TRACKER_EMPTY_MARKERS]
    return ", ".join(parts)


async def wait_for_tracker_list(page: Any) -> dict[str, Any]:
    """Wait for the tracker's LIST to resolve. Three outcomes, none a verdict.

    The third sibling of :func:`wait_for_save_control` and
    :func:`wait_for_job_description`, and it keeps their contract exactly: ONE
    bounded wait, ONE verdict, NO retry loop. Re-reading until the answer
    changes is how a racy reader is made to LOOK reliable while staying racy.

    THREE-VALUED, and the third value is not decoration:

    ======================  ==================================================
    ``attached`` is True    a job row or an empty state attached. It drew.
    ``attached`` is False   the wait ran its full course and found neither.
                            THIS IS A FINDING about the page.
    ``attached`` is None    the readiness check ITSELF failed -- a locator
                            error, a closed page. Evidence for NEITHER.
    ======================  ==================================================

    ``attached`` is the key name both siblings use for the same idea, so a
    caller holding any of the three reads out through one timing note.

    WHAT THIS DOES AND DOES NOT CLAIM TO FIX, because the difference is the
    finding of the wave that added it. It closes the read-too-early failure on
    this surface, which the posting page had and has since had fixed. It is NOT
    established as the cause of the Saved tab failing on 2026-08-30: measured
    that afternoon through this same loader, inside one ten-minute window,
    Saved failed 6 of 6 while Draft succeeded 2 of 2 and Applied 2 of 2. A
    settle race does not produce 6-0 against 4-0. That is why
    :func:`read_tracker_evidence` ships beside this and why the refusal reports
    both: the wait removes one candidate cause, the evidence names the next.

    Never raises. The caller decides what to do with all three.
    """
    out: dict[str, Any] = {
        # THE DEFAULT IS THE INSTRUMENT-FAILED VALUE, not the finding, so a
        # path nobody thought about cannot arrive claiming to have measured
        # LinkedIn.
        "attached": None,
        "waited_ms": 0,
        "timeout_ms": int(TRACKER_LIST_TIMEOUT_MS),
        "failure": None,
        "why": "the readiness check did not run",
    }
    started = time.monotonic()
    try:
        await page.locator(tracker_list_selector()).first.wait_for(
            state="attached", timeout=TRACKER_LIST_TIMEOUT_MS
        )
        out["attached"] = True
        out["why"] = "a job row or an empty state attached"
    except Exception as exc:  # noqa: BLE001 - classified below, never re-raised
        # CLASSIFIED BY NAME, the same idiom wait_for_job_description runs and
        # for the same reason: only a timeout is the page answering "not here"
        # for the whole bounded period. Every other exception is this function
        # failing to ask.
        name = type(exc).__name__
        out["failure"] = name
        if name == "TimeoutError":
            out["attached"] = False
            out["why"] = (
                "neither a job row nor an empty state attached within the "
                "bound, so the list had not resolved"
            )
        else:
            out["why"] = (
                "the readiness check itself failed (%s), so this says nothing "
                "about the page" % name
            )
            logger.debug("tracker readiness check failed: %s: %s", name, exc)
    out["waited_ms"] = int((time.monotonic() - started) * 1000)
    return out


#: Cap on the anchor walk below. The tracker draws each row twice and carries a
#: tab strip and a footer, so a healthy page is tens of links; this exists so a
#: page that has gone wrong cannot turn a diagnostic into a sweep.
TRACKER_LINK_SCAN_LIMIT = 400


async def read_tracker_evidence(page: Any) -> dict[str, Any]:
    """WHAT THE TRACKER PAGE ACTUALLY HELD, counted and never quoted.

    WHY THIS EXISTS, and it is the same lesson twice. The save refusal was
    rebuilt on 2026-08-30 because it "made a correct decision and then threw
    away the evidence for it"; the tracker refusal has the identical shape --
    it reports LinkedIn's tab count and its own zero, and nothing whatever
    about the page those two disagree over. So a reader cannot tell three
    causes apart, and they want completely different responses:

      * the list never drew            -> re-read; the readiness wait says so
      * the list drew and is empty     -> an empty state nobody matched
      * the list drew rows the harvest -> the row's link shape changed, and the
        does not match                    fix is to re-measure, not to re-read

    THE THIRD IS THE LIVE SUSPECT AND THIS REPO CANNOT CURRENTLY SEE IT. Every
    tracker capture on disk is either the DRAFT tab carrying a row or the SAVED
    tab carrying nothing; a POPULATED SAVED tab has never been captured, so the
    shape of a saved row is unmeasured. ``rows_matching`` set against
    ``anchors_total`` is what separates that case from a page that never drew:
    many anchors and zero matching rows is a rename, few anchors is a page that
    did not render.

    COUNTS, NEVER TEXT. A tracker row names a company and a job, and this
    package does not hand page bodies around for diagnostics -- the save sweep
    took the same ruling, for the same reason.
    """
    out: dict[str, Any] = {
        # UNREPORTED, NOT ZERO. Zero is a measurement; None is what an unread
        # page says, and the note prints the two differently.
        "main_present": None,
        "main_chars": None,
        "anchors_total": None,
        "rows_matching": None,
        "scan_complete": False,
    }
    try:
        out["main_present"] = int(await page.locator("main").count()) > 0
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("tracker main presence unreadable: %s", type(exc).__name__)
        return out

    out["main_chars"] = len(await read_main_text(page))

    try:
        anchors = page.locator("main a[href]")
        total = int(await anchors.count())
        out["anchors_total"] = min(total, TRACKER_LINK_SCAN_LIMIT)
        out["rows_matching"] = int(await page.locator(TRACKER_ROW_LINK).count())
        # OVER-LIMIT IS NOT A COMPLETE SCAN, said out loud rather than by a
        # silent min(). That silent cap was itself a defect in the save sweep.
        out["scan_complete"] = total <= TRACKER_LINK_SCAN_LIMIT
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("tracker anchor scan failed: %s", type(exc).__name__)
    return out
