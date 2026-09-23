"""WHICH CONTROL IS AT EACH INDEX OF `[aria-expanded]` / `[aria-haspopup]`?

`linkedin_server/press.py::disclose(page, shape=..., index=N)` presses
`page.locator(shape).nth(N)` over the WHOLE PAGE, where `shape` is one of the
two entries in `press.SANCTIONED_SHAPES`. Nobody has recorded WHICH control
each index actually is on two pages this server reads -- page chrome (the
global nav, a skip-link jump menu) precedes `<main>` in document order, so
index 0 on `/feed/` may be a navigation control rather than anything on the
feed itself.

This probe loads each page ONCE, PRESSES NOTHING, and reports -- for every
node matching each shape, in exactly the order `locator(shape)` would resolve
them -- structural facts plus a CLOSED-VOCABULARY TERM for its accessible
name. The name itself never crosses out of the page.

## WHAT IT MAY NOT DO

**NO CLICK. NO KEYBOARD. NO FILL. NO SCROLL. NO PRESS.** No hover either.
This file's only calls into a live page are `BROWSER.goto`, its own
`page.evaluate` script, and `locator(...).count()`. Enumerating an index
requires none of those verbs -- it is a read of attributes and structure that
are already in the document the moment it settles.

**WHAT LEAVES THIS PROCESS:** literals written in THIS file (the vocabulary's
own term names, band names, landmark names), integers, and booleans.
Component names, CSS class tokens, and now `role`/`type` cross ONLY after an
in-page regex check confines them to LinkedIn's own internal naming shape or
to the closed ARIA-role / HTML-type vocabulary -- never a raw label, never
`page.content()`, never a url. `visible` is a plain boolean: whether a press
could land on this control at all, read from `getClientRects()`, the
element's own computed visibility, and an explicit walk for an
ancestor-or-self `display:none` / `[hidden]` -- a press can only ever
address a rendered node, so the index this probe reports is only actionable
where `visible` is true.

## THE CLASSIFIER, REIMPLEMENTED RATHER THAN IMPORTED

`linkedin_server/menus.py::classify` is the model this follows: a label is
matched in the page against a closed vocabulary of UI verbs and only the
matched TERM (one of this file's own literals) crosses back, never the label.
`menus.py` cannot be called from injected JavaScript, so the algorithm --
lowercase, collapse non-`[a-z0-9]` runs to a single space, a single-word
phrase must equal the WHOLE normalised label, a multi-word phrase may be
CONTAINED as a contiguous token run, longest phrase wins by token count then
character length -- is reimplemented here in the page, over a vocabulary that
is this module's own and unrelated to `menus.VOCABULARY` (a different
surface). `menus.py`'s own docstring records the reason for the asymmetry
between single- and multi-word phrases: a bare single-word term can also be a
person's given name (`Mark`, `Star`), so it may only match a label that IS
that one word.

## THE VOCABULARY IS A STARTING FLOOR, AND SOME ENTRIES WERE COMPLETED HERE

The brief for this vocabulary gave an explicit phrase for most terms and left
seven with none, naming only the term: `show_less_analytics`, `all_viewers`,
`industry_filter`, `location_filter`, `reset`, `dismiss`, `search`. Each was
completed with the plain, single-word-or-obvious English phrasing that
parallels its given sibling (`show_more_analytics` -> `show_less_analytics`,
`interesting_viewers` -> `all_viewers`, `company_filter` -> `industry_filter`,
`job_title_filter` -> `location_filter`) or the term's own bare word
(`reset`, `dismiss`, `search`). This is a judgement call recorded here rather
than hidden in a diff; every completed term is single-word, so the same
whole-label-only rule that already protects `nav_me` ("me") and `company_filter`
("company") protects these too.

## SESSION HEALTH, AND WHY IT LOADS NOTHING FURTHER ON A HIT

Before this file trusts anything about a page, it asks whether the SESSION
answered at all. `config.AUTHWALL_MARKERS` covers a redirect; a CLOSED list of
challenge phrases, matched INSIDE THE PAGE against `document.body.innerText`
and reported back only as which of THIS FILE's own phrases hit, covers an
interstitial that does not redirect. Either one stops the run: a page that
did not answer teaches nothing about where a control sits, and reading
further would be measuring the wall instead of the page.

## THE DETECTOR CONTROL

`run_detector_control()` mirrors the convention in
`scripts/_probe_off_platform_controls.py`: a KNOWN document with a KNOWN
answer, checked before any live load and re-checked immediately before one.
Unlike that file's plain string-counting control, this probe's classification
logic lives entirely inside the injected script, so the control launches a
throwaway LOCAL Chromium -- never the operator's attached browser, never the
persistent profile -- sets a small fixed document, and asserts the script
reports the landmark, the attribute value and the vocabulary term it is known
to have. Runnable standalone::

    ./venv/Scripts/python.exe scripts/_probe_disclosure_targets.py --control

Live run (attach only; refuses otherwise)::

    set LINKEDIN_CDP_ATTACH=1
    venv\\Scripts\\python.exe scripts/_probe_disclosure_targets.py

Writes its record under gitignored `_state/readers4/disclosure-targets.json`.
Prints integers, booleans, and this file's own literals.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import config, readonly  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

_ROOT = Path(__file__).resolve().parents[1]

#: How long to wait between the two in-page readings. Long enough that a page
#: still hydrating at t+0 has settled by t+4, matching the wait this
#: repository's own settle-without-a-press probe used for the same question.
STABILITY_WAIT_S = 4.0

#: The two shapes `press.disclose` may address -- read from that module's own
#: enumeration would be the tidy move, but `press.SANCTIONED_SHAPES` is a
#: constant about what may be PRESSED, and this file's whole point is to stay
#: entirely on the read side of that boundary, importing nothing from it.
SHAPE_EXPANDED = "[aria-expanded]"
SHAPE_HASPOPUP = "[aria-haspopup]"

#: The two targets, serial, profile-views first. Loads go through
#: `BROWSER.goto`, which enforces `config.MIN_NAVIGATION_INTERVAL_S` (3.0s by
#: default) between navigations, so no extra spacing is added here.
TARGETS: tuple[str, ...] = (
    "%s/analytics/profile-views/" % config.BASE_URL,
    "%s/feed/" % config.BASE_URL,
)

#: `aria-haspopup`'s own closed value vocabulary. A value off this list
#: crosses as "other", never itself.
HASPOPUP_TOKENS: tuple[str, ...] = (
    "true", "false", "menu", "listbox", "dialog", "tree", "grid",
)

#: The container a record's `item_ordinal` is counted against -- a feed-item
#: or tracker-row shaped selector, never a person-bearing one.
ITEM_SELECTOR = "[data-urn], [data-id]"

#: THE OTHER WAY A FEED MARKS ONE POST, added by the wave lead after review:
#: the ARIA feed pattern puts each item in an ``article`` / ``[role=article]``.
#: A current feed may carry that and no ``data-urn`` at all, and a probe that
#: knew only one marker would report every control as belonging to no item.
#: Counted separately so the two markers can disagree visibly.
ARTICLE_SELECTOR = 'article, [role="article"]'

#: A CLOSED list of challenge-interstitial phrases. Matched INSIDE the page
#: against `document.body.innerText`; only which of THESE literals hit ever
#: crosses back.
CHALLENGE_PHRASES: tuple[str, ...] = (
    "unusual activity",
    "security verification",
    "security check",
    "captcha",
    "verify you are human",
    "too many requests",
    "temporarily restricted",
    "let's confirm it's you",
)

#: THE VOCABULARY. Every string this probe can emit as a `term` is a key
#: here, and every value is this file's own literal -- never a page's.
#: See the module docstring for which entries were completed by the
#: implementer where the brief named only the term.
VOCABULARY: dict[str, tuple[str, ...]] = {
    "show_more_analytics": ("show more analytics",),
    "show_less_analytics": ("show less analytics",),
    "interesting_viewers": ("interesting viewers",),
    "all_viewers": ("all viewers",),
    "company_filter": ("company",),
    "industry_filter": ("industry",),
    "job_title_filter": ("job title",),
    "location_filter": ("location",),
    "time_range": (
        "past 7 days", "past 14 days", "past 28 days", "past 30 days",
        "past 90 days", "past 365 days", "past year",
    ),
    "all_filters": ("all filters",),
    "sort": ("most recent", "most relevant", "sort by"),
    "reset": ("reset",),
    "submit": ("submit", "show results", "apply"),
    "recruiter_views": ("view all recruiters",),
    "nav_me": ("me",),
    "nav_for_business": ("for business",),
    "nav_badge": ("new notification", "new notifications"),
    "jump_menu": (
        "skip to main content", "skip to search", "skip to primary content",
        "skip to aside", "close jump menu", "jump menu",
    ),
    "more": ("more",),
    "ad_menu": (
        "hide or report this ad", "report this ad", "why am i seeing this ad",
    ),
    "dismiss": ("dismiss",),
    "search": ("search",),
    "post_control_menu": ("open control menu",),
    "send": ("send", "send in a private message"),
    "repost": ("repost",),
    "start_a_post": ("start a post",),
    "reactions_menu": ("open reactions menu",),
    "react": ("like", "react"),
    "comment": ("comment",),
    "copy_link": ("copy link to post", "copy link"),
    "embed": ("embed this post",),
    "share_via": ("share via",),
    "share": ("share",),
    "save": ("save",),
    "premium_upsell": ("try premium", "try it"),
    # ADDED FOR THE SIBLING LANE L2's M C29 question (sort a post's comments):
    # whether any comment control is drawn at all on the first render. A
    # single word, so it matches only a label that IS the word.
    "comments": ("comments",),
}

#: A closed vocabulary term never begins with the refusal marker, so the two
#: alphabets cannot collide once `term()` reports one or the other.
REFUSAL_KEYS: tuple[str, ...] = ("no_label", "unmatched")


def emitted_alphabet() -> frozenset[str]:
    """Every string `term`/`refused` may ever hold. See `menus.emitted_alphabet`."""
    return frozenset(VOCABULARY) | frozenset(REFUSAL_KEYS)


def _phrase_index() -> list[list[str]]:
    """``[[phrase, term], ...]`` sorted longest-first. See `menus._PHRASE_INDEX`."""
    pairs = [
        (phrase, term)
        for term, phrases in VOCABULARY.items()
        for phrase in phrases
    ]
    pairs.sort(key=lambda pair: (-len(pair[0].split()), -len(pair[0]), pair[0]))
    return [[phrase, term] for phrase, term in pairs]


def _build_cfg() -> dict:
    """The one object handed into every `DISCLOSURE_TARGETS_JS` call. Pure."""
    return {
        "itemSelector": ITEM_SELECTOR,
        "articleSelector": ARTICLE_SELECTOR,
        "phraseIndex": _phrase_index(),
        "haspopupTokens": list(HASPOPUP_TOKENS),
    }


#: Reads `document.body.innerText` once, INSIDE the page, and returns a
#: boolean per `cfg.phrases` -- never the text itself.
CHALLENGE_CHECK_JS = """
(cfg) => {
  const body = document.body;
  const text = (body && body.innerText ? body.innerText : "").toLowerCase();
  const phrases = cfg.phrases || [];
  const hits = [];
  for (let i = 0; i < phrases.length; i++) {
    hits.push(text.indexOf(String(phrases[i]).toLowerCase()) >= 0);
  }
  return hits;
}
"""

#: THE READER. Builds, separately, a list of records for `[aria-expanded]`
#: and for `[aria-haspopup]`, in document order, plus page-level counts.
#: Every field is either a count, a boolean, a closed-enum string, or a
#: string an in-page regex has confined to LinkedIn's own component/class
#: naming shape. See the module docstring for the full contract.
DISCLOSURE_TARGETS_JS = """
(cfg) => {
  const MAX_LABEL_CHARS = 400;

  const normalise = (label) => {
    const lowered = String(label).toLowerCase();
    let out = "";
    let prevSpace = true;
    for (let i = 0; i < lowered.length; i++) {
      const ch = lowered[i];
      if ((ch >= "a" && ch <= "z") || (ch >= "0" && ch <= "9")) {
        out += ch;
        prevSpace = false;
      } else if (!prevSpace) {
        out += " ";
        prevSpace = true;
      }
    }
    return out.trim();
  };

  const containsPhrase = (haystackWords, phraseWords) => {
    if (phraseWords.length === 0 || phraseWords.length > haystackWords.length) {
      return false;
    }
    if (phraseWords.length === 1) {
      return haystackWords.length === 1 && haystackWords[0] === phraseWords[0];
    }
    for (let start = 0; start <= haystackWords.length - phraseWords.length; start++) {
      let match = true;
      for (let j = 0; j < phraseWords.length; j++) {
        if (haystackWords[start + j] !== phraseWords[j]) { match = false; break; }
      }
      if (match) return true;
    }
    return false;
  };

  const band = (length) => {
    if (length >= 41) return "41-plus";
    if (length >= 21) return "21-40";
    if (length >= 9) return "9-20";
    if (length >= 1) return "1-8";
    return "empty";
  };

  const classify = (rawLabel) => {
    if (rawLabel === null || rawLabel === undefined) {
      return { refused: "no_label" };
    }
    const raw = String(rawLabel).slice(0, MAX_LABEL_CHARS);
    const normalised = normalise(raw);
    if (!normalised) {
      return { refused: "no_label" };
    }
    const words = normalised.split(" ");
    const index = cfg.phraseIndex || [];
    for (let i = 0; i < index.length; i++) {
      const phraseWords = index[i][0].split(" ");
      if (containsPhrase(words, phraseWords)) {
        return { term: index[i][1] };
      }
    }
    const trimmed = raw.trim();
    const tokens = trimmed.length ? trimmed.split(/\\s+/) : [];
    const hasDigits = /[0-9]/.test(raw);
    let allCapitalised = tokens.length > 0;
    for (let i = 0; i < tokens.length; i++) {
      const first = tokens[i].charAt(0);
      if (/[a-zA-Z]/.test(first) && first !== first.toUpperCase()) {
        allCapitalised = false;
        break;
      }
    }
    return {
      refused: "unmatched",
      band: band(trimmed.length),
      tokens: tokens.length,
      has_digits: hasDigits,
      all_capitalised: allCapitalised,
    };
  };

  const accessibleName = (el) => {
    const ariaLabel = el.getAttribute("aria-label");
    if (ariaLabel) return ariaLabel;
    const labelledBy = el.getAttribute("aria-labelledby");
    if (labelledBy) {
      const parts = [];
      const ids = labelledBy.split(/\\s+/).filter((s) => s.length > 0);
      for (let i = 0; i < ids.length; i++) {
        const target = document.getElementById(ids[i]);
        if (target && target.textContent) parts.push(target.textContent);
      }
      if (parts.length > 0) return parts.join(" ");
    }
    const title = el.getAttribute("title");
    if (title) return title;
    return el.innerText || el.textContent || null;
  };

  const VIEW_NAME_RE = /^[a-z0-9][a-z0-9-]{0,59}$/;
  const CLASS_TOKEN_RE = /^[a-z][a-z0-9_-]{2,60}$/;
  const DIGIT_RUN_RE = /[0-9]{3,}/;
  const NUMERIC_P_RE = /^[0-9][0-9,.]*%?$/;
  const ROLE_TYPE_RE = /^[a-z][a-z-]{0,23}$/;

  const shapedView = (value) => (VIEW_NAME_RE.test(value) ? value : "<unshaped>");

  // `role` and `type` are closed, ASCII, hyphen-lowercase vocabularies by
  // their own specs (ARIA roles, HTML input/button types) -- same
  // discipline as own_view: present-and-shape-valid crosses verbatim,
  // present-and-off-shape crosses as the sentinel, absent crosses as null.
  // Never the raw attribute value on any branch that fails the regex.
  const shapedAttr = (value) => (
    value === null ? null : (ROLE_TYPE_RE.test(value) ? value : "<unshaped>")
  );

  const ownView = (el) => {
    const value = el.getAttribute("data-view-name");
    return value === null ? null : shapedView(value);
  };

  const holderView = (el) => {
    let node = el.parentElement;
    let depth = 0;
    while (node) {
      depth += 1;
      const value = node.getAttribute ? node.getAttribute("data-view-name") : null;
      if (value !== null && value !== undefined) {
        return { view: shapedView(value), depth: depth };
      }
      node = node.parentElement;
    }
    return { view: null, depth: -1 };
  };

  const LANDMARK_TAGS = ["header", "nav", "main", "aside", "footer", "dialog"];
  const LANDMARK_ROLES = [
    "banner", "navigation", "main", "complementary", "contentinfo", "search",
    "dialog",
  ];

  const landmarkOf = (el) => {
    let node = el.parentElement;
    while (node) {
      const tag = node.tagName ? node.tagName.toLowerCase() : "";
      if (LANDMARK_TAGS.indexOf(tag) >= 0) return tag;
      const role = node.getAttribute ? node.getAttribute("role") : null;
      if (role && LANDMARK_ROLES.indexOf(role.toLowerCase()) >= 0) {
        return "role:" + role.toLowerCase();
      }
      node = node.parentElement;
    }
    return "none";
  };

  const classesOf = (el) => {
    const out = [];
    const list = el.classList ? Array.from(el.classList) : [];
    for (let i = 0; i < list.length && out.length < 6; i++) {
      const token = list[i];
      if (CLASS_TOKEN_RE.test(token) && !DIGIT_RUN_RE.test(token)) {
        out.push(token);
      }
    }
    return out;
  };

  const isHiddenish = (node) => {
    if (!node || node.nodeType !== 1) return false;
    if (node.hasAttribute("hidden")) return true;
    if (node.getAttribute("aria-hidden") === "true") return true;
    let style = null;
    try { style = window.getComputedStyle(node); } catch (e) { return false; }
    if (!style) return false;
    return style.display === "none" || style.visibility === "hidden";
  };

  const targetHidden = (el) => {
    let node = el;
    while (node) {
      if (isHiddenish(node)) return true;
      node = node.parentElement;
    }
    return false;
  };

  // A press can only land on a control that is actually rendered. Three
  // signals, all required: at least one client rect (catches an ancestor's
  // display:none reliably, since a non-rendered subtree has none), the
  // element's OWN computed visibility is not "hidden" (visibility is
  // inherited, so this also catches an ancestor's visibility:hidden), and
  // an EXPLICIT walk of the element and every ancestor for display:none or
  // the `hidden` attribute -- kept separate from `isHiddenish` above, which
  // also treats aria-hidden as hidden: aria-hidden is an ACCESSIBILITY-tree
  // signal, and an aria-hidden element can still be visually rendered and
  // pressable, which is a different question from the one this answers.
  const isVisible = (el) => {
    if (el.getClientRects().length === 0) return false;
    let ownStyle = null;
    try { ownStyle = window.getComputedStyle(el); } catch (e) { return false; }
    if (!ownStyle || ownStyle.visibility === "hidden") return false;
    let node = el;
    while (node) {
      if (node.nodeType !== 1) { node = node.parentElement; continue; }
      if (node.hasAttribute && node.hasAttribute("hidden")) return false;
      let style = null;
      try { style = window.getComputedStyle(node); } catch (e) { return false; }
      if (style && style.display === "none") return false;
      node = node.parentElement;
    }
    return true;
  };

  const textBand = (length) => {
    if (length <= 0) return "0";
    if (length <= 40) return "1-40";
    if (length <= 200) return "41-200";
    if (length <= 1000) return "201-1000";
    return "1001-plus";
  };

  const controlsOf = (el) => {
    const raw = el.getAttribute("aria-controls");
    const out = {
      present: raw !== null && raw.trim().length > 0,
      target_found: false,
      target_hidden: false,
      text_band: "0",
      view_names: [],
      numeric_p: 0,
      labels: 0,
      menuitems: 0,
      options: 0,
    };
    if (!out.present) return out;
    let target = null;
    const ids = raw.split(/\\s+/).filter((s) => s.length > 0);
    for (let i = 0; i < ids.length; i++) {
      const found = document.getElementById(ids[i]);
      if (found) { target = found; break; }
    }
    if (!target) return out;
    out.target_found = true;
    out.target_hidden = targetHidden(target);
    const text = target.innerText || target.textContent || "";
    out.text_band = textBand(text.trim().length);
    const seenViews = [];
    const viewNodes = target.querySelectorAll("[data-view-name]");
    for (let i = 0; i < viewNodes.length && seenViews.length < 12; i++) {
      const value = viewNodes[i].getAttribute("data-view-name");
      const shaped = shapedView(value);
      if (seenViews.indexOf(shaped) < 0) seenViews.push(shaped);
    }
    out.view_names = seenViews;
    const paragraphs = target.querySelectorAll("p");
    let numericCount = 0;
    for (let i = 0; i < paragraphs.length; i++) {
      const trimmed = (paragraphs[i].textContent || "").trim();
      if (NUMERIC_P_RE.test(trimmed)) numericCount += 1;
    }
    out.numeric_p = numericCount;
    out.labels = target.querySelectorAll("label").length;
    out.menuitems = target.querySelectorAll("[role='menuitem']").length;
    out.options = target.querySelectorAll("[role='option'], option").length;
    return out;
  };

  const itemContainers = Array.from(document.querySelectorAll(cfg.itemSelector));

  const itemOrdinalOf = (el) => {
    const container = el.closest(cfg.itemSelector);
    return container ? itemContainers.indexOf(container) : -1;
  };

  const articleContainers = Array.from(
    document.querySelectorAll(cfg.articleSelector)
  );

  const articleOrdinalOf = (el) => {
    const container = el.closest(cfg.articleSelector);
    return container ? articleContainers.indexOf(container) : -1;
  };

  const recordFor = (el, idx) => {
    const expandedRaw = el.getAttribute("aria-expanded");
    let expanded = null;
    if (expandedRaw !== null) {
      const lowered = expandedRaw.toLowerCase();
      expanded = (lowered === "true" || lowered === "false") ? lowered : "other";
    }
    const haspopupRaw = el.getAttribute("aria-haspopup");
    let haspopup = null;
    if (haspopupRaw !== null) {
      const lowered = haspopupRaw.toLowerCase();
      const tokens = cfg.haspopupTokens || [];
      haspopup = tokens.indexOf(lowered) >= 0 ? lowered : "other";
    }
    const holder = holderView(el);
    const record = {
      idx: idx,
      tag: el.tagName ? el.tagName.toLowerCase() : "",
      role: shapedAttr(el.getAttribute("role")),
      type: shapedAttr(el.getAttribute("type")),
      expanded: expanded,
      haspopup: haspopup,
      landmark: landmarkOf(el),
      in_main: !!el.closest('main,[role="main"]'),
      in_form: !!el.closest("form"),
      own_view: ownView(el),
      holder_view: holder.view,
      holder_depth: holder.depth,
      classes: classesOf(el),
      controls: controlsOf(el),
      term: classify(accessibleName(el)),
      item_ordinal: itemOrdinalOf(el),
      article_ordinal: articleOrdinalOf(el),
      visible: isVisible(el),
    };
    if (record.tag === "select") {
      const options = Array.from(el.querySelectorAll("option")).slice(0, 20);
      record.option_count = el.querySelectorAll("option").length;
      record.option_terms = options.map((opt) => classify(opt.textContent));
    }
    return record;
  };

  const buildShape = (selector) => {
    const nodes = Array.from(document.querySelectorAll(selector));
    return nodes.map((el, idx) => recordFor(el, idx));
  };

  return {
    expanded: { records: buildShape("[aria-expanded]") },
    haspopup: { records: buildShape("[aria-haspopup]") },
    page_counts: {
      aria_expanded: document.querySelectorAll("[aria-expanded]").length,
      aria_expanded_true: document.querySelectorAll('[aria-expanded="true"]').length,
      aria_haspopup: document.querySelectorAll("[aria-haspopup]").length,
      role_menu: document.querySelectorAll('[role="menu"]').length,
      role_menuitem: document.querySelectorAll('[role="menuitem"]').length,
      role_dialog: document.querySelectorAll('[role="dialog"]').length,
      dialog_tag: document.querySelectorAll("dialog").length,
      role_listbox: document.querySelectorAll('[role="listbox"]').length,
      form: document.querySelectorAll("form").length,
      select: document.querySelectorAll("select").length,
      main_present: document.querySelectorAll('main,[role="main"]').length > 0,
      item_containers: itemContainers.length,
      articles: articleContainers.length,
    },
  };
}
"""

#: A small KNOWN document with a KNOWN answer -- the detector control's
#: fixture. Kept separate from the offline test's much larger fixture: this
#: one exists to gate a LIVE run in seconds, not to exercise every branch.
CONTROL_HTML = (
    "<html><body>"
    '<header><button aria-expanded="false">Menu</button></header>'
    '<main><button aria-haspopup="menu" aria-label="All filters">'
    "Filters</button></main>"
    "</body></html>"
)


def say(line: str = "") -> None:
    print(line, flush=True)


def _records_for(reading: object, shape_key: str) -> list:
    """The record list for one shape, or `[]` if the reading is malformed."""
    if not isinstance(reading, dict):
        return []
    shape = reading.get(shape_key)
    if not isinstance(shape, dict):
        return []
    records = shape.get("records")
    return records if isinstance(records, list) else []


def _stability_key(records: list) -> tuple:
    """`(term-or-refusal, landmark, own_view, holder_view)` per record, in order."""
    key = []
    for record in records:
        if not isinstance(record, dict):
            key.append(None)
            continue
        term = record.get("term")
        term_key = None
        if isinstance(term, dict):
            term_key = term.get("term") or term.get("refused")
        key.append(
            (term_key, record.get("landmark"), record.get("own_view"),
             record.get("holder_view"))
        )
    return tuple(key)


async def _one_reading(page, cfg: dict) -> dict:
    """One `DISCLOSURE_TARGETS_JS` pass. Never returns a falsy container."""
    raw = await page.evaluate(DISCLOSURE_TARGETS_JS, cfg)  # readonly-ok: reads attributes, presses nothing
    if isinstance(raw, dict):
        return raw
    return {"expanded": {"records": []}, "haspopup": {"records": []}, "page_counts": {}}


async def _challenge_phrases_hit(page) -> list:
    """One boolean per `CHALLENGE_PHRASES`, read inside the page."""
    raw = await page.evaluate(  # readonly-ok: reads body text in-page, returns booleans
        CHALLENGE_CHECK_JS, {"phrases": list(CHALLENGE_PHRASES)}
    )
    return raw if isinstance(raw, list) else [False] * len(CHALLENGE_PHRASES)


async def _read_page(page, url: str) -> dict:
    """Session health, then (if healthy) both shapes, twice, plus counts."""
    landed = await BROWSER.goto(page, url)
    walled = any(marker in landed for marker in config.AUTHWALL_MARKERS)
    hits = await _challenge_phrases_hit(page)
    matched_phrases: list[str] = []
    for i in range(len(CHALLENGE_PHRASES)):
        if i < len(hits) and hits[i]:
            matched_phrases.append(CHALLENGE_PHRASES[i])
    challenge_hit = bool(matched_phrases)

    if walled or challenge_hit:
        return {
            "url": url,
            "walled": walled,
            "challenge_hit": challenge_hit,
            "matched_phrases": matched_phrases,
            "stopped_early": True,
            "shapes": {},
            "page_counts": {},
        }

    cfg = _build_cfg()
    first = await _one_reading(page, cfg)
    await asyncio.sleep(STABILITY_WAIT_S)
    second = await _one_reading(page, cfg)

    pw_expanded_count = await page.locator(SHAPE_EXPANDED).count()
    pw_haspopup_count = await page.locator(SHAPE_HASPOPUP).count()

    shapes: dict = {}
    for shape_key, pw_count in (
        ("expanded", pw_expanded_count),
        ("haspopup", pw_haspopup_count),
    ):
        first_records = _records_for(first, shape_key)
        second_records = _records_for(second, shape_key)
        shapes[shape_key] = {
            "records": first_records,
            "records_second": second_records,
            "playwright_count": pw_count,
            "js_count_first": len(first_records),
            "js_count_second": len(second_records),
            "order_basis_ok": pw_count == len(first_records),
            "stable": _stability_key(first_records) == _stability_key(second_records),
        }

    return {
        "url": url,
        "walled": False,
        "challenge_hit": False,
        "matched_phrases": [],
        "stopped_early": False,
        "shapes": shapes,
        "page_counts": first.get("page_counts", {}) if isinstance(first, dict) else {},
    }


def _term_str(term: dict) -> str:
    if term.get("term") is not None:
        return "term=" + str(term.get("term"))
    if term.get("refused") == "unmatched":
        return (
            "refused=unmatched(band=%s,tokens=%s,digits=%s,caps=%s)"
            % (term.get("band"), term.get("tokens"), term.get("has_digits"),
               term.get("all_capitalised"))
        )
    return "refused=" + str(term.get("refused"))


def _controls_str(controls: dict) -> str:
    return (
        "present=%s found=%s hidden=%s band=%s views=%d numP=%s labels=%s "
        "menuitems=%s options=%s"
        % (controls.get("present"), controls.get("target_found"),
           controls.get("target_hidden"), controls.get("text_band"),
           len(controls.get("view_names") or []), controls.get("numeric_p"),
           controls.get("labels"), controls.get("menuitems"),
           controls.get("options"))
    )


def _print_record(shape_name: str, record: dict) -> None:
    say(
        "    idx=%s tag=%s role=%s type=%s %s=%s landmark=%s in_main=%s "
        "in_form=%s own_view=%s holder_view=%s@%s classes=%s %s "
        "controls[%s] item=%s article=%s visible=%s"
        % (record.get("idx"), record.get("tag"), record.get("role"),
           record.get("type"), shape_name, record.get(shape_name),
           record.get("landmark"), record.get("in_main"), record.get("in_form"),
           record.get("own_view"), record.get("holder_view"),
           record.get("holder_depth"), record.get("classes"),
           _term_str(record.get("term") or {}),
           _controls_str(record.get("controls") or {}),
           record.get("item_ordinal"), record.get("article_ordinal"),
           record.get("visible"))
    )


def _print_shape(shape_name: str, shape: dict) -> None:
    say(
        "  shape=%s playwright_count=%s js_first=%s js_second=%s "
        "order_basis_ok=%s stable=%s"
        % (shape_name, shape.get("playwright_count"), shape.get("js_count_first"),
           shape.get("js_count_second"), shape.get("order_basis_ok"),
           shape.get("stable"))
    )
    for record in shape.get("records") or []:
        _print_record(shape_name, record)


def _print_health(result: dict) -> None:
    say(
        "  walled=%s challenge_hit=%s matched_terms=%d"
        % (result.get("walled"), result.get("challenge_hit"),
           len(result.get("matched_phrases") or []))
    )


def _print_page_counts(counts: dict) -> None:
    say(
        "  counts: expanded=%s expanded_true=%s haspopup=%s menu=%s "
        "menuitem=%s dialog_role=%s dialog_tag=%s listbox=%s form=%s "
        "select=%s main_present=%s items=%s articles=%s"
        % (counts.get("aria_expanded"), counts.get("aria_expanded_true"),
           counts.get("aria_haspopup"), counts.get("role_menu"),
           counts.get("role_menuitem"), counts.get("role_dialog"),
           counts.get("dialog_tag"), counts.get("role_listbox"),
           counts.get("form"), counts.get("select"),
           counts.get("main_present"), counts.get("item_containers"),
           counts.get("articles"))
    )


async def run_detector_control() -> bool:
    """A KNOWN document, a KNOWN answer -- gates every live read below.

    Launches a THROWAWAY LOCAL Chromium: never `BROWSER`, never the
    persistent profile, never the operator's attached browser. If this
    fails, nothing live is loaded.
    """
    say("=" * 70)
    say("DETECTOR CONTROL -- gates every live read below")
    say("=" * 70)
    try:
        async with async_playwright() as offline_pw:
            engine = await offline_pw.chromium.launch(headless=True)
            try:
                tab = await engine.new_page()
                await tab.set_content(CONTROL_HTML, wait_until="domcontentloaded")
                reading = await tab.evaluate(DISCLOSURE_TARGETS_JS, _build_cfg())
            finally:
                await engine.close()
    except Exception as exc:  # noqa: BLE001 - type only, never the message
        say("  CONTROL RAISED " + type(exc).__name__)
        return False

    expanded_records = _records_for(reading, "expanded")
    haspopup_records = _records_for(reading, "haspopup")
    checks: list = [
        ("expanded count == 1", len(expanded_records) == 1),
        ("haspopup count == 1", len(haspopup_records) == 1),
    ]
    if expanded_records:
        record = expanded_records[0]
        checks.append(("expanded landmark == header", record.get("landmark") == "header"))
        checks.append(("expanded value == false", record.get("expanded") == "false"))
    if haspopup_records:
        record = haspopup_records[0]
        checks.append(("haspopup landmark == main", record.get("landmark") == "main"))
        checks.append(("haspopup in_main is True", record.get("in_main") is True))
        checks.append(("haspopup value == menu", record.get("haspopup") == "menu"))
        term = record.get("term") or {}
        checks.append(("haspopup term == all_filters", term.get("term") == "all_filters"))

    ok = True
    failed_labels: list = []
    for label, passed in checks:
        say("  %-30s %s" % (label, "PASS" if passed else "FAIL"))
        if not passed:
            ok = False
            failed_labels.append(label)
    say("  DETECTOR USABLE: %s  failed=%s" % (ok, failed_labels))
    return ok


OUTPUT_PATH = _ROOT / "_state" / "readers4" / "disclosure-targets.json"


def _write_output(results: list) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"pages": results}
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="ascii")
    say("WROTE " + OUTPUT_PATH.name + " under _state/ (gitignored)")


async def main() -> int:
    if "--control" in sys.argv:
        return 0 if await run_detector_control() else 1

    if not config.CDP_ATTACH:
        say("REFUSING: LINKEDIN_CDP_ATTACH is not set. This probe attaches")
        say("to the browser already running on the persistent profile and")
        say("never launches one.")
        return 2

    for target in TARGETS:
        if not readonly.is_read_url(target):
            say("REFUSING: an address is not on the read allowlist.")
            return 2

    if not await run_detector_control():
        say("DETECTOR BROKEN. Nothing live is loaded.")
        return 1

    results: list = []
    page = None
    try:
        async with BROWSER.session() as opened:
            page = opened
            for target in TARGETS:
                say("=" * 70)
                say("PAGE")
                say("=" * 70)
                one = await _read_page(page, target)
                results.append(one)
                _print_health(one)
                if one.get("walled") or one.get("challenge_hit"):
                    say("STOP -- session health failed; loading nothing further.")
                    _write_output(results)
                    return 3
                _print_page_counts(one.get("page_counts") or {})
                for shape_name in ("expanded", "haspopup"):
                    _print_shape(
                        shape_name, (one.get("shapes") or {}).get(shape_name) or {}
                    )
    except Exception as exc:  # noqa: BLE001 - type only, never the message
        say("THE RUN RAISED " + type(exc).__name__)
        _write_output(results)
        return 1
    finally:
        try:
            if page is not None and not page.is_closed():
                await page.close()
        except Exception as exc:  # noqa: BLE001 - shutdown noise only
            say("    closing our tab raised " + type(exc).__name__)
        try:
            await BROWSER.stop()
        except Exception as exc:  # noqa: BLE001 - shutdown noise only
            say("    cleanup raised " + type(exc).__name__)

    _write_output(results)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
