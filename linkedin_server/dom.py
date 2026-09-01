"""Reading the rendered page.

LinkedIn's class names are generated and its GraphQL query ids rotate with
every deploy, so both make brittle anchors. What does not rotate is the shape
of a link: a person is behind ``/in/<slug>``, a job is behind
``/jobs/view/<id>``. Every list surface here is harvested by finding those
links and taking the text of the card around them.

Six small scripts are injected, and only six -- this sentence said "three" for
long enough to survive three additions, so the count is now stated as a count
somebody has to change. Each is a module-level constant so it can be read in
one place and scanned by ``tests/test_readonly.py`` against
:data:`readonly.JS_MUTATION_TOKENS` -- the scripts query the DOM and return
text, tag names, character counts or, in the newest one, nothing but integers.
The Python side of each call carries a ``# readonly-ok`` waiver, which is what
keeps a future ``evaluate`` from slipping in unreviewed.

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
  // IS THIS ELEMENT'S TEXT ACTUALLY IN innerText? That is the only question
  // the hidden budget may ask, and asking a different one was a live defect.
  //
  // shape.strip_screen_reader_copies subtracts BY COUNT: each hidden element
  // removes ONE occurrence of its own text from the card. That is correct for
  // the CLIP pattern, where the element IS rendered and innerText therefore
  // carries a second copy. It is WRONG for display:none and
  // visibility:hidden, whose text innerText never returned -- and textOf()
  // still reads them, because innerText on a NON-RENDERED element falls back
  // to textContent. So the budget charged the card for a duplicate that was
  // never there, and the subtraction paid for it out of the VISIBLE copy.
  //
  // Measured 2026-08-30: a row whose title was duplicated in a display:none
  // span lost its title entirely, parse_job_card then had nothing to read,
  // and the row was dropped. UNKNOWN COUNTS AS RENDERED -- an engine without
  // checkVisibility keeps the old behaviour rather than silently halving the
  // subtraction.
  // TWO PARTS OF THIS ARE NOT REACHED BY ANY TEST, measured 2026-08-30 rather
  // than assumed, and both are recorded instead of being quietly kept:
  //
  //   * the `return true` fallback is DEAD in this engine. Chromium 151 has
  //     checkVisibility and it does not throw, so the line never evaluates.
  //     It is kept as the answer for an engine that lacks the API, where the
  //     alternative -- defaulting to false -- would silently halve every
  //     subtraction on every surface. A fallback that is wrong in the safe
  //     direction is worth more than a line count.
  //   * `visibilityProperty` changes no SUBTRACTION. A visibility:hidden
  //     element yields no innerText, so textOf() returns '' and it is never
  //     pushed either way; the option only makes the skip COUNTER accurate.
  //     Measured: dropping it moves hidden_not_rendered 2 -> 0 and leaves the
  //     budget identical.
  const isRendered = (el) => {
    try {
      if (el && el.checkVisibility) {
        return el.checkVisibility({
          contentVisibilityAuto: true,
          visibilityProperty: true
        });
      }
    } catch (e) { /* fall through to the permissive answer */ }
    return true;
  };
  let skippedHidden = 0;
  const hiddenWithin = (node) => {
    const out = [];
    if (!node || !node.querySelectorAll || !cfg.hiddenSelector) return out;
    let marked;
    try { marked = node.querySelectorAll(cfg.hiddenSelector); } catch (e) { marked = []; }
    for (const el of marked) {
      if (!isRendered(el)) { skippedHidden += 1; continue; }
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
  let droppedEmpty = 0;
  for (const item of found) {
    const rec = record(item.href, item.row, item.anchor);
    if (rec) {
      out.push(rec);
    } else {
      // A DROP THAT NOBODY COUNTED, until 2026-08-30. record() returns null
      // for a row whose innerText is empty, and a walk that discards rows
      // without saying how many is indistinguishable from a page that had
      // none -- which is precisely the ambiguity that cost this repo a day on
      // the Saved tab. Counted here, reported by harvest_census, and NOT
      // acted on: an untitled row is still not a row.
      droppedEmpty += 1;
    }
    if (out.length >= cfg.maxItems) break;
  }
  if (cfg.census) {
    return {
      rows: out,
      anchors_keyed: found.length,
      hidden_not_rendered: skippedHidden,
      dropped_empty_text: droppedEmpty
    };
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
  // IS THIS ELEMENT'S TEXT ACTUALLY IN innerText? The hidden budget may ask
  // nothing else, and asking a different question was a live defect on the
  // sibling walk.
  //
  // PORTED FROM HARVEST_LINKED_CARDS_JS (8573b8b), which fixed it there and
  // left this script alone for a stated reason: notifications are its only
  // caller, no fixture exercised a non-rendered duplicate here, and a surface
  // that cannot be verified may not be changed on the strength of an
  // argument. That fixture now exists -- tests/test_sdui_surfaces_fixture.py
  // section 4c -- and it was RED against this script before this guard.
  //
  // shape.strip_screen_reader_copies subtracts BY COUNT: each hidden element
  // removes ONE occurrence of its own text from the card. Correct for the
  // CLIP pattern, where the element IS rendered and innerText therefore
  // carries a second copy. WRONG for display:none, whose copy innerText never
  // returned -- and textOf() reads it anyway, because innerText on a
  // NON-RENDERED element falls back to textContent. So the budget was charged
  // for a duplicate that was never in the card, and the subtraction paid for
  // it out of the VISIBLE one.
  //
  // Measured 2026-08-31, on a notification repeating its whole body in a
  // display:none span: hidden=[body], the card's single visible copy spent,
  // parse_notification left with no line at all, the row DROPPED --
  // records=1, dropped=1. UNKNOWN COUNTS AS RENDERED, so an engine without
  // checkVisibility keeps the old behaviour rather than silently halving
  // every subtraction.
  //
  // TWO THINGS THIS SCRIPT DOES NOT GET, recorded rather than quietly
  // omitted. There is no skip COUNTER: harvest_block_cards returns a bare
  // list of cards, and widening that shape to carry a census field would
  // change every caller for a diagnostic nothing has asked this surface for.
  // And visibilityProperty is consequently observable in NOTHING here -- a
  // visibility:hidden element yields no innerText, so textOf() returns '' and
  // it was never pushed either way, measured both before and after this
  // guard. It is passed regardless, so the two walks ask the DOM the same
  // question instead of drifting into two different ones.
  //
  // TWO LINES BELOW ARE NOT REACHED BY ANY TEST, mutation-checked 2026-08-31
  // rather than assumed, and recorded instead of quietly kept. Dropping
  // visibilityProperty leaves all three of section 4c's cases green, and so
  // does flipping the `return true` fallback to false: Chromium 151.0.7922.34
  // has checkVisibility and does not throw, so that line never evaluates
  // here. Both are kept anyway. The fallback is the answer for an engine that
  // LACKS the API, where returning false would silently halve every
  // subtraction on this surface -- a fallback wrong in the safe direction is
  // worth more than a line count.
  const isRendered = (el) => {
    try {
      if (el && el.checkVisibility) {
        return el.checkVisibility({
          contentVisibilityAuto: true,
          visibilityProperty: true
        });
      }
    } catch (e) { /* fall through to the permissive answer */ }
    return true;
  };
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
          if (!isRendered(el)) continue;
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


async def harvest_census(
    page: Any, *, href_pattern: str, max_items: int
) -> dict[str, Any]:
    """The same walk, reporting WHAT IT THREW AWAY as well as what it kept.

    WHY THIS EXISTS, and it is the same lesson this package has now learned on
    three surfaces. ``harvest_linked_cards`` returns a list. A list of length
    zero is returned both when the page offered no keyed anchor at all and
    when it offered several and the walk discarded every one -- and those want
    completely different repairs. On 2026-08-30 the Saved tab produced FOUR
    job-row anchors and zero rows, and nothing in this package could say which
    of the two had happened, or whether the row parser had even been reached.

    Two numbers close that:

    ``anchors_keyed``       how many DISTINCT keyed anchors the walk considered
                            (deduped by key, which is what the walk itself does)
    ``dropped_empty_text``  how many of those produced a row the walk refused
                            because its ``innerText`` was empty

    NOT A SECOND IMPLEMENTATION. It runs the identical script under a flag, so
    it cannot drift from the walk it is describing -- a separate counting
    routine would be free to disagree with the thing it counts, which is how a
    diagnostic starts lying.

    ``sibling_rows`` IS NOT AVAILABLE HERE and that is deliberate rather than
    an omission: that path returns early with its own list, so a census over it
    would report the tail's counters for the head's rows. The tracker, which is
    what this was built for, does not use it.

    A DIAGNOSTIC, NEVER A DECISION INPUT. Nothing branches on either number.
    An untitled row is still not a row, and this does not make one.
    """
    cfg = {
        "hrefPattern": href_pattern,
        "maxItems": int(max_items),
        "maxChars": 1200,
        "maxHops": 8,
        "siblingRows": False,
        "hiddenSelector": CARD_HIDDEN_SELECTOR,
        "maxHidden": 12,
        "census": True,
    }
    out: dict[str, Any] = {
        # DEFAULTS THAT REFUSE. A census that could not run must not come back
        # looking like a page that offered nothing.
        "rows": [],
        "anchors_keyed": None,
        "dropped_empty_text": None,
        "hidden_not_rendered": None,
    }
    try:
        result = await page.evaluate(HARVEST_LINKED_CARDS_JS, cfg)  # readonly-ok
    except Exception as exc:  # noqa: BLE001 - a diagnostic never raises
        logger.debug("harvest census failed: %s: %s", type(exc).__name__, exc)
        return out
    if isinstance(result, dict):
        out["rows"] = list(result.get("rows") or [])
        out["anchors_keyed"] = result.get("anchors_keyed")
        out["dropped_empty_text"] = result.get("dropped_empty_text")
        out["hidden_not_rendered"] = result.get("hidden_not_rendered")
    return out


#: How many row anchors :func:`read_tracker_row_shape` will describe, and how
#: far up from each it will climb. The climb matches ``rowOf``'s own
#: ``maxHops`` so the report describes the walk the harvest actually performs
#: rather than a deeper one nobody runs.
TRACKER_SHAPE_ROWS = 3
TRACKER_SHAPE_HOPS = 8

#: The shape reader's script. TAG NAMES AND LENGTHS ONLY -- never text, never
#: an attribute value. A tracker row names a company and a job, so the same
#: ruling the save sweep took applies here: the question is WHERE the text is,
#: and that is answerable in integers.
TRACKER_ROW_SHAPE_JS = """
(cfg) => {
  const re = new RegExp(cfg.hrefPattern);
  const out = [];
  const anchors = document.querySelectorAll(cfg.rowSelector);
  const seen = new Set();
  for (const anchor of anchors) {
    const m = (anchor.getAttribute('href') || '').match(re);
    const key = m ? (m[1] || '') : '';
    if (!key || seen.has(key)) continue;
    seen.add(key);
    const keysIn = (node) => {
      const keys = new Set();
      if (!node.querySelectorAll) return keys;
      for (const link of node.querySelectorAll('a[href]')) {
        const hit = (link.getAttribute('href') || '').match(re);
        if (hit) keys.add(hit[1] || '');
      }
      return keys;
    };
    const climb = [];
    let node = anchor;
    let hops = 0;
    while (node && hops <= cfg.maxHops) {
      // DISTINCT KEYS, not link count, and it is the same test rowOf stops on
      // (keysWithin(node).size > 1). It is what separates "still inside this
      // row" from "climbed out into the container holding the others", and
      // without it a verdict about the ROW's text ends up measuring the whole
      // page's chrome -- which is what the first draft of this did.
      climb.push({
        tag: node.tagName,
        children: node.childElementCount,
        text_chars: (node.innerText || '').trim().length,
        content_chars: (node.textContent || '').trim().length,
        keys: keysIn(node).size,
        links: node.querySelectorAll ? node.querySelectorAll('a[href]').length : 0
      });
      node = node.parentElement;
      hops += 1;
    }
    out.push(climb);
    if (out.length >= cfg.maxRows) break;
  }
  return out;
}
"""


async def read_tracker_row_shape(page: Any) -> list[list[dict[str, Any]]]:
    """WHERE a tracker row's text lives, in integers and tag names.

    THE QUESTION THIS ANSWERS. ``harvest_census`` says the walk discarded rows
    for carrying no text. It cannot say whether the text is somewhere the walk
    did not climb to, present but unrendered, or absent from the document
    altogether -- and those are three different repairs. This climbs from each
    row anchor exactly as ``rowOf`` does and reports, at every level, how many
    characters are RENDERED against how many are merely PRESENT.

    Read the two columns against each other:

    ``text_chars`` 0 and ``content_chars`` 0 at every level
        the row genuinely holds no text. LinkedIn drew the link and not its
        contents, and no reader keyed on text can find one.
    ``text_chars`` 0 with ``content_chars`` non-zero
        the text is in the DOM and not being rendered. ``innerText`` reports
        nothing for a rendered ancestor whose subtree is hidden -- note this
        is NOT true of a node that is itself unrendered, which returns its
        ``textContent`` instead, so the level at which the two diverge is
        the level that is hidden.
    both non-zero at some level above the anchor
        the text exists and the walk stopped short of it.

    TAG NAMES, COUNTS AND LENGTHS ONLY. No text and no attribute value leaves
    this function. A tracker row names a company and a job, and the save sweep
    already took this ruling for the same reason.

    Never raises; an empty list means the shape could not be read.
    """
    cfg = {
        "hrefPattern": JOB_HREF,
        "rowSelector": TRACKER_ROW_LINK,
        "maxRows": TRACKER_SHAPE_ROWS,
        "maxHops": TRACKER_SHAPE_HOPS,
    }
    try:
        result = await page.evaluate(TRACKER_ROW_SHAPE_JS, cfg)  # readonly-ok
    except Exception as exc:  # noqa: BLE001 - a diagnostic never raises
        logger.debug("tracker row shape failed: %s: %s", type(exc).__name__, exc)
        return []
    return list(result or [])


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


#: The ARIA role an ``<input>`` of a given type carries, for the two types
#: this package builds a click from. DELIBERATELY NOT THE WHOLE HTML-AAM
#: TABLE: a mapping is only here if a control of that kind has actually been
#: measured on a page this server acts on, so an input type absent from this
#: dict makes :func:`aria_role_of` return ``None`` and the caller refuse.
#:
#: WHY IT MATTERS AT ALL. ``radio`` and ``checkbox`` are two different roles
#: wearing one tag, and Playwright's accessible-name selector engine is
#: addressed BY ROLE -- so a selector built on the wrong one matches nothing.
#: Six readings of the dark-mode page established three checkable inputs and
#: NONE of them established which of the two types they are, because the
#: census's ``checked`` gate admits both. The type is therefore read off the
#: row at click time and mapped here.
INPUT_TYPE_ROLES: dict[str, str] = {
    "radio": "radio",
    "checkbox": "checkbox",
}


def aria_role_of(row: dict[str, Any]) -> Optional[str]:
    """The role a censused control carries, or ``None`` if it is not one this
    package will build a click from.

    THREE ROUTES, IN ORDER, AND THE LAST IS A REFUSAL. An explicit ``role``
    attribute wins, because it is what the author wrote and what the browser
    honours. Otherwise an ``<input>``'s type decides it, through
    :data:`INPUT_TYPE_ROLES`. Anything else -- an input type nobody has
    measured here, a tag with an implicit role this package has never needed
    -- returns ``None``, and every caller treats that as a refusal rather
    than falling back to a plausible role.

    ``None`` IS NOT "no role". Every rendered element has one; this says THIS
    READER WILL NOT NAME IT, which is the same distinction ``checked: None``
    and ``name_source: "none"`` each cost this module once before it was
    written down.
    """
    explicit = row.get("role")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip().lower()
    if str(row.get("tag") or "").lower() != "input":
        return None
    return INPUT_TYPE_ROLES.get(str(row.get("input_type") or "").lower())


#: The characters a name may not contain if it is going into a role selector.
#: A quote would end the quoted value early and a bracket would end the
#: attribute clause, so either could turn one control's name into a selector
#: matching something else entirely.
_SELECTOR_UNSAFE = ('"', "'", "[", "]", "\\", "\n", "\r", "\t", ">", "<")


def named_role_selector(role: str, name: str) -> str:
    """A selector for the ONE control with this role and this accessible name.

    Playwright's ``role=`` engine, because it is the only selector form that
    computes an ACCESSIBLE NAME -- and the dark-mode radios are named through
    ``aria-labelledby``, which no attribute selector can follow.
    ``save_control_selector`` can use ``button[aria-label="..."]`` because its
    control is named by the attribute itself; this one cannot.

    THIS SAID ``[exact=true]`` UNTIL 2026-09-02, and that is not an attribute
    Playwright's role engine has. It raises ``Unknown attribute "exact"`` on
    any page, so this builder returned a string that could not resolve and
    ``update_setting``'s only click could not land. Nothing caught it because
    every test compared the STRING and no test ever handed one to a browser --
    a selector test that never resolves the selector is a check that cannot
    fail on the one thing the selector is for.
    ``tests/test_selectors_resolve.py`` is the instrument that closes that,
    and it is what found this.

    AND THE REASON THE CLAUSE WAS THERE WAS ALSO WRONG. It read: *"a substring
    match would let ``Always on`` select a control named ``Always on,
    recommended``"*. MEASURED 2026-09-02 against this Playwright: the role
    engine matches a name WHOLE, never as a substring, with or without any
    suffix -- ``[name="Always"]`` matches nothing on a page drawing both of
    those controls. The clause was defending against something the engine does
    not do, spelled in a way that made every selector it built unusable.

    WHAT THE ``s`` SUFFIX ACTUALLY BUYS, measured on the same page: CASE
    SENSITIVITY. ``[name="always on"]`` matches 0 and ``[name="always on"i]``
    matches 1. Case-sensitive is also this version's DEFAULT, so the suffix is
    the behaviour written down rather than inherited -- which is the reason to
    keep it, and the honest size of that reason.

    SO THE SUFFIX IS DOCUMENTATION AND THE TEST IS THE GUARD. Because
    case-sensitivity is already the default, dropping ``s`` changes nothing
    observable -- a mutation doing exactly that passes the suite, and is
    recorded passing rather than hidden. What actually protects this package
    from a future Playwright flipping that default is
    ``tests/test_selectors_resolve.py`` pinning ``[name="always on"]`` to
    ZERO. That assertion is load-bearing and the suffix is not; deleting it
    on the grounds that the ``s`` covers it would leave the suffix looking
    correct while silently doing nothing, which is precisely the state
    ``[exact=true]`` was in.

    GUARDED THE SAME WAY :func:`save_control_selector` IS, and the guard has
    to be here rather than at the call site: this is a string a CLICK is built
    from. The role must be one this package maps, and the name must contain
    none of the characters that would let it escape its own quotes. Both
    refuse rather than escaping, because an escaping rule is a thing to get
    subtly wrong and a refusal is not.
    """
    if role not in set(INPUT_TYPE_ROLES.values()):
        raise ExtractionFailedError(
            f"refusing to build a selector for role {role!r}: this package "
            f"builds clicks only for {sorted(set(INPUT_TYPE_ROLES.values()))}. "
            "A selector assembled for an unmeasured role is a guess pointed "
            "at a control."
        )
    if not name or any(bad in name for bad in _SELECTOR_UNSAFE):
        raise ExtractionFailedError(
            "refusing to build a selector from this name: it is empty or "
            "carries a character that would end the selector's own quoting. "
            "The name is not escaped and made to work -- an escaping rule is "
            "a thing to get subtly wrong, and what a wrong one produces here "
            "is a click on a different control."
        )
    return f'role={role}[name="{name}"s]'


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
#:
#: THE CHAIN, AND THE DAY IT GREW. In order: ``aria-label``,
#: ``aria-labelledby``, ``title``, ``<label for=id>``, an ancestor ``<label>``,
#: then the element's own text. The two label routes were added 2026-08-31, and
#: they were added because the instrument was caught being BLIND rather than
#: because a spec says so. ``linkedin_surface_census("profile_edit_intro")``
#: was run twice against ``/in/me/edit/intro/`` and came back identical both
#: times: 67 controls, ``forms: 1``, and three ``input`` controls at
#: ``name_source: "none"`` with an empty shape -- while the same day's
#: ``settings_dark_mode`` capture resolved its three inputs through
#: ``aria-labelledby``. Every surface censused before that day was made of
#: buttons and anchors, which LinkedIn labels with ``aria-label``; the profile
#: editor is the first one made of FORM FIELDS, and a form field is named by a
#: ``<label>``. So ``name_source: "none"`` had been reading as "this control
#: carries no name" when what it meant was "this instrument cannot read one",
#: which is the conflation this package exists to refuse.
#:
#: TWO ROUTES, REPORTED SEPARATELY -- ``label-for`` and ``label-ancestor`` --
#: and not collapsed into one ``label`` source. The whole value of
#: ``name_source`` is that it says WHERE the string came from; a reader costing
#: a capability off a census can act on "this field is labelled by a sibling"
#: and cannot act on "something labelled it".
#:
#: THE GATE IS ``el.labels``, chosen over a ``document.querySelector`` on an
#: escaped id, and the reason is blast radius rather than escaping. ``.labels``
#: exists only on the elements HTML lets a ``<label>`` name -- input, button,
#: select, textarea, and the meter/output/progress family -- so an anchor or a
#: ``div[role="button"]`` that happens to sit inside a label cannot be renamed
#: by one. A querySelector would have had to be TOLD that rule; this way the
#: browser holds it, and ``CSS.escape`` never enters the script. It also
#: settles the ``<label for="other">`` case for free: HTML drops the implicit
#: association when the wrapper points elsewhere, so ``.labels`` is empty and
#: no name is invented.
#:
#: PRECEDENCE IS DELIBERATELY NARROWER THAN THE ACCESSIBLE-NAME SPEC, which
#: ranks a native label ABOVE ``title``. Here ``title`` still wins, and
#: ``aria-label`` wins over everything. The constraint is not correctness in
#: the abstract: captures taken with the three-route chain are already in the
#: audit record, and a new route that outranked an existing one would rename
#: controls inside them with nothing in the diff saying so.
#:
#: WHAT THE FALL-THROUGH ACTUALLY REACHES WAS MEASURED, not reasoned about.
#: This script and one with the label call site deleted were both run over all
#: 19 committed fixtures -- 537 controls -- and 28 controls move. 26 are
#: ``input`` controls going from ``none`` to ``label-for``, which is the blind
#: spot, and they are in the Easy Apply and job-tracker captures as well as on
#: the profile editor that found it. The other 2 are one ``select`` -- a footer
#: language picker -- going from ``text`` to ``label-for``: its ``text`` name
#: was the entire option list in a dozen scripts, which the shaper refused as
#: ``<opaque>``, and its label reads ``Select language``. NOT ONE control whose
#: published shape was a readable name changed, so no census already written
#: down is contradicted by this edit; a non-answer became an answer. The sweep
#: is pinned in ``tests/test_surface_census.py`` rather than described here.
#:
#: WHICH CONTAINER EACH CONTROL SITS IN, added 2026-08-31 as ``container``,
#: and added because the flat list had already been GUESSED AT TWICE.
#: ``linkedin_surface_census("profile_edit_intro")`` was run four times; the
#: two most recent agree exactly -- 256 controls, ``forms: 2``, ``dialogs:
#: 5`` -- and among them sit ``Save`` (button, enabled), ``Submit`` (button,
#: disabled, count 2), ``Additional name``, ``City``, ``Comments`` and
#: ``Posts``. The editor is a DIALOG inside a full profile render and the same
#: page draws an ad-report dialog and an activity rail, so nobody could say
#: whether ``Save`` was the editor's commit control or whether
#: ``Comments``/``Posts`` were profile fields or the rail's filters. Two
#: readers answered it from ADJACENCY IN THE LIST. Adjacency here is
#: ``querySelectorAll`` order, which is document order, and document order is
#: not containment.
#:
#: THE DESCRIPTOR IS A SHAPE, NEVER A NAME, and that constraint is what makes
#: it narrow rather than useful. A container is a NEW source of page text into
#: this script -- a dialog is named by an ``aria-label``, a section by its
#: heading -- and both of those can be a member; an id or a class can carry a
#: member slug. So none of them is read. What is returned is the container's
#: ROLE or TAG plus an INDEX, e.g. ``form#0``, ``dialog#3``, and ``none`` for
#: a control with no such ancestor. ``none`` is a string and the key is always
#: present, because a missing key and a null are two ways of saying "not
#: measured" and this script already paid once for that conflation.
#:
#: ONE INDEX SEQUENCE OVER THE UNION, in document order, assigned once per
#: run. Not one counter per kind: a single sequence makes the descriptor
#: unique within the document, so ``dialog#3`` and ``form#3`` cannot be two
#: names for different containers, and two controls in one container get a
#: string a reader can GROUP BY -- which is the whole capability being bought.
#:
#: NEAREST ANCESTOR, via ``closest()``, and the nesting is not hypothetical:
#: the intro editor is a FORM INSIDE A DIALOG, so nearest-versus-outermost is
#: the difference between naming the editor and naming the page furniture
#: around it. The outermost walk is derived and shown FAILING in the tests.
#: ``closest()`` starts at the element itself; a control that also matched the
#: container selector would therefore name itself, which no member of
#: ``CENSUS_CONTROL_SELECTOR`` can do without a role a real page does not
#: write, and which has never been observed -- documented rather than guarded.
#:
#: THE SELECTOR IS A LITERAL HERE, not a ``cfg`` entry like the control
#: selector, because nothing in Python reads it. It is deliberately a
#: SUPERSET of the counts block: ``counts.forms`` is ``form`` and
#: ``counts.dialogs`` is ``[role="dialog"], dialog``, and neither counts
#: ``[role="form"]``. A reader who adds those two counts and expects that many
#: descriptors will be wrong; the mismatch is pinned in the tests.
#:
#: ADDITIVE, AND MEASURED TO BE. The key is appended last and no existing
#: field is renamed, removed or reordered. This script and one with the
#: container call site deleted were run over all 19 committed fixtures -- 537
#: controls -- and NOT ONE pre-existing field moved on any control: same
#: names, same ``name_source``, same counts, same order. Captures already in
#: ``_audit/`` are therefore still true readings of this instrument.
#:
#: WHERE A NEW FIELD GOES, and this paragraph said the OPPOSITE until
#: 2026-08-31: it read "WHAT IT DOES NOT YET REACH ... this descriptor stops
#: at this script's own return value and no tool output carries it yet". That
#: was true of ``container`` for as long as it took to close and is true of
#: nothing here now -- but the MECHANISM it described is permanent, which is
#: why the paragraph is corrected rather than deleted. BOTH DOWNSTREAM SITES
#: ENUMERATE THEIR FIELDS: ``read_surface_census`` below shapes each row by
#: building a dict literal that NAMES ITS KEYS, and ``shape.census_aggregate``
#: merges rows on an explicit tuple whose field names are
#: ``shape.CENSUS_KEY_FIELDS``. A field this script emits and neither of those
#: names is dropped in SILENCE -- which is exactly what happened to
#: ``container`` on the day it was added, with the aggregate's docstring
#: calling itself "the WHOLE record" as the sentence that made the drop
#: invisible. ``checked`` and ``checked_source`` were added to both sites in
#: one edit, and ``input_type`` in another on 2026-08-31.
#:
#: THE COUNTS THAT USED TO BE IN THIS PARAGRAPH HAVE BEEN REMOVED, and the
#: removal is the lesson rather than an omission. It read "NAMES TEN KEYS ...
#: an explicit TEN-FIELD tuple" and told the reader those two numbers were the
#: thing to re-check -- which is a comment asking to be kept in step with code
#: by hand, and this module's most-repeated defect is exactly that going
#: stale. ``shape.CENSUS_KEY_FIELDS`` is now the single place the field list
#: exists, the published row is BUILT from it, and a test pins the tool's
#: promised key set against it. There is no number here to rot.
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
  const labelName = (node) => textOf(node).slice(0, cfg.maxChars);
  const labelRoutes = (el) => {
    let labels = null;
    try { labels = el.labels; } catch (e) { labels = null; }
    if (!labels || !labels.length) return null;
    const id = attrOf(el, 'id');
    if (id) {
      for (const node of labels) {
        if (attrOf(node, 'for') !== id) continue;
        const named = labelName(node);
        if (named) return { name: named, source: 'label-for' };
      }
    }
    let wrapper = null;
    try { wrapper = el.closest('label'); } catch (e) { wrapper = null; }
    if (wrapper) {
      const named = labelName(wrapper);
      if (named) return { name: named, source: 'label-ancestor' };
    }
    return null;
  };
  const nameOf = (el) => {
    const aria = attrOf(el, 'aria-label');
    if (aria) return { name: aria, source: 'aria-label' };
    const referenced = labelledBy(el);
    if (referenced) return { name: referenced, source: 'aria-labelledby' };
    const title = attrOf(el, 'title');
    if (title) return { name: title, source: 'title' };
    const labelled = labelRoutes(el);
    if (labelled) return labelled;
    const body = textOf(el);
    if (body) return { name: body, source: 'text' };
    return { name: '', source: 'none' };
  };

  const containerSelector = 'form, dialog, [role="dialog"], [role="form"]';
  let containerNodes;
  try {
    containerNodes = Array.from(document.querySelectorAll(containerSelector));
  } catch (e) { containerNodes = []; }
  const containerKind = (node) => {
    const role = attrOf(node, 'role').trim().toLowerCase();
    if (role === 'dialog' || role === 'form') return role;
    return (node.tagName || '').toLowerCase();
  };
  const containerOf = (el) => {
    let found = null;
    try { found = el.closest(containerSelector); } catch (e) { found = null; }
    if (!found) return 'none';
    const index = containerNodes.indexOf(found);
    if (index < 0) return 'none';
    return containerKind(found) + '#' + index;
  };

  // NATIVE BEFORE ARIA, and the order is deliberate rather than incidental:
  // it is the OPPOSITE of nameOf above, which tries aria-label first. On a
  // native radio or checkbox el.checked is the state the browser holds and
  // the state a click would move, and an aria-checked written beside it is
  // redundant markup that can go stale; on a div[role="radio"] there is no
  // native state and ARIA is the only truth. THE TYPE GATE is the point, not
  // a detail: HTMLInputElement.checked is defined for every input type and
  // reads false on a text box, so an ungated read would report every text
  // field as "unchecked" -- not-checkable reported as checkable-and-off.
  // null means NOT A CHECKABLE CONTROL; false means CHECKABLE AND OFF.
  const checkedOf = (el) => {
    const tag = (el.tagName || '').toLowerCase();
    if (tag === 'input') {
      const type = String(el.type || '').toLowerCase();
      if (type === 'radio' || type === 'checkbox') {
        return { checked: el.checked === true, source: 'native' };
      }
    }
    const aria = attrOf(el, 'aria-checked').trim().toLowerCase();
    if (aria === 'true') return { checked: true, source: 'aria-checked' };
    if (aria === 'false') return { checked: false, source: 'aria-checked' };
    if (aria === 'mixed') return { checked: 'mixed', source: 'aria-checked' };
    return { checked: null, source: 'none' };
  };

  // THE INPUT'S TYPE, and it is read from the PROPERTY rather than the
  // attribute on purpose: an <input> with no type attribute is a text box,
  // and el.type reports the default the browser actually applies while
  // getAttribute reports the empty string. A selector has to match what the
  // browser applied.
  //
  // null MEANS NOT AN INPUT, and it is the same tri-state discipline
  // checkedOf keeps one function up. A <button> and an <input type="button">
  // are different elements with different ARIA roles, and reporting the
  // second's type as "" would put them in one row.
  //
  // WHY IT IS HERE AT ALL, since the census counts controls rather than
  // driving them: writes._live_control for update_setting builds its click
  // selector from the ROLE the control actually has, and an input's role is
  // decided by its type -- radio and checkbox are different roles wearing
  // one tag. Without this the selector would have to assume one of them,
  // which is exactly the guessed shape this package refuses on a write.
  const inputTypeOf = (el) => {
    const tag = (el.tagName || '').toLowerCase();
    if (tag !== 'input') return null;
    const type = String(el.type || '').toLowerCase();
    return type ? type : null;
  };

  const controls = [];
  let nodes;
  try { nodes = document.querySelectorAll(cfg.controlSelector); } catch (e) { nodes = []; }
  for (const el of nodes) {
    const named = nameOf(el);
    const href = attrOf(el, 'href');
    const expanded = attrOf(el, 'aria-expanded');
    const ariaDisabled = attrOf(el, 'aria-disabled');
    const state = checkedOf(el);
    controls.push({
      tag: (el.tagName || '').toLowerCase(),
      input_type: inputTypeOf(el),
      role: attrOf(el, 'role') || null,
      name: named.name,
      name_source: named.source,
      has_href: !!href,
      href: href,
      aria_expanded: expanded ? expanded : null,
      disabled: el.disabled === true || ariaDisabled === 'true',
      container: containerOf(el),
      checked: state.checked,
      checked_source: state.source
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
                # THE INPUT'S TYPE, or ``None`` for anything that is not an
                # ``<input>``. UNCOERCED, for the same reason ``checked`` is:
                # ``str(... or "")`` would turn "not an input" into the empty
                # string, which is a value a real type could never take and
                # would put a ``<button>`` and an ``<input type="button">`` in
                # one row. Added 2026-08-31 with the eleventh key.
                "input_type": control.get("input_type"),
                "role": control.get("role"),
                "name_source": control.get("name_source"),
                "has_href": bool(control.get("has_href")),
                "href_shape": href_shape,
                "aria_expanded": control.get("aria_expanded"),
                "disabled": bool(control.get("disabled")),
                # WHICH CONTAINER, as a SHAPE. Carried from 2026-08-31,
                # and this literal is why it needed a deliberate edit: the
                # keys are NAMED, so a field the script emits and this dict
                # does not name is dropped in silence -- which is what
                # happened to this one on the day it was added. Ten keys are
                # named now. ``str()`` with a ``none`` default rather than the
                # value, so a control from an older script that never emitted
                # the field reads ``none`` instead of ``None`` -- the same
                # absent-is-a-value discipline the rest of this reader keeps.
                "container": str(control.get("container") or "none"),
                # WHETHER IT IS CHECKED, carried from 2026-08-31, and it
                # passes through UNSHAPED AND UNCOERCED on purpose. The value
                # is ``True``, ``False``, the string ``"mixed"`` or ``None``,
                # and ``bool()`` here would turn the ``None`` into ``False``
                # -- which is the conflation the field was built to refuse:
                # ``None`` means the control is NOT CHECKABLE and ``False``
                # means it is checkable and OFF. A shaper would also flatten
                # ``"mixed"`` to ``True``.
                "checked": control.get("checked"),
                # The SOURCE gets the same ``str(... or "none")`` default
                # ``container`` uses, for the same reason: a record from an
                # older script that never emitted the key reads ``"none"``
                # rather than ``None``, so absent and unknown wear one string
                # instead of two.
                "checked_source": str(control.get("checked_source") or "none"),
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
# The self-owned editor: NAMES, inside ONE measured container
# ---------------------------------------------------------------------------
#
# WHAT THIS IS AND WHY IT IS NOT THE CENSUS. ``linkedin_surface_census``
# reports SHAPES and never names, and that gate is what makes it safe to point
# at a page made of other members. It is also why
# ``linkedin_update_profile_field`` cannot name a field to type into: the
# 2026-08-31 capture of ``/in/me/edit/intro/`` found the editor at ``dialog#0``
# with ``Save`` enabled inside it and ELEVEN controls in there, of which the
# ones that capability would target came back ``<opaque>`` -- read by the
# census and deliberately not published. Section 2g of
# ``_audit/2026-08-31-linkedin-finish.md`` carries the table.
#
# THE OPERATOR RULED on that measurement: a reader scoped to ONE container,
# MEASURED to be self-owned, may publish names the document-wide gate would
# redact, because ``dialog#0`` on his own profile editor holds only his data
# and there is no third party inside it to protect. This is that reader. The
# census is NOT changed by any of it -- nothing already published changes
# meaning, and there is no argument a caller can pass to
# ``linkedin_surface_census`` that reaches this behaviour.
#
# THE RELAXATION IS EXACTLY ONE THING WIDE, and the two halves are worth
# separating because only one of them moved:
#
# * DROPPED -- the ``<opaque>`` length/character gate, and the singleton
#   blanking in ``shape.census_redact_rare``. Both exist to stop a STRANGER'S
#   name being published, and the containment measurement is what removes the
#   stranger.
# * KEPT -- the substitutions, which are these five rules: urn,
#   ``/in/<member>/``, ``/company/<company>/``, the two possessives, and long
#   digit runs. A urn identifies somebody whichever container it was read in.
#   This reader calls ``shape.census_substitute``, which is the SAME code
#   ``shape.census_shape`` runs as its first half; the move that created it is
#   recorded in that function and pinned against pre-move outputs in
#   ``tests/test_editor_fields.py``.
#
# WHAT IT STILL MAY NOT DO. It reads control LABELS. It does not read or return
# any control's VALUE -- ``.value`` appears nowhere in the script below, and
# that is asserted rather than described. A label is "First name"; a value is
# his first name, and nothing this reader serves needs one. It returns no href
# either, only whether there was one: the container's controls can link out.
#
# THE NAME CHAIN BELOW IS A COPY OF THE ONE IN :data:`CENSUS_JS`, and the
# duplication is forced rather than chosen. ``CENSUS_JS`` is document-wide and
# returns raw names for the whole page -- running it here would bring every
# stranger's name on the profile render into this process, which is the thing
# being avoided. Assembling this script from a shared fragment is also not
# available: ``tests/test_readonly.py`` resolves injected scripts from the
# ``evaluate`` CALL SITE and every ``_JS`` attribute of this module has to be
# declared, so a fragment constant would join the declaration list as a script
# that never runs. So the chain is written twice and the two copies are held to
# agreeing by ``test_the_editor_chain_resolves_the_same_names_as_the_census``,
# which runs both scripts over one document and compares.
#
# IT READS AND RETURNS. No click, no focus, no attribute write, no scroll, no
# request: the tokens that would do any of those are refused by
# ``readonly.JS_MUTATION_TOKENS``, and this script is scanned against that list
# by name.
#
# TEN FIELDS PER CONTROL, enumerated rather than summarised because this module
# has already dropped a field by describing a dict instead of listing it --
# ``container`` on the day it was added: ``name``, ``name_source``, ``tag``,
# ``type``, ``role``, ``disabled``, ``checked``, ``checked_source``,
# ``required``, ``has_href``. The count and the names are pinned in
# ``tests/test_editor_fields.py`` rather than trusted to this comment.
EDITOR_FIELDS_JS = """
(cfg) => {
  const textOf = (node) => (node && node.innerText ? node.innerText.trim() : '');
  const attrOf = (el, name) => {
    if (!el || !el.getAttribute) return '';
    const found = el.getAttribute(name);
    return found === null ? '' : String(found).slice(0, cfg.maxChars);
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
  const labelName = (node) => textOf(node).slice(0, cfg.maxChars);
  const labelRoutes = (el) => {
    let labels = null;
    try { labels = el.labels; } catch (e) { labels = null; }
    if (!labels || !labels.length) return null;
    const id = attrOf(el, 'id');
    if (id) {
      for (const node of labels) {
        if (attrOf(node, 'for') !== id) continue;
        const named = labelName(node);
        if (named) return { name: named, source: 'label-for' };
      }
    }
    let wrapper = null;
    try { wrapper = el.closest('label'); } catch (e) { wrapper = null; }
    if (wrapper) {
      const named = labelName(wrapper);
      if (named) return { name: named, source: 'label-ancestor' };
    }
    return null;
  };
  // WHETHER THIS CONTROL'S OWN TEXT IS ITS VALUE, which for exactly one kind
  // of control it is. A contenteditable node HOLDS what has been typed into
  // it, and its accessible name falls back to that content -- so the LAST
  // route in nameOf below publishes a VALUE for these and a LABEL for
  // everything else.
  const isEditable = (el) => {
    try { if (el.isContentEditable === true) return true; } catch (e) {}
    const flag = attrOf(el, 'contenteditable').trim().toLowerCase();
    if (flag && flag !== 'false') return true;
    return attrOf(el, 'role').trim().toLowerCase() === 'textbox';
  };

  const nameOf = (el) => {
    const aria = attrOf(el, 'aria-label');
    if (aria) return { name: aria, source: 'aria-label' };
    const referenced = labelledBy(el);
    if (referenced) return { name: referenced, source: 'aria-labelledby' };
    const title = attrOf(el, 'title');
    if (title) return { name: title, source: 'title' };
    const labelled = labelRoutes(el);
    if (labelled) return labelled;
    const body = textOf(el);
    if (body) {
      // THE ONE PLACE THIS TOOL'S "LABELS, NEVER VALUES" PROMISE WAS FALSE,
      // and it was false on the field it matters most on.
      //
      // MEASURED 2026-08-31 on the live intro editor: the headline control is
      // a div[role=textbox] whose accessible name resolves through THIS
      // route, so the answer carried his headline VERBATIM. The three layers
      // built to keep values out -- a script scan for the value property, the
      // field dict's named keys, a JSON sweep of the whole answer -- all
      // catch a value read through a PROPERTY, and NONE of them covers a
      // control whose NAME IS ITS CONTENT.
      //
      // REFUSED HERE, IN THE PAGE, rather than shaped in Python, for the same
      // reason INVITE_NEEDLE_JS does its comparison in the page: a value that
      // reaches this process can reach a traceback or a log line, and no care
      // downstream un-rings that.
      //
      // THE MARKER follows the census's <opaque>/<redacted> convention and
      // means something specific: this control HAS a name, that name is its
      // own content, and this instrument will not publish it. It is not the
      // same answer as 'none', which means no name was found at all.
      //
      // WHAT THIS COSTS, stated because it is the interesting half: the
      // current value of a field is exactly what would make an edit
      // REVERTIBLE, which is one of the two things still blocking
      // update_profile_field. Withholding it keeps the promise and leaves
      // that blocker standing. Publishing it would widen this tool's stated
      // contract -- and this tool exists BECAUSE the operator ruled a narrow
      // widening, not because widenings are cheap. So it is a ruling.
      if (isEditable(el)) return { name: '<content>', source: 'content' };
      return { name: body, source: 'text' };
    }
    return { name: '', source: 'none' };
  };

  // NATIVE BEFORE ARIA, the same order and for the same reason as the census:
  // el.checked is the state the browser holds, and the TYPE GATE is what stops
  // a text box reporting as checkable-and-off. null means NOT CHECKABLE.
  const checkedOf = (el) => {
    const tag = (el.tagName || '').toLowerCase();
    if (tag === 'input') {
      const kind = String(el.type || '').toLowerCase();
      if (kind === 'radio' || kind === 'checkbox') {
        return { checked: el.checked === true, source: 'native' };
      }
    }
    const aria = attrOf(el, 'aria-checked').trim().toLowerCase();
    if (aria === 'true') return { checked: true, source: 'aria-checked' };
    if (aria === 'false') return { checked: false, source: 'aria-checked' };
    if (aria === 'mixed') return { checked: 'mixed', source: 'aria-checked' };
    return { checked: null, source: 'none' };
  };

  // THE SAME TRI-STATE DISCIPLINE checkedOf keeps, for the same reason. A
  // native form control always answers the question, so it gets true or false;
  // a button or an anchor cannot be required at all, so it gets null unless it
  // wears an aria-required saying otherwise. false there would have meant
  // "this one is optional", which is a claim nobody measured.
  const requiredOf = (el) => {
    const tag = (el.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'select' || tag === 'textarea') {
      return el.required === true;
    }
    const aria = attrOf(el, 'aria-required').trim().toLowerCase();
    if (aria === 'true') return true;
    if (aria === 'false') return false;
    return null;
  };

  const out = {
    anchor_controls: 0,
    container_kind: null,
    controls_inside: 0,
    truncated: false,
    controls: []
  };

  let all;
  try { all = Array.from(document.querySelectorAll(cfg.controlSelector)); }
  catch (e) { all = []; }

  // THE ANCHOR IS COUNTED ACROSS THE WHOLE DOCUMENT, not within a container,
  // and that is the strict direction: a second control wearing the anchor name
  // anywhere on the page means the aim is ambiguous, and choosing between them
  // would be choosing by position -- which is the defect the container
  // descriptor was added to end.
  const anchors = [];
  for (const el of all) {
    if (nameOf(el).name.trim() === cfg.anchorName) anchors.push(el);
  }
  out.anchor_controls = anchors.length;
  if (anchors.length !== 1) return out;

  let container = null;
  try { container = anchors[0].closest(cfg.containerSelector); }
  catch (e) { container = null; }
  if (!container) return out;

  // The selector admits exactly two things, so the kind is total rather than a
  // lookup: the tag, or else it matched on the role.
  const containerTag = (container.tagName || '').toLowerCase();
  out.container_kind = containerTag === 'dialog' ? 'dialog' : 'role=dialog';

  let inside;
  try { inside = Array.from(container.querySelectorAll(cfg.controlSelector)); }
  catch (e) { inside = []; }
  out.controls_inside = inside.length;

  for (const el of inside) {
    if (out.controls.length >= cfg.maxControls) break;
    const named = nameOf(el);
    const tag = (el.tagName || '').toLowerCase();
    const state = checkedOf(el);
    out.controls.push({
      name: named.name,
      name_source: named.source,
      tag: tag,
      type: tag === 'input' ? String(el.type || '').toLowerCase() : null,
      role: attrOf(el, 'role') || null,
      disabled: el.disabled === true
        || attrOf(el, 'aria-disabled').trim().toLowerCase() === 'true',
      checked: state.checked,
      checked_source: state.source,
      required: requiredOf(el),
      // WHETHER, never WHICH. The address itself stays in the page: a control
      // in this container can link out, and an href is the one field here that
      // could carry an identity out of a container measured to hold none.
      has_href: !!attrOf(el, 'href')
    });
  }
  out.truncated = out.controls.length < inside.length;
  return out;
}
"""

#: The accessible name of the intro editor's commit control, and the ONLY
#: structural handle this reader has on the container.
#:
#: MEASURED, not chosen: ``Save``, ``disabled: false``, in ``dialog#0`` beside
#: the editor's own fields, read twice on 2026-08-31 and recorded in
#: ``_audit/2026-08-31-linkedin-finish.md`` section 2g. The two DISABLED
#: ``Submit`` controls on the same render sit in ``form#3`` and ``form#6``
#: beside "Report this ad" -- they are the ad-report forms and were never this
#: editor's commit control.
#:
#: WHY A NAME AND NOT ``dialog#0``. That descriptor is an INDEX assigned in
#: document order over whatever containers the page happens to draw, and the
#: same capture found five dialogs. Which one is first is LinkedIn's business
#: and can change without anything here being wrong. The anchor is the one
#: property of the container that means something.
EDITOR_ANCHOR_NAME = "Save"

#: What counts as the container. Deliberately NARROWER than the container
#: selector inside :data:`CENSUS_JS`, which also admits ``form`` and
#: ``[role="form"]``: the ruling was about a DIALOG on his own profile editor,
#: and a form is the wrong shape to inherit it -- the same render draws two
#: ad-report forms.
EDITOR_CONTAINER_SELECTOR = 'dialog, [role="dialog"]'

#: Ceiling on controls returned from one container. The measured container held
#: eleven, so this is not a limit anybody is near; it exists so that a page
#: that changes shape cannot hand this reader an unbounded list, and it is
#: REPORTED as truncated rather than silently cut.
EDITOR_MAX_CONTROLS = 200


async def read_self_owned_editor_fields(
    page: Any,
    *,
    max_controls: int = EDITOR_MAX_CONTROLS,
    max_chars: int = 300,
    anchor_name: str = EDITOR_ANCHOR_NAME,
    container_selector: str = EDITOR_CONTAINER_SELECTOR,
) -> dict[str, Any]:
    """Label every control inside the editor dialog, or REFUSE and name why.

    THE CALLER MUST HAVE ESTABLISHED SELF-OWNERSHIP BEFORE THIS RUNS. This
    function reads a container; it does not and cannot establish whose page it
    is on. ``server.linkedin_profile_editor_fields`` is the only caller and it
    does that first, from LinkedIn's own ``isSelfProfile=true`` assertion plus
    a same-member comparison across two landed urls. Pointing this at an
    arbitrary page would publish names off it, which is precisely what the
    census's gate exists to prevent -- so it is not exposed as a tool and takes
    no argument selecting a surface.

    TWO RETURN SHAPES, AND THEY DO NOT OVERLAP.

    * Success carries ``container`` and ``fields``.
    * A refusal carries ``refused`` and ``reason`` and CARRIES NO ``fields``
      KEY AT ALL. Not an empty list: a caller must not be able to read "this
      reader would not aim" as "the container has no fields in it". That is the
      absent-is-not-zero rule the rest of this module keeps, applied to the one
      place where the wrong reading would be acted on.

    THE THREE REFUSALS, and each is the anchor rule rather than a policy:

    * ``no_anchor`` -- nothing on the page is named :data:`EDITOR_ANCHOR_NAME`.
    * ``ambiguous_anchor`` -- two or more are. Choosing between them would be
      choosing by position, which is what this reader exists not to do. Note
      the count is DOCUMENT-WIDE: a second one outside any dialog still makes
      it ambiguous, because "the one in the dialog" is itself a rule about
      position.
    * ``anchor_outside_a_container`` -- exactly one, with no
      ``dialog, [role="dialog"]`` ancestor. There is no container to scope to,
      and the whole permission is the scope.

    NAMES COME BACK UNGATED AND SUBSTITUTED. See the block above this script
    for the ruling and for the half of the shaping that survives it.
    """
    # THE ANCHOR AND CONTAINER ARE ARGUMENTS FROM 2026-09-01, defaulting to
    # the profile editor's. EDITOR_FIELDS_JS was ALREADY fully parameterised
    # on all three -- cfg.anchorName, cfg.containerSelector,
    # cfg.controlSelector -- so a second surface needs no second script, no
    # second `# readonly-ok` waiver and no budget bump. That was checked
    # before one was written: the composer's send-mode question looked like it
    # needed a new injected script and it needed a keyword argument.
    cfg = {
        "controlSelector": CENSUS_CONTROL_SELECTOR,
        "containerSelector": container_selector,
        "anchorName": anchor_name,
        "maxControls": int(max_controls),
        "maxChars": int(max_chars),
    }
    try:
        data = await page.evaluate(EDITOR_FIELDS_JS, cfg)  # readonly-ok
    except Exception as exc:
        raise ExtractionFailedError(
            f"could not read the editor container: {type(exc).__name__}: {exc}",
            url=_url_of(page),
        ) from exc

    data = dict(data or {})
    anchors = int(data.get("anchor_controls") or 0)
    if anchors == 0:
        return {
            "refused": "no_anchor",
            "reason": (
                f"no control on this page is named {anchor_name!r}, so "
                "there is nothing to identify the editor container by. This "
                "reader does not fall back to a position."
            ),
            "anchor_controls": anchors,
        }
    if anchors > 1:
        return {
            "refused": "ambiguous_anchor",
            "reason": (
                f"{anchors} controls on this page are named "
                f"{anchor_name!r}. Picking one of them would be picking "
                "by document order, which is not containment."
            ),
            "anchor_controls": anchors,
        }
    kind = data.get("container_kind")
    if not kind:
        return {
            "refused": "anchor_outside_a_container",
            "reason": (
                f"the one control named {anchor_name!r} has no "
                f"{container_selector} ancestor, so there is no "
                "container to scope this read to -- and the scope is the whole "
                "of the permission."
            ),
            "anchor_controls": anchors,
        }

    fields: list[dict[str, Any]] = []
    for control in list(data.get("controls") or []):
        fields.append(
            {
                # THE UNGATED NAME. ``census_substitute`` and not
                # ``census_shape``: the substitutions run, the <opaque> gate
                # does not. That one-word difference IS the capability.
                "name": shape.census_substitute(control.get("name")),
                "name_source": str(control.get("name_source") or "none"),
                "tag": str(control.get("tag") or ""),
                "type": control.get("type"),
                "role": control.get("role"),
                "disabled": bool(control.get("disabled")),
                # UNCOERCED, exactly as the census carries it: None means NOT
                # CHECKABLE and False means checkable and off, and bool() here
                # would collapse the two.
                "checked": control.get("checked"),
                "checked_source": str(control.get("checked_source") or "none"),
                # Same tri-state, same reason -- None is "no required marker is
                # readable on this kind of control", never "optional".
                "required": control.get("required"),
                "has_href": bool(control.get("has_href")),
            }
        )

    out: dict[str, Any] = {
        "container": {
            "kind": str(kind),
            "anchor": anchor_name,
            "controls_inside": int(data.get("controls_inside") or 0),
        },
        "fields": fields,
    }
    if data.get("truncated"):
        out["truncated"] = True
        out["truncated_note"] = (
            f"the container carried more than {max_controls} controls and the "
            "tail was not read. controls_inside is the whole-container count."
        )
    return out


# ---------------------------------------------------------------------------
# The SAME container, read for VALUES. The restore path.
# ---------------------------------------------------------------------------
#
# WHY THIS EXISTS AND WHAT IT IS FOR. ``linkedin_update_profile_field``
# overwrites a field and this server cannot say what it overwrote. The
# operator ruled on 2026-08-31 that it may ship that way PROVIDED the preview
# says so -- and then refined it on 2026-09-01, which is the ruling this
# reader answers: the previous value is the FEATURE, not the blocker. It is
# what makes the write UNDOABLE. Code can make an action correct; it cannot
# make an irreversible outward-facing action undoable. Only the old value can,
# and only if somebody has it.
#
# So this reads it. Nothing here writes, nothing here previews and nothing
# here is wired into the gate: it hands the operator the string he would need
# to type back, and the typing back is his own call through the ordinary
# two-step gate.
#
# WHY A SECOND SCRIPT RATHER THAN A FLAG ON :data:`EDITOR_FIELDS_JS`. That
# script is guarded by ``assert ".value" not in dom.EDITOR_FIELDS_JS``, which
# is UNCONDITIONAL: there is no code path, no argument and no caller mistake
# that reaches a value through it. Adding ``cfg.readValues`` would convert
# that into a claim about a branch -- the narrowest, most-scrutinised reader
# in this package would then be one flag-check away from publishing values,
# and the whole reason it is trusted is that it is not. The cost of a second
# script is a third copy of the name chain, and that cost is PAID rather than
# waved at: ``test_the_three_name_chains_agree`` runs all three over one
# document and compares name AND name_source.
#
# THE NAME HALF IS THE LABEL READER'S, UNCHANGED, and that is deliberate down
# to the ``<content>`` marker. A contenteditable's accessible name IS its own
# content, and the label reader refuses to publish it there. This reader keeps
# that refusal -- so the content is disclosed EXACTLY ONCE, in the value slot,
# where a reader knows what it is looking at. A tool that answered "the
# control called <his headline> holds <his headline>" would be publishing the
# same string twice under two different promises.
#
# VALUES COME BACK VERBATIM. NOT substituted, and this is the one place in
# this module where ``shape.census_substitute`` is deliberately NOT called on
# something published. The substitutions replace a urn, a member path, a
# company path, a possessive and a long digit run -- and every one of those is
# a legal thing to have in a headline. A substituted value is not a restore
# path; it is a corrupted string that would be pasted back as-is. Anything
# that is not exactly what the field holds is worse than nothing here, because
# the failure is SILENT: he would restore the mangled version and the tool
# would have caused the loss it was built to prevent.
#
# WHAT IS WITHHELD, IN THE PAGE, AND WHY EACH:
#
# * ``input[type=file]`` -- its value is a PATH ON HIS DISK. It names a
#   directory layout and often a real filename, neither of which is a profile
#   field and neither of which any restore needs.
# * ``input[type=password]`` -- a secret. There is no editor field this is,
#   which is exactly why it is withheld structurally rather than by noticing
#   its absence: a surface that grows one must not start publishing it.
# * checkbox and radio -- their ``value`` attribute is a submission token, not
#   the state. The STATE is ``checked`` and that is the label reader's field.
#   Publishing ``value`` here would answer a different question in the same
#   slot, which is how a caller ends up restoring the wrong thing.
#
# Withheld IN THE PAGE, for the reason ``INVITE_NEEDLE_JS`` does its
# comparison there: a string that reaches this process can reach a traceback
# or a log line, and no care downstream un-rings that.
#
# TEN FIELDS PER CONTROL, enumerated rather than summarised for the reason the
# label reader's ten are -- this module has dropped a field by describing a
# dict instead of listing it: ``name``, ``name_source``, ``tag``, ``type``,
# ``role``, ``index``, ``value``, ``value_source``, ``value_chars``,
# ``value_truncated``. ``index`` is the pairing key: both readers enumerate
# the same container with the same control selector, so position within
# ``controls_inside`` lines a value up with the label reader's record for the
# same control. Across TWO CALLS that is pairing across two renders, and the
# tool says so rather than implying the pairing is free.
#
# IT READS AND RETURNS. No click, no focus, no attribute write, no scroll, no
# request.
EDITOR_VALUES_JS = """
(cfg) => {
  const textOf = (node) => (node && node.innerText ? node.innerText.trim() : '');
  const attrOf = (el, name) => {
    if (!el || !el.getAttribute) return '';
    const found = el.getAttribute(name);
    return found === null ? '' : String(found).slice(0, cfg.maxChars);
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
  const labelName = (node) => textOf(node).slice(0, cfg.maxChars);
  const labelRoutes = (el) => {
    let labels = null;
    try { labels = el.labels; } catch (e) { labels = null; }
    if (!labels || !labels.length) return null;
    const id = attrOf(el, 'id');
    if (id) {
      for (const node of labels) {
        if (attrOf(node, 'for') !== id) continue;
        const named = labelName(node);
        if (named) return { name: named, source: 'label-for' };
      }
    }
    let wrapper = null;
    try { wrapper = el.closest('label'); } catch (e) { wrapper = null; }
    if (wrapper) {
      const named = labelName(wrapper);
      if (named) return { name: named, source: 'label-ancestor' };
    }
    return null;
  };
  const isEditable = (el) => {
    try { if (el.isContentEditable === true) return true; } catch (e) {}
    const flag = attrOf(el, 'contenteditable').trim().toLowerCase();
    if (flag && flag !== 'false') return true;
    return attrOf(el, 'role').trim().toLowerCase() === 'textbox';
  };

  // BYTE-FOR-BYTE THE LABEL READER'S CHAIN, the <content> marker included.
  // The content is published ONCE, by valueOf below, in the slot that says
  // what it is.
  const nameOf = (el) => {
    const aria = attrOf(el, 'aria-label');
    if (aria) return { name: aria, source: 'aria-label' };
    const referenced = labelledBy(el);
    if (referenced) return { name: referenced, source: 'aria-labelledby' };
    const title = attrOf(el, 'title');
    if (title) return { name: title, source: 'title' };
    const labelled = labelRoutes(el);
    if (labelled) return labelled;
    const body = textOf(el);
    if (body) {
      if (isEditable(el)) return { name: '<content>', source: 'content' };
      return { name: body, source: 'text' };
    }
    return { name: '', source: 'none' };
  };

  // THE VALUE CHAIN. Every branch is total: a control either yields a string
  // or says in source which rule withheld it, and 'none' means no route
  // applied rather than 'the field is empty'. An empty string is a REAL
  // ANSWER here -- a cleared headline is a thing he can have.
  const valueOf = (el) => {
    const tag = (el.tagName || '').toLowerCase();
    if (tag === 'input') {
      const kind = String(el.type || '').toLowerCase();
      if (kind === 'file' || kind === 'password') {
        return { value: null, source: 'withheld_by_type' };
      }
      if (kind === 'checkbox' || kind === 'radio') {
        return { value: null, source: 'state_not_value' };
      }
      // BOUND FIRST, and that is not a style choice. Comparing the
      // property against null IN PLACE puts a dot-value immediately
      // before an equals sign, and that sequence is one of
      // ``readonly.JS_MUTATION_TOKENS`` -- so the scanner reads a
      // COMPARISON as an assignment and refuses the whole script. The
      // scanner is RIGHT to be crude in that direction and must not be
      // taught about equality: a token list that starts making exceptions
      // for things that only LOOK like writes is one an actual write can
      // be dressed to slip past. So the SCRIPT is written not to look
      // like one -- and this comment is worded around the sequence for
      // the same reason, because the first draft of it tripped the
      // scanner by quoting the token it was explaining.
      const held = el.value;
      return { value: held == null ? '' : String(held), source: 'native' };
    }
    if (tag === 'textarea') {
      const held = el.value;
      return { value: held == null ? '' : String(held), source: 'native' };
    }
    if (tag === 'select') {
      // THE OPTION'S TEXT, not el.value. A select's value is the submission
      // token behind the option; what he would have to re-pick is what the
      // option SAYS. Restoring by token is not something a human can do in
      // the editor, so the token is the wrong answer to the question asked.
      let index = -1;
      try { index = el.selectedIndex; } catch (e) { index = -1; }
      if (index < 0) return { value: null, source: 'no_selection' };
      let chosen = null;
      try { chosen = el.options[index]; } catch (e) { chosen = null; }
      if (!chosen) return { value: null, source: 'no_selection' };
      const label = chosen.textContent == null ? '' : String(chosen.textContent);
      return { value: label, source: 'selected_option' };
    }
    if (isEditable(el)) {
      // NOT TRIMMED, unlike every name route above, and the difference is the
      // point of this reader. A name is being read for a human to recognise;
      // a value is being read for a human to put BACK. Trimming would return
      // a string that is not what the field holds, and the restore would
      // silently differ from the original.
      const held = el.innerText;
      return { value: held == null ? '' : String(held), source: 'content' };
    }
    return { value: null, source: 'none' };
  };

  const out = {
    anchor_controls: 0,
    container_kind: null,
    controls_inside: 0,
    truncated: false,
    controls: []
  };

  let all;
  try { all = Array.from(document.querySelectorAll(cfg.controlSelector)); }
  catch (e) { all = []; }

  // THE SAME DOCUMENT-WIDE ANCHOR COUNT the label reader keeps, and it is the
  // same rule for the same reason: a second control wearing the anchor name
  // anywhere on the page means the aim is ambiguous, and choosing between
  // them would be choosing by position.
  const anchors = [];
  for (const el of all) {
    if (nameOf(el).name.trim() === cfg.anchorName) anchors.push(el);
  }
  out.anchor_controls = anchors.length;
  if (anchors.length !== 1) return out;

  let container = null;
  try { container = anchors[0].closest(cfg.containerSelector); }
  catch (e) { container = null; }
  if (!container) return out;

  const containerTag = (container.tagName || '').toLowerCase();
  out.container_kind = containerTag === 'dialog' ? 'dialog' : 'role=dialog';

  let inside;
  try { inside = Array.from(container.querySelectorAll(cfg.controlSelector)); }
  catch (e) { inside = []; }
  out.controls_inside = inside.length;

  for (let i = 0; i < inside.length; i += 1) {
    if (out.controls.length >= cfg.maxControls) break;
    const el = inside[i];
    const named = nameOf(el);
    const tag = (el.tagName || '').toLowerCase();
    const held = valueOf(el);
    const raw = held.value;
    const full = raw === null ? null : raw.length;
    out.controls.push({
      name: named.name,
      name_source: named.source,
      tag: tag,
      type: tag === 'input' ? String(el.type || '').toLowerCase() : null,
      role: attrOf(el, 'role') || null,
      // POSITION WITHIN THE CONTAINER, which is what pairs this record with
      // the label reader's.
      //
      // AND IT IS THE SAME NUMBER AS out.controls.length UNDER THIS LOOP,
      // which is worth saying because the comment here used to claim they
      // diverge once maxControls truncates. THEY DO NOT: truncation cuts the
      // TAIL, so every row that IS pushed has the same container position as
      // row number. A mutation swapping one for the other was run and the
      // test PASSED, which is how the false claim was found.
      //
      // The two would only diverge if this loop began SKIPPING a control
      // inside the container without pushing a row -- which nothing here
      // does, and which is exactly the change that would silently break the
      // pairing with the label reader. Writing the container position is
      // what keeps that change honest rather than invisible.
      index: i,
      value: raw === null ? null : raw.slice(0, cfg.maxValueChars),
      value_source: held.source,
      // THE FULL LENGTH, always, even when the string was cut. A count is not
      // content, and a caller cannot otherwise tell a value that fitted from
      // one that did not.
      value_chars: full,
      value_truncated: full !== null && full > cfg.maxValueChars
    });
  }
  out.truncated = out.controls.length < inside.length;
  return out;
}
"""

#: Ceiling on ONE value's characters. Chosen against the surface rather than
#: picked: LinkedIn's headline caps at 220 and the About section at 2,600, so
#: 3,000 returns every profile field this reader can meet WHOLE. That is the
#: number that matters -- a truncated value is a BROKEN restore path, not a
#: shorter one, and the honest failure mode is to say so via
#: ``value_truncated`` rather than to hand back a prefix that looks complete.
EDITOR_VALUE_MAX_CHARS = 3000


async def read_self_owned_editor_values(
    page: Any,
    *,
    max_controls: int = EDITOR_MAX_CONTROLS,
    max_chars: int = 300,
    max_value_chars: int = EDITOR_VALUE_MAX_CHARS,
    anchor_name: str = EDITOR_ANCHOR_NAME,
    container_selector: str = EDITOR_CONTAINER_SELECTOR,
) -> dict[str, Any]:
    """Read what the editor's controls HOLD, or REFUSE and name why.

    THE CALLER MUST HAVE ESTABLISHED SELF-OWNERSHIP BEFORE THIS RUNS, and the
    bar is not merely the same as :func:`read_self_owned_editor_fields`'s -- it
    is literally the same code. ``server._establish_self_owned_editor`` is the
    one place either tool proves whose page it is on, and
    ``tests/test_editor_values.py`` pins that neither tool re-implements it.
    That matters more here than there: a label read off a stranger's page
    publishes what LinkedIn already shows the viewer, and a VALUE read off one
    publishes what they typed.

    TWO RETURN SHAPES AND THEY DO NOT OVERLAP, the same rule the label reader
    keeps: success carries ``container`` and ``fields``; a refusal carries
    ``refused`` and ``reason`` and NO ``fields`` key at all, so "this reader
    would not aim" can never be read as "the container holds nothing".

    THE THREE REFUSALS ARE THE ANCHOR RULE, identical to the label reader's --
    ``no_anchor``, ``ambiguous_anchor``, ``anchor_outside_a_container``.

    VALUES ARE RETURNED VERBATIM AND UNSUBSTITUTED. See the block above
    :data:`EDITOR_VALUES_JS` for why that is the only honest answer for a
    restore path, and for the three kinds of control whose value is withheld
    inside the page.
    """
    cfg = {
        "controlSelector": CENSUS_CONTROL_SELECTOR,
        "containerSelector": container_selector,
        "anchorName": anchor_name,
        "maxControls": int(max_controls),
        "maxChars": int(max_chars),
        "maxValueChars": int(max_value_chars),
    }
    try:
        data = await page.evaluate(EDITOR_VALUES_JS, cfg)  # readonly-ok
    except Exception as exc:
        raise ExtractionFailedError(
            f"could not read the editor container: {type(exc).__name__}: {exc}",
            url=_url_of(page),
        ) from exc

    data = dict(data or {})
    anchors = int(data.get("anchor_controls") or 0)
    if anchors == 0:
        return {
            "refused": "no_anchor",
            "reason": (
                f"no control on this page is named {anchor_name!r}, so "
                "there is nothing to identify the editor container by. This "
                "reader does not fall back to a position."
            ),
            "anchor_controls": anchors,
        }
    if anchors > 1:
        return {
            "refused": "ambiguous_anchor",
            "reason": (
                f"{anchors} controls on this page are named "
                f"{anchor_name!r}. Picking one of them would be picking "
                "by document order, which is not containment."
            ),
            "anchor_controls": anchors,
        }
    kind = data.get("container_kind")
    if not kind:
        return {
            "refused": "anchor_outside_a_container",
            "reason": (
                f"the one control named {anchor_name!r} has no "
                f"{container_selector} ancestor, so there is no "
                "container to scope this read to -- and the scope is the whole "
                "of the permission."
            ),
            "anchor_controls": anchors,
        }

    fields: list[dict[str, Any]] = []
    for control in list(data.get("controls") or []):
        raw_value = control.get("value")
        fields.append(
            {
                # THE NAME HALF IS THE LABEL READER'S, substitutions and all.
                # A urn in a LABEL identifies somebody whichever container it
                # was read in, and that argument does not weaken because the
                # same record also carries a value.
                "name": shape.census_substitute(control.get("name")),
                "name_source": str(control.get("name_source") or "none"),
                "tag": str(control.get("tag") or ""),
                "type": control.get("type"),
                "role": control.get("role"),
                "index": int(control.get("index") or 0),
                # THE VALUE HALF, AND census_substitute IS NOT CALLED ON IT.
                # Deliberate, argued above the script, and pinned by
                # test_a_value_that_looks_like_a_urn_is_not_substituted: a
                # substituted value is a corrupted restore string, and the
                # failure would be silent.
                "value": None if raw_value is None else str(raw_value),
                "value_source": str(control.get("value_source") or "none"),
                # UNCOERCED. None means no value route applied at all, which
                # is not the same as a zero-length value -- the
                # absent-is-not-zero rule, on the field where confusing them
                # would mean restoring an empty string over real content.
                "value_chars": control.get("value_chars"),
                "value_truncated": bool(control.get("value_truncated")),
            }
        )

    out: dict[str, Any] = {
        "container": {
            "kind": str(kind),
            "anchor": anchor_name,
            "controls_inside": int(data.get("controls_inside") or 0),
        },
        "fields": fields,
    }
    if data.get("truncated"):
        out["truncated"] = True
        out["truncated_note"] = (
            f"the container carried more than {max_controls} controls and the "
            "tail was not read. controls_inside is the whole-container count."
        )
    return out


# ---------------------------------------------------------------------------
# His OWN activity rail: ITEM KEYS, and only for items he wrote
# ---------------------------------------------------------------------------
#
# WHAT PROBLEM THIS SOLVES. ``linkedin_comment_on_item`` and
# ``linkedin_react_to_item`` are specced, registered and REFUSING, and the
# blocker was never the read boundary or the click anchor -- both are in hand.
# They are UNAIMABLE: no tool in this package returns an item key. The census
# cannot publish one by construction (``shape.census_substitute`` turns every
# ``urn:li:...`` into ``<urn>`` before a count is taken, which is the whole
# reason it is safe to point at a page of strangers), and
# ``shape.notification_handles`` deliberately yields ``{}`` for a feed urn --
# pinned in ``tests/test_notification_handles.py`` under
# ``test_a_link_with_no_usable_key_says_nothing``.
#
# THE OPERATOR RULED on 2026-08-31: build a reader over HIS OWN activity that
# returns item keys FOR HIS OWN ITEMS ONLY, and establish authorship rather
# than infer it from placement. This is that reader.
#
# THE MEASUREMENT THIS RESTS ON, taken live 2026-08-31 by
# ``linkedin_surface_census`` on the two surfaces this server may read. The two
# rows below differ in a way that IS the finding:
#
#     /in/me/   232 controls, landed .../in/<member>/?isSelfProfile=true
#       shape "Open control menu for post by <his name, in full>"  count 8
#       shape "Reaction button state: no reaction"                 count 8
#       shape "Comment"  count 8, a, href_shape .../feed/update/<urn>/
#       href_shape "https://www.linkedin.com/feed/update/<urn>/"   20 hrefs
#
#     /feed/    297 controls
#       shape "Open control menu for post by <redacted>"           count 8
#       href_shape ".../feed/update/<urn>/"                        ZERO
#
# On the profile the shape came back with a READABLE NAME at count 8, because
# ``shape.census_redact_rare`` blanks a shape only at ``count == 1`` -- so
# eight controls carried ONE author string. On the feed the same shape came
# back ``<redacted>`` at count 8, because eight controls carried EIGHT
# DIFFERENT author strings, each redacted as a singleton and then re-merged.
# THE PROFILE ACTIVITY RAIL IS UNANIMOUS IN ITS AUTHOR AND THE FEED IS NOT,
# and that asymmetry is the whole design.
#
# THREE CONJUNCTIVE CONDITIONS, ALL REQUIRED, ALL REPORTED. Two of them live
# in this script; the first lives in the caller because it is a fact about a
# url rather than about a document.
#
# * C1 -- LinkedIn's own self-assertion. ``isSelfProfile=true`` on the landed
#   url of ``/in/me/``. ``server._self_assertion_on``, the same helper
#   ``linkedin_profile_editor_fields`` uses. Not in this script.
# * C2 -- UNANIMITY. Every control whose accessible name starts with
#   :data:`ACTIVITY_OVERFLOW_PREFIX` must carry the SAME remainder, and there
#   must be at least one. Two different authors anywhere on the page is MIXED
#   and is a refusal.
# * C3 -- that one author is the PAGE OWNER, compared against the page's own
#   ``h1``.
#
# C2 IS THE SAME RULE ``writes._read_feed_item`` ALREADY APPLIES to reaction
# state -- "a mixed page cannot settle a direction for any single item", and
# picking one would be picking by position. It is also what makes the pairing
# in C4 safe: IF EVERY OVERFLOW CONTROL ON THE PAGE NAMES ONE AUTHOR, NO
# PAIRING CAN ATTRIBUTE AN ITEM TO THE WRONG PERSON. The pairing rule below
# still has to hold, and it is separately tested, but its failure mode under
# C2 is "his item is missed", never "somebody else's item is published".
#
# NO NAME AND NO HEADING TEXT LEAVES THE PAGE. The C3 comparison happens
# INSIDE the document and only booleans come out -- the same discipline
# :data:`INVITE_NEEDLE_JS` keeps, and for the same reason: a string that
# reaches Python can reach a traceback, a cache key or a log line. The author
# string and the ``h1`` text are read, compared and discarded in the page;
# neither is in this script's return value, and there is nothing for the
# reader below to redact because there is nothing to redact.
#
# THE PREFIX RULE IS WEAKER THAN EQUALITY AND THIS COMMENT SAYS SO RATHER THAN
# LETTING A LATER READER ASSUME OTHERWISE. C3 accepts when either string is a
# prefix of the other, because LinkedIn is MEASURED to write a shortened form
# of his name into the overflow label while the ``h1`` carries the full one --
# exact equality would refuse a page that is entirely his. The cost is that a
# prefix rule would also accept a DIFFERENT member whose display name is a
# prefix of the owner's. That cannot arise here, because C2 has already
# established there is exactly one author on the page and C1 has established
# the page is his -- but the rule on its own is weaker than equality, and a
# future reader who drops either of the other two conditions inherits a hole
# rather than an inconvenience.
#
# THE NAME CHAIN IS THE THIRD COPY IN THIS MODULE and the duplication is
# forced for the reason recorded above :data:`EDITOR_FIELDS_JS`: ``CENSUS_JS``
# is document-wide and returns RAW NAMES for the whole page, so running it here
# would bring every stranger's name on the render into this process, which is
# the thing being avoided; and a script assembled from a shared fragment cannot
# be certified by ``tests/test_readonly.py``, which resolves injected scripts
# from the ``evaluate`` CALL SITE. So the chain is written a third time and
# held to agreeing with the census's by
# ``test_the_activity_chain_resolves_the_same_names_as_the_census``.
#
# IT MATCHES ON THE UNION, NOT ON THE CHAIN'S WINNER, and that difference is
# deliberate and is the safety direction. ``CENSUS_JS`` resolves ONE name per
# control -- the first route that answers. This script asks whether ANY of the
# five routes yields a name carrying the overflow prefix. A control whose
# ``aria-label`` is generic while its ``title`` names an author would be
# invisible to the chain, and an author this script cannot see is an author
# C2 cannot count: unanimity would hold over a page that is not unanimous,
# which is exactly the failure A1 exists to catch. The union can only ever
# find MORE authors than the chain, so it can only ever refuse more.
#
# IT READS AND RETURNS. No click, no focus, no attribute write, no scroll, no
# request: the tokens that would do any of those are refused by
# ``readonly.JS_MUTATION_TOKENS``, and this script is scanned against that
# list by name in ``tests/test_readonly.py`` and a second time in
# ``tests/test_activity_items.py``.
#
# IT READS NO CONTROL'S VALUE. ``.value`` appears nowhere below, and that is
# asserted rather than described.
#
# THE ONE THING IT PUBLISHES IS A REAL IDENTIFIER. Every other reader in this
# module hands its output to ``shape.census_shape`` or at least to
# ``shape.census_substitute``; this one deliberately does neither for the urn
# list, because the urn IS the deliverable. Everything else it returns is a
# NUMBER or a BOOLEAN. That is the complete enumeration of what crosses this
# boundary: one list of urn strings, one mapping of those same urns to
# integers, and otherwise integers and booleans.

#: The accessible-name prefix of the item overflow control. MEASURED, not
#: chosen: ``Open control menu for post by <name>``, ``button``, ``aria-label``,
#: ``aria_expanded=false``, count 8 on his own profile and count 8 on the feed,
#: 2026-08-31. ``writes.py`` already quotes the same string in the aiming
#: preview for ``comment_on_item``.
#:
#: THE TRAILING SPACE IS LOAD-BEARING. Without it the remainder of every label
#: would begin with a space, which ``norm`` would strip anyway -- but the
#: prefix would also match a control named ``Open control menu for post byline``
#: and hand back ``line`` as an author. The space is what makes the match a
#: word boundary.
ACTIVITY_OVERFLOW_PREFIX = "Open control menu for post by "

#: The substring that marks an item permalink. MEASURED as the ``href_shape``
#: ``https://www.linkedin.com/feed/update/<urn>/``, 20 hrefs on his profile and
#: ZERO on the feed -- which is the second half of why this reader points at
#: the profile and no argument selects a surface.
ACTIVITY_PERMALINK_MARKER = "/feed/update/"

#: How short an author string may be before the TITLE route refuses to use it.
#:
#: A BOUND, NOT A FIX, and it is written as one. The heading routes compare by
#: a bidirectional PREFIX; the title route can only compare by CONTAINMENT,
#: because a browser title carries decoration a prefix cannot survive -- an
#: unread count in front of it and " | LinkedIn" behind. Containment is looser,
#: and the way it is loosest is a very short author string being a coincidental
#: substring of some other word in the title.
#:
#: Four characters is chosen against the shape LinkedIn actually writes into
#: the overflow label, which is a given name plus an initial -- ``Ada L`` is
#: five. It is not chosen against a threat model, because there is not one to
#: choose against: what this bound does is stop the DEGENERATE case, where a
#: one- or two-character author matches almost any title, from reading as an
#: established authorship claim.
ACTIVITY_MIN_AUTHOR_CHARS = 4

#: Ceiling on the ancestor climb used to find an item root when LinkedIn has
#: labelled none. Twelve, and it is a REFUSAL bound rather than a performance
#: one: a climb that runs out reports the anchor as UNPAIRED rather than
#: pairing it to something further away.
#:
#: IT IS NOT WHAT STOPS THE CLIMB REACHING ``body``, and this comment said it
#: was until the fixtures were written. ``body`` contains every overflow
#: control on the page, so a climb that stopped there would pair every urn to
#: the whole render -- and a shallow document reaches ``body`` in TWO hops,
#: well inside twelve. The script refuses ``body`` and ``documentElement`` by
#: name; see ``isDocumentLevel`` in it. The two bounds do different jobs and
#: neither replaces the other.
ACTIVITY_MAX_HOPS = 12

#: Ceiling on permalink anchors walked. The measured page carried 20; this is
#: not a limit anybody is near, and it is REPORTED as truncated rather than
#: silently cut. ``permalink_anchors`` counts every one found, so the count and
#: the walk can disagree and say so.
ACTIVITY_MAX_ANCHORS = 200

ACTIVITY_ITEMS_JS = """
(cfg) => {
  const textOf = (node) => (node && node.innerText ? node.innerText.trim() : '');
  const attrOf = (el, name) => {
    if (!el || !el.getAttribute) return '';
    const found = el.getAttribute(name);
    return found === null ? '' : String(found).slice(0, cfg.maxChars);
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
  const labelName = (node) => textOf(node).slice(0, cfg.maxChars);
  const labelRoutes = (el) => {
    let labels = null;
    try { labels = el.labels; } catch (e) { labels = null; }
    if (!labels || !labels.length) return null;
    const id = attrOf(el, 'id');
    if (id) {
      for (const node of labels) {
        if (attrOf(node, 'for') !== id) continue;
        const named = labelName(node);
        if (named) return { name: named, source: 'label-for' };
      }
    }
    let wrapper = null;
    try { wrapper = el.closest('label'); } catch (e) { wrapper = null; }
    if (wrapper) {
      const named = labelName(wrapper);
      if (named) return { name: named, source: 'label-ancestor' };
    }
    return null;
  };

  // EVERY route that answers, in the census's order -- not the first one that
  // does. nameOf() below reproduces the census's single answer and exists so
  // the two can be compared; candidatesOf() is what the prefix match runs
  // over, because a control naming an author through a LATER route than the
  // one that wins is an author C2 must still count.
  const candidatesOf = (el) => {
    const found = [];
    const aria = attrOf(el, 'aria-label');
    if (aria) found.push({ name: aria, source: 'aria-label' });
    const referenced = labelledBy(el);
    if (referenced) found.push({ name: referenced, source: 'aria-labelledby' });
    const title = attrOf(el, 'title');
    if (title) found.push({ name: title, source: 'title' });
    const labelled = labelRoutes(el);
    if (labelled) found.push(labelled);
    const body = textOf(el);
    if (body) found.push({ name: body, source: 'text' });
    return found;
  };
  const nameOf = (el) => {
    const found = candidatesOf(el);
    return found.length ? found[0] : { name: '', source: 'none' };
  };

  // WHITESPACE-NORMALISED ON BOTH SIDES of every comparison. A label wrapped
  // across two source lines and a heading with a trailing newline are the same
  // name to a reader and different strings to ===, and the C3 comparison is
  // the one place in this package where that difference would be read as
  // "a different member".
  const norm = (value) => String(
    value === null || value === undefined ? '' : value
  ).replace(/\\s+/g, ' ').trim();

  const prefix = String(cfg.overflowPrefix);

  // null means NOT AN OVERFLOW CONTROL. The empty string means it IS one and
  // carries no author behind the prefix -- a distinction C3 needs, because an
  // empty author must never satisfy a prefix rule.
  const overflowAuthorOf = (el) => {
    const found = candidatesOf(el);
    for (const candidate of found) {
      const named = norm(candidate.name);
      if (named.indexOf(prefix) === 0) return norm(named.slice(prefix.length));
    }
    return null;
  };

  let all;
  try { all = Array.from(document.querySelectorAll(cfg.controlSelector)); }
  catch (e) { all = []; }

  // C2. The author strings live in this array and NOWHERE ELSE -- they are
  // counted, compared and dropped, and the array is not part of the return.
  const distinct = [];
  let overflowControls = 0;
  for (const el of all) {
    const author = overflowAuthorOf(el);
    if (author === null) continue;
    overflowControls += 1;
    if (distinct.indexOf(author) === -1) distinct.push(author);
  }
  const unanimous = distinct.length === 1;
  const soleAuthor = unanimous ? distinct[0] : null;

  // C3. EXACTLY ONE non-empty h1, never "the first one". A page drawing two
  // headings has no unambiguous owner, and choosing between them would be
  // choosing by document order -- the same defect the container descriptor was
  // added to end. Zero and two are different refusals and are reported as a
  // COUNT so the caller can tell them apart.
  //
  // TWO ROUTES TO THE HEADING'S TEXT, AND THE SECOND EXISTS BECAUSE THE
  // FIRST ANSWERED ZERO ON THE LIVE PAGE. Until 2026-08-31 the only route was
  // ``innerText``, and it returned ZERO owner headings on the live profile --
  // twice, identically, on a page the census measured at 233 controls, so not
  // a half-render.
  //
  // WHAT IS MEASURED AND WHAT IS NOT, kept apart on purpose. MEASURED: the
  // innerText route finds no heading there. NOT MEASURED: why. ``innerText``
  // is a RENDERED-TEXT reading and returns '' for an element CSS has taken
  // out of layout, so a heading LinkedIn draws for assistive readers and
  // hides visually would produce exactly this -- but so would a heading
  // inside a shadow root, and so would a page with no h1 at all. THIS CHANGE
  // DOES NOT ASSUME WHICH. It adds the second route and reports BOTH counts,
  // so the next live reading says which of the three it is instead of being
  // interpreted. If ``textContent`` also answers zero, the refusal stands and
  // means something stronger than it did.
  //
  // WHY TAKING THE SECOND ROUTE IS NOT A RELAXATION. What C3 is checking is
  // whether LINKEDIN'S OWN MARKUP names this page's owner. That is a claim
  // about the document, not about what a sighted viewer sees, so making it
  // depend on CSS was the defect -- the same class as ``name_source: "none"``
  // meaning "this instrument cannot read one" while reading as "the control
  // has none". A visually-hidden h1 is still LinkedIn asserting whose page
  // this is, and an assistive reader is told exactly that.
  //
  // ``innerText`` IS STILL PREFERRED AND BOTH COUNTS ARE REPORTED, so a
  // caller can see which route answered and the reading stays falsifiable. If
  // BOTH are zero the refusal stands and now means something stronger: there
  // is no h1 element with any text in it at all.
  let headings;
  try { headings = Array.from(document.querySelectorAll('h1')); }
  catch (e) { headings = []; }
  const rendered = [];
  const contained = [];
  for (const node of headings) {
    const shown = norm(textOf(node));
    if (shown) rendered.push(shown);
    let raw = '';
    try { raw = norm(node && node.textContent ? node.textContent : ''); }
    catch (e) { raw = ''; }
    if (raw) contained.push(raw);
  }
  // PREFER THE RENDERED ROUTE; FALL BACK ONLY WHEN IT FOUND NOTHING AT ALL.
  //
  // WRITTEN AS TWO EXPRESSIONS RATHER THAN A BRANCH CHAIN, and that is a
  // correction rather than a style choice. The first draft was three arms --
  // "exactly one rendered", "zero rendered and exactly one contained", and a
  // catch-all -- and the CATCH-ALL ALREADY DID BOTH JOBS, so the middle arm
  // was dead. It was caught by the mutation that deletes the fallback: the
  // suite stayed green, because deleting a dead arm changes nothing. A check
  // that cannot fail certifies nothing, and neither does the code shape that
  // makes it unable to.
  //
  // NO ARITY TEST HERE ON PURPOSE. "Exactly one" is enforced downstream, on
  // ``owners.length``, so two rendered headings refuse as ambiguous instead
  // of falling through to the contained route and being resolved by it --
  // which would be resolving an ambiguity by changing the question.
  const owners = rendered.length ? rendered : contained;
  const ownerSource = rendered.length
    ? 'h1-innertext'
    : (contained.length ? 'h1-textcontent' : null);

  // THE THIRD ROUTE, AND IT EXISTS BECAUSE THE FIRST TWO BOTH ANSWERED ZERO
  // ON THE LIVE PAGE. Measured 2026-08-31, after the textContent route
  // shipped: ``owner_headings_rendered: 0`` AND ``owner_headings_contained:
  // 0``, on a page the census measured at 233 controls with
  // ``isSelfProfile=true`` and one unanimous author. The CSS hypothesis the
  // second route was built on is REFUTED -- the profile has no h1 carrying
  // text by any route. Reporting both counts is what settled that in one
  // call instead of leaving it to be argued.
  //
  // ``document.title`` IS LINKEDIN'S OWN MARKUP NAMING THE PAGE, which is the
  // same class of assertion as ``isSelfProfile=true`` on the url and is what
  // C3 has always been asking for. It is consulted LAST, so a page with a
  // real heading is still judged on the heading.
  //
  // CONTAINMENT, NOT THE PREFIX RULE, and the difference is forced by the
  // string rather than chosen: a browser title carries decoration a prefix
  // cannot survive -- an unread count in front, " | LinkedIn" behind -- so
  // the question asked is whether the ONE author every overflow control names
  // appears INSIDE it.
  //
  // WHAT THAT STILL REFUSES, which is the whole point of keeping C3 at all:
  // a rail of eight reshares by one OTHER member is unanimous and passes C2,
  // and its author does not appear in the title of HIS profile, so it refuses
  // here exactly as it would have on a heading.
  //
  // THE WEAKNESS, WRITTEN DOWN RATHER THAN HIDDEN, as the prefix rule's is:
  // containment is looser than a prefix, so a very short author string could
  // be a coincidental substring. A minimum length is required below for that
  // reason, and it is a bound rather than a fix.
  let pageTitle = '';
  try { pageTitle = norm(document.title || ''); } catch (e) { pageTitle = ''; }
  let titleMatch = null;
  if (unanimous && owners.length !== 1 && pageTitle && soleAuthor
      && soleAuthor.length >= cfg.minAuthorChars) {
    titleMatch = pageTitle.toLowerCase().indexOf(soleAuthor.toLowerCase()) !== -1;
  }

  // null means NOT COMPARED -- there was no single author, or no single
  // heading. false means compared and different. Collapsing the two would be
  // the absent-is-not-zero conflation this module keeps paying for.
  let ownerMatch = null;
  let namedBy = null;
  if (unanimous && owners.length === 1) {
    const owner = owners[0];
    ownerMatch = !!(soleAuthor && owner)
      && (soleAuthor.indexOf(owner) === 0 || owner.indexOf(soleAuthor) === 0);
    namedBy = ownerSource;
  } else if (titleMatch !== null) {
    ownerMatch = titleMatch;
    namedBy = 'document-title';
  }

  // ESTABLISHED IS NOW "C3 ANSWERED AND AGREED", whichever route answered,
  // rather than "there was exactly one heading". The heading count is still
  // what decides WHICH route runs; it is no longer what decides whether the
  // question can be asked at all.
  const established = unanimous && ownerMatch === true;

  const out = {
    overflow_controls: overflowControls,
    authors_found: distinct.length,
    unanimous: unanimous,
    owner_headings: owners.length,
    // BOTH ROUTES' COUNTS, ALWAYS, and never only the one that answered. A
    // caller that sees ``owner_headings_rendered: 0`` beside
    // ``owner_headings_contained: 1`` is being shown the CSS-visibility
    // finding directly rather than having to infer it, and a future drift in
    // either direction is visible in the reading instead of in a refusal.
    owner_headings_rendered: rendered.length,
    owner_headings_contained: contained.length,
    owner_source: namedBy,
    owner_heading_source: ownerSource,
    owner_title_present: pageTitle ? 1 : 0,
    owner_match: ownerMatch,
    established: established,
    permalink_anchors: 0,
    distinct_urns: 0,
    unrecognised: 0,
    unpaired: 0,
    item_root_source: { 'data-urn': 0, 'data-id': 0, 'climb': 0 },
    truncated: false
  };

  // C4. ANCHORED, so a malformed href cannot smuggle a string out. The shape
  // is the one MEASURED in the census's href_shape column and nothing wider:
  // a percent-encoded urn does not match and is counted unrecognised, because
  // the encoded spelling has never been observed in this position and a shape
  // nobody has seen is not a shape to admit.
  const urnShape = /^urn:li:[A-Za-z]+:[0-9]+$/;

  const hasOverflowInside = (root) => {
    if (!root || !root.querySelectorAll) return false;
    let inside;
    try { inside = Array.from(root.querySelectorAll(cfg.controlSelector)); }
    catch (e) { inside = []; }
    for (const el of inside) {
      if (overflowAuthorOf(el) !== null) return true;
    }
    return false;
  };

  // THREE ROUTES, IN ORDER, AND WHICH ONE FIRED IS REPORTED. The first two ask
  // LinkedIn where the item boundary is; the third is this script guessing,
  // and a caller has to be able to tell those apart -- the same name_source
  // discipline the rest of this module keeps. The attribute VALUE is never
  // read: [data-urn] is used as a MARKER of a boundary, and the urn that gets
  // published is always the one parsed out of the href.
  //
  // THE DOCUMENT IS NOT AN ITEM. body and documentElement contain every
  // overflow control on the page, so a route that landed on either would
  // "pair" any urn on the render to the whole render -- which is not pairing,
  // it is giving up while reporting success. THE HOP CEILING DOES NOT CLOSE
  // THIS ON ITS OWN and the tempting reading that it does is wrong: a shallow
  // page reaches body in two hops, well inside twelve. So both are here, and
  // they bound different things -- the ceiling bounds how far a deep page is
  // walked, this bounds where the walk is allowed to stop.
  const isDocumentLevel = (node) => (
    !node || node === document.body || node === document.documentElement
  );
  const rootOf = (el) => {
    let node = null;
    try { node = el.closest('[data-urn]'); } catch (e) { node = null; }
    if (node && !isDocumentLevel(node)) {
      return { root: node, source: 'data-urn' };
    }
    try { node = el.closest('[data-id]'); } catch (e) { node = null; }
    if (node && !isDocumentLevel(node)) {
      return { root: node, source: 'data-id' };
    }
    let hop = el.parentElement;
    let hops = 0;
    while (hop && !isDocumentLevel(hop) && hops < cfg.maxHops) {
      if (hasOverflowInside(hop)) return { root: hop, source: 'climb' };
      hop = hop.parentElement;
      hops += 1;
    }
    return { root: null, source: 'none' };
  };

  const marker = String(cfg.permalinkMarker);
  let anchors;
  try { anchors = Array.from(document.querySelectorAll('a[href]')); }
  catch (e) { anchors = []; }

  const seen = [];
  const perItem = [];
  let walked = 0;
  for (const el of anchors) {
    // THE RAW ATTRIBUTE, uncapped, unlike every other read in this script. The
    // cap on attrOf exists so a huge string cannot be RETURNED; an href is
    // never returned from here, only searched, and a cap would silently cut a
    // long tracking url mid-segment and report a real urn as unrecognised.
    let href = '';
    try {
      const raw = el.getAttribute('href');
      href = raw === null ? '' : String(raw);
    } catch (e) { href = ''; }
    const at = href.indexOf(marker);
    if (at === -1) continue;
    out.permalink_anchors += 1;
    if (walked >= cfg.maxAnchors) { out.truncated = true; continue; }
    walked += 1;
    let segment = href.slice(at + marker.length);
    const stop = segment.search(/[\\/?#]/);
    if (stop !== -1) segment = segment.slice(0, stop);
    if (!urnShape.test(segment)) { out.unrecognised += 1; continue; }
    const paired = rootOf(el);
    if (!paired.root || !hasOverflowInside(paired.root)) {
      out.unpaired += 1;
      continue;
    }
    out.item_root_source[paired.source] += 1;
    const index = seen.indexOf(segment);
    if (index === -1) { seen.push(segment); perItem.push(1); }
    else { perItem[index] += 1; }
  }
  out.distinct_urns = seen.length;

  // THE GATE IS HERE, IN THE PAGE, and not only in the reader below. The
  // counts above are numbers and cross the boundary on every path; the urn
  // LIST crosses it on one path only. A caller that has not established
  // authorship never receives an identifier, whatever the Python half does or
  // stops doing.
  if (established) {
    out.items = seen;
    out.anchors_per_item = {};
    for (let i = 0; i < seen.length; i += 1) {
      out.anchors_per_item[seen[i]] = perItem[i];
    }
  }
  return out;
}
"""


#: The refusal codes, enumerated because a caller branching on them needs the
#: whole set and because "the reader refuses when authorship does not hold" is
#: a completeness claim this module is not allowed to make without listing what
#: it means. C1 is not here: it is the caller's, and it never reaches this
#: reader.
ACTIVITY_REFUSALS = (
    "no_overflow_controls",
    "mixed_authors",
    "no_page_owner_heading",
    "ambiguous_page_owner_heading",
    "author_is_not_the_page_owner",
)


async def read_own_activity_items(
    page: Any,
    *,
    max_anchors: int = ACTIVITY_MAX_ANCHORS,
    max_hops: int = ACTIVITY_MAX_HOPS,
    max_chars: int = 300,
) -> dict[str, Any]:
    """Item keys for items the page owner wrote, or REFUSE and name why.

    THE CALLER MUST HAVE ESTABLISHED C1 BEFORE THIS RUNS. This function reads a
    document; it cannot see a url's query string and does not try.
    ``server.linkedin_my_activity_items`` is the only caller and it checks
    LinkedIn's own ``isSelfProfile=true`` first, with the same
    ``server._self_assertion_on`` ``linkedin_profile_editor_fields`` uses. This
    reader is not exposed as a tool and takes no argument selecting a surface,
    for the reason ``read_self_owned_editor_fields`` is not: pointed at an
    arbitrary page it would publish item keys off it.

    TWO RETURN SHAPES, AND THEY DO NOT OVERLAP.

    * Success carries ``items`` and ``anchors_per_item``.
    * A refusal carries ``refused`` and ``reason`` and CARRIES NO ``items`` KEY
      AT ALL. Not an empty list: a caller must not be able to read "this reader
      would not aim" as "he has no items". That is the absent-is-not-zero rule
      this module keeps, applied to the one place where the wrong reading is a
      claim about him rather than about a page.

    BOTH SHAPES CARRY ``counts`` AND ``item_root_source``, and that is
    deliberate. Every field in them is an integer or a boolean, so a refusal
    can say what it saw -- eight overflow controls, two authors, four
    permalinks -- without publishing anything. The one thing that changes
    between the two shapes is whether any urn string is present.

    THE FIVE REFUSALS, enumerated in :data:`ACTIVITY_REFUSALS`:

    * ``no_overflow_controls`` -- nothing on the page is named with
      :data:`ACTIVITY_OVERFLOW_PREFIX`. An empty rail is not an authorship
      claim, and treating "no author found" as "no author disagrees" is how a
      unanimity rule becomes a rubber stamp.
    * ``mixed_authors`` -- two or more distinct authors. The feed's shape, and
      the reason no argument selects a surface.
    * ``no_page_owner_heading`` -- NOTHING ON THE PAGE NAMES ITS OWNER, by any
      of the three routes. The name is kept from when there was one route,
      because a refusal code a caller branches on is not worth renaming; what
      it MEANS has widened twice in one day and both widenings were forced by
      a live reading rather than chosen.

      THREE ROUTES, IN ORDER: an ``h1``'s ``innerText``, the same ``h1``'s
      ``textContent``, then ``document.title``. The second was added when the
      live profile answered ZERO by the first on two identical readings, on
      the hypothesis that LinkedIn draws a heading CSS hides -- ``innerText``
      is a RENDERED-text reading and C3 asks a question about the DOCUMENT, so
      making it depend on CSS was a real defect whatever the live page turned
      out to do. THE LIVE PAGE THEN ANSWERED ZERO BY BOTH: it has no ``h1``
      carrying text at all, which REFUTED the hypothesis and is exactly what
      reporting both counts was for -- it settled in one call what would
      otherwise have been argued. The third route is the page's own title,
      which is LinkedIn's markup naming the page in the same sense
      ``isSelfProfile=true`` is LinkedIn's url naming it.

      Compared by CONTAINMENT rather than by prefix, and that is forced by the
      string: a browser title carries an unread count in front and
      " | LinkedIn" behind. Looser, so a minimum author length applies --
      ``ACTIVITY_MIN_AUTHOR_CHARS``, a bound and not a fix. What it still
      refuses is the case C3 exists for: a rail of reshares by one OTHER
      member is unanimous, passes C2, and its author is not in the title of
      HIS profile.
    * ``ambiguous_page_owner_heading`` -- two or more, so the comparison would
      have to choose one by document order.
    * ``author_is_not_the_page_owner`` -- C1 and C2 both held and the strings
      do not satisfy the prefix rule. This is the only refusal that says
      something about WHOSE items are on the page rather than about whether the
      page can be read.

    NOTHING THIS RETURNS IS SHAPED, AND NOTHING NEEDS TO BE. The author string
    and the heading text never leave the document -- see the block above the
    script -- so there is no name here for ``shape.census_substitute`` to act
    on. The urns are returned RAW and on purpose: a substituted urn is
    ``<urn>``, which is exactly the useless answer this reader exists to
    replace.
    """
    cfg = {
        "controlSelector": CENSUS_CONTROL_SELECTOR,
        "overflowPrefix": ACTIVITY_OVERFLOW_PREFIX,
        "permalinkMarker": ACTIVITY_PERMALINK_MARKER,
        "maxAnchors": int(max_anchors),
        "maxHops": int(max_hops),
        "maxChars": int(max_chars),
        "minAuthorChars": ACTIVITY_MIN_AUTHOR_CHARS,
    }
    try:
        data = await page.evaluate(ACTIVITY_ITEMS_JS, cfg)  # readonly-ok
    except Exception as exc:
        raise ExtractionFailedError(
            f"could not read the activity rail: {type(exc).__name__}: {exc}",
            url=_url_of(page),
        ) from exc

    data = dict(data or {})
    overflow = int(data.get("overflow_controls") or 0)
    authors = int(data.get("authors_found") or 0)
    headings = int(data.get("owner_headings") or 0)
    owner_match = data.get("owner_match")
    owner_source = data.get("owner_source")

    facts = {
        "authors_found": authors,
        # RE-DERIVED IN PYTHON from the count rather than carried over from the
        # script's own boolean. The two agree, and a test asserts they do; the
        # point of deriving it here is that ``authors_found`` is the primitive
        # a reader can check by eye against ``overflow_controls``, and a
        # boolean that disagreed with its own count would otherwise be
        # invisible.
        "unanimous": authors == 1,
        "matches_page_owner": owner_match,
        # WHICH ROUTE NAMED THE OWNER, or ``None`` when no heading did. Part
        # of the authorship facts rather than of the counts because it is a
        # statement about HOW the claim was established, and this reader's
        # whole contract is that the claim is established rather than
        # inferred. ``"h1-innertext"`` is the rendered heading;
        # ``"h1-textcontent"`` is a heading LinkedIn draws for assistive
        # readers and CSS hides. ``"document-title"`` is the page's own title,
        # consulted last and only when no heading named anybody -- which is
        # what the LIVE profile turned out to require, both heading routes
        # having answered zero on it.
        "owner_source": data.get("owner_source"),
        # WHICH HEADING ROUTE WOULD HAVE ANSWERED, separately from which route
        # actually did. ``None`` here beside a non-null ``owner_source`` is
        # exactly the live profile's shape, and reporting the two apart is
        # what makes that visible rather than inferable.
        "owner_heading_source": data.get("owner_heading_source"),
    }
    counts = {
        "overflow_controls": overflow,
        "owner_headings": headings,
        # THE TWO ROUTES, SEPARATELY, so a refusal can be diagnosed from the
        # answer instead of from the source. ``rendered`` is the innerText
        # count -- what a sighted viewer sees -- and ``contained`` is the
        # textContent count. They differ exactly when LinkedIn draws a heading
        # CSS has taken out of layout, which is what it does on the live
        # profile and what made this reader refuse for a day.
        "owner_headings_rendered": int(data.get("owner_headings_rendered") or 0),
        "owner_headings_contained": int(
            data.get("owner_headings_contained") or 0
        ),
        # WHETHER THE PAGE HAS A TITLE AT ALL, as a count rather than the
        # string. It is the third owner route's raw material and an empty one
        # is a different refusal from a title that simply does not carry the
        # author -- the same absent-is-not-zero distinction the two heading
        # counts keep.
        "owner_title_present": int(data.get("owner_title_present") or 0),
        "permalink_anchors": int(data.get("permalink_anchors") or 0),
        "distinct_urns": int(data.get("distinct_urns") or 0),
        "unrecognised": int(data.get("unrecognised") or 0),
        "unpaired": int(data.get("unpaired") or 0),
    }
    routes = dict(data.get("item_root_source") or {})
    item_root_source = {
        key: int(routes.get(key) or 0) for key in ("data-urn", "data-id", "climb")
    }

    def refusal(code: str, reason: str) -> dict[str, Any]:
        return {
            "refused": code,
            "reason": reason,
            "authorship_facts": facts,
            "counts": counts,
            "item_root_source": item_root_source,
        }

    if overflow == 0:
        return refusal(
            "no_overflow_controls",
            f"no control on this page is named with "
            f"{ACTIVITY_OVERFLOW_PREFIX!r}, so nothing on it asserts an "
            "author. An empty rail is not an authorship claim, and this "
            "reader does not treat 'nobody disagreed' as agreement.",
        )
    if authors != 1:
        return refusal(
            "mixed_authors",
            f"{overflow} control(s) on this page name an author and "
            f"{authors} distinct names are among them. A mixed page cannot "
            "say whose item any single urn belongs to, and picking one would "
            "be picking by position. None of the names is reported here; that "
            "they differ is the whole of the answer.",
        )
    # THE HEADING COUNT DECIDES WHICH ROUTE RUNS; IT NO LONGER DECIDES WHETHER
    # C3 CAN BE ASKED. Two headings is still ambiguous and still refuses --
    # picking one would be picking by document order. ZERO headings is no
    # longer a refusal by itself, because a third route exists: the page's own
    # title. Both refusals below fire only when NO route named an owner.
    if headings > 1:
        return refusal(
            "ambiguous_page_owner_heading",
            f"the page draws {headings} h1 elements with text in them, so "
            "there is no unambiguous page owner to compare the one author "
            "against. Choosing one of them would be choosing by document "
            "order -- and falling through to the title route instead would be "
            "resolving an ambiguity by changing the question.",
        )
    if owner_source is None:
        return refusal(
            "no_page_owner_heading",
            "NOTHING ON THIS PAGE NAMES ITS OWNER, by any of the three routes "
            "this reader consults. No h1 carries text -- neither rendered "
            f"({counts['owner_headings_rendered']}) nor contained "
            f"({counts['owner_headings_contained']}) -- and the page title "
            f"{'is empty' if not counts['owner_title_present'] else 'does not carry the one author found, or that author is too short to compare by containment'}"
            ". So the one author found has nothing to be compared against, "
            "and authorship is not inferred from the address this reader was "
            "pointed at.",
        )
    if owner_match is not True:
        return refusal(
            "author_is_not_the_page_owner",
            "the page carries exactly one author and an owner named through "
            f"{owner_source!r}, and the two do not match -- by prefix for a "
            "heading, by containment for the title, which is what a browser "
            "title's decoration forces. The comparison happened inside the "
            "page and NEITHER STRING is reported here; that they do not match "
            "is the whole of the answer.",
        )

    items = [str(value) for value in (data.get("items") or [])]
    per_item_raw = dict(data.get("anchors_per_item") or {})
    out: dict[str, Any] = {
        "authorship_facts": facts,
        "items": items,
        "anchors_per_item": {
            key: int(per_item_raw.get(key) or 0) for key in items
        },
        "counts": counts,
        "item_root_source": item_root_source,
    }
    if data.get("truncated"):
        out["truncated"] = True
        out["truncated_note"] = (
            f"the page carried more than {max_anchors} permalink anchors and "
            "the tail was not walked. counts.permalink_anchors is the "
            "whole-page count, so it and the walk can disagree and say so."
        )
    return out


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
# WHY ALMOST NO ``page.evaluate`` BELOW, AND WHY EXACTLY ONE. This comment
# read "WHY NO ``page.evaluate`` ANYWHERE BELOW" until 2026-08-31 and it is
# quoted rather than deleted, because the trade it describes is still the
# right one for six of these seven readers: an injected script has to be
# declared in ``test_readonly.py``'s ``INJECTED_SCRIPTS`` and put through the
# JS mutation scanner, and a locator chain injects nothing.
#
# ``INVITE_NEEDLE_JS`` is the exception and it BUYS something the other six do
# not need. Their readers count controls; this one has to COMPARE a label
# against a needle, and the label is a third party's name. A locator chain
# doing that comparison in Python would have to fetch the label into this
# process first, which is the exact thing the ruling on this capability
# forbids -- so here the cheap side of the trade is the unacceptable one. The
# script pays a boundary declaration in order to keep a name out of Python
# entirely. See the constant for what it returns, which is three numbers.

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

#: THE POST COMPOSER'S OWN TWO CONTROLS, measured on /preload/sharebox/ across
#: three settle-agreeing readings (31 controls each, verdict "consistent" on
#: the third). Both sit in ``dialog#0``.
#:
#: THE SUBMIT'S EMPTY STATE IS THE LOAD-BEARING FACT and it is why this action
#: can be gated at all: ``Post`` renders **disabled** on an empty composer. So
#: a fill produces an OBSERVABLE TRANSITION -- disabled to enabled -- and a
#: gate can require that transition before it presses anything.
#:
#: CONTRAST, because the same reasoning fails one surface over: the comment
#: control on an item permalink is named ``Comment`` and is measured ENABLED
#: while the box is empty, so no transition exists there and enabled-ness
#: discriminates nothing. Same family, opposite outcome, one measured boolean
#: apart. See ``writes._publish_submit_gate``.
POST_EDITOR_LABEL = "Text editor for creating content"
POST_SUBMIT_NAME = "Post"


def post_editor_selector() -> str:
    """The contenteditable a post's text is typed into. NO ARGUMENT.

    Assembled from a module constant, like :func:`reaction_control_selector`,
    so there is nothing a caller can influence about where a fill lands.
    """
    return 'div[role="textbox"][aria-label="' + POST_EDITOR_LABEL + '"]'


def post_submit_selector() -> str:
    """The control that publishes. NO ARGUMENT, for the same reason.

    NOT BUILT THROUGH :func:`named_role_selector`, and the reason is a guard
    worth leaving intact. That function refuses any role outside
    ``INPUT_TYPE_ROLES`` -- checkbox and radio -- because it exists to address
    a control whose ROLE was read off the row, and a role it has never
    measured would be a guess. Widening it to admit ``button`` so that this
    one call could use it would trade a measured restriction for a
    convenience, and every other caller would inherit the widening.

    So this builds its own, from a MODULE CONSTANT rather than any argument,
    and re-runs the same unsafe-character check against that constant. The
    check cannot fail today; it is here because the constant is a string
    somebody may one day re-measure and re-type, and a name carrying a quote
    would otherwise end the selector's own quoting.
    """
    if not POST_SUBMIT_NAME or any(
        bad in POST_SUBMIT_NAME for bad in _SELECTOR_UNSAFE
    ):
        raise ExtractionFailedError(
            "refusing to build the composer's submit selector: "
            "POST_SUBMIT_NAME is empty or carries a character that would end "
            "the selector's own quoting."
        )
    return 'role=button[name="' + POST_SUBMIT_NAME + '"s]'


async def read_post_composer(page: Any) -> dict[str, Any]:
    """The composer's two controls and the SUBMIT'S ENABLED STATE.

    Counts and one boolean, never text. It does NOT read what is in the
    editor: the text this server would type is already known to it -- the
    caller supplied it and the preview printed it -- so reading it back would
    add nothing and would put a draft's contents into this process for no
    purpose.

    ``submit_enabled`` is ``None`` when the control is absent, which is a
    different answer from ``False``. Absent means the page had not drawn it;
    False means it is drawn and refusing. A gate that collapsed the two would
    read a half-rendered page as a composer declining to publish.
    """
    out: dict[str, Any] = {
        "editors": 0,
        "submits": 0,
        "submit_enabled": None,
        "error": None,
    }
    try:
        out["editors"] = int(await page.locator(post_editor_selector()).count())
        submits = page.locator(post_submit_selector())
        out["submits"] = int(await submits.count())
        if out["submits"] == 1:
            out["submit_enabled"] = bool(await submits.first.is_enabled())
    except Exception as exc:  # pragma: no cover - defensive
        out["error"] = f"{type(exc).__name__}: {exc}"
        logger.debug("post composer unreadable: %s", out["error"])
    return out

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

#: THE SDUI ACTION TOKENS, as LinkedIn writes them into the React flight
#: payload. Counted, never returned as text.
#:
#: WHY THESE FOUR. ``ServerRequest`` is the one that decides: the operator
#: ruled 2026-09-01 that a click measured to issue NO ServerRequest is by
#: effect a READ. The other three are counted so that a reading of ZERO
#: ServerRequest can be told apart from a reading of NOTHING AT ALL -- a
#: parser that has stopped working reports zero of everything, and zero of
#: everything is not a measurement.
SDUI_ACTION_TOKENS: dict[str, str] = {
    "server_request": "ServerRequest",
    "navigate": "Navigate",
    "set_state": "SetState",
    "show_menu": "ShowMenu",
}

#: How far either side of a needle a component's actions are looked for.
#: DELIBERATELY GENEROUS: an over-wide window counts a NEIGHBOUR's
#: ServerRequest and refuses a click that would have been safe, where a
#: too-narrow one misses this control's own and permits a click that sends.
#: Those two errors are not symmetric, so the window errs at the safe end.
SDUI_WINDOW_CHARS = 6000

#: Read-only: sums the length of every script's text and counts token
#: occurrences. It reads ``textContent`` and returns INTEGERS -- no payload
#: string is ever returned, which is what keeps a megabyte of his profile out
#: of this process.
SDUI_ACTIONS_JS = """
(cfg) => {
  const tokens = cfg.tokens || {};
  const out = {
    script_blocks: 0,
    payload_chars: 0,
    needle_hits: 0,
    global: {},
    scoped: {},
  };
  for (const key of Object.keys(tokens)) { out.global[key] = 0; out.scoped[key] = 0; }
  const texts = [];
  for (const el of Array.from(document.scripts)) {
    const t = el.textContent || '';
    if (!t) continue;
    out.script_blocks += 1;
    out.payload_chars += t.length;
    texts.push(t);
  }
  const countIn = (hay, token) => {
    if (!token) return 0;
    let n = 0, i = hay.indexOf(token);
    while (i !== -1) { n += 1; i = hay.indexOf(token, i + token.length); }
    return n;
  };
  for (const t of texts) {
    for (const key of Object.keys(tokens)) {
      out.global[key] += countIn(t, tokens[key]);
    }
  }
  const needle = cfg.needle || '';
  if (needle) {
    const span = cfg.window || 6000;
    for (const t of texts) {
      let i = t.indexOf(needle);
      while (i !== -1) {
        out.needle_hits += 1;
        const slice = t.slice(Math.max(0, i - span), i + needle.length + span);
        for (const key of Object.keys(tokens)) {
          out.scoped[key] += countIn(slice, tokens[key]);
        }
        i = t.indexOf(needle, i + needle.length);
      }
    }
  }
  return out;
}
"""


async def read_sdui_actions(
    page: Any, needle: str = "", *, window: int = SDUI_WINDOW_CHARS
) -> dict[str, Any]:
    """Count SDUI action types in the flight payload. COUNTS ONLY, never text.

    THIS IS THE INSTRUMENT THE NO-ServerRequest RULING TURNS ON. The operator
    ruled that a click measured to issue no ``ServerRequest`` is, by effect, a
    read -- so something has to do the measuring, and this is it.

    IT RETURNS INTEGERS AND A NEEDLE-HIT COUNT AND NOTHING ELSE. The profile's
    flight payload was measured at 1,091,238 characters, 92.7% of the
    document, and it is where his identity lives -- which is exactly why the
    sanitised fixtures in this repo carry ZERO script characters. Returning
    any of it would undo that. So the page counts and this function receives
    numbers.

    ``needle`` SCOPES THE COUNT and must be a STABLE, NON-IDENTIFYING string --
    a payload ``viewName`` such as ``opento_preview_otw``, which names a
    surface rather than a person. It is never a member name.

    THE WINDOW ERRS TOWARD REFUSING. A component's actions are looked for
    within :data:`SDUI_WINDOW_CHARS` either side of the needle, and multiple
    needle hits are SUMMED rather than disambiguated. Both choices over-count:
    an over-wide window attributes a neighbour's ``ServerRequest`` to this
    control and refuses a click that would have been safe, where a too-narrow
    one misses this control's own and permits a click that SENDS. Those errors
    are not symmetric and this leans at the safe end deliberately.

    WHAT A CALLER MUST DO WITH THE RESULT, because the numbers alone are not
    the ruling: a zero ``scoped["server_request"]`` means nothing unless the
    reader has been shown returning NON-ZERO on a control known to have one.
    A parser that has stopped working returns zero for everything. See
    ``writes`` for the gate that requires that negative control before it will
    treat any zero as permission.
    """
    out: dict[str, Any] = {
        "script_blocks": 0,
        "payload_chars": 0,
        "needle_hits": 0,
        "global": {key: 0 for key in SDUI_ACTION_TOKENS},
        "scoped": {key: 0 for key in SDUI_ACTION_TOKENS},
        "readable": False,
        "error": None,
    }
    cfg = {
        "tokens": dict(SDUI_ACTION_TOKENS),
        "needle": str(needle or ""),
        "window": int(window),
    }
    try:
        reading = await page.evaluate(SDUI_ACTIONS_JS, cfg)  # readonly-ok
    except Exception as exc:  # pragma: no cover - defensive
        out["error"] = f"{type(exc).__name__}: {exc}"
        logger.debug("sdui actions unreadable: %s", out["error"])
        return out
    for key in ("script_blocks", "payload_chars", "needle_hits"):
        out[key] = int(reading.get(key) or 0)
    for bucket in ("global", "scoped"):
        got = reading.get(bucket) or {}
        out[bucket] = {key: int(got.get(key) or 0) for key in SDUI_ACTION_TOKENS}
    # READABLE means the payload was there AND carried recognisable actions.
    # A page with script blocks but no action tokens is a page this reader
    # cannot speak for, and it says so rather than reporting a comfortable
    # row of zeroes.
    out["readable"] = bool(
        out["payload_chars"] > 0 and sum(out["global"].values()) > 0
    )
    return out

#: The comment editor on an item permalink, MEASURED 2026-09-01: a div with
#: role=textbox, named through aria-label, count 1, on a page reporting
#: contenteditable == 1. Every previous census of every readable surface
#: reported zero, so this is the first comment editor this server has seen.
COMMENT_EDITOR_LABEL = "Text editor for creating comment"

#: THE COMPOSER'S TWO NAMED CONTROLS, measured 2026-09-01 on
#: /messaging/compose/ with the badge at 0 either side, no redirect and zero
#: dialogs. Recorded here because they were paid for and are the half of
#: send_message's first clause that IS met.
#:
#: THE OTHER HALF IS NOT: the message BODY's aria-label and the two SEND-MODE
#: radio labels all come back reduced by the census, and reading them needs a
#: script of its own -- see the note in writes.py. `Send` is drawn DISABLED on
#: an empty composer, the same transition signal as `Post`.
MESSAGE_RECIPIENT_LABEL = "Enter message recipients"
MESSAGE_SEND_NAME = "Send"

#: The composer's own container. Measured: every composer control -- the body
#: editor, both send-mode radios, Send and the two attach buttons -- reports
#: ``form#0``, and the page draws exactly one form.
MESSAGE_CONTAINER_SELECTOR = "form"


async def read_compose_fields(page: Any) -> dict[str, Any]:
    """Name the composer's controls, or REFUSE. Labels, never values.

    WHY THIS EXISTS AND WHY IT IS NOT THE BODY'S NAME. The composer draws TWO
    SEND-MODE RADIOS, one checked, and the census reduces both to
    ``<redacted>`` and ``<redacted> to <redacted>``. **He is on Premium
    Career, and one of those modes may be an InMail** -- a metered allowance,
    not a free action. So the unreadable choice is potentially the difference
    between sending a message and SPENDING ONE OF HIS CREDITS, and a gate that
    cannot tell him whether an action costs him something is not a gate, it is
    a formality. That makes this a hard precondition rather than a nicety.

    IT REUSES :data:`EDITOR_FIELDS_JS` RATHER THAN ADDING A SCRIPT. That
    script was already parameterised on anchor, container and control
    selector, so this surface costs no new ``# readonly-ok`` waiver and no
    budget bump -- checked before one was written.

    TWO GUARDS, AND EITHER REFUSES.

    **No recipient may be selected.** The self-ownership argument here is
    stronger than the profile editor's -- a composer with nobody in it
    contains no third party AT ALL, so there is nothing to disclose. That is
    asserted rather than assumed: once a recipient is chosen the labels start
    describing a conversation with a person in it and the argument evaporates.

    **Nothing name-shaped is published.** Any label carrying a run of
    capitalised words -- the same rule ``shape.census_redact_rare`` applies --
    stops this reader. The second send-mode label came back from the census as
    ``<redacted> to <redacted>``, two name-shaped tokens, which is exactly the
    case that must stop it. A reader that guessed there would be publishing a
    stranger's name to explain a radio button.

    A REFUSAL CARRIES NO FIELD DATA, following the profile editor's rule:
    there is no ``fields`` key on a refusal, so a refusal cannot be misread as
    "the container has none".
    """
    out: dict[str, Any] = {"refused": None, "recipients_selected": None}
    try:
        chosen = int(
            await page.locator(
                'button[aria-label^="Remove"], [data-test-selected-recipient]'
            ).count()
        )
    except Exception as exc:  # pragma: no cover - defensive
        out["refused"] = "recipient_count_unreadable"
        out["why"] = f"{type(exc).__name__}: {exc}"
        return out
    out["recipients_selected"] = chosen
    if chosen:
        out["refused"] = "recipient_already_selected"
        out["why"] = (
            f"{chosen} recipient(s) are already selected, so this composer "
            "holds a third party and the self-ownership argument this reader "
            "rests on does not apply. Nothing was read."
        )
        return out

    reading = await read_self_owned_editor_fields(
        page,
        anchor_name=MESSAGE_SEND_NAME,
        container_selector=MESSAGE_CONTAINER_SELECTOR,
    )
    # NO EXPLICIT REFUSAL PASSTHROUGH, and its absence is deliberate. One was
    # written here and REMOVED on 2026-09-01 after a mutation showed deleting
    # it left the suite green: a refusal carries no ``fields``, so the walk
    # below finds nothing to name-check and returns the reading as it arrived.
    # The branch and the test guarding it were the same redundancy twice, and
    # a branch that cannot be observed to matter is a branch that hides
    # whether the code under it works.
    fields = list(reading.get("fields") or [])
    named = [str(field.get("name") or "") for field in fields]
    offending = [name for name in named if shape.looks_name_shaped(name)]
    if offending:
        # THE GUARD REFUSES AND THE READER STILL ANSWERS.
        #
        # The raw labels are NOT returned -- not because he must not see his
        # own name, but because a control label becomes a COMMITTED CONSTANT
        # in this repository, and a literal "<name> will send message" in
        # source is a name committed. test_no_committed_identity would flag it
        # on the next run and would be right to.
        #
        # So what comes back is the DISCRIMINATOR rather than the string. The
        # composer's two send modes differ structurally and the difference
        # carries no name: one capitalised run without " to ", against two
        # runs joined by it, both before the same name-free tail. That is
        # enough to say WHICH MODE IS CHECKED, which is the question, and it
        # is storable where the label is not.
        return {
            "refused": "name_shaped_label_present",
            "recipients_selected": chosen,
            "why": (
                f"{len(offending)} control label(s) in this container carry a "
                "run of capitalised words, which is how a person's name looks "
                "to every reader in this package. The labels are NOT returned "
                "-- a label becomes a committed constant, and a name in source "
                "is a name committed. Their SHAPE is returned instead, which "
                "distinguishes the send modes without carrying anybody's name."
            ),
            # NAME-FREE BY CONSTRUCTION: counts, a boolean, and the text that
            # survives the last capitalised run.
            "label_shapes": [
                dict(shape.describe_name_shaped(name), checked=bool(field.get("checked")))
                for name, field in zip(named, fields)
                if shape.looks_name_shaped(name)
            ],
        }
    return dict(reading, recipients_selected=chosen)


def comment_editor_selector() -> str:
    """The contenteditable a comment's text is typed into. NO ARGUMENT."""
    return 'div[role="textbox"][aria-label="' + COMMENT_EDITOR_LABEL + '"]'


def comment_submit_selector(name: str) -> str:
    """A selector for the comment submit, by a name MEASURED AFTER a fill.

    THE ONE SELECTOR BUILDER HERE WHOSE NAME IS NOT A MODULE CONSTANT, and it
    is guarded hardest for exactly that reason. ``post_submit_selector`` and
    ``reaction_control_selector`` take no argument because their labels are
    measured and frozen; this control's label CANNOT be frozen, because it
    does not exist until a fill lands and nobody has ever seen it.

    So the name arrives from ``writes._comment_submit_gate``, which obtained it
    by diffing a SHAPED census -- meaning any label carrying a member's
    identity has already had it substituted out and will fail the check below
    on its ``<`` bracket. That is the intended path, not an edge case: a
    control this server cannot name without naming a person is one it does not
    press.

    NOT ROUTED THROUGH :func:`named_role_selector` for the reason
    ``post_submit_selector`` gives -- that function refuses any role outside
    ``INPUT_TYPE_ROLES``, and widening it so one caller could use it would
    trade a measured restriction for a convenience that every other caller
    would inherit.
    """
    text = str(name or "").strip()
    if not text or any(bad in text for bad in _SELECTOR_UNSAFE):
        raise ExtractionFailedError(
            "refusing to build a comment submit selector from this name: it "
            "is empty or carries a character that would end the selector's "
            "own quoting. A shaped name containing '<' means the label held "
            "somebody's identity, and that is a refusal rather than a bug."
        )
    return 'role=button[name="' + text + '"s]'


async def read_comment_surface(page: Any) -> dict[str, Any]:
    """The editor, and a SHAPED NAME CENSUS of every control on the page.

    BUILT ON ``read_surface_census`` RATHER THAN BESIDE IT, because that
    function is the only caller of ``CENSUS_JS`` and is where a raw accessible
    name is discarded. This surface is the one place in the package where
    reading names matters most and is most dangerous: LinkedIn writes OTHER
    MEMBERS' NAMES into the labels here -- ``View more options for <member>'s
    comment.`` is measured on it -- so a reader that returned raw names would
    pull third-party identity into this process to build a selector with.

    Everything below is therefore a SHAPE. A name that carried somebody's
    identity comes back with it substituted out, which also means it comes
    back UNUSABLE AS A SELECTOR -- and that is the correct outcome, not a
    limitation to work around.

    WHY A WHOLE-PAGE CENSUS AND NOT A SCOPED ONE. The comment apparatus has no
    container to scope to: the editor, the ``Comment`` control and all four
    ``Reply`` buttons report container ``none``, measured. The only
    container-bearing controls on that permalink are two ad dialogs and the
    ad-report form. So there is nothing to narrow to, and the delta this feeds
    is over the whole page with that noise named rather than hidden.
    """
    out: dict[str, Any] = {
        "editors": 0,
        "names": {},
        "controls_read": 0,
        "error": None,
    }
    try:
        out["editors"] = int(
            await page.locator(comment_editor_selector()).count()
        )
        census = await read_surface_census(page)
    except Exception as exc:  # pragma: no cover - defensive
        out["error"] = f"{type(exc).__name__}: {exc}"
        logger.debug("comment surface unreadable: %s", out["error"])
        return out
    counts: dict[str, int] = {}
    for row in census.get("control_shapes", []):
        name = str(row.get("shape") or "")
        if not name:
            continue
        counts[name] = counts.get(name, 0) + int(row.get("count") or 0)
    out["names"] = counts
    out["controls_read"] = int(census.get("controls_read") or 0)
    return out

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


def reaction_control_selector() -> str:
    """The ONE control a reaction would press, on an item permalink.

    TAKES NO ARGUMENT, AND THAT IS THE SAFETY PROPERTY RATHER THAN a
    simplification. Every other selector builder in this module is GUARDED
    because a caller supplies part of it -- a numeric job id, a company id, an
    index. This one is assembled from a module constant and nothing else, so
    there is no input to escape, no predicate to widen, and no way for a
    caller to influence what gets clicked.

    IT ANCHORS ON THE OFF LABEL, not on the state PREFIX. ``REACTION_CONTROL``
    matches any toggle state and is the right thing for COUNTING; a click must
    land only on a control measured to be in the state the action is valid
    from, so it anchors on the exact name that means "no reaction" and matches
    nothing once that has stopped being true. Pressing a control whose state
    has changed under the gate is the one thing gate 5 exists to prevent.
    """
    return 'button[aria-label="' + REACTION_OFF_LABEL + '"]'

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


def invite_control_selector(index: int) -> str:
    """A selector for ONE of the invitation controls, by its position.

    GUARDED, like every other selector builder here that takes an argument.
    ``index`` must be a real, non-negative ``int`` -- a bool is refused too,
    because ``True`` is ``1`` in Python and a boolean arriving here means a
    caller passed the wrong thing entirely.

    POSITION, AND WHY THAT IS NOT "PICKING BY POSITION". This package refuses
    to aim a write by position, and this selector is an index -- so the
    distinction has to be exact. The index is not CHOSEN; it is the output of
    :func:`writes.aim_invitation`, which returns one ONLY when the operator's
    own needle matched exactly one control on the surface. Two matches erase
    it rather than picking the first. So the position is a way of ADDRESSING
    a control his word already selected, not a way of selecting one.

    THE ANCHOR IS THE SUFFIX, NOT A NAME. These controls are labelled with
    another person's name plus :data:`INVITE_CONTROL_SUFFIX`, and this server
    does not read those names. Anchoring on the suffix keeps the selector free
    of any third-party identity while still restricting it to controls that
    are demonstrably invitations.
    """
    if isinstance(index, bool) or not isinstance(index, int) or index < 0:
        raise ValueError(
            "invite_control_selector needs a non-negative int index; a click "
            "target is built from this string, so nothing else may reach it."
        )
    return INVITE_CONTROL + " >> nth=" + str(index)

#: AIMING ONE OF THOSE NINE, AND THE REASON THIS IS A SCRIPT RATHER THAN A
#: LOCATOR CHAIN. Every other reader in the block below deliberately injects
#: nothing; this one injects, and the trade runs the other way here for one
#: reason: A NAME THAT REACHES PYTHON CANNOT BE TAKEN BACK. It can reach an
#: exception message, a log line, a cache key, a traceback, a rendered confirm
#: block -- and no care downstream un-rings that. So the comparison happens
#: INSIDE THE PAGE, where the label already lives, and what crosses back is
#: arithmetic.
#:
#: WHAT GOES IN is a needle THE OPERATOR TYPED at call time, handed over as a
#: script ARGUMENT rather than spliced into source -- so the script is a
#: constant that ``test_readonly.py`` can read whole, and no caller string ever
#: becomes executable text.
#:
#: WHAT COMES OUT IS THREE NUMBERS AND NOTHING ELSE: how many controls wear the
#: suffix, how many of those contain the needle, and -- only when that is
#: exactly one -- which position in the suffix-matched list it sits at. No
#: label, no fragment of one, no href, not even truncated. The prefix of these
#: labels has never been read by this server and is not read here either: the
#: suffix is matched AS A SUFFIX with ``endsWith``, never by rebuilding a whole
#: label from a prefix nobody has seen.
#:
#: ``index`` IS ``null`` AND NOT ``-1`` when there is no aim, deliberately. A
#: sentinel integer is an index, and ``-1`` handed to Playwright's ``nth``
#: means THE LAST CONTROL -- so the sentinel for "do not aim" would aim, at a
#: stranger, which is the one failure this whole reader exists to prevent.
INVITE_NEEDLE_JS = """
(cfg) => {
  const needle = String(cfg.needle).toLowerCase();
  const nodes = document.querySelectorAll(cfg.selector);
  let total = 0;
  let matches = 0;
  let index = null;
  let only = null;
  for (const node of nodes) {
    const label = node.getAttribute('aria-label') || '';
    // MATCHED AS A SUFFIX, and re-checked here even though cfg.selector is
    // itself a suffix selector. The two predicates are written in different
    // languages over the same fact, so a CSS engine that ever matched more
    // loosely than endsWith would be narrowed by this line rather than
    // followed by it.
    if (!label.endsWith(cfg.suffix)) continue;
    const position = total;
    total += 1;
    if (label.toLowerCase().indexOf(needle) !== -1) {
      matches += 1;
      // The FIRST match records where it sits; a SECOND erases the aim rather
      // than keeping either. Choosing between two would be choosing by
      // position, which is what the caller is refused for doing.
      index = (matches === 1) ? position : null;
      // THE LABEL RIDES THE SAME RULE AS THE INDEX, and it is erased by a
      // second match for the same reason: it exists only to let him CHECK
      // that the control his own word selected is the person he meant, and
      // there is nothing to check if the word picked out two people.
      only = (matches === 1) ? label : null;
    }
  }
  // GATED ON THE CALLER ASKING, ON TOP OF matches === 1. Two independent
  // conditions rather than one, because this is the only line in this script
  // that can emit a third party's name and a single condition is a single
  // edit away from always being true.
  const reveal = (cfg.revealSingleMatch === true) && (matches === 1);
  return {
    total: total,
    matches: matches,
    index: index,
    label: reveal ? only : null
  };
}
"""

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


async def read_invitation_surface(
    page: Any,
    needle: Optional[str] = None,
    *,
    reveal_single_match: bool = False,
) -> dict[str, Any]:
    """How many invitation controls this page draws, and -- if asked -- which.

    STILL NUMBERS AND NOTHING ELSE, WHICHEVER QUESTION IS ASKED. This control's
    accessible name IS another person's name. A reader that returned the label
    would be collecting third-party identity in order to populate a confirm
    block, which is the cost this whole family of rulings refuses to pay. So
    the label is never returned -- not shaped, not truncated, not dropped after
    a peek in Python.

    ``needle`` IS THE OPERATOR'S OWN WORD, NOT A STORED ONE. Ruled 2026-08-31:
    this server may RECEIVE a person's identity per call and must not persist
    it. That is why the needle is a parameter and not a field: it arrives, it
    is handed into the page, and it leaves with the frame. It is not written
    into the result, not into a log line, and not into any exception message
    raised below.

    WHY THE COMPARISON HAPPENS IN THE PAGE. It is what makes "never stored"
    ENFORCEABLE rather than promised. Doing it in Python would require the
    label here first, and a name that reaches this process can reach a
    traceback, a cache key or a rendered block, where no downstream care
    retrieves it. See :data:`INVITE_NEEDLE_JS`.

    THE THREE FIELDS, and the difference between two of them is the whole
    aiming rule:

    * ``controls`` -- how many controls wear :data:`INVITE_CONTROL_SUFFIX`.
    * ``matches`` -- ``None`` when NO needle was asked for, which is a
      different answer from ``0``. Zero means the question was put and nobody
      on this surface carries that word; ``None`` means nobody asked.
    * ``index`` -- the position within the suffix-matched list, set ONLY when
      ``matches`` is exactly 1. Two matches erase it rather than picking one.

    AN EMPTY NEEDLE IS NOT A NEEDLE. A blank string is a substring of every
    label, so passing one through would report a match on all nine controls --
    true, useless, and indistinguishable from a real ambiguity. It is treated
    as "nothing was asked" instead, so the two honest answers stay separable
    and no branch silently matches everybody.
    """
    out: dict[str, Any] = {
        "controls": 0,
        "matches": None,
        "index": None,
        # THE ONE LABEL, and ``None`` unless the caller ASKED for it AND the
        # needle picked out exactly one control.
        #
        # ADMITTED 2026-08-31, and the ruling turned on a distinction worth
        # keeping in view: loading a stranger's PROFILE stays refused because
        # it EMITS -- linkedin_who_viewed_me measures the receiving end, so
        # the cost lands on somebody who did not agree to it. Reading one
        # accessible name off a page already rendered on HIS OWN profile emits
        # NOTHING. Nobody is notified, no record is created, and the person is
        # not made aware. The cost to the third party is nil.
        #
        # AND HE ALREADY KNOWS THE NAME -- he supplied the needle. Reading the
        # label back is not disclosing a stranger to him; it confirms that the
        # control his own word uniquely selected belongs to the person he
        # meant. That is verification of his input, which is the opposite of
        # collection.
        "label": None,
    }
    wanted = "" if needle is None else str(needle).strip()
    if not wanted:
        try:
            out["controls"] = int(await page.locator(INVITE_CONTROL).count())
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("invite controls unreadable: %s: %s", type(exc).__name__, exc)
        return out
    cfg = {
        "selector": INVITE_CONTROL,
        "suffix": INVITE_CONTROL_SUFFIX,
        "needle": wanted,
        "revealSingleMatch": bool(reveal_single_match),
    }
    try:
        reading = await page.evaluate(INVITE_NEEDLE_JS, cfg)  # readonly-ok
    except Exception as exc:  # pragma: no cover - defensive
        # THE EXCEPTION IS NOT STRINGIFIED HERE, and every other reader in this
        # module does stringify its own. The needle was handed to that call;
        # a driver that echoes an argument back inside its error text would be
        # publishing the operator's word into a log through this line. The
        # type alone says which failure happened and carries nothing.
        logger.debug("invite needle unreadable: %s", type(exc).__name__)
        return out
    out["controls"] = int(reading.get("total") or 0)
    out["matches"] = int(reading.get("matches") or 0)
    position = reading.get("index")
    out["index"] = None if position is None else int(position)
    # THE THIRD GATE, IN PYTHON, over the two already applied in the page.
    # Three conditions rather than one on the line that can carry a name, and
    # they are written in two different languages so that a single edit
    # cannot open all of them.
    label = reading.get("label")
    if reveal_single_match and out["matches"] == 1 and isinstance(label, str):
        out["label"] = label
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
        "main_content_chars": None,
        "anchors_total": None,
        "rows_matching": None,
        "rows_visible": None,
        "scan_complete": False,
    }
    try:
        out["main_present"] = int(await page.locator("main").count()) > 0
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("tracker main presence unreadable: %s", type(exc).__name__)
        return out

    out["main_chars"] = len(await read_main_text(page))

    # RENDERED TEXT AGAINST TEXT THAT IS MERELY PRESENT, and this pair is the
    # measurement the 2026-08-30 refusal could not take. ``read_main_text`` is
    # ``inner_text``, which returns what is RENDERED; ``textContent`` returns
    # what is in the DOM whether painted or not. The whole harvest is built on
    # ``innerText`` -- ``HARVEST_LINKED_CARDS_JS``'s ``record`` drops any row
    # whose ``innerText`` is empty -- so a list drawn into the DOM and not
    # painted is INVISIBLE to it while being plainly present to a selector.
    #
    # Those two readings being far apart is the signature of exactly that, and
    # nothing else in this payload can distinguish it from a page that drew no
    # text at all.
    #
    # ``locator.text_content()`` RATHER THAN AN INJECTED SCRIPT, deliberately:
    # it is Playwright's own first-class read of ``textContent`` and needs no
    # ``readonly-ok`` waiver, where the obvious one-line ``page.evaluate``
    # would have spent one to learn the same integer. The waiver budget exists
    # to make each injection reviewable, so an injection that a plain API call
    # replaces does not get to spend it.
    try:
        content = await page.locator("main").first.text_content()
        out["main_content_chars"] = len(str(content or "").strip())
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("tracker main content unreadable: %s", type(exc).__name__)

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

    # THE SAME QUESTION ASKED OF THE ROWS THEMSELVES. Its own try, because
    # ``:visible`` is a Playwright pseudo-class rather than CSS and a future
    # engine that rejects it must cost this ONE number rather than the four
    # above it. rows_matching against rows_visible says whether the anchors a
    # selector can see are anchors a reader could have read.
    try:
        out["rows_visible"] = int(
            await page.locator(f"{TRACKER_ROW_LINK}:visible").count()
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("tracker visible scan failed: %s", type(exc).__name__)
    return out
