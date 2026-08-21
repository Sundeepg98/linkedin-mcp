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
HARVEST_LINKED_CARDS_JS = """
(cfg) => {
  const re = new RegExp(cfg.hrefPattern);
  const out = [];
  const seen = new Set();
  const anchors = document.querySelectorAll('a[href]');
  for (const a of anchors) {
    const href = a.getAttribute('href') || '';
    const m = href.match(re);
    if (!m) continue;
    const key = m[1] || href;
    if (seen.has(key)) continue;
    let node = a;
    let hops = 0;
    while (node && hops < cfg.maxHops) {
      const tag = node.tagName;
      if (tag === 'LI' || tag === 'ARTICLE') break;
      if (node.dataset && node.dataset.viewName) break;
      node = node.parentElement;
      hops += 1;
    }
    const card = node || a;
    const text = (card.innerText || '').trim();
    if (!text) continue;
    seen.add(key);
    out.push({ href: href, text: text.slice(0, cfg.maxChars) });
    if (out.length >= cfg.maxItems) break;
  }
  return out;
}
"""

#: Harvest block-shaped cards (notifications) that have no reliable link.
HARVEST_BLOCK_CARDS_JS = """
(cfg) => {
  for (const selector of cfg.selectors) {
    let nodes;
    try { nodes = document.querySelectorAll(selector); } catch (e) { continue; }
    if (!nodes || nodes.length === 0) continue;
    const out = [];
    for (const node of nodes) {
      const text = (node.innerText || '').trim();
      if (!text) continue;
      const link = node.querySelector('a[href]');
      out.push({
        href: link ? (link.getAttribute('href') || '') : '',
        text: text.slice(0, cfg.maxChars),
        selector: selector
      });
      if (out.length >= cfg.maxItems) break;
    }
    if (out.length) return out;
  }
  return [];
}
"""

#: Read the operator's own profile page: identity, about, section presence.
READ_PROFILE_JS = """
() => {
  const pick = (sels) => {
    for (const s of sels) {
      let el;
      try { el = document.querySelector(s); } catch (e) { continue; }
      if (el && el.innerText && el.innerText.trim()) return el.innerText.trim();
    }
    return null;
  };
  const sectionIds = [];
  for (const node of document.querySelectorAll('main div[id], main section[id]')) {
    const id = node.getAttribute('id') || '';
    if (id && id.length < 40 && !/^ember/.test(id)) sectionIds.push(id);
  }
  const sectionText = (id) => {
    const anchor = document.getElementById(id);
    if (!anchor) return null;
    const section = anchor.closest('section') || anchor.parentElement;
    if (!section) return null;
    const text = (section.innerText || '').trim();
    return text ? text.slice(0, 4000) : null;
  };
  const countIn = (id) => {
    const anchor = document.getElementById(id);
    if (!anchor) return null;
    const section = anchor.closest('section') || anchor.parentElement;
    if (!section) return null;
    return section.querySelectorAll('li').length;
  };
  return {
    url: document.location.href,
    name: pick(['main h1', 'h1']),
    headline: pick([
      'main .text-body-medium.break-words',
      'main .top-card-layout__headline',
      'main h1 + div'
    ]),
    location: pick([
      'main .text-body-small.inline.t-black--light.break-words',
      'main .top-card__subline-item'
    ]),
    photo: !!document.querySelector('main img.pv-top-card-profile-picture__image, main img[class*="profile-photo"]'),
    sections: sectionIds,
    about: sectionText('about'),
    skills_text: sectionText('skills'),
    experience_count: countIn('experience'),
    education_count: countIn('education'),
    skills_count: countIn('skills')
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
) -> list[dict[str, Any]]:
    """Return ``{href, text}`` for each card anchored on a matching link."""
    cfg = {
        "hrefPattern": href_pattern,
        "maxItems": int(max_items),
        "maxChars": int(max_chars),
        "maxHops": int(max_hops),
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
) -> list[dict[str, Any]]:
    """Return ``{href, text, selector}`` for the first selector that matches."""
    cfg = {
        "selectors": list(selectors),
        "maxItems": int(max_items),
        "maxChars": int(max_chars),
    }
    try:
        records = await page.evaluate(HARVEST_BLOCK_CARDS_JS, cfg)  # readonly-ok
    except Exception as exc:
        raise ExtractionFailedError(
            f"could not read the page: {type(exc).__name__}: {exc}",
            url=_url_of(page),
        ) from exc
    return list(records or [])


async def read_profile_fields(page: Any) -> dict[str, Any]:
    """Return the raw profile fields read off the rendered profile page."""
    try:
        data = await page.evaluate(READ_PROFILE_JS)  # readonly-ok
    except Exception as exc:
        raise ExtractionFailedError(
            f"could not read the profile page: {type(exc).__name__}: {exc}",
            url=_url_of(page),
        ) from exc
    return dict(data or {})


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
